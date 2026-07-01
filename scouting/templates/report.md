# Probe 스카우트 리포트 — YYYY-MM-DD · Pillar P#

**Run date:** YYYY-MM-DD
**Agent version:** v0.1
<!-- Papers scanned: ONE-LINE summary only (STYLE §4-5) — provenance lives
     here. If a tool call failed, state it verbatim inline (e.g.
     "일부 쿼리 HTTP 429 실패"); never fabricate. -->
**Papers scanned:** <N from arXiv> + <M from citation graph> + <K from author watch>
**Papers surfaced (every dimension ≥ 2):** <count>

---

## 🔑 참조 약어 풀이

<!--
style.md §3-1 is authoritative. Summary:
  · ONLY P#/D# codes that this report actually cites. No others.
  · One table, rows ordered P# → D# (asc), one per distinct code.
  · Each code is a shields.io BADGE (STYLE §3-1): P# uses the pillar palette
    (P1 f5e9d5, P2 e2f5d5, P3 d5f5e7, P4 d5def5), every D# shares d97706 (amber).
    Format: `![CODE](https://img.shields.io/badge/CODE-<hex>.svg)`.
  · Legend row: <a id="ref-CODE"></a>![CODE](…badge…) | one-line meaning (English only).
    The anchor stays so body links resolve; the legend badge itself is not a link.
  · Meaning source (do not invent), from context/P#.md:
      P# → §2 heading "Pillar P# — <name>"     → "<name> (pillar)"
      D# → §4 "#### [D#] <title>" + its current default
           → "<title> — <concise gloss, ≤~12 words>". NO `v1:` label,
             NO `;` semicolon chains (use commas); it is a decode gloss.
  · In the body, the FIRST occurrence of each code per ## section is a
    LINKED badge `[![CODE](…badge…)](#ref-CODE)`; later same-section
    occurrences stay plain text. Codes inside table cells stay plain text.
    Do NOT add a Korean gloss next to a body badge — the badge alone ties
    the paper; the meaning lives in the legend.
  · If the report cites no P#/D# code, delete this whole section.
-->

