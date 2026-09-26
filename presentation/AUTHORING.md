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
presentation_of: <arxiv-id>         # the paper's arXiv id; matches the filename
title: "<the paper's title>"
venue: <venue, or Preprint> · <institution> · <year>
audience: <the room> · <what it already knows>
minutes: <the talk's length, in minutes>
spine: <the one sentence the talk lands — ` / ` at its seam>
arxiv_html: <arxiv-id>v<n>          # the edition every number was confirmed in
generated: YYYY-MM-DD HH:MM
generator: presentation/v2
---
```

Every key but `generator` and `lineage_drop` is required. `lineage_drop` is
written only by a talk that goes without one of its two lineage figures, and
says which and why (§4-9). Two of the required keys do work the rest do not:

`spine` is the one sentence the talk exists to land. The test is that someone
who disagrees with it can say so from that line alone, without sitting through
the presentation. A `spine` that describes the method — rather than naming the
turn — is not a spine yet.

It is also the cover slide's headline. On every other slide the header is the
claim and the body is its evidence; the cover reverses that — the header is the
hook and the spine underneath is what the room reads while the talk starts. So
the cover carries no evidence of its own and needs none: the sentence is the
slide. The hook is still a claim the paper makes — a cover line the paper does
not support is the first thing a sceptical room checks.
A long spine takes its break the same way a title does (§5) — ` / `, at the
seam where the claim turns. Only the cover honours it; the 발표 index drops the
marker, since a row is not that width.

**The cover gives the right of its frame to the paper's own figure**, bled to
the edge — a `probe-figure` fence (§1-2). It is the one place in a presentation
where an image is not evidence: the room is looking at what the talk is about
while the talk starts. The image is cropped to fill that column, and `focus`
says where the crop centres — `"focus": "12% 40%"`, across then down, as a
share of the image — because only the author knows where the apparatus is in a
wide figure. `focus` only pans: when the photograph shares its image with other
panels or with caption text set into the figure, `crop` (§1-3) cuts it to the
photograph first. `source` rides over the image, because the cover has no
other line to carry provenance; the `caption` — what the room is looking at, in
one line — is the image's alt text and the presenter's to say (§3-5). Choose it
the way a poster is chosen: the apparatus, the task, the moment of contact. A
teaser that is itself a diagram is a figure for a reader, and it belongs on an
`evidence` or `split` slide where the presentation argues with it.

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
## [<act> · <type>] <the slide's assertion>
```

For example, `## [轉 · statement] 모든 입력이 같은 속도로 / 처리될 필요는 없다`.

**The act** — one of `起` `承` `轉` `結`. The slide prints the act's Korean word
(상황, 막다른 길, 전환, 결과), not the glyph, so write no act label into the
title yourself. A presentation whose slides all sit in one act is a table of
contents, which is what the paper already is. `轉` carries the paper's turn and
needs two slides, not one: why the turn is permitted, and what it buys. What it
costs is `結`'s to say, on a `ledger`. Everything else is compressible.

The act is also what the room sees move: every slide's eyebrow draws the four
beats as four short bars — the ones behind solid, the current one long, the
ones ahead in outline — with the current beat's word beside them, each in its
act's colour. Nothing about it is authored beyond the header, and the only
other chrome is the page number.

**The type** — the slide's shape, which decides its composition and the fence
it is drawn from (§1-2).

`statement` is the one frame on its own ground — the page tinted toward the
`轉` colour, with a thick band of that colour down its left edge — so the room
knows it has reached the sentence the talk exists for without being told. The
frame stays in the theme's own ink: a turn that flips light to dark reads as a
different deck, not a louder beat of this one. **A talk has exactly one, and
it sits in `轉`**: a talk with three tinted frames has no turn, only three loud
slides, and a talk with none has left its signature to chance. Whatever
permits the turn goes under the sentence at the frame's width — the paper's
own figure, a chart of the numbers that force the turn, or a drawing of the
mechanism. The turn's sentence is the header; the line under it is its one
condition, and it takes an authored break (§5) like any headline.

**Two slides that make the same point are one slide.** When a created figure
starts saying what a later panel says, the panel goes and its substance folds
into the figure slide's `probe-script`. The count is an outcome, never a target.

### 1-2. The fences

A slide is its header, the fence its type is drawn from, and at most one each
of `probe-facts` and `probe-script` — plus a `probe-video` beside the figure of
an `evidence` or `split` slide (§8-1). Every fence but `probe-script` is JSON.
These schemas are the presentation track's own: a `probe-figure` here is not
the rewrites' fence of the same name, and a key from `analysis/AUTHORING.md` is
not read.

| Type | The evidence it carries | Its fence | Prose under the header draws as |
|---|---|---|---|
| `cover` | the paper's photograph, or the act rail (§1-0) | `probe-figure`, optional | `- ` bullets, under the spine |
| `evidence` | a paper figure wider than about 2 : 1, at the frame's width | `probe-figure`, optional `probe-video` | one claim line under the figure |
| `split` | a squarer paper figure at the frame's height | `probe-figure`, optional `probe-video` | two or three `- ` lines beside the figure |
| `chart` | the paper's result numbers, plotted — a sweep, categories, or one quantity against another (§4-6) | `probe-chart` | a claim line |
| `heat` | a value per position — a schedule, a mask — as a strip (§4-7) | `probe-heat` | a claim line |
| `timing` | call paths or workers on one clock (§4-8) | `probe-timing` | a claim line |
| `budget` | where one call's time goes, against the control period | `probe-budget` | a claim line |
| `statement` | the turn in one sentence, over the visual that permits it (§1-1) | one of `probe-figure`, `probe-chart`, `probe-heat`, `probe-timing`, `probe-diagram` — `probe-diagram` is drawn here and nowhere else | the condition line under the sentence |
| `contrast` | the priors against the properties the paper contrasts itself on — the gap it fills (§4-9) | `probe-contrast` | a claim line |
| `inheritance` | what flowed in from each prior, what the paper adds, and the question it leaves (§4-9) | `probe-inheritance` | a claim line |
| `versus`, `ledger` | two columns of claims — the one text slide (§1-3) | `probe-versus`, `probe-ledger` | nothing |

`evidence` or `split` is decided by the figure's shape, not by taste: a banner
of four photographs squeezed into a column is a strip of thumbnails, and a
square plot stretched across the frame is a small plot with white either side.
Either way the figure sits on a card of the paper's own white, so it reads as a
page laid on the slide in both themes.

