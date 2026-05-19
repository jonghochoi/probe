# P1 Synthesis Brief — Heterogeneous Body/Hand Action Expert

재생성일: 2026-05-19 · P1 scope extract of `research_context.md`

---

## D1 — Split form (P1)

D1의 v1 선택은 (iii) hybrid(shared trunk + split body/hand heads)이며, π의 공유 표현을 재사용하면서 CP1에서 split 기여를 가장 깨끗하게 격리한다는 논리에 근거합니다. D1을 직접 떠받치는 §6 핀 논문은 없으며, methodology base의 DQ-RISE([arXiv:2605.03363](https://arxiv.org/abs/2605.03363), D1/D3 arm-hand action-space decoupling)가 분할 자체에 간접 근거를 제공할 뿐 v1은 π reuse 가정에만 의존합니다. shared-trunk에서 body↔hand 경사 간섭이 관찰되면 (i) 완전 분리로의 전환이 CP1에서 트리거되며, 대응 문헌인 PCGrad([arXiv:2001.06782](https://arxiv.org/abs/2001.06782), D1 deferred)는 비핀 methodology base로만 등록되어 있어 즉응 기반이 상대적으로 취약합니다.

## D2 — Body output space (P1)

D2의 v1 선택은 (a) both-wrist / tool-flange pose이며, flange pose가 Body expert를 arm kinematics에서 분리해 embodiment-transfer를 용이하게 한다는 근거입니다(joint-space는 비교군). 이 결정을 직접 떠받치는 핀 논문은 없으며, 오히려 §6의 Demystifying Action Space Design([arXiv:2602.23408](https://arxiv.org/abs/2602.23408), D2 evidence)이 joint=stability / task=generalization를 보여 (b) joint-space 비교군 쪽에 무게를 실어 v1과 긴장 관계에 있습니다. flange-pose Body가 joint-space 대비 불안정하면 (b)로의 전환이 CP1에서 트리거됩니다.

## D3 — Hand output space (P1)

D3의 v1 선택은 (i) finger joint command이며, tactile/proprioceptive-feedback에 가장 직접적으로 grounding되는 정밀도이자 Sharpa joint 인터페이스와 합치한다는 근거입니다. D3를 직접 떠받치는 §6 핀 논문은 없으며, methodology base의 DQ-RISE([arXiv:2605.03363](https://arxiv.org/abs/2605.03363), D1/D3)가 arm-hand 행동공간 분리 맥락에서만 인접합니다. position 제어의 과도 접촉력이 관찰되면 (iii) impedance로의 전환이 CP2에서 트리거됩니다.

## D4 — Body↔Hand information sharing (P1)

D4의 v1 선택은 (F) FiLM($a_b$ → ($\gamma,\beta$)로 hand head 입력을 single point에서 변조)이며, methodology base의 FiLM 원론([arXiv:1709.07871](https://arxiv.org/abs/1709.07871), D4)이 직접 building block 근거이고 MLP형 hand head + minimum delta 원칙이 이를 보강합니다. 이 결정을 가장 강하게 흔드는 것은 cross-attention/다층 경쟁군으로, LaMP([arXiv:2603.25399](https://arxiv.org/abs/2603.25399), D4 deferred dual-expert gated cross-attention), TwinBrainVLA([arXiv:2601.14133](https://arxiv.org/abs/2601.14133), D4/D7 AsyMoT), HEX([arXiv:2604.07993](https://arxiv.org/abs/2604.07993), D4 residual-gated), RLDX-1([arXiv:2605.03269](https://arxiv.org/abs/2605.03269), D4 cross-modal joint self-attn), 그리고 다층 깊이 측면의 MolmoAct2([arXiv:2605.02881](https://arxiv.org/abs/2605.02881), D4 multi-layer deferred)가 single-point bottleneck 시 CP1에서 (B) 또는 multi-layer 전환을 점등시킵니다.

## D5 — Input-modality + control-rate separation (P1)

D5의 v1 선택은 (ii) modality-separated(Body={vision, language, proprio, task} / Hand={tactile, proprio, local visual, VLA intent}) + (α) shared rate이며, modality 분리는 hand=contact라는 identity와 정합하고 shared rate는 첫 실험의 minimum delta라는 근거입니다. D5를 직접 떠받치거나 흔드는 §6 핀 논문은 없으며, 결정은 identity 정합성과 minimum-delta 원칙에만 의존합니다. finger 정밀도가 body보다 높은 주파수 루프를 요구하면 (β) rate separation으로의 전환이 CP2에서 트리거됩니다.

## D6 — Coordination direction & flow (P1)

D6의 v1 선택은 body→hand 방향 + (a) hierarchical flow(body가 $K$-step 후 $a_b$ → hand가 $a_b$에 조건화)이며, π0.5([arXiv:2504.16054](https://arxiv.org/abs/2504.16054), D6 reference)의 hierarchical inference 구조와 DexterityGen([arXiv:2502.04307](https://arxiv.org/abs/2502.04307), D6 bounded coarse→fine precedent)이 직접 근거입니다. 다만 DexterityGen은 동시에 antagonist evidence로, bounded coarse→fine이 한정적 선례임을 시사해 순차 가정 자체에 압력을 줍니다. slip이 arm motion을 제때 재형성하지 못하면 iterative/bidirectional + (b) coupled denoising으로의 전환이 CP1+CP2에서 트리거됩니다.

## D7 — π backbone integration / partition (P1)

D7의 v1 선택은 (i) slice π0 action expert + 양측 FT이며, π0([arXiv:2410.24164](https://arxiv.org/abs/2410.24164), D7 backbone; flow-matching action expert)의 action-expert 패턴이 분할 baseline의 직접 근거이고 TwinBrainVLA([arXiv:2601.14133](https://arxiv.org/abs/2601.14133), D4/D7 frozen generalist + trainable specialist)가 가장 가까운 analog로 이를 보강합니다. 핵심 미결은 §9.B의 **Repurpose vs Subdivide** sub-reading으로 CP1 코드 진입 시 명시적 결정이 요구되며, (ii) repurpose는 CP4, (iv) distillation은 CP1에서 트리거됩니다. 이 결정은 full-doc P4의 D19 freeze 전략(VLM prior 보존)과 강하게 결합되어 있으나 D19 자체는 P1 범위 밖입니다.

---

## 지금 머릿속에 들고 있어야 할 것

- π reuse 가정이 D1·D6·D7의 v1을 동시에 고정하며, D7의 Repurpose vs Subdivide(§9.B) 결정이 전체 P1 아키텍처 코드 진입의 선행 조건입니다.
- D1·D3·D5는 직접 떠받치는 §6 핀 논문이 없고 π reuse·identity 정합·minimum-delta 가정에만 의존하므로, 분기별 풀 리뷰에서 핀 보강 여부를 점검해야 합니다.
- 현재 가장 날카로운 미결 긴장점은 D4의 FiLM single-point vs cross-attention/multi-layer 경쟁군(LaMP·TwinBrainVLA·HEX·RLDX-1·MolmoAct2)이며, CP1 ablation이 이를 가릅니다.
- D2는 v1(flange pose)을 떠받치는 핀이 없고, 오히려 핀 논문 Demystifying Action Space Design이 joint-space 안정성 쪽으로 무게를 실어 비교군과의 CP1 대결이 결정적입니다.
- 단일 신규 논문이 그림을 움직이려면, anatomical Body/Hand split을 실제 로봇 contact-precision 지표에서 split-vs-monolithic으로 비교하면서 Body↔Hand 공유 메커니즘(FiLM vs cross-attention/multi-layer)을 함께 통제·측정해야 합니다.
