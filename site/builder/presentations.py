"""Discover the presentations the site publishes, and draw their slides.

A presentation is one paper retold as a talk — `presentation/<arxiv-id>.md`, written by `/present`
the way `analysis/<id>.md` is written by `/analyze`. It is a track of its own
because a talk is not a shorter rewrite: it argues in a sequence, it carries a
speaker essay under every slide, and its unit is a frame rather than a section.

Two constraints shape everything here, and both come from
`presentation/AUTHORING.md`:

    **only a paper that already has a rewrite may have a presentation**, and
    **every slide declares its act and its type.**

The first is the same discipline `comparison/` runs on: a slide compresses, and
what it compresses away has to be one link off. Without the rewrite there is
nowhere to send the listener who wants the detail, so the presentation would have to
carry it and stop being a presentation.

The second is what keeps a presentation from becoming a table of contents. The act
(起承轉結) is the beat the slide serves; the type is its shape, and the shape
decides the composition — one grid stretched over every slide is what leaves
holes. Both live in the source rather than in the author's head, which is what
makes them checkable.

Discovery and drawing sit in one module for the same reason `glance.py` does:
the surface is small, its rules are its layout, and splitting them would put a
schema in one file and the reason for it in another.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import components as c
from . import corpus, frontmatter

PRESENTATION_DIR = corpus.REPO_ROOT / "presentation"

ID_RE = re.compile(r"^\d{4}\.\d{4,5}$")
SOURCE_RE = re.compile(r"^(\d{4}\.\d{4,5})v(\d+)$")
HEAD_RE = re.compile(r"^\[(\S+) · (\w+)\]\s*(.+)$")

# The four beats, with the word each one is doing on a slide. A presentation whose
# slides all sit in one act is a table of contents, which is what the paper
# already is — so the labels are printed, not just validated.
ACTS = {"起": "상황", "承": "막다른 길", "轉": "전환", "結": "결과"}
ACT_ORDER = {a: i + 1 for i, a in enumerate(ACTS)}

# Every slide type, and the fence it is drawn from. `None` is a type that draws
# itself from the header and the prose under it.
TYPE_FENCE = {
    "cover": None,
    "statement": None,
    "evidence": "figure",
    "split": "figure",
    "versus": "versus",
    "ledger": "ledger",
    "budget": "budget",
    "timing": "timing",
    "lineage": "lineage",
}

# The fences a slide may carry beside the one its type is drawn from.
EXTRA_FENCES = ("diagram", "facts", "script")
FENCES = tuple(f for f in TYPE_FENCE.values() if f) + EXTRA_FENCES

REQUIRED_FRONT = ("presentation_of", "title", "venue", "audience", "minutes", "spine",
                  "arxiv_html", "generated")

# `probe-facts` is the evidence ribbon every slide closes on. Three cells is
# the shape; two is what a slide with only two numbers gets. More than three
# stops being a ribbon and starts being a table the audience reads instead of
# listening.
FACTS_MAX = 3


@dataclass
class Slide:
    act: str
    kind: str
    title: str
    claim: str = ""
    bullets: list[str] = field(default_factory=list)
    data: dict = field(default_factory=dict)
    script: str = ""


@dataclass
class Presentation:
    paper_id: str
    path: Path
    front: dict
    slides: list[Slide]

    @property
    def title(self) -> str:
        return self.front.get("title", "")

    @property
    def spine(self) -> str:
        return self.front.get("spine", "")

    @property
    def minutes(self) -> str:
        return self.front.get("minutes", "")

    @property
    def venue(self) -> str:
        return self.front.get("venue", "")

    @property
    def acts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for s in self.slides:
            counts[s.act] = counts.get(s.act, 0) + 1
        return counts


def discover(papers_by_id: dict,
             partial: bool = False) -> tuple[dict[str, Presentation], list[str]]:
    """Every `presentation/<id>.md`, keyed by paper id, plus the problems found.

    A problem that would publish a broken talk skips the presentation; the rest are
    reported and the presentation still builds, so one soft slip does not take the
    whole talk off the paper's page.

    `partial` says the corpus handed in is a subset (`--only`). A presentation belongs
    to one paper, so unlike a comparison it can still be judged — but only the
    presentations of papers in the subset. The rest are not this build's business, and
    reporting them as missing rewrites would make every partial build noisy
    with a problem that is not one.
    """
    presentations: dict[str, Presentation] = {}
    problems: list[str] = []
    if not PRESENTATION_DIR.is_dir():
        return presentations, problems

    for path in sorted(PRESENTATION_DIR.glob("*.md")):
        name = path.name
        if name == "AUTHORING.md":
            continue
        paper_id = path.stem
        if not ID_RE.match(paper_id):
            problems.append(
                f"presentation/{name}: name is not an arXiv id — one presentation per paper, "
                f"filed under the id its rewrite is filed under"
            )
            continue
        try:
            front, body = frontmatter.parse(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            problems.append(f"presentation/{name}: {exc}")
            continue

        # The track's constraint, and the reason it is a skip rather than a
        # warning: a slide compresses, and the rewrite is where the detail it
        # dropped has to be reachable.
        if paper_id not in papers_by_id:
            if partial:
                continue
            problems.append(
                f"presentation/{name}: {paper_id} has no rewrite in `analysis/` — not "
                f"published. A presentation compresses, and the rewrite is where the "
                f"detail it drops stays reachable. Run `/analyze {paper_id}` first"
            )
            continue
        if front.get("presentation_of", "").strip() != paper_id:
            problems.append(
                f"presentation/{name}: `presentation_of` is {front.get('presentation_of', '')!r} but the "
                f"file is filed under {paper_id}"
            )
            continue

        for key in REQUIRED_FRONT:
            if not front.get(key):
                problems.append(f"presentation/{name}: missing `{key}`")
        src = front.get("arxiv_html", "").strip()
        if src and not SOURCE_RE.match(src):
            problems.append(
                f"presentation/{name}: `arxiv_html` is {src!r} — the arXiv edition the "
                f"talk was cut from, as `<id>v<n>`"
            )
        elif src and SOURCE_RE.match(src).group(1) != paper_id:
            problems.append(
                f"presentation/{name}: `arxiv_html` reads {src!r} for a presentation of {paper_id}"
            )
        if not corpus._GENERATED.match(front.get("generated", "").strip()):
            problems.append(
                f"presentation/{name}: `generated` is "
                f"{front.get('generated', '')!r} — write it as `YYYY-MM-DD HH:MM`"
            )

        slides, slide_problems = parse_slides(body)
        problems += [f"presentation/{name}: {p}" for p in slide_problems]
        if not slides:
            problems.append(f"presentation/{name}: no slides — not published")
            continue
        presentation = Presentation(paper_id=paper_id, path=path, front=front, slides=slides)
        # One act is a table of contents. It is a warning rather than a skip:
        # the talk still reads, it just has no spine, and the author is the one
        # who has to decide which beats it is missing.
        if len(presentation.acts) < 2:
            problems.append(
                f"presentation/{name}: every slide sits in one act — a presentation with no "
                f"turn is a table of contents, which is what the paper already is"
            )
        presentations[paper_id] = presentation

    return presentations, problems


def parse_slides(body: str) -> tuple[list[Slide], list[str]]:
    """`## [<act> · <type>] <title>` and the fences under it, per slide."""
    slides: list[Slide] = []
    problems: list[str] = []
    for chunk in re.split(r"^## ", body, flags=re.M)[1:]:
        head, _, rest = chunk.partition("\n")
        m = HEAD_RE.match(head.strip())
        if not m:
            problems.append(
                f"slide header {head.strip()!r} is not `[<act> · <type>] <title>`"
            )
            continue
        act, kind, title = m.groups()
        where = f"slide {len(slides) + 1} ({title})"
        if act not in ACTS:
            problems.append(f"{where}: act {act!r} is not one of 起 承 轉 結")
            continue
        if kind not in TYPE_FENCE:
            problems.append(
                f"{where}: type {kind!r} is not one of "
                f"{' '.join(sorted(TYPE_FENCE))}"
            )
            continue

        data: dict = {}
        for fence in FENCES:
            raw, rest = _cut(fence, rest)
            if raw is None:
                continue
            if fence == "script":
                data["script"] = raw
                continue
            try:
                data[fence] = json.loads(raw)
            except json.JSONDecodeError as exc:
                problems.append(f"{where}: ```probe-{fence} is not JSON — {exc}")

        need = TYPE_FENCE[kind]
        if need and need not in data:
            problems.append(f"{where}: a {kind} slide needs ```probe-{need}")
            continue
        problems += _check_registers(where, data)

        bullets = [l[2:].strip() for l in rest.split("\n") if l.startswith("- ")]
        claim = " ".join(l.strip() for l in rest.split("\n")
                         if l.strip() and not l.startswith(("- ", "#", "`")))
        slides.append(Slide(act=act, kind=kind, title=title, claim=claim,
                            bullets=bullets, data=data,
                            script=data.pop("script", "")))
    return slides, problems


def _cut(fence: str, rest: str) -> tuple[str | None, str]:
    m = re.search(r"```probe-" + fence + r"\n(.*?)\n```", rest, re.S)
    if not m:
        return None, rest
    return m.group(1), rest.replace(m.group(0), "")


def _check_registers(where: str, data: dict) -> list[str]:
    """The two-register rule (`presentation/AUTHORING.md` §2), where it is structural.

    A claim with nothing under it is a bullet; a claim with the number or the
    source that makes it checkable is evidence. The build can only see the
    *shape* — whether the second register exists — so that is what it checks,
    and a genuinely absent one is left alone: the paper does not always supply
    it, and an invented `n` is worse than a bare line.

    What it will not accept is a created figure with no `why`. That one is not
    a matter of what the paper supplied: a drawn figure has to say which of the
    paper's own figures covers the ground and what this one strips out.
    """
    problems = []
    fig = data.get("figure")
    if isinstance(fig, dict):
        gone = [k for k in ("url", "caption", "source")
                if not str(fig.get(k, "")).strip()]
        if gone:
            problems.append(
                f"{where}: ```probe-figure has no `"
                + "`, `".join(gone)
                + "` — a figure the room cannot look up is a picture, and on "
                  "the cover there is no evidence ribbon to put the provenance in"
            )
    dia = data.get("diagram")
    if dia and not str(dia.get("why", "")).strip():
        problems.append(
            f"{where}: ```probe-diagram has no `why` — a drawn figure states "
            f"which of the paper's own figures covers this ground and what "
            f"this one leaves out"
        )
    facts = data.get("facts")
    if facts is not None and not isinstance(facts, list):
        problems.append(f"{where}: ```probe-facts is not a list of cells")
    elif facts and len(facts) > FACTS_MAX:
        problems.append(
            f"{where}: ```probe-facts has {len(facts)} cells — at most "
            f"{FACTS_MAX}. Past three it is a table the audience reads instead "
            f"of listening"
        )
    return problems


# ── drawing ───────────────────────────────────────────────────────────

_BOLD = re.compile(r"\*\*(.+?)\*\*")
_CODE = re.compile(r"`([^`]+)`")


def inline(text: str, breaks: bool = False) -> str:
    """Slide text. Bold, code, and the authored line break — nothing else.

    ` / ` is the only way a line breaks on a slide (`presentation/AUTHORING.md` §5).
    A break that came from the container's width instead is a wrap, and the
    author never saw where it landed.
    """
    out = _BOLD.sub(r"<b>\1</b>", c.esc(text))
    out = _CODE.sub(r'<i class="m">\1</i>', out)
    return out.replace(" / ", "<br>") if breaks else out


def render(presentation: Presentation) -> str:
    """The whole talk — every slide, each with its speaker essay under it."""
    return "\n".join(_slide(i, s, len(presentation.slides), presentation)
                     for i, s in enumerate(presentation.slides))


def deck(presentation: Presentation) -> str:
    """The deck under the frame — where in the talk this slide is.

    One tick per slide, in its act's colour, so the strip is the act rail read
    a second way: the shape of the talk and the reader's position in it are the
    same drawing. A tick is a button because the question a reader asks of a
    talk they are halfway through is "what was the turn again", and eight
    presses of → is not an answer to it.

    Drawn only under `data-browsing`, which `presentation.js` sets. Without a
    script every slide is on screen already and there is no position to mark,
    so the strip would be a control pointing at nothing.
    """
    ticks = "".join(
        f'<button type="button" class="prs-tick prs-r{ACT_ORDER[sl.act]}" '
        f'data-pres-go="{i}" aria-label="{i + 1}장 · {c.esc(ACTS[sl.act])}" '
        f'title="{i + 1}. {c.esc(sl.title.replace(" / ", " "))}"></button>'
        for i, sl in enumerate(presentation.slides))
    return (f'<div class="prs-deck" data-pres-deck>'
            f'<div class="prs-ticks">{ticks}</div>'
            f'<p class="prs-where"><b data-pres-at>1</b>'
            f'<i>/</i>{len(presentation.slides)}</p></div>')


def _slide(i: int, s: Slide, total: int, presentation: Presentation) -> str:
    inner = _compose(s, presentation)
    facts = _facts(s.data["facts"]) if s.data.get("facts") else ""
    head = ("" if s.kind == "statement"
            else f"<h3>{inline(s.title, True)}</h3>")
    # A cover that carries a figure splits the frame, which is a different
    # composition rather than a decorated one — the class is what the CSS needs
    # to give the text a column and the image the edge.
    mod = " prs-hero" if s.kind == "cover" and s.data.get("figure") else ""
    # The eyebrow says the beat in the word the room can use. The glyph is the
    # author's spine and the presenter's position marker, so it rides on the
    # element as data and the notes window shows it — printing both on the
    # slide is one line saying the same thing twice.
    return f"""<article class="prs-slide prs-{c.esc(s.kind)}{mod}" id="s{i + 1}"
         data-act="{c.esc(s.act)}">
  <header><span class="prs-act">{c.esc(ACTS[s.act])}</span>{head}</header>
  <div class="prs-body">{inner}</div>
  {facts}
  <footer><span>{c.esc(presentation.title)}</span><span>{i + 1} / {total}</span></footer>
