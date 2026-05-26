#!/usr/bin/env python3
"""Emit the two controlled foundry-mapping agent prompts for an a-axis ablation.

The a-axis ablation (PROTOCOL.md) compares a *design-only* mapping (a1) against
a *context-rich* mapping (a2) to test H_context — whether the analysis->design
filtering drops load-bearing detail. The two agents must differ ONLY in their
input corpus and use identical task wording, so this script templates the
prompts from one source and fills in the paper id. Run it, then spawn two
isolated agents with the printed prompts.

    python3 scripts/foundry-ablation/prep_ablation.py <arxiv-id> [--foundry lerobot] [--base pi0]

Exits non-zero if the paper lacks both an analysis and a design (ablation needs
both — a1 reads the design, a2 reads both).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ANALYSIS = REPO_ROOT / "analysis"

# Shared task body — IDENTICAL across a1/a2 so only the corpus differs.
TASK = """\
TASK: Decide how you would implement the paper's core add-on module on the \
`{base}` base of the `{foundry}` foundry (the module that branches the action \
expert's shared latent into per-limb/sub pathways with auxiliary heads + a \
fused main head, or this paper's equivalent). Report ONLY these decision \
points, each with a one-line justification AND an explicit tag:
  - `[SPECIFIED: where]`  if a source pins it (cite the section), or
  - `[ASSUMED: reason]`   if you had to choose.

  1. The per-limb encoder MLP: input dim, HIDDEN layer width, output dim.
  2. The auxiliary loss weight (lambda) in L_total = L_main + lambda*(aux): value.
  3. The action-vector DoF split used for the index masks (arm_dim / hand_dim
     or this paper's equivalent).
  4. The shared-latent dim d_s: what foundry quantity does it bind to?

Report in under 250 words as a compact list. Do NOT write code or files — just
the four decisions + justifications + tags. {paper_clause}"""

FORBIDDEN = """\
STRICTLY FORBIDDEN — do not open, grep, or look at any of these (it invalidates
the experiment, they contain the answer):
  - /home/user/probe/analysis/{id}/impl/**
  - /home/user/probe/analysis/{id}/audit/**
  - any reference repository that already implements this paper (e.g. a fork
    under /home/user/ other than the probe repo itself)"""

A1 = """\
You are a scoped sub-task in a controlled experiment. Read ONLY the sources I name.

CONTEXT: /home/user/probe maps paper Designs onto the vendored `{foundry}`
foundry. You are the `/foundry` mapping step for arXiv:{id} on the `{base}` base.

ALLOWED SOURCES (read ONLY these):
  - /home/user/probe/analysis/{id}/design.md   (the Layer-1 Design — your spec)
  - /home/user/probe/vendor/{foundry}/policies/{base}/   (the foundry base, to ground dims)

{forbidden}

{task}"""

A2 = """\
You are a scoped sub-task in a controlled experiment. Read ONLY the sources I name.

CONTEXT: /home/user/probe maps paper Designs onto the vendored `{foundry}`
foundry. You are the `/foundry` mapping step for arXiv:{id} on the `{base}` base.

ALLOWED SOURCES (read ONLY these):
  - /home/user/probe/analysis/{id}/design.md   (the Layer-1 Design)
  - /home/user/probe/analysis/{id}/analysis.md (the FULL deep-dive analysis — richer than the Design)
  - /home/user/probe/vendor/{foundry}/policies/{base}/   (the foundry base)
  - You MAY fetch the actual paper if reachable: arXiv:{id}
    (https://arxiv.org/abs/{id}). If blocked, rely on the analysis and say so.

{forbidden}

{task}"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("arxiv_id")
    ap.add_argument("--foundry", default="lerobot")
    ap.add_argument("--base", default="pi0")
    args = ap.parse_args()

    design = ANALYSIS / args.arxiv_id / "design.md"
    analysis = ANALYSIS / args.arxiv_id / "analysis.md"
    missing = [str(p.relative_to(REPO_ROOT)) for p in (design, analysis) if not p.is_file()]
    if missing:
        sys.stderr.write(
            f"error: ablation needs both files; missing: {', '.join(missing)}\n"
        )
        return 2

    forbidden = FORBIDDEN.format(id=args.arxiv_id)
    task_a1 = TASK.format(base=args.base, foundry=args.foundry, paper_clause="")
    task_a2 = TASK.format(
        base=args.base,
        foundry=args.foundry,
        paper_clause="State whether you could fetch the paper.",
    )
    common = dict(id=args.arxiv_id, foundry=args.foundry, base=args.base, forbidden=forbidden)

    print("=" * 72)
    print(f"a1 (design-only) — spawn an isolated agent with this prompt:")
    print("=" * 72)
    print(A1.format(task=task_a1, **common))
    print()
    print("=" * 72)
    print(f"a2 (context-rich) — spawn an isolated agent with this prompt:")
    print("=" * 72)
    print(A2.format(task=task_a2, **common))
    print()
    print("=" * 72)
    print("After both agents report, log with:")
    print(f"  python3 scripts/foundry-ablation/ablation_ledger.py add <sample.json>")
    print("  (record schema: ablation_ledger.py --schema)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
