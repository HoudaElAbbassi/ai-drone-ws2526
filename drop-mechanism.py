#!/usr/bin/env python3
import time
import sys
import serial
import struct
import RPi.GPIO as GPIO

# --- CONFIGURATION ---
SERIAL_PORT = '/dev/ttyS0'
BAUD_RATE = 115200
AUX_CHANNEL_INDEX = 8
TRIGGER_VALUE = 1000  # <1000 = Knopf gedrückt

# --- SERVO CONFIGURATION (LINKS statt RECHTS) ---
SERVO_PIN = 18
SERVO_OPEN_ANGLE = 180    # OFFEN = LINKS
SERVO_CLOSED_ANGLE = 0    # GESCHLOSSEN = RECHTS

# --- INITIALIZE SERIAL ---
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    print(f"✅ Serial: {SERIAL_PORT}")
except Exception as e:
    print(f"❌ Serial Fehler: {e}")
    sys.exit(1)

# --- INITIALIZE SERVO ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

def set_servo_angle(angle):
    duty = 2 + (angle / 18)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    pwm.ChangeDutyCycle(0)

# Servo startet GESCHLOSSEN
set_servo_angle(SERVO_CLOSED_ANGLE)
servo_open = False
last_button_state = False  # Knopf war vorher LOS
print("🔒 Servo GESCHLOSSEN | Warte auf Knopf...")

MSP_RC_REQUEST = b'$M<\x00\x69\x69'

def get_rc_channels():
    try:
        ser.reset_input_buffer()
        ser.write(MSP_RC_REQUEST)
        header = ser.read(5)
        if len(header) < 5 or header[:3] != b'$M>': return None
        size = header[3]
        payload = ser.read(size)
        ser.read(1)
        count = size // 2
        return struct.unpack('<' + 'H'*count, payload)
    except:
        return None

def main():
    global servo_open, last_button_state
    
    print("🎮 AUX Knopf gedrückt=EIN → loslassen=TOGGLE")
    
    try:
        while True:
            channels = get_rc_channels()
            
            if channels and len(channels) > AUX_CHANNEL_INDEX:
                aux_value = channels[AUX_CHANNEL_INDEX]
                button_pressed = (aux_value < TRIGGER_VALUE)  # True = gedrückt
                
                # **NEU: Nur beim LOSLASSEN togglen!**
                if last_button_state and not button_pressed:
                    # Übergang: GEDRÜCKT → LOS = Toggle!
                    print(f"\n🔄 Knopf losgelassen! AUX:{aux_value} → Toggle...")
                    
                    if not servo_open:
                        print("   → ÖFFNEN (LINKS)")
                        set_servo_angle(SERVO_OPEN_ANGLE)
                        servo_open = True
                    else:
                        print("   → SCHLIESSEN (RECHTS)")
                        set_servo_angle(SERVO_CLOSED_ANGLE)
                        servo_open = False
                
                # Status anzeigen
                state = "🟢 GEDRÜCKT" if button_pressed else "🔴 LOS"
                print(f"AUX:{aux_value:4d} {state} | Servo: {'🔓 OFFEN' if servo_open else '🔒 GESCHLOSSEN'}", end='\r')
                
                last_button_state = button_pressed  # Merke Zustand
            
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\n👋 Stop...")
    finally:
        set_servo_angle(SERVO_CLOSED_ANGLE)
        pwm.stop()
        GPIO.cleanup()
        ser.close()

if __name__ == "__main__":
    main()

