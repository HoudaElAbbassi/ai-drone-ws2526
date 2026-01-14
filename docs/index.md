---
layout: default
title: Home
---

<div style="text-align: center; padding: 2rem 0 3rem;">
  <div style="display: inline-flex; align-items: center; gap: 8px; background: linear-gradient(135deg, #e0f2fe, #f0f9ff); padding: 0.5rem 1rem; border-radius: 9999px; font-size: 0.8rem; font-weight: 600; color: #0369a1; margin-bottom: 1.5rem;">
    <span style="width: 8px; height: 8px; background: #10b981; border-radius: 50%;"></span>
    Frankfurt UAS · WS 2025/26
  </div>
  <h1 style="font-size: 2.75rem; background: linear-gradient(135deg, #0f172a 0%, #0369a1 50%, #06b6d4 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 1rem; line-height: 1.2;">AI-Powered Road Damage Detection</h1>
  <p style="font-size: 1.2rem; color: #64748b; max-width: 600px; margin: 0 auto 2rem;">Autonomous FPV drone system with real-time AI detection for revolutionizing road infrastructure maintenance.</p>
  <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
    <a href="{{ site.baseurl }}/road-inspection/overview.html" style="display: inline-flex; align-items: center; gap: 8px; background: linear-gradient(135deg, #0ea5e9, #06b6d4); color: white; padding: 0.875rem 1.75rem; border-radius: 10px; font-weight: 600; text-decoration: none; box-shadow: 0 4px 14px rgba(14, 165, 233, 0.4);">
      Get Started →
    </a>
    <a href="{{ site.github.repository_url }}" style="display: inline-flex; align-items: center; gap: 8px; background: #1e293b; color: white; padding: 0.875rem 1.75rem; border-radius: 10px; font-weight: 600; text-decoration: none;">
      View on GitHub
    </a>
  </div>
</div>

---

## 🎯 Project Mission

Traditional road inspection is **time-consuming**, **costly**, and often **inconsistent**. Our solution combines autonomous drone technology with edge AI to deliver:

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.25rem; margin: 2rem 0;">

<div style="background: linear-gradient(135deg, #f8fafc, #f0f9ff); border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem;">
  <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #0ea5e9, #06b6d4); border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 1rem; color: white; font-size: 1.25rem;">🚁</div>
  <h4 style="margin: 0 0 0.5rem; color: #0f172a;">Autonomous Flight</h4>
  <p style="margin: 0; color: #64748b; font-size: 0.9rem;">Pre-programmed paths for systematic road coverage with GPS tracking.</p>
</div>

<div style="background: linear-gradient(135deg, #f8fafc, #f0f9ff); border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem;">
  <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #8b5cf6, #a78bfa); border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 1rem; color: white; font-size: 1.25rem;">🧠</div>
  <h4 style="margin: 0 0 0.5rem; color: #0f172a;">AI-Powered Detection</h4>
  <p style="margin: 0; color: #64748b; font-size: 0.9rem;">Real-time identification of 7+ types of road damage using deep learning.</p>
</div>

<div style="background: linear-gradient(135deg, #f8fafc, #f0f9ff); border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem;">
  <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #10b981, #34d399); border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 1rem; color: white; font-size: 1.25rem;">⚡</div>
  <h4 style="margin: 0 0 0.5rem; color: #0f172a;">Edge Computing</h4>
  <p style="margin: 0; color: #64748b; font-size: 0.9rem;">On-board processing with Google Coral TPU for 10-100x faster inference.</p>
</div>

<div style="background: linear-gradient(135deg, #f8fafc, #f0f9ff); border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem;">
  <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #f59e0b, #fbbf24); border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 1rem; color: white; font-size: 1.25rem;">📷</div>
  <h4 style="margin: 0 0 0.5rem; color: #0f172a;">Live Monitoring</h4>
  <p style="margin: 0; color: #64748b; font-size: 0.9rem;">FPV transmission for real-time inspection oversight and control.</p>
</div>

