# Probe
> Research scout for hand-centric dexterous manipulation.

---

# Research Context — Hand-centric Dexterous Manipulation

> **Last updated**: 2026-05-19
> **Maintainer**: \<your-name\>
> **Agent usage**: This is the *static* context. The retrieval agent reads (never writes) this file. Findings go to `scouting/P#/YYYY-MM-DD.md` (one file per run, per pillar) instead.

---

## 0. How to use this file [STABLE]

**Section markers**
- `[STABLE]`: changes rarely (identity, purpose, hardware)
- `[LIVING]`: updated as research progresses
- `[AGENT-INPUT]`: retrieval agent conditions on this — keep signal-dense

**Update protocol**
- Identity / Purpose: change only with deliberate review (semantic shift, not phrasing)
- Pillars: structure stable; tracked items within can evolve as evidence accumulates
- Decision Log: append-only; do not renumber. Decisions are *first-attempt defaults* with explicit deferred candidates and revisit triggers
- Tracked Literature: rebalanced quarterly. Hard cap 8 pinned per pillar; replace, don't append
- Competitor/Kindred Monitoring: review whenever a Tracked-Literature rebalance lands

**Output formatting & authoring rules**
All formatting rules (emoji system, link format, Korean authoring principles) are consolidated in **`docs/STYLE.md`** — the single source of truth. The agent must read `docs/STYLE.md` before producing any output. Do not duplicate formatting rules here; edit `docs/STYLE.md` instead.

**Audience**: maintainer (self, future-self) + AI retrieval agent + future collaborators. Keep terminology accessible without sacrificing precision.

**Current state**: ⏸️ paused before step (iii) implementation entry. Knowledge consolidation phase active. All open items have v1 defaults; no hard blocker. See Appendix C.1 for the four-category classification of remaining insufficiencies.

---

## 1. Identity [STABLE] [AGENT-INPUT]

> Most VLA-style policies attempt to converge on dexterity via a **monolithic action decoder + vision-dominant observation**, and most attempts to push the ceiling bolt a **correction/residual module onto a frozen VLA**. I argue both are dead ends for *dexterous **hand** manipulation*: a correction module is structurally bounded by the VLA's own local output distribution and must be re-trained whenever the VLA's motion pattern shifts, so it cannot exceed the VLA ceiling — it only tracks it. RL-as-core is likewise not the answer for *generalized* dexterity: generalized tasks cannot be reward-engineered, which is why leading labs use RL only as a deploy-ready fine-tuning stage (π RLT), not as the source of capability. **I argue dexterity must be tackled at the VLA level itself**, via (1) an **anatomically heterogeneous Body/Hand action-expert decoder**, (2) **structured finger/palm-bound proprio-tactile input + multi-camera pre-fusion**, (3) a **System1-gated low-level Hand System0 RL stabilization module** (the *only* place RL is necessary, because slip/grasp-retention *is* reward-engineerable), and (4) **VLM-pretraining preservation** through VLA fine-tuning. Task specification stays goal-centric (arm-hand integrated).

**Decomposition**
- *Antagonist A*: VLA-output correction/residual modules — performance bounded by the VLA's local output distribution; re-train on every VLA motion-pattern shift; full-pipeline bottleneck
- *Antagonist B*: RL-as-core for generalized dexterity — generalized tasks are not reward-engineerable; leading-lab RL use is deploy-ready fine-tuning only (π RLT), not capability source
- *Antagonist C*: monolithic decoder treating arm/torso/finger as one homogeneous action space + simple concat of heterogeneous modalities
- *Protagonist*: VLA-level tackling of dexterous **hand** manipulation — heterogeneous Body/Hand experts + structured input binding + System0 stabilization + VLM-prior preservation
- *Stays goal-centric*: task specification (arm-hand integrated)
- *RL's confined role*: System0 hand-level contact stabilization only (tractable reward: slip suppression, grasp retention)

> *Maintainer's anchor (Korean original, preserved for self-reference)*:
> 대다수 VLA-style policy는 monolithic action decoder + vision-dominant observation으로 dexterity를 수렴시키려 하고, 성능 한계를 넘으려는 시도는 frozen VLA 위에 correction/residual 모듈을 붙인다. 그러나 보정 모듈은 VLA 출력 주변 local distribution 내로 성능이 한정되고 VLA 모션 패턴이 바뀔 때마다 재학습해야 하므로 VLA ceiling을 넘지 못한다. RL-as-core 또한 generalized task를 reward engineering할 수 없어 해답이 아니며, 선도사는 RL을 deploy-ready fine-tuning(π RLT)으로만 쓴다. 나는 dexterous **hand** manipulation을 VLA-level에서 직접 tackle해야 한다고 본다: (1) anatomically heterogeneous Body/Hand action expert, (2) structured finger/palm proprio-tactile 입력 + multi-cam pre-fusion, (3) System1-gated 저수준 Hand System0 RL 안정화(slip/grasp 유지는 reward-engineerable하므로 RL이 필요한 유일 지점), (4) VLM-pretraining 보존. Task spec은 arm-hand 통합 goal-centric 유지.

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
Build a holistic system for human-level dexterous manipulation. Full stack envisioned: hardware that expresses rich contact, data collection preserving human interaction, control minimizing intent-execution gap, models absorbing multimodal supervision at scale, evaluation infrastructure enabling scalable + reproducible iteration. *Current scope-of-work focuses on modeling at the VLA level.*

### 3.2 Scope of work
**Body expert and hand expert both directly designed and trained at the VLA level.** No outsourcing of dexterity to a post-hoc correction module (which would be distribution-bounded by the VLA). Pretrained VLM/π weights are leveraged *and explicitly preserved* (P4). The Hand System0 RL module is the single RL component; everything else is VLA-level (flow-matching) learning.

### 3.3 Task philosophy
**Hand expert as a stabilization layer on top of architectural grounding**, where grounding is body's grasp/arm intent + backbone's visual/task embeddings (with VLM prior preserved). System0 is a *further* low-level stabilization layer beneath the Hand expert, activated only when contact retention demands sub-policy-loop reaction speed. Hand-level contact elevation remains the **differentiation claim**; the **deliverable** is the integrated VLA system.

### 3.4 Long-term task families
- **In-hand reorientation** (HORA-style): object rotation in palm — first demo, architectural validation
- **Tool articulation** (e.g., tagging machine, trigger tools): hold tool + finger operation — identity flagship demo (phase 2)
- **Diverse functional grasping**: appropriate nominal pose synthesis across objects — generalization phase (later)

### 3.5 Demo task phasing
- **Phase 1**: in-hand cube rotation (architectural validation of split + structured input + System0 gating, measurable falsifier)
- **Phase 2**: tool articulation (identity flagship; body-hand coordination + finger asymmetry); 5-tool evaluation set matching CATFA precedent (arXiv:2509.23075)
- **Phase 3**: cross-object generalization

---

## 4. Target Hardware & Stack [STABLE]

### 4.1 Hardware
**Hand**
- Near-term: **Sharpa Hand** (22-DOF, no wrist DOF) — fingertip tactile (Deform Map: vision-based, ~320×240 per fingertip @30Hz)
- Alternate near-term: **xhand** (dexterous hand, no wrist DOF)
- Mid-term (2H 2026+): **in-house custom hand** (spec TBD — DOF, tendon layout, sensor modality, control rate)

