#!/usr/bin/env python3
"""Check that local path references in the contributor/agent docs resolve.

PROBE has no cross-link automation (CLAUDE.md → "When adding a new top-level
doc"): every doc reference is hand-maintained, and a restructure can silently
leave a dangling `context/MASTER.md`-style path or orphan a moved file. This
lint turns the manual "run a final grep" step of that checklist into a CI gate:
it scans a fixed doc set and verifies every LOCAL path reference points at a
file or directory that actually exists.

Two kinds of reference are checked:
  1. Markdown links `[text](relative/path)` whose target is local (not a URL or
     a pure `#anchor`). An explicit link is always checked.
  2. Backtick path tokens `` `dir/file.ext` `` — a backticked token that
     contains `/`, has no whitespace, carries a known file extension, and is
     free of glob/placeholder/URL syntax.

Precision over recall (deliberate, mirroring the repo's other gates): tokens
carrying placeholder or glob syntax are SKIPPED, not flagged, so the documented
patterns `context/P{1..4}.md`, `scouting/<PILLAR>/YYYY-MM-DD.md`,
`.claude/prompts/**`, `…/x1.png`, `arxiv.org/abs/...`, `cat:cs.RO`, shell
snippets, etc. do not produce false positives. Fenced code blocks (``` ... ```)
are skipped entirely. A token with no known file extension (a bare directory
fragment like `datasets/`, or an identifier like `cs.RO/x`) is treated as
non-concrete and skipped — only references to a concrete file are flagged.

A path resolves if it exists relative to the repo root OR relative to the
referencing doc's own directory (standard Markdown link semantics + the repo's
habit of citing root-relative paths in prose).

Usage (repo root):
    python3 scripts/check-doc-links.py [PATH ...]

No PATH -> scan the default doc set: the structural index docs `CLAUDE.md`
(its Repository-map table) and `README.md`, where every path reference is meant
to point at a real file. The agent-output spec (`docs/STYLE.md`) and the
prompts are out of the default set — they are full of *illustrative* example
paths (example arXiv ids, partial `impl/…` fragments) by design — but can be
scanned explicitly by passing them as PATH args.

Exit codes: 0 = clean / 1 = unresolved references found / 2 = nothing to scan.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Concrete file references we are confident enough about to flag when broken.
_KNOWN_EXTENSIONS = (
    ".md", ".py", ".sh", ".json", ".html", ".yml", ".yaml",
    ".patch", ".txt", ".png", ".svg", ".toml", ".cfg",
)

# A backtick token carrying any of these is a glob/placeholder/URL/command, not
# a concrete path we can resolve — skip it (precision guard). Includes the U+2026
# ellipsis used as an elision placeholder (`…/2604.../x1.png`).
_SKIP_CHARS = set("*<>{}#|=+$%@:` …")

_MD_LINK = re.compile(r"\[(?:[^\]]*)\]\(([^)]+)\)")
_BACKTICK = re.compile(r"`([^`]+)`")

# Default scan set: the structural index docs whose path references are meant to
# point at real files. STYLE.md / prompts are intentionally excluded (they carry
# illustrative example paths) but can be passed explicitly as PATH args.
_DEFAULT_DOCS = [
    "CLAUDE.md",
    "README.md",
]


def _resolves(candidate: str, doc_dir: str) -> bool:
    """True if candidate exists relative to the repo root or the doc's dir."""
    cand = candidate.rstrip("/")
    if not cand:
        return False
    for base in (_REPO_ROOT, doc_dir):
        if os.path.exists(os.path.join(base, cand)):
            return True
    return False


def _is_local_link_target(target: str) -> bool:
    t = target.strip()
    if not t or t.startswith("#"):
        return False
    lowered = t.lower()
    if "://" in lowered or lowered.startswith(("mailto:", "tel:")):
        return False
    return True


def _strip_link_target(target: str) -> str:
    """[text](path "title") / path#anchor / path?query -> bare path."""
    t = target.strip()
    # Drop an optional ` "title"` suffix.
    t = t.split(" ", 1)[0]
    t = t.split("#", 1)[0].split("?", 1)[0]
    return t


def _qualifies_as_path_token(tok: str) -> bool:
    if "/" not in tok:
        return False
    if any(c in _SKIP_CHARS for c in tok):
        return False
    return tok.lower().endswith(_KNOWN_EXTENSIONS)


def check_file(path: str) -> list[tuple[int, str]]:
    """Return a list of (line_number, unresolved_reference) for one doc."""
    abs_path = path if os.path.isabs(path) else os.path.join(_REPO_ROOT, path)
    doc_dir = os.path.dirname(abs_path)
    findings: list[tuple[int, str]] = []
    in_fence = False
    try:
        with open(abs_path, encoding="utf-8") as fh:
            lines = fh.readlines()
    except OSError as e:
        return [(0, f"<could not read: {e}>")]

    for lineno, line in enumerate(lines, start=1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        for m in _MD_LINK.finditer(line):
            target = m.group(1)
            if not _is_local_link_target(target):
                continue
            cand = _strip_link_target(target)
            if cand and not _resolves(cand, doc_dir):
                findings.append((lineno, cand))

        for m in _BACKTICK.finditer(line):
            tok = m.group(1).strip()
            if not _qualifies_as_path_token(tok):
                continue
            if not _resolves(tok, doc_dir):
                findings.append((lineno, tok))

    return findings


def _gather_default_docs() -> list[str]:
    return [d for d in _DEFAULT_DOCS if os.path.exists(os.path.join(_REPO_ROOT, d))]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check that local path references in PROBE docs resolve."
    )
    parser.add_argument("paths", nargs="*", help="docs to scan (default: the standard doc set)")
    args = parser.parse_args(argv)

    docs = args.paths or _gather_default_docs()
    if not docs:
        sys.stderr.write("[check-doc-links] nothing to scan\n")
        return 2

    total = 0
    for doc in docs:
        findings = check_file(doc)
        rel = os.path.relpath(os.path.join(_REPO_ROOT, doc), _REPO_ROOT) if not os.path.isabs(doc) else doc
        for lineno, ref in findings:
            total += 1
            print(f"{rel}:{lineno}: unresolved path reference -> {ref}")

    if total:
        print(f"\n[check-doc-links] {total} unresolved reference(s) across {len(docs)} doc(s)")
        return 1
    print(f"[check-doc-links] clean — {len(docs)} doc(s) scanned, all path references resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
