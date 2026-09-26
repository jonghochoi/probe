# Scouting Report Authoring Guide
> **Scope:** every `scouting/P#/YYYY-MM-DD.md` — the dated reports the
> scheduled routine writes — plus the skeleton in `scouting/templates/`.
> This document is the single source of truth for that format.
> `.claude/prompts/scouting.txt` owns the *procedure* (retrieval, evidence,
> commit) and defers to this file for the output contract, the rubric
> included. Change a rule here first, then the prompt.
>
> The reading site is a separate track with its own contract: `analysis/<id>.md`
> is governed by `analysis/AUTHORING.md`, not by this guide. Nothing here applies to it.

---

## 1. Output File Convention

Each run of the routine writes **one Korean file** for one pillar. The
cadence is the routine's schedule, set in `scouting/SETUP.md`.

| File | Language | Purpose |
|------|----------|---------|
| `scouting/P#/YYYY-MM-DD.md` | Korean | The scouting report. `P#` is the pillar (P0–P4); `YYYY-MM-DD` is the run date. |

There is no separate English file. Paper titles, arXiv links, and `P#/D#`
tags stay verbatim (§4-1), so de-duplication across previous reports works on
those tokens regardless of prose language.

---

## 2. Emoji System and Section Headers

Every `##` header opens with one emoji from §2-1; §2-3 holds the rules.

### 2-1. Scouting report `##` sections

The table fixes the emoji, the exact Korean header text and the canonical
**section order** (top to bottom). The decision content — papers, scores,
context suggestions — stays up top; the 🚫 appendix sits last.

| Emoji | `##` header (verbatim) | Holds | Rules |
|-------|------------------------|-------|-------|
| 🔑 | `## 🔑 참조 약어 풀이` | Reference Legend — the `P#` / `D#` codes this report cites | §3-1 |
| 🥇 🥈 🥉 | `## 🥇 논문 N — 우선순위 ★★★` | The top three surfaced papers, one medal each and each medal at most once. The medal is the paper's rank (§5-3); the stars are its priority after the ceiling, so a capped top paper reads `## 🥇 논문 1 — 우선순위 ★★` | §3, §5-1, §5-3 |
| 🌱 | `## 🌱 논문 N — 인접 분야 픽` | The cross-pollination pick — an adjacent-field paper, scored on the same rubric and carrying the same label | §5 |
| 📋 | `## 📋 기준 통과 · 추가 후보` | Every further surfaced paper, ranked below 🥉 — one table row each | §5-1 |
| 📊 | `## 📊 점수 요약` | Scoring Summary — the rubric rationale for each paper with a section of its own | §5-1, §5-2 |
| 🔍 | `## 🔍 근접 후보` | Near-Miss Candidates — this run's papers one gate axis short | §5-4 |
| 💡 | `## 💡 컨텍스트 제안` | Context Suggestions — proposed edits to `context/P#.md` | §7-1 |
| 🔄 | `## 🔄 직전 리포트 대비 종합` | Run-over-Run Synthesis — this run against the recent reports | §7-2 |
| 🚫 | `## 🚫 필터 통과 실패 후보 논문` | Candidate Papers That Did Not Pass Filter — each with its reason | §4-5, §7-3 |

### 2-2. Subsection (`###`) headers

Every paper section (🥇 🥈 🥉 🌱) carries the same four subsections, read as one
story — tie → contribution → what it means for us → what to check:

| `###` header (verbatim) | Holds |
|-------------------------|-------|
| `### (a) 관련 Pillar / Decision` | The badge line only (§3-1) |
| `### (b) 핵심 기여` | What the paper is and does, and what is genuinely new against the field |
| `### (c) 시사점` | What it could mean for us, in plain terms (`공개 기준점 확보`, `도입 비용 낮음`) |
| `### (d) 먼저 확인할 점` | The paper's own limits and the cheapest transfer caveat |

💡 carries three:

| `###` header (verbatim) | Holds |
|-------------------------|-------|
| `### Tracked literature` | Replace, add or remove a pin within the pillar's cap (`context/P#.md` §3-2), with its arXiv link |
| `### Decision Log` | Trigger a deferred alternative, revise a default, or propose a new decision — naming the evidence this run moved |
| `### Anti-topics` | A candidate exclusion rule this run's filter surfaced |

### 2-3. Rules

- One emoji per `##` header, at the start, after `## ` and a space.
- No emoji on `#`, on `###` or deeper, on table headers, in table cells, in
  code blocks, or in body text.
