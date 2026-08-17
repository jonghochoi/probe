# Readable Rewrite Authoring Guide

> **Scope:** every `readable/<arxiv-id>.md` — the corpus the reading site
> publishes. This file is the single source of truth for that format.
> `.claude/prompts/readable.txt` owns the *procedure* (which paper, where the
> facts come from, how to verify and commit) and defers to this file for the
> output contract; `site/build-site.py` implements it. Change a rule here
> first, then the build.

`docs/style.md` governs the `scouting/` and `analysis/` tracks and does **not**
apply here. The two formats share a renderer target (github.com) but nothing
else, so the render traps they have in common are restated in §3 rather than
cross-referenced — this guide is self-contained on purpose.

---

## 1. File and Front Matter Contract

One rewrite per paper, `readable/<arxiv-id>.md`. It deliberately does **not**
live under `analysis/<id>/`: that folder's contract is one artifact per paper
(`analysis.md`), and a folder holding only a rewrite is reported as a metadata
failure by `scripts/refresh-analysis-index.py --check`.

The site takes **all** of its metadata from this front matter — there is no
other source, so a missing field is a hole on the landing page.

```yaml
---
readable_of: 2607.26055        # MUST equal the file name
title: "πR²: Reactive Real-time Flow Policies"
tagline: πR² — 무거운 VLA 백본을 그대로 둔 채 25 Hz 폐루프 힘 반응을 얻는 법
authors: Sungjae Park, Shubham Tulsiani (Carnegie Mellon University)
pillars: P1, P3                # ours — the first decides the card's group
tags: [vla-arch, flow-matching, force]
links: [arxiv|https://arxiv.org/abs/2607.26055, code|https://github.com/…]
published: 2026-07-28          # the paper's date, from arXiv
generated: 2026-08-16          # yours — this sorts the landing page
generator: readable-paper/v2
arxiv_html: 2607.26055v1       # the exact version actually read
arxiv_fetched: 2026-08-16
figures: [S1.F1, S4.F4, S4.F5] # figure ids cited, verbatim from the original
terms: 16                      # count of inline term anchors
summary: >                     # 한 문단 요약 — on the page AND on the card
  …
---
```

| Key | Rule |
|---|---|
| `readable_of` | must equal the file name — **mismatch fails the build**. This catches the copy-paste that lands a rewrite under the wrong id |
| `title` | required. The paper's title, as the card and the page header print it |
| `tagline` | required. **One line naming what the paper does**, printed under the body H1. The H1 is our thesis — often a metaphor — and on its own it does not tell a reader which paper they opened; the header prints the paper's own title. This is the sentence between them |
| `summary` | required. 2–3 sentences, read cold. Printed **on the page** as the `한 문단 요약` block between the thesis line and act 1, and flattened for the landing card. Authored as markdown — `**강조**` and `` $`math`$ `` render on the page and are stripped for the card, so bold the three or four phrases that carry the argument (§3-3 applies) |
| `authors` | one line, as printed |
| `pillars` | **ours**, not the paper's — read `context/P#.md` and pick honestly. First entry decides the card's group; empty → 미분류, which beats a wrong pillar |
| `tags` | flow list, feeds the landing page's filter chips. Free vocabulary; the bar offers the 12 most common facets and search covers the tail |
| `links` | `kind\|url` pairs; kinds fixed at `arxiv` `code` `weights` `data` `site` `demo` (R10). Unknown kinds are dropped rather than guessed at |
| `published` / `generated` | the paper's date / this rewrite's. `generated` sorts the landing page |
| `arxiv_html` / `arxiv_fetched` | the exact version read, and when |
| `figures` | cited figure ids, verbatim from the original (`[S1.F1, S4.F4]`) |
| `terms` | count of inline term anchors |
| `generator` | `readable-paper/v2` |

**Source contract.** Facts come from the paper's arXiv HTML original (parsed
by `site/probe_site/arxiv.py`); *our view* — `D#` impact, tensions, what we
would check — comes from `context/`. `analysis/` is neither read nor written.
No HTML edition (~4% of papers) means **no rewrite is written**: an
abstract-based fallback would be indistinguishable on the page from a real one.

