"""The three ` ```probe-* ` fences of the readable layer.

`readable.md` is markdown with JSON where structure is needed: an inline term
definition, a cited figure, a per-section quiz. JSON because the nesting
(quiz options, answer, explanation) parses strictly with the stdlib and fails
loudly when malformed — a silently half-parsed quiz would publish with no
right answer and nobody would notice.

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

FENCES = ("probe-term", "probe-figure", "probe-quiz", "probe-eq", "probe-flow")


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


def error_block(message: str) -> str:
    """A visible failure. A dropped fence would leave a hole nobody notices."""
    return f'<div class="fence-error">⚠️ {_esc(message)}</div>'
