# Analysis Rewrite Authoring Guide

> **Scope:** every `analysis/<arxiv-id>.md` — the corpus the reading site
> publishes. This file is the single source of truth for that format.
> `.claude/prompts/analyze.txt` owns the *procedure* (which paper, where the
> facts come from, how to verify and commit) and defers to this file for the
> output contract; `site/build-site.py` implements it. Change a rule here
> first, then the build.

**One file, three surfaces.** A rewrite publishes as three tabs on one page:

| Tab | What it is | Rules |
|---|---|---|
| 상세 | the full re-telling — four acts, term anchors, quizzes | §1–§3 |
| 한눈에 | one screen: our thesis, a narrative, the evidence in four cards | §4 |
| 발표 | a deck for an audience outside the team | §5 |

All three are written **in the same `/analyze` run, from the same reading of
the arXiv original**, and they live in one `analysis/<id>.md`. The two short
surfaces are not summaries of the long one — see G1 and S1, which is the rule
the other two most often violate.

**The output is an HTML page.** A rewrite is Markdown only as a source
language: what a reader gets is `site/build-site.py`'s output, rendered by
`markdown-it-py` plus this repo's own extensions. Every rule below is judged
against that page — not against how github.com would render the same file.
Where the two disagree, the page wins, and §3-4 lists the sibling track's rules
that deliberately do **not** apply here.

`scouting/AUTHORING.md` governs `scouting/`, which *is* read as rendered
Markdown on github.com. It does not apply to this track, and this guide does
not cross-reference it — the rules the two tracks share are restated here in
the terms of this renderer.

---

## 1. File and Front Matter Contract

One rewrite per paper, `analysis/<arxiv-id>.md` — flat, one file per paper, no
per-paper folder. (`analysis_legacy/` is a legacy corpus in a different format;
nothing here reads or writes it.)

The site takes **all** of its metadata from this front matter — there is no
other source, so a missing field is a hole on the landing page.

```yaml
---
analysis_of: <arxiv-id>          # MUST equal the file name
title: "<the paper's own title, verbatim>"
tagline: <one line: what this paper does>
authors: <first authors et al. (affiliation)>
pillars: P<a>, P<b>              # ours — the first decides the card's group
tags: [<tag>, <tag>]
links: [arxiv|<url>, code|<url>]
published: YYYY-MM-DD            # the paper's date, from arXiv
generated: YYYY-MM-DD            # yours — this sorts the landing page
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
| `analysis_of` | must equal the file name — **mismatch fails the build**. This catches the copy-paste that lands a rewrite under the wrong id |
| `title` | required. The paper's title, as the card and the page header print it |
| `tagline` | required. **One line naming what the paper does**, printed under the body H1 and under the title on the landing page. The H1 is our thesis and often a metaphor, so on its own it does not tell a reader which paper they opened; the header prints the paper's own title. This is the sentence between them. **It never restates the paper's name** — `<코드명> — <무엇을 하는가>` printed under a title that already reads `<코드명>: <…>` spends the one line the tagline has on the word directly above it. Open with what the paper does, not with the codename; **the build reports the echo** |
| `summary` | required. 2–3 sentences, read cold. Printed **on the page** as the `한 문단 요약` block between the thesis line and act 1, and flattened for the landing card. Authored as markdown — `**강조**` and `` $`math`$ `` render on the page and are stripped for the card, so bold the three or four phrases that carry the argument (§3-2 applies) |
| `authors` | one line, as printed |
| `pillars` | **ours**, not the paper's — read `context/P#.md` and pick honestly. First entry decides the card's group; empty → 미분류, which beats a wrong pillar |
| `tags` | flow list, feeds the landing page's filter chips. Free vocabulary; the bar offers the most common facets and search covers the tail |
| `links` | `kind\|url` pairs; kinds fixed at `arxiv` `code` `weights` `data` `site` `demo` (R10). Unknown kinds are dropped rather than guessed at |
| `published` / `generated` | the paper's date / this rewrite's. `generated` sorts the landing page |
| `arxiv_html` / `arxiv_fetched` | the exact version read, and when |
| `figures` | cited figure ids, verbatim from the original as `arxiv.py` reports them. **One list for all three surfaces** — the build matches it both ways against every figure id cited anywhere in the file (body, glance, deck), and an id in one and not the other is reported |
| `appendix` | the appendix sections this rewrite drew on (`[A, B, D.2, G]`), or `none` for a paper without one. Required — see R15. An empty value is not accepted, because "I looked and there was nothing" and "I never looked" are the two cases this key exists to separate |
| `terms` | count of inline term anchors |
| `metric` | **optional.** The one result the paper is remembered by, as a printable fragment — `<지표> <전> → <후> <단위>` for a number the paper moved, `<수치> <단위> · <함께 성립한 조건>` for one it holds under a constraint. The number is already in `summary`, but as prose — the landing list cannot pull it out of a sentence, so it is stated once here and printed as a chip beside the title. Under 40 characters (**longer fails the build**), no verb, no claim the paper does not make. A paper whose contribution is not a single number **omits the key** — an invented headline number is worse than none |
| `generator` | `analyze/v3` |

