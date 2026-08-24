"""Copy the static assets into the output tree.

KaTeX is vendored rather than pulled from a CDN: the published site must have
zero third-party requests (the one exception, giscus, is click-to-load). The
woff/ttf duplicates are dropped and the CSS rewritten to woff2-only, which
takes the font payload from 1.2 MB to ~296 KB with no visual difference on any
browser from the last decade.
"""

from __future__ import annotations

import hashlib
import re
import shutil
from functools import lru_cache
from pathlib import Path

from . import fonts

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


ASSET_FILES = ("site.css", "index.css", "theme.js", "brand.js", "nav.js",
               "paper.js", "memo.js", "shelf.js", "match.js", "palette.js",
               "filter.js", "hub.js")
# The icons `components.head()` links. Shipped and hashed like everything else
# but never scanned for characters: they carry no text the page renders, and
# two of them are bytes that cannot be decoded as any. `favicon.svg` is the
# tab icon; the PNGs are what a client that will not take an SVG icon falls
# back to — 32 px for a tab, and the 180 px opaque tile iOS composites onto
# the home screen.
ICON_FILES = ("favicon.svg", "favicon-32.png", "apple-touch-icon.png")
# Shipped only when the build was given the endpoint it talks to. A tree with
# no endpoint carries nothing about search: no script to load, and none of its
# Korean strings dragged into the webfont subset for a file nobody fetches.
OPTIONAL = {"search": ("semantic.js",)}


def _files(extras: tuple[str, ...] = ()) -> tuple[str, ...]:
    return ASSET_FILES + ICON_FILES + extras


def asset_text(extras: tuple[str, ...] = ()) -> str:
    """Every character the assets themselves contribute to the page.

    The JS files carry Korean UI strings that never appear in the markup —
    status chips, confirm dialogs — and would otherwise be missing from the
    subset and render in the fallback font mid-interaction.
    """
    return "".join(
        (_ASSETS / name).read_text(encoding="utf-8")
        for name in ASSET_FILES + extras if (_ASSETS / name).is_file()
    )


# Files this build writes rather than copies — they carry no bytes on disk to
# hash, so the build hands them over before it renders a page.
_GENERATED: dict[str, str] = {}


def register(name: str, text: str) -> None:
    """Fold a generated asset into the version token.

    `assets/corpus-index.js` is built from the corpus, so it changes on the
    day a rewrite lands and on no other day — exactly when a reader's cached
    copy stops matching the page that reads it.
    """
    _GENERATED[name] = text
    version.cache_clear()


@lru_cache(maxsize=1)
def version() -> str:
    """The `?v=` token every asset URL carries — a hash of what is shipped.

    Pages serves `assets/site.css` under the same URL forever, so a reader
    whose browser still holds yesterday's copy meets today's markup styled by
    yesterday's rules: a new component lands *unstyled* rather than absent,
    which looks broken in a way a missing feature never does. The token moves
    with the bytes, so markup and the rules that style it are always fetched
    as a pair.

    Every shipped file is hashed, optional ones included, so the token does
    not depend on which flags the build ran with — two builds of the same
    tree agree, and a search build does not invalidate a reader's cache of
    the files it shares with a plain one.
    """
    h = hashlib.sha256()
    names = (ASSET_FILES + ICON_FILES
             + tuple(n for group in OPTIONAL.values() for n in group))
    for name in sorted(names):
        src = _ASSETS / name
        if src.is_file():
            h.update(src.read_bytes())
    for name, text in sorted(_GENERATED.items()):
        h.update(text.encode("utf-8"))
    return h.hexdigest()[:8]


def copy_all(out: Path, charset: set[str] | None = None,
             extras: tuple[str, ...] = (),
             mono_charset: set[str] | None = None) -> dict:
    dest = out / "assets"
    dest.mkdir(parents=True, exist_ok=True)

    for name in _files(extras):
        src = _ASSETS / name
        if src.is_file():
            shutil.copy2(src, dest / name)

    font_stats = fonts.emit(dest, charset or set(), mono_charset)

    stats = {"fonts": 0, "katex": False, "problems": [], **font_stats}
    if _KATEX_DIST.is_dir():
        kdir = dest / "katex"
        (kdir / "fonts").mkdir(parents=True, exist_ok=True)
        css = (_KATEX_DIST / "katex.min.css").read_text(encoding="utf-8")
        slim = _woff2_only(css)
        # Appended, not assigned — `font_stats["problems"]` (the mono
        # coverage-gap warning) already sits in `stats["problems"]` via the
        # spread above, and a plain `=` here would silently drop it.
        stats["problems"] += _check_intact(css, slim)
        (kdir / "katex.min.css").write_text(slim, encoding="utf-8")
        for font in sorted((_KATEX_DIST / "fonts").glob("*.woff2")):
            shutil.copy2(font, kdir / "fonts" / font.name)
            stats["fonts"] += 1
        stats["katex"] = True
    return stats
