# PROBE Style Guide
> **Version:** v1.10 (2026-05-20) · **Scope:** All files under `scouting/`, `analysis/`, and `experiments/`
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

Every Korean output in PROBE (`scouting/`, `synthesis/`, `analysis/`,
`experiments/`) passes through the `humanize-korean` skill
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
regardless of what the authoring agent produced. STYLE_GUIDE no longer
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
- `P#` / `D#` / `CP#` / `H###` tags
- `<a id="ref-…">` anchors and `[CODE](#ref-CODE)` intra-doc links
- arXiv / DOI links
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

### 5-6. 원문 인용 · 개조식 · 키워드 규약

방법론(🔬)·실험 결과(📊) 섹션은 본문 근거를 추적 가능하게 두고,
문제 정의(❓)·기술 키워드(🔑) 섹션은 스캔성을 높이기 위해 다음
규약을 따릅니다.

- **원문 blockquote 인용** — 핵심 설계 문장(앵커 클레임), 모든 수식,
  핵심 수치 주장은 `>` blockquote 에 영문 원문을 verbatim 으로 두고
  바로 아래 줄에 한글 해설을 답니다. 형식 고정:

  ```markdown
  > "We model the action distribution with conditional flow matching." (§3.2)
  (한글 해설 — 이 문장이 왜 핵심인지.)
  ```

  출처 표기는 `(§n)` 또는 `(§n, Table k)`. 본문에서 절 번호가
  식별되지 않으면 `(§?)` 로 두고 추정하지 않습니다. 영문은 절대
  paraphrase 하지 않으며, `humanize-korean` 패스도 이 blockquote
  내부를 verbatim 토큰으로 취급해 손대지 않습니다(§4-5 invariants
  확장).

- **수식 verbatim + GitHub KaTeX 렌더링** — LaTeX/유니코드 표기를
  원문 그대로 유지하며, paraphrase·기호 치환·줄임 금지. 변수 정의는
  본문 표기와 일치시킵니다. github.com 의 Markdown 렌더러는
  2022-05 부터 KaTeX 를 지원하므로, 본문에 넣는 수식은 다음 표기로
  감쌉니다 — inline 은 `$…$`, display 는 별도 줄의 `$$…$$`.
  `\(…\)` / `\[…\]` 는 GitHub 에서 렌더링되지 않으므로 사용하지
  않습니다. arXiv HTML(LaTeXML) 본문에서 수식을 가져올 때는 다음
  절차로 변환합니다.

  1. `<math display="inline" … alttext="X">` → `` `$X$` `` — inline
     수식은 **반드시 백틱으로 감싼 `` `$X$` `` 형태**로 적습니다.
     GitHub Markdown 파서가 KaTeX 보다 먼저 동작하면서 `$…$` 안의
     `_` 를 italic 으로 잘라먹는 알려진 한계를 우회하기 위함입니다
     (`x_{t}` 같은 첨자가 거의 모든 식에 등장하므로 사실상 모든
     inline 식에 적용). GitHub 공식 권장 표기입니다.
  2. `<math display="block" … alttext="X">` 또는 `class="ltx_equation*"`
     컨테이너 안쪽의 alttext → 별도 줄의 `$$X$$`. 선행 `\displaystyle`
     과 후행 콤마는 제거할 수 있습니다. display 는 블록으로 인식되어
     underscore 문제가 없으므로 백틱이 필요하지 않습니다.
  3. HTML 엔티티 디코딩 — `&gt;` → `>`, `&lt;` → `<`, `&amp;` → `&`.
  4. KaTeX 미지원 매크로(`\bm`, 일부 `\xrightarrow` 변형, 저자 정의
     `\newcommand` 등)는 임의 치환 금지. 그대로 두면 GitHub 에서 빨간
     에러로 표시되며, 이는 정직성 원칙(§5-4)에 부합합니다.
  5. 본문 산문에 일반 달러 기호가 등장하면 `\$` 로 escape 해 수식
     시작으로 오해되지 않도록 합니다.

- **개조식(❓ 문제 정의 / 동기)** — 단일 산문 문단을 쓰지 않고 4–6
  항목의 굵은 라벨 + 1–2문장 형태로 작성합니다. 권장 라벨:
  `풀고자 하는 문제`, `기존 접근의 한계`, `본 논문의 가설`,
  `왜 지금 중요한가`.

- **🔑 기술 키워드** — 본 논문 이해에 필요한 핵심 용어 5–10개를
  `- **<원어 / 약어>** — <비유적 한 줄 설명>` 형식으로 정리합니다.
  §4-2 글로서리에 등재된 용어는 글로서리 번역을 그대로 사용하되,
  비유 한 줄을 곁들입니다. 비유는 사실 왜곡이 없는 선에서만
  허용되며, 적절한 비유가 없으면 평이한 정의로만 적습니다.

