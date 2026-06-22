# Paper Analysis — Co-VLA: Coordination-Aware Structured Action Modeling for Dual-Arm Vision–Language–Action Systems

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Co-VLA: Coordination-Aware Structured Action Modeling for Dual-Arm Vision–Language–Action Systems |
| 저자 | Yandong Wang, Jiaqian Yu, Xiongfeng Peng, Lu Xu, Yamin Mao, Weiming Li, Jaewook Yoo, Dongwook Lee, Daehyun Ji, Mingbo Zhao, Chao Zhang (Donghua University · Samsung R&D Institute China-Beijing · Samsung AI Center DS) |
| 링크 | [arXiv:2606.20285](https://arxiv.org/abs/2606.20285) |
| 발행일 / 버전 | 2026-06-18 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-22 |
| 관련 Pillar | P1, P4, P0 |
| 태그 | vla-arch, flow-matching, dexterity |

---

## 🧭 한 줄 요약 (TL;DR)

양팔(bimanual) VLA 의 monolithic action head 를 **shared latent(협응 의도) + 좌·우 arm residual latent(실행 보정)** 로 분해하는 Structured Action Expert(SAE) 와, 학습된 latent 구조를 배포 시 해석해 강성(stiffness)을 적응적으로 조절하는 Latent-Aware Controller(LAC) 를 제안해, π₀ 류 baseline 대비 tight-coordination task 성공률을 27%p, 실세계 OOD 를 13%→27% 로 끌어올린 논문입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 양팔 협응(coordination)이 강하게 결합된 task(handover, 공동 운반, 동기화)에서 reliable·interpretable·deploy-stable 한 행동을 보장하는 것. 기존 VLA 는 양팔 14-DoF 를 하나의 벡터로 직접 회귀해 협응을 *암묵적으로만* 학습합니다.
- **기존 접근의 한계** — monolithic action head 는 "task-level 협응 의도"와 "팔별 실행 디테일"이라는 근본적으로 다른 변동 요인을 하나의 벡터에 뭉뚱그려, 동기화 강도·실행 비대칭·안전 제약이 모두 implicit 으로 남고 배포 시 해석·조정이 불가능합니다.
- **본 논문의 가설** — *"협응은 그 자체가 action 이 아니라 action 들 위의 구조(structure over actions)"* 라는 관찰. 따라서 협응을 명시적 구조 사전(structural prior)으로 action 생성 단계에 주입하면 더 강한 inductive bias 와 해석 가능한 latent 를 얻는다는 가설입니다.
- **왜 지금 중요한가** — backbone 용량을 키운 π₀.₅ 가 bimanual-specific task 에서 π₀ 를 일관되게 못 이긴다는 관찰(§IV-B)이, 용량만으로는 inter-arm 협응이 해결되지 않으며 구조적 inductive bias 가 별도로 필요함을 시사합니다.
- **추가 동기 (배포·데이터)** — 학습된 협응 표현을 force/impedance 제어 하드웨어 없이 standard joint-command 파이프라인 위에서 실시간으로 활용(LAC)하고, sequential 위주의 시연 데이터를 concurrent 협응 밀도가 높은 분포(Co-Motion)로 보강하려는 동기입니다.

---

## 🧩 핵심 기여

- **Structured Action Expert (SAE)** — 사전학습 VLA backbone 의 monolithic projector 를 shared latent + 좌·우 residual latent 의 병렬 디코더로 교체하고, 최종 joint command 를 `shared + residual` 의 **가법 합성(additive composition)**으로 구성. 기존 joint-level action 인터페이스를 그대로 보존하면서 협응 구조와 실행 보정을 명시 분리합니다.
- **Task-Adaptive Coordination Losses** — 대칭/비대칭/시간결합이라는 협응 regime 별로 골라 쓰는 3종 보조손실(Sparse Residual / Shared Mean Velocity / Temporal Sync)을 모듈식으로 도입.
- **Latent-Aware Controller (LAC)** — 추가 학습 모듈 없이, 배포 시 shared/residual 의 energy·opposition 을 읽어 stiffness $`\alpha_t`$ 를 macro-dominant / precision-critical / noise-suppression 세 regime 으로 적응 변조하는 1차 low-pass 컨트롤러.
- **Co-Motion 시연 패러다임** — RoboTwin 2.0 코드생성 파이프라인의 스케줄링 로직만 재구성해 양팔을 병렬 dispatch, 동시 협응 샘플 밀도를 높이는 데이터 전략. efficiency↔learnability trade-off 를 드러냅니다.
- **실험적 검증** — sim(RoboTwin 2.0) + 실세계(AgileX Cobot Magic)에서 tight-coordination 27%p 향상, 실세계 OOD 2배 이상(13%→27%), 완료시간 최대 25% 단축.

---

## 🔑 기술 키워드

- **Structured Action Expert (SAE)** — VLA 의 단일 action projector 를 "공통 의도용 head + 팔별 보정용 head" 로 쪼갠 구조화 action 디코더.
- **Shared–Residual Decomposition** — 같은 hidden state 에서 공통 latent 하나와 팔별 residual latent 둘을 뽑아 `공통+보정` 으로 명령을 합성하는 분해 — "두 사람이 같은 악보(shared)를 보되 각자 미세 보정(residual)을 더하는" 구조.
- **Latent-Aware Controller (LAC)** — 학습 없이 배포 시 latent 의 크기·방향만 읽어 실행 강성을 조절하는 어댑티브 저역통과 필터.
- **Micro-Motion Ratio $`\rho_t`$** — residual energy 대 shared energy 비. 현재 스텝에서 미세 보정이 얼마나 중요한지를 나타내는 스칼라.
- **Opposition Score $`\omega_t`$** — 좌·우 residual 의 코사인 유사도에 음부호. 두 팔이 *반대 방향* 보정을 가하는(안정화·정렬 같은 의미 있는 협응) 정도.
- **Adaptive Stiffness Modulation** — $`\rho_t,\omega_t`$ 에 따라 강성을 올리거나(빠른 직행 / 정밀보정 보호) 내리는(노이즈 억제) 3-regime 규칙.
- **Co-Motion** — 양팔을 sequential 이 아닌 concurrent 로 시연·수집하는 데이터 패러다임 — "병렬 작업 분배 + 공유 기준 좌표 + look-ahead".
- **Temporal Synchronization Loss** — 두 팔의 가감속 *타이밍*(방향 무관)을 상관시키는 손실, $`1-\mathrm{corr}_{\text{pred}}`$.
- **Flow-matching action expert (π₀ backbone)** — 본 논문이 SAE 를 이식하는 토대가 되는 연속 action 예측 VLA backbone.

---

## 🔬 방법론

### 직관

Co-VLA 의 출발점은 단순한 관찰입니다. 두 팔이 협력해 물건을 옮길 때, 그 행동에는 "둘이 함께 가야 하는 공통 의도"(예: 물체를 같은 방향으로 운반)와 "각 팔이 따로 해야 하는 미세 보정"(예: 한 팔은 잡고 한 팔은 미끄러짐 방지)이 섞여 있습니다. 기존 VLA 는 이 둘을 14차원 벡터 하나로 토해내므로, 무엇이 "공통 협응"이고 무엇이 "팔별 디테일"인지 모델 내부에 뒤섞여 버립니다.

SAE 는 이 둘을 **구조적으로** 갈라놓습니다. 같은 hidden state 에서 공통 latent 하나와 좌·우 latent 둘을 뽑아, 공통 latent 은 양팔 공통 동작을, residual latent 은 각 팔의 보정만을 만들도록 하고, 최종 명령은 둘의 덧셈으로 만듭니다. 그리고 task 마다 협응의 성격(대칭이냐, 역할 비대칭이냐, 타이밍 결합이냐)이 다르므로, regime 에 맞는 보조손실을 골라 이 분해가 *의미 있게* 학습되도록 형태를 잡아줍니다.

LAC 는 학습된 분해를 *배포 시점에* 활용하는 영리한 후처리입니다. 매 스텝, residual 이 shared 대비 얼마나 큰지(에너지 비)와 두 팔의 residual 이 얼마나 *반대 방향*인지(opposition)를 보고, 지금이 "빠르게 직행해도 되는 macro 구간"인지 "미세 정렬을 보호해야 하는 정밀 구간"인지 "그냥 떨림(노이즈)인지"를 판정해 저역통과 필터의 강성을 실시간으로 바꿉니다. 학습을 건드리지 않고, force/impedance 센서도 없이, 표준 joint 명령만으로 부드럽고 안전한 실행을 얻는 것이 핵심입니다.

마지막으로 Co-Motion 은 *학습 데이터 쪽* 보강입니다. 시뮬레이터의 시연 스케줄을 sequential 에서 concurrent 로 바꿔 동시 협응 샘플을 늘립니다. 다만 이는 데이터를 더 어렵게 만들어, 수집은 빨라지지만 학습은 더 까다로워지는 trade-off 를 드러냅니다.

### 아키텍처

![Figure 1 — SAE architecture](https://arxiv.org/html/2606.20285/fig/co-vla-SAE-new.png)

> "Figure 1 : Structured Action Expert (SAE) architecture." (§III-A)
(SAE 가 단일 projector 를 shared/residual 병렬 디코더로 대체하고 가법 합성으로 joint command 를 복원하는 구조를 시각화합니다.)

표준 VLA(예: π₀)는 hidden state $`h_t\in\mathbb{R}^{H}`$ 를 하나의 projection 으로 joint 명령에 직접 사상합니다.

> "In state-of-the-are VLA models such as $`\pi_{0}`$ [4], the action head maps transformer hidden states directly to joint-level commands." (§III-A)
(monolithic head 는 양팔 action 을 단일 벡터로 취급해 inter-arm 협응을 암묵적 학습에 떠넘깁니다.)

$$a_{t}=f_{\pi_{0}}(h_{t}),\qquad a_{t}=[a_{t,L},a_{t,R}]\in\mathbb{R}^{14}$$

SAE 는 같은 $`h_t`$ 에서 세 latent 을 계산합니다. 공유 latent $`z_t^{s}\in\mathbb{R}^{L}`$ 는 공통 협응 의도를, 좌/우 latent $`z_t^{L},z_t^{R}\in\mathbb{R}^{L}`$ 는 팔별 실행 정보를 인코딩합니다.

$$z_{t}^{s}=g_{s}(h_{t}),\qquad z_{t}^{L}=g_{L}(h_{t}),\qquad z_{t}^{R}=g_{R}(h_{t})$$

공유 latent 은 좌·우 별도 head 로 공통 성분을, residual latent 은 각각 별도 head 로 보정 성분을 만든 뒤 가법 합성합니다.

$$a_{t,L}^{s}=\phi_{L}^{s}(z_{t}^{s}),\qquad a_{t,R}^{s}=\phi_{R}^{s}(z_{t}^{s})$$

$$a_{t,L}^{r}=\phi_{L}^{r}(z_{t}^{L}),\qquad a_{t,R}^{r}=\phi_{R}^{r}(z_{t}^{R})$$

$$a_{t,L}=a_{t,L}^{s}+a_{t,L}^{r},\qquad a_{t,R}=a_{t,R}^{s}+a_{t,R}^{r}$$

여기서 $`a_{t,L},a_{t,R}\in\mathbb{R}^{7}`$ 는 각 매니퓰레이터의 예측 joint velocity 입니다.

> "This decomposition preserves the original joint-level action interface while introducing an explicit separation between coordination structure and execution-specific adjustments." (§III-A)
(분해가 기존 joint-level 인터페이스를 보존한 채 협응 구조와 실행 보정을 명시적으로 가른다는 점이 SAE 의 설계 의도를 한 문장에 못 박습니다.)

### 학습 목표 / 손실

세 보조손실은 각각 다른 협응 regime 을 겨냥합니다.

**(1) Sparse Residual Regularization** — 대칭 task 에서 residual 을 $`\ell_1`$ 로 눌러 shared-dominant 행동을 유도합니다.

$$\mathcal{L}_{\text{sparse}}=\mathbb{E}_{t}\left[\|a_{t,L}^{r}\|_{1}+\|a_{t,R}^{r}\|_{1}\right]$$

> "This loss biases the model toward encoding common motion in the shared latent, while allowing residual components to activate only when asymmetric adjustments are necessary." (§III-A, Eq. (1))
(residual 이 *필요할 때만* 켜지도록 강제해 공통 동작을 shared latent 에 몰아넣습니다.)

**(2) Shared Mean Velocity Consistency** — shared 성분을 양팔 평균 속도 $`\bar{u}_t=\tfrac12(u_{t,L}+u_{t,R})`$ 에 정렬해 "공통 동작 추세"로서의 의미를 부여합니다.

$$\mathcal{L}_{\text{shared}}=\mathbb{E}_{t}\left[\|a_{t,L}^{s}-\bar{u}_{t}\|_{2}^{2}+\|a_{t,R}^{s}-\bar{u}_{t}\|_{2}^{2}\right]$$

**(3) Temporal Synchronization Loss** — 시간 차분 크기 $`m_{t,L}=\|\Delta a_{t,L}\|_2`$, $`m_{t,R}=\|\Delta a_{t,R}\|_2`$ 를 표준화 후 상관시켜, 방향과 무관하게 가감속 *타이밍*을 맞춥니다.

$$\mathrm{corr}_{\text{pred}}=\mathbb{E}_{t}\left[\tilde{m}_{t,L}\tilde{m}_{t,R}\right],\qquad \mathcal{L}_{\text{sync}}=1-\mathrm{corr}_{\text{pred}}$$

전체 목적함수는 primary action loss 에 task 별로 *하나*의 보조손실을 더한 형태입니다.

$$\mathcal{L}=\mathcal{L}_{\text{action}}+\lambda\,\mathcal{L}_{\text{aux}},\qquad \mathcal{L}_{\text{aux}}\in\{\mathcal{L}_{\text{sparse}},\mathcal{L}_{\text{shared}},\mathcal{L}_{\text{sync}}\}$$

> "$`\mathcal{L}_{\text{sparse}}`$ for near-symmetric execution, $`\mathcal{L}_{\text{shared}}`$ for asymmetric role assignment, and $`\mathcal{L}_{\text{sync}}`$ for temporally coupled motion. We set $`\lambda=0.001`$ across all experiments." (§III-A, Eq. (4))
(보조손실 선택이 task 의 *사전지식*에 의해 수동으로 라우팅되며, 가중치는 전 실험 공통 $`\lambda=0.001`$ 입니다 — 이 수동 라우팅이 곧 ⚖️ 한계의 핵심 약점입니다.)

### LAC — 배포 시 latent 해석 컨트롤러

LAC 는 추가 학습/정책 수정 없이, SAE 가 이미 만든 shared/residual 분해를 배포 시 해석합니다. 매 스텝 다음을 계산합니다.

**Energy & micro-motion ratio:**

$$E_{t}^{s}=\tfrac12(\|a_{t,L}^{s}\|_{2}+\|a_{t,R}^{s}\|_{2}),\quad E_{t}^{r}=\tfrac12(\|a_{t,L}^{r}\|_{2}+\|a_{t,R}^{r}\|_{2}),\quad \rho_{t}=\frac{E_{t}^{r}}{E_{t}^{s}+\varepsilon}$$

**Opposition score** (residual 코사인 유사도에 음부호):

$$\omega_{t}=-\frac{\langle a_{t,L}^{r},a_{t,R}^{r}\rangle}{\|a_{t,L}^{r}\|_{2}\,\|a_{t,R}^{r}\|_{2}+\varepsilon}$$

> "A high opposition score indicates that the two arms apply residual adjustments in opposing directions, which commonly arises in coordinated behaviors such as stabilizing, holding, or fine alignment." (§III-B)
(반대 방향 residual = 의미 있는 협응(안정화·정렬), 무질서한 residual = 떨림으로 구분하는 신호입니다.)

**Adaptive stiffness (3-regime):** $`\rho_t<\tau_\rho`$ → macro-dominant($`+\Delta_{\text{macro}}`$, 빠른 직행); $`\rho_t\ge\tau_\rho \wedge \omega_t>\tau_\omega`$ → precision-critical($`+\Delta_{\text{prec}}`$, 미세 정렬 보호); 그 외 → noise suppression($`-\Delta_{\text{noise}}`$). 이후 $`[\alpha_{\min},\alpha_{\max}]`$ 로 클립하고 시간 평활합니다.

$$\alpha_{t}=(1-\beta)\,\alpha_{t-1}+\beta\,\hat{\alpha}_{t}$$

**Joint-level refinement** — raw 명령 $`q_t=[a_{t,L};a_{t,R}]`$ 에 1차 low-pass 적용:

$$\tilde{q}_{t}=(1-\alpha_{t})\,\tilde{q}_{t-1}+\alpha_{t}\,q_{t}$$

> "LAC does not introduce additional learning modules and does not modify the trained policy. ... without requiring force sensing or impedance control." (§III-B)
(LAC 의 차별점은 "학습 없이, 센서 없이" 이미 학습된 latent 구조만으로 EMA 식 균일 평활의 phase-lag 문제를 피한다는 데 있습니다.)

### Co-Motion — 협응 시연 패러다임

![Figure 2 — Co-Motion paradigm](https://arxiv.org/html/2606.20285/fig/co-motion.png)

> "Figure 2 : Visualization of sequential motion paradigm (left) and our designed collaborative motion paradigm (right)." (§III-C)
(sequential 시연 대비, task 를 동기화 경계가 있는 stage 로 쪼개 비충돌 subtask 를 양팔에 병렬 dispatch 하는 방식을 대비합니다.)

> "It is implemented by restructuring the task-level scheduling logic within the RoboTwin 2.0 code-generation pipeline; the underlying motion planner (cuRobo) and primitive interfaces remain unchanged." (§III-C)
(motion planner(cuRobo)·primitive 는 그대로 두고 *스케줄링 로직만* 재구성한, 모델 비침습적 데이터 전략임이 중요합니다.)

세 지원 메커니즘: (i) 공유 기준 좌표(handover midpoint·goal pose), (ii) 근미래 상호작용 타깃의 look-ahead precompute, (iii) clearance margin 을 둔 safe intermediate target(병렬 불가 시 sequential 로 graceful fallback).

### 학습 셋업

2-phase 전략입니다. **Phase 1 (warm-up):** backbone 동결, 새 SAE 층(shared/residual projection + share-to-arm routing)만 1,000 step, peak LR $`5\times10^{-5}`$. **Phase 2 (full FT):** Phase 1 체크포인트에서 전체 unfreeze, 30,000 step, peak LR $`2.5\times10^{-5}`$ → $`2.5\times10^{-6}`$ decay. 양 phase 모두 batch 32, 4 GPU FSDP.

---

## 📊 실험 설정과 결과

평가는 sim(RoboTwin 2.0, Aloha-AgileX) + 실세계(AgileX Cobot Magic, wrist-mounted camera) 두 축입니다. sim 은 동시 양팔 동작이 *필수*인 subset 을 골라 task 당 1,000 시연으로 task별 별도 모델을 FT, 100 rollout 으로 Easy/Hard 평가. baseline 은 π₀, π₀.₅.

**Table I — RoboTwin 2.0 성공률(%), 100 rollout:**

| Task | π₀.₅ Easy | π₀.₅ Hard | π₀ Easy | π₀ Hard | Co-VLA Easy | Co-VLA Hard |
|---|---|---|---|---|---|---|
| Handover Block | 44 | 10 | 64 | 7 | **91** | **12** |
| Lift Pot | 100 | 60 | 100 | 63 | 100 | **65** |
| Pick Diverse Bottles | 95 | 18 | 91 | 13 | **95** | 16 |
| Pick Dual Bottles | 100 | **27** | 100 | 16 | 100 | 18 |
| Place Bread Basket | **92** | 28 | 70 | 46 | 69 | **48** |
| Place Bread Skillet | 38 | 7 | 63 | 8 | **70** | **8** |
| Put Object Cabinet | 70 | **19** | 79 | 8 | **81** | 5 |
| Scan Object | 45 | **6** | 41 | 3 | **50** | 2 |
| **Average** | 73 | 21.9 | 76 | 21 | **82** | **22** |

> "raising the average Easy-setting success rate from 76% ($`\pi_{0}`$) and 73% ($`\pi_{0.5}`$) to 82%. The largest improvement appears in Handover Block (64% $`\to`$ 91% over $`\pi_{0}`$; 44% $`\to`$ 91% over $`\pi_{0.5}`$)." (§IV-B, Table I)
(가장 큰 향상이 tight-coordination 의 대표인 Handover Block 에서 나온다는 점이, 구조 분해가 *역할 결합* task 에 특히 유효하다는 핵심 증거입니다.)

> "Notably, $`\pi_{0.5}`$ does not consistently outperform $`\pi_{0}`$ on these bimanual-specific tasks, indicating that backbone capacity alone is insufficient to resolve inter-arm coordination without structural inductive bias." (§IV-B, Table I)
(용량을 키운 π₀.₅ 가 bimanual task 에서 π₀ 를 못 이긴다는 관찰이 "구조적 inductive bias 가 별도로 필요"라는 논문 주장의 핵심 지지입니다.)

**Co-Motion 효율 (Table II/III)** — 4개 task(Handover Block, Scan Object, Place Bread Skillet, Put Object Cabinet)에서 1,000 시연 생성시간을 10–25% 단축. 추론 시 완료시간도 Co-Motion 학습 모델이 더 짧음(Table III 평균 RoboTwin π₀ 21.58 / Co-VLA 22.88 vs Co-Motion π₀ 19.78 / Co-VLA **18.18**초).

**Table IV — Co-Motion 학습 시 성공률(%), Learnability:**

| Task | π₀ Easy | π₀ Hard | Co-VLA Easy | Co-VLA Hard |
|---|---|---|---|---|
| Handover Block | 15 | 8 | 38 | 8 |
| Place Bread Skillet | 60 | 3 | 62 | 8 |
| Put Object Cabinet | 83 | 45 | 70 | 47 |
| Scan Object | 43 | 8 | 53 | 3 |
| **Average** | 50 | 16 | **56** | 17 |

> "the average Easy-setting success rate drops from 76% to 50% for $`\pi_{0}`$, and from 82% to 56% for Co-VLA. This drop is consistent across architectures, indicating that the difficulty lies in the data distribution itself rather than a specific model limitation." (§IV-B, Table IV)
(Co-Motion 은 수집은 빠르지만 학습을 *더 어렵게* 만드는 efficiency↔learnability trade-off 를 드러냅니다 — 단, Co-VLA 가 π₀ 보다 덜 떨어져(56 vs 50) 구조 분해가 고밀도 협응 흡수에 유리함을 시사합니다.)

**Table V — 실세계 30 rollout, ID/OOD:**

| Method | Handover ID | Handover OOD | Pick Bottles ID | Pick Bottles OOD | Lift Pot ID | Lift Pot OOD |
|---|---|---|---|---|---|---|
| π₀ | 63 | 13 | 57 | 37 | 43 | 33 |
| Co-VLA (noLAC) | 57 | 17 | 57 | **50** | 63 | 27 |
| Co-VLA (LAC) | **73** | **27** | **67** | 47 | **67** | **37** |

> "Comparing Co-VLA$`{}_{\text{noLAC}}`$ with $`\pi_{0}`$ isolates the effect of SAE alone. The results are task-dependent: SAE yields a notable improvement on Lift Pot (43% $`\to`$ 63% ID) but a slight decrease on Handover (63% $`\to`$ 57% ID), suggesting that structured action decomposition alone does not uniformly translate to higher success without execution-time refinement." (§IV-C, Table V)
(SAE *단독*은 task-dependent 하며 Handover ID 에서는 오히려 하락 — LAC 가 붙어야 모든 ID 에서 π₀ 를 회복·초과합니다. SAE 와 LAC 의 상보성이 핵심 메시지입니다.)

한편 Pick Bottles OOD 는 noLAC(50%)가 LAC(47%)보다 높은 *예외*인데, 논문은 LAC 의 noise suppression 이 분포 변화에서 우연히 유익했던 residual 보정까지 걸러냈을 가능성으로 해석합니다.

**Table VI — 보조손실 ablation(Easy, 100 rollout):**

| Aux. Loss | Lift (Sym.) | Cabinet (Asym.) | Skillet (Temp.) |
|---|---|---|---|
| None | 99 | 49 | 51 |
| $`+\mathcal{L}_{\text{sparse}}`$ | 100 | 51 | 55 |
| $`+\mathcal{L}_{\text{shared}}`$ | 100 | **72** | 55 |
| $`+\mathcal{L}_{\text{sync}}`$ | 100 | 70 | **62** |

> "On the role-asymmetric Put Object Cabinet task, adding shared consistency produces the largest improvement (49% $`\rightarrow`$ 70%) ... On the temporally coupled Place Bread Skillet task, synchronization loss yields the highest performance (51% $`\rightarrow`$ 62%)." (§IV-D, Table VI)
(각 보조손실이 *자기 regime* 에서 최대 이득을 낸다는 것이 "협응을 다중 regime 으로 보는" 가설의 직접 검증입니다. 단 단일-loss 변형만 평가했습니다.)

**Latent–behavior alignment (Fig. 5)** — shared energy $`E_t^s`$ 와 inter-arm 동기화 $`\mathrm{Sync}_t`$ 는 양의 상관, residual energy $`E_t^r`$ 는 음의 상관 → 학습된 분해가 *해석 가능한* 협응 구조를 포착함을 시사.

**LAC ablation (Fig. 6)** — naive EMA 는 가장 매끄러운 궤적을 내지만 Pick Bottles 60% 로 LAC(67%) 대비 하락. EMA 의 균일 저역통과가 phase-lag 와 over-smoothing 으로 precision-critical micro-adjustment 를 지워버리는 반면, LAC 는 의미 있는 residual 을 선택적으로 보호합니다.

---

## ⚖️ 한계

- **보조손실의 수동 라우팅** — $`\mathcal{L}_{\text{aux}}`$ 선택이 "각 task 협응 구조의 사전지식"에 의존합니다(§III-A). task 별로 사람이 regime 을 분류해 손실을 골라야 하므로, task 분포가 커지거나 협응 regime 이 모호한 task 에서는 확장성이 떨어집니다. 저자도 자동 loss routing(inter-arm velocity correlation·role asymmetry index 등 computable descriptor)을 future work 로 명시합니다.
- **task별 별도 모델 FT** — sim 에서 "fine-tune a separate model per task"(§IV-B). 즉 단일 multi-task 정책의 협응 일반화가 아니라 task-specialized 모델들의 합이며, 본 논문의 성공률은 task 별 전문화 가정 위에 있습니다. 멀티태스크/언어조건 일반화는 미검증입니다.
- **단일-loss ablation 한계** — 계산 제약으로 보조손실 조합(joint activation·adaptive weighting)은 평가하지 않았습니다(§IV-D). 여러 regime 이 한 task 안에 공존할 때의 거동이 비어 있습니다.
- **Co-Motion 의 learnability 손실** — concurrent 시연은 수집을 빠르게 하지만 성공률을 크게 떨어뜨립니다(82→56). 현재 VLA backbone 의 spatio-temporal reasoning 이 고밀도 협응 분포를 충분히 못 소화한다는 것으로, Co-Motion 은 "더 나은 데이터"가 아니라 "더 어려운 데이터"입니다 — 당장의 성능 레버가 아닙니다.
- **LAC 의 다수 휴리스틱 파라미터** — $`\alpha_{\text{base}},\Delta_{\text{macro/prec/noise}},\tau_\rho,\tau_\omega,\beta`$ 등 8개 임계/마진을 실세계에서 *경험적으로* 고정(§IV-C). task 간 공유한다고 했으나 robot·dynamics 가 바뀌면 재튜닝 부담이 있고, Pick Bottles OOD 의 LAC 역효과처럼 noise-suppression 이 유익 신호를 지우는 실패 양식이 존재합니다.
- **backbone 일반성 미검증** — shared–residual 분해가 architecture-agnostic 이라 주장하지만, Diffusion Policy 등 다른 연속-action paradigm 검증은 future work 로 남겨져 flow-matching π₀ 외 일반화 증거가 없습니다.

---

## ♻️ 재현성

- **코드/모델 공개** — 본문에서 코드·체크포인트 공개 링크(GitHub/HF)는 확인되지 않습니다(arXiv HTML 본문 기준). π₀/π₀.₅ backbone 위 구현이나 가중치 배포 명시는 없습니다.
- **시뮬레이터/벤치마크** — RoboTwin 2.0(50+ dual-arm task, cuRobo planner)과 그 코드생성 파이프라인을 사용하며, Co-Motion 은 이 파이프라인의 스케줄링 로직 재구성으로 구현됨이 명시되어 재현 가능성이 비교적 높습니다.
- **하드웨어** — sim: Aloha-AgileX, 실세계: AgileX Cobot Magic(양팔, wrist 카메라), 4 GPU FSDP. 학습 step·LR·batch·LAC 파라미터($`\alpha_{\text{base}}=0.4`$ 등)는 본문에 수치로 명시되어 재현에 유리합니다.
- **데이터** — sim task당 1,000 successful demo(clean scene), 실세계 task당 50 teleop demo. 데이터셋 공개 언급은 없습니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P1(Heterogeneous Body/Hand Action Expert) — 1차.** SAE 는 monolithic action head 를 **공유 trunk + 분리 head** 로 교체하는 전형적 D1(split form, v1=hybrid 공유 trunk+split head)·D4(Body↔Hand information sharing)·D7(π backbone integration / partition, v1=slice π0 action expert + FT both sides) 사례입니다. 단 본 논문의 split 축은 *anatomical Body/Hand* 가 아니라 *Left/Right arm* 이며, sharing 메커니즘도 FiLM(우리 D4 v1)이 아니라 **shared latent 의 가법 합성**입니다. P1 §2 scouting lens 의 "comparison group(action-space architecture 패밀리)"으로 정확히 들어오며, Body/Hand split 의 north star 와 *구조는 동형, 해부학 축만 다른* 강한 비교 대상입니다.
- **P4(Pretraining for Data-Efficient Adaptation) — 2차.** 2-phase(warm-up freeze→full FT)는 D21(staged recipe)의 Stage 2(VLM-stable + 새 head 학습)·Stage 3 와 직접 대응합니다. 단 Phase 2 에서 backbone 을 *완전히* unfreeze 하므로 우리 D19 v1(VLM freeze + action experts only)·D20(prior-preservation)과는 **긴장**합니다 — 이 논문은 prior-preservation 을 포기하고 full-FT 로 갑니다.
- **P0(Datasets & Benchmarks) — 보조.** Co-Motion 은 D26(benchmark/eval 스코프, RoboTwin)·데이터 수집 파이프라인 측면에서 닿지만, 새 데이터셋/벤치마크를 *공개*하지 않으므로 P0 핀 자격은 약합니다.
- **Identity 지지/긴장** — Identity 의 "monolithic decoder 는 dead end, 구조적 분리가 답" 명제를 **강하게 지지**(π₀.₅ 용량 무용론 + 구조 inductive bias 필요)합니다. 긴장점: 본 논문의 차별 축은 *contact-rich hand dexterity* 가 아니라 *dual-arm coordination* 이라, 우리 hand-centric 코어(per-finger·tactile)와는 결이 다릅니다.
- **경쟁자 함의** — P1 §5 핀 중 LaMP(dual-expert), DexGrasp-VLA(anatomical arm/hand split)와 직접 비교군. Samsung 계열 저자라는 점에서 산업계 bimanual VLA 구조화 트렌드의 신호입니다.

---

## ✨ 핀 논문 대비 델타

- **vs π₀ / π₀.₅ (P1 backbone 핀)** — 본 논문은 두 backbone 을 *baseline* 으로 깔고, action head 만 SAE 로 교체해 일관 향상을 보입니다. 델타는 "backbone 은 그대로, head 구조화만으로 협응 이득"이라는 분리 실험 — 우리가 π0 action expert 를 slice 할 때(D7) head 구조 선택이 독립 레버임을 보여줍니다.
- **vs LaMP (dual-expert gated cross-attention 핀)** — LaMP 가 *두 expert + gating* 으로 정보를 섞는다면, Co-VLA 는 *하나의 hidden state → 세 latent → 가법 합성* 으로 더 단순합니다. gating 대신 **명시적 손실로 latent 의미를 형성**하고, 배포 시 LAC 로 해석하는 점이 새롭습니다.
- **vs DexGrasp-VLA / Shared-Autonomy Arm-Hand VLA (anatomical split 핀)** — 둘 다 *arm vs hand* 해부학 분리인 반면, Co-VLA 는 *left vs right* 대칭 분리 + *shared coordination* 축을 추가합니다. "공통 협응 latent" 이라는 제3의 축(shared)은 두 핀 어디에도 없는 진짜 새 요소입니다.
- **진정한 신규성** — (1) shared/residual *가법 분해*를 joint-velocity 공간에 직접 적용, (2) regime 별 보조손실로 latent 의미를 *형성*, (3) 학습 없는 배포-시 latent 해석 컨트롤러(LAC)의 energy·opposition 휴리스틱. 특히 (3)은 P1 핀 어디에도 없는 deployment-side 기여입니다.

---

## ⚙️ 의사결정 함의

- **D1/D4 — 분해 축과 sharing 메커니즘.** "shared latent 가법 합성"을 우리 Body/Hand split 의 *추가 후보*로 등록할 가치가 있습니다. 구체적으로 D4 의 FiLM(v1) 대신 `a = a_shared(z_s) + a_residual(z_b, z_h)` 가법 합성을 비교군으로 두는 ablation — config 키로는 `action_head.composition ∈ {film, additive_shared_residual}`.
- **보조손실 도입.** $`\mathcal{L}_{\text{sync}}=1-\mathrm{corr}_{\text{pred}}`$ 와 $`\mathcal{L}_{\text{sparse}}`$ 는 Body/Hand 협응에도 이식 가능 — Body↔Hand 타이밍 결합이 중요한 tool-articulation(Phase 2)에서 `loss.aux.sync_weight=0.001` 로 시도. 단 *수동 라우팅* 약점을 그대로 들이지 말고 task descriptor 자동 라우팅을 함께 설계.
- **D19/D20 긴장 주의.** 본 논문의 성능은 Phase 2 *full unfreeze* 에 기댑니다. 우리 v1(freeze + action experts only)을 유지하려면, SAE 형 구조 이득이 backbone freeze 하에서도 유지되는지 별도 검증 필요 — 이게 안 되면 D19 freeze 가정과 충돌합니다.
- **배포-시 LAC.** force/impedance 없이 latent energy·opposition 으로 stiffness 를 변조하는 LAC 는 우리 System0(P3) 와 *대안적* 안전·평활 레버입니다. 단 LAC 는 학습 없는 휴리스틱이라 System0 의 RL 안정화와는 역할이 다름 — 보완재로만.
- **메트릭.** 완료시간(temporal compactness)·trajectory 가속 peak·cross-rollout variance 를 협응 품질 메트릭으로 추가 검토.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 체크) 해부학 축 불일치.** 우리는 Left/Right 대칭이 아니라 Body/Hand *비대칭* 분해입니다. "shared coordination latent" 의 전제(두 출력이 평균을 공유)는 양팔엔 자연스럽지만 Body(7-DoF arm pose)와 Hand(22-DoF finger)에는 *단위·차원·의미가 다름*. $`\mathcal{L}_{\text{shared}}`$ 의 평균속도 정렬이 Body/Hand 에 그대로 적용되면 무의미할 수 있음 — 먼저 shared latent 을 Body/Hand 공통 "task intent" 로 재정의할지 종이 위에서 점검.
- **full-FT 의존성.** Co-VLA 이득이 Phase 2 full unfreeze 에 묶여 있다면, 우리 VLM-freeze 정책에서 재현 안 될 수 있음. 가장 싼 검증: backbone freeze + SAE-only(Phase 1만 연장)로 Handover-류 task 성공률이 π0 head 대비 오르는지.
- **수동 loss 라우팅의 확장 실패.** 우리 task(in-hand rotation, tool articulation)는 협응 regime 이 단일 라벨로 안 떨어질 수 있음. 잘못된 regime 라벨 → 잘못된 보조손실 → 성능 하락 위험. descriptor 자동 라우팅 없이 도입하면 task 수 증가 시 관리 불능.
- **LAC 의 OOD 역효과.** Pick Bottles OOD 에서 LAC 가 noLAC 보다 *낮았던* 사례(47 vs 50)처럼, noise-suppression 이 유익 residual 을 지우는 실패가 contact-rich hand 에서 더 잦을 수 있음(미세 접촉 보정 = 작은 residual). LAC 의 $`\tau_\rho,\tau_\omega`$ 가 tactile 보정 신호를 노이즈로 오판하지 않는지 점검.
- **task별 별도 모델 가정.** 우리는 multi-task·언어조건 일반화를 지향하는데, 본 논문 수치는 task-specialized 모델 합. 단일 정책에서 협응 이득이 유지되는지가 미지수 — 멀티태스크 세팅 재현이 가장 큰 리스크.
- **시뮬레이터 의존(Co-Motion).** Co-Motion 은 RoboTwin/cuRobo 코드생성에 묶여 있어 우리 Isaac Lab/실데이터 파이프라인엔 직접 이식 불가. 데이터 측 레버로 기대하지 말 것.

---

## 💡 컨텍스트 제안

- **P1 §5 비핀 비교군 추가 후보** — Co-VLA(arXiv:2606.20285)를 "shared–residual 가법 분해 + 배포-시 latent 컨트롤러(LAC)" 사례로 P1 Methodology base(non-pinned) 표에 등재 검토. D1/D4 의 *가법 합성* 비교군 + D7 *full-FT vs freeze* 긴장 사례로 가치가 있습니다(핀 cap 8 은 유지 — 비핀 권장).
- **D4 후보 확장 제안** — D4(Body↔Hand information sharing) deferred 후보에 "shared-latent additive composition"을 FiLM/gated-cross-attention(LaMP)과 나란히 기록할 것을 제안합니다. (context 파일은 직접 수정하지 않음.)
- 그 외 핀 교체·Decision 이동은 없음.

> 💡 base 매핑은 `/implement-design analysis/2606.20285/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
