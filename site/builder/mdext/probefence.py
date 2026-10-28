"""The ` ```probe-* ` fences of the rewrite layer.

`analysis/<id>.md` is markdown with JSON where structure is needed: an inline term
definition, a cited figure, a per-section quiz. JSON because the nesting
(quiz options, answer, explanation) parses strictly with the stdlib and fails
loudly when malformed — a silently half-parsed quiz would publish with no
right answer and nobody would notice.

Four of these fences carry the planted context AUTHORING §2-5 (R5) asks for.
Written as prose, 계보 is a paragraph, 숫자의 지형 is a sentence with numbers in
it, and 대조 is two adjacent paragraphs the reader has to hold side by side —
all three satisfy the rule and flatten into undifferentiated body text.
`probe-lineage`, `probe-scale`, `probe-split` and `probe-parts` are those
shapes made real.

Rendering these is not optional decoration. Without it the fences fall through
to the code highlighter and a term definition is published as a block of JSON,
so `analysis/AUTHORING.md` and this module are one contract: the guide tells the
agent the build validates its fences, and this is where that is true.

Every other fence language the corpus uses is `math` or a code language
(`analysis/AUTHORING.md` R8), so the `probe-` names do not collide with
anything an author might mean literally.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
from collections import Counter

FENCES = (
    "probe-term", "probe-figure", "probe-quiz", "probe-eq", "probe-flow",
    "probe-lineage", "probe-scale", "probe-split", "probe-parts",
)

# The short surface has its own fences, validated by `glance.py` where the
# counts across a surface can be seen. Named here so the body renderer can say
# so: one of these in the article is a section that ended up outside its `:::`
# container, and highlighting it as code would publish the JSON as a code
# block.
SURFACE_FENCES = ("probe-hub", "probe-rail", "probe-act")

# The comparison track's own fence, and the ones it may not use. A comparison
# compares; anything that zooms into a single paper belongs to that paper's own
# page, which every compared paper is guaranteed to have (comparison/AUTHORING.md).
# Both directions are reported rather than silently dropped — a fence that
# renders to nothing is one the author never learns was wrong.
COMPARE_FENCES = ("probe-matrix", "probe-figs", "probe-timeline")
COMPARE_BANNED = ("probe-figure", "probe-eq", "probe-quiz")


class FenceError(ValueError):
    """Malformed fence payload — carries a message fit for a build warning."""


def _esc(value) -> str:
    return html.escape(str(value or ""), quote=True)


def parse(info: str, content: str) -> dict:
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise FenceError(f"{info}: invalid JSON — {exc.msg} (line {exc.lineno})") from exc
    if not isinstance(data, dict):
        raise FenceError(f"{info}: expected a JSON object, got {type(data).__name__}")
    return data


# ── ```probe-term ───────────────────────────────────────────────────────────

def term(data: dict, inline_md) -> tuple[str, str]:
    """Return `(term_id, html)` for a definition panel.

    The panel is emitted **at the anchor**, not after the paragraph holding it
    (R4). Emitted after the paragraph, the definition would land one or two
    sentences below the word that needed it; opening it in place splits the
    paragraph exactly where the reader stopped.

    That placement is why this is a `<span>` wrapper and not a `<div>`: the
    anchor sits inside a `<p>`, and a block-level child there is invalid markup
    the parser would hoist somewhere else. The inner panel takes
    `display:block` from CSS instead.
    """
    tid = data.get("id", "").strip()
    if not tid:
        raise FenceError("probe-term: missing `id`")
    title = data.get("title", "").strip()
    body = data.get("body", "").strip()
    if not body:
        raise FenceError(f"probe-term[{tid}]: missing `body`")

    return tid, (
        f'<span class="tbox" data-term="{_esc(tid)}" hidden>'
        f'<span class="tdef">'
        # A dedicated title class, never a bare `b` (site/CLAUDE.md): `display:block` on an
        # inline tag also catches every `<b>` in the body and breaks the line at
        # each emphasis.
        f'<span class="th">{_esc(title) or _esc(tid)}</span>'
        f'<span class="tbody">{inline_md(body)}</span>'
        f"</span></span>"
    )



# ── ```probe-figure ─────────────────────────────────────────────────────────

def figure(data: dict) -> str:
    url = data.get("url", "").strip()
    if not url:
        raise FenceError(f"probe-figure[{data.get('id', '?')}]: missing `url`")
    if not url.startswith(("http://", "https://")):
        # Mirroring a paper's figure into the repo is a copyright problem
        # (AUTHORING §2-6); a relative URL here means someone did.
        raise FenceError(
            f"probe-figure[{data.get('id', '?')}]: `url` must be absolute — "
            f"figures are hotlinked, never mirrored"
        )
    caption = data.get("caption", "").strip()
    source = data.get("source", "").strip()
    # `source` is authored as `Figure <n>, 원문 §<x.y>` (R6). The figure number
    # is what a reader matches against the PDF open beside them, so it leads the
    # caption as a badge instead of trailing it in a parenthesis at the end of
    # three lines of Korean; only the origin stays at the back.
    num, _, origin = source.partition(",")
    num, origin = num.strip(), origin.strip()
    cap = ""
    if caption or source:
        cap = (
            "<figcaption>"
            + (f'<span class="fig-num">{_esc(num)}</span> — ' if num else "")
            + _esc(caption)
            + (f' <em class="fig-src">({_esc(origin)})</em>' if origin else "")
            + "</figcaption>"
        )
    return (
        f'<figure class="fig" id="fig-{_esc(data.get("id", ""))}">'
        f'<img src="{_esc(url)}" alt="{_esc(caption)}" loading="lazy" '
        f'decoding="async" referrerpolicy="no-referrer">{cap}</figure>'
    )


# ── ```probe-quiz ───────────────────────────────────────────────────────────

def quiz(data: dict, index: int, inline_md) -> str:
    options = data.get("options")
    question = (data.get("q") or "").strip()
    why = (data.get("why") or "").strip()
    answer = data.get("answer")

    if not question:
        raise FenceError("probe-quiz: missing `q`")
    if not isinstance(options, list) or len(options) != 3:
        raise FenceError(
            f"probe-quiz[{question[:32]}…]: `options` must be a list of 3, "
            f"got {len(options) if isinstance(options, list) else type(options).__name__}"
        )
    if not isinstance(answer, int) or not 0 <= answer < 3:
        raise FenceError(
            f"probe-quiz[{question[:32]}…]: `answer` must be an index 0–2, got {answer!r}"
        )
    if not why:
        raise FenceError(f"probe-quiz[{question[:32]}…]: missing `why`")

    # Buttons, not radios. A radio dot reads as a form the reader is filling in
    # and can be re-picked; the question is a single check with one shot at it,
    # and a full-width button says that without a legend explaining it.
    choices = "".join(
        f'<button type="button" class="qopt" '
        f'data-correct="{"1" if i == answer else "0"}">'
        f"{inline_md(str(opt).strip())}</button>"
        for i, opt in enumerate(options)
    )
    return (
        f'<section class="quiz" data-quiz="{index}">'
        f'<span class="q-label">확인</span>'
        f'<p class="qq">{inline_md(question)}</p>'
        f'<div class="qopts">{choices}</div>'
        f'<div class="qwhy" hidden>{inline_md(why)}</div>'
        f"</section>"
    )


# ── ```probe-eq ─────────────────────────────────────────────────────────────

def equation(data: dict, katex_block, inline_md) -> str:
    """A display equation with its reading line and symbol table (R7).

    A fence rather than raw HTML: the parser runs with `html=False`, so a
    hand-written `<div class="eqread">` would be escaped and published as
    visible angle brackets. This also lets the build check that a display
    equation actually carries its explanation.
    """
    tex = (data.get("tex") or "").strip()
    read = (data.get("read") or "").strip()
    symbols = data.get("symbols") or []
    if not tex:
        raise FenceError("probe-eq: missing `tex`")
    if not read:
        raise FenceError(f"probe-eq[{tex[:32]}…]: missing `read` — a display "
                         f"equation without its one-line reading is R7's whole point")
    if not isinstance(symbols, list):
        raise FenceError(f"probe-eq[{tex[:32]}…]: `symbols` must be a list")

    # A three-track grid, not a `<table>` with a 기호/이름/설명 header row. The
    # header restated what every glance already tells you — a formula, a name,
    # a sentence — and cost a boxed band of chrome directly under the equation,
    # which is the one place the eye should travel straight down.
    rows = ""
    for entry in symbols:
        if not isinstance(entry, dict) or not entry.get("sym"):
            raise FenceError(
                f"probe-eq[{tex[:32]}…]: each symbol needs at least `sym` "
                f"(got {entry!r})"
            )
        rows += (
            '<div class="sym-row">'
            # The corpus math dialect is GitHub's `$`X`$`, so the symbol cell
            # goes through the same inline rule as body math rather than a
            # second, ambiguous plain-`$` one.
            f'<span class="sym-k">{inline_md("$`" + str(entry["sym"]) + "`$")}</span>'
            f'<span class="sym-n">{_esc(entry.get("name", ""))}</span>'
            f'<span class="sym-d">{inline_md(str(entry.get("note", "")))}</span>'
            "</div>"
        )
    table = f'<div class="symtab">{rows}</div>' if rows else ""
    return (
        '<div class="eqblock">'
        f'<p class="eqread">읽으면 — <em>{_esc(read)}</em></p>'
        f"{katex_block(tex)}{table}</div>"
    )


# ── ```probe-flow ───────────────────────────────────────────────────────────

def flow(data: dict, inline_md, heads: list | None = None) -> str:
    """A hand-drawn step diagram — R6's fallback for a point the paper does
    not illustrate. HTML/CSS boxes, never ASCII art.

    `why` is required and prints under the diagram. A redrawn figure competes
    with figures the authors already drew, and when it wins by accident the
    reader gets a box of our labels in place of the paper's own picture — with
    nothing on the page saying an original existed. Naming the gap is cheap;
    having to name it is the check.

    In a comparison the same diagram is the map of where each paper intervenes:
    a step's `marks` names, per compared paper, what that paper does at that
    step, drawn with the paper's mark, and `blind` marks a step every paper
    leaves untouched. `heads` is the comparison's `(id, label, href, mark)` per
    paper; a rewrite passes none and may not mark. From the marks the build
    reads the comparison's shape — one step held by two or more papers is
    competition for one slot, marks on separate steps are papers filling
    different slots — and prints it over the diagram.
    """
    steps = data.get("steps")
    if not isinstance(steps, list) or not steps:
        raise FenceError("probe-flow: `steps` must be a non-empty list")
    why = str(data.get("why", "")).strip()
    if not why:
        raise FenceError(
            "probe-flow: `why` is required — state which figure of the paper "
            "would have covered this point and why it cannot be used "
            "(no such figure / inline SVG with no file to hotlink). "
            "If the paper does illustrate it, use `probe-figure` instead"
        )
    names = {pid: (label, mark) for pid, label, _, mark in (heads or [])}
    marked = [_flow_marks(b, names) for b in _flow_boxes(steps)]
    title = (data.get("title") or "").strip()
    head = f'<p class="flow-title">{_esc(title)}</p>' if title else ""
    if any(n >= 2 for n in marked):
        head += ('<p class="flow-verdict"><span class="flow-tag">경쟁형</span>'
                 '둘 이상이 같은 칸을 서로 다르게 메운다</p>')
    elif sum(1 for n in marked if n) >= 2:
        head += ('<p class="flow-verdict"><span class="flow-tag">보완형</span>'
                 '저마다 다른 칸을 메운다</p>')
    # Printed, not merely required: the reader deserves to know this box is
    # ours and what the paper had in its place.
    note = f'<p class="flow-why"><em class="fig-src">{_esc(why)}</em></p>'
    hot = sum(1 for s in _flow_boxes(steps) if isinstance(s, dict) and s.get("hot"))
    if hot > FLOW_HOT:
        raise FenceError(
            f"probe-flow: {hot} steps are `hot` — at most {FLOW_HOT}; the accent "
            "marks what to look at first, and on every step it marks nothing"
        )
    return f'<div class="flow">{head}{_flow_grid(steps, inline_md, names)}{note}</div>'


# A drawn flow keeps to what one look takes in; past these it is two flows.
FLOW_ROWS = 9
FLOW_LANES = (2, 3)
FLOW_HOT = 2
FLOW_LOOP_LABEL = 16
FLOW_MARK_MAX = 30


def _flow_marks(s, names: dict) -> int:
    """Check a step's `marks` and `blind`; the number of papers marking it."""
    if not isinstance(s, dict):
        return 0
    marks, blind = s.get("marks"), s.get("blind")
    if (marks or blind) and not names:
        raise FenceError("probe-flow: `marks` and `blind` belong to a comparison — "
                         "a rewrite describes one paper, so it has no papers to mark")
    if blind is not None and (not str(blind).strip() or len(str(blind)) > FLOW_MARK_MAX):
        raise FenceError(f"probe-flow: `blind` on {_flow_label(s)!r} says what every "
                         f"paper leaves here, in {FLOW_MARK_MAX} characters or fewer")
    if marks is None:
        return 0
    if blind is not None:
        raise FenceError(f"probe-flow: {_flow_label(s)!r} is both marked and `blind`")
    if not isinstance(marks, dict) or not marks:
        raise FenceError(f"probe-flow: `marks` on {_flow_label(s)!r} must map paper "
                         f"ids to what each does there")
    for pid, text in marks.items():
        if pid not in names:
            raise FenceError(f"probe-flow: `marks` names {pid!r}, which is not one of "
                             f"the compared papers ({', '.join(names)})")
        if not str(text).strip() or len(str(text)) > FLOW_MARK_MAX:
            raise FenceError(f"probe-flow: the mark of {pid} on {_flow_label(s)!r} is "
                             f"what it does there, in {FLOW_MARK_MAX} characters or fewer")
    return len(marks)


