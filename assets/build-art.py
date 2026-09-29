#!/usr/bin/env python3
"""Bake the generated README images — each a light/dark pair.

    hero.svg            the front door: the flood, then the reader, and the
                        link to the reading site
    own.svg             How it works: who writes what
    probe-ideation.svg  the ideation mark, sized like the four track icons

    python3 assets/build-art.py            # write every pair
    python3 assets/build-art.py --check    # fail if any file is out of date

The other images in this folder are hand-authored. These carry timed cycles
whose keyframes are computed from the geometry — a card is marked when it
crosses a line, so moving the line moves the keyframe — which is why they are
generated: edit this script, never the SVG. What the images have to keep
saying is `assets/CLAUDE.md`.

Durations are literal, never `var()`: a custom property declared on `:root`
resolves only while the SVG is its own document, and an unresolved duration
drops the whole animation.
"""

from __future__ import annotations

import sys
from pathlib import Path
from string import Template

OUT = Path(__file__).resolve().parent

LIGHT = dict(
    CARD="#FFFCFA", BORDER="#E8CDBD", SOFT="#F2DFD3",
    ACCENT="#D97757", DEEP="#B06749", INK="#1F1611", MUTED="#7A6A60",
    HULL="#D97757", STALK="#CC785C", IRIS="#FFFAF7", PUPIL="#2A1A12",
    DIM="#C4B6AE", DIMSTALK="#B3A49B", DIMINK="#6B5A50", GHOST="#EFE4DC",
)
DARK = dict(
    CARD="#211C19", BORDER="#3D3129", SOFT="#332B26",
    ACCENT="#E8916F", DEEP="#C98A6D", INK="#F2EAE4", MUTED="#A08D80",
    HULL="#E8916F", STALK="#F0A183", IRIS="#FFF6F1", PUPIL="#2A1A12",
    DIM="#6E625B", DIMSTALK="#5E534C", DIMINK="#2A211C", GHOST="#2E2622",
)

# System stacks, not webfonts: a README image is rendered wherever GitHub is
# read, and every run is anchored with room to spare for a wider face.
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"
SANS = "system-ui, -apple-system, 'Segoe UI', 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif"

# The character's parts and motions, redrawn from `site/builder/components.py`'s
# `mark()`. Animated classes sit on groups with no transform attribute, since a
# CSS transform replaces one.
CHARACTER_CSS = """
    .hull   { fill: ${HULL}; }
    .iris   { fill: ${IRIS}; }
    .pupil  { fill: ${PUPIL}; }
    .stalk  { stroke: ${STALK}; stroke-width: 5; stroke-linecap: round; fill: none; }
    .beacon { fill: ${STALK}; }
    .page   { fill: ${IRIS}; stroke: ${DEEP}; stroke-width: 2; }
    .line   { fill: ${DEEP}; opacity: .3; }
    .shadow { fill: ${STALK}; opacity: .45; }
    .dim    { fill: ${DIM}; }
    .dimst  { stroke: ${DIMSTALK}; stroke-width: 5; stroke-linecap: round; fill: none; }
    .dimbe  { fill: ${DIMSTALK}; }
    .cross  { fill: none; stroke: ${DIMINK}; stroke-width: 3.2; stroke-linecap: round; }
    .mug    { fill: ${IRIS}; stroke: ${DEEP}; stroke-width: 2; stroke-linejoin: round; }
    .handle { fill: none; stroke: ${DEEP}; stroke-width: 2.4; stroke-linecap: round; }
    .brew   { fill: ${DEEP}; }
    .steam  { fill: none; stroke: ${STALK}; stroke-width: 2.2; stroke-linecap: round; opacity: 0; }
    .rig    { animation: bob 3.4s ease-in-out infinite; }
    .lid    { transform-box: fill-box; transform-origin: 50% 50%;
              animation: blink 7s ease-in-out infinite; }
    .readp  { animation: read 3.6s ease-in-out infinite; }
    .l1     { animation: lit 4.8s ease-in-out infinite; }
    .l2     { animation: lit 4.8s ease-in-out 1.6s infinite; }
    .l3     { animation: lit 4.8s ease-in-out 3.2s infinite; }
    .s1     { animation: steam 3.8s ease-in-out infinite; }
    .s2     { animation: steam 3.8s ease-in-out 1.9s infinite; }
    .breathe { animation: breathe 4.6s ease-in-out infinite; }
    .drift  { transform-box: fill-box; transform-origin: 50% 100%;
              animation: drift 4.6s ease-in-out infinite; }
    @keyframes bob   { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-3px); } }
    @keyframes blink { 0%, 44%, 50%, 100% { transform: scaleY(1); } 47% { transform: scaleY(.08); } }
    @keyframes read  { 0% { transform: translateX(-2.4px); } 72% { transform: translateX(2.4px); }
                       86%, 100% { transform: translateX(-2.4px); } }
    @keyframes lit   { 0%, 28% { opacity: .95; } 34%, 100% { opacity: .3; } }
    @keyframes steam { 0% { opacity: 0; transform: translateY(2px); } 30%, 55% { opacity: .7; }
                       100% { opacity: 0; transform: translateY(-6px); } }
    @keyframes drift { 0%, 100% { transform: rotate(-3deg); } 50% { transform: rotate(3deg); } }
    @keyframes breathe { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-1.6px); } }
"""

