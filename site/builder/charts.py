"""The results chart drawn from a paper's own numbers, as inline SVG.

One fence, ```probe-chart, which the distinction track's deep dives stand among
their §6 bullets (`distinction/AUTHORING.md` §3-5) and
`distinction/render-distinction.py` draws on their pages: `line` over a sweep,
`dots` across categories, `scatter` for one quantity against another (cost
against quality) — with at most one series marked `us` in the accent and
every other one in the de-emphasis grey.

Every colour is a site token, read through the `--pc-*` properties that
`site/builder/assets/charts.css` sets on the `.pc-frame` around the drawing,
so the light theme and the dark theme are one drawing.

The drawing fills the frame's width. The caller hands in the shape of the box
it has (`ratio`, width over height), and each kind spends the slack on the one
dimension it can stretch — a plot's height, a row's pitch — so the drawing
arrives at the box's own shape and the SVG scales to its full width. A chart
that cannot get short enough without crushing its rows widens its coordinate
space instead: its type comes out a little smaller, but the frame has no empty
flanks. Type is set in viewBox units against a 1000-wide drawing, so it scales
with the frame the way the surrounding text does.

A chart takes its numbers and phrases from the paper and nothing else. What the
drawing adds is the arrangement: which series is ours, which baseline is the
one to beat, the one annotation that carries the takeaway. A number read off
the paper's plot image is not a number the paper states, so there is no field
for an error bar or an interpolated point — and no field for a coordinate
either: the author states values, and the build places them, which is what
keeps every mark checkable against the paper by reading the fence. A number is
printed at the precision it was written in: `80.0` stays `80.0`, and a gap
between two values written to one decimal is stated to one decimal.

The rules the drawing keeps are the ones that decide whether a chart reads at
a glance:

  - one series is the point, so it is the only one in colour — the rest are
    grey, told apart by shape and by a direct label, never by hue alone;
  - a legend whenever two or more series share the plot, and direct labels
    beside it rather than instead of it;
  - hairline grid, a surface ring on every marker so overlaps stay legible,
    and text in text tokens rather than the series colour;
  - every mark carries a `<title>`, so the value is one hover away.

`omitted` — the source rows a chart leaves out on purpose — is read by the
linter and the author's self-check, never drawn.

The module imports nothing outside the standard library and `components`:
`distinction/render-distinction.py` and `linters/check-distinction-format.py`
import it on a machine that has not installed the site's dependencies.
"""

from __future__ import annotations

import re

from . import components as c

# The width every size in a drawing is set against. A figure that has to widen
# its coordinate space to reach the frame's shape does so from here.
W0 = 1000

# The shape a chart falls back to when the caller does not say.
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
        out.append("".join(key))
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
    keeps the distances it was run at and the slopes on the page are the real
    ones. A `null` value is a point the paper did not measure: the line
    breaks there rather than bridging it.

    The end labels are placed at the value they name and pushed apart only as
    far as they must be; a label that moved gets a leader back to its line, so
    it never floats free of the mark it belongs to.
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

    out = [_legend(series, ref, 18, W - _legend_width(series, True), line=True,
                   subj=subj)]
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
        out.append(tick)
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
            marks.append(_marker(
                shape, px(i), py(v), 8 if s.get("us") or s["name"] == subj else 6,
                cls, tip))
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
    for k in order:
        body = "".join(drawn[k])
        if series[k] is us:
            body += "".join(ours)
        out.append(body)
    if us is None and ours:
        out.append("".join(ours))

    return _svg(W, bottom + 10, "".join(out), ch)


# ── dots: categories side by side ─────────────────────────────────────

def dots(ch: dict, ratio: float | None = None) -> str:
    """One row per category, every series a mark on a shared scale.

    The distance that matters — ours against the row's strongest baseline, or
    the baseline the row names in its own `vs` — is drawn as a connector and
    labelled with its size, so a reader reads the gap rather than subtracting
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
                out.append(mark)
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
    out.append("".join(ours))
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
        out.append("".join(drawn))

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
        out.append(body)
    return _svg(W, B + bottom_pad, "".join(out), ch)


# ── the frame around a drawing ────────────────────────────────────────

def _svg(width: float, height: float, body: str, spec: dict) -> str:
    """The drawing and the one line of provenance under it.

    What is printed under a drawing is `source` — where every value is stated
    and the setup it was measured in — and, when the drawing picked any of its
    parameters itself, `illustrative` in front of it, so a value chosen to draw
    with is never read as the paper's setting. A chart whose values were
    measured on a clock — a delay in ticks, a latency — names it in `clock`,
    first on the line. `why` — which of the paper's figures covers this ground
    and what this one strips out — is not printed here: the page that holds the
    drawing sets it apart beside the figure rather than as a paragraph under it.
    """
    ill = (f'<span class="pc-ill">예시 · {c.esc(spec["illustrative"])}</span>'
           if spec.get("illustrative") else "")
    clock = (f'<span class="pc-clock">{c.esc(spec["clock"])}</span>'
             if spec.get("clock") else "")
    cap = (f'<figcaption>{clock}{ill}{c.esc(spec.get("source", ""))}</figcaption>'
           if spec.get("source") or ill or clock else "")
    return (f'<figure class="pc-fig">'
            f'<svg viewBox="0 0 {width:.0f} {height:.0f}" preserveAspectRatio="xMidYMid meet" '
            f'role="img" aria-label="{c.esc(spec.get("alt", ""))}">{body}</svg>'
            f'{cap}</figure>')


# ── the fence ─────────────────────────────────────────────────────────

KINDS = {"line": line, "dots": dots, "scatter": scatter}


def chart(ch: dict, ratio: float | None = None) -> str:
    return KINDS[ch["kind"]](ch, ratio)


def _is_num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def problems(where: str, fence: str, spec) -> list[str]:
    """What the drawing needs, and the provenance it will not draw without. A
    non-empty list means the chart is not drawn, rather than drawn wrong."""
    out = []
    if not isinstance(spec, dict):
        return [f"{where}: ```probe-{fence} is not an object"]
    need = ("source", "why") if fence == "chart" else ()
    gone = [k for k in need if not str(spec.get(k, "")).strip()]
    if gone:
        out.append(f"{where}: ```probe-{fence} has no `" + "`, `".join(gone)
                   + "` — a data figure names where every number is stated and "
                     "which of the paper's own figures it redraws")
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
    return out
