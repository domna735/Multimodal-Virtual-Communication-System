from __future__ import annotations

import dataclasses
import os
import random
from pathlib import Path
from typing import Any

import numpy as np
import torch


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def resolve_path(path: str | os.PathLike[str]) -> Path:
    return Path(path).expanduser().resolve()


@dataclasses.dataclass(frozen=True)
class AverageMeter:
    total: float = 0.0
    count: int = 0

    def update(self, value: float, n: int = 1) -> "AverageMeter":
        return AverageMeter(total=self.total + value * n, count=self.count + n)

    @property
    def avg(self) -> float:
        return self.total / max(1, self.count)


def to_device(batch: Any, device: torch.device) -> Any:
    if torch.is_tensor(batch):
        return batch.to(device, non_blocking=True)
    if isinstance(batch, (list, tuple)):
        return type(batch)(to_device(x, device) for x in batch)
    if isinstance(batch, dict):
        return {k: to_device(v, device) for k, v in batch.items()}
    return batch
