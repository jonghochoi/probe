"""Proposal E — Fold: one strip of five tracks, everything else folded away."""
from pathlib import Path
from common import probe, human, svg, write

OUT = Path(__file__).parent / "E-fold"
COL = 176

CSS = """
    .name { fill: ${INK}; font: 700 15px ${MONO}; }
    .cmd  { fill: ${DEEP}; font: 12px ${MONO}; }
    .when { fill: ${MUTED}; font: 10px ${MONO}; letter-spacing: 1.4px; }
    .pg   { fill: ${IRIS}; stroke: ${DEEP}; stroke-width: 2; }
    .up   { animation: pan 3s ease-in-out infinite; }
    .dn   { animation: pan 3s ease-in-out 1.5s infinite; }
    .scr  { fill: ${CARD}; stroke: ${BORDER}; stroke-width: 2; }
    .band { fill: ${ACCENT}; opacity: .25; }
    .bd1  { animation: lit 3.6s ease-in-out infinite; }
    .bd2  { animation: lit 3.6s ease-in-out 1.2s infinite; }
    .bd3  { animation: lit 3.6s ease-in-out 2.4s infinite; }
    .bub  { fill: ${IRIS}; stroke: ${DEEP}; stroke-width: 1.6; }
    .bdot { fill: ${DEEP}; opacity: .2; }
    .t1   { animation: think 2.4s ease-in-out infinite; }
    .t2   { animation: think 2.4s ease-in-out .3s infinite; }
    .t3   { animation: think 2.4s ease-in-out .6s infinite; }
    .sep  { stroke: ${SOFT}; stroke-width: 1.5; }
    @keyframes pan   { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
    @keyframes think { 0%, 100% { opacity: .2; } 40% { opacity: 1; } }
"""


def pages(x, y, s):
    return f'''<g transform="translate({x} {y}) scale({s})">
      <g class="up"><rect class="pg" x="20" y="66" width="26" height="18" rx="3"/><rect class="line" x="25" y="71" width="16" height="2.2"/><rect class="line" x="25" y="76" width="12" height="2.2"/></g>
      <g class="dn"><rect class="pg" x="50" y="66" width="26" height="18" rx="3"/><rect class="line" x="55" y="71" width="16" height="2.2"/><rect class="line" x="55" y="76" width="12" height="2.2"/></g></g>'''


def screen(x, y, s):
    return f'''<g transform="translate({x} {y}) scale({s})">
      <rect class="scr" x="56" y="-4" width="46" height="36" rx="3"/>
      <rect class="band bd1" x="62" y="3" width="34" height="5" rx="1.5"/>
      <rect class="band bd2" x="62" y="12" width="34" height="5" rx="1.5"/>
      <rect class="band bd3" x="62" y="21" width="22" height="5" rx="1.5"/></g>'''


def thought(x, y, s):
    return f'''<g transform="translate({x} {y}) scale({s})">
      <circle class="bub" cx="80" cy="26" r="2.6"/><circle class="bub" cx="87" cy="16" r="4"/>
      <ellipse class="bub" cx="104" cy="2" rx="16" ry="11"/>
      <circle class="bdot t1" cx="96" cy="2" r="2.6"/><circle class="bdot t2" cx="104" cy="2" r="2.6"/><circle class="bdot t3" cx="112" cy="2" r="2.6"/></g>'''


S = .92
TRACKS = [
    ("scouting",     "scheduled",   lambda x, y: probe(x, y, S, "sweep", waves=True)),
    ("analysis",     "/analyze",    lambda x, y: probe(x, y, S, "read", page=True)),
    ("comparison",   "/compare",    lambda x, y: probe(x, y, S, "side") + pages(x, y, S)),
    ("presentation", "/present",    lambda x, y: screen(x, y, S) + probe(x - 10, y, S, "look") + human(x - 32, y + 44, .42)),
    ("ideation",     "/ideate",     lambda x, y: probe(x, y, S, "up") + thought(x, y, S)),
]

parts = []
for i, (name, cmd, draw) in enumerate(TRACKS):
    cx = i * COL + COL / 2
    parts.append(draw(cx - 44 * S - 4, 26))
    parts.append(f'<text class="name" x="{cx}" y="156" text-anchor="middle">{name}</text>')
    parts.append(f'<text class="cmd" x="{cx}" y="178" text-anchor="middle">{cmd}</text>')
    if i:
        parts.append(f'<line class="sep" x1="{i*COL}" y1="140" x2="{i*COL}" y2="184"/>')

strip = svg(880, 196, "Five tracks — scouting (scheduled), analysis (/analyze), comparison (/compare), presentation (/present), ideation (/ideate)", CSS, "\n  ".join(parts))

if __name__ == "__main__":
    write(OUT, "tracks", strip)
