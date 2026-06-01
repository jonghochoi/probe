#!/usr/bin/env python3
"""Scan a local Dexora (LeRobotDataset) tree and print per-task stats.

Reads every ``meta/info.json`` found under the given root (any depth) and
prints a table sorted by episode count, so you can pick a small task to
fine-tune on without eyeballing the HF tree. Pure stdlib; works fully offline.

Usage:
  python dexora_stats.py ~/data/Dexora_Real-World_Dataset
  python dexora_stats.py ~/data/Dexora_Real-World_Dataset --sort frames
"""
import argparse
import json
import sys
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", type=Path, help="dataset root to scan (recurses for meta/info.json)")
    ap.add_argument("--sort", choices=["episodes", "frames", "name"], default="episodes")
    ap.add_argument("--top", type=int, default=5, help="how many smallest tasks to suggest")
    args = ap.parse_args()

    infos = sorted(args.root.rglob("meta/info.json"))
    if not infos:
        print(f"no meta/info.json found under {args.root}", file=sys.stderr)
        sys.exit(1)

    rows = []
    for info_path in infos:
        ds_root = info_path.parent.parent  # <task>/meta/info.json -> <task>
        try:
            info = json.loads(info_path.read_text())
        except Exception as e:  # noqa: BLE001 - report and skip unreadable meta
            print(f"skip {info_path}: {e}", file=sys.stderr)
            continue
        feats = info.get("features", {})

        def dim(key: str) -> object:
            shape = feats.get(key, {}).get("shape")
            return shape[0] if shape else None

        cams = [k for k in feats if k.startswith("observation.images")]
        rel = str(ds_root.relative_to(args.root)) if ds_root != args.root else ds_root.name
        rows.append(
            {
                "task": rel,
                "episodes": info.get("total_episodes"),
                "frames": info.get("total_frames"),
                "fps": info.get("fps"),
                "ver": info.get("codebase_version"),
                "act": dim("action"),
                "state": dim("observation.state"),
                "cams": len(cams),
                "root": str(ds_root),
            }
        )

    sort_key = {"episodes": "episodes", "frames": "frames", "name": "task"}[args.sort]
    rows.sort(key=lambda r: (r[sort_key] is None, r[sort_key]))

    hdr = f"{'task':42} {'eps':>7} {'frames':>10} {'fps':>4} {'ver':>5} {'act':>4} {'state':>5} {'cam':>3}"
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        print(
            f"{r['task'][:42]:42} {str(r['episodes']):>7} {str(r['frames']):>10} "
            f"{str(r['fps']):>4} {str(r['ver']):>5} {str(r['act']):>4} {str(r['state']):>5} {str(r['cams']):>3}"
        )

    print(f"\nsmallest {args.top} by {args.sort} (paste into DATASET_DIR):")
    for r in rows[: args.top]:
        print(f"  DATASET_DIR={r['root']}   # episodes={r['episodes']} frames={r['frames']} act={r['act']}")


if __name__ == "__main__":
    main()
