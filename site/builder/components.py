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
# The star is the one glyph drawn outside the icon set as well — 서재's
# masthead fills it rather than stroking it — so the outline is a constant and
# both callers take the same points.
_STAR_D = ("m8 1.9 1.85 3.75 4.15.6-3 2.93.71 4.13L8 11.4l-3.71 "
           "1.91.71-4.13-3-2.93 4.15-.6Z")
# 책갈피, the same way: `mark_fab()` presses it, 서재's masthead drops it
# into the window. `assets/shelf.js` and `assets/hub.js` carry the same points
# for the rows they build at runtime, so a move here is a move there.
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


# One box for all three masthead diagrams. The art column is the same width on
# every band, so a second aspect ratio is a second band height — and "one frame
# for the three destinations" stops being true the moment one of them is taller.
# The foot stops just under the drawing: the band's own padding is the margin,
# and a taller box would push the page down with empty space.
_ART_BOX = "0 0 560 164"

# The landing diagram's geometry, in the box's units. The four pieces are the
# only numbers that have to agree with anything: each one departs a line of an
# original and lands on the part of the list it becomes, and `index.css` moves
# them between exactly these coordinates.
_ART_PIECES = ((62, 62), (62, 80), (62, 98), (62, 116))
_ART_ROWS = ((40, 42), (40, 44), (40, 38), (40, 36),
             (40, 42), (36, 44), (32, 40), (40, 28))
# One row of the list per piece after the lead — where it sits, and how far its
# title runs. Unequal on purpose: a column of equal bars is a table, and the
# thing being drawn is a list of different papers.
_ART_LIST = ((100, 168), (122, 210), (144, 140))


