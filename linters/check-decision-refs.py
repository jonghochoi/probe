#!/usr/bin/env python3
"""Check that D# citations in agent outputs resolve to the pillars' open questions.

The open questions are allocated per pillar (a section of `context/P#.md`, entries shaped
`#### [D<n>] <title> (P<m>)` — see context/CLAUDE.md "Open-question entry format"), and
analysis / scouting outputs cite them constantly (`P1 / D9ZP`,
`[![D6JW]](…)`, "feeds P4 D9QJ"). A mistyped id, or a decision moved between
pillars, is invisible on the page, so this lint runs three checks:

  1. EXISTENCE — every `D<n>` token cited in a scanned doc must exist in some
     pillar's open questions. An id on `context/MASTER.md`'s `Retired:` line is
     named as retired: a folded question's citations are rewritten to the id
     it folded into (`context/CLAUDE.md`), so none stays published.
  2. ALLOCATION — every explicit `P<m> / D<n>` pairing must agree with the
     owning pillar of `D<id>` (a `P1 / D9KS` tie is wrong when D9KS belongs to
     P3).
  3. FORM — a numeric id (`D17`) is a malformed citation; ids are `D` + digit
     + two letters.

Precision over recall (mirroring check-doc-links.py): a live id is `D` + digit
+ two capitals (a camera name like `D435` never matches, and neither does a
model name like `DINO`), and matches immediately preceded by figure/table/
appendix designators (`Fig. D2`, `Appendix D1`) are skipped — those are
paper-internal labels, not Decision citations — and so is anything inside an
inline code span, where an output puts a paper's own name shaped like a code.

Usage (repo root):
    python3 linters/check-decision-refs.py [PATH ...]

No PATH -> scan the default set: `analysis/*.md`, `scouting/P*/*.md` and
`comparison/*.md` (templates and `AUTHORING.md` excluded — they carry
`D<a>`-style placeholders and illustrative ids).

Exit codes: 0 = clean / 1 = bad citation(s) found / 2 = no open questions or no
`Retired:` line parsed.
"""
from __future__ import annotations

import glob
import os
import re
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ids of questions folded into others or dropped. `context/MASTER.md` lists
# them on its `Retired:` line (the same line `site/builder/decisions.py` reads)
# so none is re-issued; a citation of one is reported as retired rather than
# unknown, since the fix is to cite the question it folded into.
_RETIRED_LINE = re.compile(r"^Retired:(.*)$", re.MULTILINE)
_RETIRED_CODE = re.compile(r"(?<![A-Za-z0-9_])(D\d[A-Z]{2}|D\d{1,2})(?![A-Za-z0-9])")

# A live id is `D<digit><two capitals>`; the numeric form (`D17`) is malformed.
_OLD_FORM = re.compile(r"(?<![A-Za-z0-9_])(D\d{1,2})(?![A-Za-z0-9])")

_HEADING = re.compile(r"^####\s*\[(D\d[A-Z]{2})\]", re.MULTILINE)
_PILLAR_FILE = re.compile(r"^P(\d)\.md$")

# A citation: D + one digit + two capitals, not embedded in a longer alphanumeric token.
_DREF = re.compile(r"(?<![A-Za-z0-9_])(D\d[A-Z]{2})(?![A-Za-z0-9])")
# An explicit pillar/decision tie: `P1 / D9ZP`, `P4 D9QJ`, `P1 · D9ZP` — the middle
# dot is the separator the Korean output actually uses (badge pairs are covered
# by the existence check on their D token).
_PAIR = re.compile(r"(?<![A-Za-z0-9_])P(\d)\s*(?:[/·]\s*)?(D\d[A-Z]{2})(?![A-Za-z0-9])")
_CODE_SPAN = re.compile(r"`[^`\n]*`")
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


def harvest_retired() -> set[str] | None:
    """The ids on `context/MASTER.md`'s `Retired:` line, or None if it is gone."""
    try:
        with open(os.path.join(_REPO_ROOT, "context", "MASTER.md"), encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return None
    m = _RETIRED_LINE.search(text)
    return set(_RETIRED_CODE.findall(m.group(1))) if m else None


def _is_designator_label(line: str, start: int) -> bool:
    return bool(_DESIGNATOR.search(line[:start]))


def check_file(path: str, owners: dict[str, int],
               retired: set[str]) -> list[tuple[int, str]]:
    findings: list[tuple[int, str]] = []
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.readlines()
    except OSError as e:
        return [(0, f"<could not read: {e}>")]

    for lineno, raw in enumerate(lines, start=1):
        # A code span is a paper's own name (`D4RT`), never a citation.
        line = _CODE_SPAN.sub(lambda c: " " * len(c.group()), raw)
        for m in _DREF.finditer(line):
            if _is_designator_label(line, m.start()):
                continue
            n = m.group(1)
            if n in retired:
                findings.append((lineno, f"{n} is retired — cite the question it folded into"))
            elif n not in owners:
                findings.append((lineno, f"{n} cited but not in any pillar's open questions"))
        for m in _OLD_FORM.finditer(line):
            if _is_designator_label(line, m.start()):
                continue
            n = m.group(1)
            findings.append(
                (lineno, f"{n} is {'retired' if n in retired else 'a numeric id'} — ids are D + digit + two letters")
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
    ]
    docs: list[str] = []
    for pat in patterns:
        for path in sorted(glob.glob(os.path.join(_REPO_ROOT, pat), recursive=True)):
            rel = os.path.relpath(path, _REPO_ROOT)
            if f"{os.sep}templates{os.sep}" in rel or rel.startswith("templates"):
                continue
            # The track's format contract, not one of its documents.
            if os.path.basename(rel) == "AUTHORING.md":
                continue
            docs.append(rel)
    return docs


def main(argv: list[str] | None = None) -> int:
    args = (argv if argv is not None else sys.argv[1:])
    owners = harvest_decision_log()
    if not owners:
        sys.stderr.write("[check-decision-refs] no open-question entries parsed from context/\n")
        return 2
    retired = harvest_retired()
    if retired is None:
        sys.stderr.write(
            "[check-decision-refs] no `Retired:` line in context/MASTER.md — "
            "retired ids cannot be resolved\n"
        )
        return 2

    docs = args or _gather_default_docs()
    total = 0
    for doc in docs:
        for lineno, msg in check_file(os.path.join(_REPO_ROOT, doc), owners, retired):
            total += 1
            print(f"{doc}:{lineno}: {msg}")

    if total:
        print(f"\n[check-decision-refs] {total} bad citation(s) across {len(docs)} doc(s)")
        return 1
    print(
        f"[check-decision-refs] clean — {len(docs)} doc(s) scanned against "
        f"{len(owners)} live decision(s) and {len(retired)} retired"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
