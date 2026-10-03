#!/usr/bin/env python3
"""Check that scouting reports and run files follow scouting/AUTHORING.md.

The scouting track has no PR — a run's `scouting/P#/YYYY-MM-DD.md` reports and
its `scouting/runs/YYYY-MM-DD.md` run file are written by a scheduled routine and pushed straight to `main` with nothing between the agent
and the reader. The contract rules that drift under those conditions are the
ones a reader cannot un-see: a `Papers scanned:` line that grows into a
2,000-character query log, a Reproducibility score that contradicts its own
rationale, a paper header that grows a grade beside its rank. This lint gates
them.

Checks, grouped by the contract section they enforce:

  AUTHORING §6  metadata block — exactly `Papers scanned:` + `Papers surfaced
            (게이트 통과):` after the H1, no `Run date:` / `Agent version:`
            line, scanned line within the 400-character cap and naming a
            retry only beside a `최종 실패`, surfaced value a bare integer, H1
            date agreeing with the filename.
  AUTHORING §2  emoji system — every `##` header opens with an emoji from the
            canonical set, `###` headers carry none, the `##` sections run in
            canonical order, each medal appears at most once, 📋 stands
            only under all three medals, a paper header carries nothing
            after `논문 N` beyond the 🌱 tag, and from `_SECTIONS_EFFECTIVE`
            the first bullet of (b) and (c) is a headline of at most
            `_HEADLINE_MAX` characters.
  AUTHORING §5  scoring contract — every 📊 paper head lists all five dimensions
            and its bullets sum to the total it states; the four gate
            dimensions of a surfaced paper and of a 📋 row are each >= 2, and
            a 🔍 row is
            exactly one gate axis short, so neither table can hold a paper
            that cleared the gate; a Reproducibility bullet scoring >= 2 may
            not also plead that the signal is unconfirmed (the
            self-contradiction that inflates the axis); every paper header
            line carries one of the three code labels.
  AUTHORING §5  from `_SECTIONS_EFFECTIVE` — the gate is Relevance, Novelty
            and Methodology; every paper section carries a score line whose
            five scores sum to its total and clear the gate, each 📋 row's
            합계 is its scores' sum, every Reproducibility score agrees with
            its code label, and every report's Methodology, Real and
            Reproducibility equal its run file's 📐 row (§5-4).
  AUTHORING §8  the run file — its H1, `Pillars:` and `Failed:` lines, the 🧭
            and 📐 sections in order, a report for each pillar it lists and
            does not fail, and each 📐 row equal to the most recent earlier
            report that scored the paper in the window.
  AUTHORING §6  `Papers surfaced` agrees with the number of 🥇 / 🥈 / 🥉 / 🌱
            sections plus the 📋 rows.
  AUTHORING §7  section discipline — 🔍 / 📋 rows are one paper each (no
            `X 외 2편` bundling behind a single link).

The gate checks are the ones with teeth. Reproducibility is scored but does
not gate (§5-1), and the way that rule fails is not a report that ignores it
outright — it is a report that surfaces one paper and files four gate-clearing
ones as 🔍 rows reading `코드 공개 시 승격`. Reading the scores back out of the
report and comparing them against the gate is what catches that.

Precision over recall, mirroring the repo's other gates: every check keys off a
literal token the contract fixes, so a report that reads oddly but obeys the
contract passes. Render traps that need inline-context parsing (§4-6 tilde
pairing, §4-8 bold-before-particle) are out of scope — review catches those.

SCOPE. Each rule binds reports dated on or after the day the rule takes
effect: `_CONTRACT_EFFECTIVE` for the metadata, emoji, label and table rules,
`_GATE_EFFECTIVE` for the gate arithmetic, `_SHAPE_EFFECTIVE` for the medal,
📋 and retry rules, `_SECTIONS_EFFECTIVE` for the section set, the bare
medal header, the score line, the three-axis gate and the run file. Earlier
reports are the record of runs that happened under the contract of their day;
they are evidence, not drafts, so the lint skips them rather than inviting a
rewrite of history.

Usage (repo root):
    python3 linters/check-scouting-format.py [PATH ...]

No PATH -> scan `scouting/P*/*.md` and `scouting/runs/*.md` (templates excluded — they are skeletons of
placeholders, not reports).

Exit codes: 0 = clean / 1 = violations found / 2 = nothing to scan.
"""
from __future__ import annotations

import argparse
import datetime
import glob
import os
import re
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Reports dated before this are out of scope (see SCOPE in the docstring).
_CONTRACT_EFFECTIVE = "2026-08-18"

# The gate-arithmetic checks bind from here — the first scheduled run their
# rules apply to.
_GATE_EFFECTIVE = "2026-08-24"

# The medal, 📋 and retry rules bind from here.
_SHAPE_EFFECTIVE = "2026-09-27"

