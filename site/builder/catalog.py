"""The corpus as data, for an agent rather than a reader.

A reader arrives at a page; an agent arrives with a question — *which papers
bear on X*, *what has not yet been set against what* — and a 300 KB page of
KaTeX and inline SVG is the most expensive way to answer it. This module turns
the same parsed corpus the pages are built from into one record set, and two
front ends serve it: the build writes it as `corpus.json` beside an `llms.txt`
that says where everything is, and `site/query.py` prints it from a checkout.
One function feeds both, so the file on the site and the answer in a terminal
cannot disagree.

**Front matter and relations only — never bodies.** A record is what a paper
*is* and what it touches; the argument lives in the rewrite, and the record
points at the raw Markdown of it (`source`) rather than carrying it. That keeps
the whole corpus inside one context window, which is the point: an agent reads
every record, shortlists, and only then opens two or three sources.

**Every kind of link keeps its own field.** A shared tag, a citation, a
sibling named by alias, a comparison that already set two papers side by side
and a Decision-Log entry both rewrites argue about are five different claims. Folded into one number
they would stop being checkable, so only `neighbours` is a score — the same
`corpus.score` the page's own neighbour row ranks by — and the rest are lists.

Standard library only, like everything it imports: `site/query.py` runs in a
checkout with no `pip install`.
"""

from __future__ import annotations

import re

from . import components as c
from . import corpus
from .corpus import PILLAR_LABELS, PILLAR_NAMES, Paper

SITE = f"https://{c.REPO.split('/')[0]}.github.io/{c.REPO.split('/')[1]}/"
RAW = c.RAW_URL

# How large `corpus.json` may get. It exists to fit in one context window next
# to the question, so it has a ceiling the way `corpus-index.js` does; past it,
# the fields to move out are `summary` and `keywords`, the two largest, not the
# budget.
BUDGET = 256 * 1024

# How many scored neighbours a record lists. More than the page's three, since
# an agent reads the scores and a reader reads only the row.
NEIGHBOURS = 6

_DREF = re.compile(r"(?<![A-Za-z0-9_])D\d[A-Z]{2}(?![A-Za-z0-9])")
_HEAD = re.compile(r"^(#{2,4})[ \t]+(.+?)[ \t]*$", re.M)
_FENCE = re.compile(r"^```.*?^```[ \t]*$", re.S | re.M)
_ACT = re.compile(r"^(\d)\b")


def _headings(md: str) -> list[tuple[int, int, str]]:
    """`(offset, level, text)` for every H2–H4 outside a code fence."""
    fenced = [(m.start(), m.end()) for m in _FENCE.finditer(md)]
    return [
        (m.start(), len(m.group(1)), m.group(2))
        for m in _HEAD.finditer(md)
        if not any(a <= m.start() < b for a, b in fenced)
    ]


def keywords(paper: Paper) -> list[str]:
    """The English terms the rewrite's H3 glosses name, first use first.

    Every section heading of a rewrite ends `| Term · Term · Term` — the
    paper's own English vocabulary for what that section argues. It is the only
    English layer a Korean rewrite carries, and it is what a query in English
    meets. Decision codes are left out; `decisions` carries those.
    """
    seen: dict[str, None] = {}
    for _, level, text in _headings(paper.article or paper.body):
        if level != 3 or "|" not in text:
            continue
        for term in text.rsplit("|", 1)[1].split("·"):
            term = term.strip()
            if term and not _DREF.fullmatch(term):
                seen.setdefault(term, None)
    return list(seen)


def _text(doc) -> str:
    """The body a rewrite argues in (its 요약 tab carved out), or a comparison's."""
    return getattr(doc, "article", "") or doc.body


def outline(doc) -> list[tuple[int, str]]:
    """`(level, heading)` for a rewrite's or a comparison's body."""
    return [(level, text) for _, level, text in _headings(_text(doc))]


