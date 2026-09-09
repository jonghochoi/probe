#!/usr/bin/env python3
"""Bake `flow.svg` and `flow-dark.svg` — the diagram the README's "How it
works" section embeds.

The other images in this folder are hand-authored: they are small enough that
editing the file is editing the drawing. This one is not — it carries twenty-odd
placed elements plus a timed picking cycle, and moving any of them drags the
wires, arrowheads and keyframes that point at it. So the geometry lives here as
named coordinates and the two files are generated, which also guarantees the
light and dark pair never drift apart: one source, two palettes, identical
markup.

    python3 assets/build-flow.py            # write both files
    python3 assets/build-flow.py --check    # fail if either is out of date

What the drawing has to keep saying, whatever is moved:

  - Rectangles are files and only files. `context/` is one card of two
    compartments, each output is one card of a header and the paths under
    it, and nothing that is not a file gets a box: a stage is a funnel, an
    act is a wire.
  - The `context/` card's divider, the drop wire and the mark share one
    vertical axis (x=468), so the read is "both documents feed one run".
  - The `context/` card takes the same ground and the same border as the
    outputs, and is marked instead by a hairline ruled just inside that
    border. It is the one card the agent may not write, and a document held
    in a matte frame is how the picture says so before any label does. The
    hairline is a frame on the card, not a second box: it never encloses a
    file of its own, so the rule above still holds.
  - The two output cards clear the `context/` card by more than the gap
    between their own edges. They overlap it horizontally, so a thin gap
    reads as one stack of three boxes rather than an input and two outputs.
  - The drawing ends at the two outputs. It runs arXiv to files and stops,
    because what a reader does with a report is a decision rather than a
    file, and a wire drawn back into `context/` would put the one folder the
    agent may not write at the end of the agent's own arrow.
  - Every wire is one drawing: the same accent, the same march, and the same
    gap off whatever it leaves. A wire says a hand-off happened, never whose
    hand — that is the cards' to say. Drawn weaker than its neighbours, a
    wire reads as a weaker hand-off rather than a different owner.
  - The mark is `site/builder/components.py`'s `mark()` redrawn with its
    animation inlined, since a README image carries no external stylesheet.
    Keep the two drawings in step.

The picking cycle earns every state it shows, in this order: a uniform field,
a scan band that marks six as it passes their column, six dispatched toward the
filter, three culled inside it — each stays a circle, turns from the accent to
the muted ink and fades out as it drifts to a halt — three landed in the kept
column. Nothing is marked before the scan reaches it and nothing sits at its
destination before it travels.

Durations are literal, never `var()`: a custom property declared on `:root`
resolves only while the SVG is its own document, and an unresolved duration
drops the whole animation.
"""

from __future__ import annotations

import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent

LIGHT = dict(
    CARD="#FFFCFA", BORDER="#E8CDBD", BORDER_SOFT="#F2DFD3",
    WASH="#FBF3EE", ACCENT="#D97757", ACCENT_DEEP="#B06749",
    INK="#1F1611", MUTED="#7A6A60",
    HULL="#D97757", STALK="#CC785C", IRIS="#FFFAF7", PUPIL="#2A1A12",
)
DARK = dict(
    CARD="#211C19", BORDER="#3D3129", BORDER_SOFT="#332B26",
    WASH="#262019", ACCENT="#E8916F", ACCENT_DEEP="#C98A6D",
    INK="#F2EAE4", MUTED="#A08D80",
    HULL="#E8916F", STALK="#F0A183", IRIS="#FFF6F1", PUPIL="#2A1A12",
)

# System stacks, not webfonts: a README image is rendered wherever GitHub is
# read. Every text run is left- or centre-anchored with room to spare, so a
# substituted face changes the width without colliding with anything.
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"
SANS = "system-ui, -apple-system, 'Segoe UI', 'Noto Sans KR', sans-serif"

W, H = 880, 348
AXIS = 468          # card divider, drop wire and mark centre

