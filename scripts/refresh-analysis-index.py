#!/usr/bin/env python3
"""Regenerate the auto-maintained analysis index (`analysis/README.md`).

Scans every per-paper subdirectory `analysis/<id>/` and reads metadata
from its `analysis.md`, then rewrites the block between fixed markers in
`analysis/README.md`.

The generated block is one table per primary Pillar (primary = first `관련
Pillar` entry), so the human-facing layout stays scannable as the corpus grows;
a single page still supports Ctrl-F. Each row carries a white 📝 shields.io
badge linking the paper's deep-dive in front of its title, plus Links / Pillars
/ Keywords / Refreshed cells.

Everything outside the `<!-- ANALYSIS_INDEX:START -->` /
`<!-- ANALYSIS_INDEX:END -->` markers (the short folder intro above the block)
stays hand-maintained.

The corpus parsing (meta-table extraction, keyword extraction) lives in the
shared `probe_corpus` module so this script and the supermemory PoC ingestor
read the `논문 메타` table identically; this file keeps only the
index-presentation logic (badges, per-pillar tables, marker rewriting).

Idempotent: re-running with no underlying change produces no diff.
Invoked post-merge on `main` by `.github/workflows/refresh-analysis-index.yml`.
Safe to run manually from the repo root:

    python3 scripts/refresh-analysis-index.py

Specification: docs/style.md §5-7.
"""

from __future__ import annotations

import re
import sys
import urllib.parse

from probe_corpus import (
    ARXIV_ID_RE,
    REPO_ROOT,
    UNCLASSIFIED,
    WARN,
    extract_keywords,
    extract_meta,
    find_analyses,
)

# The generated deep-dive index is the analysis folder's own README; rows link
# down into <id>/analysis.md with a path relative to that README.
INDEX = REPO_ROOT / "analysis" / "README.md"

MARKER_START = "<!-- ANALYSIS_INDEX:START -->"
MARKER_END = "<!-- ANALYSIS_INDEX:END -->"

# Pillar display names mirror context/MASTER.md §5 Pillars (kept here only
# because this script never reads the human-owned context/ tree). The taxonomy
# covers the six pillars P0–P5; a P# outside that range is stripped from the
# Pillars column (by PILLAR_RE in probe_corpus at extraction time).
PILLAR_NAMES = {
    "P0": "VLA Datasets & Benchmarks",
    "P1": "Heterogeneous Body/Hand Action Expert",
    "P2": "Structured Multimodal Observation Fusion",
    "P3": "Hand-level System0 Module",
    "P4": "Pretraining for Data-Efficient Adaptation",
    "P5": "World Model",
}
PILLAR_ORDER = ["P0", "P1", "P2", "P3", "P4", "P5", UNCLASSIFIED]
# One fixed color per pillar (distinct from the 빨주노초파 keyword palette).
PILLAR_COLOR = {
    "P0": "f5d5d5",  # pale red
    "P1": "f5e9d5",  # pale orange
    "P2": "e2f5d5",  # pale green
    "P3": "d5f5e7",  # pale mint
    "P4": "d5def5",  # pale blue
    "P5": "e0d5f5",  # pale purple
    UNCLASSIFIED: "888888",  # grey
}

# All keyword badges share one color (노 yellow). Keywords are descriptive, not
# ranked, so a per-position palette added visual noise without meaning.
KEYWORD_COLOR = "e8e7e7"  # pale grey


def _shields_escape(text: str) -> str:
    """Escape a shields.io badge field: `-`→`--`, `_`→`__`, space→`_`, then URL-quote."""
    text = text.replace("-", "--").replace("_", "__").replace(" ", "_")
    return urllib.parse.quote(text, safe="_-.")


def _badge(label: str, color: str, href: str = "") -> str:
    alt = label.replace("|", "/").replace("]", ")")
    img = f"![{alt}](https://img.shields.io/badge/{_shields_escape(label)}-{color}.svg)"
    return f"[{img}]({href})" if href else img


def keyword_badges(labels: list[str]) -> str:
    """Render keyword labels as space-separated shields.io badges.

    GitHub's Markdown sanitizer strips inline CSS (`<span style=…>`), so a
    shields.io badge is the only way to color keyword text on github.com. All
    keyword badges use one color (pale grey) — keywords are descriptive, not
    ranked, so a positional palette carried no meaning.
    """
    if not labels:
        return "—"
    return " ".join(_badge(label, KEYWORD_COLOR) for label in labels)


def pillar_badges(pillars: list[str]) -> str:
    """Render a paper's full pillar set as fixed-color badges."""
    if not pillars:
        return "—"
    return " ".join(_badge(p, PILLAR_COLOR.get(p, PILLAR_COLOR[UNCLASSIFIED])) for p in pillars)


