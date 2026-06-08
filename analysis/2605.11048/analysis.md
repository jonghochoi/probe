# Paper Analysis — ForceFlow: Learning to Feel and Act via Contact-Driven Flow Matching

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | ForceFlow: Learning to Feel and Act via Contact-Driven Flow Matching |
| 저자 | Shuoheng Zhang, Yifu Yuan, Hongyao Tang, Yan Zheng, Qiaojun Yu, Pengyi Li, Guowei Huang, Helong Huang, Xingyue Quan, Jianye Hao (Tianjin University · Huawei Noah's Ark Lab · Shanghai AI Lab) |
| 링크 | [arXiv:2605.11048](https://arxiv.org/abs/2605.11048) |
| 발행일 / 버전 | 2026-05-11 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-05-26 |
| 관련 Pillar | P2, P3 |
| 태그 | force, flow-matching, tactile |

---

## 🧭 한 줄 요약 (TL;DR)

ForceFlow 는 force-torque 신호를 AdaLN 으로 전 layer 에 주입하는 비대칭 multimodal fusion + flow matching 정책에, VLM pointing 으로 접근을 처리하고 도착 시점에 force-주도 stage 로 넘겨주는 V2F handover 를 결합해 여섯 개 contact-rich 실로봇 과제에서 ForceVLA 대비 평균 SR 을 45% → 81.67% 로 끌어올린 force-aware reactive 프레임워크입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — Contact-rich 조작에서 vision-centric IL 정책 (ACT, Diffusion Policy, π0.5, OpenVLA) 이 종이 두께·스프링 강성·서브밀리미터 공차 같은 visually-ambiguous contact dynamics 에 부딪쳐 무너지는 문제. 끝점 위치는 맞춰도 접촉 force 를 제대로 규제하지 못합니다.
- **기존 접근의 한계** — Force/torque 를 관측에 추가한 기존 framework (ForceVLA, Reactive Diffusion Policy, TacDiffusion) 들은 저차원·고주파인 force 신호가 고차원 visual feature 에 의해 학습 중 *masking* 되는 modal-masking 현상을 겪습니다. 물리적 generalization 과 공간 generalization 을 하나의 end-to-end policy 안에서 동시에 풀려다 둘 다 깨뜨립니다.
- **본 논문의 가설** — Force 를 layer 마다 statistic 을 modulate 하는 *global regulatory signal* 로 비대칭으로 주입하고 모션과 next-step contact force 를 *joint* 로 예측하게 만들면 force–motion coupling 을 내재화시킬 수 있다는 것입니다. 동시에 spatial generalization 은 VLM pointing 으로 풀고 contact regulation 은 force-aware flow matching 으로 *드러내 놓고 나누면* 두 generalization 이 서로의 발목을 잡지 않습니다.
- **왜 지금 중요한가** — π0.5 / OpenVLA / ForceVLA 같은 force-aware VLA 가 쏟아지는 시점에서 "force 를 어떻게 fuse 하는가" 가 architectural-design 문제로 부각되었습니다. ForceVLA 가 같은 관측 셋업 (multi-view RGB + EE pose + 6D F/T) 의 공식 baseline 위치를 차지하면서 비교 기준점이 합의된 상태입니다.

---

## 🧩 핵심 기여

- 비대칭 multimodal fusion 아키텍처: force history + proprioception 을 AdaLN 으로 DiT 전 layer 에 *global* 로 주입하고 multi-view 이미지는 cross-attention 으로 *local* 로 붙이는 분리 설계로 modal masking 을 직접 겨냥했습니다.
- Joint prediction paradigm: motion command $`\Delta\mathbf{p}_{t}`$ 와 next-step contact force $`\hat{\mathbf{f}}_{t+1}`$ 를 한 hybrid action $`\mathbf{a}_{t}=[\Delta\mathbf{p}_{t},\hat{\mathbf{f}}_{t+1}]`$ 로 묶어 flow matching 으로 함께 학습. 실행 시점에서는 motion 만 보내고 force 예측은 학습 신호로만 쓰입니다.
- V2F (Vision-to-Force) handover: VLM 이 픽셀 좌표 $`(\hat{u},\hat{v})`$ 를 예측 → depth + intrinsics 로 3D waypoint deprojection → motion planner 가 도달 → 위치 기반 strict trigger 로 ForceFlow 로 인계. spatial 과 contact generalization 을 task 레벨에서 분리합니다.
- 여섯 개 real-world contact-rich 과제 (Stamp / Plug / Press / USB Insert / Clean Whiteboard / Clean Vase) 에서 평균 SR 45% (ForceVLA) → 81.67% (ForceFlow) 의 *+37%* 상승과 Force Cost 평균 23.31 N → 8.23 N 감소를 동시에 달성했습니다 (Table 1, 2).
- Ablation 으로 "10-step force history 가 SR 의 결정 요인 (85% → 55% drop), active force prediction 은 compliance regularizer (Force Cost 10.61 → 12.52 N)" 라는 기여 분해를 제시했습니다 (Table 5).

---

## 🔑 기술 키워드

- **Flow Matching** — diffusion sampling 보다 *deterministic ODE path generation* 으로 latency 가 낮고 trajectory 가 안정적인 생성 모델 백본. 본 논문에서 closed-loop contact control 의 backbone 으로 선택된 이유는 고주파 force feedback 에 실시간 응답이 필요해서입니다.
- **Asymmetric multimodal fusion** — 모달리티별 *주입 경로* 자체를 비대칭으로 가르는 fusion. force 는 AdaLN 으로 글로벌하게, vision 은 cross-attn 으로 selective 하게 들어가는 식의 "어디서 어떻게 들어가는가" 분리입니다.
- **AdaLN (Adaptive Layer Normalization)** — 조건 벡터로부터 $`\gamma,\beta`$ 를 만들어 LayerNorm 출력의 통계를 modulate 하는 conditioning 방식 (Peebles & Xie 2023 DiT). force 가 layer 마다 feature 분포를 *지속적으로* 끌어당기는 정규화 신호가 됩니다.
- **Modal masking** — 고차원 모달리티 (vision) 가 end-to-end 학습을 지배하면서 저차원 모달리티 (force) 의 학습 신호가 무력화되는 multimodal 학습 병리. Wang 2020 / Wu 2022 / Dong 2025 에서 정식화된 개념입니다.
- **V2F (Vision-to-Force) handover** — VLM 이 공간 localization 까지 끝낸 뒤 위치 기준 strict trigger 로 force-주도 정책에 제어권을 넘기는 task-level 계층화. "보는 단계 → 느끼는 단계" 를 따로 나눈 설계입니다.
- **Joint prediction** — action 과 다음 step contact force 를 같은 출력으로 예측해 force–motion 상관을 internalize 시키는 학습 목표. 실행 시점에서는 force 예측이 직접 제어에 쓰이지 않고 *active compliance regularizer* 역할만 합니다.
- **Force history window ($`H_{\text{force}}`$)** — 즉시 측정값이 노이즈에 흔들리는 것을 막기 위해 길이 10 의 force-torque 시계열을 정책 입력으로 유지. ablation 에서 1-step 으로 줄이면 SR 이 85% → 55% 로 무너집니다.
- **Force Fidelity (MAE Cost, $`\mathcal{J}_{\text{force}}`$)** — 정책이 만든 접촉 force 와 expert reference 사이 mean absolute error. short-horizon 은 peak force, continuous 는 평균 effective force 로 task-dependent 하게 정의됩니다.
- **Pointing mechanism** — natural-language instruction + global view 로부터 VLM 이 target keypoint 의 픽셀 $`(u,v)`$ 를 회귀하는 VQA-style 지시. spatial generalization 을 *순수 semantic localization* 문제로 격리합니다.

---

## 🔬 방법론

### 직관

저자들이 깔아두는 그림은 단순합니다. Contact-rich 조작은 "보는 단계 (vision-dominant approach)" 와 "느끼는 단계 (touch-dominant interaction)" 가 본질적으로 다른 모달리티에 의존합니다. 한 정책 안에 욱여넣으면 force 가 vision 에 묻히고 spatial generalization 과 contact generalization 이 서로의 학습을 망칩니다.

> "Coupling both within a single end-to-end policy causes mutual performance degradation." (§3.2)
(한글 해설 — V2F handover 의 설계 동기를 한 문장에 못박는 anchor. 공간 일반화와 접촉 일반화는 메커니즘이 다르므로 task 레벨에서 분리해야 한다는 주장입니다.)

> "force signals are low-dimensional, high-frequency, and strongly temporally structured, making them easily overshadowed by high-dimensional visual features during end-to-end training" (§1)
(한글 해설 — modal masking 을 정면으로 명명한 anchor 문장. AdaLN 으로 force 를 *globally* 주입하는 비대칭 fusion 설계의 출발점입니다.)

여기서 두 가지 결정이 따라 나옵니다. 첫째, force 는 모든 layer 의 통계를 modulate 하는 글로벌 신호로 주입해 학습 중에도 사라지지 않게 만든다 (AdaLN). 둘째, action 만 예측하지 말고 next-step force 까지 같이 예측하게 해서 force–motion 결합을 학습 목표로 강제한다 (joint prediction).

![Figure 2 — ForceFlow Architecture](https://arxiv.org/html/2605.11048/x2.png)

> "Figure 2: The ForceFlow Architecture." (§3.3)
(한글 해설 — Stage 1 은 VLM pointing → 3D waypoint deprojection → motion planner 의 V2F approach 경로, Stage 2 는 force history + proprio → AdaLN, 듀얼 뷰 RGB → cross-attn 으로 DiT 에 들어가 hybrid action $`[\Delta\mathbf{p},\hat{\mathbf{f}}]`$ 를 flow matching 으로 생성하는 contact 경로. 두 stage 가 명시적으로 분리되어 있다는 사실이 이 그림의 핵심입니다.)

### 아키텍처

전체는 두 stage 의 계층 정책입니다.

**Approach Stage — VLM Pointing + V2F Handover.** 글로벌 카메라 뷰 $`I_{\text{fix}}`$ 와 자연어 instruction 을 받은 VLM 이 target contact keypoint 의 픽셀 좌표 $`(\hat{u},\hat{v})`$ 를 회귀합니다. expert demonstration 의 초기 프레임에 2D ground truth $`(u_{\text{gt}},v_{\text{gt}})`$ 를 수동 annotation 한 VQA 형태 데이터로 VLM 을 fine-tune 합니다. 추론 시에는 예측된 픽셀이 depth + camera intrinsics 로 robot base frame 의 3D approach waypoint 로 deproject 됩니다. motion planner 가 그 점까지 끝점을 옮긴 뒤 *positional criterion* 만으로 V2F handover 가 발화해 ForceFlow 로 제어권을 넘깁니다.

**Contact Stage — Asymmetric Multimodal Fusion + Flow Matching.** 시점 $`t`$ 의 관측은
$`\mathcal{O}_{t}=\{I_{\text{arm},t},I_{\text{fix},t},\mathbf{q}_{t},\mathbf{F}_{t}^{\text{hist}}\}`$ 로 듀얼 뷰 RGB, proprioception $`\mathbf{q}_{t}\in\mathbb{R}^{d_{q}}`$, force-torque 히스토리 $`\mathbf{F}_{t}^{\text{hist}}\in\mathbb{R}^{H\times d_{f}}`$ 로 구성됩니다 ($`H=10`$, $`d_{f}=6`$). 정책 $`\pi_{\theta}(\mathbf{a}_{t}\mid\mathcal{O}_{t})`$ 가 길이 $`H^{a}=64`$ 의 action chunk 를 예측합니다.

관측은 두 경로로 비대칭 분기됩니다.

- **Force-Centric Vector Condition $`c_{\text{vec}}`$.** $`\mathbf{F}_{t}^{\text{hist}}`$ 와 $`\mathbf{q}_{t}`$ 가 force/low-dim encoder (2-layer MLP, 출력 256) 로 통합 글로벌 벡터가 된 뒤 *Diffusion Transformer (DiT)* 의 모든 layer 에 AdaLN 으로 주입됩니다.

> "By modulating feature statistics globally at every network layer, force signals act as a persistent regulatory constraint rather than being marginalized." (§3.3)
(한글 해설 — AdaLN 을 선택한 핵심 근거. force 가 layer 마다 feature 통계를 끌고 다니므로 학습 중 visual 신호에 가려지지 않는다는 주장입니다.)

- **Visual Sequence Condition $`c_{\text{seq}}`$.** ResNet-18 듀얼 뷰 인코더의 spatial feature 를 *pooling 없이* 시퀀스로 보존해 cross-attention 으로 DiT 에 결합합니다 (출력 차원 512).

### 학습 목표 / 손실

Action 은 hybrid space $`\mathbf{a}_{t}=[\Delta\mathbf{p}_{t},\hat{\mathbf{f}}_{t+1}]`$ 에서 정의되고 (motion 7D + next force 6D = 13D), flow matching 으로 학습됩니다. expert hybrid action $`\mathbf{a}_{t}^{0}\sim p_{\text{data}}(\mathbf{a})`$ 와 표준 가우시안 prior $`\mathbf{a}_{t}^{1}\sim\mathcal{N}(0,\mathbf{I})`$ 사이를 잇는 선형 probability path 가
$`\mathbf{a}_{t}^{k}=(1-k)\mathbf{a}_{t}^{0}+k\mathbf{a}_{t}^{1}`$, target drift 는 $`\mathbf{u}_{t}^{k}=\mathbf{a}_{t}^{1}-\mathbf{a}_{t}^{0}`$ 로 잡힙니다. 신경 velocity field $`v_{\theta}`$ 는 다음 손실로 학습합니다.

$$\mathcal{L}_{\text{FM}}(\theta)=\mathbb{E}_{k,\mathbf{a}_{t}^{0},\mathbf{a}_{t}^{1}}\left\|v_{\theta}(\mathbf{a}_{t}^{k},k,c_{\text{vec}},c_{\text{seq}})-\mathbf{u}_{t}^{k}\right\|^{2}$$

추론은 $`k=1\to 0`$ 으로 ODE $`d\mathbf{a}_{t}^{k}=v_{\theta}(\mathbf{a}_{t}^{k},k,c_{\text{vec}},c_{\text{seq}})\,dk`$ 를 결정론적 numerical solver 로 풉니다.

> "At execution time, only the motion command $`\Delta\mathbf{p}_{t}`$ is sent to the robot controller; the force prediction $`\hat{\mathbf{f}}_{t+1}`$ serves as a joint training objective that encourages the network to internalize the coupling between force and motion, rather than directly participating in low-level force control." (§3.3)
(한글 해설 — joint prediction 이 *학습 신호* 일 뿐 실행 force 제어에는 직접 개입하지 않는다는 점을 못박는 anchor. ablation 에서 force prediction 을 빼면 Force Cost 가 올라가지만 SR 하락은 작다는 결과와 정확히 들어맞습니다.)

평가 지표는 두 가지로, Success Rate (각 task 20 trial) 와 Force Fidelity 입니다. Force Fidelity 는

$$\mathcal{J}_{\text{force}}=\frac{1}{N}\sum_{i=1}^{N}\left|\hat{F}_{\text{policy}}^{(i)}-F_{\text{expert}}\right|$$

로 정의되며 short-horizon contact 에서는 $`\hat{F}=\max_{t}\|\mathbf{f}_{t}\|`$ (peak force), continuous contact 에서는 $`\|\mathbf{f}_{t}\|>5\text{N}`$ 구간의 평균 effective force 로 task-dependent 하게 계산됩니다.

### 학습 셋업

하드웨어는 6-DoF UFactory xArm6 + 1-DoF gripper, 글로벌은 Intel RealSense L515, wrist 는 D435 입니다. 30 Hz teleoperation (SpaceMouse / Quest Pro) 으로 task 당 50–100 demonstration 을 수집해 듀얼 뷰 $`320\times 240`$ RGB + 7D proprio (6D pose + 1D gripper) + 10-step F/T history 를 동기 저장합니다. DiT 백본은 model dim 384, depth 12, head 6, ResNet-18 인코더 듀얼 뷰 (각 256), force encoder $`(H_{\text{force}}\times 6)\to 128`$. 학습은 RTX 4090 ×4 / 48 CPU / 283 GB RAM 노드에서 AdamW ($`\beta_{1}=0.9,\beta_{2}=0.999`$, weight decay 0.01), cosine LR (시작 $`1\times 10^{-4}`$), batch 64, gradient clip $`\|\nabla\|=1.0`$, bf16-mixed, 100k step (task 당 8–10시간) 로 진행됩니다 (Table 6).

---

## 📊 실험 설정과 결과

여섯 개 실로봇 과제는 두 카테고리로 나뉩니다. Short-Horizon Contact (Stamp / Plug / Press / Insert) 는 정확한 접촉 확립을, Continuous Contact (Clean Whiteboard / Clean Vase) 는 일정 normal force 유지를 요구합니다.

| Method | Stamp | Plug | Press | Insert | Clean WB | Clean Vase | Avg. |
|---|---|---|---|---|---|---|---|
| $`\pi_{0.5}`$ | 0% | 60% | 30% | 45% | 10% | 0% | 24.17% |
| ACT | 0% | 30% | 5% | 0% | 15% | 0% | 8.33% |
| Diffusion Policy | 0% | 40% | 20% | 50% | 75% | 0% | 30.83% |
| ForceVLA | 20% | 70% | 65% | 15% | 100% | 0% | 45% |
| ForceFlow (w/o Force) | 20% | 75% | 0% | 40% | 100% | 30% | 44.17% |
| **ForceFlow (Ours)** | **85%** | **90%** | **90%** | **60%** | **100%** | **65%** | **81.67%** |

> "ForceFlow achieves an average success rate of 81.67%, significantly outperforming the best baseline (ForceVLA, 45%)." (§4.2, Table 1)
(한글 해설 — vision-centric ($`\pi_{0.5}`$ / ACT / DP) 는 종이 두께·스프링 강성 등 visually-ambiguous 신호 앞에서 0–30% SR 로 무너집니다. force-aware ForceVLA 도 곡면 Clean Vase 에서 0% 입니다. ForceFlow 만 곡면 65%, USB 60% 를 잡아냅니다.)

Force Fidelity 도 일관되게 우위입니다.

| Method | Stamp | Plug | Press | Insert | Clean WB | Clean Vase | Avg. (N) |
|---|---|---|---|---|---|---|---|
| $`\pi_{0.5}`$ | 31.99 | 21.41 | 17.39 | 50.89 | 11.93 | 7.87 | 23.58 |
| ACT | 31.86 | 25.54 | 31.81 | 38.71 | 11.91 | 30.45 | 28.38 |
| Diffusion Policy | 32.26 | 15.79 | 24.86 | 23.85 | 8.22 | 23.56 | 21.42 |
| ForceVLA | 30.03 | 9.59 | 30.94 | 37.82 | 20.16 | 11.29 | 23.31 |
| ForceFlow (w/o Force) | 30.03 | 13.36 | 37.50 | 34.75 | 7.16 | 13.24 | 22.67 |
| **ForceFlow (Ours)** | **10.61** | **3.58** | **5.03** | **21.79** | **4.59** | **3.76** | **8.23** |

> "The average Force Cost drops from the 20–30 N range of vision-dominant models to 8.23 N." (§4.3)
(한글 해설 — instantaneous 접촉 (Stamp / Plug / Press) 에서 50% 이상 감소가 두드러집니다. SR 만 보면 ForceFlow (w/o Force) 와 ForceVLA 가 비슷해 보여도 Force Cost 차이는 두 배 이상이라, "성공해도 force 분포는 expert 와 다르다" 는 점을 분리해서 드러내는 metric 입니다.)

OOD generalization 도 두 축으로 검증되었습니다.

| Physical OOD (Table 3) | Press | Clean WB | Clean Vase |
|---|---|---|---|
| $`\pi_{0.5}`$ / ACT / DP | 0% | 0% | 0% |
| ForceVLA | 40% | 90% | 0% |
| **ForceFlow** | **80%** | **100%** | **60%** |

| Spatial OOD (Table 4) | Press | Plug | Clean WB |
|---|---|---|---|
| All baselines incl. ForceFlow (no V2F) | 0% | 0% | 0% |
| **ForceFlow + V2F** | **40%** | **10%** | **50%** |

> "Without semantic guidance, low-level policies (including standalone baselines) fail to locate objects in OOD regions." (§4.4)
(한글 해설 — Spatial 분포가 train 과 disjoint 한 영역에서는 ForceFlow 단독도 0% 이지만 V2F 가 결합되면 다시 살아납니다. 이 결과가 "spatial 은 VLM, contact 는 force policy" 분리의 정당화입니다.)

Ablation (Stamp, Table 5):

| Variant | SR | Cost (N) |
|---|---|---|
| w/o Force History (1-step) | 55% | 15.50 |
| w/o Force Prediction | 80% | 12.52 |
| w/o Both | 40% | 18.21 |
| **ForceFlow (Full)** | **85%** | **10.61** |

> "Temporal force history proves decisive for task success. … active force prediction acts as a compliance regularizer." (§4.5)
(한글 해설 — 10-step history 가 SR 결정 요인 (85→55), prediction head 는 Force Cost 정밀화 (10.61→12.52). 둘 다 빼면 40% 로 시너지가 무너집니다.)

![Figure 6 — Predicted vs measured force](https://arxiv.org/html/2605.11048/x6.png)

> "Figure 6: Comparison of Predicted and Measured Forces. Alignment between the predicted (red) and measured ground truth (blue) contact forces. Shaded areas represent prediction error, demonstrating high temporal fidelity during interaction." (§4.3)
(한글 해설 — joint prediction 이 학습 신호로만 쓰이는데도 predicted 곡선이 실측에 시간적으로 정렬된다는 정성 결과. 모델이 force–motion 결합을 실제로 internalize 했다는 주장의 증거 그림입니다.)

---

## ⚖️ 한계

- 저자 명시: "the current framework relies on high-fidelity force/torque sensors, which may restrict its deployment on low-cost robotic platforms." (§5) — 6D F/T 센서가 없는 저가 플랫폼으로 가는 이식이 약점.
- 저자 명시: V2F switching 이 *strict positional criterion* 만으로 발화하기에 적응형 전환 (예: contact 확률 기반) 으로 가는 확장이 향후 과제로 남음.
- 비명시 갭 — Hand 단은 1-DoF gripper 로, 본 논문이 다루는 "force-aware contact" 는 *손 안* 의 in-hand 조작이 아니라 EE 단의 거시 접촉입니다. multi-finger / in-hand 영역으로 직접 이식할 근거는 없습니다.
- 비명시 갭 — V2F handover 가 깨지는 (예: VLM pointing 이 틀린) 시나리오에서 fail-safe 동작이 정량적으로 평가되지 않았습니다 (spatial OOD 표에 ForceFlow 단독 0%, 곧 V2F 없으면 spatial generalization 0% 라는 점이 간접 증거).
- 비명시 갭 — VLM 은 task 별 VQA 데이터로 fine-tune 되므로, "zero-shot spatial generalization" 의 zero-shot 범위가 새로운 keypoint 의미까지 포함하지는 않습니다.

---

## ♻️ 재현성

- 코드: [github.com/JokerESC/ForceFlow](https://github.com/JokerESC/ForceFlow) (저자 명시).
- 데이터: [huggingface.co/datasets/JokerESC/ForceFlow](https://huggingface.co/datasets/JokerESC/ForceFlow) (저자 명시).
- 프로젝트 페이지: [jokeresc.github.io/ForceFlow-page](https://jokeresc.github.io/ForceFlow-page).
- 하드웨어: xArm6 + 1-DoF gripper, RealSense L515 (글로벌) + D435 (wrist), SpaceMouse / Quest Pro teleop, 6D F/T sensor (모델 미명시).
- 학습 자원: RTX 4090 ×4, 48 CPU cores, 283 GB RAM. task 당 100k step / 8–10 시간. 평가는 task 당 20 trial.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P2 (Structured Input-Modality Binding) — 강한 지지/긴장.** ForceFlow 의 비대칭 fusion 은 P2 의 "modality 별 binding 분리" 와 직접 맞닿아 있습니다. 다만 P2 는 *finger-level* 구조적 binding 을 전제합니다. 본 논문은 손 안 finger 가 아닌 EE-level 6D F/T 만 다룹니다. 따라서 D11 (visuotactile encoder), D5 (modality 분리) 에 대해서는 강한 *설계 패턴* 증거 (force=global AdaLN, vision=local cross-attn) 입니다. 다만 D8/D9/D10 (finger 토큰화·topology·aggregation) 에 대한 직접 증거는 아닙니다.
- **P3 (Hand-level System0 Module, RL-scoped) — 안타고니스트 증거 후보.** ForceFlow 는 contact-rich regulation 을 RL 없이 *순수 IL + flow matching* 로 해결합니다. §10 의 "Genesis AI / VLA-only without RL" antagonist 와 같은 줄에 놓이며 *D13 (System0 필요성)* 의 가설을 직접 시험합니다. 단, ForceFlow 가 다루는 contact 는 EE 단 거시 접촉이라 손가락 슬립/유지 (P3 의 핵심 reward-engineerable 문제) 와 정확히 동치는 아닙니다.
- **P4 (VLM Preservation) — 약한 지지.** V2F 가 VLM 의 zero-shot pointing 능력을 fine-tune 으로 한정해 끌어 쓰고 접촉 정책에는 VLM 을 *전혀* 통과시키지 않습니다. D19 (a) "frozen backbone + action experts only" 와 같은 *기능 분리* 정신을 task-level 에서 구현한 사례로 읽힙니다.
- **P5 (Falsifiable Evaluation) — Force Fidelity metric 의 직접 참조.** D26 의 contact-precision metric 후보 (slip count / pose stability) 에 *force-MAE cost* 라는 의미적으로 동치인 지표 정의를 더해 줍니다.
- **P1 (Body/Hand Split) — 거의 무관.** 1-DoF gripper 만 사용하므로 anatomical 분리 의제와 직접 닿지 않습니다. *task-level* V2F 분리는 P1 의 *architectural* split 과 다른 층위입니다.
- **단계(phase) 함의** — 4-contribution ablation 보다는 *실로봇 데모(real-world demo)* 에서 force-fidelity metric 채택 여부와, System0 RL 의 필요성 판단에서 antagonist 증거로 직접 참조됩니다.

---

## ✨ 핀 논문 대비 델타

- vs **ForceVLA (Yu et al. 2025, [arXiv § 8.4 미핀이나 §10 모니터])** — 본 논문의 직접 baseline. 같은 관측 (multi-view RGB + EE pose + 6D F/T) 에서 force-aware MoE VLA 대신 *AdaLN 으로 global force conditioning + joint force prediction* 으로 갈아탔습니다. 평균 SR +37%·Force Cost −15.1 N 으로 수치에서 앞섰습니다. ForceVLA 가 force 를 *expert* 단위로 라우팅하는 데 비해 ForceFlow 는 *layer-wise statistic modulation* 으로 다룹니다.
- vs **AdapTac ([arXiv:2505.13982](https://arxiv.org/abs/2505.13982), P2 핀)** — AdapTac 의 force-guided attention + future-force aux 와 ForceFlow 의 active force prediction 은 *aux head 로 force 예측을 학습 신호로만 쓴다* 는 발상이 겹칩니다. 차이: AdapTac 은 cross-attention 으로 force 를 *local* 신호로 다루고 ForceFlow 는 AdaLN 으로 *global* 통계 modulator 로 다룹니다.
- vs **ViTacFormer ([arXiv:2506.15953](https://arxiv.org/abs/2506.15953), P2 핀)** — ViTacFormer 는 vision-tactile cross-attention 으로 *대칭적* fusion 을 합니다. ForceFlow 의 새로움은 비대칭성 자체, 다시 말해 *force=global / vision=local* 로 원인-결과를 나눠 본 점을 modal masking 가설에 정면으로 묶어 정당화한 대목입니다.
- vs **π0.5 ([arXiv:2504.16054](https://arxiv.org/abs/2504.16054), P1/P3/P4 핀)** — π0.5 의 hierarchical inference (high-level VLM + low-level action) 와 ForceFlow 의 V2F handover 는 *계층 분리* 라는 점에서 같습니다. 다만 π0.5 는 모달리티 분리 없이 계층만 나누고 ForceFlow 는 *모달리티 dominance* 자체를 분리합니다 (vision 단계 → force 단계).
- vs **Reactive Diffusion Policy (Xue et al. 2025, "slow-fast visuo-tactile")** — slow visual / fast tactile 계층 분리는 ForceFlow 의 V2F + AdaLN 조합과 *직접 경쟁* 합니다. ForceFlow 는 fast-loop 자체를 *flow matching deterministic ODE* 로 두고 force history 를 layer 마다 주입하는 방식으로 차별화합니다.

---

## ⚙️ 의사결정 함의

이 논문이 옳다면, 우리 스택에 다음과 같은 구체 변경이 트리거됩니다.

- **D11 (Visuotactile encoder 후보) — global modulator path 추가.** 현재 D11 은 *swappable sensor head + per-finger token* 으로 D8 의 finger token 에 흡수시키는 *local* 경로만 있습니다. ForceFlow 결과는 "force 를 token 으로 cross-attn 에 넣을 때 modal masking 이 발생할 수 있다" 는 가설을 강화합니다. → **action experts (Body/Hand) 의 backbone LayerNorm 에 force-summary AdaLN $`\gamma,\beta`$ 를 주입하는 옵션을 D11 deferred 후보로 등록** 검토 (구체 config: hand expert DiT block 의 모든 LayerNorm 을 AdaLN 으로, force-summary = `[F_palm_summary; F_finger_summary_aggregated]`).
- **D5 (Input-modality + control-rate 분리) — modality dominance 분리의 정당화.** ForceFlow 결과는 D5 v1 의 "Body={vision/lang/proprio}, Hand={tactile/proprio/local visual}" 분리 정당성을 *비대칭 fusion* 가설로 보강합니다. → 변동 없음, 현 v1 유지를 강화.
- **D13/D14 (System0 필요성) — 반증 후보 등록.** ForceFlow 는 RL 없이 force history (10-step) + joint force prediction 만으로 contact regulation 을 잡았습니다. 초기 sim ablation / 실로봇 데모 비교군에 *"Hand expert with force history 10-step + next-force prediction head, no System0"* 변형을 추가하는 것이 합리적입니다. → **D25 4-contribution ablation 의 (d) +System0 조건 옆에 "(d') force history+pred head, no RL" 비교 셀 추가** 검토.
- **D17 (System0 reward) — joint prediction aux 영감.** Force prediction 을 학습 신호로만 쓰는 active-compliance 패턴은 System0 policy 의 next-tactile prediction aux head 로 이식 가능합니다. → **System0 PPO loss 에 `+ λ · MSE(predicted_next_tactile, observed_next_tactile)` aux term** 검토 ($`\lambda`$ ≈ 0.01–0.1 부터 sweep).
- **D26 (평가 metric) — Force Fidelity (MAE Cost) 채택.** contact-precision metric 의 slip-count / pose-stability 옆에 *task-dependent force MAE* (short-horizon: peak ‖f‖, continuous: 평균 effective ‖f‖) 를 정식으로 등록. → **초기 sim ablation 의 falsifier metric 에 `force_mae_cost` 추가**.
- **V2F handover 패턴은 우리 phase 매핑상 별도.** 우리 단계는 *in-hand rotation → tool articulation* 로, V2F 가 노리는 *approach→contact* 분리와 시점이 다릅니다. 직접 채택 후보는 tool articulation 단계의 *tool 도달 → tool 조작* 분리에 한해 검토.

---

## ⚠️ 먼저 검증할 실패 모드

- **Modal masking 가설이 우리 multi-finger F/T 에는 같은 강도로 성립하지 않을 수 있다.** ForceFlow 의 force 는 단일 EE 6D 입니다. 우리는 (Sharpa 기준) finger 별 320×240 Deform Map 으로, 차원이 force 쪽도 *고차원* 입니다. 첫 sanity check: **D8 의 per-finger token 을 cross-attn 으로 넣은 baseline 과 AdaLN-summary 로 넣은 변형을 동일 데이터로 학습해 contact-precision metric 비교** (가장 싼 sim 단일 task, e.g. 큐브 회전 슬립 카운트).
- **VLM pointing 이 in-hand 도메인에서는 의미가 다르다.** V2F 는 "approach waypoint" 라는 자연스러운 분기점이 있지만 in-hand rotation 은 손 안에서 끊임없이 접촉합니다. → **V2F 이식은 tool articulation 단계까지 미루고 초기 sim ablation / 실로봇 데모 에서는 무리하게 적용하지 않는다.**
- **Joint force prediction 은 datasource bias 에 민감.** 우리 demonstration 의 force annotation 노이즈가 ForceFlow 의 6D F/T 보다 훨씬 거칠 가능성. → **prediction head 채택 전 expert force 신호의 SNR / temporal smoothness 를 먼저 측정.**
- **Force Cost metric 이 force regulation 우수성을 *과대평가* 할 수 있다.** ForceFlow (w/o Force) 가 SR 44% 로 ForceVLA 와 거의 같은데 Force Cost 22.67 N vs 23.31 N 으로 비슷합니다. SR 과 Force Cost 가 상관이 약한 영역에서는 metric 채택의 의미가 줄어듭니다. → **초기 sim ablation 에서 SR 과 Force Cost 의 task-별 상관을 먼저 측정**, 그 다음에 falsifier 에 정식 편입.
- **Flow matching vs diffusion 의 closed-loop latency 우위는 우리 control rate 에서 무의미할 수 있다.** π 백본은 이미 flow matching 입니다. → 별도 검증 불필요, 기존 D23 (iii) 유지.

---

## 💡 컨텍스트 제안

- **§8.2 P2 핀 후보로 ForceFlow 등록 검토.** ForceVLA 가 §10 모니터링 후보로 있지만 핀이 아닌데, ForceFlow 가 ForceVLA 의 직접 후속이고 SR/Force Cost 모두에서 새 SOTA 를 찍었습니다. AdapTac 또는 TacFiLM 의 자리와 비교해 *비대칭 fusion = AdaLN-global + cross-attn-local* 의 architectural pattern 을 분명히 박는 의미에서 핀 교체 후보입니다. — 결정은 사람이.
- **§10 Competitor 모니터링에 "force-IL no-RL 강성과군" 카테고리 추가 검토.** 현재 §10.1 은 "Genesis AI / IMCopilot" 으로 RL 회피 진영을 잡고 있는데 ForceFlow 는 *force-aware IL 만으로 contact-rich* 라는 점에서 System0 필요성에 대한 정량 antagonist 입니다. — §10.1 에 ForceFlow / ForceVLA / Reactive Diffusion Policy 를 묶어 한 줄 추가하는 것을 제안.
- **D26 metric 확장.** 위 ⚙️ 항목과 동일 — `force_mae_cost` 를 contact-precision metric 에 정식 등록.
- **현 핀 교체 후보 없음 (P1/P3/P4/P5).** P3 의 antagonist 증거이지만 *핀* 자리는 RL-side (HORA/AnyRotate) 가 차지하는 게 일관성이 있습니다.

---

> 💡 base 매핑은 `/implement-design analysis/2605.11048/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
