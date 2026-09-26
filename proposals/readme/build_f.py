"""Proposal F — Bento: every track as a tile on one board."""
from pathlib import Path
from common import probe, human, svg, write
from build_e import pages, screen, thought

OUT = Path(__file__).parent / "F-bento"

CSS = """
    .tile  { fill: ${CARD}; stroke: ${BORDER}; stroke-width: 1.2; }
    .hot   { fill: ${ACCENT}; }
    .eb    { fill: ${DEEP}; font: 10.5px ${MONO}; letter-spacing: 2px; }
    .ti    { fill: ${INK}; font: 700 19px ${SANS}; letter-spacing: -.3px; }
    .tis   { fill: ${INK}; font: 700 16px ${SANS}; }
    .sb    { fill: ${MUTED}; font: 13px ${SANS}; }
    .path  { fill: ${INK}; font: 700 12px ${MONO}; }
    .note  { fill: ${MUTED}; font: 12px ${MONO}; }
    .ebh   { fill: ${IRIS}; opacity: .8; font: 10.5px ${MONO}; letter-spacing: 2px; }
    .q     { fill: ${IRIS}; font: 700 15.5px ${SANS}; }
    .dot   { fill: ${BORDER}; }
    .keep  { fill: ${BORDER}; animation: keep 6s ease-in-out infinite; }
    .k2    { animation-delay: .9s; }
    .k3    { animation-delay: 1.8s; }
    .scanb { fill: ${ACCENT}; opacity: .08; animation: scanx 6s ease-in-out infinite; }
    .lock  { fill: none; stroke: ${DEEP}; stroke-width: 2.4; stroke-linecap: round; }
    .lockb { fill: ${DEEP}; }
    .doc   { fill: ${IRIS}; stroke: ${BORDER}; stroke-width: 1.5; }
    .frame { fill: none; stroke: ${BORDER}; stroke-width: 1; }
    .dl    { fill: ${MUTED}; opacity: .3; }
    .qm    { transform-box: fill-box; transform-origin: 50% 50%; animation: qpop 4.5s ease-in-out infinite; }
    .q2    { animation-delay: .5s; }
    .q3    { animation-delay: 1s; }
    @keyframes keep  { 0%, 25% { fill: ${BORDER}; } 35%, 85% { fill: ${ACCENT}; } 100% { fill: ${BORDER}; } }
    @keyframes scanx { 0%, 100% { transform: translateX(0); } 50% { transform: translateX(210px); } }
    @keyframes qpop  { 0%, 10% { opacity: .35; } 20%, 80% { opacity: 1; } 100% { opacity: .35; } }
""" + open(Path(__file__).parent / "build_e.py").read().split('CSS = """')[1].split('"""')[0]

G = 16


def tile(x, y, w, h, cls="tile"):
    return f'<rect class="{cls}" x="{x+.6}" y="{y+.6}" width="{w-1.2}" height="{h-1.2}" rx="14"/>'


b = []
# Scouting — the big tile
b.append(tile(0, 0, 432, 300))
b.append('<text class="eb" x="26" y="38">SCOUTING · SCHEDULED</text>')
b.append('<text class="ti" x="26" y="66">The day\'s arXiv, narrowed to 3–5</text>')
b.append('<text class="sb" x="26" y="88">one pillar per run, scored against your open decisions</text>')
KEEP = {(1, 1): "", (6, 3): " k2", (4, 0): " k3"}
for c in range(9):
    for r in range(5):
        cls = "keep" + KEEP[(c, r)] if (c, r) in KEEP else "dot"
        b.append(f'<circle class="{cls}" cx="{178 + c * 26}" cy="{130 + r * 26}" r="5"/>')
b.append('<rect class="scanb" x="164" y="114" width="28" height="136" rx="10"/>')
b.append(probe(22, 116, 1.28, "sweep", waves=True))
b.append('<text class="path" x="26" y="280">scouting/P#/&lt;date&gt;.md</text>')

