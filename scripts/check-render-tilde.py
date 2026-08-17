#!/usr/bin/env python3
"""Report prose tildes that pair into a GitHub strikethrough (docs/style.md §4-6).

Scope is the github.com-rendered track — `scouting/`. The reading site
(`analysis/`) is not one: its parser needs the doubled `~~`, so a pair of single
tildes renders literally there and this is not a defect to report.

GitHub's strikethrough extension accepts a SINGLE `~`, not just the doubled
`~~`. Two raw tildes in the same inline context therefore strike out every
character between them on the rendered page — invisible in the source and in
CommonMark previews, visible only on github.com.

This linter reports exactly that condition: >= 2 raw tildes in one inline
context (paragraph / list item / table cell / blockquote line). A lone tilde
renders literally and is not an error.

Contexts where `~` is legitimate are excluded, because they are parsed before
the strikethrough scan or are not rendered at all:
  - fenced code blocks and inline code spans (incl. `$`math`$`)
  - display math `$$…$$` (LaTeX `~` is a non-breaking space)
  - HTML comments

Usage:
    python3 scripts/check-render-tilde.py [paths ...]

Exit status is 1 when any pairing context is found, 0 otherwise.
"""

from __future__ import annotations

import argparse
import glob
import re
import sys

DEFAULT_GLOBS = (
    "scouting/**/*.md",
)

FENCE_RE = re.compile(r"^\s*(```|~~~)")
CODE_SPAN_RE = re.compile(r"`[^`]*`")
DISPLAY_MATH_RE = re.compile(r"^\s*\$\$.*\$\$\s*$")
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
LIST_ITEM_RE = re.compile(r"^\s*([-*+]|\d+\.)\s")


def _blank_out_comments(text: str) -> str:
    """Replace HTML comments with spaces, preserving line numbering."""
    return COMMENT_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def inline_contexts(text: str):
    """Yield (lineno, context_text) for each span GitHub parses as one inline run."""
    lines, in_fence = [], False
    for line in _blank_out_comments(text).split("\n"):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            lines.append("")
            continue
        if in_fence:
            lines.append("")
            continue
        line = CODE_SPAN_RE.sub("", line)
        if DISPLAY_MATH_RE.match(line):
            line = ""
        lines.append(line)

    buf, start = [], 0
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("|"):  # table row — each cell is its own run
            if buf:
                yield start, "\n".join(buf)
                buf, start = [], 0
            for cell in line.split("|"):
                yield i, cell
            continue
        breaks = (
            LIST_ITEM_RE.match(line)
            or line.startswith("#")
            or line.strip().startswith(">")
        )
        if not line.strip() or breaks:
            if buf:
                yield start, "\n".join(buf)
            buf, start = ([line], i) if (breaks and line.strip()) else ([], 0)
        else:
            if not buf:
                start = i
            buf.append(line)
    if buf:
        yield start, "\n".join(buf)


def scan(paths):
    findings, singles = [], 0
    for path in paths:
        try:
            text = open(path, encoding="utf-8").read()
        except OSError as exc:  # unreadable file is a finding, not a crash
            print(f"{path}: cannot read ({exc})", file=sys.stderr)
            continue
        for lineno, ctx in inline_contexts(text):
            count = ctx.count("~")
            if count >= 2:
                excerpt = " ".join(ctx.split())[:90]
                findings.append((path, lineno, count, excerpt))
            elif count == 1:
                singles += 1
    return findings, singles


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="*", help="files or dirs to scan")
    args = ap.parse_args()

    if args.paths:
        paths = []
        for p in args.paths:
            paths.extend(glob.glob(f"{p}/**/*.md", recursive=True) if "*" not in p else glob.glob(p, recursive=True))
            if p.endswith(".md"):
                paths.append(p)
    else:
        paths = [f for g in DEFAULT_GLOBS for f in glob.glob(g, recursive=True)]
    paths = sorted(set(paths))

    findings, singles = scan(paths)

    for path, lineno, count, excerpt in findings:
        print(f"{path}:{lineno} — {count} raw tildes in one inline context "
              f"→ renders as strikethrough (docs/style.md §4-6): {excerpt}")

    if findings:
        files = len({f[0] for f in findings})
        print(f"\n[check-render-tilde] {len(findings)} pairing context(s) in {files} file(s). "
              f"Use an en dash for ranges (`1–4`) and 약 for approximations (`약 300M`).")
        return 1

    print(f"[check-render-tilde] clean — {len(paths)} doc(s) scanned, "
          f"no strikethrough pairing ({singles} lone tilde(s), harmless)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
