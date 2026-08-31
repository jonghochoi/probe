# Scouting Report Authoring Guide
> **Version:** v1.36 (2026-08-18) · **Scope:** every `scouting/P#/YYYY-MM-DD.md`
> — the dated reports the scheduled routine writes, plus the templates in
> `scouting/templates/`.
> This document is the single source of truth for that format.
> `.claude/prompts/scouting.txt` owns the *procedure* (retrieval, scoring,
> commit) and defers to this file for the output contract. Agent reads this
> file before producing any output; change a rule here first, then the prompt.
>
> The reading site is a separate track with its own contract: `analysis/<id>.md`
> is governed by `analysis/AUTHORING.md`, not by this guide. Nothing here applies to it.

---

## 1. Output File Convention

The scouting routine runs **on a scheduled cadence**, once per pillar per run.
Each run produces **one Korean file**:

| File | Language | Purpose |
|------|----------|---------|
| `scouting/P#/YYYY-MM-DD.md` | Korean | The scouting report. `P#` is the pillar (P0–P4); `YYYY-MM-DD` is the run date. The agent reads sibling files in the same `P#/` folder for de-duplication. |

The report is written directly in Korean (no separate English file).
Paper titles, arXiv links, and `P#/D#` tags stay verbatim in their
original form (see §4-1), so de-duplication across previous reports
works on those verbatim tokens regardless of prose language.

---

## 2. Emoji System

Emoji are used **only on section headers (`##`)** — exactly one, at the start of
the header text after `## ` and a space. **`###` and deeper headers are plain
text (no emoji)**, and emoji never appear in body text, bullet points, table
cells, or code blocks.

### 2-1. Scouting report `##` emojis

The table also fixes the canonical **section order** (top to bottom). The
🚫 dropped-candidates table is a reference appendix and sits LAST, after
🔄; the decision content (papers, scores, context suggestions) stays up top.

| Emoji | Section |
|-------|---------|
| 🔑 | Reference Legend (참조 약어 풀이) |
| 🥇 | Paper N — PRIORITY ★★★ |
| 🥈 | Paper N — PRIORITY ★★ |
| 🥉 | Paper N — PRIORITY ★ |
| 🌱 | Paper N — CROSS-POLLINATION (인접 분야 픽) |
| 📊 | Scoring Summary (점수 요약) |
| 🔍 | Near-Miss Candidates (근접 후보) |
| 💡 | Context Suggestions (컨텍스트 제안) |
| 🔄 | Run-over-Run Synthesis (직전 리포트 대비 종합) |
| 🚫 | Candidate Papers That Did Not Pass Filter (필터 통과 실패 후보 논문) |

Retrieval-pass provenance — including verbatim disclosure of any tool
failure that is still failing at the end of the run (e.g.
`일부 쿼리 HTTP 429 실패`) — is summarized in the `Papers scanned:` header
line, not a dedicated section. A retry that eventually succeeded is not a
failure and is not reported at all (§6).

### 2-2. Subsection (`###`) headers are plain

The per-paper `###` subsections — (a) P# / D# touched, (b) what is genuinely
new, (c) decision implication, (d) failure mode to probe first — and the
Context-Suggestions `###` subsections carry **no emoji**.

### 2-3. Rules

- One emoji per `##` header, at the start, after `## ` and a space.
- No emoji on `#`, on `###` or deeper, on table headers, in table cells, or in
  body text.
- Do not use an emoji not listed in this guide (§2-1).
- Emojis are not translated — use the symbols exactly as listed.

#### Correct example
```markdown
## 🥇 Paper 1 — PRIORITY ★★★
### (a) P# / D# touched
### (b) What is genuinely new
```