def _flow_boxes(steps):
    for s in steps:
        if isinstance(s, dict) and isinstance(s.get("lanes"), list):
            yield from s["lanes"]
        else:
            yield s


def _flow_label(s) -> str:
    return str(s.get("label", "") if isinstance(s, dict) else s).strip()


def _flow_box(s, inline_md, cls: str, extra: str = "", names: dict | None = None) -> str:
    hot = " hot" if isinstance(s, dict) and s.get("hot") else ""
    note = (f'<span class="fs-note">{inline_md(str(s["note"]))}</span>'
            if isinstance(s, dict) and s.get("note") else "")
    marks = s.get("marks") if isinstance(s, dict) else None
    if marks:
        # In the comparison's column order, so a paper keeps its place on every step.
        hot += " has-marks" + (" is-contested" if len(marks) >= 2 else "")
        note += '<span class="fs-marks">' + "".join(
            f'<span class="fs-mark" data-paper="{_esc(pid)}">{names[pid][1]}'
            f'<span>{inline_md(str(marks[pid]))}</span></span>'
            for pid in (names or {}) if pid in marks) + "</span>"
    if isinstance(s, dict) and s.get("blind"):
        hot += " is-blind"
        note += f'<span class="fs-blind">{inline_md(str(s["blind"]))}</span>'
    return (f'<li class="{cls}{hot}"><span class="fs-label">{inline_md(_flow_label(s))}</span>'
            f'{note}{extra}</li>')


