# Comparison authoring

The format contract for `comparison/<slug>.md` — the comparison track. One file is
one comparison: two or three papers held under one question, with everything
that is not the divergence left to the papers' own pages.

`.claude/prompts/compare.txt` defers to this file for what a comparison must
look like, and owns the procedure — which papers, how the rewrites and the
originals are read, how to verify and commit. Edit this first, then the code.

## 1. The one rule

**Only papers that already have a rewrite in `analysis/` may be compared.**

A paper's own detail belongs to its own page, and the comparison links out to
it for everything but what separates the papers. A compared paper with no
rewrite has no page to link to, so the comparison would have to carry its
detail and stop being a comparison — one rewrite and two summaries. The build
therefore **refuses to publish** it rather than warning.

What follows from that:

| Consequence | Where it is written down |
|---|---|
| A comparison never introduces a paper — the page does it from front matter | §2-2 |
| Fences that zoom into one paper are unavailable | §2-4 |
| The document is short, because it is only carrying the divergence | §2-5 |
| Facts are confirmed in the original, not inherited from a rewrite | §2-6 |

## 2. The document

### 2-1. Front matter

Flat keys, parsed by `site/builder/frontmatter.py` — the same minimal parser
`analysis/` uses. `summary` is the only block scalar.

```yaml
compares: [2603.10158, 2606.10683, 2608.14028]
sources: [2603.10158v2, 2606.10683v1, 2608.14028v1]
title: "손이 여러 개일 때 행동 공간을 하나로 만드는 세 가지 방법"
tagline: 배우게 할 것인가, 토큰으로 자를 것인가, 손으로 배정할 것인가
stances: [잠재 벡터로 묶는다, 토큰으로 접는다, 표를 그려 꽂는다]
common: 셋 다 손대지 않는 자리가 있다
problem: 로봇 손마다 관절 수와 순서가 달라, 정책이 관절 각도를 바로 내면 그 손 전용이 된다
plain: [손마다 통역사를 붙여 공통어로 말하게 한다, 모든 손을 22칸 표준 양식에 옮겨 적는다, 사람이 손가락 자리표를 그려 꽂는다]
primer: [fk, latent, retarget]
pillars: P1, P4
generated: 2026-08-21 14:30
generator: compare/v1
summary: >
  2–3 sentences, read cold.
```

| Key | Rule |
|---|---|
| `compares` | 2–3 arXiv ids, **each with a rewrite in `analysis/`**. Two is a contrast, three is a field; four is a survey and wants a different shape. No duplicates. This list fixes the column order of every `probe-matrix` and the order of the paper cards |
| `sources` | The arXiv edition actually read, `<id>v<n>`, **one per entry of `compares`, in the same order**. Which version was read is the one fact a comparison cannot recover later |
| `title` | The comparison's **question**, not a list of the papers' names. The cards below the header already name them |
| `tagline` | One line: what reading these together tells you |
| `stances` | **One per entry of `compares`, in the same order** — what that paper does about the question, in 20 characters or fewer (`끝까지 푼다`, `토큰으로 접는다`). The divergence in its shortest form. A stance that needs a clause of mechanism to land is not a stance — that clause belongs in a `probe-matrix` cell |
| `common` | One line, 30 characters or fewer: **the commitment all of them share** (`셋 다 이미지 평면에서 끝낸다`) — act 2 in its shortest form (§2-3). Required |
| `problem` | One line, 60 characters or fewer: **the problem every compared paper is up against**, in words a reader outside the field follows. It prints under the question, in the tagline's place. Write it |
| `primer` | **At most three** background cards, by id, from `site/builder/primers.py` — `vla` · `chunk` · `denoise` · `fk` · `latent` · `compress` · `retarget` · `taxel` · `proprio` · `track` · `frozen` · `history` · `edit-obs` · `speedup`. Each is a drawing and one plain line, printed under the paper cards as 읽기 전에. Name only what a reader outside the field cannot read the divergence without; a card cannot be defined in the document |
| `plain` | **One per entry of `compares`, in the same order**, 40 characters or fewer: what that paper does, said in everyday Korean — **no Latin script and no math**, so no acronym, no paper name, no symbol. An analogy is the usual shape (`손마다 통역사를 붙여 공통어로 말하게 한다`). It prints on the paper's card under its stance. Write it |
| `pillars` | Ours, comma-separated. Which pillars this question sits in |
| `generated` | `YYYY-MM-DD HH:MM` — the clock as you write |
| `generator` | Literal `compare/v1` |
| `summary` | 2–3 sentences read cold. Markdown and `` $`math`$ `` render |

