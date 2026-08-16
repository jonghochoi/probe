"""Markdown → HTML for the PROBE corpus.

Owns the configured `MarkdownIt` and every renderer override. The math dialect
lives in `mdext.ghmath`; everything else — headings/anchors, figures, the
quote+gloss component, links, tables, code — is here.

Parser configuration, and why:

    html=False        The corpus has one intentional raw-HTML use and 170+
                      `<!-- provenance -->` comments that must not be
                      published. `ghmath.mask_source` strips the comments; the
                      one anchor is re-emitted by us.
    linkify=False     docs/style.md §4-7 forbids bare URLs in Korean prose (the
                      following particle joins the href), so auto-linking would
                      only ever fire on a bug.
    typographer=False The corpus contains typographic quotes verbatim inside
                      byte-locked English quotations; smartening would mutate
                      quoted source text.
"""

from __future__ import annotations

import html
import re

from markdown_it import MarkdownIt
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound

from .mdext import callouts, ghmath, probefence

# `Figure 3 — RGB-DF 동기 생성` → ("Figure 3", "RGB-DF 동기 생성")
_FIG_ALT = re.compile(r"^\s*(Figure\s*\d+|Fig\.?\s*\d+)\s*[—–-]\s*(.*)$", re.I)


# `## 🔬 방법론` — a leading emoji is optional in a readable rewrite, but when
# present it belongs to the heading's display, not to its slug.
_LEADING_EMOJI = re.compile(
    r"^([\U0001F300-\U0001FAFF☀-➿⬀-⯿〰〽]"
    r"[\U0001F3FB-\U0001F3FF️‍]*)\s*(.*)$"
)


def split_emoji(header_text: str) -> tuple[str, str]:
    """`🔬 방법론` → (`🔬`, `방법론`); plain text → (`""`, text)."""
    m = _LEADING_EMOJI.match(header_text.strip())
    return (m.group(1), m.group(2).strip()) if m else ("", header_text.strip())


def _slugify(text: str, index: int) -> str:
    """Deterministic ASCII id.

    Korean ids work in browsers but survive copy-paste and tooling badly, so
    headings get a numbered ASCII slug instead of a transliteration.
    """
    ascii_part = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    ascii_part = re.sub(r"-{2,}", "-", ascii_part)[:40].strip("-")
    return f"h{index}-{ascii_part}" if ascii_part else f"h{index}"


