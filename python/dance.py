"""
Dance command: press T, wait 300ms, paste /e dance3, press Enter.
Uses clipboard paste for fast, reliable input.
"""

import serial
import time
import pyperclip


def dance(port="COM9"):
    """Execute dance3 emote command."""
    # Connect
    ser = serial.Serial(port, 115200, timeout=2)
    time.sleep(2)
    ser.reset_input_buffer()
    print("Connected!")

    # Copy command to clipboard first
    pyperclip.copy("/e dance3")

    # Small delay before starting
    time.sleep(0.5)

    # Release any stuck keys first
    ser.write(b"RELEASEALL\n")
    ser.readline()
    time.sleep(0.1)

    # Press t to open console
    ser.write(b"PRESS:T\n")
    ser.readline()
    time.sleep(0.1)  # Hold for 100ms
    ser.write(b"RELEASE:T\n")
    ser.readline()

    # Wait 300ms for console to open
    time.sleep(0.3)

    # Ctrl+V to paste
    ser.write(b"PRESS:CTRL\n")
    ser.readline()
    time.sleep(0.05)
    ser.write(b"KEY:V\n")
    ser.readline()
    time.sleep(0.05)
    ser.write(b"RELEASE:CTRL\n")
    ser.readline()
    time.sleep(0.1)

    # Press Enter to submit
    ser.write(b"KEY:ENTER\n")
    ser.readline()

    # Safety: release all keys
    time.sleep(0.1)
    ser.write(b"RELEASEALL\n")
    ser.readline()

    print("Sent: /e dance3")

    # Close connection
    ser.close()
    print("Done!")


if __name__ == "__main__":
    dance()
