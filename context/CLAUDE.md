# context/CLAUDE.md

Rules for the human-owned research context. `context/MASTER.md` is the global
anchor; `context/P{0..4}.md` are the pillars a run actually reads. Repo-wide
rules — commits, contributor-doc style, the local checks — are in the root
`CLAUDE.md`.

## The read-only boundary

`context/` is the research input, and the agent does not edit it. A run that
believes a pillar file is wrong or stale says so **in its report**, as a
proposal the human acts on; it never edits `MASTER.md` or a `P#.md` itself.
This file and the pillar template are contributor material rather than research
input, and are edited like any other doc. `EVENTS.md` is neither: it holds the
conference and submission dates the reading site's first screen counts down
to, read by the build (`site/builder/events.py`) and never by a research run.

`EVENTS.md` is also the boundary's one exception. The weekly follow routine
(`.claude/prompts/follow.txt`) writes it — the rows of its dates table, the
hosts it could not reach, and a venue's link when the venue moves to its next
edition's site — and nothing else in the folder. What it may write is fixed there: only dates a venue's own
site states, one commit straight to `main`. Which venues are followed stays
the human's: a venue is added or dropped by hand, and a row a person added for
a venue outside that list is never touched by the routine.

Ownership inside the folder is just as fixed. The Decision Log, Tracked
Literature and Anti-topics are **owned by the relevant `P#.md`**;
`MASTER.md` holds only what crosses pillars — Identity, Purpose, Long-term
Context, the P0–P4 overview, Venue, Cross-pollination. Edit the
`P#.md` for pillar content and `MASTER.md` only for global content; the same
fact in both is one of them going stale.

## Decision-Log entry format

Every entry in a `P#.md` Decision Log section has exactly this shape. The
scouting and analyze prompts, `linters/check-decision-refs.py` and
`site/builder/decisions.py` all pattern-match on it, so it is load-bearing,
not cosmetic:

```
#### [D<id>] <Decision title> (P<m>)
- **<the choice, in words>** — <what it commits to>. Tracked: <alternatives>. Deferred: <alternatives>. Reopens if: <condition>.
```

One `####` heading and one bullet per decision, the bullet on one line. An
`OPEN` decision appends ` — **OPEN**` to the title line, opens its bullet with
`**Working, not settled** — ` before the working choice, and ends it with
`Settles on: <the result that closes it>.`

The bullet is read by a run deciding whether a paper bears on the choice, and
by a reader of the site's axis popup, so every pillar writes it one way:

1. **The choice comes first, bold, in words.** Never an option code from a
   menu the file does not carry — `(iii) hybrid`, `(F) FiLM` say nothing to a
   reader who has not seen (i) and (ii). A choice that is a policy — what to
   scout, which license to prefer — is still stated as the stance taken, not
   as an instruction.
2. **After the em dash, what the choice commits to** — one or two sentences.
   No rationale, evidence or results: those live in the rewrites and
   comparisons that cite the decision. A paper is named only as a pointer to a
   style or lineage (`VGGT-style`, `the DexWM lineage`).
3. **Alternatives under fixed labels.** `Tracked:` is an alternative watched
   because it could replace the choice; `Deferred:` is one set aside until
   something changes. A label with nothing under it is left out.
4. **`Reopens if:`** names the result that would put the decision back to
   `OPEN`, where one is known. It is optional.
5. **Plain text.** No TeX, no emoji, and at most 420 characters — a bullet
   longer than that is carrying rationale.

`linters/check-context-consistency.py` holds every pillar file to this shape.

`<id>` is `D` + one digit + two letters (`I` and `O` excluded, so nothing
reads as a `1` or a `0`) — drawn at random, unique across the repo, and
**opaque**. It carries no pillar and no order: ownership comes from the file
the decision is defined in, which is what `site/builder/decisions.py` already
reads, and a leading digit keeps a model name like `DINO` from matching. An
id is never re-issued, so a decision that is dropped leaves no gap to fill and
a pillar's set never has to be contiguous.

Superseding a choice rewrites the bullet in place. The log carries what is
current and never a history of what it replaced — a version marker on a
one-line answer is a second thing to keep in step, and `git log` already knows
which choice a document argued with.

The allocation, which the lint reads back off these files:

