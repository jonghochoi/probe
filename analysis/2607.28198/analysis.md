# Paper Analysis — UniCross: Unified Cross-Skill Dexterous Manipulation Synthesis

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | UniCross: Unified Cross-Skill Dexterous Manipulation Synthesis |
| 저자 | Hui Zhang, Julian Ferchow, Jie Song, Mirko Meboldt (ETH Zürich · inspire AG · HKUST (Guangzhou)) |
| 링크 | [arXiv:2607.28198](https://arxiv.org/abs/2607.28198) · [Website](https://zdchan.github.io/UniCross/) |
| 발행일 / 버전 | 2026-07-30 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-08-02 |
| 관련 Pillar | P3, P1, P2 |
| 태그 | dexterity, force |

<!-- 부록 포함 전문을 arXiv HTML 로 확보했습니다. 프로젝트 페이지
     https://zdchan.github.io/UniCross/ 는 본 실행 환경의 네트워크 정책이
     CONNECT 를 거부해(HTTP 403, `curl -L --fail -sS https://zdchan.github.io/UniCross/`)
     내용을 확인하지 못했습니다. URL 자체는 논문 본문·arXiv abs 페이지에
     명시된 값 그대로입니다. ♻️ 재현성 참조. -->

---

## 🧭 한 줄 요약 (TL;DR)

grasping · relocation · in-hand rotation · in-hand translation 네 가지 손재주 조작 스킬을, 접촉 패턴이 아니라 **손-물체 상대 운동(hand-object relational motion)** 관점에서 하나의 관측·행동·보상 형식으로 통일하고, 그렇게 학습한 10개 per-skill 전문가를 DAgger 로 단일 정책에 증류해 미학습 물체·외란·손 형상 변화에 견디면서 스킬을 끊김 없이 연쇄시킵니다. 스킬별 특수 설계(팔을 위로 향한 고정 손목, 스킬 전용 손 형상 등)를 제거한 것이 장기 과제 연쇄가 가능해진 직접적 원인이라는 주장입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 물체를 손 안에 계속 안정적으로 붙잡은 채 수행하는 조작은 grasping, relocation, in-hand rotation, in-hand translation 네 가지 정준 스킬로 분해됩니다. 인간은 이들을 자유롭게 조합하지만, 기존 방법은 각 스킬을 별도 문제로 모델링합니다.
- **기존 접근의 한계** — 스킬마다 다른 행동 제약·목표·심지어 전용 손 형상을 쓰기 때문에, 한 스킬이 도달한 상태가 다음 스킬의 유효 시작 상태가 되지 못합니다. 즉 장기 과제 조합에 필요한 호환성(compatibility)과 연속성(continuity)이 구조적으로 깨집니다.
- **본 논문의 가설** — 네 스킬은 접촉 양상은 다르지만 모두 "물체 안정성을 유지한 채 원하는 손-물체 상대 운동을 실현한다"는 동일한 목적을 가집니다. 따라서 상대 운동을 조건으로 하는 **단일 형식(single formulation)** 의 서로 다른 인스턴스로 볼 수 있다는 가설입니다.
- **통일이 어려운 이유** — 논문 스스로 세 가지 난점을 듭니다. (1) 스킬마다 요구 접촉 체제가 근본적으로 다르고(grasp/relocate 는 지속적 강접촉, in-hand 는 잦은 접촉 재구성), (2) 물체 형상 표현이 스킬 전반을 커버해야 하며, (3) 스킬 간 상태 호환을 위해 팔을 위로 향한 손바닥 지지 같은 스킬 특화 셋업을 쓸 수 없습니다.
- **왜 지금 중요한가** — 캐릭터 애니메이션 분야는 이미 통일된 해 공간 위에서 단일 컨트롤러가 다양한 전신 행동을 합성하는 단계에 도달했지만, 손재주 조작은 아직 개별 스킬 단계에 머물러 있습니다. 손재주 조작에 통일된 해 공간이 존재하는지 자체가 미해결 질문입니다.

---

## 🧩 핵심 기여

- 손재주 조작을 **손-물체 상대 운동 관점**으로 재정의하고, grasping · relocation · in-hand rotation · in-hand translation 을 동일한 상태 공간 · 행동 공간 · 보상 구조를 공유하는 단일 형식의 인스턴스로 모델링합니다.
- 이 형식 위에서 학습한 10개 per-skill 전문가(grasp 1 · relocate 1 · rotation 6축 · translation 2축)를 **vanilla DAgger** 로 단일 cross-skill 정책에 증류합니다. 다중 스킬 증류에서 흔한 성능 저하가 거의 없는 것을 보입니다.
- 단일 정책이 스킬별로 학습된 baseline(GraspXL · RotateIt · Yin et al.)을 **baseline 자신의 유리한 셋업에서도** 능가하며, 미학습 기하(구·육각기둥·팔각기둥)와 외란에도 견딤을 보입니다.
- 동일 프레임워크가 **Allegro · MANO · Sharpa Wave** 세 가지 손 형상에 그대로 적용되어, 형상 비의존적(morphology-agnostic) 임을 보입니다.
- 스킬 간 상태 호환성 덕분에 grasp → relocate → in-hand rotation/translation 의 **장기 연쇄를 단일 정책의 연속 실행으로** 수행합니다(전체 성공률 87.4% / 96.3%).

---

## 🔑 기술 키워드

- **Hand-object relational motion** — 접촉이 어떻게 생겼는가가 아니라 손과 물체의 *상대적 움직임*으로 스킬을 정의하는 관점. "무엇을 어떻게 쥐었나" 대신 "손 기준으로 물체가 어디로 움직이나"를 기술 단위로 삼습니다. 본 논문 통일 형식의 출발점입니다.
- **Root frame / hand frame** — root frame 은 에피소드 시작 시의 손목 자세로 고정된 기준계, hand frame 은 매 순간의 손 자세를 따라가는 이동 기준계. 네 스킬은 "무엇이 어느 프레임에서 고정/추적/자유인가"의 조합만으로 구분됩니다.
- **Virtual wrist joints** — 손목의 6-DoF 운동을 3 병진 + 3 회전의 zero-initialized 가상 관절로 파라미터화한 것. 절대 세계 좌표 대신 초기 자세 대비 상대 운동을 다루게 해 일반화에 유리합니다.
- **Interaction-aware object representation** — 물체를 메시·포인트클라우드로 주는 대신, 손 링크별 접촉 여부 · 접촉력 크기 · 링크에서 물체 표면 최근접점까지의 거리 벡터로 표현하는 hand-centric 표현. GraspXL 에서 가져와 네 스킬 전체로 확장했습니다.
- **Task axis** — hand frame 에서 과제 방향을 정의하는 단위 벡터. grasp 는 물체 중심→손 원점, relocate 는 현재 위치→목표 위치, rotation 은 6축 중 하나, translation 은 2축 중 하나를 가리킵니다. 스킬 정체성을 3차원 벡터로 압축한 장치입니다.
- **Tracked / Fixed / Free instantiation** — 6개 목표 자세 변수 각각을 "목표를 향해 동적으로 갱신(Tracked) / 초기값 유지(Fixed) / 현재값 대입해 자유화(Free)"로 지정하는 규칙. 이 세 값의 배정표 하나가 곧 스킬 정의가 됩니다.
- **Residual wrist action** — 행동을 증분 명령으로 두되, 손가락은 직전 행동을, 손목은 *현재 목표 손목 자세*를 기준점으로 삼는 비대칭 파라미터화. 손목의 큰 진폭 탐색을 가속하는 장치이며 ablation 에서 relocation 성능을 가장 크게 좌우합니다.
- **DAgger distillation** — 학습 중인 정책을 굴려 상태를 모으고 그 상태에 대해 전문가 행동을 질의해 MSE 로 모방하는 표준 절차. 본 논문은 아무 변형 없는 vanilla 형태로 10개 전문가를 하나로 합칩니다.
- **PPO (Proximal Policy Optimization)** — per-skill 전문가를 학습하는 on-policy 강화학습 알고리즘. IsaacGym 대규모 병렬 환경에서 사용합니다.
- **Skill chaining** — 한 스킬의 종료 상태가 다음 스킬의 유효 시작 상태가 되어 정책 교체 없이 연속 실행되는 것. 본 논문이 스킬 특화 셋업을 버린 이유이자 그 대가로 얻은 능력입니다.

---

## 🔬 방법론

### 직관

이 논문의 출발 질문은 "왜 잡기와 손 안 돌리기를 서로 다른 문제로 풀어야 하는가"입니다. 통상적인 답은 접촉 양상이 다르기 때문입니다. 잡기와 옮기기는 강하고 지속적인 접촉을 원하지만, 손 안에서 물체를 굴리거나 밀어 넣으려면 손가락이 계속 붙었다 떨어지며 접촉을 재구성해야 합니다. 접촉을 기준으로 문제를 나누면 두 부류는 정반대의 요구를 갖게 되고, 그래서 보상도 행동 제약도 심지어 손 하드웨어까지 갈라집니다.

저자들은 기준을 바꿉니다. 접촉이 아니라 **손과 물체의 상대 운동**을 봅니다. 그러면 네 스킬은 하나의 문장으로 묶입니다 — "물체를 손에 안정적으로 붙잡은 채, 원하는 상대 운동을 만들어라." 잡기는 물체가 세계에 고정된 채 손이 다가가는 것이고, 옮기기는 물체가 손에 고정된 채 손목이 세계에서 움직이는 것이며, 손 안 회전/이동은 손목이 세계에 고정된 채 물체가 손 기준으로 도는/미끄러지는 것입니다. 즉 두 개의 기준계(에피소드 시작 손목 자세로 고정된 root frame, 매 순간 손을 따라가는 hand frame)에서 무엇을 고정하고 무엇을 추적하느냐만 다릅니다.

이 관점을 그대로 구현하면 스킬 정의는 코드가 아니라 **표 한 장**이 됩니다. 목표 자세 변수 6개(물체 위치/자세 × 두 프레임, 손 위치/자세 × root frame)에 대해 각각 Tracked / Fixed / Free 를 지정하면 그것이 스킬입니다. 관측·행동·보상은 건드리지 않습니다. 관측에는 어떤 스킬인지 알려주는 one-hot 과 과제 축을 가리키는 단위 벡터가 들어가고, 보상은 "접촉을 유지하라 + 과제 축 방향으로 움직여라 + 목표 자세를 추적하라 + 낭비하지 마라"라는 동일한 뼈대를 스킬마다 계수만 바꿔 재사용합니다.

형식이 같으면 증류가 거저 따라옵니다. 10개 전문가가 같은 입출력 규격과 같은 네트워크를 쓰므로, 어떤 특별한 다중 과제 기법도 없이 표준 DAgger 로 하나에 합쳐집니다. 그리고 이렇게 만든 단일 정책은 스킬 특화 가정(손바닥을 위로 향한 채 물체를 받치는 셋업 등)을 아예 갖지 않기 때문에, 잡고 → 옮기고 → 손 안에서 돌리는 동작을 정책 전환 없이 한 번에 이어서 수행할 수 있습니다. 논문이 최종적으로 주장하는 것은 성능 수치가 아니라 이 구조적 결과입니다.

### 아키텍처

![Figure 2 — unified framework overview](https://arxiv.org/html/2607.28198/x1.png)

> "Figure 2: Overview of the proposed unified framework. Ten per-skill policies (one for grasp, one for relocate, six for rotation (x+/x-/y+/y-/z+/z- of the hand frame), and two for translation (z+/z- of the hand frame)) are first trained independently and then distilled into a single unified policy via DAgger. All policies share a unified observation space, network architecture, and action space, and the per-skill policies share a unified reward formulation." (§3)
(한글 해설 — 파이프라인 전체가 이 한 장에 들어 있습니다. 왼쪽의 통일된 관측(Hand State / Object State / Objective)이 10개 전문가와 최종 단일 정책에 동일하게 공급되고, 오른쪽에서 DAgger 로 하나로 합쳐지는 구조입니다.)

**기준계 정의.** 에피소드 시작 시 세계 좌표의 손목 자세로 root frame 을 정의하고 에피소드 내내 고정합니다. 손목 운동은 3 병진 + 3 회전의 zero-initialized 가상 관절로 파라미터화합니다.

> "This formulation represents wrist motion relative to the initial pose instead of absolute world coordinates, which benefits generalization." (§3.1.1)
(한글 해설 — 절대 좌표를 쓰면 정책이 특정 작업 공간 위치에 묶입니다. 초기 손목 자세를 원점으로 삼아 상대 운동만 다루면 같은 정책이 임의의 시작 자세에서 재사용됩니다. 뒤의 rotation/translation 평가에서 손목 자세를 세계 좌표에서 무작위 초기화할 수 있는 근거가 여기에 있습니다.)

현재 손 자세로는 hand frame 을 정의합니다. 물체 자세는 hand frame 에서 $`\mathbf{x}_{o}^{h}`$ · $`\mathbf{q}_{o}^{h}`$ , root frame 에서 $`\mathbf{x}_{o}^{r}`$ · $`\mathbf{q}_{o}^{r}`$ 로, 손 자세는 root frame 에서 $`\mathbf{x}_{h}^{r}`$ · $`\mathbf{q}_{h}^{r}`$ 로 표현합니다. 목표 자세는 $`\hat{\cdot}`$ 로 표기합니다.

네 스킬의 상대 운동 정의는 다음과 같이 서술됩니다.

> "Grasp: the object is fixed in the root frame, while the hand moves in the root frame towards the object." (§3.1.1)
> "Relocate: the object is fixed in the hand frame, while the wrist moves in the root frame to reach a target object pose." (§3.1.1)
> "Rotate: the wrist is fixed in the root frame, the object position is fixed in the hand frame, and the object orientation rotates about a designated axis in the hand frame." (§3.1.1)
> "Translate: the wrist is fixed in the root frame, the object orientation is fixed in the hand frame, and the object position translates along a designated axis in the hand frame." (§3.1.1)
(한글 해설 — 네 문장이 사실상 이 논문의 전부입니다. 접촉·힘·손 형상 같은 물리적 서술이 하나도 등장하지 않고, 오직 "어느 프레임에서 무엇이 고정/이동하는가"만으로 스킬이 정의됩니다. 이 추상화 수준이 유지되기 때문에 뒤이어 관측·행동·보상을 공유할 수 있습니다.)

**관측 공간.** 관측은 세 블록으로 구성됩니다.

$$\textbf{o}_{t}=(\mathbf{s}_{t}^{\text{h}},\mathbf{s}_{t}^{\text{o}},\mathbf{g}_{t})$$

- **손 상태** — $`\mathbf{s}_{t}^{\text{h}}=[\mathbf{q}_{t},\mathbf{q}_{t-1}^{\text{target}}]`$ , 모든 손 관절(손가락 관절 + 가상 손목 관절)의 현재 위치와 직전 목표 위치입니다.
- **물체 표현** — $`\mathbf{s}_{t}^{\text{o}}=[\mathbf{c}_{t},\mathbf{f}_{t},\mathbf{v}_{t}]`$ , 링크별 접촉 상태 $`\mathbf{c}_{t}`$ , 접촉력 크기 $`\mathbf{f}_{t}`$ , 각 손가락 링크에서 물체 표면 최근접점까지의 거리 벡터 $`\mathbf{v}_{t}`$ 입니다.
- **목표 특징** — 55차원 벡터 $`\mathbf{g}_{t}=[\mathbb{I}_{t},\mathbf{d}_{t}^{\text{h}},\mathbf{g}_{t}^{\text{current}},\mathbf{g}_{t}^{\text{target}}]`$ 로, $`\mathbb{I}_{t}\in\mathbb{R}^{10}`$ 는 현재 과제 모드(잡기, 옮기기, 2방향 이동, 6방향 회전)를 가리키는 one-hot, $`\mathbf{d}_{t}^{\text{h}}\in\mathbb{R}^{3}`$ 는 hand frame 에서 과제 축을 정의하는 단위 방향 벡터입니다.

여기서 $`\mathbf{g}_{t}^{\text{current}}=[\mathbf{x}_{o}^{h},\mathbf{q}_{o}^{h},\mathbf{x}_{o}^{r},\mathbf{q}_{o}^{r},\mathbf{x}_{h}^{r},\mathbf{q}_{h}^{r}]`$ 이고 $`\mathbf{g}_{t}^{\text{target}}`$ 는 그 목표 버전입니다(각각 21차원, 합쳐 10 + 3 + 21 + 21 = 55).

> "This interaction-centric representation, inspired by [67], captures hand-object spatial relationships as well as object geometry features shared across manipulation skills." (§3.1.2)
(한글 해설 — 물체 기하를 전역 메시로 주지 않고 손 링크 기준의 접촉·거리 관계로만 주는 것이 핵심입니다. 표현이 손에 붙어 있으므로 물체가 바뀌어도 표현의 차원과 의미가 변하지 않고, 그래서 미학습 기하로의 일반화와 손 형상 교체가 동시에 가능해집니다. 원 출처는 grasping 전용으로 제안된 GraspXL [67] 이며, 본 논문의 기여는 이것이 네 스킬 전부에서 유효함을 보인 데 있습니다.)

**행동 공간.** 행동은 가상 손목 관절 6개와 모든 손가락 관절을 포괄하는 증분 명령이며, 목표 관절 위치로 변환됩니다.

$$\mathbf{q}_{t}^{\text{act}}=\text{clamp}(\mathbf{q}_{t}^{\text{ref}}+\boldsymbol{\alpha}\cdot\mathbf{a}_{t},\mathbf{q}_{\min},\mathbf{q}_{\max})$$

여기서 $`\boldsymbol{\alpha}`$ 는 관절별 행동 스케일, $`\text{clamp}(\cdot)`$ 은 $`\mathbf{q}_{\min}`$ · $`\mathbf{q}_{\max}`$ 로 정의된 해부학적 관절 한계입니다. 결정적인 비대칭은 기준점 $`\mathbf{q}_{t}^{\text{ref}}`$ 에 있습니다 — 손가락 관절은 $`\mathbf{q}_{t-1}^{\text{act}}`$ (직전 행동)를, 가상 손목 관절은 *현재 목표 손목 자세*( $`\hat{\mathbf{x}}_{h}^{r}`$ 와 $`\hat{\mathbf{q}}_{h}^{r}`$ 의 오일러각)를 씁니다.

> "This incremental motion parameterization facilitates temporally coherent and smooth finger motions while accelerating wrist motion exploration." (§3.1.3)
(한글 해설 — 손가락은 직전 명령 주변의 작은 증분으로 부드러움을 얻고, 손목은 목표 자세 주변의 증분으로 탐색해 큰 진폭 이동을 빨리 배웁니다. 같은 행동 공간 안에서 신체 부위별로 기준점만 바꾼 것인데, ablation 에서 이 한 줄이 relocation 성공률을 99.0% → 37.4% 로 가르는 결정적 요소로 드러납니다.) 최종 목표 관절 위치는 PD 컨트롤러로 토크로 변환되어 적용됩니다.

**네트워크.** 목표 특징 $`\mathbf{g}_{t}`$ 를 받는 MLP 인코더(은닉 2층, [128, 64])와, $`\mathbf{s}_{t}^{\text{h}}`$ · $`\mathbf{s}_{t}^{\text{o}}`$ 및 인코더 출력을 받아 행동을 예측하는 main MLP(은닉 3층, [512, 256, 128]) 두 부분으로 구성되며, 10개 전문가와 최종 단일 정책이 모두 이 구조를 공유합니다.

### 학습 목표 / 손실

보상은 세 항의 합으로 정의됩니다 (식 1).

$$r_{t}=r_{t}^{\text{goal}}+r_{t}^{\text{track}}+r_{t}^{\text{reg}}$$

$`r_{t}^{\text{goal}}`$ 은 일반적 손-물체 상호작용 목표를, $`r_{t}^{\text{track}}`$ 은 목표 자세 추적을, $`r_{t}^{\text{reg}}`$ 는 안정성·효율성 페널티를 담당합니다.

**목표 항 (식 2).** "물체는 원하는 운동을 수행하는 동안 손에 안정적으로 붙잡혀 있어야 한다"는 요구를 접촉 항과 운동 항으로 나눕니다.

$$r_{t}^{\text{goal}}=r_{t}^{\text{contact}}+r_{t}^{\text{motion}}$$

접촉 항은 $`r_{t}^{\text{contact}}=\frac{1}{N}\sum_{i}^{N}(-w_{\text{dis}}\cdot d_{i}+w_{\text{con}}\cdot c_{i}+w_{\text{f}}\cdot f_{i})`$ 로, $`N`$ 은 손 링크 수, $`d_{i}`$ 는 링크 $`i`$ 에서 물체까지 거리, $`c_{i}\in\{0,1\}`$ 는 접촉 여부, $`f_{i}`$ 는 접촉력 크기입니다. 운동 항은 $`r_{t}^{\text{motion}}=w_{\text{p}}\cdot\text{min}(\mathbf{v}_{o}^{h}\cdot\mathbf{d}^{\text{h}},v_{\max})`$ 로, hand frame 물체 속도를 과제 축에 사영한 성분을 $`v_{\max}`$ 로 상한 두어 보상합니다. 과도한 속도를 상한으로 잘라내 "빨리 던지는" 퇴화 해를 막는 장치입니다.

**추적 항 (식 3).** 두 프레임 각각에서 손과 물체의 목표 자세 이탈을 벌합니다. $`\mathcal{A}(\cdot,\cdot)`$ 는 두 쿼터니언의 각도 차이입니다.

```math
r_{t}^{\text{track}}=\begin{aligned} &w_{opr}\|\mathbf{x}_{o,t}^{r}-\hat{\mathbf{x}}_{o}^{r}\|^{2}+w_{oqr}\mathcal{A}(\mathbf{q}_{o,t}^{r},\hat{\mathbf{q}}_{o}^{r})\\ &+w_{oph}\|\mathbf{x}_{o,t}^{h}-\hat{\mathbf{x}}_{o}^{h}\|^{2}+w_{oqh}\mathcal{A}(\mathbf{q}_{o,t}^{h},\hat{\mathbf{q}}_{o}^{h})\\ &+w_{hpr}\|\mathbf{x}_{h,t}^{r}-\hat{\mathbf{x}}_{h}^{r}\|^{2}+w_{hqr}\mathcal{A}(\mathbf{q}_{h,t}^{r},\hat{\mathbf{q}}_{h}^{r}).\end{aligned}
```

여섯 항이 모두 항상 켜져 있고, 스킬 차이는 목표값 $`\hat{\cdot}`$ 이 Tracked / Fixed / Free 중 무엇으로 채워지는가로만 발생합니다. Free 로 지정된 변수는 목표가 현재값으로 대입되므로 해당 항이 자동으로 0 이 되어 그 자유도가 풀립니다. 보상 함수를 스킬마다 다시 쓰지 않고도 스킬별 제약을 표현하는 장치입니다.

**정규화 항 (식 4).**

$$r_{t}^{\text{reg}}=r_{t}^{\text{pose}}+r_{t}^{\text{vel}}+r_{t}^{\text{energy}}+r_{t}^{\text{drop}}$$

- $`r_{t}^{\text{pose}}=w_{\text{pose}}\sum_{i=1}^{N}(q_{i,t}-q_{i,0})^{2}`$ — 초기 손가락 관절 위치 이탈을 벌해 과도한 손가락 움직임을 억제합니다.
- $`r_{t}^{\text{vel}}=w_{\text{vel}}\|\dot{\mathbf{x}}_{h,t}\|^{2}+w_{\text{ang}}\|\boldsymbol{\omega}_{h,t}\|^{2}`$ — 손목 병진·각속도를 벌해 부드러운 손목 운동을 유도합니다.
- $`r_{t}^{\text{energy}}=w_{\tau}\|\boldsymbol{\tau}_{t}\|^{2}`$ — 관절 토크 크기를 벌합니다.
- $`r_{t}^{\text{drop}}=w_{\text{drop}}\mathbb{I}_{\text{drop}}`$ — 물체 낙하로 인한 조기 종료를 벌하며, 지시자는 모든 손 링크와 물체 사이 거리가 임계를 넘는지로 정의됩니다.

**목표 자세 인스턴스화.** 스킬 정의는 $`\mathbf{d}^{\text{h}}`$ 와 $`\mathbf{g}_{t}^{\text{target}}`$ 를 어떻게 채우는가로 환원됩니다.

> "As summarized in Tab. 1, each target is set as Tracked (dynamically updated toward the skill objective), Fixed (held at the initial variable value), or Free (set to the current variable value so the corresponding DOF is unconstrained)." (§3.2, Table 1)
(한글 해설 — 이 세 값이 스킬 문법의 전부입니다. 알고리즘·네트워크·보상식을 건드리지 않고 목표 변수 배정표만 바꿔 새 스킬을 정의할 수 있다는 것이 이 형식의 확장성 주장입니다.)

| Skill | Tracked | Fixed | Free |
|---|---|---|---|
| Grasp | $`\hat{\mathbf{x}}_{o}^{h}`$ | $`\hat{\mathbf{x}}_{o}^{r},\hat{\mathbf{q}}_{o}^{r}`$ | $`\hat{\mathbf{q}}_{o}^{h},\hat{\mathbf{x}}_{h}^{r},\hat{\mathbf{q}}_{h}^{r}`$ |
| Relocate | $`\hat{\mathbf{x}}_{o}^{r},\hat{\mathbf{q}}_{o}^{r},\hat{\mathbf{x}}_{h}^{r},\hat{\mathbf{q}}_{h}^{r}`$ | $`\hat{\mathbf{x}}_{o}^{h},\hat{\mathbf{q}}_{o}^{h}`$ | None |
| Rotate | $`\hat{\mathbf{q}}_{o}^{h},\hat{\mathbf{q}}_{o}^{r}`$ | $`\hat{\mathbf{x}}_{h}^{r},\hat{\mathbf{q}}_{h}^{r},\hat{\mathbf{x}}_{o}^{r},\hat{\mathbf{x}}_{o}^{h}`$ | None |
| Translate | $`\hat{\mathbf{x}}_{o}^{h},\hat{\mathbf{x}}_{o}^{r}`$ | $`\hat{\mathbf{x}}_{h}^{r},\hat{\mathbf{q}}_{h}^{r},\hat{\mathbf{q}}_{o}^{r},\hat{\mathbf{q}}_{o}^{h}`$ | None |

과제 축 $`\mathbf{d}^{\text{h}}`$ 는 grasping 에서 물체 중심→손 프레임 원점, relocation 에서 현재 물체 위치→목표 위치, rotation 에서 6축(x+/x−/y+/y−/z+/z−) 중 하나, translation 에서 2축(z+/z−) 중 하나를 가리킵니다. Tracked 목표의 동적 갱신은 rotation 이 $`\hat{\mathbf{q}}_{o,t}^{h}=\mathbf{R}(\omega_{\max}\Delta t,\mathbf{d}^{\text{h}})\cdot\mathbf{q}_{o,t}^{h}`$ , translation 이 $`\hat{\mathbf{x}}_{o,t}^{h}=\mathbf{x}_{o,t}^{h}+v_{\max}\Delta t\cdot\mathbf{d}^{\text{h}}`$ 로, 즉 **현재 상태에서 한 스텝만큼 앞선 목표**를 매 스텝 다시 만드는 방식입니다. 절대 목표 자세를 주지 않으므로 회전·이동이 무한히 연속될 수 있습니다. relocation 은 예외적으로 주어진 최종 6D 자세 $`\mathbf{T}^{\text{final}}`$ 를 향해 현재 자세에서 선형 보간한 값을 목표로 씁니다.

**증류 목표.** 10개 전문가를 하나로 합치는 절차는 표준 DAgger 이며, 논문은 이것이 형식 통일의 자연스러운 귀결임을 강조합니다.

> "Modeled with a unified relational formulation, the per-skill policies share the same observation space, action space, and network structure. Distilling them into a single unified policy is therefore a straightforward consequence of the framework." (§3.3)
(한글 해설 — 다중 스킬 증류에서 보통 필요한 특수 기법이 여기서는 불필요하다는 주장입니다. 학습 중 정책을 굴려 상태를 수집하고, 그 상태에 대한 per-skill 전문가 행동을 질의해 MSE 모방 손실로 학습합니다. 환경은 유효한 (물체, 스킬) 쌍 전체에 균등 분포시킵니다.)

### 학습 셋업

- **시뮬레이터 / 주기** — IsaacGym, 시뮬레이션 120 Hz, 제어 20 Hz. per-skill 전문가는 PPO, 증류는 DAgger.
- **PPO 하이퍼파라미터 (Table 6)** — 할인 계수 $`\gamma`$ 0.99, GAE $`\lambda`$ 0.95, 학습률 0.005, KL threshold 0.02, truncate gradients True, max gradient norm 1.0, mini epochs 5, batch size 32768. 에피소드 길이는 rotation 400 / 기타 스킬 64, horizon length 는 grasp & relocate 64 / rotation & translation 8.
- **DAgger 하이퍼파라미터 (Table 7)** — batch size 16384, 학습률 3.0e-4, 최대 epoch 3500, epoch 당 gradient update 100, rollout steps 32, replay buffer 1.0e6, expert query rate 100%.
- **보상 계수 (Table 8)** — grasp 와 나머지 스킬 사이 접촉 계열 계수가 100배 차이납니다: $`w_{\text{dis}}`$ 20.0(grasp) / 0.2(기타), $`w_{\text{con}}`$ 0.75 / 0.075, $`w_{\text{f}}`$ 0.05 / 0.005. 운동 항 계수 $`w_{\text{p}}`$ 는 grasp & relocate 0.0, rotation 1.0, translation 10.0. 추적 항은 $`w_{opr}`$ −5.0, $`w_{oqr}`$ −1.0, $`w_{oph}`$ −5.0, $`w_{oqh}`$ −1.0, $`w_{hpr}`$ −15.0, $`w_{hqr}`$ −3.0. 정규화 항은 $`w_{\text{pose}}`$ −0.3, $`w_{\text{vel}}`$ −0.5, $`w_{\text{ang}}`$ −0.05, $`w_{\tau}`$ −0.1, $`w_{\text{drop}}`$ −10.0.
- **물체 (§4.1.1)** — 박스와 원기둥을 두 범주로 무작위 샘플링합니다. wrappable 물체는 모든 치수가 $`[0.045,0.075]`$ m, elongated 물체는 길이 $`[0.6,0.8]`$ m · 나머지 치수 $`[0.045,0.065]`$ m. grasping · relocation 은 두 범주 모두, rotation 은 전자, translation 은 후자에서 학습·평가합니다. 범주 × 물체 유형마다 200개(학습 100 / 테스트 100)를 샘플링해 학습 400 · 테스트 400개를 얻습니다.
- **도메인 랜덤화 (Appendix C)** — 물체 질량 $`[0.002,0.04]`$ kg, 접촉 마찰 계수 $`[0.3,3.0]`$ (손·물체 양쪽 동일 적용), 관절 위치 관측에 $`\epsilon_{q}\sim\mathcal{U}(-0.02,0.02)`$ rad 의 i.i.d. 균등 노이즈. 외란력은 $`\mathbf{f}=2.0\,m_{\mathrm{obj}}\,\boldsymbol{\epsilon}_{f}`$ , $`\boldsymbol{\epsilon}_{f}\sim\mathcal{N}(\mathbf{0},\mathbf{I}_{3})`$ 로 샘플링하고, 시뮬레이션 스텝마다 0.9 로 감쇠시키거나 확률 $`0.25`$ 로 새 값으로 교체합니다.
- **초기 손가락 자세 (Appendix E)** — 후속 인핸드 조작이 가능한 잡기 자세가 생성되도록 초기 손가락 자세를 설계합니다. wrappable 물체는 손가락이 여러 방향을 감싸도록, elongated 물체는 양쪽에 최소 두 손가락이 놓이도록 합니다. Allegro · MANO 각각에 대한 16 / 20차원 관절각 초기값이 부록에 명시됩니다.

---

## 📊 실험 설정과 결과

**평가 프로토콜 (§4.1.2).** grasping 은 물체당 테이블 위 무작위 자세 25개, 손목은 물체 위 5 cm 에서 시작해 75 스텝 실행하고 50 스텝 후 손목에 고정된 상방 힘을 가해 들어 올립니다. 성공은 에피소드 전 구간에서 낙하 없이 들어 올린 경우입니다. relocation 은 성공한 잡기 자세 25개에서 시작해 x·y 로 $`[-0.1,0.1]`$ m, z 로 $`[0.2,0.4]`$ m, roll·pitch·yaw 로 $`[-0.75,0.75]`$ rad 오프셋을 준 목표를 75 스텝 안에 추적하며, 위치 오차 PE(cm) · 자세 오차 AE(rad)는 마지막 25 스텝 평균, 성공은 3 cm · 0.15 rad 이내입니다. rotation · translation 은 방향별 25 trial(회전 150 · 이동 50)이며 손목 자세를 세계 좌표에서 무작위 초기화합니다. 성공 기준은 400 스텝 내 $`\pi/2`$ rad 초과 회전 또는 50 스텝 내 5 cm 초과 이동입니다.

**per-skill baseline 비교 (Table 2).** grasping 은 GraspXL, rotation 은 RotateIt, translation 은 Yin et al. 의 teacher policy 를, relocation 은 선행 연구가 없어 잡기 자세를 조인 뒤 PD 컨트롤러로 손목을 목표로 구동하는 naive baseline 을 씁니다. 손은 Allegro 입니다. Ori. 는 baseline 자신의 원래 셋업(테이블 충돌 없는 grasping, 손목을 위로 고정한 in-hand), Gen. 은 본 논문의 일반 셋업입니다.

| Method | Grasp SR ↑ | Relocate SR ↑ | PE ↓ | AE ↓ | Rotate SR ↑ | Rot. ↑ | Translate SR ↑ | Trans. ↑ |
|---|---|---|---|---|---|---|---|---|
| Ori. (Base.) | 97.5 | – | – | – | 76.5 | 15.4 | 98.3 | 12.8 |
| Ori. (Ours) | 98.9 | – | – | – | 99.1 | 15.8 | 99.4 | 18.1 |
| Gen. (Base.) | 97.1 | 92.8 | 0.85 | 0.0231 | 62.7 | 9.43 | 70.6 | 5.81 |
| Gen. (Ours) | **98.7** | **99.0** | **0.54** | **0.0134** | **98.8** | **13.6** | **99.1** | **20.3** |

여기서 결정적인 비대칭이 있습니다. baseline 은 Ori. 와 Gen. 각각에 대해 따로 학습되지만, 본 논문 정책은 일반 셋업에서 학습한 **단 하나의 cross-skill 정책을 재학습 없이 양쪽에서 평가**합니다.

> "Although our single policy is never trained under baseline settings, it consistently outperforms the per-skill baselines that are specifically designed and trained for that setting." (§4.2, Table 2)
(한글 해설 — Ori. 열에서 rotation 76.5% → 99.1%, translation 98.3% → 99.4% 로, baseline 이 유리한 조건에서조차 단일 정책이 앞섭니다. 통일 형식이 per-skill 특화에 대한 성능 희생이 아니라는 것이 이 비교의 요지입니다.)

> "Moving to our more general setting, the rotation and translation baselines drop sharply even after retraining. This is mainly because they rely heavily on finger or palm support rather than stably holding the object." (§4.2)
(한글 해설 — rotation 76.5 → 62.7, translation 98.3 → 70.6 의 붕괴는 성능 문제가 아니라 가정의 문제입니다. 손바닥 지지에 의존하는 정책은 손바닥이 위를 향하지 않는 순간 물체가 미끄러지거나 떨어집니다. 반대로 본 논문 정책은 후속 인핸드 조작과 호환되는 잡기 자세에서 출발해 전 구간 물체를 붙잡고 있으므로 이 붕괴가 없습니다.)

**일반화·강건성 (Table 3).** 미학습 기하 테스트셋은 구 100개 · 육각기둥 100개(모든 치수 $`[0.045,0.075]`$ m)와 팔각기둥 200개(직경 $`[0.045,0.065]`$ m, 길이 $`[0.6,0.8]`$ m)입니다. 손 형상 일반화는 MANO(26 DOF, 손가락당 4 + 손목 6, CPF 관절 정의)와 Sharpa Wave(5지 28 DOF, 손목 6)로 각각 별도의 단일 정책을 학습해 검증하며, 작은 손 크기에 맞춰 모든 물체를 0.7배로 스케일합니다. 외란 실험은 에피소드 리셋마다 무작위 방향 · 크기 $`[0,10m_{\mathrm{obj}}g]`$ 의 힘을 물체에 가합니다(grasping 은 들어 올리는 동안, 나머지는 전 구간).

| Setting | Grasp SR ↑ | Relocate SR ↑ | PE ↓ | AE ↓ | Rotate SR ↑ | Rot. ↑ | Translate SR ↑ | Trans. ↑ |
|---|---|---|---|---|---|---|---|---|
| Allegro | 98.7 | 99.0 | 0.54 | 0.0134 | 98.8 | 13.6 | 99.1 | 20.3 |
| Allegro (Uns.) | 95.8 | 98.6 | 0.50 | 0.0152 | 98.3 | 14.5 | 96.0 | 18.1 |
| MANO | 96.8 | 96.6 | 1.26 | 0.0207 | 94.5 | 10.3 | 95.3 | 10.3 |
| Sharpa Wave | 99.1 | 98.0 | 0.80 | 0.0116 | 98.5 | 13.5 | 99.0 | 17.8 |
| Allegro (Dis.) | 98.6 | 99.0 | 0.55 | 0.0136 | 98.4 | 13.7 | 97.6 | 20.2 |

미학습 기하에서 가장 큰 하락은 grasping(98.7 → 95.8)과 translation(99.1 → 96.0)이며, rotation 은 오히려 평균 회전각이 13.6 → 14.5 rad 로 증가합니다. 손 형상 중에서는 MANO 만 눈에 띄게 떨어지고(relocation PE 0.54 → 1.26 cm, rotation 각 13.6 → 10.3 rad), 저자는 MANO 의 관절 가동 범위가 더 제한적인 탓으로 설명합니다. Sharpa Wave 는 grasping 99.1% · AE 0.0116 으로 Allegro 보다 오히려 나은 항목이 있습니다. 외란 조건에서는 rotation · translation 의 하락이 grasping · relocation 보다 약간 큽니다.

> "As shown in Tab. 3 (Allegro (Dis.)), rotation and translation show slightly larger performance drops than grasping and relocation, as stably constraining the object is more challenging during relative hand-object motion." (§4.4, Table 3)
(한글 해설 — 상대 운동 중에는 접촉을 계속 재구성해야 하므로 외란에 취약해지는 것이 자연스럽습니다. 다만 실제 하락 폭은 translation 99.1 → 97.6 수준으로 작아, "물체를 계속 붙잡는다"는 형식의 목표가 외란 하에서도 유지된다는 주장을 뒷받침합니다.)

![Figure 3 — cross-morphology & unseen-geometry qualitative results](https://arxiv.org/html/2607.28198/x2.png)

> "Figure 3: Qualitative results on different hand morphologies and geometrically irregular non-convex unseen objects." (§4.3.1)
(한글 해설 — Table 3 의 수치가 실제로 어떤 손·물체 조합에서 나온 것인지 보여줍니다. 비볼록·불규칙 기하에서도 동일 정책이 작동한다는 §4.3.1 의 일반화 주장을 시각화합니다.)

또한 저자는 정책이 물체 기하에 따라 손가락 운동 패턴을 바꾼다고 보고합니다(둥근 물체는 부드러운 감싸기, 각기둥은 모서리를 의식한 주기적 운동), 다만 이는 보충 영상 기반 정성 관찰이며 수치 근거는 제시되지 않습니다.

**장기 연쇄 (Table 4).** grasp + relocate + rotate 와 grasp + relocate + translate 두 시퀀스를 물체당 25개 무작위 테이블 자세로 평가하며, 세 단계가 모두 성공해야 시퀀스 성공으로 셉니다.

| Sequence | Grasp SR ↑ | Relocate SR ↑ | In-hand SR ↑ | Overall SR ↑ |
|---|---|---|---|---|
| Gr. + Re. + Rot. | 99.7 | 92.2 | 95.1 | 87.4 |
| Gr. + Re. + Trans. | 99.9 | 98.3 | 98.0 | 96.3 |

> "The rotation success rate is lower than in the per-skill evaluation because, after relocation, the hand starts from downward or diagonally downward orientations rather than from randomly sampled ones, making the task inherently more challenging as the object is more prone to slipping or dropping." (§4.5)
(한글 해설 — 단일 스킬 평가의 98.8% 와 연쇄 내 95.1% 의 차이는 정책 열화가 아니라 초기 상태 분포의 이동에서 옵니다. 옮기기가 끝난 뒤 손은 아래 또는 사선 아래를 향하고 있어 중력이 불리하게 작용합니다. 또 옮기기가 잡기 직후 시작되므로 잡기 단계의 잔여 운동이 옮기기를 교란해 92.2% 로 떨어집니다.)

**Ablation (Table 5).** 목표 조건부 요소 3종(목표 자세 관측 $`\mathbf{g}_{t}^{\text{target}}`$ , 추적 보상 $`r_{t}^{\text{track}}`$ , 잔차 손목 행동)과 물체 표현 2종(거리 벡터, 접촉 상태)을 제거하고, 증류 전 10개 전문가와도 비교합니다.

| Method | Grasp SR ↑ | Relocate SR ↑ | PE ↓ | AE ↓ | Rotate SR ↑ | Rot. ↑ | Translate SR ↑ | Trans. ↑ |
|---|---|---|---|---|---|---|---|---|
| W/o Tar. Obs. | 96.0 | 98.2 | 0.60 | 0.0158 | 98.6 | 13.1 | 98.9 | 19.5 |
| W/o Tar. Act. | 94.5 | 37.4 | 2.95 | 0.1828 | 98.5 | 12.7 | 96.1 | 19.7 |
| W/o Tar. Rew. | 98.5 | 62.9 | 5.47 | 0.0176 | 98.4 | 13.5 | 91.9 | 20.1 |
| W/o Distance | 96.7 | 98.9 | 0.58 | 0.0134 | 96.5 | 12.2 | 98.8 | 16.4 |
| W/o Contact | 96.9 | 99.0 | 0.55 | 0.0129 | 82.7 | 8.78 | 98.1 | 14.4 |
| Experts | 99.0 | 99.1 | 0.53 | 0.0140 | 99.1 | 14.1 | 99.3 | 20.5 |
| Ours | 98.7 | 99.0 | 0.54 | 0.0134 | 98.8 | 13.6 | 99.1 | 20.3 |

각 행이 분리해 보여주는 것은 다음과 같습니다.

- **W/o Tar. Act.** — 손목 기준점을 손가락과 동일하게 $`\mathbf{q}_{t-1}^{\text{act}}`$ 로 바꾼 변형입니다. relocation 이 99.0 → 37.4%, PE 0.54 → 2.95 cm, AE 0.0134 → 0.1828 rad 로 붕괴하는 반면 rotation 은 98.8 → 98.5% 로 사실상 무변화입니다. 큰 진폭 손목 이동을 요구하는 스킬만 선택적으로 무너지므로, 이 항목은 **행동 파라미터화의 신체 부위별 비대칭이 어느 스킬에 값하는지**를 정확히 격리합니다.
- **W/o Tar. Rew.** — 추적 보상 제거 역시 relocation 을 62.9% / PE 5.47 cm 로 떨어뜨립니다. 정확한 자세 정합이 필요 없는 나머지 스킬은 $`r_{t}^{\text{goal}}`$ 만으로도 상호작용 목표가 유지되어 덜 떨어집니다. 즉 추적 보상은 "목표 자세 도달형" 스킬 전용 신호입니다.
- **W/o Tar. Obs.** — 세 변형 중 하락이 가장 작습니다(grasp 98.7 → 96.0). 저자 설명대로 과제 축 $`\mathbf{d}^{\text{h}}`$ 가 남아 상대 운동 목표 정보를 여전히 전달하기 때문입니다. 55차원 목표 벡터 중 3차원 축 벡터가 정보량의 상당 부분을 담당한다는 뜻으로 읽힙니다.
- **W/o Contact** — 링크별 접촉 상태를 빼면 rotation 이 98.8 → 82.7%, 회전각 13.6 → 8.78 rad 로 가장 크게 무너지고 relocation 은 99.0% 로 무변화입니다. 손가락 재구성이 거의 없는 스킬은 접촉 정보가 필요 없고, 접촉을 계속 끊었다 붙여야 하는 스킬만 이 채널에 의존한다는 명확한 대비입니다.
- **W/o Distance** — 거리 벡터 제거는 rotation(98.8 → 96.5, 각 13.6 → 12.2)과 translation 거리(20.3 → 16.4 cm)를 낮춥니다. 성공률보다 **운동량 지표**가 더 크게 깎이는 패턴입니다.

> "Although multi-skill distillation typically incurs degradation, our policy closely matches the experts on all four skills." (§4.6, Table 5)
(한글 해설 — Experts 행과 Ours 행의 차이는 grasp 0.3%p, relocation 0.1%p, rotation 0.3%p, translation 0.2%p 로 사실상 무손실입니다. 저자는 이를 성능 주장이 아니라 **형식 주장의 증거**로 씁니다 — 스킬들이 서로 충돌하지 않고 호환적이기 때문에 동일 용량의 단일 네트워크가 vanilla DAgger 만으로 넷을 모두 담아낸다는 것입니다.)

![Figure 6 — Sharpa Wave long-horizon manipulation](https://arxiv.org/html/2607.28198/x5.png)

> "Figure 6: Sharpa Wave long-horizon manipulation" (§Appendix D)
(한글 해설 — Table 4 의 장기 연쇄가 Sharpa Wave 손에서 어떻게 실행되는지 보여주는 정성 결과입니다. PROBE 의 근시일 목표 하드웨어와 동일 계열 손이라 참조 가치가 높습니다.)

---

## ⚖️ 한계

- **(A) 실물 로봇 검증이 전무** — 전 실험이 IsaacGym 안에서 끝납니다. 도메인 랜덤화는 걸려 있지만 실환경 전이 실험도, 실물 하드웨어도 논문에 등장하지 않습니다. 통일 형식의 주장은 시뮬레이션 내부에서만 검증된 것이며, 특히 관측이 시뮬레이터 특권 정보에 크게 의존하므로(아래 B) "형식이 옳다"와 "이 정책을 로봇에 올릴 수 있다"는 별개의 명제로 남습니다.
- **(B) 관측 전체가 특권 정보** — 물체 표현 $`[\mathbf{c}_{t},\mathbf{f}_{t},\mathbf{v}_{t}]`$ 의 거리 벡터는 각 손가락 링크에서 물체 표면 최근접점까지의 벡터로, 물체 기하와 자세를 모두 아는 시뮬레이터만 계산할 수 있습니다. 목표 특징 $`\mathbf{g}_{t}`$ 의 두 프레임 물체 자세도 마찬가지입니다. 논문은 이를 한계로 명시하지 않지만, ablation 이 rotation 성능의 상당 부분을 이 채널들에 귀속시키고 있어(W/o Contact 82.7%, W/o Distance 96.5%) 실환경에서 이 정보를 어떻게 대체할지가 미해결로 남습니다.
- **(C) 물체 범위가 강체 기본 도형에 한정** — 학습은 박스·원기둥, 미학습 평가는 구·육각기둥·팔각기둥입니다. 모두 강체이며 관절 물체·도구·변형체가 없습니다. 저자들이 서론에서 동기로 든 플러그 삽입, 나사 조이기, 칼질 같은 과제는 물체가 환경과 접촉하거나 관절 자유도를 갖는데, 그런 상황은 실험에 등장하지 않습니다. 즉 동기와 검증 사이에 간극이 있습니다.
- **(D) 질량 범위가 비현실적으로 가벼움** — 도메인 랜덤화 질량이 $`[0.002,0.04]`$ kg 입니다. 길이 0.6–0.8 m · 단면 4.5–6.5 cm 인 elongated 물체가 최대 40 g 이라면 밀도가 스티로폼 수준입니다. 인핸드 이동·회전에서 중력 토크가 거의 작용하지 않는 조건이므로, 접촉 유지 난도가 실제 도구·부품 조작보다 구조적으로 낮게 설정되어 있습니다. 외란 실험의 $`10m_{\mathrm{obj}}g`$ 도 상대적으로는 크지만 절대값으로는 최대 약 4 N 에 불과합니다.
- **(E) 스킬 전환이 정책 내부에서 자율적으로 일어나지 않음** — 관측의 one-hot $`\mathbb{I}_{t}`$ 와 축 벡터 $`\mathbf{d}^{\text{h}}`$ 가 외부에서 주어져야 합니다. 장기 연쇄 실험도 grasp → relocate → in-hand 순서를 사람이 정해 주입한 것입니다. "언제 스킬을 바꿀지"를 결정하는 상위 계층은 이 논문 범위 밖이며, 논문이 주장하는 "seamless chaining" 은 *전환 시 상태가 유효하다*는 의미이지 *전환을 스스로 결정한다*는 의미가 아닙니다.
- **(F) 성공 기준이 관대한 축이 있음** — rotation 성공은 400 스텝(20 Hz 기준 20초) 내 $`\pi/2`$ rad 이며, 보고되는 평균 회전각 13.6 rad 은 약 2.2 회전에 해당합니다. 회전 속도(rad/s) 기준으로 보면 인핸드 회전 문헌의 통상 지표와 직접 비교하기 어려운 형태이고, 성공률이 99% 대로 포화되어 있어 이 지표만으로는 방법 간 변별력이 약합니다.
- **(G) 손 형상 일반화의 실제 범위** — 세 손 모두 **6-DoF 가상 손목 관절을 갖는 free-floating 손**입니다. 형상 일반화는 손가락 수·관절 배치의 차이를 커버하지만, 손목이 팔에 물려 있어 자유롭게 움직일 수 없는 실제 마운트 조건은 다루지 않습니다. relocation 스킬 자체가 자유 손목을 전제로 정의되어 있습니다.

---

## ♻️ 재현성

- **코드 / 데이터** — 확보한 arXiv HTML 본문(부록 포함)에는 코드 저장소 링크가 없습니다. 명시된 것은 프로젝트 페이지 `https://zdchan.github.io/UniCross/` 뿐이며, 본 실행 환경의 네트워크 정책이 해당 호스트 CONNECT 를 거부해(`curl -L --fail -sS https://zdchan.github.io/UniCross/` → HTTP 403, 프록시 policy denial) 코드·가중치 공개 여부를 확인하지 못했습니다. 데이터셋 공개는 해당 없음 — 물체는 절차적으로 샘플링된 박스·원기둥이며 외부 자산 의존이 없습니다.
- **하드웨어** — 실물 로봇 없음. 시뮬레이션 손 모델은 Allegro, MANO(CPF 관절 정의로 26 DOF 시뮬레이션 가능 모델을 직접 구축), Sharpa Wave(5지 28 DOF). 학습 GPU 사양·학습 시간·시드 수는 본문·부록 어디에도 명시되지 않습니다.
- **재현에 필요한 값의 공개 수준** — 높은 편입니다. PPO(Table 6)·DAgger(Table 7)·보상 계수(Table 8) 전체, 도메인 랜덤화 범위(Appendix C), 초기 손가락 관절각 실수값(Appendix E), 네트워크 은닉 차원([128, 64] / [512, 256, 128])이 모두 수치로 제시됩니다.
- **본문 미명시 항목** — 행동 스케일 $`\boldsymbol{\alpha}`$ 의 구체값, 관절 한계 $`\mathbf{q}_{\min}`$ · $`\mathbf{q}_{\max}`$ , PD 컨트롤러 게인, 운동 항 상한 $`v_{\max}`$ 와 회전 목표 갱신 각속도 $`\omega_{\max}`$ , 낙하 판정 거리 임계, 병렬 환경 수, 학습 스텝 수는 확보 본문에서 확인되지 않습니다.
- **라이선스** — arXiv 페이지 기준 arXiv.org perpetual non-exclusive license(논문 문서).

---

## 🎯 관련 Pillar / Decision (P# / D#)

본 논문은 PROBE 의 **P3(Hand-level System0 Module, RL-scoped)** 에 가장 직접적으로 맞닿고, **P1(Heterogeneous Body/Hand Action Expert)** 과 **P2(Structured Multimodal Observation Fusion)** 에 각각 한 개씩의 구체적 증거를 제공합니다.

- **P3 / D13(System0 role & operating regime)·D15(System0 input modality)·D16(System0 output form)·D17(System0 RL policy spec)** — 논문의 문제 정의 자체가 "물체를 손에 안정적으로 붙잡은 채 상대 운동을 만든다"이며, 이는 D13 의 v1 인 "post-grasp maintenance · in-hand stable-contact maintenance" 와 사실상 동일한 작동 영역입니다. 관측에서 **시각이 완전히 배제**되고 관절 상태 + 링크별 접촉·접촉력만 쓰는 구성은 D15 v1 의 "vision excluded" 설계와 일치합니다. 출력은 손가락(+손목) 관절 목표 명령의 증분이라 D16 v1 (direct finger joint command)과 맞습니다. D17 v1 이 지정한 PPO · 접촉 인지 보상 · 낙하 종료 구성이 그대로 구현되어 있어, 보상 항 구조와 계수(Table 8)는 직접 참조값입니다.
- **P3 / D18(System0 sim2real) — 지지 근거가 아님** — 도메인 랜덤화는 있지만 실물 전이 실험이 없습니다. 마찰은 정적/동적 구분 없이 단일 계수 $`[0.3,3.0]`$ 로 랜덤화되어 D18 v1 이 채택한 정적/동적 마찰 분리(arXiv:2503.01255)보다 후퇴한 형태이고, RMA 계열 teacher-student 도 쓰지 않습니다. 본 논문은 D18 의 근거로 인용해서는 안 됩니다.
- **P1 / D3(Hand output space)·D5(Input-modality + control-rate separation)** — W/o Tar. Act. ablation 이 P1 에 주는 값이 큽니다. 손목과 손가락에 **동일한 행동 공간을 쓰되 증분의 기준점만 해부학적으로 다르게** 둔 것만으로 relocation 성공률이 37.4% ↔ 99.0% 로 갈립니다. 이는 "신체 부위별 이질적 액션 파라미터화가 실제로 값한다"는 D1/D3 계열 가설에 대한 저비용·고분해능 증거입니다. 다만 손목·손가락이 **동일 제어 주기(20 Hz)** 를 공유하므로 D5 v1 의 (α) shared rate 와 정합적이고, 제어율 분리에 대한 근거는 제공하지 않습니다.
- **P2 / D11(Proprio-tactile-force token construction)·D12(topology-aware encoding)** — 물체 표현 $`[\mathbf{c}_{t},\mathbf{f}_{t},\mathbf{v}_{t}]`$ 는 **링크 단위 접촉 이진값 + 접촉력 크기**로, D11 v1 의 "per-finger proprio-tactile binding, contact-binary aux head" 가 지키려는 정보와 정확히 같은 종류입니다. W/o Contact ablation(rotation 98.8 → 82.7%)은 D11 의 비협상 조건인 "접촉 관련 특징 보존"에 대한 정량 근거가 됩니다. 다만 이 채널들은 flat concat 으로 MLP 에 들어가므로 **D10(cross-attention 융합)의 근거는 아닙니다** — 오히려 flat concat 으로도 이 정도가 된다는 반례 쪽에 가깝고, 그 대신 정보 *내용*(무엇을 토큰에 담아야 하는가)에 대한 근거를 줍니다.
- **P0 / P4 / P5 — 무관** — 데이터셋·벤치마크 공개가 없어 P0 와 무관하고, VLM 백본·사전학습·PEFT 가 전혀 없어 P4 와 무관하며, 예측 모델·상상 속 롤아웃이 없어 P5 와도 무관합니다. 연결을 만들지 않겠습니다.
- **Identity 긴장/지지** — 논문은 네 가지 스킬을 강화학습으로 직접 학습하므로 표면적으로 Identity 의 *Antagonist B*(RL-as-core)에 해당합니다. 다만 다루는 과제는 언어 조건부 일반 과제가 아니라 "물체를 놓치지 않고 지정된 축으로 상대 운동을 만든다"는 명백히 reward-engineerable 한 영역이며, 이는 PROBE 가 RL 을 허용한 유일한 범위(System0)와 정확히 겹칩니다. 따라서 프레이밍은 Identity 와 충돌하지 않고, **방법론은 System0 로 흡수 가능**합니다. 다른 한편 "하나의 형식으로 전부 통일한다"는 논문의 주장은 PROBE 의 이질적 분할(D1 hybrid trunk + split heads)과 표면적으로 반대 방향으로 들리지만, 논문의 통일은 *스킬* 축의 통일이고 그 내부에서 손목/손가락 행동 기준점은 오히려 이질적으로 두었습니다. 결과적으로 해부학적 이질성 주장을 약화시키지 않습니다.
- **경쟁자 함의** — 저자 소속에 **inspire AG**(취리히)가 포함되고 평가 손에 **Sharpa Wave** 가 들어 있습니다. PROBE 의 근시일 하드웨어(Sharpa Hand)와 같은 계열 손이 학계 벤치마크에 등장했다는 점은 하드웨어 선택의 검증 신호이자, 동일 손 위에서 인핸드 조작을 다루는 그룹이 존재한다는 신호입니다.

---

## ✨ 핀 논문 대비 델타

- **HORA(arXiv:2210.04887) 대비 (P3 핀, D17/D18)** — HORA 는 인핸드 회전 + RMA + 특권→촉각 증류로 P3 에 핀되어 있습니다. UniCross 의 진짜 델타는 **손목 자세 가정의 제거**입니다. 회전·이동 평가에서 손목 자세를 세계 좌표에서 무작위 초기화하고, 손바닥 지지 없이 물체를 붙잡은 채 회전합니다. 반대로 sim2real 축에서는 HORA 가 우위입니다 — UniCross 에는 teacher-student 증류도, 실물 전이도 없습니다. 두 논문은 "무엇을 없앴는가"가 정확히 반대입니다(HORA 는 특권 정보를 없앴고, UniCross 는 스킬 특화 셋업을 없앴습니다).
- **AnyRotate(arXiv:2405.07391) 대비 (D17 보상 항 참조)** — AnyRotate 는 보상 항 구조의 직접 참조로 등재되어 있습니다. UniCross 의 보상은 접촉 항 + 과제 축 사영 운동 항 + **두 기준계 목표 자세 추적 항**의 3층 구조이며, 이 중 추적 항이 새로운 요소입니다. 이 항 덕분에 회전뿐 아니라 잡기·옮기기까지 하나의 보상 뼈대로 커버됩니다. 즉 델타는 보상 항의 정교함이 아니라 **보상의 스킬 커버리지**입니다.
- **VE2VF(arXiv:2605.29564) 대비 (P3 핀, D14–D17)** — VE2VF 는 vision-enabled → vision-free 증류를 실세계 강화학습으로 ~50분 만에 수행하는 near-direct System0 아날로그입니다. UniCross 의 증류는 축이 다릅니다 — 모달리티 축이 아니라 **스킬 축의 증류**(전문가 10개 → 1개)이며, 그 결과가 near-lossless 라는 것이 논문의 주장입니다. 두 증류는 상호 배타적이지 않아, System0 설계에서는 "스킬 축 통합(UniCross) → 모달리티 축 축소(VE2VF)"의 2단 구성이 자연스럽게 조합됩니다.
- **Beyond Binary(arXiv:2605.28812) 대비 (P3 핀, D18)** — Beyond Binary 는 접촉을 물리 기반 CoP(3D 힘 벡터 + 3D 접촉 위치)로 표현해 시뮬레이션·하드웨어를 정렬합니다. UniCross 의 접촉 표현은 접촉 이진값 + **힘 크기(스칼라)** + 거리 벡터로, 방향 정보가 없고 하드웨어 정렬도 시도하지 않습니다. 표현 충실도·전이성 축에서는 Beyond Binary 가 명백히 앞서며, UniCross 의 기여는 표현이 아니라 그 위의 **과제 형식**에 있습니다. 두 논문을 겹치면 "CoP 관측 + UniCross 목표 형식"이라는 조합이 곧바로 도출됩니다.
- **P1 Demystifying Action Space Design(arXiv:2602.23408) 대비** — 해당 논문은 13k+ 실제 롤아웃으로 joint 대 task 공간의 안정성/일반화 트레이드오프를 다룹니다. UniCross 의 델타는 공간의 *선택*이 아니라 **증분 기준점의 선택**이라는 한 단계 아래 층위이며, 같은 관절 공간 안에서 기준점만 바꿔도 특정 스킬이 붕괴함을 보입니다. 실물이 아닌 시뮬레이션 근거라는 점에서 증거 등급은 낮습니다.
- **종합** — 핀들 대비 UniCross 의 단일 최대 델타는 "**접촉 체제가 아니라 손-물체 상대 운동을 기준으로 스킬을 정의하면, 잡기부터 인핸드 조작까지가 하나의 관측·행동·보상 규격에 들어가고 스킬 연쇄가 공짜로 따라온다**"입니다. 반대로 표현 품질(Beyond Binary)과 실환경 전이(HORA·VE2VF) 축에서는 핀들보다 뒤에 있습니다.

---

## ⚙️ 의사결정 함의

- **D14(System1↔System0 인터페이스) — 대안 인터페이스 후보 추가** — 현재 v1 은 이진 `maintain_grasp` on/off 입니다. UniCross 는 같은 자리에 **과제 모드 one-hot(10차원) + hand frame 과제 축 단위 벡터(3차원)** 를 넣습니다. System1 이 "지금 붙잡아라"만이 아니라 "지금 z+ 축으로 물체를 굴려라"까지 전달할 수 있게 되므로, System0 가 단순 유지 모듈에서 방향성 있는 안정화 모듈로 확장됩니다. 구현 수준: System0 관측에 `task_mode_onehot`(R^K) + `task_axis_hand_frame`(R³) 를 추가하고, 보상의 운동 항을 $`w_{\text{p}}\cdot\min(\mathbf{v}_{o}^{h}\cdot\mathbf{d}^{\text{h}},v_{\max})`$ 형태로 둡니다. 다만 W/o Tar. Obs. ablation 이 보이듯 축 벡터 3차원만으로도 상당 부분이 전달되므로, **최소 구현은 축 벡터만 추가하는 것**입니다.
- **D17(System0 RL 정책 스펙) — 보상 계수의 스킬 의존 스케일링** — 가장 이식 가치가 높은 수치는 접촉 계열 계수의 **100배 스케일 차이**입니다: $`w_{\text{dis}}`$ 20.0(grasp) vs 0.2(인핸드), $`w_{\text{con}}`$ 0.75 vs 0.075, $`w_{\text{f}}`$ 0.05 vs 0.005. 접촉을 재구성해야 하는 국면에서 접촉 유인 보상을 그대로 두면 손가락이 붙어버려 회전이 멈춘다는 뜻입니다. System0 가 D13 의 세 역할(slip 예측 / 파지 유지 / 손가락 자세 미세 보정) 사이를 오갈 때 **접촉 유인 가중치를 게이트 신호에 따라 두 자릿수 스케일로 전환**하는 설계를 검토할 값이 있습니다. 함께 이식 가능한 값: 낙하 페널티 −10.0, 초기 자세 이탈 페널티 −0.3, 토크 페널티 −0.1, 손목 병진/각속도 페널티 −0.5 / −0.05.
- **D17 — PPO 설정과 horizon 분리** — 학습률 0.005, KL threshold 0.02, batch 32768, mini epochs 5, $`\gamma`$ 0.99, GAE $`\lambda`$ 0.95 는 System0 PPO 초기값의 참조점입니다. 특히 **horizon length 를 스킬별로 분리**(grasp/relocate 64, 인핸드 8)한 선택은, 접촉 재구성이 잦은 과제에서 짧은 rollout 이 유리함을 시사합니다. System0 는 정의상 인핸드 국면에서 작동하므로 horizon 8 계열을 기본값 후보로 둡니다.
- **D15(System0 입력 모달리티) — 관측 벡터 구성** — 논문의 손 상태는 `[q_t, q_target_{t-1}]`, 즉 현재 관절 위치와 **직전 목표 관절 위치**입니다. 속도·토크를 넣지 않고 직전 명령을 넣는 이 선택은 D15 v1 (관절 위치 + 속도 + 토크 + 접촉 이력)보다 가볍고, 명령-실현 격차를 정책이 직접 관측하게 만듭니다. 저비용 A/B 후보입니다. 물체 채널은 링크별 `contact_binary` + `contact_force_magnitude` 까지만 우리 하드웨어에서 재현 가능하며, 거리 벡터 $`\mathbf{v}_{t}`$ 는 재현 불가이므로 대체가 필요합니다(아래 ⚠️ 참조).
- **D13(System0 역할) — 범위 확장 검토** — v1 은 "인핸드 안정 접촉 유지"까지를 System0 로 봅니다. 본 논문은 그 범위에서 **능동적 인핸드 회전·이동까지** 하나의 정책으로 처리되며 잡기·옮기기와도 상태 호환이 유지됨을 보입니다. Phase 1 데모(인핸드 큐브 회전)를 System0 단독으로 실행할 수 있는지에 대한 상향 근거이며, 동시에 "System0 를 어디까지 능동적으로 만들 것인가"라는 경계 재검토를 촉발합니다.
- **하드웨어 검증 신호** — Sharpa Wave(28 DOF, 손목 6)에서 grasp 99.1% · rotation 98.5% 로 Allegro 와 동급 이상입니다. PROBE 의 근시일 손(Sharpa Hand, 22-DOF, 손목 DOF 없음)은 손가락 자유도 수가 일치하며(28 − 6 = 22), **손목 6 DOF 를 팔이 제공한다는 전제**만 맞추면 본 형식이 그대로 적용될 가능성이 높습니다. 다만 이 전제가 곧 최대 전이 위험이기도 합니다(⚠️ 참조).

---

## ⚠️ 먼저 검증할 실패 모드

싼 검증부터 나열합니다.

1. **거리 벡터 $`\mathbf{v}_{t}`$ 는 우리 스택에서 존재하지 않습니다 (가장 싼 확인).** 각 손가락 링크에서 물체 표면 최근접점까지의 벡터는 물체 메시와 자세를 아는 시뮬레이터만 계산합니다. 실환경에서는 시각 기반 자세 추정이 필요한데 System0 는 정의상 시각을 배제합니다(D15). **검증**: 시뮬레이션에서 $`\mathbf{v}_{t}`$ 를 제거한 W/o Distance 설정을 우리 과제(큐브 회전)에 재현해 성능 하락을 측정합니다. 논문 수치는 rotation 98.8 → 96.5%, 회전각 13.6 → 12.2 rad 로 작아 보이지만, 우리 물체·질량 조건에서도 그런지가 관건입니다. 이 실험만으로 System0 관측 설계의 실현 가능성이 판정됩니다.
2. **손목 6-DoF 자유도 전제.** 세 손 모두 free-floating 손목을 가정합니다. PROBE 의 근시일 하드웨어는 손목 DOF 가 없고 손목 운동은 팔이 담당하며, 팔은 다른 제어 주기·지연·동역학을 갖습니다. relocation 스킬은 정의상 자유 손목이 없으면 성립하지 않고, 인핸드 회전·이동조차 "손목을 root frame 에 고정"하는 것을 *정책이 능동적으로 유지*합니다. **검증**: 가상 손목 관절을 동결(행동 차원에서 제외)하고 rotation/translation 만 재학습해 성능이 유지되는지 봅니다. 유지되면 System0 를 손목 없이 정의할 수 있고, 무너지면 손목-팔 결합 설계가 System0 선결 조건이 됩니다.
3. **질량 스케일 불일치.** 학습 질량이 2–40 g 입니다. 우리의 Phase 1 큐브와 Phase 2 도구(태깅 머신 등)는 그보다 한두 자릿수 무겁고, 중력 토크가 접촉 유지 난도를 지배합니다. 이 논문의 접촉 계수·낙하 임계·행동 스케일이 무거운 물체에서 그대로 통할 근거는 없습니다. **검증**: 동일 형식에서 질량만 0.2–1.0 kg 로 올려 인핸드 이동 성공률의 변화를 봅니다. 2번과 함께 묶어 한 번의 학습 스윕으로 처리 가능합니다.
4. **접촉 신호의 성질 차이.** 논문의 $`\mathbf{c}_{t}`$ · $`\mathbf{f}_{t}`$ 는 PhysX 가 보고하는 링크별 접촉 리포트로, 지연 없고 잡음 없고 자가 충돌·환경 접촉과 구분됩니다. 우리 하드웨어의 Deform Map 은 손끝당 320×240 시각 기반 · 30 Hz 이며, 지연·양자화·자가 접촉 오검출이 모두 존재합니다. W/o Contact ablation 이 rotation 98.8 → 82.7% 로 이 채널 의존도가 매우 높음을 보이므로, 신호 품질 저하가 곧바로 성능 저하로 이어질 위험이 큽니다. **검증**: 시뮬레이션 접촉 채널에 30 Hz 샘플링 + 측정된 센서 지연 + 이진화 임계 오차를 주입해 rotation 성능 곡선을 그립니다.
5. **제어 주기 20 Hz 는 System0 의 존재 이유와 충돌합니다.** PROBE 가 System0 를 두는 근거는 slip 대응이 정책 루프보다 빠른 반응을 요구하기 때문입니다. 그런데 본 논문의 제어는 20 Hz 로, 통상적인 System1 정책 주기와 다르지 않습니다. 즉 이 논문은 "빠른 안정화 루프"의 근거를 제공하지 않으며, 이식 시 주기를 올렸을 때 보상 계수·행동 스케일이 그대로 유효한지는 미검증입니다. **검증**: 동일 설정을 100–200 Hz 제어로 재학습해 행동 스케일 $`\boldsymbol{\alpha}`$ 재조정 없이 학습이 되는지 확인합니다.
6. **스킬 전환 신호의 출처.** one-hot 과 과제 축은 외부 입력입니다. 우리 스택에서는 System1(Hand expert)이 이 신호를 만들어야 하는데, 논문은 그 상위 계층을 다루지 않습니다. 장기 연쇄 87.4% 수치도 전환 시점을 사람이 정해 준 조건의 값입니다. **검증**: 전환 시점에 ±k 스텝의 지터를 주입해 연쇄 성공률이 얼마나 민감한지 측정합니다. 민감하다면 D14 인터페이스 설계에서 전환 타이밍 자체가 1급 설계 변수가 됩니다.
7. **증류 무손실성의 전제.** near-lossless 증류는 전문가들이 "호환적"이기 때문이라고 저자가 명시합니다. 우리 상황은 다릅니다 — System0 는 System1(모방 학습 기반 flow-matching 액션 전문가)과 공존해야 하며, 그쪽은 같은 형식의 질의 가능한 전문가가 아닙니다. expert query rate 100% 의 vanilla DAgger 는 성립하지 않습니다. **검증**: System0 만 이 형식으로 학습한 뒤, System1 롤아웃 상태 분포에서 System0 를 평가해 상태 분포 이동 하에서의 성능 저하를 측정합니다. 이는 위 1–6 이 통과한 뒤에 할 가장 비싼 실험입니다.
8. **과제 범위의 간극.** 학습·평가 물체에 관절 물체·도구·환경 접촉이 없습니다. Phase 2 의 도구 조작(도구를 쥔 채 손가락으로 트리거 조작)은 "물체가 손에 고정된 채 손가락 일부만 별도로 움직인다"는 다섯 번째 상대 운동 모드에 가까우며, 논문의 네 스킬 어디에도 해당하지 않습니다. **검증**: Tracked/Fixed/Free 배정표에 "물체 자세는 hand frame 에서 Fixed, 특정 손가락만 자유"라는 행을 추가해 형식이 확장되는지 시뮬레이션에서 확인합니다. 이 확장 가능성이 형식 채택 여부의 실질적 판단 근거입니다.

---

## 💡 컨텍스트 제안

- **P3 §5 Pinned 에 추가 제안** — 현재 P3 핀은 4/8 로 여유가 있습니다. UniCross 는 잡기 → 옮기기 → 인핸드 조작을 하나의 형식·단일 정책으로 잇는 유일한 참조이고, 평가 손에 Sharpa Wave 가 포함되어 하드웨어 정합성도 높습니다. 역할 문구 제안: `Cross-skill unified relational formulation; grasp→relocate→in-hand chaining, PPO+DAgger, Sharpa Wave 포함 3종 손 (D13/D14/D17)`. 다만 실물 전이가 없으므로 **D18 근거로는 인용 금지**를 역할 문구에 함께 남기는 편이 안전합니다.
- **P1 §5 Methodology base 에 추가 제안** — W/o Tar. Act. ablation(relocation 99.0 → 37.4%)은 신체 부위별 이질적 행동 파라미터화의 값을 격리한 드문 증거입니다. 역할 문구 제안: `손목/손가락 증분 기준점 비대칭 ablation — 이질적 액션 파라미터화 근거 (D3/D5, 시뮬레이션 한정)`.
- **D14(System1↔System0 인터페이스) — deferred 후보 등록 제안** — v1 의 이진 `maintain_grasp` 옆에 "과제 축 단위 벡터(hand frame, R³) 조건부" 를 deferred 대안으로 기록해 둘 값이 있습니다. 위 ⚠️ 2번(손목 동결)과 ⚠️ 6번(전환 타이밍 민감도) 실험이 통과하면 트리거되는 형태를 제안합니다.
- **D13(System0 역할) — 재검토 트리거 제안** — "System0 를 유지 전용으로 둘 것인가, 축 지정 능동 인핸드 조작까지 포함할 것인가"를 열린 질문으로 기록해 두시길 제안합니다. 트리거 조건: ⚠️ 1번(거리 벡터 제거) 실험에서 성능 하락이 5%p 이내로 확인될 때.
- **하드웨어 메모 (MASTER §4.1)** — Sharpa Wave(28 DOF, 손목 6)가 외부 논문 벤치마크에 등장했고 Allegro 와 동급 성능을 냈다는 사실은 하드웨어 선택의 외부 검증 신호입니다. 다만 그 28 DOF 는 손목 6 을 포함하므로, 손목 DOF 가 없는 Sharpa Hand 와 직접 동일시하지 않도록 각주를 남기시길 제안합니다. `context/` 파일은 수정하지 않았습니다.

---

> 💡 base 매핑은 `/implement-design analysis/2607.28198/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
