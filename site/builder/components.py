"""HTML components as plain functions returning strings.

No template engine: a handful of page types and ~20 components do not justify
a fifth dependency. Every interpolation goes through `esc()`.
"""

from __future__ import annotations

import html

from . import assets_out

# Where the repository lives. The nav links it on every page, and `pages.py`
# builds the blob and Discussions URLs off the same string — one name for the
# one place the site's source, its context files and its threads all are.
REPO = "jonghochoi/probe"
REPO_URL = f"https://github.com/{REPO}"
RAW_URL = f"https://raw.githubusercontent.com/{REPO}/main"


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


# ── The icon set ────────────────────────────────────────────────────────────
# One pen for every glyph a control is drawn with: a 16px viewBox, no fill,
# 1.6px strokes in `currentColor`, round caps and joins. Size and colour come
# from the control's own CSS rule, so one path serves the nav's 32px button and
# a list row's 14px star without a second copy of the shape.
#
# A text glyph cannot hold this line — `☾` and `☰` are drawn by whichever font
# the reader happens to have, at a weight and an optical size the page has no
# say in, and `🔍` arrives in colour. So every control here is a vector, and
# the characters that stay are the ones that are punctuation rather than
# controls: `↗` after a link's label, the `✓` and `●` that mark a row's state
# inside a line of text.
# The star is the one glyph whose points leave this file — `assets/shelf.js`
# draws the same star on the rows it builds at runtime — so the outline is a
# named constant rather than a line in the set, and a move here is a move there.
_STAR_D = ("m8 1.9 1.85 3.75 4.15.6-3 2.93.71 4.13L8 11.4l-3.71 "
           "1.91.71-4.13-3-2.93 4.15-.6Z")
# 책갈피, the same way: `mark_fab()` presses it, and `assets/shelf.js` and
# `assets/hub.js` carry the same points for the rows they build at runtime.
_FLAG_D = "M3.6 1.7h8.8v12.6L8 11.1l-4.4 3.2z"

_ICON_PATHS = {
    "search": '<circle cx="7" cy="7" r="4.6"/><path d="M10.4 10.4 14 14"/>',
    "moon": '<path d="M13.6 9.9A5.8 5.8 0 0 1 6.1 2.4 6 6 0 1 0 13.6 9.9Z"/>',
    "sun": ('<circle cx="8" cy="8" r="3"/>'
            '<path d="M8 1.2v1.5M8 13.3v1.5M2.6 2.6l1.1 1.1M12.3 12.3l1.1 1.1'
            'M1.2 8h1.5M13.3 8h1.5M2.6 13.4l1.1-1.1M12.3 3.7l1.1-1.1"/>'),
    "menu": '<path d="M2.3 4.6h11.4M2.3 8h11.4M2.3 11.4h11.4"/>',
    "close": '<path d="M3.8 3.8 12.2 12.2M12.2 3.8 3.8 12.2"/>',
    # The one shape that carries a state rather than a name: `index.css` fills
    # it from `currentColor` on the pressed button, so on and off are the same
    # path and nothing has to swap markup to answer a click.
    "star": f'<path d="{_STAR_D}"/>',
    # 읽음 — the claim the reader makes, drawn as the mark people make for it.
    "check": '<path d="M3 8.4 6.4 11.6 13 4.6"/>',
    # The presentation controls. A slide deck's controls are the one place on
    # the site where a label costs more than it carries: every one of them sits
    # on the frame a room is looking at, and 전체 화면 · 노트 · 목록 · 레이저 ·
    # 나가기 spelled out is five words of chrome competing with the sentence on
    # screen. So they are glyphs at the same weight as the rest of the set, and
    # the word survives in `aria-label` and `title`, where a reader who needs it
    # can still get it.
    # Four corners pulling apart, which is the shape of the thing the button
    # does: the frame stops being a card on a page and becomes the screen.
    "expand": '<path d="M6 2.3H2.3V6M10 2.3h3.7V6M13.7 10v3.7H10M2.3 10v3.7H6"/>',
    # A card with what is said over the slide written on it. Two rules rather
    # than three: at 15px a third line closes the gaps and the card reads solid.
    "note": ('<rect x="2.3" y="3.1" width="11.4" height="9.8" rx="1.7"/>'
             '<path d="M5.2 6.7h5.6M5.2 9.4h3.3"/>'),
    "grid": ('<rect x="2.2" y="2.2" width="5.1" height="5.1" rx="1.2"/>'
             '<rect x="8.7" y="2.2" width="5.1" height="5.1" rx="1.2"/>'
             '<rect x="2.2" y="8.7" width="5.1" height="5.1" rx="1.2"/>'
             '<rect x="8.7" y="8.7" width="5.1" height="5.1" rx="1.2"/>'),
    # A pointer is an aim rather than a beam: the dot is what the room follows,
    # and the ticks say it is being held on something.
    "laser": ('<circle cx="8" cy="8" r="4.5"/><circle cx="8" cy="8" r="1.25"/>'
              '<path d="M8 1.1v1.7M8 13.2v1.7M1.1 8h1.7M13.2 8h1.7"/>'),
    "prev": '<path d="M9.9 3.3 5.1 8l4.8 4.7"/>',
    "next": '<path d="M6.1 3.3 10.9 8l-4.8 4.7"/>',
    # A slide's clip. The button carries both and the stylesheet shows the one
    # the clip's own state calls for.
    "play": '<path d="M5 3.2v9.6L12.6 8Z"/>',
    "pause": '<path d="M5.6 3.4v9.2M10.4 3.4v9.2"/>',
}