- **방법론 분해** — 🔬 방법론 은 가능하면 `### 직관`, `### 아키텍처`,
  `### 학습 목표 / 손실`, `### 학습 셋업` 4 하위절로 분해해 디테일
  보존을 우선합니다. `### ` 하위 헤더에는 이모지를 두지 않습니다
  (§2 의 H3 plain 규칙과 동일).

---

## 6. Design + Foundry Implementation Documents

The `/analyze-paper` and `/hypothesize` slash commands emit a **Layer 1
Design** (vendor-agnostic) alongside the analysis or hypothesis. The
`/foundry` slash command (prompt: `.claude/prompts/foundry.md`)
consumes that Design and produces a **Layer 2** foundry-specific
implementation. The two-layer split exists so the same Design can
serve multiple foundries (the v0 foundry is `lerobot`).

Outputs per track:

- 논문 트랙:
  - `analysis/<id>_design.md`                  — Layer 1 Design.
  - `analysis/<id>_impl/<foundry>/impl.md`     — Korean impl guide.
  - `analysis/<id>_impl/<foundry>/impl.patch`  — unified diff against
                                                 the foundry's code
                                                 root (for lerobot:
                                                 `vendor/lerobot/`).
- 가설 트랙:
  - `experiments/H###-*/D###.md`               — Layer 1 Design.
  - `experiments/H###-*/I###/<foundry>/impl.md` + `impl.patch`.

### 6-1. File convention

- Korean single document, written natively per §4 (formal 합니다/됩니다
  체, glossary §4-2, verbatim tokens).
- Filenames: see the per-track paths above. No language suffix.
- Both Design and impl are **regenerable snapshots** — re-running the
  generator overwrites them.
- The Design document follows `analysis/_TEMPLATE_DESIGN.md` (논문) or
  `experiments/_TEMPLATE_D.md` (가설) — 9 `##` sections in this order:
  📄 메타, 🧮 데이터 계약, 🧰 모듈 인터페이스, ⛓️ 불변식·가정,
  📊 하이퍼파라미터·손실, 🎯 평가 메트릭, ✨ 변경 의도, 🔌 Foundry
  힌트, 🚧 미해결 / 잠정.
- The impl document follows `analysis/_TEMPLATE_IMPL.md` (or
  `experiments/_TEMPLATE_I.md`) exactly. Six `##` sections in this
  order: 📄 가이드 메타, 🧱 베이스 / 코드 좌표 식별, 🪛 변경 지점
  매핑, ⚙️ 핵심 변경 (diff), 🧪 실무 구현 주의, 🚧 미해결 / 잠정.

### 6-2. Emoji system

Same rule as §2: one emoji at the start of each `##` / `###` header,
never in body. Section (`##`) emojis specific to this document family
(added on top of §2 and §5-2):

| Emoji | Section | Document |
|-------|---------|----------|
| 📄 | Design 메타 · 가이드 메타 | Design · impl (reused from §5-2) |
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
| 🧪 | 실무 구현 주의 | impl |
| 🚧 | 미해결 / 잠정 | Design · impl |

🧮 🧰 ⛓️ 🔌 are introduced by this section (Design). 🧱 🪛 🧪 are
introduced for impl. 🚧 is reused across both. None appear elsewhere
in PROBE outputs outside §6 and §7.

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
  down is left as `(원문에 명시 없음 — 가정으로 메움)` (논문 트랙) or
  `(가설에 명시 없음 — 가정으로 메움)` (가설 트랙).
- If `git apply --check` fails on the generated patch, the failure is
  recorded verbatim in the 📄 가이드 메타 table and at the end of
  ⚙️ 핵심 변경 (diff). Affected hunks are downgraded to 🪛 + 🚧 entries
  instead of being silently forged.
- If the Design cannot ground in the target foundry, **neither**
  `impl.md` nor `impl.patch` is produced. Instead `/foundry` writes
  `<impl-root>/<foundry>/UNMAPPABLE.md` with one paragraph of reason,
  and appends one line to the originating document
  (`analysis/<id>.md` or `experiments/H###-*/H###.md`):
  `> 🚧 매핑 불가 (<foundry>) — Design 의 일부가 이 foundry 의 좌표계로 매핑되지 않습니다.`

---

## 7. Experiments Documents (`experiments/`)

The `/hypothesize`, `/foundry`, and `/verify` slash commands (prompts:
`.claude/prompts/hypothesize.md` · `foundry.md` · `verify.md`) produce
a hypothesis-design-implementation-validation cycle under
`experiments/H###-<slug>/`. Design + impl formats are governed by §6;
this section covers the experiments-specific lifecycle and the
validation report.

### 7-1. File convention

