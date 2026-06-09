#!/usr/bin/env python3
"""Regenerate the auto-maintained analysis surfaces (index + catalog cross-links).

Scans every per-paper subdirectory `analysis/<id>/` and reads metadata
from its `analysis.md`, checks for foundry-specific impl artifacts, and
rewrites the block between fixed markers in `analysis/README.md`.

The generated block is one table per primary Pillar (primary = first `관련
Pillar` entry), so the human-facing layout stays scannable as the corpus grows;
a single page still supports Ctrl-F.

It also maintains the bidirectional cross-link between the hand-curated
`analysis/catalogs/models.md` and the deep-dive corpus: every catalog bullet
whose arXiv id has an `analysis/<id>/` folder gets a `deep-dive` badge, and the
matching index row gets a `catalog` badge back. Only the link badges are
automated — catalog entry add/remove and its `Updated` badge stay hand-owned.

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
INDEX = ANALYSIS_DIR / "README.md"
CATALOG = ANALYSIS_DIR / "catalogs" / "models.md"

MARKER_START = "<!-- ANALYSIS_INDEX:START -->"
MARKER_END = "<!-- ANALYSIS_INDEX:END -->"

# Rows we extract from the 논문 메타 table.
TITLE_ROW = re.compile(r"^\|\s*원문\s*제목\s*\(영문\)\s*\|\s*(.+?)\s*\|\s*$")
LINK_ROW = re.compile(r"^\|\s*링크\s*\|\s*(.+?)\s*\|\s*$")
MD_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
ARXIV_ID_RE = re.compile(r"(\d{4}\.\d{4,5})")
REFRESHED_ROW = re.compile(r"^\|\s*분석\s*생성일\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*$")
PILLAR_ROW = re.compile(r"^\|\s*관련\s*Pillar\s*\|\s*(.+?)\s*\|\s*$")

WARN = "⚠️ metadata"
UNCLASSIFIED = "미분류"

# Pillar display names mirror context/MASTER.md §5 Pillars (kept here only
# because this script never reads the human-owned context/ tree). The taxonomy
# covers the six pillars P0–P5; a P# outside that range is stripped from the
# Pillars column.
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
    "P0": "ff7f0e",  # orange
    "P1": "1f77b4",  # blue
    "P2": "9467bd",  # purple
    "P3": "2ca02c",  # green
    "P4": "d62728",  # red
    "P5": "17becf",  # cyan
    UNCLASSIFIED: "888888",  # grey
}
# P0–P5; anything outside the range is dropped at extraction time.
PILLAR_RE = re.compile(r"P[0-5]")


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
    """Pull title / links / refreshed / pillars out of the meta table.

    The `링크` row may carry several links (arXiv + GitHub / HuggingFace /
    project site); each is classified by host and rendered as its own badge.
    Missing or malformed scalar rows produce the `⚠️ metadata` placeholder for
    that cell rather than aborting; a missing pillar row yields an empty list.
    """
    title = arxiv_id = arxiv_url = refreshed = ""
    links: list[tuple[str, str]] = []   # (kind, url), arXiv first
    pillars: list[str] = []
    analysis_file = paper_dir / "analysis.md"
    try:
        text = analysis_file.read_text(encoding="utf-8")
    except OSError:
        return {
            "title": WARN, "arxiv_id": WARN, "arxiv_url": "",
            "refreshed": WARN, "pillars": [], "links": [],
        }

    for line in text.splitlines():
        if not title:
            m = TITLE_ROW.match(line)
            if m:
                title = m.group(1).strip()
                continue
        if not links:
            m = LINK_ROW.match(line)
            if m and MD_LINK.search(m.group(1)):
                for _label, url in MD_LINK.findall(m.group(1)):
                    url = url.strip()
                    kind = classify_link(url)
                    links.append((kind, url))
                    if kind == "arxiv" and not arxiv_id:
                        am = ARXIV_ID_RE.search(url) or ARXIV_ID_RE.search(_label)
                        if am:
                            arxiv_id, arxiv_url = am.group(1), url
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

    return {
        "title": title or WARN,
        "arxiv_id": arxiv_id or WARN,
        "arxiv_url": arxiv_url,
        "refreshed": refreshed or WARN,
        "pillars": pillars,
        "links": links,
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


# 기술 키워드 bullet head: `- **<term>** — …` (em dash separates head/def).
# The `## 🔑 기술 키워드` header carries the §2 emoji; accept it with or without.
KEYWORD_HEADER_RE = re.compile(r"^##\s+(?:🔑\s*)?기술\s*키워드")
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
    """Return up to MAX_KEYWORDS English keyword labels from 기술 키워드.

    Reads the `## 기술 키워드` section (spec'd in docs/STYLE.md §5-6) and
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


def classify_link(url: str) -> str:
    """Bucket a meta-table link by host: arxiv / github / hf / web."""
    host = urllib.parse.urlparse(url).netloc.lower()
    if "arxiv.org" in host:
        return "arxiv"
    if "github.com" in host:
        return "github"
    if "huggingface.co" in host:
        return "hf"
    return "web"


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


# ── Catalog cross-link (analysis/catalogs/models.md ↔ index) ─────────────
# Both directions share one purple badge color, distinct from the link/pillar/
# keyword palettes, so a cross-link reads as "the same paper, the other surface".
CROSSLINK_COLOR = "6f42c1"  # 보라 purple
# Index → catalog: appended to a row's Links cell when the paper is curated.
CATALOG_BADGE = (
    f"[![catalog](https://img.shields.io/badge/catalog-📚_models-{CROSSLINK_COLOR}.svg)]"
    "(catalogs/models.md)"
)
# Catalog → index: injected into a models.md bullet after its arXiv badge.
# Matches any prior injection (id-agnostic) so re-runs strip-then-readd cleanly.
DEEP_DIVE_RE = re.compile(r"\s*\[!\[deep-dive\][^\)]*\)\]\([^)]*\)")
# The arXiv badge in a models.md bullet — we splice the deep-dive badge in right
# after it (id always present when there is one), keeping trailing status emoji last.
CATALOG_ARXIV_BADGE_RE = re.compile(
    r"\[!\[arXiv\]\(https://img\.shields\.io/badge/arXiv-(\d{4}\.\d{4,5})-b31b1b\.svg\)\]\([^)]*\)"
)


def _deep_dive_badge(stem: str) -> str:
    """Deep-dive badge for a models.md bullet → `../<id>/analysis.md` (catalog is one level down)."""
    return (
        f" [![deep-dive](https://img.shields.io/badge/deep--dive-📄_analysis-{CROSSLINK_COLOR}.svg)]"
        f"(../{stem}/analysis.md)"
    )


def load_catalog_ids() -> set[str]:
    """Return the set of arXiv ids curated in analysis/catalogs/models.md.

    Used for the reverse badge: an index row whose paper is in this set gets a
    `catalog` badge. Missing catalog file → empty set (reverse link disabled).
    """
    try:
        text = CATALOG.read_text(encoding="utf-8")
    except OSError:
        return set()
    return set(ARXIV_ID_RE.findall(text))


def enrich_catalog(analysis_ids: set[str]) -> bool:
    """Inject/refresh deep-dive badges in models.md; return True if changed.

    For every bullet carrying an arXiv badge whose id has an `analysis/<id>/`
    folder, splice a deep-dive badge right after the arXiv badge; strip any
    existing deep-dive badge first so the op is idempotent and a deleted folder
    drops its badge. Lines without an arXiv badge (id-less entries) are left
    untouched. The hand-owned `Updated` badge is never modified.
    """
    try:
        original = CATALOG.read_text(encoding="utf-8")
    except OSError:
        return False

    out_lines: list[str] = []
    for line in original.splitlines():
        stripped = DEEP_DIVE_RE.sub("", line)
        m = CATALOG_ARXIV_BADGE_RE.search(stripped)
        if m and m.group(1) in analysis_ids:
            insert_at = m.end()
            stripped = stripped[:insert_at] + _deep_dive_badge(m.group(1)) + stripped[insert_at:]
        out_lines.append(stripped)

    updated = "\n".join(out_lines)
    if original.endswith("\n"):
        updated += "\n"
    if updated == original:
        return False
    CATALOG.write_text(updated, encoding="utf-8")
    return True


def sort_key(row: dict) -> tuple[str, str]:
    # Refreshed date descending → tied by arXiv id descending.
    # Use string sort: ISO dates and arXiv ids both order lexically.
    refreshed = row["refreshed"] if row["refreshed"] != WARN else "0000-00-00"
    arxiv_id = row["arxiv_id"] if row["arxiv_id"] != WARN else ""
    return (refreshed, arxiv_id)


def primary_pillar(row: dict) -> str:
    return row["pillars"][0] if row["pillars"] else UNCLASSIFIED


def build_block(rows: list[dict], catalog_ids: set[str]) -> str:
    """Compose the generated block: one table per primary Pillar.

    A row whose arXiv id is curated in `catalog_ids` gets a `catalog` badge
    appended to its Links cell (the reverse half of the catalog cross-link).
    """
    if not rows:
        return (
            "## 미분류\n\n"
            "| # | Analysis | Links | Title | Pillars | Keywords | Refreshed | impl |\n"
            "|---|---|---|---|---|---|---|---|\n"
            "| — | _no deep-dives yet_ | — | — | — | — | — | — |\n"
        )

    # Bucket by primary pillar.
    groups: dict[str, list[dict]] = {key: [] for key in PILLAR_ORDER}
    for row in rows:
        groups[primary_pillar(row)].append(row)
    for key in groups:
        groups[key].sort(key=sort_key, reverse=True)

    out: list[str] = []

    # ── Per-pillar tables ───────────────────────────────────────────────
    header = (
        "| # | Analysis | Links | Title | Pillars | Keywords | Refreshed | impl |\n"
        "|---|---|---|---|---|---|---|---|\n"
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
            links_cell = link_badges(row["links"], row["arxiv_id"])
            if row["arxiv_id"] in catalog_ids:
                links_cell += f" {CATALOG_BADGE}"
            out.append(
                f"| {i} | {link} | {links_cell} "
                f"| {row['title']} | {pillar_badges(row['pillars'])} "
                f"| {keyword_badges(row['keywords'])} "
                f"| {row['refreshed']} | {row['impl']} |\n"
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
    analysis_ids = {p.name for p in analyses}
    catalog_ids = load_catalog_ids()

    rows: list[dict] = []
    for paper_dir in analyses:
        meta = extract_meta(paper_dir)
        meta["stem"] = paper_dir.name
        meta["keywords"] = extract_keywords(paper_dir)
        meta["impl"] = impl_state(paper_dir.name)
        rows.append(meta)

    block = build_block(rows, catalog_ids)
    index_changed = rewrite_index(block)
    catalog_changed = enrich_catalog(analysis_ids)
    print(
        f"refresh-analysis-index: {len(rows)} analyses · "
        f"README {'updated' if index_changed else 'no change'} · "
        f"models.md {'updated' if catalog_changed else 'no change'}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
