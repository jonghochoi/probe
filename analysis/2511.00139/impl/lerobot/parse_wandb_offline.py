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
    ap.add_argument("--debug", action="store_true", help="dump the first history record's raw key/nested_key items to stderr")
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
        from wandb.proto.wandb_internal_pb2 import Record
        from wandb.sdk.internal.datastore import DataStore
    except Exception as e:  # noqa: BLE001
        print(f"failed to import wandb internals ({e}); install wandb", file=sys.stderr)
        sys.exit(1)

    ds = DataStore()
    ds.open_for_scan(wandb_file)

    def _bytes_to_record(data):
        if not isinstance(data, (bytes, bytearray)) or not data:
            return None
        rec = Record()
        try:
            rec.ParseFromString(bytes(data))
        except Exception:  # noqa: BLE001
            return None
        return rec

    history: list[dict] = []
    summary: dict = {}
    parse_skips = 0
    seen = 0
    first_history_dumped = False

    def _hi_key(item) -> str:
        """Resolve a HistoryItem key across wandb proto shapes.

        Newer wandb (>=0.18) stores hierarchical metric paths (e.g.
        ``train/loss``) under ``nested_key`` (a repeated string) and leaves
        ``key`` empty; older versions kept the full string in ``key``.
        """
        nk = list(getattr(item, "nested_key", []) or [])
        if nk:
            return "/".join(nk)
        return item.key or ""

    truncated = False
    while True:
        try:
            out = ds.scan_record()
        except Exception as e:  # noqa: BLE001
            # wandb's own scan_record() raises (e.g. IndexError in the crc step)
            # on a corrupt/truncated trailing record — typical of a run still in
            # progress or interrupted mid-write. Keep every complete record read
            # so far and stop cleanly instead of crashing.
            truncated = True
            print(f"stopped early at a corrupt/truncated record after {seen} records "
                  f"({type(e).__name__}); the run may still be in progress or was "
                  f"interrupted", file=sys.stderr)
            break
        if out is None:
            break
        seen += 1
        rec = None
        if hasattr(out, "HasField"):
            rec = out
        elif isinstance(out, tuple) and out:
            rec = _bytes_to_record(out[-1])
        else:
            rec = _bytes_to_record(out)
        if rec is None:
            parse_skips += 1
            continue
        if rec.HasField("history"):
            if args.debug and not first_history_dumped:
                first_history_dumped = True
                print("first history record items (diagnostic):", file=sys.stderr)
                for item in rec.history.item:
                    nk = list(getattr(item, "nested_key", []) or [])
                    val_preview = (item.value_json or "")[:60]
                    print(f"  key={item.key!r}  nested_key={nk}  value_json={val_preview!r}", file=sys.stderr)
            row = {_hi_key(item): _decode_value(item.value_json) for item in rec.history.item}
            # Drop the empty-key fallback if present (rare, defensive).
            row = {k: v for k, v in row.items() if k}
            if row:
                history.append(row)
                summary.update(row)  # last write wins -> final summary
        elif rec.HasField("summary"):
            for item in rec.summary.update:
                k = _hi_key(item)
                if k:
                    summary[k] = _decode_value(item.value_json)

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
    if parse_skips:
        print(f"note: {parse_skips}/{seen} records were unparseable and skipped", file=sys.stderr)
    if truncated:
        print("note: file ended on a truncated record — re-run after the training "
              "run finishes for the full curve", file=sys.stderr)


if __name__ == "__main__":
    main()
