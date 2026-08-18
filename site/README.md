# site/

Everything the reading site is made of — the authoring rules, the static-site
generator, and its build-time dependencies. The site publishes
`analysis/<arxiv-id>.md` and nothing else; the legacy `analysis_legacy/` corpus
is not read at all.

One rewrite becomes **two tabs on one page** — 상세 (the body) and 한눈에 (one
screen). Both come out of the same source file and the
same `/analyze` run; `AUTHORING.md` §4 and §5 are their contracts.

The corpus itself stays at the repo root (`analysis/`), next to the other
agent-written track (`scouting/`). This folder is human-owned tooling and rules;
the agent writes into `analysis/` and reads from here.

## Layout

| Path | Role |
|---|---|
| `AUTHORING.md` | **The format contract for `analysis/<id>.md`** — front matter, body rules R1–R15, render traps, the 한눈에 rules G1–G7, what the build enforces. `.claude/prompts/analyze.txt` defers to it; edit this file first, then the code |
| `build-site.py` | Build entry point. `--out` writes the tree, `--only <id>` builds one rewrite, `--check` lints and writes nothing, `--strict` fails on any warning, `--serve` previews under the deployed path |
| `builder/corpus.py` | Rewrite discovery, front-matter validation (including R6's `figures:` ↔ body agreement, R15's required `appendix:` and the tagline-echo check), pillar names, the R10 link vocabulary |
| `builder/render.py` | Markdown → HTML, plus the rule checks that have no other home (R2, R4, R5, R11, R14) |
| `builder/mdext/` | `probefence.py` (the ` ```probe-* ` fences and their schemas), `callouts.py` (R9 GFM alerts → `co-*`, and the callout length ceiling), `ghmath.py` (the `` $`x`$ `` dialect) |
| `builder/glance.py` | The 한눈에 tab — the four-part spine, the narrative's length band and bullet ban, the fact rail, exactly four evidence cards, and the refusal of any `D#` or `context/` material on this surface (G1–G7) |
| `builder/pages.py`, `components.py` | Page assembly — the landing briefing (newest rewrite as a lead block, everything else as one row each, facets in a left rail), the memo hub and the paper page |
| `builder/arxiv.py` | LaTeXML extraction of an arXiv original. Serves the prompt rather than the build: `python3 -m builder.arxiv <id>` from this folder prints the section tree — `── 본문 ──` and `── 부록 ──` separately, since R15 makes the appendix a checklist — plus figure ids and URLs, marking the inline-SVG figures that genuinely have no file to hotlink. Raises `Unavailable` when a paper has no HTML edition, which is `/analyze`'s stop condition |
| `builder/katex.py`, `katex-render.mjs` | Server-side math, cached by `sha256(tex\|display)` under `.site-cache/` |
| `builder/fonts.py`, `assets/` | Webfont subsetting and the site's CSS/JS. Visual rules live here, not in a rewrite (R12) |
| `builder/decisions.py` | The `context/P*.md` §3 Decision-Log parser, so a `D<n>` citation in a rewrite renders as a tooltip carrying the decision's title |
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
