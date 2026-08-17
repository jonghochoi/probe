"""GitHub-flavored KaTeX dialect support for markdown-it-py.

`site/AUTHORING.md` §3-1 fixes three accepted math forms that no standard
Markdown parser understands:

    inline   $`X`$          ← backticks INSIDE the dollars
    display  $$X$$          ← alone on a line, at column 0
    multirow ```math …```   ← a fenced block at column 0

The inline form is the hard one: a naive parser sees a backtick code span and
swallows the math. We fix that structurally rather than with regex patching, by
registering an inline rule *before* markdown-it's own `backtick` rule — the
code-span rule then never gets a chance to look at those backticks.

Four hooks, in the order they run:

    A  mask_source()      raw text, before md.render()
    B  inline rule        $`X`$   → math_inline token
    C  block rule + fence $$…$$ / ```math → math_block token
    D  normalize_tex()    inside the renderers, the single choke point

Hook A exists because GFM splits table rows on `|` *before* any inline parsing
runs, so a literal `|` inside `` $`…`$ `` inside a table row tears the cell in
half. It masks those pipes with a Private Use Area sentinel that Hook D — the
only code that ever sees a math token's content — puts back.
"""

from __future__ import annotations

import re

# U+E000, Unicode Private Use Area. Verified absent from the corpus, so it can
# never collide with authored content. Hook A puts it in, Hook D takes it out;
# no other code path touches a math token's content, so it cannot leak to HTML.
PIPE_SENTINEL = "\ue000"

# `<!-- … -->` provenance/retrieval logs. Present in most analyses, invisible on
# github.com but plainly readable in view-source, so they are stripped from the
# source rather than merely hidden with CSS.
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)

# An inline math span, used only by Hook A's table-row scan. The real tokenizing
# is Hook B's; this just needs to find the spans' extents on one line.
_INLINE_SPAN = re.compile(r"\$(`+)(.+?)\1\$")


def _mask_row_pipes(line: str) -> str:
    """Replace `|` inside inline math with the sentinel, on a table-row line."""
    return _INLINE_SPAN.sub(
        lambda m: "$" + m.group(1) + m.group(2).replace("|", PIPE_SENTINEL)
        + m.group(1) + "$",
        line,
    )




def mask_source(text: str) -> str:
    """Hook A — the raw-source pre-pass. Run once before `md.render()`."""
    text = _HTML_COMMENT.sub("", text)
    lines = text.split("\n")
    for i, line in enumerate(lines):
        # Only table rows are at risk; a `|` anywhere else is just a character.
        if line.lstrip().startswith("|") and "$" in line:
            lines[i] = _mask_row_pipes(line)
    return "\n".join(lines)


# ── Hook D — the single normalization choke point ────────────────────────────

# Sanctioned macro substitutions. AUTHORING §3-1 is the rule; extend this list
# only by editing it. Every *other* unsupported macro is deliberately left
# broken so the render failure stays visible rather than being papered over.
MACRO_SUBS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\\bm\{"), r"\\mathbf{"),
    (re.compile(r"\\mathds\{"), r"\\mathbb{"),
    (re.compile(r"\\operatorname\*?"), r"\\mathrm"),
)


def normalize_tex(tex: str) -> str:
    """Hook D — undo Hook A's masking, then apply the sanctioned macro subs.

    Never writes to the source file — the corpus is what the author wrote,
    and normalization happens on the way to the page.
    """
    tex = tex.replace(PIPE_SENTINEL, "|")
    for pattern, replacement in MACRO_SUBS:
        tex = pattern.sub(replacement, tex)
    return tex


# ── Hook B — the inline rule ─────────────────────────────────────────────────


def _inline_math(state, silent: bool) -> bool:
    """Match `$` + backtick-run + TeX + same backtick-run + `$`."""
    src, start, maximum = state.src, state.pos, state.posMax
    if src[start] != "$" or start + 1 >= maximum or src[start + 1] != "`":
        return False

    run_start = start + 1
    pos = run_start
    while pos < maximum and src[pos] == "`":
        pos += 1
    ticks = pos - run_start
    marker = "`" * ticks
    content_start = pos

    search = content_start
    while True:
        idx = src.find(marker, search)
        if idx < 0 or idx >= maximum:
            return False
        end = idx + ticks
        # A longer backtick run is not our closer; skip past it.
        if end < maximum and src[end] == "`":
            while end < maximum and src[end] == "`":
                end += 1
            search = end
            continue
        if end < maximum and src[end] == "$":
            break
        search = end
        if search >= maximum:
            return False

    content = src[content_start:idx]
    if not content.strip():
        return False
    if not silent:
        token = state.push("math_inline", "math", 0)
        token.markup = "$`"
        token.content = content
    state.pos = end + 1
    return True


# ── Hook C — the block rule ($$…$$ at column 0) ──────────────────────────────


def _block_math(state, start_line: int, end_line: int, silent: bool) -> bool:
    """Match a line that is exactly `$$…$$`.

    AUTHORING §3-1 requires column 0; an indented one is a corpus bug, and
    rendering it as written keeps that bug visible rather than quietly
    compensating for it.
    """
    if state.sCount[start_line] != 0:
        return False
    begin = state.bMarks[start_line] + state.tShift[start_line]
    stop = state.eMarks[start_line]
    line = state.src[begin:stop].rstrip()
    if len(line) < 5 or not line.startswith("$$") or not line.endswith("$$"):
        return False
    content = line[2:-2]
    if not content.strip():
        return False
    if silent:
        return True

    token = state.push("math_block", "math", 0)
    token.block = True
    token.markup = "$$"
    token.content = content
    token.map = [start_line, start_line + 1]
    state.line = start_line + 1
    return True


def install(md, render_inline, render_block) -> None:
    """Register hooks B and C, and bind the two math renderers.

    `render_inline(tex) -> html` and `render_block(tex) -> html` are supplied by
    the caller (KaTeX server-side, or a client-side placeholder emitter) so this
    module stays free of any rendering policy.
    """
    # Before `backticks`: the code-span rule never sees our inner backticks.
    # markdown-it's default inline order is text → newline → escape →
    # backticks → …, so this also lands *after* `escape`, which is why a
    # literal `\$` in prose is already a text token and never reaches us.
    md.inline.ruler.before("backticks", "gh_math_inline", _inline_math)
    # Before `fence`: a `$$…$$` line is claimed before any other block rule.
    md.block.ruler.before(
        "fence", "gh_math_block", _block_math, {"alt": ["paragraph", "blockquote", "list"]}
    )

    def _inline_renderer(tokens, idx, options, env):
        return render_inline(normalize_tex(tokens[idx].content))

    def _block_renderer(tokens, idx, options, env):
        return render_block(normalize_tex(tokens[idx].content))

    # Assigned directly rather than via `add_render_rule`, which binds the
    # function as a method and would pass an extra `self`.
    md.renderer.rules["math_inline"] = _inline_renderer
    md.renderer.rules["math_block"] = _block_renderer
