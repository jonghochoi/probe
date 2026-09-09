#!/usr/bin/env python3
"""Check `presentation/<arxiv-id>.md` against the contract in `presentation/AUTHORING.md`.

The build validates what it needs in order to publish a talk — front matter,
the act and type header, the fence a type is drawn from. This lint is the other
half: the authoring rules, the ones a presentation can break while still rendering
perfectly. A slide dump publishes cleanly; it just is not a talk.

The six it checks, each naming the section it comes from:

  SPINE     (§1)  two acts at least, and the turn among them. A presentation whose
                  slides all sit in one act is a table of contents, which is
                  what the paper already is.
  REGISTER  (§2)  panel items carry a second layer — the number or source that
                  makes the claim checkable. Not demanded item by item: the
                  paper does not always supply one, and an invented `n` is
                  worse than a bare line. What is demanded is that most of them
                  do, because a presentation where none does was written before the
                  rule.
  CLOSE     (§3)  every panel column closes on `foot`, and every slide but the
                  cover closes on the evidence ribbon.
  DRAWN     (§4)  a created figure states `why` — which of the paper's own
                  figures covers this ground, and what this one leaves out.
  SPEAK     (§6)  every slide carries its speaker essay. A slide with none is
                  a slide nobody worked out how to present.
  SOURCE    (§0)  no `context/` material. A `D#` is a claim about our own
                  decisions, which is the one thing on a slide a listener
                  cannot check against the paper.

It re-parses the source rather than importing `site/builder/presentations.py`, for the
same reason `check-decision-refs.py` re-parses the Decision Log: this has to run
with no build dependencies installed.

Usage (repo root):
    python3 linters/check-presentation-format.py [PATH ...]

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
_TYPES = ("cover", "statement", "evidence", "split", "versus", "ledger",
          "budget", "timing", "lineage")
_PANEL_FENCES = ("versus", "ledger")

_HEAD = re.compile(r"^## \[(\S+) · (\w+)\]\s*(.+)$", re.M)
_FENCE = re.compile(r"^```probe-([a-z]+)\n(.*?)\n```", re.M | re.S)

# The share of panel items that must carry a second register. Not one — a
# column where a single line happens to have a number is the defect this rule
# exists to catch. Not all — the paper does not always supply one.
_REGISTER_FLOOR = 0.6

# Math on a slide is read from across a room, where a rendered fraction is a
# smudge. The presentation writes its symbols as literal text (`d₀`, `W₀`, `tanh(α)`),
# so the GitHub-KaTeX dialect the rewrites use is a slip rather than a choice.
_MATH = re.compile(r"\$`|`\$|\$\$")

# The Decision-Log citation form (`check-decision-refs.py` owns the vocabulary).
# Here it is not validated but refused: a presentation argues from the paper alone.
_DREF = re.compile(r"(?<![A-Za-z0-9_])D\d[A-Z]{2}(?![A-Za-z0-9])")


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


def check_file(path: str) -> list[tuple[int, str]]:
    text = open(path, encoding="utf-8").read()
    found: list[tuple[int, str]] = []
    slides = _slides(text)
    if not slides:
        return [(1, "SPINE (§1): no slides — a presentation is `## [<act> · <type>] <title>` "
                    "and the fences under it")]

    acts = {s[1] for s in slides}
    reg_total = reg_noted = 0

    for line, act, kind, title, chunk in slides:
        where = f"slide '{title}'"
        if act not in _ACTS:
            found.append((line, f"SPINE (§1): {where} declares act {act!r} — "
                                f"one of {' '.join(_ACTS)}"))
        if kind not in _TYPES:
            found.append((line, f"SPINE (§1): {where} declares type {kind!r} — "
                                f"one of {' '.join(_TYPES)}"))
        fences = _fences(chunk)

        # The header is part of the slide, so both refusals below read it too.
        whole = f"{title}\n{chunk}"

        hits = sorted(set(_DREF.findall(whole)))
        if hits:
            found.append((line, f"SOURCE (§0): {where} cites {', '.join(hits)} — "
                                f"`context/` is not a source for this track. That "
                                f"argument belongs to the rewrite's act 4, which "
                                f"is one link away"))

        if _MATH.search(whole):
            found.append((line, f"§2: {where} carries KaTeX math — a slide is read "
                                f"from across a room, so its symbols are written "
                                f"as literal text (d₀, W₀, tanh(α))"))

        if "facts" not in fences and kind != "cover":
            found.append((line, f"CLOSE (§3-4): {where} has no ```probe-facts — "
                                f"every slide closes on the evidence ribbon, and "
                                f"the panel types are not exempt"))
        if "script" not in fences:
            found.append((line, f"SPEAK (§6): {where} has no ```probe-script — "
                                f"a slide with no speaker essay is one nobody "
                                f"worked out how to present"))
        if "diagram" in fences:
            try:
                dia = json.loads(fences["diagram"])
            except json.JSONDecodeError as exc:
                found.append((line, f"{where}: ```probe-diagram is not JSON — {exc}"))
            else:
                if not str(dia.get("why", "")).strip():
                    found.append((line, f"DRAWN (§4-2): {where} draws a figure with "
                                        f"no `why` — name the paper's own figure "
                                        f"that covers this ground and what this "
                                        f"one leaves out"))

        for fence in _PANEL_FENCES:
            if fence not in fences:
                continue
            try:
                data = json.loads(fences[fence])
            except json.JSONDecodeError as exc:
                found.append((line, f"{where}: ```probe-{fence} is not JSON — {exc}"))
                continue
            for key, col in data.items():
                if not isinstance(col, dict):
                    continue
                if not str(col.get("foot", "")).strip():
                    found.append((line, f"CLOSE (§3-3): {where}, column {key!r} has "
                                        f"no `foot` — the column closes on its own "
                                        f"one-line conclusion, which is what holds "
                                        f"the bottom edge"))
                for item in col.get("lines", []):
                    reg_total += 1
                    if isinstance(item, dict) and str(item.get("n", "")).strip():
                        reg_noted += 1

    if _TURN not in acts:
        found.append((1, f"SPINE (§1-1): no {_TURN} slide — the turn is what the "
                         f"presentation exists to land, and a presentation without one retells "
                         f"the paper in its own order"))
    elif len(acts) < 2:
        found.append((1, "SPINE (§1-1): every slide sits in one act — a presentation with "
                         "no beats is a table of contents, which is what the paper "
                         "already is"))

    if reg_total and reg_noted / reg_total < _REGISTER_FLOOR:
        found.append((1, f"REGISTER (§2): {reg_noted} of {reg_total} panel items "
                         f"carry a second register, under the {_REGISTER_FLOOR:.0%} "
                         f"floor. A claim with the number or source under it is "
                         f"evidence; a claim alone is a bullet"))
    return sorted(found)


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    docs = args or sorted(
        os.path.relpath(p, _REPO_ROOT)
        for p in glob.glob(os.path.join(_REPO_ROOT, "presentation", "*.md"))
        if os.path.basename(p) != "AUTHORING.md"
    )
    if not docs:
        print("[check-presentation-format] no presentations to check")
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
