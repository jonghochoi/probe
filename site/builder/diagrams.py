"""The five shapes a deck may draw, and the one it may play — AUTHORING §5-5, §5-7.

A slide declares data; this module decides geometry and colour (R12). Authors
supply no SVG: a hand-drawn figure cannot be checked against the original, and
a rewrite that ships its own geometry drifts from the site's type and palette
the first time either changes.

Everything is drawn in `currentColor` plus `var(--orange)` for the one row that
carries the claim, so a diagram lives in both themes without a second palette —
the same reason the rest of the site's components take their colour from tokens.

Motion is the same contract in one dimension more: `film` plays frames the
paper already published, cut out of the hotlinked original by background
geometry rather than by cropping an image into the repository (R6).
"""

from __future__ import annotations

from . import components as c

KINDS = ("bars", "timeline", "matrix", "lanes", "slope")

ORANGE = "var(--orange)"
FILM_SLOW_MIN, FILM_SLOW_MAX = 2, 4


# ── validation ──────────────────────────────────────────────────────────────

def check(spec, where: str) -> list[str]:
    if not isinstance(spec, dict):
        return [f"{where}: `kind: diagram` needs a `diagram` object (S5)"]
    kind = str(spec.get("kind", "")).strip()
    if kind not in KINDS:
        return [f"{where}: diagram `kind` must be one of {', '.join(KINDS)} — got {kind!r}"]
    if not str(spec.get("title", "")).strip():
        return [f"{where}: the diagram needs a `title` — what this picture says"]

    problems: list[str] = []
    if kind == "bars":
        rows = spec.get("rows")
        if not isinstance(rows, list) or not rows:
            return [f"{where}: `bars` needs a non-empty `rows`"]
        for row in rows:
            if not isinstance(row, dict) or not row.get("label"):
                problems.append(f"{where}:each bar row needs `label` (got {row!r})")
                continue
            if "n" not in row and not {"before", "after"} <= set(row):
                problems.append(
                    f"{where}: bar `{row['label']}` needs `n`, or `before` and `after`"
                )
            problems += _numbers(where, row, ("n", "before", "after"))
        base = spec.get("baseline")
        if base is not None and (not isinstance(base, dict) or "n" not in base):
            problems.append(f"{where}: `baseline` needs `label` and `n`")
    elif kind == "timeline":
        rows = spec.get("rows")
        if not isinstance(rows, list) or not rows:
            return [f"{where}: `timeline` needs a non-empty `rows`"]
        for row in rows:
            segs = row.get("segments") if isinstance(row, dict) else None
            if not isinstance(row, dict) or not row.get("label") or not segs:
                problems.append(f"{where}:each timeline row needs `label` and `segments`")
                continue
            for seg in segs:
                if not isinstance(seg, dict) or "len" not in seg:
                    problems.append(f"{where}: each segment needs `len` (got {seg!r})")
                else:
                    problems += _numbers(where, seg, ("len",))
    elif kind == "matrix":
        panels = spec.get("panels")
        if not isinstance(panels, list) or not 1 <= len(panels) <= 2:
            return [f"{where}: `matrix` needs one or two `panels` (before / after)"]
        for panel in panels:
            cells = panel.get("cells") if isinstance(panel, dict) else None
            if not isinstance(cells, list) or not cells or not all(
                isinstance(row, list) and row for row in cells
            ):
                problems.append(f"{where}: each matrix panel needs `cells` as a grid of 0/1")
    elif kind == "lanes":
        lanes = spec.get("lanes")
        if not isinstance(lanes, list) or not 1 <= len(lanes) <= 2:
            return [f"{where}: `lanes` needs one or two lanes — the two actors"]
        for lane in lanes:
            if not isinstance(lane, dict) or not lane.get("label") or not lane.get("blocks"):
                problems.append(f"{where}: each lane needs `label` and `blocks`")
    elif kind == "slope":
        pairs = spec.get("pairs")
        if not isinstance(pairs, list) or not pairs:
            return [f"{where}: `slope` needs a non-empty `pairs`"]
        for pair in pairs:
            if not isinstance(pair, dict) or not pair.get("label"):
                problems.append(f"{where}: each slope pair needs `label`")
                continue
            if "before" not in pair or "after" not in pair:
                problems.append(f"{where}: slope `{pair['label']}` needs `before` and `after`")
            problems += _numbers(where, pair, ("before", "after"))
    return problems


