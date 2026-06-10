# Paper Analysis — Robots Need More than VLA and World Models

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Robots Need More than VLA and World Models |
| 저자 | Elis Karcini, Faisal Mehrban, Quang Nguyen, Mac Schwager, Arash Ajoundani, César Cadena, Jan Peters, Marco Hutter, Haitham Bou-Ammar (Motoniq.ai · Stanford · IIT · ETH Zurich · TU Darmstadt · UCL) |
| 링크 | [arXiv:2606.06556](https://arxiv.org/abs/2606.06556) |
| 발행일 / 버전 | 2026-06-04 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-09 |
| 관련 Pillar | P4, P3 |
| 태그 | dataset, egocentric-data, sim2real |

> **문서 성격 주의** — 본 논문은 실험·벤치마크가 없는 **position / survey paper** 입니다. 따라서 아래 📊 섹션은 저자가 *인용한* 외부 시스템·데이터셋의 수치를 정리한 것이며, 본 논문 자체의 측정값이 아닙니다. PROBE 의 모든 Pillar Anti-topic 은 "Survey / position papers (read manually, not via agent)" 를 배제하므로, 본 분석은 사람이 직접 지정해 수행한 manual 분석임을 명시합니다.

---

## 🧭 한 줄 요약 (TL;DR)

생성주의 로봇 지능의 병목은 "정책(policy)을 더 키우는 것"이 아니라, 세상에 넘쳐나는 비정형 행동 데이터(인간 영상·시뮬레이션·상호작용)를 로봇이 학습 가능한 supervision(액션·접촉·물체 상태·태스크 단계·보상)으로 **변환(grounding)** 하는 메커니즘의 부재라고 주장하며, VLA 와 world model 위에 얹어야 할 **네 가지 누락 컴포넌트**(physical data engine, task-preserving retargeting, physics-grounded world model, self-improving deployment loop)를 제시하는 입장 논문입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 일반화 로봇 지능을 "정책 스케일링 문제(더 많은 데모 + 더 큰 VLA = 더 넓은 일반화)"로만 보는 프레이밍이 불완전하다는 것. 핵심 병목은 정책 학습이 아니라, 비정형 물리 경험을 로봇이 쓸 수 있는 supervision 으로 바꾸는 메커니즘의 부재입니다.
- **기존 접근의 한계** — 현재 파이프라인은 여전히 **robot-data-centric** 입니다. 로봇 데모를 모으고, 태스크/언어 라벨을 붙이고, 정책을 학습하고, 하드웨어에서 평가하는 루프인데, 텍스트 코퍼스와 달리 모든 trajectory 는 물리적으로 실행 가능해야 하고 embodiment 에 묶여 있어 비싸고 확장이 어렵습니다.
- **본 논문의 가설** — 미래 파이프라인은 **grounding-centric** 이어야 합니다. 넓은 물리 경험(인간 모션·인터넷 영상·시뮬·촉각·언어)에서 출발해 grounding 메커니즘을 통과시켜 로봇이 쓸 수 있는 액션·접촉·물체 상태·태스크 단계·보상을 산출해야 한다는 것입니다.
- **VLA 의 위치 재정의** — VLA 가 불필요하다는 주장이 아니라, VLA 는 더 큰 physical-intelligence 스택의 **한 레이어(policy interface)** 일 뿐이며 상류의 데이터·embodiment·dynamics·reward·deployment grounding 에 의존한다는 재배치입니다.
- **왜 지금 중요한가** — 로봇이 "foundation-model 순간"에 진입했지만 아직 "인터넷(= 자연 디지털화된 풍부한 supervision)"이 없습니다. 사용 가능한 로봇 supervision 의 총량은 세상에 이미 존재하는 물리 행동량에 비해 극히 작아, 이 비대칭을 해소할 메커니즘이 다음 세대의 결정 요인입니다.

---

## 🧩 핵심 기여

- 로봇 학습 진척을 모델 패밀리/데이터셋/알고리즘 트렌드가 아니라 **각 연구 라인이 드러내는 "supervision 병목"** 기준으로 재조직하는 분류 관점을 제시합니다(robot-native = 강한 grounding, video = 약한 grounding, sim/world-model = 생성된 경험의 물리 보존 문제).
- 다음 세대 로봇 지능에 필요한 **네 가지 누락 컴포넌트**를 정의합니다: ① 비정형 행동을 구조화 신호로 바꾸는 physical data engine(embodied autolabelling), ② embodiment 간 task-preserving retargeting, ③ consequence 예측용 physics-grounded world model, ④ 배포 결과를 supervision 으로 환류하는 self-improving deployment loop.
- 각 컴포넌트를 가벼운 **수식 형식화**로 못박습니다 — 이질적·비동기 episode $`\mathbf{x}`$, 정렬 변수 $`\mathcal{A}`$, 잠재 물리 사건 구조 $`\mathbf{z}_{\zeta}`$, 추론 모델 $`q_{\theta}`$, retargeting $`f_{\psi}`$, world model $`p_{\omega}`$, task-conditioned reward $`\mathbf{r}_{\eta}`$.
- 이 네 컴포넌트가 **닫힌 루프(closed-loop)** 로 서로를 개선한다는 시스템적 주장을 제시합니다 — 다음 로봇 foundation model 은 단일 모놀리식 모델이 아니라 경험을 누적 학습하는 compounding system 이라는 결론.
- robot foundation model · cross-embodiment 데이터셋 · learning-from-video · world model · reward modelling 전반의 최신 문헌을 광범위하게 survey 하고, 일반화 로봇용 **평가 질문 셋**(약한 경험을 supervision 으로 바꿀 수 있는가?)을 재정의합니다.

---

## 🔑 기술 키워드

- **Grounding** — 비정형 물리 경험을 로봇이 학습할 수 있는 변수(액션·접촉·물체 상태·태스크 단계·보상)로 변환하는 작업. 본 논문 전체를 관통하는 핵심 개념이며, 저자는 병목이 "데이터 부족"이 아니라 "grounding 메커니즘 부재"라고 봅니다.
- **Robot-native supervision** — 이미 로봇 학습 좌표계(특정 embodiment 의 관측-액션 쌍, 태스크 라벨, 보상)로 표현된 경험. 강력하지만 그 강함이 곧 한계.
- **Embodied autolabelling** — 수동 주석 없이 물리 센싱·시간 구조·world knowledge 로 행동에서 로봇 관련 라벨(접촉 사건·물체 상태 전이·태스크 단계·성공/실패)을 자동 추론하는 과정.
- **Physical data engine** — 이질적·비동기 멀티모달 경험을 정렬된 잠재 물리 사건 시퀀스로 매핑하는 추론 모델 $`q_{\theta}`$. 단순 perception 모델이 아니라 정렬·분절·상태추정·접촉추론·보상 grounding 을 동시 해결.
- **Task-preserving retargeting** — 인간/잠재 액션을 다른 로봇 body 로 옮길 때 관절 궤적이 아니라 **태스크 관련 물리 효과** $`\Delta_{\mathbf{g}}`$ 를 보존하도록 매핑하는 문제.
- **Latent action** — 영상 transition 을 설명하는, embodiment 에 아직 묶이지 않은 행동 유사 코드 $`\mathbf{z}_{1:\mathsf{T}}`$ / $`\mathbf{u}_{\zeta}`$. embodiment-conditioned decoder 를 통과해야 비로소 로봇 명령이 됨.
- **Physics-grounded world model** — 픽셀의 그럴듯함이 아니라 기하·접촉·힘·제약·물성 같은 **행동의 물리적 결과**를 예측하는 모델 $`p_{\omega}`$. 결과(consequence) 예측이 핵심.
- **Consequence prediction** — 주어진 상태·목표·액션에서 다음 물리 상태를 예측하는 것. "미래가 사실적으로 보이는가"가 아니라 "성공/실패를 결정하는 물리 결과를 보존하는가"가 목표.
- **Task-conditioned reward** — 보상을 상태에 붙은 스칼라가 아니라 **목표 하의 물리적 진척 해석** $`\mathbf{r}_{\eta}(\mathbf{s}_{\zeta},\mathbf{g},\phi_{\zeta})`$ 로 정의. 같은 상태도 목표에 따라 성공/실패/무관이 달라짐.
- **Self-improving deployment loop** — 모든 배포 rollout(성공·실패·인간 교정)을 라벨링된 물리 episode 로 만들어 data engine 으로 환류, 정책·보상·world model·retargeting 을 갱신하는 compounding 루프.

---

## 🔬 방법론

> 본 논문은 알고리즘을 구현/학습하지 않는 position paper 이므로, 여기서 "방법론"은 저자가 제시하는 **연구 어젠다(네 컴포넌트)와 그 형식화**를 가리킵니다. 학습 셋업·하이퍼파라미터·손실 함수는 존재하지 않으며, 형식화는 "어떤 변수를 추론/보존해야 하는가"를 못박는 수준입니다.

### 직관

저자의 출발점은 단순한 비대칭입니다. 텍스트와 이미지는 풍부하고 자연스럽게 디지털화되어 있으며 인간이 만든 supervision 이 빽빽하게 붙어 있습니다. 반면 물리 상호작용 데이터는 세상에 넘쳐나지만(인간 데모·공장 작업·가사 활동·시뮬 rollout) 대부분 로봇이 **직접 쓸 수 없는** 형태입니다 — 무슨 태스크인지, 물체가 어떻게 움직이는지, 언제 접촉이 일어나는지는 보이지만, embodiment 별 액션 라벨·힘 신호·태스크 의미·보상 구조가 없기 때문입니다.

따라서 저자는 "로봇 데이터를 더 모으자"가 아니라 "넓은 물리 경험을 로봇이 쓸 수 있게 만들자"로 질문을 바꿉니다. 오늘의 파이프라인은 데이터가 이미 정책에 편리하게 가공된 *뒤에* 학습을 시작합니다(관측-액션 쌍, 분절된 데모, 명시된 성공 조건). 미래 시스템은 거꾸로 더 약하고 지저분한 소스(인간 모션·인터넷 영상·wearable 센싱·촉각·실패 trace)에서 이 변수들을 **회복(recover)** 해야 합니다.

이 회복 작업을 네 개의 인터페이스로 나눕니다. 무슨 일이 일어났는지를 라벨로 복원하는 **data engine**, 그 효과를 다른 몸으로 옮기는 **retargeting**, 후보 액션이 무엇을 일으킬지 예측하는 **world model**, 그리고 그 결과가 유용했는지를 목표 기준으로 해석해 다시 데이터로 만드는 **deployment loop**. 핵심 메시지는 이 넷이 feed-forward 가 아니라 서로를 개선하는 닫힌 루프라는 점이며, VLA 는 이 스택의 한 레이어(정책 인터페이스)로 재배치됩니다.

> "Importantly, our argument is not that VLA models are unimportant. Rather, VLAs should be understood as one layer in a larger physical-intelligence stack: a policy interface that depends on upstream grounding of data, embodiment, dynamics, rewards, and deployment feedback." (§1)
(이 문장이 논문의 설계 의도를 못박습니다 — VLA 무용론이 아니라, VLA 의 효용이 상류 grounding 의 품질에 종속된다는 "레이어 재배치" 선언입니다. PROBE 의 Identity 와 정면으로 맞닿는 지점이므로 아래 (B) 에서 다시 다룹니다.)

### grounding-centric 파이프라인 (아키텍처)

저자는 오늘의 파이프라인(robot-data-centric)과 제안하는 파이프라인(grounding-centric)을 대조합니다.

> "Today's pipeline is largely robot-data-centric: collect robot demonstrations, attach task or language labels, train a policy, evaluate on hardware, and repeat. We argue that the future pipeline must instead be grounding-centric: start from broad physical experience, e.g., human motion, internet video, robot interaction, simulation, tactile sensing, and language and pass it through grounding mechanisms that produce robot-usable actions, contacts, object states, task phases, goals, and rewards." (§1)
(직관적으로 — 입력을 "로봇이 직접 모은 깨끗한 데모"에서 "세상의 거친 물리 경험 전부"로 넓히고, 그 사이에 grounding 레이어를 끼워 로봇 사용 가능 변수로 정제한다는 것입니다. 데이터 수집의 단위 비용을 낮추는 게 아니라, 데이터 소스의 모집단 자체를 바꾸려는 시도입니다.)

![Figure 1 — beyond-VLA grounding pipeline](https://arxiv.org/html/2606.06556/Moto.png)

> "Figure 1 : Next generation robotics will come from advances that go well beyond scaling vision language action (VLA) models." (§3)
(이 그림이 논문의 중심 주장을 시각화합니다 — VLA 스케일링 너머의 네 가지 누락 컴포넌트가 다음 세대 로봇 지능의 원천이라는 closed-loop 스택 개요입니다.)

전체 스택은 다음 네 컴포넌트로 구성되며, 배포가 evaluation 이 아니라 supervision 생성 단계로 환류된다는 점이 핵심입니다.

> "The physical data engine infers what happened; retargeting proposes how a robot could reproduce the relevant physical effect; the world model predicts what would happen if the robot tried." (§3.3)
(세 컴포넌트(+deployment)의 역할 분담을 한 문장으로 요약 — 무엇이 일어났나(data engine) → 어떻게 재현하나(retargeting) → 시도하면 무엇이 일어나나(world model) → 결과가 유용했나(deployment/reward).)

### 컴포넌트 1 — Physical Data Engine / Embodied Autolabelling (§3.1)

raw episode 는 이질적·비동기 멀티모달 스트림입니다. 저자는 episode 를 다음과 같이 표기합니다.

```math
\begin{aligned}
\mathbf{x}=\{ &(v_{i},\tau_{i}^{(v)})_{i=1}^{T_{v}},\ (m_{j},\tau_{j}^{(m)})_{j=1}^{T_{m}},\ (h_{k},\tau_{k}^{h})_{k=1}^{T_{h}}, \\
&(r_{l},\tau_{l}^{(r)})_{l=1}^{T_{r}},\ \texttt{L}\}
\end{aligned}
```

여기서 $`(v_{i},\tau_{i}^{(v)})`$ 는 타임스탬프가 붙은 비디오 프레임, $`(m_{j},\tau_{j}^{m})`$ 는 모션캡처/wearable/body-pose 측정, $`(h_{k},\tau_{k}^{(h)})`$ 는 촉각·힘·접촉·hand-sensor 측정, $`(r_{l},\tau_{l}^{(r)})`$ 는 (있다면) raw 로봇 로그, $`\texttt{L}`$ 은 episode 에 연관된 언어(지시·캡션·태스크 설명·인간 교정)입니다. 모든 episode 가 모든 모달리티를 갖지는 않으므로 일반형은 $`\mathbf{x}\in\mathcal{X}`$.

스트림이 비동기이므로 첫 번째 숨은 객체는 **정렬(alignment)** 입니다. 잠재 사건 타임라인 $`\zeta\in\{1,\dots,Z\}`$ 에 대해 정렬 변수 $`\mathcal{A}`$ 를 도입합니다.

$$\mathcal{A}:\{\tau_{i}^{(v)},\tau_{j}^{(m)},\tau_{k}^{(h)},\tau_{l}^{(r)}\}\rightarrow\{1,\dots,Z\}$$

> "In this sense, temporal alignment is not a preprocessing detail. It is, in fact, part of the embodied autolabelling problem." (§3.1)
(직관 — 어느 비디오 프레임/모션/촉각 스파이크가 동일한 물리 사건(예: $`\zeta=2`$: contact-begins)에 대응하는지를 맞추는 것 자체가 학습 문제의 일부라는 주장입니다. 흔히 전처리로 치부되는 동기화가 라벨링의 본질에 포함됩니다.)

각 사건 $`\zeta`$ 에 대해 로봇 학습에 유용한 변수를 회복합니다.

$$\mathbf{z}_{\zeta}=[\mathbf{s}_{\zeta},\mathbf{c}_{\zeta},\phi_{\zeta},\mathbf{u}_{\zeta},\mathbf{r}_{\zeta}]$$

$`\mathbf{s}_{\zeta}`$ 는 object-centric 물리 상태, $`\mathbf{c}_{\zeta}`$ 는 접촉/상호작용 라벨, $`\phi_{\zeta}`$ 는 태스크 단계, $`\mathbf{u}_{\zeta}`$ 는 잠재 물리 액션(전이 코드), $`\mathbf{r}_{\zeta}`$ 는 task-conditioned 진척/보상 신호입니다. episode 수준에서는 목표 $`\mathbf{g}`$ 와 결과 라벨 $`\mathbf{y}`$(성공/실패/부분성공/위험실행)를 추론하여 전체 숨은 설명은 $`\mathbf{z}=[\mathbf{z}_{1:Z},\mathbf{g},\mathbf{y}]`$. 따라서 data engine 은 추론 모델 $`q_{\theta}(\mathbf{z},\mathcal{A}|\mathbf{x})`$ 로 볼 수 있습니다.

> "Importantly, $`q_{\theta}`$ is not merely a perception model. It must jointly solve temporal alignment, event segmentation, object-state estimation, contact inference, phase recognition, latent-action discovery, reward grounding, and outcome prediction." (§3.1)
(이 문장이 컴포넌트 1 의 난이도를 규정합니다 — 단일 perception 태스크가 아니라 8개 하위문제를 *공동으로* 푸는 구조적 추론이라는 점에서, 본 논문이 말하는 "data engine"은 모델 하나가 아니라 시스템 수준의 요구입니다.)

저자는 컵을 트레이에 올리는 인간 데모 예시로 사건 시퀀스 $`\zeta=1:\texttt{reach-to-cup},\ \zeta=2:\texttt{contact-begins},\ \zeta=3:\texttt{grasp}\dots`$ 를 들며, captioning 모델("사람이 컵을 트레이에 올린다")과 달리 retarget·simulate·reward 에 쓸 수 있는 **물리 사건 시퀀스**를 복원해야 한다고 강조합니다. 또한 wearable 센싱(모션캡처 슈트)은 단순 teleoperation 인터페이스가 아니라 "물리 세계의 labelling instrument" 로 재해석되며, 실패조차 적절히 라벨링하면 미래 스킬(예: 의도적 drop)로 축적될 수 있다고 봅니다.

### 컴포넌트 2 — Task-preserving Retargeting (§3.2)

구조화된 사건 시퀀스를 추론해도 그 자체로는 로봇 정책이 되지 않습니다. 인간 손·평행 그리퍼·다지 손·모바일 매니퓰레이터·4족·휴머노이드는 운동학·동역학·센서·액션 공간·접촉면·실패 모드가 모두 다릅니다 — 이것이 **embodiment gap** 입니다. retargeting 은 사건 $`\zeta`$ 의 잠재 물리 액션 $`\mathbf{u}_{\zeta}`$ 와 object-centric 상태 $`\mathbf{s}_{\zeta}`$ 에서, embodiment e 에 대한 실행 가능 액션/스킬을 찾는 문제입니다.

$$\mathbf{a}_{\zeta}^{(\text{embodied})}=f_{\psi}(\mathbf{u}_{\zeta},\mathbf{s}_{\zeta},\text{embodiment})$$

이때 목표 관련 물리 변화가 보존되어야 합니다.

$$\Delta_{\mathbf{g}}(\text{s}_{\zeta},\mathbf{a}_{\zeta}^{(\text{embodied})})\approx\Delta_{\mathbf{g}}(\mathbf{s}_{\zeta},\mathbf{u}_{\zeta})$$

$`\Delta_{\mathbf{g}}`$ 는 목표 g 하의 태스크 관련 효과(여는 동작이면 서랍 변위, 놓기면 물체 pose, 삽입이면 상대 정렬, packing 이면 containment, grasping 이면 접촉 상태)입니다.

> "This formulation makes clear why pose matching is insufficient. The correct retargeting target is not the human joint trajectory, but the physical transformation that matters for the task." (§3.2)
(직관 — 인간 관절 궤적을 그대로 베끼는 pose matching 은 틀린 목표이고, 보존해야 할 것은 "태스크에 중요한 물리 변환"이라는 것입니다. 저자는 retargeting 이 pose → contact → object-state transition → intent/skill 의 4단계 불변량 위계를 올라가야 한다고 봅니다.)

### 컴포넌트 3 — Physics-grounded World Model (§3.3)

사건을 추론하고 embodiment 로 옮겨도, 로봇은 **결과(consequence)** 를 추론해야 합니다. 물체가 미끄러질지, 접촉이 성립/상실될지, 서랍이 열릴지 걸릴지를 예측해야 하며, 이는 시각적 질문이 아니라 기하·접촉·힘·제약·물성에 대한 추론입니다. 저자는 이를 consequence prediction 으로 추상화합니다.

$$\mathbf{s}_{\zeta+1}\sim p_{\omega}(\cdot|\mathbf{s}_{\zeta},\mathbf{u}_{\zeta},\mathbf{g})$$

특정 embodiment 에 대해서는

$$\mathbf{s}_{\zeta+1}\sim p_{\omega}(\cdot|\mathbf{s}_{\zeta},\mathbf{a}^{(\text{embodied})}_{\zeta},\text{embodiement},\mathbf{g})$$

첫 형태는 태스크 수준 추론("pull/lift/insert/place 의도 시 어떤 물리 전이가 일어나야 하는가"), 둘째 형태는 embodiment 별 계획을 지원합니다. 두 경우 모두 모델은 픽셀 이상의 것 — 제어와 보상에 중요한 물리 변수 — 을 예측해야 합니다.

> "The question is not 'does the future look realistic?' but 'does the prediction preserve the physical consequences that determine success or failure?'" (§3.3)
(이 문장이 world model 평가 기준을 재정의합니다 — 시각적 사실성이 아니라 task-conditioned consequence 보존이 목표입니다. 저자는 픽셀 예측·object-centric·3D·mechanics-based 표현의 trade-off 를 논하며, 가장 유망한 방향을 learned 3D scene + object-centric + physics-inspired 제약 + data-driven residual dynamics 의 **hybrid** 로 봅니다.)

### 컴포넌트 4 — Self-Improving Deployment Loop (§3.4)

배포 후의 질문은 "무엇이 일어났나"가 아니라 "일어난 일이 유용했나"입니다. 이는 generic state evaluator 로는 답할 수 없고 **reward grounding** — 시도 중인 태스크 기준으로 진척·성공·실패를 부여하는 능력 — 을 요구합니다. 저자는 보상을 목표 하의 물리 진척 해석으로 정의합니다.

$$\mathbf{r}_{\eta}(\mathbf{s}_{\zeta},\mathbf{g},\phi_{\zeta})$$

> "A physical state is not intrinsically successful or unsuccessful. The same state can mean different things depending on the goal: a cup resting on a table is success for 'put the cup down', failure for 'pick up the cup', and irrelevant for 'open the drawer'." (§3.4)
(직관 — 보상은 상태에 내재하지 않고 목표에 상대적이라는 것입니다. 따라서 reward model 은 generic preference modelling 과 달리 물체 상태·접촉·제약·태스크 단계에 묶여야 합니다.)

이 reward grounding 이 self-improving deployment 를 가능케 합니다. 모든 rollout 이 pass/fail 기록을 넘어 라벨링된 물리 episode 가 되며, 루프는 다음과 같습니다: deploy policy → observe outcome → infer task-conditioned progress/success/failure → explain failure or correction → add grounded supervision to the data engine → update reward model, world model, retargeting, and policy → redeploy. 저자는 이 루프가 세 능력 — (1) 의미 있는 사건 탐지, (2) 태스크 기준 평가, (3) **컴포넌트 수준 credit assignment**(정책/world-model/retargeting/reward 중 어디를 갱신할지 라우팅) — 을 요구한다고 못박습니다.

### 학습 셋업

해당 없음. 본 논문은 학습/평가를 수행하지 않는 position paper 이므로 데이터셋·옵티마이저·스케줄·하드웨어 셋업이 존재하지 않습니다. 형식화($`q_{\theta}`$ / $`f_{\psi}`$ / $`p_{\omega}`$ / $`\mathbf{r}_{\eta}`$)는 학습 목표가 아니라 "어떤 변수를 추론/보존해야 하는가"를 규정하는 명세 수준입니다.

---

## 📊 실험 설정과 결과

> 본 논문에는 자체 실험·벤치마크·정량 결과가 **없습니다**. 아래 표는 §2 survey 에서 저자가 인용한 외부 시스템·데이터셋의 verbatim 수치를 정리한 것이며, 본 논문의 측정값이 아닙니다(추론·보정·반올림 없음). PROBE 의 의사결정 맥락에서 "저자가 어떤 데이터/시스템을 grounding 병목의 근거로 인용했는가"를 추적하기 위한 정리입니다.

| 인용 시스템 / 데이터셋 | 본문이 인용한 규모·수치 | 역할 (저자 분류) |
|---|---|---|
| RoboNet | 15M video frames, 7 robot platforms | 초기 multi-robot 데이터셋 |
| BridgeData V2 | ~60k manipulation trajectories, 24 environments | robot-native 다양성 |
| DROID | ~76k demonstration trajectories ≈ 350 hours, hundreds of scenes | robot-native 다양성 |
| RH20T | 110,000+ contact-rich sequences (visual/force/audio/action + human video) | 멀티모달 grounding |
| RT-1 | ~130,000 episodes, 13 robots, 700+ tasks | language-conditioned generalist |
| Open X-Embodiment / RT-X | 1M+ trajectories, 22 robot embodiments | cross-embodiment |
| Octo | pretrained on 800,000 trajectories (OXE) | open-source generalist |
| OpenVLA | 7B params, ~970,000 demonstrations | open-source VLA |
| SpatialVLA | ~1.1M real robot episodes | spatial 표현 VLA |
| RDT-1B | 1M+ multi-robot episodes, diffusion-transformer | bimanual VLA |
| RLBench | 100 hand-designed tasks | 시뮬 벤치마크 |
| LIBERO | 130 language-conditioned tasks | lifelong 학습 |
| MimicGen | 50,000+ demos from <200 seed demos, 18 tasks | sim 데이터 생성 |
| RoboCasa365 | 365 tasks, 2,500 kitchen scenes, 2,000+ hours | 가사 sim 스케일 |

본문이 직접 명시한 대표 수치 인용을 두 개만 verbatim 으로 남깁니다.

> "Open X-Embodiment and RT-X pooled more than one million real robot trajectories from 22 robot embodiments by aggregating datasets from many research laboratories into a common format, making cross-embodiment training a practical research direction (O'Neill et al., 2024)." (§2.1)
(저자가 cross-embodiment 학습이 "실용 연구 방향"이 되었음을 보이는 근거로 인용 — robot-native supervision 의 스케일 한계를 논하는 §2.1 의 핵심 사례입니다.)

> "MimicGen ... automatically synthesises large-scale demonstration datasets in a simulator from a small number of human demonstrations ... generating more than 50,000 demonstrations from fewer than 200 seed demonstrations across 18 tasks (Mandlekar et al., 2023)." (§2.3)
(생성된 경험(sim data-generation)의 대표 사례로 인용 — "소량 seed → 대량 변형"이 가능하지만 그 변형이 접촉·안정성·마찰 등 제어에 중요한 물리 디테일을 보존하는지가 열린 질문이라는 §2.3 의 논지를 뒷받침합니다.)

각 survey 절의 결론은 "Takeaway" 단락으로 명시되어 있어, ablation 대신 **절별 논지**를 한 줄로 읽을 수 있습니다.

- **§2.1 Takeaway** — robot-native supervision 이 가장 인상적인 진척을 냈지만, 그 강함은 곧 한계(데이터가 이미 로봇 학습 좌표계로 표현됨). VLA 스케일링은 강력하나 여전히 *이미 grounding 된* supervision 에 의존.
- **§2.2 Takeaway** — passive video 는 표현·진척 신호·잠재 액션·행동 prior 를 줄 수 있으나 아직 로봇 supervision 이 아님(잠재 액션 ≠ 명령, 진척 신호 ≠ 보상, 인간 전략 ≠ 실행 가능). video 는 소스를 넓히지만 grounding 문제를 불가피하게 만듦.
- **§2.3 Takeaway** — 생성된 경험은 제어를 결정하는 물리 변수를 보존할 때만 유용. 시각적으로 그럴듯해도 접촉·힘·마찰·안정성을 무시하면 신뢰할 supervision 이 아님. 시뮬·world model 의 가치는 시각적 사실성이 아니라 **physically grounded counterfactual** 경험.

---

## ⚖️ 한계

- **검증 불가능한 입장 논문** — 네 컴포넌트 어느 것도 구현·측정되지 않았습니다. $`q_{\theta}`$(8개 하위문제 공동 추론)는 사실상 perception+추론의 거의 모든 미해결 난제를 한 모델에 모은 것이며, "어떻게"가 비어 있어 falsifiable 한 주장이 아닙니다. 어젠다로서의 가치와 별개로, 어떤 컴포넌트가 먼저 가능한지에 대한 우선순위·실현 가능성 분석이 없는 것이 가장 큰 약점입니다.
- **grounding 오차의 전파를 정량화하지 않음** — 저자 스스로 "errors in this grounding affect downstream policy learning" 을 언급하지만(§2.2), 잘못 추론된 latent action·접촉 라벨·보상이 retargeting → world model → policy 로 어떻게 누적·증폭되는지는 다루지 않습니다. 닫힌 루프는 오차도 닫힌 루프로 증폭될 수 있는데(저자가 world model hallucination 의 "viscous cycle"은 §2.3 에서 인정), 컴포넌트 간 오차 전파는 미분석입니다.
- **dexterity / hand-level 접촉이 사실상 부재** — 논문은 embodiment 목록에 "dexterous hand" 를 넣고 촉각·힘을 data engine 의 한 스트림으로 언급하지만, 손가락 수준 접촉·grasp 안정성·in-hand 조작의 고유 난제는 다루지 않습니다. 일반화 로봇 전반을 조망하는 altitude 라 hand-centric 문제가 해상도 밖으로 밀려납니다.
- **retargeting 위계의 상위 단계가 추상적** — pose → contact → object-state → intent 위계는 직관적이나, "intent/skill 보존"을 어떻게 정의·측정·최적화하는지는 비어 있습니다. $`\Delta_{\mathbf{g}}`$ 근사 보존을 무엇으로 측정하는지(metric)가 명시되지 않아 Layer 1 스펙으로 굳히기 어렵습니다.
- **VLA-level 개선과의 보완/경쟁 관계 미해소** — 저자는 VLA 를 "한 레이어"로 재배치하지만, VLA 아키텍처 자체의 개선(이질적 디코더·구조적 입력 등)이 grounding 어젠다와 어떻게 상호작용하는지는 논하지 않습니다. 상류 grounding 이 완벽해도 정책 인터페이스의 표현력이 천장이라면 어떻게 되는가에 대한 답이 없습니다(이는 PROBE 와 직접 충돌하는 지점 — 아래 ⚠️).

---

## ♻️ 재현성

- **코드/데이터/하드웨어** — 해당 없음. position paper 로 산출물(코드·데이터셋·모델 가중치)이 없으며, 본문/메타에서 GitHub·HuggingFace·프로젝트 사이트 링크가 확인되지 않았습니다(arXiv abstract HTML 및 전문 HTML 스캔 결과 외부 리포지토리 링크 부재).
- **재현 대상** — 재현할 실험이 없습니다. 본 논문의 "재현"은 인용 문헌(survey)의 추적 가능성에 한정되며, §2 의 모든 인용은 공개 논문입니다.
- **본문 확보** — 전문(arXiv HTML, LaTeXML 생성) 확보. 수식은 MathML+alttext 로 정상 추출되었습니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **분류상 위치** — 본 논문은 PROBE 의 모든 Pillar Anti-topic 이 명시적으로 배제하는 "Survey / position papers" 에 해당합니다. 즉 scout 라우팅으로는 통과하지 못하는 유형이며, 사람이 직접 지정해 manual 분석한 케이스입니다. 따라서 아래 Pillar 연결은 "방법 차용" 이 아니라 **전략·Identity 수준의 맥락 충돌/지지** 입니다.
- **P4(VLM 사전학습 보존) — 1차 연결.** 논문의 핵심(비정형 경험 → 로봇 supervision 변환, 인간 영상·cross-embodiment 데이터·retargeting)은 P4 가 소유한 **D22(multi-embodiment pretraining data)** 와 **D19b(VLM backbone lineage = 초기 가중치 × further-pretrain corpus)** 의 상위 질문과 직결됩니다. 저자가 인용한 GR00T N1(egocentric human video + sim/real robot + synthetic 혼합)은 P4 §5 에 핀된 논문이며, 본 논문은 그 데이터 혼합을 "embodied autolabelling 이 부재한 채 수동 grounding 된 결과"로 재해석합니다. 즉 P4 의 데이터 카탈로그(`catalogs/dataset.md`) 작업의 *상위 프레이밍* 을 제공합니다.
- **P3(Hand-level System0 / sim2real) — 2차 연결.** §2.3·§3.3 의 physics-grounded world model·sim2real·domain randomization·RMA(Kumar et al. — P3 §5 의 RMA 와 동일 계보) 논의는 P3 의 **D18(System0 sim2real)** 과 직접 맞닿습니다. 특히 ContactGaussian-WM(접촉 집약 differentiable contact world model)은 P3 §5 의 Contact-Aware Neural Dynamics 와 같은 "학습된 접촉 보정" 계보이며, 본 논문은 이를 "consequence prediction 이 픽셀이 아니라 접촉·힘을 보존해야 한다"는 일반 원칙으로 묶습니다.
- **P2(구조적 입력-모달리티 결합) — 약한 연결.** wearable 센싱·촉각·힘을 "물리 세계의 labelling instrument" 로 보는 §3.1 의 관점은 P2 의 촉각·force 스트림 철학과 공명하나, P2 의 핵심(per-finger 구조적 토큰화)과는 해상도가 다릅니다.
- **Identity 긴장 (핵심).** PROBE Identity 는 "dexterity 는 **VLA-level 에서 직접** tackle 해야 한다"고 봅니다. 본 논문은 정반대 altitude 에서 "VLA 는 한 레이어일 뿐이고 진짜 병목은 상류 grounding/data" 라고 주장합니다. 이는 PROBE 의 D-레벨 결정과 충돌하는 것이 아니라, PROBE 의 *작업 범위(scope-of-work)* 가 더 큰 스택의 일부임을 상기시키는 **Identity 수준의 외부 압력**입니다 (지지도 반박도 아닌 재배치).
- **경쟁자 함의** — 저자 소속(Motoniq.ai + Schwager/Hutter/Peters/Bou-Ammar)은 grounding·world-model·deployment 어젠다를 미는 진영으로, P3/P4 의 Tracked Literature 와 인접하나 hand-centric 경쟁자는 아닙니다.

---

## ✨ 핀 논문 대비 델타

- **GR00T N1(P4 §5 핀) 대비** — GR00T N1 은 "egocentric human video + sim/real + synthetic" 혼합으로 dual-system VLA 를 *학습한* 구체 시스템입니다. 본 논문은 그 데이터 혼합이 여전히 **수동으로 grounding 된** 결과임을 지적하고, 그 grounding 을 자동화할 $`q_{\theta}`$(embodied autolabelling)를 누락 컴포넌트로 격상시킨다는 점이 새롭습니다. 즉 "어떤 데이터를 섞었는가" → "그 데이터를 어떻게 supervision 으로 변환하는가" 로 질문을 한 단계 올립니다.
- **π0 / π0.5(P1·P4 §5 핀) 대비** — π0 는 flow-matching action expert 로 VLA 의 정책 인터페이스를 정의합니다. 본 논문은 π0 류를 명시적으로 "스택의 한 레이어" 로 인용·재배치하며(§2.1), 정책 아키텍처 자체보다 상류 4개 인터페이스가 다음 병목이라고 주장합니다 — π0 의 기여를 부정하지 않되 그 효용의 *천장* 을 상류 grounding 으로 돌리는 관점 전환.
- **Contact-Aware Neural Dynamics / Beyond Binary(P3 §5 핀) 대비** — 이들은 접촉 sim2real 의 구체 기법입니다. 본 논문은 동일 계보(ContactGaussian-WM 등)를 인용하되, 개별 기법이 아니라 "physics-grounded consequence prediction" 이라는 일반 요구로 추상화하고, 이를 retargeting·deployment loop 와 묶는 시스템 관점이 델타입니다.
- **순수 신규성 평가** — 본 논문의 신규성은 *방법* 이 아니라 *조직 원리(organizing principle)* 입니다. 개별 컴포넌트(autolabelling·retargeting·world model·reward)는 모두 기존 연구가 있으나, 이를 "supervision 병목"이라는 단일 축으로 묶고 closed-loop 스택으로 제시한 프레이밍이 차별점입니다.

---

## ⚙️ 의사결정 함의

- **P4 / D22 — 데이터 카탈로그의 상위 축 추가 후보.** 본 논문은 `catalogs/dataset.md` 의 further-pretrain corpus 를 분류할 때 "grounding 수준"(robot-native = 강 / human-video = 약 / sim-generated = 물리보존 의존)이라는 축을 제안합니다. v1 의 D22(=π pretrained prior 만 사용, 추가 co-train 없음)는 유지하되, 향후 human-video / egocentric 데이터를 도입할 때 "grounding 비용"을 데이터셋 평가 컬럼으로 추가하는 것을 검토할 수 있습니다. 구체 변경 대상: `dataset.md` 의 entry facts line.
- **P3 / D18 — world-model consequence 평가를 sim2real 체크에 반영.** "시각적 사실성 ≠ 제어 유용성, consequence(접촉·힘·안정성) 보존이 기준" 이라는 §3.3 의 원칙은 System0 sim2real 프로토콜(Chen et al. 2024 계보 촉각 sim2real)의 *평가 메트릭* 에 직접 적용 가능합니다. 즉 DR 의 성공을 "픽셀/렌더 품질"이 아니라 "접촉 상태·grasp 유지 결과의 sim-real 상관"으로 측정하도록 메트릭을 고정.
- **scope-of-work 경계 재확인.** 본 논문이 옳다면, PROBE 의 VLA-level 작업(P1 이질적 디코더·P2 구조적 입력)은 *충분조건이 아니라 필요조건의 일부* 입니다. 다만 이는 PROBE 의 어떤 v1 결정(D1–D23)도 바꾸지 않습니다 — PROBE 는 의도적으로 modeling-at-VLA-level 에 scope 를 한정했고(MASTER §3.2), 본 논문은 그 scope 밖(data engine·retargeting·deployment)을 다루기 때문입니다. **변경 없음** 이 올바른 결론.
- **구체 파이프라인 변경 — 없음(현 단계).** 본 논문은 position paper 라 즉시 적용할 config 키·하이퍼파라미터·loss term 이 없습니다. 유일하게 actionable 한 것은 위 두 *평가/카탈로그* 메트릭 후보이며, 학습 파이프라인 자체는 무변경입니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 체크) altitude 불일치 — "우리 문제에 답을 주는가?"** 본 논문은 일반화 로봇 전반의 데이터/supervision 어젠다이고, PROBE 는 hand-centric dexterous manipulation 의 VLA-level 아키텍처입니다. 30초 sanity check: 네 컴포넌트 중 PROBE 의 현재 Phase 1(in-hand cube rotation)에 *오늘* 적용 가능한 것이 있는가? → 없음. 따라서 "방법 전이" 기대는 즉시 기각하고, 본 논문은 **전략적 맥락/외부 압력**으로만 소비하는 것이 맞습니다.
- **grounding 자동화의 미성숙 — System0 데이터에 의존 금지.** 만약 $`q_{\theta}`$ 식 autolabelling 을 차용해 인간 영상에서 접촉/슬립 라벨을 자동 추출하려 한다면, 그 라벨 품질이 P3 의 hand-crafted contact-aware reward(D17)를 대체할 만큼 검증되지 않았습니다. 값싼 체크: 소규모 wearable/촉각 episode 에서 자동 추론된 contact 라벨과 수동 라벨의 일치율을 먼저 측정 — 일치율이 낮으면 autolabelling 도입 보류.
- **retargeting $`\Delta_{\mathbf{g}}`$ 보존의 측정 불가 위험.** 손가락 수준 in-hand 조작에서 "task-relevant 물리 효과 보존"은 grasp pose·접촉 분포의 미세 차이에 극도로 민감합니다. 인간 손 → Sharpa Hand(22-DOF) retargeting 시 $`\Delta_{\mathbf{g}}`$ 가 정의 가능한 metric 으로 환원되는지 불명확하므로, embodiment gap 이 가장 큰 손 영역에서 본 논문의 위계(pose→intent)가 실제로 작동하는지부터 의심.
- **world-model consequence 평가의 sim-real 상관 미검증.** §3.3 의 "consequence 보존" 원칙을 System0 sim2real 메트릭으로 채택하기 전에, 접촉 상태 기반 메트릭이 실제 grasp 유지 성공률과 상관하는지(저자가 인용한 Zhang et al. 2025b 의 deformable 사례처럼)를 우리 하드웨어에서 먼저 확인. 상관이 약하면 메트릭 교체는 오히려 잡음 도입.
- **인용 편향 / 신생 진영 주장.** 저자 소속이 grounding/world-model/deployment 어젠다를 미는 진영이라 survey 가 그 방향으로 기울 수 있습니다. P3/P4 의사결정에 인용할 때는 본 논문의 "주장"과 인용된 "원논문의 측정값"을 분리해 사용(원논문을 직접 확인).

---

## 💡 컨텍스트 제안

- **핀 교체 — 제안 없음.** 본 논문은 position/survey paper 로, P3·P4 §5 의 8-핀 cap(구체 method/시스템 우선)에 추가할 후보가 아닙니다. Anti-topic("survey/position papers, read manually")에 부합하므로 핀 미등재가 올바릅니다.
- **D22 평가 축 후보(검토만)** — 향후 human-video / egocentric 데이터를 `catalogs/dataset.md` 에 추가할 때 "grounding 수준(robot-native / weak-video / sim-generated)" 을 facts line 의 보조 축으로 둘지 사람이 판단. 지금 당장 D22 v1(π prior only)을 바꿀 근거는 아님.
- **D18 평가 메트릭 메모(검토만)** — System0 sim2real 검증 메트릭을 "렌더 품질"이 아니라 "접촉·grasp 결과의 sim-real 상관"으로 정의하는 방향을 P3 real-robot transition 계획 시 참고. 현 단계 결정 변경 아님.
- **종합** — PROBE Identity 의 scope-of-work(modeling at VLA level)는 의도적 한정이며, 본 논문은 그 밖의 스택을 다루므로 어떤 context/ 파일도 수정할 필요가 없습니다.

---

> 💡 base 매핑은 `/implement-design analysis/2606.06556/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
