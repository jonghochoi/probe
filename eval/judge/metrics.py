"""Metrics for probe's binary soundness (rigor-bucket) calibration.

`cohen_kappa` and `compute_bucket_metrics` are ported from SoundnessBench
`rigorbench/evaluation/metrics.py`. `optimism_metrics` is new: it reports
the false-"high" rate on gold-`low` items — the direct, quantitative
signal of the optimism bias the skeptical gate is meant to reduce.
"""

from __future__ import annotations

from typing import Any

from .buckets import normalize_bucket


def cohen_kappa(y_pred: list[str], y_true: list[str]) -> float | None:
    """Compute Cohen's kappa for categorical labels."""
    n = len(y_pred)
    if n != len(y_true) or n < 2:
        return None
    labels = sorted(set(y_true) | set(y_pred))
    observed = sum(p == g for p, g in zip(y_pred, y_true)) / n
    expected = sum((y_pred.count(label) / n) * (y_true.count(label) / n) for label in labels)
    if expected == 1.0:
        return 1.0
    return (observed - expected) / (1.0 - expected)


def compute_bucket_metrics(
    predictions: list[dict[str, Any]],
    ground_truths: list[dict[str, Any]],
    bucket_key: str = "rigor_bucket",
) -> dict[str, Any]:
    """Return accuracy and Cohen's kappa for normalized rigor_bucket labels."""
    pairs: list[tuple[str, str]] = []
    for pred, gt in zip(predictions, ground_truths):
        pred_bucket = normalize_bucket(pred.get(bucket_key))
        gt_bucket = normalize_bucket(gt.get(bucket_key))
        if pred_bucket is not None and gt_bucket is not None:
            pairs.append((pred_bucket, gt_bucket))

    n = len(pairs)
    if n == 0:
        accuracy = None
        kappa = None
    else:
        pred_vals = [p for p, _ in pairs]
        gt_vals = [g for _, g in pairs]
        accuracy = sum(p == g for p, g in pairs) / n
        kappa = cohen_kappa(pred_vals, gt_vals)

    return {
        "per_field": {
            bucket_key: {
                "n": n,
                "accuracy": accuracy,
                "cohen_kappa": kappa,
            }
        },
        "summary": {
            "rigor_bucket_accuracy": accuracy,
            "rigor_bucket_kappa": kappa,
            "total_n": n,
        },
    }


def optimism_metrics(
    predictions: list[dict[str, Any]],
    ground_truths: list[dict[str, Any]],
    bucket_key: str = "rigor_bucket",
) -> dict[str, Any]:
    """Quantify optimism bias on gold-`low` items.

    The optimism bias is over-rating unsound work as sound, i.e. predicting
    "high" where the gold label is "low". `false_high_rate` is exactly that
    error rate; the skeptical prompt should drive it down relative to the
    neutral prompt. `low_recall` is the complement (correctly held at low).
    """
    n_low = 0
    false_high = 0
    for pred, gt in zip(predictions, ground_truths):
        gt_bucket = normalize_bucket(gt.get(bucket_key))
        pred_bucket = normalize_bucket(pred.get(bucket_key))
        if gt_bucket != "low" or pred_bucket is None:
            continue
        n_low += 1
        if pred_bucket == "high":
            false_high += 1

    false_high_rate = (false_high / n_low) if n_low else None
    low_recall = (1.0 - false_high_rate) if false_high_rate is not None else None
    return {
        "n_gold_low": n_low,
        "false_high": false_high,
        "false_high_rate": false_high_rate,
        "low_recall": low_recall,
    }
