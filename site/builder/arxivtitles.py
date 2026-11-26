"""The full title of each paper 빈자리 names.

A paper the corpus has not rewritten has only the name a lineage rail gives
it — usually an alias such as `π0` — so its title comes from arXiv's metadata
API, every id in one request.

Fetching is a network step, so a build asks for it (`--gap-titles`) and every
answer is kept in `.site-cache/arxiv-titles.json`. A build that does not fetch
still prints what the cache holds, and a paper with no entry prints its alias
alone. Standard library only.
"""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from .arxiv import TIMEOUT, UA

API = "https://export.arxiv.org/api/query"
CACHE_NAME = "arxiv-titles.json"
_ATOM = "{http://www.w3.org/2005/Atom}"
_ABS_ID = re.compile(r"arxiv\.org/abs/(\d{4}\.\d{4,5})(?:v\d+)?$")
# Inline TeX in a title: `$\pi_0$`, `$π_{0.5}$`, `M$^{2}$`. Printed as plain
# text, the dollars and a command's backslash go and the letters stay. A
# subscript keeps its characters on the line (`π0.5`, as the corpus writes
# it); a superscript of digits, signs or parentheses rises to Unicode (`M²`),
# and one that has no Unicode form stays on the line too.
_TEX_CMD = {r"\pi": "π", r"\alpha": "α", r"\beta": "β", r"\gamma": "γ",
            r"\delta": "δ", r"\epsilon": "ε", r"\lambda": "λ", r"\mu": "μ",
            r"\sigma": "σ", r"\tau": "τ", r"\phi": "φ", r"\omega": "ω",
            r"\Delta": "Δ", r"\times": "×", r"\cdot": "·", r"\dagger": "†"}
_SUPER = str.maketrans("0123456789+-=()n", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿ")
_STYLE = re.compile(r"\\(?:math[a-z]+|text[a-z]*|operatorname|boldsymbol)\{([^{}]*)\}")


def _rise(body: str) -> str:
    raised = body.translate(_SUPER)
    return raised if all(ch != o for ch, o in zip(raised, body)) else body


def plain_title(title: str) -> str:
    """A paper title with its inline TeX printed as plain text."""
    text = " ".join(title.split())
    text = _STYLE.sub(r"\1", text)
    for cmd, char in sorted(_TEX_CMD.items(), key=lambda kv: -len(kv[0])):
        text = re.sub(re.escape(cmd) + r"(?![A-Za-z])", char, text)
    text = re.sub(r"\^\{([^{}]*)\}", lambda m: _rise(m.group(1)), text)
    text = re.sub(r"\^([0-9n])", lambda m: _rise(m.group(1)), text)
    text = re.sub(r"_\{([^{}]*)\}", r"\1", text)
    text = re.sub(r"_(\w)", r"\1", text)
    return text.replace("$", "").replace("\\", "")


def _fetch(ids: list[str]) -> dict[str, str]:
    """`{id: title}` for the ids arXiv knows; empty when it cannot be reached."""
    query = urllib.parse.urlencode({"id_list": ",".join(ids), "max_results": len(ids)})
    req = urllib.request.Request(f"{API}?{query}", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            root = ET.fromstring(resp.read())
    except (OSError, ET.ParseError):
        return {}
    out = {}
    for entry in root.iter(f"{_ATOM}entry"):
        m = _ABS_ID.search(entry.findtext(f"{_ATOM}id", ""))
        title = plain_title(entry.findtext(f"{_ATOM}title", ""))
        if m and title:
            out[m.group(1)] = title
    return out


def titles(paper_ids: list[str], cache_dir: Path, *, fetch: bool) -> dict[str, str]:
    """Each id's title, from the cache and, when `fetch`, from arXiv."""
    path = cache_dir / CACHE_NAME
    try:
        cache = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        cache = {}
    todo = [pid for pid in dict.fromkeys(paper_ids) if pid not in cache]
    if fetch and todo:
        got = _fetch(todo)
        cache.update(got)
        cache_dir.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(cache, ensure_ascii=False, indent=0, sort_keys=True),
                        encoding="utf-8")
        missed = len(todo) - len(got)
        print(f"gap titles: {len(got)} fetched"
              + (f", {missed} unreachable" if missed else ""))
    return {pid: cache[pid] for pid in paper_ids if cache.get(pid)}