</div>

## 🛠️ System Architecture

Our drone integrates multiple components for autonomous road inspection:

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

## 🔍 Damage Types Detected

| Type | Description | Severity |
|------|-------------|----------|
| **Longitudinal Cracks** | Parallel to traffic direction | Low / Medium / High |
| **Transverse Cracks** | Perpendicular to traffic | Low / Medium / High |
| **Alligator Cracks** | Interconnected patterns | Low / Medium / High |
| **Potholes** | Surface depressions | Low / Medium / High |
| **Rutting** | Wheel path depressions | Low / Medium / High |
| **Bleeding** | Excess asphalt on surface | Low / Medium / High |
| **Weathering** | Surface aggregate loss | Low / Medium / High |

## 📚 Documentation

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1rem; margin: 2rem 0;">

<a href="{{ site.baseurl }}/road-inspection/overview.html" style="display: block; background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; text-decoration: none; color: inherit;">
  <h4 style="margin: 0 0 0.5rem; color: #0f172a;">📋 Project Overview</h4>
  <p style="margin: 0; color: #64748b; font-size: 0.9rem;">Detailed concept, problem statement, and solution approach.</p>
</a>

<a href="{{ site.baseurl }}/hardware/setup.html" style="display: block; background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; text-decoration: none; color: inherit;">
  <h4 style="margin: 0 0 0.5rem; color: #0f172a;">🔧 Hardware Setup</h4>
  <p style="margin: 0; color: #64748b; font-size: 0.9rem;">Assemble and configure drone hardware components.</p>
</a>

<a href="{{ site.baseurl }}/software/installation.html" style="display: block; background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; text-decoration: none; color: inherit;">
  <h4 style="margin: 0 0 0.5rem; color: #0f172a;">💻 Software Installation</h4>
  <p style="margin: 0; color: #64748b; font-size: 0.9rem;">Install and configure the AI framework and tools.</p>
</a>

<a href="{{ site.baseurl }}/software/camera-control.html" style="display: block; background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; text-decoration: none; color: inherit;">
  <h4 style="margin: 0 0 0.5rem; color: #0f172a;">📷 Camera Control</h4>
  <p style="margin: 0; color: #64748b; font-size: 0.9rem;">RC-triggered recording and AI detection system.</p>
</a>

<a href="{{ site.baseurl }}/ai-applications/setup.html" style="display: block; background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; text-decoration: none; color: inherit;">
  <h4 style="margin: 0 0 0.5rem; color: #0f172a;">🧠 AI & Datasets</h4>
  <p style="margin: 0; color: #64748b; font-size: 0.9rem;">Train and deploy damage detection models.</p>
</a>

<a href="{{ site.baseurl }}/tutorials/getting-started.html" style="display: block; background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; text-decoration: none; color: inherit;">
  <h4 style="margin: 0 0 0.5rem; color: #0f172a;">📖 Tutorials</h4>
  <p style="margin: 0; color: #64748b; font-size: 0.9rem;">Step-by-step guides for first flight and testing.</p>
</a>

</div>

## 🚀 Technology Stack

<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 2rem; margin: 2rem 0;">

<div>

### Hardware
- FPV Drone Frame
- Raspberry Pi Zero 2 WH
- Google Coral USB Accelerator
- Camera Module
- GPS Receiver
- Flight Controller (INAV/ArduPilot)

</div>

<div>

### Software
- **OS**: Raspbian/Ubuntu
- **AI**: TensorFlow Lite, YOLOv8
- **Flight**: INAV, ArduPilot
- **Camera**: Picamera2
- **Languages**: Python, C++

</div>

</div>

---

<div style="text-align: center; padding: 2rem 0;">
  <p style="color: #64748b; margin-bottom: 0.5rem;">Supervised by <strong>Prof. Dr. Christian Baun</strong></p>
  <p style="color: #94a3b8; font-size: 0.875rem;">Frankfurt University of Applied Sciences · Winter Semester 2025/2026</p>
</div>
