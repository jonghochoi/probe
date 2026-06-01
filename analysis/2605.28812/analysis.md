# Paper Analysis — Beyond Binary: Sim-to-Real Dexterous Manipulation with Physics-Grounded Contact Representation

> PROBE analysis 모드 산출물. 단일 한글 문서이며, 영문 1차 파일은
> 없습니다. 형식·이모지·용어 규칙은 `docs/STYLE.md` §5 / §4 를
> 정확히 따릅니다. 재실행 시 이 파일을 덮어씁니다.

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Beyond Binary: Sim-to-Real Dexterous Manipulation with Physics-Grounded Contact Representation |
| 저자 | Jiahe Pan, Stelian Coros, Jitendra Malik, Toru Lin (ETH Zürich · UC Berkeley) |
| 링크 | [arXiv:2605.28812](https://arxiv.org/abs/2605.28812) |
| 발행일 / 버전 | 2026-05-27 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-05-29 |

---

## 🧭 한 줄 요약 (TL;DR)

촉각 센서의 raw taxel 신호를 물리 원리에 기반한 압력 중심(Center-of-Pressure, 3D 접촉력 벡터 + 3D 접촉 위치)으로 압축해, 학습된 촉각 인코더나 교사-학생 distillation 없이 다지 손의 접촉 집약적 정책을 zero-shot 으로 Sim2Real 전이하는 방법을 제안합니다. 단순화된 binary 접촉과 raw taxel 양쪽을 모두 능가합니다. 정책의 잠재 표현은 물체 질량 같은 물리량을 부수적으로 인코딩합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 접촉 집약적 다지 조작은 실세계 데이터 수집 비용이 큽니다. 대안인 Sim2Real 강화학습은 촉각처럼 정보 밀도가 높은 모달리티를 시뮬레이션-실환경 격차 때문에 제대로 쓰지 못합니다. 촉각을 살리면서 전이도 되는 표현이 필요합니다.
- **기존 접근의 한계** — 기존 Sim2Real 방법은 격차를 줄이려고 촉각을 binary·ternary 같은 거친 저차원 특징으로 단순화하면서 복잡한 조작에 필요한 풍부함을 희생합니다. 반대로 raw 촉각에 가까운 표현은 정보가 풍부한 대신 센서 특화적이라 시뮬레이터 접촉량과 정렬하기 어렵습니다.
- **본 논문의 가설** — 접촉을 3D 힘 벡터 + 3D 접촉 위치라는 물리 기반 중간 표현(CoP)으로 요약하면, 시뮬레이션과 하드웨어 사이에서 정렬할 만큼 충분히 압축적이면서도 접촉 집약적 제어에 필요한 힘·위치 정보를 보존하는 "중간 지점"을 얻을 수 있습니다.
- **왜 지금 중요한가** — 조작이 더 정밀해질수록 정책은 세밀한 물리 상호작용을 추론해야 합니다. 이때 효과적 촉각 표현이 없으면 Sim2Real 강화학습을 더 어려운 과제로 확장하기 어렵고, 바로 이 점이 핵심 병목입니다.

---

## 🧩 핵심 기여

- 물리 원리에 기반한 촉각 표현 **Center-of-Pressure (CoP)** 를 제안합니다 — 로봇 링크에 작용하는 총 접촉력 3D 벡터와 3D 접촉 위치로 국소 촉각 정보를 요약하며, raw taxel 의 dense 정보를 보존하면서 Sim2Real 강건성을 유지합니다.
- raw taxel 힘과 CoP 표현 사이의 **미분 가능한 양방향 매핑**을 응력 분포 모델로 유도해, 시뮬레이션의 CoP 접촉량과 하드웨어 taxel 측정값을 실용적으로 상호 변환합니다.
- ground-truth 힘 측정 없이 taxel 방향(orientation)을 추정하는 **미분 가능 동역학 기반 센서 캘리브레이션**을 제안합니다. 정적 평형의 관절 토크와 촉각에서 추론한 외력을 정합시켜 학습합니다.
- 시각 단서가 거의 없는 두 개의 "blind" 접촉 집약적 과제(peg-in-hole 삽입, 공 균형 잡기)에서 다지 손으로 **zero-shot Sim2Real 전이**를 달성하며 binary 접촉과 raw taxel baseline 을 모두 능가합니다.
- CoP 조건부 정책의 잠재 상태는 물체 질량 같은 **과제 관련 물리량을 제어의 부수적 산물로 인코딩**합니다. linear probing 과 PCA 군집 분석으로 이를 보입니다.

---

## 🔑 기술 키워드

- **Center-of-Pressure (CoP)** — 분산된 접촉 압력 분포를 단일 힘 벡터 + 단일 접촉점으로 환원한 국소 접촉 기술자(descriptor). 발바닥에 실린 무게중심을 한 점으로 보는 것과 같은 개념을 손끝 접촉에 적용한 것입니다.
- **Taxel** — 촉각 센서 어레이의 개별 감지점. 각 taxel 이 3축 힘을 측정하며, XELA uSkin 처럼 격자형으로 배열됩니다.
- **Sim2Real (시뮬레이션-실환경 이전)** — 시뮬레이션에서 학습한 정책을 실제 로봇으로 옮기는 것. 본 논문은 촉각 표현을 정렬해 추가 학습 없이 zero-shot 전이를 노립니다.
- **응력 분포 모델 (stress distribution model)** — 접촉력이 부드러운 실리콘 층을 통해 퍼지며 거리에 따라 감쇠하는 현상을 Gaussian 가중치로 근사한 저파라미터 모델. CoP 와 taxel 힘을 잇는 매핑의 핵심.
- **미분 가능 동역학 캘리브레이션** — taxel 프레임의 미지 회전을, 정적 평형에서 관절 토크와 촉각 기반 추정 토크의 MSE 를 역전파해 학습하는 절차. 힘 센서 ground-truth 없이 캘리브레이션합니다.
- **비대칭 actor-critic PPO** — actor 는 고유수용감각 + 접촉 표현만, critic 은 특권(privileged) 물체 상태까지 받는 PPO 구성. 특권 정보로 가치 추정을 돕되 정책은 전이 가능한 관측만 씁니다.
- **Blind manipulation** — 시각 입력 없이 고유수용감각과 접촉 피드백만으로 수행하는 조작. 촉각의 역할을 분리해 측정하기 위한 과제 설계.
- **Secondary contact** — 손-물체(primary) 가 아니라 조작 물체와 또 다른 과제 물체 사이의 접촉. 정책이 primary 촉각으로 secondary 상태를 암묵 추론해야 해 난도가 높습니다.
- **Linear probing** — 학습된 정책 잠재 벡터에 선형 회귀를 얹어 어떤 물리량(공 위치·속도)이 인코딩됐는지 검사하는 진단 기법.

---

## 🔬 방법론

### 직관

핵심 직관은 촉각 표현의 "충실도 ↔ 전이성" 트레이드오프에 중간 지점을 두는 것입니다. binary 같은 단순 표현은 전이는 잘 되지만 정보가 거칩니다. 반대로 raw taxel 은 정보가 풍부한 대신 센서 특화적이라 시뮬레이터 접촉량과 맞추기 어렵습니다.

> "To balance this trade-off, we introduce Center-of-Pressure (CoP), a physics-grounded representation that summarizes local tactile information as a 3D contact force vector and a 3D contact location." (§1)
> (한글 해설 — CoP 는 접촉력 벡터와 접촉 위치라는 두 물리량으로 국소 촉각을 요약합니다. 이 둘은 대부분의 강체 시뮬레이터가 접촉쌍 정보로 직접 제공합니다. 그래서 학습된 인코더 없이도 시뮬레이션-하드웨어 정렬이 가능하다는 것이 설계의 출발점입니다.)

시뮬레이터(IsaacSim, MuJoCo 등)는 물체 간 3D 접촉력 벡터와 접촉 위치를 world frame 으로 제공합니다. 하드웨어 taxel 신호를 같은 CoP 좌표계로 사상할 수만 있으면 시뮬레이션에서 배운 정책이 실세계에서 같은 형태의 관측을 받습니다.

### 아키텍처

CoP 는 둥근 손끝에서 센서 프레임 $`\mathcal{S}`$ 으로 표현된 총 접촉력 벡터 $`{}^{\mathcal{S}}f_{\rm{cop}}\in\mathbb{R}^{3}`$ 와 3D 접촉 위치 $`{}^{\mathcal{S}}p_{\rm{cop}}\in\mathbb{R}^{3}`$ 로 구성됩니다.

![Figure 1 — CoP representation & stress model](https://arxiv.org/html/2605.28812/x1.png)

> "Figure 1: (a) CoP representation. (b) The proposed stress distribution model for XELA uSkin sensors [42]." (§3.1)
(한글 해설 — 왼쪽은 손끝에 작용하는 접촉력 벡터와 접촉점으로 정의되는 CoP, 오른쪽은 taxel 프레임과 센서 프레임 사이 변환을 나타냅니다. 본문 §3.1–§3.2 의 표현 정의와 매핑을 시각화합니다.)

센서 어레이는 격자형으로 배열된 $`N`$ 개의 taxel 로 이루어지고, $`i`$ 번째 taxel 의 국소 프레임 $`\mathcal{T}_{i}`$ 는 센서 프레임 기준 위치 $`{}^{\mathcal{S}}p_{i}\in\mathbb{R}^{3}`$ 와 회전 $`R_{i}\in\mathbb{SO}(3)`$ 로 주어집니다. 각 taxel 힘 $`{}^{\mathcal{T}_{i}}f_{i}\in\mathbb{R}^{3}`$ 는 법선·전단 성분을 모두 포함합니다.

**Taxel-CoP 매핑.** 단순히 개별 taxel 힘을 합하거나 평균 내는 방식은 부드러운 실리콘 층을 통한 힘 확산을 무시하므로 합력과 접촉 위치가 모두 편향됩니다. 대신 응력 분포 모델을 둡니다. CoP 힘 벡터를 법선 $`f_{n}`$ 과 전단 $`f_{s}`$ 성분으로 분해한 뒤, 변형에 따른 방향 변화와 접촉점으로부터의 거리에 비례하는 크기 감쇠를 모델링해 taxel 별 유효 힘 $`f_{i}`$ 를 만듭니다.

### 학습 목표 / 손실

**Forward mapping (CoP → taxel).** 곡면 손끝의 법선 $`\hat{n}_{\rm{cop}}`$ 을 taxel 법선의 inverse-distance weighting 으로 근사하고, taxel 의 국소 법선 $`\hat{n}_{i}`$ 과 CoP→taxel 방향 $`\hat{v}_{i}`$ 를 Gaussian 반경 가중치로 보간한 "blended" 방향 $`\hat{b}_{i}`$ 으로 유효 법선력 방향을 근사합니다. 전단력은 접선 평면 사영행렬 $`P_{\text{shear}}=I_{3}-\hat{n}_{\rm{cop}}\hat{n}_{\rm{cop}}^{\top}`$ 로 근사합니다. 전체 관계는 아래 한 식으로 압축됩니다.

$$f_{i}=M_{i}f_{\rm{cop}},\quad M_{i}=w_{i}(\hat{b}_{i}\hat{n}_{\rm{cop}}^{\top}+P_{\text{shear}})\in\mathbb{R}^{3\times 3}$$

> "This low-parameter model captures the dominant distance-dependent spreading effect of the stress field while remaining differentiable and easy to align across simulation and hardware." (§3.2)
> (한글 해설 — 거리 의존 확산 효과를 소수 파라미터로 담으면서 미분 가능성을 유지하는 것이 핵심이며, 이 미분 가능성 덕분에 §3.3 의 gradient 기반 캘리브레이션이 성립합니다.)

**Inverse mapping (taxel → CoP).** 관측된 active taxel 힘 집합에서 미지의 $`f_{\rm{cop}}`$ 을 구하려면 taxel 별 식을 전역 선형계 $`Af_{\rm{cop}}=b`$ 로 모은 뒤 정규화 최소제곱의 닫힌 해로 풉니다.

$$f_{\rm{cop}}=(A^{\top}A+\lambda^{2}I)^{-1}A^{\top}b,\quad A=[M_{1}^{\top},\dots,M_{N}^{\top}]^{\top},b=[f_{1}^{\top},\dots,f_{N}^{\top}]^{\top}$$

접촉 위치 $`p_{\rm{cop}}`$ 은 측정된 힘 크기 $`\|f_{i}\|`$ 로 가중한 taxel 위치의 가중 평균으로 추정하되, idle 노이즈를 없애기 위해 active 집합 $`\mathcal{A}=\{i:\|f_{i}\|>\epsilon\}`$ 만 포함합니다.

**미분 가능 동역학 캘리브레이션.** taxel 원점 $`{}^{\mathcal{S}}p_{i}`$ 은 센서 스펙에서 얻지만, 회전 $`R_{i}`$ 는 미지이며 손끝 곡면 때문에 수동 캘리브레이션이 어렵습니다. 회전은 $`\mathbb{R}^{9}\mathord{+}\rm{SVD}`$ 파라미터화로 학습합니다.

$$R=\text{SVD}^{+}(P)=U\text{diag}(1,1,\text{det}(UV^{\top}))V^{\top},\quad P=U\Sigma V^{\top}$$

정적 평형에서 외력과 관절 토크는 다음 wrench-space 관계를 만족합니다 (중력 보상 $`g(q)`$ 는 무시 가정).

$$\tau=-J^{\top}f+g(q)\approx-J^{\top}f$$

추정된 CoP 힘으로 기대 관절 토크 $`\hat{\tau}=-{}^{\mathcal{B}}\hat{J}_{\mathrm{cop}}^{\top}{}^{\mathcal{B}}\hat{f}_{\mathrm{cop}}`$ 를 계산하고, 기록된 관절 토크 $`\tau`$ 와의 MSE 손실을 역전파해 회전 파라미터 $`\hat{P}`$ 를 개선합니다.

![Figure 2 — differentiable dynamics calibration](https://arxiv.org/html/2605.28812/x3.png)

> "Figure 2: Our proposed differentiable dynamics-based sensor calibration method, consisting of 1) data collection and 2) gradient-based optimization. Red arrows indicate gradient flow during back-propagation." (§3.3)
(한글 해설 — 강성 PD 제어로 손끝을 고정한 채 무작위 접촉을 가해 taxel 힘·관절 토크·관절 각도를 수집하고(1단계), taxel→CoP→토크 경로를 역전파해 taxel 회전을 학습합니다(2단계). 핵심은 힘 센서 ground-truth 없이 캘리브레이션한다는 데 있습니다.)

### 학습 셋업

XELA uSkin 센서로 손끝·지골·손바닥을 덮은 16-DOF Allegro hand 를 사용합니다. 접촉은 IsaacLab 의 `ContactSensor` API 로 추적합니다. 다만 손끝 형상에 대한 전단 추정이 불안정해 **시뮬레이션·하드웨어 양쪽에서 CoP 의 법선 성분만** 사용합니다(전단 정보를 의도적으로 희생해 Sim2Real 강건성 확보).

> "In contrast, our aligned CoP representation enables direct sim-to-real transfer." (§4)
> (한글 해설 — 기존 연구는 시뮬레이션과 하드웨어의 촉각 관측이 직접 정렬되지 않아 교사-학생 distillation 을 씁니다. 반면 정렬된 CoP 표현은 distillation 없이 곧바로 전이합니다.)

비대칭 actor-critic PPO 로 학습하며 actor 는 고유수용감각 + 접촉 표현을, critic 은 추가로 특권 물체 상태를 받습니다. 두 네트워크는 동일한 recurrent 구조를 공유합니다. 과거 관측을 stacking 하는 대신 recurrent 정책으로 시간 맥락을 주니 sample efficiency 가 더 좋았습니다. 여기에 도메인 랜덤화(마찰 정적/동적 분리, 질량, 관측 노이즈·지연), Bayesian 최적화 기반 actuator 동역학 system identification, 시각 기반으로 측정한 센서 지연 주입을 함께 적용합니다.

---

## 📊 실험 설정과 결과

두 과제 모두 시각 없이 고유수용감각(현재·명령 관절각)과 접촉 관측만 받는 blind 정책입니다. baseline 은 고유수용감각만(`base`), 센싱 어레이별 binary 접촉(`bin`), CoP 힘 크기(`mag`), 힘 벡터만(`vec`), 접촉 위치만(`pos`), raw taxel(`taxel`), 그리고 전문가 인간(`human`) 입니다.

**Peg-in-hole 삽입 (Table 1, 형상 6종 × 10 trial, 성공률 sr ↑ / 완료시간 time ↓).**

| 표현 | Overall sr ↑ | Overall time (s) ↓ | OOD Init. sr ↑ | Masked sr ↑ |
|------|------|------|------|------|
| `base` | 0.43 | 4.65 ±2.80 | 0.17 | - |
| `bin` | 0.53 | 10.15 ±8.57 | 0.20 | 0.52 |
| `mag` | 0.55 | 9.47 ±9.73 | 0.27 | 0.48 |
| `vec` | 0.67 | 7.19 ±7.60 | 0.42 | 0.57 |
| `pos` | 0.50 | 10.19 ±10.12 | 0.28 | 0.48 |
| `taxel` | 0.48 | 10.94 ±9.81 | 0.27 | 0.30 |
| **`cop` (ours)** | **0.78** | **10.34 ±7.62** | **0.63** | 0.62 |
| `human` | 1.0 | 2.03 ±1.32 | - | - |

> "As summarized in Table 1, cop achieves the highest overall success rate and outperforms all baselines on most insertion shapes." (§4.1, Table 1)
> (한글 해설 — `cop` 의 overall 성공률 0.78 은 모든 로봇 baseline 보다 높습니다. 단, 완료 시간은 단순 표현보다 깁니다. 고충실도 표현이 더 적응적이고 끈질긴 정책을 만들되 더 느린 경향을 보입니다.)

OOD 초기화에서 `cop` 의 성공률 하락이 가장 작습니다(0.78 → 0.63). 끈질긴 인핸드 물체 이동·재정렬로 정렬을 회복하는 emergent 능력도 함께 나타납니다. raw taxel 마스킹 40% 에서는 고충실도 표현이 단순 표현보다 큰 성능 저하를 겪습니다(개별 taxel 정밀값에 더 민감).

**공 균형 잡기 (Table 2, 공 4종 × 10 trial, time-to-fall(s) ↑).**

| 표현 | Tennis | Baseball | Moon | Hockey | Overall ↑ |
|------|------|------|------|------|------|
| `base` | 1.38 | 1.42 | 1.50 | 1.24 | 1.38 ±0.21 |
| `bin` | 2.20 | 2.22 | 1.78 | 1.75 | 1.99 ±1.03 |
| `mag` | 2.83 | 2.17 | 2.35 | 2.25 | 2.40 ±0.79 |
| `vec` | 5.59 | 3.27 | 4.59 | 2.80 | 4.52 ±2.93 |
| `pos` | 1.63 | 1.59 | 1.70 | 1.26 | 1.55 ±0.27 |
| `taxel` | 1.38 | 1.73 | 1.61 | 1.22 | 1.49 ±0.36 |
| **`cop` (ours)** | **5.07** | **4.77** | **4.50** | **3.06** | **4.60 ±2.19** |
| `human` | 11.29 | 9.41 | 5.96 | 10.82 | 9.37 ±5.32 |

> "As shown in Table 2, precise force information is crucial for this task, since only cop, vec, and taxel policies, which are conditioned on numerical force values, successfully learned the task in simulation." (§4.2, Table 2)
> (한글 해설 — 명시적 힘 정보가 없는 `base`·`bin`·`pos` 는 시뮬레이션에서 과제 자체를 학습하지 못합니다. `cop` 와 `vec` 의 실세계 성능이 비슷한 것을 보면 이 과제에서는 힘만으로도 충분할 수 있습니다.)

**잠재 표현 분석.** recurrent 층의 256-dim 잠재를 linear probing 해 공 상태를 예측합니다. 위치는 잘 잡지만(x/y pos $`r^{2}`$ 0.76 / 0.62, RMSE 0.013 / 0.019 m) 속도는 약합니다(x/y vel $`r^{2}`$ 0.23 / 0.15). 3종 질량(50g·150g·250g) 궤적의 잠재를 PCA 하면 시간이 흐르며 질량별 군집이 자연히 형성됩니다(Silhouette Coefficient 증가). 명시적 감독 없이도 CoP 조건부 정책이 물체 질량 같은 물리량 중심으로 상태를 조직함을 시사하는 결과입니다.

![Figure 7 — emergent latent mass clusters](https://arxiv.org/html/2605.28812/x9.png)

> "Figure 7: Visualization of the emergence of latent embedding clusters across trajectories in temporal evolution, where different clusters correlate with different physical properties. Here we show object mass as an example." (§4.2)
(한글 해설 — 궤적이 진행될수록 잠재 임베딩이 질량 값별 군집으로 재조직되는 과정을 시각화합니다. 물리량의 emergent 인코딩이라는 핵심 주장을 뒷받침합니다.)

---

## ⚖️ 한계

- **(A) 충실도 vs 전이성** — CoP 는 raw taxel 을 더 전이 가능한 힘·위치 정보로 의도적으로 추상화합니다. 불완전한 촉각 시뮬레이션 아래에서 강건성은 좋아지지만 센서 특화 디테일 일부를 버립니다. 정확한 센서 모델과 결합된 raw 촉각 표현이 더 복잡한 조작에서는 더 높은 성능을 줄 수도 있습니다.
- **(B) Sim-Real 접촉 불일치** — 시뮬레이션 전단력 추정이 불안정해 CoP 힘 벡터를 법선 방향으로 제한했습니다. 사용한 시뮬레이터는 과제 물체 접촉만 보고하는 반면 실제 촉각 센서는 자가 충돌·환경 접촉 등 모든 접촉에 반응합니다. 그래서 더 다양한 환경에서는 OOD 촉각 관측이 생길 수 있습니다.
- **(C) 범위와 향후 방향** — 고정 베이스 다지 손 + XELA uSkin 으로 한정해 촉각 표현의 효과를 분리했습니다. arm-hand 통합 시스템, 손 전체 촉각 커버리지, 다른 촉각 센서 종류로 넓히는 일이 향후 과제로 남습니다. Sim2Real 강화학습을 넘어 모방 학습이나 sample-efficient 실세계 강화학습과 통합하는 것도 희망 방향입니다.
- (추가 관찰) 모든 과제에서 `human` 이 최고 로봇 정책을 크게 앞섭니다. 저자는 인간이 촉각과 고수준 기하 추론·탐색 전략을 결합하는 반면 로봇 정책은 반응적 접촉 피드백에 의존하기 때문으로 추정합니다.

---

## ♻️ 재현성

- **하드웨어** — 16-DOF Allegro hand + XELA uSkin 촉각 센서(손끝·지골·손바닥). peg/hole 자산 6종 형상은 부록 F 에 치수가 명시되며, hole 은 $`x`$ / $`y`$ 축으로 10% 크게 해 10% 삽입 공차를 둡니다.
- **시뮬레이터·알고리즘** — IsaacLab + 비대칭 actor-critic PPO. 부록 E 에 관측·행동·보상·리셋·도메인 랜덤화·PPO 하이퍼파라미터가 표로 정리됩니다(학습률 5e-4 적응형, target KL 0.016, γ=0.99, λ=0.95, clip 0.2, entropy 0.005; 5 seed).
- **코드/데이터 공개** — 본문에 project site 와 supplementary video 링크가 언급되나, 코드·학습 데이터·모델 가중치의 공개 여부와 라이선스는 확보한 본문(HTML)에서 명시적으로 확인되지 않습니다. 라이선스는 arXiv 페이지 기준 CC BY 4.0(논문 문서).
- **캘리브레이션 재현 변수** — 응력 spread $`\sigma`$, 정규화 $`\lambda`$, active 임계 $`\epsilon`$, taxel 수 $`N`$ 의 구체 수치는 확보 본문에 명시되지 않았습니다(센서 스펙 의존).

---

## 🎯 관련 Pillar / Decision (P# / D#)

본 논문은 PROBE 의 **P3(Hand-level System0 Module, RL-scoped)** 와 **P2(Structured Input-Modality Binding)** 에 직접 맞닿습니다.

- **P3 / D15·D17·D18** — 시각을 배제한("blind") 다지 손 접촉 집약적 과제를 PPO 로 Sim2Real 전이하는 구성은 System0 의 작동 영역과 정확히 겹칩니다. 관측은 촉각 + 고유수용감각만(시각 제외)으로 D15 의 v1 입력 모달리티 설계와 일치합니다. 접촉 인지 보상 항(`good contact reward` $`\sum_{i}\mathbb{1}(\|f_{i}\|\geq 1.0)`$, action-diff penalty 등)과 PPO·도메인 랜덤화는 각각 D17·D18 의 직접 참고점입니다. 특히 마찰 정적/동적 분리 DR 은 D18 의 핀 논문(Static Friction Sim2Real, arXiv:2503.01255)이 정한 방향과 같습니다.
- **P2 / D8·D11** — CoP(3D 힘 벡터 + 3D 접촉 위치)는 D11 의 "촉각 특징 옵션(tactile image / resultant force vector / pressure distribution / contact map)" 중 **resultant force vector + contact position** 조합의 구체적 물리 기반 사례입니다. 손끝별 CoP 는 D8 의 per-finger 토큰 구성과도 맞물립니다.
- **Identity 긴장/지지** — 논문은 강화학습을 과제 전체 학습기로 씁니다(Identity 의 Antagonist B "RL-as-core"). PROBE 는 일반화 과제에서 RL-as-core 를 거부하지만, 본 논문의 과제(peg 삽입·균형)는 정확히 reward-engineerable 한 접촉 안정화 영역, 즉 System0 의 정당화 범위입니다. 그래서 "전체 정책을 RL 로 학습한다"는 프레이밍은 지지하지 않되, "촉각 표현 + 접촉 보상 + Sim2Real"이라는 **방법론 자체는 System0(P3)에 흡수 가능**합니다.
- **건드리지 않는 축** — Body/Hand 분할이나 VLA·flow-matching 액션 전문가가 없어 **P1 은 무관**하며, VLM 백본이 없어 **P4 도 무관**합니다. P5 측면에서는 peg-in-hole·blind 과제와 마스킹·OOD 강건성 평가 프로토콜이 참고 가치가 있으나 핀과 직접 연결되진 않습니다.
- **§9 저자/§10 경쟁자** — 저자 Toru Lin·Jitendra Malik 은 §9.1 에 이미 추적 대상(Berkeley)으로 등재되어 있어 신규 추가 대상은 없습니다.

---

## ✨ 핀 논문 대비 델타

- **HORA(arXiv:2210.04887) / AnyRotate(arXiv:2405.07391) 대비 (P3 핀)** — 두 핀은 특권→촉각 **교사-학생 distillation** 으로 Sim2Real 을 다룹니다. 본 논문의 진정한 새로움은 **distillation 없이** 시뮬레이션·하드웨어 촉각을 동일 CoP 좌표계로 정렬해 곧바로 전이한다는 데 있습니다. 정책은 처음부터 전이 가능한 관측만 받으므로 별도 student 단계가 필요 없습니다.
- **Static Friction Sim2Real(arXiv:2503.01255) 대비 (D18 핀)** — 정적/동적 마찰 분리 DR 은 동일 기법을 공유합니다(델타 아님). 차별점은 DR 이 아니라 **관측 표현 자체를 물리 기반으로 정렬**해 격차를 줄인다는 접근입니다.
- **SaTA(arXiv:2510.14647) / DexViTac(arXiv:2603.17851) / AdapTac(arXiv:2505.13982) / Sparsh(arXiv:2410.24090) 대비 (P2 핀)** — 이들은 모두 **학습된 촉각 인코더**(FiLM 융합, kinematic-grounded 인코딩, force-guided attention, 촉각 foundation model)로 촉각을 잠재 특징화합니다. CoP 의 델타는 표현 자체를 **닫힌 형식의 미분 가능 매핑**으로 손수 설계해 해석 가능하고 시뮬레이터 정렬이 쉽다는 데 있습니다. 학습되는 부분은 taxel 회전 캘리브레이션뿐이고 표현 인코더는 학습하지 않습니다. DexViTac 의 kinematic-grounded 발상과 가장 가깝지만, CoP 는 인코더를 두지 않는다는 점에서 갈립니다.
- **종합** — 핀들과 비교한 본 논문의 단일 최대 델타는 "**학습된 인코더·distillation 없이, 물리 기반 정렬 표현만으로 zero-shot 촉각 Sim2Real**"이며, 이는 P3 의 D18 RMA 교사-학생 v1 기본값에 대한 대안적 경로를 제시합니다.

---

## ⚙️ 의사결정 함의

- **D15(System0 입력 모달리티)** — 현재 v1 은 "촉각 특징 + 관절 위치·속도·토크 + 접촉 상태 이력"입니다. 본 논문은 촉각 채널을 **손끝별 CoP(3D 접촉력 벡터 + 3D 접촉 위치, 법선 성분만)** 로 구체화할 것을 제안합니다. 구현 수준: System0 관측에 `contact_force_vec`(R³) + `contact_pos`(R³) 를 손끝당 추가하고, raw 촉각 대신 이 정렬 표현을 1차 입력으로 둡니다.
- **D18(System0 Sim2Real)** — RMA 교사-학생을 v1 기본으로 두되, 본 논문이 보인 **"정렬 표현 기반 직접 전이"를 대안/보완**으로 등록할 가치가 있습니다. 시뮬레이터가 정렬된 접촉량을 제공하면(IsaacLab `ContactSensor`, PROBE 도 Isaac Sim/PhysX 사용 — §4.2) distillation 단계를 생략할 수 있다는 가설입니다. 함께 채택 가능한 구체 DR: 마찰 정적/동적 분리, 질량, 관측 노이즈, PD 게인 랜덤화 ×U(0.8,1.2)/×U(0.7,1.3), 접촉 관측 지연 [0.05,0.1]s.
- **D17(System0 RL 정책 스펙)** — 접촉 인지 보상 항의 구체 사례를 제공합니다: `good contact reward` 가중치 0.25, action-diff penalty, plate contact reward 등(부록 E Table 5). PPO 설정(lr 5e-4 적응형·target KL 0.016·γ 0.99·λ 0.95·clip 0.2·entropy 0.005)과 행동 평활화(EMA α=0.5, action scale 0.03/0.05)는 System0 정책 초기 설정의 직접 참고값입니다.
- **정책 구조 함의** — 과거 관측 stacking MLP 대신 **recurrent 정책**이 sample efficiency·성능에서 우세했다는 결과는, System0 가 접촉 이력을 다룰 때 명시적 history 적층 대신 recurrent 잠재를 쓰는 선택지를 시사합니다(D16/D17 구조 선택).

---

## ⚠️ 먼저 검증할 실패 모드

- **센서 형식 불일치 (가장 싼 sanity check 먼저)** — Taxel-CoP 매핑은 3축 힘을 주는 **이산 taxel 격자**(XELA uSkin)를 가정합니다. PROBE 의 Sharpa Hand 는 비전 기반 dense Deform Map(~320×240/손끝)이라 매핑이 그대로 적용되지 않습니다. 가장 싼 검증: Deform Map 출력에서 합력 벡터 + 접촉 중심(=CoP 등가량)을 적분/추정할 수 있는지 오프라인으로 먼저 확인합니다. 불가하면 표현 차용 전체가 막힙니다.
- **전단 정보 손실 vs System0 의 존재 이유** — 논문은 시뮬레이션 전단 불안정 때문에 **법선 성분만** 씁니다. 그런데 System0 의 핵심 임무는 slip 억제이고 slip 은 본질적으로 **전단 현상**입니다. 법선만 남긴 CoP 가 slip 신호를 충분히 담는지 시뮬레이션에서 먼저 검증해야 합니다. 담지 못하면 D15 의 촉각 채널로 부적합합니다. (PROBE 도 같은 PhysX 스택이라 전단 불안정 한계를 그대로 물려받습니다.)
- **직접 전이 가정의 깨짐** — 직접 전이는 시뮬레이터가 손 형상에 대해 신뢰할 만한 정렬 접촉량을 줄 때만 성립합니다. 논문조차 자신들의 손끝 형상에서 전단이 불안정했습니다. PROBE 손 형상에서 PhysX 접촉 추정이 노이즈가 크면 distillation 생략(D18 대안)이 무너지므로, RMA 기본값을 성급히 폐기하면 안 됩니다.
- **범위 오해 금지** — 논문 정책은 과제 전체를 RL 로 학습합니다(Antagonist B). PROBE 가 차용할 것은 **표현·보상·DR·전이 기법**이지 "RL 이 전체 과제를 학습한다"는 프레이밍이 아닙니다. System0 는 게이트되는 하위 루프이므로, 표현은 가져오되 학습 범위는 분리해 검증해야 합니다.

---

## 💡 컨텍스트 제안

- **P3 / D18 trigger 후보** — "정렬된 물리 기반 촉각 표현으로 distillation 없는 직접 Sim2Real" 을 D18 의 *deferred 대안*으로 기록할 것을 제안합니다(현재 v1 = RMA 교사-학생). 트리거 예시: "Sharpa Deform Map 에서 CoP 등가량을 안정적으로 추출 가능함이 확인되고, 시뮬레이터 접촉량 정렬이 신뢰 가능할 때." `context/MASTER.md` 는 수정하지 않습니다 — 사람 판단에 맡깁니다.
- **P2 / D11 촉각 특징 후보 보강** — D11 의 "resultant force vector" 옵션에 본 논문(arXiv:2605.28812)을 물리 기반 구체 사례로 연결할 것을 제안합니다. 단, P2 핀 슬롯은 8개로 가득 차 있어 분기별 rebalance 시 "replace, don't append" 규칙을 따라야 하므로, 즉시 핀 교체보다 **competitor/watch 수준 추적**을 권합니다.
- **핀 교체는 보류 권고** — 본 논문은 RL-as-core·비전 없는 단일 손 과제로 Identity 핵심(VLA-level 분할)과는 거리가 있어, 핀 승격보다 P3·P2 방법론 참고 자료로 두는 편이 적절합니다.
- 그 외 신규 컨텍스트 변경 제안: 없음.

> 💡 base 매핑은 `/implement-design analysis/2605.28812/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