**Arm**: not yet committed. Generic 6–7 DOF assumed in design (Body expert outputs both-wrist / tool-flange pose per D2).

**Design constraint**: avoid Sharpa-specific lock-in. Tactile encoder uses *swappable sensor head + common token format* (P2).

### 4.2 Simulation
- Primary: **NVIDIA Isaac Sim + Isaac Lab** (PhysX rigid-body, Signorini-Coulomb contact) — used for **System0 RL training only**
- Secondary (deferred to a later phase): **MuJoCo MJX** as alternative for differentiable contact
- Visuotactile sim: Sharpa Deform Map sim-side rendering — protocol TBD before real-robot transition (Chen et al. 2024 / Akinola Isaac Gym tactile library as reference)

Known gap: PhysX point contact vs. real fingertip viscoelastic deformation (P3/System0-sim2real scope). Contact-Aware Neural Dynamics (arXiv:2601.12796) documents this gap.

### 4.3 Training
- **Primary policy**: VLA backbone (**Physical Intelligence π**, π0 / π0.5) + flow-matching Body/Hand action experts, trained by imitation with VLM-prior preservation (P4). This is the capability source.
- **RL (scoped)**: GPU-parallel RL, 8,192–16,384 envs, **PPO**, **for the Hand System0 stabilization module only** (P3). Not the primary policy's learning signal.
- Backbone weights from openpi (Apache 2.0); see §13.A.

---

## 5. Pillars [STABLE structure, LIVING content] [AGENT-INPUT]

Five pillars.

### P1. Heterogeneous Body/Hand Action Expert
**Scope**: Body vs Hand action-expert design. Body/torso/arm handle macro motion (object approach, transport, placement); fingers handle post-contact contact-rich precision. Either an explicit BodyExpert–HandExpert split, or a single ActionExpert with strongly separated body/hand latents (comparison group). Body output = both-wrist or tool-flange pose (embodiment-transfer easing); Hand output = finger joint command. Includes Body↔Hand information-sharing, input-modality separation, control-rate separation, and π backbone integration.

**Identity tie**: heterogeneous-decoder claim → this pillar (the architectural core).

**Tracked items**: split form (D1), Body output space (D2), Hand output space (D3), Body↔Hand information sharing (D4), input-modality + control-rate separation (D5), coordination direction & flow (D6), π backbone integration / partition (D7).

**Anti-topics**: monolithic decoders without arm-hand split; router-based MoE (different pattern; DexReMoE monitoring exception); post-hoc correction/residual-on-frozen-VLA without addressing distribution-bound limitation.

**Literature anchor**: π0/π0.5 (backbone); TwinBrainVLA (AsyMoT frozen-generalist + trainable-specialist), DexterityGen (bounded coarse→fine precedent), LaMP / HEX (dual-expert), Shared-Autonomy Arm-Hand VLA / DexGrasp-VLA (anatomical arm/hand split), Demystifying Action Space Design (D2 evidence). See §8.1.

### P2. Structured Input-Modality Binding
**Scope**: replace simple concat/token-append with finger/palm-bound structured tokens. Each finger's joint state + that finger's tactile feature → one local embedding (~10 finger + 2 palm tokens). Topology-aware encoding (finger/hand identity, palm-relative fingertip pose, kinematic chain). Hand-level aggregation encoder. Multi-camera vision pre-fusion (cross-attention fuser → unified spatial embedding) before the VLM.

**Identity tie**: hand-level "observation elevation" — finger-wise contact semantics made explicit, not implicitly learned.

**Tracked items**: finger/palm structured token construction (D8), topology-aware encoding (D9), hand-level aggregation encoder (D10), visuotactile/proprio-tactile encoder candidate (D11), multi-camera pre-fusion (D12).

**Anti-topics**: vision-only manipulation; pure tactile-only without structured binding; flat-concat fusion without per-finger attribution.

**Literature anchor**: SaTA (Sharpa hardware), TacFiLM, Sparsh, ViTacFormer, DexViTac (kinematic-grounded tactile), Touch Dreaming (latent tactile prediction), AdapTac, XL-VLA. See §8.2.

### P3. Hand-level System0 Module (RL-scoped)
**Scope**: low-level RL contact-stabilization. System1 HandExpert emits finger commands; post-contact slip / grasp weakening / unstable contact need sub-policy-loop reaction. System0 = vision-excluded RL policy on tactile + finger joint state maintaining stable grasp/contact. Bypasses System1 output in nominal operation; activated only by System1 on/off signal during retention-critical intervals.

**Identity tie**: the *only* RL component; "supervision elevation" now scoped to a reward-engineerable sub-problem.

**Tracked items**: System0 role & operating regime (D13), System1↔System0 interface (D14), System0 input modality (D15), System0 output form (D16), System0 RL policy spec (D17), System0 sim2real (D18).

**Anti-topics**: RL reward-engineering for generalized full-task (out of scope unless System0-scoped); locomotion sim2real; contact-agnostic DR.

**Literature anchor**: HORA, AnyRotate (reward terms), CCGE (contact coverage), RMA (teacher-student adaptation), Static Friction Sim2Real, Contact-Aware Neural Dynamics, π0.5 (hierarchical inference as System1/System0 analog). See §8.3.

### P4. VLM Pretraining Preservation
**Scope**: generalization/situation-understanding originates in the VLM backbone; full fine-tuning on deploy data over-specializes and erodes the pretrained prior. Decide VLM FT range (freeze / partial / LoRA-adapter / full), prior-preservation strategy, staged training recipe, multi-embodiment pretraining data, and the action-representation × VLM-preservation relationship. The **VLM lineage itself** (= initial weights × further-pretrain corpus) and the **multi-embodiment pretraining data catalog** are first-class P4 variables, not only the preservation strategy on top of them.

**Identity tie**: protects the VLA ceiling that the whole identity rests on; without it, the VLA-level pivot self-defeats.

**Tracked items**: VLM FT range (D19), VLM backbone lineage choice (D19b), prior-preservation strategy (D20), staged training recipe (D21), multi-embodiment pretraining data (D22), action-representation × VLM-preservation (D23).

**Anti-topics**: action-only papers ignoring backbone preservation; pick-and-place-only VLA without forgetting/over-specialization analysis.

**Literature anchor**: π0/π0.5, VLM2VLA (LoRA + NL-action, forgetting mitigation), RT-2 (web/robot co-FT), VLA-Adapter (Bridge Attention), PriorVLA (prior-preserving adaptation), multi-embodiment data survey [arXiv:2506.19121], MolmoAct2 (per-layer KV-cache conditioning). See §8.4.

### P5. Task Definition & Falsifiable Evaluation
**Scope**: single-skill demo selection, evaluation protocol, metrics, falsifier thresholds. **Falsifier**: a 4-contribution VLA-level ablation isolating (split / structured-binding / +System0 / VLM-preserved).

**Identity tie**: must isolate each of the four architectural contributions to validate the VLA-level identity claim.

**Tracked items**: demo task & phasing (D24), 4-contribution ablation & falsifier (D25), evaluation protocol (D26).

**Anti-topics**: benchmark-only evaluation (no real-world); single-metric aggregate assessment.

**Literature anchor**: OpenAI Learning Dexterous In-Hand, DexArt, CATFA, RoboEval, Grounding Sim2Real VLA, AutoEval, NVIDIA Robot Policy Evaluation. See §8.5.

---

