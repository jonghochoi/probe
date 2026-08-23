"""HTML components as plain functions returning strings.

No template engine: a handful of page types and ~20 components do not justify
a fifth dependency. Every interpolation goes through `esc()`.
"""

from __future__ import annotations

import html

from . import assets_out

# The mark at 16 px, inlined as a data URI so the zero-third-party rule holds
# and no extra request is made for a tab icon. Two shapes and two tones: the
# hull and the pupil are all that survives at this size, and they are enough —
# a tab full of favicons is scanned for silhouette, not for detail.
FAVICON = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
    "%3Crect width='32' height='32' rx='8' fill='%23D97757'/%3E"
    "%3Ccircle cx='16' cy='5.6' r='2.1' fill='%23fff'/%3E"
    "%3Crect x='5.5' y='9' width='21' height='18' rx='6.4' fill='%23fff'/%3E"
    "%3Ccircle cx='12.2' cy='18' r='2.5' fill='%232a1a12'/%3E"
    "%3Ccircle cx='19.8' cy='18' r='2.5' fill='%232a1a12'/%3E%3C/svg%3E"
)


def asset(url: str) -> str:
    """An asset URL carrying the build's version token.

    Every stylesheet and script goes through here, so nothing this build
    prints can be served against a cached copy of a different build's rules
    — see `assets_out.version()` for why that matters more than a missing
    file would.
    """
    return f"{url}?v={assets_out.version()}"


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def mark(size: int) -> str:
    """The animated PROBE mark — a probe that looks back at the reader.

    One `viewBox` serves every size; the caller picks the pixel box. Geometry
    only: the idle bob, the blink, the mood swap and the beacon's signal are
    keyframes in `site.css`, and `brand.js` steers the pupils after the
    pointer. Two eyes rather than one, because a single eye reads as
    "something moved" while a pair reads as "it is looking at you" — which is
    the whole point of putting a face on a scouting agent. Each eye ships both
    of its faces at once — the round pupil and the `joy` arc it smiles with —
    because a stroke cannot be tweened into a disc, so the mood keyframes
    cross-fade between them and each face holds half the cycle. The two signal
    arcs sit at fixed radii a clear gap apart and light in sequence, the way a
    reception meter fills. Decorative in every slot it appears in — the logo
    and the masthead both name the site in text right next to it — so it stays
    out of the accessibility tree.
    """
    eyes = "".join(
        f'<g class="eye {side}"><g class="lid">'
        f'<circle class="iris" cx="{x}" cy="52" r="11"/>'
        f'<circle class="pupil" cx="{x}" cy="52" r="5"/>'
        f'<path class="joy" d="M{x - 6} 54 a6.5 6.5 0 0 1 12 0"/>'
        "</g></g>"
        for side, x in (("eL", 36), ("eR", 60))
    )
    return (
        f'<svg class="probe-mark" width="{size}" height="{size}" '
        'viewBox="0 0 96 96" aria-hidden="true" focusable="false">'
        '<ellipse class="shadow" cx="48" cy="90" rx="20" ry="4"/>'
        '<g class="rig">'
        '<path class="wave w1" d="M41.04 11.12 A8.5 8.5 0 0 1 54.96 11.12"/>'
        '<path class="wave w2" d="M36.94 8.25 A13.5 13.5 0 0 1 59.06 8.25"/>'
        '<path class="stalk" d="M48 26 V19"/>'
        '<circle class="beacon" cx="48" cy="16" r="5"/>'
        '<rect class="hull" x="17" y="27" width="62" height="54" rx="19"/>'
        f"{eyes}"
        "</g></svg>"
    )


# The masthead diagram's geometry, in its own viewBox units. The four pieces
# are the only numbers that have to agree with anything: each one departs a
# line of the original and lands on the part of the rewrite it becomes, and
# `index.css` moves them between exactly these coordinates.
_ART_PIECES = ((66, 62), (66, 80), (66, 98), (66, 116))
_ART_ACTS = (214, 298, 382, 466)
_ART_ROWS = ((44, 44), (44, 44), (44, 44), (44, 38),
             (44, 44), (44, 44), (36, 44), (44, 30))


