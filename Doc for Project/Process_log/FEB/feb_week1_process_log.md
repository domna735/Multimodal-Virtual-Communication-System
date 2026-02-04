# Process Log — Feb Week 1 (2026)

This log captures the work done in the first week of February 2026 for the demo-first MVP of the **Multimodal Virtual Communication System**.

## Summary (What we built / changed)
- Added **hands-free voice conversation** support via **continuous Azure STT** (no need to press `r` each time).
- Added a safeguard to reduce echo/feedback: **pause STT while TTS is speaking**, then resume.
- Exposed continuous mode via CLI (`--stt-mode`) and PowerShell wrapper (`-SttMode`).
- Renamed the demo repo folder to a cleaner name (removed `_v2_restart`) and updated docs/process logs that referenced the old path.

## Work Notes (chronological)

### 2026-02-04 — Continuous STT + Repo rename

**Goal:** Make the demo feel more like “talking with a real person” (continuous listening → response → TTS), and clean up the repo folder name.

**Implemented: continuous STT mode**
- Added an Azure continuous STT helper class (`AzureContinuousSTT`) that collects recognized utterances in a thread-safe queue.
- Wired it into the MVP loop so recognized phrases trigger the same response pipeline as typed/STT push-to-talk input.
- Added **auto pause/resume** around TTS playback to reduce the system transcribing its own voice.

**CLI / scripts updated**
- New flag: `--stt-mode push|continuous` in the MVP demo.
- PowerShell wrapper supports: `-SttMode push|continuous`.

**Repo folder rename (safety + cleanup)**
- Renamed:
	- From: `realtime_fer/Real-time-Facial-Expression-Recognition-System_v2_restart`
	- To: `realtime_fer/Real-time-Facial-Expression-Recognition-System`
- Updated docs/process logs/checklist references to the old folder name so PowerShell commands still copy/paste correctly.

### 2026-02-04 — Offline chat quality issue (repetitive replies)

**Observed behavior (baseline run):**
- When running with `-Llm offline`, typed messages with different meaning (e.g., `hi`, `how to improve happy`, `i full sad`) could produce the **same reply repeatedly** if the FER label stayed constant (e.g., `Disgust`).

**Root cause:**
- The offline reply generator relied mostly on the detected FER emotion and did not sufficiently use the **user text intent** or **self-reported emotion**.

**Fix / improvement:**
- Updated the offline dialogue logic so it uses:
	- user intent (greeting / ask help / statement)
	- self-reported emotion in text (e.g., “I’m sad”) when present
	- FER emotion as a gentle tone hint (trusted only when confidence is reasonable)
- Added lightweight variation and repetition avoidance so consecutive replies are less likely to be identical.

**Additional UX tweak:**
- Reduced “STT is disabled” spam when pressing/holding `r` by adding a small debounce/cooldown.

### Optional: “free” online LLM via OpenAI-compatible local servers

To enable LLM replies without paid cloud API, the MVP supports OpenAI-compatible local endpoints (e.g., LM Studio / Ollama OpenAI server):

- Set `OPENAI_BASE_URL` to your local server URL.
- `OPENAI_API_KEY` can be empty for local servers (the code uses a dummy key internally).
- Run with `-Llm openai`.

## Key Decisions / Constraints
- **Mic contention constraint:** continuous STT and live mic-capture prosody both use the microphone and may conflict.
	- For “hands-free talk” demos: prefer `--prosody off` (or `--prosody wav`).
	- For “voice mood” multimodal proof: prefer `--stt-mode push` + `--prosody mic`.

## Commands used (examples)

**Hands-free conversation (recommended for natural talk):**
```powershell
Set-Location "C:\Multimodal Virtual Communication System\realtime_fer\Real-time-Facial-Expression-Recognition-System"
.\run_mvp.ps1 -Device dml -Detector yunet -Speak -Stt azure -SttMode continuous -SttLang en-US -Prosody off -Llm azure-openai -Tts azure
```

**Multimodal voice mood proof (push-to-talk + mic prosody):**
```powershell
.\run_mvp.ps1 -Device dml -Detector yunet -Speak -Stt azure -SttMode push -SttLang en-US -Prosody mic -ProsodySeconds 3.0
```

## Next Steps
- Verify end-to-end continuous STT on the target machine (mic permissions, recognition stability, latency).
- Decide the demo mode to present:
	- Mode A: continuous STT (best “real person talk”) + prosody off
	- Mode B: push-to-talk + prosody mic (best “multimodal proof”) 
- Update demo script + record 1–3 minute video.