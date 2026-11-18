# Probe
> Research scout for hand-centric dexterous manipulation.

---

# Research Context — Hand-centric Dexterous Manipulation

> **Agent usage**: This file is the *static, cross-cutting* **global anchor** — Purpose, Long-term Context, the Pillars overview, and cross-pillar references. Per-pillar working context (Open Questions, Tracked Literature, Anti-topics) is **owned by `context/P0–P5.md`**, which the retrieval agent reads (never writes). Findings go to `scouting/P#/YYYY-MM-DD.md` (one file per run, per pillar).

---

## 0. How to use this file [STABLE]

**What lives where**
- This document (`MASTER.md`) is the **global anchor**: cross-cutting content that is not specific to one pillar. It is *not* a superset of the pillar files.
- `context/P0–P5.md` are the **owners** of their pillar's Open Questions, Tracked Literature and Anti-topics. Edit the pillar file for pillar content; edit this anchor only for cross-cutting content.

**Section markers**
- `[STABLE]`: changes rarely (purpose, scope)
- `[LIVING]`: updated as research progresses
- `[AGENT-INPUT]`: retrieval agent conditions on this — keep signal-dense

**Update protocol**
- Purpose / Scope of work: change only with deliberate review (semantic shift, not phrasing)
- Pillars: structure stable; the open questions and their threads evolve as evidence accumulates

**Output formatting & authoring rules**
Output format is one contract per track — `scouting/AUTHORING.md`, `analysis/AUTHORING.md`, `comparison/AUTHORING.md`. The agent reads its track's contract before producing any output. Do not duplicate formatting rules here; edit the contract instead.

**Audience**: maintainer (self, future-self) + AI retrieval agent + future collaborators. Keep terminology accessible without sacrificing precision.

---

## 1. Purpose [STABLE]

This document serves *two coupled functions*:

1. **Filter (outward)** — enables the retrieval agent and collaborators to surface external content (papers, methods, ideas) that bears on the pillars' open questions, and to set the rest aside. Requires signal-density and structured fields.
2. **Anchor (inward)** — keeps the open questions each pillar asks and the threads followed on each. Counters drift when external noise (trends, hype) pulls: a paper is read for what it adds to a question, not for whether it agrees with an answer.

**Audience scope**: future-self + AI retrieval agent + future collaborators
**Question depth**: skeleton (the questions that shape a pillar; not every sub-question)

---

## 2. Long-term Context [STABLE → semi-LIVING] [AGENT-INPUT]

### 2.1 Field
Human-level dexterous manipulation spans a full stack — hardware that
expresses rich contact, data collection that preserves human interaction,
control, models that absorb multimodal supervision at scale, and evaluation
that makes iteration reproducible. The research this repo scouts can sit
anywhere on it.

### 2.2 Scope of work
The current scope is **hand-centric dexterous manipulation at the VLA level** —
how each part of a VLA is built, what each choice buys and costs on a
dexterous, contact-rich task, and the human-to-robot data collection it learns
from: the six pillars of §3.
The rest of the stack is read where it bears on a pillar question and is not
scouted for its own sake.

The context holds questions about this scope, never an answer or a bet on
one: the common default of a VLA part is a **thread to be measured
against**, never a position to argue against, and where the operator's
stance lives instead is `context/CLAUDE.md`'s rule.

---

## 3. Pillars [STABLE structure, LIVING content] [AGENT-INPUT]

**Six pillars (P0–P5)**, none ranked above another.

Each pillar file owns its own scope, scouting lens, anti-topics, open questions
and tracked literature. This table is the index — what a pillar owns in one
line, how many questions it holds, and where the rest of it lives. The ids
themselves are mapped in `context/CLAUDE.md`. A pillar's scope restated here
is a second copy to keep in step, so it is not restated.

| Pillar | Owns | Questions | File |
|---|---|---|---|
| P0 — VLA Datasets & Benchmarks | the corpora and the instruments that measure on them | 3 | `context/P0.md` |
| P1 — Heterogeneous Action Expert Decomposition | how the action decoder is split into more than one expert, and the questions that stand split or not | 4 | `context/P1.md` |
| P2 — Observation Design | what happens to sensing before it reaches the policy — spatial registration, per-finger contact attribution, the encoder, where in the view the policy reads | 5 | `context/P2.md` |
| P3 — World Model | how a predictive model of dynamics folds into the stack — role, integration, prediction space, conditioning | 4 | `context/P3.md` |
| P4 — Pretraining for Data-Efficient Adaptation | the questions upstream of deploy — corpus × recipe × adaptation — and what they cost to protect afterwards | 5 | `context/P4.md` |
| P5 — Retargeting & Human-in-the-Loop Data Collection | how human motion becomes robot training data — the retargeting map, its yield, the human-in-the-loop handover, where operator time goes | 4 | `context/P5.md` |

Retired: **D17**, **D18**, **D6ZD**, **D4NT**, **D5QT**, **D4QX**, **D5SH**, **D5DQ**, **D8SD**, **D9WZ**, **D7VC**, **D5ZL**.
A retired id is never re-issued. When a question folds into another, every
citation of the retired id in `analysis/`, `comparison/` and `scouting/` is
rewritten to the id it folded into — or dropped, where it became a premise
rather than part of another question — so no published page points at it.

---

## 4. Venue Priority [AGENT-INPUT]

| Tier | Venues |
|------|--------|
| 1 | CoRL, RSS |
| 2 | ICRA, IROS |
| 3 | T-RO, RA-L (journal — archival weight) |
| 4 | arXiv raw (cs.RO, cs.LG) — noisiest, lowest default weight |
| — | NeurIPS/ICML robotics workshops — read only if pinned author |

---

## 5. Cross-pollination Budget [AGENT-INPUT]

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