def _flow_width(text: str) -> float:
    """The width `text` takes at the loop label's size, in rem — a Hangul
    syllable is a full em, anything else a little over half of one."""
    em = sum(1.0 if "\uac00" <= ch <= "\ud7a3" else 0.56 for ch in text)
    return em * 0.74


def _flow_grid(steps: list, inline_md, names: dict | None = None) -> str:
    """Steps down one spine, with the two shapes a list cannot say — lanes
    and a loop.

    A `lanes` row is work that runs side by side: the row before forks into
    it and the row after merges out of it, so two paths over the same input
    are not read as one step after the other. A `loop` on a step sends it
    back to an earlier one, named by its label, so a repeat is drawn once
    rather than unrolled into copies or folded into a last step that says 반복.

    Every connector is orthogonal and every bend one quarter arc — the
    connector rules of a routed schematic — and the whole figure is grid and
    borders, so labels wrap in the site's own type and the tokens carry it
    into the dark theme. A loop's label sits in a gutter sized to it, beside
    the line rather than on it.

    The grid is an `<ol>`, so a screen reader hears the steps in order, a
    lanes row as one item that says it splits (side by side in a
    rewrite, one lane per paper in a comparison), and a loop as a
    sentence on the step it leaves; the wires and the gutter label are
    hidden from it, since the words already say what they draw.
    """
    if len(steps) > FLOW_ROWS:
        raise FenceError(f"probe-flow: {len(steps)} rows — at most {FLOW_ROWS}; "
                         "past that it is two flows")
    loops = [(i, s["loop"]) for i, s in enumerate(steps, 1)
             if isinstance(s, dict) and "loop" in s]
    if len(loops) > 1:
        raise FenceError("probe-flow: one `loop` per flow — two loops cross "
                         "or nest, and either is two flows")
    back, gutter = {}, []
    for i, lp in loops:
        if not isinstance(lp, dict):
            raise FenceError(f"probe-flow: row {i} `loop` must be "
                             '{"to": "<an earlier step\'s label>", "label": "…"}')
        to, label = str(lp.get("to", "")).strip(), str(lp.get("label", "")).strip()
        hits = [r for r, s in enumerate(steps[:i - 1], 1)
                if not (isinstance(s, dict) and "lanes" in s) and _flow_label(s) == to]
        if len(hits) != 1:
            raise FenceError(f"probe-flow: row {i} `loop.to` must be the label of "
                             f"exactly one earlier step, written as it is — {to!r} "
                             f"matches {len(hits)}")
        if isinstance(steps[i - 1], dict) and "lanes" in steps[i - 1]:
            raise FenceError(f"probe-flow: row {i} `loop` — a loop leaves a single "
                             "step, not lanes")
        if not label or len(label) > FLOW_LOOP_LABEL:
            raise FenceError(f"probe-flow: row {i} `loop.label` is required and at "
                             f"most {FLOW_LOOP_LABEL} characters — what repeats and "
                             "how often; the rest goes in the step's `note`")
        back[i] = (f'<span class="sr"> 여기서 「{_esc(to)}」 단계로 돌아가 '
                   f'반복합니다 — {_esc(label)}.</span>')
        span = f"grid-row:{hits[0]} / {i + 1}"
        # Two lines at most: half the label's width, kept between a word and
        # the width the gutter can afford.
        line = min(max(_flow_width(label) / 2 + 0.4, 2.5), 5.25)
        gutter = [f"--fl-lw:{line:.2f}rem",
                  f'<li class="fl-loop" style="{span}" aria-hidden="true"></li>'
                  f'<li class="fl-loopnote" style="{span}" aria-hidden="true">'
                  f'{inline_md(label)}</li>']
    rows = []
    for i, s in enumerate(steps, 1):
        style = f' style="grid-row:{i}"'
        fin = " fg-in" if i > 1 else ""
        if isinstance(s, dict) and "lanes" in s:
            lanes = s["lanes"]
            if (not isinstance(lanes, list)
                    or not FLOW_LANES[0] <= len(lanes) <= FLOW_LANES[1]):
                raise FenceError(f"probe-flow: row {i} `lanes` must list "
                                 f"{FLOW_LANES[0]}–{FLOW_LANES[1]} steps")
            if any(isinstance(b, dict) and ("lanes" in b or "loop" in b) for b in lanes):
                raise FenceError(f"probe-flow: row {i} — a lane is one step, "
                                 "with no lanes or loop of its own")
            fork, merge = i > 1, i < len(steps)
            tip = " fg-tip" if fork else ""
            boxes = "".join(_flow_box(b, inline_md, "fg-step" + tip, names=names) for b in lanes)
            cls = (f"fg-lanes n{len(lanes)}" + (" fg-split" if fork else "")
                   + (" fg-join" if merge else ""))
            wires = ('<span class="fl-fork" aria-hidden="true"></span>' if fork else "") + (
                '<span class="fl-merge" aria-hidden="true"></span>' if merge else "")
            rows.append(f'<li class="{cls}" style="grid-row:{i};--n:{len(lanes)}">{wires}'
                        f'<span class="sr">{len(lanes)} 갈래로 나뉨:</span>'
                        f'<ul class="fl-par">{boxes}</ul></li>')
            continue
        rows.append(_flow_box(s, inline_md, "fg-step" + fin, back.get(i, ""), names)
                    .replace("<li ", f"<li{style} ", 1))
    if gutter:
        return (f'<ol class="fgrid has-loop" style="{gutter[0]}">'
                f'{"".join(rows)}{gutter[1]}</ol>')
    return f'<ol class="fgrid">{"".join(rows)}</ol>'


