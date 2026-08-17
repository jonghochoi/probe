"""Minimal `---`-fenced front-matter parser.

`analysis/<id>.md` carries flat scalars plus one folded block (`summary: >`).
Pulling in PyYAML for that would add a dependency whose feature surface
(anchors, tags, implicit typing) is entirely unwanted here — a stray `yes`
becoming `True` is a real YAML footgun. Flat keys only; genuine nesting is
rejected rather than half-supported.

The one structure that IS supported is the block scalar, because the contract
in `site/AUTHORING.md` §1 requires it: `summary` is 2–3 sentences of Korean and
folding it over several lines is the only way to keep the front matter
readable.
"""

from __future__ import annotations

FENCE = "---"
_BLOCK = {">": " ", "|": "\n"}


def parse(text: str) -> tuple[dict[str, str], str]:
    """Return (front_matter, body). No fence → ({}, text)."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != FENCE:
        return {}, text

    front: dict[str, str] = {}
    block_key = ""      # key currently collecting a `>` / `|` block
    block_join = " "
    block_lines: list[str] = []

    def close_block() -> None:
        nonlocal block_key
        if block_key:
            front[block_key] = block_join.join(block_lines).strip()
            block_key = ""

    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == FENCE:
            close_block()
            return front, "\n".join(lines[i + 1:]).lstrip("\n")

        # Inside a block scalar, any indented line is content — including one
        # containing a colon, which the flat-key branch below would misread.
        if block_key and (not line.strip() or line[:1] in " \t"):
            block_lines.append(line.strip())
            continue
        close_block()

        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            raise ValueError(f"front-matter line is not `key: value`: {line!r}")
        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.strip()
        if not key or key.startswith("-"):
            raise ValueError(f"front-matter supports flat keys only: {line!r}")
        if value in _BLOCK:
            block_key, block_join, block_lines = key, _BLOCK[value], []
            continue
        front[key] = value.strip("'\"")

    raise ValueError("front-matter opened with `---` but never closed")



def as_list(value: str) -> list[str]:
    """`[a, b]` or `a, b` → `['a', 'b']`. Flow sequences only."""
    inner = (value or "").strip().lstrip("[").rstrip("]")
    return [item.strip().strip("'\"") for item in inner.split(",") if item.strip()]
