"""Page assemblers."""

from __future__ import annotations

import json
import re
from collections import Counter

from . import components as c
from . import corpus, scouting, glance as glance_mod
from .corpus import PILLAR_LABELS, PILLAR_NAMES, PILLAR_ORDER, Paper
from .render import DocRenderer, _decorate_refs

# Pages serves a project site under /<repo>/. 404.html and `build-site.py
# serve` use this; every other page is depth-relative and needs no knowledge
# of where it is hosted.
SITE_BASE = f"/{c.REPO.split('/')[1]}/"
BLOB = f"{c.REPO_URL}/blob/main"
DISCUSSIONS_NEW = f"{c.REPO_URL}/discussions/new?category=paper-notes"

# How many rewrites one page of the list holds, and which of them the bar
# offers. `0` is 전체 — the whole list on one page, which is what a browser with
# no script gets and what the reader can always come back to.
#
# The default is a page rather than the whole corpus: the list is the one part
# of this page that grows without limit, and a reader arriving at it should
# meet a screen of papers, not a year of them. Ten is a screen and a half with
# the lead block above it.
PAGE_SIZES = (10, 20, 0)
PAGE_DEFAULT = 10

# How large `assets/corpus-index.js` may get before it stops being a file every
# page can afford to carry. It is fetched once and cached across the whole site,
# so the ceiling is generous — but it grows with the corpus and nothing else
# here does, so the build says something rather than letting it drift.
INDEX_BUDGET = 100 * 1024


def corpus_index(papers: list[Paper], comps: list | None = None) -> str:
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
    reader reads it off the rail and may type it here, and the English name
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
    """
    ordered = sorted(papers, key=lambda p: p.order_key, reverse=True)
    ranked = sorted(comps or [], key=lambda x: x.order_key, reverse=True)
    payload = {
        "pillars": PILLAR_NAMES,
        "pillarLabels": PILLAR_LABELS,
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
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return f"window.ProbeIndex={body};\n"


def _shelf_facets(cls: str) -> str:
    """New / Starred, the two facets the rail carries beside the axes.

    Server-rendered with a zero count and no pressed state, because which
    papers are starred or new is the reader's and the build cannot know either.
    New ships `hidden` and stays hidden until there is something new to point
    at — a zero that never moves is furniture.

    Both name something the reader put there. What is left to read is not a
    mark anyone made: on a corpus a reader has barely started it counts almost
    every paper, which selects the list they are already looking at. 읽음 is
    still kept — as the state column on 서재's rows and in its export — it
    just has no facet here.
    """
    flags = (("fresh", "New"), ("star", "Starred"))
    return "".join(
        f'<button type="button" class="{c.esc(cls)}" data-facet-flag="{key}" '
        f'aria-pressed="false"{" hidden" if key == "fresh" else ""}>'
        f'<span class="sw {key}" aria-hidden="true"></span><b>{label}</b>'
        f'<span class="rn" data-flag-count="{key}">0</span></button>'
        for key, label in flags
    )


def _page_sizes() -> str:
    """10편 · 20편 · 전체 — how much of the list one page holds.

    A view control, so it sits with 정렬 and wears the same pill group. The
    pressed state printed here is the default; `filter.js` moves it to whatever
    the hash or this browser's last choice says, the same way the shelf facets
    have their counts filled in.
    """
    return "".join(
        f'<button type="button" data-size="{n}" '
        f'aria-pressed="{"true" if n == PAGE_DEFAULT else "false"}">'
        f'{f"{n}편" if n else "전체"}</button>'
        for n in PAGE_SIZES
    )


def _seg(name: str, cls: str, buttons: str) -> str:
    """A pill group, and the chip a phone folds it into.

    The group is the same three buttons at every width — `filter.js` binds
    them, presses one and reads the pressed one back, and none of that knows
    the chip exists. What changes below 680px is where the group sits: it
    becomes a panel under a chip that names the choice currently pressed, so
    the bar carries 정렬 and 한 쪽에 in the width of two words rather than six.

    The chip's label is filled in by `filter.js` off the pressed button, for
    the same reason the shelf facets get their counts there: printing it twice
    is two places for it to disagree with what the list is actually in.
    """
    return (f'<div class="segwrap" data-seg>'
            f'<button type="button" class="segchip" data-seg-toggle '
            f'data-seg-name="{c.esc(name)}" aria-expanded="false" '
            f'aria-haspopup="true"><span data-seg-label></span>'
            f'<span class="segcaret" aria-hidden="true">▾</span></button>'
            f'<div class="sort {cls}" role="group" aria-label="{c.esc(name)}">'
            f'{buttons}</div></div>')


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
  <span class="pgstat" data-page-stat></span>
</nav>"""


