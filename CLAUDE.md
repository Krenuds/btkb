# CLAUDE.md

## Project Overview

**Bighead** is a voice-controlled emote system for FiveM. Say specific keywords to trigger emotes via speech recognition.

## Architecture

```
┌─────────────────┐     ┌───────────────┐     ┌─────────────────┐
│  AudioCapture   │────▶│  Whisper STT  │────▶│ KeywordMatcher  │
│   (PyAudio)     │     │               │     │                 │
└─────────────────┘     └───────────────┘     └────────┬────────┘
                                                       │
                                              keyword match?
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │   FiveMDriver   │───▶ FiveM
                                              │   (clipboard)   │
                                              └────────┬────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │   ESP32 BLE     │───▶ Game
                                              │   Keyboard      │
                                              └─────────────────┘
```

### Keyword-Only System

Say a keyword → emote plays. No keyword → nothing happens. Simple.

### Voice Toggle

The system starts **paused** by default. Say "toggle" to activate/deactivate:
- **Paused**: STT still listens but keyword triggers are ignored
- **Active**: Keywords trigger emotes

## Quick Start

```bash
cd python
python main.py           # Full system with ESP32
python main.py --test    # Test mode without hardware
```

Say "toggle" to activate the system, then say keywords to trigger emotes.

## Configuration

Edit `python/config.json`:

```json
{
  "toggle_word": "toggle",
  "keyword_triggers": {
    "cooldown": 3.0,
    "groups": [
      {"triggers": ["yes", "yeah", "yep", "yup"], "emotes": ["yes"]},
      {"triggers": ["no", "nope", "nah"], "emotes": ["no", "noway", "forgetit"]}
    ]
  }
}
```

### Config Reference

| Section | Key | Description |
|---------|-----|-------------|
| (root) | `toggle_word` | Word to activate/deactivate system (default: "toggle") |
| `keyword_triggers` | `cooldown` | Seconds before same keyword group can trigger again |
| `keyword_triggers` | `groups` | Array of trigger-word to emote mappings |

## Project Structure

```
btkb/
├── src/main.cpp              # ESP32 BLE keyboard firmware
├── python/
│   ├── main.py               # Orchestrator entry point
│   ├── config.json           # Configuration
│   ├── config_loader.py      # Config loading with defaults
│   ├── keyword_matcher.py    # STT keyword -> emote matching
│   ├── stt.py                # Whisper STT + audio capture
│   ├── vad.py                # Silero VAD (unused, kept for future)
│   ├── fivem_driver.py       # FiveM slash command driver
│   ├── bighead.py            # ESP32 serial connection
│   └── emotes.json           # Available emote reference
├── platformio.ini            # PlatformIO config
└── CLAUDE.md                 # This file
```

## Dependencies

```bash
pip install faster-whisper pyaudio numpy pyperclip pyserial torch
```

**CUDA (recommended)**: For GPU-accelerated STT
```bash
pip install nvidia-cudnn-cu12==9.1.0.70
```

## Hardware

| Component | Details |
|-----------|---------|
| ESP32 | BLE keyboard, device name "Bighead" |
| Serial | 115200 baud, auto-detected COM port |
| GPU | NVIDIA with CUDA for Whisper STT (CPU fallback available) |

## Build Commands

| Command | Description |
|---------|-------------|
| `pio run` | Build ESP32 firmware |
| `pio run --target upload` | Flash to ESP32 |
| `python main.py` | Run full system |
| `python main.py --test` | Test without ESP32 |

## Serial Protocol

ESP32 accepts commands over serial (115200 baud):

| Command | Description |
|---------|-------------|
| `KEY:X` | Press and release key |
| `PRESS:X` / `RELEASE:X` | Hold/release key |
| `TEXT:abc` | Type text (25ms/char) |
| `STATUS` | Check BLE connection |

## Known Limitations

- STT latency: ~30-50ms with GPU, higher on CPU
- Total latency: ~300ms (STT + serial + BLE + game input)
- FiveM console input works; direct gameplay controls may not due to anti-cheat

## Future Improvements

- Re-add VAD-triggered idle/cycling animations (configurable)
- Add emote sequences (multiple emotes from one trigger)
- WebSocket/direct input for lower latency
