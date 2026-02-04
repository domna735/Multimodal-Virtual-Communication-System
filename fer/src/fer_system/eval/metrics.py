from __future__ import annotations

import numpy as np


def accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float((y_true == y_pred).mean())


def macro_f1(y_true: np.ndarray, y_pred: np.ndarray, num_classes: int) -> float:
    # Manual macro-F1 to avoid heavy dependencies at runtime.
    f1s: list[float] = []
    for c in range(num_classes):
        tp = float(((y_true == c) & (y_pred == c)).sum())
        fp = float(((y_true != c) & (y_pred == c)).sum())
        fn = float(((y_true == c) & (y_pred != c)).sum())

        precision = tp / (tp + fp + 1e-12)
        recall = tp / (tp + fn + 1e-12)
        f1 = (2 * precision * recall) / (precision + recall + 1e-12)
        f1s.append(float(f1))
    return float(np.mean(f1s))


def brier_score(y_true: np.ndarray, probs: np.ndarray) -> float:
    # y_true: (N,), probs: (N, C)
    n, c = probs.shape
    y_onehot = np.zeros((n, c), dtype=np.float32)
    y_onehot[np.arange(n), y_true] = 1.0
    return float(np.mean(np.sum((probs - y_onehot) ** 2, axis=1)))


def expected_calibration_error(
    y_true: np.ndarray,
    probs: np.ndarray,
    n_bins: int = 15,
) -> float:
    confidences = probs.max(axis=1)
    predictions = probs.argmax(axis=1)
    accuracies = (predictions == y_true).astype(np.float32)

    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        lo, hi = bin_edges[i], bin_edges[i + 1]
        mask = (confidences > lo) & (confidences <= hi)
        if not np.any(mask):
            continue
        bin_acc = float(np.mean(accuracies[mask]))
        bin_conf = float(np.mean(confidences[mask]))
        ece += (mask.mean()) * abs(bin_acc - bin_conf)
    return float(ece)
