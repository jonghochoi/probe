"""The LaTeX source arXiv serves, read as a `Paper` when there is no HTML edition.

arXiv builds its HTML edition by running LaTeXML over the source the authors
submitted, and that build does not always succeed — a custom document class
is the usual cause. The source itself is still the paper's full text: the
same sections, figures, tables and math the HTML would have carried. This
module reads it into the same `Paper` shape `builder.arxiv` produces, so
`load`, `--grep`, `--section`, `--tables` and `--bib` behave the same on
either edition, and the caller tells them apart by `Paper.source`.

What the source cannot give is a figure to hotlink: its image files exist
only inside the archive, and a rewrite never mirrors one (AUTHORING R6). Every
figure read here is therefore unlinkable — `url` is empty — and its `id` is
the figure's own `\\label`, or `F<n>` when it has none.

The archive is downloaded data. It is read in memory — only the `.tex`,
`.bib` and `.bbl` members, never extracted to disk, never executed — so a
member path cannot land anywhere. A PDF-only submission has no source, and
raises `Unavailable` like a paper with no HTML edition.

Stdlib only, for the same reason as `builder.arxiv`. The LaTeX handling is a
reading aid, not a renderer: sectioning, floats, citations, references,
zero-argument macros and the common text commands are resolved; any other
command stays in the text as written, which is still legible to a reader
checking a number.
"""

from __future__ import annotations

import gzip
import io
import posixpath
import re
import tarfile
import urllib.error
import urllib.request

from builder.arxiv import (
    TIMEOUT, UA, Figure, Paper, Section, Table, Unavailable, _BIB_ID, _VERSIONED,
)

SRC_BASE = "https://arxiv.org/e-print"
ABS_BASE = "https://arxiv.org/abs"

# `.cls` / `.sty` are read for their zero-argument macros only — a house
# class often defines the words the body is written with.
_TEXT_MEMBER = (".tex", ".bib", ".bbl", ".cls", ".sty")
_MAX_INPUT_DEPTH = 8


# ── Fetch ───────────────────────────────────────────────────────────────────

def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        raise Unavailable(f"{url} → HTTP {exc.code}") from exc
    except OSError as exc:
        raise Unavailable(f"{url} → {exc}") from exc


def latest_version(paper_id: str) -> str:
    """`<id>v<n>` for the newest version the abstract page's history lists."""
    page = _get(f"{ABS_BASE}/{paper_id}").decode("utf-8", errors="replace")
    found = [int(n) for n in re.findall(r"\[v(\d+)\]", page)]
    if not found:
        raise Unavailable(f"{ABS_BASE}/{paper_id} → no version history on the page")
    return f"{paper_id}v{max(found)}"


def fetch_source(paper_id: str) -> tuple[str, dict[str, str]]:
    """Return `(version, files)` — every `.tex` / `.bib` / `.bbl` member by path.

    Raises `Unavailable` for a PDF-only submission or a failed fetch.
    """
    m = _VERSIONED.match(paper_id.strip())
    if not m:
        raise Unavailable(f"not an arXiv id: {paper_id!r}")
    version = m.group(0) if m.group(2) else latest_version(m.group(1))
    url = f"{SRC_BASE}/{version}"
    raw = _get(url)
    if raw.startswith(b"%PDF"):
        raise Unavailable(f"{url} → PDF-only submission, no LaTeX source")
    try:
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:*") as tar:
            files = {}
            for member in tar.getmembers():
                if member.isfile() and member.name.lower().endswith(_TEXT_MEMBER):
                    data = tar.extractfile(member)
                    if data is not None:
                        name = posixpath.normpath(member.name.lstrip("/"))
                        files[name] = data.read().decode("utf-8", errors="replace")
    except tarfile.TarError:
        # A single-file submission is one gzipped `.tex`, not an archive.
        try:
            text = gzip.decompress(raw).decode("utf-8", errors="replace")
        except OSError:
            text = raw.decode("utf-8", errors="replace")
        if text.startswith("%PDF"):
            raise Unavailable(f"{url} → PDF-only submission, no LaTeX source")
        files = {"main.tex": text}
    if not any(n.endswith(".tex") for n in files):
        raise Unavailable(f"{url} → no .tex file in the source")
    return version, files


