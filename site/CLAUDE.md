# site/CLAUDE.md

Rules for the reading site's generator. `site/README.md` maps what is in the
folder and how to build it locally; `site/search/README.md` does the same for
semantic search. This file is only the invariants a change here must not break.
Repo-wide rules are in the root `CLAUDE.md`.

## The build implements contracts it does not own

`analysis/AUTHORING.md` and `comparison/AUTHORING.md` are the rules; this
folder enforces them. A new rule is written into the contract
first and checked here second — a rule that exists only in `builder/` is a rule
no author can read. The same holds in reverse: what the build refuses, the
contract must say.

## Invariants

**Only `analysis/`, `comparison/` and `scouting/` publish.**
Nothing else in the repo reaches the site — `context/` is not a published
surface beyond the `D#` titles a tooltip prints, the dates of
`context/EVENTS.md`, which the first screen counts down to, and what an axis
chip's popup prints: each pillar's optional introduction and the titles of
its open questions.

**A scouting report is read, never rewritten.** `builder/scouting.py` reads
each paper's scores off the score line under its header line, and a paper
section without one is reported. A report is the record of a run, so the
build never asks one to be rewritten. The page merges by arXiv id and orders
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

**A band is its eyebrow and its title, and nothing beside them.**
`components.mast()` prints those two lines and no more: whatever sits next to
the title either repeats the list under the band or argues for it, and the
list makes its own case one scroll down. The four bands are one height, so
moving between them in the nav moves nothing but the words.

**계보 is read, never written.** `builder/lineage.py` draws only what the
rewrites already say — a `probe-lineage` rail entry and an arXiv link in the
prose — so no file exists to keep in step with the corpus. It is a tab of a
paper's page — what that paper stands on and what stands on it — and one list
at the foot of the analysis list, 빈자리: the papers several rewrites stand on
that the corpus has no rewrite of. There is no page of the whole graph and no
ranking of what to read. A partial build (`--only`) prints neither, since a
corner of the corpus shows every paper's ancestors as missing.

**Reader state never reaches the build.** 즐겨찾기, the 읽음 mark, 책갈피, memos
and the ids this browser has been shown live in that browser's `localStorage`
under `assets/shelf.js` and `assets/memo.js`; the analysis list's page size
— a view setting rather than a mark on a paper — under `probe.view.v1`; and
the reader's colour under `probe.accent`. Both marks are set by the reader and
never inferred: neither opening a page nor scrolling to its end is evidence it
was read.

**The article frame is the stylesheet's.** What `analysis/AUTHORING.md` R12
forbids an author to write, `builder/assets/site.css` keeps:

- A 3px left accent band means "aside" — the five callouts, a term panel, a
  quiz — and every such card squares off on that edge
  (`border-radius: 0 var(--radius) var(--radius) 0`), since a rounded band
  reads as a different component. A card inside a multi-card grid
  (`probe-split`) is keyed by its heading color, never a band. The 요약
  cards are the surface, not asides: each is named by an underlined head
  and a glow from its top edge, and carries no band. Inside the story a
  move is named in the margin beside it, never by a band either.
- Every component owns its internal spacing; body paragraph and list margins
  apply only to the article flow, a callout body and a `::: details` body.
- A `###` section keeps its `id` (contents, scroll-spy and memo anchor resolve
  against it) but prints no `#` anchor glyph — `builder/render.py` never emits
  one, so the stylesheet has none to hide.
- Never `display:block` on an inline tag: `.X b{display:block}` catches body
  emphasis and breaks the line at every `<b>`. Titles get their own class, or
  a `>` child combinator.

**A browser with no script loses only the extras.** Every control removes
itself rather than sitting inert, and the analysis list falls back to one page.

**One query is read by one rule.** `assets/match.js` is what both the analysis
list (a `#q=` address) and the ⌘K palette ask their question with; two
surfaces answering the same query differently is a bug, not two behaviours.

**`components.mark()` has copies in `assets/`.** The README's hero, track
icons and who-writes-what picture redraw it with their animation inlined
(`assets/CLAUDE.md`), and `builder/assets/` carries it as the site's icons —
`favicon.svg`, and `favicon-32.png` and `apple-touch-icon.png` rendered from
it, which are what a phone's home-screen shortcut shows — and as `og.png`, the
1200×630 card a pasted link unfurls with. Change the mark here and bring all
of those into step. The first screen draws it with `wardrobe=True`: the
README track icons' props plus three of its own (a deadline's sweat, a new
post's confetti, the night's sleep), every one hidden until `home.js` names a
costume, so the bare mark it draws is the one those copies redraw. A prop
changed in a track icon is changed in the wardrobe too.