CYCLE = "9s"        # one full pick, slow enough to watch out of the corner of an eye
BAND = ".11"        # the scan band, faint enough not to compete with the wires

# Six candidates, ordered by column so the scan reaches them left to right.
# Three carry a landing slot; three are culled part-way, inside the funnel —
# each at its own fraction of the path, chosen to miss the filter caption.
KEPT_Y = (186, 206, 226)
PICKS = [
    dict(x=73,  y=188, land=0),
    dict(x=98,  y=288, land=None, cull=.55),
    dict(x=123, y=138, land=None, cull=.42),
    dict(x=148, y=213, land=1),
    dict(x=198, y=163, land=None, cull=.40),
    dict(x=223, y=238, land=2),
]
LANDINGS = [58, 62, 66]      # % of the cycle, in slot order


def pct_column(x: float) -> float:
    """When the scan band's centre crosses a column, as % of the cycle."""
    return round((x - 43) / 196 * 30, 1)


def pick_css() -> str:
    """Per-candidate keyframes: the mark, the flight, the cull or the landing."""
    out = []
    for i, p in enumerate(PICKS):
        tc, dep = pct_column(p["x"]), 34 + 2 * i
        out.append(f"""    #m{i} {{ animation: mark{i} {CYCLE} linear infinite; }}
    @keyframes mark{i} {{
      0%, {tc}%        {{ fill: {{BORDER}}; transform: scale(1); }}
      {tc + 1.5}%      {{ fill: {{ACCENT}}; transform: scale(1.9); }}
      {tc + 6}%        {{ fill: {{ACCENT}}; transform: scale(1); }}
      {dep}%           {{ fill: {{ACCENT}}; transform: scale(1); }}
      {dep + 5}%, 100% {{ fill: {{BORDER}}; transform: scale(1); }}
    }}
""")
        if p["land"] is None:
            dx, dy = 404 - p["x"], 206 - p["y"]
            mx, my = dx * p["cull"], dy * p["cull"]
            gx, gy = mx * 1.13, my * 1.13
            stop, grey, gone = dep + 13, dep + 17, dep + 29
            out.append(f"""    #t{i} {{ animation: trav{i} {CYCLE} ease-out infinite; }}
    @keyframes trav{i} {{
      0%, {dep}%    {{ transform: translate(0, 0) scale(1); opacity: 0; fill: {{ACCENT}}; }}
      {dep + 1}%    {{ transform: translate(0, 0) scale(1); opacity: 1; fill: {{ACCENT}}; }}
      {stop}%       {{ transform: translate({mx:.0f}px, {my:.0f}px) scale(1); opacity: 1; fill: {{ACCENT}}; }}
      {grey}%       {{ transform: translate({mx:.0f}px, {my:.0f}px) scale(1); opacity: .9; fill: {{MUTED}}; }}
      {gone}%, 100% {{ transform: translate({gx:.0f}px, {gy:.0f}px) scale(.72); opacity: 0; fill: {{MUTED}}; }}
    }}
""")
        else:
            slot = p["land"]
            dx, dy = 404 - p["x"], KEPT_Y[slot] - p["y"]
            land = LANDINGS[slot]
            out.append(f"""    #t{i} {{ animation: trav{i} {CYCLE} ease-in-out infinite; }}
    @keyframes trav{i} {{
      0%, {dep}%        {{ transform: translate(0, 0) scale(1); opacity: 0; }}
      {dep + 1}%        {{ transform: translate(0, 0) scale(1); opacity: 1; }}
      {land}%           {{ transform: translate({dx}px, {dy}px) scale(1.6); opacity: 1; }}
      {land + 4}%, 100% {{ transform: translate({dx}px, {dy}px) scale(1.18); opacity: 1; }}
    }}
""")
    return "".join(out)