REDUCED = """
    @media (prefers-reduced-motion: reduce) {
      * { animation: none !important; }
    }
"""

PAGE = """<g transform="rotate(-5 48 75.5)">
        <rect class="page" x="25" y="67" width="46" height="17" rx="3"/>
        <rect class="line l1" x="31" y="70.6" width="34" height="2.2" rx="1.1"/>
        <rect class="line l2" x="31" y="74.4" width="34" height="2.2" rx="1.1"/>
        <rect class="line l3" x="31" y="78.2" width="22" height="2.2" rx="1.1"/>
      </g>"""

MUG = """<g><ellipse class="shadow" cx="91.5" cy="90" rx="9.4" ry="2.6"/>
      <path class="steam s1" d="M87.6 63 c-3 -3.2 3 -5.2 0 -8.6"/>
      <path class="steam s2" d="M95 62 c-3 -3.2 3 -5.2 0 -8.6"/>
      <path class="handle" d="M99.6 72.6 a5 5 0 0 1 0 9.6"/>
      <path class="mug" d="M83 68 h17 l-1.9 17.4 a3.2 3.2 0 0 1 -3.2 3.1 h-6.8 a3.2 3.2 0 0 1 -3.2 -3.1 Z"/>
      <ellipse class="brew" cx="91.5" cy="68" rx="8.5" ry="2.5"/></g>"""


def probe(x: float, y: float, s: float, mood: str = "read",
          page: bool = False, mug: bool = False) -> str:
    """The character in its 96-unit box, top-left at (x, y).

    read — pupils down on the page, following its lines
    up   — pupils up and to the right, at a thought
    """
    eyes = []
    for cx in (36, 60):
        if mood == "read":
            pupil = f'<g class="readp"><circle class="pupil" cx="{cx}" cy="56.5" r="5"/></g>'
        else:
            pupil = f'<circle class="pupil" cx="{cx + 2.5}" cy="48" r="5"/>'
        eyes.append(f'<g class="lid"><circle class="iris" cx="{cx}" cy="52" r="11"/>{pupil}</g>')
    return f"""<g transform="translate({x} {y}) scale({s})">
    <ellipse class="shadow" cx="48" cy="90" rx="20" ry="4"/><g class="rig">
      <path class="stalk" d="M48 26 V19"/><circle class="beacon" cx="48" cy="16" r="5"/>
      <rect class="hull" x="17" y="27" width="62" height="54" rx="19"/>
      {"".join(eyes)}
      {PAGE if page else ""}
    </g>{MUG if mug else ""}
  </g>"""


