# Process Log - Week 5 of January 2026
This document captures the daily activities, decisions, and reflections during the fifth week of January 2026, focusing on reconstructing the facial expression recognition system as per the established plan.

---

## 2026-01-25 | Online API integration (Azure-first)

Intent:
- Continue the MVP plan by upgrading the demo to support **online LLM** and **online TTS** while keeping an offline fallback.
- Prefer an **Azure-first stack** for simplicity: Azure OpenAI (LLM) + Azure Speech (TTS).

Actions:
- Updated the project plan to explicitly include optional online backends and key management:
	- LLM: Azure OpenAI (preferred) / OpenAI (optional)
	- TTS: Azure Speech (optional) with Windows TTS fallback
- Implemented API-ready backends in the real-time demo repo:
	- Added `requirements-online.txt` for optional dependencies
	- Added `.env.example` and `.env` loading for local secret configuration
	- Added `--llm offline|openai|azure-openai` and `--tts windows|azure` flags in the MVP demo
	- Ensured graceful fallback: if API is not configured or fails, the demo continues using offline replies / Windows TTS

Result:
- The MVP demo remains runnable with the original offline behavior.
- The project now has a clear “one-by-one” setup path to enable:
	1) Online LLM replies (Azure OpenAI)
	2) Online TTS speech output (Azure Speech)

Next steps (immediate):
- Create Azure OpenAI deployment + Azure Speech resource.
- Fill `.env` values locally and test:
	- `--llm azure-openai`
	- `--tts azure`
- Add a short scripted demo scenario (3 personas × 2–3 emotions) for recording.

---

## 2026-01-25 | Recording-ready demo + latency evaluation

Intent:
- Make the MVP demo easier to record and easier to evaluate (latency + fallback behavior), while keeping offline-first reliability.

Actions:
- Added per-turn latency logging in the MVP demo JSONL logs:
	- `llm_ms` (time to get a reply)
	- `tts_ms` + `tts_ok` (time/success for speech output)
	- `used_llm_fallback` / `used_tts_fallback`
- Added a small latency summarizer script for the report evaluation section:
	- `tools/diagnostics/summarize_session_latency.py`
- Updated MVP playbook with the correct PowerShell commands to run the summarizer.

Notes:

- On Windows PowerShell, use a real Python path like `.\.venv\Scripts\python.exe` (not `.python.exe`).
	Example:
	- `.\.venv\Scripts\python.exe tools\diagnostics\summarize_session_latency.py --by-backend`

Next steps (immediate):
- Run the MVP once to produce `outputs/sessions/mvp_<timestamp>.jsonl`, then run the summarizer and paste the output into the evaluation notes.

---

## 2026-01-25 | Voice chat (STT) for “real-time talk”

Intent:
- Upgrade the MVP from typed chat (press `t`) to **voice input** (press `r`, speak once) using an **online STT API**.
- Keep the MVP reliable: voice is optional; typed chat remains available as a fallback.

Actions:
- Added Azure Speech-to-Text (STT) module:
	- `src/fer/nl/stt_azure.py`
- Upgraded the MVP demo to support voice input:
	- New flags: `--stt off|azure` and `--stt-lang en-US`
	- New hotkey: `r` = record one utterance from the microphone, then generate reply and speak it
	- Added STT timing fields into the JSONL latency events:
		- `stt_ms`, `stt_ok`, `stt_backend`, `stt_lang`, `input_mode`
- Updated the helper run script to pass STT options:
	- `run_mvp.ps1 -Stt azure -SttLang en-US`
- Updated the latency summarizer to report STT latency when present.

Notes:
- STT requires the optional online deps:
	- `requirements-online.txt` (Azure Speech SDK)
- STT uses the same Azure Speech credentials as TTS:
	- `AZURE_SPEECH_KEY` + `AZURE_SPEECH_REGION`
	- Optional: `AZURE_SPEECH_LANG` (or pass `--stt-lang`)

Run commands (PowerShell):
```powershell
Set-Location "C:\Multimodal Virtual Communication System\realtime_fer\Real-time-Facial-Expression-Recognition-System"
.\run_mvp.ps1 -Device dml -Detector yunet -Speak -Stt azure -SttLang en-US
```

