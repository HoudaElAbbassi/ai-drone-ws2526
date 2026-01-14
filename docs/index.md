---
layout: default
title: Home
---

# AI-Powered Road Damage Detection

Autonomous FPV drone system with real-time AI for road infrastructure maintenance.

<p style="margin: 1.5rem 0;">
  <a href="{{ site.baseurl }}/road-inspection/overview.html" style="display: inline-block; padding: 0.5rem 1rem; background: #171717; color: white; border-radius: 6px; font-size: 0.8rem; font-weight: 500; text-decoration: none; margin-right: 0.5rem;">Get Started →</a>
  <a href="{{ site.github.repository_url }}" style="display: inline-block; padding: 0.5rem 1rem; background: #f5f5f5; color: #171717; border-radius: 6px; font-size: 0.8rem; font-weight: 500; text-decoration: none;">GitHub</a>
</p>

---

## Project Mission

Traditional road inspection is time-consuming, costly, and often inconsistent. This project combines autonomous drone technology with edge AI to deliver efficient infrastructure monitoring.

**Key capabilities:**

- **Autonomous Flight** — Pre-programmed paths with GPS tracking for systematic road coverage
- **AI Detection** — Real-time identification of 7+ road damage types using deep learning
- **Edge Computing** — On-board processing with Google Coral TPU for fast inference
- **Live Monitoring** — FPV transmission for real-time oversight and control

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FPV DRONE PLATFORM                       │
│  ┌──────────────┐              ┌────────────────────┐      │
│  │   Camera     │─────────────▶│   Raspberry Pi     │      │
│  │   Module     │              │   Zero 2 WH        │      │
│  └──────────────┘              └─────────┬──────────┘      │
│                                          │                  │
│  ┌──────────────┐              ┌─────────▼──────────┐      │
│  │   Flight     │◀────────────▶│   Google Coral     │      │
│  │  Controller  │              │   AI Accelerator   │      │
│  └──────────────┘              └────────────────────┘      │
│                                                             │
│  ┌──────────────┐              ┌────────────────────┐      │
│  │     GPS      │              │    FPV TX/RX       │      │
│  │   Receiver   │              │    System          │      │
│  └──────────────┘              └────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Damage Types Detected

| Type | Description | Severity |
|------|-------------|----------|
| Longitudinal Cracks | Parallel to traffic direction | Low / Medium / High |
| Transverse Cracks | Perpendicular to traffic | Low / Medium / High |
| Alligator Cracks | Interconnected patterns | Low / Medium / High |
| Potholes | Surface depressions | Low / Medium / High |
| Rutting | Wheel path depressions | Low / Medium / High |
| Bleeding | Excess asphalt on surface | Low / Medium / High |
| Weathering | Surface aggregate loss | Low / Medium / High |

---

## Documentation

- [Project Overview]({{ site.baseurl }}/road-inspection/overview.html) — Concept, problem statement, and approach
- [Hardware Setup]({{ site.baseurl }}/hardware/setup.html) — Assemble and configure drone components
- [Software Installation]({{ site.baseurl }}/software/installation.html) — Install AI framework and tools
- [Camera Control]({{ site.baseurl }}/software/camera-control.html) — RC-triggered recording system
- [AI & Datasets]({{ site.baseurl }}/ai-applications/setup.html) — Train and deploy detection models
- [Tutorials]({{ site.baseurl }}/tutorials/getting-started.html) — Step-by-step guides

---

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
- **AI**: TensorFlow Lite, YOLOv8
- **Flight**: INAV, ArduPilot
- **Camera**: Picamera2
- **Languages**: Python, C++

---

<p style="text-align: center; color: #737373; font-size: 0.8rem; margin-top: 2rem;">
  Supervised by Prof. Dr. Christian Baun<br>
  Frankfurt University of Applied Sciences · WS 2025/26
</p>
