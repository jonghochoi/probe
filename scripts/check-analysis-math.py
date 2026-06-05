#!/usr/bin/env python3
"""Check (and optionally fix) math formatting in analysis documents.

Enforces the GitHub-KaTeX math conventions of `docs/STYLE.md` §5-6 across
the analysis deep-dive docs: inline math MUST be the inside-dollar backtick
form `` $`X`$ `` and display math `$$X$$` on its own line. The outside-dollar
form `` `$X$` ``, the `\\(…\\)` / `\\[…\\]` delimiters, KaTeX-unsupported
macros (`\\bm`, `\\mathds`), and `$` glued to Hangul/CJK/bold all break
rendering on github.com and leak the source.

Scope: `analysis/<id>/analysis.md`, `analysis/<id>/design.md`, and
`analysis/<id>/impl/<foundry>/impl.md`. Catalogs, templates, and README.md
are out of scope.

Auto-fixable (applied with --fix):
  1. `` `$X$` ``            -> `` $`X`$ ``        (forbidden outside-dollar form)
  2. `\\(X\\)` / `\\[X\\]`  -> `` $`X`$ `` / `$$X$$`
  3. bare inline `$X$`      -> `` $`X`$ ``        (single dollars, not display)
  4. `\\bm{X}`/`\\mathds{X}`-> `\\mathbf{X}`/`\\mathbb{X}` (inside math only)
  5. boundary spacing       -> insert a space where Hangul/CJK/`·`/`*` is glued
                              to an inline `$` delimiter

Report-only (no safe auto-fix; cause a non-zero exit):
  - odd count of unescaped `$` on a line (unbalanced delimiters)
  - KaTeX-unsupported author macros (`\\newcommand`, `\\def`, `\\renewcommand`)

Usage (repo root):
    python3 scripts/check-analysis-math.py [--fix] [PATH ...]

No PATH -> scan the whole scope. --fix rewrites files in place, then
re-checks. Idempotent: a clean tree re-runs with no diff.

Exit codes: 0 = clean (no unfixable issues) / 1 = unfixable issues remain
/ 2 = nothing to scan (skipped).

Specification: docs/STYLE.md §5-6.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ANALYSIS_DIR = REPO_ROOT / "analysis"

# §5-6 rule 2 — inline-math delimiter neighbours that GitHub's KaTeX parser
# accepts. Opener `$` may follow these; closer `$` may precede these.
OPENER_OK = set(" \t([{<")   # plus start-of-line
CLOSER_OK = set(" \t.,;:!?)]}>")  # plus end-of-line

# §5-6 rule 5 — the only sanctioned macro substitutions.
MACRO_SUBS = [
    (re.compile(r"\\bm\{"), r"\\mathbf{"),
    (re.compile(r"\\mathds\{"), r"\\mathbb{"),
]
# Author macros KaTeX cannot resolve; we surface them rather than guess a fix.
UNSUPPORTED_MACRO = re.compile(r"\\(?:newcommand|renewcommand|def)\b")

VALID_INLINE = re.compile(r"\$`[^`]*?`\$")      # the one allowed inline form
DISPLAY = re.compile(r"\$\$.+?\$\$")            # display block (possibly inline)
# Valid inline (`$`X`$ `) and the forbidden outside-dollar form (`` `$X$` ``)
# are mirror images, so a single left-to-right pass dispatches on which
# alternative matched — separate passes would let one form's delimiters be
# misread as the other's (e.g. the `$`` inside `` `$X$` ``).
COMBINED_INLINE = re.compile(r"\$`(?P<vbody>[^`]*?)`\$|`\$(?P<obody>[^`$]+?)\$`")
PAREN_INLINE = re.compile(r"\\\((.+?)\\\)")     # \( ... \)
BRACKET_DISPLAY = re.compile(r"\\\[(.+?)\\\]")  # \[ ... \]
BARE_INLINE = re.compile(r"(?<![\$`])\$(?!\$)([^$`\n]+?)\$(?![\$`])")


class Issue:
    """A single unfixable finding, reported as file:line:col — reason."""

    def __init__(self, path: Path, lineno: int, col: int, reason: str):
        self.path = path
        self.lineno = lineno
        self.col = col
        self.reason = reason

    def render(self) -> str:
        rel = self.path.relative_to(REPO_ROOT)
        return f"{rel}:{self.lineno}:{self.col} — {self.reason}"


def in_scope_files(paths: list[Path]) -> list[Path]:
    """Resolve the scan set: analysis.md / design.md / impl/**/impl.md."""
    out: list[Path] = []
    if paths:
        for p in paths:
            p = p if p.is_absolute() else (REPO_ROOT / p)
            if p.is_file():
                out.append(p)
            elif p.is_dir():
                out.extend(_scope_under(p))
        return sorted(set(out))
    return _scope_under(ANALYSIS_DIR)


def _scope_under(root: Path) -> list[Path]:
    out: list[Path] = []
    for p in sorted(root.rglob("*.md")):
        rel = p.relative_to(REPO_ROOT).as_posix()
        if "/catalogs/" in f"/{rel}" or "/templates/" in f"/{rel}":
            continue
        name = p.name
        if name in ("analysis.md", "design.md") or (
            name == "impl.md" and "/impl/" in f"/{rel}"
        ):
            out.append(p)
    return out


def _apply_macro_subs(math: str, fixes: list[str]) -> str:
    for pat, repl in MACRO_SUBS:
        new = pat.sub(repl, math)
        if new != math:
            fixes.append(f"macro substitution ({pat.pattern} → {repl})")
            math = new
    return math


def process_line(line: str) -> tuple[str, list[str], list[tuple[int, str]]]:
    """Return (new_line, fixes, issues) for one non-code-block line.

    `issues` is a list of (col, reason) for unfixable findings.
    """
    fixes: list[str] = []
    issues: list[tuple[int, str]] = []
    protected: list[str] = []

    def _stash(text: str) -> str:
        protected.append(text)
        return f"\x00{len(protected) - 1}\x00"

    # 1. \[X\] -> $$X$$  and  \(X\) -> $`X`$  (delimiter conversion). The
    #    products are canonical forms, immediately stashed below.
    def _bracket(m: re.Match) -> str:
        fixes.append(r"\[…\] → $$…$$")
        return f"$${m.group(1)}$$"

    def _paren(m: re.Match) -> str:
        fixes.append(r"\(…\) → $`…`$")
        return f"$`{m.group(1)}`$"

    line = BRACKET_DISPLAY.sub(_bracket, line)
    line = PAREN_INLINE.sub(_paren, line)

    # 2. Stash display blocks first (applying the macro whitelist), so the
    #    inline passes below cannot see their `$$` delimiters.
    def _display(m: re.Match) -> str:
        return _stash(_apply_macro_subs(m.group(0), fixes))

    line = DISPLAY.sub(_display, line)

    # 3. Single left-to-right pass over inline math: valid `$`X`$ ` is stashed
    #    as-is (macro-subbed); the forbidden `` `$X$` `` is fixed and stashed.
    def _inline(m: re.Match) -> str:
        if m.group("vbody") is not None:
            body = m.group("vbody")
        else:
            fixes.append("outside-dollar `$X$` → $`X`$")
            body = m.group("obody")
        return _stash(f"$`{_apply_macro_subs(body, fixes)}`$")

    line = COMBINED_INLINE.sub(_inline, line)

    # 4. bare inline $X$ -> $`X`$  (after display/valid/outside are stashed).
    def _bare(m: re.Match) -> str:
        fixes.append("bare $X$ → $`X`$")
        return _stash(f"$`{_apply_macro_subs(m.group(1), fixes)}`$")

    line = BARE_INLINE.sub(_bare, line)

    # 5. Report-only: stray unescaped `$` left after all conversions means an
    #    unbalanced delimiter (escaped \$ and protected spans are excluded).
    residue = re.sub(r"\\\$", "", line)
    if "$" in residue:
        col = line.find("$") + 1
        issues.append((col, "unbalanced/stray `$` (delimiter mismatch)"))

    # Reinsert protected spans, then apply boundary spacing around inline math.
    def _restore(m: re.Match) -> str:
        return protected[int(m.group(1))]

    line = re.sub(r"\x00(\d+)\x00", _restore, line)

    # 6. Boundary spacing for inline `$`...`$` spans (§5-6 rule 2).
    line, bfix = _fix_boundaries(line)
    if bfix:
        fixes.append("boundary spacing around inline `$`")

    # Report-only: KaTeX-unsupported author macros.
    for m in UNSUPPORTED_MACRO.finditer(line):
        issues.append(
            (m.start() + 1, f"KaTeX-unsupported macro `{m.group(0)}`")
        )

    return line, fixes, issues


def _fix_boundaries(line: str) -> tuple[str, bool]:
    """Insert a space where an inline `$`…`$ ` delimiter is glued to a
    Hangul/CJK syllable or middle-dot `·` (§5-6 rule 2).

    Bold markers `*`/`**` are deliberately NOT touched here: the prescribed
    fix is structural (move the math outside the bold span), which a space
    insertion would get wrong (a trailing space breaks the bold). Those are
    left for human authoring rather than risked by an auto-fix."""
    changed = False
    out: list[str] = []
    i = 0
    for m in VALID_INLINE.finditer(line):
        start, end = m.start(), m.end()
        out.append(line[i:start])
        # opener neighbour (char immediately before the opening `$`)
        if start > 0:
            prev = line[start - 1]
            if prev not in OPENER_OK and not (out and out[-1].endswith(" ")):
                if _needs_space(prev):
                    out.append(" ")
                    changed = True
        out.append(m.group(0))
        # closer neighbour (char immediately after the closing `$`)
        nxt = line[end] if end < len(line) else ""
        if nxt and nxt not in CLOSER_OK and _needs_space(nxt):
            out.append(" ")
            changed = True
        i = end
    out.append(line[i:])
    return "".join(out), changed


def _needs_space(ch: str) -> bool:
    """A neighbour where inserting a space is a safe, content-preserving fix."""
    if ch == "·":
        return True
    # CJK / Hangul ranges (rough but sufficient for boundary detection).
    o = ord(ch)
    return (
        0xAC00 <= o <= 0xD7A3  # Hangul syllables
        or 0x1100 <= o <= 0x11FF  # Hangul Jamo
        or 0x3130 <= o <= 0x318F  # Hangul compatibility Jamo
        or 0x4E00 <= o <= 0x9FFF  # CJK unified ideographs
        or 0x3040 <= o <= 0x30FF  # Hiragana / Katakana
    )


def check_file(path: Path, fix: bool) -> tuple[bool, list[str], list[Issue]]:
    """Process one file. Return (changed, fix_descriptions, issues)."""
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    fence = False
    new_lines: list[str] = []
    fix_descs: list[str] = []
    issues: list[Issue] = []

    for n, line in enumerate(lines, start=1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            fence = not fence
            new_lines.append(line)
            continue
        if fence or "$" not in line and "\\(" not in line and "\\[" not in line:
            new_lines.append(line)
            continue

        new_line, fixes, line_issues = process_line(line)
        for col, reason in line_issues:
            issues.append(Issue(path, n, col, reason))
        if fixes:
            for f in fixes:
                fix_descs.append(f"{path.relative_to(REPO_ROOT)}:{n} — {f}")
        new_lines.append(new_line)

    changed = new_lines != lines
    if changed and fix:
        path.write_text("\n".join(new_lines), encoding="utf-8")
    return changed, fix_descs, issues


def main() -> int:
    ap = argparse.ArgumentParser(description="Check analysis math formatting.")
    ap.add_argument("--fix", action="store_true", help="rewrite files in place")
    ap.add_argument("paths", nargs="*", type=Path, help="files or dirs to scan")
    args = ap.parse_args()

    files = in_scope_files(args.paths)
    if not files:
        print("check-analysis-math: nothing in scope to scan.", file=sys.stderr)
        return 2

    any_changed = False
    all_fixes: list[str] = []
    all_issues: list[Issue] = []
    for path in files:
        changed, fixes, issues = check_file(path, args.fix)
        any_changed = any_changed or changed
        all_fixes.extend(fixes)
        all_issues.extend(issues)

    if args.fix and all_fixes:
        print(f"Applied {len(all_fixes)} fix(es):")
        for f in all_fixes:
            print(f"  {f}")
    elif not args.fix and any_changed:
        print(f"{len(all_fixes)} auto-fixable issue(s) (run with --fix):")
        for f in all_fixes:
            print(f"  {f}")

    if all_issues:
        print(f"\n{len(all_issues)} unfixable issue(s):", file=sys.stderr)
        for it in all_issues:
            print(f"  {it.render()}", file=sys.stderr)
        return 1

    if not any_changed and not all_issues:
        print(f"check-analysis-math: {len(files)} file(s) clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
