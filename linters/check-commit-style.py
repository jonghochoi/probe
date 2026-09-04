#!/usr/bin/env python3
"""Check a commit subject / PR title against the CLAUDE.md commit style.

CLAUDE.md ("Commit message style") pins an exact subject grammar and calls the
imperative-verb rule "the one that drifts most easily" — yet nothing enforced
any of it. This lint validates one or more subjects against the mechanical
half of the rules (grammar shape, type set, casing, length, punctuation) plus
a blocklist of the common non-imperative offenders. It cannot prove a verb is
imperative; it catches the drift patterns the doc itself names.

Accepted shapes:

  <type>(<scope>): <description>        type in feat|fix|refactor|docs|chore|
  <type>: <description>                 style|deps
  scout: P<N> report YYYY-MM-DD         generated routine commits, formats per
  analysis: add|update <id> rewrite …  CLAUDE.md "generated routine commits"
  analysis: add|update <id> facts …     (a facts backfill of a landed rewrite)
  compare: add|update <slug>            (the scouting routine, /analyze,
  stress: YYYY-MM memo                  /compare, the monthly stress test)

Checked for the human shapes: allowed type; description starts lowercase; no
trailing period; ≤72 chars total; no manual "(#NN)" suffix (GitHub appends the
PR number on squash-merge); first word not an obvious non-imperative
(added/adding/updates/…).

Usage:
    python3 linters/check-commit-style.py "<subject>" [...]
    git log --format=%s main..HEAD | python3 linters/check-commit-style.py -

Exit codes: 0 = all subjects pass / 1 = violation(s) / 2 = nothing to check.
"""
from __future__ import annotations

import re
import sys

_TYPES = "feat|fix|refactor|docs|chore|style|deps"

_HUMAN = re.compile(rf"^({_TYPES})(\(([^)\s]+)\))?: (.+)$")

_GENERATED = [
    re.compile(r"^scout: P\d report \d{4}-\d{2}-\d{2}$"),
    re.compile(r"^analysis: (add|update) \S+ (rewrite|facts).*"),
    # The slug is the comparison's question, so it carries no alias and there
    # is nothing to say after it — a subject that keeps going is describing
    # the comparison, which the file already does.
    re.compile(r"^compare: (add|update) [a-z0-9]+(-[a-z0-9]+)*$"),
    # One memo per month, named by the month it covers — the memo is the only
    # thing the run produces, so the subject carries nothing else.
    re.compile(r"^stress: \d{4}-\d{2} memo$"),
]

# Common non-imperative first words seen in the wild (past tense, gerund,
# 3rd person). Deliberately small — precision over recall.
_NON_IMPERATIVE = {
    "added", "adds", "adding",
    "fixed", "fixes", "fixing",
    "removed", "removes", "removing",
    "updated", "updates", "updating", "update",
    "changed", "changes", "changing",
    "renamed", "renames", "renaming",
    "moved", "moves", "moving",
    "improved", "improves", "improving",
    "refactored", "refactoring",
    "new",
}


def check_subject(subject: str) -> list[str]:
    problems: list[str] = []
    s = subject.rstrip("\n")
    if not s.strip():
        return ["empty subject"]

    if any(p.match(s) for p in _GENERATED):
        return []

    m = _HUMAN.match(s)
    if not m:
        return [
            "does not match `<type>(<scope>): <description>` "
            f"(type in {_TYPES}) or a documented generated-commit format"
        ]

    desc = m.group(4)
    if len(s) > 72:
        problems.append(f"subject is {len(s)} chars (limit 72)")
    if desc[0].isupper():
        problems.append("description must start lowercase (imperative verb)")
    if desc.rstrip().endswith("."):
        problems.append("no trailing period")
    if re.search(r"\(#\d+\)\s*$", desc):
        problems.append(
            "drop the manual (#NN) — GitHub appends the PR number on squash-merge"
        )
    first = re.split(r"[\s:]", desc, 1)[0].lower()
    if first in _NON_IMPERATIVE:
        problems.append(
            f'first word "{first}" is not an imperative verb '
            "(use add/fix/remove/rename/move/refactor/… per CLAUDE.md)"
        )
    return problems


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if args == ["-"]:
        subjects = [l for l in sys.stdin.read().splitlines() if l.strip()]
    else:
        subjects = args
    if not subjects:
        sys.stderr.write("[check-commit-style] nothing to check\n")
        return 2

    total = 0
    for s in subjects:
        for problem in check_subject(s):
            total += 1
            print(f"{s!r}: {problem}")
    if total:
        print(f"\n[check-commit-style] {total} violation(s) in {len(subjects)} subject(s)")
        return 1
    print(f"[check-commit-style] clean — {len(subjects)} subject(s) checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
