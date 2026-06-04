#!/usr/bin/env python3
"""Regenerate the auto-maintained analyses index in analysis/INDEX.md.

Scans every per-paper subdirectory `analysis/<id>/` and reads metadata
from its `analysis.md`, checks for foundry-specific impl artifacts, and
rewrites the block between fixed markers in `analysis/INDEX.md`.

The generated block is grouped by **Pillar** (primary = first `관련 Pillar`
entry) under a top "분류 지도" summary, so the human-facing layout stays
scannable as the corpus grows; a single page still supports Ctrl-F.

Idempotent: re-running with no underlying change produces no diff.
Invoked post-merge on `main` by `.github/workflows/refresh-analysis-index.yml`.
Safe to run manually from the repo root:

    python3 scripts/refresh-analysis-index.py

Specification: docs/STYLE.md §5-7.
"""

from __future__ import annotations

import re
import sys
import urllib.parse
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
PILLAR_ROW = re.compile(r"^\|\s*관련\s*Pillar\s*\|\s*(.+?)\s*\|\s*$")
TAGS_ROW = re.compile(r"^\|\s*태그\s*\|\s*(.+?)\s*\|\s*$")

WARN = "⚠️ metadata"
UNCLASSIFIED = "미분류"

# Pillar display names mirror context/MASTER.md §5 Pillars (SSOT — kept here
# only because this script never reads the human-owned context/ tree). P5
# (evaluation) is deliberately excluded from the index taxonomy: it is a
# cross-cutting pillar no analysis takes as its primary identity (it lives only
# in MASTER.md, with no P5.md extract), so it never groups and is stripped from
# the Pillars column.
PILLAR_NAMES = {
    "P1": "Heterogeneous Body/Hand Action Expert",
    "P2": "Structured Input-Modality Binding",
    "P3": "Hand-level System0 Module",
    "P4": "VLM Pretraining Preservation",
}
PILLAR_ORDER = ["P1", "P2", "P3", "P4", UNCLASSIFIED]
# One fixed color per pillar (distinct from the 빨주노초파 keyword palette).
PILLAR_COLOR = {
    "P1": "1f77b4",  # blue
    "P2": "9467bd",  # purple
    "P3": "2ca02c",  # green
    "P4": "d62728",  # red
    UNCLASSIFIED: "888888",  # grey
}
# P1–P4 only; P5 (and anything else) is dropped at extraction time.
PILLAR_RE = re.compile(r"P[1-4]")
# Tag badges share one neutral color so they read as a single facet.
TAG_COLOR = "555555"


def find_analyses() -> list[Path]:
    """Return per-paper subdirectory paths (not templates or other dirs)."""
    out: list[Path] = []
    for path in sorted(ANALYSIS_DIR.iterdir()):
        if not path.is_dir():
            continue
        name = path.name
        # `templates` is the skeleton; `catalogs` is hand-curated cross-paper
        # reference material, explicitly out of INDEX auto-regeneration scope
        # (CLAUDE.md "Automatically-maintained indexes"). Neither is a paper.
        if name.startswith("_") or name in ("templates", "catalogs"):
            continue
        # Accept arXiv ids or arbitrary slug directory names.
        out.append(path)
    return out


def _split_csv(value: str) -> list[str]:
    return [tok.strip() for tok in value.split(",") if tok.strip()]


def extract_meta(paper_dir: Path) -> dict:
    """Pull title / arxiv / refreshed / pillars / tags out of the meta table.

    Missing or malformed scalar rows produce the `⚠️ metadata` placeholder for
    that cell rather than aborting; missing pillar/tag rows yield empty lists.
    """
    title = arxiv_id = arxiv_url = refreshed = ""
    pillars: list[str] = []
    tags: list[str] = []
    analysis_file = paper_dir / "analysis.md"
    try:
        text = analysis_file.read_text(encoding="utf-8")
    except OSError:
        return {
            "title": WARN, "arxiv_id": WARN, "arxiv_url": "",
            "refreshed": WARN, "pillars": [], "tags": [],
        }

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
        if not pillars:
            m = PILLAR_ROW.match(line)
            if m:
                # Keep declared order; first entry is the primary pillar.
                pillars = [p for p in PILLAR_RE.findall(m.group(1))]
                continue
        if not tags:
            m = TAGS_ROW.match(line)
            if m:
                tags = [t.lower() for t in _split_csv(m.group(1))]
                continue

    return {
        "title": title or WARN,
        "arxiv_id": arxiv_id or WARN,
        "arxiv_url": arxiv_url,
        "refreshed": refreshed or WARN,
        "pillars": pillars,
        "tags": tags,
    }


