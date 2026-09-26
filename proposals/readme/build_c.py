"""Proposal C — Editorial: the whole argument as three numbers."""
from pathlib import Path
from common import probe, svg, write

OUT = Path(__file__).parent / "C-editorial"

COLS = [  # x, number, class, mood kwargs, label lines
    (24,  "100", "n0", dict(mood="lost"),                       ("papers a day", "on cs.RO + cs.LG")),
    (318, "3–5", "n1", dict(mood="sweep", waves=True),          ("a week that touch", "dexterous hands")),
    (612, "1",   "n2", dict(mood="read", page=True, mug=True),  ("page you finish", "in one sitting, in Korean")),
]

CSS = """
    .num  { font: 700 76px ${MONO}; letter-spacing: -3px; }
    .n0   { fill: ${DIM}; }
    .n1   { fill: ${DEEP}; }
    .n2   { fill: ${ACCENT}; }
    .lab  { fill: ${INK}; font: 600 16px ${SANS}; }
    .sub  { fill: ${MUTED}; font: 14px ${SANS}; }
    .base { fill: ${SOFT}; }
    .bar  { fill: ${ACCENT}; transform-box: fill-box; transform-origin: 0 50%; transform: scaleX(0); }
    .b0   { fill: ${DIM}; animation: fill0 9s ease-in-out infinite; }
    .b1   { fill: ${DEEP}; animation: fill1 9s ease-in-out infinite; }
    .b2   { animation: fill2 9s ease-in-out infinite; }
    .chev { fill: none; stroke: ${ACCENT}; stroke-width: 2.4; stroke-linecap: round; stroke-linejoin: round;
            animation: chev 1.8s ease-in-out infinite; }
    @keyframes fill0 { 0% { transform: scaleX(0); } 18%, 90% { transform: scaleX(1); } 100% { transform: scaleX(0); } }
    @keyframes fill1 { 0%, 22% { transform: scaleX(0); } 40%, 90% { transform: scaleX(1); } 100% { transform: scaleX(0); } }
    @keyframes fill2 { 0%, 44% { transform: scaleX(0); } 62%, 90% { transform: scaleX(1); } 100% { transform: scaleX(0); } }
    @keyframes chev  { 0%, 100% { transform: translateX(0); opacity: .5; } 50% { transform: translateX(4px); opacity: 1; } }
"""

parts = []
for i, (x, num, cls, kw, (l1, l2)) in enumerate(COLS):
    parts.append(probe(x - 8, 6, .78, **kw))
    parts.append(f'<text class="num {cls}" x="{x}" y="170">{num}</text>')
    parts.append(f'<rect class="base" x="{x+2}" y="188" width="236" height="3" rx="1.5"/>')
    parts.append(f'<rect class="bar b{i}" x="{x+2}" y="188" width="236" height="3" rx="1.5"/>')
    parts.append(f'<text class="lab" x="{x+2}" y="220">{l1}</text>')
    parts.append(f'<text class="sub" x="{x+2}" y="242">{l2}</text>')
for cx in (278, 572):
    parts.append(f'<g class="chev"><path class="chev" d="M{cx} 128 l9 9 -9 9"/></g>')

funnel = svg(880, 260, "100 papers a day on cs.RO + cs.LG, 3–5 a week that touch dexterous hands, 1 page you finish in one sitting, in Korean", CSS, "\n  ".join(parts))

if __name__ == "__main__":
    write(OUT, "funnel", funnel)