def mast_art() -> str:
    """The landing masthead's diagram — what this page holds, drawn.

    A scan crosses originals that stay shut and lifts four pieces out of them;
    the four wait in a rack over the mark; then they land, one at a time and
    top to bottom, as the list this page is: the newest rewrite printed in
    full, and every other one as a line.

    The picture carries the title's two verbs. 옮김 is the lead block, where a
    line of an original comes back as a line someone can read. 둠 is the rows
    under it, where the rest of the corpus is filed rather than piled. Nothing
    appears on the right that a piece did not carry there, which is what makes
    the drawing an argument rather than an ornament.

    It draws **this** page and no other. The paper page's tabs, the fork a
    comparison opens, the shelf a browser keeps — each belongs to the band of
    the page that holds it, and a band drawing a different page's surface goes
    stale every time that page gains one. That is why the tabs are not here:
    there are four of them now and there will be more.

    No pillar chip either. A chip only reads as an axis in that axis's colour,
    and painting one here would put the pillar set in a fourth place
    (`site/CLAUDE.md`). The rail directly under the band names the axes, in a
    place that already knows them.

    `mark()` is nested rather than redrawn, so the face here is the same
    drawing as the one in the nav — same tokens, same blink, same pupils under
    `brand.js`. Geometry only: every beat is a keyframe in `index.css`.

    Nothing on the page states any of this in words, and the figure does not
    either: it sets the band rather than carrying a claim, so it stays out of
    the accessibility tree. Naming it there would hand a reader on a screen
    reader a sentence no sighted reader is given.
    """
    rows = "".join(
        f'<rect x="16" y="{y}" width="{w1}" height="3" rx="1.5"/>'
        f'<rect x="62" y="{y}" width="{w2}" height="3" rx="1.5"/>'
        for y, (w1, w2) in zip(range(56, 128, 9), _ART_ROWS)
    )
    pieces = "".join(
        f'<circle class="ma-dot ma-d{i + 1}" cx="{x}" cy="{y}" r="3.4"/>'
        for i, (x, y) in enumerate(_ART_PIECES)
    )
    # A row carries what a row on this page carries: the star it is kept with,
    # its arXiv id, its title, and how long a sit it is.
    listrows = "".join(
        f'<g class="ma-row ma-r{i + 1}">'
        f'<g transform="translate(206,{y - 6}) scale(.75)">'
        f'<path class="ma-star" d="{_STAR_D}"/></g>'
        f'<rect class="ma-id" x="226" y="{y - 2}" width="34" height="4" rx="2"/>'
        f'<rect class="ma-title" x="270" y="{y - 2.5}" width="{w}" height="5" rx="2.5"/>'
        f'<rect class="ma-id" x="506" y="{y - 2}" width="48" height="4" rx="2"/>'
        f'<path class="ma-sep" d="M206 {y + 11} H554"/>'
        "</g>"
        for i, (y, w) in enumerate(_ART_LIST)
    )
    return (
        f'<svg class="mast-art home-art" viewBox="{_ART_BOX}" aria-hidden="true" '
        'focusable="false">'
        "<defs>"
        '<linearGradient id="ma-scan" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" class="ma-scan-0"/><stop offset="1" class="ma-scan-1"/>'
        "</linearGradient>"
        '<clipPath id="ma-clip">'
        '<rect x="6" y="26" width="112" height="126" rx="8"/></clipPath>'
        "</defs>"

        # The corpus as it arrives — stacked, and none of it opened. The scan
        # crosses only the sheet on top, because one is enough to say what is
        # happening to all of them.
        '<text class="ma-label" x="6" y="17">arXiv 원문</text>'
        '<rect class="ma-sheet ma-stack" x="18" y="34" width="112" height="126" rx="8"/>'
        '<rect class="ma-sheet ma-stack" x="12" y="30" width="112" height="126" rx="8"/>'
        '<rect class="ma-sheet" x="6" y="26" width="112" height="126" rx="8"/>'
        '<rect class="ma-head" x="16" y="40" width="56" height="6" rx="3"/>'
        f'<g class="ma-type">{rows}</g>'
        '<rect class="ma-veil" x="6" y="26" width="112" height="126" rx="8"/>'
        '<g clip-path="url(#ma-clip)"><g class="ma-band">'
        '<rect x="6" y="26" width="112" height="26" fill="url(#ma-scan)"/>'
        '<rect class="ma-edge" x="6" y="51" width="112" height="1.3"/>'
        "</g></g>"
        '<rect class="ma-pill" x="16" y="128" width="54" height="15" rx="7.5"/>'
        '<text class="ma-pill-t" x="43" y="138.5">열지 않음</text>'

        # What this page holds. The newest rewrite is a card because it is one
        # here; the rest are lines because they are lines here. The card's own
        # sheet stands for the whole loop — it is the surface the list is
        # written on, the way the original's sheet is the surface it is read
        # from, and only what gets written into it arrives.
        '<text class="ma-label" x="206" y="17">PROBE 재작성 · 한글</text>'
        '<rect class="ma-sheet" x="206" y="26" width="348" height="58" rx="8"/>'
        '<g class="ma-lead">'
        '<rect class="ma-flag" x="220" y="38" width="36" height="4" rx="2"/>'
        '<rect class="ma-lead-t" x="220" y="54" width="210" height="7" rx="3.5"/>'
        '<rect class="ma-lead-s" x="220" y="68" width="266" height="4" rx="2"/></g>'
        f"{listrows}"

        # The pieces sit under the mark, so one in transit passes behind the
        # face and lands in front of the line it becomes.
        '<g class="ma-rack"><rect x="144" y="55" width="56" height="1.2" rx=".6"/></g>'
        f"{pieces}"
        f'<g transform="translate(148,64)">{mark(44)}</g>'
        "</svg>"
    )



# ── The two list mastheads that are not the landing ─────────────────────────
# What each drawing argues, in words. A drawing that carries a claim rather
# than setting the band is named in the accessibility tree instead of hidden
# from it, and this is the name: the art writes it into its own `aria-label`.
CMP_LEAD = (
    "논문 두세 편을 한 질문 아래 놓고 갈리는 자리만 봅니다. "
    "각 논문이 무엇을 하는지는 그 논문의 재작성본에 있습니다."
)
TALK_LEAD = (
    "논문 한 편을 起承轉結 네 막의 슬라이드로 다시 짭니다. "
    "슬라이드마다 그 앞에서 무엇을 말할지가 아래에 붙고, "
    "재작성본이 있는 논문만 여기에 섭니다."
)
SHELF_LEAD = (
    "즐겨찾기 · 읽은 논문 · 책갈피 · 메모. "
    "넷 다 이 브라우저에만 남고, 사이트 데이터를 지우면 사라집니다. "
    "옮기거나 남길 것은 내보내세요."
)


