"""
Simulate game chat commands: T to open console, then various emotes.
"""

import serial
import time


def send(ser, command):
    """Send command and print response."""
    ser.write(f"{command}\n".encode())
    response = ser.readline().decode().strip()
    print(f"> {command}")
    print(f"< {response}")
    return response


def main():
    ser = serial.Serial("COM9", 115200, timeout=2)
    time.sleep(2)  # Wait for device reset
    ser.reset_input_buffer()
    print("Connected! Starting command sequence...\n")

    # Press T to open console
    send(ser, "KEY:T")
    time.sleep(1)  # Wait for console to open

    # Type /e dance3 and press Enter
    send(ser, "TEXT:/e dance3")
    time.sleep(0.3)  # Let text finish
    send(ser, "KEY:ENTER")
    time.sleep(2)  # Let the dance play

    # Open console and do /sit
    send(ser, "KEY:T")
    time.sleep(1)
    send(ser, "TEXT:/sit")
    time.sleep(0.3)
    send(ser, "KEY:ENTER")
    time.sleep(2)

    # Open console and do /fly
    send(ser, "KEY:T")
    time.sleep(1)
    send(ser, "TEXT:/fly")
    time.sleep(0.3)
    send(ser, "KEY:ENTER")
    time.sleep(2)

    # Open console and do /bird
    send(ser, "KEY:T")
    time.sleep(1)
    send(ser, "TEXT:/bird")
    time.sleep(0.3)
    send(ser, "KEY:ENTER")

    ser.close()
    print("\nDone!")


if __name__ == "__main__":
    main()
