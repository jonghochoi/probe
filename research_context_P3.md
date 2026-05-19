# Research Context — P3: Hand-level System0 Module

> **P3 scope extract of `research_context.md` (single source of truth).**
> Narrowed to **Pillar 3 (Hand-level System0 Module, RL-scoped)**; P1/P2/P4/P5
> content lives in the full document, not here. P3 owns **D13–D18**.
> **Agent usage**: *static* context. The retrieval agent reads (never writes)
> this file. Weekly findings go to `research_log/YYYY-WW.md`.
> **Formatting & translation rules**: `docs/STYLE_GUIDE.md` (single source of
> truth — agent must read it before producing output).

---

## 1. Identity [STABLE] [AGENT-INPUT]

> RL-as-core is not the answer for *generalized* dexterity (generalized tasks are not reward-engineerable). But post-contact slip / grasp weakening / unstable contact *is* a narrow, reward-engineerable sub-problem. System0 is a System1-gated low-level RL stabilization module — the **only** place RL is necessary — running on tactile + finger-joint state, bypassing the System1 Hand expert only during retention-critical intervals. Task specification stays goal-centric (arm-hand integrated).

**Decomposition (P3-relevant)**
- *Antagonist*: RL reward-engineering for generalized full-task; locomotion-style sim2real; contact-agnostic domain randomization
- *Protagonist (P3 owns)*: vision-excluded RL contact-stabilization sub-loop — slip suppression / grasp retention / minor finger-posture correction, gated on/off by System1
- *Upstream context*: System1 Hand expert (P1) emits finger commands; System0 takes over only when gated; preserves the VLA-level capability source (full doc P1/P4)

> **Note**: P3 owns the low-level RL stabilization half. The decoder split
> (P1), structured input (P2), VLM preservation (P4), evaluation (P5) are out
> of scope here — see `research_context.md`.

---

## 2. Pillar P3 — Hand-level System0 Module (RL-scoped) [STABLE structure, LIVING content] [AGENT-INPUT]

**Scope**: low-level RL contact-stabilization. System1 HandExpert emits finger commands; post-contact slip / grasp weakening / unstable contact need sub-policy-loop reaction. System0 = vision-excluded RL policy on tactile + finger joint state maintaining stable grasp/contact. Bypasses System1 output in nominal operation; activated only by System1 on/off signal during retention-critical intervals.

**Identity tie**: the *only* RL component; "supervision elevation" scoped to a reward-engineerable sub-problem.

**Tracked items**: System0 role & operating regime (D13), System1↔System0 interface (D14), System0 input modality (D15), System0 output form (D16), System0 RL policy spec (D17), System0 sim2real (D18).

**Anti-topics**: RL reward-engineering for generalized full-task (out of scope unless System0-scoped); locomotion sim2real; contact-agnostic DR.

**Literature anchor**: HORA, AnyRotate (reward terms), CCGE (contact coverage), RMA (teacher-student adaptation), Static Friction Sim2Real, Contact-Aware Neural Dynamics, π0.5 (hierarchical inference as System1/System0 analog). See §6.

---

## 3. Revisit Checkpoints (CP1–CP5) [LIVING]

- **CP1**: v1 first ablation analysis (4-contribution ablation on in-hand rotation, sim)
- **CP2**: in-hand rotation first real-world demo result analysis
- **CP3**: tool articulation demo entry (phase 2; 5-tool evaluation set)
- **CP4**: hardware transition (Sharpa → xhand → in-house)
- **CP5**: cross-object generalization phase entry

**CP2 prerequisite (P3-owned)**: System0 tactile sim2real protocol verified (Chen et al. 2024 lineage) + static friction range estimation completed. System0 activates mostly at CP2 — plan, not current implementation.

---

## 4. Decision Log — P3 / System0 (D13–D18) [LIVING] [AGENT-INPUT]

Options / v1 / rationale / deferred (trigger + checkpoint). Append-only.

> P3 covers **D13–D18**. P1 (D1–D7), P2 (D8–D12), P4 (D19–D23),
> P5 (D24–D26) are out of scope here — see `research_context.md`.

#### [D13] System0 role & operating regime (P3)
- **Role options**: slip anticipation / stable grasp maintenance / minor finger posture correction
- **v1**: all three, scoped to: post-grasp grasp maintenance; in-hand stable-contact maintenance; insertion/contact retention
- **Rationale**: narrow, reward-engineerable sub-problem — the only place RL is justified
- **Constraint**: must NOT interfere with peg-in-hole insertion motion (gated off when System1 needs free finger motion)
- **Deferred**: expand to dynamic regrasp → trigger: static-maintenance scope too narrow at CP3 / **CP3**

