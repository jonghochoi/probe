# Analysis Rewrite Authoring Guide

> **Scope:** every `analysis/<arxiv-id>.md` — the corpus the reading site
> publishes. This file is the single source of truth for that format.
> `.claude/prompts/analyze.txt` owns the *procedure* (which paper, how to read
> it, how to verify and commit) and defers to this file for the output
> contract; `site/build-site.py` implements it. Change a rule here first, then
> the build.

**One file, two surfaces.** A rewrite publishes as two tabs on one page:

| Tab | What it is | Rules |
|---|---|---|
| 요약 (`::: glance`) | one screen: our thesis, a narrative, the evidence in four cards | §4 |
| 상세 | the full re-telling — four acts, term anchors, quizzes | §1–§3 |

Both are written **in the same `/analyze` run, from the same reading of the
arXiv original**, and they live in one `analysis/<id>.md`. 요약 is the tab a
reader opens first, but it is not made by summarising 상세 — it is a second
reading of the paper (G1, the rule it most often violates).

**Both are required.** A file carrying only the body is an incomplete rewrite,
not a shorter one: the page would publish an empty tab. Bringing an existing
rewrite up to this contract is a `/analyze <id> --refresh` run, which re-reads
the original — the one thing a from-the-body shortcut cannot do.

**The output is an HTML page.** Markdown is only the source language: what a
reader gets is `site/build-site.py`'s output, rendered by `markdown-it-py` plus
this repo's own extensions. Every rule below is judged against that page, not
against how github.com would render the same file. `scouting/AUTHORING.md`
governs a track that *is* read on github.com and does not apply here; the rules
the two tracks share are restated below in this renderer's terms.

---

## 1. File and Front Matter Contract

One rewrite per paper, `analysis/<arxiv-id>.md` — flat, no per-paper folder.

The site takes **all** of its metadata from this front matter — there is no
other source, so a missing field is a hole on the landing page.

```yaml
---
analysis_of: <arxiv-id>          # MUST equal the file name
title: "<the paper's own title, verbatim>"
alias: <the paper's own name for its method>   # optional — omit rather than invent
tagline: <one line: what this paper does>
authors: <first authors et al. (affiliation)>
pillars: P<a>, P<b>              # ours — most relevant first; the site files it under two
links: [arxiv|<url>, code|<url>]
published: YYYY-MM-DD            # the paper's date, from arXiv
generated: YYYY-MM-DD HH:MM      # yours — the clock as you write it
generator: analyze/v3
arxiv_html: <arxiv-id>v<n>       # the exact version actually read
arxiv_fetched: YYYY-MM-DD
figures: [<fig-id>, <fig-id>]    # verbatim ids of the figures cited
appendix: [<A>, <B.2>, <G>]      # appendix sections drawn on, or `none`
terms: <n>                       # count of inline term anchors
metric: <the headline number>    # optional — omit rather than invent one
summary: >                       # 한 문단 요약 — on the page AND on the card
  …
---
```

| Key | Rule |
|---|---|
| `analysis_of` | must equal the file name — the build reports a mismatch. It catches the copy-paste that lands a rewrite under the wrong id |
| `title` | required. The paper's title, as the card and the page header print it |
| `alias` | **optional.** The paper's own codename, for surfaces with no room for a title — a reader sees `T-Rex` where an id says nothing. `comparison/` names every compared paper by it (`comparison/AUTHORING.md` §2-1), and a rewrite's commit subject carries it as `(<alias>)`. Resolved by the ladder below; under 24 characters |
| `tagline` | required. **One line naming what the paper does**, printed under the body H1 and under the title on the landing page. The H1 is our thesis, often a metaphor, and does not say which paper this is; the header prints the paper's own title; the tagline is the sentence between them. **It never restates the paper's name** — `<코드명> — <무엇을 하는가>` under a title reading `<코드명>: <…>` spends its one line on the word directly above it. Open with what the paper does; the build reports the echo |
| `summary` | required. 2–3 sentences, read cold. Printed **on the page** as the `한 문단 요약` block between the thesis line and act 1, and flattened for the landing card. Authored as markdown — `**강조**` and `` $`math`$ `` render on the page and are stripped for the card, so bold the three or four phrases that carry the argument (§3-2 applies) |
| `authors` | one line, as printed |
| `pillars` | **ours**, not the paper's — read `context/P#.md` and pick honestly, **most relevant first**. The site files the paper under the **first two** only: the chips its card prints, the axes the landing rail counts it in, and what a click on those counts returns. A third is harmless and does not publish. The first entry decides the card's group; empty → 미분류, which beats a wrong pillar |
| `links` | `kind\|url` pairs — kinds and sourcing rules in R10 |
| `published` / `generated` | the paper's date / this rewrite's, as the clock reads when you write it. The landing page **orders the corpus by the commit that lands the file** — its add, or the `analysis: update <id> rewrite` that redoes it — so 최근 is the order a reader watched rewrites appear. `generated` dates a rewrite that has not landed yet and separates two that land in one commit, which is why it carries the clock time. The build reports a value it cannot read |
| `arxiv_html` / `arxiv_fetched` | the exact version read, and when |
| `figures` | cited figure ids, verbatim from the original as `arxiv.py` reports them. **One list for both surfaces** — the build matches it both ways against every figure id cited anywhere in the file (body and 요약) and reports an id in one and not the other |
| `appendix` | the appendix sections this rewrite drew on (`[A, B, D.2, G]`), or `none` for a paper without one. Required — the build reports a missing key (R15). Never leave it empty: "I looked and there was nothing" and "I never looked" are the two cases this key exists to separate, and only `none` says the first |
| `terms` | count of inline term anchors |
| `metric` | **optional.** The one result the paper is remembered by, as a printable fragment — `<지표> <전> → <후> <단위>` for a number the paper moved, `<수치> <단위> · <함께 성립한 조건>` for one it holds under a constraint. The landing list cannot pull a number out of `summary`'s prose, so it is stated once here and printed on the landing list on its own 결과 line under the tagline, and in the foot of a comparison's paper card. Under 40 characters (the build reports longer), no verb, no claim the paper does not make. A paper whose contribution is not a single number **omits the key** — an invented headline number is worse than none |
| `generator` | `analyze/v3` |

