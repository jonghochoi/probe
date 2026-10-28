#!/usr/bin/env python3
"""Render the distinction track's documents as standalone HTML pages for reading.

A versus note, a report and a deep dive are records: the lint reads them and the
next run builds on them. Each gets a page beside it for a person —
`versus/<id>--<alias>.html`, `reports/<date>.html`, `deepdive/<id>--<alias>--<scope>.html` — one
file opened from disk that never leaves the private folder. A page is
redrawn from its Markdown and never edited by hand
(`distinction/AUTHORING.md` §3-6).

The pages borrow the reading site's look rather than its build: the design
tokens are cut from `site/builder/assets/site.css`, the drawn charts come from
`site/builder/charts.py` and their rules from `site/builder/assets/charts.css`,
inlined whole. Nothing here reaches the site — `site/CLAUDE.md`'s publish list does not change — and
the script runs on the standard library alone, like the lint, because the
machine that runs `/distinguish` need not hold the site's dependencies.

What a page adds to the Markdown is arrangement, never content:

    versus note    §2 their choice and this method's side by side; §4 the fill
              verdict as a badge; §5 one card per idea
    report     a basket id links to its versus note's page; §8 one row per audited
              versus note; the closing state block as a table of when each
              versus note was last verified, the raw block folded; the runs
              before and after it one click away
    deep dive  §1 the count line as one bar split by verdict, 틀림 and 과장
              open, 원문 없음 and 맞음 folded; §4 one card per stage, the two
              sides side by side; §5 the table, the scope's column in the
              accent; §6 a ```probe-chart fence drawn; §7 the fill verdict
              as a badge; §8 one card per idea
    everywhere  the anchors a bullet ends on set apart as its evidence;
              `원문 §… "…"` set as a quotation; `path:line` linked into the
              editor through the code root; `cfg:`, `C#` and `METHOD §n` as
              chips, `C#` and `D#` titled on hover; the paper anchor linked
              to the rewrite on the reading site

Usage (repo root):
    python3 distinction/render-distinction.py              # every page in $PROBE_PRIVATE_DIR
    python3 distinction/render-distinction.py <md> [<md>…] # those pages
    python3 distinction/render-distinction.py <md> -o OUT  # one page, elsewhere

A page is written next to its Markdown with `.html`. The code root is `code:`
in the private folder's `MY-METHOD.md`, else its `code` symlink
(`distinction/SETUP.md` §2-4).

Exit codes: 0 = written / 1 = a chart fence cannot be drawn / 2 = no input.
"""
from __future__ import annotations

import argparse
import glob
import html
import json
import os
import re
import sys
import urllib.parse

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_REPO_ROOT, "site"))

from builder import charts  # noqa: E402  (standard library only)
from builder.decisions import harvest_decisions  # noqa: E402

_SITE = "https://jonghochoi.github.io/probe/"
_ASSETS = os.path.join(_REPO_ROOT, "site", "builder", "assets")

_ERRATA = ("틀림", "과장", "원문 없음", "맞음")
_FILLS = ("메운다", "부분", "못 메운다")
# Folded by default: the rows a reader checks only when doubting the bar.
_ERRATA_FOLDED = ("원문 없음", "맞음")

_H2 = re.compile(r"^## (\d) (.+)$")
_H3 = re.compile(r"^### (.+)$")
_FENCE = re.compile(r"^\s*```(\S*)\s*$")
_ROW = re.compile(r"^\s*\|(.+)\|\s*$")
_RULE = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
_COUNT = re.compile(r"(점검|맞음|틀림|과장|원문 없음) (\d+)")
_META = re.compile(r"(\w+): (\S+)")

_CODE_SPAN = re.compile(r"`([^`\n]+)`")
_QUOTE = re.compile(r'원문 §([^\s"]+) "([^"]+)"')
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
_DECISION = re.compile(r"\b(D\d[A-Z]{2})\b")
# A bare arXiv id in running text — not one inside a URL or a path.
_ID = re.compile(r"(?<![\w/.=])(\d{4}\.\d{5})(?![\w/])")
_CLAIM = re.compile(r"^C\d+$")
_METHOD = re.compile(r"^METHOD §(\d)$")
_CFG = re.compile(r"^cfg:\S+")
_PATH_LINE = re.compile(r"^([^\s:]+):(\d+)$")
_PAPER = re.compile(r"^(\S.*?) §([1-4]) (.+)$")


def esc(text: str) -> str:
    return html.escape(text, quote=True)


# ── Context: what an anchor resolves against ──────────────────────────


