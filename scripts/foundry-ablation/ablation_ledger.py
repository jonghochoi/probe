#!/usr/bin/env python3
"""Accumulate and aggregate foundry-ablation samples (PROTOCOL.md).

One JSONL record per paper-sample. `add` appends a validated record; `report`
aggregates the H_context verdict and the H_verify / form signals across all
logged papers.

    python3 scripts/foundry-ablation/ablation_ledger.py --schema
    python3 scripts/foundry-ablation/ablation_ledger.py add sample.json
    python3 scripts/foundry-ablation/ablation_ledger.py report

Per-paper H_context verdict from the a1-vs-a2 decision points:
  - context_pins    — some point upgraded ASSUMED->SPECIFIED (H_context supported)
  - context_shifts  — some value changed without an upgrade (ambiguous)
  - context_neutral — identical decisions (H_context refuted)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

LEDGER = Path(__file__).resolve().parent / "ledger.jsonl"

SCHEMA = """\
Record schema (JSON object):
{
  "id": "2511.00139",                  # arXiv id (required)
  "date": "2026-05-22",                # YYYY-MM-DD (required)
  "foundry": "lerobot",                # optional, default "lerobot"
  "decision_points": [                 # required, the a1-vs-a2 comparison
    {"name": "mlp_hidden_width",
     "a1_value": "d_s", "a1_status": "ASSUMED",
     "a2_value": "d_s", "a2_status": "ASSUMED"},
    ...
  ],
  "exec_verdict": "pass",              # optional: pass|fail|skipped (audit §🧬)
  "form": "subclass-seam",             # optional: subclass-seam|in-place
  "gold_ref": "lerobot:pi0_hetero",    # optional: reference impl, if any
  "notes": "..."                       # optional
}
status is one of SPECIFIED | ASSUMED. Values are short strings.
"""

VALID_STATUS = {"SPECIFIED", "ASSUMED"}


def load() -> list[dict]:
    if not LEDGER.is_file():
        return []
    out = []
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def validate(rec: dict) -> None:
    for key in ("id", "date", "decision_points"):
        if key not in rec:
            raise ValueError(f"record missing required key '{key}'")
    if not isinstance(rec["decision_points"], list) or not rec["decision_points"]:
        raise ValueError("decision_points must be a non-empty list")
    for p in rec["decision_points"]:
        for key in ("name", "a1_value", "a1_status", "a2_value", "a2_status"):
            if key not in p:
                raise ValueError(f"decision point missing '{key}': {p}")
        for s in (p["a1_status"], p["a2_status"]):
            if s not in VALID_STATUS:
                raise ValueError(f"status must be one of {VALID_STATUS}, got '{s}'")


def classify(rec: dict) -> str:
    """Per-paper H_context verdict from its decision points."""
    upgraded = any(
        p["a1_status"] == "ASSUMED" and p["a2_status"] == "SPECIFIED"
        for p in rec["decision_points"]
    )
    if upgraded:
        return "context_pins"
    shifted = any(p["a1_value"] != p["a2_value"] for p in rec["decision_points"])
    return "context_shifts" if shifted else "context_neutral"


def cmd_add(path: str) -> int:
    rec = json.loads(Path(path).read_text(encoding="utf-8"))
    validate(rec)
    with LEDGER.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"added {rec['id']} ({rec['date']}) — verdict: {classify(rec)}")
    return 0


def cmd_report() -> int:
    recs = load()
    if not recs:
        print("ledger empty — add samples first (see --schema).")
        return 0

    verdicts = {"context_pins": 0, "context_shifts": 0, "context_neutral": 0}
    print(f"{'id':<14} {'verdict':<16} {'exec':<8} {'form':<14} pts(chg/up)")
    print("-" * 64)
    for rec in recs:
        v = classify(rec)
        verdicts[v] += 1
        pts = rec["decision_points"]
        chg = sum(1 for p in pts if p["a1_value"] != p["a2_value"])
        up = sum(1 for p in pts if p["a1_status"] == "ASSUMED" and p["a2_status"] == "SPECIFIED")
        print(
            f"{rec['id']:<14} {v:<16} {rec.get('exec_verdict','-'):<8} "
            f"{rec.get('form','-'):<14} {len(pts)}({chg}/{up})"
        )

    n = len(recs)
    print("-" * 64)
    print(f"N = {n} papers")
    print(
        f"  H_context supported (context_pins):  {verdicts['context_pins']}"
        f"  ({verdicts['context_pins']/n:.0%})"
    )
    print(f"  ambiguous (context_shifts):          {verdicts['context_shifts']}")
    print(
        f"  H_context refuted (context_neutral):  {verdicts['context_neutral']}"
        f"  ({verdicts['context_neutral']/n:.0%})"
    )
    execs = {}
    forms = {}
    for rec in recs:
        execs[rec.get("exec_verdict", "-")] = execs.get(rec.get("exec_verdict", "-"), 0) + 1
        forms[rec.get("form", "-")] = forms.get(rec.get("form", "-"), 0) + 1
    print(f"  §🧬 exec verdicts: {execs}")
    print(f"  form:             {forms}")
    print()
    print("Reading: context_pins => richer context recovered a spec the design")
    print("dropped (H_context). context_neutral => design filtering lost nothing")
    print("for the tested points (H_verify/H_null favoured). Need several papers")
    print("before trusting the aggregate.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--schema", action="store_true", help="print the record schema and exit")
    sub = ap.add_subparsers(dest="cmd")
    p_add = sub.add_parser("add")
    p_add.add_argument("path", help="path to a JSON record")
    sub.add_parser("report")
    args = ap.parse_args()

    if args.schema:
        print(SCHEMA)
        return 0
    if args.cmd == "add":
        return cmd_add(args.path)
    if args.cmd == "report":
        return cmd_report()
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