# ── Brace-aware helpers ─────────────────────────────────────────────────────

def _group(text: str, start: int) -> tuple[str, int]:
    """The `{…}` group opening at or after `start` (whitespace skipped):
    `(inner, index after the closing brace)`. A missing group is `("", start)`."""
    i = start
    while i < len(text) and text[i] in " \t\n":
        i += 1
    if i >= len(text) or text[i] != "{":
        return "", start
    depth = 0
    for j in range(i, len(text)):
        c = text[j]
        if c == "\\":
            continue
        if c == "{" and (j == 0 or text[j - 1] != "\\"):
            depth += 1
        elif c == "}" and text[j - 1] != "\\":
            depth -= 1
            if depth == 0:
                return text[i + 1:j], j + 1
    return text[i + 1:], len(text)


def _optional(text: str, start: int) -> int:
    """Skip one `[…]` optional argument at `start`, if present."""
    i = start
    while i < len(text) and text[i] in " \t":
        i += 1
    if i < len(text) and text[i] == "[":
        depth = 0
        for j in range(i, len(text)):
            if text[j] == "[":
                depth += 1
            elif text[j] == "]":
                depth -= 1
                if depth == 0:
                    return j + 1
    return start


def _command_arg(text: str, name: str) -> str:
    """The first argument of the first `\\name{…}` in `text`, or ""."""
    m = re.search(rf"\\{name}\*?\s*", text)
    if not m:
        return ""
    return _group(text, _optional(text, m.end()))[0]