**Stance.** Facts are the paper's. Opinions are ours and must anchor to a `D#`
that exists in the Decision Log — never invent a position `context/` does not
hold. Where our context has no view, relay without one. Subjective judgements
take a hedge (`~인 것 같아요`), not a flat assertion.

---

## 2. Body Rules (R1–R14)

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

```markdown
# 관절은 눈보다 천 배 빠르다                    ← thesis
## 1 무엇이 문제인가                            ← act → divider band
### 청크를 던져놓고 눈을 감는다 | Action Chunking · Open-loop Execution
#### 한 번의 호출에서 벌어지는 일               ← sub-point
```

- **`#` carries the thesis** — the one sentence you would say if you had only
  one. It is NOT the paper's title: the header already prints that from
  `title:`, so repeating it wastes the first line. If the paper has a metaphor
  in it, this is where it goes. Exactly one H1, before act 1. The
  `한 문단 요약` block is printed under it from `summary:` — do not write one
  into the body.
- **`##` is an act**, rendered as a numbered divider band, not a heading. It
  names the question and carries no content. Keep the act number: the table of
  contents groups sections under it.
- **`###` is a section**, rendered as the page's `<h2>`, and **must carry its
  English keyword line in the heading itself**, after a `|`. Written as the
  paragraph below the heading it becomes ordinary body text, never reaches the
  TOC, and reads as a stray sentence — **the build warns**.

      ### 지연이 커질수록 격차가 벌어진다 | Effective Delay · Deployment under VLA Latency

- **`####` is a sub-point** inside a section.
- **Section titles describe *this* paper.** Template titles are banned —
  "왜 이 문제가 생기는가", "우리에게 무슨 의미인가" fit any paper and therefore
  say nothing. Skimming the titles alone must convey the paper's argument.
  Good: "픽셀은 3D를 모른다" · "RGB 는 절대 dropout 하지 않는다" · "990 ms 의 벽"
  · "FFN 하나를 공유했더니 전부 무너졌다".
- **No 원문 절번호 in the title.** Origin stays traceable through figure
  captions (`원문 §4.3`) and `Eq. n` labels.

### 2-3. R3 — Density: high

Roughly 20 lines per section expanded, ~420 lines per paper. Quotes, numbers
and our callouts stay in the body. Only **equation derivations, training
configs, task definitions and appendix detail** are collapsed, with a
container:

    ::: details 학습 하이퍼파라미터
    | 항목 | 값 |
    |---|---|
    | … | … |
    :::

NOT a hand-written `<details>` — the parser runs with `html=False`, so raw HTML
is escaped and published as visible angle brackets. The container body is
ordinary markdown, so tables and math work inside it.

The bar is the **restoration floor**: a reader who never opens the paper must
be able to explain the mechanism, the evidence and the numbers. Naming a
concept and moving on is a failure — "flow denoising 을 둘로 쪼갬" is not
enough; say why there, and what gets faster.

### 2-4. R4 — Background: inline anchors only

Explain a term where it FIRST appears. No document-level primer, no
per-section primer, no global glossary — if the reader has to leave the
sentence, the explanation is in the wrong place.

Authoring syntax is `[용어](term:flow-matching)`, a reserved link scheme
resolved by the renderer, with the definition body in a fence:

    ```probe-term
    {"id": "flow-matching", "title": "Flow Matching",
     "body": "…한 줄 정의 + 왜 여기 쓰이는지…"}
    ```

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

1. **계보** — the line of work this sits in, in time order. If our corpus
   already covered a paper in that line, link it.

       ```probe-lineage
       {"title": "이 문제를 푸는 계보 — 우리가 이미 읽은 논문들",
        "items": [
          {"when": "2025-06", "what": "RTC — Real-Time Execution of …",
           "note": "…무엇이 장점이고 무엇이 남았나…",
           "link": "https://arxiv.org/abs/2506.07339",
           "link_label": "arXiv:2506.07339"},
          {"when": "2026-07", "what": "πR² — 지금 읽는 논문", "current": true,
           "note": "…앞의 것들과 무엇이 다른가…"}]}
       ```

   At most one entry carries `current: true` — the paper being read. That is
   what turns a bibliography into a position. **Do not invent a lineage**:
   check `readable/` for a site link and `context/P#.md` §Tracked Literature
   otherwise, and verify each link resolves before citing it.

