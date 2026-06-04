#!/usr/bin/env python3
"""Compare a base pi0 run against a pi0_enhance run, fairly.

Consumes the per-run outputs of ``parse_wandb_offline.py`` (``summary.json``
+ ``metrics.csv``) and reports the *dimension-homomorphic* comparison the
paper (2511.00139) actually calls for.

The trap this tool exists to avoid: enhance's ``train/loss`` is the composite
``L_main + lambda*(L_arm + L_hand)``, so it is NOT comparable to base's
main-only ``train/loss``. ``PI0EnhancePolicy.forward`` logs ``loss_main`` /
``loss_main_per_dim`` precisely so a like-for-like comparison is possible:

  scalar      base train/loss          <-> enhance train/loss_main
  per-dim     base train/loss_per_dim  <-> enhance train/loss_main_per_dim

Index contract (Design / build_index_masks): arm = [0, arm_dim),
hand = [arm_dim, active_dim); trailing padding is dropped. The hand-region
mean is the paper's enhancement target.

Pure stdlib; no plotting dependency. Emits a Markdown table to stdout and,
with -o, an aligned step-wise ``compare.csv`` (base loss vs enhance
loss_main over ``_step``) for whatever plotting you prefer.

Usage:
  python compare_runs.py outputs/tb/s1_base outputs/tb/s1_enhance --arm-dim 12
  python compare_runs.py outputs/tb/s1_base outputs/tb/s1_enhance --arm-dim 12 \
      --per-dim -o outputs/tb/compare.csv
"""
import argparse
import csv
import json
import sys
from pathlib import Path


def _load_summary(run_dir: Path) -> dict:
    p = run_dir / "summary.json"
    if not p.exists():
        print(f"no summary.json in {run_dir}", file=sys.stderr)
        sys.exit(1)
    with p.open() as f:
        return json.load(f)


def _scalar(summary: dict, key: str):
    v = summary.get(key)
    return float(v) if isinstance(v, (int, float)) else None


def _per_dim(summary: dict, base_key: str) -> list[float]:
    """Collect ``<base_key>/0``, ``<base_key>/1``, ... in index order."""
    vals: dict[int, float] = {}
    prefix = base_key + "/"
    for k, v in summary.items():
        if k.startswith(prefix):
            tail = k[len(prefix):]
            if tail.isdigit() and isinstance(v, (int, float)):
                vals[int(tail)] = float(v)
    if not vals:
        return []
    return [vals[i] for i in range(max(vals) + 1)]


def _mean(xs: list[float]):
    return sum(xs) / len(xs) if xs else None


def _fmt(x, nd: int = 5) -> str:
    return f"{x:.{nd}f}" if isinstance(x, (int, float)) else "—"


def _delta_row(label: str, base, enh) -> str:
    if base is None or enh is None:
        return f"| {label} | {_fmt(base)} | {_fmt(enh)} | — | — |"
    d = enh - base
    pct = (d / base * 100) if base else float("nan")
    sign = "🟢" if d < 0 else "🔴"  # lower loss = better = green
    return f"| {label} | {_fmt(base)} | {_fmt(enh)} | {d:+.5f} | {sign} {pct:+.1f}% |"


def _write_curve_csv(base_dir: Path, enh_dir: Path, out: Path) -> int:
    """Align base train/loss and enhance train/loss_main on _step."""
    def _read(d: Path, col: str) -> dict[str, str]:
        p = d / "metrics.csv"
        if not p.exists():
            return {}
        with p.open() as f:
            r = csv.DictReader(f)
            return {row["_step"]: row[col] for row in r if row.get("_step") and row.get(col)}

    base = _read(base_dir, "train/loss")
    enh = _read(enh_dir, "train/loss_main")
    steps = sorted(set(base) & set(enh), key=lambda s: float(s))
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["_step", "base_loss", "enhance_loss_main"])
        for s in steps:
            w.writerow([s, base[s], enh[s]])
    return len(steps)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("base_dir", type=Path, help="base run output dir (parse_wandb_offline.py -o target)")
    ap.add_argument("enhance_dir", type=Path, help="enhance run output dir")
    ap.add_argument("--arm-dim", type=int, default=12, help="arm = [0, arm_dim); hand = [arm_dim, active) (default 12, Dexora dual-arm)")
    ap.add_argument("--per-dim", action="store_true", help="also print the full per-dim table")
    ap.add_argument("-o", "--out", type=Path, default=None, help="write aligned step-wise compare.csv here")
    args = ap.parse_args()

    base = _load_summary(args.base_dir)
    enh = _load_summary(args.enhance_dir)

    # Scalar: base loss <-> enhance loss_main (fall back with a warning).
    base_scalar = _scalar(base, "train/loss")
    enh_scalar = _scalar(enh, "train/loss_main")
    if enh_scalar is None:
        enh_scalar = _scalar(enh, "train/loss")
        print("warning: enhance run has no train/loss_main; falling back to "
              "composite train/loss — NOT a fair comparison (see --help)", file=sys.stderr)

    # Per-dim: base loss_per_dim <-> enhance loss_main_per_dim.
    base_pd = _per_dim(base, "train/loss_per_dim")
    enh_pd = _per_dim(enh, "train/loss_main_per_dim") or _per_dim(enh, "train/loss_per_dim")

    active = min(len(base_pd), len(enh_pd)) if base_pd and enh_pd else max(len(base_pd), len(enh_pd))
    a = args.arm_dim
    base_arm, base_hand = _mean(base_pd[:a]), _mean(base_pd[a:active])
    enh_arm, enh_hand = _mean(enh_pd[:a]), _mean(enh_pd[a:active])

    print(f"# base vs enhance — fair comparison (loss vs loss_main)\n")
    print(f"- base    : `{args.base_dir}`")
    print(f"- enhance : `{args.enhance_dir}`")
    print(f"- contract: arm `[0:{a})` · hand `[{a}:{active})` · active dims `{active}`\n")
    print("| 지표 | base | enhance | Δ | 개선 |")
    print("|---|---|---|---|---|")
    print(_delta_row("scalar (loss ↔ loss_main)", base_scalar, enh_scalar))
    print(_delta_row(f"arm  mean [0:{a})", base_arm, enh_arm))
    print(_delta_row(f"hand mean [{a}:{active}) ← 표적", base_hand, enh_hand))

    if args.per_dim and base_pd and enh_pd:
        wins = sum(1 for i in range(active) if enh_pd[i] < base_pd[i])
        print(f"\n## per-dim (enhance가 더 낮은 차원: {wins}/{active})\n")
        print("| dim | region | base | enhance | Δ |")
        print("|---|---|---|---|---|")
        for i in range(active):
            region = "arm" if i < a else "hand"
            d = enh_pd[i] - base_pd[i]
            print(f"| {i} | {region} | {_fmt(base_pd[i])} | {_fmt(enh_pd[i])} | {d:+.5f} |")

    if args.out:
        n = _write_curve_csv(args.base_dir, args.enhance_dir, args.out)
        print(f"\nwrote {n} aligned steps -> {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
