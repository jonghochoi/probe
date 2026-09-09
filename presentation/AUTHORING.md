# presentation/AUTHORING.md

Format contract for the `presentation/` track — `presentation/<arxiv-id>.md`,
one talk per paper, rendered to slides plus a speaker essay under each. The
`/present` prompt owns the procedure (which paper, where the facts come from,
how to verify, how to commit); this file owns the format, and is the only place
a format rule is written.

A rewrite in `analysis/` is the entry condition: a presentation is built from
the paper's arXiv original and the rewrite together, never from the rewrite
alone.

**`context/` is not a source for this track.** A presentation argues from the
paper to a room. A `D#` citation on a slide is a claim about our own decisions
that the room did not come to hear, and it is the one thing on the slide a
listener cannot check against the paper — the rewrite's act 4 is where that
argument belongs, and it is one link away. This holds for the speaker essays
too.

## 1. The document

### 1-0. Front matter

```yaml
---
presentation_of: 2607.26055                 # the paper's arXiv id; matches the filename
title: "πR²: Reactive Real-time Flow Policies"
venue: Preprint · Carnegie Mellon University · 2026
audience: 랩 그룹 미팅 · action chunking·flow policy 에 익숙한 로보틱스 연구자
minutes: 14
spine: 지연을 견디는 문제가 아니라, 지연을 구조적으로 없애는 문제로 다시 쓴다
arxiv_html: 2607.26055v1            # the edition every number was confirmed in
generated: 2026-09-09 01:10
generator: presentation/v1
---
```

Every key but `generator` is required. Two of them do work the rest do not:

`spine` is the one sentence the talk exists to land, and it is written **before
the slides**. The test is that someone who disagrees with it can say so from
that line alone, without sitting through the presentation. A `spine` that describes the
method — rather than naming the turn — is not a spine yet.

It is also the cover slide's headline. On every other slide the header is the
claim and the body is its evidence; the cover reverses that — the header is the
hook and the spine underneath is what the room reads while the talk starts. So
the cover carries no `probe-facts` and needs none: the sentence is the slide.

A long spine takes its break the same way a title does (§5) — ` / `, at the
seam where the claim turns. The tab's one-line lead drops the marker; only the
cover honours it, because only the cover has the width to.

**The cover gives half its frame to the paper's own figure** — a
`probe-figure` fence with the same three keys every other figure takes. It is
the one place in a presentation where an image is not evidence: the room is not being
argued at yet, it is looking at what the talk is about while the talk starts,
and half a frame of something that is not type is most of why a title slide
reads as one. So the caption is written for that moment rather than for the
argument — what the room is looking at, in one line — and it rides over the
image with the `source` under it, because the cover has no evidence ribbon to
carry provenance and a photograph with no figure number is one the room cannot
look up.

Choose it the way a poster is chosen: the apparatus, the task, the moment of
contact. A teaser that is itself a diagram is a figure for a reader, and it
belongs on the `evidence` slide where the presentation argues with it.

**Without one, the act rail fills the frame.** It is not an exception to §4: it
argues nothing about the paper, because every value in it is the presentation's own
declaration — the act on each slide header, counted, with each run of a beat
weighted by the slides it holds. What it tells the room is how long this will
take and in what order, which is the one thing the spine cannot say. It is
drawn by the build from the headers, so there is nothing to author and nothing
that can disagree with the presentation. It is the fallback rather than the default: a
photograph from the paper says more to a room than the presentation's own proportions
do, and a cover that has one does not draw the rail as well.

`audience` is what makes a slide's omissions legible. A presentation written for a room
that already knows action chunking may skip explaining it; the same presentation for
another room is under-argued rather than tight, and only this line says which.

### 1-1. The spine

Every slide declares two things in its header, and both are in the source rather
than in the author's head:

```
## [轉 · statement] 모든 입력이 같은 속도로 / 처리될 필요는 없다
```

