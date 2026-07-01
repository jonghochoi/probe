#!/usr/bin/env python3
"""supermemory PoC ingestor — PROBE `analysis/` corpus → supermemory documents.

Cut 1 of the integration in `docs/supermemory-integration.md`: build one
supermemory document per `analysis/<id>/analysis.md`, mapped to supermemory's
`customId` / `containerTags` / `metadata` fields (§2-3), and either emit them as
JSON (`--dry-run`) or POST them to a running server (`/v3/documents`).

The corpus parsing is shared with the deep-dive index via `probe_corpus`
(`build_analysis_doc`), so both read the `논문 메타` table identically.

Usage
-----
    # Offline — build docs and print JSON (no server needed). The only path
    # verifiable in a sandbox without a supermemory server.
    python3 scripts/supermemory_ingest.py --dry-run
    python3 scripts/supermemory_ingest.py --dry-run --id 2511.00139 --out /tmp/docs.json

    # Live — POST to a local `npx supermemory local` server (default :6767).
    # The server prints an `sm_...` key on first boot; pass it here or via
    # SUPERMEMORY_API_KEY.
    python3 scripts/supermemory_ingest.py --api-key sm_xxx
    python3 scripts/supermemory_ingest.py --base-url http://localhost:6767 --api-key sm_xxx

Notes
-----
- supermemory computes embeddings itself (self-host: built-in local model), so
  this script never touches an embedding provider — it only ships documents.
- Idempotent: re-POSTing the same `customId` upserts (§2), so re-running after a
  source edit refreshes just the changed papers.
- `context/` is never read or written here — cut 1 is `analysis/` only.
- The live `/v3/documents` request/response contract should be confirmed against
  a running server; wire-field names are centralized in `_wire_payload` below.

Specification: docs/supermemory-integration.md §2-3, docs/supermemory-poc-runbook.md.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

from probe_corpus import build_analysis_doc, find_analyses

DEFAULT_BASE_URL = "http://localhost:6767"


def _request(method: str, url: str, api_key: str | None, body: dict | None) -> tuple[int, dict]:
    """Issue a JSON HTTP request via stdlib urllib. Returns (status, parsed)."""
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8") or "{}"
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"raw": raw}
        return resp.status, parsed


def post_json(base_url: str, path: str, api_key: str | None, body: dict) -> tuple[int, dict]:
    return _request("POST", base_url.rstrip("/") + path, api_key, body)


def get_json(base_url: str, path: str, api_key: str | None) -> tuple[int, dict]:
    return _request("GET", base_url.rstrip("/") + path, api_key, None)


def _wire_payload(doc: dict) -> dict:
    """Map an internal doc dict to the `/v3/documents` request body.

    Field names are the one place the supermemory wire contract lives; confirm
    them against a running server before trusting the live path. `containerTags`
    carries the full pillar set (primary first) for cross-pollination filtering;
    the primary also lives in `metadata.pillars[0]`.
    """
    payload: dict = {"content": doc["content"], "metadata": doc["metadata"]}
    if doc.get("customId"):
        payload["customId"] = doc["customId"]
    if doc.get("containerTags"):
        payload["containerTags"] = doc["containerTags"]
    return payload


def build_docs(source: str, only_id: str | None) -> list[dict]:
    """Build supermemory documents for the requested source (cut 1: analysis)."""
    if source != "analysis":
        raise SystemExit(f"error: unsupported --source {source!r} (cut 1 supports 'analysis')")
    docs: list[dict] = []
    for paper_dir in find_analyses():
        if only_id and paper_dir.name != only_id:
            continue
        doc = build_analysis_doc(paper_dir)
        if doc is None:
            sys.stderr.write(f"skip: {paper_dir.name} (unreadable / no arXiv id)\n")
            continue
        docs.append(doc)
    return docs


def run_dry(docs: list[dict], out: str | None) -> int:
    """Emit the built documents as a JSON array (stdout or --out)."""
    text = json.dumps(docs, ensure_ascii=False, indent=2)
    if out:
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        sys.stderr.write(f"dry-run: wrote {len(docs)} docs → {out}\n")
    else:
        print(text)
        sys.stderr.write(f"dry-run: emitted {len(docs)} docs\n")
    return 0


def run_ingest(docs: list[dict], base_url: str, api_key: str | None) -> int:
    """POST each document to `{base_url}/v3/documents`."""
    ok = 0
    for doc in docs:
        cid = doc.get("customId", "?")
        try:
            status, resp = post_json(base_url, "/v3/documents", api_key, _wire_payload(doc))
        except urllib.error.HTTPError as exc:
            sys.stderr.write(f"FAIL {cid}: HTTP {exc.code} {exc.reason}\n")
            continue
        except urllib.error.URLError as exc:
            sys.stderr.write(
                f"FAIL {cid}: cannot reach {base_url} ({exc.reason}). "
                "Is `npx supermemory local` running?\n"
            )
            return 1  # server unreachable — no point continuing
        if 200 <= status < 300:
            ok += 1
            print(f"OK   {cid}  (HTTP {status})")
        else:
            sys.stderr.write(f"FAIL {cid}: HTTP {status} {resp}\n")
    sys.stderr.write(f"ingest: {ok}/{len(docs)} documents accepted by {base_url}\n")
    return 0 if ok == len(docs) else 1


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Ingest PROBE analyses into supermemory (PoC cut 1).")
    p.add_argument("--base-url", default=DEFAULT_BASE_URL,
                   help=f"supermemory server base URL (default {DEFAULT_BASE_URL})")
    p.add_argument("--dry-run", action="store_true",
                   help="build docs and emit JSON without contacting a server")
    p.add_argument("--out", default=None, help="write dry-run JSON to this file instead of stdout")
    p.add_argument("--source", default="analysis", choices=["analysis"],
                   help="corpus source to ingest (cut 1: analysis only)")
    p.add_argument("--id", dest="only_id", default=None,
                   help="limit to a single paper directory (e.g. 2511.00139)")
    p.add_argument("--api-key", default=os.environ.get("SUPERMEMORY_API_KEY"),
                   help="supermemory API key (or set SUPERMEMORY_API_KEY); "
                        "printed by `npx supermemory local` on first boot")
    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    docs = build_docs(args.source, args.only_id)
    if not docs:
        sys.stderr.write("no documents built — nothing to do\n")
        return 1
    if args.dry_run:
        return run_dry(docs, args.out)
    return run_ingest(docs, args.base_url, args.api_key)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