def section(doc, act: int | None = None, match: str = "") -> str:
    """Parts of the body, each cut at its own headings.

    `act` is the numbered H2 (`## 3 정말 되는가`) — the four-part spine every
    rewrite and every comparison shares. `match` is a substring of any H2–H4, compared case-folded,
    which is how an English gloss from `keywords` finds the section that argues
    it; every heading it hits is returned, in body order, not only the first.
    A part runs from its heading to the next heading of the same or a higher
    level. Empty when nothing matches.
    """
    md = _text(doc)
    heads = _headings(md)
    parts: list[str] = []
    covered = 0
    for i, (start, level, text) in enumerate(heads):
        if act is not None:
            m = _ACT.match(text)
            hit = level == 2 and m is not None and int(m.group(1)) == act
        else:
            hit = match.casefold() in text.casefold()
        if hit and start >= covered:
            end = next((s for s, lv, _ in heads[i + 1:] if lv <= level), len(md))
            parts.append(md[start:end].rstrip() + "\n")
            covered = end
    return "\n".join(parts)


def section_files(paper: Paper, toc: list[dict]) -> list[dict]:
    """One record per H3 of the body, carrying the text under it.

    What a full build writes as `p/<id>/s/<anchor>.md` beside the page, with
    the list of them as `p/<id>/sections.json` — so an agent that has only the
    site reads the one section an argument rests on instead of the whole
    rewrite. The page itself is untouched: these are the same body cut at its
    own headings, linked from no reader surface.

    `toc` is the page renderer's (`DocRenderer.toc`), so a section file is
    named by the anchor the page carries and a semantic-search hit, which
    returns that anchor, names its file directly. The H3s here and the toc's
    are the same headings in the same order; a body where they disagree yields
    nothing rather than files under the wrong names.
    """
    md = _text(paper)
    heads = _headings(md)
    anchors = [e for e in toc if e.get("kind") == "sec"]
    h3 = [i for i, (_, level, _t) in enumerate(heads) if level == 3]
    if len(h3) != len(anchors):
        return []
    out, act = [], 0
    k = 0
    for i, (start, level, text) in enumerate(heads):
        if level == 2:
            m = _ACT.match(text)
            act = int(m.group(1)) if m else act
            continue
        if level != 3:
            continue
        end = next((s for s, lv, _ in heads[i + 1:] if lv <= 3), len(md))
        entry = anchors[k]
        k += 1
        out.append({
            "act": act,
            "heading": entry["label"],
            "keywords": [t.strip() for t in (entry.get("en") or "").split("·") if t.strip()],
            "anchor": entry["id"],
            "text": md[start:end].rstrip() + "\n",
        })
    return out


def decision_refs(paper: Paper) -> list[str]:
    return sorted(set(_DREF.findall(paper.body)))


def _alias_pattern(alias: str) -> re.Pattern | None:
    """A word-bounded, case-sensitive match for an alias, or None when too thin.

    Two ASCII letters name nothing reliably; a Greek or superscripted alias
    (`μ0`, `πR²`) is distinctive at any length.
    """
    if len(alias) < 3 and alias.isascii():
        return None
    return re.compile(r"(?<![A-Za-z0-9])" + re.escape(alias) + r"(?![A-Za-z0-9])")


def mentions(papers: list[Paper], cited: dict) -> dict[str, list[str]]:
    """`{id: [ids it names by alias]}` — the references an arXiv link misses.

    A rewrite often names a sibling by its codename in prose or in a panel
    (`… KV 캐시로 남겨 두고 대조합니다(TacPAC)`) without linking it. That is a
    different claim from a citation — the paper did not stand on it, the
    rewrite set it beside — so it is its own field, and a pair already joined by
    a citation is not repeated here.
    """
    linked = {(q.stem, target) for target, qs in cited.items() for q in qs}
    patterns = [(p.stem, p.alias, pat) for p in papers if p.alias
                for pat in [_alias_pattern(p.alias)] if pat]
    out: dict[str, list[str]] = {}
    for p in papers:
        for stem, alias, pat in patterns:
            # The substring test first: it rules out nearly every pair for a
            # fraction of what the bounded regex costs on a 70 KB body.
            if (stem != p.stem and (p.stem, stem) not in linked
                    and alias in p.body and pat.search(p.body)):
                out.setdefault(p.stem, []).append(stem)
    return {k: sorted(v) for k, v in out.items()}


