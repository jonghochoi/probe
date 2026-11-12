"""계보 — who stands on whom, read out of the rewrites and drawn.

Every rewrite already says what it stands on, twice: its ```probe-lineage rail
names the line of work in time order, and its prose links the papers it argues
from. Nothing here is authored a second time — the graph is those two readings
of `analysis/*.md`, and a paper nobody linked has no edge.

Two drawings come out of the one graph. `map_svg` is the whole corpus on a
time-by-axis grid, for the 계보 page; `near_svg` is one paper with what it
stands on to its left and what stands on it to its right, for that paper's own
page. Both are inline SVG whose every node is a link, so the page reads
without a script and `assets/lineage.js` only adds the lighting-up.

An edge is one of two kinds, and the drawings keep them apart. A **rail** edge
is an ancestor the rewrite put on its lineage rail — a claim about descent. A
**text** edge is an arXiv link in the prose — the paper was reached for, which
may be a comparison or a baseline rather than a parent.

A paper outside the corpus is drawn only when a rail named it: the rail's
`what` is the one place a rewrite gives such a paper a name, and a node with
no name is a number. On the whole-corpus map it must also be an ancestor of
`SHARED` rewrites or more — one rewrite's private ancestor is on that
rewrite's own page, and a map that drew all of them would be mostly them.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from html import escape

from .corpus import _ARXIV_IN_BODY, Paper

RAIL, TEXT = "rail", "text"
SHARED = 2
OUTSIDE = "outside"          # the lane of a paper with no rewrite
# A node outside the corpus links to arXiv, which is another site.
_NEW_TAB = ' target="_blank" rel="noopener noreferrer"'

_FENCE = re.compile(r"^```probe-lineage\n(.*?)\n```", re.S | re.M)
_ABS = re.compile(r"arxiv\.org/abs/(\d{4}\.\d{4,5})")


@dataclass(frozen=True)
class Node:
    id: str
    name: str
    lane: str                 # the primary pillar, or `OUTSIDE`
    paper: Paper | None = None

    @property
    def month(self) -> int:
        """Months since year 0, from the arXiv id — one clock for every node.

        A rail's `when` is the author's reading of a date and a rewrite's
        `published:` is another; the id is the one stamp both kinds of node
        carry in the same form.
        """
        return (2000 + int(self.id[:2])) * 12 + int(self.id[2:4]) - 1


@dataclass
class Graph:
    nodes: dict[str, Node] = field(default_factory=dict)
    up: dict[str, dict[str, str]] = field(default_factory=dict)     # child → {parent: kind}
    down: dict[str, dict[str, str]] = field(default_factory=dict)   # parent → {child: kind}

    def link(self, parent: str, child: str, kind: str) -> None:
        # A rail edge outranks a text edge between the same two papers: the
        # rewrite that put a paper on its rail also links it in prose.
        if self.up.setdefault(child, {}).get(parent) == RAIL:
            return
        self.up[child][parent] = kind
        self.down.setdefault(parent, {})[child] = kind

    def parents(self, nid: str) -> list[str]:
        return sorted(p for p in self.up.get(nid, {}) if p in self.nodes)

    def children(self, nid: str) -> list[str]:
        return sorted(self.down.get(nid, {}))


def _rail_items(body: str) -> list[tuple[str, str]]:
    """`(arXiv id, name)` for each rail entry that links an abstract.

    A fence that does not parse is `render.py`'s to report; here it simply
    contributes no edge.
    """
    out = []
    for block in _FENCE.findall(body):
        try:
            items = json.loads(block).get("items", [])
        except (ValueError, AttributeError):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            m = _ABS.search(str(item.get("link", "")))
            if m:
                name = str(item.get("what", "")).split(" — ")[0].strip()
                out.append((m.group(1), name))
    return out


def build(papers: list[Paper], name) -> Graph:
    """The graph over `papers`. `name` gives a rewrite its short name."""
    g = Graph()
    for p in papers:
        g.nodes[p.stem] = Node(p.stem, name(p), p.primary, p)
    for p in papers:
        railed = set()
        for aid, what in _rail_items(p.body):
            if aid == p.stem:
                continue
            railed.add(aid)
            if aid not in g.nodes and what:
                g.nodes[aid] = Node(aid, what, OUTSIDE)
            g.link(aid, p.stem, RAIL)
        for aid in set(_ARXIV_IN_BODY.findall(p.body)) - railed - {p.stem}:
            g.link(aid, p.stem, TEXT)
    return g


def drawn(g: Graph) -> set[str]:
    """The nodes the whole-corpus map draws — see the module docstring."""
    return {nid for nid, n in g.nodes.items()
            if n.paper or len(g.down.get(nid, {})) >= SHARED}


# ── The whole-corpus map ────────────────────────────────────────────────────
# Time runs left to right and the axes stack, so a line that climbs is a paper
# reaching across axes and a long one is a paper reaching back. The grid is
# uneven on purpose: the corpus is recent and its ancestors are not, so the
# newest `RECENT` months get a column each, the two years before them a column
# per half-year, and everything older shares one.

RECENT = 6
COL_W, ROW_H, LANE_PAD, GUTTER, TOP = 138, 17, 12, 62, 30
LABEL_MAX = 18


def _column(month: int, newest: int) -> tuple[int, str]:
    """`(sort key, label)` of the column a month falls in."""
    year, mo = divmod(month, 12)
    first_recent = newest - RECENT + 1
    if month >= first_recent:
        return month, f"{year}.{mo + 1:02d}"
    floor_year = newest // 12 - 2
    if year < floor_year:
        return -1, f"{floor_year - 1} 이전"
    start = year * 12 + (6 if mo >= 6 else 0)
    end = min(start + 5, first_recent - 1)
    if end < start + 5:
        return start, f"{year}.{start % 12 + 1:02d}–{end % 12 + 1:02d}"
    return start, f"{year} {'하반기' if mo >= 6 else '상반기'}"


def radius(n_children: int) -> float:
    return round(3.2 + math.sqrt(n_children) * 1.15, 1)


def _clip(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit - 1] + "…"


def _curve(a: tuple[float, float], b: tuple[float, float]) -> str:
    """One edge. A parent in the same column or a later one bows left, so the
    line leaves the node on the side its label is not."""
    dx = b[0] - a[0]
    if dx > 0:
        return (f"M{a[0]} {a[1]}C{a[0] + dx * .5:.1f} {a[1]} "
                f"{b[0] - dx * .5:.1f} {b[1]} {b[0]} {b[1]}")
    return f"M{a[0]} {a[1]}C{a[0] - 26} {a[1]} {b[0] - 26} {b[1]} {b[0]} {b[1]}"


def map_svg(g: Graph, lanes: list[str], href) -> str:
    """The whole corpus as one SVG, with its lane names pinned beside it.

    `lanes` is the pillar order top to bottom; the outside lane goes above
    them. `href(node)` is where a node's link goes.
    """
    keep = drawn(g)
    if not keep:
        return ""
    newest = max(g.nodes[n].month for n in keep)
    col_of = {nid: _column(g.nodes[nid].month, newest) for nid in keep}
    cols = sorted(set(col_of.values()))
    col_x = {key: GUTTER + i * COL_W for i, (key, _) in enumerate(cols)}

    def kids(nid: str) -> int:
        return len(g.down.get(nid, {}))

    cells: dict[tuple[str, int], list[str]] = {}
    for nid in keep:
        cells.setdefault((g.nodes[nid].lane, col_of[nid][0]), []).append(nid)
    for members in cells.values():
        members.sort(key=lambda n: (-kids(n), n))

    pos: dict[str, tuple[float, float]] = {}
    bands = []
    y = TOP
    for lane in [OUTSIDE] + lanes:
        rows = max((len(m) for (ln, _), m in cells.items() if ln == lane), default=0)
        if not rows:
            continue
        height = rows * ROW_H + LANE_PAD * 2
        bands.append((lane, y, height))
        for (ln, key), members in cells.items():
            if ln == lane:
                for i, nid in enumerate(members):
                    pos[nid] = (col_x[key] + 14,
                                y + LANE_PAD + i * ROW_H + ROW_H / 2)
        y += height
    width, height = GUTTER + len(cols) * COL_W + 8, y + 6

    out = [f'<svg class="gm-svg" width="{width}" height="{height}" '
           f'viewBox="0 0 {width} {height}" role="img" '
           f'aria-label="재작성본과 그 조상을 시간과 연구 축 위에 놓은 계보 지도">']
    for i, (_, top, h) in enumerate(bands):
        if i % 2 == 0:
            out.append(f'<rect class="gm-band" x="0" y="{top}" width="{width}" height="{h}"/>')
    for key, label in cols:
        x = col_x[key]
        out.append(f'<line class="gm-rule" x1="{x}" y1="{TOP - 8}" x2="{x}" y2="{height}"/>'
                   f'<text class="gm-axis" x="{x + 8}" y="16">{escape(label)}</text>')
    for child in sorted(keep):
        for parent, kind in sorted(g.up.get(child, {}).items()):
            if parent in pos:
                out.append(
                    f'<path class="gm-edge{" is-text" if kind == TEXT else ""}" '
                    f'data-a="{parent}" data-b="{child}" '
                    f'd="{_curve(pos[parent], pos[child])}"/>')
    for nid in sorted(keep, key=lambda n: (pos[n][1], pos[n][0])):
        node = g.nodes[nid]
        x, cy = pos[nid]
        r = radius(kids(nid))
        outside = node.paper is None
        pillars = " ".join(node.paper.filed) if node.paper else ""
        out.append(
            f'<a class="gm-node{" is-out" if outside else ""}" href="{escape(href(node))}" '
            f'data-id="{nid}" data-lane="{node.lane}" data-p="{pillars}" '
            f'data-name="{escape(node.name)}"'
            f'{_NEW_TAB if outside else ""}>'
            f'<title>{escape(node.name)} · {nid}</title>'
            f'<circle cx="{x}" cy="{cy}" r="{r}"/>'
            f'<text x="{x + r + 5:.1f}" y="{cy + 4}">{escape(_clip(node.name, LABEL_MAX))}</text></a>')
    out.append("</svg>")

    tags = "".join(
        f'<span data-lane="{lane}" style="top:{top + 5}px">'
        f'{"바깥" if lane == OUTSIDE else lane}</span>'
        for lane, top, _ in bands)
    return f'<div class="gm-lanes" aria-hidden="true">{tags}</div>{"".join(out)}'


# ── One paper's neighbourhood ───────────────────────────────────────────────
# Three columns and no time axis: what the paper stands on, the paper, what
# stands on it. Each side is in arXiv order, which is time order, so the eye
# reads both lists oldest first.

NEAR_W, NEAR_ROW, NEAR_TOP = 640, 22, 34
NEAR_L, NEAR_C, NEAR_R = 232, 320, 408
NEAR_LABEL = 30


def near_svg(g: Graph, nid: str, href) -> str:
    """`nid` between its parents and its children, or `""` when it has neither."""
    parents, children = g.parents(nid), g.children(nid)
    if not parents and not children:
        return ""
    rows = max(len(parents), len(children), 1)
    height = NEAR_TOP + rows * NEAR_ROW + 14
    mid = NEAR_TOP + rows * NEAR_ROW / 2

    def ys(n: int) -> list[float]:
        first = mid - (n - 1) * NEAR_ROW / 2
        return [first + i * NEAR_ROW for i in range(n)]

    def node(other: str, x: float, y: float, left: bool) -> str:
        n = g.nodes[other]
        outside = n.paper is None
        tx, anchor = (x - 9, "end") if left else (x + 9, "start")
        return (
            f'<a class="near-node{" is-out" if outside else ""}" href="{escape(href(n))}" '
            f'data-lane="{n.lane}"'
            f'{_NEW_TAB if outside else ""}>'
            f'<title>{escape(n.name)} · {other}</title>'
            f'<circle cx="{x}" cy="{y}" r="4"/>'
            f'<text x="{tx}" y="{y + 4}" text-anchor="{anchor}">'
            f'{escape(_clip(n.name, NEAR_LABEL))}</text></a>')

    def edge(a: tuple[float, float], b: tuple[float, float], kind: str) -> str:
        return (f'<path class="near-edge{" is-text" if kind == TEXT else ""}" '
                f'd="{_curve(a, b)}"/>')

    me = g.nodes[nid]
    out = [f'<svg class="near-svg" width="{NEAR_W}" height="{height:.0f}" '
           f'viewBox="0 0 {NEAR_W} {height:.0f}" role="img" '
           f'aria-label="{escape(me.name)} 이 딛고 선 논문 {len(parents)}편과 '
           f'이 논문을 딛는 재작성본 {len(children)}편">',
           f'<text class="near-head" x="{NEAR_L}" y="16" text-anchor="end">'
           f'딛고 선 것 {len(parents)}</text>',
           f'<text class="near-head" x="{NEAR_R}" y="16">이 논문을 딛는 것 {len(children)}</text>']
    for other, y in zip(parents, ys(len(parents))):
        out.append(edge((NEAR_L, y), (NEAR_C, mid), g.up[nid][other]))
    for other, y in zip(children, ys(len(children))):
        out.append(edge((NEAR_C, mid), (NEAR_R, y), g.down[nid][other]))
    for other, y in zip(parents, ys(len(parents))):
        out.append(node(other, NEAR_L, y, True))
    for other, y in zip(children, ys(len(children))):
        out.append(node(other, NEAR_R, y, False))
    out.append(f'<g class="near-me" data-lane="{me.lane}">'
               f'<circle cx="{NEAR_C}" cy="{mid}" r="7"/></g></svg>')
    return "".join(out)