Next steps (immediate):
- Record a short demo video showing:
	- (1) emotion overlay changing,
	- (2) voice input (press `r` and speak),
	- (3) persona reply + TTS output.
- Re-run the latency summarizer and paste STT/LLM/TTS numbers into evaluation notes.

---

## 2026-01-25 | Prosody (voice mood) demo — decision A: pre-recorded .wav

Intent:
- Complete the “simplest multimodal demo” checklist step for **voice prosody / voice mood**, while keeping the demo reliable.
- Use **(A) a pre-recorded `.wav` file** first (instead of live mic audio capture) to reduce risk and simplify recording.

Actions:
- Added a lightweight prosody analyzer module (demo-level):
	- `src/fer/nl/prosody.py`
	- Extracts simple pitch/energy features and classifies a coarse `voice_mood` (e.g., calm/excited/tense/sad).
- Upgraded the MVP demo to optionally load/analyze a pre-recorded `.wav` and surface the result:
	- New flags: `--prosody off|wav` and `--prosody-wav <path>`
	- UI overlay shows `voice_mood` + pitch estimate
	- JSONL logs include: `voice_mood`, `voice_pitch_hz`, `voice_rms`, `prosody_backend`, `prosody_wav`, `prosody_ms`
	- Added a small demo-level fusion heuristic: when face is Neutral but voice mood is strong, the reply can be nudged.
- Added an optional dependency file:
	- `requirements-prosody.txt` (librosa + soundfile)
- Updated the PowerShell launcher to support prosody args:
	- `run_mvp.ps1 -Prosody wav -ProsodyWav <path>`

Notes:
- Prosody is optional and should never break the demo.
	- If optional deps are missing, the demo prints a message and continues without prosody.
- This is a demo-ready baseline; later we can improve thresholds, add live mic capture, and fuse more systematically.

Run commands (PowerShell):
```powershell
Set-Location "C:\Multimodal Virtual Communication System\realtime_fer\Real-time-Facial-Expression-Recognition-System"
.
\.venv\Scripts\python.exe -m pip install -r requirements-prosody.txt

# Example: run MVP with wav prosody + speak
.\run_mvp.ps1 -Device dml -Detector yunet -Speak -Prosody wav -ProsodyWav "C:\path\to\demo_voice.wav"
```

Next steps (immediate):
- Pick 1–2 short `.wav` clips that clearly represent different moods (calm vs excited/tense) for the recorded demo.
- Record a demo segment showing:
	- (1) face emotion overlay,
	- (2) `voice_mood` overlay from the `.wav`,
	- (3) persona reply + TTS output.

---

## 2026-01-25 | Prosody (voice mood) demo — switch to decision B: live microphone capture

Intent:
- Make the prosody part feel more “real-time” by switching to **(B) microphone live capture**.
- Reduce operator steps by capturing **one utterance** and reusing that same audio for:
	- (1) prosody analysis (voice mood)
	- (2) speech-to-text (STT) transcript (Azure)

Actions:
- Implemented live mic capture for prosody:
	- `--prosody mic` records ~N seconds to a temp `.wav` using `sounddevice` + `soundfile`.
	- Prosody analysis runs on that captured audio and updates the UI overlay + logs.
- Updated Azure STT wrapper to optionally accept a `.wav` file as input.
	- This lets the MVP use the *same* recorded utterance for both prosody + STT.
- Updated the PowerShell launcher to support:
	- `-Prosody mic` and `-ProsodySeconds 3.0`

Notes:
- This is slightly more setup than a pre-recorded `.wav` (requires mic device + optional deps), but produces a more convincing live demo.

Run commands (PowerShell):
```powershell
Set-Location "C:\Multimodal Virtual Communication System\realtime_fer\Real-time-Facial-Expression-Recognition-System"

# Install prosody mic deps (optional)
.\.venv\Scripts\python.exe -m pip install -r requirements-prosody.txt

# Live mic prosody + Azure STT + TTS
.\run_mvp.ps1 -Device dml -Detector yunet -Speak -Stt azure -SttLang en-US -Prosody mic -ProsodySeconds 3.0
```

Next steps (immediate):
- Do a quick mic sanity check (volume / device selection) and record a short demo clip.
- For the recorded demo, use the flow:
	- press `r` → speak one utterance → see `voice_mood` overlay + get reply + TTS.