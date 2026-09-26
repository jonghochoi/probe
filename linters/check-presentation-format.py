#!/usr/bin/env python3
"""Check `presentation/<arxiv-id>.md` against the contract in `presentation/AUTHORING.md`.

The build validates what it needs in order to publish a talk — front matter,
the act and type header, the fence a type is drawn from. This lint is the other
half: the authoring rules, the ones a presentation can break while still rendering
perfectly. A slide dump publishes cleanly; it just is not a talk.

The rules it checks, each naming the section it comes from:

  SPINE        (§1-1)  two acts at least, and the turn among them. A
                       presentation whose slides all sit in one act is a
                       table of contents, which is what the paper already is.
  TURN         (§1-1)  exactly one `statement` — the tinted turn frame — and
                       it sits in 轉. A talk with none, or with three, has no
                       turn.
  VISUAL       (§1-3)  every slide but the cover carries one piece of visual
                       evidence, and at most one slide in the talk is text
                       alone. A talk of text slides is a document read aloud.
  RESULT       (§1-3)  at least one 結 slide shows a result — the paper's
                       figure or a chart of its numbers.
  REGISTER     (§2)    panel items carry a second layer — the number or
                       source that makes the claim checkable. Not demanded
                       item by item: the paper does not always supply one, and
                       an invented `n` is worse than a bare line. What is
                       demanded is that most of them do, because a
                       presentation where none does is a list of bullets.
  MATH         (§2)    no KaTeX. A slide is read from across a room, so its
                       symbols are literal text.
  WORDS        (§3-1)  the slide's visible text stays inside the word budget,
                       and a panel item's second register inside a few words
                       of its own, so the evidence never competes with the
                       claims for the budget.
  CLOSE        (§3-2)  every panel column closes on `foot`.
  DRAWN        (§4-2)  a created figure states `why` — which of the paper's
                       own figures covers this ground, and what this one
                       leaves out — and a figure of the paper's numbers or
                       sentences (`probe-chart`, `probe-heat`,
                       `probe-contrast`, `probe-inheritance`) also states
                       `source` and `omitted`. `--omitted` prints the left-out
                       rows under each headline for the self-check.
  ILLUSTRATIVE (§4-1)  every strip and worker drawing (`probe-heat`,
                       `probe-timing`) says what it chose — `illustrative`, or
                       `false` when every parameter is the paper's own.
  CLOCK        (§4-8)  a drawing of time (`probe-timing`, `probe-budget`)
                       names its `clock`, and every drawing of time in one act
                       is on one clock.
  LINEAGE      (§4-9)  a `contrast` in 承 and an `inheritance` in 結, one of
                       each, unless the front matter's `lineage_drop` names
                       the one left out and why. A prior is one work, this
                       paper is dated from its own arXiv id, and the
                       inheritance's additions do not restate the contrast's
                       contribution column.
  SPEAK        (§6)    every slide carries its speaker essay. A slide with
                       none is a slide nobody worked out how to present.
  SOURCE       (§1-5)  no `context/` material. A `D#` is a claim about our own
                       decisions, which is the one thing on a slide a listener
                       cannot check against the paper.
  MOTION       (§8)    a clip rides beside the paper's own figure, is a file
                       the authors publish — never an embedded player — and
                       says where; a stepped figure's essay says when to step;
                       and no more than three slides move.

It re-parses the source rather than importing `site/builder/presentations.py`, for the
same reason `check-decision-refs.py` re-parses the Decision Log: this has to run
with no build dependencies installed.

Usage (repo root):
    python3 linters/check-presentation-format.py [PATH ...]
    python3 linters/check-presentation-format.py --words [PATH ...]   # per-slide counts
    python3 linters/check-presentation-format.py --omitted [PATH ...] # headline vs left-out rows
    python3 linters/check-presentation-format.py --numbers EXTRACT [PATH ...]

`--numbers` reads EXTRACT — the paper's text and tables as
`python3 -m builder.arxiv <id> --tables` and `--section` print them — and lists,
under each slide, every numeral on the slide, in its fences or in its script
that the extract does not contain verbatim. It reports and never fails: a gap
or a ratio is arithmetic on printed numbers and legitimately absent, so each
line is for the self-check to justify or fix.

No PATH -> scan `presentation/*.md` (`AUTHORING.md` excluded — it is the contract).

Exit codes: 0 = clean / 1 = violation(s) found.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_ACTS = ("起", "承", "轉", "結")
_TURN = "轉"
_CLOSE_ACT = "結"
_TYPES = ("cover", "statement", "evidence", "split", "versus", "ledger",
          "budget", "timing", "contrast", "inheritance", "chart", "heat")
_PANEL_FENCES = ("versus", "ledger")

# The shapes that carry no visual of their own. A statement becomes a visual
# slide by carrying one — a drawing, a chart of the paper's numbers, or the
# paper's own figure.
_TEXT_TYPES = ("ledger", "versus", "statement")
_STATEMENT_VISUALS = ("diagram", "timing", "chart", "heat", "figure")
_TEXT_MAX = 1

# The tinted turn frame: one per talk, on the turn.
_STATEMENT = "statement"

# What shows a result on a 結 slide.
_RESULT_TYPES = ("evidence", "split", "chart")

# The drawn figures, all of which state `why`; the ones drawn from the
# paper's numbers or its sentences about its priors also state `source` and
# `omitted`.
_LINEAGE = ("contrast", "inheritance")
_DRAWN = ("diagram", "timing", "chart", "heat") + _LINEAGE
_SOURCED = ("chart", "heat") + _LINEAGE

# §4-9. Each lineage figure answers its own question, so it sits in the act
# that asks it. A talk may go without one of them, and says which and why in
# its front matter (`lineage_drop: contrast — <why>`), where the storyboard's
# reason is kept.
_LINEAGE_ACT = {"contrast": "承", "inheritance": "結"}
_DROP = re.compile(r"^lineage_drop:\s*(\S+)\s+—\s+(\S.*)$", re.M)

# The drawings of time, which name the clock they are on.
_CLOCKED = ("timing", "budget")

# The drawings that choose a setting to draw at, and must say whether they did.
_CHOOSING = ("heat", "timing")

# A numeral as the room reads it: digits with an optional decimal part. Signs,
# units and thousands separators are not part of it, so `−3.5` is looked up
# as `3.5` and `1.5×` as `1.5`.
_NUMERAL = re.compile(r"(?<![\d.])\d+(?:\.\d+)?(?![\d])")

# §8. A clip is a file the authors' page serves and rides beside the figure it
# falls back to; an embedded player takes the keyboard the deck runs on. A
# stepped figure's essay marks its states with ↓. Motion is the exception.
_CLIP = re.compile(r"^https://[^\s/]+/\S+\.(?:mp4|webm)(?:\?\S*)?$", re.I)
_EMBED = re.compile(r"(?:youtube\.com|youtu\.be|vimeo\.com|/embed/|<iframe)", re.I)
_VIDEO_TYPES = ("evidence", "split")
_CLIPS_MAX = 2
_STEPPED = ("chart", "heat")
_MOTION_MAX = 3

_HEAD = re.compile(r"^## \[(\S+) · (\w+)\]\s*(.+)$", re.M)
_FENCE = re.compile(r"^```probe-([a-z]+)\n(.*?)\n```", re.M | re.S)

# The share of panel items that must carry a second register. Not one — a
# column where a single line happens to have a number is the defect this rule
# exists to catch. Not all — the paper does not always supply one.
_REGISTER_FLOOR = 0.6

# The word budget (§3-1): visible words per slide, counted as space-separated
# tokens — 어절 for Korean. A slide is looked at for as long as it is talked
# over, and at this count the room has finished reading before the presenter
# has finished the first sentence.
_WORD_BUDGET = 40
# The one text slide a talk may have (§1-3) has no visual to carry its point,
# so its claims are the evidence — a two-column ledger's heads, items and
# feet. Their second registers are not counted here; each is held to
# `_REGISTER_WORDS` instead, so an item that carries its number costs the
# budget nothing more than one that does not.
_TEXT_BUDGET = 50
_REGISTER_WORDS = 6

# Math on a slide is read from across a room, where a rendered fraction is a
# smudge. The presentation writes its symbols as literal text (`d₀`, `W₀`, `tanh(α)`),
# so the GitHub-KaTeX dialect the rewrites use is a slip rather than a choice.
_MATH = re.compile(r"\$`|`\$|\$\$")

# The Decision-Log citation form (`check-decision-refs.py` owns the vocabulary).
# Here it is not validated but refused: a presentation argues from the paper alone.
_DREF = re.compile(r"(?<![A-Za-z0-9_])D\d[A-Z]{2}(?![A-Za-z0-9])")

# Tokens that are punctuation or a line-break marker rather than a word.
_NOT_A_WORD = re.compile(r"^[\W_]+$")


def _slides(text: str) -> list[tuple[int, str, str, str, str]]:
    """(line, act, type, title, chunk) per slide."""
    out = []
    hits = list(_HEAD.finditer(text))
    for i, m in enumerate(hits):
        end = hits[i + 1].start() if i + 1 < len(hits) else len(text)
        line = text.count("\n", 0, m.start()) + 1
        out.append((line, m.group(1), m.group(2), m.group(3),
                    text[m.end():end]))
    return out


def _fences(chunk: str) -> dict[str, str]:
    return {m.group(1): m.group(2) for m in _FENCE.finditer(chunk)}


def _json(raw: str):
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _visible(title: str, chunk: str, fences: dict[str, str]) -> list[str]:
    """Every string the slide puts in front of the room.

    Counted: the header, the prose line and bullets, ribbon cells, panel
    heads, items and feet, a diagram's boxes and notes, a budget's labels and
    notes, a timing's row names, notes, marks and brace, a chart's one
    annotation (`note` or `group`, with its `sub`), a contrast's column heads
    and its `key_note`, and an inheritance's edge phrases, additions and open
    question — each is a sentence the room reads.

    Not counted: the script (the room hears it); `source`, `illustrative`,
    `clock` and `why` (provenance, set as one line or kept in the essay); a
    paper figure's `caption` (it closes the essay and is not on the slide); a
    panel item's `n` (the second register, held to its own few words); a
    chart's or a strip's own labels and values — axis and tick labels, series
    and row names, row notes — which are the data; and a lineage figure's
    names, dates, sections and a cell's `n`, which say who, when and where
    rather than what.
    """
    out = [title]
    prose = _FENCE.sub("", chunk)
    out += [l[2:] if l.startswith("- ") else l
            for l in prose.split("\n") if l.strip()]
    for kind, raw in fences.items():
        data = _json(raw) if kind != "script" else None
        if data is None:
            continue
        if kind == "chart" and isinstance(data, dict):
            for key in ("note", "group"):
                ann = data.get(key)
                if isinstance(ann, dict):
                    out += [str(ann.get("text", "")), str(ann.get("sub", ""))]
        elif kind == "facts" and isinstance(data, list):
            out += [f"{c.get('값', '')} {c.get('라벨', '')}" for c in data
                    if isinstance(c, dict)]
        elif kind in _PANEL_FENCES:
            for col in data.values():
                if not isinstance(col, dict):
                    continue
                out += [str(col.get("head", "")), str(col.get("foot", ""))]
                for item in col.get("lines", []):
                    out += ([item] if isinstance(item, str)
                            else [str(item.get("t", ""))])
        elif kind == "diagram":
            boxes = list(data.get("before", {}).get("chain", []))
            after = data.get("after", {})
            boxes += [after.get(k, {}) for k in ("slow", "fast", "join", "out")]
            for b in boxes:
                if isinstance(b, dict):
                    out += [str(b.get(k, "")) for k in ("box", "note", "loop")]
        elif kind == "budget":
            out += [str(p.get(k, "")) for p in data.get("항목", [])
                    for k in ("label", "note")]
        elif kind == "timing":
            for row in data.get("줄", []):
                out += [str(row.get("name", "")), str(row.get("note", "")),
                        str(row.get("mark", {}).get("label", ""))]
            out.append(str((data.get("brace") or {}).get("label", "")))
        elif kind == "contrast" and isinstance(data, dict):
            out += [str(h) for h in data.get("cols", [])]
            out.append(str(data.get("key_note", "")))
        elif kind == "inheritance" and isinstance(data, dict):
            out += [str(ln.get("gave", "")) for ln in data.get("lines", [])
                    if isinstance(ln, dict)]
            out += [str(a) for a in (data.get("me") or {}).get("adds", [])]
            out.append(str((data.get("open") or {}).get("text", "")))
    return out


def _words(strings: list[str]) -> int:
    n = 0
    for s in strings:
        s = s.replace("**", " ").replace(" / ", " ")
        n += sum(1 for t in s.split() if not _NOT_A_WORD.match(t))
    return n


def _textual(kind: str, fences: dict[str, str]) -> bool:
    return kind in _TEXT_TYPES and not (
        kind == "statement" and any(f in fences for f in _STATEMENT_VISUALS))


def _budget(kind: str, fences: dict[str, str]) -> int:
    return _TEXT_BUDGET if _textual(kind, fences) else _WORD_BUDGET


def slide_words(path: str) -> list[tuple[str, int, int]]:
    text = open(path, encoding="utf-8").read()
    out = []
    for _, _, kind, title, chunk in _slides(text):
        fences = _fences(chunk)
        out.append((title, _words(_visible(title, chunk, fences)),
                    _budget(kind, fences)))
    return out


def slide_omitted(path: str) -> list[tuple[str, str, list[str]]]:
    """(headline, figure, omitted rows) for every figure of the paper's numbers
    or sentences — what the self-check reads to ask whether a headline still
    holds against the rows its figure left out."""
    text = open(path, encoding="utf-8").read()
    out = []
    for _, _, _, title, chunk in _slides(text):
        fences = _fences(chunk)
        for kind in _SOURCED:
            data = _json(fences[kind]) if kind in fences else None
            if isinstance(data, dict):
                om = data.get("omitted")
                out.append((title, kind, om if isinstance(om, list) else []))
    return out


# Fence fields that are addresses or instructions to the build rather than
# text anyone reads or hears, and a lineage figure's dates, which come from
# arXiv and the bibliography rather than the paper's text: their digits are
# not claims about the paper.
_NOT_CLAIMS = ("url", "src", "page", "id", "focus", "crop", "cells", "at",
               "span_ms", "from", "to", "rows", "steps", "min", "max", "step",
               "decimals", "cols", "shift", "into", "place", "side", "regions",
               "mark", "shared", "feeds", "band", "brace", "dots", "when", "key")


def _claims(data) -> list[str]:
    """The strings and values of a fence that are claims about the paper —
    every label, note and plotted value, but not a URL, a layout position or
    a cell the drawing computed."""
    if isinstance(data, dict):
        return [x for k, v in data.items() if k not in _NOT_CLAIMS
                for x in _claims(v)]
    if isinstance(data, list):
        return [x for v in data for x in _claims(v)]
    if isinstance(data, bool) or data is None:
        return []
    return [str(data)]


def _canon(num: str) -> set[str]:
    """The spellings a printed number can take: `70` for `70.0`, `.45` for
    `0.45`, and a percentage for a fraction (`0.45` → `45`)."""
    out = {num}
    if "." in num:
        out.add(num.rstrip("0").rstrip("."))
        if num.startswith("0."):
            out.add(num[1:])
            frac = num[2:]
            out.add(frac.lstrip("0") or "0")
            if len(frac) > 2:
                out.add(f"{frac[:2].lstrip('0') or '0'}.{frac[2:]}")
    return out


def slide_numbers(path: str, extract: str) -> list[tuple[str, list[str]]]:
    """(headline, numerals absent from the extract) per slide — the
    mechanical half of "every number is one the paper prints"."""
    printed = {c for n in set(_NUMERAL.findall(extract)) for c in _canon(n)}
    text = open(path, encoding="utf-8").read()
    out = []
    for _, _, _, title, chunk in _slides(text):
        fences = _fences(chunk)
        said = [title] + [l for l in _FENCE.sub("", chunk).split("\n") if l.strip()]
        for kind, raw in fences.items():
            if kind == "script":
                said.append(raw)
                continue
            data = _json(raw)
            said += _claims(data) if data is not None else []
        missing = []
        for s in said:
            for num in _NUMERAL.findall(s):
                if len(num) == 1 or num in missing:
                    continue
                if not (_canon(num) & printed):
                    missing.append(num)
        out.append((title, missing))
    return out


def _motion(line: int, where: str, kind: str,
            fences: dict[str, str]) -> tuple[list[tuple[int, str]], bool]:
    """§8 — the rules a moving slide can break while playing perfectly.
    Returns the findings and whether the slide moves."""
    found: list[tuple[int, str]] = []
    moves = False
    if "video" in fences:
        moves = True
        vid = _json(fences["video"])
        if not isinstance(vid, dict):
            return [(line, f"{where}: ```probe-video is not a JSON object")], True
        if kind not in _VIDEO_TYPES or "figure" not in fences:
            found.append((line, f"MOTION (§8-1-1): {where} carries a clip with no "
                                f"paper figure beside it — a clip rides on an "
                                f"evidence or split slide, next to the "
                                f"```probe-figure it falls back to"))
        gone = [k for k in ("page", "caption", "source") if not str(vid.get(k, "")).strip()]
        if gone:
            found.append((line, f"MOTION (§8-1-2): {where}'s clip has no "
                                f"`{'`, `'.join(gone)}` — the room is owed where "
                                f"the authors publish it"))
        clips = vid.get("clips") if isinstance(vid.get("clips"), list) else []
        if not 1 <= len(clips) <= _CLIPS_MAX:
            found.append((line, f"MOTION (§8-1-3): {where} carries {len(clips)} "
                                f"clips — one, or a pair"))
        for clip in clips:
            src = str(clip.get("src", "")) if isinstance(clip, dict) else ""
            if _EMBED.search(src):
                found.append((line, f"MOTION (§8-1-2): {where}: {src!r} is an "
                                    f"embedded player — it takes the deck's "
                                    f"keyboard and has no figure to fall back "
                                    f"to. Name it in the essay instead"))
            elif not _CLIP.match(src):
                found.append((line, f"MOTION (§8-1-2): {where}: {src!r} is not an "
                                    f"https .mp4 or .webm the authors' page serves"))
            if len(clips) > 1 and not (isinstance(clip, dict)
                                       and str(clip.get("label", "")).strip()):
                found.append((line, f"MOTION (§8-1-3): {where}: a clip in a pair "
                                    f"has no `label`"))
    for fence in _STEPPED:
        data = _json(fences[fence]) if fence in fences else None
        if isinstance(data, dict) and data.get("steps"):
            moves = True
            if "↓" not in fences.get("script", ""):
                found.append((line, f"MOTION (§8-2-3): {where} steps, but its essay "
                                    f"never says when — mark each state where it "
                                    f"falls (`↓ — (b).`)"))
    return found, moves


def _flat(text: str) -> str:
    return re.sub(r"[\s/*·,]+", "", text)


def _lineage_nodes(line: int, where: str, kind: str, data: dict,
                   paper: str) -> list[tuple[int, str]]:
    """§4-9 on one lineage figure — the rules its build cannot see: a prior
    is one work, and this paper is dated from its own id."""
    found = []
    if kind == "contrast":
        nodes = [r for r in data.get("rows", []) if isinstance(r, dict)]
        mine = [r for r in nodes if r.get("us")]
    else:
        nodes = [ln for ln in data.get("lines", []) if isinstance(ln, dict)]
        mine = [data["me"]] if isinstance(data.get("me"), dict) else []
    for node in nodes:
        if " · " in str(node.get("name", "")) and node not in mine:
            found.append((line, f"LINEAGE (§4-9): {where}: {node['name']!r} joins "
                                f"several works — a prior is one work, the first "
                                f"the paper names in that citation, and the rest "
                                f"go into `omitted`"))
    month = f"20{paper[:2]}.{paper[2:4]}" if re.match(r"^\d{4}\.\d{4,5}$", paper) else None
    for node in mine:
        if month and str(node.get("when", "")) != month:
            found.append((line, f"LINEAGE (§4-9): {where}: this paper is dated "
                                f"{node.get('when', '')!r} — its own arXiv id "
                                f"{paper} was first posted {month}"))
    return found


def _lineage_talk(text: str, lineage: dict[str, list[tuple[int, str, dict]]]
                  ) -> list[tuple[int, str]]:
    """§4-9 across the talk: a contrast in 承 and an inheritance in 結, one of
    each, unless the front matter drops one and says why; and the two do not
    say the same thing."""
    found = []
    front = text.split("\n---", 1)[0] if text.startswith("---") else ""
    drops = _DROP.findall(front)
    named = [k for k, _ in drops]
    if "lineage_drop:" in front and not drops:
        found.append((1, "LINEAGE (§4-9): `lineage_drop` is `<contrast|inheritance> "
                         "— <why>`, the storyboard's reason for going without it"))
    for kind in named:
        if kind not in _LINEAGE_ACT:
            found.append((1, f"LINEAGE (§4-9): `lineage_drop` names {kind!r} — "
                             f"one of {', '.join(_LINEAGE_ACT)}"))
        elif kind in lineage:
            found.append((1, f"LINEAGE (§4-9): `lineage_drop` names {kind}, but the "
                             f"talk carries one — drop the slide or the line"))
    if len([k for k in named if k in _LINEAGE_ACT]) >= len(_LINEAGE_ACT):
        found.append((1, "LINEAGE (§4-9): `lineage_drop` drops both figures — a "
                         "talk may go without one of them, never both"))
    for kind, act in _LINEAGE_ACT.items():
        slides = lineage.get(kind, [])
        if not slides and kind not in named:
            found.append((1, f"LINEAGE (§4-9): no `{kind}` slide — every talk "
                             f"places its paper with a contrast in 承 and an "
                             f"inheritance in 結. Draw it, or name it in "
                             f"`lineage_drop` with the storyboard's reason"))
        if len(slides) > 1:
            found.append((slides[1][0], f"LINEAGE (§4-9): {len(slides)} `{kind}` "
                                        f"slides — a talk places its paper once "
                                        f"each way"))
        for line, at, _ in slides:
            if at != act:
                found.append((line, f"LINEAGE (§4-9): the `{kind}` slide sits in "
                                    f"{at} — it answers {act}'s question and "
                                    f"belongs there"))
    con = lineage.get("contrast", [])
    inh = lineage.get("inheritance", [])
    if con and inh:
        data = con[0][2]
        cols, key = data.get("cols", []), data.get("key")
        if isinstance(key, int) and not isinstance(key, bool) and 0 <= key < len(cols):
            head = _flat(str(cols[key]))
            for a in (inh[0][2].get("me") or {}).get("adds", []):
                if _flat(str(a)) == head:
                    found.append((inh[0][0], f"LINEAGE (§4-9): the inheritance adds "
                                             f"{a!r}, the contrast's contribution "
                                             f"column word for word — the contrast "
                                             f"shows the gap, the inheritance the "
                                             f"mechanism that fills it"))
    return found


def check_file(path: str) -> list[tuple[int, str]]:
    text = open(path, encoding="utf-8").read()
    found: list[tuple[int, str]] = []
    slides = _slides(text)
    if not slides:
        return [(1, "SPINE (§1-1): no slides — a presentation is `## [<act> · <type>] <title>` "
                    "and the fences under it")]

    acts = {s[1] for s in slides}
    reg_total = reg_noted = 0
    text_only: list[str] = []
    shows_result = False
    statements: list[tuple[int, str, str]] = []
    clocks: dict[str, dict[str, str]] = {}
    moving: list[str] = []
    lineage: dict[str, list[tuple[int, str, dict]]] = {}
    paper = os.path.splitext(os.path.basename(path))[0]

    for line, act, kind, title, chunk in slides:
        where = f"slide '{title}'"
        if act not in _ACTS:
            found.append((line, f"SPINE (§1-1): {where} declares act {act!r} — "
                                f"one of {' '.join(_ACTS)}"))
        if kind not in _TYPES:
            found.append((line, f"SPINE (§1-1): {where} declares type {kind!r} — "
                                f"one of {' '.join(_TYPES)}"))
        fences = _fences(chunk)

        # The header is part of the slide, so both refusals below read it too.
        whole = f"{title}\n{chunk}"

        hits = sorted(set(_DREF.findall(whole)))
        if hits:
            found.append((line, f"SOURCE (§1-5): {where} cites {', '.join(hits)} — "
                                f"`context/` is not a source for this track. That "
                                f"argument belongs to the rewrite's act 4, which "
                                f"is one link away"))

        if _MATH.search(whole):
            found.append((line, f"MATH (§2): {where} carries KaTeX math — a slide is read "
                                f"from across a room, so its symbols are written "
                                f"as literal text (d₀, W₀, tanh(α))"))

        if _textual(kind, fences):
            text_only.append(title)
        if kind == _STATEMENT:
            statements.append((line, act, title))
        if act == _CLOSE_ACT and kind in _RESULT_TYPES:
            shows_result = True

        words = _words(_visible(title, chunk, fences))
        budget = _budget(kind, fences)
        if words > budget:
            found.append((line, f"WORDS (§3-1): {where} puts {words} words in front "
                                f"of the room — the budget is {budget}. Cut to "
                                f"the assertion and its evidence; the rest belongs "
                                f"in the script"))

        if "script" not in fences:
            found.append((line, f"SPEAK (§6): {where} has no ```probe-script — "
                                f"a slide with no speaker essay is one nobody "
                                f"worked out how to present"))
        for drawn in _DRAWN:
            if drawn not in fences:
                continue
            data = _json(fences[drawn])
            if not isinstance(data, dict):
                found.append((line, f"{where}: ```probe-{drawn} is not a JSON object"))
                continue
            if not str(data.get("why", "")).strip():
                found.append((line, f"DRAWN (§4-2): {where} draws a {drawn} with "
                                    f"no `why` — name the paper's own figure that "
                                    f"covers this ground, or say it has none, and "
                                    f"what this one leaves out"))
            if drawn in _SOURCED and not str(data.get("source", "")).strip():
                found.append((line, f"DRAWN (§4-6, §4-9): {where} draws from the "
                                    f"paper with no `source` — name the table, "
                                    f"equation or section where every value or "
                                    f"phrase is printed"))
            if drawn in _CHOOSING and not (
                    data.get("illustrative") is False
                    or str(data.get("illustrative") or "").strip()):
                found.append((line, f"ILLUSTRATIVE (§4-1): {where} draws a "
                                    f"{drawn} with no `illustrative` — name the "
                                    f"setting it was drawn at, or set `false` "
                                    f"when every parameter is the paper's own"))
            if drawn in _SOURCED and not isinstance(data.get("omitted"), list):
                found.append((line, f"DRAWN (§4-6, §4-9): {where} draws from the "
                                    f"paper with no `omitted` — list the source rows "
                                    f"or cited works the figure leaves out, or `[]` "
                                    f"if it leaves out none. The headline is checked "
                                    f"against them"))
            if drawn in _LINEAGE:
                found += _lineage_nodes(line, where, drawn, data, paper)
                lineage.setdefault(drawn, []).append((line, act, data))

        motion, moves = _motion(line, where, kind, fences)
        found += motion
        if moves:
            moving.append(title)

        for clocked in _CLOCKED:
            if clocked not in fences:
                continue
            data = _json(fences[clocked])
            if not isinstance(data, dict):
                continue
            clock = str(data.get("clock", "")).strip()
            if not clock:
                found.append((line, f"CLOCK (§4-8): {where} draws time with no "
                                    f"`clock` — name the hardware and rate its "
                                    f"times were measured on"))
            else:
                clocks.setdefault(act, {}).setdefault(clock, title)

        for fence in _PANEL_FENCES:
            if fence not in fences:
                continue
            data = _json(fences[fence])
            if data is None:
                found.append((line, f"{where}: ```probe-{fence} is not JSON"))
                continue
            for key, col in data.items():
                if not isinstance(col, dict):
                    continue
                if not str(col.get("foot", "")).strip():
                    found.append((line, f"CLOSE (§3-2): {where}, column {key!r} has "
                                        f"no `foot` — the column closes on its own "
                                        f"one-line conclusion, which is what holds "
                                        f"the bottom edge"))
                for item in col.get("lines", []):
                    reg_total += 1
                    if isinstance(item, dict) and str(item.get("n", "")).strip():
                        reg_noted += 1
                        n_words = _words([str(item["n"])])
                        if n_words > _REGISTER_WORDS:
                            found.append((line, f"REGISTER (§2): {where}, item "
                                                f"{item.get('t', '')!r} carries a "
                                                f"{n_words}-word `n` — the second "
                                                f"register is a number and its "
                                                f"condition, at most "
                                                f"{_REGISTER_WORDS} words"))

    if _TURN not in acts:
        found.append((1, f"SPINE (§1-1): no {_TURN} slide — the turn is what the "
                         f"presentation exists to land, and a presentation without one retells "
                         f"the paper in its own order"))
    elif len(acts) < 2:
        found.append((1, "SPINE (§1-1): every slide sits in one act — a presentation with "
                         "no beats is a table of contents, which is what the paper "
                         "already is"))

    if len(statements) != 1:
        found.append((statements[1][0] if len(statements) > 1 else 1,
                      f"TURN (§1-1): {len(statements)} `statement` slides — a talk "
                      f"has exactly one tinted turn frame, and it carries the turn"))
    for line, act, title in statements:
        if act != _TURN:
            found.append((line, f"TURN (§1-1): slide '{title}' is the tinted turn "
                                f"`statement` in {act} — it belongs to {_TURN}, the "
                                f"sentence the talk exists for"))
    for act, seen in clocks.items():
        if len(seen) > 1:
            found.append((1, f"CLOCK (§4-8): act {act} draws time on "
                             f"{len(seen)} clocks — "
                             + "; ".join(f"{c!r} ({t})" for c, t in seen.items())
                             + ". Redraw on one clock, or move the other to "
                               "the act it belongs to"))

    if len(text_only) > _TEXT_MAX:
        found.append((1, f"VISUAL (§1-3): {len(text_only)} slides carry no visual "
                         f"evidence ({'; '.join(text_only)}) — at most {_TEXT_MAX}. "
                         f"Show the paper's figure, plot its numbers, or draw what "
                         f"it states"))
    if not shows_result:
        found.append((1, f"RESULT (§1-3): no {_CLOSE_ACT} slide shows a result — "
                         f"the paper's figure or a `chart` of its numbers. A talk "
                         f"that argues the turn and never shows it working has "
                         f"skipped its evidence"))

    found += _lineage_talk(text, lineage)

    if len(moving) > _MOTION_MAX:
        found.append((1, f"MOTION (§8-3): {len(moving)} slides move "
                         f"({'; '.join(moving)}) — at most {_MOTION_MAX}. A talk "
                         f"where half the slides move is a demo, and the still "
                         f"slides beside it stop reading as evidence"))

    if reg_total and reg_noted / reg_total < _REGISTER_FLOOR:
        found.append((1, f"REGISTER (§2): {reg_noted} of {reg_total} panel items "
                         f"carry a second register, under the {_REGISTER_FLOOR:.0%} "
                         f"floor. A claim with the number or source under it is "
                         f"evidence; a claim alone is a bullet"))
    return sorted(found)


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    words = "--words" in args
    omitted = "--omitted" in args
    extract = None
    if "--numbers" in args:
        k = args.index("--numbers")
        if k + 1 >= len(args):
            print("[check-presentation-format] --numbers takes the extract's path")
            return 1
        extract = open(args[k + 1], encoding="utf-8").read()
        del args[k:k + 2]
    args = [a for a in args if a not in ("--words", "--omitted")]
    docs = args or sorted(
        os.path.relpath(p, _REPO_ROOT)
        for p in glob.glob(os.path.join(_REPO_ROOT, "presentation", "*.md"))
        if os.path.basename(p) != "AUTHORING.md"
    )
    if not docs:
        print("[check-presentation-format] no presentations to check")
        return 0

    if extract is not None:
        for doc in docs:
            for i, (title, missing) in enumerate(slide_numbers(
                    os.path.join(_REPO_ROOT, doc), extract)):
                if missing:
                    print(f"{doc} s{i + 1:02d}  {title}")
                    print(f"    not in the extract: {', '.join(missing)}")
        return 0

    if omitted:
        for doc in docs:
            for title, kind, rows in slide_omitted(os.path.join(_REPO_ROOT, doc)):
                print(f"{doc}  [{kind}] {title}")
                for r in rows or ["(none left out)"]:
                    print(f"    - {r}")
        return 0

    if words:
        for doc in docs:
            for i, (title, n, cap) in enumerate(slide_words(os.path.join(_REPO_ROOT, doc))):
                flag = "  over" if n > cap else ""
                print(f"{doc} s{i + 1:02d} {n:3d}/{cap}{flag}  {title}")
        return 0

    total = 0
    for doc in docs:
        for line, msg in check_file(os.path.join(_REPO_ROOT, doc)):
            total += 1
            print(f"{doc}:{line}: {msg}")

    if total:
        print(f"\n[check-presentation-format] {total} violation(s) across {len(docs)} presentation(s)")
        return 1
    print(f"[check-presentation-format] clean — {len(docs)} presentation(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
