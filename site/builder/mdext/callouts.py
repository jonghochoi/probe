"""GFM alert syntax → the rewrite layer's five callout roles (R9).

    > [!NOTE] <선택 라벨>
    > <본문>

`analysis/AUTHORING.md` §2-9 fixes five roles and five colors, and GitHub's own five
alert types already carry exactly those colors — note/blue, tip/green,
important/purple, warning/amber, caution/red. Reusing them means the same
source renders as a recognisable callout on github.com as well, with no
private syntax to learn.

The label after the marker is optional; without one the role's own name is
used, which is what makes R9 mechanical rather than a matter of taste. GitHub
ignores trailing text on the marker line, so a labelled callout degrades there
to a plain blockquote rather than breaking.
"""

from __future__ import annotations

import html
import re

# GFM type → (css role, default Korean label). The mapping is by *meaning*,
# and the colors line up because both palettes were chosen for the same
# semantics.
ROLES = {
    "note": ("co-key", "작동 원리"),
    "tip": ("co-win", "확인된 이득"),
    "warning": ("co-warn", "한계·비용"),
    "caution": ("co-ten", "우리와 충돌"),
    "important": ("co-ctx", "논문 밖 맥락"),
}
MARKER = re.compile(r"^\[!(\w+)\][ \t]*(.*)$")

# A callout is an aside: one point, pulled out of the flow so the eye catches
# it. Past this it stops being an aside and becomes a section wearing a border
# — the reader loses the paragraph it interrupted, and the pale wash it is set
# on runs long enough to read as a second column. Measured on the body's
# printed characters, so emphasis markers and TeX macros do not count against
# an author who wrote a short sentence with a formula in it. §2-9.
BODY_MAX = 400

_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_MATH = re.compile(r"\$`([^`]*)`\$")
_TEX_NOISE = re.compile(r"\\[A-Za-z]+|[{}\\]")
_MARKUP = re.compile(r"[*_`~]")
_WS = re.compile(r"\s+")


def body_length(text: str) -> int:
    """Characters a reader sees — markup stripped, math counted as it prints."""
    text = _LINK.sub(r"\1", text)
    text = _MATH.sub(lambda m: _TEX_NOISE.sub("", m.group(1)), text)
    return len(_WS.sub("", _MARKUP.sub("", text)))


def install(md, inline_md=None, report=None) -> None:
    """`inline_md` renders the label. Without it the label is escaped, which
    publishes any math or emphasis in a callout title as its own source.
    `report` takes one message per over-long callout body."""
    md.core.ruler.push("probe_alerts", lambda state: _rule(state, report))
    md.renderer.rules["blockquote_open"] = _opener(inline_md)
    md.renderer.rules["blockquote_close"] = _close


def _rule(state, report=None) -> None:
    tokens = state.tokens
    for i, token in enumerate(tokens):
        if token.type != "blockquote_open" or i + 2 >= len(tokens):
            continue
        if tokens[i + 1].type != "paragraph_open" or tokens[i + 2].type != "inline":
            continue

        inline = tokens[i + 2]
        head, _, rest = inline.content.partition("\n")
        m = MARKER.match(head.strip())
        if not m:
            continue
        role = ROLES.get(m.group(1).lower())
        if not role:
            continue

        cls, default_label = role
        label = m.group(2).strip() or default_label
        token.meta = {"role": cls, "label": label}
        # Drop the marker line from both the raw content and the already-parsed
        # children; leaving it in either place publishes `[!NOTE]` as body text.
        inline.content = rest
        _strip_first_line(inline)
        if report is not None:
            length = body_length(_body_text(tokens, i))
            if length > BODY_MAX:
                report(
                    f"callout `{label}` runs {length} chars — a callout holds one "
                    f"point in at most {BODY_MAX} (R9); move the rest into body "
                    f"prose or a `::: details` block"
                )


def _body_text(tokens, open_idx: int) -> str:
    """Every inline run inside one callout, marker line already removed."""
    depth = 0
    parts = []
    for token in tokens[open_idx + 1:]:
        if token.type == "blockquote_open":
            depth += 1
        elif token.type == "blockquote_close":
            if depth == 0:
                break
            depth -= 1
        elif token.type == "inline":
            parts.append(token.content)
    return "\n".join(parts)


def _strip_first_line(inline) -> None:
    children = inline.children or []
    if not children:
        return
    if children[0].type == "text":
        _, sep, rest = children[0].content.partition("\n")
        children[0].content = rest if sep else ""
    # A softbreak now leads the run, which would open the body with a blank
    # line; the marker line and its break are one unit.
    while children and children[0].type in ("softbreak", "hardbreak"):
        children.pop(0)
    while children and children[0].type == "text" and not children[0].content:
        children.pop(0)
    inline.children = children


def _opener(inline_md):
    def _open(tokens, idx, options, env):
        meta = getattr(tokens[idx], "meta", None) or {}
        role = meta.get("role")
        if not role:
            return "<blockquote>"
        raw = meta.get("label", "")
        label = inline_md(raw) if inline_md else html.escape(raw, quote=True)
        return (
            f'<div class="callout {role}">'
            f'<span class="c-label">{label}</span>'
            f'<div class="c-body">'
        )
    return _open


def _close(tokens, idx, options, env):
    # The matching open is the nearest unclosed blockquote_open.
    depth = 0
    for token in reversed(tokens[:idx]):
        if token.type == "blockquote_close":
            depth += 1
        elif token.type == "blockquote_open":
            if depth == 0:
                meta = getattr(token, "meta", None) or {}
                return "</div></div>" if meta.get("role") else "</blockquote>"
            depth -= 1
    return "</blockquote>"