CSS = f"""
    .hull   {{ fill: {{HULL}}; }}
    .iris   {{ fill: {{IRIS}}; }}
    .pupil  {{ fill: {{PUPIL}}; }}
    .stalk  {{ stroke: {{STALK}}; stroke-width: 5; stroke-linecap: round; fill: none; }}
    .beacon {{ fill: {{STALK}}; }}
    .wave   {{ fill: none; stroke: {{STALK}}; stroke-width: 2.6;
              stroke-linecap: round; opacity: 0; }}
    .shadow {{ fill: {{STALK}}; opacity: .45; }}
    .rig    {{ animation: bob 3.4s ease-in-out infinite; }}
    .w1     {{ animation: ping 2.6s ease-in-out infinite; }}
    .w2     {{ animation: ping 2.6s ease-in-out .34s infinite; }}
    .lid    {{ animation: blink 5.4s ease-in-out infinite; }}
    .eL, .eL .lid {{ transform-origin: 36px 52px; }}
    .eR, .eR .lid {{ transform-origin: 60px 52px; }}
    @keyframes bob   {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-3px); }} }}
    @keyframes ping  {{ 0%, 100% {{ opacity: 0; }} 12%, 42% {{ opacity: .85; }} 58% {{ opacity: 0; }} }}
    @keyframes blink {{ 0%, 88%, 100% {{ transform: scaleY(1); }}
                       92% {{ transform: scaleY(.06); }} 96% {{ transform: scaleY(1); }} }}
    @keyframes march {{ to {{ stroke-dashoffset: -14; }} }}

    .m    {{ font-family: {{MONO}}; }}
    .lab  {{ font-family: {{MONO}}; font-size: 10px; letter-spacing: 2.2px; fill: {{ACCENT_DEEP}}; }}
    .tick {{ font-family: {{MONO}}; font-size: 9.5px; letter-spacing: 1.4px; fill: {{ACCENT_DEEP}}; }}
    .path {{ font-family: {{MONO}}; font-size: 15.5px; font-weight: 700; fill: {{INK}}; }}
    .rest {{ font-weight: 400; font-size: 11.5px; fill: {{MUTED}}; }}
    .note {{ font-family: {{SANS}}; font-size: 11px; fill: {{MUTED}}; }}
    .wire {{ fill: none; stroke: {{ACCENT}}; stroke-width: 1.6; stroke-linecap: round;
            stroke-linejoin: round; }}
    .flow {{ stroke-dasharray: 7 7; animation: march 1.1s linear infinite; }}
    .head  {{ fill: {{ACCENT}}; }}

    .d    {{ fill: {{BORDER}}; opacity: .85; }}
    .mk   {{ fill: {{BORDER}}; opacity: .9; }}
    .tv   {{ fill: {{ACCENT}}; opacity: 0; }}
    .keep {{ fill: {{ACCENT}}; animation: keep {CYCLE} linear infinite; }}
    .scan {{ animation: scan {CYCLE} linear infinite; }}
    @keyframes scan {{
      0%        {{ transform: translateX(0); opacity: 0; }}
      3%        {{ opacity: {BAND}; }}
      30%       {{ transform: translateX(196px); opacity: {BAND}; }}
      34%, 100% {{ transform: translateX(196px); opacity: 0; }}
    }}
    @keyframes keep {{
      0%, 34%   {{ opacity: 1; }}
      40%, 100% {{ opacity: 0; }}
    }}
{pick_css()}
    @media (prefers-reduced-motion: reduce) {{
      .rig, .lid, .wave, .flow {{ animation: none; }}
      .wave {{ opacity: .5; }}
      .scan, .tv {{ display: none; }}
      .mk, .keep {{ animation: none; }}
      .mk {{ fill: {{ACCENT}}; }}
      .keep {{ opacity: 1; }}
    }}
"""