def _strip_comments(text: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", text)


# ── Assemble ────────────────────────────────────────────────────────────────

def _resolve(files: dict[str, str], base: str, name: str) -> str | None:
    name = name.strip()
    for cand in (name, name + ".tex"):
        for path in (posixpath.normpath(posixpath.join(base, cand)),
                     posixpath.normpath(cand)):
            if path in files:
                return path
    return None


def _root(files: dict[str, str]) -> str:
    roots = [n for n, t in files.items()
             if n.endswith(".tex") and re.search(r"^\s*\\documentclass",
                                                 _strip_comments(t), re.M)]
    if not roots:
        return min((n for n in files if n.endswith(".tex")), key=len)
    # A source with several roots (a supplement beside the paper) keeps the
    # one nearest the archive root, then the shortest name.
    return min(roots, key=lambda n: (n.count("/"), len(n), n))


def _expand_inputs(files: dict[str, str], path: str, depth: int = 0) -> str:
    text = _strip_comments(files[path])
    if depth >= _MAX_INPUT_DEPTH:
        return text
    base = posixpath.dirname(path)

    def sub(m: re.Match) -> str:
        target = _resolve(files, base, m.group(2))
        return _expand_inputs(files, target, depth + 1) if target else ""

    return re.sub(r"\\(input|include|subfile)\s*\{([^}]*)\}", sub, text)


def _macros(text: str) -> dict[str, str]:
    """Zero-argument `\\newcommand` / `\\renewcommand` / `\\def` bodies — the
    method's own name is usually one, and a `--grep` for it must hit."""
    out: dict[str, str] = {}
    rx = re.compile(r"\\(?:re)?newcommand\*?\s*\{?\\([A-Za-z]+)\}?(\s*\[)?|\\def\\([A-Za-z]+)(\s*[#\[])?")
    for m in rx.finditer(text):
        name = m.group(1) or m.group(3)
        if m.group(2) or m.group(4):        # takes arguments — left as written
            continue
        body, _ = _group(text, m.end())
        if body:
            out[name] = body
    return out


def _apply_macros(text: str, macros: dict[str, str]) -> str:
    if not macros:
        return text
    rx = re.compile(r"\\(" + "|".join(sorted(map(re.escape, macros), key=len, reverse=True))
                    + r")(?![A-Za-z])(\{\})?")
    for _ in range(4):
        new = rx.sub(lambda m: macros[m.group(1)], text)
        if new == text:
            break
        text = new
    return text


# ── Detex ───────────────────────────────────────────────────────────────────

_KEEP_ARG = ("textbf", "textit", "emph", "texttt", "textsc", "textrm", "textsf",
             "underline", "mbox", "text", "textnormal", "uline", "textup")
_DROP_ARG = ("label", "vspace", "hspace", "vspace*", "hspace*", "bibliographystyle",
             "bibliography", "addcontentsline", "pagestyle", "thispagestyle",
             "setlength", "nonumfootnote", "phantomsection")
_DROP_BARE = ("centering", "noindent", "maketitle", "clearpage",
              "newpage", "small", "footnotesize", "scriptsize", "tiny", "large",
              "Large", "normalsize", "raggedright", "raggedleft", "hline",
              "toprule", "midrule", "bottomrule", "par", "medskip", "smallskip",
              "bigskip", "ignorespaces", "appendix", "tableofcontents",
              "justifying", "FloatBarrier")
_DISPLAY_ENVS = ("equation", "equation*", "align", "align*", "gather", "gather*",
                 "multline", "multline*", "eqnarray", "eqnarray*", "displaymath")
_LIST_ENVS = ("itemize", "enumerate", "description", "compactitem", "compactenum")


def _replace_cmd(text: str, names: tuple[str, ...], fn) -> str:
    rx = re.compile(r"\\(" + "|".join(map(re.escape, names)) + r")(?![A-Za-z*])")
    out, pos = [], 0
    for m in rx.finditer(text):
        if m.start() < pos:
            continue
        arg_at = _optional(text, m.end())
        arg, end = _group(text, arg_at)
        out.append(text[pos:m.start()])
        out.append(fn(m.group(1), arg, text, end))
        pos = end if end != arg_at else m.end()
    out.append(text[pos:])
    return "".join(out)


def _detex(text: str, labels: dict[str, tuple[str, str]]) -> str:
    for env in _DISPLAY_ENVS:
        e = re.escape(env)
        text = re.sub(rf"\\begin\{{{e}\}}(.*?)\\end\{{{e}\}}",
                      lambda m: "\n$" + re.sub(r"\\label\{[^}]*\}", "", m.group(1)).strip() + "$\n",
                      text, flags=re.S)
    text = re.sub(r"\\\[(.*?)\\\]", lambda m: "\n$" + m.group(1).strip() + "$\n", text, flags=re.S)
    text = re.sub(r"\$\$(.*?)\$\$", lambda m: "\n$" + m.group(1).strip() + "$\n", text, flags=re.S)
    text = re.sub(r"\\\((.*?)\\\)", lambda m: "$" + m.group(1) + "$", text, flags=re.S)

    def cite(_n, arg, *_):
        return "[" + ", ".join(k.strip() for k in arg.split(",")) + "]"

    def ref(name, arg, *_):
        out = []
        for key in (k.strip() for k in arg.split(",")):
            kind, number = labels.get(key, ("", key))
            if name == "eqref":
                out.append(f"({number})")
            elif name in ("cref", "Cref", "autoref") and kind:
                out.append(f"{kind} {number}")
            else:
                out.append(number)
        return ", ".join(out)

    text = _replace_cmd(text, ("cite", "citep", "citet", "citealp", "citeauthor",
                               "citeyear", "parencite", "textcite", "autocite"), cite)
    text = _replace_cmd(text, ("ref", "autoref", "cref", "Cref", "eqref", "pageref",
                               "nameref"), ref)
    text = _replace_cmd(text, ("href",), lambda _n, url, t, end: (
        _group(t, end)[0] or url))
    text = re.sub(r"\\href\s*\{[^}]*\}", "", text)
    text = _replace_cmd(text, ("url",), lambda _n, arg, *_: arg)
    text = _replace_cmd(text, ("footnote",), lambda _n, arg, *_: f" ({arg})")
    text = _replace_cmd(text, ("paragraph", "subparagraph"), lambda _n, arg, *_: f"\n\n{arg} ")
    text = _replace_cmd(text, _DROP_ARG, lambda *_: "")
    text = re.sub(r"\\(" + "|".join(_DROP_BARE) + r")(?![A-Za-z])\s*", "", text)
    for _ in range(3):
        text = _replace_cmd(text, _KEEP_ARG, lambda _n, arg, *_: arg)
    text = re.sub(r"\\begin\{(" + "|".join(_LIST_ENVS) + r")\}(\[[^\]]*\])?", "\n", text)
    text = re.sub(r"\\end\{(" + "|".join(_LIST_ENVS) + r")\}", "\n", text)
    text = re.sub(r"\\item\s*(\[([^\]]*)\])?\s*",
                  lambda m: "\n- " + (f"**{m.group(2)}** " if m.group(2) else ""), text)
    text = re.sub(r"\\(begin|end)\{(center|flushleft|flushright|minipage|small|quote)\}(\{[^}]*\})?",
                  "", text)
    text = re.sub(r"\\xspace(?![A-Za-z])", "", text)
    text = text.replace("{,}", ",").replace("{}", "")
    text = text.replace("\\\\", "\n").replace("~", " ")
    text = re.sub(r"\\([%&#_$])", r"\1", text)
    text = text.replace("``", "\u201c").replace("''", "\u201d").replace("---", "\u2014")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _split_top(text: str, sep: str) -> list[str]:
    """Split on `sep` outside every brace group — a `\\\\` inside
    `\\shortstack{…}` breaks a line in a cell, not a row."""
    parts, depth, i, last = [], 0, 0, 0
    while i < len(text):
        c = text[i]
        if c == "\\" and not text.startswith(sep, i):
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        elif depth == 0 and text.startswith(sep, i):
            parts.append(text[last:i])
            i += len(sep)
            last = i
            continue
        i += 1
    parts.append(text[last:])
    return parts


def _last_of(text: str, name: str, nargs: int) -> str:
    """Replace each `\\name[…]{…}…{…}` taking `nargs` groups by its last
    group — the cell text of `\\multicolumn` and `\\multirow`."""
    out, pos = [], 0
    for m in re.finditer(rf"\\{name}(?![A-Za-z])", text):
        if m.start() < pos:
            continue
        end, arg = m.end(), ""
        for _ in range(nargs):
            arg, end = _group(text, _optional(text, end))
        out.append(text[pos:m.start()] + arg)
        pos = end
    out.append(text[pos:])
    return "".join(out)


_TABULAR_ARGS = {"tabular": 1, "tabular*": 2, "tabularx": 2, "tabulary": 2, "longtable": 1}


def _tabular_markdown(body: str, labels: dict[str, tuple[str, str]]) -> str:
    m = re.search(r"\\begin\{(tabular\*?|tabularx|tabulary|longtable)\}", body)
    if not m:
        return ""
    pos = _optional(body, m.end())
    for _ in range(_TABULAR_ARGS[m.group(1)]):
        pos = _group(body, _optional(body, pos))[1]
    close = body.find(f"\\end{{{m.group(1)}}}", pos)
    grid = body[pos:close if close > 0 else len(body)]
    rows = []
    for line in _split_top(grid, "\\\\"):
        line = re.sub(r"\\(hline|toprule|midrule|bottomrule|cline\{[^}]*\}|"
                      r"cmidrule(\([^)]*\))?\{[^}]*\}|addlinespace(\[[^]]*\])?)", "", line)
        line = _last_of(line, "multicolumn", 3)
        line = _last_of(line, "multirow", 3)
        line = _last_of(line, "rotatebox", 2)
        line = _replace_cmd(line, ("shortstack", "makecell"),
                            lambda _n, a, *_: a.replace("\\\\", " "))
        cells = [_detex(c, labels).replace("\n", " ").strip()
                 for c in _split_top(line, "&")]
        if any(cells):
            rows.append(cells)
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    out = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * width]
    out += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(out)


