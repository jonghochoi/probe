#!/usr/bin/env python3
"""Check that `context/` keeps the shape its own documents promise.

`context/_TEMPLATE.md` defines the pillar section spine, `context/MASTER.md`
§4 states how many decisions each pillar holds and which sections MASTER owns,
and `context/CLAUDE.md` restates that ownership — every one of those is a claim
some other file has to keep true, and nothing reads them back. This lint turns
the four claims into checks:

  1. SPINE — every `context/P<n>.md` carries the `## N.` sections
     `context/_TEMPLATE.md` defines. The spine is read from the template at run
     time, so a section added there is demanded everywhere with no code change.
  2. COUNT — each row of MASTER §4's pillar table states a decision count equal
     to the number of `#### [D…]` headings in the pillar file the row names.
  3. SECTION — every section name a document claims MASTER owns resolves to a
     real `## ` heading in MASTER. The claims live in two closed forms: the
     blockquote at the top of a pillar file ("… are `context/MASTER.md`'s") and
     the ownership sentence in `context/CLAUDE.md` ("`MASTER.md` holds only
     what crosses pillars — …").
  4. PILLARSET — prose claims about how many pillars exist ("five pillars",
     "다섯 루틴") match the number of `context/P<n>.md` files, and a `P<a>–P<b>`
     range token covers exactly that set.

Precision over recall, mirroring the repo's other gates. SECTION resolves a
claim by a deliberately small normalization — lowercase, drop a leading `the`,
drop the `## N.` number and the trailing `[STABLE]`-style markers, then accept
an exact match or a word-prefix of a heading (`Venue` → `Venue Priority`) —
plus two aliases for the names MASTER files under a different heading, listed
in `_SECTION_ALIASES`. PILLARSET only fires on a number word directly
qualifying pillar/routine, so "six gates" and "five helpers" are left alone.

Usage (repo root):
    python3 linters/check-context-consistency.py [PATH ...]

No PATH -> scan `context/` (MASTER, every pillar, the folder rule file) plus
the index docs that carry pillar-set prose: `CLAUDE.md`, every
`<dir>/CLAUDE.md`, `README.md` and `scouting/SETUP.md`. `context/_TEMPLATE.md`
is the spine's source rather than a scan target. The anchors a check needs
(the template, MASTER, the pillar files) are resolved next to the doc being
scanned, so a copy of `context/` elsewhere can be scanned by passing its files
as PATH args.

Exit codes: 0 = clean / 1 = inconsistencies found / 2 = nothing to scan.
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Default scan set, gathered the way `linters/check-doc-links.py` gathers its
# own: a short list of root docs plus globs, so a new pillar or a new folder
# rule file needs no edit here.
_DEFAULT_ROOT_DOCS = [
    "CLAUDE.md",
    "README.md",
    "scouting/SETUP.md",
    "context/MASTER.md",
]
_CONTEXT_PILLAR_GLOB = "context/P[0-9].md"
_FOLDER_RULE_GLOB = "*/CLAUDE.md"

_PILLAR_FILE = re.compile(r"^P(\d)\.md$")
_TEMPLATE_NAME = "_TEMPLATE.md"
_MASTER_NAME = "MASTER.md"

# A `## N. Title [MARKER] [MARKER]` heading; the number is the spine position.
_NUMBERED_HEADING = re.compile(r"^##\s+(\d+)\.\s+(.+?)\s*$")
# Any `## ` heading, numbered or not — MASTER's own section list.
_ANY_H2 = re.compile(r"^##\s+(.+?)\s*$")
_TRAILING_MARKERS = re.compile(r"\s*\[[^\]]*\]")
# The per-pillar tag a section title carries in a pillar file or the template
# (`## 2. Decision Log — P0`, `## 2. Decision Log — P<N>`).
_PILLAR_TAG = re.compile(r"\s*[—-]\s*P(?:\d+|<N>)\s*$")

_DECISION_HEADING = re.compile(r"^####\s+\[D")

# MASTER §4's pillar table: a header row naming a `Decisions` cell and a `File`
# cell, then one row per pillar.
_TABLE_ROW = re.compile(r"^\s*\|(.+)\|\s*$")
_TABLE_RULE = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
_PILLAR_LABEL = re.compile(r"^\**P(\d)\**\b")

# The two closed claim forms. Both run over a whitespace-flattened copy of the
# doc, so a claim wrapped across lines still matches.
_CLAIM_BLOCKQUOTE = re.compile(r"([^.—]+?)\s+are\s+`?context/MASTER\.md`?", re.I)
_CLAIM_OWNERSHIP = re.compile(
    r"`?MASTER\.md`?\s+holds only what crosses pillars\s*—\s*([^.]+)"
)
_CLAIM_SPLIT = re.compile(r",|\band\b")
# List glue that is not a section name.
_CLAIM_STOPWORDS = {"those", "that", "which", "it", "them"}

# Claims MASTER files under a heading of another name. Two entries, each a
# pointer the documents already make explicit: a pillar's `Thesis tie` points
# at MASTER §1 Identity, and the pillar overview is MASTER §4 Pillars — written
# as a range so a new pillar does not need an entry here.
_SECTION_ALIASES = (
    (re.compile(r"^thesis$"), "identity"),
    (re.compile(r"^(?:pillars?|p\d+-p\d+) overview$"), "pillars"),
)

_NUMBER_WORDS = {
    "five": 5, "six": 6, "seven": 7,
    "다섯": 5, "여섯": 6, "일곱": 7,
}
_PILLAR_COUNT_EN = re.compile(r"\b(five|six|seven)\s+(pillars?|routines?)\b", re.I)
_PILLAR_COUNT_KO = re.compile(r"(다섯|여섯|일곱)\s*(?:개(?:의)?\s*)?(필러|루틴)")
_PILLAR_RANGE = re.compile(r"\bP(\d)\s*[–—-]\s*P(\d)")

_DASHES = str.maketrans({"–": "-", "—": "-"})


# ── Reading helpers ───────────────────────────────────────────────────────


def _abs(path: str) -> str:
    return path if os.path.isabs(path) else os.path.join(_REPO_ROOT, path)


def _display(path: str) -> str:
    """Repo-relative when the file is in the repo, as given when it is not."""
    rel = os.path.relpath(path, _REPO_ROOT)
    return rel if not rel.startswith(os.pardir) else path


def _read_lines(path: str) -> list[str] | None:
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read().splitlines()
    except OSError:
        return None


def _flatten(lines: list[str]) -> tuple[str, list[int]]:
    """One whitespace-joined string plus the source line number of each char."""
    parts: list[str] = []
    line_of: list[int] = []
    for lineno, raw in enumerate(lines, start=1):
        text = re.sub(r"^\s*>\s?", "", raw).strip()
        piece = text + " "
        parts.append(piece)
        line_of.extend([lineno] * len(piece))
    return "".join(parts), line_of


def _line_at(line_of: list[int], offset: int) -> int:
    if not line_of:
        return 1
    return line_of[min(max(offset, 0), len(line_of) - 1)]


def _normalize_title(title: str) -> str:
    """`## 2. Decision Log — P0 [LIVING]` -> `decision log`."""
    text = _TRAILING_MARKERS.sub("", title)
    text = _PILLAR_TAG.sub("", text)
    text = text.translate(_DASHES).strip().strip("*` ")
    return re.sub(r"\s+", " ", text).lower()


def _normalize_claim(name: str) -> str:
    text = name.translate(_DASHES).strip().strip("*`\"' ")
    text = re.sub(r"^the\s+", "", text, flags=re.I)
    text = re.sub(r"'s$", "", text)
    return re.sub(r"\s+", " ", text).lower()


# ── Anchor resolution (works on a copy of `context/` too) ─────────────────


def _context_dir_for(doc_abs: str) -> str | None:
    """The `context/` the scanned doc belongs to, or the repo's own."""
    own = os.path.dirname(doc_abs)
    if os.path.exists(os.path.join(own, _MASTER_NAME)):
        return own
    nested = os.path.join(own, "context")
    if os.path.exists(os.path.join(nested, _MASTER_NAME)):
        return nested
    fallback = os.path.join(_REPO_ROOT, "context")
    return fallback if os.path.exists(os.path.join(fallback, _MASTER_NAME)) else None