class Context:
    def __init__(self, private: str, paper_id: str, kind: str, scope: str = ""):
        self.private = private
        self.paper_id = paper_id
        self.kind = kind
        # `{id: alias}` per versus note, read off each H1, so a basket id written
        # anywhere can link to the page that holds the position on it; the
        # page's file stem beside it, since the name carries the alias too.
        self.ledgers: dict[str, str] = {}
        self.ledger_stems: dict[str, str] = {}
        for lp in sorted(glob.glob(os.path.join(private, "versus", "*.md"))):
            try:
                with open(lp, encoding="utf-8") as fh:
                    first = fh.readline()
            except OSError:
                continue
            stem = os.path.basename(lp)[:-3]
            lid = stem.partition("--")[0]
            self.ledger_stems[lid] = stem
            self.ledgers[lid] = first[2:].partition(" — ")[0].strip() if first.startswith("# ") else lid
        self.decisions = {k: t for k, (_, t) in harvest_decisions().items()}
        self.claims: dict[str, str] = {}
        # What our side is called beside the paper's alias (AUTHORING §6):
        # the scope a deep dive names, else `MY-METHOD.md`'s `name:`.
        self.ours = scope
        code = os.path.join(private, "code")
        try:
            with open(os.path.join(private, "MY-METHOD.md"), encoding="utf-8") as fh:
                for raw in fh:
                    m = re.match(r"^#### \[(C\d+)\] (.+)$", raw)
                    if m:
                        self.claims[m.group(1)] = m.group(2).strip()
                    m = re.match(r"^code: (/\S+)", raw)
                    if m:
                        code = m.group(1)
                    m = re.match(r"^name: (\S+)", raw)
                    if m and not self.ours:
                        self.ours = m.group(1)
        except OSError:
            pass
        self.code_root = os.path.realpath(code) if os.path.exists(code) else None

    def ledger_href(self, pid: str) -> str:
        page = self.ledger_stems.get(pid, pid) + ".html"
        return page if self.kind == "versus" else f"../versus/{page}"

    def code_href(self, path: str, line: str) -> str | None:
        if not self.code_root:
            return None
        full = os.path.join(self.code_root, path)
        return "vscode://file" + urllib.parse.quote(full) + f":{line}"


# ── Inline: one line of the Markdown, anchors made legible ────────────


def _anchor(code: str, ctx: Context) -> str:
    if _CLAIM.match(code):
        title = ctx.claims.get(code, "")
        return f'<span class="ax ax-claim" title="{esc(title)}">{esc(code)}</span>'
    m = _METHOD.match(code)
    if m:
        return (f'<a class="ax ax-method" href="../MY-METHOD.md">{esc(code)}</a>')
    if _CFG.match(code):
        key, eq, val = code[4:].partition("=")
        return (f'<code class="ax ax-cfg"><span>cfg</span>{esc(key.strip())}'
                + (f' = {esc(val.strip())}' if eq else "") + "</code>")
    m = _PATH_LINE.match(code)
    if m and "/" in m.group(1):
        path, line = m.groups()
        base = path.rsplit("/", 1)[-1]
        href = ctx.code_href(path, line)
        inner = f'{esc(base)}<b>:{line}</b>'
        if href:
            return f'<a class="ax ax-code" href="{esc(href)}" title="{esc(path)}:{line}">{inner}</a>'
        return f'<code class="ax ax-code" title="{esc(path)}:{line}">{inner}</code>'
    m = _PAPER.match(code)
    if m:
        alias, act, term = m.groups()
        href = f"{_SITE}p/{ctx.paper_id}/index.html"
        return (f'<a class="ax ax-paper" href="{esc(href)}" title="재작성본 {act}막 · {esc(term)}">'
                f'<span>{esc(alias)} §{act}</span>{esc(term)}</a>')
    return f"<code>{esc(code)}</code>"


def _prose(text: str, ctx: Context) -> str:
    out = html.escape(text, quote=False)
    out = _QUOTE.sub(lambda m: (
        f'<span class="dx-q"><span class="dx-qs">원문 §{m.group(1)}</span>'
        f'<q lang="en">{m.group(2)}</q></span>'), out)
    out = _BOLD.sub(r"<strong>\1</strong>", out)
    out = _LINK.sub(r'<a href="\2">\1</a>', out)
    out = _DECISION.sub(lambda m: (
        f'<abbr class="ax-dec" title="{esc(ctx.decisions[m.group(1)])}">{m.group(1)}</abbr>'
        if m.group(1) in ctx.decisions else m.group(1)), out)
    out = _ID.sub(lambda m: (
        f'<a class="ax-led" href="{ctx.ledger_href(m.group(1))}" title="맞대기 · {esc(ctx.ledgers[m.group(1)])}">'
        f'{m.group(1)}</a>' if m.group(1) in ctx.ledgers and m.group(1) != (ctx.paper_id if ctx.kind == "versus" else "")
        else m.group(1)), out)
    return out.replace("원문 미확인", '<span class="dx-unq">원문 미확인</span>')


def inline(text: str, ctx: Context) -> str:
    # Code spans are cut first so a quote or `**` inside one stays literal.
    out, at = [], 0
    for m in _CODE_SPAN.finditer(text):
        out.append(_prose(text[at:m.start()], ctx))
        out.append(_anchor(m.group(1), ctx))
        at = m.end()
    out.append(_prose(text[at:], ctx))
    return "".join(out)


# One piece of evidence at the very end of a bullet, with the separator before it.
_TAIL = re.compile(r'(?:\s*[,·]\s*|\s+)?(`[^`\n]+`|원문 §[^\s"]+ "[^"]+"|원문 미확인)\s*$')


def _evidence(text: str) -> tuple[str, list[str]]:
    """Peel the anchors and quotes a bullet ends on into a list of their own.

    A bullet states its point and then its evidence; set apart, the point
    reads as a sentence and the evidence as a row of sources. Anchors inside
    the sentence stay where they are — they are part of what it says."""
    tail: list[str] = []
    while True:
        m = _TAIL.search(text)
        if not m or not text[:m.start()].strip() or not _is_anchor(m.group(1)):
            break
        tail.insert(0, m.group(1))
        text = text[:m.start()].rstrip()
    return text.rstrip(" ,·"), tail


