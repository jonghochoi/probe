"""HTML components as plain functions returning strings.

No template engine: a handful of page types and ~20 components do not justify
a fifth dependency. Every interpolation goes through `esc()`.
"""

from __future__ import annotations

import html
import re

from . import assets_out

# Where the repository lives. The nav links it on every page, and `pages.py`
# builds the blob and Discussions URLs off the same string — one name for the
# one place the site's source, its context files and its threads all are.
REPO = "jonghochoi/probe"
REPO_URL = f"https://github.com/{REPO}"
RAW_URL = f"https://raw.githubusercontent.com/{REPO}/main"
# The deployed root. Pages are linked relatively (see `page()`), but a link
# preview is fetched by a crawler that never sees the page's own URL, so the
# one image it is pointed at needs the absolute address.
SITE = f"https://{REPO.split('/')[0]}.github.io/{REPO.split('/')[1]}/"


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


# The corpus writes a space between a number and its unit (`41.4 %`, `240 Hz`),
# and that space is a break opportunity: a phone ends a line on `41.4` and
# starts the next on `%`. A no-break space keeps the reading whole. Units only,
# never a Hangul counter — `3 분석` is not `3 분`. Applied to printed text and
# never to `esc()` as a whole, so a filter haystack keeps the plain space a
# reader types.
_UNIT_GAP = re.compile(
    r"(?<=\d) (?=(?:%p?|pp|×|k?Hz|ms|s|h|min|mm/s|mm|cm|m|Nm|N|rad|FPS|fps"
    r"|GB|μL|°|[MBK])(?![A-Za-z0-9]))"
)


def glue_units(text: str) -> str:
    """`text` with each number–unit space made a no-break space."""
    return _UNIT_GAP.sub("\u00a0", text)


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
# 책갈피, the same way: `mark_button()` presses it, and `assets/shelf.js` and
# `assets/hub.js` carry the same points for the rows they build at runtime.
_FLAG_D = "M3.6 1.7h8.8v12.6L8 11.1l-4.4 3.2z"

_ICON_PATHS = {
    "search": '<circle cx="7" cy="7" r="4.6"/><path d="M10.4 10.4 14 14"/>',
    "moon": '<path d="M13.6 9.9A5.8 5.8 0 0 1 6.1 2.4 6 6 0 1 0 13.6 9.9Z"/>',
    "sun": ('<circle cx="8" cy="8" r="3"/>'
            '<path d="M8 1.2v1.5M8 13.3v1.5M2.6 2.6l1.1 1.1M12.3 12.3l1.1 1.1'
            'M1.2 8h1.5M13.3 8h1.5M2.6 13.4l1.1-1.1M12.3 3.7l1.1-1.1"/>'),
    "menu": '<path d="M2.3 4.6h11.4M2.3 8h11.4M2.3 11.4h11.4"/>',
    # 연구 축 — three stacked layers, the axes a list is filtered by.
    "layers": '<path d="M8 2.4 2.4 5.2 8 8l5.6-2.8z"/><path d="M2.4 8 8 10.8 13.6 8"/><path d="M2.4 10.8 8 13.6l5.6-2.8"/>',
    # The one shape that carries a state rather than a name: `index.css` fills
    # it from `currentColor` on the pressed button, so on and off are the same
    # path and nothing has to swap markup to answer a click.
    "star": f'<path d="{_STAR_D}"/>',
    # 읽음 — the claim the reader makes, drawn as the mark people make for it.
    "check": '<path d="M3 8.4 6.4 11.6 13 4.6"/>',
    # 색 테마 — a painter's palette, the reader's colour.
    "palette": ('<path d="M8 1.8a6.2 6.2 0 1 0 0 12.4c.9 0 1.3-.6 1.3-1.2 0-.8-.6-1-.6-1.7 0-.6.5-1 '
                '1.1-1h1.6a2.8 2.8 0 0 0 2.8-2.8C14.2 4.4 11.4 1.8 8 1.8Z"/>'
                '<circle cx="5" cy="7" r=".5"/><circle cx="7.6" cy="4.6" r=".5"/><circle cx="10.6" cy="5.6" r=".5"/>'),
    # 책갈피 — the flag a paper's contents mark a section with.
    "flag": f'<path d="{_FLAG_D}"/>',
    # 설정 — two sliders, the button the nav's card opens from.
    "sliders": ('<path d="M2.4 4.6h6.2M12 4.6h1.6M2.4 11.4h1.6M7.4 11.4h6.2"/>'
                '<circle cx="10.3" cy="4.6" r="1.7"/><circle cx="5.7" cy="11.4" r="1.7"/>'),
    # 닫기 — the cross a card closes with.
    "close": '<path d="M4.2 4.2l7.6 7.6M11.8 4.2l-7.6 7.6"/>',
    # More — the three dots a menu of the rarer actions opens from.
    "more": '<circle cx="3.6" cy="8" r=".7"/><circle cx="8" cy="8" r=".7"/><circle cx="12.4" cy="8" r=".7"/>',
    # 탐색 회차 — a month page, the cell the date line opens its calendar from.
    "calendar": '<rect x="2.4" y="3.4" width="11.2" height="10.4" rx="1.6"/><path d="M2.4 6.6h11.2M5.6 1.8v2.8M10.4 1.8v2.8"/>',
    # 목차 — three lines, the last one short: a list of headings.
    "list": '<path d="M2.6 4h10.8M2.6 8h10.8M2.6 12h6.4"/>',
    # 메모 — a pencil, because the button opens a place to write.
    "pencil": '<path d="M10.6 2.7 13.3 5.4 5.6 13.1 2.4 13.6 2.9 10.4Z"/><path d="M9.1 4.2l2.7 2.7"/>',
}