- **Korean single documents.** Like every other PROBE output,
  `H###.md`, `D###.md`, `I###/<foundry>/impl.md`, and
  `V###/<foundry>.md` are single Korean documents — written natively
  per §4 (tone, glossary, verbatim tokens). No English-primary file.
  No language suffix on the filename.
- Folder name: `experiments/H###-<slug>/` — `H###` is zero-padded to
  three digits and the slug is kebab-case ASCII derived from the
  hypothesis title (or supplied by the human at `/hypothesize` time).
  The same numeric ID is reused for `D###`, `I###`, and `V###` inside
  that folder. Per-foundry impl/verify outputs live one level deeper
  under `I###/<foundry>/` and `V###/<foundry>.md`.
- `H###.md` and `D###.md` are **immutable** once written by
  `/hypothesize` (the only later addition is a single 🚧 blockquote
  line on `H###.md` if `/foundry` finds the Design unmappable for
  some foundry). To revise a hypothesis, start a new `H###`.
- `I###/<foundry>/impl.md` + `impl.patch` are **regenerable
  snapshots** — re-running `/foundry --foundry <name>` overwrites both
  for that foundry only. Other foundries' outputs are untouched.
- `V###/<foundry>.md` is a **regenerable snapshot** — re-running
  `/verify --foundry <name>` overwrites it.
- `manifest.yaml` is the **only** jointly written file: agents update
  foundry-keyed `implementation.<foundry>.*` and
  `validation.<foundry>.*`, and graduate `status: draft → validated`
  only when **every registered foundry** has all three validation
  checks at `pass`. The transitions `→ adopted` and `→ rejected` plus
  the `adopted:` date are **human-only**.
- The `experiments/` folder follows `_TEMPLATE_H.md` / `_TEMPLATE_D.md`
  / `_TEMPLATE_I.md` / `_TEMPLATE_V.md` exactly.

### 7-2. Emoji system

Same rule as §2: one emoji at the **start** of each `##` / `###`
header, never in body text. Section (`##`) emojis specific to this
document family (added on top of §2, §5-2, §6-2):