# The section set of AUTHORING §2-1, the bare `## 🥇 논문 N` header, the score
# line, the three-axis gate and the run file bind from here — the first run
# of the single routine. Reports dated earlier carry 💡, 🚫 and 📊 and gate on
# four axes under the contract of their day.
_SECTIONS_EFFECTIVE = "2026-10-05"
_OUT_OF_SET = {
    "💡": "a decision a run moves is a 🔄 bullet, and `context/` edits are the human's",
    "🚫": "a dropped candidate is part of the 🔄 filter count, not a row",
    "📊": "each paper section carries its scores on its own score line (AUTHORING §5-1)",
}

# The score line under a paper's header line (AUTHORING §5-1).
_SCORE_LINE = re.compile(
    r"^\*\*점수 (?P<total>\d{1,2})/15\*\* · R(?P<R>\d) · N(?P<N>\d) · M(?P<M>\d) · "
    r"Real(?P<Real>\d) · Repro(?P<Repro>\d) — (?P<evidence>\S.*)$"
)

# The label each Reproducibility score implies (AUTHORING §5-3).
_LABEL_OF_REPRO = {0: "코드 미공개", 1: "코드 공개 예정", 2: "코드 공개", 3: "코드 공개"}

# The dimensions that describe the paper rather than the pillar, and the window
# an earlier judgement of them is kept from (AUTHORING §5-4). A row's fourth
# score is Real; reports dated before `_SECTIONS_EFFECTIVE` call it Sim2Real
# and score the same thing, real-robot evidence.
_SCORES = ("R", "N", "M", "Real", "Repro")
_PAPER_DIMENSIONS = ("M", "Real", "Repro")
_CARRY_WINDOW_DAYS = 56
_ARXIV_ID = re.compile(r"arxiv\.org/abs/(\d{4}\.\d{4,5})")

# A paper header after `논문 N`: nothing for a medal, the 🌱 tag for the pick.
_MEDAL_HEADER = re.compile(r"^\S+ 논문 \d+$")
_PICK_HEADER = re.compile(r"^🌱 논문 \d+ — 인접 분야 픽$")

_SCANNED_MAX_CHARS = 400

# A retry is named on `Papers scanned` only beside the failure it ended in
# (AUTHORING §6); one that succeeded is a non-event.
_RETRY = re.compile(r"재시도|백오프|retry|backoff", re.IGNORECASE)
_FINAL_FAILURE = "최종 실패"

_H1 = re.compile(r"^# Probe 스카우트 리포트 — (\d{4}-\d{2}-\d{2}) · Pillar (P\d)\s*$")
_SCANNED = re.compile(r"^\*\*Papers scanned:\*\*\s*(.*)$")
_SURFACED = re.compile(r"^\*\*Papers surfaced \((?:4축 )?게이트 통과\):\*\*\s*(.*)$")
_BANNED_META = re.compile(r"^\*\*(Run date|Agent version):\*\*")
_FILENAME_DATE = re.compile(r"(\d{4}-\d{2}-\d{2})\.md$")

# Canonical `##` section order (AUTHORING §2-1). Sections must run non-decreasing
# in rank, pinning 📋 → 📊 → 🔍 → 🔄. 💡 and 🚫 hold their rank for the reports
# dated before `_SECTIONS_EFFECTIVE`.
_SECTION_RANK = {
    "🔑": 0, "🥇": 1, "🥈": 2, "🥉": 3, "🌱": 4, "📋": 5,
    "📊": 6, "🔍": 7, "💡": 8, "🔄": 9, "🚫": 10,
}

_MEDALS = ("🥇", "🥈", "🥉")

_RUBRIC_DIMENSIONS = ("Relevance", "Novelty", "Reproducibility", "Methodology", "Sim2Real")

# The four that gate (AUTHORING §5-1) — Reproducibility is scored, shown and
# ranked on, but never gates.
_GATE_DIMENSIONS = ("Relevance", "Novelty", "Methodology", "Sim2Real")
# From `_SECTIONS_EFFECTIVE` the gate is the first three (AUTHORING §5-1).
_GATE_THREE = _GATE_DIMENSIONS[:3]

_PAPER_SECTIONS = ("🥇", "🥈", "🥉", "🌱")

# Any pictographic character, so an `###` header is flagged for carrying an
# emoji the canonical `##` set does not even contain (AUTHORING §2-3).
_EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U00002B00-\U00002BFF\U0001F000-\U0001F2FF️]"
)

_CODE_LABELS = ("코드 공개 예정", "코드 미공개", "코드 공개")  # longest first

# A 📊 paper head: `**HapTile (13/15)**`, optionally trailing commentary.
_SCORE_HEAD = re.compile(r"^\*\*(?P<name>[^*]+?)\((?P<total>\d{1,2})/15[^*]*\)\*\*")
_SCORE_BULLET = re.compile(r"^-\s*(?P<dim>[A-Za-z0-9]+)\s+(?P<score>\d)\s*—\s*(?P<why>.*)$")