def icon(name: str, size: int = 16) -> str:
    """One glyph from the set above, sized by the caller."""
    return (
        f'<svg class="ico ico-{name}" viewBox="0 0 16 16" '
        f'width="{size}" height="{size}" fill="none" stroke="currentColor" '
        'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" '
        f'aria-hidden="true" focusable="false">{_ICON_PATHS[name]}</svg>'
    )


_SPROUT = ('<g class="sprout"><path class="stem" d="M48 26.5 V18.5"/>'
           '<path class="leaf" d="M48 20.5 C43 20.6, 39.4 17.6, 38.5 13.5 C43.2 13, 47.2 15.6, 48 20.5 Z"/>'
           '<path class="leaf" d="M48 18.2 C53.2 17.6, 57.6 14, 58.5 9.5 C53.2 9.5, 48.8 13, 48 18.2 Z"/></g>')

# The wardrobe — what the first screen's mark wears (`home.js` picks it,
# `home.css` shows it). The track props are the README icons' own drawings
# (`assets/probe-*.svg`), on the same 96-unit grid, so a prop moves in both
# places or neither. Three layers, by where a prop sits in the stack: behind
# the eyes (the deerstalker, which carries its own sprout so the sprout still
# pokes through the cap), in front of them (what rides under the eyes or on
# the hull — the party hat sits at a tilt on the hull's shoulder, clear of
# the sprout, with a glint in each eye), and off the bobbing body (what
# floats over the head or stands on the ground — the confetti drifts down
# the two sides, never across the face). The tweed's pattern id is the page's only one, since the first
# screen is the one page that draws the wardrobe.
_WARDROBE_UNDER = (
    '<defs><pattern id="w-tw" width="3.4" height="3.4" patternUnits="userSpaceOnUse">'
    '<path class="w-weave" d="M0 0 H3.4 M0 0 V3.4"/></pattern></defs>'
    '<g class="w w-hat">'
    '<path class="w-flap" d="M18 33 C13 38, 14 46, 17.5 49 C21 47, 23.5 41, 23 34 Z"/>'
    '<path class="w-flap" d="M78 33 C83 38, 82 46, 78.5 49 C75 47, 72.5 41, 73 34 Z"/>'
    '<path class="w-cap" d="M18.5 38 C18.5 25, 31 17.5, 48 17.5 C65 17.5, 77.5 25, 77.5 38 Z"/>'
    '<path class="w-tweed" d="M18.5 38 C18.5 25, 31 17.5, 48 17.5 C65 17.5, 77.5 25, 77.5 38 Z"/>'
    '<path class="w-visor" d="M26 37 C34 43.5, 62 43.5, 70 37 Z"/>'
    f"{_SPROUT}</g>"
)
_WARDROBE_OVER = (
    '<g class="w w-sleep"><path class="w-closed" d="M30 52 q6 5 12 0"/>'
    '<path class="w-closed" d="M54 52 q6 5 12 0"/></g>'
    '<g class="w w-scout">'
    '<path class="w-mast" d="M77.25 44 V29.6"/><circle class="w-sig" cx="77.25" cy="23.5" r="2.2"/>'
    '<path class="w-wave" d="M74.01 18.69 A5.8 5.8 0 0 1 80.49 18.69"/>'
    '<path class="w-wave w-w2" d="M71.66 15.21 A10 10 0 0 1 82.84 15.21"/>'
    '<rect class="w-rim" x="73.5" y="41" width="7.5" height="19" rx="3.75"/>'
    '<rect class="w-rim" x="72" y="49.4" width="5" height="4.6" rx="1.5"/>'
    '<circle class="w-glass" cx="60" cy="52" r="12.6"/><circle class="w-mast" cx="60" cy="52" r="13.4"/>'
    '<path class="w-shine" d="M51.2 47.2 a10 10 0 0 1 4.6 -4.6 l1 1.8 a8 8 0 0 0 -3.7 3.7 z"/></g>'
    '<g class="w w-read"><g transform="rotate(-4 48 74.5)">'
    '<rect class="w-page" x="27" y="66" width="42" height="17" rx="3"/>'
    '<rect class="w-line" x="33" y="69.6" width="30" height="2.2" rx="1.1"/>'
    '<rect class="w-line" x="33" y="73.4" width="30" height="2.2" rx="1.1"/>'
    '<rect class="w-line" x="33" y="77.2" width="19" height="2.2" rx="1.1"/>'
    '<g class="w-slide"><rect class="w-mag" x="32" y="71.2" width="12" height="4.2" rx="2.1"/>'
    '<circle class="w-stone" cx="38" cy="73.3" r="7"/></g></g></g>'
    '<g class="w w-pages">'
    '<g transform="rotate(-6 33 86)"><rect class="w-page" x="21" y="60" width="24" height="26" rx="2.5"/>'
    '<rect class="w-line" x="25.5" y="64" width="15" height="2.2" rx="1.1"/>'
    '<rect class="w-bar" x="26" y="76" width="3.8" height="6" rx=".8"/>'
    '<rect class="w-bar" x="31.6" y="72" width="3.8" height="10" rx=".8"/>'
    '<rect class="w-bar" x="37.2" y="67" width="3.8" height="15" rx=".8"/>'
    '<ellipse class="w-ring" cx="37.1" cy="74" rx="5.4" ry="10" transform="rotate(-10 37.1 74)" pathLength="100"/></g>'
    '<g transform="rotate(6 63 86)"><rect class="w-page" x="51" y="60" width="24" height="26" rx="2.5"/>'
    '<rect class="w-line" x="55.5" y="64" width="15" height="2.2" rx="1.1"/>'
    '<rect class="w-bar" x="56" y="76" width="3.8" height="6" rx=".8"/>'
    '<rect class="w-bar" x="61.6" y="72" width="3.8" height="10" rx=".8"/>'
    '<rect class="w-bar" x="67.2" y="78" width="3.8" height="4" rx=".8"/>'
    '<ellipse class="w-ring" cx="67.1" cy="74" rx="5.4" ry="10" transform="rotate(-10 67.1 74)" pathLength="100"/></g></g>'
    '<g class="w w-party"><g transform="rotate(-18 31 28)">'
    '<path class="w-cone" d="M22 28 L31 6 L40 28 Z"/>'
    '<path class="w-band" d="M24.05 23 L37.95 23 L36.73 20 L25.27 20 Z"/>'
    '<path class="w-band" d="M26.91 16 L35.09 16 L33.86 13 L28.14 13 Z"/>'
    '<ellipse class="w-brim" cx="31" cy="28" rx="10.5" ry="2.2"/>'
    '<circle class="w-pom" cx="31" cy="5.4" r="3.2"/></g>'
    '<circle class="w-glint" cx="38.4" cy="49.6" r="1.9"/><circle class="w-glint" cx="62.4" cy="49.6" r="1.9"/>'
    '<circle class="w-glint" cx="34.2" cy="54.6" r=".9"/><circle class="w-glint" cx="58.2" cy="54.6" r=".9"/></g>'
    '<g class="w w-sweat"><path class="w-drop" d="M82 33 C84.5 37, 85 39.5, 82 40.5 C79 39.5, 79.5 37, 82 33 Z"/></g>'
)
_WARDROBE_OUT = (
    '<g class="w w-bulb">'
    + "".join(f'<path class="w-ray" d="{d}"/>' for d in (
        "M61.1 9.8 L57.8 8.6", "M64.6 5.2 L62.5 2.4", "M70 3.5 L70 0", "M75.4 5.2 L77.5 2.4",
        "M78.9 9.8 L82.2 8.6", "M79.2 15.5 L82.6 16.4", "M60.8 15.5 L57.4 16.4"))
    + '<path class="w-bulbglass" d="M70 4 C75 4, 78.5 7.6, 78.5 12.4 C78.5 16, 76 17.6, 74.6 20 L65.4 20 '
      'C64 17.6, 61.5 16, 61.5 12.4 C61.5 7.6, 65 4, 70 4 Z"/>'
      '<path class="w-fil" d="M67.4 19 L67.4 14.6 L69 12.4 L71 14.6 L72.6 12.4 L72.6 19"/>'
      '<rect class="w-screw" x="65.6" y="20.6" width="8.8" height="2.6" rx="1"/>'
      '<rect class="w-screw" x="66.4" y="23.8" width="7.2" height="2.4" rx="1"/></g>'
      '<g class="w w-bang"><text class="w-bangt" x="76" y="20" text-anchor="middle">!</text></g>'
      '<g class="w w-zz"><text class="w-z" x="70" y="22">z</text>'
      '<text class="w-z" x="76" y="16">z</text><text class="w-z" x="83" y="9">Z</text></g>'
      '<g class="w w-cal"><rect class="w-page" x="79" y="64" width="19" height="22" rx="2"/>'
      '<rect class="w-caltop" x="79" y="64" width="19" height="5.5" rx="2"/>'
      '<path class="w-calx" d="M84 74 l9 8 M93 74 l-9 8"/></g>'
      '<g class="w w-party">'
    + "".join(f'<rect class="w-cf w-cf{i % 4}" x="{x}" y="{y}" width="5" height="3.4" rx=".6" '
              f'transform="rotate({r} {x + 2.5} {y + 1.7})"/>'
              for i, (x, y, r) in enumerate(((5, 14, 20), (86, 20, -25), (9, 40, -35), (84, 46, 30),
                                             (4, 64, 15), (88, 70, -15), (62, 6, 40), (74, 12, -10))))
    + "</g>"
)


