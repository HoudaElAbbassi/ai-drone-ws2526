---
layout: default
title: AI Applications
---

# AI Applications for Structural Inspection

[← Back to Home](../)

## Overview

This section covers the development and implementation of AI-powered applications for structural inspection using computer vision and machine learning.

## Inspection Use Cases

### 1. Crack Detection
Identify cracks in concrete structures, bridges, and buildings.

### 2. Surface Defect Analysis
Detect corrosion, spalling, and other surface defects.

### 3. Thermal Anomaly Detection
Identify heat loss and insulation problems.

### 4. Object Classification
Classify structural elements and damage types.

## AI Framework Overview

### TensorFlow Lite
- Optimized for embedded devices
- Runs on Raspberry Pi
- Accelerated by Google Coral

### YOLO (You Only Look Once)
- Real-time object detection
- High accuracy
- Multiple versions available (YOLOv5, YOLOv8)

## Model Selection

### Pre-trained Models

**Object Detection:**
- YOLOv5s (Small, fast)
- YOLOv5m (Medium, balanced)
- MobileNet-SSD (Lightweight)

**Segmentation:**
- U-Net (Medical/structural imaging)
- Mask R-CNN (Instance segmentation)

### Custom Training

For structural inspection, we'll need to train custom models on:
- Crack datasets
- Corrosion images
- Infrastructure photos

## Implementation

### Basic Object Detection Script

```python
# detect_defects.py
import cv2
import numpy as np
from pycoral.utils import edgetpu
from pycoral.adapters import common
from pycoral.adapters import detect
from PIL import Image

class DefectDetector:
    def __init__(self, model_path, labels_path):
        """Initialize the detector with model and labels"""
        self.interpreter = edgetpu.make_interpreter(model_path)
        self.interpreter.allocate_tensors()

        # Load labels
        with open(labels_path, 'r') as f:
            self.labels = [line.strip() for line in f.readlines()]

    def detect(self, image_path, threshold=0.5):
        """Detect defects in an image"""
        # Load and preprocess image
        image = Image.open(image_path)
        _, scale = common.set_resized_input(
            self.interpreter, image.size,
            lambda size: image.resize(size, Image.ANTIALIAS))

        # Run inference
        self.interpreter.invoke()

        # Get results
        objects = detect.get_objects(self.interpreter, threshold, scale)

        return objects

    def draw_results(self, image_path, objects, output_path):
        """Draw bounding boxes on image"""
        image = cv2.imread(image_path)

        for obj in objects:
            bbox = obj.bbox
            class_id = obj.id
            score = obj.score

            # Draw box
            cv2.rectangle(image,
                         (bbox.xmin, bbox.ymin),
                         (bbox.xmax, bbox.ymax),
                         (0, 255, 0), 2)

            # Add label
            label = f"{self.labels[class_id]}: {score:.2f}"
            cv2.putText(image, label,
                       (bbox.xmin, bbox.ymin - 10),
                       cv2.FONT_HERSHEY_SIMPLEX,
                       0.5, (0, 255, 0), 2)

        cv2.imwrite(output_path, image)
        return image

# Usage
if __name__ == "__main__":
    detector = DefectDetector(
        model_path="models/defect_detector_edgetpu.tflite",
        labels_path="models/labels.txt"
    )

    objects = detector.detect("test_image.jpg", threshold=0.6)
    detector.draw_results("test_image.jpg", objects, "result.jpg")

    print(f"Found {len(objects)} defects")
```

### Real-time Video Detection

```python
# realtime_detection.py
import cv2
import time
from defect_detector import DefectDetector

def main():
    # Initialize detector
    detector = DefectDetector(
        model_path="models/defect_detector_edgetpu.tflite",
        labels_path="models/labels.txt"
    )

    # Initialize camera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    fps_counter = 0
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Save frame temporarily
        cv2.imwrite('/tmp/current_frame.jpg', frame)

        # Detect defects
        objects = detector.detect('/tmp/current_frame.jpg', threshold=0.5)

        # Draw results
        result_frame = detector.draw_results('/tmp/current_frame.jpg', objects, '/tmp/result.jpg')
        result_frame = cv2.imread('/tmp/result.jpg')

        # Calculate FPS
        fps_counter += 1
        elapsed = time.time() - start_time
        fps = fps_counter / elapsed if elapsed > 0 else 0

        # Display FPS
        cv2.putText(result_frame, f"FPS: {fps:.1f}",
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                   1, (0, 255, 0), 2)

        # Show frame
        cv2.imshow('Defect Detection', result_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
```

## Training Custom Models

### Dataset Preparation

1. **Collect Images**
   - Take photos of structures with defects
   - Include various lighting conditions
   - Capture different angles

2. **Annotation**
   - Use tools like LabelImg or CVAT
   - Draw bounding boxes around defects
   - Label each defect type

