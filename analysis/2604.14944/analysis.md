# Paper Analysis — HRDexDB: A Paired Human-Robot Dataset for Cross-Embodiment Dexterous Grasping

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | HRDexDB: A Paired Human-Robot Dataset for Cross-Embodiment Dexterous Grasping |
| 저자 | Jongbin Lim, Taeyun Ha, Mingi Choi, Jisoo Kim, Byungjun Kim, Subin Jeon, Hanbyul Joo (Seoul National University · RLWRLD) |
| 링크 | [arXiv:2604.14944](https://arxiv.org/abs/2604.14944) · [Website](https://snuvclab.github.io/HRDexDB/) |
| 발행일 / 버전 | 2026-04-16 · v2 (2026-06-19) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-07-01 |
| 관련 Pillar | P0, P1, P3, P2 |
| 태그 | dataset, dexterity, tactile |
| Design 적용 | 🚫 비대상 (dataset) |

---

## 🧭 한 줄 요약 (TL;DR)

동일 물체를 대상으로 **인간 손 + 4종 dexterous 로봇 핸드**(Allegro V4 / V5 Plus, Inspire RH56DFTP / RH56F1)가 의미적으로 대응되는 grasp 을 수행한 것을 21개 exocentric + 2개 egocentric RGB 로 markerless 캡처한 **paired cross-embodiment dexterous grasping 데이터셋** HRDexDB 를 제안합니다 — 100 objects / 2.1K sequences / 24M frames 에 3D hand motion · object 6D pose · 로봇 tactile force · 성공/실패 라벨을 동기화해 제공합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 인간의 손 조작을 로봇에게 전이하려면 단순 imitation 이상이 필요하며, human↔robot 및 robot↔robot 간 morphology · kinematics · actuation 차이(embodiment gap)를 넘어 **grasp 전략을 어떻게 전이할지**가 열린 문제입니다.
- **기존 접근의 한계** — 기존 데이터셋은 (a) 인간 손 중심(HOI)이라 로봇 대응이 없거나, (b) 로봇 중심이라 object motion 이 부분적으로만 추적되거나, (c) paired human–robot 이더라도 **다수 dexterous 로봇 임바디먼트를 공유 물체 위에서** 대응시키지 못하고 markerless RGB / tactile 이 빠져 있습니다.
- **본 논문의 가설** — 같은 물체·같은 workspace 에서 인간과 여러 로봇 핸드의 **의미적으로 대응되는** grasp 을 나란히 캡처하면, human→robot 및 cross-embodiment 로 grasp 전략을 학습·전이할 수 있는 foundational benchmark 가 된다는 것입니다.
- **왜 지금 중요한가** — anthropomorphic dexterous 핸드가 parallel gripper 를 넘어 확산되면서, 인간 시연을 다종 로봇 손에 어떻게 이식하느냐가 dexterous manipulation 학습의 병목이 되었습니다.

---

## 🧩 핵심 기여

- **HRDexDB 데이터셋** — 최초의 markerless paired human-robot dexterous manipulation 데이터셋. 100 objects 를 인간 + 4 dexterous 로봇 핸드가 조작하며, multi-view 관측 · 3D hand 및 object 6D annotation · tactile-enabled 로봇 핸드의 tactile 신호를 제공(제출 시점 100+ objects, 1,000 objects 로 확장 중).
- **멀티카메라 캡처·복원 시스템** — 21개 calibrated exocentric + 2개 egocentric 카메라로 severe hand–object occlusion 하에서 동기화된 3D hand-robot-object 추적 + tactile 취득을 수행하는 통합 하드웨어·소프트웨어 파이프라인.
- **다운스트림 벤치마크 4종** — human-to-robot contact map transfer, cross-embodiment grasp retrieval, 3D hand pose estimation, dexterous grasping 하 object 6D pose estimation 을 HRDexDB 위에서 정의·평가.
- **공유 물체 위 paired 캡처** — 인간 dexterity 와 로봇 실행을 comparable 한 grasp motion 으로 정렬해, "인간의 손 재주가 다양한 로봇 손으로 어떻게 전이되는가"를 데이터 기반으로 연구할 수 있게 함.

![Figure 1 — HRDexDB paired human-robot 개요](https://arxiv.org/html/2604.14944/x1.png)

> "Figure 1: Overview of HRDexDB. HRDexDB contains paired human and robotic dexterous grasping episodes across 100 objects and multiple hand embodiments. Using a synchronized multi-view capture system, we record comparable human demonstrations and robotic executions with reconstructed 3D hand and robot trajectories, object 6D poses, egocentric observations, contact force signals from robotic hands equipped with tactile sensors, and success/failure annotations." (§1)
(한글 해설 — 동일 물체 위에서 인간 시연과 로봇 실행을 나란히 캡처하고, 복원된 3D hand/robot 궤적 · object 6D pose · egocentric 관측 · contact force · 성공/실패 라벨이 하나의 paired 레코드로 묶인다는 데이터셋 전체 구조를 한 장으로 보여줍니다.)

---

## 🔑 기술 키워드

- **Cross-embodiment dexterous grasping** — 인간 손과 서로 다른 dexterous 로봇 손들이 같은 물체를 잡는 문제 — "같은 의도, 다른 손"의 grasp 전략을 손 종류를 넘나들며 정렬.
- **Paired human-robot capture** — 동일 물체·워크스페이스에서 인간 grasp 과 그에 대응하는 로봇 grasp 을 나란히 기록한 데이터 — 두 임바디먼트를 semantic 수준에서 짝지음.
- **Markerless multi-view reconstruction** — 마커 없이 다수 calibrated 카메라만으로 3D hand/object 를 복원 — 손·물체에 부착물 없이 자연스러운 grasp 을 캡처.
- **MANO** — 손의 pose+shape 를 저차원 파라미터로 표현하는 parametric 손 모델 — 인간 손 모션을 51-dim 벡터로 압축.
- **Object 6D pose tracking** — 물체의 3D 위치+회전(SE(3))을 시간축으로 추적 — grasp 중 물체가 어떻게 움직였는지의 ground truth.
- **Contact map transfer** — 인간 접촉 패턴을 로봇 손 특유의 접촉 맵으로 변환하는 학습 — "인간이 여기를 잡았다"를 "이 로봇 손은 여기를 잡아야 한다"로 번역.
- **Latent-space grasp retrieval** — 공유 임베딩 공간에서 인간 grasp 쿼리로 feasible 로봇 grasp 후보를 검색 — CLIP-style 대조학습으로 cross-embodiment grasp 를 정렬.
- **Tactile-enabled robot hand** — fingertip 에 촉각 센서를 단 로봇 손 — grasp 중 contact force 신호를 함께 기록.
- **Exocentric / egocentric views** — 워크스페이스를 둘러싼 외부 시점(21) + 어깨/헬멧 장착 1인칭 시점(2) — occlusion 이 심한 dexterous 조작을 dense 하게 커버.

---

## 🔬 방법론

> **참고** — 본 논문은 데이터셋 논문(Design 비대상)입니다. 아래 "방법론"은 이식 가능한 단일 알고리즘이 아니라 **데이터셋 구축 파이프라인**(캡처 시스템 · paired 취득 프로토콜 · multi-modal 복원)과, 데이터의 가치를 보이기 위한 **부수 baseline** 을 정리한 것입니다.

### 직관

HRDexDB 의 핵심 난제는 "같은 물체를, 인간과 여러 로봇 손이, 의미적으로 같은 방식으로 잡는 장면을, 마커 없이, 3D 로 정확히 기록"하는 것입니다. dexterous grasp 은 손가락이 물체를 감싸므로 self-occlusion 과 hand–object occlusion 이 극심하고, 단일 시점으로는 3D hand/object 를 안정적으로 복원할 수 없습니다. 그래서 워크스페이스를 삼면 프레임으로 둘러싼 **21대 exocentric 카메라**로 dense 하게 관측하고, 여기에 1인칭 관측을 위한 2대 egocentric 카메라를 더합니다.

"paired" 는 두 단계 프로토콜로 만듭니다. 먼저 인간이 물체를 자연스럽게 잡고, 그 multi-view 기록으로 인간 손 모션과 물체 궤적을 복원합니다. 이어서 teleoperator 가 그 시연을 보고 **의미적으로 대응되는** grasp 을 로봇 손으로 재현하되, morphology·kinematics·timing 의 임바디먼트별 차이는 허용합니다. 이 "같은 의도, 다른 손" 정렬이 데이터셋의 정체성입니다.

복원은 세 축입니다. 인간 손은 multi-view HaMeR keypoint → triangulation → MANO 최적화로, 물체 6D 는 FoundationStereo depth + SAM3 mask + FoundationPose 로, 그리고 두 결과를 통일된 world 좌표계에 정렬합니다. occlusion 하 drift 를 막기 위해 물체 mesh 를 모든 뷰에 렌더링해 silhouette 불일치를 최소화하는 cross-view 일관성 제약을 겁니다.

데이터의 가치는 두 부류의 baseline 으로 시연됩니다 — (1) 인간 접촉을 로봇 접촉으로 번역하는 **contact map transfer**, (2) 인간 grasp 쿼리로 로봇 grasp 을 검색하는 **latent-space retrieval**. 둘 다 HRDexDB 의 paired 신호가 있어야 학습 가능하다는 점이 요지입니다.

### 데이터셋 구성

각 trial 은 시간 인덱스 시퀀스로 표현됩니다. 로봇 trial (식 1):

$$\mathcal{T}^{\mathrm{robot}}=\left\{\{\mathbf{I}^{c_{i}}_{t}\}_{c_{i}=1}^{21},\,\mathbf{I}^{\mathrm{ego}}_{t},\,\mathbf{q}^{\mathrm{robot}}_{t},\,\mathbf{T}^{\mathrm{object}}_{t},\,\mathbf{F}^{\mathrm{tactile}}_{t},\,y\right\}_{t=1}^{T_{r}}$$

> "Here, $`\mathbf{I}^{1..21}_{t}`$ and $`\mathbf{I}^{\mathrm{ego}}_{t}`$ denote synchronized exocentric and egocentric RGB observations, $`\mathbf{q}^{\mathrm{robot}}_{t}`$ denotes the robot state, $`\mathbf{T}^{\mathrm{object}}_{t}\in\mathrm{SE}(3)`$ represents the object 6D pose. Tactile signals $`\mathbf{F}^{\mathrm{tactile}}_{t}`$ are measured from tactile-enabled robot fingertips, and $`y\in\{0,1\}`$ indicates whether the grasp was successful." (§3.1)
(한글 해설 — 로봇 레코드는 21개 exo + 1개 ego RGB, 로봇 상태 $`\mathbf{q}`$, 물체 6D pose $`\mathbf{T}\in\mathrm{SE}(3)`$, fingertip tactile force $`\mathbf{F}`$, 성공/실패 라벨 $`y`$ 로 구성되며, tactile 은 촉각 센서가 있는 손에서만 기록됩니다.)

인간 trial (식 2)은 로봇 상태 대신 MANO pose 를 담습니다:

$$\mathcal{T}^{\mathrm{human}}=\left\{\{\mathbf{I}^{c_{i}}_{t}\}_{c_{i}=1}^{21},\,\mathbf{I}^{\mathrm{ego}}_{t},\,\mathbf{\theta}^{\mathrm{human}}_{t},\,\mathbf{T}^{\mathrm{object}}_{t},\,y\right\}_{t=1}^{T_{h}}$$

> "where $`\mathbf{\theta}^{\mathrm{human}}_{t}\in\mathbb{R}^{51}`$ denotes MANO pose parameters and $`T_{h}`$ is the human sequence length." (§3.1)
(한글 해설 — 인간 손은 51-dim MANO pose 파라미터 $`\mathbf{\theta}`$ 로 표현되어, 로봇의 관절 상태 $`\mathbf{q}`$ 와 서로 다른 표현이지만 같은 물체 6D pose $`\mathbf{T}`$ 를 공유합니다.)

- **임바디먼트** — 인간 손 + 4 로봇 핸드: **Allegro Hand V4 · V5 Plus**, **Inspire Hand RH56DFTP · RH56F1** (Table 1 의 `#Emb.` = 5).
- **규모** — 24M frames · 2.1K sequences · 100 objects (제출 시점, 1,000 objects 로 확장 중).
- **뷰/해상도** — 21 exocentric + 2 egocentric = 23 views, $`2048\times1536`$.
- **모달리티** — 동기화 exo/ego RGB, 3D human hand motion(MANO), robot states, object 6D pose trajectory, scanned 3D object model, tactile 신호(tactile-enabled 손), 성공/실패 라벨.

### 캡처 시스템 & paired 취득 프로토콜

![Figure 2 — 캡처·복원 파이프라인](https://arxiv.org/html/2604.14944/x2.png)

> "Figure 2: Capture and Reconstruction Pipeline. Multi-view recordings are processed to reconstruct hand motion and object 6D trajectories, producing aligned human and robot grasps." (§3.2)
(한글 해설 — 다시점 기록 → hand motion / object 6D 궤적 복원 → 인간·로봇 grasp 정렬로 이어지는 전체 파이프라인을 보여줍니다.)

> "Our capture platform (Fig. 2) consists of a 21-camera RGB rig on a three-sided metal frame surrounding the workspace, enabling dense multi-view capture under severe hand–object occlusions, plus stereo egocentric views from an over-the-shoulder rig for robotic trials and a custom stereo helmet for human demonstrations." (§3.2)
(한글 해설 — 삼면 프레임의 21대 exo rig 가 occlusion 대응 dense 커버리지를 만들고, egocentric 은 로봇 trial 은 어깨 위 rig, 인간 시연은 맞춤 stereo helmet 으로 확보합니다.)

- **텔레오퍼레이션** — Xsens inertial motion-capture suit + MANUS gloves 로 오퍼레이터의 손목·손가락 모션을 로봇 팔·손에 매핑.
- **2단계 paired 프로토콜** — (1) 인간이 target object 를 자연스럽게 grasp → multi-view 로 인간 손 모션·물체 궤적 복원, (2) teleoperator 가 시연을 관찰 후 grasp intent 를 보존하되 임바디먼트별 morphology·kinematics·timing 차이를 허용하며 로봇으로 대응 grasp 수행.

### Multi-modal 복원

- **인간 손 복원** — MANO parametric model 사용. GigaHands 의 multi-view fitting 전략을 따라 각 calibrated 뷰에서 HaMeR 로 2D keypoint 검출 → 3D joint triangulation → 프레임별 MANO pose 최적화. subject 별 hand shape 는 SAM3 mask 기반 silhouette alignment 로 캘리브레이션, temporal filtering 으로 jitter 감소.
- **물체 6D 추적** — 지정된 calibrated stereo pair 로 FoundationStereo dense depth 추정, SAM3 로 object mask 취득, CAD model + RGB-D 로 FoundationPose 6D 추정(첫 프레임 global registration 초기화 → 이후 temporal tracking). 단일 시점 drift 를 막기 위해 물체 mesh 를 모든 calibrated 뷰에 렌더링해 cross-view silhouette 불일치를 최소화.

### 부수 baseline (데이터 가치 시연용)

- **(1) Human-to-Robot Contact Map Transfer (§4.1)** — 물체 point cloud $`O\in\mathbb{R}^{N\times 3}`$ 위의 contact map $`C\in[0,1]^{N}`$ (per-point 접촉 확률)과 part map $`P`$ (접촉점→hand part 할당)로 grasp 을 표현. 인간 표현 $`[C^{h},P^{h}]`$ (part map $`P^{h}\in\mathbb{R}^{N\times 6}`$) + PointNet++ object feature 를 조건으로 로봇 표현 $`[C^{r},P^{r}]`$ (Inspire $`B=6`$, Allegro $`B=5`$)을 예측. $`C^{r}`$ 에 contact-weighted $`L_{1}`$, $`P^{r}`$ 에 접촉점 cross-entropy 로 supervise. 손별 개별 모델 학습, 예측 contact 로 CEDex 물리 기반 optimizer 를 돌려 grasp 합성.
- **(2) Latent-Space Robot Grasp Retrieval (§4.2)** — CLIP-style multi-branch retrieval. 인간 손 / Inspire-F1 / Allegro-V5 별 point-cloud encoder + 공유 object encoder 를 shared embedding 으로 사영, symmetric contrastive loss 로 paired cross-embodiment grasp 을 가깝게 학습. 추론 시 인간 grasp 쿼리로 로봇 grasp 후보를 유사도 랭킹, 상위 grasp 을 BODex fine stage 초기화에 사용.

---

## 📊 실험 설정과 결과

> 본 논문의 "실험"은 method 성능 경쟁이 아니라 **데이터셋의 유용성**(전이 학습 가능성 + perception 벤치마크 난이도)을 보이는 것이 목적입니다.

### 데이터셋 비교 (Table 1)

HRDexDB 는 HROI(Human-Robot-Object Interaction) 타입에서 **dexterous 로봇 핸드 · tactile · markerless · 3D hand · object 6D 를 동시에** 제공하는 유일한 항목이라고 주장합니다.

| Dataset | Type | #Emb. | Dex Hand | Views | Objs | Seqs | Frames | Tactile | M-less | 3D Hand | Obj 6D |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RealDex [23] | ROI | 1 | ✓ | 4 | 52 | 2.6K | 955K | ✗ | ✓ | ✓ | ✓ |
| RH20T [10] | HROI | 7 | ✗ | 7 | – | 220K | 50M | ✓ | ✓ | ✗ | ✗ |
| DexWild [41] | HROI | 2 | ✓ | 6 | 180 | 10K | – | ✗ | ✗ | ✗ | ✗ |
| H&R [49] | HROI | 2 | ✗ | 1 | – | 2.6K | 1M | ✗ | ✓ | ✗ | ✗ |
| **HRDexDB (Ours)** | HROI | 5 | ✓ | 23 | 100 | 2.1K | 24M | ✓ | ✓ | ✓ | ✓ |

(읽기 — RH20T·H&R 는 parallel-jaw 위주라 dexterous 손이 없고(또는 3D hand/6D 결측), DexWild 는 dexterous 이나 markerless·3D annotation 이 없습니다. HRDexDB 는 5 임바디먼트 · 23 뷰 · tactile · markerless · 3D hand · object 6D 를 모두 채운 유일 행입니다.)

### 벤치마크 1 — Human-to-Robot Contact Map Transfer (Table 2)

> "Transferred-Contact improves success over directly using human contact maps in both simulation and real hardware, showing that HRDexDB enables learning robot-specific contact strategies from paired human–robot grasps." (§4.1)
(한글 해설 — 인간 접촉을 그대로 쓰는 것보다, paired 데이터로 학습한 **로봇 특화 접촉 맵**으로 optimize 하면 sim·real 모두에서 grasp 성공률이 오릅니다. optimizer 는 동일하고 contact term 만 다르므로 접촉 표현의 효과가 분리됩니다.)

| Method | Inspire Sim ↑ | Inspire Real ↑ | Allegro Sim ↑ | Allegro Real ↑ |
|---|---|---|---|---|
| Human-Contact | 54.6 | 66.7 | 60.2 | 63.3 |
| Transferred (Ours) | **55.6** | **73.3** | **65.8** | **80.0** |

(읽기 — 이득은 특히 real hardware 에서 큽니다: Allegro real 63.3→80.0(+16.7%p), Inspire real 66.7→73.3(+6.6%p). Sim 이득은 상대적으로 작습니다(Allegro +5.6%p, Inspire +1.0%p). Sim trials 1000/1000, real trials 60/30(Inspire/Allegro).)

### 벤치마크 2 — Cross-Embodiment Grasp Retrieval (Table 3–4)

| Retrieval Direction | R@1 | R@3 | R@5 |
|---|---|---|---|
| Human → Inspire | 36.36% | 81.82% | 100.00% |
| Human → Allegro | 24.24% | 63.64% | 72.73% |
| Inspire → Allegro | 8.18% | 57.58% | 72.73% |

(읽기 — 33개 후보 중 랭킹. random 대비 크게 상회해 paired 데이터가 embodiment-aware latent 표현을 유도함을 시사합니다. Human→Inspire 가 가장 쉽고(R@5 100%), robot→robot(Inspire→Allegro)은 R@1 8.18% 로 가장 어렵습니다 — 임바디먼트 간극이 클수록 정렬이 어렵다는 신호.)

BODex refinement 초기화 (Table 4) — retrieval 기반 초기화가 vanilla·kinematic retargeting 을 능가:

| Init. | Inspire-F1 seed% | Allegro-v5 seed% | Inspire-F1 ep% | Allegro-v5 ep% |
|---|---|---|---|---|
| Vanilla | 3.39 | 16.24 | 69.70 | 84.85 |
| Kinematic Retargeting | 3.52 | 1.21 | 42.42 | 30.30 |
| Retrieval-top5 | 10.79 | 17.09 | 75.76 | **93.94** |
| Retrieval-top1 | **12.24** | **21.33** | 57.58 | 75.76 |

> "Retrieval-top1 yields the highest seed success, whereas Retrieval-top5 yields the highest episode success, reflecting a precision–coverage trade-off between the best single prior and multiple candidate priors." (§4.2)
(한글 해설 — 단일 최상위 prior(top1)는 seed 단위 성공에, 다섯 개 분산(top5)은 episode 단위 coverage 에 유리한 precision–coverage trade-off 입니다. kinematic retargeting 은 임바디먼트 mismatch 하 직접 pose 전이라 오히려 vanilla 보다 나빠집니다.)

### 벤치마크 3 — 3D Hand Pose Estimation (Table 5–6)

> "Table 6 shows that all evaluated models incur consistently higher errors on our dataset than on FreiHAND [53], confirming that our benchmark poses a more challenging setting." (§4.3)
(한글 해설 — WiLoR·HaMeR·Hamba·MeshGraphormer·FrankMocap 5종 모두 FreiHAND 대비 오차가 커집니다($`\Delta=\text{Ours}-\text{FreiHAND}>0`$) — dexterous 조작 하 occlusion 이 hand pose 추정을 더 어렵게 만든다는 것으로, HRDexDB 가 도전적 perception 벤치마크임을 보입니다. 단 논문 본문이 Table 5/6 을 혼용 참조합니다.)

| Model | Ours PA-MPJPE ↓ | Ours PA-MPVPE ↓ | ΔPA-MPJPE | ΔPA-MPVPE |
|---|---|---|---|---|
| WiLoR | 5.94 | 6.09 | +0.23 | +0.82 |
| HaMeR | 6.15 | 6.16 | +0.04 | +0.44 |
| Hamba | 6.11 | 6.10 | −0.03 | +0.26 |
| MeshGraphormer | 8.31 | 8.10 | +1.67 | +1.32 |
| FrankMocap | 10.61 | 12.48 | +1.09 | +0.84 |

데이터로서의 가치(Table 6) — HRDexDB 6k 샘플을 finetuning 셋(10개 데이터셋 집계 2.7M 샘플)에 섞으면 HaMeR·WiLoR 둘 다 FreiHAND 에서 PA-MPJPE·PA-MPVPE 가 개선(예: HaMeR 6.108→6.027, WiLoR 5.711→5.677) — redundant 가 아니라 complementary signal 임을 시사.

### 벤치마크 4 — Object 6D Pose Estimation (Table 7–8)

> "Table 7 shows that all methods perform worse under robot grasping than under paired human grasping. This suggests that robotic hands introduce additional ambiguities for object localization, as rigid links and fingertips can overlap with object boundaries and produce object-like visual structures." (§4.4)
(한글 해설 — FoundPose·GigaPose·PicoPose(± MegaPose) 모두 robot grasp 프레임에서 human 대비 ADD↑·ARMSSD↓ 로 악화됩니다($`\Delta=\text{Robot}-\text{Human}`$) — 로봇 손의 rigid link·fingertip 이 물체 경계와 겹쳐 object-like 시각 구조를 만들어 localization 이 더 어려워지기 때문입니다.)

| Method | Human ADD↓ | Robot ADD↓ | Δ ADD | Human ARMSSD↑ | Robot ARMSSD↑ | Δ ARMSSD |
|---|---|---|---|---|---|---|
| FoundPose | 6.91 | 8.74 | +1.83 | 44.10 | 33.30 | −10.80 |
| FoundPose + MegaPose | 3.35 | 4.40 | +1.05 | 70.00 | 64.10 | −5.90 |
| GigaPose | 13.10 | 13.80 | +0.70 | 19.70 | 17.30 | −2.40 |
| GigaPose + MegaPose | 5.99 | 8.02 | +2.03 | 54.10 | 49.20 | −4.90 |
| PicoPose | 6.31 | 8.39 | +2.08 | 48.40 | 38.80 | −9.60 |

데이터로서의 가치(Table 8) — MegaPose refiner 를 100k GSO synthetic + 5.3k HRDexDB robot-grasp annotation 으로 fine-tune 하면(OmniRobotHome held-out 평가) 평균 ADD-S 가 상대 **10.2%** 개선(4.40→3.95cm) — interaction-centric 세팅으로의 적응을 supervise 할 수 있음을 시사.

---

## ⚖️ 한계

- **Tactile heterogeneity (저자 명시)** — tactile 은 로봇 손에서만 가용하고 플랫폼별 sensor 스펙이 달라 통일된 촉각 분석이 어렵습니다. 저자는 normalization / shared latent tactile 표현을 향후 과제로 남깁니다. 즉 **인간 쪽 촉각은 아예 없고**, 로봇 쪽도 Allegro(4-finger)와 Inspire(tactile RH56DFTP) 간 신호 규격이 이질적이라 그대로 cross-embodiment 촉각 학습에 쓰기 어렵습니다.
- **Trajectory correspondence 정의의 모호성 (저자 명시)** — paired 정렬이 **semantic 수준**(같은 grasp intent)에 그치고, 서로 다른 손 morphology 간 "기능적으로 등가인 모션"을 정의하는 것은 여전히 열린 문제입니다. 이는 프레임 단위 dense correspondence 를 요구하는 imitation/retargeting 학습에 직접적 걸림돌입니다.
- **grasp 태스크로의 국한 (추론된 갭)** — 데이터셋은 **grasping** (들어 올려 10초 유지)에 집중되어, in-hand reorientation·tool articulation 같은 contact-rich 동적 조작 시퀀스는 담지 않습니다. dexterity 의 상한을 재는 태스크로는 범위가 좁습니다.
- **teleoperation 기반 로봇 데이터의 최적성 (추론된 갭)** — 로봇 grasp 은 Xsens+MANUS 텔레오퍼레이션 재현이라, teleoperator 의 숙련도·retargeting 품질에 성능이 묶이고 "로봇에 최적인 grasp"과 다를 수 있습니다(인간 grasp 의 semantic 재현이 목표이므로).
- **규모의 상대적 소규모성 (추론된 갭)** — 2.1K sequences / 100 objects 는 pretraining-scale 로봇 corpus(AgiBot 1M, DROID 76K traj)에 비하면 작습니다. frame 수(24M)는 multi-view(23뷰) 곱셈 효과라, 실제 독립 grasp 시퀀스 수는 제한적입니다. 1,000 objects 확장이 예고되어 있습니다.
- **성공/실패 라벨의 이진성 (추론된 갭)** — $`y\in\{0,1\}`$ 이라 grasp 품질의 연속 지표(안정성 margin, contact 품질)가 없어, 미세한 grasp 우열 학습에는 supervision 이 성깁니다.

---

## ♻️ 재현성

- **데이터/코드 공개 예정** — "The full dataset will be publicly released to facilitate future research in dexterous manipulation and robot learning." (§1). Project page: https://snuvclab.github.io/HRDexDB/ (다운로드/코드 링크는 공개 시점 확인 필요). License: **CC BY 4.0** (arXiv 표기) — 허용적.
- **캡처 하드웨어 명시** — 21-camera exo rig(삼면 metal frame) + over-the-shoulder ego rig(로봇) + custom stereo helmet(인간), Xsens IMU suit + MANUS gloves 텔레오퍼레이션, $`2048\times1536`$ 해상도. 로봇 핸드: Allegro V4/V5 Plus, Inspire RH56DFTP/RH56F1.
- **복원 파이프라인 재현 요소** — HaMeR + MANO multi-view fitting(GigaHands 전략), SAM3 mask, FoundationStereo depth, FoundationPose 6D + cross-view silhouette consistency. 모두 공개 도구 기반이라 파이프라인 재현 가능성이 높습니다.
- **벤치마크 세팅** — contact transfer 는 CEDex optimizer + BODex/CuRobo 실행, Isaac Gym 6축 force 평가(sim) / 10초 유지(real, 60·30 trials); retrieval 은 CLIP-style + BODex(MuJoCo 평가, 33 episodes × 7 objects × 50 seeds); hand pose 는 PA-MPJPE/PA-MPVPE(mm); object 6D 는 ADD(cm)/ARMSSD(%)/ADD-S + BOP-style. 지표·프로토콜이 표준 도구를 따라 재현 용이.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P0(VLA Datasets & Benchmarks) — 주 연결.** HRDexDB 는 P0 가 추적하는 데이터/벤치마크 릴리스의 정면 타깃입니다. D25(tactile·force·torque 데이터 스카우팅)의 first-class gap 을 **로봇 tactile force** 로 부분 충족하고, D26(benchmark/eval 스카우팅 범위)에는 4종 dexterous 벤치마크(contact transfer / grasp retrieval / 3D hand pose / object 6D)가 정확히 들어옵니다. License 가 **CC BY 4.0** 이라 D27(license/usability bar = 허용적 선호)을 만족합니다. 반면 D24(priority data axis = egocentric human video)와는 **부분적으로만** 정렬됩니다 — egocentric 뷰가 2개 있으나 데이터셋의 본질은 21-cam exocentric mocap-style multi-view 이지 egocentric-centric corpus 가 아닙니다. `catalogs/datasets.md`(🔀 mixed human→robot / tactile)와 `catalogs/benchmarks.md`(✋ dexterous)에 등재 후보.
- **P1(Heterogeneous Body/Hand Action Expert) — 부 연결.** 데이터셋 전체가 **cross-embodiment dexterous grasping** 이라, D2(Body output space = both-wrist/tool-flange pose 로 embodiment-transfer 완화) 관점에서 "인간→다종 로봇 손 grasp 전이"의 실증 데이터가 됩니다. 단 우리 타깃 손(Sharpa 22-DOF / xhand)이 아닌 Allegro/Inspire 임바디먼트라 직접 학습 소스라기보다 전이 방법론 레퍼런스입니다.
- **P3(Hand-level System0 Module) — 부 연결.** tactile-enabled 손의 contact-force 신호는 D15(System0 input modality = tactile + finger joint state) 관점의 실제 접촉 데이터이나, **성공/실패 이진 라벨 + 플랫폼별 이질 스펙**이라 slip-suppression reward 로 바로 쓰기엔 정밀도가 부족합니다.
- **P2(Structured Multimodal Observation Fusion) — 약한 연결.** 23뷰 multi-camera + object 6D + tactile 동기화는 D8(multi-camera spatial-geometric grounding)·D11(proprio-tactile-force token 구성)의 데이터 측 재료가 되나, 관측 융합 method 자체를 제안하진 않습니다.
- **Identity 지지/긴장.** Identity 의 "multi-cam spatial grounding + per-finger proprio-tactile binding"을 **데이터 측에서** 지지합니다(다시점 + 로봇 tactile). 긴장점은 이 데이터가 **offline grasp 캡처/전이 연구용**이지 VLA-level 정책 학습 corpus 가 아니며, egocentric-centric(D24)도 아니라는 점입니다.
- **경쟁자 함의.** P0 핀 중 RH20T(arXiv:2307.00595, 로봇 F/T)와 겹치는 축(paired human-robot + 접촉 모달리티)이 있으나, RH20T 는 parallel-jaw 위주이고 HRDexDB 는 **dexterous 다종 손 + object 6D + markerless 3D hand** 로 차별화됩니다.

---

## ✨ 핀 논문 대비 델타

- **RH20T(arXiv:2307.00595, P0 핀, F/T) 대비** — RH20T 는 7 임바디먼트 · 6축 wrist F/T 의 paired human-robot corpus 이나 **parallel-jaw 그리퍼 위주 + 3D hand / object 6D 결측**입니다. HRDexDB 는 **dexterous 다종 손(Allegro/Inspire) + markerless 3D hand(MANO) + object 6D(SE(3)) + fingertip tactile** 을 동시에 채워, "손가락 수준 dexterous grasp 의 human↔robot 대응"이라는 RH20T 가 못 다룬 축을 정면으로 채웁니다.
- **EgoDex(arXiv:2505.11709, P0 핀, egocentric) 대비** — EgoDex 는 829h 대규모 **인간 egocentric** dexterous + 3D hand 이나 **로봇 대응·object 6D·tactile 이 없습니다**. HRDexDB 는 규모는 훨씬 작지만(2.1K seq) **로봇 paired 실행 + object 6D + tactile** 을 더한 것이 델타입니다 — 축이 "인간 스케일" vs "human-robot paired dexterous" 로 다릅니다.
- **종합 델타** — "paired human + 다종 dexterous 로봇 + 공유 물체 + markerless 3D hand + object 6D + tactile" 의 동시 결합은 기존 P0 핀 어느 것도 제공하지 않던 조합입니다(Table 1 의 유일 완비 행). 단 기여 무게중심은 **데이터셋/벤치마크**이며, 부수 baseline(contact transfer / retrieval)의 method 신규성은 낮습니다.

---

## ⚙️ 의사결정 함의

- **`catalogs/datasets.md` 등재** — HRDexDB 를 🔀 mixed(human→robot paired) × dexterity × tactile 항목으로 등재. `Facts` 에 "100 objects(→1,000 확장) / 2.1K seq / 24M frames / 5 임바디먼트(human + Allegro V4·V5Plus + Inspire RH56DFTP·RH56F1) / 21 exo + 2 ego / $`2048\times1536`$ / MANO 3D hand / object 6D(SE(3)) / robot tactile force / 성공라벨", `License` 에 **CC BY 4.0** 기록. `catalogs/benchmarks.md` 에는 ✋ dexterous 벤치마크(contact transfer / grasp retrieval / hand pose / object 6D)로 등재.
- **D25(tactile 스카우팅) 갱신** — 로봇 fingertip contact-force 를 담은 신규 릴리스로 태그. 단 **인간 촉각 부재 + 플랫폼별 이질 스펙**이라 우리 fingertip 촉각(Sharpa Deform Map) 학습 소스로는 제한적 — "표현/전이 참고"로 플래그.
- **cross-embodiment 전이 레퍼런스** — 인간→로봇 grasp 전이가 **kinematic retargeting(Table 4 에서 최악) 보다 데이터 기반 contact-transfer / latent retrieval 이 낫다**는 결과는, 우리 D2(both-wrist/tool-flange pose 로 embodiment 전이 완화) 설계의 방향성(직접 retargeting 지양)을 지지하는 근거로 인용 가능.
- **perception 벤치마크 활용** — dexterous grasp 하 3D hand pose / object 6D 추정이 표준 벤치마크보다 어렵다는 정량 근거(Table 5·7)는, 우리 P2 관측 인코더(hand/object state 추정)의 **난이도·평가 셋** 참고가 됩니다. HRDexDB 데이터를 섞으면 hand pose·6D refiner 가 개선(Table 6·8)되므로 보조 학습 신호 후보.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 체크) 임바디먼트 불일치** — 데이터의 로봇 손은 **Allegro(16-DOF급) / Inspire(6-DOF급)**, 우리 타깃은 **Sharpa Hand(22-DOF, no wrist DOF) / xhand**. 관절 수·토폴로지·tactile 배치가 달라, grasp/contact 표현을 우리 손에 쓰기 전에 "이 contact map / retrieval prior 가 22-DOF Sharpa 로 매핑 가능한가"를 먼저 따져야 합니다(대개 재-retarget 필요).
- **egocentric-centric 아님 (D24 정렬 확인)** — 우리 데이터 축은 egocentric human video 우선인데, HRDexDB 는 21-cam exocentric mocap-style 이 본질이고 ego 는 2뷰 보조입니다. pretraining corpus(P4 D22) 로 쓰려면 ego 축과의 정합을 먼저 확인해야 하며, 그대로는 우선 축과 어긋납니다.
- **인지 ≠ 정책** — 본 논문은 offline grasp 캡처 + **정적 grasp 합성/검색** 벤치마크이지 폐루프 dexterous 정책이 아닙니다. 우리 스택은 VLA-level flow-matching 정책 학습이 목표라, HRDexDB 데이터를 정책 학습에 쓰려면 action chunk / 제어율 규약으로의 변환이 별도로 필요합니다.
- **tactile 절대 캘리브레이션·인간측 부재** — contact-force 가 로봇 손에서만·플랫폼별 이질 스펙으로 제공되어 System0(P3) slip-suppression reward 가 요구하는 절대 힘 단위/일관 캘리브레이션이 없습니다. 인간 촉각은 아예 없어 human↔robot 촉각 전이는 불가.
- **teleoperation·semantic pairing 품질 의존** — 로봇 grasp 이 텔레오퍼레이션 재현이라 correspondence 가 semantic 수준에 그칩니다(저자 명시 한계). frame-level dense correspondence 를 요구하는 imitation 학습에 쓰면 정렬 오차가 성능을 제한할 수 있습니다.
- **소규모 + 이진 라벨** — 2.1K sequences · 성공/실패 이진 라벨은 pretraining-scale·연속 품질 supervision 을 요구하는 우리 학습에는 성깁니다. 벤치마크 수치도 신뢰구간 보고가 없어(단일 run 가능성) 의사결정 인용 전 반복 분산 확인 필요.

---

## 💡 컨텍스트 제안

- **`catalogs/datasets.md` / `catalogs/benchmarks.md` 추가 후보** — HRDexDB 를 🔀 mixed(human→robot) × dexterity × tactile 데이터 + ✋ dexterous 벤치마크로 등재(D25/D26). License CC BY 4.0(D27 만족) 기록. 공개 시점의 실제 다운로드/코드 링크 확인 필요.
- **P0 §5 핀 검토(쿼터 리밸런스)** — paired human-robot **dexterous** 축은 현재 핀에 비어 있습니다(RH20T 는 parallel-jaw). HRDexDB 공개·규모 확장(1,000 objects) 확인 시, cross-embodiment dexterous grasp 슬롯 신설을 고려할 만합니다(append 아님, 8핀 cap 내 교체).
- 그 외 Decision/trigger 이동 제안: 없음.

> 💡 본 논문은 Design 비대상(dataset)이라 foundry 매핑 대상이 아닙니다. 가치는 분석 문서 본문으로 전달됩니다.
