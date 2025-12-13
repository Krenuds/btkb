"""
Voice Activity Detection using Silero VAD.

Detects when the user starts and stops speaking, with hysteresis
to avoid rapid state flipping from brief pauses or noise.
"""

import time
import numpy as np
import torch

# Silero VAD expects 16kHz audio with exactly 512 samples per chunk
SAMPLE_RATE = 16000
VAD_CHUNK_SIZE = 512  # ~32ms at 16kHz


class VADEngine:
    """
    Real-time voice activity detection with speech start/end callbacks.

    Uses Silero VAD (via torch hub) which runs on CPU with ~1ms latency
    per 30ms audio chunk.
    """

    def __init__(
        self,
        config: dict,
        on_speech_start=None,
        on_speech_end=None,
    ):
        """
        Initialize VAD engine.

        Args:
            config: VAD configuration dict with keys:
                - threshold: Speech probability threshold (0.0-1.0)
                - min_speech_ms: Minimum speech duration to trigger start
                - min_silence_ms: Minimum silence duration to trigger end
            on_speech_start: Callback when speech begins (no args)
            on_speech_end: Callback when speech ends (no args)
        """
        self.threshold = config.get("threshold", 0.5)
        self.min_speech_ms = config.get("min_speech_ms", 250)
        self.min_silence_ms = config.get("min_silence_ms", 500)

        self.on_speech_start = on_speech_start
        self.on_speech_end = on_speech_end

        self.model = None
        self._is_speaking = False
        self._speech_start_time = None
        self._silence_start_time = None
        self._triggered_start = False
        self._audio_buffer = np.array([], dtype=np.float32)

    def load_model(self):
        """Load Silero VAD model from torch hub."""
        print("Loading Silero VAD model...")
        self.model, utils = torch.hub.load(
            repo_or_dir="snakers4/silero-vad",
            model="silero_vad",
            force_reload=False,
            trust_repo=True,
        )
        self.model.eval()
        print("VAD model loaded.")

    def reset(self):
        """Reset VAD state (call when restarting audio stream)."""
        self._is_speaking = False
        self._speech_start_time = None
        self._silence_start_time = None
        self._triggered_start = False
        self._audio_buffer = np.array([], dtype=np.float32)
        if self.model is not None:
            self.model.reset_states()

    def process(self, audio_chunk: np.ndarray):
        """
        Process an audio chunk and potentially trigger callbacks.

        Args:
            audio_chunk: float32 numpy array, 16kHz mono, normalized to [-1, 1]
                        Can be any size; will be buffered and processed in 512-sample chunks.
        """
        if self.model is None:
            return

        # Add to buffer
        self._audio_buffer = np.concatenate([self._audio_buffer, audio_chunk])

        # Process all complete 512-sample chunks
        while len(self._audio_buffer) >= VAD_CHUNK_SIZE:
            chunk = self._audio_buffer[:VAD_CHUNK_SIZE]
            self._audio_buffer = self._audio_buffer[VAD_CHUNK_SIZE:]
            self._process_chunk(chunk)

    def _process_chunk(self, chunk: np.ndarray):
        """Process a single 512-sample chunk through VAD."""
        # Convert to torch tensor
        audio_tensor = torch.from_numpy(chunk).float()

        # Get speech probability
        with torch.no_grad():
            speech_prob = self.model(audio_tensor, SAMPLE_RATE).item()

        now = time.time()
        is_speech = speech_prob >= self.threshold

        if is_speech:
            # Reset silence timer
            self._silence_start_time = None

            if not self._is_speaking:
                # Potential speech start
                if self._speech_start_time is None:
                    self._speech_start_time = now

                # Check if we've been speaking long enough
                elapsed_ms = (now - self._speech_start_time) * 1000
                if elapsed_ms >= self.min_speech_ms and not self._triggered_start:
                    self._is_speaking = True
                    self._triggered_start = True
                    if self.on_speech_start:
                        self.on_speech_start()
        else:
            # Reset speech start timer
            self._speech_start_time = None

            if self._is_speaking:
                # Potential speech end
                if self._silence_start_time is None:
                    self._silence_start_time = now

                # Check if we've been silent long enough
                elapsed_ms = (now - self._silence_start_time) * 1000
                if elapsed_ms >= self.min_silence_ms:
                    self._is_speaking = False
                    self._triggered_start = False
                    if self.on_speech_end:
                        self.on_speech_end()

    def is_speaking(self) -> bool:
        """Return current speech state."""
        return self._is_speaking


def main():
    """Test VAD with microphone input."""
    import pyaudio

    CHUNK_SIZE = 512  # ~32ms at 16kHz

    def on_start():
        print("\n>>> SPEECH START")

    def on_end():
        print("<<< SPEECH END\n")

    config = {
        "threshold": 0.5,
        "min_speech_ms": 250,
        "min_silence_ms": 500,
    }

    vad = VADEngine(config, on_speech_start=on_start, on_speech_end=on_end)
    vad.load_model()

    pa = pyaudio.PyAudio()

    def audio_callback(in_data, frame_count, time_info, status):
        audio = np.frombuffer(in_data, dtype=np.int16).astype(np.float32) / 32768.0
        vad.process(audio)
        return (None, pyaudio.paContinue)

    stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE,
        stream_callback=audio_callback,
    )

    print("VAD Test - Speak into microphone (Ctrl+C to stop)")
    print("-" * 50)

    stream.start_stream()

    try:
        while stream.is_active():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()


if __name__ == "__main__":
    main()
