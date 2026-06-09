# Probe
> Research scout for hand-centric dexterous manipulation.

---

# Research Context — Hand-centric Dexterous Manipulation

> **Last updated**: 2026-06-04
> **Maintainer**: \<your-name\>
> **Agent usage**: This file is the *static, cross-cutting* **global anchor** — Identity, Purpose, Long-term Context, Hardware, the Pillars overview, and cross-pillar references. Per-pillar working context (Decision Log, Tracked Literature, Anti-topics, Curated Lists) is **owned by `context/P1–P4.md`**, which the retrieval agent reads (never writes). Findings go to `scouting/P#/YYYY-MM-DD.md` (one file per run, per pillar).

---

## 0. How to use this file [STABLE]

**What lives where**
- This document (`MASTER.md`) is the **global anchor**: cross-cutting content that is not specific to one pillar. It is *not* a superset of the pillar files.
- `context/P1–P4.md` are the **owners** of their pillar's Decision Log, Tracked Literature, Anti-topics, and Curated Lists. Edit the pillar file for pillar content; edit this anchor only for cross-cutting content.

**Section markers**
- `[STABLE]`: changes rarely (identity, purpose, hardware)
- `[LIVING]`: updated as research progresses
- `[AGENT-INPUT]`: retrieval agent conditions on this — keep signal-dense

**Update protocol**
- Identity / Purpose: change only with deliberate review (semantic shift, not phrasing)
- Pillars: structure stable; tracked items within can evolve as evidence accumulates

**Output formatting & authoring rules**
All formatting rules (emoji system, link format, Korean authoring principles) are consolidated in **`docs/STYLE.md`** — the single source of truth. The agent must read `docs/STYLE.md` before producing any output. Do not duplicate formatting rules here; edit `docs/STYLE.md` instead.

**Audience**: maintainer (self, future-self) + AI retrieval agent + future collaborators. Keep terminology accessible without sacrificing precision.

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
**Decision-log depth**: skeleton (key branchpoints recorded; not exhaustive)

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
- Backbone weights from openpi (Apache 2.0).

---

## 5. Pillars [STABLE structure, LIVING content] [AGENT-INPUT]

Four pillars.

### 5.1 P1. Heterogeneous Body/Hand Action Expert
**Scope**: Body vs Hand action-expert design. Body/torso/arm handle macro motion (object approach, transport, placement); fingers handle post-contact contact-rich precision. Either an explicit BodyExpert–HandExpert split, or a single ActionExpert with strongly separated body/hand latents (comparison group). Body output = both-wrist or tool-flange pose (embodiment-transfer easing); Hand output = finger joint command. Includes Body↔Hand information-sharing, input-modality separation, control-rate separation, and π backbone integration.

**Identity tie**: heterogeneous-decoder claim → this pillar (the architectural core).

**Tracked items**: split form (D1), Body output space (D2), Hand output space (D3), Body↔Hand information sharing (D4), input-modality + control-rate separation (D5), coordination direction & flow (D6), π backbone integration / partition (D7).

**Anti-topics**: monolithic decoders without arm-hand split; router-based MoE (different pattern; DexReMoE monitoring exception); post-hoc correction/residual-on-frozen-VLA without addressing distribution-bound limitation.

**Literature anchor**: π0/π0.5 (backbone); TwinBrainVLA (AsyMoT frozen-generalist + trainable-specialist), LaMP (dual-expert), Dexora (open-source bimanual), PriorVLA (frozen Prior + Adaptation, D7), Shared-Autonomy Arm-Hand VLA / DexGrasp-VLA (anatomical arm/hand split), Demystifying Action Space Design (D2 evidence). See `context/P1.md` §5.

### 5.2 P2. Structured Input-Modality Binding
**Scope**: replace simple concat/token-append with finger/palm-bound structured tokens. Each finger's joint state + that finger's tactile feature → one local embedding (~10 finger + 2 palm tokens). Topology-aware encoding (finger/hand identity, palm-relative fingertip pose, kinematic chain). Hand-level aggregation encoder. Multi-camera vision pre-fusion (cross-attention fuser → unified spatial embedding) before the VLM.

**Identity tie**: hand-level "observation elevation" — finger-wise contact semantics made explicit, not implicitly learned.

