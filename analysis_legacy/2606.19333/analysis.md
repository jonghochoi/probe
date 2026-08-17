# Paper Analysis — Do as I Do: Dexterous Manipulation Data from Everyday Human Videos

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Do as I Do: Dexterous Manipulation Data from Everyday Human Videos |
| 저자 | Bhawna Paliwal, Haritheja Etukuru, William Liang, Pieter Abbeel, Nur Muhammad Mahi Shafiullah, Jitendra Malik |
| 링크 | [arXiv:2606.19333](https://arxiv.org/abs/2606.19333) · [Website](https://do-as-i-do.com) |
| 발행일 / 버전 | 2026-06-17 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-22 |
| 관련 Pillar | P0, P4 |
| 태그 | egocentric-data, dexterity, dataset |

---

## 🧭 한 줄 요약 (TL;DR)

단안(monocular) RGB 인터넷·에고센트릭 영상을 4D 손-물체 상호작용으로 복원한 뒤
물리 시뮬레이터 안에서 sampling-based optimization 으로 22-DoF 다지(多指) 로봇
손에 retarget 하여, "인터넷 영상 → 실제 로봇 손 rollout" 까지 이어지는 첫
파이프라인을 제시합니다. 손-물체 복원과 dynamics-aware retargeting 양쪽에서
기존 SOTA 를 능가하며, 인터넷 영상에서 dexterous manipulation 데이터를 확장적으로
뽑아내는 길을 보입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 로봇 학습 데이터는 대부분 teleoperation / 시뮬레이션 탐색
  같은 경험적(experiential) 데이터에 의존하는데, 이는 조작자 숙련도·비용·리그 투명성
  (teleop) 또는 환경·보상 설계 복잡도(sim)로 병목입니다. 관찰적(observational) 인간
  영상을 로봇용 경험 데이터로 변환하는 것이 목표입니다.
- **기존 접근의 한계** — 기존 "Do as I do" 계열은 pick-and-place 한정, 3D 스캔된
  물체 한정, 또는 depth·3D·hand keypoint 가 담긴 특수 하드웨어 데이터를 가정해 왔습니다.
  그러나 가용 관찰 데이터의 대부분은 단안 RGB 영상이라 이 일반적 케이스를 다루는
  알고리즘이 가장 큰 데이터 증가를 가져옵니다.
- **본 논문의 가설** — (1) 단안 RGB 에서 depth·object·hand 를 3D 복원하는 비전 파운데이션
  모델과, (2) GPU-병렬 물리 시뮬레이터 위의 sampling-based optimization 을 결합하면,
  파지(grasp) prior·물체 클래스 가정 없이 임의 강체에 대해 4D 손-물체 상태로부터
  로봇 손 동작을 수 분 안에 추론할 수 있습니다.
- **왜 지금 중요한가** — SAM 3D 같은 occlusion-robust 이미지→3D 생성 모델과 MuJoCo
  Warp / Isaac 같은 GPU-병렬 시뮬레이터가 최근에야 동시에 성숙했기 때문에, 양쪽의
  최소 가정 특성을 묶어 in-the-wild 영상으로 일반화하는 접근이 비로소 가능해졌습니다.

---

## 🧩 핵심 기여

- **Do as I Do 2단계 알고리즘** — 단안 RGB 영상에서 행동을 복원(reconstruct)하고 다지
  로봇 손으로 retarget 하는 2-step 파이프라인을 제안합니다.
- **occlusion-robust 손-물체 복원** — ego/exo, in-the-wild 인터넷 클립부터 생성형 비디오
  출력까지 다양한 영상을 다루며 관련 지표에서 SOTA 를 능가합니다.
- **noisy reference 강건 retargeting** — scalable dynamics-aware retargeting (SPIDER 계열)에
  warmup / random force perturbation / transition reward 세 신규 컴포넌트를 더해 noisy
  복원 reference 를 robustify 합니다.
- **인터넷 영상 → 실 로봇 rollout** — 저자들이 아는 한 인터넷 영상에서 실제 다지 손
  rollout 까지 가는 첫 완결 파이프라인이며, 인터넷(53%)·ego(31%)·생성(16%) 영상에서
  500 개의 human-verified 궤적을 산출했습니다.
- **인간 데이터 필터링 playbook** — 100DOH 분석을 통해 온라인 인간 데이터의 품질
  이슈를 정량화하고, 전처리·필터링 부재 시 20× 페널티를 제시합니다.

---

## 🔑 기술 키워드

- **Hand-object reconstruction** — 단안 RGB 영상에서 손과 물체의 3D 형상·자세를 시간축에
  따라 동시에 복원하는 것 — 본 논문 1단계의 출력(4D 손-물체 궤적)이 retargeting 의 입력이 됩니다.
- **Retargeting** — 사람 손 동작을 형상이 크게 다른 로봇 손 임베디먼트로 옮기는 것 — 본
  논문 2단계로, 단순 기구학(kinematic)이 아니라 물리 시뮬레이션 기반 dynamics-aware 방식을 씁니다.
- **Guided diffusion (flow matching)** — 이미지→3D 생성 모델 SAM 3D 의 flow matching 추론
  궤적을 anchor 형상/이전 프레임 자세 쪽으로 블렌딩해 프레임 간 일관성을 부여하는 트릭 — 단일
  이미지 생성기를 비디오 물체 트래커로 재용도화합니다.
- **Sampling-based optimization (MPPI)** — 무수히 많은 제어 후보를 시뮬레이션에서 굴려 보상
  높은 쪽으로 가중평균하는 무미분(derivative-free) 최적화 — gradient 없이 dynamics-aware
  retargeting 을 수행하는 엔진입니다.
- **Annealed sampling** — 반복(iteration)·예측 horizon 양축에 걸쳐 샘플 커널을 점차 좁혀
  광역 탐색→국소 정제로 전환하는 스케줄 — SPIDER 의 기본 골격이자 본 논문 baseline 입니다.
- **Warmup steps** — reference 앞에 H 스텝을 덧붙여 물체를 고정(weld)한 채 로봇 손만 먼저
  자세를 잡게 하는 워밍업 — noisy 첫 프레임에서 복구 불능 상태로 초기화되는 문제를 해소합니다.
- **Random force perturbation** — rollout 샘플에 임의 외력을 가해 작은 외란에 강건한 제어를
  유도하는 sim-to-real 풍 기법 — fingertip 균형 같은 불안정 local minimum 을 탈출시킵니다.
- **Transition reward** — "rest"↔"in-hand" 전이 시점에서 접촉 실패에 상수 페널티를 부여해
  step-function 적 집기/놓기 상호작용을 강제하는 보상 — noisy reference 의 tracking reward
  만으로는 부족한 임계 전이를 보강합니다.
- **MANO / dexterous hand** — 사람 손의 구조적 형상·운동 모델(MANO)을 활용한 hand tracking
  (HaWoR)과, 22-DoF Sharpa Wave 같은 다지 로봇 손 — 사람↔로봇 형상 격차의 양 끝점입니다.

---

## 🔬 방법론

### 직관

Do as I Do 는 "보는 데이터(영상)"를 "하는 데이터(로봇 동작)"로 바꾸는 두 단계
변환기입니다. 1단계는 **복원**으로, 단안 RGB 영상 한 편에서 손이 어디에 있고 물체가
무엇이며 어떻게 움직이는지를 3D 로 재구성합니다. 손은 이미 충분히 강건한 기성 모델
(HaWoR)로 추적하고, 진짜 어려운 물체 추적은 직접 만든 방법으로 해결합니다 — occlusion 에
강한 이미지→3D 생성 모델(SAM 3D)을 비디오 트래커로 바꿔 쓰는 것이 핵심입니다.

2단계는 **retargeting** 으로, 복원된 사람 손-물체 궤적을 형상이 완전히 다른 로봇 손에
옮깁니다. 단순히 기하학적으로 손가락 끝을 맞추면 침투·미끄러짐·파지 불안정이 생기므로,
물리 시뮬레이터 안에서 reference 를 따라가되 물리적으로 실현 가능한 궤적만 남기는
dynamics-aware 방식을 씁니다. 이때 reference 자체가 noisy 하다는 것이 본 논문의 출발점
이며, 그 noise 를 견디게 하는 세 장치(warmup·perturbation·transition reward)가 기여의
핵심입니다.

전체를 관통하는 설계 철학은 **최소 가정**입니다. 파지 prior 도, 물체 카테고리 가정도,
별도 장면 복원도 두지 않고 임의 강체에 대해 동작하게 만들어, in-the-wild 인터넷 영상
이라는 가장 풍부하지만 가장 noisy 한 데이터 소스를 1급 시민으로 끌어들입니다.

### 아키텍처

![Figure 2 — Method Overview](https://arxiv.org/html/2606.19333/figures/method.jpg)

> "Figure 2: Method Overview. Our method leverages vision foundation models to reconstruct the hand and object, and retargets them onto the robot via sampling-based optimization in simulation." (§3)
> (한글 해설 — 좌측 복원 단계(비전 파운데이션 모델로 손·물체 3D 복원)와 우측 retargeting
> 단계(시뮬레이션 내 sampling-based optimization)로 이루어진 2-step 구조를 한눈에 보여줍니다.)

파이프라인은 두 부분으로 나뉩니다(Fig. 2).

> "Do as I Do consists of two parts ... First, we reconstruct the 3D hand and object, and track them through time (Section 3.1). Then, we retarget the reconstructions onto the robot embodiment, producing dynamically-feasible trajectories that are effective in the real world (Section 3.2)." (§3)
> (한글 해설 — 입력은 단안 RGB 영상 한 편, 최종 출력은 실 세계에서 실행 가능한
> dynamically-feasible 로봇 손-팔 궤적입니다.)

**복원 단계(§3.1)** 는 세 전처리 — (a) SAM 3 로 손·물체 분할, (b) MoGe 로 depth·camera
intrinsics 추정, (c) SAM 3D 로 물체 3D 메시 생성 — 후, 손 추적(HaWoR)과 자체 물체 추적을
수행하고, 3D 손·물체·카메라를 일관된 near metric-space 로 합성합니다.

> "Recognizing and reconstructing hand-object interactions from in-the-wild videos can be decomposed into two components: (1) tracking the human hand, and (2) determining object shape and tracking its pose." (§3.1)
> (한글 해설 — 손 추적은 기성 HaWoR 로 충분하다고 보고, 물체 형상 결정·자세 추적이
> 직접 해결해야 할 난제임을 분명히 합니다.)

**retargeting 단계(§3.2)** 는 Pan et al. (SPIDER)의 MPPI-style sampling-based optimization
위에 세 신규 컴포넌트를 얹은 모듈입니다(아래 학습 목표 / 손실 참조).

### 학습 목표 / 손실

이 논문은 정책을 학습하지 않습니다 — 두 핵심 "목표"는 (1) 물체 추적을 위한 guided
flow-matching 추론과 (2) retargeting 을 위한 보상 기반 sampling 최적화입니다.

**(1) Guided diffusion 물체 추적.** SAM 3D 는 단일 2D 이미지·마스크에서 형상·자세의 결합
분포를 학습합니다.

> "It learns the joint distribution over shape and pose $`p_{\theta}(x^{s},x^{p}\mid c)`$ given a single 2D image and object mask." (§3.1)
> (한글 해설 — 프레임마다 독립 적용하면 매 프레임 다른 메시·일관성 없는 자세열이 나오는데,
> 형상·자세가 같은 latent space 를 공유한다는 관찰이 트릭의 출발점입니다.)

추적은 anchor 프레임에서 형상 $`\bar{x}^{s}`$ 를 고정하고 이전 프레임 자세 $`x^{p}_{k-1}`$
쪽으로 bias 된 조건부 분포에서 자세를 뽑는 것으로 환원됩니다.

> "Tracking thus reduces to drawing from $`p_{\theta}(x^{p}_{k}\mid x^{s}_{k}=\bar{x}^{s},\,c_{k})`$ biased toward $`x^{p}_{k-1}`$." (§3.1)
> (한글 해설 — 6-DoF 연속 자세 공간에서 marginalize 는 불가능하므로, flow matching 추론
> 자체를 활용합니다.)

flow 샘플은 $`x_{0}\!\sim\!\mathcal{N}(0,\mathbf{I})`$ 에서 출발해 선형 경로
$`x_{t}=(1-t)\,x_{0}+t\,x_{1}`$ 를 따라 ODE $`\dot{x}=v_{\theta}(x_{t},t,c)`$ 를 적분해
얻습니다. 각 Euler 스텝에서 모델의 자유 업데이트를 target interpolant 쪽으로 블렌딩합니다(Eq. 1):

$$x^{s}_{t}=(1-\alpha_{s})(x^{s}_{t-\Delta}+\Delta v^{s}_{\theta})+\alpha_{s}\,z^{s}_{\mathrm{ref}}(t),\quad x^{p}_{t}=(1-\alpha_{p})(x^{p}_{t-\Delta}+\Delta v^{p}_{\theta})+\alpha_{p}\,z^{p}_{\mathrm{ref}}(t)$$

여기서 $`\alpha_{s},\alpha_{p}\in[0,1]`$ 는 guidance 강도, target interpolant 는
$`z^{s}_{\mathrm{ref}}(t)=(1-t)\,\epsilon^{s}+t\,\bar{x}^{s}`$ 와
$`z^{p}_{\mathrm{ref}}(t)=(1-t)\,\epsilon^{p}+t\,x^{p}_{k-1}`$ 입니다(형상 블록은 canonical
형상 $`\bar{x}^{s}`$ 로, 자세 블록은 이전 프레임 자세 $`x^{p}_{k-1}`$ 로 nudging).

> "any fixed shape guidance $`\alpha_{s}\in[0.9,1]`$ works well." (§3.1)
> (한글 해설 — 강체이므로 형상 guidance 는 고정해도 무방하고, 자세 guidance $`\alpha_{p}`$
> 는 over-rigidity·spurious flip 방지를 위해 2D point track 으로 추정한 물체 회전 속도에서
> 데이터 기반으로 유도(adaptive)합니다.)

자세 sampling 은 확률적이므로 프레임마다 $`N`$ 개 후보를 뽑아 하나를 고릅니다.

> "we sample and cluster poses under a weighted $`\mathrm{SE}(3)`$ distance ... consensus filtering and mask-IoU recovers the mode-best pose without ever re-invoking the diffusion backbone." (§3.1)
> (한글 해설 — 정석은 조건부 log-density 로 후보를 순위 매기는 것이나 비디오 스케일에서
> 비용이 과도하므로, clustering 기반 consensus 선택으로 backbone 재호출 없이 mode-best 자세를
> 회수합니다. 부록 ablation 상 log-likelihood 선택과 동등하면서 최대 30× 빠릅니다.)

**손-물체 정렬.** 손·물체를 서로 다른 스케일로 독립 복원한 뒤 정렬합니다. 손 복원 스케일을
ground-truth 로 보고 물체 translation 을 손에 맞춰 스케일링하며, centroid $`z`$ 값 비율
$`k=z^{\mathrm{H}}_{\mathrm{hand}}/z^{\mathrm{M}}_{\mathrm{hand}}`$ 로 목표 물체 위치

$$\mathbf{obj}_{\mathrm{target}}=\mathbf{c}^{\mathrm{H}}_{\mathrm{hand}}+k\,\bigl(\mathbf{c}^{\mathrm{M}}_{\mathrm{obj}}-\mathbf{c}^{\mathrm{M}}_{\mathrm{hand}}\bigr)$$

를 최소제곱으로 풉니다. 마지막으로 GeoCalib 로 궤적을 중력 정렬합니다.

**(2) Dynamics-aware retargeting 의 세 혁신.**

![Figure 4 — Retargeting](https://arxiv.org/html/2606.19333/figures/retargeting.jpg)

> "Figure 4: Retargeting. Our method succeeds in common failure modes (top) and excels at handling noisy references (bottom), despite, e.g., incorrect depth estimation causing poor alignment." (§3.2)
> (한글 해설 — 흔한 실패 모드(상)와 noisy reference(하)를 각 컴포넌트가 어떻게 구제하는지를
> 시각화합니다.)

> "Building on the framework from Pan et al. [15], we perform an MPPI-style sampling-based optimization with a kernel annealed across both iterations and the prediction horizon, which shifts from broad exploration to local refinement." (§3.2)
> (한글 해설 — 골격은 SPIDER 의 annealed sampling 이며, 여기에 noisy reference 대응 3종을 더합니다.)

> "Thus, we introduce additional $`H`$ warmup steps prepended to the reference. During warmup, the object is held in place (e.g., in mid-air) while the robot hand is free to move; afterwards, the weld is dropped and simulation proceeds as normal." (§3.2)
> (한글 해설 — **Warmup**: noisy 첫 프레임이 복구 불능 상태(예: 물체 미파지)로 초기화되는
> 문제와, annealed sampling 이 horizon 시작부의 H 스텝을 충분히 탐색하지 못하는 문제를 동시에
> 해소합니다. 파지 sampling·heuristic 가정 없이 기존 최적화 절차만 활용합니다.)

> "drawing inspiration from sim-to-real [69, 70], we introduce random forces to sample rollouts, thus encouraging controls robust to such perturbations." (§3.2)
> (한글 해설 — **Random force perturbation**: rollout horizon 이 fingertip 균형 같은 불안정
> 상호작용의 local minimum 에 갇히는 것을 막습니다. contact guidance 같은 대안과 달리
> high-fidelity reference 를 가정하지 않는 general-purpose 해법입니다.)

> "we add a constant penalty term for failed transitions: (1) lack of object-floor contact during resting reference timesteps and (2) lack of hand-object contact during in-hand reference timesteps. We define reference timestep stages by measuring reference hand-object distance under threshold $`\epsilon`$." (§3.2)
> (한글 해설 — **Transition reward**: "rest"↔"in-hand" 전이는 궤적의 임계 변곡점인데 noisy
> reference 에서는 tracking reward 만으로 step-function 적 상호작용을 강제하기 어렵습니다.
> 전이 실패에 상수 페널티를 주어 집기/놓기를 보강합니다.)

### 학습 셋업

- **시뮬레이터** — MuJoCo Warp, sim timestep 0.005s(200 Hz). 물체 메시는 CoACD 로 convex
  decompose 하고, 다접촉 안정화를 위해 2 mm 두껍게 dilate.
- **기준 reference 생성** — 먼저 mink 로 fingertip 위치를 맞추는 kinematic retargeting 으로
  reference 궤적을 만든 뒤, sampling-based dynamics-aware retargeting 을 수행.
- **최적화 스케줄** — 0.5s 마다 plan(2 Hz), horizon 3s. plan 당 1024 샘플 평가, 32 iteration
  최적화. 보상은 물체(위치·방향)·손(위치·방향·관절) tracking + 과도 침투 페널티 + transition reward.
- **하드웨어(로봇)** — 22-DoF Sharpa Wave 손. 실 배포는 Sharpa Wave 손 + UR3e 팔의 bimanual
  셋업, 양쪽 50 Hz 명령.
- **주요 하이퍼파라미터(Table 4)** — `num_samples=1024`, `max_num_iterations=32`,
  `horizon=3.0`, `knot_dt=0.2`, `terminal_rew_scale=10.0`,
  `penetration_penalty_scale=3000.0`, `transition_penalty_scale=0.5`,
  perturbation `num_perturb_samples=4`, `perturb_force_scale=0.5`,
  `perturb_prob=0.05`, `perturb_continue_prob=0.95`.

---

## 📊 실험 설정과 결과

평가는 단계별로 분리됩니다. 복원은 DexYCB(160 영상)·HOI4D(12 영상)에서 GT 손을 공급해
물체 수준 성능을 격리 측정하고, in-the-wild 150 영상에서는 GT 가 없어 human preference 로
평가합니다. retargeting 은 자체 in-the-wild 복원 데이터 655 reference 와 OakInk2(1,352
bimanual MoCap 궤적)에서, SOTA 인 SPIDER 를 Annealed Sampling baseline 으로 두고 세
컴포넌트를 점진 추가하며 측정합니다.

### 복원 결과

![Figure 5 — Object Tracking Comparison](https://arxiv.org/html/2606.19333/figures/tracking_comparison.jpg)

> "Figure 5: Object Tracking Comparison. We compare Ours and FoundationPose [17] for object tracking with head-to-head human evaluations on 150 videos (left), and visualize samples (right)." (§4.2)
> (한글 해설 — in-the-wild 150 영상에서 SOTA FPose 와의 head-to-head 인간 선호 비교를 보여줍니다.)

> "human raters prefer our object tracking over the state-of-the-art FPose 67% of the time, with most videos receiving unanimous preferences." (§4.2)
> (한글 해설 — 부록 기준 FPose 18%·tie 15% 로, non-tie 판정 중 79% win rate, 75% 영상이
> 만장일치, Fleiss' $`\kappa=0.65`$ (substantial agreement)입니다.)

**Table 2 — 복원 결과 (F-5 / F-10 ↑, Chamfer distance CD ↓)**

| Method | DexYCB F-5 ↑ | F-10 ↑ | CD ↓ | HOI4D F-5 ↑ | F-10 ↑ | CD ↓ |
|---|---|---|---|---|---|---|
| HO | 0.24 | 0.48 | 4.76 | 0.28 | 0.51 | 3.86 |
| IHOI | – | – | – | 0.42 | 0.70 | 2.7 |
| HORSE | 0.23 | 0.42 | 6.97 | 0.26 | 0.45 | 6.69 |
| MCC-HO | 0.36 | 0.60 | 3.74 | 0.52 | 0.78 | 1.36 |
| G-HOP | 0.31 | 0.49 | 8.11 | 0.69 | 0.91 | 0.63 |
| FoundationPose | 0.69 | 0.89 | 0.89 | 0.71 | 0.91 | 0.49 |
| Any6D | 0.69 | 0.88 | 0.97 | 0.71 | 0.91 | 0.50 |
| **Ours** | **0.71** | **0.93** | **0.66** | **0.72** | 0.91 | 0.49 |

> "we establish a new state-of-the-art on both DexYCB and HOI4D, outperforming all baselines." (§4.2, Table 2)
> (한글 해설 — DexYCB 에서 F-10 0.93·CD 0.66 으로 best, HOI4D 에서도 동급 최고 수준입니다.)

**Table 5 — 물체 추적 ablation (부록 C)**

| Pose Guidance | Candidate Selection | DexYCB F-5 | F-10 | CD | HOI4D F-5 | F-10 | CD |
|---|---|---|---|---|---|---|---|
| Fixed | Clustering | 0.70 | 0.91 | 0.74 | 0.69 | 0.91 | 0.50 |
| Adaptive | Random | 0.70 | 0.91 | 0.74 | 0.62 | 0.87 | 0.66 |
| Adaptive | Log-likelihood | 0.72 | 0.93 | 0.65 | 0.72 | 0.91 | 0.49 |
| Adaptive | Clustering | 0.71 | 0.93 | 0.66 | 0.72 | 0.91 | 0.49 |

> "adaptive pose guidance via point tracking consistently improves reconstruction quality, and clustering-based selection performs on par with pose-likelihood selection while being up to 30 $`\times`$ faster." (§4.2)
> (한글 해설 — 각 ablation 행이 격리하는 것: ① Fixed vs Adaptive guidance(특히 HOI4D 에서
> adaptive 가 우위), ② Random vs Log-likelihood vs Clustering 후보 선택(Clustering 이
> Log-likelihood 와 동급이면서 최대 30× 빠름 — 비디오 스케일 실용성의 근거).)

### Retargeting 결과

**Table 3 — Retargeting 결과 (Success ↑, Pos ↓, Rot ↓)**

| Method | Recon. Success ↑ | Pos ↓ | Rot ↓ | OakInk2 Success ↑ | Pos ↓ | Rot ↓ |
|---|---|---|---|---|---|---|
| Annealed Sampling (SPIDER) | 0.25 | 0.08 | 0.40 | 0.72 | 0.08 | 0.32 |
| + Warmup | 0.66 | 0.06 | 0.28 | 0.77 | 0.06 | 0.25 |
| + Perturbation | 0.67 | 0.06 | 0.30 | 0.79 | 0.03 | 0.14 |
| + Transition Reward | **0.71** | **0.05** | **0.28** | **0.81** | **0.03** | **0.15** |

> "On our reconstructed in-the-wild data, Do as I Do reaches a 71% success rate, significantly improving over the baseline of 25%." (§4.3, Table 3)
> (한글 해설 — 각 ablation 행이 격리하는 것: **Warmup** 이 25%→66% 로 가장 큰 단일 기여
> (noisy 첫 프레임 대신 안정·자연스러운 초기 상태 발견), **Perturbation** 은 정량 지표엔
> 미미하나 자연스러운 grasp 등 정성 결과를 개선, **Transition Reward** 가 임계 전이의
> 집기/놓기를 보강해 71% 로 마무리.)

> "Further validating our method on OakInk2, we also see consistent improvement with the introduction of each component, moving from a baseline of 72% up to 81%." (§4.3, Table 3)
> (한글 해설 — noisy reference 용으로 설계됐음에도 clean MoCap 궤적에서도 이득이 있고,
> 1,000+ bimanual 작업으로 잘 확장됨을 보입니다.)

### 실 배포 및 데이터 필터링 playbook

> "our pipeline produced 500 high-quality, human-verified dexterous manipulation trajectories across internet (53%), egocentric (31%), and generated (16%) videos." (§4.4)
> (한글 해설 — 10개 동작(whisking·pouring·dusting 등)을 다양한 물체 기하·grasp class
> (writing tripod·power·ventral·parallel extension)로 실 세계에서 실행. 단, 중력 정렬 후
> 카메라 좌표를 따르므로 초기 자세(x,y,z,yaw)는 수동으로 워크스페이스에 정렬 후 IK·배포.)

> "only 83 (4%) survive our quality check for the reconstruction pass ... implying a $`20\times`$ penalty in not properly preprocessing and filtering internet videos for robot learning." (§4.5)
> (한글 해설 — 100DOH 에서 2,000 클립 샘플 중 의미 있는 손-물체 상호작용은 187개(9%),
> 경계 밖·shot 경계·카메라 모션·SAM 3D 실패 등을 제하면 83개(4%)만 생존. best case 로도
> ~5%(107개)만 학습에 직접 유효 → 전처리·필터링의 중요성을 정량화한 playbook 의 핵심 수치.)

---

## ⚖️ 한계

- **강체·metric depth 가정** — 저자가 명시하듯 본 방법은 강체와 단안 RGB 의 준정확한 metric
  depth 예측을 가정합니다. 비강체(천·끈·관절체)나 depth 예측 실패 시 파이프라인 전체가
  무너지며, 이는 손-물체 정렬 식이 centroid $`z`$ 비율 스케일링에 의존하기 때문입니다.
- **접촉/occlusion 모호성** — 단안 관측은 손-물체 실제 거리에 본질적 모호성이 있어 물리적
  접촉과 단순 시각적 가림을 구분하기 어렵습니다. transition reward 의 threshold $`\epsilon`$
  가 이 모호성에 직접 노출되므로, $`\epsilon`$ 선택이 잘못되면 전이 보상이 오작동합니다.
- **장면 무지(scene-blind)** — 손과 물체 하나만 복원하고 전체 장면은 복원하지 않아 장애물·
  관절 제약 같은 환경 제약을 추론하지 못합니다. 완벽한 reference 라도 인간 의도는 hand-scene
  상호작용으로도 표현되므로 scene-level reasoning 부재는 구조적 갭입니다.
- **시뮬레이터 충실도 상한** — 현 물리 시뮬레이터가 실세계 동역학을 근사만 하므로 달성 가능한
  실세계 성능에 상한이 걸립니다. dynamics-aware 의 장점이 곧 sim-real gap 의 종속변수가 됩니다.
- **수동 초기 정렬 잔존(추론된 갭)** — §4.4 에서 실 배포 전 초기 자세(x,y,z,yaw)를 수동
  정렬한다는 점은, "인터넷→로봇" 자동화 주장에 수작업 한 단계가 남아 있음을 뜻합니다. 대규모
  자동 데이터 생산을 노린다면 이 수동 단계가 throughput 병목이 될 수 있습니다.
- **단일 임베디먼트 검증(추론된 갭)** — 모든 실험이 22-DoF Sharpa Wave 손 한 종에 묶여 있어,
  finger link 길이·articulation 이 다른 로봇 손으로의 일반화는 미검증입니다.

---

## ♻️ 재현성

- **코드/데이터** — 본문 HTML 에서 공식 코드 저장소 링크는 확인되지 않았습니다(프로젝트
  웹사이트 [do-as-i-do.com](https://do-as-i-do.com) 만 명시). 비교에 쓴 FoundationPose++
  (`teal024/FoundationPose-plus-plus`)·mink(`kevinzakka/mink`) 등 외부 의존성 저장소만 인용됩니다.
- **구성 요소** — HaWoR(손 추적)·SAM 3 / SAM 3D(분할·메시)·MoGe(depth)·GeoCalib(중력 정렬)·
  CoACD(convex decomp)·mink(kinematic retarget)·SPIDER(annealed sampling)·MuJoCo Warp(시뮬)
  등 기성 모델·도구의 조합이라 각 구성 요소의 공개 여부에 재현성이 좌우됩니다.
- **하이퍼파라미터** — retargeting 하이퍼는 Table 4 에 전부 명시되어 retargeting 단계는 비교적
  재현 가능하나, 복원 단계의 일부 임계값(자세 후보 수 $`N`$, transition threshold $`\epsilon`$
  구체값)은 본문에 수치가 명시되지 않았습니다.
- **하드웨어** — 22-DoF Sharpa Wave 손 + UR3e 팔(bimanual, 50 Hz). Kyutai 의 compute 자원 사용.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P0(VLA Datasets & Benchmarks) — primary.** 본 논문은 정확히 P0 의 핵심 관심사인
  *데이터 생성 방법*입니다. D24(priority data axis — egocentric human video 중심)에 직접
  닿습니다: ego/exo in-the-wild 영상을 robot-complete manipulation 데이터로 변환하는 파이프라인은
  egocentric 우선 데이터 축을 "수집"에서 "생성"으로 확장합니다. D27(license/usability bar)
  관점에서는 100DOH 같은 인터넷 소스 활용의 품질·라이선스 리스크를 §4.5 playbook 이 정량화합니다.
- **P4(Pretraining for Data-Efficient Adaptation) — secondary.** D22(pretraining data
  composition — egocentric vs mixed)에 닿습니다: 본 방법이 산출하는 human-video-derived dexterous
  데이터는 P4 의 사전학습 corpus 구성에서 "mixed human→robot retarget" 항목을 채울 후보 소스입니다.
- **Identity 지지/긴장** — Identity 의 "egocentric 중심 corpus"·"data is upstream of method"
  주장을 **지지**합니다. 다만 본 논문은 *데이터 파이프라인*이지 VLA 아키텍처(P1–P3)·world model
  (P5) 기여가 아니므로, hand-centric VLA-level 코어와는 직접 긴장이 없습니다.
- **경쟁자 함의** — P0 §5 Tracked Literature 의 UniHand-2.0(human→multi-hand retarget) 와
  같은 "human→robot retarget" 계열로, 규모(UniHand ~35k h, 30 임베디먼트) 대신 in-the-wild
  단안 RGB 일반성과 dynamics-aware 물리 검증을 차별점으로 내세웁니다.

---

## ✨ 핀 논문 대비 델타

P0 §5 의 핀 논문 **UniHand-2.0**([arXiv:2601.12993](https://arxiv.org/abs/2601.12993),
~35k h × 30 임베디먼트 human→multi-hand retarget) 대비 진정한 신규성:

- **데이터 소스의 일반성** — UniHand 가 대규모 인간 모션 corpus 의 retarget 에 초점이라면, Do as
  I Do 는 **단안 RGB in-the-wild 인터넷 클립 + 생성형 비디오 출력**까지 소스로 끌어들입니다
  (파지 prior·물체 카테고리 가정 없음).
- **물리 검증(dynamics-aware)** — 단순 kinematic retarget 이 아니라 시뮬레이션 내 sampling-based
  optimization 으로 dynamically-feasible 궤적만 산출하며, noisy reference 강건화 3종(warmup·
  perturbation·transition reward)이 핵심 차별점입니다.
- **complete pipeline** — "인터넷 영상 → 실 다지 손 rollout" 의 end-to-end 검증(500 궤적,
  10 동작 실 배포)을 명시적으로 닫았습니다.
- (보강) HOI4D 는 P0 methodology base 에 이미 retarget candidate 로 등재되어 있는데, 본 논문은
  바로 그 HOI4D 를 복원 벤치마크로 써 SOTA 를 보입니다(Table 2).

---

## ⚙️ 의사결정 함의

- **P0 데이터 파이프라인 후보 채택** — egocentric/in-the-wild 영상을 dexterous 데이터로 변환하는
  도구로서 `catalogs/datasets.md`(👤 human / 🔀 mixed) 의 잠재 소스 생성기로 추적할 가치가 있습니다.
  사내 ego 계획(D24)에서 "수집"에 더해 "기존 영상 retarget"을 병행하는 옵션을 제공합니다.
- **데이터 필터링 정책** — §4.5 의 100DOH playbook(4% 생존율, 20× 페널티)은 인터넷 영상 기반
  corpus 를 구성할 때의 **전처리·필터링 예산**을 구체화합니다. P0 의 license/usability bar(D27)에
  "원시 인터넷 영상 → 유효 클립" 수율을 명시적 메트릭으로 추가할 근거가 됩니다.
- **retargeting 하이퍼 참조** — 만약 사내 human-video retarget 을 시도한다면 Table 4 가 출발
  config (예: `num_samples=1024`, `horizon=3.0`, `penetration_penalty_scale=3000.0`,
  `transition_penalty_scale=0.5`)을 그대로 제공합니다. 시뮬레이터는 MuJoCo Warp, 물체는 CoACD
  decompose + 2 mm dilate 가 권장 셋업입니다.
- **메트릭 정의** — retargeting 성공률은 mean position error 임계 기반(본문 §4.1 에서 정의가
  도표에 의해 잘려 정확 임계값 미확보)으로, 사내 평가 시 Pos/Rot error + success rate 조합을
  채택할 수 있습니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 체크) 강체 가정 위반** — 사내 타깃 작업이 천·끈·관절체·가변형 물체를 포함하면 복원
  단계가 즉시 실패합니다. 타깃 물체 목록을 강체/비강체로 분류하는 것이 1차 sanity check 입니다.
- **metric depth 신뢰성** — MoGe 의 metric depth 가 사내 카메라·조명에서 얼마나 정확한지 먼저
  소규모 검증 필요. depth 가 틀리면 손-물체 정렬 식 전체가 어긋납니다(Fig. 4 의 "incorrect depth"
  사례).
- **임베디먼트 전이** — 본 논문은 22-DoF Sharpa Wave 전용입니다. 사내 손이 DOF·링크 구조가 다르면
  kinematic reference(mink fingertip matching)부터 재튜닝해야 하고, retargeting 보상 스케일도
  재보정이 필요할 수 있습니다.
- **시뮬레이터 의존** — MuJoCo Warp 위에 구축돼 있어 다른 시뮬레이터(Isaac/SAPIEN)로 옮기면
  접촉 모델·penetration 페널티(3000.0)·dilate(2 mm) 등이 그대로 통하지 않을 위험이 있습니다.
- **수동 초기 정렬의 확장성** — §4.4 의 수동 (x,y,z,yaw) 정렬이 사내 대량 생산에서 자동화되지
  않으면 throughput 병목이 됩니다. 데이터 1만 클립 규모를 가정한 비용 추정이 필요합니다.
- **컴퓨트 비용** — frame 당 N 자세 후보 sampling + plan 당 1024 샘플 × 32 iteration 의 비용이
  사내 GPU 예산에서 감당 가능한지(수 분/클립 주장)부터 벤치마크해야 합니다.

---

## 💡 컨텍스트 제안

- **P0 catalog 후보** — `catalogs/datasets.md`(🔀 mixed 또는 👤 human) 에 본 파이프라인이 산출하는
  human-video-derived dexterous 데이터(또는 파이프라인 자체)를 데이터 *소스 생성기*로 등재 검토를
  사람에게 제안합니다(현 시점 공식 데이터 릴리스 링크 미확인이라 보류 가능). context 파일은 수정하지 않았습니다.
- **D24 보강 후보** — egocentric 우선 데이터 축(D24)에 "기존 인터넷/ego 영상의 dynamics-aware
  retarget 을 통한 데이터 생성" 을 supplement 로 명시할지 여부를 사람이 판단하도록 제안합니다.
- **핀 교체는 비권장** — 본 논문은 데이터셋 릴리스가 아닌 *데이터 생성 방법*이라 P0 §5 의 8-핀
  데이터셋/벤치마크 캡에 직접 들어가기보다 methodology base 또는 catalog 항목이 더 적합합니다.
