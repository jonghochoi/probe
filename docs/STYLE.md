# PROBE Style Guide
> **Version:** v1.13 (2026-05-21) · **Scope:** All files under `scouting/`, `synthesis/`, and `analysis/`
> This document is the single source of truth for formatting rules.
> Agent reads this file before producing any output. Never modify output format without updating this guide first.

---

## 1. Output File Convention

The scouting routine runs **twice a week (Monday & Thursday)**, once per
pillar. Each run produces **one Korean file**:

| File | Language | Purpose |
|------|----------|---------|
| `scouting/YYYY-MM-DD-P#.md` | Korean | The scouting report. `YYYY-MM-DD` is the run date; `P#` is the pillar (P1–P4). Used by the agent for de-duplication and future retrieval. |

The report is written directly in Korean (no separate English file).
Paper titles, arXiv links, and `P#/D#/CP#` tags stay verbatim in their
original form (see §4-1), so de-duplication across previous reports
works on those verbatim tokens regardless of prose language.

---

## 2. Emoji System

Emojis are used **only on section and subsection headers** (lines starting with `##` or `###`).
They are **never** used inside body text, bullet points, table cells, or code blocks.

### 2-1. Section-level (`##`) Emojis

| Emoji | Section |
|-------|---------|
| 🔑 | Reference Legend |
| 📋 | Scout Methodology |
| 🥇 | Paper N — PRIORITY ★★★ |
| 🥈 | Paper N — PRIORITY ★★ |
| 🥉 | Paper N — PRIORITY ★ |
| 🌱 | Paper N — CROSS-POLLINATION |
| 📊 | Scoring Summary |
| 🚫 | Candidate Papers That Did Not Pass Filter |
| 💡 | Context Suggestions |
| 🔄 | Run-over-Run Synthesis |

### 2-2. Subsection-level (`###`) Emojis

These four emojis are used consistently across **all** paper entries:

| Emoji | Subsection |
|-------|------------|
| 🎯 | (a) P# / D# touched |
| ✨ | (b) What is genuinely new |
| ⚙️ | (c) Decision implication |
| ⚠️ | (d) Failure mode to probe first |

Context Suggestions subsections use a single emoji:

| Emoji | Subsection |
|-------|------------|
| 📌 | All sub-sections within Context Suggestions |

### 2-3. Rules

- One emoji per header, placed at the **start** of the header text, after `##` or `###` and a space.
- Do not add emojis to the report title (`#`) or to table headers.
- Do not use any emoji not listed in this guide.
- Emojis are not translated — use the symbols exactly as listed.

#### Correct example
```markdown
## 🥇 Paper 1 — PRIORITY ★★★
### 🎯 (a) P# / D# touched
### ✨ (b) What is genuinely new
```

#### Incorrect example
```markdown
## Paper 1 — PRIORITY ★★★ 🥇              ← emoji at end, wrong
### (a) 🎯 P# / D# touched                  ← emoji inside text, wrong
The policy achieved ✨ great results.       ← emoji in body text, wrong
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
`P#` / `D#` / `CP#` codes, so a reader who does not have the codes
memorized can decode the report without opening `context/P#.md`.

**Scope.** Only `P#` (Pillar), `D#` (Decision), `CP#` (Checkpoint) codes.
**Only codes actually cited in this report.** Never list a code the body
does not use; never list competitor codenames, Identity, or the falsifier.

**Placement.** A single `## 🔑 Reference Legend` section, immediately
after the top intro blockquote and immediately before `## 📋 Scout
Methodology`. It is the first content section of the report.

**Format.** One compact table, rows ordered `P#` → `D#` (ascending) →
`CP#` (ascending), one row per distinct cited code:

```markdown
## 🔑 Reference Legend

| Code | Meaning |
|------|---------|
| <a id="ref-P1"></a>**P1** | Heterogeneous Body/Hand Action Expert (pillar) |
| <a id="ref-D4"></a>**D4** | Body↔Hand information sharing — v1 FiLM; cross-attn/hidden-state deferred |
| <a id="ref-CP1"></a>**CP1** | Checkpoint 1: v1 first ablation (4-contribution, in-hand rotation, sim) |
```

If the body cites no such code (rare), omit the section entirely.

**Meaning source** (deterministic — derive from `context/P#.md`,
which the agent already reads; do not invent):

