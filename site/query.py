#!/usr/bin/env python3
"""Query the PROBE corpus from a checkout — for an agent, standard library only.

Reads the same records the build publishes as `corpus.json`
(`builder/catalog.py`), so an answer here and the file on the site agree.
Tab-separated rows by default; `--json` prints one JSON object per line, the
same keys on every line of one command.

    python3 site/query.py catalog [--pillar P2] [--tag flow-matching] [--decision D9NB]
    python3 site/query.py tags
    python3 site/query.py show <id|alias>
    python3 site/query.py related <id|alias>
    python3 site/query.py outline <id|alias>
    python3 site/query.py section <id|alias> (--act 1-4 | --match "Flow Matching")
    python3 site/query.py decision <D#>
    python3 site/query.py pairs [--with <id|alias>] [--by score|decisions|contrast] [--limit 20]
"""

from __future__ import annotations

import argparse
import json
import math
import signal
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from builder import catalog, comparisons, corpus, presentations  # noqa: E402
from builder.decisions import harvest_decisions, retired_decisions  # noqa: E402

ACTS = range(1, 5)


def load() -> tuple[dict, dict]:
    papers, _ = corpus.discover()
    by_id = {p.stem: p for p in papers}
    comps, _ = comparisons.discover(by_id)
    presented, _ = presentations.discover(by_id)
    cat = catalog.records(papers, comps, harvest_decisions(),
                          corpus.citations(papers), set(presented), retired_decisions())
    return cat, by_id


def resolve(cat: dict, key: str) -> dict:
    fold = key.casefold()
    for r in cat["papers"]:
        if fold in (r["id"], r["alias"].casefold()):
            return r
    sys.exit(f"query: no rewrite with id or alias {key!r} — `catalog` lists them")


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
    for row in rows:
        if as_json:
            print(json.dumps(dict(zip(header, row)), ensure_ascii=False))
        else:
            print("\t".join(" ".join(v) if isinstance(v, list) else str(v) for v in row))


def cmd_catalog(cat: dict, a) -> None:
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
    rows = [
        r for r in cat["papers"]
        if (not pillar or pillar in r["pillars"])
        and (not tag or tag in r["tags"])
        and (not code or code in r["decisions"] + r["retired_decisions"])
    ]
    emit([[r["id"], name(r), r["pillars"], r["tagline"]] for r in rows],
         a.json, ["id", "name", "pillars", "tagline"])


def cmd_tags(cat: dict, a) -> None:
    emit([[t, n] for t, n in cat["tags"].items()], a.json, ["tag", "papers"])


def cmd_show(cat: dict, a) -> None:
    print(json.dumps(resolve(cat, a.paper), ensure_ascii=False,
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
    paper = by_id[resolve(cat, a.paper)["id"]]
    heads = catalog.outline(paper)
    if a.json:
        emit([[lv, t] for lv, t in heads], True, ["level", "heading"])
        return
    for level, text in heads:
        print(f"{'  ' * (level - 2)}{'#' * level} {text}")


def cmd_section(cat: dict, a, by_id: dict) -> None:
    paper = by_id[resolve(cat, a.paper)["id"]]
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
    - `decisions` asks which pairs argue about the same narrow Decision-Log
      entries, each shared code weighed by `rarity`.
    - `contrast` asks which pairs meet on a narrow open question from
      *different* machinery: the decision weight divided by one plus the tags
      the two share. Two papers already alike answer the question twice; this
      is the order to read for a combination neither paper makes alone.
    """
    w = rarity(cat)
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
        weight = round(sum(w[d] for d in shared), 1)
        tags = [t for t in x["tags"] if t in set(y["tags"])]
        link = ("cites" if y["id"] in x["cites"] or x["id"] in y["cites"] else
                "mentions" if y["id"] in x["mentions"] or x["id"] in y["mentions"] else "")
        rows.append({
            "score": corpus.score(by_id[x["id"]], by_id[y["id"]]),
            "decision_weight": weight,
            "contrast": round(weight / (1 + len(tags)), 2),
            "row": [x["id"], name(x), y["id"], name(y)],
            "tail": [shared, link, tags],
        })
    first, second = {"score": ("score", "decision_weight"),
                     "decisions": ("decision_weight", "score"),
                     "contrast": ("contrast", "decision_weight")}[a.by]
    rows.sort(key=lambda r: (-r[first], -r[second], r["row"][0], r["row"][2]))
    emit(
        [r["row"] + [r["score"], r["decision_weight"], r["contrast"]] + r["tail"]
         for r in rows[:max(a.limit, 0)]],
        a.json, ["a", "a_name", "b", "b_name", "score", "decision_weight", "contrast",
                 "shared_decisions", "link", "shared_tags"],
    )


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
    command("tags", "every tag with how many papers carry it")
    p = command("show", "one paper's full record")
    p.add_argument("paper")
    p = command("related", "every relation a paper has, by kind")
    p.add_argument("paper")
    p.add_argument("--limit", type=int, default=8, help="rows of same_decision")
    p = command("outline", "a rewrite's headings")
    p.add_argument("paper")
    p = command("section", "parts of a rewrite's body")
    p.add_argument("paper")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--act", type=int, help="the numbered part, 1–4")
    g.add_argument("--match", help="a substring of any H2–H4 heading; every hit prints")
    p = command("decision", "a Decision-Log code and the rewrites citing it")
    p.add_argument("code")
    p = command("pairs", "paper pairs no comparison covers yet")
    p.add_argument("--with", dest="with_", metavar="PAPER")
    p.add_argument("--by", choices=("score", "decisions", "contrast"), default="score")
    p.add_argument("--limit", type=int, default=20)
    a = ap.parse_args()

    cat, by_id = load()
    if a.cmd in ("outline", "section", "pairs"):
        {"outline": cmd_outline, "section": cmd_section, "pairs": cmd_pairs}[a.cmd](cat, a, by_id)
    else:
        {"catalog": cmd_catalog, "tags": cmd_tags, "show": cmd_show,
         "related": cmd_related, "decision": cmd_decision}[a.cmd](cat, a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
