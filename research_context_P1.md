# Research Context — P1: Heterogeneous Body/Hand Action Expert

> **P1 scope extract of `research_context.md` (single source of truth).**
> Narrowed to **Pillar 1 (Heterogeneous Body/Hand Action Expert)**; P2–P5
> content lives in the full document, not here. P1 owns **D1–D7**.
> **Agent usage**: *static* context. The retrieval agent reads (never writes)
> this file. Findings go to `research_log/YYYY-MM-DD-P1.md` (one per run).
> **Formatting & authoring rules**: `docs/STYLE_GUIDE.md` (single source of
> truth — agent must read it before producing output).

---

## 1. Identity [STABLE] [AGENT-INPUT]

> Most VLA-style policies attempt dexterity via a **monolithic action decoder + vision-dominant observation**, and most ceiling-pushing attempts bolt a **correction/residual module onto a frozen VLA** — which is structurally bounded by the VLA's local output distribution and must be re-trained on every motion-pattern shift. Dexterous **hand** manipulation must instead be tackled at the VLA level: an **anatomically heterogeneous Body/Hand action-expert decoder** (both directly designed and trained), structured input binding, a System1-gated System0 stabilization layer, and VLM-prior preservation. Task specification stays goal-centric (arm-hand integrated).

**Decomposition (P1-relevant)**
- *Antagonist*: monolithic decoders (arm/torso/finger in one homogeneous space); post-hoc correction-on-frozen-VLA (distribution-bounded)
- *Protagonist (P1 owns)*: heterogeneous Body/Hand action-expert decoder — Body = both-wrist/tool-flange pose (embodiment-transfer easing); Hand = finger joint command (contact precision)
- *Upstream context*: body grasp/arm intent + backbone visual/task embedding (VLM prior preserved — see full doc P4)

> **Note**: P1 owns the heterogeneous-decoder half. Structured input binding
> (P2), System0 (P3), VLM preservation (P4), evaluation (P5) are out of scope
> here — see `research_context.md`.

---

## 2. Pillar P1 — Heterogeneous Body/Hand Action Expert [STABLE structure, LIVING content] [AGENT-INPUT]

**Scope**: Body vs Hand action-expert design. Body/torso/arm handle macro motion (object approach, transport, placement); fingers handle post-contact contact-rich precision. Either an explicit BodyExpert–HandExpert split, or a single ActionExpert with strongly separated body/hand latents (comparison group). Body output = both-wrist / tool-flange pose; Hand output = finger joint command. Includes Body↔Hand information sharing, input-modality separation, control-rate separation, and π backbone integration.

**Identity tie**: heterogeneous-decoder claim → this pillar (the architectural core).

**Tracked items**: split form (D1), Body output space (D2), Hand output space (D3), Body↔Hand information sharing (D4), input-modality + control-rate separation (D5), coordination direction & flow (D6), π backbone integration / partition (D7).

**Anti-topics**: monolithic decoders without arm-hand split; router-based MoE (different pattern; DexReMoE monitoring exception); post-hoc correction/residual-on-frozen-VLA without addressing the distribution-bound limitation.

**Literature anchor**: π0/π0.5 (backbone); TwinBrainVLA (AsyMoT), DexterityGen (bounded precedent), LaMP / HEX (dual-expert), RLDX-1, Demystifying Action Space Design (D2 evidence). See §6.

---

## 3. Revisit Checkpoints (CP1–CP5) [LIVING]

- **CP1**: v1 first ablation analysis (4-contribution ablation on in-hand rotation, sim)
- **CP2**: in-hand rotation first real-world demo result analysis
- **CP3**: tool articulation demo entry (phase 2; 5-tool evaluation set)
- **CP4**: hardware transition (Sharpa → xhand → in-house)
- **CP5**: cross-object generalization phase entry

**CP2 prerequisite**: System0 tactile sim2real protocol verified (Chen et al. 2024 lineage) + static friction range estimation completed (full-doc P3 scope).

---

## 4. Decision Log — P1 (D1–D7) [LIVING] [AGENT-INPUT]

Options / v1 / rationale / deferred (trigger + checkpoint). Append-only.

