"""The 요약 surface — AUTHORING §4 (G1–G7).

One screen: the claim, a narrative, the conditions beside it, and the evidence
in four cards. Parsing and validation live here rather than in `render.py`
because this surface has its own component vocabulary and its own failure
modes, and because `--check` has to catch them without rendering anything.

Two rules carry most of the weight and both are checked here:

* the spine is fixed (G2). The reader's path is claim → story → conditions →
  evidence, and a surface that reorders it delivers numbers before the reason
  they matter.
* our own view never appears (G7). Act 4 of the body is where a `D#` belongs;
  one card away from the paper's own figures it reads as something the paper
  claimed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import components as c
from .mdext import probefence

# G4's length band. The printed target is 8–10 연 / 900–1,100 자; the build
# rejects outside the wider band, because "roughly" is the author's business
# and "a paragraph" or "the body again" is the build's.
STANZA_MIN, STANZA_MAX = 8, 10
CHARS_MIN, CHARS_MAX = 750, 1350

RAIL_MIN, RAIL_MAX = 5, 7
ACTS = 4

_FENCE = re.compile(r"^```(probe-[a-z]+)[ \t]*\n(.*?)^```[ \t]*$", re.M | re.S)
_SPACE = re.compile(r"\s")
# `D2DV` but not the `D` in `3D`: a word boundary already excludes a digit
# before it, and a `#` after guards the HTML entities the renderer emits.
_DREF = re.compile(r"(?<![A-Za-z0-9_])D\d[A-Z]{2}(?![A-Za-z0-9])")
_CONTEXT = re.compile(r"\bcontext/[A-Za-z0-9_]+\.md")
_LISTY = re.compile(r"^\s*(?:[-*+•]\s|\d+[.)]\s|#{1,6}\s|>\s)")


@dataclass
class Glance:
    hub: dict = field(default_factory=dict)
    narrative: list[str] = field(default_factory=list)
    rail: list[dict] = field(default_factory=list)
    acts: list[dict] = field(default_factory=list)


def parse(source: str) -> tuple[Glance, list[str]]:
    """`(model, problems)` — everything G1–G7 can be checked without rendering."""
    problems: list[str] = []
    model = Glance()

    blocks: list[tuple[str, str]] = []      # (kind, payload) in document order
    cursor = 0
    prose: list[str] = []
    for match in _FENCE.finditer(source):
        chunk = source[cursor:match.start()].strip()
        if chunk:
            blocks.append(("prose", chunk))
            prose.append(chunk)
        blocks.append((match.group(1), match.group(2)))
        cursor = match.end()
    tail = source[cursor:].strip()
    if tail:
        blocks.append(("prose", tail))
        prose.append(tail)

    kinds = [kind for kind, _ in blocks]
    payloads: dict[str, list[dict]] = {}
    for kind, raw in blocks:
        if kind == "prose":
            continue
        try:
            payloads.setdefault(kind, []).append(probefence.parse(kind, raw))
        except probefence.FenceError as exc:
            problems.append(f"glance: {exc}")

    known = {"probe-hub", "probe-rail", "probe-act", "prose"}
    for kind in kinds:
        if kind not in known:
            problems.append(
                f"glance: ```{kind} does not belong on this surface — the glance "
                f"is probe-hub, prose, probe-rail and four probe-act (G2)"
            )

    problems += _check_spine(kinds)
    model.hub, hub_problems = _hub(payloads.get("probe-hub", []))
    problems += hub_problems
    model.narrative, narr_problems = _narrative(prose)
    problems += narr_problems
    model.rail, rail_problems = _rail(payloads.get("probe-rail", []))
    problems += rail_problems
    model.acts, act_problems = _acts(payloads.get("probe-act", []))
    problems += act_problems
    problems += _check_our_view(source)
    return model, problems


# ── G2 · the spine ──────────────────────────────────────────────────────────

def _check_spine(kinds: list[str]) -> list[str]:
    spine = [k for k in kinds if k in ("probe-hub", "prose", "probe-rail", "probe-act")]
    shape = []
    for kind in spine:
        if not shape or shape[-1] != kind:
            shape.append(kind)
    expected = ["probe-hub", "prose", "probe-rail", "probe-act"]
    if shape != expected:
        return [
            "glance: the spine is 중심 주장 카드 → 내러티브 → 팩트 레일 → 4막 "
            f"(G2) — got {' → '.join(shape) or 'nothing'}"
        ]
    return []


# ── G3 · the hub card ───────────────────────────────────────────────────────

def _hub(cards: list[dict]) -> tuple[dict, list[str]]:
    if len(cards) != 1:
        return {}, [f"glance: expected exactly one ```probe-hub, got {len(cards)} (G3)"]
    hub = cards[0]
    problems = []
    for key in ("thesis", "line"):
        if not str(hub.get(key, "")).strip():
            problems.append(f"glance: probe-hub is missing `{key}` (G3)")
    facts = hub.get("facts") or []
    if not isinstance(facts, list) or not 2 <= len(facts) <= 4:
        problems.append(
            f"glance: probe-hub `facts` must be 2–4 numbers the paper states — got "
            f"{len(facts) if isinstance(facts, list) else type(facts).__name__} (G3)"
        )
    else:
        for fact in facts:
            if not isinstance(fact, dict) or not fact.get("k") or not fact.get("v"):
                problems.append(f"glance: probe-hub fact needs `k` and `v` (got {fact!r})")
    return hub, problems


# ── G4 · the narrative ──────────────────────────────────────────────────────

def _narrative(prose: list[str]) -> tuple[list[str], list[str]]:
    if not prose:
        return [], ["glance: no narrative between the hub card and the rail (G4)"]
    text = "\n\n".join(prose)
    stanzas = [s.strip() for s in re.split(r"\n\s*\n", text) if s.strip()]
    problems = []
    if not STANZA_MIN <= len(stanzas) <= STANZA_MAX:
        problems.append(
            f"glance: the narrative is {len(stanzas)} 연 — G4 asks for "
            f"{STANZA_MIN}–{STANZA_MAX}, one move per stanza"
        )
    size = len(_SPACE.sub("", text))
    if not CHARS_MIN <= size <= CHARS_MAX:
        problems.append(
            f"glance: the narrative is {size} chars — G4's band is "
            f"{CHARS_MIN}–{CHARS_MAX} (printed target 900–1,100). "
            f"{'Under it this is the summary again' if size < CHARS_MIN else 'Over it this is the body again'}"
        )
    listy = [s.splitlines()[0][:40] for s in stanzas if _LISTY.search(s)]
    if listy:
        problems.append(
            "glance: the narrative uses bullets, a heading or a quote "
            f"({', '.join(repr(x) for x in listy[:3])}) — G4 is flowing prose, and "
            f"a list here is a summary wearing prose clothes"
        )
    return stanzas, problems


# ── G5 · the fact rail ──────────────────────────────────────────────────────

def _rail(rails: list[dict]) -> tuple[list[dict], list[str]]:
    if len(rails) != 1:
        return [], [f"glance: expected exactly one ```probe-rail, got {len(rails)} (G5)"]
    items = rails[0].get("items")
    if not isinstance(items, list) or not RAIL_MIN <= len(items) <= RAIL_MAX:
        return [], [
            f"glance: probe-rail carries "
            f"{len(items) if isinstance(items, list) else type(items).__name__} items — "
            f"G5 asks for {RAIL_MIN}–{RAIL_MAX}, keyed by the questions the "
            f"narrative raises"
        ]
    problems = [
        f"glance: rail item needs `k` and `v` (got {item!r})"
        for item in items
        if not isinstance(item, dict) or not item.get("k") or not item.get("v")
    ]
    return items, problems


# ── G6 · four evidence cards ────────────────────────────────────────────────

def _acts(cards: list[dict]) -> tuple[list[dict], list[str]]:
    problems = []
    if len(cards) != ACTS:
        problems.append(
            f"glance: {len(cards)} ```probe-act — exactly {ACTS}, one per act (G6). "
            f"A fifth card means this surface is becoming the body"
        )
    ordered = sorted(cards, key=lambda c: c.get("n", 0))
    seen = []
    for card in ordered:
        n = card.get("n")
        title = str(card.get("title", "")).strip()
        if not isinstance(n, int) or not 1 <= n <= ACTS:
            problems.append(f"glance: probe-act `n` must be 1–{ACTS}, got {n!r}")
        elif n in seen:
            problems.append(f"glance: two probe-act cards share `n`: {n}")
        else:
            seen.append(n)
        if not title:
            problems.append(f"glance: probe-act[{n!r}] is missing `title` (R2 applies)")
        if not str(card.get("claim", "")).strip():
            problems.append(f"glance: probe-act[{title[:24] or n!r}] is missing `claim`")
        if not str(card.get("source", "")).strip():
            problems.append(
                f"glance: probe-act[{title[:24] or n!r}] is missing `source` — every "
                f"number on this surface is traceable without leaving it (G6)"
            )
        if not any(card.get(k) for k in ("figure", "eq", "scale")):
            problems.append(
                f"glance: probe-act[{title[:24] or n!r}] carries no figure, equation "
                f"or scale — a card of three prose lines is what G6 exists to prevent"
            )
    return ordered, problems


# ── G7 · what may not appear ────────────────────────────────────────────────

def _check_our_view(source: str) -> list[str]:
    problems = []
    refs = sorted(set(_DREF.findall(source)))
    if refs:
        problems.append(
            f"glance: our Decision Log appears here ({', '.join(refs)}) — G7 keeps "
            f"this surface to the paper. Our view is act 4 of the body"
        )
    if _CONTEXT.search(source):
        problems.append("glance: a `context/` reference appears here — G7 forbids it")
    return problems


# ── rendering ───────────────────────────────────────────────────────────────

def render(model: Glance, renderer, katex, figure_urls: dict[str, str]) -> str:
    """The tab's HTML. `renderer.inline` carries the corpus's inline dialect."""
    if not model or not model.hub:
        return ""
    md = renderer.inline
    esc = c.esc

    facts = "".join(
        f'<div class="gh-fact"><span class="gh-k">{esc(f.get("k", ""))}</span>'
        f'<span class="gh-v">{esc(f.get("v", ""))}</span></div>'
        for f in model.hub.get("facts", []) if isinstance(f, dict)
    )
    fig = _figure(model.hub.get("figure"), model.hub.get("caption"), figure_urls)
    hub = (
        '<section class="g-hub">'
        '<div class="gh-text"><span class="gh-l">중심 주장</span>'
        f'<h2 class="gh-thesis">{md(str(model.hub.get("thesis", "")))}</h2>'
        f'<p class="gh-line">{md(str(model.hub.get("line", "")))}</p>'
        f'<div class="gh-facts">{facts}</div></div>'
        + (f'<div class="gh-fig">{fig}</div>' if fig else "")
        + "</section>"
    )

    stanzas = "".join(f"<p>{md(s)}</p>" for s in model.narrative)
    rail = "".join(
        f'<div class="g-rail-item"><span class="gr-k">{esc(i.get("k", ""))}</span>'
        f'<p class="gr-v">{md(str(i.get("v", "")))}</p>'
        + (f'<p class="gr-n">{md(str(i["note"]))}</p>' if i.get("note") else "")
        + "</div>"
        for i in model.rail if isinstance(i, dict)
    )
    narrative = (
        '<section class="g-narr">'
        '<div class="g-narr-h"><span class="gn-l">한 번에 읽는 이야기</span></div>'
        f'<div class="g-narr-body">{stanzas}</div>'
        f'<aside class="g-rail">{rail}</aside>'
        "</section>"
    )

    cards = ""
    for card in model.acts:
        body = ""
        if card.get("eq"):
            body += f'<div class="ga-eq">{katex.block(str(card["eq"]))}</div>'
        if card.get("figure"):
            body += _figure(card.get("figure"), card.get("caption"), figure_urls)
        if isinstance(card.get("scale"), dict):
            body += probefence.scale(
                {"rows": card["scale"].get("rows", [])}, renderer.inline
            )
        cards += (
            f'<article class="g-act" data-n="{esc(card.get("n", ""))}">'
            f'<span class="ga-n">{esc(card.get("n", ""))}</span>'
            f'<h3 class="ga-t">{md(str(card.get("title", "")))}</h3>'
            f'<p class="ga-c">{md(str(card.get("claim", "")))}</p>'
            f"{body}"
            f'<p class="ga-s">{esc(card.get("source", ""))}</p>'
            "</article>"
        )
    return f'<div class="glance">{hub}{narrative}<div class="g-acts">{cards}</div></div>'


def _figure(fid, caption, figure_urls: dict[str, str]) -> str:
    """A figure cited by id — the URL comes from the body's own `probe-figure`.

    Citing by id rather than by URL is what keeps one figure one hotlink: the
    body already declared where it lives, and a second URL here could drift
    from it silently.
    """
    if not fid:
        return ""
    url = figure_urls.get(str(fid).strip())
    if not url:
        return ""
    cap = c.esc(caption or "")
    return (
        f'<figure class="fig"><img src="{c.esc(url)}" alt="{cap}" '
        f'loading="lazy" decoding="async" referrerpolicy="no-referrer">'
        + (f"<figcaption>{cap}</figcaption>" if cap else "")
        + "</figure>"
    )
