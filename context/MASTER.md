# Probe
> Research scout for hand-centric dexterous manipulation.

---

# Research Context — Hand-centric Dexterous Manipulation

> **Agent usage**: This file is the *static, cross-cutting* **global anchor** — Identity, Purpose, Long-term Context, Hardware, the Pillars overview, and cross-pillar references. Per-pillar working context (Decision Log, Tracked Literature, Anti-topics) is **owned by `context/P0–P4.md`**, which the retrieval agent reads (never writes). Findings go to `scouting/P#/YYYY-MM-DD.md` (one file per run, per pillar).

---

## 0. How to use this file [STABLE]

**What lives where**
- This document (`MASTER.md`) is the **global anchor**: cross-cutting content that is not specific to one pillar. It is *not* a superset of the pillar files.
- `context/P0–P4.md` are the **owners** of their pillar's Decision Log, Tracked Literature and Anti-topics. Edit the pillar file for pillar content; edit this anchor only for cross-cutting content.

**Section markers**
- `[STABLE]`: changes rarely (identity, purpose, hardware)
- `[LIVING]`: updated as research progresses
- `[AGENT-INPUT]`: retrieval agent conditions on this — keep signal-dense

**Update protocol**
- Identity / Purpose: change only with deliberate review (semantic shift, not phrasing)
- Pillars: structure stable; tracked items within can evolve as evidence accumulates

**Output formatting & authoring rules**
All formatting rules (emoji system, link format, Korean authoring principles) are consolidated in **`scouting/AUTHORING.md`** — the single source of truth. The agent must read `scouting/AUTHORING.md` before producing any output. Do not duplicate formatting rules here; edit `scouting/AUTHORING.md` instead.

**Audience**: maintainer (self, future-self) + AI retrieval agent + future collaborators. Keep terminology accessible without sacrificing precision.

---

## 1. Identity [STABLE] [AGENT-INPUT]

> Most VLA-style policies attempt to converge on dexterity via a **monolithic action decoder + vision-dominant observation**, and most attempts to push the ceiling bolt a **correction/residual module onto a frozen VLA**. I argue both are dead ends for *dexterous **hand** manipulation*: a correction module is structurally bounded by the VLA's own local output distribution and must be re-trained whenever the VLA's motion pattern shifts, so it cannot exceed the VLA ceiling — it only tracks it. **I argue dexterity must be tackled at the VLA level itself**, via (1) an **anatomically heterogeneous Body/Hand action-expert decoder**, (2) **structured multimodal observation fusion** — multi-camera spatial-geometric grounding + per-finger proprio-tactile binding beyond flat concat, (3) a **gated contact-reaction sub-loop** beneath the Hand expert, running faster than the policy loop while a grasp must be held and handing finger control back when it must not, and (4) **data-efficient adaptation through the VLM pretraining recipe** (lineage × egocentric-centric corpus × staged recipe), with prior-preservation as one downstream lever. Task specification stays goal-centric (arm-hand integrated). Two supporting pillars feed this core — **P0** scouts the datasets and benchmarks the pretraining corpus draws on, and **P3** (a later-phase bet) folds an action-conditioned world model into the stack.

**Decomposition**
- *Antagonist A*: VLA-output correction/residual modules — performance bounded by the VLA's local output distribution; re-train on every VLA motion-pattern shift; full-pipeline bottleneck
- *Antagonist B*: monolithic decoder treating arm/torso/finger as one homogeneous action space + simple concat of heterogeneous modalities
- *Protagonist*: VLA-level tackling of dexterous **hand** manipulation — heterogeneous Body/Hand experts + structured multimodal observation fusion + a gated contact-reaction sub-loop + pretraining composed for data-efficient adaptation
- *Stays goal-centric*: task specification (arm-hand integrated)

---

## 2. Purpose [STABLE]

This document serves *two coupled functions*:

