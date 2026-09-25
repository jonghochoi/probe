#!/usr/bin/env python3
"""Query the PROBE corpus from a checkout — for an agent, standard library only.

Reads the same records the build publishes as `corpus.json`
(`builder/catalog.py`), so an answer here and the file on the site agree.
Tab-separated rows under a `# column` header line by default; `--json` prints
one JSON object per line, the same keys on every line of one command.

    python3 site/query.py catalog [--pillar P2] [--tag flow-matching] [--decision D9NB]
                                  [--match "지연|latency"]
    python3 site/query.py tags
    python3 site/query.py search "정책이 느린 걸 해결한 논문" [--pillar P1] [--limit 12]
    python3 site/query.py show <id|alias|comparison slug>
    python3 site/query.py related <id|alias>
    python3 site/query.py outline <id|alias|slug>
    python3 site/query.py section <id|alias|slug> (--act 1-4 | --match "Flow Matching")
    python3 site/query.py decision <D#>
    python3 site/query.py pairs [--with <id|alias>] [--by score|decisions|contrast] [--limit 20]
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import signal
import sys
import urllib.error
import urllib.request
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from builder import catalog, comparisons, corpus, presentations  # noqa: E402
from builder.decisions import harvest_decisions, retired_decisions  # noqa: E402

ACTS = range(1, 5)


def load() -> tuple[dict, dict]:
    """The records, and every source document by id or comparison slug."""
    papers, _ = corpus.discover()
    by_id = {p.stem: p for p in papers}
    comps, _ = comparisons.discover(by_id)
    presented, _ = presentations.discover(by_id)
    cat = catalog.records(papers, comps, harvest_decisions(),
                          corpus.citations(papers), set(presented), retired_decisions())
    return cat, {**by_id, **{x.slug: x for x in comps}}


def resolve(cat: dict, key: str) -> dict:
    fold = key.casefold()
    for r in cat["papers"]:
        if fold in (r["id"], r["alias"].casefold()):
            return r
    sys.exit(f"query: no rewrite with id or alias {key!r} — `catalog` lists them")


def resolve_doc(cat: dict, key: str) -> dict:
    """A paper's record, or failing that a comparison's, by its slug."""
    for x in cat["comparisons"]:
        if key == x["slug"]:
            return x
    return resolve(cat, key)


def doc_key(r: dict) -> str:
    return r.get("id") or r["slug"]


def name(r: dict) -> str:
    return r["alias"] or r["title"]


def rarity(cat: dict) -> dict[str, float]:
    """`{code: weight}` — how much sharing a Decision-Log code says.

    A handful of codes are cited by most rewrites, and two papers both citing
    one of them share little more than a corpus. Inverse document frequency
    weighs a code by how few rewrites argue about it. Retired codes carry no
    weight: they name no open question left to share.
    """
    n = len(cat["papers"])
    df: dict[str, int] = {}
    for r in cat["papers"]:
        for d in r["decisions"]:
            df[d] = df.get(d, 0) + 1
    return {d: math.log(n / k) for d, k in df.items()}


def by_weight(codes, w: dict) -> list[str]:
    """Rarest first, ties by code — the same order on every run."""
    return sorted(codes, key=lambda d: (-w[d], d))


def emit(rows: list[list], as_json: bool, header: list[str]) -> None:
    if rows and header and not as_json:
        print("# " + "\t".join(header))
    for row in rows:
        if as_json:
            print(json.dumps(dict(zip(header, row)), ensure_ascii=False))
        else:
            print("\t".join(" ".join(v) if isinstance(v, list) else str(v) for v in row))


MATCH_FIELDS = ("title", "alias", "tagline", "keywords", "summary")


def cmd_catalog(cat: dict, a) -> None:
    """One row per paper; `--json` is the whole record, `--match` a text filter.

    `--match` is a case-folded regular expression over the fields that say what
    a paper is about, and each row names the fields it hit — which is what a
    topic search needs before it opens anything.
    """
    pillar = a.pillar.upper() if a.pillar else ""
    tag = a.tag.casefold() if a.tag else ""
    code = a.decision.upper() if a.decision else ""
    if pillar and pillar not in cat["pillars"]:
        sys.exit(f"query: no pillar {pillar} — {', '.join(cat['pillars'])}")
    if tag and tag not in cat["tags"]:
        close = [t for t in cat["tags"] if tag in t or t in tag][:8]
        sys.exit(f"query: no tag {tag!r}" + (f" — close: {', '.join(close)}" if close
                                             else " — `tags` lists them"))
    if code and code not in cat["decisions"]:
        sys.exit(f"query: no rewrite cites {code}")
    try:
        rx = re.compile(a.match, re.I) if a.match else None
    except re.error as exc:
        sys.exit(f"query: --match is a regular expression: {exc}")

    def hits(r: dict) -> list[str]:
        if not rx:
            return []
        return [f for f in MATCH_FIELDS
                if rx.search(" · ".join(r[f]) if isinstance(r[f], list) else r[f])]

    rows = []
    for r in cat["papers"]:
        if ((not pillar or pillar in r["pillars"])
                and (not tag or tag in r["tags"])
                and (not code or code in r["decisions"] + r["retired_decisions"])):
            fields = hits(r)
            if not rx or fields:
                rows.append((r, fields))
    if a.json:
        for r, fields in rows:
            print(json.dumps({**r, "matched": fields} if rx else r, ensure_ascii=False))
        return
    emit([[r["id"], name(r), r["pillars"]] + ([fields] if rx else []) + [r["tagline"]]
          for r, fields in rows],
         False, ["id", "name", "pillars"] + (["matched"] if rx else []) + ["tagline"])


def cmd_tags(cat: dict, a) -> None:
    emit([[t, n] for t, n in cat["tags"].items()], a.json, ["tag", "papers"])


_ENDPOINT = re.compile(r"`POST (https://[^`\s]+)`")


def endpoint(explicit: str) -> str:
    """The semantic-search endpoint: `--api`, `PROBE_SEARCH_API`, or `llms.txt`.

    The URL is a repository variable, not a file in the checkout, so a checkout
    that was not handed it reads it where the site publishes it.
    """
    url = explicit or os.environ.get("PROBE_SEARCH_API", "")
    if url:
        return url
    try:
        with urllib.request.urlopen(catalog.SITE + "llms.txt", timeout=10) as res:
            m = _ENDPOINT.search(res.read().decode("utf-8"))
    except (urllib.error.URLError, OSError):
        m = None
    return m.group(1) if m else ""


def cmd_search(cat: dict, a) -> None:
    """Semantic search, from the endpoint the site's own search box asks.

    The one subcommand that needs the network: the index lives in the
    deployed project, not in the checkout. Each hit names the section file
    (`p/<id>/s/<anchor>.md`) its anchor points into; from a checkout, `section
    <id> --match "<title>"` prints the same passage. When the endpoint cannot
    be reached, `catalog --match` is the lexical search that needs nothing.
    """
    url = endpoint(a.api)
    if not url:
        sys.exit("query: no search endpoint — pass --api or set PROBE_SEARCH_API "
                 "(the site's llms.txt lists it); `catalog --match` searches offline")
    body = {"q": a.q, "limit": a.limit}
    if a.pillar:
        body["pillars"] = [a.pillar.upper()]
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            got = json.load(res)
    except (urllib.error.URLError, OSError, ValueError) as exc:
        sys.exit(f"query: search failed ({exc}) — `catalog --match` searches offline")
    by_id = {r["id"]: r for r in cat["papers"]}
    rows = []
    for h in got.get("hits", []):
        pid, anchor = h.get("paperId", ""), h.get("anchor") or ""
        rows.append([pid, name(by_id[pid]) if pid in by_id else "", h.get("kind", ""),
                     h.get("title", ""),
                     f"{catalog.SITE}p/{pid}/s/{anchor}.md" if anchor else "",
                     h.get("snippet", "")])
    if not a.json and got.get("expanded"):
        print("# read as: " + ", ".join(got["expanded"]))
    emit(rows, a.json, ["id", "name", "kind", "title", "section_file", "snippet"])


def cmd_show(cat: dict, a) -> None:
    print(json.dumps(resolve_doc(cat, a.paper), ensure_ascii=False,
                     indent=None if a.json else 1))


def cmd_related(cat: dict, a) -> None:
    """Every relation the paper has, one kind per block and never merged."""
    me = resolve(cat, a.paper)
    by_id = {r["id"]: r for r in cat["papers"]}
    rows = [["neighbour", n["id"], name(by_id[n["id"]]),
             f"score {n['score']}: "
             + " ".join(t for t in me["tags"] if t in by_id[n["id"]]["tags"])]
            for n in me["neighbours"]]
    for kind in ("cites", "cited_by", "mentions", "mentioned_by"):
        rows += [[kind, i, name(by_id[i]), ""] for i in me[kind]]
    for x in cat["comparisons"]:
        if me["id"] not in x["compares"]:
            continue
        for pid, stance in zip(x["compares"], x["stances"]):
            if pid != me["id"]:
                rows.append(["compared_with", pid, name(by_id[pid]),
                             f"{x['slug']}: {stance}"])
    # A comparison this paper is not in, holding a paper it is linked to: the
    # question may already be argued one step away.
    linked = {n["id"] for n in me["neighbours"]}.union(
        me["cites"], me["cited_by"], me["mentions"], me["mentioned_by"])
    for x in cat["comparisons"]:
        if me["id"] in x["compares"]:
            continue
        for pid, stance in zip(x["compares"], x["stances"]):
            if pid in linked:
                rows.append(["nearby_comparison", pid, name(by_id[pid]),
                             f"{x['slug']}: {stance}"])
    w = rarity(cat)
    mine = set(me["decisions"])
    shared = []
    for r in cat["papers"]:
        common = by_weight(mine & set(r["decisions"]), w)
        if r is not me and common:
            shared.append((round(sum(w[d] for d in common), 1), r["id"], r, common))
    shared.sort(key=lambda t: (-t[0], t[1]))
    rows += [["same_decision", r["id"], name(r), f"weight {s}: {' '.join(common)}"]
             for s, _, r, common in shared[:a.limit]]
    emit(rows, a.json, ["relation", "id", "name", "detail"])


def cmd_outline(cat: dict, a, by_id: dict) -> None:
    paper = by_id[doc_key(resolve_doc(cat, a.paper))]
    heads = catalog.outline(paper)
    if a.json:
        emit([[lv, t] for lv, t in heads], True, ["level", "heading"])
        return
    for level, text in heads:
        print(f"{'  ' * (level - 2)}{'#' * level} {text}")


def cmd_section(cat: dict, a, by_id: dict) -> None:
    paper = by_id[doc_key(resolve_doc(cat, a.paper))]
    if a.act is not None and a.act not in ACTS:
        sys.exit("query: acts are 1–4 — the problem, the method, the evidence, the pillars")
    text = catalog.section(paper, act=a.act, match=a.match or "")
    if not text:
        heads = "\n".join(f"  {'#' * lv} {t}" for lv, t in catalog.outline(paper))
        sys.exit(f"query: no heading matched {a.match!r}; the headings are:\n{heads}")
    sys.stdout.write(text)


def cmd_decision(cat: dict, a) -> None:
    code = a.code.upper()
    info = cat["decisions"].get(code)
    if not info:
        sys.exit(f"query: no rewrite cites {code}")
    key = "retired_decisions" if info.get("retired") else "decisions"
    rows = [[code, info["pillar"] or "retired", info["title"], r["id"], name(r), r["tagline"]]
            for r in cat["papers"] if code in r[key]]
    if a.json:
        emit(rows, True, ["decision", "pillar", "title", "id", "name", "tagline"])
        return
    print(f"# {code} (retired — context/MASTER.md)" if info.get("retired")
          else f"# {code} ({info['pillar']}) {info['title']}")
    emit([row[3:] for row in rows], False, [])


def cmd_pairs(cat: dict, a, by_id: dict) -> None:
    """Pairs no comparison has set side by side yet — raw material for an idea.

    Three orders, each a different question, and every column prints under all
    of them:

    - `score` (the default) is `corpus.score`, the rule the site's neighbour
      row and `/compare`'s candidate list already rank by — a second rule for
      that question would be a second answer to it.
    - `decisions` asks which pairs argue about the same Decision-Log entries,
      each shared code weighed by `rarity`.
    - `contrast` asks which pairs meet on a *narrow* open question from
      *different* machinery. Only a narrow code counts — one at most
      `narrow_df` rewrites cite, since a code half the corpus argues about is
      no meeting point — and its weight is discounted by how alike the two
      papers' tags already are (`1 - Jaccard`). A pair sharing no narrow code
      is not a contrast and is left out of this order.
    """
    w = rarity(cat)
    n = len(cat["papers"])
    df = {d: round(n / math.exp(v)) for d, v in w.items()}
    narrow_df = max(3, n // 8)
    done = {frozenset(p) for x in cat["comparisons"]
            for p in combinations(x["compares"], 2)}
    papers = cat["papers"]
    if a.with_:
        me = resolve(cat, a.with_)
        pool = [(me, r) for r in papers if r is not me]
    else:
        pool = list(combinations(papers, 2))
    rows = []
    for x, y in pool:
        if frozenset((x["id"], y["id"])) in done:
            continue
        shared = by_weight(set(x["decisions"]) & set(y["decisions"]), w)
        narrow = [d for d in shared if df[d] <= narrow_df]
        tx, ty = set(x["tags"]), set(y["tags"])
        jaccard = len(tx & ty) / len(tx | ty) if tx | ty else 0.0
        if a.by == "contrast" and not narrow:
            continue
        link = ("cites" if y["id"] in x["cites"] or x["id"] in y["cites"] else
                "mentions" if y["id"] in x["mentions"] or x["id"] in y["mentions"] else "")
        rows.append({
            "score": corpus.score(by_id[x["id"]], by_id[y["id"]]),
            "decision_weight": round(sum(w[d] for d in shared), 1),
            "contrast": round(sum(w[d] for d in narrow) * (1 - jaccard), 2),
            "row": [x["id"], name(x), y["id"], name(y)],
            "tail": [[f"{d}({df[d]})" for d in narrow], shared, link,
                     [t for t in x["tags"] if t in ty]],
        })
    first, second = {"score": ("score", "decision_weight"),
                     "decisions": ("decision_weight", "score"),
                     "contrast": ("contrast", "decision_weight")}[a.by]
    rows.sort(key=lambda r: (-r[first], -r[second], r["row"][0], r["row"][2]))
    if not rows and a.by == "contrast":
        sys.exit(f"query: no uncovered pair shares a Decision-Log code cited by "
                 f"{narrow_df} rewrites or fewer — `--by decisions` ranks the broad ones")
    emit(
        [r["row"] + [r["score"], r["decision_weight"], r["contrast"]] + r["tail"]
         for r in rows[:max(a.limit, 0)]],
        a.json, ["a", "a_name", "b", "b_name", "score", "decision_weight", "contrast",
                 "narrow_decisions", "shared_decisions", "link", "shared_tags"],
    )


PAIRS_COLUMNS = """columns:
  score             corpus.score — 2 per shared tag + 1 per shared pillar
  decision_weight   sum of log(n/df) over the live Decision-Log codes both cite
  contrast          narrow codes' weight x (1 - tag Jaccard); 0 when none is narrow
  narrow_decisions  shared codes cited by at most max(3, n/8) rewrites, (df) beside each
  shared_decisions  every live code both cite, rarest first
  link              cites | mentions, when one rewrite already reaches the other
  shared_tags       tags both carry
