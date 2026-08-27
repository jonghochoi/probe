# Probe
> Research scout for hand-centric dexterous manipulation.

---

# Research Context — Hand-centric Dexterous Manipulation

> **Last updated**: 2026-06-04
> **Maintainer**: \<your-name\>
> **Agent usage**: This file is the *static, cross-cutting* **global anchor** — Identity, Purpose, Long-term Context, Hardware, the Pillars overview, and cross-pillar references. Per-pillar working context (Decision Log, Tracked Literature, Anti-topics) is **owned by `context/P0–P5.md`**, which the retrieval agent reads (never writes). Findings go to `scouting/P#/YYYY-MM-DD.md` (one file per run, per pillar).

---

## 0. How to use this file [STABLE]

**What lives where**
- This document (`MASTER.md`) is the **global anchor**: cross-cutting content that is not specific to one pillar. It is *not* a superset of the pillar files.
- `context/P0–P5.md` are the **owners** of their pillar's Decision Log, Tracked Literature and Anti-topics. Edit the pillar file for pillar content; edit this anchor only for cross-cutting content.

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

> Most VLA-style policies attempt to converge on dexterity via a **monolithic action decoder + vision-dominant observation**, and most attempts to push the ceiling bolt a **correction/residual module onto a frozen VLA**. I argue both are dead ends for *dexterous **hand** manipulation*: a correction module is structurally bounded by the VLA's own local output distribution and must be re-trained whenever the VLA's motion pattern shifts, so it cannot exceed the VLA ceiling — it only tracks it. RL-as-core is likewise not the answer for *generalized* dexterity: generalized tasks cannot be reward-engineered, which is why leading labs use RL only as a deploy-ready fine-tuning stage (π RLT), not as the source of capability. **I argue dexterity must be tackled at the VLA level itself**, via (1) an **anatomically heterogeneous Body/Hand action-expert decoder**, (2) **structured multimodal observation fusion** — multi-camera spatial-geometric grounding + per-finger proprio-tactile binding beyond flat concat, (3) a **System1-gated low-level Hand System0 RL stabilization module** (the *only* place RL is necessary, because slip/grasp-retention *is* reward-engineerable), and (4) **data-efficient adaptation through the VLM pretraining recipe** (lineage × egocentric-centric corpus × staged recipe), with prior-preservation as one downstream lever. Task specification stays goal-centric (arm-hand integrated). Two supporting pillars feed this core — **P0** scouts the datasets and benchmarks the pretraining corpus draws on, and **P5** (a later-phase bet) folds an action-conditioned world model into the stack.

**Decomposition**
- *Antagonist A*: VLA-output correction/residual modules — performance bounded by the VLA's local output distribution; re-train on every VLA motion-pattern shift; full-pipeline bottleneck
- *Antagonist B*: RL-as-core for generalized dexterity — generalized tasks are not reward-engineerable; leading-lab RL use is deploy-ready fine-tuning only (π RLT), not capability source
- *Antagonist C*: monolithic decoder treating arm/torso/finger as one homogeneous action space + simple concat of heterogeneous modalities
- *Protagonist*: VLA-level tackling of dexterous **hand** manipulation — heterogeneous Body/Hand experts + structured multimodal observation fusion + System0 stabilization + pretraining composed for data-efficient adaptation
- *Stays goal-centric*: task specification (arm-hand integrated)
- *RL's confined role*: System0 hand-level contact stabilization only (tractable reward: slip suppression, grasp retention)

> *Maintainer's anchor (Korean original, preserved for self-reference)*:
> 대다수 VLA-style policy는 monolithic action decoder + vision-dominant observation으로 dexterity를 수렴시키려 하고, 성능 한계를 넘으려는 시도는 frozen VLA 위에 correction/residual 모듈을 붙인다. 그러나 보정 모듈은 VLA 출력 주변 local distribution 내로 성능이 한정되고 VLA 모션 패턴이 바뀔 때마다 재학습해야 하므로 VLA ceiling을 넘지 못한다. RL-as-core 또한 generalized task를 reward engineering할 수 없어 해답이 아니며, 선도사는 RL을 deploy-ready fine-tuning(π RLT)으로만 쓴다. 나는 dexterous **hand** manipulation을 VLA-level에서 직접 tackle해야 한다고 본다: (1) anatomically heterogeneous Body/Hand action expert, (2) structured multimodal observation fusion (multi-cam spatial-geometric grounding + per-finger proprio-tactile binding, flat-concat 초월), (3) System1-gated 저수준 Hand System0 RL 안정화(slip/grasp 유지는 reward-engineerable하므로 RL이 필요한 유일 지점), (4) VLM 사전학습 recipe(lineage × egocentric 중심 corpus × staged recipe)를 통한 data-efficient adaptation — prior 보존은 그 하위 레버. Task spec은 arm-hand 통합 goal-centric 유지. 이 코어는 두 지원 pillar가 받친다 — **P0**는 사전학습 corpus 가 끌어다 쓰는 dataset/benchmark 를 스카우팅하고, **P5**(후기 단계)는 action-conditioned world model 을 stack 에 결합한다.

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
**Body expert and hand expert both directly designed and trained at the VLA level.** No outsourcing of dexterity to a post-hoc correction module (which would be distribution-bounded by the VLA). Pretrained VLM/π weights are leveraged via a *deliberately composed pretraining recipe for data-efficient adaptation* (P4), with prior-preservation as one downstream lever. The Hand System0 RL module is the single RL component; everything else is VLA-level (flow-matching) learning.

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

