---
sidebar_position: 10
title: Chapter 9 - Humanoid Robot Systems
---

# Chapter 9: Humanoid Robot Systems

<div className="chapter-actions">
  <button className="ai-button chat-button">💬 Ask Questions from This Chapter</button>
  <button className="ai-button personalize-button">✨ Personalize this Chapter for Me</button>
  <button className="ai-button translate-button">🌐 Translate to Urdu</button>
</div>

## Learning Objectives

- Understand humanoid robot kinematics and dynamics
- Implement balance and walking controllers
- Design whole-body motion planning systems
- Apply human-robot interaction principles
- Build teleoperation and imitation systems

## 9.1 Humanoid Robot Architecture

### Typical Humanoid Configuration

```
Head (cameras, sensors)
    ↓
Torso (compute, IMU)
    ↓
Arms (7 DOF each)
    ├── Shoulder (3 DOF)
    ├── Elbow (1 DOF)
    ├── Wrist (3 DOF)
    └── Hand/Gripper
    ↓
Legs (6 DOF each)
    ├── Hip (3 DOF)
    ├── Knee (1 DOF)
    └── Ankle (2 DOF)
```

### Robot Specifications

```python
class HumanoidRobotSpec:
    """Specifications for a humanoid robot"""
    def __init__(self):
        # Dimensions (meters)
        self.height = 1.7
        self.mass = 75.0  # kg

        # Link lengths
        self.torso_length = 0.6
        self.upper_arm_length = 0.3
        self.forearm_length = 0.3
        self.thigh_length = 0.4
        self.shin_length = 0.4

        # Degrees of Freedom
        self.total_dof = 30
        self.arm_dof = 7
        self.leg_dof = 6
        self.head_dof = 2

        # Joint limits (radians)
        self.joint_limits = {
            'shoulder_pitch': (-np.pi, np.pi/2),
            'shoulder_roll': (-np.pi/2, np.pi/2),
            'shoulder_yaw': (-np.pi/2, np.pi/2),
            'elbow': (0, 2.5),
            'hip_pitch': (-np.pi/2, np.pi/2),
            'hip_roll': (-np.pi/4, np.pi/4),
            'hip_yaw': (-np.pi/4, np.pi/4),
            'knee': (0, 2.5),
            'ankle_pitch': (-np.pi/4, np.pi/4),
            'ankle_roll': (-np.pi/6, np.pi/6)
        }

        # Performance specs
        self.max_walking_speed = 1.5  # m/s
        self.max_payload = 20.0  # kg
        self.battery_life = 2.0  # hours
```

## 9.2 Balance and Stability

### Center of Mass (COM) Control

```python
import numpy as np

class BalanceController:
    def __init__(self):
        self.g = 9.81  # gravity
        self.robot_mass = 75.0  # kg
        self.com_height = 0.85  # meters

    def compute_com(self, joint_angles, link_masses, link_com_positions):
        """Calculate center of mass position"""
        total_mass = sum(link_masses)
        com = np.zeros(3)

        for mass, pos in zip(link_masses, link_com_positions):
            com += mass * pos

        com /= total_mass
        return com

    def compute_zmp(self, com, com_accel):
        """
        Calculate Zero Moment Point
        com: center of mass position [x, y, z]
        com_accel: COM acceleration [ax, ay, az]
        """
        zmp_x = com[0] - (com[2] / (com_accel[2] + self.g)) * com_accel[0]
        zmp_y = com[1] - (com[2] / (com_accel[2] + self.g)) * com_accel[1]

        return np.array([zmp_x, zmp_y, 0])

    def is_stable(self, zmp, support_polygon):
        """Check if ZMP is inside support polygon"""
        # Simple rectangular support polygon check
        x_min, x_max, y_min, y_max = support_polygon

        return (x_min <= zmp[0] <= x_max and
                y_min <= zmp[1] <= y_max)

    def compute_stabilizing_torque(self, com_error, com_vel_error):
        """Compute ankle torques for balance"""
        Kp = 100  # Proportional gain
        Kd = 20   # Derivative gain

        torque = Kp * com_error + Kd * com_vel_error
        return torque

# Example usage
controller = BalanceController()

# Current state
com = np.array([0.0, 0.0, 0.85])
com_accel = np.array([0.1, 0.0, 0.0])

# Compute ZMP
zmp = controller.compute_zmp(com, com_accel)
print(f"ZMP: {zmp}")

# Check stability (single foot support)
support_polygon = [-0.1, 0.1, -0.05, 0.05]  # [x_min, x_max, y_min, y_max]
stable = controller.is_stable(zmp, support_polygon)
print(f"Stable: {stable}")
```