# Analysis — wide
x0 = 432 + G
b.append(tile(x0, 0, 432, 142))
b.append(probe(x0 + 18, 22, 1.0, "read", page=True))
b.append(f'<text class="eb" x="{x0+140}" y="42">ANALYSIS · /analyze</text>')
b.append(f'<text class="ti" x="{x0+140}" y="70">One paper, in Korean</text>')
b.append(f'<text class="sb" x="{x0+140}" y="92">from the arXiv HTML original — a 요약</text>')
b.append(f'<text class="sb" x="{x0+140}" y="110">tab and the full re-telling</text>')

# Comparison and presentation — small
y1 = 142 + G
w = (432 - G) / 2
for i, (eb, ti, sb, art) in enumerate((
        ("COMPARISON", "Where they part", ("2–3 rewrites,", "one question"),
         lambda x, y: probe(x, y, .74, "side") + pages(x, y, .74)),
        ("PRESENTATION", "Slide by slide", ("a speaker essay", "for each one"),
         lambda x, y: screen(x, y, .74) + probe(x - 8, y, .74, "look")))):
    x = x0 + i * (w + G)
    b.append(tile(x, y1, w, 142))
    b.append(f'<text class="eb" x="{x+20}" y="{y1+32}">{eb}</text>')
    b.append(f'<text class="tis" x="{x+20}" y="{y1+56}">{ti}</text>')
    b.append(f'<text class="sb" x="{x+20}" y="{y1+80}">{sb[0]}</text>')
    b.append(f'<text class="sb" x="{x+20}" y="{y1+98}">{sb[1]}</text>')
    b.append(art(x + w - 84, y1 + 64))

# Row 3 — context, ideation, the three questions
y2 = 300 + G
b.append(tile(0, y2, 432, 142))
b.append(human(18, y2 + 30, .9))
b.append(f'<rect class="doc" x="116" y="{y2+30}" width="54" height="68" rx="5"/><rect class="frame" x="120" y="{y2+34}" width="46" height="60" rx="3"/>')
for k in range(3):
    b.append(f'<rect class="dl" x="126" y="{y2+44+k*10}" width="{32 - 8*(k==2)}" height="3" rx="1.5"/>')
b.append(f'<path class="lock" d="M152 {y2+92} v-6 a7 7 0 0 1 14 0 v6"/><rect class="lockb" x="147" y="{y2+91}" width="24" height="18" rx="4"/>')
b.append(f'<text class="eb" x="196" y="{y2+42}">CONTEXT · YOURS</text>')
b.append(f'<text class="tis" x="196" y="{y2+68}">It reads. It never writes.</text>')
b.append(f'<text class="sb" x="196" y="{y2+90}">MASTER.md + one P#.md per</text>')
b.append(f'<text class="sb" x="196" y="{y2+108}">pillar — it proposes, you decide</text>')

x = x0
b.append(tile(x, y2, w, 142))
b.append(f'<text class="eb" x="{x+20}" y="{y2+32}">IDEATION · /ideate</text>')
b.append(f'<text class="tis" x="{x+20}" y="{y2+56}">Untried ideas</text>')
b.append(f'<text class="sb" x="{x+20}" y="{y2+80}">in chat,</text>')
b.append(f'<text class="sb" x="{x+20}" y="{y2+98}">no file written</text>')
b.append(probe(x + w - 108, y2 + 66, .7, "up") + thought(x + w - 108, y2 + 66, .7))

x = x0 + w + G
b.append(tile(x, y2, w, 142, "hot"))
b.append(f'<text class="ebh" x="{x+20}" y="{y2+32}">EVERY PAPER, ASKED</text>')
for k, qq in enumerate(("Is it actually new?", "Real hardware?", "Can I get the code?")):
    b.append(f'<g class="qm q{k+1}"><text class="q" x="{x+20}" y="{y2+64+k*26}">{qq}</text></g>')

bento = svg(880, 458, "PROBE's tracks as tiles — scouting, analysis, comparison, presentation, ideation — the human-owned context, and the three questions every paper is asked", CSS, "\n  ".join(b))

if __name__ == "__main__":
    write(OUT, "bento", bento)
