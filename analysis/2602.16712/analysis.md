# Paper Analysis — One Hand to Rule Them All: Canonical Representations for Unified Dexterous Manipulation

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | One Hand to Rule Them All: Canonical Representations for Unified Dexterous Manipulation |
| 저자 | Zhenyu Wei, Yunchao Yao, Mingyu Ding |
| 링크 | [arXiv:2602.16712](https://arxiv.org/abs/2602.16712) · [Website](https://zhenyuwei2003.github.io/OHRA/) |
| 발행일 / 버전 | 2026-02-18 (v1) · 2026-05-15 (v2) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-26 |
| 관련 Pillar | P1, P3, P4 |
| 태그 | dexterity, sim2real |

---

## 🧭 한 줄 요약 (TL;DR)

다양한 다지 로봇손(dexterous hand)을 단일한 **파라미터 공간 + canonical URDF** 로 표준화하여, 형태(morphology)를 조건으로 받는 단일 정책이 서로 다른 손 구조에 걸쳐 학습·전이되도록 만드는 cross-embodiment 표현 프레임워크입니다. 미관측 손 형태에 대한 zero-shot grasping (예: 3-finger LEAP Hand 81.9%) 으로 그 일반화 능력을 입증합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 오늘날 다지 조작(dexterous manipulation) 정책은 손 설계를 고정된 것으로 가정하여, 운동학·구조 layout 이 다른 새 embodiment 으로의 일반화가 심하게 제약됩니다.
- **기존 접근의 한계** — URDF 는 손의 기하·운동학을 완전히 기술하지만 트리 구조이고 플랫폼마다 이질적이어서 신경망 입력으로 직접 쓰기 어렵고, point cloud / SDF 같은 3D 표현은 정적 기하만 담아 운동학·동역학 속성을 놓칩니다.
- **본 논문의 가설** — 인간 손에서 영감을 받은 공유 운동학 구조를 포착하는 **고정 파라미터 집합 + 표준 URDF** 로 손을 표현하면, (i) 학습 친화적 형태 조건 입력과 (ii) DoF 가 다른 손들에 걸친 통일된 action space 를 동시에 얻을 수 있다는 것입니다.
- **왜 지금 중요한가** — 손마다 정책을 재학습하는 현 방식은 데이터 수집 비용을 키우고 이종 하드웨어 간 데이터셋 재활용을 막아, 진보가 개별 손 설계에 파편화되어 있습니다. 통일 표현은 대규모·morphology-aware 학습으로 가는 확장 가능한 토대를 제공합니다.

---

## 🧩 핵심 기여

- 이질적인 다지 손의 형태·운동학 구조를 **단일 파라미터화 포맷(82개 파라미터 기본 / 173개 확장)** 으로 표준화하는 canonical representation 을 제안하여, 일관되고 학습 친화적인 구조 인코딩을 가능하게 합니다.
- canonical URDF 위에 **22-DoF 고정 통일 action space** 를 정의하고, 원본 ↔ canonical 조인트 벡터 간 양방향 매핑(parsing 기반)을 제공하여 서로 다른 DoF 손들에 걸친 정책 공유·전이를 가능하게 합니다.
- 파라미터 공간 위에 **VAE 를 학습해 16차원 morphology latent manifold** 를 얻고, 두 손 사이의 latent 보간이 부드럽고 물리적으로 의미 있는 형태 전이를 만들어냄을 보입니다.
- canonical 표현을 조건으로 받는 **cross-embodiment grasp 생성 정책**(diffusion + MLP)을 학습하여, 세 손(Allegro/Barrett/Shadow) 공유 학습이 손별 학습을 능가하고, ~100개 LEAP Hand 변형으로 확장 시 미관측 손에 zero-shot 일반화함을 시뮬레이션·실제 로봇에서 입증합니다.

---

## 🔑 기술 키워드

- **Canonical URDF** — 모든 손을 동일한 5-finger·22-DoF 틀로 강제하는 "표준 신발 사이즈" 같은 URDF — 손마다 다른 좌표·조인트 표기를 통일된 규약으로 다시 그립니다.
- **Canonical parameter space** — 손 형태를 고정 길이 벡터(palm/finger 반지름, link 길이, 조인트 origin/축/범위)로 압축한 표현 — 신경망 조건 입력으로 직접 쓸 수 있는 손의 "DNA".
- **Cross-embodiment policy learning** — 운동학·DoF 가 다른 여러 로봇손에 걸쳐 하나의 정책을 학습·전이하는 패러다임 — 본 논문의 표준화가 노리는 최종 목표.
- **Unified action space** — 비활성 조인트를 dummy 변수로 둔 22-DoF 공통 제어·관측 공간 — DoF 가 다른 손들의 조인트 순서·부호를 일치시킵니다.
- **Morphology latent manifold** — VAE 로 학습한 16차원 손-형태 잠재 공간 — 두 손 사이 보간이 연속적 형태 전이를 만드는 "손 모양 지도".
- **VAE (Variational Autoencoder)** — 파라미터 벡터를 잠재 분포로 인코딩·복원하는 생성 모델 — 형태의 compact·semantically-rich embedding 을 얻는 수단.
- **Morphology conditioning** — grasp 정책에 손 형태 표현을 조건으로 주입하는 기법 — 같은 정책이 손이 바뀌면 다르게 동작하도록 만듭니다.
- **Zero-shot generalization** — 학습 데이터에 없던 손 형태에 추가 fine-tuning 없이 정책이 동작하는 능력 — 표현의 일반화를 검증하는 핵심 지표.
- **Two-stage grasp generation** — wrist translation 을 diffusion 으로 샘플링한 뒤 조인트 구성을 MLP 로 회귀하는 2단계 grasp 파이프라인 — orientation 과 translation 을 분리해 grasp 방향을 직접 제어.
- **Action mapping / replay** — 원본 ↔ canonical 양방향 조인트 매핑으로 한쪽 공간에서 학습한 정책을 다른 공간에서 재생하는 검증 — canonical 표현의 동역학 충실도(fidelity)를 측정.

---

## 🔬 방법론

![Figure 1 — Canonical 표현 개요](https://arxiv.org/html/2602.16712/fig/teaser.png)

> "Figure 1: We introduce a canonical hand representation that unifies diverse dexterous hands into a shared parameter space and canonical URDF format, serving as a condition for cross-embodiment policy learning. It enables dexterous grasping and zero-shot generalization to novel hand morphologies, highlighting its potential for a wide range of dexterous manipulation tasks." (§1)
(한글 해설 — 통일된 파라미터 공간·canonical URDF 가 cross-embodiment 정책 학습의 조건 입력으로 쓰이며, grasping 과 미관측 형태 zero-shot 일반화로 이어지는 전체 그림을 한 장에 요약합니다.)

### 직관

이 논문의 출발점은 "손마다 URDF 가 제각각이라 정책을 재사용할 수 없다"는 실무적 통증입니다. 어떤 손은 손가락이 5개, 어떤 손은 3개이고, 같은 하드웨어조차 전역/국소 좌표축 정의가 달라 동일한 운동을 표현해도 숫자가 다르게 나옵니다. 저자들은 이 혼란을 "모든 손을 인간 손에서 영감을 받은 하나의 표준 틀에 끼워 맞추자"는 발상으로 풉니다. 표준 틀이란 최대 5손가락·22-DoF 를 가진 canonical URDF 이며, 실제 손은 이 틀의 부분집합(없는 손가락·조인트는 비활성)으로 표현됩니다.

표준 틀에는 두 얼굴이 있습니다. 하나는 **고정 길이 파라미터 벡터**(손바닥/손가락 반지름, link 길이, 조인트 위치·축·범위)로, 신경망이 손 형태를 "읽을 수 있는" 입력입니다. 다른 하나는 그 파라미터로부터 자동 생성되는 **표준 URDF** 로, 시뮬레이터에서 실제로 움직일 수 있는 모델입니다. 이 두 얼굴이 양방향으로 연결되어 있어서, 임의의 손 URDF 를 파라미터로 추출(parsing)하고 다시 표준 URDF 로 복원(generation)할 수 있습니다.

표준화가 주는 보상은 세 가지입니다. 첫째, 파라미터 공간 위에 VAE 를 학습하면 손 형태들이 연속적인 잠재 지도(latent manifold)를 이루어, 두 손 사이를 부드럽게 보간할 수 있습니다. 둘째, 22-DoF 고정 action space 덕분에 DoF 가 다른 손들이 같은 정책을 공유할 수 있고, 한쪽에서 학습한 정책을 다른 손에 그대로 재생(replay)할 수 있습니다. 셋째, 손 형태 표현을 grasp 정책의 조건으로 넣으면, 같은 정책이 손이 바뀔 때 그에 맞게 grasp 를 생성합니다 — 그리고 이 조건이 충분히 표현력이 있으면 학습 때 보지 못한 새 손에도 zero-shot 으로 일반화합니다.

핵심 주장은 "새로운 grasping 알고리즘을 제안하는 것이 아니라, canonical URDF 라는 표현·action space 자체의 유효성을 검증하는 것"입니다. 즉 단순한 모델조차 이 표현 위에서 학습하면 다양한 손에 걸쳐 고품질 grasp 를 만든다는 점이 메시지의 중심입니다.

### 아키텍처

**(1) Canonical URDF 설계 (§III-B).** 대표적인 상용·오픈소스 손 12종(Shadow, Allegro, LEAP, Barrett 등; Table I)의 운동학을 분석해, 대부분의 손이 인간 손에서 영감을 받은 공통 layout — 엄지의 2개 distal flexion + 선택적 abduction-adduction, 나머지 손가락의 abduction-adduction proximal 조인트 + flexion chain — 을 공유함을 관찰합니다.

> "Guided by these observations, we define a canonical URDF supporting up to five fingers and 22 DoF (Fig. 3), capturing the shared human-like topology." (§III-B1)
(한글 해설 — 공통 운동학 관찰을 바탕으로 최대 5손가락·22-DoF 의 표준 URDF 를 정의하며, 모든 link 를 capsule primitive 로 표현해 기하 복잡도를 낮추면서 핵심 운동학 관계를 보존합니다.)

좌표 규약도 통일합니다: 손바닥 법선을 $`+x`$, (오른손) 엄지를 $`+y`$, 나머지 손가락을 $`+z`$ 로 정렬하고, 국소 축은 abduction-adduction 에 $`x`$, flexion-extension 에 $`y`$, axial rotation 에 $`z`$ 를 씁니다 (§III-B2).

![Figure 3 — Canonical URDF 구조](https://arxiv.org/html/2602.16712/fig/canonical_URDF.png)

> "Figure 3: Structure of the canonical URDF. A right-hand configuration is shown for clarity, but the representation is applicable to both left- and right-handed hands." (§III-B1)
(한글 해설 — 표준 URDF 의 mesh·frame·운동학 골격을 시각화하며, 오른손 구성으로 보이지만 좌·우 손 모두에 적용 가능한 통일 구조임을 보입니다.)

**(2) Canonical 파라미터 (§III-C, Appendix -A).** 기본 표현은 **82개 파라미터**로 구성됩니다 (Table X): `palm_radius`(1), `finger_radius`(1), `finger_lengths`(6: 엄지 3 + 비엄지 공유 3), `finger_xyz`(15), `little_extra_origin`(6), `thumb_rpy`(3), `thumb_axes`(6), `joint_lowers`(22), `joint_uppers`(22). 비엄지 손가락은 동일 직경·동일 link 길이를 공유하고 palm 의 $`yz`$-평면에 놓인다고 가정하여 차원을 줄입니다. 구조 편차가 큰 손(예: Allegro 의 비엄지 joint1 이 $`+z`$ 축, LEAP 의 proximal 2조인트 swap)을 정확히 인코딩하기 위해 **173개 확장 파라미터**(per-finger 반지름·길이 + 12개 조인트의 origin/축 명시)도 제공합니다 (Table XI).

**(3) URDF parsing/generation (§III-D).** 임의 손 URDF 에서 canonical 파라미터를 추출하고, 최소 수동 입력으로 형태·운동학을 표준 공간에서 재구성하며, 파라미터로부터 완전한 URDF 를 생성합니다. 생성은 Jinja2 동적 템플릿으로 구현되어 손가락·link 수에 따라 element 를 조건부 포함합니다.

**(4) Action space 통일 (§III-E).** 모든 손이 22-DoF 고정 구조를 공유하고, 활성 DoF 가 적은 손은 해당 조인트를 비활성·link 제거합니다. parsing 의 joint-to-joint 매핑으로 원본 ↔ canonical 조인트 벡터를 일관된 indexing·부호 규약으로 양방향 변환합니다.

**(5) Morphology VAE (§IV-A, Appendix -C).** MLP 인코더가 입력 벡터를 hidden dim `[512,256,128]` + BatchNorm + ReLU 로 통과시켜 16차원 latent 분포의 평균·log-variance 를 출력하고, 디코더는 대칭 구조에 multi-head 출력(연속 기하 파라미터용 continuous head, 조인트 축 예측용 categorical head, 조인트 활성용 sigmoid head)으로 복원합니다.

**(6) Cross-embodiment grasp 생성 (§IV-C).** grasp pose 는 object frame 기준 wrist pose $`(T,R)`$ 와 조인트 구성 $`\theta`$ 로 정의됩니다. 2단계 파이프라인(Zhang et al. [42] 영감)으로, 1단계는 grasp feature $`f_{g}`$ 와 명시적 wrist rotation $`R`$ 을 조건으로 wrist translation 분포를 예측하는 diffusion 생성기, 2단계는 샘플된 $`(T,R)`$ 과 $`f_{g}`$ 를 조건으로 $`\theta`$ 를 예측하는 경량 MLP(결정적 매핑)입니다.

> "The grasp feature $`f_{g}`$ integrates both object and hand morphology information. Object features are extracted from the input point cloud using the $`\mathcal{D(R,O)}`$ point-based encoder, while hand features are obtained from the frozen VAE latent embedding introduced in Sec. IV-A." (§IV-C)
(한글 해설 — grasp feature 는 object point cloud 인코딩과 **frozen VAE latent** 손 형태 임베딩을 결합하여, 형태가 다른 손들에 걸쳐 grasp 예측을 일반화하게 합니다. 즉 morphology conditioning 의 통로가 바로 이 VAE latent 입니다.)

![Figure 6 — 2단계 cross-embodiment grasp 파이프라인](https://arxiv.org/html/2602.16712/fig/grasp_pipeline.png)

> "Figure 6: Two-stage cross-embodiment grasp generation pipeline." (§IV-B)
(한글 해설 — diffusion 으로 wrist translation 을 샘플링하고 MLP 로 조인트 구성을 회귀하는 2단계 구조를 도식화하며, 본문 §IV-C 의 grasp 생성 절차를 시각화합니다.)

### 학습 목표 / 손실

**Grasp 생성 손실 (§IV-C, Eq. 1).** diffusion 기반 translation 예측과 결정적 조인트 회귀를 모두 Smooth-$`L_{1}`$ 로 최적화합니다.

$$\mathcal{L}=\text{SmoothL1}(\hat{T},T)+\text{SmoothL1}(\hat{\theta},\theta)$$

**VAE 재구성 손실 (§Appendix -C3, Eq. 2).** 파라미터 종류별로 손실을 분리합니다.

$$\mathcal{L}_{\text{cont}}=\left\|\hat{q}_{\text{cont}}-q_{\text{cont}}\right\|_{2}^{2}$$
$$\mathcal{L}_{\text{axis}}=\text{CrossEntropy}(\hat{q}_{\text{axis}},q_{\text{axis}})$$
$$\mathcal{L}_{\text{joint}}=\text{BinaryCrossEntropy}\!\left(\sigma(\hat{q}_{\text{joint}}),q_{\text{joint}}\right)$$

여기서 $`q_{\text{cont}}`$ 는 연속 형태 파라미터, $`q_{\text{axis}}`$ 는 6-way 조인트 축 인코딩, $`q_{\text{joint}}`$ 는 이진 조인트 활성 지표입니다. 전체 손실은 KL 정규화를 더합니다 (Eq. 3).

$$\mathcal{L}=\mathcal{L}_{\text{cont}}+\mathcal{L}_{\text{axis}}+\mathcal{L}_{\text{joint}}+\beta\,\mathcal{L}_{\text{KL}}$$

> "where $`\beta=0.01`$ in all experiments." (§Appendix -C3)
(한글 해설 — KL 가중치 $`\beta`$ 를 0.01 로 작게 두어 재구성 충실도를 우선하면서 latent 를 정규화합니다.)

**In-hand reorientation 보상 (§Appendix -D2, Eq. 4).** PPO 보상은 z축 회전 reward 와 다수 penalty 의 가중합입니다. 회전 보상 $`r_{\text{rot}}=\text{clip}(\omega_{\text{z}},\omega_{\text{min}},\omega_{\text{max}})`$, pose penalty $`p_{\text{pose}}=\lVert q-q^{0}\rVert_{2}^{2}`$, torque penalty $`p_{\tau}=\lVert\tau\rVert_{2}^{2}`$, work penalty $`p_{\text{work}}=(\tau^{\top}\dot{q})^{2}`$, 속도 penalty $`p_{\text{v}}=\lVert\mathbf{v}\rVert_{1}`$ 이며 최종 보상은 다음과 같습니다.

$$r_{\text{base}}=s_{\text{rot}}r_{\text{rot}}-s_{\text{v}}\,p_{\text{v}}-s_{\text{pose}}\,p_{\text{pose}}-s_{\tau}\,p_{\tau}-s_{\text{work}}\,p_{\text{work}}$$

**Latent 보간 (§V-A).** 두 손 latent $`z_{a}`$, $`z_{b}`$ 에 대해 $`z(\alpha)=(1-\alpha)z_{a}+\alpha z_{b}`$ ($`\alpha\in[0,1]`$) 로 보간 후 디코딩하여 중간 형태를 생성합니다.

### 학습 셋업

- **VAE 데이터** — 각 canonical 파라미터를 물리적으로 타당한 범위에서 샘플링한 **65,536개 합성 손 구성**. 연속 형태 파라미터는 bounded interval uniform, 조인트 축은 6개 canonical 방향 $`(\pm x,\pm y,\pm z)`$ 의 one-hot, 조인트 가용성은 22 DoF 이진 지표로 인코딩.
- **VAE 최적화** — Adam, learning rate $`1\mathrm{e}{-4}`$, $`(\beta_{1},\beta_{2})=(0.95,0.999)`$, weight decay $`1\mathrm{e}{-6}`$.
- **Grasp 데이터** — D(R,O) Grasp [30] 가 제공한 필터링된 GenDexGrasp [13] 데이터셋(Allegro/Barrett/Shadow 3종, 8–22 DoF, **24,764개 유효 grasp**)을 canonical URDF 로 변환. zero-shot 실험용 LEAP 변형 데이터셋은 **69,917개 grasp**.
- **Grasp 모델 최적화** — MLP diffusion(hidden 512·256, step embedding 64), 1000 timestep "sample" prediction, Adam initial lr $`1\mathrm{e}{-3}`$ + cosine annealing → $`1\mathrm{e}{-7}`$. 추론은 10-step DDIM sampler, **0.13초**.
- **In-hand RL** — IsaacGym, MLP `[512,256,128]` + 단일 GRU(hidden 256) + ELU, PPO. LEAP 정책 400 gradient iteration(~200M env step), Shadow 정책 1,000 update iteration(~500M env step). 주요 PPO 하이퍼: $`\gamma=0.99`$, GAE $`\lambda=0.95`$, horizon 32, minibatch 32768, lr $`5\times 10^{-3}`$, clip $`\epsilon=0.2`$, KL threshold 0.02.
- **LEAP 변형 생성 (§IV-D)** — link 유무를 손가락별로 변화시켜 $`4^{4}=256`$ 개 변형(leap_xyzw, $`x,y,z,w\in\{0,1,2,3\}`$) 구성, grasp 데이터는 Lightning Grasp [37] 로 생성 후 D(R,O) 필터링. grasping 데이터셋은 $`x+y+z+w\geq 8`$ 을 만족하는 66개 변형으로 구축.

---

## 📊 실험 설정과 결과

**1) Canonical 충실도 — in-hand reorientation (§V-B1, Table II).** 원본 URDF vs canonical URDF 로 각각 in-hand 회전 정책을 학습해 비교합니다.

| Policy | Steps-to-Fall ↑ | Cumulative Rotation ↑ |
|---|---|---|
| Shadow (Original) | 369.66 | 9.09 |
| Shadow (Canonical) | 390.62 | 10.92 |
| LEAP (Original) | 397.62 | 5.63 |
| LEAP (Canonical) | 326.98 | 6.31 |

> "Table II reports the average performance, showing that canonical representations achieve comparable Steps-to-Fall and Cumulative Rotation." (§V-B1)
(한글 해설 — Shadow 는 canonical 이 두 지표 모두 소폭 상회, LEAP 는 Steps-to-Fall 이 397.62→326.98 로 하락하나 Cumulative Rotation 은 5.63→6.31 로 상승 — 전반적으로 canonical 화가 핵심 조작 동역학을 보존함을 보입니다.)

**2) Action mapping 전이 (§V-B2, Table III).** 한 공간에서 학습한 정책을 다른 공간으로 매핑해 재생합니다.

| Method | Allegro | Barrett | ShadowHand |
|---|---|---|---|
| Ours (Canonical) | 84.20 | 88.10 | 62.90 |
| Ours (Original) | 71.60 (-12.60) | 88.70 (+0.60) | 62.60 (-0.30) |
| D(R,O) (Original) | 92.30 | 87.30 | 83.00 |
| D(R,O) (Canonical) | 92.38 (+0.08) | 87.34 (+0.04) | 78.63 (-4.37) |

> "The main discrepancy occurs with the Allegro Hand, due to the omission of its axial-rotation joint in the canonical URDF, creating a minor structural mismatch." (§V-B2)
(한글 해설 — 양방향 전이가 대체로 근접하게 일치하나, Allegro 는 axial-rotation 조인트가 기본 canonical URDF 에서 생략되어 -12.60 의 가장 큰 손실 — 이것이 확장 173-파라미터 표현이 필요한 동기입니다.)

**3) Grasp 성능 비교 (§V-C, Table IV).** SOTA grasp 방법과의 비교입니다.

| Method | Allegro | Barrett | ShadowHand | Time (sec.) ↓ |
|---|---|---|---|---|
| DFC | 76.2 | 86.3 | 58.8 | >1800 |
| GenDexGrasp | 51.0 | 67.0 | 54.2 | 19.71 |
| D(R,O) Grasp | 92.3 | 87.3 | 83.0 | 0.65 |
| Ours | 84.2 | 88.1 | 62.9 | 0.13 |

> "Inference uses a 10-step DDIM sampler [25] and runs in only 0.13 s, making it the most efficient among the evaluated methods." (§V-C, Table IV)
(한글 해설 — 성공률은 D(R,O) 보다 낮으나 최적화 기반 refinement 없이 0.13초로 가장 빠르며, 목표는 새 grasp 알고리즘이 아니라 canonical URDF 를 downstream action space 로 검증하는 것임을 강조합니다.)

**4) Unified vs Specific (§V-C, Table V).** 공유 학습이 손별 학습을 능가하는지 검증합니다.

