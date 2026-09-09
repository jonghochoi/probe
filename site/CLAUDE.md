# site/CLAUDE.md

Rules for the reading site's generator. `site/README.md` maps what is in the
folder and how to build it locally; `site/search/README.md` does the same for
semantic search. This file is only the invariants a change here must not break.
Repo-wide rules are in the root `CLAUDE.md`.

## The build implements contracts it does not own

`analysis/AUTHORING.md`, `comparison/AUTHORING.md` and `presentation/AUTHORING.md` are
the rules; this folder enforces them. A new rule is written into the contract
first and checked here second — a rule that exists only in `builder/` is a rule
no author can read. The same holds in reverse: what the build refuses, the
contract must say.

## Invariants

**Only `analysis/`, `comparison/` and `presentation/` publish.** Nothing else in the
repo reaches the site — `scouting/` and `context/` are not published surfaces.

**Generated HTML is never committed.** `deploy-site.yml` builds it fresh; a
local build goes to `--out` and stays there.

**`D#` and `context/` material never reach the 요약.** `builder/glance.py`
refuses them, because that surface is what a reader lands on and it argues from
the paper alone.

**A comparison naming a paper with no rewrite is not published.**
`builder/comparisons.py` holds that line: every paper's own detail stays on its
own page, and the comparison links out.

**A presentation of a paper with no rewrite is not published.** `builder/presentations.py`
holds the same line for the same reason: a slide compresses, and the rewrite is
where the detail it dropped stays reachable. The presentation is a tab on that paper's
own page rather than a page of its own, so the link back is the page it is
already on — and `t/` is an index of those tabs rather than a second home for
them: every row it prints links into the paper page it belongs to.

**Every band draws what its own page holds.** `components.mast()` is one frame
for the destinations the nav names, and the drawing beside each title is that
page's own: 논문 the list, 비교 the fork a comparison opens, 발표 the four acts
a talk is cut into with what is said under each, 서재 the window a browser
keeps. A band that draws some *other* page's surface goes stale every time that
page changes — a drawing of the paper page's tab strip asserts a shape that
page stops having the moment a track is added, on a band whose own page has no
tabs at all. A new track that earns a destination draws what its own list
holds, and the ones already here stay true.

**Reader state never reaches the build.** 즐겨찾기, the 읽음 mark, 책갈피, memos
and the ids this browser has been shown live in that browser's `localStorage`
under `assets/shelf.js`, and the landing page size — a view setting rather than
a mark on a paper — under `probe.view.v1`. Both marks are set by the reader and
never inferred: neither opening a page nor scrolling to its end is evidence it
was read. This binds the drawings too — `components.shelf_art()` draws the four
kinds without drawing how full any of them is, because a picture that implies a
count leaks the same fact as markup that prints one.

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

**The pillar set is hard-coded in three places here** — `PILLAR_NAMES` with
the Korean `PILLAR_LABELS` beside it in `builder/corpus.py` (the build refuses
to start when the two name different pillars), `PILLARS` in
`search/function/search.ts`, and the `--p<n>` tokens with their `[data-p]`
rules in `builder/assets/site.css` and `index.css`. Adding a pillar walks the
checklist in `context/CLAUDE.md`.

## Before pushing

```bash
python3 site/build-site.py --check --strict --out /tmp/probe-check
```

A comparison's fence and length rules are checked while the page renders, so
`--out` is what makes them run. Touching `search/function/`, also:

```bash
npx esbuild@0.28.2 site/search/function/search.ts --loader:.ts=ts --outfile=/dev/null
```