def _is_anchor(token: str) -> bool:
    """A quote or one of the anchor kinds — not a value in code type."""
    if not token.startswith("`"):
        return True
    code = token.strip("`")
    m = _PATH_LINE.match(code)
    return bool(_CLAIM.match(code) or _METHOD.match(code) or _CFG.match(code)
                or (m and "/" in m.group(1)) or _PAPER.match(code))


def _ev(tail: list[str], ctx: Context) -> str:
    if not tail:
        return ""
    return ('<div class="dx-ev">' + "".join(f"<span>{inline(t, ctx)}</span>" for t in tail)
            + "</div>")


# `<alias> 은 …, <ours> 는 …` — a bullet that sets the two sides in one
# sentence, cut where our side's half begins.
def _sides(text: str, ours: str) -> re.Match | None:
    if not ours:
        return None
    return re.match(rf"^(.+?), ({re.escape(ours)}\s*(?:은|는|의|도)\s+(.+))$", text)


def _labelled(text: str) -> tuple[str, str]:
    """`**label** — rest` -> (label, rest); no label -> ("", text)."""
    m = re.match(r"^\*\*(.+?)\*\*\s*(?:—\s*)?(.*)$", text)
    return (m.group(1), m.group(2)) if m else ("", text)


def _verdict(text: str, verdicts: tuple[str, ...]) -> tuple[str, str]:
    for v in sorted(verdicts, key=len, reverse=True):
        for form in (f"**{v}**", v):
            if text.startswith(form):
                rest = text[len(form):].lstrip()
                return v, rest[1:].lstrip() if rest.startswith("—") else rest
    return "", text


# ── Blocks: a section's lines as bullets, tables, fences, paragraphs ──


def blocks(lines: list[str]) -> list[tuple[str, object]]:
    out: list[tuple[str, object]] = []
    fence: tuple[str, list[str]] | None = None
    for raw in lines:
        if fence is not None:
            if raw.strip().startswith("```"):
                out.append(("fence", fence))
                fence = None
            else:
                fence[1].append(raw)
            continue
        m = _FENCE.match(raw)
        if m:
            fence = (m.group(1), [])
        elif _H3.match(raw):
            out.append(("h3", _H3.match(raw).group(1).strip()))
        elif raw.startswith("- "):
            out.append(("bullet", raw[2:].strip()))
        elif raw.startswith("  ") and raw.strip() and out and out[-1][0] == "bullet":
            out[-1] = ("bullet", f"{out[-1][1]} {raw.strip()}")
        elif _ROW.match(raw):
            if _RULE.match(raw):
                continue
            cells = [c.strip() for c in _ROW.match(raw).group(1).split("|")]
            if out and out[-1][0] == "table":
                out[-1][1].append(cells)
            else:
                out.append(("table", [cells]))
        elif raw.strip():
            out.append(("para", raw.strip()))
    return out


def _row(text: str, ctx: Context, badge: str = "", cls: str = "",
         alias: str = "") -> str:
    label, rest = _labelled(text)
    rest, tail = _evidence(rest)
    head = f'<span class="dx-badge" data-v="{esc(badge)}">{esc(badge)}</span>' if badge else ""
    if label in ctx.ledgers:
        # A row about one versus note — a report's audit — names the paper, not the id.
        lab = (f'<a class="dx-label" href="{ctx.ledger_href(label)}">{esc(ctx.ledgers[label])}'
               f' <small class="ax-led">{label}</small></a>')
    else:
        lab = f'<span class="dx-label">{inline(label, ctx)}</span>' if label else ""
    sides = _sides(rest, ctx.ours) if alias else None
    if sides and rest.startswith(alias):
        theirs = re.sub(rf"^{re.escape(alias)}\s*(?:은|는|의)\s+", "", sides.group(1))
        body = (f'<div class="dx-sides"><div><span class="dx-sh">{esc(alias)}</span>{inline(theirs, ctx)}</div>'
                f'<div><span class="dx-sh">{esc(ctx.ours)}</span>{inline(sides.group(3), ctx)}</div></div>')
    else:
        body = f'<div class="dx-text">{inline(rest, ctx)}</div>'
    return (f'<li class="dx-row {cls}"><div class="dx-head">{head}{lab}</div>'
            f'{body}{_ev(tail, ctx)}</li>')


def _chart(info: str, body: list[str], where: str) -> tuple[str, list[str]]:
    if info != "probe-chart":
        return f"<pre><code>{esc(chr(10).join(body))}</code></pre>", []
    try:
        spec = json.loads("\n".join(body))
    except json.JSONDecodeError as err:
        return "", [f"{where}: ```probe-chart is not JSON — {err}"]
    probs = charts.problems(where, "chart", spec)
    if probs:
        return "", probs
    why = (f'<details class="dx-why"><summary>이 그림이 원문에서 가져온 것</summary>'
           f'<p>{esc(spec["why"])}</p>'
           + (f'<p class="dx-om">뺀 것 — {esc(" · ".join(spec["omitted"]))}</p>' if spec.get("omitted") else "")
           + "</details>")
    # The page column hands the chart the shape its rows need, so a tall
    # `dots` keeps its type size instead of widening.
    ratio = 1000 / (136 + 72 * len(spec.get("rows", []))) if spec["kind"] == "dots" else 1000 / 560
    return f'<div class="pc-frame dx-chart">{charts.chart(spec, ratio)}{why}</div>', []