def mast_art() -> str:
    """The landing masthead's diagram — the tagline beside it, drawn.

    The sentence it answers is "원문을 열지 않아도 메커니즘까지 남도록 다시
    씁니다", and the drawing carries it in one loop: a scan
    crosses an arXiv original that stays shut (it keeps its 열지 않음 tag the
    whole way) and lifts **four pieces** out of it; the four line up over the
    mark; then two of them cross to the 요약 tab and become its act cards and
    its summary, and — once the tab turns — the last two become the term panel
    and the figure of 상세. Nothing appears in the rewrite that a piece did not
    carry there, which is what makes the picture an argument rather than an
    ornament: the two tabs are visibly one reading of one paper.

    The rack over the mark is what keeps the loop honest at the seam. Pieces
    held in the open say "two still to place" for the whole middle of the
    cycle, and the remaining pair slides back to centre as the first pair
    leaves, so the wait reads as deliberate rather than as a stall.

    `mark()` is nested rather than redrawn, so the face here is the same
    drawing as the one in the nav — same tokens, same blink, same pupils under
    `brand.js`. Geometry only: every beat is a keyframe in `index.css`.

    The tagline states all of this in text immediately to the left, so the
    figure is decorative and stays out of the accessibility tree.
    """
    rows = "".join(
        f'<rect x="18" y="{y}" width="{w1}" height="3" rx="1.5"/>'
        f'<rect x="68" y="{y}" width="{w2}" height="3" rx="1.5"/>'
        for y, (w1, w2) in zip(range(56, 128, 9), _ART_ROWS)
    )
    pieces = "".join(
        f'<circle class="ma-dot ma-d{i + 1}" cx="{x}" cy="{y}" r="3.4"/>'
        for i, (x, y) in enumerate(_ART_PIECES)
    )
    acts = "".join(
        f'<g class="ma-act ma-a{i + 1}">'
        f'<rect class="ma-card" x="{x}" y="64" width="76" height="42" rx="6"/>'
        f'<rect class="ma-act-bar" x="{x}" y="64" width="76" height="3" rx="1.5"/>'
        f'<rect x="{x + 8}" y="78" width="46" height="3" rx="1.5"/>'
        f'<rect x="{x + 8}" y="87" width="56" height="3" rx="1.5"/>'
        f'<rect x="{x + 8}" y="96" width="34" height="3" rx="1.5"/>'
        "</g>"
        for i, x in enumerate(_ART_ACTS)
    )
    return (
        # The box stops just under the rewrite card (its foot is at 160): the
        # masthead's own padding is the margin, and a viewBox taller than the
        # drawing would push the filter bar down with empty space.
        '<svg class="mast-art" viewBox="0 0 560 164" aria-hidden="true" '
        'focusable="false">'
        "<defs>"
        '<linearGradient id="ma-scan" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" class="ma-scan-0"/><stop offset="1" class="ma-scan-1"/>'
        "</linearGradient>"
        '<clipPath id="ma-clip">'
        '<rect x="6" y="26" width="118" height="132" rx="8"/></clipPath>'
        "</defs>"

        # The original — read, never opened.
        '<text class="ma-label" x="6" y="17">arXiv 원문 · PDF</text>'
        '<rect class="ma-sheet" x="6" y="26" width="118" height="132" rx="8"/>'
        '<rect class="ma-head" x="18" y="40" width="62" height="6" rx="3"/>'
        f'<g class="ma-type">{rows}</g>'
        '<rect class="ma-veil" x="6" y="26" width="118" height="132" rx="8"/>'
        '<g clip-path="url(#ma-clip)"><g class="ma-band">'
        '<rect x="6" y="26" width="118" height="26" fill="url(#ma-scan)"/>'
        '<rect class="ma-edge" x="6" y="51" width="118" height="1.3"/>'
        "</g></g>"
        '<rect class="ma-pill" x="18" y="132" width="54" height="15" rx="7.5"/>'
        '<text class="ma-pill-t" x="45" y="142.5">열지 않음</text>'

        # The rewrite, in the two tabs the site actually publishes. Its sheet
        # starts where the original's does, so the two labels sit on one line
        # and the drawing reads as this document becoming that one.
        '<text class="ma-label" x="200" y="17">PROBE 재작성 · 한글</text>'
        '<rect class="ma-sheet" x="200" y="26" width="356" height="132" rx="10"/>'
        '<text class="ma-tab ma-tab-1" x="216" y="46">요약</text>'
        '<text class="ma-tab ma-tab-2" x="254" y="46">상세</text>'
        '<line class="ma-rule" x1="212" y1="52" x2="544" y2="52"/>'
        '<rect class="ma-tabbar" x="214" y="50.6" width="26" height="2.4" rx="1.2"/>'
        f'<g class="ma-glance">{acts}'
        '<g class="ma-sum">'
        '<rect x="214" y="118" width="300" height="3.4" rx="1.7"/>'
        '<rect x="214" y="128" width="262" height="3.4" rx="1.7"/></g></g>'
        '<g class="ma-detail">'
        '<rect class="ma-thesis" x="214" y="64" width="188" height="7" rx="3.5"/>'
        '<g class="ma-body">'
        '<rect x="214" y="82" width="322" height="3.4" rx="1.7"/>'
        '<rect x="214" y="92" width="308" height="3.4" rx="1.7"/>'
        '<rect x="214" y="102" width="266" height="3.4" rx="1.7"/></g>'
        '<g class="ma-term">'
        '<rect class="ma-term-bg" x="214" y="112" width="158" height="40" rx="6"/>'
        '<rect class="ma-term-edge" x="214" y="112" width="3" height="40"/>'
        '<rect x="226" y="122" width="72" height="3" rx="1.5"/>'
        '<rect x="226" y="131" width="128" height="3" rx="1.5"/>'
        '<rect x="226" y="140" width="104" height="3" rx="1.5"/></g>'
        '<g class="ma-fig">'
        '<rect class="ma-card" x="384" y="112" width="158" height="40" rx="6"/>'
        '<g class="ma-fig-plot">'
        '<rect x="396" y="122" width="26" height="20" rx="3"/>'
        '<rect x="440" y="122" width="26" height="20" rx="3"/>'
        '<rect x="484" y="122" width="26" height="20" rx="3"/>'
        '<path d="M424 132 h13 M468 132 h13"/></g></g></g>'

        # The four pieces sit under the mark, so a piece in transit passes
        # behind the face and lands in front of the page it becomes.
        f'<g class="ma-rack"><rect x="132" y="57.4" width="58" height="1.2" rx=".6"/></g>'
        f"{pieces}"
        f'<g transform="translate(140,66)">{mark(42)}</g>'
        "</svg>"
    )


