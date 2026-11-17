# Probe
> Research scout for hand-centric dexterous manipulation.

---

# Research Context — Hand-centric Dexterous Manipulation

> **Agent usage**: This file is the *static, cross-cutting* **global anchor** — Identity, Purpose, Long-term Context, the Pillars overview, and cross-pillar references. Per-pillar working context (Open Questions, Tracked Literature, Anti-topics) is **owned by `context/P0–P4.md`**, which the retrieval agent reads (never writes). Findings go to `scouting/P#/YYYY-MM-DD.md` (one file per run, per pillar).

---

## 0. How to use this file [STABLE]

**What lives where**
- This document (`MASTER.md`) is the **global anchor**: cross-cutting content that is not specific to one pillar. It is *not* a superset of the pillar files.
- `context/P0–P4.md` are the **owners** of their pillar's Open Questions, Tracked Literature and Anti-topics. Edit the pillar file for pillar content; edit this anchor only for cross-cutting content.

**Section markers**
- `[STABLE]`: changes rarely (identity, purpose, hardware)
- `[LIVING]`: updated as research progresses
- `[AGENT-INPUT]`: retrieval agent conditions on this — keep signal-dense

**Update protocol**
- Identity / Purpose: change only with deliberate review (semantic shift, not phrasing)
- Pillars: structure stable; the open questions and their threads evolve as evidence accumulates

**Output formatting & authoring rules**
Output format is one contract per track — `scouting/AUTHORING.md`, `analysis/AUTHORING.md`, `comparison/AUTHORING.md`. The agent reads its track's contract before producing any output. Do not duplicate formatting rules here; edit the contract instead.

**Audience**: maintainer (self, future-self) + AI retrieval agent + future collaborators. Keep terminology accessible without sacrificing precision.

---

## 1. Identity [STABLE] [AGENT-INPUT]

> Dexterity is pursued two ways that do not reach it. A **monolithic action
> decoder over vision-dominant observation** treats arm, torso and finger as
> one homogeneous action space and takes sensing as a flat concat. A
> **correction or residual module bolted onto a frozen VLA** is structurally
> bounded by that VLA's own local output distribution and must be re-trained
> whenever its motion pattern shifts, so it tracks the ceiling rather than
> exceeding it. Dexterous **hand** manipulation is therefore tackled **at the
> VLA level itself** — the decoder, the observation and the pretraining are
> each designed rather than left to be learned incidentally. Task
> specification stays goal-centric, arm and hand integrated.

**Decomposition**
- *Antagonist A*: a monolithic decoder over one homogeneous action space
- *Antagonist B*: sensing taken as a flat concat of heterogeneous streams
- *Antagonist C*: a correction/residual module on a frozen VLA —
  distribution-bounded, re-trained on every motion-pattern shift
- *Protagonist*: the decoder, the observation and the pretraining, each
  designed at the VLA level
- *Stays goal-centric*: task specification, arm and hand integrated

Each pillar carries its own tie back to this claim, and §4 says which pillar
owns what. Neither is restated here.

---

## 2. Purpose [STABLE]

This document serves *two coupled functions*:

1. **Filter (outward)** — enables the retrieval agent and collaborators to surface external content (papers, methods, ideas) aligned with the maintainer's identity, and to reject the rest. Requires signal-density and structured fields.
2. **Anchor (inward)** — keeps the open questions each pillar asks and the threads followed on each. Counters drift when external noise (trends, hype) pulls: a paper is read for what it adds to a question, not for whether it agrees with an answer.

**Audience scope**: future-self + AI retrieval agent + future collaborators
**Question depth**: skeleton (the questions that shape a pillar; not every sub-question)

---

## 3. Long-term Context [STABLE → semi-LIVING]

### 3.1 Vision
Build a holistic system for human-level dexterous manipulation. Full stack envisioned: hardware that expresses rich contact, data collection preserving human interaction, control minimizing intent-execution gap, models absorbing multimodal supervision at scale, evaluation infrastructure enabling scalable + reproducible iteration. *Current scope-of-work focuses on modeling at the VLA level.*

