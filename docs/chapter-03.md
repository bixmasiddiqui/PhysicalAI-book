---
sidebar_position: 4
title: Chapter 3 - Programming for Robotics with ROS
---

# Chapter 3: Programming for Robotics with ROS

<div className="chapter-actions">
  <button className="ai-button chat-button">💬 Ask Questions from This Chapter</button>
  <button className="ai-button personalize-button">✨ Personalize this Chapter for Me</button>
  <button className="ai-button translate-button">🌐 Translate to Urdu</button>
</div>

## Learning Objectives

- Understand the Robot Operating System (ROS) architecture
- Create and manage ROS nodes, topics, and services
- Implement publisher-subscriber patterns for robot communication
- Work with sensor data and control systems in ROS
- Build a simple autonomous robot controller

## 3.1 Introduction to ROS

### What is ROS?

ROS (Robot Operating System) is not an actual operating system, but a middleware framework that provides:

- **Communication Infrastructure**: Message passing between processes
- **Hardware Abstraction**: Standardized interfaces for sensors and actuators
- **Package Management**: Modular, reusable code libraries
- **Tools**: Visualization, simulation, debugging utilities

### ROS Concepts

```
┌─────────────────────────────────────┐
│         ROS Master                  │  ← Coordination service
├─────────────────────────────────────┤
│   Node 1    Node 2    Node 3        │  ← Independent processes
├─────────────────────────────────────┤
│   Topics, Services, Actions         │  ← Communication methods
└─────────────────────────────────────┘
```

## 3.2 ROS Nodes and Topics

### Creating a Simple Publisher

```python
#!/usr/bin/env python3
import rospy
from std_msgs.msg import String

def talker():
    # Initialize the node
    rospy.init_node('talker', anonymous=True)

    # Create publisher
    pub = rospy.Publisher('chatter', String, queue_size=10)

    # Set publishing rate (10 Hz)
    rate = rospy.Rate(10)

    count = 0
    while not rospy.is_shutdown():
        msg = f"Hello World {count}"
        rospy.loginfo(msg)
        pub.publish(msg)
        count += 1
        rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
```

### Creating a Subscriber

```python
#!/usr/bin/env python3
import rospy
from std_msgs.msg import String

def callback(data):
    rospy.loginfo(f"I heard: {data.data}")

def listener():
    rospy.init_node('listener', anonymous=True)

    # Subscribe to topic
    rospy.Subscriber('chatter', String, callback)

    # Keep node running
    rospy.spin()

if __name__ == '__main__':
    listener()
```

## 3.3 Working with Sensor Data

### Processing Laser Scan Data

```python
#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class ObstacleAvoider:
    def __init__(self):
        rospy.init_node('obstacle_avoider')

        # Subscribe to laser scan
        self.scan_sub = rospy.Subscriber('/scan', LaserScan, self.scan_callback)

        # Publish velocity commands
        self.cmd_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

        self.safe_distance = 0.5  # meters
        self.linear_speed = 0.2
        self.angular_speed = 0.5

    def scan_callback(self, msg):
        """Process laser scan and avoid obstacles"""
        # Get minimum distance in front sector
        front_ranges = msg.ranges[len(msg.ranges)//4:3*len(msg.ranges)//4]
        min_distance = min(front_ranges)

        # Create velocity command
        cmd = Twist()

        if min_distance < self.safe_distance:
            # Obstacle detected - turn
            cmd.linear.x = 0.0
            cmd.angular.z = self.angular_speed
            rospy.loginfo(f"Obstacle at {min_distance:.2f}m - Turning")
        else:
            # Clear path - move forward
            cmd.linear.x = self.linear_speed
            cmd.angular.z = 0.0
            rospy.loginfo(f"Clear path - Moving forward")

        self.cmd_pub.publish(cmd)

    def run(self):
        rospy.spin()

if __name__ == '__main__':
    try:
        avoider = ObstacleAvoider()
        avoider.run()
    except rospy.ROSInterruptException:
        pass
```

### Camera Image Processing