**The `alias` ladder.** Take the first rung that yields a name:

1. The prefix before the first colon in the paper's own title (`T-Rex`,
   `Being-H0.7`).
2. An acronym the paper defines for itself as `ACRONYM (Full Expansion)` in
   the title, abstract or intro, whose expansion initials spell it
   (`Human Universal Grasping` → `HUG`).
3. The name the authors give their own method in their prose — introduced as
   "we propose X" / "we call it X" / "our X" and used as its designator from
   there on, **even when never expanded** (`DQ-RISE`). It qualifies only if it
   reads as a proper name — capitals, digits or a hyphenated compound — so
   "our quantized hand state policy" yields nothing.
4. Otherwise **omit the key.** A descriptive title whose method is never given
   a name of its own gets no alias; one is never invented.

**Source contract.** Facts come from the paper's arXiv HTML original; *the
axis view* — `D#` impact, tensions, what the research axes would check — comes
from `context/`. A paper with no HTML edition gets **no rewrite**: an
abstract-based fallback would be indistinguishable on the page from a real one.

**Stance.** Facts are the paper's. Opinions are ours and must anchor to a `D#`
that exists in the Decision Log — never invent a position `context/` does not
hold. Where our context has no view, relay without one. Subjective judgements
take a hedge (`~인 것 같아요`); a flat assertion of an opinion reads as AI.

**A `D#` is an anchor, never the subject.** The token is a join key — the lint,
the Decision Log and the site all resolve on it — not a name the reader knows.
So the sentence says the decision in Korean and the `D#` rides along in
parentheses:

    디코더는 body/hand 라는 해부학 축으로 나뉩니다(D3GS).   ← 이렇게
    D3GS 은 body/hand 라는 해부학 축입니다.                  ← 이렇게 말고

This binds everywhere the reader reads a sentence: prose, callout bodies, a
section heading's Korean half, and the Korean inside a fence — a `probe-quiz`
question and its options, a `probe-term` body. It does
**not** reach the four places the token *is* the key — a table's Decision
cell, a heading's keyword slot, a `co-ten` label, and the `P# / D#` form naming
an allocation — because there the reader is looking at a label.

Anchor the decision once per paragraph or bullet, on its first mention; a
second `(D3GS)` three lines down is noise. Naming the decision is also what
stops `D3AG 과 충돌한다` — a sentence that satisfies the anchor rule while
telling the reader nothing.

---

## 2. Body Rules (R1–R15)

Free-form Korean markdown under a fixed four-act spine. There is no section
schema beyond the acts — a rigid spine would turn a re-telling back into a form
to fill in.

### 2-1. R1 — Four acts, always

```
1 무엇이 문제인가   — the problem, and where existing approaches stop
2 무엇을 바꿨나     — the core insight + the design. The paper's method
3 정말 되는가       — experiments, numbers, ablations
4 연구축에 무엇이 걸리나 — the axis layer: `D#` impact, and what it checks
```

Section count varies per paper; the acts are always four. **Act 2 legitimately
thins out** on a dataset, benchmark or survey paper — it then covers what was
built and the choices behind it (collection protocol, annotation, splits,
filtering) and stays short. Say so plainly rather than inflating it; act 4 for
such a paper leans on what it adds to our corpus rather than on Decision
conflict.

### 2-2. R2 — The heading spine

Four levels, none of which renders as its own tag.

| Level | Renders as | Carries |
|---|---|---|
| `#` | the page's thesis line | one sentence — **not** the paper's title |
| `##` | a numbered divider band | an act name, no content |
| `###` | the page's `<h2>` + a TOC entry | a section title **and** its English keyword line |
| `####` | a sub-point inside a section | — |

```markdown
# <thesis — the one sentence worth remembering>
## 1 무엇이 문제인가
### <이 논문에만 맞는 제목> | <English Keyword> · <English Keyword>
#### <세부 논점>
```

- **`#` carries the thesis.** The header already prints the title from
  `title:`, so repeating it wastes the first line. If the paper has a metaphor
  in it, this is where it goes. Exactly one H1, before act 1. The `한 문단 요약`
  block is printed under it from `summary:` — do not write one into the body.
