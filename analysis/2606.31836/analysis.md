# Paper Analysis — RoboTacDex: A Dexterous Visual-Tactile-Action Dataset for Humanoid Manipulation

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | RoboTacDex: A Dexterous Visual-Tactile-Action Dataset for Humanoid Manipulation |
| 저자 | Xinyi Wang, Donghan Li, Zi'Ang Chen, Chong Yu, Chen Xin, Peng Ye, Yingkai Sun, Tao Chen (Fudan University · ByteDance Intelligent Creation · Shanghai AI Laboratory · The Chinese University of Hong Kong) |
| 링크 | [arXiv:2606.31836](https://arxiv.org/abs/2606.31836) |
| 발행일 / 버전 | 2026-06-30 · v1 |
| 본문 확보 수준 | PDF 텍스트(PyMuPDF) |
| 분석 생성일 | 2026-07-01 |
| 관련 Pillar | P0, P2, P3 |
| 태그 | dataset, tactile, dexterity |
| 카탈로그 | dataset/robot/RoboTacDex |

<!-- 본문 확보: arXiv HTML(/html/2606.31836) 및 ar5iv 는 각각 HTTP 404 / 403 로
     실패. PDF(https://arxiv.org/pdf/2606.31836, 7쪽)를 받아 PyMuPDF 로 전문
     추출(약 40k자). 시스템에 pdftotext 미설치 → PyMuPDF 로 대체(동일 PDF-텍스트
     수준). PDF 텍스트 추출 특성상 표·그림·기호는 열화되므로 표 수치는 본문에서
     받은 그대로만 인용하고, 추출 잡음이 있는 항목은 그 사실을 명시합니다.
     PDF 수준 확보이므로 arXiv 그림 hotlink 는 수집하지 않습니다(placeholder 없음).
     본 논문은 순수 데이터셋 논문 → DESIGN APPLICABILITY gate 상 🚫 비대상(dataset).
     본문 전문 확보이므로 (본문 미확보 — 잠정) 마커는 붙이지 않습니다. -->

---

## 🧭 한 줄 요약 (TL;DR)

Unitree G1 휴머노이드 + Brainco Revo2 촉각형 다지 손으로 수집한 6k+ trajectory(약 25시간, 19 task / 23 skill / 22 object) 규모의 멀티뷰·멀티모달 조작 데이터셋으로, RGB-D 4시점 + 손가락별 촉각(normal/tangential force) + 언어 주석을 하드웨어-소프트웨어 동기화로 함께 기록합니다. Table I 기준 휴머노이드·다지 손·인간-로봇 상호작용·촉각·멀티뷰 5개 속성을 모두 갖춘 유일한 데이터셋이라 주장하며, ACT / DP / GROOT N1.5 세 정책으로 데이터 품질을 검증합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 휴머노이드 로봇용 고품질 조작 데이터셋이 극심하게 부족합니다. 고정 베이스 매니퓰레이터용 대규모 코퍼스는 성숙했지만, 고DOF·양손·다지 접촉을 담은 휴머노이드 데이터는 희소합니다.
- **기존 접근의 한계** — 단일 시점 순수 시각 입력은 복잡한 물리 상호작용과 진짜 일반화에 부족하고, 기존 휴머노이드 데이터셋(AgiBot World / RoboMIND / Humanoid Everyday)은 다지 손·촉각·멀티뷰 중 하나 이상이 빠져 있습니다.
- **본 논문의 가설** — 시각 + 깊이 + 촉각을 통합한 멀티모달 휴머노이드 데이터셋이 보편 embodied intelligence 를 향한 핵심 초석이며, 촉각은 시각적으로 모호하거나 숨은 latent 상태를 드러내는 핵심 피드백 채널이라는 가설입니다.
- **왜 지금 중요한가** — VLA·diffusion 정책이 급부상하지만 휴머노이드의 고차원 액션 공간을 촉각까지 담아 검증할 코퍼스가 없어 병목입니다. P0(데이터/벤치마크 스카우팅)의 D25(tactile/force/torque 코퍼스 우선 스카우팅) 결정에 정면으로 대응하는 신규 릴리스 후보입니다.

---

## 🧩 핵심 기여

- **멀티뷰·멀티모달 휴머노이드 상반신 조작 데이터셋** — 6k+ trajectory(약 25시간), 19 task / 23 skill / 22 object 를 Unitree G1 + Brainco Revo2 촉각형 다지 손으로 수집. 다양한 human-like task 를 커버.
- **이종 센서 동기화 수집 시스템** — 하드웨어-소프트웨어 co-synchronization 으로 여러 카메라 간 타임스탬프 misalignment 를 해결(밀리초 급). Unitree 공식 teleop 스크립트를 재설계해 depth·촉각 기록을 추가.
- **손가락별 촉각 기록** — 각 fingertip 의 normal/tangential force(방향 포함) + self-capacitance 근접 신호를 100Hz DDS 로 publish → 30Hz 로 다른 modality 와 정렬 기록.
- **표준 벤치마크 + ablation 검증** — ACT / DP / GROOT N1.5 세 대표 imitation learning 정책을 4개 task 에서 평가하고, 멀티뷰·촉각 관측 설계에 대한 ablation 을 수행해 데이터 품질과 modality 가치를 검증.
- **데이터셋 속성 포지셔닝** — Table I 비교에서 humanoid + dexterous hand + human-robot interaction + tactile sensing + multi-view camera 5개 속성을 동시에 갖춘 유일한 데이터셋으로 자리매김.

---

## 🔑 기술 키워드

- **Tactile Sensing** — 손가락 끝 접촉의 normal/tangential force 를 직접 측정하는 촉각 피드백. 본 데이터셋의 차별화 modality 이자 P0 D25 의 대상.
- **Dexterous Hand** — 다관절 손(여기선 Brainco Revo2, 12-DOF)으로 사람 손가락 수준의 조작을 수행하는 end-effector.
- **Humanoid Manipulation** — 양팔 + 다지 손을 가진 휴머노이드(Unitree G1)로 수행하는 상반신 양손 조작.
- **Teleoperation** — Meta Horizon VR 로 사람 상반신 동작을 포착해 로봇 관절에 매핑, 시연을 수집하는 방식.
- **Multi-view RGB-D** — 4대 RGB-D 카메라(head-centric / wrist ×2 / third-person)로 다각도 컬러 + 깊이 관측을 수집.
- **Multi-camera Synchronization** — 하드웨어(RealSense D435i) + 소프트웨어 결합으로 카메라 간 타임스탬프를 정렬하는 동기화 시스템.
- **Imitation Learning** — 전문가 시연을 모방해 정책을 학습. 데이터셋 검증에 ACT / DP / VLA 세 정책을 사용.
- **Vision-Language-Action (VLA)** — 여기선 GROOT N1.5. 대규모 사전학습 prior 로 일반화가 강한 베이스라인.
- **Proprioceptive Proximity Sensing** — self-capacitance 로 손가락과 외부 물체 사이 거리를 감지하는 근접 신호.
- **DDS (Data Distribution Service)** — 촉각/관절 상태를 100Hz 로 publish 하는 실시간 메시징 미들웨어.

---

## 🔬 방법론

> 데이터셋 논문이므로 이 섹션은 *학습 알고리즘* 이 아니라 *데이터 수집 플랫폼·파이프라인·데이터셋 구성* 을 분해합니다. 학습 목표/손실 하위절은 해당 없음(데이터셋 자체에 loss 가 없음).

### 직관

RoboTacDex 의 출발 문제의식은 단순합니다. 고정 베이스 로봇용 데이터는 넘치는데 휴머노이드용은 희소하고, 있더라도 대개 단일 카메라·그리퍼 중심이라 접촉이 풍부한 dexterous 작업을 담지 못한다는 것입니다. 저자들은 이 갭을 "시각만으로는 부족하다"는 관찰로 못박습니다 — 단일 시점 RGB 는 occlusion 과 물리 접촉 상태를 놓치므로, 멀티뷰 + 깊이(공간 기하)와 촉각(접촉 피드백)을 함께 기록해야 진짜 dexterous 조작을 학습할 수 있다는 논리입니다.

그래서 이 논문의 "방법"은 모델이 아니라 *수집 시스템* 입니다. 핵심은 세 가지 엔지니어링 결정으로 요약됩니다. (1) 하드웨어: Unitree G1 + 촉각형 Brainco 손 + 4대 RGB-D 카메라 + VR teleop. (2) 동기화: 서로 다른 주파수·프로토콜로 들어오는 카메라·촉각·관절 스트림을 밀리초 급으로 정렬하는 하드웨어+소프트웨어 결합 동기화. (3) 다양성: 기본 pick-and-place 를 넘어 "양손·다지 손이 아니면 불가능한" 상대적으로 어려운 task 를 의도적으로 설계.

마지막으로 저자들은 수집된 데이터를 실세계 로봇과 IsaacSim 양쪽에서 replay 해 기록이 올바른지 검증하는 루프를 둡니다. 즉 데이터 품질을 "다시 재생해서 맞는지 본다"는 방식으로 담보합니다.

### 데이터 수집 플랫폼 (하드웨어)

> "We employ a Unitree G1 humanoid robot for data collection: dual arms with 14 DOF and dual Brainco dexterous hands with 12 DOF" (§III-A)
(한글 해설 — 플랫폼은 공개 접근 가능한 Unitree G1 입니다. 양팔 14 DOF + 양손 각 12 DOF 로, 본문 실험부에서 손+팔 합산을 "up to 26 DOF" 로 표현하는 고차원 액션 공간입니다. 하반신·허리는 고정해 head 카메라가 desktop 을 일관되게 잡도록 안정화합니다.)

관측 구성:

- **4대 RGB-D 카메라** — head-centric 1대, wrist 장착 2대(다지 손 초점), third-person overview 1대. 해상도 640×480.
- **촉각형 손** — Brainco Revo2 Tactile version.

> "The dexterous hands are Brainco Revo2 Tactile version, capable of recording touch information such as normal forces and tangential forces on each finger." (§III-A)
(한글 해설 — 각 손가락에서 normal/tangential force 를 기록한다는 점이 이 데이터셋의 핵심 차별 modality 입니다. 대다수 대규모 코퍼스가 vision-only 인 것과 대비됩니다.)

- **Teleop** — 조작자가 Meta Horizon VR 를 착용해 상반신 동작을 포착, 팔·손가락 각 관절 모션으로 매핑.

### 데이터 파이프라인·동기화

프레임 구성과 주파수:

> "We record trajectories on high-frequency 30Hz." (§III-B)
(한글 해설 — 각 프레임은 팔·손가락 관절의 저차원 state, 4대 카메라의 RGB+depth(640×480), 양손 촉각, 팔·손가락 관절 action 을 담습니다.)

카메라 동기화는 하드웨어 + 소프트웨어 결합입니다. first-/third-person 카메라는 하드웨어 동기화를 지원하는 RealSense D435i 이고, head/third-person 과 wrist 카메라 사이는 소프트웨어 동기화로 스트림 간 시간 오정렬을 제거합니다. 동기화가 필요한 이유는 본문이 명확히 밝힙니다 — 서로 다른 시점이 시간적으로 어긋나면 같은 물리 상태가 서로 모순된 멀티모달 입력으로 잘못 모델링됩니다.

촉각·관절 스트림 전송:

> "Tactile information and joint state data from the dexterous hand are published at a frequency of 100Hz in the DDS messages form. The local computer receives these messages and records them at 30Hz alongside other modalities." (§III-B2)
(한글 해설 — 촉각/손 관절은 100Hz DDS 로 publish 되지만 최종 기록은 다른 modality 와 맞춰 30Hz 로 다운샘플됩니다.)

> "The tactile sensing modality provides normal and tangential contact forces (including direction) at each fingertip, along with proprioceptive signals derived from self-capacitance proximity sensing— the latter serving as a measure of the distance between the finger and external objects." (§III-B2)
(한글 해설 — 촉각 채널은 force 3성분(방향 포함)에 더해 self-capacitance 기반 근접(거리) 신호까지 제공합니다. 접촉 *직전* 의 거리 정보까지 담긴다는 뜻으로, 순수 force-only 촉각보다 풍부합니다.)

수집된 데이터는 실세계 로봇과 IsaacSim 시뮬레이션 양쪽에서 replay 해 기록의 정확성을 검증합니다.

### 데이터셋 구성·다양성

> "This dataset comprises 6k high-quality trajectories across 19 tasks, 23 skills, and 22 objects." (§IV)
(한글 해설 — 규모의 핵심 숫자입니다. 총 약 25시간 분량으로 본문 §I 에 명시됩니다.)

task 는 5개 manipulation type 으로 분류되며 한 trajectory 가 복수 type 에 속할 수 있습니다: (1) Basic, (2) Articulated, (3) Dual-arm Collaborative, (4) Fine, (5) Humanoid Interactive. 저자들은 기본 pick-and-place 위주 데이터셋과 차별화하기 위해 의도적으로 어려운 task 를 설계했다고 밝힙니다.

> "we defined multiple relatively challenging tasks that can only be completed by dual arms and dexterous hands" (§IV-A)
(한글 해설 — "양손+다지 손이 아니면 불가능한" task 를 데이터셋의 정체성으로 삼았다는 설계 의도입니다.)

object 도 5개 class 로 분류: Articulated / Constrained / Containers / Functional / Graspable. 환경 변인으로 robot-to-table 거리(5cm, 15cm) × 배경(white, green grid) 2×2 = 4개 config 를 대부분 task 에 대해 수집해 scene 요인이 성공률에 미치는 영향을 통제합니다. task 지속시간은 대부분 10–40초 구간에 분포합니다.

---

## 📊 실험 설정과 결과

### 데이터셋 비교 (Table I)

> "In contrast, our dataset distinguishes itself by compiling comprehensive multi-modal data, encompassing RGB, depth, tactile inputs and natural language annotations (see Table I)." (§II-B)
(한글 해설 — RoboTacDex 는 5개 속성(휴머노이드/다지 손/인간-로봇 상호작용/촉각/멀티뷰)을 동시에 만족하는 유일한 행이라는 것이 이 표의 요지입니다. ✓/✗ 는 PDF 추출본에서 재구성.)

| Dataset | # Traj | # Skills | Humanoid | Dexterous Hand | Human-Robot Interaction | Tactile Sensing | Multi-view Camera |
|---|---|---|---|---|---|---|---|
| RH20T [39] | 13k | 33 | ✗ | ✗ | ✗ | ✓ | ✓ |
| BridgeData [2] | 7.2k | 4 | ✗ | ✗ | ✗ | ✗ | ✓ |
| DROID [40] | 76k | 86 | ✗ | ✗ | ✗ | ✗ | ✓ |
| Open X-Embodiment [41] | 1400k | 217 | ✗ | ✗ | ✗ | ✗ | ✓ |
| Fourier ActionNet [44] | 13k | 16 | ✓ | ✓ | ✗ | ✗ | ✗ |
| RoboMIND [3] | 107k | 38 | ✓ | ✓ | ✗ | ✗ | ✗ |
| Agibot World [42] | 1000k | 87 | ✓ | ✗† | ✓ | ✗ | ✓ |
| Humanoid Everyday [43] | 10.3k | 221 | ✓ | ✓ | ✓ | ~* | ✗ |
| **RoboTacDex** | **6k** | **23** | **✓** | **✓** | **✓** | **✓** | **✓** |

† Mostly grippers and only a few dexterous hands. · * Only three-fingered (Dex-3) hand with tactile perception. (원문 표 각주 그대로.)

읽기: RoboTacDex 는 규모(# Traj 6k)로는 AgiBot World(1000k) / OXE(1400k)에 크게 못 미치지만, *modality 커버리지* 로 포지셔닝합니다. 특히 dexterous hand + tactile 을 동시에 가진 행은 RoboTacDex 뿐이며, RH20T 가 유일하게 촉각을 갖되(6축 F/T) 휴머노이드·다지 손이 아니라는 점이 P0 관점의 핵심 대비입니다.

### 데이터셋 통계 (Fig. 4a / Fig. 5)

| 축 | 분포 (원문 수치) |
|---|---|
| Object category (Fig. 5) | Graspable 33.6% · Constrained 26.0% · Containers 18.3% · Functional 11.7% · Articulated 8.4% |
| Atomic skills (Fig. 4a, 상위) | pick 21.0% · place 11.0% · align 9.0% · press 7.8% · insert 5.3% · pull 4.6% · rotate 4.5% · unscrew 2.9% · release 2.5% · receive 2.3% … |
| Task 지속시간 (Fig. 4b) | 대부분 10–40s 구간 |

> Fig. 4a 의 나머지 저비율 skill(brace/pinch/wedge/signal/hang/shielded grasp/wipe/deliver 등)은 PDF 그림 추출본에서 라벨·수치가 일부 열화되어 상위 legible 항목만 인용합니다. 원문 그림 확인 권장.

### 정책 성공률 (Table II)

> "we evaluate three policies on RoboTacDex: Action Chunking with Transformers (ACT) [13], Diffusion Policy (DP) [5], and GROOT N1.5 [33]." (§V)
(한글 해설 — 4개 task(PickAndPlacePear / TurnPage / InsertBook / UnscrewBottle), task 당 약 200 trajectory 학습, 정책당 task 당 10 trial. 관측은 head image + joint state 의 baseline 구성.)

| Task | ACT | DP | GROOT N1.5 |
|---|---|---|---|
| PickAndPlacePear | 0/10 | 3/10 | 9/10 |
| TurnPage | 6/10 | 5/10 | 6/10 |
| InsertBook | 4/10 | 3/10 | 4/10 |
| UnscrewBottle | 3/10 | 2/10 | 6/10 |
| **Average** | **3/10** | **3/10** | **6/10** |

> "We find that VLA generally outperforms the other two models, primarily due to its base model pretrained on large-scale manipulation datasets." (§V-A)
(한글 해설 — GROOT N1.5(VLA)가 평균 6/10 으로 ACT/DP(각 3/10)를 앞섭니다. 사전학습 prior 가 PickAndPlacePear 처럼 흔한 task 에서 강한 일반화를 준다는 해석. 반대로 InsertBook/UnscrewBottle 같은 드문 task 에서는 GROOT 도 semantic 요구·공간 제약 학습에 실패했다고 명시.)

정책별 분석: ACT 는 temporal ensemble 특성상 좌/우 손 선택 같은 multi-modality 가 있는 데이터에서 양손이 동시에 움직이되 목표에 도달하지 못하는 실패를 보입니다. DP 는 action score function 의 gradient 를 학습하므로 multimodal action 분포를 더 잘 표현합니다. 이는 데이터셋이 인간 시연 특유의 stochasticity·multimodality 를 담고 있어 관측→액션 매핑 학습을 어렵게 한다는 것을 정책별로 드러냅니다.

### Ablation — 멀티뷰 (Fig. 7a)

> "no model demonstrates significant performance improvement after adding wrist cameras or third-person perspective camera." (§V-B)
(한글 해설 — PickAndPlacePear/InsertBook 에서 wrist·third-person 카메라를 추가해도 유의한 향상이 없습니다. ACT/DP 는 multi-view 매칭·추가 supervision 기제가 없어 단순 concat 이 무효이고, GROOT 는 단순 task 의 단일 시점 성공률이 이미 높아 추가 뷰 이득이 없다는 해석. 즉 멀티뷰 이득은 모델이 시점 간 기하 관계를 추론할 수 있어야 실현된다는 결론 — P2 와 직결.)

### Ablation — 촉각 (Fig. 7b)

DP 로 UnscrewBottle(촉각-풍부 task)에서 촉각 유무를 비교. 촉각은 low-dimensional state 의 일부로 관측에 편입.

> "the failure patterns shift from Idle Spinning Failure without tactile sensing to Stuck/Adjusts Failure when tactile feedback is incorporated." (§V-B)
(한글 해설 — 성공률 자체는 오르지 않지만, 실패 양상이 "헛돎(Idle Spinning)"에서 "끼임/재조정(Stuck/Adjusts)"으로 이동합니다. 즉 촉각을 넣으면 손이 뚜껑을 더 잘 잡는다는 정성적 증거입니다.)

> "This outcome underscores the unique value of tactile sensing: it reveals latent state variables that are visually ambiguous or entirely hidden, especially when the visual scene remains static but the physical contact state changes dramatically." (§V-B)
(한글 해설 — 촉각의 가치는 *시각적으로 정지된 장면에서도 접촉 상태가 급변할 때* 숨은 latent 상태를 드러내는 데 있다는 핵심 주장. 성공률이 아닌 실패 모드 전환으로 modality 가치를 논증한 점이 방법론적으로 눈여겨볼 지점입니다.)

---

## ⚖️ 한계

- **촉각의 순진한(naive) 편입** — 저자 스스로 밝힌 한계입니다. 촉각을 dedicated multimodal fusion 아키텍처 없이 저차원 state 에 concat 하는 straightforward 방식으로만 넣었습니다. 그래서 촉각 ablation 에서 성공률이 오르지 않고 실패 모드만 이동한 것도 이 순진한 편입의 직접 귀결일 가능성이 큽니다 — modality 는 있으나 이를 활용할 fusion 이 없다는 뜻.
- **규모의 상대적 열세** — 6k trajectory 는 AgiBot World(1M+)/OXE(1.4M)와 두세 자릿수 차이입니다. 본문은 task 당 약 200 trajectory 학습이 "reasonable trajectory" 를 주지만 로봇 팔 대비 훨씬 많은 데이터가 필요하다고 인정합니다(26 DOF 고차원 액션 공간 탓). 사전학습 스케일 코퍼스로 단독 사용하기엔 작고, mix 의 한 성분으로서 가치가 큽니다.
- **평가 task·trial 수의 협소함** — 검증이 4개 task × 정책당 10 trial 로, 통계적으로 표본이 얇습니다. 0/10 ~ 9/10 의 넓은 분산은 정책 서열을 강하게 결론짓기엔 신뢰구간이 큽니다. 데이터셋 "품질 검증" 목적이라 이해되나, 벤치마크로서의 정밀도는 제한적입니다.
- **멀티뷰 이득 미실현** — 4시점을 수집했지만 실험에서 멀티뷰가 성능을 올리지 못했습니다. 이는 데이터셋 결함이 아니라 *현행 정책이 시점 간 기하를 추론하지 못한다*는 관측이지만, 데이터셋의 셀링 포인트(멀티뷰)가 기본 baseline 으로는 즉시 payoff 를 주지 못한다는 긴장을 남깁니다.
- **미공개 상태** — 본문 초록/결론이 "open-sourced soon" 이라 분석 시점(2026-07)에 실제 데이터·코드·라이선스가 확인되지 않습니다. 재현성·라이선스 평가가 릴리스 전까지 유보됩니다(아래 ♻️).
- **동기화 정량 근거 부족** — "millisecond synchronization" 을 주장하지만 정확한 오차 분포·측정 프로토콜의 수치가 본문 텍스트에서 확인되지 않아, 동기화 품질을 정량 검증하기 어렵습니다.

---

## ♻️ 재현성

- **데이터/코드** — "Our dataset will be open-sourced soon." (§Abstract). 분석 시점에 공개 URL·리포지토리·HuggingFace 링크가 논문 본문에 없어 미확인. 라이선스도 미상 → P0 D27(license/usability bar) 평가 유보.
- **하드웨어** — Unitree G1, Brainco Revo2 Tactile hands, Meta Horizon VR, Intel RealSense D435i 등 상용 부품 수준으로 기술되어 원리상 재제작 가능. 단 정확한 카메라 배치·캘리브레이션·teleop 매핑 세부는 텍스트로만 서술.
- **재생 검증 루프** — 실세계 + IsaacSim replay 로 기록 정확성을 검증한다는 절차가 명시되어, 릴리스 시 데이터 무결성 확인 경로가 있습니다.
- **소속/게재** — IEEE Robotics and Automation Letters(RA-L) 포맷. Venue Tier 3(저널, archival weight).

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P0(VLA Datasets & Benchmarks) — primary.** 본 논문은 P0 의 정중앙에 있는 신규 데이터셋 릴리스 후보입니다. 특히 D25(tactile/force/torque 데이터 스카우팅 — 희소성을 first-class gap 으로 취급)에 정확히 대응하는 *촉각-보유 코퍼스* 입니다. RH20T(6축 wrist F/T)가 P0 핀의 유일한 tactile/torque 코퍼스인데, RoboTacDex 는 *손가락별(fingertip) normal/tangential force + 근접 신호* 라는 더 세밀한 접촉 modality 를 제공한다는 점에서 D25 라인업에 직접 들어옵니다.
- **P0 D24(priority data axis)** — 다만 데이터 축으로는 *로봇 teleop(third-person 포함) 휴머노이드* 이지 *egocentric human video* 가 아닙니다. D24 v1 이 egocentric human video 를 우선 축으로 두고 로봇-action 코퍼스는 down-weight 하므로, RoboTacDex 는 "촉각 때문에 D25 로 승격되지만 D24 우선축에서는 보조" 라는 이중 포지션입니다.
- **P0 D26(benchmark/eval scope)** — 3-policy(ACT/DP/GROOT) 표준 평가 + 멀티뷰/촉각 ablation 을 제공하므로 dexterous·contact-rich 실로봇 eval 후보로 기록할 수 있습니다. 단 4 task × 10 trial 규모라 정밀 벤치마크보다는 데이터 검증 harness 수준.
- **P0 D27(license/usability bar)** — "open-sourced soon" → 라이선스 미상. ⚠️ 플래그로 tracked, 릴리스 후 재평가.
- **P2(Structured Multimodal Observation Fusion) — secondary.** 멀티뷰가 단순 concat 으로는 이득이 없다는 ablation 은 P2 의 핵심 주장(flat-concat 초월, 시점 간 기하 grounding 필요; D8 multi-camera spatial-geometric grounding)을 *데이터로 뒷받침* 하는 antagonist-free 증거입니다. 손가락별 촉각 토큰(D11 proprio-tactile-force token) 구성의 원천 데이터로도 유용.
- **P3(Hand-level System0) — secondary.** 손가락별 force + 근접 신호는 System0 의 입력 modality(D15, tactile + finger joint state)와 정확히 일치하는 real-robot 촉각 스트림이라, System0 sim2real(D18) 검증용 실측 데이터로 가치가 있습니다.
- **Identity 지지/긴장** — Identity 의 "per-finger proprio-tactile binding, flat-concat 초월" 주장을 데이터 측면에서 지지합니다(촉각의 latent-state 가치 + 멀티뷰 concat 무효 증거). 긴장은 없음 — method 를 제안하지 않으므로 아키텍처 청구와 충돌하지 않습니다.

---

## ✨ 핀 논문 대비 델타

- **vs RH20T (P0 §5 핀, [arXiv:2307.00595]) — 촉각 modality 의 세밀도.** RH20T 는 6축 *wrist* F/T + audio 의 contact-rich 코퍼스이지만 그리퍼·고정베이스입니다. RoboTacDex 는 *휴머노이드 + 다지 손 + fingertip 별* normal/tangential force + self-capacitance 근접 신호로, 접촉 부위가 wrist→손가락으로 내려온 것이 핵심 델타입니다. P3/System0 의 "손가락별 접촉 유지" 문제에 RH20T 보다 직접적인 데이터.
- **vs AgiBot World (P0 §5 핀, [arXiv:2503.06669]) — 규모↔modality 트레이드.** AgiBot World 는 1M+ 휴머노이드 bimanual 이지만 dexterous hand 비중이 작고 촉각이 없습니다(Table I). RoboTacDex 는 규모를 100× 이상 포기하는 대신 dexterous+tactile+multi-view 를 모두 확보 — "작지만 접촉 modality 완비" 라는 상보적 위치.
- **vs Humanoid Everyday ([43], 비핀) — 멀티뷰 유무.** Humanoid Everyday 는 휴머노이드+다지 손+HRI+촉각(3지 Dex-3 한정)을 갖되 *멀티뷰가 없습니다*. RoboTacDex 는 4시점 멀티뷰를 더한 것이 델타이며, 이는 P2(멀티뷰 grounding) 연구용 데이터로서의 차별점입니다.

---

## ⚙️ 의사결정 함의

- **`catalogs/datasets.md` 신규 row 후보** — `dataset/robot/RoboTacDex` 로 라우팅. 축 = 🤖 robot(+tactile). 기록 컬럼: modality(RGB-D×4 + fingertip tactile + NL), scale(6k traj / ~25h), embodiment(Unitree G1, 14+12×2 DOF), license(TBD — "open-sourced soon" ⚠️), lineage(신규, RH20T 계열 tactile 축). D25 대상으로 우선 태깅.
- **D25 스카우팅 갱신** — tactile/torque 코퍼스 목록에 fingertip-force 급 신규 항목으로 추가. RH20T(wrist F/T) 옆에 "fingertip normal/tangential + proximity" 세밀도 축을 한 칸 넓히는 근거.
- **P2 ablation 설계 입력** — "멀티뷰 concat 은 무효, 기하 추론 기제가 있어야 이득" 이라는 이 논문의 관측을 우리 D8(multi-camera spatial-geometric grounding) 실험의 *baseline 대비군* 근거로 인용. 구체적으로 `obs.multiview_fusion ∈ {concat, geometry_grounded}` sweep 에서 concat 이 flat-payoff 라는 외부 증거.
- **릴리스 감시 트리거** — 데이터 공개 시(라이선스 확인 후) P3/System0 sim2real(D18) 검증용 실측 촉각 스트림 후보로 재평가. 공개 전까지는 catalog 에 ⚠️ pending 으로만 등재.

---

## ⚠️ 먼저 검증할 실패 모드

- **데이터가 아직 없다(가장 싼 체크)** — "open-sourced soon" 이므로 실제 URL·라이선스·포맷을 확인하기 전에는 우리 파이프라인 편입을 확정할 수 없습니다. 가장 싼 sanity check 는 arXiv/저자 페이지에서 릴리스 여부와 라이선스(Apache/CC-BY vs NC)를 먼저 확인하는 것 — NC 이면 D27 상 downstream-use 위험 플래그.
- **촉각 포맷이 우리 손(Sharpa)과 다르다** — Brainco Revo2 의 fingertip force(normal/tangential) + self-capacitance 근접은 Sharpa Deform Map(vision-based 320×240/finger)와 *센서 물리·표현이 다릅니다*. 우리 P2 의 "swappable sensor head + common token format" 으로 흡수 가능한지, 즉 force-vector 촉각을 우리 tactile 토큰 스키마로 재매핑할 수 있는지 확인이 선행 조건.
- **DOF/embodiment 불일치** — Unitree G1(14+12×2 DOF) 액션 공간은 우리 target hardware(Sharpa 22-DOF hand + 미정 6–7 DOF arm)와 다릅니다. teleop 매핑·정규화 통계가 우리 embodiment 로 그대로 전이되지 않으므로, retarget 없이 direct co-train 하면 액션 분포 mismatch 로 학습이 흔들릴 위험.
- **30Hz·표본 규모의 학습 신호 한계** — task 당 200 trajectory 로도 "reasonable" 수준이라는 것은, 우리 data-efficient adaptation(minutes-of-deploy-data) 목표와는 스케일 가정이 다릅니다. 이 데이터를 *사전학습 mix 성분* 으로 쓸 때와 *few-shot adaptation* 대상으로 쓸 때를 구분해야 하며, 후자로 오인하면 기대치 mismatch.
- **멀티뷰·촉각의 payoff 가 modality 편입 방식에 종속** — 본 논문에서 두 modality 모두 성공률을 못 올렸습니다. 우리가 이 데이터로 멀티뷰/촉각 이득을 재현하려면 *fusion 아키텍처*(P2 D10 beyond-concat)를 반드시 함께 도입해야 하며, flat-concat baseline 으로 검증하면 "데이터가 쓸모없다" 는 잘못된 결론에 도달할 수 있습니다.

---

## 💡 컨텍스트 제안

- **P0 §5 catalog 반영 제안** — `catalogs/datasets.md` 에 `RoboTacDex` 를 🤖 robot(+tactile) 항목으로 추가 검토(license TBD ⚠️, D25 태그). 핀 8개 캡은 유지하되, RH20T 옆의 tactile 축을 "fingertip-force 세밀도" 로 한 줄 보강하는 후보로 기록. `context/*` 는 수정하지 않았습니다 — 제안만.
- **D25 노트 보강 후보** — "wrist 6축 F/T(RH20T)" 중심이던 tactile/torque 스카우팅 범위에 "fingertip normal/tangential + self-capacitance 근접(RoboTacDex)" 세밀도 급을 명시적으로 포함하도록 D25 노트 확장 검토.
- **릴리스 트리거** — 데이터 공개 감지 시(다음 P0 스카우팅 라운드) 라이선스·포맷 확인 후 catalog pending→confirmed 승격. 공개 전까지는 등재 보류 권장.
- context/MASTER.md 및 context/P0.md 는 수정하지 않았습니다 — 위는 모두 제안입니다.

---