def mark(size: int, wardrobe: bool = False) -> str:
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

    `wardrobe` adds the props the first screen dresses it in, every one hidden
    until `data-w` names it, so the mark drawn with them looks exactly like
    the mark drawn without.
    """
    eyes = "".join(
        f'<g class="eye {side}"><g class="lid">'
        f'<circle class="iris" cx="{x}" cy="52" r="11"/>'
        f'<circle class="pupil" cx="{x}" cy="52" r="5"/>'
        f'<path class="joy" d="M{x - 6} 54 a6.5 6.5 0 0 1 12 0"/>'
        "</g></g>"
        for side, x in (("eL", 36), ("eR", 60))
    )
    under, over, out = (_WARDROBE_UNDER, _WARDROBE_OVER, _WARDROBE_OUT) if wardrobe else ("", "", "")
    return (
        f'<svg class="probe-mark" width="{size}" height="{size}" '
        'viewBox="0 0 96 96" aria-hidden="true" focusable="false">'
        '<ellipse class="shadow" cx="48" cy="90" rx="20" ry="4"/>'
        '<g class="rig">'
        f"{_SPROUT}"
        '<rect class="hull" x="17" y="27" width="62" height="54" rx="19"/>'
        f"{under}{eyes}{over}"
        f"</g>{out}</svg>"
    )


def mast(*, eyebrow: str, title: str, count: str = "") -> str:
    """The band every list page opens on.

    One frame for the four destinations the nav names, because they are one
    level of the site and a band that changed shape between them would say
    otherwise. Two things and no third: what this surface is, and what it does.
    Nothing sits beside the title — the list under the band is what the page
    is for, and anything set there either repeats that list or argues for it,
    when the list makes its own case one scroll down.

    `count` is the exception the analysis list earns — the pair it prints beside its
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