- **`##` keeps its act number.** The table of contents groups sections under it.
- **`###` carries its English keyword line in the heading**, after a `|`.
  Written as the paragraph below, it becomes body text, never reaches the TOC,
  and reads as a stray sentence — the build reports it.
- **Section titles describe *this* paper.** Template titles are banned:
  "왜 이 문제가 생기는가" or "무엇을 시사하는가" fit any paper and therefore say
  nothing. Skimming the titles alone must convey the argument. Aim for a claim,
  not a topic — across different papers: "픽셀은 3D를 모른다" · "990 ms 의 벽" ·
  "FFN 하나를 공유했더니 전부 무너졌다".
- **No 원문 절번호 in the title.** Origin stays traceable through figure
  captions and equation labels.

### 2-3. R3 — Density: high

Roughly 20 lines per section expanded; rewrites in this corpus run 600–1,100
lines per paper, both surfaces included. Quotes, numbers and our callouts stay
in the body. Only **equation derivations, training configs, task definitions
and appendix detail** are collapsed, with a container:

    ::: details <요약 라벨>
    | 항목 | 값 |
    |---|---|
    | … | … |
    :::

NOT a hand-written `<details>` — the parser runs with `html=False`, so raw HTML
is escaped and published as visible angle brackets. The container body is
ordinary markdown, so tables and math work inside it.

The bar is the **restoration floor**: a reader who never opens the paper must
be able to explain the mechanism, the evidence and the numbers. Naming a
concept and moving on is a failure — say what it does *there*, and what
changes because of it.

### 2-4. R4 — Background: inline anchors only

Explain a term where it FIRST appears. No document-level primer, no
per-section primer, no global glossary — if the reader has to leave the
sentence, the explanation is in the wrong place.

Authoring syntax is `[<표시할 말>](term:<id>)`, a reserved link scheme resolved
by the renderer, with the definition body in a fence:

    ```probe-term
    {"id": "<id>", "title": "<Term>",
     "body": "<한 줄 정의 + 왜 여기 쓰이는지>"}
    ```

| Key | Meaning |
|---|---|
| `id` | matches the anchor's `term:<id>`; unique per document |
| `title` | the term as the paper writes it |
| `body` | one or two sentences — definition, then why it matters *here* |

**The definition opens at the anchor, inside the paragraph** — wherever the
fence sits after it (the renderer pre-scans them). So do not place a fence for
visual reasons, and do not repeat an anchor to "bring the definition closer".

Aim for 12–20 anchors and count them into `terms:`. Every anchor needs a
definition and every definition an anchor — the build reports both halves,
and a duplicate `id`.

### 2-5. R5 — Context: five kinds, planted deliberately

These are what the original paper cannot give you; they come from reading
across our corpus.

**Three of them have a component and MUST use it.** Written as prose they
satisfy the rule and show the reader nothing — which is how a page ends up
reading flat however good the sentences are. **The build reports a rewrite
that uses none of the three.**

**1. 계보** — the line of work this sits in, in time order. If our corpus
already covered a paper in that line, link it.

    ```probe-lineage
    {"title": "<계보의 이름>",
     "items": [
       {"when": "YYYY-MM", "what": "<선행 연구 — 한 줄 정체>",
        "note": "<무엇이 장점이고 무엇이 남았나>",
        "link": "<url>", "link_label": "<표시할 라벨>"},
       {"when": "YYYY-MM", "what": "<지금 읽는 논문>", "current": true,
        "note": "<앞의 것들과 무엇이 다른가>"}]}
    ```

At most one entry carries `current: true` — the paper being read. That is what
turns a bibliography into a position. **Do not invent a lineage**: draw it from
`context/P#.md` §Tracked Literature and from the rest of `analysis/`, and
verify each link resolves before citing it. `link` is always the paper's own
arXiv abstract; the build adds the 재작성본 marker itself (§3-3).

**2. 숫자의 지형** — the paper's key number placed against the others of its
kind (a human baseline, a hardware limit, another paper we read).

    ```probe-scale
    {"title": "<이 숫자는 어디쯤인가>",
     "rows": [{"label": "<비교 대상>", "n": <number>, "value": "<표시 형태>"},
              {"label": "<이 논문>", "n": <number>, "value": "<표시 형태>",
               "us": true}]}
    ```

`n` is the NUMBER — the bar is drawn from it, linearly, against the largest row
— and `value` is how it prints; `us: true` marks this paper's row. Bars are
linear on purpose: when our row is a stub next to the top of the range, the
reader should see the stub.

**3. 대조** — two or three things held apart, or one object decomposed.

    ```probe-split
    {"cards": [{"title": "<A>", "tag": "<짧은 꼬리표>",
                "body": "<본문>", "note": "<한 줄 논평>"},
               {"title": "<B>", "tag": "<짧은 꼬리표>", "us": true,
                "body": "<본문>", "note": "<한 줄 논평>"}]}
    ```

    ```probe-parts
    {"rows": [{"label": "<구간 이름>", "range": "<표기>", "state": "<이 구간의 상태>",
               "body": "<이 구간이 무엇인가>"},
              {"label": "<구간 이름>", "range": "<표기>", "state": "<이 구간의 상태>",
               "body": "<이 구간이 무엇인가>"}]}
    ```

