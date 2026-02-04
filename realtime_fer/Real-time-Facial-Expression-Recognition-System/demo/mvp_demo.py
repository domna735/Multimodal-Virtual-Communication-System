from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2  # type: ignore


REPO_ROOT = Path(__file__).resolve().parents[1]

# Ensure this repo is importable when running as a script:
#   python demo\mvp_demo.py ...
sys.path.insert(0, str(REPO_ROOT))

# Reuse the proven real-time FER building blocks.
import demo.realtime_demo as rd  # noqa: E402

# Optional: load API keys from a local .env file.
try:
    from dotenv import load_dotenv  # type: ignore

    load_dotenv(REPO_ROOT / ".env")
except Exception:
    pass

from src.fer.nl.llm_openai import try_generate_reply_openai  # noqa: E402
from src.fer.nl.llm_azure_openai import try_generate_reply_azure_openai  # noqa: E402
from src.fer.nl.tts_azure import speak_azure  # noqa: E402
from src.fer.nl.stt_azure import AzureContinuousSTT, listen_once_azure  # noqa: E402
from src.fer.nl.prosody import ProsodyResult, analyze_wav, record_mic_to_wav  # noqa: E402
from src.fer.nl.offline_dialogue import (  # noqa: E402
    OfflinePersona,
    generate_offline_reply,
)


@dataclass(frozen=True)
class Persona:
    key: str
    display: str
    style: str


PERSONAS: list[Persona] = [
    Persona(
        key="calm_companion",
        display="Calm Companion",
        style="calm, friendly, emotionally supportive, short sentences",
    ),
    Persona(
        key="supportive_mentor",
        display="Supportive Mentor",
        style="encouraging, structured guidance, practical next steps",
    ),
    Persona(
        key="technical_advisor",
        display="Technical Advisor",
        style="direct, concise, engineering-oriented, actionable",
    ),
]


def _pick_persona(key: str) -> Persona:
    for p in PERSONAS:
        if p.key == key:
            return p
    return PERSONAS[0]


def generate_reply(*, user_text: str, emotion: str, confidence: float, persona: Persona, previous_reply: str = "") -> str:
    # Offline baseline: use the user text (intent + self-report) and only use FER emotion as a gentle hint.
    return generate_offline_reply(
        user_text=user_text,
        detected_emotion=emotion,
        confidence=float(confidence),
        persona=OfflinePersona(key=persona.key, display=persona.display),
        previous_reply=previous_reply or None,
    )


def speak_windows(text: str, *, rate: int = 0, volume: int = 100) -> None:
    """Speak using Windows built-in System.Speech (no extra Python deps).

    If speech fails (e.g., missing voices), we silently continue.
    """
    t = text.strip()
    if not t:
        return

    # Escape single quotes for PowerShell string literal.
    t_ps = t.replace("'", "''")

    ps = (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"$s.Rate = {int(rate)}; "
        f"$s.Volume = {int(volume)}; "
        f"$s.Speak('{t_ps}');"
    )

    try:
        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                ps,
            ],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return


@dataclass
class SessionLogger:
    path: Path

    def __post_init__(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, payload: dict) -> None:
        line = json.dumps(payload, ensure_ascii=False)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")


def _wrap_text(text: str, *, max_chars: int) -> list[str]:
    t = (text or "").strip()
    if not t:
        return []
    words = t.split()
    lines: list[str] = []
    cur: list[str] = []
    cur_len = 0
    for w in words:
        add = len(w) if not cur else (1 + len(w))
        if cur and (cur_len + add) > int(max_chars):
            lines.append(" ".join(cur))
            cur = [w]
            cur_len = len(w)
        else:
            cur.append(w)
            cur_len += add
    if cur:
        lines.append(" ".join(cur))
    return lines


