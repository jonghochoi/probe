"""HTML components as plain functions returning strings.

No template engine: a handful of page types and ~20 components do not justify
a fifth dependency. Every interpolation goes through `esc()`.
"""

from __future__ import annotations

import html

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

    The sentence it answers is "원문을 열지 않고도 메커니즘까지 이해되도록,
    논문을 한 편씩 새로 씁니다", and the drawing carries it in one loop: a scan
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


def chip(label: str, cls: str = "", *, href: str = "", data: dict | None = None) -> str:
    attrs = "".join(f' data-{k}="{esc(v)}"' for k, v in (data or {}).items())
    inner = esc(label)
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
    # theme.js is unconditional — the nav button it drives is on every page.
    script_tags = "".join(
        f'<script src="{up}assets/{s}" defer></script>'
        for s in ["theme.js", "brand.js", *(scripts or [])]
    )
    return f"""<!DOCTYPE html>
<html lang="ko" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
{f'<meta name="description" content="{esc(description)}">' if description else ""}
<link rel="icon" href="{FAVICON}">
<link rel="stylesheet" href="{up}assets/fonts.css">
<link rel="stylesheet" href="{up}assets/katex/katex.min.css">
<link rel="stylesheet" href="{up}assets/site.css">
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


def nav(up: str) -> str:
    return f"""<nav>
  <div class="nav-inner">
    <a class="nav-logo" href="{up}index.html">{mark(19)}PROBE</a>
    <span class="nav-spacer"></span>
    <ul class="nav-links">
      <li><a href="{up}index.html">논문</a></li>
      <li><a href="{up}shelf/index.html">내 서재</a></li>
    </ul>
    <button class="icon-btn" data-theme-toggle aria-label="다크 모드로">☾</button>
  </div>
</nav>"""