def check_film(spec, where: str) -> list[str]:
    if not isinstance(spec, dict):
        return [f"{where}: `kind: film` needs a `film` object (S7)"]
    problems = []
    cols = spec.get("cols")
    if not isinstance(cols, int) or cols < 2:
        problems.append(f"{where}: `film.cols` is how many frames the strip holds (≥ 2)")
    interval = spec.get("interval_ms")
    if not isinstance(interval, (int, float)) or interval <= 0:
        problems.append(
            f"{where}: `film.interval_ms` must be the frame interval the ORIGINAL "
            f"states — without it the playback speed would be ours, and a speed "
            f"we invented is a claim about the system's timing (S7)"
        )
    slow = spec.get("slow")
    if not isinstance(slow, (int, float)) or not FILM_SLOW_MIN <= slow <= FILM_SLOW_MAX:
        problems.append(
            f"{where}: `film.slow` must be {FILM_SLOW_MIN}–{FILM_SLOW_MAX}× — real "
            f"time is too fast to read from a seat (S7)"
        )
    tracks = spec.get("tracks")
    if not isinstance(tracks, list) or not 1 <= len(tracks) <= 2:
        problems.append(f"{where}: `film.tracks` is one or two rows of the strip")
    else:
        for track in tracks:
            if not isinstance(track, dict) or "row" not in track or not track.get("label"):
                problems.append(f"{where}: each film track needs `row` and `label`")
    box = spec.get("box")
    if box is not None and (not isinstance(box, list) or len(box) != 4):
        problems.append(f"{where}: `film.box` is [x, y, w, h] as fractions of the figure")
    return problems


def _numbers(where: str, obj: dict, keys) -> list[str]:
    out = []
    for key in keys:
        if key in obj and not isinstance(obj[key], (int, float)):
            out.append(f"{where}: `{key}` must be a number, got {obj[key]!r}")
    return out


# ── drawing ─────────────────────────────────────────────────────────────────

_DRAWERS = {}


def draw(spec, *, staged: bool = False) -> str:
    """The diagram, flat — or split into the reveal groups S6 steps through."""
    if not isinstance(spec, dict) or spec.get("kind") not in KINDS:
        return ""
    base, layers, height = _DRAWERS[spec["kind"]](spec)
    body = "".join(base)
    for i, layer in enumerate(layers, 1):
        chunk = "".join(layer)
        body += f'<g data-rev="{i}">{chunk}</g>' if staged else chunk
    return _frame(spec, body, height)


def groups(spec) -> int:
    """How many reveal groups this diagram has of its own.

    A staged reveal steps through the component's own units — the 기존 bars and
    then the 이후 bars, one panel and then the other — so the slide's `steps`
    has to match this. A reveal that lands mid-group splits a thought instead
    of pacing one.
    """
    if not isinstance(spec, dict) or spec.get("kind") not in KINDS:
        return 0
    _, layers, _ = _DRAWERS[spec["kind"]](spec)
    return len(layers)


W = 1000


def _frame(spec: dict, body: str, height: int) -> str:
    """Title above, note below — the two things a diagram cannot say by itself."""
    title = c.esc(spec.get("title", ""))
    note = c.esc(spec.get("note", ""))
    return (
        '<figure class="dgfig">'
        f'<svg viewBox="0 0 {W} {height}" role="img" aria-label="{title}" '
        f'xmlns="http://www.w3.org/2000/svg">{body}</svg>'
        + (f"<figcaption>{note}</figcaption>" if note else "")
        + "</figure>"
    )


