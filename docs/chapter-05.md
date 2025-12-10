---
sidebar_position: 6
title: Chapter 5 - Actuators and Control Systems
---

# Chapter 5: Actuators and Control Systems

<div className="chapter-actions">
  <button className="ai-button chat-button">💬 Ask Questions from This Chapter</button>
  <button className="ai-button personalize-button">✨ Personalize this Chapter for Me</button>
  <button className="ai-button translate-button">🌐 Translate to Urdu</button>
</div>

## Learning Objectives

- Understand different types of actuators for robotics
- Implement PID control for motor control
- Design control systems for robotic joints
- Apply feedforward and feedback control strategies
- Build trajectory following controllers

## 5.1 Types of Actuators

### Electric Motors

**DC Motors**
- Simple speed control
- Cost-effective
- Used in mobile robots

**Servo Motors**
- Position control
- Feedback built-in
- Common in robot arms

**Stepper Motors**
- Precise positioning
- Open-loop control
- 3D printers, CNC

### Other Actuator Types

**Hydraulic**
- Very high force
- Heavy-duty applications
- Excavators, large robots

**Pneumatic**
- Compliant motion
- Soft robotics
- Grippers

## 5.2 PID Control

### Understanding PID

```python
import numpy as np
import matplotlib.pyplot as plt

class PIDController:
    def __init__(self, Kp, Ki, Kd, setpoint=0):
        """
        Proportional-Integral-Derivative Controller
        Kp: Proportional gain
        Ki: Integral gain
        Kd: Derivative gain
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint

        self.integral = 0
        self.previous_error = 0

    def update(self, measurement, dt):
        """
        Calculate control output
        measurement: Current process value
        dt: Time step
        """
        # Error
        error = self.setpoint - measurement

        # Proportional term
        P = self.Kp * error

        # Integral term
        self.integral += error * dt
        I = self.Ki * self.integral

        # Derivative term
        derivative = (error - self.previous_error) / dt
        D = self.Kd * derivative

        # Calculate output
        output = P + I + D

        # Save error for next iteration
        self.previous_error = error

        return output

    def set_setpoint(self, setpoint):
        """Update target setpoint"""
        self.setpoint = setpoint

    def reset(self):
        """Reset controller state"""
        self.integral = 0
        self.previous_error = 0

# Example: Position control simulation
class Motor:
    def __init__(self):
        self.position = 0
        self.velocity = 0
        self.damping = 0.5

    def apply_force(self, force, dt):
        """Update motor state"""
        # Simple dynamics
        acceleration = force - self.damping * self.velocity
        self.velocity += acceleration * dt
        self.position += self.velocity * dt

# Simulation
motor = Motor()
pid = PIDController(Kp=10, Ki=1, Kd=5, setpoint=10)

dt = 0.01
time = np.arange(0, 5, dt)
positions = []
setpoints = []

for t in time:
    # Calculate control
    control = pid.update(motor.position, dt)

    # Apply to motor
    motor.apply_force(control, dt)

    positions.append(motor.position)
    setpoints.append(pid.setpoint)

# Plot results
plt.figure(figsize=(10, 6))
plt.plot(time, positions, label='Actual Position')
plt.plot(time, setpoints, '--', label='Setpoint')
plt.xlabel('Time (s)')
plt.ylabel('Position')
plt.title('PID Position Control')
plt.legend()
plt.grid(True)
# plt.show()
```

### Tuning PID Controllers

**Ziegler-Nichols Method:**

```python
def tune_pid_zn(Ku, Tu):
    """
    Ziegler-Nichols tuning method
    Ku: Ultimate gain (where system oscillates)
    Tu: Ultimate period
    """
    Kp = 0.6 * Ku
    Ki = 2 * Kp / Tu
    Kd = Kp * Tu / 8

    return Kp, Ki, Kd

# Example
Ku = 15  # Found experimentally
Tu = 0.5  # seconds

Kp, Ki, Kd = tune_pid_zn(Ku, Tu)
print(f"Tuned PID gains: Kp={Kp}, Ki={Ki}, Kd={Kd}")
```

## 5.3 Joint Control

### Single Joint Controller