# ── Parse ───────────────────────────────────────────────────────────────────

_LEVEL = {"section": 1, "subsection": 2, "subsubsection": 3}
_FLOAT = re.compile(r"\\begin\{(figure\*?|wrapfigure|table\*?|wraptable)\}(.*?)\\end\{\1\}", re.S)
_NUMBERED_EQ = re.compile(r"\\begin\{(equation|align|gather|multline|eqnarray)\}(.*?)\\end\{\1\}", re.S)
_SUBFLOAT = re.compile(r"\\begin\{(subfigure|subtable)\}.*?\\end\{\1\}", re.S)
_HEAD = re.compile(r"\\(section|subsection|subsubsection)(\*?)|\\appendix(?![A-Za-z])")


def _letter(n: int) -> str:
    return chr(ord("A") + n - 1) if 1 <= n <= 26 else str(n)


def parse_source(version: str, files: dict[str, str]) -> Paper:
    paper_id = version.split("v")[0]
    full = _expand_inputs(files, _root(files))
    macros = {}
    for name, text in sorted(files.items(), key=lambda kv: not kv[0].endswith((".cls", ".sty"))):
        if name.endswith((".tex", ".cls", ".sty")):
            macros.update(_macros(_strip_comments(text)))
    full = _apply_macros(full, macros)
    title = re.sub(r"\s+", " ", _command_arg(full, "title")).strip()
    doc = re.search(r"\\begin\{document\}(.*?)(\\end\{document\}|$)", full, re.S)
    doc = doc.group(1) if doc else full

    # The abstract is an environment in the standard classes and a command
    # in many conference and house classes.
    abstract = ""
    am = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", full, re.S)
    if am:
        abstract = am.group(1)
        doc = doc.replace(am.group(0), "")
    else:
        cm = re.search(r"\\abstract\s*(?=\{)", full)
        if cm:
            abstract, end = _group(full, cm.end())
            doc = doc.replace(full[cm.start():end], "")

    # Number the sections and floats first, so `\ref` can print what the PDF
    # prints. Floats are numbered in source order, as LaTeX's counters run.
    heads, labels = [], {}
    in_app, counts, unnumbered = False, [0, 0, 0], 0
    for m in _HEAD.finditer(doc):
        if m.group(0).startswith("\\appendix"):
            in_app, counts = True, [0, 0, 0]
            continue
        level, star = _LEVEL[m.group(1)], bool(m.group(2))
        title_at = _optional(doc, m.end())
        head_title, end = _group(doc, title_at)
        if star:
            unnumbered += 1
            parent = (f"A{counts[0]}" if in_app else f"S{counts[0]}") if level > 1 else ""
            sid = (f"{parent}.x{unnumbered}" if parent
                   else (f"A0.x{unnumbered}" if in_app else f"Sx{unnumbered}"))
            number = ""
        else:
            counts[level - 1] += 1
            for k in range(level, 3):
                counts[k] = 0
            first = _letter(counts[0]) if in_app else str(counts[0])
            number = ".".join([first] + [str(c) for c in counts[1:level]])
            prefix = "A" if in_app else "S"
            sid = f"{prefix}{counts[0]}" + "".join(
                f".{'S' * (k + 1)}{counts[k]}" for k in range(1, level))
        heads.append((m.start(), end, sid, level, number, head_title))
        if number:
            for lab in re.match(r"(\s*\\label\{[^}]*\})*", doc[end:]).group(0).split("\\label")[1:]:
                labels[lab.strip(" \n{}")] = ("App." if in_app else "Sec.", number)

    floats = []
    n_fig = n_tab = 0
    for m in _FLOAT.finditer(doc):
        kind, body = m.group(1), m.group(2)
        is_table = kind.startswith(("table", "wraptable"))
        if is_table:
            n_tab += 1
            number = str(n_tab)
        else:
            n_fig += 1
            number = str(n_fig)
        for lab in re.findall(r"\\label\{([^}]*)\}", body):
            labels.setdefault(lab, ("Table" if is_table else "Fig.", number))
        floats.append((m.start(), m.end(), is_table, number, body))

    # Numbered display math: one number per equation, one per row of an
    # aligned block unless the row opts out.
    n_eq = 0
    for m in _NUMBERED_EQ.finditer(doc):
        rows = _split_top(m.group(2), "\\\\") if m.group(1) != "equation" else [m.group(2)]
        for row in rows:
            if re.search(r"\\(nonumber|notag)\b", row) or not row.strip():
                continue
            n_eq += 1
            for lab in re.findall(r"\\label\{([^}]*)\}", row):
                labels.setdefault(lab, ("Eq.", str(n_eq)))

    def section_at(pos: int) -> str:
        sid = ""
        for start, _e, s, *_ in heads:
            if start > pos:
                break
            sid = s
        return sid

    # Any other label names the numbered section it sits in, as LaTeX's
    # `\label` refers to the last counter stepped.
    current = ("Sec.", "")
    events = sorted([(h[0], "head", h) for h in heads] +
                    [(m.start(), "label", m.group(1))
                     for m in re.finditer(r"\\label\{([^}]*)\}", doc)], key=lambda e: e[0])
    for _pos, what, item in events:
        if what == "head":
            if item[4]:
                current = ("App." if item[2].startswith("A") else "Sec.", item[4])
        elif item not in labels and current[1]:
            labels[item] = current

    figures, tables = [], []
    for start, _end, is_table, number, body in floats:
        # A subfigure carries its own caption and label ahead of the float's.
        own = _SUBFLOAT.sub("", body)
        caption = _detex(_command_arg(own, "caption"), labels).replace("\n", " ")
        label = (re.findall(r"\\label\{([^}]*)\}", own) or [""])[-1]
        if is_table:
            tables.append(Table(id=label or f"T{number}", number=number, caption=caption,
                                markdown=_tabular_markdown(body, labels),
                                section=section_at(start)))
        else:
            figures.append(Figure(id=label or f"F{number}", url="", number=number,
                                  caption=caption, section=section_at(start)))

    stripped = _FLOAT.sub("", doc)
    # Re-find the heads in the float-free text; their order is unchanged.
    sections = []
    spans = list(_HEAD.finditer(stripped))
    head_iter = iter(heads)
    marks = []
    for m in spans:
        if m.group(0).startswith("\\appendix"):
            continue
        _s, _e, sid, level, number, head_title = next(head_iter)
        end = _group(stripped, _optional(stripped, m.end()))[1]
        marks.append((m.start(), end, sid, level, number, head_title))
    # Text before the first heading is the title block and the teaser; the
    # abstract is read on its own above.
    for i, (_s, end, sid, level, number, head_title) in enumerate(marks):
        stop = marks[i + 1][0] if i + 1 < len(marks) else len(stripped)
        sections.append(Section(id=sid, level=level, number=number,
                                title=_detex(head_title, labels).replace("\n", " "),
                                text=_detex(stripped[end:stop], labels)))
    return Paper(id=paper_id, version=version, title=title,
                 abstract=_detex(abstract, labels),
                 sections=[s for s in sections if s.title or s.text],
                 figures=figures, tables=tables, source="tex",
                 bib=bibliography(files))


