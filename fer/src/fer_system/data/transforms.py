from __future__ import annotations

from dataclasses import dataclass

import torchvision.transforms as T


@dataclass(frozen=True)
class AugmentConfig:
    image_size: int = 224
    mean: tuple[float, float, float] = (0.485, 0.456, 0.406)
    std: tuple[float, float, float] = (0.229, 0.224, 0.225)


def build_train_transforms(cfg: AugmentConfig) -> T.Compose:
    return T.Compose(
        [
            T.Resize((cfg.image_size, cfg.image_size)),
            T.RandomHorizontalFlip(p=0.5),
            T.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05),
            T.ToTensor(),
            T.Normalize(mean=cfg.mean, std=cfg.std),
        ]
    )


def build_eval_transforms(cfg: AugmentConfig) -> T.Compose:
    return T.Compose(
        [
            T.Resize((cfg.image_size, cfg.image_size)),
            T.ToTensor(),
            T.Normalize(mean=cfg.mean, std=cfg.std),
        ]
    )
