#!/usr/bin/env python3
"""Compare a base pi0 run against a pi0_enhance run, fairly and per region.

Consumes the per-run outputs of ``parse_wandb_offline.py`` (``summary.json``
+ ``metrics.csv``) and reports the *dimension-homomorphic* comparison the
paper (2511.00139) actually calls for.

Trap 1 — wrong scalar: enhance's ``train/loss`` is the composite
``L_main + lambda*(L_arm + L_hand)``, NOT comparable to base's main-only
``train/loss``. ``PI0EnhancePolicy.forward`` logs ``loss_main`` /
``loss_main_per_dim`` so a like-for-like comparison is possible:

  scalar      base train/loss          <-> enhance train/loss_main
  per-dim     base train/loss_per_dim  <-> enhance train/loss_main_per_dim

Trap 2 — wrong regions: the action vector is NOT "arm then all-hand". For
Dexora (39-DoF) the documented layout (train_dexora.md, build_index_masks)
is left/right arm + left/right hand + head/spine, and only arm/hand get aux
supervision. Folding head/spine into "hand", or not splitting L/R, hides the
left/right asymmetry that dominates a single-task run. So regions are an
explicit, overridable map rather than a single arm/hand boundary.

  --regions name:start:end,name:start:end,...

Region names ending in ``_L`` / ``_R`` are rolled up to a parent group
(``hand_L`` + ``hand_R`` -> ``hand``) for a both-sides summary row. Default
is the Dexora 39-DoF layout; override for any other embodiment.

Pure stdlib; no plotting dependency. Emits a Markdown table to stdout and,
with -o, an aligned step-wise ``compare.csv`` (base loss vs enhance
loss_main over ``_step``) for whatever plotting you prefer.

Usage:
  python compare_runs.py outputs/tb/s1_base outputs/tb/s1_enhance
  python compare_runs.py outputs/tb/s1_base outputs/tb/s1_enhance --per-dim \
      -o outputs/tb/compare.csv
  python compare_runs.py base enh --regions arm:0:12,hand:12:36,head_spine:36:39
"""
import argparse
import csv
import json
import math
import re
import sys
from collections import OrderedDict
from pathlib import Path

# Dexora 39-DoF action layout (train_dexora.md "데이터 차원" table):
# arm 6+6, hand 12+12 (xhand), head 2 + spine 1. Only arm/hand get aux loss.
DEFAULT_REGIONS = "arm_L:0:6,arm_R:6:12,hand_L:12:24,hand_R:24:36,head_spine:36:39"


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


def _window_means(run_dir: Path, scalar_key: str, pd_prefix: str, frac: float):
    """Mean of the last ``frac`` of metrics.csv steps — robust to the per-step
    noise that makes a single summary.json snapshot unreliable.

    Returns (scalar_mean, per_dim_means, window_rows, total_rows).
    """
    p = run_dir / "metrics.csv"
    if not p.exists():
        print(f"no metrics.csv in {run_dir} (needed for --window)", file=sys.stderr)
        sys.exit(1)
    with p.open() as f:
        rows = [r for r in csv.DictReader(f) if r.get("_step")]
    if not rows:
        return None, [], 0, 0
    rows.sort(key=lambda r: float(r["_step"]))
    w = max(1, math.ceil(len(rows) * frac))
    last = rows[-w:]

    def cmean(k: str):
        xs = [float(r[k]) for r in last if r.get(k) not in (None, "")]
        return sum(xs) / len(xs) if xs else None

    scalar = cmean(scalar_key)
    prefix = pd_prefix + "/"
    vals: dict[int, float] = {}
    for k in last[0]:
        if k.startswith(prefix):
            tail = k[len(prefix):]
            if tail.isdigit():
                v = cmean(k)
                if v is not None:
                    vals[int(tail)] = v
    pd_list = [vals[i] for i in range(max(vals) + 1)] if vals else []
    return scalar, pd_list, w, len(rows)


def _parse_regions(spec: str) -> list[tuple[str, int, int]]:
    out: list[tuple[str, int, int]] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            name, start, end = part.rsplit(":", 2)
            out.append((name, int(start), int(end)))
        except ValueError:
            print(f"bad --regions entry {part!r}; want name:start:end", file=sys.stderr)
            sys.exit(1)
    return out


def _fmt(x, nd: int = 5) -> str:
    return f"{x:.{nd}f}" if isinstance(x, (int, float)) else "—"


def _stats(base_pd: list[float], enh_pd: list[float], idxs: list[int]):
    """Mean of base/enhance over idxs (clamped to both lengths) + win count."""
    idxs = [i for i in idxs if i < len(base_pd) and i < len(enh_pd)]
    if not idxs:
        return None, None, 0, 0
    b = sum(base_pd[i] for i in idxs) / len(idxs)
    e = sum(enh_pd[i] for i in idxs) / len(idxs)
    wins = sum(1 for i in idxs if enh_pd[i] < base_pd[i])
    return b, e, wins, len(idxs)