`probe-split` for a contrast (2–3 cards), including a corpus paper that
prescribed something different for the same problem; `probe-parts` for one
thing cut into named regions.

**`us` marks 이 논문의 자리** — the card holding the position this paper takes
in the contrast, and the only card that carries a color, as `us` does on a
`probe-scale` row and `current` on a `probe-lineage` entry. So:

- **At most one card, and often none.** Two peers held apart (`매끄러움` vs
  `반응`), two rejected alternatives, two halves of the paper's own
  architecture, a wins-column against a loses-column — none has a card that is
  the paper's position, and all render plain. The build reports a second `us`.
  Reach for it when a card can be labelled `이 논문 — …` or its note says
  이 논문이 서는 자리, not to brighten a block.
- **The paper's position, not the reading you prefer.** A contrast between
  what this paper measured and what our stack would need marks the paper's
  card; where we stand goes in `note`.
- **Color is never card identity.** Cards are told apart by their titles and
  `tag`, in the order the rewrite argues them — a contrast that grows a card
  grows one more plain card.

**`state` is the rewrite's own word**, not a value from a fixed list. Each
paper cuts its object into the conditions *that* paper argues about — how
pinned down a region is, which channel a block belongs to, which stage owns it
— and the fence hands out a color per distinct state, in first-appearance
order. Write the states as short parallel phrases, one grammatical shape
across the rows, so the column reads as one question answered per region.

- **Rows in the same state share a color, and that is the point** — the
  rewrite says they are in one condition, and the printed state says which.
  Colors are grouping, never row identity.
- **Every row carries a state, or none does.** Unlabelled rows in a
  half-labelled band render neutral and read as leftovers; the build reports
  it.
- **At most four distinct states.** Past four the color stops sorting anything
  — merge the states that mean the same thing, or the decomposition is a
  table. The build reports a fifth.

**4. 출처·배경** — where the technique came from, and why it arrives now. A
`co-ctx` callout and term anchors.

**5. 코퍼스 지도** — where this sits among what we have read, plus the question
nobody has answered yet. Act 4.

### 2-6. R6 — Figures: the paper's own, first

Architecture, pipeline, benchmark and hardware figures are hotlinked from
arXiv:

    ```probe-figure
    {"id": "<figure id from arxiv.py>", "url": "<absolute arXiv url>",
     "caption": "<한글 캡션>", "source": "Figure <n>, 원문 §<x.y>"}
    ```

**"First" is a ranking, and it is the rule most easily lost.** The authors drew
their figures to carry the paper's argument, and the reader can hold ours
against the original.

- **The figure that carries the paper's central mechanism is not optional.**
  If the paper illustrates the thing the rewrite is named after — the schedule,
  the pipeline, the architecture — that figure is cited, in the section that
  explains it. An Act 2 with no figure while the paper has one is wrong
  however good the prose is.
- **A figure left out is a decision to be able to defend** — above all one
  that shows a mechanism, a timeline, a rig or a task set. Appendix figures
  count: they are usually the rig, the task set, the ablation curves and the
  error analysis (R15).
- **"Unlinkable" means one thing**: LaTeXML drew the figure as inline `<svg>`
  (a TikZ/PGF picture), so there is no file behind it and `arxiv.py` reports
  an empty `url`. A figure exported to a standalone `.svg` and embedded with
  `<object data>` is an ordinary file and hotlinks like a PNG — do not redraw
  it. An unlinkable figure is redrawn or left unillustrated, never linked by a
  broken URL. **An algorithm listing** is transcribed as a captioned code block
  (R8) rather than redrawn as boxes: it is the paper's own artifact, line
  numbers and all.
- **Never mirror an image into the repo** — hotlink only, on copyright
  grounds. The build reports a relative `url`.
- Caption: translate the original caption to Korean. The origin goes in
  `source`, never in `caption`.
- **A caption is plain text** — escaped, not parsed, so `**강조**` and
  `` $`math`$ `` publish as their own characters. Write Greek letters and
  symbols as themselves (`α`, `s_min`, `H−d`) and carry emphasis in the
  paragraph next to the figure. The build reports the two most common cases,
  not every one.
- **`source` is split on its first comma** — the head becomes the
  figure-number badge that leads the caption (`Figure 3 — …`), the tail the
  italic origin at the end (`(원문 §3.2)`). Written as one run with no comma,
  the whole thing prints as the origin with no badge.
- Where the paper has NO corresponding figure and a sequence still needs
  showing, use `probe-flow` — never ASCII art, never raw HTML:

      ```probe-flow
      {"title": "<이 흐름의 이름>",
       "why": "<원문의 어느 그림도 이 지점을 덮지 못하는 이유>",
       "steps": [{"label": "<단계>", "note": "<조건이나 빈도>"},
                 {"label": "<단계>"}]}
      ```

  **`why` is required and prints under the diagram.** A redrawn box competes
  with figures the authors already made, and when it wins by accident the page
  shows our labels where the paper had a picture. Name which figure would have
  covered the point and why it cannot serve (no such figure / inline SVG with
  no file). If the paper does illustrate it, use `probe-figure` instead.

### 2-7. R7 — Math

