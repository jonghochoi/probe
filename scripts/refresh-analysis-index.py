#!/usr/bin/env python3
"""Regenerate the auto-maintained analyses index in analysis/README.md.

Scans every deep-dive `analysis/<id>.md`, pulls metadata from its
"📄 논문 메타" table, checks for foundry-specific impl artifacts, and
rewrites the table between fixed markers in `analysis/README.md`.

Idempotent: re-running with no underlying change produces no diff.
Invoked from the GIT step of `/analyze-paper`, `/foundry`, and
`/verify`. Safe to run manually from the repo root:

    python3 scripts/refresh-analysis-index.py

Specification: docs/STYLE_GUIDE.md §5-7.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ANALYSIS_DIR = REPO_ROOT / "analysis"
README = ANALYSIS_DIR / "README.md"

MARKER_START = "<!-- ANALYSIS_INDEX:START -->"
MARKER_END = "<!-- ANALYSIS_INDEX:END -->"

# arXiv ids look like 1234.56789 (with optional version suffix).
ARXIV_FILENAME_RE = re.compile(r"^\d{4}\.\d{4,5}(?:v\d+)?$")

# Rows we extract from the 📄 논문 메타 table.
TITLE_ROW = re.compile(r"^\|\s*원문\s*제목\s*\(영문\)\s*\|\s*(.+?)\s*\|\s*$")
LINK_ROW = re.compile(r"^\|\s*링크\s*\|\s*\[arXiv:([^\]]+)\]\(([^)]+)\)\s*\|\s*$")
REFRESHED_ROW = re.compile(r"^\|\s*분석\s*생성일\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*$")

WARN = "⚠️ metadata"


def find_analyses() -> list[Path]:
    """Return deep-dive analysis paths (not templates, designs, impls, verifies)."""
    out: list[Path] = []
    for path in sorted(ANALYSIS_DIR.glob("*.md")):
        name = path.name
        if name.startswith("_"):
            continue
        if name in {"README.md"}:
            continue
        stem = path.stem
        if any(stem.endswith(suffix) for suffix in ("_design", "_impl", "_verify")):
            continue
        # Accept arXiv ids or arbitrary slug filenames (PDF-input analyses).
        out.append(path)
    return out


def extract_meta(path: Path) -> dict[str, str]:
    """Pull title / arxiv id / arxiv url / refreshed date out of the meta table.

    Missing or malformed rows produce the `⚠️ metadata` placeholder for that
    cell rather than aborting.
    """
    title = arxiv_id = arxiv_url = refreshed = ""
    try:
        text = path.read_text(encoding="utf-8")
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
    base = ANALYSIS_DIR / f"{stem}_impl" / "lerobot"
    if (base / "impl.md").is_file():
        return "✅"
    if (base / "UNMAPPABLE.md").is_file():
        return "🚧 UNMAPPABLE"
    return "—"


def sort_key(row: dict[str, str]) -> tuple[str, str]:
    # Refreshed date descending → tied by arXiv id descending.
    # Use string sort: ISO dates and arXiv ids both order lexically.
    refreshed = row["refreshed"] if row["refreshed"] != WARN else "0000-00-00"
    arxiv_id = row["arxiv_id"] if row["arxiv_id"] != WARN else ""
    # Negate by mapping to a complement-style key; easier: sort reverse.
    return (refreshed, arxiv_id)


def build_table(rows: list[dict[str, str]]) -> str:
    header = (
        "| # | Analysis | arXiv | Title | Refreshed | lerobot |\n"
        "|---|---|---|---|---|---|\n"
    )
    if not rows:
        return header + "| — | _no deep-dives yet_ | — | — | — | — |\n"
    out = [header]
    for i, row in enumerate(rows, 1):
        link = f"[`{row['stem']}.md`]({row['stem']}.md)"
        if row["arxiv_url"]:
            arxiv = f"[`{row['arxiv_id']}`]({row['arxiv_url']})"
        else:
            arxiv = f"`{row['arxiv_id']}`" if row["arxiv_id"] != WARN else WARN
        out.append(
            f"| {i} | {link} | {arxiv} | {row['title']} | {row['refreshed']} | {row['lerobot']} |\n"
        )
    return "".join(out)


def rewrite_readme(table: str) -> bool:
    """Replace the marker block in analysis/README.md. Return True if changed."""
    original = README.read_text(encoding="utf-8")
    if MARKER_START not in original or MARKER_END not in original:
        sys.stderr.write(
            f"error: missing {MARKER_START} / {MARKER_END} markers in {README}\n"
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
    README.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    rows: list[dict[str, str]] = []
    for path in find_analyses():
        meta = extract_meta(path)
        meta["stem"] = path.stem
        meta["lerobot"] = lerobot_state(path.stem)
        rows.append(meta)
    rows.sort(key=sort_key, reverse=True)
    table = build_table(rows)
    changed = rewrite_readme(table)
    print(f"refresh-analysis-index: {len(rows)} analyses · {'updated' if changed else 'no change'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
