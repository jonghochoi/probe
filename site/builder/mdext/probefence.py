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

The only other fence language the corpus uses is `math`, so these names do not
collide with anything an author might mean literally.
"""

from __future__ import annotations

import html
import json

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
COMPARE_FENCES = ("probe-matrix",)
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
    (R4). Hoisting it to the end of the block put the definition one or two
    sentences below the word that needed it, so the reader had to find their
    way back into the sentence they left; opening it in place splits the
    paragraph exactly where they stopped reading.

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
        # A dedicated title class, never a bare `b` — R13: `display:block` on an
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

def flow(data: dict, inline_md) -> str:
    """A hand-drawn step diagram — R6's fallback for a point the paper does
    not illustrate. HTML/CSS boxes, never ASCII art.

    `why` is required and prints under the diagram. A redrawn figure competes
    with figures the authors already drew, and when it wins by accident the
    reader gets a box of our labels in place of the paper's own picture — with
    nothing on the page saying an original existed. Naming the gap is cheap;
    having to name it is the check.
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
    items = "".join(
        f'<li class="fstep"><span class="fs-label">{inline_md(str(s.get("label", "")))}</span>'
        + (f'<span class="fs-note">{inline_md(str(s["note"]))}</span>' if s.get("note") else "")
        + "</li>"
        if isinstance(s, dict)
        else f'<li class="fstep"><span class="fs-label">{inline_md(str(s))}</span></li>'
        for s in steps
    )
    title = (data.get("title") or "").strip()
    head = f'<p class="flow-title">{_esc(title)}</p>' if title else ""
    # Printed, not merely required: the reader deserves to know this box is
    # ours and what the paper had in its place.
    note = f'<p class="flow-why"><em class="fig-src">{_esc(why)}</em></p>'
    return f'<div class="flow">{head}<ol class="fsteps">{items}</ol>{note}</div>'


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


def matrix(data: dict, inline_md, heads: list[tuple[str, str, str]]) -> str:
    """The comparison track's grid — one question per row, one paper per column.

    Every other component here describes one paper. This one exists because a
    comparison that lets an axis speak about two of its three papers has
    stopped comparing: the schema requires a cell per paper per axis, so a
    thought that only fits two of them has to be reworded until it fits all
    three, or dropped. That reworking is where the comparison actually happens.

    Cells are placed by `of` rather than by position, so the author writes them
    in whatever order the axis reads best and the columns still line up.

    `heads` is `(id, label, href)` per column, in column order — the fence has
    no way to know which papers are being compared or where their rewrites
    live, and both come from the document's front matter.
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

        tds = ""
        for pid in ids:
            cell = by_id[pid]
            note = str(cell.get("note", "")).strip()
            tds += (
                "<td>"
                f'<span class="mx-v">{inline_md(str(cell["v"]))}</span>'
                + (f'<span class="mx-note">{inline_md(note)}</span>' if note else "")
                + "</td>"
            )
        rows += f'<tr><th scope="row" class="mx-k">{inline_md(key)}</th>{tds}</tr>'

    cols = "".join(
        f'<th scope="col"><a href="{_esc(href)}">{_esc(label)}</a>'
        f'<span class="mx-id">{_esc(pid)}</span></th>'
        for pid, label, href in heads
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
