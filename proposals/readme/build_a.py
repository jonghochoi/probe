"""Proposal A — Stage: one wide hero, pill actions, a 2x2 track grid."""
from pathlib import Path
from common import probe, svg, write

OUT = Path(__file__).parent / "A-stage"

# ── hero ──────────────────────────────────────────────────────────────
FEED_X, FEED_TOP, FEED_BOT, ROW = 690, 46, 300, 34
N = 8                                   # rows per loop; the loop is N*ROW tall
MARKED = {2, 6}


def feed_rows(offset: int) -> str:
    out = []
    for i in range(N):
        y = offset + i * ROW
        if i in MARKED:
            out.append(f'''<rect x="{FEED_X}" y="{y}" width="150" height="24" rx="5" class="hit"/>
      <circle cx="{FEED_X+13}" cy="{y+12}" r="4" class="dot"/>
      <rect x="{FEED_X+24}" y="{y+7}" width="96" height="3.4" rx="1.7" class="hitl"/>
      <rect x="{FEED_X+24}" y="{y+14}" width="62" height="3.4" rx="1.7" class="hitl" opacity=".5"/>''')
        else:
            w1, w2 = (110, 70) if i % 2 else (96, 84)
            out.append(f'''<rect x="{FEED_X}" y="{y}" width="150" height="24" rx="5" class="miss"/>
      <rect x="{FEED_X+12}" y="{y+7}" width="{w1}" height="3.4" rx="1.7" class="missl"/>
      <rect x="{FEED_X+12}" y="{y+14}" width="{w2}" height="3.4" rx="1.7" class="missl"/>''')
    return "\n      ".join(out)


HERO_CSS = """
    .ground { fill: ${CARD}; }
    .edge   { fill: none; stroke: ${ACCENT}; }
    .eyebrow{ fill: ${DEEP}; font: 11px ${MONO}; letter-spacing: 2.6px; }
    .head   { fill: ${INK}; font: 700 42px ${SANS}; letter-spacing: -1px; }
    .claim  { fill: ${ACCENT}; font: 700 24px ${SANS}; letter-spacing: -.3px; }
    .sub    { fill: ${MUTED}; font: 15px ${SANS}; }
    .tag    { fill: ${MUTED}; font: 10px ${MONO}; letter-spacing: 1.6px; }
    .miss   { fill: ${GHOST}; }
    .missl  { fill: ${MUTED}; opacity: .28; }
    .hit    { fill: ${IRIS}; stroke: ${ACCENT}; stroke-width: 1.5; }
    .hitl   { fill: ${DEEP}; }
    .dot    { fill: ${ACCENT}; }
    .fade0  { stop-color: ${CARD}; stop-opacity: 1; }
    .fade1  { stop-color: ${CARD}; stop-opacity: 0; }
    .wire   { fill: none; stroke: ${ACCENT}; stroke-width: 1.6; stroke-dasharray: 4 5;
              animation: march 1.2s linear infinite; }
    .feed   { animation: scroll 18s linear infinite; }
    .scan   { fill: ${ACCENT}; opacity: .10; animation: scan 4.5s ease-in-out infinite; }
    @keyframes scroll { from { transform: translateY(0); } to { transform: translateY(-272px); } }
    @keyframes march  { to { stroke-dashoffset: -18; } }
    @keyframes scan   { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(200px); } }
"""

hero = svg(880, 340, "PROBE — Stop drowning in arXiv. PROBE marks the target.", HERO_CSS, f'''
  <defs>
    <clipPath id="win"><rect x="{FEED_X-10}" y="{FEED_TOP}" width="180" height="{FEED_BOT-FEED_TOP}"/></clipPath>
    <linearGradient id="ft" x1="0" y1="0" x2="0" y2="1"><stop class="fade0" offset="0"/><stop class="fade1" offset="1"/></linearGradient>
    <linearGradient id="fb" x1="0" y1="1" x2="0" y2="0"><stop class="fade0" offset="0"/><stop class="fade1" offset="1"/></linearGradient>
  </defs>
  <rect class="ground" width="880" height="340" rx="12"/>
  <rect class="edge" x=".5" y=".5" width="879" height="339" rx="11.5"/>

  <text class="eyebrow" x="48" y="66">PROBE · RESEARCH SCOUT</text>
  <text class="head" x="46" y="124">Stop drowning</text>
  <text class="head" x="46" y="174">in arXiv.</text>
  <text class="claim" x="47" y="222">PROBE marks the target.</text>
  <text class="sub" x="48" y="264">Dexterous-manipulation papers, scouted on a schedule —</text>
  <text class="sub" x="48" y="286">and retold in Korean when you name one.</text>

  <text class="tag" x="{FEED_X}" y="34">ARXIV · cs.RO + cs.LG</text>
  <g clip-path="url(#win)">
    <g class="feed">
      {feed_rows(FEED_TOP + 4)}
      {feed_rows(FEED_TOP + 4 + N * ROW)}
    </g>
    <rect class="scan" x="{FEED_X-6}" y="{FEED_TOP}" width="162" height="40" rx="6"/>
    <rect x="{FEED_X-10}" y="{FEED_TOP}" width="180" height="46" fill="url(#ft)"/>
    <rect x="{FEED_X-10}" y="{FEED_BOT-46}" width="180" height="46" fill="url(#fb)"/>
  </g>
  <text class="tag" x="850" y="322" text-anchor="end">50–100 A DAY → 3–5 A WEEK</text>

  <path class="wire" d="M{FEED_X-8} 173 C 660 173, 650 232, 628 236"/>
  {probe(470, 118, 1.62, "read", page=True, mug=True)}
''')

# ── actions ───────────────────────────────────────────────────────────
BTN_CSS = """
    .fill  { fill: ${ACCENT}; }
    .ring  { fill: ${CARD}; stroke: ${ACCENT}; stroke-width: 1.5; }
    .on    { fill: ${IRIS}; font: 600 15px ${SANS}; }
    .off   { fill: ${DEEP}; font: 600 15px ${SANS}; }
    .arr   { fill: none; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
    .nudge { animation: nudge 1.8s ease-in-out infinite; }
    @keyframes nudge { 0%, 100% { transform: translateX(0); } 50% { transform: translateX(3px); } }
"""
read_btn = svg(276, 48, "Open the reading site", BTN_CSS, '''
  <rect class="fill" x="1" y="1" width="274" height="46" rx="23"/>
  <text class="on" x="28" y="29">Open the reading site</text>
  <g class="nudge"><path class="arr" stroke="${IRIS}" d="M230 24h18m-6-6 6 6-6 6"/></g>''')
setup_btn = svg(250, 48, "Schedule the scouting routine", BTN_CSS, '''
  <rect class="ring" x="1" y="1" width="248" height="46" rx="23"/>
  <text class="off" x="28" y="29">Schedule scouting</text>
  <path class="arr" stroke="${ACCENT}" d="M206 24h18m-6-6 6 6-6 6"/>''')

if __name__ == "__main__":
    write(OUT, "hero", hero)
    write(OUT, "btn-read", read_btn)
    write(OUT, "btn-setup", setup_btn)
