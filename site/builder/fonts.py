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

JetBrains Mono gets the same treatment, cut to the narrower `mono_charset` —
only the text that actually lands inside a `<pre>` block, since a code fence
and a research paper's pseudocode draw on the full Latin/Greek/symbol range
(→ ← τ Δ θ̄ x̂ ‖ …) that plain Korean-prose text never does. The upstream
`jetbrains-mono` package (not `@fontsource/jetbrains-mono`, whose prebuilt
weight files are cut to a ~230-glyph Latin-only cmap) ships a ~1,180-glyph
cmap per weight, wide enough to cover ordinary paper notation; `emit()` also
reports any `mono_charset` character that full cmap still lacks, so a rare
symbol (a circled digit, a blackboard-bold letter) is a build warning instead
of a silent tofu box on a reader's phone.

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
_JBM = _MODULES / "jetbrains-mono" / "fonts" / "webfonts"
_JBM_FACES = {400: "Regular", 700: "Bold"}

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


def subset_mono(weight: int, charset: set[str]) -> bytes | None:
    """Subset one JetBrains Mono weight to `charset`, returned as woff2."""
    src = _JBM / f"JetBrainsMono-{_JBM_FACES[weight]}.woff2"
    if not src.is_file():
        return None
    try:
        from fontTools import subset
        from fontTools.ttLib import TTFont
    except ImportError:
        return None

    font = TTFont(src)
    options = subset.Options()
    # Keep every layout feature: JetBrains Mono's `->` / `!=` / `=>` ligatures
    # and its accent mark positioning (x + combining circumflex → x̂) both live
    # in GSUB/GPOS.
    options.layout_features = ["*"]
    options.flavor = "woff2"
    options.notdef_outline = True
    subsetter = subset.Subsetter(options=options)
    subsetter.populate(text="".join(sorted(charset)))
    subsetter.subset(font)

    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    font.close()
    return buf.getvalue()


def _is_hangul(ch: str) -> bool:
    """A Korean syllable or jamo — R8 code fences carry Korean captions and
    comments alongside transcribed pseudocode (AUTHORING §2-8), and no
    monospace typeface bundles Hangul. That is a fallback-font case by
    design, not a coverage gap worth a build warning."""
    o = ord(ch)
    return (
        0x1100 <= o <= 0x11FF   # Hangul Jamo
        or 0x3130 <= o <= 0x318F  # Hangul Compatibility Jamo
        or 0xA960 <= o <= 0xA97F  # Hangul Jamo Extended-A
        or 0xAC00 <= o <= 0xD7A3  # Hangul Syllables
        or 0xD7B0 <= o <= 0xD7FF  # Hangul Jamo Extended-B
    )


def mono_coverage_gap(charset: set[str]) -> set[str]:
    """`charset` characters the full (unsubsetted) JetBrains Mono has no glyph for.

    Checked against the Regular face's own cmap rather than the trimmed
    subset above, so this reports a real font gap and not just "this build's
    corpus didn't happen to ask for it." Hangul is excluded — see `_is_hangul`.
    """
    src = _JBM / f"JetBrainsMono-{_JBM_FACES[400]}.woff2"
    if not src.is_file():
        return set()
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        return set()
    font = TTFont(src)
    cmap: set[int] = set()
    for table in font["cmap"].tables:
        cmap |= set(table.cmap.keys())
    font.close()
    return {
        ch for ch in charset
        if not ch.isspace() and not _is_hangul(ch) and ord(ch) not in cmap
    }


def emit(dest: Path, charset: set[str], mono_charset: set[str] | None = None) -> dict:
    """Write `assets/fonts/*` and `assets/fonts.css`; return byte counts."""
    fonts = dest / "fonts"
    fonts.mkdir(parents=True, exist_ok=True)
    faces: list[str] = []
    mono_charset = charset if mono_charset is None else mono_charset
    stats = {"pretendard": 0, "mono": 0, "glyphs": len(charset), "problems": []}

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

    for weight in _JBM_FACES:
        data = subset_mono(weight, mono_charset)
        if not data:
            continue
        name = f"jetbrains-mono-{weight}.woff2"
        (fonts / name).write_bytes(data)
        stats["mono"] += len(data)
        faces.append(_face("JetBrains Mono", f"fonts/{name}", str(weight)))

    gap = mono_coverage_gap(mono_charset)
    if gap:
        listed = ", ".join(f"{c!r} (U+{ord(c):04X})" for c in sorted(gap, key=ord))
        stats["problems"].append(
            f"mono font gap — JetBrains Mono has no glyph for {listed}; inside "
            f"a code fence this reaches the page as a fallback-font box or "
            f"nothing on a reader whose system has no matching font. Rewrite "
            f"it as inline math ($`…`$) or an ASCII-safe form (AUTHORING §2-8)"
        )

    (dest / "fonts.css").write_text("\n".join(faces) + "\n", encoding="utf-8")
    return stats
