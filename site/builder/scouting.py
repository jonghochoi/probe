"""Scouting run discovery — every `scouting/P#/YYYY-MM-DD.md`, merged by date.

A run writes one report per pillar, for the routine's sake — one context
file, one window each — and a run file beside them (`scouting/runs/`). The
site's unit is the run instead: one page per date that puts every pillar's
surfaced papers on one list, one row per arXiv id, so a paper four pillars
flagged reads as one paper flagged four times rather than as four papers. The
run file says which pillars failed, carries the run's synthesis and names
each paper; a date with no run file publishes the pillars it has and marks
the rest as missing.

The reports' form is `scouting/AUTHORING.md`; this module reads it and owns
none of it. A report carries its total on a score line under each paper's
header line (§5-1), or, dated before that rule binds, in a `## 📊` section of
bold heads in paper order — each report is read in its own form, never
rewritten to fit the reader. Only a report that carries score lines can be
wrong about them, so only those raise a problem.

Standard library only, like every module the agent's `query.py` could reach.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .corpus import PILLAR_NAMES, REPO_ROOT

SCOUTING = REPO_ROOT / "scouting"

MEDALS = {"🥇": 1, "🥈": 2, "🥉": 3}
PICK = "🌱"
ROW = "📋"

# How a merged paper is grouped on its date's page, in page order: flagged by
# more than one pillar, written up in full by one, or one 📋 row only.
GROUPS = (
    ("shared", "여러 연구 축이 함께 지목"),
    ("top", "연구 축별 상위"),
    ("rest", "그 밖에 게이트 통과"),
)

_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_ID = re.compile(r"arxiv\.org/abs/(\d{4}\.\d{4,5})")
_LINK_LINE = re.compile(r"^\[(?:arXiv:[^\]]+|DOI)\]\(https?://[^)]+\)\s*·")
_TITLE = re.compile(r"^\*\*(.+?)\*\*\s*$")
_COMMENT = re.compile(r"<!--.*?-->", re.S)
# A report's linked badge, `[![D8XB](https://img.shields.io/…)](#ref-D8XB)`, or
# a bare one. The page prints the code as text and gives it the tooltip every
# `D#` gets: the badge image is a third-party request the site never makes,
# and its `#ref-` anchor points into a legend the page does not print.
_BADGE_MD = re.compile(r"\[?!\[([A-Z0-9]+)\]\([^)]*\)\]?(?:\(#ref-[A-Za-z0-9]+\))?")
_SCORE_LINE = re.compile(r"^\*\*점수 (?P<total>\d{1,2})/15\*\* · ")
_SCORE_HEAD = re.compile(r"^\*\*(?P<name>[^*]+?)\s*\((?P<total>\d{1,2})/15[^*]*\)\*\*")
_ROW_SCORES = re.compile(r"\d·\d·\d·\d")
_CODE_LABELS = ("코드 공개 예정", "코드 미공개", "코드 공개")  # longest first
_ALIAS_ID = re.compile(r"\s*\(\d{4}\.\d{4,5}\)$")


@dataclass
class Pick:
    """One paper as one pillar's report wrote it up — a section or a 📋 row."""
    pillar: str
    kind: str                     # 🥇 🥈 🥉 🌱 or 📋
    rank: int                     # 1–3 medals, 4 the pick, 5+ the 📋 rows in order
    paper_id: str
    alias: str
    title: str = ""
    code: str = ""
    total: int | None = None
    meta: list[str] = field(default_factory=list)
    contrib: str = ""
    implic: str = ""
    check: str = ""
    gist: str = ""                # a 📋 row's 한 줄 근거

    @property
    def full(self) -> bool:
        return self.kind != ROW


@dataclass
class NearMiss:
    pillar: str
    paper_id: str
    alias: str
    condition: str


@dataclass
class Report:
    pillar: str
    date: str
    path: Path
    picks: list[Pick] = field(default_factory=list)
    near: list[NearMiss] = field(default_factory=list)

    @property
    def source(self) -> str:
        return self.path.relative_to(REPO_ROOT).as_posix()


