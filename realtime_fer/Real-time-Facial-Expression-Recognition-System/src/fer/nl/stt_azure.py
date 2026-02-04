from __future__ import annotations

import os
import queue
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class AzureSpeechSTTConfig:
    key: str
    region: str
    language: str


def load_azure_speech_stt_config(*, language: Optional[str] = None) -> Optional[AzureSpeechSTTConfig]:
    key = (os.getenv("AZURE_SPEECH_KEY") or "").strip()
    region = (os.getenv("AZURE_SPEECH_REGION") or "").strip()
    if not key or not region:
        return None

    lang = (language or os.getenv("AZURE_SPEECH_LANG") or "en-US").strip()
    if not lang:
        lang = "en-US"

    return AzureSpeechSTTConfig(key=key, region=region, language=lang)


def listen_once_azure(*, language: Optional[str] = None, audio_wav_path: Optional[Path] = None) -> Optional[str]:
    """Capture one utterance from the default microphone using Azure Speech-to-Text.

    Returns the recognized text, or None if STT is not configured or fails.
    """
    cfg = load_azure_speech_stt_config(language=language)
    if cfg is None:
        return None

    try:
        import azure.cognitiveservices.speech as speechsdk  # type: ignore
    except Exception:
        return None

    try:
        speech_config = speechsdk.SpeechConfig(subscription=cfg.key, region=cfg.region)
        speech_config.speech_recognition_language = cfg.language

        if audio_wav_path is not None:
            audio_config = speechsdk.audio.AudioConfig(filename=str(audio_wav_path))
        else:
            audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        result = recognizer.recognize_once_async().get()
        if result is None:
            return None

        if getattr(result, "reason", None) == speechsdk.ResultReason.RecognizedSpeech:
            text = (getattr(result, "text", "") or "").strip()
            return text or None

        return None
    except Exception:
        return None


@dataclass(frozen=True)
class ContinuousSTTResult:
    text: str


class AzureContinuousSTT:
    """Continuous Azure Speech STT from default microphone.

    Usage:
      stt = AzureContinuousSTT(language="en-US")
      if stt.start():
          while ...:
              text = stt.poll_text()

    Notes:
    - Designed for demo use.
    - If you are also recording the mic with another library (e.g. sounddevice),
      you may get device contention. Prefer using either continuous STT OR mic-capture prosody.
    """

    def __init__(self, *, language: Optional[str] = None):
        self._language = language
        self._cfg = load_azure_speech_stt_config(language=language)
        self._speechsdk = None
        self._recognizer = None
        self._q: "queue.Queue[str]" = queue.Queue()
        self._running = False
        self._lock = threading.Lock()

    @property
    def is_running(self) -> bool:
        with self._lock:
            return bool(self._running)

    def start(self) -> bool:
        if self._cfg is None:
            return False

        try:
            import azure.cognitiveservices.speech as speechsdk  # type: ignore

            self._speechsdk = speechsdk
        except Exception:
            return False

        try:
            speech_config = self._speechsdk.SpeechConfig(subscription=self._cfg.key, region=self._cfg.region)
            speech_config.speech_recognition_language = self._cfg.language

            audio_config = self._speechsdk.audio.AudioConfig(use_default_microphone=True)
            recognizer = self._speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

            def _on_recognized(evt):
                try:
                    res = getattr(evt, "result", None)
                    if res is None:
                        return
                    if getattr(res, "reason", None) != self._speechsdk.ResultReason.RecognizedSpeech:
                        return
                    text = (getattr(res, "text", "") or "").strip()
                    if not text:
                        return
                    self._q.put(text)
                except Exception:
                    return

            recognizer.recognized.connect(_on_recognized)
            recognizer.start_continuous_recognition_async().get()

            with self._lock:
                self._recognizer = recognizer
                self._running = True
            return True
        except Exception:
            return False

    def stop(self) -> None:
        with self._lock:
            recognizer = self._recognizer
            self._recognizer = None
            self._running = False

        try:
            if recognizer is not None:
                recognizer.stop_continuous_recognition_async().get()
        except Exception:
            return

    def poll_text(self) -> Optional[str]:
        try:
            return self._q.get_nowait()
        except queue.Empty:
            return None
