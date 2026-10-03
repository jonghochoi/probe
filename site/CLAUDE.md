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

**Only `analysis/`, `comparison/`, `presentation/` and `scouting/` publish.**
Nothing else in the repo reaches the site — `context/` is not a published
surface beyond the `D#` titles a tooltip prints.

**A scouting report is read as it was written.** `builder/scouting.py` reads
each report in the form of its own day: a score line where the report has
one, the `## 📊` heads of an earlier report otherwise. A report is the record
of a run, so the build never asks one to be rewritten, and only a report that
carries score lines is held to them. The page merges by arXiv id and orders
by the scores without printing one: a reader gets the Real score in words
(`scouting/AUTHORING.md` §5-3) and the rest stays in the reports.

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

**Every band draws what its own page holds.** The drawing beside each title in
`components.mast()` is that page's own — 논문 the list, 비교 a comparison's
fork, 발표 the four acts, 서재 the browser's window. A band that draws another
page's surface goes stale whenever that page changes.

**Reader state never reaches the build.** 즐겨찾기, the 읽음 mark, 책갈피, memos
and the ids this browser has been shown live in that browser's `localStorage`
under `assets/shelf.js` and `assets/memo.js`, and the landing page size — a view setting rather than
a mark on a paper — under `probe.view.v1`. Both marks are set by the reader and
never inferred: neither opening a page nor scrolling to its end is evidence it
was read. This binds the drawings too — `components.shelf_art()` draws the four
kinds without drawing how full any of them is, because a picture that implies a
count leaks the same fact as markup that prints one.

**The article frame is the stylesheet's.** What `analysis/AUTHORING.md` R12
forbids an author to write, `builder/assets/site.css` keeps:

- A 3px left accent band means "aside" — the 요약 block, the five callouts, a
  term panel, a quiz — and every such card squares off on that edge
  (`border-radius: 0 var(--radius) var(--radius) 0`), since a rounded band
  reads as a different component. A card inside a multi-card grid
  (`probe-split`) is keyed by its heading color, never a band.
- Every component owns its internal spacing; body paragraph and list margins
  apply only to the article flow, a callout body and a `::: details` body.
- A `###` section keeps its `id` (contents, scroll-spy and memo anchor resolve
  against it) but prints no `#` anchor glyph — `builder/render.py` never emits
  one, so the stylesheet has none to hide.
- Never `display:block` on an inline tag: `.X b{display:block}` catches body
  emphasis and breaks the line at every `<b>`. Titles get their own class, or
  a `>` child combinator.

**A browser with no script loses only the extras.** Every control removes
itself rather than sitting inert, and the landing list falls back to one page.

**A moving slide is a still first.** `builder/charts.py` draws every state a
stepped figure can be in and `builder/presentations.py` draws the authors' clip
over the paper's own figure; `assets/presentation.js` only chooses what is on
screen and computes no number the room reads. A clip that cannot play, a
printout and a browser with no script all get the figure or the first state —
never an empty frame — and nothing of a clip is fetched until the talk is a
slide away from it.

**One query is read by one rule.** `assets/match.js` is what both the landing
filter box and the ⌘K palette ask their question with; two surfaces answering
the same query differently is a bug, not two behaviours.

**`components.mark()` has copies in `assets/`.** The README's hero, track
icons and who-writes-what picture redraw it with their animation inlined
(`assets/CLAUDE.md`). Change the mark here and bring those into step.

**Two modules serve the prompts, not the build.** `builder/arxiv.py` (its CLI:
`site/README.md`) raises `Unavailable` when a paper has no HTML edition —
`/analyze`'s stop condition — and `builder/mdext/probefence.py` owns the
` ```probe-* ` fences. Both are called by hand from a run, so keep them
importable without the rest of the build.

**Search is an enhancement.** A build without `--search-api` emits no script and
the site makes no request. `site/search/verify.py` needs a key and egress, so it
is run by hand and never in CI.

**`corpus.json` carries front matter and relations, never bodies.** It exists
to fit one context window beside an agent's question, so a record points at the
raw Markdown (`source`) rather than holding it, and the build refuses the file
past `catalog.BUDGET`. From `context/` it carries only what the pages already
print in a `D#` tooltip — the code, its pillar and its title. Relations stay
one kind per field; only `neighbours` is a score, and it is `corpus.score`, the
rule the page's own neighbour row ranks by.

**Section files are the page's own headings, never a second parser.** A full
build writes each rewrite's H3s as `p/<id>/s/<anchor>.md` with
`p/<id>/sections.json` beside the page, cut by `catalog.section_files` and
named by the anchors `DocRenderer` gives the page — the anchors a search hit
returns. No reader surface links them; the page stays one page.

**`query.py` runs with the standard library.** An agent in a checkout has not
run `pip install`, so `query.py` and every `builder/` module it imports —
`catalog`, `corpus`, `comparisons`, `presentations`, `decisions` and theirs —
keep a third-party import out of module scope. `query.py search` is the one
subcommand that touches the network, and it points at `catalog --match` when
the endpoint cannot be reached.

**The pillar set is hard-coded, not read.** `PILLAR_NAMES` and `PILLAR_LABELS`
in `builder/corpus.py` (the build refuses to start when the two disagree),
`PILLARS` in `search/function/search.ts` and the `--p<n>` tokens in the CSS each
carry it. Adding a pillar walks the checklist in `context/CLAUDE.md`.

## What each build command sees

`python3 site/build-site.py --check --strict` stops after discovery and writes
nothing: front matter, the 요약 fences, a comparison's sources and fork, every
presentation check and the `corpus.json` budget. The rewrite body rules in
`render.py`, a comparison's fence and length rules, KaTeX and the asset
pipeline run only while pages render, so the full build —
`python3 site/build-site.py --strict --out /tmp/probe-check` — is the one that
sees them. The rest of the checks are in the root `CLAUDE.md`.
