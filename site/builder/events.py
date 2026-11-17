"""`context/EVENTS.md` — the conference and submission dates the first
screen counts down to.

The dates table in that file — the one whose header opens `시작` — read row by
row against the shape the file itself states: two ISO dates, a kind out of
three, a name, an optional place and the official page the date came from. The
venues table above it is the follow routine's input and is not read here. A
row that breaks the shape is a problem the build reports rather than a date it
guesses at. Standard library only, so the routine runs this check without the
site's dependencies.
"""
from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass
from pathlib import Path

from .corpus import REPO_ROOT

PATH = REPO_ROOT / "context" / "EVENTS.md"
# The file's Korean kind, and the class the page colours it by.
KINDS = {"학회": "conf", "마감": "deadline", "발표": "notice"}
_ROW = re.compile(r"^\|(.*)\|\s*$")


@dataclass
class Event:
    start: str
    end: str
    kind: str          # conf · deadline · notice
    name: str
    place: str
    url: str


def discover(path: Path = PATH) -> tuple[list[Event], list[str]]:
    """Every row, nearest first, and what is wrong with the ones that break."""
    if not path.is_file():
        return [], []
    events, problems = [], []
    in_dates = False
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        m = _ROW.match(line.strip())
        if not m:
            in_dates = False
            continue
        cells = [c.strip() for c in m.group(1).split("|")]
        if cells[0] == "시작":
            in_dates = True
            continue
        if not in_dates or set("".join(cells)) <= set("-: "):
            continue
        where = f"{path.relative_to(REPO_ROOT)}:{n}"
        if len(cells) != 6:
            problems.append(f"{where}: an event row has six cells, got {len(cells)}")
            continue
        start, end, kind, name, place, url = cells
        try:
            if dt.date.fromisoformat(end) < dt.date.fromisoformat(start):
                problems.append(f"{where}: ends before it starts")
                continue
        except ValueError:
            problems.append(f"{where}: dates are YYYY-MM-DD")
            continue
        if kind not in KINDS:
            problems.append(f"{where}: 종류 is one of {', '.join(KINDS)}, got {kind!r}")
            continue
        if not name or not url.startswith("https://"):
            problems.append(f"{where}: a row needs a name and an https 출처")
            continue
        events.append(Event(start, end, KINDS[kind], name, place, url))
    events.sort(key=lambda e: (e.start, e.end))
    return events, problems
