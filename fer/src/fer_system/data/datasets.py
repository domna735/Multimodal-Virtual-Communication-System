from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from torchvision.datasets import ImageFolder


@dataclass(frozen=True)
class DatasetSpec:
    train_dir: Path
    val_dir: Path
    num_classes: int
    class_to_idx: dict[str, int]


def build_imagefolder_datasets(
    dataset_root: Path,
    train_subdir: str = "train",
    val_subdir: str = "val",
    train_transform: Callable | None = None,
    val_transform: Callable | None = None,
) -> tuple[ImageFolder, ImageFolder, DatasetSpec]:
    train_dir = (dataset_root / train_subdir).resolve()
    val_dir = (dataset_root / val_subdir).resolve()

    train_ds = ImageFolder(str(train_dir), transform=train_transform)
    val_ds = ImageFolder(str(val_dir), transform=val_transform)

    if train_ds.class_to_idx != val_ds.class_to_idx:
        # Allow different folder discovery order but enforce identical mapping.
        # If mismatch, users should ensure same class folder names exist.
        raise ValueError(
            "Train/val class mappings differ. Ensure identical class folders in both splits. "
            f"train={train_ds.class_to_idx} val={val_ds.class_to_idx}"
        )

    spec = DatasetSpec(
        train_dir=train_dir,
        val_dir=val_dir,
        num_classes=len(train_ds.classes),
        class_to_idx=train_ds.class_to_idx,
    )
    return train_ds, val_ds, spec
