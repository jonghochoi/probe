"""The ` ```probe-* ` fences of the readable layer.

`readable.md` is markdown with JSON where structure is needed: an inline term
definition, a cited figure, a per-section quiz. JSON because the nesting
(quiz options, answer, explanation) parses strictly with the stdlib and fails
loudly when malformed — a silently half-parsed quiz would publish with no
right answer and nobody would notice.

Four of these fences exist because §5-8 R5 asks for five kinds of planted
context and only two of them had anywhere to go. 계보 became a paragraph of
prose, 숫자의 지형 became a sentence with numbers in it, and 대조 became two
adjacent paragraphs the reader had to hold side by side themselves. The rule
was already right; the page had no component to satisfy it with, so every one
of them flattened into undifferentiated body text. `probe-lineage`,
`probe-scale`, `probe-split` and `probe-parts` are those shapes made real.

Rendering these is not optional decoration. Without it the fences fall through
to the code highlighter and a term definition is published as a block of JSON,
so `.claude/prompts/readable.txt` and this module are one contract: the prompt
tells the agent the build validates its fences, and this is where that is true.

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

    Rendered collapsed, directly under the paragraph that introduced the term
    (R4): background belongs where the reader hits the word, not in a glossary
    they would have to leave the sentence to reach.
    """
    tid = data.get("id", "").strip()
    if not tid:
        raise FenceError("probe-term: missing `id`")
    title = data.get("title", "").strip()
    body = data.get("body", "").strip()
    if not body:
        raise FenceError(f"probe-term[{tid}]: missing `body`")

    return tid, (
        f'<div class="tdef" id="term-{_esc(tid)}" hidden>'
        # A dedicated title class, never a bare `b` — R13: `display:block` on an
        # inline tag also catches every `<b>` in the body and breaks the line at
        # each emphasis.
        f'<span class="th">{_esc(title) or _esc(tid)}</span>'
        f'<span class="tbody">{inline_md(body)}</span>'
        f"</div>"
    )



# ── ```probe-figure ─────────────────────────────────────────────────────────

