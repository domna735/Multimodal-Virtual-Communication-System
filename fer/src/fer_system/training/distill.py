from __future__ import annotations

import torch
import torch.nn.functional as F


def kd_loss(
    student_logits: torch.Tensor,
    teacher_logits: torch.Tensor,
    temperature: float = 4.0,
) -> torch.Tensor:
    """Standard Hinton KD loss (KL divergence on softened logits)."""
    t = float(temperature)
    p_s = F.log_softmax(student_logits / t, dim=1)
    p_t = F.softmax(teacher_logits / t, dim=1)
    return F.kl_div(p_s, p_t, reduction="batchmean") * (t * t)


def dkd_loss(
    student_logits: torch.Tensor,
    teacher_logits: torch.Tensor,
    labels: torch.Tensor,
    alpha: float = 1.0,
    beta: float = 6.0,
    temperature: float = 4.0,
) -> torch.Tensor:
    """Decoupled Knowledge Distillation (DKD), simplified implementation.

    This separates distillation into:
    - TCKD: target class vs non-target classes
    - NCKD: non-target class distribution

    Based on: Zhao et al., CVPR 2022.
    """
    t = float(temperature)
    num_classes = student_logits.size(1)

    # Soft distributions
    s = F.softmax(student_logits / t, dim=1)
    te = F.softmax(teacher_logits / t, dim=1)

    # Create target mask
    target_mask = F.one_hot(labels, num_classes=num_classes).float()
    non_target_mask = 1.0 - target_mask

    # Target vs non-target probability (binary)
    s_t = (s * target_mask).sum(dim=1, keepdim=True)
    s_nt = (s * non_target_mask).sum(dim=1, keepdim=True)
    te_t = (te * target_mask).sum(dim=1, keepdim=True)
    te_nt = (te * non_target_mask).sum(dim=1, keepdim=True)

    s_bin = torch.cat([s_t, s_nt], dim=1).clamp_min(1e-8)
    te_bin = torch.cat([te_t, te_nt], dim=1).clamp_min(1e-8)

    tckd = F.kl_div(s_bin.log(), te_bin, reduction="batchmean")

    # Non-target distribution, renormalized
    s_non = (s * non_target_mask).clamp_min(1e-8)
    te_non = (te * non_target_mask).clamp_min(1e-8)

    s_non = s_non / s_non.sum(dim=1, keepdim=True).clamp_min(1e-8)
    te_non = te_non / te_non.sum(dim=1, keepdim=True).clamp_min(1e-8)

    nckd = F.kl_div(s_non.log(), te_non, reduction="batchmean")

    return (alpha * tckd + beta * nckd) * (t * t)
