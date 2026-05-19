# Pulse Hint — Week 2026-W17 [EXAMPLE, not real data]

**Digest date:** 2026-04-24
**Source:** `inbox/2026-W17_dexterous-ch.txt` (illustrative)
**Window:** 2026-04-17 → 2026-04-23
**Messages processed:** 142 (3 distinct speakers)
**Confidence:** medium

> This week the team converged on narrowing the single-skill demo to in-hand
> rotation only, and repeatedly raised doubts about whether RMA extrinsics
> actually capture friction vs. mass separately. They explicitly set aside
> bottle-cap opening for this quarter. Next scout should bias toward
> RMA-ablation and friction-identification work; deprioritize bottle-cap.

---

## Focus Signals

### Converging on
- Single-skill demo will be **in-hand rotation only** this quarter; bottle-cap opening is deferred (3 speakers, no pushback over 3 days).
- RMA extrinsics probing is the near-term experiment — a concrete probing-classifier setup is under discussion (2 speakers agree on the approach).

### Exploring / confused about
- Whether `friction` and `mass` are actually *separable* in the current extrinsics, or collapse to a single "inertia-ish" axis. No resolution.
- Whether to run system-ID before or after narrowing DR — two speakers argued both sides.

### Explicitly discarded
- Bottle-cap opening as the demo task for Q2 2026.
- Running DrEureka-style automatic reward synthesis on the rotation task (one member ran it, others agreed it under-performs hand-crafted).

---

## Scouting Bias (next run only)

- **Boost authors:** Haozhi Qi, Ashish Kumar, Yichao Liang (RMA lineage + extrinsics probing).
- **Boost keywords:** `RMA extrinsics probing`, `friction identification`, `mutual information extrinsics`, `in-hand rotation ablation`.
- **Downweight topics:** bottle-cap opening, DrEureka / automatic reward synthesis (unless directly ablating against hand-crafted).
- **Retrieval mode bias:** citation-graph (expand around HORA, RMA2).

---

## Context Links

- **Touches Q#:** Q2 (single-skill mastery — scope narrowed), Q3 (RMA quantification — active probing).
- **Pressures H#:** H2 (supports — team agrees hand-crafted > auto reward), H3 (challenges — subspace separability under question).
- **Pinned literature referenced:** HORA, RMA2.
- **New names surfaced (not yet pinned):** "AnyRotate ablation" paper (mentioned twice, no arXiv ID given — scout should verify).

---

## Provenance

- `[2026-04-18 14:22] A`: "let's just kill bottle-cap for this quarter. we keep cycling on it and it's not moving."
- `[2026-04-19 10:05] B`: "the probing classifier on mass vs friction should tell us whether the extrinsics are actually disentangled — I bet they aren't."
- `[2026-04-20 17:41] C`: "ran DrEureka on rotation. hand-crafted still wins by 8pp. not worth another week."
- `[2026-04-22 09:30] A`: "do we narrow DR first, then system-ID? or the other way? I keep flipping on this."

---

## Low-confidence flags

- *Exploring / confused about* #2 (DR vs. system-ID ordering) has speaker A flipping position — treat as unresolved, not as bias.
- "AnyRotate ablation" was mentioned without a link; scout must verify before using it as a retrieval anchor.
