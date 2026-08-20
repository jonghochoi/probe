#!/usr/bin/env python3
"""Check that scouting reports follow the output contract in scouting/AUTHORING.md.

The scouting track has no build step — `analysis/` is validated by
`site/build-site.py`, but a `scouting/P#/YYYY-MM-DD.md` is written by a
scheduled routine and pushed straight to `main` with nothing between the agent
and the reader. The contract rules that drift under those conditions are the
ones a reader cannot un-see: a `Papers scanned:` line that grows into a
2,000-character query log, a Reproducibility score that contradicts its own
rationale, a `★★★` promotion for a paper nobody can run. This lint gates them.

Checks, grouped by the contract section they enforce:

  AUTHORING §6  metadata block — exactly `Papers scanned:` + `Papers surfaced
            (4축 게이트 통과):` after the H1, no `Run date:` / `Agent version:`
            line, scanned line within the 400-character cap, surfaced value a
            bare integer, H1 date agreeing with the filename.
  AUTHORING §2  emoji system — every `##` header opens with an emoji from the
            canonical set, `###` headers carry none, and the `##` sections run
            in canonical order.
  AUTHORING §5  scoring contract — every 📊 paper head lists all five dimensions
            and its bullets sum to the total it states; the four gate
            dimensions of a surfaced paper are each >= 2, and a 🔍 row is
            exactly one gate axis short, so neither table can hold a paper
            that cleared the gate; a Reproducibility bullet scoring >= 2 may
            not also plead that the signal is unconfirmed (the
            self-contradiction that inflates the axis); every paper header
            line carries one of the three code labels; a `★★★` section
            requires `코드 공개`.
  AUTHORING §6  `Papers surfaced` agrees with the number of 🥇 / 🥈 / 🥉 / 🌱
            sections.
  AUTHORING §7  section discipline — 🚫 / 🔍 rows are one paper each (no
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
`_GATE_EFFECTIVE` for the gate arithmetic added with them. Earlier reports are
the record of runs that happened under the contract of their day; they are
evidence, not drafts, so the lint skips them rather than inviting a rewrite of
history.

Usage (repo root):
    python3 linters/check-scouting-format.py [PATH ...]

No PATH -> scan `scouting/P*/*.md` (templates excluded — they are skeletons of
placeholders, not reports).

Exit codes: 0 = clean / 1 = violations found / 2 = nothing to scan.
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Reports dated before this are out of scope (see SCOPE in the docstring).
_CONTRACT_EFFECTIVE = "2026-08-18"

# The gate-arithmetic checks bind from here — the first scheduled run under the
# revision that added them.
_GATE_EFFECTIVE = "2026-08-24"

_SCANNED_MAX_CHARS = 400

_H1 = re.compile(r"^# Probe 스카우트 리포트 — (\d{4}-\d{2}-\d{2}) · Pillar (P\d)\s*$")
_SCANNED = re.compile(r"^\*\*Papers scanned:\*\*\s*(.*)$")
_SURFACED = re.compile(r"^\*\*Papers surfaced \(4축 게이트 통과\):\*\*\s*(.*)$")
_BANNED_META = re.compile(r"^\*\*(Run date|Agent version):\*\*")
_FILENAME_DATE = re.compile(r"(\d{4}-\d{2}-\d{2})\.md$")

# Canonical `##` section order (AUTHORING §2-1). Sections must run non-decreasing
# in rank, which allows several paper sections while pinning 📊 → 🔍 → 💡 →
# 🔄 → 🚫 and keeps the 🚫 appendix last.
_SECTION_RANK = {
    "🔑": 0, "🥇": 1, "🥈": 2, "🥉": 3, "🌱": 4,
    "📊": 5, "🔍": 6, "💡": 7, "🔄": 8, "🚫": 9,
}

_RUBRIC_DIMENSIONS = ("Relevance", "Novelty", "Reproducibility", "Methodology", "Sim2Real")

# The four that gate (AUTHORING §5-1) — Reproducibility is scored, shown and
# ranked on, but never gates.
_GATE_DIMENSIONS = ("Relevance", "Novelty", "Methodology", "Sim2Real")

_PAPER_SECTIONS = ("🥇", "🥈", "🥉", "🌱")

# Any pictographic character, so an `###` header is flagged for carrying an
# emoji the canonical `##` set does not even contain (AUTHORING §2-2).
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

# Table-cell paper bundling (AUTHORING §7-3): `Faster-WAM 외 2편 (…)`.
_BUNDLED = re.compile(r"외\s*\d+\s*편")

# The `R·N·M·S2R` cell of a 🔍 row (AUTHORING §5-4): `2·2·1·3`.
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


def _check_metadata(lines: list[str], date_from_name: str, findings: list[tuple[int, str]]) -> None:
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

    if not surfaced:
        findings.append((2, "metadata block is missing the `**Papers surfaced (4축 게이트 통과):**` line (AUTHORING §6)"))
    else:
        lineno, m = surfaced[0]
        value = m.group(1).strip()
        if not re.fullmatch(r"\d+", value):
            findings.append((
                lineno,
                f"`Papers surfaced` must be a bare integer, got {value!r} — the reasoning belongs in 📊 (AUTHORING §6)",
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
                findings.append((lineno, "emoji belongs on `##` headers only, not `###` (AUTHORING §2-2)"))
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
            cur = (_emoji_of(text) or "?", text, lineno, [])
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
                    "(AUTHORING §5-1, §5-4)",
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


def _check_near_miss(sections, findings: list[tuple[int, str]]) -> None:
    """🔍 rows are exactly one gate axis short (AUTHORING §5-4)."""
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
                    f"🔍 row `{paper}` carries no `R·N·M·S2R` score cell — the four gate "
                    "scores are what place a paper in this table (AUTHORING §5-4)",
                ))
                continue
            scores = [int(v) for v in _NEAR_MISS_SCORES.fullmatch(score_cell).groups()]
            short = [d for d, v in zip(_GATE_DIMENSIONS, scores) if v < 2]
            if not short:
                findings.append((
                    offset,
                    f"🔍 row `{paper}` scores {score_cell} — every gate dimension clears, so the "
                    "paper is surfaced, not held for its repository (AUTHORING §5-1, §5-4)",
                ))
            elif len(short) > 1:
                findings.append((
                    offset,
                    f"🔍 row `{paper}` scores {score_cell}, short on {', '.join(short)} — 🔍 is "
                    "exactly one axis short, two or more is a 🚫 row (AUTHORING §5-4)",
                ))


def _check_surfaced_count(lines: list[str], sections, findings: list[tuple[int, str]]) -> None:
    """`Papers surfaced` equals the number of paper sections (AUTHORING §6)."""
    stated: tuple[int, str] | None = None
    for lineno, raw in enumerate(lines, start=1):
        m = _SURFACED.match(raw.rstrip("\n"))
        if m:
            stated = (lineno, m.group(1).strip())
            break
    if stated is None or not re.fullmatch(r"\d+", stated[1]):
        return  # absent or non-integer — already reported by _check_metadata
    lineno, value = stated
    actual = sum(1 for emoji, _h, _s, _b in sections if emoji in _PAPER_SECTIONS)
    if int(value) != actual:
        findings.append((
            lineno,
            f"`Papers surfaced` is {value} but the report carries {actual} "
            "🥇 / 🥈 / 🥉 / 🌱 section(s) (AUTHORING §6)",
        ))


def _check_paper_headers(sections, findings: list[tuple[int, str]]) -> None:
    for emoji, header, start, body in sections:
        if emoji not in ("🥇", "🥈", "🥉", "🌱"):
            continue
        is_top = "★★★" in header
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
            elif is_top and label != "코드 공개":
                findings.append((
                    offset,
                    f"★★★ requires `코드 공개`, this paper is `{label}` — "
                    "an unobtainable artifact caps at ★★ (AUTHORING §5-3)",
                ))
            break


def _check_tables(sections, findings: list[tuple[int, str]]) -> None:
    for emoji, _header, start, body in sections:
        if emoji not in ("🚫", "🔍"):
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
                    f"({first_cell.strip()!r}) — one row per paper (AUTHORING §7-3)",
                ))


def check_file(path: str) -> list[tuple[int, str]]:
    abs_path = path if os.path.isabs(path) else os.path.join(_REPO_ROOT, path)
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
    _check_metadata(lines, date_from_name, findings)
    _check_sections(lines, findings)
    sections = _split_sections(lines)
    _check_scoring(sections, findings, gate_rules)
    _check_paper_headers(sections, findings)
    _check_tables(sections, findings)
    if gate_rules:
        _check_near_miss(sections, findings)
        _check_surfaced_count(lines, sections, findings)
    return sorted(findings)


def _in_scope(path: str) -> bool:
    date = _report_date(path)
    return date is not None and date >= _CONTRACT_EFFECTIVE


def _gather_default_reports() -> list[str]:
    return sorted(
        os.path.relpath(p, _REPO_ROOT)
        for p in glob.glob(os.path.join(_REPO_ROOT, "scouting", "P[0-9]", "*.md"))
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check scouting reports against the scouting/AUTHORING.md output contract."
    )
    parser.add_argument("paths", nargs="*", help="reports to scan (default: scouting/P*/*.md)")
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