# One branch per row, and the stance each one runs out to. Three is the most a
# comparison may hold (`comparison/AUTHORING.md`), so three is what the picture
# draws.
_CMP_ROWS = (82, 112, 142)
_CMP_STANCE = (196, 244, 160)


def cmp_art() -> str:
    """The comparison masthead's diagram — `CMP_LEAD`, drawn.

    The claim is the track's own premise: two or three papers are put under one
    question, and what is worth printing is only the place they part. So the
    question is a card over everything, the papers arrive as the aliases they
    are listed under, and the bracket opens beneath it — the same trunk, spine
    and tick `pages._fork_bracket()` draws on every comparison card, at the
    size a masthead can carry. What each paper *is* never appears: a branch
    ends in an arrow leaving the frame, because that detail lives on the
    paper's own page and the comparison links out to it.

    `공통` is the trunk and takes the muted ink; the three stances take
    `--act1..3`, so what the picture colours is exactly what the track exists
    to show. Unlike the landing's diagram this one carries the page's sentence
    rather than setting its band, so it is named in the accessibility tree
    instead of hidden from it.
    """
    branches = "".join(
        f'<g class="ca-b ca-b{i + 1}">'
        f'<rect class="ca-pill" x="162" y="{y - 11}" width="56" height="22" rx="11"/>'
        f'<rect class="ca-stance" x="238" y="{y - 3}" width="{w}" height="6" rx="3"/>'
        f'<path class="ca-out" d="M524 {y - 5} l6 5 -6 5"/>'
        "</g>"
        for i, (y, w) in enumerate(zip(_CMP_ROWS, _CMP_STANCE))
    )
    ticks = "".join(
        f'<path class="ca-tick ca-t{i + 1}" d="M132 {y} H152"/>'
        for i, y in enumerate(_CMP_ROWS)
    )
    return (
        f'<svg class="mast-art cmp-art" viewBox="{_ART_BOX}" role="img" '
        f'aria-label="{esc(CMP_LEAD)}" focusable="false">'
        # One group over the whole drawing, so the loop can dissolve and
        # rebuild without any single piece being caught snapping back.
        '<g class="ca-all">'

        # The question, over everything it holds.
        '<text class="ca-label" x="6" y="17">한 질문</text>'
        '<rect class="ca-sheet" x="6" y="26" width="548" height="34" rx="8"/>'
        '<rect class="ca-q" x="20" y="39" width="300" height="7" rx="3.5"/>'

        # The trunk: what they all accept, and the stub that carries it in.
        '<text class="ca-label ca-trunk-l" x="6" y="104">공통</text>'
        '<rect class="ca-trunk" x="6" y="109" width="98" height="6" rx="3"/>'
        '<path class="ca-stub" d="M110 112 H132"/>'

        # The fork itself — spine first, then a tick per branch.
        '<path class="ca-spine" d="M132 82 V142"/>'
        f"{ticks}{branches}"
        # The one place the three branches stop agreeing. Everything left
        # of it is the question and the 공통; everything right of it is
        # what the comparison was written to print. The title over the
        # drawing names it, so the rule does not label itself.
        '<path class="ca-cut" d="M232 66 V158"/>'
        "</g></svg>"
    )


# The four beats a talk is cut into, and the slide the drawing gives each —
# how wide its content runs, and how much there is to say under it. The acts
# are `presentations.ACTS`; the numbers only say that four unequal slides are
# four different slides.
_TALK_SLIDES = ((78, 100), (96, 74), (62, 108), (88, 86))


