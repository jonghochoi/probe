# Research Context — P1: Heterogeneous Action Decoder

> **Derived from `research_context.md` v4.0 (2026-05-12) — P1 scope only.**
> This is a narrowed extract focused solely on **Pillar 1 (Heterogeneous Action
> Decoder)**. The full multi-pillar document `research_context.md` remains the
> single source of truth; P2–P5 content lives there, not here.
> **Agent usage**: This is *static* context. The retrieval agent reads (never
> writes) this file. Weekly findings go to `research_log/YYYY-WW.md`.
> **Formatting & translation rules**: see `docs/STYLE_GUIDE.md` (single source of
> truth — agent must read it before producing output).

---

## 1. Identity [STABLE] [AGENT-INPUT]

> Most VLA-style policies attempt to converge on dexterity via a **monolithic action decoder + vision-dominant observation**. I argue that **an arm-hand anatomically heterogeneous decoder (both experts directly designed and trained) + hand-level contact-grounded supervision/observation** is what determines the ceiling of dexterity. Task specification stays goal-centric (arm-hand integrated); on top of the upstream context supplied by body and backbone (grasp intent, visual embedding, task intent), the hand's internal language of control, loss, and observation is elevated toward contact.

**Decomposition**
- *Antagonist*: monolithic VLA decoders + vision-dominant observation
- *Protagonist*: anatomically heterogeneous decoder + hand-level contact elevation
- *Stays goal-centric*: task specification (arm-hand integrated)
- *Elevated to contact*: hand's internal control / loss / observation language
- *Upstream context source*: body (grasp intent, arm action) + backbone (visual embedding, task intent) — pretrained anchoring optional, not required

> **Note**: The heterogeneous-decoder half of this identity is what P1 owns. The
> contact-grounded supervision/observation half (hand-level elevation) is carried
> by P2/P3 in the full document and is intentionally out of scope here.

---

## 2. Pillar P1 — Heterogeneous Action Decoder [STABLE structure, LIVING content] [AGENT-INPUT]

**Scope**: body/hand decoder split, information-sharing module, π backbone integration. The architectural core of identity.

**Identity tie**: heterogeneous decoder claim → this pillar.

**Tracked items**: sequential direction (D1), wrist boundary (D2), action expert partition (D3), tactile fusion (D4), backbone freeze (D5), proprioception split (D6), flow matching coordination (D7), sharing module mechanism (D8), gradient conflict mitigation (D9).

**Anti-topics**: monolithic VLA decoders without split, router-based MoE (different pattern), multi-expert ablations without single-expert comparison.

**Literature anchor**: π0/π0.5 (backbone); DexterityGen, RLDX-1, Shared-Autonomy Arm-Hand VLA, TacFiLM (FiLM fusion), CoDA, π_RL. See §6.

---

## 3. Revisit Checkpoints (CP1–CP5) [LIVING]

Reusable temporal anchors. Most deferred P1 decisions trigger at one of these.

- **CP1**: v1 first ablation analysis (split vs monolithic on in-hand rotation, sim)
- **CP2**: in-hand rotation first real-world demo result analysis
- **CP3**: tool articulation demo entry (phase 2; 5-tool evaluation set)
- **CP4**: hardware transition (Sharpa → xhand → in-house)
- **CP5**: cross-object generalization phase entry

**CP2 prerequisite**: tactile sim2real protocol verified (Chen et al. 2024 lineage) + static friction range estimation completed. Without these, CP2 entry is premature.

---

## 4. Decision Log — P1 (D1–D9) [LIVING] [AGENT-INPUT]

All architectural commits recorded with: options considered, v1 choice, rationale, deferred candidates with revisit triggers and checkpoints. Append-only. Decisions are *first-attempt defaults*.

> P1 covers D1–D9. D10 (P2), D11 (P3), D12 (P4), D13 (P5), D14, D15 are out of
> scope for this file — see `research_context.md`.

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
- **Note**: §9.B documents the unresolved sub-reading (Repurpose vs Subdivide) that must be decided at CP1 code entry.

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
- **Cross-ref**: tightly connected to P3 (hand reward magnitude affects loss balance) — see full doc D11.
- **Falsifier caveat**: if conflict is severe, evidence for "split > monolithic" depends on which mitigation restores performance — must be reported explicitly

---

## 5. P1 Anti-topics (Noise Filter) [AGENT-INPUT]

Papers matching these are excluded from the weekly digest unless they have an unusually strong tie to P1 or a P1 Decision (D1–D9):

