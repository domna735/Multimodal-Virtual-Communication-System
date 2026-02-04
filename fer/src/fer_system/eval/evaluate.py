from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from fer_system.eval.metrics import brier_score, expected_calibration_error, macro_f1
from fer_system.models.backbones import BackboneOut


@dataclass(frozen=True)
class EvalResults:
    acc: float
    macro_f1: float
    ece: float
    brier: float


@torch.no_grad()
def evaluate(
    model: torch.nn.Module,
    loader: DataLoader,
    num_classes: int,
    device: torch.device,
) -> EvalResults:
    model.eval()
    y_true: list[int] = []
    y_prob: list[np.ndarray] = []

    for xb, yb in tqdm(loader, desc="eval"):
        xb = xb.to(device, non_blocking=True)
        yb = yb.to(device, non_blocking=True)

        out: BackboneOut = model(xb)
        probs = torch.softmax(out.logits, dim=1)

        y_true.extend(yb.cpu().numpy().tolist())
        y_prob.extend(probs.cpu().numpy())

    y_true_arr = np.asarray(y_true, dtype=np.int64)
    y_prob_arr = np.asarray(y_prob, dtype=np.float32)
    y_pred_arr = y_prob_arr.argmax(axis=1)

    acc = float((y_pred_arr == y_true_arr).mean())
    mf1 = macro_f1(y_true_arr, y_pred_arr, num_classes=num_classes)
    ece = expected_calibration_error(y_true_arr, y_prob_arr)
    brier = brier_score(y_true_arr, y_prob_arr)
    return EvalResults(acc=acc, macro_f1=mf1, ece=ece, brier=brier)