def icon(name: str, size: int = 16) -> str:
    """One glyph from the set above, sized by the caller."""
    return (
        f'<svg class="ico ico-{name}" viewBox="0 0 16 16" '
        f'width="{size}" height="{size}" fill="none" stroke="currentColor" '
        'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" '
        f'aria-hidden="true" focusable="false">{_ICON_PATHS[name]}</svg>'
    )


def mark(size: int) -> str:
    """The animated PROBE mark — a probe that looks back at the reader.

    One `viewBox` serves every size; the caller picks the pixel box. Geometry
    only: the idle bob, the blink, the mood swap and the sprout's sway are
    keyframes in `site.css`, and `brand.js` steers the pupils after the
    pointer. Two eyes rather than one, because a single eye reads as
    "something moved" while a pair reads as "it is looking at you" — which is
    the whole point of putting a face on a scouting agent. Each eye ships both
    of its faces at once — the round pupil and the `joy` arc it smiles with —
    because a stroke cannot be tweened into a disc, so the mood keyframes
    cross-fade between them and each face holds half the cycle. Decorative — the
    logo names the site in text right next to it — so it stays out of the
    accessibility tree.
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
        '<g class="sprout"><path class="stem" d="M48 26.5 V18.5"/>'
        '<path class="leaf" d="M48 20.5 C43 20.6, 39.4 17.6, 38.5 13.5 C43.2 13, 47.2 15.6, 48 20.5 Z"/>'
        '<path class="leaf" d="M48 18.2 C53.2 17.6, 57.6 14, 58.5 9.5 C53.2 9.5, 48.8 13, 48 18.2 Z"/></g>'
        '<rect class="hull" x="17" y="27" width="62" height="54" rx="19"/>'
        f"{eyes}"
        "</g></svg>"
    )


def mast(*, eyebrow: str, title: str, count: str = "") -> str:
    """The band every list page opens on.

    One frame for the five destinations the nav names, because they are one
    level of the site and a band that changed shape between them would say
    otherwise. Two things and no third: what this surface is, and what it does.
    Nothing sits beside the title — the list under the band is what the page
    is for, and anything set there either repeats that list or argues for it,
    when the list makes its own case one scroll down.

    `count` is the exception the landing earns — the pair it prints beside its
    title for a reader whose filter bar has not arrived — and it is the only
    number any band carries, because it is the only one the build has. What
    this browser has kept is not a fact this generator holds.
    """
    count_html = f'<p class="mast-count">{esc(count)}</p>' if count else ""
    return f"""<header class="mast">
  <div class="mast-inner">
    <div class="mast-text">
      <p class="mast-eyebrow">{esc(eyebrow)}</p>
      <div class="mast-line">
        <h1>{esc(title)}</h1>{count_html}
      </div>
    </div>
  </div>
