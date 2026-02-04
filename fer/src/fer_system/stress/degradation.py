from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
import torch


@dataclass(frozen=True)
class DegradationConfig:
    jpeg_quality: int | None = 40
    gaussian_blur_ksize: int | None = 5
    gaussian_noise_std: float | None = 0.02


def degrade_batch(x: torch.Tensor, cfg: DegradationConfig) -> torch.Tensor:
    """Apply simple image degradations on a normalized tensor batch.

    Input/Output: torch float tensor in CHW, already normalized.

    NOTE: This is a simple stress-test. For best results, apply degradations pre-normalization.
    """
    if x.ndim != 4:
        raise ValueError("Expected NCHW tensor")

    # Move to CPU numpy for OpenCV ops
    x_cpu = x.detach().cpu()
    out = []

    for img in x_cpu:
        # unnormalize approximately to 0..1 is not possible without mean/std; keep in -inf..inf.
        # We instead map through a sigmoid-ish clamp to get something image-like.
        img01 = torch.clamp((img - img.min()) / (img.max() - img.min() + 1e-6), 0.0, 1.0)
        np_img = (img01.permute(1, 2, 0).numpy() * 255.0).astype(np.uint8)

        if cfg.gaussian_blur_ksize is not None and cfg.gaussian_blur_ksize >= 3:
            k = int(cfg.gaussian_blur_ksize)
            if k % 2 == 0:
                k += 1
            np_img = cv2.GaussianBlur(np_img, (k, k), 0)

        if cfg.jpeg_quality is not None:
            q = int(np.clip(cfg.jpeg_quality, 5, 100))
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), q]
            ok, enc = cv2.imencode(".jpg", np_img, encode_param)
            if ok:
                np_img = cv2.imdecode(enc, cv2.IMREAD_COLOR)

        if cfg.gaussian_noise_std is not None and cfg.gaussian_noise_std > 0:
            noise = np.random.normal(0.0, float(cfg.gaussian_noise_std), size=np_img.shape).astype(np.float32)
            np_img = np.clip(np_img.astype(np.float32) / 255.0 + noise, 0.0, 1.0)
            np_img = (np_img * 255.0).astype(np.uint8)

        out_img = torch.from_numpy(np_img).permute(2, 0, 1).float() / 255.0
        out.append(out_img)

    out_t = torch.stack(out, dim=0)
    return out_t.to(x.device)