| Fence | Required keys | Optional keys | Limits |
|---|---|---|---|
| `probe-figure` | `url`, `caption`, `source` | `id` — the rewrite's figure id, not drawn; `crop` (§1-3); `focus` on the cover (§1-0) | `crop` one to four percentages, `focus` two |
| `probe-video` | `clips` — `{src, label}`; `page`; `caption`; `source` | — | one or two clips, each an https `.mp4` or `.webm`; `label` on both sides of a pair (§8-1) |
| `probe-chart` | `kind` — `line`, `dots` or `scatter`; `series`; `source`; `why`; `omitted` | `vs`, `note` (`group` on `dots`), `clock`, `alt`; `step` per series; `steps` on a `line` (§8-2) | `line`: `x.ticks` and `y`, `values` per series; `dots`: `rows` and `x`; `scatter`: `x` and `y`, `points` per series (§4-6) |
| `probe-heat` | `cols`; `rows` — `{name, cells}`, or `{name, states}` when stepped; `source`; `why`; `omitted`; `illustrative` | `axis`, `value`, `scale`; per row `us`, `note`, `shared`, `regions`, `mark`, `step`; `steps`, `cycle` (§8-2) | cells in [0, 1] (§4-7) |
| `probe-timing` | `span_ms`; `제어주기` — `{label, ms}`; `줄` — list of `{name, blocks}`; `clock`; `why`; `illustrative` | `band`, `feeds`, `brace`, `눈금`, `source`; per row `mark`, `kind`, `dots`, `note`, `us`, `step` | block: `label`, `at`, `ms`, optional `kind` (§4-8) |
| `probe-budget` | `항목` — list of `{label, ms}`; `제어주기` — `{label, ms}`; `clock` | `이름` (the bar's label); `note` per `항목`; `출처` | `ms` numeric (§4-8) |
| `probe-contrast` | `cols`; `key`; `rows` — `{name, when, cells}`; `source`; `why`; `omitted` | `key_note`; per row `id`, `sub`, `us`, `step` | two to five `cols`, two to six `rows`; a cell is `●` `◐` `○` `–`, with `n` on a prior's (§4-9) |
| `probe-inheritance` | `lines` — `{when, name, gave, where}`; `me` — `{when, name, adds}`; `source`; `why`; `omitted` | `open` — `{text, where}`; `id` per node | one to four `lines` and `adds` (§4-9) |
| `probe-diagram` | `before` — `{label, chain}`; `after` — `{label, slow, fast, join, out}`; `why` | per box: `note`, `hot`, `loop` | box: `box`; `why` non-empty (§4-2) |
| `probe-facts` | a list of `{값, 라벨}` | — | at most three cells (§3-3) |
| `probe-script` | plain Markdown, paragraphs split by a blank line | — | not JSON |
| `probe-versus` | `left`, `right` — each a column | — | column: `head`, `lines`; optional `foot` (§3-2) |
| `probe-ledger` | `buy`, `sell` — each a column | — | as `probe-versus` |
| column `lines` item | `t` | `n` | a bare string is a line with no `n` |

A key the table does not name is not drawn.

### 1-3. One assertion, one piece of evidence

**The header is an assertion and the body is the evidence for it.** An
assertion is a sentence with its verb — `손끝이 50 N 에서 멈춘다`, not
`실험 결과` — something a listener could disagree with from the header alone. The
body is one visual that makes the room believe it: the paper's own figure, a
chart of the paper's numbers, or a drawing of something the paper states.
Words on the slide label that visual; they do not replace it.

**An assertion is no stronger than the paper's sentence under it.** Every
header, and the `spine`, rests on a sentence of the paper, and its quantifiers
— `모두`, `만`, `아니라`, `무너진다` — are read against that sentence. Where the
paper hedges — *also*, *not only … but also*, *partly*, *for example*, *up to*
— the header carries the hedge or narrows to the rows that hold. `X 가 아니라
Y` states that X was not bought; a paper that says "Y more than X" or "X and
also Y" supports `X 보다 Y` or `X 만이 아니라 Y`. A category claimed from the
paper's examples (`어려운 과제에선`, from two tasks it names *for example*)
is narrowed to those examples. This is the most common way a talk ends up
arguing past its paper, and it survives every gate, because the numbers under
an overclaim are all correct.

**The paper's own figures come first** where they carry the point at slide
scale. They are what the room would see if it opened the paper, and they carry
the authors' evidence in the authors' form. A created figure is for what the
paper states and does not draw — a mechanism given only as pseudocode or an
equation, a results table with no plot (§4). One figure family is shown one
way: a result drawn from the paper's numbers and the same result shown as the
paper's plot image, side by side, are two readings the room has to reconcile.

**A figure whose point is one panel is shown as that panel.** `crop` takes the
region to keep as CSS `inset()` takes it — top, right, bottom, left, in percent
of the image (`"crop": "0 0 0 79%"` keeps the right fifth) — and the card is
sized to the panel rather than to the page it came from. `source` then names
the panel (`Figure 2 (d)(e)`). When the panel the point lives in is still
unreadable cropped — a plot whose numbers are also printed in the text — the
numbers go on a `probe-chart` instead, and the figure family is shown that one
way.

**At most one slide in the talk is text alone** — a `ledger`, a `versus`, or a
`statement` without its visual. It is where the judgement goes, what the paper
buys and what it sells, and that is argued in words. Every other slide shows
something.

**At least one `結` slide shows a result working** — an `evidence` or `split`
slide on a result figure, or a `chart`. A talk that argues the turn and never
shows it paying off has skipped its evidence.

### 1-4. The storyboard comes before the fences

Before any fence is written, the talk exists as a list — one row per slide:
the act, the assertion, the visual that proves it, named by what the room
will look at (`Figure 5`, `Table 1 → dots`, `Figure 3 → line`), and the
paper's sentence the assertion rests on, quoted with its section. Read the
assertions alone, in order: they are what a listener retains, and they must
argue the `spine` without the slides. A row whose visual cell is empty is a
slide that does not know what it is showing yet; a row whose quoted sentence
is weaker than its assertion is an overclaim waiting to be said to a room
(§1-3).

Two rows of every storyboard are the lineage (§4-9) — a `contrast` in `承`
and an `inheritance` in `結` — and a talk that goes without one says why in
that row.

Most talks need no drawn mechanism at all. A talk of the paper's figures and
two or three charts of its tables is the common case; a `probe-timing`, a
`probe-heat` or a clip is for the paper whose point is one of those shapes,
not a feature every talk should use.

### 1-5. No `context/` material

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
| `probe-timing` | `name` | `mark`, or `note` on a worker row |
| `probe-budget` | `label`, with `note` for what the segment is | `ms` |
| `probe-contrast` | a cell's glyph | its `n` — the paper's sentence and section it rests on |
| `probe-inheritance` | `gave` — what flows in; `adds` | `where` — the section that says so |
| `probe-chart` | `note` or `group` — the takeaway, drawn on the chart | the plotted values, `source`, and `clock` when they were measured on one |
| `probe-heat` | row `name` | row `note`, and `source` for the values |
| `probe-facts` | `값` | `라벨` |
| `probe-versus`, `probe-ledger` | `t` | `n` — a number and its condition, at most six words |

The second layer is a number, a source, or the condition under which the claim
holds — `Figure 5 — 약 50 N 에서 정지, baseline 은 120 N 까지`, not a restatement.
**When the paper does not supply one, leave it out.** A slide with one bare item
among five is honest; an invented `n` is not, and the empty slot is itself a
finding worth saying out loud in the script.

**A second register is from the setup of the claim it sits under.** Model,
benchmark, level, hardware: an `n`, a ribbon cell's `라벨` or a drawing's row
note that comes from a different setup than its claim makes the claim look
measured where it was not — a simulation number under a real-robot claim, a
deployment GPU on a drawing timed on another. When a slide's argument really
does join two setups, its claim line or its script says so where the join
happens. §4-8 is this rule applied to clocks.

**Both layers are literal text — no math fence.** The rewrites render KaTeX
because a page is read at a desk; a slide is read from across a room, where a
rendered fraction is a smudge and a subscript is gone. A presentation writes its symbols
out — `d₀`, `W₀`, `tanh(α)`, `0.25 d₀` — and a formula that cannot survive that
is a formula the room was not going to follow anyway. It belongs in the
rewrite.

## 3. Filling the frame

A slide reads thin because its content stops short of the frame, not because
it has too few words. More text is never the fix: the build stretches and
spaces what is there, and gives the slack of a short slide to its visual and
its type size rather than to a second paragraph. The author's part is below.

**3-1. The word budget.** A slide puts at most **40 words** in front of the room
— counted as space-separated tokens, which in Korean is 어절.

- **Counted** — every sentence the room reads: the header, the prose line, the
  bullets, ribbon cells, panel heads, items and feet, diagram boxes and notes,
  budget labels and notes, timing row names, notes, marks and the brace
  label, a chart's one annotation (`note` or `group`, with its `sub`), a
  contrast's column heads and `key_note`, and an inheritance's `gave`, `adds`
  and open question.
- **Not counted** — the speaker essay (the room hears it); the provenance line
  — `source`, `clock`, `illustrative` — which is one line by §3-5; a paper
  figure's `caption`, which is not on the slide (§3-5); `why`, which closes the
  essay; a chart's or a strip's own labels and values — axis and tick labels,
  series and row names, row notes and region labels — which are the data; a
  lineage figure's names, dates, `sub`, `where` and a cell's `n`, which say
  who, when and where rather than what; a stepped figure's state labels and a
  clip's `label` and `caption` (§8), which name what is on screen; and a panel
  item's `n`.

The one text slide (§1-3) has no visual to carry its point, so its claims are
the evidence: **50**, counted over the header, heads, items and feet. Each
item's `n` is held to **six words** of its own instead of drawing on that
budget, so an item that carries its number costs no more than one that does
not — the two-register rule (§2) and the budget never trade a real item for a
second register. A slide past its budget is read instead of listened to — cut
to the assertion and its evidence, and move the rest into the script, where it
is said.

**3-2. A column closes on its own conclusion.** `foot` is one line on the bottom
rule saying what the column amounts to — `사는 자리는 국소 교정`. It anchors the
bottom edge so the last item does not float, and it moves the punchline from
the script onto the slide, where the audience can read it while it is being
said.

**3-3. The ribbon is for a number the visual cannot show.** `probe-facts` — at
most three cells — goes on a slide only when a number the slide leans on is not
already visible in its figure, chart or drawing. A ribbon that repeats what the
marks already say is the same fact twice, and a ribbon on every slide is a
template the room stops reading by the third. Most slides carry none. Its
cells count toward §3-1.

It is set as numbers, not as a table: the numerals in `값` are drawn large and
every word around them — the unit, `약`, `d =` — small beside them, so write
`값` as the number with its unit (`약 50 N`, `0.25 d₀`) and put the sentence in
`라벨`. A `값` with no numeral in it is set as a phrase, one size. Beside a
`split` figure it is the column next to the figure; everywhere else it closes
the slide.

**3-4. A build is for a comparison the room should see arrive.** `"step": k` on
a chart series or a timing row holds that item back until the presenter's k-th
press on the stage — the baselines first, then the method; the slow pipeline
first, then each device that shortens it. Only the stage holds a build: a
reader browsing the tab and the overview see the whole slide. Use it where the
order of arrival is the argument, not as decoration. A figure that steps
through states (§8-2) takes the same press, after the slide's builds.

**3-5. The room's floor.** Every line of content on a slide is set at or above
the size a room reads from the back — 1.5 % of the slide's content width,
which is 16 px in the tab and 26 px on a 1920 stage. Chrome (the act eyebrow,
the page number) may go under it; a figure's provenance, a ribbon label and a
panel item's `n` may not. What that rules out is fine print, and the rule that
follows from it is where a figure's description goes: **the slide prints one
line of provenance under a figure and nothing else** — `source`, the figure or
table number, its section, and the setup the numbers come from — and the
paper figure's `caption` is its alt text and closes the speaker essay, where
the presenter walks the room through it. The one line under the figure that
says what to see in it is the slide's claim line, which is the author's to
write for the room and already counts toward §3-1. Keep `source` to one line:
past that it is a second claim line set in the wrong face.

## 4. Created figures

`analysis/AUTHORING.md` R6 holds here — the paper's own figures, first. A drawn
figure is allowed only under these:

**4-1. Derivable, not interpretive.** Every box, row, mark and edge quotes a
sentence or a number the paper states. A figure that adds a claim the paper
does not make is an argument, and arguments belong in the script where they can
be attributed. A drawing whose times or values are illustrative says so in
`source` — `도식 · …` — and says what they are taken from.

**Any parameter the drawing chose is labelled on the slide.** A schedule
computed over twelve positions because twelve cells read at slide size, a
timeline cut at one tick to count an age — the room takes every number on a
figure for the paper's setting unless told. `illustrative` is that label: one
short phrase, printed as `예시 · …` in front of the provenance line, that names
the chosen value and, where the paper has its own, the paper's —
`<chosen> (실험 <the paper's>)`, e.g. `H = 12 · d = 3 (실험 16 / 50)`. Keep it a
label, not a sentence. Every `probe-heat` and `probe-timing` states it — the
string, or `false` when every parameter the drawing uses is the paper's own —
because almost every strip or worker drawing picks a setting, and one that
forgot to say so reads as the paper's.

**4-2. `why` is required and names what it is not replacing.** Every drawn
figure — `probe-diagram`, `probe-timing`, `probe-chart`, `probe-heat`,
`probe-contrast`, `probe-inheritance` — states
which figure of the paper covers this ground (or that none does) and what the
drawn one strips out; see `probe-flow` in `analysis/AUTHORING.md` for the same
requirement. It is the presenter's answer to "is that in the paper?", so the
build closes the speaker essay on it and keeps it off the slide. What the slide
prints under a drawing is its one provenance line (§3-5).

**4-3. `probe-diagram` is for routing changes.** One lane becoming two and
merging is the shape of a paper that moved where a signal goes. Test it before
drawing: if `before` and `after` come out with near-identical boxes and the whole
difference lives inside the `note` strings, it is a table, not a figure — do not
draw it. When the change is *when* things run rather than *where* a signal goes,
it is a `probe-timing` (§4-8).

**4-4. `loop` marks state carried across timesteps.** A recurrence is the one
thing box-and-arrow prose cannot show, so it is drawn rather than written.

**4-5. Compression is admitted in the note.** When a per-layer operation is drawn
once, the `note` says `층마다`. A figure that quietly flattens structure is wrong;
one that flattens it and says so is a figure.

**4-6. Results are plotted, not listed.** The paper's result numbers go on a
`probe-chart`, not into a ribbon or a ledger line. A `結` that lists `0.45`,
`0.36` and `0.33` asks the room to compare numbers in its head while the
presenter talks; a chart makes the comparison before the presenter opens their
mouth.

- **Every value is printed in the paper** — body text or a table, in the
  edition `arxiv_html` names. A value read off the paper's plot image is not
  printed, and there is no field for one: when the numbers live only in an
  image, the slide is an `evidence` or `split` slide showing that image. A
  point the paper did not measure is `null`, and the line breaks there rather
  than bridging it.
- **At most one series is `us`**, drawn in the accent; every other series is
  grey, told apart by shape and by a direct label. A chart of a finding rather
  than a method — a wall the obvious answer hits, a sweep of the paper's own
  measurement — has no `us`: the series its note is about (`note.of` on a
  `line`, `note.series` on a `scatter`) is drawn in the text's own ink, the
  heaviest line on the chart, and every other series is grey. `vs` names the
  strongest baseline **at the point the note reads**, by the paper's own
  numbers — usually the one the paper calls strongest, but not when another
  baseline beats it there; it takes the darker grey, and a `line` note
  measures from it unless the note names its own pair (`of`, `from`). The
  same holds for a `probe-facts` comparison: the baseline cell is the
  strongest one at that setting, never the one that makes the widest gap.
- **One annotation carries the takeaway** — `note` on a `line` or a `scatter`,
  `group` on `dots`. The header states the claim; the annotation shows where on
  the chart it is true. A chart with no annotation leaves the room to find the
  point. Where it sits is the author's call, not the build's guess: a `line`
  note takes `side` (`left`, `right` — which side of the points its bracket
  stands on) and `place` (`above`, `below`, `middle`); a `scatter` note is
  pinned to a point by its `label` and takes `place` (`above`, `below`,
  `left`, `right`).
- **The form follows the data.**
  - `line` is a sweep over an ordered x — delay, horizon, data size — where
    the slope is the finding. When the x values are numbers, `x.values` gives
    each tick its value and the points are spaced by it: a sweep over 0, 9, 12,
    16, 17 drawn at equal steps is a sweep with the wrong slopes.
  - `dots` is methods across categories — tasks, benchmarks — one row per
    category on a shared scale. The gap to `us` is drawn and labelled on every
    row, measured from **that row's strongest baseline** (`x.better: "lower"`
    when less is better), or from the series a row names in its own `vs` when
    the comparison is a fixed one — an ablation against the paper's full
    method. A gap that would run through another series' mark is lifted over
    the row. `"gap": false` draws none, for two readings of one thing rather
    than rivals.
  - `scatter` is one quantity against another — size against success, cost
    against quality — which is the shape a compression or a scaling result
    has. Each point is `{x, y, label}` with the label on the side the author
    names (`place`); `frontier` on a series joins its points in x order;
    `guides` draw the reference levels a reader measures against (`{"y": 80.0,
    "label": "압축 전 80.0"}`).