| Code | Source in `context/P#.md` | Meaning string |
|------|-----------------------------------|----------------|
| `P#` | §2 heading `Pillar P# — <name>` | `<name>` + `(pillar)` |
| `D#` | §4 `#### [D#] <title>` + its v1 line | `<title>` — v1 choice in ≤ ~12 words |
| `CP#` | §3 bullet `- **CP#**: <desc>` | `Checkpoint #: <desc>` (compressed) |

**Anchor convention.** Each legend row carries an explicit HTML anchor
`<a id="ref-<CODE>"></a>` placed before the bold code. `<CODE>` is the
verbatim code (`P1`, `D4`, `CP2` — case preserved; GitHub matches explicit
`id=` attributes verbatim).

**In-body links (first occurrence per section).** Within each top-level
`##` section (each Paper N, 📋, 📊, 🚫, 💡, 🔄), the **first** textual
occurrence of each distinct code is written as `[D4](#ref-D4)`. Later
occurrences of that same code **in the same section** stay plain text.
Each new `##` section links the first occurrence again, so any section is
self-contained for jump-back. Codes inside table cells and code blocks are
not linked. The legend rows themselves are not self-linked.

---

## 4. Korean Authoring Principles

The report is written directly in Korean. There is no English source
file to translate from — but the same rules apply for which tokens stay
verbatim in their original form versus which prose is Korean.

### 4-1. What to write in Korean vs. keep verbatim

| Category | Treatment |
|----------|-----------|
| Body prose | Korean — tone fully governed by §4-5 (humanize-korean) |
| Paper titles | Keep original English title; add Korean description if helpful |
| Technical terms | First occurrence: Korean term + English in parentheses. Subsequent: Korean only |
| Config / code names | Keep verbatim (`env_cfg.py`, `ObservationManager`, etc.) |
| Formulas / numbers | Keep verbatim (`ε = 0.1`, `±2σ`, `< 15%`, etc.) |
| P#, D#, CP# tags | Keep verbatim (`P2`, `D11`, `CP3`, etc.) |
| Reference Legend | Meaning column in Korean; codes + `<a id="ref-…">` anchors verbatim |
| Anchor / intra-doc links | Keep `id=` and `[…](#ref-…)` verbatim — links resolve within the file |
| arXiv links | Keep verbatim |
| Emojis | Keep identical — same position, same emoji |
| Section headers | Korean header text (see §4-3); keep emoji prefix |

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
| Author Watch | Author Watch (저자 추적) |
| Keyword Sweep | Keyword Sweep (키워드 스윕) |
| System0 / System1 | System0 / System1 (저수준 안정화 / 고수준 정책 계층) |
| Structured input-modality binding | 구조적 입력-모달리티 결합 |
| VLM pretraining preservation | VLM 사전학습 보존 |
| Action expert | 액션 전문가 |
| Flow matching | 플로우 매칭 |

### 4-3. Header translation reference

| English header | Korean header |
|----------------|--------------|
| 🔑 Reference Legend | 🔑 참조 약어 풀이 |
| 📋 Scout Methodology | 📋 스카우트 방법론 |
| 🥇 Paper N — PRIORITY ★★★ | 🥇 논문 N — 우선순위 ★★★ |
| 🥈 Paper N — PRIORITY ★★ | 🥈 논문 N — 우선순위 ★★ |
| 🥉 Paper N — PRIORITY ★★ | 🥉 논문 N — 우선순위 ★ |
| 🌱 Paper N — CROSS-POLLINATION | 🌱 논문 N — 크로스폴리네이션 |
| 📊 Scoring Summary | 📊 점수 요약 |
| 🚫 Candidate Papers That Did Not Pass Filter | 🚫 필터 통과 실패 후보 논문 |
| 💡 Context Suggestions | 💡 컨텍스트 제안 |
| 🔄 Run-over-Run Synthesis | 🔄 직전 리포트 대비 종합 |
| 🎯 (a) P# / D# touched | 🎯 (a) 관련 Pillar / Decision (P# / D#) |
| ✨ (b) What is genuinely new | ✨ (b) 진정으로 새로운 점 |
| ⚙️ (c) Decision implication | ⚙️ (c) 의사결정 함의 |
| ⚠️ (d) Failure mode to probe first | ⚠️ (d) 먼저 검증해야 할 실패 모드 |
| 📌 (sub-sections) | 📌 (하위 섹션) |

### 4-4. Tone and style — delegated to humanize-korean