class DocRenderer:
    """Renders one document kind, collecting its TOC as it goes."""

    def __init__(self, katex, *, decisions: dict | None = None,
                 base_prefix: str = ""):
        self.katex = katex
        self.decisions = decisions or {}
        self.base_prefix = base_prefix
        self.toc: list[dict] = []
        self._heading_seq = 0
        # Readable-layer bookkeeping. Collected while rendering and checked at
        # the end of `render()`, because the checks are cross-token: a term
        # anchor with no definition, a section with no quiz.
        self.problems: list[str] = []
        self._terms_defined: dict[str, int] = {}
        self._terms_used: set[str] = set()
        self._quiz_seq = 0
        self._quiz_in_section = 0
        self._sections_seen = 0
        self._sections_without_quiz: list[str] = []
        self._current_section = ""
        self.md = self._build()

    # ── parser construction ─────────────────────────────────────────────
    def _build(self) -> MarkdownIt:
        md = MarkdownIt(
            "commonmark",
            {"html": False, "linkify": False, "typographer": False},
        )
        md.enable(["table", "strikethrough"])
        ghmath.install(md, self.katex.inline, self.katex.block)
        callouts.install(md)

        rules = md.renderer.rules
        rules["heading_open"] = self._heading_open
        rules["heading_close"] = self._heading_close
        rules["image"] = self._image
        rules["fence"] = self._fence
        rules["link_open"] = self._link_open
        rules["link_close"] = self._link_close
        rules["table_open"] = lambda *a: '<div class="table-wrap"><table>'
        rules["table_close"] = lambda *a: "</table></div>"
        rules["text"] = self._text
        return md

    # ── headings ────────────────────────────────────────────────────────
    def _heading_open(self, tokens, idx, options, env):
        token = tokens[idx]
        level = int(token.tag[1])
        raw = tokens[idx + 1].content if idx + 1 < len(tokens) else ""
        emoji, label = split_emoji(raw)

        self._heading_seq += 1
        # A readable section is an H3 (H2 is one of the four acts). Each one
        # closes the quiz tally for the section before it — R11.
        if level <= 3:
            self._close_section()
            self._current_section = (label or raw).strip() if level == 3 else ""
        anchor = _slugify(label or raw, self._heading_seq)

        # Guard against a duplicate slug colliding across a long document.
        existing = {e["id"] for e in self.toc}
        if anchor in existing:
            anchor = f"{anchor}-{self._heading_seq}"

        # H1 is the page title, rendered by the shell — not a TOC entry.
        if 2 <= level <= 3:
            self.toc.append(
                {"id": anchor, "level": level,
                 "emoji": emoji, "label": label or raw}
            )
        token.attrSet("id", anchor)
        cls = f"h-sec h{level}" + (" has-emoji" if emoji else "")
        token.attrSet("class", cls)
        self._pending_anchor = anchor
        return f'<{token.tag} id="{anchor}" class="{cls}">'

    def _heading_close(self, tokens, idx, options, env):
        anchor = getattr(self, "_pending_anchor", "")
        link = (
            f'<a class="anchor" href="#{anchor}" aria-label="이 섹션 링크">#</a>'
            if anchor else ""
        )
        return f"{link}</{tokens[idx].tag}>\n"

    # ── figures ─────────────────────────────────────────────────────────
    def _image(self, tokens, idx, options, env):
        token = tokens[idx]
        src = token.attrGet("src") or ""
        alt = token.content or ""
        m = _FIG_ALT.match(alt)
        num, caption = (m.group(1), m.group(2)) if m else ("", alt)
        # arXiv may reject hotlinks by referer; the site never mirrors the
        # images (docs/style.md §5-6 forbids it on copyright grounds).
        img = (
            f'<img src="{html.escape(src, quote=True)}" '
            f'alt="{html.escape(alt, quote=True)}" '
            f'loading="lazy" decoding="async" referrerpolicy="no-referrer">'
        )
        cap = ""
        if num or caption:
            cap = (
                '<figcaption>'
                + (f'<span class="fig-num">{html.escape(num)}</span> ' if num else "")
                + html.escape(caption)
                + "</figcaption>"
            )
        return f'<figure class="fig">{img}{cap}</figure>'

    # ── code ────────────────────────────────────────────────────────────
    def _fence(self, tokens, idx, options, env):
        token = tokens[idx]
        info = (token.info or "").strip()
        # ```math is display math, not code — reuse markdown-it's own fence
        # tokenizer rather than adding a second block rule for it.
        if info == "math":
            return self.katex.block(ghmath.normalize_tex(token.content))
        if info in probefence.FENCES:
            return self._probe_fence(info, token.content)
        code = token.content
        lexer = None
        if info:
            try:
                lexer = get_lexer_by_name(info.split()[0])
            except ClassNotFound:
                lexer = None
        if lexer is None and info in ("", "text"):
            return (
                f'<pre class="hl plain"><code>{html.escape(code)}</code></pre>'
            )
        if lexer is None:
            try:
                lexer = guess_lexer(code)
            except ClassNotFound:
                return f'<pre class="hl plain"><code>{html.escape(code)}</code></pre>'
        # No `style=` here: the token *classes* are style-independent, so one
        # highlight pass serves both themes and only the CSS differs.
        formatter = HtmlFormatter(nowrap=False, cssclass="hl")
        return highlight(code, lexer, formatter)

    # ── readable-layer fences ───────────────────────────────────────────
    def _inline(self, text: str) -> str:
        """Markdown inside a JSON payload — inline only, so a definition body
        can carry `**bold**`, `` `code` `` and `$math$` without the paragraph
        wrapper that `render()` would add."""
        return self.md.renderInline(text)

    def _probe_fence(self, info: str, content: str) -> str:
        try:
            data = probefence.parse(info, content)
            if info == "probe-term":
                tid, out = probefence.term(data, self._inline)
                if tid in self._terms_defined:
                    self.problems.append(f"term `{tid}` defined more than once")
                self._terms_defined[tid] = self._terms_defined.get(tid, 0) + 1
                return out
            if info == "probe-figure":
                return probefence.figure(data)
            if info == "probe-quiz":
                self._quiz_seq += 1
                self._quiz_in_section += 1
                return probefence.quiz(data, self._quiz_seq, self._inline)
            if info == "probe-eq":
                return probefence.equation(data, self.katex.block, self._inline)
            if info == "probe-flow":
                return probefence.flow(data, self._inline)
        except probefence.FenceError as exc:
            # Reported AND rendered: a build warning the reader never sees is
            # how a broken quiz stays broken.
            self.problems.append(str(exc))
            return probefence.error_block(str(exc))
        return ""

    def _close_section(self) -> None:
        """R11 — one quiz per section, checked as each section ends."""
        if not self._current_section:
            return
        if self._quiz_in_section != 1:
            self._sections_without_quiz.append(
                f"{self._current_section} ({self._quiz_in_section} quiz)"
            )
        self._quiz_in_section = 0

    def _check(self) -> None:
        for tid in sorted(self._terms_used - set(self._terms_defined)):
            self.problems.append(f"term anchor `term:{tid}` has no ```probe-term definition")
        for tid in sorted(set(self._terms_defined) - self._terms_used):
            self.problems.append(f"term `{tid}` is defined but never anchored")
        if self._sections_without_quiz:
            self.problems.append(
                "sections without exactly one quiz: "
                + ", ".join(self._sections_without_quiz)
            )

    # ── links ───────────────────────────────────────────────────────────
    def _link_open(self, tokens, idx, options, env):
        token = tokens[idx]
        href = token.attrGet("href") or ""
        if href.startswith("term:"):
            tid = href[len("term:"):].strip()
            self._terms_used.add(tid)
            # markdown-it emits link_open / …inline… / link_close, so the
            # matching close is rewritten by `_link_close` via this flag.
            self._term_depth = getattr(self, "_term_depth", 0) + 1
            return (
                f'<button type="button" class="tref" data-term="{html.escape(tid, quote=True)}" '
                f'aria-expanded="false">'
            )
        if href.startswith(("http://", "https://")):
            token.attrSet("target", "_blank")
            token.attrSet("rel", "noopener")
        else:
            # Intra-corpus links must land on site pages, not raw markdown.
            href = re.sub(r"^\.\./([^/]+)/analysis\.md$", r"../\1/", href)
            href = re.sub(r"^\./analysis\.md$", "#view=analysis", href)
            token.attrSet("href", href)
        attrs = " ".join(
            f'{k}="{html.escape(str(v), quote=True)}"' for k, v in token.attrs.items()
        )
        return f"<a {attrs}>"

    def _link_close(self, tokens, idx, options, env):
        if getattr(self, "_term_depth", 0):
            self._term_depth -= 1
            return '<span class="ti" aria-hidden="true">ⓘ</span></button>'
        return "</a>"

    # ── D# / P# tooltips ────────────────────────────────────────────────
    def _text(self, tokens, idx, options, env):
        text = html.escape(tokens[idx].content)
        if not self.decisions:
            return text
        return _decorate_refs(text, self.decisions)

    # ── entry point ─────────────────────────────────────────────────────
    def render(self, source: str) -> str:
        self.toc = []
        self._heading_seq = 0
        masked = ghmath.mask_source(source)
        out = self.md.render(masked)
        self._close_section()
        self._check()
        return out