def mark(tx: float, ty: float, s: float) -> str:
    """The PROBE mark at (tx, ty), scaled by s."""
    eyes = "".join(
        f'<g class="eye {side}"><g class="lid">'
        f'<circle class="iris" cx="{x}" cy="52" r="11"/>'
        f'<circle class="pupil" cx="{x}" cy="52" r="5"/>'
        "</g></g>"
        for side, x in (("eL", 36), ("eR", 60))
    )
    return (
        f'<g transform="translate({tx} {ty}) scale({s})">'
        '<ellipse class="shadow" cx="48" cy="90" rx="20" ry="4"/>'
        '<g class="rig">'
        '<path class="wave w1" d="M41.04 11.12 A8.5 8.5 0 0 1 54.96 11.12"/>'
        '<path class="wave w2" d="M36.94 8.25 A13.5 13.5 0 0 1 59.06 8.25"/>'
        '<path class="stalk" d="M48 26 V19"/>'
        '<circle class="beacon" cx="48" cy="16" r="5"/>'
        '<rect class="hull" x="17" y="27" width="62" height="54" rx="19"/>'
        f"{eyes}</g></g>"
    )


# Arrowheads are drawn, not `<marker>`-ed: one less element for a Markdown
# sanitiser to have an opinion about. Each takes the tip, not the tail.
def arrow_r(x: float, y: float) -> str:
    return f'<path class="head" d="M{x} {y} l-8 -4.6 v9.2 z"/>'


def arrow_d(x: float, y: float) -> str:
    return f'<path class="head" d="M{x} {y} l-4.6 -8 h9.2 z"/>'


def at(x: float, y: float, inner: str) -> str:
    """Place at (x, y) so a CSS scale turns about the element's own centre."""
    return f'<g transform="translate({x:.0f} {y:.0f})">{inner}</g>'


def card(x: float, y: float, header: str, paths: list[str]) -> str:
    """One agent-written output: a header naming its cadence, then its files.

    A card holds paths and the header that binds them, and nothing else. A
    subtitle under one card and not the others reads as that output being the
    important one, when the only difference is cadence and the header already
    carries it. Nothing is ruled between the paths either: a divider inside an
    output card groups or ranks, and these share exactly the cadence named
    above them.

    A path is set in two registers, because it is two things: everything up
    to the last `/` is where the file lives, and the rest is a filename
    pattern. Set alike they read as one wall of bold — every card the same
    weight, nothing leading the eye — so the directory carries the size and
    the ink, and the pattern drops to the weight of a note. What a reader is
    looking for is which four tracks exist and where each one writes, and a
    track that nests one level deeper says so in the same register as the
    track itself.

    Every path is written with a `<…>` placeholder rather than a specimen
    filename. The face is a system stack, so a wide substitution has to have
    somewhere to go; a literal date is the longest string here and the first
    to leave the card through its right edge.
    """
    h = 64 + 22 * (len(paths) - 1)
    return (
        f'<rect x="{x}" y="{y}" width="240" height="{h}" rx="10" '
        'fill="{CARD}" stroke="{BORDER}"/>'
        f'<text class="tick" x="{x + 20}" y="{y + 26}">{header}</text>'
        + "".join(
            f'<text class="path" x="{x + 20}" y="{y + 50 + 22 * j}">{track}/'
            f'<tspan class="rest">{rest}</tspan></text>'
            for j, (track, _, rest) in enumerate(p.rpartition("/") for p in paths))
    )


def field() -> str:
    """The day's pile — uniform until the scan reaches each column."""
    picked = {(p["x"], p["y"]) for p in PICKS}
    plain = "".join(
        f'<circle class="d" cx="{48 + c * 25}" cy="{138 + r * 25}" r="3.4"/>'
        for r in range(7) for c in range(8)
        if (48 + c * 25, 138 + r * 25) not in picked
    )
    marks = "".join(
        at(p["x"], p["y"], f'<circle class="mk" id="m{i}" r="3.4"/>')
        for i, p in enumerate(PICKS)
    )
    band = ('<rect class="scan" x="36" y="128" width="14" height="172" rx="7" '
            'fill="{ACCENT}"/>')
    return band + plain + marks


