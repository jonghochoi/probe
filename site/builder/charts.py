"""The figures a talk draws from the paper's own numbers and sentences, as inline SVG.

Five fences, all drawn here so they share one vocabulary and one palette:

    ```probe-chart    a results chart — `line` over a sweep, `dots` across
                      categories, `scatter` for one quantity against another
                      (cost against quality) — with at most one series marked
                      `us` in the accent and every other one in the
                      de-emphasis grey
    ```probe-heat     a per-position strip — rows of cells whose shade is a
                      value in [0, 1], for the mechanisms a paper states as a
                      value per position (a schedule, a mask)
    ```probe-timing   rows on one millisecond ruler with the control period as
                      the grid — either call paths, each ending on its total,
                      or workers running side by side, with what one hands the
                      other drawn as an arrow
    ```probe-contrast the prior work the paper names against the properties
                      it contrasts itself on — one glyph per cell, this paper
                      last in the accent, and the column only it fills drawn
                      as the contribution
    ```probe-inheritance
                      the priors the paper takes something from, each flowing
                      into it along an edge that says what it took, the paper
                      listing what it adds, and the question it leaves

Every colour is a site token, read through the `--pc-*` properties
`presentation.css` sets on the frame, so the light theme, the dark theme and the
turn's tinted frame are one drawing.

The drawing fills the frame's width. The slide hands in the shape of the box
it has left (`ratio`, width over height), and each figure spends the slack on
the one dimension it can stretch — a plot's height, a row's pitch, a cell's
height — so the drawing arrives at the box's own shape and the SVG scales to
its full width. A figure that cannot get short enough without crushing its
rows widens its coordinate space instead: its type comes out a little smaller,
but the frame has no empty flanks. Type is set in viewBox units against a
1000-wide drawing, so it grows with the frame on the stage the way the slide's
own type does.

All five take their numbers and phrases from the paper and nothing else
(`presentation/AUTHORING.md` §4). What the drawing adds is the arrangement:
which series is ours, which baseline is the one to beat, the one annotation
that carries the takeaway. A number read off the paper's plot image is not a
number the paper states, so there is no field for an error bar or an
interpolated point — and no field for a coordinate either: the author states
values and times, and the build places them, which is what keeps every mark
checkable against the paper by reading the fence. A number is printed at the
precision it was written in: `80.0` stays `80.0`, and a gap between two values
written to one decimal is stated to one decimal.

The rules the drawing keeps are the ones that decide whether a chart reads from
across a room:

  - one series is the point, so it is the only one in colour — the rest are
    grey, told apart by shape and by a direct label, never by hue alone;
  - a legend whenever two or more series share the plot, and direct labels
    beside it rather than instead of it;
  - hairline grid, a surface ring on every marker so overlaps stay legible,
    and text in text tokens rather than the series colour;
  - every mark carries a `<title>`, so the value is one hover away.

`step` on a series or a row wraps what it draws in `data-build`, which
`presentation.js` holds back until the presenter's press on the stage.
`steps` on a `line` or a `probe-heat` draws the figure in every state the
presenter walks it through — a swept column at a time, or a schedule carried
through a step — with the row naming the states over it; the script only
chooses which state is on screen.
`omitted` — the source rows a chart leaves out on purpose — is read by the
linter and the author's self-check, never drawn.
"""

from __future__ import annotations

import math
import re

from . import components as c

# The width every size in a drawing is set against. A figure that has to widen
# its coordinate space to reach the frame's shape does so from here.
W0 = 1000

# The shape a figure falls back to when the slide does not say.
RATIO = 2.6

# Glyph widths in em, for placing labels before the browser has laid them out.
# Hangul is square; Latin and digits run about six-tenths. Over-estimating is
# the safe side — a label given too much room sits a little loose, one given
# too little collides.
_WIDE = 1.0
_NARROW = 0.6

_MINUS = "−"


def _tw(text: str, size: float) -> float:
    return sum((_WIDE if ord(ch) > 0x2000 and not 0x2080 <= ord(ch) <= 0x209F
                else _NARROW) for ch in text) * size


def _t(x: float, y: float, text: str, cls: str, anchor: str = "start") -> str:
    return (f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" '
            f'text-anchor="{anchor}">{c.esc(text)}</text>')


# ── numbers at the precision they were written in ─────────────────────

def _written(v) -> int:
    """How many decimals `v` was written with. JSON keeps `80.0` a float and
    `80` an int, so the author's own digits are the precision to print at."""
    if isinstance(v, bool) or v is None:
        return 0
    if isinstance(v, int):
        return 0
    s = repr(float(v))
    if "e" in s:
        return 0
    return len(s.split(".")[1]) if "." in s else 0


_LABEL_DEC = re.compile(r"\d+\.(\d+)")


def _decimals(axis: dict, series: list, key: str = "values") -> int:
    """The precision an axis prints at: `decimals` when the author states it,
    otherwise the most decimals any value or label on it was written with."""
    if isinstance(axis.get("decimals"), int):
        return axis["decimals"]
    pct = axis.get("fmt", "raw") == "pct"
    dec = 0
    for s in series:
        for v in _flat(s, key):
            # 0.625 is 62.5 %: two of its decimals are the percent.
            dec = max(dec, _written(v) - 2 if pct else _written(v))
        for lab in s.get("labels") or []:
            for m in _LABEL_DEC.finditer(str(lab or "")):
                dec = max(dec, len(m.group(1)))
    return min(dec, 4)


def _flat(s: dict, key: str) -> list:
    if key == "points":
        return [p.get(a) for p in s.get("points", []) for a in ("x", "y")
                if isinstance(p.get(a), (int, float))]
    return [v for v in s.get(key, []) if isinstance(v, (int, float))]


def _num(v: float, dec: int) -> str:
    s = f"{v:.{dec}f}"
    return s.replace("-", _MINUS) if s.startswith("-") else s


def _fmt(v: float, axis: dict, dec: int) -> str:
    if axis.get("fmt", "raw") == "pct":
        return f"{_num(v * 100, dec)}%"
    return _num(v, dec) + axis.get("unit", "")


def _delta(d: float, axis: dict, dec: int) -> str:
    """A gap, signed, at the axis's precision and in its unit — `%p` on a
    percentage scale, the axis's own unit on a raw one. A gap that rounds to
    nothing says so rather than printing `+0`."""
    pct = axis.get("fmt", "raw") == "pct"
    v = d * 100 if pct else d
    if round(v, dec) == 0:
        return "±" + _num(0, dec) + ("%p" if pct else axis.get("unit", ""))
    sign = "+" if v > 0 else _MINUS
    return sign + f"{abs(v):.{dec}f}" + ("%p" if pct else axis.get("unit", ""))


def _tick(v: float, axis: dict) -> str:
    if axis.get("fmt", "raw") == "pct":
        return f"{v * 100:g}%"
    return f"{v:g}".replace("-", _MINUS)


def _build(item: dict, body: str) -> str:
    """Wrap `body` so the stage holds it until the presenter's `step`-th press."""
    k = item.get("step") if isinstance(item, dict) else None
    if isinstance(k, int) and not isinstance(k, bool) and k > 0:
        return f'<g data-build="{k}">{body}</g>'
    return body


# ── states: a figure the presenter steps through ──────────────────────
#
# A stepped figure is drawn once with every state it can be in, and
# `presentation.js` only chooses which one is on screen — so every number a
# state shows is in the markup the build wrote, and nothing is computed in the
# browser. Three attributes carry it: `data-in` (the states an element is shown
# in), `data-lo` (the states it is set back in) and `data-vars` (a custom
# property's value per state, `--name:v0;v1;…|--other:…`). The markup is
# written in state 0, which is what a printout and a browser with no script
# keep (`presentation/AUTHORING.md` §8-2).

def _shown(states: list[int], body: str) -> str:
    """`body`, shown only in `states`."""
    if not states:
        return ""
    out = "" if 0 in states else ' class="prs-out"'
    return f'<g data-in="{" ".join(map(str, states))}"{out}>{body}</g>'


def _dimmed(states: list[int], body: str) -> str:
    """`body`, set back in `states` — there, but not what the state is about."""
    if not states:
        return body
    lo = ' class="prs-lo"' if 0 in states else ""
    return f'<g data-lo="{" ".join(map(str, states))}"{lo}>{body}</g>'


def _vars(**props: list[str]) -> str:
    """`data-vars` and the state-0 inline style for a per-state property."""
    names = {k: "--" + k.replace("_", "-") for k in props}
    spec = "|".join(f"{names[k]}:" + ";".join(v) for k, v in props.items())
    first = ";".join(f"{names[k]}:{v[0]}" for k, v in props.items())
    return f'data-vars="{c.esc(spec)}" style="{c.esc(first)}"'


def _stepper(labels: list[str]) -> str:
    """The row that names every state and marks the one on screen.

    On the stage it is the room's caption for the state it is looking at; in
    the tab its buttons are how a reader steps. Drawn only once
    `presentation.js` has set a reading, since without it the figure stands in
    its first state and a row of buttons would point at nothing.
    """
    btns = "".join(
        f'<button type="button" data-step-to="{i}" '
        f'aria-pressed="{"true" if i == 0 else "false"}">{c.esc(l)}</button>'
        for i, l in enumerate(labels))
    return (f'<div class="prs-stepper" role="group" aria-label="단계">{btns}'
            f'<span class="prs-stepkeys" aria-hidden="true">↑ ↓</span></div>')


def _marker(shape: str, x: float, y: float, r: float, cls: str, tip: str) -> str:
    """One data mark with its surface ring. The ring is what keeps two marks
    that land on each other legible as two."""
    title = f"<title>{c.esc(tip)}</title>"
    if shape == "square":
        s = r * .9
        return (f'<rect x="{x - s:.1f}" y="{y - s:.1f}" width="{2 * s:.1f}" '
                f'height="{2 * s:.1f}" rx="1.5" class="{cls}">{title}</rect>')
    if shape == "diamond":
        s = r * 1.2
        return (f'<path d="M{x:.1f} {y - s:.1f} L{x + s:.1f} {y:.1f} L{x:.1f} '
                f'{y + s:.1f} L{x - s:.1f} {y:.1f} Z" class="{cls}">{title}</path>')
    if shape == "triangle":
        s = r * 1.15
        return (f'<path d="M{x:.1f} {y - s:.1f} L{x + s:.1f} {y + s * .8:.1f} '
                f'L{x - s:.1f} {y + s * .8:.1f} Z" class="{cls}">{title}</path>')
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" class="{cls}">{title}</circle>'


# Baselines are told apart by shape, since they share the grey. The one `vs`
# names — the strongest at the point the note reads — gets the darker grey.
_SHAPES = ("circle", "square", "diamond", "triangle")


def _style(i: int, s: dict, ref: str | None,
           subj: str | None = None) -> tuple[str, str]:
    """(shape, css class) for series `i`."""
    if s.get("us"):
        return "circle", "pc-us"
    if s["name"] == subj:
        return _SHAPES[i % len(_SHAPES)], "pc-subj"
    tone = "pc-ref" if s["name"] == ref else "pc-ctx"
    return _SHAPES[i % len(_SHAPES)], tone