- Do not use an emoji not listed in §2-1.
- Emojis are not translated — use the symbols exactly as listed.

#### Correct example
```markdown
## 🥇 논문 1 — 우선순위 ★★★
### (a) 관련 Pillar / Decision
### (b) 핵심 기여
```

#### Incorrect example
```markdown
## 논문 1 — 우선순위 ★★★ 🥇               ← emoji at end, wrong
### 🎯 (a) 관련 Pillar / Decision         ← emoji on H3, wrong (## only)
The policy achieved ✨ great results.     ← emoji in body text, wrong
```

---

## 3. Link Format Rule

Every paper entry must include a direct link. Precedence:

1. arXiv preprint → `[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX)`
2. DOI / proceedings → `[DOI](https://doi.org/...)`
3. Neither available → `[no public link]`

Links must appear:
- In the paper header (immediately below the bold title)
- In the further-surfaced (📋) and Near-Miss Candidates (🔍) tables (`Link` column)
- In the Candidate Papers table (`Link` column)
- Inline in Context Suggestions when an arXiv ID is mentioned

The 📊 section carries no table and therefore no `Link` column (§5-1) — a
paper scored there already has its link in its own header.

Do not fabricate arXiv IDs. Verify that the URL resolves before including it.

### 3-1. Reference Legend & cross-reference links

The report opens with a **Reference Legend** — a one-line glossary of the
`P#` / `D#` codes, so a reader who does not have the codes memorized can
decode the report without opening `context/P#.md`.

**Scope.** Only `P#` (Pillar) and `D#` (Decision) codes.
**Only codes actually cited in this report.** Never list a code the body
does not use; never list competitor codenames, Identity, or the falsifier.

**Placement.** A single `## 🔑 참조 약어 풀이` section, immediately after the
top metadata block and before the first paper section — the report goes
metadata → legend, with no boilerplate intro between them.

**Format.** One compact table, the pillar row first and the decision rows in
order of first appearance in the body — a `D#` id is opaque and carries no
sort order. One row per distinct cited code. Each code renders as a **shields.io
badge**, color-coded by category:

| Category | Color | Source |
|----------|-------|--------|
| `P0` | `f5d5d5` (pale red) | pillar palette — this table is the palette's source of truth |
| `P1` | `f5e9d5` (pale orange) | pillar palette |
| `P2` | `e2f5d5` (pale green) | pillar palette |
| `P3` | `d5def5` (pale blue) | pillar palette |
| `P4` | `e0d5f5` (pale purple) | pillar palette |
| every `D#` | `d97706` (amber) | single shared decision color |

Badge URL: `https://img.shields.io/badge/<CODE>-<hex>.svg` (label-only, no
message). All `D#` share one color (they are codes, not a ranked palette);
`P#` follows the per-pillar palette so one pillar always reads as one color
across reports. A scouting report is single-pillar, so in practice one pillar
color plus amber decisions appear.

```markdown
## 🔑 참조 약어 풀이

| Code | Meaning |
|------|---------|
| <a id="ref-P2"></a>![P2](https://img.shields.io/badge/P2-e2f5d5.svg) | Structured Multimodal Observation Fusion (pillar) |
| <a id="ref-D9ZP"></a>![D9ZP](https://img.shields.io/badge/D9ZP-d97706.svg) | Body↔Hand information sharing — FiLM, cross-attn/hidden-state deferred |
```

If the body cites no such code (rare), omit the section entirely.

**Meaning source** (deterministic — derive from `context/P#.md`,
which the agent already reads; do not invent). The meaning is a **decode
gloss**, so keep it clean: **English only** (the codes and their definitions
are English; no Korean in this column) and **no `;` semicolon chains** —
use commas, ≤~12 words:

| Code | Source in `context/P#.md` | Meaning string |
|------|-----------------------------------|----------------|
| `P#` | the pillar file's H1, `P# — <name>` | `<name>` + `(pillar)` |
| `D#` | the Decision Log's `#### [D#] <title>` + its current default | `<title>` — concise gloss, ≤~12 words, commas not semicolons |

**Anchor convention.** Each legend row carries an explicit HTML anchor
`<a id="ref-<CODE>"></a>` placed before the code badge (the legend badge
itself is not a link). `<CODE>` is the verbatim code (`P1`, `D9ZP` — case
preserved; GitHub matches explicit `id=` attributes verbatim).

