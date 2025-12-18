---
sidebar_position: 8
title: Chapter 7 - Motion Planning and Navigation
---

# Chapter 7: Motion Planning and Navigation

<div className="chapter-actions">
  <button className="ai-button chat-button">💬 Ask Questions from This Chapter</button>
  <button className="ai-button personalize-button">✨ Personalize this Chapter for Me</button>
  <button className="ai-button translate-button">🌐 Translate to Urdu</button>
</div>

## Learning Objectives

- Understand path planning algorithms (A*, RRT, PRM)
- Implement collision detection and avoidance
- Apply SLAM for mapping and localization
- Design navigation stacks for mobile robots
- Build obstacle avoidance behaviors

## 7.1 Graph-Based Planning

### A* Pathfinding

```python
import numpy as np
import heapq
from collections import defaultdict

class AStarPlanner:
    def __init__(self, grid):
        """
        A* path planning on grid
        grid: 2D numpy array (0 = free, 1 = obstacle)
        """
        self.grid = grid
        self.rows, self.cols = grid.shape

    def heuristic(self, a, b):
        """Euclidean distance heuristic"""
        return np.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

    def get_neighbors(self, pos):
        """Get valid neighboring cells (8-connected)"""
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue

                new_pos = (pos[0] + dx, pos[1] + dy)

                # Check bounds
                if (0 <= new_pos[0] < self.rows and
                    0 <= new_pos[1] < self.cols and
                    self.grid[new_pos] == 0):
                    neighbors.append(new_pos)

        return neighbors

    def plan(self, start, goal):
        """Find optimal path from start to goal"""
        # Priority queue: (f_score, counter, position)
        counter = 0
        open_set = [(0, counter, start)]
        counter += 1

        came_from = {}
        g_score = defaultdict(lambda: float('inf'))
        g_score[start] = 0

        f_score = defaultdict(lambda: float('inf'))
        f_score[start] = self.heuristic(start, goal)

        open_set_hash = {start}

        while open_set:
            current = heapq.heappop(open_set)[2]
            open_set_hash.remove(current)

            if current == goal:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return list(reversed(path))

            for neighbor in self.get_neighbors(current):
                tentative_g = g_score[current] + self.heuristic(current, neighbor)

                if tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = g_score[neighbor] + self.heuristic(neighbor, goal)

                    if neighbor not in open_set_hash:
                        heapq.heappush(open_set, (f_score[neighbor], counter, neighbor))
                        counter += 1
                        open_set_hash.add(neighbor)

        return None  # No path found

# Example usage
grid = np.zeros((50, 50))
grid[20:30, 20:30] = 1  # Add obstacle

planner = AStarPlanner(grid)
path = planner.plan((5, 5), (45, 45))

if path:
    print(f"Path found with {len(path)} waypoints")
    print(f"First 5 waypoints: {path[:5]}")
else:
    print("No path found")
```

## 7.2 Sampling-Based Planning

### RRT (Rapidly-exploring Random Tree)

