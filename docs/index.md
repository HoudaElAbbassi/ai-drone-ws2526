---
layout: default
title: Home
---

# AI Drone Project - Road Damage Detection System

Welcome to the documentation for our AI-powered FPV drone project focused on automated road damage detection and assessment.

## Project Overview

This project is part of the **Master's Program in Computer Science** (Field of Study: Intelligent Systems) at **Frankfurt University of Applied Sciences**, Winter Semester 2025/2026.

**Supervisor**: Prof. Dr. Christian Baun

### Mission Statement

We are developing an intelligent drone system that autonomously flies over roads to detect and classify surface damage using computer vision and deep learning. Our goal is to revolutionize road infrastructure maintenance through automated, efficient, and accurate damage assessment.

## Project Concept

Traditional road inspection is time-consuming, costly, and often inconsistent. Our solution: an autonomous drone equipped with AI that can:

- **Fly over roads** systematically and capture high-resolution imagery
- **Detect damage** in real-time using onboard AI processing (Google Coral TPU)
- **Classify defects** into categories: cracks, potholes, rutting, bleeding, weathering
- **Record locations** with precise GPS coordinates for each detected damage
- **Generate reports** with damage severity, location maps, and maintenance priorities

This enables proactive maintenance, reduces inspection costs, and improves road safety.

## Key Features

- **AI-Powered Damage Detection**: Real-time identification of 7+ types of road damage
- **Autonomous Flight**: Pre-programmed flight paths for systematic road coverage
- **Edge Computing**: On-board AI processing using Google Coral accelerator (10-100x faster)
- **GPS Tracking**: Precise localization of each detected defect
- **Live Monitoring**: FPV transmission for real-time inspection oversight
- **Automated Reporting**: Generate inspection reports with maps and statistics

## Types of Road Damage We Detect

Our system identifies and classifies:

1. **Longitudinal Cracks**: Parallel to traffic direction
2. **Transverse Cracks**: Perpendicular to traffic direction
3. **Alligator Cracks**: Interconnected cracking patterns
4. **Potholes**: Surface depressions and holes
5. **Rutting**: Depressions in wheel paths
6. **Bleeding**: Excess asphalt on surface
7. **Weathering**: Surface aggregate loss

Each damage type is assessed for severity (low/medium/high) and recorded with GPS coordinates.

## System Architecture

```
┌─────────────────────────────────────────────┐
│          FPV Drone Platform                 │
│  ┌────────────┐        ┌─────────────┐     │
│  │  Camera    │───────▶│ Raspberry Pi│     │
│  │  System    │        │   Zero 2 WH │     │
│  └────────────┘        └──────┬──────┘     │
│                               │             │
│  ┌────────────┐        ┌──────▼──────┐     │
│  │   Flight   │◀──────▶│ Google Coral│     │
│  │ Controller │        │ AI Accel.   │     │
│  └────────────┘        └─────────────┘     │
│                                             │
│  ┌────────────┐        ┌─────────────┐     │
│  │    GPS     │        │  FPV TX/RX  │     │
│  │  Receiver  │        │   System    │     │
│  └────────────┘        └─────────────┘     │
└─────────────────────────────────────────────┘
```

## Project Tasks

### [Task 1: Hardware & Software Setup](hardware/)
Assemble drone, install computing hardware (Raspberry Pi, Google Coral), and configure software stack.

### [Task 2: AI Application Development](ai-applications/)
Train and deploy deep learning models for road damage detection and classification.

### [Task 3: Autopilot Integration](autopilot/)
Implement autonomous flight paths for systematic road coverage using ArduPilot/INAV.

### [Task 4: Payload System](delivery/)
Optional: Integrate additional sensors or delivery mechanisms for maintenance supplies.

### [Task 5: Documentation](tutorials/)
Create comprehensive documentation enabling replication by other researchers and students.

## Quick Links

- **[Road Damage Detection Overview](road-inspection/overview.html)** - Detailed project concept
- [Hardware Setup Guide](hardware/setup.html) - Assemble and configure drone
- [Software Installation](software/installation.html) - Install AI framework and tools
- **[Camera Control System](software/camera-control.html)** - RC-triggered recording & AI detection
- [AI Model Training](ai-applications/setup.html) - Train damage detection models
- [Getting Started Tutorial](tutorials/getting-started.html) - First flight and testing

## Technology Stack

### Hardware
- FPV Drone Frame
- Raspberry Pi Zero 2 WH
- Google Coral USB Accelerator
- Camera Module
- GPS Receiver
- Flight Controller (INAV/ArduPilot)

### Software
- **OS**: Raspbian/Ubuntu
- **AI Frameworks**: TensorFlow Lite, YOLOv8, Google Coral TPU
- **Flight Software**: INAV, ArduPilot, QGroundControl
- **Camera**: Picamera2 with dual-stream processing
- **Languages**: Python, C++

## Team

- Team Member 1 - [Role]
- Team Member 2 - [Role]
- Team Member 3 - [Role]
- Team Member 4 - [Role]

## Repository

View the complete source code and resources on [GitHub](https://github.com/HoudaElAbbassi/ai-drone-ws2526).

## Contact

**Project Supervisor**
- Prof. Dr. Christian Baun
- Email: christianbaun@fra-uas.de
- Web: [www.christianbaun.de](http://www.christianbaun.de)

---

*Last updated: October 2025*
