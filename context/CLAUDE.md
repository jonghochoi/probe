# context/CLAUDE.md

Rules for the human-owned research context. `context/MASTER.md` is the global
anchor; `context/P{0..5}.md` are the pillars a run actually reads. Repo-wide
rules — commits, contributor-doc style, the local checks — are in the root
`CLAUDE.md`.

## The read-only boundary

`context/` is the research input, and the agent does not edit it. A run that
believes a pillar file is wrong or stale says so **in its report**, as a
proposal the human acts on; it never edits `MASTER.md` or a `P#.md` itself.
This file and the pillar template are contributor material rather than research
input, and are edited like any other doc.

Ownership inside the folder is just as fixed. The Decision Log, Tracked
Literature and Anti-topics are **owned by the relevant `P#.md`**;
`MASTER.md` holds only what crosses pillars — Identity, Purpose, Long-term
Context, Hardware, the P0–P4 overview, Venue, Cross-pollination. Edit the
`P#.md` for pillar content and `MASTER.md` only for global content; the same
fact in both is one of them going stale.

## Decision-Log entry format

Every entry in a `P#.md` Decision Log section has exactly this shape (used 30×
across the five pillars; the scouting and analyze prompts,
`linters/check-decision-refs.py` and `site/builder/decisions.py` all
pattern-match on it, so it is load-bearing, not cosmetic):

```
#### [D<id>] <Decision title> (P<m>)
- <the current choice — **bold** the chosen alternative; tracked and deferred
  alternatives named inline; an `OPEN` decision appends ` — **OPEN**` to the
  title line and opens its bullet with `**Working, not settled** —`>
```

One `####` heading and one bullet per decision.

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

## When adding a new pillar (P6+)

The pillars share one skeleton — owned by `context/_TEMPLATE.md` — and
several surfaces key off
the pillar set — none of them update automatically. Walk this list end to end;
a half-added pillar silently drops out of the index and the lints:

- [ ] **Copy `context/_TEMPLATE.md` to `context/P<N>.md`** and fill every
      `<placeholder>`. Keep the template's section spine and its `[STABLE]` /
      `[LIVING]` / `[AGENT-INPUT]` markers exactly — the pipeline
      pattern-matches on them.
- [ ] **Draw ids for its decisions** — `D` + digit + two letters, checked
      against every id already in the repo and against the retired list in
      `linters/check-decision-refs.py`. Never reuse, renumber or re-issue.
      Record them in the allocation table above, and give
      `context/MASTER.md`'s pillar table the new row's count.
- [ ] **Add a row** to `context/MASTER.md` §4's pillar table — what the pillar
      owns in one line, its decision range, and its file. The scope itself
      belongs in the pillar file and is not restated there.
- [ ] **Create `scouting/P<N>/`** and deploy a scouting routine instance for it
      (replace every `<PILLAR>` token in `.claude/prompts/scouting.txt` per
      `scouting/SETUP.md`).
- [ ] **Extend the pillar-keyed tooling** — four surfaces, one entry each,
      because none of them can read the pillar set from another:
      `PILLAR_NAMES` in `site/builder/corpus.py` (the build's source of truth —
      display order and the `P#` pattern derive from it, and an id outside it
      lands the paper in `UNCLASSIFIED`); the §3-1 palette table in
      `scouting/AUTHORING.md` (the palette's source of truth); `PILLARS` in
      `site/search/function/search.ts` (a deployed function imports nothing
      from the build — its prompt and both pillar guards read this object, and
      an id missing here filters a search to nothing); and the `--p<n>` token
      pair plus its `[data-p]` rules in `site/builder/assets/site.css` and
      `index.css` (plain CSS cannot loop). The lints need no edit — both glob
      `context/P*.md`.
- [ ] **Run `python3 linters/check-doc-links.py`** — the new file's path
      references, and every doc now referencing it, must resolve.
