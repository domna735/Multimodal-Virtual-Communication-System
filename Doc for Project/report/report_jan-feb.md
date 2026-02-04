
# System Process Report (Jan–Feb 2026) — Multimodal Virtual Communication System (Demo-first MVP)

**Author:** Ma Kai Lun Donovan  
**Institution:** The Hong Kong Polytechnic University  
**Report period:** 2026-01-19 → 2026-02-04  
**Primary demo repo:** `realtime_fer/Real-time-Facial-Expression-Recognition-System/`

---

## Abstract

This report documents the development process and current state of the **demo-first MVP** for the *Multimodal Virtual Communication System* during late January to early February 2026. While the long-term proposal targets robust multi-stage research (FER robustness, acoustic-phonological modeling, expressive TTS, persona reconstruction, and multimodal fusion), the work in this period prioritizes a **stable, demonstrable end-to-end prototype**: **webcam-based facial emotion recognition → persona-aware dialogue → speech output**, with optional voice input and prosody.

Key contributions in this period include: (i) selecting a Windows-friendly real-time FER baseline and consolidating the MVP inside a single runnable repository; (ii) implementing offline-first dialogue with optional Azure/OpenAI backends; (iii) adding Windows TTS with optional Azure Speech TTS; (iv) adding Azure Speech STT in both push-to-talk and hands-free continuous modes; (v) implementing simple prosody analysis (pitch/energy → `voice_mood`) with both `.wav` and live microphone capture; and (vi) implementing JSONL session logging and latency summarization utilities to support evaluation and reporting.

The immediate next milestone is to **run and validate the baseline MVP end-to-end**, then **enable hands-free voice conversation** reliably on the target machine, and finally record a short demo video with a reproducible run guide and basic latency statistics.

---

## Contents

1. Introduction
2. Demo-first MVP Scope (vs. Long-term Proposal)
3. System Architecture Overview
4. Implementation Progress Timeline (Jan–Feb 2026)
5. Module Details (FER, Dialogue, TTS, STT, Prosody, Logging)
6. Environment, Setup, and Reproducibility
7. Evaluation Plan and Current Evidence
8. Risks, Constraints, and Mitigations
9. Next Steps (Immediate)
Appendix A. Command Cheat Sheet

---

## 1. Introduction

Human communication is inherently multi-modal: facial expression, speech content, prosody, and interaction style co-occur and jointly shape perceived intent and emotion. The project’s long-term aim (as described in the formal proposal) is to integrate these modalities into a unified framework for naturalistic interaction.

However, a research roadmap must be grounded in demonstrable system capability. Therefore, this report focuses on the **demo-first MVP**: a pragmatic, end-to-end system that is runnable on Windows and provides observable outputs (UI overlay + speech + logs). This MVP serves as a stable platform for later research improvements (robustness, calibration, better fusion, and personality reconstruction).

---

## 2. Demo-first MVP Scope (vs. Long-term Proposal)

### 2.1 Relationship to the proposal
The proposal outlines an ambitious staged pipeline:

- Robust FER under stress tests (imbalance, degradation, drift)
- Acoustic-phonological modeling for prosody and speaker individuality
- Expressive speech generation
- Persona reconstruction and consistent interaction style
- Multimodal fusion for real-time interaction

The Jan–Feb 2026 work focuses on a **subset that can be demonstrated reliably**:

- Real-time webcam FER inference and overlay
- Persona-aware dialogue responses (offline baseline, optional LLM)
- TTS speech output (Windows baseline, optional Azure)
- Optional STT voice input (push-to-talk and continuous)
- Optional prosody features (demo-level)
- Logging and basic latency evaluation

### 2.2 Definition of the MVP pipeline

**Webcam** → **FER emotion label + confidence** → **Dialogue agent (persona-aware)** → **TTS speech output**

Optional voice input:

**Microphone** → **STT transcript** → (same agent) → **TTS**

Optional prosody add-on:

**Audio clip** → **pitch/energy** → **`voice_mood` label** → (agent adjusts tone)

---

## 3. System Architecture Overview

### 3.1 Repositories and roles

This workspace contains two FER-related codebases:

1) **Demo-first runnable system (primary):**
- `realtime_fer/Real-time-Facial-Expression-Recognition-System/`
- Purpose: real-time webcam demo, voice interaction, and logging.

2) **Research/training scaffold (secondary, not critical path for demo):**
- `fer/`
- Purpose: training/evaluation scaffolding (KD/DKD, metrics, stress tests).

### 3.2 Runtime flow (MVP)

At runtime, the MVP demo:

1. Captures frames from webcam.
2. Detects a face (YuNet by default).
3. Runs FER inference (student checkpoint / ONNX path used by the demo) to produce emotion probabilities.
4. Applies smoothing to reduce flicker.
5. Displays an overlay (emotion, confidence, persona, speaking state, optional `voice_mood`).
6. Collects user input:
	- typed (`t`)
	- push-to-talk STT (`r`)
	- hands-free continuous STT (automatic)