**Six pillars (P0–P5).** P1–P4 are the architectural core; P0 (data) is the
upstream supporting pillar; P5 (world model) is a later-phase capability bet.
Decision-number allocation:

| Pillar | Owns | Decisions |
|---|---|---|
| P0 — VLA Datasets & Benchmarks | data/benchmark scouting | D24–D27 |
| P1 — Heterogeneous Body/Hand Action Expert | action-expert / action-space architecture | D1–D7 |
| P2 — Structured Multimodal Observation Fusion | spatial + multimodal observation fusion | D8–D12 |
| P3 — Hand-level System0 Module (RL-scoped) | low-level contact-stabilization RL | D13–D18 |
| P4 — Pretraining for Data-Efficient Adaptation | lineage × corpus × recipe | D19–D23 |
| P5 — World Model | action-conditioned world model integration | D28–D32 |

### 5.0 P0. VLA Datasets & Benchmarks
**Scope**: data is upstream of method. Dedicated scouting front-end for VLA datasets (robot action / human-egocentric video / mixed) + the scarce tactile/force/torque corpora + benchmarks/eval harnesses. Output feeds the P4 pretraining-corpus decisions. Egocentric + tactile/torque emphasis sets the priority data axis.

**Identity tie**: the pretraining corpus (P4 D22) and the egocentric data priority need an evidence-driven data front-end, not incidental scouting.

**Tracked items**: priority data axis (D24), tactile/torque data scouting (D25), benchmark/eval scouting scope (D26), license/usability bar (D27).

**Anti-topics**: method-only papers with no released data/benchmark; sub-pretraining-scale single-task sets; vision-only corpora pitched as sufficient for dexterity.

**Literature anchor**: EgoDex, Ego-Exo4D, UniHand-2.0, AgiBot World, DROID, RH20T (F/T), ManiSkill 3, vla-eval. See `context/P0.md` §5.

### 5.1 P1. Heterogeneous Body/Hand Action Expert
**Scope**: Body vs Hand action-expert design. Body/torso/arm handle macro motion (object approach, transport, placement); fingers handle post-contact contact-rich precision. Either an explicit BodyExpert–HandExpert split, or a single ActionExpert with strongly separated body/hand latents (comparison group). Body output = both-wrist or tool-flange pose (embodiment-transfer easing); Hand output = finger joint command. Includes Body↔Hand information-sharing, input-modality separation, control-rate separation, and π backbone integration.

**Identity tie**: heterogeneous-decoder claim → this pillar (the architectural core).

**Tracked items**: split form (D1), Body output space (D2), Hand output space (D3), Body↔Hand information sharing (D4), input-modality + control-rate separation (D5), coordination direction & flow (D6), π backbone integration / partition (D7).

**Anti-topics**: post-hoc correction/residual-on-frozen-VLA without addressing the distribution-bound limitation; pick-and-place-only VLAs with no action-architecture contribution. (Monolithic decoders + router/MoE action heads are surfaced as the comparison group, scored against the Body/Hand split — not rejected.)

**Scouting lens**: the Body/Hand split stays the *north star*, but the retrieval lens spans the broader action-expert / action-space architecture family — recall wide, thesis unchanged.

**Literature anchor**: π0 (backbone); Dexora (open-source bimanual), LaMP (dual-expert), Shared-Autonomy Arm-Hand VLA / DexGrasp-VLA (anatomical arm/hand split). TwinBrainVLA / PriorVLA / Demystifying tracked off-pin. See `context/P1.md` §5.

### 5.2 P2. Structured Multimodal Observation Fusion
**Scope**: elevate the observation on three axes — (a) **multi-camera spatial-geometric grounding** (geometry-grounded multi-view encoder → unified 3D-consistent embedding, vs flat per-camera concat); (b) **heterogeneous modality fusion beyond concat** (cross-attention / asymmetric fusion of vision + proprio + tactile + force, with per-finger/palm contact attribution preserved — ~10 finger + 2 palm tokens, topology-aware); (c) an **action/dynamics-aware vision encoder** (DynaFLIP / eVGGT family over a generic stem). The encoder *choice* is P2; the VLM *weights/lineage* are P4.

**Identity tie**: hand-level "observation elevation" — spatial information kept and registered, contact semantics attributed per finger, encoder action-aware — not implicitly learned from flat concat.