# ── ```probe-lineage ────────────────────────────────────────────────────────

def lineage(data: dict, inline_md, sibling=None) -> str:
    """R5's 계보 — the papers this one stands on, in date order.

    A dated rail rather than a paragraph naming three prior works: the reader's
    question is *what moved between them*, and a list answers that in one
    downward scan. Exactly one entry may be `current` — the paper being read —
    which is what turns a bibliography into a position.

    `sibling` is `url -> marker HTML`, given by the build for a rail entry that
    points at a paper the corpus has its own rewrite of. It defaults to nothing
    so a run can call this module with the fence alone.
    """
    items = data.get("items")
    if not isinstance(items, list) or not items:
        raise FenceError("probe-lineage: `items` must be a non-empty list")
    current = [i for i in items if isinstance(i, dict) and i.get("current")]
    if len(current) > 1:
        raise FenceError(
            f"probe-lineage: {len(current)} entries marked `current` — "
            f"exactly one (the paper being read) or none"
        )

    rows = ""
    for item in items:
        if not isinstance(item, dict) or not item.get("what"):
            raise FenceError(f"probe-lineage: each item needs `what` (got {item!r})")
        note = str(item.get("note", "")).strip()
        link = str(item.get("link", "")).strip()
        if link and not link.startswith(("http://", "https://")):
            raise FenceError(
                f"probe-lineage[{item['what'][:32]}…]: `link` must be absolute"
            )
        tail = (
            f' <a href="{_esc(link)}" target="_blank" rel="noopener">'
            f"{_esc(item.get('link_label') or link)}</a>"
            + (sibling(link) if sibling else "")
            if link else ""
        )
        # Title and note share one cell so the `current` tint can wrap the
        # entry's text without swallowing the date beside it — the date is the
        # rail the reader scans down, and tinting it breaks that column.
        rows += (
            f'<li class="ln-item{" cur" if item.get("current") else ""}">'
            f'<span class="ln-when">{_esc(item.get("when", ""))}</span>'
            f'<span class="ln-text">'
            f'<span class="ln-what">{inline_md(str(item["what"]))}</span>'
            + (f'<span class="ln-note">{inline_md(note)}{tail}</span>' if note else "")
            + "</span></li>"
        )
    title = str(data.get("title", "")).strip()
    # The three planted-context components share one framed shape — a titled
    # bar over a body — so the reader learns them as one family on first sight
    # instead of three differently-dressed boxes (R5).
    head = f'<div class="box-head">{_esc(title)}</div>' if title else ""
    return (f'<div class="lineage">{head}'
            f'<div class="box-body"><ol class="ln-list">{rows}</ol></div></div>')


# ── ```probe-scale ──────────────────────────────────────────────────────────

def scale(data: dict, inline_md) -> str:
    """R5's 숫자의 지형 — one number placed against the others of its kind.

    Bars are linear in `n` against the largest row, deliberately. A log scale
    would make every row look comparable, which is the opposite of the point:
    when the paper's own row is a stub next to the top of the range, the reader
    should see the stub.
    """
    rows_in = data.get("rows")
    if not isinstance(rows_in, list) or not rows_in:
        raise FenceError("probe-scale: `rows` must be a non-empty list")

    numbers = []
    for row in rows_in:
        if not isinstance(row, dict) or not row.get("label"):
            raise FenceError(f"probe-scale: each row needs `label` (got {row!r})")
        if "n" not in row:
            raise FenceError(
                f"probe-scale[{row['label']}]: missing `n` — the numeric value the "
                f"bar is drawn from (`value` is only its printed form)"
            )
        try:
            numbers.append(float(row["n"]))
        except (TypeError, ValueError):
            raise FenceError(
                f"probe-scale[{row['label']}]: `n` must be a number, got {row['n']!r}"
            ) from None
    top = max(numbers) or 1.0

    rows = ""
    for row, n in zip(rows_in, numbers):
        width = max(n / top * 100.0, 0.0)
        rows += (
            f'<div class="sc-row{" us" if row.get("us") else ""}">'
            f'<span class="sc-label">{inline_md(str(row["label"]))}</span>'
            f'<span class="sc-bar"><i style="width:{width:.4g}%"></i></span>'
            f'<span class="sc-v">{_esc(row.get("value", row["n"]))}</span>'
            "</div>"
        )
    title = str(data.get("title", "")).strip()
    head = f'<div class="box-head">{_esc(title)}</div>' if title else ""
    return f'<div class="scale">{head}<div class="box-body">{rows}</div></div>'


# ── ```probe-split ──────────────────────────────────────────────────────────

def split(data: dict, inline_md) -> str:
    """R5's 대조 — two or three things the paper holds apart, held apart here.

    The paper's contrast is structural (this channel is slow, that one is
    fast); rendering it as consecutive paragraphs asks the reader to rebuild
    the parallel from prose. Cards put the parallel in the layout.

    At most one card carries `us` — the position this paper takes in the
    contrast — and it is the only card that gets a color, the same accent that
    marks this paper's row in 숫자의 지형 and the reader's place in 계보. The
    cards are peers until one of them is the paper's own, so a second color
    would have to mean something, and there is nothing left for it to mean; a
    palette handed out per card instead says only that the cards are numbered,
    and runs out the moment a contrast grows.
    """
    cards = data.get("cards")
    if not isinstance(cards, list) or not 2 <= len(cards) <= 3:
        raise FenceError(
            f"probe-split: `cards` must be a list of 2–3, got "
            f"{len(cards) if isinstance(cards, list) else type(cards).__name__}"
        )
    out = ""
    marked = ""
    for card in cards:
        if not isinstance(card, dict) or not card.get("title") or not card.get("body"):
            raise FenceError(f"probe-split: each card needs `title` and `body` (got {card!r})")
        us = bool(card.get("us"))
        if us and marked:
            raise FenceError(
                f"probe-split[{card['title']}]: `us` is already on "
                f"[{marked}] — one card is the position this paper takes and "
                f"the rest are what it is held against, so only one carries it"
            )
        if us:
            marked = str(card["title"])
        tag = str(card.get("tag", "")).strip()
        note = str(card.get("note", "")).strip()
        out += (
            f'<div class="sp-card{" sp-us" if us else ""}">'
            f'<p class="sp-head">{inline_md(str(card["title"]))}'
            + (f'<span class="sp-tag">{_esc(tag)}</span>' if tag else "")
            + "</p>"
            f'<div class="sp-body">{inline_md(str(card["body"]))}</div>'
            + (f'<p class="sp-note">{inline_md(note)}</p>' if note else "")
            + "</div>"
        )
    return f'<div class="split">{out}</div>'


# ── ```probe-parts ──────────────────────────────────────────────────────────

