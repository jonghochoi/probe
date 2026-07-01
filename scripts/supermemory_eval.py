#!/usr/bin/env python3
"""supermemory PoC — Korean retrieval-quality eval (§6 risk #1).

Korean embedding recall is the #1 risk (docs/supermemory-poc-runbook.md §3):
PROBE bodies are dense Korean, and self-hosted supermemory embeds with a
built-in local model the user can't swap. Before committing to full indexing,
measure it.

This harness runs a small, hand-picked set of Korean concept queries — each
tied to the one `analysis/<id>` that should answer it — against a running
supermemory server (`/v3/search`) and reports the rank at which the expected
document was retrieved, plus hit@1/@3/@5 and MRR. A low score is the go/no-go
signal to escalate to the hosted tier (§5.2) rather than a code bug.

Live-only: it needs a server with the corpus already ingested
(`supermemory_ingest.py`). In a sandbox with no server it will report the
connection failure and exit non-zero — that is expected; run it in the
environment where `npx supermemory local` is up.

Usage
-----
    python3 scripts/supermemory_eval.py --api-key sm_xxx
    python3 scripts/supermemory_eval.py --base-url http://localhost:6767 --top-k 10
    python3 scripts/supermemory_eval.py --queries my_queries.json   # override the set

Query file (optional): JSON array of {"query": "...", "expect": "<arxiv-id>"}.

Specification: docs/supermemory-poc-runbook.md §3.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error

from supermemory_ingest import DEFAULT_BASE_URL, post_json

# Hand-picked Korean concept queries → the single analysis that should answer
# each. Grounded in the current corpus (titles/tags); concepts are distinctive
# enough that the right paper is unambiguous. Keep this small — it is a PoC
# measurement, not a benchmark suite.
DEFAULT_QUERIES: list[dict] = [
    {"query": "촉각을 action expert 에 적응적으로 주입해 피드백 반응을 높이는 방법",
     "expect": "2605.07308"},   # AT-VLA: Adaptive Tactile Injection
    {"query": "모달리티별 비동기 처리로 force 를 gated cross-attention 으로 주입하는 VLA",
     "expect": "2606.12105"},   # DAM-VLA: Decoupled Asynchronous Multimodal
    {"query": "VR 원격조작과 자율 손 VLA 를 결합한 shared autonomy 데이터 수집",
     "expect": "2511.00139"},   # Shared-Autonomy Arm-Hand VLA
    {"query": "contact 기반 flow matching 으로 힘을 느끼고 행동하는 정책",
     "expect": "2605.11048"},   # ForceFlow: Contact-Driven Flow Matching
    {"query": "손 상태를 양자화해서 dexterous manipulation 을 학습",
     "expect": "2509.17450"},   # Quantized Hand State
    {"query": "LoRA 가 덜 배우지만 덜 잊는다는 파인튜닝 분석",
     "expect": "2405.09673"},   # LoRA Learns Less and Forgets Less
    {"query": "flow policy 를 test-time 에 gradient 로 유도하는 강화학습",
     "expect": "2606.11087"},   # Test-Time Gradient Guidance of Flow Policies
    {"query": "body 와 hand prior 를 조율하는 휴머노이드 loco-manipulation",
     "expect": "2606.23680"},   # CoorDex: Coordinating Body and Hand Priors
    {"query": "단안 사람 영상으로부터 양손 dexterous manipulation 을 모방 학습",
     "expect": "2602.10105"},   # DexImit: Monocular Human Videos
    {"query": "force 로 유도되는 촉각 world model 로 contact-rich manipulation",
     "expect": "2606.11184"},   # TacForeSight: Force-Guided Tactile World Model
]


def _extract_custom_ids(resp: dict) -> list[str]:
    """Best-effort ordered list of `customId`s from a /v3/search response.

    Tolerant of the exact response shape (confirm against a running server):
    scans the first list value under common keys, pulling a customId from each
    item directly or from its metadata (arXiv id → `arxiv:<id>`).
    """
    items = None
    for key in ("results", "documents", "memories", "matches", "data"):
        val = resp.get(key)
        if isinstance(val, list):
            items = val
            break
    if items is None:
        return []
    ids: list[str] = []
    for it in items:
        if not isinstance(it, dict):
            continue
        cid = it.get("customId") or it.get("custom_id") or it.get("documentCustomId")
        if not cid:
            meta = it.get("metadata") or {}
            if isinstance(meta, dict):
                cid = meta.get("customId") or (
                    f"arxiv:{meta['arxiv_id']}" if meta.get("arxiv_id") else None
                )
        ids.append(cid or "")
    return ids


def _rank_of(expected_cid: str, retrieved: list[str]) -> int | None:
    for i, cid in enumerate(retrieved, 1):
        if cid == expected_cid:
            return i
    return None


def run_eval(queries: list[dict], base_url: str, api_key: str | None, top_k: int) -> int:
    ranks: list[int | None] = []
    print(f"eval: {len(queries)} queries against {base_url} (top-{top_k})\n")
    for q in queries:
        expected = f"arxiv:{q['expect']}"
        body = {"q": q["query"], "limit": top_k}
        try:
            status, resp = post_json(base_url, "/v3/search", api_key, body)
        except urllib.error.URLError as exc:
            sys.stderr.write(
                f"cannot reach {base_url} ({exc.reason}). "
                "Ingest first and ensure the server is running.\n"
            )
            return 1
        if not (200 <= status < 300):
            sys.stderr.write(f"search failed: HTTP {status} {resp}\n")
            return 1
        retrieved = _extract_custom_ids(resp)
        rank = _rank_of(expected, retrieved)
        ranks.append(rank)
        tag = f"#{rank}" if rank else "MISS"
        print(f"  [{tag:>5}] {q['expect']}  ← {q['query']}")

    n = len(ranks)
    hit1 = sum(1 for r in ranks if r and r <= 1)
    hit3 = sum(1 for r in ranks if r and r <= 3)
    hit5 = sum(1 for r in ranks if r and r <= 5)
    mrr = sum(1.0 / r for r in ranks if r) / n if n else 0.0
    print(
        f"\nsummary: hit@1={hit1}/{n}  hit@3={hit3}/{n}  hit@5={hit5}/{n}  "
        f"MRR={mrr:.3f}"
    )
    return 0


def load_queries(path: str | None) -> list[dict]:
    if not path:
        return DEFAULT_QUERIES
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list) or not all("query" in d and "expect" in d for d in data):
        raise SystemExit(f"error: {path} must be a JSON array of {{query, expect}} objects")
    return data


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Measure Korean retrieval quality (PoC §6 gate).")
    p.add_argument("--base-url", default=DEFAULT_BASE_URL,
                   help=f"supermemory server base URL (default {DEFAULT_BASE_URL})")
    p.add_argument("--top-k", type=int, default=10, help="results per query (default 10)")
    p.add_argument("--queries", default=None,
                   help="JSON file overriding the inline query set")
    p.add_argument("--api-key", default=os.environ.get("SUPERMEMORY_API_KEY"),
                   help="supermemory API key (or set SUPERMEMORY_API_KEY)")
    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    queries = load_queries(args.queries)
    return run_eval(queries, args.base_url, args.api_key, args.top_k)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