def landing_page(papers: list[Paper], katex=None, search_api: str = "",
                 partial: bool = False) -> str:
    """The corpus index — a briefing: newest rewrite in full, the rest as rows.

    The page answers "what should I read" before "what is here". The most
    recent rewrite is printed as a lead block with its thesis, summary and
    numbers; everything else is one scannable row per paper, sorted newest
    first. Facets live in a left rail rather than a chip bank above the list,
    which is what lets the rows start in the first screen.

    Every row is server-rendered with its facets on `data-` attributes rather
    than hydrated from an inline JSON blob. That keeps the page fully readable
    with JavaScript off (the filter bar, the rail and the page strip hide
    themselves, the rows stay, newest first, all of them), and the filter
    script only ever reorders and toggles `hidden` on nodes that already exist.

    The list is paged — `PAGE_DEFAULT` rewrites at a time, the bar offering
    `PAGE_SIZES` — because it is the one part of this page that grows with the
    corpus. A page is counted in papers, not in rows: on the first page the
    lead block *is* the first of them and its own row stands down, so 10편 is
    ten papers there as it is on every other page.

    Order is `Paper.order_key` — the order the rewrites landed on `main`, which
    is the order a reader watched them appear — and the rows carry that key on
    `data-order`, so the script's 최신순 reproduces this list rather than a
    near-miss of it.

    The corpus's size and freshness are stated in the filter bar, whose count
    is the live one; the masthead carries the same pair only for an unscripted
    page, and `index.css` hides it once a script runs.
    """
    ordered = sorted(papers, key=lambda p: p.order_key, reverse=True)

    # Taglines and the lead summary are authored markdown — emphasis is what
    # makes a summary scannable, and a summary that opens with math is common
    # enough that escaping it would publish backticks. `decisions` is left
    # empty on purpose: a `D#` tooltip needs `paper.js`, which this page does
    # not load.
    renderer = DocRenderer(katex) if katex is not None else None

    # Counted over the axes a paper is *filed* under — `Paper.filed`, the two
    # its card prints — because that is what the facet below selects on. Count
    # one set and filter on another and the rail promises rows the click never
    # delivers. The pillar separators in the list still count primaries: a
    # paper sits under one heading, and that is a different question asked in
    # place.
    filed = Counter(p for paper in ordered for p in paper.filed)
    primaries = Counter(p.primary for p in ordered)

    # The reader's own two filters answer a question the corpus cannot: not
    # "which papers are about X" but "which ones are mine" and "which ones are
    # new here". Their counts are the only numbers on this page the build does
    # not know — `filter.js` fills them from the shelf, and the group hides
    # itself when nothing is scripted.
    #
    # They are English for the reason the masthead's eyebrow is: a label is a
    # control, not a sentence, and `Starred` names the star beside it in a
    # width a Korean label needs two lines for. Everything that speaks in
    # sentences stays Korean — the group heading, 서재's tabs, the paper
    # header, and the masthead's own title.
    #
    # The pair is printed twice, once for the rail and once for the filter bar,
    # because the rail leaves at 900px and these two would leave with it — and
    # unlike the 연구 축 below them, nothing else on a phone can reach what
    # they select. Exactly one copy is ever on screen (`index.css`);
    # `filter.js` binds every copy it finds, so the pair never disagrees.
    rail_mine = _shelf_facets("rail-item mine")
    rail_pillars = "".join(
        f'<button type="button" class="rail-item pillar" data-p="{c.esc(k)}" '
        f'data-facet-pillar="{c.esc(k)}" aria-pressed="false">'
        f'<span class="sw"></span><b>{c.esc(k)}</b>'
        f'<span class="rl">{c.esc(PILLAR_LABELS.get(k, "축 미지정"))}</span>'
        f'<span class="rn">{filed[k]}</span></button>'
        for k in PILLAR_ORDER if filed.get(k)
    )

    # One separator per pillar, parked in the list and shown only by the
    # pillar sort. Rendering them up front keeps the sort a reordering of
    # existing nodes — the script never builds markup.
    seps = "".join(
        f'<div class="rsep" data-sep="{c.esc(k)}" hidden>'
        f'<span class="chip pillar" data-p="{c.esc(k)}">{c.esc(k)}</span>'
        f"<h2>{c.esc(PILLAR_LABELS.get(k, '축 미지정'))}</h2>"
        f'<span class="rsep-n" data-sep-count>{primaries[k]}</span></div>'
        for k in PILLAR_ORDER if primaries.get(k)
    )
    rows = "".join(
        _row(p, renderer, lead=(i == 0))
        for i, p in enumerate(ordered)
    )

    head = c.mast(
        eyebrow="Dexterous manipulation",
        title="분석, 원문을 읽기 좋게 풀어 둡니다",
        count=f"{len(ordered)}편" + (f" · 최근 {ordered[0].date}" if ordered else ""),
    )

    body = f"""{head}

<div class="filters" data-filters>
  <div class="filters-inner">
    <label class="search">
      {c.icon("search", 14)}
      <input type="search" data-q autocomplete="off" spellcheck="false"
             placeholder="제목 · 본문 · 용어 · 태그 · 저자 · arXiv id 로 검색"
             aria-label="논문 검색">
      {_search_go(search_api)}
    </label>
    <button type="button" class="barreset" data-reset="facet" hidden>필터 초기화</button>
    <span class="filter-spacer"></span>
    {_seg("정렬", "", '<button type="button" data-sort="recent" aria-pressed="true">최신순</button>'
                      '<button type="button" data-sort="pillar" aria-pressed="false">연구 축별</button>'
                      '<button type="button" data-sort="title" aria-pressed="false">제목순</button>')}
    {_seg("한 쪽에 몇 편", "psize", _page_sizes())}
  </div>
</div>

<div class="deck">
  <aside class="rail" data-rail>
    <p class="rail-stat"><span data-result-count>{len(ordered)}편</span>{
      f'<span data-corpus-when> · <span class="when-word">최근 </span>'
      f'{c.esc(ordered[0].date)}</span>' if ordered else ""}<button type="button"
      class="rail-reset" data-reset hidden>초기화</button></p>
    <p class="rail-h" data-mine-h>서재</p>
    {rail_mine}
    <p class="rail-h">연구 축</p>
    {rail_pillars}
  </aside>
  <main class="corpus" data-corpus>
    {_first_run() if not ordered else ""}
    {_resume()}
    {_lead_block(ordered[0], renderer) if ordered else ""}
    {_search_tabs(search_api)}
    <div class="sem" data-sem hidden></div>
    <div class="listhead" data-listhead{" hidden" if len(ordered) < 2 else ""}>
      <span class="lh-star"></span><span>재작성</span><span>arXiv</span><span>논문 · 한 줄</span><span>연구 축</span><span>분량</span>
    </div>
    <p class="corpus-partial" data-partial hidden>
      모든 단어를 포함하는 논문이 없어, <b>일부만 일치</b>하는 논문을 관련도순으로 보여줍니다.
    </p>
    <p class="corpus-partial" data-fresh-note hidden>
      이 브라우저에서 <b>아직 열지 않은</b> 새 글입니다. 논문을 열면 하나씩 빠집니다.
      <button type="button" class="linkish" data-fresh-ack>모두 확인</button>
    </p>
    <div class="rows" data-rows>{seps}{rows}</div>
    {_pager(len(ordered))}
    <p class="corpus-empty" data-empty hidden>
      조건에 맞는 논문이 없습니다. <button type="button" class="linkish" data-reset>필터를 지워</button> 보세요.
    </p>
  </main>
</div>
"""
    return c.page(
        title="PROBE",
        here="papers",
        description=f"Dexterous manipulation 논문 {len(ordered)}편을 원문에서 다시 쓴 한글 판",
        body=body,
        depth=0,
        # `semantic.js` ships only when the build is handed an endpoint, so a
        # default build makes no request and needs no network to be correct.
        scripts=["shelf.js", "filter.js"] + (["semantic.js"] if search_api else []),
        # `llms.txt` is where an agent handed this URL finds the corpus as
        # data; a partial build writes none, so it links none.
        extra_head=(f'<link rel="stylesheet" href="{c.asset("assets/index.css")}">'
                    + ("" if partial else
                       '\n<link rel="alternate" type="text/plain" title="llms.txt" href="llms.txt">')),
        body_attrs=f'data-search-api="{c.esc(search_api)}"' if search_api else "",
    )


def _search_go(search_api: str) -> str:
    """The button that submits the question, beside the box that holds it.

    It ships with the endpoint and with nothing else: the list below filters as
    the reader types, so where there is no remote index there is nothing for a
    button to do. `index.css` keeps it off a browser with no script for the same
    reason — the control that cannot run removes itself rather than sitting
    there — and `semantic.js` disables it until there is a question to ask.
    """
    if not search_api:
        return ""
    return ('<button type="button" class="search-go" data-ask disabled '
            'aria-label="의미 검색 (Enter)">검색</button>')


def _search_tabs(search_api: str) -> str:
    """The strip that splits a search into its two answers.

    A question reaches the corpus two ways and they are not the same answer:
    의미 is what the remote index found by meaning, 글자 is what the filter in
    this browser matched letter for letter. The strip names both, carries each
    one's count, and shows one at a time.

    It ships with the endpoint, like the button that submits to it, and stays
    hidden until there is something on both sides to choose between — a tab
    over nothing is a tab nobody can use. `filter.js` fills in the counts and
    owns which one is on; the build only prints the control.

    It reads as the paper page's tab strip and is announced as what it is: two
    buttons, one pressed. The 글자 answer is the listing below and everything
    that describes it — a head, a note, the rows, the page strip — rather than
    one element, and a `tab` with no panel to point at is a promise to a screen
    reader that nothing keeps.
    """
    if not search_api:
        return ""
    return (
        '<div class="restabs" data-restabs role="group" '
        'aria-label="검색 결과" hidden>'
        '<button type="button" class="restab" data-restab="sem" '
        'aria-pressed="true">의미 검색<span class="restab-n" '
        'data-restab-n="sem"></span></button>'
        '<button type="button" class="restab" data-restab="lex" '
        'aria-pressed="false">글자 검색<span class="restab-n" '
        'data-restab-n="lex"></span></button>'
        '</div>'
    )


