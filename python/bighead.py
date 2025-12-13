"""
Bighead Connection Handler

Low-level serial connection to the ESP32 BLE keyboard device.
Handles command sending, response parsing, and auto-detection.
"""

import serial
import serial.tools.list_ports
import time


# Known USB-to-serial chip identifiers for ESP32 dev boards
KNOWN_DEVICES = [
    {"vid": 0x10C4, "pid": 0xEA60, "name": "CP210x"},      # Silicon Labs CP210x
    {"vid": 0x1A86, "pid": 0x7523, "name": "CH340"},       # CH340
    {"vid": 0x0403, "pid": 0x6001, "name": "FTDI"},        # FTDI FT232
    {"vid": 0x1A86, "pid": 0x55D4, "name": "CH9102"},      # CH9102
]


class Bighead:
    """Connection handler for the ESP32 BLE keyboard."""

    def __init__(self, port=None, baud=115200):
        """
        Initialize Bighead connection parameters.

        Args:
            port: Serial port (auto-detected if None)
            baud: Baud rate (default 115200)
        """
        self.port = port
        self.baud = baud
        self.ser = None
        self._connected = False

    @property
    def connected(self):
        """Check if connected to the device."""
        return self._connected and self.ser is not None

    @staticmethod
    def list_ports():
        """
        List all available serial ports with device info.

        Returns:
            List of dicts with port info
        """
        ports = []
        for p in serial.tools.list_ports.comports():
            ports.append({
                "port": p.device,
                "description": p.description,
                "vid": p.vid,
                "pid": p.pid,
                "serial": p.serial_number,
                "manufacturer": p.manufacturer,
            })
        return ports

    @staticmethod
    def find_port():
        """
        Auto-detect the Bighead device port.

        Returns:
            Port string (e.g., "COM9") or None if not found
        """
        for p in serial.tools.list_ports.comports():
            for device in KNOWN_DEVICES:
                if p.vid == device["vid"] and p.pid == device["pid"]:
                    return p.device
        return None

    def connect(self):
        """
        Connect to the ESP32 BLE keyboard.

        Returns:
            self for method chaining

        Raises:
            ConnectionError: If device not found or connection fails
        """
        # Auto-detect port if not specified
        if self.port is None:
            self.port = self.find_port()
            if self.port is None:
                available = self.list_ports()
                if available:
                    port_info = "\n".join(
                        f"  {p['port']}: {p['description']} (VID:{p['vid']:04X} PID:{p['pid']:04X})"
                        if p['vid'] else f"  {p['port']}: {p['description']}"
                        for p in available
                    )
                    raise ConnectionError(
                        f"Bighead device not found. Available ports:\n{port_info}"
                    )
                raise ConnectionError("No serial ports found")

        self.ser = serial.Serial(self.port, self.baud, timeout=2)
        time.sleep(2)  # Wait for BLE to stabilize
        self.ser.reset_input_buffer()
        self.send("RELEASEALL")  # Clear any stuck keys
        self._connected = True
        return self

    def disconnect(self):
        """Disconnect and release all keys."""
        if self.ser:
            self.send("RELEASEALL")
            self.ser.close()
            self.ser = None
        self._connected = False

    def send(self, cmd):
        """
        Send a raw command to the ESP32.

        Args:
            cmd: Command string (e.g., "KEY:ENTER", "TEXT:hello")

        Returns:
            Response string from device
        """
        if not self.ser:
            raise ConnectionError("Not connected to Bighead device")
        self.ser.write(f"{cmd}\n".encode())
        return self.ser.readline().decode().strip()

    def key(self, key_name):
        """Press and release a key."""
        return self.send(f"KEY:{key_name}")

    def press(self, key_name):
        """Press and hold a key."""
        return self.send(f"PRESS:{key_name}")

    def release(self, key_name):
        """Release a held key."""
        return self.send(f"RELEASE:{key_name}")

    def release_all(self):
        """Release all held keys."""
        return self.send("RELEASEALL")

    def text(self, content):
        """Type text string."""
        return self.send(f"TEXT:{content}")

    def delay(self, ms):
        """Wait for specified milliseconds on device."""
        return self.send(f"DELAY:{ms}")

    def status(self):
        """Check BLE connection status."""
        return self.send("STATUS")

    def __enter__(self):
        """Context manager support."""
        return self.connect()

    def __exit__(self, *args):
        """Context manager cleanup."""
        self.disconnect()


if __name__ == "__main__":
    print("Scanning for devices...")
    for p in Bighead.list_ports():
        vid = f"{p['vid']:04X}" if p['vid'] else "----"
        pid = f"{p['pid']:04X}" if p['pid'] else "----"
        print(f"  {p['port']}: {p['description']} (VID:{vid} PID:{pid})")

    port = Bighead.find_port()
    if port:
        print(f"\nFound Bighead on {port}")
        with Bighead() as bh:
            print(f"Connected: {bh.connected}")
            print(f"Status: {bh.status()}")
    else:
        print("\nBighead device not found")
