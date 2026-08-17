# Paper Analysis — CoRMA: Contrastive RMA for Contact-Rich Meta-Adaptation

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | CoRMA: Contrastive RMA for Contact-Rich Meta-Adaptation |
| 저자 | Wentian Wang, Chutong Wen, Hongxu Ma, Wuhao Wang, Zhexiong Xue, Abdul Haseeb Nizamani, Dandi Zhou, Xinhai Sun, Jianqiao Zhu (Synthoid AI; The University of Hong Kong) |
| 링크 | [arXiv:2605.22082](https://arxiv.org/abs/2605.22082) |
| 발행일 / 버전 | 2026-05-21 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-05-26 |
| 관련 Pillar | P3, P1 |
| 태그 | sim2real, force |

---

## 🧭 한 줄 요약 (TL;DR)

CoRMA 는 RMA 의 privileged-train/deployable-test 골격을 유지한 채 시뮬레이터 raw parameter 적응을 6D semantic contact context 추론으로 바꾼 force-dominant assembly 용 meta-adaptation 프레임워크입니다. causal Transformer adapter 와 force-regime InfoNCE 보조 목표를 결합한 결과, PegInsert / GearMesh / NutThread 세 과제에서 동일한 Marvin 실로봇 인터페이스를 기준으로 FORGE baseline 보다 sim-to-real 격차가 작게 나옵니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — Contact-rich assembly (PegInsert, GearMesh, NutThread) 에서 시뮬레이터에서 강한 policy 가 실로봇으로 옮겨갈 때 발생하는 sim-to-real 성능 붕괴를 줄이는 것. 작은 contact 기하·마찰·컴플라이언스 mismatch 만으로 jamming 이나 비가역 실패가 발생합니다.
- **기존 접근의 한계** — FORGE 같은 task-specific RL policy 는 시뮬레이션 성공률은 거의 100% 에 가깝지만 실로봇에서는 12–25% 수준으로 급락합니다. demonstration 기반 IL/BC, residual sim-to-real fine-tuning, 적응 제어 모두 setup 이 바뀔 때마다 재calibration 비용이 들고 task variant 마다 다시 학습해야 합니다.
- **본 논문의 가설** — 관련된 assembly 과제들은 *recurring semantic contact structure* 를 공유한다는 것입니다. 즉 raw simulator parameter 보다 "contact onset, lateral engagement, guided transition, contact direction, jamming" 같은 의미 단위 latent 이 task 간 재사용 가능한 적응 인터페이스라는 주장입니다.
- **왜 RMA 변형이 필요한가** — 기존 RMA 는 visual / object-centric 정보 기반의 privileged extrinsics 를 가정합니다. 그런데 접촉 단계가 시작된 뒤 정작 중요한 정보는 "현재 상호작용이 free motion / first touch / guided sliding / thread engagement / jam 중 무엇인가"이며, 이를 force·proprio·action history 로 추론해야 합니다.

---

## 🧩 핵심 기여

- raw simulator parameter 대신 6D semantic contact context (`onset`, `lateral`, `guided`, `dir-x`, `dir-y`, `jam`) 를 privileged latent 로 정의해 PegInsert / GearMesh / NutThread 가 동일한 contact vocabulary 를 공유하도록 정렬한 설계.
- deployable 한 force / proprioceptive / action history 를 입력으로 받는 causal Transformer adapter 를 도입해, RMA 의 Conv1D 인코더 대비 mean validation $`R^{2}`$ 를 0.4336 에서 0.8792 로 끌어올린 성능 (Table 2).
- semantic regression head 위에 force-regime InfoNCE 보조 목표를 얹는 두-헤드 구조. 보조 head 의 임베딩 $`u_{t}`$ 는 표현 구조화 용도이고, policy 에는 $`\hat{z}_{t}`$ 만 주입됩니다.
- FORGE 와 동일한 Marvin 7-DoF 하드웨어 인터페이스 / TRAC-IK 실행 스택 / verification 규칙에서 세 과제 모두 verified real success 가 더 높게 유지되는 결과로 보여준 점 (Table 1).
- Stage 2 ablation 에서 "causal Transformer 가 주된 이득, InfoNCE 는 약한 정규화 효과" 라는 기여 분해를 보였습니다. InfoNCE weight 가 $`\lambda=0.01`$ 부근일 때 가장 좋다는 hyperparameter 증거도 함께 제시됩니다 (Appendix C).

---

## 🔑 기술 키워드

- **RMA (Rapid Motor Adaptation)** — privileged 교사 정책을 sim 에서 학습한 뒤 deployable sensor history 로 그 latent 를 예측하는 adapter 를 훈련하고, deploy 단계에서는 비특권 정보만 쓰는 teacher-student 프레임. CoRMA 의 비-cheating deployment 원칙이 여기서 나옵니다.
- **Privileged $`Z`$ (semantic contact context)** — 시뮬레이터에서만 접근 가능한 6D 의미 latent. raw friction/mass 같은 물리 파라미터가 아니라 "지금 접촉이 어느 단계인가" 를 점수화한 벡터로, 다중 assembly 과제의 공통 어휘 역할을 합니다.
- **Causal Transformer adapter** — fixed-length history 를 학습된 readout 토큰으로 요약하는 시계열 인코더. RMA 원형의 Conv1D 인코더보다 sparse 한 접촉 단서를 장기 horizon 에 걸쳐 통합하는 데 유리하다고 주장합니다.
- **InfoNCE (force-regime contrastive)** — 같은 force-regime 라벨끼리 positive, 다른 라벨이 negative 인 contrastive loss. CoRMA 에서는 표현 구조화용 약한 regularizer 로 쓰이며 supervised regression 을 대체하지 않습니다.
- **Force regime labels** — `free` / `first_contact` / `guided_slide` / `jam` 의 네 가지 coarse 라벨. deployable force evidence 로 계산되어 contrastive positive/negative 짝짓기에 쓰입니다.
- **FORGE baseline** — Isaac Lab 의 force-guided contact-rich manipulation RL 프레임워크. CoRMA 의 주된 비교군으로, privileged $`Z`$ 와 adapter 없이 같은 task family 로 학습됩니다.
- **Within-episode adaptation** — demonstration 도 test-time gradient 도 없이, 한 에피소드 안에서 추론된 contact context 만으로 policy 가 조정되는 적응 방식. MAML 계열의 inner-loop gradient update 와 대비됩니다.

---

## 🔬 방법론

### 직관

CoRMA 의 핵심 직관은 두 갈래로 정리됩니다. force-dominant assembly 에서 진짜로 알고 싶은 것은 "물체가 어디 있나"보다 "지금 접촉이 어느 단계인가"이고, 그 단계 정보는 raw simulator parameter 보다 의미 수준의 latent 로 표현해야 PegInsert / GearMesh / NutThread 가 공유 가능한 적응 인터페이스가 됩니다.

> "CoRMA is built on the hypothesis that related assembly tasks share recurring semantic contact structure." (§1)
(한글 해설 — 적응 latent 의 선택을 결정한 앵커 문장. 시뮬레이터 파라미터 대신 의미 단위 contact context 를 privileged target 으로 삼은 근거입니다.)

raw force history 만으로는 pointwise regression 이 모호하기에 CoRMA 는 causal Transformer 로 시간 컨텍스트를 모으고, force-regime InfoNCE 로 "비슷한 접촉 상황이면 비슷한 임베딩" 이라는 약한 의미 정규화를 더 겁니다.

![Figure 1 — CoRMA pipeline overview](https://arxiv.org/html/2605.22082/CoRMA.png)

> "Figure 1: CoRMA pipeline overview." (§1)
(한글 해설 — Stage 1 에서 privileged $`z_{t}`$ 로 교사 정책을 학습합니다. Stage 2 에서는 deployable history → $`\hat{z}_{t}`$ adapter 를 학습하고, Stage 3 에서 oracle $`z_{t}`$ 를 adapter 예측으로 대체해 fine-tune / 실로봇 배포한다는 3단 파이프라인을 한 장으로 요약합니다.)

### 아키텍처

전체는 3 단계 파이프라인입니다.

**Stage 1 — Privileged Teacher.** Isaac Lab FORGE 환경 위에서 RL-Games PPO 로 과제별 교사 정책을 학습합니다. 관측 벡터에 6D Privileged $`Z`$ 가 덧붙습니다.

$$a_{t}\sim\pi_{i}(a_{t}\mid o_{t},z_{t})$$

여기서 $`i`$ 는 과제 인덱스 (`PegInsert`, `GearMesh`, `NutThread`) 이고, $`z_{t}\in\mathbb{R}^{6}`$ 는 다음과 같이 정의됩니다.

$$z_{t}=[z_{t}^{\mathrm{onset}},z_{t}^{\mathrm{lateral}},z_{t}^{\mathrm{guided}},z_{t}^{\mathrm{dir}\text{-}x},z_{t}^{\mathrm{dir}\text{-}y},z_{t}^{\mathrm{jam}}]\in\mathbb{R}^{6}$$

> "These scores are computed from simulator contact and force dynamics and are used only during training." (§3.1)
(한글 해설 — 이 6 차원은 시뮬레이터의 접촉·force 동역학에서 산출된 점수이며, 시뮬레이션 학습 시점에만 사용됩니다. 실로봇 배포 시 oracle 은 사라지고 adapter 예측으로 대체됩니다.)

**Stage 2 — CoRMA Adapter.** 교사 rollout 을 history window $`\mathcal{D}=\{(o_{t-H+1:t},a_{t-H+1:t},z_{t},c_{t})\}`$ 로 변환합니다. $`H`$ 는 history 길이이고 $`c_{t}`$ 는 약한 force-regime 라벨입니다. adapter 는 다음과 같이 mapping 합니다.

$$\hat{z}_{t}=\phi(o_{t-H+1:t},a_{t-H+1:t})$$

내부적으로는 causal Transformer 가 learned readout token 으로 history 를 요약한 뒤 semantic head 와 contrastive head 두 갈래로 갈라집니다.

$$h_{t}=f_{\theta}(o_{t-H+1:t},a_{t-H+1:t}),\quad \hat{z}_{t}=g_{\mathrm{sem}}(h_{t}),\quad u_{t}=g_{\mathrm{nce}}(h_{t})$$

policy 가 보는 것은 $`\hat{z}_{t}`$ 뿐이고 $`u_{t}`$ 는 adapter 학습 시 표현 구조화에만 쓰입니다.

![Figure 2 — CoRMA adapter](https://arxiv.org/html/2605.22082/Adapter.png)

> "Figure 2: CoRMA adapter." (§2.3)
(한글 해설 — causal Transformer + learned readout 토큰 → 두 head 분기 구조와, force-regime positive/negative 매칭 규칙을 도식화합니다.)

**Stage 3 — Latent Injection.** fine-tuning 과 실로봇 배포에서는 oracle $`z_{t}`$ 가 제거되고 frozen adapter 가 online 으로 $`\hat{z}_{t}`$ 를 예측합니다.

$$a_{t}\sim\pi(a_{t}\mid o_{t},\hat{z}_{t})$$

> "This preserves the RMA non-cheating principle: privileged contact semantics supervise training, but deployment uses only onboard force/proprioceptive/action history." (§3.4)
(한글 해설 — RMA 의 "특권 정보는 학습 감독에만, 배포는 onboard 정보만" 원칙을 그대로 따른다는 명시. CoRMA 가 새 적응 패러다임을 제안하는 게 아니라 RMA 의 target 만 바꾼 것이라는 위치 선언입니다.)

### 학습 목표 / 손실

semantic head 는 6D Privileged $`Z`$ 를 직접 회귀합니다.

$$\mathcal{L}_{\mathrm{sem}}=\|\hat{z}_{t}-z_{t}\|_{2}^{2}$$

contrastive head 는 force-regime 라벨 기반 InfoNCE 입니다.

$$\mathcal{L}_{\mathrm{nce}}=-\log\frac{\exp(\mathrm{sim}(u_{t},u^{+})/\tau)}{\exp(\mathrm{sim}(u_{t},u^{+})/\tau)+\sum_{u^{-}\in\mathcal{N}_{t}}\exp(\mathrm{sim}(u_{t},u^{-})/\tau)}$$

여기서 $`\mathrm{sim}(\cdot,\cdot)`$ 는 cosine similarity 이고 $`\tau`$ 는 temperature 입니다. 같은 force-regime 라벨끼리 positive 이고 task identity 와 무관하게 다른 라벨이 negative 로 들어갑니다. Stage 2 통합 목표는 다음과 같습니다.

$$\mathcal{L}_{\mathrm{adapter}}=\mathcal{L}_{\mathrm{sem}}+\lambda_{\mathrm{nce}}\mathcal{L}_{\mathrm{nce}}$$

> "We use the contrastive term as a weak semantic regularizer rather than as a replacement for supervised Privileged $`Z`$ regression." (§3.3)
(한글 해설 — InfoNCE 의 역할 한정을 못 박는 문장. policy 는 어디까지나 supervised 회귀 출력 $`\hat{z}_{t}`$ 만 받고 contrastive 항은 표현을 정돈하는 정규화로만 작동합니다.)

### 학습 셋업

- **시뮬레이터** — Isaac Lab / Isaac Sim 5.0, FORGE direct RL 환경 기반. 6-DoF Franka/Panda 가정인 원본 FORGE 를 7-DoF Marvin 으로 옮기기 위해 robot-specific 제어 인터페이스만 교체했습니다.
- **RL 알고리즘** — RL-Games PPO 로 모든 시뮬레이션 policy 를 학습합니다.
- **관측** — proprioceptive, force/torque, force-threshold, previous-action 의 deployable 신호. 교사에는 여기에 6D Privileged $`Z`$ 가 덧붙고 FORGE baseline 에서는 제거됩니다.
- **실로봇 인터페이스** — Marvin 7-DoF arm + TRAC-IK 기반 Cartesian → joint 변환. CoRMA 와 FORGE 모두 동일 IK 레이어와 force sensor, verification 규칙을 공유합니다.
- **실로봇 perturbation** — 약 3 mm 의 target-position noise 를 주입해 camera-based localization 오차를 모사합니다. 온보드 카메라는 쓰지 않습니다.
- **평가** — 시뮬레이션 80 episode/조건. 실로봇 verified success 는 `insertion_verified` 신호를 `run_id` 별 max 로 집계합니다.

---

## 📊 실험 설정과 결과

### 시뮬레이션·실로봇 성공률 (Table 1)

| Task | Method | Sim Success | Real Success | Gap |
|---|---|---|---|---|
| GearMesh | CoRMA | 74/80 (92.50%) | 13/20 (65.0%) | -27.50 |
| GearMesh | FORGE | 80/80 (100.00%) | 5/20 (25.0%) | -75.00 |
| PegInsert | CoRMA | 48/80 (60.00%) | 11/22 (50.0%) | -10.00 |
| PegInsert | FORGE | 79/80 (98.75%) | 3/24 (12.5%) | -86.25 |
| NutThread | CoRMA | 73/80 (91.25%) | 16/27 (59.3%) | -31.95 |
| NutThread | FORGE | 54/80 (67.50%) | 0/20 (0.0%) | -67.50 |

> "CoRMA is not uniformly better in simulation: it underperforms FORGE on PegInsert and is slightly lower on GearMesh. However, under the same real-robot deployment interface, CoRMA retains substantially higher real success on all three tasks." (§4.3)
(한글 해설 — 시뮬레이션 성능과 실로봇 성능이 분리될 수 있다는 핵심 관찰. PegInsert·GearMesh 에서 CoRMA 는 sim 성능이 더 낮음에도 실로봇에서는 모든 과제에서 우세합니다.)

> "On NutThread, CoRMA obtains 16/27 verified real successes, while FORGE obtains 0/20 under the same verification rule." (§4.3)
(한글 해설 — verification 기준 동일성을 강조한 인용. FORGE NutThread 의 0/20 은 누락 데이터가 아니라 동일 검증 규칙 하에서의 0 입니다.)

### Stage 2 adapter 검증 (Table 2)

| Adapter | $`R^{2}`$ | Pearson | Cos-Sim | MSE |
|---|---|---|---|---|
| RMA-Conv | 0.4336 | 0.6411 | 0.6307 | 0.5664 |
| RMA-Transformer | 0.8688 | 0.9313 | 0.9151 | 0.1312 |
| CoRMA (Ours) | 0.8792 | 0.9369 | 0.9215 | 0.1208 |

> "The causal Transformer is the dominant architectural factor: replacing it with an RMA-style Conv1D adapter reduces mean validation $`R^{2}`$ from 0.8792 to 0.4336 and increases mean MSE from 0.1208 to 0.5664." (§4.4)
(한글 해설 — 기여 분해의 핵심. 성능 향상의 대부분은 causal Transformer 도입이 가져왔고, InfoNCE 는 그 위에 작은 정규화 이득을 더하는 구조라는 명시입니다.)

> "The force-regime contrastive objective gives a smaller but consistent gain over Transformer-MSE, improving mean $`R^{2}`$ from 0.8688 to 0.8792 and reducing mean MSE from 0.1312 to 0.1208." (§4.4)
(한글 해설 — InfoNCE 자체의 한계 효과 (marginal gain) 수치. 큰 폭의 개선이 아니라는 점을 저자가 직접 인정합니다.)

### Hyperparameter ablation 요점 (Appendix C, Table 4)

- 가장 좋은 설정은 large Transformer ($`d=256`$, 4 layers) + NCE $`\lambda=0.01`$ 로 validation $`R^{2}=0.9044`$, MSE $`0.0956`$ 를 달성.
- NCE weight 를 0.5 등 크게 키우면 $`R^{2}`$ 가 0.6799 까지 떨어져, contrastive 항은 dominant 가 아닌 약한 regularizer 로만 써야 한다는 결론을 뒷받침합니다.

### Wilson 95% 신뢰구간 (Table 3, Appendix B)

| Task | Method | Trials | Verified Success | Wilson 95% CI |
|---|---|---|---|---|
| GearMesh | CoRMA | 20 | 13/20 (65.0%) | [43.3, 81.9]% |
| GearMesh | FORGE | 20 | 5/20 (25.0%) | [11.2, 46.9]% |
| PegInsert | CoRMA | 22 | 11/22 (50.0%) | [30.7, 69.3]% |
| PegInsert | FORGE | 24 | 3/24 (12.5%) | [4.3, 31.0]% |
| NutThread | CoRMA | 27 | 16/27 (59.3%) | [40.7, 75.5]% |
| NutThread | FORGE | 20 | 0/20 (0.0%) | [0.0, 16.1]% |

> "Wilson 95% confidence intervals quantify uncertainty from the finite number of real-robot trials." (§Appendix B)
(한글 해설 — 과제당 시도가 수십 회 수준이라 신뢰구간이 꽤 넓다고 논문은 명시합니다. CoRMA 와 FORGE 의 PegInsert / GearMesh CI 가 겹치지 않는 반면 NutThread 차이는 표본 한계 안에서 해석된다는 단서가 함께 붙습니다.)

---

## ⚖️ 한계

- 평가는 PegInsert / GearMesh / NutThread 라는 *related* assembly family 안에서의 재사용을 측정한 것이며, held-out unseen task generalization 은 포함되지 않습니다. 논문도 task-family-level meta-adaptation 으로 한정해 해석합니다.
- 실로봇은 FORGE 가 원래 설계된 6-DoF Franka/Panda 가 아니라 7-DoF Marvin arm 이고 Cartesian target 은 TRAC-IK 로 풀립니다. IK 수렴, joint-limit, tracking error, servo timing, 컴플라이언스가 실성공률에 동시에 영향을 줍니다.
- Real2Sim calibration 은 수행되지 않았습니다. 남은 sim-to-real 격차의 원인 (dynamics, contact compliance, friction, sensing, latency, controller timing) 이 모델이 아니라 환경 mismatch 에 있을 가능성을 논문은 명시합니다.
- force pipeline 은 기본 smoothing 만 사용하며 dedicated state estimator 가 없습니다. contact-onset event 를 살리면서 노이즈를 줄이는 필터링이 future work 으로 남아 있습니다.
- 실로봇 시도 수가 과제당 수십 회 수준이라 reliability certification 이 아니라 controlled deployment evidence 로 봐야 합니다.
- NutThread 의 CoRMA vs FORGE 격차 (16/27 vs 0/20) 는 가장 큰 효과 크기이지만, 동시에 실제 접촉·구동·verification mismatch 영향이 가장 큰 과제라 논문도 신중한 해석을 권합니다.

---

## ♻️ 재현성

- **코드/체크포인트** — 본문·부록 모두에서 코드/모델 공개에 대한 명시는 없습니다.
- **데이터** — 시뮬레이션 데이터는 Isaac Lab + FORGE 환경에서 재생성 가능하나 실로봇 trial 로그 (`insertion_verified`, run_id 그룹화) 공개 여부는 명시되지 않습니다.
- **하드웨어** — 시뮬레이션은 Isaac Lab / Isaac Sim 5.0, 실로봇은 7-DoF Marvin arm + TRAC-IK. FORGE 원본 6-DoF 가정과 다르므로 동일 비교를 위해선 동일 IK 스택 / force sensor 가 필요합니다.
- **재현 비용** — RL-Games PPO + GPU-parallel 환경이라 PPO 학습 자체는 표준 lerobot 외 의존성 (Isaac Lab) 이 필수입니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **[P3](#ref-P3) — Hand-level System0 Module (RL-scoped)** : 가장 직접 연결됩니다. CoRMA 는 P3 의 핀 논문인 [RMA](https://arxiv.org/abs/2107.04034) 의 contact-rich assembly 변형이며, [D17](#ref-D17) (System0 RL policy spec) 의 reward 와 privileged 정보 정의, [D18](#ref-D18) (System0 sim2real) 의 RMA-family teacher-student 라인을 바로 건드립니다. 다만 PROBE 의 System0 가정 (post-grasp 안정화, slip 억제) 과 CoRMA 의 target (assembly insertion 의 contact regime) 은 task 자체가 다르고, P3 의 RMA 의존을 *어떻게* 응용할지에 대한 새로운 예시에 가깝습니다.
- **[P1](#ref-P1) — Heterogeneous Body/Hand Action Expert (보조)** : CoRMA 가 정의하는 6D semantic latent 는 [D4](#ref-D4) (Body↔Hand 정보 공유) 의 v1 인 FiLM 모듈이 받는 정보의 *공급 형태* 와 유사한 발상입니다. raw simulator parameter 대신 의미 단위 latent 를 policy 에 주입한다는 점이 P1 의 hand expert 에 contact 단계 latent 를 conditioning 으로 넣는 가설과 결이 같습니다. 단, architecture 가 직접 일치하지는 않습니다.
- **in-hand rotation 실로봇 데모 분석 시점** : CoRMA 가 보여주는 "sim 100% 가 real 12.5% 로 떨어지는" 격차는 PROBE 가 실로봇 데모 진입 시 마주칠 sim-to-real 시나리오의 정확한 reference 입니다. P3 의 D18 deferred priority (RMA-style Phase-3 RL fine-tuning, static-friction-aware DR) 가 실로봇 데모 직전에 활성화되는 트리거와 바로 닿습니다.
- **§10 경쟁자 함의** — `RMA family` 는 P3 의 anti-topic 면제 대상이므로 CoRMA 는 anti-topic 위반이 아닙니다. assembly task family (PegInsert / GearMesh / NutThread) 는 PROBE 의 in-hand rotation / tool articulation 과 거리가 있으나, force-dominant contact regime 추론이라는 메커니즘은 그대로 차용 가능합니다.

| Code | Meaning |
|------|---------|
| <a id="ref-P1"></a>**P1** | Heterogeneous Body/Hand Action Expert (pillar) |
| <a id="ref-P3"></a>**P3** | Hand-level System0 Module — RL-scoped contact stabilization (pillar) |
| <a id="ref-D4"></a>**D4** | Body↔Hand information sharing — v1 FiLM with $`a_{b}`$ → ($`\gamma,\beta`$); cross-attn deferred |
| <a id="ref-D17"></a>**D17** | System0 RL policy spec — PPO, contact reward, hand-crafted v1; Eureka/DrEureka deferred |
| <a id="ref-D18"></a>**D18** | System0 sim2real — RMA-family teacher-student; static/dynamic friction split DR |

---

## ✨ 핀 논문 대비 델타

- **vs. [RMA (Kumar et al., 2021)](https://arxiv.org/abs/2107.04034) — P3 핀, 원형** : RMA 는 raw simulator extrinsic vector 를 privileged target 으로 두고 locomotion 의 proprioceptive history 를 입력으로 받는 Conv1D adapter 를 학습합니다. CoRMA 는 privileged target 을 6D *semantic* contact context 로 바꾸고 입력 modality 를 locomotion proprio 가 아닌 contact-rich assembly 의 force + proprio + action history 로, 인코더를 causal Transformer 로 교체했습니다. 새로움의 핵심은 *target 의 의미화* 이지 RMA 골격 자체가 아닙니다.
- **vs. [HORA (Qi et al., 2022)](https://arxiv.org/abs/2210.04887) — P3 핀, 인핸드** : HORA 는 in-hand rotation 에서 privileged 정보를 *촉각* 으로 distill 합니다. 입력 modality (촉각) 와 target task (회전) 가 다르고, CoRMA 는 assembly insertion + force/torque 라는 다른 평면을 다룹니다. 두 논문은 "privileged 정보를 deployable 으로 변환" 이라는 큰 아이디어를 공유할 뿐, target latent 의 의미 단위 정의는 CoRMA 가 새 기여입니다.
- **vs. [AnyRotate](https://arxiv.org/abs/2405.07391) — D17 reward 직접 reference** : AnyRotate 는 reward term 의 직접 reference 이지만 task (회전) 와 modality (촉각) 가 다릅니다. CoRMA 는 reward 가 아니라 *adaptation latent 의 표현 학습* 을 손본 쪽이라 바로 충돌하지 않고 보완 관계가 됩니다.
- **vs. [Static Friction Sim2Real](https://arxiv.org/abs/2503.01255) — D18 DR 핀** : CoRMA 는 static/dynamic friction split DR 을 따로 도입하지 않고, 대신 의미 단위 contact latent 로 sim-to-real 격차가 줄어드는 경로를 택합니다. PROBE 의 v1 D18 (friction split + RMA-family) 과는 *다른 단면* 에서 같은 문제를 공격하는 사례이며, 둘은 결합 가능합니다.
- **vs. [Contact-Aware Neural Dynamics](https://arxiv.org/abs/2601.12796) — D18 (tool articulation 단계) deferred** : 학습된 contact correction 으로 sim-to-real 격차를 메우는 아이디어와 비교하면, CoRMA 는 *correction* 이 아니라 *적응 latent 를 통한 conditioning* 으로 격차를 줄이려 합니다. 보완 관계로 해석할 수 있습니다.

---

## ⚙️ 의사결정 함의

본 논문이 옳다면 PROBE 의 System0 파이프라인에서 다음이 바뀝니다.

- **D17 privileged 정보 정의 후보 추가** — 현재 D17 의 privileged 정보는 따로 정의돼 있지 않습니다 (PPO 의 state 는 tactile + proprio + history 로만 기재). CoRMA 를 따른다면 in-hand rotation 의 privileged target 을 raw friction / mass / 접촉 점 같은 raw extrinsic 이 아니라 *의미 단위 contact context* 로 정의하는 옵션이 자연스러운 후보입니다. 예: `slip_onset`, `grasp_stable`, `regrasp_needed`, `contact_loss_imminent` 차원의 4–6D latent.
- **D17 RL state 에 adapter 출력 주입 인터페이스** — System0 의 입력 (`state`) 정의에 "frozen adapter 가 산출한 $`\hat{z}_{t}`$" 라는 차원도 검토 대상으로 올립니다. AnyRotate reward 는 그대로 두되, RMA Phase-3 가 활성화될 때 latent injection 인터페이스를 어떤 식으로 둘지가 구체적 config 결정 사항입니다.
- **D18 adapter 아키텍처 디폴트 후보 변경** — 현재 D18 v1 은 RMA-family teacher-student 만 명시하고 인코더는 미지정입니다. Table 2 의 $`R^{2}`$ 0.43 → 0.87 격차가 Conv1D 디폴트를 causal Transformer 로 바꾸는 결정의 직접 근거가 됩니다. config 키 후보: `system0_adapter.arch = "causal_transformer"`, `system0_adapter.d_model = 256`, `system0_adapter.n_layers = 4`.
- **D18 보조 손실 후보** — semantic regression + 약한 InfoNCE 의 조합을 v1 후보로 들이고, contrastive weight 는 $`\lambda_{\mathrm{nce}}\in[0.01,0.05]`$ 범위로 좁힙니다. 더 큰 값이 회귀 성능을 무너뜨린다는 Table 4 (D6, D4, A3 row) 증거가 있습니다.
- **D18 sim2real 진단 지표** — 실로봇 oracle 이 없는 상황에서 adapter 정확도를 바로 측정할 수 없다는 CoRMA 의 한계는 PROBE 에도 그대로 적용됩니다. compensated wrench / force onset / EE motion 과의 정합성 같은 *대리 진단* 을 evaluation log 에 포함하는 것이 metric 정의 단계의 검토 대상으로 둡니다.

특별히 모호하지 않은 구체 결정은 위 다섯 가지이며, "InfoNCE 의 효과는 작다" 는 ablation 증거를 무시하고 contrastive 를 dominant 로 쓰는 설계는 따로 배제할 근거가 됩니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **Task mismatch — assembly insertion vs in-hand rotation/tool articulation** : CoRMA 의 6D semantic latent (`onset, lateral, guided, dir-x, dir-y, jam`) 는 peg–hole / thread 같은 directional contact 에 맞춰진 어휘입니다. PROBE 의 첫 데모인 in-hand cube rotation 은 다지 접촉 + 회전이라 "lateral engagement" 나 "guided transition" 의 의미가 그대로 옮겨가지 않을 가능성이 큽니다. 가장 싼 sanity check: PROBE 의 회전 시뮬레이션에서 4-regime force-label (`free / first_contact / guided / jam` 대신 `free / contact / slip / drop`) 이 history 만으로 분리 가능한지 InfoNCE 없는 단순 분류기로 먼저 확인.
- **Modality mismatch — F/T sensor 중심 vs Sharpa Deform Map 촉각** : CoRMA 의 deployable evidence 는 6-axis wrench 와 force-threshold 입니다. PROBE 의 System0 입력은 vision-excluded *tactile* + proprio (D15) 로, 320×240 Deform Map 이 우세합니다. 같은 의미 latent 라도 sensor 차원에서 추론 가능한지는 별개 문제이고, adapter 입력에 tactile feature 를 어떤 형식으로 끼울지가 큰 미지수입니다.
- **Arm-specific 변수** : CoRMA 가 보고하는 sim-to-real 격차에는 Marvin + TRAC-IK 의 IK 수렴 / joint-limit / tracking error 가 섞여 있어 CoRMA 자체의 효과를 분리하기 어렵습니다. PROBE 가 generic 7-DoF arm 가정으로 따라가더라도, IK 스택이 다르면 동일 격차 절감 효과가 나타난다는 보장은 없습니다.
- **NutThread 의 0/20 baseline** : FORGE NutThread real success 가 0/20 인 것은 CoRMA 우세를 가장 크게 보이는 row 이지만, 동시에 verification 규칙·threading 동역학 mismatch 가 가장 큰 과제입니다. PROBE 가 이 결과를 일반화 근거로 삼기 전에 verification rule 의 sensitivity 가 먼저 검토 대상이 됩니다.
- **InfoNCE 가 노이즈를 정렬할 위험** : force-regime 라벨이 weak supervision 이라 noisy label 환경에서 임베딩을 잘못된 축으로 정렬할 가능성이 있습니다. PROBE 가 4 라벨을 어떻게 정의하느냐에 따라 동일한 risk 가 옮겨갑니다. 라벨 정의의 robustness 를 leave-one-trajectory-out 으로 점검하는 것이 권장 절차입니다.

---

## 💡 컨텍스트 제안

- §8.3 P3 핀 후보 보충 — CoRMA 자체를 P3 핀으로 올리는 것은 **권하지 않습니다**: task 가 PROBE 의 in-hand rotation / tool articulation 과 거리가 있고, 핀 한도 (≤8) 안에서 HORA · AnyRotate · RMA · Static Friction Sim2Real 의 우선순위가 더 높습니다. 다만 §10 (Competitor / Kindred Monitoring) 의 *RMA-family 응용 사례* 또는 D18 의 **Note** 로 "CoRMA = RMA target 의 의미화 사례 ([arXiv:2605.22082](https://arxiv.org/abs/2605.22082))" 한 줄 인용을 추가하면 D18 v2 (privileged 정보 형태 변경 옵션) 의 트리거 증거로 활용할 수 있습니다.
- D18 **Deferred (priority)** 항목에 "privileged target 의 semantic-encoding 화 (CoRMA-style)" 한 줄을 추가 후보로 검토 (트리거는 초기 sim ablation 에서 raw extrinsic 기반 RMA adapter 의 $`R^{2}`$ 가 0.5 미만일 때).
- §10.2 (Bounded RL-in-VLA precedents) 와 §10.3 (Architectural siblings) 에는 바로 해당하지 않으므로 신규 carryover 는 필요 없습니다.

---
