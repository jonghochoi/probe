"""Harvest the Decision Log so a bare `D<n>` in prose can carry its title.

The Decision Log lives per pillar in `context/P<m>.md`, one entry shaped
`#### [D<n>] <title> (P<m>)` (context/CLAUDE.md "Decision-Log entry format"). The site
reads it to turn every `D<n>` citation in a rewrite into a tooltip naming the
decision the opinion anchors to.

`linters/check-decision-refs.py` lints the same citations across the whole repo
and parses the log itself: it must run without the site's build dependencies,
so the two parsers stay separate on purpose.
"""

from __future__ import annotations

import re

from .corpus import REPO_ROOT

# `#### [D<n>] <title> (P<m>)` — the title is everything up to the trailing
# `(P<m>)` marker; an `— **OPEN**` suffix stays part of the title on purpose,
# since an open decision should read as open in the tooltip too.
_HEADING = re.compile(
    r"^####\s*\[(D\d[A-Z]{2})\]\s*(.*?)\s*(?:\(P(\d)\))?\s*$",
    re.MULTILINE,
)
_PILLAR_FILE = re.compile(r"^P(\d)\.md$")


def harvest_decisions() -> dict[str, tuple[int, str]]:
    """Return {decision_id: (owning_pillar, title)} from context/P*.md.

    The owning pillar comes from the filename, not the `(P<m>)` suffix, so a
    mis-typed suffix cannot silently reassign a decision — that mismatch is
    `check-decision-refs.py`'s ALLOCATION check to report, not this parser's to
    paper over.
    """
    out: dict[str, tuple[int, str]] = {}
    for path in sorted((REPO_ROOT / "context").glob("P*.md")):
        m = _PILLAR_FILE.match(path.name)
        if not m:  # _TEMPLATE.md and friends
            continue
        pillar = int(m.group(1))
        text = path.read_text(encoding="utf-8")
        for h in _HEADING.finditer(text):
            n = h.group(1)
            title = (h.group(2) or "").strip()
            if n in out and out[n][0] != pillar:
                print(
                    f"context: {n} defined in both P{out[n][0]} and P{pillar} "
                    f"— duplicate allocation"
                )
            out[n] = (pillar, title)
    return out


_RETIRED_LINE = re.compile(r"^Retired:(.*)$", re.MULTILINE)
_CODE = re.compile(r"\bD\d[A-Z]{2}\b")


def retired_decisions() -> set[str]:
    """The retired codes `context/MASTER.md` lists on its `Retired:` line.

    A retired code is never re-issued and still appears in rewrites written
    before it retired, so a reader of `corpus.json` meets it with no entry in
    any pillar's Decision Log. Only the current `D<digit><two letters>` form is
    returned; the numeric forms predate the scheme and no rewrite's regex
    matches them.
    """
    text = (REPO_ROOT / "context" / "MASTER.md").read_text(encoding="utf-8")
    m = _RETIRED_LINE.search(text)
    return set(_CODE.findall(m.group(1))) if m else set()
