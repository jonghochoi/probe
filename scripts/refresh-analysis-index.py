#!/usr/bin/env python3
"""Regenerate the auto-maintained analysis surfaces (index + catalog cross-links).

Scans every per-paper subdirectory `analysis/<id>/` and reads metadata
from its `analysis.md`, checks for foundry-specific impl artifacts, and
rewrites the block between fixed markers in `catalogs/analyses.md`.

The generated block is one table per primary Pillar (primary = first `관련
Pillar` entry), so the human-facing layout stays scannable as the corpus grows;
a single page still supports Ctrl-F.

It also maintains the cross-links between the hand-curated catalogs and the
deep-dive corpus:

- `catalogs/models.md` — every bullet whose arXiv id has an `analysis/<id>/`
  folder gets a leading `📝` analysis badge spliced in right after the list
  marker (arXiv-id matching, as ever).
- `catalogs/datasets.md` / `catalogs/benchmarks.md` — hand-curated rich tables.
  A paper opts in with a `카탈로그` (`target/section/handle`) meta row; the script
  then **creates a skeleton row once** in that section (Links / Refreshed /
  Analysis auto-filled, the rich Source/Facts/… columns seeded `❓`) and never
  overwrites it again — a human backfills the `❓` cells. Every existing row's
  trailing **Analysis** cell is kept fresh (a `📝` badge when its arXiv id has an
  `analysis/<id>/` folder, `—` otherwise).

The cross-link is one-directional (catalog → deep-dive): the reverse `catalog`
badge that used to sit in the index `Links` cell was dropped, since it pointed
at a whole catalog file rather than a specific row.

Every other part of the catalogs (entry curation, the rich columns once a human
fills them, the per-row Refreshed dates, the `models.md` lineage grouping) is
hand-owned and never touched.

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
# The generated deep-dive index lives alongside the hand-curated catalogs
# (a sibling of models.md / datasets.md / benchmarks.md), so relative links
# from a row point back up into ../analysis/<id>/.
INDEX = REPO_ROOT / "catalogs" / "analyses.md"
CATALOG = REPO_ROOT / "catalogs" / "models.md"
CATALOG_DATASET = REPO_ROOT / "catalogs" / "datasets.md"
CATALOG_BENCHMARK = REPO_ROOT / "catalogs" / "benchmarks.md"

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

# ── Catalog routing (`카탈로그` meta → skeleton upsert) ─────────────────────
# An analysis opts a paper into a catalog with a `카탈로그` row of comma-separated
# tokens. Two grammars by target:
#   • datasets / benchmarks — `target/section/handle` (rich table; skeleton row)
#   • models                — `models/group/series/handle` (awesome-list bullet)
# In both cases the script *creates the entry once* and never overwrites it
# again — a human owns the cells/curation thereafter (docs/STYLE.md §5-7).
CATALOG_ROW = re.compile(r"^\|\s*카탈로그\s*\|\s*(.+?)\s*\|\s*$")
# `Design 적용` row (optional): present only for 🚫 비대상 papers; a missing
# row means ✅ 적용 (the default). The cell carries `🚫 비대상 (<사유>)`.
DESIGN_ROW = re.compile(r"^\|\s*Design\s*적용\s*\|\s*(.+?)\s*\|\s*$")
CATALOG_SECTIONS = {
    "dataset": ("robot", "human", "mixed"),
    "benchmark": ("harness", "sim", "dexterous"),
}
# (target, section) → the catalog's `##` header text. Dict order is irrelevant
# here (rows are inserted into whichever section already exists in the file).
SECTION_LABELS = {
    ("dataset", "robot"): "🤖 Robot Action",
    ("dataset", "human"): "👤 Human Video",
    ("dataset", "mixed"): "🔀 Mixed (Robot + Human)",
    ("benchmark", "harness"): "🧪 Eval Harness",
    ("benchmark", "sim"): "🎮 Simulator / Sim Benchmark",
    ("benchmark", "dexterous"): "✋ Dexterous / Contact-rich Eval",
}
# models.md `group` token → its `##` header text. The `series` token then names
# an existing `### ` lineage subsection under that group (e.g. `Standalone`).
MODELS_GROUPS = {
    "vla": "🤖 VLA",
    "vlm": "🧠 Open-weight VLM",
    "wam": "🌐 WAM",
}
# The four hand-owned rich columns seeded `❓` on skeleton creation (between the
# auto Links cell and the auto Refreshed/Analysis tail). Same count for both
# targets, so one skeleton shape serves both.
CATALOG_RICH_COLS = {
    "dataset": ("Source", "Facts", "Embodiment", "License"),
    "benchmark": ("Source", "Details", "Type", "License"),
}


def _split_csv(value: str) -> list[str]:
    return [tok.strip() for tok in value.split(",") if tok.strip()]


def parse_catalog(value: str) -> list[tuple[str, ...]]:
    """Parse a `카탈로그` row value into routing tuples.

    Two shapes by target:
      • `dataset`/`benchmark` → `(target, section, handle)` (3 parts)
      • `models`              → `("models", group, series, handle)` (4 parts)

    `none` (or empty) routes nowhere. A malformed token, invalid section, or
    invalid models group is warned and dropped (mirrors the P# out-of-range
    drop) so a typo never fabricates an entry.
    """
    out: list[tuple[str, ...]] = []
    if value.strip().lower() == "none":
        return out
    for tok in _split_csv(value):
        parts = [p.strip() for p in tok.split("/")]
        target = parts[0] if parts else ""
        if target == "models":
            if len(parts) != 4 or not all(parts):
                sys.stderr.write(f"warning: malformed 카탈로그 token {tok!r} (want models/group/series/handle)\n")
                continue
            _, group, series, handle = parts
            if group not in MODELS_GROUPS:
                sys.stderr.write(f"warning: invalid models group in {tok!r} (want vla|vlm|wam)\n")
                continue
            out.append(("models", group, series, handle))
        elif target in CATALOG_SECTIONS:
            if len(parts) != 3 or not all(parts):
                sys.stderr.write(f"warning: malformed 카탈로그 token {tok!r} (want target/section/handle)\n")
                continue
            _, section, handle = parts
            if section not in CATALOG_SECTIONS[target]:
                sys.stderr.write(f"warning: invalid 카탈로그 section in {tok!r}\n")
                continue
            out.append((target, section, handle))
        else:
            sys.stderr.write(f"warning: invalid 카탈로그 target in {tok!r} (want dataset|benchmark|models)\n")
            continue
    return out


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
    catalog: list[tuple[str, str, str]] = []
    catalog_seen = False
    design_na = False
    analysis_file = paper_dir / "analysis.md"
    try:
        text = analysis_file.read_text(encoding="utf-8")
    except OSError:
        return {
            "title": WARN, "arxiv_id": WARN, "arxiv_url": "",
            "refreshed": WARN, "pillars": [], "links": [], "catalog": [],
            "design_na": False,
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
        if not catalog_seen:
            m = CATALOG_ROW.match(line)
            if m:
                catalog = parse_catalog(m.group(1))
                catalog_seen = True
                continue
        if not design_na:
            m = DESIGN_ROW.match(line)
            if m and "비대상" in m.group(1):
                design_na = True
                continue

    return {
        "title": title or WARN,
        "arxiv_id": arxiv_id or WARN,
        "arxiv_url": arxiv_url,
        "refreshed": refreshed or WARN,
        "pillars": pillars,
        "links": links,
        "catalog": catalog,
        "design_na": design_na,
    }


def impl_state(stem: str, design_na: bool = False) -> str:
    """Return ✅ / 🚧 UNMAPPABLE / 🚫 / — for the impl column.

    Vendor-neutral header, but pathed to the v0 foundry (`lerobot`): ✅ when
    `impl/lerobot/impl.md` exists, 🚧 UNMAPPABLE when `UNMAPPABLE.md` exists,
    `—` when neither has been generated. A Design 비대상 paper (Design 적용 row)
    never gets an impl — surface that as a bare 🚫 marker, not a pending `—`,
    unless an impl artifact was somehow already generated.
    """
    base = ANALYSIS_DIR / stem / "impl" / "lerobot"
    if (base / "impl.md").is_file():
        return "✅"
    if (base / "UNMAPPABLE.md").is_file():
        return "🚧 UNMAPPABLE"
    if design_na:
        return "🚫"
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


# ── Catalog cross-link (catalog → index) ──────────────────────────────────
# Only the forward mark survives: a white post-it `📝` on the catalog side
# (front of a models.md bullet / the Analysis column of datasets.md /
# benchmarks.md) pointing at the paper's deep-dive. The reverse badge (index
# Links cell → catalog file) was dropped — it only pointed at a whole catalog
# file, never a specific row, so it carried no navigational value.
ANALYSIS_BADGE_COLOR = "ffffff"  # white
ANALYSIS_BADGE_ICON = "📝"
# The arXiv badge in a catalog entry — its id keys the forward mark.
CATALOG_ARXIV_BADGE_RE = re.compile(
    r"\[!\[arXiv\]\(https://img\.shields\.io/badge/arXiv-(\d{4}\.\d{4,5})-b31b1b\.svg\)\]\([^)]*\)"
)
# A leading analysis badge in a models.md bullet — spliced right after the list
# marker. Matched id-agnostically (and tolerant of the earlier `📄` / `📄_analysis`
# icons and any color) so re-runs strip-then-readd cleanly.
LEADING_DIVE_RE = re.compile(
    r"^\[!\[\]\(https://img\.shields\.io/badge/(?:📝|📄)(?:_analysis)?-[0-9a-fA-F]{6}\.svg\)\]\([^)]*\)\s+"
)
# Legacy trailing `deep-dive` badge (the prior models.md format) — stripped on
# migration so a re-run replaces it with the leading badge.
LEGACY_DIVE_RE = re.compile(r"\s*\[!\[deep-dive\][^\)]*\)\]\([^)]*\)")
# A models.md / catalog list bullet: leading whitespace + `*`/`-` marker.
BULLET_RE = re.compile(r"^(\s*[*-]\s+)(.*)$")


def _analysis_badge(stem: str) -> str:
    """Single-field `📝` badge (white) linking the deep-dive →
    `../analysis/<id>/analysis.md` (catalog sits at repo root, a sibling of
    analysis/). Used both at the front of a models.md bullet and in the
    dataset/benchmark Analysis column."""
    return (
        f"[![](https://img.shields.io/badge/{ANALYSIS_BADGE_ICON}-{ANALYSIS_BADGE_COLOR}.svg)]"
        f"(../analysis/{stem}/analysis.md)"
    )


def enrich_models(analysis_ids: set[str]) -> bool:
    """Inject/refresh leading 📄 analysis links in models.md; return True if changed.

    For every bullet carrying an arXiv badge whose id has an `analysis/<id>/`
    folder, splice a `[📄](…)` link right after the list marker. Any existing
    leading link (and any legacy trailing `deep-dive` badge) is stripped first
    so the op is idempotent and a deleted folder drops its link. Bullets with no
    arXiv badge (id-less entries) are left untouched. The hand-owned lineage
    grouping and `Updated` badge are never modified.
    """
    try:
        original = CATALOG.read_text(encoding="utf-8")
    except OSError:
        return False

    out_lines: list[str] = []
    for line in original.splitlines():
        bm = BULLET_RE.match(line)
        if not bm:
            out_lines.append(line)
            continue
        marker, rest = bm.group(1), bm.group(2)
        rest = LEGACY_DIVE_RE.sub("", rest)
        rest = LEADING_DIVE_RE.sub("", rest)
        am = CATALOG_ARXIV_BADGE_RE.search(rest)
        if am and am.group(1) in analysis_ids:
            rest = f"{_analysis_badge(am.group(1))} {rest}"
        out_lines.append(marker + rest)

    updated = "\n".join(out_lines)
    if original.endswith("\n"):
        updated += "\n"
    if updated == original:
        return False
    CATALOG.write_text(updated, encoding="utf-8")
    return True


def enrich_catalog_table(path: Path, analysis_ids: set[str]) -> bool:
    """Fill the trailing **Analysis** column of datasets.md / benchmarks.md.

    The tables are hand-curated; the script owns only the last cell of each data
    row. For a row whose arXiv id has an `analysis/<id>/` folder the cell becomes
    a `[📄](…)` link, otherwise `—`. Header and separator rows (no arXiv badge)
    are left untouched, as is everything outside the tables. Markdown table cells
    never contain an unescaped `|`, so splitting the row on `|` is safe.
    """
    try:
        original = path.read_text(encoding="utf-8")
    except OSError:
        return False

    out_lines: list[str] = []
    for line in original.splitlines():
        am = CATALOG_ARXIV_BADGE_RE.search(line)
        if line.lstrip().startswith("|") and am:
            cells = line.split("|")
            aid = am.group(1)
            cell = f" {_analysis_badge(aid)} " if aid in analysis_ids else " — "
            cells[-2] = cell  # last content cell (cells[-1] is the trailing '')
            line = "|".join(cells)
        out_lines.append(line)

    updated = "\n".join(out_lines)
    if original.endswith("\n"):
        updated += "\n"
    if updated == original:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def _skeleton_row(target: str, handle: str, meta: dict) -> str:
    """Build a fresh catalog row for `meta`: auto Links + Refreshed + Analysis,
    the four rich columns seeded `❓` for a human to backfill. The `#` is left
    `0`; `_renumber_table` fixes it once the row is in place."""
    links = link_badges(meta["links"], meta["arxiv_id"])
    refreshed = meta["refreshed"] if meta["refreshed"] != WARN else "—"
    rich = ["❓"] * len(CATALOG_RICH_COLS[target])
    cells = ["0", f"**{handle}**", links, *rich, refreshed, _analysis_badge(meta["stem"])]
    return "| " + " | ".join(cells) + " |"


def _renumber_table(table: list[str]) -> list[str]:
    """Renumber the leading `#` cell of a markdown table's data rows 1..n.
    `table[0]` is the header, `table[1]` the separator, the rest data rows."""
    out = table[:2]
    for idx, row in enumerate(table[2:], 1):
        cells = row.split("|")
        cells[1] = f" {idx} "
        out.append("|".join(cells))
    return out


def upsert_catalog_rows(path: Path, target: str, rows: list[dict]) -> bool:
    """Create a skeleton row for every analyzed paper routed here that is not yet
    in the table; never touch a row that already exists.

    Routing comes from each paper's `카탈로그` meta (`target/section/handle`). A
    new row is appended to the end of its section's table — Links / Refreshed /
    Analysis auto-filled, the rich columns `❓` — then the section's `#` column is
    renumbered. Rows already carrying the paper's arXiv id are left untouched
    (create-once; the human owns the cells thereafter), so the pass is idempotent.
    A routed section with no table in the file is warned and skipped.
    """
    routed: dict[str, list[tuple[str, dict]]] = {}
    for row in rows:
        for entry in row.get("catalog", []):
            # datasets/benchmarks routing is a 3-tuple; models is a 4-tuple,
            # handled separately by upsert_models_bullets.
            if entry[0] != target or len(entry) != 3:
                continue
            _, section, handle = entry
            routed.setdefault(section, []).append((handle, row))
    if not routed:
        return False
    label_to_key = {SECTION_LABELS[(target, key)]: key for key in CATALOG_SECTIONS[target]}

    try:
        original = path.read_text(encoding="utf-8")
    except OSError:
        return False
    lines = original.splitlines()

    out: list[str] = []
    cur_key: str | None = None
    seen_sections: set[str] = set()
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        if line.startswith("## "):
            cur_key = label_to_key.get(line[3:].strip())
            out.append(line)
            i += 1
            continue
        if cur_key and line.lstrip().startswith("|"):
            j = i
            while j < n and lines[j].lstrip().startswith("|"):
                j += 1
            table = lines[i:j]
            existing = {m.group(1) for t in table if (m := CATALOG_ARXIV_BADGE_RE.search(t))}
            for handle, meta in routed.get(cur_key, []):
                if meta["arxiv_id"] not in existing:
                    table.append(_skeleton_row(target, handle, meta))
                    existing.add(meta["arxiv_id"])
            out.extend(_renumber_table(table))
            seen_sections.add(cur_key)
            cur_key = None
            i = j
            continue
        out.append(line)
        i += 1

    for section in routed:
        if section not in seen_sections:
            sys.stderr.write(
                f"warning: 카탈로그 routes to {target}/{section} but {path.name} has no "
                f"'{SECTION_LABELS[(target, section)]}' table; skipping\n"
            )

    updated = "\n".join(out)
    if original.endswith("\n"):
        updated += "\n"
    if updated == original:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def _models_bullet(handle: str, meta: dict) -> str:
    """Build a fresh models.md bullet for `meta`: `* **<handle>**, <title>. <links>`.
    The leading `📝` analysis badge is added by `enrich_models` on the same run."""
    title = meta["title"] if meta["title"] != WARN else handle
    links = link_badges(meta["links"], meta["arxiv_id"])
    tail = f" {links}" if links not in ("—", WARN) else ""
    return f"* **{handle}**, {title}.{tail}"


def upsert_models_bullets(path: Path, rows: list[dict]) -> bool:
    """Create a skeleton bullet for every analyzed paper routed to `models` that
    is not yet listed; never touch an existing bullet.

    Routing is `models/group/series/handle`. A new bullet is inserted at the
    **top** of its `### <series>` lineage subsection (under the `## <group>`
    header), newest-first per the reverse-chronological convention. A paper whose
    arXiv id is already anywhere in the file is skipped (create-once; the human
    owns curation and ordering thereafter), so the pass is idempotent. A routed
    `### <series>` absent under its group is warned and skipped — brand-new
    lineage subsections are added by hand once, then auto-fill on the next run.
    """
    # group_label -> {series -> [(handle, meta), …]}
    routed: dict[str, dict[str, list[tuple[str, dict]]]] = {}
    for row in rows:
        for entry in row.get("catalog", []):
            if entry[0] != "models" or len(entry) != 4:
                continue
            _, group, series, handle = entry
            routed.setdefault(MODELS_GROUPS[group], {}).setdefault(series, []).append((handle, row))
    if not routed:
        return False

    try:
        original = path.read_text(encoding="utf-8")
    except OSError:
        return False
    existing_ids = set(ARXIV_ID_RE.findall(original))

    out: list[str] = []
    cur_group: str | None = None
    inserted: set[tuple[str, str]] = set()
    for line in original.splitlines():
        if line.startswith("## "):
            cur_group = line[3:].strip()
            out.append(line)
            continue
        out.append(line)
        if line.startswith("### ") and cur_group in routed:
            series = line[4:].strip()
            for handle, meta in routed[cur_group].get(series, []):
                if meta["arxiv_id"] not in existing_ids:
                    out.append(_models_bullet(handle, meta))
                    existing_ids.add(meta["arxiv_id"])
                inserted.add((cur_group, series))

    for group_label, by_series in routed.items():
        for series in by_series:
            if (group_label, series) not in inserted:
                sys.stderr.write(
                    f"warning: 카탈로그 routes to models/{group_label}/{series} but "
                    f"{path.name} has no '### {series}' subsection there; skipping\n"
                )

    updated = "\n".join(out)
    if original.endswith("\n"):
        updated += "\n"
    if updated == original:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def sort_key(row: dict) -> tuple[str, str]:
    # Refreshed date descending → tied by arXiv id descending.
    # Use string sort: ISO dates and arXiv ids both order lexically.
    refreshed = row["refreshed"] if row["refreshed"] != WARN else "0000-00-00"
    arxiv_id = row["arxiv_id"] if row["arxiv_id"] != WARN else ""
    return (refreshed, arxiv_id)


def primary_pillar(row: dict) -> str:
    return row["pillars"][0] if row["pillars"] else UNCLASSIFIED


def build_block(rows: list[dict]) -> str:
    """Compose the generated block: one table per primary Pillar."""
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
            link = f"[`{row['stem']}/analysis.md`](../analysis/{row['stem']}/analysis.md)"
            links_cell = link_badges(row["links"], row["arxiv_id"])
            out.append(
                f"| {i} | {link} | {links_cell} "
                f"| {row['title']} | {pillar_badges(row['pillars'])} "
                f"| {keyword_badges(row['keywords'])} "
                f"| {row['refreshed']} | {row['impl']} |\n"
            )
        out.append("\n")

    return "".join(out).rstrip() + "\n"


def rewrite_index(block: str) -> bool:
    """Replace the marker block in catalogs/analyses.md. Return True if changed."""
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

    rows: list[dict] = []
    for paper_dir in analyses:
        meta = extract_meta(paper_dir)
        meta["stem"] = paper_dir.name
        meta["keywords"] = extract_keywords(paper_dir)
        meta["impl"] = impl_state(paper_dir.name, meta.get("design_na", False))
        rows.append(meta)

    # Create any missing skeleton entries (routed by `카탈로그`), then fill the
    # forward catalog marks (the `📝` analysis badge on the catalog side).
    dataset_up = upsert_catalog_rows(CATALOG_DATASET, "dataset", rows)
    benchmark_up = upsert_catalog_rows(CATALOG_BENCHMARK, "benchmark", rows)
    models_up = upsert_models_bullets(CATALOG, rows)
    dataset_enr = enrich_catalog_table(CATALOG_DATASET, analysis_ids)
    benchmark_enr = enrich_catalog_table(CATALOG_BENCHMARK, analysis_ids)
    dataset_changed = dataset_up or dataset_enr
    benchmark_changed = benchmark_up or benchmark_enr

    block = build_block(rows)
    index_changed = rewrite_index(block)
    models_changed = models_up or enrich_models(analysis_ids)
    print(
        f"refresh-analysis-index: {len(rows)} analyses · "
        f"analyses.md {'updated' if index_changed else 'no change'} · "
        f"models.md {'updated' if models_changed else 'no change'} · "
        f"datasets.md {'updated' if dataset_changed else 'no change'} · "
        f"benchmarks.md {'updated' if benchmark_changed else 'no change'}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
