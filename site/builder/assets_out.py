"""Copy the static assets into the output tree.

KaTeX is vendored rather than pulled from a CDN: the published site must have
zero third-party requests (the one exception, giscus, is click-to-load). The
woff/ttf duplicates are dropped and the CSS rewritten to woff2-only, which
takes the font payload from 1.2 MB to ~296 KB with no visual difference on any
browser from the last decade.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from . import fonts
from .render import pygments_css

_HERE = Path(__file__).resolve().parent
_ASSETS = _HERE / "assets"
_KATEX_DIST = _HERE / "node_modules" / "katex" / "dist"

# A @font-face src list; we keep only the woff2 entry.
#
# The terminator is `[;}]`, and that bracket is the whole rule. `src:` is the
# LAST declaration in each of KaTeX's minified @font-face blocks, so it ends at
# the closing brace with no semicolon: a `[^;]+;` pattern ran straight through
# `}@font-face{…` and stopped at the next block's first semicolon, swallowing
# the boundary. Every substitution ate one block, 20 @font-face rules collapsed
# into 1, and `.katex{font:1.21em KaTeX_Main…}` — the first rule after them —
# went with it. The site published every formula in the body sans-serif with no
# KaTeX face loaded at all, which looks close enough to right that it survived
# review; `_check_intact` below is why it cannot happen again silently.
_SRC_BLOCK = re.compile(r"src:([^;}]+)([;}])")
_WOFF2 = re.compile(r"url\(([^)]*\.woff2)\)\s*format\(([\"'])woff2\2\)")


def _woff2_only(css: str) -> str:
    def fix(m: re.Match[str]) -> str:
        hit = _WOFF2.search(m.group(1))
        return f"src:{hit.group(0)}{m.group(2)}" if hit else m.group(0)
    return _SRC_BLOCK.sub(fix, css)


def _check_intact(before: str, after: str) -> list[str]:
    """The rewrite drops `src` entries and nothing else."""
    problems = []
    faces_in, faces_out = before.count("@font-face"), after.count("@font-face")
    if faces_in != faces_out:
        problems.append(
            f"katex.min.css: the woff2 rewrite lost @font-face blocks "
            f"({faces_in} in, {faces_out} out) — math would publish in the "
            f"body font with no KaTeX face loaded"
        )
    if "KaTeX_Main" not in after or ".katex{font:" not in after:
        problems.append(
            "katex.min.css: the woff2 rewrite dropped the `.katex` base rule — "
            "every formula would inherit the body font"
        )
    return problems


ASSET_FILES = ("site.css", "index.css", "theme.js", "paper.js", "memo.js",
               "filter.js", "hub.js", "deck.js")


def asset_text() -> str:
    """Every character the assets themselves contribute to the page.

    The JS files carry Korean UI strings that never appear in the markup —
    status chips, confirm dialogs — and would otherwise be missing from the
    subset and render in the fallback font mid-interaction.
    """
    return "".join(
        (_ASSETS / name).read_text(encoding="utf-8")
        for name in ASSET_FILES if (_ASSETS / name).is_file()
    )


def copy_all(out: Path, charset: set[str] | None = None) -> dict:
    dest = out / "assets"
    dest.mkdir(parents=True, exist_ok=True)

    for name in ASSET_FILES:
        src = _ASSETS / name
        if src.is_file():
            shutil.copy2(src, dest / name)

    (dest / "pygments.css").write_text(pygments_css(), encoding="utf-8")
    font_stats = fonts.emit(dest, charset or set())

    stats = {"fonts": 0, "katex": False, "problems": [], **font_stats}
    if _KATEX_DIST.is_dir():
        kdir = dest / "katex"
        (kdir / "fonts").mkdir(parents=True, exist_ok=True)
        css = (_KATEX_DIST / "katex.min.css").read_text(encoding="utf-8")
        slim = _woff2_only(css)
        stats["problems"] = _check_intact(css, slim)
        (kdir / "katex.min.css").write_text(slim, encoding="utf-8")
        for font in sorted((_KATEX_DIST / "fonts").glob("*.woff2")):
            shutil.copy2(font, kdir / "fonts" / font.name)
            stats["fonts"] += 1
        stats["katex"] = True
    return stats
