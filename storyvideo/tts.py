"""Narration with Kokoro (free, open source, runs locally)."""
import hashlib
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
MODEL = ROOT / "models" / "kokoro-v1.0.onnx"
VOICES = ROOT / "models" / "voices-v1.0.bin"

_kokoro = None


def _engine():
    global _kokoro
    if _kokoro is None:
        if not MODEL.exists() or not VOICES.exists():
            raise SystemExit("Kokoro model missing. Run ./setup.sh first.")
        from kokoro_onnx import Kokoro

        _kokoro = Kokoro(str(MODEL), str(VOICES))
    return _kokoro


def _trim(x, sr, thresh=0.01):
    idx = np.where(np.abs(x) > thresh)[0]
    if len(idx) == 0:
        return x
    pad = int(0.03 * sr)
    return x[max(0, idx[0] - pad): idx[-1] + pad]


def speak(text, voice, speed, cache_dir: Path):
    """Return (samples float32 mono, sample_rate). Cached by text/voice/speed."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha1(f"{voice}|{speed}|{text}".encode()).hexdigest()[:16]
    path = cache_dir / f"{key}.wav"
    if path.exists():
        x, sr = sf.read(path, dtype="float32")
        return x, sr
    x, sr = _engine().create(text, voice=voice, speed=speed, lang="en-us")
    x = _trim(np.asarray(x, dtype=np.float32), sr)
    sf.write(path, x, sr)
    return x, sr
