# CLAUDE.md

## Project Overview

**Bighead** is a voice-controlled emote system for FiveM. Say specific words to trigger emotes, with background animations cycling automatically while you speak.

## Architecture

```
                    ┌─────────────────────────────────────────────┐
                    │              State Machine                   │
                    │         (IDLE / TALKING states)              │
                    └─────────────────────────────────────────────┘
                                        ▲
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
              keyword emote        speech start       speech end
              (priority)           /random emote      /idle emote
                    │                   │                   │
         ┌─────────────────┐    ┌─────────────┐            │
         │ Keyword Matcher │    │     VAD     │────────────┘
         │  (Whisper STT)  │    │  (Silero)   │
         └─────────────────┘    └─────────────┘
                    ▲                   ▲
                    └───────┬───────────┘
                            │
                    ┌───────────────┐
                    │ Audio Capture │
                    │  (PyAudio)    │
                    └───────────────┘
                            │
                            ▼
                    ┌───────────────┐      ┌─────────────┐
                    │  FiveMDriver  │─────▶│ ESP32 BLE   │─────▶ FiveM
                    │  (clipboard)  │      │  Keyboard   │
                    └───────────────┘      └─────────────┘
```

### Two-Layer Emote System

1. **Keywords (Priority)**: Say "yes", "yeah", "no", "nope" etc. to trigger specific emotes instantly
2. **Fallback Cycling**: While talking, random emotes cycle every ~4 seconds if no keywords detected

### Voice Toggle

The system starts **paused** by default. Say "toggle" to activate/deactivate:
- **Paused**: STT still listens but VAD and keyword triggers are ignored
- **Active**: Full emote system running

## Quick Start

```bash
cd python
python main.py           # Full system with ESP32
python main.py --test    # Test mode without hardware
```

Say "toggle" to activate the system, then speak to trigger emotes.

## Configuration

Edit `python/config.json`:

```json
{
  "toggle_word": "toggle",
  "vad": {
    "threshold": 0.5,
    "min_speech_ms": 250,
    "min_silence_ms": 2000
  },
  "talking_mode": {
    "cycle_interval": 4.0,
    "emotes": ["impatient", "argue", "what", "taunt", "beg", "nervous"],
    "idle_emote": "wait11"
  },
  "keyword_triggers": {
    "cooldown": 3.0,
    "groups": [
      {"triggers": ["yes", "yeah", "yep", "yup"], "emotes": ["yes"]},
      {"triggers": ["no", "nope", "nah"], "emotes": ["no", "no2"]}
    ]
  }
}
```

### Config Reference

| Section | Key | Description |
|---------|-----|-------------|
| (root) | `toggle_word` | Word to activate/deactivate system (default: "toggle") |
| `vad` | `threshold` | Speech detection sensitivity (0-1) |
| `vad` | `min_speech_ms` | Milliseconds of speech before triggering |
| `vad` | `min_silence_ms` | Milliseconds of silence before stopping |
| `talking_mode` | `cycle_interval` | Seconds between fallback emote changes |
| `talking_mode` | `emotes` | Pool of random emotes while talking |
| `talking_mode` | `idle_emote` | Emote when speech ends |
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
│   ├── state_machine.py      # IDLE/TALKING state management
│   ├── stt.py                # Whisper STT + audio capture
│   ├── vad.py                # Silero VAD voice detection
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
| `python vad.py` | Test VAD standalone |

## State Machine

```
                         ┌──────────────────────────────┐
                         │                              │
                         ▼                              │
┌──────┐  speech_start  ┌─────────┐  speech_end  ┌───────────┐
│ IDLE │───────────────▶│ TALKING │─────────────▶│idle_emote │──┐
└──────┘                └─────────┘              └───────────┘  │
    ▲                        │                                  │
    │                        │ timer (4s)                       │
    │                        ▼                                  │
    │                  ┌─────────────┐                          │
    │                  │random emote │                          │
    │                  └─────────────┘                          │
    │                                                           │
    └───────────────────────────────────────────────────────────┘

Keywords override at any point:
  - If IDLE: force transition to TALKING, play keyword emote
  - If TALKING: play keyword emote, reset 4s timer
```

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
- VAD may trigger on loud background noise (increase `min_silence_ms`)
- FiveM console input works; direct gameplay controls may not due to anti-cheat

## Future Improvements

- Add more keyword trigger groups (emotions, actions, gestures)
- Tune VAD sensitivity for different microphone setups
- Add emote sequences (multiple emotes from one trigger)
- WebSocket/direct input for lower latency
