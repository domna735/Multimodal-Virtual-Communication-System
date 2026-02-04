# MVP Demo Playbook (FER + Persona + TTS)

This MVP demo follows the pipeline in your proposal:

Webcam → FER (emotion label) → Persona-conditioned reply → TTS

## 1) Create environment (Python 3.11)
From the project root.

If you are not sure you are in the right folder, run this first (safe with spaces):
```powershell
Set-Location "C:\Multimodal Virtual Communication System\realtime_fer\Real-time-Facial-Expression-Recognition-System"
```

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-directml.txt
```

Optional (online LLM + online TTS backends):
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-online.txt
```

Optional (prosody / voice mood from a pre-recorded .wav):
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-prosody.txt
```

## 1b) Configure API keys (optional)

Copy the example env file:
```powershell
Copy-Item .env.example .env
```

Then edit `.env` and set:
- `AZURE_OPENAI_API_KEY` + `AZURE_OPENAI_ENDPOINT` + `AZURE_OPENAI_DEPLOYMENT` (recommended; for LLM replies)
- OR `OPENAI_API_KEY` (optional alternative)
- `AZURE_SPEECH_KEY` + `AZURE_SPEECH_REGION` (for online TTS + online STT)
- Optional: `AZURE_SPEECH_LANG` (for STT; e.g. `en-US`)

The demo automatically loads `.env` on startup if `python-dotenv` is installed.

Tip: If you don't want to use `.env`, you can set environment variables in PowerShell instead.

## 2) Check device

```powershell
.\.venv\Scripts\python.exe scripts\check_device.py
```

If DirectML is installed you should see `backend: dml`.

## 3) Run MVP demo

Easiest (recommended): use the helper script (avoids copy/paste/link issues):
```powershell
Set-Location "C:\Multimodal Virtual Communication System\realtime_fer\Real-time-Facial-Expression-Recognition-System"
.\run_mvp.ps1 -Device dml -Detector yunet -Speak
```

Enable voice input (Azure STT):
```powershell
.\run_mvp.ps1 -Device dml -Detector yunet -Speak -Stt azure -SttLang en-US
```

Hands-free voice input (continuous Azure STT):
```powershell
.\run_mvp.ps1 -Device dml -Detector yunet -Speak -Stt azure -SttMode continuous -SttLang en-US
```

Enable prosody from a pre-recorded `.wav` (decision A; simplest multimodal demo):
```powershell
.\run_mvp.ps1 -Device dml -Detector yunet -Speak -Prosody wav -ProsodyWav "C:\path\to\demo_voice.wav"
```

Enable prosody from live microphone capture (decision B; more real-time):
```powershell
.\run_mvp.ps1 -Device dml -Detector yunet -Speak -Stt azure -SttLang en-US -Prosody mic -ProsodySeconds 3.0
```

Note: `-SttMode continuous` and `-Prosody mic` may conflict (both use the microphone). For hands-free STT, prefer `-Prosody off` or `-Prosody wav`.

```powershell
.\.venv\Scripts\python.exe demo\mvp_demo.py --device dml --detector yunet --speak
```

For Azure OpenAI + Azure TTS (recommended):
```powershell
.\.venv\Scripts\python.exe demo\mvp_demo.py --device dml --detector yunet --speak --llm azure-openai --tts azure
```

For voice input + Azure OpenAI + Azure TTS:
```powershell
.\.venv\Scripts\python.exe demo\mvp_demo.py --device dml --detector yunet --speak --stt azure --stt-lang en-US --llm azure-openai --tts azure
```

Hands-free voice input + Azure OpenAI + Azure TTS:
```powershell
.\.venv\Scripts\python.exe demo\mvp_demo.py --device dml --detector yunet --speak --stt azure --stt-mode continuous --stt-lang en-US --llm azure-openai --tts azure
```

Important:
- Don’t paste VS Code “linkified” text like `[python.exe](http://...)` into PowerShell. Type/copy the real command above.

By default, the demo writes a JSONL session log to:
- `outputs/sessions/mvp_<timestamp>.jsonl`

To summarize latency for your evaluation section:
```powershell
.\.venv\Scripts\python.exe tools\diagnostics\summarize_session_latency.py
```

Easiest (recommended):
```powershell
.\run_latency.ps1
```

To break down results by backend pair (LLM + TTS):
```powershell
.\.venv\Scripts\python.exe tools\diagnostics\summarize_session_latency.py --by-backend
```

Or:
```powershell
.\run_latency.ps1 -ByBackend
```

To disable logging:
```powershell
.\.venv\Scripts\python.exe demo\mvp_demo.py --device dml --detector yunet --speak --no-log
```

To choose a custom log file path:
```powershell
.\.venv\Scripts\python.exe demo\mvp_demo.py --device dml --detector yunet --speak --log-path outputs/sessions/my_run.jsonl
```

Controls:
- Click the demo window first, then press:
	- `q`: quit
	- `p`: cycle persona
	- `t`: start a chat (you will then type your message in the PowerShell console prompt)
	- `r`: record one utterance from the microphone (requires `--stt azure`; only used in `--stt-mode push`)
	- `s`: toggle speech

If you run with `--stt-mode continuous`, you can just speak naturally (the demo pauses listening while it speaks to reduce feedback loops).

## 4) Notes
- If you don’t want speech output, run with `--no-speak`.
- Default dialogue is a lightweight offline baseline (rule-based).

### Online LLM (optional)
Use Azure OpenAI for replies:
```powershell
.\.venv\Scripts\python.exe demo\mvp_demo.py --device dml --detector yunet --speak --llm azure-openai
```

Use the OpenAI API for replies (alternative):
```powershell
.\.venv\Scripts\python.exe demo\mvp_demo.py --device dml --detector yunet --speak --llm openai
```

### Online TTS (optional)
Use Azure Speech for TTS (falls back to Windows voice if not configured):
```powershell
.\.venv\Scripts\python.exe demo\mvp_demo.py --device dml --detector yunet --speak --tts azure
```

You can combine both:
```powershell
.\.venv\Scripts\python.exe demo\mvp_demo.py --device dml --detector yunet --speak --llm openai --tts azure
```

## 5) Locked recording script
Use this when you’re ready to record a stable demo video:
- [docs/demo_recording_script.md](docs/demo_recording_script.md)