def _t(x, y, text, *, size=14, anchor="start", fill="currentColor",
       opacity=1.0, weight=400, mono=False) -> str:
    family = ' font-family="ui-monospace, monospace"' if mono else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
        f'fill="{fill}" opacity="{opacity:g}" font-weight="{weight}"{family}>'
        f"{c.esc(text)}</text>"
    )


def _rect(x, y, w, h, *, fill="currentColor", opacity=1.0, r=3) -> str:
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0.5):.1f}" '
        f'height="{h:.1f}" rx="{r}" fill="{fill}" opacity="{opacity:g}"/>'
    )


def _bars(spec: dict):
    """Ranked values, optionally 기존 → 이후, against a floor the reader knows."""
    rows = spec["rows"]
    paired = any("before" in r for r in rows)
    x0, x1 = 250, 880
    top, rh = 58, (74 if paired else 46)
    values = [v for r in rows for v in (r.get("before"), r.get("after"), r.get("n"))
              if isinstance(v, (int, float))]
    base_spec = spec.get("baseline") or {}
    if isinstance(base_spec.get("n"), (int, float)):
        values.append(base_spec["n"])
    span = (max(values or [1]) * 1.06) or 1

    def X(v):
        return x0 + (x1 - x0) * float(v) / span

    height = top + rh * len(rows) + 46
    base, first, second = [], [], []
    if isinstance(base_spec.get("n"), (int, float)):
        bx = X(base_spec["n"])
        base.append(f'<line x1="{bx:.1f}" y1="40" x2="{bx:.1f}" '
                    f'y2="{top + rh * len(rows) - 12}" stroke="currentColor" '
                    f'stroke-width="1.5" opacity=".45" stroke-dasharray="4 4"/>')
        base.append(_t(bx + 8, 34, str(base_spec.get("label", "")), size=13, opacity=.55))
    for i, row in enumerate(rows):
        y = top + i * rh
        base.append(_t(x0 - 18, y + (22 if paired else 15), str(row["label"]),
                       size=15, anchor="end", opacity=.82))
        if paired:
            first.append(_rect(x0, y, X(row["before"]) - x0, 17, opacity=.22))
            first.append(_t(X(row["before"]) + 9, y + 14, _num(row["before"]),
                            size=13, opacity=.55))
            second.append(_rect(x0, y + 22, X(row["after"]) - x0, 17, fill=ORANGE))
            second.append(_t(X(row["after"]) + 9, y + 36, _num(row["after"]), size=14,
                             fill=ORANGE, weight=700))
            if row["after"]:
                ratio = float(row["before"]) / float(row["after"])
                second.append(_t(x1 + 96, y + 30, f"{ratio:.2f}×", size=15, weight=700,
                                 opacity=.62, anchor="end"))
        else:
            mine = bool(row.get("us"))
            first.append(_rect(x0, y, X(row["n"]) - x0, 18,
                               fill=ORANGE if mine else "currentColor",
                               opacity=1 if mine else .22))
            first.append(_t(X(row["n"]) + 9, y + 14, _num(row["n"]), size=14,
                            fill=ORANGE if mine else "currentColor",
                            weight=700 if mine else 400, opacity=1 if mine else .6))
    if spec.get("unit"):
        base.append(_t(x0 - 18, height - 12, str(spec["unit"]), size=13,
                       anchor="end", opacity=.5))
    layers = [first, second] if paired else [first]
    return base, layers, height


