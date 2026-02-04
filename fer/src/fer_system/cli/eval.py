from __future__ import annotations

import argparse
from pathlib import Path

import torch
import yaml
from torch.utils.data import DataLoader

from fer_system.data.datasets import build_imagefolder_datasets
from fer_system.data.transforms import AugmentConfig, build_eval_transforms
from fer_system.eval.evaluate import evaluate
from fer_system.models.backbones import create_student_vit_tiny
from fer_system.utils import resolve_path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--checkpoint", required=False, help="(Optional) path to a model checkpoint")
    args = ap.parse_args()

    cfg_path = resolve_path(args.config)
    with cfg_path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    dataset_root = resolve_path(raw["dataset_root"])
    batch_size = int(raw.get("batch_size", 32))
    num_workers = int(raw.get("num_workers", 2))

    aug_cfg = AugmentConfig(image_size=int(raw.get("image_size", 224)))
    eval_tf = build_eval_transforms(aug_cfg)

    _, val_ds, spec = build_imagefolder_datasets(dataset_root, train_transform=eval_tf, val_transform=eval_tf)

    loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers, pin_memory=True)

    model = create_student_vit_tiny(num_classes=spec.num_classes, pretrained=False)
    if args.checkpoint:
        ckpt_path = resolve_path(args.checkpoint)
        state = torch.load(ckpt_path, map_location="cpu")
        if isinstance(state, dict) and "state_dict" in state:
            state = state["state_dict"]
        model.load_state_dict(state, strict=False)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    res = evaluate(model, loader, num_classes=spec.num_classes, device=device)
    print(res)


if __name__ == "__main__":
    main()
