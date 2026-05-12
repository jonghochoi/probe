# Probe
> Research scout for hand-centric dexterous manipulation.

---

# Research Context — Hand-centric Dexterous Manipulation

> **Version**: v4.0 (2026-05-12)
> **Maintainer**: \<your-name\>
> **Agent usage**: This is the *static* context. The retrieval agent reads (never writes) this file. Weekly findings are appended to `research_log/YYYY-WW.md` instead.

---

## 0. How to use this file [STABLE]

**Section markers**
- `[STABLE]`: changes rarely (identity, purpose, hardware)
- `[LIVING]`: updated as research progresses
- `[AGENT-INPUT]`: retrieval agent conditions on this — keep signal-dense

**Update protocol**
- Identity / Purpose: change only with deliberate review (semantic shift, not phrasing)
- Pillars: structure stable; tracked items within can evolve at Revisit Checkpoints (CP1–CP5)
- Decision Log: append-only. Decisions are *first-attempt defaults* with explicit deferred candidates and revisit triggers
- Tracked Literature: rebalanced quarterly. Hard cap 8 pinned per pillar; replace, don't append
- Competitor/Kindred Monitoring: review at every CP

**Output formatting & translation rules**
All formatting rules (emoji system, link format, Korean translation principles) are consolidated in **`docs/STYLE_GUIDE.md`** — the single source of truth. The agent must read `docs/STYLE_GUIDE.md` before producing any output. Do not duplicate formatting rules here; edit `docs/STYLE_GUIDE.md` instead.

**Audience**: maintainer (self, future-self) + AI retrieval agent + future collaborators. Keep terminology accessible without sacrificing precision.

**Current state**: ⏸️ paused before step (iii) implementation entry. Knowledge consolidation phase active. All open items have v1 defaults; no hard blocker. See Appendix C.1 for the four-category classification of remaining insufficiencies.

**Re-entry checklist** (consult before resuming step iii):
- [ ] Category A knowledge gaps consolidated (esp. RL experimental rigor + π0 internals + Sharpa tactile sim)
- [ ] Category B information acquired (esp. compute budget + team capacity)
- [ ] §10 Competitor monitoring scan (DexReMoE / CATFA / Sharpa VTLA / π0.7 release)
- [ ] Decision Log scan: any deferred candidate's trigger now observable?

---

## 1. Identity [STABLE] [AGENT-INPUT]

> Most VLA-style policies attempt to converge on dexterity via a **monolithic action decoder + vision-dominant observation**. I argue that **an arm-hand anatomically heterogeneous decoder (both experts directly designed and trained) + hand-level contact-grounded supervision/observation** is what determines the ceiling of dexterity. Task specification stays goal-centric (arm-hand integrated); on top of the upstream context supplied by body and backbone (grasp intent, visual embedding, task intent), the hand's internal language of control, loss, and observation is elevated toward contact.

**Decomposition**
- *Antagonist*: monolithic VLA decoders + vision-dominant observation
- *Protagonist*: anatomically heterogeneous decoder + hand-level contact elevation
- *Stays goal-centric*: task specification (arm-hand integrated)
- *Elevated to contact*: hand's internal control / loss / observation language
- *Upstream context source*: body (grasp intent, arm action) + backbone (visual embedding, task intent) — pretrained anchoring optional, not required

> *Maintainer's anchor (Korean original, preserved for self-reference)*:
> 대다수의 VLA-style policy는 monolithic action decoder + vision-dominant observation으로 dexterity를 수렴시키려 하지만, 나는 arm-hand anatomically heterogeneous decoder + hand-level contact-grounded supervision/observation이 dexterity의 ceiling을 결정한다고 본다. Task spec은 arm-hand 통합 goal-centric으로 유지하고, body·backbone이 공급하는 upstream context 위에서 손 내부의 control·loss·observation 언어를 contact 쪽으로 elevation한다.

---

## 2. Purpose [STABLE]

This document serves *two coupled functions*:

1. **Filter (외향)** — enables the retrieval agent and collaborators to surface external content (papers, methods, ideas) aligned with the maintainer's identity, and to reject the rest. Requires signal-density and structured fields.
2. **Anchor (내향)** — records current commitments, open questions, and falsifiability conditions. Counters drift when external noise (trends, hype) pulls. Requires explicit decision rationale and revisit triggers.

**Audience scope**: future-self + AI retrieval agent + future collaborators
**Decision-log depth**: skeleton (key branchpoints recorded with rationale; not exhaustive)

---

## 3. Long-term Context [STABLE → semi-LIVING]

### 3.1 Vision
Build a holistic system for human-level dexterous manipulation. Full stack envisioned: hardware that expresses rich contact, data collection preserving human interaction, control minimizing intent-execution gap, models absorbing multimodal supervision at scale, evaluation infrastructure enabling scalable + reproducible iteration. *Current scope-of-work focuses on modeling.*

### 3.2 Scope of work
**Body expert and hand expert both directly designed and trained.** No outsourcing of either to an external module (with the exception that leveraging pretrained weights from e.g. π is a separate, optional sub-decision). Hand-level contact elevation is the **differentiation claim**; the **deliverable** is the integrated system (body + hand + coordination).

### 3.3 Task philosophy
**Hand expert as a stabilization layer on top of architectural grounding**, where the grounding is provided by body's grasp decision + backbone's visual/task embeddings (with optional pretrained anchoring). Hand expert is not the sole source of dexterity; its identity-defining role is *contact-grounded execution refinement*.

### 3.4 Long-term task families
- **In-hand reorientation** (HORA-style): object rotation in palm — first demo, architectural validation
- **Tool articulation** (e.g., tagging machine, trigger tools): hold tool + finger operation — identity flagship demo (phase 2, CP3)
- **Diverse functional grasping**: appropriate nominal pose synthesis across objects — generalization phase (later)

### 3.5 Demo task phasing
- **Phase 1**: in-hand cube rotation (architectural validation of split + tactile + contact reward, measurable falsifier)
- **Phase 2 (CP3)**: tool articulation (identity flagship; validates body-hand coordination + finger asymmetry); 5-tool evaluation set matching CATFA precedent (arXiv:2509.23075)
- **Phase 3 (CP5)**: cross-object generalization

---

## 4. Target Hardware & Stack [STABLE]

### 4.1 Hardware
**Hand**
- Near-term: **Sharpa Hand** (22-DOF, no wrist DOF) — fingertip tactile (Deform Map: vision-based, ~320×240 per fingertip @30Hz)
- Alternate near-term: **xhand** (dexterous hand, no wrist DOF)
- Mid-term (2H 2026+): **in-house custom hand** (spec TBD — DOF, tendon layout, sensor modality, control rate)

**Arm**: not yet committed. Generic 6–7 DOF assumed in design (last 3 DOF treated as "wrist", attributed to hand expert per D2).

**Design constraint**: avoid Sharpa-specific lock-in. Tactile encoder uses *swappable sensor head + common token format* (P2).