- Inline math is `` $`X`$ ``. Display math goes in a `probe-eq` fence, which
  carries its reading line and symbol table with it. `tex` is raw LaTeX with no
  delimiters. Full dialect and its failure modes: §3-1.

      ```probe-eq
      {"read": "<이 식을 한국어 문장으로 읽으면>",
       "tex": "<LaTeX, 구분자 없이>",
       "symbols": [{"sym": "<기호>", "name": "<이름>", "note": "<설명>"},
                   {"sym": "<기호>", "name": "<이름>", "note": "<설명>"}]}
      ```

  The reading line is the point of the fence — the build reports an equation
  without one. `read` prints above the formula; `symbols` prints as a
  기호 / 이름 / 설명 grid with no header row, so do not add one. Formulas set
  in the body font instead of KaTeX's are a build fault, never something to
  work around in the source.
- **Explain DISPLAY equations only.** Inline symbols are handled by term
  anchors (R4).
- **First occurrence only.** A symbol that returns later gets a back reference
  or nothing.

### 2-8. R8 — Code: language **and** caption

Pygments language highlighting — the paper's pseudocode, our mapping code,
configs, diffs. The info string carries two things:

    ```<lang> <한글 캡션>
    <code>
    ```

    ```python 학습 스텝 — 계단 스케줄 + 앞부분 마스킹

- **The language is mandatory** and prints as the chip on the block's header
  bar.
- **The caption is mandatory too** — everything after the first space, and the
  build reports a block without one. One line naming what the block
  *demonstrates* is what turns transcribed pseudocode into an exhibit. Write it
  in Korean, as a noun phrase, and never name the language, which the chip
  already says.
- **The code font covers only the characters this corpus uses**
  (`site/builder/fonts.py`), and the build reports one it cannot cover
  (`mono font gap`). The paper's own Greek letters, arrows and operators
  (τ, Δ, →, x̂) are covered. Avoid what is not: a precomposed accented letter
  (ẑ, U+1E91) where the same block writes x̂ / z̄ as base letter plus combining
  accent — match that form; and a symbol with an ASCII stand-in in pseudocode
  (`||` for norm bars, not `‖`; `(1)`, `(2)`, not `①②`). Genuine paper
  notation belongs in inline math (`` $`\mathcal N`$ ``, §3-1), which has no
  such gap.

### 2-9. R9 — Callouts: five roles, mechanically applied

Authored as GFM alert syntax, which this renderer maps to the five roles:

```markdown
> [!CAUTION] <선택 라벨>
> <본문>
```

The text after the marker is an optional label; without one the role's own name
is used. Never write the `co-*` class by hand.

| marker | class | role | test question |
|---|---|---|---|
| `[!NOTE]` | `co-key` | 작동 원리 | explains why/how it works |
| `[!TIP]` | `co-win` | 확인된 이득 | a measured result (numbers) |
| `[!WARNING]` | `co-warn` | 한계·비용·조건 | a cost, failure mode, limit |
| `[!CAUTION]` | `co-ten` | 연구축과 충돌 | a `D#`/`P#` shakes |
| `[!IMPORTANT]` | `co-ctx` | 논문 밖 맥락 | lineage, background, corpus |

- **`co-ten` is ACT-4 ONLY.** A problem the paper points out about itself is
  `co-warn`. Without this discipline the things that matter *to us* are
  visually buried among the things that merely matter.
- **Author-stated limitations close ACT 3**, as `co-warn`. They must not land
  after Act 4's verification plan — the authors' admission is an INPUT to our
  plan, not a footnote to it.
- **One point per callout, and at most 400 printed characters** — counted on
  what the reader sees, so emphasis markers and TeX macros cost nothing. A
  callout is an aside the eye takes in one stop; past that length it is a
  section wearing a border, and the paragraph it interrupted is gone by the
  time the reader comes back. The build reports an over-long body. A run of
  author-stated limitations is one clause each inside the callout, with the
  elaboration in a `::: details` under it.

### 2-10. R10 — Resource links

The header's resource links are built from `links:`. What you author is the
`kind|url` pair; the labels, order and marks are the site's
(`LINK_KINDS` in `site/builder/corpus.py`, `SRC_MARKS` in
`site/builder/components.py`), and adding or renaming a kind is a code change
in both plus the list below.

- **Six kinds, and only these**: `arxiv` `code` `weights` `data` `site` `demo`.
  An unknown kind is dropped rather than guessed at.
- **ONLY URLs confirmed in the paper body or abstract.** Never guess a
  repository owner, never construct a model-hub path.
- **Unconfirmed → leave the slot empty.** Do not write "없음". A short link row
  is itself reproducibility information.
- Write them in any order — the cells sort themselves.
- No `P#` pillar chips in the header. No eyebrow tag above the title.

### 2-11. R11 — Quizzes

Exactly one per section, three options, one correct.

    ```probe-quiz
    {"q": "<질문>", "options": ["<A>", "<B>", "<C>"], "answer": <0-2>,
     "why": "<왜 정답인지 + 나머지 둘이 왜 틀렸는지>"}
    ```

The explanation must say why the *other* two are wrong; one that only restates
the answer teaches nothing. The quiz locks on the first click, so write three
options a reader could plausibly hold, not two obvious throwaways beside the
answer. The build reports a section without exactly one quiz, and a quiz
without exactly one correct option.

