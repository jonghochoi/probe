"""The 발표 surface — AUTHORING §5 (S1–S9).

A deck for people outside the team, presented from the page itself. Parsing and
validation live here for the same reason as `glance.py`: its vocabulary is its
own, and `--check` has to catch a malformed deck without rendering it.

The two ceilings are the point of this module. Five drawn diagrams (S5) is
where a reviewer can still check every one against the original; four staged
slides (S6) is where a presenter can still remember the clicks. Both are
counted here rather than trusted to the author, because both are the kind of
budget that gets spent without anyone deciding to.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import components as c
from . import diagrams
from .mdext import probefence

SLIDES_MIN, SLIDES_MAX = 9, 13          # S3 — 11 ± 2
DIAGRAM_MAX = 5                          # S5
STEPPED_MAX = 4                          # S6
STEPS_MIN, STEPS_MAX = 2, 4
CHAPTERS = ("문제", "관찰", "방법", "결과", "정리")
KINDS = ("cover", "figure", "diagram", "film", "text")

_FENCE = re.compile(r"^```(probe-[a-z]+)[ \t]*\n(.*?)^```[ \t]*$", re.M | re.S)
_DREF = re.compile(r"(?<![A-Za-z0-9_])D\d{1,2}\b")
_CONTEXT = re.compile(r"\bcontext/[A-Za-z0-9_]+\.md")


@dataclass
class Deck:
    slides: list[dict] = field(default_factory=list)


def parse(source: str) -> tuple[Deck, list[str]]:
    problems: list[str] = []
    slides: list[dict] = []

    for match in _FENCE.finditer(source):
        kind = match.group(1)
        if kind != "probe-slide":
            problems.append(
                f"deck: ```{kind} does not belong here — a deck is one "
                f"```probe-slide per slide (S3)"
            )
            continue
        try:
            slides.append(probefence.parse(kind, match.group(2)))
        except probefence.FenceError as exc:
            problems.append(f"deck: {exc}")

    stray = _FENCE.sub("", source).strip()
    if stray:
        problems.append(
            f"deck: loose text outside the slide fences ({stray[:40]!r}…) — "
            f"everything a slide says belongs to that slide (S3)"
        )

    problems += _check_deck(slides)
    for index, slide in enumerate(slides, 1):
        problems += _check_slide(index, slide)
    problems += _check_outside_audience(source)
    return Deck(slides=slides), problems


# ── S3 · S5 · S6 · S9 — deck-wide ───────────────────────────────────────────

def _check_deck(slides: list[dict]) -> list[str]:
    problems = []
    if not SLIDES_MIN <= len(slides) <= SLIDES_MAX:
        problems.append(
            f"deck: {len(slides)} slides — S3's band is {SLIDES_MIN}–{SLIDES_MAX} "
            f"(11 ± 2). Under it the talk skips its own mechanism; over it the "
            f"deck is the body with bigger type"
        )
    covers = [i for i, s in enumerate(slides) if s.get("kind") == "cover"]
    if covers != [0]:
        problems.append(
            "deck: the first slide is the cover and there is exactly one "
            f"(covers at {covers or 'none'})"
        )

    drawn = sum(1 for s in slides if s.get("kind") == "diagram")
    if drawn > DIAGRAM_MAX:
        problems.append(
            f"deck: {drawn} drawn diagrams — the ceiling is {DIAGRAM_MAX} (S5). "
            f"Every one is a claim we own and have to verify against the "
            f"original; a sixth usually means a figure of the paper's went unused"
        )
    stepped = [s for s in slides if s.get("steps")]
    if len(stepped) > STEPPED_MAX:
        problems.append(
            f"deck: {len(stepped)} slides carry `steps` — at most {STEPPED_MAX} "
            f"(S6). Past that the presenter is remembering click counts"
        )

    # S9 — one contiguous run per chapter, in the fixed order.
    runs: list[str] = []
    for slide in slides:
        chapter = str(slide.get("chapter", "")).strip()
        if not chapter or (runs and runs[-1] == chapter):
            continue
        runs.append(chapter)
    seen = [ch for ch in runs if ch in CHAPTERS]
    if len(set(seen)) != len(seen):
        problems.append(
            f"deck: a chapter is split across the deck ({' → '.join(seen)}) — "
            f"slides in one chapter are contiguous (S9)"
        )
    elif seen != [ch for ch in CHAPTERS if ch in seen]:
        problems.append(
            f"deck: the chapters run out of order ({' → '.join(seen)}) — "
            f"{' → '.join(CHAPTERS)} (S9)"
        )
    return problems


# ── S3 · S4 · S7 · S8 — per slide ───────────────────────────────────────────

def _check_slide(index: int, slide: dict) -> list[str]:
    problems = []
    kind = str(slide.get("kind", "")).strip()
    where = f"deck slide {index}"
    if kind not in KINDS:
        problems.append(f"{where}: `kind` must be one of {', '.join(KINDS)} — got {kind!r}")
    if not str(slide.get("title", "")).strip():
        problems.append(
            f"{where}: missing `title` — it carries a claim, so that reading only "
            f"the titles is the talk (S3)"
        )
    if kind != "cover":
        chapter = str(slide.get("chapter", "")).strip()
        if chapter not in CHAPTERS:
            problems.append(
                f"{where}: `chapter` must be one of {' · '.join(CHAPTERS)} — got "
                f"{chapter!r} (S9)"
            )
        for key, why in (
            ("note", "what the presenter says here (S8)"),
            ("qa", "one anticipated question and its answer (S8)"),
        ):
            if not str(slide.get(key, "")).strip():
                problems.append(f"{where}: missing `{key}` — {why}")

    if kind in ("figure", "film"):
        if not str(slide.get("figure", "")).strip():
            problems.append(f"{where}: `kind: {kind}` needs the `figure` id it shows")
        url = str(slide.get("url", "")).strip()
        if not url.startswith(("http://", "https://")):
            problems.append(
                f"{where}: `url` must be the absolute arXiv URL — figures are "
                f"hotlinked, never mirrored (R6)"
            )
    if kind == "diagram":
        if not str(slide.get("why", "")).strip():
            problems.append(
                f"{where}: a drawn diagram needs `why` — name the figure of the "
                f"paper's that would have covered this and why it cannot serve "
                f"(no such figure / inline SVG with no file / unreadable at "
                f"presentation distance). S4"
            )
        problems += diagrams.check(slide.get("diagram"), where)
    if kind == "film":
        problems += diagrams.check_film(slide.get("film"), where)
    if kind == "text" and not slide.get("body"):
        problems.append(f"{where}: `kind: text` needs `body`")

    steps = slide.get("steps")
    if steps is not None:
        if not isinstance(steps, int) or not STEPS_MIN <= steps <= STEPS_MAX:
            problems.append(
                f"{where}: `steps` must be {STEPS_MIN}–{STEPS_MAX}, got {steps!r} (S6)"
            )
        elif kind in ("figure", "film"):
            problems.append(
                f"{where}: a photograph or a single figure is taken in at once — "
                f"staged reveals are for comparisons and accumulating numbers (S6)"
            )
        elif kind == "diagram":
            own = diagrams.groups(slide.get("diagram"))
            if steps != own:
                problems.append(
                    f"{where}: `steps` is {steps} but this diagram has {own} group(s) "
                    f"of its own — a reveal steps through the component's own units, "
                    f"so a mismatch lands mid-thought (S6)"
                )
        elif kind == "text":
            if steps > _text_units(slide.get("body")):
                problems.append(
                    f"{where}: `steps` is {steps} but the slide has "
                    f"{_text_units(slide.get('body'))} item(s) to reveal (S6)"
                )
    return problems


def _text_units(body) -> int:
    """How many things a text slide can reveal — columns, else lines."""
    if isinstance(body, dict) and isinstance(body.get("cols"), list):
        return len(body["cols"])
    return len(body) if isinstance(body, list) else 0


def _check_outside_audience(source: str) -> list[str]:
    problems = []
    refs = sorted(set(_DREF.findall(source)))
    if refs:
        problems.append(
            f"deck: our Decision Log appears here ({', '.join(refs)}) — the "
            f"audience is outside the team and cannot read it (S2)"
        )
    if _CONTEXT.search(source):
        problems.append("deck: a `context/` reference appears here — S2 forbids it")
    return problems


# ── rendering ───────────────────────────────────────────────────────────────

def render(model: Deck, renderer) -> str:
    if not model or not model.slides:
        return ""
    md = renderer.inline
    out = []
    for index, slide in enumerate(model.slides, 1):
        out.append(_slide(index, len(model.slides), slide, md))
    chapters = "".join(
        f'<span class="dk-ch" data-ch="{c.esc(ch)}">'
        f'<span class="dk-bead"></span>{c.esc(ch)}</span>'
        for ch in CHAPTERS
    )
    film = "".join(diagrams.film_style(s.get("film"), i)
                   for i, s in enumerate(model.slides, 1)
                   if s.get("kind") == "film")
    return (
        f"{film}"
        '<div class="deck" data-deck>'
        f'<div class="dk-stage" data-dk-stage tabindex="0" aria-label="슬라이드">'
        f'<div class="dk-chapters" data-dk-chapters>{chapters}</div>'
        + "".join(out)
        + "</div>"
        '<div class="dk-bar">'
        '<button type="button" class="dk-btn" data-dk-prev>← 이전</button>'
        '<button type="button" class="dk-btn" data-dk-next>다음 →</button>'
        '<span class="dk-count" data-dk-count></span>'
        '<button type="button" class="dk-btn" data-dk-full>전체화면</button>'
        '<span class="dk-spacer"></span>'
        '<span class="dk-hint">← → 키로도 넘어갑니다</span>'
        "</div>"
        '<div class="dk-film" data-dk-film></div>'
        '<div class="dk-notes" data-dk-notes>'
        '<span class="dk-nl">발표자 노트</span><p data-dk-note></p>'
        '<p class="dk-qa" data-dk-qa></p></div>'
        "</div>"
    )


def _slide(index: int, total: int, slide: dict, md) -> str:
    kind = str(slide.get("kind", "text")).strip()
    staged = isinstance(slide.get("steps"), int)
    title = md(str(slide.get("title", "")))
    kicker = c.esc(slide.get("kicker", ""))
    source = c.esc(slide.get("source", ""))
    # A full-bleed figure carries its origin in the caption band that already
    # sits at the bottom; printing `source` again in the footer stacks two
    # lines of mono on the same row.
    foot = (
        '<div class="dk-foot">'
        + (f"<span>{source}</span>" if kind not in ("figure", "film") else "<span></span>")
        + f'<span class="dk-pg">{index} / {total}</span></div>'
    )
    attrs = (
        f' data-dk-slide data-kind="{c.esc(kind)}"'
        f' data-ch="{c.esc(slide.get("chapter", ""))}"'
        f' data-note="{c.esc(slide.get("note", ""))}"'
        f' data-qa="{c.esc(slide.get("qa", ""))}"'
        + (f' data-steps="{int(slide["steps"])}"' if isinstance(slide.get("steps"), int) else "")
        + ("" if index == 1 else " hidden")
    )

    if kind == "cover":
        return (
            f'<section class="dk-slide dk-cover"{attrs}>'
            + (f'<span class="dk-kicker">{kicker}</span>' if kicker else "")
            + '<span class="dk-rule"></span>'
            f'<h2 class="dk-title">{title}</h2>'
            + (f'<p class="dk-body">{md(str(slide.get("lead", "")))}</p>'
               if slide.get("lead") else "")
            + f"{foot}</section>"
        )

    if kind in ("figure", "film"):
        caption = c.esc(slide.get("caption", ""))
        if kind == "figure":
            visual = (
                f'<div class="dk-bleed"><img src="{c.esc(slide.get("url", ""))}" '
                f'alt="{caption}" loading="lazy" decoding="async" '
                f'referrerpolicy="no-referrer"></div>'
            )
        else:
            visual = diagrams.film(slide.get("film"), slide.get("url", ""), index)
        return (
            f'<section class="dk-slide dk-figslide"{attrs}>{visual}'
            f'<div class="dk-cap"><h2 class="dk-title">{title}</h2>'
            + (f'<span class="dk-src">{caption}</span>' if caption else "")
            + f"</div>{foot}</section>"
        )

    if kind == "diagram":
        return (
            f'<section class="dk-slide"{attrs}>'
            + (f'<span class="dk-kicker">{kicker}</span>' if kicker else "")
            + f'<h2 class="dk-title dk-sm">{title}</h2>'
            f'<div class="dk-dg">{diagrams.draw(slide.get("diagram"))}</div>'
            f"{foot}</section>"
        )

    body = slide.get("body")
    if isinstance(body, dict) and isinstance(body.get("cols"), list):
        cols, cols_done = "", []
        for column in body["cols"]:
            head = ""
            lines = column
            if isinstance(column, dict):
                head = (f'<span class="dk-colhead">{c.esc(column.get("head", ""))}</span>'
                        if column.get("head") else "")
                lines = column.get("lines", [])
            items = "".join(f"<li>{md(str(line))}</li>" for line in lines or [])
            cols += f'<div>{head}<ul class="dk-list">{items}</ul></div>'
        inner = f'<div class="dk-cols">{cols}</div>'
    else:
        items = "".join(f"<li>{md(str(line))}</li>" for line in (body or []))
        inner = f'<ul class="dk-list">{items}</ul>'
    return (
        f'<section class="dk-slide"{attrs}>'
        + (f'<span class="dk-kicker">{kicker}</span>' if kicker else "")
        + f'<h2 class="dk-title dk-sm">{title}</h2>{inner}{foot}</section>'
    )