3. **Dataset Structure**
```
dataset/
├── images/
│   ├── train/
│   │   ├── img001.jpg
│   │   ├── img002.jpg
│   │   └── ...
│   └── val/
│       ├── img101.jpg
│       └── ...
└── labels/
    ├── train/
    │   ├── img001.txt
    │   ├── img002.txt
    │   └── ...
    └── val/
        ├── img101.txt
        └── ...
```

### Training with YOLOv5

```bash
# Clone YOLOv5
git clone https://github.com/ultralytics/yolov5
cd yolov5
pip install -r requirements.txt

# Create dataset config
cat > data/defects.yaml << EOF
train: ../dataset/images/train
val: ../dataset/images/val

nc: 3  # number of classes
names: ['crack', 'corrosion', 'spalling']
EOF

# Train model
python train.py --img 640 --batch 16 --epochs 100 \
                --data data/defects.yaml --weights yolov5s.pt

# Export to TFLite
python export.py --weights runs/train/exp/weights/best.pt \
                 --include tflite --img 320

# Compile for Edge TPU
edgetpu_compiler best-fp16.tflite
```

### Model Evaluation

```python
# evaluate_model.py
import cv2
import numpy as np
from sklearn.metrics import precision_recall_fscore_support

def evaluate(detector, test_images, ground_truth):
    """Evaluate model performance"""
    predictions = []
    true_labels = []

    for img_path, gt in zip(test_images, ground_truth):
        # Detect
        objects = detector.detect(img_path, threshold=0.5)

        # Process predictions
        pred_classes = [obj.id for obj in objects]
        predictions.extend(pred_classes)
        true_labels.extend(gt)

    # Calculate metrics
    precision, recall, f1, _ = precision_recall_fscore_support(
        true_labels, predictions, average='weighted'
    )

    print(f"Precision: {precision:.3f}")
    print(f"Recall: {recall:.3f}")
    print(f"F1-Score: {f1:.3f}")

    return precision, recall, f1
```

## Performance Optimization

### Inference Speed
- Use Google Coral for 10-100x acceleration
- Optimize model size (quantization)
- Reduce input resolution if needed

### Accuracy Improvements
- Collect more training data
- Apply data augmentation
- Use ensemble methods
- Fine-tune hyperparameters

## Integration with Drone

### Flight Integration Script

```python
# drone_inspector.py
import cv2
import time
from defect_detector import DefectDetector
from pymavlink import mavutil

class DroneInspector:
    def __init__(self, model_path, labels_path, mavlink_connection):
        self.detector = DefectDetector(model_path, labels_path)
        self.drone = mavutil.mavlink_connection(mavlink_connection)
        self.camera = cv2.VideoCapture(0)

    def inspect_structure(self, waypoints):
        """Fly to waypoints and inspect for defects"""
        defects_found = []

        for wp in waypoints:
            # Navigate to waypoint
            self.goto_position(wp['lat'], wp['lon'], wp['alt'])

            # Capture image
            ret, frame = self.camera.read()
            if not ret:
                continue

            # Save image
            img_path = f"inspection_{time.time()}.jpg"
            cv2.imwrite(img_path, frame)

            # Detect defects
            objects = self.detector.detect(img_path, threshold=0.6)

            if objects:
                defects_found.append({
                    'location': wp,
                    'image': img_path,
                    'defects': objects,
                    'timestamp': time.time()
                })

                print(f"Found {len(objects)} defects at waypoint")

        return defects_found

    def goto_position(self, lat, lon, alt):
        """Navigate to GPS position"""
        # Implementation depends on autopilot system
        pass
```

## Inspection Report Generation

```python
# generate_report.py
import json
from datetime import datetime

def generate_report(defects_found, output_path):
    """Generate inspection report"""
    report = {
        'inspection_date': datetime.now().isoformat(),
        'total_defects': sum(len(d['defects']) for d in defects_found),
        'locations': []
    }

    for detection in defects_found:
        location = {
            'coordinates': detection['location'],
            'image': detection['image'],
            'defects': [
                {
                    'type': obj.id,
                    'confidence': obj.score,
                    'bbox': {
                        'xmin': obj.bbox.xmin,
                        'ymin': obj.bbox.ymin,
                        'xmax': obj.bbox.xmax,
                        'ymax': obj.bbox.ymax
                    }
                }
                for obj in detection['defects']
            ]
        }
        report['locations'].append(location)

    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    return report
```

## Next Steps

1. [Integrate Autopilot](../autopilot/configuration.html)
2. [Test in Real Flights](../tutorials/first-flight.html)
3. [Optimize Performance](../tutorials/optimization.html)

---

[← Back to Home](../) | [Next: Autopilot Configuration →](../autopilot/configuration.html)