# Color slots, not meanings. A row's `state` is the paper's own word for the
# condition that region is in, and the slot it lands in is decided by the order
# the states appear — so two rows in the same state are the same color because
# they say the same word, and the word is printed next to the color.
PART_STATE_SLOTS = 4


def parts(data: dict, inline_md) -> str:
    """One object decomposed into named regions — R5's 대조 in its other shape.

    A schedule split into front/interior/tail, a loss into its terms, a
    pipeline into its stages. The `label` is set in mono because it is the
    paper's own name for the region, `range` carries the math that bounds it,
    and `state` names the condition it is in. That vocabulary belongs to the
    rewrite — each paper cuts its object into the conditions that paper argues
    about — so the fence takes the words rather than supplying a fixed set.

    Rows sharing a state share a color, which is the whole reason the color is
    there. Either every row carries a state or none does — a half-labelled band
    says the unlabelled rows have no state, which is never what is meant.
    """
    rows_in = data.get("rows")
    if not isinstance(rows_in, list) or not rows_in:
        raise FenceError("probe-parts: `rows` must be a non-empty list")

    states = [str(row.get("state", "")).strip() if isinstance(row, dict) else ""
              for row in rows_in]
    if any(states) and not all(states):
        missing = [str(r.get("label", "?")) for r, s in zip(rows_in, states) if not s]
        raise FenceError(
            f"probe-parts: `state` is on some rows but not {', '.join(missing)} — "
            f"give every row a state or none of them"
        )
    slots: dict[str, int] = {}
    for state in states:
        if state and state not in slots:
            slots[state] = len(slots) + 1
    if len(slots) > PART_STATE_SLOTS:
        raise FenceError(
            f"probe-parts: {len(slots)} distinct states "
            f"({', '.join(slots)}) — at most {PART_STATE_SLOTS} carry a color; "
            f"merge the ones that mean the same thing, or use a table"
        )

    out = ""
    for row, state in zip(rows_in, states):
        if not isinstance(row, dict) or not row.get("label") or not row.get("body"):
            raise FenceError(f"probe-parts: each row needs `label` and `body` (got {row!r})")
        rng = str(row.get("range", "")).strip()
        out += (
            f'<div class="pt-row pt-s{slots.get(state, 0)}">'
            f'<div class="pt-label"><code>{_esc(row["label"])}</code>'
            + (f'<span class="pt-range">{inline_md(rng)}</span>' if rng else "")
            + (f'<span class="pt-state">{_esc(state)}</span>' if state else "")
            + "</div>"
            f'<div class="pt-body">{inline_md(str(row["body"]))}</div>'
            "</div>"
        )
    title = str(data.get("title", "")).strip()
    head = f'<div class="box-head">{_esc(title)}</div>' if title else ""
    # No `box-body` here: the rows run edge to edge and divide themselves, so
    # an inset wrapper would only add a margin the dividers have to stop short of.
    return f'<div class="parts">{head}{out}</div>'


def error_block(message: str) -> str:
    """A visible failure. A dropped fence would leave a hole nobody notices."""
    return f'<div class="fence-error">⚠️ {_esc(message)}</div>'


# ── ```probe-matrix ─────────────────────────────────────────────────────────

MATRIX_MIN, MATRIX_MAX = 3, 7
# An axis's `type` says what shape its answers take, and so how it is drawn
# (`comparison/AUTHORING.md` §3-1): sentences, a place on a few named stops,
# a yes/partly/no mark, or a measurement whose yardstick may differ by paper.
MATRIX_TYPES = ("text", "stops", "mark", "measure")
MATRIX_STOPS = (3, 5)
MATRIX_STOP_MAX = 16
MATRIX_METRIC_MAX = 20
# A mark is a claim, and `–` is the absence of one: drawn fainter than `○` so
# a paper that says nothing never reads as a paper that says no.
MATRIX_MARKS = {"●": ("full", "한다"), "◐": ("half", "일부"),
                "○": ("none", "못 한다"), "–": ("na", "원문 언급 없음")}


def matrix(data: dict, inline_md, heads: list[tuple[str, str, str, str]]) -> str:
    """The comparison track's grid — one question per row, one paper per column.

    Every other component here describes one paper. This one exists because a
    comparison that lets an axis speak about two of its three papers has
    stopped comparing: the schema requires a cell per paper per axis, so a
    thought that only fits two of them has to be reworded until it fits all
    three, or dropped. That reworking is where the comparison actually happens.

    Cells are placed by `of` rather than by position, so the author writes them
    in whatever order the axis reads best and the columns still line up.

    `heads` is `(id, label, href, mark)` per column, in column order — the
    fence has no way to know which papers are being compared or where their
    rewrites live, and both come from the document's front matter. `mark` is
    the paper's mark as markup (`components.paper_mark`), the same one its card
    and its branch of the fork carry. Every head and cell carries
    `data-paper`, so a reader pointing at one paper lights its whole column.
    """
    axes = data.get("axes")
    if not isinstance(axes, list) or not MATRIX_MIN <= len(axes) <= MATRIX_MAX:
        raise FenceError(
            f"probe-matrix: `axes` must be a list of {MATRIX_MIN}–{MATRIX_MAX}, got "
            f"{len(axes) if isinstance(axes, list) else type(axes).__name__} — "
            f"fewer than {MATRIX_MIN} is a sentence, more than {MATRIX_MAX} is a spreadsheet"
        )
    ids = [head[0] for head in heads]

    rows = ""
    for axis in axes:
        if not isinstance(axis, dict) or not str(axis.get("k", "")).strip():
            raise FenceError(f"probe-matrix: each axis needs `k`, the question it asks (got {axis!r})")
        key = str(axis["k"]).strip()
        cells = axis.get("cells")
        if not isinstance(cells, list):
            raise FenceError(f"probe-matrix[{key}]: `cells` must be a list")

        by_id: dict[str, dict] = {}
        for cell in cells:
            if not isinstance(cell, dict):
                raise FenceError(f"probe-matrix[{key}]: each cell must be an object (got {cell!r})")
            of = str(cell.get("of", "")).strip()
            if of not in ids:
                raise FenceError(
                    f"probe-matrix[{key}]: `of` is {of!r}, which is not one of the "
                    f"compared papers ({', '.join(ids)})"
                )
            if of in by_id:
                raise FenceError(f"probe-matrix[{key}]: two cells claim {of} — one per paper")
            if not str(cell.get("v", "")).strip():
                raise FenceError(f"probe-matrix[{key}] · {of}: missing `v`")
            by_id[of] = cell

        missing = [pid for pid in ids if pid not in by_id]
        if missing:
            # The one rule this component exists for. An axis that answers for
            # some of the papers is a remark about those papers, and it reads
            # on the page as though the others had nothing to say.
            raise FenceError(
                f"probe-matrix[{key}]: no cell for {', '.join(missing)} — an axis "
                f"answers for every compared paper or it is not an axis"
            )

        kind = str(axis.get("type", "text")).strip() or "text"
        if kind not in MATRIX_TYPES:
            raise FenceError(f"probe-matrix[{key}]: `type` is {kind!r} — one of "
                             f"{', '.join(MATRIX_TYPES)}")
        if kind == "stops":
            rows += _stops_row(key, axis, by_id, heads, inline_md)
            continue
        leads, flag = _cell_leads(key, kind, by_id, ids)

        tds = ""
        for pid in ids:
            cell = by_id[pid]
            note = str(cell.get("note", "")).strip()
            tds += (
                f'<td data-paper="{_esc(pid)}">{leads.get(pid, "")}'
                f'<span class="mx-v">{inline_md(str(cell["v"]))}</span>'
                + (f'<span class="mx-note">{inline_md(note)}</span>' if note else "")
                + "</td>"
            )
        rows += f'<tr><th scope="row" class="mx-k">{inline_md(key)}{flag}</th>{tds}</tr>'

    cols = "".join(
        f'<th scope="col" data-paper="{_esc(pid)}"><a href="{_esc(href)}">{mark}{_esc(label)}</a>'
        f'<span class="mx-id">{_esc(pid)}</span></th>'
        for pid, label, href, mark in heads
    )
    title = str(data.get("title", "")).strip()
    head = f'<div class="box-head">{_esc(title)}</div>' if title else ""
    # Three columns of Korean sentences overflow a phone, so the table scrolls
    # inside its own wrapper rather than taking the page with it.
    return (
        f'<div class="matrix">{head}'
        f'<div class="mx-wrap"><table class="mx">'
        f'<thead><tr><td class="mx-corner"></td>{cols}</tr></thead>'
        f"<tbody>{rows}</tbody>"
        "</table></div></div>"
    )


