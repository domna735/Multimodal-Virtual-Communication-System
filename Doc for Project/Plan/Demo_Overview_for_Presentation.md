# Demo Overview — Multimodal Virtual Communication System (最簡單可行版)

Use this as a **presentation script** (what you say + what you show).

---

## 0) One-sentence goal (最重要一句)

**「系統睇住你個樣 + 聽你講一句 → 用唔同語氣回應你。」**

(English) *The system watches your face + listens to one utterance, then replies with an appropriate tone and speaks it out.*

---

## 1) What is the MVP doing (pipeline)

**Webcam video** → **FER** (emotion label + confidence) → **Agent** (persona/rules or LLM) → **TTS** (speech output)

Optional voice input mode:

**Microphone** → **STT** (speech-to-text) → (same Agent → TTS)

Planned multimodal add-on (demo-level):

**Audio clip** → **Prosody features (pitch/energy)** → **voice_mood (tired/excited/neutral)** → (Agent uses emotion + voice_mood)

---

## 2) What you have already built (DONE today)

- Real-time FER (webcam + face detection + emotion overlay)
- Persona switching
- Typed chat (`t`) and voice chat (`r` with Azure STT)
- TTS output (Windows; optional Azure Speech)
- JSONL logging + latency summary

---

## 3) Live demo flow (你示範時照住做)

### Step 1 — Show real-time FER
What you do:
- Open the demo
- Show the webcam window

What you say:
- 「左邊係 real-time FER，會輸出 emotion label 同 confidence。」

### Step 2 — Show voice input (real-time talk)
What you do:
- Click the demo window
- Press `r`
- Speak one sentence

What you say:
- 「我撳 `r` 錄一句，Azure STT 會轉做文字，之後系統會回應同讀出嚟。」

### Step 3 — Show persona change
What you do:
- Press `p` to switch persona
- Press `r` again and speak the same sentence

What you say:
- 「Persona 會改變回應風格，但仍然會參考情緒。」

### Step 4 — Show evaluation proof (latency)
What you do:
- End demo
- Run latency summary

What you say:
- 「我有記錄 STT/LLM/TTS latency，方便寫 evaluation。」

---

## 4) Key selling points (你要 highlight)

- **Demo-first**: always runs offline (fallbacks)
- **Real-time**: webcam overlay updates continuously
- **Multimodal roadmap**: already has face + voice (STT), next adds prosody as a second voice feature
- **Measurable**: session logs + latency summary

---

## 5) Limitations (誠實講，反而加分)

- Prosody analysis (pitch/energy → voice_mood) is planned but not yet integrated.
- Current “agent” can be offline rules or optional Azure OpenAI.
- This is a **prototype MVP** (最簡單可行版), not a full research-grade multimodal transformer.

---

## 6) Next step (what we build one-by-one next)

1. Add simple prosody analyzer (librosa) + voice_mood overlay
2. Add fusion rule: emotion + voice_mood → response
3. (Optional) improve expressive TTS controls (speed/pitch/SSML)

---

## 7) Suggested 60–90 sec demo script (短講稿)

- 「呢個係一個最簡單可行嘅 multimodal prototype。」
- 「左邊係 webcam FER，會輸出 emotion label。」
- 「我而家用 voice input（STT）講一句，系統會轉文字，然後根據情緒同 persona 回應，再用 TTS 讀出嚟。」
- 「我亦都有記錄 latency，方便 evaluation。」
- 「下一步會加簡單 prosody 分析（pitch/energy），做更完整嘅 face+voice fusion。」