```python
class JointController:
    def __init__(self, joint_name, Kp=10, Ki=1, Kd=5):
        self.joint_name = joint_name
        self.pid = PIDController(Kp, Ki, Kd)

        self.current_position = 0
        self.current_velocity = 0
        self.max_torque = 100  # Nm

    def set_target(self, target_position):
        """Set target joint angle"""
        self.pid.set_setpoint(target_position)

    def update(self, measured_position, measured_velocity, dt):
        """Calculate torque command"""
        self.current_position = measured_position
        self.current_velocity = measured_velocity

        # PID control
        torque = self.pid.update(measured_position, dt)

        # Limit torque
        torque = np.clip(torque, -self.max_torque, self.max_torque)

        return torque

# Example: Control multiple joints
class RobotArmController:
    def __init__(self, num_joints):
        self.joints = []
        for i in range(num_joints):
            controller = JointController(f"joint_{i}", Kp=20, Ki=2, Kd=10)
            self.joints.append(controller)

    def set_joint_targets(self, target_angles):
        """Set target angles for all joints"""
        for joint, target in zip(self.joints, target_angles):
            joint.set_target(target)

    def update_all(self, measured_angles, measured_velocities, dt):
        """Update all joint controllers"""
        torques = []
        for joint, angle, velocity in zip(
            self.joints, measured_angles, measured_velocities
        ):
            torque = joint.update(angle, velocity, dt)
            torques.append(torque)
        return torques
```

## 5.4 Trajectory Following

### Trajectory Generation

```python
class TrajectoryGenerator:
    @staticmethod
    def quintic_polynomial(q0, qf, v0, vf, a0, af, T):
        """
        Generate quintic polynomial trajectory
        q0, qf: initial and final position
        v0, vf: initial and final velocity
        a0, af: initial and final acceleration
        T: total time
        """
        # Solve for coefficients
        A = np.array([
            [1, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0],
            [0, 0, 2, 0, 0, 0],
            [1, T, T**2, T**3, T**4, T**5],
            [0, 1, 2*T, 3*T**2, 4*T**3, 5*T**4],
            [0, 0, 2, 6*T, 12*T**2, 20*T**3]
        ])

        b = np.array([q0, v0, a0, qf, vf, af])
        coeffs = np.linalg.solve(A, b)

        return coeffs

    @staticmethod
    def evaluate_trajectory(coeffs, t):
        """Evaluate position, velocity, acceleration at time t"""
        position = sum(coeffs[i] * t**i for i in range(6))
        velocity = sum(i * coeffs[i] * t**(i-1) for i in range(1, 6))
        acceleration = sum(i * (i-1) * coeffs[i] * t**(i-2) for i in range(2, 6))

        return position, velocity, acceleration

# Example usage
traj_gen = TrajectoryGenerator()

# Generate trajectory from 0 to 90 degrees in 2 seconds
coeffs = traj_gen.quintic_polynomial(
    q0=0, qf=np.pi/2,  # 0 to 90 degrees
    v0=0, vf=0,         # start and end at rest
    a0=0, af=0,         # zero acceleration at ends
    T=2.0               # 2 seconds
)

# Sample trajectory
time_steps = np.linspace(0, 2.0, 100)
positions = []
velocities = []
accelerations = []

for t in time_steps:
    pos, vel, acc = traj_gen.evaluate_trajectory(coeffs, t)
    positions.append(pos)
    velocities.append(vel)
    accelerations.append(acc)

# Plot
fig, axes = plt.subplots(3, 1, figsize=(10, 10))
axes[0].plot(time_steps, np.rad2deg(positions))
axes[0].set_ylabel('Position (deg)')
axes[0].grid(True)

axes[1].plot(time_steps, velocities)
axes[1].set_ylabel('Velocity (rad/s)')
axes[1].grid(True)

axes[2].plot(time_steps, accelerations)
axes[2].set_ylabel('Acceleration (rad/s²)')
axes[2].set_xlabel('Time (s)')
axes[2].grid(True)
# plt.show()
```

### Trajectory Tracking Controller

```python
class TrajectoryTrackingController:
    def __init__(self, Kp_pos=100, Kd_vel=20):
        """
        PD controller with feedforward for trajectory tracking
        """
        self.Kp = Kp_pos
        self.Kd = Kd_vel

    def compute_torque(self, desired_state, actual_state):
        """
        Compute control torque
        desired_state: (position, velocity, acceleration)
        actual_state: (position, velocity)
        """
        q_des, qd_des, qdd_des = desired_state
        q_actual, qd_actual = actual_state

        # Position error
        e_pos = q_des - q_actual

        # Velocity error
        e_vel = qd_des - qd_actual

        # PD + Feedforward control
        # τ = Kp*(q_des - q) + Kd*(qd_des - qd) + qdd_des
        torque = self.Kp * e_pos + self.Kd * e_vel + qdd_des

        return torque

# Example: Track trajectory
tracker = TrajectoryTrackingController(Kp_pos=150, Kd_vel=30)

# Simulate tracking
dt = 0.01
time = np.arange(0, 2.0, dt)
actual_position = 0
actual_velocity = 0

tracked_positions = []

for t in time:
    # Get desired state from trajectory
    desired = traj_gen.evaluate_trajectory(coeffs, t)

    # Compute control
    torque = tracker.compute_torque(
        desired_state=desired,
        actual_state=(actual_position, actual_velocity)
    )

    # Simple dynamics simulation
    actual_velocity += torque * dt
    actual_position += actual_velocity * dt

    tracked_positions.append(actual_position)

plt.figure(figsize=(10, 6))
plt.plot(time_steps, np.rad2deg(positions), '--', label='Desired')
plt.plot(time, np.rad2deg(tracked_positions), label='Actual')
plt.xlabel('Time (s)')
plt.ylabel('Position (deg)')
plt.title('Trajectory Tracking')
plt.legend()
plt.grid(True)
# plt.show()
```

