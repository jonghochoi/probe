"""Discover the comparisons the site publishes.

A comparison reads two or three papers against each other and says where they
diverge — `comparison/<slug>.md`, written by `/compare`. Only papers that
already have a rewrite may be compared, so a comparison naming a paper the
corpus does not have is **not published** rather than published with a dead
reference. The slug is the comparison's question, not its member list. The
contract is `comparison/AUTHORING.md`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from . import corpus, frontmatter, primers

COMPARISON_DIR = corpus.REPO_ROOT / "comparison"

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
# `<id>v<n>` — the exact arXiv edition read, one per compared paper. The bare
# id is what links; the version is what makes the reading reproducible.
SOURCE_RE = re.compile(r"^(\d{4}\.\d{4,5})v(\d+)$")

COMPARE_MIN, COMPARE_MAX = 2, 3
# A stance is a branch label and `common` the trunk it leaves — both are read at
# a glance in a list, not down a page, so the ceilings are the width that keeps
# them on one line rather than a stylistic preference.
STANCE_MAX, COMMON_MAX = 20, 30
# `problem` is the one sentence a reader meets under the question, and each
# `plain` line sits on its paper's card — read before any term is explained, so
# a plain line carries no Latin script and no math (`comparison/AUTHORING.md`
# §2-1).
PROBLEM_MAX, PLAIN_MAX = 60, 40
_LATIN_OR_MATH = re.compile(r"[A-Za-z$\\]")


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
    def stances(self) -> list[str]:
        """What each compared paper does about the question, in `compares` order."""
        return frontmatter.as_list(self.front.get("stances", ""))

    @property
    def common(self) -> str:
        """The commitment all of them share — the trunk the stances leave."""
        return self.front.get("common", "").strip()

    @property
    def problem(self) -> str:
        """The problem every compared paper faces, in plain words."""
        return self.front.get("problem", "").strip()

    @property
    def plain(self) -> list[str]:
        """What each paper does, in everyday words, in `compares` order."""
        return frontmatter.as_list(self.front.get("plain", ""))

    @property
    def primer(self) -> list[str]:
        """The background cards the page opens on (`builder/primers.py` ids)."""
        return frontmatter.as_list(self.front.get("primer", ""))

    @property
    def pillars(self) -> list[str]:
        return corpus.PILLAR_RE.findall(self.front.get("pillars", ""))

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
        # The track's one rule (`comparison/AUTHORING.md` §1) — a skip, not a
        # warning.
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
        problems += _check_fork(name, ids, comp.stances, comp.common)
        problems += _check_plain(name, ids, comp.problem, comp.plain)
        problems += _check_primer(name, comp.primer)
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


def _check_fork(name: str, ids: list[str], stances: list[str], common: str) -> list[str]:
    """`stances` is one line per compared paper; `common` is the one they share.

    The index card draws these as a fork, so a comparison missing either one
    renders as a card that names a question and then says nothing about it.
    Both are reported rather than skipped: the comparison's own page is whole
    without them, and it is the list that goes quiet.

    `stances` pairs positionally with `compares`, like `sources` — the third
    branch and the third `probe-matrix` column are the same paper, and a count
    that drifts is the one way that can silently stop being true.
    """
    problems = []
    if not stances:
        problems.append(
            f"comparison/{name}: missing `stances` — what each paper does about "
            f"the question, one per entry of `compares`, in the same order"
        )
    elif len(stances) != len(ids):
        problems.append(
            f"comparison/{name}: `stances` has {len(stances)} entries for "
            f"{len(ids)} papers — one per compared paper, in `compares` order"
        )
    else:
        for pid, stance in zip(ids, stances):
            if len(stance) > STANCE_MAX:
                problems.append(
                    f"comparison/{name}: the stance for {pid} is {len(stance)} "
                    f"chars — keep it to {STANCE_MAX}. One that needs a clause of "
                    f"mechanism to land is not a stance; that clause is a "
                    f"`probe-matrix` cell"
                )
    if not common:
        # Act 2 is the act most often skipped, and this is the key that catches
        # the skip: three stances that leave no trunk are three papers that are
        # merely different rather than diverging.
        problems.append(
            f"comparison/{name}: missing `common` — the commitment all "
            f"{len(ids)} share, in one line"
        )
    elif len(common) > COMMON_MAX:
        problems.append(
            f"comparison/{name}: `common` is {len(common)} chars — keep it to "
            f"{COMMON_MAX}. It prints as the trunk of a fork, on one line"
        )
    return problems


def _check_plain(name: str, ids: list[str], problem: str, plain: list[str]) -> list[str]:
    """`problem` and `plain` — the comparison in everyday words.

    Both are optional: a comparison without them prints its tagline under the
    question and its cards without a plain line. Written, they are held to the
    width they print at, and a plain line to everyday words — it is read before
    any term on the page is explained.
    """
    problems = []
    if problem and len(problem) > PROBLEM_MAX:
        problems.append(
            f"comparison/{name}: `problem` is {len(problem)} chars — keep it to "
            f"{PROBLEM_MAX}. It is the one sentence under the question"
        )
    if not plain:
        return problems
    if len(plain) != len(ids):
        return problems + [
            f"comparison/{name}: `plain` has {len(plain)} entries for {len(ids)} "
            f"papers — one per compared paper, in `compares` order"
        ]
    for pid, line in zip(ids, plain):
        if len(line) > PLAIN_MAX:
            problems.append(
                f"comparison/{name}: the plain line for {pid} is {len(line)} "
                f"chars — keep it to {PLAIN_MAX}"
            )
        if _LATIN_OR_MATH.search(line):
            problems.append(
                f"comparison/{name}: the plain line for {pid} carries Latin "
                f"script or math ({line!r}) — say it in everyday Korean; the "
                f"term belongs in a cell"
            )
    return problems


def _check_primer(name: str, primer: list[str]) -> list[str]:
    """`primer` names at most three background cards, each one that exists."""
    problems = []
    if len(primer) > primers.PRIMER_MAX:
        problems.append(
            f"comparison/{name}: `primer` names {len(primer)} cards — at most "
            f"{primers.PRIMER_MAX}; past that the background is a lesson, and the "
            f"comparison has stopped comparing"
        )
    for pid in primer:
        if pid not in primers.PRIMERS:
            problems.append(
                f"comparison/{name}: `primer` names {pid!r}, which is not a card — "
                f"one of {', '.join(primers.PRIMERS)}"
            )
    if len(set(primer)) != len(primer):
        problems.append(f"comparison/{name}: `primer` names a card twice")
    return problems


def for_paper(paper_id: str, comps: list[Comparison]) -> list[Comparison]:
    """The comparisons this paper appears in, newest first."""
    hits = [c for c in comps if paper_id in c.paper_ids]
    return sorted(hits, key=lambda c: c.order_key, reverse=True)