def overlay() -> str:
    """Everything that crosses the funnel, so it paints above it."""
    keep = "".join(f'<circle class="keep" cx="404" cy="{y}" r="4"/>' for y in KEPT_Y)
    fly = "".join(
        at(p["x"], p["y"], f'<circle class="tv" id="t{i}" r="3.4"/>')
        for i, p in enumerate(PICKS)
    )
    return keep + fly


def drawing() -> str:
    return f"""
  <rect width="{W}" height="{H}" rx="14" fill="{{CARD}}"/>
  <rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="13.25" fill="none" stroke="{{BORDER}}"/>

  <rect x="288" y="26" width="360" height="82" rx="10" fill="{{CARD}}" stroke="{{BORDER}}"/>
  <rect x="293.5" y="31.5" width="349" height="71" rx="6" fill="none" stroke="{{BORDER_SOFT}}"/>
  <text class="tick" x="308" y="50">CONTEXT · HUMAN-OWNED · READ-ONLY</text>
  <path d="M{AXIS} 60 V96" stroke="{{BORDER}}" stroke-width="1"/>
  <text class="path" x="308" y="76" font-size="13">MASTER.md</text>
  <text class="note" x="308" y="95">global anchor</text>
  <text class="path" x="488" y="76" font-size="13">P#.md</text>
  <text class="note" x="488" y="95">per-pillar decision log</text>
  <path class="wire flow" d="M{AXIS} 122 V138"/>
  {arrow_d(AXIS, 146)}

  <text class="lab" x="44" y="112">ARXIV cs.RO + cs.LG</text>
  {field()}
  <text class="note" x="44" y="312" font-size="10.5">50–100 papers a day</text>

  <path d="M246 124 L392 176 V236 L246 288" fill="{{WASH}}" stroke="{{BORDER}}"
        stroke-width="1.2" stroke-dasharray="5 5" stroke-linejoin="round"/>
  <text class="note" x="266" y="200" font-size="10.5">citation graph ·</text>
  <text class="note" x="266" y="218" font-size="10.5">anti-topics · scoring</text>
  {overlay()}

  {mark(422, 158, .96)}

  <path class="wire flow" d="M516 206 C548 206, 552 166, 578 166"/>
  {arrow_r(586, 166)}
  <path class="wire flow" d="M516 206 C548 206, 552 272, 578 272"/>
  {arrow_r(586, 272)}

  {card(592, 134, "SCHEDULED · PER PILLAR", ["scouting/P#/&lt;date&gt;.md"])}
  {card(592, 218, "ON DEMAND · YOU NAME IT", ["analysis/&lt;id&gt;.md",
                                              "comparison/&lt;slug&gt;.md",
                                              "presentation/&lt;id&gt;.md"])}
"""


def render(palette: dict[str, str]) -> str:
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" '
        'aria-label="PROBE pipeline — arXiv in, a scouting report and the '
        'on-demand pages out">\n'
        f"  <style>{CSS}  </style>\n"
        f"{drawing()}\n</svg>\n"
    )
    for key, value in {**palette, "MONO": MONO, "SANS": SANS}.items():
        svg = svg.replace("{" + key + "}", value)
    return svg


def main(argv: list[str]) -> int:
    files = {"flow.svg": render(LIGHT), "flow-dark.svg": render(DARK)}
    if "--check" in argv:
        stale = [
            name for name, body in files.items()
            if not (OUT / name).exists() or (OUT / name).read_text(encoding="utf-8") != body
        ]
        if stale:
            print(
                "[build-flow] stale: " + ", ".join(stale)
                + " — run `python3 assets/build-flow.py`"
            )
            return 1
        print(f"[build-flow] clean — {len(files)} file(s) match the source")
        return 0
    for name, body in files.items():
        (OUT / name).write_text(body, encoding="utf-8")
    print("[build-flow] wrote " + ", ".join(files))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