def figure(data: dict) -> str:
    url = data.get("url", "").strip()
    if not url:
        raise FenceError(f"probe-figure[{data.get('id', '?')}]: missing `url`")
    if not url.startswith(("http://", "https://")):
        # Mirroring a paper's figure into the repo is a copyright problem
        # (style.md §5-6); a relative URL here means someone did.
        raise FenceError(
            f"probe-figure[{data.get('id', '?')}]: `url` must be absolute — "
            f"figures are hotlinked, never mirrored"
        )
    caption = data.get("caption", "").strip()
    source = data.get("source", "").strip()
    cap = ""
    if caption or source:
        cap = (
            "<figcaption>"
            + _esc(caption)
            + (f' <span class="fig-src">({_esc(source)})</span>' if source else "")
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

    name = f"quiz{index}"
    choices = "".join(
        f'<label class="qopt"><input type="radio" name="{name}" '
        f'value="{i}" data-correct="{"1" if i == answer else "0"}">'
        f"<span>{inline_md(str(opt).strip())}</span></label>"
        for i, opt in enumerate(options)
    )
    return (
        f'<section class="quiz" data-quiz>'
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

    rows = ""
    for entry in symbols:
        if not isinstance(entry, dict) or not entry.get("sym"):
            raise FenceError(
                f"probe-eq[{tex[:32]}…]: each symbol needs at least `sym` "
                f"(got {entry!r})"
            )
        rows += (
            "<tr>"
            # The corpus math dialect is GitHub's `$`X`$`, so the symbol cell
            # goes through the same inline rule as body math rather than a
            # second, ambiguous plain-`$` one.
            f'<td class="eqsym">{inline_md("$`" + str(entry["sym"]) + "`$")}</td>'
            f'<td>{_esc(entry.get("name", ""))}</td>'
            f'<td>{inline_md(str(entry.get("note", "")))}</td>'
            "</tr>"
        )
    table = (
        '<div class="table-wrap"><table><thead><tr>'
        "<th>기호</th><th>이름</th><th>설명</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></div>"
        if rows else ""
    )
    return (
        '<div class="eqblock">'
        f'<p class="eqread">읽으면 — <em>{_esc(read)}</em></p>'
        f"{katex_block(tex)}{table}</div>"
    )


# ── ```probe-flow ───────────────────────────────────────────────────────────

def flow(data: dict, inline_md) -> str:
    """A hand-drawn step diagram — R6's fallback for a point the paper does
    not illustrate. HTML/CSS boxes, never ASCII art."""
    steps = data.get("steps")
    if not isinstance(steps, list) or not steps:
        raise FenceError("probe-flow: `steps` must be a non-empty list")
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
    return f'<div class="flow">{head}<ol class="fsteps">{items}</ol></div>'


# ── ```probe-lineage ────────────────────────────────────────────────────────

def lineage(data: dict, inline_md) -> str:
    """R5's 계보 — the papers this one stands on, in date order.

    A dated rail rather than a paragraph naming three prior works: the reader's
    question is *what moved between them*, and a list answers that in one
    downward scan. Exactly one entry may be `current` — the paper being read —
    which is what turns a bibliography into a position.
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
            if link else ""
        )
        rows += (
            f'<li class="ln-item{" cur" if item.get("current") else ""}">'
            f'<span class="ln-when">{_esc(item.get("when", ""))}</span>'
            f'<span class="ln-what">{inline_md(str(item["what"]))}</span>'
            + (f'<span class="ln-note">{inline_md(note)}{tail}</span>' if note else "")
            + "</li>"
        )
    title = str(data.get("title", "")).strip()
    head = f'<p class="ln-title">{_esc(title)}</p>' if title else ""
    return f'<div class="lineage">{head}<ol class="ln-list">{rows}</ol></div>'


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
    head = f'<p class="sc-title">{_esc(title)}</p>' if title else ""
    return f'<div class="scale">{head}{rows}</div>'


# ── ```probe-split ──────────────────────────────────────────────────────────

_SPLIT_TONES = {"cold", "warm", "plain"}


def split(data: dict, inline_md) -> str:
    """R5's 대조 — two or three things the paper holds apart, held apart here.

    The paper's contrast is structural (this channel is slow, that one is
    fast); rendering it as consecutive paragraphs asks the reader to rebuild
    the parallel from prose. Cards put the parallel in the layout.
    """
    cards = data.get("cards")
    if not isinstance(cards, list) or not 2 <= len(cards) <= 3:
        raise FenceError(
            f"probe-split: `cards` must be a list of 2–3, got "
            f"{len(cards) if isinstance(cards, list) else type(cards).__name__}"
        )
    out = ""
    for card in cards:
        if not isinstance(card, dict) or not card.get("title") or not card.get("body"):
            raise FenceError(f"probe-split: each card needs `title` and `body` (got {card!r})")
        tone = str(card.get("tone", "plain")).strip() or "plain"
        if tone not in _SPLIT_TONES:
            raise FenceError(
                f"probe-split[{card['title']}]: `tone` must be one of "
                f"{', '.join(sorted(_SPLIT_TONES))} — got {tone!r}"
            )
        tag = str(card.get("tag", "")).strip()
        note = str(card.get("note", "")).strip()
        out += (
            f'<div class="sp-card sp-{_esc(tone)}">'
            f'<p class="sp-head">{inline_md(str(card["title"]))}'
            + (f'<span class="sp-tag">{_esc(tag)}</span>' if tag else "")
            + "</p>"
            f'<div class="sp-body">{inline_md(str(card["body"]))}</div>'
            + (f'<p class="sp-note">{inline_md(note)}</p>' if note else "")
            + "</div>"
        )
    return f'<div class="split">{out}</div>'


# ── ```probe-parts ──────────────────────────────────────────────────────────

_PART_TONES = {"settled", "partial", "open"}


def parts(data: dict, inline_md) -> str:
    """One object decomposed into named regions — R5's 대조 in its other shape.

    A schedule split into front/interior/tail, a loss into its terms, a
    pipeline into its stages. The `label` is set in mono because it is the
    paper's own name for the region, and `range` carries the math that bounds
    it. `tone` says whether the region is pinned, in transition, or free.
    """
    rows_in = data.get("rows")
    if not isinstance(rows_in, list) or not rows_in:
        raise FenceError("probe-parts: `rows` must be a non-empty list")
    out = ""
    for row in rows_in:
        if not isinstance(row, dict) or not row.get("label") or not row.get("body"):
            raise FenceError(f"probe-parts: each row needs `label` and `body` (got {row!r})")
        tone = str(row.get("tone", "open")).strip() or "open"
        if tone not in _PART_TONES:
            raise FenceError(
                f"probe-parts[{row['label']}]: `tone` must be one of "
                f"{', '.join(sorted(_PART_TONES))} — got {tone!r}"
            )
        rng = str(row.get("range", "")).strip()
        out += (
            f'<div class="pt-row pt-{_esc(tone)}">'
            f'<div class="pt-label"><code>{_esc(row["label"])}</code>'
            + (f'<span class="pt-range">{inline_md(rng)}</span>' if rng else "")
            + "</div>"
            f'<div class="pt-body">{inline_md(str(row["body"]))}</div>'
            "</div>"
        )
    title = str(data.get("title", "")).strip()
    head = f'<p class="pt-title">{_esc(title)}</p>' if title else ""
    return f'<div class="parts">{head}{out}</div>'


def error_block(message: str) -> str:
    """A visible failure. A dropped fence would leave a hole nobody notices."""
    return f'<div class="fence-error">⚠️ {_esc(message)}</div>'
