"""Page assemblers."""

from __future__ import annotations

import json
from collections import Counter

from . import components as c
from . import corpus, glance as glance_mod
from .corpus import PILLAR_NAMES, PILLAR_ORDER, UNCLASSIFIED, Paper
from .render import DocRenderer

REPO = "jonghochoi/probe"
# Pages serves a project site under /<repo>/. Only 404.html uses this; every
# other page is depth-relative and needs no knowledge of where it is hosted.
SITE_BASE = f"/{REPO.split('/')[1]}/"
BLOB = f"https://github.com/{REPO}/blob/main"
DISCUSSIONS_NEW = f"https://github.com/{REPO}/discussions/new?category=paper-notes"

# How many tag facets the filter bar offers. The corpus has ~90 distinct tags
# and a long tail of one-offs; past this point the chips cost more scanning
# than they save. Search covers everything the chips leave out.
TAG_FACETS = 12

# How many rewrites one page of the list holds, and which of them the bar
# offers. `0` is 전체 — the whole list on one page, which is what a browser with
# no script gets and what the reader can always come back to.
#
# The default is a page rather than the whole corpus: the list is the one part
# of this page that grows without limit, and a reader arriving at it should
# meet a screen of papers, not a year of them. Ten is a screen and a half with
# the lead block above it.
PAGE_SIZES = (5, 10, 20, 0)
PAGE_DEFAULT = 10

def _shelf_facets(cls: str) -> str:
    """New / Starred / Unread, in whichever of its two homes.

    Server-rendered with a zero count and no pressed state, because which
    papers are starred, read or new is the reader's and the build cannot know
    any of it. New ships `hidden` and stays hidden until there is something new
    to point at — a zero that never moves is furniture.
    """
    flags = (("fresh", "New"), ("star", "Starred"), ("unread", "Unread"))
    return "".join(
        f'<button type="button" class="{c.esc(cls)}" data-facet-flag="{key}" '
        f'aria-pressed="false"{" hidden" if key == "fresh" else ""}>'
        f'<span class="sw {key}" aria-hidden="true"></span><b>{label}</b>'
        f'<span class="rn" data-flag-count="{key}">0</span></button>'
        for key, label in flags
    )


