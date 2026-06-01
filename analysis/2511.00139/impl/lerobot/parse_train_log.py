#!/usr/bin/env python3
"""Convert lerobot stdout train logs to TensorBoard events + CSV.

Reads lines like:
  INFO ... lerobot_train.py:488 step:200 smpl:400 ep:3 epch:0.13 \
    loss:3.207 grdn:6.314 lr:1.3e-05 updt_s:0.800 data_s:0.007
and writes:
  <out>/events.out.tfevents.*   (TensorBoard scalars under train/<metric>)
  <out>/train.csv               (one row per logged step)

Pure stdlib + torch (which the lerobot venv already has); no extra installs
needed to PRODUCE these files. Viewing the TB events needs `tensorboard` on
the viewer machine, e.g.:
  tensorboard --logdir outputs/tb

Usage:
  python parse_train_log.py outputs/s1_base.log    -o outputs/tb/s1_base
  python parse_train_log.py outputs/s1_enhance.log -o outputs/tb/s1_enhance
"""
import argparse
import csv
import re
import sys
from pathlib import Path

LINE = re.compile(
    r"step:(?P<step>\d+)\s+"
    r"smpl:(?P<smpl>\d+)\s+"
    r"ep:(?P<ep>\d+)\s+"
    r"epch:(?P<epch>[-\d.eE+]+)\s+"
    r"loss:(?P<loss>[-\d.eE+]+)\s+"
    r"grdn:(?P<grdn>[-\d.eE+]+)\s+"
    r"lr:(?P<lr>[-\d.eE+]+)\s+"
    r"updt_s:(?P<updt_s>[-\d.eE+]+)\s+"
    r"data_s:(?P<data_s>[-\d.eE+]+)"
)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("log", type=Path, help="lerobot train stdout log (tee'd to a file)")
    ap.add_argument("-o", "--out", type=Path, required=True, help="output dir for TB events + train.csv")
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)

    # Lazy import so this script still works to write CSV if torch missing.
    try:
        from torch.utils.tensorboard import SummaryWriter

        writer = SummaryWriter(str(args.out))
    except Exception as e:  # noqa: BLE001
        print(f"warn: torch.utils.tensorboard unavailable ({e}); will only write CSV", file=sys.stderr)
        writer = None

    rows = []
    for line in args.log.read_text().splitlines():
        m = LINE.search(line)
        if not m:
            continue
        d = m.groupdict()
        step = int(d["step"])
        record = {
            "step": step,
            "sample": int(d["smpl"]),
            "episode": int(d["ep"]),
            "epoch": float(d["epch"]),
            "loss": float(d["loss"]),
            "grad_norm": float(d["grdn"]),
            "lr": float(d["lr"]),
            "update_s": float(d["updt_s"]),
            "data_s": float(d["data_s"]),
        }
        rows.append(record)
        if writer is not None:
            for k in ("loss", "grad_norm", "lr", "update_s", "data_s"):
                writer.add_scalar(f"train/{k}", record[k], step)
            writer.add_scalar("train/sample", record["sample"], step)
            writer.add_scalar("train/episode", record["episode"], step)
            writer.add_scalar("train/epoch", record["epoch"], step)

    if writer is not None:
        writer.close()

    csv_path = args.out / "train.csv"
    if rows:
        with csv_path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    print(f"wrote {len(rows)} step rows -> {args.out} (TB events + {csv_path.name})")


if __name__ == "__main__":
    main()
