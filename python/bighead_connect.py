"""
Simple connection test for the Bighead Bluetooth Keyboard.
"""

import serial
import time


def connect(port: str = "COM9", baud: int = 115200, timeout: float = 2.0):
    """Connect to the Bighead device and verify it's ready."""

    print(f"Connecting to {port} at {baud} baud...")

    try:
        ser = serial.Serial(port, baud, timeout=timeout)
    except serial.SerialException as e:
        print(f"ERROR: Could not open {port}: {e}")
        return None

    # Give the device a moment to reset after serial connection
    time.sleep(2)

    # Clear any buffered data
    ser.reset_input_buffer()

    # Send STATUS command to check connection
    print("Sending STATUS command...")
    ser.write(b"STATUS\n")

    # Read response
    response = ser.readline().decode("utf-8").strip()
    print(f"Response: {response}")

    if response == "OK:CONNECTED":
        print("SUCCESS: Device is connected to Bluetooth host!")
        return ser
    elif response == "OK:DISCONNECTED":
        print("WARNING: Device is ready but not paired to a Bluetooth host.")
        print("         Pair 'Bighead' in your Bluetooth settings.")
        return ser
    elif response.startswith("OK:"):
        print(f"SUCCESS: Device responded with {response}")
        return ser
    else:
        print(f"WARNING: Unexpected response: {response}")
        return ser


def main():
    ser = connect()

    if ser:
        print("\nConnection established! Listening for messages...")
        print("Press Ctrl+C to exit.\n")

        try:
            while True:
                if ser.in_waiting:
                    line = ser.readline().decode("utf-8").strip()
                    if line:
                        print(f"< {line}")
        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            ser.close()
            print("Connection closed.")


if __name__ == "__main__":
    main()
