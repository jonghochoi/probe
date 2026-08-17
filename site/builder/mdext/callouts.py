"""GFM alert syntax → the readable layer's five callout roles (R9).

    > [!NOTE] <선택 라벨>
    > <본문>

`site/AUTHORING.md` §2-9 fixes five roles and five colors, and GitHub's own five
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


def install(md) -> None:
    md.core.ruler.push("probe_alerts", _rule)
    md.renderer.rules["blockquote_open"] = _open
    md.renderer.rules["blockquote_close"] = _close


def _rule(state) -> None:
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
        token.meta = {"role": cls, "label": m.group(2).strip() or default_label}
        # Drop the marker line from both the raw content and the already-parsed
        # children; leaving it in either place publishes `[!NOTE]` as body text.
        inline.content = rest
        _strip_first_line(inline)


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


def _open(tokens, idx, options, env):
    meta = getattr(tokens[idx], "meta", None) or {}
    role = meta.get("role")
    if not role:
        return "<blockquote>"
    label = html.escape(meta.get("label", ""), quote=True)
    return (
        f'<div class="callout {role}">'
        f'<span class="c-label">{label}</span>'
        f'<div class="c-body">'
    )


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