pairs a comparison already holds are never listed."""


def main() -> int:
    # A pipe closed early (`| head`) ends the listing, not the program with a trace.
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog="\n".join(__doc__.split("\n")[7:]))
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", help="one JSON object per line")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def command(cmd: str, text: str) -> argparse.ArgumentParser:
        return sub.add_parser(cmd, help=text, parents=[common])

    p = command("catalog", "one row per paper, optionally filtered")
    p.add_argument("--pillar")
    p.add_argument("--tag")
    p.add_argument("--decision")
    p.add_argument("--match", help="regex over title, alias, tagline, keywords, summary")
    command("tags", "every tag with how many papers carry it")
    p = command("search", "semantic search through the site's endpoint (network)")
    p.add_argument("q")
    p.add_argument("--pillar")
    p.add_argument("--limit", type=int, default=12)
    p.add_argument("--api", default="", help="the endpoint; default PROBE_SEARCH_API or llms.txt")
    p = command("show", "one paper's or comparison's full record")
    p.add_argument("paper")
    p = command("related", "every relation a paper has, by kind")
    p.add_argument("paper")
    p.add_argument("--limit", type=int, default=8, help="rows of same_decision")
    p = command("outline", "a rewrite's or comparison's headings")
    p.add_argument("paper")
    p = command("section", "parts of a rewrite's or comparison's body")
    p.add_argument("paper")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--act", type=int, help="the numbered part, 1–4")
    g.add_argument("--match", help="a substring of any H2–H4 heading; every hit prints")
    p = command("decision", "a Decision-Log code and the rewrites citing it")
    p.add_argument("code")
    p = sub.add_parser("pairs", help="paper pairs no comparison covers yet",
                       parents=[common], epilog=PAIRS_COLUMNS,
                       formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--with", dest="with_", metavar="PAPER")
    p.add_argument("--by", choices=("score", "decisions", "contrast"), default="score")
    p.add_argument("--limit", type=int, default=20)
    a = ap.parse_args()

    cat, by_id = load()
    if a.cmd in ("outline", "section", "pairs"):
        {"outline": cmd_outline, "section": cmd_section, "pairs": cmd_pairs}[a.cmd](cat, a, by_id)
    else:
        {"catalog": cmd_catalog, "tags": cmd_tags, "search": cmd_search, "show": cmd_show,
         "related": cmd_related, "decision": cmd_decision}[a.cmd](cat, a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
