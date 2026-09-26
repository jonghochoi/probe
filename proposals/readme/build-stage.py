#!/usr/bin/env python3
"""Draft (`python3 proposals/readme/build-stage.py`): the flow diagram as a single stage holding the whole cast.

Reuses assets/build-flow.py's geometry and inlines every character icon from
assets/ at the spot that carries its meaning, so the README needs no other
character image than the lockup.
"""
import importlib.util
import re
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
ASSETS = OUT.parents[1] / "assets"
spec = importlib.util.spec_from_file_location("bf", ASSETS / "build-flow.py")
bf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bf)

W, H = 880, 372
CARD_X, CARD_W, ROW = 588, 262, 30


def inline(name: str, dark: bool, pfx: str, x: float, y: float, h: float) -> str:
    """Inline an icon file as a nested <svg>, namespacing its classes, ids and keyframes."""
    src = (ASSETS / f"{name}{'-dark' if dark else ''}.svg").read_text()
    style = re.search(r"<style>(.*?)</style>", src, re.S).group(1)
    body = re.sub(r"<svg[^>]*>|</svg>|<style>.*?</style>", "", src, flags=re.S)
    kf = re.findall(r"@keyframes\s+([\w-]+)", style)
    for k in kf:
        style = re.sub(rf"(?<![\w-]){k}(?![\w-])", f"{pfx}{k}", style)
    style = re.sub(r"\.([A-Za-z][\w-]*)", lambda m: f".{pfx}{m.group(1)}", style)
    body = re.sub(r'class="([^"]*)"',
                  lambda m: 'class="' + " ".join(pfx + c for c in m.group(1).split()) + '"', body)
    body = re.sub(r'id="([^"]+)"', lambda m: f'id="{pfx}{m.group(1)}"', body)
    body = re.sub(r"url\(#([^)]+)\)", lambda m: f"url(#{pfx}{m.group(1)})", body)
    w = h * 72 / 96
    return (f'<svg x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" viewBox="12 0 72 96" '
            f'overflow="visible"><style>{style}</style>{body.strip()}</svg>')


def card(x, y, header, rows, dark):
    h = 58 + ROW * (len(rows) - 1)
    out = (f'<rect x="{x}" y="{y}" width="{CARD_W}" height="{h}" rx="10" '
           'fill="{CARD}" stroke="{BORDER}"/>'
           f'<text class="tick" x="{x + 18}" y="{y + 24}">{header}</text>')
    for j, (icon, p) in enumerate(rows):
        track, _, rest = p.rpartition("/")
        by = y + 46 + ROW * j
        out += inline(icon, dark, f"{icon[6:9]}{j}-", x + 14, by - 19, 26)
        out += (f'<text class="path" x="{x + 44}" y="{by}">{track}/'
                f'<tspan class="rest">{rest}</tspan></text>')
    return out


def drawing(dark: bool) -> str:
    A = bf.AXIS
    return f"""
  <rect width="{W}" height="{H}" rx="14" fill="{{CARD}}"/>
  <rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="13.25" fill="none" stroke="{{ACCENT}}"/>

  {inline("human", dark, "hu-", 246, 34, 58)}
  <rect x="288" y="26" width="360" height="82" rx="10" fill="{{CARD}}" stroke="{{BORDER}}"/>
  <rect x="293.5" y="31.5" width="349" height="71" rx="6" fill="none" stroke="{{BORDER_SOFT}}"/>
  <text class="tick" x="308" y="50">CONTEXT · HUMAN-OWNED · READ-ONLY</text>
  <path d="M{A} 60 V96" stroke="{{BORDER}}" stroke-width="1"/>
  <text class="path" x="308" y="76" font-size="13">MASTER.md</text>
  <text class="note" x="308" y="95">global anchor</text>
  <text class="path" x="488" y="76" font-size="13">P#.md</text>
  <text class="note" x="488" y="95">per-pillar decision log</text>
  <path class="wire flow" d="M{A} 122 V138"/>
  {bf.arrow_d(A, 146)}

  <text class="lab" x="44" y="112">ARXIV cs.RO + cs.LG</text>
  {bf.field()}
  {inline("probe-lost", dark, "lo-", 42, 306, 44)}
  <text class="note" x="82" y="330" font-size="10.5">50–100 papers a day</text>
  <text class="note" x="82" y="345" font-size="10.5">skimmed, none remembered</text>

  <path d="M246 124 L392 176 V236 L246 288" fill="{{WASH}}" stroke="{{BORDER}}"
        stroke-width="1.2" stroke-dasharray="5 5" stroke-linejoin="round"/>
  <text class="note" x="266" y="200" font-size="10.5">citation graph ·</text>
  <text class="note" x="266" y="218" font-size="10.5">anti-topics · scoring</text>
  {bf.overlay()}

  {inline("probe-locked", dark, "lk-", 430, 156, 94)}
  <text class="note" x="468" y="272" font-size="10.5" text-anchor="middle">3–5 kept · scored</text>
  <text class="note" x="468" y="287" font-size="10.5" text-anchor="middle">tied to a decision</text>

  <path class="wire flow" d="M516 206 C546 206, 550 150, 574 150"/>
  {bf.arrow_r(582, 150)}
  <path class="wire flow" d="M516 206 C546 206, 550 262, 574 262"/>
  {bf.arrow_r(582, 262)}

  {card(CARD_X, 108, "SCHEDULED · PER PILLAR", [("probe-scouting", "scouting/P#/&lt;date&gt;.md")], dark)}
  {card(CARD_X, 196, "ON DEMAND · YOU NAME IT", [("probe-analysis", "analysis/&lt;id&gt;.md"),
                                                 ("probe-comparison", "comparison/&lt;slug&gt;.md"),
                                                 ("probe-presentation", "presentation/&lt;id&gt;.md")], dark)}
"""


def render(palette, dark):
    css = bf.CSS
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           'role="img" aria-label="PROBE — the human owns context/, the day of arXiv narrows to a '
           'scored shortlist, and four tracks write scouting, analysis, comparison and presentation">\n'
           f"  <style>{css}  </style>\n{drawing(dark)}\n</svg>\n")
    for k, v in {**palette, "MONO": bf.MONO, "SANS": bf.SANS}.items():
        svg = svg.replace("{" + k + "}", v)
    return svg


(OUT / "stage.svg").write_text(render(bf.LIGHT, False))
(OUT / "stage-dark.svg").write_text(render(bf.DARK, True))
print("ok")