def _resume() -> str:
    """One line back to wherever the reader put a 책갈피.

    Above the lead block, because it is the only thing on the page that is
    about this reader rather than about the corpus, and because a reader who
    left a mark came back for it. One line and no more: the lead block under
    it is the site's own answer to "what should I read", and a stack of the
    reader's unfinished business would push it off the first screen.

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
        '<div class="resume" data-resume="p/" hidden>'
        '<span class="resume-k">책갈피</span>'
        '<span class="resume-chips" data-resume-chips></span>'
        '<a class="resume-all" data-resume-all href="shelf/index.html#marks">'
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
    them ready to match, so a keystroke costs the script a substring test and
    nothing else (`corpus.HAY_MAX` bounds what one row can weigh).
    """
    return (
        f'data-id="{c.esc(paper.stem)}" '
        f'data-pillars="{c.esc(" ".join(paper.filed))}" '
        f'data-primary="{c.esc(paper.primary)}" '
        f'data-order="{c.esc(paper.order_token)}" '
        f'data-title="{c.esc(paper.title.lower())}" '
        f'data-key="{c.esc(paper.search_key)}" '
        f'data-hay="{c.esc(paper.search_hay)}"'
    )


def _star(paper: Paper, cls: str = "rowstar") -> str:
    """The star, wherever a paper is named.

    Server-rendered hollow; `shelf.js` presses it and `index.css` fills the one
    path from `currentColor`. Which papers are starred is the reader's, not the
    corpus's, and the build has no way to know it. The
    title rides along because the shelf keeps a copy of it — a starred paper
    that later leaves the corpus still lists under a name in 서재 rather than
    as a bare id. Nothing without JavaScript can toggle it, so the button
    removes itself there (`index.css`) instead of sitting inert.
    """
    return (
        f'<button type="button" class="{cls}" data-star="{c.esc(paper.stem)}" '
        f'data-star-title="{c.esc(paper.title)}" aria-pressed="false" '
        f'aria-label="즐겨찾기">{c.icon("star", 15)}</button>'
    )


def _size(paper: Paper, *, short: bool = False) -> str:
    """본문 27분 · 용어 18 · 그림 5 — how much of a sit this is.

    Printed before the reader commits, which is the only moment the number is
    worth anything. All three come from what the rewrite already declares.
    `short` drops the figure count and the label for the list, where the column
    heading already says 분량 and the row has one line to give it.
    """
    if short:
        bits = [f"{paper.read_minutes}분"]
        if paper.term_count:
            bits.append(f"용어 {paper.term_count}")
        return " · ".join(bits)
    bits = [f"본문 {paper.read_minutes}분"]
    if paper.term_count:
        bits.append(f"용어 {paper.term_count}")
    if paper.figure_count:
        bits.append(f"그림 {paper.figure_count}")
    return " · ".join(bits)


def _md(renderer, text: str) -> str:
    """Authored markdown where there is a renderer, escaped text where not."""
    return renderer.inline(text) if renderer is not None else c.esc(text)


def _row_readout(paper: Paper) -> str:
    """A row's headline number, on a line of its own under the tagline.

    Riding at the end of the title, the figure lands wherever the title
    happens to wrap — inline on one row, alone on the next line on another —
    and the column loses its rhythm. A fixed slot is what lets a reader run an
    eye down the list and compare results, which is why the number is there.
    """
    if not paper.metric:
        return ""
    return (
        '<span class="row-ro"><span class="row-ro-k">결과</span>'
        f'<span class="row-ro-v">{c.esc(paper.metric)}</span></span>'
    )


def _lead_readout(paper: Paper) -> str:
    """The lead's headline number, at display size and keyed on its left.

    A row gives the figure a slot under its tagline (`_row_readout`); on the
    lead it is the number a reader would quote, so it stands on its own line
    between the thesis it backs and the summary that explains it.
    """
    if not paper.metric:
        return ""
    return (
        '<span class="lead-ro"><span class="lead-ro-k">결과</span>'
        f'<span class="lead-ro-v">{c.esc(paper.metric)}</span></span>'
    )


def _lead_block(paper: Paper, renderer=None) -> str:
    """The newest rewrite, printed rather than summarised.

    A grid of equal cards makes every paper look equally likely to be the one
    you came for. The one that landed most recently is the one a returning
    reader has not seen, so it gets the space — and with it the thesis line, which is
    ours and appears nowhere else on this page.
    """
    links = "".join(
        c.chip(label, "src-link", href=url, mark=c.src_mark(kind))
        for kind, label, url in paper.links
    )
    return f"""<article class="lead" data-lead data-read-of="{c.esc(paper.stem)}">
  <div class="lead-top">
    <span class="lead-flag">가장 최근</span>
    <span class="lead-when">{c.esc(paper.date)} · arXiv {c.esc(paper.stem)}</span>
    <span class="filter-spacer"></span>
    {_star(paper, "leadstar")}
  </div>
  <a class="lead-body" href="p/{c.esc(paper.stem)}/index.html">
    <h2 class="lead-title">{c.esc(paper.title)}</h2>
    <p class="lead-tagline">{_md(renderer, paper.tagline)}</p>
    {_lead_readout(paper)}
    <p class="lead-sum">{_md(renderer, paper.summary_md)}</p>
  </a>
  <div class="lead-foot">
    {c.pillar_chips(paper.filed)}
    {links}
    <span class="filter-spacer"></span>
    <span class="lead-size">{c.esc(_size(paper))}</span>
  </div>
</article>"""


def _row(paper: Paper, renderer=None, *, lead: bool = False) -> str:
    """One paper, one line.

    `data-lead-dup` marks the row the lead block is currently standing in for.
    The row still exists — it has to, or filtering and the other two sorts
    would silently lose a paper — but it ships `hidden`, so with JavaScript
    off the paper appears once (in the lead) instead of twice. The script
    reveals it the moment the lead block stops being the right thing to show.
    """
    # The axes the paper is filed under, which are also the ones the rail
    # counts and filters on — the chips on a row are what a reader checks the
    # rail's number against.
    pillars = c.pillar_chips(paper.filed)
    return f"""<article class="row" data-card{' data-lead-dup hidden' if lead else ''}
  data-read-of="{c.esc(paper.stem)}" {_facets(paper)}>
  {_star(paper)}
  <span class="row-when">{c.esc(paper.date[5:] or paper.date)}</span>
  <span class="row-id">{c.esc(paper.stem)}</span>
  <a class="row-main" href="p/{c.esc(paper.stem)}/index.html">
    <span class="row-title">{c.esc(paper.title)}</span>
    <span class="row-tagline">{_md(renderer, paper.tagline)}</span>
    {_row_readout(paper)}
  </a>
  <span class="row-pillars">{pillars}</span>
  <span class="row-size">{c.esc(_size(paper, short=True))}</span>
</article>"""


# The three lists 서재 holds, in the order a reader meets them: what they
# picked out, where they stopped, what they wrote down.
SHELF_TABS = (
    ("stars", "즐겨찾기"),
    ("marks", "책갈피"),
    ("memos", "메모"),
)


