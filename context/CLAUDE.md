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
Literature, Anti-topics and Curated Lists are **owned by the relevant `P#.md`**;
`MASTER.md` holds only what crosses pillars — Identity, Purpose, Long-term
Context, Hardware, the P0–P5 overview, Venue, Cross-pollination. Edit the
`P#.md` for pillar content and `MASTER.md` only for global content; the same
fact in both is one of them going stale.

## Decision-Log entry format

Every entry in a `P#.md` §3 Decision Log has exactly this shape (used 32×
across the six pillars; the scouting and analyze prompts,
`linters/check-decision-refs.py` and `site/builder/decisions.py` all
pattern-match on it, so it is load-bearing, not cosmetic):

```
#### [D<n>] <Decision title> (P<m>)
- **v1**: <current first-attempt choice — **bold** the chosen alternative;
  tracked/deferred alternatives named inline; `OPEN` decisions append
  ` — **OPEN**` to the title line and mark the bullet `(working, not settled)`>
```

One `####` heading and one `- **v<k>**:` bullet per decision. `D<n>` stays
within the pillar's allocated range and is never renumbered; superseding a
choice bumps the bullet to `**v2**:` (etc.) in place — the old version's
rationale lives outside the context file, not as a second bullet.

The allocation, which the lint reads back off these files:

| Pillar | Decisions |
|---|---|
| P0. VLA Datasets & Benchmarks | D24–D27 |
| P1. Heterogeneous Body/Hand Action Expert | D1–D7 |
| P2. Structured Multimodal Observation Fusion | D8–D12 |
| P3. Hand-level System0 Module | D13–D18 |
| P4. Pretraining for Data-Efficient Adaptation | D19–D23 |
| P5. World Model | D28–D32 |

## When adding a new pillar (P6+)

The six pillars share an identical §1–§6 skeleton, and several surfaces key off
the pillar set — none of them update automatically. Walk this list end to end;
a half-added pillar silently drops out of the index and the lints:

- [ ] **Copy `context/_TEMPLATE.md` to `context/P<N>.md`** and fill every
      `<placeholder>`. Keep the §1–§6 spine and the `[STABLE]` / `[LIVING]` /
      `[AGENT-INPUT]` markers exactly — the pipeline pattern-matches on them.
- [ ] **Allocate a fresh, contiguous Decision range** (`D33+` — never reuse or
      renumber an existing `D#`). Record it in three places: the new `P<N>.md`
      §3 header, the allocation table above, and `context/MASTER.md` §5's
      pillar table.
- [ ] **Add the pillar overview** to `context/MASTER.md` §5 — scope, identity
      tie, tracked items, mirroring the existing §5.N blocks.
- [ ] **Create `scouting/P<N>/`** and deploy a scouting routine instance for it
      (replace every `<PILLAR>` token in `.claude/prompts/scouting.txt` per
      `scouting/SETUP.md`).
- [ ] **Extend the pillar-keyed tooling** — four surfaces, one entry each,
      because none of them can read the pillar set from another:
      `PILLAR_NAMES` in `site/builder/corpus.py` (the build's source of truth —
      display order and the `P#` pattern derive from it, and an id outside it
      lands the paper in 미분류); the §3-1 palette table in
      `scouting/AUTHORING.md` (the palette's source of truth); `PILLARS` in
      `site/search/function/search.ts` (a deployed function imports nothing
      from the build — its prompt and both pillar guards read this object, and
      an id missing here filters a search to nothing); and the `--p<n>` token
      pair plus its `[data-p]` rules in `site/builder/assets/site.css` and
      `index.css` (plain CSS cannot loop). The lints need no edit — both glob
      `context/P*.md`.
- [ ] **Run `python3 linters/check-doc-links.py`** — the new file's path
      references, and every doc now referencing it, must resolve.
