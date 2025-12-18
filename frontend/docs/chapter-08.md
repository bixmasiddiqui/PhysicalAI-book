---
sidebar_position: 9
title: Chapter 8 - Computer Vision for Robotics
---

# Chapter 8: Computer Vision for Robotics

<div className="chapter-actions">
  <button className="ai-button chat-button">💬 Ask Questions from This Chapter</button>
  <button className="ai-button personalize-button">✨ Personalize this Chapter for Me</button>
  <button className="ai-button translate-button">🌐 Translate to Urdu</button>
</div>

## Learning Objectives

- Implement object detection and tracking systems
- Apply deep learning for visual recognition
- Understand 3D vision and depth estimation
- Build visual servoing controllers
- Create robust vision pipelines for robots

## 8.1 Object Detection with Deep Learning

### YOLO for Real-Time Detection

```python
import cv2
import numpy as np
import torch
from torchvision import transforms

class RobotVisionSystem:
    def __init__(self, model_path='yolov5s.pt'):
        """Initialize vision system with YOLO"""
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        self.model.eval()

        self.confidence_threshold = 0.5
        self.target_classes = ['person', 'bottle', 'cup', 'book']

    def detect_objects(self, frame):
        """Detect objects in frame"""
        results = self.model(frame)

        detections = []
        for *box, conf, cls in results.xyxy[0].cpu().numpy():
            if conf > self.confidence_threshold:
                x1, y1, x2, y2 = map(int, box)
                class_name = self.model.names[int(cls)]

                detections.append({
                    'box': [x1, y1, x2, y2],
                    'confidence': float(conf),
                    'class': class_name,
                    'center': ((x1 + x2) // 2, (y1 + y2) // 2)
                })

        return detections

    def draw_detections(self, frame, detections):
        """Draw bounding boxes on frame"""
        for det in detections:
            x1, y1, x2, y2 = det['box']
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            label = f"{det['class']}: {det['confidence']:.2f}"
            cv2.putText(frame, label, (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Draw center point
            cv2.circle(frame, det['center'], 5, (0, 0, 255), -1)

        return frame

# Example usage
vision_system = RobotVisionSystem()
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    detections = vision_system.detect_objects(frame)
    frame = vision_system.draw_detections(frame, detections)

    cv2.imshow('Robot Vision', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### Custom Object Detection

```python
import torch
import torch.nn as nn
from torchvision import models

class CustomObjectDetector(nn.Module):
    def __init__(self, num_classes):
        super(CustomObjectDetector, self).__init__()

        # Backbone
        backbone = models.resnet50(pretrained=True)
        self.features = nn.Sequential(*list(backbone.children())[:-2])

        # Detection head
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(2048, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )

        # Bounding box regression
        self.bbox_regressor = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(2048, 512),
            nn.ReLU(),
            nn.Linear(512, 4)  # [x, y, w, h]
        )

    def forward(self, x):
        features = self.features(x)
        class_scores = self.classifier(features)
        bbox = self.bbox_regressor(features)
        return class_scores, bbox

# Training function
def train_detector(model, dataloader, optimizer, criterion, device):
    model.train()
    total_loss = 0

    for images, labels, bboxes in dataloader:
        images = images.to(device)
        labels = labels.to(device)
        bboxes = bboxes.to(device)

        optimizer.zero_grad()

        class_scores, pred_bboxes = model(images)

        loss_cls = criterion['classification'](class_scores, labels)
        loss_bbox = criterion['bbox'](pred_bboxes, bboxes)

        loss = loss_cls + loss_bbox
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    return total_loss / len(dataloader)
```

## 8.2 Object Tracking

### Kalman Filter Tracker

```python
import cv2
import numpy as np

