"""Page assemblers."""

from __future__ import annotations

import json
from collections import Counter

from . import components as c
from . import corpus, presentations, glance as glance_mod
from .corpus import PILLAR_LABELS, PILLAR_NAMES, PILLAR_ORDER, Paper
from .render import DocRenderer

# Pages serves a project site under /<repo>/. Only 404.html uses this; every
# other page is depth-relative and needs no knowledge of where it is hosted.
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
    id, the title, the tags and the 연구 축, and shows the tagline under each
    title — which is also the only Korean any of those fields carry, since
    titles and tags in this corpus are the paper's own English. 서재 turns a
    kept id back into a titled, taglined row with the same records.

    Both pillar vocabularies ride along so either surface can match a query
    against an axis without carrying the dicts: the Korean label because a
    reader reads it off the rail and may type it here, and the English name
    because the papers themselves are English and a reader may type that
    instead. Neither is printed — a row marks its axes with the id, which is
    what the chips beside it are keyed to.

    **Two kinds, one payload.** `comparisons` sits beside `papers` because the
    palette is the only way to reach a document from a page that is not a list,
    and a comparison the palette cannot find is a comparison reachable only
    from a paper it already names — which is the one place a reader who wants
    it is least likely to be. The two arrays stay separate rather than merging
    under a `kind` field: they are keyed differently (an arXiv id against a
    slug), they land at different depths, and 서재 reads only the first —
    shelf records are kept per arXiv id, so a comparison has nothing there to
    look up.

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
             "pillars": p.filed, "tags": p.tags, "date": p.date}
            for p in ordered
        ],
        "comparisons": [
            {"slug": x.slug, "title": x.title, "tagline": x.tagline,
             "pillars": x.pillars, "tags": x.tags, "date": x.date,
             "of": x.paper_ids}
            for x in ranked
        ],
    }
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return f"window.ProbeIndex={body};\n"