### Inverted Pendulum Model

```python
class InvertedPendulumBalance:
    def __init__(self, mass, height):
        """
        Linear Inverted Pendulum Model for balance
        mass: robot mass (kg)
        height: COM height (m)
        """
        self.mass = mass
        self.height = height
        self.g = 9.81

        # Natural frequency
        self.omega = np.sqrt(self.g / self.height)

    def compute_cop_trajectory(self, com_initial, com_final, T):
        """
        Compute Center of Pressure trajectory
        com_initial: initial COM position
        com_final: final COM position
        T: time duration
        """
        t = np.linspace(0, T, 100)
        cop = np.zeros_like(t)

        for i, ti in enumerate(t):
            # Analytical solution for LIPM
            C = np.cosh(self.omega * T)
            S = np.sinh(self.omega * T)

            cop[i] = ((com_final - com_initial * C) / S) * np.sinh(self.omega * (T - ti)) + com_initial * np.cosh(self.omega * (T - ti))

        return t, cop

    def compute_required_cop(self, com_pos, com_vel, com_accel_desired):
        """Compute required COP for desired COM acceleration"""
        cop = com_pos - (self.height / self.g) * com_accel_desired
        return cop
```

## 9.3 Walking Gait Generation

### Simple Walking Pattern Generator

```python
class WalkingPatternGenerator:
    def __init__(self, step_length=0.2, step_height=0.05, step_time=0.8):
        """
        Generate walking patterns
        step_length: forward distance per step (m)
        step_height: foot clearance (m)
        step_time: time per step (s)
        """
        self.step_length = step_length
        self.step_height = step_height
        self.step_time = step_time
        self.double_support_ratio = 0.2  # 20% of step is double support

    def generate_foot_trajectory(self, phase):
        """
        Generate foot trajectory for swing phase
        phase: 0 to 1 (swing phase progress)
        """
        if phase < 0 or phase > 1:
            raise ValueError("Phase must be between 0 and 1")

        # Forward motion (linear)
        x = self.step_length * phase

        # Vertical motion (parabolic)
        z = 4 * self.step_height * phase * (1 - phase)

        # No lateral motion for straight walking
        y = 0

        return np.array([x, y, z])

    def generate_walking_cycle(self, num_steps, dt=0.01):
        """Generate complete walking cycle"""
        single_support_time = self.step_time * (1 - self.double_support_ratio)
        num_samples = int(self.step_time / dt)

        trajectory = {
            'time': [],
            'left_foot': [],
            'right_foot': [],
            'com': []
        }

        left_pos = np.array([0, 0.1, 0])  # Start position
        right_pos = np.array([0, -0.1, 0])

        for step in range(num_steps):
            for i in range(num_samples):
                t = i * dt
                phase = t / single_support_time

                if step % 2 == 0:  # Right foot swing
                    if phase <= 1:
                        swing_offset = self.generate_foot_trajectory(phase)
                        right_foot = right_pos + swing_offset
                        left_foot = left_pos
                    else:
                        right_foot = right_pos + np.array([self.step_length, 0, 0])
                        left_foot = left_pos
                else:  # Left foot swing
                    if phase <= 1:
                        swing_offset = self.generate_foot_trajectory(phase)
                        left_foot = left_pos + swing_offset
                        right_foot = right_pos
                    else:
                        left_foot = left_pos + np.array([self.step_length, 0, 0])
                        right_foot = right_pos

                # COM trajectory (simplified - midpoint between feet)
                com = (left_foot + right_foot) / 2
                com[2] = 0.85  # COM height

                trajectory['time'].append(step * self.step_time + t)
                trajectory['left_foot'].append(left_foot.copy())
                trajectory['right_foot'].append(right_foot.copy())
                trajectory['com'].append(com.copy())

            # Update positions for next step
            if step % 2 == 0:
                right_pos += np.array([self.step_length, 0, 0])
            else:
                left_pos += np.array([self.step_length, 0, 0])

        return trajectory

# Example usage
wpg = WalkingPatternGenerator(step_length=0.3, step_height=0.05, step_time=0.8)
walking_traj = wpg.generate_walking_cycle(num_steps=4)

print(f"Generated {len(walking_traj['time'])} trajectory points")
print(f"Total time: {walking_traj['time'][-1]:.2f} seconds")
```

## 9.4 Whole-Body Motion Planning

### Inverse Kinematics for Humanoid

