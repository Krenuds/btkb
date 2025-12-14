# Bighead

A programmable ESP32-based Bluetooth keyboard that you control via serial commands. Send commands from any application to simulate keyboard input on any connected device.

## What It Does

```
Your App  →  Serial (USB)  →  ESP32  →  Bluetooth HID  →  Any Device
```

The ESP32 appears as a standard Bluetooth keyboard to any device (PC, phone, tablet, game console). You control it by sending simple text commands over USB serial. No drivers needed on the target device.

## Use Cases

- **Automation**: Script keyboard sequences for any application
- **Gaming**: Trigger macros, combos, or chat commands
- **Accessibility**: Create custom input devices
- **Testing**: Automate UI testing on any platform
- **Kiosks**: Control displays without exposing a physical keyboard

## Hardware

| Component | Details |
|-----------|---------|
| ESP32 | Any ESP32 dev board (DevKit, NodeMCU-32S, etc.) |
| USB Cable | For serial communication and power |

That's it. No additional components required.

## Quick Start

### 1. Flash the firmware

```bash
pio run --target upload
```

### 2. Pair via Bluetooth

The ESP32 appears as **"Bighead"** in your Bluetooth settings. Pair it like any keyboard.

### 3. Send commands

Open a serial terminal (115200 baud) or use the Python SDK:

```python
from bighead import Bighead

with Bighead() as bh:
    bh.text("Hello World!")
    bh.key("ENTER")
```

## Serial Protocol

Connect at **115200 baud**. Send commands as text lines (terminated with `\n`).

### Commands

| Command | Example | Description |
|---------|---------|-------------|
| `TEXT:string` | `TEXT:Hello` | Type a string (25ms per character) |
| `KEY:name` | `KEY:ENTER` | Press and release a key |
| `PRESS:name` | `PRESS:CTRL` | Press and hold a key |
| `RELEASE:name` | `RELEASE:CTRL` | Release a held key |
| `RELEASEALL` | `RELEASEALL` | Release all held keys |
| `MEDIA:action` | `MEDIA:PLAY` | Send media key |
| `RAW:code` | `RAW:0x17` | Send raw HID scancode |
| `DELAY:ms` | `DELAY:100` | Wait N milliseconds (max 10000) |
| `STATUS` | `STATUS` | Check BLE connection status |

### Responses

Every command returns a response:

| Response | Meaning |
|----------|---------|
| `OK:READY` | Device initialized |
| `OK:CONNECTED` | BLE connected to host |
| `OK:DISCONNECTED` | BLE not connected |
| `OK:TYPED` | Text sent successfully |
| `OK:KEY_SENT` | Key press sent |
| `OK:KEY_PRESSED` | Key is now held |
| `OK:KEY_RELEASED` | Key released |
| `OK:MEDIA_SENT` | Media key sent |
| `OK:RAW_SENT` | Raw scancode sent |
| `OK:DELAYED` | Delay completed |
| `ERROR:NOT_CONNECTED` | Command failed - BLE not connected |
| `ERROR:INVALID_KEYCODE` | Unknown key name |
| `ERROR:UNKNOWN_COMMAND` | Unrecognized command |

### Supported Keys

**Basic Keys**
```
ENTER, TAB, SPACE, BACKSPACE, DELETE, ESC
```

**Arrow Keys**
```
UP, DOWN, LEFT, RIGHT
```

**Modifiers**
```
CTRL, SHIFT, ALT, WIN (or GUI/META)
RCTRL, RSHIFT, RALT, RGUI (right-side variants)
```

**Function Keys**
```
F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12
```

**Navigation**
```
HOME, END, PAGEUP (PGUP), PAGEDOWN (PGDN), INSERT
```

**Other**
```
CAPSLOCK, PRINTSCREEN (PRTSC)
A-Z, 0-9 (single characters)
```

### Media Keys

```
PLAY, PAUSE, PLAYPAUSE, STOP
NEXT, PREV (track controls)
VOLUMEUP, VOLUMEDOWN, MUTE
```

### Examples

**Type and submit:**
```
TEXT:Hello World
KEY:ENTER
```

**Keyboard shortcut (Ctrl+C):**
```
PRESS:CTRL
KEY:C
RELEASE:CTRL
```

**Media control:**
```
MEDIA:PLAYPAUSE
MEDIA:VOLUMEUP
```

**Raw scancode:**
```
RAW:0x17
RAW:23
```

## Python SDK

A Python wrapper is included in `python/bighead.py`:

```python
from bighead import Bighead

# Auto-detect device
bh = Bighead()
bh.connect()

# Basic operations
bh.text("Hello")           # Type text
bh.key("ENTER")            # Press key
bh.press("SHIFT")          # Hold key
bh.release("SHIFT")        # Release key
bh.release_all()           # Release all
bh.delay(100)              # Wait 100ms on device
print(bh.status())         # Check connection

bh.disconnect()

# Or use context manager
with Bighead() as bh:
    bh.text("Automated typing!")
    bh.key("ENTER")
```

### Device Detection

The SDK auto-detects common ESP32 USB-to-serial chips:
- Silicon Labs CP210x
- CH340/CH9102
- FTDI FT232

Or specify a port manually:
```python
bh = Bighead(port="COM9")  # Windows
bh = Bighead(port="/dev/ttyUSB0")  # Linux
```

## Building

Requires [PlatformIO](https://platformio.org/).

```bash
pio run                    # Build
pio run --target upload    # Flash to ESP32
pio device monitor         # Serial monitor
```

## Project Structure

```
bighead/
├── src/main.cpp           # ESP32 firmware
├── python/
│   └── bighead.py         # Python SDK
├── plugins/
│   └── fivem-voice/       # Example plugin (voice-controlled FiveM emotes)
├── platformio.ini
└── README.md
```

## Example Plugin

The `plugins/fivem-voice/` directory contains an example application: a voice-controlled emote system for FiveM. It uses Whisper for speech recognition and triggers game emotes when you say specific keywords.

```bash
cd plugins/fivem-voice
pip install faster-whisper pyaudio numpy pyperclip pyserial
python main.py
```

## License

MIT