PROBE no longer carries its own Korean tone rules. Every Korean output
passes through the `humanize-korean` skill (§4-5) immediately before
commit, and that skill is the sole authority on register, rhythm,
density, sentence-length distribution, conjunction frequency, hedging
level, and visual-ornament usage. Authoring agents draft freely; the
post-processing pass normalizes the prose.

The two surface conventions that still live here, because they are
markdown rather than tone:

- Use bold (`**text**`) for emphasis where it aids the reader.
- Code blocks and inline code (`` `text` ``) are kept verbatim — see
  the §4-5 invariants list.

### 4-5. Humanize-korean post-processing (mandatory tail step)

Every Korean output in PROBE (`scouting/`, `synthesis/`, `analysis/`)
passes through the `humanize-korean` skill
(`.claude/skills/humanize-korean/SKILL.md`, ported from
[`epoko77-ai/im-not-ai`](https://github.com/epoko77-ai/im-not-ai))
immediately before `git add`. The skill detects and rewrites the
"AI tell" patterns catalogued at
`.claude/skills/humanize-korean/references/ai-tell-taxonomy.md` —
translation-ese, mechanical parallelism, AI signature phrases,
hedging chains, formal-noun overuse, visual-ornament overuse —
into natural Korean prose. **Content is never touched.**

**In-scope rewrites.** Categories A (translation-ese), C (mechanical
parallelism / colon-subtitle headings), D (AI signature phrases like
"결론적으로 / ~할 수 있다 / 시사하는 바가 크다"), E (uniform rhythm),
F (over-modification), G (hedging), H (conjunction overuse), I
(formal-noun overuse), J (visual ornament) in the taxonomy are all
in-scope. This skill is also the authority on **register** — every
PROBE Korean output is normalized to formal 합니다/됩니다 정중체
regardless of what the authoring agent produced. STYLE no longer
encodes its own tone rules; if the desired register changes, the
upstream taxonomy is the single point of edit.

**Forbidden by `content-fidelity-auditor` (rollback on violation).**
Anything that would change meaning — facts, claims, numbers, dates,
direct quotations, citation polarity, causal direction, hedging level
(단정 ↔ 추측), enumeration order, omitted or added information — is
forbidden. PROBE-specific invariants the auditor MUST also treat as
rollback triggers:

- Paper titles in original English (see §4-1)
- Config / code names (`env_cfg.py`, `ObservationManager`, etc.)
- Formulas and numbers (`ε = 0.1`, `±2σ`, `< 15%`)
- `P#` / `D#` / `CP#` tags
- `<a id="ref-…">` anchors and `[CODE](#ref-CODE)` intra-doc links
- arXiv / DOI links
- arXiv figure hotlinks and their accompanying English caption
  blockquotes (see §5-6 figure-citation block)
- Emoji set, position, and the one-emoji-per-header rule (see §2)
- §4-2 glossary translations for technical terms (no resynonymization
  to a non-glossary word)

**Operational guards.** Change rate `> 30%` triggers an automatic
rework round; `> 50%` aborts the rewrite and keeps the original. A
`fidelity_audit` verdict of `fail` always rolls back to the
pre-humanize content; that content is what gets committed.
`humanize-korean` is the LAST step before `git add` — never run it
before the agent has finished writing the output file.

**Pipeline.** PROBE uses the `--strict` 4-agent pipeline:
`ai-tell-detector` → `korean-style-rewriter` →
[`content-fidelity-auditor` ∥ `naturalness-reviewer`]. The two
reviewers run in parallel and are orthogonal — the fidelity auditor
asks only "is the meaning preserved?", the naturalness reviewer asks
only "did the AI tells actually disappear, and was the rewrite not
over-polished?". A `fail` from fidelity always rolls back; a
`rewrite_round_2` or `rollback_and_rewrite` from naturalness triggers
a second pass (max 3 rounds, then `hold_and_report` for human review).
The monolith fast-path from `im-not-ai` upstream is not used here.

This subsection is the single source of truth that the
`humanize-korean` skill must respect when run against any PROBE
output. The skill's own taxonomy and playbook are upstream defaults;
this section overrides them on conflict.

---

## 5. Paper Analysis Document (`analysis/`)

The `/analyze-paper` slash command (prompt: `.claude/prompts/paper-analysis.md`)
produces a deep-dive on **one** paper at `analysis/<arxiv-id>.md`.

### 5-1. File convention

- **Korean single document.** Like every other PROBE output, a paper
  analysis is a single Korean document — there is no English source
  file. It is written natively in Korean per §4 (tone, glossary,
  verbatim tokens), not translated. The filename carries no language
  suffix — every PROBE output is Korean, so marking it is redundant.
- Filename: `analysis/<arxiv-id>.md` (e.g. `analysis/2401.12345.md`);
  non-arXiv PDF input uses a human-chosen slug.
- Regenerable snapshot — re-running overwrites the file, never appends.
- The document follows `analysis/_TEMPLATE.md` exactly: part (A) a
  neutral structured summary, part (B) `context/MASTER.md`-anchored
  decision-grade implications.

### 5-2. Emoji system

Same rule as §2: one emoji at the **start** of each `##` / `###`
header, never in body text. Section (`##`) emojis for this document
type — these are the only emojis permitted here in addition to §2:

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

Part (B) reuses the existing 🎯 ✨ ⚙️ ⚠️ 💡 semantics from §2-2 / §2-1.
Do not use any emoji not listed in §2 or here.

### 5-3. Korean & verbatim rules

§4 applies in full. Specifically: original English paper title,
config/code names, formulas, arXiv links, and `P#`/`D#`/`CP#` tags
are kept verbatim; technical terms use the §4-2 glossary; tone is
formal 합니다/됩니다 체.

### 5-4. Body-acquisition honesty

The 📄 메타 header MUST state the actual full-text level reached
(`전문(arXiv HTML)` / `전문(ar5iv)` / `PDF 텍스트(pdftotext)` /
`초록 only`). If only the abstract was obtained, every part (B)
section is prefixed **(본문 미확보 — 잠정)**. Failed `curl` calls are
recorded verbatim (command + HTTP status); fabricated content is never
substituted.

### 5-5. Foundry follow-up line

The analysis always ends with exactly one blockquote line as its very
last line, regardless of whether a baseline can be matched:

```markdown
> 💡 base 매핑은 `/foundry analysis/2401.12345_design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
```

`/foundry` itself decides whether the Design can be grounded in the
target foundry (and emits a clean `🚧 매핑 불가 (<foundry>)` line if
not). The analysis prompt never speculates about base matching — that
decision belongs to Layer 2.

### 5-6. Quotation, bullet-form, keyword, math, and figure conventions

🔬 방법론 and 📊 실험 결과 must keep the source body traceable;
❓ 문제 정의 / 동기 and 🔑 기술 키워드 must stay scannable. The
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
  English text is never paraphrased; the `humanize-korean` pass
  treats the entire blockquote as a verbatim token (§4-5 invariants
  extension).

- **Formula verbatim + GitHub KaTeX rendering** — Keep the original
  LaTeX / Unicode notation. No paraphrasing, symbol substitution, or
  shortening. Variable definitions match the source body.
  github.com's Markdown renderer supports KaTeX (since 2022-05), so
  PROBE wraps math as **`` $`X`$ `` for inline (backticks INSIDE the
  dollars) and `$$X$$` on its own line for display**. `\(…\)` /
  `\[…\]` do not render on GitHub and are forbidden. From arXiv HTML
  (LaTeXML) source, follow this extraction recipe:

  1. `<math display="inline" … alttext="X">` → `` $`X`$ `` —
     **inline math MUST use the inside-dollar backtick form**
     `` $`X`$ ``. GitHub Markdown's italic pass runs before KaTeX
     and otherwise captures the `_` in subscripts like `x_{t}`
     (which appears in practically every inline span). With multiple
     such spans on the same line, the italic toggle cascades and
     breaks every math boundary on the line. The inside-dollar
     backtick form is GitHub's official recommendation and PROBE's
     only allowed inline form. **The outside-dollar form `` `$X$` ``
     is FORBIDDEN** — it becomes an inline-code span, so KaTeX
     never runs. The two forms differ only in character order and
     produce opposite results.
  2. **Inline math boundary rule** — GitHub's KaTeX inline parser
     only recognises a `$` when its neighbours are non-word. The
     opener `$` must be preceded by start-of-line, whitespace, or
     one of `(` `[` `{` `<`. The closer `$` must be followed by
     end-of-line, whitespace, or one of `.` `,` `;` `:` `!` `?`
     `)` `]` `}` `>`. CJK middle-dot `·`, bold markers `*`/`**`, or
     Hangul syllables glued directly to a `$` make that boundary
     invisible and the source leaks through. Failures → fixes:
     - `$X$·$Y$` (two math spans joined by middle-dot) →
       `$X$ · $Y$` (one space on each side).
     - `**$X$ Y**` (math glued inside bold) → `$X$ **Y**` or
       `X **Y**` — move the math outside the bold marker so the
       `$` never touches a `*`.
     - `의$X$` / `$X$를` (Hangul touching `$`) → always one space
       between Hangul and `$`.
  3. `<math display="block" … alttext="X">` or any
     `class="ltx_equation*"` container's `alttext` → its own `$$X$$`
     line. Leading `\displaystyle` and trailing commas may be
     stripped. Display blocks are recognised as their own line
     blocks, so they have no underscore / boundary problem and need
     no backticks.
  4. Decode HTML entities: `&gt;` → `>`, `&lt;` → `<`, `&amp;` →
     `&`.
  5. Do not silently substitute KaTeX-unsupported macros (`\bm`,
     certain `\xrightarrow` variants, author-defined `\newcommand`).
     Leaving them in place surfaces a visible render error on
     GitHub, which aligns with the honesty principle (§5-4).
  6. Escape a literal `$` in prose as `\$` so it isn't mistaken for
     a math opener.

- **Bullet form (❓ 문제 정의 / 동기)** — Do not write a single
  paragraph. Use 4–6 items, each a bold label + 1–2 sentences.
  Recommended Korean labels (verbatim): `풀고자 하는 문제`,
  `기존 접근의 한계`, `본 논문의 가설`, `왜 지금 중요한가`.

- **🔑 기술 키워드** — 5–10 key terms needed to read the paper,
  each formatted as `- **<original / abbrev>** — <one-line analogy
  or plain definition>`. For terms in the §4-2 glossary, use the
  glossary translation as the head and add a short analogy.
  Analogies are allowed only when they do not distort the paper's
  claim; when no faithful analogy fits, write a plain definition.

- **Methodology decomposition** — Split 🔬 방법론 into four H3
  subsections wherever possible, with verbatim Korean headers:
  `### 직관`, `### 아키텍처`, `### 학습 목표 / 손실`,
  `### 학습 셋업`. Detail preservation comes first. H3 headers
  carry no emoji (same as the §2 H3-plain rule).

- **arXiv figure hotlink + English caption verbatim** — Insert 1–3
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

  - URL must be the arXiv HTML `<img src>` resolved to an absolute
    path (`https://arxiv.org/html/<id>/<src>`). ar5iv mirrors,
    author project pages, and cached hotlinks are out — too much
    link-rot risk. Do not pin a version (`<id>v2/...`); arXiv
    auto-maps the unversioned URL to the latest figure.
  - The alt text follows `Figure N — <short English label>` so the
    figure number survives even when the image fails to load.
  - The English caption blockquote is a verbatim token (§4-5
    invariants extension); the humanize-korean pass leaves it
    untouched.
  - Abstract-only acquisition, or a non-arXiv-HTML source
    (PDF-only), means no figure URLs are available — omit the
    figure citations entirely. No placeholders, no guessing.
  - Cap: never more than 3 figures per analysis. This is a decision
    tool, not a slide deck.

### 5-7. Auto-maintained analysis index

`analysis/README.md` carries a generated index of every deep-dive in
the folder, refreshed by `scripts/refresh-analysis-index.py`. The
script is invoked automatically by the GIT step of `/analyze-paper`,
`/foundry`, and `/audit`, so any run that adds or refreshes an
analysis (or its downstream impl/audit artifacts) updates the index
in the same commit. This is the first intentional exception to the
"every doc reference is hand-maintained" rule recorded in `CLAUDE.md`.

The script rewrites only the block between these fixed markers in
`analysis/README.md`; the rest of the file is preserved verbatim:

```markdown
<!-- ANALYSIS_INDEX:START -->
... auto-generated table ...
<!-- ANALYSIS_INDEX:END -->
```

The table has six columns: `#`, `Analysis` (relative hotlink),
`arXiv` (link to the arXiv abstract), `Title` (the paper's English
title), `Refreshed` (ISO date), `lerobot` (✅ if
`<id>_impl/lerobot/impl.md` exists, 🚧 if `UNMAPPABLE.md` exists,
`—` if `/foundry` has not been run for the lerobot foundry).
Sort: `Refreshed` descending, ties broken by arXiv id descending.

Load-bearing 📄 논문 메타 rows the script reads from every
`analysis/<id>.md`:

| Row label | Required format |
|---|---|
| `원문 제목 (영문)` | Plain English title |
| `링크` | `[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX)` |
| `분석 생성일` | `YYYY-MM-DD` |

If any of these rows is missing or malformed, the script writes
`⚠️ metadata` in the affected cell rather than aborting, so one
broken file cannot break the whole index. Running
`python3 scripts/refresh-analysis-index.py` by hand is safe and
idempotent — re-running with no underlying change produces no diff.

---

## 6. Design + Foundry Implementation Documents

The `/analyze-paper` slash command emits a **Layer 1 Design**
(vendor-agnostic) alongside the analysis. The `/foundry` slash command
(prompt: `.claude/prompts/foundry.md`) consumes that Design and
produces a **Layer 2** foundry-specific implementation. The two-layer
split exists so the same Design can serve multiple foundries (the v0
foundry is `lerobot`).

Outputs:

- `analysis/<id>_design.md`                  — Layer 1 Design.
- `analysis/<id>_impl/<foundry>/impl.md`     — Korean impl guide.
- `analysis/<id>_impl/<foundry>/impl.patch`  — unified diff against
                                               the foundry's code
                                               root (for lerobot:
                                               `vendor/lerobot/`).
- `analysis/<id>_audit/<foundry>.md`        — Korean static
                                               validation report
                                               (`/audit`).

### 6-1. File convention

- Korean single document, written natively per §4 (formal 합니다/됩니다
  체, glossary §4-2, verbatim tokens).
- Filenames: see the per-track paths above. No language suffix.
- Both Design and impl are **regenerable snapshots** — re-running the
  generator overwrites them.
- The Design document follows `analysis/_TEMPLATE_DESIGN.md` — 9 `##`
  sections in this order: 📄 메타, 🧮 데이터 계약, 🧰 모듈 인터페이스,
  ⛓️ 불변식·가정, 📊 하이퍼파라미터·손실, 🎯 평가 메트릭, ✨ 변경
  의도, 🔌 Foundry 힌트, 🚧 미해결 / 잠정.
- The impl document follows `analysis/_TEMPLATE_IMPL.md` exactly. Six
  `##` sections in this order: 📄 가이드 메타, 🧱 베이스 / 코드 좌표
  식별, 🪛 변경 지점 매핑, ⚙️ 핵심 변경 (diff), 🧪 실무 구현 주의,
  🚧 미해결 / 잠정.
- The audit report follows `analysis/_TEMPLATE_AUDIT.md` — six `##`
  sections: 📄 검증 메타, 📚 문헌 대조, 🔍 패치 정합성, 🧪 시그니처
  ·하이퍼파라미터 일치, 📐 식·표 일치, ⚖️ 종합 판정, 🚧 미해결 /
  잠정.

### 6-2. Emoji system

Same rule as §2: one emoji at the start of each `##` / `###` header,
never in body. Section (`##`) emojis specific to this document family
(added on top of §2 and §5-2):

| Emoji | Section | Document |
|-------|---------|----------|
| 📄 | Design 메타 · 가이드 메타 · 검증 메타 | Design · impl · verify (reused from §5-2) |
| 🧮 | 데이터 계약 | Design (new) |
| 🧰 | 모듈 인터페이스 | Design (new) |
| ⛓️ | 불변식·가정 | Design (new) |
| 📊 | 하이퍼파라미터·손실 | Design (reused from §5-2) |
| 🎯 | 평가 메트릭 | Design (reused from §5-2 / §2-2) |
| ✨ | 변경 의도 | Design (reused from §5-2 / §2-2) |
| 🔌 | Foundry 힌트 | Design (new) |
| 🧱 | 베이스 / 코드 좌표 식별 | impl |
| 🪛 | 변경 지점 매핑 | impl |
| ⚙️ | 핵심 변경 (diff) | impl |
| 🧪 | 실무 구현 주의 · 시그니처·하이퍼파라미터 일치 | impl · verify |
| 📚 | 문헌 대조 | verify (new) |
| 🔍 | 패치 정합성 | verify (new) |
| 📐 | 식·표 일치 | verify (new) |
| ⚖️ | 종합 판정 | verify (new) |
| 🚧 | 미해결 / 잠정 | Design · impl · verify |

🧮 🧰 ⛓️ 🔌 are introduced by Design. 🧱 🪛 are introduced for impl.
📚 🔍 📐 ⚖️ are introduced for verify. 🧪 🚧 are reused across
documents. None appear elsewhere in PROBE outputs outside §6.

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
the SHA in `vendor/lerobot/README.md`, which the impl's 📄 가이드 메타
table MUST cite verbatim. Bumping the snapshot invalidates every
existing `*/lerobot/impl.patch`; see `vendor/lerobot/README.md` for the
refresh procedure.

### 6-4. Honesty rules carried over

- If `analysis/<id>.md` was produced from abstract-only, every Design
  section is prefixed **(본문 미확보 — 잠정)** and most fields will be
  `(원문에 명시 없음 — 가정으로 메움)`. The impl document, when
  generated, also prefixes every `##` section first line with
  **(본문 미확보 — 잠정)** and no patch file is produced — only the
  markdown.
- Sparse Design > fabricated Design. Any field the source does not pin
  down is left as `(원문에 명시 없음 — 가정으로 메움)`.
- If `git apply --check` fails on the generated patch, the failure is
  recorded verbatim in the 📄 가이드 메타 table and at the end of
  ⚙️ 핵심 변경 (diff). Affected hunks are downgraded to 🪛 + 🚧 entries
  instead of being silently forged.
- If the Design cannot ground in the target foundry, **neither**
  `impl.md` nor `impl.patch` is produced. Instead `/foundry` writes
  `analysis/<id>_impl/<foundry>/UNMAPPABLE.md` with one paragraph of
  reason, and appends one line to `analysis/<id>.md`:
  `> 🚧 매핑 불가 (<foundry>) — Design 의 일부가 이 foundry 의 좌표계로 매핑되지 않습니다.`

### 6-5. Verify report (`/audit` output)

The audit report is the static check of a Design + foundry patch
against the originating analysis and the foundry code. It is the
single deliverable — there is no manifest, no graduated status.

Four `##` sections drive the verdict (`pass` / `fail` / `partial` per
section), followed by ⚖️ 종합 판정 summarising whether the analysis
can rely on this implementation:

- 📚 문헌 대조 — Design vs cited analyses (일치 / 충돌 / 확장 / 무관).
- 🔍 패치 정합성 — re-run `git apply --check` against the current
  foundry tree.
- 🧪 시그니처·하이퍼파라미터 일치 — function signatures, hyperparameter
  constants, and import paths must match between patch and foundry.
- 📐 식·표 일치 — formulas and tables cited in the Design or analyses
  must either be implemented in the patch or explicitly deferred to 🚧.

The verifier executes no code beyond `git apply --check`. `partial` is
a normal outcome and far better than a fabricated `pass`.

---

## 7. Changelog

| Version | Date | Change |
|---------|------|--------|
| v1.0 | 2026-04-22 | Initial version — emoji system, link rules, Korean translation principles |
| v1.1 | 2026-05-12 | Schema rename: subsection emoji 🎯 label and Korean glossary updated from `Q# / H#` to `P# / D#` (Pillar + Decision; CP# referenced in body text as needed) |
| v1.2 | 2026-05-19 | Glossary §4-2 extended with canonical terms: System0/System1, structured input-modality binding, VLM pretraining preservation, action expert, flow matching |
| v1.3 | 2026-05-19 | Added §3-1 Reference Legend (cited-code glossary) + in-body `#ref-` anchor links; 🔑 section emoji; KO mirroring rules (§4-1, §4-3) |
| v1.4 | 2026-05-19 | Single Korean file per run named `YYYY-MM-DD-P#.md` (date + pillar); English file retired; Mon & Thu cadence; §1 + §4 reworked from "translation" to direct Korean authoring |
| v1.5 | 2026-05-19 | Scope extended to `analysis/`; added §5 Paper Analysis Document (Korean-single deep-dive, emoji set, body-acquisition honesty); Changelog renumbered §6 |
| v1.6 | 2026-05-19 | Path migration: `research_log/` → `scouting/`, `research_context*.md` → `context/MASTER.md` + `context/P{1..4}.md`; dropped redundant `-KO` filename suffix in `analysis/` (output is always Korean) |
| v1.7 | 2026-05-20 | Added §5-5 (reproduction follow-up line) and new §6 (Paper Reproduction Document — `_impl.md` + `_impl.patch` against `vendor/lerobot/`); introduced section emojis 🧱 🪛 🧪 🚧; Changelog renumbered §7 |
| v1.8 | 2026-05-20 | Scope extended to `experiments/`; added §7 (Experiments Documents — `H###.md` + `I###.md` + `I###.patch` + `V###.md` + `manifest.yaml`); introduced section emojis 📚 🔍 📐 ⚖️; manifest schema + honesty rules (validator never writes `adopted`/`rejected`); Changelog renumbered §8 |
| v1.9 | 2026-05-20 | Added §4-5 — `humanize-korean` post-processing tail step (ported from [`epoko77-ai/im-not-ai`](https://github.com/epoko77-ai/im-not-ai)); every Korean output passes the `ai-tell-detector` → `korean-style-rewriter` → `content-fidelity-auditor` pipeline before commit. PROBE invariants (paper titles, P#/D#/CP# tags, `<a id="ref-…">` anchors, arXiv/DOI links, emoji rules, §4-2 glossary) codified as rollback triggers. §4-4 (Tone and style) deleted — tone, register, rhythm, density, hedging, and visual-ornament rules are now fully delegated to the upstream `humanize-korean` taxonomy; STYLE no longer carries its own tone spec |
| v1.10 | 2026-05-20 | §4-5 pipeline expanded from 3-stage to 4-agent — `naturalness-reviewer` reintroduced as a parallel second-stage check next to `content-fidelity-auditor`. The two reviewers are orthogonal: fidelity guards meaning, naturalness guards "did AI tells actually disappear + was the rewrite not over-polished". Verdict matrix combines both; `rewrite_round_2` / `rollback_and_rewrite` from naturalness triggers up to 2 additional Phase B rounds before `hold_and_report` |
| v1.11 | 2026-05-21 | Two-layer fabless/foundry split: §5-5 now points at `/foundry` (was `/reproduce-paper`); §6 rewritten as Design (Layer 1) + foundry-bound impl (Layer 2) with new emojis 🧮 🧰 ⛓️ 🔌; §7 introduced experiments track at `/hypothesize` → `/foundry` → `/audit` with foundry-keyed `manifest.{implementation,validation}.<foundry>.*` and per-foundry `I###/<foundry>/{impl.md,impl.patch}` + `V###/<foundry>.md` paths; status graduation requires every registered foundry to pass |
| v1.12 | 2026-05-21 | Drop hypothesize/experiments track entirely — `/hypothesize` slash command and `experiments/` folder removed. §7 (Experiments Documents) and `manifest.yaml` schema deleted; §6 reorganised as analysis-only (`/analyze-paper` → `/foundry` → `/audit`) with the audit report (📚 🔍 📐 ⚖️ emojis) folded into §6 as §6-5. Scope tagline now lists `scouting/`, `synthesis/`, `analysis/` only. H### code dropped from verbatim tag list |
| v1.13 | 2026-05-21 | §5-6 rewritten English-default — inline math recipe flipped from `` `$X$` `` (outside dollars; renders as code, KaTeX never runs) to `` $`X`$ `` (inside dollars; GitHub's official escape that lets KaTeX render while suppressing Markdown's italic toggling on `_`). Added inline-math boundary rule: CJK middle-dot `·`, bold marker `*`/`**`, and Hangul syllables touching a `$` are invalid neighbours — separate with whitespace or restructure (`$X$·$Y$` → `$X$ · $Y$`; `**$X$ Y**` → `$X$ **Y**`). Added arXiv figure hotlink + English-caption-verbatim convention (cap 3 per analysis, arXiv HTML host only). §4-5 invariants extended to cover figure hotlinks and their caption blockquotes. New §5-7 codifies the auto-maintained `analysis/README.md` index table refreshed by `scripts/refresh-analysis-index.py` from the GIT step of `/analyze-paper`, `/foundry`, and `/audit` |
| v1.14 | 2026-05-21 | New `/reproduce-paper` orchestrator command (`.claude/commands/reproduce-paper.md` + `.claude/prompts/reproduce-paper.md`) drives `/analyze-paper → /foundry → /audit` as an iterative loop with verdict-cell parsing and honest-partial stable termination. Inner-loop refinement uses `/foundry --feedback <audit-path>` to update the prior round's impl surgically; outer-loop refinement (Design-side update) is deferred — 📚 fail/partial currently exits as `hold_and_report` for manual intervention. `/verify` renamed to `/audit` (noun form); output paths `<id>_verify/` → `<id>_audit/`, template `_TEMPLATE_VERIFY.md` → `_TEMPLATE_AUDIT.md` |