#### Incorrect example
```markdown
## Paper 1 — PRIORITY ★★★ 🥇             ← emoji at end, wrong
### 🎯 (a) P# / D# touched               ← emoji on H3, wrong (## only)
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
- In the Near-Miss Candidates table (`Link` column)
- In the Candidate Papers table (`Link` column)
- Inline in Context Suggestions when an arXiv ID is mentioned

The 📊 section carries no table and therefore no `Link` column (§4-5) — a
paper scored there already has its link in its own header.

Do not fabricate arXiv IDs. Verify that the URL resolves before including it.

### 3-1. Reference Legend & cross-reference links

The report opens with a **Reference Legend** — a one-line glossary of the
`P#` / `D#` codes, so a reader who does not have the codes memorized can
decode the report without opening `context/P#.md`.

**Scope.** Only `P#` (Pillar) and `D#` (Decision) codes.
**Only codes actually cited in this report.** Never list a code the body
does not use; never list competitor codenames, Identity, or the falsifier.

**Placement.** A single `## 🔑 Reference Legend` section, immediately
after the top metadata block and immediately before the first
`## 🥇 Paper` section. It is the first content section of the report.
There is no boilerplate intro blockquote — it would repeat in every file and
carry no per-report information, so the report goes metadata → legend.

**Format.** One compact table, the pillar row first and the decision rows in
order of first appearance in the body — a `D#` id is opaque and carries no
sort order. One row per distinct cited code. Each code renders as a **shields.io
badge**, color-coded by category:

| Category | Color | Source |
|----------|-------|--------|
| `P0` | `f5d5d5` (pale red) | pillar palette — this table is the palette's source of truth |
| `P1` | `f5e9d5` (pale orange) | pillar palette |
| `P2` | `e2f5d5` (pale green) | pillar palette |
| `P3` | `e0d5f5` (pale purple) | pillar palette |
| `P4` | `d5def5` (pale blue) | pillar palette |
| every `D#` | `d97706` (amber) | single shared decision color |

Badge URL: `https://img.shields.io/badge/<CODE>-<hex>.svg` (label-only, no
message). All `D#` share one color (they are codes, not a ranked palette);
`P#` follows the per-pillar palette so one pillar always reads as one color
across reports. A scouting report is single-pillar, so in practice one pillar
color plus amber decisions appear.

```markdown
## 🔑 Reference Legend

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
meaning is in the legend and the paper-specific angle is in the (a)
개조식 bullets below. Separate the pillar badge from the decision badges
with ` / `, and decision badges from each other with a **single space**.

**Paper sections stay paper-focused.** The four per-paper sections read as
one story — (a) tie → (b) 핵심 기여 → (c) 시사점 → (d) 먼저 확인할 점 — and
(a) is the badge line only (no body bullets; the substance starts in (b)).
In (b)–(d), **do not plaster internal decision bookkeeping**: avoid `D#`
codes, `deferred`, config-key / `*.yaml` names in the prose. A reader
should be able to follow the paper without stopping to ask "what is D3AG?
what is deferred?". The decision link is carried by the (a) badges; concrete
context-edit proposals (which `D#` to move, which deferred candidate to
trigger) belong in 💡 Context Suggestions, the section built for them.

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
| Section headers | Korean header text (see §4-3); `##` keeps its emoji, `###` plain |

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

### 4-3. Header translation reference

`##` headers carry the §2 emoji; `###` subsections are plain.

| English header (`##`) | Korean header (`##`) |
|----------------|--------------|
| 🔑 Reference Legend | 🔑 참조 약어 풀이 |
| 🥇 Paper N — PRIORITY ★★★ | 🥇 논문 N — 우선순위 ★★★ |
| 🥈 Paper N — PRIORITY ★★ | 🥈 논문 N — 우선순위 ★★ |
| 🥉 Paper N — PRIORITY ★ | 🥉 논문 N — 우선순위 ★ |
| 🌱 Paper N — CROSS-POLLINATION | 🌱 논문 N — 인접 분야 픽 |
| 📊 Scoring Summary | 📊 점수 요약 |
| 💡 Context Suggestions | 💡 컨텍스트 제안 |
| 🔄 Run-over-Run Synthesis | 🔄 직전 리포트 대비 종합 |
| 🚫 Candidate Papers That Did Not Pass Filter | 🚫 필터 통과 실패 후보 논문 |
| (a) P# / D# touched | (a) 관련 Pillar / Decision |
| (b) Key contribution | (b) 핵심 기여 |
| (c) Takeaway for us | (c) 시사점 |
| (d) What to check first | (d) 먼저 확인할 점 |
| (sub-sections) | (하위 섹션) |

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

