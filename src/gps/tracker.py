#!/usr/bin/env python3
"""
GPS tracking module for logging detection locations
"""

import time
import threading
from queue import Queue
from typing import Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("WARNING: pyserial not available. GPS disabled.")

from ..config import GPS_CONFIG


@dataclass
class GPSData:
    """GPS data container"""
    timestamp: float
    latitude: float
    longitude: float
    altitude: float
    speed: float
    satellites: int
    fix_quality: int

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude,
            "speed": self.speed,
            "satellites": self.satellites,
            "fix_quality": self.fix_quality,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat()
        }

    def __repr__(self) -> str:
        return (f"GPS(lat={self.latitude:.6f}, lon={self.longitude:.6f}, "
                f"alt={self.altitude:.1f}m, sats={self.satellites})")


class GPSTracker:
    """
    GPS tracker for Matek M10Q-5883 GPS module
    Parses NMEA sentences from serial port
    """

    def __init__(self, port: str = None, baudrate: int = None):
        """
        Initialize GPS tracker

        Args:
            port: Serial port (e.g., /dev/ttyAMA0)
            baudrate: Baud rate
        """
        self.port = port or GPS_CONFIG["port"]
        self.baudrate = baudrate or GPS_CONFIG["baudrate"]

        self.serial = None
        self.running = False
        self.thread = None

        self.current_gps = None
        self.gps_queue = Queue(maxsize=100)
        self.last_fix_time = 0
        self.fix_count = 0

    def start(self):
        """Start GPS tracking"""
        if not SERIAL_AVAILABLE:
            print("GPS disabled: pyserial not available")
            return

        try:
            self.serial = serial.Serial(
                self.port,
                self.baudrate,
                timeout=GPS_CONFIG["timeout"]
            )
            print(f"GPS opened on {self.port} @ {self.baudrate}")

        except Exception as e:
            print(f"Failed to open GPS: {e}")
            return

        self.running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()

    def _read_loop(self):
        """Main GPS reading loop"""
        gga_data = {}
        rmc_data = {}

        while self.running:
            try:
                line = self.serial.readline().decode('ascii', errors='ignore').strip()

                if line.startswith('$GNGGA') or line.startswith('$GPGGA'):
                    # GGA: Fix data
                    gga_data = self._parse_gga(line)

                elif line.startswith('$GNRMC') or line.startswith('$GPRMC'):
                    # RMC: Recommended minimum
                    rmc_data = self._parse_rmc(line)

                # Combine GGA and RMC data
                if gga_data and rmc_data:
                    gps_data = self._combine_data(gga_data, rmc_data)
                    if gps_data:
                        self.current_gps = gps_data
                        if not self.gps_queue.full():
                            self.gps_queue.put(gps_data)
                        self.fix_count += 1
                        self.last_fix_time = time.time()

            except Exception as e:
                print(f"GPS read error: {e}")
                time.sleep(0.1)

    def _parse_gga(self, sentence: str) -> dict:
        """Parse GGA sentence"""
        try:
            parts = sentence.split(',')
            if len(parts) < 15:
                return {}

            # Check if we have a fix
            if parts[6] == '0':  # No fix
                return {}

            lat = self._parse_coordinate(parts[2], parts[3])
            lon = self._parse_coordinate(parts[4], parts[5])
            alt = float(parts[9]) if parts[9] else 0.0
            sats = int(parts[7]) if parts[7] else 0
            fix = int(parts[6]) if parts[6] else 0

            return {
                "latitude": lat,
                "longitude": lon,
                "altitude": alt,
                "satellites": sats,
                "fix_quality": fix,
            }

        except Exception as e:
            return {}

    def _parse_rmc(self, sentence: str) -> dict:
        """Parse RMC sentence"""
        try:
            parts = sentence.split(',')
            if len(parts) < 12:
                return {}

            # Check if data is valid
            if parts[2] != 'A':  # Not valid
                return {}

            lat = self._parse_coordinate(parts[3], parts[4])
            lon = self._parse_coordinate(parts[5], parts[6])
            speed = float(parts[7]) if parts[7] else 0.0  # Speed in knots
            speed_ms = speed * 0.514444  # Convert to m/s

            return {
                "latitude": lat,
                "longitude": lon,
                "speed": speed_ms,
            }

        except Exception as e:
            return {}

    def _parse_coordinate(self, coord_str: str, direction: str) -> float:
        """
        Parse NMEA coordinate to decimal degrees

        Args:
            coord_str: Coordinate string (e.g., "5004.1234")
            direction: Direction (N/S/E/W)

        Returns:
            Decimal degrees
        """
        if not coord_str:
            return 0.0

        # Split degrees and minutes
        if direction in ['N', 'S']:
            # Latitude: ddmm.mmmm
            degrees = float(coord_str[:2])
            minutes = float(coord_str[2:])
        else:
            # Longitude: dddmm.mmmm
            degrees = float(coord_str[:3])
            minutes = float(coord_str[3:])

        # Convert to decimal degrees
        decimal = degrees + (minutes / 60.0)

        # Apply direction
        if direction in ['S', 'W']:
            decimal = -decimal

        return decimal

    def _combine_data(self, gga: dict, rmc: dict) -> Optional[GPSData]:
        """Combine GGA and RMC data"""
        if not gga or not rmc:
            return None

        return GPSData(
            timestamp=time.time(),
            latitude=gga.get("latitude", 0.0),
            longitude=gga.get("longitude", 0.0),
            altitude=gga.get("altitude", 0.0),
            speed=rmc.get("speed", 0.0),
            satellites=gga.get("satellites", 0),
            fix_quality=gga.get("fix_quality", 0),
        )

    def get_current_position(self) -> Optional[GPSData]:
        """Get current GPS position"""
        return self.current_gps

    def get_position_queue(self, timeout: float = 1.0) -> Optional[GPSData]:
        """Get GPS position from queue"""
        try:
            return self.gps_queue.get(timeout=timeout)
        except:
            return None

    def has_fix(self) -> bool:
        """Check if GPS has valid fix"""
        if self.current_gps is None:
            return False
        return self.current_gps.fix_quality > 0

    def get_fix_age(self) -> float:
        """Get age of last fix in seconds"""
        if self.last_fix_time == 0:
            return float('inf')
        return time.time() - self.last_fix_time

    def stop(self):
        """Stop GPS tracking"""
        self.running = False

        if self.thread:
            self.thread.join(timeout=2.0)

        if self.serial:
            self.serial.close()

        print(f"GPS stopped. Received {self.fix_count} fixes.")

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()