> P1 covers **D1–D7**. P2 (D8–D12), P3/System0 (D13–D18), P4 (D19–D23),
> P5 (D24–D26) are out of scope here — see `research_context.md`.

#### [D1] Split form (P1)
- **Options**: (i) explicit BodyExpert–HandExpert separation, (ii) single ActionExpert with shared representation + body-specific + hand-specific latent, (iii) hybrid (shared trunk, split heads)
- **v1**: (iii) hybrid — shared trunk + split body/hand heads
- **Rationale**: cleanest isolation of the split contribution at CP1 while reusing π's shared representation; (i)/(ii) become the ablation comparison group
- **Deferred**: (i) fully separate → trigger: shared-trunk body↔hand gradient interference / **CP1**; (ii) latent-only → trigger: explicit split underperforms latent separation on contact metrics / **CP1**

#### [D2] Body output space (P1)
- **Options**: (a) both-wrist / tool-flange pose (Cartesian), (b) joint-space minus wrist, (c) delta Cartesian, (d) split
- **v1**: (a) both-wrist / tool-flange pose
- **Rationale**: embodiment-transfer easing; flange pose decouples Body expert from arm kinematics (joint-space is the comparison group)
- **Deferred**: (b) joint-space → trigger: flange-pose Body unstable vs joint-space ("Demystifying Action Space Design": joint=stability, task=generalization) / **CP1**; (c) delta Cartesian → trigger: absolute-pose learnability poor / **CP1**

#### [D3] Hand output space (P1)
- **Options**: (i) finger joint command, (ii) fingertip pose, (iii) grip-force / impedance, (iv) hybrid
- **v1**: (i) finger joint command
- **Rationale**: directest tactile/proprioceptive-feedback-grounded precision; matches Sharpa joint interface
- **Deferred**: (iii) impedance → trigger: stiff position control causes excessive contact force / **CP2**

#### [D4] Body↔Hand information sharing (P1)
- **Options (mechanism)**: (A) shared latent, (B) cross-attention, (C) mutual conditioning, (D) routing/gating, (E) action/history sharing, (F) FiLM
- **Options (what flows)**: (i) $a_b$ only, (ii) body hidden state, (iii) both
- **v1**: (F) FiLM with $a_b$ → ($\gamma,\beta$) modulating hand head input, single point
- **Rationale**: MLP-style hand head + minimum delta + sufficient first-experiment expressivity
- **Deferred**: (B) cross-attention → trigger: FiLM bottleneck OR hand head → transformer (cf. LaMP gated cross-attn, TwinBrainVLA AsyMoT) / **CP1**; (ii) hidden-state → trigger: D6 v2 / **CP1**; multi-layer depth → trigger: single-point info bottleneck (cf. MolmoAct2 per-layer KV) / **CP1**

#### [D5] Input-modality + control-rate separation (P1)
- **Options (modality)**: (i) shared, (ii) Body={vision, language, proprio, task} / Hand={tactile, proprio, local visual, VLA intent}, (iii) partial
- **Options (rate)**: (α) shared rate, (β) separated (time-positional encoding / action timestamp embedding / async conditioning)
- **v1**: (ii) modality-separated + (α) shared rate
- **Rationale**: modality separation identity-aligned (hand=contact); shared rate = minimum delta for first experiment
- **Deferred**: (β) rate separation → trigger: finger precision needs higher-frequency loop than body / **CP2**

#### [D6] Coordination direction & flow (P1)
- **Options**: body→hand / hand→body / iterative / bidirectional; flow = (a) hierarchical (body K-step → $a_b$ → hand conditioned), (b) coupled denoising, (c) coupled single net, (d) independent
- **v1**: body→hand, (a) hierarchical flow
- **Rationale**: literal sequential conditioning; clean interface; training stability
- **Deferred**: iterative/bidirectional + (b) coupled → trigger: slip fails to reshape arm motion in time / **CP1+CP2**; (c) single net → trigger: latency budget pressure / **CP3**

