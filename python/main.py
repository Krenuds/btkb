"""
Bighead Voice-Controlled Emote System

Main entry point that orchestrates STT and keyword matching
to play emotes when specific words are detected.

Usage:
    python main.py           # Run the voice-controlled emote system
    python main.py --test    # Test mode without ESP32 connection
"""

import sys
import time

from config_loader import load_config, get_keyword_config
from stt import AudioCapture, RealtimeSTT
from keyword_matcher import KeywordMatcher
from fivem_driver import FiveMDriver


class VoiceEmoteOrchestrator:
    """
    Main orchestrator for voice-controlled emotes.

    Wires together:
    - AudioCapture: Microphone input
    - RealtimeSTT: Speech-to-text transcription
    - KeywordMatcher: Keyword-to-emote matching
    - FiveMDriver: Emote execution via ESP32
    """

    def __init__(self, config_path: str = None, test_mode: bool = False):
        """
        Initialize the orchestrator.

        Args:
            config_path: Path to config.json (None for default location)
            test_mode: If True, skip ESP32 connection for testing
        """
        self.config = load_config(config_path)
        self.test_mode = test_mode

        self.fivem = None
        self.stt = None
        self.keyword_matcher = None
        self.audio_capture = None

        # Toggle state - when paused, keywords are ignored
        self._paused = True  # Start paused, say "toggle" to activate
        self._toggle_word = self.config.get("toggle_word", "toggle")

    def _toggle(self):
        """Toggle the system on/off."""
        self._paused = not self._paused
        status = "PAUSED" if self._paused else "ACTIVE"
        print(f"\n[{time.time():.3f}] [TOGGLE] System is now {status}")
        print("=" * 60)

    def start(self):
        """Initialize and start all components."""
        print("=" * 60)
        print("Bighead Voice-Controlled Emote System")
        print("=" * 60)

        # 1. Connect to ESP32 (unless in test mode)
        if not self.test_mode:
            print("\n[1/4] Connecting to ESP32...")
            self.fivem = FiveMDriver()
            self.fivem.connect()
            print(f"      Connected: {self.fivem.bighead.port}")
        else:
            print("\n[1/4] Test mode - skipping ESP32 connection")
            self.fivem = None

        # 2. Initialize STT
        print("[2/4] Loading STT model (Whisper)...")
        self.stt = RealtimeSTT(model_size="tiny")
        self.stt.start()

        # 3. Initialize keyword matcher
        print("[3/4] Initializing keyword matcher...")
        keyword_config = get_keyword_config(self.config)
        self.keyword_matcher = KeywordMatcher(keyword_config)
        groups = keyword_config.get("groups", [])
        for group in groups:
            triggers = ", ".join(group.get("triggers", []))
            emotes = ", ".join(group.get("emotes", []))
            print(f"      [{triggers}] -> [{emotes}]")

        # 4. Start audio capture (feeds STT)
        print("[4/4] Starting audio capture...")
        self.audio_capture = AudioCapture(callbacks=[self.stt.feed])

        # List available devices
        print("\n      Available microphones:")
        for d in self.audio_capture.list_devices():
            print(f"        [{d['index']}] {d['name']}")

        self.audio_capture.start()

        print("\n" + "=" * 60)
        print(f"Ready! Say '{self._toggle_word}' to activate. Press Ctrl+C to stop.")
        print("System starts PAUSED - voice commands are ignored until toggled.")
        print("=" * 60 + "\n")

    def run(self):
        """Run the main loop (blocks until interrupted)."""
        try:
            while True:
                # Poll STT for transcriptions
                result = self.stt.get(timeout=0.1)
                if result:
                    text, latency = result
                    text_lower = text.lower()

                    # Check for toggle word (always active, even when paused)
                    if self._toggle_word in text_lower:
                        print(f"[{time.time():.3f}] [STT] '{text}' ({latency*1000:.0f}ms)")
                        self._toggle()
                        continue

                    # Skip keyword processing if paused
                    if self._paused:
                        continue

                    # Check for keyword triggers
                    emote = self.keyword_matcher.match(text)
                    if emote:
                        print(f"[{time.time():.3f}] [STT] '{text}' ({latency*1000:.0f}ms)")
                        print(f"[{time.time():.3f}] [KEYWORD] -> /e {emote}")
                        if self.fivem:
                            self.fivem.emote(emote)
        except KeyboardInterrupt:
            print("\n\nShutting down...")

    def stop(self):
        """Stop all components and clean up."""
        if self.audio_capture:
            self.audio_capture.stop()
        if self.stt:
            self.stt.stop()
        if self.fivem:
            self.fivem.disconnect()
        print("Goodbye!")

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, *args):
        """Context manager exit."""
        self.stop()


def main():
    """Entry point."""
    test_mode = "--test" in sys.argv

    if test_mode:
        print("Running in TEST MODE (no ESP32 required)\n")

    try:
        with VoiceEmoteOrchestrator(test_mode=test_mode) as orch:
            orch.run()
    except Exception as e:
        print(f"\nError: {e}")
        if not test_mode:
            print("Make sure ESP32 is connected and FiveM is running.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
