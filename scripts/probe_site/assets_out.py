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
_SRC_BLOCK = re.compile(r"src:([^;]+);")
_WOFF2 = re.compile(r"url\(([^)]*\.woff2)\)\s*format\(([\"'])woff2\2\)")


def _woff2_only(css: str) -> str:
    def fix(m: re.Match[str]) -> str:
        hit = _WOFF2.search(m.group(1))
        return f"src:{hit.group(0)};" if hit else m.group(0)
    return _SRC_BLOCK.sub(fix, css)


ASSET_FILES = ("site.css", "index.css", "theme.js", "paper.js", "memo.js",
               "filter.js", "hub.js")


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

    stats = {"fonts": 0, "katex": False, **font_stats}
    if _KATEX_DIST.is_dir():
        kdir = dest / "katex"
        (kdir / "fonts").mkdir(parents=True, exist_ok=True)
        css = (_KATEX_DIST / "katex.min.css").read_text(encoding="utf-8")
        (kdir / "katex.min.css").write_text(_woff2_only(css), encoding="utf-8")
        for font in sorted((_KATEX_DIST / "fonts").glob("*.woff2")):
            shutil.copy2(font, kdir / "fonts" / font.name)
            stats["fonts"] += 1
        stats["katex"] = True
    return stats