# A Reproducibility rationale scoring >= 2 must not simultaneously plead that
# the code signal was never confirmed — the evidence pass has already looked
# (AUTHORING §5-2).
_UNCONFIRMED = re.compile(r"미확인|확인 필요|확인 불가|공개 여부 불명|불명확")

# A paper header line: the line carrying the arXiv/DOI link under a bold title.
_PAPER_LINK_LINE = re.compile(r"^\[(?:arXiv:[^\]]+|DOI)\]\(https?://[^)]+\)\s*·")

# Table-cell paper bundling (AUTHORING §7-2): `Faster-WAM 외 2편 (…)`.
_BUNDLED = re.compile(r"외\s*\d+\s*편")

# The `R·N·M·Real` cell of a 🔍 or 📋 row (AUTHORING §5-1, §5-5): `2·2·1·3`.
_NEAR_MISS_SCORES = re.compile(r"(\d)·(\d)·(\d)·(\d)")


def _report_date(path: str) -> str | None:
    m = _FILENAME_DATE.search(os.path.basename(path))
    return m.group(1) if m else None


def _emoji_of(header_text: str) -> str | None:
    """Leading emoji of a `## ` header, if the header starts with one."""
    if not header_text:
        return None
    first = header_text[0]
    return first if first in _SECTION_RANK else None


def _check_metadata(lines: list[str], date_from_name: str, findings: list[tuple[int, str]],
                    shape_rules: bool) -> None:
    if not lines or not _H1.match(lines[0].rstrip("\n")):
        findings.append((1, "H1 must read `# Probe 스카우트 리포트 — YYYY-MM-DD · Pillar P#` (AUTHORING §6)"))
    else:
        h1_date = _H1.match(lines[0].rstrip("\n")).group(1)
        if h1_date != date_from_name:
            findings.append((1, f"H1 date {h1_date} disagrees with the filename date {date_from_name}"))

    # The metadata block is everything up to the first `---` rule.
    block: list[tuple[int, str]] = []
    for idx, raw in enumerate(lines[1:], start=2):
        line = raw.rstrip("\n")
        if line.strip() == "---":
            break
        if line.strip():
            block.append((idx, line))

    for lineno, line in block:
        if _BANNED_META.match(line):
            field = _BANNED_META.match(line).group(1)
            findings.append((lineno, f"`{field}:` line is dropped from the metadata block (AUTHORING §6)"))

    scanned = [(n, m) for n, l in block if (m := _SCANNED.match(l))]
    surfaced = [(n, m) for n, l in block if (m := _SURFACED.match(l))]

    if not scanned:
        findings.append((2, "metadata block is missing the `**Papers scanned:**` line (AUTHORING §6)"))
    else:
        lineno, m = scanned[0]
        value = m.group(1).strip()
        if len(value) > _SCANNED_MAX_CHARS:
            findings.append((
                lineno,
                f"`Papers scanned:` is {len(value)} chars, over the {_SCANNED_MAX_CHARS}-char cap — "
                "drop the funnel arithmetic and the retry narration (AUTHORING §6)",
            ))
        if shape_rules and _RETRY.search(value) and _FINAL_FAILURE not in value:
            findings.append((
                lineno,
                "`Papers scanned:` narrates a retry that succeeded — only a call that ends in "
                f"`{_FINAL_FAILURE}` is disclosed (AUTHORING §6)",
            ))

    if not surfaced:
        findings.append((2, "metadata block is missing the `**Papers surfaced (게이트 통과):**` line (AUTHORING §6)"))
    else:
        lineno, m = surfaced[0]
        value = m.group(1).strip()
        if not re.fullmatch(r"\d+", value):
            findings.append((
                lineno,
                f"`Papers surfaced` must be a bare integer, got {value!r} — the reasoning belongs in 🔄 (AUTHORING §6)",
            ))


def _check_sections(lines: list[str], findings: list[tuple[int, str]]) -> None:
    last_rank = -1
    last_emoji = ""
    in_fence = False
    for lineno, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        if line.startswith("###"):
            if _EMOJI.search(line):
                findings.append((lineno, "emoji belongs on `##` headers only, not `###` (AUTHORING §2-3)"))
            continue

        if not line.startswith("## "):
            continue

        text = line[3:].strip()
        emoji = _emoji_of(text)
        if emoji is None:
            findings.append((lineno, f"`##` header must open with a canonical emoji (AUTHORING §2-1): {text!r}"))
            continue
        rank = _SECTION_RANK[emoji]
        if rank < last_rank:
            findings.append((
                lineno,
                f"section {emoji} is out of canonical order — it follows {last_emoji} (AUTHORING §2-1)",
            ))
        last_rank, last_emoji = rank, emoji


def _split_sections(lines: list[str]) -> list[tuple[str, str, int, list[str]]]:
    """[(emoji, header_text, start_lineno, body_lines)] for each `##` section."""
    out: list[tuple[str, str, int, list[str]]] = []
    cur: tuple[str, str, int, list[str]] | None = None
    for lineno, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")
        if line.startswith("## "):
            if cur:
                out.append(cur)
            text = line[3:].strip()
            cur = (_emoji_of(text) or text[:1] or "?", text, lineno, [])
        elif cur:
            cur[3].append(line)
    if cur:
        out.append(cur)
    return out