# One mark per `corpus.LINK_KINDS` kind, drawn on a 20-unit grid at a single
# stroke weight so the six read as one set. Drawn here rather than picked from
# the emoji block: an emoji set is six drawings by six hands — the weights,
# the saturation and even the perspective disagree — and the reader's device,
# not this build, decides what each one looks like. These take `currentColor`,
# so a link's mark and its label change together on hover and the pair follows
# the theme with everything else.
SRC_MARKS = {
    "arxiv": '<path d="M5 2.8h6.2L15 6.6V17a.6.6 0 0 1-.6.6H5a.6.6 0 0 1-.6-.6V3.4A.6.6 0'
             ' 0 1 5 2.8Z"/><path d="M11 2.8v4h4M7.2 10.5h5.6M7.2 13.4h5.6"/>',
    "code": '<path d="m7 6.5-4 3.6 4 3.6M13 6.5l4 3.6-4 3.6M11.4 4.6 8.6 15.6"/>',
    "weights": '<path d="M10 2.9 17 6.4v7.2L10 17.1 3 13.6V6.4Z"/>'
               '<path d="M3 6.4 10 10m0 0 7-3.6M10 10v7.1"/>',
    "data": '<ellipse cx="10" cy="5.3" rx="6" ry="2.4"/><path d="M4 5.3v9.4c0 1.3 2.7 2.4 6'
            ' 2.4s6-1.1 6-2.4V5.3M4 10c0 1.3 2.7 2.4 6 2.4s6-1.1 6-2.4"/>',
    "site": '<circle cx="10" cy="10" r="7.1"/><ellipse cx="10" cy="10" rx="2.9" ry="7.1"/>'
            '<path d="M3.2 7.6h13.6M3.2 12.4h13.6"/>',
    "demo": '<rect x="2.9" y="4.2" width="14.2" height="11.6" rx="2.2"/>'
            '<path d="m8.6 7.9 4.4 2.4-4.4 2.4Z"/>',
}