def _subject(ch: dict) -> str | None:
    """The series a chart with no `us` is about: the one its note names.

    A chart of a finding has no method to put in the accent, and without this
    the strongest-baseline grey (`vs`) would be the darkest line on it — the
    eye landing on the reference rather than on the series the header argues
    about. That series takes the text's own ink instead: the heaviest line,
    and still not the accent, which stays the method's."""
    if any(s.get("us") for s in ch.get("series", [])):
        return None
    note = ch.get("note") or {}
    name = note.get("of") or note.get("series")
    return name if any(s["name"] == name for s in ch.get("series", [])) else None


def _legend(series: list, ref: str | None, y: float, x0: float, line: bool,
            size: float = 17, subj: str | None = None) -> str:
    """The identity channel that does not depend on colour matching."""
    out, x = [], x0
    for i, s in enumerate(series):
        shape, cls = _style(i, s, ref, subj)
        key = []
        if line:
            key.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x + 24:.1f}" '
                       f'y2="{y:.1f}" class="{cls} pc-ln"/>')
            key.append(_marker(shape, x + 12, y, 5.5, cls, s["name"]))
            x += 32
        else:
            key.append(_marker(shape, x + 7, y, 7, cls, s["name"]))
            x += 20
        key.append(_t(x, y + 6, s["name"], "pc-key" + (
            " pc-key-us" if s.get("us") or s["name"] == subj else "")))
        out.append(_build(s, "".join(key)))
        x += _tw(s["name"], size) + 30
    return "".join(out)


def _legend_width(series: list, line: bool, size: float = 17) -> float:
    return sum((32 if line else 20) + _tw(s["name"], size) + 30 for s in series) - 30


def _ticks(lo: float, hi: float, step: float) -> list[float]:
    n = int(round((hi - lo) / step))
    return [round(lo + k * step, 10) for k in range(n + 1)]


def _fit(fixed: float, per: float, lo: float, hi: float, ratio: float | None,
         width: float = W0) -> tuple[float, float, float]:
    """Spend a drawing's slack on its one stretchable dimension.

    `fixed` is the height everything but that dimension takes, `per` how many
    times the dimension recurs (rows, or 1 for a plot), `lo`/`hi` its bounds.
    Returns (the dimension, the drawing's height, its width): the width grows
    past `width` only when the dimension is already at `lo` and the drawing is
    still taller than the box is shaped for — so the SVG reaches the frame's
    width rather than standing in the middle of it with empty flanks.
    """
    ratio = ratio or RATIO
    target = width / ratio
    dim = max(lo, min(hi, (target - fixed) / per))
    height = fixed + per * dim
    return dim, height, max(width, height * ratio)


# ── line: a sweep ─────────────────────────────────────────────────────

def line(ch: dict, ratio: float | None = None) -> str:
    """Several series over one ordered x, with the takeaway as a bracket.

    The x axis is ordinal by default — one step per tick — and numeric when
    `x.values` gives each tick its value, so a sweep over 0, 9, 12, 16, 17
    keeps the distances it was run at and the slopes the room reads are the
    real ones. A `null` value is a point the paper did not measure: the line
    breaks there rather than bridging it.

    The end labels are placed at the value they name and pushed apart only as
    far as they must be; a label that moved gets a leader back to its line, so
    it never floats free of the mark it belongs to.

    `steps` walks the sweep one x at a time: state 0 is the whole chart, and
    each later state washes one column, sets every other column back and
    prints each series' value beside its mark there — the room reads the gap
    at that x instead of estimating it from the slopes. The last column
    already carries the end labels, so stepping onto it prints nothing new.
    """
    xs = ch["x"]["ticks"]
    subs = ch["x"].get("sub", [])
    xv = ch["x"].get("values")
    y = ch["y"]
    lo, hi = y["min"], y["max"]
    series = ch["series"]
    ref = ch.get("vs")
    subj = _subject(ch)
    dec = _decimals(y, series)

    def last(s: dict) -> int:
        idx = [i for i, v in enumerate(s["values"]) if v is not None]
        return idx[-1] if idx else 0

    def end_text(s: dict) -> str:
        labs = s.get("labels") or []
        k = last(s)
        return labs[k] if k < len(labs) and labs[k] else _fmt(s["values"][k], y, dec)

    label_w = max(_tw(s["name"], 17) + _tw(end_text(s), 20) + 18 for s in series)
    T = 66
    has_x_label = bool(ch["x"].get("label"))

    # Tick blocks that would collide at their x are staggered onto a second
    # row rather than printed over each other.
    def blockw(i: int) -> float:
        return max(_tw(xs[i], 20), _tw(subs[i], 15) if i < len(subs) and subs[i] else 0)

    # A first pass with the default width finds how many tick rows there are.
    below = (60 if subs else 36) + (26 if has_x_label else 0) + 10
    plot, height, W = _fit(T + below, 1, 150, 330, ratio)

    def layout(W: float):
        L, R = 76, W - label_w - 30
        if xv:
            vlo = ch["x"].get("min", min(xv))
            vhi = ch["x"].get("max", max(xv))

            def px(i: int) -> float:
                pad = (R - L) * .05
                return L + pad + (R - L - 2 * pad) * ((xv[i] - vlo) / ((vhi - vlo) or 1))
        else:
            def px(i: int) -> float:
                pad = (R - L) * .08
                return L + pad + (R - L - 2 * pad) * (i / max(1, len(xs) - 1))
        level, edge = [], [-1e9, -1e9]
        for i in range(len(xs)):
            w = blockw(i)
            lv = 0 if px(i) - w / 2 > edge[0] + 8 else 1
            level.append(lv)
            edge[lv] = px(i) + w / 2
        return L, R, px, level

    L, R, px, level = layout(W)
    if any(level):
        below += 50 if subs else 24
        plot, height, W = _fit(T + below, 1, 150, 330, ratio)
        L, R, px, level = layout(W)
    B = T + plot

    def py(v: float) -> float:
        return B - (v - lo) / (hi - lo) * (B - T)

    steps = ch.get("steps") or []

    def away(i: int) -> list[int]:
        """The states that are about some other column than `i`."""
        return [k + 1 for k, j in enumerate(steps) if j != i]

    out = [_legend(series, ref, 18, W - _legend_width(series, True), line=True,
                   subj=subj)]
    # The washed column, under everything else.
    for k, i in enumerate(steps):
        half = min(56, (px(min(i + 1, len(xs) - 1)) - px(max(i - 1, 0)))
                   / (4 if 0 < i < len(xs) - 1 else 2))
        out.append(_shown([k + 1], f'<rect x="{px(i) - half:.1f}" y="{T - 14}" '
                                   f'width="{2 * half:.1f}" height="{B - T + 14:.1f}" '
                                   f'rx="6" class="pc-band"/>'))
    for v in _ticks(lo, hi, y["step"]):
        out.append(f'<line x1="{L}" x2="{R + 20:.1f}" y1="{py(v):.1f}" '
                   f'y2="{py(v):.1f}" class="pc-grid{" pc-base" if v == lo else ""}"/>')
        out.append(_t(L - 14, py(v) + 6, _tick(v, y), "pc-tick", "end"))
    out.append(_t(0, 24, y.get("label", ""), "pc-axis"))
    step_y = 50 if subs else 24
    for i, lab in enumerate(xs):
        off = level[i] * step_y
        tick = _t(px(i), B + 30 + off, lab, "pc-xt", "middle")
        if i < len(subs) and subs[i]:
            tick += _t(px(i), B + 56 + off, subs[i], "pc-xs", "middle")
        out.append(_dimmed(away(i), tick))
    bottom = B + (60 if subs else 36) + (step_y if any(level) else 0)
    if has_x_label:
        bottom += 26
        out.append(_t((px(0) + px(len(xs) - 1)) / 2, bottom, ch["x"]["label"],
                      "pc-axis", "middle"))

    us = next((s for s in series if s.get("us")), None)
    names = {s["name"]: s for s in series}
    ours: list[str] = []

    # The takeaway: a bracket between two series at one x — ours and the named
    # baseline unless the note names its own pair — with the label where the
    # author put it: `side` is which side of the points the bracket stands on,
    # `place` whether the words sit over its upper end, under its lower end or
    # beside its middle.
    note = ch.get("note")
    if note:
        i = note["at"]
        a = names.get(note.get("of")) or us
        b = names.get(note.get("from", ref))
        side = note.get("side", "left")
        sub = note.get("sub")
        va = a["values"][i] if a else None
        vb = b["values"][i] if b else None
        if va is not None and vb is not None:
            x = px(i) + (34 if side == "right" else -34)
            y1, y2 = py(va), py(vb)
            top, bot = min(y1, y2), max(y1, y2)
            tick = 7 if side == "left" else -7
            ours.append(f'<path d="M{x + tick:.1f} {top - 10:.1f} H{x:.1f} V{bot + 10:.1f} '
                        f'H{x + tick:.1f}" class="pc-brace"/>')
            place = note.get("place") or ("above" if y1 < y2 else "below")
            anchor = "start" if side == "right" else "end"
            tx = x + (14 if side == "right" else -14)
            if place == "above":
                ty = top - (46 if sub else 18)
            elif place == "below":
                ty = bot + 40
            else:
                ty = (top + bot) / 2 - (6 if sub else -8)
        else:
            tx, anchor = px(i), "middle"
            ty = T + 8
        ours.append(_t(tx, ty, note["text"], "pc-note", anchor))
        if sub:
            ours.append(_t(tx, ty + 24, sub, "pc-nsub", anchor))

    ends = []
    early = []
    order = sorted(range(len(series)), key=lambda k: series[k].get("us", False))
    drawn: dict[int, list[str]] = {}
    for k in order:
        s = series[k]
        shape, cls = _style(k, s, ref, subj)
        marks = []
        run: list[str] = []
        for i, v in enumerate(s["values"] + [None]):
            if v is None:
                if len(run) > 1:
                    marks.append(f'<polyline points="{" ".join(run)}" class="{cls} pc-ln"/>')
                run = []
                continue
            run.append(f"{px(i):.1f},{py(v):.1f}")
        for i, v in enumerate(s["values"]):
            if v is None:
                continue
            tip = f'{s["name"]} · {xs[i]} · {_fmt(v, y, dec)}'
            marks.append(_dimmed(away(i), _marker(
                shape, px(i), py(v), 8 if s.get("us") or s["name"] == subj else 6,
                cls, tip)))
        drawn[k] = marks
        # A series that stops before the last tick is labelled where it
        # stops; a leader run across the plot to the common label column
        # would read as a line of data.
        (ends if last(s) == len(xs) - 1 else early).append([py(s["values"][last(s)]), k])

    # Push the end labels apart top-down, then back up if the last one ran off.
    ends.sort()
    gap = 34
    for j in range(1, len(ends)):
        if ends[j][0] - ends[j - 1][0] < gap:
            ends[j][0] = ends[j - 1][0] + gap
    over = ends[-1][0] - (B + 4) if ends else 0
    if over > 0:
        for e in ends:
            e[0] -= over
    lx = px(len(xs) - 1) + 22
    for e in ends:
        ly, k = e[0], e[1]
        s = series[k]
        li = last(s)
        vy = py(s["values"][li])
        if abs(ly - vy) > 3:
            drawn[k].append(f'<path d="M{px(li) + 10:.1f} {vy:.1f} '
                            f'L{lx - 4:.1f} {ly:.1f}" class="pc-lead"/>')
        cls = "pc-end pc-end-us" if s.get("us") or s["name"] == subj else "pc-end"
        drawn[k].append(f'<text x="{lx + 4:.1f}" y="{ly + 7:.1f}" class="{cls}">'
                        f'<tspan class="pc-endv">{c.esc(end_text(s))}</tspan>'
                        f'<tspan dx="8">{c.esc(s["name"])}</tspan></text>')
    for vy, k in early:
        s = series[k]
        cls = "pc-end pc-end-us" if s.get("us") else "pc-end"
        drawn[k].append(f'<text x="{px(last(s)) + 16:.1f}" y="{vy + 7:.1f}" class="{cls}">'
                        f'<tspan class="pc-endv">{c.esc(end_text(s))}</tspan>'
                        f'<tspan dx="8">{c.esc(s["name"])}</tspan></text>')
    # Stepped, the takeaway stands in the whole chart and returns on the
    # state that washes its own column — the walk sets it aside while the
    # room reads the other columns, and ends by arriving at it.
    if steps and ours and note:
        ours = [_shown([0] + [k + 1 for k, j in enumerate(steps) if j == note["at"]],
                       "".join(ours))]
    for k in order:
        body = "".join(drawn[k])
        if series[k] is us:
            body += "".join(ours)
        out.append(_build(series[k], body))
    if us is None and ours:
        out.append("".join(ours))

    # Each state's readout: the value of every series at its column, on a tag
    # beside its own mark — a tag rather than bare figures, because the lines
    # run on through the column and a number set on its own line reads as
    # struck through. Tags are pushed apart only as far as they must be.
    for st, i in enumerate(steps, start=1):
        if i == len(xs) - 1:
            continue
        here = sorted(([py(s["values"][i]), k] for k, s in enumerate(series)
                       if s["values"][i] is not None), key=lambda e: e[0])
        for j in range(1, len(here)):
            if here[j][0] - here[j - 1][0] < 32:
                here[j][0] = here[j - 1][0] + 32
        read = []
        for ly, k in here:
            s = series[k]
            text = _fmt(s["values"][i], y, dec)
            us = " pc-read-us" if s.get("us") else ""
            # The series' own mark leads the tag, so a value is matched to its
            # line by shape rather than by counting positions.
            shape, cls = _style(k, s, ref, subj)
            w = _tw(text, 20) + 38
            # A column next to the last one would push its tags into the end
            # labels, so there they stand on the column's left instead.
            right = px(i) + 16
            x0 = right if right + w < px(len(xs) - 1) - 12 else px(i) - 16 - w
            read.append(_build(s, (
                f'<rect x="{x0:.1f}" y="{ly - 15:.1f}" width="{w:.1f}" height="30" '
                f'rx="6" class="pc-read{us}"/>'
                + _marker(shape, x0 + 14, ly, 5.5, cls, s["name"])
                + _t(x0 + 28, ly + 7, text, f"pc-readv{us}"))))
        out.append(_shown([st], "".join(read)))

    labels = (["전체"] + [xs[i] for i in steps]) if steps else None
    return _svg(W, bottom + 10, "".join(out), ch, labels)


