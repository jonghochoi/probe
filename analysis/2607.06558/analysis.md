# Paper Analysis — RynnWorld-Teleop: An Action-Conditioned World Model for Digital Teleoperation

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | RynnWorld-Teleop: An Action-Conditioned World Model for Digital Teleoperation |
| 저자 | Haoyu Zhao, Xingyue Zhao, Hangyu Li, Biao Gong, Kehan Li, Siteng Huang, Xin Li, Deli Zhao, Zhongyu Li (DAMO Academy Alibaba Group · Hong Kong Embodied AI Lab · CUHK · Hupan Lab · Ant Group) |
| 링크 | [arXiv:2607.06558](https://arxiv.org/abs/2607.06558) · [GitHub](https://github.com/alibaba-damo-academy/RynnWorld-Teleop) · [HuggingFace](https://huggingface.co/Alibaba-DAMO-Academy/RynnWorld-Teleop) · [Website](https://alibaba-damo-academy.github.io/RynnWorld-Teleop.github.io) |
| 발행일 / 버전 | 2026-07-07 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-07-10 |
| 관련 Pillar | P5, P0 |
| 태그 | egocentric-data, dexterity, sim2real |

---

## 🧭 한 줄 요약 (TL;DR)

실물 로봇 없이 조작자의 손 포즈 스트림만으로 로봇 시점(egocentric) 실행 영상을 실시간(40+ FPS)으로 생성하는 robot-centric·action-conditioned world model 을 만들고, 이를 "digital teleoperation" 데이터 엔진으로 승격시킨 논문입니다. 생성 데이터만으로 학습한 정책의 zero-shot 실로봇 이전과, 실데이터 1:1 증강 시 일관된 성공률 상승(정밀 과제 최대 +20%p)을 실로봇에서 실증합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 로봇 학습 데이터 수집이 물리 teleoperation 에 묶여 조작자 시간 × 하드웨어 가용성으로 상한이 걸립니다. 시연 하나하나가 실로봇과 고정 작업 공간을 점유하고, 환경 리셋·물체 조달 비용 때문에 long-tail 상호작용 분포를 덮지 못합니다.
- **기존 접근의 한계 (human-to-robot 영상 변환)** — Phantom / Masquerade / Mitty 류는 사람 시연 영상에 로봇 embodiment 를 렌더링해 시각 갭은 건너지만, 본질적으로 passive·observation-only 입니다. 로봇 액션이 생성되지 않고, 무거운 DiT 백본이 closed-loop 상호작용을 막습니다.
- **기존 접근의 한계 (action-conditioned egocentric world model)** — Hand2World / GeneratedReality 류는 액션 조건 생성까지 나아갔지만 human-centric 에 머뭅니다. 렌더되는 손이 여전히 사람 손이라 embodiment 갭이 해소되지 않습니다.
- **본 논문의 가설** — robot-centric · action-grounded · real-time 세 요건을 동시에 만족하는 생성 world model 이 있으면, 실로봇을 생성 모델로 대체한 "digital teleoperation" 으로도 imitation learning 이 그대로 소비할 수 있는 (RGB 관측, 로봇 액션) 궤적을 얻을 수 있습니다.
- **왜 지금 중요한가** — VLA 와 world model 의 성능 상한이 데이터 규모에 걸려 있는 시점이고, 손 포즈는 retargeting 만으로 임의 embodiment 에 이전되는 embodiment-agnostic 액션 라벨입니다. 데이터 수집의 상한을 물리 인프라에서 "조작자의 상상력"으로 옮길 수 있다는 것이 저자들의 주장입니다.

---

## 🧩 핵심 기여

- **패러다임 공식화** — digital teleoperation 을 로봇 데이터 생성의 새 패러다임으로 정의하고, 실용적 인스턴스가 만족해야 할 3 요건(robot-centric / action-grounded / real-time)을 식별했습니다.
- **모델** — 3 요건을 모두 만족하는 action-conditioned egocentric world model: depth-aware skeletal representation + progressive human-to-robot training + streaming autoregressive distillation 을 결합해 단일 H100 에서 40+ FPS 인터랙티브 생성을 달성합니다.
- **시스템** — 단일 reference 이미지로 임의 조작 장면을 인스턴스화하고, retargeting → skeletal-conditioned synthesis → chunked re-anchoring 으로 완결된 (영상, 액션) 궤적을 무한정 생성하는 데이터 엔진으로 확장했습니다.
- **정책-레벨 실증** — 생성 데이터만으로 학습한 정책의 zero-shot 실로봇 이전, 그리고 실데이터 증강 시 DP · $`\pi_{0}`$ · $`\pi_{0.5}`$ 전반의 일관된 성공률 향상을 보여, digital teleoperation 이 물리 teleoperation 을 대체·증폭할 수 있다는 첫 실증 근거를 제시합니다.

---

## 🔑 기술 키워드

- **Digital Teleoperation** — 실로봇 대신 생성 world model 을 "조종"해 데이터를 모으는 패러다임. 비행 시뮬레이터로 조종 기록을 쌓되, 그 기록이 실기체 훈련 데이터로 쓰이는 것에 비유할 수 있습니다.
- **Action-Conditioned World Model** — 액션 신호(여기서는 손 포즈 시퀀스)를 조건으로 다음 프레임들을 예측·생성하는 환경 동역학 모델. 본 논문에서는 raw-pixel 영상 생성형입니다.
- **Depth-Aware Skeletal Conditioning** — 21-관절 손 스켈레톤을 카메라 거리로 색·굵기를 변조해 렌더링한 2D 영상 조건. 2D 투영이 잃는 깊이 정보를 색/크기 단서로 되살립니다.
- **Autoregressive Distillation** — bidirectional teacher 를 프레임 단위 causal student 로 증류해 스트리밍 생성을 가능케 하는 절차. causal flow-matching warm-up → DMD 2단계입니다.
- **Conditional Flow Matching (CFM)** — 플로우 매칭 기반 학습 목표: 노이즈→데이터 확률 경로의 속도장을 회귀합니다. 본 논문 DiT 의 기본 학습 목표입니다.
- **Distribution-Aligned Additive Conditioning** — 제어 latent 를 video latent 의 평균·표준편차에 정렬한 뒤 zero-init patch embedding + 게이트 스칼라로 더하는 주입 방식. 사전학습 prior 를 깨지 않고 새 조건을 넣는 장치입니다.
- **Distribution Matching Distillation (DMD)** — critic 과 frozen teacher 의 score 지도로 student 출력 분포를 teacher 분포에 맞추는 few-step 증류. 4-step 샘플링으로 teacher 화질을 회복합니다.
- **Chunked Re-anchoring** — 81-프레임 chunk 마다 실측 egocentric 프레임을 새 reference 로 재앵커해 장호라이즌 생성의 드리프트를 억제하는 전략입니다.
- **Damped Least-Squares IK** — Vive 트래커 포즈를 로봇 관절로 옮기는 감쇠 최소제곱 역기구학. 특이점 근처에서 감쇠를 키우고 null-space 어깨 prior 로 자연스러운 팔 자세를 유도합니다.
- **Sink Token** — 자기회귀 롤아웃 내내 reference 이미지 임베딩을 KV cache 에 상주시키는 앵커 토큰. 초기 장면의 identity·공간 맥락을 보존합니다.

---

## 🔬 방법론

### 직관

이 논문의 출발점은 "로봇 데이터에서 정말 비싼 것은 로봇 그 자체"라는 관찰입니다. teleoperation 시연 한 편이 만들어내는 것은 결국 (로봇 시점 영상, 로봇 액션) 쌍인데, 액션 쪽은 이미 조작자의 손 포즈에서 retargeting 으로 얻어지고 있습니다. 그렇다면 남는 것은 영상뿐이고, 영상을 충분히 정확하게 "상상"해 주는 생성 모델이 있다면 실로봇은 루프에서 빠져도 됩니다. 조작자는 화면 속 가상 로봇을 조종하고, 그 손 포즈 기록이 액션 라벨, 생성 영상이 관측이 되는 구조입니다.

이를 위해 모델은 세 가지 문제를 순서대로 풉니다. 첫째, 손 포즈라는 3D 액션을 2D 영상 생성 파이프라인이 소화할 수 있는 조건으로 바꿔야 합니다. 저자들은 스켈레톤을 그냥 투영하는 대신 깊이에 따라 색과 굵기를 바꿔 그려, 2D 조건 안에 3D 단서를 심습니다. 둘째, 로봇 데이터는 1,800 에피소드뿐이므로 손-물체 상호작용의 물리 상식은 대규모 사람 egocentric 영상에서 먼저 배우고, 로봇 도메인에는 나중에 적응시킵니다. 사람 손이든 로봇 손이든 조건은 동일한 (2D 스켈레톤, RGB) 계약으로 통일되어 있어 이 이전이 성립합니다. 셋째, 조작자가 루프 안에 있으려면 생성이 실시간이어야 하므로, 양방향 attention 의 teacher 를 인과(causal) student 로 증류해 4-step 샘플링·40+ FPS 스트리밍 생성으로 압축합니다.

마지막으로 모델 바깥의 시스템이 이를 데이터 엔진으로 완성합니다. 트래커 포즈는 감쇠 최소제곱 IK 로 54-차원 로봇 액션으로 retarget 되고, 긴 시연은 81-프레임 chunk 로 잘라 chunk 마다 실측 프레임으로 재앵커해 드리프트를 막습니다. 그 결과물이 imitation learning 파이프라인에 그대로 들어가는 완결된 궤적입니다.

### 아키텍처

전체 구조는 Wan-I2V 계열 video Diffusion Transformer 위에 조건 분기를 더한 형태입니다.

![Figure 3 — RynnWorld-Teleop 개요](https://arxiv.org/html/2607.06558/x5.png)

> "Figure 3: Overview of RynnWorld-Teleop. (a) Actions are rendered as depth-aware skeletal videos and encoded into the latent space via a VAE. (b) We expand a pretrained video DiT to incorporate hand-pose conditioning using a distribution-aligned patch embedding branch. (c) The model is distilled into a causal student for interactive, autoregressive generation using a streaming rollout schedule." (§3)
(한글 해설 — 액션 렌더링 → VAE 인코딩 → 분포-정렬 patch embedding 주입 → causal 증류로 이어지는 본 논문의 3단 파이프라인 전체를 시각화한 그림입니다.)

- **베이스 모델** — Wan-I2V 아키텍처(3D VAE + Transformer denoiser $`\mathcal{F}_{\Theta}`$ ), 구체적으로 Wan2.2-TI2V-5B 를 사용합니다. reference 이미지 latent $`z_{ref}=\mathcal{E}(I_{ref})`$ 와 제어 latent $`c`$ 를 조건으로 속도장을 예측하는 image-to-video 패러다임입니다.
- **액션 표현 (depth-aware skeletal video)** — 21-관절 손 트래킹에서 유도한 스켈레톤 영상 시퀀스가 액션입니다. 각 관절·본(bone)의 색과 지름을 카메라-공간 깊이에 따라 동적으로 스케일링해 렌더링합니다.

![Figure 2 — Depth-Aware 표현](https://arxiv.org/html/2607.06558/x4.png)

> "Figure 2: Depth-Aware Representation. We bridge the gap between 2D projections and 3D dynamics by rendering hand skeletons with depth-modulated color and size." (§1)
(한글 해설 — 동일한 2D 투영이라도 깊이가 다르면 색·굵기가 달라지도록 렌더링해, 2D 조건 신호에 3D 단서를 임베드하는 핵심 표현을 보여줍니다.)

> "To resolve the inherent depth ambiguity in standard 2D projections—which is critical for modeling precise hand-object interactions—we employ a depth-modulated rendering technique." (§3.2)
(한글 해설 — 정밀한 손-물체 상호작용에는 깊이 정보가 필수인데, 표준 2D 투영은 이를 잃습니다. 3D 좌표를 직접 조건화하는 대신 렌더링 단계에서 깊이를 색·크기로 인코딩해, video VAE 가 그대로 소화할 수 있는 2D latent 조건으로 만드는 것이 이 설계의 요점입니다.)

- **조건 인코딩** — 렌더링된 포즈 영상은 사전학습 VAE 인코더로 latent 공간에 투영되어, 타깃 video latent 와 공간·시간적으로 정렬된 제어 latent $`c\in\mathbb{R}^{C\times T\times H\times W}`$ 가 됩니다.
- **조건 주입 (distribution-aligned additive patch embedding)** — 기존 video embedding 층과 병렬로 전용 제어 patch-embedding 층을 두고, 학습 가능한 스칼라 게이트 $`\alpha`$ 로 융합합니다 (식 3):

$$x=\mathrm{PatchEmbed}^{z}_{C\rightarrow D}(z_{t})\;+\;\alpha\cdot\mathrm{PatchEmbed}^{c}_{C\rightarrow D}\!\left(\widetilde{c}\right),\quad\widetilde{c}=\frac{c-\mu_{c}}{\sigma_{c}}\cdot\sigma_{z}+\mu_{z}$$

여기서 $`z_{t}\in\mathbb{R}^{C\times T\times H\times W}`$ 는 노이즈 낀 video latent, $`\widetilde{c}`$ 는 정렬된 제어 latent 입니다. 두 모달리티의 통계가 다르므로 그대로 더하면 사전학습 스트림이 흔들립니다.

> "We maintain running estimates of the mean and standard deviation $`(\mu,\sigma)`$ for both signals and align $`c`$ to the video latent distribution before patchification." (§3.3)
(한글 해설 — 두 신호 각각의 평균·표준편차를 running 추정으로 유지하고, patch 화 이전에 제어 latent 를 video latent 분포로 정규화-재스케일합니다. additive 조건이 학습 내내 사전학습 스트림과 통계적으로 호환되도록 만드는 장치입니다.)

> "To preserve the generative prior, $`\mathrm{PatchEmbed}^{c}`$ is zero-initialized and the gating scalar $`\alpha`$ is initialized to a small value (e.g., $`0.1`$ ), allowing the network to gradually incorporate the pose signal without destabilizing the pretrained weights." (§3.3)
(한글 해설 — 제어 분기를 zero-init 하고 게이트를 0.1 로 시작하면 학습 초기의 모델은 사전학습 모델과 사실상 동일하게 동작하고, 포즈 신호는 점진적으로만 흘러들어 갑니다. ControlNet 류의 zero-init 사상을 patch embedding 수준의 초경량 분기로 구현한 셈입니다.)

### 학습 목표 / 손실

기본 학습 목표는 conditional flow matching 입니다. 초기 이미지 latent $`z_{0}=\mathcal{E}(I_{V})`$ 에 대해 데이터-노이즈 확률 경로를 구성하고 (식 1):

$$z_{t}=(1-t)z_{0}+t\epsilon,\quad\epsilon\sim\mathcal{N}(0,\mathbf{I})$$

$`t\in[0,1]`$ 에서 네트워크 $`v_{\Theta}`$ 가 reference latent $`z_{ref}`$ 와 제어 latent $`c`$ 를 조건으로 속도장을 회귀합니다 (식 2):

$$\mathcal{L}_{\text{CFM}}=\mathbb{E}_{t,z_{0},\epsilon}\left[\left\|v_{\Theta}(z_{t},t,z_{ref},c)-(\epsilon-z_{0})\right\|_{2}^{2}\right]$$

추론 시에는 $`v_{\Theta}`$ 가 정의하는 ODE 를 풀되, 실시간 응답을 위해 증류된 causal student 를 사용합니다.

### 자기회귀 증류 (실시간화)

인터랙티브 closed-loop 사용을 위해 bidirectional teacher 를 프레임-레벨 자기회귀 causal student 로 증류합니다. 절차는 causal flow-matching warm-up → adversarial distribution matching 의 2단계입니다.

- **Causal streaming 구조** — student 는 causal temporal mask 와 고정 크기 KV cache(사전 할당 버퍼 + in-place 쓰기)를 사용하고, 시점 $`t`$ 의 attention 은 $`\{1,\dots,t\}`$ 로 제한됩니다.

> "To maintain long-term consistency during autoregressive rollouts, we retain the embedding of $`I_{ref}`$ as a persistent sink token and append all subsequently generated KV states to the cache." (§3.5)
(한글 해설 — reference 이미지 임베딩을 sink 토큰으로 cache 에 상주시켜, 롤아웃이 길어져도 초기 장면의 identity 와 공간 맥락이 유지되도록 하는 설계입니다.)

**Causal flow-matching warm-up** — bidirectional↔causal 처리 간극을 잇기 위해 프레임-인과적 방식으로 속도장 $`\mathbf{v}_{\theta}`$ 를 회귀합니다 (식 4):

$$\mathcal{L}_{\text{MSE}}=\mathbb{E}_{t,\boldsymbol{\epsilon}}\left[\left\|\mathbf{v}_{\theta}(\mathbf{x}_{t},t)-(\boldsymbol{\epsilon}-\mathbf{x}_{0})\right\|^{2}\right]$$

이 단계가 스트리밍 생성·제어 추종 능력을 세우고, 샘플링 가속을 위한 안정적 초기화를 제공합니다.

**Distribution Matching Distillation (DMD)** — 4-step 만으로 고화질 합성을 얻기 위해 학습된 critic 과 frozen teacher 의 score 기반 gradient 지도를 사용합니다. 이 단계에서 student 는 4-step 샘플링 롤아웃을 수행합니다.

> "Crucially, we backpropagate gradients through the persisted KV cache across successive chunks." (§3.5)
(한글 해설 — chunk 경계를 넘어 KV cache 를 통해 gradient 를 흘려보내는 것이 핵심입니다. chunk 전환부의 경계 아티팩트를 최소화하도록 학습 신호가 직접 걸려, 실시간 루프에서도 teacher 급 화질과 매끄러운 시간 연속성이 유지됩니다.)

### 학습 셋업

학습은 2-stage progressive cross-domain 패러다임입니다. 두 stage 의 데이터는 모두 (2D Skeleton, RGB) 쌍으로 통일됩니다 (Table 1).

| Dataset | Type | Seq. Length | Total Frames | Total Slices |
|---|---|---|---|---|
| VITRA (Stage 1) | Human | 25 | 30.7M | 1.23M |
| EgoDex (Stage 1) | Human | 81 | 74.0M | 0.91M |
| Ours, Real-Robot (Stage 2) | Robot | 81 | 0.43M | 5.3K |

- **Stage 1 (Egocentric Human Pretraining)** — EgoDex 는 81-프레임 클립으로 분절하고 3D SE(3) 손 포즈를 카메라 프레임으로 변환·2D 투영해 양손+전완 스켈레톤 영상을 렌더링합니다. VITRA 는 25-프레임 세그먼트에 제공된 21-관절 MediaPipe 액션 주석을 각 클립 첫 프레임의 카메라 내참수·포즈로 투영합니다. DiT 가 손-물체 상호작용의 기본 동역학과 스켈레톤→시각 합성 매핑을 학습하는 단계입니다.
- **Stage 2 (Robotic Domain Adaptation)** — 사람 제스처가 IK 로 로봇 액션에 매핑된 paired teleoperation 데이터로 미세조정합니다.

> "We fine-tune the model on paired teleoperation data, where human gestures are mapped to robotic actions via Inverse Kinematics (IK)." (§3.4)
(한글 해설 — Stage 2 의 페어링이 이 모델을 "사람 의도가 로봇 실행 영상을 구동하는" robot-centric world model 로 바꿉니다. MoCap 으로 조작자 손 움직임을 기록해 동기화된 2D 스켈레톤을 얻고, 모든 로봇 궤적을 사전학습과 동일한 81-프레임 클립으로 분절해 시간 일관성을 유지합니다.)

Stage 2 용으로 4개 bimanual 과제, 총 1,800 에피소드의 실로봇 데이터를 수집했습니다 (Table 2): Dual Picking 500 / Block Pushing 500 / Bimanual Lifting 500 / Lid Placement 300.

세부 학습 설정 (§5.1):

- **TI2V warm-up** — 액션 조건 없이 대상 환경의 시각 특성에 적응: 전체 모델 2,000 steps, lr $`2\times 10^{-5}`$ , NVIDIA H100 64장.
- **액션 조건 학습** — LoRA(rank 64, patch embedding 층 + LoRA 가중치 최적화)와 full-parameter SFT(EMA decay $`0.999`$ , 200-step warmup) 두 패러다임 모두 탐구. Stage 1 lr $`2\times 10^{-5}`$ , Stage 2 lr $`1\times 10^{-5}`$ .
- **증류** — causal warm-up lr $`1\times 10^{-5}`$ ; DMD 생성기 lr $`2\times 10^{-6}`$ , critic lr $`5\times 10^{-7}`$ .

### 데이터 생성 파이프라인 (시스템 레이어)

모델을 데이터 엔진으로 완성하는 세 구성요소입니다 (§4.1, 부록 §8).

**Retargeting** — 가슴·양 손목·양 상완에 착용한 Vive 트래커의 6-DoF 포즈에서 좌표 변환 체인으로 목표 end-effector 포즈를 계산합니다 (식 5):

$$\mathbf{T}_{\text{target}}=\mathbf{T}_{\text{base}}\cdot\text{Scale}(\mathbf{T}_{\text{chest}}^{-1}\cdot\mathbf{T}_{\text{wrist}})\cdot\mathbf{T}_{\text{ee}}$$

$`\text{Scale}(\cdot)`$ 은 병진 성분만 배율 $`s`$ (예: $`s=1.5`$ )로 스케일링해 조작자 작업 공간을 로봇 작업 공간에 매핑합니다. 관절 구성은 반복 damped least-squares IK 로 풉니다 (식 6, 7):

$$\Delta\mathbf{q}=\mathbf{J}^{\#}_{\lambda}\,\mathbf{e}$$

$$\mathbf{J}=\mathbf{U}\boldsymbol{\Sigma}\mathbf{V}^{\top},\quad\mathbf{J}^{\#}_{\lambda}=\mathbf{V}\,\text{diag}\!\left(\frac{\sigma_{i}}{\sigma_{i}^{2}+\lambda^{2}}\right)\mathbf{U}^{\top}$$

감쇠 인자는 특이점 근처에서 커지는 적응형 $`\lambda=\lambda_{\min}+\frac{0.01}{1+\sigma_{\max}}`$ 입니다. 상완 트래커에서 유도한 어깨 참조값 $`\mathbf{q}_{\text{shoulder}}^{\text{ref}}`$ 는 null-space 과제로 주입됩니다 (식 8, 어깨 관절 가중치 $`w=0.5`$ ):

$$\Delta\mathbf{q}\leftarrow\Delta\mathbf{q}+(\mathbf{I}-\mathbf{J}^{\#}_{\lambda}\mathbf{J})\,w\,(\mathbf{q}^{\text{ref}}-\mathbf{q})$$

> "This yields, for every operator gesture, a synchronized 54-dimensional robot action vector (dual 7-DoF arms + dual 20-DoF dexterous hands) that is exactly aligned with the hand-pose stream driving RynnWorld-Teleop." (§4.1)
(한글 해설 — 모든 제스처가 양팔 7-DoF + 양손 20-DoF 의 54-차원 절대 관절 위치 벡터로 변환되고, world model 을 구동하는 포즈 스트림과 프레임 단위로 정확히 정렬됩니다. 이 정렬이 (관측, 액션) 쌍의 무결성을 보장합니다.)

**Skeletal-conditioned synthesis** — 각 원본 시연의 첫 RGB 프레임을 $`I_{ref}`$ 로 추출하고, 손 포즈 스트림을 16 FPS 의 depth-aware 스켈레톤 시퀀스 $`S_{1:T}`$ 로 렌더링해 로봇 실행 영상을 합성합니다. $`I_{ref}`$ 는 장면의 유일한 시각 명세이므로 사용자가 제공하거나 이미지 편집으로 합성해 학습 분포 밖 장면도 인스턴스화할 수 있습니다.

**Chunked re-anchoring** — 순수 자기회귀 장호라이즌 생성은 시각 드리프트와 물리 불일치를 누적하므로, 81-프레임 chunk 단위로 생성합니다.

> "For each subsequent chunk, we re-anchor the generation by providing the actual egocentric frame from the robot’s camera at that specific timestep as the new $`I_{ref}`$ ." (§4.1)
(한글 해설 — 첫 chunk 는 시연의 실제 시작 프레임으로 초기화하고, 이후 chunk 는 해당 시점 로봇 카메라의 실측 프레임으로 재앵커합니다. 물체 포즈·조명 같은 합성 환경이 ground-truth 액션 시퀀스와 어긋나지 않도록 주기적으로 접지하는 전략인데, 뒤집어 말하면 합성 궤적이 원본 실측 시연의 프레임에 주기적으로 의존한다는 뜻이기도 합니다 (⚖️ 한계 참조).)

전통 물리 시뮬레이터 대비 저자들이 내세우는 데이터-엔진 이점은 세 가지입니다 (§4.2): 3D 에셋·URDF 제작 오버헤드 제로(단일 이미지로 환경 암시 인스턴스화), 시각 도메인 갭 없음(실세계 픽셀 분포에서 직접 합성), 수동 System Identification 불필요(대규모 사람 영상에서 흡수한 암시적 물리 상식).

---

## 📊 실험 설정과 결과

### 실험 셋업

- **실로봇 플랫폼** — TIANJI M6 모바일 로봇 + 양팔(7-DoF ×2) + WUJI 덱스터러스 핸드(20-DoF ×2), egocentric RealSense D435i. 정책 추론 50 Hz, 저수준 인터페이스 500 Hz (부록 §7).
- **과제 4종** — Dual Picking(양팔 순차 과일 집기), Block Pushing(좌→중앙→우 순차 밀기), Bimanual Lifting(양팔 동기 리프팅), Lid Placement(정밀 정렬). 초기 상태에 6-DoF 물체 포즈 랜덤화를 적용하고, 과제당 35회 연속 실측 시행, 120초 내 목표 도달 시 성공으로 채점합니다.
- **생성 평가 벤치마크 2종** — EgoDex-Test(공식 테스트셋에서 81-프레임 × 50 시퀀스, human-centric 도메인·ablation 용)와 Robotic-Test(자체 수집 teleop 데이터 중 학습 미사용 20 시퀀스, 4개 과제 전 범주). 지표는 PSNR / SSIM / LPIPS / FVD(표준 I3D 백본, 81-프레임 롤아웃) + 단일 H100 기준 FPS 입니다.

### 정책 학습 결과 (Table 3)

| Method | Data Source | Dual Picking | Block Pushing | Bimanual Lifting | Lid Placement |
|---|---|---|---|---|---|
| DP | 300 Real | 82.86 | 85.71 | 88.57 | 57.14 |
| DP | 300 Real + 300 RynnWorld-Teleop | 88.57 | 88.57 | 94.29 | 65.71 |
| $`\pi_{0.5}`$ | 300 Real | 94.29 | 100.00 | 94.29 | 42.86 |
| $`\pi_{0.5}`$ | 300 Real + 300 RynnWorld-Teleop | 97.14 | 97.14 | 100.00 | 62.86 |
| $`\pi_{0}`$ | 300 Real | 88.57 | 94.29 | 91.43 | 34.29 |
| $`\pi_{0}`$ | 0 Real + 300 RynnWorld-Teleop | 68.57 | 82.86 | 77.14 | 28.57 |
| $`\pi_{0}`$ | 300 Real + 300 RynnWorld-Teleop | 94.29 | 100.00 | 97.14 | 54.29 |

> "The improvement is most pronounced in high-precision tasks like Lid Placement, where the success rate of $`\pi_{0.5}`$ increases from 42.86% to 62.86% (+20%) and $`\pi_{0}`$ from 34.29% to 54.29% (+20%)." (§5.2, Table 3)
(한글 해설 — 실데이터 300 에 합성 300 을 1:1 로 더했을 때 거의 모든 (정책, 과제) 조합에서 성공률이 오르고, 특히 실데이터가 가장 부족함을 드러내는 고정밀 과제(Lid Placement)에서 +20%p 로 이득이 가장 큽니다. $`\pi_{0.5}`$ 의 Block Pushing 처럼 이미 100.00 인 셀은 97.14 로 소폭 내려가는 예외도 있습니다.)

> "Notably, $`\pi_{0}`$ trained solely on 300 RynnWorld-Teleop-generated episodes (without any real data) achieves a competitive success rate of 82.86% in Block Pushing and 77.14% in Bimanual Lifting." (§5.2, Table 3)
(한글 해설 — 실데이터 0 으로 합성 데이터만 학습해도 zero-shot 실로봇 이전이 동작한다는 것이 이 논문의 가장 강한 주장입니다. 다만 같은 표에서 300 Real 단독(88.57 / 94.29 / 91.43 / 34.29) 대비로는 전 과제에서 뒤지므로, 현 상태의 합성 데이터는 대체재라기보다 증강재입니다.)

**Feature 분포 분석** — 실측 궤적과 생성 궤적에서 각 1,000 프레임을 샘플링해 사전학습 I3D 특징을 t-SNE 로 시각화한 결과, 두 분포가 크게 겹칩니다 (Fig. 5). 저자들은 이 특징-레벨 정합이 zero-shot 이전 성능의 설명이라고 해석합니다.

**지연 분석** — 증류된 causal student 는 4-step flow matching 스케줄로 동작합니다.

> "Our distilled causal student model, optimized with a 4-step flow matching schedule, achieves a high throughput of 40.0 fps at $`480\times 832`$ resolution." (§5.2)
(한글 해설 — 프레임당 평균 약 25 ms: Skeletal Action Encoding ~5%, Causal DiT Denoising ~72% (sliding-window KV cache 활용 4-step 추론), Visual Decoding ~23% 구성입니다. 기존 action-conditioned world model 의 2–10 Hz 를 크게 상회하고 실로봇 카메라 표준 30 Hz 를 넘어서므로, 조작자가 루프 안에 머무는 real-time 요건이 충족됩니다.)

### World model 생성 품질 (Table 4)

평가는 EgoDex-Test(text-/action-conditioned 비교군, ablation)와 Robotic-Test(robot-specific)로 나뉩니다.

| Method | PSNR ↑ | SSIM ↑ | LPIPS ↓ | FVD ↓ | FPS ↑ |
|---|---|---|---|---|---|
| CogVideoX-1.5-I2V-5B | 18.22 | 0.786 | 0.322 | 2790 | 0.8 |
| Wan-2.2-TI2V-5B | 18.61 | 0.772 | 0.373 | 1998 | 2.8 |
| Wan-2.1-I2V-14B | 18.08 | 0.735 | 0.418 | 1540 | 0.3 |
| Wan-2.2-I2V-14B | 21.05 | 0.816 | 0.265 | 1337 | 0.3 |
| Wan-2.2-TI2V-5B (SFT) | 20.93 | 0.806 | 0.282 | 1223 | 2.8 |
| InterDyn | 21.47 | 0.831 | 0.279 | 655 | 2.9 |
| CosHand | 18.14 | 0.785 | 0.406 | 1527 | 0.8 |
| Mask2IV | 21.50 | 0.836 | 0.219 | 1650 | 0.9 |
| RynnWorld-Teleop (LoRA) | 26.08 | 0.876 | 0.151 | 585 | 2.8 |
| RynnWorld-Teleop (SFT) | 26.78 | 0.887 | 0.119 | 550 | 2.8 |
| RynnWorld-Teleop-Causal | 22.25 | 0.830 | 0.207 | 1226 | 40.0 |
| Concatenation Fusion (ablation) | 19.69 | 0.821 | 0.260 | 1191 | 2.8 |
| w/o Human Pre-training (ablation) | 17.81 | 0.763 | 0.453 | 2598 | 2.8 |
| w/o DMD, Causal (ablation) | 19.25 | 0.777 | 0.244 | 1338 | 40.0 |
| w/o Causal Warm-up, Causal (ablation) | 14.26 | 0.688 | 0.408 | 2150 | 40.0 |
| RynnWorld-Teleop (Robotic-Test) | 22.53 | 0.898 | 0.148 | 763 | 2.8 |
| RynnWorld-Teleop-Causal (Robotic-Test) | 18.66 | 0.743 | 0.249 | 1534 | 40.0 |

> "Notably, a vanilla SFT baseline that directly fine-tunes Wan-2.2-TI2V-5B on the same robotic and human datasets (denoted as SFT in Tab. 4) still trails RynnWorld-Teleop by a wide margin (FVD 1223 vs. 585; PSNR 20.93 vs. 26.08)." (§5.3, Table 4)
(한글 해설 — 동일 데이터로 베이스 모델을 그냥 SFT 한 것보다 depth-aware 포즈 표현 + 분포-정렬 조건화가 큰 격차로 앞선다는, "데이터가 아니라 조건화 설계가 기여"임을 분리해 보여주는 비교입니다. 사람-중심 마스크 조건 모델(CosHand, Mask2IV) 대비로도 robot embodiment 렌더링에서 우위를 주장합니다.)

### Ablation 별 해석

- **Addition vs. Concatenation (조건 융합)** — 제어 latent 를 노이즈 latent 에 이어붙이는 표준 concat 융합으로 바꾸면 FVD 585→1191 로 악화됩니다. concat 이 사전학습 latent 분포를 교란해 합성이 불안정해진다는 진단으로, 분포-정렬 additive 주입의 존재 이유를 격리합니다.

> "As shown in Tab. 4, Concat Fusion results in a significant performance drop, with FVD increasing from 585 to 1191." (§5.4, Table 4)
(한글 해설 — 이 ablation 이 "새 조건 모달리티를 사전학습 생성 모델에 넣을 때는 분포 정렬 + zero-init additive 가 concat 보다 낫다"는 본 논문의 가장 재사용 가능한 교훈을 뒷받침합니다.)

- **w/o Human Pre-training (2-stage 의 가치)** — 로봇 데이터만으로 직접 미세조정하면 성능이 붕괴합니다.

> "Quantitative results in Tab. 4 show a severe performance collapse (FVD 2598, LPIPS 0.453), as the limited robotic data is insufficient to teach the model complex hand-object physics from scratch." (§5.4, Table 4)
(한글 해설 — 1,800 에피소드 규모의 로봇 데이터로는 손-물체 물리를 밑바닥부터 못 배웁니다. 사람 egocentric 대규모 사전학습이 embodiment 갭을 잇는 상호작용 prior 를 공급한다는, 본 논문에서 P4/P0 관점으로 가장 중요한 ablation 입니다. 정성적으로는 고스팅·텍스처 붕괴와 함께 로봇 effector 와 대상 물체가 조작 중 소멸하는 object permanence 상실까지 관찰됩니다.)

![Figure 9 — 사전학습 효과](https://arxiv.org/html/2607.06558/x11.png)

> "Figure 9: Effect of Pretraining. Stage 1 pretraining provides a robust interaction prior. Without it, the model fails to maintain visual quality when fine-tuned on limited robotic data." (§5.4)
(한글 해설 — Stage 1 사람 영상 사전학습 유무에 따른 시각 품질 차이를 정성적으로 보여주는 ablation 그림입니다.)

- **순차 증류 커리큘럼** — flow-matching 만 한 causal 모델(w/o DMD)은 PSNR 22.25 vs 19.25 로 최종 모델에 뒤지고, causal warm-up 없이 DMD 를 직접 적용하면(w/o Causal Warm-up) 학습 불안정과 텍스처 붕괴가 발생합니다 (PSNR 14.26, FVD 2150 — Table 4 전 지표 최악).

> "This confirms that the first stage (Causal Warm-up) is essential for bridging the structural gap between bidirectional and causal processing" (§5.4)
(한글 해설 — warm-up 이 bidirectional↔causal 구조 간극을 먼저 메워야 DMD 가 teacher 의 손-물체 상호작용 prior 를 4-step 으로 안정적으로 물려받을 수 있다는, 증류 순서의 필요성을 격리한 ablation 입니다.)

### OOD 일반화

reference 이미지를 off-the-shelf 이미지 편집으로 바꿔 학습 분포 밖 장면을 인스턴스화하는, digital teleoperation 의 핵심 주장에 대한 검증입니다. 미학습 물체(나무 블록→빨간 구, 수박 인형→럭비공)와 미학습 배경(무늬 식탁보) 두 축 모두에서 시간 일관성과 액션 추종이 유지됨을 정성적으로 보입니다.

![Figure 7 — OOD 시각 상태 일반화](https://arxiv.org/html/2607.06558/x9.png)

> "Figure 7: Generalization to Out-of-Distribution (OOD) Visual States. RynnWorld-Teleop generalizes along two axes that are absent from training: (i) unseen objects (top two rows), where the manipulated item in the reference frame is replaced by a novel category or shape; and (ii) unseen backgrounds (bottom two rows), where the tabletop texture is swapped for an environment not seen during training. In all cases, the modified reference image is obtained via off-the-shelf image editing, without any real-world object or scene modification. RynnWorld-Teleop preserves high visual fidelity, temporal coherence, and physically plausible dynamics under both object-level and background-level shifts." (§5.3)
(한글 해설 — "단일 reference 이미지로 임의 장면을 인스턴스화한다"는 패러다임-레벨 주장의 근거 그림입니다. 다만 정량 지표 없이 정성 결과이며, 물체/배경 치환 축에 한정됩니다.)

---

## ⚖️ 한계

- **저자 명시 (1) — 복잡 물리 현상** — 미세한 액체 동역학이나 고변형 물체 조작에서 종종 실패합니다. depth-modulated 렌더링이 공간 동역학은 담지만, 픽셀 생성 모델의 "암시적 물리"는 학습 데이터에 없는 물리 영역에서 보장이 없다는 구조적 문제이며, 저자들도 해당 상호작용을 덮는 데이터 확충이 필요하다고 봅니다.
- **저자 명시 (2) — per-platform 미세조정** — embodiment 갭 해소가 로봇 플랫폼마다 별도 미세조정을 요구해 로봇 fleet 스케일링이 제한됩니다. "실로봇 불필요" 패러다임이 실은 플랫폼마다 paired 실로봇 데이터(본 논문 1,800 에피소드)를 선행 요구한다는 자기모순적 병목으로, 저자들은 로봇 kinematic descriptor 조건화 cross-embodiment foundation world model 을 향후 방향으로 제시합니다.

> "Second, bridging the embodiment gap currently requires per-platform fine-tuning, which limits the paradigm’s scalability across robot fleets." (§6)
(한글 해설 — 이 문장이 본 논문 파이프라인의 실질 비용 구조를 정직하게 요약합니다. 새 로봇마다 Stage 2 를 반복해야 합니다.)

- **추론된 갭 (1) — 합성의 범위가 시각에 한정** — 생성되는 것은 영상뿐이고 액션은 원본 teleop 세션에서 기록된 포즈의 retarget 입니다. 즉 현 실험의 합성 데이터는 "기존 시연의 시각 변주"에 가깝고, 진짜 새 행동 궤적을 상상으로 만드는 시나리오(라이브 digital teleoperation 수집)의 정책-레벨 효과는 아직 분리 검증되지 않았습니다.
- **추론된 갭 (2) — re-anchoring 의 실측 프레임 의존** — chunk 재앵커가 로봇 카메라의 실측 프레임을 요구하므로, 완전-합성 장호라이즌 롤아웃의 드리프트 내성은 미검증입니다. reference 편집 기반 OOD 장면에서는 재앵커할 실측 프레임 자체가 존재하지 않아 장호라이즌 생성 품질이 열릴 문제로 남습니다.
- **추론된 갭 (3) — causal student 의 robot 도메인 품질 저하** — Robotic-Test 에서 teacher PSNR 22.53 / FVD 763 이 causal 에서 18.66 / 1534 로 떨어집니다. 실시간성이 필요한 라이브 수집 모드일수록 화질이 나쁜 모델을 쓰게 되는 역설이며, 이 품질의 데이터로 학습한 정책 성능은 별도 보고되지 않습니다 (Table 3 의 데이터가 teacher / causal 어느 쪽 생성인지 본문에 명시가 없습니다).
- **추론된 갭 (4) — 평가 범위** — 실로봇 검증이 단일 랩 환경·4개 과제·과제당 35 시행에 한정되고, 접촉 정밀도의 상한을 시험하는 in-hand 재배향류 과제는 없습니다. t-SNE(I3D 특징) 겹침은 분포 정합의 거친 지표일 뿐 접촉 물리의 정확성을 보장하지 않습니다.

---

## ♻️ 재현성

- **코드 / 가중치** — GitHub 공개 + HuggingFace 모델 공개(Apache-2.0, base `Wan-AI/Wan2.2-TI2V-5B-Diffusers` 명시) + ModelScope 미러. 프로젝트 페이지 별도 운영.
- **데이터** — Stage 1 은 공개 코퍼스(VITRA, EgoDex). Stage 2 의 자체 수집 1,800 에피소드 실로봇 데이터는 공개 여부가 본문에 명시되지 않았습니다.
- **하드웨어** — 학습 NVIDIA H100 64장, 추론 단일 H100 (40 FPS). 실로봇은 TIANJI M6 + WUJI Hand(총 54-DoF), HTC Vive 트래커 5개 + Manus 데이터 글러브, Pinocchio IK + Ruckig 스무딩 스택이 부록 §7–8 에 상세히 기록되어 있습니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P5(World Model) — 주 pillar.** 본 논문은 P5 스코프의 정중앙인 action-conditioned egocentric world model 이되, 역할이 정책 co-training prior 가 아니라 **데이터 엔진**입니다.
  - **D28(world-model role)** — v1 은 "latent dynamics prior + future-prediction auxiliary" 이고 data-augmentation(rollout synthesis)은 *tracked* 상태입니다. 본 논문은 그 tracked 역할에 대해 실로봇 정책-레벨 증거(DP · $`\pi_{0}`$ · $`\pi_{0.5}`$ 전반 향상, zero-real 이전)를 제시하는 현재까지 가장 강한 데이터포인트입니다.
  - **D30(prediction space)** — v1 latent/3D-flow 와 정면 긴장하는 raw-pixel 생성이지만, D30 이 raw-pixel 을 deferred-but-tracked 로 남긴 이유(eval-in-imagination 등 현실감이 필수인 역할)와 정합합니다. IL 정책이 픽셀 관측을 소비하는 한 데이터-엔진 역할에는 픽셀 생성이 필수라는 역할-공간 분리를 명확히 해 줍니다. co-training prior 로서의 D30 v1 을 흔들 증거는 아닙니다.
  - **D31(action conditioning)** — 프레임-정렬 per-frame 액션(손 포즈) 조건화로 v1 방향을 지지합니다.
  - **D32(egocentric hand-object WM)** — 사람 egocentric 영상(EgoDex/VITRA) 사전학습 → 로봇 도메인 이전이라는 v1 의 브리지 시나리오를 world-model 축에서 그대로 실행한 사례입니다.
- **P0(VLA Datasets & Benchmarks) — 부 pillar.** **D24(priority data axis)** 의 egocentric-중심 베팅을 지지합니다: EgoDex(P0 핀)가 world model 사전학습 코퍼스로 실전 투입되어 FVD 2598→585 차이를 만드는 것이 확인됩니다. 또한 "생성 world model = 새로운 데이터 소스 유형"이라는 축을 P0 스카우팅 관점에 추가합니다. 다만 자체 1,800 에피소드가 미공개인 한 P0 핀 후보는 아닙니다.
- **P4(Pretraining for Data-Efficient Adaptation) — 간접.** **D21(staged recipe)** / **D22(pretraining data composition)** 의 "ego 사전학습 → 소량 타깃 적응" 구조가 world model 도메인에서 재현됨을 보이는 방증입니다(w/o Human Pre-training 붕괴). **D20(prior-preservation strategy)** 관점에서는 zero-init + 게이트 + 분포 정렬이라는 조건-주입 레시피가 사전학습 prior 보존 패턴의 구체 사례입니다.
- **Identity 관계** — 지지도 긴장도 아닌 **보완**: 우리 스택의 차별화 주장(VLA-level dexterity)과 직접 경쟁하지 않고, P0/P5 지원 축(데이터 생성)에 놓입니다. 단, 관측이 RGB 뿐이라 per-finger proprio-tactile 결합(P2 스코프)을 요구하는 우리 관측 계약과는 데이터 수준에서 어긋납니다 (⚠️ 참조).
- **경쟁자 함의 (P5 §5 Tracked 대비)** — LOME(핀, action-conditioned egocentric WM)의 human-centric 한계를 robot-centric 으로 넘었고, Ctrl-World(핀, raw-pixel 데이터 증강/eval-in-imagination)의 3인칭 로봇팔 세팅을 egocentric 양손 dexterous 세팅으로 옮긴 위치입니다.

---

## ✨ 핀 논문 대비 델타

- **vs LOME (P5 핀)** — LOME 은 image+text+per-frame action 조건의 egocentric world model 이지만 human-centric 생성에 머뭅니다. RynnWorld-Teleop 의 델타는 (1) 로봇 embodiment 를 직접 렌더링하는 robot-centric 전환, (2) 2–10 Hz 급이던 이 계열을 40 FPS 실시간 스트리밍으로 끌어올린 causal 증류, (3) 생성물을 실로봇 정책 학습까지 연결한 end-to-end 검증입니다.
- **vs Ctrl-World (P5 핀)** — 데이터 증강 역할의 raw-pixel world model 이라는 위치는 같지만, Ctrl-World 가 로봇 관측 궤적 기반 3인칭 세팅이라면 본 논문은 사람 손 포즈가 직접 구동하는 egocentric 양손 dexterous 세팅이고, "합성 데이터만으로 zero-shot 실로봇 이전"이라는 더 강한 주장을 실증합니다.
- **vs DexWM / Being-H0.7 (P5 핀)** — 두 핀은 latent(각각 finger-keypoint/hand-consistency, latent world-action) 예측으로 D30 v1 축에 있습니다. 본 논문은 반대편 raw-pixel 생성 축이며, 그 대가로 latent 모델이 줄 수 없는 것 — IL 이 직접 소비하는 픽셀 관측 데이터 — 을 내놓습니다. 예측-공간 선택이 "정책 내부용 prior vs 외부 데이터 엔진"이라는 역할 분기와 정렬됨을 보여주는 대조 사례입니다.
- **vs EgoDex (P0 핀)** — EgoDex 를 소비하는 쪽의 대표 사례로서, egocentric 손 트래킹 코퍼스가 로봇 world model 의 상호작용 prior 로 전이됨을 정량 실증(FVD 2598→585)했다는 점이 P0 관점의 델타입니다.

---

## ⚙️ 의사결정 함의

- **D28 후속 트리거 구체화** — data-augmentation(rollout synthesis) 역할을 tracked 에서 승격할지 판단할 때 본 논문의 셋업을 기준선으로 삼습니다: 혼합 비율 `real:synthetic = 1:1` (300+300), 기대 효과 "정밀 과제 +20%p, 평균 +3~9%p", 게이트 지표 FVD(I3D) + t-SNE 특징 겹침.
- **D30 은 유지, 역할-공간 매트릭스로 기록** — co-training dynamics prior 는 latent/3D-flow(v1 유지), 데이터-엔진/eval-in-imagination 은 raw-pixel 이라는 2×2 역할 분리를 P5 의사결정 노트에 반영할 근거가 생겼습니다.
- **조건-주입 레시피 채택 후보** — 사전학습 백본에 새 모달리티 분기를 붙일 때(예: P2 D10/D11 tactile 토큰 주입, P4 D20 프라이어 보존) 본 논문의 3종 세트를 기본값으로 검토합니다: `zero-init` 분기 + 게이트 스칼라 `alpha_init=0.1` + 조건 latent 의 running $`(\mu,\sigma)`$ 분포 정렬. concat 대비 FVD 585 vs 1191 이 정량 근거입니다.
- **P4 D21/D22 방증 축적** — "ego 대규모 사전학습 → 소량(5.3K slice) 타깃 적응" 이 2-stage 로 성립한다는 결과를 D22 open ablation(egocentric-centric vs mixed)의 ego 쪽 방증으로 기록합니다. 단 world model 도메인의 결과이므로 정책 도메인 직접 증거로 취급하지 않습니다.
- **평가 파이프라인** — 향후 합성 데이터를 우리 IL 파이프라인에 수용할 때 채택 게이트를 "FVD(I3D, 81-frame) + 실측 대비 t-SNE 겹침 + 소규모 정책 A/B(real vs real+syn)" 3단으로 구성하는 것이 본 논문 프로토콜의 직접 이식입니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 체크) 공개 체크포인트로 dexterous 접촉 클로즈업 검증** — HF 공개 모델(Apache-2.0)을 받아 EgoDex-Test 류 클립에서 20+ DoF 손가락-물체 접촉 구간의 생성 품질(손가락 관통, 물체 소멸, 접촉 시점 오차)을 육안+LPIPS 로 확인합니다. GPU 1장·수 시간 수준이며, in-hand 재배향급 정밀 접촉에서 무너지면 우리 용도(Sharpa 22-DOF 손)로는 조기 탈락입니다.
- **관측 모달리티 갭** — 생성되는 관측은 RGB 뿐입니다. 우리 관측 계약은 per-finger proprio-tactile 토큰(P2 D11)을 포함하므로, 이 데이터 엔진으로는 tactile 채널이 없는 IL 데이터만 증강됩니다. tactile 필수 구간(System0, P3)에는 원천적으로 무력한지, RGB-only 사전학습 증강으로도 이득이 남는지를 분리 실험해야 합니다.
- **substitution 아님을 전제로 설계** — 0 Real 성능(68.57 / 82.86 / 77.14 / 28.57)이 300 Real(88.57 / 94.29 / 91.43 / 34.29)에 전 과제에서 뒤집니다. "실로봇 수집 생략" 시나리오는 배제하고 증강 시나리오만 검토합니다.
- **per-platform 적응 비용 견적** — 우리 손·팔 조합에 Stage 2 급 paired 데이터(본 논문 1,800 에피소드)가 필요합니다. 초기 실로봇 teleop 수집이 선행돼야 하므로, "데이터 엔진 도입으로 절약되는 수집량 > Stage 2 요구량" 이 성립하는 규모인지 먼저 계산합니다.
- **재앵커 의존성 스트레스 테스트** — 실측 프레임 재앵커 없이(완전 합성, 특히 편집된 reference 로 시작) 81-프레임 chunk 를 2~3개 이어 붙였을 때의 드리프트를 측정합니다. OOD 장면 인스턴스화 주장(Fig. 7)이 장호라이즌에서도 성립하는지가 데이터 엔진 가치의 실질 상한입니다.
- **causal 화질의 정책 영향** — Robotic-Test 에서 causal 모델 FVD 1534 (teacher 763). 라이브 수집은 causal 모델로 이뤄지므로, causal 생성 데이터로 학습한 정책 성능이 teacher 생성 대비 얼마나 떨어지는지 확인 전에는 40 FPS 수치를 데이터 품질로 오독하지 않습니다.

---

## 💡 컨텍스트 제안

- **P5 §5 Methodology base(non-pinned)에 RynnWorld-Teleop 추가 검토** — D28 의 data-augmentation(rollout synthesis) tracked 역할에 대한 첫 정책-레벨 실로봇 증거로서, Ctrl-World 와 함께 raw-pixel 데이터-엔진 축을 대표합니다. 핀 교체(예: Ctrl-World 대체)는 egocentric·dexterous 세팅 정합성에서 본 논문이 앞서지만, 자체 로봇 데이터 미공개·단일 랩 검증이라는 약점이 있어 우선 non-pinned 트래킹을 제안합니다.
- **D28 노트 갱신 제안** — data-augmentation 역할 항목에 "RynnWorld-Teleop: 1:1 혼합 시 정밀 과제 +20%p, zero-real 이전 성립하나 real 단독 대비 열위" 를 방증으로 병기하고, 승격 트리거를 "우리 embodiment 에서의 소규모 A/B 재현" 으로 명시하는 것을 제안합니다.
- **P0 관찰 노트** — "생성 world model 데이터 엔진" 이라는 새 데이터 소스 유형이 등장했으므로, P0 스카우팅 렌즈에 (합성 데이터 릴리스 + 생성기 가중치 공개) 조합을 추적 대상으로 추가할지 사람 판단을 요청합니다. context/ 파일은 수정하지 않습니다.

---

> 💡 base 매핑은 `/implement-design analysis/2607.06558/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
