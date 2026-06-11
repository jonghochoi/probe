# Paper Analysis — Demystifying Action Space Design for Robotic Manipulation Policies

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Demystifying Action Space Design for Robotic Manipulation Policies |
| 저자 | Yuchun Feng, Jinliang Zheng, Zhihao Wang, Dongxiu Liu, Jianxiong Li, Jiangmiao Pang, Tai Wang, Xianyuan Zhan |
| 링크 | [arXiv:2602.23408](https://arxiv.org/abs/2602.23408) |
| 발행일 / 버전 | 2026-02-26 · v2 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-11 |
| 관련 Pillar | P1, P4 |
| 태그 | vla-arch, flow-matching |

<!-- 코드/데이터는 "open-sourced upon publication" 으로만 명시 — 공개 repo/site URL 이
     본문·메타에 없어 링크 행은 arXiv 단독. 카탈로그 등재 대상(model/dataset/benchmark)
     아님(기존 RoboTwin 2.0 사용, 신규 산출물은 study 결과)이라 카탈로그 행 생략. -->

---

## 🧭 한 줄 요약 (TL;DR)

Imitation 기반 로봇 매니퓰레이션에서 **action space 설계(시간축: absolute vs delta·chunking horizon / 공간축: joint vs task space)** 가 데이터·모델 스케일 못지않게 성능을 좌우함을 13,000+ 실로봇 rollout·500+ 모델로 대규모 실증하고, "delta(특히 chunk-wise) 는 항상 유리, joint space 는 단일 임베디먼트 안정성·task space 는 cross-embodiment 일반화에 유리"라는 설계 지침을 도출합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 정책이 출력하는 action 을 어떤 표현으로 정의할지(절대 vs 상대, joint vs end-effector, chunk horizon)가 정책 학습 난이도와 배포 안정성을 어떻게 바꾸는지를 체계적으로 규명하는 것입니다.
- **기존 접근의 한계** — 최근 연구는 데이터·모델 용량 스케일링에 집중하는 반면 action space 는 ad-hoc heuristic 이나 코드베이스에서 물려받은 legacy 설정으로 결정돼, "SOTA" 결과가 문서화되지 않은 control 선택과 뒤섞여 재현성을 해칩니다.
- **본 논문의 가설** — action 표현은 사소한 구현 디테일이 아니라 optimization landscape 를 근본적으로 바꾸는 결정적 설계 변수이며, 시간·공간 두 직교 축으로 분해하면 **learnability ↔ control stability** 사이 trade-off 를 구조적으로 설명할 수 있다는 것입니다.
- **왜 지금 중요한가** — 분야가 cross-embodiment 가능한 generalist foundation model 로 향하면서, control interface 설계 오류의 비용이 커지고 원칙 있는 통일 지침의 필요가 커졌습니다.

---

## 🧩 핵심 기여

- **Action space 의 2축 taxonomy 정립** — action 표현을 **temporal abstraction**(absolute=0차 vs delta=1차, + action chunking)과 **spatial abstraction**(joint space vs task space)이라는 직교 두 축으로 형식화하고, 각 축이 learnability·stability 에 거는 trade-off 를 분석합니다.
- **대규모 실증 연구** — AgileX(단일/양팔)·AIRBOT 실로봇 + RoboTwin 2.0 시뮬에서 2,000+ 데모, 13,000+ 실로봇 rollout, 500+ 학습 모델, 5종 cross-validation 으로 결론을 교차검증합니다.
- **Chunk-wise vs step-wise delta 의 결정적 차이 규명** — action chunking 과 delta 를 결합할 때 reference frame 선택이 성능을 평균 10%+ 가르며, step-wise 적분이 노이즈를 $`\mathcal{O}(k)`$ 로 증폭한다는 명제(Proposition 4.1)로 메커니즘을 증명합니다.
- **Horizon-abstraction 결합 발견** — chunking horizon $`k`$ 는 독립 하이퍼파라미터가 아니라 temporal abstraction 과 결합돼, delta 는 짧은 horizon·absolute 는 긴 horizon 에서 최적임을 grid search 로 보입니다.
- **설계 지침 도출** — (1) horizon 은 temporal abstraction 에 맞춰 적응, (2) 단일 임베디먼트 성능 극대화엔 joint + chunk-wise delta, (3) cross-embodiment/transfer 엔 task space(EE) 가 우월하다는 actionable guideline 을 제시합니다.

---

## 🔑 기술 키워드

- **Action space (action abstraction)** — 정책의 신경망 출력과 물리 하드웨어 사이를 잇는 인터페이스. 무엇을 어떤 좌표·차수로 예측할지를 정하는 본 논문의 분석 대상입니다.
- **Temporal abstraction** — action 시퀀스가 표현하는 시간 미분 차수. 0차=절대 목표 상태(absolute), 1차=상태 증분(delta/relative) 으로 나뉩니다.
- **Spatial abstraction** — 정책-컨트롤러 사이 추상화 경계. configuration space(joint position) 와 task space(EE pose) 두 운동학적 표현을 다룹니다.
- **Action chunking** — 한 번에 미래 $`k`$ 스텝 action 시퀀스를 예측하는 기법(ACT 유래). temporal dependency 포착으로 성능을 올리지만 delta 와 결합 시 reference frame 모호성을 낳습니다.
- **Chunk-wise vs step-wise delta** — chunk 내 각 action 을 chunk 시작 상태 기준으로 정의(chunk-wise)할지, 직전 예측 상태 기준 누적으로 정의(step-wise)할지의 선택. 본 논문이 노이즈 증폭으로 갈라내는 핵심 구현 디테일입니다.
- **Inverse Kinematics (IK)** — task-space 목표를 joint command 로 역사상하는 사상 $`\Phi_{\mathrm{IK}}`$. task space 배포 시 singularity·error 누적을 유발하는 비용 요소입니다.
- **Flow matching policy** — 노이즈 $`\epsilon`$ 를 전문가 action 으로 옮기는 velocity field $`v_\theta`$ 를 학습하는 생성형 정책(DP 변형). 복잡·multimodal 한 joint-space 분포를 잘 모델링합니다.
- **Regression policy** — MSE 손실로 action 을 직접 회귀하는 정책(ACT 변형). joint space 의 multimodality 에는 flow matching 보다 취약합니다.
- **Noise amplification (spectral norm)** — 예측 노이즈가 디코딩 과정에서 얼마나 증폭되는지를 선형 변환 행렬의 spectral norm 으로 측정하는 안정성 척도. step-wise 가 불안정한 이유를 정량화합니다.
- **Cross-embodiment / transfer learning** — 서로 다른 로봇 형상 간, 또는 사전학습 foundation model($`\pi_0`$) 로부터의 지식 이전. task-space 가 embodiment-invariant 해 유리해지는 regime 입니다.

---

## 🔬 방법론

### 직관

이 논문은 새 모델을 제안하지 않습니다. 대신 "정책이 무엇을 출력하도록 만들 것인가" 라는, 보통 코드베이스에서 무심코 물려받는 선택이 사실은 학습 난이도와 배포 안정성을 근본적으로 가른다는 것을 대규모 실험으로 증명하는 연구입니다. 핵심 관점은 action 표현을 서로 직교하는 두 축으로 쪼개는 것입니다. **시간축** 은 "목표를 절대 좌표로 찍을 것인가(absolute), 아니면 지금으로부터의 변위로 줄 것인가(delta)" 이고, **공간축** 은 "관절 각도(joint)로 줄 것인가, 손끝 위치/자세(task=EE)로 줄 것인가" 입니다.

두 축 각각에 trade-off 가 있습니다. 시간축에서 absolute 는 의미가 명확하지만 정책이 전체 장면 기하·전역 위치를 raw 관측에서 추론해야 해 학습이 어렵고, delta 는 "바로 다음 변위" 라는 더 다루기 쉬운 타깃을 주지만 배포 시 노이즈·지연·추종오차가 누적돼 drift 위험이 있습니다. 공간축에서 task space 는 물체 중심 관측과 기하적으로 잘 정렬되지만 배포에 IK 가 필요해 singularity·오차 누적을 부르고, joint space 는 IK 없이 안정적이지만 정책이 비선형 configuration manifold 로의 사상을 암묵적으로 배워야 해 학습이 복잡합니다.

여기에 현대 정책의 필수 요소인 action chunking(한 번에 $`k`$ 스텝 예측)이 끼면 delta 정의에 숨은 모호성이 드러납니다. chunk 내 각 스텝을 **chunk 시작점 기준**(chunk-wise)으로 줄지 **직전 스텝 기준 누적**(step-wise)으로 줄지에 따라 action 분포가 완전히 달라지며, 저자들은 step-wise 누적이 예측 노이즈를 horizon 에 비례해 증폭한다는 것을 행렬 spectral norm 으로 증명합니다. 또한 horizon $`k`$ 자체가 독립 하이퍼파라미터가 아니라 시간축 선택과 결합돼, delta 는 짧게·absolute 는 길게 가야 최적이라는 점을 발견합니다.

결론적으로 이 연구의 산출물은 알고리즘이 아니라 **설계 지침** 입니다: delta(특히 chunk-wise)는 거의 항상 유리하고, joint space 는 자원이 충분한 단일 임베디먼트에서·task space 는 cross-embodiment/transfer 에서 강점을 보인다는 것을, 실로봇 13,000+ rollout 으로 뒷받침합니다.

![Figure 2 — action space taxonomy](https://arxiv.org/html/2602.23408/figure/preliminary.png)

> "Figure 2: Hierarchy of the action space for robotic manipulation policies and its abstraction taxonomy" (§2)
> (한글 해설 — action 표현을 spatial(joint/task) × temporal(absolute/delta) 두 직교 축으로 분해하는 본 논문의 분석 골격을 시각화합니다.)

### 아키텍처

분석 대상은 단일 모델이 아니라 **2×2 action space**(spatial: joint/task × temporal: absolute/delta)이며, 이를 두 모델 패러다임 위에서 교차 평가합니다.

**(1) Spatial abstraction (§2.1).**

> "we restrict our scope to the two dominant kinematic abstractions used in practice: configuration space (joint positions) and task space (robot-based end-effector pose)." (§2.1)
> (한글 해설 — torque 수준은 고차원·저효율이라 제외하고, 운동학적으로 등가지만 학습 landscape 가 다른 joint vs task 두 표현만 비교 대상으로 좁힙니다.)

> "Consequently, spatial abstraction presents a fundamental trade-off between learning alignment and execution robustness." (§2.1)
> (한글 해설 — task space 는 물체 중심 관측과의 정렬(learning alignment)이 좋지만 IK 가 필요해 배포가 불안정하고, joint space 는 그 반대라는 핵심 trade-off 를 한 문장에 못 박습니다.)

**(2) Temporal abstraction (§2.2).** 0차=absolute(목표 상태 직접 지정), 1차=delta(상태 증분 지정).

> "In contrast, a delta parameterization predicts relative increments, yielding a better-conditioned and closed-loop learning target. However, deploying delta actions makes the system more sensitive to feedback imperfections: noise, latency, and tracking errors can accumulate over time and lead to drift." (§2.2)
> (한글 해설 — delta 가 학습 타깃으로는 더 잘 조건화되지만, 배포 시 누적 drift 라는 대가를 지닌다는 점이 시간축 trade-off 의 핵심입니다. 단, 저자들은 position-based low-level controller 를 인터페이스로 쓰므로 "1차" 는 물리 제어 모드가 아니라 정책 출력의 의미적 차수입니다.)

**(3) Action chunking 의 두 구현 모호성 (§2.3).**

> "step-wise delta (relative to the immediately preceding predicted state within the sequence) versus chunk-wise delta (relative to the robot's state at the start of the chunk). This choice fundamentally reshapes the action distribution." (§2.3)
> (한글 해설 — chunk 내 delta 의 기준 프레임 선택. 직전 예측 상태 누적(step-wise) vs chunk 시작 상태 고정(chunk-wise)이 action 분포를 근본적으로 바꿉니다.)

> "delta-based control may necessitate shorter horizons to facilitate rapid correction, whereas absolute position control might benefit from longer horizons to maintain global spatial grounding." (§2.3)
> (한글 해설 — horizon $`k`$ 와 action abstraction 사이 결합 가설. delta 는 빠른 보정을 위해 짧은 horizon, absolute 는 전역 grounding 유지를 위해 긴 horizon 을 선호한다는 예측으로, §4.1.2 에서 실증됩니다.)

**(4) 형식화 (Appendix G).** 정책은 latent 시퀀스 $`\mathbf{Z}_{t}\in\mathbb{R}^{c\times d_{a}}`$ 를 내고, 이는 temporal decoding → spatial projection 의 2단계로 실행 가능한 joint command $`\mathbf{u}_{t}\in\mathbb{R}^{d_{q}}`$ 가 됩니다($`c`$ = chunk length, $`d_a`$ = action 차원, $`d_q`$ = joint 차원).

Temporal decoding — reference 상태 $`\mathbf{s}^{\mathrm{ref}}_{t}`$ 기준 (Eq. 1):

```math
\tilde{\mathbf{a}}_{t+k}=\begin{cases}\mathbf{s}^{\mathrm{ref}}_{t}+\mathbf{z}_{t,k},&\text{Chunk},\\[5.0pt] \mathbf{s}^{\mathrm{ref}}_{t}+\displaystyle\sum_{j=1}^{k}\mathbf{z}_{t,j},&\text{Step}.\end{cases}
```

chunk-wise 는 각 latent 가 chunk 시작점 대비 직접 변위이고, step-wise 는 $`j=1`$ 부터 $`k`$ 까지 누적합이라 적분 연산이 들어갑니다. 이 차이가 아래 안정성 분석의 출발점입니다.

Spatial mapping — IK 사상 $`\Phi_{\mathrm{IK}}:\mathbb{R}^{d_{a}}\times\mathbb{R}^{d_{q}}\to\mathbb{R}^{d_{q}}`$ (Eq. 2):

```math
\mathbf{u}_{t+k}=\begin{cases}\tilde{\mathbf{a}}_{t+k},&\text{joint-space},\\[6.0pt] \Phi_{\mathrm{IK}}(\tilde{\mathbf{a}}_{t+k},\,\mathbf{q}_{t}),&\text{task-space}.\end{cases}
```

joint-space 는 항등사상이라 추가 변환이 없고, task-space 는 현재 joint 구성 $`\mathbf{q}_{t}`$ 에 의존하는 IK 를 거칩니다.

결합 선형 근사 — 전체 사상의 국소 Jacobian (Eq. 4):

$$\mathcal{T}_{\mathrm{total}}\;\approx\;(\mathbf{I}_{k}\otimes\mathbf{S}_{t})\,\mathbf{M}_{\mathrm{time}}.$$

여기서 $`\mathbf{S}_{t}=\partial\,\mathcal{T}_{\mathrm{space}}/\partial\tilde{\mathbf{a}}`$ 는 공간 projection 의 Jacobian(joint 면 $`\mathbf{I}_{d_q}`$, task 면 differential IK Jacobian), $`\mathbf{M}_{\mathrm{time}}`$ 은 시간 디코딩 선형 연산자입니다. 핵심은 시간·공간 표현이 **곱(multiplicative)** 으로 결합돼 전체 안정성이 두 인자의 spectral 성질에 함께 좌우된다는 점입니다.

### 학습 목표 / 손실

두 생성 패러다임으로 정책을 학습합니다(각각 ACT·DP 의 구현에 대응).

(1) Regression-based policy — 표준 MSE:

$$\mathcal{L}_{\mathrm{R}}=\mathbb{E}_{(\mathbf{o},\mathbf{a})\sim\mathcal{D}}\left[\left|\pi_{\theta}(\mathbf{o})-\mathbf{a}\right|^{2}\right]$$

(2) Flow matching-based policy — 노이즈 $`\epsilon`$ 를 전문가 action 으로 옮기는 velocity field $`v_\theta`$ 학습:

$$\mathcal{L}_{\text{F}}=\mathbb{E}_{\tau\sim\mathcal{U}(0,1),\,(o,a)\sim\mathcal{D}}\Big[\,\big\|v_{\theta}(a^{\tau},o,t)-(a-\epsilon)\big\|^{2}\,\Big]$$

여기서 보간점은 $`\mathbf{x}_{\tau}=(1-\tau)\boldsymbol{\epsilon}+\tau\mathbf{a}`$, $`\tau\sim\mathcal{U}(0,1)`$ 입니다. flow matching 은 복잡·multimodal 분포(특히 joint-space 의 비선형 configuration manifold)를 더 강하게 모델링합니다.

**안정성 정리 — chunk vs step 의 분기점 (Proposition 4.1 / G.1).** chunk 길이 $`k`$ 의 예측 노이즈 $`\boldsymbol{\epsilon}\in\mathbb{R}^{k}`$ ($`\|\boldsymbol{\epsilon}\|_{2}\leq\delta`$)가 디코딩된 실행 action 오차 $`\mathbf{e}_{a}`$ 로 선형변환 행렬 $`\mathbf{M}`$ 을 통해 전파됩니다.

> "For step-wise delta, $`\mathbf{M}_{\mathrm{step}}=\mathbf{L}_{k}`$, where $`\mathbf{L}_{k}`$ is the $`k\times k`$ lower-triangular matrix of ones. The worst-case error bound scales linearly with the horizon" (§4.1.1)
> (한글 해설 — step-wise 의 연산자는 모두 1 인 하삼각(누적합) 행렬 $`\mathbf{L}_{k}`$ 라서, 최악 오차가 horizon 에 선형으로 커집니다.)

step-wise: $`\|\mathbf{e}_{a}\|_{2}\leq\|\mathbf{L}_{k}\|_{2}\|\boldsymbol{\epsilon}\|_{2}\approx\frac{2k+1}{\pi}\delta\sim\mathcal{O}(k)`$. chunk-wise·absolute: $`\mathbf{M}=\mathbf{I}_{k}`$ 라 $`\|\mathbf{e}_{a}\|_{2}\leq\delta\sim\mathcal{O}(1)`$ 로 horizon 무관 상수 bound.

증명 핵심(§G.2)은 $`\mathbf{L}_k`$ 의 역행렬이 차분 연산자 $`\mathbf{D}_k`$ 이고, $`\sigma_{\max}(\mathbf{L}_{k})=1/\sigma_{\min}(\mathbf{D}_{k})`$ 를 쓴 뒤 $`\mathbf{D}_k\mathbf{D}_k^{T}`$ (이산 Laplacian 형)의 고유값 $`\lambda_{i}=4\sin^{2}\!\big(\frac{(2i-1)\pi}{2(2k+1)}\big)`$ 로부터 $`\sigma_{\min}(\mathbf{D}_{k})=2\sin\!\big(\frac{\pi}{2(2k+1)}\big)`$ 를 얻고, 소각 근사로 $`\|\mathbf{L}_{k}\|_{2}\approx\frac{2k+1}{\pi}`$ 를 도출하는 것입니다. 즉 step-wise 누적은 $`k\geq2`$ 부터 노이즈를 반드시 증폭합니다.

또한 chunk-wise·absolute 도 open-loop 한계는 공유합니다(§G.2 Remark): 각 offset 을 단일 관측 $`\mathbf{o}_t`$ 에서 예측해야 하므로, horizon 이 커지면 (1) 변위 크기 증가로 타깃 분포 분산이 커지고(variance growth), (2) $`I(\mathbf{a}^{*}_{t+k};\mathbf{o}_{t})`$ 가 줄어 조건부 엔트로피 $`H(\Delta\mathbf{a}^{*}_{k}\mid\mathbf{o}_{t})`$ 가 증가(information decay)합니다. 이것이 §4.1.2 의 horizon saturation/decorrelation 현상의 이론적 근거입니다.

### 학습 셋업

- **Base architecture** — FiLM-conditioned ResNet-18 vision encoder + 6-layer Transformer decoder(RT-1/ACT/DP 관행). language feature 를 FiLM 으로 visual 표현에 주입하고 encoder-decoder 로 action 생성.
- **두 변형** — Regression(L2, ACT 대응) / Flow matching(velocity field, DP 대응). 추가로 Foundation policy $`\pi_0`$ 를 transfer 분석용으로 도입.
- **하이퍼파라미터 (Table 2)** — Optimizer AdamW, batch size 512, learning rate $`1\times10^{-4}`$, CosineAnnealingLR, weight decay 0.01, $`\beta_1,\beta_2=0.9,0.95`$, float32, image 224×224, ColorJitter(0.2,0.2,0.2,0).
- **하드웨어/규모** — 8× NVIDIA A100, 총 16,000+ GPU-hours. 실로봇 데모 2,000+, rollout 13,000+, 학습 모델 500+.
- **$`\pi_0`$ transfer 설정 (§E.3)** — 공식 codebase 의 LoRA 로 파인튜닝, Touch Cube/Pick Cup/Pick&Place 3태스크 통합 multi-task, 30,000 step, batch 32, 10,000 step 마다 검증.

---

## 📊 실험 설정과 결과

**플랫폼/프로토콜.** 4종 하드웨어 — 단일팔 AgileX PiPER(주 실험), 양팔 AgileX, AIRBOT(cross-morphology), RoboTwin 2.0 시뮬(hard mode, 50태스크 중 10선택). 실로봇은 workspace 를 $`6\times6`$ grid 로 균등분할해 물체 초기위치를 표준화하고, trial 3회 × rollout 10회로 progress score 를 보고합니다. 실세계 태스크: Touch Cube, Pick Up Cup, Pick and Place Cup, Bimanual Cube Transfer(접촉·horizon·협응 난이도 증가 curriculum).

**RQ1 — 구현 디테일이 결정적 (§4.1).**

> "chunk-wise delta consistently and significantly outperforms step-wise delta across all tasks. Notably, the performance gap reaches upwards of 10% on average" (§4.1.1)
> (한글 해설 — regression 정책 기준, chunk-wise delta 가 step-wise 대비 전 태스크에서 평균 10%+ 우위. Proposition 4.1 의 노이즈 증폭이 실증된 것입니다.)

> "absolute control benefits from a significantly longer horizon, whereas delta control peaks at a shorter horizon." (§4.1.2)
> (한글 해설 — 학습은 $`k=60`$(30Hz·2초) 고정, 추론 horizon 을 15~60 grid search. absolute 는 긴 horizon, delta 는 짧은 horizon 에서 최적 — §2.3 가설 확인. absolute 는 일부 태스크에서 saturation(information decorrelation)도 관찰.)

**RQ2 — action abstraction 의 체계적 경향 (§4.2).** delta 표준화(chunk-wise) + horizon 결합 반영(delta $`k=30`$, absolute $`k=60`$) 후 14태스크(실4+시뮬10)·regression/flow-matching 양쪽·single/multi-task 로 평가(Table 1).

| 셋업 (Overall Avg) | EE-abs | EE-delta | Joint-abs | Joint-delta |
|---|---|---|---|---|
| ACT (Regression) | 63.4±2.7 | 78.4±1.4 | 71.2±2.9 | 79.7±2.5 |
| DP (Flow Matching) | 71.9±4.8 | 82.9±1.6 | 79.6±2.2 | **88.0±2.3** |

| 셋업 (Single Arm AgileX Avg) | EE-abs | EE-delta | Joint-abs | Joint-delta |
|---|---|---|---|---|
| ACT | 69.0±2.0 | 89.6±2.1 | 77.3±2.8 | 88.0±2.9 |
| DP | 74.0±3.1 | 91.4±1.6 | 85.0±2.3 | **95.9±1.1** |

> "with standard modern practice, delta abstraction consistently and significantly outperforms absolute abstraction across all platforms, task configurations, and model variations." (§4.2.1)
> (한글 해설 — temporal 축의 결론은 결정적입니다. 어느 열에서도 delta > abs. 표에서 EE-delta·Joint-delta 가 동일 공간의 abs 를 모두 상회합니다.)

> "policies trained under the flow-matching generative paradigm exhibit a distinct excellence in Joint space learning." (§4.2.2)
> (한글 해설 — 공간 축은 joint 가 대체로 우세하되 불일치 존재. 단 flow-matching 은 joint space 의 비선형·multimodal manifold 를 잘 잡아 envelope 가 크게 확장(Fig. 4) — 최고점 Joint-delta(DP) 88.0/95.9 가 이를 뒷받침합니다.)

**RQ3 — 일관성·스케일링 (§4.3).** epoch(600/900/1200)·데이터(100/250/500 traj) grid. 각 점은 12 trial 평균(120 rollout).

> "as training epochs and data volume increase, the superiority of joint-space actions becomes increasingly pronounced, particularly for regression-based policies." (§4.3.1)
> (한글 해설 — joint space 는 자원이 늘수록 task space 대비 격차가 벌어집니다. task space 는 저데이터·저연산 regime 에서만 경쟁적.)

> "under cross-embodiment and transfer learning settings, task-space representations exhibit a more pronounced advantage and, in some cases, surpass joint-space control." (§4.3.2)
> (한글 해설 — AIRBOT cross-embodiment· $`\pi_0`$ LoRA transfer 에서는 반전: task space 가 embodiment-invariant 해 joint space 를 역전할 수 있음. delta 우위는 여기서도 유지.)

**Cross-validation (§F).** flow-matching backbone 으로도 chunk-wise > step-wise 재확인(F.1), RoboTwin 시뮬에서 delta·joint 우위가 데이터/연산 스케일 전반 일관(F.2), multi-task 에서도 trend 유지(F.3).

![Figure 3 — chunk vs step delta & horizon](https://arxiv.org/html/2602.23408/figure/delta_horizon.png)

> "Figure 3: (a) We verified that chunk-wise delta for both EEF and Joint perform better than step-wise delta representations. (b) Grid search over execution horizons across four different action space." (§4.1)
> (한글 해설 — (a) chunk-wise > step-wise, (b) absolute 는 긴·delta 는 짧은 horizon 최적이라는 RQ1 의 두 결론을 시각화합니다.)

![Figure 5 — scaling consistency](https://arxiv.org/html/2602.23408/figure/ep_left.png)

> "Figure 5: Consistency of Action Space Superiority under Scaling. We evaluate policy performance across varying (a) training epochs and (b) number of demonstrations." (§4.3.1)
> (한글 해설 — epoch·데모 수가 늘어도 delta·joint 우위가 유지·강화됨을 보여, 결론이 특정 자원 budget 의 artifact 가 아님을 입증합니다.)

---

## ⚖️ 한계

- **Taxonomy 가 경직(저자 명시, §B).** absolute/delta·joint/task 를 정적 범주로 고정하지만, 최적 action space 는 task phase 에 따라 동적일 수 있습니다(예: reaching 은 task-space delta, fine 조작은 joint-space absolute). hybrid/adaptive 표현은 미탐색으로 남아, 본 연구의 "단일 표현 고정" 결론이 phase-혼합 정책에는 그대로 적용되지 않을 수 있습니다.
- **Action chunking 의 이론이 경험적 수준(저자 명시, §B).** horizon 선택이 여전히 heuristic 이고, "긴 horizon 이 absolute 에 유리" 라는 결과의 수렴 안정성·information decorrelation 메커니즘이 형식화되지 않았습니다. saturation 지점을 예측할 원칙이 없어 grid search 의존이 남습니다.
- **저DoF·준정적 태스크에 국한(저자 명시, §B).** 6-DoF 팔의 pick-and-place 류가 중심이라, humanoid·다지 손처럼 manifold 차원·비선형성이 큰 high-DoF 계나 table tennis·천 접기 같은 동적/dexterous 도메인에서 "delta joint 우위" 가 유지될지는 미검증입니다. **본 분석 스택(hand-centric)에 가장 직접적인 갭입니다.**
- **Transfer 결론의 표본 협소(저자 명시, §B).** task-space 의 transfer 우위는 $`\pi_0`$ 단일 foundation model + 소수 embodiment pair 에서만 관찰돼, pretraining paradigm(VL alignment vs 순수 BC)별 상호작용은 열린 질문입니다. "joint-space 정렬 사전학습이 transfer gap 을 줄일 수 있는가" 는 저자 스스로 미해결로 둡니다.
- **추론된 갭 — 인터페이스 결합 누락.** $`6\times6`$ grid·position-based controller·30Hz 라는 특정 control stack 에 묶여 있어, gripper(저DoF end-effector) 외 손가락 다접점 제어나 force/torque 인터페이스와 action space 의 상호작용은 다루지 않습니다. 본 연구의 spatial 축은 "joint vs EE pose" 둘 뿐이라, 손 관절 공간이 본질적으로 고차원·접촉 구속인 dexterous hand 에는 새 축이 필요할 수 있습니다.

---

## ♻️ 재현성

- **코드/데이터** — Ethics & Reproducibility Statement(§A)에서 "all code and datasets will be open-sourced upon publication" 으로만 명시. 분석 시점 공개 repo/URL 은 본문에 없습니다(LLM 은 writing polishing 에만 사용).
- **시뮬** — RoboTwin 2.0(공식 data generation tool)으로 완전 투명·재현 가능, AgileX embodiment·10태스크 명시.
- **하드웨어** — AgileX PiPER(단일/양팔, 6-DoF)·AIRBOT(6-DoF, 상이 kinematics), third-person + wrist camera. 8× A100, 16,000+ GPU-hours.
- **프로토콜** — $`6\times6`$ grid 초기화, 3 trial × 10 rollout, 학습 600 epoch(RQ2 기준) 등 평가 절차가 상세히 기술돼 재현 친화적이나, 실로봇 하드웨어 의존성이 큽니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P1(Heterogeneous Body/Hand Action Expert) — 직접 관련.** 본 논문은 P1 §5 에 이미 off-pin 으로 추적 중("D2 evidence"). spatial 축(joint vs task=EE)은 **D2(Body output space — both-wrist/tool-flange pose vs joint)** 과 **D3(Hand output space — finger joint command)** 의 핵심 증거입니다. 현재 v1 은 D2=(a) tool-flange **pose**(=task space), D3=(i) finger **joint** command 인데, 본 논문은 "단일 임베디먼트 안정성엔 joint, cross-embodiment 일반화엔 task space" 라는 분기를 줍니다 — 즉 Body(arm)는 transfer 를 위해 pose(task) 가 합당하나, Hand(다지 joint)는 joint 우위 증거에 부합합니다.
- **P1 D5(control-rate separation) / chunking horizon.** "delta=짧은 horizon, absolute=긴 horizon" 결합은 D5 의 control-rate 분리 설계에 입력이 됩니다(Body/Hand 가 서로 다른 abstraction·horizon 을 가질 근거).
- **P1 D7(π backbone 통합).** $`\pi_0`$ 를 LoRA 로 transfer 한 §4.3.2 실험은 D7(π0 action expert slice + FT)·D6(body→hand 위계) 의 base 통합 가정과 직접 맞닿습니다.
- **P4(Pretraining for Data-Efficient Adaptation) — 부차 관련.** **D23(action-representation × pretraining/preservation)** 에 직접 증거: transfer/cross-embodiment 에서 task-space 가 우위라는 발견은, foundation model 사전학습 supervision 을 어떤 action 좌표로 둘지(D23) 의 설계 변수입니다. 또 §B 의 "joint-space 정렬 사전학습이 transfer gap 을 줄이는가" 라는 열린 질문은 D22(corpus 구성)·D23 와 맞물립니다.
- **Identity 긴장/지지** — Identity 의 "anatomically heterogeneous Body/Hand decoder" 를 직접 지지(공간 표현이 부위별로 달라야 한다는 논거 보강). 다만 본 논문 스택은 저DoF gripper·pick-and-place 라 **hand-level dexterity 검증은 부재** — Identity 의 차별화 주장(hand 다접점)에 대한 직접 근거는 아닙니다.
- **경쟁자 함의** — P1 비교군(monolithic vs split)에 "표현 선택만으로 15%p 격차" 라는 baseline 정량 근거를 제공. 우리 split 설계가 이 표현 trade-off 를 어떻게 흡수하는지 보여야 함.

---

## ✨ 핀 논문 대비 델타

- **π0([arXiv:2410.24164], P1/P4 핀) 대비.** π0 는 chunk-wise delta + joint-space 를 *채택*만 했지 그 선택을 정당화하지 않습니다. 본 논문은 그 chunk-wise delta 선택이 step-wise 대비 노이즈 증폭 $`\mathcal{O}(k)\to\mathcal{O}(1)`$ 이라는 **이론적 근거** 와 13k rollout **실증** 을 제공해, π0 의 암묵적 control choice 를 사후 정당화합니다.
- **Dexora([arXiv:2605.18722], P1 핀) 대비.** Dexora 는 high-DoF bimanual 의 action-space *구현* 레퍼런스인 반면, 본 논문은 action-space 선택의 *원리* 를 controlled study 로 분리해 냅니다 — 단 Dexora 가 다루는 dexterous high-DoF 영역은 본 논문이 미검증으로 남긴 정확한 갭.
- **Shared-Autonomy Arm-Hand VLA([arXiv:2511.00139], P1 핀) 대비.** 후자는 arm/hand 해부학적 분리를 *데이터·아키텍처* 로 구현. 본 논문은 그 분리에서 "arm=task(transfer)/hand=joint(stability)" 라는 **좌표 배정 근거** 를 제공해 보완적입니다.

---

## ⚙️ 의사결정 함의

본 논문이 맞다면 우리 파이프라인에서 다음이 바뀝니다.

- **D2/D3 action 좌표 재검토** — Body(arm) expert 출력은 cross-embodiment/transfer 우선이면 **task-space(EE pose, D2=(a) 유지·강화)**, Hand expert 출력은 단일 임베디먼트 정밀 안정성 우선이면 **joint-space(D3=(i) 유지)** 라는 비대칭 좌표 배정이 정량 근거를 얻습니다. config 키: Body action head 의 `output_space=ee_pose`, Hand 의 `output_space=joint`.
- **delta 를 기본값으로, chunk-wise 강제** — 두 expert 모두 `delta=True` + **reference frame=`chunk_wise`**(`step_wise` 금지). step-wise 는 noise amplification 으로 horizon 확장 시 drift.
- **horizon 을 abstraction 별로 분리** — `action_horizon` 를 단일 상수로 두지 말고, delta head 는 짧게(예: $`k\approx30`$), absolute head 는 길게($`k\approx60`$). Body/Hand control-rate 분리(D5)와 직접 연동.
- **flow-matching head 유지(D23) 보강** — joint-space 의 multimodal manifold 는 flow matching 이 regression 보다 우월하므로, Hand(joint) expert 에 continuous flow-matching head(D23 v1=(iii)) 선택이 강화됩니다.
- **메트릭** — action-space ablation 시 progress score 를 $`6\times6`$ grid 표준화 초기화 + 다 trial 평균으로 보고하는 프로토콜을 차용(통계적 유의성 확보).

---

## ⚠️ 먼저 검증할 실패 모드

우리 스택(hand-centric, 22-DOF Sharpa, 다접점)으로 전이되지 않을 이유를 싼 검사부터:

1. **(가장 싼 검사) DoF·접촉 구조 불일치.** 본 논문 결론은 6-DoF 팔 + gripper(저DoF EE)·준정적 pick-and-place 산물입니다. 우리 Hand 는 22-DOF 접촉 구속 manifold 라, "joint > task" 가 그대로 갈지 먼저 시뮬에서 단일 in-hand 태스크로 joint-delta vs task-delta 만 빠르게 비교(별도 학습 없이 기존 데모 재라벨)해 부호 일치 여부를 확인.
2. **Task-space 자체가 손에 정의 곤란.** 다지 손의 "EE pose" 는 손가락별 fingertip pose 다수 + 접촉 구속이라 IK $`\Phi_{\mathrm{IK}}`$ 가 ill-posed/과결정. 본 논문의 spatial 축(단일 EE pose) 가정이 깨지므로, "task space" 대안 자체가 적용 가능한지 먼저 정의 차원에서 점검.
3. **Chunk-wise delta 의 reference 상태 정의.** 우리 dual-expert(body→hand 위계, D6)에서 hand 의 chunk reference $`\mathbf{s}^{\mathrm{ref}}_{t}`$ 가 body 의 변하는 grasp 상태에 묶이면, 정적 reference 가정이 약해져 noise bound $`\mathcal{O}(1)`$ 이 보장되지 않을 수 있음. body-relative vs world-relative reference 를 작은 데이터로 A/B.
4. **Transfer 결론의 사전학습 의존.** task-space transfer 우위는 $`\pi_0`$ 단일 backbone 산물 — 우리 lineage(PaliGemma×π0, P4 D19)에서도 동일한 부호인지, 그리고 손 관절을 joint-space 로 사전학습(§B 열린 질문)했을 때 역전되는지 확인 전엔 "transfer=task" 를 일반화하지 말 것.
5. **Flow-matching×joint 시너지의 horizon 민감도.** joint-space flow matching 우위가 우리 짧은 control-rate·고주파 손 제어에서도 유지되는지, 그리고 saturation/information decay 가 더 일찍 오는지(고차원일수록 entropy 증가 빠름) 확인.

---

## 💡 컨텍스트 제안

- **P1 §5 off-pin 코멘트 갱신 제안(사람 판단).** 현재 "13k+ real rollouts; joint=stability/task=generalization (D2 evidence)" 는 정확합니다. 다만 이번 분석으로 **D3·D5(horizon)·P4 D23** 까지 증거가 닿음이 드러났으니, role 설명을 "D2/D3 좌표 비대칭 + horizon-abstraction 결합 + D23 transfer 좌표" 로 확장하면 검색 시 연결이 풍부해집니다. (핀 승격은 불필요 — study/benchmark 성격이라 off-pin 유지가 적절.)
- **Decision 이동 없음.** 본 논문은 기존 v1 선택(D2=pose, D3=joint, D23=flow-matching)을 *지지·정당화* 하지 D-값을 뒤집지 않습니다. 다만 "horizon 을 abstraction 별로 분리" 라는 신규 설계 변수는 D5 deferred 후보로 기록할 가치가 있습니다.

> 💡 base 매핑은 `/implement-design analysis/2602.23408/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