def impl_state(stem: str) -> str:
    """Return ✅ / 🚧 UNMAPPABLE / — for the impl column.

    Vendor-neutral header, but pathed to the v0 foundry (`lerobot`): ✅ when
    `impl/lerobot/impl.md` exists, 🚧 UNMAPPABLE when `UNMAPPABLE.md` exists,
    `—` when neither has been generated.
    """
    base = ANALYSIS_DIR / stem / "impl" / "lerobot"
    if (base / "impl.md").is_file():
        return "✅"
    if (base / "UNMAPPABLE.md").is_file():
        return "🚧 UNMAPPABLE"
    return "—"


# 🔑 기술 키워드 bullet head: `- **<term>** — …` (em dash separates head/def).
KEYWORD_HEADER_RE = re.compile(r"^##\s+🔑")
KEYWORD_BULLET_RE = re.compile(r"^-\s+(.+)$")
# Secondary cut for bullets that use `term: def` instead of the spec's em dash.
KEYWORD_COLON_RE = re.compile(r":\s")
# Hangul (incl. Jamo) — a keyword head must reduce to English before it ships.
HANGUL_RE = re.compile(r"[가-힣ᄀ-ᇿ㄰-㆏]")
# `<a> (<b>)` split used to recover the English half of a bilingual head.
PAREN_RE = re.compile(r"^(.*?)\s*\(([^()]*)\)\s*(.*)$")
# Any math/markup markup → the keyword is excluded outright (English plain
# text only): inline KaTeX `$`…`$`, `$…$`, raw LaTeX, backticks.
MATH_RE = re.compile(r"[`$\\]")
MAX_KEYWORDS = 5
KEYWORD_HEAD_CAP = 40  # badges stay short and scannable
# All keyword badges share one color (노 yellow). Keywords are descriptive, not
# ranked, so a per-position palette added visual noise without meaning.
KEYWORD_COLOR = "ffd700"  # 노 yellow


def _englishize(head: str) -> str:
    """Reduce a keyword head to its English form, dropping any Korean gloss.

    Bilingual heads in the corpus take the shape `한글 (English)` or
    `English (한글)`; we keep whichever side carries no Hangul. A head with no
    recoverable English (pure Korean) collapses to the empty string and is
    dropped by the caller — the English-only rule is enforced in
    docs/STYLE.md §5-6 for new analyses.
    """
    if not HANGUL_RE.search(head):
        return head.strip()
    m = PAREN_RE.match(head)
    if m:
        inner = m.group(2).strip()
        outer = f"{m.group(1)} {m.group(3)}".strip()
        if inner and not HANGUL_RE.search(inner):
            return inner
        if outer and not HANGUL_RE.search(outer):
            return outer
    cleaned = re.sub(r"\s{2,}", " ", HANGUL_RE.sub(" ", head)).strip(" -–—·,/")
    return "" if HANGUL_RE.search(cleaned) else cleaned


def extract_keywords(paper_dir: Path) -> list[str]:
    """Return up to MAX_KEYWORDS English keyword labels from 🔑 기술 키워드.

    Reads the `## 🔑 기술 키워드` section (spec'd in docs/STYLE.md §5-6) and
    takes each top-level bullet's head term — the text before the em dash `—`
    (the spec delimiter; a `: ` separator is tolerated for non-conforming
    bullets). English plain text only: a head carrying any math/markup
    (`MATH_RE` — inline KaTeX, LaTeX, backticks) is excluded outright, and a
    head with no recoverable English (`_englishize`) is dropped too. The scan
    continues past skipped heads to fill up to MAX_KEYWORDS. Empty list when
    the section is missing.
    """
    analysis_file = paper_dir / "analysis.md"
    try:
        text = analysis_file.read_text(encoding="utf-8")
    except OSError:
        return []

    in_section = False
    labels: list[str] = []
    for line in text.splitlines():
        if not in_section:
            if KEYWORD_HEADER_RE.match(line):
                in_section = True
            continue
        # End of section: next ## header or a horizontal rule.
        if line.startswith("## ") or line.strip() == "---":
            break
        m = KEYWORD_BULLET_RE.match(line)
        if not m:
            continue
        head = m.group(1).split("—", 1)[0].replace("**", "").strip()
        head = KEYWORD_COLON_RE.split(head, maxsplit=1)[0].strip()
        # Exclude math keywords outright — no $…$, KaTeX, LaTeX, or backticks.
        if MATH_RE.search(head):
            continue
        head = re.sub(r"\s{2,}", " ", _englishize(head)).strip()
        if not head:
            continue
        if len(head) > KEYWORD_HEAD_CAP:
            head = head[: KEYWORD_HEAD_CAP - 1].rstrip() + "…"
        labels.append(head)
        if len(labels) >= MAX_KEYWORDS:
            break
    return labels


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
    keyword badges use one color (노 yellow) — keywords are descriptive, not
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


def tag_badges(tags: list[str]) -> str:
    """Render a paper's tags as neutral-color facet badges."""
    if not tags:
        return "—"
    return " ".join(_badge(t, TAG_COLOR) for t in tags)