### 4.2 Simulation
- Primary: **NVIDIA Isaac Sim + Isaac Lab** (PhysX rigid-body, Signorini-Coulomb contact)
- Secondary (deferred to CP2+): **MuJoCo MJX** as alternative for differentiable contact
- Visuotactile sim: Sharpa Deform Map sim-side rendering — protocol TBD at CP2 prerequisite (Chen et al. 2024 / Akinola Isaac Gym tactile library as reference)

Known gap: PhysX point contact vs. real fingertip viscoelastic deformation (P4 scope). Contact-Aware Neural Dynamics (arXiv:2601.12796) directly documents this gap.

### 4.3 Training
- GPU-parallel RL, 8,192–16,384 envs in current runs
- Primary algorithm: **PPO**
- Backbone: **Physical Intelligence π** (π0 / π0.5) — used as starting point; not exclusively pretrained-anchored (action experts may be trained from scratch — see D3)

---

## 5. Pillars [STABLE structure, LIVING content] [AGENT-INPUT]

Five pillars derived from identity.

### P1. Heterogeneous Action Decoder
**Scope**: body/hand decoder split, information-sharing module, π backbone integration. The architectural core of identity.

**Identity tie**: heterogeneous decoder claim → this pillar.

**Tracked items**: sequential direction (D1), wrist boundary (D2), action expert partition (D3), tactile fusion (D4), backbone freeze (D5), proprioception split (D6), flow matching coordination (D7), sharing module mechanism (D8), gradient conflict mitigation (D9).

**Anti-topics**: monolithic VLA decoders without split, router-based MoE (different pattern), multi-expert ablations without single-expert comparison.

**Literature anchor**: π0/π0.5 (backbone); DexterityGen, MoDE-VLA, DexVLA, Hierarchical RL Tool Articulation, Shared-Autonomy Arm-Hand VLA, TacFiLM (FiLM fusion). See §8.1.

### P2. Tactile-Dominant Visuotactile Encoder
**Scope**: hand-level fusion of tactile + vision, with tactile as the dominant signal (not augmentation).

**Identity tie**: hand-level "observation elevation".

**Tracked items**: Deform Map preprocessing (hardware-specific CNN), late-fusion mechanism (concat → FiLM with $a_b$), cross-hardware portability (swappable sensor head + common token format), encoder pretraining strategy, contact-grounded representation loss, force-prediction aux as deferred (D10 v2). See D10.

**Anti-topics**: vision-only manipulation, pure tactile-only (e.g., TacTip lineage without vision).

**Literature anchor**: **SaTA (uses Sharpa Wave)**, TacFiLM, Sparsh, ViTacFormer, AdapTac, GelFusion, XL-VLA, Sparsh-skin. See §8.2.

### P3. Contact-Grounded Supervision
**Scope**: design of reward/loss for body and hand. Body remains goal-pose-based; hand elevated to contact-aligned.

**Identity tie**: hand-level "supervision elevation".

**Tracked items**: body reward composition (goal-pose + smoothness + collision), hand reward 3-term core (task success + contact maintenance + slip penalty), reward synthesis methodology (hand-crafted; automatic synthesis as deferred), task/contact reward balance, demonstration integration with π. See D11. Multi-task loss balancing handled in P1 (D9).

**Anti-topics**: pure task-goal reward, contact-agnostic automatic reward synthesis (Eureka-style) without contact-aware variant.

**Literature anchor**: HORA, AnyRotate, Eureka, DrEureka, CCGE, Humanoid Sim2Real (contact+object goals decomposition), DAPG, DemoGrasp. See §8.3.

### P4. Sim-to-Real for Contact Dynamics
**Scope**: closing the PhysX contact model gap vs. real viscoelastic contact. DR · system ID · RMA-family adaptation, contact-specific.

**Identity tie**: contact elevation must transfer (sim-only success ≠ identity validation).

**Tracked items**: contact-relevant DR parameters (**static_friction + dynamic_friction** + contact stiffness + restitution + mass + surface compliance + actuator delay/noise), DR range strategy (wide ranges v1; narrowing via system ID at CP2+), adaptation mechanism (**RMA-family teacher-student**; **A-RMA Phase 3** as primary deferred). See D12.

**Anti-topics**: locomotion sim2real, contact-agnostic DR.

**Literature anchor**: RMA (legged), RMA for Manipulator Arms, A-RMA, OpenAI Solving Rubik's Cube (ADR), Static Friction Sim2Real, Contact-Aware Neural Dynamics, Closing the Reality Gap, General-purpose Sim2Real for Visuotactile. See §8.4.

### P5. Task Definition & Falsifiable Evaluation
**Scope**: single-skill demo selection, evaluation protocol, metrics, falsifier quantitative thresholds. Arm-hand integrated scope.

**Identity tie**: must isolate split contribution and tactile contribution to validate identity claim.

**Tracked items**: first demo task (in-hand cube rotation), phase-2 task (tool articulation; 5 articulated tools matching CATFA precedent), **4-condition 2×2 factorial ablation** (monolithic / +tactile / split / full), contact-precision metrics (slip count + pose stability), throughput metrics (consecutive rotation count + rotations/sec), coordination metric ($a_b \times a_h$ cross-correlation), **per-metric falsifier** (v1: ≥5% absolute improvement on at least one contact-precision metric; v2: ≥3% additional). **Grouped Blind Ensemble + AutoEval automation** in protocol. See D13.

**Anti-topics**: benchmark-only evaluation (no real-world), single-metric aggregate assessment.

**Literature anchor**: OpenAI Learning Dexterous In-Hand, DexArt, In-Hand Articulated Tools (CATFA), DexReMoE, RoboEval, Grounding Sim2Real VLA, AutoEval, NVIDIA Robot Policy Evaluation. See §8.5.

---

## 6. Decision Log [LIVING] [AGENT-INPUT]

All architectural commits recorded with: options considered, v1 choice, rationale, deferred candidates with revisit triggers and checkpoints.

### 6.1 Revisit Checkpoints (CP1–CP5)
Reusable temporal anchors. Most deferred decisions trigger at one of these.

- **CP1**: v1 first ablation analysis (split vs monolithic on in-hand rotation, sim)
- **CP2**: in-hand rotation first real-world demo result analysis
- **CP3**: tool articulation demo entry (phase 2; 5-tool evaluation set)
- **CP4**: hardware transition (Sharpa → xhand → in-house)
- **CP5**: cross-object generalization phase entry

**CP2 prerequisite**: tactile sim2real protocol verified (Chen et al. 2024 lineage) + static friction range estimation completed. Without these, CP2 entry is premature.

### 6.2 Decisions

#### [D1] Sequential conditioning direction (P1)
- **Options**: body→hand, hand→body, iterative, bidirectional
- **v1**: body→hand (literal sequential)
- **Rationale**: training stability + literature compatibility (DexterityGen) + cleanest split-effect isolation
- **Deferred**
  - iterative / bidirectional → trigger: slip detection fails to reshape arm motion in time / checkpoint: **CP1 + CP2**