def _timeline(spec: dict):
    """One axis of time, one row per condition — where the waiting is."""
    rows = spec["rows"]
    x0, x1 = 200, 940
    top, rh, bar = 70, 80, 38
    total = max(sum(float(s["len"]) for s in r["segments"]) for r in rows)
    span = (total * 1.08) or 1

    def X(v):
        return x0 + (x1 - x0) * float(v) / span

    height = top + rh * len(rows) + 48
    base, layers = [], []
    grid = spec.get("grid")
    if isinstance(grid, (int, float)) and grid > 0:
        tick = 0.0
        while tick <= span:
            gx = X(tick)
            base.append(f'<line x1="{gx:.1f}" y1="{top - 18}" x2="{gx:.1f}" '
                        f'y2="{top + rh * len(rows) - 26}" stroke="currentColor" '
                        f'stroke-width="1" opacity=".16" stroke-dasharray="3 5"/>')
            if tick:
                base.append(_t(gx, top + rh * len(rows) - 6, _num(tick), size=13,
                               anchor="middle", opacity=.45))
            tick += float(grid)
    if spec.get("unit"):
        base.append(_t(x1, height - 12, str(spec["unit"]), size=13,
                       anchor="end", opacity=.45))

    for i, row in enumerate(rows):
        y = top + i * rh
        mine = bool(row.get("us"))
        layer = [_t(16, y + 22, str(row["label"]), size=15, opacity=.8)]
        at = 0.0
        for j, seg in enumerate(row["segments"]):
            width = X(at + float(seg["len"])) - X(at)
            lead = (j == 0)
            layer.append(_rect(X(at), y, width - 1.4, bar,
                               fill="currentColor" if lead else (ORANGE if mine else "currentColor"),
                               opacity=.16 if lead else (1 if mine else .34), r=2))
            if seg.get("name") and width > 70:
                layer.append(_t(X(at) + width / 2, y - 9, str(seg["name"]), size=13,
                                anchor="middle", opacity=.6,
                                fill=ORANGE if (mine and not lead) else "currentColor"))
            at += float(seg["len"])
        end = X(at)
        layer.append(f'<line x1="{end:.1f}" y1="{y - 10}" x2="{end:.1f}" '
                     f'y2="{y + bar + 10}" stroke="{ORANGE if mine else "currentColor"}" '
                     f'stroke-width="2" opacity="{1 if mine else .5:g}"/>')
        if row.get("mark"):
            far = end > W * 0.72
            layer.append(_t(end + (-10 if far else 10), y + (bar + 26 if far else 24),
                            str(row["mark"]), size=16, weight=700,
                            anchor="end" if far else "start",
                            fill=ORANGE if mine else "currentColor",
                            opacity=1 if mine else .65))
        layers.append(layer)
    return base, layers, height


def _matrix(spec: dict):
    """Two grids side by side — what is settled, and when."""
    panels = spec["panels"]
    cell, gap, top = 26, 4, 92
    rows = max(len(p["cells"]) for p in panels)
    cols = max(len(p["cells"][0]) for p in panels)
    gw = cols * (cell + gap)
    axis = spec.get("axis") or {}
    lefts = [110 + i * (gw + 150) for i in range(len(panels))]
    layers = []
    for panel, left in zip(panels, lefts):
        mine = bool(panel.get("us"))
        layer = [_t(left, 40, str(panel.get("label", "")), size=16, weight=700,
                    fill=ORANGE if mine else "currentColor", opacity=1 if mine else .72)]
        if panel.get("note"):
            layer.append(_t(left, 62, str(panel["note"]), size=13, opacity=.5))
        if axis.get("y"):
            layer.append(_t(left - 12, top - 10, str(axis["y"]), size=12,
                            anchor="end", opacity=.45))
        for r, line in enumerate(panel["cells"]):
            y = top + r * (cell + gap)
            layer.append(_t(left - 12, y + cell - 8, str(r + 1), size=12,
                            anchor="end", opacity=.38))
            for k, state in enumerate(line):
                x = left + k * (cell + gap)
                on = bool(state)
                layer.append(_rect(x, y, cell, cell,
                                   fill=ORANGE if on else "currentColor",
                                   opacity=(1 if mine else .8) if on else .13))
        if axis.get("x"):
            layer.append(_t(left + gw / 2, top + rows * (cell + gap) + 26,
                            str(axis["x"]), size=13, anchor="middle", opacity=.5))
        layers.append(layer)
    return [], layers, top + rows * (cell + gap) + 52