# Per-kind shields.io badge: (alt/left label, right label, color). arXiv is
# built separately so the badge carries the id; the rest are fixed-style badges.
# Badge order is always arXiv → Website → GitHub → HuggingFace.
_LINK_BADGE = {
    "web": ("Website", "Link", "blue"),
    "github": ("GitHub", "Code", "black"),
    "hf": ("HuggingFace", "Model", "yellow"),
}
_LINK_ORDER = {"arxiv": 0, "web": 1, "github": 2, "hf": 3}


def link_badges(links: list[tuple[str, str]], arxiv_id: str) -> str:
    """Render the links cell as shields.io badges in a fixed order.

    arXiv → Website → GitHub → HuggingFace. Falls back to `—` when the row
    carried no links.
    """
    if not links:
        return WARN if arxiv_id == WARN else "—"
    out: list[str] = []
    for kind, url in sorted(links, key=lambda kv: _LINK_ORDER.get(kv[0], 9)):
        if kind == "arxiv":
            m = ARXIV_ID_RE.search(url)
            aid = m.group(1) if m else arxiv_id
            label = _shields_escape(aid)
            out.append(f"[![arXiv](https://img.shields.io/badge/arXiv-{label}-b31b1b.svg)]({url})")
        else:
            left, right, color = _LINK_BADGE[kind]
            out.append(f"[![{left}](https://img.shields.io/badge/{left}-{right}-{color})]({url})")
    return " ".join(out)


def sort_key(row: dict) -> tuple[str, str]:
    # Refreshed date descending → tied by arXiv id descending.
    # Use string sort: ISO dates and arXiv ids both order lexically.
    refreshed = row["refreshed"] if row["refreshed"] != WARN else "0000-00-00"
    arxiv_id = row["arxiv_id"] if row["arxiv_id"] != WARN else ""
    return (refreshed, arxiv_id)


def primary_pillar(row: dict) -> str:
    return row["pillars"][0] if row["pillars"] else UNCLASSIFIED


# Columns: a 📝 deep-dive badge spliced in front of the title, then Links /
# Pillars / Keywords / Refreshed. Both the analysis-link and impl columns the
# index used to carry were dropped — the link folds into the title cell.
HEADER = (
    "| # | Title | Links | Pillars | Keywords | Refreshed |\n"
    "|---|---|---|---|---|---|\n"
)


def build_block(rows: list[dict]) -> str:
    """Compose the generated block: one table per primary Pillar."""
    if not rows:
        return (
            "## 미분류\n\n"
            + HEADER
            + "| — | _no deep-dives yet_ | — | — | — | — |\n"
        )

    # Bucket by primary pillar.
    groups: dict[str, list[dict]] = {key: [] for key in PILLAR_ORDER}
    for row in rows:
        groups[primary_pillar(row)].append(row)
    for key in groups:
        groups[key].sort(key=sort_key, reverse=True)

    out: list[str] = []

    # ── Per-pillar tables ───────────────────────────────────────────────
    for key in PILLAR_ORDER:
        bucket = groups[key]
        if not bucket:
            continue
        title = key if key == UNCLASSIFIED else f"{key} — {PILLAR_NAMES[key]}"
        out.append(f"## {title}\n\n")
        out.append(HEADER)
        for i, row in enumerate(bucket, 1):
            badge = (
                "[![](https://img.shields.io/badge/📝-ffffff.svg)]"
                f"(../analysis/{row['stem']}/analysis.md)"
            )
            links_cell = link_badges(row["links"], row["arxiv_id"])
            out.append(
                f"| {i} | {badge} {row['title']} | {links_cell} "
                f"| {pillar_badges(row['pillars'])} "
                f"| {keyword_badges(row['keywords'])} "
                f"| {row['refreshed']} |\n"
            )
        out.append("\n")

    return "".join(out).rstrip() + "\n"


def rewrite_index(block: str) -> bool:
    """Replace the marker block in analysis/README.md. Return True if changed."""
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
    new_block = f"{MARKER_START}\n\n{block}\n{MARKER_END}"
    updated = pattern.sub(lambda _m: new_block, original, count=1)
    if updated == original:
        return False
    INDEX.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    analyses = find_analyses()

    rows: list[dict] = []
    for paper_dir in analyses:
        meta = extract_meta(paper_dir)
        meta["stem"] = paper_dir.name
        meta["keywords"] = extract_keywords(paper_dir)
        rows.append(meta)

    block = build_block(rows)
    index_changed = rewrite_index(block)
    print(
        f"refresh-analysis-index: {len(rows)} analyses · "
        f"README.md {'updated' if index_changed else 'no change'}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