7. Produces a response via offline rules or optional online LLM.
8. Speaks the response via Windows TTS or optional Azure Speech TTS.
9. Writes per-session JSONL logs including per-turn latency and backend/fallback information.

---

## 4. Implementation Progress Timeline (Jan–Feb 2026)

This section summarizes work performed, aligned with the process logs.

### 4.1 Week 4 of January 2026 — Demo-first pivot and baseline validation

**Key decision:** prioritize a runnable MVP by reusing an existing real-time FER system, instead of building a training pipeline first.

Actions and outcomes:

- Adopted `realtime_fer/Real-time-Facial-Expression-Recognition-System/` as the demo baseline.
- Standardized Windows-friendly execution:
  - use `py -3.11` or `.\.venv\Scripts\python.exe`
  - avoid relying on `python` being on PATH
- Created demo repo-local venv and installed DirectML-compatible dependencies.
- Verified backend/device configuration via `scripts/check_device.py` (DirectML).
- Established a clear demo entrypoint and run documentation.

### 4.2 Week 5 of January 2026 — Online services, voice input, prosody, and evaluation logging

Actions and outcomes:

1) **Online backend integration (optional, offline-first):**
- Added optional LLM backends: Azure OpenAI / OpenAI.
- Added optional Azure Speech TTS with Windows TTS fallback.
- Added `.env.example` and `.env` loading for secrets.

2) **Evaluation instrumentation:**
- Added JSONL session logs with per-turn latency fields (LLM, TTS, STT).
- Added a latency summarizer script: `tools/diagnostics/summarize_session_latency.py`.

3) **Voice input (STT):**
- Added Azure Speech STT in push-to-talk mode (press `r`, speak once).
- Logged STT timing and success/failure.

4) **Prosody analysis (demo-level):**
- Implemented prosody feature extraction (pitch/energy) → coarse `voice_mood`.
- Supported both `.wav` prosody mode and live mic-capture prosody.
- Implemented a small fusion heuristic so responses can incorporate both face emotion and voice mood.

### 4.3 Week 1 of February 2026 — Hands-free continuous STT and repo cleanup

Actions and outcomes:

- Implemented **hands-free continuous STT** via an `AzureContinuousSTT` helper that queues recognized phrases.
- Integrated continuous STT into the main MVP loop so recognized text triggers the same message handling as typed input.
- Added a reliability safeguard: **pause STT while TTS is speaking**, then resume.
- Exposed the mode via `--stt-mode push|continuous` and PowerShell `-SttMode push|continuous`.
- Renamed the demo repo folder to a cleaner name and updated documentation references.

---

## 5. Module Details

This section describes the current MVP modules at the level needed for reporting and reproduction.

### 5.1 FER (Facial Expression Recognition)

**Role:** Real-time emotion label + confidence for UI overlay and agent conditioning.

Implementation notes:

- The demo uses a lightweight student checkpoint / ONNX artifact packaged under the demo repo.
- A face detector (YuNet) provides a stable face crop for inference.
- Smoothing (EMA/hysteresis/vote) reduces rapid label flicker.

Relevant assets:

- Student model artifacts: `models/student_best.onnx` (+ metadata JSON)
- Demo entrypoint: `demo/mvp_demo.py`

### 5.2 Dialogue / Persona module

**Role:** Given user input and state (emotion + persona, optionally `voice_mood`), generate a short response.

Design choices:

- **Offline-first** baseline to ensure the demo always runs.
- Optional online LLM backends behind the same interface.
- Persona conditioning supported (demo-level).

### 5.3 TTS (Speech output)

**Role:** Speak the response text.

Backends:

- **Windows built-in TTS** (baseline, zero setup)
- Optional **Azure Speech TTS** (higher quality), with fallback to Windows.

### 5.4 STT (Speech-to-text)

**Role:** Convert user speech into text input for the agent.

Modes:

- **Push-to-talk:** press `r`, capture one utterance, then respond.
- **Hands-free continuous:** continuously listen; when a phrase is recognized, respond immediately.

Reliability safeguard:

- **Pause STT during TTS playback** to reduce self-transcription.

### 5.5 Prosody analysis (demo-level)

**Role:** Provide an additional audio-derived signal (`voice_mood`) from pitch/energy.

Modes:

- `.wav` prosody: analyze a pre-recorded file (stable for demo).
- Mic-capture prosody: record a short segment via microphone and analyze it.

Constraint:

- Continuous STT and live mic-capture prosody both require the microphone and can conflict. For hands-free STT demos, prefer `prosody=off` or `prosody=wav`.

### 5.6 Logging and latency evaluation

**Role:** Provide evidence for stability and performance claims.

Artifacts:

- Session logs are stored as JSONL under: `outputs/sessions/`
- Latency summarizer:
  - `tools/diagnostics/summarize_session_latency.py`
  - wrapper: `run_latency.ps1`

Recorded fields include (depending on which backends are enabled):