- Monolithic VLA decoders without an arm-hand split
- Router-based MoE for action selection (different architectural pattern from anatomical split; out of scope unless explicitly contrasting — DexReMoE monitoring is the exception, see §8)
- Multi-expert ablations without a single-expert (monolithic) comparison baseline
- VLA papers without (a) a low-level dexterous control component, (b) a bridge/residual architecture with an RL expert, or (c) tactile/force modality injection (pick-and-place-only excluded)

---

## 6. P1 Tracked Literature [LIVING] [AGENT-INPUT]

> Hard cap 8 pinned. Rebalance quarterly; replace, don't append.
> **Format rule**: every paper entry must carry an arXiv ID and a Markdown
> hyperlink `[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX)` (DOI/official
> URL if no preprint; `[no public link]` if neither). Canonical source:
> `docs/STYLE_GUIDE.md` §3.

### 6.1 P1 Pinned — Heterogeneous Action Decoder
| Paper | arXiv | Year | Role |
|---|---|---|---|
| π0 (Physical Intelligence) | [arXiv:2410.24164](https://arxiv.org/abs/2410.24164) | 2024 | Backbone (D3, D5 anchor); flow matching VLA, action expert pattern |
| π0.5 | [arXiv:2504.16054](https://arxiv.org/abs/2504.16054) | 2025 | Hierarchical inference variant; D7 reference |
| DexterityGen (Yin et al., Berkeley/Meta FAIR) | [arXiv:2502.04307](https://arxiv.org/abs/2502.04307) | 2025 | Coarse→fine control precedent (D1 reference) |
| RLDX-1 (Technical Report) | [arXiv:2605.03269](https://arxiv.org/abs/2605.03269) | 2026 | Multi-Stream Action Transformer; cross-modal joint self-attention heterogeneous decoder (D8 anchor) |
| Shared-Autonomy Arm-Hand VLA | [arXiv:2511.00139](https://arxiv.org/abs/2511.00139) | 2025 | Late tactile fusion precedent (D4) |
| TacFiLM | [arXiv:2603.14604](https://arxiv.org/abs/2603.14604) | 2026 | FiLM tactile fusion VLA (D8 anchor) |
| CoDA | [arXiv:2505.21437](https://arxiv.org/abs/2505.21437) | 2025 | Coordinated diffusion noise optimization; body+hand specialized diffusion (D1, D3) |
| π_RL | [arXiv:2510.25889](https://arxiv.org/abs/2510.25889) | 2025 | Online RL fine-tuning for flow-based VLA (D3/D5/D7) |

**Methodology base (non-pinned)**
| Paper | arXiv | Relevance |
|---|---|---|
| FiLM: Visual Reasoning with a General Conditioning Layer (Perez et al. 2018) | [arXiv:1709.07871](https://arxiv.org/abs/1709.07871) | Feature-wise linear modulation; conditioning-layer building block underlying TacFiLM (D8 anchor) |
| Gradient Surgery for Multi-Task Learning / PCGrad (Yu et al. 2020) | [arXiv:2001.06782](https://arxiv.org/abs/2001.06782) | Conflict-free multi-objective gradient projection (D9, deferred) |
| DeMUSE | [arXiv:2602.19764](https://arxiv.org/abs/2602.19764) | Auxiliary reference (abstract unverified) |
| HEX: Humanoid-Aligned Experts for Cross-Embodiment Whole-Body Manipulation | [arXiv:2604.07993](https://arxiv.org/abs/2604.07993) | MoE + residual-gated fusion, cross-embodiment whole-body decoder; D8 pinned candidate, reinforces RLDX-1 |
| Learning Reactive Dexterous Grasping via Hierarchical Task-Space RL Planning and Joint-Space QP Control | [arXiv:2509.17450](https://arxiv.org/abs/2509.17450) | Multi-agent RL (separate arm/hand agents) high-level task-space planner + GPU-parallel QP joint controller; high-level intent vs low-level execution split (D1 candidate, arm/hand split) |
| DQ-RISE: Learning Dexterous Manipulation with Quantized Hand State | [arXiv:2605.03363](https://arxiv.org/abs/2605.03363) | Quantized hand state + continuous relaxation so arm actions diffuse jointly with compact hand states; arm-hand coupled action-space decoupling and coordination (D1, D3) |
| LaMP: Learning Vision-Language-Action Policies with 3D Scene Flow as Latent Motion Prior | [arXiv:2603.25399](https://arxiv.org/abs/2603.25399) | Dual-expert: flow-matching Motion Expert + policy Action Expert via gated cross-attention; 3D scene flow latent motion prior (D8 dual-expert decoder, D3/D5; reinforces RLDX-1/HEX) |

---

## 7. P1 Researchers & Groups to Follow [LIVING]

> Ordered by proximity to the P1 anchor (heterogeneous arm-hand decoder).

### 7.1 Individuals
- **Physical Intelligence π team** — Kevin Black, Danny Driess, Karl Pertsch, Lucy Xiaoyang Shi, Allen Z. Ren — backbone + flow-matching action expert (π0/π0.5); π_RL RL-finetune lineage
- **Cewu Lu, Lixin Yang (SJTU MVIG / RISE)** — DQ-RISE arm-hand action-space decoupling; LaMP dual-expert (Motion/Action) — closest to P1 split philosophy
- **Zhao-Heng Yin (Berkeley)** — DexterityGen, coarse→fine control (D1)
- **Taku Komura (HKU)** — CoDA whole-body coordinated diffusion (D1/D3)
- **Toru Lin (Berkeley)** — dexterous sim-to-real
- **Haozhi Qi (Berkeley/Meta)** — HORA, in-hand rotation

### 7.2 Labs / groups (watch code releases)
- **Physical Intelligence (π team)** — backbone, action-expert pattern, RL finetune
- **SJTU MVIG / RISE (Cewu Lu)** — dual-expert + arm-hand decoupling (LaMP, DQ-RISE)
- **Berkeley BAIR / RAIL** — DexterityGen; in-hand RL; RMA/A-RMA/DR origin
- **Meta FAIR Robotics** — TacFiLM; π-team overlap

---

## 8. P1 Competitor / Kindred Monitoring [LIVING] [AGENT-INPUT]

Architectural siblings of the P1 arm-hand split — review at every CP, ordered by closeness.

| Work | arXiv | Overlap | Difference vs P1 | Watch trigger |
|---|---|---|---|---|
| **LaMP** | [2603.25399](https://arxiv.org/abs/2603.25399) | Explicit two-expert decoder (Motion + Action) joined by gated cross-attention | Split axis = scene-flow motion prior, **not** anatomical arm/hand | CP1 architecture comparison; OOD robustness numbers |
| **HEX** | [2604.07993](https://arxiv.org/abs/2604.07993) | Expert decomposition + residual-gated fusion | Embodiment-routing vs anatomical split | CP1 code release; cross-embodiment claims |
| **DexReMoE** | [2508.01695](https://arxiv.org/abs/2508.01695) | Explicit expert decomposition for dexterity | Object-conditioned routing vs anatomical split | CP1 result race; CP5 cross-object comparison |

*Differentiation hypothesis*: anatomical split + contact-grounded supervision wins on **contact-precision** metrics; routing/motion-prior approaches win on **object/embodiment generalization**.

---

## 9. P1 Open Items & Architectural Sub-Unclarity [LIVING] [AGENT-INPUT]

### 9.A — Open implementation decisions

> Resolved: π weights public via openpi (π0, π0.5, π0-FAST, Apache 2.0; PyTorch port + open-pi-zero re-impl).

| Item | Status | Default if unresolved | Deadline |
|---|---|---|---|
| π variant (π0 / π0.5 / π0.7) | 🟡 open | π0 (most stable) | CP1 code start |
| Code base (JAX openpi / HF PyTorch port / open-pi-zero) | 🟡 open | PyTorch port (Isaac Lab + active community) | CP1 code start |
| Compute budget — GPU mem for D3 (i) slice partition + FT × 8k–16k env | 🟡 unknown | Fallback 2k–4k env (sample-budget trade-off) | Before CP1 exec |
| Sample budget per condition | 🟡 unknown | HORA precedent ~few×10⁸ steps | CP1 monitoring |
| π0.7 weight release | 🟡 unknown | Start π0/π0.5; π0.7 = CP3+ migration candidate | Recheck CP1 |

### 9.B — Architectural sub-unclarity (D3 / P1 core)

> Maps to §9.C in the full `research_context.md` (full-doc §9.B is non-P1, out of scope here).

π0 is *already* MoT (PaliGemma 2.291B VLM + action expert 0.315B). D3 (i) "slice partition + FT" admits two readings:

| Reading | Content | Trade-off |
|---|---|---|
| **A — Repurpose** | π0 action expert (0.315B) as hand expert; *add* new body expert | Minimal π disruption; body expert random init loses π prior |
| **B — Subdivide** | *Slice* π0 action expert internally into body / hand | Preserves π prior both sides; needs slice-boundary + capacity decision |

→ Sub-readings of D3 v1; decide at CP1 code-writing entry (explicit acknowledgment, no hard commit now). open-pi-zero useful as parameter-level reference. **LaMP's gated cross-attention Motion→Action conditioning is a concrete reference for the body→hand information-sharing module.**

---

*P1 scope extract of `research_context.md` v4.0. For P2–P5, decisions D10–D15,
full §7 anti-topics, §9 researchers, §10 monitoring, §13–14 dependency graph,
and Appendix C, consult the full document.*