</header>"""


# One mark per `corpus.LINK_KINDS` kind, drawn on a 20-unit grid at a single
# stroke weight so the six read as one set — GitHub's mark aside, which is a
# brand silhouette and keeps its own fill. Drawn here rather than picked from
# the emoji block: an emoji set is six drawings by six hands — the weights,
# the saturation and even the perspective disagree — and the reader's device,
# not this build, decides what each one looks like. These take `currentColor`,
# so a link's mark and its label change together on hover and the pair follows
# the theme with everything else.
SRC_MARKS = {
    "arxiv": '<path d="M5 2.8h6.2L15 6.6V17a.6.6 0 0 1-.6.6H5a.6.6 0 0 1-.6-.6V3.4A.6.6 0'
             ' 0 1 5 2.8Z"/><path d="M11 2.8v4h4M7.2 10.5h5.6M7.2 13.4h5.6"/>',
    # GitHub's own mark (Octicons `mark-github`, MIT), drawn on its 16-unit
    # grid and scaled onto this one. The one filled shape in the set: the
    # silhouette is what a reader recognises, and outlined it stops being the
    # mark. It stands for `code` because every code link the corpus declares
    # is a GitHub repository.
    "code": ('<path fill="currentColor" stroke="none" transform="translate(1.2 1.2) scale(1.1)" '
             'd="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 '
             '0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 '
             '0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27'
             '-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 '
             '1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66'
             '-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 '
             '0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z"/>'),
    "weights": '<path d="M10 2.9 17 6.4v7.2L10 17.1 3 13.6V6.4Z"/>'
               '<path d="M3 6.4 10 10m0 0 7-3.6M10 10v7.1"/>',
    "data": '<ellipse cx="10" cy="5.3" rx="6" ry="2.4"/><path d="M4 5.3v9.4c0 1.3 2.7 2.4 6'
            ' 2.4s6-1.1 6-2.4V5.3M4 10c0 1.3 2.7 2.4 6 2.4s6-1.1 6-2.4"/>',
    # The project's own page — its home, drawn to fill the grid the way the
    # document and the mark beside it do.
    "site": '<path d="M2.2 9.4 10 2.6l7.8 6.8"/><path d="M4.4 7.6v9.6h11.2V7.6"/>'
            '<path d="M8.2 17.2v-4.8h3.6v4.8"/>',
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
        f'focusable="false"><path d="{_FLAG_D}"/></svg>'
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


def icon_links(up: str) -> str:
    """Every icon the document declares, as real files rather than a data URI.

    A data URI reaches exactly one consumer — a browser that parses the
    markup — and the tab is not the only thing that asks for an icon. A feed
    reader, a bookmark manager, a chat unfurl and iOS's home screen each go
    looking for a file, and the deployed site sits under `/probe/`, so the
    `/favicon.ico` those clients fall back to is not even this site's to
    answer. Naming the files is what puts an icon in all of them.

    The SVG is the one a browser prefers and the only one that follows the
    reader's colour scheme; the 32 px PNG is what a client that will not take
    an SVG icon gets instead, listed after it so the SVG wins wherever both
    are understood. `theme-color` tints the browser chrome around the page on
    the platforms that paint it, and is a pair because the page itself is.
    """
    return "\n".join([
        f'<link rel="icon" type="image/svg+xml" href="{asset(f"{up}assets/favicon.svg")}">',
        f'<link rel="icon" type="image/png" sizes="32x32" href="{asset(f"{up}assets/favicon-32.png")}">',
        f'<link rel="apple-touch-icon" sizes="180x180" href="{asset(f"{up}assets/apple-touch-icon.png")}">',
        '<meta name="theme-color" content="#faf7f5" media="(prefers-color-scheme: light)">',
        '<meta name="theme-color" content="#14110f" media="(prefers-color-scheme: dark)">',
    ])


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
    here: str = "",
) -> str:
    """Full document shell.

    Hrefs are relative and computed from page depth, so `--serve` on
    localhost, a `file://` open, and the deployed `/probe/` subpath all behave
    identically — and a future custom domain needs no rebuild.

    `here` is the `DESTINATIONS` key this page sits under, which the nav marks
    as the reader's place. Every page passes one but `404.html`, which stands
    under no destination.

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
    # The unconditional ones are the ones every page carries: theme.js drives
    # the nav's own button, brand.js the mark beside it, nav.js the menu the
    # nav folds its destinations into on a phone, and the ⌘K palette is
    # reachable from anywhere — so its index, its matching rule and the script
    # itself ride along too. `defer` runs them in this order, which is what
    # lets `filter.js` further down the list read `match.js`.
    script_tags = "".join(
        f'<script src="{asset(f"{up}assets/{s}")}" defer></script>'
        for s in ["theme.js", "brand.js", "nav.js", "corpus-index.js",
                  "match.js", "palette.js", *(scripts or [])]
    )
    return f"""<!DOCTYPE html>
<html lang="ko" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
{f'<meta name="description" content="{esc(description)}">' if description else ""}
{icon_links(up)}
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
{nav(up, here)}
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
            f'{icon("search", 15)}</button>')


# GitHub's own mark, the one shape a reader recognises as "the source is over
# there". One path at a 16 px viewBox, inlined like every other glyph here —
# the site fetches nothing from a third party, least of all a logo.
GITHUB_MARK = (
    "M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0"
    "-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13"
    "-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66"
    ".07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15"
    "-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0"
    " 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82"
    " 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01"
    " 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"
)


def repo_link() -> str:
    """The way out to the repository, on every page.

    The site publishes one half of this project — the rewrites and the
    comparisons — and the other half is the part that produced them: the
    prompts, the human's `context/`, the format contracts, this generator. A
    reader who wants to know how a paper came to be written this way has
    nowhere on the site to go and ask.

    It sits last in the nav, past the theme toggle, and is spaced and drawn
    exactly like it: the three of them are one row of glyph-sized controls, and
    a glyph set apart by its border or by its spacing reads as a control that
    lost something rather than as one of a different kind. Last is what says it
    is of a different kind, and it is also what lets it arrive without moving
    anything that was already in reach.

    The glyph alone, like the two controls beside it, with the destination in
    the `title` and in `aria-label` — an icon-sized link is nothing to a screen
    reader unless it is named. Nothing here needs a script, so unlike the ⌘K
    button this one is on an unscripted page too.
    """
    return (
        f'<a class="icon-btn nav-repo" href="{REPO_URL}" '
        'target="_blank" rel="noopener noreferrer" '
        'aria-label="GitHub (새 탭)" title="GitHub">'
        '<svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true" '
        f'focusable="false"><path fill="currentColor" d="{GITHUB_MARK}"/>'
        '</svg></a>'
    )


# Every place the site goes, in the order the nav offers them. The row and the
# phone's sheet print the same list rather than each keeping their own, so a
# destination cannot arrive in one and be missing from the other.
#
# A track's destination is named for its track, in two syllables of Korean —
# 탐색 Scouting, 분석 Analysis, 비교 Comparison, 발표 Presentation — and they
# run in the pipeline's order, the order the README's table lists them in.
# Five labels of one width read as one row on a desktop and fit beside the
# controls without crowding them. 서재 is the reader's own shelf rather than a
# track, and stands after them.
#
# The key in front is what a page names itself with. A paper and a comparison
# each sit *under* a destination rather than being one, so `p/<id>/` marks
# 분석 and `c/<slug>/` marks 비교 — the mark answers "which part of the site
# is this", which is what a reader glancing at a nav is asking.
#
# 발표 is the one destination that is an index and nothing else: a
# presentation is a tab on its paper's page, so the row it lists links back
# into 분석, and a paper page opened at that tab still marks 분석 — which is
# the part of the site it is standing in.
DESTINATIONS = (("scout", "s/index.html", "탐색"),
                ("papers", "index.html", "분석"),
                ("compare", "c/index.html", "비교"),
                ("talk", "t/index.html", "발표"),
                ("shelf", "shelf/index.html", "서재"))


def _current(key: str, here: str) -> str:
    """`aria-current` on the destination the reader is standing in.

    One attribute carries the whole mark: `site.css` draws the rule under it
    from `[aria-current="page"]`, and a screen reader is told which of the
    three it is without a second, visual-only class to keep in step. `here`
    may be empty — 404 stands under no destination and marks none.
    """
    return ' aria-current="page"' if key and key == here else ""


def nav_sheet(up: str, here: str = "") -> str:
    """The phone's menu — the row's destinations, one per line, plus the way out.

    A phone is not wide enough for the mark, the site's name, four
    destinations and three glyph controls on one line, and the name is the part
    that says which site this is. So the destinations fold behind one button
    and the name stays: the row keeps what a reader cannot reconstruct, and the
    sheet takes what a label can name in full.

    It is `hidden` until `nav.js` opens it, and the button that opens it is
    printed only for a scripted browser — an unscripted phone keeps the row of
    links it always had, and gives up the name instead (`site.css`).
    """
    links = "".join(
        f'<a href="{up}{href}"{_current(key, here)}>{label}</a>'
        for key, href, label in DESTINATIONS)
    return (f'<div class="nav-sheet" id="nav-sheet" hidden>{links}'
            f'<a class="nav-sheet-out" href="{REPO_URL}" target="_blank" '
            'rel="noopener noreferrer">GitHub ↗</a></div>')


def nav(up: str, here: str = "") -> str:
    """The row every page opens on — where the site goes, and what it can do.

    Two clusters, and they are different kinds: five places to go, then three
    things to do to the page in front of the reader. A hairline stands between
    them (`site.css`), because the seam between an unboxed label and a bordered
    32px button reads as a control that lost its border unless something says
    the boundary is meant.

    `here` is the destination this page sits under, and marking it is the
    other half of the same job: a row of five names that never says which one
    the reader is standing in is a row with a hole in it, and the hole is what
    makes the labels beside the controls look unfinished.
    """
    links = "".join(
        f'<li><a href="{up}{href}"{_current(key, here)}>{label}</a></li>'
        for key, href, label in DESTINATIONS)
    return f"""<nav class="site-nav">
  <div class="nav-inner">
    <a class="nav-logo" href="{up}index.html">{mark(19)}<span class="nav-word">PROBE</span></a>
    <span class="nav-spacer"></span>
    <ul class="nav-links">{links}</ul>
    <span class="nav-rule"></span>
    {cmdk_button()}
    <button class="icon-btn" data-theme-toggle aria-label="다크 모드로" title="다크 모드로">{icon("moon", 15)}{icon("sun", 15)}</button>
    {repo_link()}
    <button class="icon-btn nav-menu" data-nav-menu aria-expanded="false"
            aria-controls="nav-sheet" aria-label="메뉴 열기" title="메뉴">{icon("menu", 15)}</button>
  </div>
  {nav_sheet(up, here)}
</nav>"""