def _lanes(spec: dict):
    """Two actors and what passes between them, step by step."""
    lanes = spec["lanes"]
    x0, x1 = 250, 920
    defs = ('<defs><marker id="dg-arrow" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="7" markerHeight="7" orient="auto">'
            '<path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>')
    layers = []
    y = 74
    for lane in lanes:
        blocks = int(lane["blocks"])
        active = int(lane.get("active", blocks))
        mine = bool(lane.get("us"))
        bw = (x1 - x0) / blocks
        layer = [_t(16, y + 14, str(lane["label"]), size=15, opacity=.82)]
        if lane.get("note"):
            layer.append(_t(16, y + 34, str(lane["note"]), size=12, opacity=.45))
        for k in range(blocks):
            live = k < active
            layer.append(_rect(x0 + k * bw, y, bw - 4, 30,
                               fill=ORANGE if (mine and live) else "currentColor",
                               opacity=(1 if mine else .34) if live else .08))
        if active < blocks and lane.get("stop"):
            sx = x0 + active * bw - 2
            layer.append(f'<line x1="{sx:.1f}" y1="{y - 12}" x2="{sx:.1f}" '
                         f'y2="{y + 42}" stroke="{ORANGE}" stroke-width="2" '
                         f'stroke-dasharray="4 3"/>')
            layer.append(_t(sx - 8, y - 16, str(lane["stop"]), size=13, weight=700,
                            anchor="end", fill=ORANGE))
        ry = y + 92
        layer.append(_rect(x0, ry, x1 - x0, 26, opacity=.08))
        if lane.get("queue"):
            layer.append(_t(16, ry + 18, str(lane["queue"]), size=12, opacity=.45))
        for hand in lane.get("handoffs") or []:
            at = int(hand.get("at", 0))
            cx = x0 + at * bw + (bw - 4) / 2
            layer.append(f'<path d="M{cx:.1f},{y + 34} L{cx:.1f},{ry - 8}" '
                         f'stroke="{ORANGE if mine else "currentColor"}" '
                         f'stroke-width="1.6" opacity="{1 if mine else .5:g}" '
                         f'marker-end="url(#dg-arrow)"/>')
            layer.append(_t(cx, ry + 18, str(hand.get("label", "")), size=13,
                            weight=700, anchor="middle",
                            fill=ORANGE if mine else "currentColor",
                            opacity=1 if mine else .6))
        layers.append(layer)
        y = ry + 64
    return [defs], layers, y + 10


def _slope(spec: dict):
    """Before → after on a shared scale — the cost, stated as a slope."""
    pairs = spec["pairs"]
    top, plot = 96, 150
    colw = min(240, (W - 140) / max(len(pairs), 1))
    x0 = 90
    lo, hi = spec.get("lo"), spec.get("hi")
    values = [float(p[k]) for p in pairs for k in ("before", "after")]
    spread = (max(values) - min(values)) or 1
    if not isinstance(lo, (int, float)):
        lo = min(values) - spread * 0.35
    if not isinstance(hi, (int, float)):
        hi = max(values) + spread * 0.35

    def Y(v):
        return top + plot - plot * (float(v) - lo) / ((hi - lo) or 1)

    out = []
    for i, pair in enumerate(pairs):
        cx = x0 + i * colw
        if pair.get("group"):
            out.append(_t(cx + 55, top - 46, str(pair["group"]), size=13,
                          anchor="middle", opacity=.5))
        out.append(_t(cx + 55, top - 26, str(pair["label"]), size=15, weight=700,
                      anchor="middle", opacity=.85))
        y1, y2 = Y(pair["before"]), Y(pair["after"])
        out.append(f'<line x1="{cx:.1f}" y1="{y1:.1f}" x2="{cx + 110:.1f}" '
                   f'y2="{y2:.1f}" stroke="{ORANGE}" stroke-width="2.4"/>')
        out.append(f'<circle cx="{cx:.1f}" cy="{y1:.1f}" r="5" fill="currentColor" '
                   f'opacity=".45"/>')
        out.append(f'<circle cx="{cx + 110:.1f}" cy="{y2:.1f}" r="5.5" fill="{ORANGE}"/>')
        out.append(_t(cx - 12, y1 + 5, _num(pair["before"]), size=14, anchor="end",
                      opacity=.6, mono=True))
        out.append(_t(cx + 122, y2 + 5, _num(pair["after"]), size=14, weight=700,
                      fill=ORANGE, mono=True))
        out.append(_t(cx, top + plot + 28, str(spec.get("before_label", "기존")),
                      size=12, anchor="middle", opacity=.4))
        out.append(_t(cx + 110, top + plot + 28, str(spec.get("after_label", "이후")),
                      size=12, anchor="middle", fill=ORANGE, opacity=.8))
    return out, [], top + plot + 56