def _pillar_files(context_dir: str) -> list[str]:
    return sorted(glob.glob(os.path.join(context_dir, "P[0-9].md")))


def _pillar_indices(context_dir: str) -> list[int]:
    out = []
    for path in _pillar_files(context_dir):
        m = _PILLAR_FILE.match(os.path.basename(path))
        if m:
            out.append(int(m.group(1)))
    return sorted(out)


# ── SPINE ─────────────────────────────────────────────────────────────────


def _template_spine(template_path: str) -> list[tuple[int, str, str]]:
    """(number, normalized title, raw title) for each `## N.` in the template."""
    lines = _read_lines(template_path)
    if lines is None:
        return []
    spine = []
    for raw in lines:
        m = _NUMBERED_HEADING.match(raw)
        if m:
            title = _TRAILING_MARKERS.sub("", m.group(2)).strip()
            spine.append((int(m.group(1)), _normalize_title(m.group(2)), title))
    return spine


def check_spine(doc: str, lines: list[str], context_dir: str) -> list[tuple[int, str]]:
    template = os.path.join(context_dir, _TEMPLATE_NAME)
    spine = _template_spine(template)
    if not spine:
        return []

    present: dict[str, int] = {}
    for lineno, raw in enumerate(lines, start=1):
        m = _NUMBERED_HEADING.match(raw)
        if m:
            present[_normalize_title(m.group(2))] = lineno

    findings = []
    for idx, (number, norm, title) in enumerate(spine):
        if norm in present:
            continue
        # Name the line the section belongs on: the next spine section that is
        # there, or the end of the file when it is the tail of the spine.
        following = [present[n] for _, n, _ in spine[idx + 1:] if n in present]
        at = min(following) if following else max(len(lines), 1)
        findings.append(
            (at, f'SPINE missing section "## {number}. {title}" — '
                 f"{_display(template)} defines the spine")
        )
    return findings