# ── dots: categories side by side ─────────────────────────────────────

def dots(ch: dict, ratio: float | None = None) -> str:
    """One row per category, every series a mark on a shared scale.

    The distance that matters — ours against the row's strongest baseline, or
    the baseline the row names in its own `vs` — is drawn as a connector and
    labelled with its size, so the room reads the gap rather than subtracting
    two positions. A connector that would cross another series' mark is lifted
    over the row as a bracket instead, so no gap is ever read through a mark
    it is not measuring. `group` brackets the rows the paper itself singles
    out, which is the takeaway line. `"gap": false` draws no connectors, for a
    chart whose series are two readings of one thing rather than rivals.
    """
    rows = ch["rows"]
    series = ch["series"]
    ref = ch.get("vs")
    x = ch["x"]
    lo, hi = x["min"], x["max"]
    higher = x.get("better", "higher") != "lower"
    dec = _decimals(x, series)
    T = 70
    tail = 66 if x.get("label") else 40
    row_h, height, W = _fit(T + tail, len(rows), 54, 96, ratio)
    L = max(max(_tw(r["name"], 20), _tw(r.get("sub", ""), 15)) for r in rows) + 30
    group = ch.get("group")
    gw = (max(_tw(group["text"], 30), _tw(group.get("sub", ""), 15)) + 40) if group else 0
    R = W - gw - 150

    def px(v: float) -> float:
        return L + (v - lo) / (hi - lo) * (R - L)

    out = [_legend(series, ref, 22, 0, line=False)]
    B = T + row_h * len(rows)
    for v in _ticks(lo, hi, x["step"]):
        out.append(f'<line x1="{px(v):.1f}" x2="{px(v):.1f}" y1="{T - 8}" '
                   f'y2="{B:.1f}" class="pc-grid"/>')
        out.append(_t(px(v), B + 28, _tick(v, x), "pc-tick", "middle"))
    if x.get("label"):
        out.append(_t(R, B + 56, x["label"], "pc-axis", "end"))

    us = next((s for s in series if s.get("us")), None)
    gaps = us is not None and ch.get("gap", True) is not False
    ours: list[str] = []
    for j, r in enumerate(rows):
        cy = T + row_h * j + row_h / 2
        out.append(_t(0, cy + (-2 if r.get("sub") else 7), r["name"], "pc-row"))
        if r.get("sub"):
            out.append(_t(0, cy + 22, r["sub"], "pc-xs"))
        out.append(f'<line x1="{L}" x2="{R:.1f}" y1="{cy:.1f}" y2="{cy:.1f}" '
                   f'class="pc-track"/>')
        vals = {s["name"]: s["values"][j] for s in series
                if s["values"][j] is not None}
        texts = {s["name"]: (s.get("labels") or [None] * len(rows))[j] for s in series}
        against = None
        if gaps and us["name"] in vals:
            rivals = {n: v for n, v in vals.items() if n != us["name"]}
            against = r.get("vs") or (
                (max if higher else min)(rivals, key=rivals.get) if rivals else None)
            if against in vals:
                a, b = px(vals[against]), px(vals[us["name"]])
                lo_x, hi_x = min(a, b), max(a, b)
                through = any(lo_x + 6 < px(v) < hi_x - 6 for n, v in vals.items()
                              if n not in (against, us["name"]))
                if through:
                    ly = cy - 17
                    ours.append(f'<path d="M{a:.1f} {cy - 9:.1f} V{ly:.1f} H{b:.1f} '
                                f'V{cy - 11:.1f}" class="pc-gap-over"/>')
                else:
                    ours.append(f'<line x1="{a:.1f}" x2="{b:.1f}" y1="{cy:.1f}" '
                                f'y2="{cy:.1f}" class="pc-gap"/>')
        order = sorted(range(len(series)), key=lambda k: (
            series[k].get("us", False), series[k]["name"] == ref))
        for k in order:
            s = series[k]
            v = s["values"][j]
            if v is None:
                continue
            shape, cls = _style(k, s, ref)
            shown = texts[s["name"]] or _fmt(v, x, dec)
            mark = _marker(shape, px(v), cy, 10 if s.get("us") else 7.5, cls,
                           f'{r["name"]} · {s["name"]} · {shown}')
            if s is us:
                ours.append(mark)
            else:
                out.append(_build(s, mark))
        # Ours, labelled with its distance to the baseline and its raw value.
        if us is None or us["name"] not in vals:
            continue
        right = max(vals.values())
        lx = px(right) + 18
        shown = texts[us["name"]] or _fmt(vals[us["name"]], x, dec)
        delta = (_delta(vals[us["name"]] - vals[against], x, dec)
                 if against in vals else "")
        tail_t = (f'<tspan dx="8" class="pc-dim">{c.esc(shown)}</tspan>' if delta
                  else f'<tspan class="pc-endv">{c.esc(shown)}</tspan>')
        ours.append(f'<text x="{lx:.1f}" y="{cy + 7:.1f}" class="pc-end pc-end-us">'
                    + (f'<tspan class="pc-endv">{c.esc(delta)}</tspan>' if delta else "")
                    + tail_t + '</text>')

    if group:
        j0, j1 = min(group["rows"]), max(group["rows"])
        y0 = T + row_h * j0 + 12
        y1 = T + row_h * (j1 + 1) - 12
        gx = W - gw + 6
        ours.append(f'<path d="M{gx - 10:.1f} {y0:.1f} H{gx:.1f} V{y1:.1f} '
                    f'H{gx - 10:.1f}" class="pc-brace"/>')
        mid = (y0 + y1) / 2
        ours.append(_t(gx + 16, mid + 2, group["text"], "pc-note pc-big"))
        if group.get("sub"):
            ours.append(_t(gx + 16, mid + 28, group["sub"], "pc-nsub"))
    out.append(_build(us, "".join(ours)) if us else "".join(ours))
    return _svg(W, B + tail, "".join(out), ch)


# ── scatter: one quantity against another ─────────────────────────────