def records(papers: list[Paper], comps: list, decisions: dict,
            cited: dict, presented: set[str], retired: set[str] = frozenset()) -> dict:
    """The whole corpus as one JSON-able dict — what `corpus.json` holds.

    `decisions` is `harvest_decisions()`; only the codes some rewrite cites are
    carried, and only their title and pillar — what the pages already print in
    the tooltip on a `D#`, and nothing else from `context/`. A cited code in
    `retired` is listed with `retired: true` and no pillar, and a paper carries
    it under `retired_decisions` rather than `decisions`, since it no longer
    names an open question two papers could share.
    """
    ordered = sorted(papers, key=lambda p: p.order_key, reverse=True)
    comps = sorted(comps, key=lambda x: x.order_key, reverse=True)
    refs = {p.stem: decision_refs(p) for p in ordered}
    named = mentions(ordered, cited)
    by_mention: dict[str, list[str]] = {}
    for src, targets in named.items():
        for t in targets:
            by_mention.setdefault(t, []).append(src)
    cites: dict[str, list[str]] = {}
    for target, citers in cited.items():
        for citer in citers:
            cites.setdefault(citer.stem, []).append(target)

    rows = []
    for p in ordered:
        near = sorted(
            ((corpus.score(p, o), o.order_key, o) for o in ordered if o is not p),
            key=lambda t: (t[0], t[1]), reverse=True,
        )
        rows.append({
            "id": p.stem,
            "alias": p.alias,
            "title": p.title,
            "tagline": p.tagline,
            "authors": p.authors,
            "pillars": p.pillars,
            "tags": p.tags,
            "metric": p.metric,
            "summary": corpus._plain(p.summary_md, limit=10_000),
            "keywords": keywords(p),
            "published": p.published,
            "date": p.date,
            "page": f"{SITE}p/{p.stem}/",
            "source": f"{RAW}/analysis/{p.stem}.md",
            "sections": f"{SITE}p/{p.stem}/sections.json",
            "presentation": p.stem in presented,
            "compared_in": [x.slug for x in comps if p.stem in x.paper_ids],
            "cites": sorted(cites.get(p.stem, [])),
            "cited_by": [q.stem for q in cited.get(p.stem, [])],
            "mentions": named.get(p.stem, []),
            "mentioned_by": sorted(by_mention.get(p.stem, [])),
            "decisions": [d for d in refs[p.stem] if d not in retired],
            "retired_decisions": [d for d in refs[p.stem] if d in retired],
            "neighbours": [{"id": o.stem, "score": s} for s, _, o in near[:NEIGHBOURS] if s],
        })

    used = sorted({d for r in refs.values() for d in r if d in decisions or d in retired})
    tag_counts: dict[str, int] = {}
    for p in ordered:
        for t in p.tags:
            tag_counts[t] = tag_counts.get(t, 0) + 1

    return {
        "schema": 1,
        "site": SITE,
        "source": f"https://github.com/{c.REPO}",
        "pillars": {k: {"name": PILLAR_NAMES[k], "label": PILLAR_LABELS.get(k, "")}
                    for k in PILLAR_NAMES},
        "decisions": {d: ({"pillar": f"P{decisions[d][0]}", "title": decisions[d][1]}
                          if d in decisions and d not in retired else
                          {"pillar": None, "title": "", "retired": True})
                      for d in used},
        "tags": dict(sorted(tag_counts.items(), key=lambda kv: (-kv[1], kv[0]))),
        "papers": rows,
        "comparisons": [
            {
                "slug": x.slug,
                "title": x.title,
                "tagline": x.tagline,
                "compares": x.paper_ids,
                "stances": x.stances,
                "common": x.common,
                "pillars": x.pillars,
                "tags": x.tags,
                "summary": corpus._plain(x.summary_md, limit=10_000),
                "date": x.date,
                "page": f"{SITE}c/{x.slug}/",
                "source": f"{RAW}/comparison/{x.slug}.md",
            }
            for x in comps
        ],
    }


