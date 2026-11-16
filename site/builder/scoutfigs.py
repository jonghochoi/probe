"""The overview figure of each paper a scouting run recommends.

A recommended paper has no rewrite yet, so there is no `probe-figure` fence to
pick from: the figure comes from the paper's arXiv HTML edition, read with
`builder.arxiv`. The rule is the one `corpus.main_figure` applies to a
rewrite — an overview or architecture figure before a results chart, early
figures and method sections first, the appendix never — over the paper's own
English captions.

Fetching is a network step, so a build asks for it (`--scout-figures`) and
every answer, a figure or none, is kept in `.site-cache/scout-figures.json`.
A build that does not fetch still prints what the cache holds, and a paper
with no entry prints its card without a figure. Standard library only, like
`arxiv.py`, which it imports.
"""
from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import arxiv

CACHE_NAME = "scout-figures.json"
WORKERS = 8

_POS = ("overview", "architecture", "pipeline", "framework", "illustration of our",
        "our method", "our approach", "system")
_NEG = ("success rate", "result", "comparison", "ablation", "performance", "plot", "curve",
        "qualitative", "example", "scaling", "distribution", "vs.", "accuracy")
_FIG_ID = re.compile(r"(?:^|\.)F(\d+)$")
_SEC_ID = re.compile(r"^S(\d+)")
_APPENDIX = re.compile(r"^A\d")
_MATH = re.compile(r"\$([^$]*)\$")


def _clean(caption: str) -> str:
    """A caption as a reader reads it: inline TeX unwrapped, braces dropped,
    and the colon LaTeXML leaves after the figure's number gone."""
    text = _MATH.sub(lambda m: m.group(1).replace("{", "").replace("}", ""), caption)
    return re.sub(r"^[\s:.]+", "", re.sub(r"\s+", " ", text))


def _choose(paper: arxiv.Paper) -> dict | None:
    best, best_key = None, None
    for i, fig in enumerate(f for f in paper.figures if f.linkable):
        low = fig.caption.lower()
        s = (sum(3 for k in _POS if k in low[:90]) + sum(1 for k in _POS if k in low)
             - sum(2 for k in _NEG if k in low[:90]))
        num = _FIG_ID.search(fig.id)
        n = int(num.group(1)) if num else i + 1
        s += {1: 1, 2: 2, 3: 1}.get(n, 0)
        sec = _SEC_ID.match(fig.section or fig.id)
        if sec and sec.group(1) in ("2", "3", "4"):
            s += 1
        if _APPENDIX.match(fig.section or fig.id):
            s -= 4
        key = (s, -i)
        if best_key is None or key > best_key:
            source = f"Figure {n}" + (f", 원문 §{sec.group(1)}" if sec else ", arXiv 원문")
            best, best_key = {"url": fig.url, "caption": fig.caption, "source": source}, key
    return best


def _fetch(paper_id: str) -> tuple[str, dict | None, bool]:
    """`(id, figure or None, answered)` — `answered` is False when arXiv could
    not be reached, so the miss is not remembered."""
    try:
        html, _ = arxiv.fetch(paper_id)
    except arxiv.Unavailable as exc:
        # A stub page is an answer (the paper has no HTML edition); a dropped
        # connection is not.
        return paper_id, None, "no HTML edition" in str(exc) or "HTTP 404" in str(exc)
    try:
        return paper_id, _choose(arxiv.parse(html, paper_id)), True
    except Exception:  # a page LaTeXML drew in a shape the parser does not read
        return paper_id, None, True


def figures(paper_ids: list[str], cache_dir: Path, *, fetch: bool) -> dict[str, dict]:
    """Each id's figure, from the cache and, when `fetch`, from arXiv."""
    path = cache_dir / CACHE_NAME
    try:
        cache = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        cache = {}
    todo = [pid for pid in dict.fromkeys(paper_ids) if pid not in cache]
    if fetch and todo:
        with ThreadPoolExecutor(WORKERS) as pool:
            for pid, fig, answered in pool.map(_fetch, todo):
                if answered:
                    cache[pid] = fig
        cache_dir.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(cache, ensure_ascii=False, indent=0, sort_keys=True),
                        encoding="utf-8")
        missed = sum(1 for pid in todo if pid not in cache)
        print(f"scout figures: {len(todo) - missed} fetched"
              + (f", {missed} unreachable" if missed else ""))
    return {pid: {**cache[pid], "caption": _clean(cache[pid]["caption"])}
            for pid in paper_ids if cache.get(pid)}