| Emoji | Section | Document |
|-------|---------|----------|
| 📄 | 가설 메타 · 가이드 메타 · 검증 메타 | H · I · V (reused from §5-2 / §6-2) |
| 🧭 | 한 줄 요약 (TL;DR) | H (reused from §5-2) |
| ❓ | 출발 갭 | H (reused from §5-2) |
| 🧩 | 가설 진술 | H (reused from §5-2) |
| 🔬 | Falsifiable Test 설계 | H (reused from §5-2) |
| 🎯 | 관련 Pillar / Decision (P# / D#) | H (reused from §5-2 / §2-2) |
| ✨ | 핀 논문 대비 델타 | H (reused from §5-2 / §2-2) |
| ⚠️ | 먼저 검증할 실패 모드 | H (reused from §5-2 / §2-2) |
| 💡 | 컨텍스트 제안 · 후속 호출 안내 | H · V (reused from §5-2 / §2-1) |
| 🧱 | 베이스 모델 식별 | I (reused from §6-2) |
| 🪛 | 변경 지점 매핑 | I (reused from §6-2) |
| ⚙️ | 핵심 변경 (diff) | I (reused from §6-2) |
| 🧪 | 실무 구현 주의 · 시그니처·하이퍼파라미터 일치 | I · V (reused from §6-2) |
| 🚧 | 미해결 / 잠정 | I · V (reused from §6-2) |
| 📚 | 문헌 대조 | V (new) |
| 🔍 | 패치 정합성 | V (new) |
| 📐 | 식·표 일치 | V (new) |
| ⚖️ | 종합 판정 | V (new) |

📚 🔍 📐 ⚖️ are introduced by this section and used nowhere else in
PROBE outputs. Do not use any emoji not listed in §2, §5, §6, or here.

### 7-3. `manifest.yaml` schema

`manifest.yaml` is YAML with two-space indentation, no surrounding
fences. Field enums (verbatim values only):

| Field | Type | Allowed values |
|-------|------|----------------|
| `id` | string | `H###` (3-digit zero-padded) |
| `pillar` | string | `P1` / `P2` / `P3` / `P4` |
| `slug` | string | kebab-case ASCII, 2–5 words |
| `title` | string | one-line; may contain Korean |
| `status` | enum | `draft` / `validated` / `adopted` / `rejected` |
| `created` | date | `YYYY-MM-DD` (`TZ=Asia/Seoul`) |
| `adopted` | date / null | `YYYY-MM-DD` once human transitions to `adopted`; `null` otherwise |
| `related_decisions` | list of strings | `[D#, D#, …]` — codes that actually exist in `context/MASTER.md` §6 |
| `related_analyses` | list of strings | `[<arxiv-id>, …]` — slugs of existing `analysis/<id>.md` files; `[]` if none |
| `related_baseline` | enum / null | `pi0` / `pi05` / `pi0_fast` / `smolvla` / `act` / `diffusion` / `null` |
| `relations[].kind` | enum | `supports` / `conflicts` / `extends` / `refines` |
| `relations[].target` | string | a `D#` or another `H###` |
| `implementation` | map | foundry-keyed dict. Each subkey is a foundry name (e.g. `lerobot`); `/foundry` adds one entry per run. |
| `implementation.<foundry>.patch` | string | `I###/<foundry>/impl.patch` once `/foundry --foundry <foundry>` runs |
| `implementation.<foundry>.apply_check` | string | `pass` / `fail — <stderr first line>` / `n/a — unmappable` |
| `validation` | map | foundry-keyed dict. Each subkey is a foundry name; `/verify` adds one entry per run. |
| `validation.<foundry>.literature` | enum | `pass` / `fail` / `partial` |
| `validation.<foundry>.patch_consistency` | enum | `pass` / `fail` / `partial` |
| `validation.<foundry>.signature_check` | enum | `pass` / `fail` / `partial` |

`relations` must be non-empty — every hypothesis has at least one
stated relationship to a Decision. `null` (not `~`, not empty string)
is used for fields not yet known.

### 7-4. Honesty rules carried over

- If `git apply --check` fails for `I###/<foundry>/impl.patch`, the
  failure is recorded verbatim in that impl.md 📄 가이드 메타 +
  `manifest.implementation.<foundry>.apply_check`, and `/verify`
  records it again under `V###/<foundry>.md` §🔍 with the live re-run
  output. Affected hunks are downgraded to 🪛 + 🚧 entries in impl.md
  — never silently forged. **A `patch_consistency: fail` for any
  registered foundry blocks `status` graduation, regardless of
  literature/signature outcomes on other foundries.**
- The verifier (`/verify`) only graduates `draft → validated`, and
  only when **every registered foundry** has all three checks at
  `pass`. A single foundry passing is not enough. The verifier NEVER
  writes `adopted` or `rejected`. A `manifest.status: adopted`
  written by an agent is a bug — those values exist solely so the
  human can mark a hypothesis as decided.
- Hypotheses sourced from a Pillar code (`P#`) carry an empty
  `related_analyses: []`. Validation `literature` is `pass` only when
  the hypothesis explicitly identifies itself as pillar-internal (no
  paper claimed); a paper-implying hypothesis with no analyses is
  `partial`, not `pass`.

### 7-5. Korean & verbatim rules

§4 applies in full. Specifically: original English paper title (when
cited in `H###.md` ✨ 핀 논문 대비 델타 or `V###/<foundry>.md` 📚 문헌
대조), config/code names, `file:line` coordinates, formulas, arXiv
links, and `P#`/`D#`/`CP#`/`H###` codes are kept verbatim; technical
terms use the §4-2 glossary; tone is formal 합니다/됩니다 체.

---

## 8. Changelog

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
| v1.9 | 2026-05-20 | Added §4-5 — `humanize-korean` post-processing tail step (ported from [`epoko77-ai/im-not-ai`](https://github.com/epoko77-ai/im-not-ai)); every Korean output passes the `ai-tell-detector` → `korean-style-rewriter` → `content-fidelity-auditor` pipeline before commit. PROBE invariants (paper titles, P#/D#/CP#/H### tags, `<a id="ref-…">` anchors, arXiv/DOI links, emoji rules, §4-2 glossary) codified as rollback triggers. §4-4 (Tone and style) deleted — tone, register, rhythm, density, hedging, and visual-ornament rules are now fully delegated to the upstream `humanize-korean` taxonomy; STYLE_GUIDE no longer carries its own tone spec |
| v1.10 | 2026-05-20 | §4-5 pipeline expanded from 3-stage to 4-agent — `naturalness-reviewer` reintroduced as a parallel second-stage check next to `content-fidelity-auditor`. The two reviewers are orthogonal: fidelity guards meaning, naturalness guards "did AI tells actually disappear + was the rewrite not over-polished". Verdict matrix combines both; `rewrite_round_2` / `rollback_and_rewrite` from naturalness triggers up to 2 additional Phase B rounds before `hold_and_report` |
| v1.11 | 2026-05-21 | Two-layer fabless/foundry split: §5-5 now points at `/foundry` (was `/reproduce-paper`); §6 rewritten as Design (Layer 1) + foundry-bound impl (Layer 2) with new emojis 🧮 🧰 ⛓️ 🔌; §7 retargeted at `/hypothesize` → `/foundry` → `/verify` with foundry-keyed `manifest.{implementation,validation}.<foundry>.*` and per-foundry `I###/<foundry>/{impl.md,impl.patch}` + `V###/<foundry>.md` paths; status graduation now requires every registered foundry to pass |