def scatter(ch: dict, ratio: float | None = None) -> str:
    """Points on two scales — the shape of a cost-against-quality result.

    Every point is a row of the paper's table: its `x`, its `y`, and the
    `label` that names it beside the mark, on the side the author says
    (`place`: right, left, above, below), because only the author knows which
    neighbour a label would land on. `frontier` on a series joins its points
    in x order — the trade-off curve the paper draws — and `guides` are the
    reference levels a reader measures against (the full model's success, a
    size budget), each a dashed rule with its own label.
    """
    xa, ya = ch["x"], ch["y"]
    series = ch["series"]
    ref = ch.get("vs")
    subj = _subject(ch)
    dx, dy = _decimals(xa, series, "points"), _decimals(ya, series, "points")
    T, bottom_pad = 66, 36 + (30 if xa.get("label") else 0) + 10
    plot, height, W = _fit(T + bottom_pad, 1, 200, 420, ratio)
    B = T + plot
    L = 76
    label_room = max((_tw(p.get("label", ""), 16) for s in series
                      for p in s["points"] if p.get("place", "right") == "right"),
                     default=0)
    R = W - min(label_room, 220) - 24

    def px(v: float) -> float:
        return L + (v - xa["min"]) / (xa["max"] - xa["min"]) * (R - L)

    def py(v: float) -> float:
        return B - (v - ya["min"]) / (ya["max"] - ya["min"]) * (B - T)

    out = [_legend(series, ref, 18, W - _legend_width(series, False), line=False,
                   subj=subj)]
    for v in _ticks(ya["min"], ya["max"], ya["step"]):
        out.append(f'<line x1="{L}" x2="{R:.1f}" y1="{py(v):.1f}" y2="{py(v):.1f}" '
                   f'class="pc-grid{" pc-base" if v == ya["min"] else ""}"/>')
        out.append(_t(L - 14, py(v) + 6, _tick(v, ya), "pc-tick", "end"))
    for v in _ticks(xa["min"], xa["max"], xa["step"]):
        out.append(f'<line x1="{px(v):.1f}" x2="{px(v):.1f}" y1="{T}" y2="{B:.1f}" '
                   f'class="pc-grid"/>')
        out.append(_t(px(v), B + 28, _tick(v, xa), "pc-tick", "middle"))
    out.append(_t(0, 24, ya.get("label", ""), "pc-axis"))
    if xa.get("label"):
        out.append(_t(R, B + 60, xa["label"], "pc-axis", "end"))

    for g in ch.get("guides", []):
        if "y" in g:
            gy = py(g["y"])
            out.append(f'<line x1="{L}" x2="{R:.1f}" y1="{gy:.1f}" y2="{gy:.1f}" class="pc-guide"/>')
            if g.get("place") == "start":
                out.append(_t(L + 8, gy - 8, g.get("label", ""), "pc-xs pc-glab"))
            else:
                out.append(_t(R, gy - 8, g.get("label", ""), "pc-xs pc-glab", "end"))
        elif "x" in g:
            gx = px(g["x"])
            out.append(f'<line x1="{gx:.1f}" x2="{gx:.1f}" y1="{T}" y2="{B:.1f}" class="pc-guide"/>')
            out.append(_t(gx + 8, T + 16, g.get("label", ""), "pc-xs"))

    us = next((s for s in series if s.get("us")), None)
    order = sorted(range(len(series)), key=lambda k: series[k].get("us", False))
    for k in order:
        s = series[k]
        shape, cls = _style(k, s, ref, subj)
        drawn = []
        pts = s["points"]
        if s.get("frontier") and len(pts) > 1:
            path = " ".join(f"{px(p['x']):.1f},{py(p['y']):.1f}"
                            for p in sorted(pts, key=lambda p: p["x"]))
            drawn.append(f'<polyline points="{path}" class="{cls} pc-ln pc-front"/>')
        for p in pts:
            x, y = px(p["x"]), py(p["y"])
            lab = p.get("label", "")
            tip = f'{s["name"]} · {lab} · {_fmt(p["x"], xa, dx)}, {_fmt(p["y"], ya, dy)}'
            drawn.append(_marker(shape, x, y, 9 if s.get("us") else 7, cls, tip))
            place = p.get("place", "right")
            cls_t = "pc-plab" + (" pc-plab-us" if s.get("us") else "")
            if place == "left":
                drawn.append(_t(x - 14, y + 6, lab, cls_t, "end"))
            elif place == "above":
                drawn.append(_t(x, y - 16, lab, cls_t, "middle"))
            elif place == "below":
                drawn.append(_t(x, y + 30, lab, cls_t, "middle"))
            else:
                drawn.append(_t(x + 14, y + 6, lab, cls_t))
        out.append(_build(s, "".join(drawn)))

    note = ch.get("note")
    if note:
        # The point is named by its label, looked up in the series the note
        # names, else in ours first — two series often share a label.
        pool = ([s for s in series if s["name"] == note.get("series")]
                or sorted(series, key=lambda s: not s.get("us")))
        hit = next(((s, p) for s in pool for p in s["points"]
                    if p.get("label") == note.get("point")), None)
        if hit:
            x, y = px(hit[1]["x"]), py(hit[1]["y"])
            place = note.get("place", "above")
            anchor = {"left": "end", "right": "start"}.get(place, "middle")
            tx = x + {"left": -18, "right": 18}.get(place, 0)
            ty = {"above": y - 64, "below": y + 70}.get(place, y - 20)
        else:
            tx, ty, anchor = (L + R) / 2, T + 10, "middle"
        body = _t(tx, ty, note["text"], "pc-note", anchor)
        if note.get("sub"):
            body += _t(tx, ty + 24, note["sub"], "pc-nsub", anchor)
        out.append(_build(us, body) if us else body)
    return _svg(W, B + bottom_pad, "".join(out), ch)


# ── heat: a value per position ────────────────────────────────────────

def heat(h: dict, ratio: float | None = None) -> str:
    """Rows of cells, each shaded by a value in [0, 1] on one sequential ramp.

    `shared` draws a run of positions that hold *one* value between them as a
    single block, because that is the claim — the positions do not have
    values of their own — and shading them one level would state a number the
    source leaves free. `regions` names spans under a row; `mark` outlines the
    span a step singles out; `step` labels the move from the row above.

    A strip whose every cell is 0 or 1 is a mask, not a ramp, so its key is
    two swatches — a six-step gradient beside yes/no data claims levels the
    data does not have.

    `steps` names the states of a schedule carried through a step, and a row
    with `states` is drawn once per state in one place (`_stepped_row`) — the
    presenter moves it from one to the next instead of the room comparing
    stacked copies.
    """
    n = h["cols"]
    rows = h["rows"]
    cells_all = [float(v) for r in rows
                 for st in (r.get("states") or [r]) for v in st.get("cells", [])]
    binary = bool(cells_all) and all(v in (0.0, 1.0) for v in cells_all)

    extra = 48 + 6
    for r in rows:
        if r.get("step"):
            extra += 40
        if any(st.get("regions") or st.get("mark") for st in (r.get("states") or [r])):
            extra += 44
        extra += 14
    if h.get("scale"):
        extra += 32
    ch_, height, W = _fit(extra, len(rows), 34, 64, ratio)

    L = max(max(_tw(r["name"], 20), _tw(r.get("note", ""), 15)) for r in rows) + 30
    L = min(L, 320)
    R = W - 4
    gap = 4
    cw = (R - L - gap * (n - 1)) / n
    y = 48
    out = []
    for p in range(n):
        out.append(_t(L + p * (cw + gap) + cw / 2, y - 14, str(p), "pc-tick", "middle"))
    if h.get("axis"):
        out.append(_t(0, y - 14, h["axis"], "pc-axis"))
    for r in rows:
        if r.get("step"):
            y += 6
            out.append(f'<path d="M{L + 10:.1f} {y - 2:.1f} v22 m-6 -7 l6 7 l6 -7" '
                       f'class="pc-stepar"/>')
            out.append(_t(L + 28, y + 16, r["step"], "pc-step"))
            y += 34
        top = y
        out.append(_t(0, top + ch_ / 2 + (-3 if r.get("note") else 7), r["name"],
                      "pc-row" + (" pc-row-us" if r.get("us") else "")))
        if r.get("note"):
            out.append(_t(0, top + ch_ / 2 + 20, r["note"], "pc-xs"))
        if r.get("states"):
            body, y = _stepped_row(r["states"], n, L, top, cw, gap, ch_, h)
            out.append(body)
            continue
        cells = r.get("cells", [])
        sh = r.get("shared")
        for p in range(n):
            if sh and sh[0] <= p < sh[1]:
                continue
            if p >= len(cells):
                continue
            v = max(0.0, min(1.0, float(cells[p])))
            x = L + p * (cw + gap)
            out.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{cw:.1f}" '
                       f'height="{ch_:.1f}" rx="4" class="pc-cell" '
                       f'style="fill:{_shade(v)}">'
                       f'<title>{p} · {c.esc(h.get("value", "값"))} = {v:.2f}</title></rect>')
        if sh:
            x0 = L + sh[0] * (cw + gap)
            x1 = L + sh[1] * (cw + gap) - gap
            out.append(f'<rect x="{x0:.1f}" y="{top:.1f}" width="{x1 - x0:.1f}" '
                       f'height="{ch_:.1f}" rx="4" class="pc-shared">'
                       f'<title>{c.esc(sh[2])}</title></rect>')
            # The block is one level that moves along the whole ramp at once,
            # so the ramp itself rides beside the label instead of one shade.
            kw, tw = 13, _tw(sh[2], 17)
            tx = (x0 + x1) / 2 - (6 * kw + 14) / 2
            out.append(_t(tx, top + ch_ / 2 + 6, sh[2], "pc-sharedt", "middle"))
            rx = tx + tw / 2 + 14
            out.append("".join(
                f'<rect x="{rx + k * kw:.1f}" y="{top + ch_ / 2 - 7:.1f}" '
                f'width="{kw - 2}" height="14" rx="2" style="fill:{_shade(k / 5)}"/>'
                for k in range(6)))
        if r.get("mark"):
            a, b, lab = r["mark"]
            x0 = L + a * (cw + gap) - 3
            x1 = L + b * (cw + gap) - gap + 3
            out.append(f'<rect x="{x0:.1f}" y="{top - 3:.1f}" width="{x1 - x0:.1f}" '
                       f'height="{ch_ + 6:.1f}" rx="6" class="pc-mark"/>')
        y = top + ch_
        spans = list(r.get("regions", []))
        if r.get("mark"):
            spans.append([r["mark"][0], r["mark"][1], r["mark"][2], True])
        if spans:
            out.append(_spans(spans, L, cw, gap, y))
            y += 44
        y += 14

    # The key, drawn with the cells' own shading so the two cannot disagree:
    # two swatches for a mask, the stepped ramp for anything else.
    if h.get("scale"):
        lo_t, hi_t = h["scale"]
        ky = y + 6
        if binary:
            kw = 30
            x = R - kw - _tw(hi_t, 15) - 10
            out.append(f'<rect x="{x:.1f}" y="{ky:.1f}" width="{kw}" height="18" rx="3" '
                       f'class="pc-cell" style="fill:{_shade(1)}"/>')
            out.append(_t(x + kw + 8, ky + 14, hi_t, "pc-xs"))
            x -= kw + _tw(lo_t, 15) + 36
            out.append(f'<rect x="{x:.1f}" y="{ky:.1f}" width="{kw}" height="18" rx="3" '
                       f'class="pc-cell" style="fill:{_shade(0)}"/>')
            out.append(_t(x + kw + 8, ky + 14, lo_t, "pc-xs"))
        else:
            kw = 28
            kx = R - kw * 6 - _tw(hi_t, 15) - 12
            out.append(_t(kx - 10, ky + 14, lo_t, "pc-xs", "end"))
            for k in range(6):
                out.append(f'<rect x="{kx + k * kw:.1f}" y="{ky:.1f}" width="{kw - 2}" '
                           f'height="18" rx="2" style="fill:{_shade(k / 5)}"/>')
            out.append(_t(kx + 6 * kw + 8, ky + 14, hi_t, "pc-xs"))
        y = ky + 26
    steps = h.get("steps")
    return _svg(W, y + 6, "".join(out), h, steps, bool(h.get("cycle")))


def _spans(spans: list, L: float, cw: float, gap: float, y: float) -> str:
    """Brackets under a row — the regions it names, and the span a step marks."""
    out = []
    for sp in spans:
        a, b, lab = sp[0], sp[1], sp[2]
        hot = len(sp) > 3
        x0 = L + a * (cw + gap) + 2
        x1 = L + b * (cw + gap) - gap - 2
        out.append(f'<path d="M{x0:.1f} {y + 8:.1f} v6 H{x1:.1f} v-6" '
                   f'class="pc-span{" pc-span-us" if hot else ""}"/>')
        out.append(_t((x0 + x1) / 2, y + 36, lab,
                      "pc-spant" + (" pc-spant-us" if hot else ""), "middle"))
    return "".join(out)


