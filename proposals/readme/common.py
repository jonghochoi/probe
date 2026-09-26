"""Shared palette, fonts and the probe character for the README proposals.

Every image is written twice — light and dark — from one template, the way
`assets/build-flow.py` bakes `flow.svg`. Tokens are `${NAME}` (string.Template)
so CSS braces stay literal.
"""
from __future__ import annotations
from pathlib import Path
from string import Template

LIGHT = dict(
    CARD="#FFFCFA", BORDER="#E8CDBD", SOFT="#F2DFD3", WASH="#FBF3EE",
    ACCENT="#D97757", DEEP="#B06749", INK="#1F1611", MUTED="#7A6A60",
    HULL="#D97757", STALK="#CC785C", IRIS="#FFFAF7", PUPIL="#2A1A12",
    DIM="#C4B6AE", DIMSTALK="#B3A49B", DIMINK="#6B5A50", GHOST="#EFE4DC",
    TERM="#1F1A17", TERMINK="#F2EAE4", TERMMUTED="#9C8B80",
)
DARK = dict(
    CARD="#211C19", BORDER="#3D3129", SOFT="#332B26", WASH="#262019",
    ACCENT="#E8916F", DEEP="#C98A6D", INK="#F2EAE4", MUTED="#A08D80",
    HULL="#E8916F", STALK="#F0A183", IRIS="#FFF6F1", PUPIL="#2A1A12",
    DIM="#6E625B", DIMSTALK="#5E534C", DIMINK="#2A211C", GHOST="#2E2622",
    TERM="#161210", TERMINK="#F2EAE4", TERMMUTED="#8C7B70",
)

MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"
SANS = "system-ui, -apple-system, 'Segoe UI', 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif"

# Character parts and the motions every scene may borrow. Animated classes sit
# on groups that carry no transform attribute — a CSS transform replaces it.
BASE_CSS = """
    .hull   { fill: ${HULL}; }
    .iris   { fill: ${IRIS}; }
    .pupil  { fill: ${PUPIL}; }
    .lids   { fill: none; stroke: ${PUPIL}; stroke-width: 3.4; stroke-linecap: round; }
    .stalk  { stroke: ${STALK}; stroke-width: 5; stroke-linecap: round; fill: none; }
    .beacon { fill: ${STALK}; }
    .page   { fill: ${IRIS}; stroke: ${DEEP}; stroke-width: 2; }
    .line   { fill: ${DEEP}; opacity: .3; }
    .wave   { fill: none; stroke: ${STALK}; stroke-width: 2.6; stroke-linecap: round; opacity: 0; }
    .shadow { fill: ${STALK}; opacity: .45; }
    .dim    { fill: ${DIM}; }
    .dimst  { stroke: ${DIMSTALK}; stroke-width: 5; stroke-linecap: round; fill: none; }
    .dimbe  { fill: ${DIMSTALK}; }
    .cross  { fill: none; stroke: ${DIMINK}; stroke-width: 3.2; stroke-linecap: round; }
    .mug    { fill: ${IRIS}; stroke: ${DEEP}; stroke-width: 2; stroke-linejoin: round; }
    .handle { fill: none; stroke: ${DEEP}; stroke-width: 2.4; stroke-linecap: round; }
    .brew   { fill: ${DEEP}; }
    .steam  { fill: none; stroke: ${STALK}; stroke-width: 2.2; stroke-linecap: round; opacity: 0; }
    .z      { fill: ${DEEP}; font-family: ${MONO}; font-weight: 700; }
    .rig    { animation: bob 3.4s ease-in-out infinite; }
    .lid    { transform-box: fill-box; transform-origin: 50% 50%;
              animation: blink 7s ease-in-out infinite; }
    .readp  { animation: read 3.6s ease-in-out infinite; }
    .sweepp { animation: sweep 3.2s ease-in-out infinite; }
    .w1     { animation: ping 2.6s ease-in-out infinite; }
    .w2     { animation: ping 2.6s ease-in-out .34s infinite; }
    .l1     { animation: lit 4.8s ease-in-out infinite; }
    .l2     { animation: lit 4.8s ease-in-out 1.6s infinite; }
    .l3     { animation: lit 4.8s ease-in-out 3.2s infinite; }
    .s1     { animation: steam 3.8s ease-in-out infinite; }
    .s2     { animation: steam 3.8s ease-in-out 1.9s infinite; }
    .z1     { animation: rise 2.8s ease-in-out infinite; }
    .z2     { animation: rise 2.8s ease-in-out .5s infinite; }
    .z3     { animation: rise 2.8s ease-in-out 1s infinite; }
    .drift  { transform-box: fill-box; transform-origin: 50% 100%;
              animation: drift 4.6s ease-in-out infinite; }
    @keyframes bob   { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-3px); } }
    @keyframes blink { 0%, 44%, 50%, 100% { transform: scaleY(1); } 47% { transform: scaleY(.08); } }
    @keyframes read  { 0% { transform: translateX(-2.4px); } 72% { transform: translateX(2.4px); }
                       86%, 100% { transform: translateX(-2.4px); } }
    @keyframes sweep { 0%, 100% { transform: translateX(-3px); } 50% { transform: translateX(3px); } }
    @keyframes ping  { 0%, 100% { opacity: 0; } 12%, 42% { opacity: .85; } 58% { opacity: 0; } }
    @keyframes lit   { 0%, 28% { opacity: .95; } 34%, 100% { opacity: .3; } }
    @keyframes steam { 0% { opacity: 0; transform: translateY(2px); } 30%, 55% { opacity: .7; }
                       100% { opacity: 0; transform: translateY(-6px); } }
    @keyframes rise  { 0% { opacity: 0; transform: translate(0, 4px); } 30%, 70% { opacity: 1; }
                       100% { opacity: 0; transform: translate(4px, -8px); } }
    @keyframes drift { 0%, 100% { transform: rotate(-3deg); } 50% { transform: rotate(3deg); } }
"""

