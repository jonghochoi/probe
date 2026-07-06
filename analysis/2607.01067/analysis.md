# Paper Analysis — Human-Centric Transferable Tactile Pre-Training for Dexterous Robotic Manipulation

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Human-Centric Transferable Tactile Pre-Training for Dexterous Robotic Manipulation |
| 저자 | Chi Zhang, Penglin Cai, Ziheng Xi, Haoqi Yuan, Hao Luo, Wanpeng Zhang, Sipeng Zheng, Chaoyi Xu, Zongqing Lu (Peking University · BeingBeyond · Tsinghua University) |
| 링크 | [arXiv:2607.01067](https://arxiv.org/abs/2607.01067) · [Website](https://beingbeyond.github.io/TTP/) |
| 발행일 / 버전 | 2026-07-01 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-07-06 |
| 관련 Pillar | P4, P0, P2, P5 |
| 태그 | tactile, egocentric-data, dataset |

<!-- Website URL 은 논문 본문 첫 페이지의 \webpage 항목에 명시된 값입니다.
     검증 시도: curl -L --fail -sS "https://beingbeyond.github.io/TTP/" →
     curl: (56) CONNECT tunnel failed, response 403 — 실행 환경의 네트워크
     정책(allowlist)이 github.io 를 차단해 resolve 여부는 미확인입니다.
     본문에 명시된 URL 이므로 날조가 아니며 그대로 기재합니다.
     GitHub / HuggingFace repo URL 은 본문에 없어 생략합니다. -->

---

## 🧭 한 줄 요약 (TL;DR)

로봇 tactile 데이터의 만성 부족을 사람 쪽에서 풀자는 제안입니다 — 160시간·300+ 태스크·135k 에피소드의 egocentric 인간 시연에 tactile·action 주석을 정렬한 H-Tac 데이터셋을 구축하고, 통일 action 공간(200-D)·통일 tactile 공간(MANO 표면 351-taxel)으로 human 사전학습과 robot 사후학습의 입출력 계약을 동일하게 유지한 채, 미래 tactile 예측 전문가(tactile expert)를 갖춘 VLA 를 사전학습(TTP)하면, 실로봇 fine-grained·contact-rich 태스크에서 tactile 없는 SOTA(BeingH-0.5, $`\pi_{0.5}`$)를 큰 폭으로 앞선다는 것을 보입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 접촉 집약적(contact-rich)·fine-grained 조작에는 촉각이 필수지만, 로봇 tactile 데이터셋은 하드웨어·수집 시스템의 제약으로 규모가 작고 접촉 커버리지가 좁습니다. 인간 시연 데이터는 수집이 훨씬 쉽고 확장 가능하지만, 기존 인간 시연 데이터셋은 vision·action 에 치우쳐 tactile 모달리티가 빠져 있습니다.
- **기존 접근의 한계** — tactile 을 VLA 에 융합하는 기존 VTLA 계열은 tactile 을 post-training 단계에서만 주입해 사전학습과의 분포 불일치를 안고 시작하며, dynamics-agnostic 한 사후학습이라 downstream 성능 ceiling 이 제한됩니다.
- **본 논문의 가설** — 대규모 tactile 사전학습을 VLA 패러다임 안에 통합하고, 사전·사후학습 전 구간에서 통일된 action·tactile 공간을 유지하면, 인간 데이터에서 얻은 tactile prior 가 human→robot 전이에서 보존된다.
- **왜 지금 중요한가** — egocentric 인간 비디오 기반 VLA 사전학습(Being-H 계열, EgoDex 등)이 성숙했고, tactile glove·시뮬레이션 파이프라인·공개 hand-object 데이터셋의 pseudo-contact 라벨링으로 tactile 수집 병목을 우회할 수단이 갖춰졌습니다.
- **자연스러운 질문** — 저자들이 스스로 던지는 질문이 논문의 프레임입니다: 대규모 tactile 사전학습을 VLA 패러다임에 통합해 human→robot 스킬 전이용으로 만들 수 있는가.

---

## 🧩 핵심 기여

- **H-Tac 데이터셋** — 160시간·300+ 태스크·135k+ 에피소드의 egocentric 인간 시연에 dense tactile·action 주석을 정렬한 대규모 tactile-action 데이터셋을 수집·오픈소스화. HOI-Tac(공개 hand-object 데이터셋에서 pseudo-contact 생성, ~106h) + DeskTask-Tac(tactile glove 실측, 37.2h) + InternData-Tac(시뮬 증강, 17.8h)의 3원 구성.
- **최초의 human-centric tactile 사전학습** — tactile 이 포함된 인간 시연으로 VLA 를 사전학습해, 로봇별 post-training 이전에 tactile-grounded prior 를 대규모로 획득하는 첫 시도(저자 주장).
- **통일 action·tactile 공간** — BeingH-0.5 의 200-D 통일 action 공간과 UniTacHand 의 MANO 표면 351-taxel 통일 tactile 공간을 사전·사후학습 전 구간에 유지해, human→robot 전이 시 prior 지식을 보존.
- **Tactile expert + MPG** — action chunk 생성과 별개로 미래 tactile 신호를 flow matching 으로 예측하는 tactile expert 를 두어 접촉 동역학을 명시적으로 모델링하고, action·tactile 이중 anchor 의 sliced Wasserstein 거리 기반 신뢰도 게이트(Tactile-Action Manifold-Preserving Gating)로 컨텍스트 변동에 강건화.
- **실로봇 cross-embodiment 검증** — Franka/Realman 팔 × Inspire(피에조 저항 tactile)/DM-Tac(visuo-tactile 그리퍼)/DexBotic(3D tactile) 손 조합의 9개 태스크에서 tactile 없는 SOTA 대비 대폭 우위(fine-grained 96.7% vs BeingH-0.5 57.3%, 카테고리 평균 진행률 기준).

---

## 🔑 기술 키워드

- **TTP (Transferable Tactile Pre-Training)** — 인간 tactile 데이터로 VLA 를 사전학습해 로봇으로 전이하는 본 논문의 시스템 전체(데이터셋 + 사전학습 + 사후학습)를 가리키는 이름.
- **H-Tac** — 본 논문이 구축한 160시간 egocentric 인간 tactile-action 데이터셋. HOI-Tac / DeskTask-Tac / InternData-Tac 세 하위 데이터셋의 합성.
- **Unified Tactile Space** — 서로 다른 손·센서의 촉각을 하나의 좌표계로 옮기는 "공용 촉각 지도". UniTacHand 를 따라 MANO 손 표면에 분포한 351개 taxel 로 모든 embodiment 의 tactile 을 투영합니다.
- **Unified Action Space** — 사람 손(MANO 파라미터)과 로봇 팔·손·그리퍼의 행동을 한 벡터에 슬롯별로 배치한 200차원 공용 action 공간(BeingH-0.5 계승).
- **MANO** — 778개 정점(vertex)·21개 관절로 손을 표현하는 파라메트릭 손 모델. H-Tac 의 contact 라벨 생성과 tactile taxel 배치의 기준 기하.
- **Tactile Expert** — action expert 와 나란히 미래 K 스텝의 tactile 신호를 flow matching 으로 예측하는 전문가 모듈. "다음에 손끝에 어떤 접촉이 느껴질지"를 맞히게 해 접촉 동역학을 학습시킵니다.
- **Flow Matching** — 플로우 매칭. 노이즈에서 목표 신호로 가는 직선 경로의 속도장을 회귀하는 생성 모델링 기법 — 본 논문에서 action·tactile 두 모달리티 모두의 예측 헤드로 사용.
- **MPG (Manifold-Preserving Gating)** — 관측 컨텍스트가 action·tactile 매니폴드 양쪽과 얼마나 정합하는지를 게이트 $`g`$ 로 측정해, 신뢰도가 낮을 때 feature 보정을 자동으로 약화시키는 잔차 게이팅 모듈(DiG-Flow·BeingH-0.5 계승, 이중 anchor 가 본 논문의 확장).
- **SWD (Sliced Wasserstein Distance)** — 고차원 분포 간 거리를 무작위 1차원 투영들의 정렬 거리 평균으로 근사하는 척도. MPG 의 신뢰도 계산에 사용.
- **Tactile Proxy** — tactile 이 없는 시뮬 벤치마크에서 직전 action 과 현재 proprioceptive state 의 차이를 zero-padding 해 tactile 관측 대신 넣는 치환물.

---

## 🔬 방법론

### 직관

이 논문의 출발점은 "촉각 데이터가 부족한 것은 로봇 쪽 사정이고, 사람 손은 매일 수만 번의 접촉을 만들고 있다"는 관찰입니다. 사람의 egocentric 시연 영상에 촉각과 행동 주석을 붙일 수만 있다면, 로봇 텔레오퍼레이션으로는 도달할 수 없는 규모의 접촉 데이터를 확보할 수 있습니다. 저자들은 세 가지 경로로 이를 실행합니다: 이미 공개된 hand-object 데이터셋의 손-물체 메시 거리에서 접촉 라벨을 역산하고(HOI-Tac), tactile glove 를 낀 사람의 실측 데이터를 모으고(DeskTask-Tac), 시뮬레이션 데이터 엔진에 접촉 기록기를 붙입니다(InternData-Tac).

그런데 사람 손과 로봇 손은 형태도 센서도 다르므로, 그대로 학습하면 사전학습(사람)과 사후학습(로봇) 사이에 분포 단절이 생깁니다. 논문의 두 번째 축은 이 단절을 입출력 공간의 통일로 막는 것입니다. 행동은 사람 손 MANO 파라미터와 로봇 팔·손·그리퍼 명령을 슬롯별로 담는 200차원 공용 벡터로, 촉각은 어떤 센서의 신호든 MANO 손 표면의 351개 고정 지점(taxel)에 투영한 벡터로 표준화합니다. 사전학습과 사후학습이 같은 공간을 쓰므로, 로봇으로 넘어갈 때 모델이 새 입출력 형식을 다시 배울 필요가 없습니다.

세 번째 축은 촉각을 "입력"으로만 쓰지 않고 "예측 대상"으로도 쓰는 것입니다. 미래 action chunk 를 생성하는 action expert 옆에, 같은 horizon 의 미래 tactile 신호를 예측하는 tactile expert 를 둡니다. 다음 순간 손끝에 느껴질 접촉을 맞히려면 접촉 동역학 — 물체가 어떻게 눌리고 미끄러지는지 — 을 내재화해야 하므로, 이 예측 과제 자체가 접촉 물리의 학습 신호가 됩니다. 마지막으로, 관측 컨텍스트가 흔들릴 때(분포 이동) 예측이 불안정해지는 것을 막기 위해, 컨텍스트가 action·tactile 매니폴드와 정합하는 정도를 게이트로 재서 보정 강도를 자동 조절하는 MPG 모듈을 얹습니다.

### H-Tac 데이터셋 구성

![Figure 2 — H-Tac 3원 구성](https://arxiv.org/html/2607.01067/x2.png)

> "Figure 2: Our H-Tac datasets, composed of (a) HOI-Tac, (b) DeskTask-Tac, and (c) InternData-Tac. In total, H-Tac contains 160-hour vison-tactile-action data, including 300+ tasks and 135k+ episodes." (§3)
> (한글 해설 — pseudo-contact 라벨링·glove 실측·시뮬 증강이라는 세 가지 서로 다른 tactile 획득 경로가 하나의 통일 tactile 공간으로 합쳐지는 구성을 시각화합니다.)

**HOI-Tac (~106h)** — ARCTIC, DexYCB, H2O, HO3D v2/v3, HOI4D, HOT3D, OakInk v1/v2 등 공개 hand-object/hand-face/hand-scene 상호작용 데이터셋들에서 접촉 라벨을 역산합니다.

> "For each frame, we generate per-vertex binary contact labels on the 778-vertex MANO hand mesh by thresholding the distance between the hand surface and object meshes." (§3.1)
> (측정된 촉각이 아니라 손 표면 메시와 물체 메시의 거리 임계값으로 만든 이진 접촉 pseudo-label 입니다 — H-Tac 의 최대 지분을 차지하는 부분이 합성 라벨이라는 점은 뒤의 한계에서 다시 짚습니다.)

> "In total, the composite contains approximately 11.5M frames ( $`\sim`$ 106 hours) across 124.8K sequences, encompassing egocentric videos with single-hand and bimanual grasps, static and dynamic object interactions, and diverse environments from tabletop to whole-body scenes." (§3.1)
> (H-Tac 160시간 중 약 106시간이 이 경로에서 나옵니다. per-vertex 접촉 신호는 UniTacHand 의 351-taxel UV 공간에 투영되어 tactile supervision 이 됩니다.)

**DeskTask-Tac (37.2h)** — 자체 수집 시스템으로 실측한 양손 탁상 조작 데이터입니다. RealSense 3대(외부 2 + egocentric 1)로 촬영하고, 1인칭 타임라인을 기준 축으로 손 기하·tactile·태스크 라벨·action 을 정렬합니다. 손 복원은 두 파이프라인을 지원합니다 — RawHand(키포인트 검출 + 다시점 삼각측량, tactile glove 만 필요)와 AprilTag(MoCap glove + tactile glove + 손목 AprilTag). tactile 센서 값은 891차원 UV vertex 로 매핑된 뒤 validation mask 로 351차원으로 변환됩니다.

> "In total, the DeskTask-Tac dataset contains 37.2 hours of 30 Hz data (947 episodes, $`\sim`$ 4M frames)." (§3.2)
> (H-Tac 에서 유일하게 사람 손의 실측 tactile 이 들어간 부분입니다.)

**InternData-Tac (17.8h)** — InternDataEngine 시뮬 파이프라인에 경량 tactile 기록기를 붙여 접촉력·패치 정보(위치·법선·거리·힘)를 에피소드 사이드카로 저장하고, 로봇 그리퍼 종속성을 없애기 위해 접촉 패치를 공유 MANO 손 표면으로 투영합니다. 활성 패치는 Gaussian kernel 로 인접 정점에 분산시켜 국소 압력으로 변환하고, 표면 근처의 zero-force 패치는 거리-감쇠 pseudo-contact 신호로 바꿔 물리적 충격 이전의 기하적 근접 supervision 을 제공합니다.

> "In total, the dataset encompasses 17.8 hours of 30 Hz data (9,563 episodes, $`\sim`$ 1.9M frames) across three diverse robot configurations: Genie1, Lift2, and Split ALOHA." (§3.3)
> (시뮬 로봇 데이터조차 MANO 표면으로 투영해 통일 tactile 공간에 편입시키는 것이 요점입니다.)

데이터셋 통계(§3.4)로는 오른손 tactile 이 전반적으로 크고 손끝(fingertip) 판독값이 손바닥보다 훨씬 두드러지며(손끝 접촉이 지배적), 언어 instruction 은 동사 시작이 대부분이고 "grasp" 가 압도적 1위입니다.

### 아키텍처

모델은 BeingH-0.5 위에 구축됩니다.

> "BeingH-0.5 contains a multimodal understanding expert initialized from InternVL-3.5 [wang2025internvl3.5] and an action generation expert for robot control." (§4)
> (이해(understanding) expert 는 InternVL-3.5 초기화 — 즉 lineage 는 π 계열이 아니라 InternVL 계열입니다. 본 논문은 여기에 VLM 의 tactile 확장과 tactile 예측 expert 를 더합니다.)

![Figure 5 — TTP 학습 아키텍처](https://arxiv.org/html/2607.01067/x5.png)

> "Figure 5: Training architecture of TTP. Our model includes an understanding expert for visual and text interpretation, an action expert, and a tactile expert. We use a unified action and tactile space to preserve pre-traing period knowledge." (§4.1)
> (understanding / action / tactile 의 3-expert 구조와, 사전학습 지식 보존 장치로서의 통일 공간이라는 두 설계 축을 한 장에 담은 그림입니다.)

**문제 정식화(§4.1).** 물리 timestep $`t`$ 에서 관측은 언어 instruction $`l`$, 뷰 $`v`$ 별 RGB $`\mathbf{I}_{t}=\{\mathbf{I}_{t}^{(v)}\}_{v=1}^{V}`$ ( $`\mathbf{I}_{t}^{(v)}\in\mathbb{R}^{H_{I}\times W_{I}\times 3}`$ ), proprioceptive state $`s_{t}\in\mathbb{R}^{D_{\mathrm{act}}}`$, tactile 판독 $`o_{t}\in\mathbb{R}^{D_{\mathrm{tac}}}`$ 로 구성됩니다. $`K`$ 는 예측 horizon(action chunk 길이)입니다. 최근 접촉 정보를 보존하기 위해 정책은 stride 를 둔 tactile history 를 조건으로 받습니다 (식 1):

$$\mathcal{O}^{\mathrm{hist}}_{t}=\left[o_{t-d(L-1)},\ldots,o_{t-d},o_{t}\right]\in\mathbb{R}^{L\times D_{\mathrm{tac}}},$$

여기서 $`L`$ 은 history 길이, $`d`$ 는 시간 stride 로, 계산 부담 축소와 프레임 간 지배적 tactile 정보 보존 사이를 조율합니다. 모델은 미래 action chunk 와 미래 tactile 판독을 모두 예측합니다 (식 2):

$$A_{t}=[a_{t},\ldots,a_{t+K-1}]\in\mathbb{R}^{K\times D_{\mathrm{act}}},\qquad O_{t}^{+}=[o_{t},\ldots,o_{t+K-1}]\in\mathbb{R}^{K\times D_{\mathrm{tac}}}.$$

정책은 다음과 같이 정식화됩니다 (식 3):

$$\left(\hat{A}_{t},\hat{O}_{t}^{+}\right)\sim\pi_{\theta}\left(A_{t},O_{t}^{+}\mid l,\mathbf{I}_{t},s_{t},\mathcal{O}^{\mathrm{hist}}_{t}\right).$$

**통일 action 공간(§4.2).**

> "Following BeingH-0.5 [beingbeyond2026beingh05], our unified action space contains $`D_{\mathrm{act}}=200`$ dimensions, including end effector pose (location and axis-angle rotation), dexterous hand actions, human MANO values (beta, translocations, and theta) [romero2022mano], etc." (§4.2)
> (200차원이 의미 단위 슬롯으로 조직됩니다 — Table 1 기준: 좌/우 EEF pose(0–17), 그리퍼(18–19), 다지 손 관절(20–43), LIBERO 전용(44–45), 좌/우 팔 관절·머리·허리(50–69), 모바일 베이스(70–75), 예약(76–89), 사람 손 MANO $`\beta`$ / $`\theta`$ (90–199). 사람 손과 로봇이 같은 벡터의 다른 슬롯을 점유하는 구조입니다.)

**통일 tactile 공간(§4.2).**

> "We use UniTacHand [zhang2025unitachand] as the unified space of tactile representation to yield a maximum preservation of morphological consistency. Following UniTacHand, we preserve $`D_{\mathrm{tac}}=351`$ taxels for each hand, which are distributed on the surface of the MANO hand model." (§4.2)
> (손마다 351개 taxel 이 MANO 표면에 분포하고, 각 embodiment 의 피에조 저항 tactile 을 이 taxel 로 투영합니다. 사람 손(사전학습)과 로봇 손(사후학습)의 형태학적 대응을 보존하는 것이 통일의 목적이며, 덕분에 cross-embodiment tactile 예측이 가능해진다고 주장합니다.)

**시퀀스 구성(§4.3).** supervision 은 VQA 식 query-answer 포맷 $`[\mathcal{S}_{Q};\mathcal{S}_{A}]`$ 의 통일 멀티모달 시퀀스로 표현됩니다. query $`\mathcal{S}_{Q}`$ 는 이미지·언어·proprioceptive state·tactile 관측 토큰을, answer $`\mathcal{S}_{A}`$ 는 action 토큰과 tactile 예측 토큰을 담습니다.

### 학습 목표 / 손실

$`H_{t}`$ 를 timestep $`t`$ 의 관측 조건 토큰 컨텍스트, $`H_{t,\tau}`$ 를 flow timestep $`\tau`$ 에서 노이즈 낀 action/tactile 궤적을 삽입한 뒤 understanding expert 가 만든 flow-time 의존 컨텍스트라 합니다. 각 모달리티 $`m\in\{\mathrm{act},\mathrm{tac}\}`$ 에 대해 clean target 을 $`x_{1}^{\mathrm{act}}=A_{t}`$, $`x_{1}^{\mathrm{tac}}=O_{t}^{+}`$ 로 정의하고, $`x_{0}^{m}\sim\mathcal{N}(\mathbf{0},\mathbf{I})`$ 와 flow timestep $`\tau^{m}\in[0,1]`$ 을 샘플링해 보간점을 만듭니다 (식 4):

$$x_{\tau^{m}}^{m}=(1-\tau^{m})x_{0}^{m}+\tau^{m}x_{1}^{m}.$$

target 속도는 $`u^{m}=x_{1}^{m}-x_{0}^{m}`$ 이고 (식 5), action expert 와 tactile expert 가 각각 속도를 예측합니다 (식 6):

$$\hat{u}_{\theta}^{m}=v_{\theta}^{m}\left(x_{\tau^{m}}^{m},\tau^{m},H_{t,\tau^{m}}\right),\qquad m\in\{\mathrm{act},\mathrm{tac}\}.$$

플로우 매칭 손실은 (식 7):

$$\mathcal{L}_{m}=\mathbb{E}_{x_{0}^{m},\tau^{m}}\left[\left\|\left(v_{\theta}^{m}(x_{\tau^{m}}^{m},\tau^{m},H_{t,\tau^{m}})-(x_{1}^{m}-x_{0}^{m})\right)\right\|_{2}^{2}\right],\qquad m\in\{\mathrm{act},\mathrm{tac}\},$$

padding 되었거나 사용 불가한 차원은 마스킹한 뒤 계산합니다. 총 목적함수는 두 항의 가중합입니다 (식 8):

$$\mathcal{L}=\lambda_{\mathrm{act}}\mathcal{L}_{\mathrm{act}}+\lambda_{\mathrm{tac}}\mathcal{L}_{\mathrm{tac}},$$

여기서 $`\lambda_{\mathrm{act}}`$ 와 $`\lambda_{\mathrm{tac}}`$ 는 각 손실 항의 가중치입니다(부록 Table 9 기준 둘 다 1.0).

### Tactile-Action Manifold-Preserving Gating (MPG)

MPG 는 action·tactile expert 가 쓰는 것과 같은 flow-time 의존 컨텍스트 $`H_{t,\tau}`$ (VLM hidden 공간으로 투영된 proprioceptive state·tactile 관측·noisy action·noisy tactile 토큰 feature) 위에서 동작하며, 속도 디코딩 전에 컨텍스트를 $`\tilde{H}_{t,\tau}=\mathrm{MPG}(H_{t,\tau})`$ 로 보강합니다. 속도장은 다음으로 평가됩니다 (식 9):

$$\hat{u}_{\theta}^{m}=v_{\theta}^{m}\left(x_{\tau}^{m},\tau,\tilde{H}_{t,\tau}^{m}\right).$$

동기는 분산 축소입니다. Euler 한 스텝 $`x_{\tau+\Delta\tau}^{m}=x_{\tau}^{m}+\Delta\tau\cdot v_{\theta}^{m}(x_{\tau}^{m},\tau;H_{t,\tau})`$ (식 10)에서 $`H_{t,\tau}=H_{t,\tau}^{\ast}+\epsilon`$ 처럼 작은 교란이 있으면, 1차 근사로 예측 분산이 $`\left\|\frac{\partial v_{\theta}^{m}}{\partial H_{t,\tau}}\right\|^{2}\mathrm{Var}(\epsilon)`$ 에 비례해 커집니다. 이를 줄이기 위해 DiG-Flow 와 BeingH-0.5 를 따라 신뢰도 게이트 $`g\in(0,1]`$ 로 잔차 보강을 변조합니다 (식 11):

$$\tilde{H}_{t,\tau}=H_{t,\tau}+\lambda\left[\mathbf{W}_{\mathrm{MPG}}\left(g^{\mathrm{sg}}\odot\mathcal{E}_{\mathrm{obs}}(H_{t,\tau})\right)+\mathbf{b}_{\mathrm{MPG}}\right],$$

여기서 $`g^{\mathrm{sg}}=\mathrm{stopgrad}(g)`$ 이고 $`\lambda`$ 는 잔차 항의 가중치입니다. 게이트 계산을 위해 노이즈 없는(noise-free) action·tactile anchor 를 구성합니다 — $`Z^{\mathrm{nf,act}}`$, $`Z^{\mathrm{nf,tac}}`$ 를 mean-pool 하고 (식 12: $`\bar{Z}^{\mathrm{act}}=\mathrm{MeanPool}(Z^{\mathrm{nf,act}})`$, $`\bar{Z}^{\mathrm{tac}}=\mathrm{MeanPool}(Z^{\mathrm{nf,tac}})`$ ), 관측·action·tactile feature 를 공유 정규화 공간으로 투영합니다 (식 13):

$$\hat{H}_{t,\tau}=\mathrm{LN}\left(\mathcal{E}_{\mathrm{obs}}(H_{t,\tau})\right),\quad\hat{Z}^{\mathrm{act}}=\mathrm{LN}\left(\mathcal{E}_{\mathrm{act}}(\bar{Z}^{\mathrm{act}})\right),\quad\hat{Z}^{\mathrm{tac}}=\mathrm{LN}\left(\mathcal{E}_{\mathrm{tac}}(\bar{Z}^{\mathrm{tac}})\right),$$

그리고 feature–action/tactile 분포 불일치를 sliced Wasserstein 거리(SWD)로 정량화합니다 (식 14):

$$D_{\mathrm{act}}=\frac{1}{M}\sum_{i=1}^{M}\left\|\mathrm{sort}\left(\theta_{i}^{\top}\hat{H}_{t,\tau}\right)-\mathrm{sort}\left(\theta_{i}^{\top}\hat{Z}^{\mathrm{act}}\right)\right\|_{2}^{2},$$

$$D_{\mathrm{tac}}=\frac{1}{M}\sum_{i=1}^{M}\left\|\mathrm{sort}\left(\theta_{i}^{\top}\hat{H}_{t,\tau}\right)-\mathrm{sort}\left(\theta_{i}^{\top}\hat{Z}^{\mathrm{tac}}\right)\right\|_{2}^{2},$$

각 $`\theta_{i}`$ 는 무작위 단위 투영 방향입니다. 결합 불일치와 게이트는 (식 15):

$$D=\frac{1}{2}\left(D_{\mathrm{act}}+D_{\mathrm{tac}}\right),\qquad g=\exp(-D/\tau_{g}).$$

> "This dual-anchor design enhances $`H_{t,\tau}`$ only when it aligns with both action and tactile manifolds, ensuring that the feature-dependent correction becomes increasingly insensitive when the context is unreliable (small $`g`$ ), and improving robustness under context shifts." (§4.4)
> (action 하나만 anchor 로 쓰던 선행(DiG-Flow·BeingH-0.5)과 달리 tactile 을 두 번째 anchor 로 추가한 것이 본 논문의 확장입니다 — 컨텍스트가 두 매니폴드 모두와 정합할 때만 보강이 살아 있고, 신뢰도가 낮으면 보정이 자동으로 죽어 분포 이동에 강건해집니다.)

### 학습 셋업

부록 Table 9 의 하이퍼파라미터가 사전학습·사후학습(시뮬/실로봇) 3열로 명시됩니다. 공통: learning rate `1e-4`, weight decay `1e-5`, warmup ratio `0.05`, action/tactile loss weight 각 `1.0`, max num tokens `8192`, expected num tokens `7680`, equivalent batch size `128`, downsample ratio `0.5`. 단계별 차이:

| 하이퍼파라미터 | Pre-Training | Post-Training (sim) | Post-Training (real robot) |
|---|---|---|---|
| image size | 448 $`\times`$ 448 | 224 $`\times`$ 224 | 224 $`\times`$ 224 |
| action chunk size | 32 | 8 | 24 |
| tactile history size | 4 | 2 | 4 |
| tactile history stride | 8 | 1 | 4 |

옵티마이저 종류·GPU 하드웨어·본 학습의 총 스텝 수는 본문에 명시되어 있지 않습니다(ablation 은 사전학습 150k 스텝 기준으로 수행). 추론 시 하이퍼파라미터는 학습 시와 동일하게 유지합니다(§7).

---

## 📊 실험 설정과 결과

실험은 세 질문에 답합니다(§5): (1) tactile 사전학습 후 hand motion·tactile 생성이 잘 되고 일반화하는가, (2) tactile 모달리티 추가라는 학습 비용에도 시뮬 벤치마크에서 대등 이상인가, (3) 실세계 tactile-relevant 태스크에서 뛰어난가.

### 사전학습 시각화 (§5.1)

![Figure 6 — 사전학습 시각화](https://arxiv.org/html/2607.01067/x6.png)

> "Figure 6: Visualization showcase. After tactile-based pre-training, our TTP model can generate hand motion and tactile predictions well, and can generalize to OOD inpainted scenes." (§5.1)
> (원 검증셋뿐 아니라 사람 손을 지우거나 로봇 팔로 inpainting 한 OOD 장면에서도 hand motion 생성과 tactile 예측(MANO 표면 heatmap)이 유지됨을 보이는 정성 결과입니다.)

### 시뮬 벤치마크 (§5.2)

tactile 이 없는 벤치마크에서 이중 목적함수(action 생성 + tactile 예측)를 유지하기 위해 tactile proxy 를 씁니다.

> "Since these benchmarks do not have tactile modalities inherently, to keep the dual-level optimization objective (action generation and tactile prediction), we use the difference between last action and current proprioceptive state as “tactile proxy” during post-training." (§5.2)
> (구체적으로 $`o_{t}^{\mathrm{proxy}}=\mathrm{padding}(s_{t}-a_{t-1})`$ 로 정의하고 $`D_{\mathrm{act}}=200`$ 과 $`D_{\mathrm{tac}}=351`$ 의 차이는 zero-padding 합니다. 즉 시뮬 수치는 실제 촉각의 증거가 아니라 "tactile 목적함수 구조가 해가 되지 않는다"의 증거로 읽어야 합니다.)

주요 결과 (Table 2 발췌 — LIBERO 는 task 당 50 에피소드 평균, LIBERO-plus 는 zero-shot 카테고리당 70 trial 평균, RoboCasa 는 24개 task 각 50 trial 평균):

| Method | LIBERO Spat. | Obj. | Goal | Long | Avg. | LIBERO-plus Avg. | RoboCasa Avg. |
|---|---|---|---|---|---|---|---|
| OpenVLA | 84.7 | 88.4 | 79.2 | 53.7 | 76.5 | 15.6 | - |
| OpenVLA-OFT | 97.6 | 98.4 | 97.9 | 94.5 | 97.1 | 69.6 | - |
| $`\pi_{0}`$ -Fast | 96.4 | 96.8 | 88.6 | 60.2 | 85.5 | 61.6 | 29.8 |
| $`\pi_{0}`$ | 98.0 | 96.8 | 94.4 | 88.4 | 94.4 | 53.6 | 42.4 |
| $`\pi_{0.5}`$ | 98.8 | 98.2 | 98.0 | 92.4 | 96.8 | 65.0 | 41.4 |
| BeingH-0.5 | 98.8 | 97.6 | 98.8 | 96.6 | 98.0 | 71.7 | 53.9 |
| TTP w/o pre-training | 98.0 | 97.4 | 97.6 | 96.6 | 97.4 | 73.4 | 52.3 |
| TTP (ours) | 98.8 | 98.2 | 98.2 | 97.0 | 98.1 | 75.7 | 55.1 |

LIBERO 평균은 98.0(BeingH-0.5)→98.1(TTP)로 사실상 동률 — tactile 토큰 추가에 따른 시퀀스 부담에도 성능을 유지했다는 주장이며, zero-shot LIBERO-plus(71.7→75.7, 특히 Language 84.3·Light 94.6·Layout 83.6)와 RoboCasa(53.9→55.1)에서 일반화 우위를 보입니다.

### 실로봇 실험 (§5.3)

**하드웨어·태스크** — Franka(7-DoF)/Realman(6-DoF ×2) 팔과 Inspire 손(6-DoF, 손가락·손바닥 피에조 저항 tactile)/DM-Tac 그리퍼(visuo-tactile)/DexBotic 손(12-DoF, 손끝 3D tactile)의 조합으로 9개 태스크: Fine-Grained(Peeling Inspire/Gripper, VaseWiping 단수/양손), Contact-Rich & Fragile(PickPlaceChips, PaperFolding), Vision Defect(SoftHard, PlugIn Gripper/DexBotic). 평가는 Peeling 은 벗긴 껍질 평균 길이(cm), PaperFolding 은 접힌 길이 비율(%), 나머지는 성공률(%)입니다.

**카테고리 평균 (Table 4 — ID 10 + OOD 5 trial 의 평균 task progress rate, TTP 를 100% 로 비례 환산):**

| Task Category | $`\pi_{0.5}`$ | $`\pi_{0.5}`$ + tactile | BeingH-0.5 | TTP w/o pre-train | TTP (ours) |
|---|---|---|---|---|---|
| Fine-grained | 43.2% | 48.3% | 57.3% | 71.0% | 96.7% |
| Contact-rich & Fragile | 3.3% | 8.0% | 9.2% | 49.7% | 79.2% |
| Vision Defect | 17.8% | 17.8% | 15.6% | 26.7% | 37.8% |

> "TTP outperforms tactile-free state-of-the-art (SOTA) baselines (including BeingH-0.5 [beingbeyond2026beingh05] and $`\pi_{0.5}`$ [intelligence2025pi05]) by a large margin, demonstrating the effectiveness of tactile modality." (§5.3.3)
> (특히 contact-rich & fragile 카테고리에서 tactile 없는 baseline 은 한 자릿수(3.3–9.2%)인 반면 TTP 는 79.2% — 촉각이 없으면 사실상 못 푸는 태스크군임을 보여줍니다. 동시에 TTP w/o pre-train 이 이미 49.7% 로 BeingH-0.5(9.2%)를 크게 앞서는 점에 주목 — 이득의 상당 부분은 tactile 관측·예측 구조 자체에서 나오고, 사전학습은 그 위의 증분(49.7→79.2)입니다.)

> "For instance, TTP can continuously peel the radish skin for a length of over 20 cm, while baseline methods peel only for a short length with jitter." (§5.3.3)
> (성공/실패의 이분법이 아니라 동작 질의 차이 — 적당한(moderate) 파지력으로 연속 동작을 유지하는 행동 양식이 tactile 사전학습의 산물이라는 정성 주장입니다. 감자칩 파지에서도 부수지 않고 놓치지도 않는 중간 힘을 냅니다.)

**ID 상세 (Table 5 — 10 trial 평균):**

| Category | Task | $`\pi_{0.5}`$ | $`\pi_{0.5}`$ + tactile | BeingH-0.5 | TTP w/o pre-train | TTP (ours) |
|---|---|---|---|---|---|---|
| Fine-Grained | Peeling (Inspire) | 10.63 cm | 9.27 cm | 12.49 cm | 14.65 cm | 23.33 cm |
| | VaseWiping (single hand) | 30% | 50% | 50% | 70% | 100% |
| | VaseWiping (bimanual) | 50% | 40% | 70% | 60% | 90% |
| | Peeling (Gripper) | 10.39 cm | 12.02 cm | 11.37 cm | 14.48 cm | 15.24 cm |
| Contact-Rich & Fragile | PickPlaceChips | 10% | 20% | 10% | 60% | 80% |
| | PaperFolding | 0% | 4% | 12% | 57% | 84% |
| Vision Defect | SoftHard | 50% | 60% | 40% | 80% | 80% |
| | PlugIn (Gripper) | 0% | 0% | 0% | 0% | 20% |
| | PlugIn (DexBotic) | 0% | 0% | 0% | 10% | 10% |

**OOD 상세 (Table 6 — 5 trial 평균, 물체·위치·장면 일반화):**

| Category | Task | $`\pi_{0.5}`$ | $`\pi_{0.5}`$ + tactile | BeingH-0.5 | TTP w/o pre-train | TTP (ours) |
|---|---|---|---|---|---|---|
| Fine-Grained | Peeling (Inspire) | 5.74cm | 5.48cm | 9.28 cm | 11.25cm | 19.12 cm |
| | VaseWiping (single hand) | 20% | 20% | 40% | 80% | 100% |
| | VaseWiping (bimanual) | 40% | 60% | 60% | 40% | 80% |
| | Peeling (Gripper) | 6.68 cm | 8.71 cm | 7.04 cm | 15.83 cm | 16.24 cm |
| Contact-Rich & Fragile | PickPlaceChips | 0% | 0% | 0% | 40% | 60% |
| | PaperFolding | 0% | 0% | 11% | 24% | 87% |
| Vision Defect | SoftHard | 60% | 40% | 60% | 60% | 80% |
| | PlugIn (Gripper) | 0% | 0% | 0% | 0% | 20% |
| | PlugIn (DexBotic) | 0% | 0% | 0% | 0% | 20% |

OOD 일반화 범주는 물체 일반화(당근·오이 껍질 벗기기, 다른 재질 종이 접기, 새 화병 닦기, 미지의 soft/hard 물체 구분), 위치 일반화(감자칩 위치 변경), 장면 일반화(소켓을 검게 칠한 PlugIn) 등입니다. OOD 에서 격차가 오히려 벌어지는 항목(PaperFolding 11%→87%)이 눈에 띕니다.

![Figure 8 — 실로봇 showcase](https://arxiv.org/html/2607.01067/x8.png)

> "Figure 8: Real robot showcases. Our TTP demonstrate strong capabilities of precise and fine-grained manipulation, outperforming various baselines." (§5.3.3)
> (radish peeling 의 연속 동작, 감자칩의 온전한 파지 등 "moderate 한 행동 양식" 주장을 시각화한 정성 결과입니다.)

### Ablation (§5.4)

**모델 설계 (Table 7 — 사전학습 150k 스텝, 검증셋 motion 예측 오차, 낮을수록 좋음):**

| Method | MPJPE | PA-MPJPE | MPJAE | PA-MPJAE |
|---|---|---|---|---|
| TTP w/o MPG w/o tac-pred | 25.5850 | 0.8622 | 0.0277 | 0.0620 |
| TTP w/o MPG | 24.7597 | 0.8151 | 0.0267 | 0.0598 |
| TTP w/o tac-pred | 24.5518 | 0.8009 | 0.0263 | 0.0583 |
| TTP (ours) | 23.5711 | 0.7877 | 0.0257 | 0.0559 |

> "The results show that both excluding MPG and excluding tactile prediction will have a negative effect on training performances, yielding higher motion prediction errors." (§5.4.1)
> (미래 tactile 예측 제거(w/o tac-pred → ours: MPJPE 24.55→23.57)와 MPG 제거(w/o MPG → ours: 24.76→23.57) 모두 오차를 키웁니다 — 다만 개선 폭은 두 모듈 합쳐 MPJPE 기준 약 8% 수준으로, downstream 성공률 격차에 비해 완만합니다. ablation 지표가 실로봇 성공률이 아니라 사전학습 검증셋의 motion 예측 오차라는 점도 유의.)

**데이터 스케일링 (Table 8 — 균일 샘플링 비율별, 150k 스텝):**

| Percentage of Training Data | MPJPE | PA-MPJPE | MPJAE | PA-MPJAE |
|---|---|---|---|---|
| 10% | 33.1917 | 1.4066 | 0.0421 | 0.0958 |
| 25% | 29.6462 | 1.2563 | 0.0374 | 0.0806 |
| 50% | 25.4919 | 1.1336 | 0.0335 | 0.0698 |
| 75% | 24.4753 | 0.9162 | 0.0295 | 0.0623 |
| 100% (ours) | 23.5711 | 0.7877 | 0.0257 | 0.0559 |

> "The results show that the motion prediction error decreases as more training data are used, which demonstrate that our proposed tactile-based pre-training can scale up." (§5.4.2)
> (10%→100% 구간에서 단조 개선이 유지되고 100% 에서도 포화 기미가 없어, tactile 사전학습이 데이터 규모의 함수로 계속 좋아진다는 스케일링 논거입니다 — 160시간이 상한이 아니라는 뜻이기도 합니다.)

---

## ⚖️ 한계

논문에 별도의 Limitations 섹션은 없으며, 아래는 본문 서술에서 추론한 갭입니다.

- **H-Tac 의 2/3 가 합성 이진 접촉 라벨** — HOI-Tac(~106h/160h)은 측정된 촉각이 아니라 손-물체 메시 거리 임계값으로 만든 per-vertex binary pseudo-label 입니다. 접촉의 유무는 담지만 힘의 크기·분포·시간 프로파일은 담지 못하므로, "정밀한 힘 피드백" 이라는 모티베이션과 사전학습 신호의 실제 밀도 사이에 간극이 있습니다. 연속 힘 값을 가진 부분은 DeskTask-Tac(37.2h, glove)과 InternData-Tac(17.8h, 시뮬)뿐입니다.
- **시뮬 이득은 tactile 의 증거가 아님** — 시뮬 벤치마크는 tactile 이 없어 $`o_{t}^{\mathrm{proxy}}=\mathrm{padding}(s_{t}-a_{t-1})`$ 로 치환했고, LIBERO 평균 이득도 98.0→98.1 로 오차 범위 수준입니다. 시뮬 결과가 말해 주는 것은 "tactile 목적함수 구조가 방해되지 않는다"까지이며, 촉각의 가치 입증은 전적으로 실로봇 표(Table 4–6)에 실려 있습니다.
- **실로봇 표본 크기** — 태스크당 ID 10 trial·OOD 5 trial 로, 10–20%p 단위 차이는 1–2회 성공 차이에 해당합니다. 카테고리 평균의 큰 격차(9.2% vs 79.2%)는 강건하겠지만, 개별 태스크 수치(특히 PlugIn 10–20%)는 통계적 해상도가 낮습니다.
- **Vision Defect 카테고리는 미해결로 남음** — tactile 을 넣고도 PlugIn 류는 TTP 기준 10–20% 로 절대 성능이 낮습니다(카테고리 평균 37.8%). 촉각이 시각 결손을 보상한다는 서사의 가장 어려운 지점에서 개선 폭이 가장 작아, 정밀 삽입은 tactile 사전학습만으로 풀리지 않는 문제로 남습니다.
- **MPG 의 기여는 완만하고 세부가 미명시** — MPG 는 DiG-Flow·BeingH-0.5 계승이라 이중 anchor 화가 증분 기여인데, ablation 개선 폭이 MPJPE 기준 ~5% 이고 게이트 온도 $`\tau_{g}`$, 투영 수 $`M`$, 잔차 가중 $`\lambda`$ 값이 본문에 없습니다. 재현·이식 시 이 모듈의 우선순위는 낮게 두는 것이 합리적입니다.
- **351-taxel 통일 공간의 해상도 상한** — 어떤 센서든 손 하나당 351차원으로 투영하므로, 고해상 visuo-tactile(DM-Tac 등 이미지형 센서)의 국소 전단·텍스처 정보는 다운샘플 과정에서 소실됩니다. 통일이 주는 전이성과 센서 고유 정보량 사이의 트레이드오프가 정량화되어 있지 않습니다.
- **ablation 지표와 downstream 의 단절** — 설계·스케일링 ablation 이 모두 사전학습 검증셋의 hand-motion 예측 오차(MPJPE 계열)로만 측정되어, 각 모듈·데이터 규모가 실로봇 성공률에 주는 기여는 직접 측정되지 않았습니다.

---

## ♻️ 재현성

- **데이터** — H-Tac 을 "collect and open-source" 한다고 명시(§1 기여 1). 공개 위치는 프로젝트 페이지( https://beingbeyond.github.io/TTP/ ) 외 본문에 URL 이 없으며, 본 분석 환경에서는 네트워크 정책으로 페이지 접근이 차단되어 실제 공개 상태는 미확인입니다.
- **코드** — 공식 GitHub repo 는 본문에서 확인되지 않습니다. 모델·학습 코드 공개 여부 미확인.
- **하드웨어** — 실로봇 구성(Franka·Realman 팔, Inspire·DexBotic 손, DM-Tac 그리퍼)은 명시. GPU·학습 하드웨어는 미명시.
- **하이퍼파라미터** — 부록 Table 9 에 학습률·배치·chunk·tactile history 등이 3단계(사전/시뮬 사후/실로봇 사후)로 명시되어 있으나, 옵티마이저 종류·총 사전학습 스텝(본 학습)·MPG 세부( $`\tau_{g}`$, $`M`$, $`\lambda`$ )는 없습니다. 베이스 모델 BeingH-0.5(InternVL-3.5 초기화)의 가용성에 재현이 강하게 종속됩니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P4(데이터 효율 적응을 위한 사전학습) · D22(pretraining data composition — OPEN) — 정중앙.** D22 의 열린 질문이 "egocentric 중심 corpus 로 충분한가" 인데, 본 논문은 그 corpus 에 **tactile 축을 추가**하면 실로봇 contact-rich 전이가 크게 좋아진다는 직접 증거를 줍니다(TTP vs TTP w/o pre-train: contact-rich 49.7→79.2%). egocentric-중심 구성(D24 와 동일 방향)에 촉각 정렬이 얹힌 corpus 의 가치를 보여 D22 의 설계 공간을 한 축 넓힙니다.
- **P4 · D21(staged recipe) / D20(prior-preservation strategy)** — 지지 + 관점 확장. TTP 의 사전→사후 이행은 D21 의 staged recipe 와 동형이며, 보존 메커니즘이 freeze/PEFT(D20 v1 의 어휘)가 아니라 **입출력 공간의 불변성**(통일 action·tactile 공간을 두 단계에서 동일 유지)이라는 점이 새로운 레버입니다 — "표현 공간의 일관성이 곧 preservation" 이라는 각도.
- **P4 · D19(lineage)** — 관련 정보. TTP 의 lineage 는 InternVL-3.5 × BeingH-0.5 mix 로, 우리 v1(PaliGemma-2B × π0 mix)과 다릅니다. 레시피(tactile 사전학습)와 checkpoint(BeingH-0.5)가 분리 가능한지가 D19 관점의 쟁점.
- **P0(VLA Datasets & Benchmarks) · D25(tactile/torque data scouting) — 정면 타격.** D25 v1 은 "새 contact-modality 릴리스를 고우선 플래그" 인데, H-Tac(160h, 손 표면 351-taxel, ego 중심)이 정확히 그 대상입니다. D24(egocentric priority axis)도 직접 지지 — ego 비디오에 tactile 을 정렬한 최초급 규모.
- **P2(구조적 다중모달 관측 융합) · D11(proprio-tactile-force token construction)** — 지지와 긴장이 공존. UniTacHand 351-taxel MANO-표면 공간은 D11 v1 의 "swappable sensor head + common token format" 의 실증 사례입니다(피에조 저항·visuo-tactile·3D tactile 세 종의 센서가 한 공간에 투영되어 실로봇 전이). 반면 **긴장**: TTP 의 tactile 은 손 전체가 flat 한 351-D 벡터 → 토큰이며, D11 v1 의 per-finger 토큰 분해(10 finger + 2 palm)·D12 의 topology-aware 집계 같은 구조화는 없습니다. D10(fusion beyond concat) 관점에서도 TTP 는 시퀀스 token-append 로, cross-attention 구조 융합이 아닙니다.
- **P5(World Model) · D28(world-model role) / D30(prediction space)** — 인접. tactile expert 의 미래 tactile 예측은 D28 v1 의 "future-prediction auxiliary co-trained with the policy" 와 구조가 같고, 예측 공간이 D30 의 latent/3D-flow 가 아닌 **tactile 공간**이라는 제3 의 선택지입니다. 접촉-관련 예측이라는 D30 의 정신(contact-relevant prediction)과는 부합.
- **P1(Body/Hand action expert)** — 건드리지 않음. TTP 의 dual-expert 는 action/tactile(모달리티) 분리이지 Body/Hand(해부학) 분리가 아니며, action expert 는 단일 200-D 공간을 통째로 생성합니다. P1 의 결정들과는 직교 — 충돌 없이 결합 가능.
- **Identity 지지/긴장** — tactile 을 1급 modality 로 끌어올리고 "vision 만으로는 fine-grained 조작이 안 된다" 를 실증한 점은 Identity 의 관측 승격 주장을 강하게 지지합니다. 긴장: 융합 방식이 flat token-append 라 "structured multimodal observation fusion(flat-concat 초월)" 과는 반대 노선이고, 그럼에도 실로봇 이득이 크다는 사실은 "구조화 없이 사전학습 규모로 밀어붙이는" 경쟁 가설의 증거로도 읽힙니다.

---

## ✨ 핀 논문 대비 델타

- **vs Being-H0.5([arXiv:2601.12993], P4 §5 핀)** — TTP 는 같은 BeingBeyond 팀의 직계 후속으로, BeingH-0.5 를 베이스 모델로 그대로 씁니다. 진짜 델타는 (i) 사전학습 corpus 에 **tactile 모달리티**를 추가(UniHand-2.0 계열엔 촉각이 없음), (ii) 미래 tactile 예측 expert 신설, (iii) MPG 의 anchor 를 action 단일→action+tactile 이중으로 확장한 것. "human-video 사전학습" 노선 자체는 계승이지 새롭지 않습니다.
- **vs UniHand-2.0([arXiv:2601.12993], P0 §5 핀)** — 규모는 UniHand-2.0(~35k h)이 압도하지만 tactile 축이 없습니다. H-Tac(160h)은 규모 대신 vision-tactile-action 3중 정렬을 제공 — P0 관점에서 서로 대체가 아니라 보완 관계.
- **vs RH20T([arXiv:2307.00595], P0 §5 핀, D25)** — RH20T 는 로봇 손목의 6축 F/T(단일 지점 힘)이고, H-Tac 은 사람 손 표면 351-taxel 의 공간 분포 촉각입니다. hand-centric 접촉 분포(손끝별·손바닥별)를 담는다는 점에서 D25 가 찾던 "희소한 contact-modality corpus" 에 한층 가깝습니다.
- **vs ViTacFormer([arXiv:2506.15953], P2 §5 핀)** — ViTacFormer 는 로봇 데이터의 post-training 단계에서 cross-attention 으로 visuotactile 을 융합합니다. TTP 의 델타는 tactile 을 **사전학습 단계로 앞당긴 것** — 융합 구조는 오히려 단순(token-append)하지만, "구조 대신 사전학습 규모" 라는 반대 방향의 베팅입니다.
- **vs Sparsh([arXiv:2410.24090], P2 methodology base)** — Sparsh 는 tactile-only 자기지도 인코더(표현 학습)이고, TTP 는 VLA 수준에서 tactile 을 action 과 공동 학습합니다. Sparsh 가 "촉각 표현"을 팔면 TTP 는 "촉각이 든 정책 prior"를 파는 셈.

---

## ⚙️ 의사결정 함의

- **D22 corpus 설계** — 사전학습 corpus 계획(egocentric-중심, P0 D24)에 tactile 정렬 스트림을 추가하는 옵션을 명시적으로 평가할 것. 구체 config: tactile supervision 채널 = UniTacHand 351-taxel 공간, 손실 = flow matching 이중 항 $`\mathcal{L}=\lambda_{\mathrm{act}}\mathcal{L}_{\mathrm{act}}+\lambda_{\mathrm{tac}}\mathcal{L}_{\mathrm{tac}}`$ 에 `lambda_tac = 1.0` (논문 기본값). H-Tac 공개 확인 시 corpus 후보에 직접 편입 가능.
- **D11 공통 토큰 포맷 후보** — Sharpa Deform Map(~320×240/fingertip)→MANO 표면 351-taxel 투영 어댑터를 D11 의 "swappable sensor head + common token format" 의 구체 인스턴스 후보로 검토. TTP 가 피에조/visuo-tactile/3D tactile 세 종을 이 공간으로 전이시킨 실증이 있으므로, Sharpa 락인 회피 요건과 정합합니다. 단 per-finger 토큰 분해(D11 v1)는 TTP 에 없으므로 "351-taxel 공간 위에 손가락별 슬라이싱을 얹는" 하이브리드가 우리 설계점.
- **D28 예측 공간 옵션** — P5 의 future-prediction auxiliary 후보에 "tactile-공간 예측 head"(action chunk 와 동일 horizon $`K`$ 의 미래 tactile flow matching)를 추가. latent/3D-flow(D30 v1) 대비 접촉 관련성이 직접적이고 출력 차원이 작아(351/hand) 저비용 — in-hand 태스크(Phase 1)에서 먼저 시험할 가치.
- **학습 config 참조값** — tactile history 는 `L=4, stride d=8`(사전학습)/`L=4, d=4`(실로봇), action chunk 는 32(사전)/24(실로봇), lr `1e-4`, batch 128. tactile 없는 벤치마크 병행 시 tactile proxy( $`\mathrm{padding}(s_{t}-a_{t-1})`$ ) 트릭 재사용 가능.
- **평가 메트릭** — 성공률 외에 연속 진행 메트릭(벗긴 껍질 길이 cm, 접힌 비율 %)을 Phase 1–2 평가에 도입 검토. tactile 이득이 성공/실패보다 "동작의 질(연속성·moderate 파지력)" 에서 먼저 드러난다는 것이 본 논문의 관찰이므로, 이 축이 없으면 이득을 놓칠 수 있습니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 점검) 시뮬 수치에 속지 말 것** — 우리 재현·비교 실험을 LIBERO 류 시뮬로 설계하면 tactile proxy 치환 때문에 TTP 의 핵심 주장을 검증할 수 없습니다(LIBERO 이득 98.0→98.1 수준). 판단 근거는 처음부터 실로봇/tactile-가능 환경 표(Table 4–6 상당물)로 한정할 것.
- **이득 분해 먼저** — TTP w/o pre-train 이 이미 contact-rich 에서 BeingH-0.5 를 40%p 이상 앞섭니다(9.2→49.7%). 즉 "tactile 관측+예측 아키텍처" 만으로 이득의 절반 이상이 회수될 가능성 — 대규모 사전학습 투자 전에, 우리 스택에서 tactile 입력 + 미래 tactile 예측 head 만 붙인 소규모 실험으로 아키텍처 몫을 먼저 측정하는 것이 압도적으로 쌉니다.
- **pseudo-label 품질 검증** — H-Tac 의 최대 지분(HOI-Tac ~106h)이 메시 거리 이진 접촉입니다. Sharpa Deform Map 의 연속 변형장과 분포가 크게 다르므로, 소량의 paired 데이터(우리 센서 실측 vs 351-taxel 투영)로 신호 정합성을 먼저 확인해야 합니다. 정합이 나쁘면 사전학습 prior 가 오히려 우리 센서 분포를 왜곡하는 negative transfer 위험.
- **Deform Map→351-taxel 어댑터 부재** — 논문의 embodiment 는 피에조 저항(Inspire)·visuo-tactile 그리퍼(DM-Tac)·3D tactile(DexBotic)이고, vision 기반 Deform Map 매핑은 전례가 없습니다. UniTacHand 공간이 손 표면 기하 기반이라 이론상 투영 가능하지만, 이 어댑터 설계·검증은 온전히 우리 몫입니다.
- **lineage 불일치** — TTP 는 InternVL-3.5 기반 BeingH-0.5 위에서만 검증되었습니다. 우리 v1 lineage(PaliGemma-2B × π0, D19)에 레시피만 이식했을 때 재현된다는 보장이 없고, BeingH-0.5 checkpoint 채택은 D19 결정 자체를 뒤집는 비용이 큰 선택입니다. 레시피/checkpoint 분리 가능성을 소규모로 먼저 확인.
- **MPG 는 마지막에** — 게이트 세부( $`\tau_{g}`$, $`M`$, $`\lambda`$ ) 미명시 + 이득 완만(MPJPE ~5%)이므로, 이식 우선순위는 tactile expert < 통일 공간 < MPG 순으로 뒤에 둘 것.
- **양손·손가락 구조화 확인** — TTP 의 351-D flat tactile 이 우리 D11/D12(per-finger binding·topology-aware 집계)와 충돌합니다. flat 공간에서 사전학습한 prior 위에 per-finger 구조화를 얹을 때 이득이 유지되는지(또는 사전학습 표현이 손가락 단위 어텐션을 방해하는지)를 Phase 1 in-hand 태스크에서 검증 필요.

---

## 💡 컨텍스트 제안

- **P0 §5 핀 후보 — H-Tac([arXiv:2607.01067])** — D25(tactile/torque data scouting)가 "새 contact-modality 릴리스 고우선 플래그" 를 명시하므로, H-Tac 은 그 정의상 등재 후보입니다. 8핀 cap 고려 시 RH20T(손목 F/T 단일 지점)와의 교체 또는 methodology base 등재를 사람 판단으로 제안합니다. 단, 공개 상태(프로젝트 페이지·라이선스)를 먼저 확인할 것 — 본 분석 환경에서는 네트워크 차단으로 미확인.
- **P4 D22 증거 등재** — D22(OPEN)의 "egocentric-centric corpus" 서술에 tactile 정렬 축의 증거로 TTP 를 methodology base 로 추가 제안. "corpus 구성에서 modality 커버리지(촉각)가 태스크군별 전이 이득을 좌우한다" 는 본 논문의 실증이 D22 ablation 설계에 직접 참고가 됩니다.
- **P2 D11 deferred 후보 명시** — "UniTacHand 351-taxel MANO-표면 공통 tactile 공간" 을 D11 의 common-token-format deferred 후보로 기록해 둘 가치가 있습니다(Sharpa 락인 회피 요건과 정합, 단 per-finger 분해는 별도 유지). (사람 판단 사항 — context 파일은 수정하지 않았습니다.)

> 💡 base 매핑은 `/implement-design analysis/2607.01067/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
