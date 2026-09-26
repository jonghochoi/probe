# Probe 스카우트 리포트 — YYYY-MM-DD · Pillar P#

<!-- Exactly these two lines — AUTHORING §6. -->
**Papers scanned:** <citation-graph N편> + <keyword sweep M편(14일 K편)>
**Papers surfaced (4축 게이트 통과):** <count>

---

## 🔑 참조 약어 풀이

<!-- AUTHORING §3-1. Only the codes this report cites; pillar row first, then
     decisions in order of first appearance. Meaning column in English.
     Delete the section if the report cites no code. -->

| Code | Meaning |
|------|---------|
| <a id="ref-P#"></a>![P#](https://img.shields.io/badge/P%23-e2f5d5.svg) | <pillar name> (pillar) |
| <a id="ref-D#"></a>![D#](https://img.shields.io/badge/D%23-d97706.svg) | <decision title> — <concise gloss, ≤~12 words, commas not semicolons> |

---

## 🥇 논문 1 — 우선순위 ★★★

<!-- Medal = rank, stars = priority after the ceiling — AUTHORING §2-1, §5-3.
     The top three only, each medal once; the rest go to 📋 (§5-1). -->

**<Paper Title>**
[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) · <authors> · <venue tier, or arXiv preprint> · source: <citation-graph | keyword-sweep> · <코드 공개 | 코드 공개 예정 | 코드 미공개>

### (a) 관련 Pillar / Decision
<!-- Linked badges only — AUTHORING §3-1:
     [![P#](…)](#ref-P#) / [![D#](…)](#ref-D#) [![D#](…)](#ref-D#) -->

### (b) 핵심 기여
<!-- 개조식 — AUTHORING §2-2, §4-4. No D# / deferred / config keys (§3-1). -->

### (c) 시사점

### (d) 먼저 확인할 점

---

## 🥈 논문 2 — 우선순위 ★★

**<Paper Title>**
[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) · <authors> · <venue> · source: <...> · <코드 라벨>

### (a) 관련 Pillar / Decision
### (b) 핵심 기여
### (c) 시사점
### (d) 먼저 확인할 점

---

## 🥉 논문 3 — 우선순위 ★

**<Paper Title>**
[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) · <authors> · <venue> · source: <...> · <코드 라벨>

### (a) 관련 Pillar / Decision
### (b) 핵심 기여
### (c) 시사점
### (d) 먼저 확인할 점

---

## 🌱 논문 4 — 인접 분야 픽

<!-- Once a month; the budget is in `.claude/prompts/scouting.txt`. -->

**<Paper Title>**
[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) · <authors> · adjacent field: <...> · <코드 라벨>

### (a) 관련 Pillar / Decision
### (b) 핵심 기여
### (c) 시사점
### (d) 먼저 확인할 점

---

## 📋 기준 통과 · 추가 후보

<!-- AUTHORING §5-1. Every further gate-clearing paper below 🥉, in rank order.
     Omit the section when three or fewer papers clear the gate. -->

| Paper | Link | R·N·M·S2R | Repro | 합계 | 코드 | 한 줄 근거 |
|---|---|---|---|---|---|---|
| <alias> | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) | 3·2·2·2 | 1 | 10/15 | 코드 공개 예정 | <한 줄> |

---

## 📊 점수 요약

<!-- No table — AUTHORING §5-1. One head per paper section (not 📋 rows), five bullets;
     Reproducibility quotes its evidence (§5-2). -->

**<alias> (<total>/15)**
- Relevance <0–3> — <근거>
- Novelty <0–3> — <근거>
- Reproducibility <0–3> — arXiv comment "<quoted substring>"
- Methodology <0–3> — <근거>
- Sim2Real <0–3> — <근거>

---

## 🔍 근접 후보

<!-- AUTHORING §5-4. Omit the section if it has no rows. -->

| Paper | Link | R·N·M·S2R | 코드 | 재검토 조건 |
|---|---|---|---|---|
| <alias> | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) | 3·2·2·1 | 공개 예정 | <what would lift the short axis> |

---

## 💡 컨텍스트 제안

<!-- AUTHORING §2-2, §7-1. Proposals only — context/ is read-only to the agent. -->

- **미결 제안 N건** — <제목>(최초 YYYY-MM-DD), <제목>(최초 YYYY-MM-DD)

### Tracked literature

### Decision Log

### Anti-topics

---

## 🔄 직전 리포트 대비 종합

<!-- AUTHORING §7-2. 3–5 bullets; omit any item that does not apply. -->

---

## 🚫 필터 통과 실패 후보 논문

<!-- AUTHORING §4-5, §7-3. One paper per row; alias only in `Paper`. -->

| Paper | Link | Reason dropped |
|-------|------|----------------|
| <alias> | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) | Anti-topic: <rule from the Anti-topics list, `context/P#.md` §1> |
| <alias> | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) | Novelty < 2 (delta over pinned:<name>) |
| <alias> | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) | Sim2Real = 0 (sim-only, no real-robot evidence) |
