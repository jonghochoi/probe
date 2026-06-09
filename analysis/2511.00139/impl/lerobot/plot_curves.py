#!/usr/bin/env python3
"""Plot the control-triangle training curves + hand per-dim loss from tb/ dirs.

Consumes the ``parse_wandb_offline.py`` outputs (``metrics.csv``) of the three
control runs (base / lambda=0 / enhance) and writes the figures that back
``RESULTS.md``:

  <out>/loss_curve.png    step-wise base ``train/loss`` vs lambda0/enhance
                          ``train/loss_main`` (the fair scalar) with a light
                          rolling mean — shows convergence speed + stability.
  <out>/hand_per_dim.png  last-``window`` mean per-dim main loss on the hand
                          dims, base vs enhance (grouped bars, L/R split).

The step curve needs the per-step series that only lives in ``metrics.csv``, so
this runs on the machine that holds ``outputs/tb`` (the training box), not in
the repo checkout. ``region_decomposition.png`` is the 15 numbers straight off
``compare_runs.py`` and is committed as-is.

Run under any python with matplotlib (the lerobot venv has it):

  LEROBOT_PY=~/dev/lerobot/.venv/bin/python
  $LEROBOT_PY plot_curves.py --tb outputs/tb --out analysis/2511.00139/impl/lerobot/results \
      --base mt_base --lam0 mt_lam0 --enhance mt_enhance --window 0.2 --hand 12:36
"""
import argparse
import csv
import math
from pathlib import Path


def _series(run_dir: Path, col: str) -> tuple[list[float], list[float]]:
    """Return (steps, values) for one column of metrics.csv, step-sorted."""
    p = run_dir / "metrics.csv"
    if not p.exists():
        raise SystemExit(f"no metrics.csv in {run_dir}")
    rows = []
    with p.open() as f:
        for r in csv.DictReader(f):
            s, v = r.get("_step"), r.get(col)
            if s and v not in (None, ""):
                rows.append((float(s), float(v)))
    rows.sort(key=lambda t: t[0])
    return [s for s, _ in rows], [v for _, v in rows]


def _roll(ys: list[float], k: int) -> list[float]:
    if k <= 1 or len(ys) < k:
        return ys
    out, acc = [], 0.0
    from collections import deque
    win: deque = deque()
    for y in ys:
        win.append(y); acc += y
        if len(win) > k:
            acc -= win.popleft()
        out.append(acc / len(win))
    return out


def _window_per_dim(run_dir: Path, prefix: str, lo: int, hi: int, frac: float) -> list[float]:
    p = run_dir / "metrics.csv"
    with p.open() as f:
        rows = [r for r in csv.DictReader(f) if r.get("_step")]
    rows.sort(key=lambda r: float(r["_step"]))
    w = max(1, math.ceil(len(rows) * frac))
    last = rows[-w:]
    out = []
    for i in range(lo, hi):
        k = f"{prefix}/{i}"
        xs = [float(r[k]) for r in last if r.get(k) not in (None, "")]
        out.append(sum(xs) / len(xs) if xs else float("nan"))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tb", type=Path, required=True, help="dir holding the per-run parse_wandb_offline outputs")
    ap.add_argument("--out", type=Path, required=True, help="dir to write PNGs into")
    ap.add_argument("--base", default="mt_base")
    ap.add_argument("--lam0", default="mt_lam0")
    ap.add_argument("--enhance", default="mt_enhance")
    ap.add_argument("--window", type=float, default=0.2, help="trailing fraction for the per-dim bars")
    ap.add_argument("--hand", default="12:36", help="hand dim span start:end (default Dexora 12:36)")
    ap.add_argument("--smooth", type=int, default=9, help="rolling-mean window (in log points) for the curve")
    args = ap.parse_args()

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    args.out.mkdir(parents=True, exist_ok=True)
    lo, hi = (int(x) for x in args.hand.split(":"))

    # ── loss_curve.png : base train/loss vs lam0/enhance train/loss_main ──
    fig, ax = plt.subplots(figsize=(11, 5.5))
    for name, run, col, color in [
        (f"{args.base} (base, loss)", args.base, "train/loss", "#9aa6b2"),
        (f"{args.lam0} (lam0, loss_main)", args.lam0, "train/loss_main", "#1565c0"),
        (f"{args.enhance} (enhance, loss_main)", args.enhance, "train/loss_main", "#2e7d32"),
    ]:
        try:
            xs, ys = _series(args.tb / run, col)
        except SystemExit:
            continue
        if not ys:
            xs, ys = _series(args.tb / run, "train/loss")  # lam0/enhance fallback
        ax.plot(xs, _roll(ys, args.smooth), label=name, color=color, lw=1.8)
    ax.set_xlabel("step"); ax.set_ylabel("main loss (rolling mean)")
    ax.set_title("Control triangle: fair main-loss curves (base loss vs enhance loss_main)")
    ax.legend(); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(args.out / "loss_curve.png", dpi=130); plt.close(fig)

    # ── hand_per_dim.png : base vs enhance window-mean per-dim on hand span ──
    base_pd = _window_per_dim(args.tb / args.base, "train/loss_per_dim", lo, hi, args.window)
    enh_pd = _window_per_dim(args.tb / args.enhance, "train/loss_main_per_dim", lo, hi, args.window)
    dims = list(range(lo, hi))
    x = np.arange(len(dims)); w = 0.38
    fig, ax = plt.subplots(figsize=(13, 5))
    ax.bar(x - w / 2, base_pd, w, label="base (pi0)", color="#9aa6b2")
    ax.bar(x + w / 2, enh_pd, w, label="enhance", color="#2e7d32")
    mid = lo + (hi - lo) // 2
    ax.axvline((mid - lo) - 0.5, color="k", ls="--", lw=1, alpha=.6)
    ax.set_xticks(x); ax.set_xticklabels(dims)
    ax.set_xlabel("action dim"); ax.set_ylabel(f"main loss (last-{args.window:.0%} window mean)")
    ax.set_title("Per-dim main loss on hand region: base vs enhance (lower = better)")
    ax.legend(); ax.grid(axis="y", alpha=.3)
    fig.tight_layout(); fig.savefig(args.out / "hand_per_dim.png", dpi=130); plt.close(fig)

    print(f"wrote {args.out/'loss_curve.png'}")
    print(f"wrote {args.out/'hand_per_dim.png'}")


if __name__ == "__main__":
    main()