def lost_probe(x: float, y: float, s: float) -> tuple[str, str]:
    """The out-of-it probe — dimmed hull, drooping beacon, crossed
    eyes — with the two crosses pulsing half a beat apart. Returns (svg, css)."""
    eyes, css = [], []
    for k, cx in enumerate((36, 60)):
        eyes.append(f'<circle class="iris" cx="{cx}" cy="52" r="10.5"/>'
                    f'<g class="xk{k}"><path class="cross" d="M{cx-5.5} 46.5 L{cx+5.5} 57.5 '
                    f'M{cx+5.5} 46.5 L{cx-5.5} 57.5"/></g>')
        delay = " animation-delay: -.9s;" if k else ""
        css.append(f"    .xk{k} {{ transform-box: fill-box; transform-origin: 50% 50%; "
                   f"animation: xpulse 1.8s ease-in-out infinite;{delay} }}")
    css.append("    @keyframes xpulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(.74); } }")
    body = f"""<g transform="translate({x} {y}) scale({s})">
    <ellipse class="dimbe" opacity=".45" cx="48" cy="90" rx="20" ry="4"/>
    <g class="drift">
      <path class="dimst" d="M48 26 q-2 -6 -8 -7"/><circle class="dimbe" cx="39" cy="18" r="5"/>
      <rect class="dim" x="17" y="27" width="62" height="54" rx="19"/>{"".join(eyes)}</g>
  </g>"""
    return body, "\n" + "\n".join(css)


def human(x: float, y: float, s: float) -> str:
    """You: the probe's clay and shadow, a head over a half-round torso, no
    face and no beacon — eyes are the character's alone. It breathes on the
    cycle `probe-presentation.svg`'s listener shares."""
    return f"""<g transform="translate({x} {y}) scale({s})">
    <ellipse class="shadow" cx="48" cy="90" rx="18" ry="4"/>
    <g class="breathe"><circle class="hull" cx="48" cy="33" r="14.5"/>
    <path class="hull" d="M21 76 a27 27 0 0 1 54 0 Z"/></g></g>"""


