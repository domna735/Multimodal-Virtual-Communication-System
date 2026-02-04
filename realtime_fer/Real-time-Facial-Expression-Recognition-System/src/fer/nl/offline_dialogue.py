from __future__ import annotations

import re
import zlib
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class OfflinePersona:
    key: str
    display: str


_RE_WS = re.compile(r"\s+")


def _norm(text: str) -> str:
    t = (text or "").strip().lower()
    t = _RE_WS.sub(" ", t)
    return t


def _pick_variant(*, key: str, n: int) -> int:
    if n <= 1:
        return 0
    v = zlib.adler32(key.encode("utf-8"))
    return int(v % n)


def _detect_self_reported_emotion(text: str) -> Optional[str]:
    t = _norm(text)

    # Common informal patterns.
    # Keep it simple and robust to imperfect grammar.
    patterns = [
        ("happy", ["i am happy", "i'm happy", "im happy", "feel happy", "feeling happy"]),
        ("sad", ["i am sad", "i'm sad", "im sad", "feel sad", "feeling sad", "i full sad", "so sad"]),
        ("angry", ["i am angry", "i'm angry", "im angry", "mad", "so angry", "annoyed", "frustrated"]),
        ("fear", ["i am scared", "i'm scared", "im scared", "afraid", "anxious", "nervous", "worried"]),
        ("disgust", ["disgust", "gross", "sick of", "nausea", "nauseous"]),
        ("surprise", ["surprised", "shocked", "unexpected"]),
        ("tired", ["tired", "exhausted", "sleepy"]),
    ]

    for emo, keys in patterns:
        for k in keys:
            if k in t:
                return emo

    # Also catch "I feel X" / "feel X" single-word endings.
    m = re.search(r"\b(feel|feeling)\s+(happy|sad|angry|mad|anxious|nervous|worried|scared|afraid|surprised|tired)\b", t)
    if m:
        word = m.group(2)
        return {
            "mad": "angry",
            "anxious": "fear",
            "nervous": "fear",
            "worried": "fear",
            "scared": "fear",
            "afraid": "fear",
        }.get(word, word)

    return None


def _detect_intent(text: str) -> str:
    t = _norm(text)

    if not t:
        return "empty"

    if any(w in t for w in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]):
        return "greeting"

    if any(w in t for w in ["how to", "how do i", "help", "improve", "fix", "solve", "advice", "suggest"]):
        return "ask_help"

    if any(w in t for w in ["thank", "thanks", "thx"]):
        return "thanks"

    if any(w in t for w in ["why", "what", "when", "where", "who"]):
        return "question"

    return "statement"


def _choose_effective_emotion(*, detected_emotion: str, confidence: float, self_reported: Optional[str]) -> str:
    # If user explicitly says how they feel, prefer that.
    if self_reported:
        return self_reported

    e = (detected_emotion or "neutral").strip().lower()
    conf = float(confidence)
    if conf < 0.55:
        return "neutral"
    return e


def generate_offline_reply(
    *,
    user_text: str,
    detected_emotion: str,
    confidence: float,
    persona: OfflinePersona,
    previous_reply: Optional[str] = None,
) -> str:
    """Offline reply generator for the MVP.

    Goals:
    - react to user text (not only FER)
    - keep responses short (1-3 sentences)
    - persona-dependent style
    - avoid repeating the exact same reply when possible
    """

    text = (user_text or "").strip()
    tnorm = _norm(text)
    intent = _detect_intent(text)
    self_emo = _detect_self_reported_emotion(text)
    emo = _choose_effective_emotion(
        detected_emotion=detected_emotion,
        confidence=confidence,
        self_reported=self_emo,
    )

    # A couple of common special cases.
    if intent == "greeting":
        options = [
            f"Hi — I’m here with you. What would you like to talk about?",
            f"Hello. What’s going on for you right now?",
            f"Hey. How are you feeling today?",
        ]
        idx = _pick_variant(key=tnorm + persona.key, n=len(options))
        return options[idx]

    if intent == "thanks":
        options = [
            "You’re welcome. Want to continue?",
            "No problem. What’s the next thing you want to try?",
        ]
        idx = _pick_variant(key=tnorm + persona.key, n=len(options))
        return options[idx]

    # Persona-specific templates.
    if persona.key == "technical_advisor":
        if intent in {"ask_help", "question"}:
            options = [
                "Give me: (1) goal, (2) current state, (3) what you tried, (4) what failed.",
                "What’s the exact target outcome, and what constraint matters most (time, cost, accuracy)?",
            ]
        elif emo in {"sad", "fear", "angry", "disgust", "tired"}:
            options = [
                f"Noted ({emo}). Let’s reduce uncertainty: what’s the one smallest next action you can do in 5 minutes?",
                f"Noted ({emo}). What would a ‘better’ outcome look like, specifically?",
            ]
        else:
            options = [
                "Understood. What do you want to achieve next?",
                "Ok. What’s the most important constraint?",
            ]

    elif persona.key == "supportive_mentor":
        if "improve" in tnorm and "happy" in tnorm:
            options = [
                "If you want more happiness: try one small activity that gives you energy, then one that gives you meaning. Which one fits today?",
                "Happiness is easier to build with small habits: sleep, movement, and one social connection. Which is easiest to start now?",
            ]
        elif emo == "sad":
            options = [
                "I’m with you. What’s one thing that’s been weighing on you most today?",
                "That sounds heavy. Do you want comfort, advice, or just someone to listen?",
            ]
        elif emo == "fear":
            options = [
                "It’s okay to feel nervous. What’s the worst-case you’re imagining, and how likely is it really?",
                "Let’s make it safer: what’s the next step with the lowest risk?",
            ]
        elif emo == "angry":
            options = [
                "That sounds frustrating. What part is unfair or out of your control?",
                "Let’s slow down. What happened right before you started feeling this way?",
            ]
        else:
            options = [
                "Tell me what’s going on, and what outcome you want.",
                "What’s the main thing you want help with right now?",
            ]

    else:
        # calm_companion
        if emo == "sad":
            options = [
                "I’m here. Want to tell me what happened?",
                "I’m listening. What’s making you feel sad?",
            ]
        elif emo == "disgust":
            options = [
                "I can see discomfort. What’s feeling unpleasant right now?",
                "Something feels off. What part is bothering you most?",
            ]
        elif emo == "angry":
            options = [
                "You look tense. Want to say what’s bothering you most?",
                "Let’s take one breath. What’s the biggest stress right now?",
            ]
        elif emo == "fear":
            options = [
                "You seem worried. What are you afraid might happen?",
                "It’s okay. What would help you feel safer right now?",
            ]
        elif emo == "happy":
            options = [
                "You look happier. Want to share what’s going well?",
                "Nice. What’s been good today?",
            ]
        elif emo == "tired":
            options = [
                "You sound tired. Do you want to rest, or talk it out for a minute?",
                "If you’re exhausted, we can keep it simple. What’s the one thing you need most right now?",
            ]
        else:
            options = [
                "I’m here. What would you like to talk about?",
                "Tell me what’s on your mind.",
            ]

    idx = _pick_variant(key=tnorm + persona.key + emo + intent, n=len(options))
    reply = options[idx]

    # Avoid repeating exactly the same sentence if we can.
    if previous_reply and reply.strip() == previous_reply.strip() and len(options) > 1:
        reply = options[(idx + 1) % len(options)]

    return reply