| Code | Meaning |
|------|---------|
| <a id="ref-P#"></a>![P#](https://img.shields.io/badge/P%23-e2f5d5.svg) | <pillar name> (pillar) |
| <a id="ref-D#"></a>![D#](https://img.shields.io/badge/D%23-d97706.svg) | <decision title> — <concise gloss, ≤~12 words, commas not semicolons> |

---

## 🥇 논문 1 — 우선순위 ★★★

**<Paper Title>**
[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) · <authors> · source: <author-watch | citation-graph | keyword-sweep>

### (a) 관련 Pillar / Decision
<!-- The decision TIE only — a single line of LINKED BADGES, nothing else
     (STYLE §3-1). `[![P2](…)](#ref-P2) / [![D11](…)](#ref-D11) [![D8](…)](#ref-D8)`
     ( ` / ` between pillar and decisions, a SPACE between decision badges); NO
     Korean gloss next to any badge, NO body bullets here — the paper substance
     goes in (b). The four sections read as ONE STORY: tie → contribution →
     what it means for us → what to check.
     PAPER-FOCUSED (do NOT plaster internal decision bookkeeping): in (b)–(d),
     avoid `D11`/`deferred`/`v1`/config-key/`*.yaml` names — a reader should not
     stop to ask "what is D11? what is deferred?". The decision link is the (a)
     badges; concrete context-edit proposals live in 💡 Context Suggestions. -->

### (b) 핵심 기여
<!-- 개조식 bullets: what the paper IS, what it DOES, and what is genuinely new
     vs. the field — paper-focused, no internal D#/config references. -->

### (c) 시사점
<!-- 개조식 bullets: what this could mean for us, in PLAIN terms (e.g. "공개
     기준점 확보", "도입 비용 낮음") — not "D11 v1 …" / config-key plumbing. -->

### (d) 먼저 확인할 점
<!-- 개조식 bullets: the paper's own limits + the cheapest transfer caveat,
     plainly. No D#/deferred jargon. -->

---

## 🥈 논문 2 — 우선순위 ★★

**<Paper Title>**
[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) · <authors> · source: <...>

### (a) 관련 Pillar / Decision
### (b) 핵심 기여
### (c) 시사점
### (d) 먼저 확인할 점

---

## 🥉 논문 3 — 우선순위 ★

**<Paper Title>**
[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) · <authors> · source: <...>

### (a) 관련 Pillar / Decision
### (b) 핵심 기여
### (c) 시사점
### (d) 먼저 확인할 점

---

## 🌱 논문 4 — 인접 분야 픽 (월 1회)

<!-- Include once per month. Rotate target field per context/MASTER.md §12 (Cross-pollination Budget). -->

**<Paper Title>**
[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) · <authors> · adjacent field: <...>

### (a) 관련 Pillar / Decision
### (b) 핵심 기여
### (c) 시사점
### (d) 먼저 확인할 점

---

## 📊 점수 요약

<!-- NO summary table — it duplicates the per-paper rationale below (STYLE §4-5).
     The rubric is FIVE dimensions, 0–3 each, total /15 (canonical
     definitions: .claude/prompts/scouting.txt; codified in STYLE §4-5):
       Relevance · Novelty · Reproducibility · Methodology · Sim2Real
     Surface a paper only if every one of the five dimensions scores ≥ 2;
     if fewer than 3 qualify, say so and do not pad. The rationale is
     개조식 (STYLE §4-4): one bold paper head carrying the total
     (`**HapTile (13/15)**`), then a nested bullet per dimension
     (`- Relevance 3 — <명사형 근거>`), all five dimensions listed. -->

---

## 💡 컨텍스트 제안

<!-- Agent proposes edits to the relevant context/P#.md. Human decides. Agent must NOT edit any context/ file directly.
     Every sub-section below is 개조식 (STYLE §4-4): labelled bullets
     (대상/제안/근거/트리거 …, 명사형 종결), not prose paragraphs. -->

### Tracked literature
<!-- Replace / add / remove a pinned paper within the pillar's 8-paper cap (`context/P#.md` §5). Include arXiv link and target Pillar. -->

### Decision Log
<!-- Trigger an existing deferred candidate (cite D# + checkpoint), revise a v1 default's rationale, or propose a new decision. State which evidence this week moved it. -->

### Anti-topics
<!-- Candidate new exclusion rule surfaced by this week's filter set. -->

---

## 🔄 직전 리포트 대비 종합

<!--
Self-check against this pillar's recent reports (last ~2 weeks, ~4 files
scouting/P#/YYYY-MM-DD.md). Keep it TIGHT — 3–4 bullets, one sentence each
where possible, no hedging; this section is the most over-written one (STYLE
§4-5). Cover:
  · Papers already covered? — verdict FIRST ("N편 전원 재등장·제외"), then the list.
  · Contradictions with recent findings?
  · Decision-Log triggers / falsifier evidence observed this run?
  · Month-trend note (only on the first run of the month).
  · Anti-topics filter health — count of papers excluded.
  · Already-analyzed dedup — count of candidates dropped for already having
    an analysis/<id>/ folder (0 if none).
-->

---

## 🚫 필터 통과 실패 후보 논문

<!-- Reference appendix — kept LAST so the decision content (papers, scores,
     context suggestions) stays up top (STYLE §4-5). -->

| Paper | Link | Reason dropped |
|-------|------|----------------|
<!-- Paper column: short name (+ author "et al." if helpful) only. Do NOT repeat
     the arXiv id here — the Link column already carries it (STYLE §4-5). -->
| <title> | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) | Anti-topic: <specific rule from the pillar's §4 Anti-topics> |
| <title> | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) | Novelty < 2 (delta over pinned:<name>) |
| <title> | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) | Sim2Real = 0 (sim-only, no real-robot evidence) |
