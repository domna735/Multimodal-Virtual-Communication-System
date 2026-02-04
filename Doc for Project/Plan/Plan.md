# Project Plan — Multimodal Virtual Communication System (Demo-first MVP)

**Author:** Ma Kai Lun Donovan  

## 1. Goal
Build a working **Minimal Viable Prototype (MVP)** that demonstrates a real-time multimodal interaction pipeline:

**Webcam → FER emotion label → persona-aware dialogue → TTS speech output → simple UI**

This MVP is the demo version aligned with the proposal in:
- [Doc for Project/short for demo v1 proposal.md](Doc%20for%20Project/short%20for%20demo%20v1%20proposal.md)

## 2. Scope

### In-scope (MVP)
1. **Real-time FER**
	- Input: webcam video
	- Output: emotion label + confidence
	- Includes smoothing (EMA/hysteresis/vote)
2. **Persona-aware dialogue**
	- Input: user text + emotion + persona
	- Output: short response (tone-adjusted)
	- Baseline: offline rule-based replies (always available)
	- Upgrade: online LLM API backend (optional; same interface)
3. **TTS output**
	- Baseline: Windows built-in TTS (System.Speech) for zero setup
	- Upgrade: online TTS API (e.g., Azure Speech) for higher quality/voices
4. **Voice input (STT) (optional)**
	- Upgrade: Azure Speech-to-Text (microphone) to support hands-free interaction
	- MVP styles:
		- Push-to-talk: press a hotkey to record one utterance, then reply + speak
		- Hands-free: continuous listening (auto-detect utterances), then reply + speak

5. **Prosody analysis (simple) (optional)**
	- Target (demo-level): analyze a short audio clip (mic capture; optional `.wav` fallback)
	- Features (simple): mean pitch + mean energy
	- Map to a small label: `calm | excited | tense | sad` (demo heuristic)

6. **UI + logging**
	- Webcam display + overlayed emotion
	- Basic chat interaction (console input is acceptable for MVP)
	- Save lightweight logs for demo/evaluation

### Out-of-scope (for MVP)
- Full personality reconstruction
- Advanced voiceprint / prosody modeling (research-level)
- Custom TTS training
- GAN-based prosody generation
- Large-scale user study

## 2.5 Demo Checklist Status (Simplest Multimodal Demo)

This maps your “最簡單可行版” checklist to the current implementation status.

**Part 0 — 基本準備**
- [x] Repo-local `.venv` + PowerShell helper scripts
- [x] Verify the repo `.venv` uses Python **3.11** (avoid 3.14 for PyTorch compatibility) (verified: 3.11.9)
- [x] `opencv-python` + `numpy` installed (demo already runs)
- [ ] `librosa` installed (needed only for the *prosody analysis* part)
- [ ] `sounddevice` installed (needed only for *mic capture prosody*; not for TTS)
- [ ] Microphone permissions / device works (only needed if we choose “live mic prosody demo”)

**Part 1 — Real-time FER**
- [x] Open webcam + detect face + run FER model
- [x] Output emotion label + confidence
- [x] UI overlay shows emotion + confidence

**Part 2 — Prosody Analysis (最簡單版)**
- [x] Implemented (demo-level): mic capture → pitch/energy → `voice_mood` (optional deps)

**Part 3 — Rule-based Agent (if-else)**
- [x] Implemented baseline rule-based replies (offline mode)
- [x] Uses emotion + persona today
- [x] Implemented (demo-level): fuse emotion + `voice_mood` into response rules (simple heuristic)

**Part 4 — TTS**
- [x] Implemented: Windows built-in TTS
- [x] Implemented (optional): Azure Speech TTS with fallback
- [ ] Not implemented: Coqui/XTTS “tone control” (pitch/speed) as you described

**Part 5 — Integration Demo Flow**
- [x] Webcam → emotion → response text → TTS (typed input and/or STT input)
- [x] Implemented: add prosody block and display `voice_mood` in UI overlay

**Part 6 — Demo 展示流程**
- [x] A stable demo path exists (FER + dialogue + TTS + logging)
- [x] Implemented: prosody step (`voice_mood`) to make it clearly “multimodal (face + voice)”
- [x] Implemented: continuous STT option for more natural conversation flow

