# PROBE Style Guide
> **Version:** v1.28 (2026-06-09) · **Scope:** All files under `scouting/` and `analysis/`
> This document is the single source of truth for formatting rules.
> Agent reads this file before producing any output. Never modify output format without updating this guide first.

---

## 1. Output File Convention

The scouting routine runs **on a scheduled cadence**, once per pillar per run.
Each run produces **one Korean file**:

| File | Language | Purpose |
|------|----------|---------|
| `scouting/P#/YYYY-MM-DD.md` | Korean | The scouting report. `P#` is the pillar (P0–P5); `YYYY-MM-DD` is the run date. The agent reads sibling files in the same `P#/` folder for de-duplication. |

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
| 💡 | Context Suggestions (컨텍스트 제안) |
| 🔄 | Run-over-Run Synthesis (직전 리포트 대비 종합) |
| 🚫 | Candidate Papers That Did Not Pass Filter (필터 통과 실패 후보 논문) |

Retrieval-pass provenance — including verbatim disclosure of any tool
failure (e.g. `일부 쿼리 HTTP 429 실패`) — is summarized in the
`Papers scanned:` header line, not a dedicated section.

### 2-2. Subsection (`###`) headers are plain

The per-paper `###` subsections — (a) P# / D# touched, (b) what is genuinely
new, (c) decision implication, (d) failure mode to probe first — and the
Context-Suggestions `###` subsections carry **no emoji**.

### 2-3. Rules

- One emoji per `##` header, at the start, after `## ` and a space.
- No emoji on `#`, on `###` or deeper, on table headers, in table cells, or in
  body text.
- Do not use an emoji not listed in this guide (§2-1, §5-2, §6-2).
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
- In the Scoring Summary table (`Link` column)
- In the Candidate Papers table (`Link` column)
- Inline in Context Suggestions when an arXiv ID is mentioned

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
(There is no boilerplate intro blockquote — it repeated every file and
carried no per-report information, so the report goes metadata → legend.)

**Format.** One compact table, rows ordered `P#` → `D#` (ascending),
one row per distinct cited code. Each code renders as a **shields.io
badge**, color-coded by category:

| Category | Color | Source |
|----------|-------|--------|
| `P0` | `ff7f0e` (orange) | pillar palette — matches `refresh-analysis-index.py` `PILLAR_COLOR` |
| `P1` | `1f77b4` (blue) | pillar palette |
| `P2` | `9467bd` (purple) | pillar palette |
| `P3` | `2ca02c` (green) | pillar palette |
| `P4` | `d62728` (red) | pillar palette |
| `P5` | `17becf` (cyan) | pillar palette |
| every `D#` | `d97706` (amber) | single shared decision color |

Badge URL: `https://img.shields.io/badge/<CODE>-<hex>.svg` (label-only, no
message). All `D#` share one color (they are codes, not a ranked palette);
`P#` follows the per-pillar palette so the badge color matches the analysis
index. A scouting report is single-pillar, so in practice one pillar color
plus amber decisions appear.

```markdown
## 🔑 Reference Legend

| Code | Meaning |
|------|---------|
| <a id="ref-P2"></a>![P2](https://img.shields.io/badge/P2-9467bd.svg) | Structured Multimodal Observation Fusion (pillar) |
| <a id="ref-D4"></a>![D4](https://img.shields.io/badge/D4-d97706.svg) | Body↔Hand information sharing — FiLM, cross-attn/hidden-state deferred |
```

If the body cites no such code (rare), omit the section entirely.

**Meaning source** (deterministic — derive from `context/P#.md`,
which the agent already reads; do not invent). The meaning is a **decode
gloss**, so keep it clean: **English only** (the codes and their definitions
are English; no Korean in this column), **no `v1:` label** (the reader does
not need the version marker in a glossary), and **no `;` semicolon chains** —
use commas, ≤~12 words:

| Code | Source in `context/P#.md` | Meaning string |
|------|-----------------------------------|----------------|
| `P#` | §2 heading `Pillar P# — <name>` | `<name>` + `(pillar)` |
| `D#` | §4 `#### [D#] <title>` + its current default | `<title>` — concise gloss, ≤~12 words, commas not semicolons |

**Anchor convention.** Each legend row carries an explicit HTML anchor
`<a id="ref-<CODE>"></a>` placed before the code badge (the legend badge
itself is not a link). `<CODE>` is the verbatim code (`P1`, `D4` — case
preserved; GitHub matches explicit `id=` attributes verbatim).

**In-body links (first occurrence per section).** Within each top-level
`##` section (each Paper N and the other sections), the **first** textual
occurrence of each distinct code is written as a **linked badge**
`[![D4](https://img.shields.io/badge/D4-d97706.svg)](#ref-D4)` (same
palette as the legend). Later occurrences of that same code **in the same
section** stay plain text.
Each new `##` section links the first occurrence again, so any section is
self-contained for jump-back. Codes inside table cells and code blocks are
not linked. The legend rows themselves are not self-linked.

