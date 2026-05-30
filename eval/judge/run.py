"""Calibration runner — measure probe's soundness prompt against a gold set.

Adapted from SoundnessBench `rigorbench/evaluation/run.py`: gold loading,
the robust JSON-extraction parser (`_parse_prediction`), and the scoring
loop. Reframed from "benchmark a model" to "calibrate probe's soundness
prompt": it scores a labelled gold set with the neutral or skeptical
prompt, reports accuracy + Cohen's kappa + the optimism (false-high)
metric, and `compare_prompts` runs both for the A/B verdict.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

from .buckets import normalize_bucket
from .client import LLMClient, get_llm_client
from .metrics import compute_bucket_metrics, optimism_metrics
from .prompts import build_messages


def load_gold(path: str | Path) -> list[dict[str, Any]]:
    """Load gold examples from a JSONL file (SoundnessBench schema)."""
    rows: list[dict[str, Any]] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _pair_text(row: dict[str, Any]) -> tuple[str, str]:
    hypothesis = str(row.get("short_hypothesis") or row.get("hypothesis") or "").strip()
    experiment = str(row.get("experiment") or "").strip()
    if not experiment and row.get("experiments"):
        # Flatten a list of structured experiments into plain text.
        parts: list[str] = []
        for i, exp in enumerate(row.get("experiments") or [], start=1):
            if isinstance(exp, dict):
                body = "; ".join(f"{k}: {v}" for k, v in exp.items())
            else:
                body = str(exp)
            parts.append(f"Experiment {i}: {body}")
        experiment = "\n".join(parts)
    return hypothesis, experiment


def _strip_markdown_fences(text: str) -> str:
    return re.sub(r"```(?:json)?\s*", "", text).replace("```", "").strip()


def _extract_first_json_object(text: str) -> str | None:
    text = _strip_markdown_fences(text)
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    for idx in range(start, len(text)):
        if text[idx] == "{":
            depth += 1
        elif text[idx] == "}":
            depth -= 1
            if depth == 0:
                return text[start : idx + 1]
    return None


def _clamp_confidence(value: Any) -> int | None:
    try:
        return int(round(max(1.0, min(5.0, float(value)))))
    except (TypeError, ValueError):
        return None


def _parse_prediction(response: str) -> dict[str, Any]:
    """Parse model JSON into {rigor_bucket, confidence, justification}."""
    parsed: dict[str, Any] = {"rigor_bucket": None, "confidence": None, "justification": None}
    raw = _extract_first_json_object(response)
    if raw is None:
        return parsed
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        bucket_match = re.search(r'"(?:rigor_bucket|bucket)"\s*:\s*"([^"]+)"', raw, flags=re.IGNORECASE)
        conf_match = re.search(r'"(?:confidence|reviewer_confidence)"\s*:\s*([-+]?\d+(?:\.\d+)?)', raw)
        if bucket_match:
            parsed["rigor_bucket"] = normalize_bucket(bucket_match.group(1))
        if conf_match:
            parsed["confidence"] = _clamp_confidence(conf_match.group(1))
        return parsed

    parsed["rigor_bucket"] = normalize_bucket(obj.get("rigor_bucket", obj.get("bucket")))
    parsed["confidence"] = _clamp_confidence(obj.get("confidence", obj.get("reviewer_confidence")))
    justification = obj.get("justification")
    if isinstance(justification, str) and justification.strip():
        parsed["justification"] = justification.strip()
    return parsed


def run_calibration(
    gold_path: str | Path,
    variant: str = "skeptical",
    client: LLMClient | None = None,
    output_path: str | Path | None = None,
    limit: int | None = None,
    delay_seconds: float = 0.0,
) -> dict[str, Any]:
    """Score a gold set with one prompt variant; return metrics + rows."""
    if client is None:
        client = get_llm_client()

    rows = load_gold(gold_path)
    if limit is not None and limit > 0:
        rows = rows[:limit]

    predictions: list[dict[str, Any]] = []
    ground_truths: list[dict[str, Any]] = []
    result_rows: list[dict[str, Any]] = []

    for idx, row in enumerate(rows):
        hypothesis, experiment = _pair_text(row)
        gt = {
            "rigor_bucket": row.get("rigor_bucket"),
            "soundness_score": row.get("soundness_score"),
        }
        try:
            if delay_seconds > 0:
                time.sleep(delay_seconds)
            response = client.chat(
                build_messages(hypothesis, experiment, variant),
                temperature=0.2,
                max_tokens=getattr(client, "max_tokens", 2048) or 2048,
            )
            pred = _parse_prediction(response)
        except Exception as exc:  # noqa: BLE001
            pair_id = row.get("pair_id") or f"row_{idx}"
            print(f"[calib][error] variant={variant} pair_id={pair_id}: {exc}")
            pred = {"rigor_bucket": None, "confidence": None, "justification": None}

        predictions.append(pred)
        ground_truths.append(gt)
        result_rows.append(
            {
                "pair_id": row.get("pair_id") or f"row_{idx}",
                "prediction": pred,
                "ground_truth": gt,
            }
        )

    bucket_metrics = compute_bucket_metrics(predictions, ground_truths)
    optimism = optimism_metrics(predictions, ground_truths)

    results = {
        "prompt_variant": variant,
        "model": getattr(client, "model", None),
        "n_examples": len(rows),
        "gold_path": str(gold_path),
        "metrics": bucket_metrics,
        "optimism": optimism,
        "results": result_rows,
    }

    if output_path is not None:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Results written to {out}")

    return results


def compare_prompts(
    gold_path: str | Path,
    client_factory=get_llm_client,
    output_dir: str | Path | None = None,
    limit: int | None = None,
    delay_seconds: float = 0.0,
) -> dict[str, Any]:
    """Run neutral + skeptical on the same gold set and report the delta."""
    summaries: dict[str, Any] = {}
    for variant in ("neutral", "skeptical"):
        out = None
        if output_dir is not None:
            out = Path(output_dir) / f"calibration_{variant}.json"
        res = run_calibration(
            gold_path,
            variant=variant,
            client=client_factory(),
            output_path=out,
            limit=limit,
            delay_seconds=delay_seconds,
        )
        summaries[variant] = {
            "accuracy": res["metrics"]["summary"]["rigor_bucket_accuracy"],
            "cohen_kappa": res["metrics"]["summary"]["rigor_bucket_kappa"],
            "false_high_rate": res["optimism"]["false_high_rate"],
            "n": res["metrics"]["summary"]["total_n"],
        }

    neu = summaries["neutral"]["false_high_rate"]
    skp = summaries["skeptical"]["false_high_rate"]
    delta = (neu - skp) if (neu is not None and skp is not None) else None
    comparison = {
        "per_variant": summaries,
        "false_high_rate_reduction": delta,
        "verdict": (
            "skeptical reduces optimism bias"
            if (delta is not None and delta > 0)
            else "no reduction measured"
        ),
    }

    if output_dir is not None:
        out = Path(output_dir) / "calibration_comparison.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(comparison, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Comparison written to {out}")

    return comparison
