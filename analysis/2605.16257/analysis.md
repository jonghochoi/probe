# Paper Analysis — DexJoCo: A Benchmark and Toolkit for Task-Oriented Dexterous Manipulation on MuJoCo

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | DexJoCo: A Benchmark and Toolkit for Task-Oriented Dexterous Manipulation on MuJoCo |
| 저자 | Hanwen Wang, Weizhi Zhao, Xiangyu Wang, Siyuan Huang (공동 1저자) · He Lin, Boyuan Zheng, Rongtao Xu, Gang Wang, Yao Mu, He Wang, Lue Fan (Project lead), Hongsheng Li, Zhaoxiang Zhang, Tieniu Tan (교신) — NLPR & MAIS CASIA · SJTU · MBZUAI · BIBMS · PKU & Galbot · CUHK |
| 링크 | [arXiv:2605.16257](https://arxiv.org/abs/2605.16257) · [Website](https://dexjoco.github.io) |
| 발행일 / 버전 | 2026-05-15 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-25 |
| 관련 Pillar | P0, P4, P1, P2 |
| 태그 | dexterity, dataset, vla-arch |
| 카탈로그 | benchmark/dexterous/DexJoCo |

<!-- 본문은 arXiv HTML(전문)로 확보. 모든 수치는 본문/표에서 받은 그대로 인용. -->

---

## 🧭 한 줄 요약 (TL;DR)

병렬 그리퍼로는 불가능한 dexterous hand 고유 능력(tool-use·bimanual·long-horizon·reasoning)을 측정하도록 설계된 **MuJoCo 기반 task-oriented dexterous 벤치마크 + 저비용 toolkit + 1.1K 시연 데이터셋**입니다. 11개 기능 기반 태스크에서 ACT·Diffusion Policy·π0.5·GR00T N1.5 같은 현대 정책을 평가해, 사전학습 우위가 추가 action 차원을 scratch 학습할 때 희석되고, fine-grained 버튼 조작·삽입·메모리·언어 일반화에서 광범위하게 실패한다는 사실을 정량 폭로합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — Dexterous hand manipulation 알고리즘을 실험실 간 환경·로봇 구성 차이를 넘어 체계적으로 비교할 **표준 벤치마크**가 부재합니다. Manipulator–gripper 평가는 성숙했지만 dexterous hand 쪽은 표준이 없습니다.
- **기존 접근의 한계 (1) — 비현실적 셋업** — 많은 기존 연구가 workspace를 키우려 manipulator를 빼고 hand-only로 두어, 실제 시나리오에서 재현하기 어려운 궤적을 만듭니다.
- **기존 접근의 한계 (2) — 빈약한 태스크** — 현재 벤치마크는 in-hand manipulation 또는 pick-and-place에 머뭅니다. in-hand는 기능적 다양성이 낮고, pick-and-place는 그리퍼 대비 손의 차별적 능력을 드러내지 못합니다.
- **기존 접근의 한계 (3) — 수집 도구 부재** — 복잡한 손 동작은 motion planning으로 만들기 어려워 대다수가 RL·자동 생성에 의존하는데, 그 결과 궤적이 자연스러운 인간 조작 패턴과 어긋납니다.
- **기존 접근의 한계 (4) — 표준 포맷 부재** — 표준화된 언어 지시·통일된 데이터 포맷이 없어 현대 VLA 모델의 체계적 학습·평가가 어렵습니다.
- **본 논문의 가설 / 왜 지금 중요한가** — 기능적으로 의미 있는 태스크 + 저비용 mocap-glove teleoperation + 통일 포맷을 묶은 벤치마크를 제공하면, dexterous policy의 공통 한계를 드러내 후속 연구를 안내할 수 있다는 것입니다. Dexterous learning이 부상하는 지금 표준 측정자가 필요합니다.

---

## 🧩 핵심 기여

- **DexJoCo benchmark** — 손 고유 능력(fine-grained manipulation, tool-use, bimanual coordination, long-horizon execution, reasoning)을 평가하는 11개 기능 기반 태스크. RoboSuite 기반 씬에 RoboCasa·SAPIEN PartNet-Mobility·Hunyuan3D 에셋을 올려 구성.
- **DexJoCo toolkit** — Rokoko Smartgloves + HTC Vive Tracker 기반 약 \$2,300 USD 저비용 teleoperation 시스템 + GeoRT retargeting 모듈. embodiment gap을 줄이는 효율적 시연 수집.
- **DexJoCo datasets** — 시뮬레이션에서 수집한 **1.1K human demonstration 궤적**과 현대 정책 5종 평가. dexterous hand 궤적 데이터가 희소한 선행 연구 대비 기여.
- **경험적 통찰** — 사전학습·규모·아키텍처 trade-off, fine-grained/삽입/메모리 실패, multi-task degradation, action-head 보존 효과, 언어 일반화 실패 등을 정량 분석해 dexterous robot learning의 핵심 도전을 제시.

![Figure 1 — DexJoCo 개요](https://arxiv.org/html/2605.16257/x1.png)

> "Figure 1: Overview of DexJoCo. DexJoCo is a dexterous manipulation benchmark with a toolkit for data collection and policy evaluation, covering tool-use, bimanual coordination, long-horizon execution, and reasoning. It includes 11 tasks, 1.1K human demonstration trajectories, and supports trajectory replay under domain randomization for robustness evaluation." (§1)
> (한글 해설 — 벤치마크·toolkit·데이터셋의 세 축과 4대 능력 범주, 그리고 궤적 replay 기반 robustness 평가 구조를 한 장에 요약한 표지 그림입니다.)

---

## 🔑 기술 키워드

- **Task-oriented dexterous manipulation** — 단순 물체 재배치가 아니라 망치질·물주기처럼 도구의 기능을 살리는 조작. 손의 차별적 능력을 강제하는 태스크 설계 철학.
- **Dexterity dependency** — 성공이 손가락 정밀 협응·관절형 물체 상호작용에 본질적으로 의존하도록 태스크를 짜, 병렬 그리퍼로는 풀 수 없게 만드는 설계 원칙.
- **Teleoperation + retargeting** — 인간 손동작을 로봇 손 관절 명령으로 변환하는 원격조작. 사람 손과 로봇 손의 구조 차이로 직접 선형 매핑이 불가능해 학습된 retargeting이 필요.
- **GeoRT (Geometric Retargeting)** — paired 인간-로봇 라벨 없이 동작하는 경량 self-supervised retargeting. 손끝 keypoint를 Allegro 관절 위치로 매핑(ref [45]).
- **Domain randomization** — 물체 배치·테이블 높이(물리) + 카메라 포즈·조명·테이블 텍스처(시각)를 무작위화해 정책의 robustness를 측정하는 분포 확장. 동일 궤적 replay로 시각 augmentation을 저비용 적용.
- **Partial pretrain-AH (action head)** — bimanual에 32차원 기본 action head가 부족할 때, 사전학습 가중치는 유지하되 추가 차원만 random init하는 부분 보존 전략.
- **Asynchronous inference** — 현재 chunk 실행 중 다음 action chunk를 생성해 idle을 없애는 추론 방식(SmolVLA 영감). 추론 빈도가 반응성에 직결.
- **Action chunking** — $`h`$ 프레임 관측과 선택적 언어 지시를 조건으로 미래 $`k`$-step action chunk의 조건부 확률을 모델링하는 정책 출력 형식.
- **FiLM (Feature-wise Linear Modulation)** — 관측을 self/cross-attention 대신 feature 스케일·시프트로 주입하는 conditioning(ref [30]). DP-C의 fine-grained 정밀 조작 우위의 가설적 원인.
- **Functional success constraints** — 시퀀스·물체 포즈·관절 상태·접촉으로 정의되는 성공 조건 집합. 모든 제약이 동시 충족돼야 성공으로 판정.

---

## 🔬 방법론

본 논문은 학습 알고리즘이 아니라 **벤치마크 + 데이터 수집 toolkit + 평가 프로토콜**을 제안합니다. 아래는 그 구성 방법을 분해한 것입니다.

### 직관

DexJoCo의 출발점은 "기존 dexterous 벤치마크가 손의 차별적 능력을 측정하지 못한다"는 진단입니다. in-hand rotation은 기능이 단조롭고, pick-and-place는 그리퍼로도 풀려 손을 쓸 이유를 보여주지 못합니다. 그래서 저자들은 **성공이 손가락 정밀 협응에 본질적으로 의존하는 기능적 태스크**(망치질, 집게 쥐기, 안경 접기, 마우스 클릭 등)를 설계해, 손이 아니면 못 푸는 문제로 평가 축을 옮깁니다.

두 번째 통찰은 "복잡한 손 궤적은 자동 생성으로 자연스럽게 못 만든다"는 것입니다. RL·motion planning 궤적은 인간 조작 패턴과 어긋나므로, 저자들은 **저비용 mocap glove teleoperation**으로 사람이 직접 시연을 수집합니다. 사람 손과 로봇 손의 구조 차이는 학습된 retargeting(GeoRT)으로 메워, 손끝 움직임을 Allegro 관절로 옮깁니다.

세 번째로, 평가를 현대 VLA가 바로 학습·실행할 수 있도록 **통일 포맷(LeRobot, DP Zarr)과 표준 언어 지시**를 제공하고, 동일 궤적을 다른 렌더링으로 replay하는 **시각 domain randomization**으로 robustness 측정을 저비용으로 확장합니다. 전체는 MuJoCo 물리 위에서 구조화된 성공 조건으로 채점됩니다.

### 시스템 구성 — 로봇·관측·액션 (§3.1)

로봇은 Rethink Robotics mount(base) + Franka Panda(manipulator) + Allegro Hand(dexterous hand)의 3요소이며, 모두 성숙·정밀 모델링된 자산입니다. 관측은 3인칭·손목 RGB 및 RGB-D, 상호작용 객체 포즈, 로봇 motion state, EE 포즈, 손 관절각을 포함합니다. 액션 공간은 다음과 같이 정의됩니다.

> "manipulator actions are represented by the target absolute end-effector pose in the world coordinate frame, while hand actions are specified as target absolute joint angles." (§3.1)
> (한글 해설 — 팔은 world 좌표계의 **절대 EE 포즈**, 손은 **절대 관절각**을 목표로 둡니다. 우리 P1(이종 Body/Hand action expert)의 출력 공간 결정 D3과 직접 맞닿는 설계로, 손은 joint-space 절대 명령을 씁니다.)

### 데이터 수집 시스템 — teleoperation + GeoRT (§3.2)

하드웨어는 Rokoko Smartgloves(손 motion capture, 카메라 occlusion 회피) + HTC Vive Tracker 2개·Base Station 2개(손목 추적·Franka EE 제어)로 구성되며, 3D 프린팅 커넥터로 일체화합니다. 총 비용은 약 \$2,300 USD로 저비용입니다. 사람·로봇 손의 구조 차이로 직접 선형 매핑이 불가능하므로 GeoRT를 채택합니다.

> "We adopt GeoRT [45], a lightweight self-supervised retargeting method without requiring paired human-robot annotations." (§3.2)
> (한글 해설 — paired 라벨 없이 손끝 keypoint $`x_{H}`$ 를 로봇 관절 $`q_{R}=f(x_{H})`$ 로 매핑하는 self-supervised retargeting을 그대로 가져다 씁니다 — 본 논문의 자체 기여가 아니라 외부 모듈 채택입니다.)

retargeting 모델 $`f`$ 는 다음 복합 손실을 최소화하여 학습됩니다.

$$\mathcal{L}=\mathcal{L}_{\text{dir}}+\lambda_{1}\mathcal{L}_{\text{cover}}+\lambda_{2}\mathcal{L}_{\text{flat}}+\lambda_{3}\mathcal{L}_{\text{pinch}}+\lambda_{4}\mathcal{L}_{\text{col}}$$

각 항의 의미는 — $`\mathcal{L}_{\text{dir}}`$ 손끝 운동 방향 보존, $`\mathcal{L}_{\text{cover}}`$ workspace 커버리지 확대, $`\mathcal{L}_{\text{flat}}`$ 균일 sensitivity 유지, $`\mathcal{L}_{\text{pinch}}`$ pinch 거동 보존, $`\mathcal{L}_{\text{col}}`$ self-collision 회피입니다(가중치 $`\lambda_1`$ ~ $`\lambda_4`$ 값은 원문 미명시). 손목은 tracker를 고정해 사람 손목 움직임이 Franka EE에 정렬되도록 하고, 초기 포즈를 기준으로 이후 동작을 **상대 포즈 변화(delta)** 로 표현해 로봇이 재현합니다.

![Figure 3 — 데이터 수집 시스템](https://arxiv.org/html/2605.16257/x3.png)

> "Figure 3: Human demonstration data collection system. The left figure shows the overall teleoperation system. A Rokoko glove is used to capture hand poses, while an HTC Vive tracker is employed to track the wrist pose. The right figure shows that a retargeting mapping is trained to convert human fingertip poses into joint configurations of the Allegro hand." (§3.2)
> (한글 해설 — glove(손)+tracker(손목)의 이원 캡처와 손끝→Allegro 관절 retargeting 매핑을 시각화합니다. 손목은 delta, 손은 학습된 매핑이라는 toolkit 핵심 구조입니다.)

### 태스크 설계 — formulation·원칙·자산 (§3.3)

각 태스크는 상호작용 객체와 목표의 쌍 $`\mathcal{T}=(\mathcal{O},\mathcal{G})`$ 로 정의됩니다. 여기서 $`\mathcal{O}=\{o_{1},o_{2},\dots,o_{m}\}`$ 는 씬의 상호작용 객체 집합이고, 목표는 기능적 성공 제약 집합 $`\mathcal{G}=\{g_{\text{seq}},g_{\text{pose}},g_{\text{joint}},g_{\text{contact}}\}`$ 로 — $`g_{\text{seq}}`$ 시간/순서 제약, $`g_{\text{pose}}`$ 목표 물체 포즈, $`g_{\text{joint}}`$ 관절 상태 요구, $`g_{\text{contact}}`$ 충돌 정의입니다.

> "A task is considered successful only when all task-dependent goal constraints are satisfied simultaneously." (§3.3)
> (한글 해설 — 부분 성공을 인정하지 않고 모든 제약의 **동시 충족**만 성공으로 봅니다. long-horizon·삽입처럼 한 단계만 빠져도 0점이 되는 엄격한 채점이 낮은 절대 성공률의 한 원인입니다.)

설계 원칙 4가지는 (1) Functional Interaction(일상 활동 의미 + 명시적 시각 피드백 — 물뿌리개 임계 관절각에서 물 표시, iPad 버튼 접촉 시 하이라이트, 마우스 클릭 시 디스플레이 활성화), (2) Dexterity Dependency(그리퍼로 불가능한 손가락 정밀 협응·관절형 물체 상호작용), (3) Long-Horizon Compositionality(하위목표 간 시간 의존 다단계), (4) Bimanual Coordination(두 손의 비대칭 기능 분담)입니다. 태스크는 tool-use·reasoning·bimanual·long-horizon 범주로 조직되며, 개별 태스크 구축 비용이 낮아 확장이 쉽습니다. 자산은 RoboSuite 씬 + MuJoCo Menagerie 로봇 + RoboCasa·SAPIEN PartNet-Mobility 큐레이션, 주석 없는 자산은 Hunyuan3D로 생성 후 물리 파라미터 수동 부여.

11개 태스크는 — 단일 팔 6종(Hammer Nail, Click Mouse, Pick Bucket, Pinch Tongs, Fold Glasses, Water Plant) + bimanual 5종(Unlock iPad, Hanoi, Assembly, Microwave, Photograph)입니다.

![Figure 4 — 태스크 설계](https://arxiv.org/html/2605.16257/x4.png)

> "Figure 4: Task design in DexJoCo. The top panel illustrates the task environment design, showing the initial state of each task. The bottom panel presents the visual and interactive properties of the task assets." (§3.3)
> (한글 해설 — 11개 태스크의 초기 상태와 자산의 시각·상호작용 속성을 한눈에 보여, "손이 아니면 못 푸는" 기능적 태스크 구성 의도를 뒷받침합니다.)

### 도메인 randomization (§3.4)

물리 다양성을 위해 테이블 평면 위 물체 배치 + 테이블 높이($`\Delta h\sim U(0,0.05)`$ m)를 무작위화하고, 시각 다양성을 위해 3인칭 카메라 포즈(구면 dense sampling 후 occlusion 최소 50개 선택)·조명 방향/색·테이블 텍스처를 무작위화합니다. 핵심은 — **동일 궤적을 다른 렌더링으로 replay**해 추가 teleoperation 없이 시각 augmentation을 확장하는 점입니다. 태스크별 물체/dynamics(질량·관절 마찰·강성 배수) randomization 범위는 App. C 표 6에 상세 명시됩니다.

### 평가 프로토콜 — baseline·배포 (§3.5)

평가 대상은 4개 정책(실질 5개 변형)입니다 — ACT(C-VAE), Diffusion Policy(DP-T transformer / DP-C CNN), π0.5, GR00T N1.5. ACT·DP는 vision+proprioception으로 scratch 학습, π0.5·GR00T N1.5는 flow-matching + 언어 조건이며 GR00T N1.5는 LoRA fine-tune. 모든 baseline은 action chunking 형식을 공유합니다.

$$\mathcal{P}(a_{t:t+k-1})=\pi_{\theta}(a_{t:t+k-1}\mid s_{t-h+1:t},l)$$

즉 $`h`$ 프레임 관측 $`s`$ 와 선택적 언어 지시 $`l`$ 을 조건으로 미래 $`k`$-step action chunk의 조건부 확률을 모델링합니다. bimanual은 기본 32차원 action head가 부족해 부분 보존 전략을 씁니다.

> "Because their default 32-dimensional action heads are insufficient for bimanual tasks, we retain these pretrained weights but randomly initialize the extra dimensions (partial pretrain-AH)." (§3.5)
> (한글 해설 — 사전학습된 head는 유지하고 **추가 차원만 random init**하는 partial pretrain-AH 입니다. 이 선택 자체가 §4의 핵심 실험(보존 vs 전체 reinit) 대상이 되며, 우리 P4 D20(prior-preservation strategy)에 직접 대응합니다.)

배포는 비동기 추론입니다.

> "we use an asynchronous inference mechanism inspired by SmolVLA [35]: the next action chunk is generated while the current one executes, eliminating idle waiting." (§3.5)
> (한글 해설 — 현재 chunk 실행 중 다음 chunk를 생성해 idle을 없애고, 겹치는 chunk는 temporal ensemble로 부드럽게 합니다. 가벼운 정책일수록 추론이 빨라 더 최신 관측을 써 반응성이 좋아진다는 점을 강조합니다.)

---

## 📊 실험 설정과 결과

평가는 in-domain 학습 후 동일 태스크에서 측정하며, 각 태스크를 "rand-obj"(물체 배치 + 테이블 높이만)와 "rand-full"(+카메라/조명/텍스처) 두 regime으로 학습·평가합니다. 모든 수치는 11개 태스크·3 seed 기준 성공률(%) ±std입니다.

**모델별 평균 성공률 (Table 2)**

| 모델 | rand-obj Avg | rand-full Avg |
|---|---|---|
| DP-T (~100M, scratch) | 50.4 ±1.4 | 20.0 ±1.4 |
| DP-C (CNN, scratch) | 47.6 ±2.0 | 28.4 ±1.5 |
| ACT (scratch) | 35.5 ±2.0 | 22.7 ±1.3 |
| **π0.5 (사전학습)** | **52.5 ±1.4** | **34.1 ±2.9** |
| GR00T N1.5 (LoRA) | 40.2 ±0.3 | 30.5 ±1.1 |

> "$`\pi_{0.5}`$ achieves the highest overall success rates, benefiting from large-scale pre-training, yet the much smaller DP-T ($`{\sim}100`$M, trained from scratch) performs comparably: $`\pi_{0.5}`$ dominates single-arm tasks while DP-T is competitive on bimanual ones, likely because training the extra action dimensions from scratch diminishes $`\pi_{0.5}`$'s pre-training advantage." (§4, Table 2)
> (한글 해설 — π0.5가 최고지만(52.5) ~100M scratch DP-T(50.4)가 근접하며, **bimanual에서 추가 action 차원을 scratch 학습하면 사전학습 우위가 희석**된다는 진단입니다. 우리 P4 D19/D22(사전학습 lineage·구성)와 P1 D3(Hand 출력 차원) 모두에 닿는 결과입니다.)

**rand-full 일반화 붕괴** — 시각 randomization을 더하면 거의 모든 정책의 성공률이 급락합니다(예: DP-T 50.4→20.0, ACT 35.5→22.7). robustness가 제한적임을 보입니다.

**태스크별 명암 (Table 2, rand-obj)**

| 태스크 | DP-T | DP-C | ACT | π0.5 | GR00T N1.5 |
|---|---|---|---|---|---|
| Hammer Nail | 81.3 | 58.7 | 50.0 | 84.7 | 67.3 |
| Pinch Tongs | 22.7 | **57.3** | 31.3 | 24.0 | 12.7 |
| Unlock iPad /B | 8.0 | **52.0** | 9.3 | 12.0 | 12.7 |
| Hanoi /B | 24.7 | 12.7 | 6.0 | 15.3 | 0.7 |
| Assembly /B | 4.7 | 3.3 | 0.0 | 5.3 | 0.7 |

> "Surprisingly, DP-C substantially outperforms all other policies on Unlock iPad and Pinch Tongs." (§4)
> (한글 해설 — DP-C가 Unlock iPad(52.0)·Pinch Tongs(57.3)에서 압도합니다. 버튼 누르기·hinge 상호작용 같은 정밀 조작에서 강한데, 저자는 그 원인을 아키텍처 한 가지로 지목합니다.)

> "We hypothesize that this advantage stems from being the only policy to use FiLM [30] for observation injection, rather than self or cross attention, which may provide stronger fine-grained visual perception and benefit precise manipulation." (§4)
> (한글 해설 — DP-C만 관측 주입에 self/cross-attention 대신 **FiLM**을 써서 fine-grained 시각 인지가 강하다는 가설입니다. 우리 P2 D9/D10(관측 인코더·fusion 방식)에 "주입 방식이 정밀도를 가른다"는 외부 단서를 줍니다.)

**Assembly·Hanoi의 near-zero** — bimanual 삽입(Assembly)은 5개 모델 모두 한 자릿수, 일부는 0.0%로 사실상 풀지 못합니다. 벤치마크가 매우 도전적임을 보입니다.

![Figure 5 — 성능·실패 모드 분석](https://arxiv.org/html/2605.16257/x5.png)

> "Figure 5: Performance evaluation and failure mode analysis. DP denotes Diffusion Policy, with -T and -C representing Transformer and CNN-based architectures, respectively. (a) Comparison of average success rates across different baselines under the "rand-obj" (Table 2) condition. (b) and (c) provide a detailed breakdown of failure modes for $`\pi_{0.5}`$ and DP-C. These statistics are aggregated from 550 evaluation trials (50 runs across 11 tasks) to identify main bottlenecks in dexterous manipulation." (§4)
> (한글 해설 — baseline 평균 성공률 비교(a)와 π0.5·DP-C의 실패 모드 분해(b,c)를 550회 시도로 집계해 주요 병목을 식별합니다.)

**실패 모드 (§4)** — 버튼 기반 태스크(Unlock iPad, Click Mouse, Photograph)에서 정책은 태블릿/카메라를 집고 마우스를 패드에 올리지만 **의도한 버튼 클릭에 자주 실패**합니다(객체는 인지하나 상호작용 요소를 놓침). 삽입(Assembly, Hanoi)은 실패 확률이 높고, Pinch Tongs는 잡되 쥐고 놓기를 못 하며(temporal memory 부족 추정), Microwave는 핫도그를 넣었다가 손과 함께 빼냅니다.

**multi-task / dynamics / action-head (Table 3, 평균)**

| 설정 | DP-T | π0.5 |
|---|---|---|
| multi-task | 33.2 ±2.4 | 45.5 ±1.5 |
| rand-dynamics | 41.6 ±0.3 | 46.5 ±2.6 |
| rand-AH (full reinit) | — | 48.7 ±0.9 |

> "When jointly training on all tasks (Table 3, multi-task) with the same number of steps as single-task training, DP-T degrades on every task, while $`\pi_{0.5}`$ achieves a success rate increase on Click Mouse and Pinch Tongs, though its average success rate drops." (§4, Table 3)
> (한글 해설 — multi-task 합동 학습 시 DP-T는 전 태스크에서 퇴화하고, π0.5도 평균은 하락하지만 일부 태스크는 오히려 상승합니다. 우리가 P4에서 multi-task corpus 합성을 고려할 때 **degradation 위험**을 경고합니다.)

> "We compare partial pretrain-AH (Table 2) against fully random reinitialization (Table 3, rand-AH), and find that retaining pretrained weights yields higher success rates on most tasks and a better average." (§4, Table 3)
> (한글 해설 — partial pretrain-AH(π0.5 rand-obj 52.5) > 전체 random reinit(rand-AH 48.7). **사전학습 action-head 가중치 보존이 +약 3.8pp 우위**를 줍니다 — 우리 P4 D20(prior-preservation)을 직접 지지하는 외부 증거입니다. dynamics randomization에서도 π0.5(46.5)가 DP-T(41.6)보다 견고합니다.)

**언어 일반화 실패 (§4, App. A)** — π0.5를 Unlock iPad 단일 숫자(1–5) 비밀번호로 학습 후 seen 숫자·산술식(1+1, 2+2)·영단어(two)로 평가하면, 모델이 언어 조건화 대신 **고정 action bias**로 회귀합니다.

> "although a chi-square test rejects the hypothesis of strict independence ($`p=2.15\times 10^{-4}`$), confirming that the VLA does react to varying language instructions, the Normalized Mutual Information between instruction and output is only $`0.018`$, indicating a negligible relationship." (App. A)
> (한글 해설 — 통계적으로 지시에 반응은 하나(p≪0.05), 지시-출력 간 정규화 상호정보가 0.018로 사실상 무관합니다. 평균 JS divergence 0.026(최대 0.057)으로 어떤 프롬프트든 action 분포가 거의 동일 — 진정한 언어 일반화 실패입니다.)

---

## ⚖️ 한계

- **(저자 명시) dexterous-hand-centric foundation model 부재** — 현 VLA는 대개 gripper 데이터로 사전학습돼 dexterous hand에 action space mismatch가 생기고, action head가 고차원 관절 coupling을 못 잡아 표현력·전이가 제한됩니다. 메커니즘상 사전학습 우위가 손 차원에서 무력화되는 이유이며, embodiment-aware 표현 + hand-centric 사전학습을 요구합니다.
- **(저자 명시) vision-only의 contact-rich 한계** — 시각만으로는 접촉이 풍부한 조작에 부족하고, proprioception을 더해도 contact force 같은 핵심 단서를 놓칩니다. tactile 도입이 상호작용 모델링을 완성하므로 정밀에는 multi-modal 정책이 필요합니다(저자가 future work로 둠).
- **(저자 명시) sim-to-real 미해결** — 물리·시각·센싱 충실도를 높이면 zero-shot 전이가 개선되겠으나, 본 연구는 domain randomization 너머의 체계적 sim–real 정렬을 다루지 않았습니다. 모든 평가가 시뮬레이션입니다.
- **(추론된 갭) 단일 손·단일 팔 고정** — Allegro Hand + Franka Panda로 고정돼 hand embodiment 다양성이 없습니다. 손 종류·DOF가 바뀌면 retargeting·action head를 다시 맞춰야 하므로, 손 일반화를 측정하는 축이 벤치마크에 없습니다.
- **(추론된 갭) 데이터 규모** — 1.1K 궤적은 11개 태스크에 걸친 평가/소규모 학습용이지 사전학습 corpus 규모가 아닙니다. 절대 성공률이 낮은 데에는 in-domain 데이터 희소성도 일부 작용합니다.
- **(추론된 갭) success-rate 단일 메트릭** — 채점이 binary 성공/실패라 slip·접촉 안정성·정밀도 같은 contact-precision 차원을 분해하지 못합니다. 손 차별성을 "성공률"로만 보면 메커니즘 진단이 제한됩니다.

---

## ♻️ 재현성

- **코드 / toolkit** — 프로젝트 페이지 `https://dexjoco.github.io` 공개. teleoperation 시스템(약 \$2,300 USD 하드웨어 + 3D 프린팅 커넥터)과 retargeting(GeoRT 채택), 태스크 환경·학습 인터페이스·평가 유틸을 toolkit으로 제공. (본문 기준 GitHub repo URL은 별도 명시되지 않아 기재하지 않음.)
- **데이터** — 1.1K human demonstration 궤적. LeRobot·DP Zarr 등 주류 포맷으로 변환하는 인터페이스 제공.
- **물리/평가** — MuJoCo 물리 시뮬레이터 기반. 평가는 server–client 프레임워크 + 비동기 추론. 태스크별 randomization 설정은 App. C에 명시.
- **하드웨어/라이선스** — 실로봇 미사용(전부 시뮬레이션). 자산 출처는 RoboSuite/MuJoCo Menagerie/RoboCasa/SAPIEN/Hunyuan3D. 데이터·코드 라이선스는 본문에 명시되지 않음(카탈로그 등재 시 사람이 backfill).

---

## 🎯 관련 Pillar / Decision (P# / D#)

본 논문은 벤치마크/데이터셋 자원으로서 **P0(VLA Datasets & Benchmarks)** 에 1차로 닿고, 그 경험적 발견을 통해 P4·P1·P2를 부차적으로 건드립니다.

- **P0 D26(benchmark/eval scouting scope)** — 가장 직접적입니다. D26 v1은 "dexterous + contact-rich manipulation 벤치마크, sim(ManiSkill/Isaac/Robocasa) 추적, in-hand-rotation / articulated-tool eval(CATFA precedent) 우선"을 명시하는데, DexJoCo는 정확히 **MuJoCo 기반 dexterous task-oriented sim 벤치마크**이며 tool-use·관절형 물체(Microwave/iPad/Fold Glasses)를 포함해 articulated-tool 축과 겹칩니다. 카탈로그 `benchmark/dexterous/DexJoCo`로 등재합니다.
- **P0 D27(license/usability bar)** — 약 \$2,300 저비용 toolkit + LeRobot/DP Zarr 포맷 지원은 D27의 usability 기준에 부합하나, 데이터/코드 **라이선스가 본문 미명시**라 ⚠️ 플래그 대상입니다.
- **P4 D20(prior-preservation strategy) / D19(post-pretraining adaptation range)** — "partial pretrain-AH > full reinit(+약 3.8pp)"는 우리 prior-preservation 결정을 지지하는 외부 증거입니다. 또한 "gripper 사전학습 → dexterous action space mismatch, head가 관절 coupling을 못 잡음"은 D22(사전학습 구성)·D19(lineage·adaptation)에 직접 닿습니다.
- **P1 D3(Hand output space) / D7(π backbone 통합)** — 손 액션을 절대 관절각으로 두고, 추가 손 차원을 scratch 학습하면 π0.5 사전학습 우위가 희석된다는 발견은 Hand 출력 차원·action head 통합 설계(D3/D7)의 직접 증거입니다.
- **P2 D9/D10(관측 인코더·fusion 방식)** — DP-C의 FiLM 관측 주입이 fine-grained 정밀 조작에서 우위라는 가설, 그리고 vision-only 부족·tactile 필요라는 Discussion은 우리 P2 thesis(concat 초월 fusion + tactile token)를 외부에서 뒷받침합니다.

**Identity 긴장** — 우리 식별성의 차별화 축은 *per-finger 접촉·tactile·contact-precision*인데, DexJoCo는 *vision+proprio, tactile 없음, success-rate-only, Allegro 고정*입니다. 측정 도구로는 유용하나 우리 핵심 falsifier(slip/접촉 안정성)를 그대로 재지 못합니다(지지보다 보완).

**경쟁자 함의** — 직접 경쟁자는 아니며, 저자진(CASIA·Galbot·He Wang)이 dexterous 데이터·foundation 라인과 겹쳐 P0/P4 watch 대상입니다.

---

## ✨ 핀 논문 대비 델타

- **ManiSkill 3([arXiv:2410.00425], P0 핀 sim 벤치마크) 대비** — ManiSkill 3은 SAPIEN GPU 고처리량 범용 sim이고 dexterous는 일부입니다. DexJoCo의 새로움은 **"손이 아니면 못 푸는" 기능적 tool-use 태스크에 특화**한 점, 그리고 RL/자동 생성이 아니라 **저비용 mocap-glove 인간 시연**으로 자연스러운 궤적을 수집하는 toolkit입니다(MuJoCo 기반).
- **CATFA([arXiv:2509.23075], MASTER §3.5 phase 2 / benchmarks.md ✋ Dexterous 핀) 대비** — CATFA는 5-tool tool-articulation eval 셋입니다. DexJoCo는 tool-use를 포함하되 **bimanual·long-horizon·reasoning까지 11개로 범주를 확장**하고, 평가 전용을 넘어 **데이터 수집 toolkit + 1.1K 데이터셋 + 통일 포맷**을 함께 제공합니다(폭과 인프라가 델타).
- **vla-eval([arXiv:2603.13966], P0 핀 eval harness) 대비** — vla-eval은 모델×벤치마크 통합 비용을 줄이는 *실행 인프라*(메트릭은 success-rate)입니다. DexJoCo는 정반대로 **태스크 자체(손 차별성 측정)와 데이터 수집을 정의**하는 콘텐츠형 벤치마크입니다. 둘은 직교·상보적입니다(실행 인프라 vs 측정 대상).
- **요약 델타** — "범용 sim 벤치마크"나 "tool-articulation eval"이 아니라, **dexterous 차별성 + 저비용 인간 시연 toolkit + LeRobot 호환 데이터**를 한 묶음으로 제공하고 현대 VLA의 공통 실패를 정량화한 자원입니다.

---

## ⚙️ 의사결정 함의

- **prior-preservation 기본값 강화 (P4 D20)** — π0.5를 dexterous hand로 적응시킬 때 **사전학습 action-head 가중치는 유지하고 추가 손 차원만 random init**(partial pretrain-AH)하는 것을 기본으로 채택. config 키: action-head 초기화 모드 = `partial-reinit`(전체 reinit 대비 +약 3.8pp). 우리 학습 스크립트의 head 초기화 분기에 못 박을 것.
- **multi-task degradation 모니터링 (P4 D21/D22)** — multi-task 합동 학습이 DP-T를 전 태스크 퇴화시켰으므로, 우리가 corpus를 다태스크로 합성할 때 per-task 성공률 회귀를 ablation 지표로 추적(π0.5가 DP-T보다 견고하다는 점도 backbone 선택 근거).
- **언어 조건화 검증 메트릭 (P1/P4)** — 태스크 스펙을 언어 지시에 의존시키려면 **NMI(instruction↔output)·JS divergence**로 실제 조건화 여부를 falsify. DexJoCo 사례(NMI 0.018)는 "언어를 받는다 ≠ 조건화한다"를 보여, 우리 goal-centric 스펙이 언어에 과의존하지 않도록 경계.
- **평가 자원 후보 + 포맷 정렬 (P0 D26/D27)** — DexJoCo는 **LeRobot 포맷 export**를 지원하므로 LeRobot 계열 데이터 경로와 직접 호환됩니다. tool-use 태스크(Hammer/Water Plant/Pinch Tongs)는 우리 phase-2 tool-articulation flagship과 의미적으로 겹쳐 보조 eval 후보. 단 Allegro·tactile 부재·MuJoCo 제약(아래 ⚠️) 확인 후 채택.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 체크) 손 하드웨어 불일치** — DexJoCo는 Allegro Hand(16-DOF) 고정, 우리는 Sharpa(22-DOF)/xhand 목표입니다. 5분 체크: toolkit이 손 자산 교체를 지원하는지(MuJoCo Menagerie 기반이라 모델 추가 가능하나 retargeting·success 조건 재정의 필요) 확인 → 그대로는 우리 손 평가 불가.
- **tactile/force 부재** — 관측이 vision+proprio뿐이라 우리 P2/P3의 contact-precision 차별성(per-finger tactile, slip)을 **측정할 축이 없습니다**. 우리 falsifier(slip count·pose stability)는 DexJoCo success-rate로 대체 불가 — 보조 eval로만.
- **MuJoCo vs Isaac 스택 분리** — 우리 System0 학습은 Isaac Sim + Isaac Lab(§4.2)인데 DexJoCo는 MuJoCo입니다. 접촉 모델(PhysX vs MuJoCo)·환경 코드가 달라 직접 재사용 비용이 큼. 데이터(LeRobot 포맷)는 호환되나 *환경*은 호환 안 됨.
- **데이터 성격(teleop ≠ egocentric)** — 1.1K 궤적은 Rokoko glove teleoperation + GeoRT retarget 결과이지, 우리 D24 우선축인 **egocentric 인간 영상**이 아닙니다. 사전학습 corpus로 끌어 쓰기엔 규모·성격이 맞지 않음(평가/소규모 학습용).
- **절대 성공률 해석 주의** — Assembly/Hanoi가 거의 0%인 것은 모델 한계뿐 아니라 in-domain 데이터 희소·동시-제약 채점의 엄격함도 섞인 결과입니다. 모델 비교에는 유효하나 절대 난이도를 우리 태스크로 직역하면 과해석 위험.

---

## 💡 컨텍스트 제안

- **P0 카탈로그 등재** — `catalogs/benchmarks.md` ✋ Dexterous 섹션에 DexJoCo 추가(카탈로그 라우팅 `benchmark/dexterous/DexJoCo`가 skeleton row 생성). 라이선스는 본문 미명시이므로 ⚠️ 플래그로 backfill 제안.
- **P4 D20 노트 보강 후보** — "partial pretrain-AH > full reinit(+약 3.8pp, DexJoCo)" 한 줄을 prior-preservation 외부 증거로 D20 옆에 메모 검토(핀 교체는 사람 판단).
- **P0 D26 phasing 연결** — DexJoCo tool-use 태스크(Hammer/Water Plant/Pinch Tongs)는 MASTER §3.5 phase-2 tool-articulation(CATFA precedent)과 의미적으로 겹쳐, 보조 eval 레퍼런스로 추적 가치. 단 Allegro·tactile 부재로 우리 식별성 평가 축은 별도 필요.
- context/ 파일은 수정하지 않았습니다 — 위는 모두 제안입니다.
