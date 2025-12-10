---
sidebar_position: 5
title: Chapter 4 - Sensors and Perception Systems
---

# Chapter 4: Sensors and Perception Systems

<div className="chapter-actions">
  <button className="ai-button chat-button">💬 Ask Questions from This Chapter</button>
  <button className="ai-button personalize-button">✨ Personalize this Chapter for Me</button>
  <button className="ai-button translate-button">🌐 Translate to Urdu</button>
</div>

## Learning Objectives

- Understand different sensor types and their applications
- Process camera and depth sensor data
- Implement sensor fusion techniques
- Build perception pipelines for object detection
- Apply filtering techniques for noisy sensor data

## 4.1 Types of Sensors

### Exteroceptive Sensors (External Environment)

**1. Cameras**
- RGB cameras: Color images
- Stereo cameras: Depth from disparity
- Event cameras: High-speed motion

**2. Depth Sensors**
- LiDAR: Laser-based ranging
- Time-of-Flight (ToF): Infrared depth
- Structured light: Pattern projection

**3. Other Sensors**
- Ultrasonic: Close-range detection
- Radar: Weather-resistant ranging
- Microphones: Audio perception

### Proprioceptive Sensors (Internal State)

**1. Position & Orientation**
- Encoders: Joint angles
- IMU: Acceleration & rotation
- GPS: Global positioning

**2. Force & Touch**
- Force/Torque sensors: Contact forces
- Tactile sensors: Touch pressure
- Current sensors: Motor load

## 4.2 Camera-Based Perception

### Basic Image Processing

```python
import cv2
import numpy as np

class ImageProcessor:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)

    def detect_colored_object(self, frame, color_range):
        """Detect objects by color"""
        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create mask
        mask = cv2.inRange(hsv, color_range['lower'], color_range['upper'])

        # Find contours
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        detections = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500:  # Minimum size
                M = cv2.moments(contour)
                if M['m00'] > 0:
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                    detections.append({
                        'center': (cx, cy),
                        'area': area,
                        'contour': contour
                    })

        return detections

    def process_frame(self):
        """Main processing loop"""
        ret, frame = self.camera.read()
        if not ret:
            return None

        # Detect red objects
        red_range = {
            'lower': np.array([0, 100, 100]),
            'upper': np.array([10, 255, 255])
        }

        detections = self.detect_colored_object(frame, red_range)

        # Draw detections
        for det in detections:
            cv2.circle(frame, det['center'], 10, (0, 255, 0), -1)
            cv2.drawContours(frame, [det['contour']], -1, (0, 255, 0), 2)

        return frame, detections

# Example usage
processor = ImageProcessor()
while True:
    result = processor.process_frame()
    if result is not None:
        frame, detections = result
        cv2.imshow('Detection', frame)
        print(f"Detected {len(detections)} objects")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

processor.camera.release()
cv2.destroyAllWindows()
```

### Deep Learning Object Detection

```python
import cv2
import numpy as np

class YOLODetector:
    def __init__(self, weights_path, config_path, labels_path):
        """Initialize YOLO object detector"""
        self.net = cv2.dnn.readNet(weights_path, config_path)

        with open(labels_path, 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]

        self.confidence_threshold = 0.5
        self.nms_threshold = 0.4

    def detect(self, frame):
        """Detect objects in frame"""
        height, width = frame.shape[:2]

        # Create blob
        blob = cv2.dnn.blobFromImage(
            frame, 1/255.0, (416, 416),
            swapRB=True, crop=False
        )

        self.net.setInput(blob)

        # Get output layer names
        layer_names = self.net.getLayerNames()
        output_layers = [layer_names[i - 1]
                        for i in self.net.getUnconnectedOutLayers()]

        # Forward pass
        outputs = self.net.forward(output_layers)

        # Process detections
        boxes = []
        confidences = []
        class_ids = []

        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > self.confidence_threshold:
                    # Get box coordinates
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        # Apply NMS
        indices = cv2.dnn.NMSBoxes(
            boxes, confidences,
            self.confidence_threshold,
            self.nms_threshold
        )

        detections = []
        if len(indices) > 0:
            for i in indices.flatten():
                detections.append({
                    'box': boxes[i],
                    'confidence': confidences[i],
                    'class_id': class_ids[i],
                    'class_name': self.classes[class_ids[i]]
                })

        return detections
```

