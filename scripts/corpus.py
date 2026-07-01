#!/usr/bin/env python3
"""Shared corpus parser for the PROBE `analysis/` tree.

This module is the single implementation of the `논문 메타` table parsing that
both `refresh-analysis-index.py` (the deep-dive index) and the supermemory PoC
ingestor (`supermemory_ingest.py`) consume. Keeping one parser is deliberate:
interpreting the same row spec in two places would let the index and the
retrieval layer drift apart. The row-spec SSOT is `docs/style.md` §5-7.

It owns:
  - corpus discovery (`find_analyses`)
  - meta-table extraction (`extract_meta`) — title / links / published /
    analyzed / pillars / tags
  - keyword extraction (`extract_keywords`)
  - supermemory-document construction (`build_analysis_doc`) + embedding-noise
    stripping (`strip_noise`)

Pure stdlib, no `main` — importable from either sibling script (both live in
`scripts/`, so `import corpus` resolves via `sys.path[0]`).

Specification: docs/style.md §5-7, docs/supermemory-poc-runbook.md §0.1.
"""

from __future__ import annotations

import re
import urllib.parse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ANALYSIS_DIR = REPO_ROOT / "analysis"

# Rows we extract from the 논문 메타 table.
TITLE_ROW = re.compile(r"^\|\s*원문\s*제목\s*\(영문\)\s*\|\s*(.+?)\s*\|\s*$")
LINK_ROW = re.compile(r"^\|\s*링크\s*\|\s*(.+?)\s*\|\s*$")
MD_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
ARXIV_ID_RE = re.compile(r"(\d{4}\.\d{4,5})")
REFRESHED_ROW = re.compile(r"^\|\s*분석\s*생성일\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*$")
PILLAR_ROW = re.compile(r"^\|\s*관련\s*Pillar\s*\|\s*(.+?)\s*\|\s*$")
# supermemory §2 additions (index ignores these; extractor uses them). The
# 발행일 / 버전 row leads with an ISO date then a ` · v1` / ` (…)` suffix; the
# 태그 row is a controlled-vocabulary list split on comma / middot.
PUBLISHED_ROW = re.compile(r"^\|\s*발행일\s*/\s*버전\s*\|\s*(\d{4}-\d{2}-\d{2})")
TAGS_ROW = re.compile(r"^\|\s*태그\s*\|\s*(.+?)\s*\|\s*$")

WARN = "⚠️ metadata"
UNCLASSIFIED = "미분류"

# P0–P5; anything outside the range is dropped at extraction time (mirrors the
# index taxonomy in refresh-analysis-index.py).
PILLAR_RE = re.compile(r"P[0-5]")


def find_analyses() -> list[Path]:
    """Return per-paper subdirectory paths (not templates or other dirs)."""
    out: list[Path] = []
    for path in sorted(ANALYSIS_DIR.iterdir()):
        if not path.is_dir():
            continue
        name = path.name
        # `templates` is the skeleton, not a paper.
        if name.startswith("_") or name == "templates":
            continue
        # Accept arXiv ids or arbitrary slug directory names.
        out.append(path)
    return out


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