```python
import numpy as np
import matplotlib.pyplot as plt

class RRT:
    def __init__(self, start, goal, obstacle_list, bounds, max_iter=500, step_size=1.0):
        """
        RRT path planning
        start: (x, y) starting position
        goal: (x, y) goal position
        obstacle_list: list of (x, y, radius) obstacles
        bounds: ((x_min, x_max), (y_min, y_max))
        """
        self.start = Node(start[0], start[1])
        self.goal = Node(goal[0], goal[1])
        self.obstacle_list = obstacle_list
        self.bounds = bounds
        self.max_iter = max_iter
        self.step_size = step_size
        self.node_list = [self.start]

    def plan(self):
        """Execute RRT planning"""
        for i in range(self.max_iter):
            # Sample random point
            rnd_node = self.sample_node()

            # Find nearest node in tree
            nearest_node = self.get_nearest_node(rnd_node)

            # Steer towards random point
            new_node = self.steer(nearest_node, rnd_node)

            # Check collision
            if self.check_collision(new_node):
                self.node_list.append(new_node)

                # Check if goal reached
                if self.calc_distance(new_node, self.goal) <= self.step_size:
                    final_node = self.steer(new_node, self.goal)
                    if self.check_collision(final_node):
                        return self.generate_final_path(len(self.node_list) - 1)

        return None  # No path found

    def sample_node(self):
        """Sample random node (with goal bias)"""
        if np.random.random() < 0.1:  # 10% goal bias
            return Node(self.goal.x, self.goal.y)

        x = np.random.uniform(self.bounds[0][0], self.bounds[0][1])
        y = np.random.uniform(self.bounds[1][0], self.bounds[1][1])
        return Node(x, y)

    def get_nearest_node(self, rnd_node):
        """Find nearest node to random node"""
        dlist = [self.calc_distance(node, rnd_node) for node in self.node_list]
        min_index = dlist.index(min(dlist))
        return self.node_list[min_index]

    def steer(self, from_node, to_node):
        """Create new node in direction of to_node"""
        new_node = Node(from_node.x, from_node.y)
        d = self.calc_distance(from_node, to_node)

        if d <= self.step_size:
            new_node.x = to_node.x
            new_node.y = to_node.y
        else:
            theta = np.arctan2(to_node.y - from_node.y, to_node.x - from_node.x)
            new_node.x += self.step_size * np.cos(theta)
            new_node.y += self.step_size * np.sin(theta)

        new_node.parent = from_node
        return new_node

    def check_collision(self, node):
        """Check if node collides with obstacles"""
        for (ox, oy, radius) in self.obstacle_list:
            dx = ox - node.x
            dy = oy - node.y
            d = np.sqrt(dx**2 + dy**2)
            if d <= radius:
                return False
        return True

    def calc_distance(self, node1, node2):
        """Calculate distance between nodes"""
        return np.sqrt((node1.x - node2.x)**2 + (node1.y - node2.y)**2)

    def generate_final_path(self, goal_index):
        """Generate path from goal to start"""
        path = [[self.goal.x, self.goal.y]]
        node = self.node_list[goal_index]

        while node.parent is not None:
            path.append([node.x, node.y])
            node = node.parent

        path.append([node.x, node.y])
        return path

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.parent = None

# Example usage
obstacles = [
    (5, 5, 1),
    (3, 6, 1),
    (7, 8, 1),
    (9, 5, 1)
]

rrt = RRT(
    start=(0, 0),
    goal=(10, 10),
    obstacle_list=obstacles,
    bounds=((-2, 12), (-2, 12))
)

path = rrt.plan()
if path:
    print(f"Path found with {len(path)} points")
else:
    print("No path found")
```

## 7.3 SLAM (Simultaneous Localization and Mapping)

### EKF-SLAM (Extended Kalman Filter SLAM)

