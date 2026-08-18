"""Page assemblers."""

from __future__ import annotations

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

def landing_page(papers: list[Paper], katex=None) -> str:
    """The corpus index — a briefing: newest rewrite in full, the rest as rows.

    The page answers "what should I read" before "what is here". The most
    recent rewrite is printed as a lead block with its thesis, summary and
    numbers; everything else is one scannable row per paper, sorted newest
    first. Facets live in a left rail rather than a chip bank above the list,
    which is what lets the rows start in the first screen.

    Every row is server-rendered with its facets on `data-` attributes rather
    than hydrated from an inline JSON blob. That keeps the page fully readable
    with JavaScript off (the filter bar and the rail hide themselves, the rows
    stay, newest first), and the filter script only ever reorders and toggles
    `hidden` on nodes that already exist.
    """
    ordered = sorted(papers, key=lambda p: p.date, reverse=True)
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
        f"<h2>{c.esc(PILLAR_NAMES.get(k, '필러 미지정'))}</h2>"
        f'<span class="rsep-n" data-sep-count>{primaries[k]}</span></div>'
        for k in PILLAR_ORDER if primaries.get(k)
    )
    rows = "".join(
        _row(p, renderer, lead=(i == 0)) for i, p in enumerate(ordered)
    )

    body = f"""<header class="mast">
  <div class="mast-inner">
    <div class="mast-line">
      <span class="mast-brand">{c.mark(30)}</span>
      <h1>Dexterous Manipulation, 다시 쓴 판</h1>
      <span class="mast-rule"></span>
      <p class="mast-count">{len(ordered)}편{f" · 최근 {c.esc(ordered[0].date)}" if ordered else ""}</p>
    </div>
    <p class="mast-sub">
      원문을 열지 않고도 메커니즘까지 이해되도록, 논문을 한 편씩 새로 씁니다.
    </p>
  </div>
</header>

<div class="filters" data-filters>
  <div class="filters-inner">
    <label class="search">
      <span aria-hidden="true">🔍</span>
      <input type="search" data-q autocomplete="off" spellcheck="false"
             placeholder="제목 · 요약 · 태그 · 저자 · arXiv id 로 검색"
             aria-label="논문 검색">
    </label>
    <div class="sort" role="group" aria-label="정렬">
      <button type="button" data-sort="recent" aria-pressed="true">최신순</button>
      <button type="button" data-sort="pillar" aria-pressed="false">Pillar 별</button>
      <button type="button" data-sort="title" aria-pressed="false">제목순</button>
    </div>
    <span class="filter-spacer"></span>
    <span class="status" data-result-count>{len(ordered)}편</span>
    <button type="button" class="linkish" data-reset hidden>필터 초기화</button>
  </div>
</div>

<div class="deck">
  <aside class="rail" data-rail>
    <p class="rail-h">Pillar</p>
    {rail_pillars}
    <p class="rail-h">태그</p>
    {rail_tags}
  </aside>
  <main class="corpus" data-corpus>
    {_first_run() if not ordered else ""}
    {_lead_block(ordered[0], renderer) if ordered else ""}
    <div class="listhead" data-listhead{" hidden" if len(ordered) < 2 else ""}>
      <span>재작성</span><span>arXiv</span><span>논문 · 한 줄</span><span>Pillar</span><span>분량</span>
    </div>
    <div class="rows" data-rows>{seps}{rows}</div>
    <p class="corpus-empty" data-empty hidden>
      조건에 맞는 논문이 없습니다. <button type="button" class="linkish" data-reset>필터를 지워</button> 보세요.
    </p>
  </main>
</div>
"""
    return c.page(
        title="PROBE · 논문 분석",
        description=f"Dexterous manipulation 논문 {len(ordered)}편을 원문에서 다시 쓴 한글 판",
        body=body,
        depth=0,
        scripts=["filter.js"],
        extra_head='<link rel="stylesheet" href="assets/index.css">',
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
    """The `data-` attributes the filter script reads off a row."""
    hay = " ".join(
        [paper.stem, paper.title, paper.tagline, paper.preview, paper.authors,
         *paper.tags]
    ).lower()
    return (
        f'data-id="{c.esc(paper.stem)}" '
        f'data-pillars="{c.esc(" ".join(paper.pillars) or UNCLASSIFIED)}" '
        f'data-primary="{c.esc(paper.primary)}" '
        f'data-tags="{c.esc(" ".join(paper.tags))}" '
        f'data-date="{c.esc(paper.date)}" '
        f'data-title="{c.esc(paper.title.lower())}" '
        f'data-hay="{c.esc(hay)}"'
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
    you came for. The one written most recently is the one a returning reader
    has not seen, so it gets the space — and with it the thesis line, which is
    ours and appears nowhere else on this page.
    """
    tag_buttons = "".join(
        f'<button type="button" class="chip tag" data-tag-jump="{c.esc(t)}">{c.esc(t)}</button>'
        for t in paper.tags[:3]
    )
    links = "".join(
        c.chip(f"{emoji} {label}", "src-link", href=url)
        for emoji, label, url in paper.links
    )
    return f"""<article class="lead" data-lead>
  <div class="lead-top">
    <span class="lead-flag">가장 최근</span>
    <span class="lead-when">{c.esc(paper.date)} · arXiv {c.esc(paper.stem)}</span>
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
  {_facets(paper)}>
  <span class="row-when">{c.esc(paper.date[5:] or paper.date)}</span>
  <span class="row-id">{c.esc(paper.stem)}</span>
  <a class="row-main" href="p/{c.esc(paper.stem)}/index.html">
    <span class="row-title">{c.esc(paper.title)}{_metric_chip(paper)}</span>
    <span class="row-tagline">{_md(renderer, paper.tagline)}</span>
  </a>
  <span class="row-pillars">{pillars}</span>
  <span class="row-size">{c.esc(_size(paper, short=True))}</span>
</article>"""


def memos_page() -> str:
    """The memo hub — rendered empty and filled from localStorage.

    Nothing here can be server-rendered: the memos live in the reader's browser
    and never reach the build. The page is the export/import surface for them.
    """
    body = """<header class="mast slim">
  <div class="mast-inner">
    <h1>메모</h1>
    <p class="mast-sub">
      논문을 읽으며 남긴 메모입니다. <strong>이 브라우저에만</strong> 저장되어 있어
      다른 기기에서는 보이지 않고, 사이트 데이터를 지우면 사라집니다.
      남길 메모는 내보내거나 Discussions 로 발행하세요.
    </p>
  </div>
</header>

<main class="hub">
  <div class="hub-actions">
    <button type="button" class="primary" data-hub="export-json">JSON 내보내기</button>
    <button type="button" data-hub="export-md">마크다운 내보내기</button>
    <label class="filebtn">가져오기<input type="file" accept="application/json" data-hub-import hidden></label>
    <span class="filter-spacer"></span>
    <span class="hub-status" data-hub-status aria-live="polite"></span>
  </div>
  <div data-hub-list></div>
  <p class="corpus-empty" data-hub-empty hidden>
    아직 메모가 없습니다. 논문 페이지 오른쪽 아래의 📝 버튼으로 남길 수 있습니다.
  </p>
  <noscript><p class="corpus-empty">메모는 브라우저에 저장되므로 JavaScript 가 필요합니다.</p></noscript>
</main>
"""
    return c.page(
        title="메모 · PROBE",
        body=body,
        depth=1,
        scripts=["memo.js", "hub.js"],
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


# The two surfaces, in the order a reader meets them. `en` is printed beside
# the Korean label because the tab strip is also how a contributor finds the
# rule set: 상세 is §1–§3 and 한눈에 is §4.
TABS = (("full", "상세", "FULL"), ("glance", "한눈에", "GLANCE"))


def paper_page(paper: Paper, katex, decisions: dict,
               problems: list[str] | None = None,
               neighbours: list[Paper] | None = None) -> str:
    """One paper's rewrite — two tabs cut from one source file.

    The body and the glance are two readings of the same paper for two
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
<div class="panel" id="p-full" role="tabpanel" aria-labelledby="t-full">
  <div class="shell">
    <aside class="toc">{_toc(renderer.toc)}</aside>
    <main class="article">
      <section class="view">{rendered}</section>
      {_related(neighbours or [])}
    </main>
  </div>
</div>
<div class="panel wide" id="p-glance" role="tabpanel" aria-labelledby="t-glance" hidden>
  {glance_html or _missing("한눈에")}
</div>
{c.memo_panel(paper.stem, paper.title, f"{BLOB}/analysis/{paper.stem}.md", DISCUSSIONS_NEW)}
"""
    return c.page(
        title=f"{paper.title} · PROBE",
        description=paper.preview,
        body=body,
        depth=2,
        scripts=["paper.js", "memo.js"],
    )


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
        link = (
            f'<a href="#{c.esc(entry["id"])}">'
            f'<span class="toc-k">{c.esc(entry["label"])}</span>'
            + (f'<span class="toc-e">{c.esc(entry["en"])}</span>' if entry.get("en") else "")
            + "</a>"
        )
        if not open_group:
            groups.append('<div class="toc-grp">')
            open_group = True
        groups.append(link)
    if open_group:
        groups.append("</div>")
    return '<div class="toc-title">목차</div>' + "".join(groups)


def _header(paper: Paper) -> str:
    chips = "".join(
        c.chip(f"{emoji} {label}", "src-link", href=url)
        for emoji, label, url in paper.links
    )
    return f"""<header class="paper-head">
  <div class="paper-head-inner">
    <div class="crumb">
      <a href="../../index.html">논문</a> ›
      <a href="../../index.html#p={c.esc(paper.primary)}">{c.esc(paper.primary)}</a> ›
      {c.esc(paper.stem)}
    </div>
    <h1 class="paper-title">{c.esc(paper.title)}</h1>
    {f'<p class="paper-authors">{c.esc(paper.authors)}</p>' if paper.authors else ""}
    <div class="chip-row">
      {c.tag_chips(paper.tags)}
    </div>
    <div class="chip-row">
      {chips}
      {c.chip(f'발행 {paper.published}') if paper.published else ""}
      {c.chip(f'작성 {paper.date}') if paper.date else ""}
      {_metric_chip(paper)}
      <span class="head-size">{c.esc(_size(paper))}</span>
    </div>
  </div>
</header>"""