def _row(label: str, span: str, base, enh, wins: int, n: int) -> str:
    if base is None or enh is None:
        return f"| {label} | {span} | — | — | — | — | — |"
    d = enh - base
    pct = (d / base * 100) if base else float("nan")
    tag = "🟢" if d < 0 else "🔴"  # lower loss = better
    return (f"| {label} | {span} | {_fmt(base)} | {_fmt(enh)} | "
            f"{d:+.5f} | {tag} {pct:+.1f}% | {wins}/{n} |")


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
    ap.add_argument("--regions", default=DEFAULT_REGIONS,
                    help=f"comma list of name:start:end; names ending _L/_R roll up. Default: {DEFAULT_REGIONS}")
    ap.add_argument("--window", type=float, default=None, metavar="FRAC",
                    help="average the last FRAC (0-1] of metrics.csv steps instead of using the "
                         "single summary.json snapshot — robust to per-step noise (e.g. 0.2)")
    ap.add_argument("--per-dim", action="store_true", help="also print the full per-dim table with region labels")
    ap.add_argument("-o", "--out", type=Path, default=None, help="write aligned step-wise compare.csv here")
    args = ap.parse_args()

    if args.window is not None:
        if not 0 < args.window <= 1:
            print("--window must be in (0, 1]", file=sys.stderr)
            sys.exit(1)
        base_scalar, base_pd, bw, bn = _window_means(args.base_dir, "train/loss", "train/loss_per_dim", args.window)
        enh_scalar, enh_pd, ew, en = _window_means(args.enhance_dir, "train/loss_main", "train/loss_main_per_dim", args.window)
        if enh_scalar is None or not enh_pd:
            fs, fp, ew, en = _window_means(args.enhance_dir, "train/loss", "train/loss_per_dim", args.window)
            if enh_scalar is None:
                enh_scalar = fs
                print("warning: enhance run has no train/loss_main; falling back to "
                      "composite train/loss — NOT a fair comparison (see --help)", file=sys.stderr)
            if not enh_pd:
                enh_pd = fp
        source = f"metrics.csv 마지막 {args.window:.0%} 윈도우 평균 (base {bw}/{bn}, enh {ew}/{en} steps)"
    else:
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
        source = "summary.json (최종 스텝 1개 — 노이즈 주의, --window 권장)"

    active = min(len(base_pd), len(enh_pd))

    regions = _parse_regions(args.regions)
    # Coverage check against active dims — catches a wrong embodiment/layout.
    covered = {i for _, s, e in regions for i in range(s, e)}
    gap = sorted(set(range(active)) - covered)
    if gap:
        print(f"warning: dims {gap} are in the data but not covered by --regions", file=sys.stderr)

    # Group L/R regions under a parent for roll-up rows.
    groups: "OrderedDict[str, list[tuple[str, int, int]]]" = OrderedDict()
    for name, s, e in regions:
        parent = re.sub(r"_(L|R)$", "", name)
        groups.setdefault(parent, []).append((name, s, e))

    print("# base vs enhance — fair comparison (loss vs loss_main), per region\n")
    print(f"- base    : `{args.base_dir}`")
    print(f"- enhance : `{args.enhance_dir}`")
    print(f"- source  : {source}")
    print(f"- active dims: `{active}`\n")
    print("| region | dims | base | enhance | Δ | 개선 | win |")
    print("|---|---|---|---|---|---|---|")
    print(_row("scalar (loss ↔ loss_main)", "—", base_scalar, enh_scalar, 0, 0)
          .replace("| 0/0 |", "| — |"))

    for parent, members in groups.items():
        if len(members) > 1:
            idxs = [i for _, s, e in members for i in range(s, e)]
            b, e_, w, n = _stats(base_pd, enh_pd, idxs)
            lo, hi = min(s for _, s, _ in members), max(e for _, _, e in members)
            print(_row(f"**{parent}**", f"[{lo}:{hi})", b, e_, w, n))
            for name, s, e in members:
                b, e_, w, n = _stats(base_pd, enh_pd, list(range(s, e)))
                print(_row(f"└ {name}", f"[{s}:{e})", b, e_, w, n))
        else:
            name, s, e = members[0]
            b, e_, w, n = _stats(base_pd, enh_pd, list(range(s, e)))
            print(_row(name, f"[{s}:{e})", b, e_, w, n))

    if args.per_dim and base_pd and enh_pd:
        dim2region = {i: name for name, s, e in regions for i in range(s, e)}
        wins = sum(1 for i in range(active) if enh_pd[i] < base_pd[i])
        print(f"\n## per-dim (enhance가 더 낮은 차원: {wins}/{active})\n")
        print("| dim | region | base | enhance | Δ |")
        print("|---|---|---|---|---|")
        for i in range(active):
            d = enh_pd[i] - base_pd[i]
            print(f"| {i} | {dim2region.get(i, '—')} | {_fmt(base_pd[i])} | {_fmt(enh_pd[i])} | {d:+.5f} |")

    if args.out:
        n = _write_curve_csv(args.base_dir, args.enhance_dir, args.out)
        print(f"\nwrote {n} aligned steps -> {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
