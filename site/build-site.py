#!/usr/bin/env python3
"""Build the PROBE reading site.

Renders every `analysis/<id>.md` into a static page tree under `--out`.
Build-time dependencies only — the published site ships no runtime Python, no
CDN request, and (with the default `--katex=server`) no math JavaScript.

    python3 site/build-site.py --out .site           # full build
    python3 site/build-site.py --only 2607.06559     # one rewrite
    python3 site/build-site.py --serve               # build + preview
    python3 site/build-site.py --check               # lint, write nothing

Requires `pip install -r site/requirements.txt`, plus Node with
`npm install --no-save --prefix site/builder katex@0.16.22` for
server-side math (`--katex=client` renders in the browser instead).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

# Tag names and attribute values are never painted, so they must not drag
# glyphs into the subset; `<script>`/`<style>` bodies likewise.
_TEXT_ONLY = re.compile(r"<(script|style)[^>]*>.*?</\1>|<[^>]+>", re.S)

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

try:
    import markdown_it  # noqa: F401
except ImportError:
    sys.stderr.write(
        "error: site build needs `pip install -r site/requirements.txt`\n"
        "       (build-time only — the generated site has no runtime deps)\n"
    )
    raise SystemExit(2)

from builder import assets_out, comparisons, corpus, pages
from builder.decisions import harvest_decisions
from builder.katex import ClientRenderer, KatexRenderer, KatexUnavailable
from builder.render import DocRenderer


def build(args) -> int:
    papers, problems = corpus.discover()

    if args.only:
        papers = [p for p in papers if p.stem in args.only]
        if not papers:
            sys.stderr.write(f"error: no rewrite matched {args.only}\n")
            return 2

    if args.index:
        return write_index(Path(args.index), papers, problems)

    papers_by_id = {p.stem: p for p in papers}
    # A partial build cannot judge a comparison: `--only` drops papers a
    # comparison names, and every one of those reads as a missing rewrite.
    comps: list = []
    if not args.only:
        comps, comp_problems = comparisons.discover(papers_by_id)
        problems += comp_problems

    if args.check:
        for line in problems:
            print(line)
        if problems:
            print(f"\nbuild-site --check: {len(problems)} problem(s) "
                  f"across {len(papers)} rewrite(s) and "
                  f"{len(comps)} comparison(s)")
            return 1
        print(f"build-site --check: {len(papers)} rewrite(s), "
              f"{len(comps)} comparison(s) clean")
        return 0

    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    cache = corpus.REPO_ROOT / ".site-cache" if args.katex == "server" else None
    katex = KatexRenderer(cache) if args.katex == "server" else ClientRenderer()
    decisions = harvest_decisions()

    rendered: dict[Path, str] = {}
    render_problems: list[str] = []
    for paper in papers:
        rendered[out / "p" / paper.stem / "index.html"] = pages.paper_page(
            paper, katex, decisions, render_problems,
            neighbours=corpus.related(paper, papers),
            comparisons=comparisons.for_paper(paper.stem, comps),
        )
    for comp in comps:
        rendered[out / "c" / comp.slug / "index.html"] = pages.comparison_page(
            comp, papers_by_id, katex, decisions, render_problems)
    rendered[out / "c" / "index.html"] = pages.comparison_index_page(comps)
    problems += render_problems

    # The landing page indexes whatever was built — with `--only`, a subset.
    rendered[out / "index.html"] = pages.landing_page(
        papers, katex, search_api=args.search_api)
    rendered[out / "shelf" / "index.html"] = pages.shelf_page(papers)
    rendered[out / "404.html"] = pages.not_found_page()

    try:
        katex.flush()
    except KatexUnavailable as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2
    katex.save_cache()

    final = {p: katex.splice(h) for p, h in rendered.items()}
    for path, html in final.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")

    # The font subset is cut from the *assembled* pages, so it must be computed
    # after the KaTeX splice — and from the asset sources too, since the JS
    # writes Korean UI strings that appear in no page's markup. The ⌘K palette
    # prints titles and taglines that no page's markup carries either — a paper
    # page names one paper and the index names them all — so the index counts
    # as asset text for the same reason.
    extras = assets_out.OPTIONAL["search"] if args.search_api else ()
    index_js = pages.corpus_index(papers)
    charset = set(assets_out.asset_text(extras)) | set(index_js)
    for html in final.values():
        charset |= set(_TEXT_ONLY.sub(" ", html))
    stats = assets_out.copy_all(out, charset, extras)
    (out / "assets" / "corpus-index.js").write_text(index_js, encoding="utf-8")
    size = len(index_js.encode("utf-8"))
    if size > pages.INDEX_BUDGET:
        problems.append(
            f"assets/corpus-index.js: {size / 1024:.0f} KB for {len(papers)} "
            f"rewrite(s), over the {pages.INDEX_BUDGET // 1024} KB budget — "
            f"every page carries it, so drop a field from `pages.corpus_index` "
            f"or raise the budget on purpose"
        )
    # An asset-pipeline failure is a page failure: a mangled KaTeX stylesheet
    # publishes every formula in the body font and no reader reports it.
    problems.extend(stats["problems"])

    warn = len(getattr(katex, "warnings", []))
    kb = (stats["pretendard"] + stats["mono"]) / 1024
    print(
        f"build-site: {len(rendered)} page(s) · {len(papers)} rewrite(s) · "
        f"{len(comps)} comparison(s) · {katex.rendered} formula(s) rendered · "
        f"{stats['glyphs']} glyph(s) → {kb:.0f} KB of webfont · "
        f"{size / 1024:.0f} KB of corpus index · "
        f"{warn} katex warning(s) → {out}"
    )
    if not stats["pretendard"]:
        sys.stderr.write(
            "warning: no Pretendard subset written — install the build fonts with\n"
            "         npm install --no-save --prefix site/builder \\\n"
            "           katex@0.16.22 pretendard @fontsource/jetbrains-mono\n"
            "         (the site falls back to system fonts)\n"
        )
    for line in problems:
        sys.stderr.write(f"warning: {line}\n")
    if args.strict and (problems or warn):
        sys.stderr.write("error: --strict and the build was not clean\n")
        return 1
    return 0


def write_index(path: Path, papers, problems: list[str]) -> int:
    """Cut the rewrites into chunks and write them as JSONL.

    Chunking needs the renderer — a chunk carries the anchor of the section it
    deep-links into, and that comes from the `DocRenderer` the page is built
    with rather than from a second slug parser. Nothing here reaches the
    network: embedding and upload are `site/search/indexer.py`, so this half
    runs in CI with no key.
    """
    from search import chunks as chunk_mod

    out = []
    for paper in papers:
        renderer = DocRenderer(ClientRenderer())
        renderer.render(paper.article or paper.body)
        out += chunk_mod.from_rewrite(paper, renderer.toc)

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for chunk in out:
            fh.write(json.dumps(chunk.as_dict(), ensure_ascii=False) + "\n")
    print(f"build-site --index: {len(out)} chunk(s) "
          f"across {len(papers)} rewrite(s) → {path}")
    for line in problems:
        sys.stderr.write(f"warning: {line}\n")
    return 0


def serve(out: Path, port: int) -> None:
    """Preview under the same `/probe/` prefix Pages will use.

    Serving the tree at `/` instead would make the local preview disagree with
    production for every root-anchored URL — which is exactly the case
    `404.html` needs, and exactly the bug a preview is supposed to catch.
    """
    import functools
    import http.server

    base = pages.SITE_BASE

    class Handler(http.server.SimpleHTTPRequestHandler):
        def translate_path(self, path):
            if path.startswith(base):
                path = "/" + path[len(base):]
            return super().translate_path(path)

        def send_head(self):
            if self.path == "/" or not self.path.startswith(base):
                self.send_response(302)
                self.send_header("Location", base)
                self.end_headers()
                return None
            return super().send_head()

    handler = functools.partial(Handler, directory=str(out))
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        print(f"serving {out} at http://127.0.0.1:{port}{base}  (Ctrl-C to stop)")
        httpd.serve_forever()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=".site", help="output directory (default: .site)")
    ap.add_argument("--only", nargs="*", help="build only these arXiv ids")
    ap.add_argument("--check", action="store_true", help="lint only; write nothing")
    ap.add_argument("--index", metavar="FILE",
                    help="write the search index (JSONL) and build no pages")
    ap.add_argument("--strict", action="store_true", help="fail on any warning")
    ap.add_argument("--serve", action="store_true", help="serve --out after building")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--katex", choices=("server", "client"), default="server")
    ap.add_argument("--search-api", default=os.environ.get("PROBE_SEARCH_API", ""),
                    metavar="URL",
                    help="semantic-search endpoint; omitted, the site makes no requests")
    args = ap.parse_args()

    code = build(args)
    if code == 0 and args.serve:
        serve(Path(args.out), args.port)
    return code


if __name__ == "__main__":
    sys.exit(main())