# A rewrite's four acts, as the page names them: a short noun the act strip,
# the contents and the 요약 cards can hold at a phone's width, and the question
# under it in grey. The acts are fixed by `analysis/AUTHORING.md` R1, so their
# names are the page's, keyed by act number.
ACT_NAMES = {"1": ("문제", "무엇이 막혔나"), "2": ("방법", "무엇을 바꿨나"),
             "3": ("검증", "정말 되는가"), "4": ("시사점", "연구 축에 걸리는 것")}

# A comparison's acts, by the same rule: a short noun beside the question the
# act's own heading asks, so the two kinds of page read with one set of
# landmarks. Its question is the author's heading, not fixed here — the
# comparison contract names the four, and a heading reworded for two papers
# rather than three still prints as written. Act 0 is the background cards,
# which the page prints before act 1 when the comparison names any.
CMP_ACT_NAMES = {"0": "배경", "1": "질문", "2": "공통", "3": "갈림", "4": "시사점"}
CMP_BACKGROUND_Q = "먼저 알아 둘 것"


def card_head(noun: str, sub: str = "") -> str:
    """A 요약 card's head: its short noun, underlined, and a grey line."""
    return (f'<div class="g-head"><b>{esc(noun)}</b>'
            + (f'<span>{esc(sub)}</span>' if sub else "") + "</div>")