def extract_meta(paper_dir: Path) -> dict:
    """Pull title / links / dates / pillars / tags out of the meta table.

    The `링크` row may carry several links (arXiv + GitHub / HuggingFace /
    project site); each is classified by host. Missing or malformed scalar rows
    produce the `⚠️ metadata` placeholder for that cell rather than aborting; a
    missing pillar/tags row yields an empty list. `published` (발행일) and
    `tags` (태그) are extra fields the supermemory extractor needs — the index
    script ignores them.
    """
    title = arxiv_id = arxiv_url = refreshed = published = ""
    links: list[tuple[str, str]] = []   # (kind, url), arXiv first
    pillars: list[str] = []
    tags: list[str] = []
    analysis_file = paper_dir / "analysis.md"
    try:
        text = analysis_file.read_text(encoding="utf-8")
    except OSError:
        return {
            "title": WARN, "arxiv_id": WARN, "arxiv_url": "",
            "refreshed": WARN, "published": WARN, "pillars": [],
            "tags": [], "links": [],
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
        if not published:
            m = PUBLISHED_ROW.match(line)
            if m:
                published = m.group(1).strip()
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
                tags = [t.strip() for t in re.split(r"[,·]", m.group(1)) if t.strip()]
                continue

    return {
        "title": title or WARN,
        "arxiv_id": arxiv_id or WARN,
        "arxiv_url": arxiv_url,
        "refreshed": refreshed or WARN,
        "published": published or WARN,
        "pillars": pillars,
        "tags": tags,
        "links": links,
    }


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


def _englishize(head: str) -> str:
    """Reduce a keyword head to its English form, dropping any Korean gloss.

    Bilingual heads in the corpus take the shape `한글 (English)` or
    `English (한글)`; we keep whichever side carries no Hangul. A head with no
    recoverable English (pure Korean) collapses to the empty string and is
    dropped by the caller — the English-only rule is enforced in
    docs/style.md §5-6 for new analyses.
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

    Reads the `## 기술 키워드` section (spec'd in docs/style.md §5-6) and
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


# ── supermemory PoC — noise stripping + document construction ────────────────

# shields.io badge markup, optionally wrapped in a link: `[![alt](…shields…)](href)`
# or a bare `![alt](…shields…)`. Meaningless to an embedding model (§6).
_BADGE_RE = re.compile(
    r"\[?!\[[^\]]*\]\(https://img\.shields\.io/[^)]*\)\]?(?:\([^)]*\))?"
)
# GitHub-flavoured inline math `$`…`$` and plain `$…$`: keep the inner token
# (`$`\pi_0`$` → `\pi_0`) rather than deleting it — the identifiers are
# meaningful and blanket removal depresses recall on math-heavy papers (§6).
_MATH_BACKTICK_RE = re.compile(r"\$`([^`]*)`\$")
_MATH_PLAIN_RE = re.compile(r"\$([^$\n]+)\$")
_MULTISPACE_RE = re.compile(r"[ \t]{2,}")
_MULTINEWLINE_RE = re.compile(r"\n{3,}")


def strip_noise(text: str) -> str:
    """Strip embedding noise from a markdown body (§6).

    Removes shields.io badge markup outright and unwraps KaTeX/`$`-delimited
    math to its inner text (delimiters gone, identifiers kept). Collapses the
    whitespace the removals leave behind. Order matters: the `$`…`$` backtick
    form is unwrapped before the plain `$…$` form.
    """
    text = _BADGE_RE.sub("", text)
    text = _MATH_BACKTICK_RE.sub(r"\1", text)
    text = _MATH_PLAIN_RE.sub(r"\1", text)
    text = _MULTISPACE_RE.sub(" ", text)
    text = _MULTINEWLINE_RE.sub("\n\n", text)
    return text.strip()


def _clean(value: str) -> str | None:
    """Map the WARN sentinel to None so it doesn't leak into metadata."""
    return None if value == WARN else value


def build_analysis_doc(paper_dir: Path) -> dict | None:
    """Build one supermemory document from an `analysis/<id>/analysis.md`.

    Maps the 논문 메타 table to supermemory fields per
    docs/supermemory-poc-runbook.md §0.1: `customId = arxiv:<id>`,
    `containerTag` = primary pillar, `containerTags` = all pillars, plus a
    `metadata` block (doc_type / pillars / tags / dates / title / keywords).
    Body is noise-stripped. Returns None when the arXiv id can't be recovered
    (malformed meta table) so a bad paper skips instead of crashing ingest.
    """
    meta = extract_meta(paper_dir)
    if meta["arxiv_id"] == WARN:
        return None
    raw = (paper_dir / "analysis.md").read_text(encoding="utf-8")
    pillars = meta["pillars"]
    doc = {
        "content": strip_noise(raw),
        "customId": f"arxiv:{meta['arxiv_id']}",
        "metadata": {
            "doc_type": "analysis",
            "pillars": pillars,
            "tags": meta["tags"],
            "decisions": [],  # analyses don't declare D# in the meta table (cut 1)
            "title": _clean(meta["title"]),
            "arxiv_id": meta["arxiv_id"],
            "published": _clean(meta["published"]),
            "analyzed": _clean(meta["refreshed"]),
            "keywords": extract_keywords(paper_dir),
        },
    }
    if pillars:
        doc["containerTag"] = pillars[0]
        doc["containerTags"] = pillars
    return doc
