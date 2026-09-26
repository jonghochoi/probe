# site/

Everything the reading site is made of — the static-site generator and its
build-time dependencies. The site publishes `analysis/<arxiv-id>.md`,
`comparison/<slug>.md` and `presentation/<arxiv-id>.md`, and nothing else.

One rewrite becomes **two tabs on one page** — 요약 (one screen, the tab a
reader lands on) and 상세 (the body). Both come out of the same source file and
the same `/analyze` run; their contracts are `analysis/AUTHORING.md` §4 (요약)
and §1–§3 (상세). Two more tabs join them when the other tracks have something
for that paper — 비교 for every comparison holding it, 발표 for its presentation.

The corpus and its contracts stay at the repo root (`analysis/`,
`comparison/`, `presentation/`); this folder only reads from there. The rules a
change here must keep are in `site/CLAUDE.md`; the reasoning behind each
surface sits in the docstring or header comment of the file that draws it.

## Layout

| Path | Role |
|---|---|
| `build-site.py` | Build entry point — `--out`, `--only <id>`, `--check`, `--strict`, `--serve`, `--index <file>`, `--search-api <url>` (see `--help`). A full build also writes `corpus.json` and `llms.txt` at the root; `--only` writes neither |
| `builder/corpus.py` | Rewrite discovery and order (by the commit that landed each rewrite), front-matter validation, pillar names, the landing filter's haystacks, and `score` — the one neighbour rule every surface ranks by |
| `builder/render.py` | Markdown → HTML, the rule checks with no other home (its row in `analysis/AUTHORING.md` §5, and a comparison's fence and length rules), and the 재작성본 sibling marker |
| `builder/mdext/` | `probefence.py` (the ` ```probe-* ` fences and their schemas, `probe-matrix` included), `callouts.py` (R9 GFM alerts → `co-*`), `ghmath.py` (the `` $`x`$ `` dialect) |
| `builder/glance.py` | The 요약 tab and its checks (G1–G7) |
| `builder/comparisons.py` | Comparison discovery and validation (`comparison/AUTHORING.md`) |
| `builder/presentations.py` | Presentation discovery, validation and slide drawing — the 발표 tab (`presentation/AUTHORING.md`) |
| `builder/pages.py`, `components.py` | Page assembly — the landing list, 같이 읽기 (`c/`), 발표 (`t/`), 내 서재, the paper page and its tabs, and the mastheads each list page opens on |
| `builder/decisions.py` | The `context/P*.md` Decision-Log parser behind the `D<n>` tooltips |
| `builder/catalog.py` | The corpus as data for an agent — `corpus.json`, `llms.txt` and the per-section Markdown under `p/<id>/s/` |
| `builder/arxiv.py` | LaTeXML extraction of an arXiv original, for the prompts: `python3 -m builder.arxiv <id>` from this folder prints the section tree and figures; `--grep <regex>` prints the matching lines with their § |
| `builder/katex.py`, `katex-render.mjs` | Server-side math, cached by `sha256(tex\|display)` under `.site-cache/` |
| `builder/fonts.py` | Webfont subsetting, `Probe Num` included |
| `builder/assets_out.py`, `builder/assets/` | The site's CSS, JS and icons, copied into the output tree. Each script opens on a comment stating what it owns |
| `search/` | Semantic search over the rewrites. Folder map: `site/search/README.md` |
| `query.py` | The same records as `corpus.json`, from a checkout and on the standard library alone — `python3 site/query.py --help` |
| `requirements.txt` | Build-time Python dependencies |

## Building locally

```bash
pip install -r site/requirements.txt
npm install --no-save --prefix site/builder \
  katex@0.16.22 pretendard jetbrains-mono
python3 site/build-site.py --serve        # http://127.0.0.1:8000/probe/
```

`.github/workflows/deploy-site.yml` builds pull requests with `--strict` and
deploys from `main`; the published site makes zero third-party requests and
needs no runtime Python.
