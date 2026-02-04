"""Summarize MVP demo latency from JSONL session logs.

Looks for lines with event == "latency" (preferred) and reads:
- stt_ms: optional[float]
- stt_ok: optional[bool]
- llm_ms: optional[float]
- tts_ms: optional[float]
- tts_ok: optional[bool]
- used_llm_fallback: bool
- used_tts_fallback: bool

Usage (PowerShell):
  .\.venv\Scripts\python.exe tools\diagnostics\summarize_session_latency.py
  .\.venv\Scripts\python.exe tools\diagnostics\summarize_session_latency.py --glob "outputs/sessions/*.jsonl"
  .\.venv\Scripts\python.exe tools\diagnostics\summarize_session_latency.py --by-backend
"""

from __future__ import annotations

import argparse
import glob
import json
import math
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median
from typing import Dict, Iterable, Iterator, List, Optional, Tuple


REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Stats:
    n: int
    avg: Optional[float]
    med: Optional[float]
    p95: Optional[float]


def _iter_jsonl(path: Path) -> Iterator[dict]:
    with path.open("r", encoding="utf-8") as fp:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                yield obj


def _pctl_nearest_rank(values: List[float], p: float) -> Optional[float]:
    if not values:
        return None
    if p <= 0:
        return float(min(values))
    if p >= 100:
        return float(max(values))
    vs = sorted(float(v) for v in values)
    k = int(math.ceil((p / 100.0) * len(vs))) - 1
    k = max(0, min(k, len(vs) - 1))
    return float(vs[k])


def _stats(values: List[float]) -> Stats:
    if not values:
        return Stats(n=0, avg=None, med=None, p95=None)
    return Stats(
        n=len(values),
        avg=float(mean(values)),
        med=float(median(values)),
        p95=_pctl_nearest_rank(values, 95.0),
    )


def _fmt_ms(x: Optional[float]) -> str:
    if x is None:
        return "n/a"
    return f"{x:.1f} ms"


def _collect_latency_rows(paths: Iterable[Path]) -> Iterator[dict]:
    for path in paths:
        for row in _iter_jsonl(path):
            if row.get("event") == "latency":
                row = dict(row)
                row["_path"] = str(path)
                yield row


def _expand_globs(globs: List[str]) -> List[Path]:
    out: List[Path] = []
    for pattern in globs:
        pat = pattern
        if not ("/" in pat or "\\" in pat):
            pat = str(REPO_ROOT / pat)
        for m in glob.glob(pat):
            p = Path(m)
            if p.is_file():
                out.append(p)
    # de-dupe, stable-ish
    seen = set()
    uniq: List[Path] = []
    for p in sorted(out, key=lambda x: str(x)):
        s = str(p.resolve())
        if s in seen:
            continue
        seen.add(s)
        uniq.append(p)
    return uniq


def _backend_key(row: dict) -> Tuple[str, str, str]:
    llm = str(row.get("llm_backend") or "")
    tts = str(row.get("tts_backend") or "")
    stt = str(row.get("stt_backend") or "")
    return (llm, tts, stt)


def main() -> int:
    ap = argparse.ArgumentParser(description="Summarize MVP demo LLM/TTS latency from JSONL logs")
    ap.add_argument(
        "--glob",
        dest="globs",
        action="append",
        default=["outputs/sessions/*.jsonl"],
        help="Glob(s) for JSONL logs. May be repeated. Default: outputs/sessions/*.jsonl",
    )
    ap.add_argument(
        "--by-backend",
        action="store_true",
        help="Also print separate summaries per (llm_backend, tts_backend) pair.",
    )
    args = ap.parse_args()

    paths = _expand_globs(list(args.globs))
    if not paths:
        print("No JSONL logs found.")
        print("Tried globs:")
        for g in list(args.globs):
            print(f"- {g}")
        print("\nTip: run the MVP once, or pass --glob to point at your log file(s).")
        return 2

    rows = list(_collect_latency_rows(paths))
    if not rows:
        print("No latency events found in logs.")
        print("Tip: ensure you're using the updated demo that logs event=latency.")
        return 3

    stt_vals: List[float] = []
    llm_vals: List[float] = []
    tts_vals: List[float] = []
    llm_fallback = 0
    tts_fallback = 0
    tts_fail = 0
    stt_fail = 0

    by_backend: Dict[Tuple[str, str, str], List[dict]] = {}

    for r in rows:
        stt = r.get("stt_ms")
        llm = r.get("llm_ms")
        tts = r.get("tts_ms")
        if isinstance(stt, (int, float)) and math.isfinite(float(stt)):
            stt_vals.append(float(stt))
        if isinstance(llm, (int, float)) and math.isfinite(float(llm)):
            llm_vals.append(float(llm))
        if isinstance(tts, (int, float)) and math.isfinite(float(tts)):
            tts_vals.append(float(tts))

        if bool(r.get("used_llm_fallback")):
            llm_fallback += 1
        if bool(r.get("used_tts_fallback")):
            tts_fallback += 1
        if r.get("tts_ok") is False:
            tts_fail += 1
        if r.get("stt_ok") is False:
            stt_fail += 1

        if args.by_backend:
            by_backend.setdefault(_backend_key(r), []).append(r)

    stt_s = _stats(stt_vals)
    llm_s = _stats(llm_vals)
    tts_s = _stats(tts_vals)

    print("Latency summary")
    print(f"- Files: {len(paths)}")
    print(f"- Latency events: {len(rows)}")
    print(f"- STT: n={stt_s.n} avg={_fmt_ms(stt_s.avg)} p95={_fmt_ms(stt_s.p95)} med={_fmt_ms(stt_s.med)}")
    print(f"- LLM: n={llm_s.n} avg={_fmt_ms(llm_s.avg)} p95={_fmt_ms(llm_s.p95)} med={_fmt_ms(llm_s.med)}")
    print(f"- TTS: n={tts_s.n} avg={_fmt_ms(tts_s.avg)} p95={_fmt_ms(tts_s.p95)} med={_fmt_ms(tts_s.med)}")
    print(f"- Fallbacks: llm={llm_fallback} tts={tts_fallback} (tts_fail={tts_fail} stt_fail={stt_fail})")

    if args.by_backend:
        print("\nBy backend")
        for (llm_b, tts_b, stt_b), rr in sorted(by_backend.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2])):
            s2: List[float] = []
            l2: List[float] = []
            t2: List[float] = []
            for r in rr:
                stt = r.get("stt_ms")
                llm = r.get("llm_ms")
                tts = r.get("tts_ms")
                if isinstance(stt, (int, float)) and math.isfinite(float(stt)):
                    s2.append(float(stt))
                if isinstance(llm, (int, float)) and math.isfinite(float(llm)):
                    l2.append(float(llm))
                if isinstance(tts, (int, float)) and math.isfinite(float(tts)):
                    t2.append(float(tts))
            ss = _stats(s2)
            ls = _stats(l2)
            ts = _stats(t2)
            label = f"llm={llm_b or 'unknown'} | tts={tts_b or 'unknown'} | stt={stt_b or 'unknown'}"
            print(
                f"- {label}: STT(avg={_fmt_ms(ss.avg)}, p95={_fmt_ms(ss.p95)}, n={ss.n}) | "
                f"LLM(avg={_fmt_ms(ls.avg)}, p95={_fmt_ms(ls.p95)}, n={ls.n}) | "
                f"TTS(avg={_fmt_ms(ts.avg)}, p95={_fmt_ms(ts.p95)}, n={ts.n})"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