## 4.3 LiDAR Processing

### Point Cloud Processing

```python
import numpy as np

class LiDARProcessor:
    def __init__(self):
        self.min_range = 0.1  # meters
        self.max_range = 10.0

    def polar_to_cartesian(self, ranges, angles):
        """Convert polar coordinates to Cartesian"""
        points = []
        for r, theta in zip(ranges, angles):
            if self.min_range < r < self.max_range:
                x = r * np.cos(theta)
                y = r * np.sin(theta)
                points.append([x, y])
        return np.array(points)

    def cluster_points(self, points, eps=0.3, min_samples=5):
        """Cluster points using DBSCAN"""
        from sklearn.cluster import DBSCAN

        if len(points) == 0:
            return []

        clustering = DBSCAN(eps=eps, min_samples=min_samples)
        labels = clustering.fit_predict(points)

        clusters = []
        for label in set(labels):
            if label == -1:  # Noise
                continue
            cluster_points = points[labels == label]
            clusters.append(cluster_points)

        return clusters

    def detect_obstacles(self, scan_msg):
        """Detect obstacles from laser scan"""
        # Convert ranges to Cartesian points
        num_readings = len(scan_msg.ranges)
        angles = np.linspace(
            scan_msg.angle_min,
            scan_msg.angle_max,
            num_readings
        )

        points = self.polar_to_cartesian(scan_msg.ranges, angles)

        # Cluster points into obstacles
        clusters = self.cluster_points(points)

        obstacles = []
        for cluster in clusters:
            # Calculate obstacle properties
            centroid = np.mean(cluster, axis=0)
            size = np.max(cluster, axis=0) - np.min(cluster, axis=0)

            obstacles.append({
                'position': centroid,
                'size': size,
                'points': cluster
            })

        return obstacles
```

## 4.4 Sensor Fusion

### Kalman Filter for Sensor Fusion

```python
import numpy as np

class KalmanFilter:
    def __init__(self, dt):
        """
        Initialize Kalman filter for position tracking
        State: [x, y, vx, vy]
        """
        self.dt = dt

        # State transition matrix
        self.A = np.array([
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

        # Measurement matrix (measure position only)
        self.H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ])

        # Process noise covariance
        self.Q = np.eye(4) * 0.1

        # Measurement noise covariance
        self.R = np.eye(2) * 0.5

        # State estimate
        self.x = np.zeros(4)

        # Covariance matrix
        self.P = np.eye(4)

    def predict(self):
        """Prediction step"""
        self.x = self.A @ self.x
        self.P = self.A @ self.P @ self.A.T + self.Q

    def update(self, measurement):
        """Update step with measurement"""
        # Innovation
        y = measurement - self.H @ self.x

        # Innovation covariance
        S = self.H @ self.P @ self.H.T + self.R

        # Kalman gain
        K = self.P @ self.H.T @ np.linalg.inv(S)

        # Update state
        self.x = self.x + K @ y

        # Update covariance
        I = np.eye(4)
        self.P = (I - K @ self.H) @ self.P

    def get_state(self):
        """Get current state estimate"""
        return {
            'position': self.x[:2],
            'velocity': self.x[2:]
        }

# Example usage
kf = KalmanFilter(dt=0.1)

# Simulate noisy measurements
true_position = np.array([0.0, 0.0])
true_velocity = np.array([1.0, 0.5])

for t in range(100):
    # Predict
    kf.predict()

    # True position with constant velocity
    true_position += true_velocity * 0.1

    # Noisy measurement
    noise = np.random.randn(2) * 0.5
    measurement = true_position + noise

    # Update with measurement
    kf.update(measurement)

    state = kf.get_state()
    print(f"t={t*0.1:.1f}: True={true_position}, Estimate={state['position']}")
```

## 4.5 Practical Task: Multi-Sensor Object Tracker

