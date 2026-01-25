---
layout: default
title: AI Applications
---

# AI Applications for Road Damage Detection

[← Back to Home](../)

## Overview

This section covers the implementation of AI-powered **pothole detection** using YOLOv8 and TensorFlow Lite. The system is optimized for real-time inference on edge devices (Raspberry Pi Zero 2 WH with Google Coral TPU accelerator).

For complete technical documentation, see the [AI Model README]({{ site.github.repository_url }}/tree/main/ai-model).

## Current Implementation: Pothole Detection

The system currently detects **potholes** - bowl-shaped depressions and holes in road surfaces. The model uses **YOLOv8n** (nano variant), chosen for its:

- **Speed**: Single-pass detection ideal for real-time applications
- **Efficiency**: Smallest and fastest YOLO variant, perfect for edge devices
- **Accuracy**: Excellent detection performance despite compact size
- **Edge-Ready**: Easily exportable to TensorFlow Lite with INT8 quantization

### Future Extensions

The architecture supports extensible damage detection. Additional damage types can be added by training on appropriate datasets:
- Longitudinal & transverse cracks
- Alligator cracks (interconnected patterns)
- Rutting (wheel path depressions)
- Bleeding (excess asphalt)
- Weathering (surface degradation)
- Severity classification (low/medium/high)

## Project Structure

```
ai-model/
├── train/                    # Training scripts
│   ├── train.py             # Main training script
│   ├── validate.py          # Model validation
│   └── runs/                # Training outputs & results
├── utilities/               # Helper utilities
│   ├── export_model.py      # Export to TFLite
│   └── utils.py            # Shared functions
├── detect/                  # Detection scripts
│   ├── detect_video.py      # Video file detection
│   └── detect_webcam.py     # Live webcam detection
└── .env.example             # Configuration template
```

## Requirements

**Python Version**: Python 3.9 - 3.12 required (due to ultralytics and TensorFlow dependencies)

**Installation:**
```bash
pip install ultralytics roboflow opencv-python python-dotenv
```

## Configuration

### Dataset Setup

The project uses Roboflow for dataset management. Create a `.env` file from `.env.example`:

```bash
ROBOFLOW_API_KEY=your_api_key_here
ROBOFLOW_WORKSPACE=your_workspace
ROBOFLOW_PROJECT=your_project_id
ROBOFLOW_PROJECT_NAME=pothole_detection
ROBOFLOW_PROJECT_VERSION=1
```

The training script automatically downloads the dataset from Roboflow when needed.

## Training the Model

### Training Script (`train/train.py`)

The training script uses YOLOv8n and automatically configures itself based on available hardware (CUDA GPU, Apple MPS, or CPU).

**Key Training Parameters:**

| Parameter | Value | Description |
|-----------|-------|-------------|
| Model | YOLOv8n | Nano variant for edge deployment |
| Epochs | 300 | Number of training iterations |
| Image Size | 640×640 | Input resolution |
| Batch Size | 16 | Images per training batch |
| Patience | 50 | Early stopping if no improvement |
| Learning Rate | 0.01 → 0.001 | Initial → Final (with warmup) |
| Loss Weights | Box: 7.5, Class: 1.0 | Bounding box vs classification |

**Usage:**
```bash
cd ai-model/train
python train.py
```

**Output:** Trained model saved to `train/runs/detect/{PROJECT_NAME}/weights/best.pt`

### Model Validation (`train/validate.py`)

Evaluates the trained model on test data and reports performance metrics.

**Metrics Reported:**
- **mAP50**: Mean Average Precision at IoU threshold 0.50 (more lenient)
- **mAP50-95**: Mean Average Precision across IoU 0.50-0.95 (stricter)
- **Precision**: Ratio of correct positive predictions
- **Recall**: Ratio of detected actual positives

**Understanding IoU (Intersection over Union):**

IoU measures bounding box overlap quality:
- **IoU ≥ 0.7**: Good localization
- **IoU ≥ 0.9**: Excellent localization
- **mAP50-95**: Requires increasingly precise boxes

**Usage:**
```bash
cd ai-model/train
python validate.py
```

## Model Export for Deployment

### Export to TensorFlow Lite (`utilities/export_model.py`)

Converts the trained PyTorch model to TensorFlow Lite format optimized for Raspberry Pi with Google Coral TPU.

**Export Configuration:**

| Parameter | Value | Description |
|-----------|-------|-------------|
| Format | TFLite | TensorFlow Lite format |
| Quantization | INT8 | 8-bit integers (~75% size reduction) |
| Image Size | 320×320 | Reduced for faster edge inference |
| Optimization | Enabled | Additional TFLite optimizations |

**INT8 Quantization**: Converts 32-bit float weights to 8-bit integers, reducing model size by ~4x while maintaining accuracy. Essential for edge deployment.

**Usage:**
```bash
cd ai-model/utilities
python export_model.py
```

**Output:** `train/runs/detect/{PROJECT_NAME}/weights/best_saved_model/best_int8.tflite`

**Edge TPU Compilation (on Raspberry Pi):**
```bash
# Transfer .tflite file to Raspberry Pi
# Install Edge TPU Compiler
# Compile for Coral TPU
edgetpu_compiler best_int8.tflite

# Use generated *_edgetpu.tflite with Coral USB Accelerator
```

## Detection & Testing

### Video Detection (`detect/detect_video.py`)

Processes video files and annotates detected potholes frame-by-frame.