def _check_scoring(sections, findings: list[tuple[int, str]], gate_rules: bool) -> None:
    for emoji, _header, start, body in sections:
        if emoji != "📊":
            continue
        head: str | None = None
        head_line = start
        head_total = 0
        seen: dict[str, int] = {}

        def close(head_name, head_lineno, stated_total, dims):
            if head_name is None:
                return
            missing = [d for d in _RUBRIC_DIMENSIONS if d not in dims]
            if missing:
                findings.append((
                    head_lineno,
                    f"📊 `{head_name}` is missing rubric bullet(s): {', '.join(missing)} — "
                    "all five dimensions are always shown (AUTHORING §5)",
                ))
                return
            if not gate_rules:
                return
            short = [f"{d} {dims[d]}" for d in _GATE_DIMENSIONS if dims[d] < 2]
            if short:
                findings.append((
                    head_lineno,
                    f"📊 `{head_name}` is surfaced with {', '.join(short)} — the four gate "
                    "dimensions are each >= 2, and a paper short of one belongs in 🔍 "
                    "(AUTHORING §5-1, §5-5)",
                ))
            bullet_total = sum(dims[d] for d in _RUBRIC_DIMENSIONS)
            if bullet_total != stated_total:
                findings.append((
                    head_lineno,
                    f"📊 `{head_name}` states {stated_total}/15 but its five bullets sum to "
                    f"{bullet_total} (AUTHORING §5-1)",
                ))

        for offset, line in enumerate(body, start=start + 1):
            m = _SCORE_HEAD.match(line.strip())
            if m:
                close(head, head_line, head_total, seen)
                head, head_line, seen = m.group("name").strip(), offset, {}
                head_total = int(m.group("total"))
                continue
            b = _SCORE_BULLET.match(line.strip())
            if not b:
                continue
            dim = b.group("dim")
            if dim in _RUBRIC_DIMENSIONS:
                seen.setdefault(dim, int(b.group("score")))
            if dim == "Reproducibility" and int(b.group("score")) >= 2 and _UNCONFIRMED.search(b.group("why")):
                findings.append((
                    offset,
                    "Reproducibility scores >= 2 while its own rationale says the signal is unconfirmed — "
                    "an absent signal scores 0 and is stated as absent (AUTHORING §5-2)",
                ))
        close(head, head_line, head_total, seen)


def _check_near_miss(sections, findings: list[tuple[int, str]], gate=_GATE_DIMENSIONS) -> None:
    """🔍 rows are exactly one gate axis short (AUTHORING §5-5)."""
    for emoji, _header, start, body in sections:
        if emoji != "🔍":
            continue
        for offset, line in enumerate(body, start=start + 1):
            stripped = line.strip()
            if not stripped.startswith("|") or stripped.startswith("|--"):
                continue
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            paper = cells[0] if cells else stripped
            score_cell = next((c for c in cells if _NEAR_MISS_SCORES.fullmatch(c)), None)
            if score_cell is None:
                if any(c.startswith("R·N") for c in cells):  # the header row
                    continue
                findings.append((
                    offset,
                    f"🔍 row `{paper}` carries no `R·N·M·Real` score cell — the gate "
                    "scores are what place a paper in this table (AUTHORING §5-5)",
                ))
                continue
            scores = [int(v) for v in _NEAR_MISS_SCORES.fullmatch(score_cell).groups()]
            short = [d for d, v in zip(gate, scores) if v < 2]
            if not short:
                findings.append((
                    offset,
                    f"🔍 row `{paper}` scores {score_cell} — every gate dimension clears, so the "
                    "paper is surfaced, not held for its repository (AUTHORING §5-1, §5-5)",
                ))
            elif len(short) > 1:
                findings.append((
                    offset,
                    f"🔍 row `{paper}` scores {score_cell}, short on {', '.join(short)} — 🔍 is "
                    "exactly one axis short, two or more is dropped (AUTHORING §5-5)",
                ))