### 2-12. R12–R14 — Implementation and authoring traps

- **R12. Visual rules are the site's, not the author's.** Typography, spacing,
  color and code highlighting live in `site/builder/assets/`; the invariants
  they keep are in `site/CLAUDE.md`. No inline styles, no `<style>` blocks, and
  no blank paragraph, `&nbsp;` line or `<br>` to open space around a component
  — each component already sets its own. The page also *adds* chrome your
  source never mentions, and re-adding it by hand duplicates it: the masthead
  eyebrow (`읽기 쉬운 버전 · 원문에서 직접 발췌`), the rule that closes the
  thesis + tagline + summary block, the hairline over every `###`, the act
  divider's bar and each component's title band. Write the content; the page
  frames it. A `###` keeps an `id` but prints no `#` link, so refer to another
  section in plain words where that reads better than a `#id` link.
- **R13. No raw HTML.** The parser runs with `html=False`, so a tag in the
  source — `<br>` in a table cell, `<b>` in prose — prints as its own
  characters. Emphasis is `**…**`; a table cell that needs two parts takes
  ` / ` or a parenthesis (`Pull Tissue (Grasp / Place)`); anything larger is a
  component. A token or placeholder the paper itself spells in angle brackets
  (`<SEG>`, `<object>`) is text and stays. The build reports the layout tags
  (§5).
- **R14. A `**` run cannot close between a closing paren and a Korean
  particle** — see §3-2.

### 2-13. R15 — The appendix is a source, not an annex

In this corpus the appendix is the second half of the source, and R3's
restoration floor is not reachable without it. Typically it holds:

| Usually in the appendix | Why the rewrite needs it |
|---|---|
| **Limitations / Future Work** | R9 requires the author-stated limitations to close Act 3. On many papers that section exists ONLY in the appendix |
| Related Work | the honest input to the 계보 component (R5) — the authors' own placement of their work |
| The rig | robot, DoF count, cameras, sensors, control rate, **what the observation vector actually contains**. The main text says "proprioception"; the appendix says which 45 numbers |
| Training recipe | steps, batch, what was frozen, how a new parameter was initialised, which rows share a checkpoint |
| Baseline settings | the one hyperparameter that is not symmetric between the method and its strongest baseline |
| Evaluation protocol | trial count, time limit, how a partial-credit score decomposes |
| Algorithm listings | the method as executable steps — see R6 on transcribing them |
| Per-task tables, ablation curves, error analysis | the numbers Act 3 argues from, and the figures that show their shape |

- **A section with real content that the rewrite ignores is a decision to be
  able to defend.**
- **Cite the section you took it from** — `(부록 D.2)`, `원문 부록 F.4` — in
  prose and in a figure's `source`. It is the only way a reader can go back,
  and it is how a mis-attribution gets caught.
- **`appendix:` in the front matter lists what you drew on.** The build cannot
  check it against the paper; the key makes the sweep a step performed rather
  than one meant.
- Appendix detail is exactly what `::: details` (R3) is for. Collapsing it is
  fine; leaving it out is not.

---

## 3. What Publishes as Literal Text

The failures below are not parse errors. The source is valid Markdown and the
sentence still reads correctly in the file — the page just prints the notation
instead of rendering it. The build reports each one; this section says what to
write so it does not have to. Raw HTML fails the same way (R13).

### 3-1. Math: three accepted forms, and nothing else

| Form | Use |
|---|---|
| `` $`X`$ `` | inline math — backticks INSIDE the dollars |
| `$$X$$` alone on a line at **column 0** | a single-row display equation |
| a ` ```math ` fence at column 0 | a multi-row display (`\\` row breaks) |

Everything else is text to this parser and reaches the page as itself:

| Written | Published as |
|---|---|
| `$X$` | `$X$` — there is deliberately no plain-`$` rule, because Korean prose quotes prices and a lone `$` would silently open a formula |
| `` `$X$` `` | a code span; the math never runs |
| `\(X\)` / `\[X\]` | `(X)` / `[X]` — the backslashes are Markdown escapes and vanish |
| `$$X$$` indented under a list item | the raw `$$X$$` |

A display equation belonging to a list item is pulled out to column 0 — or,
preferably, written as a `probe-eq` fence (§2-7), the only form that carries a
reading line and symbol table.

**Code span vs. math.** Backticks for literal source tokens (identifiers,
config keys, dtypes, CLI flags), tensor shapes and numeric specs; inline math
for genuine paper notation (Greek letters, variables, sub/superscripts,
operators, set and interval notation). The discriminating signal is a Greek
letter, a LaTeX macro, a math operator or an equation `=` — never `×` / `·` /
`_` alone, which occur in shapes and specs too.

KaTeX renders server-side at build time, so a macro that works in KaTeX works
here. There is no macro whitelist to memorize.

### 3-2. Emphasis that never closes

CommonMark closes an emphasis run only where the delimiter is
*right-flanking*, and a `**` between punctuation and a letter is not. In Korean
that is an ordinary sentence shape: a parenthetical gloss, then a particle.

| Write | Not |
|---|---|
| `**<구A>**(<보충>)과 **<구B>**(<보충>)로` | `**<구A>(<보충>)과 <구B>(<보충>)**로` |

Both markers publish as literal asterisks, and the sentence still makes sense
on the page, which is why it survives review. Bold the phrase, not the phrase
plus its parenthesis.

### 3-3. A bare URL is not a link

`linkify` is off, so a bare `https://…` in prose renders as plain text. Every
URL is explicit `[텍스트](…)` link syntax, which also keeps the prose readable.
Inside a code span a bare URL is fine and stays literal.

