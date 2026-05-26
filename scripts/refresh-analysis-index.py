#!/usr/bin/env python3
"""Regenerate the auto-maintained analyses index in analysis/INDEX.md.

Scans every per-paper subdirectory `analysis/<id>/` and reads metadata
from its `analysis.md`, checks for foundry-specific impl artifacts, and
rewrites the table between fixed markers in `analysis/INDEX.md`.

Idempotent: re-running with no underlying change produces no diff.
Invoked from the GIT step of `/analyze-paper`, `/foundry`, and
`/audit`. Safe to run manually from the repo root:

    python3 scripts/refresh-analysis-index.py

Specification: docs/STYLE.md §5-7.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ANALYSIS_DIR = REPO_ROOT / "analysis"
INDEX = ANALYSIS_DIR / "INDEX.md"

MARKER_START = "<!-- ANALYSIS_INDEX:START -->"
MARKER_END = "<!-- ANALYSIS_INDEX:END -->"

# Rows we extract from the 📄 논문 메타 table.
TITLE_ROW = re.compile(r"^\|\s*원문\s*제목\s*\(영문\)\s*\|\s*(.+?)\s*\|\s*$")
LINK_ROW = re.compile(r"^\|\s*링크\s*\|\s*\[arXiv:([^\]]+)\]\(([^)]+)\)\s*\|\s*$")
REFRESHED_ROW = re.compile(r"^\|\s*분석\s*생성일\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*$")

WARN = "⚠️ metadata"


def find_analyses() -> list[Path]:
    """Return per-paper subdirectory paths (not templates or other dirs)."""
    out: list[Path] = []
    for path in sorted(ANALYSIS_DIR.iterdir()):
        if not path.is_dir():
            continue
        name = path.name
        if name.startswith("_"):
            continue
        # Accept arXiv ids or arbitrary slug directory names.
        out.append(path)
    return out


def extract_meta(paper_dir: Path) -> dict[str, str]:
    """Pull title / arxiv id / arxiv url / refreshed date out of the meta table.

    Missing or malformed rows produce the `⚠️ metadata` placeholder for that
    cell rather than aborting.
    """
    title = arxiv_id = arxiv_url = refreshed = ""
    analysis_file = paper_dir / "analysis.md"
    try:
        text = analysis_file.read_text(encoding="utf-8")
    except OSError:
        return {"title": WARN, "arxiv_id": WARN, "arxiv_url": "", "refreshed": WARN}

    for line in text.splitlines():
        if not title:
            m = TITLE_ROW.match(line)
            if m:
                title = m.group(1).strip()
                continue
        if not arxiv_id:
            m = LINK_ROW.match(line)
            if m:
                arxiv_id = m.group(1).strip()
                arxiv_url = m.group(2).strip()
                continue
        if not refreshed:
            m = REFRESHED_ROW.match(line)
            if m:
                refreshed = m.group(1).strip()
                continue
        if title and arxiv_id and refreshed:
            break

    return {
        "title": title or WARN,
        "arxiv_id": arxiv_id or WARN,
        "arxiv_url": arxiv_url,
        "refreshed": refreshed or WARN,
    }


def lerobot_state(stem: str) -> str:
    """Return ✅ / 🚧 UNMAPPABLE / — for the lerobot foundry column."""
    base = ANALYSIS_DIR / stem / "impl" / "lerobot"
    if (base / "impl.md").is_file():
        return "✅"
    if (base / "UNMAPPABLE.md").is_file():
        return "🚧 UNMAPPABLE"
    return "—"


# 🧬 execution-verification verdict, read from the audit report meta header.
EXEC_ROW_RE = re.compile(r"^\|\s*🧬[^|]*\|\s*`?(pass|fail|skipped)`?\s*\|\s*$")


def lerobot_exec(stem: str) -> str:
    """Return the 🧬 실행 검증 verdict for the lerobot audit (pass/fail/skipped/—).

    Reads the `| 🧬 실행 검증 | <verdict> |` row from the audit report meta
    header. `—` when no audit report exists or the row is absent (older
    reports predating the execution tier).
    """
    audit = ANALYSIS_DIR / stem / "audit" / "lerobot.md"
    try:
        text = audit.read_text(encoding="utf-8")
    except OSError:
        return "—"
    for line in text.splitlines():
        m = EXEC_ROW_RE.match(line)
        if m:
            return m.group(1)
    return "—"


# §🔎 §🚧 bucket counts come from the audit report's machine marker.
BUCKETS_START = "<!-- ANALYSIS_BUCKETS:START -->"
BUCKETS_END = "<!-- ANALYSIS_BUCKETS:END -->"
BUCKET_LINE_RE = re.compile(r"^-\s*(vendor-resolved|paper-extractable|paper-silent-defaultable|paper-silent-experimental|out-of-base-scope)\s*:\s*(.*)$")
BUCKET_ORDER = (
    "vendor-resolved",
    "paper-extractable",
    "paper-silent-defaultable",
    "paper-silent-experimental",
    "out-of-base-scope",
)


def lerobot_buckets(stem: str) -> str:
    """Return the §🔎 bucket counts `vr/pe/sd/se/ob` for the lerobot audit.

    Reads the ANALYSIS_BUCKETS marker block from
    `analysis/<stem>/audit/lerobot.md` and counts the comma-separated
    row ids per bucket. `—` when no audit report exists; `0/0/0/0/0` when
    the marker is present but empty (e.g. all checks pass with no §🚧).
    `ob` = out-of-base-scope (fully specified but outside the chosen
    foundry base's coordinate system).
    """
    audit = ANALYSIS_DIR / stem / "audit" / "lerobot.md"
    try:
        text = audit.read_text(encoding="utf-8")
    except OSError:
        return "—"
    if BUCKETS_START not in text or BUCKETS_END not in text:
        return "—"
    block = text.split(BUCKETS_START, 1)[1].split(BUCKETS_END, 1)[0]
    counts = {name: 0 for name in BUCKET_ORDER}
    for line in block.splitlines():
        m = BUCKET_LINE_RE.match(line.strip())
        if not m:
            continue
        name, payload = m.group(1), m.group(2).strip()
        # Count comma-separated ids; ignore placeholder/empty payloads.
        if not payload or payload.startswith("<"):
            continue
        counts[name] = len([tok for tok in payload.split(",") if tok.strip()])
    return "/".join(str(counts[name]) for name in BUCKET_ORDER)


def sort_key(row: dict[str, str]) -> tuple[str, str]:
    # Refreshed date descending → tied by arXiv id descending.
    # Use string sort: ISO dates and arXiv ids both order lexically.
    refreshed = row["refreshed"] if row["refreshed"] != WARN else "0000-00-00"
    arxiv_id = row["arxiv_id"] if row["arxiv_id"] != WARN else ""
    # Negate by mapping to a complement-style key; easier: sort reverse.
    return (refreshed, arxiv_id)


def build_table(rows: list[dict[str, str]]) -> str:
    header = (
        "| # | Analysis | arXiv | Title | Refreshed | lerobot | 🧬 | 🔎 vr/pe/sd/se/ob |\n"
        "|---|---|---|---|---|---|---|---|\n"
    )
    if not rows:
        return header + "| — | _no deep-dives yet_ | — | — | — | — | — | — |\n"
    out = [header]
    for i, row in enumerate(rows, 1):
        link = f"[`{row['stem']}/analysis.md`]({row['stem']}/analysis.md)"
        if row["arxiv_url"]:
            arxiv = f"[`{row['arxiv_id']}`]({row['arxiv_url']})"
        else:
            arxiv = f"`{row['arxiv_id']}`" if row["arxiv_id"] != WARN else WARN
        out.append(
            f"| {i} | {link} | {arxiv} | {row['title']} | {row['refreshed']} "
            f"| {row['lerobot']} | {row['exec']} | {row['buckets']} |\n"
        )
    return "".join(out)


def rewrite_index(table: str) -> bool:
    """Replace the marker block in analysis/INDEX.md. Return True if changed."""
    original = INDEX.read_text(encoding="utf-8")
    if MARKER_START not in original or MARKER_END not in original:
        sys.stderr.write(
            f"error: missing {MARKER_START} / {MARKER_END} markers in {INDEX}\n"
        )
        sys.exit(2)
    pattern = re.compile(
        re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END),
        re.DOTALL,
    )
    new_block = f"{MARKER_START}\n\n{table}\n{MARKER_END}"
    updated = pattern.sub(lambda _m: new_block, original, count=1)
    if updated == original:
        return False
    INDEX.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    rows: list[dict[str, str]] = []
    for paper_dir in find_analyses():
        meta = extract_meta(paper_dir)
        meta["stem"] = paper_dir.name
        meta["lerobot"] = lerobot_state(paper_dir.name)
        meta["exec"] = lerobot_exec(paper_dir.name)
        meta["buckets"] = lerobot_buckets(paper_dir.name)
        rows.append(meta)
    rows.sort(key=sort_key, reverse=True)
    table = build_table(rows)
    changed = rewrite_index(table)
    print(f"refresh-analysis-index: {len(rows)} analyses · {'updated' if changed else 'no change'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