```python
#!/usr/bin/env python3
import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import numpy as np

class LineFollower:
    def __init__(self):
        rospy.init_node('line_follower')

        self.bridge = CvBridge()

        # Subscribe to camera
        self.image_sub = rospy.Subscriber('/camera/image_raw', Image, self.image_callback)

        # Publish control commands
        self.cmd_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

    def image_callback(self, msg):
        """Process camera image to follow line"""
        # Convert ROS image to OpenCV
        cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")

        # Convert to HSV for color detection
        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

        # Define range for black line
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([180, 255, 50])

        # Create mask
        mask = cv2.inRange(hsv, lower_black, upper_black)

        # Find centroid of line
        M = cv2.moments(mask)
        if M['m00'] > 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])

            # Calculate error from center
            image_center = cv_image.shape[1] // 2
            error = cx - image_center

            # Proportional control
            Kp = 0.005
            angular_z = -Kp * error

            # Publish command
            cmd = Twist()
            cmd.linear.x = 0.2
            cmd.angular.z = angular_z
            self.cmd_pub.publish(cmd)

            rospy.loginfo(f"Line at x={cx}, error={error}")

if __name__ == '__main__':
    try:
        follower = LineFollower()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
```

## 3.4 ROS Services

### Creating a Service Server

```python
#!/usr/bin/env python3
import rospy
from std_srvs.srv import SetBool, SetBoolResponse

class RobotController:
    def __init__(self):
        rospy.init_node('robot_controller')

        self.enabled = False

        # Create service
        self.enable_service = rospy.Service(
            'enable_robot',
            SetBool,
            self.handle_enable
        )

        rospy.loginfo("Robot controller ready")

    def handle_enable(self, req):
        """Handle enable/disable requests"""
        self.enabled = req.data
        message = "Robot enabled" if self.enabled else "Robot disabled"
        rospy.loginfo(message)

        return SetBoolResponse(success=True, message=message)

if __name__ == '__main__':
    controller = RobotController()
    rospy.spin()
```

### Calling a Service

```python
#!/usr/bin/env python3
import rospy
from std_srvs.srv import SetBool

def enable_robot(enable):
    rospy.wait_for_service('enable_robot')
    try:
        enable_srv = rospy.ServiceProxy('enable_robot', SetBool)
        response = enable_srv(enable)
        rospy.loginfo(f"Service response: {response.message}")
    except rospy.ServiceException as e:
        rospy.logerr(f"Service call failed: {e}")

if __name__ == '__main__':
    rospy.init_node('robot_client')
    enable_robot(True)
```

## 3.5 Practical Task: Autonomous Navigator

### Task: Build a Complete Navigation System

