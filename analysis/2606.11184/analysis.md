# Paper Analysis — TacForeSight: Force-Guided Tactile World Model for Contact-Rich Manipulation

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | TacForeSight: Force-Guided Tactile World Model for Contact-Rich Manipulation |
| 저자 | Yujie Zang, Yuhang Zheng, Xian Nie, Yupeng Zheng, Shuai Tian, Songen Gu, Chen Gao, Zining Wang, Shuicheng Yan, Wenchao Ding (TARS Robotics · National University of Singapore · Shanghai Jiao Tong University · Institute of Automation, CAS · Fudan University) |
| 링크 | [arXiv:2606.11184](https://arxiv.org/abs/2606.11184) · [Website](https://tacforesight.github.io/ProjectPage) |
| 발행일 / 버전 | 2026-06-09 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-11 |
| 관련 Pillar | P5, P2, P3 |
| 태그 | tactile, force, flow-matching |

---

## 🧭 한 줄 요약 (TL;DR)

손목 force/torque 신호를 조건으로 단기 미래 촉각 잠재 상태를 예측하는 경량 촉각 world model(TacForceWM)을 사전학습하고, 그 예측 잠재를 "선행 접촉 사전(anticipatory contact prior)"으로 정책에 주입함으로써, 반응형(reactive) 촉각 융합을 넘어 **예측형(proactive)** 접촉 추론으로 접촉 집약적(contact-rich) 조작의 외란 복원력을 끌어올린 연구입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 접촉 집약적 조작은 접촉 전이(contact transition)나 복잡한 표면 기하에서 힘·국소 기하·물체 자세가 빠르게 변하며 미끄러짐·정렬 오류·접촉 손실을 유발합니다. 로봇이 진화하는 물리 상호작용을 **지속적으로 지각·조절**해야 합니다.
- **기존 접근의 한계** — 최근 모방 학습은 촉각·손목 force/torque 피드백을 visuomotor 정책에 넣어 접촉 인지를 개선했으나, 대부분 두 신호를 별개 모달리티로 융합하거나 반응형(reactive) 제어 신호로만 씁니다. 본질적으로 반응형이라 **선행적·시간 협응적 상호작용 모델링**이 필요한 과제에서 한계가 있습니다.
- **본 논문의 가설** — global force와 local tactile은 **비대칭적 시공간 역할**을 가집니다. 손목 wrench는 고주파 전역 단서(외부 부하 변화)를, optical tactile은 국소 미세 변형을 포착하며, 거친-세밀(coarse-to-fine) 시간 의존성 속에서 **force 변화가 미래 촉각 상태의 선행 지표**로 작동합니다. 이 관계를 명시적으로 모델링하면 미래 촉각을 예측해 능동 제어가 가능합니다.
- **왜 지금 중요한가** — 인간 감각운동 제어가 부하 단서로 물체 상호작용을 예견하고 국소 접촉을 조정하듯, 고대역 force 신호로 촉각을 forecast하면 고주파 실시간 제어(20 Hz)에 맞는 효율적 예측 추론을 얻을 수 있습니다. 고차원 픽셀/촉각 관측 생성형 예측은 실시간 제어에 비용이 과합니다.

---

## 🧩 핵심 기여

- **TacForeSight** — 실시간 접촉 집약적 조작을 위한 compact force-conditioned 촉각 예측 프레임워크를 제안하고, 다양한 외란에서 관련 기법 대비 우월한 강건성을 실증합니다.
- **TacForceWM** — dual-finger 촉각 관측으로부터, 고주파 손목 force/torque 신호를 조건으로 **단기 촉각 잠재 동역학을 latent space에서 forecast**하는 촉각 world model을 도입합니다.
- **Predictive Tactile-Conditioned Policy** — 미래 촉각 잠재를 선행 접촉 사전으로 사용하고, current–future 촉각 진화를 cross-attention으로 모델링하며, tactile-guided gate로 **채널 단위 적응형 visuo-tactile 융합**을 수행하는 정책을 설계합니다.
- **비대칭 모델링 관점** — global force(선행 지표) ↔ local tactile(미래 상태)의 비대칭 시공간 관계를 명시적 cross-modal dynamics로 모델링한 점이 기존 반응형 융합과의 핵심 차별점입니다.

---

## 🔑 기술 키워드

- **TacForceWM (Force-conditioned Tactile World Model)** — 손목 wrench를 조건으로 미래 촉각 "잠재"를 내다보는, 픽셀이 아닌 압축 latent에서 동작하는 예측 모델입니다.
- **Force-to-Tactile prediction** — "엔진음(전역 force)이 바퀴 미끄러짐(국소 촉각)보다 먼저 들린다"는 식으로, 고주파 force 변화를 미래 촉각의 선행 신호로 쓰는 예측 패러다임입니다.
- **Chunk-based latent forecasting** — 한 프레임씩 one-step 예측 대신 시간 청크 단위로 미래 잠재 묶음을 한 번에 예측해 시간적으로 일관된 동역학을 얻는 방식입니다.
- **AdaLN (Adaptive Layer Normalization)** — DiT에서 온 조건 주입 기법으로, force 컨텍스트가 Transformer 중간 특징의 scale/shift를 변조해 "조건"을 흘려넣습니다.
- **SIGReg (Sketched Isotropic Gaussian Regularizer)** — LeJEPA에서 차용한 정규화로, 촉각 잠재 분포를 등방 가우시안 쪽으로 밀어 표현 붕괴(collapse)를 막습니다.
- **Cross-attention current–future interaction** — 현재 촉각을 query, 예측 미래 촉각을 key/value로 두어 현재 상태가 미래 단서를 "조회"하게 만드는 잔차(residual) 결합입니다.
- **Tactile-guided gating** — 촉각 표현에서 생성한 sigmoid gate로 시각·촉각 기여를 **채널 단위**로 동적 조절하는 융합 게이트입니다.
- **Conditional flow matching** — 노이즈→전문가 행동의 선형 보간 경로 위에서 속도장을 회귀해 행동 청크를 생성하는 경량 생성 정책 헤드입니다.
- **Wrist wrench conditioning** — 6축 손목 force/torque를 촉각 예측의 조건으로 쓰는 선택으로, ablation에서 RGB·robot state보다 우월한 물리 조건으로 확인됩니다.
- **DINOv2** — 동결(frozen)된 시각 백본으로 RGB를 인코딩해 시각 특징을 공급하는 자기지도 사전학습 인코더입니다.

---

## 🔬 방법론

TacForeSight는 두 단계의 cascade로 구성됩니다. Stage 1에서 force-conditioned 촉각 world model(TacForceWM)을 사전학습해 단기 촉각 진화를 latent space에서 예측하고, Stage 2에서 그 예측 촉각 동역학을 경량 flow 기반 행동 시퀀스 예측에 활용합니다.

> "we propose TacForeSight, a cascaded predictive framework that first pretrains a force-conditioned world model to predict short-horizon tactile evolution in latent space and then leverages the predicted tactile dynamics for lightweight flow-based action sequence prediction." (§III)
> (전체 설계 의도를 한 문장에 못 박는 anchor 입니다 — "world model 사전학습 → 예측 잠재를 정책에 주입"이라는 2단계 분리가 이 논문의 골격입니다.)

### 직관

핵심 발상은 **"힘이 촉각보다 먼저 말한다"** 입니다. 전구를 끼워 돌리거나(bulb locking) 관을 삽입할 때, 손목에서 느껴지는 급격한 force/torque 변화가 손끝 촉각 변화보다 항상 먼저 나타납니다. 즉 전역 force는 미래 국소 촉각의 **선행 지표**입니다. 기존 방법은 force와 촉각을 동시에 받아 "지금 상태"를 반응적으로 융합할 뿐, 이 시간 비대칭(force가 앞서고 촉각이 뒤따름)을 모델링하지 않습니다.

TacForeSight는 이 선행 관계를 학습으로 포착합니다. 먼저 촉각 world model이 "현재까지의 촉각 + 고주파 손목 force"를 입력받아 **곧 다가올 촉각이 어떤 모습일지**를 latent로 예측합니다. 중요한 점은 픽셀이나 원시 촉각 맵을 복원하지 않고 **압축된 잠재 공간에서만 forecast**한다는 것입니다 — 그래서 가볍고 빠릅니다(20 Hz). 이 "미래 촉각 잠재"는 접촉이 변하기 전에 미리 알려주는 사전 경보 역할을 합니다.

정책 쪽은 이 예측을 단순히 입력에 덧붙이지 않습니다. cross-attention으로 **현재 촉각이 미래 촉각 단서를 조회**하게 하고, 그 결과를 채널 단위 gate로 시각 특징과 적응적으로 섞은 뒤, flow matching 행동 헤드로 행동 청크를 생성합니다. 외란이 들어와 접촉이 흐트러져도, 미래 촉각 사전이 "곧 미끄러진다/정렬이 어긋난다"를 예고하므로 정책이 **선제적으로** 접촉을 재확립하고 복원합니다.

### 아키텍처

![Figure 2 — TacForceWM + Predictive Policy 전체 개요](https://arxiv.org/html/2606.11184/x1.png)

> "Figure 2: Overview of TacForceSight. Our framework consists of two coupled components. In Stage 1, a force-conditioned tactile world model encodes dual-finger tactile fields into compact latent representations and predicts tactile evolution conditioned on wrist force/torque signals. In Stage 2, the predicted tactile dynamics are used as contact priors for a lightweight flow-based policy." (§II-B)
> (한글 해설 — Stage 1 world model(좌)이 dual-finger 촉각을 잠재로 토큰화하고 force 조건으로 미래 잠재를 예측하면, Stage 2 정책(우)이 그 예측을 접촉 사전으로 받아 flow 기반 행동을 생성하는 2-coupled 구조를 시각화합니다.)

**(1) TacForceWM — Force-conditioned Tactile World Model.** 촉각 토크나이저 + force 인코더 + latent dynamics predictor 로 구성됩니다.

- **Tactile Tokenizer** — hybrid CNN-Transformer 입니다. 시각 $`t`$ 의 손가락별 촉각 필드는 $`\mathbf{X}_{t}^{s}\in\mathbb{R}^{H\times W\times 3}`$ ($`s\in\{L,R\}`$, 3채널은 각 위치의 dense 3D marker displacement)로 표기됩니다. 공유 spatial encoder $`\Phi_{\mathrm{sp}}`$ (residual conv + 계층적 downsampling)가 국소 변형 특징을 추출합니다 (식 1):

$$\mathbf{F}_{t}^{s}=\Phi_{\mathrm{sp}}(\mathbf{X}_{t}^{s})\in\mathbb{R}^{H^{\prime}\times W^{\prime}\times D_{h}}.$$

  인코더 가중치는 두 손가락에 공유됩니다. 접촉 기하와 손가락별 역할을 구분하기 위해 학습 가능한 spatial positional embedding $`\mathbf{E}_{\mathrm{pos}}`$ 과 finger-specific identity embedding $`\mathbf{E}_{\mathrm{id}}^{s}`$ 을 더합니다 (식 2):

$$\tilde{\mathbf{F}}_{t}^{s}=\mathbf{F}_{t}^{s}+\mathbf{E}_{\mathrm{pos}}+\mathbf{E}_{\mathrm{id}}^{s}.$$

  feature map을 patch 토큰으로 펼치고 학습 가능한 `[CLS]` 토큰을 붙인 뒤, 좌·우 손가락 토큰을 이어 Transformer에 통과시켜 손가락 내·손가락 간 상호작용을 self-attention으로 포착합니다. `[CLS]` 출력이 frame-level 촉각 잠재 $`\mathbf{z}_{t}\in\mathbb{R}^{D_{z}}`$ 입니다.

> "The [CLS] output is taken as the frame-level tactile latent ... This latent provides a compact representation of the joint in-hand interaction state for subsequent latent dynamics prediction." (§III-A1)
> (한글 해설 — 두 손가락의 접촉 상태를 하나의 `[CLS]` 잠재로 압축해, 이후 동역학 예측이 고차원 맵이 아니라 단일 벡터 위에서 돌도록 만드는 것이 토크나이저의 책임입니다.)

- **Force Encoder** — 고주파 손목 wrench에서 시간 일관적 조건을 뽑는 temporal encoder 입니다. 6축 force/torque 시퀀스 $`\mathbf{w}_{t-nH:t}\in\mathbb{R}^{nH\times 6}`$ ($`n`$ = 촉각 대비 sampling-rate 비율)을 촉각-정렬 조건 시퀀스로 매핑합니다 (식 3):

$$\mathbf{c}_{t-H:t}=G_{\phi}(\mathbf{w}_{t-nH:t}).$$

  원시 force/torque를 잠재로 사영한 뒤 dilated causal 1D conv 블록(WaveNet 계열)으로 multi-scale 시간 변화를 잡고, causal temporal downsampling으로 고주파 force를 촉각 잠재 시퀀스에 정렬합니다. 인과성(causality)을 보존해 미래 정보 누출 없이 조건을 만듭니다.

- **Latent Dynamics Predictor** — 원시 촉각을 복원하지 않고 미래 표현을 forecast하는 latent predictive 형식(V-JEPA 계열)입니다. frame-wise one-step 대신 **chunk 기반 forecasting**으로 시간 일관성을 얻습니다. 촉각 잠재 청크 $`\mathbf{z}_{t-H:t}`$ 와 정렬된 force 조건 $`\mathbf{c}_{t-H:t}`$ 가 주어지면 시간 offset $`\Delta`$ 만큼의 미래 잠재 청크를 추정합니다 (식 4):

$$\hat{\mathbf{z}}_{t-H+\Delta:t+\Delta}=T_{\psi}\left(\mathbf{z}_{t-H:t}^{\mathrm{tac}},\mathbf{c}_{t-H:t}^{\mathrm{tac}}\right),$$

  여기서 $`T_{\psi}`$ 는 force-conditioned latent Transformer 백본이며, force 조건은 **AdaLN**을 통해 wrench 컨텍스트에 따라 중간 특징을 변조하며 주입됩니다.

**(2) Predictive Tactile-Conditioned Policy.** 다중 모달 관측에서 시각·proprioception·촉각 잠재를 추출하고, current/predicted 촉각 잠재의 상호작용을 모델링해 시각과 융합한 뒤, conditional flow matching 헤드로 행동 청크를 예측합니다.

- **Multimodal Feature Extraction** — 현재 RGB는 **frozen DINOv2-small**로 인코딩해 $`\mathbf{h}^{\mathrm{img}}_{t}`$ 를 얻고, proprioceptive 이력 $`\mathbf{s}_{t-K+1:t}`$ 는 flatten 후 MLP로 $`\mathbf{h}^{\mathrm{s}}_{t}`$ 를 만듭니다. 촉각 토크나이저가 최근 H-frame 촉각을 $`\mathbf{z}_{t-H:t}^{\mathrm{tac}}`$ 로 인코딩하면, **사전학습된 world model**이 $`\mathbf{z}^{\mathrm{tac}}_{t-H:t}`$ 와 정렬된 force 특징 $`\mathbf{c}_{t-H:t}`$ 로부터 미래 촉각 잠재 $`\hat{\mathbf{Z}}^{\mathrm{tac}}_{t}`$ 를 예측합니다.

- **Current–Future Tactile Interaction** — 현재 잠재는 "현 상태", 예측 잠재는 "선행 동역학"을 담습니다. 둘의 상호작용을 cross-attention으로 명시화하되, 먼저 시간 순서를 보존하도록 learnable temporal embedding을 더합니다 (식 7):

$$\bar{\mathbf{Z}}_{t,cur}^{\mathrm{tac}}=\mathbf{z}^{\mathrm{tac}}_{t-H:t}+\mathbf{E}_{temp},\quad\bar{\mathbf{Z}}_{t,fut}^{\mathrm{tac}}=\hat{\mathbf{Z}}_{t}^{\mathrm{tac}}+\mathbf{E}_{temp}.$$

  현재 잠재를 query, 예측 미래 잠재를 key/value로 두어 현재 상태가 미래 단서를 조회하게 합니다 (식 8):

$$\mathbf{H}_{t}^{\mathrm{tac}}=\bar{\mathbf{Z}}_{cur}^{\mathrm{tac}}+\mathrm{CA}\left(Q=\bar{\mathbf{Z}}_{t,cur}^{\mathrm{tac}},K,V=\bar{\mathbf{Z}}_{t,fut}^{\mathrm{tac}}\right).$$

  이 잔차 구조가 즉시 접촉 상태에 예측 동역학을 보강하며, $`\mathbf{H}_{t}^{\mathrm{tac}}`$ 를 시간축 평균해 compact future-aware 촉각 표현 $`\mathbf{h}_{t}^{\mathrm{tac}}`$ 를 만듭니다.

- **Adaptive Visuo-Tactile Fusion** — 단순 concat이 아니라 예측 촉각 표현으로 모달 기여를 동적 조절하는 **채널 단위** 게이트입니다. 토큰 단위 융합(OmniVTA)과 달리 feature-channel 단위로 융합합니다. gate는 sigmoid MLP로 생성됩니다 (식 9):

$$\boldsymbol{\alpha}=\sigma\left(\mathrm{MLP}\left(\mathbf{h}_{t}^{\mathrm{tac}}\right)\right).$$

  시각·촉각을 공유 공간으로 사영 후 채널 단위 적응 융합합니다 (식 10):

$$\mathbf{h}_{t}^{\mathrm{vt}}=(\mathbf{1}-\boldsymbol{\alpha})\odot\mathbf{h}_{t}^{\mathrm{img}}+\boldsymbol{\alpha}\odot\mathbf{h}_{t}^{\mathrm{tac}}.$$

> "Rather than directly concatenating visual and tactile features, we introduce an adaptive channel-wise visuo-tactile fusion module that uses predictive tactile representations to dynamically regulate modality contributions according to interaction dynamics." (§III-B3)
> (한글 해설 — gate $`\boldsymbol{\alpha}`$ 가 촉각에서 나오므로, 접촉이 격렬할 때 촉각 채널을, 자유 이동 구간엔 시각 채널을 키우는 식으로 모달리티 비중을 상황에 맞게 바꾸는 것이 핵심입니다.)

- **Flow-matching Action Head** — 융합 특징 $`\mathbf{h}_{t}^{\mathrm{vt}}`$ 와 proprioceptive 특징 $`\mathbf{h}_{t}^{\mathrm{s}}`$ 를 concat·condition encoder를 거쳐 전역 조건 $`\mathbf{y}_{t}`$ 를 만들고, 행동 청크 $`\mathbf{A}_{t}=\mathbf{a}_{t:t+L-1}\in\mathbb{R}^{L\times d_{a}}`$ 를 예측합니다. (학습 목표는 아래 절.)

### 학습 목표 / 손실

**(A) World model 손실.** 예측 목표는 절대 미래 잠재와 그 1차 시간 동역학을 함께 감독해 촉각 진화를 잡고 over-smoothing을 줄입니다. 타깃/예측 미래 청크를 $`\mathbf{Z}_{t}^{\mathrm{tac}}`$, $`\hat{\mathbf{Z}}_{t}^{\mathrm{tac}}`$ 로 두면 (식 5):

$$\mathcal{L}_{\mathrm{pred}}=\mathrm{MSE}\left(\hat{\mathbf{Z}}_{t}^{\mathrm{tac}},\mathbf{Z}_{t}^{\mathrm{tac}}\right)+\lambda_{\mathrm{dyn}}\mathrm{MSE}\left(\nabla\hat{\mathbf{Z}}_{t}^{\mathrm{tac}},\nabla\mathbf{Z}_{t}^{\mathrm{tac}}\right),$$

여기서 $`\nabla`$ 는 청크 차원의 1차 시간 차분입니다.

> "The prediction objective jointly supervises absolute future tactile latents and their first-order temporal dynamics to capture tactile evolution and reduce over-smoothed latent predictions." (§III-A4)
> (한글 해설 — 절대값만 맞추면 예측이 평탄(over-smoothed)해지므로, 차분 항 $`\lambda_{\mathrm{dyn}}`$ 로 "변화의 속도"까지 맞춰 접촉 전이의 날카로움을 살리는 것이 의도입니다.)

표현 붕괴를 막기 위해 LeJEPA의 **SIGReg**(Sketched Isotropic Gaussian Regularizer)를 도입해 촉각 잠재 분포를 등방 가우시안 쪽으로 정규화합니다. 최종 world model 목표는 (식 6):

$$\mathcal{L}_{\mathrm{WM}}=\mathcal{L}_{\mathrm{pred}}+\lambda_{\mathrm{sig}}\mathcal{L}_{\mathrm{sig}}.$$

**(B) 정책 손실 — Conditional Flow Matching.** 전문가 행동 청크를 $`\mathbf{A}_{t}^{(1)}`$, 가우시안 노이즈 청크를 $`\mathbf{A}_{t}^{(0)}\sim\mathcal{N}(\mathbf{0},\mathbf{I})`$ 로 두고, flow time $`\tau\sim\mathcal{U}(0,1)`$ 에 대해 선형 보간 경로를 구성합니다 (식 11):

$$\mathbf{A}_{t}^{(\tau)}=(1-\tau)\mathbf{A}_{t}^{(0)}+\tau\mathbf{A}_{t}^{(1)},\quad\mathbf{u}_{t}=\mathbf{A}_{t}^{(1)}-\mathbf{A}_{t}^{(0)}.$$

temporal U-Net $`v_{\theta}`$ 가 이 경로의 조건부 속도장을 회귀합니다 (식 12):

$$\mathcal{L}_{\mathrm{FM}}=\mathbb{E}_{\mathbf{A}_{t}^{(0)},\mathbf{A}_{t}^{(1)},\tau}\left[\left\|v_{\theta}\left(\mathbf{A}_{t}^{(\tau)},\tau,\mathbf{y}_{t}\right)-\mathbf{u}_{t}\right\|_{2}^{2}\right].$$

추론 시 $`\mathbf{A}_{t}^{(0)}\sim\mathcal{N}(\mathbf{0},\mathbf{I})`$ 에서 시작해 학습된 ODE를 $`\tau=0`$ 에서 $`\tau=1`$ 까지 적분해 행동 청크 $`\hat{\mathbf{A}}_{t}`$ 를 얻습니다 (식 13):

$$\frac{d\mathbf{A}_{t}^{(\tau)}}{d\tau}=v_{\theta}\left(\mathbf{A}_{t}^{(\tau)},\tau,\mathbf{y}_{t}\right).$$

### 학습 셋업

- **2단계 학습** — Stage 1에서 TacForceWM(11.8M params)을 2,700개 force-tactile 상호작용 에피소드(과제별 시연 + 다양한 접촉 상호작용 데이터)로 150k step 학습합니다. $`\lambda_{\mathrm{dyn}}=1.00`$, $`\lambda_{\mathrm{sig}}=0.09`$. 이후 사전학습된 촉각 인코더와 predictor를 **동결**하고 그 잠재를 downstream flow-matching 정책(68.9M params) 학습에 사용합니다.
- **하드웨어** — 모든 실험은 8× NVIDIA A100 GPU에서 학습합니다. 추론은 RTX 4090D GPU에서 20 Hz.

> "We then freeze the pretrained tactile encoder and predictor to extract latent tactile representations for the downstream flow-matching policy (68.9M parameters)." (§IV-A2)
> (한글 해설 — world model을 먼저 학습·동결한 뒤 정책만 학습하는 분리 구조라, 정책이 표현 학습과 행동 학습을 동시에 떠안지 않습니다 — 경량·실시간성의 근거입니다.)

---

## 📊 실험 설정과 결과

**실험 플랫폼.** 7-DoF UFactory xArm7 + Robotiq 2F-85 그리퍼, Intel RealSense D435 손목 카메라, UFactory 6축 force/torque 센서, 양 손끝에 Xense 촉각 센서 2개. 이미지·촉각은 30 Hz, 손목 wrench는 120 Hz로 수집(즉 $`n=4`$). 각 촉각 센서는 `35×20` 3D displacement map을 출력합니다.

**과제.** 5개 접촉 집약적 과제 — Vase Wiping, Card Swiping, Tube Adjustment & Insertion, Bulb Insertion & Locking, Wire Insertion. + 3개 in-process 외란 — Wiping-P(height), Swiping-P(angle), Adjustment-P(pose). 각 과제 20회 독립 시행, 평균 완료 점수 보고(Wiping/Swiping은 완료 길이/목표 길이 비율, 2단계 과제는 1단계 50%·전체 100%, Wire Insertion은 완전 삽입 시만 성공, 외란 설정은 복원·완료 시만 성공).

**Baselines.** DP, DP+Tactile+Force, KineDex, FoAR(원 point-cloud 인코더를 2D RGB로 교체해 공정 비교), RDP.

| Policy | Wiping | Swiping | Adjustment | Locking | Insertion | Wiping-P | Swiping-P | Adjustment-P |
|---|---|---|---|---|---|---|---|---|
| DP | 70% | 35% | 30% | 10% | 15% | 0% | 0% | 0% |
| DP+Tactile+Force | 80% | 40% | 35% | 30% | 15% | 25% | 0% | 35% |
| KineDex | 30% | 35% | 25% | 45% | 30% | 10% | 0% | 0% |
| FoAR | 50% | 50% | 35% | 25% | 20% | 30% | 0% | 25% |
| RDP | 85% | 50% | 25% | 55% | 0% | 35% | 65% | 0% |
| **Ours** | **100%** | **85%** | **70%** | **80%** | **60%** | **90%** | **85%** | **85%** |

> "On the five representative contact-rich manipulation tasks, our method achieves an average completion score of 79.0%, substantially outperforming all baselines." (§IV-C1, Table I)
> (한글 해설 — nominal 5과제 평균 79.0%로 모든 baseline을 큰 폭으로 앞섭니다. 특히 다단계·정밀 접촉이 필요한 Locking·Insertion에서 격차가 큽니다.)

> "Across height, angle, and pose disturbances, our method achieves 90%, 85%, and 85%, respectively, with an average score of 86.7%, clearly outperforming all baselines." (§IV-C1, Table I)
> (한글 해설 — 외란 설정 평균 86.7%. 여러 baseline이 0%로 무너지는 Swiping-P·Adjustment-P에서 85%를 내며, 예측 촉각 사전이 동적 외란 복원에 결정적임을 보입니다.)

### 촉각 잠재 표현 분석

![Figure 4 — 촉각 잠재 시간 예측 + t-SNE 군집](https://arxiv.org/html/2606.11184/x3.png)

> "Figure 4: Tactile latent representation analysis. (a) Temporal visualization of tactile latents during Bulb Insertion and Locking and Vase Wiping. (b) t-SNE visualization of tactile latent embeddings on different primitive interactions." (§IV-C2)
> (한글 해설 — (a) 예측 잠재가 현재 잠재보다 접촉 전이를 앞서 반응함을, (b) pressing/twisting/sliding 등 접촉 패턴이 잠재 공간에서 잘 분리됨을 시각화합니다.)

> "the predicted tactile latents exhibit contact-related variations approximately 200 ms before similar changes appear in the current tactile latents." (§IV-C2)
> (한글 해설 — 예측 잠재가 현재 잠재 대비 약 200 ms 선행해 접촉 변화를 드러냅니다 — "force가 촉각의 선행 지표"라는 가설을 정량적으로 뒷받침하는 가장 직접적 증거입니다.)

t-SNE에서 미지(unseen) force–tactile 에피소드(pressing/twisting/sliding)의 sequence-level 임베딩이 접촉 패턴별로 잘 분리된 군집을 형성해, 인코더가 학습 분포를 넘어 접촉 판별적 표현을 학습함을 보입니다.

### Ablation — World Model Conditioning (Table II)

| Condition | MSE $`\downarrow`$ | Cos $`\uparrow`$ | KL$`_{\mathrm{sym}}`$ $`\downarrow`$ |
|---|---|---|---|
| w/o Condition | 0.027 | 0.954 | 0.014 |
| RGB Image | 0.025 | 0.973 | 0.013 |
| Robot State | 0.022 | 0.975 | 0.011 |
| Wrist Wrench | **0.017** | **0.992** | **0.009** |

> "Compared with the no-condition variant, it reduces MSE from 0.027 to 0.017 and KL sym from 0.014 to 0.009, while increasing cosine similarity from 0.954 to 0.992." (§IV-D1, Table II)
> (한글 해설 — 조건 후보 4종 중 wrist wrench가 모든 지표에서 최고입니다. RGB·robot state도 무조건보다 낫지만, 접촉 물리 변화를 직접 담는 손목 wrench가 미래 촉각 forecast에 가장 유익한 물리 조건임을 보입니다.)

### Ablation — Predictive Tactile Policy (Table III)

| Method | Wiping | Wiping-P | Swiping-P |
|---|---|---|---|
| Parallel fusion | 80% | 25% | 10% |
| w/o force condition | 70% | 50% | 75% |
| w/o predicted tactile | 65% | 15% | 15% |
| w/o cross-attention | 100% | 65% | 0% |
| w/o adaptive gate | 90% | 65% | 75% |
| **Ours** | **100%** | **85%** | **90%** |

- **Parallel fusion** — force·촉각을 단순 concat한 입력. 외란에서 Wiping-P 25%·Swiping-P 10%로 급락 → 단순 결합은 강건한 접촉 복원에 부족.
- **w/o predicted tactile** — 예측 촉각 제거(현재 촉각만). Wiping-P 15%·Swiping-P 15%로 명확히 하락 → 미래 촉각 사전이 접촉 유지·복원의 핵심.
- **w/o force condition / w/o cross-attention** — wrench 조건과 명시적 current–future 상호작용 둘 다 예측 촉각의 효과적 활용에 필요함을 확인(특히 w/o cross-attention은 Swiping-P 0%).
- **w/o adaptive gate** — Wiping-P 저하 + **복원 시간 2.56 s → 4.06 s 증가** → 적응형 융합이 외란 복원 중 접촉 조절을 개선.

> "Removing the adaptive gate also reduces Wiping-P performance and increases recovery time from 2.56 s to 4.06 s, suggesting that adaptive visuo-tactile fusion improves contact regulation during perturbation recovery." (§IV-D2)
> (한글 해설 — gate가 없으면 외란 후 접촉 재확립이 1.5 s가량 느려집니다 — 채널 게이트가 단순 정확도뿐 아니라 복원 "속도"에도 기여함을 보여주는 수치입니다.)

![Figure 5 — Vase Wiping 외란에서의 tactile gate 시각화](https://arxiv.org/html/2606.11184/x4.png)

> "Figure 5: Visualization of tactile gating on the Vase Wiping Perturbation. The top panel shows the tactile resultant force trajectory, with gating features projected to one dimension by PCA and overlaid as a colormap. The bottom panel shows representative tactile observations from four interaction stages." (§IV-D2)
> (한글 해설 — gate 응답이 접촉 단계별로 달라짐을 보여, 게이트가 변하는 접촉 조건에 맞춰 촉각 정보를 변조함을 시각적으로 입증합니다.)

---

## ⚖️ 한계

- **2-finger 평행 그리퍼 + Xense 평면 촉각에 국한** — 검증 하드웨어가 Robotiq 2F-85 그리퍼와 손끝 2개 `35×20` displacement map입니다. 다지(multi-finger) 손이나 손가락별 접촉 귀속이 필요한 손재주 조작으로의 확장은 검증되지 않았으며, "dual-finger" 설계(좌/우 identity embedding)가 N-finger로 자명하게 일반화될지는 미지수입니다.
- **World model 동결의 양면성** — 정책 학습 시 촉각 인코더·predictor를 동결하므로 경량·안정적이지만, 다운스트림 과제 분포가 world model 사전학습 분포에서 벗어나면 예측 잠재가 부정확해도 정책이 이를 교정할 경로가 없습니다. 2,700 에피소드라는 비교적 작은 규모의 사전학습 데이터가 일반화 상한을 정할 수 있습니다.
- **고정 예측 지평 $`\Delta`$ / 청크 $`H`$ 의 과제 의존성** — 약 200 ms 선행이라는 효용은 force가 촉각을 분명히 앞서는 과제(삽입·잠금)에서 가장 큽니다. force-tactile 비대칭이 약한 과제(예: 미끄러운 표면의 순수 활주, 비접촉 구간 비중이 큰 과제)에서는 선행 신호 자체가 빈약해 이득이 줄 수 있습니다.
- **SIGReg· $`\lambda`$ 민감도 미보고** — 표현 붕괴 방지에 SIGReg가 핵심 역할을 하지만 $`\lambda_{\mathrm{sig}}=0.09`$, $`\lambda_{\mathrm{dyn}}=1.00`$ 외 민감도 분석이 없어, 다른 센서·과제로 옮길 때 재튜닝 비용이 불확실합니다.
- **baseline 공정성 한쪽 조정** — FoAR는 원 point-cloud 인코더를 2D RGB로 교체해 비교했는데, 이는 FoAR의 기하 입력 이점을 제거한 변형이라 절대 성능 격차의 일부가 입력 모달리티 차이에서 올 가능성을 배제하기 어렵습니다.

---

## ♻️ 재현성

- **코드/데이터** — "All models and datasets will be made publicly available on the project website" (§Abstract) 로 모델·데이터셋 공개를 **예고**하나, 분석 시점 기준 프로젝트 페이지([tacforesight.github.io/ProjectPage](https://tacforesight.github.io/ProjectPage))에 공개 여부는 본문만으로 확정 불가입니다. arXiv GitHub 링크는 메타에 명시되지 않았습니다.
- **데이터 규모** — world model 학습 2,700 force-tactile 상호작용 에피소드(과제 시연 + 다양한 접촉 데이터). 과제별 nominal 시연 + 외란 복원 시연을 함께 수집.
- **하드웨어 명세** — xArm7 + Robotiq 2F-85 + RealSense D435 + UFactory 6축 F/T + Xense 촉각 2개, 학습 8× A100, 추론 RTX 4090D 20 Hz로 명시되어 재현 경로가 비교적 구체적.
- **파라미터** — TacForceWM 11.8M / 정책 68.9M, 150k step, $`\lambda_{\mathrm{dyn}}=1.00`$, $`\lambda_{\mathrm{sig}}=0.09`$. learning rate·batch·optimizer 등은 본문 미명시.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P5(action-conditioned world model 통합)** — 가장 직접적입니다. TacForceWM은 **action-conditioned가 아닌 force-conditioned 촉각 latent world model**로, D28(world-model role)의 "latent dynamics prior + future-prediction auxiliary"와 정확히 같은 역할(예측 잠재를 접촉 사전으로 정책에 주입)을 합니다. D29(integration architecture)에서는 world model을 먼저 학습·동결 후 정책을 붙이는 **2-stage decoupled** 구조로, VLA-JEPA 식 "JEPA pretrain → action-head fine-tune" 변형에 해당합니다. D30(prediction space)은 raw-pixel이 아닌 **latent 예측**으로 우리 v1(latent/3D-flow) 선택과 일치합니다. 다만 D31(action conditioning)·D32(egocentric hand-object)에서는 어긋납니다 — 조건이 action이 아니라 force이고, egocentric 인간 영상이 아니라 로봇 촉각·wrench입니다.
- **P2(구조적 다중 모달 관측 융합)** — Tactile Tokenizer(per-finger identity embedding + CNN-Transformer)는 D11(proprio-tactile-force token 구성)의 "per-finger 결합 + 공통 토큰 포맷" 정신과 통하고, current–future cross-attention + tactile-guided 채널 게이트는 D10(concat 넘어선 이종 모달 융합, cross-attention/AdaLN/asymmetric fusion)에 직접 대응합니다. 단 우리 D11이 요구하는 "swappable sensor head + Sharpa lock-in 회피"는 본 논문 범위 밖입니다.
- **P3(System0 접촉 안정화)와의 긴장** — 목표(접촉 유지·미끄러짐 복원)는 P3와 겹치지만, 본 논문은 **RL이 아니라 모방·flow matching**으로 이를 달성합니다. P3는 "reward-engineerable한 sub-problem에 한해 RL"로 좁게 정의되므로, TacForeSight는 P3의 직접 지지가 아니라 "RL 없이 예측형 모방으로도 외란 복원이 상당히 가능하다"는 **대안적 증거**입니다 — System0 도입 필요성의 임계선을 재고하게 만드는 경쟁 신호.
- **Identity 지지/긴장** — Identity의 "structured multimodal observation fusion(per-finger proprio-tactile binding, flat-concat 초월)"과 P5 "action-conditioned world model" 베팅을 동시에 지지합니다. 긴장점은 본 논문이 **VLA backbone(π) 없이** 소규모 from-scratch 정책으로 동작한다는 점 — 우리의 "VLA-level에서 dexterity tackle" 노선과는 스케일·백본 철학이 다릅니다.

---

## ✨ 핀 논문 대비 델타

- **P5 핀 대비** — DexWM(hand-object WM, 인간 영상)·LOME(action-conditioned egocentric WM)·AHEAD(motion-aware latent WM)·VLA-JEPA(JEPA latent WM)는 모두 **시각/영상 또는 action 조건** world model입니다. TacForceWM의 진짜 새로움은 조건 변수가 **고주파 손목 force/torque**이고 예측 대상이 **촉각 latent**라는 점 — 핀 논문 어느 것도 "force→tactile" cross-modal 예측을 다루지 않습니다. AHEAD가 "미래를 가로채 동적 조작을 돕는" 발상에서 가장 가깝지만, AHEAD는 시각 운동 예측, 본 논문은 접촉·촉각 예측으로 모달리티 축이 직교합니다.
- **P2 핀 대비** — ViTacFormer(cross-attention visuotactile)·ForceFlow(asymmetric multimodal fusion + V2F handover)가 가장 인접합니다. ForceFlow가 force/vision 비대칭 융합을 다루지만, TacForeSight는 비대칭을 **융합**이 아니라 **시간 예측**(force가 촉각을 200 ms 선행)으로 재정의한 점이 델타입니다. ViTacFormer 대비로는 "현재" cross-attention이 아니라 **current↔predicted-future** cross-attention이라는 시간축 확장이 새롭습니다.
- **non-pinned 인접** — 본 논문 자체 인용의 OmniVTA(visuo-tactile world modeling)·DreamTacVLA(촉각 예측 보조 목표)·Visuo-Tactile World Models가 같은 흐름이며, TacForeSight의 차별점은 "예측을 보조 목표로만 쓰지 않고 **실행 중 명시적 사전으로 주입**"하는 데 있습니다.

---

## ⚙️ 의사결정 함의

- **D30(prediction space) 보강 증거** — latent 예측이 raw-pixel 대비 20 Hz 실시간을 유지하면서 외란 복원에서 유효함을 실증 → 우리 v1 "latent/3D-flow" 선택을 지지. 픽셀 생성형 WM 연기(deferred) 근거가 강화됩니다.
- **새 config 후보 — `force_condition` 채널** — world model 조건으로 `wrist_wrench`(6축, 촉각 대비 `n×` 고주파)를 도입하면, RGB/robot state 조건 대비 MSE 0.027→0.017로 개선. 우리 P2 D11 토큰 구성에 **force/torque를 별도 고주파 조건 스트림으로 분리**(촉각과 동일 rate로 다운샘플 정렬)하는 설계 변수를 추가 검토.
- **loss term — `lambda_dyn`(temporal-difference MSE)** — 예측 잠재의 over-smoothing 방지에 1차 차분 MSE($`\lambda_{\mathrm{dyn}}=1.00`$)를 쓰는 것이 효과적. 우리 P5 latent WM 보조 목표에 동일 항을 후보로 채택.
- **정규화 — SIGReg($`\lambda_{\mathrm{sig}}=0.09`$)** — JEPA 계열 latent 예측에서 collapse 방지가 필수임을 재확인 → VLA-JEPA/ThinkJEPA 경로를 우리가 채택할 때 SIGReg(또는 VICReg류)를 기본 정규화로 포함.
- **아키텍처 — 2-stage freeze** — WM 사전학습·동결 후 정책 학습 분리가 경량·실시간성을 확보. 우리 P5 D29 "auxiliary head on shared backbone" v1과 비교해, **decoupled freeze** 변형을 실시간 제어 제약이 강할 때의 대안으로 평가.
- **메트릭** — world model 품질을 MSE / cosine similarity / symmetric KL 3종으로 직접 평가하는 프로토콜을 우리 latent WM ablation 메트릭으로 차용.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 체크) force–tactile 시간 비대칭이 우리 하드웨어에 존재하는가** — Sharpa Hand(22-DOF, **손목 DOF 없음**)에는 본 논문이 의존하는 손목 6축 F/T 센서 신호가 없습니다. 우리 스택에서 "global force 선행 지표"의 물리적 출처(손목 wrench)가 부재하므로, force conditioning을 그대로 옮기면 조건 신호 자체가 없습니다. 가장 먼저 "우리 손/팔에 어떤 force/torque 신호가 어디서 측정되는가"를 확인해야 합니다.
- **2-finger → 22-DOF 다지 손 전이** — dual-finger identity embedding과 `[CLS]` 단일 잠재로 "양손가락 joint 상태"를 요약하는 토크나이저가, per-finger 접촉 귀속이 핵심인 다지 손재주에 그대로 맞지 않습니다. 손가락 수가 늘면 단일 `[CLS]` 압축이 접촉 정보를 병목시킬 우려 — per-finger 토큰 보존(우리 D11)과 충돌할 수 있어 토크나이저 재설계가 선행되어야 합니다.
- **촉각 센서 modality 불일치** — 본 논문은 Xense `35×20` 3D displacement map. Sharpa Deform Map(~320×240/fingertip @30Hz)과 해상도·표현이 달라, 공유 spatial encoder를 옮기려면 sensor head 교체가 필요(우리 D11 "swappable sensor head"가 정확히 이 위험을 흡수하도록 설계됨).
- **소규모 사전학습 데이터의 일반화** — 2,700 에피소드로 WM을 동결 학습하므로, 우리 과제 분포가 이와 다르면 예측 잠재가 부정확하고 정책이 교정 불가. 옮기기 전 "우리 접촉 데이터로 WM 예측 MSE/cosine이 본 논문 수준(0.017/0.992)에 근접하는가"를 작은 파일럿으로 먼저 측정.
- **VLA backbone 부재 철학 충돌** — 본 정책은 frozen DINOv2 + 소형 from-scratch 정책(68.9M)입니다. 우리는 π backbone 위 flow-matching action expert 노선이므로, force-tactile WM 모듈을 우리 VLA 스택에 "보조 head"로 끼워 넣을 때 backbone과의 표현 정렬·동결 범위가 본 논문과 달라 그대로 재현되지 않습니다.

---

## 💡 컨텍스트 제안

- **P5 §5 Tracked Literature 후보** — TacForeSight는 핀 8편(hard cap)의 어느 것도 다루지 않는 **force-conditioned tactile latent world model**이라는 새 축을 엽니다. P5 핀 교체 1슬롯(예: raw-pixel branch와 중복이 큰 항목 대비) 또는 "Methodology base (non-pinned)"에 추가를 제안합니다. 등재 시 [arXiv:2606.11184](https://arxiv.org/abs/2606.11184), Role: "force→tactile latent WM; 예측 잠재를 접촉 사전으로 정책 주입 (D28/D30)".
- **P2 §5 인접 후보** — current↔future tactile cross-attention + 채널 단위 tactile gate는 ViTacFormer/ForceFlow 사이의 빈틈(시간 예측 기반 비대칭 융합)을 메웁니다. P2 non-pinned methodology base 후보로 검토.
- **P3 재고 트리거(약함)** — "RL 없는 예측형 모방으로 동적 외란 복원 86.7%"는 System0 RL 도입의 손익분기를 재평가할 신호입니다. 당장 D13–D18을 옮길 근거는 아니나, "System0가 필요한 잔여 실패 모드"를 정의할 때 본 논문 수준을 baseline 상한으로 잡아두는 것을 제안합니다.
- **카탈로그** — 공개 예고된 2,700-에피소드 데이터셋은 단일 task-군·sub-pretraining-scale이라 P0 anti-topic에 가까워 현재는 등재 보류 권장(공개 후 규모·라이선스 확인 시 재평가).

---

> 💡 base 매핑은 `/implement-design analysis/2606.11184/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
