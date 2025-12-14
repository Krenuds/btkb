# CLAUDE.md

## Project Overview

**Bighead** is an ESP32-based Bluetooth keyboard controlled via serial commands. It bridges any serial-capable application to any Bluetooth-enabled device.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Your App   │────▶│   ESP32     │────▶│   Target    │
│  (Serial)   │ USB │ (BLE HID)   │ BT  │   Device    │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Project Structure

```
btkb/
├── src/main.cpp           # ESP32 firmware (the product)
├── python/
│   └── bighead.py         # Python SDK
├── plugins/
│   └── fivem-voice/       # Example: voice-controlled FiveM emotes
├── platformio.ini
└── README.md
```

## Build Commands

| Command | Description |
|---------|-------------|
| `pio run` | Build firmware |
| `pio run --target upload` | Flash to ESP32 |
| `pio device monitor` | Serial monitor |

## Serial Protocol

**115200 baud**, newline-terminated commands.

### Commands

| Command | Description |
|---------|-------------|
| `KEY:X` | Press and release key |
| `PRESS:X` / `RELEASE:X` | Hold/release key |
| `RELEASEALL` | Release all keys |
| `TEXT:abc` | Type string (25ms/char) |
| `MEDIA:PLAY` | Media keys (PLAY, PAUSE, NEXT, PREV, VOLUP, VOLDOWN, MUTE) |
| `RAW:0x17` | Raw HID scancode (hex or decimal) |
| `DELAY:100` | Wait N ms on device |
| `STATUS` | Check BLE connection |

### Keys

- Basic: `ENTER`, `TAB`, `SPACE`, `BACKSPACE`, `DELETE`, `ESC`
- Arrows: `UP`, `DOWN`, `LEFT`, `RIGHT`
- Modifiers: `CTRL`, `SHIFT`, `ALT`, `WIN` (+ right variants: `RCTRL`, etc.)
- Function: `F1`-`F12`
- Navigation: `HOME`, `END`, `PAGEUP`, `PAGEDOWN`, `INSERT`
- Single chars: `A`-`Z`, `0`-`9`

### Responses

- `OK:CONNECTED` / `OK:DISCONNECTED` - BLE status
- `OK:TYPED`, `OK:KEY_SENT`, `OK:KEY_PRESSED`, `OK:KEY_RELEASED` - Success
- `ERROR:NOT_CONNECTED` - BLE not paired
- `ERROR:INVALID_KEYCODE` - Unknown key name

## Python SDK

```python
from bighead import Bighead

with Bighead() as bh:
    bh.text("Hello")
    bh.key("ENTER")
    bh.press("CTRL")
    bh.key("V")
    bh.release("CTRL")
```

Auto-detects CP210x, CH340, FTDI chips. Manual: `Bighead(port="COM9")`.

## Hardware

- Any ESP32 dev board
- USB for power + serial
- BLE range ~10m

Device appears as "Bighead" in Bluetooth settings.