def shelf_page(papers: list[Paper]) -> str:
    """서재 — everything this browser has kept about the corpus.

    Rendered empty and filled from `localStorage`: stars, 읽음 marks and memos
    never reach the build, so there is nothing here to server-render but the
    frame. What turns a kept id back into a row with a link is `corpus_index()`,
    the same file the ⌘K palette searches — every page carries it, so this one
    needs no index of its own. A kept id missing from it is a paper that has
    left the corpus, and 서재 says so rather than dropping it.

    The page is also the export surface, and the only one: a shelf that lives
    in one browser profile reaches a second machine as a file or not at all.
    The two export buttons are printed `disabled` for the same reason the
    lists are printed empty — an empty shelf has nothing to write out, and a
    file that downloads with nothing in it reports a success that did not
    happen. `hub.js` opens them the moment a count is non-zero.
    """
    tabs = "".join(
        f'<button type="button" role="tab" id="sh-t-{key}" aria-controls="sh-{key}" '
        f'aria-selected="{"true" if i == 0 else "false"}" data-shelf-tab="{key}">'
        f'{c.esc(label)} <span class="tab-n" data-tab-count>0</span></button>'
        for i, (key, label) in enumerate(SHELF_TABS)
    )
    panels = "".join(
        f'<section id="sh-{key}" role="tabpanel" aria-labelledby="sh-t-{key}" '
        f'data-shelf-panel="{key}"{"" if i == 0 else " hidden"}></section>'
        for i, (key, label) in enumerate(SHELF_TABS)
    )

    head = c.mast(
        eyebrow="Kept in this browser",
        title="서재, 이 브라우저에만 남습니다",
    )

    body = f"""{head}

<main class="hub" data-hub>
  <div class="hub-tabs" role="tablist" aria-label="서재 보기">{tabs}</div>
  <div class="hub-actions">
    <button type="button" data-hub-action="export-json" disabled>JSON 내보내기</button>
    <button type="button" data-hub-action="export-md" disabled>마크다운 내보내기</button>
    <label class="filebtn">가져오기<input type="file" accept="application/json" data-hub-import hidden></label>
    <span class="filter-spacer"></span>
    <span class="hub-status" data-hub-status aria-live="polite"></span>
  </div>
  {panels}
  <noscript><p class="corpus-empty">서재는 브라우저에 저장되므로 JavaScript 가 필요합니다.</p></noscript>
</main>
"""
    return c.page(
        title="서재 · PROBE",
        here="shelf",
        body=body,
        depth=1,
        scripts=["memo.js", "shelf.js", "hub.js"],
        extra_head=f'<link rel="stylesheet" href="{c.asset("../assets/index.css")}">',
    )


def not_found_page() -> str:
    body = f"""<main class="hub notfound">
  <h1>404</h1>
  <p>이 주소에는 아무것도 없습니다.</p>
  <p><a href="{SITE_BASE}">논문 목록으로 돌아가기</a></p>
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
# worth the long read, and that is the question the short surface answers. `en`
# is printed beside the Korean label because the tab strip is also how a
# contributor finds the rule set: 요약 is `analysis/AUTHORING.md` §4, 상세 is
# §1–§3 and 비교 is `comparison/AUTHORING.md`.
#
# 비교 is not a further reading of this paper and its label does not pretend
# to be: BRIEF and FULL say how much of the paper a surface carries, COMPARED
# says what happened to it. It is also the one tab that is not always there —
# it appears only for a paper some comparison holds, and a tab that is empty
# for most of the corpus is furniture.
TABS = (("glance", "요약", "BRIEF"), ("full", "상세", "FULL"),
        ("cmp", "비교", "COMPARED"))
CMP_TAB = "cmp"


def paper_page(paper: Paper, katex, decisions: dict,
               problems: list[str] | None = None,
               neighbours: list[Paper] | None = None,
               comparisons: list | None = None,
               papers_by_id: dict | None = None,
               citers: list[Paper] | None = None) -> str:
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
    """
    by_id = papers_by_id or {}
    renderer = DocRenderer(
        katex, decisions=decisions,
        siblings={pid: p.title for pid, p in by_id.items()},
        self_id=paper.stem,
    )
    renderer.lead_html = _lead(paper, renderer)
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
    body = f"""{_header(paper)}
{_tabstrip(len(comps))}
<div class="panel wide" id="p-glance" role="tabpanel" aria-labelledby="t-glance">
  {glance_html or _missing("요약")}
</div>
<div class="panel" id="p-full" role="tabpanel" aria-labelledby="t-full" hidden>
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
{c.mark_fab()}
{c.memo_panel(paper.stem, paper.title, f"{BLOB}/analysis/{paper.stem}.md", DISCUSSIONS_NEW)}
"""
    return c.page(
        title=f"{paper.title} · PROBE",
        here="papers",
        description=paper.preview,
        body=body,
        depth=2,
        scripts=["paper.js", "memo.js", "shelf.js"],
        # The source an agent should read instead of this page's markup.
        extra_head=(
            f'<link rel="alternate" type="text/markdown" href="{c.RAW_URL}/analysis/{paper.stem}.md">'),
    )


def _acts(paper: Paper) -> str:
    """즐겨찾기 and 읽음, for this paper, in this browser.

    Both are server-rendered in their empty state and corrected by `shelf.js`
    on load — the build cannot know either one. 읽음 is the reader's claim and
    only ever theirs: neither opening a page nor scrolling to the end of it is
    evidence that it was read, so nothing marks it on their behalf.

    They are glyphs, one joined pair at the right end of the action bar: the
    bar is one line on a phone only while nothing in it is a word it can do
    without, and a star and a check are the two marks this site already draws
    for these two states. What each does and which way it goes is the
    button's accessible name, which `shelf.js` keeps in step with the state.
    """
    return f"""<div class="paper-acts" data-paper-acts
     data-paper-id="{c.esc(paper.stem)}" data-paper-title="{c.esc(paper.title)}">
  <button type="button" class="act-btn" data-star="{c.esc(paper.stem)}"
          data-star-title="{c.esc(paper.title)}" aria-pressed="false"
          aria-label="즐겨찾기" title="즐겨찾기">{c.icon("star", 16)}</button>
  <button type="button" class="act-btn" data-read-toggle aria-pressed="false"
          aria-label="읽음으로 표시" title="읽음으로 표시">{c.icon("check", 16)}</button>
</div>"""


def _tabstrip(cmp_n: int = 0) -> str:
    """The tabs. Server-rendered and `hidden`-toggled, so the page is readable
    with JavaScript off — the first panel stays open and the rest are reachable
    by their anchors.

    비교 is printed only when there is something behind it, and it carries its
    count: the number is the whole reason to look, and a tab that made the
    reader click to find out it says zero would have spent their click to tell
    them nothing.
    """
    buttons = []
    for i, (key, label, en) in enumerate(TABS):
        if key == CMP_TAB and not cmp_n:
            continue
        count = (f'<span class="cnt">{cmp_n}</span>' if key == CMP_TAB else "")
        buttons.append(
            f'<button type="button" class="tab" role="tab" id="t-{key}" '
            f'aria-controls="p-{key}" aria-selected="{"true" if i == 0 else "false"}" '
            f'data-tab="{key}">{c.esc(label)} '
            f'<span class="en">{c.esc(en)}</span>{count}</button>'
        )
    return (f'<div class="tabs-wrap"><div class="tabs" role="tablist" '
            f'aria-label="논문 보기 방식">{"".join(buttons)}</div></div>')