def talk_art() -> str:
    """The talk masthead's diagram — `TALK_LEAD`, drawn.

    One talk, in the shape the track's contract gives it: the spine over
    everything — the one sentence a talk is allowed — then a slide per act,
    ranked 起承轉結 in `--act1..4`, and under each one the speaker essay. The
    two rows are the whole argument: a slide is what the room sees and the
    essay is what is said in front of it, and neither is the other. A deck
    with no second row is a slide dump, which is the thing
    `presentation/AUTHORING.md` §6 exists to refuse.

    Four is the act count, not a slide count. A talk carries as many slides as
    it needs and the acts are what order them, so the drawing shows the beats
    rather than pretending to count frames.

    `--act1..4` mean the four acts everywhere else on this site, and here they
    mean the same four. Unlike the landing's list, this drawing has acts.
    """
    slides = "".join(
        f'<g class="pa-s pa-a{i + 1}">'
        f'<text class="pa-act" x="{x + 2}" y="52">{act}</text>'
        f'<rect class="pa-slide" x="{x}" y="58" width="117" height="62" rx="6"/>'
        f'<rect class="pa-bar" x="{x}" y="58" width="117" height="3.5" rx="1.75"/>'
        f'<g class="pa-body">'
        f'<rect x="{x + 10}" y="76" width="{w}" height="4" rx="2"/>'
        f'<rect x="{x + 10}" y="90" width="{w - 16}" height="4" rx="2"/>'
        f'<rect x="{x + 10}" y="104" width="{w - 34}" height="4" rx="2"/></g>'
        f'<g class="pa-say">'
        f'<rect x="{x + 2}" y="132" width="{e}" height="3.5" rx="1.75"/>'
        f'<rect x="{x + 2}" y="142" width="{e - 28}" height="3.5" rx="1.75"/></g>'
        "</g>"
        for i, (x, act, (w, e)) in enumerate(
            zip((54, 181, 308, 435), "起承轉結", _TALK_SLIDES))
    )
    return (
        f'<svg class="mast-art talk-art" viewBox="{_ART_BOX}" role="img" '
        f'aria-label="{esc(TALK_LEAD)}" focusable="false">'
        '<g class="pa-all">'

        # What the three rows are, named once on the left so the drawing does
        # not have to be guessed at.
        '<text class="pa-label" x="6" y="32">한 문장</text>'
        '<rect class="pa-spine" x="54" y="26" width="320" height="7" rx="3.5"/>'
        '<text class="pa-label" x="6" y="92">슬라이드</text>'
        '<text class="pa-label" x="6" y="142">말할 것</text>'
        f"{slides}"
        "</g></svg>"
    )


# The four lists 서재 holds, in `pages.SHELF_TABS` order, and how far each
# one's row runs. The widths differ only so the rows do not read as a table:
# no number here is a count, because the build has none to give.
_SHELF_ROWS = ((74, 196), (98, 150), (122, 232), (146, 168))