**Tracked items**: multi-camera spatial-geometric grounding (D8), action/dynamics-aware vision encoder (D9), heterogeneous modality fusion beyond concat (D10), proprio-tactile-force token construction (D11), topology-aware encoding + hand-level aggregation (D12).

**Anti-topics**: vision-only manipulation; flat-concat fusion that loses spatial registration or per-finger attribution; generic non-action-aware encoders pitched as sufficient.

**Literature anchor**: VGGT (multi-view geometry), eVGGT (geometry encoder for manipulation), DynaFLIP (action/dynamics-aware encoder), ForceFlow (asymmetric multimodal fusion), ViTacFormer (cross-attention visuotactile). See `context/P2.md` §5.

### 5.3 P3. Hand-level System0 Module (RL-scoped)
**Scope**: low-level RL contact-stabilization. System1 HandExpert emits finger commands; post-contact slip / grasp weakening / unstable contact need sub-policy-loop reaction. System0 = vision-excluded RL policy on tactile + finger joint state maintaining stable grasp/contact. Bypasses System1 output in nominal operation; activated only by System1 on/off signal during retention-critical intervals.

**Identity tie**: the *only* RL component; "supervision elevation" now scoped to a reward-engineerable sub-problem.

**Tracked items**: System0 role & operating regime (D13), System1↔System0 interface (D14), System0 input modality (D15), System0 output form (D16), System0 RL policy spec (D17), System0 sim2real (D18).

**Anti-topics**: RL reward-engineering for generalized full-task (out of scope unless System0-scoped); locomotion sim2real; contact-agnostic DR.

**Literature anchor**: HORA, AnyRotate (reward terms), DexSynRefine (residual RL + RMA contact adaptation), RMA (teacher-student adaptation), Static Friction Sim2Real, Contact-Aware Neural Dynamics, Beyond Binary (physics-grounded contact sim2real). See `context/P3.md` §5.

### 5.4 P4. Pretraining for Data-Efficient Adaptation
**Scope**: pretraining quality/composition is the upstream lever behind Genesis-style data-efficient adaptation (minutes of deploy data). Decide the **VLM backbone lineage** (= initial weights × further-pretrain corpus), the **pretraining data composition** (egocentric-only vs mixed dump — an *open* variable matching the in-house ego plan), the **staged recipe / curriculum**, and the **post-pretraining adaptation range** (freeze / PEFT / full) with its **prior-preservation strategy** (a downstream sub-lever, not the headline). Corpus scouting is shared with P0; a world-model pretraining objective is coordinated with P5.

**Identity tie**: pretraining composition is what lets minutes of deploy data suffice — the lever the whole VLA-level pivot rests on.

**Tracked items**: VLM backbone lineage + post-pretraining adaptation range (D19), prior-preservation strategy (D20), staged pretraining + adaptation recipe (D21), pretraining data composition — egocentric vs mixed (D22), action-representation × pretraining/preservation (D23).

**Anti-topics**: deploy-fine-tuning papers with no pretraining-composition / lineage lever; pick-and-place-only VLA with no adaptation-efficiency or forgetting analysis.

**Literature anchor**: π0/π0.5 (π lineage), GR00T N1 (cross-embodiment lineage), Being-H0.5 (human-video-centric pretraining), Xiaomi-Robotics-0 (open-weight lineage), Qwen-VLA (Qwen lineage + text-to-action pretraining), ConSFT (conservative adaptation). VLM2VLA / UAM tracked off-pin (preservation sub-lever). See `context/P4.md` §5.

### 5.5 P5. World Model
**Scope**: fold an action-conditioned world model (predictive model of environment dynamics) into the hand-centric VLA stack — as a latent dynamics prior / future-prediction auxiliary co-trained with the policy, eval-in-imagination, or RL-env. Hand-centric narrowing: **action-conditioned, egocentric, hand-object** world models with latent / 3D-flow (contact-relevant) prediction over raw-pixel generation. A *later-phase* capability bet.

**Identity tie**: forward dynamics is the predictive sense a VLA lacks; heavily-pretrained world models are the lever behind Genesis-style adaptation — scoped to hand-object egocentric prediction.

**Tracked items**: world-model role (D28), integration architecture (D29), prediction space (D30), action conditioning (D31), egocentric hand-object world model (D32).

**Anti-topics**: action-free video generation without robot transfer; driving/navigation world models; locomotion model-based RL; world models with no manipulation eval.

**Literature anchor**: DexWM (hand-object WM from human video), Being-H0.7 (latent world-action from ego video), WorldVLA (unified VLA+WM), LOME (action-conditioned egocentric WM), AHEAD (latent predictive WM for dynamic VLA), VLA-JEPA / ThinkJEPA (JEPA latent-prediction world models for VLA). See `context/P5.md` §5.

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
- **Month C**: spatial-geometric / multimodal fusion representation (P2 adjacency)
- **Month D**: tactile sensing in prosthetics / neuroscience

---

*End.*