**Two registers, one thought.** `tagline` is prose and prints on the
comparison's own page, under the question — unless `problem` is written, which
takes that line, and the tagline then serves the index and the search preview. `stances` and `common` are the same
claim as structure: a fork — a branch per paper, labelled with its `alias:`
(`analysis/AUTHORING.md` §1), and the trunk for what they all accept. The
index card draws it **instead of** the tagline; the comparison's own page
draws it at full size, `common` as the trunk over the paper cards and each
card led by its paper's stance.

Writing `common` is the check, not the caption. The moment you cannot fill it
in one line is the moment to ask whether these are the right two or three
papers (§2-3).

`analysis/` keys that are deliberately **absent** — `figures` · `appendix` ·
`terms` · `metric` · `published` · `authors` · `links` — each describe one
paper's original, which that paper's rewrite already carries.

**File name.** `comparison/<slug>.md`, lowercase words joined by hyphens,
drawn from the question — never the ids joined together.

### 2-2. The prose never introduces a paper

The page prints a card per compared paper above the argument — the paper's
mark, its alias and stance, then its full title, arXiv id, headline metric and
a link to the rewrite — built entirely from front matter that is already
written. That is the introduction. It is on the screen before the first
sentence.

Each paper keeps one mark across the page — ● ▲ ■ in `compares:` order — on
its card and its `probe-matrix` column, and pointing at any of a paper's places
lights that paper alone. So the prose names papers by alias; it never refers to
"the first" or "the left column".

So the first sentence does not repeat it. Three paragraphs opening "A 는 ~하는
논문이다" are not a comparison; they are three rewrites' introductions stacked.
Act 1 starts at the question that puts these papers on one table.

### 2-3. The spine — four acts

```
# <한 문장 — 이 셋을 같이 읽으면 무엇이 보이는가>
## 1 왜 이 셋인가
## 2 무엇이 같은가
## 3 어디서 갈리는가        ← ```probe-matrix lives here
## 4 연구축에 무엇이 걸리나   ← the D# layer
```

`#` is the thesis: what emerges from reading them together, in one sentence.
Not a title, and not a summary of any one paper.

Act 4 prints **folded** — its divider is the line a reader opens. The
research-axis layer reads only after the divergence itself has landed, so a
first read of the page ends at act 3, and act 4 must not carry anything act 3
needs.

Act 2 is load-bearing and is the act most often skipped. Papers that share
nothing cannot diverge — they are merely different, and act 3 degenerates into
a list of unrelated methods. Naming the shared commitment is what makes act 3
a fork rather than a list. The test: act 2 says something **no single one of
these papers says about itself**. A shared commitment is visible only from
outside, so act 2 that could have been copied off one paper's abstract has not
found it yet.

`###` subsections are free. **Not required, unlike a rewrite**: the quiz per
section (R11), the `| English Keyword` heading line (R2), and the
planted-context component (R5). All three exist to make one paper learnable,
and a comparison teaches no paper — do not carry them over from
`analysis/AUTHORING.md`.

### 2-4. Which fences are available

**Components that speak about several things at once are available. Components
that zoom into one paper are not** — that paper's own page has them.