2. **숫자의 지형** — the paper's key number placed against the others of its
   kind (human, hardware limit, another paper we read).

       ```probe-scale
       {"title": "25 Hz 는 어디쯤인가 — 제어 주파수의 지형",
        "rows": [{"label": "[PID 제어기](term:pid)", "n": 500, "value": "500+ Hz"},
                 {"label": "πR² 폐루프", "n": 25, "value": "25 Hz", "us": true}]}
       ```

   `n` is the NUMBER (the bar is drawn from it, linearly, against the largest
   row); `value` is how it prints; `us: true` marks this paper's row. Bars are
   linear on purpose — when our row is a stub next to the top of the range, the
   reader should see the stub.

3. **대조** — two or three things held apart, or one object decomposed.

       ```probe-split
       {"cards": [{"title": "느린 채널", "tag": "비동기", "tone": "cold",
                   "body": "…", "note": "거친 공간·과제 안내"},
                  {"title": "빠른 채널", "tag": "매 tick", "tone": "warm",
                   "body": "…", "note": "정밀도가 요구하는 미세 운동 조정"}]}
       ```

       ```probe-parts
       {"rows": [{"label": "front", "range": "$`[0,d)`$", "tone": "settled",
                  "body": "진행 중인 행동. …"},
                 {"label": "interior", "range": "$`[d,H{-}d)`$",
                  "tone": "partial", "body": "…선형 램프…"},
                 {"label": "tail", "range": "$`[H{-}d,H)`$", "tone": "open",
                  "body": "…순수 노이즈…"}]}
       ```

   `probe-split` for a contrast (2–3 cards, `tone`: `cold`/`warm`/`plain`);
   `probe-parts` for one thing cut into named regions (`tone`: `settled` =
   pinned, `partial` = in transition, `open` = free). `probe-split` is also the
   right component for a corpus paper that prescribed something different for
   the same problem.

4. **출처·배경** — where the technique came from, and why it arrives now. A
   `co-ctx` callout and term anchors.
5. **코퍼스 지도** — where this sits among what we have read, plus the question
   nobody has answered yet. Act 4.

### 2-6. R6 — Figures: the paper's own, first

Architecture, pipeline, benchmark and hardware figures are hotlinked from
arXiv:

    ```probe-figure
    {"id": "S1.F1", "url": "https://arxiv.org/html/<id>v<n>/fig/x.png",
     "caption": "…한글 캡션…", "source": "Figure 1, 원문 §1"}
    ```

- **Never mirror an image into the repo** — hotlink only, on copyright
  grounds. A relative `url` means someone did, and the build rejects it.
- `loading=lazy` + `no-referrer` are the renderer's job, not yours.
- Caption: translate the original caption to Korean and append the
  `(Figure N, 원문 §x.y)` origin.
- Some figures are inline SVG (TikZ) and have no hotlinkable raster —
  `arxiv.py` reports these with an empty `url` / `linkable == False`. Redraw or
  leave the point unillustrated; never link a broken URL.
- Where the paper has NO corresponding figure and a sequence still needs
  showing, use `probe-flow` — never ASCII art, never raw HTML:

      ```probe-flow
      {"title": "호출당 1 NFE 방출 사이클",
       "steps": [{"label": "fast 채널 갱신", "note": "매 tick"},
                 {"label": "Euler substep 1회"}]}
      ```

### 2-7. R7 — Math

- Inline math is `` $`X`$ `` — dollar, backtick, TeX, backtick, dollar. A bare
  `$X$` is NOT math here and renders literally: there is deliberately no
  plain-`$` rule, because Korean prose quotes prices and a lone `$` would
  silently open a formula. Full dialect in §3-1.
