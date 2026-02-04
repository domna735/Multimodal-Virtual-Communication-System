from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from torch.utils.data import Sampler


@dataclass(frozen=True)
class ImbalanceConfig:
    minority_fraction: float = 0.3
    minority_classes: int = 2


class ImbalancedSubsetSampler(Sampler[int]):
    """Sampler that down-samples a subset of classes to simulate imbalance."""

    def __init__(self, targets: list[int] | np.ndarray, cfg: ImbalanceConfig, seed: int = 42):
        self.targets = np.asarray(targets, dtype=np.int64)
        self.cfg = cfg
        self.seed = seed

        classes = np.unique(self.targets)
        rng = np.random.default_rng(seed)
        self.minority = set(rng.choice(classes, size=min(cfg.minority_classes, len(classes)), replace=False).tolist())

        indices = []
        for c in classes:
            cls_idx = np.where(self.targets == c)[0]
            if c in self.minority:
                k = max(1, int(len(cls_idx) * cfg.minority_fraction))
                cls_idx = rng.choice(cls_idx, size=k, replace=False)
            indices.extend(cls_idx.tolist())

        rng.shuffle(indices)
        self.indices = indices

    def __iter__(self):
        return iter(self.indices)

    def __len__(self) -> int:
        return len(self.indices)
