"""Proposal G — Stage + Fold: A's hero and actions over E's track strip,
with every detail folded away below."""
from pathlib import Path
from common import svg, write
from build_a import hero, read_btn, setup_btn
from build_e import CSS as STRIP_CSS, TRACKS, COL, S

OUT = Path(__file__).parent / "G-stage-fold"

NOTES = ["3–5 papers a run", "one paper, in Korean", "where 2–3 part",
         "a paper as a talk", "in chat, no file"]

CSS = STRIP_CSS + """
    .what { fill: ${MUTED}; font: 12.5px ${SANS}; }
"""

parts = []
for i, ((name, cmd, draw), note) in enumerate(zip(TRACKS, NOTES)):
    cx = i * COL + COL / 2
    parts.append(draw(cx - 44 * S - 4, 20))
    parts.append(f'<text class="name" x="{cx}" y="150" text-anchor="middle">{name}</text>')
    parts.append(f'<text class="cmd" x="{cx}" y="171" text-anchor="middle">{cmd}</text>')
    parts.append(f'<text class="what" x="{cx}" y="192" text-anchor="middle">{note}</text>')
    if i:
        parts.append(f'<line class="sep" x1="{i*COL}" y1="134" x2="{i*COL}" y2="198"/>')

strip = svg(880, 206, "Five tracks — scouting (scheduled, 3–5 papers a run), analysis (/analyze, one paper in Korean), comparison (/compare, where 2–3 papers part), presentation (/present, a paper as a talk), ideation (/ideate, in chat, no file)", CSS, "\n  ".join(parts))

if __name__ == "__main__":
    write(OUT, "hero", hero)
    write(OUT, "btn-read", read_btn)
    write(OUT, "btn-setup", setup_btn)
    write(OUT, "tracks", strip)
