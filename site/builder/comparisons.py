"""Discover the comparisons the site publishes.

A comparison reads two or three papers against each other and says where they
diverge. It is a track of its own — `comparison/<slug>.md`, written by `/compare`
the way `analysis/<id>.md` is written by `/analyze` — and one constraint shapes
everything about it:

    **only papers that already have a rewrite may be compared.**

That is a discipline before it is a check. A paper's own detail belongs to its
own page, where a reader who wants more can go; the comparison stays on the
divergence and links out for everything else. A compared paper with no rewrite
would have nowhere to link, so the comparison would have to carry that paper's
detail itself — and the track's premise would be gone. So a comparison naming a
paper the corpus does not have is **not published**, rather than published with
a dead reference.

The slug is the comparison's question, not its member list: three ids run to
forty characters, their order has no right answer, and what identifies a
comparison is what it asks.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from . import corpus, frontmatter

COMPARISON_DIR = corpus.REPO_ROOT / "comparison"

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
# `<id>v<n>` — the exact arXiv edition read, one per compared paper. The bare
# id is what links; the version is what makes the reading reproducible.
SOURCE_RE = re.compile(r"^(\d{4}\.\d{4,5})v(\d+)$")

COMPARE_MIN, COMPARE_MAX = 2, 3


@dataclass
class Comparison:
    slug: str
    path: Path
    front: dict
    body: str

    @property
    def title(self) -> str:
        return self.front.get("title", "") or self.slug

    @property
    def tagline(self) -> str:
        return self.front.get("tagline", "")

    @property
    def paper_ids(self) -> list[str]:
        return frontmatter.as_list(self.front.get("compares", ""))

    @property
    def sources(self) -> list[str]:
        return frontmatter.as_list(self.front.get("sources", ""))

    @property
    def pillars(self) -> list[str]:
        return corpus.PILLAR_RE.findall(self.front.get("pillars", ""))

    @property
    def tags(self) -> list[str]:
        return frontmatter.as_list(self.front.get("tags", ""))

    @property
    def summary_md(self) -> str:
        return self.front.get("summary", "")

    @property
    def preview(self) -> str:
        return corpus._plain(self.front.get("summary", ""))

    @property
    def generated_at(self) -> str:
        m = corpus._GENERATED.match(self.front.get("generated", "").strip())
        return f"{m.group(1)} {m.group(2) or '00:00'}" if m else ""

    @property
    def date(self) -> str:
        return self.generated_at[:10]

    @property
    def order_key(self) -> tuple[str, str]:
        """Newest first under `reverse=True`.

        `generated:` alone, unlike a rewrite's git-landing rank. The reason the
        rewrites need the walk — that a redone one should land again at the top
        of a list a reader scans daily — has no counterpart here: comparisons
        are few and are not the page anyone opens first.
        """
        return (self.generated_at, self.slug)


def discover(papers_by_id: dict) -> tuple[list[Comparison], list[str]]:
    """Every `comparison/<slug>.md`, plus the problems found reading them.

    A problem that would publish a broken page skips the document; the rest are
    reported and the document still builds, so one soft slip does not take the
    whole comparison off the site.
    """
    comps: list[Comparison] = []
    problems: list[str] = []
    if not COMPARISON_DIR.is_dir():
        return comps, problems

    for path in sorted(COMPARISON_DIR.glob("*.md")):
        name = path.name
        if name == "AUTHORING.md":
            continue
        slug = path.stem
        if not SLUG_RE.match(slug):
            problems.append(
                f"comparison/{name}: name is not a slug — lowercase words joined "
                f"by hyphens, drawn from the question the comparison asks"
            )
            continue
        try:
            front, body = frontmatter.parse(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            problems.append(f"comparison/{name}: {exc}")
            continue

        comp = Comparison(slug=slug, path=path, front=front, body=body)

        ids = comp.paper_ids
        if not COMPARE_MIN <= len(ids) <= COMPARE_MAX:
            problems.append(
                f"comparison/{name}: `compares` names {len(ids)} papers — "
                f"{COMPARE_MIN}–{COMPARE_MAX}. Two is a contrast and three is a "
                f"field; four is a survey and wants a different shape"
            )
            continue
        # The track's constraint, and the reason it is a skip rather than a
        # warning: without the rewrite there is nowhere to send a reader who
        # wants this paper's detail, so the comparison would have to carry it.
        missing = [pid for pid in ids if pid not in papers_by_id]
        if missing:
            problems.append(
                f"comparison/{name}: {', '.join(missing)} has no rewrite in "
                f"`analysis/` — not published. A comparison links out for every "
                f"paper's own detail, so every compared paper needs a page to "
                f"link to. Run `/analyze` on it first, or compare other papers"
            )
            continue
        if len(set(ids)) != len(ids):
            problems.append(f"comparison/{name}: `compares` names the same paper twice")
            continue

        problems += _check_sources(name, ids, comp.sources)
        for required in ("title", "tagline", "summary"):
            if not front.get(required):
                problems.append(f"comparison/{name}: missing `{required}`")
        if not corpus._GENERATED.match(front.get("generated", "").strip()):
            problems.append(
                f"comparison/{name}: `generated` is "
                f"{front.get('generated', '')!r} — write it as `YYYY-MM-DD HH:MM`"
            )
        comps.append(comp)

    return comps, problems


def _check_sources(name: str, ids: list[str], sources: list[str]) -> list[str]:
    """`sources:` is `compares:` with the edition stated, in the same order.

    Which version was read is the one fact a comparison cannot recover later,
    and pairing it positionally with `compares:` means neither list can drift
    without the other noticing.
    """
    if not sources:
        return [
            f"comparison/{name}: missing `sources` — the arXiv edition read for "
            f"each paper, as `<id>v<n>`, in the order `compares` names them"
        ]
    if len(sources) != len(ids):
        return [
            f"comparison/{name}: `sources` has {len(sources)} entries for "
            f"{len(ids)} papers — one edition per compared paper"
        ]
    problems = []
    for pid, src in zip(ids, sources):
        m = SOURCE_RE.match(src)
        if not m:
            problems.append(
                f"comparison/{name}: `sources` entry {src!r} is not `<id>v<n>`"
            )
        elif m.group(1) != pid:
            problems.append(
                f"comparison/{name}: `sources` is out of step with `compares` — "
                f"{src!r} sits where {pid} does"
            )
    return problems


def for_paper(paper_id: str, comps: list[Comparison]) -> list[Comparison]:
    """The comparisons this paper appears in, newest first."""
    hits = [c for c in comps if paper_id in c.paper_ids]
    return sorted(hits, key=lambda c: c.order_key, reverse=True)
