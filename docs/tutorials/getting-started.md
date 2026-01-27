---
layout: default
title: Getting Started
---

# Getting Started Tutorial

[← Back to Home](../)

## Overview

This tutorial will guide you through your first steps with the AI drone system, from unboxing to your first test flight.

## Prerequisites

Before you begin, ensure you have:
- [ ] All hardware components assembled
- [ ] Batteries charged
- [ ] Software installed on Raspberry Pi
- [ ] Flight controller configured
- [ ] Open outdoor space for testing
- [ ] Safety equipment (goggles, fire extinguisher)

## Step 1: Pre-Flight Checklist

### Hardware Inspection

```
□ Frame integrity check - no cracks or loose screws
□ Motor mounting secure
□ Propellers undamaged and properly mounted
□ Battery fully charged and not swollen
□ All wiring secure with no exposed connections
□ Camera lens clean
□ GPS has clear view of sky
□ Raspberry Pi powered on and booting
□ Google Coral connected
□ FPV goggles charged
```

### Software Check

```bash
# SSH into Raspberry Pi
ssh pi@ai-drone.local

# Check system status
systemctl status drone-ai.service

# Test camera
raspistill -o test.jpg

# Verify Coral
python3 << EOF
from pycoral.utils import edgetpu
print(f"Edge TPU devices: {len(edgetpu.list_edge_tpus())}")
EOF

# Check disk space
df -h

# Verify GPS (if applicable)
cat /dev/ttyAMA0  # Should show NMEA sentences
```

## Step 2: Ground Testing

### Motor Test (No Propellers!)

**WARNING: Remove all propellers before motor testing!**

```bash
# Using Betaflight CLI or Configurator
# Motors Tab -> Test each motor individually
# Verify motor direction and order:
# 1: Front-Left (CCW)
# 2: Front-Right (CW)
# 3: Back-Right (CCW)
# 4: Back-Left (CW)
```

### AI System Test

Use the built-in camera/AI pipeline to verify the Edge TPU model loads and live inference runs while recording:

```bash
# From the Raspberry Pi
python3 camera_control.py
```

Expected behavior:
- On startup, the script prints the model input shape and starts the camera.
- Toggling the AUX channel starts/stops recording.
- While recording, detections are saved as images in the configured video folder.

If you are testing the payload drop mechanism, run it separately:

```bash
python3 drop-mechanism.py
```

Expected behavior:
- Servo starts in the closed position.
- Releasing the AUX button toggles open/close.

### Radio Range Test

1. Power on remote control
2. Check RSSI (signal strength) in OSD
3. Walk 50 meters away - verify signal strength
4. Test control inputs - verify responsiveness
5. Test failsafe - turn off controller, drone should disarm

## Step 3: First Flight (Manual Mode)

### Safety Procedures

**Pre-Flight:**
1. Clear the area of people and obstacles
2. Check wind conditions (< 10 mph for first flight)
3. Verify GPS lock (if using)
4. Arm failsafe configured correctly
5. Spotter assigned (recommended)

**Flight Rules:**
1. Maintain visual line of sight
2. Stay below 400 feet AGL
3. Avoid flying over people
4. Follow local regulations
5. Keep away from airports

### First Takeoff

```
1. Place drone on level ground
2. Power on remote control first
3. Power on drone
4. Wait for boot sequence (LEDs)
5. Check OSD - verify battery voltage, GPS
6. Arm the drone (arm switch)
7. Slowly increase throttle
8. Hover at 1-2 meters height
9. Test basic controls:
   - Pitch (forward/backward)
   - Roll (left/right)
   - Yaw (rotation)
   - Throttle (up/down)
10. Practice hovering for 1-2 minutes
11. Land gently
12. Disarm
```

### Flight Modes

**Angle/Stabilized Mode (Beginner):**
- Self-levels when sticks centered
- Limited tilt angle
- Easiest to fly

**Horizon Mode (Intermediate):**
- Self-levels when sticks centered
- Can do flips with full stick deflection
- More agile than Angle

**Acro Mode (Advanced):**
- No self-leveling
- Full manual control
- Most responsive

**Start with Angle mode!**

## Step 4: AI System First Test
During your first test flight, keep the AI pipeline enabled by running the camera control script. The system will save detections automatically when the model finds an object above the confidence threshold.

## Step 5: Troubleshooting

### Common Issues

**Drone won't arm:**
- Check battery voltage (should be > 3.5V per cell)
- Verify accelerometer calibration
- Check arm switch position
- Review error messages in OSD/configurator

**Poor video quality:**
- Check camera focus
- Adjust FPV transmitter power
- Change video channel to avoid interference
- Clean camera lens

**GPS not locking:**
- Ensure clear view of sky
- Wait 2-3 minutes
- Check GPS module orientation
- Verify GPS is enabled in flight controller

**AI detection slow:**
- Verify Coral is connected: `lsusb | grep Google`
- Check model is EdgeTPU compiled
- Reduce input image resolution
- Close other processes on Raspberry Pi

**Motors not spinning:**
- Check ESC connections
- Verify motor order in Betaflight
- Calibrate ESCs
- Check for shorts in wiring

## Next Steps

Now that you've completed your first flight and inspection:

1. **Practice Flying**: Get comfortable with manual control
2. **Tune AI Model**: Train on your specific inspection targets
3. **Plan Missions**: Create automated inspection routes
4. **Document Findings**: Keep detailed logs of inspections

## Safety Reminders

- Always fly in open areas
- Check weather conditions
- Maintain visual line of sight
- Follow local regulations
- Have fire extinguisher ready for LiPo batteries
- Never fly over people
- Respect privacy

## Resources

- [Hardware Setup](../hardware/setup.html)
- [Drop Mechanism](../hardware/drop-mechanism.html)
- [Camera Control](../software/camera-control.html)
- [Software Installation](../software/installation.html)
- [AI Applications](../ai-applications/setup.html)

---

[← Back to Home](../) | [Questions? Contact Us](mailto:christianbaun@fra-uas.de)
