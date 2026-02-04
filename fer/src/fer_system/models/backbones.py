from __future__ import annotations

from dataclasses import dataclass

import timm
import torch
import torch.nn as nn


@dataclass(frozen=True)
class BackboneOut:
    features: torch.Tensor
    logits: torch.Tensor


class TimmBackbone(nn.Module):
    def __init__(self, model_name: str, num_classes: int, pretrained: bool = True):
        super().__init__()
        self.model = timm.create_model(model_name, pretrained=pretrained, num_classes=num_classes)

    def forward(self, x: torch.Tensor) -> BackboneOut:
        logits = self.model(x)
        # timm models often expose forward_features; use if present
        if hasattr(self.model, "forward_features"):
            features = self.model.forward_features(x)
            # Some models return (B,C,H,W); pool to (B,C)
            if features.ndim == 4:
                features = features.mean(dim=(2, 3))
        else:
            # Fallback: treat logits as features (not ideal but keeps pipeline runnable)
            features = logits
        return BackboneOut(features=features, logits=logits)


def create_teacher(name: str, num_classes: int, pretrained: bool = True) -> nn.Module:
    return TimmBackbone(model_name=name, num_classes=num_classes, pretrained=pretrained)


def create_student_vit_tiny(num_classes: int, pretrained: bool = True) -> nn.Module:
    # timm vit_tiny_patch16_224 is a good lightweight baseline
    return TimmBackbone(model_name="vit_tiny_patch16_224", num_classes=num_classes, pretrained=pretrained)
