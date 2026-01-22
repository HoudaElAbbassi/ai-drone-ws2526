---
layout: default
title: Drop Mechanism
---

# Drop Mechanism

[← Back to Hardware Setup](setup.html)

## Overview

Der Drop Mechanism ermöglicht das ferngesteuerte Abwerfen von Nutzlasten während des Fluges. Das System nutzt einen Servo-Motor, der über den RC-Sender (AUX8-Kanal) gesteuert wird und mit dem INAV Flight Controller über das MSP-Protokoll kommuniziert.

## Fotos

### Aktuelles Foto

![Drop Mechanism Foto](../assets/images/drop-mechanism-photo.jpg)
*Platzhalter: Aktuelles Foto des Drop Mechanism hier einfügen*

<!-- TODO: Ersetze den Platzhalter mit dem tatsächlichen Foto -->
<!-- Speichere das Foto unter: docs/assets/images/drop-mechanism-photo.jpg -->

### 3D-Modell

![Drop Mechanism 3D-Modell](../assets/images/drop-mechanism-3d-model.jpg)
*Platzhalter: 3D-Modell des Drop Mechanism hier einfügen*

<!-- TODO: Ersetze den Platzhalter mit dem 3D-Modell Rendering -->
<!-- Speichere das Bild unter: docs/assets/images/drop-mechanism-3d-model.jpg -->

## Komponenten

| Komponente | Spezifikation | Zweck |
|-----------|---------------|-------|
| Servo Motor | Standard Servo (z.B. SG90/MG90S) | Mechanische Betätigung |
| Raspberry Pi | Pi Zero 2 WH | Steuerungslogik |
| GPIO Pin | Pin 18 (BCM) | PWM-Signal für Servo |
| Flight Controller | INAV-kompatibel | RC-Kanal Übertragung |
| UART Verbindung | /dev/ttyS0 @ 115200 Baud | MSP-Kommunikation |

## Funktionsweise

### Systemarchitektur

```
┌─────────────────────────────────────────────────────────────┐
│                     RC-Sender (Fernsteuerung)               │
│                         AUX8 Schalter                       │
└──────────────────────────┬──────────────────────────────────┘
                           │ RC-Signal
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   ELRS Receiver                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               INAV Flight Controller                        │
│                  (MSP Protokoll)                            │
└──────────────────────────┬──────────────────────────────────┘
                           │ UART (ttyS0)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Raspberry Pi Zero 2                        │
│              drop-mechanism.py Script                       │
│                                                             │
│  1. Liest RC-Kanäle via MSP                                 │
│  2. Überwacht AUX8 Wert                                     │
│  3. Toggle bei Knopf-Loslassen                              │
└──────────────────────────┬──────────────────────────────────┘
                           │ GPIO 18 (PWM)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Servo Motor                              │
│           OFFEN (180°) ←→ GESCHLOSSEN (0°)                  │
└─────────────────────────────────────────────────────────────┘
```

### Steuerungslogik

Das System verwendet eine **Toggle-Logik beim Loslassen** des AUX8-Schalters:

1. **Knopf drücken**: Keine Aktion (nur Statusanzeige)
2. **Knopf loslassen**: Servo wechselt Position
   - War GESCHLOSSEN → wird OFFEN (180°)
   - War OFFEN → wird GESCHLOSSEN (0°)

Diese Logik verhindert unbeabsichtigtes mehrfaches Auslösen.

## Konfiguration

### Servo-Einstellungen

```python
SERVO_PIN = 18              # GPIO Pin (BCM-Nummerierung)
SERVO_OPEN_ANGLE = 180      # Offene Position (links)
SERVO_CLOSED_ANGLE = 0      # Geschlossene Position (rechts)
```

### Kommunikationsparameter

```python
SERIAL_PORT = '/dev/ttyS0'  # UART Port
BAUD_RATE = 115200          # Baudrate
AUX_CHANNEL_INDEX = 8       # AUX8 Kanal (0-basiert)
TRIGGER_VALUE = 1000        # PWM-Schwellwert (<1000 = gedrückt)
```

## Verkabelung

### Servo-Anschluss

```
Raspberry Pi                 Servo
─────────────               ─────────
GPIO 18 (Pin 12) ──────────→ Signal (Orange/Gelb)
5V (Pin 2 oder 4) ─────────→ VCC (Rot)
GND (Pin 6) ───────────────→ GND (Braun/Schwarz)
```

### UART-Verbindung zum Flight Controller

```
Raspberry Pi                 Flight Controller
─────────────               ─────────────────
TX (GPIO 14) ──────────────→ RX (UART)
RX (GPIO 15) ←──────────────  TX (UART)
GND ───────────────────────→ GND
```

## Installation

### Voraussetzungen

```bash
# Python-Pakete installieren
pip3 install pyserial RPi.GPIO
```

### Script kopieren

Das Script `drop-mechanism.py` befindet sich im Root-Verzeichnis des Projekts:

```bash
# Script ausführbar machen
chmod +x drop-mechanism.py

# Script starten
python3 drop-mechanism.py
```

### Autostart einrichten (optional)

```bash
# Systemd Service erstellen
sudo nano /etc/systemd/system/drop-mechanism.service
```

Service-Datei Inhalt:

```ini
[Unit]
Description=Drop Mechanism Control
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /home/pi/drop-mechanism.py
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Aktivieren:

```bash
sudo systemctl enable drop-mechanism.service
sudo systemctl start drop-mechanism.service
```

## Verwendung

### Manuelle Steuerung

1. **Script starten**: `python3 drop-mechanism.py`
2. **Status beobachten**: Terminal zeigt aktuellen Zustand
3. **AUX8 betätigen**: Schalter am RC-Sender drücken und loslassen
4. **Servo reagiert**: Toggle zwischen OFFEN und GESCHLOSSEN

### Terminal-Ausgabe

```
✅ Serial: /dev/ttyS0
🔒 Servo GESCHLOSSEN | Warte auf Knopf...
🎮 AUX Knopf gedrückt=EIN → loslassen=TOGGLE
AUX:1500 🔴 LOS | Servo: 🔒 GESCHLOSSEN

🔄 Knopf losgelassen! AUX:1500 → Toggle...
   → ÖFFNEN (LINKS)
AUX:1500 🔴 LOS | Servo: 🔓 OFFEN
```

## Code-Erklärung

### MSP-Protokoll

Das Script verwendet das MSP (MultiWii Serial Protocol) zur Kommunikation mit dem Flight Controller:

```python
MSP_RC_REQUEST = b'$M<\x00\x69\x69'

def get_rc_channels():
    ser.write(MSP_RC_REQUEST)
    header = ser.read(5)
    if header[:3] != b'$M>': return None
    size = header[3]
    payload = ser.read(size)
    count = size // 2
    return struct.unpack('<' + 'H'*count, payload)
```

### PWM-Berechnung

Die Servo-Position wird über den Duty-Cycle gesteuert:

```python
def set_servo_angle(angle):
    duty = 2 + (angle / 18)  # Konvertiert Winkel zu Duty-Cycle
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)          # Wartezeit für Servo-Bewegung
    pwm.ChangeDutyCycle(0)   # PWM stoppen (verhindert Zittern)
```

## Troubleshooting

### Häufige Probleme

**Problem**: Serial Fehler beim Start
- Überprüfe UART-Verbindung
- Stelle sicher, dass `/dev/ttyS0` verfügbar ist
- Prüfe Baudrate-Einstellung im Flight Controller

**Problem**: Servo reagiert nicht
- Überprüfe GPIO-Verkabelung
- Prüfe 5V Stromversorgung für Servo
- Teste Servo separat mit einfachem PWM-Script

**Problem**: AUX-Kanal zeigt keine Änderung
- Überprüfe AUX8-Zuweisung im RC-Sender
- Stelle sicher, dass MSP im Flight Controller aktiviert ist
- Prüfe UART-Port-Konfiguration in INAV

**Problem**: Servo zittert
- Erhöhe `time.sleep()` Wert in `set_servo_angle()`
- Überprüfe Stromversorgung (zu schwach?)
- Verwende separates BEC für Servo

## Sicherheitshinweise

⚠️ **Wichtige Sicherheitshinweise:**

1. **Vor dem Flug testen**: Immer am Boden testen, bevor der Mechanismus im Flug verwendet wird
2. **Nutzlast sichern**: Sicherstellen, dass die Nutzlast nicht versehentlich auslöst
3. **Fluggebiet prüfen**: Nur in erlaubten Gebieten und mit entsprechender Genehmigung verwenden
4. **Ausfallsicher**: Bei Signalverlust bleibt der Servo in seiner letzten Position

## Anpassungsmöglichkeiten

### Andere Servo-Winkel

```python
# Beispiel: Kleinerer Öffnungswinkel
SERVO_OPEN_ANGLE = 90       # Nur 90° öffnen
SERVO_CLOSED_ANGLE = 0
```

### Anderer AUX-Kanal

```python
# Beispiel: AUX5 statt AUX8 verwenden
AUX_CHANNEL_INDEX = 4       # 0-basiert: AUX5 = Index 4
```

### Invertierte Logik

```python
# Trigger bei hohem Wert statt niedrigem
TRIGGER_VALUE = 1500
button_pressed = (aux_value > TRIGGER_VALUE)  # > statt <
```

## Nächste Schritte

Nach der Einrichtung des Drop Mechanism:
1. [Zurück zum Hardware Setup](setup.html)
2. [Camera Control konfigurieren](../software/camera-control.html)
3. [Erste Flugübungen](../tutorials/getting-started.html)

---

[← Zurück zum Hardware Setup](setup.html) | [Nächstes: Software Installation →](../software/installation.html)