| Fence | In a comparison | |
|---|---|---|
| `probe-matrix` | **Required** — at least one, in act 3 | §3-1 |
| `probe-figs` | Available — the papers' own figures for one question, one frame | §3-2 |
| `probe-split` · `probe-parts` | Available | contrast components; they already hold things apart |
| `probe-scale` | Available | putting several numbers on one axis is what it does |
| `probe-lineage` | Available | several papers on a time axis — act 1's natural shape |
| `probe-flow` | Available | for a pipeline all of them share, marked with where each paper acts (§3-3) |
| `probe-timeline` | Available | for papers that part over time — one ruler, one row per paper (§3-4) |
| `probe-term` | Available, **shared vocabulary only** | a term only one paper uses belongs to that paper's panel |
| `probe-figure` | **Unavailable** | one paper's figure on its own is one paper's detail — `probe-figs` shows it beside the others |
| `probe-eq` | **Unavailable** | so is a derivation. Inline `` $`x`$ `` carries what an axis needs |
| `probe-quiz` | **Unavailable** | it teaches one paper; it does not compare |

An unavailable fence is **reported and rendered as an error block**, never
silently dropped — a fence that renders to nothing is one the author never
learns was wrong.

GFM alert callouts are not fences and the table does not govern them. They are
available, and `> [!CAUTION]` in particular publishes as 연구축과 충돌 — act 4's
natural shape when the three answers cost the decisions different things.

### 2-5. Length

A comparison that runs as long as a rewrite has stopped comparing. The build
warns past 7,000 printed characters (rewrites run about 8,500–20,000).

**The count is prose only** — every fenced block is stripped first, so a
`probe-matrix` costs nothing. That also means it cannot see where a comparison
usually starts explaining one paper: a **cell note** that grows a second clause
of mechanism. Catching that is reading (§4).

When the ceiling fires, the fix is never to compress the prose. Find the
paragraph or note that started explaining one paper, and either link to its
rewrite or drop the axis.

### 2-6. Where the facts come from

**Every number, mechanism and stated limitation in a cell is confirmed in the
arXiv original**, never inherited from a rewrite, and `sources:` records which
edition it was confirmed against. A number the paper does not give is not in a
cell; a paper that is ambiguous on an axis gets a cell saying so — that is a
finding, and one only a comparison produces.

### 2-7. What publishes as literal text

The renderer is the one `analysis/` uses, so the traps
`analysis/AUTHORING.md` §3 names bind here as written: the three accepted math
forms and nothing else (§3-1 — inline is `` $`x`$ ``), emphasis that never
closes (§3-2), and a bare URL that is not a link (§3-3). Read that section
before writing a cell or a note — a matrix cell is inline Markdown and falls
into the same traps as prose.

## 3. The drawn components

### 3-1. `probe-matrix`

The component this track is built on, and the reason a comparison does not
collapse into three summaries sharing a file.

```probe-matrix
{"title": "<선택 — 이 표가 묻는 것>",
 "axes": [
   {"k": "<축 — 질문 형태로>",
    "cells": [{"of": "<arxiv-id>", "v": "<이 논문의 답>", "note": "<선택 — 한 줄>"}]}]}
```

- **3–7 axes.** Fewer than three is a sentence; more than seven is a
  spreadsheet.
- Each axis needs `k`, the question it asks.
- **Each axis needs one cell per compared paper.** `of` must name one of
  `compares:`, with no duplicates and none missing. An axis that fits only two
  papers is reworded until it fits all three, or dropped — that rewording is
  where the comparison happens.
- `v` is required; `note` is one optional line under it.
- Cells are placed by `of`, not by position, so they may be written in whatever
  order the axis reads best.
- A cell is an answer. A paper with nothing on an axis gets a cell saying
  **what it does instead** — never `해당 없음` or another placeholder; if no
  such sentence exists, the axis is the wrong one.

Columns run in `compares:` order and their heads link to the rewrites, so the
third column and the third card are always the same paper, under the same
mark.

**An axis may say what shape its answers take**, with `type`. Without it the
axis is sentences, as above. With it the build draws the answers, and every
cell still carries its `v`:

| `type` | Each cell adds | Drawn as |
|---|---|---|
| `stops` | `at` — the index of a stop; the axis adds `stops`, 3–5 names of 16 characters or fewer | a strip of equal-width places, each paper's mark on the one it holds; the sentences fold under it |
| `mark` | `mark` — `●` 한다 · `◐` 일부 · `○` 못 한다 · `–` 원문 언급 없음 | the word with its dot, before the sentence |
| `measure` | `metric` — what the number measures, 20 characters or fewer | the yardstick on each cell; a paper off the majority's is flagged `다른 잣대`, and a row with no majority says its yardsticks all differ |

```probe-matrix
{"k": "정렬을 무엇이 감독하나", "type": "stops",
 "stops": ["순기구학으로 학습", "재구성 오차로 학습", "학습 없음 · 사람의 표"],
 "cells": [{"of": "<arxiv-id>", "at": 0, "v": "<이 논문의 답>"}],
 "probes": [{"of": "<arxiv-id>", "at": 2, "v": "<절제 실험에서 본 것>"}]}
```

- **Stops say order, never distance.** Name them from values the compared
  papers actually reach, and use `stops` only when the places have an order a
  reader would agree with; otherwise the axis is sentences.
- `probes` (optional) marks a place a paper reached **only in an ablation** —
  drawn as its mark hollow, so a stop that was tried and failed does not read
  as one nobody tried.
- `–` is the absence of a claim, not a claim of absence: use `○` only where
  the paper says it does not.
- `measure` is the axis for any row where a reader would line the numbers up.
  Name the metric the same way for the same measure — the flag compares the
  strings.

### 3-2. `probe-figs`

The papers' own figures for one question, shown one at a time in one frame:
the reader switches papers in place, so what differs is what changes on
screen. Never three figures side by side — a diagram shrinks past reading and
mismatched shapes pad out with blank space.

```probe-figs
{"q": "<모든 그림이 답하는 한 질문>",
 "figs": [{"of": "<arxiv-id>", "fig": "<그 논문 재작성본의 probe-figure id>",
           "look": "<그림에서 볼 곳 한 줄>"}]}
```

- `q` — one question, 40 characters or fewer, that every figure answers.
- `figs` — a figure from **at least two** compared papers, one each. `fig` is
  the figure's id in that paper's own rewrite, which already declares where it
  lives; the build takes the URL and the original's figure number from there.
  A figure the rewrite does not carry cannot be shown.
- `look` — where in the figure to look, 60 characters or fewer.
- Pick figures of one kind and similar shape — photographs with photographs,
  diagrams with diagrams — whose text stays legible at the column's width.
  Look at each figure before choosing it; a figure whose point needs a crop to
  find is the wrong figure.

### 3-3. `probe-flow` as a map of where each paper acts

The pipeline every compared paper shares, drawn as `analysis/AUTHORING.md` R6
draws a flow, with two keys a comparison adds to a step:

```probe-flow
{"title": "<이 흐름의 이름>", "why": "<원문의 어느 그림도 이 지점을 덮지 못하는 이유>",
 "steps": [
   {"label": "<단계>", "blind": "<셋 다 여기를 어떻게 남겨 두는가>"},
   {"label": "<단계>", "marks": {"<arxiv-id>": "<이 논문이 여기서 하는 일>",
                                 "<arxiv-id>": "<…>"}}]}
```

- `marks` maps a compared paper to what it does at that step, 30 characters
  or fewer, drawn with the paper's mark. A paper acts where it is marked.
- `blind` is a step **every** paper leaves as it found it — the shared blind
  spot act 2 names, drawn dashed. A step is marked or blind, never both.
- From the marks the build reads the comparison's shape and prints it over
  the diagram: a step two or more papers mark is **경쟁형** — they compete
  for one slot; marks on separate steps only is **보완형** — each fills a
  different one.
