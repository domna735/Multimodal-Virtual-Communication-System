from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class OpenAIChatConfig:
    api_key: str
    base_url: Optional[str]
    model: str
    timeout_s: float


def load_openai_chat_config() -> Optional[OpenAIChatConfig]:
    api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    if not api_key:
        return None

    base_url = (os.getenv("OPENAI_BASE_URL") or "").strip() or None
    model = (os.getenv("OPENAI_CHAT_MODEL") or "gpt-4o-mini").strip()
    try:
        timeout_s = float(os.getenv("OPENAI_TIMEOUT_S") or "20")
    except Exception:
        timeout_s = 20.0

    return OpenAIChatConfig(api_key=api_key, base_url=base_url, model=model, timeout_s=timeout_s)


def try_generate_reply_openai(
    *,
    user_text: str,
    emotion: str,
    persona_display: str,
    persona_style: str,
) -> Optional[str]:
    cfg = load_openai_chat_config()
    if cfg is None:
        return None

    try:
        from openai import OpenAI  # type: ignore
    except Exception:
        # Dependency not installed.
        return None

    client = OpenAI(api_key=cfg.api_key, base_url=cfg.base_url)

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
            model=cfg.model,
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
