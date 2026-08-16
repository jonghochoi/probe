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
from mdit_py_plugins.container import container_plugin
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


def _render_details(self, tokens, idx, options, env) -> str:
    token = tokens[idx]
    if token.nesting != 1:
        return "</div></details>\n"
    summary = token.info.strip()[len("details"):].strip() or "자세히"
    return (
        f'<details class="fold"><summary>{html.escape(summary)}</summary>'
        f'<div class="fold-body">'
    )


# `## 1 무엇이 문제인가` → ("1", "무엇이 문제인가"). The number is the act's rail
# marker; without one the renderer falls back to counting acts as they appear.
_ACT_NUM = re.compile(r"^\s*(\d{1,2})[.)]?\s+(.*)$")


def _split_act(text: str) -> tuple[str, str]:
    m = _ACT_NUM.match(text.strip())
    return (m.group(1), m.group(2).strip()) if m else ("", text.strip())


def _split_keyword_line(text: str) -> tuple[str, str]:
    """`제목 | Keyword · Keyword` → (제목, keywords).

    §5-8 R2 has always asked for a line of English keywords under each section
    title. Written as the paragraph after the heading it renders as body text
    and never reaches the table of contents, so it reads as a stray sentence
    the section opens with. Carried *in* the heading it is part of the section's
    identity and the TOC can show it.
    """
    ko, sep, en = text.partition("|")
    return (ko.strip(), en.strip()) if sep else (text.strip(), "")


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
                 base_prefix: str = "", lead_html: str = ""):
        self.katex = katex
        self.decisions = decisions or {}
        self.base_prefix = base_prefix
        # Emitted immediately after the body H1 closes. The one-paragraph
        # summary is the first thing a reader wants and the front matter
        # already carries it, so the page prints it instead of reserving it
        # for the landing card and opening the article on paragraph one.
        self.lead_html = lead_html
        self.toc: list[dict] = []
        self._heading_seq = 0
        self._acts_seen = 0
        self._pending_close = ""
        self._context_kinds: set[str] = set()
        self._sections_without_keywords: list[str] = []
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
        # `::: details <summary>` → a real <details>. R3 wants configs and
        # derivations collapsed, and the parser runs with `html=False`, so a
        # hand-written `<details>` would be escaped into visible angle
        # brackets. A container keeps the body as markdown (tables included),
        # which a JSON fence could not.
        container_plugin(md, "details", render=_render_details)
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
        """Three heading levels, three different components.

        The markdown spine is unchanged — `#` thesis, `##` act, `###` section —
        but the levels no longer map onto `<h1>/<h2>/<h3>`. An act is a rail
        marker, not a heading: it names which of the four questions we are
        answering and carries no content of its own, so it renders as a divider
        band and the section under it gets the real `<h2>`. Rendering the act as
        a heading is what made every section read as a subordinate `<h3>` — a
        section title one notch above body text, which is why the page scanned
        flat no matter how good the prose was.
        """
        token = tokens[idx]
        level = int(token.tag[1])
        inline = tokens[idx + 1] if idx + 1 < len(tokens) else None
        raw = inline.content if inline else ""
        emoji, label = split_emoji(raw)

        self._heading_seq += 1
        # A readable section is an H3 (H2 is one of the four acts). Each one
        # closes the quiz tally for the section before it — R11.
        if level <= 3:
            self._close_section()
            # The keyword line is part of the heading now, so strip it before
            # the name is used in a warning — "제목 | Keywords (0 quiz)" reads
            # like the pipe is part of the problem.
            self._current_section = (
                _split_keyword_line(label or raw)[0] if level == 3 else ""
            )

        # Every branch below emits its own markup, so the inline token must not
        # also render: markdown-it would print the heading text a second time
        # between our open and close.
        def take_inline() -> None:
            if inline is not None:
                inline.children = []
                inline.content = ""

        if level == 1:
            self._pending_close = "</h1>\n" + self.lead_html
            return '<h1 class="thesis">'

        if level == 2:
            number, act = _split_act(label or raw)
            self._acts_seen += 1
            self.toc.append({"kind": "act", "n": number or str(self._acts_seen),
                             "label": act})
            take_inline()
            self._pending_close = ""
            return (
                '<div class="pdiv">'
                f'<span class="pn">{html.escape(number or str(self._acts_seen))}</span>'
                f'<span class="pt">{self._inline(act)}</span>'
                "</div>\n"
            )

        ko, en = _split_keyword_line(label or raw)
        anchor = _slugify(ko, self._heading_seq)
        existing = {e.get("id") for e in self.toc}
        if anchor in existing:
            anchor = f"{anchor}-{self._heading_seq}"

        if level == 3:
            if not en:
                self._sections_without_keywords.append(ko)
            self.toc.append({"kind": "sec", "id": anchor, "label": ko, "en": en,
                             "emoji": emoji})
            take_inline()
            self._pending_close = (
                (f'<span class="en">{html.escape(en)}</span>' if en else "")
                + f'<a class="anchor" href="#{anchor}" aria-label="이 섹션 링크">#</a>'
                + "</h2>\n"
            )
            return f'<h2 class="h-sec sec" id="{anchor}">{self._inline(ko)}'

        # H4+ stays an ordinary heading — a sub-point inside a section.
        take_inline()
        self._pending_close = f"</{token.tag}>\n"
        return f'<{token.tag} class="h-sub" id="{anchor}">{self._inline(ko)}'

    def _heading_close(self, tokens, idx, options, env):
        return getattr(self, "_pending_close", f"</{tokens[idx].tag}>\n")

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
    def inline(self, text: str) -> str:
        """Markdown inline-only — no paragraph wrapper.

        Used for fence payloads (a term body carrying `**bold**` and math) and
        for the front-matter lines the page prints above the article.
        """
        return self.md.renderInline(ghmath.mask_source(text))

    def _inline(self, text: str) -> str:
        # Fence payloads arrive from a source that `render()` already masked.
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
            if info == "probe-lineage":
                self._context_kinds.add("계보")
                return probefence.lineage(data, self._inline)
            if info == "probe-scale":
                self._context_kinds.add("숫자의 지형")
                return probefence.scale(data, self._inline)
            if info == "probe-split":
                self._context_kinds.add("대조")
                return probefence.split(data, self._inline)
            if info == "probe-parts":
                self._context_kinds.add("대조")
                return probefence.parts(data, self._inline)
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
        if self._sections_without_keywords:
            self.problems.append(
                "sections with no `| English keyword` line in the heading (R2): "
                + ", ".join(self._sections_without_keywords)
            )
        # R5 names five kinds of planted context; three of them now have a
        # component each. Warn when a rewrite uses none of them — that is the
        # exact failure this build was flat before: the rule was satisfied in
        # prose and nothing on the page showed it.
        if not self._context_kinds:
            self.problems.append(
                "no planted-context component (R5): expected at least one of "
                "```probe-lineage (계보) / ```probe-scale (숫자의 지형) / "
                "```probe-split · ```probe-parts (대조)"
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

    def _check_stray_emphasis(self, out: str) -> None:
        """`**bold**` that never became bold.

        CommonMark will not close a `**` run that sits between a punctuation
        mark and a letter, which in Korean prose is the extremely ordinary
        shape `**…(괄호)**로` — a closing paren, then a particle. The emphasis
        silently publishes as literal asterisks, and because the sentence still
        reads fine in the source nobody catches it. Cheap to detect after the
        fact, so detect it after the fact.
        """
        # Code spans are exempt — a document *about* this trap quotes the
        # broken form on purpose — and a match may not cross a tag boundary,
        # or two unrelated `**` inside adjacent code spans pair up.
        prose = re.sub(r"<code\b[^>]*>.*?</code>", "", out, flags=re.S)
        for stray in set(re.findall(r"\*\*[^*<>\n]{1,60}\*\*", prose)):
            self.problems.append(
                f"unrendered emphasis published as literal asterisks: {stray!r} "
                f"— a `**` run cannot close between punctuation and a letter; "
                f"move the closing marker off the parenthesis"
            )

    # ── entry point ─────────────────────────────────────────────────────
    def render(self, source: str) -> str:
        self.toc = []
        self._heading_seq = 0
        self._acts_seen = 0
        self._context_kinds = set()
        self._sections_without_keywords = []
        masked = ghmath.mask_source(source)
        out = self.md.render(masked)
        self._close_section()
        self._check()
        self._check_stray_emphasis(self.lead_html + out)
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