def chip(label: str, cls: str = "", *, data: dict | None = None) -> str:
    attrs = "".join(f' data-{k}="{esc(v)}"' for k, v in (data or {}).items())
    classes = f"chip {cls}".strip()
    return f'<span class="{classes}"{attrs}>{esc(label)}</span>'


def pillar_chips(pillars: list[str]) -> str:
    return "".join(chip(p, "pillar", data={"p": p}) for p in pillars)


# A compared paper's mark: its place in `compares:` drawn as a shape first and
# a hue second, so ● ▲ ■ still tell two or three papers apart for a reader who
# cannot tell the hues apart. One comparison page uses one set everywhere a
# paper appears — its card, its branch of the fork, its matrix column — so the
# eye follows a paper by its mark rather than by counting positions.
_PAPER_MARKS = ('<circle cx="6" cy="6" r="5"/>',
                '<path d="M6 .9 11.4 10.7H.6Z"/>',
                '<rect x="1.3" y="1.3" width="9.4" height="9.4" rx="1.2"/>')


def paper_mark(i: int, size: int = 11) -> str:
    """The mark of the `i`-th compared paper (0-based)."""
    return (f'<svg class="pmark pm-{i + 1}" viewBox="0 0 12 12" width="{size}" '
            f'height="{size}" fill="currentColor" aria-hidden="true" '
            f'focusable="false">{_PAPER_MARKS[i]}</svg>')


def mark_button() -> str:
    """책갈피 for the section on screen, without going back to the contents.

    The contents are the exact surface — a flag per section — but they sit at
    the top of the article and a reader who stops reading is at the bottom of
    it. This marks where they are, which is what a 책갈피 means, and it is the
    same one-per-paper toggle: pressing it on a section already marked takes
    the mark off.

    One of the reader's controls at the tab strip's right end. Ships
    `hidden`; it belongs to 상세 — 요약 is one screen and has no sections to
    stand in — so `shelf.js` shows it only while that surface is open, and the
    stylesheet keeps its slot meanwhile.
    """
    return (
        '<button type="button" class="act-btn" data-mark-fab hidden aria-pressed="false" '
        'aria-label="여기에 책갈피" title="여기에 책갈피">'
        '<svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true" '
        f'focusable="false"><path d="{_FLAG_D}"/></svg>'
        "</button>"
    )


def memo_button() -> str:
    """The control that opens the memo panel, beside 책갈피 in the reader's
    group; `memo.js` lights it and counts the draft."""
    return (
        '<button type="button" class="act-btn" data-memo-fab data-has-memo="0" '
        f'aria-label="메모 열기" title="메모">{icon("pencil", 16)}<span class="count"></span></button>'
    )