**Three modules serve the prompts as well as the build.** `builder/arxiv.py`
(its CLI: `site/README.md`) reads a paper's HTML edition, falling back to
`builder/arxivsrc.py` for the LaTeX source, and raises `Unavailable` only when
there is neither — `/analyze`'s stop condition — and
`builder/mdext/probefence.py` owns the ` ```probe-* ` fences. All three are
called by hand from a run, so keep them importable without the rest of the
build. `arxiv.py` also runs from the repo root as
`python3 site/builder/arxiv.py`, and its `__main__` block calls
`builder.arxiv`'s own `_main`: run as a second module, it would raise an
`Unavailable` its handler cannot catch. The build's one use of `arxiv.py` is
`builder/scoutfigs.py`.

**The distinction track draws with four pieces of this folder.**
`distinction/render-distinction.py` draws the private versus notes, reports
and code notes with `builder/charts.py` and `assets/charts.css`, which exist
for it alone and no site page links, and with `builder/decisions.py` and the
`:root` blocks of `assets/site.css`, which it shares with the site. It runs on
the standard library and its pages never reach the site, so keep those two
modules free of a third-party import at module scope.

**The build reaches the network only when asked.** `--scout-figures` fetches
the arXiv HTML of each written-up scouted paper to pick its overview figure,
and every answer stays in `scout-figures.json` under `.site-cache/`;
`--gap-titles` asks arXiv's metadata API for the title of each paper 빈자리
prints, kept in `arxiv-titles.json` beside it. Without a flag the build prints
what its cache holds: a paper it lacks shows no figure, or its rail name with
no title. A paper arXiv cannot reach is not remembered, so the next fetch asks
again.

**Search is an enhancement.** A build without `--search-api` carries no
endpoint in `assets/corpus-index.js`, so the ⌘K palette shows no 의미 tab and
the site makes no request. `site/search/verify.py` needs a key and egress, so it
is run by hand and never in CI.

**`corpus.json` carries front matter and relations, never bodies.** It exists
to fit one context window beside an agent's question, so a record points at the
raw Markdown (`source`) rather than holding it, and the build refuses the file
past `catalog.CORPUS_JSON_BUDGET`. From `context/` it carries only what the
pages already print in a `D#` tooltip — the code, its pillar and its title.
Relations stay one kind per field; only `neighbours` is a score, and it is
`corpus.score`, the rule the page's own neighbour row ranks by.

**Section files are the page's own headings, never a second parser.** A full
build writes each rewrite's H3s as `p/<id>/s/<anchor>.md` with
`p/<id>/sections.json` beside the page, cut by `catalog.section_files` and
named by the anchors `DocRenderer` gives the page — the anchors a search hit
returns. No reader surface links them; the page stays one page.

**`query.py` runs with the standard library.** An agent in a checkout has not
run `pip install`, so `query.py` and every `builder/` module it imports —
`catalog`, `corpus`, `comparisons`, `decisions` and theirs —
keep a third-party import out of module scope. `query.py search` is the one
subcommand that touches the network, and it points at `catalog --match` when
the endpoint cannot be reached.

**The pillar set is hard-coded, not read.** `PILLAR_NAMES` and `PILLAR_LABELS`
in `builder/corpus.py` (the build refuses to start when the two disagree),
`PILLARS` in `search/function/search.ts` and the `--p<n>` tokens in the CSS each
carry it. Adding a pillar walks the checklist in `context/CLAUDE.md`.

## What each build command sees

`python3 site/build-site.py --check --strict` stops after discovery and writes
nothing: front matter, the 요약 fences, a comparison's sources and fork and the
`corpus.json` budget. The rewrite body rules in
`render.py`, a comparison's fence and length rules, KaTeX and the asset
pipeline run only while pages render, so the full build —
`python3 site/build-site.py --strict --out /tmp/probe-check` — is the one that
sees them. The rest of the checks are in the root `CLAUDE.md`.
