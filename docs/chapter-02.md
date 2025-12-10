---
sidebar_position: 3
title: Chapter 2 - Mathematical Foundations for Robotics
---

# Chapter 2: Mathematical Foundations for Robotics

<div className="chapter-actions">
  <button className="ai-button chat-button">💬 Ask Questions from This Chapter</button>
  <button className="ai-button personalize-button">✨ Personalize this Chapter for Me</button>
  <button className="ai-button translate-button">🌐 Translate to Urdu</button>
</div>

## Learning Objectives

By the end of this chapter, you will be able to:

- Apply linear algebra to represent robot positions and orientations
- Use transformation matrices for coordinate frame conversions
- Understand rotation representations (matrices, quaternions, Euler angles)
- Calculate forward and inverse kinematics for simple robots
- Apply calculus concepts to robot motion and dynamics

## 2.1 Vectors and Coordinate Frames

### Position Vectors

A robot's position in 3D space is represented as a vector:

```
p = [x, y, z]ᵀ
```

```python
import numpy as np

# Position of robot end-effector
position = np.array([1.5, 2.0, 0.5])  # meters

# Distance from origin
distance = np.linalg.norm(position)
print(f"Distance from origin: {distance:.2f}m")
```

### Coordinate Frames

Multiple coordinate frames are essential in robotics:

```
World Frame (W)
    ↓
  Base Frame (B)
    ↓
 Joint Frame (J)
    ↓
End-Effector Frame (E)
```

**Example**: Robot arm on a mobile base
- World frame: Fixed in the environment
- Base frame: Attached to the mobile base
- End-effector frame: At the gripper

## 2.2 Rotation Representations

### Rotation Matrices

A 3D rotation is represented by a 3×3 orthogonal matrix:

```python
def rotation_matrix_z(theta):
    """Rotation around Z-axis by angle theta (radians)"""
    c = np.cos(theta)
    s = np.sin(theta)
    return np.array([
        [c, -s, 0],
        [s,  c, 0],
        [0,  0, 1]
    ])

def rotation_matrix_y(theta):
    """Rotation around Y-axis"""
    c = np.cos(theta)
    s = np.sin(theta)
    return np.array([
        [ c, 0, s],
        [ 0, 1, 0],
        [-s, 0, c]
    ])

def rotation_matrix_x(theta):
    """Rotation around X-axis"""
    c = np.cos(theta)
    s = np.sin(theta)
    return np.array([
        [1,  0,  0],
        [0,  c, -s],
        [0,  s,  c]
    ])

# Example: Rotate 90 degrees around Z-axis
theta = np.pi / 2  # 90 degrees
R = rotation_matrix_z(theta)
print("Rotation matrix:")
print(R)

# Apply rotation to a point
point = np.array([1, 0, 0])
rotated_point = R @ point
print(f"Original: {point}")
print(f"Rotated: {rotated_point}")
```

### Euler Angles

Represent rotation as three sequential rotations:

```python
def euler_to_rotation_matrix(roll, pitch, yaw):
    """
    Convert Euler angles (ZYX convention) to rotation matrix
    roll: rotation around X
    pitch: rotation around Y
    yaw: rotation around Z
    """
    R_x = rotation_matrix_x(roll)
    R_y = rotation_matrix_y(pitch)
    R_z = rotation_matrix_z(yaw)

    # Combined rotation: R = Rz * Ry * Rx
    R = R_z @ R_y @ R_x
    return R

# Example
roll = np.deg2rad(10)
pitch = np.deg2rad(20)
yaw = np.deg2rad(30)

R = euler_to_rotation_matrix(roll, pitch, yaw)
print("Rotation from Euler angles:")
print(R)
```

### Quaternions

Quaternions avoid gimbal lock and are computationally efficient:

```python
class Quaternion:
    def __init__(self, w, x, y, z):
        self.w = w  # scalar part
        self.x = x  # vector part
        self.y = y
        self.z = z

    def normalize(self):
        """Normalize to unit quaternion"""
        norm = np.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)
        self.w /= norm
        self.x /= norm
        self.y /= norm
        self.z /= norm

    def to_rotation_matrix(self):
        """Convert quaternion to rotation matrix"""
        w, x, y, z = self.w, self.x, self.y, self.z

        R = np.array([
            [1-2*(y**2+z**2), 2*(x*y-w*z), 2*(x*z+w*y)],
            [2*(x*y+w*z), 1-2*(x**2+z**2), 2*(y*z-w*x)],
            [2*(x*z-w*y), 2*(y*z+w*x), 1-2*(x**2+y**2)]
        ])
        return R

    @staticmethod
    def from_axis_angle(axis, angle):
        """Create quaternion from axis-angle representation"""
        axis = axis / np.linalg.norm(axis)  # normalize
        half_angle = angle / 2
        w = np.cos(half_angle)
        x = axis[0] * np.sin(half_angle)
        y = axis[1] * np.sin(half_angle)
        z = axis[2] * np.sin(half_angle)
        return Quaternion(w, x, y, z)

# Example: 90 degree rotation around Z-axis
axis = np.array([0, 0, 1])
angle = np.pi / 2
q = Quaternion.from_axis_angle(axis, angle)
print(f"Quaternion: [{q.w:.3f}, {q.x:.3f}, {q.y:.3f}, {q.z:.3f}]")
print("Rotation matrix from quaternion:")
print(q.to_rotation_matrix())
```