def _stepped_row(states: list[dict], n: int, L: float, top: float, cw: float,
                 gap: float, ch_: float, h: dict) -> tuple[str, float]:
    """One row of a strip in every state a step carries it through.

    Each cell is one *slot of the buffer* rather than one position, so it keeps
    its identity across the step: a state's `shift` slides the whole row that
    many positions to the left, the slots that pass the front leave, and the
    fresh ones waiting past the right edge come in. Stepped through, the room
    follows each slot as its value changes and, on a `cycle`, sees the row
    return to the shape it started from — which is the claim a pair of stacked
    rows cannot make.

    The row is clipped to its own track by a nested `<svg>` a few pixels wider
    than the cells, so a slot on its way in or out disappears at the strip's
    edge instead of crossing the row's label or the frame. A state's `mark`
    is drawn inside the sliding row, on the slots it outlines: when the next
    state shifts, the outline travels with the slots it named rather than
    fading out over cells that are no longer those slots.

    Returns the markup and the y the next row starts at.
    """
    pitch = cw + gap
    off = [0]
    for st in states[1:]:
        off.append(off[-1] + int(st.get("shift", 0)))
    ns = len(states)
    m = 4
    cells = []
    for k in range(n + off[-1]):
        pos = [k - off[s] for s in range(ns)]
        shown = [s for s in range(ns) if 0 <= pos[s] < n]
        if not shown:
            continue
        vals = []
        for s in range(ns):
            # Off the row, a slot keeps the value it has where it is seen, so
            # it slides out of the track at its own shade rather than changing it.
            near = s if s in shown else min(shown, key=lambda t: (abs(t - s), t))
            vals.append(max(0.0, min(1.0, float(states[near]["cells"][pos[near]]))))
        tip = " → ".join(f"{v:.2f}" for v in vals)
        cells.append(_shown(shown, (
            f'<rect x="{k * pitch:.1f}" y="0" width="{cw:.1f}" height="{ch_:.1f}" '
            f'rx="4" class="pc-cell pc-slot" '
            f'{_vars(f=[_shade(v) for v in vals])}>'
            f'<title>{c.esc(h.get("value", "값"))} = {c.esc(tip)}</title></rect>')))
    for s, st in enumerate(states):
        if st.get("mark"):
            a, b, _ = st["mark"]
            x0 = (a + off[s]) * pitch - 3
            x1 = (b + off[s]) * pitch - gap + 3
            cells.append(_shown([s], (
                f'<rect x="{x0:.1f}" y="-3" width="{x1 - x0:.1f}" '
                f'height="{ch_ + 6:.1f}" rx="6" class="pc-mark"/>')))
    slide = (f'<g class="pc-slide" '
             f'{_vars(dx=[f"{-o * pitch:.1f}px" for o in off])}>{"".join(cells)}</g>')
    out = [f'<svg class="pc-track-clip" x="{L - m:.1f}" y="{top - m:.1f}" '
           f'width="{n * pitch - gap + 2 * m:.1f}" height="{ch_ + 2 * m:.1f}" '
           f'overflow="hidden"><g transform="translate({m} {m})">{slide}</g></svg>']
    y = top + ch_
    has_spans = any(st.get("regions") or st.get("mark") for st in states)
    for s, st in enumerate(states):
        spans = list(st.get("regions", []))
        if st.get("mark"):
            spans.append([st["mark"][0], st["mark"][1], st["mark"][2], True])
        out.append(_shown([s], _spans(spans, L, cw, gap, y)))
    if has_spans:
        y += 44
    return "".join(out), y + 14


# ── timing: rows on one clock ─────────────────────────────────────────

def timing(t: dict, ratio: float | None = None) -> str:
    """Rows on one millisecond ruler, the control period as its grid.

    Two readings of one drawing. **Call paths**: each row is one way of making
    a call, ending on its `mark` — the path's total — and the first control
    period is washed across every row, because the question is which path fits
    inside one tick and a band the room sees a bar stop inside answers it
    without a number. **Workers**: rows running side by side, with `feeds`
    drawing what one row hands another (a cache refresh, a fresh reading) as
    an arrow at the moment it happens, `dots` marking a signal read once a
    tick, `band` washing the one tick the slide is about, and `brace`
    measuring a span over a row — the age of what that tick is working from.

    The ruler's caption names the clock — the hardware and rate the times were
    measured on — because a tick is only a length on one machine.

    Waiting segments are grey, the slow worker's are the cool tone, and what
    runs on the fast path takes the accent, so the eye goes to what is left of
    the call rather than to what was removed.
    """
    span = t["span_ms"]
    per = t["제어주기"]["ms"]
    rows = t["줄"]
    ticks_as = t.get("눈금", "ms")
    brace = t.get("brace")
    head = 64 + (44 if brace else 0)
    row_h, height, W = _fit(head + 70, len(rows), 66, 112, ratio)
    bar = min(50, row_h * .56)
    L = min(max(max(_tw(r["name"], 19), _tw(r.get("note", ""), 15))
                for r in rows) + 30, 330)
    marks = any(r.get("mark") for r in rows)
    R = W - (max(_tw(r["mark"]["label"], 19) for r in rows if r.get("mark")) + 34
             if marks else 16)
    T = head
    B = T + row_h * len(rows)

    def px(ms: float) -> float:
        return L + ms / span * (R - L)

    def cy_of(j: int) -> float:
        return T + row_h * j + row_h / 2

    band = t.get("band", {"at": 0, "ms": per, "label": "한 " + t["제어주기"]["label"]})
    out = []
    if band:
        out.append(f'<rect x="{px(band["at"]):.1f}" y="{T - 12}" '
                   f'width="{px(band["at"] + band["ms"]) - px(band["at"]):.1f}" '
                   f'height="{B - T + 12:.1f}" class="pc-band"/>')
        if band.get("label"):
            out.append(_t(px(band["at"] + band["ms"] / 2), T - 22, band["label"],
                          "pc-bandt", "middle"))
    k = 0
    while k * per <= span + 1e-9:
        x = px(k * per)
        out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{T - 12}" y2="{B:.1f}" '
                   f'class="pc-grid{" pc-base" if k == 0 else ""}"/>')
        out.append(_t(x, B + 28, f"{k * per:g}" if ticks_as == "ms" else str(k),
                      "pc-tick", "middle"))
        k += 1
    unit = "ms" if ticks_as == "ms" else "tick"
    clock = f' · {t["clock"]}' if t.get("clock") else ""
    out.append(_t(R, B + 58, f'{unit} — 세로선 한 칸이 {t["제어주기"]["label"]} '
                             f'({per:g} ms){clock}', "pc-axis", "end"))

    for j, r in enumerate(rows):
        cy = cy_of(j)
        us = " pc-row-us" if r.get("us") else ""
        drawn = [_t(L - 18, cy + (-3 if r.get("note") else 7), r["name"],
                    f"pc-row{us}", "end")]
        if r.get("note"):
            drawn.append(_t(L - 18, cy + 21, r["note"], "pc-xs", "end"))
        for b in r.get("blocks", []):
            x0, x1 = px(b["at"]) + 1.5, px(b["at"] + b["ms"]) - 1.5
            kind = b.get("kind", "wait")
            drawn.append(f'<rect x="{x0:.1f}" y="{cy - bar / 2:.1f}" '
                         f'width="{x1 - x0:.1f}" height="{bar:.1f}" rx="5" '
                         f'class="pc-{kind}"><title>{c.esc(b["label"])} · '
                         f'{b["ms"]:g} ms</title></rect>')
            # A label that does not fit at the row's size is set a size down
            # before it is dropped; the `<title>` carries it either way.
            for size, cls in ((16, ""), (13, " pc-blk-sm")):
                if x1 - x0 > _tw(b["label"], size) + 8:
                    drawn.append(_t((x0 + x1) / 2, cy + 6, b["label"],
                                    f"pc-blk pc-blk-{kind}{cls}", "middle"))
                    break
        dots = r.get("dots")
        if dots:
            into = dots.get("into") if isinstance(dots, dict) else None
            m = 0
            while (m + .5) * per <= span:
                x = px((m + .5) * per)
                if into is not None:
                    tgt = cy_of(into)
                    y0, y1 = (cy - 12, tgt + bar / 2 + 4) if tgt < cy else (cy + 12, tgt - bar / 2 - 4)
                    drawn.append(_arrow(x, y0, x, y1, "pc-feed-us"))
                drawn.append(f'<circle cx="{x:.1f}" cy="{cy:.1f}" r="8" class="pc-dot"/>')
                m += 1
        mk = r.get("mark")
        if mk:
            x = px(mk["at"])
            hot = mk.get("us")
            drawn.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{cy - bar / 2 - 8:.1f}" '
                         f'y2="{cy + bar / 2 + 8:.1f}" '
                         f'class="pc-mkl{" pc-mkl-us" if hot else ""}"/>')
            drawn.append(_t(x + 12, cy + 7, mk["label"],
                            "pc-mkt pc-mkt-us" if hot else "pc-mkt"))
        out.append(_build(r, "".join(drawn)))

    for f in t.get("feeds", []):
        (ra, ta), (rb, tb) = f["from"], f["to"]
        ya, yb = cy_of(ra), cy_of(rb)
        down = yb > ya
        y0 = ya + (bar / 2 if down else -bar / 2)
        y1 = yb - (bar / 2 + 4 if down else -bar / 2 - 4)
        out.append(_arrow(px(ta), y0, px(tb), y1, "pc-feed"))

    if brace:
        r = brace["row"]
        top = cy_of(r) - bar / 2 - 14
        x0, x1 = px(brace["from"]), px(brace["to"])
        out.append(f'<path d="M{x0:.1f} {top:.1f} v-10 H{x1:.1f} v10" class="pc-brace"/>')
        out.append(_t((x0 + x1) / 2, top - 20, brace["label"], "pc-note pc-mid", "middle"))
    return _svg(W, B + 70, "".join(out), {k: v for k, v in t.items() if k != "clock"})


def _arrow(x0: float, y0: float, x1: float, y1: float, cls: str) -> str:
    """A shaft and its head, drawn as paths rather than an SVG marker — a marker
    is an id, and ids collide once two figures share a page."""
    a = math.atan2(y1 - y0, x1 - x0)
    h = 9
    lx, ly = x1 - h * math.cos(a - .45), y1 - h * math.sin(a - .45)
    rx, ry = x1 - h * math.cos(a + .45), y1 - h * math.sin(a + .45)
    return (f'<path d="M{x0:.1f} {y0:.1f} L{x1:.1f} {y1:.1f}" class="{cls}"/>'
            f'<path d="M{lx:.1f} {ly:.1f} L{x1:.1f} {y1:.1f} L{rx:.1f} {ry:.1f}" '
            f'class="{cls} pc-head"/>')


