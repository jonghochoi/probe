"""Structural extraction from an arXiv HTML paper.

`/readable-paper` rewrites from the paper itself, not from `analysis.md` — the
analysis is a summary and drops most of what a first-time reader needs
(preliminaries, curation detail, hardware, most figures). This module is what
turns the 400 KB LaTeXML page into the sections, figures and tables the prompt
works from.

arXiv's HTML is LaTeXML output, which is far more tractable than a PDF: every
section carries a stable `id` (`S3.SS1`), every figure carries the `id` that
`readable.md`'s `figures:` front-matter records (`S1.F1`), and every formula
keeps its TeX in `<math alttext>`. That last one matters most — the math
survives the trip as `$…$` instead of being lost to entity soup.

Stdlib only, like every other script in this repo. `html.parser` rather than a
regex sweep: the caption of a figure routinely contains nested `<math>`,
`<span>` and another `<figure>`, and matching that with regex is how you
silently truncate a caption at the first `>`.

Not every paper has an HTML edition — measured at 22/23 on a sample of this
corpus. `fetch` raises `Unavailable` in that case, and the prompt is required
to stop rather than fall back to a summary-based rewrite.
"""

from __future__ import annotations

import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from html.parser import HTMLParser

BASE = "https://arxiv.org/html"
UA = "probe-readable/1.0 (+https://github.com/jonghochoi/probe)"
TIMEOUT = 30

# `<section id="S3" class="ltx_section">` → level 1; SS → 2; SSS → 3.
_LEVEL = {"ltx_section": 1, "ltx_subsection": 2, "ltx_subsubsection": 3}
_DROP = {"script", "style", "noscript"}
_VERSIONED = re.compile(r"^(\d{4}\.\d{4,5})(v\d+)?$")


class Unavailable(RuntimeError):
    """No HTML edition for this paper (or the fetch failed)."""


@dataclass
class Section:
    id: str
    level: int
    number: str          # "3.1" — the §-anchor a figure caption cites
    title: str
    text: str = ""

    @property
    def anchor(self) -> str:
        return f"§{self.number}" if self.number else f"#{self.id}"


@dataclass
class Figure:
    id: str              # "S1.F1" — goes verbatim into readable.md front matter
    url: str             # absolute; hotlinked, never mirrored (style.md §5-6)
    number: str          # "1", "3(a)"
    caption: str
    section: str = ""    # id of the enclosing section

    @property
    def linkable(self) -> bool:
        """False for a TikZ/PGF figure — drawn as inline SVG, so there is no
        raster to hotlink. It still belongs in the list: the paper *has* that
        figure, and the prompt needs to know it exists before deciding whether
        to redraw it (R6) or leave the point unillustrated."""
        return bool(self.url)


@dataclass
class Table:
    id: str
    number: str
    caption: str
    markdown: str
    section: str = ""


@dataclass
class Paper:
    id: str              # as fetched, e.g. "2607.26055"
    version: str         # "2607.26055v1" — what `arxiv_html:` records
    title: str
    abstract: str
    sections: list[Section] = field(default_factory=list)
    figures: list[Figure] = field(default_factory=list)
    tables: list[Table] = field(default_factory=list)


# ── Fetch ───────────────────────────────────────────────────────────────────

def fetch(paper_id: str) -> tuple[str, str]:
    """Return `(html, resolved_url)`. Raises `Unavailable` if there is none."""
    m = _VERSIONED.match(paper_id.strip())
    if not m:
        raise Unavailable(f"not an arXiv id: {paper_id!r}")
    url = f"{BASE}/{m.group(0)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            final = resp.geturl()
    except urllib.error.HTTPError as exc:
        raise Unavailable(f"{url} → HTTP {exc.code}") from exc
    except OSError as exc:
        raise Unavailable(f"{url} → {exc}") from exc

    # arXiv answers 200 with a stub page for papers that have no HTML build,
    # so a status check alone is not enough to know the paper is there.
    if len(body) < 20_000 or "ltx_document" not in body:
        raise Unavailable(f"{url} → no HTML edition (stub page)")
    return body, final