## 2.3 Homogeneous Transformations

Combine rotation and translation in a single 4×4 matrix:

```python
def homogeneous_transform(R, p):
    """
    Create 4x4 homogeneous transformation matrix
    R: 3x3 rotation matrix
    p: 3x1 position vector
    """
    T = np.eye(4)
    T[0:3, 0:3] = R
    T[0:3, 3] = p
    return T

# Example: Transform from base to end-effector
R_be = rotation_matrix_z(np.pi / 4)  # 45 degree rotation
p_be = np.array([1.0, 0.5, 0.3])     # position offset

T_be = homogeneous_transform(R_be, p_be)
print("Homogeneous transformation:")
print(T_be)

# Transform a point from end-effector frame to base frame
point_in_ee = np.array([0.1, 0.0, 0.0, 1.0])  # homogeneous coordinates
point_in_base = T_be @ point_in_ee
print(f"Point in base frame: {point_in_base[0:3]}")
```

## 2.4 Forward Kinematics

Calculate end-effector position from joint angles:

```python
class TwoLinkArm:
    def __init__(self, L1, L2):
        self.L1 = L1  # length of first link
        self.L2 = L2  # length of second link

    def forward_kinematics(self, theta1, theta2):
        """
        Calculate end-effector position from joint angles
        theta1: angle of joint 1 (radians)
        theta2: angle of joint 2 (radians)
        Returns: (x, y) position of end-effector
        """
        x = self.L1 * np.cos(theta1) + self.L2 * np.cos(theta1 + theta2)
        y = self.L1 * np.sin(theta1) + self.L2 * np.sin(theta1 + theta2)
        return x, y

# Example
arm = TwoLinkArm(L1=1.0, L2=0.8)
theta1 = np.deg2rad(30)
theta2 = np.deg2rad(45)

x, y = arm.forward_kinematics(theta1, theta2)
print(f"End-effector position: ({x:.3f}, {y:.3f})")
```

## 2.5 Inverse Kinematics

Calculate joint angles from desired end-effector position:

```python
class TwoLinkArmIK(TwoLinkArm):
    def inverse_kinematics(self, x, y):
        """
        Calculate joint angles from end-effector position
        Returns: (theta1, theta2) or None if unreachable
        """
        # Check if point is reachable
        distance = np.sqrt(x**2 + y**2)
        if distance > (self.L1 + self.L2) or distance < abs(self.L1 - self.L2):
            return None  # unreachable

        # Law of cosines for theta2
        cos_theta2 = (x**2 + y**2 - self.L1**2 - self.L2**2) / (2 * self.L1 * self.L2)
        cos_theta2 = np.clip(cos_theta2, -1, 1)  # handle numerical errors
        theta2 = np.arccos(cos_theta2)

        # Calculate theta1
        k1 = self.L1 + self.L2 * np.cos(theta2)
        k2 = self.L2 * np.sin(theta2)
        theta1 = np.arctan2(y, x) - np.arctan2(k2, k1)

        return theta1, theta2

# Example
arm_ik = TwoLinkArmIK(L1=1.0, L2=0.8)
target_x, target_y = 1.5, 0.5

result = arm_ik.inverse_kinematics(target_x, target_y)
if result:
    theta1, theta2 = result
    print(f"Joint angles: theta1={np.rad2deg(theta1):.1f}°, theta2={np.rad2deg(theta2):.1f}°")

    # Verify with forward kinematics
    x_verify, y_verify = arm_ik.forward_kinematics(theta1, theta2)
    print(f"Verification: ({x_verify:.3f}, {y_verify:.3f})")
else:
    print("Target unreachable!")
```

## 2.6 Practical Task: 3D Arm Simulator

### Task: Implement a 3-Link Robot Arm

