# context/CLAUDE.md

Rules for the human-owned research context. `context/MASTER.md` is the global
anchor; `context/P{0..7}.md` are the pillars a run actually reads. Repo-wide
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
edition's site — and nothing else in the folder. That prompt fixes what it may
write: only dates a venue's own site states, in one commit straight to
`main`. Which venues are followed stays the human's: a venue is added or
dropped by hand, and a row a person added for a venue outside that list is
never touched by the routine.

Ownership inside the folder is just as fixed. The Open Questions, Tracked
Literature and Anti-topics are **owned by the relevant `P#.md`**;
`MASTER.md` holds only what crosses pillars — Purpose, Long-term Context,
the P0–P7 overview, Venue, Cross-pollination. Edit the
`P#.md` for pillar content and `MASTER.md` only for global content; the same
fact in both is one of them going stale.

## Open-question entry format

A pillar is a set of open questions — what the axis keeps asking, and the
threads the corpus has followed on each — not a record of answers. The
operator's own answers and bets, where they hold any, belong in the private
method file the distinction track reads (`distinction/templates/MY-METHOD.md`),
never here or in `MASTER.md`: an answer written into the context turns every
paper a run reads into evidence for or against it.

Every entry in a `P#.md` Open Questions section has exactly this shape.
`linters/check-decision-refs.py`, `linters/check-context-consistency.py` and
`site/builder/decisions.py` parse it, and every prompt that cites a `D#` reads
it, so it is load-bearing, not cosmetic:

```
#### [D<id>] <the question, in Korean> (P<m>)
- <what the question turns on>. Threads: <thread>; <thread>; ….
```

One `####` heading and one bullet per question, the bullet on one line.

1. **The title is the question, in Korean.** The axis popup prints it to a
   Korean reader, so it is written in their language; the rest of the
   pillar file stays English. It asks; it never states an answer.
2. **The bullet opens with what the question turns on** — one or two
   sentences on why the axis keeps it open. No rationale for a choice, no
   evidence or results: those live in the rewrites and comparisons that cite
   the question.
3. **`Threads:` lists the directions the corpus has followed**, separated by
   semicolons, none marked as preferred. A paper is named only as a pointer to
   where a thread is argued (`(XL-VLA)`). A thread is added when a paper opens
   one and dropped when nothing in the corpus argues it any more; the question
   itself is never closed.
4. **A question stands whatever its siblings' threads turn out to be.** One
   that only makes sense under one thread of another is folded into that one.
5. **Plain text.** No bold, no TeX, no emoji, and at most 420 characters — a
   bullet longer than that is carrying an argument.

`linters/check-context-consistency.py` holds every pillar file to this shape.

`<id>` is `D` + one digit + two letters (`I` and `O` excluded, so nothing
reads as a `1` or a `0`) — drawn at random, unique across the repo, and
**opaque**. It carries no pillar and no order: ownership comes from the file
the question is defined in, which is what `site/builder/decisions.py` already
reads, and a leading digit keeps a model name like `DINO` from matching. An
id is never re-issued, so a question that is folded into another or dropped
leaves no gap to fill. Its id goes on `context/MASTER.md`'s `Retired:` line so
it is never re-issued, and every citation of it in `analysis/`, `comparison/`
and `scouting/` is rewritten to the id it folded into, in the same change — or
dropped, where the question became a premise rather than part of another.

Rephrasing a question or its threads rewrites the bullet in place. The file
carries what is asked now and never a history of what it asked before —
`git log` already knows which wording a document argued with.

The allocation, kept in step with the files by hand:

| Pillar | Questions |
|---|---|
| P0. Retargeting & Human-in-the-Loop Data Collection | D2KT, D7HF, D5VN, D8LC |
| P1. VLA Datasets & Benchmarks | D4ML, D1AL, D6SE |
| P2. Pretraining for Data-Efficient Adaptation | D3RP, D3WV, D9QJ, D6JW, D1WE |
| P3. Observation Design | D8EJ, D9NB, D2DV, D3AG, D1SX |
| P4. Forward Prediction | D3FQ, D8XB, D9KS, D6FM |
| P5. Heterogeneous Action Expert Decomposition | D3GS, D1QT, D9ZP |
| P6. Action Timing & Motion Quality | D1MZ, D3MR, D0BZ |
| P7. Memory & Long-Horizon Structure | D5GY, D3HN, D7KC, D4WB |

## The other pillar sections

`context/_TEMPLATE.md` is the skeleton; these are the shapes inside it that
every pillar keeps the same, so the pillar files read as one document:

- **Questions** is one line, `**Questions**: <short form> (D<id>), …` —
  every question of the pillar in the order §2 lists them.
- **Thesis tie** opens `**Thesis tie** — why this axis is asked:` — what is
  open on the axis, stated as a tension the questions keep open and never as
  a bet on how it resolves. Where the axis has a common default, it stays in
  the questions as a thread, the baseline the others are measured against,
  and **Anti-topics** never exclude a thread: they drop papers that assert
  one without measuring it, or that fall outside the axis, never the thread
  itself.
- **Premises** is one paragraph, `**Premises** — …`, and only where the
  pillar has any: the setting its questions are asked in — the class of hand,
  a notation, a usage bar — stated as fact, never as a question. It names no
  specific hardware or weights the operator uses; those are private, with the
  stance.
- **Scouting lens** is a ladder of three numbered tiers, each a bold name and
  a sentence: tier 1 is the north star, tier 3 the outermost ring a run still
  surfaces. It closes on `Recall runs wide across all three; the ranking
  anchor stays tier 1.`
- **The Open Questions section opens with one paragraph**: `The questions
  this pillar keeps open. Each names what it turns on and the threads the
  corpus has followed so far; none is waiting to be closed, and a thread is
  added when a paper opens one.`
- **An external pin's Role** opens with its bold tier on the §1 ladder
  (`**tier 1**`, or `**tier 1 · ego**` where a kind beside the tier helps),
  then an em dash, what the paper is and what it bears on, and ends with the
  questions it anchors in parentheses (`(D8EJ, D9NB)`).

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

The site's axis-chip popup prints it above the pillar's open questions
(`site/builder/decisions.py`); a run does not read it.

## When adding a new pillar

The pillars share one skeleton, owned by `context/_TEMPLATE.md`, and several
surfaces key off the pillar set without updating on their own. Walk this list
end to end; a half-added pillar silently drops out of the index and the lints:

- [ ] **Copy `context/_TEMPLATE.md` to `context/P<N>.md`** and fill every
      `<placeholder>`. Keep the template's section spine exactly —
      `linters/check-context-consistency.py` reads it back — and its
      `[STABLE]` / `[LIVING]` / `[AGENT-INPUT]` markers, which tell a run how
      to weigh each section (`context/MASTER.md` §0).
- [ ] **Draw ids for its questions** — `D` + digit + two letters, checked
      against every id already in the repo and against the `Retired:` line in
      `context/MASTER.md` (the build and `linters/check-decision-refs.py`
      both read it). Never reuse, renumber or re-issue.
      Record them in the allocation table above.
- [ ] **Add a row** to `context/MASTER.md` §3's pillar table — what the pillar
      owns in one line, its question count, and its file. The scope itself
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
      from the build — its prompt and both pillar guards read this object, an
      id missing here is dropped as a filter, and the live copy changes only
      when it is uploaded again by hand: `site/search/SETUP.md`); and the
      `--p<n>` token pair plus its `[data-p]` rules in
      `site/builder/assets/site.css` and `index.css` (plain CSS cannot loop).
      The lints need no edit — they glob the pillar files.
- [ ] **Run `python3 linters/check-doc-links.py`** — the new file's path
      references, and every doc now referencing it, must resolve.