def src_mark(kind: str) -> str:
    """The mark for one resource kind, or nothing for a kind without one."""
    body = SRC_MARKS.get(kind)
    if not body:
        return ""
    return (f'<svg class="src-mark" viewBox="0 0 20 20" aria-hidden="true">'
            f"{body}</svg>")


def chip(label: str, cls: str = "", *, href: str = "", data: dict | None = None,
         mark: str = "") -> str:
    attrs = "".join(f' data-{k}="{esc(v)}"' for k, v in (data or {}).items())
    inner = f"{mark}{esc(label)}"
    classes = f"chip {cls}".strip()
    if href:
        return (
            f'<a class="{classes} link" href="{esc(href)}" target="_blank" '
            f'rel="noopener"{attrs}>{inner}</a>'
        )
    return f'<span class="{classes}"{attrs}>{inner}</span>'


def pillar_chips(pillars: list[str]) -> str:
    return "".join(chip(p, "pillar", data={"p": p}) for p in pillars)


def tag_chips(tags: list[str]) -> str:
    return "".join(chip(t, "tag") for t in tags)




def callout(icon: str, body_html: str, cls: str = "") -> str:
    classes = f"callout {cls}".strip()
    return (
        f'<div class="{classes}"><span class="ci">{icon}</span>'
        f"<div>{body_html}</div></div>"
    )



def mark_fab() -> str:
    """책갈피 for the section on screen, without going back to the contents.

    The contents are the exact surface — a flag per section — but they sit at
    the top of the article and a reader who stops reading is at the bottom of
    it. This marks where they are, which is what a 책갈피 means, and it is the
    same one-per-paper toggle: pressing it on a section already marked takes
    the mark off.

    Ships `hidden` and stays out of the page without a script. It belongs to
    상세 — 요약 is one screen and has no sections to stand in — so `shelf.js`
    shows it only while that surface is open.
    """
    return (
        '<button class="mark-fab" data-mark-fab hidden aria-pressed="false" '
        'aria-label="여기에 책갈피" title="여기에 책갈피">'
        '<svg viewBox="0 0 16 16" width="15" height="15" aria-hidden="true" '
        'focusable="false"><path d="M3.6 1.7h8.8v12.6L8 11.1l-4.4 3.2z"/></svg>'
        "</button>"
    )


def memo_panel(paper_id: str, title: str, paper_url: str, discussions_new: str) -> str:
    return f"""
<button class="memo-fab" data-memo-fab data-has-memo="0" aria-label="메모 열기">
  📝 <span>메모</span><span class="count"></span>
</button>
<div class="scrim" data-scrim data-open="0"></div>
<aside class="memo" data-memo-root data-open="0"
       data-paper-id="{esc(paper_id)}"
       data-paper-title="{esc(title)}"
       data-paper-url="{esc(paper_url)}"
       data-discussions-new="{esc(discussions_new)}"
       aria-label="이 논문의 메모">
  <div class="memo-head">
    <h3>메모</h3>
    <span class="memo-status" data-memo-status aria-live="polite"></span>
  </div>
  <p class="memo-anchor" data-memo-anchor hidden></p>
  <textarea data-memo-input placeholder="읽다가 생긴 의문·확인할 것을 적어두세요."></textarea>
  <p class="memo-note">
    초안은 <strong>이 브라우저에만</strong> 저장됩니다 — 다른 기기에서는 보이지 않고,
    사이트 데이터를 지우면 사라집니다. 남길 메모는 Discussions 로 발행하세요.
  </p>
  <div class="memo-actions">
    <button type="button" class="primary" data-memo-action="publish">Discussions 로 발행</button>
    <button type="button" data-memo-action="export">내보내기</button>
    <span class="spacer"></span>
    <button type="button" class="danger" data-memo-action="clear">삭제</button>
  </div>
</aside>
""".strip()


