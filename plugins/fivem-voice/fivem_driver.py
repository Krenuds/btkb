"""
FiveM Slash Command Driver

Sends slash commands to FiveM via the Bighead ESP32 Bluetooth keyboard.
Primarily used for emotes (/e dance, /e sit3, etc.) but supports any slash command.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "python"))

import time
import pyperclip

from bighead import Bighead


class FiveMDriver:
    """Driver for sending slash commands to FiveM."""

    def __init__(self, bighead=None, port=None, baud=115200):
        """
        Initialize FiveM driver.

        Args:
            bighead: Existing Bighead connection (optional)
            port: Serial port if creating new connection (auto-detected if None)
            baud: Baud rate if creating new connection
        """
        self._owns_connection = bighead is None
        self._bighead = bighead
        self._port = port
        self._baud = baud

    @property
    def bighead(self):
        """Get the Bighead connection."""
        return self._bighead

    def connect(self):
        """Connect to the ESP32 BLE keyboard."""
        if self._owns_connection:
            self._bighead = Bighead(self._port, self._baud)
            self._bighead.connect()
        return self

    def disconnect(self):
        """Disconnect if we own the connection."""
        if self._owns_connection and self._bighead:
            self._bighead.disconnect()
            self._bighead = None

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
        self._bighead.press("T")
        time.sleep(0.05)
        self._bighead.release("T")
        time.sleep(0.15)  # Wait for console to open

        # Ctrl+V to paste
        self._bighead.press("CTRL")
        time.sleep(0.02)
        self._bighead.key("V")
        time.sleep(0.02)
        self._bighead.release("CTRL")
        time.sleep(0.03)

        # Enter to submit
        self._bighead.key("ENTER")
        time.sleep(0.03)
        self._bighead.release_all()

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
