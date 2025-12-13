"""
FiveM Slash Command Driver

Sends slash commands to FiveM via ESP32 Bluetooth keyboard.
Primarily used for emotes (/e dance, /e sit3, etc.) but supports any slash command.
"""

import serial
import time
import pyperclip


class FiveMDriver:
    """Driver for sending slash commands to FiveM."""

    def __init__(self, port="COM9", baud=115200):
        self.port = port
        self.baud = baud
        self.ser = None

    def connect(self):
        """Connect to the ESP32 BLE keyboard."""
        self.ser = serial.Serial(self.port, self.baud, timeout=2)
        time.sleep(2)  # Wait for BLE to stabilize
        self.ser.reset_input_buffer()
        self._send("RELEASEALL")  # Clear any stuck keys
        return self

    def disconnect(self):
        """Disconnect and release all keys."""
        if self.ser:
            self._send("RELEASEALL")
            self.ser.close()
            self.ser = None

    def _send(self, cmd):
        """Send a command to the ESP32."""
        self.ser.write(f"{cmd}\n".encode())
        return self.ser.readline().decode().strip()

    def slash(self, command):
        """
        Send a slash command to FiveM.

        Args:
            command: The command without leading slash (e.g., "e dance3" or "sit")
                     Can also include the slash (e.g., "/e dance3")
        """
        # Normalize: ensure it starts with /
        if not command.startswith("/"):
            command = "/" + command

        # Copy to clipboard
        pyperclip.copy(command)

        # Press T to open console
        self._send("PRESS:T")
        time.sleep(0.1)
        self._send("RELEASE:T")
        time.sleep(0.3)  # Wait for console to open

        # Ctrl+V to paste
        self._send("PRESS:CTRL")
        time.sleep(0.05)
        self._send("KEY:V")
        time.sleep(0.05)
        self._send("RELEASE:CTRL")
        time.sleep(0.1)

        # Enter to submit
        self._send("KEY:ENTER")
        time.sleep(0.1)
        self._send("RELEASEALL")

    def emote(self, name):
        """
        Shortcut for emote commands.

        Args:
            name: Emote name (e.g., "dance3", "sit", "lean")
        """
        self.slash(f"e {name}")

    def __enter__(self):
        """Context manager support."""
        return self.connect()

    def __exit__(self, *args):
        """Context manager cleanup."""
        self.disconnect()


if __name__ == "__main__":
    # Example usage
    with FiveMDriver() as fm:
        print("Connected! Focus FiveM window...")
        time.sleep(2)

        fm.emote("dance3")
        print("Sent: /e dance3")
        time.sleep(3)

        fm.emote("sit")
        print("Sent: /e sit")
        time.sleep(3)

        fm.slash("e lean")
        print("Sent: /e lean")

    print("Done!")
