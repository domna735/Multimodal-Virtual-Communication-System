from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AzureOpenAIChatConfig:
    api_key: str
    endpoint: str
    deployment: str
    api_version: str
    timeout_s: float


def load_azure_openai_chat_config() -> Optional[AzureOpenAIChatConfig]:
    api_key = (os.getenv("AZURE_OPENAI_API_KEY") or "").strip()
    endpoint = (os.getenv("AZURE_OPENAI_ENDPOINT") or "").strip()
    deployment = (os.getenv("AZURE_OPENAI_DEPLOYMENT") or "").strip()

    if not api_key or not endpoint or not deployment:
        return None

    api_version = (os.getenv("AZURE_OPENAI_API_VERSION") or "2024-02-15-preview").strip()
    try:
        timeout_s = float(os.getenv("AZURE_OPENAI_TIMEOUT_S") or "20")
    except Exception:
        timeout_s = 20.0

    return AzureOpenAIChatConfig(
        api_key=api_key,
        endpoint=endpoint,
        deployment=deployment,
        api_version=api_version,
        timeout_s=timeout_s,
    )


def try_generate_reply_azure_openai(
    *,
    user_text: str,
    emotion: str,
    persona_display: str,
    persona_style: str,
) -> Optional[str]:
    cfg = load_azure_openai_chat_config()
    if cfg is None:
        return None

    try:
        from openai import AzureOpenAI  # type: ignore
    except Exception:
        return None

    client = AzureOpenAI(
        api_key=cfg.api_key,
        azure_endpoint=cfg.endpoint,
        api_version=cfg.api_version,
    )

    system = (
        "You are a persona-conditioned dialogue agent for a live demo. "
        "Keep responses short (1-3 sentences), friendly, and safe. "
        "Do not ask for private data. Do not mention policies."
    )

    prompt = (
        f"Persona name: {persona_display}\n"
        f"Persona style: {persona_style}\n"
        f"Detected facial emotion: {emotion}\n"
        "Task: Reply to the user in the persona style. "
        "Reflect the emotion gently in tone, but do not over-assume.\n\n"
        f"User: {user_text.strip()}"
    )

    try:
        resp = client.chat.completions.create(
            model=cfg.deployment,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=120,
            timeout=cfg.timeout_s,
        )
        text = (resp.choices[0].message.content or "").strip()
        return text or None
    except Exception:
        return None