def svg(w: int, h: int, label: str, css: str, body: str, vb: str | None = None) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{vb or f'0 0 {w} {h}'}" role="img" aria-label="{label}">
  <style>{CHARACTER_CSS}{css}{REDUCED}  </style>
{body}
</svg>
"""


# ── hero ──────────────────────────────────────────────────────────────
# One 25 s cycle in two scenes. 0–34 %: the probe out of it while loose
# papers fall where the feed will stand, labelled as arXiv's daily count.
# 40–96 %: the reader with its coffee, and the feed, where PROBE marks a few
# papers as they cross a reading line, labelled as its weekly count.

H = 330
FEED_X, FEED_TOP, ROW = 690, 46, 34
FEED_BOT = H - 40
LINE_Y = (FEED_TOP + FEED_BOT) // 2          # where a card is marked
N, DUR = 18, 25                               # rows per loop, s per cycle
LOOP = N * ROW                                # px scrolled per cycle, ~24.5 px/s
# Rows (per copy of eighteen) that get marked: 10.9, 13.7, 16.5 and 19.3 s,
# all inside the reader's scene. Each starts below the reading line, so the
# feed fades in unmarked; the copy scrolling in behind never reaches the line
# within a cycle, so the loop joins without a card changing state; and the
# last marked card has left the window before the flood comes back.
PICKED = (11, 13, 15, 17)
LOST, READ = "0%, 34% { opacity: 1; } 40%, 96% { opacity: 0; } 100% { opacity: 1; }", \
             "0%, 34% { opacity: 0; } 40%, 96% { opacity: 1; } 100% { opacity: 0; }"
FLOOD = [(704, 84, 8), (752, 120, -10), (806, 96, 12), (774, 104, -6),
         (726, 176, -6), (790, 196, 6), (832, 150, -12), (700, 136, 10)]

HERO_CSS = f"""
    .ground {{ fill: ${{CARD}}; }}
    .edge   {{ fill: none; stroke: ${{ACCENT}}; }}
    .eyebrow{{ fill: ${{DEEP}}; font: 11px {MONO}; letter-spacing: 2.6px; }}
    .head   {{ fill: ${{INK}}; font: 700 44px {SANS}; letter-spacing: -1.2px; }}
    .claim  {{ fill: ${{ACCENT}}; font: 700 24px {SANS}; letter-spacing: -.3px; }}
    .sub    {{ fill: ${{MUTED}}; font: 15px {SANS}; }}
    .tag    {{ fill: ${{MUTED}}; font: 10px {MONO}; letter-spacing: 1.6px; }}
    .miss   {{ fill: ${{GHOST}}; }}
    .missl  {{ fill: ${{MUTED}}; opacity: .28; }}
    .hit    {{ fill: ${{IRIS}}; stroke: ${{ACCENT}}; stroke-width: 1.5; }}
    .hitl   {{ fill: ${{DEEP}}; }}
    .dot    {{ fill: ${{ACCENT}}; }}
    .ring   {{ fill: none; stroke: ${{ACCENT}}; stroke-width: 1.5; opacity: 0;
              transform-box: fill-box; transform-origin: 50% 50%; }}
    .fade0  {{ stop-color: ${{CARD}}; stop-opacity: 1; }}
    .fade1  {{ stop-color: ${{CARD}}; stop-opacity: 0; }}
    .sheet  {{ fill: ${{IRIS}}; stroke: ${{BORDER}}; stroke-width: 1.5; }}
    .sl     {{ fill: ${{MUTED}}; opacity: .3; }}
    .cta    {{ fill: ${{ACCENT}}; }}
    .ctat   {{ fill: ${{IRIS}}; font: 600 15px {SANS}; }}
    .ctaa   {{ fill: none; stroke: ${{IRIS}}; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round;
              animation: nudge 1.8s ease-in-out infinite; }}
    .feed   {{ animation: scroll {DUR}s linear infinite; }}
    .mood-lost {{ animation: mlost {DUR}s ease-in-out infinite; }}
    .mood-read {{ animation: mread {DUR}s ease-in-out infinite; }}
    .feedwin   {{ animation: mread {DUR}s ease-in-out infinite; }}
    .rain      {{ animation: rain 2.4s ease-in infinite; }}
    .rn1 {{ animation-delay: .6s; }} .rn2 {{ animation-delay: 1.2s; }} .rn3 {{ animation-delay: 1.8s; }}
    @keyframes scroll {{ from {{ transform: translateY(0); }} to {{ transform: translateY(-{LOOP}px); }} }}
    @keyframes nudge  {{ 0%, 100% {{ transform: translateX(0); }} 50% {{ transform: translateX(3px); }} }}
    @keyframes mlost  {{ {LOST} }}
    @keyframes mread  {{ {READ} }}
    @keyframes rain   {{ 0% {{ transform: translateY(-40px); opacity: 0; }} 20% {{ opacity: 1; }}
                        80% {{ opacity: 1; }} 100% {{ transform: translateY(40px); opacity: 0; }} }}"""


def sheet(x: float, y: float, rot: float, cls: str) -> str:
    """One loose paper, the unread kind — no accent, no mark."""
    return (f'<g class="{cls}" transform="rotate({rot} {x+15} {y+19})">'
            f'<rect class="sheet" x="{x}" y="{y}" width="30" height="38" rx="3"/>'
            f'<rect class="sl" x="{x+6}" y="{y+8}" width="18" height="2.4" rx="1.2"/>'
            f'<rect class="sl" x="{x+6}" y="{y+14}" width="18" height="2.4" rx="1.2"/>'
            f'<rect class="sl" x="{x+6}" y="{y+20}" width="12" height="2.4" rx="1.2"/></g>')


def feed() -> tuple[str, str]:
    """Two copies of the feed, and the keyframes that mark and ring the picks."""
    rows, css = [], []
    for copy in (0, 1):
        for i in range(N):
            y = FEED_TOP + 4 + i * ROW + copy * LOOP
            w1, w2 = (110, 70) if i % 2 else (96, 84)
            rows.append(f'<rect x="{FEED_X}" y="{y}" width="150" height="24" rx="5" class="miss"/>'
                        f'<rect x="{FEED_X+12}" y="{y+7}" width="{w1}" height="3.4" rx="1.7" class="missl"/>'
                        f'<rect x="{FEED_X+12}" y="{y+14}" width="{w2}" height="3.4" rx="1.7" class="missl"/>')
            if i not in PICKED or copy:
                continue
            a = round((y + 12 - LINE_Y) / LOOP * 100, 2)      # crosses the line
            b, c = round(a + 1.2, 2), round(a + 5, 2)
            css.append(f"    .m{i} {{ animation: m{i} {DUR}s linear infinite; }}\n"
                       f"    @keyframes m{i} {{ 0%, {a}% {{ opacity: 0; }} {b}%, 100% {{ opacity: 1; }} }}\n"
                       f"    .r{i} {{ animation: r{i} {DUR}s ease-out infinite; }}\n"
                       f"    @keyframes r{i} {{ 0%, {a}% {{ opacity: 0; transform: scale(.4); }} "
                       f"{b}% {{ opacity: .9; transform: scale(.6); }} "
                       f"{c}%, 100% {{ opacity: 0; transform: scale(3.6); }} }}")
            rows.append(f'<g class="m{i}"><rect x="{FEED_X}" y="{y}" width="150" height="24" rx="5" class="hit"/>'
                        f'<circle cx="{FEED_X+13}" cy="{y+12}" r="4" class="dot"/>'
                        f'<rect x="{FEED_X+24}" y="{y+7}" width="96" height="3.4" rx="1.7" class="hitl"/>'
                        f'<rect x="{FEED_X+24}" y="{y+14}" width="62" height="3.4" rx="1.7" class="hitl" opacity=".5"/></g>'
                        f'<circle class="ring r{i}" cx="{FEED_X+13}" cy="{y+12}" r="4"/>')
    return "\n      ".join(rows), "\n" + "\n".join(css)


def hero() -> str:
    rows, marks = feed()
    lost, lost_css = lost_probe(544, H - 164, 1.3)
    rain = "".join(sheet(x, y, r, f"rain rn{k % 4}") for k, (x, y, r) in enumerate(FLOOD))
    reader = probe(534, H - 172, 1.4, "read", page=True, mug=True)
    return svg(880, H, "PROBE — Stop drowning in arXiv. PROBE marks the target. Open the reading site.",
               HERO_CSS + marks + lost_css, f"""
  <defs>
    <clipPath id="win"><rect x="{FEED_X-12}" y="{FEED_TOP}" width="184" height="{FEED_BOT-FEED_TOP}"/></clipPath>
    <linearGradient id="ft" x1="0" y1="0" x2="0" y2="1"><stop class="fade0" offset="0"/><stop class="fade1" offset="1"/></linearGradient>
    <linearGradient id="fb" x1="0" y1="1" x2="0" y2="0"><stop class="fade0" offset="0"/><stop class="fade1" offset="1"/></linearGradient>
  </defs>
  <rect class="ground" width="880" height="{H}" rx="12"/>
  <rect class="edge" x=".5" y=".5" width="879" height="{H-1}" rx="11.5"/>

  <text class="eyebrow" x="48" y="62">PROBE · RESEARCH SCOUT</text>
  <text class="head" x="45" y="116">Stop drowning in arXiv.</text>
  <text class="claim" x="47" y="160">PROBE marks the target.</text>
  <text class="sub" x="48" y="202">Dexterous manipulation papers, scouted on a schedule,</text>
  <text class="sub" x="48" y="224">and retold in Korean when you name one.</text>
  <rect class="cta" x="48" y="252" width="258" height="44" rx="22"/>
  <text class="ctat" x="72" y="279">Open the reading site</text>
  <path class="ctaa" d="M270 274h16m-6-6 6 6-6 6"/>

  <g class="feedwin" clip-path="url(#win)">
    <g class="feed">
      {rows}
    </g>
    <rect x="{FEED_X-12}" y="{FEED_TOP}" width="184" height="46" fill="url(#ft)"/>
    <rect x="{FEED_X-12}" y="{FEED_BOT-46}" width="184" height="46" fill="url(#fb)"/>
  </g>
  <text class="tag mood-lost" x="{FEED_X}" y="34">arXiv · 50–100 A DAY</text>
  <text class="tag mood-read" x="{FEED_X}" y="34">PROBE · 3–5 A WEEK</text>

  <g class="mood-lost">{lost}{rain}</g>
  <g class="mood-read">{reader}</g>
