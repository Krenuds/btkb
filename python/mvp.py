"""
MVP: Voice -> Emote

Say 'yes' or 'no' to trigger the corresponding emote in FiveM.
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

from stt import RealtimeSTT, AudioCapture, EmoteTrigger
from fivem_driver import FiveMDriver


def main():
    print("MVP: Voice-Triggered Emotes")
    print("=" * 40)

    # 1. Connect to ESP32
    print("\n[1/3] Connecting to ESP32...")
    fivem = FiveMDriver()
    fivem.connect()
    print("      Connected!")

    # 2. Start STT engine
    print("\n[2/3] Loading Whisper model...")
    stt = RealtimeSTT(model_size="tiny")
    stt.start()

    # 3. Wire emote trigger with FiveM connection
    trigger = EmoteTrigger(fivem=fivem, cooldown=2.0)

    # 4. Start microphone capture
    print("\n[3/3] Starting microphone...")
    capture = AudioCapture(callback=stt.feed)
    capture.start()

    print("\n" + "=" * 40)
    print("Say 'yes' or 'no' to trigger emotes")
    print("Press Ctrl+C to stop")
    print("=" * 40 + "\n")

    try:
        while True:
            result = stt.get()
            if result:
                text, latency = result
                emote = trigger.process(text)
                if emote:
                    print(f"[{latency*1000:.0f}ms] '{text}' -> /e {emote}")
                else:
                    print(f"[{latency*1000:.0f}ms] '{text}'")
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        capture.stop()
        stt.stop()
        fivem.disconnect()


if __name__ == "__main__":
    main()
