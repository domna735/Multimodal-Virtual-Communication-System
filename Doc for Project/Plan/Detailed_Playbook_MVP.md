# Detailed Playbook — Multimodal Virtual Communication System (MVP)

This playbook is designed to be followed **one-by-one**, so each step gives you a working demo milestone.

Target OS: Windows (PowerShell)

---

## 0) Working folder (always start here)

```powershell
Set-Location "C:\Multimodal Virtual Communication System\realtime_fer\Real-time-Facial-Expression-Recognition-System"
```

---

## 1) Milestone A — Baseline: webcam + FER UI

### A1. Create venv (Python 3.11)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-directml.txt
```

### A2. Verify device

```powershell
.\.venv\Scripts\python.exe scripts\check_device.py
```

Expected: `backend: dml` (or `cpu` if DirectML is not available).

### A3. Run the demo

```powershell
.\run_mvp.ps1 -Device dml -Detector yunet
```

Controls (click the demo window first):
- `q` quit
- `p` cycle persona
- `s` toggle speaking
- `t` typed chat (console input)
- `r` voice input (only works if STT is enabled)

---

## 2) Milestone B — Typed chat + Windows TTS

```powershell
.\run_mvp.ps1 -Device dml -Detector yunet -Speak
```

Now:
- Press `t` in the demo window
- Type a message in the console
- The bot replies and speaks (Windows built-in voice)

Logs are written to:
- `outputs/sessions/mvp_<timestamp>.jsonl`

---

## 3) Milestone C — Latency evaluation (STT/LLM/TTS)

After a short run (a few turns), summarize latency:

```powershell
.\run_latency.ps1
```

Optional breakdown by backend pair:

```powershell
.\run_latency.ps1 -ByBackend
```

---

## 4) Milestone D — Enable online backends (install deps)

Install the optional online packages:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-online.txt
```

---

## 5) Milestone E — Configure secrets via `.env` (recommended)

```powershell
Copy-Item .env.example .env
```

Edit `.env` and set:
- Azure OpenAI (LLM): `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`
- Azure Speech (TTS + STT): `AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION`
- Optional STT language: `AZURE_SPEECH_LANG` (example: `en-US`)

---

## 6) Milestone F — Online LLM (Azure OpenAI)

```powershell
.\run_mvp.ps1 -Device dml -Detector yunet -Speak -Llm azure-openai
```

If the API is missing or fails, it automatically falls back to offline replies.

---

## 7) Milestone G — Online TTS (Azure Speech)

```powershell
.\run_mvp.ps1 -Device dml -Detector yunet -Speak -Tts azure
```

If Azure TTS fails, it falls back to Windows TTS.

---

## 8) Milestone H — “Real-time talk”: voice input (Azure STT)

Run with STT enabled:

```powershell
.\run_mvp.ps1 -Device dml -Detector yunet -Speak -Stt azure -SttLang en-US
```

Then:
- Click the demo window
- Press `r`
- Speak one sentence
- The recognized text is used as the user message, then the system replies and speaks

If no speech is recognized, it prints `(No speech recognized)` and continues.

---

## 9) Recommended demo recording checklist

- Start with `llm=azure-openai`, `tts=azure`, `stt=azure` shown in the overlay.
- Show emotion overlay changing for a few seconds.
- Press `r` and speak a short line (clear voice).
- Press `p` to change persona and repeat once.
- End by running:

```powershell
.\run_latency.ps1 -ByBackend
```

Paste the printed numbers into your evaluation notes.

---

## 10) Troubleshooting (quick)

- If PowerShell says a command is not found, ensure you ran the `Set-Location ...` step.
- If STT/TTS doesn’t work, re-check `.env` values: `AZURE_SPEECH_KEY` and `AZURE_SPEECH_REGION`.
- If the demo window doesn’t respond to keys, click the window once to focus it.