def _shade(v: float) -> str:
    """One hue, light to dark: the low ground at 0, the accent's ink at 1."""
    return f"color-mix(in oklch, var(--pc-hi) {v * 100:.0f}%, var(--pc-lo))"


def _svg(width: float, height: float, body: str, spec: dict,
         steps: list[str] | None = None, cycle: bool = False) -> str:
    """The drawing and the one line of provenance under it.

    What is printed under a drawing is `source` — where every value is stated
    and the setup it was measured in — and, when the drawing picked any of its
    parameters itself, `illustrative` in front of it, so a value chosen to draw
    with is never read as the paper's setting. A chart whose values were
    measured on a clock — a delay in ticks, a latency — names it in `clock`,
    first on the line; a timing names it on its own ruler instead. `why` — which of the paper's
    figures covers this ground and what this one strips out — is the
    presenter's answer to "is that in the paper?", so `presentations.py` closes
    the speaker essay on it rather than setting a paragraph under the figure.

    `steps` names the states of a stepped figure, in order; the figure then
    carries its state count and, above the drawing, the row that names them.
    `cycle` marks a figure whose last state is its first again, which the
    presenter steps through as a loop.
    """
    ill = (f'<span class="pc-ill">예시 · {c.esc(spec["illustrative"])}</span>'
           if spec.get("illustrative") else "")
    clock = (f'<span class="pc-clock">{c.esc(spec["clock"])}</span>'
             if spec.get("clock") else "")
    cap = (f'<figcaption>{clock}{ill}{c.esc(spec.get("source", ""))}</figcaption>'
           if spec.get("source") or ill or clock else "")
    stepped = ""
    if steps:
        stepped = (f' data-steps="{len(steps)}" data-at="0"'
                   + (" data-cycle" if cycle else ""))
    return (f'<figure class="prs-dfig{" prs-stepped" if steps else ""}"{stepped}>'
            + (_stepper(steps) if steps else "")
            + f'<svg viewBox="0 0 {width:.0f} {height:.0f}" preserveAspectRatio="xMidYMid meet" '
            f'role="img" aria-label="{c.esc(spec.get("alt", ""))}">{body}</svg>'
            f'{cap}</figure>')


# ── lineage: where the paper stands, and what flowed into it ──────────
#
# Two figures place a paper among the work it names, and a talk carries both
# (`presentation/AUTHORING.md` §4-9). `contrast` sets the priors against the
# properties the paper contrasts itself on, so the room sees the gap the paper
# fills; `inheritance` draws what flowed in from each prior and what the paper
# adds, so the room sees what is new. Both take every word from the paper's
# own sentences about its priors, date each prior the same way, and link a
# prior the corpus has a rewrite of.

# The two lineage fences, which `presentations.py` draws beside the others.
LINEAGE = ("contrast", "inheritance")

_ARXIV_ID = re.compile(r"^\d{4}\.\d{4,5}$")
_WHEN = re.compile(r"^(\d{4})(?:\.(\d{2}))?$")


def _rewrite_link(pid: str, body: str, cls: str) -> str:
    """`body` as a link to the corpus's rewrite of `pid`, opening beside the
    talk so the stage stays where it is."""
    return (f'<a href="../{c.esc(pid)}/index.html" target="_blank" rel="noopener" '
            f'class="{cls}"><title>{c.esc(pid)} — PROBE 재작성으로</title>{body}</a>')


def _dated(where: str, fence: str, node: dict, mine: bool = False) -> list[str]:
    """A prior's date is its arXiv id's first-version month, which the id
    itself encodes, or the venue year when the bibliography gives no id — so a
    month with no id to read it from is a date nobody can check. This paper's
    own node is dated from the paper, which the linter reads off the file."""
    name = node.get("name")
    when = str(node.get("when", ""))
    m = _WHEN.match(when)
    if not m:
        return [f"{where}: ```probe-{fence} {name!r} `when` is {when!r} — `YYYY.MM` "
                f"from an arXiv id, or the venue year"]
    pid = node.get("id")
    if pid is None:
        if m.group(2) and not mine:
            return [f"{where}: ```probe-{fence} {name!r} is dated to the month "
                    f"{when} with no `id` — a month is read off the cited arXiv "
                    f"id; with none, the venue year"]
        return []
    pid = str(pid)
    if not _ARXIV_ID.match(pid):
        return [f"{where}: ```probe-{fence} {name!r} `id` {pid!r} is not an arXiv id"]
    if when != f"20{pid[:2]}.{pid[2:4]}":
        return [f"{where}: ```probe-{fence} {name!r} is dated {when} but its arXiv "
                f"id {pid} was first posted 20{pid[:2]}.{pid[2:4]}"]
    return []


# The four readings a contrast cell can take, and what each one states about
# the paper's own sentence on that prior: it says the prior does this, does it
# in part, does not — or says nothing, which is drawn as nothing rather than
# guessed into one of the other three.
CONTRAST_MARKS = {"●": "한다", "◐": "일부", "○": "못 한다", "–": "원문 언급 없음"}


def _mark(v: str, x: float, y: float, r: float, us: bool, tip: str) -> str:
    """One cell's glyph, drawn rather than set as text, so every glyph is the
    same size in every font and the half-filled one is really half."""
    tone = "pc-us" if us else "pc-ref"
    title = f"<title>{c.esc(tip)}</title>"
    if v == "●":
        return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" '
                f'class="pc-ct-full {tone}">{title}</circle>')
    if v == "◐":
        return (f'<g class="pc-ct-half {tone}">{title}'
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r - 1.4:.1f}" class="pc-ct-ring"/>'
                f'<path d="M{x:.1f} {y - r + 1.4:.1f} A{r - 1.4:.1f} {r - 1.4:.1f} 0 0 0 '
                f'{x:.1f} {y + r - 1.4:.1f} Z" class="pc-ct-fill"/></g>')
    if v == "○":
        return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r - 1.4:.1f}" '
                f'class="pc-ct-ring pc-ct-none">{title}</circle>')
    return (f'<line x1="{x - r * .45:.1f}" y1="{y:.1f}" x2="{x + r * .45:.1f}" '
            f'y2="{y:.1f}" class="pc-ct-dash">{title}</line>')


def contrast(spec: dict, ratio: float | None = None,
             corpus: frozenset | set = frozenset()) -> str:
    """The priors a paper names, against the properties it contrasts itself on.

    Rows are the prior work in the order it appeared — its date in the left
    margin on one rail, so the matrix is read down as a flow as well as across
    as a difference — with this paper last, in the accent. Columns are the
    properties the paper's own text uses to say how it differs, phrased as it
    phrases them. Each cell is a drawn glyph, and its `n` — the paper's
    sentence and section it rests on — is the glyph's `<title>`, so every mark
    is one hover away from what makes it checkable.

    `key` is the column the paper alone fills, and it is drawn as the
    contribution: a band down the whole column in the accent's tint, ruled in
    the accent, with `key_note` under it. The build refuses a key column that
    any prior fills, so the band never claims a first the paper does not.

    A prior whose arXiv id has a rewrite in `analysis/` (`corpus`) links to it
    and carries the mark that says so, handing the room the next thing to
    read.

    `step` on this paper's row holds the row and the key note back until the
    presenter's press, so the room first sees the priors and the band standing
    empty over them — the gap before what fills it.
    """
    cols = spec["cols"]
    rows = spec["rows"]
    key = spec.get("key")
    n = len(cols)

    head_lines = max(len(h.split(" / ")) for h in cols)
    head_h = 16 + head_lines * 25
    used = [m for r in rows for m in (_cell(v)[0] for v in r["cells"])]
    legend = [m for m in CONTRAST_MARKS if m in used]
    note = spec.get("key_note")
    # The key note and the glyphs' key share one line under the grid — the
    # note under its column, the key from the left edge — so the grid keeps
    # the height a second line would take.
    foot = 48
    fixed = head_h + foot + 4
    pitch, height, W = _fit(fixed, len(rows), 48, 92, ratio)

    # The left margin holds the date rail and the names; the rest is shared
    # evenly between the columns, so no column reads as weightier by width.
    when_w = max((_tw(r.get("when", ""), 17) for r in rows), default=0) + 34
    name_w = max(_tw(r["name"], 25) + (86 if r.get("id") in corpus and not r.get("us")
                                       else 0) for r in rows)
    sub_w = max((_tw(r.get("sub", ""), 17) for r in rows), default=0)
    L = when_w + max(name_w, sub_w) + 24
    R = W - 6
    cw = (R - L) / n
    rad = min(pitch * .32, cw * .2, 24)

    out = []
    top = head_h
    bottom = top + pitch * len(rows)
    us_i = next(i for i, r in enumerate(rows) if r.get("us"))

    # This paper's row, on a ground of its own under the grid, and the
    # contribution over it: the key band is a tint rather than a fill, so
    # where the two cross — this paper's cell in the key column — is the
    # darkest ground on the figure. Everything of this paper's row goes in
    # `mine`, which a `step` holds back as one piece.
    y_us = top + us_i * pitch
    mine = [f'<rect x="0" y="{y_us + 4:.1f}" width="{R:.1f}" height="{pitch - 8:.1f}" '
            f'rx="12" class="pc-ct-us"/>']
    if isinstance(key, int):
        x0 = L + key * cw + 6
        out.append(f'<rect x="{x0:.1f}" y="2" width="{cw - 12:.1f}" '
                   f'height="{bottom + (foot - 6 if note else 8):.1f}" rx="16" '
                   f'class="pc-ct-key"/>')

    # Column heads, bottom-aligned on the grid's top edge.
    for j, h in enumerate(cols):
        lines = h.split(" / ")
        cx = L + j * cw + cw / 2
        cls = "pc-ct-head" + (" pc-ct-head-key" if j == key else "")
        for k, ln in enumerate(lines):
            y = top - 16 - (len(lines) - 1 - k) * 25
            out.append(_t(cx, y, ln, cls, "middle"))

    # The date rail: one line down the margin, a tick at each row, so the
    # order of the rows reads as time before the cells are read at all.
    rail_x = 8
    last = top + (us_i - .5) * pitch + 7
    out.append(f'<line x1="{rail_x}" y1="{top + pitch / 2:.1f}" x2="{rail_x}" '
               f'y2="{last:.1f}" class="pc-ct-rail"/>')
    mine.append(f'<line x1="{rail_x}" y1="{last:.1f}" x2="{rail_x}" '
                f'y2="{y_us + pitch / 2:.1f}" class="pc-ct-rail"/>')

    for i, r in enumerate(rows):
        y = top + i * pitch
        cy = y + pitch / 2
        us = bool(r.get("us"))
        row = mine if us else out
        row.append(f'<circle cx="{rail_x}" cy="{cy:.1f}" r="{6 if us else 4.5}" '
                   f'class="pc-ct-tick{" pc-us" if us else ""}"/>')
        row.append(_t(rail_x + 18, cy + 6, r.get("when", ""),
                      "pc-ct-when" + (" pc-ct-when-us" if us else "")))
        sub = r.get("sub")
        ny = cy + (-3 if sub else 9)
        name = _t(when_w, ny, r["name"], "pc-ct-name" + (" pc-ct-name-us" if us else ""))
        pid = r.get("id")
        if pid in corpus and not us:
            # A rewrite exists: the name is the way to it, and the pill says so
            # to a room that cannot hover.
            px = when_w + _tw(r["name"], 25) + 12
            name = _rewrite_link(pid, name
                                 + f'<rect x="{px:.1f}" y="{ny - 21:.1f}" width="72" '
                                   f'height="26" rx="13" class="pc-ct-pill"/>'
                                 + _t(px + 36, ny - 2.5, "재작성 ↗", "pc-ct-pillt", "middle"),
                                 "pc-ct-link")
        row.append(name)
        if sub:
            row.append(_t(when_w, cy + 20, sub, "pc-ct-sub"))
        for j, v in enumerate(r["cells"]):
            mark, tip = _cell(v)
            cx = L + j * cw + cw / 2
            label = f'{r["name"]} · {cols[j].replace(" / ", " ")} — {CONTRAST_MARKS[mark]}'
            row.append(_mark(mark, cx, cy, rad, us, f"{label}. {tip}" if tip else label))

    ly = bottom + 34
    if isinstance(key, int) and note:
        mine.append(_t(L + key * cw + cw / 2, ly, note, "pc-note", "middle"))
    out.append(_build(rows[us_i], "".join(mine)))

    # The key to the glyphs, only the ones the matrix uses.
    x = 0.0
    for m in legend:
        out.append(_mark(m, x + 10, ly - 6, 9, False, CONTRAST_MARKS[m]))
        out.append(_t(x + 26, ly, CONTRAST_MARKS[m], "pc-key"))
        x += 26 + _tw(CONTRAST_MARKS[m], 17) + 18
    return _svg(W, bottom + foot, "".join(out), spec)


