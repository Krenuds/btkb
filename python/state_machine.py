"""
Emote State Machine for voice-controlled animations.

Manages transitions between IDLE and TALKING states,
with timer-based emote cycling while speaking.
"""

import random
import threading
import time
from enum import Enum, auto


class EmoteState(Enum):
    """Possible states for the emote system."""
    IDLE = auto()
    TALKING = auto()


class EmoteStateMachine:
    """
    State machine for managing voice-triggered emotes.

    States:
        IDLE: Not speaking, no emotes playing
        TALKING: Speaking, cycling through random emotes

    Transitions:
        IDLE -> TALKING: on_speech_start()
        TALKING -> IDLE: on_speech_end() (plays idle emote first)
    """

    def __init__(self, config: dict, fivem_driver):
        """
        Initialize the state machine.

        Args:
            config: talking_mode configuration dict with keys:
                - cycle_interval: Seconds between emote changes
                - emotes: List of emote names to cycle through
                - idle_emote: Emote to play when speech ends
            fivem_driver: FiveMDriver instance for executing emotes
        """
        self.cycle_interval = config.get("cycle_interval", 4.0)
        self.emotes = config.get("emotes", ["think2", "argue", "wait"])
        self.idle_emote = config.get("idle_emote", "wait")

        self.fivem = fivem_driver
        self._state = EmoteState.IDLE
        self._lock = threading.Lock()
        self._cycle_timer = None
        self._last_emote = None

    @property
    def state(self) -> EmoteState:
        """Current state (thread-safe)."""
        with self._lock:
            return self._state

    def on_speech_start(self):
        """
        Handle speech start event from VAD.

        Transitions from IDLE to TALKING and starts emote cycling.
        """
        with self._lock:
            if self._state == EmoteState.IDLE:
                self._state = EmoteState.TALKING
                print(f"[STATE] IDLE -> TALKING")
                self._play_random_emote()
                self._schedule_next_cycle()

    def on_speech_end(self):
        """
        Handle speech end event from VAD.

        Transitions from TALKING to IDLE and plays idle emote.
        """
        with self._lock:
            if self._state == EmoteState.TALKING:
                self._cancel_timer()
                self._state = EmoteState.IDLE
                print(f"[STATE] TALKING -> IDLE")
                self._play_idle_emote()

    def _play_random_emote(self):
        """Play a random emote from the configured list."""
        if not self.emotes:
            return

        # Pick a random emote, avoiding repeats if possible
        available = [e for e in self.emotes if e != self._last_emote]
        if not available:
            available = self.emotes

        emote = random.choice(available)
        self._last_emote = emote
        self._execute_emote(emote)

    def _play_idle_emote(self):
        """Play the idle/neutral emote."""
        if self.idle_emote:
            self._execute_emote(self.idle_emote)

    def _execute_emote(self, emote: str):
        """Execute an emote via FiveMDriver."""
        try:
            print(f"[EMOTE] /e {emote}")
            if self.fivem:
                self.fivem.emote(emote)
        except Exception as e:
            print(f"[ERROR] Failed to execute emote '{emote}': {e}")

    def _schedule_next_cycle(self):
        """Schedule the next emote cycle."""
        self._cancel_timer()
        self._cycle_timer = threading.Timer(self.cycle_interval, self._on_cycle_timer)
        self._cycle_timer.daemon = True
        self._cycle_timer.start()

    def _on_cycle_timer(self):
        """Timer callback for emote cycling."""
        with self._lock:
            if self._state == EmoteState.TALKING:
                self._play_random_emote()
                self._schedule_next_cycle()

    def _cancel_timer(self):
        """Cancel any pending cycle timer."""
        if self._cycle_timer is not None:
            self._cycle_timer.cancel()
            self._cycle_timer = None

    def stop(self):
        """Stop the state machine and clean up."""
        self._cancel_timer()
        with self._lock:
            self._state = EmoteState.IDLE


def main():
    """Test state machine with simulated VAD events."""
    from fivem_driver import FiveMDriver

    config = {
        "cycle_interval": 3.0,
        "emotes": ["think2", "argue", "what", "wait", "notepad"],
        "idle_emote": "wait",
    }

    print("State Machine Test (Ctrl+C to stop)")
    print("-" * 50)
    print("Connecting to ESP32...")

    try:
        with FiveMDriver() as fivem:
            sm = EmoteStateMachine(config, fivem)

            print("\nSimulating: 10s of speech, then 5s silence, repeat")
            print("Focus your FiveM window now!\n")
            time.sleep(3)

            try:
                while True:
                    # Simulate speech start
                    sm.on_speech_start()
                    time.sleep(10)

                    # Simulate speech end
                    sm.on_speech_end()
                    time.sleep(5)
            except KeyboardInterrupt:
                print("\nStopping...")
                sm.stop()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure ESP32 is connected and FiveM is running.")


if __name__ == "__main__":
    main()
