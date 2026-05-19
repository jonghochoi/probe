# Probe 스카우트 리포트 — YYYY-MM-DD · Pillar P#

**Run date:** YYYY-MM-DD
**Agent version:** v0.1
**Papers scanned:** <N from arXiv> + <M from citation graph> + <K from author watch>
**Papers surfaced (every dimension ≥ 2):** <count>

> 에이전트가 아래 모든 섹션을 채웁니다. 본문은 한글로 작성하되, 이모지·링크·verbatim 유지 규칙은 `STYLE_GUIDE.md`에 정의되어 있으니 정확히 따릅니다.
> 루틴은 주 2회(월·목) 실행되며, 매 실행마다 한글 파일 **하나**(`YYYY-MM-DD-P#.md`)를 산출합니다.
> 각 섹션에서 처음 등장하는 P#/D#/CP# 코드는 아래 🔑 참조 약어 풀이로 링크합니다.

---

## 🔑 참조 약어 풀이

<!--
STYLE_GUIDE.md §3-1 is authoritative. Summary:
  · ONLY P#/D#/CP# codes that this report actually cites. No others.
  · One table, rows ordered P# → D# (asc) → CP# (asc), one per distinct code.
  · Each row: <a id="ref-CODE"></a>**CODE** | one-line meaning (Korean).
  · Meaning source (do not invent), from context/P#.md:
      P#  → §2 heading "Pillar P# — <name>"           → "<name> (pillar)"
      D#  → §4 "#### [D#] <title>" + its v1 line       → "<title> — v1 choice (≤~12 words)"
      CP# → §3 bullet "- **CP#**: <desc>"              → "Checkpoint #: <desc>"
  · In the body, link only the FIRST occurrence of each code per ## section
    as [CODE](#ref-CODE); later same-section occurrences stay plain.
  · If the report cites no P#/D#/CP# code, delete this whole section.
-->

| Code | Meaning |
|------|---------|
| <a id="ref-P#"></a>**P#** | <pillar name> (pillar) |
| <a id="ref-D#"></a>**D#** | <decision title> — <v1 choice, ≤~12 words> |
| <a id="ref-CP#"></a>**CP#** | Checkpoint #: <checkpoint description> |

---

## 📋 스카우트 방법론

<!--
Section numbers below are for the full context/MASTER.md. The cloud
scouting routine instead reads a per-pillar extract context/P#.md,
where the same content is renumbered: Researchers=§7, Tracked Literature=§6,
Anti-topics=§5, Competitor=§8. Use whichever the active prompt points at.

Summarize the retrieval passes in 3–5 bullets. Weight: Author Watch > Citation-Graph > Keyword Sweep; add Competitor Monitoring as a dedicated pass.
  · Author Watch — N researchers (full §9 / extract §7), date range
  · Citation-Graph Expansion — M pinned papers (full §8 / extract §6, Tracked Literature), citation window
  · Keyword Sweep — queries, cs.RO + cs.LG window, anti-topic filter (full §7 / extract §5)
  · Competitor Monitoring — watch-list scan (full §10 / extract §8)
If any tool call failed, state the error verbatim. Do not fabricate.
-->

---

## 🥇 논문 1 — 우선순위 ★★★

**<Paper Title>**
[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) · <authors> · source: <author-watch | citation-graph | keyword-sweep>

### 🎯 (a) 관련 Pillar / Decision (P# / D#)
<!-- Which Pillar(s) (P1–P5) and Decision(s) (D1–D15) from context/MASTER.md does this address? Mention CP1–CP5 in body if it lands at a specific Checkpoint. Also note any Identity tension/support and any §10 Competitor implication. -->

### ✨ (b) 진정으로 새로운 점
<!-- One sentence. Not an abstract paraphrase. What is the delta against the pinned literature? -->

### ⚙️ (c) 의사결정 함의
<!-- What changes in MY Isaac Lab pipeline next week if this paper is right?
     Name the exact config key, hyperparameter, or metric. Vague = failure. -->

### ⚠️ (d) 먼저 검증해야 할 실패 모드
<!-- Why might this NOT transfer to our stack? What is the cheapest sanity check? -->

---

## 🥈 논문 2 — 우선순위 ★★

**<Paper Title>**
[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) · <authors> · source: <...>

### 🎯 (a) 관련 Pillar / Decision (P# / D#)
### ✨ (b) 진정으로 새로운 점
### ⚙️ (c) 의사결정 함의
### ⚠️ (d) 먼저 검증해야 할 실패 모드

---

## 🥉 논문 3 — 우선순위 ★

**<Paper Title>**
[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) · <authors> · source: <...>

### 🎯 (a) 관련 Pillar / Decision (P# / D#)
### ✨ (b) 진정으로 새로운 점
### ⚙️ (c) 의사결정 함의
### ⚠️ (d) 먼저 검증해야 할 실패 모드

---

## 🌱 논문 4 — 크로스폴리네이션 (월 1회)

<!-- Include once per month. Rotate target field per context/MASTER.md §12 (Cross-pollination Budget). -->

**<Paper Title>**
[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) · <authors> · adjacent field: <...>

### 🎯 (a) 관련 Pillar / Decision (P# / D#)
### ✨ (b) 진정으로 새로운 점
### ⚙️ (c) 의사결정 함의
### ⚠️ (d) 먼저 검증해야 할 실패 모드

---

## 📊 점수 요약

| # | Paper | Link | Relevance (0–3) | Novelty (0–3) | Reproducibility (0–3) | Sim2Real (0–3) | Total (/12) |
|---|-------|------|:---:|:---:|:---:|:---:|:---:|
| 1 | <title> | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) | – | – | – | – | – |
| 2 | <title> | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) | – | – | – | – | – |
| 3 | <title> | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) | – | – | – | – | – |

<!-- Surface a paper only if every dimension scores ≥ 2. If fewer than 3 qualify, say so and do not pad. -->

---

## 🚫 필터 통과 실패 후보 논문

| Paper | Link | Reason dropped |
|-------|------|----------------|
| <title> | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) | Anti-topic: <specific rule from §7> |
| <title> | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) | Novelty < 2 (delta over pinned:<name>) |
| <title> | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) | Sim2Real = 0 (sim-only, no real-robot evidence) |

---

## 💡 컨텍스트 제안

<!-- Agent proposes edits to context/MASTER.md. Human decides. Agent must NOT edit context/MASTER.md directly. -->

### 📌 Tracked literature
<!-- Replace / add / remove a pinned paper within a Pillar's 8-paper cap (§8.1–§8.5). Include arXiv link and target Pillar. -->

### 📌 Decision Log
<!-- Trigger an existing deferred candidate (cite D# + checkpoint), revise a v1 default's rationale, or propose a new decision. State which evidence this week moved it. -->

### 📌 Anti-topics
<!-- Candidate new exclusion rule surfaced by this week's filter set. -->

### 📌 Researchers to follow
<!-- Add / remove authors based on signal this week (§9). -->

### 📌 Competitor / Kindred monitoring
<!-- Any new release from §10 watch list (DexReMoE / CATFA / SaTA / Sharpa VTLA / π lineage)? Differentiation vehicle still intact? -->

---

## 🔄 직전 리포트 대비 종합

<!--
Self-check against this pillar's recent reports (last ~2 weeks, ~4 files
scouting/YYYY-MM-DD-P#.md):
  · Papers already covered? (list, or "none")
  · Contradictions with recent findings?
  · Decision-Log triggers / falsifier evidence observed this run?
  · Month-trend note (only on the first run of the month).
  · Anti-topics filter health — count of papers excluded.
-->