def shelf_art() -> str:
    """The shelf masthead's diagram — `SHELF_LEAD`, drawn.

    Four kinds of mark fall into one browser window and stay there. The window
    frame is the whole argument: it is a boundary, it lights once to say so,
    and the only thing that crosses it is the export arrow. A reader who has
    understood the picture has understood why the page has two export buttons
    and no account.

    Nothing here is counted. Rows are drawn without numbers because the build
    cannot know what this browser holds — `site/CLAUDE.md`'s "reader state
    never reaches the build" is a rule about the drawing too, not only about
    the markup under it. The four glyphs are the site's own: the star every
    row is starred with, the check a 읽음 mark leaves, the flag 책갈피 plants,
    and a memo's card.
    """
    rows = "".join(
        f'<g class="sa-row sa-r{i + 1}">'
        f'<g class="sa-glyph" transform="translate(28,{y - 8})">{glyph}</g>'
        f'<rect class="sa-title" x="56" y="{y - 2.5}" width="{w}" height="5" rx="2.5"/>'
        "</g>"
        for i, ((y, w), glyph) in enumerate(zip(_SHELF_ROWS, (
            f'<path class="sa-star" d="{_STAR_D}"/>',
            '<path class="sa-check" d="M3.4 8.4 6.6 11.6 12.8 4.8"/>',
            f'<path class="sa-flag" d="{_FLAG_D}"/>',
            '<g class="sa-memo"><rect x="3" y="2.4" width="10" height="11.2" rx="1.6"/>'
            '<path d="M5.4 6.1h5.2M5.4 8.6h5.2M5.4 11.1h3"/></g>',
        )))
    )
    return (
        f'<svg class="mast-art shelf-art" viewBox="{_ART_BOX}" role="img" '
        f'aria-label="{esc(SHELF_LEAD)}" focusable="false">'
        '<g class="sa-all">'

        # The window, and the edge that says it is one.
        '<text class="sa-label" x="6" y="17">이 브라우저</text>'
        '<rect class="sa-win" x="6" y="26" width="380" height="132" rx="10"/>'
        '<path class="sa-rule" d="M6 54 H386"/>'
        '<circle class="sa-dot" cx="26" cy="40" r="3.5"/>'
        '<circle class="sa-dot" cx="40" cy="40" r="3.5"/>'
        '<circle class="sa-dot" cx="54" cy="40" r="3.5"/>'
        f"{rows}"
        '<rect class="sa-edge" x="6" y="26" width="380" height="132" rx="10"/>'

        # The one door out.
        '<text class="sa-label sa-out-l" x="502" y="54">내보내기</text>'
        '<g class="sa-arrow"><path d="M398 92 H432"/><path d="M426 86 l6 6 -6 6"/></g>'
        '<g class="sa-file">'
        '<rect class="sa-card" x="450" y="64" width="104" height="56" rx="7"/>'
        '<rect class="sa-line" x="466" y="80" width="64" height="5" rx="2.5"/>'
        '<rect class="sa-line" x="466" y="94" width="50" height="5" rx="2.5"/>'
        '<rect class="sa-line" x="466" y="108" width="58" height="5" rx="2.5"/></g>'
        "</g></svg>"
    )


def mast(*, eyebrow: str, title: str, art: str, count: str = "") -> str:
    """The band every list page opens on.

    One frame for the three destinations the nav names, because they are one
    level of the site and a band that changed shape between them would say
    otherwise. What differs is the drawing beside the title, and it has to:
    each art is its own page's claim, and the landing's — an original becoming
    two tabs — argues nothing on a page about comparisons.

    Three things and no fourth: what this surface is, what it does, and the
    drawing that argues it. `count` is the exception the landing earns — the
    pair it prints beside its title for a reader whose filter bar has not
    arrived — and it is the only number any band carries, because it is the
    only one the build has. What this browser has kept is not a fact this
    generator holds.
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
    {art}
  </div>
</header>"""


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
        'aria-label="GitHub 저장소 (새 탭)" title="GitHub 저장소">'
        '<svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true" '
        f'focusable="false"><path fill="currentColor" d="{GITHUB_MARK}"/>'
        '</svg></a>'
    )


# Every place the site goes, in the order the nav offers them. The row and the
# phone's sheet print the same list rather than each keeping their own, so a
# destination cannot arrive in one and be missing from the other.
#
# The key in front is what a page names itself with. A paper and a comparison
# each sit *under* a destination rather than being one, so `p/<id>/` marks 논문
# and `c/<slug>/` marks 비교 — the mark answers "which part of the site is
# this", which is what a reader glancing at a nav is asking.
#
# 발표 is the one destination that is an index and nothing else: a presentation is a
# tab on its paper's page, so the row it lists links back into 논문, and a paper
# page opened at that tab still marks 논문 — which is the part of the site it
# is standing in.
DESTINATIONS = (("papers", "index.html", "논문"),
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

    A phone is not wide enough for the mark, the site's name, three
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
            'rel="noopener noreferrer">GitHub 저장소 ↗</a></div>')


def nav(up: str, here: str = "") -> str:
    """The row every page opens on — where the site goes, and what it can do.

    Two clusters, and they are different kinds: three places to go, then three
    things to do to the page in front of the reader. A hairline stands between
    them (`site.css`), because the seam between an unboxed label and a bordered
    32px button reads as a control that lost its border unless something says
    the boundary is meant.

    `here` is the destination this page sits under, and marking it is the
    other half of the same job: a row of three names that never says which one
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

