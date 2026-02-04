
# Demo Checklist — Multimodal Virtual Communication System (MVP)

**Source docs used:**
- `Doc for Project/Plan/Plan.md` (demo-first MVP scope + status)
- `Doc for Project/PROPOSAL OF PERSONAL PROJECT MULTIMODAL VIRTUAL COMMUNICATE SYSTEM.md` (overall research roadmap)

**Goal right now:** finish a stable **demo** that clearly shows **multimodal interaction**:

**Webcam (FER) + Voice (STT + simple prosody) + Dialogue + TTS + Logging**

---

## 0) Demo “Definition of Done” (what you must show)

- [x] done — **One command to run** (PowerShell) exists: `run_mvp.ps1`
- [ ] **Live FER** visible on webcam overlay (emotion + confidence)
- [ ] **Interaction works**
	- [ ] typed input works (press `t`)
	- [ ] voice input works (push-to-talk: press `r`, speak once)
	- [ ] voice input works (hands-free: continuous STT)
- [ ] **Multimodal evidence** in the UI overlay
	- [ ] `emotion=...` from face
	- [ ] `voice_mood=...` from mic prosody (demo-level)
- [ ] **System replies** (persona-aware) and **speaks** reply (TTS)
- [ ] **Session logs saved** (JSONL) with latency fields
- [ ] **A 1–3 minute demo video recorded** (screen + audio) with a clear script

---

## 1) Environment & Setup (Windows)

### 1.1 Repo / working folder
- [x] done — Repo exists: `realtime_fer/Real-time-Facial-Expression-Recognition-System`
- [x] done — Stable entrypoint exists: `run_mvp.ps1`

### 1.2 Python + venv
- [x] done — Repo-local venv path planned: `.venv\Scripts\python.exe`
- [x] Confirm Python version is **3.11** for this repo venv (avoid 3.14) (verified: 3.11.9)
	- Evidence: `.\.venv\Scripts\python.exe --version`

### 1.3 Base dependencies (demo must run)
- [ ] Install base deps (DirectML / base demo): `-r requirements-directml.txt` (if using `-Device dml`)
- [ ] Verify webcam opens + UI renders without crashes (run 2–5 minutes)

### 1.4 Optional dependencies (only if using online / prosody features)
- [ ] Online backends installed (Azure Speech + Azure OpenAI): `-r requirements-online.txt`
- [ ] Prosody deps installed (mic capture + analysis): `-r requirements-prosody.txt`

### 1.5 Secrets / .env (online mode only)
- [ ] `.env` created in repo root (DO NOT COMMIT)
- [ ] Azure OpenAI vars set (for `--llm azure-openai`)
	- [ ] `AZURE_OPENAI_API_KEY`
	- [ ] `AZURE_OPENAI_ENDPOINT`
	- [ ] `AZURE_OPENAI_DEPLOYMENT`
- [ ] Azure Speech vars set (for `--tts azure` / `--stt azure`)
	- [ ] `AZURE_SPEECH_KEY`
	- [ ] `AZURE_SPEECH_REGION`

---

## 2) Real-time FER Module (must for demo)

### 2.1 Camera + face detection
- [x] done — Webcam capture path exists in MVP demo
- [x] done — Face detector supported (YuNet)
- [ ] Confirm correct camera opens on your laptop/PC (if multiple cameras)

### 2.2 FER inference
- [x] done — FER model loads successfully (student checkpoint / ONNX)
- [x] done — Emotion label + confidence computed
- [x] done — Smoothing is present (EMA/hysteresis/vote) per Plan

### 2.3 UI overlay
- [x] done — Overlay shows emotion + confidence
- [ ] Ensure overlay text is readable in screen recording (font size, contrast)

---

## 3) Dialogue / Persona Module (demo-level)

### 3.1 Persona selection
- [x] done — Persona selection exists (demo-level)
- [ ] Prepare 2–3 personas to demonstrate consistency (e.g., Friendly, Professional, Funny)

### 3.2 Offline rule-based baseline (must always work)
- [x] done — Offline replies available (fallback)
- [x] done — Replies can condition on emotion + persona

### 3.3 Optional: Azure OpenAI LLM mode
- [x] done — Azure OpenAI backend integrated (optional)
- [ ] Verify LLM actually responds under your network + key
- [ ] Confirm fallback triggers cleanly if API fails (no crash)
- [ ] For demo: decide which mode you will present
	- [ ] Option A (safer): `--llm offline`
	- [ ] Option B (better quality): `--llm azure-openai`

---

## 4) TTS Output (must for demo)

### 4.1 Baseline Windows TTS
- [x] done — Windows TTS exists (System.Speech)
- [ ] Verify audio output device is correct (headphones/speakers)

### 4.2 Optional: Azure Speech TTS
- [x] done — Azure Speech TTS integrated (optional)
- [ ] Verify Azure TTS speaks successfully (keys, region)
- [ ] Decide demo default
	- [ ] Safer: Windows TTS
	- [ ] Better voice: Azure TTS

---

## 5) Voice Input (STT) (strongly recommended for demo)

### 5.1 Hotkey workflow
- [x] done — Hotkey `r` exists to capture one utterance
- [x] done — STT latency is logged

### 5.3 Hands-free workflow (continuous STT)
- [x] done — Continuous Azure STT mode implemented (`--stt-mode continuous` / `-SttMode continuous`)
- [ ] Verify continuous STT works well on this machine (mic permissions, echo, stability)