# Per kind: the section drawn as errata, as stage cards, as idea cards, the
# one whose bullets open on a fill verdict, the one whose bullets set the two
# sides side by side, and the one a ```probe-chart is drawn in.
_LAYOUT = {
    "deepdive": {"errata": "1", "stages": "4", "ideas": "8", "fills": "7", "sides": "", "charts": "6"},
    "versus": {"errata": "", "stages": "", "ideas": "5", "fills": "4", "sides": "2", "charts": ""},
    "reports": {"errata": "", "stages": "", "ideas": "5", "fills": "", "sides": "", "charts": ""},
}


def section(num: str, lines: list[str], ctx: Context, problems: list[str],
            alias: str) -> str:
    bl = blocks(lines)
    out: list[str] = []
    lay = _LAYOUT[ctx.kind]
    if num == lay["errata"]:
        return _errata(bl, ctx)
    if num == lay["stages"]:
        return _stages(bl, ctx, alias)
    if num == lay["ideas"]:
        return _ideas(bl, ctx)
    items: list[str] = []

    def flush() -> None:
        if items:
            out.append(f'<ul class="dx-rows">{"".join(items)}</ul>')
            items.clear()

    for kind, val in bl:
        if kind == "bullet":
            if val == "없음":
                items.append('<li class="dx-none">없음</li>')
            elif num == lay["fills"]:
                v, rest = _verdict(val, _FILLS)
                items.append(_row(rest, ctx, badge=v))
            else:
                items.append(_row(val, ctx, alias=alias if num == lay["sides"] else ""))
            continue
        flush()
        if kind == "table":
            out.append(_table(val, ctx))
        elif kind == "fence" and num == lay["charts"]:
            drawn, probs = _chart(val[0], val[1], f"§{num}")
            problems.extend(probs)
            out.append(drawn)
        elif kind == "fence" and val[0] == "probe-state":
            out.append(_state(val[1], ctx))
        elif kind == "para":
            out.append(f"<p>{inline(val, ctx)}</p>")
    flush()
    return "".join(out)


def _state(body: list[str], ctx: Context) -> str:
    """The report's closing block: when each versus note was last verified, then
    the block itself, folded — it is the next run's memory, not reading."""
    raw = "\n".join(body)
    try:
        state = json.loads(raw)
    except json.JSONDecodeError:
        state = {}
    rows = "".join(
        f'<tr><th scope=row><a href="{ctx.ledger_href(pid)}">{esc(ctx.ledgers.get(pid, pid))}</a></th>'
        f"<td>{esc(pid)}</td><td>{esc(str(day))}</td></tr>"
        for pid, day in sorted((state.get("verified") or {}).items(), key=lambda kv: str(kv[1])))
    table = (f'<h3>맞대기별 마지막 검증</h3><div class="dx-table"><table><thead><tr><th>맞대기</th><th>id</th>'
             f"<th>날짜</th></tr></thead><tbody>{rows}</tbody></table></div>") if rows else ""
    pretty = json.dumps(state, ensure_ascii=False, indent=1) if state else raw
    return (f'<div class="dx-state">{table}<details class="dx-why"><summary>런 상태 원문 · probe-state</summary>'
            f"<pre><code>{esc(pretty)}</code></pre></details></div>")


def _table(rows: list[list[str]], ctx: Context) -> str:
    head, body = rows[0], rows[1:]
    th = "".join(f"<th>{inline(c, ctx)}</th>" for c in head)
    tr = "".join("<tr>" + "".join(
        f'<{"th scope=row" if i == 0 else "td"}>{inline(c, ctx)}</{"th" if i == 0 else "td"}>'
        for i, c in enumerate(r)) + "</tr>" for r in body)
    return f'<div class="dx-table dx-scope"><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


def _errata(bl: list, ctx: Context) -> str:
    count = next((v for k, v in bl if k == "para" and _COUNT.search(v)), "")
    n = {k: int(v) for k, v in _COUNT.findall(count)}
    groups: dict[str, list[str]] = {v: [] for v in _ERRATA}
    for kind, val in bl:
        if kind == "bullet" and val != "없음":
            v, rest = _verdict(val, _ERRATA)
            groups.setdefault(v or "맞음", []).append(_row(rest, ctx))
    total = sum(n.get(v, 0) for v in _ERRATA) or 1
    bar = "".join(
        f'<span class="dx-seg" data-v="{v}" style="flex:{n.get(v, 0)}" '
        f'title="{v} {n.get(v, 0)}"></span>' for v in _ERRATA if n.get(v))
    legend = "".join(
        f'<a class="dx-key" href="#errata-{i}" data-v="{v}"><i></i>{v} <b>{n.get(v, 0)}</b>'
        f'<small>{100 * n.get(v, 0) / total:.0f}%</small></a>' for i, v in enumerate(_ERRATA))
    note = ("<p class=\"dx-note\">아래 줄은 대표 사례입니다. 막대는 정오표 에이전트가 점검한 "
            f"{n.get('점검', total)} 개 진술 전체의 집계입니다.</p>")
    parts = [f'<div class="dx-bar">{bar}</div><div class="dx-keys">{legend}</div>{note}']
    for i, v in enumerate(_ERRATA):
        rows = groups.get(v) or []
        if not rows:
            continue
        open_ = "" if v in _ERRATA_FOLDED else " open"
        parts.append(
            f'<details class="dx-group" id="errata-{i}" data-v="{v}"{open_}>'
            f'<summary><span class="dx-badge" data-v="{v}">{v}</span>'
            f'<span class="dx-gn">{len(rows)} 줄</span></summary>'
            f'<ul class="dx-rows">{"".join(rows)}</ul></details>')
    return "".join(parts)


