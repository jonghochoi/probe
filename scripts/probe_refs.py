#!/usr/bin/env python3
"""Shared `D#` / `P#` citation regexes and Decision-Log harvesting.

The Decision Log lives per pillar in `context/P<m>.md` §3, one entry shaped
`#### [D<n>] <title> (P<m>)` (CLAUDE.md "Decision-Log entry format"). Two
consumers read it:

  - `check-decision-refs.py` — needs {n: pillar} to lint citations.
  - `build-site.py` — needs {n: (pillar, title)} so a bare `D30` in prose can
    render as a tooltip carrying the decision's actual title.

Keeping one parser here stops the two from disagreeing about what counts as a
citation. Not executable — import it.
"""

from __future__ import annotations

import glob
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# `#### [D<n>] <title> (P<m>)` — the title is everything up to the trailing
# `(P<m>)` marker; an `— **OPEN**` suffix stays part of the title on purpose,
# since an open decision should read as open in the tooltip too.
_HEADING = re.compile(
    r"^####\s*\[D(\d{1,2})\]\s*(.*?)\s*(?:\(P(\d)\))?\s*$",
    re.MULTILINE,
)
_PILLAR_FILE = re.compile(r"^P(\d)\.md$")

# A citation: D + 1-2 digits, not embedded in a longer alphanumeric token.
_DREF = re.compile(r"(?<![A-Za-z0-9_])D(\d{1,2})(?![\d])")
# An explicit pillar/decision tie: `P1 / D4`, `P4 D22` (badge pairs are covered
# by the existence check on their D token).
_PAIR = re.compile(r"(?<![A-Za-z0-9_])P(\d)\s*(?:/\s*)?D(\d{1,2})(?![\d])")
# Paper-internal designators — `Fig. D2` is a figure label, not a Decision.
_DESIGNATOR = re.compile(
    r"(?:Fig\.?|Figure|Table|Tab\.?|Eq\.?|Equation|App\.?|Appendix|Sec\.?|Section|§)\s*$",
    re.IGNORECASE,
)

# A pillar citation: P + one digit on a word boundary.
_PREF = re.compile(r"(?<![A-Za-z0-9_])P([0-5])(?![\dA-Za-z])")

PILLAR_TITLES = {
    0: "VLA Datasets & Benchmarks",
    1: "Heterogeneous Body/Hand Action Expert",
    2: "Structured Multimodal Observation Fusion",
    3: "Hand-level System0 Module",
    4: "Pretraining for Data-Efficient Adaptation",
    5: "World Model",
}


def harvest_decisions() -> dict[int, tuple[int, str]]:
    """Return {decision_number: (owning_pillar, title)} from context/P*.md §3.

    The owning pillar comes from the filename, not the `(P<m>)` suffix, so a
    mis-typed suffix cannot silently reassign a decision — that mismatch is
    `check-decision-refs.py`'s ALLOCATION check to report, not this parser's to
    paper over.
    """
    out: dict[int, tuple[int, str]] = {}
    for path in sorted(glob.glob(os.path.join(REPO_ROOT, "context", "P*.md"))):
        m = _PILLAR_FILE.match(os.path.basename(path))
        if not m:  # _TEMPLATE.md and friends
            continue
        pillar = int(m.group(1))
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        for h in _HEADING.finditer(text):
            n = int(h.group(1))
            title = (h.group(2) or "").strip()
            if n in out and out[n][0] != pillar:
                print(
                    f"context: D{n} defined in both P{out[n][0]} and P{pillar} "
                    f"— duplicate allocation"
                )
            out[n] = (pillar, title)
    return out


def harvest_decision_log() -> dict[int, int]:
    """Return {decision_number: owning_pillar} — the lint's narrower view."""
    return {n: pillar for n, (pillar, _title) in harvest_decisions().items()}


def is_designator_label(line: str, start: int) -> bool:
    """True when the match at `start` follows a Fig./Table/§ designator."""
    return bool(_DESIGNATOR.search(line[:start]))