def resolve_version(html: str, paper_id: str) -> str:
    """Recover the exact version from an asset path (`2607.26055v1/fig/x.png`)."""
    m = re.search(rf"{re.escape(paper_id)}(v\d+)/", html)
    return f"{paper_id}{m.group(1)}" if m else paper_id


# ── Parse ───────────────────────────────────────────────────────────────────

class _Extractor(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base = base_url.rstrip("/")
        self.sections: list[Section] = []
        self.figures: list[Figure] = []
        self.tables: list[Table] = []
        self.title = ""
        self.abstract = ""

        self._stack: list[str] = []          # open section ids
        self._by_id: dict[str, Section] = {}
        self._skip = 0                       # depth inside <math>/<script>
        self._mode = ""                      # title | caption | abstract | doctitle
        self._buf: list[str] = []
        # A figure *stack*: `ltx_flex_figure` nests panel figures inside a
        # parent that carries the real caption. A single slot would let the
        # inner `</figure>` close the outer one and lose it.
        self._figs: list[Figure] = []
        self._tbl_rows: list[list[str]] = []
        self._cell: list[str] | None = None
        self._in_table = 0

    # -- helpers ---------------------------------------------------------
    @staticmethod
    def _cls(attrs: dict) -> set[str]:
        return set((attrs.get("class") or "").split())

    @property
    def _current(self) -> Section | None:
        """The innermost OPEN section — not the last one appended.

        Those differ whenever a parent has trailing prose after its last
        subsection closes; keying off the stack puts that text back where the
        author wrote it instead of appending it to the subsection above.
        """
        return self._by_id.get(self._stack[-1]) if self._stack else None

    def _emit(self, text: str) -> None:
        if self._cell is not None:
            self._cell.append(text)
        elif self._mode:
            self._buf.append(text)
        else:
            section = self._current
            if section is not None:
                section.text += text

    def _flush(self) -> str:
        # `\s+`, not `[ \t]+`: a LaTeX title wrapped over three source lines
        # keeps those newlines, and a title with hard breaks in it is unusable
        # as a one-line label.
        out = re.sub(r"\s+", " ", "".join(self._buf)).strip()
        self._buf = []
        return out

    # -- tags ------------------------------------------------------------
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = self._cls(a)

        if tag in _DROP:
            self._skip += 1
            return
        if self._skip:
            if tag == "math":
                self._skip += 1
            return

        if tag == "math":
            # The rendered MathML is unreadable as text; the TeX source next to
            # it is exactly what we want, so emit that and skip the subtree.
            alt = a.get("alttext", "").strip()
            if alt:
                self._emit(f"${alt}$")
            self._skip += 1
            return

        if tag == "section":
            for name, level in _LEVEL.items():
                if name in cls:
                    sid = a.get("id", "") or f"_anon{len(self.sections)}"
                    section = Section(id=sid, level=level, number="", title="")
                    self._stack.append(sid)
                    self._by_id[sid] = section
                    self.sections.append(section)
                    return

        if tag in ("h1", "h2", "h3", "h4") and any(c.startswith("ltx_title") for c in cls):
            self._mode = "doctitle" if "ltx_title_document" in cls else "title"
            self._buf = []
            return

        if tag == "span" and "ltx_tag" in cls and self._mode in ("title", "caption"):
            # `<span class="ltx_tag">3.1 </span>` — the number, kept apart from
            # the title text so a caption can cite `(원문 §3.1)`.
            self._mode += "-tag"
            self._buf = []
            return

        if tag == "div" and "ltx_abstract" in cls:
            self._mode = "abstract"
            self._buf = []
            return

        if tag == "figure":
            if "ltx_table" in cls:
                self._in_table += 1
                self._tbl_rows = []
            self._figs.append(Figure(
                id=a.get("id", ""), url="", number="", caption="",
                section=self._stack[-1] if self._stack else "",
            ))
            return

        if tag == "img" and self._figs and not self._figs[-1].url:
            src = a.get("src", "")
            if src:
                self._figs[-1].url = src if src.startswith("http") else f"{self.base}/{src}"
            return

        if tag == "figcaption":
            self._mode = "caption"
            self._buf = []
            return

        if tag in ("td", "th") and self._in_table:
            self._cell = []
            return
        if tag == "tr" and self._in_table:
            self._tbl_rows.append([])
            return

        if tag in ("p", "li", "div") and not self._mode:
            self._emit("\n")

    def handle_endtag(self, tag):
        if self._skip:
            if tag in _DROP or tag == "math":
                self._skip -= 1
            return

        if tag in ("h1", "h2", "h3", "h4") and self._mode.startswith(("title", "doctitle")):
            text = self._flush()
            if self._mode.startswith("doctitle"):
                self.title = self.title or text
            elif self.sections:
                self.sections[-1].title = text
            self._mode = ""
            return

        if tag == "span" and self._mode.endswith("-tag"):
            tagtext = self._flush().strip()
            base = self._mode[: -len("-tag")]
            if base == "title" and self.sections:
                self.sections[-1].number = tagtext
            elif base == "caption" and self._figs:
                # "Figure 3:" / "Table 1:" → "3" / "1"
                m = re.search(r"([\d.]+[a-z]?)", tagtext)
                self._figs[-1].number = m.group(1) if m else tagtext
            self._mode = base
            return

        if tag == "div" and self._mode == "abstract":
            self.abstract = self._flush()
            self._mode = ""
            return

        if tag == "figcaption":
            if self._figs:
                self._figs[-1].caption = self._flush()
            self._mode = ""
            return

        if tag in ("td", "th") and self._cell is not None:
            cell = re.sub(r"\s+", " ", "".join(self._cell)).strip()
            if self._tbl_rows:
                self._tbl_rows[-1].append(cell)
            self._cell = None
            return

        if tag == "figure":
            if not self._figs:
                return
            fig = self._figs.pop()
            if self._in_table:
                self._in_table -= 1
                self.tables.append(Table(
                    id=fig.id, number=fig.number, caption=fig.caption,
                    markdown=_as_markdown(self._tbl_rows), section=fig.section,
                ))
                self._tbl_rows = []
            else:
                self.figures.append(fig)
            return

        if tag == "section" and self._stack:
            self._stack.pop()

    def handle_data(self, data):
        if not self._skip:
            self._emit(data)


def _as_markdown(rows: list[list[str]]) -> str:
    rows = [r for r in rows if any(c for c in r)]
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    head, *body = rows
    out = ["| " + " | ".join(c.replace("|", "\\|") for c in head) + " |",
           "|" + "---|" * width]
    out += ["| " + " | ".join(c.replace("|", "\\|") for c in r) + " |" for r in body]
    return "\n".join(out)


def parse(html: str, paper_id: str) -> Paper:
    version = resolve_version(html, paper_id.split("v")[0])
    # Asset srcs are already version-prefixed ("2607.26055v1/fig/x.png") and
    # resolve against /html/, not against the paper page itself.
    ex = _Extractor(BASE)
    ex.feed(html)
    for s in ex.sections:
        s.text = re.sub(r"\n{3,}", "\n\n", re.sub(r"[ \t]+", " ", s.text)).strip()
    return Paper(
        id=paper_id, version=version, title=ex.title, abstract=ex.abstract,
        sections=[s for s in ex.sections if s.title or s.text],
        figures=ex.figures, tables=ex.tables,
    )


def load(paper_id: str) -> Paper:
    html, _ = fetch(paper_id)
    return parse(html, paper_id)


if __name__ == "__main__":  # `python3 -m probe_site.arxiv 2607.26055`
    import sys

    try:
        paper = load(sys.argv[1])
    except Unavailable as exc:
        # A traceback here would read as a bug in this script; it is a fact
        # about the paper, and the caller must stop rather than fall back.
        sys.exit(f"unavailable: {exc}")
    print(f"{paper.version}  {paper.title}")
    print(f"  abstract {len(paper.abstract)} chars · "
          f"{len(paper.sections)} sections · {len(paper.figures)} figures · "
          f"{len(paper.tables)} tables\n")
    for s in paper.sections:
        print(f"  {'  ' * (s.level - 1)}{s.anchor:9} {s.title[:56]:58} {len(s.text):6} chars")
    print()
    for f in paper.figures:
        print(f"  {f.id:12} Fig {f.number:4} {f.url}")
