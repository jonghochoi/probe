#!/usr/bin/env python3
"""Check what has to be true once InsForge is connected.

    python3 site/build-site.py --index .search/index.jsonl
    python3 site/search/verify.py .search/index.jsonl

Seven checks, each assuming the one before it: the migration, the index, the
endpoint, the query cache, the trigger that empties it, query expansion, and the
lock on the two tables.

Most of them fail invisibly. The site treats semantic search as an enhancement,
so a missing function, a rejected key and an empty index all look the same from
a browser — the lexical filter answers and the page is exactly what it should
be. Nothing on the page distinguishes a working search from a search that never
ran, which is what this script is for.

Run it by hand after the deploy steps in this folder's `README.md`, and again
after anything that touches the schema. It is deliberately not in CI: a gate
that needs a key and egress fails for reasons its pull request did not cause,
and in the deploy job it would make publishing the site depend on a service the
site does not need. Check 2 is what makes the CI index step knowable anyway —
that step is these two commands and nothing else.

It writes one no-op `UPDATE` on `probe_chunks` and nothing else of its own —
check 5 needs it, since a per-statement trigger fires for a statement and
proving it fires takes one. Its three endpoint calls fill the query cache and
that `UPDATE` empties it, which is checks 4 and 5 between them; the cache is
derived, so leaving it cold costs the next reader one embedding.

Environment:
    INSFORGE_URL        https://<project>.insforge.app
    INSFORGE_API_KEY    admin or project API key — checks 1, 2, 5, 7
    PROBE_SEARCH_API    the deployed function URL — checks 3, 4, 6
    INSFORGE_ANON_KEY   optional; read from the project when unset
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

CHUNKS = "probe_chunks"
CACHE = "probe_query_cache"
DIMS = 1536
ROWS_PER_CALL = 1000
# What `semantic.js` waits before it drops the remote block. An answer slower
# than this is one no reader ever sees, so it is a failure the operator wants
# named even though every call in it succeeded.
PAGE_BUDGET_MS = 5_000
# What the page asks for, so the cache key exercised here is the key it writes.
LIMIT = 8
# The question the lexical filter cannot answer — the reason this folder exists.
PROBE_Q = "정책이 느려터진 거 해결한 논문"
# A transliteration sharing no character with the term it transliterates, so an
# expansion is the only thing that can bridge it.
EXPAND_Q = "플로우매칭"
EXPAND_WANT = "flow matching"


class Fail(SystemExit):
    def __init__(self, msg: str):
        super().__init__(f"error: {msg}")


class Reply:
    """One answer, kept rather than raised — a failing check has to say why."""

    def __init__(self, status: int, data, note: str = ""):
        self.status, self.data, self.note = status, data, note

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300


def call(url: str, *, token: str, method: str = "GET", body=None,
         timeout: int = 30) -> Reply:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            raw = res.read()
            return Reply(res.status, json.loads(raw) if raw else None)
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            parsed = json.loads(raw)
        except ValueError:
            parsed = None
        return Reply(exc.code, parsed, raw[:300].decode(errors="replace").strip())
    except urllib.error.URLError as exc:
        return Reply(0, None, str(exc.reason))
    except OSError as exc:                      # a socket timeout lands here
        return Reply(0, None, str(exc))


def why(reply: Reply) -> str:
    """The shortest true sentence about a reply that did not work."""
    if reply.status == 0:
        return reply.note or "no answer"
    said = ""
    if isinstance(reply.data, dict):
        said = str(reply.data.get("message") or reply.data.get("error") or "")
    return f"HTTP {reply.status}" + (f": {said}" if said else "")


def page_all(base: str, token: str, table: str, select: str):
    """Every row of `table`, projected. `(rows, error)` — one of the two is set."""
    out: list[dict] = []
    offset = 0
    while True:
        got = call(f"{base}/api/database/records/{table}?select={select}"
                   f"&limit={ROWS_PER_CALL}&offset={offset}", token=token)
        if not got.ok:
            return None, why(got)
        rows = got.data or []
        out += rows
        if len(rows) < ROWS_PER_CALL:
            return out, ""
        offset += ROWS_PER_CALL


def cache_rows(base: str, token: str):
    """Up to one page of cache keys. `(rows, error)` — one of the two is set.

    A page answers both questions asked of the cache — whether it is empty, and
    roughly how much the trigger cleared — and a reading site's cache runs to
    however many distinct questions its readers have asked.
    """
    got = call(f"{base}/api/database/records/{CACHE}"
               f"?select=q_norm&limit={ROWS_PER_CALL}", token=token)
    return (None, why(got)) if not got.ok else (got.data or [], "")


def weigh(rows: list) -> str:
    """`n row(s)`, marked when the page it came from was full."""
    return f"{len(rows)}{'+' if len(rows) >= ROWS_PER_CALL else ''} row(s)"


def ask(url: str, body: dict) -> tuple[Reply, int]:
    """One endpoint call, with the round trip the page would have measured."""
    started = time.monotonic()
    got = call(url, token="", method="POST", body=body)
    return got, round((time.monotonic() - started) * 1000)


class Report:
    """The transcript. Every check prints one line whatever happens to it."""

    MARK = {"ok": "ok  ", "off": "off ", "warn": "warn",
            "skip": "skip", "fail": "FAIL"}

    def __init__(self):
        self.counts: Counter = Counter()
        self.n = 0

    def __call__(self, name: str, status: str, detail: str, hint: str = "") -> None:
        self.n += 1
        self.counts[status] += 1
        print(f"{self.n}  {name:<16}{self.MARK[status]}  {detail}", flush=True)
        if hint:
            print(f"       → {hint}", flush=True)


# ── The checks ──────────────────────────────────────────────────────────────

def check_migration(rep: Report, base: str, admin: str) -> bool:
    """`probe_search` answers, which no partly-applied migration can fake.

    One unit vector and one row: the function reads the table, casts a vector
    and returns a set, so a reply at all means the extension, the index table
    and the function are there. A zero vector would be the obvious probe and
    is the wrong one — cosine distance against it is NaN, so the call succeeds
    and proves less. What comes back is not scored; check 2 is what knows
    whether the index behind it is right, and checks 4 and 5 the cache table.
    """
    got = call(f"{base}/api/database/rpc/probe_search", token=admin, method="POST",
               body={"query_embedding": [1.0] + [0.0] * (DIMS - 1), "match_count": 1})
    if got.ok and isinstance(got.data, list):
        rep("migration", "ok", f"probe_search answered with {len(got.data)} row(s)")
        return True
    if got.ok:
        rep("migration", "fail",
            f"probe_search returned {type(got.data).__name__}, not a list",
            "a SETOF function answers as an array through the proxy — check the "
            "RETURNS TABLE clause in site/search/schema.sql")
        return False
    hint = {
        0: "check INSFORGE_URL",
        400: "the function is there and refused the call — a missing `vector` "
             "extension or a signature that moved; re-apply site/search/schema.sql",
        401: "INSFORGE_API_KEY was rejected",
        403: "INSFORGE_API_KEY was rejected",
        404: "probe_search does not exist — apply site/search/schema.sql to "
             "the project",
    }.get(got.status, "read the message above against site/search/schema.sql")
    rep("migration", "fail", why(got), hint)
    return False


def check_index(rep: Report, base: str, admin: str, want: dict[str, str],
                index: Path) -> bool:
    """The table holds the chunks this build produced, and the same versions."""
    rows, err = page_all(base, admin, CHUNKS, "uid,content_hash")
    if err:
        rep("index", "fail", f"cannot read {CHUNKS}: {err}")
        return False
    have = {r["uid"]: r["content_hash"] for r in rows}
    if not have:
        rep("index", "fail",
            f"{CHUNKS} is empty; the build produced {len(want)} chunk(s)",
            f"run: python3 site/search/indexer.py {index}")
        return False
    missing = sorted(set(want) - set(have))
    orphan = sorted(set(have) - set(want))
    stale = sorted(u for u in set(want) & set(have) if have[u] != want[u])
    if not (missing or orphan or stale):
        rep("index", "ok", f"{len(have)} row(s), matching the build exactly")
        return True
    sample = ", ".join((missing + stale + orphan)[:3])
    rep("index", "fail",
        f"{len(have)} row(s) against {len(want)} chunk(s) — {len(missing)} missing, "
        f"{len(stale)} stale, {len(orphan)} orphaned",
        f"{sample} — re-run the indexer against this same index file")
    return False


def check_endpoint(rep: Report, url: str) -> dict | None:
    """A Korean question reaches the deployed function and comes back a list."""
    got, took = ask(url, {"q": PROBE_Q, "limit": LIMIT})
    if not got.ok:
        said = ""
        if isinstance(got.data, dict):
            said = str(got.data.get("error") or "")
        hint = {
            "embedding unavailable": "the function's OPENROUTER_API_KEY is missing "
                                     "or rejected by OpenRouter",
            "search unavailable": "probe_search returned an error to the function — "
                                  "check ANON_KEY has EXECUTE on it",
        }.get(said) or {
            0: "nothing is listening — deploy site/search/function/search.ts as "
               "`search`, or correct PROBE_SEARCH_API",
            404: "the project has no function named `search` at this URL",
            405: "PROBE_SEARCH_API does not name the function — it answers POST only",
            429: "the function's own rate limit; wait a minute and re-run",
        }.get(got.status, "read the function's logs in the InsForge dashboard")
        # No timing when nothing answered — the number would be how long the
        # socket took to refuse, which says nothing about the endpoint.
        when = "" if got.status == 0 else f" in {took} ms"
        rep("endpoint", "fail", f"{why(got)}{when}", hint)
        return None
    hits = (got.data or {}).get("hits")
    if not isinstance(hits, list):
        rep("endpoint", "fail", "the answer carries no `hits` list",
            "PROBE_SEARCH_API reaches something that is not this function")
        return None
    if not hits:
        rep("endpoint", "fail", f"0 hit(s) in {took} ms",
            "the semantic arm has no relevance floor, so an empty list is an "
            "empty pool — an empty index, or an expansion that guessed a pillar "
            "no chunk carries")
        return None
    served = got.data.get("tookMs", "?")
    where = hits[0].get("path", "?")
    if took > PAGE_BUDGET_MS:
        rep("endpoint", "warn",
            f"{len(hits)} hit(s) in {took} ms, {served} ms of it inside the function",
            f"the page drops an answer slower than {PAGE_BUDGET_MS} ms, so no reader "
            f"sees this one — a cold isolate warms up, a slow model does not")
    else:
        rep("endpoint", "ok",
            f"“{PROBE_Q}” → {len(hits)} hit(s) in {took} ms, first {where}")
    return got.data


def check_cache(rep: Report, url: str, base: str, admin: str) -> bool:
    """The same question twice: the second answer comes from the cache.

    Both halves are checked separately because they fail separately — the row
    landing but not coming back means `probe_cache_get`, no row at all means
    `probe_cache_put`, and the two are one grant apart.
    """
    got, took = ask(url, {"q": PROBE_Q, "limit": LIMIT})
    if not got.ok:
        rep("query cache", "fail", f"the second ask failed: {why(got)}")
        return False
    rows, err = cache_rows(base, admin)
    stored = "an unreadable number of rows" if err else weigh(rows)
    if (got.data or {}).get("cached") is True:
        rep("query cache", "ok", f"the second ask came back cached in {took} ms, "
                                 f"{CACHE} holding {stored}")
        return True
    if not err and not rows:
        rep("query cache", "fail", f"answered fresh again and {CACHE} is empty",
            "probe_cache_put wrote nothing — check GRANT EXECUTE ... TO anon in "
            "site/search/schema.sql")
    else:
        rep("query cache", "fail",
            f"answered fresh again although {CACHE} holds {stored}",
            "probe_cache_get is not returning the row — its key is "
            "`<normalised query>|<limit>|<sorted pillars>`")
    return False


def check_cache_clear(rep: Report, base: str, admin: str, uid: str) -> bool:
    """A write to the index empties the cache, so no answer outlives its index."""
    before, err = cache_rows(base, admin)
    if err:
        rep("cache clearing", "fail", f"cannot read {CACHE}: {err}")
        return False
    if not before:
        rep("cache clearing", "skip", f"{CACHE} is already empty — nothing to clear")
        return False
    problem = touch(base, admin, uid)
    if problem:
        rep("cache clearing", "fail", f"cannot write {CHUNKS}: {problem}")
        return False
    after, err = cache_rows(base, admin)
    if err:
        rep("cache clearing", "fail", f"cannot re-read {CACHE}: {err}")
        return False
    if after:
        rep("cache clearing", "fail",
            f"{weigh(after)} survived a write to {CHUNKS}",
            "the statement trigger did not fire — check probe_chunks_clear_cache "
            "in site/search/schema.sql")
        return False
    rep("cache clearing", "ok",
        f"one write to {CHUNKS} cleared {weigh(before)} from the cache")
    return True


def touch(base: str, token: str, uid: str) -> str:
    """Write one chunk row's own timestamp back to it. `""` when that worked.

    Its own value, because the row is derived from the repo and this script is
    not the indexer. The trigger under test is per statement rather than per
    row, so an `UPDATE` that changes nothing still fires it.
    """
    key = urllib.parse.quote(uid, safe="")
    got = call(f"{base}/api/database/records/{CHUNKS}"
               f"?uid=eq.{key}&select=uid,updated_at", token=token)
    if not got.ok:
        return why(got)
    if not got.data:
        return f"{uid} is not in the table"
    wrote = call(f"{base}/api/database/records/{CHUNKS}?uid=eq.{key}", token=token,
                 method="PATCH", body={"updated_at": got.data[0]["updated_at"]})
    return "" if wrote.ok else why(wrote)


def check_expansion(rep: Report, url: str) -> bool:
    """A transliteration reaches the English term, and the page is told so."""
    got, took = ask(url, {"q": EXPAND_Q, "limit": LIMIT})
    if not got.ok:
        rep("query expansion", "fail", f"“{EXPAND_Q}” failed: {why(got)}")
        return False
    terms = [str(t) for t in (got.data or {}).get("expanded") or []]
    if not terms:
        rep("query expansion", "off", f"“{EXPAND_Q}” was searched as it was typed",
            "PROBE_REWRITE_MODEL is unset in the function's environment, or the "
            "model timed out — the endpoint is correct without it, and the site "
            "prints no 읽은 뜻 line")
        return False
    flat = " ".join(terms).lower().replace("-", " ")
    if EXPAND_WANT not in flat:
        rep("query expansion", "warn",
            f"“{EXPAND_Q}” → {', '.join(terms[:6])}",
            f"the model answered but never named `{EXPAND_WANT}`, which is the "
            f"bridge this step exists for — try a stronger PROBE_REWRITE_MODEL")
        return False
    rep("query expansion", "ok",
        f"“{EXPAND_Q}” → {', '.join(terms[:6])} in {took} ms")
    return True


def check_lock(rep: Report, base: str, anon: str) -> bool:
    """The anon key the endpoint carries reads neither table directly.

    Locked reads two ways and both pass: no policy on a table the role may
    select from returns an empty set, and no grant at all is refused outright.
    What fails is a row — that key ships inside the page, so a row here is a
    row any reader can take, and the corpus goes in one request.
    """
    leaked = []
    shut = []
    for table, select in ((CHUNKS, "uid"), (CACHE, "q_norm")):
        got = call(f"{base}/api/database/records/{table}?select={select}&limit=1",
                   token=anon)
        if got.ok and got.data:
            leaked.append(f"{table} returned {len(got.data)} row(s)")
        elif got.ok:
            shut.append(f"{table} 0 rows")
        elif got.status in (401, 403):
            shut.append(f"{table} refused")
        else:
            rep("table lock", "fail", f"{table}: {why(got)}",
                "neither a row nor a refusal — the answer says nothing about the lock")
            return False
    if leaked:
        rep("table lock", "fail", "; ".join(leaked),
            "the anon key reads the corpus directly — row-level security is off "
            "on that table, or it carries a read policy; site/search/schema.sql "
            "enables the first and adds none of the second")
        return False
    rep("table lock", "ok", f"the anon key reads nothing — {', '.join(shut)}")
    return True


def anon_key(base: str, admin: str) -> tuple[str, str]:
    """The key the deployed function carries. `(key, problem)`."""
    key = os.environ.get("INSFORGE_ANON_KEY", "").strip()
    if key:
        return key, ""
    got = call(f"{base}/api/metadata/anon-key", token=admin)
    if not got.ok:
        return "", why(got)
    key = (got.data or {}).get("anonKey") or ""
    return (key, "") if key else ("", "the project reports no anon key")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("index", type=Path, help="JSONL from build-site.py --index")
    args = ap.parse_args()

    if not args.index.is_file():
        raise Fail(f"{args.index} does not exist — run: "
                   f"python3 site/build-site.py --index {args.index}")
    chunks = [json.loads(line) for line in
              args.index.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not chunks:
        raise Fail(f"{args.index} holds no chunks")
    want = {c["uid"]: c["content_hash"] for c in chunks}

    base = os.environ.get("INSFORGE_URL", "").rstrip("/")
    admin = os.environ.get("INSFORGE_API_KEY", "")
    url = os.environ.get("PROBE_SEARCH_API", "").strip()
    if not base or not admin or not url:
        raise Fail("set INSFORGE_URL, INSFORGE_API_KEY and PROBE_SEARCH_API")

    print(f"{base} · {url}")
    print(f"{len(want)} chunk(s) from {args.index}")
    rep = Report()

    indexed = cached = False
    if check_migration(rep, base, admin):
        indexed = check_index(rep, base, admin, want, args.index)
    else:
        rep("index", "skip", "needs a table to read")

    if check_endpoint(rep, url) is not None:
        cached = check_cache(rep, url, base, admin)
    else:
        rep("query cache", "skip", "needs an endpoint that answers")

    if cached and indexed:
        check_cache_clear(rep, base, admin, chunks[0]["uid"])
    else:
        rep("cache clearing", "skip", "needs a filled cache and a matching index")

    if cached:
        check_expansion(rep, url)
    else:
        rep("query expansion", "skip", "needs an endpoint that answers")

    key, problem = anon_key(base, admin)
    if key:
        check_lock(rep, base, key)
    else:
        rep("table lock", "skip", f"no anon key: {problem}",
            "set INSFORGE_ANON_KEY to the project's anon_... key")

    said = {"ok": "ok", "off": "off", "warn": "warned",
            "skip": "skipped", "fail": "failed"}
    print("verify: " + " · ".join(f"{rep.counts[k]} {said[k]}"
                                  for k in said if rep.counts[k]))
    return 1 if rep.counts["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
