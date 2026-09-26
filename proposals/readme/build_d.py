"""Proposal D — Storyboard: one run as four panels, left to right."""
from pathlib import Path
from common import probe, human, svg, write

OUT = Path(__file__).parent / "D-storyboard"
PW, GAP = 205, 20
PX = [i * (PW + GAP) for i in range(4)]
CYCLE = 12

CAPS = [
    ("01 · ARXIV",    "100 papers land",       "cs.RO + cs.LG, every day"),
    ("02 · SCOUTING", "One pillar, one sweep", "scored against your decisions"),
    ("03 · REPORT",   "3–5 reach your repo",   "you read it, you decide"),
    ("04 · /analyze", "You name one",          "it comes back in Korean"),
]

CSS = f"""
    .ground {{ stroke: ${{SOFT}}; stroke-width: 2; stroke-linecap: round; }}
    .step   {{ fill: ${{DEEP}}; font: 11px ${{MONO}}; letter-spacing: 1.8px; }}
    .ttl    {{ fill: ${{INK}}; font: 600 16px ${{SANS}}; }}
    .cap    {{ fill: ${{MUTED}}; font: 13px ${{SANS}}; }}
    .sheet  {{ fill: ${{IRIS}}; stroke: ${{BORDER}}; stroke-width: 1.5; }}
    .sl     {{ fill: ${{MUTED}}; opacity: .3; }}
    .fall   {{ animation: fall 2.8s cubic-bezier(.5,0,.8,.6) infinite; }}
    .fall2  {{ animation: fall 2.8s cubic-bezier(.5,0,.8,.6) 1.4s infinite; }}
    .dotf   {{ fill: ${{BORDER}}; }}
    .dotk   {{ fill: ${{BORDER}}; animation: pick 3.6s ease-in-out infinite; }}
    .k2     {{ animation-delay: .6s; }}
    .k3     {{ animation-delay: 1.2s; }}
    .doc    {{ fill: ${{CARD}}; stroke: ${{ACCENT}}; stroke-width: 1.5; }}
    .dname  {{ fill: ${{INK}}; font: 700 10px ${{MONO}}; }}
    .medal  {{ transform-box: fill-box; transform-origin: 50% 50%; animation: pop 4s ease-in-out infinite; }}
    .m1     {{ fill: ${{ACCENT}}; }}
    .m2     {{ fill: ${{DEEP}}; animation-delay: .4s; }}
    .m3     {{ fill: ${{DIM}}; animation-delay: .8s; }}
    .ml     {{ fill: ${{MUTED}}; opacity: .35; }}
    .track  {{ fill: ${{SOFT}}; }}
    .now    {{ fill: ${{ACCENT}}; animation: now {CYCLE}s steps(1, end) infinite; }}
    @keyframes fall {{ 0% {{ transform: translateY(-84px); opacity: 0; }} 15% {{ opacity: 1; }}
                      60%, 82% {{ transform: translateY(0); opacity: 1; }} 100% {{ transform: translateY(0); opacity: 0; }} }}
    @keyframes pick {{ 0%, 20% {{ fill: ${{BORDER}}; }} 30%, 80% {{ fill: ${{ACCENT}}; }} 100% {{ fill: ${{BORDER}}; }} }}
    @keyframes pop  {{ 0%, 15% {{ transform: scale(0); }} 25%, 85% {{ transform: scale(1); }} 100% {{ transform: scale(0); }} }}
    @keyframes now  {{ 0% {{ transform: translateX(0); }} 25% {{ transform: translateX({PW+GAP}px); }}
                      50% {{ transform: translateX({2*(PW+GAP)}px); }} 75%, 100% {{ transform: translateX({3*(PW+GAP)}px); }} }}
"""


def sheet(x, y, cls=""):
    return f'''<g class="{cls}"><rect class="sheet" x="{x}" y="{y}" width="30" height="38" rx="3"/>
      <rect class="sl" x="{x+6}" y="{y+8}" width="18" height="2.4" rx="1.2"/>
      <rect class="sl" x="{x+6}" y="{y+14}" width="18" height="2.4" rx="1.2"/>
      <rect class="sl" x="{x+6}" y="{y+20}" width="12" height="2.4" rx="1.2"/></g>'''


x = PX[0]
p1 = "".join(sheet(x + 120 + dx, 118 - dy) for dx, dy in ((0, 0), (14, 4), (4, 12), (22, 16), (10, 26)))
p1 += sheet(x + 128, 84, "fall") + sheet(x + 146, 80, "fall2")
p1 += probe(x + 2, 66, .8, "doze", zzz=True)

x = PX[1]
dots = []
KEEP = {(1, 0): "", (3, 2): " k2", (2, 3): " k3"}
for c in range(5):
    for r in range(4):
        cls = "dotk" + KEEP[(c, r)] if (c, r) in KEEP else "dotf"
        dots.append(f'<circle class="{cls}" cx="{x + 112 + c * 20}" cy="{80 + r * 20}" r="4.5"/>')
p2 = "".join(dots) + probe(x + 2, 66, .8, "sweep", waves=True)

x = PX[2]
p3 = human(x + 2, 72, .74)
p3 += f'<rect class="doc" x="{x+82}" y="40" width="118" height="124" rx="6"/>'
p3 += f'<text class="dname" x="{x+94}" y="62">P2/&lt;date&gt;.md</text>'
for i, (m, w) in enumerate((("m1", 64), ("m2", 56), ("m3", 48))):
    y = 86 + i * 26
    p3 += f'<circle class="medal {m}" cx="{x+102}" cy="{y}" r="7"/><rect class="ml" x="{x+116}" y="{y-3}" width="{w}" height="6" rx="3"/>'

x = PX[3]
p4 = probe(x + 38, 62, 1.0, "read", page=True, mug=True)

body = [p1, p2, p3, p4]
for i, (s, t, c) in enumerate(CAPS):
    x = PX[i]
    body.append(f'<line class="ground" x1="{x}" y1="170" x2="{x+PW}" y2="170"/>')
    body.append(f'<text class="step" x="{x}" y="200">{s}</text>')
    body.append(f'<text class="ttl" x="{x}" y="224">{t}</text>')
    body.append(f'<text class="cap" x="{x}" y="246">{c}</text>')
body.append(f'<rect class="track" x="0" y="270" width="880" height="3" rx="1.5"/>')
body.append(f'<rect class="now" x="0" y="270" width="{PW}" height="3" rx="1.5"/>')

story = svg(880, 280, "One PROBE run: 100 papers land; one pillar is swept; 3–5 reach your repo; you name one and it comes back in Korean", CSS, "\n  ".join(body))

if __name__ == "__main__":
    write(OUT, "story", story)