def _cell_leads(key: str, kind: str, by_id: dict, ids: list[str]) -> tuple[dict, str]:
    """What a `mark` or `measure` cell prints before its sentence, and the flag
    a `measure` row carries when its papers measured different things.

    A measurement means nothing next to another on a different yardstick, and
    the sentences rarely say so where a reader compares the numbers. So the
    build compares the `metric` each cell names: the papers outside a majority
    are flagged `다른 잣대`, and a row with no majority says its yardsticks all
    differ.
    """
    leads: dict[str, str] = {}
    if kind == "mark":
        for pid in ids:
            mark = str(by_id[pid].get("mark", "")).strip()
            if mark not in MATRIX_MARKS:
                raise FenceError(f"probe-matrix[{key}] · {pid}: a `mark` axis needs "
                                 f"`mark`, one of {' '.join(MATRIX_MARKS)}")
            cls, word = MATRIX_MARKS[mark]
            leads[pid] = f'<span class="mx-mk mx-mk-{cls}">{word}</span>'
        return leads, ""
    if kind != "measure":
        return leads, ""
    metrics: dict[str, str] = {}
    for pid in ids:
        metric = str(by_id[pid].get("metric", "")).strip()
        if not metric or len(metric) > MATRIX_METRIC_MAX:
            raise FenceError(f"probe-matrix[{key}] · {pid}: a `measure` axis needs "
                             f"`metric`, what the number measures, in "
                             f"{MATRIX_METRIC_MAX} characters or fewer")
        metrics[pid] = metric
    top, n = Counter(metrics.values()).most_common(1)[0]
    flag, off = "", set()
    if len(set(metrics.values())) > 1:
        if n * 2 > len(ids):
            off = {pid for pid, m in metrics.items() if m != top}
        else:
            flag = '<span class="mx-flag">잣대가 모두 다름</span>'
    for pid, metric in metrics.items():
        tag = "다른 잣대 · " if pid in off else ""
        leads[pid] = (f'<span class="mx-metric{" is-off" if pid in off else ""}">'
                      f'{tag}{_esc(metric)}</span>')
    return leads, flag


def _plain(md: str) -> str:
    """A cell's sentence as a tooltip — the markdown marks taken off."""
    return re.sub(r"[*`$\\]", "", md)


def _stops_row(key: str, axis: dict, by_id: dict, heads: list, inline_md) -> str:
    """A `stops` axis: a few named places, each paper's mark on the one it holds.

    The places are the author's, named from values the compared papers actually
    reach, and they say order only — never distance — so the drawing gives
    every stop the same width. `probes` are places a paper went only in an
    ablation, drawn as its mark hollow, so an empty-looking stop that was tried
    and failed does not read as one nobody tried. The sentences stay one click
    down, under the strip, where each mark's grounds can be checked.
    """
    stops = axis.get("stops")
    lo, hi = MATRIX_STOPS
    if (not isinstance(stops, list) or not lo <= len(stops) <= hi
            or not all(isinstance(t, str) and t.strip() for t in stops)):
        raise FenceError(f"probe-matrix[{key}]: a `stops` axis needs `stops`, "
                         f"{lo}–{hi} names for the places on it")
    for t in stops:
        if len(t) > MATRIX_STOP_MAX:
            raise FenceError(f"probe-matrix[{key}]: stop {t!r} is {len(t)} chars — "
                             f"keep a stop's name to {MATRIX_STOP_MAX}")
    names = {pid: (label, mark) for pid, label, _, mark in heads}

    def at(where: str, value) -> int:
        if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value < len(stops):
            raise FenceError(f"probe-matrix[{key}] · {where}: `at` must be the index "
                             f"of a stop, 0–{len(stops) - 1}")
        return value

    pins: list[list[str]] = [[] for _ in stops]
    lines = []
    for pid, (label, mark) in names.items():
        cell = by_id[pid]
        i = at(pid, cell.get("at"))
        pins[i].append(f'<span class="mx-pin" data-paper="{_esc(pid)}" '
                       f'title="{_esc(label)} — {_esc(_plain(str(cell["v"])))}">{mark}</span>')
        note = str(cell.get("note", "")).strip()
        lines.append(f'<li data-paper="{_esc(pid)}">{mark}<span><span class="mx-v">'
                     f'{inline_md(str(cell["v"]))}</span>'
                     + (f'<span class="mx-note">{inline_md(note)}</span>' if note else "")
                     + "</span></li>")
    probes = axis.get("probes", [])
    if not isinstance(probes, list):
        raise FenceError(f"probe-matrix[{key}]: `probes` must be a list")
    for probe in probes:
        pid = str(probe.get("of", "")).strip() if isinstance(probe, dict) else ""
        if pid not in names or not str(probe.get("v", "")).strip():
            raise FenceError(f"probe-matrix[{key}]: each probe needs `of` (a compared "
                             f"paper), `at` and `v`, what the ablation found")
        i = at(f"probe of {pid}", probe.get("at"))
        label, mark = names[pid]
        pins[i].append(f'<span class="mx-pin is-probe" data-paper="{_esc(pid)}" '
                       f'title="{_esc(label)} 절제 실험 — {_esc(_plain(str(probe["v"])))}">{mark}</span>')
        lines.append(f'<li data-paper="{_esc(pid)}">{mark}<span><span class="mx-v">'
                     f'<span class="mx-probe-l">절제 실험</span> {inline_md(str(probe["v"]))}</span></span></li>')
    strip = "".join(
        f'<div class="mx-stop"><span class="mx-pins">{"".join(p)}</span>'
        f'<span class="mx-stop-l">{_esc(t.strip())}</span></div>'
        for t, p in zip(stops, pins))
    return (f'<tr class="mx-row-stops"><th scope="row" class="mx-k">{inline_md(key)}</th>'
            f'<td colspan="{len(names)}"><div class="mx-stops" style="--k:{len(stops)}">{strip}</div>'
            f'<details class="mx-why"><summary>칸마다 근거</summary><ul>{"".join(lines)}</ul></details>'
            "</td></tr>")


