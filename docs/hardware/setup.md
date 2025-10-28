---
layout: default
title: Hardware Setup
---

# Hardware Setup Guide

[← Back to Home](../)

## Overview

This guide covers the complete hardware setup for the AI-powered FPV drone system.

## Components List

### Core Drone Components

| Component | Specification | Purpose |
|-----------|--------------|---------|
| Frame | FPV Racing Frame | Structural foundation |
| Flight Controller | (Model TBD) | Flight stabilization and control |
| ESC | Electronic Speed Controller | Motor speed regulation |
| Motors | Brushless Motors x4 | Propulsion |
| Propellers | (Size TBD) | Lift generation |
| Battery | LiPo Battery | Power supply |
| GPS Receiver | GPS Module | Position tracking |

### AI & Computing

| Component | Specification | Purpose |
|-----------|--------------|---------|
| Single-Board Computer | Raspberry Pi Zero 2 WH | Main computing unit |
| AI Accelerator | Google Coral USB Accelerator | AI inference acceleration |
| Camera | (Model TBD) | Visual input |
| A/V Video Grabber | USB Video Capture | Video processing |

### Control & Communication

| Component | Specification | Purpose |
|-----------|--------------|---------|
| Remote Control | ELRS Compatible | Manual control |
| ELRS Receiver | ExpressLRS Receiver | RC signal reception |
| FPV Transmitter | Video TX | Real-time video transmission |
| FPV Goggles | (Model TBD) | Pilot video display |

## Assembly Instructions

### Step 1: Frame Assembly
- Assemble the drone frame according to manufacturer instructions
- Ensure all screws are properly tightened
- Check frame alignment

### Step 2: Motor Installation
- Mount motors to frame arms
- Connect ESC to motors (pay attention to motor direction)
- Secure wiring with zip ties

### Step 3: Flight Controller Setup
- Mount flight controller at center of frame
- Ensure orientation is correct (arrow forward)
- Connect ESCs to flight controller

### Step 4: Raspberry Pi Integration
- Mount Raspberry Pi securely on frame
- Connect camera module to Pi camera port
- Connect Google Coral USB Accelerator to Pi USB port

### Step 5: Power Distribution
- Connect battery connector to PDB (Power Distribution Board)
- Wire power to flight controller, Raspberry Pi, and FPV transmitter
- Use appropriate voltage regulators (5V for Pi, etc.)

### Step 6: GPS & Receiver
- Mount GPS receiver on top of drone (clear view of sky)
- Install ELRS receiver
- Connect to flight controller

### Step 7: FPV System
- Mount FPV camera
- Connect A/V video grabber
- Wire to FPV transmitter
- Configure video channels

## Wiring Diagram

```
┌─────────────────────────────────────────────────┐
│                   Battery (LiPo)                │
└──────────────────┬──────────────────────────────┘
                   │
          ┌────────▼─────────┐
          │  Power Dist.     │
          │  Board (PDB)     │
          └┬─────┬─────┬────┬┘
           │     │     │    │
    ┌──────▼┐  ┌─▼──┐ ┌▼──┐│
    │ ESC 1 │  │ESC2│ │..││
    └───┬───┘  └─┬──┘ └┬──┘│
        │        │     │    │
    ┌───▼───┐  ┌─▼──┐ ┌▼──┐│
    │Motor1 │  │M2  │ │.. ││
    └───────┘  └────┘ └───┘│
                            │
         ┌──────────────────▼──────┐
         │   Flight Controller     │
         │  (Betaflight/ArduPilot) │
         └──┬─────────┬─────────┬──┘
            │         │         │
     ┌──────▼──┐  ┌───▼───┐ ┌──▼────┐
     │  ELRS   │  │  GPS  │ │ RasPi │
     │Receiver │  │Module │ │Zero 2 │
     └─────────┘  └───────┘ └───┬───┘
                                 │
                          ┌──────▼───────┐
                          │ Google Coral │
                          │ Accelerator  │
                          └──────────────┘
```

## Safety Considerations

⚠️ **Important Safety Notes:**

1. **Battery Safety**
   - Never leave LiPo batteries unattended while charging
   - Store in LiPo safe bags
   - Check for swelling or damage before each use

2. **Propeller Safety**
   - Remove propellers during testing
   - Wear eye protection
   - Keep hands away from spinning props

3. **Electrical Safety**
   - Double-check wiring before powering on
   - Use proper gauge wires for current ratings
   - Insulate exposed connections

4. **Flight Safety**
   - Test in open areas away from people
   - Follow local drone regulations
   - Maintain visual line of sight

## Testing & Calibration

### Initial Power-On Tests
1. Power on without propellers
2. Check all LED indicators
3. Verify flight controller boot sequence
4. Test Raspberry Pi connection
5. Check camera feed

### Sensor Calibration
1. Accelerometer calibration
2. Magnetometer calibration
3. GPS initialization
4. ESC calibration

### Range Test
1. Test RC signal range
2. Verify video transmission range
3. Check telemetry connection

## Troubleshooting

### Common Issues

**Problem**: Motors not spinning
- Check ESC connections
- Verify battery voltage
- Check flight controller configuration

**Problem**: No video feed
- Check camera connections
- Verify FPV transmitter power
- Match video channels on goggles

**Problem**: Raspberry Pi not booting
- Check power supply (5V regulated)
- Verify SD card installation
- Check for loose connections

**Problem**: GPS not acquiring signal
- Ensure clear view of sky
- Wait 2-3 minutes for initial lock
- Check GPS module orientation

## Next Steps

Once hardware is assembled and tested:
1. [Configure Software](../software/installation.html)
2. [Set up Flight Controller](../autopilot/configuration.html)
3. [Install AI Framework](../ai-applications/setup.html)

---

[← Back to Home](../) | [Next: Software Installation →](../software/installation.html)