**Tracked items**: finger/palm structured token construction (D8), topology-aware encoding (D9), hand-level aggregation encoder (D10), visuotactile/proprio-tactile encoder candidate (D11), multi-camera pre-fusion (D12).

**Anti-topics**: vision-only manipulation; pure tactile-only without structured binding; flat-concat fusion without per-finger attribution.

**Literature anchor**: SaTA (Sharpa hardware), ForceFlow (contact-driven flow), Sparsh, ViTacFormer, DexViTac (kinematic-grounded tactile), Touch Dreaming (latent tactile prediction), Mirror Touch Net (visuo-tactile alignment), XL-VLA. See `context/P2.md` §5.

### 5.3 P3. Hand-level System0 Module (RL-scoped)
**Scope**: low-level RL contact-stabilization. System1 HandExpert emits finger commands; post-contact slip / grasp weakening / unstable contact need sub-policy-loop reaction. System0 = vision-excluded RL policy on tactile + finger joint state maintaining stable grasp/contact. Bypasses System1 output in nominal operation; activated only by System1 on/off signal during retention-critical intervals.

**Identity tie**: the *only* RL component; "supervision elevation" now scoped to a reward-engineerable sub-problem.

**Tracked items**: System0 role & operating regime (D13), System1↔System0 interface (D14), System0 input modality (D15), System0 output form (D16), System0 RL policy spec (D17), System0 sim2real (D18).

**Anti-topics**: RL reward-engineering for generalized full-task (out of scope unless System0-scoped); locomotion sim2real; contact-agnostic DR.

**Literature anchor**: HORA, AnyRotate (reward terms), DexSynRefine (residual RL + RMA contact adaptation), RMA (teacher-student adaptation), Static Friction Sim2Real, Contact-Aware Neural Dynamics, Beyond Binary (physics-grounded contact sim2real). See `context/P3.md` §5.

### 5.4 P4. VLM Pretraining Preservation
**Scope**: generalization/situation-understanding originates in the VLM backbone; full fine-tuning on deploy data over-specializes and erodes the pretrained prior. Decide VLM FT range (freeze / partial / LoRA-adapter / full), prior-preservation strategy, staged training recipe, multi-embodiment pretraining data, and the action-representation × VLM-preservation relationship. The **VLM lineage itself** (= initial weights × further-pretrain corpus) and the **multi-embodiment pretraining data catalog** are first-class P4 variables, not only the preservation strategy on top of them.

**Identity tie**: protects the VLA ceiling that the whole identity rests on; without it, the VLA-level pivot self-defeats.

**Tracked items**: VLM FT range (D19), VLM backbone lineage choice (D19b), prior-preservation strategy (D20), staged training recipe (D21), multi-embodiment pretraining data (D22), action-representation × VLM-preservation (D23).

**Anti-topics**: action-only papers ignoring backbone preservation; pick-and-place-only VLA without forgetting/over-specialization analysis.

**Literature anchor**: π0/π0.5, VLM2VLA (LoRA + NL-action, forgetting mitigation), UAM (dual-stream preservation without full freeze), VLA-Adapter (Bridge Attention), PriorVLA (prior-preserving adaptation), multi-embodiment data survey [arXiv:2506.19121], ConSFT (conservative SFT, π0-tested). See `context/P4.md` §5.

---

## 6. Venue Priority [AGENT-INPUT]

| Tier | Venues |
|------|--------|
| 1 | CoRL, RSS |
| 2 | ICRA, IROS |
| 3 | T-RO, RA-L (journal — archival weight) |
| 4 | arXiv raw (cs.RO, cs.LG) — noisiest, lowest default weight |
| — | NeurIPS/ICML robotics workshops — read only if pinned author |

---

## 7. Cross-pollination Budget [AGENT-INPUT]

1 paper per month from an adjacent field that plausibly transfers. Rotating:
- **Month A**: continual learning / catastrophic forgetting / PEFT (P4 adjacency)
- **Month B**: VLA architecture advances broadly (π, OpenVLA, self-improving VLA)
- **Month C**: structured / graph representation for multimodal binding (P2 adjacency)
- **Month D**: tactile sensing in prosthetics / neuroscience

---

*End.*