@dataclass
class Paper:
    """One arXiv id across every pillar that surfaced it on one date."""
    paper_id: str
    picks: list[Pick]

    @property
    def lead(self) -> Pick:
        """The write-up the row speaks from: a full section before a row, then
        the higher rank, then the higher total."""
        return min(self.picks, key=lambda p: (not p.full, p.rank, -(p.total or 0)))

    @property
    def pillars(self) -> list[str]:
        seen = {p.pillar for p in self.picks}
        return [p for p in PILLAR_NAMES if p in seen]

    @property
    def group(self) -> str:
        if len(self.pillars) > 1:
            return "shared"
        return "top" if any(p.full for p in self.picks) else "rest"

    @property
    def best(self) -> int:
        return max((p.total or 0) for p in self.picks)

    @property
    def alias(self) -> str:
        return next((p.alias for p in sorted(self.picks, key=lambda p: p.full) if p.alias),
                    self.paper_id)

    @property
    def title(self) -> str:
        return next((p.title for p in self.picks if p.title), "")

    @property
    def code(self) -> str:
        return self.lead.code

    @property
    def gist(self) -> str:
        """One line on what the paper is, for the collapsed row."""
        lead = self.lead
        if lead.contrib:
            first = next((l[2:].strip() for l in lead.contrib.splitlines()
                          if l.startswith("- ")), "")
            if first:
                return first
        return next((p.gist for p in self.picks if p.gist), "")


@dataclass
class RunFile:
    """`scouting/runs/<date>.md` — the pillars that failed, the run's
    cross-pillar synthesis and each paper's alias (AUTHORING §8)."""
    failed: dict[str, str]
    synthesis: str
    aliases: dict[str, str]       # arXiv id -> the alias every report of the run uses


@dataclass
class Run:
    date: str
    reports: list[Report]
    papers: list[Paper]
    run_file: RunFile | None = None

    @property
    def arrived(self) -> list[str]:
        return [r.pillar for r in self.reports]

    @property
    def missing(self) -> dict[str, str]:
        """Pillar -> why it has no report on this date: the run file's
        `Failed:` reason, or, on a date with no run file, 대기."""
        if self.run_file:
            return {p: f"실패 — {why}" for p, why in self.run_file.failed.items()}
        return {p: "대기" for p in PILLAR_NAMES if p not in self.arrived}

    @property
    def near(self) -> list[NearMiss]:
        """Near misses no pillar surfaced, one per id, pillars in order."""
        surfaced = {p.paper_id for p in self.papers}
        out: dict[str, NearMiss] = {}
        for r in self.reports:
            for n in r.near:
                if n.paper_id not in surfaced and n.paper_id not in out:
                    out[n.paper_id] = n
        return list(out.values())

    def grouped(self) -> list[tuple[str, str, list[Paper]]]:
        out = []
        for key, label in GROUPS:
            members = [p for p in self.papers if p.group == key]
            if members:
                out.append((key, label, members))
        return out


def _sections(text: str) -> list[tuple[str, str]]:
    out = []
    for chunk in re.split(r"\n(?=## )", text):
        if chunk.startswith("## "):
            head, _, body = chunk.partition("\n")
            out.append((head[3:].strip(), body))
    return out


def _subsections(body: str) -> dict[str, str]:
    subs: dict[str, str] = {}
    for chunk in re.split(r"\n(?=### )", body):
        if chunk.startswith("### "):
            head, _, rest = chunk.partition("\n")
            # The `---` rule that closes a paper section lands in its last
            # subsection; it is the report's layout, not the paper's content.
            subs[head[4:].strip()[:3]] = re.sub(r"(\n\s*-{3,}\s*)+$", "", rest.strip())
    return subs


def _rows(body: str):
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("|") and not re.match(r"^\|\s*:?-", s):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if cells and cells[0] != "Paper":
                yield cells


def _alias_from_title(title: str) -> str:
    head = title.split(":")[0].strip()
    return head if ":" in title and len(head) <= 32 else title


def _plain(text: str) -> str:
    return _BADGE_MD.sub(lambda m: m.group(1), text)


def _code(text: str) -> str:
    return next((c for c in _CODE_LABELS if c in text), "")