_DRAWERS.update({"bars": _bars, "timeline": _timeline, "matrix": _matrix,
                 "lanes": _lanes, "slope": _slope})


def _num(value) -> str:
    text = f"{float(value):g}"
    return text


# ── film ────────────────────────────────────────────────────────────────────

def _geometry(spec: dict, track: dict) -> tuple[float, float, float, float, float]:
    """`(size_x, size_y, from_x, to_x, y)` in percent, for one track.

    The strip is a grid inside the figure — `box` is which part of the image
    holds it — so one cell is shown by scaling the background up and stepping
    `background-position` across it. Percentage positioning aligns the same
    fraction of image and box, which is why each stop divides by `1 − cell`.
    """
    x, y, w, h = (spec.get("box") or [0, 0, 1, 1])
    cols = int(spec["cols"])
    rows = max(int(spec.get("rows", len(spec.get("tracks", [1])))), 1)
    cw, ch = float(w) / cols, float(h) / rows
    size_x, size_y = 100.0 / cw, 100.0 / ch
    def px(col):
        return (float(x) + col * cw) / (1 - cw) * 100.0 if cw < 1 else 0.0
    first, last = px(0), px(cols - 1)
    # `steps()` lands on n − 1 of n stops, so the end value is extrapolated one
    # cell past the last frame.
    end = first + (last - first) * cols / (cols - 1) if cols > 1 else first
    row = int(track.get("row", 0))
    py = (float(y) + row * ch) / (1 - ch) * 100.0 if ch < 1 else 0.0
    return size_x, size_y, first, end, py


def film_style(spec, index: int) -> str:
    """Per-track keyframes. One rule per track, named by slide and row."""
    if not isinstance(spec, dict):
        return ""
    rules = []
    for t, track in enumerate(spec.get("tracks") or []):
        if not isinstance(track, dict):
            continue
        _, _, first, end, py = _geometry(spec, track)
        rules.append(
            f"@keyframes dk-film-{index}-{t}{{"
            f"from{{background-position:{first:.3f}% {py:.3f}%}}"
            f"to{{background-position:{end:.3f}% {py:.3f}%}}}}"
        )
    return f"<style>{''.join(rules)}</style>" if rules else ""


def film(spec, url: str, index: int) -> str:
    """Two tracks of the paper's own filmstrip, played at its stated interval."""
    if not isinstance(spec, dict):
        return ""
    cols = int(spec.get("cols", 1))
    duration = float(spec.get("interval_ms", 0)) * cols * float(spec.get("slow", 1)) / 1000.0
    clips = ""
    for t, track in enumerate(spec.get("tracks") or []):
        size_x, size_y, first, _, py = _geometry(spec, track)
        mine = bool(track.get("us"))
        clips += (
            '<div class="dk-clipwrap">'
            f'<div class="dk-cliplab{" us" if mine else ""}">{c.esc(track.get("label", ""))}</div>'
            f'<div class="dk-clip" style="background-image:url({c.esc(url)});'
            f"background-size:{size_x:.3f}% {size_y:.3f}%;"
            f"background-position:{first:.3f}% {py:.3f}%;"
            f"animation:dk-film-{index}-{t} {duration:.3f}s steps({cols}) infinite\"></div>"
            "</div>"
        )
    interval = spec.get("interval_ms")
    foot = (
        f'<p class="dk-filmnote">원문 프레임 {cols} 장 · 실제 간격 {_num(interval)} ms 를 '
        f'{_num(spec.get("slow", 1))} 배 느리게</p>'
    )
    return f'<div class="dk-film-stage">{clips}{foot}</div>'