REDUCED = """
    @media (prefers-reduced-motion: reduce) {
      * { animation: none !important; }
    }
"""


def eyes(kind: str) -> str:
    """kind: read (pupils down), sweep (pupils centred, tracking), joy, doze, cross."""
    out = []
    for cx in (36, 60):
        if kind == "read":
            inner = f'<g class="readp"><circle class="pupil" cx="{cx}" cy="56.5" r="5"/></g>'
        elif kind == "sweep":
            inner = f'<g class="sweepp"><circle class="pupil" cx="{cx}" cy="52" r="5"/></g>'
        elif kind == "look":
            inner = f'<circle class="pupil" cx="{cx - 3}" cy="56" r="5"/>'
        elif kind == "up":
            inner = f'<circle class="pupil" cx="{cx + 2.5}" cy="48" r="5"/>'
        elif kind == "side":
            inner = f'<g class="readp"><circle class="pupil" cx="{cx}" cy="55" r="5"/></g>'
        elif kind == "joy":
            inner = f'<path class="lids" d="M{cx-6} 54 a6.5 6.5 0 0 1 12 0"/>'
        elif kind == "doze":
            inner = f'<path class="lids" d="M{cx-7} 51 a7.5 5 0 0 0 14 0"/>'
        else:
            inner = f'<path class="cross" d="M{cx-5.5} 46.5 L{cx+5.5} 57.5 M{cx+5.5} 46.5 L{cx-5.5} 57.5"/>'
        iris = "iris"
        blink = kind in ("read", "sweep", "look", "up", "side")
        body = f'<circle class="{iris}" cx="{cx}" cy="52" r="11"/>{inner}'
        out.append(f'<g class="lid">{body}</g>' if blink else body)
    return "".join(out)