#### [D7] π backbone integration / partition (P1)
- **Options**: (i) slice π0 action expert + FT both sides, (ii) repurpose π expert as Hand + add new Body, (iii) both re-init, (iv) distillation from monolithic π
- **v1**: (i) slice partition + FT
- **Rationale**: maximally preserves π manipulation prior; cleanest split-vs-monolithic baseline. Sub-reading **Repurpose vs Subdivide** unresolved → §9.B, decide at CP1 code entry
- **Deferred**: (ii) repurpose → trigger: Body re-init acceptable / **CP4**; (iv) distillation → trigger: π surgery overhead prohibitive / **CP1**
- **Note**: tightly coupled to full-doc P4 (D19 freeze strategy) — VLM prior preservation

---

## 5. P1 Anti-topics (Noise Filter) [AGENT-INPUT]

Excluded from the weekly digest unless an unusually strong tie to P1 or a P1 Decision (D1–D7):

- Monolithic VLA decoders without an arm-hand split
- Post-hoc correction/residual on a frozen VLA that does not address the distribution-bound limitation
- Router-based MoE for action selection (different pattern; DexReMoE monitoring is the exception — §8)
- Flat-concat multimodal fusion presented as a decoder contribution (structured binding is P2, full doc)
- VLA papers without (a) arm-hand split / heterogeneous experts, (b) a learned low-level expert, or (c) backbone-preservation-aware action decoding (pick-and-place-only excluded)

---

## 6. P1 Tracked Literature [LIVING] [AGENT-INPUT]

> Hard cap 8 pinned. Rebalance quarterly; replace, don't append.
> **Format rule**: every entry carries `[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX)` (DOI/official URL if no preprint; `[no public link]` if neither). Never fabricate arXiv IDs. Canonical: `docs/STYLE_GUIDE.md` §3.

