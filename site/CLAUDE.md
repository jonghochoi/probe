# site/CLAUDE.md

Rules for the reading site's generator. `site/README.md` maps what is in the
folder and how to build it locally; `site/search/README.md` does the same for
semantic search. This file is only the invariants a change here must not break.
Repo-wide rules are in the root `CLAUDE.md`.

## The build implements contracts it does not own

`analysis/AUTHORING.md` and `comparison/AUTHORING.md` are the rules; this folder
enforces them. A new rule is written into the contract first and checked here
second — a rule that exists only in `builder/` is a rule no author can read.
The same holds in reverse: what the build refuses, the contract must say.

## Invariants

**Only `analysis/` and `comparison/` publish.** Nothing else in the repo
reaches the site — `scouting/` and `context/` are not published surfaces.

**Generated HTML is never committed.** `deploy-site.yml` builds it fresh; a
local build goes to `--out` and stays there.

**`D#` and `context/` material never reach the 요약.** `builder/glance.py`
refuses them, because that surface is what a reader lands on and it argues from
the paper alone.

**A comparison naming a paper with no rewrite is not published.**
`builder/comparisons.py` holds that line: every paper's own detail stays on its
own page, and the comparison links out.

**Reader state never reaches the build.** 즐겨찾기, the 읽음 mark, 책갈피, memos
and the ids this browser has been shown live in that browser's `localStorage`
under `assets/shelf.js`, and the landing page size — a view setting rather than
a mark on a paper — under `probe.view.v1`. Both marks are set by the reader and
never inferred: neither opening a page nor scrolling to its end is evidence it
was read.

**A browser with no script loses only the extras.** Every control removes
itself rather than sitting inert, and the landing list falls back to one page.

**One query is read by one rule.** `assets/match.js` is what both the landing
filter box and the ⌘K palette ask their question with; two surfaces answering
the same query differently is a bug, not two behaviours.

**`components.mark()` has copies in `assets/`.** The README's lockup, state
icons, track icons, tagline and flow diagram redraw it with their animation
inlined (`assets/CLAUDE.md`). Change the mark here and bring those into step.

**Two modules serve the prompt, not the build.** `builder/arxiv.py` extracts an
arXiv original — body and appendix, figures, tables — and raises `Unavailable`
when a paper has no HTML edition, which is `/analyze`'s stop condition;
`builder/mdext/probefence.py` owns the ` ```probe-* ` fences and their
validation. Both are called by hand from a run, so keep them importable without
the rest of the build.

**Search is an enhancement.** A build without `--search-api` emits no script and
the site makes no request. `site/search/verify.py` needs a key and egress, so it
is run by hand and never in CI.

**The pillar set is hard-coded in three places here** — `PILLAR_NAMES` in
`builder/corpus.py`, `PILLARS` in `search/function/search.ts`, and the `--p<n>`
tokens with their `[data-p]` rules in `builder/assets/site.css` and
`index.css`. Adding a pillar walks the checklist in `context/CLAUDE.md`.

## Before pushing

```bash
python3 site/build-site.py --check --strict --out /tmp/probe-check
```

A comparison's fence and length rules are checked while the page renders, so
`--out` is what makes them run. Touching `search/function/`, also:

```bash
npx esbuild@0.28.2 site/search/function/search.ts --loader:.ts=ts --outfile=/dev/null
```
