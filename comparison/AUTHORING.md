# Comparison authoring

The format contract for `comparison/<slug>.md` — the comparison track. One file is
one comparison: two or three papers held under one question, with everything
that is not the divergence left to the papers' own pages.

`.claude/prompts/compare.txt` defers to this file. Edit this first, then the
code.

## 1. The one rule

**Only papers that already have a rewrite in `analysis/` may be compared.**

Every other rule here is a consequence of it, so it is worth stating why it
exists rather than only that it does.

A paper's own detail belongs to its own page. A reader who finishes an axis and
wants to know how one of the three actually implements it should have somewhere
to go, and `p/<id>/` is that somewhere — four acts, the figures, the equations,
the term panels, the whole read. The comparison stays on what separates the
papers and links out for everything else.

A compared paper with no rewrite has no page to link to. The comparison would
have to carry that paper's detail itself, and the moment it does, it is no
longer a comparison — it is one rewrite and two summaries. So the build does
not warn about a missing rewrite. It **refuses to publish the comparison**.

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
pillars: P1, P4
tags: [action-space, cross-embodiment, retargeting]
generated: 2026-08-21 14:30
generator: compare/v1
summary: >
  2–3 sentences, read cold.
```

| Key | Rule |
|---|---|
| `compares` | 2–3 arXiv ids, **each with a rewrite in `analysis/`**. Two is a contrast, three is a field; four is a survey and wants a different shape. No duplicates. This list fixes the column order of every `probe-matrix` and the order of the paper cards |
| `sources` | The arXiv edition actually read, `<id>v<n>`, **one per entry of `compares`, in the same order**. Which version was read is the one fact a comparison cannot recover later, and pairing it positionally means neither list can drift without the other noticing |
| `title` | The comparison's **question**, not a list of the papers' names. The cards below the header already name them |
| `tagline` | One line: what reading these together tells you |
| `pillars` | Ours, comma-separated. Which pillars this question sits in |
| `tags` | Free vocabulary, same as `analysis/` |
| `generated` | `YYYY-MM-DD HH:MM` — the clock as you write |
| `generator` | Literal `compare/v1` |
| `summary` | 2–3 sentences read cold. Markdown and `` $`math`$ `` render |

`analysis/` keys that are deliberately **absent**: `figures` · `appendix` ·
`terms` · `metric` · `published` · `authors` · `links`. Each declares something
about one paper's original, and each compared paper's own rewrite already
carries it. Adding one here later is easier than emptying one now.

**File name.** `comparison/<slug>.md`, lowercase words joined by hyphens, drawn
from the question. Not the ids joined together: three run to forty characters,
their order has no right answer, and what identifies a comparison is what it
asks.

### 2-2. The prose never introduces a paper

The page prints a card per compared paper above the argument — title, tagline,
headline metric, pillars, and a link to the rewrite — built entirely from front
matter that is already written. That is the introduction. It is on the screen
before the first sentence.

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

Act 2 is load-bearing and is the act most often skipped. Papers that share
nothing cannot diverge — they are merely different. Naming the shared
commitment is what makes act 3 a fork rather than a list.

`###` subsections are free. **Not required, unlike a rewrite**: the quiz per
section (R11), the `| English Keyword` heading line (R2), and the
planted-context component (R5). All three exist to make one paper learnable,
and a comparison teaches no paper.

### 2-4. Which fences are available

**Components that speak about several things at once are available. Components
that zoom into one paper are not** — that paper's own page has them.

| Fence | In a comparison | |
|---|---|---|
| `probe-matrix` | **Required** — at least one, in act 3 | §3 |
| `probe-split` · `probe-parts` | Available | contrast components; they already hold things apart |
| `probe-scale` | Available | putting several numbers on one axis is what it does |
| `probe-lineage` | Available | several papers on a time axis — act 1's natural shape |
| `probe-flow` | Available | for a pipeline all of them share |
| `probe-term` | Available, **shared vocabulary only** | a term only one paper uses belongs to that paper's panel |
| `probe-figure` | **Unavailable** | one paper's figure is one paper's detail |
| `probe-eq` | **Unavailable** | so is a derivation. Inline `` $`x`$ `` carries what an axis needs |
| `probe-quiz` | **Unavailable** | it teaches one paper; it does not compare |
| `probe-facts` | **Unavailable** | one paper's eight axes are that paper's own coordinates, and its page prints them |

