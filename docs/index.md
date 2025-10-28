---
layout: default
title: Home
---

# AI Drone Project - Structural Inspection System

Welcome to the documentation for our AI-powered FPV drone project focused on structural inspection and monitoring applications.

## Project Overview

This project is part of the **Master's Program in Computer Science** (Field of Study: Intelligent Systems) at **Frankfurt University of Applied Sciences**, Winter Semester 2025/2026.

**Supervisor**: Prof. Dr. Christian Baun

### Mission Statement

We are developing an intelligent drone system that combines computer vision, machine learning, and autonomous flight to revolutionize structural inspection and infrastructure monitoring.

## Key Features

- **AI-Powered Object Detection**: Real-time identification of structural defects and anomalies
- **Autonomous Flight**: Integrated autopilot for automated inspection routes
- **Delivery System**: Payload mechanisms for transporting inspection equipment
- **Live Video Streaming**: FPV transmission for real-time monitoring
- **Edge Computing**: On-board AI processing using Google Coral accelerator

## Application Areas

Our drone is designed for:

1. **Building Inspection**: Detecting cracks, water damage, and structural weaknesses
2. **Bridge Monitoring**: Identifying corrosion and structural defects
3. **Infrastructure Assessment**: Power lines, towers, and industrial facilities
4. **Thermal Analysis**: Heat loss detection and energy efficiency evaluation

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
Learn about drone components, capabilities, and limitations.

### [Task 2: AI Application Development](ai-applications/)
Develop and integrate AI for structural inspection.

### [Task 3: Autopilot Integration](autopilot/)
Implement autonomous flight capabilities.

### [Task 4: Delivery System](delivery/)
Create payload drop mechanisms.

### [Task 5: Documentation](tutorials/)
Comprehensive guides for replication.

## Quick Links

- [Hardware Setup Guide](hardware/setup.html)
- [Software Installation](software/installation.html)
- [AI Model Training](ai-applications/training.html)
- [Flight Controller Configuration](autopilot/configuration.html)
- [Getting Started Tutorial](tutorials/getting-started.html)

## Technology Stack

### Hardware
- FPV Drone Frame
- Raspberry Pi Zero 2 WH
- Google Coral USB Accelerator
- Camera Module
- GPS Receiver
- Flight Controller (Betaflight/INAV/ArduPilot)

### Software
- **OS**: Raspbian/Ubuntu
- **AI Frameworks**: TensorFlow Lite, YOLO
- **Flight Software**: ArduPilot, QGroundControl
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
