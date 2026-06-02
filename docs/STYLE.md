# PROBE Style Guide
> **Version:** v1.20 (2026-06-01) · **Scope:** All files under `scouting/`, `synthesis/`, and `analysis/`
> This document is the single source of truth for formatting rules.
> Agent reads this file before producing any output. Never modify output format without updating this guide first.

---

## 1. Output File Convention

The scouting routine runs **twice a week (Monday & Thursday)**, once per
pillar. Each run produces **one Korean file**:

| File | Language | Purpose |
|------|----------|---------|
| `scouting/P#/YYYY-MM-DD.md` | Korean | The scouting report. `P#` is the pillar (P1–P4); `YYYY-MM-DD` is the run date. The agent reads sibling files in the same `P#/` folder for de-duplication. |

The report is written directly in Korean (no separate English file).
Paper titles, arXiv links, and `P#/D#` tags stay verbatim in their
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
`P#` / `D#` codes, so a reader who does not have the codes memorized can
decode the report without opening `context/P#.md`.

**Scope.** Only `P#` (Pillar) and `D#` (Decision) codes.
**Only codes actually cited in this report.** Never list a code the body
does not use; never list competitor codenames, Identity, or the falsifier.

**Placement.** A single `## 🔑 Reference Legend` section, immediately
after the top intro blockquote and immediately before `## 📋 Scout
Methodology`. It is the first content section of the report.

**Format.** One compact table, rows ordered `P#` → `D#` (ascending),
one row per distinct cited code:

```markdown
## 🔑 Reference Legend

| Code | Meaning |
|------|---------|
| <a id="ref-P1"></a>**P1** | Heterogeneous Body/Hand Action Expert (pillar) |
| <a id="ref-D4"></a>**D4** | Body↔Hand information sharing — v1 FiLM; cross-attn/hidden-state deferred |
```

If the body cites no such code (rare), omit the section entirely.

**Meaning source** (deterministic — derive from `context/P#.md`,
which the agent already reads; do not invent):

| Code | Source in `context/P#.md` | Meaning string |
|------|-----------------------------------|----------------|
| `P#` | §2 heading `Pillar P# — <name>` | `<name>` + `(pillar)` |
| `D#` | §4 `#### [D#] <title>` + its v1 line | `<title>` — v1 choice in ≤ ~12 words |

