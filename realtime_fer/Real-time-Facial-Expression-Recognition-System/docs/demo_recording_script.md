# Locked Demo Script (Recording)

Goal: record a stable 1–3 minute demo that shows **FER → persona reply → TTS**.

## Setup

- Run the demo first in offline mode to confirm camera + FER are stable.
- For the recorded version, enable Azure OpenAI + Azure Speech (optional).

Recommended run (Azure-first):
```powershell
.\.venv\Scripts\python.exe demo\mvp_demo.py --device dml --detector yunet --speak --llm azure-openai --tts azure
```

Controls reminder:
- `p`: cycle persona
- `t`: type in console
- `s`: toggle speech
- `q`: quit

## Recording structure (3 personas × 3 emotions × 3 prompts)

Record 3 short segments (about 30–45s each). For each segment:
1) Switch persona (`p`) until it matches
2) Act the target facial emotion for ~2 seconds until the overlay stabilizes
3) Press `t`, enter the prompt, let it respond and speak

### Segment A — Calm Companion

Target emotions to demonstrate: **Neutral → Happy → Sad**

Prompts:
1) (Neutral) "Hi. I just want to talk for a minute."
2) (Happy) "Something good happened today. Can you celebrate with me?"
3) (Sad) "I feel a bit overwhelmed. Can you help me calm down?"

### Segment B — Supportive Mentor

Target emotions to demonstrate: **Neutral → Surprise → Fear**

Prompts:
1) (Neutral) "I want to improve my daily routine. What’s one small step I can take?"
2) (Surprise) "I suddenly got an unexpected task deadline. What should I do first?"
3) (Fear) "I’m worried I will fail this project. How do I reduce the risk?"

### Segment C — Technical Advisor

Target emotions to demonstrate: **Neutral → Anger → Disgust**

Prompts:
1) (Neutral) "Help me plan the next engineering task for this MVP."
2) (Anger) "Nothing is working and I’m stuck. What should I check first?"
3) (Disgust) "The output quality is unacceptable. What’s the fastest fix path?"

## Tips for stability

- Keep lighting consistent; face detector stability matters.
- Keep your face centered and avoid fast motion.
- If emotion flickers, hold the expression for a few seconds (smoothing needs time).

## What to show on screen

- Emotion label + confidence
- Persona name
- LLM backend + TTS backend
- Speech on/off

## What to capture for evaluation notes

- JSONL logs are written to `outputs/sessions/`.
- Look for `event=latency` lines to summarize:
  - `llm_ms` (LLM response latency)
  - `tts_ms` (speech synthesis/playback latency)
  - `used_llm_fallback`, `used_tts_fallback`