#### [D2] Wrist boundary (P1)
- **Options**: A (wrist→body), B-1 (wrist→hand, body=joint-space minus wrist), B-2 (wrist→hand, body=Cartesian EE target), C (separate wrist expert), D (split wrist)
- **v1**: B-1
- **Rationale**: wrist contact-mediated learning under contact-grounded supervision (P3 elevation); π reuse cleanest with joint-space partition
- **Deferred**
  - B-2 (Cartesian body) → trigger: hardware transition or cross-arm generalization need / checkpoint: **CP4 + CP5**
  - A (wrist→body) → trigger: first demo becomes pick-and-place-like (contradicts current in-hand rotation/tool articulation phasing) / checkpoint: **CP3**

#### [D3] Action expert partition (P1; π weight reuse #1)
- **Options**: (i) slice partition + FT both sides, (ii) body re-init only, (iii) both re-init, (iv) distillation from monolithic π
- **v1**: (i) slice partition + FT
- **Rationale**: maximally preserves π's manipulation prior; cleanest baseline for split-vs-monolithic comparison; transitionable to (ii) at B-2 migration
- **Deferred**
  - (ii) body re-init → trigger: B-2 migration imminent / checkpoint: **CP4**
  - (iv) distillation → trigger: π architectural surgery overhead becomes prohibitive / checkpoint: **CP1**
- **Note**: §14.C documents the unresolved sub-reading (Repurpose vs Subdivide) that must be decided at CP1 code entry.

#### [D4] Tactile fusion strategy (P1; π weight reuse #3)
- **Options**: early fusion (backbone input), late fusion (hand head only), both
- **v1**: late fusion (hand head only)
- **Rationale**: training stability + minimal backbone perturbation + identity-aligned (hand-level tactile dominance)
- **Deferred**
  - early fusion → trigger: cross-modal interaction bottleneck for generalization / checkpoint: **CP5**
  - both → trigger: late fusion shows vision-dominance / tactile-underweighting in contact tasks / checkpoint: **CP1**

#### [D5] Backbone freeze strategy (P1; π weight reuse #2)
- **Options**: (a) full freeze, (b) full FT, (c) LoRA/PEFT, (d) selective layer FT
- **v1**: (a) full freeze
- **Rationale**: late tactile fusion → backbone receives only π-trained modalities → no adaptation pressure; minimum delta
- **Deferred**
  - (c) LoRA → trigger: backbone representation insufficient for new modality combinations / checkpoint: **CP1**

#### [D6] Proprioception split (P1; π weight reuse #4)
- **Options**: (i) unified prop encoder, (ii) split prop encoder, (iii) unified + hand-prop direct injection
- **v1**: (i) unified (π standard)
- **Rationale**: π reuse direct; minimum delta
- **Deferred**
  - (iii) hand-prop direct injection → trigger: finger-level coordination bottlenecked by backbone information flow / checkpoint: **CP2 (in-hand rotation)**

#### [D7] Flow matching coordination (P1; π weight reuse #5)
- **Options**: (a) shared flow + coupled denoising, (b) independent flows, (c) coupled flow (single network), (d) hierarchical flow
- **v1**: (d) hierarchical flow (body completes $K$-step denoising → $a_b$ → hand denoises conditioned on $a_b$)
- **Rationale**: literal implementation of body→hand sequential conditioning (D1); clean interface
- **Deferred**
  - (a) coupled denoising → trigger: D1 v2 (iterative/bidirectional) transition / checkpoint: **CP1, alongside D1 v2**
  - (c) coupled flow (single network) → trigger: latency budget pressure / checkpoint: **CP3**

#### [D8] Sharing module mechanism (P1.4)
- **Options for injection**: (A) concat, (B) FiLM, (C) cross-attention, (D) token-level interface
- **Options for what flows**: (i) $a_b$ only, (ii) body hidden state, (iii) both
- **Options for depth**: (α) single point, (β) multi-layer
- **v1**: (B) FiLM with $a_b$ → ($\gamma, \beta$) modulating hand head input at (α) single point
- **Rationale**: MLP-style hand head + minimum delta + sufficient expressivity for first experiment
- **Architectural assumption**: hand head is MLP-style. Transformer-style would shift default to (C) cross-attention.
- **Deferred**
  - (C) cross-attention → trigger: FiLM bottleneck (hand under-utilizes body conditioning) OR hand head restructured to transformer / checkpoint: **CP1**
  - (ii) hidden state injection → trigger: D7 v2 entry / checkpoint: **CP1 alongside D7 v2**
  - (β) multi-layer → trigger: single-point conditioning info bottleneck / checkpoint: **CP1**
  - (A) concat → trigger: rarely (FiLM strictly superior in literature) / checkpoint: —
  - (D) token-level → trigger: VLA backbone transition requires modular consistency / checkpoint: **CP4**

#### [D9] Gradient conflict mitigation (P1.5)
- **Options**: (A) vanilla weighted sum, (B) PCGrad, (C) GradNorm, (D) stop-gradient on FiLM input, (E) sequential training
- **v1**: (A) vanilla weighted sum, $w_b = w_h = 1$, with gradient cosine similarity monitoring on body-hand losses (shared params)
- **Rationale**: body head thin (D3) → limited conflict capacity; FiLM modulation small; cosine monitoring provides quantitative trigger
- **Deferred**
  - (B) PCGrad → trigger: cosine similarity persistently negative + unstable training / checkpoint: **CP1**
  - (C) GradNorm → trigger: loss magnitude imbalance stalls training / checkpoint: **CP1**
  - (D) Stop-gradient → trigger: B/C insufficient and hand→body coupling judged harmful / checkpoint: **CP1 + ablation**
  - (E) Sequential training → trigger: all above fail / checkpoint: **CP2** (last resort)
- **Note**: tightly connected to P3 (hand reward magnitude affects loss balance)
- **Falsifier caveat**: if conflict is severe, evidence for "split > monolithic" depends on which mitigation restores performance — must be reported explicitly

#### [D10] P2 skeleton — Tactile-Dominant Encoder
- **Encoder**: hardware-specific CNN on Deform Map → per-fingertip token → hand-side aggregate (mean pool)
- **Fusion mechanism**: concat → FiLM with $a_b$ (D8-consistent)
- **Portability**: swappable sensor head + common token format (architectural commit, not deferred)
- **Pretraining**: random init v1
- **Aux loss v1**: contact-binary + slip-binary heads, light weight (architectural commit, not deferred)
- **Aux loss v2 (deferred candidate)**: future force prediction head (AdapTac-style, arXiv:2505.13982) → trigger: contact-binary/slip-binary saturation; need richer signal / checkpoint: **CP1**
- **Deferred** (see Pillar P2 tracked items): geometric feature extraction, frequency decomposition, cross-attention fusion, abstraction layer, Sparsh/T3 pretraining, force matching aux, deformation regression aux, vision-tactile contrastive
- **Two non-negotiable commitments**: (1) avoid Sharpa-specific lock-in, (2) encoder must preserve contact-relevant features