def _page_sizes() -> str:
    """5편 · 10편 · 20편 · 전체 — how much of the list one page holds.

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


def landing_page(papers: list[Paper], katex=None, search_api: str = "") -> str:
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

    How large the corpus is and how fresh it is are stated once, in the filter
    bar: the count there is the live one — it answers 몇 편 after a filter as
    well as before — so a second, fixed count in the masthead would be the same
    number twice on one screen, and only one of them would ever move. The
    masthead carries the same pair for the reader whose page is unscripted and
    who therefore has no filter bar; `index.css` hides it once a script runs.
    """
    ordered = sorted(papers, key=lambda p: p.order_key, reverse=True)
    tag_counts = Counter(t for p in ordered for t in p.tags)
    facets = [t for t, _ in tag_counts.most_common(TAG_FACETS)]

    # Taglines and the lead summary are authored markdown — emphasis is what
    # makes a summary scannable, and a summary that opens with math is common
    # enough that escaping it would publish backticks. `decisions` is left
    # empty on purpose: a `D#` tooltip needs `paper.js`, which this page does
    # not load.
    renderer = DocRenderer(katex) if katex is not None else None

    # Counted over *every* declared pillar, not just the primary one: the filter
    # keeps a paper that touches the pillar anywhere, so a count of primaries
    # would promise fewer results than the click delivers. The pillar
    # separators in the list still count primaries — a different question,
    # asked in place.
    touches = Counter(p for paper in ordered for p in (paper.pillars or [UNCLASSIFIED]))
    primaries = Counter(p.primary for p in ordered)

    # The reader's own three filters answer a question the corpus cannot: not
    # "which papers are about X" but "which ones are mine", "which ones are
    # left" and "which ones are new here". Their counts are the only numbers on
    # this page the build does not know — `filter.js` fills them from the
    # shelf, and the group hides itself when nothing is scripted.
    #
    # They are the only English on either surface: a facet is a control, not a
    # sentence, and `Starred` names the ★ beside it in the width `아직 안 읽음`
    # needs two lines for. Everything that speaks in sentences stays Korean —
    # the group heading, 내 서재's tabs, the paper header.
    #
    # The same three are printed twice, once for the rail and once for the
    # filter bar, because the rail leaves at 900px and these three would leave
    # with it — and unlike the pillars and tags below them, nothing else on a
    # phone can reach what they select. Exactly one copy is ever on screen
    # (`index.css`); `filter.js` binds every copy it finds, so the pair never
    # disagrees.
    rail_mine = _shelf_facets("rail-item mine")
    bar_mine = _shelf_facets("barflag")
    rail_pillars = "".join(
        f'<button type="button" class="rail-item pillar" data-p="{c.esc(k)}" '
        f'data-facet-pillar="{c.esc(k)}" aria-pressed="false">'
        f'<span class="sw"></span><b>{c.esc(k)}</b>'
        f'<span class="rn">{touches[k]}</span></button>'
        for k in PILLAR_ORDER if touches.get(k)
    )
    rail_tags = "".join(
        f'<button type="button" class="rail-item" data-facet-tag="{c.esc(t)}" '
        f'aria-pressed="false"><b>{c.esc(t)}</b>'
        f'<span class="rn">{tag_counts[t]}</span></button>'
        for t in facets
    )

    # One separator per pillar, parked in the list and shown only by the
    # pillar sort. Rendering them up front keeps the sort a reordering of
    # existing nodes — the script never builds markup.
    seps = "".join(
        f'<div class="rsep" data-sep="{c.esc(k)}" hidden>'
        f'<span class="chip pillar" data-p="{c.esc(k)}">{c.esc(k)}</span>'
        f"<h2>{c.esc(PILLAR_NAMES.get(k, '축 미지정'))}</h2>"
        f'<span class="rsep-n" data-sep-count>{primaries[k]}</span></div>'
        for k in PILLAR_ORDER if primaries.get(k)
    )
    rows = "".join(
        _row(p, renderer, lead=(i == 0)) for i, p in enumerate(ordered)
    )

    body = f"""<header class="mast brief">
  <div class="mast-inner">
    <div class="mast-text">
      <div class="mast-line">
        <span class="mast-brand">{c.mark(30)}</span>
        <h1>Dexterous Manipulation, 다시 쓴 판</h1>
        <p class="mast-count">{len(ordered)}편{f" · 최근 {c.esc(ordered[0].date)}" if ordered else ""}</p>
      </div>
      <p class="mast-sub">
        원문을 열지 않고도 메커니즘까지 이해되도록,<br class="mast-br">
        논문을 한 편씩 새로 씁니다.
      </p>
    </div>
    {c.mast_art()}
  </div>
</header>

<div class="filters" data-filters>
  <div class="filters-inner">
    <label class="search">
      <span aria-hidden="true">🔍</span>
      <input type="search" data-q autocomplete="off" spellcheck="false"
             placeholder="제목 · 본문 · 용어 · 태그 · 저자 · arXiv id 로 검색"
             aria-label="논문 검색">
    </label>
    <div class="sort" role="group" aria-label="정렬">
      <button type="button" data-sort="recent" aria-pressed="true">최신순</button>
      <button type="button" data-sort="pillar" aria-pressed="false">연구 축별</button>
      <button type="button" data-sort="title" aria-pressed="false">제목순</button>
    </div>
    <div class="sort psize" role="group" aria-label="한 쪽에 몇 편">{_page_sizes()}</div>
    <div class="barflags" role="group" aria-label="내 서재">{bar_mine}</div>
    <span class="filter-spacer"></span>
    <span class="status" data-result-count>{len(ordered)}편</span>
    {f'<span class="status when" data-corpus-when>· 최근 {c.esc(ordered[0].date)}</span>' if ordered else ""}
    <button type="button" class="linkish" data-reset hidden>필터 초기화</button>
  </div>
</div>

<div class="deck">
  <aside class="rail" data-rail>
    {rail_mine}
    <p class="rail-h">연구 축</p>
    {rail_pillars}
    <p class="rail-h">태그</p>
    {rail_tags}
  </aside>
  <main class="corpus" data-corpus>
    {_first_run() if not ordered else ""}
    {_resume()}
    {_lead_block(ordered[0], renderer) if ordered else ""}
    <div class="listhead" data-listhead{" hidden" if len(ordered) < 2 else ""}>
      <span class="lh-star"></span><span>재작성</span><span>arXiv</span><span>논문 · 한 줄</span><span>연구 축</span><span>분량</span>
    </div>
    <div class="sem" data-sem hidden></div>
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
        description=f"Dexterous manipulation 논문 {len(ordered)}편을 원문에서 다시 쓴 한글 판",
        body=body,
        depth=0,
        # `semantic.js` ships only when the build was handed an endpoint, so a
        # default build makes no request and needs no network to be correct.
        scripts=["shelf.js", "filter.js"] + (["semantic.js"] if search_api else []),
        extra_head='<link rel="stylesheet" href="assets/index.css">',
        body_attrs=f'data-search-api="{c.esc(search_api)}"' if search_api else "",
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
        '내 서재 →</a></div>'
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
        f'data-pillars="{c.esc(" ".join(paper.pillars) or UNCLASSIFIED)}" '
        f'data-primary="{c.esc(paper.primary)}" '
        f'data-tags="{c.esc(" ".join(paper.tags))}" '
        f'data-order="{c.esc(paper.order_token)}" '
        f'data-title="{c.esc(paper.title.lower())}" '
        f'data-key="{c.esc(paper.search_key)}" '
        f'data-hay="{c.esc(paper.search_hay)}"'
    )


def _star(paper: Paper, cls: str = "rowstar") -> str:
    """The star, wherever a paper is named.

    Server-rendered empty and filled in by `shelf.js`: which papers are starred
    is the reader's, not the corpus's, and the build has no way to know it. The
    title rides along because the shelf keeps a copy of it — a starred paper
    that later leaves the corpus still lists under a name in 내 서재 rather than
    as a bare id. Nothing without JavaScript can toggle it, so the button
    removes itself there (`index.css`) instead of sitting inert.
    """
    return (
        f'<button type="button" class="{cls}" data-star="{c.esc(paper.stem)}" '
        f'data-star-title="{c.esc(paper.title)}" aria-pressed="false" '
        f'aria-label="즐겨찾기"><span data-star-glyph aria-hidden="true">☆</span></button>'
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


def _metric_chip(paper: Paper) -> str:
    return (
        f'<span class="metric">{c.esc(paper.metric)}</span>' if paper.metric else ""
    )


def _lead_block(paper: Paper, renderer=None) -> str:
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
    {"".join(c.chip(p, "pillar", data={"p": p}) for p in paper.pillars)}
    {_metric_chip(paper)}
    {tag_buttons}
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
    # Two chips, not every pillar: a third one wraps the column onto a second
    # line and makes the row taller than its own title. `data-pillars` still
    # carries all of them, so filtering is unaffected.
    pillars = "".join(
        c.chip(p, "pillar", data={"p": p}) for p in paper.pillars[:2]
    )
    return f"""<article class="row" data-card{' data-lead-dup hidden' if lead else ''}
  data-read-of="{c.esc(paper.stem)}" {_facets(paper)}>
  {_star(paper)}
  <span class="row-when">{c.esc(paper.date[5:] or paper.date)}</span>
  <span class="row-id">{c.esc(paper.stem)}</span>
  <a class="row-main" href="p/{c.esc(paper.stem)}/index.html">
    <span class="row-title">{c.esc(paper.title)}{_metric_chip(paper)}</span>
    <span class="row-tagline">{_md(renderer, paper.tagline)}</span>
  </a>
  <span class="row-pillars">{pillars}</span>
  <span class="row-size">{c.esc(_size(paper, short=True))}</span>