# ── COUNT ─────────────────────────────────────────────────────────────────


def _split_row(raw: str) -> list[str]:
    m = _TABLE_ROW.match(raw)
    return [c.strip() for c in m.group(1).split("|")] if m else []


def _decision_count(path: str) -> int | None:
    lines = _read_lines(path)
    if lines is None:
        return None
    return sum(1 for raw in lines if _DECISION_HEADING.match(raw))


def check_count(doc: str, lines: list[str], context_dir: str) -> list[tuple[int, str]]:
    findings: list[tuple[int, str]] = []
    cols: dict[str, int] | None = None
    for lineno, raw in enumerate(lines, start=1):
        cells = _split_row(raw)
        if not cells:
            cols = None
            continue
        if _TABLE_RULE.match(raw):
            continue
        lowered = [c.lower() for c in cells]
        if "decisions" in lowered and "file" in lowered:
            cols = {"count": lowered.index("decisions"), "file": lowered.index("file")}
            continue
        if cols is None or max(cols.values()) >= len(cells):
            continue

        label = _PILLAR_LABEL.match(cells[0])
        if not label:
            continue
        pillar = f"P{label.group(1)}"
        stated = cells[cols["count"]].strip("* ")
        if not stated.isdigit():
            continue
        target = cells[cols["file"]].strip("`* ")
        # The sibling file first, so a copy of `context/` checks against its
        # own pillars rather than the repo's.
        candidates = [os.path.join(context_dir, os.path.basename(target)), _abs(target)]
        resolved = next((c for c in candidates if os.path.exists(c)), None)
        if resolved is None:
            findings.append(
                (lineno, f"COUNT {pillar} row names {target}, which does not exist")
            )
            continue
        actual = _decision_count(resolved)
        if actual is None:
            continue
        if int(stated) != actual:
            findings.append(
                (lineno, f"COUNT {pillar} row states {stated} decisions; "
                         f"{_display(resolved)} holds {actual} "
                         f"`#### [D…]` heading(s)")
            )
    return findings


# ── SECTION ───────────────────────────────────────────────────────────────


def _master_headings(master_path: str) -> list[tuple[str, str]]:
    """(normalized, raw) for every `## ` heading in MASTER."""
    lines = _read_lines(master_path)
    if lines is None:
        return []
    out = []
    for raw in lines:
        m = _ANY_H2.match(raw)
        if not m:
            continue
        title = _TRAILING_MARKERS.sub("", m.group(1)).strip()
        out.append((_normalize_title(re.sub(r"^\d+\.\s*", "", title)),
                    re.sub(r"^\d+\.\s*", "", title)))
    return out


def _resolves_to_heading(claim: str, headings: list[tuple[str, str]]) -> bool:
    for pattern, target in _SECTION_ALIASES:
        if pattern.match(claim):
            claim = target
            break
    for norm, _raw in headings:
        if claim == norm or norm.startswith(claim + " "):
            return True
    return False