def parse(path: Path, pillar: str, problems: list[str]) -> Report:
    text = _COMMENT.sub("", path.read_text(encoding="utf-8"))
    report = Report(pillar=pillar, date=path.stem, path=path)
    has_score_lines = "**점수 " in text
    heads: list[dict] = []
    rows = 0
    for header, body in _sections(text):
        emoji = header[:1]
        if emoji in MEDALS or emoji == PICK:
            lines = body.splitlines()
            at = next((i for i, l in enumerate(lines) if _LINK_LINE.match(l.strip())), None)
            ident = _ID.search(lines[at]) if at is not None else None
            if ident is None:
                problems.append(f"{report.source}: {header} carries no arXiv link line")
                continue
            title = next((t.group(1) for l in lines[:at]
                          if (t := _TITLE.match(l.strip()))), "")
            link = lines[at].strip()
            subs = _subsections(body)
            pick = Pick(
                pillar=pillar, kind=emoji, rank=MEDALS.get(emoji, 4),
                paper_id=ident.group(1), alias=_alias_from_title(title), title=title,
                code=_code(link), meta=[s.strip() for s in link.split("·")[1:]
                                        if not _code(s)],
                contrib=_plain(subs.get("(b)", "")), implic=_plain(subs.get("(c)", "")),
                check=_plain(subs.get("(d)", "")),
            )
            score = next((s for l in lines[at + 1:] if (s := l.strip())), "")
            sm = _SCORE_LINE.match(score)
            if sm:
                pick.total = int(sm.group("total"))
            elif has_score_lines:
                problems.append(f"{report.source}: {header} has no score line under its "
                                f"header line (scouting/AUTHORING.md §5-1)")
            report.picks.append(pick)
        elif emoji == "📊":
            for line in body.splitlines():
                if (h := _SCORE_HEAD.match(line.strip())):
                    heads.append((_ALIAS_ID.sub("", h.group("name").strip()),
                                  int(h.group("total"))))
        elif emoji == ROW:
            for cells in _rows(body):
                ident = next((i for c in cells if (i := _ID.search(c))), None)
                if ident is None or not any(_ROW_SCORES.fullmatch(c) for c in cells):
                    continue
                rows += 1
                total = next((int(c.split("/")[0]) for c in cells
                              if re.fullmatch(r"\d{1,2}/15", c)), None)
                report.picks.append(Pick(
                    pillar=pillar, kind=ROW, rank=4 + rows, paper_id=ident.group(1),
                    alias=_ALIAS_ID.sub("", cells[0]), code=_code(" ".join(cells)),
                    total=total, gist=_plain(cells[-1])))
        elif emoji == "🔍":
            for cells in _rows(body):
                ident = next((i for c in cells if (i := _ID.search(c))), None)
                if ident is None:
                    continue
                report.near.append(NearMiss(
                    pillar=pillar, paper_id=ident.group(1), alias=_ALIAS_ID.sub("", cells[0]),
                    condition=_plain(cells[-1])))
    # A report with no score lines scores in its 📊 heads, which follow the
    # paper sections in order. Fewer heads than sections leaves the last ones
    # unscored rather than shifting every score by one.
    if not has_score_lines:
        sections = [p for p in report.picks if p.full]
        for pick, (alias, total) in zip(sections, heads):
            pick.alias, pick.total = alias, total
    return report


def parse_run_file(path: Path) -> RunFile:
    text = _COMMENT.sub("", path.read_text(encoding="utf-8"))
    failed = dict(re.findall(r"^\*\*Failed:\*\*\s*(P\d) — (.*)$", text, re.M))
    synthesis = ""
    aliases: dict[str, str] = {}
    for header, body in _sections(text):
        if header.startswith("🧭"):
            synthesis = _plain(re.sub(r"(\n\s*-{3,}\s*)+$", "", body.strip()))
        elif header.startswith("📐"):
            for cells in _rows(body):
                ident = next((i for c in cells if (i := _ID.search(c))), None)
                if ident:
                    aliases[ident.group(1)] = _ALIAS_ID.sub("", cells[0])
    return RunFile(failed=failed, synthesis=synthesis, aliases=aliases)


def discover() -> tuple[list[Run], list[str]]:
    """Every run date, newest first, and the problems found reading them."""
    problems: list[str] = []
    by_date: dict[str, list[Report]] = {}
    for pillar in PILLAR_NAMES:
        for path in sorted((SCOUTING / pillar).glob("*.md")):
            if not _DATE.match(path.stem):
                continue
            by_date.setdefault(path.stem, []).append(parse(path, pillar, problems))
    runs = []
    for date in sorted(by_date, reverse=True):
        reports = by_date[date]
        merged: dict[str, list[Pick]] = {}
        for r in reports:
            for pick in r.picks:
                merged.setdefault(pick.paper_id, []).append(pick)
        papers = [Paper(pid, picks) for pid, picks in merged.items()]
        # Within a group: more pillars first, then a medal before the pick,
        # then the total. 📋 ranks are row positions in one pillar's table and
        # mean nothing across pillars, so a row-only paper sorts on its total.
        order = {k: i for i, (k, _label) in enumerate(GROUPS)}
        papers.sort(key=lambda p: (order[p.group], -len(p.pillars),
                                   min((x.rank for x in p.picks if x.full), default=9),
                                   -p.best))
        run_path = SCOUTING / "runs" / f"{date}.md"
        run_file = parse_run_file(run_path) if run_path.exists() else None
        # A paper section names the paper by its title; the run file's 📐 row
        # is where the run gives it the alias its rows and prose use.
        for pick in (p for r in reports for p in r.picks):
            if run_file and pick.paper_id in run_file.aliases:
                pick.alias = run_file.aliases[pick.paper_id]
        runs.append(Run(date=date, reports=reports, papers=papers, run_file=run_file))
    return runs, problems
