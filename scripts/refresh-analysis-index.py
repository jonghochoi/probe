#!/usr/bin/env python3
"""Regenerate the auto-maintained analyses index in analysis/INDEX.md.

Scans every per-paper subdirectory `analysis/<id>/` and reads metadata
from its `analysis.md`, checks for foundry-specific impl artifacts, and
rewrites the table between fixed markers in `analysis/INDEX.md`.

Idempotent: re-running with no underlying change produces no diff.
Invoked from the GIT step of `/analyze-paper`, `/implement`, and
`/validate`. Safe to run manually from the repo root:

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

WARN = "⚠️ metadata"


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
# 빨주노초파 — five fixed colors assigned sequentially by position (badge #1 is
# red, #2 orange, …); never hashed, so 3 keywords get 빨주노 and 5 get 빨주노초파.
KEYWORD_PALETTE = (
    "e60000",  # 빨 red
    "ff8c00",  # 주 orange
    "ffd700",  # 노 yellow
    "2ca02c",  # 초 green
    "1f77b4",  # 파 blue
)


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


def keyword_badges(labels: list[str]) -> str:
    """Render keyword labels as space-separated colored shields.io badges.

    GitHub's Markdown sanitizer strips inline CSS (`<span style=…>`), so a
    shields.io badge is the only way to vary text color per keyword on
    github.com. Colors are the fixed 빨주노초파 palette assigned sequentially by
    position (badge #1 red … #5 blue).
    """
    if not labels:
        return "—"
    badges = []
    for i, label in enumerate(labels):
        color = KEYWORD_PALETTE[i % len(KEYWORD_PALETTE)]
        alt = label.replace("|", "/").replace("]", ")")
        badges.append(
            f"![{alt}](https://img.shields.io/badge/{_shields_escape(label)}-{color}.svg)"
        )
    return " ".join(badges)


def arxiv_badge(arxiv_id: str, arxiv_url: str) -> str:
    """Render the arXiv cell as a red shields.io badge linking to the abs page."""
    if arxiv_id == WARN:
        return WARN
    if not arxiv_url:
        return f"`{arxiv_id}`"
    label = _shields_escape(arxiv_id)
    return f"[![arXiv](https://img.shields.io/badge/arXiv-{label}-b31b1b.svg)]({arxiv_url})"


def sort_key(row: dict[str, str]) -> tuple[str, str]:
    # Refreshed date descending → tied by arXiv id descending.
    # Use string sort: ISO dates and arXiv ids both order lexically.
    refreshed = row["refreshed"] if row["refreshed"] != WARN else "0000-00-00"
    arxiv_id = row["arxiv_id"] if row["arxiv_id"] != WARN else ""
    # Negate by mapping to a complement-style key; easier: sort reverse.
    return (refreshed, arxiv_id)


def build_table(rows: list[dict[str, str]]) -> str:
    header = (
        "| # | Analysis | arXiv | Title | Keywords | Refreshed | impl |\n"
        "|---|---|---|---|---|---|---|\n"
    )
    if not rows:
        return header + "| — | _no deep-dives yet_ | — | — | — | — | — |\n"
    out = [header]
    for i, row in enumerate(rows, 1):
        link = f"[`{row['stem']}/analysis.md`]({row['stem']}/analysis.md)"
        arxiv = arxiv_badge(row["arxiv_id"], row["arxiv_url"])
        keywords = keyword_badges(row["keywords"])
        out.append(
            f"| {i} | {link} | {arxiv} | {row['title']} | {keywords} "
            f"| {row['refreshed']} | {row['impl']} |\n"
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
        meta["keywords"] = extract_keywords(paper_dir)
        meta["impl"] = impl_state(paper_dir.name)
        rows.append(meta)
    rows.sort(key=sort_key, reverse=True)
    table = build_table(rows)
    changed = rewrite_index(table)
    print(f"refresh-analysis-index: {len(rows)} analyses · {'updated' if changed else 'no change'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