```python
#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist, PoseStamped
from nav_msgs.msg import Odometry
import numpy as np
import tf.transformations as tf_trans

class AutonomousNavigator:
    def __init__(self):
        rospy.init_node('autonomous_navigator')

        # Robot state
        self.position = np.array([0.0, 0.0])
        self.yaw = 0.0
        self.goal = None
        self.min_obstacle_distance = float('inf')

        # Parameters
        self.goal_tolerance = 0.3  # meters
        self.safe_distance = 0.5
        self.max_linear_speed = 0.3
        self.max_angular_speed = 1.0

        # Subscribers
        rospy.Subscriber('/scan', LaserScan, self.scan_callback)
        rospy.Subscriber('/odom', Odometry, self.odom_callback)
        rospy.Subscriber('/goal', PoseStamped, self.goal_callback)

        # Publishers
        self.cmd_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

        # Control loop
        self.rate = rospy.Rate(10)  # 10 Hz

    def scan_callback(self, msg):
        """Update obstacle information"""
        self.min_obstacle_distance = min(msg.ranges)

    def odom_callback(self, msg):
        """Update robot pose"""
        self.position[0] = msg.pose.pose.position.x
        self.position[1] = msg.pose.pose.position.y

        # Extract yaw from quaternion
        orientation = msg.pose.pose.orientation
        quaternion = (orientation.x, orientation.y, orientation.z, orientation.w)
        euler = tf_trans.euler_from_quaternion(quaternion)
        self.yaw = euler[2]

    def goal_callback(self, msg):
        """Set new goal"""
        self.goal = np.array([
            msg.pose.position.x,
            msg.pose.position.y
        ])
        rospy.loginfo(f"New goal: {self.goal}")

    def navigate_to_goal(self):
        """Main navigation logic"""
        if self.goal is None:
            return Twist()  # No goal, stay still

        # Calculate distance and angle to goal
        dx = self.goal[0] - self.position[0]
        dy = self.goal[1] - self.position[1]
        distance = np.sqrt(dx**2 + dy**2)
        angle_to_goal = np.arctan2(dy, dx)

        # Angle error
        angle_error = angle_to_goal - self.yaw
        # Normalize to [-pi, pi]
        angle_error = np.arctan2(np.sin(angle_error), np.cos(angle_error))

        cmd = Twist()

        if distance < self.goal_tolerance:
            # Goal reached
            rospy.loginfo("Goal reached!")
            self.goal = None
            return cmd

        # Check for obstacles
        if self.min_obstacle_distance < self.safe_distance:
            # Obstacle avoidance
            cmd.linear.x = 0.0
            cmd.angular.z = self.max_angular_speed
            rospy.loginfo("Avoiding obstacle")
        else:
            # Move toward goal
            # Proportional control
            Kp_linear = 0.5
            Kp_angular = 2.0

            cmd.linear.x = min(Kp_linear * distance, self.max_linear_speed)
            cmd.angular.z = np.clip(
                Kp_angular * angle_error,
                -self.max_angular_speed,
                self.max_angular_speed
            )

            rospy.loginfo(f"Distance: {distance:.2f}m, Angle error: {np.rad2deg(angle_error):.1f}°")

        return cmd

    def run(self):
        """Main control loop"""
        while not rospy.is_shutdown():
            cmd = self.navigate_to_goal()
            self.cmd_pub.publish(cmd)
            self.rate.sleep()

if __name__ == '__main__':
    try:
        navigator = AutonomousNavigator()
        navigator.run()
    except rospy.ROSInterruptException:
        pass
```

### Exercise Questions

1. Add waypoint navigation (multiple sequential goals)
2. Implement a more sophisticated obstacle avoidance algorithm
3. Add recovery behaviors when stuck
4. Integrate mapping (SLAM) to remember explored areas

## Glossary

- **Node**: Independent process performing computation
- **Topic**: Named bus for message passing
- **Message**: Data structure for communication
- **Publisher**: Node that sends messages to a topic
- **Subscriber**: Node that receives messages from a topic
- **Service**: Synchronous request-reply communication
- **Action**: Asynchronous goal-based communication with feedback
- **Parameter Server**: Centralized configuration storage

## Checkpoint Quiz

<div className="quiz-container">

### Question 1
What is the main purpose of ROS topics?

A) Store configuration parameters
B) Asynchronous message passing between nodes
C) Synchronous request-reply communication
D) File system management

<details>
<summary>Show Answer</summary>
**Answer: B** - Topics provide asynchronous, many-to-many message passing.
</details>

### Question 2
When should you use a ROS service instead of a topic?

A) When you need continuous data streaming
B) When you need a synchronous request-reply
C) When multiple publishers are required
D) When data needs to be logged

<details>
<summary>Show Answer</summary>
**Answer: B** - Services are for synchronous request-reply interactions.
</details>

### Question 3
What does `rospy.spin()` do?

A) Rotates the robot
B) Keeps the node running and processing callbacks
C) Initializes the ROS master
D) Publishes messages continuously

<details>
<summary>Show Answer</summary>
**Answer: B** - `spin()` keeps the node alive and processes callbacks.
</details>

</div>

## AI Assistant Prompts for Deep Learning

1. "Explain the publish-subscribe pattern in ROS. Why is it better than direct function calls?"
2. "When should I use topics vs services vs actions in ROS? Give examples for each."
3. "How does the ROS master coordinate communication between nodes?"
4. "Walk me through building a complete ROS package from scratch."
5. "Explain tf (transform) frames in ROS and why they're important for robotics."

---

**Previous**: [Chapter 2: Mathematical Foundations](./chapter-02.md) | **Next**: [Chapter 4: Sensors and Perception](./chapter-04.md)
