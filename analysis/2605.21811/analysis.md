# Paper Analysis — Safe and Steerable Geometric Motion Policies for Robotic Dexterous Manipulation

> PROBE paper-analysis 모드 산출물. 단일 한글 문서이며, 영문 1차 파일은
> 없습니다. 형식·이모지·용어 규칙은 `docs/STYLE.md` §5 / §4 를
> 정확히 따릅니다. 재실행 시 이 파일을 덮어씁니다.

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Safe and Steerable Geometric Motion Policies for Robotic Dexterous Manipulation |
| 저자 | Albert Wu, Riccardo Bonalli, Thomas Lew, C. Karen Liu (Stanford TML; Université Paris-Saclay; Toyota Research Institute) |
| 링크 | [arXiv:2605.21811](https://arxiv.org/abs/2605.21811) |
| 발행일 / 버전 | 2026-05-20 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-05-26 |

---

## 🧭 한 줄 요약 (TL;DR)

SafePBDS 는 PBDS (Pullback Bundle Dynamical Systems) 위에 *pullback CBF* 로 task manifold 안전 제약을 configuration manifold 가속도 위의 선형 부등식으로 변환합니다. 여기에 *task manifold action interface* 를 더해, 상위 정책이 저차원 잔차를 주입해도 안전을 깨지 않으면서 동작을 조향할 수 있게 만든 기하학적 모션 정책 프레임입니다. 23-DOF Franka–Allegro 실로봇에서 별도 학습 없이 4-finger 그래스핑 92.5%, 3-finger 그래스핑 94.4%, *model-based* 손바닥-아래 in-hand reorientation 360° 이상을 달성합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 다지 조작에서 서로 다른 기하학 공간 위의 목적과 제약 (구성 공간 자유도 $`\mathbb{R}^{m}`$, 엔드 이펙터 자세 $`\mathrm{SE}(3)`$, 장애물 거리 $`\mathbb{R}`$ 등) 을 매 제어 스텝마다 *동시에* 충족하면서 안전 제약은 *절대* 위반하지 않는 반응형 모션 정책을 만드는 것.
- **기존 접근의 한계 (학습 측)** — DRL · BC · VLA 류는 task-end-to-end 로 동작은 만들지만 train distribution 밖에서 *catastrophic* 실패가 가능하고 hard safety 보장을 정책 자체에 심을 수 없습니다. VLA 의 다지손 일반화는 데이터·모달리티 측면에서 아직 한정적입니다.
- **기존 접근의 한계 (최적화 측)** — Trajectory optimization 은 제약과 동역학을 명시적으로 다룰 수 있지만 계산 비용 때문에 실시간 반응형 제어에는 부담이 큽니다.
- **본 논문의 가설** — 기하학적으로 일관된 PBDS 위에 *pullback control barrier function* 한 층을 더하면 task manifold 안전을 configuration manifold 가속도의 *선형 제약* 으로 환원할 수 있고, 그 안전 집합을 깨지 않는 형태로 상위 정책의 입력을 받는 action interface 도 정의할 수 있다는 것.
- **왜 지금 중요한가** — VLA / RL 같은 상위 정책의 다지 조작 신뢰도가 *학습된 능력 ceiling* 에 묶여 있는 동안, 그 위 또는 그 아래에 *certifiable* 한 model-based 안전 층을 까는 설계가 안전·해석가능성·데이터 효율을 동시에 끌어올릴 수 있기 때문입니다.

---

## 🧩 핵심 기여

- *Pullback CBF* 구성을 새로 제시. task manifold 위에 정의된 안전 조건을 configuration manifold 위 *가속도에 대한 선형 부등식* 으로 일관되게 끌어내려 PBDS 의 다중 task QP 안에 hard constraint 로 자연스럽게 박는 방법입니다. ECBF (exponential CBF) 와 BCBF (backstepping CBF) 두 갈래를 모두 task manifold 로 확장합니다.
- *Task manifold action interface* 제시. 상위 정책이 task manifold 위 force-like 입력 $`u_l \in T^{*}N_l`$ 을 주면 autonomous 가속도 $`\bar a`$ 위에 그만큼만 residual 로 더해지는 두 번째 QP 로 처리합니다. 입력 0 은 자율 동작 복귀, 입력이 임의의 값이라도 안전 집합은 깨지지 않습니다.
- 두 단계 convex QP 로 정리된 알고리즘. QP 1 (autonomous safe acceleration) → QP 2 (action-steered acceleration). 매 제어 스텝마다 풀리는 *online* 최적화입니다.
- 시뮬레이션 검증. $`\mathbb{S}^{2}`$ 더블 인테그레이터로 chart invariance · safety recovery · multi-task composition · action interface 의 이론 속성을 모두 확인하고 MuJoCo 7-DOF Franka 에서 ECBF on/off ablation 으로 장애물 회피 효과를 검증합니다.
- 23-DOF 실로봇 하드웨어 (Franka Panda + Allegro Hand) 에서 (i) 20 객체 120 trial 4-finger 그래스핑 92.5% (111/120), (ii) 3 객체 36 trial *손가락 1 개를 제외한* 3-finger 그래스핑 94.4% (34/36). 정책 자체는 재학습 없이 ECBF 변형 + 1D action 만 교체했습니다.
- *Model-based, fully actuated* palm-down in-hand reorientation 을 최초로 보임. 깊이우선 트리 서치로 사전 계획한 finger gaiting 시퀀스를 SafePBDS 로 실행해 양방향 360° 이상 회전을 달성했고, 외부 진동·추가 하중에도 robust 합니다.

---

## 🔑 기술 키워드

- **PBDS (Pullback Bundle Dynamical Systems)** — 여러 task manifold 위의 simple mechanical control system (SMCS) 을 metric-weighted 최소제곱으로 합쳐 configuration 가속도를 뽑는 PROBE 정신의 기하학적 multi-task 합성 프레임. 본 논문이 그 위에 *안전 보장* 과 *조향 입력* 을 얹는 모태입니다.
- **CBF (Control Barrier Function)** — 안전 집합 $`\mathcal{C}_0=\{x:h_0(x)\geq 0\}`$ 의 forward invariance 를 보장하는 제어 측면의 보장 함수. 일반화: ECBF 는 higher relative degree, BCBF 는 backstepping 으로 안전 *속도장* 추종.
- **Pullback** — task manifold 위 정의된 수학 객체 (metric · 1-form · barrier 조건) 를 task map $`f:M\to N`$ 의 미분 정보로 *configuration manifold* 로 끌어내리는 미분기하 연산. SafePBDS 의 *task → config* 변환의 핵심 도구.
- **Sharp $`\sharp`$ (musical isomorphism)** — 코탱전트 $`T^*N`$ 의 1-form (force-like) 을 탱전트 $`TN`$ 의 가속도-유사 양 (좌표상으로는 $`g^{-1}u`$) 으로 옮기는 사상. action interface 에서 force-like 입력 $`u_l`$ 을 가속도 단위 $`u_l^{\sharp}`$ 로 바꿔 autonomous 동역학에 가산합니다.
- **Surjective submersive task map** — task map $`f:M\to N`$ 이 surjective submersion 이라는 가정 (Assumption 1). 다지 손 같은 *fully actuated / over-actuated* 시스템에서 자연스럽게 성립하며 pullback CBF 도출이 성립하는 조건.
- **Force closure** — 객체에 가해지는 접촉 wrench 가 외부 임의 wrench 를 상쇄할 수 있는 그립 조건. 본 논문은 [22] 의 $`l^*`$ metric 기반 force closure 를 ECBF 의 안전 함수로 직접 채택해 "안정적 그립을 유지하는" 것을 *제약* 으로 강제합니다.
- **Finger gaiting** — 손가락이 객체 위 접촉 위치를 순차로 옮겨가며 in-hand 회전을 만드는 시퀀스. SafePBDS 의 force closure CBF 가 매 단계 유지돼야 trajectory 가 valid.
- **Steerable PBDS** — autonomous 가속도 $`\bar a`$ 에 task manifold 입력 $`u_l^{\sharp}`$ 을 residual 로 얹는 두 번째 QP. 입력 0 → 자율 행동, 임의 입력 → 안전 보존. 본 논문이 상위 정책 (RL · VLA · 사람) 과의 결합 지점으로 제안하는 인터페이스.

---

## 🔬 방법론

### 직관

SafePBDS 의 출발점은 PBDS [6] 입니다. 여러 task manifold 위에 *원하는 동작* 을 SMCS (potential + dissipation) 로 설계하고 그것들을 metric-weighted 최소제곱으로 합쳐 configuration 가속도 $`\sigma^{..}\in T_\sigma M`$ 하나를 뽑는 reactive 합성기죠. 문제는 두 가지였습니다. (i) 안전이 "task 중 하나" 로 들어가면 다른 task 압력에 밀려 *진짜* 위반이 가능하고 (ii) 상위 정책이 끼어들 곳이 없습니다. autonomous 동역학뿐이죠.

저자들의 두 직관은 이렇습니다.

- *Pullback CBF*. 안전은 "task manifold 위에서 정의된 부등식 $`h_0(f(\sigma))\geq 0`$" 이고 그 부등식의 한 줄 또는 두 줄 미분이면 configuration 가속도에 대한 *선형 부등식* 으로 환원됩니다. 그러면 그 부등식을 QP 의 inequality constraint 로 박아 hard guarantee 가 됩니다.
- *Task manifold action*. 상위 정책의 출력을 task manifold 위 *force-like* 입력 $`u_l \in T^* N_l`$ 으로 정의하면 autonomous 가속도 $`\bar a`$ 위에 그만큼만 더 옮겨가도록 두 번째 QP 를 풀 수 있습니다. 입력이 0 이면 autonomous 동작이 그대로 살고, 어떤 값이 들어와도 안전 부등식은 같은 inequality 로 보호됩니다.

이 두 직관이 합쳐지면 *동일한 컨트롤러* 가 self-contained 자율 동작 (그래스핑·in-hand) 도, 상위 정책 (사람 조이스틱·RL·VLA) 의 잔차 조향 입력도 일관되게 받습니다.

> "We address these limitations by incorporating pullback control barrier functions, which produce sufficient conditions for a configuration-controlled robot to enforce task manifold safety." (§IV)
(한글 해설 — 본 논문이 PBDS 의 두 한계 (soft safety, 조향 부재) 중 *안전* 을 푸는 핵심 도구를 한 줄에 박은 anchor 문장입니다.)

![Figure 1 — SafePBDS 개요](https://arxiv.org/html/2605.21811/figures/fig_headline.png)

> "Figure 1: Overview of SafePBDS . At each control step, tasks on heterogeneous manifolds $(N_{i},g_{i})$ are pulled back to the configuration manifold $M$ and composed into a safe acceleration $\bar{a}$ via quadratic programs." (§I)
(한글 해설 — 이종 manifold 위의 task 들이 pullback 으로 configuration 가속도로 통합되고 autonomous (파란) · action (빨간) · safety (초록) 의 세 색이 분리된 채 하나의 QP 로 합쳐져 16-DOF Allegro Hand 의 palm-down IHR 까지 구동된다는 한 컷 요약.)

### 아키텍처

전체는 *제어 스텝당 두 QP 를 순차로 푸는* 구조이고 입력은 $`(\sigma, \dot\sigma) \in TM`$ 의 현재 상태, 출력은 configuration 가속도 $`\ddot\sigma`$ 입니다. 사용자가 사전에 디자인해 두는 객체가 셋입니다.

- **Behavior tasks** $`\{(f_i, g_i, \Phi_i, \mathcal{F}_{D,i}, w_i)\}_{i=1}^K`$ — 각 task manifold $`N_i`$ 위의 SMCS: task map, Riemannian metric, potential, dissipative force, weighting pseudometric. 예: end-effector pose tracking, joint damping, 핑거-객체 접촉 거리 끌어당기기.
- **Safety tasks** — pullback ECBF 인덱스 $`\mathcal{J}_E`$ 와 pullback BCBF 인덱스 $`\mathcal{J}_B`$. 각각 $`(f_j, h_{0,j}, \boldsymbol{\kappa}_j)`$.
- **Control tasks** $`\{(f_l, g_l, w_l, u_l)\}_{l=1}^L`$ — 상위 정책이 force-like 입력 $`u_l \in T^* N_l`$ 을 채워주는 채널. 입력 0 이면 자율.

알고리즘 (Algorithm 1) 의 흐름은 다음과 같습니다.

1. 안전 집합 $`\mathcal{A}_{\text{safe}} \leftarrow T_\sigma M`$ 초기화.
2. 모든 ECBF safety task $`j \in \mathcal{J}_E`$ 에 대해 pullback ECBF inequality (아래 식 IV-B) 의 half-space 로 $`\mathcal{A}_{\text{safe}}`$ 를 교차.
3. 모든 BCBF safety task $`j \in \mathcal{J}_B`$ 에 대해 pullback BCBF inequality 로 추가 교차.
4. **QP 1 (autonomous):** $`\bar a = \arg\min_{a \in \mathcal{A}_{\text{safe}}} \sum_i \tfrac{1}{2}\|Z_i(a) - S_i(\dot\sigma)\|^2_{F_i^* w_i}`$.
5. **QP 2 (steered):** action 입력이 있으면 (식 48) 을 다시 풀어 $`\ddot\sigma`$ 를 얻음.
6. $`\ddot\sigma`$ 반환.

PBDS 핵심 사상인 multi-task 합성은 식 (10) 의 weighted least-squares 형태로 표현됩니다.

$$\ddot{\sigma}(t)=\underset{a\in\mathcal{D}_{\dot{\sigma}(t)}}{\arg\min}\ \sum_{i=1}^{K}\frac{1}{2}\lVert Z_{i}(a)-S_{i}(\dot{\sigma}(t))\rVert^{2}_{F_{i}^{*}w_{i}}.$$

여기서 $`Z_i, S_i`$ 는 PBDS 의 pullback bundle 위 미분 사상이고 $`F_i^* w_i`$ 는 task 별 가중 pseudometric 입니다. 본 논문은 이 식에 $`\mathcal{A}_{\text{safe}}`$ 라는 추가 inequality 집합을 끼워 hard safety 를 강제합니다.

상위 정책 입력이 들어올 때는 식 (48) 로 확장됩니다.

$$\ddot{\sigma}(t)=\underset{a\in\mathcal{D}_{\dot{\sigma}(t)}\cap\mathcal{A}_{\mathrm{safe}}}{\arg\min}\ \sum^{K}_{i=1}\frac{1}{2}\lVert Z_{i}(a)-S_{i}(\dot{\sigma}(t))\rVert^{2}_{F_{i}^{*}w_{i}}+\sum^{L}_{l=1}\frac{1}{2}\lVert Z_{l}(a)-Z_{l}(\bar{a})-u_{l}^{\sharp}\rVert^{2}_{F_{l}^{*}w_{l}}.$$

첫 항은 식 (10) 그대로의 autonomous 목적이고 둘째 항이 *autonomous 가속도 $`\bar a`$ 에서 $`u_l^{\sharp}`$ 만큼 옮겨가는* residual injection 입니다. 입력이 0 이면 둘째 항이 vanish 해 첫 항만 남고 autonomous 와 동일.

> "Its first innovation is a pullback control barrier function construction, which converts task manifold safety conditions into linear constraints on configuration manifold accelerations." (§Abstract)
(한글 해설 — 본 논문의 첫 기여를 한 줄로 못 박는 anchor. task → config 변환을 *선형 부등식* 으로 떨어뜨린 게 핵심입니다. 그래야 QP inequality 로 박혀 hard guarantee 가 됩니다.)

> "The second innovation is a task manifold action interface that allows a high-level policy to inject low dimensional residual motions; zero input recovers the autonomous behavior, while safety is preserved under arbitrary inputs." (§Abstract)
(한글 해설 — 두 번째 기여인 action interface 의 *영입력 = 자율*, *임의 입력 = 안전 보존* 두 속성을 명시합니다. PROBE 의 System1↔System0 인터페이스 정의 ([D14](#ref-D14)) 와 구조적으로 가장 가까운 한 문장.)

### 학습 목표 / 손실

본 논문은 *학습 알고리즘이 아닙니다*. 손실 함수 대신 매 제어 스텝에서 푸는 두 convex QP 가 있습니다. 안전을 만드는 두 갈래 inequality 가 핵심입니다.

**Pullback ECBF (Theorem IV.1).** task manifold safety function $`h_0:N\to\mathbb{R}`$ 가 relative degree 2 일 때, configuration manifold 가속도 $`\ddot\sigma`$ 가 만족해야 하는 안전 부등식은 다음과 같습니다.

$$\frac{\partial(h_{0}\circ f)}{\partial\sigma^{i}}\ddot{\sigma}^{i}\geq-\frac{\partial^{2}(h_{0}\circ f)}{\partial\sigma^{i}\partial\sigma^{j}}\dot{\sigma}^{i}\dot{\sigma}^{j}-\kappa_{2}\dot{h}_{0}-\kappa_{1}h_{0}.$$

이 한 줄이 본 논문 첫 기여의 핵심 결과입니다. 좌변은 $`\ddot\sigma`$ 에 대해 *선형* 이므로 QP 의 half-space inequality 로 바로 들어갑니다. $`\kappa_1, \kappa_2`$ 는 ECBF gain 으로, $`F - G\boldsymbol{\kappa}^\top`$ 의 고유값 조건 (식 19) 을 만족하면 forward invariance 가 보장됩니다.

**Pullback BCBF (Theorem IV.3).** 안전 *속도장* $`\tilde\xi`$ 추종이 필요한 경우, BCBF candidate

$$h(x,\dot{x})=h_{0}(x)-\frac{\varepsilon}{2}\left\|\dot{x}-\mu_{x}\right\|_{N}^{2}$$

의 시간 미분 (Lemma IV.2, 식 45) 이 음수가 되지 않게 강제합니다. 이 갈래는 metric 의존성과 chart switching 측면에서 ECBF 보다 일반적이며, 안전 회복 (recovery) 능력도 더 robust 합니다.

**QP 1 — Autonomous safe acceleration:** 위 두 inequality 집합으로 $`\mathcal{A}_{\text{safe}}`$ 를 만든 뒤 식 (10) 을 풀어 $`\bar a`$ 를 얻습니다.

**QP 2 — Steered acceleration:** action 입력이 있으면 식 (48) 을 한 번 더 풀어 $`\ddot\sigma`$ 를 얻습니다. 두 QP 모두 *convex* 이라 실시간 풀이가 가능합니다.

### 학습 셋업

학습이 아닌 *제어 셋업* 입니다.

- **시뮬레이션 환경** — $`\mathbb{S}^{2}`$ 더블 인테그레이터는 자체 RK4 적분기. 7-DOF Franka 시뮬레이션은 MuJoCo [47].
- **하드웨어** — Franka Emika Panda 7-DOF arm + Wonik Allegro 16-DOF 다지손 (합 23-DOF). 팔은 [Deoxys](https://arxiv.org/abs/2402.02508) 프레임워크로 20 Hz 제어, PBDS 활성 시 joint impedance, pre-grasp 접근 시 joint position. 손은 ZMQ 로 joint-level PD 와 Cartesian 핑거팁 impedance 모드 혼용.
- **인식 스택** — Intel RealSense D435 + Segment Anything (분할) + FoundationPose (6-DOF pose tracking, 10 Hz). 객체 메시는 KIRI Engine + LiDAR iPhone 으로 스캔.
- **객체 모델링** — 추적된 객체 자세는 MuJoCo 시뮬레이션 안의 객체로 반영, PBDS 컨트롤러가 그 시뮬레이션을 *online model* 로 사용해 동작.
- **하이퍼파라미터** — 별도 데이터셋 학습이 아니므로 ML 류 하이퍼는 없음. CBF gain $`(\kappa_1, \kappa_2)`$, task 가중 pseudometric $`w_i`$, BCBF $`\varepsilon`$, dissipation 계수 등이 *수작업* 으로 task 별 튜닝됩니다. 그래스핑에는 84 개 ECBF task, in-hand reorientation 에는 61 개 ECBF task 가 인스턴스화되며 매 스텝 *active subset* 만 활용됩니다 (FSM 으로 토글).

---

## 📊 실험 설정과 결과

### $`\mathbb{S}^{2}`$ 더블 인테그레이터 (Section VI)

12 개 run 구성 (Table II) 으로 chart invariance · safety recovery · multi-task composition · action interface 의 이론 속성을 모두 확인합니다.

- *Chart invariance* — geometric (round metric) PBDS 는 north/south stereographic chart 전환에도 동일 trajectory; flat metric 은 chart 의존성 노출.
- *Safety recovery* — 의도적으로 unsafe 시작 (run vi, vii) 에도 ECBF / BCBF 모두 안전 집합으로 복귀.
- *Action interface* — run (viii) 영입력 = autonomous trajectory, run (ix)/(x) $`\pm u_\perp`$ 입력 = 안전을 유지한 채 트래젝토리 호모토피 분기, run (xi) $`u_{\text{unsafe}}`$ 의도적 위험 입력에도 안전 제약 유지.

### 7-DOF Franka 시뮬레이션 (Section VII)

End-effector tracking + workspace obstacle avoidance ablation:

| Setup | 실험 수 | 결과 |
|---|---|---|
| 6-DOF pose tracking, 단일 장애물 | 1 | 전체 시스템 회피 성공 / ECBF 제거 ablation 통과 |
| Random $`\mathrm{SO}(3)`$ tracking + 무작위 장애물 (반경 8 cm) | 50 | 전체 시스템 50/50 안전 (min $`h_{\text{obs}}=+0.010`$), ECBF 제거시 11/50 위반 (min $`h_{\text{obs}}=-0.080`$) |

> "The full system is safe in all 50 runs (min $h_{\mathrm{obs}}=+0.010$), whereas the ablation violates the obstacle constraint in 11 of 50 runs (min $h_{\mathrm{obs}}=-0.080$); all runs reach the goal orientation." (§VII-A)
(한글 해설 — pullback ECBF 의 *효과 분리* 가 가장 깔끔하게 드러나는 ablation. 두 시스템 모두 목표 자세에는 수렴하지만 안전 제약은 ECBF 가 있어야 깨지지 않습니다.)

### 23-DOF 실로봇 — Dexterous Grasping (Section VIII-C)

![Figure 4 — 23-DOF Franka–Allegro 하드웨어 셋업](https://arxiv.org/html/2605.21811/figures/system_setup.jpg)

> "Figure 4: Hardware setup for the dexterous manipulation experiments: a 7-DOF arm equipped with a 16-DOF dexterous hand, a camera for runtime perception, and household objects used for grasping and in-hand reorientation." (§VIII-A)
(한글 해설 — Franka Panda 7-DOF + Allegro 16-DOF 의 23-DOF 결합 시스템과 카메라 1 대, 20 종 일상 물체로 구성된 실험 셋업. 한 컷으로 task 의 hardware footprint 를 보여줍니다.)

20 객체 × 객체당 2–6 trial = 총 120 trial 의 4-finger 그래스핑, 3 객체 × 4 손가락 제외 × 3 위치 = 36 trial 의 3-finger 그래스핑.

| Setup | Trials | Success | 성공률 |
|---|---|---|---|
| 4-finger 그래스핑 (20 객체) | 120 | 111 | 92.5% |
| 4-finger, 객체별 만점 (6/6) | 20 | 15 | 75% (20 객체 중 15 객체 perfect) |
| 3-finger 그래스핑 (3 객체, 4 손가락 제외) | 36 | 34 | 94.4% |

![Figure 7 — 객체 무게 × 수직 높이 별 그래스핑 결과](https://arxiv.org/html/2605.21811/x6.png)

> "Figure 7: Per-(object, pose) grasp outcomes plotted against object weight and the vertical bounding-box length at the tested pose." (§VIII-C2)
(한글 해설 — *수직 높이가 작고 무거운* 객체에서 실패가 집중되는 시각화. 낮은 수직 높이는 pose 추정 오차에 민감하고 높은 무게는 저수준 impedance 컨트롤러와 손 하드웨어 한계에 닿는다는 진단을 한 컷에 담습니다.)

> "SafePBDS achieves an overall success rate of $111/120$ ($92.5\%$) on the $20$ household objects, with $15$ of $20$ attaining full $6/6$ success." (§VIII-C2)
(한글 해설 — 전체 성공률과 *객체별 perfect* 분포를 동시에 보고. 평균치 위주가 아닌 *고난도 객체에서 실패가 집중* 한다는 점이 함께 드러나는 anchor.)

> "Across the three objects and four exclusions, tested at three table locations each ($36$ trials), SafePBDS achieves $34/36$ ($94.4\%$); both failures occur on the wide object (bottom row) with the thumb excluded." (§VIII-C2)
(한글 해설 — 3-finger ablation 의 결과 인용. 자율 PBDS 행동을 그대로 두고 ECBF 변형 + 1D action 만 교체한 *config 수준 수정* 만으로 그립 성공률 94.4% 가 나옵니다. 상위 정책이 손가락 선택을 다양화할 여지를 보여주는 결과입니다.)

### 23-DOF 실로봇 — Palm-Down In-Hand Reorientation (Section VIII-D)

오프라인 DFS 트리 서치로 finger gaiting 시퀀스를 사전 계획 → 실로봇에서 open-loop 재생.

| 조건 | 결과 |
|---|---|
| (i) arm static, 무하중 | 360° 이상 회전 (양방향) |
| (ii) arm static, 병 안에 ≤98 g 추가 하중 점진 투입 | 360° 이상 회전 (양방향) |
| (iii) arm swinging, 병 안에 70 g 느슨한 하중 | 360° 이상 회전 (양방향) |

> "Using the same open loop motion plan across all three conditions, SafePBDS achieves over $360^{\circ}$ rotation in both directions. We attribute this robustness to the fact that our IHR plan is certifiably in force closure." (§VIII-D3)
(한글 해설 — *open-loop* 동일 plan 으로 세 조건 모두 360° 이상 회전한다는 결과는, 본 논문의 force closure ECBF 가 plan 자체를 *공인된* 그립 안에 가둬 둔 덕분이라는 해석. 상위 plan 의 burden 을 *낮추는* 가장 명확한 evidence.)

> "SafePBDS enables the first model-based, fully actuated palm-down in-hand reorientation, producing over $360^{\circ}$ rotation in both directions under varying object weight and arm motion." (§IX)
(한글 해설 — Discussion 의 한 줄 자평. *model-based, fully actuated* palm-down IHR 의 첫 사례라는 위치 선언이며, RL 기반 [HORA](https://arxiv.org/abs/2210.04887) / [AnyRotate](https://arxiv.org/abs/2405.07391) 계열과 결을 달리합니다.)

---

## ⚖️ 한계

- **국소 모션 정책** — vector-field 정책의 일반 한계와 동일하게 SafePBDS 도 *local* 모션 생성이며 장기 horizon 에서는 local minima 에 갇힐 수 있습니다. 탈출은 action interface 를 채우는 *상위 정책* 의 책임으로 명시.
- **Kinematic 가정** — SafePBDS 는 가속도 명령만 만들고 그 가속도의 실현은 lower-level tracker 또는 impedance 컨트롤러에 위임합니다. 접촉 force 자체를 추론하지 않으므로 compliant interaction 이 필요한 시점에 impedance 층이 별도로 필요.
- **Surjective submersion 가정 (Assumption 1)** — pullback 유도가 fully actuated / over-actuated 시스템을 가정합니다. underactuated robot 은 현재 framework 밖.
- **수작업 task 디자인 비용** — 그래스핑 84 ECBF task / IHR 61 ECBF task 등 task / FSM / 가중치를 사용자가 일일이 설계해야 합니다. *학습된* prior 가 자동으로 채워주는 영역이 없습니다.
- **하드웨어 한계 노출** — Figure 7 의 실패 분포는 *낮은 수직 높이 + 무거운 객체* 에서 집중. 알고리즘 한계가 아니라 perception 정확도, 저수준 impedance 컨트롤러, 손 hardware capability 의 결합 한계로 진단됩니다.
- **3-finger 실패 (2/36)** — 폭이 넓은 객체에서 *엄지 제외* 했을 때 index–ring pinch 가 손의 reachable workspace 한계 근처. 알고리즘이 아니라 hand reachability 의 문제.
- **IHR 은 open-loop** — finger gaiting 시퀀스 자체는 *오프라인* DFS 로 사전 계산되고 실로봇에서는 그대로 재생 (perturbation 대응은 force closure CBF 가 잡아 줌). closed-loop sequential planning 은 future work.

---

## ♻️ 재현성

- **코드/체크포인트** — 본문에서 공개 여부 명시 없음. demo video 와 프로젝트 페이지는 [tml.stanford.edu/safe-pbds](https://tml.stanford.edu/safe-pbds) 로 안내됨.
- **시뮬레이션** — MuJoCo [47] + 자체 RK4 적분기 ($`\mathbb{S}^{2}`$).
- **하드웨어** — Franka Panda 7-DOF + Wonik Allegro 16-DOF. Deoxys 프레임워크, Intel RealSense D435, FoundationPose, Segment Anything. 메시 스캔은 KIRI Engine + LiDAR iPhone.
- **모델링** — 객체 메시와 손 / 팔 URDF 가 필요한 model-based 접근. policy 학습 데이터셋은 *없음*.
- **재현 비용** — RL training 비용 0. QP 풀이 (e.g. OSQP / qpSWIFT 류) 의 실시간성이 핵심. 하드웨어 셋업·perception 스택·물체 메시 준비가 가장 큰 부담.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **[P3](#ref-P3) — Hand-level System0 Module (RL-scoped)** : 가장 직접적인 연결. SafePBDS 는 PROBE 의 System0 자리에 들어갈 수 있는 *model-based, RL-free* 안전 보장 층의 한 후보로 읽힙니다. 특히 [D13](#ref-D13) (System0 role: post-grasp 안정화) 의 *grasp 유지 → force closure ECBF* 가 직접 매핑되고 [D14](#ref-D14) (System1↔System0 인터페이스) 의 옵션 (ii) "continuous blend weight" 또는 (iii) "always-on residual" 의 *기하학적으로 깔끔한 변형* 이 본 논문의 task manifold action interface 입니다. 다만 PROBE 의 v1 D14 는 (i) binary on/off 이고 SafePBDS 의 *입력 0 = autonomous, 입력≠0 = residual* 은 (iii) 에 더 가까워 v1 결정과는 *다른 선택지* 를 제시합니다. 또한 SafePBDS 는 RL 이 아닌 model-based 라 D17 (PPO 기반 System0 spec) 자체를 옮기지는 않고, *대안* 으로 RL 대신 model-based 안전 층을 쓰는 시나리오를 비춥니다.
- **[P1](#ref-P1) — Heterogeneous Body/Hand Action Expert (보조)** : SafePBDS 자체는 action decoder 가 아니지만, *상위 정책 (= HandExpert / BodyExpert) 의 출력을 task manifold force-like 입력으로 안전하게 받아 주는 인터페이스 채널 역할* 을 합니다. [D6](#ref-D6) (Coordination direction & flow) 와 D7 (π backbone integration) 의 *하위 layer 가 무엇인지* 에 대한 한 선택지로, VLA action 을 곧장 joint command 로 보내는 대신 SafePBDS 의 action interface 를 거치게 하는 옵션입니다.
- **[CP3](#ref-CP3) — tool articulation 데모 진입 시점** : palm-down IHR 360° 가 *model-based* 로 달성된 evidence 는 PROBE 의 phase-2 tool articulation 데모에서 *손바닥 아래로 도구를 잡고 회전* 같은 sub-task 의 가능성 reference 가 됩니다.
- **§10 경쟁자 함의** — Anti-topic "RL reward-engineering for generalized full-task" 와 충돌하지 않고, 오히려 *RL 의 영역 (System0 stabilization)* 을 *얇은 model-based 층* 으로 대체 가능하다는 evidence 가 제시됩니다. 이 결과는 PROBE 의 RL-scoped 정신과 결을 같이 하지만, "RL 이 필요한 유일 지점" 이라는 P3 정체성 주장에는 *대안 가설* 을 던집니다. C. Karen Liu (Stanford) 는 §9.1 cross-pillar researchers 목록에 이미 등재되어 있어 추가 author watch 는 불요.

| Code | Meaning |
|------|---------|
| <a id="ref-P1"></a>**P1** | Heterogeneous Body/Hand Action Expert (pillar) |
| <a id="ref-P3"></a>**P3** | Hand-level System0 Module — RL-scoped contact stabilization (pillar) |
| <a id="ref-D6"></a>**D6** | Coordination direction & flow (P1) |
| <a id="ref-D13"></a>**D13** | System0 role & operating regime — post-grasp 안정화 등 (P3) |
| <a id="ref-D14"></a>**D14** | System1↔System0 interface — v1 binary on/off, bypass-when-off (P3) |
| <a id="ref-D17"></a>**D17** | System0 RL policy spec — PPO, contact reward, hand-crafted v1 (P3) |
| <a id="ref-CP3"></a>**CP3** | Checkpoint 3: tool articulation 데모 진입 |

---

## ✨ 핀 논문 대비 델타

- **vs. [HORA (Qi et al., 2022)](https://arxiv.org/abs/2210.04887) — P3 핀, 인핸드 회전 원형** : HORA 는 RL + privileged teacher → 촉각 student distill 로 in-hand 회전을 학습합니다. SafePBDS 는 *학습 없이* 모델·기하·QP 만으로 palm-down IHR 360° 를 달성합니다. *손이 위로* (HORA) vs *손바닥 아래* (SafePBDS) 라는 더 어려운 변형에서 *model-based first* 라는 위치를 가져갑니다. 새로움의 핵심은 *기법* (RL→QP) 보다도 *어떤 task 까지 model-based 로 가능한지의 경계 이동* 입니다.
- **vs. [AnyRotate (Yang et al., 2024)](https://arxiv.org/abs/2405.07391) — D17 reward 직접 reference** : AnyRotate 의 학습 가능한 reward 와 비교하면, SafePBDS 는 reward 가 아예 없는 *제약 만족* 접근. 두 접근은 *직접 대체* 가 아니라 *다른 축* 에서 안정 그립을 다룹니다. AnyRotate 의 reward term 은 SafePBDS 의 ECBF 안전 함수로 *형식 변환* 이 가능합니다.
- **vs. [Shared-Autonomy Arm-Hand VLA / DexGrasp-VLA (arXiv:2511.00139)](https://arxiv.org/abs/2511.00139) — P1 핀, 해부학적 split** : DexGrasp-VLA 의 *VR-teleop arm + autonomous hand VLA* 같은 split 에서, SafePBDS 의 task manifold action interface 는 *arm 입력을 안전하게 받는 채널* 의 후보 인터페이스가 됩니다. DexGrasp-VLA 는 VLA + sharing autonomy 측, SafePBDS 는 그 *밑단* 의 model-based 안전 층 측에서 같은 split 정신을 만나는 다른 단면.
- **vs. [π0.5 (Physical Intelligence, 2025)](https://arxiv.org/abs/2504.16054) — D14 reference** : π0.5 의 hierarchical inference (System1 / System0 analog) 는 *주파수와 추상화 수준* 의 분리이지 *안전 보장* 의 분리는 아닙니다. SafePBDS 는 동일한 분리를 *수학으로 정의된 안전 집합* 으로 강화한 변형이며 π0.5 의 인터페이스 추상화에 *certifiable safety contract* 가 붙은 모양.
- **vs. [PBDS (Bylard et al., 2021)](https://arxiv.org/abs/2105.00638) [참고문헌 6]** : 원본 PBDS 는 metric-based soft safety 만 다뤘고, 본 논문의 두 기여 (pullback CBF + action interface) 가 정확히 그 두 한계를 풉니다. *진정으로 새로운* 점은 안전 부등식이 task manifold 의 임의 차원에서 configuration manifold 가속도의 *선형* 부등식으로 환원된다는 결과 (Theorem IV.1) 와, 안전을 깨지 않는 action injection 의 *2-단계 QP* 구조입니다.

---

## ⚙️ 의사결정 함의

본 논문이 옳다면 PROBE 의 System0 / 안전 / 인터페이스 영역에서 다음이 바뀝니다.

- **[D14] System1↔System0 인터페이스 v1 재검토 후보** — 현재 v1 은 binary on/off (옵션 i). SafePBDS 의 *입력 0 = autonomous, 입력≠0 = safety-preserving residual* 은 옵션 (iii) "always-on residual" 의 기하학적·certifiable 구현입니다. CP1 ablation 에서 binary 전환이 *finger-command 불연속* (D14 의 deferred trigger) 을 일으킨다면, SafePBDS 의 task manifold action interface 형태를 *옵션 (iii) 구체 후보* 로 올리는 결정이 가능합니다. config 키 후보: `system0_interface.mode = "safety_qp_residual"`, `system0_interface.task_manifolds = [...]`.
- **[D13] System0 의 *대안* 후보 — model-based safety layer** — PROBE 의 v1 System0 는 PPO + Isaac Lab RL policy 입니다. SafePBDS 는 *동일 역할 (slip 억제 / grasp 유지)* 을 RL 없이 force closure ECBF + per-finger contact ECBF 로 강제합니다. 이 구성은 D13 의 *대체 후보* 가 되며, *RL 이 필요한 유일 지점* 이라는 P3 정체성 주장의 *반례* 후보로 검토 대상입니다. 의사결정 함의: RL 학습 비용·sim2real 부담을 *수작업 task 디자인 비용* 과 trade 하는 선택지가 명시적으로 추가됩니다.
- **[D17] System0 reward → ECBF 함수 변환 옵션** — AnyRotate 류의 reward term (object retention · slip suppression · contact stability) 은 SafePBDS 의 안전 함수 $`h_0(x)`$ 로 변환 가능. 의사결정 함의: D17 의 hand-crafted reward 가 만일 sim2real 격차로 실패할 경우 (D18 trigger), reward 를 ECBF 안전 함수로 *형식 재구성* 한 hybrid (RL + safety QP) 가 후보로 들어옵니다.
- **[D6] Coordination direction & flow 의 *하위 layer*** — HandExpert / BodyExpert 의 출력을 *직접 joint command* 로 보낼지, 아니면 *task manifold force-like 입력* 으로 보내 SafePBDS 같은 안전 층을 거칠지의 옵션이 추가됩니다. 후자는 [D2](#ref-D2) (Body output space = both-wrist / tool-flange pose) 와 자연스럽게 결합되며, pose 명령이 곧 task manifold $`\mathrm{SE}(3)`$ 위의 control task 가 됩니다.
- **CBF gain 의 sanity check 비용** — pullback ECBF / BCBF 의 gain $`(\kappa_1, \kappa_2)`$ 는 *고유값 조건* 으로 forward invariance 가 보장되지만, 실제 trajectory quality 는 튜닝에 민감. PROBE 가 이 방향을 채택한다면 CBF gain tuning 도구·평가 메트릭이 새 평가 항목으로 들어옵니다 ([D26](#ref-D26) 후보).

특별히 모호하지 않은 구체 결정은 위 다섯이며, 그중 가장 큰 결단은 *System0 자리에 RL 대신 model-based safety layer 를 둘 가능성* 입니다. 이 가능성은 P3 의 *Identity tie* (RL 이 필요한 유일 지점) 와 정면으로 부딪히므로 컨텍스트 변경 제안 (아래 💡) 으로 따로 적습니다.

| Code | Meaning |
|------|---------|
| <a id="ref-D2"></a>**D2** | Body output space — v1 both-wrist / tool-flange pose (P1) |
| <a id="ref-D26"></a>**D26** | Evaluation protocol (P5) |

---

## ⚠️ 먼저 검증할 실패 모드

- **Task 미스매치 — palm-down IHR vs in-hand *cube* rotation** : SafePBDS 가 보여준 IHR 은 *6 cm 병* + 손바닥 아래, finger gaiting + DFS pre-plan 의 조합입니다. PROBE 의 [phase 1 데모](#ref-D24-like) 는 in-hand *cube* 회전이라 객체 형상·접촉 모델이 다릅니다. 가장 싼 sanity check: SafePBDS 의 force closure ECBF 가 cube 같은 *평면 접촉 + 모서리* 에서도 numerically 동일하게 잘 작동하는지 시뮬레이션 (MuJoCo) 으로 단일 객체 미니 ablation.
- **Hardware 미스매치 — Allegro vs Sharpa Hand** : SafePBDS 의 ECBF gain · task 가중치는 Allegro 의 기구·강성·sensing 한계에 맞춰 튜닝됐습니다. PROBE 의 [v1 hardware Sharpa Hand (22-DOF, no wrist DOF)](#ref-sharpa) 에 옮길 때 *촉각 모달리티 (Sharpa Deform Map)* 가 SafePBDS 의 perception (FoundationPose + RGB-D 외부 카메라) 과 *전혀 다른 정보* 라는 점이 큰 불확실성. SafePBDS 는 object pose tracking 에 강하게 의존하지만 PROBE System0 는 *vision-excluded* 가 원칙 (D15) 이라 의미 단위 mismatch 가 있습니다.
- **수작업 task 디자인 비용 폭증** — 84 ECBF task 의 *손 작업* 디자인 비용은 단일 task 데모에서는 감당되지만 phase-2 tool articulation (5-tool eval set, CATFA precedent) 으로 확장하면 *도구별로 task 를 다시 설계해야 할 가능성* 이 큽니다. 가장 싼 sanity check: 5-tool 중 1 도구에 SafePBDS 의 task 디자인을 옮겨 보고 task 정의·CBF 함수 디자인 *시간* 을 측정.
- **QP 풀이 시간 + 다지 손 자유도** — 23-DOF + 다중 inequality 의 online QP 가 실로봇 control rate (논문은 arm 20 Hz) 에서 풀린다고 보고하지만, PROBE 의 phase-2 22-DOF Sharpa + arm 7-DOF = 29-DOF 에서 *더 빠른 제어 주기* 가 필요하면 QP solver 의 latency 가 병목이 될 수 있습니다.
- **Action interface 의 의미 매핑** — task manifold 위 force-like 입력 $`u_l`$ 을 *상위 정책* 이 어떤 의미로 채워야 할지는 본 논문에서 사용자 책임으로 남겨져 있습니다. HandExpert / BodyExpert 의 출력 ([D3 finger joint command](#ref-D3-like) / D2 wrist pose) 을 task manifold force-like 입력으로 *재해석* 하는 매핑은 자연스럽지 않을 가능성이 있습니다. 가속도 단위 변환 (sharp operator) 과 모달리티 분리가 필요한 지점.
- **Open-loop IHR 의 일반화 한계** — IHR 360° 결과는 *동일 plan* 의 open-loop 재생인데, perturbation 강도가 더 커지거나 객체 형상이 다른 상황에서는 plan 자체를 *online* 으로 재계산해야 합니다. DFS 트리 서치의 계산 비용이 *실시간* 으로 옮겨지면 framework 의 *실시간성* 주장에 부담이 생깁니다.

---

## 💡 컨텍스트 제안

- **§5 P3 Identity tie 의 *대안 가설* 한 줄 추가** — 현 P3 "System0 = the *only* RL component" 는 SafePBDS 의 evidence (model-based 로도 grasp 유지·force closure 가능) 에 비추어 보면 *대체 가능성* 이 열립니다. context 수정은 사람 책임이므로 이 자리에서 제안만 합니다. "System0 의 RL 필연성은 *task / hardware 종속* 일 가능성. model-based safety QP (e.g. SafePBDS, [arXiv:2605.21811](https://arxiv.org/abs/2605.21811)) 가 동일 역할을 수행한 evidence 가 존재" 한 줄을 P3 Anti-topics 또는 §10 Architectural-sibling 영역에 보태는 게 자연스럽습니다.
- **§8.3 P3 핀 후보 — 보충 검토 권고 (핀 등재는 권하지 않음)** — SafePBDS 자체를 P3 핀으로 올리는 것은 ≤8 한도와 RL 중심 라인업 (HORA · AnyRotate · CCGE · RMA · Static Friction Sim2Real · Contact-Aware Neural Dynamics · π0.5) 의 우선순위 측면에서 *권하지 않습니다*. 다만 §8.3 **Methodology base** 또는 §10 (Competitor / Kindred Monitoring) 의 *model-based safety alternative* 슬롯에 "SafePBDS = model-based palm-down IHR 360° + pullback CBF + task manifold action interface ([arXiv:2605.21811](https://arxiv.org/abs/2605.21811))" 한 줄 인용을 권합니다.
- **§6 [D14] deferred candidate 보강** — 현 D14 deferred 는 "(ii) continuous blend → trigger: hard switching causes finger-command discontinuity / CP2" 만 있습니다. *(iii) safety-preserving residual injection (SafePBDS 형)* 옵션을 deferred candidate 로 추가하는 게 가능합니다. trigger 는 동일하게 "CP2 의 binary on/off 가 acceleration discontinuity 를 일으킬 때".
- **§9.1 cross-pillar researchers** — C. Karen Liu (Stanford) 는 이미 cross-pillar 목록에 등재. 본 논문이 *공인된 evidence* 로 우선순위를 올릴 author 인지의 별도 메모는 사람 판단.
- **§14 Open Items 후보** — *"phase-2 hand expert 의 출력 인터페이스: 직접 joint command vs task manifold force-like input"* 한 줄을 새 open item 으로 검토 권고 (P1 / P3 모두 걸침).

<a id="ref-D24-like"></a><a id="ref-D3-like"></a><a id="ref-sharpa"></a>

---

> 💡 base 매핑은 `/foundry analysis/2605.21811/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