def _missing(name: str) -> str:
    """A surface the rewrite does not carry.

    Printed rather than silently empty: the build already reported it, and a
    reader who clicked the tab deserves to know the tab is empty because the
    rewrite is incomplete, not because the page broke.
    """
    return (f'<p class="corpus-empty">이 재작성본에는 아직 {c.esc(name)} 섹션이 '
            f'없습니다 — <code>/analyze &lt;id&gt; --refresh</code> 로 다시 씁니다.</p>')




def _related(neighbours: list[Paper]) -> str:
    """The nearest rewrites, at the end of the one just read.

    Placed after the article rather than in the sidebar: it is a next step, not
    a navigation aid, and it should not compete with the table of contents
    while there is still text above it. Empty when nothing shares a Decision-Log
    code or a pillar — see `corpus.related`.
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

    The same fork the list draws, with this paper's branch marked — which is
    what makes the card a position rather than a list: not only that these
    papers were on one table, but which answer was this one's.
    """
    return (
        f'<a class="incmp-item" href="../../c/{c.esc(comp.slug)}/index.html">'
        f'<span class="incmp-when">{c.esc(comp.date)}</span>'
        f'<span class="incmp-t">{c.esc(comp.title)}</span>'
        f"{_fork(comp, papers_by_id, mark=paper.stem)}</a>"
    )


def _lead(paper: Paper, renderer: DocRenderer) -> str:
    """`tagline` and `summary`, printed between the thesis line and act 1.

    A reader arriving here needs to know what the next 400 lines will argue
    before paragraph one starts arguing it, and the front matter already
    carries that sentence. Both go through the inline renderer rather than
    `esc()`: the emphasis in a summary is what makes it scannable, and a
    summary that opens with math is common enough that escaping it would
    publish backticks.
    """
    out = ""
    if paper.tagline:
        out += f'<p class="thesis-sub">{renderer.inline(paper.tagline)}</p>\n'
    if paper.summary_md:
        out += (
            '<div class="tldr"><span class="tldr-label">한 문단 요약</span>'
            f"<p>{renderer.inline(paper.summary_md)}</p></div>\n"
        )
    return f"\n{out}" if out else ""


def _toc(entries: list[dict]) -> str:
    """Table of contents, grouped under its acts and rendered server-side.

    Built from the renderer's own heading pass rather than scraped from the DOM
    by `paper.js`: the act grouping and the English keyword line are structure
    the renderer knows and the rendered HTML does not spell out. Server-side
    also means the contents survive with JavaScript off, which for a document
    this long is the difference between a page you can navigate and a scroll.
    """
    if not entries:
        return ""
    groups: list[str] = []
    open_group = False
    for entry in entries:
        if entry.get("kind") == "act":
            if open_group:
                groups.append("</div>")
            groups.append(
                '<div class="toc-grp"><div class="toc-gh">'
                f'<span class="toc-n">{c.esc(entry["n"])}</span>'
                f'<span class="toc-gl">{c.esc(entry["label"])}</span></div>'
            )
            open_group = True
            continue
        # Each entry is wrapped rather than bare: `shelf.js` hangs the 책갈피
        # button off the row, and a button inside the anchor would be both
        # invalid and un-clickable without swallowing the link.
        link = (
            '<div class="toc-row">'
            f'<a href="#{c.esc(entry["id"])}">'
            f'<span class="toc-k">{c.esc(entry["label"])}</span>'
            + (f'<span class="toc-e">{c.esc(entry["en"])}</span>' if entry.get("en") else "")
            + "</a></div>"
        )
        if not open_group:
            groups.append('<div class="toc-grp">')
            open_group = True
        groups.append(link)
    if open_group:
        groups.append("</div>")
    return '<div class="toc-title">목차</div>' + "".join(groups)


def _header(paper: Paper) -> str:
    """What the paper is, and the one line of things to do with it.

    Under the title there are exactly two kinds of thing — who wrote it, and a
    bar of what a reader can press — and the bar is ruled off from the rest so
    it reads as controls rather than as more facts. Everything in the bar is
    one line at a phone's width whatever the paper declares, which is why the
    header carries no headline number and no length: the number is the first
    thing the 요약 tab directly below prints, with its context, and a chip of
    variable length here was what decided where the links wrapped.

    The only date is the rewrite's own, on the breadcrumb line. When the paper
    itself appeared is already in its arXiv id; when this corpus read it is
    not recoverable from anything else on the page.

    Where else on this site the paper is argued about is the 비교 tab's job:
    the tab strip sits directly under this header and carries the count.
    """
    return f"""<header class="paper-head">
  <div class="paper-head-inner">
    <div class="crumb-row">
      <div class="crumb">
        <a href="../../index.html">분석</a> ›
        <a href="../../index.html#p={c.esc(paper.primary)}">{c.esc(paper.primary)}</a> ›
        {c.esc(paper.stem)}
      </div>
      {f'<span class="crumb-date">재작성 {c.esc(paper.date)}</span>' if paper.date else ""}
    </div>
    <h1 class="paper-title">{c.esc(paper.title)}</h1>
    {_authors(paper)}
    <div class="actbar">
      {_src_group(paper)}
      {_acts(paper)}
    </div>
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
    """Every link out of the site, as one joined group.

    One bordered box divided into cells, so the bar reads as two things — where
    the paper lives, and the pair of 서재 controls — rather than as a row of
    loose buttons. Empty when a rewrite declares no link, which R10 allows and
    which is itself reproducibility information.
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
    """One comparison — the papers as cards, then the argument.

    The card row is where the track's constraint pays off. Every compared paper
    is guaranteed to have a rewrite, so the page can state what the three
    papers *are* entirely from front matter already written — title, tagline,
    headline metric, pillars, and a link to the full read. Nothing here is
    authored twice.

    That is what lets the contract forbid the prose from introducing anybody:
    the introduction is already on the page, so the first sentence of act 1 can
    go straight at the divergence, and a reader who wants one paper's detail
    has a door to it rather than a paragraph about it.

    None of the 서재 layer is here — 즐겨찾기, 읽음, 책갈피 and 메모 are all keyed
    by arXiv id, and a comparison has a slug. Rather than ship controls that
    cannot resolve, the page ships none: `paper.js` alone, for the term anchors
    a shared vocabulary panel needs.
    """
    papers = [papers_by_id[pid] for pid in comp.paper_ids]
    heads = [(p.stem, _alias(p), f"../../p/{p.stem}/index.html") for p in papers]

    renderer = DocRenderer(katex, decisions=decisions, kind="compare",
                           matrix_heads=heads,
                           siblings={pid: p.title
                                     for pid, p in papers_by_id.items()})
    renderer.lead_html = _cmp_lead(comp, renderer)
    rendered = renderer.render(comp.body)
    if problems is not None:
        problems.extend(f"comparison/{comp.slug}.md: {p}" for p in renderer.problems)

    body = f"""{_cmp_header(comp)}
{_cmp_cards(papers)}
<div class="shell one">
  <main class="article">
    <section class="view">{rendered}</section>
  </main>
</div>
"""
    return c.page(
        title=f"{comp.title} · PROBE",
        here="compare",
        description=comp.preview,
        body=body,
        depth=2,
        scripts=["paper.js"],
        extra_head=f'<link rel="alternate" type="text/markdown" href="{c.RAW_URL}/comparison/{comp.slug}.md">',
    )


