"""Build-time font subsetting.

Pretendard ships 6.5 MB of variable TTF covering all of Hangul; this corpus
uses 1,324 distinct characters. Subsetting to exactly those takes the payload
to ~270 KB, which is the difference between a font that arrives before the
reader scrolls and one that does not.

The subset covers the whole corpus and is shared by every page, rather than
being cut per page and inlined: a per-page subset is smaller in isolation
(~55 KB/weight against ~108 KB for the union) but it ships in each of the 95
pages and is re-fetched on every navigation, where the shared file is fetched
once and cached.

It is the variable font, not static cuts. The site uses six weights
(400/500/600/700/750/800); as static files that is ~540 KB, against ~272 KB
for one variable subset — and `font-weight: 750` renders at 750 rather than
snapping to the nearest cut.

Everything degrades: if `node_modules/` or `fonttools` is absent, no font files
are written and the generated `fonts.css` carries only the system fallback
stack. The site is still fully readable — it just looks like the OS.
"""

from __future__ import annotations

import io
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_MODULES = _HERE / "node_modules"
_PRETENDARD = _MODULES / "pretendard" / "dist" / "public" / "variable" / "PretendardVariable.ttf"
_JBM = _MODULES / "@fontsource" / "jetbrains-mono" / "files"
_JBM_WEIGHTS = (400, 700)

# Characters the markup never contains because JavaScript writes them at
# runtime. The asset sources are scanned for exactly this reason, but a string
# built by concatenation at runtime would still slip through.
RUNTIME_CHARS = "저장됨입력중삭제발행가져옴실패공간이가득찼습니다개편"


def _face(family: str, url: str, weight: str, fmt: str = "woff2") -> str:
    return (
        f"@font-face{{font-family:'{family}';"
        f"src:url({url}) format('{fmt}');"
        f"font-weight:{weight};font-style:normal;font-display:swap}}"
    )


def subset_pretendard(charset: set[str]) -> bytes | None:
    """Subset the variable font to `charset`, returned as woff2."""
    if not _PRETENDARD.is_file():
        return None
    try:
        from fontTools import subset
        from fontTools.ttLib import TTFont
    except ImportError:
        return None

    font = TTFont(_PRETENDARD)
    options = subset.Options()
    # Keep every layout feature: Hangul composition and the Latin kerning both
    # live in GSUB/GPOS, and dropping them is visible in running text.
    options.layout_features = ["*"]
    options.flavor = "woff2"
    options.notdef_outline = True
    options.drop_tables += ["FFTM"]
    subsetter = subset.Subsetter(options=options)
    subsetter.populate(text="".join(sorted(charset)))
    subsetter.subset(font)

    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    font.close()
    return buf.getvalue()


def emit(dest: Path, charset: set[str]) -> dict:
    """Write `assets/fonts/*` and `assets/fonts.css`; return byte counts."""
    fonts = dest / "fonts"
    fonts.mkdir(parents=True, exist_ok=True)
    faces: list[str] = []
    stats = {"pretendard": 0, "mono": 0, "glyphs": len(charset)}

    data = subset_pretendard(charset | set(RUNTIME_CHARS))
    if data:
        (fonts / "pretendard-subset.woff2").write_bytes(data)
        stats["pretendard"] = len(data)
        # `woff2-variations` is the format hint that keeps the weight axis
        # continuous; the `45 930` range is Pretendard's own fvar span.
        faces.append(
            _face("Pretendard Variable", "fonts/pretendard-subset.woff2",
                  "45 930", "woff2-variations")
        )

    for weight in _JBM_WEIGHTS:
        src = _JBM / f"jetbrains-mono-latin-{weight}-normal.woff2"
        if not src.is_file():
            continue
        name = f"jetbrains-mono-{weight}.woff2"
        (fonts / name).write_bytes(src.read_bytes())
        stats["mono"] += src.stat().st_size
        faces.append(_face("JetBrains Mono", f"fonts/{name}", str(weight)))

    (dest / "fonts.css").write_text("\n".join(faces) + "\n", encoding="utf-8")
    return stats