#### [D14] System1↔System0 interface (P3)
- **Options**: (i) binary `maintain_grasp` on/off (bypass System1 when off → System0 takes finger command), (ii) continuous blend weight, (iii) System0 always-on residual
- **v1**: (i) binary on/off, bypass-when-off
- **Rationale**: cleanest interface; clearest ablation of System0 contribution
- **Deferred**: (ii) continuous blend → trigger: hard switching causes finger-command discontinuity / **CP2**

#### [D15] System0 input modality (P3)
- **v1**: tactile feature + finger joint position + velocity + joint torque (or motor current) + contact-state history. **Vision excluded** (by design)
- **Rationale**: sub-loop reaction speed requires vision-free low-latency state
- **Deferred**: add wrist IMU/force → trigger: tactile+proprio insufficient for slip anticipation / **CP2**

#### [D16] System0 output form (P3)
- **Options**: (i) finger joint command (direct), (ii) grip-force / impedance parameter, (iii) local stabilizing correction added to System1 output
- **v1**: (i) direct finger joint command (active only when gated on)
- **Rationale**: matches P1 D3 Hand output space; clean bypass semantics
- **Deferred**: (ii) impedance → trigger: position control overshoots contact force / **CP2**; (iii) correction-residual → trigger: full-bypass loses System1 intent during maintenance / **CP2**

#### [D17] System0 RL policy spec (P3)
- **State**: tactile + proprioceptive history (D15)
- **Action**: finger-level stabilizing command (D16)
- **Reward**: object retention + slip suppression + contact stability − excessive-force penalty − smoothness penalty (task/contact/slip core + AnyRotate term structure)
- **Termination**: object drop / contact loss / excessive deformation or force
- **Synthesis v1**: hand-crafted contact-aware; **deferred** Eureka/DrEureka contact-aware variant → trigger: hand-crafted reward search cost prohibitive / **CP1**
- **Algorithm**: PPO, GPU-parallel Isaac Lab (8k–16k env)

#### [D18] System0 sim2real (P3)
- **DR params**: static_friction + dynamic_friction (split, arXiv:2503.01255) + contact stiffness + restitution + mass + surface compliance + actuator delay/noise
- **Adaptation**: RMA-family teacher-student with contact-relevant extrinsics
- **Deferred (priority)**: RMA-style Phase-3 RL fine-tuning → **CP2 (pre sim→real)**; static-friction-aware DR scheduling → **CP2 (post-real-demo)**; learned contact correction (Contact-Aware Neural Dynamics) → **CP3**
- **Caveat**: System0-scoped only; activates mostly at CP2 — plan, not current implementation

---

## 5. P3 Anti-topics (Noise Filter) [AGENT-INPUT]

Excluded from the weekly digest unless an unusually strong tie to P3 or a P3 Decision (D13–D18):

- RL reward-engineering for generalized full-task (in scope only if System0-scoped: slip/grasp-retention)
- Locomotion / quadruped / bipedal gait (RMA family is the exception — System0 adaptation anchor)
- Contact-agnostic domain randomization
- Mobile manipulation / whole-body humanoid (unless dexterous hand contact-rich learning)
- Survey / position papers (read manually, not via agent)

---

## 6. P3 Tracked Literature [LIVING] [AGENT-INPUT]

> Hard cap 8 pinned. Rebalance quarterly; replace, don't append.
> **Format rule**: every entry carries `[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX)` (DOI/official URL if no preprint; `[no public link]` if neither). Never fabricate arXiv IDs. Canonical: `docs/STYLE_GUIDE.md` §3.

