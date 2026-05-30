"""Soundness prompt loading and message building.

The prompt markdown files (`eval/prompts/soundness_{neutral,skeptical}.md`)
follow SoundnessBench's two-section convention — a `## System prompt`
block and a `## User prompt template` block with `{hypothesis}` /
`{experiment}` placeholders — so the same dataset schema scores under
either variant. `neutral` and `skeptical` differ ONLY in rigor policy,
which is what makes the A/B comparison clean.
"""

from __future__ import annotations

import re
from pathlib import Path

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"

PROMPT_VARIANTS = {
    "neutral": "soundness_neutral.md",
    "skeptical": "soundness_skeptical.md",
}


def _split_sections(text: str) -> tuple[str, str]:
    """Split a prompt markdown into (system, user-template) bodies."""
    sys_match = re.search(r"##\s*System prompt\s*\n(.*?)(?=\n##\s|\Z)", text, flags=re.DOTALL)
    usr_match = re.search(r"##\s*User prompt template\s*\n(.*?)(?=\n##\s|\Z)", text, flags=re.DOTALL)
    if not sys_match or not usr_match:
        raise ValueError("Prompt file must contain '## System prompt' and '## User prompt template' sections")
    return sys_match.group(1).strip(), usr_match.group(1).strip()


def load_prompt(variant: str) -> tuple[str, str]:
    """Return (system_prompt, user_template) for a named variant."""
    if variant not in PROMPT_VARIANTS:
        raise ValueError(f"Unknown prompt variant '{variant}'. Use one of: {sorted(PROMPT_VARIANTS)}")
    path = PROMPT_DIR / PROMPT_VARIANTS[variant]
    return _split_sections(path.read_text(encoding="utf-8"))


def build_messages(hypothesis: str, experiment: str, variant: str) -> list[dict[str, str]]:
    """Build the chat messages for one hypothesis-experiment pair."""
    system_prompt, user_template = load_prompt(variant)
    user_prompt = user_template.replace("{hypothesis}", hypothesis).replace("{experiment}", experiment)
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