| Method | Allegro | Barrett | ShadowHand |
|---|---|---|---|
| Specific | 82.1 | 87.6 | 55.4 |
| Unified | 84.2 | 88.1 | 62.9 |

> "The unified model consistently outperforms embodiment-specific models (Table V), indicating that the canonical URDF enables effective policy sharing across morphologies." (§V-C)
(한글 해설 — Unified 가 세 손 모두에서 Specific 을 능가(특히 Shadow 55.4→62.9) — 공유 action space 에서 손들이 서로의 데이터로부터 이득을 본다는 핵심 cross-embodiment 주장의 직접 증거입니다.)

**5) Zero-shot 일반화 (§V-D, Table VII; underline=zero-shot).** 특정 LEAP 변형 데이터를 제외하고 학습 후 그 변형에 zero-shot 평가합니다.

| Model | leap_3033 | leap_3303 | leap_3330 |
|---|---|---|---|
| All Data | 76.1 | 85.4 | 43.3 |
| No leap_3033 Data | 67.8 (ZS) | 83.4 | 31.5 |
| No leap_3303 Data | 81.5 | 81.9 (ZS) | 46.9 |
| No leap_3330 Data | 74.7 | 81.6 | 36.3 (ZS) |

> "the models conditioned on hand morphology achieve performance on unseen hands comparable to that on seen hands, demonstrating strong zero-shot transfer capability across unobserved hand designs." (§V-D)
(한글 해설 — 초록의 "81.9% on 3-finger LEAP Hand" 가 No leap_3303 모델의 leap_3303 zero-shot 값으로, seen(All Data 85.4) 대비 근접 — morphology conditioning 이 미관측 손에 일반화함을 입증합니다.)