- **Numbers keep the paper's precision.** A value is printed as it was written
  — `0.20` stays `0.20` — and a gap is stated to the most decimals its values
  carry (`−0.5%p`, not `−1%p`); `x.decimals` or `y.decimals` overrides, and a
  series' `labels` print exactly what they say (`11/20`). One axis prints one
  precision: when the paper writes some values of a chart as `80%` and others
  as `62.5%`, `labels` pad the short ones (`80.0%`) — a trailing zero states
  nothing new, and a column of mixed precisions reads as numbers from
  different tables. A gap in points is written `4.5%p`, with no space, in the
  header and on the chart alike. `fmt` is `pct` for a fraction shown as a
  percentage, whose gaps are `%p`, or `raw`, whose `unit` (`×`, `ms`) follows
  every value and gap.
- **`omitted` lists what the chart leaves out**, one entry per source row with
  its values — `"<row> · <series> <value> · …"`, e.g. `"Don't Spill Prog ·
  πR² 55/80 · RTC 45/80"` — and `[]` when it leaves out none. Nothing of it
  is drawn. It is there because a headline is a claim about the whole table,
  and a chart that shows five rows of twelve can support a headline the other
  seven contradict: the self-check reads the headline against this list, and
  a headline that does not survive it is narrowed until it does.