def _cell(v) -> tuple[str, str]:
    """(glyph, the paper's sentence under it) for a cell written either as
    the glyph alone or as `{"v": glyph, "n": sentence}`."""
    if isinstance(v, dict):
        return str(v.get("v", "")), str(v.get("n", ""))
    return str(v), ""


def _contrast_problems(where: str, spec: dict) -> list[str]:
    out = []
    cols = spec.get("cols")
    rows = spec.get("rows")
    if not (isinstance(cols, list) and 2 <= len(cols) <= 5
            and all(isinstance(h, str) and h.strip() for h in cols)):
        return [f"{where}: ```probe-contrast `cols` is two to five column heads — "
                f"the properties the paper contrasts itself on, as it phrases them"]
    if not (isinstance(rows, list) and 2 <= len(rows) <= 6):
        return [f"{where}: ```probe-contrast `rows` is two to six rows — the priors, "
                f"then this paper"]
    us = [i for i, r in enumerate(rows) if isinstance(r, dict) and r.get("us")]
    if us != [len(rows) - 1]:
        out.append(f"{where}: ```probe-contrast marks this paper `us` on its last row, "
                   f"and on no other")
    for r in rows:
        if not isinstance(r, dict) or not str(r.get("name", "")).strip():
            out.append(f"{where}: ```probe-contrast row {r!r} has no `name`")
            continue
        cells = r.get("cells")
        if not isinstance(cells, list) or len(cells) != len(cols):
            out.append(f"{where}: ```probe-contrast row {r['name']!r} has "
                       f"{len(cells) if isinstance(cells, list) else 0} cells for "
                       f"{len(cols)} columns")
            continue
        bad = [v for v in cells if _cell(v)[0] not in CONTRAST_MARKS]
        if bad:
            out.append(f"{where}: ```probe-contrast row {r['name']!r} has cells "
                       f"{bad!r} — each is one of {' '.join(CONTRAST_MARKS)}")
        bare = [j for j, v in enumerate(cells)
                if _cell(v)[0] in "●◐○" and not _cell(v)[1].strip()]
        if bare and not r.get("us"):
            out.append(f"{where}: ```probe-contrast row {r['name']!r}: cells "
                       f"{bare} carry no `n` — every mark on a prior is the paper's "
                       f"sentence about it, and `n` names where it says so")
        out += _dated(where, "contrast", r, bool(r.get("us")))
    key = spec.get("key")
    if not (isinstance(key, int) and not isinstance(key, bool) and 0 <= key < len(cols)):
        out.append(f"{where}: ```probe-contrast `key` is the column only this paper "
                   f"fills, as an index (0 – {len(cols) - 1})")
    elif not out:
        if _cell(rows[-1]["cells"][key])[0] != "●":
            out.append(f"{where}: ```probe-contrast `key` column is the one this "
                       f"paper fills — its own cell there is ●")
        filled = [r["name"] for r in rows[:-1] if _cell(r["cells"][key])[0] == "●"]
        if filled:
            out.append(f"{where}: ```probe-contrast `key` column is drawn as the "
                       f"contribution, but {', '.join(filled)} also fill it — a "
                       f"band there would claim a first the paper does not")
    return out


def inheritance(spec: dict, ratio: float | None = None,
                corpus: frozenset | set = frozenset()) -> str:
    """The priors this paper takes something from, flowing into it.

    Each prior stands on the left under its date and name, and its edge into
    the paper carries what the paper takes from it — a short noun phrase the
    paper itself states, with the section that says so under it. The paper
    stands on the right as the one node in the accent, listing what it adds
    that none of the priors had. So the drawing answers the two questions a
    room asks of a method it has just been shown — what came from where, and
    what is new — in one look, without a legend.

    `open` is the question the paper leaves — its own limitation or future
    work — drawn as a dashed edge out of the paper node, because it did not
    flow in. Work the paper names as concurrent is not drawn here: it ran
    beside the paper rather than into it, and it stands as a row of the
    talk's contrast instead.

    A prior whose arXiv id has a rewrite in the corpus links to it, marked
    `재작성 ↗`: the talk compresses the prior into a noun phrase, and the
    corpus is where the rest of it is one click away.

    Edges land on the paper node spread across its left side rather than at
    one point, so each inheritance stays its own line to the end; the node is
    shorter than the column of priors, so they visibly converge.
    """
    lines = spec["lines"]
    me, opn = spec["me"], spec.get("open")
    n = len(lines)
    rows = n + (1 if opn else 0)

    def marked(node: dict) -> bool:
        return str(node.get("id", "")) in corpus

    # The column of names is as wide as its widest name, so the edges get the
    # rest; the paper node as wide as its own name or its widest addition.
    # Names are mostly Latin in a bold face whose lower case runs near half an
    # em, so they are measured closer than `_tw` measures a label: the column
    # ends where the names do, and the edges start there.
    def bare_w(node: dict) -> float:
        return sum(1.0 if ord(ch) > 0x2000 else .68 if ch.isupper() else .54
                   for ch in node["name"]) * 23

    def name_w(node: dict) -> float:
        return bare_w(node) + (_tw("재작성 ↗", 15) + 14 if marked(node) else 0)

    Lw = min(max(max(name_w(x) for x in lines),
                 max(_tw(x.get("when", ""), 16) for x in lines)) + 8, 330)
    Lw = max(Lw, 170)
    adds = me["adds"]
    Wme = min(max(_tw(me["name"], 40), max(_tw(a, 21) for a in adds) + 44,
                  _tw("새로 더한 것", 15)) + 56, 400)
    Wme = max(Wme, 300)
    # A long name is set down until it fits the node rather than widening it
    # into the edges' room.
    me_size = min(40, (Wme - 56) / max(_tw(me["name"], 1), 1))
    head = 8
    pitch, height, W = _fit(head + 12, rows, 74, 132, ratio)
    X = W - Wme
    # The open question takes a row's height under the paper node, and the
    # priors spread over the whole of it, so the column of names stands as
    # tall as the node and the question together.
    pitch = (height - head - 12) / n

    def cy(i: int) -> float:
        return head + pitch * i + pitch / 2

    out = []
    # The paper node: centred on the priors it gathers, as tall as it needs,
    # and high enough to leave the open question its line under it.
    box_h = 34 + 46 + 30 + 34 * len(adds) + 16
    mid = (cy(0) + cy(n - 1)) / 2
    top = max(head, mid - box_h / 2)
    if opn:
        top = max(head, min(top, height - 12 - 70 - box_h))
    bot = top + box_h
    # Where each edge lands on the node's left side.
    span = min(box_h - 36, pitch * (n - 1) * .55) if n > 1 else 0
    land = [mid - span / 2 + (span / (n - 1) * i if n > 1 else 0) for i in range(n)]

    def node(x: dict, y: float) -> str:
        name = _t(0, y + 13, x["name"], "pc-ih-name")
        if marked(x):
            name = _rewrite_link(str(x["id"]), name
                                 + _t(bare_w(x) + 12, y + 12, "재작성 ↗", "pc-ih-cor"),
                                 "pc-ih-link")
        return (f'<g class="pc-ih-node"><title>{c.esc(x.get("when", ""))} · '
                f'{c.esc(x["name"])}</title>'
                + _t(0, y - 16, x.get("when", ""), "pc-ih-when") + name
                + f'<circle cx="{Lw + 12:.1f}" cy="{y:.1f}" r="6" class="pc-ih-dot"/></g>')

    x0 = Lw + 24
    bend = X - 120
    for i, ln in enumerate(lines):
        y, yl = cy(i), land[i]
        out.append(node(ln, y))
        out.append(f'<path d="M{x0:.1f} {y:.1f} H{bend:.1f} '
                   f'C{bend + 70:.1f} {y:.1f} {X - 60:.1f} {yl:.1f} {X - 4:.1f} {yl:.1f}" '
                   f'class="pc-ih-edge"/>')
        out.append(_arrow(X - 16, yl, X - 3, yl, "pc-ih-edge"))
        # What the paper takes from this prior, over the edge's straight run,
        # and under it where the paper says so — the claim and its second
        # register, on either side of the line they are about.
        small = _tw(ln["gave"], 21) > bend - x0 - 10
        out.append(_t(x0 + 10, y - 12, ln["gave"],
                      "pc-ih-gave" + (" pc-ih-gave-sm" if small else "")))
        if ln.get("where"):
            out.append(_t(x0 + 10, y + 27, ln["where"], "pc-ih-where"))

    items = "".join(
        f'<text x="{X + 30:.1f}" y="{top + 34 + 46 + 30 + 34 * k + 22:.1f}" '
        f'class="pc-ih-add"><tspan class="pc-ih-plus">+</tspan> {c.esc(a)}</text>'
        for k, a in enumerate(adds))
    out.append(f'<g class="pc-ih-me"><title>{c.esc(me.get("when", ""))} · '
               f'{c.esc(me["name"])}</title>'
               f'<rect x="{X:.1f}" y="{top:.1f}" width="{Wme:.1f}" height="{box_h:.1f}" '
               f'rx="10" class="pc-ih-box"/>'
               f'<rect x="{X:.1f}" y="{top:.1f}" width="7" height="{box_h:.1f}" '
               f'class="pc-ih-band"/>'
               + _t(X + 30, top + 30, me.get("when", ""), "pc-ih-when")
               + _t(X + 30, top + 34 + 40, me["name"], "pc-ih-mename")
                 .replace(' class=', f' style="font-size:{me_size:.0f}px" class=', 1)
               + _t(X + 30, top + 34 + 46 + 22, "새로 더한 것", "pc-ih-cap")
               + items + "</g>")

    if opn:
        ax = X + 40
        ya = bot + 6
        yt = bot + 50
        out.append(_arrow(ax, ya, ax, yt - 22, "pc-ih-edge pc-ih-dash"))
        out.append(_t(ax + 18, yt - 20, "남긴 질문" + (f' · {opn["where"]}' if opn.get("where") else ""),
                      "pc-ih-cap"))
        out.append(_t(ax + 18, yt + 4, opn["text"], "pc-ih-open"))
        height = max(height, yt + 16)

    return _svg(W, height, "".join(out), spec)