**Source contract.** Facts come from the paper's arXiv HTML original (parsed
by `site/builder/arxiv.py`); *our view* — `D#` impact, tensions, what we
would check — comes from `context/`. `analysis_legacy/` is neither read nor
written.
No HTML edition (~4% of papers) means **no rewrite is written**: an
abstract-based fallback would be indistinguishable on the page from a real one.

**Stance.** Facts are the paper's. Opinions are ours and must anchor to a `D#`
that exists in the Decision Log — never invent a position `context/` does not
hold. Where our context has no view, relay without one. Subjective judgements
take a hedge (`~인 것 같아요`); a flat assertion of an opinion reads as AI.

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
4 우리는 무엇을 하나 — our layer: `D#` impact, and what we would check
```

Section count varies per paper; the acts are always four. **Act 2 legitimately
thins out** on a dataset, benchmark or survey paper — it then covers what was
built and the choices behind it (collection protocol, annotation, splits,
filtering) and stays short. Say so plainly rather than inflating it; act 4 for
such a paper leans on what it adds to our corpus rather than on Decision
conflict.

### 2-2. R2 — The heading spine

Three levels, none of which render as their own tag.

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

- **`#` carries the thesis.** It is NOT the paper's title: the header already
  prints that from `title:`, so repeating it wastes the first line. If the paper
  has a metaphor in it, this is where it goes. Exactly one H1, before act 1. The
  `한 문단 요약` block is printed under it from `summary:` — do not write one
  into the body.
- **`##` keeps its act number.** The table of contents groups sections under it.
- **`###` must carry its English keyword line in the heading**, after a `|`.
  Written as the paragraph below the heading it becomes ordinary body text,
  never reaches the TOC, and reads as a stray sentence — **the build warns**.
- **Section titles describe *this* paper.** Template titles are banned:
  "왜 이 문제가 생기는가" or "우리에게 무슨 의미인가" fit any paper and
  therefore say nothing. Skimming the titles alone must convey the argument.
  The shape to aim for is a claim, not a topic — across different papers:
  "픽셀은 3D를 모른다" · "990 ms 의 벽" · "FFN 하나를 공유했더니 전부 무너졌다".
- **No 원문 절번호 in the title.** Origin stays traceable through figure
  captions and equation labels.

### 2-3. R3 — Density: high

Roughly 20 lines per section expanded, ~420 lines per paper. Quotes, numbers
and our callouts stay in the body. Only **equation derivations, training
configs, task definitions and appendix detail** are collapsed, with a
container:

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

**The definition opens at the anchor, inside the paragraph** — not under it.
The fence may sit anywhere after the paragraph (the renderer pre-scans them);
where you *write* it does not change where it *opens*. So do not try to place a
fence for visual reasons, and do not repeat an anchor to "bring the definition
closer" — it is already there.

Aim for 12–20 anchors and count them into `terms:`. Every anchor needs a
definition and every definition needs an anchor — the build reports both
halves, and a duplicate `id`.

### 2-5. R5 — Context: five kinds, planted deliberately

These are what the original paper cannot give you; they come from reading
across our corpus.