def _alias(paper: Paper) -> str:
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
# A comparison's list card draws `stances:` and `common:` (comparison/
# AUTHORING.md §2-1) rather than its tagline: a branch per paper for what it
# does, the trunk for what they all accept. The branch carries the alias AND
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
        f'{c.esc(_alias(papers_by_id[pid]) if pid in papers_by_id else pid)}</span>'
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
    pillars = c.pillar_chips(comp.pillars)
    return f"""<header class="paper-head">
  <div class="paper-head-inner">
    <div class="crumb-row">
      <div class="crumb">
        <a href="../index.html">비교</a> › {c.esc(comp.slug)}
      </div>
    </div>
    <h1 class="paper-title">{c.esc(comp.title)}</h1>
    {f'<div class="chip-row head-facts">{pillars}</div>' if pillars else ""}
    <div class="metaline"><span class="mi">{c.esc(comp.date)}</span><span class="mi">논문 {len(comp.paper_ids)}편</span></div>
  </div>
</header>"""


def _cmp_lead(comp, renderer: DocRenderer) -> str:
    out = ""
    if comp.tagline:
        out += f'<p class="thesis-sub">{renderer.inline(comp.tagline)}</p>\n'
    if comp.summary_md:
        out += (
            '<div class="tldr"><span class="tldr-label">한 문단 요약</span>'
            f"<p>{renderer.inline(comp.summary_md)}</p></div>\n"
        )
    return f"\n{out}" if out else ""


def _cmp_cards(papers: list[Paper]) -> str:
    """Who the compared papers are, drawn entirely from their own front matter.

    In `compares:` order, which is the comparison author's order and the same
    one every ```probe-matrix column runs in — so the third card and the third
    column are the same paper wherever the reader is on the page.
    """
    cards = "".join(
        f'<a class="cmp-card" href="../../p/{c.esc(p.stem)}/index.html">'
        f'<span class="cmp-card-p">{c.pillar_chips(p.filed)}</span>'
        f'<span class="cmp-card-t">{c.esc(p.title)}</span>'
        f'<span class="cmp-card-tag">{c.esc(p.tagline)}</span>'
        f'<span class="cmp-card-foot">'
        f'<span class="cmp-card-id">{c.esc(p.stem)}</span>'
        + (f'<span class="cmp-card-m">{c.esc(p.metric)}</span>' if p.metric else "")
        + "</span></a>"
        for p in papers
    )
    return (
        '<section class="cmp-cards">'
        '<h2 class="cmp-cards-h">읽은 논문</h2>'
        f'<div class="cmp-card-row">{cards}</div>'
        "</section>"
    )


def _ix_foot(count: str) -> str:
    """The table's last line: that it ends.

    A short list otherwise stops on a row rule with the page running on under
    it, and a reader cannot tell a list that is complete from one that has not
    finished arriving. The count says the former.
    """
    return (f'<div class="ix-foot">'
            f'<span class="ix-end">목록 끝 · {c.esc(count)}</span></div>')


def comparison_index_page(comps: list, papers_by_id: dict) -> str:
    """비교 — every comparison, newest first.

    A row carries the question, then the fork: what each paper does about it and
    what they all accept. The tagline is not printed here — it is the same
    thought as prose, and it prints under the H1 on the comparison's own page.
    Around it the landing list's columns: when, the comparison's axes, and how
    many papers it holds.
    """
    ordered = sorted(comps, key=lambda x: x.order_key, reverse=True)
    if ordered:
        rows = "".join(
            f'<a class="cmp-item ix-row ix-cmp" href="{c.esc(x.slug)}/index.html">'
            f'<span class="ix-when">{c.esc(x.date[5:] or x.date)}</span>'
            f'<span class="ix-main">'
            f'<span class="cmp-item-t">{c.esc(x.title)}</span>'
            f"{_fork(x, papers_by_id)}</span>"
            f'<span class="ix-pillars">{c.pillar_chips(x.pillars)}</span>'
            f'<span class="ix-size">{len(x.paper_ids)}편</span></a>'
            for x in ordered
        )
        list_html = (
            '<div class="ix-head ix-cmp" aria-hidden="true"><span>작성</span>'
            '<span>질문 · 공통 → 갈래</span><span>연구 축</span><span>논문</span></div>'
            f'<div class="cmp-list">{rows}</div>'
            + _ix_foot(f"비교 {len(ordered)}건")
        )
    else:
        list_html = '<p class="corpus-empty">아직 비교한 글이 없습니다.</p>'

    head = c.mast(
        eyebrow="Side by side",
        title="비교, 갈리는 자리만 봅니다",
    )

    body = f"""{head}

<main class="hub hub-wide">
  {list_html}
</main>
"""
    return c.page(
        title="비교 · PROBE",
        here="compare",
        body=body,
        depth=1,
        extra_head=f'<link rel="stylesheet" href="{c.asset("../assets/index.css")}">',
    )


# ── 탐색 ────────────────────────────────────────────────────────────────────
# One page per run date, every pillar on it, and an index of the dates. The
# reports are written per pillar for the routine's sake — one context file and
# one window each — and read per date for the reader's: what did this run turn
# up, and which of it did more than one axis notice.

# Where a pick sits in its pillar's report, as the row prints it. Words, not
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
    return c.chip(f"{pick.pillar} · {_PICK_LABEL[pick.kind]}", "pillar",
                  data={"p": pick.pillar})


# A figure in a report's prose — `1,880.2시간`, `84.0%`, `5개` — is what a
# reader scanning a row is looking for, so the page marks it. A digit inside a
# code (`D4QX`) or an id is not a figure.
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


def _bullets(md: str) -> list[str]:
    return [line[2:].strip() for line in md.splitlines() if line.startswith("- ")]


# The (c) headline's limit (`scouting/AUTHORING.md` §2-2). A reading whose
# first line runs past it predates the rule and is drawn as plain prose.
_HEADLINE_MAX = 50


def _scout_axis(pick, decisions: dict) -> str:
    """One pillar's reading of the paper: its rank and its headline on one
    line, and the rest of what it wrote under them, quieter. A 📋 row has only
    its one line."""
    if not pick.full:
        return (f'<div class="sc-ax sc-ax-row"><p class="sc-ax-h">{_scout_chip(pick)}'
                f'<span>{_figures(_scout_md(pick.gist, decisions, inline=True))}</span></p></div>')
    lines = [_figures(_scout_md(l, decisions, inline=True))
             for l in (_bullets(pick.implic) or [pick.implic])]
    raw = (_bullets(pick.implic) or [pick.implic])[0]
    long = ' class="sc-ax-long"' if len(_plain_text(raw)) > _HEADLINE_MAX else ""
    head = f'<p class="sc-ax-h">{_scout_chip(pick)}<span{long}>{lines[0]}</span></p>'
    rest = "".join(f"<li>{l}</li>" for l in lines[1:])
    return f'<div class="sc-ax">{head}' + (f'<ul class="sc-ax-t">{rest}</ul>' if rest else "") + "</div>"


# What the paper's Real score says about its hardware evidence, in the words
# `scouting/AUTHORING.md` §5-3 gives the page. The rubric's numbers rank the
# papers and stay in the report; a reader deciding what to open needs only
# whether the result stands on a robot, said in words.
_REAL_LABEL = {3: "실물 정량, 다수 과제", 2: "실물 정량 결과", 1: "실물 시연만", 0: "실물 결과 없음"}


