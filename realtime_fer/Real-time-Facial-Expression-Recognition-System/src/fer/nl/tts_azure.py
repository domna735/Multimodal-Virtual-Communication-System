from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AzureSpeechConfig:
    key: str
    region: str
    voice: str


def load_azure_speech_config() -> Optional[AzureSpeechConfig]:
    key = (os.getenv("AZURE_SPEECH_KEY") or "").strip()
    region = (os.getenv("AZURE_SPEECH_REGION") or "").strip()
    if not key or not region:
        return None

    voice = (os.getenv("AZURE_SPEECH_VOICE") or "en-US-JennyNeural").strip()
    return AzureSpeechConfig(key=key, region=region, voice=voice)


def speak_azure(text: str) -> bool:
    """Speak via Azure Cognitive Services Speech.

    Returns True if speech was attempted successfully.
    """
    t = (text or "").strip()
    if not t:
        return False

    cfg = load_azure_speech_config()
    if cfg is None:
        return False

    try:
        import azure.cognitiveservices.speech as speechsdk  # type: ignore
    except Exception:
        return False

    try:
        speech_config = speechsdk.SpeechConfig(subscription=cfg.key, region=cfg.region)
        speech_config.speech_synthesis_voice_name = cfg.voice
        audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        result = synthesizer.speak_text_async(t).get()
        return result is not None
    except Exception:
        return False