**Three of them have a component and MUST use it.** Written as prose they
satisfy the rule and show the reader nothing — that is exactly how a page ends
up reading flat no matter how good the sentences are. **The build warns if a
rewrite uses none of the three.**

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
turns a bibliography into a position. **Do not invent a lineage**: check
the rest of `analysis/` for a site link and `context/P#.md` §Tracked
Literature otherwise,
and verify each link resolves before citing it.

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
    {"cards": [{"title": "<A>", "tag": "<짧은 꼬리표>", "tone": "cold",
                "body": "<본문>", "note": "<한 줄 논평>"},
               {"title": "<B>", "tag": "<짧은 꼬리표>", "tone": "warm",
                "body": "<본문>", "note": "<한 줄 논평>"}]}
    ```

    ```probe-parts
    {"rows": [{"label": "<구간 이름>", "range": "<표기>", "state": "<이 구간의 상태>",
               "body": "<이 구간이 무엇인가>"},
              {"label": "<구간 이름>", "range": "<표기>", "state": "<이 구간의 상태>",
               "body": "<이 구간이 무엇인가>"}]}
    ```

`probe-split` for a contrast (2–3 cards; `tone`: `cold` / `warm` / `plain`);
`probe-parts` for one thing cut into named regions. `probe-split` is also the
right component for a corpus paper that prescribed something different for the
same problem.

**`state` is the rewrite's own word**, not a value from a fixed list. Each
paper cuts its object into the conditions *that* paper argues about — how
pinned down a region is, which channel a block belongs to, which stage owns it
— so the fence takes those words and hands out a color per distinct state, in
the order the states first appear. Write them as short parallel phrases: one
grammatical shape across the rows, so the column reads as one question answered
once per region.

- **Rows in the same state get the same color, and that is the point** — two
  regions wearing one wash means the rewrite says they are in one condition,
  and the printed state says which. Colors are grouping, never row identity.
- **Every row carries a state, or none does.** A half-labelled band claims the
  unlabelled rows have no state; those rows render neutral and read as leftovers.
- **At most four distinct states carry a color.** Past four the color stops
  sorting anything — merge the states that mean the same thing, or the
  decomposition is a table.

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
against the original. So before any hand-made component goes on the page, the
paper's own figure list is walked:

- **The figure that carries the paper's central mechanism is not optional.**
  If the paper illustrates the thing the rewrite is named after — the schedule,
  the pipeline, the architecture — that figure is cited, in the section that
  explains it. A rewrite whose Act 2 has no figure while the paper has one is
  wrong regardless of how good the prose is.
- **Read `arxiv.py`'s figure list as a checklist, not as a menu.** Its CLI
  prints the linkable count and marks every unlinkable figure explicitly. A
  figure that shows a mechanism, a timeline, a rig or a task set and is *not*
  in the rewrite is a decision to be able to defend.
- **Appendix figures count.** They are usually the rig, the task set, the
  ablation curves and the error analysis — see R15.
- **"Unlinkable" means one specific thing**: LaTeXML drew the figure as inline
  `<svg>` (a TikZ/PGF picture), so there is no file behind it. A figure
  exported to a standalone `.svg` and embedded with `<object data>` is an
  ordinary file and hotlinks like a PNG. Conflating the two costs a paper its
  own pipeline and schedule diagrams, redrawn by hand for nothing. If a figure
  looks unavailable, check what the extractor actually says before redrawing.
- **Never mirror an image into the repo** — hotlink only, on copyright
  grounds. A relative `url` means someone did, and the build rejects it.
- `loading=lazy` + `no-referrer` are the renderer's job, not yours.
- Caption: translate the original caption to Korean. The origin goes in
  `source`, never in `caption`.
- **A caption is plain text.** It is escaped, not parsed — `**강조**` and
  `` $`math`$ `` inside a caption publish as their own characters. Write Greek
  letters and symbols as themselves (`α`, `s_min`, `H−d`) and carry emphasis in
  the paragraph next to the figure, which *is* markdown. The build reports the
  two most common cases, but not every one.
- **`source` is split on its first comma** — the head becomes the figure-number
  badge that leads the caption (`Figure 3 — …`), the tail becomes the italic
  origin at the end (`(원문 §3.2)`). Write it as `Figure <n>, 원문 §<x.y>` and
  both halves land where they belong; write it as one run with no comma and the
  whole thing prints as the origin with no badge.
- Some figures are inline SVG (TikZ) and have no hotlinkable file —
  `arxiv.py` reports these with an empty `url` / `linkable == False`. Redraw or
  leave the point unillustrated; never link a broken URL. **An algorithm
  listing is one of these**, and transcribing it as a captioned code block
  (R8) beats redrawing it as boxes: it is the paper's own artifact, line
  numbers and all, and it says more per line than a flow diagram can.
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
  shows our labels where the paper had a picture, with nothing saying an
  original existed. Name which figure would have covered the point and why it
  cannot serve (no such figure / inline SVG with no file). If the answer is
  "the paper does illustrate this", the fence is the wrong component — use
  `probe-figure`.

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

  The reading line is the point of the fence — the build rejects an equation
  without one. Do NOT hand-write raw HTML for an equation; the parser runs with
  `html=False`.
  Formulas are set in KaTeX's own faces (KaTeX_Main / KaTeX_Math), vendored
  with the site and checked at build time. If math on a page ever looks like
  the body font, that is a build failure, not something to work around in the
  source.

  `symbols` renders as a three-track grid — 기호 / 이름 / 설명 — with **no
  header row**: a labelled band directly under the formula is chrome in the one
  place the eye should run straight down, and the three columns say what they
  are. `read` renders above the formula against an accent rule.
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

- **The language is mandatory** and prints as the chip on the left of the
  block's header bar.
- **The caption is mandatory too, and the build warns without one.** Everything
  after the first space is the caption. A block of transcribed pseudocode with
  nothing above it makes the reader decode the code to find out why it is on
  the page; one line naming what it shows is what turns it into an exhibit.
  Write it in Korean, as a noun phrase, and say what the block *demonstrates* —
  not what language it is in, which the chip already said.
- Horizontal scrolling is confined to the block; body text never shifts.

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
| `[!CAUTION]` | `co-ten` | 우리와 충돌 | a `D#`/`P#` of ours shakes |
| `[!IMPORTANT]` | `co-ctx` | 논문 밖 맥락 | lineage, background, corpus |

- **`co-ten` is ACT-4 ONLY.** A problem the paper points out about itself is
  `co-warn`. Without this discipline the things that matter *to us* are
  visually buried among the things that merely matter.
- **Author-stated limitations close ACT 3**, as `co-warn`. They must not land
  after Act 4's verification plan — the authors' admission is an INPUT to our
  plan, not a footnote to it.