def bibliography(files: dict[str, str]) -> list[str]:
    """One line per entry — `.bbl` `\\bibitem`s when the source ships them,
    else the `.bib` entries — with the arXiv id's first-version month, as
    `builder.arxiv.bibliography` prints it for the HTML edition."""
    entries: list[str] = []
    bbl = [t for n, t in files.items() if n.endswith(".bbl")]
    if bbl:
        for text in bbl:
            entries += [e for e in re.split(r"\\bibitem", _strip_comments(text))[1:]]
    else:
        for name, text in files.items():
            if name.endswith(".bib"):
                entries += re.split(r"\n\s*@", "\n" + _strip_comments(text))[1:]
    out = []
    for entry in entries:
        flat = re.sub(r"\\[A-Za-z]+\s*|[{}]", " ", entry)
        flat = re.sub(r"\s+", " ", flat).strip()
        flat = re.sub(r"\s+([,.;:)])", r"\1", flat)
        m = _BIB_ID.search(flat)
        out.append(flat + (f"  → arXiv {m.group(0)} · 20{m.group(1)}.{m.group(2)}"
                           if m else "  → no arXiv id · venue year"))
    return out


def load_source(paper_id: str) -> Paper:
    version, files = fetch_source(paper_id)
    return parse_source(version, files)
