"""
Bighead Orchestrator

Main entry point for the Bighead BLE keyboard system.
Manages the device connection and provides access to drivers.
"""

import time

from bighead import Bighead
from fivem_driver import FiveMDriver


class Orchestrator:
    """Central orchestrator for Bighead operations."""

    def __init__(self, port=None, baud=115200):
        """
        Initialize the orchestrator.

        Args:
            port: Serial port (auto-detected if None)
            baud: Baud rate
        """
        self.bighead = Bighead(port, baud)
        self._fivem = None

    @property
    def fivem(self):
        """Get the FiveM driver (lazy initialization)."""
        if self._fivem is None:
            self._fivem = FiveMDriver(bighead=self.bighead)
        return self._fivem

    def connect(self):
        """Connect to the Bighead device."""
        self.bighead.connect()
        return self

    def disconnect(self):
        """Disconnect from the Bighead device."""
        self.bighead.disconnect()

    def __enter__(self):
        """Context manager support."""
        return self.connect()

    def __exit__(self, *args):
        """Context manager cleanup."""
        self.disconnect()


def main():
    """Example usage of the orchestrator."""
    with Orchestrator() as orch:
        print(f"Connected to Bighead: {orch.bighead.connected}")
        print("Focus FiveM window...")
        time.sleep(2)

        # Use FiveM driver through orchestrator
        orch.fivem.emote("dance3")
        print("Sent: /e dance3")
        time.sleep(3)

        orch.fivem.emote("sit")
        print("Sent: /e sit")

    print("Done!")


if __name__ == "__main__":
    main()