### Task: Fuse Camera and LiDAR Data

```python
import numpy as np
import cv2

class MultiSensorTracker:
    def __init__(self):
        self.trackers = {}  # Object ID -> Kalman Filter
        self.next_id = 0

    def match_detections(self, camera_dets, lidar_dets, max_distance=1.0):
        """Match camera and LiDAR detections"""
        matches = []

        for cam_det in camera_dets:
            cam_pos = cam_det['position_3d']  # Assume we have 3D position

            best_match = None
            best_distance = max_distance

            for lidar_det in lidar_dets:
                lidar_pos = lidar_det['position']
                distance = np.linalg.norm(cam_pos[:2] - lidar_pos)

                if distance < best_distance:
                    best_distance = distance
                    best_match = lidar_det

            if best_match is not None:
                matches.append({
                    'camera': cam_det,
                    'lidar': best_match,
                    'fused_position': (cam_pos + np.append(best_match['position'], 0)) / 2
                })

        return matches

    def update_trackers(self, matched_detections):
        """Update or create trackers"""
        for match in matched_detections:
            # Simple nearest-neighbor association
            position = match['fused_position'][:2]

            # Find closest existing tracker
            best_id = None
            best_distance = 2.0  # Maximum association distance

            for obj_id, tracker in self.trackers.items():
                track_pos = tracker.get_state()['position']
                distance = np.linalg.norm(position - track_pos)

                if distance < best_distance:
                    best_distance = distance
                    best_id = obj_id

            if best_id is not None:
                # Update existing tracker
                self.trackers[best_id].predict()
                self.trackers[best_id].update(position)
            else:
                # Create new tracker
                new_tracker = KalmanFilter(dt=0.1)
                new_tracker.update(position)
                self.trackers[self.next_id] = new_tracker
                self.next_id += 1

    def get_tracked_objects(self):
        """Get all tracked objects"""
        objects = []
        for obj_id, tracker in self.trackers.items():
            state = tracker.get_state()
            objects.append({
                'id': obj_id,
                'position': state['position'],
                'velocity': state['velocity']
            })
        return objects
```

## Glossary

- **Sensor Fusion**: Combining data from multiple sensors
- **Point Cloud**: Set of 3D points from LiDAR/depth sensors
- **Kalman Filter**: Optimal estimator for linear systems
- **NMS (Non-Maximum Suppression)**: Removing duplicate detections
- **Feature Extraction**: Identifying distinctive image patterns
- **Depth Estimation**: Computing distance to objects
- **IMU**: Inertial Measurement Unit (accelerometer + gyroscope)

## Checkpoint Quiz

<div className="quiz-container">

### Question 1
What is the main advantage of sensor fusion?

A) Reduces cost
B) Increases reliability and accuracy
C) Simplifies processing
D) Reduces power consumption

<details>
<summary>Show Answer</summary>
**Answer: B** - Sensor fusion combines complementary sensors for better reliability.
</details>

### Question 2
Which sensor type is best for accurate long-range distance measurement?

A) Ultrasonic
B) Camera
C) LiDAR
D) Tactile

<details>
<summary>Show Answer</summary>
**Answer: C** - LiDAR provides accurate long-range distance measurements.
</details>

### Question 3
What does a Kalman filter do?

A) Removes noise from images
B) Estimates system state from noisy measurements
C) Detects objects in images
D) Controls motor speed

<details>
<summary>Show Answer</summary>
**Answer: B** - Kalman filters optimally estimate state from noisy sensor data.
</details>

</div>

## AI Assistant Prompts for Deep Learning

1. "Explain how stereo vision works to estimate depth. Include the mathematical principles."
2. "Compare LiDAR vs cameras for autonomous robots. What are the trade-offs?"
3. "Walk me through implementing a Kalman filter for robot localization step by step."
4. "How does sensor fusion improve object detection compared to using a single sensor?"
5. "Explain the challenges of processing real-time sensor data in robotics applications."

---

**Previous**: [Chapter 3: Programming for Robotics](./chapter-03.md) | **Next**: [Chapter 5: Actuators and Control](./chapter-05.md)
