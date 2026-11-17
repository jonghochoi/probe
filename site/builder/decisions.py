"""Harvest the open questions so a bare `D<n>` in prose can carry its title.

The open questions live per pillar in `context/P<m>.md`, one entry shaped
`#### [D<n>] <title> (P<m>)` (context/CLAUDE.md "Open-question entry format"). The site
reads it to turn every `D<n>` citation in a rewrite into a tooltip naming the
question the citation bears on.

`linters/check-decision-refs.py` lints the same citations across the whole repo
and parses the log itself: it must run without the site's build dependencies,
so the two parsers stay separate on purpose.
"""

from __future__ import annotations

import re

from .corpus import REPO_ROOT

# `#### [D<n>] <title> (P<m>)` — the title, a pillar's open question, is
# everything up to the trailing `(P<m>)` marker.
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

    A retired code is never re-issued, and `linters/check-decision-refs.py`
    keeps it out of published documents; one that reaches a build anyway is
    set aside here rather than weighed or listed as a live question. Only the `D<digit><two capitals>` form is
    returned: it is the only form the site's citation regex matches, so a
    numeric id on the line has nothing here to resolve.
    """
    text = (REPO_ROOT / "context" / "MASTER.md").read_text(encoding="utf-8")
    m = _RETIRED_LINE.search(text)
    return set(_CODE.findall(m.group(1))) if m else set()


# A pillar's optional Korean introduction: one blockquote in its file whose
# first line opens `> **소개** —` (context/CLAUDE.md "Pillar introduction").
_INTRO = re.compile(r"^> \*\*소개\*\* —[ \t]*(.*(?:\n>.*)*)", re.MULTILINE)
_OWNER = re.compile(r"\s*\(P\d\)\s*$")


def pillar_cards() -> dict[str, dict]:
    """{`P<m>`: {"intro": str, "decisions": [[id, title]]}} — what an axis
    chip's popup says about its axis: the owner's introduction where the file
    has one, and the open questions it keeps, in file order.
    """
    out: dict[str, dict] = {}
    for path in sorted((REPO_ROOT / "context").glob("P*.md")):
        m = _PILLAR_FILE.match(path.name)
        if not m:
            continue
        text = path.read_text(encoding="utf-8")
        intro = _INTRO.search(text)
        intro_text = ""
        if intro:
            lines = [l.lstrip(">").strip() for l in intro.group(1).splitlines()]
            intro_text = " ".join(l for l in lines if l)
        decisions = []
        for h in _HEADING.finditer(text):
            title = (h.group(2) or "").strip()
            decisions.append([h.group(1), _OWNER.sub("", title)])
        out[f"P{m.group(1)}"] = {"intro": intro_text, "decisions": decisions}
    return out
