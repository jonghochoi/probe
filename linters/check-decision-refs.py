#!/usr/bin/env python3
"""Check that D# decision citations in agent outputs resolve to the Decision Log.

The Decision Log is allocated per pillar (a section of `context/P#.md`, entries shaped
`#### [D<n>] <title> (P<m>)` — see context/CLAUDE.md "Decision-Log entry format"), and
analysis / scouting outputs cite decisions constantly (`P1 / D9ZP`,
`[![D6JW]](…)`, "feeds P4 D9QJ"). Nothing verified those citations: a mistyped
id, or a decision moved between pillars, went undetected.
This lint closes that gap with two checks:

  1. EXISTENCE — every `D<n>` token cited in a scanned doc must exist in some
     pillar's Decision Log, or be listed in `_RETIRED` below.
  2. ALLOCATION — every explicit `P<m> / D<n>` pairing must agree with the
     owning pillar of `D<id>` (a `P1 / D9KS` tie is wrong when D9KS belongs to
     P3).

Precision over recall (mirroring check-doc-links.py): only `D` + digit + two
letters counts (a camera name like `D435` never matches, and neither does a
model name like `DINO`), and
matches immediately preceded by figure/table/appendix designators (`Fig. D2`,
`Appendix D1`) are skipped — those are paper-internal labels, not Decision
citations.

Usage (repo root):
    python3 linters/check-decision-refs.py [PATH ...]

No PATH -> scan the default set: `analysis/*.md`, `scouting/P*/*.md`,
`comparison/*.md` and `decisions/*.md` (templates excluded — they carry
`D<a>`-style placeholders and illustrative ids; a track's `AUTHORING.md` and
`SETUP.md` are its contract and its operator guide, not its documents). The
generated `decisions/MAP.md` IS scanned: it names every live id, so a decision
that leaves `context/` is caught there on the next build.

Exit codes: 0 = clean / 1 = bad citation(s) found / 2 = no Decision Log parsed.
"""
from __future__ import annotations

import glob
import os
import re
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Decisions dropped from `context/` while documents citing them stay published,
# in either id form — retirement is about the decision, not about how it is
# written. A dated scouting report records what a run concluded, and a rewrite's
# act 4 argues from the log as it stood; erasing the citation would rewrite the
# conclusion rather than the reference. A retired id resolves here and is never
# re-issued — the authoring prompts read `context/`, so they only ever cite live
# decisions.
_RETIRED = {
    "D17": "contact sub-loop RL policy spec — the stack states no learning signal for the loop",
    "D18": "that spec's sim2real",
    "D6ZD": "the sub-loop's gate — settled before D5DQ asked whether the loop earns a place",
    "D4NT": "what that gated loop reads",
    "D5QT": "what it emits",
}

# Numeric ids predate the current scheme. Only the retired two may still appear;
# any other is a citation the migration missed.
_OLD_FORM = re.compile(r"(?<![A-Za-z0-9_])(D\d{1,2})(?![A-Za-z0-9])")

_HEADING = re.compile(r"^####\s*\[(D\d[A-Z]{2})\]", re.MULTILINE)
_PILLAR_FILE = re.compile(r"^P(\d)\.md$")

# A citation: D + 1-2 digits, not embedded in a longer alphanumeric token.
_DREF = re.compile(r"(?<![A-Za-z0-9_])(D\d[A-Z]{2})(?![A-Za-z0-9])")
# An explicit pillar/decision tie: `P1 / D9ZP`, `P4 D9QJ`, `P1 · D9ZP` — the middle
# dot is the separator the Korean output actually uses (badge pairs are covered
# by the existence check on their D token).
_PAIR = re.compile(r"(?<![A-Za-z0-9_])P(\d)\s*(?:[/·]\s*)?(D\d[A-Z]{2})(?![A-Za-z0-9])")
# Paper-internal designators — `Fig. D2` is a figure label, not a Decision.
_DESIGNATOR = re.compile(
    r"(?:Fig\.?|Figure|Table|Tab\.?|Eq\.?|Equation|App\.?|Appendix|Sec\.?|Section|§)\s*$",
    re.IGNORECASE,
)


def harvest_decision_log() -> dict[str, int]:
    """Return {decision_id: owning_pillar} from context/P*.md headings."""
    owners: dict[str, int] = {}
    for path in sorted(glob.glob(os.path.join(_REPO_ROOT, "context", "P*.md"))):
        m = _PILLAR_FILE.match(os.path.basename(path))
        if not m:  # _TEMPLATE.md and friends
            continue
        pillar = int(m.group(1))
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        for h in _HEADING.finditer(text):
            n = h.group(1)
            if n in owners and owners[n] != pillar:
                print(
                    f"context: {n} defined in both P{owners[n]} and P{pillar} "
                    f"— duplicate allocation"
                )
            owners[n] = pillar
    return owners


def _is_designator_label(line: str, start: int) -> bool:
    return bool(_DESIGNATOR.search(line[:start]))


def check_file(path: str, owners: dict[str, int]) -> list[tuple[int, str]]:
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
            n = m.group(1)
            if n not in owners and n not in _RETIRED:
                findings.append((lineno, f"{n} cited but not in any Decision Log"))
        for m in _OLD_FORM.finditer(line):
            if _is_designator_label(line, m.start()):
                continue
            n = m.group(1)
            if n not in _RETIRED:
                findings.append(
                    (lineno, f"{n} is an old numeric id — ids are D + digit + two letters")
                )
        for m in _PAIR.finditer(line):
            if _is_designator_label(line, m.start()):
                continue
            pillar, n = int(m.group(1)), m.group(2)
            if n in owners and owners[n] != pillar:
                findings.append(
                    (lineno, f"P{pillar} / {n} tie — {n} belongs to P{owners[n]}")
                )
    return findings


def _gather_default_docs() -> list[str]:
    patterns = [
        "analysis/*.md",
        "scouting/P*/*.md",
        # A comparison's act 4 is our layer and cites the log like any rewrite.
        "comparison/*.md",
        # The stress-test memos and the generated map, which name ids directly.
        "decisions/*.md",
    ]
    docs: list[str] = []
    for pat in patterns:
        for path in sorted(glob.glob(os.path.join(_REPO_ROOT, pat), recursive=True)):
            rel = os.path.relpath(path, _REPO_ROOT)
            if f"{os.sep}templates{os.sep}" in rel or rel.startswith("templates"):
                continue
            # The track's format contract and its operator guide, not its documents.
            if os.path.basename(rel) in ("AUTHORING.md", "SETUP.md"):
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
        f"{len(owners)} live decision(s) and {len(_RETIRED)} retired"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