#### [D11] P3 skeleton — Contact-Grounded Supervision
- **Body reward**: goal-pose tracking + smoothness + collision
- **Hand reward**: task success (sparse) + contact maintenance (dense) + slip penalty (dense) — 3-term core (architectural commit, not deferred)
- **Synthesis**: hand-crafted contact-aware (architectural commit; H2 hypothesis testing setting)
- **Task/contact balance**: task primary ($w_{task} \gg w_{shaping}$)
- **Demo integration**: π prior only v1 (no additional task-specific demos)
- **Deferred candidates (priority ordered)**:
  1. **CP1 — Eureka/DrEureka contact-aware variant**: literature evidence (DrEureka 300% on throughput) justifies; reward search budget savings
  2. **CP1 — Force distribution matching aux**: AdapTac-style future force prediction (cross-references D10 v2)
  3. **CP3 — Contact-pattern matching score**: CCGE-style finger-region coverage reward (arXiv:2603.10971)
  4. **CP2/CP3 — Few-shot demos + BC loss (DAPG-style)**: activate if 0-demo v1 underperforms
  5. Annealing schedule / dynamic weighting / human video demos: additional deferred
- **Two non-negotiable commitments**: (1) hand reward must include contact-grounded shaping, (2) hand-crafted design takes priority (automatic synthesis is v2)

#### [D12] P4 skeleton — Sim-to-Real for Contact
- **DR parameters**: **static_friction + dynamic_friction** (split, evidence: arXiv:2503.01255) + contact stiffness + restitution + mass + inertia + surface compliance + actuator delay/noise
- **DR range**: wide ranges (literature-grounded); narrowing deferred to CP2
- **Adaptation**: **RMA-family teacher-student** with contact-relevant extrinsics (architectural commit)
- **Deferred candidates (priority ordered)**:
  1. **CP2 (pre sim→real) — A-RMA Phase 3 fine-tuning**: re-adapt base policy on imperfect ẑ (Smith/Kew/Peng/Ha/Tan/Levine)
  2. **CP2 (post-real-demo) — Static-friction-aware DR scheduling**: separate schedule management for friction (arXiv:2503.01255)
  3. **CP3 — Learned contact correction**: overcome pure DR limits (Contact-Aware Neural Dynamics, arXiv:2601.12796)
  4. **CP4 (hardware transition) — Visuotactile sim-side rendering retooling**: Chen et al. 2024 protocol + Akinola Isaac Gym tactile library
  5. Differentiable contact sim (MuJoCo MJX) / meta-RL adaptation: subsequent
- **Caveat**: most P4 decisions activate at CP2; this pillar is plan, not current implementation
- **Two non-negotiable commitments**: (1) DR targets must include contact-relevant parameters, (2) RMA-family adaptation adopted

#### [D13] P5 skeleton — Task & Evaluation
- **First demo**: in-hand cube rotation, 50–100g, multiple friction ranges, arbitrary axis target, angular error < 10°, episode 5s
  - **CP1 (sim)**: 30 trials/condition
  - **CP2 (real-world)**: 50+ trials/condition for statistical power
- **Tool articulation (phase 2)**: 5 articulated tools (CATFA precedent matching, arXiv:2509.23075); concrete tool list TBD at CP3
- **Ablation**: 4-condition 2×2 factorial — (a) monolithic / (b) +tactile / (c) split / (d) full
  - Decomposition: split contribution = (c)−(a); tactile contribution = (b)−(a); interaction = (d)−(b)−(c)+(a)
- **Metric set**
  - Primary contact-precision metrics: slip count, pose stability — H2 validation
  - Primary throughput metrics: consecutive rotation count (OpenAI/HORA/DrEureka standard), rotations/sec — field comparison
  - Coordination metric: arm-hand action cross-correlation $\text{corr}(a_b(t), a_h(t))$ — deeper P1 split validation
  - Robustness metric (CP2+): success drop under perturbation (CATFA precedent)
- **Falsifier (P1 anchor, per-metric)**
  - **v1 rejection**: split architecture fails to achieve ≥5% absolute improvement on at least one contact-precision metric (slip count OR pose stability). Per-metric, not aggregate.
  - **v2 rejection**: full architecture fails to achieve ≥3% additional improvement over split on at least one contact-precision metric
  - Supplementary condition: coordination metric must show meaningful improvement over monolithic — supports the *how* of split rationale
  - Both stages failing → heterogeneous decoder hypothesis rejected
- **Evaluation protocol**
  - **Grouped Blind Ensemble** (BeingBeyond 2026): operator blinding + separation of execution/judgment → reduces experimenter bias
  - **AutoEval-style automated scoring** (arXiv:2503.24278): CP1 sim-only ablation automation; CP2 real-world is manual + blind
- **Deferred** (see Pillar P5): diverse objects, tighter angular thresholds, additional ablation conditions, contact-pattern matching score, force closure margin, stricter falsifier thresholds, statistical framework (bootstrap CIs)
- **Three non-negotiable commitments**: (1) 4-condition 2×2 factorial ablation, (2) per-metric falsifier with quantitative threshold, (3) phased demo (in-hand rotation → tool articulation)

#### [D14] Nominal pose source
- **v1**: (α) π pretrained weight (architecturally internal upstream context via D3 slice partition)
- **Deferred**: (β) separate grasp synthesis module → trigger: object diversity exceeds π prior coverage / checkpoint: **CP3 (tool articulation with diverse tools)**
- **Note**: this is source diversification of upstream context, not "external prior". Identity does not commit to pretrained anchoring.

#### [D15] Finger-finger role asymmetry (tool articulation)
- **v1**: (i) single hand network + reward differentiation across fingers
- **Deferred**: (iii) role embedding input → trigger: tool articulation finger role inference insufficient via reward alone / checkpoint: **CP3**
- **Cross-reference**: CCGE (arXiv:2603.10971) provides natural contact-coverage formulation for finger-region role differentiation; can serve as reference at CP3.

---

## 7. Anti-topics (Noise Filter) [AGENT-INPUT]

Papers matching these are excluded from weekly digest unless they have an unusually strong tie to a Pillar or Decision:

- Mobile manipulation / whole-body humanoid (unless dexterous hand performs contact-rich learning)
- Locomotion / quadruped / bipedal gait (RMA family is exception — P4 anchor)
- 2-finger parallel-jaw grippers only
- Pure teleoperation without learning component (shared autonomy *with* RL/residual learning allowed)
- Pure imitation from human video with no RL / physics-informed / closed-loop component
- VLA papers: in scope only if (a) low-level dexterous control component, (b) bridge/residual architecture with RL expert, (c) tactile/force modality injection. Exclude pick-and-place-only.
- Grasping-only (lift-and-hold, no in-hand reorientation/contact-rich interaction) — but pre-grasp / nominal-pose papers in scope for D14
- Soft robotics hardware design without learning
- Survey / position papers (read manually, not via agent)
- Router-based MoE for action selection (different architectural pattern from anatomical split; out of scope unless explicitly contrasting; DexReMoE monitoring is an exception — see §10)

---

## 8. Tracked Literature [LIVING] [AGENT-INPUT]

> 5 pillars × 8 pinned papers = 40 papers + methodology base per pillar.
> Rebalance: quarterly. Hard cap 8 pinned per pillar; replace, don't append.

### 8.0 Format rule
Every paper entry surfaced by the agent — whether in the weekly scouting report, the pinned literature table, or context suggestions — **must** include:
1. arXiv ID in the form `arXiv:XXXX.XXXXX`
2. Direct hyperlink in Markdown format: `[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX)`
3. If no arXiv preprint exists, use the DOI or official proceedings URL instead: `[DOI](https://doi.org/...)`
4. If neither is available, write `[no public link]` explicitly — do not omit the field.

