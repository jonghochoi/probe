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

### 5-5. Reproduction follow-up line

When the analyzed paper builds on one of the six baselines vendored at
`vendor/lerobot/policies/{pi0,pi05,pi0_fast,smolvla,act,diffusion}/`,
the analysis ends with exactly one blockquote line as its very last
line:

```markdown
> 💡 이 논문은 `pi0` 기반으로 보입니다. 구현 가이드는 `/reproduce-paper 2401.12345` 로 생성하실 수 있습니다.
```

`<base>` is the verbatim vendor directory name. If the baseline cannot
be matched to one of the six with reasonable confidence, the line is
omitted — never speculated, never pointed at an outside-of-vendor
baseline.

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

## 6. Paper Reproduction Document (`analysis/<id>_impl.md`)

The `/reproduce-paper` slash command (prompt:
`.claude/prompts/paper-reproduction.md`) consumes an existing
`analysis/<id>.md` and produces two files:

- `analysis/<id>_impl.md`    — Korean reproduction guide.
- `analysis/<id>_impl.patch` — unified diff against `vendor/lerobot/`.

### 6-1. File convention

- Korean single document, written natively per §4 (formal 합니다/됩니다
  체, glossary §4-2, verbatim tokens).
- Filename is the analysis filename with `_impl` appended before the
  extension (`<id>_impl.md`, `<id>_impl.patch`). No language suffix.
- Regenerable snapshot — re-running overwrites both files.
- The document follows `analysis/_TEMPLATE_IMPL.md` exactly. Six `##`
  sections in this order: 📄 가이드 메타, 🧱 베이스 모델 식별, 🪛 변경
  지점 매핑, ⚙️ 핵심 변경 (diff), 🧪 실무 구현 주의, 🚧 미해결 / 잠정.

### 6-2. Emoji system

Same rule as §2: one emoji at the start of each `##` / `###` header,
never in body. Section (`##`) emojis specific to this document type
(added on top of §2 and §5-2):

| Emoji | Section |
|-------|---------|
| 📄 | 가이드 메타 |
| 🧱 | 베이스 모델 식별 |
| 🪛 | 변경 지점 매핑 |
| ⚙️ | 핵심 변경 (diff) |
| 🧪 | 실무 구현 주의 |
| 🚧 | 미해결 / 잠정 |

📄 and ⚙️ are reused from §5-2 / §2-2 — same emoji, document-local
meaning. 🧱 🪛 🧪 🚧 are introduced by this section and used nowhere
else in PROBE outputs.

### 6-3. Vendor coordinate rule

Every code reference points inside `vendor/lerobot/` and follows the
form `vendor/lerobot/policies/<base>/<file>:<line>` (line numbers
optional but recommended). Coordinates are bound to the pinned commit
recorded in `vendor/lerobot/README.md` — the guide's 📄 가이드 메타
table MUST cite the same SHA. Bumping the snapshot invalidates every
existing `_impl.patch`; see `vendor/lerobot/README.md` for the refresh
procedure.

### 6-4. Honesty rules carried over

- If `analysis/<id>.md` was produced from abstract-only, every guide
  `##` section first line is prefixed **(본문 미확보 — 잠정)** and
  no patch file is produced — only the markdown.
- If `git apply --check` fails on the generated patch, the failure is
  recorded verbatim in the 📄 가이드 메타 table and at the end of
  ⚙️ 핵심 변경 (diff). Affected hunks are downgraded to 🪛 + 🚧 entries
  instead of being silently forged.
- If the paper's baseline cannot be matched to one of the six vendored
  policies, **neither** `_impl.md` nor `_impl.patch` is produced. The
  agent appends one line to `analysis/<id>.md`:
  `> 🚧 재현 가이드 미생성 — 베이스 모델이 vendor 범위 밖입니다.`

---

## 7. Experiments Documents (`experiments/`)