- **`clock`** names the setup a chart's values were measured on when they are
  times, delays or ticks — `<setup> · <platform> · <rate>`, e.g.
  `시뮬레이션 · Leap Hand · 50 Hz` — and is printed first on the provenance
  line.
- **`source` and `why` are required** (§4-2): `source` says where every value
  is printed, `why` which of the paper's figures or tables it redraws and what
  it leaves out — error bars and series whose numbers are only in the image
  are the usual two.

An example — a sweep over the delay, with the method arriving on the first
press:

```probe-chart
{"kind": "line",
 "x": {"ticks": ["d₀ = 1", "d₀ = 2", "d₀ = 3"], "sub": ["…", "…", "…"], "label": "…"},
 "y": {"min": 0, "max": 0.6, "step": 0.1, "fmt": "raw", "label": "성공률"},
 "series": [{"name": "naive-async", "values": [0.33, 0.29, 0.22]},
            {"name": "Train-Time RTC", "values": [0.36, 0.32, 0.19]},
            {"name": "πR²", "us": true, "step": 1, "values": [0.43, 0.42, 0.45]}],
 "vs": "naive-async",
 "note": {"at": 2, "text": "0.45 대 0.22", "sub": "…", "side": "left", "place": "above"},
 "clock": "시뮬레이션 · Leap Hand · 50 Hz",
 "source": "Figure 3 오른쪽 · 원문 §4.1.2 본문 수치",
 "omitted": ["πR² w/o async (계단만) — 그림에만 수치"],
 "why": "…", "alt": "…"}
```

