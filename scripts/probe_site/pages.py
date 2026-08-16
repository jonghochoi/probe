"""Page assemblers."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from . import components as c
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

def landing_page(papers: list[Paper]) -> str:
    """The corpus index — pillar-grouped card grid over a sticky filter bar.

    Every card is server-rendered with its facets on `data-` attributes rather
    than hydrated from an inline JSON blob. That keeps the page fully readable
    with JavaScript off (the filter bar hides itself, the cards stay), and the
    filter script only ever toggles `hidden` on nodes that already exist.
    """
    ordered = sorted(papers, key=lambda p: p.date, reverse=True)
    tag_counts = Counter(t for p in ordered for t in p.tags)
    facets = [t for t, _ in tag_counts.most_common(TAG_FACETS)]

    by_pillar: dict[str, list[Paper]] = {}
    for paper in ordered:
        by_pillar.setdefault(paper.primary, []).append(paper)

    groups = []
    for key in PILLAR_ORDER:
        bucket = by_pillar.get(key)
        if not bucket:
            continue
        name = PILLAR_NAMES.get(key, "필러 미지정")
        cards = "".join(_card(p) for p in bucket)
        groups.append(
            f'<section class="pgroup" data-pgroup="{c.esc(key)}">\n'
            f'  <header class="pgroup-head">\n'
            f'    <span class="chip pillar" data-p="{c.esc(key)}">{c.esc(key)}</span>\n'
            f"    <h2>{c.esc(name)}</h2>\n"
            f'    <span class="pgroup-count" data-group-count>{len(bucket)}</span>\n'
            f"  </header>\n"
            f'  <div class="grid">{cards}</div>\n'
            f"</section>"
        )

    # Counted over *every* declared pillar, not just the primary one: the filter
    # keeps a paper that touches the pillar anywhere, so a count of primaries
    # would promise fewer results than the click delivers. The group headings
    # below still count primaries — a different question, asked in place.
    touches = Counter(p for paper in ordered for p in (paper.pillars or [UNCLASSIFIED]))
    pillar_chips = "".join(
        f'<button type="button" class="facet-chip pillar" data-p="{c.esc(k)}" '
        f'data-facet-pillar="{c.esc(k)}" aria-pressed="false">'
        f"{c.esc(k)}<span class=\"n\">{touches[k]}</span></button>"
        for k in PILLAR_ORDER if touches.get(k)
    )
    tag_chips = "".join(
        f'<button type="button" class="facet-chip" data-facet-tag="{c.esc(t)}" '
        f'aria-pressed="false">{c.esc(t)}<span class="n">{tag_counts[t]}</span></button>'
        for t in facets
    )

    body = f"""<header class="hero">
  <div class="hero-inner">
    <p class="hero-eyebrow">hand-centric dexterous manipulation</p>
    <h1>읽은 논문 {len(ordered)}편</h1>
    <p class="hero-sub">
      논문 원문에서 다시 쓴 한글 판입니다. 원문을 열지 않고도 메커니즘까지 이해되도록,
      요청한 논문을 한 편씩 새로 씁니다.
    </p>
    <dl class="hero-stats">
      <div><dt>논문</dt><dd>{len(ordered)}</dd></div>
      <div><dt>Pillar</dt><dd>{len([k for k in PILLAR_ORDER if by_pillar.get(k)])}</dd></div>
      <div><dt>태그</dt><dd>{len(tag_counts)}</dd></div>
    </dl>
  </div>
</header>

<div class="filters" data-filters>
  <div class="filters-inner">
    <div class="filter-row">
      <label class="search">
        <span aria-hidden="true">🔍</span>
        <input type="search" data-q autocomplete="off" spellcheck="false"
               placeholder="제목 · 요약 · 태그 · 저자 · arXiv id 로 검색"
               aria-label="논문 검색">
      </label>
      <span class="filter-spacer"></span>
      <div class="sort" role="group" aria-label="정렬">
        <button type="button" data-sort="pillar" aria-pressed="true">Pillar 별</button>
        <button type="button" data-sort="recent" aria-pressed="false">최신순</button>
        <button type="button" data-sort="title" aria-pressed="false">제목순</button>
      </div>
    </div>
    <div class="filter-row facets" data-facet-group="pillar">{pillar_chips}</div>
    <div class="filter-row facets" data-facet-group="tag">{tag_chips}</div>
    <div class="filter-row status">
      <span data-result-count>{len(ordered)}편</span>
      <button type="button" class="linkish" data-reset hidden>필터 초기화</button>
    </div>
  </div>