def _inheritance_problems(where: str, spec: dict) -> list[str]:
    out = []
    lines = spec.get("lines")
    if not (isinstance(lines, list) and 1 <= len(lines) <= 4):
        return [f"{where}: ```probe-inheritance `lines` is one to four priors the "
                f"paper takes something from — past four the edges crowd too close "
                f"to label"]
    for ln in lines:
        if not (isinstance(ln, dict) and str(ln.get("name", "")).strip()
                and str(ln.get("gave", "")).strip()):
            out.append(f"{where}: ```probe-inheritance line {ln!r} needs `name` and "
                       f"`gave` — who, and what the paper takes from them")
            continue
        out += _dated(where, "inheritance", ln)
    me = spec.get("me")
    if not (isinstance(me, dict) and str(me.get("name", "")).strip()
            and isinstance(me.get("adds"), list) and 1 <= len(me["adds"]) <= 4
            and all(isinstance(a, str) and a.strip() for a in me["adds"])):
        out.append(f"{where}: ```probe-inheritance `me` needs `name` and one to four "
                   f"`adds` — what this paper brings that none of the lines had")
    else:
        out += _dated(where, "inheritance", me, True)
    opn = spec.get("open")
    if opn is not None and not (isinstance(opn, dict)
                                and str(opn.get("text", "")).strip()):
        out.append(f"{where}: ```probe-inheritance `open` needs `text` — the "
                   f"question the paper itself leaves")
    return out


KINDS = {"line": line, "dots": dots, "scatter": scatter}


def chart(ch: dict, ratio: float | None = None) -> str:
    return KINDS[ch["kind"]](ch, ratio)


def _is_num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def problems(where: str, fence: str, spec) -> list[str]:
    """What the build needs to draw the figure, and the provenance it will not
    draw without. A non-empty list means the slide is skipped, not drawn wrong."""
    out = []
    if not isinstance(spec, dict):
        return [f"{where}: ```probe-{fence} is not an object"]
    need = ("source", "why") if fence in ("chart", "heat") + LINEAGE else ()
    gone = [k for k in need if not str(spec.get(k, "")).strip()]
    if gone:
        out.append(f"{where}: ```probe-{fence} has no `" + "`, `".join(gone)
                   + ("` — a lineage figure names the sections its phrases come "
                      "from and which of the paper's paragraphs it gathers"
                      if fence in LINEAGE else
                      "` — a data figure names where every number is stated and "
                      "which of the paper's own figures it redraws"))
    om = spec.get("omitted")
    if om is not None and not (isinstance(om, list) and all(isinstance(o, str) for o in om)):
        out.append(f"{where}: ```probe-{fence} `omitted` is not a list of strings — "
                   f"one entry per source row the figure leaves out")
    if fence == "chart":
        kind = spec.get("kind")
        if kind not in KINDS:
            out.append(f"{where}: ```probe-chart `kind` is {kind!r} — "
                       f"one of {' '.join(KINDS)}")
            return out
        series = spec.get("series") or []
        n_us = sum(1 for s in series if s.get("us"))
        if n_us > 1:
            out.append(f"{where}: ```probe-chart marks {n_us} series `us` — at most "
                       f"one series is the point of the chart")
        names = {s.get("name") for s in series}
        if kind == "scatter":
            for s in series:
                pts = s.get("points")
                if not isinstance(pts, list) or not pts:
                    out.append(f"{where}: ```probe-chart scatter series {s.get('name')!r} "
                               f"has no `points`")
                    continue
                for p in pts:
                    if not (isinstance(p, dict) and _is_num(p.get("x")) and _is_num(p.get("y"))):
                        out.append(f"{where}: ```probe-chart scatter point {p!r} needs "
                                   f"numeric `x` and `y`")
            for ax in ("x", "y"):
                a = spec.get(ax) or {}
                if not all(_is_num(a.get(k)) for k in ("min", "max", "step")):
                    out.append(f"{where}: ```probe-chart scatter `{ax}` needs `min`, "
                               f"`max` and `step`")
        else:
            xa = spec.get("x") or {}
            n = len(xa.get("ticks", [])) if kind == "line" else len(spec.get("rows", []))
            for s in series:
                vals = s.get("values", [])
                if len(vals) != n:
                    out.append(f"{where}: ```probe-chart series {s.get('name')!r} has "
                               f"{len(vals)} values for {n} positions")
                if any(v is not None and not _is_num(v) for v in vals):
                    out.append(f"{where}: ```probe-chart series {s.get('name')!r} has a "
                               f"value that is neither a number nor null")
                if vals and all(v is None for v in vals):
                    out.append(f"{where}: ```probe-chart series {s.get('name')!r} has "
                               f"no values at all")
            if kind == "line" and "values" in xa:
                xv = xa["values"]
                if (not isinstance(xv, list) or len(xv) != n
                        or not all(_is_num(v) for v in xv)):
                    out.append(f"{where}: ```probe-chart `x.values` needs one number "
                               f"per tick")
                elif any(b <= a for a, b in zip(xv, xv[1:])):
                    out.append(f"{where}: ```probe-chart `x.values` must increase")
            if kind == "dots":
                for r in spec.get("rows", []):
                    if r.get("vs") and r["vs"] not in names:
                        out.append(f"{where}: ```probe-chart row {r.get('name')!r} "
                                   f"measures against {r['vs']!r}, which is not a series")
            note = spec.get("note") or {}
            for k in ("of", "from"):
                if note.get(k) and note[k] not in names:
                    out.append(f"{where}: ```probe-chart `note.{k}` names {note[k]!r}, "
                               f"which is not a series")
            if note.get("side") not in (None, "left", "right"):
                out.append(f"{where}: ```probe-chart `note.side` is left or right")
            if note.get("place") not in (None, "above", "below", "middle"):
                out.append(f"{where}: ```probe-chart `note.place` is above, below or middle")
        if spec.get("vs") and spec["vs"] not in names:
            out.append(f"{where}: ```probe-chart `vs` names {spec['vs']!r}, which is "
                       f"not a series")
    if fence == "chart" and spec.get("steps") is not None:
        st = spec["steps"]
        n = len((spec.get("x") or {}).get("ticks", []))
        if spec.get("kind") != "line":
            out.append(f"{where}: ```probe-chart `steps` walks a sweep — only a "
                       f"`line` has one")
        elif (not isinstance(st, list) or not st
              or not all(isinstance(i, int) and not isinstance(i, bool) and 0 <= i < n
                         for i in st)
              or len(set(st)) != len(st)):
            out.append(f"{where}: ```probe-chart `steps` is a list of tick indices "
                       f"(0 – {n - 1}), each once — the columns the presenter walks")
    if fence == "heat":
        steps = spec.get("steps")
        stepped = [r for r in spec.get("rows", []) if "states" in r]
        if steps is not None and not (isinstance(steps, list) and len(steps) >= 2
                                      and all(isinstance(l, str) and l.strip() for l in steps)):
            out.append(f"{where}: ```probe-heat `steps` names the states, in order — "
                       f"two labels at least")
            return out
        if stepped and not steps:
            out.append(f"{where}: ```probe-heat has a row with `states` but no "
                       f"`steps` naming them")
            return out
        if steps and not stepped:
            out.append(f"{where}: ```probe-heat names `steps` but no row carries "
                       f"`states`")
        for r in spec.get("rows", []):
            for st in (r.get("states") or [r]):
                bad = [v for v in st.get("cells", []) if not 0 <= float(v) <= 1]
                if bad:
                    out.append(f"{where}: ```probe-heat row {r.get('name')!r} has values "
                               f"outside [0, 1]: {bad}")
        n = spec.get("cols")
        for r in stepped:
            sts = r["states"]
            name = r.get("name")
            if "cells" in r:
                out.append(f"{where}: ```probe-heat row {name!r} carries both `cells` "
                           f"and `states` — a stepped row's cells are its states'")
            if not isinstance(sts, list) or len(sts) != len(steps):
                out.append(f"{where}: ```probe-heat row {name!r} has "
                           f"{len(sts) if isinstance(sts, list) else 0} states for "
                           f"{len(steps)} steps")
                continue
            for k, st in enumerate(sts):
                if len(st.get("cells", [])) != n:
                    out.append(f"{where}: ```probe-heat row {name!r}, state {k}, has "
                               f"{len(st.get('cells', []))} cells for {n} columns")
                sh = st.get("shift", 0)
                if not isinstance(sh, int) or isinstance(sh, bool) or sh < 0 or (k == 0 and sh):
                    out.append(f"{where}: ```probe-heat row {name!r}, state {k}: "
                               f"`shift` is a count of positions the row slides left "
                               f"entering that state, and the first state has none")
            if spec.get("cycle") and sts[0].get("cells") != sts[-1].get("cells"):
                out.append(f"{where}: ```probe-heat is a `cycle`, but row {name!r} does "
                           f"not end on the cells it starts from — a loop the figure "
                           f"cannot close is not one")
    if fence == "contrast":
        out += _contrast_problems(where, spec)
    if fence == "inheritance":
        out += _inheritance_problems(where, spec)
    if fence == "timing":
        rows = spec.get("줄") or []
        if not rows or not spec.get("span_ms") or not (spec.get("제어주기") or {}).get("ms"):
            out.append(f"{where}: ```probe-timing needs `span_ms`, `제어주기.ms` and `줄`")
            return out
        idx = range(len(rows))
        for f in spec.get("feeds", []):
            ends = f.get("from", [None]), f.get("to", [None])
            if not all(isinstance(e, list) and len(e) == 2 and e[0] in idx for e in ends):
                out.append(f"{where}: ```probe-timing feed {f!r} needs `from` and `to` "
                           f"as [row, ms] with a row that exists")
        for r in rows:
            dots = r.get("dots")
            if isinstance(dots, dict) and dots.get("into") not in idx:
                out.append(f"{where}: ```probe-timing row {r.get('name')!r} feeds "
                           f"its dots into row {dots.get('into')!r}, which does not exist")
        br = spec.get("brace")
        if br and br.get("row") not in idx:
            out.append(f"{where}: ```probe-timing `brace` names row {br.get('row')!r}, "
                       f"which does not exist")
    return out