def page(
    *,
    title: str,
    body: str,
    depth: int,
    description: str = "",
    scripts: list[str] | None = None,
    extra_head: str = "",
    base: str = "",
    body_attrs: str = "",
) -> str:
    """Full document shell.

    Hrefs are relative and computed from page depth, so `--serve` on
    localhost, a `file://` open, and the deployed `/probe/` subpath all behave
    identically — and a future custom domain needs no rebuild.

    `base` overrides that with an absolute prefix. Exactly one page needs it:
    Pages serves `404.html` at whatever depth the bad URL had, so a relative
    `assets/site.css` resolves against `/probe/p/typo/` and the error page
    arrives unstyled with dead links.
    """
    up = base or "../" * depth
    # Classic scripts, not ES modules: `type="module"` is blocked by CORS on
    # `file://`, and opening a built page directly is the fastest way to check
    # a render. Shared state goes on `window.ProbeMemo` instead of exports.
    #
    # The four unconditional ones are the ones every page carries: theme.js
    # drives the nav's own button, brand.js the mark beside it, and the ⌘K
    # palette is reachable from anywhere — so its index, its matching rule and
    # the script itself ride along too. `defer` runs them in this order, which
    # is what lets `filter.js` further down the list read `match.js`.
    script_tags = "".join(
        f'<script src="{asset(f"{up}assets/{s}")}" defer></script>'
        for s in ["theme.js", "brand.js", "corpus-index.js", "match.js",
                  "palette.js", *(scripts or [])]
    )
    return f"""<!DOCTYPE html>
<html lang="ko" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
{f'<meta name="description" content="{esc(description)}">' if description else ""}
<link rel="icon" href="{FAVICON}">
<link rel="stylesheet" href="{asset(f"{up}assets/fonts.css")}">
<link rel="stylesheet" href="{asset(f"{up}assets/katex/katex.min.css")}">
<link rel="stylesheet" href="{asset(f"{up}assets/site.css")}">
{extra_head}
<script>
/* Runs before first paint. Two jobs: set the theme (otherwise a dark-mode
   reader gets a white flash on every navigation) and mark the document as
   scripted, so JS-only controls can hide themselves in CSS instead of
   appearing and then vanishing once a deferred script loads. */
(function(){{document.documentElement.classList.add('js');
try{{var t=localStorage.getItem('probe.theme');
if(!t)t=matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}}})();
</script>
</head>
<body{" " + body_attrs if body_attrs else ""}>
{nav(up)}
{body}
{script_tags}
</body>
</html>
"""


def cmdk_button() -> str:
    """The one part of the ⌘K palette the build prints.

    The dialog itself is `palette.js`'s markup, so a browser with no script
    never has it — but a reader needs something to press, and a shortcut nobody
    is told about is a shortcut nobody uses. `site.css` keeps the button off an
    unscripted page, the same way every other JS-only control here removes
    itself rather than sitting inert.

    It is the glyph alone, on every viewport — a desktop and a phone read the
    same button rather than one growing a label the other never had room for.
    The shortcut lives in the `title`, a pointer's-length away rather than
    printed beside the icon at all times. It reads `Ctrl K` here, which is
    what it is on every platform but one; `palette.js` swaps it to `⌘K` on a
    Mac, since which keyboard is in front of the reader is the one thing about
    this button the build cannot know.
    """
    return ('<button type="button" class="nav-cmdk" data-cmdk-open '
            'aria-label="논문 찾기" title="논문 찾기 (Ctrl K)">'
            '<svg viewBox="0 0 16 16" width="15" height="15" '
            'aria-hidden="true" focusable="false">'
            '<circle cx="7" cy="7" r="4.6" fill="none" stroke="currentColor" '
            'stroke-width="1.6"/>'
            '<path d="M10.4 10.4 14 14" stroke="currentColor" stroke-width="1.6" '
            'stroke-linecap="round"/></svg></button>')


def nav(up: str) -> str:
    return f"""<nav class="site-nav">
  <div class="nav-inner">
    <a class="nav-logo" href="{up}index.html">{mark(19)}PROBE</a>
    <span class="nav-spacer"></span>
    <ul class="nav-links">
      <li><a href="{up}index.html">논문</a></li>
      <li><a href="{up}c/index.html">같이 읽기</a></li>
      <li><a href="{up}shelf/index.html">내 서재</a></li>
    </ul>
    {cmdk_button()}
    <button class="icon-btn" data-theme-toggle aria-label="다크 모드로" title="다크 모드로">☾</button>
  </div>
</nav>"""

