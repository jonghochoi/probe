# Probe Scouting Report — Week 2026-16 [EXAMPLE, not real data]

**Run date:** 2026-04-18
**Agent version:** v0.1
**Papers scanned:** 47 from arXiv (cs.RO + cs.LG, last 14d) + 23 from citation graph + 8 from author watch
**Papers surfaced (score ≥3):** 3

> This is an illustrative example so you can see the expected output quality.
> Real runs will replace this file.

---

## Top picks

### 1. Residual Tactile Policies for Under-actuated Hands (arXiv:2604.xxxxx) [score 4/5]
- **Source:** citation-graph from pinned:Qi'23-Visuotactile
- **Connects to:** Q3 (reward shaping for 22-DOF) + H3 (residual policy) + H5 (action space)
- **What's genuinely new**: Applies residual RL on top of an analytical impedance controller *specifically* when the base controller is poor on contact-rich phases, and ablates the crossover point where residual helps vs. hurts.
- **Decision implication**: If the residual-helps threshold they find holds for Sharpa's tendon coupling, we should prototype residual-on-impedance before learning from scratch — could cut sample complexity 3–5×. But requires an analytical impedance baseline we don't yet have.
- **Failure mode to probe**: Their hand is 16-DOF fully-actuated. Sharpa's tendon coupling creates kinematic singularities their analytical baseline doesn't face; residual may need to absorb non-trivial singularity handling, which is exactly what we hoped to avoid.

### 2. Noise-aware Tactile Encoders via Masked Pretraining (arXiv:2604.yyyyy) [score 3/5]
- **Source:** keyword-sweep (tactile + self-supervised + manipulation)
- **Connects to:** Q2 (tactile state estimation) + H1 (Deform Map as latent)
- **What's genuinely new**: Masked-patch pretraining on tactile image stream, with explicit dropout augmentation during pretraining (not just fine-tuning). Shows latent stability under sensor failure is 2× better than CNN-from-scratch.
- **Decision implication**: Worth replicating on a small Deform Map pretraining corpus before full policy training — low cost (tens of GPU-hours), high info value for Q2. Consider this a prerequisite experiment, not a direct policy change.
- **Failure mode to probe**: Their dropout model is Bernoulli per-pixel; real Sharpa dropout may be spatially correlated (whole-finger dropout when cable noise spikes). Pretraining advantage may not transfer if the failure statistics differ.

### 3. The Signorini Gap: Measuring PhysX Contact Error on Soft Fingertips (arXiv:2604.zzzzz) [score 5/5]
- **Source:** author-watch (Yashraj Narang)
- **Connects to:** Q1 (contact model gap) — direct hit
- **What's genuinely new**: First quantitative measurement of PhysX point-contact error vs. FEM-simulated soft fingertip across 12 object geometries, with a proposed correction term usable as a residual loss during policy training.
- **Decision implication**: This is the closest thing to a ground-truth answer for Q1 we've seen. The correction term is plug-in with Isaac Lab. **Recommend: pin this paper, replace the empty 8th slot.** Then an early experiment: train two policies, one with and one without the correction term, compare sim2real gap on a fixed object set.
- **Failure mode to probe**: Their FEM reference is also a model — not ground truth. If real Deform Map disagrees with both PhysX and FEM, correction term may overfit to the FEM artifact. Need real-hardware calibration data to validate the correction itself.

---

## Cross-pollination pick (monthly only)

**Contact-implicit trajectory optimization for legged locomotion** (arXiv:2604.aaaaa)
Why included: Their contact-schedule implicit formulation is mathematically identical to the finger-gaiting problem. Not directly usable but a formulation worth borrowing for Q3 reward shaping — treating finger contact-make/break as implicit decision variables rather than explicit reward terms.

---

## Anomalies / low-confidence findings

- Two papers this week contradict on whether domain randomization range for friction should be *wider* or *narrower* for tactile-observing policies. One claims wider (more robust), one claims narrower (better sample efficiency with tactile feedback substituting for friction uncertainty). Needs deeper read; flagging for user.
- One paper (arXiv:2604.bbbbb) claimed SOTA on in-hand rotation with a 4-DOF hand — filtered out per anti-topics, but noting in case user wants to override.

---

## Candidate edits to research_context.md

- [x] **Pin paper #3 above (Signorini Gap) in empty slot 8.** Direct relevance to Q1.
- [ ] Consider adding "masked tactile pretraining" as an experimental prerequisite note under Q2.
- [ ] No change to anti-topics this week.
- [ ] H3 (residual policy) — no change yet, but paper #1 suggests the hypothesis should be narrowed to "residual helps *when analytical baseline is non-trivial*" rather than a blanket claim.

---

## Self-check

- Papers already covered in last 2 weeks' logs? None (this is week 1 of logging).
- Anti-topics filter enforced? Yes — filtered out 12 papers (6 mobile manipulation, 3 locomotion, 2 parallel-gripper, 1 pure teleop).
- At least one failure-mode / negative result paper? Partially — paper #1 includes ablation of when residual *hurts*, which counts. Next week aim for at least one paper that explicitly reports negative sim2real transfer.
