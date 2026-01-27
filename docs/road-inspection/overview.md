---
layout: default
title: Road Damage Detection Overview
---

# Road Damage Detection - Project Overview

[← Back to Home](../)

## Mission Statement

Our AI-powered drone system revolutionizes road infrastructure maintenance by providing automated, efficient, and accurate road damage detection. By flying over roads and analyzing surface conditions in real-time, we enable proactive maintenance and improve road safety.

## The Problem

Traditional road inspection methods face several challenges:

- **Time-consuming**: Manual inspections require significant labor and time
- **Costly**: Professional inspectors and specialized equipment are expensive
- **Inconsistent**: Human assessment can vary between inspectors
- **Dangerous**: Inspectors must work near traffic or on damaged roads
- **Reactive**: Damage often discovered after it becomes severe
- **Limited coverage**: Budget constraints limit inspection frequency

## Our Solution

An autonomous drone equipped with the hardware listed below, running an AI model that currently detects potholes. The current implementation does not record GPS data; detections are saved locally via the AI pipeline in `camera_control.py`.

## Hardware Components (Drone 3)

- **Frame**: SpeedyBee BEE35 Pro 3.5" CineWhoop Frame Kit
- **Flight Controller**: Flywoo GOKU F722 PRO V2 (STM32F722, 216MHz, 512kB Flash) 55A Stack 3-6S AM32 (Betaflight v4.5.2)
- **Camera**: Caddx Ratel Pro 1500TVL Analog (FPV)
- **Video Transmitter**: SpeedyBee TX800 VTX
- **Channel**: 5847 MHz (Band: BOSCAM/RichWave, Channel: 7)
- **VTX Antenna**: Foxeer Lollipop 4 RHCP
- **Receiver**: Radiomaster XR1 ELRS Dual Band RX (Firmware: ExpressLRS 3.6.0)
- **Binding Phase**: drone3
- **Motors**: Axisflying C206 2006 2500KV 4-6S
- **Propellers**: Gemfan 90mm D90-5 3.5" Ducted 5-Blade Propeller
- **GPS**: Matek M10Q-5883 GPS with Compass

## Types of Road Damage Detected

### 1. Potholes (current model)
**Description**: Bowl-shaped depressions in the pavement surface, varying in size and depth.

**Causes**:
- Water infiltration through cracks
- Freeze-thaw cycles
- Traffic loading on weakened pavement

**Severity levels**:
- Low: Diameter < 200mm, depth < 25mm
- Medium: Diameter 200-500mm, depth 25-50mm
- High: Diameter > 500mm, depth > 50mm

## System Workflow

```
┌─────────────────────────────────────────────────────┐
│  1. FLIGHT PLANNING                                 │
│  - Define road segments to inspect                  │
│  - Generate autonomous flight path                  │
│  - Set altitude and speed parameters                │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  2. AUTONOMOUS FLIGHT                               │
│  - Drone follows pre-programmed route               │
│  - Maintains consistent altitude (5-10m)            │
│  - Camera continuously captures images              │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  3. REAL-TIME IMAGE CAPTURE                         │
│  - Analog video frames captured (1500TVL)           │
│  - Timestamp for temporal tracking                  │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  4. AI DETECTION & CLASSIFICATION                   │
│  - Images processed by YOLO/TensorFlow Lite         │
│  - Google Coral accelerates inference               │
│  - Potholes detected and classified by severity     │
│  - Detection screenshots saved                      │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  5. DATA STORAGE & LOGGING                          │
│  - Detection screenshots saved                      │
│  - Metadata: timestamp and confidence score         │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  6. REPORT GENERATION (PLANNED)                     │
│  - Interactive map with damage locations            │
│  - Statistical summary of road condition            │
│  - Priority list for maintenance                    │
│  - Before/after tracking over time                  │
└─────────────────────────────────────────────────────┘
```

## Technical Approach