### 5.2 Azure Speech STT
- [x] done — Azure STT integrated (optional)
- [ ] Verify microphone permissions and input level
- [ ] Verify `--stt-lang` works (e.g., `en-US`)
- [ ] Verify STT transcript appears and drives response

---

## 6) Prosody / Voice Mood (demo-level multimodal proof)

### 6.1 Prosody approach (per Plan: Decision B)
- [x] done — Implemented: **live mic capture** → save temp wav → analyze pitch/energy
- [x] done — Implemented: reuse the same wav for STT + prosody (one press = one utterance)

### 6.2 Dependencies
- [ ] Install prosody deps:
	- [ ] `librosa`
	- [ ] `soundfile`
	- [ ] `sounddevice`
	- [ ] `numpy`

### 6.3 Output + mapping
- [x] done — `voice_mood` label exists (demo heuristic)
- [ ] Confirm `voice_mood` changes when you speak differently (calm vs excited)
- [ ] Confirm overlay shows `voice_mood` clearly

### 6.4 Simple fusion (face emotion + voice mood)
- [x] done — Demo-level fusion heuristic exists (response influenced by both)
- [ ] Prepare 2–3 scripted examples to show fusion
	- [ ] Example: face=Sad + voice=tense → comforting response
	- [ ] Example: face=Happy + voice=excited → energetic response

---

## 7) Logging & Evaluation (must for demo credibility)

### 7.1 Session logging
- [x] done — JSONL session logs exist under `outputs/sessions/`
- [x] done — Logs include latency events (stt/llm/tts)
- [ ] Confirm logs are created every run (even if online services fail)

### 7.2 Latency summarizer
- [x] done — `run_latency.ps1` exists
- [ ] After a demo run, generate a latency summary
	- [ ] baseline summary
	- [ ] by-backend summary (if you used online services)

---

## 8) Demo Script (what you will say + do)

### 8.1 Prepare a short scenario (recommended)
- [ ] 30s: introduce modules (FER + voice + persona)
- [ ] 60–90s: 2 interactions using voice (press `r`)
- [ ] 30s: switch persona and show different style
- [ ] 30s: show latency summary or show the log file exists

### 8.2 “No-fail” fallback plan (for live presentation)
- [ ] If internet fails → switch to offline:
	- [ ] `--llm offline`
	- [ ] `--tts windows`
	- [ ] keep `--stt off` and use typed input
- [ ] If mic fails → typed input still works (`t`)

---

## 9) Record the Demo Video (deliverable)

### 9.1 Recording setup
- [ ] Use OBS (recommended) or Windows Game Bar
- [ ] Capture: screen + system audio + mic (if needed)
- [ ] Check levels: no clipping, clear TTS audio

### 9.2 Video requirements
- [ ] 1–3 minutes total
- [ ] Shows the UI overlay clearly
- [ ] Shows at least 2 voice interactions
- [ ] Shows at least 2 different emotions or 2 different personas

### 9.3 Archive artifacts
- [ ] Save 1 example session log `.jsonl`
- [ ] Save latency summary output
- [ ] Note which command line you used (copy into your process log)

---

## 10) Research Roadmap Alignment (proposal vs demo)

This section is to track what’s *required by the proposal* vs what’s *already covered by the demo MVP*.

### 10.1 Proposal modules (high-level)
- [x] FER emotion analysis module (demo-level)
- [ ] Robust FER training + KD/DKD + stress testing report (research deliverable; not needed to finish demo)
- [ ] Voiceprint / speaker embedding (research; not in MVP)
- [x] Prosody (demo-level pitch/energy)
- [x] Speech generation (TTS via Windows/Azure; demo-level)
- [ ] Expressive TTS with timbre/prosody factorization (research; not required for demo)
- [x] Persona-conditioned dialogue (demo-level; offline rules + optional LLM)
- [ ] Personality reconstruction (research-level; out of MVP scope)
- [ ] Transformer-based multimodal fusion (research-level; MVP uses simple heuristics)

---

## 11) Recommended “Finish Demo” Run Commands (PowerShell)

Run from:
`C:\Multimodal Virtual Communication System\realtime_fer\Real-time-Facial-Expression-Recognition-System`

### 11.1 Install (only once per venv)
```powershell
Set-Location "C:\Multimodal Virtual Communication System\realtime_fer\Real-time-Facial-Expression-Recognition-System"

.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-directml.txt

# Optional (online LLM/TTS/STT)
.\.venv\Scripts\python.exe -m pip install -r requirements-online.txt

# Optional (prosody mic capture)
.\.venv\Scripts\python.exe -m pip install -r requirements-prosody.txt
```

### 11.2 Run (recommended demo mode: multimodal proof)
```powershell
.\run_mvp.ps1 -Device dml -Detector yunet -Speak -Stt azure -SttMode push -SttLang en-US -Prosody mic -ProsodySeconds 3.0
```

### 11.3 Run (recommended demo mode: hands-free conversation)
```powershell
.\run_mvp.ps1 -Device dml -Detector yunet -Speak -Stt azure -SttMode continuous -SttLang en-US -Prosody off -Llm azure-openai -Tts azure
```

If online services are not ready, use safe offline mode:
```powershell
.\run_mvp.ps1 -Device dml -Detector yunet -Speak -Llm offline -Tts windows -Stt off -Prosody off
```

