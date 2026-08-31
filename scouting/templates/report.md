# Probe 스카우트 리포트 — YYYY-MM-DD · Pillar P#

<!-- Metadata block is exactly these two lines (AUTHORING §6). No `Run date:`
     (the H1 carries it), no `Agent version:` (a constant is not information).
     `Papers scanned:` — ONE line, ≤ 400 chars: which passes ran, an
     order-of-magnitude count each, and any call STILL failing at the end of
     the run (verbatim). No funnel arithmetic, no per-query log, no retry
     narration — a retry that succeeded is a non-event.
     `Papers surfaced:` — an INTEGER and nothing else; the "why" goes in 📊. -->
**Papers scanned:** <citation-graph N편> + <keyword sweep M편(14일 K편)>
**Papers surfaced (4축 게이트 통과):** <count>

---

## 🔑 참조 약어 풀이

<!--
`scouting/AUTHORING.md` §3-1 is authoritative. Summary:
  · ONLY P#/D# codes that this report actually cites. No others.
  · One table, rows ordered P# → D# (asc), one per distinct code.
  · Each code is a shields.io BADGE (AUTHORING §3-1): P# takes its hex from the
    pillar palette table there, which is the palette's source of truth; every
    D# shares d97706 (amber).
    Format: `![CODE](https://img.shields.io/badge/CODE-<hex>.svg)`.
  · Legend row: <a id="ref-CODE"></a>![CODE](…badge…) | one-line meaning (English only).
    The anchor stays so body links resolve; the legend badge itself is not a link.
  · Meaning source (do not invent), from context/P#.md:
      P# → §2 heading "Pillar P# — <name>"     → "<name> (pillar)"
      D# → §3 "#### [D#] <title>" + its current default
           → "<title> — <concise gloss, ≤~12 words>". NO Korean,
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

<!-- ★★★ requires 코드 공개 (Reproducibility ≥ 2) — AUTHORING §5-3. A paper
     labelled 공개 예정 / 미공개 caps at ★★ however strong the rest is. -->

**<Paper Title>**
[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) · <authors> · <venue tier, or arXiv preprint> · source: <citation-graph | keyword-sweep> · <코드 공개 | 코드 공개 예정 | 코드 미공개>

### (a) 관련 Pillar / Decision
<!-- The decision TIE only — a single line of LINKED BADGES, nothing else
     (AUTHORING §3-1). `[![P<n>](…)](#ref-P<n>) / [![D<a>](…)](#ref-D<a>) [![D<b>](…)](#ref-D<b>)`
     ( ` / ` between pillar and decisions, a SPACE between decision badges); NO
     Korean gloss next to any badge, NO body bullets here — the paper substance
     goes in (b). The four sections read as ONE STORY: tie → contribution →
     what it means for us → what to check.
     PAPER-FOCUSED (do NOT plaster internal decision bookkeeping): in (b)–(d),
     avoid `D<n>`/`deferred`/config-key/`*.yaml` names — a reader should not
     stop to ask "what is D<n>? what is deferred?". The decision link is the (a)
     badges; concrete context-edit proposals live in 💡 Context Suggestions. -->

### (b) 핵심 기여
<!-- 개조식 bullets: what the paper IS, what it DOES, and what is genuinely new
     vs. the field — paper-focused, no internal D#/config references. -->

