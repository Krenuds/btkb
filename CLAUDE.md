# CLAUDE.md

## Project Overview

**Bighead** is an ESP32 Bluetooth HID keyboard that enables programmatic keystroke injection. The primary use case is a **FiveM slash command driver** for triggering emotes and other in-game commands via Python scripts.

### Architecture

```
Python Script  ──(Serial/USB)──▶  ESP32  ──(Bluetooth HID)──▶  Windows/FiveM
```

- **ESP32 Firmware** (`src/main.cpp`): BLE keyboard that accepts serial commands
- **Python Driver** (`python/fivem_driver.py`): High-level API for FiveM commands
- **Device Name**: "Bighead" (appears in Windows Bluetooth settings)

## Quick Start

```python
from fivem_driver import FiveMDriver

with FiveMDriver() as fm:
    fm.emote("dance3")  # /e dance3
    fm.emote("sit")     # /e sit
    fm.slash("fly")     # /fly
```

## Build Commands

| Command | Description |
|---------|-------------|
| `pio run` | Build firmware |
| `pio run --target upload` | Flash to ESP32 |
| `pio device monitor` | Serial monitor |
| `pio run --target upload && pio device monitor` | Build, flash, monitor |

## Serial Protocol

Commands are sent over serial (115200 baud) with newline terminator.

### Keyboard Commands

| Command | Description | Example |
|---------|-------------|---------|
| `KEY:X` | Press and release key | `KEY:ENTER` |
| `PRESS:X` | Press and hold | `PRESS:CTRL` |
| `RELEASE:X` | Release held key | `RELEASE:CTRL` |
| `RELEASEALL` | Release all keys | |
| `TEXT:abc` | Type text (25ms/char) | `TEXT:hello` |
| `DELAY:ms` | Wait milliseconds | `DELAY:500` |
| `STATUS` | Check BLE connection | |

### Supported Keys

- **Letters**: A-Z (sent as lowercase)
- **Numbers**: 0-9
- **Modifiers**: CTRL, SHIFT, ALT, GUI/WIN
- **Navigation**: UP, DOWN, LEFT, RIGHT, HOME, END, PAGEUP, PAGEDOWN
- **Function**: F1-F12
- **Special**: ENTER, TAB, SPACE, BACKSPACE, DELETE, ESC, INSERT, CAPSLOCK

### Response Codes

| Response | Meaning |
|----------|---------|
| `OK:READY` | Firmware started |
| `OK:CONNECTED` | Bluetooth connected |
| `OK:DISCONNECTED` | Bluetooth disconnected |
| `OK:KEY_SENT` | Key command executed |
| `ERROR:NOT_CONNECTED` | No Bluetooth connection |
| `ERROR:INVALID_KEYCODE` | Unknown key name |

## FiveM Command Flow

The slash command process:
1. Copy command to Windows clipboard (pyperclip)
2. Press `T` to open FiveM console
3. `Ctrl+V` to paste command
4. `Enter` to submit
5. `RELEASEALL` to prevent stuck keys

## Project Structure

```
btkb/
├── src/main.cpp           # ESP32 firmware
├── python/
│   ├── fivem_driver.py    # FiveM slash command driver
│   ├── dance.py           # Single emote example
│   └── testCommand.py     # Multi-command example
├── platformio.ini         # PlatformIO config
└── CLAUDE.md              # This file
```

## Hardware

- **Board**: ESP32 Dev Module (ESP-WROOM-32)
- **Serial**: 115200 baud (USB), COM9 default on Windows
- **BLE Library**: ESP32-BLE-Keyboard

## Known Limitations

- BLE keyboard works for text input but may not trigger DirectInput/Raw Input game controls
- FiveM console (`T` key) works because it's a standard text input field
- Movement keys (WASD) during gameplay may not work due to anti-cheat input handling