class ObjectTracker:
    def __init__(self):
        """Multi-object tracker using Kalman filters"""
        self.trackers = {}
        self.next_id = 0
        self.max_age = 5  # Max frames without detection

    def update(self, detections):
        """Update trackers with new detections"""
        # Predict step for all trackers
        for track_id in list(self.trackers.keys()):
            self.trackers[track_id]['kf'].predict()
            self.trackers[track_id]['age'] += 1

            # Remove old tracks
            if self.trackers[track_id]['age'] > self.max_age:
                del self.trackers[track_id]

        # Associate detections with tracks
        if len(detections) > 0 and len(self.trackers) > 0:
            matches, unmatched_dets = self.associate(detections)

            # Update matched tracks
            for det_idx, track_id in matches:
                detection = detections[det_idx]
                self.trackers[track_id]['kf'].update(detection['center'])
                self.trackers[track_id]['age'] = 0
                self.trackers[track_id]['bbox'] = detection['box']
                self.trackers[track_id]['class'] = detection['class']

            # Create new tracks for unmatched detections
            for det_idx in unmatched_dets:
                self.create_track(detections[det_idx])
        elif len(detections) > 0:
            # No existing tracks, create new ones
            for detection in detections:
                self.create_track(detection)

    def create_track(self, detection):
        """Create new track"""
        kf = KalmanFilter2D()
        kf.update(detection['center'])

        self.trackers[self.next_id] = {
            'kf': kf,
            'age': 0,
            'bbox': detection['box'],
            'class': detection['class']
        }
        self.next_id += 1

    def associate(self, detections):
        """Associate detections with tracks using IOU"""
        matches = []
        unmatched_dets = list(range(len(detections)))

        for track_id, track in self.trackers.items():
            best_iou = 0.3  # Minimum IOU threshold
            best_det_idx = None

            for det_idx in unmatched_dets:
                iou = self.compute_iou(track['bbox'], detections[det_idx]['box'])
                if iou > best_iou:
                    best_iou = iou
                    best_det_idx = det_idx

            if best_det_idx is not None:
                matches.append((best_det_idx, track_id))
                unmatched_dets.remove(best_det_idx)

        return matches, unmatched_dets

    def compute_iou(self, box1, box2):
        """Compute Intersection over Union"""
        x1_min, y1_min, x1_max, y1_max = box1
        x2_min, y2_min, x2_max, y2_max = box2

        inter_xmin = max(x1_min, x2_min)
        inter_ymin = max(y1_min, y2_min)
        inter_xmax = min(x1_max, x2_max)
        inter_ymax = min(y1_max, y2_max)

        if inter_xmax < inter_xmin or inter_ymax < inter_ymin:
            return 0.0

        inter_area = (inter_xmax - inter_xmin) * (inter_ymax - inter_ymin)

        box1_area = (x1_max - x1_min) * (y1_max - y1_min)
        box2_area = (x2_max - x2_min) * (y2_max - y2_min)

        iou = inter_area / (box1_area + box2_area - inter_area)
        return iou

    def get_tracks(self):
        """Get all active tracks"""
        tracks = []
        for track_id, track in self.trackers.items():
            state = track['kf'].get_state()
            tracks.append({
                'id': track_id,
                'position': state[:2],
                'velocity': state[2:],
                'bbox': track['bbox'],
                'class': track['class']
            })
        return tracks

class KalmanFilter2D:
    """Simple 2D Kalman filter for tracking"""
    def __init__(self):
        # State: [x, y, vx, vy]
        self.state = np.zeros(4)
        self.cov = np.eye(4) * 1000

        dt = 1.0
        self.F = np.array([
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

        self.H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ])

        self.Q = np.eye(4) * 0.1
        self.R = np.eye(2) * 10

    def predict(self):
        self.state = self.F @ self.state
        self.cov = self.F @ self.cov @ self.F.T + self.Q

    def update(self, measurement):
        y = measurement - self.H @ self.state
        S = self.H @ self.cov @ self.H.T + self.R
        K = self.cov @ self.H.T @ np.linalg.inv(S)

        self.state = self.state + K @ y
        self.cov = (np.eye(4) - K @ self.H) @ self.cov

    def get_state(self):
        return self.state.copy()
```

## 8.3 Depth Estimation

### Stereo Vision

```python
import cv2
import numpy as np