### Image Acquisition
- **Altitude**: 5-10 meters above road surface
- **Speed**: 2-5 m/s for optimal image quality
- **Overlap**: 60-80% forward overlap between images
- **Capture source**: Caddx Ratel Pro 1500TVL analog camera
- **Processing resolution**: Typically 720p/1080p (depends on capture pipeline)
- **Frame rate**: 5-10 FPS

### AI Model Architecture

**Option 1: YOLOv5/YOLOv8**
- Single-stage detector for real-time processing
- Excellent speed-accuracy tradeoff
- Well-suited for edge devices
- Can detect multiple damage types simultaneously

**Option 2: Faster R-CNN**
- Two-stage detector for higher accuracy
- Better for small object detection (small cracks)
- Requires more computational resources
- May need post-processing optimization

**Option 3: EfficientDet**
- Balanced approach between speed and accuracy
- Efficient architecture for mobile/edge deployment
- Good performance on varied scales

### Training Dataset

**Required dataset characteristics**:
- Minimum 5,000 labeled images for potholes
- Various lighting conditions (sunny, cloudy, shadows)
- Different road surface types (asphalt, concrete)
- Multiple viewing angles and altitudes
- Balanced representation of severity levels

**Potential public datasets**:
- RDD2020: Road Damage Dataset (global dataset)
- SDNET2018: Concrete crack dataset
- Custom dataset collection with our drone

### Performance Metrics

- **mAP (mean Average Precision)**: Overall detection accuracy
- **Precision**: Ratio of correct detections to all detections
- **Recall**: Ratio of detected damages to all actual damages
- **F1-Score**: Harmonic mean of precision and recall
- **Inference time**: Time to process one image (target: < 100ms)
- **FPS**: Frames processed per second (target: > 10 FPS)

## Expected Benefits

### For Municipalities
- **Cost savings**: 40-60% reduction in inspection costs
- **Increased coverage**: Inspect 10x more road length per day
- **Better planning**: Data-driven maintenance prioritization
- **Historical tracking**: Monitor road degradation over time

### For Road Safety
- **Early intervention**: Fix problems before they worsen
- **Hazard prevention**: Identify dangerous potholes quickly
- **Reduced accidents**: Better maintained roads = safer driving

### For Research
- **Open-source platform**: Replicable system for research
- **Dataset creation**: Contribute to road damage detection research
- **Algorithm benchmarking**: Test different AI approaches
- **Infrastructure analytics**: Study road degradation patterns

## Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Variable lighting conditions | Image augmentation, HDR capture |
| Small crack detection | Shorter altitude, sharper optics, multi-scale detection |
| Real-time processing constraints | Edge TPU acceleration, model optimization |
| Location tagging | Not implemented yet (no GPS logging) |
| Shadow/water confusion | Additional spectral bands, temporal analysis |
| Battery life vs coverage | Efficient flight planning, battery swap stations |
| Wind stability for imaging | Gimbal stabilization, weather-aware scheduling |

## Project Milestones

**Month 1-2**: Hardware setup and initial testing
- Assemble drone and test flight capabilities
- Install Raspberry Pi and Google Coral
- Camera calibration and image quality testing

**Month 2-3**: AI model development
- Collect/acquire training dataset
- Train initial damage detection models
- Evaluate model performance and iterate

**Month 3-4**: System integration
- Integrate AI inference with drone camera
- Implement autonomous flight with ArduPilot
- Develop data logging and storage system

**Month 4-5**: Field testing and refinement
- Test on actual roads with known damage
- Refine detection algorithms based on results
- Optimize flight parameters (altitude, speed, overlap)

**Month 5-6**: Documentation and presentation
- Create comprehensive technical documentation
- Develop demonstration materials
- Prepare final project presentation

## Future Extensions

- **Multi-spectral imaging**: Detect subsurface damage
- **3D reconstruction**: Create detailed surface topology
- **Predictive maintenance**: ML models to predict future damage
- **Traffic integration**: Coordinate with traffic signals for safe flights
- **Fleet management**: Multiple drones for large-scale surveys
- **Mobile app**: Real-time monitoring and reporting interface

---

[← Back to Home](../) | [Next: Hardware Setup →](../hardware/setup.html)
