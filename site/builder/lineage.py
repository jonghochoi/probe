"""계보 — who stands on whom, read out of the rewrites.

Every rewrite already says what it stands on, twice: its ```probe-lineage rail
names the line of work in time order, and its prose links the papers it argues
from. Nothing here is authored a second time — the graph is those two readings
of `analysis/*.md`, and a paper nobody linked has no edge.

The graph is read one paper at a time, for that paper's 계보 tab: the paper
with the older papers it is joined to on its left and the newer ones on its
right. `near_svg` is that as inline SVG whose every node is a link, so the tab
reads without a script; `assets/lineage.js` replaces it with the same three
columns as cells. Only the paper's own edges are drawn — a neighbour's
neighbours would read as a path the paper's ideas travelled, and the graph
makes no such claim. `gaps` is the one reading of the whole: the papers
several rewrites stand on that the corpus has no rewrite of, which the
analysis list prints at its foot.

An edge is one of two kinds, and the drawings keep them apart. A **rail** edge
joins a paper to one its lineage rail names — a claim that the two are one
line of work. A **text** edge is an arXiv link in the prose — the paper was
mentioned, which may be a comparison or a baseline. Either way the older paper
is the parent (`Graph.link`).

A paper outside the corpus is a node only when a rail named it: the rail's
`what` is the one place a rewrite gives such a paper a name, and a node with
no name is a number.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from html import escape

from .corpus import _ARXIV_IN_BODY, Paper

RAIL, TEXT = "rail", "text"
# How many rewrites must stand on a paper with no rewrite before the corpus
# counts it as a gap: one rewrite's private ancestor is that rewrite's own.
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


@dataclass
class Graph:
    nodes: dict[str, Node] = field(default_factory=dict)
    up: dict[str, dict[str, str]] = field(default_factory=dict)     # child → {parent: kind}
    down: dict[str, dict[str, str]] = field(default_factory=dict)   # parent → {child: kind}

    def link(self, a: str, b: str, kind: str) -> None:
        """Join two papers, the older as the parent.

        Which rewrite named which says nothing about descent: a rail runs past
        the paper being read into the work that followed it, and prose links
        later papers as freely as earlier ones. The arXiv id is the one clock
        both papers carry, so it alone sets the direction — and two rewrites
        naming each other are one edge, not a loop.

        A rail edge outranks a text edge between the same two papers.
        """
        parent, child = sorted((a, b))
        if self.up.setdefault(child, {}).get(parent) == RAIL:
            return
        self.up[child][parent] = kind
        self.down.setdefault(parent, {})[child] = kind

    def parents(self, nid: str) -> list[str]:
        return sorted(p for p in self.up.get(nid, {}) if p in self.nodes)

    def children(self, nid: str) -> list[str]:
        return sorted(c for c in self.down.get(nid, {}) if c in self.nodes)


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


def gaps(g: Graph) -> list[tuple[Node, list[Node]]]:
    """빈자리 — the papers with no rewrite that `SHARED` rewrites or more stand
    on, each with those rewrites, the most stood-on first.

    The one thing the graph says about the corpus as a whole: what it leans on
    and has not written.
    """
    rows = [(node, [g.nodes[c] for c in g.children(nid)])
            for nid, node in g.nodes.items()
            if node.paper is None and len(g.down.get(nid, {})) >= SHARED]
    return sorted(rows, key=lambda row: (-len(row[1]), row[0].id))


def _clip(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit - 1] + "…"


def _curve(a: tuple[float, float], b: tuple[float, float]) -> str:
    """One edge, left to right."""
    dx = b[0] - a[0]
    return (f"M{a[0]} {a[1]}C{a[0] + dx * .5:.1f} {a[1]} "
            f"{b[0] - dx * .5:.1f} {b[1]} {b[0]} {b[1]}")


# ── One paper's neighbourhood ───────────────────────────────────────────────
# Three columns: what the paper stands on, the paper, what stands on it. Each side is in arXiv order, which is time order, so the eye
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
           f'aria-label="{escape(me.name)} 의 선행 {len(parents)}편과 '
           f'후속 {len(children)}편">',
           f'<text class="near-head" x="{NEAR_L}" y="16" text-anchor="end">'
           f'선행 {len(parents)}</text>',
           f'<text class="near-head" x="{NEAR_R}" y="16">후속 {len(children)}</text>']
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
