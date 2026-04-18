# Probe Scouting Report — Week 2026-W16 [EXAMPLE, not real data]

**Run date:** 2026-04-22
**Agent version:** v0.1
**Papers scanned:** 47 from arXiv (cs.RO + cs.LG, last 14d) + 23 from citation graph + 8 from author watch
**Papers surfaced (every dimension ≥ 2):** 3

> This is an illustrative example so you can see the expected output quality.
> Real runs will replace this file, and every run also produces `2026-W16-KO.md`.

---

## 📋 Scout Methodology

- **Author Watch** — 12 researchers from `research_context.md` §5, window 2026-04-08 → 2026-04-22. 8 candidates, 1 surfaced.
- **Citation-Graph Expansion** — 6 pinned papers from §4, citations from the last 8 weeks via `semantic-scholar.get_paper_citations`. 23 candidates, 1 surfaced.
- **Keyword Sweep** — `cs.RO` + `cs.LG`, last 14 days, queries: *tactile pretraining*, *residual policy dexterous*, *Sim2Real contact model*. Anti-topics filter (§7) dropped 12 papers. 47 candidates, 1 surfaced.
- No tool-call failures this run.

---

## 🥇 Paper 1 — PRIORITY ★★★

**The Signorini Gap: Measuring PhysX Contact Error on Soft Fingertips**
[arXiv:2604.zzzzz](https://arxiv.org/abs/2604.zzzzz) · Narang et al. · source: author-watch (Yashraj Narang)

### 🎯 (a) Q# / H# touched
Q1 (contact model gap) — direct hit.

### ✨ (b) What is genuinely new
First quantitative measurement of PhysX point-contact error vs. an FEM-simulated soft fingertip across 12 object geometries, with a proposed correction term usable as a residual loss during policy training.

### ⚙️ (c) Decision implication
Closest thing to a ground-truth answer for Q1 we have seen. The correction term is plug-in with Isaac Lab. Next week: train two policies with identical config, one with and one without the correction term (`env_cfg.contact.signorini_correction = True/False`), compare sim-to-real gap on a fixed object set.

### ⚠️ (d) Failure mode to probe first
Their FEM reference is itself a model — not ground truth. If the real Deform Map disagrees with both PhysX and FEM, the correction term may overfit to the FEM artifact. Cheapest sanity check: calibrate correction term against one real hardware contact pair before full policy training.

---

## 🥈 Paper 2 — PRIORITY ★★

**Residual Tactile Policies for Under-actuated Hands**
[arXiv:2604.xxxxx](https://arxiv.org/abs/2604.xxxxx) · Smith et al. · source: citation-graph from pinned:Qi'23-Visuotactile

### 🎯 (a) Q# / H# touched
Q3 (reward shaping for 22-DOF) + H3 (residual policy) + H5 (action space).

### ✨ (b) What is genuinely new
Applies residual RL on top of an analytical impedance controller *specifically* when the base controller is poor on contact-rich phases, and ablates the crossover point where residual helps vs. hurts.

### ⚙️ (c) Decision implication
If the residual-helps threshold holds for Sharpa's tendon coupling, prototype residual-on-impedance before learning from scratch — could cut sample complexity 3–5×. Requires an analytical impedance baseline we do not yet have; build that first.

### ⚠️ (d) Failure mode to probe first
Their hand is 16-DOF fully-actuated. Sharpa's tendon coupling creates kinematic singularities their analytical baseline does not face; the residual may need to absorb non-trivial singularity handling, which is exactly what we hoped to avoid.

---

## 🥉 Paper 3 — PRIORITY ★

**Noise-aware Tactile Encoders via Masked Pretraining**
[arXiv:2604.yyyyy](https://arxiv.org/abs/2604.yyyyy) · Kim et al. · source: keyword-sweep (tactile + self-supervised + manipulation)

### 🎯 (a) Q# / H# touched
Q2 (tactile state estimation) + H1 (Deform Map as latent).

### ✨ (b) What is genuinely new
Masked-patch pretraining on the tactile image stream with explicit dropout augmentation during pretraining (not just fine-tuning). Reports latent stability under sensor failure 2× better than a CNN trained from scratch.

### ⚙️ (c) Decision implication
Worth replicating on a small Deform Map pretraining corpus before full policy training — low cost (tens of GPU-hours), high info value for Q2. Treat as a prerequisite experiment, not a direct policy change.

### ⚠️ (d) Failure mode to probe first
Their dropout model is Bernoulli per-pixel; real Sharpa dropout is probably spatially correlated (whole-finger dropout when cable noise spikes). The pretraining advantage may not transfer if the failure statistics differ.

---

## 🌱 Paper 4 — CROSS-POLLINATION (monthly pick)

**Contact-implicit Trajectory Optimization for Legged Locomotion**
[arXiv:2604.aaaaa](https://arxiv.org/abs/2604.aaaaa) · Tassa et al. · adjacent field: legged locomotion (per §8)

### 🎯 (a) Q# / H# touched
Q3 (reward shaping) — indirect; formulation borrow only.

### ✨ (b) What is genuinely new
Contact-schedule as an implicit decision variable rather than an explicit reward term. Mathematically identical to the finger-gaiting problem we hand-tune reward shaping for.

### ⚙️ (c) Decision implication
Not directly usable, but the formulation is worth borrowing for Q3: treat finger contact make/break as implicit decision variables in the reward, replacing the hand-tuned contact-phase reward terms. Prototype on a 2-finger pinch task before committing to the full 22-DOF.

### ⚠️ (d) Failure mode to probe first
Their optimizer is MPC over a physics model; we run model-free RL. The implicit formulation may not survive translation into a reward signal — the gradient may be too sparse.

---

## 📊 Scoring Summary

| # | Paper | Link | Relevance (0–3) | Novelty (0–3) | Reproducibility (0–3) | Sim2Real (0–3) | Total (/12) |
|---|-------|------|:---:|:---:|:---:|:---:|:---:|
| 1 | The Signorini Gap | [arXiv:2604.zzzzz](https://arxiv.org/abs/2604.zzzzz) | 3 | 3 | 3 | 2 | **11** |
| 2 | Residual Tactile Policies | [arXiv:2604.xxxxx](https://arxiv.org/abs/2604.xxxxx) | 3 | 2 | 2 | 2 | **9** |
| 3 | Noise-aware Tactile Encoders | [arXiv:2604.yyyyy](https://arxiv.org/abs/2604.yyyyy) | 2 | 2 | 2 | 2 | **8** |
| 4 | Contact-implicit Traj. Opt. | [arXiv:2604.aaaaa](https://arxiv.org/abs/2604.aaaaa) | 2 | 3 | 2 | 1 | **8** (cross-pollination, Sim2Real excluded) |

---

## 🚫 Candidate Papers That Did Not Pass Filter

| Paper | Link | Reason dropped |
|-------|------|----------------|
| SOTA In-hand Rotation with a 4-DOF Hand | [arXiv:2604.bbbbb](https://arxiv.org/abs/2604.bbbbb) | Anti-topic (§7): parallel-gripper / low-DOF. Flagging in case user wants to override. |
| Mobile-manipulation for Household Tasks | [arXiv:2604.ccccc](https://arxiv.org/abs/2604.ccccc) | Anti-topic (§7): mobile manipulation. |
| Improved PPO for Locomotion | [arXiv:2604.ddddd](https://arxiv.org/abs/2604.ddddd) | Anti-topic (§7): primary task is locomotion. |
| Friction-randomized In-hand Rotation | [arXiv:2604.eeeee](https://arxiv.org/abs/2604.eeeee) | Novelty < 2 (delta over pinned:Qi'23-Visuotactile is marginal). |

---

## 💡 Context Suggestions

### 📌 Pinned literature
Pin Paper 1 — **The Signorini Gap** ([arXiv:2604.zzzzz](https://arxiv.org/abs/2604.zzzzz)) — in the currently empty slot 8. Direct relevance to Q1.

### 📌 Hypotheses
H3 (residual policy) — consider narrowing to "residual helps *when the analytical baseline is non-trivial*" rather than a blanket claim. Evidence: Paper 2 ablation.

### 📌 Anti-topics
No change this week. Two papers contradict on whether DR friction range should be *wider* or *narrower* for tactile-observing policies — not an anti-topic signal, but worth a user deep-read before committing.

### 📌 Researchers to follow
No change this week. Narang's author-watch signal remains strong (Paper 1).

---

## 🔄 Week-over-Week Synthesis

- Papers already covered in last 2 weeks: none (this is week 1 of logging).
- Anti-topics filter caught 12 papers (6 mobile manipulation, 3 locomotion, 2 parallel-gripper, 1 pure teleop) — within the healthy exclusion rate.
- Open-question status: Q1 (contact model gap) moved the most this week thanks to Paper 1; Q2 moved partially via Paper 3 as a prerequisite experiment.
- Negative-result coverage: partial — Paper 2 includes an ablation of *when* residual hurts. Next week aim for at least one paper that explicitly reports failed Sim2Real transfer.