In it, at `d₀ = 3` the strongest baseline is naive-async (0.22), not the one
the paper calls strongest overall, so it is the `vs` and the note's pair.

`dots` takes `rows` (`name`, `sub`, and `vs` for a fixed reference) in place
of `x.ticks`, an `x` scale in place of `y`, per-series `labels` for the raw
counts (`11/20`) the tooltip and the row label print, and `group: {"rows":
[...], "text", "sub"}` for the rows the paper itself singles out. `scatter`
takes an `x` and a `y` scale, each with `min`, `max` and `step`, and `points`
per series in place of `values`. `alt` is the chart in one sentence with its
numbers — the reading for anyone who cannot see it.

**4-7. A value per position is a strip.** `probe-heat` draws the mechanisms a
paper states as a value per position — a noise level per chunk slot, a mask, a
schedule — as rows of cells on one sequential ramp, so two schedules read
against each other cell by cell. Every cell is computed from the paper's own
equation at a stated setting, and `source` names the setting. A run of
positions that shares one value between them (`shared: [from, to, label]`) is
drawn as a single block off the ramp, because shading it at one level would
state a number the paper leaves free. `regions` names spans under a row,
`mark` outlines the span a step singles out, `step` labels the move from the
row above. A strip whose every cell is 0 or 1 is a mask — kept or dropped —
and its key is two swatches rather than the ramp, since a gradient beside
yes/no data claims levels the data does not have. A setting chosen to draw at
is `illustrative` (§4-1), and `omitted` holds as it does for a chart. A
schedule the paper carries through a step — panels (a) (b) (c) of one buffer —
is one row stepped through its states rather than stacked copies of it (§8-2).

**4-8. Time is drawn on one clock.** `probe-timing` puts rows on one
millisecond ruler with the control period as its grid; the author states times
— `at` and `ms` for every block — and the build places them, so every mark is
checkable against the paper by reading the fence. It has two readings.

**A drawing of time names its clock.** `clock` on a `probe-timing` or a
`probe-budget` is the hardware and the rate the times were measured on —
`<§> · <hardware> · <rate>`, e.g. `§3.2 · RTX A6000 · 50 Hz` — and it is
printed on a timing's ruler and at the head of a budget's provenance line,
because a tick is only a length on one machine. **Every drawing of time in one
act is on one clock**: a paper that states its latency on one GPU and
deploys on another has two clocks, and an act that draws the first and counts
in the second has blurred the mechanism it was drawn to explain. A result
chart measured on a different setup — a simulation's delays beside a real
robot's success — is not a drawing of time and may sit in the same act, but it
names its own `clock` (§4-6), so the room is told when the setup changes.

- **Call paths**: each row is one way of making a call, ending on its `mark`,
  the path's total. The first control period is washed across every row
  (`band`), because the question is which path fits inside one tick.
- **Workers**: rows running side by side — a slow worker (`kind: "slow"`), the
  fast one (`"run"`), a signal read once a tick (`dots`, with `into` naming the
  row it feeds). `feeds` draws what one row hands another as an arrow at the
  moment it happens, `band` washes the one tick the slide is about, and `brace`
  measures a span over a row — the age of what that tick is working from.
  `"눈금": "tick"` numbers the grid in ticks rather than ms.

A worker drawing is the one place a talk explains a mechanism the paper gives
only as pseudocode, which makes it the easiest to over-draw: every row is a
worker the paper names, every arrow a hand-off it describes, and times that
come from a different setup than the one the drawing shows are labelled in
`source`.

**4-9. The lineage: the gap, then the inheritance.** A room asks two things
of a paper it is shown — what could the work before it not do, and what in it
is new — and one drawing answers one of them well. So every talk places its
paper twice, each figure in the act whose question it answers:

- **`contrast`, in `承`** — the priors the paper names, set against the
  properties it contrasts itself on, with the column only this paper fills
  drawn as the contribution. It is the wall the obvious answers hit, stated in
  the paper's own terms, and it stands before the turn so the room sees the
  empty column before the turn fills it.
- **`inheritance`, in `結`** — what flowed in from each prior, what the paper
  adds, and the question it leaves. It stands after the room has seen the
  mechanism, usually before the ledger: before the turn, its additions would
  give the turn away.

**The two do not say the same thing.** The contrast shows the gap as a
property (`백본을 / 호출 밖으로`); the inheritance names the mechanism that
fills it (`비동기 시각 · 언어 처리`). An addition that restates the contrast's
key column is one point made twice, and the headlines follow the same split —
the contrast's names what was missing, the inheritance's what was taken and
what was made. Work the paper names as concurrent is a row of the contrast
and never a line of the inheritance: it ran beside the paper, not into it.

**Both, by default.** A talk goes without one only when the paper gives it
nothing to draw: related work that lists its priors without contrasting on
any property the paper states leaves no contrast, and a paper that names no
prior it takes anything from leaves no inheritance. The storyboard row where
the slide would have stood says so (§1-4), and the front matter carries the
reason, which is what the linter reads — never both:

```yaml
lineage_drop: <contrast | inheritance> — <why the paper gives it nothing to draw>
```

For example, `lineage_drop: contrast — §2 는 선행 연구를 나열할 뿐, 스스로를
대비하는 속성을 적지 않는다`.

**Every mark rests on the paper.** What holds for both figures:

- **Every row, column head, cell, edge phrase and addition rests on a
  sentence of the paper** — its related work, introduction, method or
  limitations — or on a title in its bibliography, which is the paper's text
  too. A taxonomy of the field the paper does not draw is an argument, and
  belongs in the script (§4-1).
