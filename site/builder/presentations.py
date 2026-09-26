"""Discover the presentations the site publishes, and draw their slides.

A presentation is one paper retold as a talk — `presentation/<arxiv-id>.md`,
written by `/present`. Only a paper with a rewrite in `analysis/` may have one,
and every slide declares its act (起承轉結) and its type; the type decides the
composition. The contract is `presentation/AUTHORING.md`.

Discovery and drawing sit in one module for the same reason `glance.py` does:
the surface is small, its rules are its layout, and splitting them would put a
schema in one file and the reason for it in another.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import charts
from . import components as c
from . import corpus, frontmatter

PRESENTATION_DIR = corpus.REPO_ROOT / "presentation"

ID_RE = re.compile(r"^\d{4}\.\d{4,5}$")
SOURCE_RE = re.compile(r"^(\d{4}\.\d{4,5})v(\d+)$")
HEAD_RE = re.compile(r"^\[(\S+) · (\w+)\]\s*(.+)$")

# The four beats, with the word each one is doing on a slide. The labels are
# printed, not just validated: the beat is what the room reads the slide as.
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
    "contrast": "contrast",
    "inheritance": "inheritance",
    "chart": "chart",
    "heat": "heat",
}

# The fences a slide may carry beside the one its type is drawn from. `video`
# rides only beside the paper's own figure, because that figure is what the
# slide is whenever the clip cannot play (`presentation/AUTHORING.md` §8-1).
EXTRA_FENCES = ("diagram", "video", "facts", "script")
VIDEO_TYPES = ("evidence", "split")

# A clip is a file the authors' page serves, played by the browser — never a
# player embedded from a video platform, which takes the keyboard the deck
# runs on and has no figure to fall back to.
CLIP_RE = re.compile(r"^https://[^\s/]+/\S+\.(?:mp4|webm)(?:\?\S*)?$", re.I)
EMBED_RE = re.compile(r"(?:youtube\.com|youtu\.be|vimeo\.com|/embed/|<iframe)", re.I)
PAGE_RE = re.compile(r"^https://\S+$")
# A pair is the one comparison worth a second clip; a third is a grid the room
# watches instead of listening.
CLIPS_MAX = 2
FENCES = tuple(f for f in TYPE_FENCE.values() if f) + EXTRA_FENCES

REQUIRED_FRONT = ("presentation_of", "title", "venue", "audience", "minutes", "spine",
                  "arxiv_html", "generated")

# `probe-facts` is the evidence ribbon — the numbers a slide leans on that its
# visual does not already put on screen. Three cells is the most; two is what a
# slide with only two numbers gets. More than three stops being a ribbon and
# starts being a table the audience reads instead of listening.
FACTS_MAX = 3

# The widest a headline's authored line may run, in the ems `_fit` measures.
# A headline is sized to fit its widest line, so a line past this is set
# below about four-fifths of the headline size — the point where a claim
# stops reading as the largest thing on the frame. The fix is a ` / ` at its
# seam (§5), which is the author's to place.
HEADLINE_EM_MAX = 33

# A figure's `crop` and the cover's `focus`, in the forms CSS takes them.
_PCT = r"(?:0|\d{1,2}(?:\.\d+)?%)"
_CROP = re.compile(rf"{_PCT}(?:\s+{_PCT}){{0,3}}")
_FOCUS = re.compile(r"\d{1,3}(?:\.\d+)?%\s+\d{1,3}(?:\.\d+)?%")


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
        # A figure that does not fit its own shape cannot be drawn — a series
        # shorter than its axis has no mark for the last tick — so the slide
        # is skipped rather than drawn wrong.
        broken = [p for fence in ("chart", "heat", "timing") + charts.LINEAGE
                  if fence in data
                  for p in charts.problems(where, fence, data[fence])]
        if broken:
            problems += broken
            continue
        problems += _check_frame(where, data)
        problems += _check_video(where, kind, data)
        if _widest(title) > HEADLINE_EM_MAX:
            problems.append(
                f"{where}: a header line runs {_widest(title):.0f} em — past "
                f"{HEADLINE_EM_MAX} it is set too small to lead the frame. Break "
                f"it with ` / ` where the claim turns"
            )

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


def _check_frame(where: str, data: dict) -> list[str]:
    """The fences a slide carries, where their shape is checkable at build time.

    A `probe-figure` needs `url`, `caption` and `source` and takes `crop` and
    `focus` in the form CSS does, a `probe-diagram` or `probe-timing` needs its
    `why` (`presentation/AUTHORING.md` §4-2), and `probe-facts` is a list of at
    most `FACTS_MAX` cells. The two-register floor on panel items is
    `linters/check-presentation-format.py`'s, not the build's.
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
    if isinstance(fig, dict):
        if fig.get("crop") and not _CROP.fullmatch(str(fig["crop"]).strip()):
            problems.append(
                f"{where}: ```probe-figure `crop` is {fig['crop']!r} — one to four "
                f"percentages, top right bottom left, as CSS `inset()` takes them "
                f"(`0 0 0 62%` keeps the right 38 %)"
            )
        if fig.get("focus") and not _FOCUS.fullmatch(str(fig["focus"]).strip()):
            problems.append(
                f"{where}: ```probe-figure `focus` is {fig['focus']!r} — two "
                f"percentages, across then down (`30% 50%`)"
            )
    for fence in ("diagram", "timing"):
        dia = data.get(fence)
        if isinstance(dia, dict) and not str(dia.get("why", "")).strip():
            problems.append(
                f"{where}: ```probe-{fence} has no `why` — a drawn figure states "
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


def _check_video(where: str, kind: str, data: dict) -> list[str]:
    """The authors' clip (`presentation/AUTHORING.md` §8-1), where it is structural.

    A clip that breaks a rule is dropped and the slide publishes on its
    figure — which is what the slide is anyway whenever the clip cannot play —
    so a bad fence costs the motion, never the slide.
    """
    vid = data.get("video")
    if vid is None:
        return []
    bad = []
    if kind not in VIDEO_TYPES or not isinstance(data.get("figure"), dict):
        bad.append(
            f"{where}: ```probe-video rides on an {' or '.join(VIDEO_TYPES)} slide "
            f"beside the paper's own ```probe-figure — that figure is the slide "
            f"whenever the clip cannot play, is printed, or runs with no script")
    if not isinstance(vid, dict):
        data.pop("video", None)
        return bad + [f"{where}: ```probe-video is not an object"]
    clips = vid.get("clips")
    if not isinstance(clips, list) or not clips:
        bad.append(f"{where}: ```probe-video has no `clips`")
        clips = []
    if len(clips) > CLIPS_MAX:
        bad.append(f"{where}: ```probe-video has {len(clips)} clips — at most "
                   f"{CLIPS_MAX}. A pair is a comparison; past that it is a grid "
                   f"the room watches instead of listening")
    for clip in clips:
        src = str(clip.get("src", "")) if isinstance(clip, dict) else ""
        if EMBED_RE.search(src):
            bad.append(f"{where}: clip {src!r} is an embedded player — it takes the "
                       f"keyboard the deck runs on and cannot fall back to the "
                       f"figure. Name it in the essay for after the talk")
        elif not CLIP_RE.match(src):
            bad.append(f"{where}: clip {src!r} is not an https `.mp4` or `.webm` — "
                       f"a clip is a file the authors' page serves")
        if len(clips) > 1 and not (isinstance(clip, dict)
                                   and str(clip.get("label", "")).strip()):
            bad.append(f"{where}: a clip in a pair has no `label` — the room has to "
                       f"know which side is which")
    gone = [k for k in ("page", "caption", "source") if not str(vid.get(k, "")).strip()]
    if gone:
        bad.append(f"{where}: ```probe-video has no `" + "`, `".join(gone)
                   + "` — a clip is published by the paper's authors somewhere, "
                     "and the room is owed where")
    elif not PAGE_RE.match(str(vid["page"])):
        bad.append(f"{where}: ```probe-video `page` is not an https URL")
    if bad:
        data.pop("video", None)
    return bad


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


def _widest(text: str) -> float:
    """The widest authored line of `text`, in ems — see `_fit`."""
    def width(line: str) -> float:
        line = _BOLD.sub(r"\1", line)
        return sum(0.28 if ch == " " else
                   0.88 if ord(ch) >= 0x1100 else
                   0.62 if ch.isupper() else 0.54 for ch in line)
    return max(width(line) for line in text.split(" / "))


def _fit(text: str) -> str:
    """The widest authored line of a headline, in ems, as `--len`.

    A headline is set as large as its column allows, and what the column has
    to hold is the longest line the author wrote — never a line the column
    made by wrapping (`presentation/AUTHORING.md` §5-1). So the stylesheet
    sizes it as `min(ceiling, column / --len)`, which lets a short claim take
    the full size and keeps a long one on the lines it was broken into.
    Hangul is taken at just under an em, Latin and digits at a little over
    half — generous, so an estimate that errs leaves a margin, not a wrap.
    """
    return f' style="--len:{_widest(text):.1f}"'


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
    # The ribbon rides beside a `split` figure and under everything else.
    # Beside, because a square figure at full height leaves a column and a
    # row of numbers under it takes the height the figure needs; under,
    # because every other composition is as wide as the frame.
    beside = s.kind == "split"
    facts = (_facts(s.data["facts"]) if s.data.get("facts") and not beside
             else "")
    head = ("" if s.kind == "statement"
            else f"<h3{_fit(s.title)}>{inline(s.title, True)}</h3>")
    # A cover that carries a figure splits the frame, which is a different
    # composition rather than a decorated one — the class is what the CSS needs
    # to give the text a column and the image the edge.
    mod = " prs-hero" if s.kind == "cover" and s.data.get("figure") else ""
    # The chrome is the page number and nothing else: the paper's title is on
    # the cover and on the page the tab sits in, and a slide that repeats it
    # in every corner spends the room's attention on a line it already read.
    foot = ("" if s.kind == "cover"
            else f'<footer><span>{i + 1:02d}</span></footer>')
    return f"""<article class="prs-slide prs-{c.esc(s.kind)}{mod}" id="s{i + 1}"
         data-act="{c.esc(s.act)}">
  <header>{_eyebrow(s.act)}{head}</header>
  <div class="prs-body"{_rows(s)}>{inner}</div>
  {facts}
  {foot}
</article>
{_script(s.script, f"s{i + 1}", _notes(s.data))}"""


def _rows(s: Slide) -> str:
    """The row tracks two panel columns share.

    A ledger's two columns are read across as much as down — the first thing
    each side buys or sells, then the second — so an item sits on the same
    row as its counterpart even when the one beside it runs to two lines. The
    stylesheet lays both columns on one grid of these rows (`subgrid`); the
    count is the longer column's.
    """
    fence = {"ledger": "ledger", "versus": "versus"}.get(s.kind)
    if not fence or not isinstance(s.data.get(fence), dict):
        return ""
    cols = [v for v in s.data[fence].values() if isinstance(v, dict)]
    n = max((len(col.get("lines", [])) for col in cols), default=0)
    return f' style="--items:{max(n, 1)}"'


# The frame, in the units the stylesheet sets it in: a share of the content
# box's width (`cqw`). These are the heights each part of a slide takes, so the
# drawing handed the rest can be laid out at the shape it will be shown at.
_FRAME_H = 54.5          # 16 : 9 less the padding, in cqw of the content width
_EYEBROW = 3.1
_BODY_PAD = 2.4
_GAP = 2.0
_SRC = 3.1               # the provenance line under a drawing, with its gap
_FACTS = 9.8
_STEPPER = 3.6           # the row naming a stepped figure's states


def _ratio(s: Slide) -> float:
    """The shape of the box a drawing on this slide gets — width over height.

    Estimated from what the slide stacks above and below the drawing: the
    headline at the size its widest authored line is set at, the takeaway
    line, the provenance under the figure, a ribbon. The estimate errs short
    — a box taken to be a little shorter than it is leaves the drawing a thin
    margin above and below, where one taken to be taller would leave it
    standing in the middle of the frame with empty flanks.
    """
    lines = len(s.title.split(" / "))
    if s.kind == "statement":
        say = min(5.4, 58 / max(_widest(s.title), 1))
        used = _EYEBROW + 1.0 + lines * say * 1.12 + _GAP
    else:
        size = min(3.7, 98 / max(_widest(s.title), 1))
        used = _EYEBROW + lines * size * 1.16 + _BODY_PAD
        if s.claim:
            claim_lines = max(1, int(_widest(s.claim) * 1.75 // 96) + 1)
            used += _GAP + claim_lines * 1.75 * 1.5
        if s.data.get("facts"):
            used += _FACTS
    if any(isinstance(s.data.get(f), dict) and s.data[f].get("steps")
           for f in ("chart", "heat")):
        used += _STEPPER
    used += _SRC + 1.5
    return 100 / max(_FRAME_H - used, 12)


def _eyebrow(act: str) -> str:
    """Where in the four beats this slide stands, and the beat's word.

    Four short bars in the act colours, the current one drawn solid and long,
    the ones behind it at half strength and the ones ahead as outlines — the
    act rail of the cover carried onto every slide, so the room feels the talk
    turn rather than being told it did. The word is the beat in the language
    the room uses; the glyph stays on the element as `data-act`, because
    printing both is one line saying the same thing twice.
    """
    here = ACT_ORDER[act]
    bars = "".join(
        f'<i class="prs-r{n}{" on" if n == here else " past" if n < here else ""}"></i>'
        for n in range(1, len(ACTS) + 1))
    return (f'<div class="prs-eyebrow"><span class="prs-acts" aria-hidden="true">'
            f'{bars}</span><span class="prs-act">{c.esc(ACTS[act])}</span></div>')


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
        said = (f'<p class="prs-spineline"{_fit(presentation.spine)}>{inline(presentation.spine, True)}</p>'
                f'<div class="prs-colophon">'
                f'<p class="prs-meta">{c.esc(presentation.venue)}</p>'
                f'<p class="prs-paper">{c.esc(presentation.title)}</p>'
                f'<ul class="prs-points">{lis}</ul></div>')
        # With a figure the frame splits and the image takes the share of it
        # the rail otherwise fills; without one the rail is what fills it.
        if s.data.get("figure"):
            return f'<div class="prs-left">{said}</div>' + _cover_art(s.data["figure"])
        return said + _rail(presentation)
    if s.kind == "statement":
        # The turn, on its tinted ground. With a visual the sentence stands over
        # it at the width of the frame; the visual is what the sentence is
        # permitted by — a drawing of the mechanism, a chart of the numbers
        # that force it, or the paper's own figure — so it takes the rest of
        # the frame under it.
        said = (f'<div class="prs-said"><p class="prs-say"{_fit(s.title)}>{inline(s.title, True)}</p>'
                f'<p class="prs-sub">{inline(s.claim, True)}</p></div>')
        r = _ratio(s)
        if d.get("timing"):
            return said + charts.timing(d["timing"], r)
        if d.get("chart"):
            return said + charts.chart(d["chart"], r)
        if d.get("heat"):
            return said + charts.heat(d["heat"], r)
        if d.get("figure"):
            f = d["figure"]
            return said + (f'<div class="prs-sfig">{_figure(f)}'
                           f'<p class="prs-src">{c.esc(f.get("source", ""))}</p></div>')
        return said + (_diagram(d["diagram"]) if d.get("diagram") else "")
    if s.kind == "evidence":
        # A figure wider than about 2 : 1 — a strip of photographs, a wide
        # plot — takes the frame's width, and what to see in it is one line
        # under it with its provenance beside. The caption is not printed: it
        # is the figure's alt text and closes the speaker essay (`_notes`).
        f = d["figure"]
        said = f'<p class="prs-claim">{inline(s.claim)}</p>' if s.claim else ""
        return (_figure(f, d.get("video")) + f'<div class="prs-under">{said}'
                f'{_src(f, d.get("video"))}</div>')
    if s.kind == "split":
        # A squarer figure at full height, and everything else in one column
        # beside it: what to see in it, the numbers it shows, where it is from.
        # Stretched across the frame the same figure is a small plot with
        # white either side.
        lis = "".join(f"<li>{inline(b)}</li>" for b in s.bullets)
        said = (f'<ul class="prs-points">{lis}</ul>' if lis else
                f'<p class="prs-claim">{inline(s.claim)}</p>' if s.claim else "")
        f = d["figure"]
        facts = _facts(d["facts"]) if d.get("facts") else ""
        return (_figure(f, d.get("video")) + f'<div class="prs-aside">{said}{facts}'
                f'{_src(f, d.get("video"))}</div>')
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
        return charts.timing(d["timing"], _ratio(s)) + (
            f'<p class="prs-claim">{inline(s.claim)}</p>' if s.claim else "")
    if s.kind in ("chart", "heat"):
        fig = (charts.chart(d["chart"], _ratio(s)) if s.kind == "chart"
               else charts.heat(d["heat"], _ratio(s)))
        return fig + (f'<p class="prs-claim">{inline(s.claim)}</p>' if s.claim else "")
    if s.kind in charts.LINEAGE:
        draw = charts.contrast if s.kind == "contrast" else charts.inheritance
        return draw(d[s.kind], _ratio(s), _corpus_ids()) + (
            f'<p class="prs-claim">{inline(s.claim)}</p>' if s.claim else "")
    return ""


def _corpus_ids() -> frozenset:
    """Every paper with a rewrite in `analysis/` — the whole corpus, not the
    subset a `--only` build draws, because a prior on a lineage figure links
    to the page the published site has for that paper."""
    return frozenset(p.stem for p in (corpus.REPO_ROOT / "analysis").glob("*.md")
                     if ID_RE.match(p.stem))


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


_NUMERAL = re.compile(r"[−+-]?\d[\d.,]*")


def _figure_value(v: str) -> str:
    """A ribbon value set as a number rather than as a phrase.

    The numerals are what the room reads from the back, so they carry the
    size; the unit and the qualifier around them (`약`, `ms`, `차원`) are
    set small beside them, the way a slide sets `50 N` when it wants the 50
    to land. A value with no numeral in it — a robot's name — is a phrase and
    stays one size.
    """
    toks = v.split(" ")
    if not any(_NUMERAL.fullmatch(t) for t in toks):
        return f'<span class="prs-vtext">{c.esc(v)}</span>'
    return " ".join(
        f'<b>{c.esc(t)}</b>' if _NUMERAL.fullmatch(t) else f'<small>{c.esc(t)}</small>'
        for t in toks)


def _facts(rows: list) -> str:
    """The evidence ribbon — the numbers a slide leans on, set as numbers.

    Not decoration for a slide that came out short: each cell is a number the
    slide leans on. A cell the paper does not supply is dropped rather than
    filled, and a ribbon of two is a ribbon of two. No rules between cells and
    no box around them: a ruled row of three is a table, and a table is read
    rather than seen.
    """
    cells = "".join(
        f'<div class="prs-fact"><p class="prs-v">{_figure_value(r["값"])}</p>'
        f'<span>{inline(r["라벨"])}</span></div>' for r in rows)
    return f'<div class="prs-facts" style="--n:{len(rows)}">{cells}</div>'


def _src(f: dict, video: dict | None = None) -> str:
    """The provenance line under a paper figure — and, when the authors' clip
    is playing over it, the clip's, since the room is owed the source of what
    is on screen rather than of what would have been. The stylesheet shows
    whichever one the figure is showing."""
    still = c.esc(f.get("source", ""))
    if not video:
        return f'<p class="prs-src">{still}</p>'
    host = re.sub(r"^https://", "", video["page"]).split("/")[0]
    return (f'<p class="prs-src"><span class="prs-cap-still">{still}</span>'
            f'<span class="prs-cap-reel">{c.esc(video["source"])} · '
            f'<a href="{c.esc(video["page"])}" rel="noopener" target="_blank">'
            f'{c.esc(host)}</a></span></p>')


def _figure(f: dict, video: dict | None = None) -> str:
    """A paper's own figure, on a card of its own.

    The card is the paper's page: its figures are drawn on white, and a
    figure set straight onto a dark frame is a white slab with no edge. On the
    card the white is the card's ground, so in either theme the figure reads as
    a page laid on the slide rather than a hole cut in it.

    `crop` shows one region of the figure alone — the panel a multi-panel
    figure makes its point in — as `object-view-box`, which changes the
    image's own proportions to the region's, so the card is sized to the
    panel rather than to the whole page. A browser without it shows the whole
    figure, which is the figure the `source` names.
    """
    crop = (f' style="object-view-box: inset({c.esc(_inset(f["crop"]))})"'
            if f.get("crop") else "")
    img = (f'<img src="{c.esc(f.get("url", ""))}" '
           f'alt="{c.esc(f.get("caption", ""))}"{crop}')
    if video:
        return _reel(img, video)
    return f'<figure class="prs-fig">{img}></figure>'


def _reel(img: str, v: dict) -> str:
    """The paper's figure, with the authors' own clip of the same scene over it.

    The figure is not a poster thrown away once the clip loads: it is the
    slide. The clip is drawn over it only once `presentation.js` has frames
    for every clip, so one that cannot load — a codec the browser lacks, a host
    the room's network blocks, a page that moved — leaves the slide exactly as
    it would be without one, and so does a printout or a browser with no
    script. `data-src` rather than `src`: nothing is fetched until the talk is
    a slide away. No `loop`: a pair restarts together from the first clip's
    end, so its two sides never drift apart one loop at a time.
    """
    clips = "".join(
        f'<div class="prs-clip">'
        + (f'<span class="prs-cliplab">{inline(cl["label"])}</span>' if cl.get("label") else "")
        + f'<video muted playsinline preload="none" data-src="{c.esc(cl["src"])}" '
          f'aria-label="{c.esc(cl.get("label") or v["source"])}"></video></div>'
        for cl in v["clips"])
    return (f'<figure class="prs-fig prs-reel" data-reel>'
            f'{img} class="prs-still">'
            f'<div class="prs-clips" style="--n:{len(v["clips"])}">{clips}</div>'
            f'<div class="prs-rctl">'
            f'<button type="button" class="prs-rbtn" data-reel-toggle '
            f'aria-label="재생 / 일시정지" title="재생 / 일시정지 (K)">'
            f'{c.icon("pause", 14)}{c.icon("play", 14)}</button>'
            f'<button type="button" class="prs-rbtn prs-rate" data-reel-rate '
            f'aria-pressed="false" aria-label="느리게" title="½ 배속 (S)">½×</button>'
            f'</div></figure>')


def _inset(crop: str) -> str:
    """`crop` as the `inset()` it becomes — top, right, bottom, left, in
    percent of the image, the same shorthand CSS takes."""
    return " ".join(crop.split())


def _cover_art(f: dict) -> str:
    """The cover's figure, bled to the edge of the frame.

    Everywhere else a figure sits on its own card, sized to its shape, with
    the line that argues with it beside or under it. Here it is not evidence — it is what the room looks at while the talk
    starts, and the share of the frame it takes is most of why a title slide
    reads as one. The provenance goes over the image for the same reason: the
    composition has no column left to give it. The crop to a tall column is
    centred on `focus` — the point of the image that has to survive it, as an
    `object-position` — because only the author knows where the apparatus is.
    `focus` only pans: a figure whose photograph shares its image with other
    panels or with the paper's own caption text takes `crop` first, as on any
    figure, and the column is then filled from the cropped region alone.

    No image on a slide is loaded lazily. Every slide but one is hidden, and a
    hidden image deferred until its slide is shown arrives while the room is
    already looking at the empty frame.
    """
    rules = []
    if f.get("crop"):
        rules.append(f"object-view-box: inset({_inset(f['crop'])})")
    if f.get("focus"):
        rules.append(f"object-position: {f['focus']}")
    style = f' style="{c.esc("; ".join(rules))}"' if rules else ""
    return (f'<div class="prs-art"><img src="{c.esc(f.get("url", ""))}" '
            f'alt="{c.esc(f.get("caption", ""))}"{style}>'
            f'<p class="prs-artcap">{c.esc(f.get("source", ""))}</p></div>')


def _diagram(d: dict) -> str:
    """A routing change — one lane becoming two and merging again.

    The shape of a paper that moved where a signal goes. It is drawn rather
    than quoted because the paper's own concept figure carries the whole model
    and this is one scene out of it; `why` says which figure that is and what
    this one leaves out, and the build refuses the fence without it. The
    `why` closes the speaker essay rather than sitting under the drawing — see
    `_whys`.

    The fork is `prs-fork` rather than anything spelled like a slide type:
    every slide carries `prs-<type>`, and a diagram class that shares a type's
    name restyles the whole frame of that type.
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
    after = (f'<div class="prs-fork"><div class="prs-lanes">'
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
            f'{inline(a["label"])}</span>{after}</div></div>')


def _budget(b: dict) -> str:
    """Where one call goes, against the time there is to spend it.

    A duration means nothing on its own: 140 ms is a number until it is put
    beside the 20 ms tick it has to fit inside. So the call is one bar, and
    under it the control loop is drawn on the same scale as the cells it
    actually is — numbered, with the one cell the loop affords in the accent —
    so the count is something the room reads off the drawing rather than
    something the drawing claims. Each segment carries its own name, and what
    it is sits directly under it, so there is no legend to cross-reference.
    """
    total = sum(p["ms"] for p in b["항목"])
    per = b["제어주기"]
    segs = "".join(
        f'<div class="prs-seg prs-g{i}" style="--w:{p["ms"] / total * 100:.2f}%">'
        f'<b>{p["ms"]:g}<small> ms</small></b><span>{inline(p["label"])}</span></div>'
        for i, p in enumerate(b["항목"]))
    notes = "".join(
        f'<p style="--w:{p["ms"] / total * 100:.2f}%">{inline(p.get("note", ""))}</p>'
        for p in b["항목"])
    # One cell per control period the call spans; a remainder is a cell cut
    # short, so the row ends where the bar ends rather than on a round number.
    cells, x, n = "", 0.0, 0
    while x < total - 1e-9:
        w = min(per["ms"], total - x)
        n += 1
        on = ' class="on"' if n == 1 else ""
        cells += (f'<i{on} '
                  f'style="--w:{w / total * 100:.2f}%"><em>{n}</em></i>')
        x += w
    count = total / per["ms"]
    # The clock is provenance, so it opens the provenance line the way it
    # does under a chart, rather than riding in the cells' legend a second
    # time beside the source that names the same section.
    clock = (f'<span class="pc-clock">{c.esc(b["clock"])}</span>'
             if b.get("clock") else "")
    count_s = f"{count:g}" if count == int(count) else f"{count:.1f}"
    return (
        f'<div class="prs-bud">'
        f'<p class="prs-bcap"><span>{c.esc(b.get("이름", ""))}</span>'
        f'<b>{total:g}<small> ms</small></b></p>'
        f'<div class="prs-bbar">{segs}</div>'
        f'<div class="prs-bnotes">{notes}</div>'
        f'<div class="prs-bcells">{cells}</div>'
        f'<p class="prs-bfoot"><span><i></i>{c.esc(per["label"])} 한 칸 · '
        f'{per["ms"]:g} ms</span><b>{count_s}<small> 칸</small></b></p>'
        + (f'<p class="prs-src">{clock}{c.esc(b.get("출처", ""))}</p>'
           if b.get("출처") or clock else "")
        + '</div>')


def _notes(data: dict) -> list[tuple[str, str]]:
    """What closes the speaker essay: the paper figure's caption, the authors'
    clip's caption and where it is published, and the `why` of every figure
    the slide draws for itself.

    The caption says what the figure shows, panel by panel; the slide already
    carries the one line of what to see in it, so the caption is the
    presenter's to walk the room through rather than a paragraph under the
    figure set too small to read. The `why` is the answer to "is that in the
    paper?" — which of the paper's figures covers this ground and what the
    drawing strips out — and that answer is the presenter's to give when
    asked.
    """
    out = []
    fig = data.get("figure")
    if isinstance(fig, dict) and str(fig.get("caption", "")).strip():
        out.append(("그림", str(fig["caption"])))
    vid = data.get("video")
    if isinstance(vid, dict):
        out.append(("영상", f'{vid["caption"]} — {vid["source"]}, {vid["page"]}'))
    out += [("그린 그림", str(data[f]["why"]))
            for f in ("diagram", "timing", "chart", "heat") + charts.LINEAGE
            if isinstance(data.get(f), dict) and str(data[f].get("why", "")).strip()]
    return out


def _script(text: str, of: str, notes: list[tuple[str, str]] | None = None) -> str:
    """The speaker essay, right after the slide it belongs to.

    Without a script every essay sits under its slide, which is the talk read
    as a document. While the tab is browsed it stays hidden until 노트 asks for
    it — inline under the frame, or in the presenter's second window once the
    talk is on a stage. It carries no fact the slide does not show — a number
    worth saying is on the slide, in a figure, an item's second register or
    the ribbon, and the essay points at it. It closes on the paper figure's
    caption and the `why` of every figure the slide drew for itself (`_notes`).

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
    paras += "".join(f'<p class="prs-drawwhy"><b>{c.esc(k)}</b> — {inline(w)}</p>'
                     for k, w in notes or [])
    return (f'<div class="prs-script" data-for="{c.esc(of)}">'
            f'<h4>말할 것</h4>{paras}</div>')