## 3. Current Assets (Already Available)
We already have a working real-time FER demo and checkpoint under:
- [realtime_fer/Real-time-Facial-Expression-Recognition-System](realtime_fer/Real-time-Facial-Expression-Recognition-System)

MVP demo entrypoint (already added):
- [realtime_fer/Real-time-Facial-Expression-Recognition-System/demo/mvp_demo.py](realtime_fer/Real-time-Facial-Expression-Recognition-System/demo/mvp_demo.py)

Run instructions:
- [realtime_fer/Real-time-Facial-Expression-Recognition-System/docs/mvp_demo_playbook.md](realtime_fer/Real-time-Facial-Expression-Recognition-System/docs/mvp_demo_playbook.md)

Detailed “one-by-one” playbook:
- [Doc for Project/Plan/Detailed_Playbook_MVP.md](Doc%20for%20Project/Plan/Detailed_Playbook_MVP.md)

Also available (future research / training scaffold, not required for Demo V1):
- [fer](fer)

## 4. Deliverables

### MVP Deliverables (Demo-ready)
1. **Working demo application**
	- Real-time webcam FER + emotion overlay
	- Persona selection
	- Dialogue response generation
	- Speech playback
2. **Short demo video** (1–3 minutes)
3. **Documentation**
	- How to run
	- Architecture diagram (simple block diagram is enough)
	- Limitations + future work
4. **Evaluation notes**
	- Latency (approx.)
	- Qualitative response appropriateness
	- Stability notes (crashes, webcam issues, etc.)

## 5. Work Plan (Phases)

### Phase 0 — Environment & Baseline Run (Day 1)
**Goal:** Ensure the demo runs end-to-end on the target machine.

Tasks:
- Use Python 3.11 via `py -3.11` (avoid Python 3.14 for PyTorch)
- Create venv and install dependencies
- Run device check
- Run FER-only realtime demo
- Run MVP demo

Recommended commands (Windows PowerShell):
```powershell
# Option A (recommended): jump to repo by absolute path (safe with spaces)
Set-Location "C:\Multimodal Virtual Communication System\realtime_fer\Real-time-Facial-Expression-Recognition-System"

# Option B: from workspace root only
# cd ".\realtime_fer\Real-time-Facial-Expression-Recognition-System"

# Create venv (Python 3.11)
py -3.11 -m venv .venv

# Install deps (DirectML runtime)
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-directml.txt

# Check backend/device
.\.venv\Scripts\python.exe scripts\check_device.py

# Run MVP demo
.\.venv\Scripts\python.exe demo\mvp_demo.py --device dml --detector yunet --speak
```

Exit criteria:
- Demo opens webcam and shows predicted emotion
- No import errors
- Stable for 2–5 minutes continuous runtime

### Phase 1 — MVP UI + Interaction Polish (Week 1)
**Goal:** Make the demo more “presentation-friendly”.

Tasks:
- Improve on-screen overlays (emotion label, confidence, persona, speaking state)
- Add simple chat log rendering (still okay to keep console input)
- Add a “push-to-talk” style flow (press key to type, then speak)
- Add basic logging (CSV/JSON) of: timestamp, emotion, persona, user text, system response

Exit criteria:
- Clear UI status
- Logs saved for each session

### Phase 1.5 — API Setup (Online LLM + Online TTS)
**Goal:** Add optional online backends without breaking offline mode.

Tasks:
- Keep offline rule-based dialogue as the default fallback
- Add **LLM API** backend behind the same interface (recommended: Azure OpenAI)
- Add **online TTS API** backend behind the same interface
- Use environment variables for secrets (no keys hard-coded)
- Add basic timeouts + graceful fallback to offline/Windows TTS
- Provide a `.env.example` file and document required env vars

Exit criteria:
- Demo still works fully offline
- When keys are configured, LLM replies and online TTS both work

### Phase 1.6 — Voice Interaction (Online STT)
**Goal:** Add optional voice input (microphone) to enable “real-time talk” while keeping typed input as a fallback.

Tasks:
- Add STT backend (recommended: Azure Speech)
	- Push-to-talk: capture one utterance on demand
	- Optional hands-free: continuous recognition for more natural talk
- Keep offline-first behavior: if STT is not configured/fails, typed chat still works
- Log STT latency + transcript (for evaluation)