- **A prior is one work.** When one citation groups several, the row or line
  is the first the paper names — unless the sentence attaches its
  description to one of them by name, and then that one stands — and every
  other work the citation groups goes into `omitted`, with its date and why
  it was left out. A name that joins works with ` · ` is refused.
- **`when` is the arXiv first-version month** (`2025.12`) of the id the
  bibliography gives, carried in `id`, which the build checks it against —
  or the venue year (`2024`) when the bibliography gives no id; a month with
  no `id` is refused. This paper's own row or node is its own id's month.
- **`id` hands the room the next thing to read.** When `analysis/<id>.md`
  exists, the prior links to that rewrite, marked `재작성 ↗`, and opens beside
  the talk.
- **`source`, `omitted` and `why` are required.** `source` names the
  sections the phrases come from and how the dates were set; `omitted` is
  every work the citations group or the paper names that the figure leaves
  out, one entry each (§4-6); `why` says that no figure of the paper draws
  this, which paragraphs the drawing gathers, and which work stands for a
  grouped citation, and why.

**The contrast.** Rows are the priors in the order they appeared, dated on a
rail, with this paper last in the accent (`us`); columns are the properties
the paper uses to say how it differs, each head phrased as the paper phrases
it (`백본을 / 호출 밖으로` for *the latency of repeatedly conditioning on a
large semantic backbone*), or its own comparison table's when it has one.
Each cell is one glyph — `●` the paper says the prior does it, `◐` in part,
`○` it does not, `–` the paper says nothing — and its `n` quotes the basis,
the section and the sentence, and is the glyph's hover text. A cell the paper
does not speak to is `–`, never inferred from what you know of the prior: `○`
drawn for silence is a claim of absence the paper did not make. `key` is the
column only this paper fills, banded in the accent's tint with `key_note`
under it; the build refuses one a prior also fills, so the band never claims
a first the paper does not. `sub` is a few words under a name (`동시대`),
and `step` on this paper's row holds it back for one press (§3-4), so the
room first sees the band standing empty. Two to five columns, two to six
rows. An example, cut to one prior:

```probe-contrast
{"cols": ["대형 VLA", "칸마다 / 다른 노이즈", "백본을 / 호출 밖으로"],
 "key": 2, "key_note": "πR² 만",
 "rows": [
  {"name": "Streaming DP", "when": "2024.06", "id": "2406.04806", "cells": [
    {"v": "○", "n": "§2 — 'uses compact visuomotor policies'"}, {"v": "●", "n": "§3.1.2 — …"},
    {"v": "○", "n": "§2 — 'None, however, address the latency of …'"}]},
  {"name": "πR²", "when": "2026.07", "us": true, "step": 1, "cells": ["●", "●", "●"]}],
 "source": "원문 §2 · §3.1.2 의 문장 — 칸마다 근거, 날짜는 arXiv 첫 버전",
 "omitted": ["Streaming Flow Policy (2025.05) — Streaming DP 와 한 문장으로 인용"],
 "why": "…", "alt": "…"}
```

**The inheritance.** Each prior stands on the left under its date, and its
edge into the paper carries `gave` — what the paper takes from it, a noun
phrase (`앞 d 칸 고정 인페인팅`) — with `where` under it, the section that
says so. The paper is the one node in the accent and lists `adds`: the
mechanism it brings that none of the priors had, one to four items. `open` is
the question the paper leaves — its own limitation or future work, with
`where` — drawn as a dashed edge out of the paper node, because it did not
flow in; it is the paper's question, never the author's. Three lines, as a
rule: a fourth crowds the edges past labelling at the room's floor, and the
build refuses a fifth — the lines that carry what the method actually takes
stand, and the rest go into `omitted`. An example:

```probe-inheritance
{"lines": [
  {"when": "2025.03", "name": "GR00T N1", "id": "2503.14734", "gave": "VLM 백본 + flow 액션 헤드", "where": "§2"},
  {"when": "2025.12", "name": "Training-Time RTC", "id": "2512.05964", "gave": "앞 d 칸 고정 인페인팅", "where": "§3.3"}],
 "me": {"when": "2026.07", "name": "πR²", "adds": ["비동기 시각 · 언어 처리", "지연 d 에 맞춘 노이즈 계단"]},
 "open": {"text": "고유수용감각 전용 어텐션 헤드", "where": "Limitations"},
 "source": "원문 §2 · §3.3 · Limitations — 날짜는 arXiv 첫 버전",
 "omitted": ["RTC (NeurIPS 38) — Training-Time RTC 와 한 문장으로 인용"],
 "why": "…", "alt": "…"}
```

**Against the word budget** (§3-1), what counts is what the room reads as a
claim: a contrast's column heads and `key_note`, an inheritance's `gave`,
`adds` and open question. Names, dates, `sub`, `where`, the glyph key and a
cell's `n` say who, when and where, and do not count. A five-column contrast
spends about a dozen words and an inheritance of three edges about twenty,
which leaves the headline its room; a lineage figure that runs past the
budget is carrying a paragraph of related work the script should say.

## 5. Line breaks

**5-1. Breaks are authored.** ` / ` in the source is the only line break on a
slide, and it breaks in the slide title, the `spine`, a `statement` slide's
prose and a contrast's column heads — everywhere else it prints as written.

A headline — a slide's title, the turn's statement, the cover's spine — is set
as large as its column allows for its widest authored line, so the column never
gets to break it. The cost lands on the author: one long line makes the whole
headline smaller, and a break at the seam is how a long claim keeps its size.
The width is estimated from the characters, erring wide so a miss leaves a
margin rather than a wrap, and a header line long enough to be set at under
about four-fifths of the headline size is refused a build pass until it is
broken.

**5-2. A break falls at a syntactic seam and leaves both halves readable alone.**
`모든 입력이 같은 속도로 / 처리될 필요는 없다` — the first half is already a claim.
`모든 입력이 같은 / 속도로 처리될 필요는 없다` is a wrap, not a break.

**5-3. A title breaks where its claim turns**, so the second line lands on the
word the slide is about.

## 6. The speaker essay

`probe-script` is what the presenter says while the slide is up, in the second
person, written to be read once and delivered from memory. The presenter reads
it on a screen of its own beside the stage, so it is written to be glanced at
under load, not studied. Where a slide has builds, the essay marks each press
where it falls — `(다음)` — and where a figure steps, each state —
`↓ — (b).` (§8-2-3).

