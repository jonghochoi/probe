#!/usr/bin/env python3
"""Check that stress-test memos follow the output contract in decisions/AUTHORING.md.

A memo is the one document in this repo whose subject is `context/` itself: it
re-reads a month of evidence against every OPEN decision and says whether the
decision still stands. That gives it two failure modes no other track has, and
both are silent:

  1. The memo covers the wrong set. A decision the human settled during the
     month is still stress-tested, or an open one is quietly skipped — and the
     reader has no way to tell a skipped decision from a decision nothing
     happened to.
  2. The memo re-quotes the month's scouting reports and calls the result a
     verdict. A scouting line is a sweep's one-line note about a paper nobody
     read in full; a verdict resting on nothing else is a summary of a summary
     wearing a decision's clothes. The contract does not forbid it — a quiet
     month is a real answer — it forbids not SAYING so, which is what the
     `(근거: 리포트 인용만)` token is.

Checks, grouped by the contract section they enforce:

  AUTHORING §2  the spine — H1 month agreeing with the filename, the metadata
            line and its four fields, one `## D<id> — <title> (P<m>)` per OPEN
            decision (the set read back out of `context/P*.md`, so a memo that
            skips one or keeps a settled one fails), the four `###` in order
            under each, and no line opening `#### [D` (a proposal is never
            written in the Decision Log's own entry form).
  AUTHORING §3  the verdict line — one per decision, one of the three states,
            and the falsifiability token present exactly when the decision's
            evidence table links into no rewrite or comparison.
  AUTHORING §2  every relative link resolves once `?plain=1#L…` is stripped —
            a line-anchored link is the memo's whole evidentiary claim.

What the lint cannot see is the judgement: whether the falsifier is really the
one the decision's own bullet implies, and whether a 지지 row supports the
decision or merely mentions it. Reading is what catches those.

SCOPE. `_CONTRACT_EFFECTIVE` is the day the contract takes effect; a memo is
bound when the month it covers is the last complete month before that day or
later, which is the first month this track can produce. A memo backfilled for
an earlier month is out of scope — it would be a record of a month nobody ran.

Usage (repo root):
    python3 linters/check-decisions-format.py [PATH ...]

No PATH -> scan `decisions/[0-9][0-9][0-9][0-9]-[0-9][0-9].md` (`AUTHORING.md`,
`SETUP.md` and the generated `MAP.md` are not memos).

Exit codes: 0 = clean / 1 = violations found / 2 = nothing to scan.
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The day the contract takes effect (see SCOPE in the docstring).
_CONTRACT_EFFECTIVE = "2026-09-04"

_MEMO_GLOB = "decisions/[0-9][0-9][0-9][0-9]-[0-9][0-9].md"

_FILENAME_MONTH = re.compile(r"(\d{4}-\d{2})\.md$")
_H1 = re.compile(r"^# 결정 스트레스 테스트 — (\d{4}-\d{2})\s*$")
_META = re.compile(
    r"^\*\*Window:\*\* \d{4}-\d{2}-\d{2} → \d{4}-\d{2}-\d{2}"
    r" · \*\*Reports read:\*\* \d+"
    r" · \*\*Rewrites landed:\*\* \d+"
    r" · \*\*Open decisions:\*\* (\d+)\s*$"
)

# `## D5DQ — Does a sub-policy-rate contact loop earn its place? (P1)`
_DECISION_H2 = re.compile(r"^## (D\d[A-Z]{2}) — (.*?) \(P(\d)\)\s*$")
_SUB = re.compile(r"^### (.*?)\s*$")
_SUBSECTIONS = ("현재 결정", "무엇이 뒤집는가", "이달의 증거", "제안 문안")

_VERDICTS = ("흔들림 없음", "재검토 권고", "뒤집을 증거 도착")
_VERDICT_LINE = re.compile(r"^\*\*판정:\*\* (.+?) — (.+?)\s*$")
_TOKEN = "(근거: 리포트 인용만)"

_LOG_ENTRY = re.compile(r"^#### \[D")

_MD_LINK = re.compile(r"\[(?:[^\]]*)\]\(([^)]+)\)")
_REWRITE_TRACKS = ("analysis/", "comparison/")

# The Decision-Log entry format (context/CLAUDE.md); the OPEN set is read back
# off it. `decisions/build-map.py` keeps its own copy for the same reason.
_ENTRY = re.compile(
    r"^####\s*\[(D\d[A-Z]{2})\]\s*(.*?)\s*\(P(\d)\)(\s*—\s*\*\*OPEN\*\*)?\s*$"
)
_PILLAR_FILE = re.compile(r"^P(\d)\.md$")


def open_decisions() -> list[tuple[str, str, int]]:
    """[(id, title, pillar)] for every OPEN entry, in pillar order."""
    out: list[tuple[str, str, int]] = []
    for path in sorted(glob.glob(os.path.join(_REPO_ROOT, "context", "P*.md"))):
        if not _PILLAR_FILE.match(os.path.basename(path)):
            continue
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                m = _ENTRY.match(line.rstrip("\n"))
                if m and m.group(4) is not None:
                    out.append((m.group(1), m.group(2), int(m.group(3))))
    return sorted(out, key=lambda d: d[2])


def _memo_month(path: str) -> str | None:
    m = _FILENAME_MONTH.search(os.path.basename(path))
    return m.group(1) if m else None


def _first_month_in_scope() -> str:
    year, month = int(_CONTRACT_EFFECTIVE[:4]), int(_CONTRACT_EFFECTIVE[5:7])
    year, month = (year - 1, 12) if month == 1 else (year, month - 1)
    return f"{year:04d}-{month:02d}"


def _strip_link_target(target: str) -> str:
    """`../analysis/x.md?plain=1#L40` -> `../analysis/x.md`."""
    t = target.strip().split(" ", 1)[0]
    return t.split("#", 1)[0].split("?", 1)[0]


def _is_local(target: str) -> bool:
    t = target.strip()
    if not t or t.startswith("#"):
        return False
    lowered = t.lower()
    return "://" not in lowered and not lowered.startswith(("mailto:", "tel:"))


def _links_into_a_rewrite(target: str) -> bool:
    """True when the target points into `analysis/` or `comparison/`."""
    cand = _strip_link_target(target).lstrip("./")
    while cand.startswith("../"):
        cand = cand[3:]
    return cand.startswith(_REWRITE_TRACKS)


def _check_head(lines: list[str], month: str, findings: list[tuple[int, str]]) -> int | None:
    """H1 and the metadata line; returns the stated open-decision count."""
    if not lines or not _H1.match(lines[0].rstrip("\n")):
        findings.append((1, "H1 must read `# 결정 스트레스 테스트 — YYYY-MM` (AUTHORING §2)"))
    else:
        h1_month = _H1.match(lines[0].rstrip("\n")).group(1)
        if h1_month != month:
            findings.append((1, f"H1 month {h1_month} disagrees with the filename month {month}"))

    for lineno, raw in enumerate(lines[1:], start=2):
        line = raw.rstrip("\n")
        if line.startswith("## "):
            break
        if not line.startswith("**Window:"):
            continue
        m = _META.match(line)
        if not m:
            findings.append((
                lineno,
                "metadata line must read `**Window:** YYYY-MM-DD → YYYY-MM-DD · "
                "**Reports read:** n · **Rewrites landed:** n · **Open decisions:** n` "
                "(AUTHORING §2)",
            ))
            return None
        return int(m.group(1))

    findings.append((2, "memo is missing its `**Window:**` metadata line (AUTHORING §2)"))
    return None


def _split_decisions(lines: list[str]):
    """[(lineno, match, body)] for each `##` section, body = [(lineno, text)]."""
    out: list[tuple[int, re.Match[str] | None, str, list[tuple[int, str]]]] = []
    cur = None
    for lineno, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")
        if line.startswith("## "):
            if cur:
                out.append(cur)
            cur = (lineno, _DECISION_H2.match(line), line, [])
        elif cur:
            cur[3].append((lineno, line))
    if cur:
        out.append(cur)
    return out


def _check_subsections(start: int, body, findings: list[tuple[int, str]]) -> None:
    seen = [(lineno, m.group(1)) for lineno, line in body if (m := _SUB.match(line))]
    names = [name for _lineno, name in seen]
    if names == list(_SUBSECTIONS):
        return
    for lineno, name in seen:
        if name not in _SUBSECTIONS:
            findings.append((
                lineno,
                f"`### {name}` is not one of the four subsections "
                f"({' / '.join(_SUBSECTIONS)}) — AUTHORING §2",
            ))
    for name in _SUBSECTIONS:
        if names.count(name) > 1:
            repeat = [ln for ln, n in seen if n == name][1]
            findings.append((repeat, f"`### {name}` appears twice in one section (AUTHORING §2)"))
    for missing in [n for n in _SUBSECTIONS if n not in names]:
        findings.append((start, f"decision section is missing `### {missing}` (AUTHORING §2)"))
    kept = [n for n in names if n in _SUBSECTIONS]
    if kept != list(_SUBSECTIONS) and sorted(set(kept)) == sorted(_SUBSECTIONS):
        findings.append((
            start,
            "the four `###` run 현재 결정 → 무엇이 뒤집는가 → 이달의 증거 → 제안 문안 "
            f"(AUTHORING §2), this section runs {' → '.join(kept)}",
        ))


def _evidence_lines(body) -> list[tuple[int, str]]:
    """The lines of the `### 이달의 증거` subsection."""
    out: list[tuple[int, str]] = []
    inside = False
    for lineno, line in body:
        m = _SUB.match(line)
        if m:
            inside = m.group(1) == "이달의 증거"
            continue
        if inside:
            out.append((lineno, line))
    return out


def _check_verdict(ident: str, body, findings: list[tuple[int, str]], start: int) -> None:
    evidence = _evidence_lines(body)
    in_evidence = {n for n, _line in evidence}
    stated = [(n, line) for n, line in body if line.startswith("**판정:**")]

    if not stated:
        findings.append((start, f"{ident}: no `**판정:**` line (AUTHORING §3)"))
        return
    for lineno, _line in stated[1:]:
        findings.append((
            lineno,
            f"{ident}: a decision carries exactly one 판정 line (AUTHORING §3)",
        ))

    lineno, line = stated[0]
    if lineno not in in_evidence:
        findings.append((
            lineno,
            f"{ident}: the 판정 line closes `### 이달의 증거`, after the evidence table "
            "(AUTHORING §3)",
        ))
    m = _VERDICT_LINE.match(line)
    if m is None:
        findings.append((
            lineno,
            f"{ident}: 판정 line must read `**판정:** <{' | '.join(_VERDICTS)}> — <한 줄>` "
            "(AUTHORING §3)",
        ))
        return
    state, rest = m.group(1), m.group(2)
    if state not in _VERDICTS:
        findings.append((
            lineno,
            f"{ident}: 판정 is one of {' / '.join(_VERDICTS)}, got {state!r} (AUTHORING §3)",
        ))

    cited = any(
        _links_into_a_rewrite(t)
        for n, ev in evidence
        for t in _MD_LINK.findall(ev)
        if _is_local(t) and not ev.startswith("**판정:**")
    )
    has_token = rest.rstrip().endswith(_TOKEN)
    if not cited and not has_token:
        findings.append((
            lineno,
            f"{ident}: every 출처 in the evidence table is a scouting line, so the 판정 line "
            f"ends with `{_TOKEN}` (AUTHORING §3)",
        ))
    if cited and has_token:
        findings.append((
            lineno,
            f"{ident}: the evidence table cites a rewrite or a comparison, so `{_TOKEN}` "
            "is wrong — the token marks a verdict resting on reports alone (AUTHORING §3)",
        ))


def _check_links(path: str, lines: list[str], findings: list[tuple[int, str]]) -> None:
    doc_dir = os.path.dirname(os.path.join(_REPO_ROOT, path))
    for lineno, raw in enumerate(lines, start=1):
        for target in _MD_LINK.findall(raw):
            if not _is_local(target):
                continue
            cand = _strip_link_target(target)
            if not cand:
                continue
            if any(os.path.exists(os.path.join(base, cand)) for base in (doc_dir, _REPO_ROOT)):
                continue
            findings.append((lineno, f"link target does not exist -> {cand} (AUTHORING §2)"))


def check_file(path: str) -> list[tuple[int, str]]:
    abs_path = path if os.path.isabs(path) else os.path.join(_REPO_ROOT, path)
    try:
        with open(abs_path, encoding="utf-8") as fh:
            lines = fh.readlines()
    except OSError as e:
        return [(0, f"<could not read: {e}>")]

    month = _memo_month(abs_path)
    if month is None:
        return [(0, "filename must be `YYYY-MM.md`")]

    findings: list[tuple[int, str]] = []
    stated_open = _check_head(lines, month, findings)

    for lineno, raw in enumerate(lines, start=1):
        if _LOG_ENTRY.match(raw):
            findings.append((
                lineno,
                "a 제안 문안 is a bullet inside a ```markdown fence, never a `#### [D` "
                "heading — the log's own entry form (AUTHORING §4)",
            ))

    sections = _split_decisions(lines)
    covered: dict[str, int] = {}
    for start, match, header, body in sections:
        if match is None:
            findings.append((
                start,
                f"`##` header must read `## D<id> — <title> (P<m>)` (AUTHORING §2): {header!r}",
            ))
            continue
        covered[match.group(1)] = start
        _check_subsections(start, body, findings)
        _check_verdict(match.group(1), body, findings, start)

    expected = open_decisions()
    by_id = {ident: (title, pillar) for ident, title, pillar in expected}
    for ident, title, pillar in expected:
        if ident not in covered:
            findings.append((
                1,
                f"{ident} is OPEN in context/P{pillar}.md but the memo has no "
                f"`## {ident}` section — the memo covers exactly the OPEN set (AUTHORING §2)",
            ))
    for start, match, _header, _body in sections:
        if match is None:
            continue
        ident = match.group(1)
        if ident not in by_id:
            findings.append((
                start,
                f"{ident} is not OPEN in any Decision Log — a settled decision is not "
                "stress-tested (AUTHORING §2)",
            ))
            continue
        title, pillar = by_id[ident]
        if (match.group(2), int(match.group(3))) != (title, pillar):
            findings.append((
                start,
                f"{ident} header must repeat the Decision Log verbatim: "
                f"`## {ident} — {title} (P{pillar})` (AUTHORING §2)",
            ))

    if stated_open is not None and stated_open != len(covered):
        findings.append((
            2,
            f"`Open decisions:` is {stated_open} but the memo carries {len(covered)} "
            "decision section(s) (AUTHORING §2)",
        ))

    _check_links(path, lines, findings)
    return sorted(findings)


def _gather_default_memos() -> list[str]:
    return sorted(
        os.path.relpath(p, _REPO_ROOT)
        for p in glob.glob(os.path.join(_REPO_ROOT, _MEMO_GLOB))
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check stress-test memos against the decisions/AUTHORING.md contract."
    )
    parser.add_argument("paths", nargs="*", help=f"memos to scan (default: {_MEMO_GLOB})")
    args = parser.parse_args(argv)

    memos = args.paths or _gather_default_memos()
    if not memos:
        sys.stderr.write("[check-decisions-format] nothing to scan\n")
        return 2

    floor = _first_month_in_scope()
    in_scope = [m for m in memos if (mm := _memo_month(m)) is not None and mm >= floor]
    skipped = len(memos) - len(in_scope)
    if not in_scope:
        print(
            f"[check-decisions-format] clean — no memo covering {floor} or later "
            f"({skipped} earlier memo(s) out of scope)"
        )
        return 0

    total = 0
    for memo in in_scope:
        for lineno, message in check_file(memo):
            total += 1
            print(f"{memo}:{lineno}: {message}")

    if total:
        print(f"\n[check-decisions-format] {total} violation(s) across {len(in_scope)} memo(s)")
        return 1
    print(
        f"[check-decisions-format] clean — {len(in_scope)} memo(s) scanned"
        + (f", {skipped} earlier memo(s) out of scope" if skipped else "")
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