def _stages(bl: list, ctx: Context, alias: str) -> str:
    cards: list[tuple[str, list[str]]] = []
    for kind, val in bl:
        if kind == "h3":
            cards.append((val, []))
        elif kind == "bullet":
            if not cards:
                cards.append(("", []))
            cards[-1][1].append(_row(val, ctx, alias=alias) if val != "없음" else '<li class="dx-none">없음</li>')
    return "".join(
        f'<article class="dx-card">'
        + (f'<h3 id="stage-{i}">{inline(t, ctx)}</h3>' if t else "")
        + f'<ul class="dx-rows dx-tight">{"".join(rows)}</ul></article>'
        for i, (t, rows) in enumerate(cards))


def _ideas(bl: list, ctx: Context) -> str:
    cards: list[tuple[str, list[str]]] = []
    for kind, val in bl:
        if kind == "h3":
            cards.append((val, []))
        elif kind == "bullet" and val != "없음" and cards:
            label, rest = _labelled(val)
            rest, tail = _evidence(rest)
            cards[-1][1].append(f"<dt>{esc(label)}</dt><dd>{inline(rest, ctx)}{_ev(tail, ctx)}</dd>")
    if not cards:
        return '<ul class="dx-rows"><li class="dx-none">없음</li></ul>'
    return "".join(
        f'<article class="dx-card dx-idea"><div class="dx-ino">{i + 1}</div>'
        f'<h3 id="idea-{i}">{inline(t, ctx)}</h3><dl>{"".join(rows)}</dl></article>'
        for i, (t, rows) in enumerate(cards))


# ── Page ──────────────────────────────────────────────────────────────


def _cut(path: str, start: str, end: str) -> str:
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    a = text.index(start)
    return text[a:text.index(end, a + len(start))]


def _tokens() -> str:
    site = os.path.join(_ASSETS, "site.css")
    light = _cut(site, ":root {", "\n}\n") + "\n}\n"
    dark = _cut(site, ':root[data-theme="dark"] {', "\n}\n") + "\n}\n"
    with open(os.path.join(_ASSETS, "charts.css"), encoding="utf-8") as fh:
        figs = fh.read()
    return light + dark + figs


_CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{background:var(--bg);color:var(--text);font:16px/1.75 var(--ko);-webkit-font-smoothing:antialiased}
body{background:var(--bg)}
a{color:var(--orange-ink);text-decoration:none}
a:hover{text-decoration:underline}
.dx-shell{display:grid;grid-template-columns:var(--toc-w) minmax(0,46rem);gap:3rem;justify-content:center;padding:3rem 1.5rem 6rem}
.dx-toc{position:sticky;top:2rem;align-self:start;font-size:.86rem;line-height:1.5}
.dx-toc b{display:block;font-size:.72rem;letter-spacing:.08em;color:var(--text-muted);margin-bottom:.6rem}
.dx-toc a{display:flex;gap:.6rem;padding:.32rem .6rem;border-left:2px solid var(--border-soft);color:var(--text-muted)}
.dx-toc a:hover,.dx-toc a.on{color:var(--text);border-left-color:var(--orange);text-decoration:none}
.dx-toc a span{font-family:var(--num);color:var(--orange-ink);min-width:1ch}
.dx-toc small{margin-left:auto;font-family:var(--num);opacity:.7}
.dx-eyebrow{font-size:.78rem;letter-spacing:.06em;color:var(--orange-ink);font-weight:700;margin-bottom:.8rem}
h1{font-size:2rem;line-height:1.25;letter-spacing:-.01em;margin-bottom:.9rem}
h1 .x{color:var(--orange-ink);padding:0 .25em;font-weight:400}
.dx-thesis{font-size:1.05rem;color:var(--text);border-left:3px solid var(--orange);padding:.2rem 0 .2rem 1rem;margin-bottom:1.4rem}
.dx-meta{display:flex;flex-wrap:wrap;gap:.4rem;margin-bottom:2.6rem}
.dx-meta span{font:.76rem/1 var(--mono);padding:.42rem .6rem;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);color:var(--text-muted)}
.dx-meta span b{color:var(--text);font-weight:600;margin-left:.35em}
section{margin-top:3.4rem;scroll-margin-top:1.5rem}
h2{display:flex;align-items:baseline;gap:.75rem;font-size:1.35rem;padding-bottom:.6rem;border-bottom:1px solid var(--border);margin-bottom:1.3rem}
h2 span{font-family:var(--num);color:var(--orange-ink);font-size:1rem}
h3{font-size:1.02rem;margin-bottom:.7rem}
p{margin:.6rem 0}
.dx-rows{list-style:none;display:grid;gap:.7rem}
.dx-row{background:var(--surface);border:1px solid var(--border-soft);border-radius:var(--radius);padding:.85rem 1rem}
.dx-tight .dx-row{background:none;border:0;border-top:1px solid var(--border-soft);border-radius:0;padding:.75rem 0 .2rem}
.dx-tight .dx-row:first-child{border-top:0;padding-top:.1rem}
.dx-head{display:flex;gap:.55rem;align-items:baseline;flex-wrap:wrap}
.dx-label{font-weight:700}
.dx-text{color:var(--text);font-size:.95rem}
.dx-head:not(:empty)+.dx-text{margin-top:.2rem}
.dx-none{color:var(--text-muted);list-style:none}
.dx-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.2rem 1.3rem;margin-bottom:1rem;position:relative}
.dx-card h3{color:var(--text)}
.dx-idea{padding-left:3.6rem}
.dx-ino{position:absolute;left:1.2rem;top:1.05rem;width:1.7rem;height:1.7rem;border-radius:50%;background:var(--orange);color:var(--accent-ink);display:grid;place-items:center;font:700 .9rem var(--num)}
.dx-idea dl{display:grid;grid-template-columns:max-content 1fr;gap:.55rem 1rem;font-size:.93rem}
.dx-idea dt{font-weight:700;color:var(--text-muted);font-size:.82rem;padding-top:.15rem}
.dx-badge{font:700 .74rem/1 var(--ko);padding:.3rem .5rem;border-radius:var(--radius-pill);white-space:nowrap;background:var(--surface-2);color:var(--text-muted)}
[data-v="틀림"]{--v:var(--red);--vw:var(--wash-ten)}
[data-v="과장"]{--v:var(--amber);--vw:var(--wash-warn)}
[data-v="원문 없음"]{--v:var(--violet);--vw:var(--wash-ctx)}
[data-v="맞음"]{--v:var(--green);--vw:var(--wash-win)}
[data-v="메운다"]{--v:var(--green);--vw:var(--wash-win)}
[data-v="부분"]{--v:var(--amber);--vw:var(--wash-warn)}
[data-v="못 메운다"]{--v:var(--red);--vw:var(--wash-ten)}
.dx-badge[data-v]{background:var(--vw);color:var(--v);box-shadow:inset 0 0 0 1px color-mix(in oklch,var(--v) 35%,transparent)}
.dx-bar{display:flex;height:.9rem;border-radius:var(--radius);overflow:hidden;gap:2px;margin-bottom:.8rem}
.dx-seg{background:var(--v);min-width:4px}
.dx-keys{display:flex;flex-wrap:wrap;gap:.4rem 1.2rem;font-size:.86rem}
.dx-key{color:var(--text);display:flex;align-items:center;gap:.4rem}
.dx-key i{width:.7rem;height:.7rem;border-radius:2px;background:var(--v)}
.dx-key b{font-family:var(--num)}
.dx-key small{color:var(--text-muted);font-family:var(--num)}
.dx-note{font-size:.82rem;color:var(--text-muted);margin:.8rem 0 1.2rem}
.dx-group{margin-top:1rem}
.dx-group>summary{cursor:pointer;display:flex;align-items:center;gap:.6rem;padding:.4rem 0;list-style:none}
.dx-group>summary::-webkit-details-marker{display:none}
.dx-group>summary::before{content:"▸";color:var(--text-muted);transition:transform var(--dur-short)}
.dx-group[open]>summary::before{transform:rotate(90deg)}
.dx-gn{font-size:.82rem;color:var(--text-muted);font-family:var(--num)}
.dx-group .dx-row{border-left:3px solid var(--v)}
.dx-q{display:inline;background:var(--surface-2);border-radius:var(--radius);padding:.05rem .4rem;font-size:.88em;box-decoration-break:clone;-webkit-box-decoration-break:clone}
.dx-qs{font:600 .78em var(--mono);color:var(--text-muted);margin-right:.4em}
.dx-q q{font-style:italic;color:var(--text)}
.dx-q q::before{content:"“"}.dx-q q::after{content:"”"}
.dx-unq{font-size:.8em;color:var(--violet);border:1px dashed var(--violet);border-radius:var(--radius);padding:0 .3rem}
.ax,code{font:500 .78em/1.5 var(--mono);border-radius:var(--radius);padding:.08rem .38rem;white-space:nowrap;background:var(--code-bg);color:var(--text);border:1px solid var(--code-rule)}
a.ax:hover{text-decoration:none;border-color:var(--orange)}
.ax-code{white-space:normal;word-break:break-all}
.dx-ev{position:relative;display:flex;flex-wrap:wrap;gap:.35rem .5rem;margin-top:.55rem;padding:.5rem 0 0 2.5rem;border-top:1px dashed var(--border-soft);font-size:.92rem;line-height:1.5}
.dx-ev::before{content:"근거";position:absolute;left:0;top:.55rem;font:700 .7rem/1.9 var(--ko);color:var(--text-muted);letter-spacing:.04em}
.dx-ev .dx-q{display:inline}
.dx-sides{display:grid;grid-template-columns:1fr 1fr;gap:.9rem;margin-top:.35rem;font-size:.93rem}
.dx-sides>div{padding:.55rem .75rem;border-radius:var(--radius);background:var(--surface-2)}
.dx-sides>div:last-child{background:var(--orange-soft)}
.dx-sides>div>.dx-sh{display:block;font:700 .72rem var(--ko);color:var(--text-muted);margin-bottom:.15rem;overflow-wrap:anywhere}
.dx-sides>div:last-child>.dx-sh{color:var(--orange-ink)}
.ax-code b{color:var(--orange-ink);font-weight:600}
.ax-cfg span{color:var(--blue);margin-right:.35em;font-weight:700}
.ax-claim{background:var(--orange-soft);color:var(--orange-ink);border-color:color-mix(in oklch,var(--orange) 40%,transparent);font-weight:700;cursor:help}
.ax-method{background:var(--wash-ctx);color:var(--violet);border-color:color-mix(in oklch,var(--violet) 30%,transparent)}
.ax-paper{background:var(--wash-key);color:var(--blue);border-color:color-mix(in oklch,var(--blue) 30%,transparent);white-space:normal}
.ax-paper span{font-weight:700;margin-right:.35em}
.ax-dec{color:var(--dref);font-weight:700;text-decoration:underline dotted;cursor:help}
.dx-table{overflow-x:auto;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface)}
.dx-table table{border-collapse:collapse;width:100%;font-size:.88rem;line-height:1.55}
.dx-table th,.dx-table td{padding:.65rem .8rem;text-align:left;vertical-align:top;border-top:1px solid var(--border-soft)}
.dx-table thead th{background:var(--surface-2);border-top:0;font-size:.8rem;color:var(--text-muted)}
.dx-scope thead th:last-child{color:var(--orange-ink)}
.dx-table tbody th{font-weight:700;white-space:nowrap}
.dx-scope td:last-child{background:color-mix(in oklch,var(--orange) 5%,transparent)}
.dx-chart{margin:1.4rem 0;padding:1.1rem 1.2rem 1rem;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius)}
.dx-chart .pc-fig>svg{height:auto}
.dx-chart .pc-fig figcaption{margin-top:.4rem}
.dx-why{margin-top:.6rem;font-size:.86rem;color:var(--text-muted)}
.dx-why summary{cursor:pointer}
.dx-om{font-size:.82rem}
.dx-theme{position:fixed;right:1rem;top:1rem;font:600 .78rem var(--ko);background:var(--surface);color:var(--text-muted);border:1px solid var(--border);border-radius:var(--radius);padding:.35rem .6rem;cursor:pointer}
h1 small{font:500 .9rem var(--mono);color:var(--text-muted)}
.ax-led{font-family:var(--mono);font-size:.9em;font-weight:600}
.dx-runs{display:flex;justify-content:space-between;font:600 .82rem var(--mono);margin-bottom:1.6rem}
.dx-state{margin-top:2.2rem}
.dx-state pre{margin-top:.6rem;padding:.8rem;background:var(--code-bg);border-radius:var(--radius);overflow-x:auto;font:.76rem/1.5 var(--mono);color:var(--text)}
.dx-state pre code{border:0;background:none;padding:0;white-space:pre}
footer{margin-top:4rem;font-size:.78rem;color:var(--text-muted)}
@media (max-width:980px){.dx-shell{grid-template-columns:minmax(0,1fr);padding:2rem 1rem 4rem}.dx-toc{display:none}h1{font-size:1.6rem}.dx-idea{padding-left:1.3rem}.dx-ino{position:static;margin-bottom:.6rem}.dx-idea dl{grid-template-columns:1fr}.dx-sides{grid-template-columns:1fr}}
@media print{.dx-toc,.dx-theme{display:none}.dx-shell{display:block}details{open:true}}
"""

_JS = """
(function(){var r=document.documentElement,k='dx-theme';
function set(m){r.setAttribute('data-theme',m)}
var s=null;try{s=localStorage.getItem(k)}catch(e){}
set(s||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'));
document.addEventListener('DOMContentLoaded',function(){
var b=document.querySelector('.dx-theme');b.onclick=function(){var m=r.getAttribute('data-theme')==='dark'?'light':'dark';set(m);try{localStorage.setItem(k,m)}catch(e){}};
var links=[].slice.call(document.querySelectorAll('.dx-toc a'));
var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){links.forEach(function(a){a.classList.toggle('on',a.getAttribute('href')==='#'+e.target.id)})}})},{rootMargin:'0px 0px -70% 0px'});
document.querySelectorAll('section[id]').forEach(function(s){io.observe(s)});
document.querySelectorAll('.dx-key').forEach(function(a){a.onclick=function(){var d=document.querySelector(a.getAttribute('href'));if(d)d.open=true}});
});})();
"""


_KINDS = {
    "deepdive": ("정밀 대조", "논문 하나 × 코드 범위 하나 · 비공개", "아홉 절"),
    "versus": ("맞대기", "방법 × 논문 하나 · 비공개", "일곱 절"),
    "reports": ("회차 보고", "지난 런 이후 바뀐 것 · 비공개", "여덟 절"),
}


def _kind(path: str) -> str | None:
    folder = os.path.basename(os.path.dirname(os.path.abspath(path)))
    return folder if folder in _KINDS else None


def _runs_nav(path: str) -> str:
    here = os.path.basename(path)[:-3]
    days = sorted(os.path.basename(p)[:-3] for p in glob.glob(os.path.join(os.path.dirname(path), "*.md")))
    if here not in days:
        return ""
    k = days.index(here)
    prev = f'<a href="{days[k - 1]}.html">← {days[k - 1]}</a>' if k else "<span></span>"
    nxt = f'<a href="{days[k + 1]}.html">{days[k + 1]} →</a>' if k + 1 < len(days) else "<span></span>"
    return f'<div class="dx-runs">{prev}{nxt}</div>'


def render(path: str) -> tuple[str, list[str]]:
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    name = os.path.basename(path)
    kind = _kind(path) or "deepdive"
    noun, eyebrow, spine = _KINDS[kind]
    # `<id>--<alias>.md` for a versus note, `<id>--<alias>--<scope>.md` for a deep dive.
    parts = name[:-3].split("--") if re.match(r"^\d{4}\.\d{5}--", name) else []
    ctx = Context(os.path.dirname(os.path.dirname(os.path.abspath(path))), parts[0] if parts else "", kind,
                  parts[2] if kind == "deepdive" and len(parts) == 3 else "")

    h1 = lines[0][2:] if lines and lines[0].startswith("# ") else name
    if kind == "reports":
        heading, thesis, alias, meta = esc(h1), "", "", []
    else:
        pair, _, thesis = h1.partition(" — ")
        alias, _, scope_name = pair.partition(" × ")
        heading = (f'{esc(alias)}<span class="x">×</span>{esc(scope_name)}' if scope_name
                   else f'{esc(alias)}<span class="x">·</span><small>{esc(ctx.paper_id)}</small>')
        meta_raw = next((ln for ln in lines[1:] if ln.strip()), "")
        meta = _META.findall(meta_raw) if not meta_raw.startswith("## ") else []
        if kind == "versus":
            claims = re.search(r"Claims: ([^·]*)", meta_raw)
            meta = [(k, v) for k, v in meta if k != "Claims"]
            if claims and claims.group(1).strip():
                meta.insert(1, ("Claims", claims.group(1).strip()))

    secs: list[tuple[str, str, list[str]]] = []
    for raw in lines[1:]:
        h = _H2.match(raw)
        if h:
            secs.append((h.group(1), h.group(2).strip(), []))
        elif secs:
            secs[-1][2].append(raw)

    lay = _LAYOUT[kind]
    problems: list[str] = []
    body, toc = [], []
    for num, title, sec in secs:
        bl = blocks(sec)
        n = sum(1 for b in bl if b[0] in ("bullet", "h3") and b[1] != "없음")
        if num in (lay["stages"], lay["ideas"]):
            n = sum(1 for b in bl if b[0] == "h3")
        toc.append(f'<a href="#s{num}"><span>{num}</span>{esc(title)}<small>{n or ""}</small></a>')
        body.append(f'<section id="s{num}"><h2><span>{num}</span>{esc(title)}</h2>'
                    f'{section(num, sec, ctx, problems, alias)}</section>')

    def chip(k: str, v: str) -> str:
        if k == "Claims":
            return f"<span>{esc(k)}<b>" + " ".join(_anchor(c.strip(), ctx) for c in v.split(",")) + "</b></span>"
        return f"<span>{esc(k)}<b>{esc(v)}</b></span>"

    chips = "".join(chip(k, v) for k, v in meta)
    title = h1 if kind == "reports" else (f"{alias} — {noun}")
    rel = os.path.join(os.path.basename(os.path.dirname(os.path.abspath(path))), name)
    page = f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<style>{_tokens()}{_CSS}</style>
<script>{_JS}</script></head>
<body><button class="dx-theme" type="button">밝게 / 어둡게</button>
<div class="dx-shell">
<nav class="dx-toc"><b>{noun} · {spine}</b>{"".join(toc)}</nav>
<main>
{_runs_nav(path) if kind == "reports" else ""}<div class="dx-eyebrow">{eyebrow}</div>
<h1>{heading}</h1>
{f'<p class="dx-thesis">{inline(thesis, ctx)}</p>' if thesis else ""}
{f'<div class="dx-meta">{chips}</div>' if chips else ""}
{"".join(body)}
<footer>{esc(rel)} 에서 그린 보기입니다. 고칠 때는 Markdown 을 고치고 다시 그립니다 — <code>python3 distinction/render-distinction.py {esc(rel)}</code></footer>
</main></div></body></html>
"""
    return page, problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("docs", nargs="*", help="versus/, reports/ or deepdive/ Markdown (default: every one in the folder)")
    ap.add_argument("-o", "--out", help="output path for a single document (default: beside it, .html)")
    args = ap.parse_args(argv)
    docs = args.docs
    if not docs:
        folder = os.environ.get("PROBE_PRIVATE_DIR", "")
        docs = [p for sub in _KINDS for p in sorted(glob.glob(os.path.join(folder, sub, "*.md")))] if folder else []
    if not docs:
        print("render-distinction: no document — pass a path or set PROBE_PRIVATE_DIR", file=sys.stderr)
        return 2
    if args.out and len(docs) != 1:
        print("render-distinction: -o takes one document", file=sys.stderr)
        return 2
    failed = False
    for doc in docs:
        if not os.path.isfile(doc) or _kind(doc) is None and not args.out:
            print(f"render-distinction: {doc} is not a versus/, reports/ or deepdive/ document", file=sys.stderr)
            failed = True
            continue
        page, problems = render(doc)
        if problems:
            for p in problems:
                print(f"render-distinction: {doc}: {p}", file=sys.stderr)
            failed = True
            continue
        out = args.out or os.path.splitext(doc)[0] + ".html"
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(page)
        print(out)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
