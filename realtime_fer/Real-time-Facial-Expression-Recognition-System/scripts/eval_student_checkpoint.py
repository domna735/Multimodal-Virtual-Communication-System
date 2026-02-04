from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch
from torch.amp import autocast
from torch.utils.data import DataLoader

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.fer.data.manifest_dataset import CANONICAL_7, ManifestImageDataset, build_splits, read_manifest  # noqa: E402

# Reuse metric logic from the training script to keep outputs consistent.
from scripts.train_student import fit_temperature, metrics_from_logits  # noqa: E402


def _pick_eval_rows(
    *,
    manifest_path: Path,
    data_root: Path,
    split: str,
    seed: int,
) -> Tuple[List[object], Dict[str, int]]:
    rows_all = read_manifest(manifest_path)
    train_rows, val_rows, test_rows = build_splits(rows_all, out_root=data_root, seed=seed)

    if split == "test":
        chosen = test_rows if test_rows else val_rows
    else:
        chosen = val_rows if val_rows else test_rows

    counts = {"train": len(train_rows), "val": len(val_rows), "test": len(test_rows), "chosen": len(chosen)}
    return list(chosen), counts


def main() -> int:
    ap = argparse.ArgumentParser(description="Evaluate a saved student checkpoint on an arbitrary manifest split (domain shift eval).")

    ap.add_argument("--checkpoint", type=Path, required=True, help="Path to a student checkpoint .pt (e.g., best.pt)")
    ap.add_argument("--eval-manifest", type=Path, required=True, help="CSV manifest to evaluate on")
    ap.add_argument("--eval-split", type=str, default="test", choices=["val", "test"], help="Split to evaluate")
    ap.add_argument("--eval-data-root", type=Path, default=REPO_ROOT, help="Data root used to resolve relative image paths")

    ap.add_argument("--model", type=str, default=None, help="Override timm model name (defaults to value stored in checkpoint)")
    ap.add_argument("--image-size", type=int, default=None, help="Override image size (defaults to value stored in checkpoint)")

    ap.add_argument("--batch-size", type=int, default=256)
    ap.add_argument("--num-workers", type=int, default=4)
    ap.add_argument("--seed", type=int, default=1337)

    ap.add_argument("--use-clahe", action="store_true", help="Force CLAHE on for eval (defaults to checkpoint args if present)")
    ap.add_argument("--clahe-clip", type=float, default=2.0)
    ap.add_argument("--clahe-tile", type=int, default=8)

    ap.add_argument("--use-amp", action="store_true", help="Use AMP autocast when on CUDA")
    ap.add_argument("--max-batches", type=int, default=0)

    ap.add_argument("--out-dir", type=Path, default=None, help="Where to write reliabilitymetrics.json (default: outputs/evals/students/...)" )

    args = ap.parse_args()

    ckpt_path: Path = args.checkpoint
    if not ckpt_path.exists():
        raise SystemExit(f"Checkpoint not found: {ckpt_path}")

    try:
        ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    except TypeError:
        ckpt = torch.load(ckpt_path, map_location="cpu")

    ckpt_args = ckpt.get("args") if isinstance(ckpt.get("args"), dict) else {}

    model_name = args.model or str(ckpt_args.get("model") or "mobilenetv3_large_100")
    image_size = int(args.image_size or ckpt_args.get("image_size") or 224)

    # Default CLAHE config from checkpoint unless user forces it.
    use_clahe = bool(args.use_clahe) or bool(ckpt_args.get("use_clahe") or False)
    clahe_clip = float(ckpt_args.get("clahe_clip") or args.clahe_clip)
    clahe_tile = int(ckpt_args.get("clahe_tile") or args.clahe_tile)

    stamp = time.strftime("%Y%m%d_%H%M%S")
    if args.out_dir is None:
        out_dir = REPO_ROOT / "outputs" / "evals" / "students" / f"{Path(ckpt_path).parent.name}__{args.eval_manifest.stem}__{args.eval_split}__{stamp}"
    else:
        out_dir = args.out_dir

    out_dir.mkdir(parents=True, exist_ok=True)

    # Device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    use_amp = bool(args.use_amp) and device.type == "cuda"

    # Transforms consistent with teacher eval transforms.
    import importlib

    train_teacher = importlib.import_module("scripts.train_teacher")
    val_tf = train_teacher.build_transforms(
        image_size=image_size,
        train=False,
        use_clahe=use_clahe,
        clahe_clip=clahe_clip,
        clahe_tile=clahe_tile,
    )

    # Eval dataset
    eval_rows, counts = _pick_eval_rows(
        manifest_path=args.eval_manifest,
        data_root=args.eval_data_root,
        split=str(args.eval_split),
        seed=int(args.seed),
    )
    if not eval_rows:
        raise SystemExit(
            f"No eval rows found for split={args.eval_split} in {args.eval_manifest}. "
            f"(counts={counts})"
        )

    eval_ds = ManifestImageDataset(eval_rows, out_root=args.eval_data_root, transform=val_tf)

    num_workers = int(args.num_workers)
    prefetch_factor = 1 if (os.name == "nt" and num_workers > 0) else 2
    dl_kwargs = {
        "batch_size": int(args.batch_size),
        "shuffle": False,
        "num_workers": num_workers,
        "pin_memory": (device.type == "cuda"),
    }
    if num_workers > 0:
        dl_kwargs["prefetch_factor"] = prefetch_factor
        dl_kwargs["persistent_workers"] = True
    eval_dl = DataLoader(eval_ds, **dl_kwargs)

    # Model
    try:
        import timm  # type: ignore
    except Exception as e:
        raise RuntimeError("timm is required for evaluation.") from e

    student = timm.create_model(model_name, pretrained=False, num_classes=len(CANONICAL_7)).to(device)
    student.load_state_dict(ckpt.get("model", {}), strict=True)
    student.eval()

    all_logits: List[torch.Tensor] = []
    all_y: List[torch.Tensor] = []

    with torch.no_grad():
        for bi, batch in enumerate(eval_dl):
            x, y, _src = batch
            x = x.to(device, non_blocking=True)
            y = y.to(device, non_blocking=True)
            with autocast(device.type if use_amp else "cpu", enabled=use_amp):
                logits = student(x)
            all_logits.append(logits.detach().float().cpu())
            all_y.append(y.detach().cpu())
            if args.max_batches and (bi + 1) >= int(args.max_batches):
                break

    logits = torch.cat(all_logits, dim=0)
    y = torch.cat(all_y, dim=0)

    raw = metrics_from_logits(logits, y, num_classes=len(CANONICAL_7))
    t_star = fit_temperature(logits, y, init_t=1.2)
    scaled_logits = logits / float(t_star)
    scaled = metrics_from_logits(scaled_logits, y, num_classes=len(CANONICAL_7))

    calib = {"mode": "global", "global_temperature": float(t_star)}
    (out_dir / "calibration.json").write_text(json.dumps(calib, indent=2), encoding="utf-8")

    rel = {
        "raw": raw,
        "temperature_scaled": {"mode": "global", "global_temperature": float(t_star), **scaled},
    }
    (out_dir / "reliabilitymetrics.json").write_text(json.dumps(rel, indent=2), encoding="utf-8")

    meta = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "checkpoint": str(ckpt_path),
        "checkpoint_run_dir": str(ckpt_path.parent),
        "model": model_name,
        "image_size": image_size,
        "use_clahe": use_clahe,
        "clahe_clip": clahe_clip,
        "clahe_tile": clahe_tile,
        "eval_manifest": str(args.eval_manifest),
        "eval_split": str(args.eval_split),
        "eval_data_root": str(args.eval_data_root),
        "counts": counts,
        "max_batches": int(args.max_batches),
    }
    (out_dir / "eval_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(json.dumps({"out_dir": str(out_dir), "raw": raw, "ts": scaled}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
