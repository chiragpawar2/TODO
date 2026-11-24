"""Push-to-talk capture, with a pluggable transcriber.

Hold F2, speak, let go. Recording is always available (sounddevice + numpy).
Turning that audio into text needs one of two backends, tried in this order:

  1. faster-whisper, running locally.    pip install faster-whisper
     The right answer for the Pi: no network, no per-request cost, and the
     `tiny`/`base` models handle Hindi and Marathi as well as English.
  2. Any OpenAI-compatible /audio/transcriptions endpoint, using the key
     already in .env.

With neither installed the face still records and tells you plainly that it
cannot hear yet. It does not pretend.

On the Pi this becomes wake-word or VAD driven - there is no keyboard in a
living room - but push-to-talk is the right thing to build first, because it
removes every false-trigger question from the loop while the character is
being judged.
"""

from __future__ import annotations

import io
import os
import threading
import wave

SAMPLE_RATE = 16000
MAX_SECONDS = 20


def _have(mod: str) -> bool:
    try:
        __import__(mod)
        return True
    except Exception:
        return False


class Recorder:
    """Non-blocking microphone capture driven by hold/release."""

    def __init__(self):
        self.available = _have("sounddevice") and _have("numpy")
        self.recording = False
        self._frames: list = []
        self._stream = None
        self.error = "" if self.available else "pip install sounddevice numpy"

    def start(self) -> bool:
        if not self.available or self.recording:
            return False
        import numpy as np
        import sounddevice as sd

        self._frames = []

        def cb(indata, frames, time_info, status):
            self._frames.append(indata.copy())

        try:
            self._stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1,
                                          dtype="int16", callback=cb)
            self._stream.start()
            self.recording = True
            return True
        except Exception as exc:
            self.error = f"{type(exc).__name__}: {exc}"[:90]
            return False

    def stop(self) -> bytes | None:
        """Returns a 16-bit mono WAV, or None if nothing usable was captured."""
        if not self.recording:
            return None
        self.recording = False
        try:
            self._stream.stop()
            self._stream.close()
        except Exception:
            pass
        if not self._frames:
            return None

        import numpy as np
        audio = np.concatenate(self._frames, axis=0)[: SAMPLE_RATE * MAX_SECONDS]
        if len(audio) < SAMPLE_RATE * 0.25:      # a stray tap, not speech
            return None

        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SAMPLE_RATE)
            w.writeframes(audio.tobytes())
        return buf.getvalue()


class Transcriber:
    def __init__(self, languages: list[str] | None = None):
        self.languages = languages or ["English"]
        self._whisper = None
        if _have("faster_whisper"):
            self.backend = "faster-whisper"
        elif os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY") \
                or os.getenv("GROQ_API_KEY"):
            self.backend = "api"
        else:
            self.backend = "none"

    @property
    def ready(self) -> bool:
        return self.backend != "none"

    def hint(self) -> str:
        if self.backend == "none":
            return "no transcriber: pip install faster-whisper (best for the Pi)"
        return f"voice via {self.backend}"

    def transcribe(self, wav: bytes, done) -> None:
        threading.Thread(target=self._work, args=(wav, done), daemon=True).start()

    def _work(self, wav: bytes, done) -> None:
        try:
            if self.backend == "faster-whisper":
                done(self._local(wav))
            elif self.backend == "api":
                done(self._api(wav))
            else:
                done("")
        except Exception as exc:
            done(f"[voice failed: {type(exc).__name__}: {exc}]"[:120])

    def _local(self, wav: bytes) -> str:
        from faster_whisper import WhisperModel
        if self._whisper is None:
            # "base" is the sweet spot for a Pi 5. "tiny" if it struggles.
            self._whisper = WhisperModel("base", device="cpu", compute_type="int8")
        segments, _ = self._whisper.transcribe(io.BytesIO(wav), beam_size=1)
        return " ".join(s.text for s in segments).strip()

    def _api(self, wav: bytes) -> str:
        from openai import OpenAI
        key = (os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
               or os.getenv("GEMINI_API_KEY"))
        base = None
        model = "whisper-1"
        if os.getenv("GROQ_API_KEY"):
            base, model = "https://api.groq.com/openai/v1", "whisper-large-v3-turbo"
        client = OpenAI(api_key=key, base_url=base)
        f = io.BytesIO(wav)
        f.name = "speech.wav"
        return client.audio.transcriptions.create(model=model, file=f).text.strip()
