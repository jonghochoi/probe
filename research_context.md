# Probe
> Research scout for hand-centric dexterous manipulation.

---

# Research Context

> **Version:** draft-v0.1 (2026-04-22) · **Maintainer:** <your-name>
> **Agent usage:** This is the *static* context. Agent reads (never writes) this file.
> Weekly findings are appended to `research_log/YYYY-WW.md` instead.

---

## 0. How to use this file

- Sections marked `[STABLE]` change rarely (hardware, stack). Edit when setup changes.
- Sections marked `[LIVING]` are rebalanced monthly during self-review.
- Sections marked `[AGENT-INPUT]` are what the retrieval agent conditions on. Keep them *signal-dense*; bloat here directly degrades retrieval quality.
- Papers listed here are **pinned** — they define the semantic neighborhood for citation-graph expansion. Rule of thumb: never exceed 8 pinned. Replace, don't append.

### Output formatting & translation rules
All formatting rules (emoji system, link format, Korean translation principles)
are consolidated in **`STYLE_GUIDE.md`** — the single source of truth.
The agent must read `STYLE_GUIDE.md` before producing any output.
Do not duplicate formatting rules here; edit `STYLE_GUIDE.md` instead.

### Link format rule [AGENT-INPUT]
Every paper entry surfaced by the agent — whether in the weekly scouting report,
the pinned literature table, or context suggestions — **must** include:
1. The arXiv ID in the form `arXiv:XXXX.XXXXX`
2. A direct hyperlink in Markdown format: `[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX)`

If no arXiv preprint exists, use the DOI or official proceedings URL instead:
`[DOI](https://doi.org/...)`

If neither is available, write `[no public link]` explicitly — do not omit the field.

---

## 1. Target Hardware & Stack [STABLE]

**Robot**
- Near-term: **Sharpa Hand**, 22-DOF
- Mid-term: **in-house custom hand** (spec TBD — DOF, tendon layout, sensor modality, control rate)
- Design guideline: **avoid lock-in to Sharpa-specific Deform Map tactile structure**. Prefer generalizable approaches that port to the custom hand. Sharpa-only experiments are acceptable when the method is transferable.
- Sensing: fingertip tactile (continuous-valued deformation field on Sharpa; modality on custom hand TBD). Encoder needed (CNN / ViT-tiny / visuotactile fusion) — see Q5.

**Simulation**
- Primary: **NVIDIA Isaac Sim + Isaac Lab**
- Secondary (under evaluation): **MuJoCo** — alternative for contact tuning and differentiable-sim experiments
- Contact: PhysX rigid-body point contact (Signorini-Coulomb); known gap vs. real fingertip viscoelastic deformation

**Training**
- GPU-parallel RL, **8,192–16,384 envs** in current runs
- Primary algo: **PPO**. SAC / DreamerV3 considered only if sample efficiency becomes a hard bottleneck.
- Distillation: privileged teacher → sensor-only student (RMA-family); see Q3 for quantitative probing.

---

## 2. Active Research Questions [AGENT-INPUT] [LIVING]

Ranked by current priority. Agent scores incoming papers on which of these they touch.

