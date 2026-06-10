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
  4. `\\bm{X}`/`\\mathds{X}`-> `\\mathbf{X}`/`\\mathbb{X}` (inside math only),
     and `\\operatorname{X}` -> `\\mathrm{X}` (github.com's KaTeX leaks the raw
     `\\operatorname`; `\\mathrm` is the same upright glyph and renders)
  5. boundary spacing       -> insert a space where Hangul/CJK/`·`/`*` is glued
                              to an inline `$` delimiter
  6. `` `$`X`$` ``          -> `` $`X`$ ``        (valid span wrapped in an extra
                              backtick pair — GitHub renders it as code, not math)

Report-only (no safe auto-fix; cause a non-zero exit):
  - odd count of unescaped `$` on a line (unbalanced delimiters)
  - KaTeX-unsupported author macros (`\\newcommand`, `\\def`, `\\renewcommand`)
  - GitHub-KaTeX-unsupported equation-numbering macros (`\\tag`, `\\label`,
    `\\ref`, `\\eqref`, `\\nonumber`) — KaTeX on github.com errors on these
    and dumps the raw LaTeX (it wraps character-by-character); number
    equations in the surrounding prose instead (`(식 N)`), the convention
    every other analysis doc follows. The fix is structural, not a token swap
  - multi-line `$$…\\…$$` (a `\\` row break inside display dollars) — GitHub
    renders `\\` only inside a ```math fenced block, so this must be moved
    there by hand (the fix is structural, not a token swap)
  - a display block indented under a list item — an indented `$$…$$` (leaks
    raw LaTeX) or an indented ```math fence (renders as a code block). GitHub
    renders display math ONLY at column 0, so both must be pulled out to the
    top level (the fix is structural, not a token swap)
  - paper math in a PLAIN backtick span (§5-6 boundary) — e.g. `` `λ` ``,
    `` `A ∈ R^{d×r}` ``, `` `L = λ_act·L_act` `` masquerading as a code token.
    Convert to inline `` $`X`$ `` if it is math; a literal identifier, tensor
    shape (`` `(B, T, d)` ``), or numeric/resolution spec (`` `224×224` ``)
    legitimately stays a code-span, so this is a judgment call, not a token swap

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
    # `\operatorname{…}` is valid KaTeX but renders broken on github.com's
    # KaTeX (it leaks the raw control word); `\mathrm` is the same upright
    # glyph and renders, so swap it (the operator-spacing delta is negligible).
    (re.compile(r"\\operatorname\*?"), r"\\mathrm"),
]
# A `$$…$$` display block indented under a list item: GitHub does NOT render
# display math inside a list (it leaks the raw LaTeX). The fix is structural
# (de-indent to column 0, or use a ```math fenced block — which DOES render in
# a list), so this is report-only.
INDENTED_DISPLAY = re.compile(r"^[ \t]+\$\$")
# Author macros KaTeX cannot resolve; we surface them rather than guess a fix.
UNSUPPORTED_MACRO = re.compile(r"\\(?:newcommand|renewcommand|def)\b")
# §5-6 — equation-numbering macros github.com's KaTeX rejects: it errors and
# leaks the raw LaTeX onto the page (wrapping it character-by-character). The
# paper's equation numbers belong in prose (`(식 N)`), not in a `\tag`.
GITHUB_UNSUPPORTED_MACRO = re.compile(r"\\(?:tag|label|ref|eqref|nonumber)\b")

# §5-6 boundary rule — signals that a PLAIN backtick span is really paper math
# wearing a code-variable costume (Greek letter, math operator, LaTeX macro,
# sub/superscript glyph, or an equation shape), not a literal code token. `×`
# (U+00D7) and `·` (U+00B7) are DELIBERATELY excluded: they are codepoint-
# distinct from the Greek/operator ranges and occur in shapes/specs the repo
# keeps as code (`224×224`, `30 fps · 2 MP`), so they never fire on their own.
_GREEK = r"Ͱ-Ͽἀ-῿"
_MATH_OP = r"∈∉⊂⊆⊕⊗≤≥≈≠≅→←↦⇒⊤⊥∑∏∫∇∂√∞∝∀∃∥‖⟨⟩⌊⌋⌈⌉"  # NB: ×, · excluded
_SUPERSUB = r"²³¹⁰-₟⁺-⁾"
MATH_SIGNAL = re.compile(rf"[{_GREEK}{_MATH_OP}{_SUPERSUB}]|\\[A-Za-z]+|\^\{{|_\{{")
# An equation shape: `=` flanked by expressions, with an operator/Greek in the
# body — catches ASCII-only `L = λ_act·L_act` while skipping `temperature=0.7`.
MATH_EQUATION = re.compile(rf"[^\s=]\s*=\s*[^\s=].*[·×+\-/Σ{_GREEK}]")
TAG_HANGUL = re.compile(r"[가-힣]")            # Korean annotation tag
TAG_EMOJI = re.compile(r"^\s*[\U0001F300-\U0001FAFF☀-➿]")  # 🚧 ✅ ⚠ …
PLAIN_BACKTICK = re.compile(r"`([^`\n]+?)`")
_MASK = re.compile(r"\$`[^`]*?`\$|`\$[^`$]+?\$`|\$\$.+?\$\$")  # blank these first

VALID_INLINE = re.compile(r"\$`[^`]*?`\$")      # the one allowed inline form
DISPLAY = re.compile(r"\$\$.+?\$\$")            # display block (possibly inline)
# A valid inline span `$`X`$ ` accidentally wrapped in an EXTRA pair of
# backticks — `` `$`X`$` ``. The inner span is correct, but the outer
# backticks make GitHub parse it as code-span($) + literal-text(X) +
# code-span($), so the LaTeX leaks as raw text in every browser. The
# author almost always meant the bare `$`X`$ `; strip the outer pair.
OUTER_WRAP = re.compile(r"`(\$`[^`]+?`\$)`")
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