# ── ```probe-figs ───────────────────────────────────────────────────────────

FIGS_Q_MAX, FIGS_LOOK_MAX = 40, 60


def figs(data: dict, inline_md, heads: list, figures: dict) -> str:
    """The compared papers' own figures for one question, one frame at a time.

    The truest picture of a mechanism is the one its authors drew, and the
    comparison may show it — but never three figures squeezed side by side,
    where a diagram shrinks past reading and mismatched shapes pad out with
    blank space. One frame holds one paper's figure at the column's full
    width, and the reader switches papers in place, so what differs is what
    changes on screen.

    A figure is named by its id in that paper's own rewrite, which already
    declares where it lives; the URL and the original's figure number come
    from there, so a comparison cannot point at a figure the rewrite does not
    carry. `figures` is `{paper id: {figure id: (url, source)}}`.
    """
    q = str(data.get("q", "")).strip()
    if not q or len(q) > FIGS_Q_MAX:
        raise FenceError(f"probe-figs: `q` is required — the one question every "
                         f"figure here answers, in {FIGS_Q_MAX} characters or fewer")
    items = data.get("figs")
    names = {pid: (label, mark) for pid, label, _, mark in heads}
    if not isinstance(items, list) or len(items) < 2:
        raise FenceError("probe-figs: `figs` needs a figure from at least two of "
                         "the compared papers — one paper's figure is its own page's")
    by_id: dict[str, dict] = {}
    for item in items:
        pid = str(item.get("of", "")).strip() if isinstance(item, dict) else ""
        if pid not in names:
            raise FenceError(f"probe-figs: `of` is {pid!r}, which is not one of the "
                             f"compared papers ({', '.join(names)})")
        if pid in by_id:
            raise FenceError(f"probe-figs: two figures for {pid} — one per paper")
        fid = str(item.get("fig", "")).strip()
        have = figures.get(pid, {})
        if fid not in have:
            raise FenceError(f"probe-figs · {pid}: `fig` is {fid!r}, which its rewrite "
                             f"does not carry — one of {', '.join(have) or 'none'}")
        look = str(item.get("look", "")).strip()
        if not look or len(look) > FIGS_LOOK_MAX:
            raise FenceError(f"probe-figs · {pid}: `look` is required — where in the "
                             f"figure to look, in {FIGS_LOOK_MAX} characters or fewer")
        by_id[pid] = item
    tabs, panels = "", ""
    for k, pid in enumerate(p for p in names if p in by_id):
        label, mark = names[pid]
        url, source = figures[pid][str(by_id[pid]["fig"]).strip()]
        look = str(by_id[pid]["look"]).strip()
        tabs += (f'<button type="button" role="tab" data-paper="{_esc(pid)}" '
                 f'data-figs-tab="{_esc(pid)}" aria-selected="{"true" if k == 0 else "false"}">'
                 f'{mark}{_esc(label)}</button>')
        panels += (f'<figure class="figs-panel" data-figs-panel="{_esc(pid)}">'
                   f'<div class="figs-frame"><img src="{_esc(url)}" loading="lazy" '
                   f'alt="{_esc(label)} 원문 그림 — {_esc(_plain(look))}"></div>'
                   f'<figcaption>{mark}<span class="figs-look">{inline_md(look)}</span>'
                   f'<span class="figs-src">{_esc(label)} · {_esc(source)}</span></figcaption></figure>')
    return (f'<div class="figs" data-figs><p class="figs-q">{_esc(q)}</p>'
            f'<div class="figs-tabs" role="tablist" aria-label="논문 고르기" hidden>{tabs}</div>'
            f'<div class="figs-panels">{panels}</div></div>')


# ── ```probe-timeline ───────────────────────────────────────────────────────

TL_STYLES = ("solid", "part", "faint", "over")
TL_LEVELS = 4
TL_LABEL_MAX, TL_NOTE_MAX, TL_UNIT_MAX, TL_CUT_MAX = 12, 60, 6, 40
TL_EVENTS_MAX = 64


