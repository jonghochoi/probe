"""Page assemblers."""

from __future__ import annotations

import html
import json
import re
from collections import Counter

from . import components as c
from . import corpus, primers, scouting, glance as glance_mod
from . import lineage
from .corpus import PILLAR_LABELS, PILLAR_NAMES, PILLAR_ORDER, Paper, main_figure
from .render import DocRenderer, _decorate_refs

# Pages serves a project site under /<repo>/. 404.html and `build-site.py
# serve` use this; every other page is depth-relative and needs no knowledge
# of where it is hosted.
SITE_BASE = f"/{c.REPO.split('/')[1]}/"
BLOB = f"{c.REPO_URL}/blob/main"
DISCUSSIONS_NEW = f"{c.REPO_URL}/discussions/new?category=paper-notes"

# How many rewrites one page of the list holds — the choices the menu at the
# end of the page strip offers. A browser with no script gets the whole list.
#
# The default is a page rather than the whole corpus: the list is the one part
# of this page that grows without limit, and a reader arriving at it should
# meet a screen of papers, not a year of them.
PAGE_SIZES = (10, 20, 30)
PAGE_DEFAULT = 10

# How large `assets/corpus-index.js` may get before it stops being a file every
# page can afford to carry. It is fetched once and cached across the whole site,
# so the ceiling is generous — but it grows with the corpus and nothing else
# here does, so the build says something rather than letting it drift.
CORPUS_INDEX_BUDGET = 100 * 1024


def corpus_index(papers: list[Paper], comps: list | None = None,
                 axes: dict | None = None, search_api: str = "") -> str:
    """`assets/corpus-index.js` — the corpus, as much of it as a row needs.

    One file for the whole site rather than a blob inlined into every page: the
    ⌘K palette opens from anywhere, so every page needs the index, and a shared
    asset is fetched once and cached for all of them. A `<script>` rather than
    JSON on the side, because `fetch` is blocked by CORS on `file://` and
    opening a built page directly has to keep working.

    Both surfaces that read it want the same fields. The palette searches the
    id, the title and the 연구 축, and shows the tagline under each title —
    which is also the only Korean any of those fields carry, since titles in
    this corpus are the paper's own English. 서재 turns a
    kept id back into a titled, taglined row with the same records.

    Both pillar vocabularies ride along so either surface can match a query
    against an axis without carrying the dicts: the Korean label because a
    reader reads it off the axis line and may type it here, and the English name
    because the papers themselves are English and a reader may type that
    instead. Neither is printed — a row marks its axes with the id, which is
    what the chips beside it are keyed to.

    **Two kinds, one payload.** `comparisons` sits beside `papers` because the
    palette is the only way to reach a comparison from a page that does not
    name it. The arrays stay separate rather than merging under a `kind`
    field: they are keyed differently (an arXiv id against a slug), they land
    at different depths, and 서재 reads only the first.

    A comparison carries the ids it compares, so typing an arXiv id finds both
    the paper and the comparisons that hold it.

    `axes` is what an axis chip's popup says (`decisions.pillar_cards()`, read
    by `pillar.js`): each pillar's introduction and the titles of its open
    questions. It rides here because every page has chips and every
    page already carries this file.

    `searchApi` is the semantic-search endpoint, present only when the build
    was given one: the palette's 의미 tab asks it, and every page carries the
    palette. Absent, the palette shows no tab and the site makes no request.
    """
    ordered = sorted(papers, key=lambda p: p.order_key, reverse=True)
    ranked = sorted(comps or [], key=lambda x: x.order_key, reverse=True)
    payload = {
        "pillars": PILLAR_NAMES,
        "pillarLabels": PILLAR_LABELS,
        "axes": axes or {},
        "papers": [
            {"id": p.stem, "title": p.title, "tagline": p.tagline,
             "pillars": p.filed, "date": p.date}
            for p in ordered
        ],
        "comparisons": [
            {"slug": x.slug, "title": x.title, "tagline": x.tagline,
             "pillars": x.pillars, "date": x.date,
             "of": x.paper_ids}
            for x in ranked
        ],
    }
    if search_api:
        payload["searchApi"] = search_api
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return f"window.ProbeIndex={body};\n"


def _page_sizes() -> str:
    """10편 · 20편 · 30편 — how much of the list one page holds.

    The menu at the end of the page strip; only the current choice shows until
    it is opened. The pressed state printed here is the default; `filter.js`
    moves it to whatever the hash or this browser's last choice says.
    """
    return "".join(
        f'<button type="button" data-size="{n}" '
        f'aria-pressed="{"true" if n == PAGE_DEFAULT else "false"}">{n}편</button>'
        for n in PAGE_SIZES
    )