An `arxiv.org/abs|html|pdf` link whose id has a rewrite in `analysis/` gains a
재작성본 marker to that paper's page automatically, in prose and in a
`probe-lineage` rail alike — so link the arXiv page and never write a
`../<id>/` site path by hand.

---

## 4. The 요약 Surface (G1–G7)

One screen that answers "what is this paper, and why should I care" before the
reader commits to the body. It is authored as a `::: glance` container at the
end of the file, after act 4's last section; the build carves it out before
the body renders, so nothing inside it reaches 상세:

````markdown
…act 4's last quiz…

::: glance

```probe-hub
{…}
```

<내러티브 — 8–10 연>

```probe-rail
{…}
```

```probe-act
{"n": 1, …}
```
…three more probe-act…

:::
````

A file without the container is reported (the tab would publish empty).

### 4-1. G1 — Written from the original, like the body

요약 draws on the same parsed original as the body and cites the same way. It
is never written by re-reading `analysis/<id>.md` and shortening it:

- a digest of a digest inherits every choice the body already made — which
  figure was dropped, which number was rounded — and adds nothing;
- the two surfaces rank the paper's material differently. A figure that sits
  mid-body is often the one 요약 leads with;
- a 요약 derived from the body goes stale the moment the body is edited, and
  nothing on the page says so.