def llms_txt(cat: dict, search_api: str = "") -> str:
    """`llms.txt` — the one URL an agent is handed, saying where the rest is.

    Descriptive only: what the corpus is, where each kind of file lives and one
    line per document. How to *use* it for a task is a procedure, and
    procedures live in `.claude/prompts/`. `search_api` is the build's
    semantic-search endpoint; given one, its contract is listed too.
    """
    site, src = cat["site"], cat["source"]
    lines = [
        "# PROBE",
        "",
        "> Korean re-tellings of dexterous-manipulation papers, each written from "
        "the paper's arXiv HTML original, plus comparisons that set two or three "
        "of them against one question. Titles, tags and section glosses are "
        "English; taglines, summaries and bodies are Korean.",
        "",
        "Every rewrite follows one four-part spine: `## 1 무엇이 문제인가` "
        "(the problem), `## 2 무엇을 바꿨나` (the method), `## 3 정말 되는가` "
        "(the evidence) and `## 4 연구축에 무엇이 걸리나` (what it means for this "
        "team's research pillars, citing Decision-Log codes like `D9NB`). Each H3 "
        "ends `| English · Terms`, the section's vocabulary.",
        "",
        "## Data",
        "",
        f"- [corpus.json]({site}corpus.json): every paper and comparison as one "
        "record — front matter, English keywords, pillars, tags, and the five "
        "relations kept apart: `neighbours` (scored by shared tags and pillars), "
        "`cites` / `cited_by` (arXiv links), "
        "`mentions` / `mentioned_by` (named by alias without a link), "
        "`compared_in` and `decisions`. No bodies.",
        f"- Raw Markdown of any paper: `{RAW}/analysis/<arxiv-id>.md`; of a "
        f"comparison: `{RAW}/comparison/<slug>.md`. A record's `source` is that "
        "URL. Far lighter than the HTML page.",
        f"- One section at a time: `{site}p/<arxiv-id>/sections.json` lists a "
        "rewrite's H3 sections — act, Korean heading, English keywords, anchor — "
        "and each is `" + site + "p/<arxiv-id>/s/<anchor>.md`, a few KB instead "
        "of the whole rewrite. A record's `sections` is that list's URL.",
        f"- Research context the `## 4` parts argue against — pillars, the "
        f"Decision Log, anti-topics: {src}/tree/main/context",
        f"- In a checkout, `python3 site/query.py --help` answers the same "
        "questions from the repo, standard library only.",
        "",
    ]
    if search_api:
        lines += [
            "## Search",
            "",
            f"Semantic search over the rewrites' sections, terms and figure captions "
            f"(comparisons are not indexed), Korean or English: `POST {search_api}` "
            "with JSON `{\"q\": \"...\", \"limit\": 12, \"pillars\": [\"P1\"]}` "
            "(`limit` at most 24, `pillars` optional). It answers `{\"hits\": [...], "
            "\"expanded\": [...]}`; a hit carries `paperId`, `kind`, `title`, "
            "`anchor` and a 240-character `snippet` — passages to open, not the "
            "text itself. `p/<paperId>/s/<anchor>.md` is the section a hit points "
            "into. 30 requests a minute; `python3 site/query.py search` asks it "
            "from a checkout.",
            "",
        ]
    lines += [
        "## Pillars",
        "",
    ]
    for k, v in cat["pillars"].items():
        lines.append(f"- {k} — {v['name']}")
    lines += ["", "## Papers", ""]
    for r in cat["papers"]:
        alias = r["alias"]
        name = (f"{alias} — {r['title']}"
                if alias and not r["title"].startswith(alias) else r["title"])
        lines.append(f"- [{name}]({r['source']}): {r['id']} · "
                     f"{', '.join(r['pillars'])} · {r['tagline']}")
    lines += ["", "## Comparisons", ""]
    for x in cat["comparisons"]:
        lines.append(f"- [{x['title']}]({x['source']}): {' vs '.join(x['compares'])} · "
                     f"{x['tagline']}")
    return "\n".join(lines) + "\n"
