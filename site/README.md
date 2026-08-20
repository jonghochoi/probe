# site/

Everything the reading site is made of — the authoring rules, the static-site
generator, and its build-time dependencies. The site publishes
`analysis/<arxiv-id>.md` and nothing else.

One rewrite becomes **two tabs on one page** — 요약 (one screen, the tab a
reader lands on) and 상세 (the body). Both come out of the same source file and
the same `/analyze` run; `AUTHORING.md` §4 and §5 are their contracts.

The corpus itself stays at the repo root (`analysis/`), next to the other
agent-written track (`scouting/`). This folder is human-owned tooling and rules;
the agent writes into `analysis/` and reads from here.

## Layout

| Path | Role |
|---|---|
| `AUTHORING.md` | **The format contract for `analysis/<id>.md`** — front matter, body rules R1–R15, render traps, the 요약 rules G1–G7, what the build enforces. `.claude/prompts/analyze.txt` defers to it; edit this file first, then the code |
| `build-site.py` | Build entry point. `--out` writes the tree, `--only <id>` builds one rewrite, `--check` lints and writes nothing, `--strict` fails on any warning, `--serve` previews under the deployed path, `--index <file>` writes the search index and builds no pages, `--search-api <url>` points the landing page at a search endpoint (omitted, the site makes no requests) |
| `builder/corpus.py` | Rewrite discovery, the corpus's order (one `git log` over `analysis/`: a rewrite ranks by the commit that landed it — its add, or the `analysis: update` that redoes it — so 최근 is merge order and not the `generated:` stamp, and a redone rewrite lands again at the top. A build with no history to read says so and falls back to `generated:`), front-matter validation (including R6's `figures:` ↔ body agreement, R15's required `appendix:` and the tagline-echo check), pillar names, the R10 link vocabulary, and the two compacted haystacks the landing filter matches a query against — the paper's identity and everything the rewrite *names* (headings, term panels, figure captions), so a search reaches past the card's 240-character preview |
| `builder/render.py` | Markdown → HTML, plus the rule checks that have no other home (R2, R4, R5, R11, R14) |
| `builder/mdext/` | `probefence.py` (the ` ```probe-* ` fences and their schemas), `callouts.py` (R9 GFM alerts → `co-*`, and the callout length ceiling), `ghmath.py` (the `` $`x`$ `` dialect) |
| `builder/glance.py` | The 요약 tab — the four-part spine, the narrative's length band and bullet ban, the fact rail, exactly four evidence cards, and the refusal of any `D#` or `context/` material on this surface (G1–G7) |
| `builder/pages.py`, `components.py` | Page assembly — the landing briefing (newest rewrite as a lead block, everything else as one row each, facets in a left rail — including the reader's own three, New, Starred and Unread, which the filter bar prints a second copy of because the rail leaves at 900px and nothing else on a phone reaches what they select — and the 책갈피 strip above the lead — the three most recent marks as chips, carrying the arXiv id because three titles do not fit on a line and three ids always do), 내 서재 and the paper page. `components.mast_art()` draws the landing masthead's diagram beside the tagline — a scan lifts four pieces out of an original that stays shut, they wait in a rack over the mark, and they cross two at a time into the 요약 and 상세 tabs they become; geometry here, timing in `assets/index.css`, and the mark itself is `mark()` nested rather than redrawn |
| `builder/arxiv.py` | LaTeXML extraction of an arXiv original. Serves the prompt rather than the build: `python3 -m builder.arxiv <id>` from this folder prints the section tree — `── 본문 ──` and `── 부록 ──` separately, since R15 makes the appendix a checklist — plus figure ids and URLs, marking the inline-SVG figures that genuinely have no file to hotlink. Raises `Unavailable` when a paper has no HTML edition, which is `/analyze`'s stop condition |
| `builder/katex.py`, `katex-render.mjs` | Server-side math, cached by `sha256(tex\|display)` under `.site-cache/` |
| `builder/fonts.py`, `assets/` | Webfont subsetting and the site's CSS/JS. Visual rules live here, not in a rewrite (R12). `assets/shelf.js` is the one piece of state the build has no say in — 즐겨찾기, the 읽음 mark, the 책갈피 and the set of ids this browser has already been shown, kept in that browser's `localStorage` beside `memo.js`'s drafts. Both marks are set by the reader and never inferred — neither opening a page nor scrolling to the end of it is evidence that it was read — so the store holds exactly what they have claimed, and un-marking removes the record. 책갈피 is placed from two surfaces — a flag per row in the contents, and one button in the corner that marks the section on screen — and from neither of them the headings themselves, which keeps `render.py`'s rule that nothing appears under the cursor beside a heading, and 새 글 is a set difference rather than a last-visit timestamp, so a second device cannot make it lie. It paints whatever markup it finds (`[data-star]`, `[data-read-of]`, the paper header's `[data-paper-acts]`), so the landing list, the paper page and 내 서재 each load it and no page has to tell it which page it is. A browser with no script gets none of it and loses nothing else: every control removes itself rather than sitting inert |
| `builder/decisions.py` | The `context/P*.md` §3 Decision-Log parser, so a `D<n>` citation in a rewrite renders as a tooltip carrying the decision's title |
| `search/` | Semantic search over the published corpus — the chunker, the InsForge schema, the indexer and the endpoint. `build-site.py --index` writes its input; nothing else in the build depends on it. Folder map: `site/search/README.md` |
| `requirements.txt` | Build-time Python dependencies |

`linters/check-decision-refs.py` lints the same citations across the whole repo
and parses the log itself — it must run without the site's build dependencies,
so the two parsers stay separate.

## Building locally

```bash
pip install -r site/requirements.txt
npm install --no-save --prefix site/builder \
  katex@0.16.22 pretendard @fontsource/jetbrains-mono
python3 site/build-site.py --serve        # http://127.0.0.1:8000/probe/
```

Generated HTML is **never committed** — `.github/workflows/deploy-site.yml`
builds it fresh on every push to `main` and deploys to GitHub Pages; pull
requests build with `--strict` without deploying. The published site makes zero
third-party requests and needs no runtime Python.