### 6.1 P3 Pinned — Hand-level System0 Module
| Paper | arXiv | Year | Role |
|---|---|---|---|
| HORA (Qi et al., CoRL'22) | [arXiv:2210.04887](https://arxiv.org/abs/2210.04887) | 2022 | In-hand rotation + RMA + privileged→tactile distill (D17/D18) |
| AnyRotate (Bristol/Cambrian) | [arXiv:2405.07391](https://arxiv.org/abs/2405.07391) | 2024 | D17 reward direct reference |
| CCGE | [arXiv:2603.10971](https://arxiv.org/abs/2603.10971) | 2026 | Contact-coverage reward (D17 deferred) |
| RMA (legged) | [arXiv:2107.04034](https://arxiv.org/abs/2107.04034) | 2021 | D18 teacher-student origin; Phase-3 RL fine-tuning deferred (CP2) |
| Static Friction Sim2Real (Hu et al.) | [arXiv:2503.01255](https://arxiv.org/abs/2503.01255) | 2025 | D18 static/dynamic friction split |
| Contact-Aware Neural Dynamics | [arXiv:2601.12796](https://arxiv.org/abs/2601.12796) | 2026 | DR limit; learned contact correction (D18 CP3) |
| π0.5 | [arXiv:2504.16054](https://arxiv.org/abs/2504.16054) | 2025 | Hierarchical inference = System1/System0 analog (D14) |

**Methodology base (non-pinned)**
| Paper | arXiv | Relevance |
|---|---|---|
| Eureka | [arXiv:2310.12931](https://arxiv.org/abs/2310.12931) | D17 reward synthesis deferred |
| DrEureka | [arXiv:2406.01967](https://arxiv.org/abs/2406.01967) | D17 contact-aware reward synthesis deferred |
| DAPG | [arXiv:1709.10087](https://arxiv.org/abs/1709.10087) | Demo integration |
| OpenAI Rubik's Cube ADR | [arXiv:1910.07113](https://arxiv.org/abs/1910.07113) | Automatic domain randomization |

---

## 7. P3 Researchers & Groups to Follow [LIVING]

> Ordered by proximity to the P3 anchor (low-level contact-stabilization RL + sim2real).

### 7.1 Individuals
- **Yecheng Jason Ma, Dinesh Jayaraman (UPenn)** — Eureka / DrEureka reward synthesis (D17)
- **Max Yang (Bristol/Cambrian)** — AnyRotate reward structure (D17)
- **Ashish Kumar, Zipeng Fu, Deepak Pathak, Jitendra Malik, Sergey Levine** — RMA lineage (D18 teacher-student)
- **Haozhi Qi (Berkeley/Meta)** — HORA in-hand rotation (D17/D18)
- **Aravind Rajeswaran, Vikash Kumar** — DAPG demo integration

### 7.2 Labs / groups (watch code releases)
- **UPenn GRASP** — reward synthesis (Eureka lineage)
- **Bristol + Cambrian** — in-hand rotation reward (AnyRotate)
- **Berkeley BAIR / RAIL** — HORA, dexterous sim-to-real
- **NVIDIA Robotics / GEAR** — Isaac Lab GPU-parallel RL, sim2real

---

## 8. P3 Competitor / Kindred Monitoring [LIVING] [AGENT-INPUT]

System0-necessity tests and bounded-RL precedents — review at every CP.

| Work | arXiv | Overlap | Difference vs P3 | Watch trigger |
|---|---|---|---|---|
| **Genesis AI** | — | VLA-only, all tasks without low-level RL | Directly tests the System0-necessity claim | Any contact-rich dexterity demo without low-level RL |
| **π RLT / RECAP** | — | Leading-lab RL use | Deploy-ready fine-tuning only, not capability source | Any RL-as-capability (not fine-tuning) result |
| **DexterityGen** | [2502.04307](https://arxiv.org/abs/2502.04307) | RL primitive policy as data aid | No guarantee RL covers all hard tasks | Target-task count / generalization claims |
| **IMCopilot / Sharpa** | [2603.08122](https://arxiv.org/abs/2603.08122) | VLA + Stable Grasp / In-hand Rotation primitives | Discrete primitive library vs learned stabilization sub-loop | Any primitive-set expansion |

*Differentiation hypothesis*: a System1-gated, reward-engineerable System0 contact loop wins on **contact retention precision**; pure VLA-only or discrete-primitive approaches either bound the contact tail or show segmented motion.

---

## 9. P3 Open Items & Cross-pillar Coupling [LIVING] [AGENT-INPUT]

### 9.A — Open implementation decisions

| Item | Status | Default if unresolved | Deadline |
|---|---|---|---|
| System0 tactile sim2real protocol (D18 prereq) | 🟡 open | Akinola Isaac Gym lib + Chen et al. 2024 | End of CP1 (CP2 gate) |
| Static friction range estimation (D18 prereq) | 🟡 open | Wide DR range, gradual narrowing | Just before CP2 |
| Compute budget — GPU mem × 8k–16k env | 🟡 unknown | Fallback 2k–4k env | Before CP1 exec |
| Reward synthesis route (hand-crafted vs Eureka) | 🟡 open | Hand-crafted contact-aware (D17 v1) | CP1 |

### 9.B — Cross-pillar coupling

> Maps to §14 dependency graph in the full `research_context.md`.

System0 is gated by the System1 Hand expert: the on/off interface (D14) and direct finger-command output (D16) must match **P1 D3** (Hand output space) and not interfere with **P1 D6** coordination. System0 is downstream of the VLA capability source (full doc P1/P4) and never substitutes for it — it patches the contact tail only. Sim2real (D18) is plan-stage and gated at **CP2**.

---

*P3 scope extract of `research_context.md`. For other pillars, decisions
D1–D12 / D19–D26, full §7 anti-topics, §9 researchers, §10 monitoring,
§14 dependency graph, and Appendix C, consult the full document.*