An unavailable fence is **reported and rendered as an error block**, never
silently dropped — a fence that renders to nothing is one the author never
learns was wrong.

GFM alert callouts are not fences and the table does not govern them. They are
available, and `> [!CAUTION]` in particular publishes as 연구축과 충돌 — act 4's
natural shape when the three answers cost the decisions different things.

### 2-5. Length

A comparison that runs as long as a rewrite has stopped comparing. The rewrites
it sits beside run 9,500–17,000 printed characters, median around 13,000; the
build warns a comparison past 7,000.

**The count is prose only.** Every fenced block is stripped before measuring, so
a `probe-matrix` costs nothing against the ceiling — a grid is scanned, not read
top to bottom. That makes the ceiling generous by construction, and it also
means it watches the wrong half: the part of the document that *is* the
comparison is the part the count cannot see.

Which matters, because a comparison does not start explaining one paper in a
paragraph. It starts in a **cell note** — one clause of mechanism to make the
cell land, then a second. Nothing counts that and nothing will; catching it is
reading, which is what §4's last paragraph is for.

When the ceiling does fire, the fix is never to compress the prose — it is to
find the paragraph that started explaining one paper and either link to its
rewrite or drop the axis. A note that has grown a second clause has the same
two options and no third.

### 2-6. Where the facts come from

Read the three rewrites first, to find where the papers diverge — they are the
map, and they are why the track requires them. Then **confirm every fact and
number in the arXiv original** before it goes in a cell.

A comparison written only from rewrites inherits each rewrite's choices about
what to foreground, so the axes end up being whatever three separate readings
happened to emphasise. It is also the failure `analysis/AUTHORING.md` G1 names —
a digest of a digest — at three times the scale.

`sources:` records which edition each fact was confirmed against.

## 3. `probe-matrix`

The one component this track adds, and the reason a comparison does not
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
  `compares:`, with no duplicates and none missing. This is the whole point: an
  axis that answers for two of three papers is a remark about those two, and on
  the page it reads as though the third had nothing to say. A thought that only
  fits two either gets reworded until it fits all three, or is dropped — and
  that rewording is where the comparison actually happens.
- `v` is required; `note` is one optional line under it.
- Cells are placed by `of`, not by position, so they may be written in whatever
  order the axis reads best.

Columns run in `compares:` order and their heads link to the rewrites, so the
third column and the third card are always the same paper.

## 4. What the build checks

Each row is a hard failure under `--strict`, which is how pull requests build.

| Rule | Enforced by |
|---|---|
| A compared paper with no rewrite (§1) — **not published**; `compares` count and duplicates; `sources` present, parallel and in step; `title` / `tagline` / `summary`; `generated` format; the file name is a slug | `site/builder/comparisons.py` |
| `probe-matrix` payload — axis count, `k`, a cell per paper, `of` known and unique, `v` present (§3) | `site/builder/mdext/probefence.py` |
| At least one `probe-matrix`; the length ceiling; an unavailable fence in a comparison; `probe-matrix` in a rewrite (§2-4, §2-5) | `site/builder/render.py` |
| Term anchor ↔ definition pairing, unclosed `**`, math published as literal text | `site/builder/render.py`, shared with `analysis/` |
| Every `D#` cited exists in the Decision Log | `linters/check-decision-refs.py` |

Verify before reporting a comparison done. `--check` reads front matter and
writes nothing; the fence and length rules are checked while the page renders,
so the full build is the gate that sees everything:

```bash
python3 site/build-site.py --out /tmp/probe-check --strict
python3 linters/check-decision-refs.py
```

What the code cannot see is the rule that decides whether a comparison was
worth writing: whether the axes are the ones a reader would have asked about,
and whether act 2 found a real shared commitment rather than a truism.

Nor can it see the one failure that is easy to commit and invisible on the
page — a cell note carrying a second clause of mechanism, which is one paper's
detail wearing a comparison's clothes (§2-5). Read every note once more with
only that question.
