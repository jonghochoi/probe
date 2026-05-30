#!/usr/bin/env python3
"""CLI for probe's soundness calibration harness.

Scores a labelled gold set with probe's soundness prompt and reports
accuracy + Cohen's kappa + the optimism (false-high) rate. Use
`--prompt compare` to A/B the neutral vs. skeptical prompt on the same
gold set and quantify the optimism-bias reduction.

Adapted from SoundnessBench `scripts/run_evaluation.py`.

Examples:
  # offline smoke run, no API key (chance-level reference):
  python scripts/run-soundness-eval.py --provider random --prompt compare

  # calibrate the skeptical prompt on the seed gold set:
  python scripts/run-soundness-eval.py --prompt skeptical \
      --output eval/results/skeptical.json

  # bootstrap against the sibling SoundnessBench dataset (1,099 labels):
  python scripts/run-soundness-eval.py --prompt compare \
      --gold ../SoundnessBench/data/soundnessbench.jsonl \
      --output-dir eval/results --limit 200
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EVAL_DIR = REPO_ROOT / "eval"
sys.path.insert(0, str(EVAL_DIR))

from judge.client import get_llm_client  # noqa: E402
from judge.run import compare_prompts, run_calibration  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="probe soundness calibration harness")
    parser.add_argument(
        "--gold",
        default=str(EVAL_DIR / "data" / "gold.jsonl"),
        help="Path to the gold JSONL (SoundnessBench schema). Default: eval/data/gold.jsonl",
    )
    parser.add_argument(
        "--prompt",
        choices=["neutral", "skeptical", "compare"],
        default="compare",
        help="Prompt variant, or 'compare' to A/B both. Default: compare",
    )
    parser.add_argument("--provider", default=None, help="Override provider (openai|anthropic|gemini|vllm|random)")
    parser.add_argument("--model", default=None, help="Override model name")
    parser.add_argument("--output", default=None, help="Output JSON path (single-variant runs)")
    parser.add_argument("--output-dir", default=None, help="Output dir (compare runs)")
    parser.add_argument("--limit", type=int, default=None, help="Cap the number of gold examples")
    parser.add_argument("--delay", type=float, default=0.0, help="Seconds to sleep between calls")
    args = parser.parse_args()

    def make_client():
        return get_llm_client(provider=args.provider, model=args.model)

    if args.prompt == "compare":
        comparison = compare_prompts(
            args.gold,
            client_factory=make_client,
            output_dir=args.output_dir,
            limit=args.limit,
            delay_seconds=args.delay,
        )
        print(json.dumps(comparison, indent=2, ensure_ascii=False))
    else:
        results = run_calibration(
            args.gold,
            variant=args.prompt,
            client=make_client(),
            output_path=args.output,
            limit=args.limit,
            delay_seconds=args.delay,
        )
        print(
            json.dumps(
                {"prompt_variant": results["prompt_variant"], **results["metrics"]["summary"], "optimism": results["optimism"]},
                indent=2,
                ensure_ascii=False,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