**Features:**
- Supports both `.pt` (PyTorch) and `.tflite` (TensorFlow Lite) models
- Configurable confidence threshold
- Progress tracking with frame counter
- Saves annotated video output

**Usage:**
```bash
cd ai-model/detect
# Edit script to set VIDEO_PATH, OUTPUT_PATH, MODEL_PATH
python detect_video.py
```

### Webcam Detection (`detect/detect_webcam.py`)

Real-time pothole detection using a connected webcam or camera module.

**Features:**
- Live video stream processing
- Real-time bounding box visualization
- FPS monitoring
- Press 'q' to quit

**Usage:**
```bash
cd ai-model/detect
# Edit script to set MODEL_PATH and CONFIDENCE threshold
python detect_webcam.py
```

## Hardware Acceleration

### Google Coral USB Accelerator

The exported TFLite model leverages the **Google Coral USB Accelerator** for significant performance improvements on the Raspberry Pi Zero 2 WH.

**Performance Benefits:**
- Up to **10x faster inference** compared to CPU-only execution
- Real-time detection capabilities on edge devices
- Low power consumption ideal for drone applications
- Automatic TPU utilization when Edge TPU compiled model is available

**Setup on Raspberry Pi:**
1. Install Edge TPU runtime and compiler
2. Transfer the `.tflite` model to Raspberry Pi
3. Compile with `edgetpu_compiler best_int8.tflite`
4. Use the generated `*_edgetpu.tflite` file in your detection scripts

## Complete Workflow

### Quick Start Guide

```bash
# 1. Install dependencies
pip install ultralytics roboflow opencv-python python-dotenv

# 2. Configure environment
cd ai-model
cp .env.example .env
# Edit .env with your Roboflow credentials

# 3. Train model
cd train
python train.py

# 4. Validate model
python validate.py

# 5. Export for Raspberry Pi
cd ../utilities
python export_model.py

# 6. Test with webcam
cd ../detect
python detect_webcam.py
```

### Training Custom Damage Types

To extend the system to detect additional road damage types:

1. **Prepare Dataset**: Collect and annotate images using tools like:
   - Roboflow (recommended - integrated with training pipeline)
   - LabelImg
   - CVAT

2. **Update Configuration**: Modify `.env` file to point to your new dataset

3. **Train**: Run `train.py` - it automatically downloads and trains on your dataset

4. **Export**: Use `export_model.py` to create TFLite model for deployment

**Supported Dataset Formats:**
- YOLO format (txt files with bounding boxes)
- Roboflow projects (automatic download)
- COCO format (with conversion)

## Performance Optimization

### Inference Speed
- **Google Coral TPU**: Up to 10x faster inference on Raspberry Pi
- **INT8 Quantization**: ~4x model size reduction with minimal accuracy loss
- **Input Resolution**: 320×320 for edge deployment (vs 640×640 training)
- **Model Variant**: YOLOv8n is the fastest YOLO variant

### Accuracy Improvements
- **More Training Data**: Collect diverse pothole images under various conditions
- **Data Augmentation**: Built into YOLOv8 training (rotation, scaling, brightness, etc.)
- **Hyperparameter Tuning**: Adjust learning rate, loss weights, and batch size
- **Extended Training**: Increase epochs with early stopping patience

### Training Hardware Recommendations
- **GPU Training**: CUDA GPU significantly speeds up training (hours vs days)
- **Apple MPS**: M1/M2 Macs provide good training performance
- **CPU Fallback**: Works but much slower; recommended for small datasets only

## Deployment Pipeline

### From Training to Production

1. **Train Model** → `train/train.py` produces `best.pt` (PyTorch format)
2. **Validate** → `train/validate.py` evaluates performance metrics
3. **Export** → `utilities/export_model.py` creates `best_int8.tflite`
4. **Transfer** → Copy `.tflite` file to Raspberry Pi
5. **Compile** → Run `edgetpu_compiler` to create `*_edgetpu.tflite`
6. **Deploy** → Use compiled model with Google Coral USB Accelerator

### On-Drone Integration

For integrating pothole detection into the drone's flight system:

1. **Camera Module**: Use Picamera2 for image capture (see [Camera Control](../software/camera-control.html))
2. **Edge TPU**: Connect Google Coral USB Accelerator to Raspberry Pi
3. **Detection Script**: Adapt `detect_webcam.py` for continuous monitoring
4. **GPS Logging**: Tag detected potholes with GPS coordinates
5. **Storage**: Save annotated images to SD card for post-flight analysis

## Additional Resources

- **[AI Model README]({{ site.github.repository_url }}/tree/main/ai-model)** - Complete technical documentation with detailed parameter explanations
- **[Dataset Documentation](datasets.html)** - Information about training datasets (coming soon)
- **[Validation Results]({{ site.github.repository_url }}/tree/main/ai-model/VALIDATION_RESULTS.md)** - Model performance metrics and benchmarks
- **[Hardware Setup](../hardware/setup.html)** - Raspberry Pi and Google Coral configuration

## Next Steps

1. [Review Datasets](datasets.html) - Learn about training data
2. [Hardware Setup](../hardware/setup.html) - Configure Raspberry Pi and Coral TPU
3. [Camera Control](../software/camera-control.html) - Integrate detection with camera
4. [Getting Started Tutorial](../tutorials/getting-started.html) - Complete walkthrough

---

[← Back to Home](../) | [Next: Datasets →](datasets.html)