**6-1. The walk-through never carries a fact the slide does not show.** A number
that matters enough to say belongs on the slide — in its figure, a chart, an
`n`, or the ribbon; the script points at it. `질문 나오면:` (§6-3) may carry
facts the slide had no room for, and each one names where the paper prints it
— `(Table 5)`, `(§4.2)` — because a fact said in answer to a question is
held to the same original as a number on a slide, and it is the one the
presenter cannot point at.

**6-2. It points at the `foot` rather than repeating it.** Once a conclusion is on
the slide, the script's job is to tell the audience where to look and why that
line is the one to keep.

**6-3. It carries the anticipated question.** `질문 나오면: …` is where a
comparison the slide has no room for goes. A paper figure's `caption` (§3-5)
and a drawn figure's `why` (§4-2) are appended after it by the build, so the
essay does not restate them.

## 7. Enforcement

Two gates, and they see different halves of this contract. The build validates
what it needs in order to draw a slide; the linter validates the rules a
presentation can break while rendering perfectly, which is exactly how a slide dump gets
published.

```bash
python3 site/build-site.py --only <arxiv-id> --out /tmp/probe-check --strict
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
| §1-1 exactly one tinted turn frame, on the turn | linter | no `statement`, a second one, or one outside `轉` |
| §1-2 a type's own fence is present, and every JSON fence parses | build | a `chart` slide with no `probe-chart` |
| §1-2 every `probe-figure` carries `url`, `caption` and `source` | build | an image with no provenance — the room cannot look it up |
| §1-0, §1-3 `focus` and `crop` are in the form CSS takes | build | a `crop` that is not one to four percentages, a `focus` that is not two |
| §1-3 at most one slide is text alone | linter | a second `ledger`, `versus` or drawing-less `statement` |
| §1-3 a `結` slide shows a result | linter | a talk whose results are never on screen |
| §1-5 no `context/` material anywhere | linter | a `D#` citation on a slide or in a script |
| §2 most panel items carry their second register | linter | a presentation under the 60 % floor — one item's missing `n` is allowed, a presentation of them is not |
| §2, §3-1 a second register is a number and its condition | linter | an `n` past six words |
| §2 no KaTeX on a slide | linter | `` $`…`$ `` or `$$` — a slide is read from across a room, so symbols are literal text |
| §3-1 the word budget | linter | a slide past 40 visible words, or the text slide past 50 — `--words` prints every slide's count |
| §3-2 every panel column closes on `foot` | linter | a column whose last item holds the bottom edge |
| §3-3 at most three ribbon cells | build | a fourth — past three it is a table the room reads instead of listening |
| §4-2 a drawn figure states `why` | build + linter | `probe-diagram`, `probe-timing`, `probe-chart`, `probe-heat`, `probe-contrast` or `probe-inheritance` without it |
| §4-6, §4-7, §4-9 a figure of the paper's numbers or sentences names `source` | build + linter | `probe-chart`, `probe-heat`, `probe-contrast` or `probe-inheritance` without it |
| §4-6, §4-7, §4-9 a figure of the paper's numbers or sentences lists what it leaves out | linter — `--omitted` prints each list under its headline | `probe-chart`, `probe-heat`, `probe-contrast` or `probe-inheritance` without `omitted` |
| §4-6 a chart is drawable as written | build — the slide is skipped | two `us`, a series short of values or with a value that is neither a number nor `null`, `x.values` that do not increase, a scatter point without `x` and `y`, a `vs`, row `vs`, `note.of` or `note.from` that is not a series |
| §4-1 a strip or a worker drawing says what it chose | linter | `probe-heat` or `probe-timing` without `illustrative` — a string, or `false` when every parameter is the paper's |
| §4-8 a drawing of time names its clock, and an act draws on one | linter | `probe-timing` or `probe-budget` without `clock`, or two clocks in one act |
| §4-8 a timing names rows that exist | build — the slide is skipped | a `feeds`, `dots.into` or `brace` pointing at a row the fence does not have |
| §4-9 a lineage figure is drawable as written | build — the slide is skipped | a contrast without two to five `cols` and two to six `rows`, a row whose cells do not match `cols` or are not one of `●` `◐` `○` `–`, a prior's mark with no `n`, `us` anywhere but the last row, no `key`, or a `key` column this paper does not fill or a prior also fills; an inheritance without one to four `lines`, a line without `name` or `gave`, a `me` without `name` or one to four `adds`, an `open` without `text`; on either, a `when` that is not `YYYY.MM` or `YYYY`, a month with no `id`, or a date its `id` contradicts |
| §4-9 every talk places its paper twice | linter | no `contrast` in `承` or no `inheritance` in `結` without a `lineage_drop` naming it and why; a second of either; one in the other act; both dropped |
| §4-9 a prior is one work, and the paper is dated by its own id | linter | a prior's name joining works with ` · `; this paper's row or node dated to another month than its id's |
| §4-9 the two lineage figures say different things | linter | an inheritance addition that is the contrast's key column word for word |
| §5-1 a header line fits the headline size | build | a header line that would be set too small to lead the frame — break it with ` / ` |
| §6 every slide carries its speaker essay | linter | a slide with no `probe-script` |
| §8-1 a clip rides beside the paper's own figure | build + linter | `probe-video` on a slide that is not `evidence` or `split`, or has no `probe-figure` — the build drops the clip and publishes the figure |
| §8-1 a clip is a file the authors publish, with its provenance | build + linter | a clip that is not an https `.mp4` or `.webm`, an embedded player, a fence without `page`, `caption` or `source`, a side of a pair without `label`, a third clip |
| §8-2 a stepped figure is drawable as written | build — the slide is skipped | `steps` on a chart that is not a `line` or naming a tick it does not have; a strip row whose `states` do not match `steps`, a state short of cells, a `cycle` that does not close |
| §8-2-3 the essay says when to step | linter | a stepped slide whose `probe-script` never marks a state with `↓` |
| §8-3 motion is the exception | linter | more than three moving slides in one presentation |

The rules no gate can see are the ones that decide whether the presentation
is a talk: whether the header sequence argues (§1-4); whether each header and
the spine are as strong as the paper's sentence under them and no stronger
(§1-3); whether §1-1's merge rule was actually applied; whether the paper's
own figures were used where they carry the point (§1-3); whether every
number on a slide and in a script is one the paper prints (§4-6, §6-1);
whether each headline still holds against the rows its chart left out
(§4-6); whether every second register is from the setup its claim names (§2);
whether every row, cell and edge of a lineage figure is the paper's own
account of its priors, and the inheritance names mechanisms rather than
restating the contrast's gap in other words (§4-9);
whether a drawn figure's labels land clear of its marks; and whether a slide
that moves had to (§8). None of them can be judged from the source alone —
they are judged by reading the original and looking at the rendered slides,
which is why the `/present` prompt's procedure renders the talk and reads
every frame. `--numbers <extract>` helps with the fifth: it prints every
numeral on a slide, in a fence or in a script that the extract does not
contain verbatim, and each one it prints is either arithmetic on numbers the
paper prints — said so in the self-check — or a slip. It reports and never
fails, since a derived gap is legitimate.

