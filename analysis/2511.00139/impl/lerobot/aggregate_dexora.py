#!/usr/bin/env python3
"""Aggregate several Dexora task folders into one multi-task LeRobotDataset.

This pinned lerobot keeps ``MultiLeRobotDataset`` OFF — ``datasets/factory.py``
raises ``NotImplementedError`` the moment ``dataset.repo_id`` is a list — so
training on several tasks at once means first merging them into a *single*
LeRobotDataset that carries all of their tasks. This is a thin CLI over
lerobot's own ``datasets.aggregate.aggregate_datasets``.

All source tasks must be v3.0 (convert first with ``convert_all_dexora.sh``)
and share the same fps / robot_type / features (action+state dim, camera set).
``aggregate_datasets`` validates that up front and aborts loudly otherwise, so
pick tasks whose ``act``/``state``/``cams`` columns match in ``dexora_stats.py``.
The aggregated dataset keeps one task entry per source (pi0 conditions on the
task string), so point ``DATASET_DIR`` at ``--out`` and train as usual.

Must run under the lerobot venv python (needs ``lerobot``):

  LEROBOT_PY=~/dev/lerobot/.venv/bin/python
  $LEROBOT_PY aggregate_dexora.py --out /data/.../dexora_mix \
      /data/.../dexora/unscrew_water_bottle_cap \
      /data/.../dexora/turn_rubiks_cube_bimanual \
      /data/.../dexora/write_with_pen
"""
import os

os.environ.setdefault("HF_HUB_OFFLINE", "1")  # never reach for the hub for local roots

import argparse
import json
import shutil
import sys
from pathlib import Path


def _info(task_dir: Path) -> dict:
    return json.loads((task_dir / "meta" / "info.json").read_text())


def _signature(info: dict) -> tuple:
    feats = info.get("features", {})

    def dim(key: str):
        shape = feats.get(key, {}).get("shape")
        return shape[0] if shape else None

    cams = tuple(sorted(k for k in feats if k.startswith("observation.images")))
    return (dim("action"), dim("observation.state"), cams, info.get("fps"), info.get("robot_type"))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tasks", type=Path, nargs="+", help="two or more v3.0 task dataset roots (each holds meta/info.json)")
    ap.add_argument("--out", type=Path, required=True, help="output dir for the aggregated multi-task dataset")
    ap.add_argument("--repo-id", default="Dexora/dexora_mix", help="label for the aggregated dataset (cosmetic)")
    ap.add_argument("--overwrite", action="store_true", help="replace --out if it already exists")
    args = ap.parse_args()

    if len(args.tasks) < 2:
        sys.exit("give at least two task folders to aggregate")

    # ── Pre-flight: v3.0 + a schema table so a mismatch is obvious before any copy.
    sigs = []
    for d in args.tasks:
        if not (d / "meta" / "info.json").exists():
            sys.exit(f"no meta/info.json in {d} (is it a LeRobotDataset root?)")
        info = _info(d)
        if info.get("codebase_version") != "v3.0":
            sys.exit(f"{d} is {info.get('codebase_version')!r}, not v3.0 — run convert_all_dexora.sh first")
        sigs.append(_signature(info))

    print("source tasks:")
    for d, s in zip(args.tasks, sigs):
        print(f"  {d.name:42} act={s[0]} state={s[1]} cams={len(s[2])} fps={s[3]} robot={s[4]}")
    if len(set(sigs)) > 1:
        print("\nWARNING: tasks differ in act/state/cams/fps/robot_type — aggregate_datasets "
              "requires identical features and will abort. Drop the odd ones out.", file=sys.stderr)

    if args.out.exists():
        if not args.overwrite:
            sys.exit(f"{args.out} already exists — pass --overwrite to replace it")
        shutil.rmtree(args.out)

    # ── Aggregate (validates fps/robot_type/features up front, before copying).
    from lerobot.datasets.aggregate import aggregate_datasets

    repo_ids = [d.name for d in args.tasks]
    roots = list(args.tasks)
    aggregate_datasets(repo_ids, args.repo_id, roots=roots, aggr_root=args.out)

    out = _info(args.out)
    print(f"\naggregated {len(args.tasks)} tasks -> {args.out}")
    print(f"  total_tasks={out.get('total_tasks')}  "
          f"total_episodes={out.get('total_episodes')}  total_frames={out.get('total_frames')}")
    print(f"  train with: DATASET_DIR={args.out}")


if __name__ == "__main__":
    main()
