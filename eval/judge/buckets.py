"""Rigor bucket utilities.

Ported verbatim from SoundnessBench `rigorbench/buckets.py` so this
harness reads the same low/high label space as the upstream benchmark
(lets a probe gold set and the SoundnessBench dataset be scored by the
identical pipeline).
"""

from __future__ import annotations

from typing import Any


BUCKET_LABELS: tuple[str, str] = ("low", "high")
BUCKET_SET = set(BUCKET_LABELS)


def normalize_bucket(label: Any) -> str | None:
    """Normalize arbitrary bucket label input to canonical labels."""
    if label is None:
        return None
    value = str(label).strip().lower()
    return value if value in BUCKET_SET else None
