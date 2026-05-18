# P1 Synthesis Brief — Heterogeneous Action Decoder

재생성일: 2026-05-18 · 출처: `research_context_P1.md` v4.0 (2026-05-12) — P1 scope only

---

## D1 — Sequential conditioning direction (순차 조건화 방향)

D1의 v1 선택은 body→hand 단방향 순차 조건화이며, DexterityGen ([arXiv:2502.04307](https://arxiv.org/abs/2502.04307), D1 reference)의 coarse→fine 제어 선례와 CoDA ([arXiv:2505.21437](https://arxiv.org/abs/2505.21437), D1·D3)의 body+hand 특화 확산 구조가 이를 뒷받침합니다. 그러나 CoDA의 coordinated diffusion은 body→hand 경계를 단일 방향으로 고정하지 않으며, methodology base에 있는 DQ-RISE의 coupled action-space 접근은 순차 가정 자체에 압력을 가합니다. CP1·CP2에서 슬립 감지(slip detection)가 팔 동작을 제때 재형성하지 못할 경우, iterative/bidirectional 방향으로 전환이 트리거됩니다.

## D2 — Wrist boundary (손목 경계)

D2를 직접 떠받치는 핀 논문은 없으며, v1 선택인 B-1(wrist→hand, body=joint-space minus wrist)은 π reuse와 P3 접촉 기반 감독(contact-grounded supervision) 하에서 손목을 hand 측에 귀속시키는 것이 가장 자연스럽다는 판단에만 근거합니다. B-2(Cartesian body) 전환은 CP4+CP5 하드웨어 이전 또는 cross-arm 일반화 필요 시 트리거되며, A(wrist→body) 전환은 CP3 첫 데모가 pick-and-place형으로 퇴행하는 경우에 해당합니다.

## D3 — Action expert partition (행동 전문가 분할)

D3의 v1 선택은 (i) slice partition + FT(양측 fine-tuning)이며, π0 ([arXiv:2410.24164](https://arxiv.org/abs/2410.24164), D3·D5 anchor)의 action expert 패턴이 분할 baseline의 직접적 근거이고, π_RL ([arXiv:2510.25889](https://arxiv.org/abs/2510.25889), D3·D5·D7)과 CoDA ([arXiv:2505.21437](https://arxiv.org/abs/2505.21437), D1·D3)가 이를 보강합니다. 핵심 미결 사항은 §9.B의 Repurpose(π0 action expert를 hand expert로 전용 + body expert 신규 초기화) vs Subdivide(π0 action expert를 내부적으로 분할) sub-reading이며, CP1 코드 작성 진입 시 명시적 결정이 요구됩니다. 이 선택이 body expert의 π prior 보존 여부를 결정하므로, split-vs-monolithic 비교의 해석 가능성에 직접 영향을 미칩니다.

## D4 — Tactile fusion strategy (촉각 융합 전략)

D4의 v1 선택은 late fusion(hand head only)이며, Shared-Autonomy Arm-Hand VLA ([arXiv:2511.00139](https://arxiv.org/abs/2511.00139), D4)의 late tactile fusion 선례가 주요 근거입니다. 한편 TacFiLM ([arXiv:2603.14604](https://arxiv.org/abs/2603.14604), D8 anchor)은 FiLM 기반 촉각 융합을 VLA 전체에 적용하는 방향을 보여주어, late-only 가정에 간접적 압력을 가합니다. CP1에서 vision-dominance 또는 tactile underweighting이 관찰되면 both(early+late) 전환이 트리거됩니다.

## D5 — Backbone freeze strategy (백본 동결 전략)

D5의 v1 선택은 (a) full freeze이며, π0 ([arXiv:2410.24164](https://arxiv.org/abs/2410.24164), D3·D5 anchor)의 훈련된 모달리티만 백본에 입력되는 구조와 D4 late fusion 결정이 어댑테이션 압력을 제거한다는 논리에 근거합니다. π_RL ([arXiv:2510.25889](https://arxiv.org/abs/2510.25889), D3·D5·D7)은 flow-based VLA의 온라인 RL fine-tuning을 보여주어 장기적으로 완전 동결 가정에 간접적 압력이 됩니다. 새로운 모달리티 조합에서 백본 표현이 불충분할 경우 LoRA 전환이 CP1에서 트리거됩니다.

## D6 — Proprioception split (고유감각 분할)

D6를 직접 떠받치는 핀 논문은 없으며, v1 선택인 (i) unified prop encoder는 π reuse 직접성과 minimum delta 원칙에만 근거합니다. 손가락 수준의 협조(finger-level coordination)가 백본 정보 흐름에 의해 병목에 걸리는 것이 CP2(in-hand rotation) 실험에서 관찰될 경우, (iii) hand-prop direct injection으로 전환이 트리거됩니다.

## D7 — Flow matching coordination (플로우 매칭 협조)

D7의 v1 선택은 (d) hierarchical flow(body가 $K$-step denoising 완료 → $a_b$ → hand가 $a_b$에 조건화되어 denoising)이며, π0.5 ([arXiv:2504.16054](https://arxiv.org/abs/2504.16054), D7 reference)의 hierarchical inference 구조와 π_RL ([arXiv:2510.25889](https://arxiv.org/abs/2510.25889), D3·D5·D7)이 이를 뒷받침합니다. D1이 iterative/bidirectional로 전환될 경우 coupled denoising (a)로, latency budget 압박 시 coupled flow (c)로 경로가 분기됩니다. D7은 D1과 동일한 순차 가정을 공유하므로 CP1+CP2 결과가 두 결정을 동시에 뒤집는 트리거가 될 수 있습니다.

## D8 — Sharing module mechanism (공유 모듈 메커니즘)

D8의 v1 선택은 (B) FiLM with $a_b$ → ($\gamma$, $\beta$) modulating hand head input at (α) single point이며, TacFiLM ([arXiv:2603.14604](https://arxiv.org/abs/2603.14604), D8 anchor)의 FiLM 조건화 VLA 구조와 methodology base인 FiLM 원론([arXiv:1709.07871](https://arxiv.org/abs/1709.07871))이 직접 근거입니다. RLDX-1 ([arXiv:2605.03269](https://arxiv.org/abs/2605.03269), D8 anchor)의 cross-modal joint self-attention은 hand head가 MLP에서 transformer로 재구성될 경우 (C) cross-attention이 기본값이 되어야 한다는 경쟁 방향을 제시합니다. CP1에서 FiLM bottleneck 또는 hand의 body conditioning 미활용이 확인되면 (C) 또는 (β) multi-layer로 전환이 트리거됩니다.

## D9 — Gradient conflict mitigation (경사 충돌 완화)

D9의 v1 선택은 (A) vanilla weighted sum($w_b = w_h = 1$) + cosine similarity 모니터링이며, D3(i)으로 body head가 얇아 conflict capacity가 제한적이라는 구조적 논리에 근거합니다. D9를 직접 떠받치는 핀 논문은 없으며, PCGrad ([arXiv:2001.06782](https://arxiv.org/abs/2001.06782))는 methodology base(비핀)로만 등록되어 있어, conflict 발생 시 즉각 대응할 문헌 기반이 상대적으로 취약합니다. cosine similarity가 지속적으로 음수이거나 훈련이 불안정할 경우 CP1에서 PCGrad/GradNorm으로 전환되며, D11(P3) hand reward magnitude가 loss balance에 직접 영향을 미치므로 P3와의 cross-pillar 협조가 필요합니다.

---

## 지금 머릿속에 들고 있어야 할 것

- π0 reuse 가정이 D3·D5·D6·D7의 v1 선택을 동시에 고정하고 있어, §9.B의 Repurpose vs Subdivide 결정이 전체 P1 아키텍처의 코드 진입 선행 조건입니다.
- D1(body→hand 순차)과 D7(hierarchical flow)은 동일한 순차 가정을 공유하므로, CP1+CP2의 slip detection 실패가 두 결정을 동시에 뒤집는 단일 트리거가 됩니다.
- D8 FiLM single-point conditioning vs RLDX-1의 cross-modal joint self-attention 대립이 현재 아키텍처에서 가장 날카로운 미결 긴장점이며, CP1 ablation이 이를 가를 핵심 실험입니다.
- D2(wrist boundary)와 D6(proprioception split)를 직접 뒷받침하는 핀 논문이 없으며, 두 결정은 π reuse 및 P3 contact-supervision 가정에만 의존합니다 — 분기별 풀 리뷰 시 핀 논문 보강 여부를 검토해야 합니다.
- 단일 신규 논문이 그림을 움직이려면, anatomical arm-hand split + FiLM/cross-attention 공유 모듈 구성에서 split-vs-monolithic 비교를 실제 로봇 contact-precision 지표로 보여 주어야 합니다.