""")


# ── own ───────────────────────────────────────────────────────────────
# You, the context/ frame, the probe, and the frame of folders it writes, on
# one row. Both frames share a top and a height with their labels above them,
# both bodies centre on the frames, and the probe stands as far from its
# folders as you do from context/.

OWN_CSS = f"""
    .mine  {{ fill: ${{CARD}}; stroke: ${{ACCENT}}; stroke-width: 1.2; }}
    .matte {{ fill: none; stroke: ${{SOFT}}; stroke-width: 1; }}
    .row   {{ fill: ${{CARD}}; stroke: ${{BORDER}}; stroke-width: 1.2; }}
    .eb    {{ fill: ${{DEEP}}; font: 9.5px {MONO}; letter-spacing: 1.8px; }}
    .p     {{ fill: ${{INK}}; font: 700 13px {MONO}; }}
    .ps    {{ fill: ${{MUTED}}; font: 11px {MONO}; }}
    .note  {{ fill: ${{MUTED}}; font: 12.5px {SANS}; }}
    .wire  {{ fill: none; stroke: ${{ACCENT}}; stroke-width: 1.6; stroke-dasharray: 4 5;
             animation: march 1.2s linear infinite; }}
    .head  {{ fill: ${{ACCENT}}; }}
    @keyframes march {{ to {{ stroke-dashoffset: -18; }} }}"""

FOLDERS = [("scouting/", "scheduled"), ("analysis/", "on demand"),
           ("comparison/", "on demand"), ("presentation/", "on demand")]


def own() -> str:
    W, H, TOP, FH, PS = 880, 204, 52, 112, .9
    mid = TOP + FH / 2
    base = mid + 34                       # where both shadows sit
    hx = 20                               # you
    cx, cw = hx + 96, 196                 # the context/ frame
    px = cx + cw + 100                    # the probe's box
    gap = cx - (hx + 75 * .8)             # you → frame, reused probe → frame
    ox, ow = px + 79 * PS + gap, 262      # the folders' frame
    shift = (W - (ox + ow) - hx) / 2      # centre the row
    wx = cx + cw + 20                     # the arrow clears the frame
    tip = px + 17 * PS - 18               # and stops short of the hull
    b = [f'<text class="eb" x="{cx}" y="{TOP-10}">YOU WRITE</text>',
         human(hx, base - 90 * .8, .8),
         f'<rect class="mine" x="{cx}" y="{TOP}" width="{cw}" height="{FH}" rx="10"/>',
         f'<rect class="matte" x="{cx+5}" y="{TOP+5}" width="{cw-10}" height="{FH-10}" rx="7"/>',
         f'<text class="p" x="{cx+20}" y="{mid-12}">context/</text>',
         f'<text class="ps" x="{cx+20}" y="{mid+10}">MASTER.md</text>',
         f'<text class="ps" x="{cx+20}" y="{mid+28}">P#.md, one per pillar</text>',
         f'<path class="wire" d="M{wx} {mid} H{tip - 8}"/><path class="head" d="M{tip} {mid} l-8 -4.5 v9 Z"/>',
         f'<text class="note" x="{(wx + tip) / 2}" y="{mid-10}" text-anchor="middle">reads</text>',
         probe(px, base - 90 * PS, PS, "read", page=True),
         f'<text class="eb" x="{ox}" y="{TOP-10}">PROBE WRITES</text>',
         f'<rect class="mine" x="{ox}" y="{TOP}" width="{ow}" height="{FH}" rx="10"/>']
    for k, (path, when) in enumerate(FOLDERS):
        y = TOP + 9 + k * 25
        b += [f'<rect class="row" x="{ox+9}" y="{y}" width="{ow-18}" height="21" rx="5"/>',
              f'<text class="p" x="{ox+20}" y="{y+15}">{path}</text>',
              f'<text class="ps" x="{ox+ow-20}" y="{y+15}" text-anchor="end">{when}</text>']
    b.append(f'<text class="note" x="{W/2 - shift}" y="{H-14}" text-anchor="middle">'
             'It reads context/ and never writes it. Changes come to you as proposals.</text>')
    return svg(W, H, "Who writes what: you write context/, and PROBE reads it and writes scouting/, "
               "analysis/, comparison/ and presentation/. Changes to context/ come to you as proposals.",
               OWN_CSS, f'<g transform="translate({shift:.1f} 0)">' + "\n  ".join(b) + "</g>")


# ── probe-ideation ────────────────────────────────────────────────────

IDEATION_CSS = """
    .bub  { fill: ${IRIS}; stroke: ${DEEP}; stroke-width: 1.6; }
    .bdot { fill: ${DEEP}; opacity: .2; }
    .t1   { animation: think 2.4s ease-in-out infinite; }
    .t2   { animation: think 2.4s ease-in-out .3s infinite; }
    .t3   { animation: think 2.4s ease-in-out .6s infinite; }
    @keyframes think { 0%, 100% { opacity: .2; } 40% { opacity: 1; } }"""


def ideation() -> str:
    """The probe looking up at a thought whose dots light in turn."""
    thought = """<g>
      <circle class="bub" cx="80" cy="26" r="2.6"/><circle class="bub" cx="87" cy="16" r="4"/>
      <ellipse class="bub" cx="104" cy="2" rx="16" ry="11"/>
      <circle class="bdot t1" cx="96" cy="2" r="2.6"/><circle class="bdot t2" cx="104" cy="2" r="2.6"/><circle class="bdot t3" cx="112" cy="2" r="2.6"/></g>"""
    return svg(84, 81, "PROBE — thinking up what nobody has tried", IDEATION_CSS,
               probe(0, 0, 1, "up") + thought, vb="4 -14 122 118")


IMAGES = {"hero": hero, "own": own, "probe-ideation": ideation}


def main() -> int:
    check = "--check" in sys.argv[1:]
    stale = []
    for name, build in IMAGES.items():
        src = build()
        for suffix, pal in (("", LIGHT), ("-dark", DARK)):
            path = OUT / f"{name}{suffix}.svg"
            text = Template(src).substitute(pal)
            if check:
                if not path.exists() or path.read_text() != text:
                    stale.append(path.name)
            else:
                path.write_text(text)
    if stale:
        print(f"[build-art] out of date: {', '.join(stale)} — run python3 assets/build-art.py")
        return 1
    print(f"[build-art] {'clean' if check else 'wrote'} — {len(IMAGES) * 2} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
