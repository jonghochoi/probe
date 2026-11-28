"""The 요약 surface — AUTHORING §4 (G1–G6).

One screen: the claim, a narrative told in four moves, and the conditions
beside it. Parsing and validation live here rather than in `render.py`
because this surface has its own component vocabulary and its own failure
modes, and because `--check` has to catch them without rendering anything.

Two rules carry most of the weight and both are checked here:

* the spine is fixed (G2). The reader's path is claim → story → conditions,
  and a surface that reorders it delivers numbers before the reason they
  matter.
* our own view never appears (G6). Act 4 of the body is where a `D#` belongs;
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

# G4's four moves, in reading order. Each opens on a stanza that starts with
# its tag, `[문제] …`; the page prints the name in the margin beside the move.
MOVES = ("문제", "방법", "결과", "한계")

_FENCE = re.compile(r"^```(probe-[a-z]+)[ \t]*\n(.*?)^```[ \t]*$", re.M | re.S)
_SPACE = re.compile(r"\s")
# `D2DV` but not the `D` in `3D`: no letter, digit or `_` may stand on either
# side, so a decision id inside a longer token is not one.
_DREF = re.compile(r"(?<![A-Za-z0-9_])D\d[A-Z]{2}(?![A-Za-z0-9])")
_CONTEXT = re.compile(r"\bcontext/[A-Za-z0-9_]+\.md")
_LISTY = re.compile(r"^\s*(?:[-*+•]\s|\d+[.)]\s|#{1,6}\s|>\s)")
_MOVE = re.compile(r"^\[([^\]\s]{1,4})\]\s+")


@dataclass
class Glance:
    hub: dict = field(default_factory=dict)
    narrative: list[str] = field(default_factory=list)   # stanzas, tags stripped
    moves: list[tuple[str, int]] = field(default_factory=list)  # (name, first stanza)
    rail: list[dict] = field(default_factory=list)


def parse(source: str) -> tuple[Glance, list[str]]:
    """`(model, problems)` — everything G1–G6 can be checked without rendering."""
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

    known = {"probe-hub", "probe-rail", "prose"}
    for kind in kinds:
        if kind not in known:
            problems.append(
                f"glance: ```{kind} does not belong on this surface — the glance "
                f"is probe-hub, prose and probe-rail (G2)"
            )

    problems += _check_spine(kinds)
    model.hub, hub_problems = _hub(payloads.get("probe-hub", []))
    problems += hub_problems
    model.narrative, model.moves, narr_problems = _narrative(prose)
    problems += narr_problems
    model.rail, rail_problems = _rail(payloads.get("probe-rail", []))
    problems += rail_problems
    problems += _check_our_view(source)
    return model, problems


# ── G2 · the spine ──────────────────────────────────────────────────────────

def _check_spine(kinds: list[str]) -> list[str]:
    spine = [k for k in kinds if k in ("probe-hub", "prose", "probe-rail")]
    shape = []
    for kind in spine:
        if not shape or shape[-1] != kind:
            shape.append(kind)
    expected = ["probe-hub", "prose", "probe-rail"]
    if shape != expected:
        return [
            "glance: the spine is 중심 주장 카드 → 내러티브 → 팩트 레일 "
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

def _narrative(prose: list[str]) -> tuple[list[str], list[tuple[str, int]], list[str]]:
    if not prose:
        return [], [], ["glance: no narrative between the hub card and the rail (G4)"]
    text = "\n\n".join(prose)
    stanzas = [s.strip() for s in re.split(r"\n\s*\n", text) if s.strip()]
    moves, stanzas, problems = _moves(stanzas)
    text = "\n\n".join(stanzas)
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
    return stanzas, moves, problems


def _moves(stanzas: list[str]) -> tuple[list[tuple[str, int]], list[str], list[str]]:
    """`(moves, untagged stanzas, problems)` — G4's four moves, from their tags.

    A move is the author's call, not the build's: where 방법 starts differs
    from paper to paper and no keyword finds it. The build holds the tags to
    their order and to the one boundary it can see, the close on 한계.
    """
    moves, plain = [], []
    for i, stanza in enumerate(stanzas):
        m = _MOVE.match(stanza)
        if m:
            moves.append((m.group(1), i))
            stanza = stanza[m.end():]
        plain.append(stanza)
    names = [name for name, _ in moves]
    problems = []
    if names != list(MOVES):
        problems.append(
            f"glance: the narrative's moves are {' → '.join(names) or 'untagged'} — "
            f"G4 asks for {' → '.join(f'[{m}]' for m in MOVES)}, each tag opening "
            f"the stanza its move starts on"
        )
    elif moves[0][1] != 0:
        problems.append("glance: the narrative must open on its [문제] stanza (G4)")
    elif moves[-1][1] < len(stanzas) - 2:
        problems.append(
            "glance: [한계] starts more than two stanzas before the end — G4 closes "
            "on the author-stated limits, not on a section of them"
        )
    return (moves if not problems else []), plain, problems


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


# ── G6 · what may not appear ────────────────────────────────────────────────

def _check_our_view(source: str) -> list[str]:
    problems = []
    refs = sorted(set(_DREF.findall(source)))
    if refs:
        problems.append(
            f"glance: our open questions appear here ({', '.join(refs)}) — G6 keeps "
            f"this surface to the paper. Our view is act 4 of the body"
        )
    if _CONTEXT.search(source):
        problems.append("glance: a `context/` reference appears here — G6 forbids it")
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
        f'<span class="gh-v">{c.glue_units(esc(f.get("v", "")))}</span></div>'
        for f in model.hub.get("facts", []) if isinstance(f, dict)
    )
    fig = _figure(model.hub.get("figure"), model.hub.get("caption"), figure_urls)
    hub = (
        '<section class="g-hub">'
        + c.card_head("주장", "이 논문이 말하는 것")
        + '<div class="gh-text">'
        f'<h2 class="gh-thesis">{md(str(model.hub.get("thesis", "")))}</h2>'
        f'<p class="gh-line">{md(str(model.hub.get("line", "")))}</p>'
        f'<div class="gh-facts">{facts}</div></div>'
        + (f'<div class="gh-fig">{fig}</div>' if fig else "")
        + "</section>"
    )

    stanzas = _render_moves(model, md)
    rail = "".join(
        f'<div class="g-rail-item"><span class="gr-k">{esc(i.get("k", ""))}</span>'
        f'<p class="gr-v">{md(str(i.get("v", "")))}</p>'
        + (f'<p class="gr-n">{md(str(i["note"]))}</p>' if i.get("note") else "")
        + "</div>"
        for i in model.rail if isinstance(i, dict)
    )
    narrative = (
        '<section class="g-narr">'
        f'<div class="g-narr-h">{c.card_head("이야기", "한 번에 읽기")}</div>'
        f'<div class="g-narr-body">{stanzas}</div>'
        f'<aside class="g-rail">{rail}</aside>'
        "</section>"
    )

    return f'<div class="glance">{hub}{narrative}</div>'


def _render_moves(model: Glance, md) -> str:
    """The stanzas grouped by move, each stanza's first sentence as its lead.

    A rewrite whose tags fail G4 has no moves; its stanzas print ungrouped
    rather than under a name that may be wrong.
    """
    para = lambda s: f"<p>{_lead(md(s))}</p>"
    if not model.moves:
        return "".join(para(s) for s in model.narrative)
    out = []
    bounds = [i for _, i in model.moves] + [len(model.narrative)]
    for k, (name, start) in enumerate(model.moves):
        body = "".join(para(s) for s in model.narrative[start:bounds[k + 1]])
        out.append(
            f'<section class="gn-move" data-move="{k + 1}">'
            f'<span class="gn-mark">{c.esc(name)}</span>'
            f'<div class="gn-st">{body}</div></section>'
        )
    return "".join(out)


_TAG = re.compile(r"<(/?)([a-zA-Z][a-zA-Z0-9]*)\b[^>]*?(/?)>")
_VOID = {"br", "img", "wbr", "hr", "input", "col", "source"}
_STOP = re.compile(r"[.?!](?=\s)")
_LAST = re.compile(r"[.?!](?=\s|$)")   # the stanza's own end closes it too


def _lead(html: str) -> str:
    """Wrap a stanza's first sentence in `.gn-lead`.

    The sentence ends at the first `.`, `?` or `!` followed by a space that
    stands outside every inline element — a period inside math or a bold run
    is not the end of the sentence. A one-sentence stanza is its own lead.
    """
    depth, pos = 0, 0
    for m in list(_TAG.finditer(html)) + [None]:
        end = m.start() if m else len(html)
        if depth == 0:
            hit = (_LAST if m is None else _STOP).search(html, pos, end)
            if hit:
                cut = hit.end()
                return f'<span class="gn-lead">{html[:cut]}</span>{html[cut:]}'
        if m is None:
            break
        if m.group(2).lower() not in _VOID and not m.group(3):
            depth = max(0, depth + (-1 if m.group(1) else 1))
        pos = m.end()
    return html


def _figure(fid, caption, figure_urls: dict[str, str]) -> str:
    """A figure cited by id — the URL comes from the body's own `probe-figure`.

    Citing by id rather than by URL is what keeps one figure one hotlink: the
    body already declared where it lives, and a second URL here could drift
    from it silently. The image links to itself: beside the claim it stands
    at the narrow track's size, and an overview drawn finer than that opens
    whole in its own tab.
    """
    if not fid:
        return ""
    url = figure_urls.get(str(fid).strip())
    if not url:
        return ""
    cap = c.esc(caption or "")
    return (
        f'<a href="{c.esc(url)}" target="_blank" rel="noopener noreferrer" '
        'title="원본 크기로 보기">'
        f'<figure class="fig"><img src="{c.esc(url)}" alt="{cap}" '
        f'loading="lazy" decoding="async" referrerpolicy="no-referrer">'
        + (f"<figcaption>{cap}</figcaption>" if cap else "")
        + "</figure></a>"
    )
