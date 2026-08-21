#!/usr/bin/env python3
"""Embed the search index and upload it to InsForge.

    python3 site/build-site.py --index .search/index.jsonl   # no network
    python3 site/search/indexer.py .search/index.jsonl --dry-run
    python3 site/search/indexer.py .search/index.jsonl

The split is deliberate: chunking runs in CI with no key and no egress, and
this half is the only thing that needs either. Stdlib only — the build's
`requirements.txt` covers pages, not this.

Re-running is cheap. Every chunk carries a `content_hash`, so a run embeds only
what changed and deletes only what left the corpus; a rewrite that gained one
section costs one embedding, not a corpus.

Environment:
    INSFORGE_URL        https://<project>.insforge.app
    INSFORGE_API_KEY    admin or project API key — writes the table
    OPENROUTER_API_KEY  optional; fetched from InsForge when unset
    PROBE_EMBED_MODEL   default openai/text-embedding-3-small (1536 dims)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

TABLE = "probe_chunks"
MODEL = os.environ.get("PROBE_EMBED_MODEL", "openai/text-embedding-3-small")
DIMS = 1536
# Batches keep the request count down without making one failure expensive.
EMBED_BATCH = 64
# A row carries its 1536-float embedding, so it serialises to about 22 KB and a
# write batch is sized by bytes rather than rows: 50 rows is ~1.6 MB, which the
# records endpoint accepts, and 100 is ~3.2 MB, which it drops mid-body as a
# 500 "socket hang up" that no amount of retrying gets past.
WRITE_BATCH = 50


class Fail(SystemExit):
    def __init__(self, msg: str):
        super().__init__(f"error: {msg}")


def _call(url: str, *, token: str, method: str = "GET", body=None,
          headers: dict | None = None, retries: int = 4):
    """One JSON call, with backoff on the failures that pass by themselves."""
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=120) as res:
                raw = res.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as exc:
            # 429 and 5xx are the upstream asking for a moment; 4xx is us.
            if exc.code not in (429, 500, 502, 503, 504) or attempt == retries - 1:
                raise Fail(f"{method} {url} → HTTP {exc.code}: "
                           f"{exc.read()[:400].decode(errors='replace')}")
            time.sleep(2 ** attempt)
        except urllib.error.URLError as exc:
            if attempt == retries - 1:
                raise Fail(f"{method} {url} → {exc.reason}")
            time.sleep(2 ** attempt)
    return None


def openrouter_key(base: str, token: str) -> str:
    """The key InsForge provisions, so the repo stores no provider credential."""
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if key:
        return key
    got = _call(f"{base}/api/ai/openrouter/api-key", token=token) or {}
    key = got.get("apiKey") or got.get("api_key") or got.get("key") or ""
    if not key:
        raise Fail("no OpenRouter key — set OPENROUTER_API_KEY, or provision one "
                   "in the InsForge dashboard under Model Gateway")
    return key


def embed(texts: list[str], key: str) -> list[list[float]]:
    out: list[list[float]] = []
    for start in range(0, len(texts), EMBED_BATCH):
        batch = texts[start:start + EMBED_BATCH]
        got = _call("https://openrouter.ai/api/v1/embeddings", token=key,
                    method="POST",
                    body={"model": MODEL, "input": batch, "dimensions": DIMS})
        rows = sorted(got["data"], key=lambda r: r["index"])
        if len(rows) != len(batch):
            raise Fail(f"embeddings returned {len(rows)} vectors for {len(batch)} inputs")
        out += [r["embedding"] for r in rows]
        print(f"  embedded {start + len(batch)}/{len(texts)}", flush=True)
    return out


def existing(base: str, token: str) -> dict[str, str]:
    """`{uid: content_hash}` already in the table."""
    out: dict[str, str] = {}
    page = 0
    while True:
        rows = _call(f"{base}/api/database/records/{TABLE}"
                     f"?select=uid,content_hash&limit=1000&offset={page * 1000}",
                     token=token) or []
        out.update({r["uid"]: r["content_hash"] for r in rows})
        if len(rows) < 1000:
            return out
        page += 1


def row_of(chunk: dict, vector: list[float]) -> dict:
    return {
        "uid": chunk["uid"], "kind": chunk["kind"],
        "paper_id": chunk["paper_id"], "title": chunk["title"],
        "context": chunk["context"], "path": chunk["path"],
        "anchor": chunk["anchor"], "pillars": chunk["pillars"],
        "tags": chunk["tags"], "chunk_date": chunk["date"] or None,
        "body": chunk["text"], "content_hash": chunk["content_hash"],
        "embedding": vector,
    }


def write(base: str, token: str, rows: list[dict], drop: list[str]) -> None:
    """Replace what changed and remove what left.

    Delete-then-insert rather than an upsert header: the rows are fully derived
    from the repo, so the two are equivalent, and this way the write does not
    depend on a `Prefer:` header surviving the proxy.
    """
    for start in range(0, len(drop), WRITE_BATCH):
        ids = ",".join(f'"{uid}"' for uid in drop[start:start + WRITE_BATCH])
        _call(f"{base}/api/database/records/{TABLE}?uid=in.({ids})",
              token=token, method="DELETE")
    for start in range(0, len(rows), WRITE_BATCH):
        _call(f"{base}/api/database/records/{TABLE}", token=token,
              method="POST", body=rows[start:start + WRITE_BATCH])
        print(f"  wrote {min(start + WRITE_BATCH, len(rows))}/{len(rows)}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("index", type=Path, help="JSONL from build-site.py --index")
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would be embedded; touch no network")
    ap.add_argument("--full", action="store_true",
                    help="re-embed every chunk, ignoring content hashes")
    args = ap.parse_args()

    chunks = [json.loads(line) for line in
              args.index.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not chunks:
        raise Fail(f"{args.index} holds no chunks")
    kinds = Counter(c["kind"] for c in chunks)
    chars = sum(len(c["text"]) for c in chunks)
    print(f"{len(chunks)} chunk(s) · {chars // 1000} K chars · "
          f"{len({c['paper_id'] for c in chunks if c['paper_id']})} paper(s)")
    print("  " + " ".join(f"{k}={n}" for k, n in kinds.most_common()))

    if args.dry_run:
        # A rough figure, and rough is enough: it exists to make the cost of a
        # full re-index visible before someone runs one in CI. Korean runs
        # about 1.2 characters to the token, so the four-to-one ratio English
        # gets would report a third of what this corpus actually costs.
        print(f"dry run — would embed {len(chunks)} chunk(s) with {MODEL} "
              f"(~{chars // 1200}K tokens)")
        return 0

    base = os.environ.get("INSFORGE_URL", "").rstrip("/")
    token = os.environ.get("INSFORGE_API_KEY", "")
    if not base or not token:
        raise Fail("set INSFORGE_URL and INSFORGE_API_KEY")

    have = {} if args.full else existing(base, token)
    fresh = [c for c in chunks if have.get(c["uid"]) != c["content_hash"]]
    gone = sorted(set(have) - {c["uid"] for c in chunks})
    print(f"{len(fresh)} new or changed · {len(gone)} removed · "
          f"{len(chunks) - len(fresh)} unchanged")
    if not fresh and not gone:
        print("index is current")
        return 0

    vectors = embed([c["text"] for c in fresh], openrouter_key(base, token)) if fresh else []
    write(base, token, [row_of(c, v) for c, v in zip(fresh, vectors)],
          gone + [c["uid"] for c in fresh])
    print(f"indexer: {len(fresh)} written · {len(gone)} dropped → {base}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