**Anchor convention.** Each legend row carries an explicit HTML anchor
`<a id="ref-<CODE>"></a>` placed before the bold code. `<CODE>` is the
verbatim code (`P1`, `D4` — case preserved; GitHub matches explicit
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
| P#, D# tags | Keep verbatim (`P2`, `D11`, etc.). |
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

Every Korean output (`scouting/`, `synthesis/`, `analysis/`) passes through
the `humanize-korean` skill (`.claude/skills/humanize-korean/SKILL.md`)
immediately before `git add` — the LAST step, never before the file is
finished. It rewrites "AI tell" patterns (translation-ese, mechanical
parallelism, signature phrases, hedging, formal-noun / visual-ornament
overuse; taxonomy categories A·C·D·E·F·G·H·I·J) into natural Korean and
normalizes register to formal 합니다/됩니다. **Content is never touched.**
This subsection is the SSOT — it overrides the skill's upstream taxonomy /
playbook on conflict, and is the single place to edit if the register changes.

**Invariants — `content-fidelity-auditor` rolls back on any violation.**
Anything that changes meaning (facts, numbers, dates, quotations, citation
polarity, causal direction, 단정↔추측, enumeration order, added/omitted info)
is forbidden, plus these PROBE-specific tokens:

- Paper titles in original English (§4-1); config / code names; formulas and numbers (`ε = 0.1`, `±2σ`).
- Inline-math wrapping — every `$...$` span (incl. inside English verbatim blockquotes) must use `` $`X`$ `` and satisfy the §5-6 boundary rule; `` `$X$` `` or unguarded `$X$` is a fidelity fail. Also enforced by CI (`scripts/check-analysis-math.py`).
- `P#` / `D#` tags; `<a id="ref-…">` anchors and `[CODE](#ref-CODE)` links; arXiv / DOI links.
- arXiv figure hotlinks + their English caption blockquotes (§5-6).
- Emoji set / position + one-emoji-per-header (§2); §4-2 glossary translations (no resynonymization).

**Operational guards.** Change rate `>30%` → auto rework round; `>50%` →
abort, keep original. `fidelity_audit: fail` → roll back to pre-humanize content.

**Pipeline (3 tiers, auto-resolved from path).** `scouting/` → fast,
`synthesis/` · `analysis/` → standard; `strict` only via `options.mode: strict`.
Invariants above are enforced identically in all tiers.

- **fast** — `ai-tell-detector` (Haiku) → `korean-style-rewriter` (Sonnet `--conservative`) → inline regex invariant check. Loop cap 1.
- **standard** — `ai-tell-detector` (Sonnet) → `korean-style-rewriter` (Opus) → `content-fidelity-auditor` (Opus), with `naturalness-reviewer` (Opus) once at the end. Loop cap 2.
- **strict** — `ai-tell-detector` → `korean-style-rewriter` → [`content-fidelity-auditor` ∥ `naturalness-reviewer`]. Loop cap 3, all Opus.

The two reviewers are orthogonal — fidelity guards meaning, naturalness guards
"did the AI tells disappear without over-polishing". `fail` rolls back;
`rewrite_round_2` / `rollback_and_rewrite` triggers another pass within the
loop cap, then `hold_and_report` for human review.

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
config/code names, formulas, arXiv links, and `P#`/`D#` tags
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
> 💡 base 매핑은 `/implement-design analysis/2401.12345/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
```

`/implement-design` itself decides whether the Design can be grounded in the
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
  LaTeX / Unicode notation; no paraphrase, symbol substitution, or
  shortening, and variable definitions match the source body. The
  normative rules (github.com renders KaTeX since 2022-05):

  - **Inline** uses `` $`X`$ `` — backticks INSIDE the dollars. The
    outside-dollar `` `$X$` `` (becomes inline code, KaTeX never runs)
    and `\(…\)` / `\[…\]` (do not render on GitHub) are FORBIDDEN.
    Why: Markdown's italic pass runs before KaTeX and eats the `_` in
    subscripts unless the backtick form shields it.
  - **Display** is `$$X$$` on its own line (no backticks).
  - **Boundary** — an inline `$` must not touch a Hangul / CJK syllable,
    middle-dot `·`, or bold marker `*` / `**`; separate with a space (or
    move the math outside the bold), or the delimiter goes invisible and
    the source leaks. A literal `$` in prose is escaped `\$`.
  - **Macro whitelist (the only sanctioned auto-substitutions)** —
    `\bm{X}` → `\mathbf{X}`, and `\mathds{X}` → `\mathbb{X}` (`\mathds`
    is not a KaTeX control sequence and otherwise fails the whole span;
    `\mathbb` is the identical double-stroke glyph). Leave every other
    unsupported macro as-is so the render failure is visible (§5-4).
    Extend this list only by editing this rule.
  - The same wrapping + boundary apply to inline math **inside English
    verbatim blockquotes** — the quoted text stays byte-identical; the
    `$` delimiters are GitHub-rendering formatting, a separate concern.

  The full arXiv-HTML → Markdown extraction procedure lives in
  `.claude/prompts/analysis.md`; PR-time enforcement and auto-fix is
  `scripts/check-analysis-math.py`
  (`.github/workflows/check-analysis-math.yml`). This subsection is the
  SSOT for the rules above — the prompt and the CI implement them.

- **Bullet form (❓ 문제 정의 / 동기)** — Do not write a single
  paragraph. Use 4–6 items, each a bold label + 1–2 sentences.
  Recommended Korean labels (verbatim): `풀고자 하는 문제`,
  `기존 접근의 한계`, `본 논문의 가설`, `왜 지금 중요한가`.

- **🔑 기술 키워드** — 5–10 key terms needed to read the paper,
  each formatted as `- **<original / abbrev>** — <one-line analogy
  or plain definition>`. **The bold head term MUST be a plain English
  word or abbreviation** (the paper's original term); any Korean gloss
  goes only *after* the em dash, never in the head, and math notation
  (`$…$`, LaTeX) belongs in the definition, not the head. This is
  load-bearing — the head is lifted into the `analysis/INDEX.md` keyword
  badges (§5-7), which drop any head that is non-English or math-bearing,
  so a math-symbol keyword (e.g. `$`\pi_0`$`) simply won't surface there.
  For terms in the
  §4-2 glossary, still lead with the English original (glossary
  translation may follow the em dash) and add a short analogy.
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
  - The English caption blockquote is a verbatim token (§4-5
    invariants extension); the humanize-korean pass leaves it
    untouched.
  - Abstract-only acquisition, or a non-arXiv-HTML source
    (PDF-only), means no figure URLs are available — omit the
    figure citations entirely. No placeholders, no guessing.
  - Cap: never more than 3 figures per analysis. This is a decision
    tool, not a slide deck.

### 5-7. Auto-maintained analysis index

`analysis/INDEX.md` is generated by `scripts/refresh-analysis-index.py`,
which rewrites only the block between `<!-- ANALYSIS_INDEX:START -->` /
`<!-- ANALYSIS_INDEX:END -->` — do not hand-edit inside the markers; the
rest of the file is hand-maintained. It runs **post-merge on `main`
only**; the per-command prompts (`/analyze-paper`, `/implement-design`,
`/validate-impl`) do NOT stage `INDEX.md` or invoke the script. The *why*
(parallel-PR conflict, the workflow) is in `CLAUDE.md`
"Automatically-maintained indexes".

The generated table sorts by `Refreshed` desc (ties by arXiv id desc) and
carries, per row:

- an `arXiv` cell rendered as a red shields.io badge linking to the abs page —
  `[![arXiv](https://img.shields.io/badge/arXiv-<id>-b31b1b.svg)](https://arxiv.org/abs/<id>)`;
- a `Keywords` cell — up to 5 `🔑 기술 키워드` head terms, each a colored
  shields.io badge. English plain text only: a head carrying any math (inline
  KaTeX / LaTeX / backticks) is excluded outright, and a head with no
  recoverable English is dropped (§5-6 enforces English heads); skipped heads
  are backfilled from later bullets. Badge colors are the fixed 빨주노초파
  five-color palette assigned **sequentially by position** — badge #1 red, #2
  orange, #3 yellow, #4 green, #5 blue (3 keywords → 빨주노). GitHub's Markdown
  sanitizer strips inline CSS (`<span style=…>`), so a shields.io badge is the
  only way to color text per keyword on github.com;
- an `impl` cell — lerobot-based: ✅ `impl/lerobot/impl.md` exists /
  🚧 `UNMAPPABLE.md` / `—` not generated.

**Load-bearing — the 📄 논문 메타 rows the script reads from every
`analysis/<id>/analysis.md`** (STYLE's contract; the author must emit them
exactly):

| Row label | Required format |
|---|---|
| `원문 제목 (영문)` | Plain English title |
| `링크` | `[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX)` |
| `분석 생성일` | `YYYY-MM-DD` |

A missing / malformed row yields `⚠️ metadata` in that cell rather than an
abort. The `🔑 기술 키워드` bullet heads are load-bearing too: the index reads
each bullet's term — the text before the em dash in the `- **<term>** — …`
shape §5-6 mandates (it also tolerates a `: ` separator and caps long heads).
`python3 scripts/refresh-analysis-index.py` by hand is safe and idempotent.

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
  sections in this order: 📄 메타, 🧮 데이터 계약, 🧰 모듈 인터페이스,
  ⛓️ 불변식·가정, 📊 하이퍼파라미터·손실, 🎯 평가 메트릭, ✨ 변경
  의도, 🔌 Foundry 힌트, 🚧 미해결 / 잠정.
- The impl document follows `analysis/templates/impl.md` exactly. Six
  `##` sections in this order: 📄 가이드 메타, 🧱 베이스 / 코드 좌표
  식별, 🪛 변경 지점 매핑, ⚙️ 핵심 변경 (diff), 🧪 실무 구현 주의,
  🚧 미해결 / 잠정.
- The validation report follows `analysis/templates/validation.md` — six `##`
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

- If `analysis/<id>/analysis.md` was produced from abstract-only,
  every Design section is prefixed **(본문 미확보 — 잠정)** and most
  fields will be `(원문에 명시 없음 — 가정으로 메움)`. The impl document,
  when generated, also prefixes every `##` section first line with
  **(본문 미확보 — 잠정)** and no patch file is produced — only the
  markdown.
- Sparse Design > fabricated Design. Any field the source does not pin
  down is left as `(원문에 명시 없음 — 가정으로 메움)`.
- If `git apply --check` fails on the generated patch, the failure is
  recorded verbatim in the 📄 가이드 메타 table and at the end of
  ⚙️ 핵심 변경 (diff). Affected hunks are downgraded to 🪛 + 🚧 entries
  instead of being silently forged.
- If the Design cannot ground in the target foundry, **neither**
  `impl.md` nor `impl.patch` is produced. Instead `/implement-design` writes
  `analysis/<id>/impl/<foundry>/UNMAPPABLE.md` with one paragraph of
  reason, and appends one line to `analysis/<id>/analysis.md`:
  `> 🚧 매핑 불가 (<foundry>) — Design 의 일부가 이 foundry 의 좌표계로 매핑되지 않습니다.`

### 6-5. Verify report (`/validate-impl` output)

The validation report is the static check of a Design + foundry patch
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