- Use bold (`**text**`) for the bullet label and for emphasis.
- When a bold span ends just before a Korean particle, do **not** close the
  `**` right after a closing paren / punctuation glued to the particle —
  `**용어(gloss)**을` renders the `**` literally (GFM right-flanking rule: a
  `**` preceded by punctuation must be followed by whitespace or punctuation
  to close). Close the bold on the Korean term and leave the gloss + particle
  plain: `**용어**(gloss)을`.
- Code blocks and inline code (`` `text` ``) are kept verbatim.

**Meaning is never altered for style.** Restructuring prose into 개조식 must
not add, drop, or reorder any fact, number, date, quotation, citation
polarity, causal direction, or `P#`/`D#` / arXiv / formula token — the same
fidelity bar that governs every edit.

### 4-5. Scannability — repetitive structure goes in a table

A decision-grade report is *scanned* by a reader hunting for the one row
that matters, not read prose-first end to end. §4-4 governs the register
inside a bullet; this rule governs the *layout above the sentence*.
It applies to every `scouting/` output.

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
- **No 📊 summary score table.** The 📊 section is the per-paper rationale
  only (one bold head carrying the total — `**HapTile (13/15)**` — then a
  bullet per dimension). A separate scores table duplicates it, so it is
  dropped.
- **The rubric is five fixed dimensions and the gate is four of them** — §5
  is authoritative. Never add, drop, or rename a dimension in a report, and
  always show all five bullets per paper.
- **Conclusion before enumeration.** When a long list resolves to one
  verdict ("10편 전원 재등장·제외"), state the verdict first, then the list —
  the reader must not parse every item to reach the point.
- **Machine identifiers stay out of prose.** Semantic Scholar author ids,
  and any arXiv id already carried by an adjacent `Link` column or table
  cell, do not belong inline in Korean sentences. Put them in a dedicated
  cell; never repeat an id a sibling cell already shows (e.g. the 🚫
  `Paper` column drops the id its `Link` column already carries).
- **`Papers scanned:` is a one-line summary**, not a full query log — §6
  caps it and names what belongs in it. A retrieval funnel restated anywhere
  else in the report (typically in 🔄) is a duplicate and is dropped.
- **No enumeration markers in body.** 개조식 uses bullets (§4-4); do not fall
  back to `①②` / `1. 2.` / `첫째·둘째` running inside a sentence.
- **P#/D# codes render as color-coded badges** (§3-1) — pillar palette for
  `P#`, one shared amber for every `D#` — so the decision ties in each
  paper's (a) line read as scannable chips rather than plain inline text.

These are fidelity-neutral: restructuring prose into a table or bullets must
not add, drop, or reorder any fact, number, date, citation, or `P#`/`D#` /
arXiv token — the §4-4 fidelity bar still binds.

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

The rubric is **five dimensions, 0–3 each, total /15** — Relevance · Novelty ·
Reproducibility · Methodology · Sim2Real. The per-dimension definitions live in
`.claude/prompts/scouting.txt`; this section owns what the report must *show*
and what the gate quantifies over.

### 5-1. The surfacing gate is four dimensions

A paper is surfaced as a `## 🥇 / 🥈 / 🥉` section when **Relevance, Novelty,
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

The metadata field is `**Papers surfaced (4축 게이트 통과):**` (§6). When fewer
than 3 papers clear the gate, say so and do not pad.

The `## 📊` section carries the rationale for exactly those surfaced papers:
one bold head per surfaced paper, and no head for a paper the report did not
surface. Its five bullets sum to the total the head states.

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
artifact. Rank within a ceiling by Relevance, then by the /15 total.

### 5-4. 🔍 Near-Miss Candidates

`## 🔍 근접 후보` is the standing home for two kinds of paper, and it is the
mechanism that makes "재검토 권고" actually happen:

1. **One axis short** — exactly one of the four gate dimensions scores 1 and
   the rest are ≥ 2. Two or more axes short is a 🚫 row; zero axes short is a
   surfaced paper (§5-1), never a 🔍 row.
2. **Carried forward** — a candidate listed in this section, or dropped for
   Reproducibility, in this pillar's last ~4 weeks of reports. Every run
   re-reads those entries and re-checks the code signal (§5-2). A candidate
   whose repository is now public is **promoted to a full paper section this
   run** and named in 🔄 as a promotion.

**A carried row expires four weeks after it first appears.** On the run that
passes that mark the row is either promoted or dropped from the table, and 🔄
names the retirement in one clause. Without the limit the table only grows —
every run re-lists every row, which keeps each row inside the carry-forward
window forever, spends one metadata call per row per run, and turns a
near-miss shortlist into a backlog of papers nobody is going to read.

One table, most recent first, no per-paper `###` subsections:

```markdown
| Paper | Link | R·N·M·S2R | 코드 | 재검토 조건 |
|---|---|---|---|---|
| LIRA | [arXiv:2608.07596](https://arxiv.org/abs/2608.07596) | 2·2·2·2 | 공개 예정 | 저장소 공개 시 승격 |
```

Omit the section when it has no rows. A paper appears in 🔍 or in 🚫, never
both — 🚫 is for candidates that are out, 🔍 for candidates that are waiting.

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
  number of `## 🥇 / 🥈 / 🥉 / 🌱` sections in the report. Prose about *why* the
  count is low belongs in 📊; the field is the count.
- **`Papers scanned` is capped at 400 characters** and names, at most: the
  source passes run, an order-of-magnitude count per pass, and any failure
  still unresolved when the run ended. It is a provenance line, not an audit
  trail — a reader checks that the sweep ran, then moves on.

What the line does **not** carry: per-query breakdowns, stage-by-stage funnel
arithmetic (`661건 → 507편 → 226편 → 190편 → 19편`), per-pin request counts,
or retry narration. A retry that succeeded is a non-event; only a call still
failing at the end of the run is disclosed, verbatim.

```markdown
**Papers scanned:** citation-graph 8핀 280편 + keyword sweep 110편(14일 44편)
— keyword sweep 1개 쿼리 HTTP 429 최종 실패
```

---

## 7. Section Discipline

§4-4 governs the register inside a bullet and §4-5 the layout above it. This
section governs what each `##` section is allowed to repeat.

### 7-1. 💡 Context Suggestions — a proposal is made once

A suggestion the human has not yet acted on is **still open**, not new. Re-stating
it every run buries the run's actual finding under a paragraph the reader has
already read and already decided about.

- A proposal already made in this pillar's last ~2 weeks of reports is **not
  restated**. It is rolled up into one line naming the open proposals and the
  date each was first made:

  ```markdown
  - **미결 제안 2건** — WAM 아키텍처 전용 논문 Anti-topic(최초 2026-07-27), D4ML 리밸런싱(최초 2026-08-06)
  ```

- Escalation is a count, not a re-argument. `3회 연속 관찰` is a fact worth one
  clause; the rationale stays where it was first written.
- A proposal disappears from the rollup when the human lands it in
  `context/P#.md` — that file is the accept/decline record, and the agent
  never edits it (§1).
- A subsection with nothing new says so in one bullet (`제안 없음 — …`) and stops.

### 7-2. 🔄 Run-over-Run Synthesis — 3–5 bullets

Cover, one bullet each and only when the run has something to say: papers
already covered (verdict first), contradictions with recent findings,
Decision-Log triggers, 🔍 promotions this run, Anti-topic filter health as a
count, already-analyzed dedup count.

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
- In the 🚫 and 🔍 tables the `Paper` column stays alias-only — the `Link`
  column is the disambiguator (§4-5).
- One table row is **one paper**. A cell like `Faster-WAM 외 2편 (ω-0, WAM-Diff2)`
  against a single link hides two papers behind a third one's id; give each its
  own row.