## 5.5 Practical Task: Robot Arm Position Control

```python
import numpy as np

class SimulatedRobotArm:
    def __init__(self, num_joints=3):
        self.num_joints = num_joints
        self.positions = np.zeros(num_joints)
        self.velocities = np.zeros(num_joints)
        self.inertia = np.ones(num_joints) * 0.5
        self.damping = np.ones(num_joints) * 2.0

    def apply_torques(self, torques, dt):
        """Update arm state with applied torques"""
        # Simple dynamics: τ = I*α + D*ω
        accelerations = (torques - self.damping * self.velocities) / self.inertia
        self.velocities += accelerations * dt
        self.positions += self.velocities * dt

    def get_state(self):
        return self.positions.copy(), self.velocities.copy()

# Complete control system
arm = SimulatedRobotArm(num_joints=3)
controller = RobotArmController(num_joints=3)

# Set target configuration
target_angles = np.array([np.pi/4, np.pi/3, -np.pi/6])  # radians
controller.set_joint_targets(target_angles)

# Simulation
dt = 0.01
num_steps = 500
time = np.arange(0, num_steps * dt, dt)

history = {'positions': [], 'targets': []}

for step in range(num_steps):
    # Get current state
    positions, velocities = arm.get_state()

    # Compute control torques
    torques = controller.update_all(positions, velocities, dt)

    # Apply to arm
    arm.apply_torques(np.array(torques), dt)

    # Record history
    history['positions'].append(positions.copy())
    history['targets'].append(target_angles.copy())

# Plot results
history['positions'] = np.array(history['positions'])
history['targets'] = np.array(history['targets'])

fig, axes = plt.subplots(3, 1, figsize=(10, 10))
for i in range(3):
    axes[i].plot(time, np.rad2deg(history['positions'][:, i]), label=f'Joint {i+1} Actual')
    axes[i].plot(time, np.rad2deg(history['targets'][:, i]), '--', label=f'Joint {i+1} Target')
    axes[i].set_ylabel(f'Joint {i+1} (deg)')
    axes[i].legend()
    axes[i].grid(True)

axes[-1].set_xlabel('Time (s)')
plt.tight_layout()
# plt.show()
```

## Glossary

- **Actuator**: Device that converts energy to motion
- **Torque**: Rotational force
- **PID**: Proportional-Integral-Derivative controller
- **Feedforward**: Control based on desired trajectory
- **Feedback**: Control based on measured error
- **Trajectory**: Planned path over time
- **Setpoint**: Desired target value

## Checkpoint Quiz

<div className="quiz-container">

### Question 1
What does the "P" in PID stand for and what does it do?

A) Power - controls motor power
B) Proportional - responds to current error
C) Position - tracks position
D) Pulse - generates pulses

<details>
<summary>Show Answer</summary>
**Answer: B** - Proportional term responds proportionally to current error.
</details>

### Question 2
Why is the derivative term useful in PID control?

A) It eliminates steady-state error
B) It dampens oscillations and improves stability
C) It increases response speed
D) It reduces computation time

<details>
<summary>Show Answer</summary>
**Answer: B** - Derivative term provides damping to reduce oscillations.
</details>

### Question 3
What is the main advantage of trajectory following over simple position control?

A) Simpler implementation
B) Lower computational cost
C) Smooth motion with velocity and acceleration control
D) No sensors required

<details>
<summary>Show Answer</summary>
**Answer: C** - Trajectory following ensures smooth motion with proper dynamics.
</details>

</div>

## AI Assistant Prompts for Deep Learning

1. "Explain each term of PID (P, I, D) with physical intuition and when each is needed."
2. "Walk me through tuning a PID controller for a real robot joint step by step."
3. "Compare feedforward vs feedback control. When would you use each approach?"
4. "How does trajectory generation ensure smooth robot motion? Explain quintic polynomials."
5. "What are the challenges of controlling multiple joints simultaneously in a robot arm?"

---

**Previous**: [Chapter 4: Sensors and Perception](./chapter-04.md) | **Next**: [Chapter 6: Machine Learning for Robotics](./chapter-06.md)