</article>"""


# The four lists 내 서재 holds, in the order a reader meets them: what they
# picked out, what they got through, where they stopped, what they wrote down.
SHELF_TABS = (
    ("stars", "즐겨찾기"),
    ("reads", "읽은 논문"),
    ("marks", "책갈피"),
    ("memos", "메모"),
)


def shelf_page(papers: list[Paper]) -> str:
    """내 서재 — everything this browser has kept about the corpus.

    Rendered empty and filled from `localStorage`: stars, 읽음 marks and memos
    never reach the build, so there is nothing here to server-render but the
    frame. What the build *does* ship is `[data-corpus-index]` — id, title,
    tagline, pillars for every rewrite — which is what turns a kept id back
    into a row with a link. A kept id missing from it is a paper that has left
    the corpus, and 내 서재 says so rather than dropping it.

    The page is also the export surface, and the only one: a shelf that lives
    in one browser profile reaches a second machine as a file or not at all.
    """
    ordered = sorted(papers, key=lambda p: p.order_key, reverse=True)
    # `</` cannot appear inside a `<script>` body — the parser ends the element
    # there, whatever the type says.
    index = json.dumps(
        [{"id": p.stem, "title": p.title, "tagline": p.tagline,
          "pillars": p.pillars, "date": p.date} for p in ordered],
        ensure_ascii=False, separators=(",", ":"),
    ).replace("</", "<\\/")

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

    body = f"""<header class="mast slim">
  <div class="mast-inner">
    <h1>내 서재</h1>
    <p class="mast-sub">
      즐겨찾기, 읽은 논문, 책갈피, 그리고 메모. 넷 다 <strong>이 브라우저에만</strong>
      저장되어 다른 기기·다른 브라우저에서는 보이지 않고, 사이트 데이터를 지우면
      사라집니다. 옮기거나 남길 것은 내보내세요.
    </p>
  </div>
