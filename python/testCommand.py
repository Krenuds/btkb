"""
Test game console commands.
T opens console, type command, Enter submits.
"""

import serial
import time

ser = None


def connect(port="COM9"):
    """Connect to Bighead device."""
    global ser
    ser = serial.Serial(port, 115200, timeout=2)
    time.sleep(2)
    ser.reset_input_buffer()
    print("Connected!")


def command(text):
    """Open console with T, type command, press Enter."""
    # T to open console
    ser.write(b"KEY:T\n")
    ser.readline()

    time.sleep(0.2)  # 200ms for console to open

    # Type the command
    ser.write(f"TEXT:{text}\n".encode())
    ser.readline()

    # Press Enter to submit
    ser.write(b"KEY:ENTER\n")
    ser.readline()

    print(f"Sent: t{text}")


def close():
    """Close connection."""
    if ser:
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
