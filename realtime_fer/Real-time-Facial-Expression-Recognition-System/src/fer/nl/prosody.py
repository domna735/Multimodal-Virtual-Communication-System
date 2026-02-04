from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class ProsodyResult:
    backend: str
    wav_path: str
    ok: bool
    voice_mood: str
    duration_s: float
    sr: int
    rms: Optional[float]
    pitch_hz: Optional[float]


def record_mic_to_wav(
    out_wav: Path,
    *,
    seconds: float = 3.0,
    sr: int = 16000,
) -> bool:
    """Record from the default microphone and write a wav file.

    Returns True on success.

    Optional-deps friendly: returns False if sounddevice/soundfile/numpy are missing.
    """
    try:
        import numpy as np  # type: ignore
    except Exception:
        return False

    try:
        import sounddevice as sd  # type: ignore
    except Exception:
        return False

    try:
        import soundfile as sf  # type: ignore
    except Exception:
        return False

    try:
        out_wav.parent.mkdir(parents=True, exist_ok=True)

        n_samples = int(max(0.1, float(seconds)) * int(sr))
        audio = sd.rec(n_samples, samplerate=int(sr), channels=1, dtype="float32")
        sd.wait()

        audio = np.asarray(audio, dtype=np.float32)
        if audio.ndim == 2 and audio.shape[1] == 1:
            audio = audio[:, 0]
        if audio.size == 0:
            return False

        sf.write(str(out_wav), audio, int(sr))
        return True
    except Exception:
        return False


def _classify_voice_mood(*, rms: Optional[float], pitch_hz: Optional[float]) -> str:
    """Very small heuristic classifier for demo purposes.

    Returns one of: calm, excited, tense, sad, unknown

    Notes:
    - `rms` is waveform RMS (0..~1 depending on normalization)
    - `pitch_hz` is median fundamental frequency in Hz
    """
    if rms is None and pitch_hz is None:
        return "unknown"

    # Rough thresholds that work acceptably for normalized audio.
    # These are intentionally simple and will be refined later.
    r = float(rms) if rms is not None else 0.0
    p = float(pitch_hz) if pitch_hz is not None else 0.0

    high_energy = r >= 0.06
    low_energy = r <= 0.02
    high_pitch = p >= 200.0
    low_pitch = 0.0 < p <= 140.0

    if high_energy and high_pitch:
        return "excited"
    if high_energy and low_pitch:
        return "tense"
    if low_energy and low_pitch:
        return "sad"
    if low_energy and high_pitch:
        return "tense"
    return "calm"


def analyze_wav(path: Path) -> Optional[ProsodyResult]:
    """Analyze a pre-recorded wav and return a lightweight prosody summary.

    - This function is optional-deps friendly: if librosa/numpy aren't installed,
      it returns None.
    - Intended for demo-level "voice mood" only.
    """
    try:
        import numpy as np  # type: ignore
    except Exception:
        return None

    try:
        import librosa  # type: ignore
    except Exception:
        return None

    if not path.exists() or not path.is_file():
        return ProsodyResult(
            backend="wav",
            wav_path=str(path),
            ok=False,
            voice_mood="unknown",
            duration_s=0.0,
            sr=0,
            rms=None,
            pitch_hz=None,
        )

    try:
        # Use a stable sampling rate for analysis.
        y, sr = librosa.load(str(path), sr=16000, mono=True)
        if y is None:
            raise RuntimeError("librosa.load returned None")

        y = np.asarray(y, dtype=np.float32)
        if y.size == 0:
            raise RuntimeError("empty audio")

        duration_s = float(len(y) / float(sr))

        rms = float(np.sqrt(np.mean(np.square(y))))

        # Fundamental frequency estimation.
        # Yin is a good simple choice for monophonic voice-like signals.
        f0 = librosa.yin(y, fmin=50.0, fmax=500.0, sr=sr)
        f0 = np.asarray(f0, dtype=np.float32)
        f0 = f0[np.isfinite(f0)]
        pitch_hz: Optional[float] = None
        if f0.size > 0:
            pitch_hz = float(np.median(f0))

        voice_mood = _classify_voice_mood(rms=rms, pitch_hz=pitch_hz)

        return ProsodyResult(
            backend="wav",
            wav_path=str(path),
            ok=True,
            voice_mood=str(voice_mood),
            duration_s=duration_s,
            sr=int(sr),
            rms=rms,
            pitch_hz=pitch_hz,
        )
    except Exception:
        return ProsodyResult(
            backend="wav",
            wav_path=str(path),
            ok=False,
            voice_mood="unknown",
            duration_s=0.0,
            sr=0,
            rms=None,
            pitch_hz=None,
        )
