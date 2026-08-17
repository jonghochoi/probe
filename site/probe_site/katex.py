"""Server-side KaTeX rendering, batched and content-cached.

The corpus carries ~7.5k inline math occurrences across ~4k distinct formulas.
Two consequences drive this design:

  1. **Never spawn a process per formula.** At ~40 ms of spawn overhead that is
     five minutes of pure fork, which is a CI non-starter. Rendering is
     deferred: the Markdown renderers emit `<!--K:hash-->` placeholders,
     `flush()` renders every cache-missing formula in ONE `node` call, and
     `splice()` substitutes the results into the finished HTML.
  2. **Cache on content, not on file.** The key is `sha256(tex|display)`, so
     adding one paper re-renders only its new formulas, and changing a macro
     substitution invalidates exactly the formulas it affects.

Math is pre-rendered rather than shipped to the browser because the result is a
build-time constant. KaTeX's `auto-render.js` is specifically disqualified: it
re-scans the DOM for `$` delimiters, which would resurrect the very ambiguity
`ghmath`'s inline rule exists to eliminate — and it would fire on the `$` in
ordinary prose.

Pinned to katex@0.16.22; the workflow installs the same version with
`npm install --no-save`, so no package.json enters the repo tree.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

KATEX_VERSION = "0.16.22"

_HERE = Path(__file__).resolve().parent
_RENDER_SCRIPT = _HERE / "katex-render.mjs"

_PLACEHOLDER = re.compile(r"<!--K:([0-9a-f]{16})-->")


def _key(tex: str, display: bool) -> str:
    raw = f"{'D' if display else 'I'}|{tex}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


class KatexRenderer:
    """Collect → batch-render → splice.

    Usage:
        kx = KatexRenderer(cache_dir)
        html = md.render(text)          # emits placeholders
        kx.flush()                      # one node call
        html = kx.splice(html)
    """

    def __init__(self, cache_dir: Path | None = None, *, node: str | None = None):
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.node = node or shutil.which("node") or "node"
        self._cache: dict[str, str] = {}
        self._pending: dict[str, tuple[str, bool]] = {}
        self.warnings: list[dict] = []
        self.rendered = 0
        self._load_cache()

    # ── cache ───────────────────────────────────────────────────────────
    @property
    def _cache_file(self) -> Path | None:
        return self.cache_dir / "katex.json" if self.cache_dir else None

    def _load_cache(self) -> None:
        path = self._cache_file
        if path and path.is_file():
            try:
                self._cache = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                self._cache = {}

    def save_cache(self) -> None:
        path = self._cache_file
        if not path:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self._cache), encoding="utf-8")

    # ── collect ─────────────────────────────────────────────────────────
    def _emit(self, tex: str, display: bool) -> str:
        h = _key(tex, display)
        if h not in self._cache:
            self._pending[h] = (tex, display)
        return f"<!--K:{h}-->"

    def inline(self, tex: str) -> str:
        return self._emit(tex, False)

    def block(self, tex: str) -> str:
        return f'<div class="math-display">{self._emit(tex, True)}</div>'

    # ── render ──────────────────────────────────────────────────────────
    def flush(self) -> None:
        """Render every pending formula in a single `node` invocation."""
        if not self._pending:
            return
        payload = {
            "items": [
                {"h": h, "tex": tex, "display": display}
                for h, (tex, display) in sorted(self._pending.items())
            ]
        }
        # ESM ignores NODE_PATH, so `katex` must resolve by directory walk from
        # katex-render.mjs — i.e. it lives in `probe_site/node_modules`, which
        # the workflow creates with `npm install --no-save --prefix`.
        env = dict(os.environ)
        try:
            proc = subprocess.run(
                [self.node, str(_RENDER_SCRIPT)],
                input=json.dumps(payload),
                capture_output=True,
                text=True,
                env=env,
                check=True,
            )
        except FileNotFoundError as exc:
            raise KatexUnavailable(
                f"node not found ({self.node}). Install Node 20+, or build with "
                f"--katex=client."
            ) from exc
        except subprocess.CalledProcessError as exc:
            raise KatexUnavailable(
                f"katex render failed. Install it next to the package:\n"
                f"  npm install --no-save --prefix {_HERE} katex@{KATEX_VERSION}\n"
                f"stderr: {exc.stderr.strip()[:500]}"
            ) from exc

        result = json.loads(proc.stdout)
        self._cache.update(result["html"])
        self.warnings.extend(result.get("warnings", []))
        self.rendered += len(self._pending)
        self._pending.clear()

    # ── splice ──────────────────────────────────────────────────────────
    def splice(self, html: str) -> str:
        """Replace `<!--K:hash-->` placeholders with rendered KaTeX."""
        def sub(m: re.Match[str]) -> str:
            return self._cache.get(m.group(1), "")
        return _PLACEHOLDER.sub(sub, html)


class ClientRenderer:
    """`--katex=client` fallback: emit data attributes, render in the browser.

    Uses an explicit `katex.render(el.dataset.tex, el)` initializer over the
    emitted elements — never `auto-render.js`, which would re-scan prose for
    `$` delimiters.
    """

    def __init__(self, *_args, **_kwargs):
        self.warnings: list[dict] = []
        self.rendered = 0

    @staticmethod
    def _esc(tex: str) -> str:
        return (
            tex.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;")
        )

    def inline(self, tex: str) -> str:
        return f'<span class="math" data-tex="{self._esc(tex)}"></span>'

    def block(self, tex: str) -> str:
        return (
            f'<div class="math-display"><span class="math" data-display="1" '
            f'data-tex="{self._esc(tex)}"></span></div>'
        )

    def flush(self) -> None:
        return None

    def save_cache(self) -> None:
        return None

    def splice(self, html: str) -> str:
        return html


class KatexUnavailable(RuntimeError):
    """Raised when the Node/KaTeX toolchain cannot render."""