class StereoDepthEstimator:
    def __init__(self, baseline=0.1, focal_length=700):
        """
        Stereo depth estimation
        baseline: distance between cameras (meters)
        focal_length: camera focal length (pixels)
        """
        self.baseline = baseline
        self.focal_length = focal_length

        # Stereo matcher
        self.stereo = cv2.StereoBM_create(numDisparities=16*10, blockSize=15)

    def compute_disparity(self, left_image, right_image):
        """Compute disparity map"""
        # Convert to grayscale
        left_gray = cv2.cvtColor(left_image, cv2.COLOR_BGR2GRAY)
        right_gray = cv2.cvtColor(right_image, cv2.COLOR_BGR2GRAY)

        # Compute disparity
        disparity = self.stereo.compute(left_gray, right_gray)

        # Normalize for visualization
        disparity_normalized = cv2.normalize(
            disparity, None, alpha=0, beta=255,
            norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U
        )

        return disparity, disparity_normalized

    def disparity_to_depth(self, disparity):
        """Convert disparity to depth"""
        # Avoid division by zero
        disparity = np.where(disparity == 0, 0.1, disparity)

        # Depth = (baseline * focal_length) / disparity
        depth = (self.baseline * self.focal_length) / disparity

        return depth

    def get_point_cloud(self, disparity, image):
        """Generate 3D point cloud"""
        h, w = disparity.shape
        points = []
        colors = []

        for v in range(h):
            for u in range(w):
                d = disparity[v, u]
                if d > 0:
                    # Convert to 3D
                    Z = (self.baseline * self.focal_length) / d
                    X = (u - w/2) * Z / self.focal_length
                    Y = (v - h/2) * Z / self.focal_length

                    points.append([X, Y, Z])
                    colors.append(image[v, u])

        return np.array(points), np.array(colors)
```

### Monocular Depth Estimation with Deep Learning

```python
import torch
import torch.nn as nn