## 8. Motion

A slide moves only where the motion is the argument — where a still can state
the claim but cannot show it. Two things qualify:

- **When** — a reaction, a contact, a recovery, the moment a force turns. That
  is the paper authors' own clip of the scene (§8-1).
- **In what order** — a state carried through a step, which the paper draws as
  panels (a) (b) (c) of one buffer or schedule, or a result read across the
  values the paper swept, where the point is how the gap moves. That is the
  strip or the chart the slide already draws, stepped one state at a time
  (§8-2).

Motion that decorates is refused: a demo reel on the cover, a clip of the
method working in general, a figure stepped because it can be.

**Every moving slide is a still first.** The clip is drawn over the paper's own
figure of the same scene, and a stepped figure stands in its first state. That
still is what the room gets whenever the clip cannot play — a codec the
browser lacks, a host the room's network blocks, a page that moved — and what a
printout and a browser with no script get. So the still makes the slide's
claim on its own and carries every number the slide leans on; the motion adds
*when* and *in what order*, never *what*.

### 8-1. The authors' clip

An example — a pair, the paper's method first:

```probe-video
{"clips": [
  {"src": "https://pi-r2-flow.github.io/static/videos/cmp/book_ours_cmp.mp4", "label": "πR²"},
  {"src": "https://pi-r2-flow.github.io/static/videos/cmp/book_rtc_cmp.mp4", "label": "Train-Time RTC"}],
 "page": "https://pi-r2-flow.github.io/#tasks",
 "caption": "Tidy Up Book 을 실제 속도로 — … 두 클립의 힘 축 눈금이 서로 달라 봉우리 높이로는 비교할 수 없습니다",
 "source": "저자 영상"}
```

**8-1-1. It rides beside the paper's figure of the same scene** — on an
`evidence` or `split` slide, next to its `probe-figure`. The figure is the
fallback and the source of the slide's numbers: a number read off a frame of a
clip is not a number the paper prints (§4-6).

**8-1-2. It is a file the authors publish.** `page` is the project page or
supplementary material the arXiv original itself links, and `source` says whose
clip it is. `clips` are https `.mp4` or `.webm` files that page serves. While
the clip plays, the provenance line under the slide names `source` and the
page's host; when it cannot play, the figure's `source`, as on any figure
slide. Never an embedded player: YouTube, Vimeo or any `<iframe>` takes the
keyboard the deck runs on and has no figure to fall back to. When an embed is
all the paper has, the slide stays on its figure and the essay names the video
for after the talk.

**8-1-3. One clip, or a pair.** A pair is a comparison — the paper's method
first, each side `label`led — and it restarts together, so both sides show the
same instant. A third clip is a grid the room watches instead of listening.

**8-1-4. `caption` says how to read it**, and what the rendering hides: two
plots on different axis scales, a speed-up burned into the frames, a cut. Like
a figure's caption it closes the essay (§3-5), so the presenter says it before
the room has to ask.

**8-1-5. Seconds, not minutes.** The clip plays muted from its first frame when
the slide arrives and stops when the slide leaves; the presenter pauses it with
K and halves its speed with S, and a click on the clip pauses it rather than
turning the page. Choose the cut that shows the moment, not the reel.

### 8-2. Stepped figures

The build draws every state and the presenter moves between them. Nothing is
computed in the browser, so every value a state shows is in the fence and §4
holds in full — `source`, `why`, `omitted`, `illustrative`. Two figures step:

- **`probe-heat`** with `steps`, the states' labels in order, and a row that
  carries `states` in place of `cells` — one `{cells, regions, mark}` per
  state. `shift` on a state slides the row that many positions to the left as
  it enters that state, so each cell is a slot that keeps its identity: the
  slots passing the front leave, fresh ones come in from the right edge.
  `cycle: true` says the last state is the first again — a schedule that
  reproduces — and the presenter steps it as a loop; the build refuses a cycle
  whose rows do not end where they began.
- **`probe-chart` `line`** with `steps`, the tick indices to walk. State 0 is
  the whole chart; each later state washes one column, sets the others back and
  tags every series' value there, each tag led by its series' mark, so the
  room reads the gap at that x instead of estimating it from the slopes. The
  note stands in state 0 and returns only on the state that washes its own
  column, so a walk that ends there arrives at the claim — list the note's
  column among `steps`, and make it the last.

An example — one buffer through the paper's three panels, as a loop:

```probe-heat
{"cols": 12, "steps": ["(a) 호출 시작", "(b) 한 스텝 뒤", "(c) d 칸 밀기"], "cycle": true,
 "rows": [
  {"name": "πR²", "us": true, "states": [
    {"cells": [1, 1, 1, 1, 0.833, …, 0, 0, 0], "regions": [[0, 3, "진행 중 행동 — 고정"], …]},
    {"cells": [1, 1, 1, 1, 1, 1, 1, 0.833, …, 0.167], "mark": [3, 6, "p = 3 – 5 방출"]},
    {"cells": [1, 1, 1, 1, 0.833, …, 0, 0, 0], "shift": 3, "regions": […]}]}],
 "source": "…", "why": "…", "omitted": [], "alt": "…"}
```

A row of the states' labels stands over the figure: in the tab its buttons are
how a reader steps, and on the stage it is the room's caption for the state on
screen. Write the labels as the paper names its panels.

**8-2-1. The first state stands alone.** It is the figure without a script and
on paper, so order the states so that it already argues.

**8-2-2. One press, the builds' press.** On the stage → takes the slide's
builds first, then its states, then the next slide, so a clicker drives the
whole talk; ↓ and ↑ move the figure without leaving the slide. In the tab ← and
→ stay the slides' alone: ↓ and ↑ step a figure the reader is working, and its
buttons step it. A slide arrives in its first state, and in its last when the
presenter steps back onto it.

**8-2-3. The essay is written against the states.** It marks each state where
it falls — `↓ — (b).` — with what the room should see when the figure moves. A
stepped slide whose essay never says when to step is a still with buttons on
it.

### 8-3. Motion is the exception

At most three moving slides — a clip or a stepped figure — in a presentation.
A talk where half the slides move is a demo, and the still slides beside it
stop reading as evidence.