</header>

<main class="hub" data-hub>
  <div class="hub-tabs" role="tablist" aria-label="내 서재 보기">{tabs}</div>
  <div class="hub-actions">
    <button type="button" class="primary" data-hub-action="export-json">JSON 내보내기</button>
    <button type="button" data-hub-action="export-md">마크다운 내보내기</button>
    <label class="filebtn">가져오기<input type="file" accept="application/json" data-hub-import hidden></label>
    <span class="filter-spacer"></span>
    <span class="hub-status" data-hub-status aria-live="polite"></span>
  </div>
  {panels}
  <noscript><p class="corpus-empty">서재는 브라우저에 저장되므로 JavaScript 가 필요합니다.</p></noscript>
</main>
<script type="application/json" data-corpus-index>{index}</script>
"""
    return c.page(
        title="내 서재 · PROBE",
        body=body,
        depth=1,
        scripts=["memo.js", "shelf.js", "hub.js"],
        extra_head='<link rel="stylesheet" href="../assets/index.css">',
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
        extra_head=f'<link rel="stylesheet" href="{SITE_BASE}assets/index.css">',
    )


# The two surfaces, in the order a reader meets them — the one-screen 요약
# first, because a reader arrives at a paper page not yet knowing whether the
# paper is worth the long read, and that is the question the short surface
# answers. `en` is printed beside the Korean label because the tab strip is
# also how a contributor finds the rule set: 요약 is §4 and 상세 is §1–§3.
TABS = (("glance", "요약", "BRIEF"), ("full", "상세", "FULL"))


def paper_page(paper: Paper, katex, decisions: dict,
               problems: list[str] | None = None,
               neighbours: list[Paper] | None = None) -> str:
    """One paper's rewrite — two tabs cut from one source file.

    The brief and the body are two readings of the same paper for two
    different sits, so they are two panels of one page rather than two pages:
    the header, the resource links and the memo panel are the same paper's,
    and a reader switching surface has not left the paper.
    """
    renderer = DocRenderer(katex, decisions=decisions)
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

    body = f"""{_header(paper)}
{_tabstrip()}
<div class="panel wide" id="p-glance" role="tabpanel" aria-labelledby="t-glance">
  {glance_html or _missing("요약")}
</div>
<div class="panel" id="p-full" role="tabpanel" aria-labelledby="t-full" hidden>
  <div class="shell">
    <aside class="toc">{_toc(renderer.toc)}</aside>
    <main class="article">
      <section class="view">{rendered}</section>
      {_related(neighbours or [])}
    </main>
  </div>
</div>
{c.mark_fab()}
{c.memo_panel(paper.stem, paper.title, f"{BLOB}/analysis/{paper.stem}.md", DISCUSSIONS_NEW)}
"""
    return c.page(
        title=f"{paper.title} · PROBE",
        description=paper.preview,
        body=body,
        depth=2,
        scripts=["paper.js", "memo.js", "shelf.js"],
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
    <span data-star-glyph aria-hidden="true">☆</span><span data-star-text>즐겨찾기</span>
  </button>
  <button type="button" class="act-btn" data-read-toggle aria-pressed="false"
          aria-live="polite">읽음으로 표시</button>
</div>"""


def _tabstrip() -> str:
    """The two surfaces. Server-rendered and `hidden`-toggled, so the page is
    readable with JavaScript off — the first panel stays open and the second is
    reachable by its anchor."""
    buttons = "".join(
        f'<button type="button" class="tab" role="tab" id="t-{key}" '
        f'aria-controls="p-{key}" aria-selected="{"true" if i == 0 else "false"}" '
        f'data-tab="{key}">{c.esc(label)} <span class="en">{c.esc(en)}</span></button>'
        for i, (key, label, en) in enumerate(TABS)
    )
    return (f'<div class="tabs-wrap"><div class="tabs" role="tablist" '
            f'aria-label="논문 보기 방식">{buttons}</div></div>')


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
        f'  <span class="rel-p">{"".join(c.esc(x) + " " for x in p.pillars[:2])}</span>\n'
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