def memo_panel(paper_id: str, title: str, paper_url: str, discussions_new: str) -> str:
    return f"""
<div class="scrim" data-scrim data-open="0"></div>
<aside class="memo" data-memo-root data-open="0" inert
       data-paper-id="{esc(paper_id)}"
       data-paper-title="{esc(title)}"
       data-paper-url="{esc(paper_url)}"
       data-discussions-new="{esc(discussions_new)}"
       aria-label="이 논문의 메모">
  <div class="memo-head">
    <h3>메모</h3>
    <span class="memo-status" data-memo-status aria-live="polite"></span>
    <button type="button" class="memo-x" data-memo-close aria-label="메모 닫기" title="닫기">{icon("close", 16)}</button>
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


def share_meta(title: str, description: str) -> str:
    """What a chat or a feed shows when a page's link is pasted into it.

    Slack, KakaoTalk, Discord and a mail client read Open Graph, not the
    `<title>`, and without it a paper's link unfurls as a bare URL. The image
    is one card for the whole site — the mark and the name — because a
    preview's job is to say which site the link is from; the title and the
    description beside it say which page.
    """
    tags = [
        '<meta property="og:site_name" content="PROBE">',
        '<meta property="og:type" content="website">',
        '<meta property="og:locale" content="ko_KR">',
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:image" content="{SITE}assets/og.png">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta name="twitter:card" content="summary_large_image">',
    ]
    if description:
        tags.insert(4, f'<meta property="og:description" content="{esc(description)}">')
    return "\n".join(tags)


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
    as the reader's place. Every page passes one but the first screen and
    `404.html`, which stand under no destination.

    `base` overrides that with an absolute prefix. Exactly one page needs it:
    Pages serves `404.html` at whatever depth the bad URL had, so a relative
    `assets/site.css` resolves against `/probe/p/typo/` and the error page
    arrives unstyled with dead links.
    """
    up = base or "../" * depth
    # The skip link's target. Every page body opens one `<main>`, so the shell
    # names it here rather than each page builder remembering to.
    body = body.replace("<main ", '<main id="main" ', 1)
    # Classic scripts, not ES modules: `type="module"` is blocked by CORS on
    # `file://`, and opening a built page directly is the fastest way to check
    # a render. Shared state goes on `window.ProbeMemo` instead of exports.
    #
    # The unconditional ones are the ones every page carries: theme.js drives
    # the nav card's 화면 and 색 테마 rows, nav.js
    # the pill and the card it grows into, and the ⌘K palette is
    # reachable from anywhere — so its index, its matching rule and the script
    # itself ride along too, and so does `pillar.js`, since an axis chip on any
    # page opens its axis's popup. `defer` runs them in this order, which is
    # what lets `filter.js` further down the list read `match.js`.
    script_tags = "".join(
        f'<script src="{asset(f"{up}assets/{s}")}" defer></script>'
        for s in ["theme.js", "nav.js", "corpus-index.js",
                  "match.js", "palette.js", "pillar.js", *(scripts or [])]
    )
    return f"""<!DOCTYPE html>
<html lang="ko" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
{f'<meta name="description" content="{esc(description)}">' if description else ""}
{share_meta(title, description)}
{icon_links(up)}
<link rel="stylesheet" href="{asset(f"{up}assets/fonts.css")}">
<link rel="stylesheet" href="{asset(f"{up}assets/katex/katex.min.css")}">
<link rel="stylesheet" href="{asset(f"{up}assets/site.css")}">
{extra_head}
<script>
/* Runs before first paint. Three jobs: set the reader's ground, accent and
   contrast (otherwise a dark-mode reader gets a white flash on every
   navigation) — a stored 종이 or 딤 is a light or dark theme plus its ground —, mark
   the document as scripted, so JS-only controls can hide themselves in CSS instead of
   appearing and then vanishing once a deferred script loads, and mark a
   session that has already seen the first screen open, so it opens still. */
(function(){{document.documentElement.classList.add('js');
try{{if(sessionStorage.getItem('probe.home.entered'))document.documentElement.classList.add('hm-entered');}}catch(e){{}}
try{{var r=document.documentElement,t=localStorage.getItem('probe.theme');
if(!t)t=matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
r.setAttribute('data-theme',t==='dark'||t==='dim'?'dark':'light');
if(t==='paper'||t==='dim')r.setAttribute('data-ground',t);
if(localStorage.getItem('probe.contrast')==='high')r.setAttribute('data-contrast','high');
var a=localStorage.getItem('probe.accent');if(a)r.setAttribute('data-accent',a);}}catch(e){{}}}})();
</script>
</head>
<body{" " + body_attrs if body_attrs else ""}>
<a class="skip" href="#main">본문으로 건너뛰기</a>
{nav(up, here)}
{body}
{script_tags}
</body>
</html>
"""


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


def _github(size: int) -> str:
    return (f'<svg viewBox="0 0 16 16" width="{size}" height="{size}" aria-hidden="true" '
            f'focusable="false"><path fill="currentColor" d="{GITHUB_MARK}"/></svg>')