class DepthEstimationNet(nn.Module):
    def __init__(self):
        """Monocular depth estimation network"""
        super(DepthEstimationNet, self).__init__()

        # Encoder
        self.encoder = nn.Sequential(
            nn.Conv2d(3, 64, 7, stride=2, padding=3),
            nn.ReLU(),
            nn.Conv2d(64, 128, 5, stride=2, padding=2),
            nn.ReLU(),
            nn.Conv2d(128, 256, 3, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(256, 512, 3, stride=2, padding=1),
            nn.ReLU()
        )

        # Decoder
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(512, 256, 3, stride=2, padding=1, output_padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(256, 128, 3, stride=2, padding=1, output_padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(128, 64, 3, stride=2, padding=1, output_padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(64, 1, 3, stride=2, padding=1, output_padding=1),
            nn.Sigmoid()  # Depth in [0, 1]
        )

    def forward(self, x):
        features = self.encoder(x)
        depth = self.decoder(features)
        return depth
```

## 8.4 Visual Servoing

### Image-Based Visual Servoing (IBVS)

```python
import numpy as np

class VisualServoController:
    def __init__(self, camera_params):
        """
        Visual servoing controller
        camera_params: {'fx', 'fy', 'cx', 'cy'}
        """
        self.fx = camera_params['fx']
        self.fy = camera_params['fy']
        self.cx = camera_params['cx']
        self.cy = camera_params['cy']

        self.lambda_gain = 0.5  # Control gain

    def compute_image_jacobian(self, pixel_coords, depth):
        """
        Compute image Jacobian
        pixel_coords: [u, v] pixel coordinates
        depth: Z depth of feature
        """
        u, v = pixel_coords

        # Normalized coordinates
        x = (u - self.cx) / self.fx
        y = (v - self.cy) / self.fy

        # Image Jacobian
        L = np.array([
            [-1/depth, 0, x/depth, x*y, -(1+x**2), y],
            [0, -1/depth, y/depth, 1+y**2, -x*y, -x]
        ])

        return L

    def compute_control(self, current_features, desired_features, depths):
        """
        Compute camera velocity command
        current_features: list of [u, v] current feature positions
        desired_features: list of [u, v] desired feature positions
        depths: list of feature depths
        """
        # Stack all feature Jacobians
        L_full = []
        error = []

        for curr, des, Z in zip(current_features, desired_features, depths):
            L = self.compute_image_jacobian(curr, Z)
            L_full.append(L)

            e = np.array(curr) - np.array(des)
            error.append(e)

        L_full = np.vstack(L_full)
        error = np.concatenate(error)

        # Pseudo-inverse control law
        # v = -λ * L^+ * e
        L_pinv = np.linalg.pinv(L_full)
        velocity = -self.lambda_gain * L_pinv @ error

        return velocity  # [vx, vy, vz, wx, wy, wz]

# Example usage
camera_params = {'fx': 500, 'fy': 500, 'cx': 320, 'cy': 240}
controller = VisualServoController(camera_params)

# Current and desired feature positions
current = [[300, 200], [350, 220]]
desired = [[320, 240], [320, 240]]
depths = [1.0, 1.0]

velocity = controller.compute_control(current, desired, depths)
print(f"Camera velocity command: {velocity}")
```

## 8.5 Practical Task: Pick-and-Place Vision System

```python
class PickAndPlaceVision:
    def __init__(self):
        self.detector = RobotVisionSystem()
        self.depth_estimator = StereoDepthEstimator()

    def locate_object(self, rgb_image, depth_image, target_class='bottle'):
        """Locate target object in 3D space"""
        # Detect objects
        detections = self.detector.detect_objects(rgb_image)

        # Filter for target class
        target_det = None
        for det in detections:
            if det['class'] == target_class:
                target_det = det
                break

        if target_det is None:
            return None

        # Get 3D position from depth
        cx, cy = target_det['center']
        depth = depth_image[cy, cx]

        # Convert to 3D coordinates
        fx, fy = 500, 500  # Camera intrinsics
        cx_cam, cy_cam = 320, 240

        X = (cx - cx_cam) * depth / fx
        Y = (cy - cy_cam) * depth / fy
        Z = depth

        return {
            'class': target_det['class'],
            'position_2d': (cx, cy),
            'position_3d': np.array([X, Y, Z]),
            'confidence': target_det['confidence']
        }

    def plan_grasp(self, object_info):
        """Plan grasp for detected object"""
        position = object_info['position_3d']

        # Simple top-down grasp
        grasp_pose = {
            'position': position,
            'orientation': [0, np.pi, 0],  # Top-down
            'gripper_width': 0.08  # 8cm opening
        }

        return grasp_pose
```

## Glossary

- **Object Detection**: Locating objects in images
- **Object Tracking**: Following objects across frames
- **Disparity**: Pixel difference in stereo images
- **Depth Map**: Image where pixel values represent depth
- **Visual Servoing**: Control using visual feedback
- **Feature**: Distinctive image point (corner, edge)
- **IOU**: Intersection over Union metric

## Checkpoint Quiz

<div className="quiz-container">

### Question 1
What is the main advantage of YOLO over traditional object detection?

A) Higher accuracy
B) Real-time detection speed
C) Works without training
D) Doesn't need GPU

<details>
<summary>Show Answer</summary>
**Answer: B** - YOLO is designed for real-time object detection.
</details>

### Question 2
How does stereo vision estimate depth?

A) Using color information
B) Using disparity between left and right images
C) Using motion blur
D) Using image brightness

<details>
<summary>Show Answer</summary>
**Answer: B** - Stereo vision uses disparity (pixel shift) to triangulate depth.
</details>

### Question 3
What is visual servoing?

A) Storing images
B) Controlling robot using visual feedback
C) Training vision models
D) Compressing video

<details>
<summary>Show Answer</summary>
**Answer: B** - Visual servoing uses visual feedback to control robot motion.
</details>

</div>

## AI Assistant Prompts for Deep Learning

1. "Compare YOLO, Faster R-CNN, and SSD for robot object detection. Which is best for real-time?"
2. "Explain how stereo vision works to estimate depth. Include the mathematical principles."
3. "What is visual servoing and how is it used in robot manipulation tasks?"
4. "How do monocular depth estimation networks work? What are their limitations?"
5. "Explain the difference between object detection and object tracking in robotics."

---

**Previous**: [Chapter 7: Motion Planning](./chapter-07.md) | **Next**: [Chapter 9: Humanoid Robot Systems](./chapter-09.md)