```python
import numpy as np

class EKFSLAM:
    def __init__(self, robot_pose, num_landmarks):
        """
        EKF-SLAM implementation
        robot_pose: [x, y, theta]
        num_landmarks: maximum number of landmarks
        """
        # State: [x, y, theta, lm1_x, lm1_y, lm2_x, lm2_y, ...]
        state_dim = 3 + 2 * num_landmarks
        self.state = np.zeros(state_dim)
        self.state[:3] = robot_pose

        # Covariance
        self.cov = np.eye(state_dim) * 0.01

        # Process noise
        self.Q = np.diag([0.1, 0.1, 0.05]) ** 2

        # Measurement noise
        self.R = np.diag([0.3, 0.2]) ** 2  # range, bearing

        self.num_landmarks = num_landmarks
        self.landmarks_initialized = np.zeros(num_landmarks, dtype=bool)

    def predict(self, control, dt):
        """
        Prediction step
        control: [v, omega] (linear velocity, angular velocity)
        """
        v, omega = control
        x, y, theta = self.state[:3]

        # Motion model
        if abs(omega) < 1e-6:
            # Straight line motion
            x_new = x + v * np.cos(theta) * dt
            y_new = y + v * np.sin(theta) * dt
            theta_new = theta
        else:
            # Circular motion
            x_new = x + (v / omega) * (np.sin(theta + omega * dt) - np.sin(theta))
            y_new = y + (v / omega) * (-np.cos(theta + omega * dt) + np.cos(theta))
            theta_new = theta + omega * dt

        # Update state
        self.state[0] = x_new
        self.state[1] = y_new
        self.state[2] = theta_new

        # Jacobian of motion model
        F = np.eye(len(self.state))
        F[0, 2] = -v * np.sin(theta) * dt
        F[1, 2] = v * np.cos(theta) * dt

        # Update covariance
        Fx = F[:3, :3]
        self.cov[:3, :3] = Fx @ self.cov[:3, :3] @ Fx.T + self.Q

    def update(self, measurement, landmark_id):
        """
        Update step with landmark observation
        measurement: [range, bearing] to landmark
        landmark_id: index of observed landmark
        """
        x, y, theta = self.state[:3]
        z = np.array(measurement)

        lm_idx = 3 + 2 * landmark_id

        # Initialize landmark if first time seeing it
        if not self.landmarks_initialized[landmark_id]:
            range_meas, bearing_meas = z
            lm_x = x + range_meas * np.cos(theta + bearing_meas)
            lm_y = y + range_meas * np.sin(theta + bearing_meas)
            self.state[lm_idx:lm_idx+2] = [lm_x, lm_y]
            self.landmarks_initialized[landmark_id] = True
            return

        # Predicted measurement
        lm_x, lm_y = self.state[lm_idx:lm_idx+2]
        dx = lm_x - x
        dy = lm_y - y
        q = dx**2 + dy**2
        z_pred = np.array([
            np.sqrt(q),
            np.arctan2(dy, dx) - theta
        ])

        # Innovation
        innovation = z - z_pred
        innovation[1] = np.arctan2(np.sin(innovation[1]), np.cos(innovation[1]))  # Normalize angle

        # Measurement Jacobian
        H = np.zeros((2, len(self.state)))
        H[0, 0] = -dx / np.sqrt(q)
        H[0, 1] = -dy / np.sqrt(q)
        H[0, lm_idx] = dx / np.sqrt(q)
        H[0, lm_idx+1] = dy / np.sqrt(q)
        H[1, 0] = dy / q
        H[1, 1] = -dx / q
        H[1, 2] = -1
        H[1, lm_idx] = -dy / q
        H[1, lm_idx+1] = dx / q

        # Kalman gain
        S = H @ self.cov @ H.T + self.R
        K = self.cov @ H.T @ np.linalg.inv(S)

        # Update state
        self.state += K @ innovation

        # Update covariance
        I = np.eye(len(self.state))
        self.cov = (I - K @ H) @ self.cov

    def get_pose(self):
        """Get robot pose"""
        return self.state[:3].copy()

    def get_map(self):
        """Get landmark map"""
        landmarks = []
        for i in range(self.num_landmarks):
            if self.landmarks_initialized[i]:
                idx = 3 + 2 * i
                landmarks.append(self.state[idx:idx+2].copy())
        return landmarks
```

## 7.4 Dynamic Obstacle Avoidance

### Dynamic Window Approach (DWA)