def main() -> int:
    ap = argparse.ArgumentParser(description="MVP demo: webcam FER + persona reply + TTS")
    ap.add_argument(
        "--device",
        type=str,
        default="auto",
        choices=["auto", "cpu", "cuda", "dml"],
        help="Device preference for FER inference.",
    )
    ap.add_argument("--source", type=str, default="webcam", help="'webcam' or a video file path")
    ap.add_argument("--camera-index", type=int, default=0)
    ap.add_argument(
        "--detector",
        type=str,
        default="yunet",
        choices=["yunet", "dnn", "haar"],
    )
    ap.add_argument(
        "--model-ckpt",
        type=Path,
        default=REPO_ROOT
        / "outputs"
        / "students"
        / "CE"
        / "mobilenetv3_large_100_img224_seed1337_CE_20251223_225031"
        / "best.pt",
    )
    ap.add_argument(
        "--persona",
        type=str,
        default="calm_companion",
        choices=[p.key for p in PERSONAS],
    )

    ap.add_argument(
        "--llm",
        type=str,
        default="offline",
        choices=["offline", "openai", "azure-openai"],
        help="Dialogue backend: offline (rule-based), openai (API), or azure-openai (Azure OpenAI API).",
    )
    ap.add_argument(
        "--tts",
        type=str,
        default="windows",
        choices=["windows", "azure"],
        help="TTS backend: windows (System.Speech) or azure (Speech API).",
    )
    ap.add_argument(
        "--stt",
        type=str,
        default="off",
        choices=["off", "azure"],
        help="STT backend for voice input: off or azure (Speech API).",
    )
    ap.add_argument(
        "--stt-mode",
        type=str,
        default="push",
        choices=["push", "continuous"],
        help="STT mode: push (press 'r' to record one utterance) or continuous (hands-free).",
    )
    ap.add_argument(
        "--stt-lang",
        type=str,
        default="en-US",
        help="Speech-to-text language (Azure). Default: en-US",
    )

    ap.add_argument(
        "--prosody",
        type=str,
        default="off",
        choices=["off", "wav", "mic"],
        help="Optional prosody backend: off, wav (pre-recorded .wav), or mic (live mic capture).",
    )
    ap.add_argument(
        "--prosody-wav",
        type=Path,
        default=None,
        help="Path to a pre-recorded .wav file to analyze for voice mood (requires --prosody wav).",
    )
    ap.add_argument(
        "--prosody-seconds",
        type=float,
        default=3.0,
        help="Seconds to record for mic prosody (requires --prosody mic). Default: 3.0",
    )
    ap.add_argument(
        "--log",
        action="store_true",
        help="Enable session logging (JSONL). Default: enabled.",
    )
    ap.add_argument(
        "--no-log",
        action="store_true",
        help="Disable session logging.",
    )
    ap.add_argument(
        "--log-path",
        type=Path,
        default=None,
        help="Where to write JSONL logs (default: outputs/sessions/mvp_<timestamp>.jsonl)",
    )
    ap.add_argument("--speak", action="store_true", help="Enable speech output")
    ap.add_argument("--no-speak", action="store_true", help="Disable speech output")
    args = ap.parse_args()

    persona = _pick_persona(args.persona)

    if not args.model_ckpt.exists():
        raise SystemExit(f"Checkpoint not found: {args.model_ckpt}")

    speak_enabled = bool(args.speak) and (not bool(args.no_speak))

    prosody: Optional[ProsodyResult] = None
    prosody_ms: Optional[float] = None
    prosody_record_ms: Optional[float] = None
    last_audio_wav: Optional[Path] = None

    if str(args.prosody) == "wav":
        if args.prosody_wav is None:
            print("[prosody] --prosody wav set but --prosody-wav not provided; disabling prosody")
        else:
            t0 = time.perf_counter()
            prosody = analyze_wav(Path(args.prosody_wav))
            prosody_ms = (time.perf_counter() - t0) * 1000.0
            if prosody is None:
                print("[prosody] Optional deps missing (install librosa + numpy). Disabling prosody.")
            elif not prosody.ok:
                print(f"[prosody] Failed to analyze wav: {prosody.wav_path}. voice_mood=unknown")
            else:
                phz = "n/a" if prosody.pitch_hz is None else f"{prosody.pitch_hz:.0f}"
                rms = "n/a" if prosody.rms is None else f"{prosody.rms:.3f}"
                print(
                    f"[prosody] wav analyzed: mood={prosody.voice_mood} pitch_hz={phz} rms={rms} dur={prosody.duration_s:.1f}s"
                )

    stamp = time.strftime("%Y%m%d_%H%M%S")
    log_enabled = (not bool(args.no_log)) or bool(args.log)
    log_path = args.log_path or (REPO_ROOT / "outputs" / "sessions" / f"mvp_{stamp}.jsonl")
    logger: Optional[SessionLogger] = SessionLogger(log_path) if log_enabled else None

    infer, _meta = rd._load_student_from_checkpoint(args.model_ckpt, prefer_device=str(args.device))

    detector = rd.FaceDetector(args.detector, model_dir=REPO_ROOT / "demo" / "models")

    if args.source.lower() == "webcam":
        cap = cv2.VideoCapture(int(args.camera_index))
        input_name = f"webcam:{args.camera_index}"
    else:
        cap = cv2.VideoCapture(str(args.source))
        input_name = str(args.source)

    if not cap.isOpened():
        raise SystemExit(f"Failed to open source: {args.source}")

    params = rd.Params()

    ema_probs: Optional[list[float]] = None
    hyster_idx: Optional[int] = None
    votes = rd.deque(maxlen=params.vote_window)

    last_emotion = "neutral"
    last_conf = 0.0
    last_user = ""
    last_bot = ""

    win = "MVP Demo (FER + Persona + TTS)"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)

    t_start = time.time()
    last_frame_ts = t_start
    ema_fps: Optional[float] = None

    if logger is not None:
        logger.log(
            {
                "event": "session_start",
                "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "source": input_name,
                "device_pref": str(args.device),
                "detector": str(args.detector),
                "model_ckpt": str(args.model_ckpt),
                "persona": persona.key,
                "speak_enabled": bool(speak_enabled),
                "llm_backend": str(args.llm),
                "tts_backend": str(args.tts),
                "stt_backend": str(args.stt),
                "stt_mode": str(args.stt_mode),
                "prosody_backend": str(args.prosody),
                "prosody_wav": str(args.prosody_wav) if args.prosody_wav is not None else None,
                "prosody_seconds": float(args.prosody_seconds),
                "prosody_ms": prosody_ms,
                "prosody_record_ms": prosody_record_ms,
                "voice_mood": None if prosody is None else prosody.voice_mood,
            }
        )

    print("\nMVP controls:")
    print("- q: quit")
    print("- p: cycle persona")
    print("- t: type a chat message in console")
    print("- r: record one utterance from microphone (push STT, and prosody if enabled)")
    print("- s: toggle speak")
    if str(args.stt) == "azure" and str(args.stt_mode) == "continuous":
        print("- (continuous STT is ON) speak naturally; the demo will respond after pauses")
    print("\nTip: keep the console visible for chat input.\n")

    # Optional: continuous hands-free STT.
    cont_stt: Optional[AzureContinuousSTT] = None
    last_cont_text: str = ""
    if str(args.stt) == "azure" and str(args.stt_mode) == "continuous":
        cont_stt = AzureContinuousSTT(language=str(args.stt_lang))
        ok_start = cont_stt.start()
        if not ok_start:
            cont_stt = None
            print("[stt] continuous mode requested but Azure STT is not configured/available. Falling back to push mode.")
        elif str(args.prosody) == "mic":
            # Both continuous STT and sounddevice mic-capture can contend for the mic.
            print("[stt] note: --stt-mode continuous may conflict with --prosody mic (both use microphone).")

    # Key debounce / cooldown state.
    last_r_ts: float = 0.0
    last_stt_disabled_ts: float = 0.0

    def _handle_user_message(
        user_text: str,
        *,
        input_mode: str,
        tsec_now: float,
        stt_ms: Optional[float] = None,
        stt_ok: Optional[bool] = None,
    ) -> None:
        nonlocal last_user, last_bot

        last_user = (user_text or "").strip()
        if not last_user:
            return

        llm_ms: Optional[float] = None
        tts_ms: Optional[float] = None
        tts_ok: Optional[bool] = None
        used_llm_fallback = False
        used_tts_fallback = False

        # Demo-level fusion heuristic: if face is Neutral but voice mood suggests emotion,
        # nudge the emotion passed into the reply generator.
        fused_emotion = str(last_emotion)
        if prosody is not None and prosody.ok:
            vm = str(prosody.voice_mood).lower()
            if vm == "sad" and fused_emotion.lower() in {"neutral", "happy"}:
                fused_emotion = "Sad"
            elif vm == "tense" and fused_emotion.lower() in {"neutral", "happy"}:
                fused_emotion = "Angry"
            elif vm == "excited" and fused_emotion.lower() == "neutral":
                fused_emotion = "Happy"

        if str(args.llm) == "openai":
            t0 = time.perf_counter()
            last_bot = (
                try_generate_reply_openai(
                    user_text=last_user,
                    emotion=fused_emotion,
                    persona_display=persona.display,
                    persona_style=persona.style,
                )
                or ""
            )
            llm_ms = (time.perf_counter() - t0) * 1000.0
            if not last_bot:
                used_llm_fallback = True
                last_bot = generate_reply(
                    user_text=last_user,
                    emotion=fused_emotion,
                    confidence=float(last_conf),
                    persona=persona,
                    previous_reply=last_bot,
                )
        elif str(args.llm) == "azure-openai":
            t0 = time.perf_counter()
            last_bot = (
                try_generate_reply_azure_openai(
                    user_text=last_user,
                    emotion=fused_emotion,
                    persona_display=persona.display,
                    persona_style=persona.style,
                )
                or ""
            )
            llm_ms = (time.perf_counter() - t0) * 1000.0
            if not last_bot:
                used_llm_fallback = True
                last_bot = generate_reply(
                    user_text=last_user,
                    emotion=fused_emotion,
                    confidence=float(last_conf),
                    persona=persona,
                    previous_reply=last_bot,
                )
        else:
            last_bot = generate_reply(
                user_text=last_user,
                emotion=fused_emotion,
                confidence=float(last_conf),
                persona=persona,
                previous_reply=last_bot,
            )

        print(f"Bot: {last_bot}\n")
        if logger is not None:
            logger.log(
                {
                    "event": "chat",
                    "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "tsec": float(tsec_now),
                    "emotion": last_emotion,
                    "emotion_fused": fused_emotion,
                    "confidence": float(last_conf),
                    "persona": persona.key,
                    "input_mode": str(input_mode),
                    "stt_backend": str(args.stt),
                    "stt_lang": str(args.stt_lang),
                    "stt_ms": stt_ms,
                    "stt_ok": stt_ok,
                    "prosody_backend": str(args.prosody),
                    "prosody_wav": str(args.prosody_wav) if args.prosody_wav is not None else None,
                    "prosody_seconds": float(args.prosody_seconds),
                    "prosody_ms": prosody_ms,
                    "prosody_record_ms": prosody_record_ms,
                    "voice_mood": None if prosody is None else prosody.voice_mood,
                    "voice_pitch_hz": None if prosody is None else prosody.pitch_hz,
                    "voice_rms": None if prosody is None else prosody.rms,
                    "user": last_user,
                    "bot": last_bot,
                    "speak_enabled": bool(speak_enabled),
                    "llm_backend": str(args.llm),
                    "tts_backend": str(args.tts),
                    "llm_ms": llm_ms,
                    "used_llm_fallback": bool(used_llm_fallback),
                }
            )

        if speak_enabled:
            # In continuous STT mode, pause listening during TTS to avoid feedback/echo loops.
            if cont_stt is not None and cont_stt.is_running:
                cont_stt.stop()

            if str(args.tts) == "azure":
                t0 = time.perf_counter()
                ok = speak_azure(last_bot)
                tts_ms = (time.perf_counter() - t0) * 1000.0
                tts_ok = bool(ok)
                if not ok:
                    used_tts_fallback = True
                    t1 = time.perf_counter()
                    speak_windows(last_bot)
                    tts_ms = (time.perf_counter() - t1) * 1000.0
                    tts_ok = True
            else:
                t0 = time.perf_counter()
                speak_windows(last_bot)
                tts_ms = (time.perf_counter() - t0) * 1000.0
                tts_ok = True

            # Resume continuous STT after speaking.
            if cont_stt is not None and (not cont_stt.is_running):
                _ = cont_stt.start()

        if logger is not None:
            logger.log(
                {
                    "event": "latency",
                    "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "tsec": float(tsec_now),
                    "input_mode": str(input_mode),
                    "stt_backend": str(args.stt),
                    "stt_lang": str(args.stt_lang),
                    "stt_ms": stt_ms,
                    "stt_ok": stt_ok,
                    "prosody_backend": str(args.prosody),
                    "prosody_wav": str(args.prosody_wav) if args.prosody_wav is not None else None,
                    "prosody_seconds": float(args.prosody_seconds),
                    "prosody_ms": prosody_ms,
                    "prosody_record_ms": prosody_record_ms,
                    "llm_backend": str(args.llm),
                    "tts_backend": str(args.tts),
                    "llm_ms": llm_ms,
                    "tts_ms": tts_ms,
                    "tts_ok": tts_ok,
                    "used_llm_fallback": bool(used_llm_fallback),
                    "used_tts_fallback": bool(used_tts_fallback),
                }
            )

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        now = time.time()
        tsec = now - t_start

        dt = max(1e-6, float(now - last_frame_ts))
        last_frame_ts = now
        inst_fps = 1.0 / dt
        if ema_fps is None:
            ema_fps = float(inst_fps)
        else:
            ema_fps = 0.9 * float(ema_fps) + 0.1 * float(inst_fps)

        faces = detector.detect(frame)
        face_box = rd._largest_face(faces)

        probs = [0.0] * len(rd.CANONICAL_7)
        pred_idx: Optional[int] = None

        if face_box is not None:
            x, y, w, h = face_box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 220, 220), 2)
            crop = rd._crop_with_margin(frame, face_box)
            _logits, probs = infer(crop)

            if ema_probs is None:
                ema_probs = list(probs)
            else:
                a = float(params.ema_alpha)
                ema_probs = [a * e + (1.0 - a) * p for e, p in zip(ema_probs, probs)]

            hyster_idx = rd._apply_hysteresis(ema_probs, hyster_idx, params.hysteresis_delta)

            votes = rd.deque(votes, maxlen=params.vote_window)
            if hyster_idx is not None:
                votes.append(int(hyster_idx))
            pred_idx = rd._vote_smooth(votes, window=params.vote_window, min_count=params.vote_min_count)

        if pred_idx is not None:
            last_emotion = rd.CANONICAL_7[pred_idx]
            if ema_probs is not None:
                last_conf = float(max(ema_probs))
            else:
                last_conf = float(max(probs))

        fps = float(ema_fps or 0.0)

        # UI overlays
        header = (
            f"emotion={last_emotion} ({last_conf:.2f}) | persona={persona.display} | "
            f"llm={args.llm} | tts={args.tts} | stt={args.stt}:{args.stt_mode} | prosody={args.prosody} | speak={'on' if speak_enabled else 'off'}"
        )
        cv2.putText(frame, header, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

        if prosody is not None:
            vm = prosody.voice_mood
            phz = "n/a" if prosody.pitch_hz is None else f"{prosody.pitch_hz:.0f}"
            cv2.putText(
                frame,
                f"voice_mood={vm} | pitch_hz={phz}",
                (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (240, 240, 240),
                1,
                cv2.LINE_AA,
            )
        cv2.putText(
            frame,
            f"t={tsec:.1f}s | fps={fps:.1f} | press 't' to type, 'r' to talk | logs={'on' if logger is not None else 'off'}",
            (10, 55),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (240, 240, 240),
            1,
            cv2.LINE_AA,
        )

        # Hands-free: poll continuous STT and auto-handle recognized phrases.
        if cont_stt is not None and cont_stt.is_running:
            text = cont_stt.poll_text()
            if text:
                norm = text.strip()
                if norm and norm != last_cont_text:
                    last_cont_text = norm
                    print(f"You(STT-cont): {norm}\n")
                    _handle_user_message(norm, input_mode="stt_continuous", tsec_now=float(tsec), stt_ms=None, stt_ok=True)

        y0 = 85
        if last_user:
            for li, line in enumerate(_wrap_text(f"you: {last_user}", max_chars=70)[:2]):
                cv2.putText(frame, line, (10, y0 + li * 22), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 220, 255), 1, cv2.LINE_AA)
            y0 += 44

        if last_bot:
            for li, line in enumerate(_wrap_text(f"bot: {last_bot}", max_chars=70)[:3]):
                cv2.putText(frame, line, (10, y0 + li * 22), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220, 220, 220), 1, cv2.LINE_AA)

        cv2.imshow(win, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

        if key == ord("p"):
            idx = [p.key for p in PERSONAS].index(persona.key)
            persona = PERSONAS[(idx + 1) % len(PERSONAS)]
            print(f"Persona -> {persona.display}")
            if logger is not None:
                logger.log(
                    {
                        "event": "persona_change",
                        "tsec": float(tsec),
                        "persona": persona.key,
                        "emotion": last_emotion,
                        "confidence": float(last_conf),
                    }
                )

        if key == ord("s"):
            speak_enabled = not speak_enabled
            print(f"Speak -> {'on' if speak_enabled else 'off'}")
            if logger is not None:
                logger.log(
                    {
                        "event": "speak_toggle",
                        "tsec": float(tsec),
                        "speak_enabled": bool(speak_enabled),
                    }
                )

        if key == ord("t"):
            # Take chat input via console.
            print(f"\n[emotion={last_emotion}] [persona={persona.display}]")
            typed = input("You: ").strip()
            if typed:
                _handle_user_message(typed, input_mode="typed", tsec_now=float(tsec))

        if key == ord("r"):
            # Debounce: if the key repeats very quickly, ignore.
            now = time.perf_counter()
            if (now - last_r_ts) < 0.75:
                continue
            last_r_ts = now

            print(f"\n[emotion={last_emotion}] [persona={persona.display}]")

            # If prosody is enabled with live mic capture, record once to a temp wav.
            audio_wav: Optional[Path] = None
            if str(args.prosody) == "mic":
                stamp2 = time.strftime("%Y%m%d_%H%M%S")
                audio_wav = REPO_ROOT / "outputs" / "tmp" / f"utt_{stamp2}.wav"
                print(f"Recording {float(args.prosody_seconds):.1f}s... (speak now)")
                t_rec0 = time.perf_counter()
                ok_rec = record_mic_to_wav(audio_wav, seconds=float(args.prosody_seconds), sr=16000)
                prosody_record_ms = (time.perf_counter() - t_rec0) * 1000.0
                if not ok_rec:
                    print("[prosody] Mic capture failed or optional deps missing (install sounddevice + soundfile).")
                    audio_wav = None
                else:
                    last_audio_wav = audio_wav
                    t_an0 = time.perf_counter()
                    prosody = analyze_wav(audio_wav)
                    prosody_ms = (time.perf_counter() - t_an0) * 1000.0
                    if prosody is None:
                        print("[prosody] Optional deps missing (install librosa + numpy). Disabling prosody.")
                    elif not prosody.ok:
                        print(f"[prosody] Failed to analyze audio: {prosody.wav_path}. voice_mood=unknown")
                    else:
                        phz = "n/a" if prosody.pitch_hz is None else f"{prosody.pitch_hz:.0f}"
                        print(f"[prosody] voice_mood={prosody.voice_mood} pitch_hz={phz}")

            if str(args.stt) != "azure":
                # Avoid spamming if the user presses/holds 'r'.
                now2 = time.perf_counter()
                if (now2 - last_stt_disabled_ts) >= 2.0:
                    print("STT is disabled. Re-run with: --stt azure\n")
                    last_stt_disabled_ts = now2
                continue

            print("Listening... (STT)")
            stt_ms: Optional[float] = None
            stt_ok: Optional[bool] = None
            t0 = time.perf_counter()
            text = listen_once_azure(language=str(args.stt_lang), audio_wav_path=audio_wav)
            stt_ms = (time.perf_counter() - t0) * 1000.0
            stt_ok = bool(text)
            if not text:
                print("(No speech recognized)\n")
            else:
                print(f"You(STT): {text}\n")
                _handle_user_message(text, input_mode="stt", tsec_now=float(tsec), stt_ms=stt_ms, stt_ok=stt_ok)

    cap.release()
    cv2.destroyAllWindows()
    if cont_stt is not None:
        cont_stt.stop()
    if logger is not None:
        logger.log({"event": "session_end", "time": time.strftime("%Y-%m-%d %H:%M:%S")})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
