"""The corpus-wide glossary, harvested from the rewrites themselves.

Every ` ```probe-term ` fence in `analysis/` is already a definition written
for a reader who hit the word mid-sentence (R4). Collected across the corpus
they are also the site's second entry point: someone who arrives asking what
action chunking is does not yet know which paper to open.

Nothing new is authored for this page. The fence stays where it is, rendered
in place on the paper page as before; this module only reads the same fences a
second time and groups them by id, so a term defined in three rewrites lands as
one entry with three sources rather than three near-duplicates.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .mdext.probefence import FenceError, parse

# `` ```probe-term `` … `` ``` ``. Bodies contain no fence of their own — the
# payload is JSON — so the non-greedy match to the next closing fence is exact.
_FENCE = re.compile(r"^```probe-term\s*\n(.*?)^```", re.S | re.M)

# A term body may anchor another term (`[inpainting](term:inpaint)`). On a
# paper page that opens the panel below the paragraph; on this page every
# definition is already present, so the anchor becomes an in-page jump instead
# of a button whose panel lives in another document.
_ANCHOR = re.compile(r"\]\(term:([^)]+)\)")


@dataclass
class Term:
    tid: str
    title: str
    body: str
    sources: list = field(default_factory=list)   # [(stem, paper title)]

    @property
    def anchor(self) -> str:
        return f"t-{self.tid}"

    @property
    def sort_key(self) -> tuple:
        # Latin acronyms first (VLA, AdaLN), then Korean — the corpus is Korean
        # prose about English-named machinery, and a reader scanning for a term
        # is almost always scanning for the English one.
        head = self.title[:1]
        return (0 if head.isascii() and head.isalnum() else 1, self.title.lower())


def collect(papers: list) -> list[Term]:
    """Every distinct term in the corpus, one entry per id.

    Two rewrites defining the same term differently is the expected case, not a
    fault: each definition is written for the paragraph it sits under, so
    `flow matching` explained inside a latency paper says something the same
    term inside a force-control paper does not. The glossary shows the **most
    recently written** one and lists every rewrite that defines it, so the
    reader can go read the version written for the context they care about.

    A malformed fence is already reported by that paper's own render pass and
    is skipped here rather than warned about twice.
    """
    found: dict[str, Term] = {}
    written: dict[str, str] = {}          # tid → date of the shown definition
    for paper in papers:
        for match in _FENCE.finditer(paper.body):
            try:
                data = parse("probe-term", match.group(1))
            except FenceError:
                continue
            tid = str(data.get("id", "")).strip()
            body = str(data.get("body", "")).strip()
            if not tid or not body:
                continue
            title = str(data.get("title", "")).strip() or tid
            entry = found.get(tid)
            if entry is None:
                found[tid] = Term(tid=tid, title=title, body=body,
                                  sources=[(paper.stem, paper.title)])
                written[tid] = paper.date
                continue
            entry.sources.append((paper.stem, paper.title))
            if paper.date > written[tid]:
                entry.title, entry.body = title, body
                written[tid] = paper.date

    return sorted(found.values(), key=lambda t: t.sort_key)


def body_md(term: Term) -> str:
    """The definition as markdown, with cross-term anchors made local."""
    return _ANCHOR.sub(r"](#t-\1)", term.body)