# The brief's six fields read as three steps of one argument — why the paper
# exists, how it answers, what it leaves — and the card draws the steps so the
# eye finds the field it wants by where it sits, not by reading every label.
_BRIEF_STEPS = (("문제의식", ("문제", "기존 한계")),
                ("접근", ("핵심 방법", "차별점")),
                ("성과", ("핵심 기여", "가치")))


def _scout_brief(brief: list[tuple[str, str]], decisions: dict) -> str:
    """(b)'s labelled fields as one card (AUTHORING §2-2)."""
    fields = dict(brief)
    steps = []
    for step, labels in _BRIEF_STEPS:
        rows = "".join(
            f'<div class="sc-bf"><dt>{c.esc(label)}</dt>'
            f'<dd>{_figures(_scout_md(fields[label], decisions))}</dd></div>'
            for label in labels)
        steps.append(f'<div class="sc-bstep" data-step="{c.esc(step)}">'
                     f'<span class="sc-bstep-h">{c.esc(step)}</span><dl>{rows}</dl></div>')
    return f'<section class="sc-blk sc-brief"><h3>논문 요지</h3>{"".join(steps)}</section>'


def _after_headline(md: str) -> str:
    """A pick's "what" with its first bullet — the row's headline — taken out."""
    lines = md.splitlines()
    first = next((i for i, l in enumerate(lines) if l.startswith("- ")), None)
    if first is None:
        return md
    return "\n".join(lines[:first] + lines[first + 1:]).strip()


def _plain_text(md: str) -> str:
    return re.sub(r"\]\([^)]*\)|[*`\[\]]", "", md)


def _scout_name(paper) -> str:
    """The paper's own name: its title as the authors wrote it, the codename
    in bold only where the title opens on it (`WB-WAM: Heterogeneous …`). A
    name the title does not carry is never printed as if it were the paper's
    — a reader searching arXiv for it finds nothing. A 📋 row carries no
    title, only its `Paper` cell, which `scouting/AUTHORING.md` §7-2 makes
    that same codename or the full title; a cell with a space in it is read
    as a title."""
    title, alias = paper.title, paper.alias
    if title:
        head, colon, rest = title.partition(":")
        if colon and rest.strip() and head.strip() == alias:
            return (f'<b class="sc-cn">{c.esc(alias)}</b>'
                    f'<span class="sc-rest">: {c.esc(rest.strip())}</span>')
        return f'<span class="sc-whole">{c.esc(title)}</span>'
    if " " in alias:
        return f'<span class="sc-whole">{c.esc(alias)}</span>'
    return f'<b class="sc-cn">{c.esc(alias)}</b>'


def _scout_rail(paper_id: str) -> str:
    """The paper's arXiv id in front of the row, linking its abstract, open
    without opening the row. The arXiv page is the one door: its own links
    reach the HTML edition and the PDF. A column of ids down the list also
    reads against a report or a run file by eye."""
    pid = c.esc(paper_id)
    return (f'<span class="sc-rail"><a class="sc-id" href="https://arxiv.org/abs/{pid}" '
            f'target="_blank" rel="noopener" title="arXiv 초록">{pid}'
            f'<span aria-hidden="true">↗</span></a></span>')


def _scout_item(paper, decisions: dict, papers_by_id: dict, up: str) -> str:
    lead = paper.lead
    picks = sorted(paper.picks, key=lambda p: (not p.full, p.rank))
    chips = "".join(_scout_chip(p) for p in picks)
    rewrite = (f'<a class="sc-rw" href="{up}p/{c.esc(paper.paper_id)}/index.html">재작성본</a>'
               if paper.paper_id in papers_by_id else "")
    # Code that is out or promised is something to act on; 코드 미공개 is not,
    # so the row prints nothing for it. Beside it, whether the result stands
    # on a robot — the one part of the rubric a reader decides by.
    code = "" if paper.code == "코드 미공개" else c.esc(paper.code)
    real = lead.dims.get("Real")
    real = f"<span>{_REAL_LABEL[real]}</span>" if real is not None else ""
    code = f"<span>{code}</span>" if code else ""
    code = (f'<span class="sc-code">{real}{code}{rewrite}</span>'
            if code or real or rewrite else "")
    meta = " · ".join(c.esc(m) for m in lead.meta)
    axes = "".join(_scout_axis(p, decisions) for p in picks)
    # Two columns and nothing across their foot: what the paper is on the
    # left, and on the right the judgement — what it means for each axis,
    # then what to check first. The right column is the short one, so it
    # stays beside the reader while the left runs on (`scout.js` pins it
    # when it fits the screen), and on a phone it comes first. The row
    # already prints the first "what" line as its headline, so the open row
    # starts at the second. A paper no pillar wrote up has only its axis
    # rows, and one 📋 row has nothing to open.
    why = f'<section class="sc-blk"><h3>연구 축별 시사점</h3><div class="sc-axes">{axes}</div></section>'
    if lead.full:
        contrib = _after_headline(lead.contrib)
        if lead.brief:
            what = _scout_brief(lead.brief, decisions)
        else:
            what = (f'<section class="sc-blk"><h3>무엇인가</h3>'
                    f'{_figures(_scout_md(contrib, decisions))}</section>' if contrib else "")
        check = (f'<section class="sc-blk sc-check"><h3>먼저 확인할 점</h3>'
                 f'{_figures(_scout_md(lead.check, decisions))}</section>')
        judge = f'<div class="sc-stack sc-judge">{why}{check}</div>'
        body = f'<div class="sc-cols2">{what}{judge}</div>' if what else judge
    elif len(picks) == 1:
        body = ""
    else:
        body = why
    row = (f'{_scout_rail(paper.paper_id)}'
           f'<span class="sc-main"><span class="sc-t">{_scout_name(paper)}</span>'
           f'<span class="sc-gist">{_scout_md(paper.gist, decisions, inline=True)}</span></span>'
           f'<span class="sc-side"><span class="sc-picks">{chips}</span>{code}</span>')
    attrs = f'id="p-{c.esc(paper.paper_id)}" data-pillars="{" ".join(paper.pillars)}"'
    if not body:
        return f'<div class="sc-item" {attrs}><div class="sc-row sc-flat">{row}</div></div>'
    foot = f'<p class="sc-links">{meta}</p>' if meta else ""
    return (f'<details class="sc-item" {attrs}><summary class="sc-row">{row}</summary>'
            f'<div class="sc-body">{body}{foot}</div></details>')


def _scout_status(run) -> str:
    """What the run holds, as four counts, and any pillar it has no report
    for. The pillars that did arrive are the filter's chips, so they are not
    printed twice; their reports are linked at the foot of the page."""
    missing = "".join(f'<span class="chip sc-missing">{p} {c.esc(why)}</span>'
                      for p, why in run.missing.items())
    shared = sum(1 for p in run.papers if p.group == "shared")
    asked = len(run.arrived) + len(run.missing)
    stats = (("게이트 통과", f"{len(run.papers)}", "편"),
             ("여러 연구 축이 지목", f"{shared}", "편"),
             ("근접 후보", f"{len(run.near)}", "편"),
             ("연구 축", f"{len(run.arrived)}", f"/{asked}"))
    tiles = "".join(f'<div><dt>{c.esc(k)}</dt><dd>{v}<small>{c.esc(u)}</small></dd></div>'
                    for k, v, u in stats)
    return (f'<div class="sc-status"><dl class="sc-stats">{tiles}</dl>'
            + (f'<span class="sc-arrive">{missing}</span>' if missing else "") + "</div>")