**The act** — one of `起` `承` `轉` `結`. The slide prints its Korean word and
not the glyph: the eyebrow saying `結 · 결과` is one line saying the same thing
twice, which is the defect §2 refuses everywhere else. The glyph is the author's
spine and the presenter's position marker, so it rides on the element as
`data-act` and the 발표자 노트 window shows it there. A presentation whose slides all sit in one
act is a table of contents, which is what the paper already is. `轉` carries the
paper's turn and needs two slides, not one: why the turn is permitted, and what
it costs. Everything else is compressible.

**The type** — the slide's shape, which decides its composition. One grid
stretched over every shape is what leaves holes. The types are `cover`,
`evidence`, `statement`, `split`, `versus`, `ledger`, `budget`, `timing`,
`lineage`.

**Two slides that make the same point are one slide.** When a created figure
starts saying what a later panel says, the panel goes and its substance folds
into the figure's `probe-script`. The count is an outcome, never a target.

## 2. Two registers

**Every element on every slide carries two layers — the claim, and what makes the
claim checkable.** One layer is a bullet; two is evidence. This is the rule that
decides whether a slide reads full, and it holds across every fence:

| Fence | Claim | Evidence |
|---|---|---|
| `probe-diagram` | `box` | `note` |
| `probe-timing` | `name` | `mark` |
| `probe-budget` | `label`, with `note` for what the segment is | `ms` |
| `probe-lineage` | year and name | `note` |
| `probe-facts` | `값` | `라벨` |
| `probe-versus`, `probe-ledger` | `t` | `n` |

The second layer is a number, a source, or the condition under which the claim
holds — `Figure 5 — 약 50 N 에서 정지, baseline 은 120 N 까지`, not a restatement.
**When the paper does not supply one, leave it out.** A slide with one bare item
among five is honest; an invented `n` is not, and the empty slot is itself a
finding worth saying out loud in the script.

**Both layers are literal text — no math fence.** The rewrites render KaTeX
because a page is read at a desk; a slide is read from across a room, where a
rendered fraction is a smudge and a subscript is gone. A presentation writes its symbols
out — `d₀`, `W₀`, `tanh(α)`, `0.25 d₀` — and a formula that cannot survive that
is a formula the room was not going to follow anyway. It belongs in the
rewrite.

## 3. Filling the frame

A slide reads thin because of how its content is distributed, not because the
type is too small. Enlarging type or figures is never the fix.

**3-1. Stretch the container, then distribute its items.** A card that hugs its
content leaves the slack outside it, where nothing can use it.

**3-2. Distribution is capped.** Spreading three short items over a full-height
card manufactures cavities rather than filling them — the gap has a maximum, and
whatever slack remains past that maximum splits evenly above and below the list.
Slack pushed to one end is a hole; slack halved at both ends is margin.

**3-3. A column closes on its own conclusion.** `foot` is one line on the bottom
rule saying what the column amounts to — `사는 자리는 국소 교정이다`. It anchors
the bottom edge so the last item does not float, and it moves the punchline from
the script onto the slide, where the audience can read it while it is being said.

**3-4. Every slide closes on the 근거 띠.** `probe-facts` is not decoration for
slides that came out short and it is not optional for the panel types. Three
cells, each a number the slide leans on; two cells when only two exist.

## 4. Created figures

`analysis/AUTHORING.md` R6 holds here — the paper's own figures, first. A drawn
figure is allowed only under these:

**4-1. Derivable, not interpretive.** Every box, row and edge quotes a sentence or
a number the paper states. A figure that adds a claim the paper does not make is
an argument, and arguments belong in the script where they can be attributed.

**4-2. `why` is required and names what it is not replacing.** It states which
figure of the paper covers this ground and what the drawn one strips out — see
`probe-flow` in `analysis/AUTHORING.md` for the same requirement.

