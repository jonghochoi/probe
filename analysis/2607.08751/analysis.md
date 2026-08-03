# Paper Analysis — DexVerse: A Modular Benchmark for Multi-Task, Multi-Embodiment Dexterous Manipulation

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | DexVerse: A Modular Benchmark for Multi-Task, Multi-Embodiment Dexterous Manipulation |
| 저자 | Yunchao Yao, Zhuxiu Xu, Tianqi Zhang, Zixian Liu, Sikai Li, Zhenyu Wei, Feng Chen, Dihong Huang, Kechang Wan, Chenyang Ma, Shuqi Zhao, Shenghua Gao, Masayoshi Tomizuka, Yi Ma, Mingyu Ding (UNC-Chapel Hill · The University of Hong Kong · UC Berkeley) |
| 링크 | [arXiv:2607.08751](https://arxiv.org/abs/2607.08751) · [Website](https://ycyao216.github.io/DexVerse.site/) |
| 발행일 / 버전 | 2026-07-09 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-08-02 |
| 관련 Pillar | P0, P2, P4, P3 |
| 태그 | dataset, dexterity |

<!-- 본문·부록 전체를 arXiv HTML(전문)로 확보했습니다. 모든 수치는 본문/표에서
     받은 그대로 인용했습니다.
     프로젝트 페이지 링크는 논문 초록 및 arXiv abs 페이지에 명시된 공식 URL을
     그대로 옮긴 것이며, 본 실행 환경의 네트워크 정책이 해당 호스트를 차단해
     응답 확인은 하지 못했습니다:
       curl -o /dev/null -sS -w "%{http_code}" -L "https://ycyao216.github.io/DexVerse.site/"
       → curl: (56) CONNECT tunnel failed, response 403
     공식 코드 저장소 URL은 본문 어디에도 명시되지 않아 기재하지 않았습니다. -->

---

## 🧭 한 줄 요약 (TL;DR)

DexVerse 는 8개 카테고리 100개 dexterous manipulation 태스크를 Isaac Lab 위에 config 주도 모듈 구조로 구현하고, 3개 arm × 6개 dexterous hand · 제어 가능한 시각 변이 · VR 텔레오퍼레이션으로 모은 3,180개 데모(proprio / RGB / depth / point cloud / state 동기화)를 함께 공개하는 벤치마크입니다. 19개 태스크에서 Diffusion Policy · DP3 · OpenVLA · $`\pi_{0.5}`$ 를 평가한 결과 최고 성적이 평균 성공률 0.34 에 그쳤고, 특히 sub-centimeter 정밀 접촉 태스크는 네 정책 모두 0.00 으로 붕괴해 벤치마크가 아직 포화되지 않았음을 보입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — dexterous manipulation 정책이 "고립된 스킬 몇 개"를 넘어 다양한 상호작용 양식·감각 조건·로봇 임베디먼트를 가로질러 얼마나 일반화되는지를 한 플랫폼에서 체계적으로 재는 벤치마크가 없습니다. 저자들은 그 측정 인프라 자체를 산출물로 삼습니다.
- **기존 접근의 한계** — CALVIN·LIBERO·RoboTwin 2.0·ManiSkill3 같은 long-horizon 벤치마크는 주로 gripper 기반이고, dexterous 쪽 벤치마크(DexMimicGen, Bi-DexHands, DexJoCo, DexHoldem, DexH2R)는 데모 생성·RL·특정 도메인 등 좁은 설정에 특화되어 있습니다. Table 1 기준 "폭넓은 dexterous 태스크 + 다중 임베디먼트 + 제어 가능한 시각 변이 + 데모 데이터셋 + 병렬 RL 환경"을 동시에 만족하는 기존 스위트는 없습니다.
- **본 논문의 가설** — 태스크 환경과 로봇 임베디먼트를 config 레벨에서 분리(decouple)하면, 하나의 태스크 정의를 여러 arm-hand 조합·관측 모달리티·시각 조건에 재사용할 수 있고, 그때 비로소 cross-task / cross-embodiment 일반화를 통제된 조건에서 비교할 수 있다는 것입니다.
- **왜 지금 중요한가** — VLA·diffusion policy 계열이 빠르게 늘고 있지만 이들이 고DoF 다지(multifinger) 접촉 제어로 실제로 확장되는지는 확인된 바가 없습니다. 저자들의 평가는 인터넷 스케일 사전학습 VLA 가 from-scratch diffusion policy 를 넘지 못한다는 결과를 내놓아, 현재 스케일링 서사에 직접적인 반례를 제공합니다.
- **평가 인프라로서의 요구** — 물리 시뮬레이션은 머신마다 발산하므로, 데모를 관측 텐서 덤프가 아니라 action-state 시퀀스로 저장하고 로컬에서 관측을 재생성하는 replay 설계가 필요하다는 것이 이 논문이 세운 재현성 요구사항입니다.

---

## 🧩 핵심 기여

- **100개 태스크 · 8개 카테고리의 dexterous 태스크 스위트** — primitive(9) / functional(11) / articulation(18) / non-prehensile(5) / contact-rich(8) / bimanual coordination(5) / multi-goal(39) / long-horizon(5). 객체 종류가 아니라 *지배적 상호작용 패턴* 기준으로 분류해 접촉 양식별 분석이 가능하도록 설계했습니다.
- **임베디먼트 분리형 모듈 환경** — Isaac Lab 의 manager-based 인터페이스 위에 scene / asset / embodiment / observation / action / init / success / randomization 을 config 클래스로 쪼개, 태스크 로직을 재작성하지 않고 3개 arm × 6개 hand 조합을 갈아끼울 수 있게 했습니다.
- **제어 가능한 시각 변이** — 객체·테이블 재질, 조명, 배경 skybox, 노출, 색온도, 카메라 시점을 reset 시점에 라이브러리에서 샘플링합니다. 시각 변이와 비시각 변이(초기 pose, 동역학 파라미터, proprio/object-state 섭동)를 독립적으로 켤 수 있습니다.
- **VR 텔레오퍼레이션 파이프라인과 3,180개 데모** — Apple Vision Pro → Isaac Lab CloudXR XR 인터페이스 → 손목 pose 는 IK, 손가락은 optimization 기반 dex-retargeting. 데모는 action-state 쌍으로 저장되고 replay 유틸리티가 관측을 로컬 재생성합니다.
- **9개 관측 그룹 인터페이스** — policy / proprio / **contact** / state / privileged / goal / rgb / depth / pointcloud. 특히 `contact` 그룹은 설정된 contact sensor 마다 **fingertip 별 3D 접촉력 벡터**를 로봇 base frame 기준으로 제공합니다.
- **19개 태스크 베이스라인 평가** — Diffusion Policy · DP3 · OpenVLA · $`\pi_{0.5}`$ 를 동일 950 에피소드로 학습하고 동일 시뮬레이터에서 closed-loop 평가했습니다. 최고 평균 성공률 0.34, 정밀 접촉 태스크 전면 붕괴.

---

## 🔑 기술 키워드

- **Manager-based environment interface** — Isaac Lab 이 제공하는 환경 구성 방식으로, 관측·행동·이벤트·종료·보상 항을 각각 "manager" 설정 클래스로 선언하고 공용 시뮬레이션 루프가 그것을 실행합니다. 태스크를 코드가 아니라 설정으로 조립하는 방식입니다.
- **Task specification tuple** — 태스크를 $`\mathcal{T}=(\Omega,\mathcal{S}_{0},\mathcal{O},\mathcal{A},\mathcal{G})`$ 로 형식화한 것. 씬의 상호작용 객체, 초기 상태 분포, 관측/행동 인터페이스, 성공 조건을 한 튜플로 묶어 태스크와 임베디먼트를 분리합니다.
- **Success predicate** — 성공 조건을 시뮬레이터 술어(predicate)로 구현한 것. "0.20 m 이상 들어올림", "축으로부터 0.0025 m 이내" 처럼 임계값이 명시되어 있어 성공률이 주관적 판정 없이 산출됩니다.
- **Observation group** — 의미 역할이 하나인 관측 항들의 묶음. 소비자(정책 / asymmetric critic / perception backbone)가 필요한 그룹만 구독하도록 만든 인터페이스로, 상태 기반·이미지 기반·point cloud 기반 정책을 같은 환경에서 돌릴 수 있게 합니다.
- **Observation-mode preset** — 관측 그룹 조합을 미리 묶어둔 프리셋(`state`, `rgb`, `rgb_depth`, `pointcloud`, `3view_*`). 각 프리셋은 열거된 그룹만 켜고 나머지를 끄며 history length 와 multiview 여부를 함께 고정합니다.
- **Privileged observation** — 로봇 관절 속도, 손 링크 전체 body state, 객체 선·각속도처럼 실세계에서 관측하기 어려운 시뮬레이터 전용 양. 어떤 프리셋도 이 그룹을 켜지 않으며 사용자가 의도적으로만 활성화합니다.
- **Dex-retargeting** — 사람 손 동작을 최적화로 각 dexterous hand 의 목표 관절 pose 로 변환하는 절차. 손 형상이 서로 다른 6종 hand 에 같은 사람 시연을 흘려보내는 다리 역할을 합니다.
- **Action-state replay** — 데모를 관측 텐서가 아니라 (행동, 시뮬레이터 상태) 시퀀스로 저장하고, 재생 시 상태를 복원한 뒤 환경에 관측을 다시 질의하는 저장 방식. 머신 간 물리 발산과 rollout drift 를 피하고 데이터셋을 가볍게 만듭니다.
- **Floating hand variant** — 각 hand 의 손목을 prismatic·revolute 관절로 직접 제어하는 변형. arm 을 배제하고 손 자체 제어만 분리해 평가할 수 있게 합니다.
- **Online success rate** — 학습된 정책을 시뮬레이터에서 실제로 굴려(태스크당 50 에피소드) 성공 술어 충족 비율로 매기는 지표. offline action MSE 가 아니라 closed-loop 결과를 잽니다.

---

## 🔬 방법론

### 직관

DexVerse 는 "새 정책을 제안하는 논문"이 아니라 "정책을 재는 자를 만드는 논문"입니다. 문제의식은 단순합니다. dexterous manipulation 은 접촉 양식(집기, 밀기, 관절 열기, 끼우기), 손 형상(Allegro 4지 vs Shadow 5지), 관측 모달리티(RGB, depth, point cloud, 접촉력), 시각 조건이 모두 결과를 흔드는데, 기존 벤치마크는 이 축들 중 한둘만 다루기 때문에 어떤 정책이 왜 잘/못 하는지를 분리해 볼 수 없다는 것입니다.

해법의 핵심은 **분리(decoupling)** 입니다. 태스크는 "무엇을 성공으로 볼 것인가"만 정의하고(어떤 객체가 씬에 있는지, 초기 상태를 어떻게 뽑는지, 성공 술어가 무엇인지), 로봇은 별도의 robot config 로 정의합니다. 이 두 축이 config 레벨에서 갈라져 있으므로 같은 `OpenLaptop` 태스크를 Franka + Shadow Hand 로도, xArm 7 + LEAP Hand 로도, 손목을 직접 구동하는 floating hand 로도 인스턴스화할 수 있습니다. 관측 역시 9개 "그룹"으로 쪼개져 있어 상태 기반 정책은 `proprio`+`state` 만, point cloud 정책은 `pointcloud`+`proprio` 만 구독합니다. 시각 변이는 또 하나의 config 스위치로, 재질·조명·배경·노출·색온도·카메라 시점을 reset 마다 다시 뽑되 성공 조건은 그대로 둡니다.

데이터 쪽은 Apple Vision Pro 로 시뮬레이션 화면을 보면서 맨손으로 시연하면, 손목 pose 는 IK 로 로봇 팔에, 손가락 동작은 최적화 retargeting 으로 각 dexterous hand 관절에 전달되는 구조입니다. 여기서 눈여겨볼 설계는 저장 포맷입니다. 관측 이미지를 통째로 굽지 않고 (행동, 시뮬레이터 상태) 만 남긴 뒤, 쓰는 쪽에서 상태를 복원해 원하는 관측 항을 다시 렌더링합니다. 물리 엔진이 머신마다 미세하게 다르게 굴러도 상태를 직접 되돌리므로 오차가 누적되지 않고, 나중에 카메라를 하나 더 붙이고 싶어도 데이터셋을 다시 모을 필요가 없습니다.

마지막으로 저자들은 이 자를 실제로 대 봅니다. 성격이 다른 네 정책 — 상태만 보는 Diffusion Policy, point cloud 를 보는 DP3, 인터넷 스케일로 사전학습된 OpenVLA 와 $`\pi_{0.5}`$ — 을 같은 950 에피소드로 학습시켜 19개 태스크에서 굴린 결과, 최고가 평균 0.34 이고 정밀 끼우기·밀기 계열은 전부 0 입니다. 즉 이 벤치마크는 아직 아무도 풀지 못한 상태이며, 그 미해결 영역이 정확히 "지속적 힘 조절과 sub-centimeter 정렬"이라는 것이 논문의 결론입니다.

### 아키텍처 — 모듈형 환경 설계

🔗 [Figure 1 — DexVerse overview](https://arxiv.org/html/2607.08751/figure/DexVerse_teaser.png) (arXiv 원본 6.4 MB — GitHub 이미지 프록시 상한을 넘어 인라인 렌더가 불가하므로 링크로 둡니다)

> "Figure 1: Overview of DexVerse, a modular benchmark for multi-task, multi-embodiment dexterous manipulation with diverse tasks, visual variations, demonstration datasets, and baseline evaluations." (§1)
(벤치마크가 태스크 스위트 · 시각 변이 · 데모 데이터셋 · 베이스라인 평가의 네 축으로 구성됨을 한 장으로 보여 주는 그림입니다.)

환경은 코드가 아니라 설정으로 조립됩니다. 같은 계열 태스크는 asset 로딩·상태 초기화·reset 이벤트·성공 판정 같은 공통 로직을 템플릿으로 공유하고, 태스크별 파라미터가 조작 대상 객체·목표 상태·샘플링 범위·완료 임계값을 지정합니다.

> "DexVerse builds on the manager-based environment interface of Isaac Lab, where observations, actions, events, terminations, and optional reward terms are specified through configuration classes and executed by a shared simulation loop." (§3.1)
(관측·행동·이벤트·종료·보상이 각각 별도 config 클래스로 선언되고 공용 루프가 이를 실행하는 구조라, 초기화 범위·카메라 설정·랜덤화 옵션·성공 임계값을 코어 코드를 건드리지 않고 override 로 바꿀 수 있습니다. 벤치마크 확장성의 실질적 근거가 여기에 있습니다.)

![Figure 4 — Modular environment architecture](https://arxiv.org/html/2607.08751/x3.png)

> "Figure 4: Modular Environment Architecture" (§3.1)
(태스크 템플릿 · 로봇 config · 관측/행동 인터페이스 · 랜덤화가 어떻게 층으로 갈라져 하나의 환경 인스턴스로 합쳐지는지를 도식화한 그림입니다.)

### 태스크 사양과 성공 조건

태스크는 하나의 튜플로 형식화됩니다.

> "Each task is specified as $`\mathcal{T}=(\Omega,\mathcal{S}_{0},\mathcal{O},\mathcal{A},\mathcal{G})`$ , where $`\Omega`$ denotes the interactive objects in the scene, $`\mathcal{S}_{0}`$ denotes the initial-state distribution, $`\mathcal{O}`$ and $`\mathcal{A}`$ denote the task observation and action interfaces, and $`\mathcal{G}`$ denotes the task-level success conditions." (§3)
(태스크가 "객체 집합 + 초기 상태 분포 + 관측/행동 인터페이스 + 성공 조건"으로만 정의되므로, 로봇 사양은 이 튜플 바깥에 남고 임베디먼트 교체가 태스크 재작성 없이 성립합니다. 이것이 multi-embodiment 지원의 형식적 뿌리입니다.)

$`\mathcal{G}`$ 는 시뮬레이터 술어로 구현됩니다. Appendix A 의 태스크 표에는 임계값이 그대로 적혀 있습니다 — `PickCube` 는 reset 높이 대비 0.20 m 이상 들어올림, `PushT` 는 목표 T 자 footprint 의 90% 이상 겹침, `InsertGear` 는 축 중심 0.0025 m 이내 · 완전 삽입 깊이 0.003 m 이내, `NutThread` 는 볼트 축 0.0025 m 이내 · 목표 깊이 약 0.002 m 이내(볼트 약 1.5 회전), `PlugCharger` 는 측방 오차 0.0025 m 미만. 뒤의 결과 섹션에서 전 정책 0.00 이 나오는 태스크들이 왜 그렇게 되는지는 이 임계값 목록만 봐도 상당 부분 설명됩니다.

8개 카테고리 구성은 다음과 같습니다 (Table 2).

| Category | # | Representative tasks | Key challenge |
|---|---|---|---|
| Primitive | 9 | PickCube, StackCube, RelocateSphere, PushButton | Direct interaction with simple goals and limited action complexity. |
| Functional | 11 | HammerStrike, RetrieveCup, GraspKettle, PourCan | Affordance-aware interaction with task-relevant object regions. |
| Articulation | 18 | OpenStapler, OpenLaptop, SqueezeScissors, OpenPhone | Controlling object parts and joints, under constrained motion. |
| Non-prehensile | 5 | PushT, TakeBook, PivotCuboid, PushSphereObstacle | Using pushing, sliding, pivoting, or environmental contact. |
| Contact-rich | 8 | InsertPeg, PlugCharger, NutThread, InsertGear | Precise alignment under sustained contact and tight constraints. |
| Bimanual Coordination | 5 | BiLiftTray, BiHandover, BiLiftBox, BiLiftCart | Coordinated stabilization, transfer, or cooperative manipulation. |
| Multi-goal | 39 | GraspMug + PushButton, GraspCan + TurnOnSwitch | Satisfying multiple goals or compositional objective conditions. |
| Long-horizon | 5 | MakeCoffee, MicrowaveFood, CleanTable, OvenBake | Completing temporally extended multi-stage procedures. |

![Figure 2 — Selected DexVerse tasks](https://arxiv.org/html/2607.08751/x1.png)

> "Figure 2: Visualization of selected tasks from the DexVerse environments." (§3)
(카테고리별 대표 태스크의 실제 렌더링으로, 태스크 다양성 주장의 시각적 근거입니다.)

![Figure 3 — Long-horizon task progression](https://arxiv.org/html/2607.08751/x2.png)

> "Figure 3: Visualization of task progression of the 5 long-horizon tasks in DexVerse environments." (§3)
(long-horizon 5개 태스크가 어떤 단계로 쪼개지는지를 보여 주는 그림으로, 이 카테고리는 Table 3 베이스라인 평가에 하나도 포함되지 않아 수치가 전무한 영역입니다.)

카테고리 구성에서 눈에 띄는 점은 multi-goal 이 39개로 전체의 39%를 차지한다는 사실입니다. 즉 100 이라는 숫자의 상당 부분은 기존 단일 목표 태스크를 조합한 합성 목표이며, 물리적으로 새로운 상호작용을 40% 가까이 추가한 것은 아닙니다.

### 로봇 임베디먼트와 시각 변이

> "The current benchmark supports 3 robot arms (Franka Research 3, UR10e, and xArm 7) and 6 dexterous hands (Sharpa Wave, WUJI Hand, Shadow Hand, Inspire Hand, Allegro Hand, and LEAP Hand), covering diverse kinematics, degrees of freedom, joint limits, actuation ranges, and hand morphologies." (§3.2)
(우리 스택의 근시일 하드웨어인 **Sharpa Wave** 가 지원 목록에 직접 포함되어 있다는 점이 이 논문에서 가장 실무적으로 중요한 한 줄입니다. Sharpa 계열 hand 가 들어간 공개 시뮬레이션 벤치마크는 흔치 않습니다.)

각 hand 는 손목을 prismatic·revolute 관절로 직접 구동하는 floating variant 를 함께 제공하므로, arm 을 제거하고 손 자체 제어만 분리해 평가하는 셋업이 가능합니다.

시각 변이는 성공 조건을 건드리지 않은 채 관측만 흔드는 방식으로 설계됩니다.

> "When enabled, visual properties are sampled at reset from predefined libraries, including object materials, table materials, lighting conditions, background skyboxes, exposure, and color-temperature settings." (§3.3)
(reset 시점 샘플링이라 에피소드 내부에서는 외형이 고정되고, 에피소드 간에만 분포가 바뀝니다. 정책의 시각 강건성을 태스크 난이도 변화와 섞지 않고 분리 측정할 수 있는 형태입니다.)

asset 은 PartNet-Mobility, ManiTwin, NVIDIA Isaac Lab/Isaac Sim, AutoBio, 공개 Synthesis asset 에서 가져오고, 적합한 객체가 없을 때는 Meshy 로 참조 이미지에서 메시를 생성한 뒤 수작업으로 시뮬레이션용 처리를 합니다. 시각 변이용으로는 Poly Haven 의 HDR skybox 100장과 Isaac Lab/Isaac Sim 의 테이블 재질 랜덤화를 씁니다 (§3.4).

### 관측 인터페이스

관측은 9개 그룹으로 나뉩니다 — `policy`(직전 행동), `proprio`(전 관절 위치), `contact`, `state`(객체 pose, 관절 위치, functional-point 위치와 축 방향, long-horizon 태스크의 stage 진행도), `privileged`, `goal`, `rgb`, `depth`, `pointcloud`.

> "Contains a per-fingertip 3D contact-force vector for each configured contact sensor, expressed in the robot base frame. This group is None when contact sensors are disabled for a task." (Appendix C)
(fingertip 단위 3D 접촉력이 base frame 기준으로 그룹화되어 제공된다는 뜻으로, per-finger 접촉 귀속(attribution)을 유지한 채 관측을 구성할 수 있는 몇 안 되는 공개 시뮬레이션 환경입니다. 다만 아래 한계에서 보듯 논문 자체의 베이스라인은 이 그룹을 하나도 쓰지 않습니다.)

프리셋은 다음과 같습니다 (Table 5). `privileged` 는 어떤 프리셋에서도 켜지지 않습니다.

| Preset | Groups enabled | History length | Multiview |
|---|---|---|---|
| state | policy, proprio, contact, state, goal | 0 | no |
| rgb | policy, proprio, goal, rgb | 3 | no |
| rgb_depth | policy, proprio, goal, rgb, depth | 3 | no |
| pointcloud | policy, proprio, goal, pointcloud | 3 | no |
| 3view_rgb | policy, proprio, goal, rgb | 3 | yes |
| 3view_rgb_depth | policy, proprio, goal, rgb, depth | 3 | yes |
| 3view_pointcloud | policy, proprio, goal, pointcloud | 3 | yes |

`contact` 그룹이 켜지는 프리셋이 `state` 하나뿐이고, 그 프리셋은 history length 가 0 이라는 점은 그대로 기록해 둘 만합니다. 접촉 이력을 쓰려면 프리셋을 벗어나 그룹을 직접 조합해야 합니다.

### 텔레오퍼레이션 데이터 파이프라인

![Figure 6 — Teleoperation data collection](https://arxiv.org/html/2607.08751/x6.png)

> "Figure 6: Teleoperation data collection system." (§4)
(Vision Pro 핸드 트래킹 → 손목 IK · 손가락 retargeting → 시뮬레이션 로봇으로 이어지는 수집 경로를 보여 줍니다.)

> "The tracked human wrist pose is used as the target pose for the robot end-effector, and the robot arm follows this target through an inverse-kinematics controller. Human hand motion is converted into target joint poses for different dexterous hands using optimization-based dex-retargeting [42] (Figure 6)." (§4)
(손목은 pose 목표 + IK, 손가락은 최적화 retargeting 이라는 이원 구조입니다. 우리 P1 D2(Body 출력 = 양손목/툴 플랜지 pose) 와 P1 D3(Hand 출력 = 손가락 관절 명령) 의 분리와 정확히 같은 경계선을 데이터 수집 측에서 채택한 셈이라, 이 데이터셋의 액션 라벨은 우리 아키텍처의 출력 공간과 자연스럽게 맞물립니다.)

새 arm 추가는 end-effector frame · 초기 pose · 저수준 컨트롤러 파라미터 갱신으로, 새 hand 추가는 keypoint · correspondence link · retargeting scale 을 담은 URDF 설정으로 끝나도록 설계되었습니다.

데이터 규모는 다음과 같습니다.

> "For each of the 56 single-goal tasks, we collect 55 demonstrations: 50 with the Shadow Hand and one with each of the other five hand embodiments." (§4)
(56 × 55 + 5 × 20 = 3,180. 즉 3,180개 중 학습 가능한 밀도로 모인 것은 Shadow Hand 분(56 × 50 = 2,800)뿐이고, 나머지 5종 hand 는 태스크당 1개씩입니다. "multi-embodiment 데이터셋"이라는 표현이 실제로 무엇을 의미하는지 정확히 알고 써야 하는 대목입니다.)

> "We provide the replay utility that restores the recorded simulator states and queries the environment locally to regenerate the requested observation terms. This design is important because physics simulation can diverge across machines due to differences in physics computation, hardware, and floating-point rounding." (§4)
(관측을 굽지 않고 상태만 저장하는 선택은 재현성 문제이자 확장성 문제입니다. 카메라를 추가하거나 관측 프리셋을 바꿔도 데이터셋 사본을 다시 만들 필요가 없고, rollout drift 누적도 피합니다.)

### 학습 목표 / 손실

**본 논문은 새 학습 목표나 손실을 제안하지 않습니다.** 평가된 네 정책은 모두 기존 공개 방법(Diffusion Policy, DP3, OpenVLA + OFT, $`\pi_{0.5}`$)이며, 논문의 기여는 이들을 공통 조건에서 굴리는 환경·데이터·프로토콜입니다. 아래 학습 셋업은 벤치마크 재현을 위한 설정값이지 새로 제안된 알고리즘이 아닙니다.

### 학습 셋업 (베이스라인, Appendix B)

네 베이스라인은 동일 코퍼스로 학습되고 동일 시뮬레이터에서 평가됩니다.

> "All four methods are trained using the same set of 950 episodes (19 tasks × 50 episodes per task) of the DexVerse teleoperation corpus, and evaluated closed-loop in the same simulator under identical termination criteria." (§4.1)
(데이터·종료 조건은 통제되었습니다. 다만 아래에서 보듯 관측 모달리티, 적응 범위(full FT vs LoRA), 학습 예산은 통제되지 않았습니다.)

- **$`\pi_{0.5}`$** — 공식 3.3B 체크포인트 full fine-tuning. 관측은 256×256 RGB 2장(고정 3인칭 + 손목; bimanual 은 3인칭 + 좌/우 손목 3장)과 태스크별 자연어 지시.
  > "the policy is conditioned on vision and language only, as the proprioceptive-state input is disabled." (Appendix B)
  (28/56차원 관절을 가진 dexterous hand 를 다루면서 proprioception 을 끈 셋업입니다. 아래 ⚖️ 한계에서 다시 다루지만, 이 한 줄이 "인터넷 스케일 사전학습이 도움이 안 된다"는 결론의 해석을 상당히 흔듭니다.)
  Gemma action expert 가 flow matching 으로 절대 관절 목표 28/56차원의 10-step chunk 를 예측. 32× H20, 2K step, AdamW ($`\beta=(0.9,0.95)`$, weight decay $`10^{-10}`$, grad-norm clip 1.0), global batch 512, cosine 스케줄(100-step warmup, peak $`10^{-4}`$ → $`10^{-6}`$).
- **OpenVLA** — `openvla-7b` 를 OFT 레시피로 fine-tuning. 이산 7-token action head 를 연속 $`L_{1}`$ 회귀 head 로 교체해 8-step chunk 의 절대 관절 목표를 출력. 관측은 $`\pi_{0.5}`$ 와 같은 RGB 세트 + 학습형 proprioceptive projector 로 인코딩한 현재 28/56차원 관절 위치 + 언어 지시. **LoRA(rank 32)** 를 모든 linear layer 에 부착하고 base weight 는 동결, 회귀 head 와 proprio projector 만 from-scratch 학습. 8× H20, 3K step, AdamW lr $`10^{-4}`$ (multi-step 으로 10× 감쇠), per-GPU batch 8, random-crop 증강.
- **Diffusion Policy (state-based)** — 태스크별 개별 정책. 정규화된 proprioceptive state 만 입력하고 **시각 입력 없음**. 1D conditional U-Net + FiLM, 채널 (256, 512, 1024), stage 당 residual block 2개. 관측은 256-d 인코더 → 128-d 조건 벡터. $`T_{o}=2`$, $`T_{a}=16`$, stride 1, chunk 마다 재계획. DDPM 목적함수, 100 timestep, squared-cosine $`\beta`$ 스케줄, 추론 20 denoising step. AdamW (lr $`1\times10^{-4}`$, weight decay $`1\times10^{-4}`$), batch 256, grad clip 1.0, EMA decay 0.995. 최대 300 epoch + held-out validation loss 기반 early stopping.
- **3D Diffusion Policy (DP3)** — 태스크별 개별 정책. point cloud + proprioception 조건, **RGB·언어 입력 없음**. 정면 depth 카메라 1대에서 역투영한 workspace-crop point cloud (bimanual 은 2 view 융합)를 world frame 에서 farthest-point 다운샘플 $`N=512`$ 점. 경량 PointNet 인코더(per-point MLP + LayerNorm, max-pool, 64-d 투영) + flatten 된 proprio 이력으로 global 조건 벡터 구성. denoiser 는 같은 1D conditional U-Net 이되 채널 (512, 1024, 2048), kernel 5, GroupNorm 8 groups. $`T_{o}=2`$, $`T_{a}=16`$, 첫 8 step 실행 후 재계획. DDIM 목적함수, 100 timestep, squared-cosine $`\beta`$, 추론 10 denoising step. 학습 split 통계로 point cloud · proprio · action 을 $`[-1,1]`$ 로 정규화. AdamW (lr $`1\times10^{-4}`$, weight decay $`1\times10^{-6}`$, $`\beta=(0.95,0.999)`$), batch 128, grad clip 1.0, EMA max-decay 0.9999, 100 epoch.

네 정책이 보는 것이 각각 (RGB+언어) / (RGB+언어+proprio) / (proprio only) / (point cloud+proprio) 로 전부 다르다는 점을 여기서 붙들어 둘 필요가 있습니다. Table 3 의 순위는 방법론 차이와 관측 모달리티 차이가 섞인 값입니다.

---

## 📊 실험 설정과 결과

평가는 19개 태스크, 태스크당 rollout 50 에피소드, 지표는 평균 online success rate 입니다.

> "For every task we roll out 50 episodes and report the mean success rate." (§4.1)
(offline action error 가 아니라 closed-loop 성공 술어 충족률이며, 성공 술어의 임계값은 Appendix A 에 태스크별로 명시되어 있습니다.)

### 태스크별 online success rate (Table 3)

| Task Characteristics | Task | Pi0.5 | OpenVLA | 3D Diffusion Policy | Diffusion Policy |
|---|---|---|---|---|---|
| Pick-and-Lift | BimanualLiftCarton | 1.00 | 0.60 | 0.90 | 0.94 |
| | BimanualLiftTray | 0.84 | 0.72 | 0.56 | 0.60 |
| | GraspBleach | 0.10 | 0.06 | 0.32 | 0.10 |
| | GraspCup | 0.16 | 0.08 | 0.22 | 0.50 |
| | GraspKettle | 0.58 | 0.16 | 0.80 | 0.90 |
| | GraspPan | 0.06 | 0.02 | 0.16 | 0.52 |
| | RetrieveCup | 0.02 | 0.02 | 0.06 | 0.04 |
| Articulated | OpenFaucet | 0.84 | 0.36 | 0.76 | 0.28 |
| | OpenFlatFolder | 0.00 | 0.00 | 0.18 | 0.16 |
| | OpenLaptop | 0.04 | 0.02 | 0.02 | 0.10 |
| | OpenStapler | 0.86 | 0.92 | 0.84 | 0.86 |
| | SlideUtilityKnife | 0.00 | 0.00 | 0.00 | 0.00 |
| | SqueezeScissors | 0.36 | 0.22 | 0.20 | 0.00 |
| Tool Use | FunctionalHammerStrike | 0.22 | 0.18 | 0.26 | 0.00 |
| | FunctionalPourCan | 0.04 | 0.10 | 0.14 | 0.38 |
| | FunctionalPourMug | 0.52 | 0.16 | 0.64 | 0.26 |
| Precision | InsertPen | 0.06 | 0.00 | 0.08 | 0.00 |
| | PushSmallSphereObstacleSlope | 0.82 | 0.08 | 0.28 | 0.36 |
| | PushT | 0.00 | 0.00 | 0.00 | 0.00 |
| **Mean** | | **0.34** | **0.19** | **0.34** | **0.32** |

> "DP3 ties $`\pi_{0.5}`$ for the highest overall success rate (0.34), ahead of DP (0.32) and OpenVLA (0.19)." (§4.1, Table 3)
(1위와 3위의 차이가 0.02 로, 태스크당 50 에피소드 · 19 태스크 규모에서는 순위 자체가 통계적으로 강하게 분리된다고 보기 어렵습니다. 논문도 "aggregate ranking is close" 라고 인정하며 카테고리별 프로파일 쪽에 무게를 둡니다.)

### 스킬 계열별 판독

> "DP is strongest on Pick-and-Lift (0.51), where a successful grasp pose is largely a function of object appearance, and a 2D image plus low-dimensional state already suffices." (§4.1)
(주의할 점은 이 문장이 DP 를 "2D image plus low-dimensional state" 라고 설명하는데, Appendix B 의 DP 셋업은 명시적으로 "no visual input" 이라는 것입니다. 본문 서술과 부록 셋업이 서로 어긋나므로, DP 의 관측 사양은 재현 시 코드로 확인해야 할 항목입니다.)

> "3D DP leads on Functional Tool Use (0.35), where explicit point-cloud geometry helps localize the tool tip and regulate the pour/strike pose." (§4.1)
(도구 끝점의 위치와 자세가 성공을 좌우하는 계열에서는 명시적 3D 기하가 이득이라는 판독으로, 우리 P2 D8(다중 카메라 공간-기하 grounding) 의 방향과 같은 결의 증거입니다.)

> "$`\pi_{0.5}`$ leads on both Articulated-object Manipulation (0.35) and Precision Contact (0.29), where language conditioning and a flow-matching action expert help disambiguate multi-stage subgoals and contact timing." (§4.1)
(다단계 서브골 분해가 필요한 계열에서 언어 조건 + flow-matching action expert 가 유리하다는 해석입니다. 다만 "flow matching 덕분"과 "3.3B full fine-tuning 덕분"이 이 실험에서는 분리되지 않습니다.)

> "This spread, a different method wins each of the four skill families, motivates DexVerse’s multi-modal observation interface rather than committing to a single sensing paradigm." (§4.1)
(네 스킬 계열에서 승자가 각각 다르다는 것이 이 논문이 관측 인터페이스를 모달리티별 그룹으로 쪼갠 설계 근거입니다. 단일 감각 패러다임에 몰빵하지 말라는 결론은 우리 P2 D10(concat 을 넘는 이종 모달리티 융합) 의 전제와 직접 맞닿습니다.)

### 사전학습 프라이어의 미전이

> "Despite being initialized from web-scale pretrained backbones, the stronger VLA ($`\pi_{0.5}`$ , 0.34) only matches the best from-scratch policy (DP3, 0.34), while OpenVLA (0.19) trails both diffusion baselines." (§4.1, Table 3)
(이 논문에서 가장 도발적인 수치입니다. 웹 스케일 사전학습이 dexterous 접촉 제어에서 from-scratch 대비 우위를 만들지 못했습니다.)

> "We attribute this to the gap between the pretraining distribution and the target embodiment: the priors carried by these backbones come from web images and low-DoF action spaces, which transfer to perception but not to the high-DoF multifinger control manifold of DexVerse." (§4.1)
(저자들의 해석은 "지각은 전이되지만 고DoF 다지 제어 manifold 는 전이되지 않는다" 입니다. 이 진단이 맞다면 사전학습 코퍼스의 **행동 공간 구성**(P4 D22) 이 lineage 선택(P4 D19) 만큼이나 결정적이라는 뜻이 됩니다. 다만 아래 한계에서 보듯 $`\pi_{0.5}`$ 의 proprio 차단과 OpenVLA 의 LoRA-only 적응이 이 결론의 교란 요인입니다.)

### 정밀 접촉의 전면 붕괴

> "Tight-tolerance tasks collapse for every method: PushT is 0.00 for all four policies, and InsertPen, SlideUtilityKnife, and OpenLaptop stay at or near zero everywhere." (§4.1, Table 3)
(`SlideUtilityKnife` 와 `PushT` 는 네 정책 모두 정확히 0.00 이고, `InsertPen` 은 최대 0.08, `OpenLaptop` 은 최대 0.10 입니다. Appendix A 임계값과 대조하면 이유가 선명합니다 — `PushT` 는 목표 footprint 90% 겹침, `InsertPen` 은 홀더 개구부 중심 0.038 m 이내에 더해 rim 아래 0.03 m 이상 밀어넣기, `SlideUtilityKnife` 는 blade 를 전체 이동 거리의 40% 이상 밀어내면서 칼 전체를 들어올리기입니다.)

> "These tasks demand sustained force regulation and sub-centimeter alignment that behavior cloning without explicit force feedback or closed-loop contact correction cannot yet provide, and they constitute the principal headroom that DexVerse exposes for future imitation-learning research." (§4.1)
(저자들이 직접 "명시적 힘 피드백 없는 behavior cloning" 을 실패 원인으로 지목했습니다. 이는 우리 Identity 의 System0 논지 — 접촉 유지·slip 억제는 정책 루프보다 빠른 저수준 안정화가 필요한 영역 — 와 정면으로 겹치는 외부 증거입니다. 흥미로운 것은 이 벤치마크가 `contact` 관측 그룹으로 fingertip 접촉력을 이미 제공하는데도, 그 그룹을 쓴 베이스라인이 하나도 없다는 점입니다.)

---

## ⚖️ 한계

- **시각 변이가 논문에서 한 번도 평가되지 않았습니다.** 재질·조명·skybox·노출·색온도·카메라 시점 randomization 은 §3.3 의 핵심 셀링 포인트이고 Table 1 의 비교 우위 항목이지만, Table 3 은 시각 변이 조건별 성공률을 하나도 보고하지 않습니다. 게다가 최고 성적을 낸 두 정책 중 DP 는 시각 입력이 없고 DP3 는 RGB 가 없으므로, 이 벤치마크가 실제로 visuomotor 강건성을 가르는지에 대한 증거는 현재 0입니다. "visuomotor generalization 을 평가한다"는 주장과 실측 사이의 간극이 이 논문의 가장 큰 미완성 지점입니다.
- **multi-embodiment 일반화도 평가되지 않았고, 데이터가 그것을 허용하지도 않습니다.** hand 6종 중 Shadow Hand 외 5종은 태스크당 데모가 **1개**입니다. 태스크당 1 데모로는 학습도 cross-embodiment 평가도 성립하지 않으므로, 3×6 조합 지원은 현재 "환경이 인스턴스화된다"는 의미이지 "그 위에서 정책을 비교했다"는 의미가 아닙니다. 임베디먼트 전이는 논문이 스스로 future work 로 미룹니다.
- **베이스라인 비교가 여러 축에서 통제되지 않았습니다.** $`\pi_{0.5}`$ 는 3.3B full fine-tuning · 32 GPU · batch 512 인 반면 OpenVLA 는 LoRA rank 32 · base 동결 · 8 GPU · per-GPU batch 8 입니다. 적응 파라미터 수, 옵티마이저 예산, 학습 step 이 모두 다른 상태에서 "OpenVLA 가 뒤진다"를 사전학습 프라이어의 문제로 귀속하기는 어렵습니다. 데이터와 종료 조건만 통제된 비교입니다.
- **$`\pi_{0.5}`$ 의 proprioception 차단은 finding 1 을 심각하게 교란합니다.** 28/56차원 관절을 제어하면서 자기 관절 상태를 보지 못하는 정책과, 오직 관절 상태만 보는 DP 를 같은 표에서 비교한 뒤 "웹 스케일 사전학습이 도움이 안 된다"고 결론짓는 구조입니다. 사전학습 프라이어의 미전이일 수도 있지만, 고DoF 손에서 proprio 를 끈 관측 설계의 결과일 수도 있으며 이 실험은 둘을 구분하지 못합니다.
- **`contact` 관측 그룹이 제공되지만 활용되지 않았습니다.** 논문은 결론에서 "explicit force feedback 부재"를 실패 원인으로 지목하는데, 정작 자신이 제공하는 fingertip 3D 접촉력 그룹을 쓴 베이스라인을 하나도 돌리지 않았습니다. 접촉력 관측을 켠 정책이 정밀 태스크에서 얼마나 회복되는지는 이 논문이 답할 수 있었으나 답하지 않은 질문이고, 벤치마크 사용자 입장에서는 가장 먼저 돌려볼 실험입니다.
- **100 이라는 태스크 수가 상호작용 다양성과 같지 않습니다.** multi-goal 39개는 기존 단일 목표 태스크의 조합이므로, 물리적으로 구별되는 상호작용 패턴은 61개에 가깝습니다. 평가는 그중 19개에서만 이뤄졌고, long-horizon 5개와 bimanual 5개 중 평가에 포함된 것은 bimanual 2개(`BimanualLiftCarton`, `BimanualLiftTray`)뿐입니다. 즉 벤치마크의 가장 어려운 부분(long-horizon)은 베이스라인 수치가 전혀 없습니다.
- **sim-only 이며 real-robot transfer 는 미검증입니다.** 저자들도 이를 명시합니다.
  > "Future extensions will study real-robot transfer, expand demonstrations across more embodiments and task families, and provide broader standardization for cross-task and cross-embodiment evaluation." (§5)
  (Isaac Sim PhysX 의 점접촉 모델과 실제 fingertip 점탄성 변형 사이의 간극은 우리가 이미 추적 중인 문제이며, 정밀 접촉 태스크의 성공률이 시뮬레이터 접촉 파라미터에 얼마나 민감한지는 보고되지 않았습니다.)
- **부록 서술에 중복·불일치가 있습니다.** Appendix B 의 Diffusion Policy 문단은 마지막 두 문장이 앞 내용을 그대로 반복하고, 본문 §4.1 은 DP 를 "2D image plus low-dimensional state" 로 서술하는 반면 Appendix B 는 "no visual input" 이라고 명시합니다. 재현 시 DP 관측 사양은 논문 텍스트만으로 확정할 수 없습니다.

---

## ♻️ 재현성

- **코드** — 본문·부록 어디에도 코드 저장소 URL 이 명시되어 있지 않습니다. 초록에 제시된 것은 [프로젝트 페이지](https://ycyao216.github.io/DexVerse.site/) 하나뿐이며, 본 실행 환경의 네트워크 정책이 해당 호스트를 차단해 공개 범위(환경 코드 / 데이터셋 / 학습 스크립트)를 확인하지 못했습니다. 저장소 존재 여부는 사람이 직접 확인해야 합니다.
- **데이터** — 3,180개 데모 공개를 명시합니다. action-state 포맷 + replay 유틸리티 구조라 배포 용량이 작고, 관측 프리셋을 바꿔도 데이터셋 재수집이 필요 없습니다. 다만 공개 위치·라이선스는 본문에 없습니다.
- **논문 라이선스** — arXiv HTML 상단에 `License: CC BY 4.0` 로 표기되어 있습니다. 코드/데이터 라이선스는 별도이며 미명시입니다 (P0 D27 의 라이선스 바를 적용하려면 확인 필요).
- **시뮬레이터 의존성** — Isaac Lab / Isaac Sim (manager-based env, CloudXR XR teleop 인터페이스) 에 강하게 결합되어 있습니다. 우리 스택의 주 시뮬레이터가 이미 Isaac Sim + Isaac Lab 이라는 점은 진입 비용 측면에서 유리합니다.
- **하드웨어** — 데이터 수집에 Apple Vision Pro 필요. 베이스라인 재학습에는 $`\pi_{0.5}`$ 32× H20, OpenVLA 8× H20 이 보고되었고 DP / DP3 의 학습 하드웨어는 명시되지 않았습니다.
- **asset 출처** — PartNet-Mobility, ManiTwin, Isaac Lab/Isaac Sim, AutoBio, Synthesis, Poly Haven HDR 100장, 그리고 Meshy 생성 메시. 각 소스의 재배포 라이선스가 혼재하므로 asset 단위 라이선스 확인이 필요합니다.
- **미보고 항목** — 시드, 에피소드 최대 길이, 제어 주파수, 성공률의 분산/신뢰구간, 시각 변이 활성화 시의 성능이 모두 보고되지 않았습니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P0(VLA Datasets & Benchmarks) — 주 pillar.**
  - `D26`(benchmark/eval scouting scope) 의 정확한 사냥감입니다. dexterous + contact-rich 시뮬레이션 벤치마크이고, 우리가 이미 핀으로 잡고 있는 ManiSkill 3 와 직접 경쟁하는 위치입니다. 특히 **Isaac Lab 기반**이라 우리 시뮬레이션 스택(P3 System0 학습용)과 같은 엔진을 씁니다.
  - `D25`(tactile / force / torque 데이터 스카우팅) — `contact` 관측 그룹이 fingertip 3D 접촉력을 제공합니다. 실측 tactile 코퍼스는 아니지만, 접촉력 라벨이 붙은 시뮬레이션 데이터를 임의 규모로 생성할 수 있는 환경이라는 점에서 D25 의 "희소성" 문제에 부분적으로 닿습니다.
  - `D24`(우선 데이터 축) 기준으로는 **down-weight** 대상입니다. 3,180개 데모는 egocentric 사람 영상이 아니라 시뮬레이션 텔레오퍼레이션 로봇 궤적입니다. 다만 수집 경로가 Vision Pro 핸드 트래킹이라 사람 손 동작이 원천이라는 점은 EgoDex 계열과 접점이 있습니다.
  - `D27`(라이선스 / 사용성 바) — 코드·데이터 라이선스 미명시라 현재로선 판정 보류입니다.
- **P2(Structured Multimodal Observation Fusion).**
  - `D11`(proprio-tactile-force 토큰 구성) — fingertip 별 3D 접촉력이 base frame 기준으로 그룹화되어 나온다는 것은 per-finger 접촉 귀속을 유지한 토큰 구성을 시뮬레이션에서 검증할 수 있다는 뜻입니다. 우리 D11 의 "10 finger + 2 palm 토큰" 구성을 실제 하드웨어 이전에 sim 에서 ablation 할 수 있는 첫 공개 환경 후보입니다.
  - `D8`(다중 카메라 공간-기하 grounding) — `3view_rgb` / `3view_pointcloud` 프리셋이 multiview 관측을 지원하며, DP3 가 Tool Use 에서 우위(0.35)를 보인 것은 명시적 3D 기하의 이득에 대한 약한 지지 증거입니다.
  - `D10`(concat 을 넘는 이종 모달리티 융합) — "네 스킬 계열에서 승자가 각각 다르다"는 결과는 단일 감각 패러다임 몰빵을 반박하는 외부 증거이며, D10 의 전제를 지지합니다.
- **P4(Pretraining for Data-Efficient Adaptation).**
  - `D19`(VLM backbone lineage & adaptation range) 에 대한 **긴장(tension) 증거**입니다. 인터넷 스케일 사전학습 backbone 이 from-scratch diffusion policy 를 못 넘었다는 결과는 lineage 선택의 가치에 의문을 던집니다. 다만 위 ⚖️ 에서 정리한 교란(proprio 차단, LoRA vs full FT, 학습 예산 불균형) 때문에 결정적 반례로 승격시키기에는 증거가 약합니다.
  - `D22`(사전학습 데이터 구성 — egocentric vs mixed, **OPEN**) — 저자들의 진단("웹 이미지와 저DoF 행동 공간의 프라이어는 지각에는 전이되지만 고DoF 다지 제어 manifold 에는 전이되지 않는다")은 D22 가 열어둔 질문에 "행동 공간의 DoF 일치가 코퍼스 크기보다 중요할 수 있다"는 가설을 하나 더 얹습니다.
- **P3(Hand-level System0 Module).**
  - `D13`(System0 역할 & 운용 영역) 을 지지하는 외부 증거입니다. "sustained force regulation and sub-centimeter alignment 를 명시적 힘 피드백 없는 behavior cloning 이 제공하지 못한다"는 저자 진술은, 접촉 유지 구간에 별도 저수준 안정화 층이 필요하다는 우리 논지와 같은 진단입니다.
  - `D15`(System0 입력 모달리티 — tactile + 관절 상태, vision 배제) — `state` 프리셋(`policy, proprio, contact, state, goal`)이 정확히 vision 없는 접촉·고유수용 관측 조합이라, System0 입력 사양의 sim 프로토타이핑에 그대로 쓸 수 있습니다. 단 이 프리셋의 history length 가 0 이므로 D15 가 요구하는 접촉 상태 이력은 그룹을 직접 조합해 확보해야 합니다.
  - `D17`(System0 RL 정책 스펙) — Table 1 이 DexVerse 의 parallel RL 환경 지원을 ✓ 로 표기하지만, 본문은 RL 학습 결과를 하나도 보고하지 않고 보상 항도 "optional reward terms" 로만 언급합니다. GPU 병렬 RL 규모(8k–16k env)에서의 실측 처리량은 미확인입니다.
- **P1(Heterogeneous Body/Hand Action Expert)** — 아키텍처 기여가 없으므로 직접적인 결정 이동 근거는 없습니다. 다만 텔레오퍼레이션이 손목 pose(IK) 와 손가락 관절(retargeting) 을 분리해 라벨을 만든다는 점은 우리 `D2`(Body 출력 = 양손목/툴 플랜지 pose) / `D3`(Hand 출력 = 손가락 관절 명령) 의 출력 공간과 정확히 정합합니다. 데이터 소비 관점의 정합성이지, 결정을 바꾸는 증거는 아닙니다.
- **P5(World Model)** — 이 논문은 world model 을 다루지 않습니다. `D28`–`D32` 와의 연결은 없습니다.
- **Identity 관계** — 지지 쪽입니다. (1) "정밀 접촉은 힘 피드백 없는 BC 로 안 된다"는 결과는 System0 논지를 지지하고, (2) "단일 감각 패러다임이 지배하지 않는다"는 결과는 구조적 다중모달 융합 논지를 지지합니다. 반면 (3) "웹 스케일 사전학습 프라이어가 우위를 못 만든다"는 결과는 π lineage 를 기반으로 삼는 우리 P4 전제와 긴장 관계에 있습니다 — 다만 교란 요인 때문에 현 시점에서는 falsifier 가 아니라 관찰 항목입니다.
- **경쟁자 함의** — P0 §5 핀 중 **ManiSkill 3** 와 직접 경쟁합니다. ManiSkill 3 는 SAPIEN 기반 고처리량 범용 벤치마크이고 DexVerse 는 Isaac Lab 기반 dexterity 특화 + 데모 동봉 + 우리 하드웨어(Sharpa Wave) 포함입니다. 축이 다르므로 교체보다는 병존이 맞습니다.

---

## ✨ 핀 논문 대비 델타

- **vs. ManiSkill 3 (P0 핀, sim 벤치마크)** — ManiSkill 3 는 dexterous hand 를 포함한 범용 고처리량 SAPIEN 벤치마크입니다. DexVerse 의 진짜 델타는 태스크 수가 아니라 (a) **Isaac Lab manager-based 인터페이스 기반**이라 우리 System0 RL 스택과 엔진이 같다는 점, (b) **Sharpa Wave 를 포함한 6종 hand** 지원, (c) fingertip 3D 접촉력을 별도 관측 그룹으로 노출한다는 점입니다. 순수 태스크 다양성만 보면 두 벤치마크는 겹칩니다.
- **vs. vla-eval (P0 핀, eval harness)** — 층이 다릅니다. vla-eval 은 모델과 벤치마크를 연결하는 어댑터 허브(`O(N+M)` 통합)이고, DexVerse 는 그 허브가 통합할 *벤치마크 하나*입니다. 경쟁이 아니라 상보 관계이며, 자연스러운 후속은 DexVerse 를 vla-eval 하니스에 붙이는 것입니다.
- **vs. RH20T (P0 핀, F/T 코퍼스)** — RH20T 는 실제 로봇의 6축 손목 F/T 를 담은 희소한 실측 접촉 코퍼스입니다. DexVerse 의 접촉력은 시뮬레이션 값이고 손목이 아니라 fingertip 단위입니다. 실측 대체재는 아니지만, per-finger 귀속이라는 축에서는 RH20T 보다 우리 D11 사양에 더 가깝습니다.
- **vs. DexMimicGen (P0 방법론 base)** — DexMimicGen 은 소수 사람 시연에서 bimanual dexterous 데모를 *증강*하는 방법입니다. DexVerse 는 증강 방법을 제안하지 않고 텔레오퍼레이션 원본을 직접 모읍니다. 두 방향은 결합 가능하며, DexVerse 의 태스크당 50 데모라는 얇은 규모를 메우는 자연스러운 보완재입니다.
- **vs. EgoDex (P0 최상위 핀, egocentric)** — 축이 다릅니다. EgoDex 는 829시간 사람 egocentric 손 추적이고 DexVerse 는 시뮬레이션 로봇 궤적입니다. 겹치는 지점은 수집 장치(Vision Pro 핸드 트래킹)뿐이며, D24 의 우선 축 기준으로 DexVerse 는 보조 자원입니다.
- **진정으로 새로운 것 한 줄** — "동일 태스크 정의를 여러 arm-hand 조합에 재사용 가능한 config 축으로 분리하고, fingertip 접촉력을 1급 관측 그룹으로 노출한 Isaac Lab 벤치마크" 가 이 논문의 유일무이한 부분입니다. 100 태스크·3,180 데모·베이스라인 평가는 규모의 문제이지 새로움이 아닙니다.

---

## ⚙️ 의사결정 함의

이 논문이 맞다면 우리 파이프라인에서 다음이 바뀝니다.

- **평가 하네스에 DexVerse 를 후보로 등록** — 우리 시뮬레이터가 이미 Isaac Sim + Isaac Lab 이므로 도입 비용이 ManiSkill 3 보다 낮습니다. 구체적 진입점: `state` 프리셋(`policy, proprio, contact, state, goal`) 을 System0 관측 사양의 sim 프로토타입으로, `3view_pointcloud` 프리셋을 P2 D8 다중 뷰 grounding ablation 의 관측 축으로 씁니다.
- **`contact` 관측 그룹을 P2 D11 토큰 구성의 sim 검증 축으로 채택** — 현재 D11 은 "per-finger proprio-tactile binding, 10 finger + 2 palm 토큰, swappable sensor head + 공통 토큰 포맷"입니다. DexVerse 의 fingertip 3D 접촉력 벡터(base frame)는 이 공통 토큰 포맷의 *시뮬레이션 측 sensor head* 하나로 그대로 매핑됩니다. 즉 Sharpa Deform Map 이 준비되기 전에 토큰 스키마와 aggregation(D12 의 finger/palm self-attention) 을 sim 에서 먼저 굳힐 수 있습니다.
- **정밀 접촉 태스크를 falsifier 후보로 승격** — `InsertPen`(개구부 중심 0.038 m 이내 + rim 아래 0.03 m), `PushT`(목표 footprint 90% 겹침), `SlideUtilityKnife`(blade 이동 40% + 들어올리기), `NutThread`(볼트 축 0.0025 m 이내) 가 네 정책 모두 0 에 가까운 구간입니다. 우리 아키텍처(Body/Hand 분리 + 구조적 관측 융합 + System0 게이팅) 가 의미 있는 우위를 주장하려면, 정확히 이 구간에서 0 을 벗어나는 것이 가장 값싼 증명입니다. Phase 1 in-hand rotation 다음의 정량 지표 후보로 `InsertPen` 성공률 > 0.10 을 잡아둘 만합니다.
- **`contact` 그룹 on/off ablation 을 우리 쪽에서 실행** — 논문이 남긴 공백이자 우리 논지의 직접 검증입니다. 동일 정책·동일 데이터에서 `state` 프리셋(contact 포함) vs `proprio`+`state`(contact 제외) 를 비교해, 정밀 접촉 태스크 성공률의 델타를 잽니다. 이 델타가 유의하면 P2 D11 의 접촉 토큰 투자와 P3 D15 의 tactile 중심 입력 사양이 동시에 지지받습니다.
- **P4 D19 의 "freeze + action expert only" 기본값 재점검 트리거는 아직 당기지 않습니다** — DexVerse 결과는 사전학습 프라이어의 가치에 의문을 던지지만, $`\pi_{0.5}`$ 의 proprio 차단이라는 치명적 교란이 있어 결정을 움직일 근거가 되지 못합니다. 대신 "고DoF 손에서 proprio 를 포함한 $`\pi_{0.5}`$ 재평가" 를 관찰 항목으로 등록합니다.
- **데이터 저장 포맷 차용** — action-state 저장 + 로컬 replay 는 우리 sim 데이터 수집에도 그대로 적용 가능한 설계입니다. 관측 프리셋을 바꿔가며 ablation 하는 우리 계획(P2 의 모달리티 조합 탐색)에서, 관측을 굽지 않는 포맷은 재수집 비용을 0 으로 만듭니다.

---

## ⚠️ 먼저 검증할 실패 모드

싼 순서대로 나열합니다.

1. **(가장 쌈, 반나절) 코드·데이터가 실제로 공개되었는가** — 본문에 저장소 URL 이 없고 프로젝트 페이지는 본 환경에서 접근 차단되었습니다. 저장소·데이터 공개 여부와 라이선스(P0 D27 바)를 먼저 확인하지 않으면 아래 전부가 무의미합니다. 미공개면 이 논문의 실무 가치는 "정밀 접촉이 미해결이라는 수치 근거" 하나로 축소됩니다.
2. **(쌈, 1일) Sharpa Wave 모델의 충실도** — 지원 목록에 이름이 있다는 것과 우리 실물 hand 의 22-DOF 운동학·관절 한계·손끝 형상을 반영한다는 것은 다릅니다. URDF/USD 의 DOF 수와 관절 범위를 우리 스펙과 대조합니다. 불일치하면 "Sharpa 지원"은 마케팅 라벨이고 우리 입장에서의 최대 장점이 사라집니다.
3. **(쌈, 1일) `contact` 그룹의 물리적 의미** — PhysX 의 점접촉 기반 접촉력이 실제 fingertip 점탄성 변형과 어떤 관계인지 확인합니다. 접촉력이 solver 스텝마다 크게 튀거나(스파이크) 접촉 판정이 이산적이면, 그 위에서 학습한 접촉 토큰 스키마는 실물 Deform Map 으로 전이되지 않습니다. 우리가 이미 추적 중인 PhysX-실물 간극(Contact-Aware Neural Dynamics 계열) 이 그대로 재현될 위험입니다.
4. **(중간, 2–3일) 시각 변이의 실제 난이도** — 논문이 시각 변이 조건에서의 성능을 하나도 보고하지 않았으므로, randomization 이 실제로 정책을 무너뜨리는지 우리가 직접 재야 합니다. skybox·재질 라이브러리가 도메인 randomization 으로 유효한 범위를 갖는지, 아니면 tabletop 근접 영역이 사실상 고정이라 시각 변이가 성능에 무영향인지가 갈립니다. 후자면 P2 강건성 평가축으로서의 가치가 없습니다.
5. **(중간, 2–3일) 병렬 처리량** — Table 1 은 parallel RL 환경 지원을 ✓ 로 표시하지만 본문에 RL 결과도 처리량 수치도 없습니다. P3 System0 은 8k–16k env 규모의 PPO 를 전제로 하므로, dexterous hand + 접촉 센서 + 카메라를 켠 상태에서 실제 env/step 처리량을 측정해야 합니다. 렌더링을 켠 채로 8k env 가 안 나오면 System0 학습 환경으로는 쓸 수 없고 평가 전용으로만 남습니다.
6. **(중간) 성공률 분산** — 태스크당 50 에피소드에서 0.34 vs 0.32 는 구분되지 않을 가능성이 큽니다. 시드를 바꿔 최소 3회 반복해 표준편차를 확인하기 전에는 Table 3 의 순위를 근거로 어떤 결정도 움직이지 않습니다.
7. **(비쌈, 1–2주) $`\pi_{0.5}`$ proprio 포함 재평가** — finding 1 의 교란을 제거하는 실험입니다. proprioceptive state 를 켜고 $`\pi_{0.5}`$ 를 다시 학습해 0.34 가 어디까지 오르는지 봅니다. 크게 오르면 "사전학습 프라이어 미전이" 서사는 무너지고 우리 P4 전제는 유지됩니다. 비용이 크므로 1–6번이 모두 통과한 뒤에만 착수합니다.
8. **(전이 위험, 상시) sim-only 결론의 실물 전이** — 이 벤치마크에서 얻은 모든 순위와 실패 패턴은 Isaac Sim 접촉 모델 위의 결과입니다. 특히 sub-centimeter 정렬 실패는 실물에서 더 나빠질 수도, (센서 노이즈가 오히려 탐색을 도와) 다르게 나타날 수도 있습니다. 어떤 아키텍처 결정도 이 벤치마크 단독 증거로 굳히지 않습니다.

---

## 💡 컨텍스트 제안

- **P0 §5 핀 교체 제안 — 없음 (추적만).** DexVerse 는 ManiSkill 3 와 축이 다르므로 교체 대상이 아니고, 8핀 하드캡을 고려하면 즉시 승격도 이릅니다. 다만 위 ⚠️ 1–2번(코드 공개 + Sharpa 충실도)이 통과하면 **P0 §5 "Methodology base (non-pinned)" 표에 추가**할 것을 제안합니다 — 우리 하드웨어가 들어간 유일한 공개 dexterous 벤치마크가 되기 때문입니다.
- **P0 `D26`(benchmark/eval scouting scope) 문구 보강 제안** — 현재 v1 은 "sim(ManiSkill / Isaac Lab / Robocasa)과 real(RoboArena-class)" 로 엔진을 나열합니다. DexVerse 사례를 보면 벤치마크 선별에서 실질적으로 중요한 축은 엔진 이름이 아니라 **(a) 우리 hand 하드웨어 모델 포함 여부, (b) 접촉/힘 관측의 1급 노출 여부** 였습니다. 이 두 축을 D26 의 선별 기준으로 명시할지 사람 판단을 요청합니다.
- **P3 `D15`(System0 입력 모달리티) 에 sim 프로토타입 경로 기록 제안** — D15 는 tactile + 관절 상태 + 토크 + 접촉 이력을 vision 없이 쓰는 사양이고, DexVerse 의 `state` 프리셋이 거의 동일한 조합(vision 제외, contact 포함)을 이미 제공합니다. 실물 Sharpa 이전 단계의 검증 경로로 이 환경을 기록해 둘지 제안합니다. 단 프리셋의 history length 가 0 이라 접촉 이력은 그룹 직접 조합이 필요하다는 단서를 함께 남깁니다.
- **P4 `D22`(사전학습 데이터 구성 — OPEN) 에 관찰 항목 추가 제안** — "웹 스케일 프라이어는 지각에는 전이되나 고DoF 다지 제어에는 전이되지 않는다"는 가설을 D22 의 열린 ablation 목록에 관찰 항목으로 덧붙일 것을 제안합니다. 결정을 움직이기에는 교란이 크지만, 코퍼스 구성 논의에서 "행동 공간 DoF 정합"이라는 축을 명시적으로 두는 것은 지금 해둘 만합니다.
- **Decision 이동 / deferred trigger 발동 — 없음.** ⚖️ 에 정리한 교란(시각 변이 미평가, 임베디먼트 전이 미평가, 적응 예산 불균형, proprio 차단) 때문에 이 논문 단독으로 어떤 `D#` 의 v1 을 v2 로 올릴 근거는 되지 못합니다.

---
