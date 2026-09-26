# presentation/AUTHORING.md

Format contract for the `presentation/` track — `presentation/<arxiv-id>.md`,
one talk per paper, rendered to slides plus a speaker essay under each. The
`/present` prompt owns the procedure (which paper, where the facts come from,
how to verify, how to commit); this file owns the format, and is the only place
a format rule is written.

The track's one rule: **only a paper with a rewrite in `analysis/` may have a
presentation.** A slide compresses, and the rewrite is where what it dropped
stays one link away.

## 1. The document

### 1-0. Front matter

```yaml
---
presentation_of: 2607.26055                 # the paper's arXiv id; matches the filename
title: "πR²: Reactive Real-time Flow Policies"
venue: Preprint · Carnegie Mellon University · 2026
audience: 랩 그룹 미팅 · action chunking·flow policy 에 익숙한 로보틱스 연구자
minutes: 14
spine: 지연을 견디는 문제가 아니라, / 지연을 구조적으로 없애는 문제로 다시 쓴다
arxiv_html: 2607.26055v1            # <id>v<n> — the edition every number was confirmed in
generated: 2026-09-09 01:10         # YYYY-MM-DD HH:MM
generator: presentation/v1
---
```

Every key but `generator` is required. Two of them do work the rest do not:

`spine` is the one sentence the talk exists to land. The test is that someone
who disagrees with it can say so from that line alone, without sitting through
the presentation. A `spine` that describes the method — rather than naming the
turn — is not a spine yet.

It is also the cover slide's headline. On every other slide the header is the
claim and the body is its evidence; the cover reverses that — the header is the
hook and the spine underneath is what the room reads while the talk starts. So
the cover carries no `probe-facts` and needs none: the sentence is the slide.
A long spine takes its break the same way a title does (§5) — ` / `, at the
seam where the claim turns. Only the cover honours it; the 발표 index drops the
marker, since a row is not that width.

**The cover gives half its frame to the paper's own figure** — a
`probe-figure` fence (§1-2). It is the one place in a presentation where an
image is not evidence: the room is looking at what the talk is about while the
talk starts. So the caption is written for that moment rather than for the
argument — what the room is looking at, in one line — and `source` rides under
it, because the cover has no evidence ribbon to carry provenance. Choose it the
way a poster is chosen: the apparatus, the task, the moment of contact. A
teaser that is itself a diagram is a figure for a reader, and it belongs on an
`evidence` slide where the presentation argues with it.

**Without one, the act rail fills the frame** — drawn by the build from the
slide headers, so there is nothing to author. It is the fallback rather than
the default: a photograph from the paper says more to a room than the
presentation's own proportions do.

`audience` is what makes a slide's omissions legible. A presentation written
for a room that already knows action chunking may skip explaining it; the same
presentation for another room is under-argued rather than tight, and only this
line says which.

### 1-1. The spine

Every slide declares two things in its header, and both are in the source rather
than in the author's head:

```
## [轉 · statement] 모든 입력이 같은 속도로 / 처리될 필요는 없다
```

**The act** — one of `起` `承` `轉` `結`. The slide prints the act's Korean word
(상황, 막다른 길, 전환, 결과), not the glyph, so write no act label into the
title yourself. A presentation whose slides all sit in one act is a table of
contents, which is what the paper already is. `轉` carries the paper's turn and
needs two slides, not one: why the turn is permitted, and what it buys. What it
costs is `結`'s to say, on a `ledger`. Everything else is compressible.

**The type** — the slide's shape, which decides its composition and the fence
it is drawn from (§1-2). The types are `cover`, `evidence`, `statement`,
`split`, `versus`, `ledger`, `budget`, `timing`, `lineage`.

**Two slides that make the same point are one slide.** When a created figure
starts saying what a later panel says, the panel goes and its substance folds
into the figure slide's `probe-script`. The count is an outcome, never a target.

### 1-2. The fences

A slide is its header, the fence its type is drawn from, and at most one each
of `probe-diagram`, `probe-facts` and `probe-script`. Every fence but
`probe-script` is JSON. These schemas are the presentation track's own: a
`probe-figure` or `probe-lineage` here is not the rewrites' fence of the same
name, and a key from `analysis/AUTHORING.md` is not read.