**No inline gloss next to a body badge.** The decision-tie line (each
paper's (a) section) is badges only — `[![P2](…)](#ref-P2) /
[![D11](…)](#ref-D11) [![D8](…)](#ref-D8)` — never a badge followed by a
parenthetical Korean description. The badge alone names the tie; its
meaning is in the legend and the paper-specific angle is in the (a)
개조식 bullets below. Separate the pillar badge from the decision badges
with ` / `, and decision badges from each other with a **single space**.

**Paper sections stay paper-focused.** The four per-paper sections read as
one story — (a) tie → (b) 핵심 기여 → (c) 시사점 → (d) 먼저 확인할 점 — and
(a) is the badge line only (no body bullets; the substance starts in (b)).
In (b)–(d), **do not plaster internal decision bookkeeping**: avoid `D#`
codes, `deferred`, `v1`, config-key / `*.yaml` names in the prose. A reader
should be able to follow the paper without stopping to ask "what is D11?
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
| P#, D# tags | Keep verbatim (`P2`, `D11`, etc.). |
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
bullets, not 합니다/됩니다 paragraphs. (The `analysis/` deep-dives keep their
explanatory 합니다/됩니다 register — §5-3, §6-1 — since they are read, not
scanned; only the scouting report is 개조식.)

- **명사형 종결.** End body items on a noun or nominalized form
  (`~함 / ~음 / ~필요 / 명사`), not a full polite sentence. `D11 인코더 학습
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
  distinct entries there) and verbatim English citation blockquotes (§5-6).

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
It applies to every `scouting/` and `analysis/` output.

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
  bullet glyph: `• a<br>• b<br>• c`. (This is how the `catalogs/`
  dataset/benchmark tables render their multi-item Source / Facts /
  Embodiment / Details cells.)
- **No 📊 summary score table.** The 📊 section is the per-paper rationale
  only (one bold head carrying the total — `**HapTile (10/12)**` — then a
  bullet per dimension). A separate scores table duplicates it, so it is
  dropped.
- **Conclusion before enumeration.** When a long list resolves to one
  verdict ("10편 전원 재등장·제외"), state the verdict first, then the list —
  the reader must not parse every item to reach the point.
- **Machine identifiers stay out of prose.** Semantic Scholar author ids,
  and any arXiv id already carried by an adjacent `Link` column or table
  cell, do not belong inline in Korean sentences. Put them in a dedicated
  cell; never repeat an id a sibling cell already shows (e.g. the 🚫
  `Paper` column drops the id its `Link` column already carries).
- **`Papers scanned:` is a one-line summary**, not a full query log —
  per-query counts and any HTTP-error disclosure live once in that header
  line (§2-1), never a separate block.
- **No enumeration markers in body.** 개조식 uses bullets (§4-4); do not fall
  back to `①②` / `1. 2.` / `첫째·둘째` running inside a sentence.
- **P#/D# codes render as color-coded badges** (§3-1) — pillar palette for
  `P#`, one shared amber for every `D#` — so the decision ties in each
  paper's (a) line read as scannable chips rather than plain inline text.

These are fidelity-neutral: restructuring prose into a table or bullets must
not add, drop, or reorder any fact, number, date, citation, or `P#`/`D#` /
arXiv token — the §4-4 fidelity bar still binds.

---

## 5. Paper Analysis Document (`analysis/`)

The `/analyze-paper` slash command (prompt: `.claude/prompts/analysis.md`)
produces a deep-dive on **one** paper at `analysis/<arxiv-id>/analysis.md`.

### 5-1. File convention

- **Korean single document.** Like every other PROBE output, a paper
  analysis is a single Korean document — there is no English source
  file. It is written natively in Korean per §4 (tone, glossary,
  verbatim tokens), not translated. The filename carries no language
  suffix — every PROBE output is Korean, so marking it is redundant.
- Filename: `analysis/<arxiv-id>/analysis.md` (e.g.
  `analysis/2401.12345/analysis.md`); non-arXiv PDF input uses a
  human-chosen slug as the folder name.
- Regenerable snapshot — re-running overwrites the file, never appends.
- The document follows `analysis/templates/analysis.md` exactly: part (A) a
  neutral structured summary, part (B) `context/MASTER.md`-anchored
  decision-grade implications.

### 5-2. Emoji system

Same rule as §2: one emoji at the start of each `##` header, `###` and body
plain. The `##` section emojis for this document type (in addition to §2):

| Emoji | Section | Part |
|-------|---------|------|
| 📄 | 논문 메타 | A |
| 🧭 | 한 줄 요약 (TL;DR) | A |
| ❓ | 문제 정의 / 동기 | A |
| 🧩 | 핵심 기여 | A |
| 🔑 | 기술 키워드 | A |
| 🔬 | 방법론 | A |
| 📊 | 실험 설정과 결과 | A |
| ⚖️ | 한계 | A |
| ♻️ | 재현성 | A |
| 🎯 | 관련 Pillar / Decision (P# / D#) | B |
| ✨ | 핀 논문 대비 델타 | B |
| ⚙️ | 의사결정 함의 | B |
| ⚠️ | 먼저 검증할 실패 모드 | B |
| 💡 | 컨텍스트 제안 | B |

Use these header names verbatim. Part (B) reuses the 🎯 ✨ ⚙️ ⚠️ 💡 semantics
from §2. Do not use an emoji not listed in §2 or here.

### 5-3. Korean & verbatim rules

§4 applies in full. Specifically: original English paper title,
config/code names, formulas, arXiv links, and `P#`/`D#` tags
are kept verbatim; technical terms use the §4-2 glossary; tone is
formal 합니다/됩니다 체.

### 5-4. Body-acquisition honesty

The 메타 header MUST state the actual full-text level reached
(`전문(arXiv HTML)` / `전문(ar5iv)` / `PDF 텍스트(pdftotext)` /
`초록 only`). If only the abstract was obtained, every part (B)
section is prefixed **(본문 미확보 — 잠정)**. Failed `curl` calls are
recorded verbatim (command + HTTP status); fabricated content is never
substituted.

### 5-5. Foundry follow-up line

The analysis always ends with exactly one blockquote line as its very
last line, regardless of whether a baseline can be matched:

```markdown
> base 매핑은 `/implement-design analysis/2401.12345/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
```

`/implement-design` itself decides whether the Design can be grounded in the
target foundry (and emits a clean `매핑 불가 (<foundry>)` line if
not). The analysis prompt never speculates about base matching — that
decision belongs to Layer 2.

### 5-6. Quotation, bullet-form, keyword, math, and figure conventions

방법론 and 실험 결과 must keep the source body traceable;
문제 정의 / 동기 and 기술 키워드 must stay scannable. The
conventions below codify both.

- **English-verbatim blockquote citation** — Anchor claims (the
  sentence that nails the design intent), every formula, and every
  key numeric claim sit inside a `>` blockquote with the English
  source text verbatim and a Korean explanation line directly below.
  Fixed format:

  ```markdown
  > "We model the action distribution with conditional flow matching." (§3.2)
  (한글 해설 — 이 문장이 왜 핵심인지.)
  ```

  Source marker is `(§n)` or `(§n, Table k)`. If the section number
  is unclear in the source body, write `(§?)` — do not guess. The
  English text is never paraphrased; the entire blockquote is a
  verbatim token, kept byte-identical.

  - **Explanation line reads as connected prose, not a terse gloss.**
    The Korean line(s) below the quote may run 1–3 sentences and
    should lead with the *intuition* — why this matters, how it works,
    what it changes — rather than restating the English. The intuition
    may also come *before* the quote, with the blockquote then standing
    as the verbatim *evidence* for a claim already made in prose. Only
    the English quote + `(§n)` marker are byte-locked; the surrounding
    explanation is where readability lives (§5-8). This is the single
    biggest lever for absorbing an explainer-tool's readability without
    losing PROBE's source traceability.

- **Formula verbatim + GitHub KaTeX rendering** — Keep the original
  LaTeX / Unicode notation; no paraphrase, symbol substitution, or
  shortening, and variable definitions match the source body. The
  normative rules (github.com renders KaTeX since 2022-05):

  - **Code-span vs. math — the boundary (decide first).** A backtick
    code-span `` `X` `` and inline math `` $`X`$ `` render differently and
    mean different things; pick by *what the token is*, not by habit:
    - **Backtick code-span** — literal source tokens (identifiers,
      function / module names, config keys, dtypes, CLI flags), tensor
      **shapes** (`` `(B, T_action, D_action)` ``), dimension variables
      (`` `d_action` ``), and numeric / resolution specs (`` `224×224` ``,
      `` `30 fps` ``). Here `×` `·` `_` `,` are code punctuation, not math.
    - **Inline math** — genuine paper notation: Greek letters, scalar /
      vector variables, sub/superscripts that denote math, operators
      (`=` `·` `≤` `≥` `≈` `→` `∈` `⊤` `Σ`), set / interval notation, and
      equations. `` `λ` `` → `` $`\lambda`$ ``; `` `A ∈ R^{d×r}` `` →
      `` $`A \in \mathbb{R}^{d\times r}`$ ``.
    - **Tag convention** — `` `(원문 미명시)` ``, `` `🚧 매핑 불가` `` are a
      deliberate annotation tag, neither code nor math; they stay backticked.
    The discriminating signal is a Greek letter, a LaTeX `\macro`, a math
    operator, a sub/superscript glyph, or an equation `=` — never `×` / `·` /
    `_` alone (those occur in shapes and specs too). `check-analysis-math.py`
    reports candidates in `design.md` (report-only — conversion is a
    judgment call, since a shape or spec legitimately stays a code-span).
  - **Inline** uses `` $`X`$ `` — backticks INSIDE the dollars. The
    outside-dollar `` `$X$` `` (becomes inline code, KaTeX never runs),
    the extra-backtick-wrapped `` `$`X`$` `` (a *valid* span wrapped in
    one more backtick pair — GitHub parses it as code-span + literal
    text + code-span, so the LaTeX leaks raw in every browser), and
    `\(…\)` / `\[…\]` (do not render on GitHub) are all FORBIDDEN.
    Why: Markdown's italic pass runs before KaTeX and eats the `_` in
    subscripts unless the backtick form shields it.
  - **Display** is `$$X$$` on its own line (no backticks) — for a
    *single-row* equation only, and it MUST start at **column 0**.
    github.com renders a display block — `$$…$$` and a ```` ```math ````
    fence alike — ONLY at the top level: indented under a list item, BOTH
    leak the raw source (the `$$` dumps raw LaTeX, the fence shows as a
    plain code block). A formula that belongs to a list item must be pulled
    OUT to column 0 — replace the intro bullet `- <label>:` with a bold
    label `**<label>**` on its own line, then the `$$…$$` at column 0 (the
    pattern every rendering analysis doc uses). Inline `` $`X`$ `` is the
    only math that renders *inside* a list item, so a short formula may stay
    inline instead.
  - **No equation-numbering macros** — `\tag`, `\label`, `\ref`,
    `\eqref`, `\nonumber` are FORBIDDEN inside `$$…$$`. github.com's KaTeX
    errors on them and dumps the raw LaTeX onto the page, wrapping it
    character-by-character. Carry the paper's equation number in the
    surrounding prose instead (`전이를 … 강제합니다 (식 1):`), then
    reference it as `식 (N)` — the convention every analysis doc follows.
  - **Multi-row display** (anything with a `\\` row break — `aligned`,
    `pmatrix` / `bmatrix` / matrices, `cases`, or a bare `\\`) MUST use a
    fenced ```` ```math ```` block, never `$$…\\…$$`. GitHub does not
    render a `\\` row break inside `$$` in *any* form (single-line or with
    the `$$` on their own lines) on any browser; only the ```` ```math ````
    block renders it. The fence, too, must sit at **column 0** — an indented
    ```` ```math ```` inside a list item shows as a code block. Example:
    ````
    ```math
    \begin{aligned} a &= b \\ c &= d \end{aligned}
    ```
    ````
  - **Boundary** — an inline `$` must not touch a Hangul / CJK syllable,
    middle-dot `·`, or bold marker `*` / `**`; separate with a space (or
    move the math outside the bold), or the delimiter goes invisible and
    the source leaks. A literal `$` in prose is escaped `\$`.
  - **Macro whitelist (the only sanctioned auto-substitutions)** —
    `\bm{X}` → `\mathbf{X}`, `\mathds{X}` → `\mathbb{X}` (`\mathds`
    is not a KaTeX control sequence and otherwise fails the whole span;
    `\mathbb` is the identical double-stroke glyph), and
    `\operatorname{X}` → `\mathrm{X}` (`\operatorname` is valid KaTeX but
    renders broken on github.com — it leaks the raw control word; `\mathrm`
    is the same upright glyph and renders). Leave every other unsupported
    macro as-is so the render failure is visible (§5-4). Extend this list
    only by editing this rule.
  - The same wrapping + boundary apply to inline math **inside English
    verbatim blockquotes** — the quoted text stays byte-identical; the
    `$` delimiters are GitHub-rendering formatting, a separate concern.

  The full arXiv-HTML → Markdown extraction procedure lives in
  `.claude/prompts/analysis.md`; PR-time enforcement and auto-fix is
  `scripts/check-analysis-math.py`
  (`.github/workflows/check-analysis-math.yml`). This subsection is the
  SSOT for the rules above — the prompt and the CI implement them.

- **Bullet form (문제 정의 / 동기)** — Do not write a single
  paragraph. Use 4–6 items, each a bold label + 1–2 sentences.
  Recommended Korean labels (verbatim): `풀고자 하는 문제`,
  `기존 접근의 한계`, `본 논문의 가설`, `왜 지금 중요한가`.

- **기술 키워드** — 5–10 key terms needed to read the paper,
  each formatted as `- **<original / abbrev>** — <one-line analogy
  or plain definition>`. **The bold head term MUST be a plain English
  word or abbreviation** (the paper's original term); any Korean gloss
  goes only *after* the em dash, never in the head, and math notation
  (`$…$`, LaTeX) belongs in the definition, not the head. This is
  load-bearing — the head is lifted into the `analysis/README.md` keyword
  badges (§5-7), which drop any head that is non-English or math-bearing,
  so a math-symbol keyword (e.g. `$`\pi_0`$`) simply won't surface there.
  For terms in the
  §4-2 glossary, still lead with the English original (glossary
  translation may follow the em dash) and add a short analogy.
  Analogies are allowed only when they do not distort the paper's
  claim; when no faithful analogy fits, write a plain definition.

- **Methodology decomposition** — Split 방법론 into four H3
  subsections wherever possible, with verbatim Korean headers:
  `### 직관`, `### 아키텍처`, `### 학습 목표 / 손실`,
  `### 학습 셋업`. Detail preservation comes first. H3 headers
  carry no emoji (same as the §2 H3-plain rule).

  - **`### 직관` is REQUIRED, and it is the plain-language layer.**
    Write the whole method so a reader with no prior context follows it:
    2–4 short paragraphs explaining *what the method does, why, and how*
    in accessible prose, with **no verbatim quotes and no formulas** —
    those belong in the `### 아키텍처` / `### 학습 목표 / 손실`
    subsections that follow. 직관 is where an explainer-tool's
    "what + why" opening is absorbed; the rigor lives below it, not
    inside it. (Abstract-only acquisition: keep 직관 brief and mark
    **(본문 미확보 — 잠정)** — do not speculate past the abstract.)

- **arXiv figure hotlink + English caption verbatim** — Insert 1–5
  high-value figures, typically one architecture / pipeline diagram
  under the methodology and one or two key ablation figures under
  the results. PROBE never copies figures into the repo; it
  hotlinks the arXiv HTML source URL (avoiding both copyright
  republication and `_assets/` size bloat). Fixed format:

  ```markdown
  ![Figure N — short label](https://arxiv.org/html/<id>/figs/<file>)

  > "Figure N: <English caption verbatim>" (§n)
  (한글 해설 — 이 그림이 본문의 어떤 주장을 시각화하는지 한 줄.)
  ```

  - URL is the arXiv HTML `<img src>` as an absolute
    `https://arxiv.org/html/<id>/<file>` — bare (unversioned) id, then
    the figure filename only. **Strip the version segment from both the
    id and the `src`** or the path doubles into a 404 (e.g.
    `…/2604.23272/2604.23272v1/x1.png`); the unversioned URL auto-maps
    to the latest figure. ar5iv mirrors / project pages / cached
    hotlinks are out (link-rot). Full extraction detail:
    `.claude/prompts/analysis.md` (FIGURE URLs).
  - The alt text follows `Figure N — <short English label>` so the
    figure number survives even when the image fails to load.
  - The English caption blockquote is a verbatim token — kept
    byte-identical, never paraphrased.
  - Abstract-only acquisition, or a non-arXiv-HTML source
    (PDF-only), means no figure URLs are available — omit the
    figure citations entirely. No placeholders, no guessing.
  - Cap: never more than 5 figures per analysis. This is a decision
    tool, not a slide deck.

### 5-7. Auto-maintained analysis index

`analysis/README.md` is generated by `scripts/refresh-analysis-index.py`,
which rewrites only the block between `<!-- ANALYSIS_INDEX:START -->` /
`<!-- ANALYSIS_INDEX:END -->` — do not hand-edit inside the markers; the
rest of the file is hand-maintained. It runs **post-merge on `main` only**;
the per-command prompts (`/analyze-paper`, `/implement-design`,
`/validate-impl`) do NOT stage `README.md` or invoke the script. The *why*
(parallel-PR conflict, the workflow) is in `CLAUDE.md`
"Automatically-maintained indexes".

The generated `README.md` block is one plain-`##` table **per primary Pillar**
(`P0`…`P5`, then `미분류`). The index taxonomy covers the six pillars P0–P5; a
`P#` outside that range is dropped at generation. The
*primary pillar* is the first entry of the `관련 Pillar` row; a paper appears
in exactly one table but lists its full pillar set in the `Pillars` column.
Empty pillar buckets are skipped. Within each table rows sort by `Refreshed`
desc (ties by arXiv id desc). Per row:

- a `Links` cell — one shields.io badge per link in the `링크` row, classified
  by host and rendered in a **fixed order: arXiv → Website → GitHub →
  HuggingFace**. Badge styles: `arXiv-<id>-b31b1b.svg` (red, carries the id),
  `Website-Link-blue`, `GitHub-Code-black`, `HuggingFace-Model-yellow`. Any
  non-arXiv/GitHub/HuggingFace URL renders as the generic `Website` badge;
- a `Pillars` cell — every `P#` from the `관련 Pillar` row as a fixed-color
  badge (P1 blue, P2 purple, P3 green, P4 red);
- a `Keywords` cell — up to 5 `기술 키워드` head terms, each a colored
  shields.io badge. English plain text only: a head carrying any math (inline
  KaTeX / LaTeX / backticks) is excluded outright, and a head with no
  recoverable English is dropped (§5-6 enforces English heads); skipped heads
  are backfilled from later bullets. All keyword badges use one color (노
  yellow, `ffd700`) — keywords are descriptive, not ranked, so a positional
  palette carried no meaning. GitHub's Markdown
  sanitizer strips inline CSS (`<span style=…>`), so a shields.io badge is the
  only way to color text per keyword on github.com;
- an `impl` cell — lerobot-based: ✅ `impl/lerobot/impl.md` exists /
  `UNMAPPABLE.md` / `—` not generated.

**Load-bearing — the 논문 메타 rows the script reads from every
`analysis/<id>/analysis.md`** (STYLE's contract; the author must emit them
exactly):

| Row label | Required format |
|---|---|
| `원문 제목 (영문)` | Plain English title |
| `링크` | `[arXiv:XXXX.XXXXX](…)`, optionally followed by `· [GitHub](…) · [HuggingFace](…) · [Website](…)` — include a non-arXiv link only if it exists and resolves; never fabricate one |
| `분석 생성일` | `YYYY-MM-DD` |
| `관련 Pillar` | Comma-separated `P#` (controlled `P0`–`P5`); first = primary |
| `태그` | Comma-separated lowercase tags from the controlled vocabulary below |
| `카탈로그` | *(optional)* Comma-separated routing tokens (or `none` / omit) opting the paper into a catalog — `target/section/handle` for datasets/benchmarks, `models/group/series/handle` for models. Drives the skeleton upsert in "Catalog cross-links" below |

The `관련 Pillar` row mirrors the `관련 Pillar / Decision` section's
pillar ties (primary first); a paper with no pillar tie omits the row and
lands in `미분류`. **Controlled tag vocabulary** (extend only by editing this
list): `vla-arch`, `forgetting`, `peft`, `tactile`, `force`,
`egocentric-data`, `dexterity`, `flow-matching`, `optimizer`, `continual`,
`sim2real`, `dataset`. Pick the 1–3 most load-bearing.

A missing / malformed scalar row yields `metadata` in that cell rather than
an abort; a missing `관련 Pillar` row yields an empty set (the paper lands in
`미분류`). The `태그` row is still authored (controlled vocabulary above) but is
no longer surfaced in the index. The
`기술 키워드` bullet heads are load-bearing too: the index reads each
bullet's term — the text before the em dash in the `- **<term>** — …` shape
§5-6 mandates (it also tolerates a `: ` separator and caps long heads).
`python3 scripts/refresh-analysis-index.py` by hand is safe and idempotent.

**Catalog cross-links.** The same script wires this index to the three
`catalogs/` files. None of the three carries a file-level `Updated` badge (the
per-row `Refreshed` cell supplies that for datasets/benchmarks); they open
directly on the first emoji `##` section header. Entry curation and the rich
hand-owned cells are never overwritten — the script only adds the marks below.

*Forward — `models.md` (badge by arXiv-id + bullet by `카탈로그` routing).* Two
independent marks. (a) **Badge:** a bullet whose arXiv id has an `analysis/<id>/`
folder gets a single-field `📝` badge (white `ffffff`, empty alt) spliced in **at
the front of the bullet, right after the list marker**, pointing at
`../analysis/<id>/analysis.md`. Idempotent: any prior leading badge (and any
legacy trailing `deep-dive` badge) is stripped before re-adding, so a removed
folder drops the badge. (b) **Bullet upsert:** a paper with a
`models/group/series/handle` `카탈로그` token that is **not yet listed** gets a
skeleton bullet (`* **<handle>**, <title>. <link badges>`) inserted at the **top**
of its `### <series>` lineage subsection (newest-first), then the badge above is
applied. `group` ∈ {`vla` → 🤖 VLA, `vlm` → 🧠 Open-weight VLM}; `series` names an
existing `### ` subsection under that group (e.g. `Standalone`,
`π (Physical Intelligence)`); `handle` is the bold display name. An already-listed
arXiv id is never re-added (create-once; the human owns curation and ordering
thereafter). A routed `### <series>` absent under its group is warned and skipped
— brand-new lineage subsections are created by hand once, then auto-fill next run.

*Forward — `datasets.md` / `benchmarks.md` (`카탈로그` routing + skeleton upsert).*
These are hand-curated rich tables (`# / <Name> / Links / Source / … / License /
Refreshed / Analysis`). A paper opts in with a `카탈로그` row =
comma-separated `target/section/handle`:

- `target` ∈ {`dataset`, `benchmark`} (here; `models` uses the 4-part grammar
  above).
- `section` controlled per target, 1:1 with the catalog's `##` headers:
  - dataset: `robot` → 🤖 Robot Action · `human` → 👤 Human Video · `mixed` →
    🔀 Mixed (Robot + Human)
  - benchmark: `harness` → 🧪 Eval Harness · `sim` → 🎮 Simulator / Sim Benchmark
    · `dexterous` → ✋ Dexterous / Contact-rich Eval
- `handle` — the short catalog display name (distinct from the paper title; e.g.
  `OXE`, `vla-eval`). No `/`.

On each run the script, for every routed paper **not already a row** in that
section's table, appends a **skeleton row** at the end of the section and
renumbers the `#` column: Links (from the `링크` row), Refreshed (= `분석 생성일`),
and the Analysis `📝` badge are auto-filled; the rich columns (Source/Facts/…)
are seeded `❓` for a human to backfill. A row whose arXiv id is already present
is **never touched** (create-once; the human owns its cells thereafter), except
its trailing **Analysis** cell, which is kept fresh (`📝` when the folder exists,
`—` otherwise). A malformed/out-of-vocabulary token is warned and dropped; a
routed section absent from the file is warned and skipped. `none` or no row
routes nowhere.

*Reverse (catalog → index badge on the index `Links` cell).* An index row whose
arXiv id appears in a catalog file gets that catalog's `catalog` badge appended
to its `Links` cell — `catalog-📚_models`, `catalog-🗂️_dataset`, or
`catalog-🎯_benchmark` (all the same purple `6f42c1`).

### 5-8. Readability / narrative layer

A paper analysis is *read* (unlike a scouting report, which is *scanned* —
§4-4), and it is also a decision tool anchored to `context/`. The rules
below raise readability to an explainer-tool standard **without touching any
machine-readable contract** (the 메타 table rows §5-7, keyword heads §5-6,
verbatim `(§n)` anchors §5-6, KaTeX §5-6, the emoji system §5-2, Part A→B
order). They govern the prose *between and around* those locked tokens.

- **Lead with intuition, then evidence.** Every (A) section earns its
  density only after the reader knows *why* it matters. The required
  `### 직관` (§5-6) carries the plain-language opening; within other
  sections, an intuition sentence may precede a verbatim quote that then
  serves as its evidence (§5-6 explanation-line rule). Restating the
  English in Korean is not an explanation — say what it *means*.

- **Short connected paragraphs over fragment dumps.** Part (A) explanatory
  prose (합니다/됩니다 체, §5-3) favors 1–4-sentence paragraphs that connect
  ideas with "왜 중요한가" expansion, not a wall of terse fragments. The
  mandated bullet sections stay bulleted (❓ 문제 정의 / 동기 §5-6, 🧩
  핵심 기여, 🔑 기술 키워드); everything else may breathe as prose. An
  architecture walk-through may use **bold inline labels + nested lists**
  (e.g. `- **CA₁ (Raw 주입)** — …`) — this is explicitly sanctioned, it
  reads better than a paragraph for component-by-component structure.

- **Expand a `D#` / `P#` on first use.** Part (B) anchors to Decision and
  Pillar codes, but a cold reader stalls on bare `D20` / `P4`. On the
  *first* occurrence in the document, attach a one-clause inline gloss:
  `D20(prior-preservation strategy)`, `P4(VLM 사전학습 보존)`. The code
  token itself stays verbatim (§4-1) — the gloss is a parenthetical, so the
  `관련 Pillar` row's `P[1-4]` parsing (§5-7) is unaffected. Later mentions
  may use the bare code.

- **⚖️ 한계 carries discursive insight; ⚠️ 먼저 검증할 실패 모드 stays
  lab-specific.** Split the two register the explainer-tool blends:
  - `⚖️ 한계` — author-stated weaknesses + inferred gaps, each with a
    1–2-sentence *discursive* read of the mechanism and why it matters
    (the "비판적 통찰" quality).
  - `⚠️ 먼저 검증할 실패 모드` — keep PROBE's differentiator: concrete
    transfer risk to *our* stack, cheapest sanity check first. Do **not**
    dilute it into generic critique; the generic critique belongs in ⚖️.

These are fidelity-neutral (§4-4 / §4-5 bar): improving readability must
not add, drop, or reorder any fact, number, quotation, citation polarity,
or `P#`/`D#` / arXiv / formula token.

---

## 6. Design + Foundry Implementation Documents

The `/analyze-paper` slash command emits a **Layer 1 Design**
(vendor-agnostic) alongside the analysis. The `/implement-design` slash command
(prompt: `.claude/prompts/implementation.md`) consumes that Design and
produces a **Layer 2** foundry-specific implementation. The two-layer
split exists so the same Design can serve multiple foundries (the v0
foundry is `lerobot`).

Outputs (all under `analysis/<id>/`):

- `analysis/<id>/design.md`                  — Layer 1 Design.
- `analysis/<id>/impl/<foundry>/impl.md`     — Korean impl guide.
- `analysis/<id>/impl/<foundry>/impl.patch`  — unified diff against
                                               the foundry's code
                                               root (for lerobot:
                                               `vendor/lerobot/`).
- `analysis/<id>/validation/<foundry>.md`         — Korean static
                                               validation report
                                               (`/validate-impl`).

### 6-1. File convention

- Korean single document, written natively per §4 (formal 합니다/됩니다
  체, glossary §4-2, verbatim tokens).
- Filenames: see the per-track paths above. No language suffix.
- Both Design and impl are **regenerable snapshots** — re-running the
  generator overwrites them.
- The Design document follows `analysis/templates/design.md` — 9 `##`
  sections in this order: 메타, 데이터 계약, 모듈 인터페이스,
  불변식·가정, 하이퍼파라미터·손실, 평가 메트릭, 변경
  의도, Foundry 힌트, 미해결 / 잠정.
- The impl document follows `analysis/templates/impl.md` exactly. Six
  `##` sections in this order: 가이드 메타, 베이스 / 코드 좌표
  식별, 변경 지점 매핑, 핵심 변경 (diff), 실무 구현 주의,
  미해결 / 잠정.
- The validation report follows `analysis/templates/validation.md` — six `##`
  sections: 검증 메타, 문헌 대조, 패치 정합성, 시그니처
  ·하이퍼파라미터 일치, 식·표 일치, 종합 판정, 미해결 /
  잠정.

### 6-2. Emoji system

Same rule as §2: one emoji at the start of each `##` header, `###` and body
plain. The `##` section emojis for this document family (added on top of §2 and
§5-2):

| Emoji | Section | Document |
|-------|---------|----------|
| 📄 | Design 메타 · 가이드 메타 · 검증 메타 | Design · impl · verify |
| 🧮 | 데이터 계약 | Design |
| 🧰 | 모듈 인터페이스 | Design |
| ⛓️ | 불변식·가정 | Design |
| 📊 | 하이퍼파라미터·손실 | Design |
| 🎯 | 평가 메트릭 | Design |
| ✨ | 변경 의도 | Design |
| 🔌 | Foundry 힌트 | Design |
| 🧱 | 베이스 / 코드 좌표 식별 | impl |
| 🪛 | 변경 지점 매핑 | impl |
| ⚙️ | 핵심 변경 (diff) | impl |
| 🧪 | 실무 구현 주의 · 시그니처·하이퍼파라미터 일치 | impl · verify |
| 📚 | 문헌 대조 | verify |
| 🔍 | 패치 정합성 | verify |
| 📐 | 식·표 일치 | verify |
| 🧬 | 실행 검증 | verify |
| ⚖️ | 종합 판정 | verify |
| 🔎 | §🚧 분류 | verify |
| 🚧 | 미해결 / 잠정 | Design · impl · verify |

### 6-3. Vendor-agnostic Design vs. foundry-bound impl

The Design contains **no `file:line` coordinates** from
`vendor/lerobot/` or any other codebase. Its module-interface section
records function signatures and contracts, not source locations. This
keeps the Design portable across foundries.

Every impl-document code reference, in contrast, points inside the
chosen foundry's code root and follows the form
`<foundry-root>/<path>:<line>` (line numbers optional but recommended;
for `lerobot` the prefix is `vendor/lerobot/policies/<base>/`).
Coordinates are bound to the foundry's pinned snapshot — for lerobot
the SHA in `vendor/lerobot/README.md`, which the impl's 가이드 메타
table MUST cite verbatim. Bumping the snapshot invalidates every
existing `*/lerobot/impl.patch`; see `vendor/lerobot/README.md` for the
refresh procedure.

### 6-4. Honesty rules carried over

- If `analysis/<id>/analysis.md` was produced from abstract-only,
  every Design section is prefixed **(본문 미확보 — 잠정)** and most
  fields will be `(원문에 명시 없음 — 가정으로 메움)`. The impl document,
  when generated, also prefixes every `##` section first line with
  **(본문 미확보 — 잠정)** and no patch file is produced — only the
  markdown.
- Sparse Design > fabricated Design. Any field the source does not pin
  down is left as `(원문에 명시 없음 — 가정으로 메움)`.
- If `git apply --check` fails on the generated patch, the failure is
  recorded verbatim in the 가이드 메타 table and at the end of
  핵심 변경 (diff). Affected hunks are downgraded to + entries
  instead of being silently forged.
- If the Design cannot ground in the target foundry, **neither**
  `impl.md` nor `impl.patch` is produced. Instead `/implement-design` writes
  `analysis/<id>/impl/<foundry>/UNMAPPABLE.md` with one paragraph of
  reason, and appends one line to `analysis/<id>/analysis.md`:
  `> 매핑 불가 (<foundry>) — Design 의 일부가 이 foundry 의 좌표계로 매핑되지 않습니다.`

### 6-5. Verify report (`/validate-impl` output)

The validation report is the static check of a Design + foundry patch
against the originating analysis and the foundry code. It is the
single deliverable — there is no manifest, no graduated status.

Four `##` sections drive the verdict (`pass` / `fail` / `partial` per
section), followed by 종합 판정 summarising whether the analysis
can rely on this implementation:

- 문헌 대조 — Design vs cited analyses (일치 / 충돌 / 확장 / 무관).
- 패치 정합성 — re-run `git apply --check` against the current
  foundry tree.
- 시그니처·하이퍼파라미터 일치 — function signatures, hyperparameter
  constants, and import paths must match between patch and foundry.
- 식·표 일치 — formulas and tables cited in the Design or analyses
  must either be implemented in the patch or explicitly deferred to .

The verifier executes no code beyond `git apply --check`. `partial` is
a normal outcome and far better than a fabricated `pass`.