### (c) 시사점
<!-- 개조식 bullets: what this could mean for us, in PLAIN terms (e.g. "공개
     기준점 확보", "도입 비용 낮음") — not "D<n> …" / config-key plumbing. -->

### (d) 먼저 확인할 점
<!-- 개조식 bullets: the paper's own limits + the cheapest transfer caveat,
     plainly. No D#/deferred jargon. -->

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

## 🌱 논문 4 — 인접 분야 픽 (월 1회)

<!-- Include ONCE PER MONTH — check this pillar's recent reports before adding
     one; if a 🌱 section appears in any report from the current month, skip it.
     The rotating target field is the Cross-pollination Budget table inlined in
     `.claude/prompts/scouting.txt` (the pillar-scoped run does not read
     context/MASTER.md). -->

**<Paper Title>**
[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) · <authors> · adjacent field: <...> · <코드 라벨>

### (a) 관련 Pillar / Decision
### (b) 핵심 기여
### (c) 시사점
### (d) 먼저 확인할 점

---

## 📊 점수 요약

<!-- NO summary table — it duplicates the per-paper rationale below (AUTHORING §4-5).
     Rubric: FIVE dimensions, 0–3 each, total /15 (definitions in
     .claude/prompts/scouting.txt; contract in AUTHORING §5):
       Relevance · Novelty · Reproducibility · Methodology · Sim2Real
     The GATE is FOUR of them — Relevance/Novelty/Methodology/Sim2Real each ≥ 2.
     Reproducibility is scored and shown but does NOT gate; it sets the priority
     ceiling (AUTHORING §5-3). If fewer than 3 clear the gate, say so, do not pad.
     Rationale is 개조식 (AUTHORING §4-4): one bold paper head carrying the total
     (`**HapTile (13/15)**`), then a bullet per dimension
     (`- Relevance 3 — <명사형 근거>`), all five dimensions listed.
     The Reproducibility bullet QUOTES the evidence it scored on — the arXiv
     comment field or the abstract (AUTHORING §5-2). "공개 벤치마크에서 평가함" is
     NOT reproducibility evidence, and an absent signal is stated as absent,
     never as "초록상 미확인 / 확인 필요". -->

---

## 🔍 근접 후보

<!-- AUTHORING §5-4. Two kinds of row:
       1. exactly ONE of the four gate dimensions scores 1, the rest ≥ 2;
       2. carried forward — listed here, or dropped for Reproducibility, in
          this pillar's last ~4 weeks. Re-check the code signal EVERY run; a
          candidate whose repo is now public is promoted to a full paper
          section this run and named in 🔄.
     A row that clears ALL FOUR gate dimensions does not belong here — it is a
     surfaced paper, whatever its code status (§5-1). Two or more axes short is
     a 🚫 row. A row expires 4 weeks after it first appears: promote it or drop
     it, and name the retirement in 🔄.
     A paper appears in 🔍 or in 🚫, never both. Omit the section if empty. -->

| Paper | Link | R·N·M·S2R | 코드 | 재검토 조건 |
|---|---|---|---|---|
| <alias> | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) | 3·2·2·1 | 공개 예정 | <what must change to promote it> |

---

## 💡 컨텍스트 제안

<!-- Agent proposes edits to the relevant context/P#.md. Human decides. Agent must NOT edit any context/ file directly.
     Every sub-section below is 개조식 (AUTHORING §4-4): labelled bullets
     (대상/제안/근거/트리거 …, 명사형 종결), not prose paragraphs.
     A proposal already made in this pillar's last ~2 weeks is NOT restated —
     it is rolled up into the 미결 제안 line below (AUTHORING §7-1). -->

- **미결 제안 N건** — <제목>(최초 YYYY-MM-DD), <제목>(최초 YYYY-MM-DD)

### Tracked literature
<!-- Replace / add / remove a pinned paper within the pillar's 8-paper cap (`context/P#.md` §5). Include arXiv link and target Pillar. -->

### Decision Log
<!-- Trigger an existing deferred candidate (cite D# + checkpoint), revise a default's rationale, or propose a new decision. State which evidence this run moved it. -->

### Anti-topics
<!-- Candidate new exclusion rule surfaced by this run's filter set. -->

---

## 🔄 직전 리포트 대비 종합

<!--
Self-check against this pillar's recent reports (last ~2 weeks, ~4 files
scouting/P#/YYYY-MM-DD.md). 3–5 bullets, one sentence each, no hedging
(AUTHORING §7-2). Cover only what this run actually has:
  · Papers already covered? — verdict FIRST ("N편 전원 재등장·제외"), then the list.
  · Contradictions with recent findings?
  · Decision-Log triggers / falsifier evidence observed this run?
  · 🔍 promotions this run (a carried-forward candidate whose code went public).
  · Anti-topics filter health — a COUNT and a reason, never the retrieval
    funnel from `Papers scanned` (AUTHORING §6).
  · Already-analyzed dedup — count of candidates dropped for already having
    an analysis/<id>.md rewrite (omit the bullet if 0).
An item that does not apply is OMITTED — do not write a bullet whose content
is that it has no content ("월간 트렌드: 첫 리포트 아님 — 생략").
-->

---

## 🚫 필터 통과 실패 후보 논문

<!-- Reference appendix — kept LAST so the decision content (papers, scores,
     context suggestions) stays up top (AUTHORING §4-5).
     ONE ROW PER PAPER (AUTHORING §7-3) — never bundle "X 외 2편" behind one link.
     Paper column: short alias (+ author "et al." if helpful) only. Do NOT
     repeat the arXiv id — the Link column carries it (AUTHORING §4-5).
     A paper waiting on a code release belongs in 🔍, not here. -->

| Paper | Link | Reason dropped |
|-------|------|----------------|
| <title> | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) | Anti-topic: <specific rule from the pillar's §4 Anti-topics> |
| <title> | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) | Novelty < 2 (delta over pinned:<name>) |
| <title> | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) | Sim2Real = 0 (sim-only, no real-robot evidence) |