```python
import numpy as np
from scipy.optimize import minimize

class HumanoidIK:
    def __init__(self, robot_spec):
        """Inverse kinematics solver for humanoid"""
        self.spec = robot_spec

    def forward_kinematics_arm(self, joint_angles):
        """Compute end-effector position from joint angles"""
        # Simplified 7-DOF arm FK
        shoulder_pitch, shoulder_roll, shoulder_yaw, elbow, wrist_pitch, wrist_roll, wrist_yaw = joint_angles

        # Compute transformation matrices (simplified)
        x = (self.spec.upper_arm_length * np.cos(shoulder_pitch) * np.cos(shoulder_yaw) +
             self.spec.forearm_length * np.cos(shoulder_pitch + elbow))

        y = (self.spec.upper_arm_length * np.sin(shoulder_roll) +
             self.spec.forearm_length * np.sin(shoulder_roll))

        z = (self.spec.upper_arm_length * np.sin(shoulder_pitch) +
             self.spec.forearm_length * np.sin(shoulder_pitch + elbow))

        return np.array([x, y, z])

    def inverse_kinematics_arm(self, target_position, initial_guess=None):
        """
        Solve IK for arm to reach target position
        Uses numerical optimization
        """
        if initial_guess is None:
            initial_guess = np.zeros(7)

        def objective(joint_angles):
            current_pos = self.forward_kinematics_arm(joint_angles)
            error = np.linalg.norm(target_position - current_pos)
            return error

        # Joint limit constraints
        bounds = [
            self.spec.joint_limits['shoulder_pitch'],
            self.spec.joint_limits['shoulder_roll'],
            self.spec.joint_limits['shoulder_yaw'],
            self.spec.joint_limits['elbow'],
            (-np.pi, np.pi),  # wrist joints
            (-np.pi, np.pi),
            (-np.pi, np.pi)
        ]

        result = minimize(objective, initial_guess, method='SLSQP', bounds=bounds)

        if result.success:
            return result.x
        else:
            return None

# Example usage
spec = HumanoidRobotSpec()
ik_solver = HumanoidIK(spec)

target = np.array([0.5, 0.3, 0.4])  # Target position
solution = ik_solver.inverse_kinematics_arm(target)

if solution is not None:
    print(f"IK Solution: {np.rad2deg(solution)}")
    # Verify
    actual_pos = ik_solver.forward_kinematics_arm(solution)
    error = np.linalg.norm(target - actual_pos)
    print(f"Position error: {error:.4f} m")
```

## 9.5 Human-Robot Interaction

### Speech Recognition and Response

```python
import numpy as np

class VoiceCommandProcessor:
    def __init__(self):
        """Process voice commands for robot"""
        self.commands = {
            'wave': self.wave_hand,
            'pick': self.pick_object,
            'walk': self.start_walking,
            'stop': self.stop_motion,
            'follow': self.follow_person
        }

    def process_command(self, speech_text):
        """Process recognized speech"""
        speech_lower = speech_text.lower()

        for command, action in self.commands.items():
            if command in speech_lower:
                return action()

        return "Command not recognized"

    def wave_hand(self):
        """Generate waving motion"""
        print("Executing wave motion")
        # Generate trajectory for waving
        return "Waving hand"

    def pick_object(self):
        """Initiate object picking"""
        print("Looking for objects to pick")
        return "Picking object"

    def start_walking(self):
        """Start walking"""
        print("Starting walking motion")
        return "Walking"

    def stop_motion(self):
        """Stop all motion"""
        print("Stopping all motion")
        return "Stopped"

    def follow_person(self):
        """Start person following behavior"""
        print("Initiating person tracking")
        return "Following person"

class GestureRecognition:
    def __init__(self):
        """Recognize human gestures"""
        self.gesture_threshold = 0.7

    def detect_pointing(self, skeleton_keypoints):
        """Detect pointing gesture from skeleton"""
        # Simplified: check if arm is extended
        shoulder = skeleton_keypoints['right_shoulder']
        elbow = skeleton_keypoints['right_elbow']
        wrist = skeleton_keypoints['right_wrist']

        # Check if arm is extended
        arm_vector = wrist - shoulder
        arm_length = np.linalg.norm(arm_vector)

        # Check if arm is roughly straight
        upper_arm = elbow - shoulder
        forearm = wrist - elbow

        angle = self.angle_between(upper_arm, forearm)

        if angle > 150:  # Nearly straight
            # Get pointing direction
            direction = arm_vector / arm_length
            return {
                'gesture': 'pointing',
                'direction': direction,
                'confidence': 0.95
            }

        return None

    def angle_between(self, v1, v2):
        """Calculate angle between vectors in degrees"""
        unit_v1 = v1 / np.linalg.norm(v1)
        unit_v2 = v2 / np.linalg.norm(v2)
        dot_product = np.dot(unit_v1, unit_v2)
        angle = np.arccos(np.clip(dot_product, -1.0, 1.0))
        return np.degrees(angle)
```