**6) 잘못된 hand condition 절제 (§V-D, Table IX; leap_3033 대상).** 의도적으로 틀린 손 조건을 주입한 결과입니다.

| Condition | All Data | Zero-Shot |
|---|---|---|
| leap_3303 | 85.4 | 81.6 |
| leap_3033 | 33.9 | 12.8 |
| leap_3330 | 20.5 | 2.4 |
| leap_3333 | 85.1 | 71.9 |

> "Overall, applying an incorrect hand condition substantially reduces grasp success rates." (§V-D)
(한글 해설 — 올바른 조건(leap_3033 자신)일 때보다 틀린 조건에서 성공률이 급락하며, zero-shot 에서는 더 극적으로 하락(예: leap_3330 조건 2.4%) — hand conditioning 이 단순 장식이 아니라 실제로 정책을 좌우함을 보입니다. gradient 시각화(Fig. 9)도 부재 손가락(ring·index)의 gradient 가 낮아 모델이 기능적 손가락에 집중함을 뒷받침합니다.)

**7) 실제 로봇 (§V-E, Table VI).** Franka Research 3 + LEAP Hand + RealSense L515, 10개 물체.

| Model | Average |
|---|---|
| leap_3333 (trained) | 83/100 |
| leap_3033 (trained) | 75/100 |
| leap_3033 (zero-shot) | 71/100 |
| leap_3303 (trained) | 70/100 |
| leap_3303 (zero-shot) | 71/100 |

