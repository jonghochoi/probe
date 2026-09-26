"""Proposal B — Session: a terminal replaying two commands, the probe peeking in."""
from pathlib import Path
from common import probe, svg, write

OUT = Path(__file__).parent / "B-session"

W, H = 880, 404
TOP = 70                 # window top edge — the probe sits behind it
X0, Y0, STEP = 40, 132, 27
CYCLE = 16               # seconds

# (kind, parts, start %) — kind "cmd" types out, "out" appears whole.
LINES = [
    ("cmd", [("p", "❯ "), ("c", "/analyze 2609.15910")], 2),
    ("out", [("k", "  reads    "), ("v", "context/MASTER.md")], 14),
    ("out", [("k", "  fetches  "), ("v", "arxiv.org/html/2609.15910")], 18),
    ("out", [("k", "  writes   "), ("v", "analysis/2609.15910.md"), ("a", "   SlipSense")], 24),
    ("out", [("ok", "  ✓ "), ("v", "요약 + 본문, live on the reading site")], 30),
    ("cmd", [("p", "❯ "), ("c", "/compare 2606.17055 2607.07287 2608.01824")], 40),
    ("out", [("k", "  writes   "), ("v", "comparison/fast-loop-without-vision.md")], 60),
    ("out", [("ok", "  ✓ "), ("v", "촉각 루프가 눈을 감은 채 행동 청크에 무엇을 할 수 있나")], 66),
]
END = 92


def line_css(i: int, kind: str, start: float, n: int) -> str:
    if kind == "cmd":
        dur = max(6, n * .45)
        done = start + dur
        steps = n
        return f"""
    .c{i} {{ animation: t{i} {CYCLE}s steps(1, end) infinite; }}
    .c{i} .cov {{ animation: k{i} {CYCLE}s linear infinite; }}
    @keyframes t{i} {{ 0%, {start}% {{ opacity: 0; }} {start+.01}%, {END}% {{ opacity: 1; }} {END+2}%, 100% {{ opacity: 0; }} }}
    @keyframes k{i} {{ 0%, {start+2}% {{ transform: translateX(0); animation-timing-function: steps({steps}, end); }}
                     {done}% {{ transform: translateX({steps * 9.03:.1f}px); }}
                     {done+.01}%, 100% {{ transform: translateX({W}px); }} }}"""
    return f"""
    .c{i} {{ animation: t{i} {CYCLE}s steps(1, end) infinite; }}
    @keyframes t{i} {{ 0%, {start}% {{ opacity: 0; }} {start+.01}%, {END}% {{ opacity: 1; }} {END+2}%, 100% {{ opacity: 0; }} }}"""


CSS = """
    .win   { fill: ${TERM}; }
    .edge  { fill: none; stroke: ${ACCENT}; }
    .bar   { fill: ${TERMMUTED}; opacity: .35; }
    .title { fill: ${TERMMUTED}; font: 12px ${MONO}; }
    text.l { font: 15px ${MONO}; white-space: pre; }
    .p     { fill: ${ACCENT}; font-weight: 700; }
    .c     { fill: ${TERMINK}; font-weight: 700; }
    .k     { fill: ${TERMMUTED}; }
    .v     { fill: ${TERMINK}; }
    .a     { fill: ${ACCENT}; }
    .ok    { fill: ${ACCENT}; font-weight: 700; }
    .cov   { fill: ${TERM}; }
    .cur   { fill: ${ACCENT}; animation: cur 1s steps(1, end) infinite; }
    @keyframes cur { 0%, 50% { opacity: 1; } 51%, 100% { opacity: 0; } }
""" + "".join(line_css(i, k, s, sum(len(t) for c, t in parts if c != "p"))
              for i, (k, parts, s) in enumerate(LINES))

rows = []
for i, (kind, parts, _) in enumerate(LINES):
    y = Y0 + i * STEP + (STEP // 2 if i >= 5 else 0)
    spans = "".join(f'<tspan class="{c}">{t}</tspan>' for c, t in parts)
    cov = f'<rect class="cov" x="{X0+16}" y="{y-18}" width="{W}" height="24"/>' if kind == "cmd" else ""
    rows.append(f'<g class="c{i}"><text class="l" x="{X0}" y="{y}" xml:space="preserve">{spans}</text>{cov}</g>')
last_y = Y0 + len(LINES) * STEP + STEP // 2

term = svg(W, H, "A PROBE session — /analyze writes a Korean rewrite, /compare writes a comparison", CSS, f'''
  <clipPath id="clip"><rect x="0" y="{TOP}" width="{W}" height="{H-TOP}" rx="12"/></clipPath>
  {probe(716, TOP - 68, 1.0, "look", shadow=False, waves=True)}
  <rect class="win" x="0" y="{TOP}" width="{W}" height="{H-TOP}" rx="12"/>
  <rect class="edge" x=".5" y="{TOP+.5}" width="{W-1}" height="{H-TOP-1}" rx="11.5"/>
  <circle class="bar" cx="26" cy="{TOP+22}" r="6"/><circle class="bar" cx="46" cy="{TOP+22}" r="6"/><circle class="bar" cx="66" cy="{TOP+22}" r="6"/>
  <text class="title" x="{W/2}" y="{TOP+26}" text-anchor="middle">claude · ~/probe</text>
  <g clip-path="url(#clip)">
  {chr(10).join("  " + r for r in rows)}
  <text class="l" x="{X0}" y="{last_y}"><tspan class="p">❯ </tspan></text>
  <rect class="cur" x="{X0+20}" y="{last_y-15}" width="9" height="19"/>
  </g>
''')

if __name__ == "__main__":
    write(OUT, "session", term)
