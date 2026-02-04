# Multimodal Virtual Communication System (MVP)

A Windows-first, demo-focused prototype that integrates:

- **Real-time Facial Expression Recognition (FER)** from webcam
- **Dialogue** (offline baseline; optional Azure OpenAI)
- **Text-to-Speech (TTS)** (Windows voice; optional Azure Speech)
- **Speech-to-Text (STT)** (optional Azure Speech: push-to-talk or hands-free continuous)
- **Simple prosody / voice mood** (optional; wav or mic)
- **Session logging** (JSONL + latency summaries)

This repo also includes a separate research/training scaffold for FER knowledge distillation.

---

## Repo Structure

- `realtime_fer/Real-time-Facial-Expression-Recognition-System/`
	- The **main runnable demo** (PowerShell entrypoint: `run_mvp.ps1`)
	- Includes the YuNet face detector model and a distilled FER student model
- `fer/`
	- Training + evaluation scaffold (KD/DKD, ArcFace, stress tests)
- `Doc for Project/`
	- Proposal, plan, process logs, and reports

---

## Quickstart (Windows) — Run the MVP Demo

The MVP demo is designed to run from:

`realtime_fer/Real-time-Facial-Expression-Recognition-System/`

### 1) Create venv (Python 3.11 recommended)

```powershell
Set-Location "C:\Multimodal Virtual Communication System\realtime_fer\Real-time-Facial-Expression-Recognition-System"
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
```

Install dependencies:

- Recommended for many Windows machines (DirectML backend):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-directml.txt
```

- Optional online features (Azure Speech + OpenAI/Azure OpenAI + `.env` loading):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-online.txt
```

- Optional prosody analysis:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-prosody.txt
```

### 2) Run (offline, safest baseline)

```powershell
Set-Location "C:\Multimodal Virtual Communication System\realtime_fer\Real-time-Facial-Expression-Recognition-System"
.\run_mvp.ps1 -Device dml -Detector yunet -Speak -Stt off
```

If you don’t want speech output, omit `-Speak`.

### 3) Optional: enable hands-free voice input (Azure STT)

1) Copy the example env file:

```powershell
Copy-Item .env.example .env
```

2) Edit `.env` and set:

- `AZURE_SPEECH_KEY`
- `AZURE_SPEECH_REGION`

3) Run continuous STT mode:

```powershell
.\run_mvp.ps1 -Device dml -Detector yunet -Speak -Stt azure -SttMode continuous -SttLang en-US
```

Push-to-talk mode (press `r` once to record one utterance):

```powershell
.\run_mvp.ps1 -Device dml -Detector yunet -Speak -Stt azure -SttMode push -SttLang en-US
```

### 4) Optional: Azure OpenAI replies and/or Azure TTS

If you installed `requirements-online.txt`, you can use:

```powershell
.\run_mvp.ps1 -Device dml -Detector yunet -Speak -Llm azure-openai -Tts azure
```

For Azure OpenAI, set these in `.env`:

- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_DEPLOYMENT`

---

## Demo Controls

Click the OpenCV window first, then press:

- `q`: quit
- `p`: cycle persona
- `t`: type a message in the terminal
- `r`: record one utterance (only in STT push mode)
- `s`: toggle speech

In continuous STT mode, you can speak naturally. The demo pauses listening while it speaks to reduce self-transcription.

---

## Logs & Latency Summary

By default, the demo writes session logs to:

- `realtime_fer/Real-time-Facial-Expression-Recognition-System/outputs/sessions/mvp_<timestamp>.jsonl`

Summarize latency:

```powershell
Set-Location "C:\Multimodal Virtual Communication System\realtime_fer\Real-time-Facial-Expression-Recognition-System"
.\run_latency.ps1
```

---

## Notes / Troubleshooting

- **Python version**: Use Python **3.11** for the demo venv to avoid PyTorch compatibility issues.
- **Multiple cameras**: If the wrong camera opens, adjust the camera index in the demo if needed.
- **Mic contention**: `-SttMode continuous` and `-Prosody mic` may compete for the microphone. For hands-free STT, prefer `-Prosody off` or `-Prosody wav`.
- **Secrets**: Do not commit `.env`. This repo ships `.env.example` only.

---

## Docs

- Demo playbook: `realtime_fer/Real-time-Facial-Expression-Recognition-System/docs/mvp_demo_playbook.md`
- Project plan and report: `Doc for Project/`