- A DISPLAY equation goes in a `probe-eq` fence, which carries its reading line
  and symbol table with it. `tex` is raw LaTeX with no delimiters:

      ```probe-eq
      {"read": "다음 상태는 현재 상태에 속도장을 한 스텝 더한 것",
       "tex": "x_{t+1} = x_t + \\Delta t \\cdot v_\\theta(x_t, c)",
       "symbols": [{"sym": "v_\\theta", "name": "속도장", "note": "…"},
                   {"sym": "c", "name": "조건", "note": "…"}]}
      ```

  The reading line is the point of the fence — the build rejects an equation
  without one. Do NOT hand-write `<div class="eqread">` or any other raw HTML;
  the parser runs with `html=False`.
- **Explain DISPLAY equations only.** Inline symbols are handled by term
  anchors (R4).
- **First occurrence only.** A symbol that returns later gets a back reference
  or nothing.

### 2-8. R8 — Code

Pygments language highlighting — the paper's pseudocode, our mapping code,
configs, `impl.patch` diffs. Always tag the fence language. Horizontal
scrolling is confined to the block; body text never shifts.

### 2-9. R9 — Callouts: five roles, mechanically applied

Authored as GFM alerts, so the same source is a recognisable callout on
github.com too:

```markdown
> [!CAUTION] D5 가 흔들린다
> 이 논문의 스케줄은 …
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

- **`co-ten` is ACT-4 ONLY.** A problem the paper points out about itself ("a
  naive linear schedule breaks") is `co-warn`. Without this discipline the
  things that matter *to us* are visually buried among the things that merely
  matter.
- **Author-stated limitations close ACT 3**, as `co-warn` (label e.g.
  "논문이 스스로 긋는 선"). They must not land after Act 4's verification plan —
  the authors' admission is an INPUT to our plan, not a footnote to it.

### 2-10. R10 — Resource links

Header chips, emoji + English label, built from `links:`:
`📄 arXiv` · `💻 GitHub` · `📦 Weights` · `📊 Dataset` · `🌐 Website` ·
`🎬 Demo`.

- ONLY URLs confirmed in the paper body or abstract. Never guess a GitHub org,
  never construct a HuggingFace path.
- Order: arXiv → code → weights → data → site → demo.
- Unconfirmed → **leave the slot empty**. Do not write "없음". A short link row
  is itself reproducibility information.
- No `P#` pillar chips in the header. No eyebrow tag above the title.

### 2-11. R11 — Quizzes

Exactly one per section, three options, one correct.

    ```probe-quiz
    {"q": "…", "options": ["…", "…", "…"], "answer": 1,
     "why": "…왜 정답인지 + 나머지 둘이 왜 틀렸는지…"}
    ```

The explanation must say why the *other* two are wrong; an explanation that
only restates the answer teaches nothing. The build checks one quiz per section
and exactly one correct option.

### 2-12. R12–R14 — Implementation and authoring traps

- **R12. Visual rules are the site's, not the author's.** Typography, spacing
  and code themes live in `site/probe_site/assets/`. Do not write inline styles
  or `<style>` blocks. Callout backgrounds stay pale; the signal is the left
  border and the label color.
- **R13. Never `display:block` on an inline tag** (a site-side rule kept here
  because it keeps recurring). Three separate bugs came from `.X b{display:block}`
  catching body emphasis and breaking the line at every `<b>`. Titles get their
  own class (`<span class="th">`); if you must, use a `>` child combinator.
- **R14. A `**` run cannot close between a closing paren and a Korean
  particle** — see §3-3.

---

## 3. Render Traps

Invisible in the source, wrong on the page. These bite the rewrite track on
both surfaces it is read on — the site and github.com (the page's memo panel
links back to the source file).

### 3-1. Inline math dialect

`` $`X`$ `` — backticks INSIDE the dollars. Forbidden alternatives, all of
which leak raw LaTeX:

| Form | What happens |
|---|---|
| `` `$X$` `` | becomes inline code; KaTeX never runs |
| ``` `$`X`$` ``` | parsed as code-span + literal text + code-span |
| `\(…\)` / `\[…\]` | does not render on GitHub |
| `$X$` | not math here by design; renders literally |

Markdown's italic pass runs before KaTeX and eats the `_` in subscripts unless
the backtick form shields it. An inline `$` must not touch a Hangul/CJK
syllable, a middle dot `·`, or a bold marker — separate with a space, or move
the math outside the bold. A literal `$` in prose is escaped `\$`.