def repo_link() -> str:
    """The way out to the repository, for a browser that runs no script.

    The site publishes one half of this project — the rewrites and the
    comparisons — and the other half is the part that produced them: the
    prompts, the human's `context/`, the format contracts, this generator. A
    scripted page carries the link as the last line of the nav's settings
    card (`nav_island()`); an unscripted page has no card, so the link stands
    in the row on its own, drawn as an outlined glyph and named in `title`
    and `aria-label`. `site.css` keeps it off a scripted page.
    """
    return (
        f'<a class="icon-btn nav-repo" href="{REPO_URL}" '
        'target="_blank" rel="noopener noreferrer" '
        f'aria-label="GitHub (새 탭)" title="GitHub">{_github(16)}</a>'
    )


# Every place the site goes, in the order the nav offers them. The row and the
# phone's card print the same list rather than each keeping their own, so a
# destination cannot arrive in one and be missing from the other.
#
# A track's destination is named for its track, in two syllables of Korean —
# 탐색 Scouting, 분석 Analysis, 비교 Comparison — the pipeline's own order:
# what arrived, then what was rewritten, then what was set side by side.
# Four labels of one width read as one row on a desktop and
# fit beside the controls without crowding them. 서재 is the reader's own shelf
# rather than a track, and stands after them.
#
# The key in front is what a page names itself with. A paper and a comparison
# each sit *under* a destination rather than being one, so `p/<id>/` marks
# 분석 and `c/<slug>/` marks 비교 — the mark answers "which part of the site
# is this", which is what a reader glancing at a nav is asking.
DESTINATIONS = (("scout", "s/index.html", "탐색"),
                ("papers", "p/index.html", "분석"),
                ("compare", "c/index.html", "비교"),
                ("shelf", "shelf/index.html", "서재"))


def _badge(key: str) -> str:
    """The count of starred papers on 서재 — printed empty and hidden, filled
    by `nav.js` from this browser's shelf and shown only when it is not
    zero."""
    return ('<span class="nav-badge" data-star-count hidden></span>'
            if key == "shelf" else "")


def _current(key: str, here: str) -> str:
    """`aria-current` on the destination the reader is standing in.

    One attribute carries the whole mark: `site.css` draws the rule under it
    from `[aria-current="page"]`, and a screen reader is told which of the
    three it is without a second, visual-only class to keep in step. `here`
    may be empty — 404 stands under no destination and marks none.
    """
    return ' aria-current="page"' if key and key == here else ""


# The accents a reader can pick, in the card's order: the name, and the key
# `site.css` reads off `data-accent` (인디고 is the default and has none).
# A swatch is drawn by `site.css` from the same key, so an accent's hue and
# chroma are written once, there. The card lays them two to a row, so the
# count stays even.
ACCENTS = (("인디고", ""),
           ("세이지", "sage"),
           ("테라코타", "terracotta"),
           ("잉크", "ink"))
# The grounds a reader can read on: two light, two dark. `theme.js` stores the
# key under `probe.theme`, and the head's boot script turns it into
# `data-theme` (light or dark) plus `data-ground` for 종이 and 딤.
GROUNDS = (("라이트", "light"),
           ("종이", "paper"),
           ("다크", "dark"),
           ("딤", "dim"))


def _seg(label: str, title: str, items: str, grid: bool = False) -> str:
    """One row of the card that picks one of several: a track, the items,
    and the indicator `nav.js` slides under whichever item is marked. `grid`
    wraps the items two to a line, for a pick with more than fit in one."""
    tip = f' title="{title}"' if title else ""
    cls = "isl-seg isl-grid" if grid else "isl-seg"
    return (f'<div class="{cls}" role="radiogroup" aria-label="{label}"{tip}>'
            f'<span class="isl-blob" aria-hidden="true"></span>{items}</div>')