| # | Priority | Question |
|---|----------|----------|
| **Q1** | **HIGH** | **VLA ↔ Hand Expert bridge.** VLA (system-1) synthesizes a nominal hand pose (wrist pose + natural grasping posture) and grounds it to the object; the RL expert (system-0) executes with precision. How should the bridge layer be designed? Compare (a) residual RL on top of VLA output, (b) latent conditioning, (c) shared-autonomy handoff, (d) nominal-pose-as-goal + closed-loop RL — which is preferable for 22-DOF contact-rich tasks? How is the nominal pose itself generated/grounded? |
| **Q2** | **HIGH** | **Single-skill mastery for demo.** What are the minimal sufficient conditions to push a single task (e.g., in-hand rotation, bottle-cap opening) to near-100% success in both sim and real? Where is the dominant bottleneck — reward shaping, observation choice, curriculum, or action space? Do Eureka/DrEureka-style automatic reward syntheses actually help at the single-task extreme, or do hand-crafted contact-aware rewards win? |
| **Q3** | **HIGH** | **Sim2Real + RMA quantification.** (a) How do we *quantify* what RMA extrinsics actually capture (mutual information, probing classifiers)? (b) What is an effective system-ID / real2sim workflow to narrow DR ranges (differentiable sim, meta-adaptation, frame-wise DR)? (c) How does the choice of teacher→student distillation loss (MSE vs. KL vs. DAgger) affect sim2real transfer? |
| **Q4** | MED | **Primitive skill MoE + online adaptation.** Given individual primitive policies (re-orientation, in-hand rotation, controlled release, in-hand translation), how do we compress their latents into a unified space and enable few-shot online adaptation to a target task with minimal real data? Trade-offs among router-based MoE, orthogonal skill basis, and residual gating? |
| **Q5** | MED | **Visuotactile encoder design.** How should Sharpa Deform Map (or the custom hand's tactile modality) be fused with vision to maximize target-task performance? Which fusion style (cross-attention, contact-grounded tokens, flow-based fusion) is most robust under sim→real transfer? |
| **Q6** | LOW | **Cross-object / cross-hardware generalization.** When policies are transferred to novel objects or a new hand, what is the dominant failure mode — observation's geometric prior, DR range, or action space choice? |

---

## 3. Working Hypotheses [AGENT-INPUT] [LIVING]

Agent should probe these — surface papers that either support or *challenge* them. Falsification > confirmation.

- **H1.** When VLA provides an object-grounded nominal hand pose, the RL expert's exploration budget shrinks by 1–2 orders of magnitude and sim2real stability improves over scratch RL. *Probe:* DexVIP, UnidexFPM, PLD (VLA+residual RL), DexterityGen's teleop-prompt structure, shared-autonomy handoff papers.
- **H2.** Near-100% on a single skill is won by reward-hacking-resistant curriculum + narrowed DR, not by automatic reward synthesis. Hand-crafted contact-aware rewards remain the stronger baseline at the extreme. *Probe:* HORA / AnyRotate ablations, DrEureka critiques, curriculum-for-dexterity papers.
- **H3.** The informative content of RMA teacher extrinsics actually lives in a low-dimensional physical subspace (friction, mass, CoM, damping). Identifying that subspace via system ID sharply accelerates adaptation. *Probe:* RMA2, FRMA, DexCtrl, meta-adaptation with few real rollouts.
- **H4.** A primitive-skill MoE with an orthogonal, state-adaptive latent basis adapts few-shot faster than concat-style MoE. *Probe:* SMP (Skill MoE), ResDex, MoDE-VLA / IMCopilot.
- **H5.** A fully learned nominal-hand-pose generator is not ROI-positive; human-video priors + geometric pre-grasp heuristics cover most of the value. *Probe:* DexVIP, UnidexFPM, functional grasping, Diffangle-Grasp.
- **H6.** A visuotactile encoder trained with a contact-consistency loss produces more object-agnostic policies than raw concatenation. *Probe:* FBI (Flow Before Imitation), ViTacFormer, GelFusion, Contact-Grounded Policy.

---

## 4. Pinned Literature [AGENT-INPUT] [LIVING]

Core papers defining the semantic neighborhood. **Max 8.** Replace quarterly.

**Format rule:** Every entry must include a direct link.
Use `[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX)` for preprints,
`[DOI](https://doi.org/...)` for published-only works, or `[no public link]` if unavailable.

| Short name | Ref | Link | Why pinned (↔ Q#) |
|---|---|---|---|
| **HORA** (Qi'22) | *In-Hand Object Rotation via Rapid Motor Adaptation*, CoRL 2022 | [arXiv:2210.04887](https://arxiv.org/abs/2210.04887) | Current in-hand rotation demo base + canonical RMA reference (Q2, Q3) |
| **SimToolReal** (Kedia/Lum'26) | *An Object-Centric Policy for Zero-Shot Dexterous Tool Manipulation*, arXiv 2602.16863 | [arXiv:2602.16863](https://arxiv.org/abs/2602.16863) | Object-centric, single-policy zero-shot tool use; sim2real + universality exemplar (Q1, Q2, Q6) |
| **DexterityGen (DexGen)** (Yin'25) | *Foundation Controller for Unprecedented Dexterity*, arXiv 2502.04307, RSS 2026 | [arXiv:2502.04307](https://arxiv.org/abs/2502.04307) | RL-trained primitive set + human-teleop prompt → foundation controller; reference architecture for VLA↔Expert bridge (Q1, Q4) |
| **DeXtreme** (Handa'23) | Handa et al., ICRA 2023 | [arXiv:2210.13702](https://arxiv.org/abs/2210.13702) | Isaac Gym → Isaac Lab sim2real methodology baseline (Q3) |
| **Factory** (Narang'22) | Narang et al., RSS 2022 | [arXiv:2205.03532](https://arxiv.org/abs/2205.03532) | PhysX contact solver advances, contact-rich assembly (Q3) |
| **PLD** (ICLR 2026) | *Self-Improving VLA with Residual Policies* | [no public link] | Freezes VLA backbone and trains residual actors that take over in failure regions; candidate bridge architecture (Q1) |
| **RMA2** (Liang'24) | *Rapid Motor Adaptation for Robotic Manipulator Arms*, CVPR 2024 | [arXiv:2312.01843](https://arxiv.org/abs/2312.01843) | Extends RMA to manipulation with vision + ablation on extrinsics design (Q3) |
| **MoDE-VLA / IMCopilot** (2026) | *Mixture-of-Dexterous-Experts VLA* + RL-trained atomic skill copilot, arXiv 2603.08122 | [arXiv:2603.08122](https://arxiv.org/abs/2603.08122) | MoE + VLA + force/tactile residual injection; direct hit on Q4, informs Q1 |

---

## 5. Researchers & Groups to Follow [AGENT-INPUT] [LIVING]

Agent queries arXiv listing API by author for new submissions in last 14 days.

**Individuals (priority: new submissions auto-surface)**
- Haozhi Qi (Berkeley / Meta) — in-hand rotation, RMA lineage, HORA
- Tyler Ga Wei Lum, Kushal Kedia (Stanford) — SimToolReal
- Jeannette Bohg, C. Karen Liu (Stanford) — object-centric RL, dexterous manipulation
- Zhaoheng Yin (UC Berkeley) — DexterityGen
- Ashish Kumar (Berkeley) — RMA originator
- Yichao Liang — RMA2 for manipulators
- Pulkit Agrawal (MIT Improbable AI)
- Pieter Abbeel (Berkeley)
- Lerrel Pinto (NYU)
- Ankur Handa (NVIDIA GEAR)
- Yashraj Narang (NVIDIA) — contact sim + Factory
- Nathan Lepora (Bristol) — tactile sensing, TacTip
- Wenzhen Yuan (UIUC) — tactile robotics
- Tess Hellebrekers (Meta) — tactile hardware
- Matei Ciocarlie (Columbia) — dexterous hand mechanisms
- Abhishek Gupta (UW) — manipulation RL
- Jitendra Malik (Berkeley / Meta) — co-author on in-hand line
- Moritz Reuss — VLA architecture surveys / ICLR 2026 VLA landscape
- Physical Intelligence (π0 team) — VLA base architectures

**Groups / labs (watch code releases, not just papers)**
- NVIDIA GEAR — Isaac Lab upstream
- Stanford SVL / IPRL — SimToolReal, object-centric dexterous
- Physical Intelligence — π0, VLA generalists
- Berkeley BDML / BAIR — DexGen, dexterous manipulation
- Meta FAIR Robotics — DIGIT, Sparsh, tactile infra
- MIT Improbable AI — in-hand manipulation
- Bristol Tactile Robotics
- CMU RoboTouch

---

## 6. Venue Priority [AGENT-INPUT]

Used for recency weighting. More recent in Tier 1 > older in Tier 3.

| Tier | Venues |
|------|--------|
| 1 | CoRL, RSS |
| 2 | ICRA, IROS |
| 3 | T-RO, RA-L (journal — archival weight) |
| 4 | arXiv raw (cs.RO, cs.LG) — noisiest, lowest default weight |
| — | NeurIPS/ICML robotics workshops — read only if pinned author |

---

## 7. Anti-topics (Noise Filter) [AGENT-INPUT]

Papers matching these **are excluded** from weekly digest unless they have an unusually strong tie to an Active Question.

- Mobile manipulation / whole-body humanoid (unless a dexterous hand is attached and is actually learning contact-rich behavior)
- Locomotion / quadruped / bipedal gait
- 2-finger parallel-jaw grippers only
- Pure teleoperation without any learning component (shared autonomy *with* RL / residual learning is allowed — see Q1)
- Pure imitation from human video with no RL / physics-informed / closed-loop component
- **VLA papers are now in scope** — include them if they satisfy at least one of: (a) a low-level dexterous control component, (b) a bridge / residual architecture with an RL expert, (c) tactile / force modality injection. Exclude VLA papers that only demonstrate task-level pick-and-place with no low-level learning.
- Grasping-only papers (lift-and-hold; no in-hand reorientation or contact-rich interaction) — but pre-grasp / nominal-pose papers are in scope for Q1 / H5
- Soft robotics hardware design without learning
- Survey / position papers (read manually, not through agent)

---

## 8. Cross-pollination Budget [AGENT-INPUT]

To avoid echo chamber: agent **must** surface 1 paper per month from an adjacent field that plausibly transfers. Rotating targets:

- Month A: system identification / differentiable simulation / real2sim pipelines
- Month B: VLA architecture advances broadly (π0, OpenVLA, self-improving VLA) — manipulation *or* non-manipulation as long as the architectural pattern can transfer
- Month C: MoE routing / skill discovery / latent skill composition outside dexterous manipulation
- Month D: tactile sensing in prosthetics / neuroscience (kept from prior version)

---

## 9. Feedback Loop [LIVING]

Filled monthly by user, **not** by agent. Without this the agent cannot be evaluated.

| Month | Papers surfaced | Actually read | Influenced an experiment / decision | Notes |
|-------|-----------------|---------------|-------------------------------------|-------|
| 2026-04 | — | — | — | baseline month |
| 2026-05 | | | | |

**Quarterly review question** (every 3 months): *Has my thinking on Q1–Q6 actually shifted? If no, the retrieval pipeline is underperforming — revisit pinned papers and hypotheses.*

---

## 10. Intentional gaps [for user to fill]

The following are deliberately left empty. Filling them in sharpens agent targeting:

- [ ] **Custom hand spec**: DOF, tendon layout, sensor modality, control rate — affects every Q1–Q6
- [ ] **Bridge interface**: what does VLA pass to the RL expert? nominal pose vs. goal pose vs. latent vs. command sequence — specializes Q1
- [ ] **Fix a single-skill demo task**: pick one (in-hand rotation / bottle-cap opening / …) and declare the success metric (success rate, time, object set, # trials) — makes Q2 measurable
- [ ] **Primitive skill granularity**: define the boundary among re-orientation, in-hand rotation, controlled release, in-hand translation — Q4 depends on this
- [ ] **RMA quantification metric**: declare concrete metrics (extrinsics probing accuracy, time-to-asymptote under adaptation, DR-range shrinkage after system ID) — Q3
- [ ] **Sim2real evaluation protocol**: specific object set, success metric, # trials — without this, "sim2real gap" is unfalsifiable
- [ ] **Korean-affiliated groups** to add (KAIST, SNU, NAVER Labs) — prevents agent blind spot to local work
- [ ] **An expected-but-unpublished failure mode** — articulating this is your highest-value search query
