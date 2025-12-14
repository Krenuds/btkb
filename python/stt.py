"""
Real-Time Speech-to-Text for Emote Triggering

Uses faster-whisper with CUDA GPU acceleration for low-latency STT.
Parses speech and triggers FiveM emotes based on keywords.

Dependencies:
    pip install faster-whisper pyaudio numpy nvidia-cudnn-cu12==9.1.0.70
"""

import os
import sys
import site

# Windows requires explicit DLL directory registration (must happen before CUDA imports)
if sys.platform == "win32":
    for sp in site.getsitepackages() + [site.getusersitepackages()]:
        for lib in ["cudnn", "cublas", "cuda_nvrtc", "cuda_runtime"]:
            dll_path = os.path.join(sp, "nvidia", lib, "bin")
            if os.path.isdir(dll_path):
                os.add_dll_directory(dll_path)

import time
import threading
import queue
import numpy as np

# Audio settings
SAMPLE_RATE = 16000
CHUNK_DURATION = 0.5
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION)


class RealtimeSTT:
    """Real-time speech-to-text with CUDA GPU acceleration."""

    def __init__(self, model_size="tiny", compute_type="float16"):
        self.model_size = model_size
        self.compute_type = compute_type
        self.model = None
        self.audio_queue = queue.Queue()
        self.text_queue = queue.Queue()
        self.running = False
        self._thread = None

    def load_model(self):
        """Load Whisper model on GPU."""
        from faster_whisper import WhisperModel
        print(f"Loading Whisper '{self.model_size}' on CUDA...")
        start = time.time()
        self.model = WhisperModel(self.model_size, device="cuda", compute_type=self.compute_type)
        print(f"Model loaded in {time.time() - start:.2f}s")

    def _worker(self):
        """Background transcription thread."""
        buffer = np.array([], dtype=np.float32)
        min_length = SAMPLE_RATE  # 1 second minimum

        while self.running:
            try:
                chunk = self.audio_queue.get(timeout=0.1)
                buffer = np.concatenate([buffer, chunk])

                if len(buffer) >= min_length:
                    start = time.time()
                    segments, _ = self.model.transcribe(
                        buffer,
                        beam_size=1,
                        language="en",
                        vad_filter=True,
                        vad_parameters={"min_silence_duration_ms": 500},
                    )
                    text = " ".join(s.text for s in segments).strip().lower()
                    if text:
                        self.text_queue.put((text, time.time() - start))
                    buffer = buffer[-SAMPLE_RATE // 2:]  # Keep 0.5s overlap
            except queue.Empty:
                continue

    def start(self):
        """Start the STT engine."""
        if not self.model:
            self.load_model()
        self.running = True
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the STT engine."""
        self.running = False
        if self._thread:
            self._thread.join(timeout=2)

    def feed(self, audio):
        """Feed audio data (float32 numpy array, 16kHz mono)."""
        self.audio_queue.put(audio)

    def get(self, timeout=1.0):
        """Get transcribed text. Returns (text, latency) or None."""
        try:
            return self.text_queue.get(timeout=timeout)
        except queue.Empty:
            return None


class AudioCapture:
    """Microphone capture via PyAudio."""

    def __init__(self, callback=None, callbacks=None, device_index=None):
        """
        Initialize audio capture.

        Args:
            callback: Single callback function (for backward compatibility)
            callbacks: List of callback functions (preferred)
            device_index: Audio device index (None for default)
        """
        # Support both single callback and list of callbacks
        if callbacks is not None:
            self.callbacks = list(callbacks)
        elif callback is not None:
            self.callbacks = [callback]
        else:
            self.callbacks = []
        self.device_index = device_index
        self.stream = None
        self.pa = None

    @staticmethod
    def list_devices():
        """List available input devices."""
        import pyaudio
        pa = pyaudio.PyAudio()
        devices = []
        for i in range(pa.get_device_count()):
            info = pa.get_device_info_by_index(i)
            if info["maxInputChannels"] > 0:
                devices.append({"index": i, "name": info["name"]})
        pa.terminate()
        return devices

    def start(self):
        """Start audio capture."""
        import pyaudio
        self.pa = pyaudio.PyAudio()

        def on_audio(in_data, frame_count, time_info, status):
            audio = np.frombuffer(in_data, dtype=np.int16).astype(np.float32) / 32768.0
            for cb in self.callbacks:
                try:
                    cb(audio)
                except Exception as e:
                    print(f"[AudioCapture] Callback error: {e}")
            return (None, pyaudio.paContinue)

        self.stream = self.pa.open(
            format=pyaudio.paInt16, channels=1, rate=SAMPLE_RATE,
            input=True, input_device_index=self.device_index,
            frames_per_buffer=CHUNK_SIZE, stream_callback=on_audio,
        )
        self.stream.start_stream()

    def stop(self):
        """Stop audio capture."""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.pa:
            self.pa.terminate()


def main():
    """Test STT standalone."""
    print("Bighead Real-Time STT")
    print("=" * 50)

    stt = RealtimeSTT(model_size="tiny")
    stt.start()

    capture = AudioCapture(callback=stt.feed)

    print("\nMicrophones:")
    for d in capture.list_devices():
        print(f"  [{d['index']}] {d['name']}")

    capture.start()
    print("\nListening... (Ctrl+C to stop)\n" + "-" * 50)

    try:
        while True:
            result = stt.get()
            if result:
                text, latency = result
                print(f"[{latency*1000:.0f}ms] {text}")
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        capture.stop()
        stt.stop()


if __name__ == "__main__":
    main()