_DREF_HTML = re.compile(r"(?<![A-Za-z0-9_&#])D(\d{1,2})(?![\d;])")
_DESIGNATOR_TAIL = re.compile(
    r"(?:Fig\.?|Figure|Table|Tab\.?|Eq\.?|Equation|App\.?|Appendix|Sec\.?|Section|§)\s*$",
    re.IGNORECASE,
)


def _decorate_refs(text: str, decisions: dict) -> str:
    """Wrap `D<n>` citations in an <abbr> carrying the decision's title."""
    def sub(m: re.Match[str]) -> str:
        if _DESIGNATOR_TAIL.search(text[: m.start()]):
            return m.group(0)
        n = int(m.group(1))
        entry = decisions.get(n)
        if not entry:
            return m.group(0)
        pillar, title = entry
        tip = html.escape(f"P{pillar} · {title}", quote=True)
        return f'<abbr class="dref" title="{tip}">D{n}</abbr>'
    return _DREF_HTML.sub(sub, text)


# A blockquote whose last paragraph is a parenthesized Korean gloss, or a
# parenthesized Korean paragraph immediately after one. Both shapes exist in the
# corpus; they normalize to the same component.
_BQ = re.compile(r"<blockquote>\s*(.*?)\s*</blockquote>", re.DOTALL)






# Paired themes: the code block follows the page instead of staying dark on a
# light page. Both are chosen for a warm ground — the cream `--bg` and the
# near-black `#14110f` — where a theme built for neutral grey goes muddy.
LIGHT_STYLE = "friendly"
DARK_STYLE = "nord-darker"


def pygments_css() -> str:
    """Both themes, scoped so specificity alone switches them.

    `.hl` is (0,1,0) and `[data-theme="dark"] .hl` is (0,1,1), so the dark
    rules win whenever the attribute is set and lose when it is not — no
    media query, and the manual toggle keeps working in both directions.
    """
    light = HtmlFormatter(style=LIGHT_STYLE, cssclass="hl").get_style_defs(".hl")
    dark = HtmlFormatter(style=DARK_STYLE, cssclass="hl").get_style_defs(
        '[data-theme="dark"] .hl'
    )
    # `get_style_defs` opens with a bare `pre { line-height: 125% }`, which is
    # unscoped and would silently override the 1.62 set in site.css for every
    # `<pre>` on the page — including ones Pygments never touched.
    drop = "pre { line-height: 125%; }"
    return "\n".join(
        part.replace(drop, "").strip() for part in (light, dark)
    ) + "\n"