What the two surfaces **do** share, as inputs rather than text: the thesis line
(the body's `#`) and the act order. **No sentence is copied from the body** —
same facts, written again.

### 4-2. G2 — The spine, in this order

```
probe-hub      중심 주장 카드 — the thesis, one line, a few numbers, one figure
<내러티브>       flowing Korean prose, no bullets
probe-rail     팩트 레일 — 어떤 판본 · 무엇에 · 얼마나 · 어떤 조건에서
probe-act ×4   the evidence, one card per act
```

Four parts, always, in that order. The reader's path is
**claim → story → conditions → evidence**; reordering them makes the numbers
arrive before the reason they matter.

### 4-3. G3 — `probe-hub`, the claim in one card

    ```probe-hub
    {"thesis": "<한 문장 — 논문 제목이 아니라 연구축이 읽어낸 테제>",
     "line": "<무엇을 어떻게 바꾸는가 — 한 줄>",
     "figure": "<figure id>", "caption": "<한 줄 캡션>",
     "facts": [{"k": "<지표 이름>", "v": "<값 · 단위>"},
               {"k": "<지표 이름>", "v": "<값 · 단위>"}]}
    ```

- `thesis` is the body's `#` — the same sentence, because a page cannot argue
  two theses. It is **not** the paper's title, which the header already prints.
- `facts` — **2 to 4**, and each must be a number the paper itself states. Past
  four they stop being headlines and become a table.
- `figure` is optional and, when present, is the figure a reader would keep if
  they could keep only one (figure ids on this surface: G6).

### 4-4. G4 — The narrative

Flowing Korean prose — a colleague telling you what the paper does, not a
report. The body argues; this talks.

| | |
|---|---|
| Length | **8–10 연**, 900–1,100 printed characters (about 1 분 40 초 읽기). The build reports outside **8–10 연 / 750–1,350 자** — "roughly" is the author's business, "a paragraph" and "the body again" are the build's |
| Shape | stanzas of 2–4 sentences, one move per stanza: 무슨 일 → 그 결과 → 이유 |
| Register | 폴라이트-캐주얼 종결 (`~요` / `~ㅂ니다`), 괄호 방백 허용, 감탄은 진짜일 때만 |
| Closing | the last stanza is a **한 줄 토** built from the paper's own stated limits |

Hard constraints:

- **No bullets, no headings, no numbered lists, no quote blocks.** A list here
  is a summary wearing prose clothes, and the tab already has cards for that.
- **Every number in it appears elsewhere with a citation** — the rail or an act
  card. The narrative itself carries no source marks; they would break the read.
- **No opinion the paper does not hold** (G7). Relaying is the whole job here.
- **Not `summary:` again.** That is 2–3 sentences read cold; this is a
  different artifact at ten times the length and does not restate it phrase for
  phrase.

### 4-5. G5 — `probe-rail`, the conditions beside the prose

    ```probe-rail
    {"items": [{"k": "<항목>", "v": "<값>", "note": "<선택 — 한 줄>"}]}
    ```

**5–7 items.** The rail answers the questions a reader forms while reading the
narrative, so it is keyed by question, not by a fixed schema:

| The question | Typical item |
|---|---|
| 무엇을 읽었나 | the exact version and date |
| 무엇에 적용했나 | the models, backbones or datasets the method was put on |
| 얼마나 | the two or three headline numbers |
| 어떤 조건에서 | rig, hardware, control rate, trial count — whatever the claim depends on |
| 무엇과 비교했나 | baselines and benchmarks |
| 저자는 무엇을 못 한다고 했나 | the author-stated limits, in three or four words |

The last row is not optional padding: without it the tab reads as advocacy.
The rail is **information, not decoration** — a rail of restated adjectives is
worse than no rail.

### 4-6. G6 — `probe-act`, four cards and no more

    ```probe-act
    {"n": <1–4>, "title": "<주장형 제목 — 이 논문에만 맞는>",
     "claim": "<한 줄>",
     "figure": "<figure id>",
     "eq": "<LaTeX, 구분자 없이>",
     "scale": {"rows": [{"label": "<비교 대상>", "n": <number>, "value": "<표기>"}]},
     "source": "<원문 §<x> · Table <n> · 부록 <X>>"}
    ```

- **Exactly four**, `n` = 1…4, mapping to the body's four acts. The act
  *names* are the ones this paper earns (문제 / 관찰 / 방법 / 증거 is the common
  shape, not a fixed vocabulary), but the count is fixed — a fifth card means
  the tab is becoming the body.
- **Each card carries at least one of `figure` / `eq` / `scale`.** A card of
  three prose lines is the failure this tab exists to avoid.
- **`eq` is ONE relation.** The card is a quarter of the row, and a wider
  formula scrolls inside it with its tail off-screen. Two relations joined by
  `\qquad` is the shape that overflows; pick the one the claim rests on.
- `title` follows R2: a claim about *this* paper, never a template heading.
- `source` is required on every card, so every number on this tab is
  traceable without leaving the tab.

**Figures on this surface are cited by id, never by URL** — in `probe-hub` and
`probe-act` alike. The id resolves through the body's own `probe-figure` (R6),
which already declared where the figure lives; an id the body never declares
publishes an empty frame, and the build reports it. Every such id also goes in
`figures:` (§1).

### 4-7. G7 — What 요약 may not contain

- **No `D#`, no `context/` material, no our-view opinion.** Our layer is act 4
  of the body; here it would put a claim the paper never made one card away
  from the paper's own numbers.
- **No number that is not in the original.** Nothing is computed for effect;
  a ratio the paper does not state is not ours to print.

---

## 5. Enforcement

Everything below is checked by the build, the same pipeline that produces the
page — so a rule is enforced against the artifact a reader actually gets.
`site/build-site.py` prints every problem it finds as a `warning:` line and
still writes the site; under `--strict` any problem makes it exit 1. CI builds
with `--strict` on every PR and on `main`, so "the build reports" in this file
means "a strict build fails".

| Rule | Enforced by |
|---|---|
| Front matter required keys, `analysis_of` == file name, `tagline` not echoing the title, `alias:` and `metric:` within their widths (§1), `appendix:` present (R15), the `::: glance` container present (§4) | `site/builder/corpus.py` |
| `figures:` ↔ every `probe-figure`, `probe-hub` and `probe-act` figure id across both surfaces, and every 요약 figure id declared by a body `probe-figure` (R6, G6) | `site/builder/corpus.py` |
| `###` keyword line (R2), planted-context component (R5), one quiz per section (R11), term anchor ↔ definition pairing (R4), code fence without a caption (R8), raw HTML published as text (R13), unclosed `**` (§3-2), math published as literal text (§3-1) | `site/builder/render.py` |
| `probe-*` fence schemas — term, eq, figure, flow (incl. its required `why`, R6), lineage, scale, split (at most one `us`), parts (all-or-none `state`, four-state ceiling, R5) | `site/builder/mdext/probefence.py` |
| GFM alert → `co-*` role mapping and the 400-character body ceiling (R9) | `site/builder/mdext/callouts.py` |
| The three accepted math forms (§3-1) | `site/builder/mdext/ghmath.py` |
| Characters the code font cannot cover (R8) | `site/builder/fonts.py` |
| The vendored KaTeX stylesheet keeping its faces — without it every formula publishes in the body font | `site/builder/assets_out.py` |
| 요약's spine — hub, narrative, rail, exactly four `probe-act` (G2, G6); `probe-hub` / `probe-rail` / `probe-act` payload shapes, including each card's `source` and its figure, equation or scale (G3, G5, G6); narrative length band and its list ban (G4) | `site/builder/glance.py` |
| A `D#` token or a `context/…md` path inside `::: glance` (G7) | `site/builder/glance.py` |

One check sits outside the build, because it is about meaning rather than
rendering:

| Rule | Enforced by |
|---|---|
| every `D#` cited exists in the Decision Log | `linters/check-decision-refs.py` |

A `D#` that does not resolve is not a render failure — it silently loses its
tooltip and prints as plain text, so the build cannot see it as wrong.

Verify before reporting a rewrite done:

```bash
python3 site/build-site.py --only <id> --out /tmp/probe-check --strict
python3 linters/check-decision-refs.py
```

`--strict` must exit 0. Everything in §1–§4 not in the tables above is
enforced by review, which is why the prompt's self-check exists. The rules code
cannot see decide whether 요약 is worth having: whether the narrative sounds
like a person, whether it relays an opinion of ours without naming a `D#`,
whether each act card's evidence is the right evidence, and whether the four
card titles read as an argument when skimmed alone.