Exit criteria:
- Demo supports both:
	- typed chat (press `t`)
	- voice input (push-to-talk: press `r`, speak once, then get reply + TTS)
	- (optional) hands-free voice input (continuous STT)

### Phase 1.7 — Prosody Analysis (Demo-level)
**Goal:** Make the demo clearly “multimodal”: face (FER) + voice (prosody/energy), without any heavy modeling.

Tasks:
- Add a small prosody analyzer using `librosa`:
	- mean/median pitch (e.g., `librosa.yin`)
	- mean energy (RMS)
- Use **Decision (B)**: microphone live capture (more real-time)
	- Record one short utterance to a temp `.wav` (via `sounddevice` + `soundfile`)
	- Reuse that same audio for both prosody analysis and STT (so one press = one utterance)
- Map to a simple `voice_mood`: `calm | excited | tense | sad`
- Display `voice_mood` on the UI overlay
- Add a simple fusion rule: response depends on both `emotion` and `voice_mood`

Exit criteria:
- A single run can demonstrate:
	- emotion label changing in real time
	- voice_mood derived from a short mic capture (1 utterance)
	- response text changes based on both signals

### Phase 2 — Dialogue Module Upgrade (Week 2)
**Goal:** Keep offline baseline, but optionally support an LLM.

Tasks:
- Keep the current offline rule-based baseline as a fallback
- Add an optional LLM backend (online API) behind the same interface:
  - input: `user_text`, `emotion`, `persona`
  - output: `reply_text`
- Add safety constraints: short responses, neutral content, no private data storage by default

Exit criteria:
- Demo works without internet (baseline)
- If configured, LLM mode generates responses that reflect persona + emotion

### Phase 3 — TTS Upgrade (Week 3)
**Goal:** Improve voice quality or expressiveness while keeping the system stable.

Options:
- Keep Windows TTS as default (fastest, no extra deps)
- Add optional **online TTS** engine (e.g., Azure Speech) as a selectable backend

Exit criteria:
- Speech output is reliable
- Clear “speak on/off” control

### Phase 4 — Integration + Demo Recording (Week 4)
**Goal:** Produce final demo artifacts for submission.

Tasks:
- Run a scripted demo scenario (3 personas, multiple emotions)
- Record screen + audio
- Produce a short results summary (latency, stability, qualitative notes)
- Finalize docs

Exit criteria:
- Demo video completed
- Run guide verified on a clean machine/venv

## 6. Timeline (Suggested)
- **Week 0 (today):** baseline run + confirm environment
- **Week 1:** UI polish + logging
- **Week 2:** optional LLM integration
- **Week 3:** optional TTS upgrade
- **Week 4:** finalize docs + record demo video

## 7. Risks & Mitigations
1. **Python/PyTorch compatibility (Windows)**
	- Mitigation: use Python 3.11 venv; prefer DirectML if no CUDA
2. **Webcam/driver issues**
	- Mitigation: allow `--camera-index` and video-file input
3. **Latency**
	- Mitigation: keep FER model lightweight; reduce frame size; avoid blocking calls in the render loop
4. **LLM/API availability**
	- Mitigation: offline fallback responses always available
6. **API keys / secret leakage**
	- Mitigation: store secrets in environment variables or a local `.env` file; never hard-code keys; avoid committing secrets
5. **Demo reliability**
	- Mitigation: log errors, keep defaults stable, avoid too many optional features in the main demo path

## 8. Definition of Done (MVP)
The MVP is considered done when:
- A single command starts the demo and opens the webcam UI
- Emotion label updates in real time with smoothing
- User can select persona and enter text
- System produces a persona-appropriate reply
- System can speak the reply (default Windows TTS is acceptable)
- A short demo video + run instructions exist

## 9. Next Step (Immediate)
Run the MVP demo and confirm the live experience:
- Emotion stability (flicker vs smoothing)
- Audio output works on your PC
- Persona switching works

Then enable online backends (one-by-one):
1) Online LLM replies
2) Online TTS speech output

If you want to continue “one by one” from FER:
- For the MVP/demo: keep using `realtime_fer/Real-time-Facial-Expression-Recognition-System` as the FER module.
- For the research report/thesis: we can later revisit the `fer/` scaffold (KD/DKD/ArcFace/stress-tests) once the demo is stable.

