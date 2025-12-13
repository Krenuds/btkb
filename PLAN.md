Bighead Bluetooth Keyboard - MVP Implementation Plan

 Project Overview

 Create "Bighead" - an ESP32-based Bluetooth HID keyboard controlled via serial connection from  
 Python, optimized for automation/scripting and text input.

 Approach: Simple Text Protocol (Phase 1 MVP)

 - Timeline: 4-6 hours to working prototype
 - Strategy: Start simple, migrate to advanced features later
 - Focus: Text typing and basic automation commands

 ---
 Phase 1: ESP32 Firmware (Current MVP)

 1. Configure Dependencies

 File: platformio.ini
 - Add library: t-vk/ESP32 BLE Keyboard@^0.3.2

 2. Implement Core Firmware

 File: src/main.cpp

 Architecture:
 - Initialize serial at 115200 baud in setup()
 - Initialize BLE keyboard with name "Bighead"
 - In loop(): read serial commands, parse, execute
 - Simple line-based text protocol

 Serial Protocol Design:
 TEXT:<string>          # Type text (e.g., TEXT:Hello World)
 KEY:<keycode>          # Press and release key (e.g., KEY:ENTER)
 PRESS:<keycode>        # Hold key down (e.g., PRESS:CTRL)
 RELEASE:<keycode>      # Release key (e.g., RELEASE:CTRL)
 RELEASEALL             # Release all held keys
 MEDIA:<action>         # Media key (e.g., MEDIA:PLAY)
 DELAY:<ms>             # Wait (handled by Python, but firmware can support)
 STATUS                 # Return "CONNECTED" or "DISCONNECTED"

 Key Features:
 - All commands terminated by newline (\n)
 - Commands are case-insensitive
 - Error responses start with "ERROR:"
 - Success responses start with "OK:"

 Keycode Mappings (subset for MVP):
 - Basic: ENTER, TAB, SPACE, BACKSPACE, DELETE, ESC
 - Arrows: UP, DOWN, LEFT, RIGHT
 - Modifiers: CTRL, SHIFT, ALT, GUI (Windows key)
 - Function: F1 through F12
 - Special: HOME, END, PAGEUP, PAGEDOWN

 Implementation Steps:
 1. Include ESP32-BLE-Keyboard library
 2. Initialize BleKeyboard bleKeyboard("Bighead", "Your Name", 100);
 3. In setup(): Start serial and BLE keyboard
 4. In loop(): Read serial line, parse command type, switch/case to handler
 5. Implement handlers for each command type
 6. Send response back via Serial for confirmation

 Error Handling:
 - Unknown command → ERROR:UNKNOWN_COMMAND
 - Invalid keycode → ERROR:INVALID_KEYCODE
 - Not connected → ERROR:NOT_CONNECTED
 - Malformed command → ERROR:MALFORMED

 ---
 Phase 2: Python Client Library

 File: bighead_client.py (separate Python project/script)

 Dependencies:
 pip install pyserial

 Class Structure:
 class BigheadKeyboard:
     def __init__(self, port, baud=115200)
     def connect()
     def disconnect()
     def type_text(text: str)
     def press_key(key: str)
     def key_combo(modifiers: list, key: str)  # e.g., Ctrl+C
     def media_key(action: str)
     def is_connected() -> bool

 Example Usage:
 from bighead_client import BigheadKeyboard

 kbd = BigheadKeyboard('COM3')  # or '/dev/ttyUSB0' on Linux
 kbd.connect()

 # Type text
 kbd.type_text("Hello from Bighead!")

 # Press Enter
 kbd.press_key("ENTER")

 # Ctrl+C
 kbd.key_combo(["CTRL"], "C")

 # Complex automation
 kbd.type_text("username")
 kbd.press_key("TAB")
 kbd.type_text("password123")
 kbd.press_key("ENTER")

 kbd.disconnect()

 Implementation Details:
 - Auto-detect available serial ports
 - Timeout handling (default 1 second)
 - Retry logic for connection
 - Command queuing with configurable delays
 - Response validation (check for OK/ERROR)

 ---
 Phase 3: Testing & Validation

 Hardware Testing:

 1. Upload firmware to ESP32
 2. Pair "Bighead" with computer via Bluetooth settings
 3. Run Python test script
 4. Verify keystrokes appear in text editor

 Test Cases:

 - Simple text typing
 - Special characters (!@#$%^&*())
 - Multi-line text (with newlines)
 - Key combinations (Ctrl+C, Ctrl+V, etc.)
 - Arrow key navigation
 - Function keys
 - Connection status checking
 - Error handling (invalid commands)
 - Reconnection after Bluetooth disconnect

 Test Script:

 # test_bighead.py
 kbd = BigheadKeyboard('COM3')
 kbd.connect()

 # Test 1: Basic typing
 kbd.type_text("Test 1: Basic typing works!")
 kbd.press_key("ENTER")

 # Test 2: Key combo
 kbd.key_combo(["CTRL"], "A")  # Select all
 kbd.type_text("Test 2: Key combos work!")

 # Test 3: Navigation
 kbd.press_key("HOME")
 kbd.press_key("END")

 print("All tests completed!")
 kbd.disconnect()

 ---
 Critical Files

 To Create:

 - platformio.ini - Add library dependency (edit existing)
 - src/main.cpp - Complete rewrite with keyboard logic
 - include/KeyboardCommands.h - Command definitions and keycode mappings (optional, can inline)  

 Python Side (Outside Repo):

 - bighead_client.py - Python library
 - examples/basic_typing.py - Simple example
 - examples/form_automation.py - Automation example
 - test_bighead.py - Test suite

 ---
 Future Enhancements (Phase 2 - Migration to Approach 3)

 Raw HID Report Support:

 - Add binary protocol mode (0xFD prefix)
 - Support simultaneous multi-key presses (gaming)
 - Custom HID descriptors

 Advanced Features:

 - Battery level reporting
 - Multiple device pairing
 - On-board macro storage (SPIFFS/LittleFS)
 - LED status indicator
 - Configuration via serial (change device name, etc.)
 - Firmware update via serial

 Python Enhancements:

 - Async/await support
 - Macro recording/playback
 - GUI application for testing
 - Web interface
 - Integration with automation tools (Selenium, PyAutoGUI alternative)

 ---
 Library References

 ESP32 Libraries:
 - https://github.com/T-vK/ESP32-BLE-Keyboard - Main keyboard library
 - https://registry.platformio.org/libraries/t-vk/ESP32%20BLE%20Keyboard

 Python Libraries:
 - https://pythontutorials.net/blog/full-examples-of-using-pyserial-package/
 - https://techtutorialsx.com/2017/12/02/esp32-esp8266-arduino-serial-communication-with-python/ 
 - https://github.com/Rad-hi/ESP_Python_Serial

 Protocol References:
 - https://learn.adafruit.com/introducing-bluefruit-ez-key-diy-bluetooth-hid-keyboard/sending-ke 
 ys-via-serial - Inspiration for Phase 2
 - https://www.usb.org/sites/default/files/documents/hut1_12v2.pdf - Keycode reference

 ---
 Success Criteria

 MVP is complete when:
 - ✅ ESP32 pairs as "Bighead" Bluetooth keyboard
 - ✅ Python can send text strings that appear on connected device
 - ✅ Python can send key commands (Enter, Tab, arrows)
 - ✅ Python can send modifier combinations (Ctrl+C, etc.)
 - ✅ Error handling works (graceful failures)
 - ✅ Reconnection works after Bluetooth disconnect
 - ✅ Code is documented with examples

 ---
 Development Order

 1. Setup (30 min)
   - Add library to platformio.ini
   - Test build compiles
 2. Basic Firmware (2 hours)
   - Serial initialization
   - BLE keyboard initialization
   - Command parser (TEXT, KEY commands)
   - Test with serial monitor
 3. Full Command Set (1.5 hours)
   - PRESS/RELEASE for modifiers
   - Status checking
   - Error responses
   - Keycode mapping table
 4. Python Client (2 hours)
   - Basic BigheadKeyboard class
   - Connection management
   - Command builders
   - Helper methods (type_text, key_combo)
 5. Testing (1 hour)
   - Hardware setup
   - Run test cases
   - Fix bugs
   - Document quirks
 6. Documentation (30 min)
   - Usage examples
   - Pin diagram (if needed)
   - Troubleshooting guide
   - Future roadmap

 Total Estimated Time: ~7 hours (within 4-6 hour estimate with buffer)

 ---
 Notes

 - Serial port on Windows: Usually COM3, COM4, etc.
 - Serial port on Linux/Mac: /dev/ttyUSB0 or /dev/cu.usbserial-*
 - ESP32 must be paired via system Bluetooth settings before use
 - Text typed appears on the device the ESP32 is connected to via Bluetooth
 - Python controls timing - can add delays between commands
 - Keep firmware simple - all complex logic in Python for easier iteration