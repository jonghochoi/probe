#!/usr/bin/env python3
"""Extract metrics from a wandb offline run dir into CSV + summary.json.

wandb's offline mode writes a binary transaction log (``run-*.wandb``) plus a
``files/`` dir; without an internet ``wandb sync``, the human-readable
``wandb-summary.json`` is often missing. This tool reads the binary directly
via ``wandb.sdk.internal.datastore.DataStore`` and emits:

  <out>/metrics.csv   — wide CSV, one row per logged step (history records)
  <out>/summary.json  — last value of each metric (synthesised from history)

Pure offline; no cloud calls. Requires the ``wandb`` package (already in the
training extra).

Usage:
  python parse_wandb_offline.py outputs/s1_base/wandb/latest-run    -o outputs/tb/s1_base
  python parse_wandb_offline.py outputs/s1_enhance/wandb/latest-run -o outputs/tb/s1_enhance
"""
import argparse
import csv
import json
import sys
from pathlib import Path


def _decode_value(s: str):
    try:
        return json.loads(s)
    except Exception:  # noqa: BLE001
        return s


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dir", type=Path, help="wandb offline run dir (contains run-*.wandb)")
    ap.add_argument("-o", "--out", type=Path, required=True, help="output dir for metrics.csv + summary.json")
    args = ap.parse_args()

    matches = list(args.run_dir.glob("run-*.wandb"))
    if not matches:
        # latest-run is usually a symlink; try following it.
        if args.run_dir.is_symlink():
            matches = list(args.run_dir.resolve().glob("run-*.wandb"))
    if not matches:
        print(f"no run-*.wandb in {args.run_dir}", file=sys.stderr)
        sys.exit(1)
    wandb_file = str(matches[0])

    try:
        from wandb.sdk.internal.datastore import DataStore
    except Exception as e:  # noqa: BLE001
        print(f"failed to import wandb internals ({e}); install wandb", file=sys.stderr)
        sys.exit(1)

    ds = DataStore()
    ds.open_for_scan(wandb_file)

    history: list[dict] = []
    summary: dict = {}
    while True:
        rec = ds.scan_record()
        if rec is None:
            break
        if rec.HasField("history"):
            row = {item.key: _decode_value(item.value_json) for item in rec.history.item}
            history.append(row)
            summary.update(row)  # last write wins -> final summary
        elif rec.HasField("summary"):
            for item in rec.summary.update:
                summary[item.key] = _decode_value(item.value_json)

    args.out.mkdir(parents=True, exist_ok=True)
    csv_path = args.out / "metrics.csv"
    summary_path = args.out / "summary.json"

    if history:
        keys: list[str] = sorted({k for r in history for k in r.keys()})
        with csv_path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(history)
    with summary_path.open("w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"wrote {len(history)} step rows -> {csv_path}")
    print(f"wrote {len(summary)} summary keys -> {summary_path}")


if __name__ == "__main__":
    main()