def timeline(data: dict, inline_md, heads: list) -> str:
    """The compared papers on one clock — what each does, and when.

    A comparison that parts over time (a control period, a chunk being run,
    what is read again mid-way) is drawn on one shared ruler: `span` units
    long, one row per paper. A row is spans and ticks, never coordinates — the
    author states values on the ruler and the build places them, so every mark
    is checkable against the paper by reading the fence.

    A span's `style` is what happens over that stretch: `solid` the paper does
    it, `part` it is handed over half-made, `faint` it is made and thrown away,
    `over` a thin layer added on top. `level` stacks a span on a sub-row of its
    own, for a paper that redoes the same stretch more than once. `every` puts
    a tick at a fixed period, for a signal read again and again. `cuts` are
    places on the ruler every row shares, drawn through the rows' bars and
    never through their words.

    The drawing is ours, not the paper's, so `why` is required and printed, as
    on `probe-flow`.
    """
    names = {pid: (i, label, mark) for i, (pid, label, _, mark) in enumerate(heads)}
    span = data.get("span")
    if not isinstance(span, (int, float)) or isinstance(span, bool) or span <= 0:
        raise FenceError("probe-timeline: `span` is the ruler's length, a positive number")
    unit = str(data.get("unit", "")).strip()
    if not unit or len(unit) > TL_UNIT_MAX:
        raise FenceError(f"probe-timeline: `unit` names the ruler's unit "
                         f"(스텝, 초, ms), {TL_UNIT_MAX} characters or fewer")
    why = str(data.get("why", "")).strip()
    if not why:
        raise FenceError("probe-timeline: `why` is required — which figure of the "
                         "papers would have covered this and why none can")

    def on_ruler(where: str, v) -> float:
        if not isinstance(v, (int, float)) or isinstance(v, bool) or not 0 <= v <= span:
            raise FenceError(f"probe-timeline: {where} must be a value on the ruler, 0–{span}")
        return float(v)

    ticks = data.get("ticks")
    if ticks is None:
        ticks = [span * k / 4 for k in range(5)]
    if not isinstance(ticks, list) or not ticks:
        raise FenceError("probe-timeline: `ticks` must be a list of values on the ruler")
    ticks = [on_ruler("a tick", t) for t in ticks]
    cuts = [on_ruler("a cut", c) for c in (data.get("cuts") or [])]
    cut_label = str(data.get("cut_label", "")).strip()
    if cuts and (not cut_label or len(cut_label) > TL_CUT_MAX):
        raise FenceError(f"probe-timeline: `cuts` need `cut_label`, what the shared "
                         f"places are, in {TL_CUT_MAX} characters or fewer")
    rows = data.get("rows")
    if not isinstance(rows, list) or len(rows) < 2:
        raise FenceError("probe-timeline: `rows` needs at least two compared papers")
    seen = set()
    for r in rows:
        pid = str(r.get("of", "")).strip() if isinstance(r, dict) else ""
        if pid not in names or pid in seen:
            raise FenceError(f"probe-timeline: a row's `of` is {pid!r} — each row is one "
                             f"compared paper, once ({', '.join(names)})")
        seen.add(pid)
        label, note = str(r.get("label", "")).strip(), str(r.get("note", "")).strip()
        if not label or len(label) > TL_LABEL_MAX:
            raise FenceError(f"probe-timeline · {pid}: `label` is what this paper does, "
                             f"{TL_LABEL_MAX} characters or fewer")
        if len(note) > TL_NOTE_MAX:
            raise FenceError(f"probe-timeline · {pid}: `note` is one line, "
                             f"{TL_NOTE_MAX} characters or fewer")
        spans = r.get("spans", [])
        if not isinstance(spans, list) or not (spans or r.get("every")):
            raise FenceError(f"probe-timeline · {pid}: a row needs `spans`, `every` or both")
        for sp in spans:
            if not isinstance(sp, dict) or sp.get("style", "solid") not in TL_STYLES:
                raise FenceError(f"probe-timeline · {pid}: a span's `style` is one of "
                                 f"{', '.join(TL_STYLES)}")
            a, b = on_ruler(f"{pid} `from`", sp.get("from")), on_ruler(f"{pid} `to`", sp.get("to"))
            if a >= b:
                raise FenceError(f"probe-timeline · {pid}: a span runs `from` before `to`")
            lv = sp.get("level", 0)
            if not isinstance(lv, int) or isinstance(lv, bool) or not 0 <= lv < TL_LEVELS:
                raise FenceError(f"probe-timeline · {pid}: `level` is 0–{TL_LEVELS - 1}")
        every = r.get("every")
        if every is not None:
            ev = every.get("at") if isinstance(every, dict) else None
            if not isinstance(ev, (int, float)) or isinstance(ev, bool) or ev <= 0 or span / ev > TL_EVENTS_MAX:
                raise FenceError(f"probe-timeline · {pid}: `every` is "
                                 f'{{"at": <period>, "label": "…"}}, at most {TL_EVENTS_MAX} ticks')

    uid = hashlib.md5(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:6]
    X0, X1, W = 170.0, 880.0, 900
    px = lambda v: X0 + (X1 - X0) * v / span
    num = lambda v: f"{v:g}"
    out = ["<defs>"] + [
        f'<pattern id="tl{uid}-{i}" class="pm-{i + 1}" width="6" height="6" '
        f'patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        f'<line x1="0" y1="0" x2="0" y2="6" class="tl-hatch"/></pattern>'
        for i in range(len(heads))] + ["</defs>"]
    out.append(f'<line x1="{X0}" y1="26" x2="{X1}" y2="26" class="tl-axis"/>')
    for t in ticks:
        out.append(f'<line x1="{px(t):.1f}" y1="22" x2="{px(t):.1f}" y2="30" class="tl-axis"/>'
                   f'<text x="{px(t):.1f}" y="16" text-anchor="middle" class="tl-tick">{_esc(num(t))}</text>')
    out.append(f'<text x="{X1:.0f}" y="44" text-anchor="end" class="tl-unit">{_esc(unit)}</text>')
    y = 52.0
    for r in sorted(rows, key=lambda r: names[r["of"]][0]):
        pid = r["of"]
        i, label, mark = names[pid]
        spans = r.get("spans", [])
        levels = max([sp.get("level", 0) for sp in spans] + [0]) + 1
        has_over = any(sp.get("style") == "over" for sp in spans)
        top = y + (10 if has_over else 2)
        bar = 24.0 if levels == 1 else 10.0
        band = bar * levels + 3 * (levels - 1)
        g = [f'<g class="tl-row pm-{i + 1}" data-paper="{_esc(pid)}">',
             f'<g transform="translate(0 {top + band / 2 - 12:.1f})">{mark}</g>',
             f'<text x="18" y="{top + band / 2 - 2:.1f}" class="tl-label">{_esc(label)}</text>',
             f'<text x="18" y="{top + band / 2 + 13:.1f}" class="tl-verb">{_esc(str(r["label"]).strip())}</text>']
        for sp in spans:
            st, lv = sp.get("style", "solid"), sp.get("level", 0)
            a, b = px(float(sp["from"])), px(float(sp["to"]))
            if st == "over":
                g.append(f'<rect x="{a + 2:.1f}" y="{top - 8:.1f}" width="{b - a - 4:.1f}" height="5" rx="2" class="tl-over"/>')
                continue
            yy = top + lv * (bar + 3)
            fill = f' fill="url(#tl{uid}-{i})"' if st == "part" else ""
            g.append(f'<rect x="{a + 1:.1f}" y="{yy:.1f}" width="{b - a - 2:.1f}" height="{bar:.0f}" rx="3" class="tl-{st}"{fill}/>')
        every = r.get("every")
        if every:
            per, k = float(every["at"]), 0
            while k * per <= span + 1e-9:
                x = px(k * per)
                g.append(f'<line x1="{x:.1f}" y1="{top - 2:.1f}" x2="{x:.1f}" y2="{top + band + 2:.1f}" class="tl-every"/>')
                k += 1
        for c in cuts:
            g.append(f'<line x1="{px(c):.1f}" y1="{top - 6:.1f}" x2="{px(c):.1f}" y2="{top + band + 4:.1f}" class="tl-cut"/>')
        foot = str(r.get("note", "")).strip()
        if every and str(every.get("label", "")).strip():
            foot = (foot + " · " if foot else "") + str(every["label"]).strip()
        if foot:
            g.append(f'<text x="{X0}" y="{top + band + 20:.1f}" class="tl-note">{_esc(foot)}</text>')
        g.append("</g>")
        out += g
        y = top + band + (34 if foot else 16)
    if cuts:
        out.append(f'<text x="{X0}" y="{y + 6:.1f}" class="tl-cutl">점선 — {_esc(cut_label)}</text>')
        y += 14
    title = str(data.get("title", "")).strip()
    head = f'<p class="flow-title">{_esc(title)}</p>' if title else ""
    return (f'<div class="timeline">{head}<div class="tl-scroll">'
            f'<svg viewBox="0 0 {W} {y + 6:.0f}" role="img" aria-label="{_esc(title or "시간축")}">'
            + "".join(out) + "</svg></div>"
            f'<p class="flow-why"><em class="fig-src">{_esc(why)}</em></p></div>')
