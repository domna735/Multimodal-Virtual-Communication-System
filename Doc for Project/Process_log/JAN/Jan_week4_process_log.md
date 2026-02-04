# Process Log - Week 4 of January 2026
This document captures the daily activities, decisions, and reflections during the fourth week of January 2026, focusing on reconstructing the facial expression recognition system as per the established plan.

---

## 2026-01-19 | Demo-first pivot + reuse existing realtime FER
Intent:
- Prioritize a **demo-first MVP** instead of building a research-grade FER training pipeline from scratch.
- Validate that the existing real-time FER repo can be used as the FER module for the MVP.

Action:
- Confirmed the MVP target pipeline: **webcam → FER label → persona reply → TTS**.
- Verified Python availability on Windows:
	- `python` was not available on PATH.
	- Used Windows Python launcher `py` to locate installed versions.
- Selected Python 3.11 for PyTorch compatibility (avoided using the default Python 3.14).
- Created a virtual environment under:
	- `realtime_fer/Real-time-Facial-Expression-Recognition-System/.venv`
- Installed DirectML-compatible runtime dependencies (Torch + `torch-directml`) using:
	- `requirements-directml.txt`

Result:
- Device/backend check succeeded with DirectML (DML) as the selected backend.
- Student checkpoint loading/inference smoke test succeeded (checkpoint loads and returns a valid probability vector).
- Added/validated demo artifacts in the realtime repo:
	- `demo/mvp_demo.py` (MVP demo entrypoint)
	- `docs/mvp_demo_playbook.md` (how to run)

Decision / Interpretation:
- For the MVP/demo path, we will treat:
	- `realtime_fer/Real-time-Facial-Expression-Recognition-System/`
	as the **FER module** (already runnable and demo-ready on Windows).
- The separate scaffold under `fer/` remains useful for future research/training work, but it is not the critical path for Demo V1.

Next:
- Run the MVP demo end-to-end on the target machine with webcam + audio output.
- If webcam/audio issues appear, capture error logs and update the playbook with fixes.

---

## 2026-01-20 | MVP run verification (pending user run)
Intent:
- Confirm live behavior: webcam capture, stable emotion overlay, persona reply, and audible TTS.

Action (planned):
- Run:
	- `./.venv/Scripts/python.exe demo/mvp_demo.py --device dml --detector yunet --speak`

Result:
- TBD (needs live run on the machine with webcam/mic/speaker permissions).

Decision / Interpretation:
- TBD

Next:
- If successful: proceed to Phase 1 polish (UI overlays + session logging).
- If failing: triage (camera index, permissions, missing models, audio policy).

---

## Notes (Week 4)
- Main risk encountered: **Windows PATH did not resolve `python`**, so all instructions should prefer `py -3.11` or `./.venv/Scripts/python.exe`.
- Main technical choice: **DirectML backend** for GPU acceleration on Windows without CUDA.
- Demo-first choice: reuse existing working repo to reduce risk and hit a reliable MVP sooner.