1. **Filter (outward)** — enables the retrieval agent and collaborators to surface external content (papers, methods, ideas) aligned with the maintainer's identity, and to reject the rest. Requires signal-density and structured fields.
2. **Anchor (inward)** — records current commitments, open questions, and falsifiability conditions. Counters drift when external noise (trends, hype) pulls. Requires explicit decision rationale and revisit triggers.

**Audience scope**: future-self + AI retrieval agent + future collaborators
**Decision-log depth**: skeleton (key branchpoints recorded; not exhaustive)

---

## 3. Long-term Context [STABLE → semi-LIVING]

### 3.1 Vision
Build a holistic system for human-level dexterous manipulation. Full stack envisioned: hardware that expresses rich contact, data collection preserving human interaction, control minimizing intent-execution gap, models absorbing multimodal supervision at scale, evaluation infrastructure enabling scalable + reproducible iteration. *Current scope-of-work focuses on modeling at the VLA level.*

### 3.2 Scope of work
**Body expert and hand expert both directly designed and trained at the VLA level.** No outsourcing of dexterity to a post-hoc correction module (which would be distribution-bounded by the VLA). Pretrained VLM/π weights are leveraged via a *deliberately composed pretraining recipe for data-efficient adaptation* (P4), with prior-preservation as one downstream lever. Every component learns at the VLA level, by imitation with flow matching.

### 3.3 Task philosophy
**Hand expert as a stabilization layer on top of architectural grounding**, where grounding is body's grasp/arm intent + backbone's visual/task embeddings (with VLM prior preserved). A contact-reaction sub-loop is a *further* low-level stabilization layer beneath the Hand expert, gated on only when contact retention demands sub-policy-loop reaction speed. Hand-level contact elevation remains the **differentiation claim**; the **deliverable** is the integrated VLA system.

### 3.4 Long-term task families
- **In-hand reorientation**: object rotation in the palm — the first demo, and the architectural validation
- **Tool articulation** (e.g. tagging machine, trigger tools): hold the tool, operate it with the fingers — the flagship demo
- **Diverse functional grasping**: nominal pose synthesis across objects — the generalization phase, later

---

---

## 4. Pillars [STABLE structure, LIVING content] [AGENT-INPUT]

**Five pillars (P0–P4).** P1, P2 and P4 are the architectural core; P0 (data)
is the upstream supporting pillar; P3 (world model) is a later-phase
capability bet.

Each pillar file owns its own scope, scouting lens, anti-topics, Decision Log
and tracked literature. This table is the index — what a pillar owns in one line, how many
decisions it holds, and where the rest of it lives. The ids themselves are
mapped in `context/CLAUDE.md`. A pillar's
scope restated here is a second copy to keep in step, so it is not restated.

| Pillar | Owns | Decisions | File |
|---|---|---|---|
| P0 — VLA Datasets & Benchmarks | the corpora and the instruments that measure on them; data is upstream of method | 4 | `context/P0.md` |
| P1 — Heterogeneous Body/Hand Action Expert | how the action decoder is split into more than one expert, on the anatomical seam and the temporal one | 11 | `context/P1.md` |
| P2 — Structured Multimodal Observation Fusion | what happens to sensing before it reaches the policy — spatial registration, per-finger contact attribution, the encoder | 5 | `context/P2.md` |
| P3 — World Model | how a predictive model of dynamics folds into the stack — role, integration, prediction space, conditioning | 5 | `context/P3.md` |
| P4 — Pretraining for Data-Efficient Adaptation | the choices upstream of deploy — lineage × corpus × recipe — and what they cost to protect afterwards | 5 | `context/P4.md` |

Retired: **D17**, **D18**. A retired number is never re-issued;
`linters/check-decision-refs.py` resolves it so already-published citations
keep working.

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

1 paper per month from an adjacent field that plausibly transfers. Rotating:
- **Month A**: continual learning / catastrophic forgetting / PEFT (P4 adjacency)
- **Month B**: VLA architecture advances broadly (π, OpenVLA, self-improving VLA)
- **Month C**: spatial-geometric / multimodal fusion representation (P2 adjacency)
- **Month D**: tactile sensing in prosthetics / neuroscience

---

*End.*