def _shelf_facets(cls: str) -> str:
    """New / Starred, in whichever of its two homes.

    Server-rendered with a zero count and no pressed state, because which
    papers are starred or new is the reader's and the build cannot know either.
    New ships `hidden` and stays hidden until there is something new to point
    at — a zero that never moves is furniture.

    Both name something the reader put there. What is left to read is not a
    mark anyone made: on a corpus a reader has barely started it counts almost
    every paper, which selects the list they are already looking at. 읽음 is
    still kept and still listed — in 서재, where the papers a reader is done
    with are the point — it just has no facet here.
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
                 comps: list | None = None) -> str:
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

    A paper that has been read against others carries a count beside its
    title, in the lead block and in every row alike. It is the only signal on
    this page that points at the other track, and it is here rather than only
    on the paper because whether a paper has been argued against something is
    part of deciding to open it.

    Order is `Paper.order_key` — the order the rewrites landed on `main`, which
    is the order a reader watched them appear — and the rows carry that key on
    `data-order`, so the script's 최신순 reproduces this list rather than a
    near-miss of it.

    How large the corpus is and how fresh it is are stated once, in the filter
    bar: the count there is the live one — it answers 몇 편 after a filter as
    well as before — so a second, fixed count in the masthead would be the same
    number twice on one screen, and only one of them would ever move. The
    masthead carries the same pair for the reader whose page is unscripted and
    who therefore has no filter bar; `index.css` hides it once a script runs.
    """
    ordered = sorted(papers, key=lambda p: p.order_key, reverse=True)
    cmp_counts = Counter(pid for x in (comps or []) for pid in x.paper_ids)

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
    # header, and the masthead's own title and lead.
    #
    # The pair is printed twice, once for the rail and once for the filter bar,
    # because the rail leaves at 900px and these two would leave with it — and
    # unlike the 연구 축 below them, nothing else on a phone can reach what
    # they select. Exactly one copy is ever on screen (`index.css`);
    # `filter.js` binds every copy it finds, so the pair never disagrees.
    rail_mine = _shelf_facets("rail-item mine")
    bar_mine = _shelf_facets("barflag")
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
        _row(p, renderer, lead=(i == 0), cmp_n=cmp_counts[p.stem])
        for i, p in enumerate(ordered)
    )

    head = c.mast(
        eyebrow="Dexterous manipulation",
        title="논문, 읽기 좋게 옮겨 둡니다",
        art=c.mast_art(),
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
    {_seg("정렬", "", '<button type="button" data-sort="recent" aria-pressed="true">최신순</button>'
                      '<button type="button" data-sort="pillar" aria-pressed="false">연구 축별</button>'
                      '<button type="button" data-sort="title" aria-pressed="false">제목순</button>')}
    {_seg("한 쪽에 몇 편", "psize", _page_sizes())}
    <div class="barflags" role="group" aria-label="서재">{bar_mine}</div>
    <span class="filter-spacer"></span>
    <span class="status"><span data-result-count>{len(ordered)}편</span>{
      f'<span data-corpus-when> · <span class="when-word">최근 </span>'
      f'{c.esc(ordered[0].date)}</span>' if ordered else ""}</span>
    <button type="button" class="linkish" data-reset hidden>필터 초기화</button>
  </div>
</div>

<div class="deck">
  <aside class="rail" data-rail>
    <p class="rail-h" data-mine-h>서재</p>
    {rail_mine}
    <p class="rail-h">연구 축</p>
    {rail_pillars}
  </aside>
  <main class="corpus" data-corpus>
    {_first_run() if not ordered else ""}
    {_resume()}
    {_lead_block(ordered[0], renderer, cmp_counts[ordered[0].stem]) if ordered else ""}
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
        extra_head=f'<link rel="stylesheet" href="{c.asset("assets/index.css")}">',
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
        f'data-tags="{c.esc(" ".join(paper.tags))}" '
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


def _cmp_count(n: int) -> str:
    """How many comparisons hold this paper, wherever the paper is listed.

    A count and not a link: the row already goes somewhere, and the paper's own
    header carries the door. What this says is only that the door is there,
    which is the thing a reader deciding what to open cannot otherwise know.
    """
    if not n:
        return ""
    return (
        f'<span class="cmp-n" title="같이 읽은 글 {n}편" '
        f'aria-label="같이 읽은 글 {n}편"><span aria-hidden="true">↔</span>{n}</span>'
    )


def _metric_chip(paper: Paper) -> str:
    return (
        f'<span class="metric">{c.esc(paper.metric)}</span>' if paper.metric else ""
    )


def _lead_block(paper: Paper, renderer=None, cmp_n: int = 0) -> str:
    """The newest rewrite, printed rather than summarised.

    A grid of equal cards makes every paper look equally likely to be the one
    you came for. The one that landed most recently is the one a returning
    reader has not seen, so it gets the space — and with it the thesis line, which is
    ours and appears nowhere else on this page.
    """
    tag_buttons = "".join(
        f'<button type="button" class="chip tag" data-tag-jump="{c.esc(t)}">{c.esc(t)}</button>'
        for t in paper.tags[:3]
    )
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
    <p class="lead-sum">{_md(renderer, paper.summary_md)}</p>
  </a>
  <div class="lead-foot">
    {c.pillar_chips(paper.filed)}
    {_metric_chip(paper)}
    {_cmp_count(cmp_n)}
    {tag_buttons}
    {links}
    <span class="filter-spacer"></span>
    <span class="lead-size">{c.esc(_size(paper))}</span>
  </div>
</article>"""


def _row(paper: Paper, renderer=None, *, lead: bool = False,
         cmp_n: int = 0) -> str:
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
    <span class="row-title">{c.esc(paper.title)}{_metric_chip(paper)}{_cmp_count(cmp_n)}</span>
    <span class="row-tagline">{_md(renderer, paper.tagline)}</span>
  </a>
  <span class="row-pillars">{pillars}</span>
  <span class="row-size">{c.esc(_size(paper, short=True))}</span>
</article>"""


# The four lists 서재 holds, in the order a reader meets them: what they
# picked out, what they got through, where they stopped, what they wrote down.
SHELF_TABS = (
    ("stars", "즐겨찾기"),
    ("reads", "읽은 논문"),
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
        art=c.shelf_art(),
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
# §1–§3, and 비교 is a different contract altogether.
#
# 비교 and 발표 are not further readings of this paper and their labels do not
# pretend to be: BRIEF and FULL say how much of the paper a surface carries,
# COMPARED says what happened to it, and TALK says what it is turned into.
# They are also the two tabs that are not always there — 비교 appears only for a
# paper some comparison holds and 발표 only for one some presentation retells, and a tab
# that is empty for most of the corpus is furniture.
#
# 발표 sits last because it is the surface a reader reaches after deciding the
# paper is worth carrying into a room, which is the decision the first two make.
TABS = (("glance", "요약", "BRIEF"), ("full", "상세", "FULL"),
        ("cmp", "비교", "COMPARED"), ("presentation", "발표", "TALK"))
CMP_TAB = "cmp"
PRESENTATION_TAB = "presentation"


def paper_page(paper: Paper, katex, decisions: dict,
               problems: list[str] | None = None,
               neighbours: list[Paper] | None = None,
               comparisons: list | None = None,
               papers_by_id: dict | None = None,
               citers: list[Paper] | None = None,
               presentation=None) -> str:
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
{_tabstrip(len(comps), presentation is not None)}
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
{_presentation_panel(presentation)}
{c.mark_fab()}
{c.memo_panel(paper.stem, paper.title, f"{BLOB}/analysis/{paper.stem}.md", DISCUSSIONS_NEW)}
"""
    return c.page(
        title=f"{paper.title} · PROBE",
        here="papers",
        description=paper.preview,
        body=body,
        depth=2,
        scripts=(["paper.js", "memo.js", "shelf.js"]
                 + (["presentation.js"] if presentation else [])),
        # The presentation's stylesheet rides only the pages that carry one: a slide is
        # a frame with its own type scale, and no other surface uses a rule of it.
        extra_head=(
            f'<link rel="stylesheet" href="{c.asset("../../assets/presentation.css")}">'
            if presentation else ""),
    )


def _acts(paper: Paper) -> str:
    """즐겨찾기 and 읽음, for this paper, in this browser.

    Both are server-rendered in their empty state and corrected by `shelf.js`
    on load — the build cannot know either one. 읽음 is the reader's claim and
    only ever theirs: neither opening a page nor scrolling to the end of it is
    evidence that it was read, so nothing marks it on their behalf. The button
    says which way it goes rather than naming a state beside itself — with two
    states, 읽음 해제 already says the paper is read.

    They ride the breadcrumb line, at the top of the header: 즐겨찾기 is what a
    reader reaches for *before* the read, and anywhere further down it lands
    below the fold on a phone.
    """
    return f"""<div class="paper-acts" data-paper-acts
     data-paper-id="{c.esc(paper.stem)}" data-paper-title="{c.esc(paper.title)}">
  <button type="button" class="act-btn" data-star="{c.esc(paper.stem)}"
          data-star-title="{c.esc(paper.title)}" aria-pressed="false">
    {c.icon("star", 13)}<span data-star-text>즐겨찾기</span>
  </button>
  <button type="button" class="act-btn" data-read-toggle aria-pressed="false"
          aria-live="polite">읽음으로 표시</button>
</div>"""


def _tabstrip(cmp_n: int = 0, has_presentation: bool = False) -> str:
    """The tabs. Server-rendered and `hidden`-toggled, so the page is readable
    with JavaScript off — the first panel stays open and the rest are reachable
    by their anchors.

    비교 and 발표 are printed only when there is something behind them, and 비교
    carries its count: the number is the whole reason to look, and a tab that
    made the reader click to find out it says zero would have spent their click
    to tell them nothing. 발표 carries none — a paper has one presentation or none, and
    the tab's own presence already says which.
    """
    buttons = []
    for i, (key, label, en) in enumerate(TABS):
        if key == CMP_TAB and not cmp_n:
            continue
        if key == PRESENTATION_TAB and not has_presentation:
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
    while there is still text above it. Empty when nothing shares a tag or a
    pillar — see `corpus.related`.
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


def _presentation_panel(presentation) -> str:
    """발표 — the paper retold as a talk, one slide at a time.

    The tab is a screen, not a scroll. Every slide is in the document and only
    the one being read is on: a talk is a sequence, and a reader who has to
    scroll past twelve frames to reach the turn is reading the deck as a
    document rather than watching it argue. So the frame holds still, ← and →
    move it, and the deck under it says where in the talk this is — the same
    reading a room gets, without anyone having to start the talk to see it.

    The speaker essay goes with the slide it belongs to rather than under it:
    the slide is what the room looks at and the essay is what the presenter
    says over it, and the two are never on screen at the same moment. 노트 is
    what asks for it — inline under the frame while the tab is being read, and
    the second window once the talk is on a stage, because those are the same
    request answered by whichever surface the presenter is standing on.

    The frame stands off the page rather than sitting on it, and every control
    it has stands on one band above it — the arrows at the left end, 노트 and
    전체 화면 at the right, moving on one side and acting on the other. Beside
    the frame the arrows would take a sixth of a phone's width and a column of
    a laptop's from the one element here that cannot spare either; on the band
    they take a strip that was half empty. They are glyphs there for the same
    reason the stage's three are: a word beside a slide is a word competing
    with the sentence on it.

    `.prs-tools` is a grid item of the presentation at the slide's own area, so
    the band is ruled to the frame and not to the panel — and the stage, which
    takes the presentation over and drops everything that is not a slide, drops
    it without being told. It carries no `hidden`: the band is drawn under
    `data-browsing`, which only `presentation.js` sets, so a browser with no
    script never meets a 전체 화면 button that cannot present. What it keeps is
    every slide with its essay under it, which is the talk read as a document.

    The bar is the stage's alone — 목록, 레이저, the zoom readout and the way
    out, none of which mean anything off the stage. It sits outside
    `.prs-presentation`, because presenting takes that element over, but inside
    `.prs-stage`, which is what goes fullscreen, so the presenter reaches those
    controls without leaving the talk to do it.

    The deck is a grid item too, which is what rules it to the frame's own
    width rather than to the panel's.
    """
    if presentation is None:
        return ""
    n = len(presentation.slides)
    return f"""<div class="panel wide" id="p-presentation" role="tabpanel"
     aria-labelledby="t-presentation" hidden>
  <div class="prs-stage" data-pres-stage>
  <div class="prs-bar" data-pres-bar>
    <button type="button" class="prs-ico" data-pres-list
            aria-pressed="false" aria-label="슬라이드 목록"
            title="슬라이드 목록 (O)">{c.icon("grid", 15)}</button>
    <button type="button" class="prs-ico" data-pres-laser
            aria-pressed="false" aria-label="레이저 포인터"
            title="레이저 포인터 (L)">{c.icon("laser", 15)}</button>
    <span class="prs-zoom" data-pres-zoom>100%</span>
    <span class="prs-sep" aria-hidden="true"></span>
    <button type="button" class="prs-ico" data-pres-exit
            aria-label="발표 끝내기" title="발표 끝내기 (Esc)">{c.icon("close", 15)}</button>
  </div>
  <div class="prs-presentation" data-pres-of="{c.esc(presentation.paper_id)}">
    <div class="prs-tools">
      <span class="prs-move">
        <button type="button" class="prs-arrow" data-pres-step="-1"
                aria-label="이전 슬라이드">{c.icon("prev", 16)}</button>
        <button type="button" class="prs-arrow" data-pres-step="1"
                aria-label="다음 슬라이드">{c.icon("next", 16)}</button>
      </span>
      <button type="button" class="prs-ico" data-pres-notes
              aria-pressed="false" aria-label="노트"
              title="노트">{c.icon("note", 15)}</button>
      <button type="button" class="prs-ico" data-pres-start
              aria-label="전체 화면" title="전체 화면">{c.icon("expand", 15)}</button>
    </div>
    {presentations.render(presentation)}
    {presentations.deck(presentation)}
  </div>
  </div>
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
    """What the paper is, in the order a reader needs it.

    The header carries three different kinds of thing — what the paper *is*
    (tags), where it lives (resource links), and when it happened and how big
    a sit it is (dates, length) — and each is drawn as its own kind, so a
    reader scanning for the arXiv link is not reading a run of identical grey
    capsules. Tags are quiet and take a `#`, the links are one bordered group
    that says it leaves the site, the dates are plain text under everything,
    and the paper's own number is the single filled pill. The two 서재 controls
    ride the first line: a row that wraps puts whatever sits at its end below
    the fold, and these two are reached for before the read.

    Where else on this site the paper is argued about is the 비교 tab's job and
    not a fourth kind here: the tab strip sits directly under this header and
    carries the same count, so a chip would be the same offer twice, a
    centimetre apart.
    """
    facts = f"{_metric_chip(paper)}{_src_group(paper)}"
    tags = c.tag_chips(paper.tags)
    return f"""<header class="paper-head">
  <div class="paper-head-inner">
    <div class="crumb-row">
      <div class="crumb">
        <a href="../../index.html">논문</a> ›
        <a href="../../index.html#p={c.esc(paper.primary)}">{c.esc(paper.primary)}</a> ›
        {c.esc(paper.stem)}
      </div>
      {_acts(paper)}
    </div>
    <h1 class="paper-title">{c.esc(paper.title)}</h1>
    {f'<p class="paper-authors">{c.esc(paper.authors)}</p>' if paper.authors else ""}
    {f'<div class="chip-row head-facts">{facts}</div>' if facts else ""}
    {f'<div class="chip-row head-tags">{tags}</div>' if tags else ""}
    {_metaline(paper)}
  </div>
</header>"""


def _src_group(paper: Paper) -> str:
    """Every link out of the site, as one group.

    A resource link is not a tag — it leaves the site — and the group says so
    once, with a `↗` in its first cell, rather than every link repeating the
    arrow. The group is also what holds when a paper declares all six kinds:
    six loose pills in the middle of the header are a wall, one group that
    wraps inside its own box is not. Empty when a rewrite declares no link,
    which R10 allows and which is itself reproducibility information.
    """
    if not paper.links:
        return ""
    items = "".join(
        f'<a href="{c.esc(url)}" target="_blank" rel="noopener">'
        f"{c.src_mark(kind)}{c.esc(label)}</a>"
        for kind, label, url in paper.links
    )
    return ('<span class="src-group" role="group" aria-label="외부 링크">'
            '<span class="sg-out" aria-hidden="true">↗</span>'
            f"{items}</span>")


def _metaline(paper: Paper) -> str:
    """When it happened and how long it is — the facts a reader checks, not
    the ones they act on.

    Plain monospace text rather than pills: a date is nothing to press, and a
    pill that cannot be pressed spends a reader's attention to say so. The
    separator rides on the item ahead of it so a line that wraps never opens
    with a stranded `·`.
    """
    bits = []
    if paper.published:
        bits.append(f"발행 {paper.published}")
    if paper.date:
        bits.append(f"등재 {paper.date}")
    bits.append(_size(paper))
    items = "".join(f'<span class="mi">{c.esc(b)}</span>' for b in bits)
    return f'<div class="metaline">{items}</div>'


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
    tags = c.tag_chips(comp.tags)
    return f"""<header class="paper-head">
  <div class="paper-head-inner">
    <div class="crumb-row">
      <div class="crumb">
        <a href="../index.html">비교</a> › {c.esc(comp.slug)}
      </div>
    </div>
    <h1 class="paper-title">{c.esc(comp.title)}</h1>
    {f'<div class="chip-row head-facts">{pillars}</div>' if pillars else ""}
    {f'<div class="chip-row head-tags">{tags}</div>' if tags else ""}
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
        f'<span class="cmp-card-p">{"".join(c.esc(x) + " " for x in p.filed)}</span>'
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


def talk_index_page(presentation_map: dict) -> str:
    """발표 — every presentation, and nothing about a paper that is not one.

    The one destination in the nav that is an index and nothing else: a
    presentation is a tab on its paper's page, so every row here links back
    into 논문. It exists because a talk is the surface someone goes looking for
    with a room already booked — "what do we have that can be presented on
    Thursday" is a question the paper list cannot answer, since a paper that
    has a talk looks exactly like one that does not until the page is open.

    Each row says the sentence the talk lands and how long it takes — both the
    presentation's own front matter, so nothing here is invented. Nothing else
    from that front matter earns the space: `venue` dates the paper rather than
    the talk, and `audience` is a sentence about a room this reader is not
    standing in, printed at the width of a line they are scanning.

    Under them the act rail, drawn the way the cover slide draws it: one block
    per run of a beat, weighted by the slides it holds. It is the talk's shape,
    and on this surface it is also the only thing that distinguishes two
    fourteen-minute talks from each other before either is opened.
    """
    ordered = sorted(presentation_map.values(),
                     key=lambda t: (t.front.get("generated", ""), t.paper_id),
                     reverse=True)
    if ordered:
        rows = "".join(_talk_row(t) for t in ordered)
        list_html = f'<div class="talk-list">{rows}</div>'
    else:
        list_html = '<p class="corpus-empty">아직 발표 자료로 만든 논문이 없습니다.</p>'

    head = c.mast(
        eyebrow="Slides and script",
        title="발표, 할 말을 순서대로 적어 둡니다",
        art=c.talk_art(),
    )

    body = f"""{head}

<main class="hub">
  {list_html}
</main>
"""
    return c.page(
        title="발표 · PROBE",
        here="talk",
        body=body,
        depth=1,
        extra_head=f'<link rel="stylesheet" href="{c.asset("../assets/index.css")}">',
    )


def _talk_row(presentation) -> str:
    """One talk, from outside it — the spine, its shape, what it was cut for.

    The spine drops its ` / ` marker here (§1-0): the break is authored for the
    width of a cover slide, and a row is not that width.
    """
    spine = presentations.inline(presentation.spine.replace(" / ", " "))
    runs: list[list] = []
    for sl in presentation.slides:
        if runs and runs[-1][0] == sl.act:
            runs[-1][1] += 1
        else:
            runs.append([sl.act, 1])
    rail = "".join(
        f'<i class="talk-r{presentations.ACT_ORDER[act]}" style="--n:{n}"'
        f' title="{c.esc(presentations.ACTS[act])} · {n}장"></i>'
        for act, n in runs)
    cost = " · ".join(x for x in (
        f"{presentation.minutes}분" if presentation.minutes else "",
        f"{len(presentation.slides)}장") if x)
    return (
        f'<a class="talk-item" href="../p/{c.esc(presentation.paper_id)}'
        f'/index.html#{PRESENTATION_TAB}">'
        f'<span class="talk-h"><span class="talk-t">{c.esc(presentation.title)}</span>'
        f'<span class="talk-id">{c.esc(presentation.paper_id)}</span></span>'
        f'<span class="talk-spine">{spine}</span>'
        f'<span class="talk-rail" aria-hidden="true">{rail}</span>'
        f'<span class="talk-cost">{c.esc(cost)}</span></a>'
    )


def comparison_index_page(comps: list, papers_by_id: dict) -> str:
    """비교 — every comparison, newest first.

    A row carries the question, then the fork: what each paper does about it and
    what they all accept. The tagline is not printed here — it is the same
    thought as prose, and it prints under the H1 on the comparison's own page.
    """
    ordered = sorted(comps, key=lambda x: x.order_key, reverse=True)
    if ordered:
        rows = "".join(
            f'<a class="cmp-item" href="{c.esc(x.slug)}/index.html">'
            f'<span class="cmp-item-h">'
            f'<span class="cmp-item-t">{c.esc(x.title)}</span>'
            f'<span class="cmp-item-when">{c.esc(x.date)}</span></span>'
            f"{_fork(x, papers_by_id)}</a>"
            for x in ordered
        )
        list_html = f'<div class="cmp-list">{rows}</div>'
    else:
        list_html = '<p class="corpus-empty">아직 비교한 글이 없습니다.</p>'

    head = c.mast(
        eyebrow="Side by side",
        title="비교, 갈리는 자리만 봅니다",
        art=c.cmp_art(),
    )

    body = f"""{head}

<main class="hub">
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
