#!/usr/bin/env python3
"""Check that D# decision citations in agent outputs resolve to the Decision Log.

The Decision Log is allocated per pillar (`context/P#.md` §3, entries shaped
`#### [D<n>] <title> (P<m>)` — see CLAUDE.md "Decision-Log entry format"), and
analysis / scouting outputs cite decisions constantly (`P1 / D4`,
`[![D6]](…)`, "feeds P4 D22"). Nothing verified those citations: a typo'd
`D14` in a P1 doc, or a decision renumbered in `context/`, went undetected.
This lint closes that gap with two checks:

  1. EXISTENCE — every `D<n>` token cited in a scanned doc must exist in some
     pillar's Decision Log.
  2. ALLOCATION — every explicit `P<m> / D<n>` pairing must agree with the
     owning pillar of `D<n>` (a `P1 / D14` tie is wrong when D14 belongs to
     P3).

Precision over recall (mirroring check-doc-links.py): only 1-2 digit `D<n>`
tokens on a word boundary count (a camera name like `D435` never matches), and
matches immediately preceded by figure/table/appendix designators (`Fig. D2`,
`Appendix D1`) are skipped — those are paper-internal labels, not Decision
citations.

Usage (repo root):
    python3 scripts/check-decision-refs.py [PATH ...]

No PATH -> scan the default set: `analysis/*.md` and `scouting/P*/*.md`
(templates excluded — they carry `D<a>`-style placeholders and illustrative
ids; the `analysis_legacy/` corpus is excluded too — it is a static folder, not
a doc a `context/` edit should be able to break).

Exit codes: 0 = clean / 1 = bad citation(s) found / 2 = no Decision Log parsed.
"""
from __future__ import annotations

import glob
import os
import re
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_HEADING = re.compile(r"^####\s*\[D(\d{1,2})\]", re.MULTILINE)
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


def harvest_decision_log() -> dict[int, int]:
    """Return {decision_number: owning_pillar} from context/P*.md §3 headings."""
    owners: dict[int, int] = {}
    for path in sorted(glob.glob(os.path.join(_REPO_ROOT, "context", "P*.md"))):
        m = _PILLAR_FILE.match(os.path.basename(path))
        if not m:  # _TEMPLATE.md and friends
            continue
        pillar = int(m.group(1))
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        for h in _HEADING.finditer(text):
            n = int(h.group(1))
            if n in owners and owners[n] != pillar:
                print(
                    f"context: D{n} defined in both P{owners[n]} and P{pillar} "
                    f"— duplicate allocation"
                )
            owners[n] = pillar
    return owners


def _is_designator_label(line: str, start: int) -> bool:
    return bool(_DESIGNATOR.search(line[:start]))


def check_file(path: str, owners: dict[int, int]) -> list[tuple[int, str]]:
    findings: list[tuple[int, str]] = []
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.readlines()
    except OSError as e:
        return [(0, f"<could not read: {e}>")]

    for lineno, line in enumerate(lines, start=1):
        for m in _DREF.finditer(line):
            if _is_designator_label(line, m.start()):
                continue
            n = int(m.group(1))
            if n not in owners:
                findings.append((lineno, f"D{n} cited but not in any Decision Log"))
        for m in _PAIR.finditer(line):
            if _is_designator_label(line, m.start()):
                continue
            pillar, n = int(m.group(1)), int(m.group(2))
            if n in owners and owners[n] != pillar:
                findings.append(
                    (lineno, f"P{pillar} / D{n} tie — D{n} belongs to P{owners[n]}")
                )
    return findings


def _gather_default_docs() -> list[str]:
    patterns = [
        "analysis/*.md",
        "scouting/P*/*.md",
    ]
    docs: list[str] = []
    for pat in patterns:
        for path in sorted(glob.glob(os.path.join(_REPO_ROOT, pat), recursive=True)):
            rel = os.path.relpath(path, _REPO_ROOT)
            if f"{os.sep}templates{os.sep}" in rel or rel.startswith("templates"):
                continue
            docs.append(rel)
    return docs


def main(argv: list[str] | None = None) -> int:
    args = (argv if argv is not None else sys.argv[1:])
    owners = harvest_decision_log()
    if not owners:
        sys.stderr.write("[check-decision-refs] no Decision Log entries parsed from context/\n")
        return 2

    docs = args or _gather_default_docs()
    total = 0
    for doc in docs:
        for lineno, msg in check_file(os.path.join(_REPO_ROOT, doc), owners):
            total += 1
            print(f"{doc}:{lineno}: {msg}")

    if total:
        print(f"\n[check-decision-refs] {total} bad citation(s) across {len(docs)} doc(s)")
        return 1
    print(
        f"[check-decision-refs] clean — {len(docs)} doc(s) scanned against "
        f"{len(owners)} decisions (D{min(owners)}–D{max(owners)})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
