# site/

Everything the reading site is made of — the static-site generator and its
build-time dependencies. The site publishes `analysis/<arxiv-id>.md`,
`comparison/<slug>.md` and the scouting reports `scouting/P#/<date>.md`, and
nothing else.

A paper's page carries the 요약 and 상세 tabs from its rewrite, plus 비교 when
a comparison holds it and 계보 when another paper stands on it or it on one. 탐색 (`s/<date>/`) is one
page per run, every pillar's report merged by arXiv id, and `s/` prints the
newest run with every date in a row above it. The corpus and its
contracts stay at the repo root; the rules a change here must keep are in
`site/CLAUDE.md`, and the reasoning behind each surface sits in the header
comment of the file that draws it.

## Layout

| Path | Role |
|---|---|
| `build-site.py` | Build entry point — `--out`, `--only <id>`, `--check`, `--strict`, `--serve`, `--index <file>`, `--search-api <url>`, `--scout-figures`, `--gap-titles` (see `--help`). A full build also writes `corpus.json` and `llms.txt` at the root; `--only` writes neither |
| `builder/corpus.py` | Rewrite discovery and order (by the commit that landed each rewrite), front-matter validation, pillar names, the analysis list's haystacks, and `score` — the one neighbour rule every surface ranks by |
| `builder/render.py` | Markdown → HTML, the rule checks with no other home (its row in `analysis/AUTHORING.md` §5, and a comparison's fence and length rules), and the 재작성본 sibling marker |
| `builder/mdext/` | `probefence.py` (the ` ```probe-* ` fences and their schemas, `probe-matrix` and `probe-figs` included), `callouts.py` (R9 GFM alerts → `co-*`), `ghmath.py` (the `` $`x`$ `` dialect) |
| `builder/primers.py` | The background cards a comparison opens on (`primer:`) — a drawing and one line each |
| `builder/glance.py` | The 요약 tab and its checks (G1–G6) |
| `builder/comparisons.py` | Comparison discovery and validation (`comparison/AUTHORING.md`) |
| `builder/events.py` | `context/EVENTS.md` read row by row for the first screen's 일정, a malformed row reported as a problem |
| `builder/arxivtitles.py` | The arXiv title of each paper 빈자리 prints, from arXiv's metadata API under `--gap-titles` and kept as `arxiv-titles.json` under `.site-cache/` |
| `builder/scoutfigs.py` | Each written-up scouted paper's overview figure, picked from its arXiv HTML edition under `--scout-figures` and kept as `scout-figures.json` under `.site-cache/` |
| `builder/scouting.py` | Scouting run discovery — each `scouting/P#/<date>.md` and its run file `scouting/runs/<date>.md` read against `scouting/AUTHORING.md` and merged by date into one row per arXiv id |
| `builder/lineage.py`, `builder/assets/lineage.css`, `lineage.js` | 계보 — the graph read from each rewrite's `probe-lineage` rail and arXiv links, read one paper at a time for that paper's 계보 tab, and once over the whole corpus for 빈자리, the papers it stands on and has not rewritten, at the foot of the analysis list |
| `builder/charts.py`, `builder/assets/charts.css` | The drawn results chart (`probe-chart`) as inline SVG, and the rules it is drawn with — borrowed by `distinction/render-distinction.py`, never linked by a site page |
| `builder/pages.py`, `components.py` | Page assembly — the first screen at the root, 탐색 (`s/`), the analysis list (`p/`), 비교 (`c/`), 서재 (`shelf/`), the paper page and its tabs, and the mastheads each list page opens on |
| `builder/decisions.py` | The `context/P*.md` Decision-Log parser behind the `D<n>` tooltips, and each pillar's introduction and decision titles for the axis-chip popup |
| `builder/catalog.py` | The corpus as data for an agent — `corpus.json`, `llms.txt` and the per-section Markdown under `p/<id>/s/` |
| `builder/arxiv.py` | LaTeXML extraction of an arXiv original, for the prompts: `python3 -m builder.arxiv <id>` from this folder prints the section tree, figures and table captions; `--grep <regex>` the matching lines with their §, `--tables` every table as Markdown, `--section <anchor>` one section's text, `--bib` the bibliography with each arXiv id's first-version month |
| `builder/arxivsrc.py` | The LaTeX source arXiv serves, read in memory into the same `Paper` when a paper has no HTML edition — `builder.arxiv` falls back to it, so every flag above works on either |
| `builder/katex.py`, `katex-render.mjs` | Server-side math, cached by `sha256(tex\|display)` under `.site-cache/` |
| `builder/fonts.py` | Webfont subsetting — Gowun Dodum merged from its range pieces, Pretendard behind it, JetBrains Mono for code |
| `builder/assets_out.py`, `builder/assets/` | The site's CSS, JS and icons, copied into the output tree. Each script opens on a comment stating what it owns |
| `search/` | Semantic search over the rewrites. Folder map: `site/search/README.md` |
| `query.py` | The same records as `corpus.json`, from a checkout and on the standard library alone — `python3 site/query.py --help` |
| `requirements.txt` | Build-time Python dependencies |

## Building locally

```bash
pip install -r site/requirements.txt
npm install --no-save --prefix site/builder \
  katex@0.16.22 pretendard jetbrains-mono @fontsource/gowun-dodum@5.3.0
python3 site/build-site.py --serve        # http://127.0.0.1:8000/probe/
```

`.github/workflows/deploy-site.yml` builds pull requests with `--strict` and
deploys from `main`; the published site makes zero third-party requests and
needs no runtime Python.
