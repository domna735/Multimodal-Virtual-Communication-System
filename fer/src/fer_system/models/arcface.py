from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F


class ArcFaceHead(nn.Module):
    """ArcFace classification head.

    This head expects normalized features and uses an angular margin.
    Use it as an optional replacement for the plain linear classifier.
    """

    def __init__(self, in_features: int, num_classes: int, s: float = 30.0, m: float = 0.50):
        super().__init__()
        self.in_features = in_features
        self.num_classes = num_classes
        self.s = s
        self.m = m

        self.weight = nn.Parameter(torch.empty(num_classes, in_features))
        nn.init.xavier_uniform_(self.weight)

        self.cos_m = math.cos(m)
        self.sin_m = math.sin(m)
        self.th = math.cos(math.pi - m)
        self.mm = math.sin(math.pi - m) * m

    def forward(self, features: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        # Normalize features and weights
        x = F.normalize(features)
        w = F.normalize(self.weight)

        cosine = F.linear(x, w).clamp(-1.0, 1.0)
        sine = torch.sqrt(torch.clamp(1.0 - cosine * cosine, min=0.0))

        phi = cosine * self.cos_m - sine * self.sin_m
        phi = torch.where(cosine > self.th, phi, cosine - self.mm)

        one_hot = torch.zeros_like(cosine)
        one_hot.scatter_(1, labels.view(-1, 1), 1.0)

        logits = (one_hot * phi) + ((1.0 - one_hot) * cosine)
        logits = logits * self.s
        return logits