(Canonical source: `docs/STYLE_GUIDE.md` §3.)

### 8.1 P1 Pinned — Heterogeneous Action Decoder
| Paper | arXiv | Year | Role |
|---|---|---|---|
| π0 (Physical Intelligence) | [arXiv:2410.24164](https://arxiv.org/abs/2410.24164) | 2024 | Backbone (D3, D5 anchor); flow matching VLA, action expert pattern |
| π0.5 | [arXiv:2504.16054](https://arxiv.org/abs/2504.16054) | 2025 | Hierarchical inference variant; D7 reference |
| DexterityGen (Yin et al., Berkeley/Meta FAIR) | [arXiv:2502.04307](https://arxiv.org/abs/2502.04307) | 2025 | Coarse→fine control precedent (D1 reference) |
| MoDE-VLA / IMCopilot | [arXiv:2603.08122](https://arxiv.org/abs/2603.08122) | 2026 | Multi-expert + residual tactile injection |
| DexVLA | [arXiv:2502.05855](https://arxiv.org/abs/2502.05855) | 2025 | Plug-in diffusion expert (D3 ref) |
| Hierarchical RL Tool Articulation | [arXiv:2507.06822](https://arxiv.org/abs/2507.06822) | 2025 | body→hand sequential direct precedent (D1) |
| Shared-Autonomy Arm-Hand VLA | [arXiv:2511.00139](https://arxiv.org/abs/2511.00139) | 2025 | Late tactile fusion precedent (D4) |
| TacFiLM | [arXiv:2603.14604](https://arxiv.org/abs/2603.14604) | 2026 | FiLM tactile fusion VLA (D8 anchor) |

**Methodology base (non-pinned)**
- Perez et al. 2018 FiLM — [arXiv:1709.07871](https://arxiv.org/abs/1709.07871) — D8 anchor
- Yu et al. 2020 PCGrad — [arXiv:2001.06782](https://arxiv.org/abs/2001.06782) — D9 deferred
- DeMUSE — [arXiv:2602.19764](https://arxiv.org/abs/2602.19764)

### 8.2 P2 Pinned — Tactile-Dominant Visuotactile Encoder
| Paper | arXiv | Year | Role |
|---|---|---|---|
| **SaTA (uses Sharpa Wave)** | [arXiv:2510.14647](https://arxiv.org/abs/2510.14647) | 2025 | *Top priority*: Sharpa hardware + FiLM spatial-tactile integration |
| TacFiLM | [arXiv:2603.14604](https://arxiv.org/abs/2603.14604) | 2026 | Direct D4+D8 precedent |
| Sparsh (Meta FAIR) | [arXiv:2410.24090](https://arxiv.org/abs/2410.24090) | 2024 | Tactile foundation model (DINO/MAE/JEPA, 460k+ images) |
| ViTacFormer (Berkeley) | [arXiv:2506.15953](https://arxiv.org/abs/2506.15953) | 2025 | Cross-attention visuotactile |
| AdapTac | [arXiv:2505.13982](https://arxiv.org/abs/2505.13982) | 2025 | Force-guided attention + future force prediction aux (D10 v2 ref) |
| GelFusion | [arXiv:2505.07455](https://arxiv.org/abs/2505.07455) | 2025 | Vision-dominated cross-attention dual-channel |
| XL-VLA (cross-hand latent) | [arXiv:2603.10158](https://arxiv.org/abs/2603.10158) | 2026 | Cross-hand representation (4 hands incl. xhand) |
| Sparsh-skin | [arXiv:2505.11420](https://arxiv.org/abs/2505.11420) | 2025 | Magnetic skin variant for future custom hand (CP4) |

**Hardware verification**: Sharpa Hand's "Deform Map" = vision-based tactile (fingertip camera + 1000+ tactile pixels, 320×240 @30Hz per SaTA). Compatible with Sparsh family (DIGIT/GelSight paradigm).

### 8.3 P3 Pinned — Contact-Grounded Supervision
| Paper | arXiv | Year | Role |
|---|---|---|---|
| HORA (Qi et al., CoRL'22) | [arXiv:2210.04887](https://arxiv.org/abs/2210.04887) | 2022 | Foundational in-hand rotation + RMA + privileged-to-tactile distillation |
| AnyRotate (Yang et al., Bristol/Cambrian) | [arXiv:2405.07391](https://arxiv.org/abs/2405.07391) | 2024 | **D11 hand reward direct reference**: rotation + contact + stability + penalty terms |
| Eureka (Ma/Jayaraman, NVIDIA/UPenn) | [arXiv:2310.12931](https://arxiv.org/abs/2310.12931) | 2023 | D11 deferred priority 1; LLM reward synthesis; H2 challenge |
| DrEureka | [arXiv:2406.01967](https://arxiv.org/abs/2406.01967) | 2024 | Eureka + safety + auto DR; 300% in-hand cube rotation (throughput challenge to H2) |
| CCGE (Contact Coverage-Guided Exploration) | [arXiv:2603.10971](https://arxiv.org/abs/2603.10971) | 2026 | Contact-centric reward; finger-region coverage (D15 cross-ref) |
| Sim-to-Real RL Humanoid Dexterous | [arXiv:2502.20396](https://arxiv.org/abs/2502.20396) | 2025 | **"Contact goals + object goals" decomposition** — hierarchical weak identity formalization |
| DAPG (Rajeswaran et al., RSS'18) | [arXiv:1709.10087](https://arxiv.org/abs/1709.10087) | 2018 | BC + RL demo integration (D11 demo deferred) |
| DemoGrasp (Universal Dexterous Grasping) | [arXiv:2509.22149](https://arxiv.org/abs/2509.22149) | 2025 | Single demo + minimal reward; D11 complexity upper-bound reference |

**Methodology base**
- DexPoint (Qin et al., CoRL'22) — [arXiv:2211.09423](https://arxiv.org/abs/2211.09423): contact pair reward without observation dependence
- See to Touch / Dexterity from Touch (Guzey et al., NYU/Pinto): tactile-guided reward
- Twisting Lids Off with Two Hands (Lin et al., CoRL'24): bimanual contact-rich

### 8.4 P4 Pinned — Sim-to-Real for Contact Dynamics
| Paper | arXiv | Year | Role |
|---|---|---|---|
| RMA (Kumar/Fu/Pathak/Malik, Legged) | [arXiv:2107.04034](https://arxiv.org/abs/2107.04034) | 2021 | D12 teacher-student origin |
| RMA for Manipulator Arms (Liang et al.) | [arXiv:2312.04670](https://arxiv.org/abs/2312.04670) | 2023 | RMA + depth + manipulation; D6 cross-ref |
| A-RMA (Smith/Kew/Peng/Ha/Tan/Levine) | RSS'22 | 2022 | Phase 3 base policy fine-tuning; **CP2 primary deferred** |
| OpenAI Solving Rubik's Cube (Akkaya et al.) | [arXiv:1910.07113](https://arxiv.org/abs/1910.07113) | 2019 | ADR (Automatic Domain Randomization) origin |
| Static Friction Sim2Real RL (Hu et al.) | [arXiv:2503.01255](https://arxiv.org/abs/2503.01255) | 2025 | **D12 static/dynamic friction split direct evidence** |
| Contact-Aware Neural Dynamics | [arXiv:2601.12796](https://arxiv.org/abs/2601.12796) | 2026 | DR limitation direct evidence; learned contact correction (CP3 deferred 3) |
| Closing the Reality Gap (Dexterous Force-Based) | [arXiv:2601.02778](https://arxiv.org/abs/2601.02778) | 2026 | Tactile sim, motor dynamics, current-to-torque; *no joint torque sensor* hardware reference (Sharpa) |
| General-purpose Sim2Real Visuotactile (Chen et al.) | (arXiv TBD) | 2024 | Visuotactile sim2real protocol; **CP2 prerequisite** |

**Methodology base**
- Tobin et al. 2017 DR — IROS'17, [arXiv:1703.06907](https://arxiv.org/abs/1703.06907)
- Akinola et al. — Isaac Gym visuotactile + contact-force distribution rendering
- Nguyen et al. — Isaac Sim + soft-body FEM + optical visuotactile rendering
- SplatSim (Qureshi et al., ICRA'25) — Gaussian splatting-based visual sim2real
- DextrAH-G/RGB — privileged-to-vision distillation

### 8.5 P5 Pinned — Task Definition & Falsifiable Evaluation
| Paper | arXiv | Year | Role |
|---|---|---|---|
| OpenAI Learning Dexterous In-Hand (Andrychowicz et al.) | IJRR 2020 | 2018-20 | **Consecutive rotation metric origin** — D13 secondary metric |
| DexArt (Bao et al., CVPR'23) | [arXiv:2305.05706](https://arxiv.org/abs/2305.05706) | 2023 | Articulated objects benchmark; CP3 entry reference |
| In-Hand Articulated Tools (CATFA) | [arXiv:2509.23075](https://arxiv.org/abs/2509.23075) | 2025 | **CP3 direct baseline**: 5 tools + perturbation robustness + Cross-Attention Tactile Force Adaptation |
| DexReMoE (MoE for in-hand reorientation) | [arXiv:2508.01695](https://arxiv.org/abs/2508.01695) | 2025 | *P1 architectural split sibling work*; monitoring (§10) |
| RoboEval (Wang et al.) | [arXiv:2507.00435](https://arxiv.org/abs/2507.00435) | 2025 | Behavioral metrics framework; D13 per-metric falsifier justification |
| Grounding Sim2Real Generalization in Dexterous VLA | [arXiv:2603.22876](https://arxiv.org/abs/2603.22876) | 2026 | 10k real-world trials comprehensive protocol; 4-dim evaluation |
| AutoEval | [arXiv:2503.24278](https://arxiv.org/abs/2503.24278) | 2025 | Autonomous evaluation system; **CP1 ablation automation** |
| Robot Policy Evaluation for Sim2Real (NVIDIA) | [arXiv:2508.11117](https://arxiv.org/abs/2508.11117) | 2025 | Sim2real benchmarking framework; Isaac stack compatible |

**Methodology base**
- Benchmarking In-Hand Manipulation (Cruciani et al., RA-L'20) — [arXiv:2001.03070](https://arxiv.org/abs/2001.03070)
- Coulson et al., Humanoids'21 — 13 Kapandji/Connolly patterns
- ArtiBench/ArtiBrain (2025) — [arXiv:2511.20330](https://arxiv.org/abs/2511.20330) — 100+ articulated tasks, 5 generalization levels (CP5)
- SimplerEnv (CoRL'24)
- Grouped Blind Ensemble Protocol (BeingBeyond, 2026) — operator-blinding methodology

---

## 9. Researchers & Groups to Follow [LIVING]

### 9.1 Individuals

**P1 (Heterogeneous Decoder)**
- Kevin Black, Danny Driess, Karl Pertsch, Lucy Xiaoyang Shi, Allen Z. Ren — Physical Intelligence π team
- Toru Lin — Berkeley
- Haozhi Qi (Berkeley/Meta) — HORA, in-hand rotation
- Zhaoheng Yin (Berkeley) — DexterityGen
- Moritz Reuss — VLA architecture surveys

**P2 (Tactile-Visuotactile)**
- Carolina Higuera (Meta FAIR/UW) — Sparsh lead
- Akash Sharma (Meta FAIR/CMU)
- Haoran Geng (Berkeley) — ViTacFormer
- Mustafa Mukadam, Francois Hogan, Mike Lambeta, Tingfan Wu, Mrinal Kalakrishnan — Meta FAIR
- Nathan Lepora — Bristol (tactile)
- Wenzhen Yuan — UIUC (tactile)
- Tess Hellebrekers, Mike Lambeta — Meta (DIGIT, Sparsh)
- SaTA authors — TBD verification; *uses Sharpa hardware*

**P3 (Contact-Grounded Supervision)**
- Yecheng Jason Ma — NVIDIA/UPenn (Eureka, DrEureka)
- Dinesh Jayaraman — UPenn (GRASP Lab)
- Max Yang — Bristol/Cambrian Robotics (AnyRotate)
- Aravind Rajeswaran — Meta FAIR (DAPG)
- Vikash Kumar — Google DeepMind (DAPG, dexterous)
- Irmak Guzey — NYU (Pinto group) — See-to-Touch

**P4 (Sim-to-Real)**
- Ashish Kumar — RMA originator
- Zipeng Fu — Stanford (RMA co-first)
- Deepak Pathak — CMU (RMA senior)
- Jitendra Malik — Berkeley (RMA senior; perception-action)
- Pieter Abbeel — Berkeley (DR foundational)
- Sergey Levine — Berkeley (A-RMA senior)
- Hao Su — UCSD (visuotactile sim2real; Maniskill)
- Lilian Weng — formerly OpenAI (Rubik's Cube ADR)
- Yichao Liang — RMA for Manipulators

**P5 (Evaluation)**
- Marcin Andrychowicz — formerly OpenAI (consecutive rotation metric origin)
- Yiru Wang — UW (RoboEval)
- Xuning Yang — NVIDIA (Robot Policy Evaluation for Sim2Real)
- Dieter Fox — NVIDIA/UW
- Yiren Bao — UCSD (DexArt)
- DexReMoE authors — TBD verification
- CATFA paper authors — TBD verification

**General / Cross-pillar**
- Tyler Ga Wei Lum, Kushal Kedia — Stanford
- Jeannette Bohg, C. Karen Liu — Stanford
- Pulkit Agrawal — MIT Improbable AI
- Lerrel Pinto — NYU
- Ankur Handa, Yashraj Narang — NVIDIA GEAR
- Matei Ciocarlie — Columbia (dexterous hand mechanisms)
- Abhishek Gupta — UW
- Physical Intelligence (π team)

### 9.2 Korean-affiliated groups (prevent local blind spot)
- KAIST: robotics, manipulation labs (specific PIs — TBD by maintainer)
- SNU: manipulation, RL (specific PIs — TBD)
- NAVER Labs
- POSTECH, UNIST (other major Korean robotics)

### 9.3 Labs / groups (watch code releases)

**Strongly aligned (P1-P5 core lineage)**
- **Physical Intelligence (π team)** — backbone, action expert pattern
- **Berkeley BAIR / RAIL** — RMA, A-RMA, DR origin; DexterityGen
- **Meta FAIR Robotics** — DIGIT, Sparsh, TacFiLM; π team overlap
- **NVIDIA Robotics Research / GEAR** — Isaac Lab upstream, Eureka, Policy Evaluation framework
- **UPenn GRASP Lab** — Eureka lineage (Jayaraman, Ma)
- **Bristol Robotics + Cambrian Robotics** — AnyRotate, TacTip lineage
- **Stanford SVL / IPRL**

**Adjacent / methodology**
- **MIT Improbable AI**
- **CMU RoboTouch + Pathak group**
- **UCSD Hao Su group** — sim2real contact-rich, Maniskill ecosystem
- **University of Washington (Fox group)** — RoboEval, AutoEval, sim2real eval
- **NYU Pinto group** — see-to-touch, dexterity-from-touch
- **Sharpa Robotics (Singapore)** — hardware vendor; **monitor as competitor + hardware partner** (own VTLA model)

---

## 10. Competitor / Kindred Monitoring [LIVING] [AGENT-INPUT]

Specific work whose architectural philosophy overlaps significantly with ours — review at every CP.

### 10.1 Architectural sibling (P1 split philosophy)
- **DexReMoE** ([arXiv:2508.01695](https://arxiv.org/abs/2508.01695)) — MoE for in-hand reorientation across 150 objects
  - *Overlap*: explicit expert decomposition for dexterity
  - *Difference*: object-conditioned routing vs. our anatomical (arm-hand) split
  - *Differentiation hypothesis*: anatomical split + contact-grounded supervision wins on **contact-precision metrics**; object-routing wins on **object-generalization**
  - **Watch trigger**: CP1 result publication race; CP5 cross-object comparison

### 10.2 Direct CP3 baseline
- **In-Hand Articulated Tools (CATFA)** ([arXiv:2509.23075](https://arxiv.org/abs/2509.23075))
  - *Overlap*: 5 articulated tools, tactile + force feedback, sim2real, dexterous hand + Franka
  - *Difference*: CATFA uses *frozen base + cross-attention adapter*; we use *split body+hand both trained*
  - *Differentiation vehicle for CP3*:
    1. body expert directly trained (vs. CATFA frozen base)
    2. Sharpa Deform Map specific tactile encoder (vs. CATFA generic force-torque)
    3. anatomical split's contact-precision advantage
  - **Watch trigger**: every CP3-related result

### 10.3 Hardware-paired direct work
- **SaTA** ([arXiv:2510.14647](https://arxiv.org/abs/2510.14647)) — *uses Sharpa Wave hardware*
  - *Overlap*: same hardware + FiLM tactile integration
  - *Difference*: SaTA is single-task adapter; we propose full system identity
  - **Watch trigger**: any follow-up from same authors

### 10.4 Hardware vendor's own model
- **Sharpa Robotics VTLA model** (their own VTLA)
  - *Status*: monitor for hardware partnership opportunity AND competitive risk
  - **Watch trigger**: any release, demo, or publication

---

## 11. Venue Priority [AGENT-INPUT]

| Tier | Venues |
|------|--------|
| 1 | CoRL, RSS |
| 2 | ICRA, IROS |
| 3 | T-RO, RA-L (journal — archival weight) |
| 4 | arXiv raw (cs.RO, cs.LG) — noisiest, lowest default weight |
| — | NeurIPS/ICML robotics workshops — read only if pinned author |

---

## 12. Cross-pollination Budget [AGENT-INPUT]

1 paper per month from an adjacent field that plausibly transfers. Rotating:
- **Month A**: system identification / differentiable simulation / real2sim
- **Month B**: VLA architecture advances broadly (π, OpenVLA, self-improving VLA)
- **Month C**: MoE routing / skill discovery outside dexterous manipulation
- **Month D**: tactile sensing in prosthetics / neuroscience

---

## 13. Feedback Loop [LIVING]

Filled monthly by maintainer, *not* by agent.

| Month | Papers surfaced | Actually read | Influenced experiment/decision | Notes |
|-------|-----------------|---------------|--------------------------------|-------|
| 2026-05 | | | | |

**Quarterly review question**: *Has my thinking on Identity / any Pillar shifted? If no, the retrieval pipeline may be underperforming — revisit pinned papers and antagonist articulation.*

**Decision-Log checkpoint review (every 3 months)**: scan D1–D15 — any deferred candidate's trigger now observed? Any decision's rationale invalidated by new evidence?

**Competitor/Kindred monitoring (every CP)**: check §10 — any new release from DexReMoE/CATFA/SaTA lineage? Differentiation vehicle still intact?

---

## 14. Open Items & Dependency Graph [LIVING] [AGENT-INPUT]

CP-tiered dependency graph identifying real blockers vs. items that can wait. Default fallbacks are documented for every open item — almost nothing is a hard CP1 blocker.

### 14.A — CP-Tiered Prerequisites

#### Tier 0 — CP1 (sim ablation) minimum blockers
| Item | Default fallback | Resolve by |
|---|---|---|
| First-demo cube fine spec | HORA/AnyRotate standard (50–100g, 7cm side, friction 0.5–1.5, axis-arbitrary, angular tolerance <10°, 5s episode) | Just before CP1 |

> Tier 0 contains a single item, and its default fallback is strong enough that *CP1 entry is effectively possible from the current committed state*.

#### Tier 1 — CP2 (real-world demo) blockers
| Item | Default fallback | Resolve by |
|---|---|---|
| Arm hardware spec | Generic Franka 7-DOF assumed in sim | 3–6 months before CP2 |
| Real-world evaluation site/setup | — (physical workspace required) | At CP2 entry |
| **Tactile sim2real protocol** (D12 prerequisite) | Akinola Isaac Gym tactile library + Chen et al. 2024 protocol attempt | End of CP1 |
| **Static friction range estimation** (D12 prerequisite) | Wide DR range (D12 v1) — gradual narrowing | Just before CP2 |

#### Tier 2 — CP3 (tool articulation) blockers
| Item | Default fallback | Resolve by |
|---|---|---|
| 5 articulated tools concrete list | CATFA 5 tools or DexArt subset (faucet/laptop/bucket/toilet) — likely additions: stapler, scissors, pen, pliers, syringe/tagging-machine | Just before CP3 |
| D15 readiness check | v1 default (single network + reward differentiation) | At CP3 entry |

#### Tier 3 — CP4+ (hardware transition) blockers
| Item | Default fallback | Resolve by |
|---|---|---|
| **Custom hand spec (2H 2026)**: DOF, tendon layout, sensor modality, control rate | Continue CP1-CP3 with Sharpa Hand — D10 swappable head commitment allows P2 encoder replacement per hand | 2H 2026 |

### 14.B — Implementation Feasibility Unclarities

Implementation feasibility dimension; not visible from the §14.A list alone.

| Item | Status | Default if unresolved | Decision deadline |
|---|---|---|---|
| π weight access | ✅ resolved: openpi repo — π0, π0.5, π0-FAST weights public (Apache 2.0); PyTorch port + community re-impl (open-pi-zero) | — | — |
| **π variant choice** (π0 / π0.5 / π0.7) | 🟡 open | π0 (most stable, longest in repo) | CP1 code start |
| **Code base choice** (JAX openpi / HF PyTorch port / open-pi-zero) | 🟡 open — user-answerable | PyTorch port (easier Isaac Lab integration + active community) | CP1 code start |
| **Compute budget**: GPU memory for D3 (i) slice partition + FT × 8k–16k env Isaac Lab parallel | 🟡 unknown | Smaller env count fallback (e.g., 2k–4k) — sample budget trade-off | Just before CP1 execution |
| **Sample budget per condition** (env steps for convergence) | 🟡 unknown | HORA precedent ~few hundred million steps as reference | During CP1 monitoring |
| **Team / engineering capacity** | 🟡 unknown — maintainer-side | — | maintainer-side |
| π0.7 weight release status | 🟡 unknown | Start with π0 / π0.5; π0.7 as backbone migration candidate (CP3+) | Recheck at CP1 code start |

### 14.C — Architectural Sub-Unclarity

**Relationship between π0 MoT and our anatomical split needs definition.** π0 is *already* an MoE-like MoT architecture (PaliGemma 2.291B VLM + action expert 0.315B). The *literal implementation* of D3 (i) "slice partition + FT" admits two readings:

| Reading | Content | Trade-off |
|---|---|---|
| **A — Repurpose**: Use π0's existing action expert (0.315B) as-is for the hand expert; *add* a new body expert (parameter increase) | Minimal π disruption | Body expert random init → loses π prior |
| **B — Subdivide**: *Slice* π0's action expert internally into body / hand | Preserves π prior on both sides | Requires exact slice boundary decision; capacity allocation |

→ Both readings are sub-readings of D3 v1. Must be decided at CP1 code-writing entry. No hard commit required now — only explicit acknowledgment.

→ open-pi-zero (community re-impl) is useful as a *parameter-level architectural reference*.

### 14.D — Non-blocking Ongoing Items

Not hard blockers for research progression, but worth ongoing attention.

| Item | Why valuable | Default posture |
|---|---|---|
| Korean-affiliated PI labs concrete contacts (KAIST / SNU / NAVER Labs / POSTECH / UNIST) | Local network, collaboration | Reach out when bandwidth permits |
| Sharpa VTLA reverse-engineering | §10 differentiation strategy refinement, hardware partnership posture | "Treat as competitor + monitor" baseline |
| **Expected-but-unpublished failure mode** | Maintainer's own assessment: *highest-value search query* | Note in passing, capture in doc when discovered |

### 14.E — Dependency Map (text diagram)

```
External / Ongoing (anytime):
   ├─ Korean PI labs            (no research blocker)
   ├─ Sharpa VTLA RE            (ongoing monitoring)
   └─ Failure-mode articulation (high-value, anytime)

Resolved:
   [π weight access] ✅────→ D3 (i) cascade safe

Tier 0 → CP1:
   [Cube spec, default available]
                  │
                  ↓
   ┌─────── CP1 entry ───────┐  ←  also requires §14.B resolution at code-start
   │  (4-condition ablation)  │     (π variant + code base; both have defaults)
   └──────────────────────────┘
                  │
   Concurrent preparation during CP1:
   ├─ Tactile sim2real protocol verified  ┐
   ├─ Friction range estimation           │ ↓
   ├─ Arm hardware spec                   │ CP2 prerequisite gate
   └─ Real-world site/setup               ┘
                  │
                  ↓
                CP2 entry
                  │
                  ↓
   [5-tool list decision] ──→ CP3 entry
                  │
                  ↓
   [Custom hand spec (2H 2026)] ──→ CP4 entry
```

### 14.F — Why This Structure?

The CP-tiered organization separates near-term blockers from distant ones. Without this separation, a flat list would conflate items requiring imminent decision (e.g., cube spec) with items 6+ months out (custom hand spec) — creating false pressure to decide everything now.

Additionally, §14.B (Hidden unclarities) and §14.C (Architectural sub-unclarity) surface the *implementation feasibility* and *literal-reading ambiguity* dimensions that flat task-list framing typically conceals.

---

## Appendix C: Open meta-questions

These are meta-uncertainties the maintainer carries, distinct from architectural decisions:

- **Domain epistemics**: in detailed design, judgment is limited because the field itself is in unknown territory. This is *legitimate research stance*, not a deficiency. Decision Log structure (defaults + triggers + checkpoints) is the principled response — each v1 default is a *bet* whose evidence accumulates at the corresponding checkpoint.
- **First-experiment fragility**: most CP1 deferred decisions converge on the first ablation. If CP1 results are noisy or inconclusive, *multiple* v2 candidates activate simultaneously — requiring careful sequencing of revisits.
- **Sim2real timing**: P4 is plan, not implementation. The lag between sim validation (CP1) and real-world transfer (CP2) creates a window where multiple Pillar revisions might queue up — manage this proactively. CP2 prerequisite (visuotactile sim protocol + friction range estimation) acts as gate.
- **Publication race risk**: DexReMoE (P1 sibling) + CATFA (CP3 baseline) both active. Differentiation vehicles documented in §10; revisit at every CP.
- **Hardware partnership uncertainty**: Sharpa is both hardware vendor and competitor (own VTLA). Strategic posture TBD by maintainer.

## Appendix C.1: Insufficient-knowledge classification

Remaining insufficiencies decompose into four categories with different resolution paths:

| Category | Resolution path | Example items | Action |
|---|---|---|---|
| **A — Knowledge gap** | Study (read, do not write) | Deep RL rigor (Henderson 2018 / Andrychowicz 2020 / Engstrom 2020), π0 architectural internals (openpi README + open-pi-zero), PhysX contact dynamics behavior in our setting, Sharpa Deform Map sim modeling | Self-paced reading; pre-condition for step (iii) re-entry |
| **B — Information gap** | Acquire (look up, ask) | π0.7 weight release status, Sharpa VTLA reverse-engineering material, Korean PI lab contacts, team compute / engineering capacity | Periodic scan; can do concurrently with A |
| **C — Experiential gap** | Run experiments (CP1~CP5) | Evidence for D1-D15 v1 defaults, §14.C π MoT × split sub-reading, fair-comparison rigor level, falsifier threshold appropriateness | Only resolved by step (iii)+ execution — *this is the purpose of step (iii)* |
| **D — External world dependency** | Wait + monitor | Custom hand spec (2H 2026), DexReMoE/CATFA/Sharpa VTLA follow-up releases, π0.7+ openpi release | Periodic scan via §10 |

**Key insight**: a sensation of "I don't know enough to commit" most often arises when Category A items are mistakenly perceived as Category C items — i.e., feeling that *experiments* are needed when *reading* would suffice. The classification clarifies which gaps can be closed *before* re-entering step (iii), and which require step (iii) itself.

---

*End of v4.0.*