**Code span vs. math**: backticks for literal source tokens (identifiers,
config keys, dtypes, CLI flags), tensor shapes (`` `(B, T, D)` ``) and
numeric specs (`` `224×224` ``, `` `30 fps` ``); inline math for genuine paper
notation (Greek letters, variables, sub/superscripts, operators, set and
interval notation). The discriminating signal is a Greek letter, a LaTeX
`\macro`, a math operator or an equation `=` — never `×` / `·` / `_` alone.

Display math never appears raw in the body: it goes in a `probe-eq` fence
(§2-7). `scripts/check-analysis-math.py` enforces the inline dialect across
`readable/` as well as `analysis/`.

### 3-2. No raw `~` in prose

GitHub's strikethrough extension accepts a **single** tilde, so two raw tildes
in one inline context (a paragraph, a list item, a table cell) silently strike
out everything between them on github.com. Write ranges and approximations
instead:

| Intent | Write | Not |
|---|---|---|
| Numeric / date range | `4.7–35.6GB`, `1–4편` (en dash, U+2013) | `4.7~35.6GB` |
| Approximation | `약 300M`, `약 2×` | `~300M` |
| Paper notation `\sim` | `` $`\sim 50`$ `` | `~50` |
| Open-ended range | `2026-05-11–`, or `2026-05-11 이후` | `2026-05-11~` |

Still correct, never "fixed": inside a code span or fence, inside math where
`~` is the LaTeX non-breaking space, inside an HTML comment, and the doubled
`~~strikethrough~~`. `python3 scripts/check-render-tilde.py` reports the
pairing condition.

### 3-3. Never close `**` between a closing paren and a particle

CommonMark closes an emphasis run only where the delimiter is *right-flanking*,
and a `**` sitting between punctuation and a letter is not. In Korean that is
the most ordinary sentence in the corpus — a parenthetical gloss, then a
particle:

| Write | Not |
|---|---|
| `**느린 채널**(비전·언어)과 **빠른 채널**(고유수용감각)로` | `**느린 채널(비전·언어)과 빠른 채널(고유수용감각)**로` |

Both markers publish as literal asterisks. The source reads correctly and the
sentence still makes sense on the page, which is why it survives review. Bold
the phrase, not the phrase plus its parenthesis. The build reports any `**…**`
that survives into the rendered HTML.

### 3-4. No bare URL in Korean prose

GitHub autolinks a bare `https://…` and does not strip a trailing Hangul
particle, so the particle is swallowed into the href and the link 404s. In
Korean prose a URL is always an explicit `[텍스트](…)` link — the particle then
attaches to the link text or sits outside the brackets. Inside a code span or
an HTML comment a bare URL is fine.

---

## 4. Enforcement

| Rule | Enforced by |
|---|---|
| Front matter required keys, `readable_of` == file name | `site/probe_site/corpus.py` |
| `###` keyword line (R2), planted-context component (R5), one quiz per section (R11), term anchor ↔ definition pairing (R4), stray `**` (R14) | `site/probe_site/render.py` |
| `probe-*` fence schemas — term, eq, figure, flow, lineage, scale, split, parts | `site/probe_site/mdext/probefence.py` |
| GFM alert → `co-*` role mapping (R9) | `site/probe_site/mdext/callouts.py` |
| Inline math dialect (§3-1) | `site/probe_site/mdext/ghmath.py` on the page, `scripts/check-analysis-math.py` in CI |
| `~` strikethrough pairing (§3-2) | `scripts/check-render-tilde.py` |
| `D#` citations resolve to a real Decision | `scripts/check-decision-refs.py` |

Verify before reporting a rewrite done:

```bash
python3 site/build-site.py --only <id> --out /tmp/probe-check --strict
python3 scripts/check-analysis-math.py
python3 scripts/check-render-tilde.py
python3 scripts/check-decision-refs.py
```

`--strict` must exit 0. Everything in §1–§3 that is not in the table above is
enforced by review, not by code — which is why the prompt's self-check list
exists.
