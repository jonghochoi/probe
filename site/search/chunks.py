"""Cut the rewrites into the units a semantic search returns.

A search result is a place to land, not a document to open: a rewrite is 60 KB
and a whole-paper vector smears its sections together, so the unit here is the
section a reader would have scrolled to. Each rewrite contributes its sections,
its term panels and its figure captions, plus one chunk standing for the paper
as a whole.

Nothing here touches the network. `build-site.py --index` writes what this
module produces; `site/search/indexer.py` is what embeds and uploads it.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass, field

# A chunk longer than this is split at a paragraph boundary. The ceiling is
# about recall, not about the model's context: one vector averages whatever it
# is given, so a chunk holding two arguments is findable by neither.
CHUNK_MAX = 1_600

_FENCE = re.compile(r"^```(probe-[a-z]+)[ \t]*\n(.*?)^```[ \t]*$", re.M | re.S)
_ANY_FENCE = re.compile(r"^```.*?^```[ \t]*$", re.M | re.S)
_H3 = re.compile(r"^###[ \t]+(.+?)[ \t]*$", re.M)
_JSON_STR = r'"{}"\s*:\s*"((?:[^"\\]|\\.)*)"'


@dataclass
class Chunk:
    uid: str                     # stable across runs — the upsert key
    kind: str                    # paper | section | term | figure
    paper_id: str                # the arXiv id, which is also the file name
    title: str                   # what a result card prints as its heading
    context: str                 # the act it sits under, so a hit reads in place
    path: str                    # the page it lands on
    anchor: str                  # in-page anchor, empty when there is none
    pillars: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    date: str = ""
    text: str = ""

    @property
    def content_hash(self) -> str:
        """What decides whether this chunk needs embedding again."""
        return hashlib.sha256(
            f"{self.title}\n{self.context}\n{self.text}".encode()
        ).hexdigest()[:16]

    def as_dict(self) -> dict:
        return {**asdict(self), "content_hash": self.content_hash}


# ── Shared text handling ────────────────────────────────────────────────────

def plain(md: str) -> str:
    """Markdown → the sentences an embedding should see.

    Badge images, link targets and heading marks are addressing, not content —
    an embedding that reads them spends dimensions on `img.shields.io`.
    """
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", md)          # badges and figures
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)     # links keep their label
    text = re.sub(r"\$`([^`]*)`\$", r"\1", text)             # inline math, as written
    text = re.sub(r"^[|>#*\-\s]*\|", " ", text, flags=re.M)  # table gutters
    text = re.sub(r"[`*_#]+", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n{2,}", "\n\n", text).strip()


def _split_long(text: str) -> list[str]:
    """One chunk per argument: paragraphs are the seam, sentences the fallback."""
    if len(text) <= CHUNK_MAX:
        return [text] if text else []
    parts, current = [], ""
    for para in re.split(r"\n{2,}", text):
        if len(current) + len(para) + 2 > CHUNK_MAX and current:
            parts.append(current.strip())
            current = ""
        current += para + "\n\n"
        while len(current) > CHUNK_MAX:            # one paragraph over the cap
            cut = current.rfind(". ", 0, CHUNK_MAX) + 1 or CHUNK_MAX
            parts.append(current[:cut].strip())
            current = current[cut:]
    if current.strip():
        parts.append(current.strip())
    return parts


def _fence_values(payload: str, key: str) -> list[str]:
    return [v.replace('\\"', '"')
            for v in re.findall(_JSON_STR.format(key), payload)]


def from_rewrite(paper, toc: list[dict]) -> list[Chunk]:
    """One rewrite's chunks.

    `toc` comes from the same `DocRenderer` the page is built with, so every
    anchor here is one the published page actually carries — the alternative is
    a second slug parser drifting away from the first.
    """
    out: list[Chunk] = []
    meta = dict(pillars=paper.pillars, tags=paper.tags, date=paper.date,
                path=f"p/{paper.stem}/")

    def add(kind: str, title: str, context: str, text: str, anchor: str = "") -> None:
        for part in _split_long(plain(text)):
            out.append(Chunk(uid=f"{paper.stem}:{len(out) + 1}", kind=kind,
                             paper_id=paper.stem, title=title, context=context,
                             anchor=anchor, text=part, **meta))

    # The paper as a whole — what answers "그 25 Hz 나오던 거" before any one
    # section does, and what a result card falls back to when no section wins.
    add("paper", paper.title, "재작성본",
        "\n\n".join(filter(None, [paper.tagline, paper.metric,
                                   plain(paper.summary_md), " ".join(paper.tags)])))

    # The toc is in document order, so walking it carries the act a section
    # sits under down onto the section's own chunk: "3. 무엇이 증명되었나" is
    # most of what tells a reader whether a hit is a claim or its evidence.
    bodies = _sections(paper.article or paper.body)
    act = ""
    idx = 0
    for entry in toc:
        if entry.get("kind") == "act":
            act = entry["label"]
            continue
        if entry.get("kind") != "sec" or idx >= len(bodies):
            continue
        body = bodies[idx][1]
        idx += 1
        label = entry["label"] + (f" · {entry['en']}" if entry.get("en") else "")
        add("section", label, act or paper.title,
            f"{label}\n\n{_ANY_FENCE.sub('', body)}", anchor=entry["id"])
        # Term panels and figure captions are their own chunks rather than part
        # of the section's: a term is the 한/영 bridge a reader searches by name,
        # and a caption is a different sentence about a different thing.
        for kind, payload in _FENCE.findall(body):
            if kind == "probe-term":
                for term, gloss in zip(_fence_values(payload, "title"),
                                       _fence_values(payload, "body")):
                    add("term", term, f"{paper.title} · 용어",
                        f"{term}\n\n{gloss}", anchor=entry["id"])
            elif kind == "probe-figure":
                for caption in _fence_values(payload, "caption"):
                    add("figure", caption, f"{paper.title} · 그림", caption,
                        anchor=entry["id"])
    return out


def _sections(article: str) -> list[tuple[str, str]]:
    """`[(heading, body)]` at H3 — the unit the page's contents links to."""
    parts = _H3.split(article)
    return list(zip(parts[1::2], parts[2::2]))