The `/hypothesize`, `/implement-hypothesis`, and `/validate-hypothesis`
slash commands (prompts: `.claude/prompts/hypothesize.md` ·
`implement-hypothesis.md` · `validate-hypothesis.md`) produce a
hypothesis-implementation-validation cycle under
`experiments/H###-<slug>/`.

### 7-1. File convention

- **Korean single documents.** Like every other PROBE output,
  `H###.md`, `I###.md`, and `V###.md` are single Korean documents —
  written natively per §4 (tone, glossary, verbatim tokens). No
  English-primary file. No language suffix on the filename.
- Folder name: `experiments/H###-<slug>/` — `H###` is zero-padded to
  three digits and the slug is kebab-case ASCII derived from the
  hypothesis title (or supplied by the human at `/hypothesize` time).
  The same numeric ID is reused for `I###`, `I###.patch`, and `V###`
  inside that folder.
- `H###.md` is **immutable** once written by `/hypothesize` (the only
  later addition is a single 🚧 blockquote line if
  `/implement-hypothesis` finds the baseline out-of-vendor). To revise
  a hypothesis, start a new `H###`.
- `I###.md` + `I###.patch` are **regenerable snapshots** — re-running
  `/implement-hypothesis` overwrites both.
- `V###.md` is a **regenerable snapshot** — re-running
  `/validate-hypothesis` overwrites it.
- `manifest.yaml` is the **only** jointly written file: agents update
  `validation.*`, `implementation.*`, and (when all checks pass)
  `status: draft → validated`. The transitions `→ adopted` and
  `→ rejected` plus the `adopted:` date are **human-only**.
- The `experiments/` folder follows `_TEMPLATE_H.md` / `_TEMPLATE_I.md`
  / `_TEMPLATE_V.md` exactly.

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
| `implementation.patch` | string / null | `I###.patch` once `/implement-hypothesis` runs |
| `implementation.apply_check` | string / null | `pass` / `fail — <stderr first line>` / `n/a — base out of vendor` |
| `validation.literature` | enum / null | `pass` / `fail` / `partial` |
| `validation.patch_consistency` | enum / null | `pass` / `fail` |
| `validation.signature_check` | enum / null | `pass` / `fail` / `partial` |

`relations` must be non-empty — every hypothesis has at least one
stated relationship to a Decision. `null` (not `~`, not empty string)
is used for fields not yet known.

### 7-4. Honesty rules carried over

- If `git apply --check` fails for `I###.patch`, the failure is
  recorded verbatim in `I###.md` 📄 가이드 메타 + `manifest.yaml`
  `implementation.apply_check`, and `/validate-hypothesis` records it
  again under V###.md §🔍 with the live re-run output. Affected hunks
  are downgraded to 🪛 + 🚧 entries in `I###.md` — never silently
  forged. **A `patch_consistency: fail` blocks `status` graduation,
  regardless of literature/signature outcomes.**
- The validator (`/validate-hypothesis`) only graduates
  `draft → validated`. It NEVER writes `adopted` or `rejected`. A
  `manifest.status: adopted` written by an agent is a bug — those
  values exist solely so the human can mark a hypothesis as decided.
- Hypotheses sourced from a Pillar code (`P#`) carry an empty
  `related_analyses: []`. Validation `literature` is `pass` only when
  the hypothesis explicitly identifies itself as pillar-internal (no
  paper claimed); a paper-implying hypothesis with no analyses is
  `partial`, not `pass`.

### 7-5. Korean & verbatim rules

§4 applies in full. Specifically: original English paper title (when
cited in `H###.md` ✨ 핀 논문 대비 델타 or `V###.md` 📚 문헌 대조),
config/code names, `file:line` coordinates, formulas, arXiv links, and
`P#`/`D#`/`CP#`/`H###` codes are kept verbatim; technical terms use
the §4-2 glossary; tone is formal 합니다/됩니다 체.

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