- **One point per callout, and at most 400 printed characters** — counted on
  what the reader sees, so emphasis markers and TeX macros cost nothing. A
  callout is an aside: the page pulls it out of the flow, sets it on a pale
  wash and expects the eye to take it in one stop. Past that length it is a
  section wearing a border, the paragraph it interrupted is gone by the time
  the reader comes back, and a page whose callouts run 100 characters in one
  place and 500 in the next reads as if the rule changed mid-document. **The
  build reports an over-long body.** A run of author-stated limitations is one
  clause each inside the callout, with the elaboration in a `::: details` under
  it — not one paragraph each inside the band.

### 2-10. R10 — Resource links

The header's resource chips are built from `links:`. What you author is the
`kind|url` pair; what the chip then looks like is the site's business.

- **Six kinds, and only these**: `arxiv` `code` `weights` `data` `site` `demo`.
  An unknown kind is dropped rather than guessed at.
- **ONLY URLs confirmed in the paper body or abstract.** Never guess a
  repository owner, never construct a model-hub path.
- **Unconfirmed → leave the slot empty.** Do not write "없음". A short link row
  is itself reproducibility information.
- The order you write them in does not matter — the chips sort themselves.
- No `P#` pillar chips in the header. No eyebrow tag above the title.

The icon, the English label and the display order are presentation, fixed once
in `LINK_KINDS` (`site/builder/corpus.py`) — that table is the single source
for them, and this guide does not restate it. Adding or renaming a kind is a
code change there plus the kind list above.

### 2-11. R11 — Quizzes

Exactly one per section, three options, one correct.

    ```probe-quiz
    {"q": "<질문>", "options": ["<A>", "<B>", "<C>"], "answer": <0-2>,
     "why": "<왜 정답인지 + 나머지 둘이 왜 틀렸는지>"}
    ```

The explanation must say why the *other* two are wrong; an explanation that
only restates the answer teaches nothing. The build checks one quiz per section
and exactly one correct option.

Options render as full-width buttons and answer on the first click — right and
wrong are both marked, `why` opens, and the question locks. Write the options
so a single pass is enough: three that a reader could plausibly hold, not two
obvious throwaways beside the answer.

### 2-12. R12–R14 — Implementation and authoring traps

- **R12. Visual rules are the site's, not the author's.** Typography, spacing
  and color live in `site/builder/assets/`; the code-highlight themes are
  `LIGHT_STYLE` / `DARK_STYLE` in `site/builder/render.py`. Do not write inline
  styles or `<style>` blocks. Callout backgrounds stay pale; the signal is the
  left border and the label color.

  The page also *adds* chrome your source never mentions, and re-adding it by
  hand duplicates it: the masthead eyebrow (`읽기 쉬운 버전 · 원문에서 직접
  발췌`), the rule that closes the thesis + tagline + summary block, the hairline
  over every `###` section, the act divider's bar, and each component's title
  band. Write the content; the page frames it.

  Two standing rules inside that frame:

  - **Every left-accent card squares off on that edge** — `border-radius: 0
    var(--radius) var(--radius) 0`. The 요약 block, the five callouts, a term
    panel and a quiz all signal with a 3px left border, and rounding it bends
    the accent into a curve so each card reads as a different component.
  - **A 3px left accent band means "aside".** It is reserved for the
    single-column asides — the 요약 block, the five callouts, a term panel, a
    quiz. A card that sits inside a multi-card grid (`probe-split`) is keyed by
    its heading color instead — a band there makes each half read as its own
    callout interrupting the flow rather than as one of two things held side
    by side.
  - **Every component owns its internal spacing, and prose margins stop at
    the article's own flow.** Body-paragraph and list margins apply to the
    article flow plus the two markdown-body containers (a callout body, a
    `::: details` body) and nowhere else. Never reach for a blank paragraph, a
    `&nbsp;` line or a `<br>` to open space around a component — the component
    already sets what it needs, and an inserted spacer is the one thing the
    stylesheet cannot take back.
  - **A `###` section prints no `#` anchor link.** It keeps its `id` — the
    contents, the scroll-spy and the memo anchor all resolve against it — but
    a glyph that appears under the cursor on every heading is a fourth thing
    moving on the page, and it buys a URL the address bar already holds. Do
    not add one back, and do not link sections to each other by `#id` in prose
    where a plain reference reads better.
- **R13. Never `display:block` on an inline tag** (a site-side rule, stated
  here because authors hit it). A rule like `.X b{display:block}` catches body
  emphasis too and breaks the line at every `<b>`. Titles get their own class;
  if you must, use a `>` child combinator.
- **R14. A `**` run cannot close between a closing paren and a Korean
  particle** — see §3-2.

### 2-13. R15 — The appendix is a source, not an annex

In this corpus the appendix is where the paper keeps what a rewrite cannot be
written without. It is not supplementary reading that a thorough author gets to
last; it is the second half of the source, and R3's restoration floor is not
reachable without it.

What lives there, measured on the two papers this rule came from:

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

Working rule:

- **Walk the appendix section list before writing, the way you walk the figure
  list.** `arxiv.py`'s CLI prints it as its own `── 부록 ──` block with a char
  count per section; a section with real content that the rewrite ignores is a
  decision to be able to defend.
- **Cite the section you took it from** — `(부록 D.2)`, `원문 부록 F.4` — in
  prose and in a figure's `source`. It is the only way a reader can go back,
  and it is how a mis-attribution gets caught.
- **`appendix:` in the front matter lists what you drew on.** The build cannot
  check it against the paper, so the key exists to make the sweep a step you
  performed rather than one you meant to.
- Appendix detail is exactly what `::: details` (R3) is for. Collapsing it is
  fine; leaving it out is not.

---

## 3. What Publishes as Literal Text

The failures below are not parse errors. The source is valid Markdown, nothing
warns at author time, and the sentence still reads correctly in the file — the
page just prints the notation instead of rendering it. `build-site.py` reports
every one of them; this section says what to write so it does not have to.

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
preferably, written as a `probe-eq` fence (§2-7), which is the only form that
carries a reading line and symbol table.

**Code span vs. math.** Backticks for literal source tokens (identifiers,
config keys, dtypes, CLI flags), tensor shapes and numeric specs; inline math
for genuine paper notation (Greek letters, variables, sub/superscripts,
operators, set and interval notation). The discriminating signal is a Greek
letter, a LaTeX macro, a math operator or an equation `=` — never `×` / `·` /
`_` alone, which occur in shapes and specs too.

KaTeX renders server-side at build time, so a macro that works in KaTeX works
here. There is no macro whitelist to memorize.

### 3-2. Emphasis that never closes

CommonMark — which this parser implements — closes an emphasis run only where
the delimiter is *right-flanking*, and a `**` sitting between punctuation and a
letter is not. In Korean that is an extremely ordinary sentence shape: a
parenthetical gloss, then a particle.

| Write | Not |
|---|---|
| `**<구A>**(<보충>)과 **<구B>**(<보충>)로` | `**<구A>(<보충>)과 <구B>(<보충>)**로` |

Both markers publish as literal asterisks. The source reads correctly and the
sentence still makes sense on the page, which is why it survives review. Bold
the phrase, not the phrase plus its parenthesis.

### 3-3. A bare URL is not a link

`linkify` is off, so a bare `https://…` in prose renders as plain text — not a
broken link, just not a link. Every URL is explicit `[텍스트](…)` link syntax,
which also keeps the prose readable: a raw URL mid-sentence is noise. Inside a
code span a bare URL is fine and stays literal.

### 3-4. Rules from the sibling track that do NOT apply here

`scouting/` is read as Markdown *on github.com*, and `scouting/AUTHORING.md`
carries rules for that surface. Two of them are dead letters on this track — do
not carry them over, and do not "fix" a rewrite to satisfy them:

- **The single-`~` strikethrough trap.** github.com's GFM treats one tilde as a
  strikethrough delimiter, so two raw tildes in a paragraph strike out
  everything between them there. This parser needs the doubled `~~`, so a
  single `~` renders literally and `4.7~35.6GB` is safe on the page. (An en
  dash still reads better; it is a style preference here, not a render bug.)
- **The bare-URL particle trap.** github.com autolinks a bare URL and swallows
  a trailing Hangul particle into the href. With `linkify` off, nothing is
  autolinked and nothing can be swallowed — §3-3 asks for explicit links for a
  different reason.

---

## 4. The Glance Section (G1–G7)

One screen that answers "what is this paper, and why should I care" before the
reader commits to §1–§3. It is a **second reading of the original**, not a
digest of the body.

### 4-1. G1 — Written from the original, like the body

The glance draws on the same parsed original as the body and cites the same
way. It is never written by re-reading `analysis/<id>.md` and shortening it:

- a digest of a digest inherits every choice the body already made — which
  figure was dropped, which number was rounded — and adds nothing;
- the two surfaces rank the paper's material differently. A figure that sits
  mid-body is often the one the glance leads with;
- a glance derived from the body goes stale the moment the body is edited, and
  nothing on the page says so.