class MockGPS(GPSTracker):
    """
    Mock GPS for testing without hardware
    Simulates movement along a path
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lat = 50.1234  # Frankfurt area
        self.lon = 8.6789
        self.alt = 100.0
        self.speed_step = 0.0001  # ~11m per step

    def start(self):
        """Start mock GPS"""
        print("Using mock GPS (no hardware)")
        self.running = True
        self.thread = threading.Thread(target=self._mock_loop, daemon=True)
        self.thread.start()

    def _mock_loop(self):
        """Generate mock GPS data"""
        direction = 1
        while self.running:
            try:
                # Simulate movement
                self.lat += self.speed_step * direction

                # Bounce back and forth
                if abs(self.lat - 50.1234) > 0.01:
                    direction *= -1

                gps_data = GPSData(
                    timestamp=time.time(),
                    latitude=self.lat,
                    longitude=self.lon,
                    altitude=self.alt,
                    speed=3.0,  # 3 m/s
                    satellites=12,
                    fix_quality=1,
                )

                self.current_gps = gps_data
                if not self.gps_queue.full():
                    self.gps_queue.put(gps_data)

                self.fix_count += 1
                self.last_fix_time = time.time()

                time.sleep(1.0)  # 1 Hz update rate

            except Exception as e:
                print(f"Mock GPS error: {e}")
                time.sleep(0.1)


# Test code
if __name__ == "__main__":
    print("Testing GPS tracker...")

    with MockGPS() as gps:
        print("Waiting for GPS fix...")

        for i in range(20):
            time.sleep(1)
            pos = gps.get_current_position()
            if pos:
                print(f"Fix {i}: {pos}")
            else:
                print(f"No fix yet...")

    print("GPS test complete.")