def arxiv_badge(arxiv_id: str, arxiv_url: str) -> str:
    """Render the arXiv cell as a red shields.io badge linking to the abs page."""
    if arxiv_id == WARN:
        return WARN
    if not arxiv_url:
        return f"`{arxiv_id}`"
    label = _shields_escape(arxiv_id)
    return f"[![arXiv](https://img.shields.io/badge/arXiv-{label}-b31b1b.svg)]({arxiv_url})"


def sort_key(row: dict) -> tuple[str, str]:
    # Refreshed date descending → tied by arXiv id descending.
    # Use string sort: ISO dates and arXiv ids both order lexically.
    refreshed = row["refreshed"] if row["refreshed"] != WARN else "0000-00-00"
    arxiv_id = row["arxiv_id"] if row["arxiv_id"] != WARN else ""
    return (refreshed, arxiv_id)


def primary_pillar(row: dict) -> str:
    return row["pillars"][0] if row["pillars"] else UNCLASSIFIED


def build_block(rows: list[dict]) -> str:
    """Compose the full generated block: 분류 지도 summary + per-pillar tables."""
    if not rows:
        return (
            "## 분류 지도\n\n_no deep-dives yet_\n\n"
            "## 미분류\n\n"
            "| # | Analysis | arXiv | Title | Pillars | Tags | Keywords | Refreshed | impl |\n"
            "|---|---|---|---|---|---|---|---|---|\n"
            "| — | _no deep-dives yet_ | — | — | — | — | — | — | — |\n"
        )

    # Bucket by primary pillar.
    groups: dict[str, list[dict]] = {key: [] for key in PILLAR_ORDER}
    for row in rows:
        groups[primary_pillar(row)].append(row)
    for key in groups:
        groups[key].sort(key=sort_key, reverse=True)

    # Tag distribution across the whole corpus.
    tag_counts: dict[str, int] = {}
    for row in rows:
        for tag in row["tags"]:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    out: list[str] = []

    # ── 분류 지도 (summary) ──────────────────────────────────────────────
    out.append("## 분류 지도\n\n")
    out.append(f"총 {len(rows)}편. Pillar 별 1차 분류(primary = 첫 `관련 Pillar`):\n\n")
    out.append("| Pillar | 논문 수 | 영역 |\n|---|---|---|\n")
    for key in PILLAR_ORDER:
        n = len(groups[key])
        if key == UNCLASSIFIED:
            if n == 0:
                continue
            name = "—"
        else:
            name = PILLAR_NAMES[key]
        anchor = key.lower() if key != UNCLASSIFIED else "미분류"
        label = _badge(key, PILLAR_COLOR[key]) if key != UNCLASSIFIED else key
        out.append(f"| {label} | {n} | {name} |\n")
    out.append("\n")
    if tag_counts:
        out.append("태그 분포: ")
        ordered = sorted(tag_counts.items(), key=lambda kv: (-kv[1], kv[0]))
        out.append(" ".join(_badge(f"{t} {c}", TAG_COLOR) for t, c in ordered))
        out.append("\n\n")

    # ── Per-pillar tables ───────────────────────────────────────────────
    header = (
        "| # | Analysis | arXiv | Title | Pillars | Tags | Keywords | Refreshed | impl |\n"
        "|---|---|---|---|---|---|---|---|---|\n"
    )
    for key in PILLAR_ORDER:
        bucket = groups[key]
        if not bucket:
            continue
        title = key if key == UNCLASSIFIED else f"{key} — {PILLAR_NAMES[key]}"
        out.append(f"## {title}\n\n")
        out.append(header)
        for i, row in enumerate(bucket, 1):
            link = f"[`{row['stem']}/analysis.md`]({row['stem']}/analysis.md)"
            out.append(
                f"| {i} | {link} | {arxiv_badge(row['arxiv_id'], row['arxiv_url'])} "
                f"| {row['title']} | {pillar_badges(row['pillars'])} "
                f"| {tag_badges(row['tags'])} | {keyword_badges(row['keywords'])} "
                f"| {row['refreshed']} | {row['impl']} |\n"
            )
        out.append("\n")

    return "".join(out).rstrip() + "\n"


def rewrite_index(block: str) -> bool:
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
    new_block = f"{MARKER_START}\n\n{block}\n{MARKER_END}"
    updated = pattern.sub(lambda _m: new_block, original, count=1)
    if updated == original:
        return False
    INDEX.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    rows: list[dict] = []
    for paper_dir in find_analyses():
        meta = extract_meta(paper_dir)
        meta["stem"] = paper_dir.name
        meta["keywords"] = extract_keywords(paper_dir)
        meta["impl"] = impl_state(paper_dir.name)
        rows.append(meta)

    block = build_block(rows)
    changed = rewrite_index(block)
    print(f"refresh-analysis-index: {len(rows)} analyses · {'updated' if changed else 'no change'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
