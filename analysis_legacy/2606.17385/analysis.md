# Paper Analysis — EgoInfinity: A Web-Scale 4D Hand-Object Interaction Data Engine for Any-View Robot Retargeting and Video-to-Action Robot Learning

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | EgoInfinity: A Web-Scale 4D Hand-Object Interaction Data Engine for Any-View Robot Retargeting and Video-to-Action Robot Learning |
| 저자 | Gaotian Wang, Kejia Ren, Andrew Morgan, Yiting Chen, Howard H. Qian, Podshara Chanrungmaneekul, Kaiyu Hang (Rice University · Robotics and AI Institute) |
| 링크 | [arXiv:2606.17385](https://arxiv.org/abs/2606.17385) · [HuggingFace](https://huggingface.co/spaces/Rice-RobotPI-Lab/EgoInfinity) |
| 발행일 / 버전 | 2026-06-16 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-22 |
| 관련 Pillar | P0, P4 |
| 태그 | egocentric-data, dataset, flow-matching |
| 카탈로그 | dataset/human/EgoInfinity |

---

## 🧭 한 줄 요약 (TL;DR)

정적 데이터셋을 또 하나 내놓는 대신, 임의의 인터넷 RGB 영상을 사람 손-물체의 **metric 4D 표현**(hand trajectory · 6-DoF object pose · contact state)으로 자동 변환하는 모듈형 **데이터 엔진**과, 그 손 궤적을 임의 로봇 형상으로 옮기는 **SE(3)-equivariant flow-matching 리타게터**를 함께 제안합니다. 휴먼-인-더-루프 주석 없이 web-scale로 video-to-action 데이터를 생성하는 것이 목표입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 인터넷 영상은 가장 큰 "체화된 사람 조작 지식" 저장소이지만, 임의의 RGB 영상을 로봇이 학습에 쓸 수 있는 데이터로 바꾸는 것이 병목입니다. 영상에는 metric 3D 기하·6-DoF 물체 상태·접촉 정보·실행 가능한 로봇 액션이 없습니다.
- **기존 접근의 한계** — 랩/공장 수집 데이터(Ego4D, EgoDex, HOT3D, DROID 등)는 헤드셋·mocap·Vision Pro·수동 narration·통제된 환경에 의존해 규모와 다양성이 제한됩니다. learning-from-human-video 방법은 2D pseudo-action에 머물러 실행 단계에서 under-grounded이거나, 2D 정렬을 로봇 액션 공간으로 들어올릴 때 mis-grounded됩니다.
- **본 논문의 가설** — 손 재구성·monocular metric depth·open-vocab segmentation·물체 재구성·중력 보정 등 핵심 컴포넌트가 충분히 성숙했으므로, 이들을 **cross-module calibration + interaction-aware refinement**로 묶으면 단순 off-the-shelf 조합을 넘어 물리적으로 신뢰할 만한 4D 데이터를 자동 생성할 수 있습니다.
- **왜 지금 중요한가** — Action100M 한 코퍼스만으로도 147M action segment / 14.6년 분량의 영상이 존재하며, 엔진이 corpus-agnostic이라 컴포넌트가 개선될수록 데이터 품질이 자동으로 따라 올라갑니다(엔진을 키우면 데이터가 무한히 따라온다는 "Infinity" 주장).

---

## 🧩 핵심 기여

- **완전 자동·모듈형 4D 조작 데이터 엔진** — 인터넷 RGB 영상을 사람 주석 없이 agent-agnostic·metric hand-object 표현으로 변환. hand mesh estimation, metric depth, camera/gravity calibration, 자동 target-object discovery, object reconstruction/tracking, interaction-aware refinement를 통합.
- **Cross-module calibration + interaction-aware refinement** — 각 모듈의 raw 출력을 공유 metric scale·통일 카메라 프레임으로 정렬하고, 검출된 interaction state(static/grasped/moving)로 물체 궤적을 보정해 drift와 contact 비일관성을 줄임.
- **Functional cross-embodiment retargeter** — 사람의 정확한 body/arm kinematics를 모사하는 대신 로봇별 **kinematic root frame**을 추정해 task-relevant 손 운동을 보존. 손만 보이거나 시점·shot size가 임의여도(부분 관측) 동작.
- **Action100M 큐레이션 subset + 브라우저 데이터 서버** — 106개 처리 영상과, 런타임 백엔드 없이 결과를 검사·다운로드하는 Viser 기반 인터랙티브 뷰어.
- **실로봇 검증** — Unitree G1 / Robonaut2 / dual-Franka FR3 리타게팅, 실제 LEAP 손 grasping policy prior, dual-arm Franka에서 cut/pour/wipe 실행.

---

## 🔑 기술 키워드

- **4D Hand-Object Interaction (HOI)** — 시간 축까지 포함한(3D + time) 손-물체 상태 표현. 본 논문의 출력 단위로, metric hand pose·6-DoF object pose·접촉 상태를 한 프레임에 묶음.
- **Data Engine** — 정적 데이터셋이 아니라 "영상을 넣으면 데이터를 뽑는 공장". 컴포넌트 교체로 품질이 계속 좋아지는 모듈형 파이프라인.
- **Functional Retargeting** — 사람 팔 동작을 똑같이 흉내 내는 대신 "과제에 필요한 손의 기능적 운동"만 로봇 제약 안에서 보존하는 리타게팅.
- **Kinematic Root Frame** — 손 궤적을 로봇의 몸통(예: humanoid torso) 기준 좌표로 변환하기 위한 기준 프레임 $`{}^{c}\mathbf{p}^{r}`$. IK의 base가 됨.
- **SE(3)-Equivariance** — 입력 궤적이나 카메라를 강체 변환하면 출력 root frame도 같은 변환을 따르는 성질. 임의 시점 영상에 robust해지는 핵심.
- **Vector Neuron (VN)** — 3D 벡터 feature를 회전-equivariant하게 처리하도록 설계된 신경망 레이어. 스칼라 대신 벡터 채널을 다뤄 SO(3)-equivariance를 구조적으로 보장.
- **Flow-Matching** — 노이즈에서 목표 분포로 가는 velocity field를 학습해 ODE 적분으로 샘플을 생성하는 생성 모델. 여기서는 한 손 운동에 대응되는 여러 torso pose의 다봉 분포를 모델링.
- **Interaction-Aware Refinement** — optical flow·손 keypoint로 프레임별 접촉 상태를 분류하고, 그에 따라 물체 pose를 손에 강체 부착(grasped)/centroid 고정(static)/proposal 유지(moving)로 보정하는 단계.
- **Metric Calibration** — 서로 다른 모듈의 출력을 같은 metric scale·카메라 프레임으로 맞추는 정렬. MoGe-2(focal/scale), Flow3r(depth), GeoCalib(gravity) 사용.
- **Exo-to-Ego Reframing** — 외부 시점 영상을 3D 공간에서 강체 좌표 재배치만으로 egocentric 시점으로 바꾸는 것. 2D generative translation의 pixel hallucination을 회피.

---

## 🔬 방법론

### 직관

EgoInfinity는 크게 두 덩어리입니다. 앞쪽 **데이터 엔진**은 "유튜브 같은 인터넷 영상 한 클립 → 손과 물체의 3D 운동이 시간에 따라 어떻게 변하는지를 미터 단위로 적은 표"를 만드는 자동 파이프라인입니다. 핵심 아이디어는 두 가지입니다. 첫째, 손 추정기·깊이 추정기·물체 추적기는 제각각 다른 스케일과 좌표계로 결과를 내놓으므로, 이들을 하나의 metric 카메라 좌표계로 **보정(calibration)**해서 손과 물체가 같은 공간에 놓이도록 합니다. 둘째, 순수 시각 추적은 물체가 가려지거나 정지해 있을 때 흔들리므로, "지금 이 물체가 정지/잡힘/이동 중 어디인가"를 먼저 분류한 뒤 그 상태에 맞는 물리적 prior로 물체 pose를 **고쳐 씁니다**(잡혀 있으면 손에 붙이고, 정지면 centroid에 고정).

뒤쪽 **리타게터**는 "사람 손이 이렇게 움직였다"를 "이 로봇의 관절이 이렇게 움직여야 한다"로 옮깁니다. 어려운 점은 인터넷 영상엔 보통 손만 보이고 팔·몸통은 안 보인다는 것입니다. 그래서 사람 팔을 복원하려 하지 않고, 대신 "로봇의 몸통(root)을 어디에 두면 이 손 궤적이 로봇 제약 안에서 실현 가능한가"를 **신경망으로 추정**합니다. 같은 손 궤적이라도 몸통 위치는 여러 개가 가능하므로(부분 관측의 모호성), 이를 하나로 회귀하지 않고 flow-matching으로 **여러 후보의 분포**를 만든 뒤 IK 점수로 최선을 고릅니다.

이 신경망을 임의 시점에 강건하게 만드는 장치가 SE(3)-equivariance입니다. 카메라가 돌아가면 손 궤적도 같이 돌아가는데, 네트워크가 equivariant하면 추정된 root frame도 자동으로 같이 돌아가므로 시점마다 따로 학습할 필요가 없습니다. 이를 Vector Neuron 레이어로 구조적으로 보장합니다.

### 아키텍처 — 데이터 엔진 파이프라인

엔진은 **두 패스** 전략으로 web-scale 처리를 가능하게 합니다.

> "EgoInfinity uses a two-pass strategy: Pass 1 performs a lightweight temporal scan to identify hand-present segments and filter videos using hand-motion statistics and camera-motion cues, retaining clips likely to contain useful manipulation. Pass 2 runs the full reconstruction stack only on active segments." (§3.1)
> (Pass 1은 손-존재 구간만 싸게 골라내는 필터, Pass 2는 그 활성 구간에만 무거운 전체 재구성을 돌립니다. 본 논문은 시점이 거의 정지한 영상 — 튜토리얼·how-to 콘텐츠 — 을 주 타깃으로 합니다.)

**Metric-calibrated 컴포넌트** 구성은 다음과 같습니다.

> "Specifically, we use MoGe-2 [27] to estimate camera focal length and global metric scale, Flow3r [28] to predict dense depth maps, and GeoCalib [33] to estimate the gravity vector $`{}^{c}\mathbf{g}`$." (§3.2)
> (MoGe-2가 focal/global metric scale을, Flow3r이 dense depth를, GeoCalib이 중력 벡터 $`{}^{c}\mathbf{g}`$ 를 줍니다. 이 공유 metric 재구성 위에 모든 image-space 예측을 같은 3D 공간으로 들어올립니다.)

손은 WiLoR로 MANO 파라미터(pose $`\mathbf{\theta}^{h}_{t}`$, shape $`\mathbf{\beta}^{h}_{t}`$)를 추정해 mesh $`\{\mathcal{M}^{h}_{t}\}`$, keypoint $`\{\mathcal{K}^{h}_{t}\}`$, global pose $`{}^{c}\mathbf{p}^{h}_{t}=({}^{c}\mathbf{R}^{h}_{t},{}^{c}\mathbf{t}^{h}_{t})\in SE(3)`$ 를 얻고, infilling 모듈이 불안정한 추정을 메웁니다. 물체는 **사람 주석 없이** 영상 description을 semantic prompt로 SAM-3 검출 → SAM-2 mask propagation → depth로 point cloud $`\{\mathcal{P}^{o}_{t}\}`$ 생성, 증거가 충분하면 SAM-3D가 mesh $`\mathcal{M}^{o}`$ 재구성, FoundationPose++가 6-DoF pose $`\{{}^{c}\mathbf{p}^{o}_{t}\}`$ 를 같은 metric 프레임에서 추적합니다. 이렇게 초기 4D 상태가 만들어집니다.

$$\mathcal{H}_{t}=\{\mathcal{M}^{h}_{t},\mathcal{K}^{h}_{t},{}^{c}\mathbf{p}^{h}_{t},\mathcal{P}^{o}_{t},\mathcal{M}^{o},{}^{c}\mathbf{p}^{o}_{t}\}$$

### 아키텍처 — Interaction-Aware Refinement

순수 시각 추적의 불안정성을 interaction state로 교정하는 것이 엔진의 차별점입니다.

> "Each frame first receives an initial 6-DoF proposal $`\tilde{\mathbf{p}}^{o}_{t}=(\mathbf{R}^{\text{cano}},\,\mathrm{center}(\mathcal{S}^{o}_{t}\odot D_{t}))`$ from the object mask and depth, keeping the canonical SAM-3D orientation $`\mathbf{R}^{\text{cano}}`$ and estimating translation from the back-projected masked points." (§3.3)
> (mask × depth의 back-projection 중심으로 translation을, SAM-3D canonical orientation으로 rotation을 잡은 초기 proposal $`\tilde{\mathbf{p}}^{o}_{t}`$ 를 만듭니다.)

이후 MEMFOF optical flow와 손 keypoint로 프레임을 $`s_{t}\in\{\text{static},\text{grasped},\text{moving}\}`$ 로 분류하고, 상태별로 다르게 처리합니다.

> "Based on $`s_{t}`$, a grasped object is rigidly attached to the hand frame as $`{}^{c}\hat{\mathbf{p}}^{o}_{t}={}^{c}\mathbf{p}^{h}_{t}\cdot\mathbf{T}^{\text{cano}}`$ with a palm-aligned canonical transform $`\mathbf{T}^{\text{cano}}`$; a static object is locked to its robust point-cloud centroid; and a moving object retains the proposal $`\tilde{\mathbf{p}}^{o}_{t}`$." (§3.3)
> (잡힌 물체는 손 프레임에 강체 부착 $`{}^{c}\hat{\mathbf{p}}^{o}_{t}={}^{c}\mathbf{p}^{h}_{t}\cdot\mathbf{T}^{\text{cano}}`$, 정지 물체는 robust centroid에 고정, 이동 물체는 시각 proposal 유지 — 상태가 물리적 prior를 선택하게 합니다.)

내부적으로는 6-state 라벨을 씁니다.

$$\sigma_{t}\in\Sigma=\{\textsc{static\_global},\;\textsc{static},\;\textsc{grasped\_l},\;\textsc{grasped\_r},\;\textsc{grasped\_both},\;\textsc{moving}\}$$

(§A.2) 여기서 global static gate는 mask centroid의 inter-percentile span $`\Delta_{[10,90]}\leq 0.02\cdot\min(H,W)`$ 이면 클립 전체를 static_global로 단축 처리하고(고정 집기·도마 등), per-frame motion gate는 centroid 변위에 Schmitt trigger $`(d_{\text{lo}},d_{\text{hi}})=(2,4)`$ px를 적용해 hysteresis-안정 motion 신호를 만듭니다. per-hand grasp는 (i) 2D mask overlap ≥ 30px(primary) (ii) fingertip ≤ 6cm (iii) wrist ≤ 5cm을 OR 결합합니다.

마지막으로 §3.4의 cleanup(mask erosion·depth-gradient filter·statistical outlier removal)과, 거의-정적 카메라 가정 하에서 **exo-to-ego 변환을 2D generative translation이 아닌 3D 강체 좌표 재배치**로 수행해 pixel hallucination을 피합니다.

![Figure 2 — 리타게팅 파이프라인](https://arxiv.org/html/2606.17385/x2.png)

> "Figure 2: Retargeting pipeline. Recovered 3D hand trajectories and gravity are fed into a simulation-trained, robot-specific root estimator $`\Phi`$ , which generates candidate root frames. After clustering and scoring, the best candidate (e.g., the torso frame for Unitree G1) is selected, and the hand motion is retargeted through IK followed by post-optimization." (§4)
> (손 궤적+중력 → root estimator $`\Phi`$ → 후보 root frame 군집화·스코어링 → 최적 후보 선택 → IK + post-optimization. 데이터 엔진 출력이 어떻게 로봇 관절 궤적이 되는지 전체 흐름을 보여줍니다.)

### 아키텍처 — Root-Frame Estimator $`\Phi`$

리타게터의 핵심은 root frame $`{}^{c}\mathbf{p}^{r}=({}^{c}\mathbf{R}^{r},{}^{c}\mathbf{t}^{r})\in SE(3)`$ 를 추정하는 VN flow 모델입니다. 입력은 각 손당 $`(T,7)`$ 텐서(3D position + 4D quaternion). bilateral centroid $`\mathbf{c}`$ 를 빼 global translation을 제거한 뒤, 각 timestep을 5개 VN 채널로 인코딩합니다.

$$\left[{}^{c}\mathbf{t}^{h}_{t}-\mathbf{c},\;{}^{c}\mathbf{R}^{h}_{t}[:,0],\;{}^{c}\mathbf{R}^{h}_{t}[:,1],\;{}^{c}\mathbf{R}^{h}_{t}[:,2],\;{}^{c}\mathbf{g}\right]$$

(§B.1, Eq. 6) centered position·3개 orientation axis·gravity로, 각 손 궤적이 $`(T,5,3)`$ VN feature가 됩니다. 좌/우 손은 $`\mathrm{VN\text{-}Linear}(5,d)`$ 로 독립 projection 후 channel 축 concat → $`\mathrm{VN\text{-}Linear}(2d,d)`$ 로 fuse되어 $`(T,d,3)`$ bilateral feature가 됩니다. flow time $`\tau\in[0,1]`$ 의 noisy root state는 4채널로 인코딩(Eq. 7)되어 $`\mathrm{VN\text{-}Linear}(4,d)`$ → sinusoidal $`\tau`$-MLP scale → bilateral feature에 더해지고, $`L`$ block VN-Transformer encoder(LayerNorm + $`H`$-head attention + sinusoidal temporal bias + FFN $`d_{\mathrm{ff}}`$)가 처리한 뒤 time mean-pool로 $`(d,3)`$ trajectory feature를 만듭니다.

### 학습 목표 / 손실 — Flow-Matching + Equivariance

equivariance 제약은 다음 등식으로 못 박힙니다.

> "For any $`\mathbf{G}\in SE(3)`$ applied to observations $`\mathbf{x}`$," (§4.1, Eq. 1)
> (관측 $`\mathbf{x}`$ 에 임의의 강체 변환 $`\mathbf{G}`$ 를 가하면 출력 root frame도 같은 변환을 따른다 — 임의 시점 robustness의 수학적 근거입니다.)

$$\mathbf{G}\cdot\Phi(\mathbf{x})=\Phi(\mathbf{G}\cdot\mathbf{x})$$

rotation head는 pooled VN feature를 두 벡터로 디코딩해 Gram–Schmidt로 $`{}^{c}\mathbf{R}^{r}\in SO(3)`$ 를 만들고, translation은 root-relative offset $`\mathbf{v}`$ 를 예측해 $`{}^{c}\mathbf{t}^{r}={}^{c}\mathbf{R}^{r}\mathbf{v}+\mathbf{c}`$ 로 복원해 camera-frame translation 직접 회귀를 피하면서 equivariance를 보존합니다. root-frame 예측은 결정론적 회귀가 아니라 flow-matching conditional generation으로 정식화됩니다.

> "Instead of deterministic regression, we formulate root-frame prediction as flow-matching conditional generation [47], modeling $`p({}^{c}\mathbf{p}^{r}\mid\mathbf{x})`$ over plausible root frames." (§4.1)
> (같은 손 운동이 여러 torso pose에 대응되는 모호성 — 특히 부분 관측 — 을 다봉 분포 $`p({}^{c}\mathbf{p}^{r}\mid\mathbf{x})`$ 로 포착합니다.)

prior 샘플은 $`{}^{c}\mathbf{R}^{r}_{0}\sim\mathcal{U}(SO(3))`$, $`{}^{c}\mathbf{t}^{r}_{0}\sim\mathcal{N}(\mathbf{c},0.5^{2}\mathbb{I})`$ 에서 뽑고, 학습된 flow가 $`\mathbf{x}`$ 조건부 root-frame hypothesis로 매핑합니다. 추론 시 learned ODE를 **20 Euler step**으로 적분해 샘플을 생성합니다. output head는 rotation/translation velocity field $`\dot{\mathbf{v}}`$ 를 예측합니다.

![Figure 7 — Root-frame estimator 아키텍처](https://arxiv.org/html/2606.17385/x7.png)

> "Figure 7: Root-frame estimator architecture. Bilateral hand trajectories and the optional gravity vector (upper left) are encoded as Vector-Neuron (VN) features and processed by a transformer-based temporal encoder. The encoder output is passed to rotation and translation output heads, which predict flow-matching velocities used to denoise a noisy root-frame sample into the final root-frame estimate (yellow, lower right)." (§B.1)
> (VN 인코딩 → VN-Transformer → rotation/translation head가 flow velocity를 내고, noisy root sample을 최종 root frame으로 denoise하는 구조를 그림으로 보여줍니다.)

### 학습 셋업

네트워크는 **MuJoCo 시뮬레이션에서만** 학습합니다(real-world supervision 없음). 각 로봇마다 paired hand trajectory–ground-truth root pose를 procedural하게 생성: noisy reference joint config에서 FK로 hand anchor를 잡고, 이 anchor로 bias된 Ornstein–Uhlenbeck random walk로 control point를 만들어 warm-start position-only IK로 joint knot 변환 후 cubic spline 보간($`T=60`$ frame, $`f=30`$ fps, 2초 window, control point $`N_{\mathrm{ctrl}}=7`$). 매 trajectory마다 robot 주위 random camera pose를 샘플해 손 궤적·root frame을 카메라 프레임으로 변환합니다. **Augmentation**으로 tracking noise/jump, hand occlusion, gravity noise를 주고, 30% 샘플은 gravity를 drop해 중력 부재에 graceful degrade하게 합니다.

| 학습/추론 파라미터 | 기호 | 값 |
|---|---|---|
| Channel width | $`d`$ | 128 |
| Attention heads | $`H`$ | 4 |
| Transformer layers | $`L`$ | 4 |
| FFN hidden width | $`d_{\mathrm{ff}}`$ | 512 |
| Dropout | – | 0.1 |
| Epochs | – | 500 |
| Steps per epoch | – | 20 |
| Batch size | – | 1024 |
| Optimizer / LR | Adam | $`10^{-3}`$ (grad clip 1.0) |
| Inference ODE steps | $`N`$ | 20 (Euler) |
| GPU / time | – | RTX 3060 12GB · 로봇당 ≈ 1.5–2 h |

추론(§4.3)은 overlapping temporal window별로 hypothesis를 샘플 → $`k`$-means 군집화 → 대표 후보 유지 → translation linear / rotation SLERP 보간으로 per-frame root trajectory → 각 후보를 IK convergence·residual error·manipulability·joint-limit margin·smoothness로 스코어링해 최선 선택. dexterous hand의 finger joint는 MANO keypoint에서 geometry-based robot-specific 매핑으로 별도 retarget합니다.

---

## 📊 실험 설정과 결과

네 관점에서 검증합니다: 인터랙티브 데이터 접근, 큐레이션 데이터셋 통계, cross-embodiment 리타게팅, 실로봇 실행·학습.

### 데이터셋 규모 비교 (Table 1)

| Dataset | Source | Wearable req.? | Auto gen.? | Manual obj.? | Scale |
|---|---|---|---|---|---|
| Ego4D | curated | headset | ✗ | ✗ | 3.7K hr |
| EgoDex | curated | V. Pro | ✗ | ✗ | 829 hr |
| HOT3D | curated | mocap | ✗ | ✗ | 13.9 hr |
| OakInk2 | curated | mocap | ✗ | ✗ | 6.5 hr |
| UniHand-Mix | aggregated | partial | ✗ | ✗ | 1.2K–35K hr |
| Open-X | robot agg. | robot | ✗ | ✗ | 1M+ traj. |
| DROID | teleop | robot | ✗ | ✗ | 350 hr |
| **EgoInfinity (ours)** | internet | ✓ none | ✓ full | ✓ none | **127K hr** |

> "Scale is currently bounded by Action100M; the data engine itself is corpus-agnostic." (§2, Table 1)
> (127K hr는 Action100M에 의해 묶인 현재 상한일 뿐, 엔진 자체는 corpus-agnostic이라는 단서 — 규모 주장의 핵심 qualifier입니다.)

이 표는 EgoInfinity가 유일하게 internet-scale + no-wearable + full-auto + no-manual-object를 동시에 만족한다고 주장합니다. 다만 다른 데이터셋은 **사람이 검증한 annotation**(mocap/tracking)인 반면 EgoInfinity는 **자동 추정 4D**라는 점에서, 같은 "scale" 축의 품질이 동일하지 않음에 유의해야 합니다(아래 ⚖️).

### Cross-Embodiment 리타게팅 (Table 2)

| Robot | IK Rate | Pos. Error | Ori. Error | Jnt.-Limit Margin | Manipulability | Smoothness |
|---|---|---|---|---|---|---|
| Unitree G1 | 0.821 | 2.86 cm | 6.73° | 0.619 rad | 0.012 | 0.00693 |
| Robonaut2 | 0.774 | 6.67 cm | 8.25° | 0.134 rad | 0.058 | 0.00343 |
| Dual-Franka | 0.706 | 10.27 cm | 12.17° | 0.572 rad | 0.080 | 0.00582 |

> "IK Rate: per-frame IK success rate. Pos./Ori. Error: mean hand position ($`\ell_{2}`$, cm) and orientation (geodesic, °) error between IK target and achieved pose." (§5.3, Table 2)
> (per-frame IK 성공률과 IK target–달성 pose 사이 평균 위치/방향 오차. Manipulability는 $`\sqrt{\det(JJ^{\top})}`$, Smoothness는 평균 제곱 관절속도 $`\dot{q}`$.)

**Per-row 읽기** — Unitree G1이 IK rate 0.821 / pos err 2.86cm로 가장 좋습니다(humanoid torso가 root frame 가정과 가장 잘 맞음). Robonaut2는 중간이지만 joint-limit margin이 0.134 rad로 가장 빡빡해(여유 적음) 제약이 가장 타이트한 embodiment임을 시사합니다. Dual-Franka는 IK rate 0.706 / pos err 10.27cm로 가장 어렵습니다 — humanoid가 아닌 dual-arm 구성이라 사람 손 궤적의 root 가정과 거리가 멀고, 10cm대 오차는 "functional" 전이임을 그대로 드러냅니다(정밀 모사가 아님). 절대 baseline 비교군이 표에 없어 이 수치들의 좋고 나쁨은 상대적으로만 해석 가능합니다(아래 ⚖️).

![Figure 4 — Action100M subset 통계](https://arxiv.org/html/2606.17385/x4.png)

> "Figure 4: Statistics of the curated Action100M subset. (a) Clip durations. (b) Object category mix. (c) Top action verbs. (d) Per-frame state distribution averaged across manipulated objects (d). 88% of clips and 47% of objects are manipulated, with balanced use of left, right, and bimanual grasps." (§5.2)
> (큐레이션 subset의 clip 길이·물체 카테고리·top verb·state 분포 — 88% clip / 47% object가 조작되며 left/right/bimanual grasp가 균형적이라는 통계.)

![Figure 3 — EgoInfinity 실험 개요](https://arxiv.org/html/2606.17385/x3.png)

> "Figure 3: EgoInfinity experiments. (a) Project page visualization (3D viewer, intermediate results, text descriptions, track summaries). (b) 4D HOI reconstructions retargeted to multiple embodiments in simulation and on real robots. (c) Extracted hand trajectories used as priors for downstream policy use, generalizing across objects. (d) Real-robot demos on Cut, Pour, and Wipe." (§5)
> (인터랙티브 뷰어·다중 embodiment 리타게팅·downstream policy prior·실로봇 데모를 한 장에 요약 — 파이프라인 전체가 실제로 도는 것을 보이는 그림입니다.)

### 실로봇 (§5.4)

큐레이션 subset은 **106개 처리 영상**이며, 실로봇 검증은 두 갈래입니다. (1) 추출한 손 운동을 prior로 실제 **LEAP dexterous hand** grasping policy를 학습해 다양한 물체 grasp(Fig. 3c), (2) dual-arm Franka FR3에 직접 리타게팅해 cut/pour/wipe를 기능적으로 실행(Fig. 3d). 정량적 success rate 표는 본문에 제시되지 않고 정성적 데모 중심입니다.

---

## ⚖️ 한계

- **거의-정적 카메라 가정** — 저자 명시. body-mounted/hand-held 영상을 제외해 web-scale 처리는 tractable해지지만(online SLAM 회피) corpus 다양성이 제한됩니다. 정작 가장 풍부한 1인칭 wearable 영상(진짜 egocentric)이 빠지므로, "internet-scale" 주장의 적용 범위는 튜토리얼/how-to류로 좁아집니다.
- **Contact-level 정확도 미보장** — 저자 명시. interaction-aware refinement는 coarse grasp 검출과 손-물체 궤적의 공간적 상관만 제공하며, 정확한 fingertip placement·force consistency·no-slip을 보장하지 않습니다. 대다수 출력이 "잡혀 있으면 손에 강체 부착"이라는 단순 prior에서 나오므로, in-hand reorientation처럼 손가락 상대운동이 핵심인 과제에는 신호가 부족합니다.
- **Tactile 부재** — 저자 명시. 촉각 관측이 없어 fine-grained contact reasoning을 못 합니다. 손-중심 dexterity의 핵심 모달리티가 구조적으로 빠져 있습니다.
- **리타게터의 robot-specific 재학습 비용** — 저자 명시. 새 로봇마다 sim에서 재학습/캘리브레이션이 필요합니다(로봇당 1.5–2h). morphology가 추가될 때마다 비용이 선형 증가하고, MuJoCo sim 분포와 in-the-wild 재구성 노이즈의 gap이 augmentation으로만 메워집니다.
- **자동 추정 품질의 검증 부재(추론)** — Table 1의 "127K hr"는 사람이 검증하지 않은 자동 4D입니다. perception/tracking 오차가 데이터 전반에 silent하게 섞일 수 있으며, IK pos error 3–10cm대는 downstream policy가 흡수해야 할 라벨 노이즈로 작용합니다. baseline 비교군이 Table 2에 없어 절대 품질을 가늠하기 어렵습니다.
- **소규모 공개 subset(추론)** — 엔진 능력은 "infinite"라 주장하나 실제 공개·검증된 것은 106개 영상 subset입니다. 엔진 자동화와 실제 큐레이션·다운로드 가능한 데이터 규모 사이 간극이 큽니다.

---

## ♻️ 재현성

- **코드** — 본문에 GitHub 코드 공개 명시 없음. Project Page는 HuggingFace Space([Rice-RobotPI-Lab/EgoInfinity](https://huggingface.co/spaces/Rice-RobotPI-Lab/EgoInfinity))로, 브라우저 기반 데이터 서버/뷰어(Viser, 런타임 백엔드 없음) 형태.
- **데이터** — Action100M의 큐레이션 subset 106개 영상이 데이터 서버에 호스팅되어 다운로드 가능하다고 기술. 원천 Action100M(arXiv:2601.10592)은 별도 코퍼스.
- **하드웨어** — 리타게터 학습은 단일 RTX 3060(12GB), 로봇당 ≈ 1.5–2h. 실로봇은 Unitree G1 / Robonaut2 / dual-Franka FR3 / LEAP hand. 엔진 컴포넌트(MoGe-2, Flow3r, GeoCalib, WiLoR, SAM-2/3/3D, FoundationPose++, MEMFOF)는 모두 외부 공개 모델.
- **하이퍼파라미터** — 네트워크/학습/추론 파라미터가 Appendix B 표(Tab. 5/6)에 상세 제공되어 리타게터 재현성은 비교적 높음. 단 엔진 전체 파이프라인의 정확한 버전 핀·임계값은 Appendix A 표(Tab. 3/4)에 일부만 명시.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P0(VLA 데이터셋·벤치마크) — 직격.** 본 논문은 D24(priority data axis — egocentric human video 중심)의 정면 사례입니다. "internet egocentric-style human video → metric 4D hand-object" 자동 생성은 P0가 우선시하는 egocentric + 3D hand-tracking 축 그 자체입니다. 또한 D25(tactile/force/torque scouting)에 대해서는 **반례적 증거** — 저자 스스로 tactile 부재를 한계로 명시하므로, P0가 "vision-only corpora를 dexterity에 충분하다고 보지 않는다"는 anti-topic 입장을 강화합니다. D27(license/usability bar)에는 원천 Action100M의 라이선스·gated 여부 확인이 필요합니다(본문 미명시).
- **P4(VLM 사전학습 recipe) — 지지.** functional cross-embodiment retargeting은 UniHand류 mixed human→robot 코퍼스 생성 레시피와 같은 계열로, P4 D22(pretraining corpus)의 데이터 공급 후보입니다.
- **Identity 긴장** — Identity는 "egocentric 중심 corpus × per-finger proprio-tactile binding"을 핵심으로 둡니다. 본 엔진은 **egocentric 축은 강하게 지지**하지만 **tactile/contact 정밀도 축은 비워둡니다**(grasp는 coarse, contact-level 미보장). 즉 P0/P4의 데이터 폭은 키우되, P2(observation fusion)·P3(System0 contact)이 요구하는 접촉 신호는 제공하지 못합니다.
- **경쟁자 함의** — P0 §5 pin인 EgoDex(Vision Pro 829h)·UniHand-2.0(35k h mixed)의 대안 데이터 소스입니다. 둘 다 wearable/aggregation 의존인데, EgoInfinity는 wearable 없이 internet에서 자동 생성한다는 점이 차별점입니다.

---

## ✨ 핀 논문 대비 델타

- **vs EgoDex(arXiv:2505.11709, P0 pin, flagship egocentric)** — EgoDex는 Vision Pro로 **검증된** 3D hand/finger tracking 829h를 수집합니다. EgoInfinity는 wearable 없이 임의 internet 영상에서 **자동 추정** 4D를 뽑아 규모 상한이 훨씬 큽니다(127K hr). 트레이드오프가 명확: EgoDex는 라벨 품질(mocap-grade), EgoInfinity는 규모·다양성. finger-level 정밀도는 EgoDex 우위.
- **vs UniHand-2.0(arXiv:2601.12993, P0 pin, mixed retarget)** — UniHand-2.0은 다수 데이터 aggregation + 30 embodiment retarget으로 heterogeneous annotation을 상속합니다. EgoInfinity의 새로움은 (a) **데이터 엔진**으로서 corpus-agnostic·component-upgradeable, (b) **SE(3)-equivariant flow-matching root estimator**라는 새 리타게팅 알고리즘 — 전신 pose 복원 없이 root frame만 추정해 partial-body·any-view에 동작한다는 점입니다.
- **vs Ego4D(P0 non-pin, gated)** — Ego4D는 3.7K hr headset 영상이지만 manipulation-specific 4D나 로봇 action이 없습니다. EgoInfinity는 이를 자동으로 robot-usable 4D로 끌어올리는 변환기 역할을 할 수 있어, Ego4D류를 소비하는 downstream 엔진으로 볼 수 있습니다.

---

## ⚙️ 의사결정 함의

- **데이터 파이프라인 후보 추가** — egocentric 사전학습 corpus(P4 D22)에 "internet video → 자동 4D HOI" 소스를 한 갈래로 둘 수 있습니다. 단, 라벨이 자동 추정이므로 **action label noise budget**을 명시적으로 잡아야 합니다 — 리타게팅 IK pos error 3–10cm를 supervision 노이즈로 모델링.
- **구체적 config 함의** — 우리 스택에 리타게터를 들인다면 핵심 하이퍼는 ODE Euler step `N=20`, VN channel `d=128`, transformer `L=4`/`H=4`, flow prior `t_0 ~ N(c, 0.5^2 I)`, gravity dropout `0.30`입니다. 손가락은 arm IK와 분리해 MANO keypoint → robot finger geometry mapping으로 별도 retarget — 우리의 Hand expert 입력으로 MANO keypoint 궤적을 그대로 쓸 수 있는지가 분기점입니다.
- **메트릭 채택** — 리타게팅 품질 게이트로 IK rate·geodesic ori error·manipulability $`\sqrt{\det(JJ^\top)}`$ ·joint-limit margin을 우리 retarget 평가 표준 메트릭으로 도입 가능.
- **무엇이 바뀌지 않는가** — tactile/force 신호가 전혀 없으므로 P3 System0(slip/grasp 유지 RL)의 학습 데이터로는 **부적합**합니다. 이 데이터는 "거친 손-팔 궤적 prior" 용도로만 한정하고, contact stabilization supervision은 별도 소스(RH20T류 F/T)에서 받아야 합니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 체크) 우리 task family와 motion type 불일치** — EgoInfinity는 functional **wrist/arm** 궤적 전이가 강점이고 in-hand reorientation 같은 손가락 상대운동은 약합니다. 우리 flagship(in-hand reorientation, tool articulation)은 정확히 그 약한 영역이므로, 먼저 큐레이션 subset 106개에 우리 task류 영상이 있는지부터 봐야 합니다.
- **자동 라벨 노이즈의 downstream 전파** — IK pos error 3–10cm, IK rate 0.7–0.82는 frame의 18–30%가 IK 실패(보간으로 메움)임을 뜻합니다. 우리 Hand expert가 이 노이즈를 흡수하는지, 아니면 prior로 쓸 때 jitter를 주입하는지 소규모 ablation 필요.
- **MANO → 우리 hand morphology 매핑 갭** — finger retarget이 "geometry-based, robot-specific mapping"으로만 기술되어 구체 알고리즘이 본문에 없습니다. 우리 손(LEAP류 또는 자체 hardware)으로의 매핑이 재현 가능한지 불확실 — 사실상 미명시 항목.
- **거의-정적 카메라 필터의 yield** — Pass 1 필터가 우리가 원하는 contact-rich 영상을 얼마나 통과시키는지 모릅니다. 88% clip이 manipulated라는 통계는 이미 큐레이션된 subset 기준이라, 원시 코퍼스에서의 실제 수율과 다를 수 있습니다.
- **sim2real gap(리타게터)** — root estimator가 MuJoCo procedural 궤적으로만 학습되어, 실제 in-the-wild WiLoR 재구성 분포와 augmentation으로만 정렬됩니다. 우리 카메라 셋업·손 추정기를 바꾸면 root 추정이 깨질 수 있어, 우리 데이터 한 줌으로 IK rate를 재측정해야 합니다.

---

## 💡 컨텍스트 제안

- **`catalogs/datasets.md` 👤 Human 섹션 등재 후보** — internet video 자동 4D HOI 소스로, EgoDex·UniHand와 나란히 둘 가치가 있습니다(라이선스·검증 품질 단서는 ⚠️ 플래그와 함께). 본 분석의 `카탈로그` 메타가 이를 라우팅합니다.
- **P0 §5 pin 교체는 보류 권장** — 데이터 자체보다 "엔진 + 리타게팅 알고리즘"이 기여라, 현 pin(EgoDex/UniHand-2.0)을 대체하기보다 methodology base(비-pin)나 datasets.md 카탈로그 행으로 추적하는 것이 적절합니다. 최종 판단은 사람 몫.
- context/ 파일은 수정하지 않았습니다.