def _pager(total: int) -> str:
    """The page strip under the list — every page it could ever need, at once.

    The number of pages depends on what the filter left standing, which is the
    reader's business and not the build's. Rendering the most it can take
    (`total` at the smallest page size) and letting the script hide the rest
    keeps the rule this page is built on: the script toggles `hidden` on nodes
    that already exist and never builds markup.

    The two `…` gaps sit at fixed positions — after the first page and before
    the last — so a long list windows down to `1 … 6 7 8 … 20` without any
    button having to be relabelled.
    """
    pages = -(-total // PAGE_SIZES[0]) if total else 1
    nums = []
    for n in range(1, pages + 1):
        if n == 2:
            nums.append('<span class="pggap" data-gap="lo" aria-hidden="true" hidden>…</span>')
        if n == pages and pages > 2:
            nums.append('<span class="pggap" data-gap="hi" aria-hidden="true" hidden>…</span>')
        nums.append(f'<button type="button" class="pgn" data-page="{n}" hidden>{n}</button>')
    return f"""<nav class="pager" data-pager aria-label="쪽 이동" hidden>
  <button type="button" class="pgstep" data-page-rel="-1">이전</button>
  <span class="pgnums">{"".join(nums)}</span>
  <button type="button" class="pgstep" data-page-rel="1">다음</button>
  <div class="psize" data-psize>
    <button type="button" class="psize-cur" data-psize-open aria-haspopup="true" aria-expanded="false" title="한 쪽에 몇 편">{c.icon("menu", 15)}<span data-psize-label>{PAGE_DEFAULT}</span><span class="psize-caret" aria-hidden="true">▾</span></button>
    <div class="psize-menu" role="group" aria-label="한 쪽에 몇 편" hidden>{_page_sizes()}</div>
  </div>
</nav>"""


# ── 첫 화면 ─────────────────────────────────────────────────────────────────
# The site's front door at its root: what came in lately, the axes it is
# filed under, and the dates coming up. No band and no title — the nav names
# the site, and the mascot's one line says where to start.
_COUNT_WORD = {2: "두", 3: "세", 4: "네", 5: "다섯", 6: "여섯", 7: "일곱"}


def _thesis(paper: Paper) -> str:
    """The rewrite's body H1 — its thesis line."""
    return next((l[2:].strip() for l in paper.body.splitlines() if l.startswith("# ")), "")


def _md_plain(md: str) -> str:
    """Markdown as plain text — links, emphasis and code marks taken off."""
    return re.sub(r"\]\([^)]*\)|[*`\[\]]", "", md)


def _mascot(line: str, ordered: list[Paper], cmps: list, run, monday: str) -> str:
    """The mascot and its line, with every other line it can say beside it.

    The build prints one line per costume `home.js` can put on it, each but
    the first `hidden`, and the script only swaps which one shows — so with
    no script the reader gets the plain mark and where to start this week.
    What it wears is the reader's business, not the build's: the dates a
    costume turns on (`data-new`, `data-run`, the 일정 rows' own) are read
    against the reader's own day and hour, and `data-new-key` — the newest
    piece's own path — against the one this browser last celebrated.

    The four track lines are what the mark cycles through when nothing calls
    for a costume: each names the newest thing on that track, and the
    ideation line points at the memo, the one place the site keeps a
    reader's own idea. `deadline` is printed empty; the script names the
    date it found.
    """
    def say(key: str, html: str) -> str:
        return f'<span data-say="{key}"{"" if key == "base" else " hidden"}>{html}</span>'

    def link(href: str, text: str) -> str:
        return f'<a href="{href}"><b>{c.esc(text)}</b></a>'

    says = [say("base", line)]
    new_attrs = ""
    if run:
        when = f"{int(run.date[5:7])}월 {int(run.date[8:10])}일"
        says.append(say("run", f"{link('s/index.html', when + ' 회차')}가 나왔어요. "
                               "연구 축마다 이번 주 읽을 논문을 골랐어요."))
        says.append(say("scout", f"{link('s/index.html', when + ' 회차')}에서 고른 논문 "
                                 f"{len(run.papers)}편이 기다려요."))
    if ordered:
        n_week = sum(1 for p in ordered if p.date >= monday)
        says.append(say("analysis", f"재작성본 {link('p/index.html', f'{len(ordered)}편')}이 쌓였어요."
                                    + (f" 이번 주에만 {n_week}편." if n_week else "")))
    if cmps:
        x = cmps[0]
        says.append(say("compare", f"비교 {link(f'c/{c.esc(x.slug)}/index.html', x.title)}. "
                                   "갈리는 자리만 모았어요."))
    says.append(say("idea", "읽다 떠오른 생각은 논문마다 메모로 남겨 둘 수 있어요."))
    latest = max([(p.date, display_alias(p), f"p/{c.esc(p.stem)}/index.html") for p in ordered[:1]]
                 + [(x.date, x.title, f"c/{c.esc(x.slug)}/index.html") for x in cmps[:1]],
                 default=None)
    if latest:
        new_attrs = f' data-new="{latest[0]}" data-new-key="{latest[2]}"'
        says.append(say("new", f"새 글이 올라왔어요. {link(latest[2], latest[1])}"))
    says.append(say("deadline", '<b data-dl-name></b>까지 <b data-dl-n></b>. 일정을 확인하세요.'))
    if ordered:
        says.append(say("night", f"늦었어요. 내일은 {link(f'p/{c.esc(ordered[0].stem)}/index.html', display_alias(ordered[0]))}부터 읽어요."))
    attrs = new_attrs + (f' data-run="{run.date}"' if run else "")
    return (f'<div class="hm-mascot" data-mascot{attrs}>'
            f'<span class="hm-mk" aria-hidden="true">{c.mark(64, wardrobe=True)}</span>'
            f'<p class="hm-bubble">{"".join(says)}</p></div>')


def _cmp_line(comp, papers_by_id: dict) -> str:
    """A comparison's fork on one line, as HTML — each paper's alias and its stance.

    The 최근 row under a rewrite says what that paper does, so the row under a
    comparison says what each of its papers does about the question: the
    divergence the title asks about. The alias is set apart from the stance,
    the way the fork's branch name is, so the line reads as papers and not as
    one sentence. A comparison whose stances cannot pair with its papers prints
    its problem line instead.
    """
    if len(comp.stances) != len(comp.paper_ids):
        return c.esc(comp.problem or comp.tagline)
    return " · ".join(
        f'<span class="hm-a">{c.esc(display_alias(papers_by_id[pid]) if pid in papers_by_id else pid)}</span> '
        f"{c.esc(stance)}"
        for pid, stance in zip(comp.paper_ids, comp.stances))


def home_page(papers: list[Paper], comps: list, runs: list, events: list,
              today: str) -> str:
    """첫 화면 — one line from the mascot, then 최근 and 연구 축 side by
    side, then 일정.

    최근 is one of each kind first — the newest rewrite, the run's first
    recommendation, the newest comparison — and on a wide screen the rest of
    the latest under them. 연구 축 counts each axis's rewrites, what the
    newest run surfaced on it, and what came in this week. 일정 is the rows of
    `context/EVENTS.md` that have not ended as of the build; `home.js` counts
    the days to each against the reader's own date and drops what has passed
    since.
    """
    import datetime as _dt
    ordered = sorted(papers, key=lambda p: p.order_key, reverse=True)
    cmps = sorted(comps, key=lambda x: x.order_key, reverse=True)
    run = runs[0] if runs else None
    first, more = scout_split(run) if run else ([], [])
    tops = [p for p in first + more if p.lead.full]
    by_id = {p.stem: p for p in papers}

    def li(kind: str, when: str, href: str, title: str, sub: str, extra: bool) -> str:
        sub = f'<span class="hm-s">{sub}</span>' if sub else ""
        return (f'<li{" class=\"hm-x\"" if extra else ""}><a href="{href}">'
                f'<span class="hm-k">{kind}<small>{c.esc(when)}</small></span>'
                f'<b>{c.esc(title)}</b>{sub}</a></li>')

    feed = ([("분석", p.date, f"p/{c.esc(p.stem)}/index.html", display_alias(p), c.esc(p.tagline)) for p in ordered[:3]]
            + [("탐색", run.date, f"s/index.html#p-{c.esc(p.paper_id)}", p.alias, c.esc(_md_plain(p.gist)))
               for p in tops[:2]]
            + [("비교", x.date, f"c/{c.esc(x.slug)}/index.html", x.title, _cmp_line(x, by_id))
               for x in cmps[:1]])
    feed.sort(key=lambda f: f[1], reverse=True)
    lean = [next(f for f in feed if f[0] == k) for k in ("분석", "탐색", "비교")
            if any(f[0] == k for f in feed)]
    feed_html = ("".join(li(k, _md_date(d) + (" 회차" if k == "탐색" else ""), h, t, s, False)
                         for k, d, h, t, s in lean)
                 + "".join(li(k, _md_date(d) + (" 회차" if k == "탐색" else ""), h, t, s, True)
                           for k, d, h, t, s in feed if (k, d, h, t, s) not in lean))

    # This week is the week of the newest rewrite, Monday on.
    newest = _dt.date.fromisoformat(ordered[0].date) if ordered else _dt.date.fromisoformat(today)
    monday = (newest - _dt.timedelta(days=newest.weekday())).isoformat()
    filed = Counter(k for p in ordered for k in p.filed)
    week = Counter(k for p in ordered if p.date >= monday for k in p.filed)
    scouted = Counter(k for p in (run.papers if run else []) for k in p.pillars)
    pillars = "".join(
        f'<li><span class="hm-pchip">{c.pillar_chips([k])}</span><b>{c.esc(PILLAR_LABELS[k])}</b>'
        + (f'<span class="hm-pnew">이번 주 +{week[k]}</span>' if week[k]
           else '<span class="hm-pnew is-zero">이번 주 0</span>')
        + f'<span class="hm-pn">분석 {filed[k]} · 이번 탐색 {scouted[k]}</span></li>'
        for k in PILLAR_ORDER if k in PILLAR_LABELS and filed.get(k))

    upcoming = [e for e in events if e.end >= today][:6]

    def when(e) -> str:
        span = _md_date(e.start) if e.start == e.end else f"{_md_date(e.start)}–{_md_date(e.end)}"
        return span + (f" · {e.place}" if e.place else "")

    def dday(e) -> str:
        n = (_dt.date.fromisoformat(e.start) - _dt.date.fromisoformat(today)).days
        return "진행 중" if n <= 0 else f"D-{n}"
    evs = "".join(
        f'<a class="hm-ev {e.kind}{" hm-x" if i >= 4 else ""}" href="{c.esc(e.url)}" target="_blank" '
        f'rel="noopener" data-start="{e.start}" data-end="{e.end}">'
        f'<span class="hm-dd" data-dday>{dday(e)}</span><b>{c.esc(e.name)}</b>'
        f'<span>{c.esc(when(e))}</span></a>'
        for i, e in enumerate(upcoming))
    events_html = (f'<section class="hm-blk" data-events><h2 class="hm-h">일정'
                   f'<span class="hm-sub">학회 · 투고 마감</span></h2>'
                   f'<div class="hm-evs">{evs}</div></section>' if evs else "")

    line = ""
    if ordered:
        p = ordered[0]
        thesis = _thesis(p)
        line = (f'이번 주엔 <b>{c.esc(display_alias(p))}</b>부터 읽어 보세요.'
                + (f" “{c.esc(_md_plain(thesis))}”" if thesis else ""))
    mascot = _mascot(line, ordered, cmps, run, monday) if line else ""
    n_axes = _COUNT_WORD.get(len(PILLAR_NAMES), str(len(PILLAR_NAMES)))

    body = f"""<main class="hm">
  {mascot}
  <div class="hm-two">
    <section class="hm-blk"><h2 class="hm-h">최근<span class="hm-sub">분석 · 탐색 · 비교</span></h2>
      <ul class="hm-feed">{feed_html}</ul></section>
    <section class="hm-blk"><h2 class="hm-h">연구 축<span class="hm-sub">{n_axes} 갈래</span></h2>
      <ul class="hm-pl">{pillars}</ul></section>
  </div>
  {events_html}
</main>
"""
    return c.page(
        title="PROBE",
        body=body,
        depth=0,
        description="손 조작 연구를 고르고, 풀어 쓰고, 나란히 놓는 곳 — 최근 글과 연구 축, 학회 일정",
        scripts=["brand.js", "home.js"],
        extra_head=f'<link rel="stylesheet" href="{c.asset("assets/home.css")}">',
        body_attrs="data-home",
    )


GAP_ROWS = 12


def _gap_title(name: str, title: str) -> str:
    """`title` less a leading `name:` — the row prints the name just before it."""
    head, sep, rest = title.partition(":")
    return rest.strip() if sep and head.strip().casefold() == name.casefold() else title


def _gaps(graph: lineage.Graph | None, titles: dict[str, str]) -> str:
    """빈자리 — under the list of what the corpus holds, what it leans on and
    does not hold (`lineage.gaps`).

    A row is the paper, how many rewrites stand on it, and those rewrites by
    name — each a link to its own 계보 tab, where the paper sits among that
    rewrite's ancestors. The paper is the name its rails give it with its
    arXiv title after it (`titles`, from `arxivtitles`), less a leading
    `name:` the title repeats; a paper the cache has no title for prints the
    name alone. The rewrites' names are printed whole, so a browser with no
    script reads every one; `filter.js` folds them to one line and a `+N`
    chip, whose tooltip names the rest and whose click opens them.
    A partial build has no graph and prints none.
    """
    rows = lineage.gaps(graph)[:GAP_ROWS] if graph else []
    if not rows:
        return ""
    items = "".join(
        f'<li class="tl-row"><span class="tl-id">{len(on)}편</span>'
        f'<span class="tl-main"><span class="tl-t">{c.esc(node.name)}'
        + (f'<span class="tl-full" title="{c.esc(titles[node.id])}">'
           f'{c.esc(_gap_title(node.name, titles[node.id]))}</span>'
           if node.id in titles else '')
        + '</span>'
        f'<span class="tl-g gap-on" data-gapnames><span class="gap-names">' + " ".join(
            f'<span class="gap-n"><a href="{c.esc(n.id)}/index.html#lin">'
            f'{c.esc(n.name)}</a></span>' for n in on)
        + '</span><button type="button" class="gap-more" aria-expanded="false" hidden>'
        '</button></span></span>'
        f'<a class="tl-id" href="https://arxiv.org/abs/{node.id}" target="_blank" '
        f'rel="noopener noreferrer">arXiv {node.id}</a></li>'
        for node, on in rows)
    return (
        '<section class="gaps"><h2 class="gaps-h">빈자리'
        '<span>아직 안 쓴 선행 논문</span></h2>'
        '<div class="tl-head"><span>후속</span><span>논문</span>'
        f'<span>원문</span></div><ol class="tl">{items}</ol></section>')


def _axis_chip(key: str, n: int) -> str:
    """One axis on the analysis and comparison lines — swatch, code, count.

    The axis name rides in the tooltip and the accessible name rather than the
    chip, so the line holds every axis on one row at any width.
    """
    label = PILLAR_LABELS.get(key, "축 미지정")
    return (f'<button type="button" class="rail-item pillar" data-p="{c.esc(key)}" '
            f'data-facet-pillar="{c.esc(key)}" aria-pressed="false" '
            f'title="{c.esc(f"{key} · {label}")}" aria-label="{c.esc(f"{key} {label} {n}편")}">'
            f'<span class="sw"></span><b>{c.esc(key)}</b>'
            f'<span class="rn">{n}</span></button>')


def analysis_page(papers: list[Paper], katex=None,
                 partial: bool = False, graph: lineage.Graph | None = None,
                 gap_titles: dict[str, str] | None = None) -> str:
    """The corpus index — one line of axes over one row per paper, newest first.

    The page opens on the list itself: the axes as a line over it (the only
    filter here — a word search is ⌘K's, from any page), then the rows, the
    newest at the top. Each row is the paper's title with its link icons, the
    tagline under it, and the axes it is filed under.

    Every row is server-rendered with its facets on `data-` attributes rather
    than hydrated from an inline JSON blob. That keeps the page fully readable
    with JavaScript off (the axis line and the page strip hide themselves, the
    rows stay, newest first, all of them), and the filter script only ever
    reorders and toggles `hidden` on nodes that already exist.

    The list is paged — `PAGE_DEFAULT` rewrites at a time, the strip's menu
    offering `PAGE_SIZES` — because it is the one part of this page that grows
    with the corpus.

    Order is `Paper.order_key` — the order the rewrites landed on `main`, which
    is the order a reader watched them appear — and the rows carry that key on
    `data-order`, so the script's newest-first reproduces this list rather than
    a near-miss of it.
    """
    ordered = sorted(papers, key=lambda p: p.order_key, reverse=True)

    # Taglines are authored markdown — emphasis is what makes a line
    # scannable, and a line that opens with math is common enough that
    # escaping it would publish backticks. `decisions` is left
    # empty on purpose: a `D#` tooltip needs `paper.js`, which this page does
    # not load.
    renderer = DocRenderer(katex) if katex is not None else None

    # Counted over the axes a paper is *filed* under — `Paper.filed`, the two
    # its row prints — because that is what the axis line selects on. Count
    # one set and filter on another and the line promises rows the click
    # never delivers.
    filed = Counter(p for paper in ordered for p in paper.filed)

    rail_pillars = "".join(
        _axis_chip(k, filed[k])
        for k in PILLAR_ORDER if filed.get(k)
    )

    rows = "".join(_row(p, renderer) for p in ordered)

    head = c.mast(
        eyebrow="Dexterous manipulation",
        title="분석, 원문을 읽기 좋게 풀어 둡니다",
        count=f"{len(ordered)}편" + (f" · 최근 {ordered[0].date}" if ordered else ""),
    )

    # The axes as one line over the list — the analysis page's only filter.
    # The icon cell on its left names the line without a word; the right end
    # carries the count the filter leaves standing.
    line = (
        '<div class="pline" data-filters role="group" aria-label="연구 축으로 거르기">'
        f'<span class="pline-ic" aria-hidden="true">{c.icon("layers", 18)}</span>'
        f'<div class="pline-items" data-pline>{rail_pillars}</div>'
        f'<span class="pline-stat"><span data-result-count>{len(ordered)}편</span>'
        + (f'<span data-corpus-when> · 최근 {c.esc(ordered[0].date)}</span>' if ordered else "")
        + "</span></div>"
    )

    body = f"""{head}

<div class="deck">
  <main class="corpus" data-corpus>
    {line}
    {_first_run() if not ordered else ""}
    {_resume()}
    <div class="listhead" data-listhead{" hidden" if len(ordered) < 2 else ""}>
      <span class="lh-star"></span><span>재작성</span><span>arXiv</span><span>논문 · 한 줄</span><span>연구 축</span>
    </div>
    <p class="corpus-partial" data-partial hidden>
      모든 단어를 포함하는 논문이 없어, <b>일부만 일치</b>하는 논문을 관련도순으로 보여줍니다.
    </p>
    <div class="rows" data-rows>{rows}</div>
    {_pager(len(ordered))}
    <p class="corpus-empty" data-empty hidden>
      조건에 맞는 논문이 없습니다. <button type="button" class="linkish" data-reset>필터를 지워</button> 보세요.
    </p>
    {_gaps(graph, gap_titles or {})}
  </main>
</div>
"""
    return c.page(
        title="PROBE",
        here="papers",
        description=f"Dexterous manipulation 논문 {len(ordered)}편을 원문에서 다시 쓴 한글 판",
        body=body,
        depth=1,
        scripts=["shelf.js", "filter.js"],
        # `llms.txt` is where an agent handed this URL finds the corpus as
        # data; a partial build writes none, so it links none.
        extra_head=(f'<link rel="stylesheet" href="{c.asset("../assets/index.css")}">'
                    + ("" if partial else
                       '\n<link rel="alternate" type="text/plain" title="llms.txt" href="../llms.txt">')),
    )


def _resume() -> str:
    """One line back to wherever the reader put a 책갈피.

    Above the list, because it is the only thing on the page that is about
    this reader rather than about the corpus, and because a reader who left a
    mark came back for it. One line and no more: a stack of the reader's
    unfinished business would push the list off the first screen.

    That is what makes the chips carry the arXiv id rather than the title —
    three titles do not fit on a line, three ids always do, and the id is
    fixed-width so the row does not jump about as marks come and go. The
    section's name rides along as the part a reader actually recognises, and
    the paper's title is on the chip's `title`, one hover away.

    Everything printed was written into the mark itself, so the strip renders
    with no corpus lookup and stays right for a paper that has left the site.
    Shipped empty and hidden; `shelf.js` fills it or leaves it alone.
    """
    return (
        '<div class="resume" data-resume="" hidden>'
        '<span class="resume-k">책갈피</span>'
        '<span class="resume-chips" data-resume-chips></span>'
        '<a class="resume-all" data-resume-all href="../shelf/index.html#marks">'
        '서재 →</a></div>'
    )


def _first_run() -> str:
    """Shown when no rewrite exists yet.

    The site starts empty by design — it is exactly the set of rewrites — so
    the first visit needs to say that rather than look broken.
    """
    return (
        '<p class="corpus-empty">아직 재작성한 논문이 없습니다.<br>'
        '<code>/analyze &lt;arXiv id&gt;</code> 로 첫 편을 추가하면 '
        "여기에 첫 줄이 생깁니다.</p>"
    )


def _facets(paper: Paper) -> str:
    """The `data-` attributes the filter script reads off a row.

    The two haystacks are built and compacted in `corpus` — the row carries
    them ready to match, so a query costs the script a substring test and
    nothing else (`corpus.HAY_MAX` bounds what one row can weigh).
    """
    return (
        f'data-id="{c.esc(paper.stem)}" '
        f'data-pillars="{c.esc(" ".join(paper.filed))}" '
        f'data-order="{c.esc(paper.order_token)}" '
        f'data-key="{c.esc(paper.search_key)}" '
        f'data-hay="{c.esc(paper.search_hay)}"'
    )


def _star(paper: Paper) -> str:
    """The star on a row of the analysis list.

    Server-rendered hollow; `shelf.js` presses it and `index.css` fills the one
    path from `currentColor`. Which papers are starred is the reader's, not the
    corpus's, and the build has no way to know it. The
    title rides along because the shelf keeps a copy of it — a starred paper
    that later leaves the corpus still lists under a name in 서재 rather than
    as a bare id. Nothing without JavaScript can toggle it, so the button
    removes itself there (`index.css`) instead of sitting inert.
    """
    return (
        f'<button type="button" class="rowstar" data-star="{c.esc(paper.stem)}" '
        f'data-star-title="{c.esc(paper.title)}" aria-pressed="false" '
        f'aria-label="즐겨찾기">{c.icon("star", 15)}</button>'
    )


def _size(paper: Paper) -> str:
    """본문 27분 · 용어 18 · 그림 5 — how much of a sit this is.

    Printed before the reader commits, which is the only moment the number is
    worth anything. All three come from what the rewrite already declares.
    """
    bits = [f"본문 {paper.read_minutes}분"]
    if paper.term_count:
        bits.append(f"용어 {paper.term_count}")
    if paper.figure_count:
        bits.append(f"그림 {paper.figure_count}")
    return " · ".join(bits)


def _md(renderer, text: str) -> str:
    """Authored markdown where there is a renderer, escaped text where not."""
    return renderer.inline(text) if renderer is not None else c.esc(text)


def _row_links(paper: Paper, cls: str) -> str:
    """The paper's outside links as icons alone — arXiv, project, code, model.

    The label rides on `title` and `aria-label`, so the row spends a glyph's
    width on each rather than a word's.
    """
    return "".join(
        f'<a class="{cls}" href="{c.esc(url)}" target="_blank" rel="noopener" '
        f'title="{c.esc(label)}" aria-label="{c.esc(label)}">{c.src_mark(kind)}</a>'
        for kind, label, url in paper.links
    )


def _row(paper: Paper, renderer=None) -> str:
    """One paper, one line.

    The title is the link to the paper, and its `::after` stretches over the
    title and the tagline so the whole block still opens it; the link icons sit
    above that box right after the title. A link cannot hold a link, which is
    why the title rather than the block is the anchor. On a phone the icons
    move to the axis chips' line, where the row has room for them.
    """
    # The axes the paper is filed under, which are also the ones the axis line
    # counts and filters on — the chips on a row are what a reader checks the
    # line's number against.
    pillars = c.pillar_chips(paper.filed)
    links = _row_links(paper, "row-link")
    # The figure a pointer resting on the row previews (`filter.js`): the
    # paper's overview, at the URL its own page shows it from.
    fig = main_figure(paper.body)
    figattrs = (f' data-fig="{c.esc(fig["url"])}" data-fig-cap="{c.esc(fig["caption"])}" '
                f'data-fig-src="{c.esc(fig["source"])}"' if fig else "")
    return f"""<article class="row" data-card{figattrs}
  data-read-of="{c.esc(paper.stem)}" {_facets(paper)}>
  {_star(paper)}
  <span class="row-when">{c.esc(paper.date[5:] or paper.date)}</span>
  <span class="row-id">{c.esc(paper.stem)}</span>
  <div class="row-main">
    <span class="row-title"><a class="row-go" href="{c.esc(paper.stem)}/index.html">{c.esc(paper.title)}</a>{f'<span class="row-links">{links}</span>' if links else ""}</span>
    <span class="row-tagline">{_md(renderer, paper.tagline)}</span>
  </div>
  <span class="row-pillars">{pillars}{f'<span class="row-links-m">{links}</span>' if links else ""}</span>
</article>"""


# The three lists 서재 holds, in the order a reader meets them: what they
# picked out, where they stopped, what they wrote down.
SHELF_TABS = (
    ("stars", "즐겨찾기", "star"),
    ("marks", "책갈피", "flag"),
    ("memos", "메모", "pencil"),
)


def shelf_page(papers: list[Paper]) -> str:
    """서재 — everything this browser has kept about the corpus.

    Rendered empty and filled from `localStorage`: stars, 읽음 marks and memos
    never reach the build, so there is nothing here to server-render but the
    frame. What turns a kept id back into a row with a link is `corpus_index()`,
    the same file the ⌘K palette searches — every page carries it, so this one
    needs no index of its own. A kept id missing from it is a paper that has
    left the corpus, and 서재 says so rather than dropping it.

    One kind at a time under underline tabs, each kind with its own icon —
    a star, a bookmark and a memo are three different things to have kept —
    and each as the analysis list's table. The page is also the export
    surface, and the only one: a shelf that lives in one browser profile
    reaches a second machine as a file or not at all. Export and import are
    rare, so they sit behind the ⋯ at the tab row's end. The two exports are
    printed `disabled`, because an empty shelf has nothing to write out and a
    file that downloads with nothing in it reports a success that did not
    happen; `hub.js` opens them the moment a count is non-zero.
    """
    tabs = "".join(
        f'<button type="button" role="tab" id="sh-t-{key}" aria-controls="sh-{key}" '
        f'aria-selected="{"true" if i == 0 else "false"}" data-shelf-tab="{key}">'
        f'{c.icon(icon, 16)}<b>{c.esc(label)}</b><span class="tab-n" data-tab-count>0</span></button>'
        for i, (key, label, icon) in enumerate(SHELF_TABS)
    )
    panels = "".join(
        f'<section id="sh-{key}" role="tabpanel" aria-labelledby="sh-t-{key}" '
        f'data-shelf-panel="{key}"{"" if i == 0 else " hidden"}></section>'
        for i, (key, _, _) in enumerate(SHELF_TABS)
    )
    menu = (
        '<div class="sh-more">'
        '<button type="button" class="sh-more-b" data-hub-more aria-haspopup="true" '
        'aria-expanded="false" aria-label="내보내기 · 가져오기" title="내보내기 · 가져오기">'
        f'{c.icon("more", 18)}</button>'
        '<div class="sh-menu" data-hub-menu hidden>'
        '<button type="button" data-hub-action="export-json" disabled>JSON 내보내기</button>'
        '<button type="button" data-hub-action="export-md" disabled>마크다운 내보내기</button>'
        '<label class="sh-menu-i">가져오기<input type="file" accept="application/json" '
        'data-hub-import hidden></label></div></div>'
    )

    head = c.mast(
        eyebrow="Kept in this browser",
        title="서재, 이 브라우저에만 남습니다",
    )

    body = f"""{head}

<div class="deck"><main class="shelf" data-hub>
  <div class="sh-tabs" role="tablist" aria-label="서재 보기">{tabs}<span class="filter-spacer"></span>{menu}</div>
  <p class="hub-status" data-hub-status aria-live="polite"></p>
  {panels}
  <noscript><p class="corpus-empty">서재는 브라우저에 저장되므로 JavaScript 가 필요합니다.</p></noscript>
</main></div>
"""
    return c.page(
        title="서재 · PROBE",
        here="shelf",
        description="즐겨찾기 · 책갈피 · 메모 — 이 브라우저에 담아 둔 논문과 읽던 자리",
        body=body,
        depth=1,
        scripts=["memo.js", "shelf.js", "hub.js"],
        extra_head=f'<link rel="stylesheet" href="{c.asset("../assets/index.css")}">',
    )


def not_found_page(papers: list[Paper]) -> str:
    """The page an old or mistyped link lands on.

    It offers the two ways a reader usually recovers: the palette, for the
    paper they came for, and the newest rewrites, for a link that pointed at
    something recent. Both are absolute, since Pages serves this file at the
    bad URL's own depth.
    """
    newest = sorted(papers, key=lambda p: p.order_key, reverse=True)[:5]
    recent = "".join(
        f'<li><a href="{SITE_BASE}p/{c.esc(p.stem)}/index.html">{c.esc(p.title)}</a></li>'
        for p in newest
    )
    body = f"""<main class="hub notfound">
  <h1>404</h1>
  <p>이 주소에는 아무것도 없습니다. 찾던 논문은 제목의 한 단어나 arXiv id 로 찾을 수 있습니다.</p>
  <p class="notfound-acts"><button type="button" class="notfound-find" data-cmdk-open>논문 찾기</button>
    <a href="{SITE_BASE}p/">논문 목록으로</a></p>
  {f'<h2 class="notfound-h">최근 재작성본</h2><ul class="notfound-list">{recent}</ul>' if recent else ""}
</main>
"""
    return c.page(
        title="404 · PROBE",
        body=body,
        depth=0,
        base=SITE_BASE,
        extra_head=f'<link rel="stylesheet" href="{c.asset(SITE_BASE + "assets/index.css")}">',
    )


# The tabs, in the order a reader meets them — the one-screen 요약 first,
# because a reader arrives at a paper page not yet knowing whether the paper is
# worth the long read, and that is the question the short surface answers.
#
# 비교 and 계보 are not further readings of this paper: 요약 and 상세 say how
# much of the paper a surface carries, 비교 and 계보 what it stands among. They
# are also the tabs that are not always there — each appears only when there
# is something behind it, and a tab that is empty for most of the corpus is
# furniture.
TABS = (("glance", "요약"), ("full", "상세"), ("cmp", "비교"), ("lin", "계보"))
# The tabs printed only when there is something behind them, each with its count.
COUNTED_TABS = ("cmp", "lin")


def paper_page(paper: Paper, katex, decisions: dict,
               problems: list[str] | None = None,
               neighbours: list[Paper] | None = None,
               comparisons: list | None = None,
               papers_by_id: dict | None = None,
               citers: list[Paper] | None = None,
               graph: lineage.Graph | None = None) -> str:
    """One paper's rewrite — two tabs cut from one source file.

    The brief and the body are two readings of the same paper for two
    different sits, so they are two panels of one page rather than two pages:
    the header, the resource links and the memo panel are the same paper's,
    and a reader switching surface has not left the paper.

    The comparisons holding this paper are the third tab rather than a footer
    under one of the other two. A footer is read by whoever reaches the foot of
    the surface it sits under, which on a long 상세 is few and on 요약 is a
    surface the section does not belong to — while the tab strip is on screen
    from the first pixel and carries its own count, so the answer to "has this
    been argued against anything" arrives before the read rather than after it.

    계보 is the fourth for the same reason: what the paper stands on and what
    stands on it is a question a reader brings to the paper, not one they
    reach the foot of 상세 to ask.
    """
    by_id = papers_by_id or {}
    renderer = DocRenderer(
        katex, decisions=decisions,
        siblings={pid: p.title for pid, p in by_id.items()},
        self_id=paper.stem,
    )
    # The tagline prints in the header, not the body; it rides as the lead
    # only so the body's literal-text checks (`analysis/AUTHORING.md` §3) read
    # it too.
    tagline = renderer.inline(paper.tagline) if paper.tagline else ""
    renderer.lead_html = tagline
    rendered = renderer.render(paper.article or paper.body)

    urls = corpus.figure_urls(paper.body)
    glance_html = glance_mod.render(paper.glance, renderer, katex, urls)
    if glance_html:
        renderer.check_text(paper.body, glance_html)
    if problems is not None:
        problems.extend(
            f"analysis/{paper.stem}.md: {p}" for p in renderer.problems
        )

    comps = comparisons or []
    lin_html, lin_n = _lin_panel(paper, graph)
    body = f"""{_header(paper, tagline)}
{_tabstrip({"cmp": len(comps), "lin": lin_n}, _src_group(paper) + _acts(paper))}
<div class="panel wide" id="p-glance" role="tabpanel" aria-labelledby="t-glance">
  {glance_html or _missing("요약")}
</div>
<div class="panel" id="p-full" role="tabpanel" aria-labelledby="t-full" hidden>
  {_act_strip(renderer.toc)}
  <div class="shell">
    <aside class="toc">{_toc(renderer.toc)}</aside>
    <main class="article">
      <section class="view">{rendered}</section>
      {_related(neighbours or [])}
      {_citers(citers or [])}
    </main>
  </div>
</div>
{_cmp_panel(paper, comps, by_id)}
{lin_html}
{c.mark_fab()}
{c.memo_panel(paper.stem, paper.title, f"{BLOB}/analysis/{paper.stem}.md", DISCUSSIONS_NEW)}
"""
    return c.page(
        title=f"{paper.title} · PROBE",
        here="papers",
        description=paper.preview,
        body=body,
        depth=2,
        scripts=["paper.js", "memo.js", "shelf.js"] + (["lineage.js"] if lin_n else []),
        # The source an agent should read instead of this page's markup.
        extra_head=(
            f'<link rel="alternate" type="text/markdown" href="{c.RAW_URL}/analysis/{paper.stem}.md">'
            + (f'\n<link rel="stylesheet" href="{c.asset("../../assets/lineage.css")}">'
               if lin_n else "")),
    )


def _acts(paper: Paper) -> str:
    """즐겨찾기 and 읽음, for this paper, in this browser.

    Both are server-rendered in their empty state and corrected by `shelf.js`
    on load — the build cannot know either one. 읽음 is the reader's claim and
    only ever theirs: neither opening a page nor scrolling to the end of it is
    evidence that it was read, so nothing marks it on their behalf.

    They are glyphs, a pair of round buttons at the right end of the action
    bar, past a hairline from the links: the bar is one line on a phone only
    while nothing in it is a word it can do without, and a star and a check are
    the two marks this site already draws for these two states. What each does is the button's
    accessible name, and `shelf.js` keeps its `aria-pressed` in step with the
    state.
    """
    return f"""<div class="paper-acts" data-paper-acts
     data-paper-id="{c.esc(paper.stem)}" data-paper-title="{c.esc(paper.title)}">
  <button type="button" class="act-btn" data-star="{c.esc(paper.stem)}"
          data-star-title="{c.esc(paper.title)}" aria-pressed="false"
          aria-label="즐겨찾기" title="즐겨찾기">{c.icon("star", 16)}</button>
  <button type="button" class="act-btn" data-read-toggle aria-pressed="false"
          aria-label="읽음으로 표시" title="읽음으로 표시">{c.icon("check", 16)}</button>
</div>"""


def _tabstrip(counts: dict[str, int], tools: str = "") -> str:
    """The tabs, and at the strip's right end the paper's links out and its
    즐겨찾기 · 읽음 pair. Server-rendered and `hidden`-toggled, so the page is
    readable with JavaScript off — the first panel stays open and the rest are
    reachable by their anchors.

    The links and the pair sit on the strip rather than on a line of their own
    under the byline: the header is what the paper is, the strip is what a
    reader does with it, and one line holds both the surface switch and the
    controls.

    비교 and 계보 are printed only when there is something behind them, and
    each carries its count: the number is the whole reason to look, and a tab
    that made the reader click to find out it says zero would have spent their
    click to tell them nothing.
    """
    buttons = []
    for i, (key, label) in enumerate(TABS):
        if key in COUNTED_TABS and not counts.get(key):
            continue
        count = (f'<span class="cnt">{counts[key]}</span>' if key in COUNTED_TABS else "")
        buttons.append(
            f'<button type="button" class="tab" role="tab" id="t-{key}" '
            f'aria-controls="p-{key}" aria-selected="{"true" if i == 0 else "false"}" '
            f'data-tab="{key}">{c.esc(label)}{count}</button>'
        )
    return (f'<div class="tabs-wrap"><div class="tabs">'
            f'<div class="tab-list" role="tablist" aria-label="논문 보기 방식">{"".join(buttons)}</div>'
            + (f'<div class="tab-tools">{tools}</div>' if tools else "")
            + '</div></div>')


def _act_strip(entries: list[dict]) -> str:
    """The four acts as milestones on one line under the tab strip, where the
    contents rail has no room — a tablet's width and below, or a wide screen
    with no pointer to reach the rail with. It sticks under the tab strip,
    fills the dot of the act being read, and ends in the 목차 button that opens
    the whole contents from below; with no script the button is not printed
    live and the links still jump.

    The milestones scroll in a box of their own and the button stands outside
    it, a glyph alone: a comparison's five acts outrun a phone's width, and a
    button scrolled off the edge is one the reader never learns is there.
    """
    acts = [e for e in entries if e.get("kind") == "act"]
    if not acts:
        return ""
    links = "".join(
        f'<a class="as-link" href="#act-{c.esc(e["n"])}">'
        f'<i class="as-dot" aria-hidden="true"></i>{c.esc(e["label"])}</a>'
        for e in acts
    )
    return (f'<nav class="actstrip" aria-label="막"><div class="actstrip-in">'
            f'<div class="as-links">{links}</div>'
            '<button type="button" class="as-toc" data-toc-open hidden '
            f'aria-label="목차" title="목차">{c.icon("list", 17)}</button></div></nav>')


def _missing(name: str) -> str:
    """A surface the rewrite does not carry.

    Printed rather than silently empty: the build already reported it, and a
    reader who clicked the tab deserves to know the tab is empty because the
    rewrite is incomplete, not because the page broke.
    """
    return (f'<p class="corpus-empty">이 재작성본에는 아직 {c.esc(name)} 섹션이 '
            f'없습니다 — <code>/analyze &lt;id&gt;</code> 로 다시 씁니다.</p>')




def _node_href(up: str, frag: str = ""):
    """Where a 계보 node goes: the rewrite's page, or arXiv for a paper without
    one. `frag` names the tab a rewrite's page should open on."""
    def href(node: lineage.Node) -> str:
        if node.paper:
            return f"{up}p/{node.id}/index.html{frag}"
        return f"https://arxiv.org/abs/{node.id}"
    return href


def _lineage_data(graph: lineage.Graph, middle: str, href) -> str:
    """One paper and the papers it is joined to, as `assets/lineage.js` reads
    them: each neighbour with which side it stands on and whether a rail or
    only the prose joins it. Only `middle` carries its tagline — the middle
    card is the one place a tagline prints.
    """
    def record(nid: str, **more) -> dict:
        node = graph.nodes[nid]
        out = {"id": nid, "n": node.name, "l": node.lane, "h": href(node), **more}
        if node.paper is None:
            out["x"] = 1
        return out
    me = record(middle, t=graph.nodes[middle].paper.tagline)
    sides = [[record(n, r=int(edges[n] == lineage.RAIL)) for n in ids]
             for ids, edges in ((graph.parents(middle), graph.up.get(middle, {})),
                                (graph.children(middle), graph.down.get(middle, {})))]
    blob = json.dumps({"me": me, "before": sides[0], "after": sides[1]},
                      ensure_ascii=False, separators=(",", ":"))
    return blob.replace("</", "<\\/")


# An arrow leaving a box: the paper has no page here and the cell goes to arXiv.
_EXT_ICON = ('<svg viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" '
             'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
             '<path d="M6.5 3.5H3.5v9h9V9.5"/><path d="M9.5 3h3.5v3.5M13 3 7.5 8.5"/></svg>')


def _key_line(cls: str) -> str:
    """One of the two lines the 계보 tab draws, as its key prints it — the
    same stroke and arrowhead `lineage.css` gives the drawing's own."""
    return (f'<svg class="k-line{cls}" viewBox="0 0 34 10" width="34" height="10" aria-hidden="true">'
            '<path d="M1 5H26"/><path class="k-head" d="M25 1.5 32 5 25 8.5Z"/></svg>')


def _lin_panel(paper: Paper, graph: lineage.Graph | None) -> tuple[str, int]:
    """계보 — `(the panel, how many papers it joins this one to)`.

    The older papers this one is joined to on the left, the newer on the
    right, and nothing further out. The panel arrives as `lineage.near_svg`,
    every node a link; `assets/lineage.js` swaps in the same three columns as
    cells, which set the rail's papers apart from the ones only mentioned. A
    cell goes to that paper's own 계보, or to arXiv when the paper has no
    rewrite. The key over the drawing is the drawing's own marks in two
    groups — what a cell is, what a line is — so nothing in the tab is
    explained in a sentence. A paper with no edge, and any paper in a partial build, has
    no tab.
    """
    if not graph or paper.stem not in graph.nodes:
        return "", 0
    count = len(graph.parents(paper.stem)) + len(graph.children(paper.stem))
    svg = lineage.near_svg(graph, paper.stem, _node_href("../../", "#lin"))
    if not svg:
        return "", 0
    data = _lineage_data(graph, paper.stem, _node_href("../../", "#lin"))
    key = (
        '<div class="lin-key" aria-label="범례">'
        '<p><span><span class="lt-ax">P#</span>재작성본</span>'
        f'<span><span class="lt-ext">{_EXT_ICON}</span>arXiv 원문</span></p>'
        f'<p><span>{_key_line("")}계보</span><span>{_key_line(" is-text")}언급</span></p>'
        '</div>')
    return f"""<div class="panel wide" id="p-lin" role="tabpanel" aria-labelledby="t-lin" hidden>
  <section class="lin-tab" data-walk>
    {key}
    <div class="near-frame" data-walk-still>{svg}</div>
    <div class="lt-frame" hidden><div class="lt" id="lin-tree"></div></div>
    <script type="application/json" id="lin-data">{data}</script>
  </section>
</div>""", count


def _related(neighbours: list[Paper]) -> str:
    """The nearest rewrites, at the end of the one just read.

    Placed after the article rather than in the sidebar: it is a next step, not
    a navigation aid, and it should not compete with the table of contents
    while there is still text above it. Empty when nothing shares an
    open-question code or a pillar — see `corpus.related`.
    """
    if not neighbours:
        return ""
    items = "".join(
        f'<a class="rel-item" href="../{c.esc(p.stem)}/index.html">\n'
        f'  <span class="rel-p">{"".join(c.esc(x) + " " for x in p.filed)}</span>\n'
        f'  <span class="rel-title">{c.esc(p.title)}</span>\n'
        f'  <span class="rel-tagline">{c.esc(p.tagline)}</span>\n'
        f'  <span class="rel-size">{c.esc(_size(p))}</span>\n'
        f"</a>"
        for p in neighbours
    )
    return (
        '<section class="related">'
        '<h2 class="related-h">같은 갈래의 다른 글</h2>'
        f'<div class="rel-list">{items}</div>'
        "</section>"
    )


def _citers(citers: list[Paper]) -> str:
    """The rewrites that cite this paper, under the ones nearest to it.

    `_related` answers "what else is like this"; this answers "who leaned on
    it", which is the stronger signal of the two — a paper another rewrite
    argues from is already load-bearing in the corpus. The two lists overlap by
    design: a neighbour that also cites this paper belongs in both, because it
    is on the page for two different reasons.
    """
    if not citers:
        return ""
    items = "".join(
        f'<a class="rel-item" href="../{c.esc(p.stem)}/index.html">\n'
        f'  <span class="rel-p">{"".join(c.esc(x) + " " for x in p.filed)}</span>\n'
        f'  <span class="rel-title">{c.esc(p.title)}</span>\n'
        f'  <span class="rel-tagline">{c.esc(p.tagline)}</span>\n'
        f'  <span class="rel-size">{c.esc(_size(p))}</span>\n'
        f"</a>"
        for p in citers
    )
    return (
        '<section class="related">'
        '<h2 class="related-h">이 논문을 언급한 다른 글</h2>'
        f'<div class="rel-list">{items}</div>'
        "</section>"
    )


def _cmp_panel(paper: Paper, comps: list, papers_by_id: dict) -> str:
    """비교 — the comparisons that hold this paper, as their own surface.

    The other half of the track's constraint. A comparison never explains this
    paper, so the paper's page is where the detail stays — and this is the way
    back out, for a reader who wants to know what it was argued against.

    Each card names the papers standing beside it, with this one marked. Which
    papers a comparison put on the table is the first thing a reader wants and
    the one thing a title cannot carry: two comparisons can ask a similar
    question of entirely different papers. Marking this paper in the row is
    what makes it a position rather than a list — the cards run in `compares:`
    order, the same order the comparison's own columns run in.
    """
    if not comps:
        return ""
    cards = "".join(_cmp_card(paper, x, papers_by_id) for x in comps)
    return f"""<div class="panel wide" id="p-cmp" role="tabpanel"
     aria-labelledby="t-cmp" hidden>
  <section class="incmp">
    <p class="incmp-lead">
      이 논문이 다른 논문과 <strong>한 질문 아래 놓인 자리</strong>입니다.
      비교문은 갈리는 자리만 쓰고, 각 논문이 무엇을 하는지는 그 논문의 페이지에
      두고 링크로 갑니다.
    </p>
    <div class="incmp-list">{cards}</div>
  </section>
</div>"""


def _cmp_card(paper: Paper, comp, papers_by_id: dict) -> str:
    """One comparison, from this paper's side of it.

    The comparison as a fork, with this paper's branch marked — which is
    what makes the card a position rather than a list: not only that these
    papers were on one table, but which answer was this one's.
    """
    return (
        f'<a class="incmp-item" href="../../c/{c.esc(comp.slug)}/index.html">'
        f'<span class="incmp-when">{c.esc(comp.date)}</span>'
        f'<span class="incmp-t">{c.esc(comp.title)}</span>'
        f"{_fork(comp, papers_by_id, mark=paper.stem)}</a>"
    )


def _toc(entries: list[dict]) -> str:
    """The contents as milestones: each act a node on one line, its sections
    the stops under it.

    Built from the renderer's own heading pass rather than scraped from the DOM
    by `paper.js`: the act grouping is structure the renderer knows and the
    rendered HTML does not spell out. An act prints its short noun, its
    question in grey and how many sections it holds; a section prints its
    number in the whole document and its Korean title — the English keyword
    line stays on the heading in the body, where it has the width.

    Server-side means the contents survive with JavaScript off, and then they
    print whole. With a script, the rail on a wide screen shows the four acts
    and only the section being read and the 책갈피 one, and the whole list
    opens over the article when the reader reaches for it (`paper.js`).
    """
    if not entries:
        return ""
    groups: list[tuple[dict | None, list[dict]]] = []
    for entry in entries:
        if entry.get("kind") == "act":
            groups.append((entry, []))
        else:
            if not groups:
                groups.append((None, []))
            groups[-1][1].append(entry)
    out: list[str] = []
    num = 0
    for act, rows in groups:
        head = ""
        if act:
            head = (
                f'<a class="ms-act" href="#act-{c.esc(act["n"])}">'
                f'<span class="ms-node">{c.esc(act["n"])}</span>'
                f'<span class="ms-at"><b>{c.esc(act["label"])}</b>'
                + (f'<span>{c.esc(act["sub"])}</span>' if act.get("sub") else "")
                + f'</span><span class="ms-cnt">{len(rows)}</span></a>'
            )
        items = []
        for entry in rows:
            # Act 0's cards are not stops in the argument, so they take no
            # number and the argument's own count starts at 1.
            if not entry.get("nonum"):
                num += 1
            # Each entry is wrapped rather than bare: `shelf.js` hangs the
            # 책갈피 button off the row, and a button inside the anchor would
            # be both invalid and un-clickable without swallowing the link.
            items.append(
                '<div class="toc-row">'
                f'<a class="ms-sec" href="#{c.esc(entry["id"])}">'
                f'<span class="ms-num">{"" if entry.get("nonum") else num}</span>'
                f'<span class="ms-t">{c.esc(entry["label"])}</span>'
                "</a></div>"
            )
        out.append(f'<div class="ms-g">{head}<div class="ms-rows">{"".join(items)}</div></div>')
    return ('<div class="toc-title">목차</div>'
            f'<nav class="ms" aria-label="목차">{"".join(out)}</nav>')


def _header(paper: Paper, tagline: str = "") -> str:
    """What the paper is: its axes, its number, its one result, its title, the
    tagline that says what it does, and who wrote it.

    The axis chips open on the line where a breadcrumb would stand: the nav
    already says which list this page belongs to, and the chips both name the
    paper's axes and open each one's introduction (`assets/pillar.js`). The
    arXiv id beside them links the abstract. The headline number is the
    rewrite's `metric:` — the one result the paper is remembered by — and the
    only date is the rewrite's own, at the line's far end: when the paper itself
    appeared is already in its id. Beside it, how many `/proofread` rounds the
    rewrite has been through, or 교정 전 — a reader is told which they read.

    The title is the paper's own. The thesis heads the 요약 tab directly below,
    and the links out and the 서재 pair sit at the right end of the tab strip.
    """
    chips = c.pillar_chips([p for p in paper.filed if p != corpus.UNCLASSIFIED])
    metric = (f'<span class="ph-metric">{c.esc(paper.metric)}</span>'
              if paper.metric else "")
    checked = f"교정 {paper.proofread}회" if paper.proofread else "교정 전"
    date = (f'<span class="ph-date">작성 {c.esc(paper.date)} · {checked}</span>'
            if paper.date else f'<span class="ph-date">{checked}</span>')
    return f"""<header class="paper-head">
  <div class="paper-head-inner">
    <div class="ph-line">
      {chips}
      <a class="ph-id" href="{_arxiv_href(paper.stem)}" target="_blank" rel="noopener">{c.esc(paper.stem)}</a>
      {metric}
      {date}
    </div>
    <h1 class="paper-title">{c.esc(paper.title)}</h1>
    {f'<p class="paper-tagline">{tagline}</p>' if tagline else ""}
    {_authors(paper)}
  </div>
</header>"""


def _authors(paper: Paper) -> str:
    """The byline, names on one line and affiliations under them.

    `authors:` is written `names (affiliations)`; split, each half wraps on its
    own rather than an affiliation list starting mid-line after the names. A
    byline that is not in that shape prints as it stands.
    """
    if not paper.authors:
        return ""
    m = re.match(r"^(.*?)\s*\((.+)\)\s*$", paper.authors)
    if not m:
        return f'<p class="paper-authors">{c.esc(paper.authors)}</p>'
    return (f'<p class="paper-authors"><span class="au-n">{c.esc(m.group(1))}</span>'
            f'<span class="au-a">{c.esc(m.group(2))}</span></p>')


def _src_group(paper: Paper) -> str:
    """Every link out of the site, as one group of pills.

    A hairline separates the group from the 서재 pair, so the bar reads as two
    things — where the paper lives, and what this reader has done with it —
    rather than as one run of buttons. Empty when a rewrite declares no link,
    which R10 allows and which is itself reproducibility information.
    """
    if not paper.links:
        return ""
    items = "".join(
        f'<a href="{c.esc(url)}" target="_blank" rel="noopener">'
        f"{c.src_mark(kind)}<span>{c.esc(label)}</span></a>"
        for kind, label, url in paper.links
    )
    return f'<div class="src-group" role="group" aria-label="외부 링크">{items}</div>'


# ── Comparisons ─────────────────────────────────────────────────────────────

def comparison_page(comp, papers_by_id: dict, katex, decisions: dict,
                    problems: list[str] | None = None) -> str:
    """One comparison — the question, the fork drawn as the papers' cards, then
    the argument under the same contents a rewrite's 상세 has.

    The first screen is the comparison's shape rather than its prose: the
    question, the problem the papers share under it, and the fork — `common:`
    as the trunk and one card per paper as its branches, each card naming the
    paper by its alias and its `stances:` line. A reader knows what the papers
    share and where each one goes before a paragraph starts arguing it. The
    thesis is not on this page: it is the answer the 비교 list's card gives,
    and here the fork already draws it.

    The card row is where the track's constraint pays off. Every compared paper
    is guaranteed to have a rewrite, so the page can state what the papers
    *are* entirely from front matter already written — alias, title, headline
    metric, and a link to the full read. Nothing here is authored twice.

    Each paper keeps one mark (`components.paper_mark`) on its card and its
    matrix column, and `compare.js` lights one paper across the page while the
    reader points at any of its places.

    The argument reads like a rewrite's 상세: the acts as named milestones on a
    contents rail, act 0 the background cards when the comparison names any,
    and each act's rows the drawn pieces it carries — a comparison has few
    sections and its tables and figures are what a reader comes back for.

    None of the 서재 layer is here — 즐겨찾기, 읽음, 책갈피 and 메모 are all keyed
    by arXiv id, and a comparison has a slug. Rather than ship controls that
    cannot resolve, the page ships none: `paper.js` alone, for the contents
    and the term anchors a shared vocabulary panel needs.
    """
    papers = [papers_by_id[pid] for pid in comp.paper_ids]
    heads = [(p.stem, display_alias(p), f"../../p/{p.stem}/index.html", c.paper_mark(i))
             for i, p in enumerate(papers)]

    figures = {}
    for p in papers:
        sources = corpus.figure_sources(p.body)
        figures[p.stem] = {fid: (url, sources.get(fid, ""))
                           for fid, url in corpus.figure_urls(p.body).items()}
    renderer = DocRenderer(katex, decisions=decisions, kind="compare",
                           matrix_heads=heads, figures=figures,
                           siblings={pid: p.title
                                     for pid, p in papers_by_id.items()})
    rendered = renderer.render(comp.body)
    if problems is not None:
        problems.extend(f"comparison/{comp.slug}.md: {p}" for p in renderer.problems)

    background, bg_entries = _cmp_background(comp)
    rendered, entries = _cmp_contents(rendered, renderer.toc)
    entries = bg_entries + entries
    body = f"""{_cmp_header(comp)}
{_cmp_cards(comp, papers)}
<div class="cmp-read">
  {_act_strip(entries)}
  <div class="shell">
    <aside class="toc">{_toc(entries)}</aside>
    <main class="article">
      <section class="view">{background}{rendered}</section>
    </main>
  </div>
</div>
"""
    return c.page(
        title=f"{comp.title} · PROBE",
        here="compare",
        description=comp.preview,
        body=body,
        depth=2,
        scripts=["paper.js", "compare.js"],
        extra_head=f'<link rel="alternate" type="text/markdown" href="{c.RAW_URL}/comparison/{comp.slug}.md">',
    )


# The drawn pieces a comparison's contents list under each act, by the title
# each prints: a figure tab's question, a timeline's or flow's title, a
# matrix's head. A comparison's `###` sections are optional and usually absent,
# so these are what a reader returning to the page looks for.
_CMP_MARKS = re.compile(
    r'<div class="pdiv pdiv-named" id="act-(?P<act>[^"]+)">'
    r'|<h2 class="h-sec" id="(?P<sec>[^"]+)"'
    r'|<(?P<tag>p|div) class="(?P<cls>figs-q|flow-title|box-head)">(?P<title>.*?)</(?P=tag)>',
    re.S)


def _cmp_contents(rendered: str, toc: list[dict]) -> tuple[str, list[dict]]:
    """`(rendered, entries)` — the acts, their sections and their drawn pieces,
    in reading order, each piece's title given an anchor to land on."""
    acts = {e["n"]: e for e in toc if e.get("kind") == "act"}
    secs = {e["id"]: e for e in toc if e.get("kind") == "sec"}
    entries: list[dict] = []
    seq = 0

    def mark(m: re.Match) -> str:
        nonlocal seq
        if m.group("act"):
            if m.group("act") in acts:
                entries.append(acts[m.group("act")])
            return m.group(0)
        if m.group("sec"):
            if m.group("sec") in secs:
                entries.append(secs[m.group("sec")])
            return m.group(0)
        seq += 1
        anchor = f"piece-{seq}"
        label = html.unescape(re.sub(r"<[^>]+>", "", m.group("title"))).strip()
        entries.append({"kind": "sec", "id": anchor, "label": label})
        return (f'<{m.group("tag")} class="{m.group("cls")}" id="{anchor}">'
                f'{m.group("title")}</{m.group("tag")}>')

    return _CMP_MARKS.sub(mark, rendered), entries


def _cmp_background(comp) -> tuple[str, list[dict]]:
    """Act 0 — the background cards the comparison names, before act 1.

    A drawing and one line each (`builder/primers.py`): the background a
    reader outside the field needs before the divergence reads, given as
    pictures rather than paragraphs. In the contents the act lists the cards
    by name, unnumbered — the numbers count the argument's own stops. Unknown
    ids were reported at discovery and are left out here.
    """
    ids = [pid for pid in comp.primer if pid in primers.PRIMERS]
    if not ids:
        return "", []
    noun = c.CMP_ACT_NAMES["0"]
    cards = "".join(primers.card(pid, anchor=f"bg-{pid}") for pid in ids)
    entries = [{"kind": "act", "n": "0", "label": noun, "sub": c.CMP_BACKGROUND_Q}]
    entries += [{"kind": "sec", "id": f"bg-{pid}", "label": primers.PRIMERS[pid][0],
                 "nonum": True} for pid in ids]
    return ('<div class="pdiv pdiv-named" id="act-0"><span class="pn">0</span>'
            f'<span class="pt">{c.esc(noun)}</span>'
            f'<span class="ps">{c.esc(c.CMP_BACKGROUND_Q)}</span></div>\n'
            f'<div class="primer-row" data-n="{min(len(ids), 3)}">{cards}</div>\n',
            entries)


def display_alias(paper: Paper) -> str:
    """The paper's short name, wherever a title does not fit.

    `alias:` is the rewrite's own answer, resolved against the paper's original
    by the ladder in `analysis/AUTHORING.md` §1 — which reaches names no title
    carries (`XL-VLA` under *Cross-Hand Latent Representation…*). A paper the
    ladder leaves without one falls back to the title's colon prefix, and then
    to the title itself: the id printed beside it is what identifies the paper
    either way, so the fallback only has to be readable, not authoritative.
    """
    if paper.alias:
        return paper.alias
    head = paper.title.split(":")[0].strip()
    return head if (":" in paper.title and len(head.split()) <= 5) else paper.title


# ── The fork ────────────────────────────────────────────────────────────────
# A paper page's 비교 panel draws a comparison's `stances:` and `common:`
# (comparison/AUTHORING.md §2-1) rather than its tagline: a branch per paper
# for what it does, the trunk for what they all accept. The comparison's own
# page draws the same two keys at full size as its paper cards (`_cmp_cards`),
# and the 비교 index as one line per paper on its card. The branch carries the alias AND
# the arXiv id — the alias is what a reader recognises, the id is what they
# search and cite — and every branch is drawn the same. Nothing here is keyed
# to a pillar: a comparison usually sits inside one axis, so a per-paper colour
# separates cards that are already apart and says nothing inside the one card
# where the reader is actually choosing between three answers.

FORK_ROW = 22          # px per branch, matched by `grid-auto-rows` in site.css


def _fork_bracket(n: int) -> str:
    """The bracket an `n`-way fork leaves: a trunk, a spine, a tick per branch."""
    h = FORK_ROW * n
    ticks = [FORK_ROW // 2 + FORK_ROW * i for i in range(n)]
    d = " ".join(
        [f"M0 {h // 2} H13", f"M13 {ticks[0]} V{ticks[-1]}"]
        + [f"M13 {y} H25" for y in ticks]
    )
    return (
        f'<svg class="fork-br" width="26" height="{h}" viewBox="0 0 26 {h}" '
        f'aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.4" '
        f'stroke-linecap="round"><path d="{d}"/></svg>'
    )


def _fork(comp, papers_by_id: dict, mark: str = "") -> str:
    """One comparison as a fork, or its ids when the front matter cannot draw one.

    `stances:` is required and checked, but a comparison missing it is reported
    rather than skipped — so the render has to stand up without it, and falls
    back to the id row the card would otherwise carry.
    """
    stances = comp.stances
    if len(stances) != len(comp.paper_ids):
        return (
            '<span class="cmp-item-ids">'
            + "".join(
                f'<span class="cmp-item-id">{c.esc(pid)}</span>'
                for pid in comp.paper_ids
            )
            + "</span>"
        )
    branches = "".join(
        f'<span class="fork-n{" is-self" if pid == mark else ""}">'
        f'{c.esc(display_alias(papers_by_id[pid]) if pid in papers_by_id else pid)}</span>'
        f'<span class="fork-id">{c.esc(pid)}</span>'
        f'<span class="fork-s">{c.esc(stance)}</span>'
        for pid, stance in zip(comp.paper_ids, stances)
    )
    trunk = (
        f'<span class="fork-trunk"><span class="fork-l">공통</span>'
        f"{c.esc(comp.common)}</span>"
        if comp.common
        else '<span class="fork-trunk"></span>'
    )
    return (
        f'<span class="fork">{trunk}{_fork_bracket(len(stances))}'
        f'<span class="fork-branches">{branches}</span></span>'
    )


def _cmp_header(comp) -> str:
    """The question, and the problem the papers share under it.

    One line above the question carries what the comparison is filed under:
    its axes, how many papers it holds, and its date at the far end — the same
    line a rewrite's header opens on. Under the question, `problem:` — what
    every compared paper is up against, in plain words — because a reader
    meeting the question needs the problem before any answer to it. A
    comparison that has not written one prints its tagline there instead, the
    comparison's own one-line answer.
    """
    if comp.problem:
        under = (f'<p class="cmp-tagline cmp-problem"><span class="cmp-problem-l">'
                 f'같이 붙든 문제</span>{c.esc(comp.problem)}</p>')
    elif comp.tagline:
        under = f'<p class="cmp-tagline">{c.esc(corpus.plain_text(comp.tagline))}</p>'
    else:
        under = ""
    return f"""<header class="paper-head">
  <div class="paper-head-inner">
    <div class="ph-line">
      {c.pillar_chips(comp.pillars)}
      <span class="ph-count">논문 {len(comp.paper_ids)}편</span>
      <span class="ph-date">작성 {c.esc(comp.date)}</span>
    </div>
    <h1 class="paper-title">{c.esc(comp.title)}</h1>
    {under}
  </div>
</header>"""


def _cmp_cards(comp, papers: list[Paper]) -> str:
    """The fork, drawn as the compared papers' cards.

    `common:` is the trunk and each card is a branch: the paper's mark, its
    alias and its `stances:` line lead, its `plain:` line says the same in
    everyday words, and its full title, arXiv id and headline metric follow at
    reference size — the alias is the name the fork,
    the matrix and the prose all use, so the card leads with it.

    In `compares:` order, which is the comparison author's order and the same
    one every ```probe-matrix column runs in — so the third card and the third
    column are the same paper, and carry the same mark.

    A comparison whose `stances:` does not match its papers is reported by
    discovery; its cards still draw, without the stance line and the trunk.
    """
    stances = comp.stances if len(comp.stances) == len(papers) else [""] * len(papers)
    plain = comp.plain if len(comp.plain) == len(papers) else [""] * len(papers)
    cards = "".join(
        f'<a class="cmp-card" data-paper="{c.esc(p.stem)}" '
        f'href="../../p/{c.esc(p.stem)}/index.html">'
        f'<span class="cmp-card-h">{c.paper_mark(i, 12)}'
        f'<span class="cmp-card-n">{c.esc(display_alias(p))}</span></span>'
        + (f'<span class="cmp-card-s">{c.esc(stance)}</span>' if stance else "")
        + (f'<span class="cmp-card-plain">{c.esc(line)}</span>' if line else "")
        + f'<span class="cmp-card-t">{c.esc(p.title)}</span>'
        f'<span class="cmp-card-foot">'
        f'<span class="cmp-card-id">{c.esc(p.stem)}</span>'
        + (f'<span class="cmp-card-m">{c.glue_units(c.esc(p.metric))}</span>' if p.metric else "")
        + "</span></a>"
        for i, (p, stance, line) in enumerate(zip(papers, stances, plain))
    )
    trunk = (f'<div class="cmp-trunk"><span class="fork-l">공통</span>'
             f'<span>{c.esc(comp.common)}</span></div>'
             if comp.common and any(stances) else "")
    return (
        f'<section class="cmp-cards{" has-trunk" if trunk else ""}" aria-label="읽은 논문">'
        f'{trunk}<div class="cmp-card-row" style="--n:{len(papers)}">{cards}</div>'
        "</section>"
    )


def comparison_index_page(comps: list, papers_by_id: dict) -> str:
    """비교 — every comparison, newest first, as cards under the axis line.

    A card is one question: its axes and date on top, the question, what the
    papers share, and under a rule each paper's name with what it does about
    the question. Under the question, the thesis — the answer reading them
    together gives, which the comparison's own page leaves to its fork. The
    tagline is not printed here: it is the same thought again. The axis
    line above is the analysis list's: pressing an axis keeps its comparisons
    (`cards.js`).
    """
    ordered = sorted(comps, key=lambda x: x.order_key, reverse=True)
    if ordered:
        counts = Counter(p for x in ordered for p in x.pillars)
        items = "".join(
            _axis_chip(k, counts[k])
            for k in PILLAR_ORDER if counts.get(k))
        line = (
            '<div class="pline" data-filters role="group" aria-label="연구 축으로 거르기">'
            f'<span class="pline-ic" aria-hidden="true">{c.icon("layers", 18)}</span>'
            f'<div class="pline-items" data-pline>{items}</div>'
            f'<span class="pline-stat"><span data-result-count>{len(ordered)}편</span>'
            f' · 최근 {c.esc(ordered[0].date)}</span></div>')

        def card(x) -> str:
            names = [display_alias(papers_by_id[pid]) if pid in papers_by_id else pid
                     for pid in x.paper_ids]
            stances = x.stances if len(x.stances) == len(names) else [""] * len(names)
            sides = "".join(f'<p class="cmp-st"><b>{c.esc(n)}</b><span>{c.esc(s)}</span></p>'
                            for n, s in zip(names, stances))
            common = (f'<p class="cmp-common"><b>공통</b>{c.esc(x.common)}</p>'
                      if x.common else "")
            return (f'<a class="card cmp-q" href="{c.esc(x.slug)}/index.html" '
                    f'data-pillars="{" ".join(x.pillars)}">'
                    f'<div class="card-top"><p class="card-chips">{c.pillar_chips(x.pillars)}</p>'
                    f'<span class="card-id">{c.esc(_md_date(x.date))}</span></div>'
                    f'<h3>{c.esc(x.title)}</h3>'
                    + (f'<p class="cmp-thesis">{c.esc(x.thesis)}</p>' if x.thesis else "")
                    + f'{common}<div class="cmp-sts">{sides}</div></a>')

        # Three across at most, as many columns as keep the rows even.
        cols = -(-len(ordered) // -(-len(ordered) // 3))
        list_html = (
            f'{line}<div class="cards" style="--cols:{cols}" data-cards>'
            + "".join(card(x) for x in ordered) + "</div>"
            '<p class="corpus-empty" data-empty hidden>이 연구 축의 비교가 아직 없습니다.</p>')
    else:
        list_html = '<p class="corpus-empty">아직 비교한 글이 없습니다.</p>'

    head = c.mast(
        eyebrow="Side by side",
        title="비교, 갈리는 자리만 봅니다",
    )

    body = f"""{head}

<div class="deck"><main class="cmps">
  {list_html}
</main></div>
"""
    return c.page(
        title="비교 · PROBE",
        here="compare",
        description="재작성본이 있는 논문 두세 편을 한 질문 아래 놓고, 갈리는 자리만 원문에서 확인한 비교",
        body=body,
        depth=1,
        scripts=["cards.js"],
        extra_head=f'<link rel="stylesheet" href="{c.asset("../assets/index.css")}">',
    )


# ── 탐색 ────────────────────────────────────────────────────────────────────
# One page per run date, every pillar on it, and an index of the dates. The
# reports are written per pillar for the routine's sake — one context file and
# one window each — and read per date for the reader's: what did this run turn
# up, and which of it did more than one axis notice.

# Where a pick sits in its pillar's report, as the chip prints it. Words, not
# the report's medal glyphs: an emoji is the reader's device's drawing, and
# the rank is a fact a short label states as well.
_PICK_LABEL = {"🥇": "1위", "🥈": "2위", "🥉": "3위", "🌱": "인접", "📋": "추가"}

_SCOUT_MD = None


def _scout_md(text: str, decisions: dict, *, inline: bool = False) -> str:
    """A report's Markdown, with each `D#` given the tooltip a rewrite's gets.

    The reports are not rewrites: none of `DocRenderer`'s rules binds them,
    and its checks would fire on prose they were never written to. The one
    thing they share with the rewrites is the decision codes, so the codes are
    decorated the same way and nothing else is borrowed.
    """
    global _SCOUT_MD
    if _SCOUT_MD is None:
        from markdown_it import MarkdownIt
        _SCOUT_MD = MarkdownIt("commonmark", {"html": False})
    out = _SCOUT_MD.renderInline(text) if inline else _SCOUT_MD.render(text)
    return _decorate_refs(out, decisions)


def _scout_chip(pick) -> str:
    """The axis and the rank it gave the paper, in one pill — `P3 · 1위`.
    The same chip on a card, a row and the detail, so a rank reads the same
    wherever the paper is."""
    return (f'<span class="chip pillar sn-rk" data-p="{c.esc(pick.pillar)}">'
            f'{c.esc(pick.pillar)}<i>·</i>{_PICK_LABEL[pick.kind]}</span>')


# A figure in a report's prose — `1,880.2시간`, `84.0%`, `5개` — is what a
# reader scanning the detail is looking for, so the page marks it. A digit
# inside a code (`D4QX`) or an id is not a figure.
# A bare number counts only when nothing word-like follows it: `1단계` and
# `5과제` are an ordinal and a count-word, not figures a reader scans for.
_FIGURE = re.compile(r"(?<![A-Za-z\d.])(\d[\d,]*(?:\.\d+)?"
                     r"(?:\s?(?:%|시간|개|회|편|배|×|Hz)|(?![\d.,가-힣A-Za-z])))")
_HTML_TAG = re.compile(r"(<[^>]+>)")


def _figures(html_text: str) -> str:
    """Mark the figures in rendered HTML, in text and never inside a tag."""
    parts = _HTML_TAG.split(html_text)
    return "".join(p if p.startswith("<") else _FIGURE.sub(r'<b class="sc-fig">\1</b>', p)
                   for p in parts)


# A list item that opens on a short label and an em dash — `VL 흐름 — …` —
# is the shape most report bullets write as `**VL 흐름** — …`. The reports
# are read as written, so the page gives the plain ones the same bold rather
# than ask a report to change. A label is plain text (a figure mark may sit
# in it) no wider than the labels the reports bold themselves, about 20
# Hangul syllables; a Latin letter or a digit counts as about half of one,
# so `Temporal Representation Bottleneck` is a label and a clause with a
# dash in it is not.
_LABEL_WIDTH = 22
_LABEL_ITEM = re.compile(
    r'(<li>(?:\s*<p>)?)((?:[^<\n—]|<b class="sc-fig">[^<]*</b>)+?) — ')
_TAG = re.compile(r"<[^>]+>")


def _label_width(text: str) -> float:
    return sum(1 if "\u1100" <= ch <= "\u11ff" or "\u3000" <= ch <= "\ud7a3" else .55
               for ch in text)


def _label_items(html_text: str) -> str:
    def sub(m: re.Match) -> str:
        label = _TAG.sub("", m.group(2))
        if _label_width(label) > _LABEL_WIDTH:
            return m.group(0)
        return f"{m.group(1)}<strong>{label}</strong> — "
    return _LABEL_ITEM.sub(sub, html_text)


def _bullets(md: str) -> list[str]:
    return [line[2:].strip() for line in md.splitlines() if line.startswith("- ")]


def _after_headline(md: str) -> str:
    """A pick's "what" with its first bullet — the card's one line — taken out."""
    lines = md.splitlines()
    first = next((i for i, l in enumerate(lines) if l.startswith("- ")), None)
    if first is None:
        return md
    return "\n".join(lines[:first] + lines[first + 1:]).strip()


# What the paper's Real score says about its hardware evidence, in the words
# `scouting/AUTHORING.md` §5-3 gives the page. The rubric's numbers rank the
# papers and stay in the report; a reader deciding what to open needs only
# whether the result stands on a robot, said in words.
_REAL_LABEL = {3: "실물 정량, 다수 과제", 2: "실물 정량 결과", 1: "실물 시연만", 0: "실물 결과 없음"}


def _scout_tags(paper) -> str:
    """The two judgements a reader decides by — whether the result stands on
    a robot, and whether the code is out — as quiet tags."""
    real = paper.lead.dims.get("Real")
    tags = [t for t in ((_REAL_LABEL[real] if real is not None else ""), paper.code) if t]
    return ('<p class="card-tags">' + "".join(f"<span>{c.esc(t)}</span>" for t in tags) + "</p>"
            if tags else "")


def _scout_title(paper) -> str:
    """The English title with its codename taken off the front when the card
    already prints that codename as its name (`WB-WAM: Heterogeneous …`)."""
    title, alias = paper.title, paper.alias
    head, colon, rest = title.partition(":")
    if colon and rest.strip() and head.strip() == alias:
        return rest.strip()
    return title if title != alias else ""


def _scout_picks(paper) -> list:
    return sorted(paper.picks, key=lambda p: (not p.full, p.rank))


def _arxiv_href(paper_id: str) -> str:
    return f"https://arxiv.org/abs/{c.esc(paper_id)}"


def _scout_card(paper, decisions: dict, fig: dict | None) -> str:
    """A recommended paper: its axes and rank, its arXiv id, its name, the
    overview figure, the English title, one line, the two tags. The whole
    card opens the detail; the id is the one link out."""
    pid = c.esc(paper.paper_id)
    chips = "".join(_scout_chip(p) for p in _scout_picks(paper))
    title = _scout_title(paper)
    figure = (f'<div class="card-fig"><img src="{c.esc(fig["url"])}" alt="" loading="lazy" '
              f'decoding="async"></div>' if fig else "")
    gist = (f'<p class="card-gist">{_scout_md(paper.gist, decisions, inline=True)}</p>'
            if paper.gist else "")
    return (f'<article class="card" data-open="{pid}">'
            f'<div class="card-top"><p class="card-chips">{chips}</p>'
            f'<a class="card-id" href="{_arxiv_href(paper.paper_id)}" target="_blank" '
            f'rel="noopener" title="arXiv 초록">{pid}</a></div>'
            f'<h3><a href="#p-{pid}" data-detail="{pid}" title="{c.esc(paper.title)}">'
            f'{c.esc(paper.alias)}</a></h3>{figure}'
            + (f'<p class="card-title">{c.esc(title)}</p>' if title else "")
            + f'{gist}{_scout_tags(paper)}</article>')


def _scout_row(paper, decisions: dict) -> str:
    """A candidate in the table under the cards: the arXiv id, the name with
    its English title after it over its line, the axes with their ranks."""
    pid = c.esc(paper.paper_id)
    chips = "".join(_scout_chip(p) for p in _scout_picks(paper))
    title = _scout_title(paper)
    full = (f'<span class="tl-full" title="{c.esc(paper.title)}">{c.esc(title)}</span>'
            if title else "")
    line = _scout_md(paper.gist, decisions, inline=True) if paper.gist else c.esc(paper.title)
    return (f'<li class="tl-row" data-open="{pid}">'
            f'<a class="tl-id" href="{_arxiv_href(paper.paper_id)}" target="_blank" '
            f'rel="noopener" title="arXiv 초록">{pid}</a>'
            f'<a class="tl-main" href="#p-{pid}" data-detail="{pid}" title="{c.esc(paper.title)}">'
            f'<span class="tl-t">{c.esc(paper.alias)}{full}</span><span class="tl-g">{line}</span></a>'
            f'<span class="tl-p">{chips}</span></li>')


# ── The detail ──────────────────────────────────────────────────────────────
# The brief's six fields, read as four tabs of about one length each: three
# fields to a tab would put three quarters of a write-up behind its first tab.
# Every heading inside is a short bold noun after an accent square, then a
# grey line saying what the noun stands for (`scout.css`).
_TAB_FIELDS = (("q", "문제", ("문제", "기존 한계")),
               ("m", "방법", ("핵심 방법", "차별점")),
               ("r", "결과", ("핵심 기여", "가치")))
_FIELD_NOUN = {"문제": ("질문", "이 논문이 푸는 것"), "기존 한계": ("한계", "기존 방법이 막힌 곳"),
               "핵심 방법": ("핵심", "무엇을 하나"), "차별점": ("차이", "기존과 다른 점"),
               "핵심 기여": ("기여", "저자가 내세우는 것"), "가치": ("가치", "남는 것")}
# A field's first line that only announces the list under it ("저자들이
# 주장하는 세 가지") says nothing the list does not, and is left out.
_ANNOUNCE_MAX = 22
_WORD = re.compile(r"[가-힣A-Za-z0-9]{2,}")


_CAP_MATH = re.compile(r"\$([^$]+)\$")


def _caption(text: str, katex) -> str:
    """An arXiv caption with its `$`-delimited TeX typeset, the rest escaped.

    The caption is the paper's own English, read from LaTeXML's `alttext`, so
    a `$` in it opens math and nothing else."""
    out, at = [], 0
    for m in _CAP_MATH.finditer(text):
        out.append(c.esc(text[at:m.start()]))
        tex = m.group(1).strip()
        out.append(katex.inline(tex) if katex is not None else c.esc(tex))
        at = m.end()
    return "".join(out) + c.esc(text[at:])


def _noun_head(noun: str, sub: str) -> str:
    return f'<h4 class="dx-nh">{c.esc(noun)}<span class="dx-nsub">{c.esc(sub)}</span></h4>'


def _brief_field(label: str, md: str, gist_words: list[str], decisions: dict) -> str:
    """One field under its noun heading: its first line, then its list.

    The first line is dropped when it only announces the list, or when it
    says again what the one line under the paper's name already said."""
    lead, _, rest = md.partition("\n")
    plain = _md_plain(lead).strip()
    words = _WORD.findall(plain)
    shared = sum(1 for w in gist_words if w in words)
    announce = bool(rest.strip()) and len(plain) < _ANNOUNCE_MAX
    repeat = bool(gist_words) and shared >= max(2, -(-len(gist_words) // 2))
    body = ("" if announce or repeat
            else f'<p class="dx-lead">{_figures(_scout_md(lead, decisions, inline=True))}</p>')
    if rest.strip():
        body += _figures(_scout_md(rest, decisions))
    return f'<section class="dx-ns">{_noun_head(*_FIELD_NOUN[label])}{body}</section>'


def _scout_axes(paper, decisions: dict) -> str:
    """Each pillar's reading: its headline, then the rest of what it wrote
    under it, in the shape of every other field.

    Only a pillar that wrote the paper up has a reading. A 📋 row's one line
    is a summary of the paper, not what it means for the pillar, and says
    again what the other tabs say, so it is left out wherever a write-up
    exists; a paper only 📋 rows carry shows those lines, as all there is.
    Where more than one reading stands, a grey line over each names its
    pillar and rank in plain text — the subtitle's voice, not the chip's,
    so the field carries no mark the others lack."""
    picks = [p for p in _scout_picks(paper) if p.full] or _scout_picks(paper)
    out = []
    for pick in picks:
        if pick.full:
            lines = _bullets(pick.implic) or [pick.implic]
            head, rest = lines[0], lines[1:]
        else:
            head, rest = pick.gist, []
        items = "".join(f"<li>{_figures(_scout_md(l, decisions, inline=True))}</li>" for l in rest)
        who = (f'<p class="dx-axl">{c.esc(pick.pillar)} · {_PICK_LABEL[pick.kind]}</p>'
               if len(picks) > 1 else "")
        out.append(f'<div class="dx-ax">{who}<p class="dx-lead">'
                   f'{_figures(_scout_md(head, decisions, inline=True))}</p>'
                   + (f"<ul>{items}</ul>" if items else "") + "</div>")
    return "".join(out)


def _scout_detail(paper, decisions: dict, fig: dict | None, rewrite: str = "",
                  katex=None) -> str:
    """Everything the run says about one paper, as one article.

    `rewrite` is the address of the paper's own rewrite when the corpus has
    one: the head links it beside arXiv, so a scouted paper already read in
    full is one click from that reading.

    With a script the article opens in a drawer — from the side, or from
    below on a phone — and its four tabs show one at a time. Without one the
    articles stand in a column at the page's foot, every tab open under its
    own name, and a card's link is a jump to its article."""
    pid = c.esc(paper.paper_id)
    lead = paper.lead
    chips = "".join(_scout_chip(p) for p in _scout_picks(paper))
    title = _scout_title(paper)
    # Who wrote it and where it appeared belongs with the title, once, not at
    # the foot of every tab.
    by = " · ".join(c.esc(m) for m in lead.meta)
    head = (f'<header class="sd-h"><div class="sd-top"><p class="card-chips">{chips}</p>'
            f'<a class="card-id" href="{_arxiv_href(paper.paper_id)}" target="_blank" '
            f'rel="noopener">arXiv {pid} ↗</a>'
            + (f'<a class="card-id sd-rw" href="{c.esc(rewrite)}">분석 읽기</a>' if rewrite else "")
            + '</div>'
            f'<h2>{c.esc(paper.alias)}</h2>'
            + (f'<p class="sd-t">{c.esc(title)}</p>' if title else "")
            + (f'<p class="sd-by">{by}</p>' if by else "")
            + (f'<p class="sd-g">{_scout_md(paper.gist, decisions, inline=True)}</p>'
               if paper.gist else "")
            + _scout_tags(paper) + "</header>")
    figure = (f'<figure class="sd-fig"><img src="{c.esc(fig["url"])}" alt="" loading="lazy" '
              f'decoding="async"><figcaption>{_caption(fig["caption"], katex)}'
              f'<span class="sd-src">{c.esc(fig["source"])}</span></figcaption></figure>' if fig else "")

    gist_words = _WORD.findall(_md_plain(paper.gist))
    tabs: list[tuple[str, str, str, str]] = []   # key, name, count, body
    if lead.full and lead.brief:
        fields = dict(lead.brief)
        for key, name, labels in _TAB_FIELDS:
            tabs.append((key, name, "", "".join(
                _brief_field(l, fields[l], gist_words, decisions) for l in labels)))
    elif lead.full:
        # A report written before the brief has one block of prose on what
        # the paper is; it reads as one tab.
        what = _after_headline(lead.contrib)
        if what:
            tabs.append(("w", "요지", "", f'<section class="dx-ns">{_noun_head("요지", "무엇인가")}'
                                         f'{_figures(_scout_md(what, decisions))}</section>'))
    checks = _bullets(lead.check) if lead.full else []
    judge = (f'<section class="dx-ns">{_noun_head("시사점", "연구 축별")}'
             f'{_scout_axes(paper, decisions)}</section>')
    if lead.full and lead.check.strip():
        n = f" · {len(checks)}" if checks else ""
        judge += (f'<section class="dx-ns"><h4 class="dx-nh">확인'
                  f'<span class="dx-nsub">먼저 볼 것{n}</span></h4>'
                  f'{_figures(_scout_md(lead.check, decisions))}</section>')
    tabs.append(("u", "판단", str(len(checks)) if checks else "", judge))

    bar = "".join(
        f'<button type="button" role="tab" data-dx-tab="{k}" aria-selected="{str(i == 0).lower()}">'
        f'{name}' + (f'<span class="dx-tc">{n}</span>' if n else "") + "</button>"
        for i, (k, name, n, _) in enumerate(tabs))
    panes = "".join(
        f'<div class="dx-pane" role="tabpanel" data-dx-pane="{k}">'
        f'<h3 class="dx-pt">{name}</h3>{body}</div>'
        for k, name, _, body in tabs)
    return (f'<article class="sd" id="p-{pid}" data-sd="{pid}">{head}{figure}'
            f'<div class="dx"><div class="dx-tabbar" role="tablist">{bar}</div>'
            f'{_label_items(panes)}</div></article>')


# ── The run picker ──────────────────────────────────────────────────────────
_WEEKDAYS = ("월", "화", "수", "목", "금", "토", "일")


def _md_date(date: str) -> str:
    return f"{date[5:7]}.{date[8:10]}"


def _scout_calendar(runs: list, here: str, href) -> str:
    """Every month that has a run, as a month grid with each run's day a link.

    The months stand one under another; `scout.js` shows the one the page's
    run is in and steps between them. The grid is a native `<details>` behind
    the date line's calendar cell, so it opens with no script."""
    import calendar as _cal
    by_date = {r.date: r for r in runs}
    months = sorted({r.date[:7] for r in runs}, reverse=True)
    out = []
    for ym in months:
        y, m = int(ym[:4]), int(ym[5:])
        start, days = _cal.monthrange(y, m)          # Monday is 0
        cells = [f'<span class="sn-dow">{d}</span>' for d in _WEEKDAYS]
        cells += ['<span class="sn-day is-pad"></span>'] * start
        for d in range(1, days + 1):
            key = f"{ym}-{d:02d}"
            run = by_date.get(key)
            if run:
                sel = ' is-sel" aria-current="page' if key == here else ""
                cells.append(f'<a class="sn-day has-run{sel}" href="{href(key)}" '
                             f'aria-label="{m}월 {d}일 회차, {len(run.papers)}편">'
                             f'<span class="sn-dn">{d}</span>'
                             f'<span class="sn-cnt">{len(run.papers)}편</span></a>')
            else:
                cells.append(f'<span class="sn-day"><span class="sn-dn">{d}</span></span>')
        out.append(f'<div class="sn-month" data-month="{ym}">'
                   '<div class="sn-cal-h">'
                   '<button type="button" class="sn-nav" data-cal="1" aria-label="이전 달">‹</button>'
                   f'<h2>{y}년 {m}월</h2>'
                   '<button type="button" class="sn-nav" data-cal="-1" aria-label="다음 달">›</button>'
                   f'</div><div class="sn-grid">{"".join(cells)}</div></div>')
    return (f'<details class="sn-calw" data-scout-cal>'
            f'<summary class="sn-lab" title="달력으로 보기" aria-label="달력으로 보기">'
            f'{c.icon("calendar", 20)}</summary>'
            f'<div class="sn-cal" data-here="{here[:7]}">{"".join(out)}</div></details>')


def _scout_dates(runs: list, here: str, href) -> str:
    """The date line: one link a run, newest first, its paper count beside it.
    It stands where the analysis list's axis line stands, at the same size."""
    items = "".join(
        f'<a class="rail-item" href="{href(r.date)}"'
        + (' aria-current="page"' if r.date == here else "")
        + f' aria-label="{int(r.date[5:7])}월 {int(r.date[8:10])}일 회차, {len(r.papers)}편">'
        f'<b>{_md_date(r.date)}</b><span class="rn">{len(r.papers)}</span></a>'
        for r in runs)
    return (f'<nav class="pline sn-dline" aria-label="탐색 회차">'
            f'{_scout_calendar(runs, here, href)}'
            f'<div class="pline-items" data-pline>{items}</div></nav>')


def scout_split(run) -> tuple[list, list]:
    """The run's papers as the page lays them out: the cards — a paper some
    axis ranked first, or one more than one axis picked — and the table,
    every other paper an axis wrote up."""
    ordered = sorted(run.papers, key=lambda p: (p.group != "shared", not p.lead.full,
                                                p.lead.rank))
    first = [p for p in ordered if p.group == "shared" or (p.lead.full and p.lead.rank == 1)]
    more = [p for p in ordered if p not in first and p.lead.full]
    return first, more


# The band every scouting page opens on. It names the surface and what it
# does, as the other bands do; which run is on screen is the date line's
# business, under the band, so the band is the same on every run.
SCOUT_EYEBROW = "Across the research axes"
SCOUT_TITLE = "탐색, 읽을 논문을 먼저 고릅니다"


def scouting_run_page(run, runs: list, decisions: dict, papers_by_id: dict,
                      figures: dict, *, depth: int, katex=None) -> str:
    """One run: the date line, the recommended papers as cards, the rest of
    the written-up papers as a table, and each paper's detail.

    A card is a paper some axis ranked first, or one more than one axis
    picked; the table holds every other paper an axis wrote up. A paper an
    axis only listed (📋) and a near miss stay in the reports, which the
    page's foot links: the page is for choosing what to read.

    The page is printed twice for the newest run: at `s/` — where the nav
    lands, so a reader arrives on what came in last — and at `s/<date>/`, the
    address that stays put once a newer run takes `s/`. `depth` is which of
    the two this is.
    """
    up = "../" * depth
    up_to_s = "" if depth == 1 else "../"

    def href(date: str) -> str:
        return f"{up_to_s}{date}/index.html"

    first, more = scout_split(run)

    # As many columns as keep the rows even — five cards are three and two,
    # never four and one — and a short row's cards widen to fill it.
    cols = -(-len(first) // -(-len(first) // 4)) if first else 1
    cards = "".join(_scout_card(p, decisions, figures.get(p.paper_id)) for p in first)
    cards = (f'<div class="cards" style="--cols:{cols}">{cards}</div>' if cards
             else '<p class="corpus-empty">이 회차에 게이트를 통과한 논문이 없습니다.</p>')
    table = ""
    if more:
        rows = "".join(_scout_row(p, decisions) for p in more)
        table = ('<div class="tl-head" aria-hidden="true"><span>arXiv</span>'
                 '<span>논문 · 한 줄</span><span>연구 축</span></div>'
                 f'<ul class="tl">{rows}</ul>')
    details = "".join(
        _scout_detail(p, decisions, figures.get(p.paper_id),
                      f"{up}p/{p.paper_id}/index.html" if p.paper_id in papers_by_id else "",
                      katex)
        for p in first + more)

    # A pillar's own 🔄 compares it with its earlier reports — the routine's
    # working record, read in the pillar's file. The page reads the run as a
    # whole and links the files, which also hold what the page leaves out.
    sources = " · ".join(
        f'<a href="{BLOB}/{c.esc(r.source)}" target="_blank" rel="noopener">{r.pillar}</a>'
        for r in run.reports)
    if run.run_file:
        sources += (f' · <a href="{BLOB}/scouting/runs/{c.esc(run.date)}.md" target="_blank" '
                    'rel="noopener">회차</a>')

    head = c.mast(eyebrow=SCOUT_EYEBROW, title=SCOUT_TITLE)
    body = f"""{head}

<main class="sn" data-scout>
  {_scout_dates(runs, run.date, href)}
  {cards}
  {table}
  <section class="sd-all" aria-label="세부 내용">{details}</section>
  <p class="sc-sources">원본 리포트 · {sources}</p>
</main>
"""
    return c.page(
        title=f"{run.date} 탐색 · PROBE",
        here="scout",
        description=f"{run.date} 스카우팅 회차 — 연구 축마다 먼저 읽을 논문을 고른 목록",
        body=body,
        depth=depth,
        scripts=["scout.js"],
        extra_head=(f'<link rel="stylesheet" href="{c.asset(f"{up}assets/index.css")}">'
                    f'<link rel="stylesheet" href="{c.asset(f"{up}assets/scout.css")}">'),
    )


def scouting_empty_page() -> str:
    """`s/` before the first run lands."""
    head = c.mast(eyebrow=SCOUT_EYEBROW, title=SCOUT_TITLE)
    body = f"""{head}

<main class="hub hub-wide">
  <p class="corpus-empty">아직 탐색 회차가 없습니다.</p>
</main>
"""
    return c.page(
        title="탐색 · PROBE",
        here="scout",
        body=body,
        depth=1,
        extra_head=(f'<link rel="stylesheet" href="{c.asset("../assets/index.css")}">'
                    f'<link rel="stylesheet" href="{c.asset("../assets/scout.css")}">'),
    )
