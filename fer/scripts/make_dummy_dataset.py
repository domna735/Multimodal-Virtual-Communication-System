from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="Output dataset root")
    ap.add_argument("--classes", type=int, default=7)
    ap.add_argument("--train", type=int, default=80, help="Images per class")
    ap.add_argument("--val", type=int, default=20, help="Images per class")
    ap.add_argument("--size", type=int, default=224)
    args = ap.parse_args()

    out = Path(args.out).resolve()
    (out / "train").mkdir(parents=True, exist_ok=True)
    (out / "val").mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(0)

    for split, n_per_class in [("train", args.train), ("val", args.val)]:
        for c in range(args.classes):
            cls_dir = out / split / f"class_{c}"
            cls_dir.mkdir(parents=True, exist_ok=True)
            for i in range(n_per_class):
                arr = (rng.random((args.size, args.size, 3)) * 255).astype(np.uint8)
                img = Image.fromarray(arr)
                img.save(cls_dir / f"img_{i}.jpg", quality=95)

    print(f"Wrote dummy dataset to: {out}")


if __name__ == "__main__":
    main()
