# Bighead

Voice-controlled emote system for FiveM. Say specific words to trigger emotes, with background animations cycling automatically while you speak.

## Features

- **Keyword Triggers**: Say "yes", "yeah", "no", "nope", etc. to trigger specific emotes instantly
- **Fallback Cycling**: Random emotes cycle every ~4 seconds while talking if no keywords detected
- **Voice Toggle**: Say "toggle" to activate/deactivate the system
- **GPU Accelerated**: Uses Whisper STT with CUDA for low-latency speech recognition

## Architecture

```
Microphone → Audio Capture → ┬→ VAD (Silero) ────────┬→ State Machine → FiveMDriver → ESP32 BLE → FiveM
                             └→ STT (Whisper) ───────┘
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed diagrams.

## Requirements

### Hardware

| Component | Details |
|-----------|---------|
| ESP32 | Any ESP32 dev board for BLE keyboard emulation |
| Microphone | Any audio input device |
| GPU | NVIDIA with CUDA recommended (CPU fallback available) |

### Software

- Python 3.10+
- PlatformIO (for ESP32 firmware)
- CUDA toolkit (optional, for GPU acceleration)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/bighead.git
cd bighead
```

### 2. Install Python dependencies

```bash
pip install faster-whisper pyaudio numpy pyperclip pyserial torch
```

For GPU acceleration (recommended):
```bash
pip install nvidia-cudnn-cu12==9.1.0.70
```

### 3. Flash ESP32 firmware

```bash
pio run --target upload
```

The ESP32 will appear as a Bluetooth keyboard named "Bighead". Pair it with your PC.

## Usage

### Run the system

```bash
cd python
python main.py           # Full system with ESP32
python main.py --test    # Test mode without hardware
```

### Controls

1. Say **"toggle"** to activate the system (starts paused by default)
2. Speak naturally - the VAD detects when you're talking
3. Say trigger words to play specific emotes
4. Say **"toggle"** again to pause

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
    "emotes": ["hi", "what", "yes", "beg", "shrug", "why"],
    "idle_emote": "wait11",
    "return_to_idle": false
  },
  "keyword_triggers": {
    "cooldown": 3.0,
    "groups": [
      {"triggers": ["yes", "yeah", "yep"], "emotes": ["yes"]},
      {"triggers": ["no", "nope", "nah"], "emotes": ["no", "noway"]}
    ]
  }
}
```

### Config Reference

| Section | Key | Description |
|---------|-----|-------------|
| (root) | `toggle_word` | Word to activate/deactivate system |
| `vad` | `threshold` | Speech detection sensitivity (0-1) |
| `vad` | `min_speech_ms` | Milliseconds of speech before triggering |
| `vad` | `min_silence_ms` | Milliseconds of silence before stopping |
| `talking_mode` | `cycle_interval` | Seconds between fallback emote changes |
| `talking_mode` | `emotes` | Pool of random emotes while talking |
| `talking_mode` | `idle_emote` | Emote when speech ends |
| `talking_mode` | `return_to_idle` | Whether to play idle emote on speech end |
| `keyword_triggers` | `cooldown` | Seconds before same keyword group can trigger again |
| `keyword_triggers` | `groups` | Array of trigger-word to emote mappings |

## Project Structure

```
bighead/
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
└── platformio.ini            # PlatformIO config
```

## How It Works

### State Machine

```
┌──────┐  speech_start  ┌─────────┐  speech_end  ┌───────────┐
│ IDLE │───────────────▶│ TALKING │─────────────▶│idle_emote │──┐
└──────┘                └─────────┘              └───────────┘  │
    ▲                        │                                  │
    │                        │ timer (cycle_interval)           │
    │                        ▼                                  │
    │                  ┌─────────────┐                          │
    │                  │random emote │                          │
    │                  └─────────────┘                          │
    │                                                           │
    └───────────────────────────────────────────────────────────┘

Keywords override at any point - they take priority over random cycling.
```

### Serial Protocol

The ESP32 accepts commands over serial (115200 baud):

| Command | Description |
|---------|-------------|
| `KEY:X` | Press and release key |
| `PRESS:X` / `RELEASE:X` | Hold/release key |
| `TEXT:abc` | Type text (25ms/char) |
| `STATUS` | Check BLE connection |

## Troubleshooting

- **High latency**: Ensure CUDA is installed and Whisper is using GPU
- **VAD triggers on background noise**: Increase `min_silence_ms` in config
- **ESP32 not detected**: Check COM port and ensure device is paired via Bluetooth
- **Emotes not working in FiveM**: FiveM console input works; direct gameplay controls may be blocked by anti-cheat

## License

MIT
