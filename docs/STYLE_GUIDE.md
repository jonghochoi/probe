# PROBE Style Guide
> **Version:** v1.3 (2026-05-19) · **Scope:** All files under `research_log/`
> This document is the single source of truth for formatting rules.
> Agent reads this file before producing any output. Never modify output format without updating this guide first.

---

## 1. Output File Convention

Every weekly scouting report is produced as **two files**:

| File | Language | Purpose |
|------|----------|---------|
| `research_log/YYYY-WXX.md` | English | Primary record; used by the agent for citation-graph search and future retrieval |
| `research_log/YYYY-WXX-KO.md` | Korean | Human-readable version; produced immediately after the English file |

The English file is always written first. The Korean file is a faithful translation of the English file, produced in the same session.

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
| 🔄 | Week-over-Week Synthesis |

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
- The Korean file uses the **identical** emoji system — emojis are not translated.

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
memorized can decode the report without opening `research_context_P#.md`.

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

**Meaning source** (deterministic — derive from `research_context_P#.md`,
which the agent already reads; do not invent):

| Code | Source in `research_context_P#.md` | Meaning string |
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

## 4. Korean Translation Principles

### 4-1. What to translate vs. keep in English

| Category | Treatment |
|----------|-----------|
| Paper titles | Keep original English title; add Korean description if helpful |
| Technical terms | First occurrence: Korean term + English in parentheses. Subsequent: Korean only |
| Config / code names | Keep verbatim (`env_cfg.py`, `ObservationManager`, etc.) |
| Formulas / numbers | Keep verbatim (`ε = 0.1`, `±2σ`, `< 15%`, etc.) |
| P#, D#, CP# tags | Keep verbatim (`P2`, `D11`, `CP3`, etc.) |
| Reference Legend | Reproduce the section; translate the Meaning column only; codes + `<a id="ref-…">` anchors verbatim |
| Anchor / intra-doc links | Keep `id=` and `[…](#ref-…)` verbatim — KO links resolve within the KO file |
| arXiv links | Keep identical to English version |
| Emojis | Keep identical — same position, same emoji |
| Section headers | Translate header text; keep emoji prefix |

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
| 🔄 Week-over-Week Synthesis | 🔄 주차별 종합 |
| 🎯 (a) P# / D# touched | 🎯 (a) 관련 Pillar / Decision (P# / D#) |
| ✨ (b) What is genuinely new | ✨ (b) 진정으로 새로운 점 |
| ⚙️ (c) Decision implication | ⚙️ (c) 의사결정 함의 |
| ⚠️ (d) Failure mode to probe first | ⚠️ (d) 먼저 검증해야 할 실패 모드 |
| 📌 (sub-sections) | 📌 (동일 주제 한글 번역) |

### 4-4. Tone and style

- Use formal Korean (합니다/됩니다 체).
- Maintain the analytical density of the English version — do not simplify.
- When the English uses bold for emphasis (`**text**`), preserve bold in Korean.
- Code blocks and inline code (`` `text` ``) are preserved unchanged.

---

## 5. Changelog

| Version | Date | Change |
|---------|------|--------|
| v1.0 | 2026-04-22 | Initial version — emoji system, link rules, Korean translation principles |
| v1.1 | 2026-05-12 | Schema rename: subsection emoji 🎯 label and Korean glossary updated from `Q# / H#` to `P# / D#` (Pillar + Decision; CP# referenced in body text as needed) |
| v1.2 | 2026-05-19 | Glossary §4-2 extended with canonical terms: System0/System1, structured input-modality binding, VLM pretraining preservation, action expert, flow matching |
| v1.3 | 2026-05-19 | Added §3-1 Reference Legend (cited-code glossary) + in-body `#ref-` anchor links; 🔑 section emoji; KO mirroring rules (§4-1, §4-3) |