## 9.6 Practical Task: Humanoid Walking Simulation

```python
class HumanoidWalkingSimulation:
    def __init__(self):
        self.spec = HumanoidRobotSpec()
        self.balance_controller = BalanceController()
        self.pattern_generator = WalkingPatternGenerator()

        self.current_phase = 0
        self.com_position = np.array([0, 0, 0.85])
        self.com_velocity = np.zeros(3)

    def simulate_step(self, dt=0.01):
        """Simulate one time step of walking"""
        # Generate desired foot positions
        phase = self.current_phase
        left_foot_des = self.pattern_generator.generate_foot_trajectory(phase)
        right_foot_des = self.pattern_generator.generate_foot_trajectory(1 - phase)

        # Update COM trajectory
        # Simplified: COM follows midpoint of feet
        com_des = (left_foot_des + right_foot_des) / 2
        com_des[2] = 0.85

        # Compute COM acceleration (PD control)
        Kp = 50
        Kd = 10
        com_error = com_des - self.com_position
        com_accel = Kp * com_error - Kd * self.com_velocity

        # Check stability
        zmp = self.balance_controller.compute_zmp(self.com_position, com_accel)

        # Update state
        self.com_velocity += com_accel * dt
        self.com_position += self.com_velocity * dt

        # Update phase
        self.current_phase = (self.current_phase + dt / self.pattern_generator.step_time) % 1.0

        return {
            'com': self.com_position.copy(),
            'zmp': zmp,
            'left_foot': left_foot_des,
            'right_foot': right_foot_des,
            'phase': self.current_phase
        }

    def run_simulation(self, duration=5.0, dt=0.01):
        """Run walking simulation"""
        num_steps = int(duration / dt)
        history = []

        for _ in range(num_steps):
            state = self.simulate_step(dt)
            history.append(state)

        return history

# Run simulation
sim = HumanoidWalkingSimulation()
results = sim.run_simulation(duration=3.0)

print(f"Simulated {len(results)} time steps")
print(f"Final COM position: {results[-1]['com']}")
```

## Glossary

- **DOF**: Degrees of Freedom
- **COM**: Center of Mass
- **ZMP**: Zero Moment Point
- **COP**: Center of Pressure
- **Gait**: Pattern of walking or running
- **Support Polygon**: Area of foot/feet contact
- **Whole-Body Control**: Coordinating all joints simultaneously

## Checkpoint Quiz

<div className="quiz-container">

### Question 1
What is the Zero Moment Point (ZMP)?

A) The robot's center of mass
B) Point where ground reaction forces create zero moment
C) The lowest point on the robot
D) The point of maximum pressure

<details>
<summary>Show Answer</summary>
**Answer: B** - ZMP is where the net moment from ground reaction forces is zero.
</details>

### Question 2
Why do humanoid robots typically have 7 DOF arms?

A) It's the minimum required
B) It provides redundancy for obstacle avoidance
C) It's cheaper to build
D) It matches human anatomy exactly

<details>
<summary>Show Answer</summary>
**Answer: B** - 7 DOF provides kinematic redundancy beyond the 6 DOF needed for positioning.
</details>

### Question 3
What is the main challenge in humanoid walking compared to wheeled robots?

A) Speed
B) Battery life
C) Maintaining dynamic balance
D) Cost

<details>
<summary>Show Answer</summary>
**Answer: C** - Bipedal walking requires continuous dynamic balance control.
</details>

</div>

## AI Assistant Prompts for Deep Learning

1. "Explain the Zero Moment Point (ZMP) and why it's critical for humanoid balance."
2. "How does the Linear Inverted Pendulum Model simplify walking control?"
3. "Compare different gait generation methods for humanoid robots."
4. "What are the main challenges in whole-body motion planning for humanoids?"
5. "Explain how modern humanoid robots like Atlas achieve dynamic balance during walking."

---

**Previous**: [Chapter 8: Computer Vision](./chapter-08.md) | **Next**: [Chapter 10: Future of Physical AI](./chapter-10.md)
