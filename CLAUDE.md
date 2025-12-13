# CLAUDE.md

## Project Overview

**Bighead** is a voice-controlled emote system for FiveM. When you speak, your character cycles through conversational emotes automatically.

### How It Works

```
Microphone ──▶ VAD (Silero) ──▶ State Machine ──▶ FiveMDriver ──▶ ESP32 BLE ──▶ FiveM
```

1. **Listen**: Microphone captures audio in real-time
2. **Detect**: Silero VAD detects when you start/stop speaking
3. **Animate**: State machine cycles through random emotes while talking
4. **Send**: ESP32 Bluetooth keyboard injects commands into FiveM

## Architecture

| Layer | File | Purpose |
|-------|------|---------|
| Config | `python/config.json` | VAD thresholds, emote list, timing |
| Config Loader | `python/config_loader.py` | Load config with defaults |
| Voice Detection | `python/vad.py` | Silero VAD with speech start/end callbacks |
| State Machine | `python/state_machine.py` | IDLE/TALKING states, emote cycling |
| Audio Capture | `python/stt.py` | Microphone input via PyAudio |
| FiveM Driver | `python/fivem_driver.py` | Clipboard-paste slash commands |
| Device Handler | `python/bighead.py` | Serial connection to ESP32 |
| Orchestrator | `python/main.py` | Entry point wiring all components |
| Firmware | `src/main.cpp` | ESP32 BLE keyboard firmware |

## Quick Start

**Run voice-controlled emotes:**
```bash
cd python
python main.py
```

**Test mode (no ESP32):**
```bash
python main.py --test
```

**Test VAD standalone:**
```bash
python vad.py
```

**Manual emote testing:**
```python
from fivem_driver import FiveMDriver

with FiveMDriver() as fm:
    fm.emote("dance3")  # /e dance3
    fm.emote("sit")     # /e sit
```

## Configuration

Edit `python/config.json`:

```json
{
  "vad": {
    "threshold": 0.5,         // Speech detection sensitivity (0-1)
    "min_speech_ms": 250,     // Min speech before triggering
    "min_silence_ms": 500     // Min silence before stopping
  },
  "talking_mode": {
    "cycle_interval": 4.0,    // Seconds between emote changes
    "emotes": ["think2", "argue", "what", "wait"],
    "idle_emote": "wait"      // Emote when speech ends
  }
}
```

## Build Commands

| Command | Description |
|---------|-------------|
| `pio run` | Build firmware |
| `pio run --target upload` | Flash to ESP32 |
| `python python/main.py` | Run voice-controlled emotes |
| `python python/main.py --test` | Test without ESP32 |
| `python python/vad.py` | Test VAD only |

## Hardware

- **ESP32**: BLE keyboard (device name "Bighead")
- **Serial**: 115200 baud, auto-detected COM port
- **GPU**: Not required (VAD runs on CPU)

## Dependencies

```bash
pip install pyaudio numpy pyperclip pyserial torch
```

## Serial Protocol

The ESP32 accepts commands over serial (115200 baud):

| Command | Description |
|---------|-------------|
| `KEY:X` | Press and release key |
| `PRESS:X` / `RELEASE:X` | Hold/release key |
| `TEXT:abc` | Type text (25ms/char) |
| `STATUS` | Check BLE connection |

## Project Structure

```
btkb/
├── src/main.cpp           # ESP32 BLE keyboard firmware
├── python/
│   ├── main.py            # Orchestrator entry point
│   ├── config.json        # Configuration file
│   ├── config_loader.py   # Config loading with defaults
│   ├── vad.py             # Silero VAD voice detection
│   ├── state_machine.py   # IDLE/TALKING state management
│   ├── stt.py             # Audio capture (+ legacy STT)
│   ├── fivem_driver.py    # FiveM slash command driver
│   ├── bighead.py         # ESP32 serial connection
│   └── emotes.json        # Available emote list (reference)
├── platformio.ini         # PlatformIO config
└── CLAUDE.md              # This file
```

## State Machine

```
IDLE ──(speech_start)──▶ TALKING ──(speech_end)──▶ idle_emote ──▶ IDLE
                              │
                         (timer: 4s)
                              │
                              ▼
                      random emote
```

## Known Limitations

- VAD may trigger on loud background noise
- ~300ms latency from speech to emote (serial + BLE + game)
- FiveM console input works; direct gameplay controls may not due to anti-cheat