def nav_island(up: str, here: str = "") -> str:
    """The nav's right end on a scripted page: one pill, and the card it opens.

    The pill holds two things. The magnifier opens the ⌘K palette
    (`palette.js` answers any `[data-cmdk-open]`), with the shortcut printed
    beside it on a viewport wide enough to have a keyboard; `palette.js`
    rewrites it to `⌘K` on a Mac. The second button opens the card — the
    sliders glyph on a desktop, ☰ on a phone, because on a phone the card also
    carries the destinations the row hands over.

    The card is the pill grown in place rather than a box dropped under it, so
    the thing that opened is visibly the thing that was pressed. `nav.js`
    animates the grow and the indicator in each row; `theme.js` owns what the
    바탕 and 강조 rows and the 고대비 switch set. Every control in it is
    printed here, so the script only moves what already exists.

    None of it works without a script, so `site.css` keeps the whole pill off
    an unscripted page, which falls back to the row of links and
    `repo_link()`.
    """
    go = "".join(
        f'<a class="isl-i" href="{up}{href}"{_current(key, here)}>'
        f'{label}{_badge(key)}</a>'
        for key, href, label in DESTINATIONS)
    grounds = "".join(
        f'<button type="button" class="isl-i isl-tile" role="radio" data-theme-set="{key}" '
        f'aria-checked="false"><i class="isl-pv" data-pv="{key}" aria-hidden="true">'
        f'<b></b><b></b><b></b></i><span>{name}</span></button>'
        for name, key in GROUNDS)
    accents = "".join(
        f'<button type="button" class="isl-i" role="radio" data-accent-pick="{key}" '
        f'aria-checked="false"><i class="isl-sw" data-sw="{key}"></i>{name}</button>'
        for name, key in ACCENTS)
    return f"""<div class="isl" data-isl>
    <div class="isl-shell">
      <div class="isl-face isl-rest is-on" data-isl-face="rest">
        <button type="button" class="isl-q" data-cmdk-open aria-label="논문 찾기 (Ctrl K)"
                title="논문 찾기 (Ctrl K)">{icon("search", 14)}<kbd data-cmdk-key>Ctrl K</kbd></button>
        <span class="isl-sep" aria-hidden="true"></span>
        <button type="button" class="isl-b" data-isl-open aria-expanded="false" aria-controls="isl-card"
                aria-label="설정" title="설정">{icon("sliders", 15)}{icon("menu", 15)}</button>
      </div>
      <div class="isl-face isl-card" id="isl-card" data-isl-face="card" role="dialog"
           aria-label="설정" tabindex="-1" inert>
        <div class="isl-top"><span>설정</span>
          <button type="button" class="isl-x" data-isl-close aria-label="닫기">{icon("close", 14)}</button></div>
        <nav class="isl-sec isl-go" aria-label="이동"><span class="isl-h">이동</span>
          <div class="isl-seg">{'<span class="isl-blob" aria-hidden="true"></span>'}{go}</div></nav>
        <div class="isl-sec"><span class="isl-h">바탕</span>{_seg("바탕", "라이트·다크 전환 (Ctrl+Shift+L)", grounds, grid=True)}</div>
        <div class="isl-sec"><span class="isl-h">강조</span>{_seg("강조", "", accents, grid=True)}</div>
        <button type="button" class="isl-switch" role="switch" aria-checked="false" data-contrast-toggle>고대비<i class="isl-track" aria-hidden="true"></i></button>
        <a class="isl-out" href="{REPO_URL}" target="_blank" rel="noopener noreferrer">{_github(15)}GitHub 저장소<span class="isl-arr" aria-hidden="true">↗</span></a>
      </div>
    </div>
  </div>"""


def nav(up: str, here: str = "") -> str:
    """The row every page opens on — where the site goes, and what it can do.

    Two clusters, and they are different kinds: four places to go, then the
    pill that acts on the page in front of the reader (`nav_island()`). A
    hairline stands between them (`site.css`), because a row of unboxed
    labels running straight into a filled pill reads as one control that
    lost its edge unless something says the boundary is meant.

    `here` is the destination this page sits under, and marking it is the
    other half of the same job: a row of four names that never says which one
    the reader is standing in is a row with a hole in it, and the hole is what
    makes the labels beside the controls look unfinished.
    """
    links = "".join(
        f'<li><a href="{up}{href}"{_current(key, here)}>{label}{_badge(key)}</a></li>'
        for key, href, label in DESTINATIONS)
    return f"""<nav class="site-nav">
  <div class="nav-inner">
    <a class="nav-logo" href="{up}index.html"><span class="nav-word">PROBE</span></a>
    <span class="nav-spacer"></span>
    <ul class="nav-links">{links}</ul>
    <span class="nav-rule"></span>
    {repo_link()}
    {nav_island(up, here)}
  </div>
</nav>"""

