# CLAUDE.md

## Project Overview

**Bighead** is a voice-controlled emote system for FiveM. Speak a trigger word, and your character performs the corresponding emote.

### How It Works

```
Microphone ──▶ STT (Whisper/CUDA) ──▶ Keyword Match ──▶ FiveMDriver ──▶ ESP32 BLE ──▶ FiveM
```

1. **Listen**: Microphone captures audio in real-time
2. **Transcribe**: GPU-accelerated Whisper converts speech to text
3. **Match**: Keywords trigger specific emotes (e.g., "dance" -> `/e dance`)
4. **Send**: ESP32 Bluetooth keyboard injects the command into FiveM

## Architecture

| Layer | File | Purpose |
|-------|------|---------|
| Speech-to-Text | `python/stt.py` | Real-time transcription with faster-whisper on CUDA |
| Emote Mapping | `python/stt.py` | Keyword -> emote trigger logic with cooldowns |
| FiveM Driver | `python/fivem_driver.py` | Clipboard-paste slash commands via BLE keyboard |
| Device Handler | `python/bighead.py` | Serial connection to ESP32 with auto-detection |
| Orchestrator | `python/main.py` | Entry point that ties components together |
| Firmware | `src/main.cpp` | ESP32 BLE keyboard accepting serial commands |

## Quick Start

**Voice-triggered emotes:**
```bash
cd python
python stt.py --emotes
```

**Manual emote testing:**
```python
from fivem_driver import FiveMDriver

with FiveMDriver() as fm:
    fm.emote("dance3")  # /e dance3
    fm.emote("sit")     # /e sit
```

## Voice Triggers

Say these words to trigger emotes:

| Word | Emote | Word | Emote |
|------|-------|------|-------|
| dance | dance | sit | sit |
| wave | waves | yes | yes |
| no | no | think | think2 |
| wait | wait | beg | beg |
| argue | argue | punch | punching |
| notepad | notepad | impatient | impatient |

## Build Commands

| Command | Description |
|---------|-------------|
| `pio run` | Build firmware |
| `pio run --target upload` | Flash to ESP32 |
| `python python/stt.py --emotes` | Run voice-triggered emotes |
| `python python/stt.py` | Test STT only |

## Hardware

- **ESP32**: BLE keyboard (device name "Bighead")
- **Serial**: 115200 baud, auto-detected COM port
- **GPU**: NVIDIA GPU with CUDA for Whisper acceleration

## Dependencies

```bash
pip install faster-whisper pyaudio numpy pyperclip pyserial nvidia-cudnn-cu12==9.1.0.70
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
│   ├── stt.py             # Real-time speech-to-text + emote triggers
│   ├── fivem_driver.py    # FiveM slash command driver
│   ├── bighead.py         # ESP32 serial connection handler
│   ├── main.py            # Orchestrator entry point
│   └── emotes.json        # Available emote list
├── platformio.ini         # PlatformIO config
└── CLAUDE.md              # This file
```

## Known Limitations

- Whisper "tiny" model trades accuracy for speed (~30-300ms latency)
- FiveM console input works; direct gameplay controls (WASD) may not due to anti-cheat
- Requires NVIDIA GPU with CUDA for real-time performance
