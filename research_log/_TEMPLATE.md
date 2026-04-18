# Probe Scouting Report — Week YYYY-WXX

**Run date:** YYYY-MM-DD
**Agent version:** v0.1
**Papers scanned:** <N from arXiv> + <M from citation graph> + <K from author watch>
**Papers surfaced (every dimension ≥ 2):** <count>

> Agent fills every section below. Emoji, link, and translation rules are defined in `STYLE_GUIDE.md` — follow it exactly.
> Every weekly run produces **two** files: `YYYY-WXX.md` (English, primary) and `YYYY-WXX-KO.md` (Korean translation).

---

## 📋 Scout Methodology

<!--
Summarize the three retrieval passes in 3–5 bullets. Weight: Author Watch > Citation-Graph > Keyword Sweep.
  · Author Watch — N researchers from research_context.md §5, date range
  · Citation-Graph Expansion — M pinned papers from §4, citation window
  · Keyword Sweep — queries, cs.RO + cs.LG window, anti-topic filter from §7
If any tool call failed, state the error verbatim. Do not fabricate.
-->

---

## 🥇 Paper 1 — PRIORITY ★★★

**<Paper Title>**
[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) · <authors> · source: <author-watch | citation-graph | keyword-sweep>

### 🎯 (a) Q# / H# touched
<!-- Which Active Question(s) or Hypothesis(es) from research_context.md does this address? -->

### ✨ (b) What is genuinely new
<!-- One sentence. Not an abstract paraphrase. What is the delta against the pinned literature? -->

### ⚙️ (c) Decision implication
<!-- What changes in MY Isaac Lab pipeline next week if this paper is right?
     Name the exact config key, hyperparameter, or metric. Vague = failure. -->

### ⚠️ (d) Failure mode to probe first
<!-- Why might this NOT transfer to our stack? What is the cheapest sanity check? -->

---

## 🥈 Paper 2 — PRIORITY ★★

**<Paper Title>**
[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) · <authors> · source: <...>

### 🎯 (a) Q# / H# touched
### ✨ (b) What is genuinely new
### ⚙️ (c) Decision implication
### ⚠️ (d) Failure mode to probe first

---

## 🥉 Paper 3 — PRIORITY ★

**<Paper Title>**
[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) · <authors> · source: <...>

### 🎯 (a) Q# / H# touched
### ✨ (b) What is genuinely new
### ⚙️ (c) Decision implication
### ⚠️ (d) Failure mode to probe first

---

## 🌱 Paper 4 — CROSS-POLLINATION (monthly only)

<!-- Include once per month. Rotate target field per research_context.md §8 (Cross-pollination Budget). -->

**<Paper Title>**
[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) · <authors> · adjacent field: <...>

### 🎯 (a) Q# / H# touched
### ✨ (b) What is genuinely new
### ⚙️ (c) Decision implication
### ⚠️ (d) Failure mode to probe first

---

## 📊 Scoring Summary

| # | Paper | Link | Relevance (0–3) | Novelty (0–3) | Reproducibility (0–3) | Sim2Real (0–3) | Total (/12) |
|---|-------|------|:---:|:---:|:---:|:---:|:---:|
| 1 | <title> | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) | – | – | – | – | – |
| 2 | <title> | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) | – | – | – | – | – |
| 3 | <title> | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) | – | – | – | – | – |

<!-- Surface a paper only if every dimension scores ≥ 2. If fewer than 3 qualify, say so and do not pad. -->

---

## 🚫 Candidate Papers That Did Not Pass Filter

| Paper | Link | Reason dropped |
|-------|------|----------------|
| <title> | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) | Anti-topic: <specific rule from §7> |
| <title> | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) | Novelty < 2 (delta over pinned:<name>) |
| <title> | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) | Sim2Real = 0 (sim-only, no real-robot evidence) |

---

## 💡 Context Suggestions

<!-- Agent proposes edits to research_context.md. Human decides. Agent must NOT edit research_context.md directly. -->

### 📌 Pinned literature
<!-- Replace / add / remove pinned paper. Include arXiv link. -->

### 📌 Hypotheses
<!-- Narrow / strengthen / weaken / retire H#. State which evidence this week moved it. -->

### 📌 Anti-topics
<!-- Candidate new exclusion rule surfaced by this week's filter set. -->

### 📌 Researchers to follow
<!-- Add / remove authors based on signal this week. -->

---

## 🔄 Week-over-Week Synthesis

<!--
Self-check against the last 2 weeks of research_log/:
  · Papers already covered? (list, or "none")
  · Contradictions with last 2 weeks' findings?
  · Open questions partially answered this week?
  · Month-trend note (only on first week of month).
  · Anti-topics filter health — count of papers excluded.
-->