def _table_rows(body: list[str], start: int):
    """(lineno, cells) for each data row of the tables in a section body."""
    for offset, line in enumerate(body, start=start + 1):
        stripped = line.strip()
        if not stripped.startswith("|") or stripped.startswith("|--"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if cells and cells[0] == "Paper":  # the header row
            continue
        yield offset, cells


def _check_shape(sections, findings: list[tuple[int, str]], gate=_GATE_DIMENSIONS) -> None:
    """The top three take the medals once each; the rest are 📋 rows that clear
    the gate (AUTHORING §5-1)."""
    seen: dict[str, int] = {}
    for emoji, _header, start, _body in sections:
        if emoji in _MEDALS:
            if emoji in seen:
                findings.append((
                    start,
                    f"{emoji} is used again (first at line {seen[emoji]}) — each medal marks one "
                    "rank, and papers below 🥉 are 📋 rows (AUTHORING §5-1)",
                ))
            else:
                seen[emoji] = start
    for emoji, _header, start, body in sections:
        if emoji != "📋":
            continue
        if len(seen) < len(_MEDALS):
            findings.append((
                start,
                "📋 holds papers ranked below 🥉, so it needs all three medal sections "
                "above it (AUTHORING §5-1)",
            ))
        for offset, cells in _table_rows(body, start):
            paper = cells[0]
            score_cell = next((c for c in cells if _NEAR_MISS_SCORES.fullmatch(c)), None)
            if score_cell is None:
                findings.append((
                    offset,
                    f"📋 row `{paper}` carries no `R·N·M·Real` score cell (AUTHORING §5-1)",
                ))
                continue
            scores = [int(v) for v in _NEAR_MISS_SCORES.fullmatch(score_cell).groups()]
            short = [d for d, v in zip(gate, scores) if v < 2]
            if short:
                findings.append((
                    offset,
                    f"📋 row `{paper}` scores {score_cell}, short on {', '.join(short)} — a 📋 "
                    "row is a surfaced paper and clears the gate (AUTHORING §5-1, §5-5)",
                ))


def _check_surfaced_count(lines: list[str], sections, findings: list[tuple[int, str]]) -> None:
    """`Papers surfaced` equals the paper sections plus the 📋 rows (AUTHORING §6)."""
    stated: tuple[int, str] | None = None
    for lineno, raw in enumerate(lines, start=1):
        m = _SURFACED.match(raw.rstrip("\n"))
        if m:
            stated = (lineno, m.group(1).strip())
            break
    if stated is None or not re.fullmatch(r"\d+", stated[1]):
        return  # absent or non-integer — already reported by _check_metadata
    lineno, value = stated
    n_sections = sum(1 for emoji, _h, _s, _b in sections if emoji in _PAPER_SECTIONS)
    n_rows = sum(
        1 for emoji, _h, start, body in sections if emoji == "📋"
        for _ in _table_rows(body, start)
    )
    if int(value) != n_sections + n_rows:
        findings.append((
            lineno,
            f"`Papers surfaced` is {value} but the report carries {n_sections} "
            f"🥇 / 🥈 / 🥉 / 🌱 section(s) and {n_rows} 📋 row(s) (AUTHORING §6)",
        ))


def _check_section_set(sections, findings: list[tuple[int, str]]) -> None:
    """The §2-1 section set and the bare paper header (AUTHORING §2-1, §5-3)."""
    for emoji, header, start, _body in sections:
        if emoji in _OUT_OF_SET:
            findings.append((
                start,
                f"{emoji} is not a §2-1 section — {_OUT_OF_SET[emoji]} (AUTHORING §2-1, §7-1)",
            ))
        elif emoji in _MEDALS and not _MEDAL_HEADER.match(header):
            findings.append((
                start,
                f"paper header {header!r} carries something after `논문 N` — the medal is the "
                "rank and the code label the only priority marker (AUTHORING §2-1, §5-3)",
            ))
        elif emoji == "🌱" and not _PICK_HEADER.match(header):
            findings.append((
                start,
                f"🌱 header {header!r} must read `## 🌱 논문 N — 인접 분야 픽` (AUTHORING §2-1)",
            ))


def _check_paper_headers(sections, findings: list[tuple[int, str]]) -> None:
    for emoji, _header, start, body in sections:
        if emoji not in _PAPER_SECTIONS:
            continue
        for offset, line in enumerate(body, start=start + 1):
            if not _PAPER_LINK_LINE.match(line.strip()):
                continue
            label = next((lb for lb in _CODE_LABELS if lb in line), None)
            if label is None:
                findings.append((
                    offset,
                    "paper header line is missing its code label "
                    "(`코드 공개` / `코드 공개 예정` / `코드 미공개`) — AUTHORING §5-3",
                ))
            break


def _check_tables(sections, findings: list[tuple[int, str]]) -> None:
    for emoji, _header, start, body in sections:
        if emoji not in ("🚫", "🔍", "📋"):
            continue
        for offset, line in enumerate(body, start=start + 1):
            stripped = line.strip()
            if not stripped.startswith("|"):
                continue
            first_cell = stripped.strip("|").split("|")[0]
            if _BUNDLED.search(first_cell):
                findings.append((
                    offset,
                    f"{emoji} table row bundles several papers behind one link "
                    f"({first_cell.strip()!r}) — one row per paper (AUTHORING §7-2)",
                ))


# The (b) and (c) headline — the first bullet — fits one scanning line
# (AUTHORING §2-2). Counted on the text a reader sees: no `**` or backticks.
_HEADLINE_MAX = 50
_HEADLINED = ("(b)", "(c)")


def _check_headlines(sections, findings: list[tuple[int, str]]) -> None:
    for emoji, _header, start, body in sections:
        if emoji not in _PAPER_SECTIONS:
            continue
        sub = None
        seen: set[str] = set()
        for offset, line in enumerate(body, start=start + 1):
            s = line.strip()
            if s.startswith("### "):
                sub = s[4:7]
                continue
            if sub in _HEADLINED and sub not in seen and s.startswith("- "):
                seen.add(sub)
                text = re.sub(r"\*\*|`", "", s[2:]).strip()
                if len(text) > _HEADLINE_MAX:
                    findings.append((offset, f"{sub} headline is {len(text)} characters, over "
                                             f"{_HEADLINE_MAX} — one line, the detail in the next "
                                             "bullet (AUTHORING §2-2)"))


def _row_scores(cells: list[str]) -> dict[str, int] | None:
    """R/N/M/Real from a row's `R·N·M·Real` cell, plus Repro from a 📋 row."""
    score_cell = next((c for c in cells if _NEAR_MISS_SCORES.fullmatch(c)), None)
    if score_cell is None:
        return None
    dims = dict(zip(("R", "N", "M", "Real"),
                    (int(v) for v in _NEAR_MISS_SCORES.fullmatch(score_cell).groups())))
    idx = cells.index(score_cell)
    if idx + 1 < len(cells) and re.fullmatch(r"\d", cells[idx + 1]):
        dims["Repro"] = int(cells[idx + 1])
    return dims


def _scored(sections) -> list[tuple[int, str, dict[str, int]]]:
    """(lineno, arXiv id, scores) for every score line and 📋 / 🔍 row."""
    out: list[tuple[int, str, dict[str, int]]] = []
    for emoji, _header, start, body in sections:
        if emoji in _PAPER_SECTIONS:
            pid = None
            for offset, line in enumerate(body, start=start + 1):
                s = line.strip()
                if pid is None:
                    if _PAPER_LINK_LINE.match(s) and (m := _ARXIV_ID.search(s)):
                        pid = m.group(1)
                    continue
                if (m := _SCORE_LINE.match(s)):
                    out.append((offset, pid, {k: int(m.group(k)) for k in _SCORES}))
                    break
        elif emoji in ("📋", "🔍"):
            for offset, cells in _table_rows(body, start):
                link = next((c for c in cells if _ARXIV_ID.search(c)), None)
                dims = _row_scores(cells)
                if link and dims:
                    out.append((offset, _ARXIV_ID.search(link).group(1), dims))
    return out


def _check_score_lines(sections, findings: list[tuple[int, str]]) -> None:
    """The score line under every paper header and the 📋 sums (AUTHORING §5-1 – §5-3)."""
    for emoji, _header, start, body in sections:
        if emoji not in _PAPER_SECTIONS:
            continue
        link_at = next((i for i, line in enumerate(body)
                        if _PAPER_LINK_LINE.match(line.strip())), None)
        if link_at is None:
            continue
        label = next((lb for lb in _CODE_LABELS if lb in body[link_at]), None)
        nxt = next(((i, line.strip()) for i, line in enumerate(body[link_at + 1:], start=link_at + 1)
                    if line.strip()), (None, ""))
        lineno = start + 1 + (nxt[0] if nxt[0] is not None else link_at)
        m = _SCORE_LINE.match(nxt[1])
        if not m:
            findings.append((
                lineno,
                f"{emoji} section has no score line under its header line — "
                "`**점수 N/15** · R# · N# · M# · Real# · Repro# — <evidence>` (AUTHORING §5-1)",
            ))
            continue
        dims = {k: int(m.group(k)) for k in _SCORES}
        if sum(dims.values()) != int(m.group("total")):
            findings.append((lineno, f"score line states {m.group('total')}/15 but its five "
                                     f"scores sum to {sum(dims.values())} (AUTHORING §5-1)"))
        short = [k for k in ("R", "N", "M") if dims[k] < 2]
        if short:
            findings.append((lineno, f"surfaced with {', '.join(f'{k}{dims[k]}' for k in short)} — the "
                                     "three gate dimensions are each >= 2, and a paper short of one "
                                     "belongs in 🔍 (AUTHORING §5-1, §5-5)"))
        if dims["Repro"] >= 2 and _UNCONFIRMED.search(m.group("evidence")):
            findings.append((lineno, "Repro scores >= 2 while its evidence says the signal is "
                                     "unconfirmed — an absent signal scores 0 (AUTHORING §5-2)"))
        if label and _LABEL_OF_REPRO.get(dims["Repro"]) != label:
            findings.append((lineno, f"Repro{dims['Repro']} implies `{_LABEL_OF_REPRO.get(dims['Repro'])}`, "
                                     f"the header line says `{label}` (AUTHORING §5-3)"))
    for emoji, _header, start, body in sections:
        if emoji != "📋":
            continue
        for offset, cells in _table_rows(body, start):
            dims = _row_scores(cells)
            total = next((c for c in cells if re.fullmatch(r"\d{1,2}/15", c)), None)
            if not dims or "Repro" not in dims or total is None:
                continue
            if sum(dims.values()) != int(total.split("/")[0]):
                findings.append((offset, f"📋 row `{cells[0]}` states {total} but its scores sum to "
                                         f"{sum(dims.values())} (AUTHORING §5-1)"))
            label = next((lb for c in cells for lb in _CODE_LABELS if c == lb), None)
            if label and _LABEL_OF_REPRO.get(dims["Repro"]) != label:
                findings.append((offset, f"📋 row `{cells[0]}` scores Repro {dims['Repro']} but reads "
                                         f"`{label}` (AUTHORING §5-3)"))


def _earlier_sources(root: str, date: str) -> dict[str, tuple[str, str, dict[str, int]]]:
    """id -> (date, pillar, scores) from every pillar's reports dated in the window
    before `date`, keeping the most recent: the latest date, then the lowest pillar
    (AUTHORING §5-4)."""
    floor = (datetime.date.fromisoformat(date)
             - datetime.timedelta(days=_CARRY_WINDOW_DAYS)).isoformat()
    best: dict[str, tuple[str, str, dict[str, int]]] = {}
    for other in sorted(glob.glob(os.path.join(root, "P[0-9]", "*.md"))):
        odate = _report_date(other)
        if odate is None or not (floor <= odate < date):
            continue
        pillar = os.path.basename(os.path.dirname(other))
        with open(other, encoding="utf-8") as fh:
            sections = _split_sections(fh.readlines())
        for _lineno, pid, dims in _scored(sections):
            have = best.get(pid)
            if have is None or (odate, -int(pillar[1:])) > (have[0], -int(have[1][1:])):
                best[pid] = (odate, pillar, dims)
    return best


# The run file (AUTHORING §8).
_RUN_H1 = re.compile(r"^# Probe 스카우트 회차 — (\d{4}-\d{2}-\d{2})\s*$")
_RUN_PILLARS = re.compile(r"^\*\*Pillars:\*\*\s*((?:P\d\s*)+)$")
_RUN_FAILED = re.compile(r"^\*\*Failed:\*\*\s*(P\d) — (\S.*)$")
_RUN_SECTIONS = ("🧭", "📐")


def _judged(lines: list[str]) -> dict[str, tuple[int, dict[str, int]]]:
    """id -> (lineno, M/Real/Repro) from a run file's 📐 table."""
    out: dict[str, tuple[int, dict[str, int]]] = {}
    for emoji, _h, start, body in _split_sections(lines):
        if emoji != "📐":
            continue
        for offset, cells in _table_rows(body, start):
            link = next((c for c in cells if _ARXIV_ID.search(c)), None)
            digits = [c for c in cells if re.fullmatch(r"[0-3]", c)]
            if link and len(digits) >= 3:
                out[_ARXIV_ID.search(link).group(1)] = (
                    offset, dict(zip(_PAPER_DIMENSIONS, map(int, digits[:3]))))
    return out


def _run_file(root: str, date: str) -> str:
    return os.path.join(root, "runs", f"{date}.md")


def _check_against_run(abs_path: str, date: str, sections, findings: list[tuple[int, str]]) -> None:
    """A report prints its run's one judgement of each paper (AUTHORING §5-4, §8)."""
    root = os.path.dirname(os.path.dirname(abs_path))
    run = _run_file(root, date)
    if not os.path.exists(run):
        findings.append((1, f"no run file `scouting/runs/{date}.md` beside this report (AUTHORING §8)"))
        return
    with open(run, encoding="utf-8") as fh:
        judged = _judged(fh.readlines())
    for lineno, pid, dims in _scored(sections):
        if pid not in judged:
            findings.append((lineno, f"{pid} has no 📐 row in `scouting/runs/{date}.md` (AUTHORING §8)"))
            continue
        jd = judged[pid][1]
        off = [f"{k} {dims[k]} vs {jd[k]}" for k in _PAPER_DIMENSIONS if k in dims and dims[k] != jd[k]]
        if off:
            findings.append((lineno, f"{pid} disagrees with the run file on {', '.join(off)} — "
                                     "Methodology, Real and Reproducibility are judged once per "
                                     "run (AUTHORING §5-4)"))


def check_run_file(path: str) -> list[tuple[int, str]]:
    """The run file's form, its pillars' reports and its judgements (AUTHORING §8)."""
    abs_path = path if os.path.isabs(path) else os.path.join(_REPO_ROOT, path)
    with open(abs_path, encoding="utf-8") as fh:
        lines = fh.readlines()
    date = _report_date(abs_path)
    findings: list[tuple[int, str]] = []
    m = _RUN_H1.match(lines[0].rstrip("\n")) if lines else None
    if not m:
        findings.append((1, "H1 must read `# Probe 스카우트 회차 — YYYY-MM-DD` (AUTHORING §8)"))
    elif m.group(1) != date:
        findings.append((1, f"H1 date {m.group(1)} disagrees with the filename date {date}"))
    pillars: list[str] = []
    failed: set[str] = set()
    for lineno, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")
        if line.strip() == "---":
            break
        if (pm := _RUN_PILLARS.match(line)):
            pillars = pm.group(1).split()
        elif (fm := _RUN_FAILED.match(line)):
            failed.add(fm.group(1))
    if not pillars:
        findings.append((2, "the run file is missing its `**Pillars:**` line (AUTHORING §8)"))
    root = os.path.dirname(os.path.dirname(abs_path))
    for p in pillars:
        report = os.path.join(root, p, f"{date}.md")
        if p not in failed and not os.path.exists(report):
            findings.append((2, f"{p} is listed and not `Failed:`, but `scouting/{p}/{date}.md` "
                                "does not exist (AUTHORING §8)"))
        if p in failed and os.path.exists(report):
            findings.append((2, f"{p} is `Failed:` but `scouting/{p}/{date}.md` exists (AUTHORING §8)"))
    emojis = [e for e, _h, _s, _b in _split_sections(lines)]
    if tuple(emojis) != _RUN_SECTIONS:
        findings.append((1, f"the run file's sections are {' '.join(emojis) or 'none'}, and must be "
                            "🧭 then 📐 (AUTHORING §8)"))
    judged = _judged(lines)
    earlier = _earlier_sources(root, date)
    for pid, (lineno, jd) in judged.items():
        if pid not in earlier:
            continue
        sdate, spillar, sdims = earlier[pid]
        off = [f"{k} {jd[k]} vs {sdims[k]}" for k in _PAPER_DIMENSIONS if k in sdims and jd[k] != sdims[k]]
        if off:
            findings.append((lineno, f"{pid} disagrees with {spillar} {sdate} on {', '.join(off)} — a "
                                     "paper scored in the window keeps that judgement (AUTHORING §5-4)"))
    return sorted(findings)


def check_file(path: str) -> list[tuple[int, str]]:
    abs_path = path if os.path.isabs(path) else os.path.join(_REPO_ROOT, path)
    if os.path.basename(os.path.dirname(abs_path)) == "runs":
        return check_run_file(abs_path)
    try:
        with open(abs_path, encoding="utf-8") as fh:
            lines = fh.readlines()
    except OSError as e:
        return [(0, f"<could not read: {e}>")]

    date_from_name = _report_date(abs_path)
    if date_from_name is None:
        return [(0, "filename must be `YYYY-MM-DD.md`")]

    findings: list[tuple[int, str]] = []
    gate_rules = date_from_name >= _GATE_EFFECTIVE
    shape_rules = date_from_name >= _SHAPE_EFFECTIVE
    _check_metadata(lines, date_from_name, findings, shape_rules)
    _check_sections(lines, findings)
    sections = _split_sections(lines)
    _check_scoring(sections, findings, gate_rules)
    _check_paper_headers(sections, findings)
    _check_tables(sections, findings)
    current = date_from_name >= _SECTIONS_EFFECTIVE
    gate = _GATE_THREE if current else _GATE_DIMENSIONS
    if gate_rules:
        _check_near_miss(sections, findings, gate)
        _check_surfaced_count(lines, sections, findings)
    if shape_rules:
        _check_shape(sections, findings, gate)
    if current:
        _check_section_set(sections, findings)
        _check_score_lines(sections, findings)
        _check_headlines(sections, findings)
        _check_against_run(abs_path, date_from_name, sections, findings)
    return sorted(findings)


def _in_scope(path: str) -> bool:
    date = _report_date(path)
    return date is not None and date >= _CONTRACT_EFFECTIVE


def _gather_default_reports() -> list[str]:
    return sorted(
        os.path.relpath(p, _REPO_ROOT)
        for pattern in ("P[0-9]", "runs")
        for p in glob.glob(os.path.join(_REPO_ROOT, "scouting", pattern, "*.md"))
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check scouting reports against the scouting/AUTHORING.md output contract."
    )
    parser.add_argument("paths", nargs="*",
                        help="reports and run files to scan (default: scouting/P*/*.md, scouting/runs/*.md)")
    args = parser.parse_args(argv)

    reports = args.paths or _gather_default_reports()
    if not reports:
        sys.stderr.write("[check-scouting-format] nothing to scan\n")
        return 2

    in_scope = [r for r in reports if _in_scope(r)]
    skipped = len(reports) - len(in_scope)
    if not in_scope:
        print(
            f"[check-scouting-format] clean — no report dated {_CONTRACT_EFFECTIVE} or later "
            f"({skipped} earlier report(s) out of scope)"
        )
        return 0

    total = 0
    for report in in_scope:
        for lineno, message in check_file(report):
            total += 1
            print(f"{report}:{lineno}: {message}")

    if total:
        print(f"\n[check-scouting-format] {total} violation(s) across {len(in_scope)} report(s)")
        return 1
    print(
        f"[check-scouting-format] clean — {len(in_scope)} report(s) scanned"
        + (f", {skipped} earlier report(s) out of scope" if skipped else "")
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