- Input mode: typed / push-to-talk / continuous
- STT: backend, language, success, `stt_ms`
- LLM: backend, fallback flags, `llm_ms`
- TTS: backend, fallback flags, `tts_ms`
- Prosody: `voice_mood`, pitch/energy estimates, `prosody_ms`

---

## 6. Environment, Setup, and Reproducibility

### 6.1 OS and runtime assumptions

- Target OS: Windows (PowerShell)
- Preferred Python for the demo repo: **Python 3.11** (PyTorch compatibility)
- Preferred compute backend: **DirectML (DML)** for GPU acceleration on Windows without CUDA.

### 6.2 Virtual environments in this workspace

This workspace currently contains at least two venv locations:

1) Workspace root venv: `.venv/` (currently created with Python 3.14.x).
	- This is **not recommended** for the PyTorch demo path.

2) Demo repo venv: `realtime_fer/Real-time-Facial-Expression-Recognition-System/.venv/`.
	- This is the venv used by `run_mvp.ps1` and should remain the **source of truth** for the demo.
	- Current evidence from the environment: Python **3.11.9** for this repo-local venv.

### 6.3 Dependencies

- Base demo deps (DirectML path): `requirements-directml.txt`
- Optional online deps (Azure Speech / OpenAI): `requirements-online.txt`
- Optional prosody deps: `requirements-prosody.txt`

---

## 7. Evaluation Plan and Current Evidence

### 7.1 What “evaluation” means for the MVP

For the demo-first MVP, evaluation emphasizes:

- **Reliability:** does the system run without crashing (2–5 minutes)?
- **Responsiveness:** rough latency for STT/LLM/TTS steps.
- **Observability:** logs exist and can be summarized.
- **User-visible behavior:** clear overlay + audible speech.

This differs from the longer-term FER research evaluation described in the proposal (accuracy, calibration, stress tests). Those remain future work and can be supported by the `fer/` scaffold.

### 7.2 Current evidence available

- Backend check succeeds for DirectML (`scripts/check_device.py`).
- JSONL session logs exist under `outputs/sessions/` (at least one historical session is present).
- The codebase includes a summarizer to produce latency summary tables for reporting.

---

## 8. Risks, Constraints, and Mitigations

1) **Python/PyTorch compatibility on Windows**
- Risk: Python 3.14.x may not be compatible with certain PyTorch wheels.
- Mitigation: use demo repo `.venv` with Python 3.11.

2) **Microphone resource contention**
- Risk: continuous STT and mic-capture prosody can both attempt to lock the microphone.
- Mitigation: for hands-free STT demos use `prosody=off` or `prosody=wav`; for “multimodal proof” use push-to-talk STT + mic prosody.

3) **STT echo/self-transcription when TTS plays**
- Risk: recognized text includes system’s own TTS output.
- Mitigation: pause STT during TTS playback and resume afterward.

4) **Cloud availability / credentials**
- Risk: Azure/OpenAI calls fail or time out; keys may be missing.
- Mitigation: offline-first defaults; `.env` for local secrets; fallback paths in the code.

5) **Demo usability issues**
- Risk: overlay readability and operator workflow may be unclear.
- Mitigation: keep a scripted recording plan; default to stable settings; reduce optional features during the recorded demo.

---

## 9. Next Steps (Immediate)

The next development step is **not more features**, but **verification on the target machine**.

### 9.1 Baseline MVP run (offline)

Goal: Confirm stable webcam UI + offline dialogue + Windows TTS.

Acceptance criteria:

- Runs 2–5 minutes without crashing
- Emotion overlay is visible and changes
- TTS output is audible
- A new session JSONL is created

### 9.2 Enable hands-free voice conversation

Goal: Confirm continuous STT recognizes utterances and triggers the response flow.

Acceptance criteria:

- Recognized phrases appear in the UI/logs
- Replies are generated and spoken
- STT pauses while speaking and resumes afterward

### 9.3 Record demo + produce quick latency summary

Goal: Generate final artifacts for submission.

- Record 1–3 minute demo video (screen + audio)
- Run the latency summarizer and paste summary into documentation/report

---

## Appendix A. Command Cheat Sheet

All commands below assume PowerShell.

### A1) Go to the demo repo

```powershell
Set-Location "C:\Multimodal Virtual Communication System\realtime_fer\Real-time-Facial-Expression-Recognition-System"
```

### A2) Baseline MVP (offline + Windows TTS)

```powershell
.\run_mvp.ps1 -Device dml -Detector yunet -Speak -Llm offline -Tts windows -Stt off -Prosody off
```

### A3) Hands-free voice (continuous STT)

Prerequisite: create `.env` from `.env.example` and set `AZURE_SPEECH_KEY` and `AZURE_SPEECH_REGION`.

```powershell
.\run_mvp.ps1 -Device dml -Detector yunet -Speak -Llm offline -Tts windows -Stt azure -SttMode continuous -SttLang en-US -Prosody off
```

### A4) Summarize latency from session logs

```powershell
.\run_latency.ps1
```

