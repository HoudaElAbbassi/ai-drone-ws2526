# AI Drone Project - Road Damage Detection System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Pages](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://houdaelabbassi.github.io/ai-drone-ws2526/)

## Overview

This project is part of the Master's Program in Computer Science (Field of Study: Intelligent Systems) at Frankfurt University of Applied Sciences, Winter Semester 2025/2026, supervised by Prof. Dr. Christian Baun.

We are developing an AI-powered FPV drone system for **automated road damage detection and assessment**. The drone flies over roads and uses computer vision and deep learning models to identify road surface damage. The current implementation focuses on **pothole detection** using YOLOv8, with architecture designed to support additional damage types in the future.

## Project Concept

Our drone autonomously patrols road infrastructure and performs real-time analysis of road surface conditions. By combining aerial imagery with AI-powered defect detection, we aim to:

- **Automate road inspection**: Replace manual inspections with efficient aerial surveys
- **Early damage detection**: Identify road damage before it becomes severe
- **Cost reduction**: Reduce inspection costs and improve maintenance planning
- **Safety improvement**: Minimize road hazards through proactive maintenance
- **Data-driven decisions**: Provide quantitative data for infrastructure management

## Project Goals

- Develop and train AI model for pothole detection using YOLOv8
- Implement real-time detection system optimized for edge devices (Raspberry Pi + Google Coral TPU)
- Create autonomous flight paths for systematic road coverage
- Generate detailed damage reports with GPS coordinates and severity assessment
- Build comprehensive documentation for replication and research

## Hardware Components

- FPV Drone Frame with Flight Controller
- Raspberry Pi Zero 2 WH (Single-board computer)
- Google Coral USB Accelerator (AI inference)
- GPS Receiver
- Camera System
- FPV Transmitter and Goggles
- ELRS Receiver
- Electronic Speed Controllers (ESC)
- Motors and Batteries

## Software Stack

- **Flight Controller Firmware**: Betaflight / INAV / ArduPilot
- **Ground Control Station**: QGroundControl
- **Operating System**: Raspbian / Ubuntu
- **AI Framework**: YOLOv8 (Ultralytics), TensorFlow Lite, PyTorch
- **Programming Languages**: Python, C++

## Project Tasks

### Task 1: Hardware & Software Familiarization
Understanding the capabilities and limitations of all drone components.

### Task 2: AI Application Development
Developed a **YOLOv8 nano-based pothole detection system** optimized for edge deployment:

**Implementation Highlights:**
- **Model**: YOLOv8n (nano variant) for real-time detection on resource-constrained devices
- **Dataset**: 4,510 annotated road images from Roboflow Universe
  - Train: 3,993 images | Validation: 352 images | Test: 165 images
  - Preprocessing: Histogram equalization, resizing to 840×840
  - Augmentations: 3× data expansion with blur, noise, and grayscale variations
- **Optimization**: INT8 quantization reducing model size by ~75% for edge deployment
- **Deployment**: TensorFlow Lite with Google Coral TPU acceleration (10× faster inference)
- **Current Focus**: Pothole detection (single-class)
- **Extensibility**: Architecture supports additional damage types with appropriate training data

**Technical Stack:**
- Training: Ultralytics YOLOv8, PyTorch, Roboflow API
- Deployment: TensorFlow Lite, INT8 quantization, Edge TPU compiler
- Detection: Real-time video/webcam inference scripts

See [`ai-model/`](ai-model/) directory for complete implementation and [AI Documentation](https://houdaelabbassi.github.io/ai-drone-ws2526/ai-applications/setup.html) for details.

### Task 3: Autopilot Integration
Implementing autonomous flight capabilities using INAV or ArduPilot.

### Task 4: Delivery/Payload System
Developing drop mechanisms for delivering inspection equipment.

### Task 5: Documentation & Presentation
Creating comprehensive online documentation via GitHub Pages.

## Documentation

Full documentation is available at: [GitHub Pages Documentation](https://houdaelabbassi.github.io/ai-drone-ws2526/)

## Team Members

- Dominique Conceicao Rosario
- Muhammad Rizki Aulia Rahman
- Houda El Abbassi

## Getting Started

```bash
# Clone the repository
git clone https://github.com/HoudaElAbbassi/ai-drone-ws2526.git

# Navigate to project directory
cd ai-drone-ws2526

# Install dependencies (detailed in documentation)
pip install -r requirements.txt
```

## Project Structure

```
ai-drone-ws2526/
├── docs/                    # GitHub Pages documentation
│   ├── hardware/            # Hardware setup guides
│   ├── software/            # Software configuration
│   ├── ai-applications/     # AI implementation guides
│   ├── road-inspection/     # Project overview
│   └── tutorials/           # Step-by-step tutorials
├── ai-model/                # AI model implementation
│   ├── train/               # Training scripts (train.py, validate.py)
│   ├── detect/              # Detection scripts (video, webcam)
│   ├── utilities/           # Model export and utilities
│   └── dataset/             # Training dataset (created when train.py is run)
├── camera_control.py        # Camera control script
└── drop-mechanism.py        # Payload delivery system
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Prof. Dr. Christian Baun - Project Supervisor
- Frankfurt University of Applied Sciences
- Master's Program in Computer Science (Intelligent Systems)

## Contact

For questions or collaboration:
- **Professor**: Prof. Dr. Christian Baun - christianbaun@fra-uas.de
- **Website**: [www.christianbaun.de](http://www.christianbaun.de)

---

**Course**: Master Project - Winter Semester 2025/2026
**University**: Frankfurt University of Applied Sciences
**Field of Study**: Intelligent Systems
