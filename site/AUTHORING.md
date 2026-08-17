# Analysis Rewrite Authoring Guide

> **Scope:** every `analysis/<arxiv-id>.md` — the corpus the reading site
> publishes. This file is the single source of truth for that format.
> `.claude/prompts/analyze.txt` owns the *procedure* (which paper, where the
> facts come from, how to verify and commit) and defers to this file for the
> output contract; `site/build-site.py` implements it. Change a rule here
> first, then the build.

**The output is an HTML page.** A rewrite is Markdown only as a source
language: what a reader gets is `site/build-site.py`'s output, rendered by
`markdown-it-py` plus this repo's own extensions. Every rule below is judged
against that page — not against how github.com would render the same file.
Where the two disagree, the page wins, and §3-4 lists the sibling track's rules
that deliberately do **not** apply here.

`docs/style.md` governs `scouting/`, which *is* read as rendered Markdown on
github.com. It does not apply to this track, and this guide does not
cross-reference it — the rules the two tracks share are restated here in the
terms of this renderer.

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
generator: analyze/v2
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
| `figures` | cited figure ids, verbatim from the original as `arxiv.py` reports them. **The build matches this list against the `probe-figure` fences in the body both ways** — an id in one and not the other is reported |
| `appendix` | the appendix sections this rewrite drew on (`[A, B, D.2, G]`), or `none` for a paper without one. Required — see R15. An empty value is not accepted, because "I looked and there was nothing" and "I never looked" are the two cases this key exists to separate |
| `terms` | count of inline term anchors |
| `metric` | **optional.** The one result the paper is remembered by, as a printable fragment — `<지표> <전> → <후> <단위>` for a number the paper moved, `<수치> <단위> · <함께 성립한 조건>` for one it holds under a constraint. The number is already in `summary`, but as prose — the landing list cannot pull it out of a sentence, so it is stated once here and printed as a chip beside the title. Under 40 characters (**longer fails the build**), no verb, no claim the paper does not make. A paper whose contribution is not a single number **omits the key** — an invented headline number is worse than none |
| `generator` | `analyze/v2` |

**Source contract.** Facts come from the paper's arXiv HTML original (parsed
by `site/builder/arxiv.py`); *our view* — `D#` impact, tensions, what we
would check — comes from `context/`. `analysis_legacy/` is neither read nor
written.
No HTML edition (~4% of papers) means **no rewrite is written**: an
abstract-based fallback would be indistinguishable on the page from a real one.

**Stance.** Facts are the paper's. Opinions are ours and must anchor to a `D#`
that exists in the Decision Log — never invent a position `context/` does not
hold. Where our context has no view, relay without one. Subjective judgements
take a hedge (`~인 것 같아요`), not a flat assertion.

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

`scouting/` is read as Markdown *on github.com*, and `docs/style.md` carries
rules for that surface. Two of them are dead letters on this track — do not
carry them over, and do not "fix" a rewrite to satisfy them:

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

## 4. Enforcement

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

One check sits outside the build, because it is about meaning rather than
rendering:

| Rule | Enforced by |
|---|---|
| every `D#` cited exists in the Decision Log | `scripts/check-decision-refs.py` |

A `D#` that does not resolve is not a render failure — it silently loses its
tooltip and prints as plain text, so the build cannot see it as wrong.

Verify before reporting a rewrite done:

```bash
python3 site/build-site.py --only <id> --out /tmp/probe-check --strict
python3 scripts/check-decision-refs.py
```

`--strict` must exit 0. `scripts/check-render-tilde.py` is **not** part of this
track — it enforces github.com's Markdown rendering for `scouting/` and does not
scan `analysis/`. Everything in §1–§3 that is not in the tables above is
enforced by review, not by code, which is why the prompt's self-check exists.