```python
import numpy as np

class DWA:
    def __init__(self, max_speed=1.0, max_yaw_rate=40*np.pi/180):
        """Dynamic Window Approach for obstacle avoidance"""
        self.max_speed = max_speed
        self.max_yaw_rate = max_yaw_rate
        self.max_accel = 0.2
        self.max_dyaw_rate = 40*np.pi/180

        self.v_resolution = 0.01
        self.yaw_rate_resolution = 0.1 * np.pi / 180

        self.dt = 0.1
        self.predict_time = 3.0

        # Cost weights
        self.to_goal_cost_gain = 0.15
        self.speed_cost_gain = 1.0
        self.obstacle_cost_gain = 1.0

    def calc_dynamic_window(self, v, yaw_rate):
        """Calculate dynamic window based on current velocity"""
        # Speed limits
        Vs = [0, self.max_speed, -self.max_yaw_rate, self.max_yaw_rate]

        # Dynamic window from acceleration
        Vd = [
            v - self.max_accel * self.dt,
            v + self.max_accel * self.dt,
            yaw_rate - self.max_dyaw_rate * self.dt,
            yaw_rate + self.max_dyaw_rate * self.dt
        ]

        # Intersection
        dw = [
            max(Vs[0], Vd[0]),
            min(Vs[1], Vd[1]),
            max(Vs[2], Vd[2]),
            min(Vs[3], Vd[3])
        ]

        return dw

    def predict_trajectory(self, x, v, yaw, yaw_rate):
        """Predict trajectory given velocity and yaw rate"""
        trajectory = [[x[0], x[1], x[2]]]
        time = 0

        while time <= self.predict_time:
            x = [
                x[0] + v * np.cos(x[2]) * self.dt,
                x[1] + v * np.sin(x[2]) * self.dt,
                x[2] + yaw_rate * self.dt
            ]
            trajectory.append(x[:])
            time += self.dt

        return np.array(trajectory)

    def calc_to_goal_cost(self, trajectory, goal):
        """Cost based on heading to goal"""
        dx = goal[0] - trajectory[-1, 0]
        dy = goal[1] - trajectory[-1, 1]
        error_angle = np.arctan2(dy, dx)
        cost_angle = error_angle - trajectory[-1, 2]
        cost = abs(np.arctan2(np.sin(cost_angle), np.cos(cost_angle)))

        return cost

    def calc_obstacle_cost(self, trajectory, obstacles):
        """Cost based on distance to obstacles"""
        min_dist = float('inf')

        for point in trajectory:
            for ox, oy, radius in obstacles:
                dist = np.sqrt((point[0] - ox)**2 + (point[1] - oy)**2) - radius
                if dist < min_dist:
                    min_dist = dist

        if min_dist < 0.2:
            return float('inf')

        return 1.0 / min_dist

    def plan(self, x, v, yaw_rate, goal, obstacles):
        """
        Calculate best velocity command
        x: [x, y, yaw]
        v: current velocity
        yaw_rate: current yaw rate
        goal: [x, y]
        obstacles: list of [x, y, radius]
        """
        dw = self.calc_dynamic_window(v, yaw_rate)

        best_v = 0
        best_yaw_rate = 0
        min_cost = float('inf')
        best_trajectory = None

        # Evaluate all velocities in dynamic window
        for v_sample in np.arange(dw[0], dw[1], self.v_resolution):
            for yaw_rate_sample in np.arange(dw[2], dw[3], self.yaw_rate_resolution):
                trajectory = self.predict_trajectory(x, v_sample, x[2], yaw_rate_sample)

                to_goal_cost = self.calc_to_goal_cost(trajectory, goal)
                speed_cost = self.max_speed - v_sample
                ob_cost = self.calc_obstacle_cost(trajectory, obstacles)

                total_cost = (
                    self.to_goal_cost_gain * to_goal_cost +
                    self.speed_cost_gain * speed_cost +
                    self.obstacle_cost_gain * ob_cost
                )

                if total_cost < min_cost:
                    min_cost = total_cost
                    best_v = v_sample
                    best_yaw_rate = yaw_rate_sample
                    best_trajectory = trajectory

        return [best_v, best_yaw_rate], best_trajectory

# Example usage
dwa = DWA()
x = [0, 0, 0]  # [x, y, yaw]
v = 0.0
yaw_rate = 0.0
goal = [10, 10]
obstacles = [[5, 5, 0.5], [7, 7, 0.5]]

control, trajectory = dwa.plan(x, v, yaw_rate, goal, obstacles)
print(f"Best control: v={control[0]:.2f}, yaw_rate={control[1]:.2f}")
```

## Glossary

- **A***: Optimal graph search algorithm
- **RRT**: Rapidly-exploring Random Tree
- **SLAM**: Simultaneous Localization and Mapping
- **EKF**: Extended Kalman Filter
- **DWA**: Dynamic Window Approach
- **Configuration Space**: Space of all possible robot configurations
- **Heuristic**: Estimate of cost-to-go in search

## Checkpoint Quiz

<div className="quiz-container">

### Question 1
What is the advantage of A* over Dijkstra's algorithm?

A) Uses less memory
B) Uses heuristic to guide search toward goal
C) Finds multiple paths
D) Works in continuous space

<details>
<summary>Show Answer</summary>
**Answer: B** - A* uses a heuristic to efficiently search toward the goal.
</details>

### Question 2
What problem does SLAM solve?

A) Path planning only
B) Localization and mapping simultaneously
C) Object recognition
D) Motor control

<details>
<summary>Show Answer</summary>
**Answer: B** - SLAM builds a map while localizing the robot within it.
</details>

### Question 3
What is the main advantage of sampling-based planners like RRT?

A) Always find optimal path
B) Work in high-dimensional spaces
C) Faster than A*
D) Don't need collision checking

<details>
<summary>Show Answer</summary>
**Answer: B** - Sampling-based planners scale well to high dimensions.
</details>

</div>

## AI Assistant Prompts for Deep Learning

1. "Compare A* and RRT. When would you use each for robot path planning?"
2. "Explain how SLAM works. Why is it a 'chicken and egg' problem?"
3. "Walk me through the Dynamic Window Approach for real-time obstacle avoidance."
4. "What are the challenges of motion planning for humanoid robots vs mobile robots?"
5. "How do sampling-based methods like RRT handle high-dimensional configuration spaces?"

---

**Previous**: [Chapter 6: Machine Learning](./chapter-06.md) | **Next**: [Chapter 8: Computer Vision for Robots](./chapter-08.md)