**In-body links (first occurrence per section).** Within each top-level
`##` section (each Paper N and the other sections), the **first** textual
occurrence of each distinct code is written as a **linked badge**
`[![D9ZP](https://img.shields.io/badge/D9ZP-d97706.svg)](#ref-D9ZP)` (same
palette as the legend). Later occurrences of that same code **in the same
section** stay plain text.
Each new `##` section links the first occurrence again, so any section is
self-contained for jump-back. Codes inside table cells and code blocks are
not linked. The legend rows themselves are not self-linked.

**No inline gloss next to a body badge.** The decision-tie line (each
paper's (a) section) is badges only — `[![P2](…)](#ref-P2) /
[![D3AG](…)](#ref-D3AG) [![D8EJ](…)](#ref-D8EJ)` — never a badge followed by a
parenthetical Korean description. The badge alone names the tie; its
meaning is in the legend and the paper-specific angle is in the (b)–(d)
개조식 bullets below. Separate the pillar badge from the decision badges
with ` / `, and decision badges from each other with a **single space**.

**Paper sections stay paper-focused.** (a) is the badge line only — no body
bullets; the substance starts in (b) (§2-2). In (b)–(d), **do not plaster
internal decision bookkeeping**: avoid `D#` codes, `deferred`, config-key /
`*.yaml` names in the prose. A reader should be able to follow the paper
without stopping to ask "what is D3AG? what is deferred?". The decision link
is carried by the (a) badges; concrete context-edit proposals (which `D#` to
move, which deferred candidate to trigger) belong in 💡, the section built
for them.

---

## 4. Korean Authoring Principles

The report is written directly in Korean. There is no English source
file to translate from — but the same rules apply for which tokens stay
verbatim in their original form versus which prose is Korean.

### 4-1. What to write in Korean vs. keep verbatim

| Category | Treatment |
|----------|-----------|
| Body prose | Korean **개조식** (명사형 종결) — register governed by §4-4 |
| Paper titles | Keep original English title; add Korean description if helpful |
| Technical terms | First occurrence: Korean term + English in parentheses. Subsequent: Korean only |
| Config / code names | Keep verbatim (`env_cfg.py`, `ObservationManager`, etc.) |
| Formulas / numbers | Keep verbatim (`ε = 0.1`, `±2σ`, `< 15%`, etc.) |
| P#, D# tags | Keep verbatim (`P2`, `D3AG`, etc.). |
| Reference Legend | Meaning column in **English** (mirrors the English code definitions — no Korean); codes + `<a id="ref-…">` anchors verbatim |
| Anchor / intra-doc links | Keep `id=` and `[…](#ref-…)` verbatim — links resolve within the file |
| arXiv links | Keep verbatim |
| Section headers | Verbatim from §2-1 and §2-2 (§4-3) |

### 4-2. Technical term glossary (standard translations)

| English | Korean |
|---------|--------|
| Sim-to-Real (Sim2Real) | Sim2Real (시뮬레이션-실환경 이전) |
| Domain Randomization (DR) | 도메인 랜덤화 (DR) |
| Reinforcement Learning (RL) | 강화학습 (RL) |
| Imitation Learning (IL) | 모방 학습 (IL) |
| Privileged teacher / student | 특권 교사 / 학생 |
| Contact-rich | 접촉 집약적 |
| In-hand manipulation | 인핸드 조작 |
| Dexterous manipulation | 다지 조작 / 손재주 조작 |
| Forward kinematics (FK) | 순방향 기구학 (FK) |
| Compliance controller | 컴플라이언스 컨트롤러 |
| Tactile sensing | 촉각 감지 |
| Visuotactile | 비주오택타일 |
| Deform Map | Deform Map (변형 맵) |
| Latent space | 잠재 공간 |
| Mixture of Experts (MoE) | 전문가 혼합 (MoE) |
| Skill basis | 스킬 기저 |
| Sticky routing | 스티키 라우팅 |
| Cross-pollination | 크로스폴리네이션 |
| Pinned paper | 핀 논문 |
| Anti-topic | Anti-topic (배제 주제) |
| Real-robot evidence | 실제 로봇 검증 |
| Failure mode | 실패 모드 |
| Decision implication | 의사결정 함의 |
| Citation-graph expansion | Citation-Graph 확장 |
| Keyword Sweep | Keyword Sweep (키워드 스윕) |
| System0 / System1 | System0 / System1 (저수준 안정화 / 고수준 정책 계층) |
| Structured input-modality binding | 구조적 입력-모달리티 결합 |
| VLM pretraining preservation | VLM 사전학습 보존 |
| Action expert | 액션 전문가 |
| Flow matching | 플로우 매칭 |

### 4-3. Section headers are fixed strings

Every `##` and `###` header is copied verbatim from §2-1 and §2-2. It is not
translated back to English, reworded, or extended — no `(월 1회)` on 🌱, no
paper name in a `###`. The English names the tables give are for this guide's
prose only.

### 4-4. Register — 개조식 (outline form, 명사형 종결)

The **scouting report** (`scouting/`) is **개조식**: a scanned decision
document, not flowing prose. Its body content is written as terse outline
bullets, not 합니다/됩니다 paragraphs. (The reading-site rewrites under
`analysis/` keep an explanatory 합니다/됩니다 register — `analysis/AUTHORING.md` —
since they are read, not scanned; only the scouting report is 개조식.)

- **명사형 종결.** End body items on a noun or nominalized form
  (`~함 / ~음 / ~필요 / 명사`), not a full polite sentence. `D3AG 인코더 학습
  기준 데이터` / `검증 필요` — not `…데이터입니다` / `…검증해야 합니다`.
- **Labelled bullets.** Each item is a bold label + a terse phrase
  (`- **판단 근거** — …`); nest sub-bullets for hierarchy. A section is a
  short bullet list, not one or more paragraphs.
- **One claim per bullet.** No `— …하기 위해` trailing-purpose tails; no
  hedging padding (`~할 수 있을 것으로 보입니다`). Speculation stays speculative
  in nominal form (`저하 우려` / `불필요 가능`), assertions stay assertive
  (단정↔추측 preserved).
- **No semicolon chains in body.** A `;` joining two or three clauses reads as
  an unstructured run-on. When a bullet carries multiple clauses, use a comma,
  or — if they are genuinely parallel items — split into nested sub-bullets
  (e.g. the 🔄 Decision-Log signal becomes one sub-bullet per D#).
- **Where it applies.** All body content — paper (a)–(d), 📊 score rationale,
  💡 context suggestions, 🔄 synthesis. Exempt: table cells (a `;` may separate
  distinct entries there) and verbatim English citation blockquotes.

Two surface conventions (markdown, not register):

- Use bold (`**text**`) for the bullet label and for emphasis — and never
  close it between a paren and a particle (§4-8).
- Code blocks and inline code (`` `text` ``) are kept verbatim.

**Meaning is never altered for style.** Restructuring prose into 개조식, a
table or bullets (§4-5) must not add, drop, or reorder any fact, number, date,
quotation, citation polarity, causal direction, or `P#`/`D#` / arXiv / formula
token.

### 4-5. Scannability — repetitive structure goes in a table

A decision-grade report is *scanned* by a reader hunting for the one row
that matters, not read prose-first end to end. §4-4 governs the register
inside a bullet; this rule governs the *layout above the sentence*.

- **Repetitive records become a table, never a run-on sentence.** Wherever
  the report enumerates the same shape N times — dropped paper → reason
  (🚫), or any researcher/paper roster — render it as a table (or a clean
  bullet list), not a comma/`·`/`—`-chained paragraph. Target: one
  eye-saccade per record. (Markdown needs a blank line both before and after
  a table, including when a `-` bullet follows.)
- **Lists inside a table cell — use `<br>` + `•`, never `*`/`-`.** A GFM
  table cell cannot hold a real list (`<ul>`) or a literal newline — a
  newline ends the row, and a leading `*`/`-` renders as text, not a bullet.
  To stack several items in one cell, join them with `<br>` and a literal
  bullet glyph: `• a<br>• b<br>• c`.
- **Conclusion before enumeration.** When a long list resolves to one
  verdict ("10편 전원 재등장·제외"), state the verdict first, then the list —
  the reader must not parse every item to reach the point.
- **Machine identifiers stay out of prose.** Semantic Scholar author ids,
  and any arXiv id already carried by an adjacent `Link` column or table
  cell, do not belong inline in Korean sentences. Put them in a dedicated
  cell; never repeat an id a sibling cell already shows (e.g. the 🚫
  `Paper` column drops the id its `Link` column already carries).
- **No enumeration markers in body.** 개조식 uses bullets (§4-4); do not fall
  back to `①②` / `1. 2.` / `첫째·둘째` running inside a sentence.

### 4-6. No raw `~` in prose — it is a strikethrough delimiter on GitHub

GitHub's strikethrough extension accepts a **single** tilde, not just the
doubled `~~`. A raw `~` in body text therefore opens a strikethrough run, and
the next raw `~` **in the same inline context** closes it — silently striking
out every character in between on the rendered page. The failure is invisible
in the source and invisible in most local previews (CommonMark requires `~~`);
it appears only on github.com, which is where these documents are read.

The pairing scope is one *inline context*, not one line: a paragraph, a single
list item, one table cell, or one blockquote line. Two tildes on different
lines of the same paragraph still pair; two tildes in different table cells do
not.

**Write ranges and approximations like this instead:**

| Intent | Write | Not |
|---|---|---|
| Numeric / date range | `4.7–35.6GB`, `2026-06-01–06-19`, `1–4편` (en dash `–`, U+2013) | `4.7~35.6GB` |
| Approximation | `약 300M`, `약 2×`, `약 110K frame` | `~300M` |
| Paper notation `\sim` | `` $`\sim 50`$ `` (inline math) | `~50` |
| Open-ended range | `2026-05-11–`, or spell it (`2026-05-11 이후`) | `2026-05-11~` |

**Where a raw `~` is still correct** — these are parsed before the
strikethrough scan (or not rendered at all), so they never pair and must not
be "fixed":

- inside a fenced code block or an inline code span (`` `d ~ Uniform{1,…,d_max}` ``);
- inside display math `$$…$$` or a ```` ```math ```` fence, where `~` is the
  LaTeX non-breaking space and changing it alters the formula;
- inside an HTML comment (`<!-- … -->`), which does not render;
- a deliberate `~~strikethrough~~`, which is the doubled form.

**English verbatim blockquotes are exempt and are never edited** — the quoted
sentence is a byte-locked token (§4-1). If a quoted sentence genuinely contains
a raw `~`, leave it and keep the Korean explanation line tilde-free so nothing
pairs with it.

Two or more raw tildes in one inline context is the condition that actually
breaks a render. A lone tilde renders literally and is not an error, but it
becomes one the moment another lands in the same context, so prefer the table
above everywhere.

### 4-7. No bare URL in Korean prose — the following particle joins the href

GitHub autolinks a bare `https://…` in body text. When it decides where the
URL ends it strips *trailing punctuation* (`.` `,` `)` `?` …) but **not
Hangul**, which it reads as an ordinary URL character. A Korean particle
written straight after the URL is therefore swallowed into the link target,
and the rendered link 404s while the source looks correct:

| | Write | Not |
|---|---|---|
| URL with a following particle | `[프로젝트 페이지](https://example.org/x/) 하나뿐이며` | `프로젝트 페이지(https://example.org/x/)만` |
| URL as the sentence subject | `[공식 저장소](https://example.org/r)에서 받습니다` | `https://example.org/r 에서 받습니다` |

The rule is simple: **in Korean prose a URL is always an explicit
`[텍스트](…)` link, never bare.** The particle then attaches to the link
text or sits outside the brackets, and no Hangul can reach the href. This
also keeps the prose readable — a raw URL mid-sentence is noise.

**Where a bare URL is still correct** — these are not autolinked (or not
rendered at all), so nothing can be glued to them:

- inside a code span or fenced code block (a `curl` command, a config value);
- inside an HTML comment (`<!-- … -->`), e.g. a retrieval-failure record;
- inside an English verbatim blockquote, which is byte-locked (§4-1) — leave
  it and keep the Korean explanation line free of an adjacent bare URL.

### 4-8. Never close `**` between a closing paren and a particle

CommonMark closes an emphasis run only where the delimiter is *right-flanking*,
and a `**` sitting between a punctuation mark and a letter is not. In English
that shape is rare. In Korean it is the most ordinary sentence in the corpus —
a parenthetical gloss, then a particle:

```
**느린 채널(비전·언어)과 빠른 채널(고유수용감각)**로 쪼개    ← publishes ** literally
```

The run never closes, so both markers are printed as asterisks. Nothing errors,
the source reads correctly, and the sentence still makes sense on the page —
which is exactly why it survives review. It is the same class of failure as the
tilde in §4-6: legible in the source, wrong in the render.

| Write | Not |
|---|---|
| `**느린 채널**(비전·언어)과 **빠른 채널**(고유수용감각)로` | `**느린 채널(비전·언어)과 빠른 채널(고유수용감각)**로` |
| `**계단 스케줄**로` (letter before the marker — closes fine) | — |

The rule in one line: **the character immediately before a closing `**` must
not be punctuation** when a letter follows it. Bold the phrase, not the phrase
plus its parenthesis. This track has no build step to catch it, so the rule
is the only defense — nothing errors and review is what has to notice.

---

## 5. Scoring Contract

The rubric is **five fixed dimensions, 0–3 each, total /15**. A report never
adds, drops, or renames one, and always shows all five for every paper it
scores. This section owns the dimensions, the gate, the ceiling and the rank
order; the prompt owns how the evidence is fetched.

| Dimension | What it scores |
|---|---|
| Relevance | Which `P#` / `D#` the paper touches, and how directly |
| Novelty | Genuinely new, or a delta over tracked work |
| Reproducibility | Whether the artifact is obtainable — scored only from quoted evidence (§5-2) |
| Methodology | Experimental rigor — baselines, ablations, eval soundness, seeds / variance. 0 anecdotal · 1 weak · 2 solid · 3 strong and honest about limits. A high-novelty paper without it is a lead, not a result |
| Sim2Real | Real-robot evidence, or sim-only |

### 5-1. The surfacing gate is four dimensions

A paper is surfaced as a `## 🥇 / 🥈 / 🥉 / 🌱` section when **Relevance, Novelty,
Methodology and Sim2Real are each ≥ 2**. Reproducibility is scored, shown, and
used for ranking (§5-3), but it is **not** part of the gate.

A fresh preprint almost never has a public repository on the day it posts, so a
Reproducibility term inside an AND-gate does not measure research quality — it
measures how long the paper has been up, and it stalls a run into surfacing
nothing while the same paper's Relevance and Methodology are the strongest of
the week. Reproducibility governs how far a paper may be promoted, not whether
the reader gets to see it.

**The gate binds in both directions.** A candidate whose four gate dimensions
are each ≥ 2 is surfaced as a `## 🥇 / 🥈 / 🥉 / 🌱` section — there is no third
outcome. Parking such a paper in `## 🔍` or `## 🚫` because its repository is
still closed puts Reproducibility back inside the gate through the appendix
tables, and the report then buries the week's strongest paper in a row whose
재검토 조건 reads `코드 공개 시 승격`. A closed artifact caps the paper's
priority at ★★ (§5-3); it never removes the paper from the report.

**The gate decides whether a paper surfaces; its rank decides the shape.**
The top three by rank (§5-3) take the full `## 🥇 / 🥈 / 🥉` sections, one
medal each. Every further paper that clears the gate is still surfaced — as one
row of `## 📋 기준 통과 · 추가 후보`, in rank order — so a strong week stays a
report a reader can scan rather than a stack of full sections. The 🌱 pick
keeps its own section (§5) and is not one of the three.

```markdown
| Paper | Link | R·N·M·S2R | Repro | 합계 | 코드 | 한 줄 근거 |
|---|---|---|---|---|---|---|
| LIRA | [arXiv:2608.07596](https://arxiv.org/abs/2608.07596) | 3·2·2·2 | 1 | 10/15 | 코드 공개 예정 | <한 줄> |
```

Omit 📋 when three or fewer papers clear the gate. The metadata field
`**Papers surfaced (4축 게이트 통과):**` (§6) counts the paper sections and the
📋 rows together. When fewer than 3 papers clear the gate, say so and do not
pad — a paper carried by two strong axes and a zero does not surface.

The `## 📊` section carries the rationale for exactly the papers with a
section of their own and **no table**: one bold head per paper carrying its
total (`**HapTile (13/15)**`), then one 개조식 bullet per dimension
(`- Relevance 3 — <근거>`), summing to that total. A 📋 row carries its own
scores and gets no head, and neither does a paper the report did not surface.

### 5-2. Reproducibility is scored from quoted evidence, never inferred

The evidence is a **string the retrieval pass actually received** — the arXiv
`<arxiv:comment>` field, or the abstract body. Both come back in the same API
response the run already makes, so this costs no extra call.

| Score | Condition |
|---|---|
| 3 | Repository URL present **and** data / checkpoints **and** hardware or config detail |
| 2 | A code repository URL is stated (`github.com/…`, `Code: …`) |
| 1 | Project page only, or a promise (`code will be released`, `release soon`, `upon acceptance`) |
| 0 | No repository, page, or release statement anywhere in the abstract or the comment field |

**Evaluation on a public benchmark is not reproducibility evidence.** LIBERO,
CALVIN, SIMPLER, DexYCB and their siblings say the *paper* is comparable, not
that the *artifact* is obtainable. A rationale bullet reading
`Reproducibility 2 — 공개 벤치마크 4종 검증` is wrong at the rubric level, and a
bullet that scores ≥ 2 while its own text says `코드 공개 미확인` contradicts
itself. Neither is publishable.

Each 📊 rationale bullet **quotes the evidence it scored on**:

```markdown
- Reproducibility 2 — arXiv comment "Code: https://github.com/LeapWM/leapbot-wa"
- Reproducibility 1 — arXiv comment "Code and model checkpoints will be released upon acceptance"
- Reproducibility 0 — 초록·arXiv comment 모두 코드·프로젝트 페이지 신호 없음
```

An absent signal is stated as absent. `초록상 미확인` / `공개 여부 확인 필요`
is not an outcome — the comment field either carries a URL or it does not, and
the run has already read it.

### 5-3. The Reproducibility label and the priority ceiling

Every paper header carries the label its Reproducibility score implies, as
plain text (emoji stay on `##` headers — §2):

| Score | Label | Priority ceiling |
|---|---|---|
| 2–3 | `코드 공개` | ★★★ |
| 1 | `코드 공개 예정` | ★★ |
| 0 | `코드 미공개` | ★★ |

A paper the team cannot run yet is still worth reading, but it does not
outrank one they can — so `★★★` is reserved for a paper with an obtainable
artifact. Rank within a ceiling by Relevance, then by the /15 total, then by
venue tier — this order assigns the medals and orders the 📋 rows (§5-1).
Venue tier comes from the Venue Priority table `context/MASTER.md` §5 owns (the prompt
carries a copy), read from the arXiv comment field and recorded on the paper header line. Venue
breaks ties only; it never gates and never overrides the rubric.

### 5-4. Near-miss candidates

`## 🔍 근접 후보` holds this run's candidates that are **exactly one gate axis
short** — one of the four gate dimensions scores 1 and the rest are ≥ 2. Two
or more axes short is a 🚫 row; zero axes short is a surfaced paper (§5-1),
never a 🔍 row.

The table is this run's alone. A row is not carried into the next report and
is not re-checked there; like every id a report names, the paper is then held
out of later runs by the routine's de-duplication window. `재검토 조건` names,
for the reader, what would lift the short axis.

One table, no per-paper `###` subsections:

```markdown
| Paper | Link | R·N·M·S2R | 코드 | 재검토 조건 |
|---|---|---|---|---|
| LIRA | [arXiv:2608.07596](https://arxiv.org/abs/2608.07596) | 2·2·2·1 | 공개 예정 | 실로봇 결과가 나오면 Sim2Real 충족 |
```

Omit the section when it has no rows. A paper appears in 🔍 or in 🚫, never
both — 🚫 is for candidates that are out, 🔍 for the ones a single axis kept out.

---

## 6. Report Metadata Block

The block between the H1 and the first `---` is exactly two lines:

```markdown
# Probe 스카우트 리포트 — YYYY-MM-DD · Pillar P#

**Papers scanned:** <one-line summary, ≤ 400 characters>
**Papers surfaced (4축 게이트 통과):** <integer>
```

- **No `Run date:` line.** The filename, the H1 and that field carry the same
  date three times; the H1 is the one a reader sees.
- **No `Agent version:` line.** A constant across every report is not
  information — the report's provenance is its commit.
- **`Papers surfaced` is an integer and nothing else**, and it equals the
  number of `## 🥇 / 🥈 / 🥉 / 🌱` sections plus the `## 📋` rows (§5-1). Prose about *why* the
  count is low belongs in 📊; the field is the count.
- **`Papers scanned` is capped at 400 characters** and names, at most: the
  source passes run, an order-of-magnitude count per pass, and any failure
  still unresolved when the run ended. It is a provenance line, not an audit
  trail — a reader checks that the sweep ran, then moves on. It is also the
  report's only provenance: no section restates the retrieval (§7-2).

What the line does **not** carry: per-query breakdowns, stage-by-stage funnel
arithmetic (`661건 → 507편 → 226편 → 190편 → 19편`), per-pin request counts,
or retry narration. A retry that succeeded is a non-event; only a call still
failing at the end of the run is disclosed, verbatim, as `… 최종 실패`. The
line names no retry or backoff at all unless that clause is there.

```markdown
**Papers scanned:** citation-graph 8핀 280편 + keyword sweep 110편(14일 44편)
— keyword sweep 1개 쿼리 HTTP 429 최종 실패
```

---

## 7. Section Discipline

§4-4 governs the register inside a bullet and §4-5 the layout above it. This
section governs what each `##` section is allowed to repeat.

### 7-1. Context Suggestions — a proposal is made once

In `## 💡 컨텍스트 제안`, a suggestion the human has not yet acted on is **still
open**, not new. Re-stating it every run buries the run's actual finding under
a paragraph the reader has already read and already decided about.

- A proposal already made in this pillar's last ~2 weeks of reports is **not
  restated**. It is rolled up into one line naming the open proposals and the
  date each was first made:

  ```markdown
  - **미결 제안 2건** — WAM 아키텍처 전용 논문 Anti-topic(최초 2026-07-27), D4ML 리밸런싱(최초 2026-08-06)
  ```

- Escalation is a count, not a re-argument. `3회 연속 관찰` is a fact worth one
  clause; the rationale stays where it was first written.
- A proposal disappears from the rollup when the human lands it in
  `context/P#.md` — that file is the accept/decline record, and it is
  read-only to the agent (`context/CLAUDE.md`).
- A subsection with nothing new says so in one bullet (`제안 없음 — …`) and stops.

### 7-2. Run-over-Run Synthesis — 3–5 bullets

`## 🔄 직전 리포트 대비 종합` covers, one bullet each and only when the run has
something to say: papers already covered (verdict first), contradictions with
recent findings, Decision-Log triggers, Anti-topic
filter health as a count, already-analyzed dedup count.

- **Never restate the retrieval funnel.** Anti-topic filter health is a count
  and a reason (`5편 제외 — WAM 아키텍처 4편, Sim2Real 미달 1편`), not the
  pipeline arithmetic from `Papers scanned` (§6).
- **A "not applicable" item is omitted, not narrated.** `월간 트렌드: 첫 리포트
  아님 — 생략` and `재등장 여부 — 해당 없음(N/A)` are lines that exist only to
  report their own emptiness. Drop the bullet.

### 7-3. Paper names must be unambiguous across reports

Codenames collide — two unrelated papers both self-titling `Faster-WAM` is an
ordinary occurrence in this corpus, and the reports read side by side across
pillars. A bare alias is only safe where a `Link` column resolves it in the
same row.

- In **prose** (💡, 🔄, 📊 heads), an alias carries its id on first use in the
  section: `Faster-WAM(2608.04404)`.
- In the 📋, 🔍 and 🚫 tables the `Paper` column stays alias-only — the `Link`
  column is the disambiguator (§4-5).
- One table row is **one paper**. A cell like `Faster-WAM 외 2편 (ω-0, WAM-Diff2)`
  against a single link hides two papers behind a third one's id; give each its
  own row.

---

## 8. Enforcement

A report goes straight to `main` with no PR, so the routine runs
`linters/check-scouting-format.py` on its own report before committing
(`.claude/prompts/scouting.txt`, LINT step) and CI re-runs it on every push to
`main` as the backstop. The lint binds reports dated on or after its
`_CONTRACT_EFFECTIVE`; the gate arithmetic binds from `_GATE_EFFECTIVE`, and
the medal, 📋 and retry rules from `_SHAPE_EFFECTIVE`.

| Rule | Checked by |
|---|---|
| H1 form and its date against the filename; the two-line metadata block, the 400-character cap, no retry narration without `최종 실패`, `Papers surfaced` a bare integer equal to the paper sections plus the 📋 rows (§6) | lint |
| Every `##` opens with a §2-1 emoji, sections in §2-1 order, each medal at most once, 📋 only under all three medals, no emoji on `###` (§2, §5-1) | lint |
| Five 📊 bullets per head summing to its total; each surfaced paper and 📋 row clears the gate; each 🔍 row exactly one gate axis short; no Reproducibility ≥ 2 that pleads an unconfirmed signal; a code label on every paper header; `★★★` only on `코드 공개` (§5) | lint |
| One paper per 🚫 / 🔍 / 📋 row (§7-3) | lint |
| Links resolve and no id is fabricated (§3); the legend lists exactly the cited codes, with badges and anchors (§3-1); the header strings (§4-3); the 개조식 register (§4-4); the render traps (§4-6 – §4-8); Reproducibility quoting its evidence (§5-2); 💡 rollup and 🔄 discipline (§7-1, §7-2) | the routine's SELF-CHECK and the reader — nothing parses them |