def check_section(doc: str, lines: list[str], context_dir: str) -> list[tuple[int, str]]:
    master = os.path.join(context_dir, _MASTER_NAME)
    headings = _master_headings(master)
    if not headings:
        return []

    flat, line_of = _flatten(lines)
    findings: list[tuple[int, str]] = []
    for pattern in (_CLAIM_BLOCKQUOTE, _CLAIM_OWNERSHIP):
        for m in pattern.finditer(flat):
            group, start = m.group(1), m.start(1)
            for piece in _CLAIM_SPLIT.split(group):
                raw = piece.strip()
                claim = _normalize_claim(raw)
                if not claim or claim in _CLAIM_STOPWORDS:
                    continue
                if "/" in claim or claim.endswith(".md"):
                    continue
                if _resolves_to_heading(claim, headings):
                    continue
                offset = flat.find(raw, start, m.end(1))
                findings.append(
                    (_line_at(line_of, offset if offset >= 0 else start),
                     f'SECTION claim "{raw}" names no `## ` heading in '
                     f"{_display(master)} "
                     f"(headings: {', '.join(h for _n, h in headings)})")
                )
    return findings


# ── PILLARSET ─────────────────────────────────────────────────────────────


def check_pillarset(doc: str, lines: list[str], context_dir: str) -> list[tuple[int, str]]:
    indices = _pillar_indices(context_dir)
    if not indices:
        return []
    actual, lo, hi = len(indices), indices[0], indices[-1]

    findings: list[tuple[int, str]] = []
    in_fence = False
    for lineno, raw in enumerate(lines, start=1):
        if raw.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        for pattern in (_PILLAR_COUNT_EN, _PILLAR_COUNT_KO):
            for m in pattern.finditer(raw):
                stated = _NUMBER_WORDS[m.group(1).lower()]
                if stated != actual:
                    findings.append(
                        (lineno, f'PILLARSET "{m.group(0)}" claims {stated}; '
                                 f"context/ holds {actual} pillar file(s) "
                                 f"(P{lo}–P{hi})")
                    )
        for m in _PILLAR_RANGE.finditer(raw):
            if (int(m.group(1)), int(m.group(2))) != (lo, hi):
                findings.append(
                    (lineno, f'PILLARSET range "{m.group(0)}" does not cover the '
                             f"pillar set P{lo}–P{hi} ({actual} file(s) in context/)")
                )
    return findings


# ── Driver ────────────────────────────────────────────────────────────────


def check_file(path: str) -> tuple[list[tuple[int, str]], bool]:
    """Findings for one doc, and whether any check could run against it."""
    abs_path = _abs(path)
    lines = _read_lines(abs_path)
    if lines is None:
        return [(0, f"<could not read {path}>")], True

    context_dir = _context_dir_for(abs_path)
    if context_dir is None:
        return [], False

    name = os.path.basename(abs_path)
    findings = list(check_pillarset(path, lines, context_dir))
    findings += check_section(path, lines, context_dir)
    if _PILLAR_FILE.match(name):
        findings += check_spine(path, lines, context_dir)
    if name == _MASTER_NAME:
        findings += check_count(path, lines, context_dir)
    return sorted(findings), True


def _gather_default_docs() -> list[str]:
    docs = [d for d in _DEFAULT_ROOT_DOCS if os.path.exists(_abs(d))]
    for pattern in (_CONTEXT_PILLAR_GLOB, _FOLDER_RULE_GLOB):
        docs += sorted(
            os.path.relpath(p, _REPO_ROOT)
            for p in glob.glob(os.path.join(_REPO_ROOT, pattern))
        )
    return docs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check that context/ keeps the shape its documents promise."
    )
    parser.add_argument(
        "paths", nargs="*", help="docs to scan (default: context/ plus the index docs)"
    )
    args = parser.parse_args(argv)

    docs = args.paths or _gather_default_docs()
    if not docs:
        sys.stderr.write("[check-context-consistency] nothing to scan\n")
        return 2

    total = 0
    checked = 0
    for doc in docs:
        findings, ran = check_file(doc)
        checked += int(ran)
        for lineno, msg in findings:
            total += 1
            print(f"{doc}:{lineno}: {msg}")

    if not checked:
        sys.stderr.write(
            "[check-context-consistency] nothing to scan — no context/ anchor found\n"
        )
        return 2
    if total:
        print(f"\n[check-context-consistency] {total} inconsistency(ies) "
              f"across {len(docs)} doc(s)")
        return 1
    print(f"[check-context-consistency] clean — {len(docs)} doc(s) scanned")
    return 0


if __name__ == "__main__":
    sys.exit(main())