| Pillar | Decisions |
|---|---|
| P0. VLA Datasets & Benchmarks | D4ML, D1AL, D6SE, D8SD |
| P1. Heterogeneous Body/Hand Action Expert | D3GS, D4QX, D1QT, D9ZP, D1MZ, D5SH, D6JW, D5DQ |
| P2. Structured Multimodal Observation Fusion | D8EJ, D9NB, D2DV, D3AG, D9WZ |
| P3. World Model | D3FQ, D8XB, D9KS, D6FM, D7VC |
| P4. Pretraining for Data-Efficient Adaptation | D3RP, D5ZL, D3WV, D9QJ, D1WE |

## The other pillar sections

`context/_TEMPLATE.md` is the skeleton; these are the shapes inside it that
every pillar keeps the same, so five files read as one document:

- **Tracked items** is one line, `**Tracked items**: <item> (D<id>), …` — every
  decision of the pillar in log order, open or not. Which ones are `OPEN` is
  the log's to say.
- **Scouting lens** is a ladder of three numbered tiers, each a bold name and
  a sentence: tier 1 is the north star, tier 3 the outermost ring a run still
  surfaces. It closes on `Recall runs wide across all three; the ranking
  anchor stays tier 1.`
- **The Decision Log opens with one sentence**: `The current choice per
  decision. The entry format and the allocation across pillars are
  `context/CLAUDE.md`'s.` — a range of ids says nothing, since ids carry no
  order.
- **An external pin's Role** opens with its bold tier on the §1 ladder
  (`**tier 1**`, or `**tier 1 · ego**` where a kind beside the tier helps),
  then an em dash, what the paper is and what it anchors, and ends with the
  decisions it anchors in parentheses (`(D8EJ, D9NB)`).

## Pillar introduction

A pillar file may carry one Korean introduction — what the axis takes on,
for a reader of the site rather than for a run. It is optional: a pillar
without one is complete, and `_TEMPLATE.md` does not ask for it. Where it
exists it is one blockquote, anywhere in the file, whose first line opens
`> **소개** —`:

```
> **소개** — <the axis in a few plain Korean sentences>
> <continuation lines, each opening `>`>
```

The site's axis-chip popup prints it above the titles of the pillar's
decisions (`site/builder/decisions.py`); a run does not read it.

## When adding a new pillar (P5+)

The pillars share one skeleton — owned by `context/_TEMPLATE.md` — and
several surfaces key off
the pillar set — none of them update automatically. Walk this list end to end;
a half-added pillar silently drops out of the index and the lints:

- [ ] **Copy `context/_TEMPLATE.md` to `context/P<N>.md`** and fill every
      `<placeholder>`. Keep the template's section spine and its `[STABLE]` /
      `[LIVING]` / `[AGENT-INPUT]` markers exactly — the pipeline
      pattern-matches on them.
- [ ] **Draw ids for its decisions** — `D` + digit + two letters, checked
      against every id already in the repo and against the `Retired:` line in
      `context/MASTER.md` (the build and `linters/check-decision-refs.py`
      both read it). Never reuse, renumber or re-issue.
      Record them in the allocation table above.
- [ ] **Add a row** to `context/MASTER.md` §4's pillar table — what the pillar
      owns in one line, its decision count, and its file. The scope itself
      belongs in the pillar file and is not restated there.
- [ ] **Create `scouting/P<N>/`** and add `<N>` to the scouting routine's
      pillar argument (`scouting/SETUP.md` §3).
- [ ] **Extend the pillar-keyed tooling** — four surfaces, one entry each,
      because none of them can read the pillar set from another:
      `PILLAR_NAMES` in `site/builder/corpus.py` (the build's source of truth —
      display order and the `P#` pattern derive from it, and an id outside it
      lands the paper in `UNCLASSIFIED`) together with the Korean
      `PILLAR_LABELS` the rail prints beside each id, which the build requires
      to name the same set; the §3-1 palette table in
      `scouting/AUTHORING.md` (the palette's source of truth); `PILLARS` in
      `site/search/function/search.ts` (a deployed function imports nothing
      from the build — its prompt and both pillar guards read this object, and
      an id missing here filters a search to nothing); and the `--p<n>` token
      pair plus its `[data-p]` rules in `site/builder/assets/site.css` and
      `index.css` (plain CSS cannot loop). The lints need no edit — they glob
      the pillar files.
- [ ] **Run `python3 linters/check-doc-links.py`** — the new file's path
      references, and every doc now referencing it, must resolve.