| Type | Its fence | Prose under the header draws as |
|---|---|---|
| `cover` | `probe-figure`, optional | `- ` bullets, under the spine |
| `statement` | none — `probe-diagram` is drawn here and nowhere else | the sub-line under the title |
| `evidence` | `probe-figure` | a claim line under the figure |
| `split` | `probe-figure` | `- ` bullets beside the figure |
| `versus` | `probe-versus` | nothing |
| `ledger` | `probe-ledger` | nothing |
| `budget` | `probe-budget` | a claim line |
| `timing` | `probe-timing` | nothing |
| `lineage` | `probe-lineage` | a claim line |

| Fence | Required keys | Optional keys | Limits |
|---|---|---|---|
| `probe-figure` | `url`, `caption`, `source` | `id` — the rewrite's figure id, not drawn | all three required ones non-empty |
| `probe-versus` | `left`, `right` — each a column | — | column: `head`, `lines`; optional `foot` |
| `probe-ledger` | `buy`, `sell` — each a column | — | as `probe-versus` |
| column `lines` item | `t` | `n` | a bare string is a line with no `n` |
| `probe-budget` | `항목` — list of `{label, ms}`; `제어주기` — `{label, ms}` | `이름` (the bar's label); `note` per `항목` | `ms` numeric |
| `probe-timing` | `span_ms`; `제어주기` — `{label, ms}`; `줄` — list of `{name, blocks}` | `mark` per row — `{at, label}` plus `us: true` on this paper's row | block: `label`, `at`, `ms`, optional `kind` — `wait` (default) or `run` |
| `probe-lineage` | `items` — list of `{when, what, gave}`; `me` — `{when, what, gave}` for this paper | — | no `current`, `note` or `link` |
| `probe-diagram` | `before` — `{label, chain}`; `after` — `{label, slow, fast, join, out}`; `why` | per box: `note`, `hot`, `loop` | box: `box`; `why` non-empty (§4-2) |
| `probe-facts` | a list of `{값, 라벨}` | — | at most three cells (§3-2) |
| `probe-script` | plain Markdown, paragraphs split by a blank line | — | not JSON |

A key the table does not name is not drawn.

### 1-3. No `context/` material

A presentation argues from the paper to a room. A `D#` citation on a slide is a
claim about our own decisions that the room did not come to hear, and it is the
one thing on the slide a listener cannot check against the paper — the
rewrite's act 4 is where that argument belongs, and it is one link away. This
holds for the speaker essays too.

## 2. Two registers

**Every element on every slide carries two layers — the claim, and what makes the
claim checkable.** One layer is a bullet; two is evidence. This is the rule that
decides whether a slide reads full, and it holds across every fence:

| Fence | Claim | Evidence |
|---|---|---|
| `probe-diagram` | `box` | `note` |
| `probe-timing` | `name` | `mark` |
| `probe-budget` | `label`, with `note` for what the segment is | `ms` |
| `probe-lineage` | `when` and `what` | `gave` |
| `probe-facts` | `값` | `라벨` |
| `probe-versus`, `probe-ledger` | `t` | `n` |

The second layer is a number, a source, or the condition under which the claim
holds — `Figure 5 — 약 50 N 에서 정지, baseline 은 120 N 까지`, not a restatement.
**When the paper does not supply one, leave it out.** A slide with one bare item
among five is honest; an invented `n` is not, and the empty slot is itself a
finding worth saying out loud in the script.

**Both layers are literal text — no math fence.** The rewrites render KaTeX
because a page is read at a desk; a slide is read from across a room, where a
rendered fraction is a smudge and a subscript is gone. A presentation writes
its symbols out — `d₀`, `W₀`, `tanh(α)`, `0.25 d₀` — and a formula that cannot survive that
is a formula the room was not going to follow anyway. It belongs in the
rewrite.

## 3. Filling the frame

A slide reads thin because its content stops short of the frame, not because
the type is too small. Enlarging type or figures is never the fix; the build
stretches and spaces what is there, and the author's part is the two closing
lines below.

**3-1. A column closes on its own conclusion.** `foot` is one line on the bottom
rule saying what the column amounts to — `사는 자리는 국소 교정이다`. It anchors
the bottom edge so the last item does not float, and it moves the punchline from
the script onto the slide, where the audience can read it while it is being said.

**3-2. Every slide closes on the 근거 띠.** `probe-facts` is not decoration for
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

**5-1. Breaks are authored.** ` / ` in the source is the only line break on a
slide, and it breaks in the slide title, the `spine` and a `statement` slide's
prose — everywhere else it prints as written. A title that is not broken by
hand wraps wherever the frame ends, which is a wrap rather than a break.

**5-2. A break falls at a syntactic seam and leaves both halves readable alone.**
`모든 입력이 같은 속도로 / 처리될 필요는 없다` — the first half is already a claim.
`모든 입력이 같은 / 속도로 처리될 필요는 없다` is a wrap, not a break.

**5-3. A title breaks where its claim turns**, so the second line lands on the
word the slide is about.

## 6. The speaker essay

`probe-script` is what the presenter says while the slide is up, in the second
person, written to be read once and delivered from memory. The presenter reads
it on a screen of its own beside the stage, so it is written to be glanced at
under load, not studied.

**6-1. It never carries a fact the slide does not show.** A number that matters
enough to say belongs in `probe-facts` or in an `n`; the script points at it.

**6-2. It points at the `foot` rather than repeating it.** Once a conclusion is on
the slide, the script's job is to tell the audience where to look and why that
line is the one to keep.

**6-3. It carries the anticipated question.** `질문 나오면: …` is where a
comparison the slide has no room for goes.

## 7. Enforcement

Two gates, and they see different halves of this contract. The build validates
what it needs in order to draw a slide; the linter validates the rules a
presentation can break while rendering perfectly, which is exactly how a slide dump gets
published.

```bash
python3 site/build-site.py --out /tmp/probe-check --strict
python3 linters/check-presentation-format.py
```

Every build row in the table below runs while the presentation is discovered,
so `--check` reports them too. What `--out` adds is the drawing itself — each
slide composed into the page — which `--check` stops short of.

| Rule | Gate | What it refuses |
|---|---|---|
| the track's one rule | build | a presentation of a paper with no rewrite in `analysis/` — not published |
| §1-0 front matter complete and well-formed | build | a missing key, an `arxiv_html` that is not `<id>v<n>` of this paper, a `generated` that is not `YYYY-MM-DD HH:MM` |
| §1-1 act and type declared, both known | build + linter | a header that is not `[<act> · <type>] <title>` |
| §1-1 the presentation has a turn, and more than one act | linter (build warns on one act) | every slide in one act, or no `轉` |
| §1-2 a type's own fence is present, and every JSON fence parses | build | a `ledger` slide with no `probe-ledger` |
| §1-2 every `probe-figure` carries `url`, `caption` and `source` | build | an image with no provenance — the room cannot look it up |
| §1-3 no `context/` material anywhere | linter | a `D#` citation on a slide or in a script |
| §2 most panel items carry their second register | linter | a presentation under the 60 % floor — one item's missing `n` is allowed, a presentation of them is not |
| §2 no KaTeX on a slide | linter | `` $`…`$ `` or `$$` |
| §3-1 every panel column closes on `foot` | linter | a column whose last item holds the bottom edge |
| §3-2 every slide but the cover closes on the ribbon | linter | a slide with no `probe-facts` — the cover is exempt because its `spine` is the slide |
| §3-2 at most three ribbon cells | build | a fourth — past three it is a table the room reads instead of listening |
| §4-2 a created figure states `why` | build + linter | `probe-diagram` without it |
| §6 every slide carries its speaker essay | linter | a slide with no `probe-script` |

Three rules here no gate can see, and they are the ones that decide whether the
presentation is a talk: whether the header sequence argues (§1-1), whether its
merge rule was actually applied, and whether a `probe-diagram` should have been
drawn at all (§4-3). The `/present` prompt's self-check is where those are walked.