What the two surfaces **do** share, as inputs rather than text: the thesis line
(the body's `#`) and the act order. Nothing is copied sentence for sentence.

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
    {"thesis": "<한 문장 — 논문 제목이 아니라 우리의 테제>",
     "line": "<무엇을 어떻게 바꾸는가 — 한 줄>",
     "figure": "<figure id>",
     "facts": [{"k": "<지표 이름>", "v": "<값 · 단위>"},
               {"k": "<지표 이름>", "v": "<값 · 단위>"}]}
    ```

- `thesis` is the body's `#` — the same sentence, because a page cannot argue
  two theses. It is **not** the paper's title, which the header already prints.
- `facts` — **2 to 4**, and each must be a number the paper itself states. Past
  four they stop being headlines and become a table.
- `figure` is optional and, when present, is the figure a reader would keep if
  they could keep only one. Its id goes in `figures:` like any other (R6).

### 4-4. G4 — The narrative

Flowing Korean prose — a colleague telling you what the paper does, not a
report. The body argues; this talks.

| | |
|---|---|
| Length | **8–10 연**, roughly 900–1,100 printed characters (about 1 분 40 초 읽기) |
| Shape | stanzas of 2–4 sentences, one move per stanza: 무슨 일 → 그 결과 → 이유 |
| Register | 폴라이트-캐주얼 종결 (`~요` / `~ㅂ니다`), 괄호 방백 허용, 감탄은 진짜일 때만 |
| Closing | the last stanza is a **한 줄 토** built from the paper's own stated limits |

Hard constraints:

- **No bullets, no headings, no numbered lists.** A list here is a summary
  wearing prose clothes, and the tab already has cards for that.
- **Every number in it appears elsewhere with a citation** — the rail or an act
  card. The narrative itself carries no source marks; it would break the read.
- **No opinion the paper does not hold.** Relaying is the whole job here; our
  own position lives in the body's act 4 and nowhere on this tab (G7).
- **Not the body's summary paragraph.** `summary:` is 2–3 sentences read cold;
  this is a different artifact at ten times the length and must not restate it
  phrase for phrase.

### 4-5. G5 — `probe-rail`, the conditions beside the prose

    ```probe-rail
    {"items": [{"k": "<항목>", "v": "<값>", "note": "<선택 — 한 줄>"}]}
    ```

**5–7 items.** The rail is the answer to the questions a reader forms while
reading the narrative, so it is keyed by question, not by a fixed schema:

| The question | Typical item |
|---|---|
| 무엇을 읽었나 | the exact version and date |
| 무엇에 적용했나 | the models, backbones or datasets the method was put on |
| 얼마나 | the two or three headline numbers |
| 어떤 조건에서 | rig, hardware, control rate, trial count — whatever the claim depends on |
| 무엇과 비교했나 | baselines and benchmarks |
| 저자는 무엇을 못 한다고 했나 | the author-stated limits, in three or four words |

The last row is not optional padding: without it the tab reads as advocacy.
The rail fills the column the narrative leaves empty, so it is **information,
not decoration** — a rail of restated adjectives is worse than no rail.

### 4-6. G6 — `probe-act`, four cards and no more

    ```probe-act
    {"n": <1–4>, "title": "<주장형 제목 — 이 논문에만 맞는>",
     "claim": "<한 줄>",
     "figure": "<figure id>",
     "eq": "<LaTeX, 구분자 없이>",
     "scale": {"rows": [{"label": "<비교 대상>", "n": <number>, "value": "<표기>"}]},
     "source": "<원문 §<x> · Table <n> · 부록 <X>>"}
    ```

- **Exactly four**, `n` = 1…4, mapping to the body's four acts. The act *names*
  on the card are the ones this paper earns (문제 / 관찰 / 방법 / 증거 is the
  common shape, not a fixed vocabulary), but the count is fixed — a fifth card
  means the tab is becoming the body.
- **Each card carries at least one of `figure` / `eq` / `scale`.** A card of
  three prose lines is the failure this tab exists to avoid.
- `title` follows R2: a claim about *this* paper, never a template heading.
- `source` is required on every card. Every number on this tab is traceable in
  one glance without leaving it.

### 4-7. G7 — What the glance may not contain

- **No `D#`, no `context/` material, no our-view opinion.** Our layer is act 4
  of the body. Mixing it in here puts a claim the paper never made one card
  away from the paper's own numbers. **The build rejects a `D#` on this tab.**
- **No number that is not in the original.** Nothing is computed for effect;
  a ratio the paper does not state is not ours to print.
- **No sentence copied from the body.** Same facts, written again.

---

## 5. The Deck Section (S1–S9)

A deck for presenting the paper to people **outside our team**. It is the one
surface where the audience does not know our context and cannot be told to
read something first.

### 5-1. S1 — Same source, same independence

S1 is G1 for slides: written from the original in the same run, never by
turning the body into bullets. A slide deck derived from a document reliably
becomes that document at 40 % scale, in a font too large for it.

### 5-2. S2 — The audience is outside the team

- **No `D#` and no `context/` citation.** The build rejects both here, for the
  same reason as G7 plus one more: they are unreadable to the audience.
- The closing slide is **적용 범위** — where the method attaches and where it
  does not, the second half taken from the author-stated limits. A deck that
  ends on results ends on advocacy.
- Our own reading of the paper stays on the 상세 tab. If an internal review
  needs it, the answer is to open that tab, not to grow the deck.

### 5-3. S3 — One container, one fence per slide

    ::: deck
    ```probe-slide
    {"kind": "cover|figure|diagram|film|text",
     "chapter": "<문제|관찰|방법|결과|정리>",
     "kicker": "<짧은 라벨>",
     "title": "<한 줄 — 주장. 토픽 이름이 아니다>",
     "source": "<원문 근거 — 그림 번호 · 절 · 표>",
     "note": "<발표자 노트 — 이 장에서 무엇을 말하나>",
     "qa": "<예상 질문 하나와 그 답>"}
    ```
    :::

**11 ± 2 slides.** `note` and `qa` are required on every slide except the
cover; `title` carries a claim, so that reading only the titles is the talk.
`chapter` is required on every slide except the cover, and the five values are
fixed — the page draws a progress row from them.

The deck is **a panel on the paper's page**, presented from the page itself —
full screen, keyboard, presenter notes. There is no export: a second artifact
would be a second thing to keep in step with the original, and the page is
already the thing that is always current.

Per-kind keys:

| `kind` | Extra keys | Use |
|---|---|---|
| `cover` | — | title, authors, id. No chapter |
| `figure` | `figure`: `<figure id>` | the paper's own figure, full bleed, with a one-line claim over it |
| `diagram` | `diagram`: {…} (§5-5), `why` | what the paper states only as a table, an equation or prose |
| `film` | `figure`, `film`: {…} (§5-7) | a filmstrip figure played at its stated frame interval |
| `text` | `body`: `["<줄>"]` or `{"cols": [["<줄>"], ["<줄>"]]}` | contrasts and the closing slide |

Any slide may carry `"steps": <2–4>` (§5-6).

### 5-4. S4 — The paper's own figure first, again

R6 governs here too, with one addition: a figure drawn for **print** often
cannot be read from the back of a room. The test is legibility, not preference.

- Reads at presentation distance → `kind: figure`. Cite it, say one thing over
  it, move on.
- Axis labels or cell text too small, or the point exists only as a table or an
  equation → `kind: diagram`, and `why` states which original figure would have
  covered the point and why it cannot serve (no such figure / inline SVG with
  no file / unreadable at distance). **`why` is required and the build rejects
  a diagram without one** — the same rule and the same reason as `probe-flow`.

### 5-5. S5 — Five drawn diagrams, and five kinds to draw them with

**At most five `kind: diagram` slides per deck. The build rejects a sixth.**
Every drawn diagram is a claim we own and have to verify; five is the point
where a reviewer can still check them all against the original.

Authors supply **data, not drawings**. Hand-written SVG is not accepted (R12 —
visual rules belong to the site), and neither is an image file. The build draws
one of five shapes:

    ```probe-diagram
    {"kind": "bars|timeline|matrix|lanes|slope",
     "title": "<이 그림이 말하는 것>",
     "unit": "<단위>",
     "note": "<축·색이 무엇인지 한 줄>"}
    ```

| `kind` | Shape | Extra keys |
|---|---|---|
| `bars` | ranked values, optionally 기존 vs 이후, against a floor | `rows`: `[{"label", "before", "after"}]` or `[{"label", "n"}]`; `baseline`: `{"label", "n"}`; `lower_better` |
| `timeline` | one axis of time, one row per condition, segments named | `rows`: `[{"label", "segments": [{"name", "len"}], "mark": "<끝점 라벨>"}]`; `grid`: `<눈금 간격>` |
| `matrix` | a grid whose cells carry one of two states — before / after side by side | `panels`: `[{"label", "cells": [[0,1,…]]}]`; `axis`: `{"x", "y"}` |
| `lanes` | two actors and what passes between them | `lanes`: `[{"label", "blocks", "active"}]`; `handoffs`: `[{"at": <n>, "label"}]` |
| `slope` | before → after pairs on a shared scale | `pairs`: `[{"group", "label", "before", "after"}]` |

Rules that hold across all five:

- **Every value comes from the original**, and `source` on the slide names
  where. A diagram is the easiest place to smuggle in a number nobody checked.
- **Do not redraw a figure that already reads.** That is what S4 decides, and
  `why` is where the decision is written down.
- **Colour is the site's** — a diagram declares meaning (`baseline`,
  `lower_better`, which row is the paper's), never a colour.

### 5-6. S6 — Progressive reveal, on comparisons only

`"steps": <n>` splits a slide into `n` reveals, advanced by the same key that
advances slides. **At most four slides in a deck carry it**, and only these
two shapes qualify:

- a **comparison** whose halves are spoken in order (먼저 A, 그다음 B);
- **numbers that accumulate** into a conclusion.

A photograph, a single figure, or a list of parallel items does not qualify —
they are taken in at once, and a reveal there only makes the presenter
remember a click count. The reveal order must match `note`, or the presenter
is reading one script while the screen runs another.

### 5-7. S7 — Motion comes from the original or not at all

A rollout filmstrip printed as one figure can be **played** instead of shown,
which is the strongest thirty seconds a deck gets. It is allowed under three
conditions, all required:

    "film": {"frames": <n>, "interval_ms": <n>, "slow": <2–4>,
             "rows": ["<행 라벨>", "<행 라벨>"]}

1. The figure **is** a filmstrip — evenly spaced frames of one continuous take.
2. The **original states the frame interval**; `interval_ms` copies it. Without
   a stated interval the playback speed would be ours, and a speed we invented
   is a claim about the system's timing.
3. `slow` is 2–4×. Real time is usually too fast to read from a seat, and the
   footer says the true interval and the factor.

Frames are cut **at render time from the hotlinked original**. Nothing is
copied into the repository — R6's hotlink rule is not relaxed by cropping.

**Every asset on this tab comes from the paper's arXiv original.** A project
page, a demo video, a repository README or any other host is not collected,
even when the paper links it: those hosts move, disappear and carry numbers
from an older version of the work, and a deck that half-loads in front of an
audience is worse than one without motion.

### 5-8. S8 — Notes carry the talk, footers carry the conditions

- `note` — what the presenter says here, in one or two sentences. For a
  `steps` slide it names the order of the reveals.
- `qa` — **one** anticipated question and its answer, on every slide. The
  questions that actually come are about measurement conditions and scope;
  writing them down is how the deck stops being a wall.
- A **results** slide states its measurement conditions in `source` — the rate,
  the horizon, how many trials, mean ± sd. "그 숫자는 뭘 기준으로" is the first
  question asked and the cheapest one to pre-empt.

### 5-9. S9 — Chapters, and the shape of a deck

The five chapters are fixed — 문제 · 관찰 · 방법 · 결과 · 정리 — and the page
draws a progress row from them. Slides within a chapter are contiguous; a deck
that revisits 문제 after 결과 is two talks.

A deck that satisfies every rule above and still feels flat is usually missing
one of these, in the order they go missing:

1. **The mechanism that carries the result to the user.** A method slide
   without the deployment path leaves "why does that make it faster / better"
   unanswered.
2. **The cost.** A slide stating what got worse, in the paper's own numbers,
   before the audience asks. Outside the team, this is what buys the rest.
3. **The scope.** Where it attaches and where it does not — S2's closing slide.

---

## 6. Enforcement

Everything is checked by the build, which is the same pipeline that produces
the page — so a rule is enforced against the artifact a reader actually gets.

| Rule | Enforced by |
|---|---|
| Front matter required keys, `analysis_of` == file name, `tagline` not echoing the title (§1), `appendix:` present (R15), `figures:` ↔ the body's `probe-figure` fences (R6) | `site/builder/corpus.py` |
| `###` keyword line (R2), planted-context component (R5), one quiz per section (R11), term anchor ↔ definition pairing (R4), code fence without a caption (R8), unclosed `**` (§3-2), math published as literal text (§3-1) | `site/builder/render.py` |
| `probe-*` fence schemas — term, eq, figure, flow (incl. its required `why`, R6), lineage, scale, split, parts (incl. its all-or-none `state` and the four-state ceiling, R5) | `site/builder/mdext/probefence.py` |
| GFM alert → `co-*` role mapping and the 400-character body ceiling (R9) | `site/builder/mdext/callouts.py` |
| The three accepted math forms (§3-1) | `site/builder/mdext/ghmath.py` |
| The vendored KaTeX stylesheet surviving the woff2 rewrite — without it every formula publishes in the body sans-serif with no KaTeX face loaded | `site/builder/assets_out.py` |

The two short surfaces are checked in the same pass, against the same source
file. Each row is a **hard failure**, not a warning — a glance that leaks our
view or a deck of eleven redrawn diagrams is not something a reader can be
asked to discount:

| Rule | Enforced by |
|---|---|
| The glance spine — hub, narrative, rail, exactly four `probe-act` (G2, G6); narrative length band and its bullet ban (G4); rail item count (G5) | `site/builder/glance.py` |
| A `D#`, a `context/` path, or an act-4 opinion anywhere in `::: glance` or `::: deck` (G7, S2) | `site/builder/glance.py`, `site/builder/deck.py` |
| Slide count band, required `chapter` / `note` / `qa`, the fixed chapter vocabulary and their contiguity (S3, S8, S9) | `site/builder/deck.py` |
| **Five drawn diagrams per deck** (S5), the required `why` on every one (S4), and the `steps` ceiling of four slides (S6) | `site/builder/deck.py` |
| `probe-hub` / `probe-rail` / `probe-act` / `probe-slide` / `probe-diagram` schemas, including the five diagram kinds and their row shapes (§4-3, §4-5, §4-6, §5-3, §5-5) | `site/builder/mdext/probefence.py` |
| Drawing the five diagram kinds from data — the author supplies no geometry and no colour (S5) | `site/builder/diagrams.py` |
| `film` accepted only with a stated `interval_ms` and `slow` in 2–4, frames cut from the hotlinked original (S7) | `site/builder/diagrams.py` |
| `figures:` ↔ every `probe-figure`, `probe-hub`, `probe-act` and `probe-slide` figure id, across all three surfaces (R6) | `site/builder/corpus.py` |

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

`--strict` must exit 0. Everything in §1–§5 that is not in the tables above is
enforced by review, not by code, which is why the prompt's self-check exists.
The rules code cannot see are the ones that decide whether the two short
surfaces are worth having: whether the narrative sounds like a person, whether
a drawn diagram was worth drawing, and whether the deck's titles read as an
argument when you skim them alone.