## 6. Decision Log [LIVING] [AGENT-INPUT]

All architectural commits recorded with: options considered, v1 choice, rationale, deferred candidates with revisit triggers. Append-only.

### 6.1 Decisions — P1 (D1–D7)

#### [D1] Split form (P1)
- **Options**: (i) explicit BodyExpert–HandExpert separation, (ii) single ActionExpert with shared representation + body-specific latent + hand-specific latent, (iii) hybrid (shared trunk, split heads)
- **v1**: (iii) hybrid — shared trunk + split body/hand heads
- **Rationale**: cleanest isolation of the split contribution at the v1 ablation while reusing π's shared representation; (i) and (ii) become the ablation comparison group
- **Deferred**: (i) fully separate experts → trigger: shared trunk shows body↔hand gradient interference; (ii) latent-only separation → trigger: explicit split underperforms latent separation on contact metrics
#### [D2] Body output space (P1)
- **Options**: (a) both-wrist / tool-flange pose (Cartesian), (b) joint-space minus wrist, (c) delta Cartesian, (d) split
- **v1**: (a) both-wrist / tool-flange pose
- **Rationale**: targets embodiment-transfer easing; flange pose decouples Body expert from arm kinematics (joint-space is the comparison group)
- **Deferred**: (b) joint-space → trigger: flange-pose Body shows training instability vs joint-space ("Demystifying Action Space Design": joint-space=stability, task-space=generalization); (c) delta Cartesian → trigger: absolute-pose learnability poor
#### [D3] Hand output space (P1)
- **Options**: (i) finger joint command, (ii) fingertip pose, (iii) grip-force / impedance, (iv) hybrid
- **v1**: (i) finger joint command
- **Rationale**: directest tactile/proprioceptive-feedback-grounded precision control; matches Sharpa joint interface
- **Deferred**: (iii) impedance → trigger: stiff joint-position control causes excessive contact force
#### [D4] Body↔Hand information sharing (P1)
- **Options for mechanism**: (A) shared latent, (B) cross-attention, (C) mutual conditioning, (D) routing/gating, (E) action/history sharing, (F) FiLM
- **Options for what flows**: (i) $a_b$ only, (ii) body hidden state, (iii) both
- **v1**: (F) FiLM with $a_b$ → ($\gamma,\beta$) modulating hand head input, single point
- **Rationale**: MLP-style hand head + minimum delta + sufficient first-experiment expressivity
- **Deferred**: (B) cross-attention → trigger: FiLM bottleneck OR hand head restructured to transformer (cf. LaMP gated cross-attn, TwinBrainVLA AsyMoT); (ii) hidden-state injection → trigger: D6 v2 entry; multi-layer depth → trigger: single-point info bottleneck (cf. MolmoAct2 per-layer KV)
#### [D5] Input-modality + control-rate separation (P1)
- **Options (modality)**: (i) shared input to both experts, (ii) Body={vision, language, proprio, task context} / Hand={tactile, proprio, local visual, VLA intent}, (iii) partial
- **Options (rate)**: (α) shared control rate, (β) separated (time-positional encoding / action timestamp embedding / async action conditioning)
- **v1**: (ii) modality-separated + (α) shared rate
- **Rationale**: modality separation is identity-aligned (hand=contact); shared rate = minimum delta for first experiment
- **Deferred**: (β) rate separation → trigger: finger precision needs higher-frequency loop than body (in-hand rotation)

#### [D6] Coordination direction & flow (P1)
- **Options**: body→hand / hand→body / iterative / bidirectional; flow = (a) hierarchical (body K-step denoise → $a_b$ → hand conditioned), (b) coupled denoising, (c) coupled single network, (d) independent
- **v1**: body→hand, (a) hierarchical flow
- **Rationale**: literal sequential conditioning; clean interface; training stability
- **Deferred**: iterative/bidirectional + (b) coupled → trigger: slip fails to reshape arm motion in time; (c) single network → trigger: latency budget pressure
#### [D7] π backbone integration / partition (P1)
- **Options**: (i) slice π0 action expert + FT both sides, (ii) repurpose π expert as Hand + add new Body, (iii) both re-init, (iv) distillation from monolithic π
- **v1**: (i) slice partition + FT
- **Rationale**: maximally preserves π manipulation prior; cleanest split-vs-monolithic baseline. Sub-reading **Repurpose vs Subdivide** unresolved → §13.C, decide at code entry
- **Deferred**: (ii) repurpose → trigger: Body re-init acceptable; (iv) distillation → trigger: π surgery overhead prohibitive
- **Note**: tightly coupled to P4 (D19 freeze strategy)

### 6.2 Decisions — P2 (D8–D12)