def _scout_runs(runs: list, here: str, up_to_s: str) -> str:
    """The way to the other runs: one step older, one step newer, and every run
    by month behind the run on screen.

    One line however many runs there are — a run a week is a hundred runs in
    two years, and a row of a hundred tabs is a row nobody can find a date in.
    The neighbours cover the common move, reading back one run at a time; the
    month list covers the rare one, going to a date. The list is a native
    `<details>`, so it opens with no script; `scout.js` only closes it when the
    reader clicks away."""
    i = next(k for k, r in enumerate(runs) if r.date == here)
    run = runs[i]

    def href(date: str) -> str:
        return f"{up_to_s}{date}/index.html"

    older = (f'<a class="sc-step" href="{href(runs[i + 1].date)}" rel="prev">'
             f'← {c.esc(runs[i + 1].date[5:])}</a>' if i + 1 < len(runs)
             else '<span class="sc-step" aria-hidden="true"></span>')
    newer = (f'<a class="sc-step sc-newer" href="{href(runs[i - 1].date)}" rel="next">'
             f'{c.esc(runs[i - 1].date[5:])} →</a>' if i > 0
             else '<span class="sc-step" aria-hidden="true"></span>')
    months: dict[str, list] = {}
    for r in runs:
        months.setdefault(r.date[:7], []).append(r)
    current = ' aria-current="page"'
    menu = "".join(
        f'<div class="sc-mo"><span class="sc-mo-h">{c.esc(month)}</span><span class="sc-mo-l">'
        + "".join(f'<a href="{href(r.date)}"{current if r.date == here else ""}>'
                  f'{c.esc(r.date[8:])}<small>{len(r.papers)}</small></a>' for r in members)
        + "</span></div>"
        for month, members in months.items())
    return (
        '<nav class="sc-runs" aria-label="회차">'
        f"{older}"
        '<details class="sc-pick" data-scout-pick>'
        f'<summary><h2 class="sc-date">{c.esc(run.date)}</h2>'
        f'<span class="sc-pick-n">{len(run.papers)}편 · 회차 {len(runs)}개</span></summary>'
        f'<div class="sc-menu">{menu}</div></details>'
        f"{newer}</nav>"
    )


def _scout_filter(run_pillars: list[str]) -> str:
    """Which pillars to show, and the one switch that opens every row.

    Scripted only — `scout.js` wires it and `scout.css` keeps it off an
    unscripted page, which gets every row closed and the browser's own
    disclosure to open each."""
    pills = "".join(
        f'<button type="button" class="chip pillar" data-p="{p}" aria-pressed="false" '
        f'data-scout-p="{p}">{p} {c.esc(PILLAR_LABELS[p])}</button>'
        for p in run_pillars)
    return (f'<div class="sc-filter" role="group" aria-label="연구 축으로 거르기">{pills}'
            '<span class="filter-spacer"></span>'
            '<button type="button" class="sc-open" data-scout-open aria-pressed="false">모두 펼치기</button>'
            '<span class="sc-shown" data-scout-shown aria-live="polite"></span></div>')


# The band every scouting page opens on. It names the surface and what it
# does, as the other four bands do; which run is on screen is the page's
# business, under the band, so the band is the same on every run.
SCOUT_EYEBROW = "Across the research axes"
SCOUT_TITLE = "탐색, 읽을 논문을 먼저 고릅니다"


def scouting_run_page(run, runs: list, decisions: dict, papers_by_id: dict,
                      *, depth: int) -> str:
    """One run, every pillar's surfaced papers on one list.

    Each paper is one row however many pillars surfaced it, and the row is
    closed: what the paper is in one line, which pillars flagged it at what
    rank. Opened, it shows each pillar's reading side by side and the
    paper's own contribution and caveats once, so the list scans as rows
    rather than reads as write-ups.

    The page is printed twice for the newest run: at `s/` — where the nav
    lands, so a reader arrives on what came in last — and at `s/<date>/`, the
    address that stays put once a newer run takes `s/`. `depth` is which of
    the two this is.
    """
    up = "../" * depth
    up_to_s = "" if depth == 1 else "../"

    # Every group folds under its head. The last one — the papers no pillar
    # wrote up, one 📋 row each — starts folded: it is the part of the run a
    # reader goes looking in, not the part that should push the write-ups off
    # the screen.
    def group(key: str, label: str, members: list) -> str:
        rows = "".join(_scout_item(p, decisions, papers_by_id, up) for p in members)
        return (f'<details class="sc-group sc-fold" data-scout-group'
                f'{"" if key == "rest" else " open"}>'
                f'<summary class="sc-gh"><h2>{c.esc(label)}</h2>'
                f'<span class="sc-gn">{len(members)}편</span></summary>{rows}</details>')
    groups = "".join(group(*g) for g in run.grouped())
    if not groups:
        groups = '<p class="corpus-empty">이 회차에 게이트를 통과한 논문이 없습니다.</p>'

    near = run.near
    near_html = ""
    if near:
        rows = "".join(
            f'<tr><td><a href="https://arxiv.org/abs/{c.esc(n.paper_id)}" target="_blank" '
            f'rel="noopener"><b>{c.esc(n.alias)}</b></a></td>'
            f'<td>{c.chip(n.pillar, "pillar", data={"p": n.pillar})}</td>'
            f'<td>{_scout_md(n.condition, decisions, inline=True)}</td></tr>'
            for n in near)
        # Folded under the same head the groups above use: it is one more
        # cut of the run's papers, the ones a single gate axis kept out.
        near_html = (
            '<details class="sc-group sc-fold">'
            f'<summary class="sc-gh"><h2>근접 후보</h2><span class="sc-gn">{len(near)}편</span></summary>'
            '<div class="sc-scroll"><table class="sc-table"><thead><tr><th>논문</th><th>연구 축</th>'
            f'<th>재검토 조건</th></tr></thead><tbody>{rows}</tbody></table></div>'
            "</details>")
    # A pillar's own 🔄 compares it with its earlier reports — the routine's
    # working record, read in the pillar's file. The page reads the run as a
    # whole and links the files.
    sources = " · ".join(
        f'<a href="{BLOB}/{c.esc(r.source)}" target="_blank" rel="noopener">{r.pillar}</a>'
        for r in run.reports)
    if run.run_file:
        sources += (f' · <a href="{BLOB}/scouting/runs/{c.esc(run.date)}.md" target="_blank" '
                    'rel="noopener">회차</a>')
    sources_html = f'<p class="sc-sources">원본 리포트 · {sources}</p>'

    head = c.mast(eyebrow=SCOUT_EYEBROW, title=SCOUT_TITLE)
    body = f"""{head}

<main class="hub hub-wide sc" data-scout>
  {_scout_runs(runs, run.date, up_to_s)}
  {_scout_status(run)}
  {_scout_filter(run.arrived)}
  {groups}
  {near_html}
  {sources_html}
</main>
"""
    return c.page(
        title=f"{run.date} 탐색 · PROBE",
        here="scout",
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
