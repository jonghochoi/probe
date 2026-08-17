# site/

Everything the reading site is made of — the authoring rules, the static-site
generator, and its build-time dependencies. The site publishes
`readable/<arxiv-id>.md` and nothing else; `analysis/` is not read at all.

The corpus itself stays at the repo root (`readable/`), next to the other two
agent-written tracks (`analysis/`, `scouting/`). This folder is human-owned
tooling and rules; the agent writes into `readable/` and reads from here.

## Layout

| Path | Role |
|---|---|
| `AUTHORING.md` | **The format contract for `readable/<id>.md`** — front matter, body rules R1–R14, render traps, what the build enforces. `.claude/prompts/readable.txt` defers to it; edit this file first, then the code |
| `build-site.py` | Build entry point. `--out` writes the tree, `--only <id>` builds one rewrite, `--check` lints and writes nothing, `--strict` fails on any warning, `--serve` previews under the deployed path |
| `builder/corpus.py` | Rewrite discovery, front-matter validation, pillar names, the R10 link vocabulary |
| `builder/render.py` | Markdown → HTML, plus the rule checks that have no other home (R2, R4, R5, R11, R14) |
| `builder/mdext/` | `probefence.py` (the ` ```probe-* ` fences and their schemas), `callouts.py` (R9 GFM alerts → `co-*`), `ghmath.py` (the `` $`x`$ `` dialect) |
| `builder/pages.py`, `components.py` | Landing page and paper page assembly |
| `builder/arxiv.py` | LaTeXML extraction of an arXiv original. Serves the prompt rather than the build: `python3 -m builder.arxiv <id>` from this folder prints the section tree, figure ids and URLs. Raises `Unavailable` when a paper has no HTML edition, which is `/readable-paper`'s stop condition |
| `builder/katex.py`, `katex-render.mjs` | Server-side math, cached by `sha256(tex\|display)` under `.site-cache/` |
| `builder/fonts.py`, `assets/` | Webfont subsetting and the site's CSS/JS. Visual rules live here, not in a rewrite (R12) |
| `requirements.txt` | Build-time Python dependencies |

`scripts/probe_refs.py` stays under `scripts/` — the Decision-Log parser is
shared with `check-decision-refs.py`, which lints the whole repo.

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