</div>

<main class="corpus" data-corpus>
  {_first_run() if not ordered else ""}
  {"".join(groups)}
  <div class="grid flat" data-flat hidden></div>
  <p class="corpus-empty" data-empty hidden>
    조건에 맞는 논문이 없습니다. <button type="button" class="linkish" data-reset>필터를 지워</button> 보세요.
  </p>
</main>
"""
    return c.page(
        title="PROBE · 논문 분석",
        description=f"손 중심 조작 연구 논문 {len(ordered)}편을 원문에서 다시 쓴 한글 판",
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
        '<code>/readable-paper &lt;arXiv id&gt;</code> 로 첫 편을 추가하면 '
        "여기에 카드가 생깁니다.</p>"
    )


def _card(paper: Paper) -> str:
    tags = paper.tags
    tag_buttons = "".join(
        f'<button type="button" class="chip tag" data-tag-jump="{c.esc(t)}">{c.esc(t)}</button>'
        for t in tags[:3]
    )
    date = paper.date
    hay = " ".join([paper.stem, paper.title, paper.preview, paper.authors, *tags]).lower()

    return f"""<article class="card" data-card
  data-id="{c.esc(paper.stem)}"
  data-pillars="{c.esc(" ".join(paper.pillars) or UNCLASSIFIED)}"
  data-tags="{c.esc(" ".join(tags))}"
  data-date="{c.esc(date)}"
  data-title="{c.esc(paper.title.lower())}"
  data-hay="{c.esc(hay)}">
  <a class="card-body" href="p/{c.esc(paper.stem)}/index.html">
    <div class="card-top">
      {"".join(c.chip(p, "pillar", data={"p": p}) for p in paper.pillars[:2])}
      <span class="card-id">{c.esc(paper.stem)}</span>
    </div>
    <h3 class="card-title">{c.esc(paper.title)}</h3>
    <p class="card-preview">{c.esc(paper.preview)}</p>
  </a>
  <div class="card-foot">
    {tag_buttons}
    <span class="filter-spacer"></span>
    {f'<time datetime="{c.esc(date)}">{c.esc(date)}</time>' if date[:1].isdigit() else ""}
  </div>
</article>"""


def memos_page() -> str:
    """The memo hub — rendered empty and filled from localStorage.

    Nothing here can be server-rendered: the memos live in the reader's browser
    and never reach the build. The page is the export/import surface for them.
    """
    body = """<header class="hero slim">
  <div class="hero-inner">
    <h1>메모</h1>
    <p class="hero-sub">
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


def paper_page(paper: Paper, katex, decisions: dict,
               problems: list[str] | None = None) -> str:
    """One paper's readable rewrite.

    One document per page: the site publishes rewrites and nothing else, so
    there is no tab strip and no second source to reconcile against.
    """
    renderer = DocRenderer(katex, decisions=decisions)
    rendered = renderer.render(paper.body)
    if problems is not None:
        problems.extend(
            f"readable/{paper.stem}.md: {p}" for p in renderer.problems
        )

    body = f"""{_header(paper)}
<div class="shell">
  <aside class="toc" data-toc></aside>
  <main class="article">
    <section class="view">{rendered}</section>
  </main>
</div>
{c.memo_panel(paper.stem, paper.title, f"{BLOB}/readable/{paper.stem}.md", DISCUSSIONS_NEW)}
"""
    return c.page(
        title=f"{paper.title} · PROBE",
        description=paper.preview,
        body=body,
        depth=2,
        scripts=["paper.js", "memo.js"],
    )


def _drop_h1(source: str) -> str:
    lines = source.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("# "):
            return "\n".join(lines[:i] + lines[i + 1:])
    return source


def _drop_meta_section(source: str) -> str:
    """Remove the leading `## 📄 …` meta table.

    Every row of it is already in the page header as a chip, so rendering it
    again pushes the actual content a full screen down. The one row the header
    lacked (`발행일 / 버전`) became a header chip instead.
    """
    lines = source.split("\n")
    start = None
    for i, line in enumerate(lines):
        if line.startswith("## ") and "📄" in line:
            start = i
            continue
        if start is not None and line.startswith("## "):
            return "\n".join(lines[:start] + lines[i:])
    return "\n".join(lines[:start]) if start is not None else source


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
    </div>
  </div>
</header>"""