> "the zero-shot models achieve success rates close to those of the trained models, highlighting strong generalization capabilities and the effectiveness of the hand condition in guiding grasping across unseen morphologies." (§V-E)
(한글 해설 — sim-to-real 전이가 신뢰성 있게 동작하고, zero-shot 모델(leap_3303 71/100)이 trained 모델(70/100)과 사실상 동일 — 시뮬레이션의 일반화가 실제 하드웨어에서도 유지됨을 보입니다.)

**8) Latent manifold (§V-A).**

![Figure 5 — Latent 보간](https://arxiv.org/html/2602.16712/fig/hand_interpolation.png)

> "Figure 5: Visualization of latent-space interpolation between two dexterous hands. Canonical URDFs are shown at the ends, with decoded reconstructions and interpolated morphologies in between, demonstrating smooth transitions in DoF, finger arrangement, and overall geometry." (§V-A)
(한글 해설 — 콤팩트한 3-finger gripper 와 high-DoF 손 사이 보간이 palm 크기·손가락 수·엄지 배치·DoF 에서 점진적으로 변해, VAE 가 연속적 형태 표현을 학습했음을 시각적으로 입증합니다.)

---

## ⚖️ 한계

- **기본 canonical URDF 의 구조 손실** — Allegro 의 axial-rotation 조인트 생략으로 action mapping 시 -12.60 의 성공률 손실(Table III)이 발생합니다. 기본 82-파라미터 표현이 모든 손의 운동학을 정확히 담지 못한다는 직접 증거이며, 173-파라미터 확장이 필요하지만 그만큼 차원이 커져 학습·일반화 부담이 늘어납니다.
- **표현 가정의 인간형 편향** — 비엄지 손가락 동일 직경·동일 link 길이·palm $`yz`$-평면 배치 등의 단순화 가정은 "인간형 다지 손"에 맞춰져 있어, 평행 그리퍼·비인간형 layout·tendon 결합이 강한 손에는 충실도가 떨어질 수 있습니다. 실제로 2-finger gripper 유사 변형(leap_0303, leap_3030)에서 zero-shot 성능이 상대적으로 낮습니다(§V-D).
- **Grasp 모델의 절대 성능 미흡** — Shadow Hand 에서 62.9% 로 D(R,O)(83.0%) 대비 격차가 큽니다. 저자는 "표현 검증이 목적"이라 방어하지만, 표준화 action space 가 5-finger high-DoF 손의 미세 grasp 를 충분히 표현하는지에 대한 의문은 남습니다.
- **In-hand reorientation 의 표현 충실도 비대칭** — LEAP 은 canonical 화 시 Steps-to-Fall 이 397.62→326.98 로 18% 하락(Table II)합니다. canonical 변환이 일부 손에서는 안정성을 침식하며, 어떤 형태가 손실에 취약한지에 대한 체계적 분석은 부족합니다.
- **데이터 생성 의존성** — zero-shot 실험은 Lightning Grasp + D(R,O) 필터로 손마다 grasp 데이터를 합성해야 하며, 표현 자체가 데이터 없이 일반화하는 것이 아니라 "많은 합성 손 변형으로 학습"한 결과입니다. 변형 수·필터 기준에 대한 민감도는 제시되지 않습니다.
- **태스크 범위의 협소함** — 검증은 grasping 과 in-hand 회전에 한정되며, 도구 조작·순차 조작 같은 long-horizon contact-rich 태스크로의 확장은 conclusion 의 전망으로만 제시됩니다.

---

## ♻️ 재현성

- **코드/데이터** — 본문에 GitHub repo 링크는 명시되지 않으며, project page (https://zhenyuwei2003.github.io/OHRA/) 만 제공됩니다. canonical 파라미터 정의(Table X/XI), VAE·diffusion·PPO 하이퍼파라미터(Appendix -C/-D/-E)는 상세히 기술되어 재현 명세가 비교적 풍부합니다.
- **외부 의존** — D(R,O) Grasp [30], GenDexGrasp [13], Lightning Grasp [37] 데이터·인코더, Jinja2 [17] 템플릿에 의존합니다.
- **하드웨어/시뮬레이터** — 시뮬레이션은 IsaacGym, 실제 로봇은 Franka Research 3 + LEAP Hand + Intel RealSense L515. grasp 성공 판정은 Isaac Gym 에서 6방향 외력 1초씩 인가 후 변위 <2cm (force-closure 기준, §Appendix -E2).

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P1(Heterogeneous Body/Hand Action Expert) — 핵심 연결.** 본 논문의 canonical action space 통일은 P1 의 **D3(Hand output space)** — v1 = (i) finger joint command — 와 직접 맞닿습니다. 22-DoF 통일 조인트 벡터(비활성 dummy 포함)는 "Hand expert 출력을 어떤 좌표계로 둘 것인가"에 대한 cross-embodiment 답변이며, 이는 우리의 hand 출력 표현 설계에 embodiment-agnostic 옵션을 제시합니다. **D2(Body output space)** 의 "both-wrist/tool-flange pose → embodiment-transfer easing" 동기와도 철학을 공유합니다(표준화로 전이 비용 절감).
- **P3(Hand-level System0, in-hand 안정화) — 강한 방법론 연결.** §IV-B 의 in-hand reorientation 은 PPO + AnyRotate 계열 보상 구조(회전 reward − pose/torque/work/velocity penalty − fall penalty)로, P3 의 **D17(System0 RL policy spec)** — PPO, GPU-parallel, AnyRotate term 구조 — 와 보상 설계가 거의 일치합니다. 우리의 Phase 1 데모(in-hand cube rotation)와 동일 태스크 패밀리이며, GRU + MLP `[512,256,128]` 아키텍처도 직접 참고 가능합니다.
- **P4(Pretraining for Data-Efficient Adaptation) — 보조 연결.** morphology conditioning 을 통한 zero-shot cross-embodiment 일반화는 P4 의 cross-embodiment lineage(D19, GR00T N1 계열) 와 동기를 공유하나, 메커니즘은 다릅니다(VLM 사전학습이 아니라 손-형태 조건 주입). 우리 스택이 손 형태 메타데이터를 정책 조건으로 넣을지에 대한 변수 제기.
- **Identity 긴장** — 우리 Identity 는 "단일 손(Sharpa 22-DOF) VLA-level dexterity" 에 집중하는 반면, 본 논문은 "여러 손에 걸친 일반화" 가 목표입니다. cross-embodiment 는 우리의 1차 목표가 아니므로, 가치는 "표현/action space 설계 아이디어" 와 "in-hand RL 보상·아키텍처 참고" 에 한정됩니다.
- **경쟁자 함의** — P1 §5 의 Demystifying Action Space Design (arXiv:2602.23408, joint=stability/task=generalization) 와 상보적입니다 — 본 논문은 joint-space 표준화의 cross-hand 일반화 가능성을 보여, action space 설계 논쟁에 morphology-conditioning 축을 추가합니다.

---

## ✨ 핀 논문 대비 델타

- **vs Demystifying Action Space Design (P1 §5 methodology base, arXiv:2602.23408)** — Demystifying 는 *단일 embodiment* 에서 joint vs task vs flange action space 의 stability/generalization trade-off 를 13k+ rollout 으로 분석합니다. 본 논문은 그 한 단계 위 — *여러 embodiment* 에 걸친 통일 joint action space 자체를 새로 정의하고, 형태 조건으로 cross-hand 일반화를 얻는다는 점이 새롭습니다.
- **vs Shared-Autonomy Arm-Hand VLA / DexGrasp-VLA (P1 핀, arXiv:2511.00139)** — 핀 논문은 *한 손* 의 arm/hand 해부학적 분리에 집중합니다. 본 논문은 분리가 아니라 *여러 손의 통일* 이라는 직교 축이며, 우리에게는 "Hand expert 출력 좌표계를 embodiment-invariant 하게 둘 수 있는가"라는 새 질문을 던집니다.
- **vs HORA (P3 핀, arXiv:2210.04887)** — HORA 는 *고정 손* 의 in-hand 회전 + RMA 입니다. 본 논문의 in-hand 실험은 동일 태스크지만, 원본 vs canonical URDF 의 *충실도 비교* 라는 새 관점을 추가합니다(표준화가 RL 동역학을 보존하는가).

---

## ⚙️ 의사결정 함의

- **D3(Hand output space) 후보 확장** — Hand expert 출력을 Sharpa-specific 22-DOF joint 벡터로 고정하는 대신, "canonical 22-DoF 통일 벡터(비활성 dummy 포함) + 손 형태 조건" 형태를 *옵션*으로 검토할 수 있습니다. 단, 우리 스택은 단일 손이므로 통일 action space 의 이득(데이터 공유)은 제한적 — 미래 in-house custom hand 전환 시 재학습 비용 절감 레버로만 보류.
- **D17(System0 RL) 보상·하이퍼 직접 차용** — in-hand reorientation 보상 5항(회전 − pose/τ/work/velocity penalty)과 PPO 하이퍼($`\gamma=0.99`$, GAE $`\lambda=0.95`$, lr $`5\times10^{-3}`$, clip 0.2, KL threshold 0.02, GRU hidden 256 + MLP `[512,256,128]`)을 우리 Phase 1 cube rotation 베이스라인 config 초기값으로 채택 검토. AnyRotate 핀과 교차 검증.
- **형태 조건 주입 메커니즘(P4)** — grasp 정책에 frozen VAE latent(16-dim)를 조건으로 넣는 설계는, 우리가 손 메타데이터(DOF·link 길이)를 정책 조건으로 넣을지 결정할 때의 참고 패턴. 단일 손에서는 불필요할 가능성이 높음(상수 조건).
- **검증 메트릭** — grasp 성공 판정(6방향 외력 1초씩 후 변위 <2cm, Isaac Gym)은 우리 grasp 평가 harness 의 force-closure 임계값 후보.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 체크) 단일 손 가정과의 적합성** — 우리는 Sharpa 22-DOF 단일 손이므로 cross-embodiment 통일의 핵심 이득(데이터 공유·zero-shot)이 사라집니다. 먼저 "통일 action space 가 단일 손 학습에 *순이득*인가, 아니면 dummy 조인트·표준화 오버헤드만 더하는가"를 종이 위에서 따져야 합니다 — 대개 후자일 가능성.
- **Sharpa 운동학의 canonical 표현 가능성** — Sharpa Hand(22-DOF, no wrist)가 82-파라미터 기본 표현으로 충실히 인코딩되는지 미지수. Allegro 사례(axial-rotation 생략 → -12.60)처럼 Sharpa 의 특수 조인트(예: tendon 결합)가 손실되면 표현 충실도가 떨어집니다. canonical 변환 후 FK 오차를 먼저 측정.
- **In-hand 충실도 비대칭** — LEAP 은 canonical 화 시 Steps-to-Fall 18% 하락(Table II). 우리 손에서도 표준화가 RL 안정성을 침식할 수 있으므로, Phase 1 도입 시 canonical 변환 없이 native URDF 로 먼저 베이스라인 확보 후 비교.
- **보상 하이퍼 전이** — IsaacGym + cube 회전에 튜닝된 보상 scale($`s_{\text{rot}}`$ 등 본문 미명시)은 우리 시뮬레이터(Isaac Sim/Isaac Lab)·손·물체에 그대로 전이되지 않습니다. scale 값이 본문에 없어(Table XII 도 scale 별도 미기재) 재튜닝 필수.
- **Grasp 절대 성능** — high-DoF 손(Shadow 62.9%)에서 격차가 크므로, 이 표현 위의 grasp 정책을 그대로 가져오면 우리 정밀 grasp 요구를 못 맞출 위험. 표현 아이디어만 차용하고 grasp 모델 자체는 별도 설계 권장.

---

## 💡 컨텍스트 제안

- **P3 §5 methodology base 후보** — 본 논문(arXiv:2602.16712)을 in-hand reorientation 보상·아키텍처 참고로 P3 methodology base 에 추가 검토 가능(단, cross-embodiment 가 주제라 우리 단일 손 scope 와 어긋나므로 핀 승격은 비권장). 사람 판단 영역.
- **P1 §5 comparison-group 메모** — action-space 설계 논쟁(Demystifying Action Space Design)에 "morphology-conditioned 통일 joint space" 라는 축을 추가하는 데이터 포인트로 비공식 기록 권장.
- 그 외 핀 교체/Decision 이동 제안 없음.

> 💡 base 매핑은 `/implement-design analysis/2602.16712/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