def process_line(
    line: str, check_backticks: bool = False
) -> tuple[str, list[str], list[tuple[int, str]]]:
    """Return (new_line, fixes, issues) for one non-code-block line.

    `issues` is a list of (col, reason) for unfixable findings. The plain-
    backtick math boundary check (§5-6) runs only when `check_backticks` is
    set — it is scoped to `design.md` (the per-paper Design docs where the
    code-vs-math boundary concentrates), not the prose-heavy `analysis.md`.
    """
    fixes: list[str] = []
    issues: list[tuple[int, str]] = []
    protected: list[str] = []

    # Report-only: a `$$…$$` display block indented under a list item — GitHub
    # renders display math only at column 0 (or inside a ```math fence), so an
    # indented `$$` leaks the raw LaTeX. The fix is structural, not a token swap.
    if INDENTED_DISPLAY.match(line):
        issues.append(
            (
                len(line) - len(line.lstrip()) + 1,
                "indented `$$` display block — GitHub does not render display "
                "math inside a list; move it to column 0 (a ```math fence "
                "does not help — it also fails in a list) (§5-6)",
            )
        )

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

    # 1b. Strip an extra backtick pair wrapping a valid inline span:
    #     `` `$`X`$` `` -> `` $`X`$ ``. Done before display/inline passes so
    #     the unwrapped span is then recognized as canonical inline math.
    def _unwrap(m: re.Match) -> str:
        fixes.append("outer-backtick-wrapped inline ``` `$`X`$` ``` → $`X`$")
        return m.group(1)

    line = OUTER_WRAP.sub(_unwrap, line)

    # 2. Stash display blocks first (applying the macro whitelist), so the
    #    inline passes below cannot see their `$$` delimiters. A `$$…$$` that
    #    carries a `\\` row break (aligned / matrix / cases / a bare line
    #    break) does not render on GitHub in any browser — only a ```math
    #    fenced block does — so flag it (report-only; the fix is structural).
    def _display(m: re.Match) -> str:
        if "\\\\" in m.group(0):
            issues.append(
                (
                    m.start() + 1,
                    "multi-line `$$…\\\\…$$` — move to a ```math fenced block "
                    "(GitHub renders `\\\\` row breaks only inside ```math)",
                )
            )
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

    # Report-only: equation-numbering macros github.com's KaTeX rejects.
    for m in GITHUB_UNSUPPORTED_MACRO.finditer(line):
        issues.append(
            (
                m.start() + 1,
                f"GitHub-KaTeX-unsupported macro `{m.group(0)}` — number the "
                "equation in prose (`(식 N)`), not with `\\tag`/`\\label` (§5-6)",
            )
        )

    # Report-only: paper math sitting in a PLAIN backtick span (§5-6 boundary).
    if check_backticks:
        _report_math_in_backticks(line, issues)

    return line, fixes, issues


def _report_math_in_backticks(line: str, issues: list[tuple[int, str]]) -> None:
    """Flag a plain backtick code-span whose body is really paper math.

    §5-6 boundary rule: math notation (Greek letters, operators, LaTeX macros,
    sub/superscripts, equations) belongs in inline math `` $`X`$ ``, not a
    backtick code-span. Report-only — converting is a judgment call (a literal
    identifier, tensor shape, or numeric/resolution spec legitimately stays a
    code-span), so we surface candidates rather than rewrite them.

    Valid inline/display math is masked to equal-length blanks first so the
    detector never sees the inner backticks of a real `` $`X`$ `` span and the
    reported column stays accurate."""
    masked = _MASK.sub(lambda m: " " * len(m.group(0)), line)
    for m in PLAIN_BACKTICK.finditer(masked):
        body = m.group(1)
        if not (MATH_SIGNAL.search(body) or MATH_EQUATION.search(body)):
            continue
        if TAG_HANGUL.search(body) or TAG_EMOJI.match(body):
            continue  # Korean annotation / status-emoji tag — neither code nor math
        shown = body if len(body) <= 40 else body[:39] + "…"
        issues.append(
            (
                m.start() + 1,
                f"math content in a plain backtick span `{shown}` — convert to "
                "inline `$`X`$` if it is paper math (§5-6)",
            )
        )


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
    # The plain-backtick math boundary check (§5-6) is scoped to design.md.
    check_bt = path.name == "design.md"
    fence = False
    new_lines: list[str] = []
    fix_descs: list[str] = []
    issues: list[Issue] = []

    for n, line in enumerate(lines, start=1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            # An indented ```math display fence inside a list item does not
            # render on github.com — it shows as a plain code block. Flag the
            # opening fence (report-only; the fix is structural — pull the
            # block out to column 0, same as an indented `$$`).
            if (
                not fence
                and stripped.startswith("```")
                and line[:1] in (" ", "\t")
                and stripped[3:].strip().lower() == "math"
            ):
                issues.append(
                    Issue(
                        path,
                        n,
                        len(line) - len(stripped) + 1,
                        "indented ```math display fence — GitHub does not render "
                        "a display-math fence inside a list (it shows as a code "
                        "block); move it to column 0 (§5-6)",
                    )
                )
            fence = not fence
            new_lines.append(line)
            continue
        has_math = "$" in line or "\\(" in line or "\\[" in line
        # design.md also processes backtick-only lines (math-in-backticks).
        if fence or not (has_math or (check_bt and "`" in line)):
            new_lines.append(line)
            continue

        new_line, fixes, line_issues = process_line(line, check_bt)
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