</article>
{_script(s.script, f"s{i + 1}")}"""


def _rail(presentation) -> str:
    """The presentation's own shape, drawn — what fills a cover that has no figure.

    §4 refuses a created figure that argues something the paper does not say,
    and this argues nothing about the paper at all: every value in it is the
    source's own declaration, the act on each slide header, counted. What it
    tells the room is how long this will take and in what order, which is the
    one thing the spine cannot say. It is the fallback rather than the default:
    a photograph from the paper says more to a room than the presentation's own
    proportions do.

    Runs are consecutive rather than totalled per act, so a presentation that returns
    to a beat draws two blocks and says so.
    """
    runs: list[list] = []
    for sl in presentation.slides:
        if runs and runs[-1][0] == sl.act:
            runs[-1][1] += 1
        else:
            runs.append([sl.act, 1])

    n = len(presentation.slides)
    blocks = ""
    for act, count in runs:
        cells = "".join("<i></i>" for _ in range(count))
        blocks += (f'<div class="prs-rblock prs-r{ACT_ORDER[act]}" '
                   f'style="--n:{count}">'
                   f'<div class="prs-rcells">{cells}</div>'
                   f'<span class="prs-rlab">{c.esc(act)}<em>{c.esc(ACTS[act])}</em>'
                   f"</span></div>")
    return (f'<div class="prs-rail" aria-hidden="true">{blocks}</div>'
            f'<p class="prs-railfoot">{n}장 · {c.esc(presentation.minutes)}분</p>')


def _compose(s: Slide, presentation: Presentation) -> str:
    """The composition follows the slide's own shape.

    One grid over every type is what leaves the holes: a claim standing alone
    wants the frame, a figure wants to fill it, two panels want to be read
    against each other, and a ledger wants both columns to close on their own
    conclusion.
    """
    d = s.data
    if s.kind == "cover":
        # The spine, at the size it is worth. It is already in the front matter
        # and in the tab's lead, and it is here for a third time on purpose:
        # the lead is read by whoever opened the tab, and this is what the room
        # is looking at while the talk starts. A listener who disagrees with
        # the spine should be able to say so from the first slide.
        lis = "".join(f"<li>{inline(b)}</li>" for b in s.bullets)
        said = (f'<p class="prs-spineline">{inline(presentation.spine, True)}</p>'
                f'<div class="prs-colophon">'
                f'<p class="prs-meta">{c.esc(presentation.venue)}</p>'
                f'<p class="prs-paper">{c.esc(presentation.title)}</p>'
                f'<ul class="prs-points">{lis}</ul></div>')
        # With a figure the frame splits and the image takes the half the rail
        # otherwise fills; without one the rail is what fills it.
        if s.data.get("figure"):
            return f'<div class="prs-left">{said}</div>' + _cover_art(s.data["figure"])
        return said + _rail(presentation)
    if s.kind == "statement":
        said = (f'<div class="prs-said"><p class="prs-say">{inline(s.title, True)}</p>'
                f'<p class="prs-sub">{inline(s.claim, True)}</p></div>')
        return said + (_diagram(d["diagram"]) if d.get("diagram") else "")
    if s.kind == "evidence":
        return _figure(d["figure"]) + (
            f'<p class="prs-claim">{inline(s.claim)}</p>' if s.claim else "")
    if s.kind == "split":
        lis = "".join(f"<li>{inline(b)}</li>" for b in s.bullets)
        return _figure(d["figure"]) + f'<ul class="prs-points">{lis}</ul>'
    if s.kind == "versus":
        v = d["versus"]
        return _panel(v["left"], "prs-wall") + _panel(v["right"], "prs-wall")
    if s.kind == "ledger":
        l = d["ledger"]
        return _panel(l["buy"], "prs-buy") + _panel(l["sell"], "prs-sell")
    if s.kind == "budget":
        return _budget(d["budget"]) + (
            f'<p class="prs-claim">{inline(s.claim)}</p>' if s.claim else "")
    if s.kind == "timing":
        return _timing(d["timing"])
    if s.kind == "lineage":
        return _lineage(d["lineage"]) + (
            f'<p class="prs-claim">{inline(s.claim)}</p>' if s.claim else "")
    return ""


def _panel(p: dict, cls: str) -> str:
    """One column of a versus or a ledger.

    Two things keep it from reading as a floating bullet list. Each item
    carries a second register — the number or source that makes the claim
    checkable — and the column closes on `foot`, its own one-line conclusion,
    which holds the bottom edge so the last item does not hang in the middle
    of the card.
    """
    def item(l) -> str:
        if isinstance(l, str):
            return f"<li>{inline(l)}</li>"
        note = f'<span>{inline(l["n"])}</span>' if l.get("n") else ""
        return f'<li>{inline(l["t"])}{note}</li>'

    lines = "".join(item(l) for l in p["lines"])
    foot = f'<p class="prs-foot">{inline(p["foot"])}</p>' if p.get("foot") else ""
    return (f'<div class="prs-panel {cls}"><h4>{inline(p["head"])}</h4>'
            f"<ul>{lines}</ul>{foot}</div>")


def _facts(rows: list) -> str:
    """The evidence ribbon every slide closes on.

    Not decoration for a slide that came out short: each cell is a number the
    slide leans on. A cell the paper does not supply is dropped rather than
    filled, and a ribbon of two is a ribbon of two.
    """
    cells = "".join(
        f'<div class="prs-fact"><b>{inline(r["값"])}</b>'
        f'<span>{inline(r["라벨"])}</span></div>' for r in rows)
    return f'<div class="prs-facts">{cells}</div>'


def _cover_art(f: dict) -> str:
    """The cover's figure, bled to the edge of the frame.

    Everywhere else a figure sits inside the frame with its caption under it,
    because the slide is arguing with it. Here it is not evidence — it is what
    the room looks at while the talk starts, and the half of the frame it takes
    is most of why a title slide reads as one. The caption goes over the image
    for the same reason: the composition has no row left to give it.
    """
    return (f'<div class="prs-art"><img src="{c.esc(f.get("url", ""))}" alt="" '
            f'loading="lazy">'
            f'<p class="prs-artcap">{c.esc(f.get("caption", ""))}'
            f'<span>{c.esc(f.get("source", ""))}</span></p></div>')


def _figure(f: dict) -> str:
    return (f'<figure class="prs-fig">'
            f'<img src="{c.esc(f.get("url", ""))}" alt="" loading="lazy">'
            f'<figcaption><b>{c.esc(f.get("source", ""))}</b> '
            f'{c.esc(f.get("caption", ""))}</figcaption></figure>')


def _diagram(d: dict) -> str:
    """A routing change — one lane becoming two and merging again.

    The shape of a paper that moved where a signal goes. It is drawn rather
    than quoted because the paper's own concept figure carries the whole model
    and this is one scene out of it; `why` says which figure that is and what
    this one leaves out, and the build refuses the fence without it.
    """
    def box(b: dict) -> str:
        note = f'<span>{inline(b["note"])}</span>' if b.get("note") else ""
        loop = ""
        if b.get("loop"):
            # State carried across timesteps. Boxes and arrows cannot say it,
            # so it is a line rather than another note.
            loop = ('<span class="prs-loop">'
                    '<svg viewBox="0 0 100 26" preserveAspectRatio="none" '
                    'aria-hidden="true" focusable="false">'
                    '<path d="M93 26 L93 19 Q93 13 87 13 L13 13 Q7 13 7 19 L7 23"/>'
                    '<path class="hd" d="M3.4 18 L7 24.5 L10.6 18"/></svg>'
                    f'<i>{inline(b["loop"])}</i></span>')
        cls = "prs-box" + (" hot" if b.get("hot") else "") + (" looped" if loop else "")
        return f'<div class="{cls}">{loop}<b>{inline(b["box"])}</b>{note}</div>'

    before = '<i class="prs-arw">→</i>'.join(box(b) for b in d["before"]["chain"])
    a = d["after"]
    after = (f'<div class="prs-split"><div class="prs-lanes">'
             f'{box(a["slow"])}{box(a["fast"])}</div>'
             f'<div class="prs-merge"><svg viewBox="0 0 40 100" '
             f'preserveAspectRatio="none" aria-hidden="true" focusable="false">'
             f'<path d="M0 26 C22 26, 22 50, 40 50"/>'
             f'<path d="M0 74 C22 74, 22 50, 40 50"/></svg></div>'
             f'{box(a["join"])}<i class="prs-arw">→</i>{box(a["out"])}</div>')
    return (f'<div class="prs-diag">'
            f'<div class="prs-drow"><span class="prs-dlab">'
            f'{inline(d["before"]["label"])}</span>'
            f'<div class="prs-chain">{before}</div></div>'
            f'<div class="prs-drow"><span class="prs-dlab hot">'
            f'{inline(a["label"])}</span>{after}</div>'
            f'<p class="prs-why">{inline(d["why"])}</p></div>')


def _budget(b: dict) -> str:
    """Where one call goes, against the time there is to spend it.

    A duration means nothing on its own: 140 ms is a number until it is put
    beside the 20 ms tick it has to fit inside. So the budget is two bars on one
    scale — what the call costs, and what one turn of the control loop affords —
    and the control period is drawn across the first as well, so the count is
    something the room reads off the bar rather than something the bar claims.
    """
    total = sum(p["ms"] for p in b["항목"])
    per = b["제어주기"]
    segs = "".join(
        f'<div class="prs-seg prs-g{i}" style="--w:{p["ms"] / total * 100:.2f}%">'
        f'<span>{p["ms"]:g}</span></div>' for i, p in enumerate(b["항목"]))
    # Interior ticks only: the two ends are the bar's own edges, and a hairline
    # drawn over a border reads as a thicker border.
    ticks = "".join(
        f'<i style="--x:{x / total * 100:.2f}%"></i>'
        for x in range(int(per["ms"]), int(total), int(per["ms"])))
    keys = "".join(
        f'<li><i class="prs-sw prs-g{i}"></i>'
        f'<span class="prs-ktext">{inline(p["label"])}'
        + (f'<span>{inline(p["note"])}</span>' if p.get("note") else "")
        + f'</span><b>{p["ms"]:g} ms</b></li>'
        for i, p in enumerate(b["항목"]))
    return (
        f'<div class="prs-bud"><div class="prs-bgroup">'
        f'<div class="prs-brow"><span class="prs-blab">{c.esc(b.get("이름", ""))}</span>'
        f'<div class="prs-bmeter"><div class="prs-bbar">{segs}</div>'
        f'<div class="prs-bticks" aria-hidden="true">{ticks}</div></div>'
        f'<b>{total:g} ms</b></div>'
        f'<div class="prs-brow"><span class="prs-blab">{c.esc(per["label"])}</span>'
        f'<div class="prs-bmeter"><div class="prs-bbar prs-btick" '
        f'style="--w:{per["ms"] / total * 100:.2f}%"></div></div>'
        f'<b>{per["ms"]:g} ms</b></div>'
        f'<p class="prs-bfoot">{total:g} ms = {c.esc(per["label"])} '
        f'{total / per["ms"]:.1f} 칸</p></div>'
        f'<ul class="prs-keys">{keys}</ul></div>')


def _timing(t: dict) -> str:
    """Several rows on one time ruler, with the control period as its ticks."""
    span = t["span_ms"]
    per = t["제어주기"]["ms"]
    ticks = "".join(
        f'<i style="--x:{x / span * 100:.2f}%"></i>'
        for x in range(0, int(span) + 1, int(per)))
    rows = ""
    for row in t["줄"]:
        blocks = "".join(
            f'<div class="prs-blk prs-{b.get("kind", "wait")}" '
            f'style="--x:{b["at"] / span * 100:.2f}%;'
            f'--w:{b["ms"] / span * 100:.2f}%">'
            f'<span>{inline(b["label"])}</span></div>' for b in row["blocks"])
        mark = ""
        if row.get("mark"):
            mk = row["mark"]
            mark = (f'<div class="prs-mk{" us" if mk.get("us") else ""}" '
                    f'style="--x:{mk["at"] / span * 100:.2f}%">'
                    f'<b>{inline(mk["label"])}</b></div>')
        rows += (f'<div class="prs-row"><span class="prs-rname">'
                 f'{inline(row["name"])}</span>'
                 f'<div class="prs-lane">{ticks}{blocks}{mark}</div></div>')
    axis = "".join(f'<span style="--x:{x / span * 100:.2f}%">{x:g}</span>'
                   for x in (0, span / 2, span))
    return (f'<div class="prs-tim">{rows}'
            f'<div class="prs-row"><span class="prs-rname"></span>'
            f'<div class="prs-axis">{axis}</div></div>'
            f'<p class="prs-tnote">세로선 한 칸이 '
            f'{c.esc(t["제어주기"]["label"])} — {per:g} ms</p></div>')


def _lineage(l: dict) -> str:
    """What this paper is downstream of.

    Every value here — the date, the name, what each prior gave — is one the
    rewrite already carries, so nothing is invented in the drawing. What the
    drawing adds is the convergence: a list states publication order, and the
    point of the slide is that these lines meet here.

    The merge is cut for however many priors there are rather than for two, so
    a lineage of three does not have one line arriving from nowhere.
    """
    items = l["items"]
    n = len(items)
    priors = "".join(
        f'<div class="prs-node"><span class="prs-when">{c.esc(a["when"])}</span>'
        f'<b>{inline(a["what"])}</b>'
        f'<span class="prs-nnote">{inline(a["gave"])}</span></div>'
        for a in items)
    paths = "".join(
        f'<path d="M0 {(i + .5) / n * 100:.1f} '
        f'C22 {(i + .5) / n * 100:.1f}, 22 50, 40 50"/>' for i in range(n))
    me = l["me"]
    return (f'<div class="prs-lin"><div class="prs-priors">{priors}</div>'
            f'<div class="prs-join"><svg viewBox="0 0 40 100" '
            f'preserveAspectRatio="none" aria-hidden="true" focusable="false">'
            f'{paths}</svg></div>'
            f'<div class="prs-node hot">'
            f'<span class="prs-when">{c.esc(me["when"])}</span>'
            f'<b>{inline(me["what"])}</b>'
            f'<span class="prs-nnote">{inline(me["gave"])}</span></div></div>')


def _script(text: str, of: str) -> str:
    """The speaker essay, under the slide it belongs to.

    Under rather than beside: the slide is what the room looks at and the essay
    is what the presenter reads, and the two are never on screen together. It
    carries no fact the slide does not show — a number worth saying is in the
    ribbon or in an item's second register, and the essay points at it.

    `data-for` names the slide, so the surfaces that show one essay at a time —
    the notes toggle and the presenter's window — ask for the essay *of this
    slide* rather than for the nth essay. §6 asks every slide for one, but a
    presentation that is short an essay is a presentation missing an essay, not
    one whose every later slide reads the wrong one.
    """
    if not text.strip():
        return ""
    paras = "".join(f"<p>{inline(p.replace(chr(10), ' '))}</p>"
                    for p in text.strip().split("\n\n") if p.strip())
    return (f'<div class="prs-script" data-for="{c.esc(of)}">'
            f'<h4>말할 것</h4>{paras}</div>')