**4-3. `probe-diagram` is for routing changes.** One lane becoming two and
merging is the shape of a paper that moved where a signal goes. Test it before
drawing: if `before` and `after` come out with near-identical boxes and the whole
difference lives inside the `note` strings, it is a table, not a figure — do not
draw it.

**4-4. `loop` marks state carried across timesteps.** A recurrence is the one
thing box-and-arrow prose cannot show, so it is drawn rather than written.

**4-5. Compression is admitted in the note.** When a per-layer operation is drawn
once, the `note` says `층마다`. A figure that quietly flattens structure is wrong;
one that flattens it and says so is a figure.

## 5. Line breaks

**5-1. Breaks are authored, never inherited from the container.** No `max-width`
that wraps a phrase because the box happened to end there. A line break is written
with ` / ` in the source and appears nowhere else.

**5-2. A break falls at a syntactic seam and leaves both halves readable alone.**
`모든 입력이 같은 속도로 / 처리될 필요는 없다` — the first half is already a claim.
`모든 입력이 같은 / 속도로 처리될 필요는 없다` is a wrap, not a break.

**5-3. A title breaks where its claim turns**, so the second line lands on the
word the slide is about.

## 6. The speaker essay

`probe-script` is what the presenter says while the slide is up, in the second
person, written to be read once and delivered from memory. On the site it is
what the 발표자 노트 window shows, on its own screen beside the stage — so it is
written to be glanced at under load, not studied.

**6-1. It never carries a fact the slide does not show.** A number that matters
enough to say belongs in `probe-facts` or in an `n`; the script points at it.

**6-2. It points at the `foot` rather than repeating it.** Once a conclusion is on
the slide, the script's job is to tell the audience where to look and why that
line is the one to keep.

**6-3. It carries the anticipated question.** `질문 나오면: …` is where a
comparison the slide has no room for goes.

## 7. Enforcement

Two gates, and they see different halves of this contract. The build validates
what it needs in order to draw a slide; the linter validates the rules a presentation
can break while rendering perfectly, which is exactly how a slide dump gets
published.

```bash
python3 site/build-site.py --out /tmp/probe-check --strict
python3 linters/check-presentation-format.py
```

`--check` alone reads front matter and the slide headers and writes nothing, so
it never draws a slide. `--out` is what makes the compositions run.

| Rule | Gate | What it refuses |
|---|---|---|
| §1 act and type declared, both known | build + linter | a header that is not `[<act> · <type>] <title>` |
| §1-1 the presentation has a turn, and more than one act | linter (build warns) | every slide in one act, or no `轉` |
| §1-1 a type's own fence is present | build | a `ledger` slide with no `probe-ledger` |
| §2 most panel items carry their second register | linter | a presentation under the 60 % floor — one item's missing `n` is allowed, a presentation of them is not |
| §2 no KaTeX on a slide | linter | `` $`…`$ `` — a slide is read from across a room, so symbols are literal text |
| §3-3 every panel column closes on `foot` | linter | a column whose last item holds the bottom edge |
| §3-4 every slide but the cover closes on the ribbon | linter | a slide with no `probe-facts` — the cover is exempt because its `spine` is the slide |
| §1-0 a cover figure carries `url`, `caption` and `source` | build | a cover image with no provenance — the cover has no ribbon to put it in |
| §3 at most three ribbon cells | build | a fourth — past three it is a table the room reads instead of listening |
| §4-2 a created figure states `why` | build + linter | `probe-diagram` without it |
| §6 every slide carries its speaker essay | linter | a slide with no `probe-script` |
| no `context/` material anywhere in a presentation | linter | a `D#` citation on a slide or in a script |
| the track's one rule | build | a presentation of a paper with no rewrite in `analysis/` — not published |

Three rules here no gate can see, and they are the ones that decide whether the
presentation is a talk: whether the header sequence argues (§1), whether §1-1's merge rule
was actually applied, and whether a `probe-diagram` should have been drawn at all
(§4-3). The `/present` prompt's self-check is where those are walked.
