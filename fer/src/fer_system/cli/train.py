from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import torch
import yaml
from torch.utils.data import DataLoader

from fer_system.data.datasets import build_imagefolder_datasets
from fer_system.data.transforms import AugmentConfig, build_eval_transforms, build_train_transforms
from fer_system.models.backbones import create_student_vit_tiny, create_teacher
from fer_system.training.train_loop import TeacherEnsemble, TrainConfig, train_student
from fer_system.utils import resolve_path, set_seed


@dataclass(frozen=True)
class Config:
    dataset_root: str
    batch_size: int = 32
    num_workers: int = 2
    seed: int = 42

    # Teacher models (timm names)
    teachers: list[str] = None  # type: ignore

    # Student
    student_pretrained: bool = True

    # Augment
    image_size: int = 224

    # Train
    train: TrainConfig = TrainConfig()


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, help="Path to YAML config")
    args = ap.parse_args()

    cfg_path = resolve_path(args.config)
    raw = load_config(cfg_path)

    dataset_root = resolve_path(raw["dataset_root"])
    batch_size = int(raw.get("batch_size", 32))
    num_workers = int(raw.get("num_workers", 2))
    seed = int(raw.get("seed", 42))

    teacher_names = raw.get(
        "teachers",
        ["resnet18", "tf_efficientnet_b3", "convnext_tiny"],
    )

    aug_cfg = AugmentConfig(image_size=int(raw.get("image_size", 224)))

    train_tf = build_train_transforms(aug_cfg)
    eval_tf = build_eval_transforms(aug_cfg)

    train_ds, val_ds, spec = build_imagefolder_datasets(dataset_root, train_transform=train_tf, val_transform=eval_tf)

    set_seed(seed)

    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    teachers = [create_teacher(n, num_classes=spec.num_classes, pretrained=True) for n in teacher_names]
    teacher = TeacherEnsemble(teachers)

    student = create_student_vit_tiny(num_classes=spec.num_classes, pretrained=bool(raw.get("student_pretrained", True)))

    train_cfg_raw = raw.get("train", {})
    train_cfg = TrainConfig(
        epochs=int(train_cfg_raw.get("epochs", 5)),
        lr=float(train_cfg_raw.get("lr", 3e-4)),
        weight_decay=float(train_cfg_raw.get("weight_decay", 1e-4)),
        temperature=float(train_cfg_raw.get("temperature", 4.0)),
        kd_weight=float(train_cfg_raw.get("kd_weight", 0.5)),
        use_dkd=bool(train_cfg_raw.get("use_dkd", True)),
        dkd_alpha=float(train_cfg_raw.get("dkd_alpha", 1.0)),
        dkd_beta=float(train_cfg_raw.get("dkd_beta", 6.0)),
        use_arcface=bool(train_cfg_raw.get("use_arcface", False)),
        arcface_s=float(train_cfg_raw.get("arcface_s", 30.0)),
        arcface_m=float(train_cfg_raw.get("arcface_m", 0.5)),
    )

    metrics = train_student(
        student=student,
        teacher=teacher,
        train_loader=train_loader,
        val_loader=val_loader,
        num_classes=spec.num_classes,
        cfg=train_cfg,
        device=device,
    )

    print("Best metrics:", metrics)


if __name__ == "__main__":
    main()