### 3.2 Scope of work
**The bet: body expert and hand expert both directly designed and trained at the VLA level.** No outsourcing of dexterity to a post-hoc correction module (which would be distribution-bounded by the VLA). Pretrained VLM/π weights are leveraged via a *deliberately composed pretraining recipe for data-efficient adaptation* (P4), with prior-preservation as one downstream lever. Every component learns at the VLA level, by imitation with flow matching. The pillars' open questions are where this bet is tested — it is the stance the questions are asked from, not an answer they defend.

### 3.3 Task philosophy
**Hand expert as a stabilization layer on top of architectural grounding**, where grounding is body's grasp/arm intent + backbone's visual/task embeddings (with VLM prior preserved). Hand-level contact elevation remains the **differentiation claim**; the **deliverable** is the integrated VLA system.

---

## 4. Pillars [STABLE structure, LIVING content] [AGENT-INPUT]

**Five pillars (P0–P4).** P1, P2 and P4 are the architectural core; P0 (data)
is the upstream supporting pillar; P3 (world model) is a later-phase
capability bet.

Each pillar file owns its own scope, scouting lens, anti-topics, open questions
and tracked literature. This table is the index — what a pillar owns in one
line, how many questions it holds, and where the rest of it lives. The ids
themselves are mapped in `context/CLAUDE.md`. A pillar's scope restated here
is a second copy to keep in step, so it is not restated.

| Pillar | Owns | Questions | File |
|---|---|---|---|
| P0 — VLA Datasets & Benchmarks | the corpora and the instruments that measure on them; data is upstream of method | 3 | `context/P0.md` |
| P1 — Heterogeneous Body/Hand Action Expert | how the action decoder is split into more than one expert, and the questions that stand split or not | 4 | `context/P1.md` |
| P2 — Structured Multimodal Observation Fusion | what happens to sensing before it reaches the policy — spatial registration, per-finger contact attribution, the encoder | 4 | `context/P2.md` |
| P3 — World Model | how a predictive model of dynamics folds into the stack — role, integration, prediction space, conditioning | 4 | `context/P3.md` |
| P4 — Pretraining for Data-Efficient Adaptation | the questions upstream of deploy — corpus × recipe × adaptation — and what they cost to protect afterwards | 5 | `context/P4.md` |

Retired: **D17**, **D18**, **D6ZD**, **D4NT**, **D5QT**, **D4QX**, **D5SH**, **D5DQ**, **D8SD**, **D9WZ**, **D7VC**, **D5ZL**.
A retired id is never re-issued. When a question folds into another, every
citation of the retired id in `analysis/`, `comparison/` and `scouting/` is
rewritten to the id it folded into — or dropped, where it became a premise
rather than part of another question — so no published page points at it.

---

## 5. Venue Priority [AGENT-INPUT]

| Tier | Venues |
|------|--------|
| 1 | CoRL, RSS |
| 2 | ICRA, IROS |
| 3 | T-RO, RA-L (journal — archival weight) |
| 4 | arXiv raw (cs.RO, cs.LG) — noisiest, lowest default weight |
| — | NeurIPS/ICML robotics workshops — read only if pinned author |

---

## 6. Cross-pollination Budget [AGENT-INPUT]

1 paper per pillar per slot from an adjacent field that plausibly transfers. A
slot is a 14-day block counted from Monday 2026-01-05, numbered
`n = ⌊days since 2026-01-05 ÷ 14⌋`; its field is A–D by `n mod 4` (A at 0), so
the four fields cycle in eight weeks. Rotating:
- **Slot A**: continual learning / catastrophic forgetting / PEFT (P4 adjacency)
- **Slot B**: VLA architecture advances broadly (π, OpenVLA, self-improving VLA)
- **Slot C**: spatial-geometric / multimodal fusion representation (P2 adjacency)
- **Slot D**: tactile sensing in prosthetics / neuroscience

---

*End.*