### 6.1 P1 Pinned — Heterogeneous Body/Hand Action Expert
| Paper | arXiv | Year | Role |
|---|---|---|---|
| π0 (Physical Intelligence) | [arXiv:2410.24164](https://arxiv.org/abs/2410.24164) | 2024 | Backbone (D7); flow-matching action expert |
| π0.5 | [arXiv:2504.16054](https://arxiv.org/abs/2504.16054) | 2025 | Hierarchical inference variant; D6 reference |
| TwinBrainVLA | [arXiv:2601.14133](https://arxiv.org/abs/2601.14133) | 2026 | AsyMoT frozen generalist + trainable specialist; D4/D7 closest analog |
| DexterityGen (Yin et al.) | [arXiv:2502.04307](https://arxiv.org/abs/2502.04307) | 2025 | Bounded coarse→fine precedent (D6); antagonist evidence |
| LaMP | [arXiv:2603.25399](https://arxiv.org/abs/2603.25399) | 2026 | Dual-expert gated cross-attention (D4 deferred) |
| HEX | [arXiv:2604.07993](https://arxiv.org/abs/2604.07993) | 2026 | MoE + residual-gated cross-embodiment decoder (D4) |
| RLDX-1 | [arXiv:2605.03269](https://arxiv.org/abs/2605.03269) | 2026 | Multi-Stream Action Transformer; cross-modal joint self-attn (D4) |
| Demystifying Action Space Design | [arXiv:2602.23408](https://arxiv.org/abs/2602.23408) | 2026 | 13k+ real rollouts; joint=stability/task=generalization (D2 evidence) |

**Methodology base (non-pinned)**
| Paper | arXiv | Relevance |
|---|---|---|
| FiLM (Perez et al. 2018) | [arXiv:1709.07871](https://arxiv.org/abs/1709.07871) | Conditioning-layer building block (D4) |
| PCGrad (Yu et al. 2020) | [arXiv:2001.06782](https://arxiv.org/abs/2001.06782) | Gradient-conflict mitigation (D1 deferred) |
| DQ-RISE | [arXiv:2605.03363](https://arxiv.org/abs/2605.03363) | Arm-hand action-space decoupling (D1/D3) |
| MolmoAct2 | [arXiv:2605.02881](https://arxiv.org/abs/2605.02881) | Per-layer KV-cache conditioning (D4 multi-layer deferred) |

---

## 7. P1 Researchers & Groups to Follow [LIVING]

> Ordered by proximity to the P1 anchor (heterogeneous Body/Hand decoder).

### 7.1 Individuals
- **Physical Intelligence π team** — Kevin Black, Danny Driess, Karl Pertsch, Lucy Xiaoyang Shi, Allen Z. Ren — backbone + flow-matching action expert (π0/π0.5)
- **Cewu Lu, Lixin Yang (SJTU MVIG / RISE)** — DQ-RISE arm-hand action-space decoupling; LaMP dual-expert — closest to P1 split
- **Zhao-Heng Yin (Berkeley)** — DexterityGen, coarse→fine (D6)
- **Toru Lin (Berkeley)** — dexterous sim-to-real
- **Haozhi Qi (Berkeley/Meta)** — HORA, in-hand rotation
- **TwinBrainVLA authors** — AsyMoT (verify)

### 7.2 Labs / groups (watch code releases)
- **Physical Intelligence (π team)** — backbone, action-expert pattern
- **SJTU MVIG / RISE (Cewu Lu)** — dual-expert + arm-hand decoupling (LaMP, DQ-RISE)
- **Berkeley BAIR / RAIL** — DexterityGen; in-hand dexterity
- **Meta FAIR Robotics** — π-team overlap

---

## 8. P1 Competitor / Kindred Monitoring [LIVING] [AGENT-INPUT]

Architectural siblings of the P1 Body/Hand split — review at every CP, ordered by closeness.

| Work | arXiv | Overlap | Difference vs P1 | Watch trigger |
|---|---|---|---|---|
| **TwinBrainVLA** | [2601.14133](https://arxiv.org/abs/2601.14133) | Frozen generalist + trainable specialist (AsyMoT) | Specialist not anatomically Body/Hand split | CP1 architecture comparison; real-robot validation |
| **LaMP** | [2603.25399](https://arxiv.org/abs/2603.25399) | Two-expert decoder + gated cross-attn | Split axis = scene-flow, not anatomical | CP1 comparison; OOD numbers |
| **HEX** | [2604.07993](https://arxiv.org/abs/2604.07993) | Expert decomposition + residual-gated fusion | Embodiment-routing vs anatomical split | CP1 code release |
| **DexReMoE** | [2508.01695](https://arxiv.org/abs/2508.01695) | Explicit expert decomposition for dexterity | Object-conditioned routing vs anatomical split | CP1 result race; CP5 cross-object |

*Differentiation hypothesis*: VLA-level anatomical Body/Hand split + structured binding wins on **contact-precision**; routing/motion-prior/correction approaches win on **object/embodiment generalization** but are distribution-bounded on contact precision.

---

## 9. P1 Open Items & Architectural Sub-Unclarity [LIVING] [AGENT-INPUT]

### 9.A — Open implementation decisions

> Resolved: π weights public via openpi (π0, π0.5, π0-FAST, Apache 2.0; PyTorch port + open-pi-zero re-impl).

| Item | Status | Default if unresolved | Deadline |
|---|---|---|---|
| π variant (π0 / π0.5 / π0.7) | 🟡 open | π0 (most stable) | CP1 code start |
| Code base (JAX openpi / HF PyTorch / open-pi-zero) | 🟡 open | PyTorch port | CP1 code start |
| Compute budget — GPU mem for D7 slice + FT | 🟡 unknown | Smaller env-count fallback | Before CP1 exec |

### 9.B — Architectural sub-unclarity (D7 / P1 core)

> Maps to §14.C in the full `research_context.md`.

π0 is *already* MoT (PaliGemma 2.291B VLM + action expert 0.315B). D7 (i) "slice partition + FT" admits two readings:

| Reading | Content | Trade-off |
|---|---|---|
| **A — Repurpose** | π0 action expert as Hand; *add* new Body | Minimal π disruption; Body random-init loses prior |
| **B — Subdivide** | *Slice* π0 action expert into Body/Hand | Preserves prior both sides; needs slice-boundary + capacity decision |

→ Sub-readings of D7 v1; decide at CP1 code-writing entry (explicit acknowledgment, no hard commit now). open-pi-zero = parameter-level reference. **TwinBrainVLA AsyMoT + LaMP gated cross-attention are concrete references for the body→hand information-sharing module (D4).**

---

*P1 scope extract of `research_context.md`. For P2–P5, decisions D8–D26,
full §7 anti-topics, §9 researchers, §10 monitoring, §14 dependency graph,
and Appendix C, consult the full document.*