```python
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class ThreeLinkArm3D:
    def __init__(self, L1, L2, L3):
        self.lengths = [L1, L2, L3]

    def forward_kinematics_3d(self, theta1, theta2, theta3):
        """
        Calculate 3D position of end-effector
        theta1: rotation around Z (base rotation)
        theta2: shoulder pitch
        theta3: elbow pitch
        """
        # Joint positions
        joints = [np.array([0, 0, 0])]  # base

        # Joint 1: base rotation
        x1 = 0
        y1 = 0
        z1 = self.lengths[0]
        joints.append(np.array([x1, y1, z1]))

        # Joint 2: shoulder
        x2 = self.lengths[1] * np.cos(theta2) * np.cos(theta1)
        y2 = self.lengths[1] * np.cos(theta2) * np.sin(theta1)
        z2 = z1 + self.lengths[1] * np.sin(theta2)
        joints.append(np.array([x2, y2, z2]))

        # End-effector: elbow
        x3 = x2 + self.lengths[2] * np.cos(theta2 + theta3) * np.cos(theta1)
        y3 = y2 + self.lengths[2] * np.cos(theta2 + theta3) * np.sin(theta1)
        z3 = z2 + self.lengths[2] * np.sin(theta2 + theta3)
        joints.append(np.array([x3, y3, z3]))

        return joints

    def plot_arm(self, theta1, theta2, theta3):
        """Visualize the arm configuration"""
        joints = self.forward_kinematics_3d(theta1, theta2, theta3)

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')

        # Plot links
        for i in range(len(joints) - 1):
            ax.plot([joints[i][0], joints[i+1][0]],
                   [joints[i][1], joints[i+1][1]],
                   [joints[i][2], joints[i+1][2]],
                   'b-', linewidth=3)

        # Plot joints
        joints_array = np.array(joints)
        ax.scatter(joints_array[:, 0], joints_array[:, 1], joints_array[:, 2],
                  c='red', s=100)

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('3-Link Robot Arm')

        # Set equal aspect ratio
        max_range = sum(self.lengths)
        ax.set_xlim([-max_range, max_range])
        ax.set_ylim([-max_range, max_range])
        ax.set_zlim([0, max_range])

        plt.show()

# Example usage
arm = ThreeLinkArm3D(L1=0.5, L2=1.0, L3=0.8)
joints = arm.forward_kinematics_3d(
    theta1=np.deg2rad(30),  # base rotation
    theta2=np.deg2rad(45),  # shoulder pitch
    theta3=np.deg2rad(-30)  # elbow pitch
)

print("Joint positions:")
for i, joint in enumerate(joints):
    print(f"Joint {i}: {joint}")

# Uncomment to visualize:
# arm.plot_arm(np.deg2rad(30), np.deg2rad(45), np.deg2rad(-30))
```

### Exercise Questions

1. Add a 4th link to create a more dexterous arm
2. Implement velocity kinematics (Jacobian matrix)
3. Create an animation of the arm moving through a trajectory
4. Add collision detection between links

## Glossary

- **Degree of Freedom (DOF)**: Number of independent parameters defining configuration
- **Euler Angles**: Three angles representing rotation (roll, pitch, yaw)
- **Forward Kinematics**: Computing end-effector pose from joint angles
- **Gimbal Lock**: Loss of one degree of freedom in Euler angle representation
- **Homogeneous Coordinates**: 4D representation combining position and rotation
- **Inverse Kinematics**: Computing joint angles from desired end-effector pose
- **Quaternion**: 4D representation of rotation avoiding gimbal lock
- **Workspace**: Set of all reachable end-effector positions

## Checkpoint Quiz

<div className="quiz-container">

### Question 1
What is the advantage of homogeneous transformations?

A) They use less memory
B) They combine rotation and translation in one matrix
C) They are faster to compute
D) They only work in 2D

<details>
<summary>Show Answer</summary>
**Answer: B** - Homogeneous transformations combine both rotation and translation.
</details>

### Question 2
Why are quaternions preferred over Euler angles for robot control?

A) They are easier to understand
B) They avoid gimbal lock
C) They require less computation
D) They work only in 2D

<details>
<summary>Show Answer</summary>
**Answer: B** - Quaternions avoid the gimbal lock problem inherent in Euler angles.
</details>

### Question 3
In forward kinematics, what are the inputs and outputs?

A) Input: position, Output: angles
B) Input: angles, Output: position
C) Input: velocity, Output: acceleration
D) Input: force, Output: torque

<details>
<summary>Show Answer</summary>
**Answer: B** - Forward kinematics takes joint angles as input and outputs end-effector position.
</details>

</div>

## AI Assistant Prompts for Deep Learning

1. "Explain why we need multiple rotation representations. When would I use each one?"
2. "Walk me through the derivation of inverse kinematics for a 2-link arm step by step."
3. "What is gimbal lock and how does it affect robot control? Give a concrete example."
4. "How do homogeneous transformations simplify calculations with multiple coordinate frames?"
5. "Explain the difference between the workspace and configuration space of a robot."

---

**Previous**: [Chapter 1: Fundamentals](./chapter-01.md) | **Next**: [Chapter 3: Programming for Robotics](./chapter-03.md)