PAGE = """<g transform="rotate(-5 48 75.5)">
        <rect class="page" x="25" y="67" width="46" height="17" rx="3"/>
        <rect class="line l1" x="31" y="70.6" width="34" height="2.2" rx="1.1"/>
        <rect class="line l2" x="31" y="74.4" width="34" height="2.2" rx="1.1"/>
        <rect class="line l3" x="31" y="78.2" width="22" height="2.2" rx="1.1"/>
      </g>"""

WAVES = """<path class="wave w1" d="M41.04 11.12 A8.5 8.5 0 0 1 54.96 11.12"/>
      <path class="wave w2" d="M36.94 8.25 A13.5 13.5 0 0 1 59.06 8.25"/>"""

MUG = """<g><ellipse class="shadow" cx="91.5" cy="90" rx="9.4" ry="2.6"/>
      <path class="steam s1" d="M87.6 63 c-3 -3.2 3 -5.2 0 -8.6"/>
      <path class="steam s2" d="M95 62 c-3 -3.2 3 -5.2 0 -8.6"/>
      <path class="handle" d="M99.6 72.6 a5 5 0 0 1 0 9.6"/>
      <path class="mug" d="M83 68 h17 l-1.9 17.4 a3.2 3.2 0 0 1 -3.2 3.1 h-6.8 a3.2 3.2 0 0 1 -3.2 -3.1 Z"/>
      <ellipse class="brew" cx="91.5" cy="68" rx="8.5" ry="2.5"/></g>"""

ZZZ = """<g class="z1"><text class="z" x="80" y="41" font-size="9">z</text></g>
      <g class="z2"><text class="z" x="87" y="32" font-size="11">z</text></g>
      <g class="z3"><text class="z" x="94" y="22" font-size="13">z</text></g>"""


def probe(x: float, y: float, s: float = 1.0, mood: str = "read",
          page: bool = False, waves: bool = False, mug: bool = False,
          zzz: bool = False, shadow: bool = True) -> str:
    """The character in its 96-unit box, placed with its box top-left at (x, y)."""
    if mood == "lost":
        body = f"""<g class="drift">
      <path class="dimst" d="M48 26 q-2 -6 -8 -7"/><circle class="dimbe" cx="39" cy="18" r="5"/>
      <rect class="dim" x="17" y="27" width="62" height="54" rx="19"/>{eyes("cross")}</g>"""
        sh = '<ellipse class="dimbe" opacity=".45" cx="48" cy="90" rx="20" ry="4"/>'
    else:
        body = f"""<g class="rig">
      {WAVES if waves else ""}
      <path class="stalk" d="M48 26 V19"/><circle class="beacon" cx="48" cy="16" r="5"/>
      <rect class="hull" x="17" y="27" width="62" height="54" rx="19"/>
      {eyes(mood)}
      {PAGE if page else ""}
      {ZZZ if zzz else ""}
    </g>"""
        sh = '<ellipse class="shadow" cx="48" cy="90" rx="20" ry="4"/>'
    return f"""<g transform="translate({x} {y}) scale({s})">
    {sh if shadow else ""}{body}{MUG if mug else ""}
  </g>"""


def human(x: float, y: float, s: float = 1.0) -> str:
    return f"""<g transform="translate({x} {y}) scale({s})">
    <ellipse class="shadow" cx="48" cy="90" rx="18" ry="4"/>
    <g class="rig"><circle class="hull" cx="48" cy="33" r="14.5"/>
    <path class="hull" d="M21 76 a27 27 0 0 1 54 0 Z"/></g></g>"""


def svg(w: int, h: int, label: str, css: str, body: str, vb: str | None = None) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{vb or f'0 0 {w} {h}'}" role="img" aria-label="{label}">
  <style>{BASE_CSS}{css}{REDUCED}  </style>
{body}
</svg>
"""


def write(folder: Path, name: str, src: str) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    for suffix, pal in (("", LIGHT), ("-dark", DARK)):
        text = Template(src).substitute(pal, MONO=MONO, SANS=SANS)
        (folder / f"{name}{suffix}.svg").write_text(text)
