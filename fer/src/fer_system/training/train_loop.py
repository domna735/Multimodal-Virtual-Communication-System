from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from tqdm import tqdm

from fer_system.models.arcface import ArcFaceHead
from fer_system.models.backbones import BackboneOut
from fer_system.training.distill import dkd_loss, kd_loss
from fer_system.utils import AverageMeter


@dataclass(frozen=True)
class TrainConfig:
    epochs: int = 10
    lr: float = 3e-4
    weight_decay: float = 1e-4
    temperature: float = 4.0
    kd_weight: float = 0.5
    use_dkd: bool = True
    dkd_alpha: float = 1.0
    dkd_beta: float = 6.0
    use_arcface: bool = False
    arcface_s: float = 30.0
    arcface_m: float = 0.50


class TeacherEnsemble(nn.Module):
    def __init__(self, teachers: list[nn.Module]):
        super().__init__()
        self.teachers = nn.ModuleList(teachers)

    @torch.no_grad()
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        logits = None
        for t in self.teachers:
            out: BackboneOut = t(x)
            logits = out.logits if logits is None else (logits + out.logits)
        return logits / len(self.teachers)


def train_student(
    *,
    student: nn.Module,
    teacher: TeacherEnsemble | None,
    train_loader: DataLoader,
    val_loader: DataLoader,
    num_classes: int,
    cfg: TrainConfig,
    device: torch.device,
) -> dict[str, float]:
    student.to(device)
    if teacher is not None:
        teacher.to(device)
        teacher.eval()

    optimizer = torch.optim.AdamW(student.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)

    arcface_head: ArcFaceHead | None = None
    if cfg.use_arcface:
        # Infer feature dim from one forward pass
        student.eval()
        xb, yb = next(iter(train_loader))
        xb = xb.to(device)
        with torch.no_grad():
            out: BackboneOut = student(xb)
        arcface_head = ArcFaceHead(
            in_features=out.features.shape[-1],
            num_classes=num_classes,
            s=cfg.arcface_s,
            m=cfg.arcface_m,
        ).to(device)
        optimizer = torch.optim.AdamW(
            list(student.parameters()) + list(arcface_head.parameters()),
            lr=cfg.lr,
            weight_decay=cfg.weight_decay,
        )
        student.train()

    best_val_acc = -1.0
    best_metrics: dict[str, float] = {}

    for epoch in range(cfg.epochs):
        student.train()
        loss_meter = AverageMeter()
        ce_meter = AverageMeter()
        kd_meter = AverageMeter()

        pbar = tqdm(train_loader, desc=f"train {epoch+1}/{cfg.epochs}")
        for xb, yb in pbar:
            xb = xb.to(device, non_blocking=True)
            yb = yb.to(device, non_blocking=True)

            out: BackboneOut = student(xb)

            if arcface_head is not None:
                logits = arcface_head(out.features, yb)
                ce = F.cross_entropy(logits, yb)
            else:
                logits = out.logits
                ce = F.cross_entropy(logits, yb)

            distill = torch.tensor(0.0, device=device)
            if teacher is not None and cfg.kd_weight > 0:
                with torch.no_grad():
                    t_logits = teacher(xb)

                if cfg.use_dkd:
                    distill = dkd_loss(
                        student_logits=logits,
                        teacher_logits=t_logits,
                        labels=yb,
                        alpha=cfg.dkd_alpha,
                        beta=cfg.dkd_beta,
                        temperature=cfg.temperature,
                    )
                else:
                    distill = kd_loss(logits, t_logits, temperature=cfg.temperature)

            loss = (1.0 - cfg.kd_weight) * ce + cfg.kd_weight * distill

            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()

            loss_meter = loss_meter.update(float(loss.item()), n=xb.size(0))
            ce_meter = ce_meter.update(float(ce.item()), n=xb.size(0))
            kd_meter = kd_meter.update(float(distill.item()), n=xb.size(0))

            pbar.set_postfix(loss=f"{loss_meter.avg:.4f}", ce=f"{ce_meter.avg:.4f}", kd=f"{kd_meter.avg:.4f}")

        # Quick val accuracy
        student.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for xb, yb in tqdm(val_loader, desc=f"val {epoch+1}/{cfg.epochs}"):
                xb = xb.to(device, non_blocking=True)
                yb = yb.to(device, non_blocking=True)
                out: BackboneOut = student(xb)
                logits = out.logits
                pred = logits.argmax(dim=1)
                correct += int((pred == yb).sum().item())
                total += int(yb.numel())

        val_acc = correct / max(1, total)
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_metrics = {"val_acc": float(val_acc)}

    return best_metrics
