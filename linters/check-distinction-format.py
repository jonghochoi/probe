#!/usr/bin/env python3
"""Check the distinction track's private folder against distinction/AUTHORING.md.

The distinction track writes nothing into the repository: its ledgers, matrix
and deltas hold the method beside the papers, so they live in a private folder
on the machine that runs `/distinguish` (`distinction/SETUP.md` §2). No build
reads them and no workflow can, which makes this lint the track's only gate —
the routine runs it before saving (prompt step 6), and a human runs it after
editing a document by hand.

Checks, grouped by the contract section they enforce:

  AUTHORING §1   every `ledger/<id>.md` names a `BASKET.md` row and the
             checkout holds `analysis/<id>.md`.
  AUTHORING §3-1 the ledger — an H1, the five-field metadata line, the seven
             `##` headers verbatim and in order with no other `##`.
  AUTHORING §3-1 / §4  per section, every bullet carries the anchors its row
             of the table requires or is `- 없음`; a §4 bullet opens with a
             verdict; §7 holds a `cfg:` anchor.
  AUTHORING §3-2 the matrix — rows are METHOD's claims, columns the active
             rewritten basket, each cell opening with a verdict.
  AUTHORING §3-3 the delta — the H1 date is the file's, the seven headers, at
             most three `###` under `5`, a closing `probe-state` fence that
             parses and carries every key.
  AUTHORING §3-4 every `###` idea carries the five labels in order, and a
             `D#` it names exists in a pillar's Decision Log.
  AUTHORING §5   active rows <= 12, ideas per ledger <= 2, ledger prose
             <= 7,000 characters outside fences.
  AUTHORING §7   no `METHOD.md` §6 string in any output.
  inputs         `BASKET.md` rows parse — id, role and status from their
             sets, no duplicate id; `METHOD.md` carries its spine and one
             bullet per `#### [C#]`.

Precision over recall, mirroring the repo's other gates: every check keys off
a literal token the contract fixes. Whether a difference is a difference, and
whether a gap came from the paper's own ablation, is reading (AUTHORING §8).

Usage (repo root):
    python3 linters/check-distinction-format.py [PRIVATE_DIR]

No PRIVATE_DIR -> `$PROBE_PRIVATE_DIR`. The checkout's `analysis/` and
`context/` are resolved next to this file.

Exit codes: 0 = clean / 1 = violations found / 2 = no folder to scan.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_ARXIV_ID = re.compile(r"^\d{4}\.\d{5}$")
_LEDGER_NAME = re.compile(r"^(\d{4}\.\d{5})\.md$")
_RUN_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")

_ROLES = ("baseline", "nearest", "threat", "donor")
_STATUSES = ("active", "parked", "graduated")
_VERDICTS = ("지지", "무관", "위협", "반박")
_FILL_VERDICTS = ("메운다", "부분", "못 메운다")
_NONE = "- 없음"

_ACTIVE_CAP = 12
_IDEAS_PER_LEDGER = 2
_IDEAS_PER_RUN = 3
_LEDGER_PROSE_MAX = 7000

_LEDGER_SPINE = (
    "## 1 공통", "## 2 차이", "## 3 그들의 빈자리", "## 4 내 방법이 메우는가",
    "## 5 그들을 개선할 아이디어", "## 6 위협", "## 7 최저가 반증 실험",
)
_RUN_SPINE = (
    "## 1 코퍼스 변화", "## 2 바구니 변화", "## 3 방법론 변화", "## 4 매트릭스 전이",
    "## 5 새 아이디어", "## 6 제안", "## 7 다음 행동",
)
_METHOD_SPINE = (
    "## 0. 문제의식", "## 1. 주장", "## 2. 방법", "## 3. 측정",
    "## 4. 알려진 약점", "## 5. 진행 중", "## 6. 외부 발화 금지",
)
_IDEA_LABELS = (
    "**조합**", "**왜 어느 쪽도 혼자 못 하나**", "**움직이는 결정**",
    "**가장 싼 반증 실험**", "**이미 있는 것**",
)
_STATE_KEYS = ("run", "corpus_head", "method", "codemap", "basket", "related")

_H1 = re.compile(r"^# \S")
_H2 = re.compile(r"^## ")
_H3 = re.compile(r"^### ")
_BULLET = re.compile(r"^- ")
_FENCE = re.compile(r"^\s*(```|~~~)")

_LEDGER_META = re.compile(
    r"^Role: (baseline|nearest|threat|donor) · Claims: (C\d+(?:, C\d+)*) · "
    r"Rewrite: analysis/(\d{4}\.\d{5})\.md · Method: [0-9a-f]{7} · Run: \d{4}-\d{2}-\d{2}$"
)
_MATRIX_META = re.compile(r"^Method: [0-9a-f]{7} · Run: \d{4}-\d{2}-\d{2}$")
_RUN_H1 = re.compile(r"^# (\d{4}-\d{2}-\d{2}) 차별화 델타$")
_MATRIX_H1 = "# 주장 × 바구니"

# Anchor grammars (AUTHORING §4).
_PAPER_ANCHOR = re.compile(r"`[^`§]+ §[1-4] [^`]+`")
_CLAIM_ANCHOR = re.compile(r"`C\d+`")
_METHOD_ANCHOR = re.compile(r"`METHOD §[0-6]`")
_CODE_ANCHOR = re.compile(r"`[^`\s:]+:\d+`")
_CFG_ANCHOR = re.compile(r"`cfg:[^`\s]+`")
_CLAIM_TOKEN = re.compile(r"\bC(\d+)\b")
_DECISION_TOKEN = re.compile(r"\bD\d[A-Z]{2}\b")
_CLAIM_HEADING = re.compile(r"^#### \[(C\d+)\] \S")
_DECISION_HEADING = re.compile(r"^#### \[(D\d[A-Z]{2})\]")
_TABLE_ROW = re.compile(r"^\s*\|(.+)\|\s*$")
_TABLE_RULE = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
_MATRIX_HEAD_CELL = re.compile(r"^.+ \((\d{4}\.\d{5})\)$")

Finding = tuple[str, int, str]


# ── Reading helpers ───────────────────────────────────────────────────────


def _read(path: str) -> list[str] | None:
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read().splitlines()
    except OSError:
        return None


def _split_row(raw: str) -> list[str]:
    m = _TABLE_ROW.match(raw)
    return [c.strip() for c in m.group(1).split("|")] if m else []


def _sections(lines: list[str], level: re.Pattern) -> list[tuple[str, int, list[tuple[int, str]]]]:
    """(header, line, [(line, text)…]) per header of `level`, fences kept."""
    out: list[tuple[str, int, list[tuple[int, str]]]] = []
    for lineno, raw in enumerate(lines, start=1):
        if level.match(raw):
            out.append((raw.rstrip(), lineno, []))
        elif out:
            out[-1][2].append((lineno, raw))
    return out


def _outside_fences(body: list[tuple[int, str]]) -> list[tuple[int, str]]:
    out, in_fence = [], False
    for lineno, raw in body:
        if _FENCE.match(raw):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append((lineno, raw))
    return out


def _top_bullets(body: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """Top-level `- ` bullets with their continuation lines folded in."""
    out: list[tuple[int, str]] = []
    for lineno, raw in _outside_fences(body):
        if _BULLET.match(raw):
            out.append((lineno, raw))
        elif out and raw.startswith("  ") and raw.strip():
            out[-1] = (out[-1][0], out[-1][1] + " " + raw.strip())
    return out


# ── Inputs: BASKET.md and METHOD.md ───────────────────────────────────────


def read_basket(path: str, findings: list[Finding]) -> dict[str, dict]:
    """id -> {alias, role, claims, status}; findings for rows that do not parse."""
    lines = _read(path)
    name = os.path.basename(path)
    if lines is None:
        findings.append((name, 0, "inputs: BASKET.md is unreadable"))
        return {}
    rows: dict[str, dict] = {}
    header_seen = False
    for lineno, raw in enumerate(lines, start=1):
        cells = _split_row(raw)
        if not cells or _TABLE_RULE.match(raw):
            continue
        if not header_seen:
            header_seen = cells[:5] == ["arXiv", "alias", "role", "claims", "status"]
            if not header_seen:
                findings.append((name, lineno, "inputs: table header is not `| arXiv | alias | role | claims | status | note |` (SETUP §2-1)"))
                return {}
            continue
        if len(cells) < 5:
            findings.append((name, lineno, "inputs: row has fewer than five cells (SETUP §2-1)"))
            continue
        pid, alias, role, claims, status = cells[:5]
        if not _ARXIV_ID.match(pid):
            findings.append((name, lineno, f"inputs: `{pid}` is not a bare arXiv id (SETUP §2-1)"))
            continue
        if pid in rows:
            findings.append((name, lineno, f"inputs: duplicate basket row for {pid} (SETUP §2-1)"))
            continue
        if role not in _ROLES:
            findings.append((name, lineno, f"inputs: role `{role}` not in {', '.join(_ROLES)} (SETUP §2-1)"))
        if status not in _STATUSES:
            findings.append((name, lineno, f"inputs: status `{status}` not in {', '.join(_STATUSES)} (SETUP §2-1)"))
        claim_ids = [c.strip() for c in claims.split(",") if c.strip()]
        rows[pid] = {"alias": alias, "role": role, "claims": claim_ids, "status": status, "line": lineno}
    active = sum(1 for r in rows.values() if r["status"] == "active")
    if active > _ACTIVE_CAP:
        findings.append((name, 0, f"§5 {active} active rows, cap is {_ACTIVE_CAP}"))
    return rows


def read_method(path: str, findings: list[Finding]) -> tuple[set[str], list[str]]:
    """(claim ids, forbidden strings); findings for a spine or claim-format slip."""
    lines = _read(path)
    name = os.path.basename(path)
    if lines is None:
        findings.append((name, 0, "inputs: METHOD.md is unreadable"))
        return set(), []
    headers = [raw.rstrip() for raw in lines if _H2.match(raw)]
    for want in _METHOD_SPINE:
        if want not in headers:
            findings.append((name, 0, f'inputs: METHOD.md lacks "{want}" (SETUP §2-2)'))
    claims: set[str] = set()
    forbidden: list[str] = []
    for header, lineno, body in _sections(lines, _H2):
        if header == _METHOD_SPINE[1]:
            pending: tuple[str, int] | None = None
            for ln, raw in _outside_fences(body):
                m = _CLAIM_HEADING.match(raw)
                if m:
                    if pending:
                        findings.append((name, pending[1], f"inputs: {pending[0]} has no bullet under its heading (SETUP §2-2)"))
                    if m.group(1) in claims:
                        findings.append((name, ln, f"inputs: {m.group(1)} is declared twice (SETUP §2-2)"))
                    claims.add(m.group(1))
                    pending = (m.group(1), ln)
                elif _BULLET.match(raw) and pending:
                    pending = None
            if pending:
                findings.append((name, pending[1], f"inputs: {pending[0]} has no bullet under its heading (SETUP §2-2)"))
        elif header == _METHOD_SPINE[6]:
            for _, raw in _top_bullets(body):
                text = raw[2:].strip()
                if text and not (text.startswith("<") and text.endswith(">")):
                    forbidden.append(text)
    if not claims:
        findings.append((name, 0, "inputs: METHOD.md §1 declares no `#### [C<n>]` claim (SETUP §2-2)"))
    return claims, forbidden


def _decision_ids() -> set[str]:
    ids: set[str] = set()
    for path in glob.glob(os.path.join(_REPO_ROOT, "context", "P[0-9].md")):
        for raw in _read(path) or []:
            m = _DECISION_HEADING.match(raw)
            if m:
                ids.add(m.group(1))
    return ids


# ── Shared: ideas and forbidden strings ───────────────────────────────────


def _check_ideas(name: str, body: list[tuple[int, str]], cap: int, where: str,
                 decisions: set[str], findings: list[Finding]) -> None:
    ideas = _sections([raw for _, raw in body], _H3)
    # `_sections` renumbers from 1; map back to file lines through the body.
    offsets = [ln for ln, _ in body]
    if len(ideas) > cap:
        findings.append((name, offsets[ideas[cap][1] - 1], f"§5 {len(ideas)} ideas under {where}, cap is {cap}"))
    for _, rel_line, idea_body in ideas:
        at = offsets[rel_line - 1]
        labels = [raw for _, raw in idea_body if _BULLET.match(raw)]
        found = [next((lab for lab in _IDEA_LABELS if raw.startswith("- " + lab)), None) for raw in labels]
        found = [f for f in found if f]
        if found != list(_IDEA_LABELS):
            findings.append((name, at, "§3-4 idea does not carry the five labels in order: " + " · ".join(_IDEA_LABELS)))
        for raw in labels:
            if raw.startswith("- " + _IDEA_LABELS[2]):
                codes = _DECISION_TOKEN.findall(raw)
                if not codes:
                    findings.append((name, at, "§3-4 **움직이는 결정** names no `D#`"))
                for code in codes:
                    if decisions and code not in decisions:
                        findings.append((name, at, f"§3-4 {code} is in no pillar's Decision Log"))


def _check_forbidden(name: str, lines: list[str], forbidden: list[str], findings: list[Finding]) -> None:
    for lineno, raw in enumerate(lines, start=1):
        for text in forbidden:
            if text in raw:
                findings.append((name, lineno, "§7 carries a `METHOD.md` §6 string"))
                break


def _check_claim_tokens(name: str, lines: list[str], claims: set[str], findings: list[Finding]) -> None:
    for lineno, raw in enumerate(lines, start=1):
        for m in _CLAIM_ANCHOR.finditer(raw):
            code = m.group(0).strip("`")
            if code not in claims:
                findings.append((name, lineno, f"§4 `{code}` is not a claim in `METHOD.md` §1"))


# ── The ledger ────────────────────────────────────────────────────────────


def check_ledger(path: str, basket: dict[str, dict], claims: set[str], forbidden: list[str],
                 decisions: set[str]) -> list[Finding]:
    name = "ledger/" + os.path.basename(path)
    findings: list[Finding] = []
    m = _LEDGER_NAME.match(os.path.basename(path))
    if not m:
        return [(name, 0, "§3-1 file name is not `<arxiv-id>.md`")]
    pid = m.group(1)
    if pid not in basket:
        findings.append((name, 0, f"§1 {pid} is not a `BASKET.md` row"))
    if not os.path.exists(os.path.join(_REPO_ROOT, "analysis", pid + ".md")):
        findings.append((name, 0, f"§1 analysis/{pid}.md does not exist — the paper has no rewrite"))
    lines = _read(path)
    if lines is None:
        return findings + [(name, 0, "unreadable")]

    if not lines or not _H1.match(lines[0]):
        findings.append((name, 1, "§3-1 line 1 is not the H1"))
    meta_line = next((ln for ln, raw in enumerate(lines[1:], start=2) if raw.strip()), None)
    if meta_line is None or not _LEDGER_META.match(lines[meta_line - 1]):
        findings.append((name, meta_line or 2, "§3-1 metadata line is not `Role: … · Claims: … · Rewrite: analysis/<id>.md · Method: <7 hex> · Run: YYYY-MM-DD`"))
    else:
        mm = _LEDGER_META.match(lines[meta_line - 1])
        if mm.group(3) != pid:
            findings.append((name, meta_line, f"§3-1 `Rewrite:` names {mm.group(3)}, the file is {pid}"))
        row = basket.get(pid)
        if row and mm.group(1) != row["role"]:
            findings.append((name, meta_line, f"§3-1 `Role:` is {mm.group(1)}, `BASKET.md` says {row['role']}"))
        if row and row["claims"] and [c.strip() for c in mm.group(2).split(",")] != row["claims"]:
            findings.append((name, meta_line, "§3-1 `Claims:` differs from the `BASKET.md` row"))

    headers = [(raw.rstrip(), ln) for ln, raw in enumerate(lines, start=1) if _H2.match(raw)]
    if [h for h, _ in headers] != list(_LEDGER_SPINE):
        findings.append((name, headers[0][1] if headers else 0, "§3-1 the `##` headers are not the seven of the spine, verbatim and in order"))

    sections = {h: body for h, _, body in _sections(lines, _H2)}

    def bullets(key: str) -> list[tuple[int, str]]:
        return _top_bullets(sections.get(key, []))

    def need(key: str, want: str, *patterns: re.Pattern) -> None:
        for ln, raw in bullets(key):
            if raw.strip() == _NONE:
                continue
            if not all(any(p.search(raw) for p in group) for group in patterns):
                findings.append((name, ln, f"§4 bullet under {key[3:]} lacks {want}"))

    need(_LEDGER_SPINE[0], "a paper anchor and a `C#` / `METHOD §n` anchor", (_PAPER_ANCHOR,), (_CLAIM_ANCHOR, _METHOD_ANCHOR))
    need(_LEDGER_SPINE[1], "a paper anchor and a `path:line` / `cfg:key` / `METHOD §n` anchor", (_PAPER_ANCHOR,), (_CODE_ANCHOR, _CFG_ANCHOR, _METHOD_ANCHOR))
    need(_LEDGER_SPINE[2], "a paper anchor", (_PAPER_ANCHOR,))
    need(_LEDGER_SPINE[5], "a paper anchor", (_PAPER_ANCHOR,))
    for ln, raw in bullets(_LEDGER_SPINE[3]):
        if raw.strip() == _NONE:
            continue
        if not any(raw.startswith("- " + v + " ") or raw.startswith("- " + v + " —") for v in _FILL_VERDICTS):
            findings.append((name, ln, "§3-1 bullet under 내 방법이 메우는가 does not open with 메운다 / 부분 / 못 메운다"))
        if not _METHOD_ANCHOR.search(raw):
            findings.append((name, ln, "§4 bullet under 내 방법이 메우는가 lacks a `METHOD §n` anchor"))
    seven = bullets(_LEDGER_SPINE[6])
    if not seven:
        findings.append((name, 0, "§3-1 최저가 반증 실험 holds no bullet"))
    elif not any(raw.strip() == _NONE for _, raw in seven) and not any(_CFG_ANCHOR.search(raw) for _, raw in seven):
        findings.append((name, seven[0][0], "§4 최저가 반증 실험 names no `cfg:` key"))
    for key in _LEDGER_SPINE[:4] + _LEDGER_SPINE[5:6]:
        if key in sections and not bullets(key):
            findings.append((name, 0, f"§3-1 {key[3:]} holds no bullet (write `- 없음` when there is nothing)"))

    _check_ideas(name, sections.get(_LEDGER_SPINE[4], []), _IDEAS_PER_LEDGER, "그들을 개선할 아이디어", decisions, findings)

    prose = sum(len(raw) for _, raw in _outside_fences(list(enumerate(lines, start=1))))
    if prose > _LEDGER_PROSE_MAX:
        findings.append((name, 0, f"§5 {prose} characters of prose, ceiling is {_LEDGER_PROSE_MAX}"))

    _check_claim_tokens(name, lines, claims, findings)
    _check_forbidden(name, lines, forbidden, findings)
    return findings


# ── The matrix ────────────────────────────────────────────────────────────


def check_matrix(path: str, basket: dict[str, dict], claims: set[str], forbidden: list[str]) -> list[Finding]:
    name = "matrix.md"
    lines = _read(path)
    if lines is None:
        return [(name, 0, "unreadable")]
    findings: list[Finding] = []
    if not lines or lines[0].rstrip() != _MATRIX_H1:
        findings.append((name, 1, f"§3-2 line 1 is not `{_MATRIX_H1}`"))
    meta_line = next((ln for ln, raw in enumerate(lines[1:], start=2) if raw.strip()), None)
    if meta_line is None or not _MATRIX_META.match(lines[meta_line - 1]):
        findings.append((name, meta_line or 2, "§3-2 metadata line is not `Method: <7 hex> · Run: YYYY-MM-DD`"))

    expected_cols = [pid for pid, r in basket.items()
                     if r["status"] == "active" and os.path.exists(os.path.join(_REPO_ROOT, "analysis", pid + ".md"))]
    header: list[str] | None = None
    seen_rows: set[str] = set()
    for lineno, raw in enumerate(lines, start=1):
        cells = _split_row(raw)
        if not cells or _TABLE_RULE.match(raw):
            continue
        if header is None:
            header = cells
            ids = []
            for cell in cells[1:]:
                m = _MATRIX_HEAD_CELL.match(cell)
                if not m:
                    findings.append((name, lineno, f"§3-2 column head `{cell}` is not `<alias> (<arxiv-id>)`"))
                else:
                    ids.append(m.group(1))
            if ids != expected_cols:
                findings.append((name, lineno, "§3-2 columns are not the active rewritten basket rows in `BASKET.md` order"))
            continue
        label = cells[0]
        if label not in claims:
            findings.append((name, lineno, f"§3-2 row `{label}` is not a claim in `METHOD.md` §1"))
        seen_rows.add(label)
        if len(cells) != len(header):
            findings.append((name, lineno, "§3-2 row does not have one cell per column"))
        for cell in cells[1:]:
            if not any(cell == v or cell.startswith(v + " ") for v in _VERDICTS):
                findings.append((name, lineno, f"§3-2 cell `{cell[:20]}` does not open with 지지 / 무관 / 위협 / 반박"))
    if header is None:
        findings.append((name, 0, "§3-2 no table"))
    for code in sorted(claims - seen_rows):
        findings.append((name, 0, f"§3-2 claim {code} has no row"))
    _check_forbidden(name, lines, forbidden, findings)
    return findings


# ── The delta ─────────────────────────────────────────────────────────────


def check_run(path: str, claims: set[str], forbidden: list[str], decisions: set[str]) -> list[Finding]:
    name = "runs/" + os.path.basename(path)
    findings: list[Finding] = []
    m = _RUN_NAME.match(os.path.basename(path))
    if not m:
        return [(name, 0, "§3-3 file name is not `YYYY-MM-DD.md`")]
    lines = _read(path)
    if lines is None:
        return [(name, 0, "unreadable")]
    h1 = _RUN_H1.match(lines[0]) if lines else None
    if not h1:
        findings.append((name, 1, "§3-3 line 1 is not `# YYYY-MM-DD 차별화 델타`"))
    elif h1.group(1) != m.group(1):
        findings.append((name, 1, f"§3-3 H1 date {h1.group(1)} differs from the file name"))

    headers = [(raw.rstrip(), ln) for ln, raw in enumerate(lines, start=1) if _H2.match(raw)]
    if [h for h, _ in headers] != list(_RUN_SPINE):
        findings.append((name, headers[0][1] if headers else 0, "§3-3 the `##` headers are not the seven of the spine, verbatim and in order"))
    sections = {h: body for h, _, body in _sections(lines, _H2)}
    for key in _RUN_SPINE:
        if key in sections and key != _RUN_SPINE[4] and not _top_bullets(sections[key]):
            findings.append((name, 0, f"§3-3 {key[3:]} holds no bullet (write `- 없음` when nothing moved)"))
    _check_ideas(name, sections.get(_RUN_SPINE[4], []), _IDEAS_PER_RUN, "새 아이디어", decisions, findings)

    # The closing probe-state fence.
    state_start = None
    for ln in range(len(lines) - 1, -1, -1):
        if lines[ln].strip() == "```probe-state":
            state_start = ln
            break
    if state_start is None:
        findings.append((name, len(lines), "§3-3 no closing ```probe-state block"))
    else:
        payload = []
        closed = False
        for raw in lines[state_start + 1:]:
            if raw.strip() == "```":
                closed = True
                break
            payload.append(raw)
        trailing = [raw for raw in lines[state_start + 1 + len(payload) + 1:] if raw.strip()] if closed else []
        if not closed:
            findings.append((name, state_start + 1, "§3-3 probe-state fence is not closed"))
        elif trailing:
            findings.append((name, state_start + 1, "§3-3 probe-state is not the last thing in the file"))
        try:
            state = json.loads("\n".join(payload))
        except ValueError:
            state = None
            findings.append((name, state_start + 2, "§3-3 probe-state is not valid JSON"))
        if isinstance(state, dict):
            for key in _STATE_KEYS:
                if key not in state:
                    findings.append((name, state_start + 2, f"§3-3 probe-state lacks `{key}`"))
            if state.get("run") != m.group(1):
                findings.append((name, state_start + 2, "§3-3 probe-state `run` differs from the file date"))
            if not isinstance(state.get("related"), dict):
                findings.append((name, state_start + 2, "§3-3 probe-state `related` is not an object of id -> [ids]"))
        elif state is not None:
            findings.append((name, state_start + 2, "§3-3 probe-state is not a JSON object"))

    _check_claim_tokens(name, lines, claims, findings)
    _check_forbidden(name, lines, forbidden, findings)
    return findings


# ── Driver ────────────────────────────────────────────────────────────────


def check_folder(folder: str) -> list[Finding]:
    findings: list[Finding] = []
    basket = read_basket(os.path.join(folder, "BASKET.md"), findings)
    claims, forbidden = read_method(os.path.join(folder, "METHOD.md"), findings)
    decisions = _decision_ids()
    for path in sorted(glob.glob(os.path.join(folder, "ledger", "*.md"))):
        findings += check_ledger(path, basket, claims, forbidden, decisions)
    matrix = os.path.join(folder, "matrix.md")
    if os.path.exists(matrix):
        findings += check_matrix(matrix, basket, claims, forbidden)
    for path in sorted(glob.glob(os.path.join(folder, "runs", "*.md"))):
        findings += check_run(path, claims, forbidden, decisions)
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check the distinction track's private folder against distinction/AUTHORING.md."
    )
    parser.add_argument("folder", nargs="?", default=os.environ.get("PROBE_PRIVATE_DIR"),
                        help="the private folder (default: $PROBE_PRIVATE_DIR)")
    args = parser.parse_args(argv)

    if not args.folder or not os.path.isdir(args.folder):
        sys.stderr.write("[check-distinction-format] no private folder — pass a path or set PROBE_PRIVATE_DIR\n")
        return 2

    findings = check_folder(args.folder)
    for name, lineno, message in findings:
        print(f"{name}:{lineno}: {message}")
    if findings:
        print(f"\n[check-distinction-format] {len(findings)} violation(s) in {args.folder}")
        return 1
    print(f"[check-distinction-format] clean — {args.folder}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
