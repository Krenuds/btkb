"""
Test game console commands using clipboard paste.
T opens console, Ctrl+V pastes command, Enter submits.
"""

import serial
import time
import pyperclip

ser = None


def connect(port="COM9"):
    """Connect to Bighead device."""
    global ser
    ser = serial.Serial(port, 115200, timeout=2)
    time.sleep(2)
    ser.reset_input_buffer()
    print("Connected!")


def command(text):
    """Open console with T, paste command via Ctrl+V, press Enter."""
    # Copy command to clipboard
    pyperclip.copy(text)

    # T to open console
    ser.write(b"KEY:T\n")
    ser.readline()

    time.sleep(0.1)  # 100ms for console to open

    # Ctrl+V to paste (hold CTRL, press V, release all)
    ser.write(b"PRESS:CTRL\n")
    ser.readline()
    ser.write(b"KEY:V\n")
    ser.readline()
    ser.write(b"RELEASEALL\n")
    ser.readline()

    # Press Enter to submit
    ser.write(b"KEY:ENTER\n")
    ser.readline()

    # Safety: ensure no keys stuck
    ser.write(b"RELEASEALL\n")
    ser.readline()

    print(f"Sent: {text}")


def close():
    """Close connection and release all keys."""
    if ser:
        # Release all keys before disconnecting
        ser.write(b"RELEASEALL\n")
        ser.readline()
        ser.close()
        print("Disconnected.")


if __name__ == "__main__":
    connect()

    time.sleep(1)  # Give user time to focus game window

    command("/e dance3")
    time.sleep(2)

    command("/sit")
    time.sleep(2)

    command("/fly")
    time.sleep(2)

    command("/bird")

    close()
