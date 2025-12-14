# CLAUDE.md

Bighead is an ESP32 Bluetooth keyboard you control via serial. This SDK lets you send keystrokes to any paired device.

## Install

```
pip install pyserial
```

## Quick Start

```python
from bighead import Bighead

with Bighead() as bh:
    bh.text("Hello")
    bh.key("ENTER")
```

Auto-detects common ESP32 USB chips. Manual port: `Bighead(port="COM9")`

## API Reference

| Method | Description |
|--------|-------------|
| `connect()` | Connect to device (called automatically with `with`) |
| `disconnect()` | Disconnect (called automatically) |
| `key(name)` | Press and release a key |
| `press(name)` | Hold a key down |
| `release(name)` | Release a held key |
| `release_all()` | Release all held keys |
| `text(string)` | Type a string |
| `delay(ms)` | Wait N milliseconds (on device) |
| `status()` | Check BLE connection status |
| `send(cmd)` | Send raw command |

## Serial Protocol

115200 baud, newline-terminated. For raw usage without the SDK:

| Command | Description |
|---------|-------------|
| `KEY:X` | Press and release key |
| `PRESS:X` | Hold key |
| `RELEASE:X` | Release key |
| `RELEASEALL` | Release all keys |
| `TEXT:abc` | Type string |
| `DELAY:100` | Wait N ms |
| `STATUS` | Check BLE status |
| `MEDIA:PLAY` | Media keys (PLAY, PAUSE, NEXT, PREV, VOLUP, VOLDOWN, MUTE) |
| `RAW:0x17` | Raw HID scancode |

## Key Names

**Basic:** `ENTER`, `TAB`, `SPACE`, `BACKSPACE`, `DELETE`, `ESC`

**Arrows:** `UP`, `DOWN`, `LEFT`, `RIGHT`

**Modifiers:** `CTRL`, `SHIFT`, `ALT`, `WIN` (also `RCTRL`, `RSHIFT`, `RALT`, `RWIN`)

**Function:** `F1` - `F12`

**Navigation:** `HOME`, `END`, `PAGEUP`, `PAGEDOWN`, `INSERT`

**Characters:** `A`-`Z`, `0`-`9`

## Responses

| Response | Meaning |
|----------|---------|
| `OK:CONNECTED` | BLE is paired |
| `OK:DISCONNECTED` | BLE not paired |
| `OK:TYPED` | Text sent |
| `OK:KEY_SENT` | Key pressed and released |
| `OK:KEY_PRESSED` | Key held |
| `OK:KEY_RELEASED` | Key released |
| `ERROR:NOT_CONNECTED` | BLE not paired to target |
| `ERROR:INVALID_KEYCODE` | Unknown key name |