- Layout is the flow's own grid, so no line crosses a box: write the steps in
  order and the build places them.

### 3-4. `probe-timeline`

The compared papers on one ruler, for a comparison that parts over time — a
control period, a chunk being run, a signal read again mid-way. The author
states values on the ruler; the build places every mark, so each is
checkable against the paper by reading the fence.

```probe-timeline
{"title": "<무엇을 따라가는 그림인가>", "unit": "<스텝 | 초 | ms>", "span": 16,
 "ticks": [0, 4, 8, 12, 16], "cuts": [0, 4, 8, 12], "cut_label": "<점선이 무엇인가>",
 "why": "<원문의 어느 그림도 이것을 덮지 못하는 이유>",
 "rows": [{"of": "<arxiv-id>", "label": "<한 단어 — 하는 일>", "note": "<한 줄>",
           "spans": [{"from": 0, "to": 16, "style": "solid", "level": 0}],
           "every": {"at": 1, "label": "<무엇을 매번 읽나>"}}]}
```

- `span` is the ruler's length in `unit` (6 characters or fewer); `ticks`
  default to quarters. Every value must lie on the ruler.
- One row per compared paper, at least two. `label` is what the paper does,
  12 characters or fewer; `note` one line of 60.
- A span's `style`: `solid` — the paper does it; `part` — handed over
  half-made; `faint` — made and thrown away; `over` — a thin layer added on
  top. `level` 0–3 stacks a span on its own sub-row, for a paper that redoes
  the same stretch.
- `every` ticks a row at a fixed period, for a signal read again and again.
- `cuts` are places every row shares, drawn through the bars and never
  through the words; `cut_label` (40 characters or fewer) says what they are.
- Every value is one the papers state — a number derived from two stated
  values says so in `note`.

## 4. What the build checks

Each row is a hard failure: the build rows under `--strict`, which is how
pull requests build, and the last row as its own CI gate.

| Rule | Enforced by |
|---|---|
| A compared paper with no rewrite (§1) — **not published**; `compares` count and duplicates; `sources` present, parallel and in step; `stances` present, parallel and within its width; `common` present and within its; `title` / `tagline` / `summary`; `generated` format; the file name is a slug | `site/builder/comparisons.py` |
| `problem` and `plain` within their widths, `plain` parallel to `compares` and free of Latin script and math (§2-1) | `site/builder/comparisons.py` |
| `probe-matrix` payload — axis count, `k`, a cell per paper, `of` known and unique, `v` present; a typed axis's own keys (§3-1) | `site/builder/mdext/probefence.py` |
| `probe-figs` payload — `q`, a figure from at least two papers, `fig` declared by that paper's rewrite, `look` within its width (§3-2) | `site/builder/mdext/probefence.py` |
| `primer` — at most three ids, each a card that exists (§2-1) | `site/builder/comparisons.py` |
| `probe-flow` `marks` and `blind` — compared papers only, each within its width, never both on one step (§3-3); `probe-timeline` payload — `span`, `unit`, `why`, values on the ruler, a row per paper at most once, a span's `style` and `level`, `cut_label` with `cuts` (§3-4) | `site/builder/mdext/probefence.py` |
| At least one `probe-matrix`; the length ceiling; an unavailable fence in a comparison; `probe-matrix` in a rewrite (§2-4, §2-5) | `site/builder/render.py` |
| Term anchor ↔ definition pairing, unclosed `**`, math published as literal text (R4, §2-7) | `site/builder/render.py`, shared with `analysis/` |
| Every `D#` cited exists in the Decision Log | `linters/check-decision-refs.py` |

`--check` reads front matter only; the fence and length rules run while the
page renders, so the full build is the gate.

What the code cannot see is the rule that decides whether a comparison was
worth writing: whether the axes are the ones a reader would have asked about,
and whether act 2 found a real shared commitment rather than a truism (§2-3).
Nor can it see a cell note that has grown a second clause of mechanism (§2-5).
Read every note once more with only that question.
