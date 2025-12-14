# CLAUDE.md - FiveM Voice Plugin

## Overview

Voice-controlled emote system for FiveM. Say keywords to trigger in-game emotes via speech recognition.

## How It Works

```
Microphone → Whisper STT → Keyword Matcher → FiveM Driver → Bighead → Game
```

1. Audio captured continuously from microphone
2. Whisper transcribes speech to text in real-time
3. Keywords matched against trigger groups
4. Matching emote sent as `/e <emote>` command via Bighead BLE keyboard

## Usage

```bash
cd plugins/fivem-voice
python main.py           # Full system with ESP32
python main.py --test    # Test mode (no hardware)
```

- System starts **paused** - say "toggle" to activate
- Say keywords to trigger emotes
- Say "toggle" again to pause

## Dependencies

```bash
pip install faster-whisper pyaudio numpy pyperclip pyserial torch
```

For GPU acceleration (recommended):
```bash
pip install nvidia-cudnn-cu12==9.1.0.70
```

## Configuration

Edit `config.json`:

```json
{
  "toggle_word": "toggle",
  "keyword_triggers": {
    "cooldown": 3.0,
    "groups": [
      {"triggers": ["yes", "yeah", "yep"], "emotes": ["yes"]},
      {"triggers": ["no", "nope", "nah"], "emotes": ["no", "noway"]}
    ]
  }
}
```

| Key | Description |
|-----|-------------|
| `toggle_word` | Word to activate/deactivate system |
| `cooldown` | Seconds before same group can trigger again |
| `triggers` | Words that activate this group |
| `emotes` | Emote(s) to play (random if multiple) |

## File Structure

```
fivem-voice/
├── main.py             # Entry point, orchestrates components
├── config.json         # Keyword trigger configuration
├── config_loader.py    # Config loading with defaults
├── stt.py              # Whisper STT + audio capture
├── keyword_matcher.py  # Trigger word → emote matching
└── fivem_driver.py     # Sends /e commands via Bighead
```

## Architecture

### main.py - VoiceEmoteOrchestrator
- Initializes all components
- Main loop: polls STT → checks keywords → triggers emotes
- Handles toggle word separately (always active, even when paused)

### stt.py - RealtimeSTT
- Uses `faster-whisper` with tiny model
- Runs transcription in background thread
- Returns (text, latency) tuples via queue

### keyword_matcher.py - KeywordMatcher
- Checks transcribed text against trigger groups
- Enforces cooldown per group
- Returns random emote from matching group

### fivem_driver.py - FiveMDriver
- Opens FiveM console (T key)
- Pastes command via clipboard (Ctrl+V)
- Submits with Enter
- Uses Bighead for all keystrokes

## Latency

| Stage | Time |
|-------|------|
| STT (GPU) | ~30-50ms |
| STT (CPU) | ~200-500ms |
| Serial + BLE | ~50ms |
| Game input | ~100ms |
| **Total** | ~200-400ms |

## Troubleshooting

- **High latency**: Ensure CUDA installed, check `nvidia-smi`
- **No audio**: Check microphone permissions, verify device index
- **ESP32 not found**: Check USB connection, ensure device paired
- **Emotes not working**: FiveM must be focused, console must accept `/e` commands
