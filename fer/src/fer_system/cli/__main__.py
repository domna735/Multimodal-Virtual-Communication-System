from __future__ import annotations

import argparse

from fer_system.cli.eval import main as eval_main
from fer_system.cli.train import main as train_main


def main() -> None:
    ap = argparse.ArgumentParser(prog="fer_system")
    sub = ap.add_subparsers(dest="cmd", required=True)

    train_p = sub.add_parser("train")
    train_p.add_argument("--config", required=True)

    eval_p = sub.add_parser("eval")
    eval_p.add_argument("--config", required=True)
    eval_p.add_argument("--checkpoint", required=False)

    args, unknown = ap.parse_known_args()

    if args.cmd == "train":
        train_main()
    elif args.cmd == "eval":
        eval_main()
    else:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
