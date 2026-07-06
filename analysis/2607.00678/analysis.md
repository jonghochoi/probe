# Paper Analysis — ABot-M0.5: Unified Mobility-and-Manipulation World Action Model

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | ABot-M0.5: Unified Mobility-and-Manipulation World Action Model |
| 저자 | Ronghan Chen, Yandan Yang, Zuojin Tang, Dongjie Huo, Tong Lin, Haoning Wu, Haoyun Liu, Yuzhi Chen, Lulu Zheng, Botai Yuan, Tianlun Li, Mingxin Wang, Dekang Qi, Bin Hu, Wei Mei, Yuze Xuan, Haolong Yang, Yanqing Zhu, Mu Xu, Zhiheng Ma, Xinyuan Chang (AMAP CV Lab, Alibaba) |
| 링크 | [arXiv:2607.00678](https://arxiv.org/abs/2607.00678) · [GitHub](https://github.com/amap-cvlab/ABot-Manipulation) |
| 발행일 / 버전 | 2026-07-01 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-07-06 |
| 관련 Pillar | P5, P1, P4, P0 |
| 태그 | flow-matching, vla-arch, sim2real |

---

## 🧭 한 줄 요약 (TL;DR)

모바일 매니퓰레이션에 맞춰 **시간 granularity · action space · train-test 일관성** 세 축을 동시에 정렬한 World Action Model(WAM) 로, (1) 비디오 latent 과 실행 action 사이를 잇는 **frame-level intermediate latent action**, (2) 이동/조작 action 을 분리하는 **dual-level Mixture-of-Transformers**, (3) 자기 예측 비디오로 inverse dynamics 를 학습하는 **Dream Forcing** 을 결합해 장기 지평·정밀 제어에서 SOTA 를 달성합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 로봇이 복잡한 환경을 **이동(navigation)** 하면서 동시에 **정밀 조작(manipulation)** 하는 mobile manipulation 을, 장기 지평에 걸쳐 안정적으로 수행하는 정책을 학습하는 것입니다.
- **기존 접근의 한계 (VLA)** — 반응형(reactive) VLA 정책은 명시적 world modeling 과 장기 메모리가 없어, 미래 상태 변화에 조건화된 결정을 내리지 못합니다.
- **기존 접근의 한계 (WAM)** — 기존 World Action Model 은 (a) 거친 video chunk 단위로 동작해 접촉 동역학 같은 미세 신호를 놓치고, (b) 이동/조작을 하나의 얽힌 action space 로 다뤄 최적화가 충돌하며, (c) autoregressive inference 와 맞지 않는 supervision 으로 inverse dynamics 를 학습합니다.
- **본 논문의 가설** — mobile manipulation 의 병목은 모델·데이터 규모가 아니라 **정렬(alignment)** 의 문제이며, 시간 granularity·action space·train-test 조건 세 축을 정렬하면 규모 확장 없이도 성능이 오른다는 것입니다.
- **왜 지금 중요한가** — WAM 을 정지형(stationary) 조작에서 이동형(mobile)으로 확장하려는 흐름에서, 단순히 chunk 를 늘리는 방식이 왜 실패하는지에 대한 구조적 진단과 처방을 제시하기 때문입니다.

---

## 🧩 핵심 기여

- 기존 WAM 이 mobile manipulation 에서 겪는 **세 구조적 병목**을 규정합니다: 거친 비디오 예측 vs 미세 제어의 **시간 granularity mismatch**, 이질적 이동/조작 행동의 **action structure mismatch**, 학습 vs autoregressive inference 의 **context(rollout) mismatch**.
- 세 병목을 각각 겨냥한 **ABot-M0.5** 아키텍처를 제안합니다: **intermediate latent action**(미세 motion 추상화), **dual-level Mixture-of-Transformers**(모달·action subspace 분리), **Dream Forcing**(train-test 일관 inverse dynamics 학습).
- RoboCasa365 / RoboTwin 2.0 / LIBERO·LIBERO-Plus / 실물 로봇에서 장기 지평 성공률과 미세 제어 정확도 양쪽에서 leading VLA·WAM baseline 을 능가함을 보이고, 각 컴포넌트 기여를 광범위한 ablation 으로 검증합니다.
- 3단계 progressive 학습 파이프라인(world model 사전학습 → latent action 사전학습 → progressive SFT)과, variable-length FlashAttention 기반 **structured attention**(~5× 속도) · **offset-based latent augmentation** 같은 시스템 최적화를 함께 제공합니다.

---

## 🔑 기술 키워드

- **World Action Model (WAM)** — 미래 관측(비디오)과 미래 action 을 하나의 생성 과정에서 함께 예측하는 모델. "다음에 무엇이 보일지"와 "무엇을 할지"를 같은 autoregressive 프로세스에 묶습니다.
- **Intermediate Latent Action** — 비디오 latent 과 실행 action 사이에 끼워 넣는 frame-level 중간 표현. 거친 화면 변화를 embodiment 에 덜 종속적인 "motion 의도"로 번역하는 중간 통역사 역할을 합니다.
- **Conditional Flow Matching (CFM)** — 노이즈에서 목표 분포로 가는 velocity field 를 회귀하는 simulation-free 생성 목표. 본 논문은 비디오·latent action·executable action 세 단계 전부를 CFM 으로 통일합니다.
- **Dual-level Mixture-of-Transformers (D-MoT)** — 두 수준에서 이질성을 분리하는 구조. 모달 수준(비디오/latent action/action)과 action 수준(이동 vs 조작)을 각각 전용 FFN·head 로 나눕니다.
- **Dream Forcing** — inverse dynamics 를 GT 비디오가 아니라 모델이 스스로 "꿈꾼(self-dreamed)" 미래 비디오에 조건화해 학습시키는 전략. 학습 조건을 배포 조건과 일치시켜 exposure bias 를 없앱니다.
- **Exposure Bias** — teacher-forcing 으로 이상적 조건에서만 학습한 모델이 배포 시 자기 예측 오차에 노출되며 오차가 누적되는 현상. sequence prediction·imitation learning 의 distribution shift 와 같은 뿌리입니다.
- **Teacher Forcing / Diffusion Forcing** — 기존 WAM 학습 패러다임 둘. 전자는 clean GT 비디오에, 후자는 임의 noise timestep 비디오에 action 을 조건화 — 둘 다 inference 조건과 어긋납니다.
- **Action Decoupling (move / manip)** — 저주파·전역적 base 이동과 고주파·국소적 arm 조작을 별도 sub-tower 로 분리해 gradient 간섭을 줄이는 설계.
- **ALAM (algebraic latent action model)** — 세 프레임 삼중항에 additive·reversal 대수 일관성을 부과해 구조화된 motion space 를 학습하는 latent action 인코더 사전학습 프레임워크(본 논문이 채택).

---

## 🔬 방법론

### 직관

ABot-M0.5 의 출발점은 단순합니다. 로봇이 방을 가로질러 이동하다가 컵을 잡으려면, 모델은 먼저 "화면이 앞으로 어떻게 바뀔지"(미래 비디오)를 상상하고, 그 거친 변화에서 "손이 지금 어느 방향으로 얼마나 움직여야 하는지"(미세 motion 의도)를 뽑아낸 다음, 이를 실제 관절 명령으로 번역해야 합니다. 기존 WAM 은 이 세 단계를 뭉뚱그려 비디오 latent 에서 곧장 action 으로 매핑하는데, 비디오는 여러 프레임을 압축한 거친 신호라 grasp 순간·접촉 시작 같은 짧은 사건이 뭉개집니다. 본 논문은 그 사이에 **frame-level latent action** 이라는 중간 다리를 놓아 granularity 간극을 메웁니다.

두 번째 직관은 "이동과 조작은 물리적으로 다른 동물"이라는 것입니다. base 이동은 느리고 전역적이며, arm 조작은 빠르고 국소적이며 접촉에 민감합니다. 이를 한 head 로 예측하면 고주파 조작 신호가 저주파 이동 신호를 흔들어 gradient 가 서로 간섭합니다. 그래서 **주의(attention)는 공유하되 FFN·head 는 subspace 별로 분리**하는 dual-level MoT 로, 협응은 유지하면서 학습 동역학만 분리합니다.

세 번째 직관은 학습과 배포의 조건 불일치입니다. 학습 때는 진짜 미래 비디오를 조건으로 주지만, 배포 때는 모델이 스스로 예측한(불완전한) 미래에 조건화해야 합니다. **Dream Forcing** 은 학습 단계에서부터 모델이 자기 예측 비디오를 조건으로 action 을 배우게 해, "내 상상이 틀렸을 때도 버티는" 강건성을 심습니다.

![Figure 1 — ABot-M0.5 개요](https://arxiv.org/html/2607.00678/x1.png)

> "Figure 1: Overview of ABot-M0.5. ABot-M0.5 is a granularity-aligned, action-disentangled, and train-test-consistent world-action model for mobile manipulation." (§1)
(한글 해설 — 3단계 학습 파이프라인(Pretrain·SFT1·SFT2)과 Video → Latent Action → Action 정렬 파이프라인, 그리고 이동/조작 action 분리라는 세 축을 한 장에 요약한 그림입니다.)

### 아키텍처

**백본과 입력.** ABot-M0.5 는 **Wan2.2 video diffusion** 백본 위에 세워진 video-action WAM 입니다. 3D VAE 가 다중 카메라 관측 `` $`o_{t}=\{I_{t}^{(1)},\dots,I_{t}^{(N_{c})}\}`$ `` 를 압축 비디오 latent `` $`z_{t}`$ `` 로, UMT5 text encoder 가 언어 지시 `` $`l`$ `` 을 조건 feature 로 변환합니다. 핵심은 국소 시각 상태 변화를 담는 frame-level latent action `` $`m_{t}`$ `` 를 도입해 거친 비디오 latent 과 미세 제어 사이의 다리로 삼는 것입니다.

**세 단계 cascade.** 생성은 clean 변수에 대한 구조화된 cascade 를 따릅니다.

$$z_{t+1}\rightarrow m_{t}\rightarrow a_{t}$$

> "This factorization decomposes direct video-to-action prediction into three distinct stages: world modeling, motion abstraction, and control generation." (§3.1)
(한글 해설 — 직접적인 video→action 매핑을 world modeling(미래 비디오) → motion abstraction(latent action) → control generation(실행 action) 세 단계로 쪼개, 각 단계가 이전 단계 출력에 조건화되도록 만듭니다.)

바라는 위계는 다음처럼 개념화됩니다(bridging space 가 미래 world 동역학과 물리적 실행을 잇는 결정적 고리입니다).

$$\text{Video Latent }z_{t+1}\rightarrow\underbrace{\text{Frame-level Motion Intents}}_{\text{Bridging Space}}\rightarrow\text{Robot Action }a_{t}$$

**세 토큰 스트림과 비대칭 정보 흐름.** 모델은 세 병렬 토큰 스트림을 처리합니다.

$$X_{t}=[X_{t+1}^{z},X_{t}^{m},X_{t}^{a}]$$

> "we enforce an asymmetric information flow: video latent tokens ($`X_{t+1}^{z}`$) are masked from attending to latent action tokens ($`X_{t}^{m}`$), as future motions are inherently unknown during video prediction." (§3.1)
(한글 해설 — 비디오 예측 시점에 미래 motion 은 알 수 없으므로 `` $`X_{t+1}^{z}`$ `` 는 `` $`X_{t}^{m}`$ `` 를 보지 못하게 막고, 반대로 action 토큰 `` $`X_{t}^{a}`$ `` 는 `` $`X_{t}^{m}`$ `` 에 명시적으로 attend 해 제어가 motion 의도에 grounding 되도록 합니다. 이 causal 마스크가 cascade 의 인과 순서를 강제합니다.)

![Figure 2 — 전체 아키텍처](https://arxiv.org/html/2607.00678/x2.png)

> "Figure 2: Overall architecture of ABot-M0.5. The model jointly predicts future video latents, frame-level latent actions, and executable actions through a structured, asymmetric cascade design of a dual-level MoT." (§3.1)
(한글 해설 — 세 스트림이 공유 trunk 를 통과하되 비대칭 마스크로 인과 순서를 지키며, action 스트림이 다시 mobile·manipulation 으로 갈라지는 구조를 보여줍니다.)

#### 컴포넌트 1 — Intermediate Latent Action Modeling

latent action 은 로봇 kinematic 라벨 없이 **시각 상태 변화만으로** 정의되므로, action-free 대규모 비디오에서 추출 가능합니다. 얼어붙은(frozen) 사전학습 인코더 `` $`E_{m}`$ `` 이 연속 프레임에서 국소 motion 표현을 뽑습니다.

$$m_{t}=E_{m}(I_{t},I_{t+1})\in\mathbb{R}^{d_{m}}$$

다중 카메라에서는 각 view 의 latent action 을 모아 `` $`M=\{m_{t}^{view}\}\in\mathbb{R}^{H\times N_{c}\times d_{m}}`$ `` 텐서로 구성합니다. latent action 생성은 CFM 으로 정식화됩니다.

$$\mathcal{L}_{\mathrm{m}}=\mathbb{E}_{m_{t},\epsilon,\tau}\left[\left\|v_{\theta}\big(m_{t}^{\tau};z_{\leq t+1},m_{<t},a_{<t},\tau,\,l\big)-(m_{t}-\epsilon)\right\|_{2}^{2}\right]$$

여기서 `` $`m_{t}^{\tau}=\tau m_{t}+(1-\tau)\epsilon`$ `` 는 보간 상태이고 `` $`v_{\theta}`$ `` 는 target velocity field 를 회귀하는 네트워크입니다. 주목할 점은 `` $`m_{t}`$ `` 가 **이미 예측된** `` $`z_{\leq t+1}`$ `` 에 조건화된다는 것 — cascade 순서가 학습 목표에 각인됩니다.

#### 컴포넌트 2 — Dual-Level Mixture-of-Transformers (D-MoT)

**모달 수준 분리.** 세 스트림(`` $`X^{z}`$ ``, `` $`X^{m}`$ ``, `` $`X^{a}`$ ``)은 같은 Transformer trunk 를 공유하되, 각자 전용 input projection·timestep embedding·output head 를 가져 표현 붕괴(representational collapse)를 막습니다.

**action 수준 분리.** 실행 action 스트림 내부에서 `` $`a_{t}`$ `` 를 조작 `` $`a_{t}^{manip}`$ `` 과 이동 `` $`a_{t}^{move}`$ `` 두 subspace 로 쪼갭니다.

> "we enforce a strict channel-to-subtower assignment, where each sub-tower is equipped with its own dedicated feed-forward network (FFN) and prediction head." (§3.3)
(한글 해설 — 채널을 sub-tower 에 엄격히 배정하고 각 tower 에 전용 FFN·head 를 두어, base 이동과 arm 조작의 학습 동역학을 엄격히 분리합니다. 고주파 조작 신호가 저주파 이동 예측을 흔드는 gradient 간섭을 차단하는 것이 목적입니다.)

**structured joint attention.** FFN 은 분리하되, 각 layer 의 self-attention 은 연결된 토큰 스트림 전체에 대해 수행됩니다. 즉 latent-action·mobility·manipulation 토큰이 하나의 attention 계산에 참여해 협응(예: base 재배치가 grasp 가능성에 영향)을 잃지 않으면서도, 후속 FFN 변환만 branch 별로 유지합니다.

![Figure 3 — Dual-level Mixture-of-Transformers](https://arxiv.org/html/2607.00678/x3.png)

> "Figure 3: Dual-level Mixture-of-Transformers. The architecture disentangles modality-specific representations and heterogeneous action subspaces while preserving coordinated reasoning through shared attention." (§3.3)
(한글 해설 — "attention 은 공유, FFN·head 는 분리"라는 D-MoT 의 핵심 트레이드오프를 도식화합니다.)

**subspace-aware CFM supervision.** 학습 시 action decoder 는 GT 상류 표현(`` $`z_{\leq k+1}`$ ``, `` $`m_{\leq k}`$ ``)을 받는 teacher-forced 조건화를 씁니다. 두 subspace 는 **하나의 공유 denoising timestep** `` $`\tau`$ `` 를 써 inference 의 병렬 joint denoising 과 정렬합니다. 노이즈 action 은 다음처럼 구성되고,

$$a_{t}^{\mathrm{move},\tau}=\tau a_{t}^{\mathrm{move}}+(1-\tau)\epsilon^{\mathrm{move}},\quad a_{t}^{\mathrm{manip},\tau}=\tau a_{t}^{\mathrm{manip}}+(1-\tau)\epsilon^{\mathrm{manip}}$$

두 branch 의 CFM 목표는 **서로의 노이즈 action 을 입력으로 받아** cross-subspace 협응을 가능하게 합니다.

$$\mathcal{L}_{\mathrm{a}}^{\mathrm{move}}=\mathbb{E}_{a_{t}^{\mathrm{move}},\epsilon^{\mathrm{move}},\tau}\left[\left\|v_{\theta}^{\mathrm{move}}\left(a_{t}^{\mathrm{move},\tau};z_{\leq t+1},m_{\leq t},a_{<t},a_{t}^{\mathrm{manip},\tau},\tau,l\right)-\left(a_{t}^{\mathrm{move}}-\epsilon^{\mathrm{move}}\right)\right\|_{2}^{2}\right]$$

$$\mathcal{L}_{\mathrm{a}}^{\mathrm{manip}}=\mathbb{E}_{a_{t}^{\mathrm{manip}},\epsilon^{\mathrm{manip}},\tau}\left[\left\|v_{\theta}^{\mathrm{manip}}\left(a_{t}^{\mathrm{manip},\tau};z_{\leq t+1},m_{\leq t},a_{<t},a_{t}^{\mathrm{move},\tau},\tau,l\right)-\left(a_{t}^{\mathrm{manip}}-\epsilon^{\mathrm{manip}}\right)\right\|_{2}^{2}\right]$$

$$\mathcal{L}_{\mathrm{a}}=\lambda_{\mathrm{move}}\mathcal{L}_{\mathrm{a}}^{\mathrm{move}}+\lambda_{\mathrm{manip}}\mathcal{L}_{\mathrm{a}}^{\mathrm{manip}}$$

#### 컴포넌트 3 — Dream Forcing

기존 WAM 학습 패러다임 둘은 각각 결함이 있습니다. Teacher Forcing 은 clean GT 비디오 latent 에 조건화하나 inference 때는 그런 GT 가 없어 exposure bias 가 심합니다. Diffusion Forcing 은 노이즈 비디오에 노출하나, 학습 때 독립 샘플된 다양한 noise timestep 조합이 inference 의 특정 denoising 궤적과 재현되기 어렵습니다.

> "Dream Forcing trains the action predictor on self-dreamed video latents produced by the model itself, as shown in Figure 4 (c). This design exposes the action model to the same type of imperfect visual states it will encounter at inference time" (§3.4)
(한글 해설 — action 예측을 모델 스스로 생성한 self-dreamed 비디오 latent 에 조건화함으로써, 학습 시점에 이미 inference 때 마주칠 불완전한 시각 상태와 같은 유형에 노출시킵니다. 조건화 컨텍스트를 inference 와 일치시켜 train-test 간극을 근본적으로 없앤다는 발상입니다.)

![Figure 4 — WAM 학습 패러다임 비교](https://arxiv.org/html/2607.00678/x4.png)

> "Figure 4: Training paradigms for World Action Models. ... (c) Our Dream Forcing conditions action prediction on self-dreamed videos generated by the model itself. This paradigm closely mirrors the inference process, achieving faithful train-test alignment" (§3.4)
(한글 해설 — (a) Teacher Forcing, (b) Diffusion Forcing 이 각각 어떤 train-test 불일치를 남기는지와, (c) Dream Forcing 이 이를 어떻게 해소하는지를 대조합니다.)

**two-phase forward.** 이를 구현하기 위해 하나의 forward 로 멀티모달 토큰을 함께 최적화하는 관행을 버리고, **dreamed latent 생성(Phase A)** 과 **action 예측 최적화(Phase B)** 를 분리합니다. Phase A 는 closed-loop 로봇 세팅에서 **가장 최근 미래 chunk 만** 꿈꾸면 되므로(과거 chunk 는 배포 시 실제 GT 로 계속 grounding 됨) sequential rollout 대신 **병렬 생성**을 쓰고, Self Forcing 을 따라 few-step denoising 으로 효율을 확보합니다. Phase B 는 이 dreamed latent 에 조건화해 action 예측 분포를 다음처럼 이동시킵니다(teacher-forcing → dream-forcing).

$$a_{t}\sim p_{a}(\cdot\mid\hat{z}_{t+1},z_{\leq t},\hat{m}_{t},m_{<t},a_{<t},l)$$

즉 미래 조건 latent `` $`z_{t+1},m_{t}`$ `` 만 self-dreamed `` $`\hat{z}_{t+1},\hat{m}_{t}`$ `` 로 교체됩니다.

### 학습 목표 / 손실

**Stage: World Model 사전학습.** Wan2.2 5B 가중치에서 초기화해 action-unconditioned 미래 비디오 예측기로 full-parameter 미세조정합니다. 이질적 카메라 구성을 다루기 위해 **fixed semantic slot allocation**(4개 canonical slot: third-person 2 + wrist 2, 부족분은 zero padding·마스킹)을 씁니다. latent-space CFM 손실은(padded 영역은 마스킹):

$$\mathcal{L}_{\mathrm{z}}^{\mathrm{pretrain}}=\mathbb{E}_{z_{t},\epsilon,\tau}\left[\left\|v_{\theta}^{z}\big(z_{t}^{\tau};z_{<t},\tau,l\big)-(z_{t}-\epsilon)\right\|_{2}^{2}\right]$$

**Stage: Latent Action Model 사전학습.** ALAM 프레임워크를 채택해, 삼중항 `` $`(o_{i},o_{j},o_{k})`$ `` 에 대수 일관성을 부과합니다.

$$\mathcal{L}_{\mathrm{add}}=\left\|m_{i}^{k}-(m_{i}^{j}+m_{j}^{k})\right\|_{2}^{2}$$

$$\mathcal{L}_{\mathrm{rev}}=\left\|m_{i}^{j}+m_{j}^{i}\right\|_{2}^{2}$$

전체 LAM 목표는 reconstruction·vector-quantization·perceptual 항을 더합니다.

$$\mathcal{L}_{\mathrm{LAM}}=\lambda_{\mathrm{vq}}\mathcal{L}_{\mathrm{vq}}+\lambda_{\mathrm{rec}}\mathcal{L}_{\mathrm{rec}}+\lambda_{\mathrm{perc}}\mathcal{L}_{\mathrm{perc}}+\lambda_{\mathrm{add}}\mathcal{L}_{\mathrm{add}}+\lambda_{\mathrm{rev}}\mathcal{L}_{\mathrm{rev}}$$

사전학습 후 **인코더 `` $`E_{m}`$ `` 만 남기고** decoder·VQ 모듈은 버려, offline feature extractor 로 latent action 라벨을 생성합니다.

**Stage: Progressive SFT — Stage I (joint, clean 조건).** 초기에는 GT 미래 비디오 latent 에 조건화해 안정적으로 학습합니다. 세 예측이 동시에 이뤄지고,

$$\mathcal{L}_{\mathrm{SFT1}}=\lambda_{z}\mathcal{L}_{\mathrm{z}}+\lambda_{m}\mathcal{L}_{\mathrm{m}}+\lambda_{a}\mathcal{L}_{\mathrm{a}}$$

**Stage: Progressive SFT — Stage II (Dream Forcing).** 모델이 초기 수렴에 도달하면 GT 미래 조건을 model-predicted `` $`\hat{z}_{t+1},\hat{m}_{t}`$ `` 로 교체합니다. action 손실은 dreamed 조건 버전으로 바뀝니다.

$$\tilde{\mathcal{L}}_{\mathrm{a}}^{\mathrm{move}}=\mathbb{E}_{a_{t}^{\mathrm{move}},\epsilon,\tau}\left[\left\|v_{\theta}^{\mathrm{move}}\big(a_{t}^{\mathrm{move},\tau};\hat{z}_{\leq t+1},\hat{m}_{\leq t},a_{<t},a_{t}^{\mathrm{manip},\tau},\tau,l\big)-(a_{t}^{\mathrm{move}}-\epsilon)\right\|_{2}^{2}\right]$$

$$\mathcal{L}_{\mathrm{SFT2}}=\lambda_{z}\mathcal{L}_{\mathrm{z}}+\lambda_{m}\mathcal{L}_{\mathrm{m}}+\lambda_{a}(\lambda_{a}^{\mathrm{move}}\tilde{\mathcal{L}}_{\mathrm{a}}^{\mathrm{move}}+\lambda_{a}^{\mathrm{manip}}\tilde{\mathcal{L}}_{\mathrm{a}}^{\mathrm{manip}})$$

### 학습 셋업

- **사전학습 corpus** — OXE, OXE-AugE, Agibot-Beta, RoboCOIN, RoboMind, Galaxea(base 이동 태스크 포함), InternData-A1(합성), 추가로 RoboNet·BridgeData V2·DROID. 모두 통일 포맷으로 표준화.
- **효율 최적화 (1) — Efficient Structured Attention** — 구조화 sparse attention 을 dense 하위 문제 집합으로 재구성해 variable-length FlashAttention 커널로 실행. FlexAttention-style baseline 대비 forward-backward 결합 pass 에서 **약 `` $`5\times`$ `` 속도 향상**.
- **효율 최적화 (2) — Offset-Based Latent Augmentation** — 고정 stride `` $`H`$ `` 로 latent 을 precompute 하되 시작 offset `` $`s\in\{0,1,\dots,H-1\}`$ `` 를 변주해 유효 latent 분할 수를 `` $`H`$ `` 배로 늘림 → 시간 다양성·타이밍 강건성 향상.
- **하드웨어/스텝 규모** — 논문 본문에 GPU 수·learning rate·batch size 는 명시되지 않았습니다. ablation 에서 등장하는 SFT step 규모는 warm-start 50k + DF 5k 수준입니다.

---

## 📊 실험 설정과 결과

**벤치마크·baseline·지표.** RoboCasa365(주 mobile manipulation 벤치, atomic/composite × seen/unseen), RoboTwin 2.0(bimanual, clean/randomized, 50 tasks), LIBERO / LIBERO-Plus(compositional tabletop, zero-shot 강건성), 실물 로봇(Agilex Piper 6-DoF 단일 arm, task 당 50 demo). 주 지표는 task success rate(실물은 success + process score).

### RoboCasa365 — 주 결과 (pretraining 세팅, Table 2)

| Method | Average | Atomic-Seen | Composite-Seen | Composite-Unseen |
|---|---|---|---|---|
| Diffusion Policy | 6.1% | 15.7% | 0.2% | 1.3% |
| $`\pi_0`$ | 14.8% | 34.6% | 6.1% | 1.1% |
| $`\pi_{0.5}`$ | 16.9% | 39.6% | 7.1% | 1.2% |
| GR00T-N1.5 | 23.9% | 50.7% | 14.8% | 2.7% |
| GigaWorld-Policy 0.1 | 20.7% | 44.4% | 11.8% | 2.9% |
| RLDX-1 | 33.2% | 63.0% | 27.5% | 5.4% |
| Qwen-RobotManip | 35.9% | 68.6% | 20.1% | 14.9% |
| **ABot-M0.5 (Ours)** | **40.4%** | **75.9%** | **38.3%** | 2.7% |
| ABot-M0.5 (+Condensed Memory) | 46.6% | 79.4% | 48.3% | 7.9% |

> "ABot-M0.5 achieves strong overall performance, with particularly clear gains on long-horizon composite tasks." (§5.2)
(한글 해설 — 평균 40.4% 로 직전 최고 Qwen-RobotManip(35.9%)을 넘고, 특히 Composite-Seen 에서 38.3% 로 큰 폭 우위입니다. 다만 Composite-Unseen(2.7%)은 Qwen-RobotManip(14.9%)에 크게 못 미쳐, 미지 조합 일반화는 약점입니다. +Condensed Memory 는 future work 로 예고된 확장입니다.)

### RoboCasa365 — Target 세팅 (Table 3)

| 세팅 | Method | Atomic-S | Composite-S | Composite-U | Average |
|---|---|---|---|---|---|
| Target 100% | GR00T-N1.5 | 60.6% | 35.0% | 33.3% | 43.7% |
| Target 100% | Lingbot-VA | 63.5% | 37.3% | 32.1% | 45.1% |
| Target 100% | **ABot-M0.5** | **70.6%** | **44.3%** | **45.6%** | **54.2%** |
| Target 10% | GR00T-N1.5 | 38.7% | 11.0% | 11.2% | 21.0% |
| Target 10% | **ABot-M0.5** | **49.0%** | **23.4%** | **15.4%** | **30.1%** |

(한글 해설 — Target 세팅에서는 Composite-Unseen 포함 전 범주에서 우위입니다. Target 10%(태스크당 50 궤적)에서도 30.1% 로 GR00T-N1.5(21.0%)를 크게 앞서, 저데이터 sample efficiency 를 보입니다.)

### RoboTwin 2.0 (Table 4) · LIBERO (Table 5)

| Model | RoboTwin Clean | RoboTwin Randomized | RoboTwin Avg |
|---|---|---|---|
| $`\pi_{0.5}`$ | 82.70 | 76.80 | 79.75 |
| Fast-WAM | 91.90 | 91.80 | 91.85 |
| Lingbot-VA | 92.93 | 91.55 | 92.24 |
| Qwen-RobotManip | 93.70 | 94.00 | 93.85 |
| **ABot-M0.5** | **94.00** | **94.20** | **94.10** |

| Method | L-Spatial | L-Object | L-Goal | L-Long | LIBERO Avg |
|---|---|---|---|---|---|
| $`\pi_0`$ | 98.0 | 96.8 | 94.4 | 88.4 | 94.4 |
| $`\pi_{0.5}`$ | 98.8 | 98.2 | 98.0 | 92.4 | 96.9 |
| CORAL | 99.6 | 99.8 | 99.0 | 98.8 | 99.3 |
| **ABot-M0.5** | **100.0** | 99.8 | 99.4 | 98.4 | **99.4** |

> "This indicates that the model does not rely solely on the mobile-specific structure of RoboCasa365, but also generalizes well to high-dimensional multi-task manipulation." (§5.3)
(한글 해설 — 이동이 없는 순수 조작 벤치에서도 latent action 추상화가 미세 제어를 돕고, rollout-aligned 학습이 시각 변동 강건성에 기여함을 시사합니다. 다만 LIBERO 는 이미 포화(99%대) 구간이라 우위 폭은 소수점입니다.)

### LIBERO-Plus zero-shot (Table 6, WAM 비교 초점)

| Method | Camera | Robot | Language | Light | Background | Noise | Layout | Total |
|---|---|---|---|---|---|---|---|---|
| Fast-WAM (WAM) | 16.4 | 44.5 | 68.9 | 78.2 | 53.7 | 37.7 | 60.7 | 51.5 |
| Cosmos-Policy (WAM) | 75.8 | 63.3 | 81.7 | 96.5 | 88.9 | 92.7 | 82.2 | 82.2 |
| ImageWAM (WAM) | 80.8 | 50.3 | 91.4 | 98.1 | 85.5 | 93.8 | 80.5 | 83.1 |
| **ABot-M0.5 (WAM)** | 70.5 | 87.4 | 88.6 | 94.0 | 89.7 | 75.5 | 85.2 | **83.4** |
| (참고) Qwen-RobotManip-Context (VLA) | 89.9 | 83.9 | 86.5 | 98.6 | 99.9 | 97.9 | 87.5 | 91.4 |

(한글 해설 — WAM 계열 내에서는 total 83.4% 로 SOTA 이지만, 최상위 VLA(Qwen-RobotManip-Context 91.4%)에는 미치지 못합니다. 저자도 "WAM 이 시각 교란에 민감"함을 명시하며 WAM 간 비교로 프레이밍합니다. Camera·Noise 범주는 상대적 약점입니다.)

### Ablation — 세 정렬 원리별 검증

**(1) Intermediate Latent Action (Table 7, RoboTwin Clean):**

| Training Strategy | Drop | Success Rate |
|---|---|---|
| Baseline (video→action 직접) | - | 87.60 |
| 2-Stage Separate | 0 | 90.86 |
| 2-Stage Channel Concat | 0 | 91.06 |
| 3-Stage Separate | 0.2 | 91.06 |
| **3-Stage Separate** | **0** | **94.00** |

(한글 해설 — latent action 을 독립 스트림으로 두고(3-Stage Separate) conditioning dropout 을 `` $`p_{\text{drop}}=0`$ `` 으로 두었을 때 94.0% 로 최고입니다. `` $`p_{\text{drop}}=0.2`$ `` 는 오히려 91.06% 로 떨어지는데, cascade inference 에서는 denoised latent action 이 항상 존재하므로 dropout 이 train-test 불일치를 만든다는 논리입니다 — Dream Forcing 과 같은 "일관성" 철학의 축소판입니다.)

**(2) Action-Decoupled MoT (RoboCasa365 Composite-Seen subset):** action-decoupled MoT 가 `` $`0.48`$ `` 로 Modality-level MoT baseline `` $`0.34`$ `` 를 능가하며 수렴도 더 빠릅니다 — cross-action gradient 간섭 감소를 뒷받침.

**(3) Dream Forcing (Table 8, RoboCasa365 Target Atomic-Seen):**

| Training Stage | Steps | Atomic-Seen |
|---|---|---|
| SFT1 (Base, warm-start) | 50k | 67.55 |
| SFT1 (teacher forcing 계속) | +5k | 66.78 |
| SFT1 (teacher forcing 계속) | +10k | 68.90 |
| **SFT2 (+DF)** | **+5k** | **70.56** |

> "Activating Dream Forcing and continuing training for mere 5k additional steps yields a substantial performance boost, elevating the success rate to 70.56% (an absolute improvement of 3.01%)." (§5.4)
(한글 해설 — 동일 50k warm-start 에서 DF 5k 만으로 +3.01%p(70.56%)인데, 같은 checkpoint 를 teacher forcing 으로 5k 더 돌리면 오히려 66.78% 로 퇴보하고 10k 를 써도 68.90% 에 그칩니다. 절반 예산으로 더 높은 성능 — train-test 간극 해소의 직접 증거입니다.)

**(4) Pretraining (Target 10% Atomic-Seen):** 사전학습 모델은 미세조정 후 49.0%, Wan2.2 에서 직접 미세조정하면 17.8% (**격차 31.2%p**). 저데이터에서 사전학습 prior 의 sample efficiency 기여가 큼을 보입니다.

### 실물 로봇 (Figure 12)

- **Peg Cylinder(정밀 삽입):** ABot-M0.5 **성공률 70% · process 96%**, vs $`\pi_{0.5}`$ (50% / 90%), FastWAM (30% / 77%).
- **장기 지평(plate/fruit/cup/flower):** 성공률 70% / 80% / 80% / 60%, process score 는 모두 88% 이상. FastWAM 은 20–40% 수준.

(한글 해설 — 태스크당 단 50 demo 로, 정밀 삽입과 장기 다단계 태스크 양쪽에서 baseline 을 앞섭니다. latent action 이 미세 motion 을, Dream Forcing 이 배포 강건성을 담당한다는 설계 서사와 일치합니다.)

---

## ⚖️ 한계

- **Composite-Unseen 일반화 취약** — pretraining 세팅에서 미지 조합 성공률이 2.7% 로, Atomic-Seen(75.9%) 대비 급락하고 Qwen-RobotManip(14.9%)에도 뒤집니다. 미래 비디오를 잘 "꿈꾼다"는 것이 새로운 태스크 **조합** 일반화로 직결되지 않음을 시사합니다 — world model 이 학습 분포 내 동역학은 잘 잡아도 조합적 태스크 구조 추상화는 별도 문제입니다.
- **시각 교란(Camera/Noise) 민감성** — 저자 스스로 "WAMs 는 시각 교란에 민감"함을 인정합니다. LIBERO-Plus Camera(70.5)·Noise(75.5)에서 최상위 VLA 에 크게 뒤지는데, 자기 예측 비디오에 조건화하는 구조가 입력 교란을 미래 예측 오차로 증폭시킬 수 있기 때문으로 읽힙니다.
- **막대한 생성 백본 비용** — Wan2.2 **5B** video diffusion + few-step denoising 을 매 chunk 마다 **두 번**(Phase A dream + Phase B action) forward 해야 합니다. 5× attention 최적화가 학습을 감당 가능하게 하지만, edge 실시간 배포는 저자도 future work 로 미뤄둔 미해결 과제입니다.
- **하이퍼파라미터·재현 세부 공개 부족** — `` $`\lambda`$ `` 가중치들, `` $`d_{m}`$ ``, horizon `` $`H`$ ``, few-step denoising step 수, GPU/learning-rate 등 핵심 수치가 본문에 없어, 정확한 재현은 공개 예정 코드에 의존합니다.
- **+Condensed Memory 의 미공개** — 최고 수치(46.6%)를 만든 memory 확장이 "future work 에서 설명"으로 미뤄져, 현재 논문의 검증 가능한 기여와 분리해 읽어야 합니다.
- **latent action 인코더 외부 의존** — 핵심 bridging space 가 별도 프레임워크(ALAM)의 frozen 인코더에 의존하므로, ALAM 품질이 상한을 설정하며 본 논문 단독으로 end-to-end 학습되지 않습니다.

---

## ♻️ 재현성

- **코드**: [github.com/amap-cvlab/ABot-Manipulation](https://github.com/amap-cvlab/ABot-Manipulation) 공개(논문 헤더 명시). 공개 시점의 완성도는 미확인.
- **데이터**: 사전학습 corpus 는 전부 공개 데이터셋(OXE, AgiBot, DROID, BridgeData V2 등) + InternData-A1 합성. 벤치마크(RoboCasa365, RoboTwin 2.0, LIBERO/LIBERO-Plus)도 공식 셋업 사용.
- **백본**: Wan2.2 5B(공개), ALAM latent action 인코더, UMT5 text encoder.
- **하드웨어**: 학습 하드웨어 규모 미공개. 실물 평가는 Agilex Piper 6-DoF 단일 arm.
- **주의**: 핵심 하이퍼파라미터·손실 가중치 미명시. 결정적 세부는 공개 코드 확인 필요.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P5(action-conditioned world model 통합) — 정면 대상.** 본 논문은 미래 비디오·latent action·executable action 을 하나의 생성 cascade 로 묶는 WAM 으로, P5 의 핵심 질문(어떻게 world model 을 stack 에 접느냐)에 대한 완결된 사례입니다.
  - **D28(world-model role)** — P5 v1 은 world model 을 "정책과 co-train 되는 latent dynamics prior + future-prediction auxiliary"(독립 planner 아님)로 둡니다. ABot-M0.5 는 이보다 강하게 **world model 이 곧 정책**입니다(미래 예측이 action 생성의 필수 조건). auxiliary 가 아니라 backbone 그 자체라는 점에서 D28 v1 과 긴장 관계 — "auxiliary head" 대신 "unified generative cascade" 노선을 지지하는 증거입니다.
  - **D29(integration architecture)** — P5 v1 은 "shared backbone 위 auxiliary head"(Being-H0.7 스타일)를 택하고, **fully unified autoregressive VLA+WM**(WorldVLA)을 attention-mask 간섭 위험이 있는 대안으로 추적합니다. ABot-M0.5 는 바로 그 **unified 노선**이며, 위험으로 지목된 attention 간섭을 **비대칭 causal 마스크 + D-MoT + structured FlashAttention** 으로 정면 관리합니다 — D29 대안 경로의 실현 가능성을 높이는 사례.
  - **D30(prediction space)** — P5 v1 은 **latent / 3D-flow**(접촉 관련, VLA-JEPA 를 pinned 인스턴스로) 예측을 택하고 raw-pixel 은 비용 문제로 유예했습니다. ABot-M0.5 는 3D VAE **비디오 latent**(사실상 압축된 raw-pixel 예측) + latent action 을 씁니다 — JEPA-식 의미 latent 이 아니라 생성형 비디오 latent 이라, D30 v1 과 노선이 갈립니다. "생성 비디오 latent 이 접촉 미세 신호를 못 잡는다"는 우려에 대해 본 논문의 답이 **intermediate latent action** 입니다.
  - **D31(action conditioning)** — P5 v1 의 per-frame action-conditioned 예측과 정확히 일치(LOME/DexWM lineage). ABot-M0.5 의 cascade 는 매 frame action 조건화를 강제합니다 — D31 지지.
  - **D32(egocentric hand-object)** — **미지지/하향.** 본 논문은 3인칭 + wrist 로봇 데이터의 **mobile** manipulation 이지 egocentric **human** video 의 hand-object 예측이 아닙니다. P5 의 hand-centric 협소화(D32)와는 어긋나므로, hand-object 관련성보다 **WAM 방법론(D28–D31)** 축에서만 참조해야 합니다.
- **P1(이질적 Body/Hand action expert) — 강한 방법론 이웃.** action-decoupled MoT(base 이동 vs arm 조작을 전용 FFN·head 로 분리하되 attention 공유)는 P1 의 **D1(split form: shared trunk + split heads)** · **D5(control-rate separation: 저주파 base vs 고주파 arm)** 와 구조적으로 동형입니다. 우리의 Body/Hand 를 Base/Arm 으로 치환한 실증 — gradient 간섭 감소·수렴 가속(0.48 vs 0.34)이 split 설계의 이점을 뒷받침합니다.
- **P4(data-efficient adaptation 사전학습) — 이웃.** 3단계 progressive 학습(world model 사전학습 → latent action 사전학습 → progressive SFT)은 P4 **D21(staged recipe)** 와, latent action 을 action-free 비디오에서 학습하는 구조는 **D22(pretraining data composition)** 와 맞닿습니다. Target 10% 에서 사전학습 격차 31.2%p 는 D21 의 "사전학습이 저데이터 적응의 상류 레버"라는 명제의 직접 증거.
- **P0(datasets) — 이웃.** 사전학습 corpus(OXE/AgiBot/DROID/BridgeData V2/Galaxea + InternData-A1)는 P0 의 데이터 스카우팅 범위와 겹칩니다. 다만 P0 **D24** 는 egocentric human video 중심을 우선하는데, 본 논문은 **3인칭·wrist 로봇** corpus 중심이라 우선순위 축이 다릅니다.
- **Identity 긴장.** PROBE 의 정체성은 **hand-centric dexterous** manipulation(손가락 접촉·촉각)입니다. ABot-M0.5 는 gripper·base 이동 중심의 mobile manipulation 으로, 손 dexterity·촉각이 전혀 없습니다. 방법론(WAM 정렬 3원리)은 강하게 전이 가능하나, 태스크 도메인은 우리 flagship(in-hand reorientation, tool articulation)과 직접 겹치지 않습니다.

---

## ✨ 핀 논문 대비 델타

- **vs WorldVLA (P5 pinned, D29 대안).** WorldVLA 는 action·image 상호 예측의 unified autoregressive VLA+WM 이고 attention-mask 간섭 완화가 핵심 기여였습니다. ABot-M0.5 는 여기에 **(a) 중간 latent action 단계**를 명시적으로 끼워 granularity 간극을 처리하고, **(b) action 내부까지 subspace 로 분리**(D-MoT 2단계)하며, **(c) Dream Forcing** 으로 train-test 간극을 정면 해결합니다 — WorldVLA 의 "unified" 방향을 유지하되 세 축의 정렬을 새로 추가한 것이 델타입니다.
- **vs Being-H0.7 (P5 pinned, D28/D29).** Being-H0.7 은 egocentric **human** video 의 latent world-action(Prior/Posterior latent reasoning)입니다. ABot-M0.5 의 진짜 새로움은 **train-test 일관성(Dream Forcing)** 과 **이동/조작 이질성 처리(D-MoT)** 로, 둘 다 Being-H0.7 이 다루지 않는 **mobile·robot** 세팅 특유의 문제입니다. 반대로 hand-object·egocentric 축에서는 Being-H0.7 이 우리 정체성에 더 가깝습니다.
- **vs World Guidance (P5 pinned, WAM 계열).** condition space 에서 world modeling → action 생성이라는 WAM 계열 공통 골격을 공유하나, ABot-M0.5 는 **self-dreamed latent 로 학습 조건 자체를 inference 와 일치**시키는 점이 구별됩니다(대부분 WAM 은 조건 표현의 *무엇*을 바꾸지, 조건의 *출처*를 inference 와 맞추지 않음).
- **핵심 델타 한 줄.** 기존 pinned WAM 이 "무엇을 예측하고 어떻게 조건화하느냐"에 집중했다면, ABot-M0.5 의 진짜 새 기여는 **"학습 조건의 출처를 배포 조건과 일치시킨다(Dream Forcing)"** 와 **"action space 내부의 이질성까지 분리한다(action-level MoT)"** 입니다.

---

## ⚙️ 의사결정 함의

이 논문이 맞다면 우리 파이프라인에서 다음이 바뀝니다.

- **train-test 조건 정렬을 명시적 학습 레버로 승격.** 우리가 P5 world-model auxiliary 를 co-train 할 때, GT 미래에만 조건화하지 말고 **2단계 커리큘럼**(Stage I clean 조건 → Stage II self-dreamed 조건)을 도입합니다. 구체 config: `wm_condition_source: {stage1: "gt_latent", stage2: "self_dreamed"}`, 전환 trigger 는 "초기 수렴 후". ablation 근거는 동일 예산에서 teacher forcing +5k(66.78%) < Dream Forcing +5k(70.56%).
- **action head 를 subspace 로 분리할 때 "attention 공유 + FFN/head 분리" 원칙 채택.** 우리의 Body/Hand split(P1 D1/D5) 을 구현할 때, 완전 분리 대신 **shared joint attention + branch-specific FFN·prediction head + 공유 denoising timestep** 을 기본형으로 둡니다. config: `action_expert: {attn: "shared_joint", ffn: "per_subspace", denoise_timestep: "shared"}`. cross-subspace 협응을 위해 각 branch 가 상대 branch 의 noisy action 을 입력으로 받게 합니다.
- **conditioning dropout 제거.** cascade inference 에서 상류 조건이 항상 존재한다면 `p_drop=0` 이 정답(94.0 vs 91.06). 우리 latent-conditioned action head 도 학습 시 상류 조건 dropout 을 끄는 것을 기본값으로 검토합니다.
- **latent action 을 action-free 비디오 사전학습의 supervision 으로 활용.** P4 corpus 에서 로봇 라벨 없는 egocentric 비디오를 **frame-level latent action** supervision 으로 흡수하는 경로(ALAM-식 additive/reversal 제약)를 P4 D22 open ablation 후보에 추가합니다.
- **평가 프로토콜.** RoboCasa365 의 atomic/composite × seen/unseen 4범주 분해와 "process score" 를 우리 장기 지평 평가에 도입해, 성공률 하나로 뭉개지 않고 **조합 일반화(unseen)** 를 독립 축으로 측정합니다.

---

## ⚠️ 먼저 검증할 실패 모드

가장 싼 확인부터:

1. **(가장 쌈) 도메인 불일치 sanity check.** 본 논문은 gripper·base 이동, 우리는 22-DOF Sharpa hand·촉각입니다. Dream Forcing·D-MoT 를 우리 스택에 붙이기 전에, 먼저 **"손가락 접촉 미세 동역학을 5B 생성 비디오 latent 이 담아내는가"** 를 소규모로 확인합니다 — 비디오 latent 이 fingertip 접촉 변화를 못 잡으면 intermediate latent action 도 빈 신호를 bridging 하게 됩니다.
2. **비용 vs 이득.** 매 chunk 두 번 forward(5B diffusion) 하는 학습·추론 비용이 우리 GPU 예산·제어 주파수(hand 은 고주파)에서 감당되는지. 우리 System0(P3)는 sub-policy-loop 반응 속도가 필요한데, 5B world model rollout 은 그 주파수와 상극일 수 있습니다 — world model 은 System1 상위에만 두는 게 현실적인지 확인.
3. **시각 교란 증폭.** LIBERO-Plus Camera/Noise 에서 WAM 이 약한 것처럼, self-dreamed 조건화가 우리 다중 카메라·촉각 입력의 교란을 미래 예측 오차로 증폭할 위험. 촉각은 카메라 교란과 독립이므로, **촉각 채널을 world model 조건에서 분리**해 교란 전파를 끊는 변형이 필요한지 조기 검증.
4. **조합 일반화 부재.** Composite-Unseen 2.7% 는 우리 flagship(cross-object generalization, phase 3)의 요구와 정면 충돌합니다. world model 이 태스크 **조합** 일반화를 주지 못한다면, P5 를 일반화 레버가 아니라 **저데이터 적응·강건성 레버**로만 포지셔닝해야 합니다.
5. **latent action 인코더 이식성.** ALAM 인코더가 로봇/egocentric 도메인 격차를 넘어 우리 손-물체 접촉 motion 을 구조화된 latent 로 뽑는지. frozen 인코더가 병목이면 bridging space 전체가 무너집니다.

---

## 💡 컨텍스트 제안

- **P5 D29(integration architecture) 재검토 후보.** 현재 v1 은 "auxiliary head"(Being-H0.7)를 기본, "unified autoregressive VLA+WM"(WorldVLA)을 대안으로 둡니다. ABot-M0.5 는 unified 노선이 attention 간섭을 **비대칭 마스크 + D-MoT + structured FlashAttention** 으로 관리 가능함을 실증하므로, unified 대안의 위험 평가를 갱신하고 **Dream Forcing 을 unified 노선의 필수 부속**으로 기록할지 사람이 판단할 것을 제안합니다.
- **P5 Tracked Literature 편입 후보(하드 캡 8 주의).** ABot-M0.5 는 WAM 계열 SOTA 이자 "train-test 조건 정렬" 이라는 새 축을 여는 논문입니다. World Guidance / Ctrl-World 대비 우선순위를 재고하되, **hand-object·egocentric(D32) 부합도가 낮다는 점**을 role 설명에 명시해 편입(비-pinned methodology base 로 두는 것이 현실적)하는 것을 제안합니다.
- **P1 D5 근거 보강.** base(저주파)/arm(고주파) control-rate 분리의 이점(gradient 간섭 감소, 0.48 vs 0.34)이 우리 Body/Hand 분리 논거를 뒷받침하는 외부 증거로 인용 가능함을 기록.
- 그 외 Decision 이동/핀 교체는 사람 판단 영역 — 본 분석은 제안에 그칩니다(context 파일 수정 없음).

> 💡 base 매핑은 `/implement-design analysis/2607.00678/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