#### [D8] Finger/palm structured token construction (P2)
- **Options**: (i) per-finger {joint state + that finger's tactile} → one token (~10 finger + 2 palm tokens), (ii) per-fingertip only, (iii) flat concat (baseline/ablation)
- **v1**: (i) per-finger proprio-tactile binding, 10 finger + 2 palm tokens (both hands)
- **Rationale**: makes finger-wise contact semantics explicit instead of implicitly learned
- **Deferred**: finer sub-finger tokenization → trigger: per-finger token too coarse for in-hand rotation
#### [D9] Topology-aware encoding (P2)
- **Options**: (i) raw sensor vector, (ii) + finger/left-right identity, (iii) + palm-relative fingertip pose + kinematic-chain embedding
- **v1**: (iii) full topology-aware
- **Rationale**: "which hand's which finger/palm produced this contact" must be explicit for cross-hand portability
- **Deferred**: learned topology embedding → trigger: hand-coded topology insufficient when the hand hardware changes
#### [D10] Hand-level aggregation encoder (P2)
- **Options**: (A) mean/sum pool, (B) self-attention, (C) graph attention, (D) lightweight transformer
- **v1**: (B) self-attention over finger/palm tokens
- **Rationale**: recovers inter-finger interaction lost by per-finger separation; lighter than full transformer
- **Deferred**: (C) graph attention → trigger: kinematic-chain structure underused; (D) transformer → trigger: self-attn capacity insufficient
#### [D11] Visuotactile / proprio-tactile encoder candidate (P2)
- **Encoder v1**: hardware-specific CNN on Deform Map → per-fingertip feature → fed into D8 finger token; swappable sensor head + common token format; contact-binary + slip-binary aux heads (light)
- **Tactile feature options**: tactile image / resultant force vector / pressure distribution / contact map — compared
- **Proprio scope options**: joint position / velocity / torque / motor current — compared
- **Deferred**: force-prediction aux (AdapTac, arXiv:2505.13982) → trigger: contact/slip-binary saturation; Sparsh/T3 pretraining → trigger: random-init encoder underperforms; latent tactile prediction (Touch Dreaming) → trigger: inference-time tactile dropout robustness needed
- **Non-negotiable**: (1) no Sharpa lock-in, (2) preserve contact-relevant features

#### [D12] Multi-camera vision pre-fusion (P2)
- **Options**: (i) N camera features fed raw to VLM, (ii) cross-attention fuser → unified spatial vision embedding → VLM, (iii) learned camera-token selection
- **v1**: (ii) cross-attention fuser → unified spatial embedding
- **Rationale**: stable spatial context; avoids VLM token bloat from N cameras
- **Deferred**: (iii) selection → trigger: fuser loses viewpoint-specific contact cues
### 6.3 Decisions — P3 / System0 (D13–D18)

#### [D13] System0 role & operating regime (P3)
- **Role options**: slip anticipation / stable grasp maintenance / minor finger posture correction
- **v1**: all three, scoped to: post-grasp grasp maintenance; in-hand stable-contact maintenance; insertion/contact retention
- **Rationale**: narrow, reward-engineerable sub-problem — the only place RL is justified
- **Constraint**: must NOT interfere with peg-in-hole insertion motion (gated off when System1 needs free finger motion)
- **Deferred**: expand to dynamic regrasp → trigger: static-maintenance scope too narrow once tool-articulation tasks enter scope
#### [D14] System1↔System0 interface (P3)
- **Options**: (i) binary `maintain_grasp` on/off (bypass System1 when off → System0 takes finger command), (ii) continuous blend weight, (iii) System0 always-on residual
- **v1**: (i) binary on/off, bypass-when-off
- **Rationale**: cleanest interface; clearest ablation of System0 contribution
- **Deferred**: (ii) continuous blend → trigger: hard switching causes finger-command discontinuity
#### [D15] System0 input modality (P3)
- **v1**: tactile feature + finger joint position + velocity + joint torque (or motor current) + contact-state history. **Vision excluded** (by design)
- **Rationale**: sub-loop reaction speed requires vision-free low-latency state
- **Deferred**: add wrist IMU/force → trigger: tactile+proprio insufficient for slip anticipation
#### [D16] System0 output form (P3)
- **Options**: (i) finger joint command (direct), (ii) grip-force / impedance parameter, (iii) local stabilizing correction added to System1 output
- **v1**: (i) direct finger joint command (active only when gated on)
- **Rationale**: matches D3 Hand output space; clean bypass semantics
- **Deferred**: (ii) impedance → trigger: position control overshoots contact force; (iii) correction-residual → trigger: full-bypass loses System1 intent during maintenance
#### [D17] System0 RL policy spec (P3)
- **State**: tactile + proprioceptive history (D15)
- **Action**: finger-level stabilizing command (D16)
- **Reward**: object retention + slip suppression + contact stability − excessive-force penalty − smoothness penalty (task/contact/slip core + AnyRotate term structure)
- **Termination**: object drop / contact loss / excessive deformation or force
- **Synthesis v1**: hand-crafted contact-aware; **deferred** Eureka/DrEureka contact-aware variant → trigger: hand-crafted reward search cost prohibitive- **Algorithm**: PPO, GPU-parallel Isaac Lab (8k–16k env)

#### [D18] System0 sim2real (P3)
- **DR params**: static_friction + dynamic_friction (split, arXiv:2503.01255) + contact stiffness + restitution + mass + surface compliance + actuator delay/noise
- **Adaptation**: RMA-family teacher-student with contact-relevant extrinsics
- **Deferred (priority)**: RMA-style Phase-3 RL fine-tuning → *before sim→real transition*; static-friction-aware DR scheduling → *post-real-robot transition*; learned contact correction (Contact-Aware Neural Dynamics) → *deferred to a later phase*
- **Caveat**: System0-scoped only; activates mostly at the real-robot transition — plan, not current implementation

### 6.4 Decisions — P4 / VLM Preservation (D19–D23)

#### [D19] VLM fine-tuning range (P4)
- **Options**: (a) full VLM freeze + action experts only, (b) vision encoder freeze + partial language/decoder, (c) selective layer unfreeze, (d) LoRA/adapter PEFT, (e) full-FT baseline
- **v1**: (a) full freeze + action experts only
- **Rationale**: late tactile/structured-input fusion → backbone sees π-trained modalities only → no adaptation pressure; minimum delta; maximal prior preservation
- **Deferred**: (d) LoRA → trigger: frozen backbone representation insufficient for new modality combos; (c) selective unfreeze → trigger: LoRA still insufficient
#### [D19b] VLM backbone lineage choice (P4)
- **Unit**: a VLM is identified by the 2-tuple `(initial weights) × (further-pretrain corpus)`, not by the bare model name. Two stacks that both load "PaliGemma" but were further-pretrained on different mixes are different lineages for our purposes.
- **Options (lineage examples)**: PaliGemma-2B × π0 mix (OXE + π in-house) — π0 default; PaliGemma × π0.5 mix; Eagle-2 (NVIDIA, 1.34B VLM portion) × GR00T cross-embodiment mix (humanoid traj + human video + synthetic); Molmo × MolmoAct mix; Being-H (init TBD) × UniHand-2.0 (~35k h × 30 embodiments, 400M+ samples / 120B tokens); **Qwen3-VL-4B-Instruct × ~200M robot trajectory timesteps (DROID + MolmoAct + in-house) + 80M+ VL samples** — Xiaomi-Robotics-0, open-weight; **Gemma-3-12B-IT × BridgeData v2 NL-formatted (fine-tune only)** — VLM2VLA, LoRA-only path; **Prismatic-VLM + Qwen2.5-0.5B × LIBERO + CALVIN (adapter-only)** — VLA-Adapter, minimal-backbone path; **OpenVLA (CLIP-B/L + Llama-7B) × frozen Prior + Adaptation on RoboTwin 2.0 + LIBERO** — PriorVLA, two-expert path; InternVL × ? / Qwen2.5-VL × ? — open-weight candidates pending corpus pairing.
- **v1**: PaliGemma-2B × π0 mix (= openpi weights). Compatible with D19(a) freeze + D23(iii) flow-matching head.
- **Rationale**: validated lineage; coexists with the rest of the v1 stack at zero re-train cost.
- **Deferred**: alternative-lineage comparison experiment → trigger: a generalization weakness surfaced on real-robot rollouts is diagnosed as *lineage-attributable*. Restricted to a **2-pair comparison** (v1 vs one diagnosis-matched candidate) to avoid ablation factor blow-up.
- **Watch artifact**: open-weight VLM candidate catalog (init-weight accessibility, license, inference cost, instruction-tuning provenance) — drives §8.4 rows.

#### [D20] Prior-preservation strategy (P4)
- **Definition (scope)**: the target is **the loss of the VLM pretrained distribution itself**. *Cause* (action-expert training, LoRA, co-pretrain, data-mix change, …) is the *activation condition* of D20, not part of its definition.
- **Standby regime**: while D19 = (a) full freeze holds, the prior-loss pathway is mathematically blocked and D20 operates as a *standby decision*. D20 activates the moment D19 moves off freeze (LoRA / partial / full FT) **or** D23 moves to (ii) NL-style action where the VLM language head is dragged into action prediction.
- **Options (active when D20 fires)**: LoRA-minimal (VLM2VLA, NL-style action), web/robot co-FT (RT-2), action-side adapter (VLA-Adapter Bridge Attention), prior-preserving adaptation (PriorVLA)
- **v1**: action-side adapter (D4/D7 split heads *are* the action-side adapter; backbone untouched)
- **Rationale**: consistent with D19(a) full-freeze; no backbone re-train burden
- **Deferred**: LoRA-minimal → trigger: D19 moves to (d); web/robot co-FT → trigger: deploy data distribution-shift severe (see D-analysis)
- **Not in scope**: "action-expert over-specialization on deploy-task distribution that degrades system-level generalization" is a *different phenomenon* — VLM weights stay intact, so it is not forgetting. Handled by D21 "Stage 2 in-distribution plateau with generalization loss" trigger. Do not conflate with D20.

#### [D21] Staged training recipe (P4)
- **v1 (with Stage 0 / Stage 0½ separation)**:
  - **Stage 0** — VLM lineage selection (= adopt D19b v1). Decision act, no training.
  - **Stage 0½** (deferred) — multi-embodiment co-pretrain on the chosen lineage (= execution site for D22 when it fires). Trigger inherited from D22.
  - **Stage 1** — keep VLM alignment (no-op: load lineage weights as-is).
  - **Stage 2** — VLM-freeze, train Body/Hand experts (current v1).
  - **Stage 3** (deferred) — LoRA / top-layer limited FT.
  - **Stage 4** (deferred) — small-LR full-FT + prior-preserving regularization.
- **Rationale**: each stage gated by the prior stage's insufficiency, minimizing forgetting risk. Stage 0 / Stage 0½ separation makes "*checkpoint selection*" (bound to D19b) and "*additional pretraining*" (bound to D22) visible as distinct decisions so their triggers do not entangle.
- **Deferred**: Stage 3/4 entry → trigger: Stage 2 in-distribution plateau with generalization loss
#### [D22] Multi-embodiment pretraining data (P4)
- **v1 (execution)**: rely on π pretrained prior only (no extra multi-embodiment co-training) for first experiment
- **Promoted action item (deliverable before v1 ablation)**: build a multi-embodiment dataset catalog. Per-dataset columns: name / source / license / accessibility; **input schema** (camera count·resolution·FPS, proprio channels, tactile presence·format, language-instruction format); **output schema** (action space — joint vs end-effector vs delta — DOF, control rate); **embodiment meta** (arm DOF, hand DOF — gripper vs dexterous — wrist DOF, mounting); **lineage-stacking info** — which landmark VLA (π / GR00T / MolmoAct2 / Being-H0.5 / Xiaomi-Robotics-0) stacked this dataset on top of its VLM, and how — wires the catalog back into D19b lineage identification.
- **Reference**: starter list from multi-embodiment data survey ([arXiv:2506.19121]).
- **Deferred (execution)**: add multi-embodiment co-training (= Stage 0½ in D21) → trigger: π prior coverage insufficient for target tasks. Catalog *build* is not deferred — it lands before v1 ablation.

#### [D23] Action representation × VLM preservation (P4)
- **Options**: (i) discrete action token, (ii) NL-style action representation, (iii) continuous flow-matching action head
- **v1**: (iii) continuous flow-matching head (π-consistent; backbone not used as action token predictor → less prior disturbance)
- **Rationale**: keeps VLM in semantic role, action experts carry control
- **Deferred**: (ii) NL-style → trigger: D20 moves to LoRA-minimal/VLM2VLA path
### 6.5 Decisions — P5 / Evaluation (D24–D26)

#### [D24] Demo task & phasing (P5)
- **First demo**: in-hand cube rotation, 50–100g, 7cm, friction 0.5–1.5, arbitrary axis, angular error <10°, 5s episode. Sim ablation 30 trials/condition; real-robot 50+/condition
- **Phase 2**: 5 articulated tools (CATFA precedent, arXiv:2509.23075)
- **Non-negotiable**: phased demo (in-hand rotation → tool articulation)

#### [D25] 4-contribution ablation & falsifier (P5)
- **Ablation conditions** (VLA-level, not RL): (a) monolithic decoder + flat concat + no System0 + full-FT (baseline), (b) +split, (c) +structured input binding, (d) +System0, (e) +VLM-preservation (= full). Each contribution isolated as a one-factor delta from baseline + the full combination
- **Falsifier (per-metric, identity anchor)**:
  - v1 rejection: the **split** contribution fails ≥5% absolute improvement on at least one contact-precision metric (slip count OR pose stability)
  - v2 rejection: adding **structured binding** and **System0** each fails ≥3% additional on at least one contact-precision metric
  - VLM-preservation validated by generalization/OOD metric not regressing vs full-FT
  - All failing → VLA-level heterogeneous identity rejected
- **Non-negotiable**: per-metric falsifier with quantitative threshold; 4-contribution decomposition

#### [D26] Evaluation protocol (P5)
- **v1**: Grouped Blind Ensemble (operator blinding; BeingBeyond 2026) + AutoEval-style automation (arXiv:2503.24278) for the sim ablation; real-robot evaluation = manual + blind
- **Metrics**: contact-precision (slip count, pose stability) — falsifier; throughput (consecutive rotation count, rotations/sec) — field comparison; coordination corr($a_b$,$a_h$) — split validation; robustness (post-real-robot, success drop under perturbation, CATFA)

---

## 7. Anti-topics (Noise Filter) [AGENT-INPUT]

Excluded from weekly digest unless unusually strong tie to a Pillar/Decision:

- Mobile manipulation / whole-body humanoid (unless dexterous hand performs contact-rich learning)
- Locomotion / quadruped / bipedal gait (RMA family is exception — System0/P3 anchor)
- 2-finger parallel-jaw grippers only
- Pure teleoperation without learning (shared autonomy *with* learning allowed)
- Pure imitation from human video with no learning / physics-informed / closed-loop component
- **RL reward-engineering for generalized full-task** (out of scope unless System0-scoped: slip/grasp-retention)
- **Post-hoc correction/residual on a frozen VLA** that does not address the distribution-bound limitation
- Monolithic VLA decoders without arm-hand split; flat-concat multimodal fusion without per-finger attribution
- VLA papers: in scope only if (a) arm-hand split / heterogeneous experts, (b) structured tactile/proprio binding, (c) VLM-preservation / forgetting / over-specialization analysis, (d) System0-style low-level stabilization. Exclude pick-and-place-only.
- Grasping-only (lift-and-hold) — pre-grasp / nominal-pose in scope only in the tool-articulation phase
- Soft robotics hardware design without learning
- Survey / position papers (read manually, not via agent)
- Router-based MoE for action selection (DexReMoE monitoring is the exception — §10)

---

## 8. Tracked Literature [LIVING] [AGENT-INPUT]

> 5 pillars × ≤8 pinned + methodology base. Rebalance quarterly; replace, don't append.
> **Format rule** (canonical: `docs/STYLE.md` §3): every entry carries `[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX)` (DOI/official URL if no preprint; `[no public link]` if neither). Never fabricate arXiv IDs — verify resolution before pinning.

### 8.1 P1 Pinned — Heterogeneous Body/Hand Action Expert
| Paper | arXiv | Year | Role |
|---|---|---|---|
| π0 (Physical Intelligence) | [arXiv:2410.24164](https://arxiv.org/abs/2410.24164) | 2024 | Backbone (D7, D19); flow-matching action expert |
| π0.5 | [arXiv:2504.16054](https://arxiv.org/abs/2504.16054) | 2025 | Hierarchical inference; D6 reference |
| TwinBrainVLA | [arXiv:2601.14133](https://arxiv.org/abs/2601.14133) | 2026 | AsyMoT: frozen generalist + trainable specialist; D4/D7/D19 closest analog |
| DexterityGen (Yin et al.) | [arXiv:2502.04307](https://arxiv.org/abs/2502.04307) | 2025 | Bounded coarse→fine precedent (D6); antagonist evidence |
| LaMP | [arXiv:2603.25399](https://arxiv.org/abs/2603.25399) | 2026 | Dual-expert gated cross-attention (D4 deferred) |
| HEX | [arXiv:2604.07993](https://arxiv.org/abs/2604.07993) | 2026 | MoE + residual-gated cross-embodiment decoder (D4) |
| Shared-Autonomy Arm-Hand VLA (DexGrasp-VLA) | [arXiv:2511.00139](https://arxiv.org/abs/2511.00139) | 2025 | Anatomical arm/hand split (macro VR-teleop arm + autonomous hand VLA) + Arm-Hand Feature Enhancement module (D1/D4); shared-autonomy data collection |
| Demystifying Action Space Design | [arXiv:2602.23408](https://arxiv.org/abs/2602.23408) | 2026 | 13k+ real rollouts; joint=stability/task=generalization (D2 evidence) |

**Methodology base**: FiLM [arXiv:1709.07871](https://arxiv.org/abs/1709.07871) (D4); PCGrad [arXiv:2001.06782](https://arxiv.org/abs/2001.06782) (D1 gradient-conflict deferred); DQ-RISE [arXiv:2605.03363](https://arxiv.org/abs/2605.03363) (arm-hand action-space decoupling).

### 8.2 P2 Pinned — Structured Input-Modality Binding
| Paper | arXiv | Year | Role |
|---|---|---|---|
| SaTA (uses Sharpa Wave) | [arXiv:2510.14647](https://arxiv.org/abs/2510.14647) | 2025 | *Top*: Sharpa hardware + FiLM spatial-tactile (D11) |
| TacFiLM | [arXiv:2603.14604](https://arxiv.org/abs/2603.14604) | 2026 | FiLM tactile fusion (D11) |
| Sparsh (Meta FAIR) | [arXiv:2410.24090](https://arxiv.org/abs/2410.24090) | 2024 | Tactile foundation model (D11 pretraining deferred) |
| ViTacFormer (Berkeley) | [arXiv:2506.15953](https://arxiv.org/abs/2506.15953) | 2025 | Cross-attention visuotactile (D10/D12) |
| DexViTac | [arXiv:2603.17851](https://arxiv.org/abs/2603.17851) | 2026 | Kinematic-grounded tactile encoding (D8/D9) |
| Touch Dreaming | [arXiv:2604.13015](https://arxiv.org/abs/2604.13015) | 2026 | Latent tactile prediction aux (D11 deferred) |
| AdapTac | [arXiv:2505.13982](https://arxiv.org/abs/2505.13982) | 2025 | Force-guided attention + future-force aux (D11 deferred) |
| XL-VLA | [arXiv:2603.10158](https://arxiv.org/abs/2603.10158) | 2026 | Cross-hand latent (D9 portability) |

### 8.3 P3 Pinned — Hand-level System0 Module
| Paper | arXiv | Year | Role |
|---|---|---|---|
| HORA (Qi et al., CoRL'22) | [arXiv:2210.04887](https://arxiv.org/abs/2210.04887) | 2022 | In-hand rotation + RMA + privileged→tactile distill (D17/D18) |
| AnyRotate (Bristol/Cambrian) | [arXiv:2405.07391](https://arxiv.org/abs/2405.07391) | 2024 | D17 reward direct reference |
| CCGE | [arXiv:2603.10971](https://arxiv.org/abs/2603.10971) | 2026 | Contact-coverage reward (D17 deferred) |
| RMA (legged) | [arXiv:2107.04034](https://arxiv.org/abs/2107.04034) | 2021 | D18 teacher-student origin; Phase-3 RL fine-tuning deferred until real-robot transition |
| Static Friction Sim2Real (Hu et al.) | [arXiv:2503.01255](https://arxiv.org/abs/2503.01255) | 2025 | D18 static/dynamic friction split |
| Contact-Aware Neural Dynamics | [arXiv:2601.12796](https://arxiv.org/abs/2601.12796) | 2026 | DR limit; learned contact correction (D18, deferred) |
| π0.5 | [arXiv:2504.16054](https://arxiv.org/abs/2504.16054) | 2025 | Hierarchical inference = System1/System0 analog (D14) |

**Methodology base**: Eureka [arXiv:2310.12931](https://arxiv.org/abs/2310.12931) / DrEureka [arXiv:2406.01967](https://arxiv.org/abs/2406.01967) (D17 synthesis deferred); DAPG [arXiv:1709.10087](https://arxiv.org/abs/1709.10087) (demo integration); OpenAI Rubik's Cube ADR [arXiv:1910.07113](https://arxiv.org/abs/1910.07113).

### 8.4 P4 Pinned — VLM Pretraining Preservation

> Two columns split off the single "VLM" identity so lineage is visible at a glance: **VLM init** = initial weights, **Further-pretrain corpus** = what the paper's team stacked on top. `TBD` marks values still to be filled from the paper.
>
> 2026-05 rebalance: VLA-Adapter / PriorVLA / Multi-Embodiment Pretraining Data demoted from pins (VLA-Adapter and PriorVLA stay tracked in the P4 competitor section of `context/P4.md` §8; Multi-Embodiment promoted into the D22 catalog under `context/P4.md` §9). Slots reused for GR00T N1, Being-H0.5, Xiaomi-Robotics-0 to widen lineage coverage (D19b).

| Paper | arXiv | Year | VLM init | Further-pretrain corpus | Role |
|---|---|---|---|---|---|
| π0 | [arXiv:2410.24164](https://arxiv.org/abs/2410.24164) | 2024 | PaliGemma-2B | OXE + π in-house mix | Frozen-backbone + action-expert pattern (D19); v1 lineage (D19b) |
| π0.5 | [arXiv:2504.16054](https://arxiv.org/abs/2504.16054) | 2025 | PaliGemma | π0.5 mix (web pretrain + co-train) | Co-training / hierarchical (D21/D22) |
| VLM2VLA | [arXiv:2509.22195](https://arxiv.org/abs/2509.22195) | 2025 | Gemma-3-12B-IT (LoRA on all linear modules) | BridgeData v2, NL-formatted via Gemini-2.5 (fine-tune corpus, *no additional pretraining*) | LoRA + NL-action, forgetting mitigation (D20); triggers D23(ii) path |
| RT-2 | [arXiv:2307.15818](https://arxiv.org/abs/2307.15818) | 2023 | PaLI-X | web VLM data + robot co-FT | Web/robot co-FT prior retention (D20) |
| GR00T N1 | [arXiv:2503.14734](https://arxiv.org/abs/2503.14734) | 2025 | Eagle-2 (NVIDIA, 1.34B VLM portion) | humanoid trajectories + human video + synthetic | Cross-embodiment dual-system VLA; lineage benchmark (D19b/D22) |
| Being-H0.5 | [arXiv:2601.12993](https://arxiv.org/abs/2601.12993) | 2026 | TBD (not disclosed in paper; check GitHub config) | UniHand-2.0 (~35k h × 30 embodiments, 400M+ samples / 120B tokens; ~16k h ego video + ~14k h robot manip + ~5k h VL) | Human-video-centric pretraining + cross-embodiment (D22/D19b) |
| Xiaomi-Robotics-0 | [arXiv:2602.12684](https://arxiv.org/abs/2602.12684) | 2026 | Qwen3-VL-4B-Instruct | ~200M robot trajectory timesteps (DROID + MolmoAct + in-house cross-embodiment) + 80M+ VL samples (4.7B total params) | Open-weight VLA + real-time exec; open-weight lineage candidate (D19b) |
| MolmoAct2 | [arXiv:2605.02881](https://arxiv.org/abs/2605.02881) | 2026 | Molmo | MolmoAct mix | Per-layer KV-cache conditioning preserves VLM (D19/D23) |

### 8.5 P5 Pinned — Task Definition & Falsifiable Evaluation
| Paper | arXiv | Year | Role |
|---|---|---|---|
| OpenAI Learning Dexterous In-Hand | IJRR 2020 | 2018-20 | Consecutive-rotation metric (D26) |
| DexArt (CVPR'23) | [arXiv:2305.05706](https://arxiv.org/abs/2305.05706) | 2023 | Articulated benchmark (tool-articulation phase) |
| CATFA (In-Hand Articulated Tools) | [arXiv:2509.23075](https://arxiv.org/abs/2509.23075) | 2025 | Tool-articulation direct baseline; 5 tools |
| RoboEval | [arXiv:2507.00435](https://arxiv.org/abs/2507.00435) | 2025 | Behavioral metrics (D25 falsifier) |
| Grounding Sim2Real VLA | [arXiv:2603.22876](https://arxiv.org/abs/2603.22876) | 2026 | 10k-trial protocol; 4-dim eval |
| AutoEval | [arXiv:2503.24278](https://arxiv.org/abs/2503.24278) | 2025 | Sim ablation automation (D26) |
| NVIDIA Robot Policy Evaluation | [arXiv:2508.11117](https://arxiv.org/abs/2508.11117) | 2025 | Sim2real benchmarking; Isaac stack |
| DexReMoE | [arXiv:2508.01695](https://arxiv.org/abs/2508.01695) | 2025 | P1 architectural sibling; monitoring (§10) |

**Methodology base**: Grouped Blind Ensemble (BeingBeyond 2026, operator-blinding); SimplerEnv (CoRL'24); ArtiBench/ArtiBrain [arXiv:2511.20330](https://arxiv.org/abs/2511.20330) (cross-object generalization phase).

---

## 9. Researchers & Groups to Follow [LIVING]

### 9.1 Individuals
**P1 (Body/Hand Decoder)**: Physical Intelligence π team (Kevin Black, Danny Driess, Karl Pertsch, Lucy Xiaoyang Shi, Allen Z. Ren); Cewu Lu / Lixin Yang (SJTU MVIG/RISE — LaMP, DQ-RISE); Zhao-Heng Yin (Berkeley — DexterityGen); Toru Lin (Berkeley); Haozhi Qi (Berkeley/Meta).
**P2 (Structured Input)**: Carolina Higuera, Akash Sharma, Mustafa Mukadam, Mike Lambeta (Meta FAIR — Sparsh); Haoran Geng (Berkeley — ViTacFormer); Nathan Lepora (Bristol); Wenzhen Yuan (UIUC); SaTA authors (uses Sharpa hardware — verify).
**P3 (System0 / contact RL)**: Yecheng Jason Ma, Dinesh Jayaraman (UPenn — Eureka/DrEureka); Max Yang (Bristol/Cambrian — AnyRotate); Ashish Kumar, Zipeng Fu, Deepak Pathak, Jitendra Malik, Sergey Levine (RMA lineage); Aravind Rajeswaran, Vikash Kumar (DAPG).
**P4 (VLM preservation)**: Physical Intelligence π team; RT-2 / Brohan-Driess lineage; VLM2VLA / VLA-Adapter / PriorVLA authors (verify); MolmoAct authors (Allen AI).
**P5 (Evaluation)**: Marcin Andrychowicz (consecutive-rotation origin); Yiru Wang (RoboEval); Xuning Yang, Dieter Fox (NVIDIA/UW); CATFA / DexReMoE authors (verify).
**Cross-pillar**: Pulkit Agrawal (MIT Improbable AI); Lerrel Pinto (NYU); Ankur Handa, Yashraj Narang (NVIDIA GEAR); Jeannette Bohg, C. Karen Liu (Stanford).

### 9.2 Korean-affiliated groups (prevent local blind spot)
KAIST / SNU / NAVER Labs / POSTECH / UNIST (specific PIs — TBD by maintainer).

### 9.3 Labs / groups (watch code releases)
Physical Intelligence; Berkeley BAIR/RAIL; SJTU MVIG/RISE; Meta FAIR Robotics; NVIDIA Robotics/GEAR; UPenn GRASP; Bristol+Cambrian; Allen AI (MolmoAct); UW Fox group; NYU Pinto group; **Sharpa Robotics (Singapore)** — hardware vendor + competitor (own VTLA); **Genesis AI** — VLA-only strong performer (antagonist evidence).

---

## 10. Competitor / Kindred Monitoring [LIVING] [AGENT-INPUT]

Reviewed when Tracked Literature rebalances or a Decision-Log trigger fires.

### 10.1 VLA-only strong performers (antagonist evidence — "RL not necessary")
- **Genesis AI** — VLA-only does all tasks without RL/System0. *Watch trigger*: any release demonstrating contact-rich dexterity without low-level RL → directly tests the System0 necessity claim.
- **IMCopilot / Sharpa** ([arXiv:2603.08122](https://arxiv.org/abs/2603.08122)) — VLA calls Primitive Skill Policy, but only Stable Grasp / In-hand Rotation primitives; visible segmented motion. *Overlap*: hierarchical VLA+primitive. *Difference*: our System0 is a learned stabilization sub-loop, not a discrete primitive library. *Watch trigger*: any primitive-set expansion.

### 10.2 Bounded RL-in-VLA precedents
- **π RLT / RECAP** — leading-lab RL use, but deploy-ready fine-tuning only (RECAP is RL-concept, not actual RL deployment beyond RLT). Supports the "RL = fine-tuning, not capability source" antagonist framing. *Watch trigger*: any RL-as-capability (not fine-tuning) result from π.
- **DexterityGen** ([arXiv:2502.04307](https://arxiv.org/abs/2502.04307)) — RL primitive policy as data-acquisition aid; no guarantee RL covers all hard tasks. *Watch trigger*: target-task count / generalization claims.

### 10.3 Architectural siblings (P1 split)
- **LaMP** ([arXiv:2603.25399](https://arxiv.org/abs/2603.25399)) — two-expert gated cross-attn; split axis = scene-flow, not anatomical. v1 architecture comparison.
- **TwinBrainVLA** ([arXiv:2601.14133](https://arxiv.org/abs/2601.14133)) — AsyMoT frozen+trainable; closest analog. Watch real-robot validation.
- **HEX** ([arXiv:2604.07993](https://arxiv.org/abs/2604.07993)) / **DexReMoE** ([arXiv:2508.01695](https://arxiv.org/abs/2508.01695)) — embodiment/object routing vs anatomical split.
- **Shared-Autonomy Arm-Hand VLA / DexGrasp-VLA** ([arXiv:2511.00139](https://arxiv.org/abs/2511.00139)) — anatomical arm/hand split at *both* the data-collection layer (VR-teleop arm + autonomous hand VLA) and the decoder layer (Arm-Hand Feature Enhancement). Closest published analog to P1's anatomical claim. *Watch trigger*: any extension to in-hand reorientation or articulated-tool tasks (would intersect both phases directly).

### 10.4 Tool-articulation baseline & hardware-paired
- **CATFA** ([arXiv:2509.23075](https://arxiv.org/abs/2509.23075)) — frozen base + cross-attn adapter vs our split-both-trained; tool-articulation baseline.
- **SaTA** ([arXiv:2510.14647](https://arxiv.org/abs/2510.14647)) — uses Sharpa Wave; single-task adapter vs full-system identity.
- **Sharpa Robotics VTLA** — vendor + competitor; any release/demo.

*Differentiation hypothesis*: VLA-level anatomical split + structured binding + System0 wins on **contact-precision**; routing/correction approaches win on **object/embodiment generalization** but are distribution-bounded on contact precision.

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
- **Month A**: continual learning / catastrophic forgetting / PEFT (P4 adjacency)
- **Month B**: VLA architecture advances broadly (π, OpenVLA, self-improving VLA)
- **Month C**: structured / graph representation for multimodal binding (P2 adjacency)
- **Month D**: tactile sensing in prosthetics / neuroscience

---

## 13. Open Items & Dependency Graph [LIVING] [AGENT-INPUT]

### 13.A — Prerequisites & Defaults

| Item | Default fallback |
|---|---|
| First-demo cube fine spec | HORA/AnyRotate standard (D24 v1) |
| Arm hardware spec | Generic 7-DOF; Body=flange pose (D2) decouples |
| Real-world site/setup | physical workspace required |
| System0 tactile sim2real protocol (D18 prereq) | Akinola Isaac Gym lib + Chen et al. 2024 |
| Static friction range estimation (D18 prereq) | Wide DR range, gradual narrowing |
| 5 articulated tools list | CATFA 5 / DexArt subset + stapler/scissors/pen/pliers |
| Custom hand spec (2H 2026) | Continue with Sharpa; D11 swappable head allows P2 encoder swap |

> Defaults are strong enough that v1 sim-ablation entry is effectively possible from the current committed state; the remaining items unlock the real-robot, tool-articulation, and hand-hardware phases respectively.

### 13.B — Implementation Feasibility Unclarities
| Item | Status | Default if unresolved |
|---|---|---|
| π weight access | ✅ openpi (π0/π0.5/π0-FAST, Apache 2.0; PyTorch port + open-pi-zero) | — |
| π variant (π0/π0.5/π0.7) | 🟡 open | π0 (most stable) |
| Code base (JAX openpi / HF PyTorch / open-pi-zero) | 🟡 open | PyTorch port |
| Compute budget — GPU mem for D7 slice + FT × 8k–16k env (System0) | 🟡 unknown | Fallback 2k–4k env |
| Multi-embodiment pretraining data access (D22) | 🟡 unknown | π prior only (D22 v1) |
| Team / engineering capacity | 🟡 unknown — maintainer-side | — |

### 13.C — Architectural Sub-Unclarity (D7 / P1 core)

π0 is *already* MoT (PaliGemma 2.291B VLM + action expert 0.315B). D7 (i) "slice partition + FT" admits two readings:

| Reading | Content | Trade-off |
|---|---|---|
| **A — Repurpose** | π0 action expert as Hand; *add* new Body | Minimal π disruption; Body random-init loses prior |
| **B — Subdivide** | *Slice* π0 action expert into Body/Hand | Preserves prior both sides; needs slice-boundary + capacity decision |

→ Sub-readings of D7 v1; decide at code entry (explicit acknowledgment, no hard commit now). open-pi-zero = parameter-level reference. TwinBrainVLA AsyMoT + LaMP gated cross-attn = concrete references for the body→hand sharing module (D4).

### 13.D — Non-blocking Ongoing Items
| Item | Why valuable | Default posture |
|---|---|---|
| Korean PI lab contacts | Local network | Reach out when bandwidth permits |
| Genesis AI / Sharpa VTLA RE | §10 differentiation; tests System0 necessity | Monitor as antagonist evidence |
| Expected-but-unpublished failure mode | Highest-value search query | Capture when discovered |

### 13.E — Dependency Map

```
External / Ongoing (anytime):
   ├─ Korean PI labs            (no research blocker)
   ├─ Genesis AI / Sharpa VTLA  (antagonist monitoring)
   └─ Failure-mode articulation (high-value, anytime)

Resolved:
   [π weight access] ✅────→ D7 (i) cascade safe

Implementation-unblocked:
   [Cube spec default] ──→ 4-contribution ablation (also needs §13.B π variant/codebase)

Real-robot prerequisites (concurrent with sim ablation):
   ├─ System0 tactile sim2real protocol
   ├─ Friction range estimation
   ├─ Arm hardware spec
   └─ Real-world site/setup

Phase items (resolve before their phase fires):
   [5-tool list] → tool-articulation phase
   [Custom hand spec 2H26] → hand-hardware phase
```

### 13.F — Why This Structure?
Open-items separates near-term implementation blockers (§13.B/§13.C) from background research and external-world items (§13.D), without committing the order in which the remaining phases land.

---

## Appendix C: Open meta-questions

- **Domain epistemics**: detailed-design judgment is limited because the field is in unknown territory. Decision Log (defaults + triggers) is the principled response — each v1 default is a *bet* whose evidence accrues as the corresponding trigger condition is observed.
- **First-experiment fragility**: most v1-deferred decisions converge on the first ablation; a noisy first ablation → multiple v2 candidates activate at once.
- **Sim2real timing (System0-scoped)**: P3/System0 sim2real is plan, not implementation; the real-robot transition prerequisite (visuotactile sim protocol + friction range) gates it.
- **Publication race**: TwinBrainVLA / LaMP / CATFA / DexReMoE active. §10 differentiation; revisit when Tracked Literature rebalances.
- **Hardware partnership uncertainty**: Sharpa = vendor + competitor (own VTLA). Posture TBD.
- **OpenProblem — Limitation of Imitation Learning**: flow-matching diffusion policy models the data distribution; it does not directly learn the task-success *mechanism*. Whether this can be *fundamentally* overcome (beyond System0 stabilization patching the contact tail) is an open research question, not a closed decision. This is the deepest uncertainty under the VLA-level identity — directly tied to Antagonist A (correction modules are distribution-bounded; but so is the VLA itself). Track, do not prematurely resolve.

## Appendix C.1: Insufficient-knowledge classification

| Category | Resolution path | Example items | Action |
|---|---|---|---|
| **A — Knowledge gap** | Study (read) | π0 internals (openpi + open-pi-zero), VLM-preservation literature (VLM2VLA/RT-2/VLA-Adapter/PriorVLA), Sharpa Deform Map sim, IL-limitation theory | Self-paced reading; pre-condition for step (iii) |
| **B — Information gap** | Acquire (look up/ask) | unverified arXiv IDs (§13.B), π0.7 release, multi-embodiment data access, Korean PI contacts, compute/team capacity | Periodic scan; concurrent with A |
| **C — Experiential gap** | Run experiments (v1 ablation through the generalization phase) | Evidence for D1–D26 v1 defaults, §13.C D7 sub-reading, falsifier threshold appropriateness, System0-necessity test | Resolved only by step (iii)+ |
| **D — External world dependency** | Wait + monitor | Custom hand spec (2H 2026), Genesis AI / Sharpa VTLA / TwinBrainVLA follow-ups, π0.7+ release | Periodic scan via §10 |

**Key insight**: a "don't know enough to commit" feeling usually arises when Category A items are mistaken for Category C. The classification clarifies which gaps close *before* re-entering step (iii) and which require step (iii) itself.

---

*End.*
