# Paper Analysis — RynnWorld-4D: 4D Embodied World Models for Robotic Manipulation

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | RynnWorld-4D: 4D Embodied World Models for Robotic Manipulation |
| 저자 | Haoyu Zhao, Xingyue Zhao, Siteng Huang, Xin Li, Deli Zhao, Zhongyu Li (Alibaba DAMO Academy) |
| 링크 | [arXiv:2607.06559](https://arxiv.org/abs/2607.06559) · [GitHub](https://github.com/alibaba-damo-academy/RynnWorld-4D) · [HuggingFace](https://huggingface.co/Alibaba-DAMO-Academy/RynnWorld-4D) · [Website](https://alibaba-damo-academy.github.io/RynnWorld-4D.github.io) |
| 발행일 / 버전 | 2026-07-07 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-07-09 |
| 관련 Pillar | P5, P2, P0 |
| 태그 | flow-matching, egocentric-data, dataset |

---

## 🧭 한 줄 요약 (TL;DR)

RynnWorld-4D는 RGB·깊이·광학 흐름(RGB-DF)을 **하나의 확산 루프**에서 동기 생성하는 4D 세계 모델로, 이 표현이 2D 픽셀보다 로봇 저수준 행동에 훨씬 가깝다는 통찰 아래, 동결된 세계 모델의 내부 4D 잠재를 단일 순전파로 소비하는 역동역학(inverse dynamics) 정책 헤드(RynnWorld-4D-Policy)를 붙여 실세계 양손 조작에서 SOTA를 달성합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 개방 세계 로봇 조작은 "장면이 어떻게 보이는가"뿐 아니라 "상호작용 아래 3D 구조가 어떻게 움직이는가"를 예측해야 하는데, 기존 비디오 세계 모델은 2D 픽셀 공간에 머물러 3D 기하 구조를 담지 못하고 예측과 로봇 행동 사이에 큰 표현 간극을 남깁니다.
- **기존 접근의 한계** — 2D 미래 예측 기반 정책(SuSIE, UniPi 등)은 픽셀 공간에서만 작동하며 매 행동 스텝마다 반복적 denoising 을 요구해 기하 정확도와 제어 반응성 양쪽에서 본질적 한계를 갖습니다. 반면 명시적 3D 볼륨·4D 가우시안·메시 기반 3D 세계 모델은 다중 뷰 입력을 요구하거나 장면 특화적이며 대규모 비디오 사전학습 prior 의 확장성을 잃습니다.
- **본 논문의 가설** — 동기화된 RGB-깊이-광학 흐름(RGB-DF)이 장면의 4D 동역학을 물리적으로 grounding 하는 표현을 제공하며, 2D 픽셀 대비 시각 외형·기하 구조·시간적 운동을 정렬시켜 로봇의 저수준 end-effector 행동에 훨씬 가까운 표현 공간을 만든다는 것입니다.
- **왜 지금 중요한가** — 대규모 비디오 확산 모델(Wan, CogVideoX)의 생성 prior 가 성숙했고, Depth Anything 3·DPFlow 같은 고품질 pseudo-label 도구로 깊이·흐름을 대량 주석할 수 있게 되면서, 2D 정렬 포맷을 유지하면서도 4D 동역학을 확장 가능하게 학습할 조건이 갖춰졌습니다.
- **우리 맥락의 의미** — P5(World Model)의 핵심 질문인 "세계 모델을 정책 스택에 어떻게 접합할 것인가"에 대한 구체적 답(동결 WM → 역동역학 헤드)이며, 동시에 예측 공간 선택(D30: latent/3D-flow vs raw-pixel)에 raw-pixel 생성 + 명시적 3D scene flow 라는 혼합 입장을 제시합니다.

---

## 🧩 핵심 기여

- **투영적(projective) 4D 표현** — RGB·깊이·광학 흐름을 함께 생성하고, 이를 자연스럽게 3D scene flow 로 읽어낼 수 있음을 보여, 기하와 운동을 명시화하면서도 대규모 비디오 확산 prior 와의 호환성(2D 정렬 포맷)을 유지합니다.
- **RynnWorld-4D (tri-branch 세계 모델)** — 상호 cross-modal 상호작용을 통해 물리적으로 일관된 RGB-DF 시퀀스를 동기 생성하는 3분기 트랜스포머 아키텍처.
- **Rynn4DDataset 1.0** — 254.4M 프레임 규모의 4D embodied 비디오 데이터셋으로, 에고센트릭 인간 + 로봇 조작 비디오에 깊이·광학 흐름 pseudo-label 을 부착.
- **RynnWorld-4D-Policy** — 내부 4D 표현을 단일 순전파로 소비해 반복 denoising 병목을 우회하고, 고주파 폐루프 로봇 제어를 가능케 하는 역동역학 헤드.

---

## 🔑 기술 키워드

- **4D World Model** — 3D 공간(RGB+깊이) + 시간(운동)을 함께 예측하는 세계 모델. 여기서는 RGB-깊이-흐름을 동기 생성해 "4D"를 구성합니다.
- **RGB-DF Representation** — RGB·Depth·Flow 3-모달을 2D 정렬 포맷으로 묶은 표현. 명시적 3D 볼륨 대신 픽셀-정렬을 유지해 비디오 확산 prior 를 상속합니다.
- **3D Scene Flow** — 각 3D 점의 프레임 간 metric 변위. 깊이(깊이→3D 점) + 광학 흐름(2D 대응)을 결합해 back-projection 으로 유도합니다.
- **Tri-branch Architecture** — 한 backbone 을 3개 모달 분기로 확장한 구조. 각 분기가 텍스처/기하/운동을 특화 모델링해 표현 간섭을 완화합니다.
- **Joint Cross-Modal Attention (JA)** — 3개 분기 토큰을 같은 시간 프레임 안에서 교차-어텐션시켜 cross-modal 일관성을 강제하는 모듈.
- **Frame-wise 3D RoPE** — 같은 $`(u,v)`$ 좌표의 모달 간 특징을 기하적으로 정렬시키는 회전 위치 임베딩. cross-branch 경로에서 픽셀 수준 정렬 다리 역할을 합니다.
- **Flow Matching** — 플로우 매칭 — Gaussian 노이즈에서 데이터로의 속도장을 학습하는 생성 목표. 세계 모델(RGB-DF 생성)과 정책(행동 생성) 양쪽에 사용됩니다.
- **Inverse Dynamics Head** — 미래 예측 표현으로부터 그 미래를 만들 행동을 역추정하는 헤드. 여기서는 동결된 4D 잠재 → 행동 청크.
- **Predictive 4D Vision Encoder** — 세계 모델을 동결한 채 "미래를 담은" 내부 잠재를 뽑는 인코더로 재활용하는 관점. 단일 순전파, 반복 denoising 없음.
- **Branch Dropout** — 학습 중 depth/flow 분기의 잠재를 순수 노이즈로 대체해 JA 가 가시 모달로부터 복원하도록 강제하는 정규화.

---

## 🔬 방법론

### 직관

RynnWorld-4D의 출발점은 "미래 예측과 정책 학습 사이의 표현 간극"입니다. 순수 비디오 세계 모델은 RGB 픽셀의 변화를 예측하지만, 로봇이 실제로 내보내야 하는 것은 3D 공간의 저수준 행동입니다. 픽셀 흐름과 3D 행동 사이에는 무거운 구조 추론이 끼어 있어, 2D 잠재만으로 정책을 학습하면 이 추론을 정책이 암묵적으로 떠안아야 합니다.

핵심 통찰은 "RGB에 깊이와 광학 흐름을 함께 생성하면, 그 표현이 곧 3D scene flow 로 back-projection 되어 행동 공간에 훨씬 가까워진다"는 것입니다. 깊이는 각 픽셀을 3D 점으로 들어올리고(unprojection), 광학 흐름은 프레임 간 대응을 주므로, 둘을 합치면 각 점의 metric 3D 변위(scene flow)가 나옵니다. 이 3D 운동이 명시적이면 정책은 "무엇이 어디로 움직이는가"를 직접 읽을 수 있습니다.

구현은 두 층으로 나뉩니다. (1) **세계 모델**: 사전학습된 비디오 확산 모델(Wan-2.2)을 3분기로 확장해 RGB/깊이/흐름을 하나의 denoising 루프에서 동기 생성합니다. 분기를 나눠 각 모달의 이질적 분포(텍스처 vs 기하 vs 운동)를 특화 모델링하되, Joint Cross-Modal Attention 으로 세 모달이 물리적으로 일관되게 진화하도록 묶습니다. (2) **정책**: 이 세계 모델을 **동결**한 채 하나의 예측적 4D 비전 인코더로 쓰고, 내부 은닉 상태를 단일 순전파로 뽑아 경량 역동역학 헤드로 행동을 생성합니다. 세계 모델은 반복 denoising 없이 한 번만 통과하므로 실시간 폐루프 제어가 가능합니다.

주의할 미묘한 점은, RynnWorld-4D 세계 모델 자체는 **행동으로 조건화되지 않는다**는 것입니다. 조건은 초기 RGB-D 관찰 + 언어 지시뿐이고, 미래를 예측한 뒤 정책이 그 미래로부터 행동을 역추정합니다. 즉 "행동-조건 예측"이 아니라 "언어-조건 미래 예측 + 역동역학" 계열입니다.

### 아키텍처

**입력/출력 및 잠재 정의**

모달 $`m\in\{\text{rgb, depth, flow}\}`$ 의 잠재를 $`\mathbf{z}_{t}^{m}`$ 로 표기하며 $`t\in[0,1]`$ 은 flow-matching timestep 입니다. 각 $`\mathbf{z}_{t}^{m}\in\mathbb{R}^{T\times C\times H\times W}`$ 는 $`T`$ 프레임 전체 시퀀스를 담습니다.

> "We denote the latents for modality $`m\in\{\text{rgb, depth, flow}\}`$ as $`\mathbf{z}_{t}^{m}`$, where $`t\in[0,1]`$ represents the flow-matching timestep." (§3.3)
> (세 모달은 각각 독립 잠재 텐서를 가지되 동일한 flow-matching timestep 을 공유하므로, denoising 궤적이 시간적으로 정렬됩니다.)

![Figure 1 — RGB-DF 동기 생성 + 3D scene flow](https://arxiv.org/html/2607.06559/x3.png)

> "Figure 1: Given an input RGB-D image and description, RynnWorld-4D generates RGB, depth, and optical flow videos synchronously, which can be further lifted into 3D scene flow (right)." (§1)
> (이 그림이 본 논문의 핵심 주장 — RGB-DF 표현이 3D scene flow 로 들어올려져 기하·운동을 명시화한다 — 을 시각화합니다.)

**Tri-branch 구조**

Wan-2.2-TI2V-5B(30-layer DiT, hidden $`d=3072`$, FFN $`14{,}336`$)의 단일-분기 RGB backbone 을 3분기로 확장합니다. 깊이·흐름 분기는 사전학습 컴포넌트(patch embedding, self-attention, normalization, FFN)를 복제해 초기화하여 비디오 backbone 의 시공간 prior 를 상속합니다.

> "This decoupled design allows each modality to model its unique feature distributions, such as complex textures for RGB, spatial geometry for depth, and motion displacements for flow to mitigate representation interference among divergent modalities." (§3.3)
> (분기 분리의 목적은 이질적 분포를 가진 모달들이 서로 표현을 간섭하지 않도록 각자의 특징 분포를 특화 모델링하게 하는 것입니다.)

**Joint Cross-Modal Attention (JA)**

JA 모듈은 30개 Wan-2.2 레이어 중 3개마다(layers $`0,3,6,\dots,27`$) 삽입되어 총 10개이며, 각 host block 의 intra-modal self-attention 뒤에 붙습니다. cross-modal 혼합 전, 각 분기는 학습 가능한 모달 임베딩 $`\mathbf{e}^{m}\in\mathbb{R}^{1\times 1\times d}`$ (zero-init → 순수 residual 로 시작)를 받고 per-modality LayerNorm 으로 스케일을 정렬합니다:

$$\tilde{\mathbf{z}}_{l}^{m}=\mathrm{LN}^{m}\bigl(\mathbf{z}_{l}^{m}+\mathbf{e}^{m}\bigr)$$

각 분기는 하나의 query 와 하나의 shared key/value 쌍을 만들어 다른 분기들의 query 가 재사용하게 하여, block 당 파라미터 비용을 $`18d^{2}`$ 에서 $`12d^{2}`$ 로 줄입니다:

$$\mathbf{Q}_{l}^{m}=\mathrm{RMSNorm}_{q}\!\bigl(\mathrm{QProj}_{l}^{m}(\tilde{\mathbf{z}}_{l}^{m})\bigr),\quad[\mathbf{K}_{l}^{m},\mathbf{V}_{l}^{m}]=\mathrm{KVProj}_{l}^{m}(\tilde{\mathbf{z}}_{l}^{m}),\quad\mathbf{K}_{l}^{m}\!\leftarrow\!\mathrm{RMSNorm}_{k}(\mathbf{K}_{l}^{m})$$

토큰은 $`[B,T{\cdot}S,d]`$ 에서 $`[B{\cdot}T,S,d]`$ 로 reshape 되어 cross-modal 어텐션이 **같은 시간 프레임의 토큰들**로 제한되며, 3D RoPE 가 $`\mathbf{Q}_{l}^{m}`$ 와 $`\mathbf{K}_{l}^{m}`$ 에 적용되어 분기 간 공간 위치가 일관되게 주입됩니다. 각 query 는 자신을 제외한 두 모달의 key/value 에만 어텐션합니다:

$$\mathbf{A}_{l}^{m}=\mathrm{Attn}\bigl(\mathrm{RoPE}(\mathbf{Q}_{l}^{m}),\;\mathrm{RoPE}(\mathbf{K}_{l}^{\text{cross}}),\;\mathbf{V}_{l}^{\text{cross}}\bigr)$$

여기서 $`\mathbf{K}_{l}^{\text{cross}}=\mathrm{concat}(\{\mathbf{K}_{l}^{j}\}_{j\neq m})`$, $`\mathbf{V}_{l}^{\text{cross}}=\mathrm{concat}(\{\mathbf{V}_{l}^{j}\}_{j\neq m})`$ 입니다.

**Saddle-point 회피 게이트** — ControlNet 의 이중 zero-init 이 saddle-point deadlock 을 낳는 것을 발견하여, zero-init output projection 과 $`1`$ 로 초기화된 학습 가능 게이트 $`g_{l}^{m}`$ 를 결합합니다:

$$\hat{\mathbf{z}}_{l}^{m}=\mathbf{z}_{l}^{m}+\tanh(g_{l}^{m})\cdot\mathrm{OutProj}_{l}^{m}(\mathbf{A}_{l}^{m})$$

> "At initialization $`\mathrm{OutProj}_{l}^{m}\equiv 0`$ guarantees a smooth warm start from the Stage-1 checkpoint, while $`\tanh(g_{l}^{m})=\tanh(1)\neq 0`$ ensures non-zero gradients flow into the gate so that it can decrease, increase, or change sign as training proceeds, preventing the joint pathway from being trapped at the origin." (§3.3)
> (출력은 0 에서 시작해 Stage-1 체크포인트를 매끄럽게 이어받지만, 게이트로 흐르는 gradient 는 0 이 아니므로 joint 경로가 원점에 갇히지 않고 학습이 진행될 수 있습니다.)

![Figure 4 — RynnWorld-4D 파이프라인 개요](https://arxiv.org/html/2607.06559/x6.png)

> "Figure 4: Overview of RynnWorld-4D. Our pipeline leverages the large-scale Rynn4DDataset 1.0 dataset to train a generative model capable of predicting future 4D sequences. Given a single RGB-D observation and a language instruction, RynnWorld-4D co-generates future RGB frames, depth maps, and optic[al flow]" (§3.3)
> (세계 모델의 전체 구조 — Rynn4DDataset 으로 학습된 tri-branch 가 초기 RGB-D + 언어로부터 미래 RGB/깊이/흐름을 함께 생성 — 를 요약합니다.)

**3D scene flow 유도 (§3.2)**

깊이 맵 $`D_{t}`$ 로 각 픽셀 $`\mathbf{p}_{t}=[u,v,1]^{\top}`$ 을 3D 카메라 공간으로 unprojection:

$$\mathbf{P}_{t}=D_{t}(u,v)\cdot\mathbf{K}^{-1}\mathbf{p}_{t}$$

광학 흐름 $`\mathbf{f}_{opt}=[\Delta u,\Delta v]^{\top}`$ 로 3D 점을 $`t+1`$ 위치로 추적:

$$\mathbf{P}_{t+1}=D_{t+1}(u+\Delta u,v+\Delta v)\cdot\mathbf{K}^{-1}(\mathbf{p}_{t}+[\Delta u,\Delta v,0]^{\top})$$

3D scene flow 는 $`\mathbf{f}_{3D}=\mathbf{P}_{t+1}-\mathbf{P}_{t}`$ 로 정의되며, 깊이 불연속(edge)에서 $`\|\nabla D\|>\tau`$ 인 픽셀을 마스킹해 아티팩트를 억제합니다.

> "This explicit 4D mapping ensures that the generated trajectories are not merely visual hallucinations but correspond to physically plausible 3D movements." (§3.2)
> (명시적 4D 매핑 덕에 생성 궤적이 단순한 시각적 환각이 아니라 물리적으로 타당한 3D 운동에 대응함을 보장합니다.)

### 학습 목표 / 손실

세 스테이지 모두 flow matching 목표로 최적화합니다. 각 모달 $`m\in\mathcal{M}=\{\text{rgb},\text{depth},\text{flow}\}`$ 에 대해 Gaussian 노이즈 $`\mathbf{\epsilon}^{m}`$ 를 데이터 $`\mathbf{z}_{0}^{m}`$ 로 옮기는 속도장 $`\mathbf{v}_{\theta}^{m}`$ 를 경로 $`\mathbf{z}_{t}^{m}=(1-t)\mathbf{z}_{0}^{m}+t\mathbf{\epsilon}^{m}`$ 위에서 학습합니다. 각 모달의 첫 프레임은 clean 조건화 잠재(실제 RGB·실제 depth·zero-flow)로 감독에서 제외되며 슬라이스 $`[1{:}]`$ 로 표기합니다:

$$\mathcal{L}_{\text{total}}=\sum_{m\in\mathcal{M}}\lambda_{m}\,\mathbb{E}_{\mathbf{z}_{0}^{m},\mathbf{\epsilon}^{m},t,\mathbf{c}}\!\left[\bigl\|\mathbf{v}_{\theta}^{m}\!\bigl(\mathbf{z}_{t}^{m},t,\mathbf{c}\bigr)_{[1{:}]}-\bigl(\mathbf{\epsilon}^{m}-\mathbf{z}_{0}^{m}\bigr)_{[1{:}]}\bigr\|_{2}^{2}\right]$$

> "$`\mathbf{\epsilon}^{\text{rgb}}=\mathbf{\epsilon}^{\text{depth}}=\mathbf{\epsilon}^{\text{flow}}`$ is a single Gaussian noise sample shared across the three modalities so that their denoising trajectories stay temporally aligned." (§3.3)
> (세 모달이 **동일한** Gaussian 노이즈 샘플을 공유하는 것이 핵심 — denoising 궤적을 시간적으로 정렬시켜 cross-modal 일관성의 물리적 기반을 만듭니다.)

모달 가중치는 $`\lambda_{\text{rgb}}=\lambda_{\text{depth}}=1`$ 로 고정, $`\lambda_{\text{flow}}=0.5`$ (Stage 1, warm-up 시 flow 첫 프레임에 정보 신호 없음) → $`\lambda_{\text{flow}}=1.0`$ (Stage 2·3).

**Branch Dropout** — Stage 2·3 에서 확률 $`p_{\text{drop}}`$ 로 $`\{\text{depth},\text{flow}\}`$ 중 하나를 골라 그 잡음 잠재(프레임 $`[1{:}]`$)를 순수 Gaussian 노이즈로 대체, JA 가 가시 모달로부터 복원하도록 강제합니다. RGB 분기는 appearance anchor 이므로 절대 dropout 하지 않습니다.

### 학습 셋업

**3-스테이지 커리큘럼** — 각 스테이지는 이전 스테이지의 model-only 체크포인트에서 초기화(optimizer/scheduler reset). AdamW($`\beta_{1}{=}0.9,\beta_{2}{=}0.95`$, weight decay $`1{\times}10^{-4}`$) + cosine + linear warm-up, EMA(decay $`0.9999`$).

| Stage | 융합 모드 | 학습 파라미터 | LR | warm-up | $`\lambda_{\text{flow}}`$ | Branch Dropout |
|---|---|---|---|---|---|---|
| 1 Modality Adaptation | none | 모든 분기 | $`2{\times}10^{-5}`$ | 500 | 0.5 | — |
| 2 Frozen-Backbone JA | joint (frozen bb.) | JA + 모달 임베딩 | $`5{\times}10^{-5}`$ | 200 | 1.0 | 0.2 |
| 3 Full-Parameter Joint SFT | joint (full SFT) | 전체 파라미터 | $`1{\times}10^{-5}`$ | 500 | 1.0 | 0.1 |

- **해상도/프레임** — $`81\times 480\times 640`$ (causal VAE 의 $`4\times`$ 시간 압축으로 $`T=21`$ latent frame, $`T_{\text{latent}}=(T_{\text{pixel}}-1)/4+1`$), bf16 mixed precision + gradient checkpointing. Stage 2·3 은 DeepSpeed ZeRO-2 + optimizer offload.

**RynnWorld-4D-Policy (§3.4)** — 동결된 RynnWorld-4D 를 예측적 4D 비전 인코더로 사용. diffusion timestep $`t=500`$ 에서 단일 스텝 특징 추출, 트랜스포머 block 15 의 은닉 상태를 캡처. 세 분기(각 3072-dim)를 채널 축으로 concat 해 $`F_{p}\in\mathbb{R}^{B\times T\times 3C\times H\times W}`$ 구성.

- **Flow Former** — 학습 가능 query $`\mathbf{Q}`$ 로 4D 특징을 압축. 프레임별 spatial cross-attention → temporal self-attention:

$$\mathbf{Q}^{\prime}_{i}=\mathrm{Spat-CrossAttn}(\mathbf{Q}_{i},F_{p}[i]),\quad\mathbf{Q}^{\prime\prime}=\mathrm{FFN}(\mathrm{Temp-SelfAttn}(\mathbf{Q}^{\prime})),\;i\in\{1,\dots,T\}$$

- **Action Generation** — flow matching 정책(Eq. 7 목표). 속도장 $`v_{\phi}`$ 는 행동 공간 $`\mathbf{a}`$ 에 작동하며 예측적 4D 토큰 $`\mathbf{Q}^{\prime\prime}`$, text embedding $`l_{\text{emb}}`$, proprioception $`p_{0}`$ 로 조건화. 추론 시 $`N=4`$ 스텝 Euler ODE. 행동 청크 길이 10, 각 행동 54-dim. AdamW($`10^{-4}`$, $`\beta=(0.9,0.9)`$, weight decay 0.05), tri-stage LR schedule(2% warmup / 8% hold / 90% cosine), backbone 동결, batch size 1/GPU, 100 epoch.

- **실시간 제어** — RTX 5090, FP8 + FlashAttention 3. 세계 모델 특징은 단일 순전파($`N=1`$)로만 추출, 4-step ODE 는 경량 정책 헤드 안에서만. $`K=10`$ 행동/순전파, cycle time $`\sim1.1`$s → planning $`\approx0.9`$Hz 이지만 action chunking + 병렬 계획으로 effective control $`\approx9`$Hz(청크는 50Hz cached lookup 로 집행).

---

## 📊 실험 설정과 결과

**평가 셋업** — 세계 모델은 RoboMIND/RDT-1B/Galaxea 에서 무작위 샘플한 held-out 50 비디오로 평가. 축 3개: (1) Visual Synthesis Quality(IQ/MS/SC/Subj. + PSNR/SSIM/LPIPS), (2) Geometric Accuracy(AbsRel, $`\delta_{1}`$), (3) Temporal Motion Consistency(AEPE). 실세계 지표는 Success Rate(120초 내 완료, 35회 연속 시행). 하드웨어: TIANJI M6 7-DOF 팔 + WUJI HAND(20-DOF), RealSense D435i FPV.

### 4D 세계 모델링 품질 (Table 4)

| Method | IQ ↑ | SC ↑ | SSIM ↑ | PSNR ↑ | LPIPS ↓ | AbsRel ↓ | $`\delta_{1}`$ ↑ | AEPE ↓ |
|---|---|---|---|---|---|---|---|---|
| CogVideoX | 0.604 | 0.866 | 0.534 | 12.17 | 0.577 | N/A | N/A | N/A |
| Wan-2.2-TI2V-5B | 0.555 | 0.886 | 0.593 | 14.54 | 0.489 | N/A | N/A | N/A |
| Wan-2.1-I2V-14B | 0.684 | 0.891 | 0.536 | 12.72 | 0.568 | N/A | N/A | N/A |
| Free4D | 0.354 | 0.787 | 0.492 | 12.40 | 0.597 | 0.804 | 0.179 | N/A |
| TesserAct | 0.608 | 0.904 | 0.693 | 16.91 | 0.335 | 0.699 | 0.279 | N/A |
| 4DNeX | 0.637 | 0.917 | 0.649 | 14.47 | 0.404 | 0.423 | 0.327 | N/A |
| **RynnWorld-4D** | **0.635** | **0.957** | **0.754** | **17.85** | **0.269** | **0.310** | **0.610** | **0.170** |

> "our model achieves a $`\delta_{1}`$ of 0.610, nearly doubling the performance of 4DNeX (0.327) and TesserAct (0.279). Regarding motion, RynnWorld-4D uniquely provides synchronized optical flow with a low AEPE of 0.170, whereas most baseline 4D models lack the capability to produce explicit motion fields." (§4.3, Table 4)
> (기하 $`\delta_{1}`$ 은 기존 4D 세계 모델을 거의 2배 능가하고, 동기 광학 흐름(AEPE 0.170)은 다른 4D 모델이 아예 생성하지 못하는 명시적 운동장을 제공한다는 차별점입니다.)

### 정책 성공률 (Table 5, %)

| Method | Dual Picking | Block Pushing | Hand-over | Bimanual Lifting | Lid Placement | Bowl Stacking |
|---|---|---|---|---|---|---|
| DP | 77.14 | 85.71 | 17.14 | 88.57 | 57.14 | 57.14 |
| $`\pi_{0}`$ | 88.57 | 94.29 | 2.86 | 91.43 | 34.29 | 51.43 |
| $`\pi_{0.5}`$ | 94.29 | **100.00** | 0.00 | 94.29 | 37.14 | 42.86 |
| **RynnWorld-4D-Policy** | **94.29** | 97.14 | **28.57** | **97.14** | **65.71** | **65.71** |

> "in tasks requiring high spatial precision such as Lid Placement and Bowl Stacking, RynnWorld-4D-Policy achieves success rates of 65.71%, surpassing the next best baseline (DP) by 8.57%." (§4.3, Table 5)
> (공간 정밀도가 요구되는 Lid Placement·Bowl Stacking 에서 DP 대비 8.57%p 앞서며, 특히 동적 물체 이전인 Hand-over 는 foundation model($`\pi_{0.5}`$ 는 0.00%)이 무너지는 지점에서 28.57% 로 유일하게 유의미한 성능을 냅니다.)

> "their pre-training data is predominantly biased towards parallel-jaw grippers, lacking the inherent priors for the complex dexterous hand coordination. Second, in a hand-over scenario, 2D-based models struggle to reason about the relative 3D distance and potential self-occlusion between two high-DOF end-effectors." (§4.3)
> (foundation model 이 Hand-over 에서 무너지는 이유를 두 가지로 진단 — 사전학습 데이터가 parallel-jaw gripper 편향이라 dexterous hand 협응 prior 가 없고, 2D 기반이라 두 고-DOF end-effector 간 3D 거리·self-occlusion 추론이 어렵다는 것 — 은 P1/P2 관점에서 특히 시사적입니다.)

### Ablation (Table 4 / Table 5)

- **Tri-branch vs Independent Branches** — 독립 분기는 depth AbsRel 0.310→0.737, flow AEPE 0.170→0.247 로 급락. 상호 특징 상호작용이 cross-modal 일관성·물리 정확도에 필수임을 확인.
- **w/o Modality Adaptation** — Stage 1 생략 시 $`\delta_{1}`$ 0.610→0.479. 모달 특화 적응이 융합의 전제 조건.
- **w/o 4D Pre-training** — Rynn4DDataset 없이 task-specific 데이터만 → AEPE 0.170→0.729 로 붕괴. 대규모 4D 사전학습의 다양성이 핵심.
- **w/o RoPE in JA** — $`\delta_{1}`$ 0.610→0.450, AEPE 0.170→0.210. 3D RoPE 가 픽셀 수준 기하 정렬 다리 역할.
- **Shared FFN** — AbsRel 0.580 / $`\delta_{1}`$ 0.380 / AEPE 0.280 로 systemic collapse. 모달별 FFN(이질적 잠재 공간)이 필수.
- **w/o RynnWorld-4D (ResNet-18 대체)** — Dual Picking 94.29%→71.43%. 정적 2D 특징으로는 복잡 과제 불가.
- **모달 기여도** — RGB only < RGB+Depth(공간 정밀 과제 이득) / RGB+Flow(운동 민감 과제 이득) < 3-모달 전체가 최고. 시각 맥락 + 공간 기하 + 운동 동역학의 시너지 확인.

![Figure 5 — 실세계 양손 조작 벤치마크 6개 과제](https://arxiv.org/html/2607.06559/x7.png)

> "Figure 5: Real-world Manipulation Benchmark. We establish a comprehensive evaluation suite comprising six diverse tasks to assess the model's performance in open-world manipulation, providing a rigorous testbed for our 4D world model." (§4.2)
> (6개 과제가 양손 협응·시간 시퀀싱·장기 지평 상호작용을 어떻게 커버하는지 보여, 정책 성능표(Table 5)의 셋업을 시각화합니다.)

**추론 지연 분해 (Table 1)** — 총 1,106 ms 중 RynnWorld-4D(tri-branch Transformer)가 990 ms(89.5%)로 주 병목. Depth Estimation(DA3) 85 ms(7.7%), Flow Former 4 ms, Action Flow Matching Head 8 ms.

---

## ⚖️ 한계

- **저자 명시 — 확산 denoising 계산 오버헤드** — 4D 시퀀스 생성이 확산 denoising 에 의존해 RTX 5090 에서 effective control 이 $`\approx9`$Hz 에 그칩니다. 초고주파 제어가 필요한 접촉-집약 작업에는 이 지연이 병목이며, 정책 헤드가 아무리 경량이어도 세계 모델 순전파(89.5%)가 프레임률의 상한을 정합니다.
- **저자 명시 — 에고센트릭 단일 시점 최적화** — 4D 시공간 일관성이 egocentric 관점에 특화되어 있어 multi-view·다중 로봇 협업으로의 확장이 미해결입니다. 3D scene flow 유도가 단일 카메라 intrinsic $`\mathbf{K}`$ 에 묶여 있어, 뷰 간 정합이 필요한 상황에서는 표현의 기하 grounding 이 곧바로 이전되지 않습니다.
- **추론 갭 — pseudo-label 감독의 상한** — 깊이·흐름이 Depth Anything 3·DPFlow 의 pseudo-label 로 학습되므로, 세계 모델의 기하·운동 정확도는 근본적으로 이 도구들의 오차에 눌립니다. 단안 metric 깊이 오차가 3D scene flow(Eq. 1·2)로 전파되면 "물리적으로 타당한 3D 운동"이라는 주장의 실제 정밀도가 label 품질에 종속됩니다.
- **추론 갭 — 행동-무조건 세계 모델의 예측 모호성** — 세계 모델이 초기 RGB-D + 언어로만 조건화되고 로봇 행동을 입력받지 않으므로, 예측된 미래는 "이 지시 하에서 그럴듯한 미래"이지 "이 특정 행동이 만들 미래"가 아닙니다. 언어+이미지가 미래를 충분히 결정하지 못하는 다중-모드 상황(예: in-hand reorientation 의 여러 회전 경로)에서는 역동역학 헤드가 학습해야 할 대응이 underdetermined 해집니다.
- **추론 갭 — dexterity 주장의 실제 범위** — WUJI HAND 는 20-DOF dexterous 이지만 6개 과제(picking, pushing, hand-over, lifting, lid, bowl stacking)는 대체로 gross 양손 협응·정밀 배치이지 손가락 수준 in-hand 조작이 아닙니다. "dexterous bimanual" 이라는 라벨은 hardware DOF 에서 오고, 과제 난이도는 손가락 접촉-집약 정밀도까지 밀지 않습니다.
- **추론 갭 — 촉각/힘 부재** — 세계 모델과 정책 모두 순수 시각(RGB-DF)이며 촉각·힘 신호가 없습니다. Hand-over 가 개선되긴 했으나 28.57% 에 머무는 것은 접촉-집약 협응에서 시각만으로는 부족함을 시사합니다.

---

## ♻️ 재현성

- **코드** — [GitHub](https://github.com/alibaba-damo-academy/RynnWorld-4D) 공개(alibaba-damo-academy).
- **모델 가중치** — [HuggingFace](https://huggingface.co/Alibaba-DAMO-Academy/RynnWorld-4D) 및 ModelScope(DAMO_Academy/RynnWorld-4D) 공개.
- **데이터** — Rynn4DDataset 1.0 은 공개 소스(Epic-Kitchens, EgoVid, RoboMIND, RDT-1B, Galaxea, RoboCoin, AgiBot)에 pseudo-label(Qwen3-VL 캡션 / Depth Anything 3 깊이 / DPFlow 흐름)을 부착한 것으로, 주석 파이프라인이 §3.1 에 명시. 데이터셋 배포 여부는 본문상 불명확(원문에 명시적 배포 링크 없음).
- **하드웨어** — 세계 모델 학습은 대규모 GPU + DeepSpeed ZeRO-2 필요(구체적 GPU 수 미명시, Table 2 에 gradient accumulation 2-4 × $`N_{\text{GPU}}`$). 추론/배포는 단일 RTX 5090(FP8 + FA3). 실세계 플랫폼 TIANJI M6 + WUJI HAND 는 상용 하드웨어.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P5(World Model) — 주 pillar.** 이 논문은 P5 의 다섯 결정 모두에 직접 닿습니다.
  - **D28(world-model role)** — RynnWorld-4D 는 독립 planner 가 아니라 정책의 **예측적 4D 비전 인코더**(표현/미래-예측 보조)로 쓰입니다. PROBE 의 v1("latent dynamics prior + future-prediction auxiliary")과 역할 방향이 일치하되, co-train 이 아니라 **동결-후-부착**이라는 점이 다릅니다.
  - **D29(integration architecture)** — 세계 모델을 사전학습 후 동결하고 경량 정책 헤드(Flow Former + flow-matching)를 붙이는 **2단계 decoupled** 접합으로, PROBE 가 D29 에서 "VLA-JEPA 의 두-단계(디커플드) 변형"으로 추적하는 경로의 또 다른 구체 사례입니다. 공유 backbone 위 auxiliary head(v1) 도, 완전 unified autoregressive(WorldVLA) 도 아닙니다.
  - **D30(prediction space)** — PROBE v1 은 "latent/3D-flow over raw-pixel" 인데, 본 논문은 **raw-pixel 생성(RGB-DF diffusion) + 명시적 3D scene flow** 라는 혼합 입장입니다. 흥미로운 긴장 — 픽셀을 실제로 생성하되(비싼 denoising) 정책은 픽셀이 아닌 내부 잠재를 단일 순전파로 소비합니다.
  - **D31(action conditioning)** — **긴장 지점.** PROBE v1 은 "action-conditioned(per-frame) prediction" 이고 §4 anti-topics 는 action-free next-frame 예측을 배제합니다. RynnWorld-4D 세계 모델은 **행동-무조건**(언어+RGB-D)이며 역동역학으로 행동을 사후 추정합니다. 로봇 전이·조작 eval 이 있으므로 anti-topic 은 아니지만, 조건화 축에서 PROBE 의 현재 선택과 반대 방향의 증거입니다.
  - **D32(egocentric hand-object WM)** — 데이터가 egocentric 인간 + 로봇, 하드웨어가 FPV(RealSense) + dexterous hand 로, PROBE 의 "egocentric human video → in-house ego 계획" 브리징 방향과 정렬됩니다.
- **P2(Structured Multimodal Observation Fusion) — 부 pillar.**
  - **D9(action/dynamics-aware vision encoder)** — RynnWorld-4D 를 "predictive 4D vision encoder" 로 재활용하는 것은 D9 이 추적하는 DynaFLIP/eVGGT 계열(동역학-인식 인코더)의 강한 사례입니다.
  - **D10(fusion beyond concat)** — Joint Cross-Modal Attention 이 flat concat 을 넘는 cross-attention 융합.
- **P0(VLA Datasets & Benchmarks) — 부 pillar.** Rynn4DDataset 1.0(254.4M 프레임, egocentric+robot, 깊이·흐름 pseudo-label)은 **D24(priority data axis: egocentric)** 에 닿고, 6-과제 실세계 벤치마크는 **D26(benchmark scouting scope)** 에 닿습니다. 단, 라이선스·배포성(D27)은 pseudo-label 파이프라인 재현에 종속.
- **P1(Body/Hand Action Expert) — 약한 tie / 대조군.** 정책은 54-dim 양손 dexterous 행동을 내는 **monolithic** flow-matching 헤드로, PROBE 의 Body/Hand 분리 차별화(D1)와 반대인 비교군입니다. 다만 §4.3 의 진단("foundation model 이 parallel-jaw 편향이라 dexterous hand prior 부재")은 P1 의 문제의식을 뒷받침합니다.
- **Identity 긴장/지지** — PROBE 정체성은 dexterity 를 VLA-level 에서 tackle 하고 RL 을 System0 접촉 안정화로만 국한합니다. 본 논문은 RL 없이 imitation(flow matching)만으로 dexterous hand 를 다루는 순수-시각 경로를 보이며, 세계 모델을 "예측적 인코더"로 접합하는 P5 방향을 지지합니다. 반면 촉각/힘·손가락 수준 접촉·행동-조건 예측이 빠져 있어 PROBE 의 hand-level 접촉 차별화와는 결이 다릅니다.

---

## ✨ 핀 논문 대비 델타

- **vs TesserAct (zhen2025learning, 본 논문의 최근접 경쟁자)** — TesserAct 는 RGB-D-**Normal** 로 4D 를 모델링하는데, RynnWorld-4D 는 정적 기하(surface normal) 대신 **광학 흐름**을 넣어 3D scene flow 로 back-projection 되는 명시적 동적 단서를 얻습니다. 결과적으로 $`\delta_{1}`$ 0.279→0.610, 그리고 TesserAct 가 못 내는 AEPE(0.170)를 유일하게 제공합니다.
- **vs LOME (P5 pin, arXiv:2603.27449)** — LOME 은 image+text+**per-frame action** 조건의 egocentric 세계 모델이나 "명시적 3D 없음". RynnWorld-4D 는 반대로 **명시적 3D(scene flow)를 갖되 행동-무조건**입니다. 두 축(3D 명시성 ↔ 행동 조건화)에서 상보적 위치.
- **vs VLA-JEPA (P5 pin, arXiv:2602.10098)** — 둘 다 "세계 모델 사전학습 → 동결 → action head" 의 2단계 decoupled 구조를 공유하나, VLA-JEPA 는 **leakage-free latent** 예측(픽셀 생성 없음)인 반면 RynnWorld-4D 는 raw-pixel RGB-DF 를 실제로 생성한 뒤 내부 잠재를 씁니다. 즉 예측 공간(latent vs raw-pixel+flow)이 정반대 선택.
- **vs DexWM (P5 top pin, arXiv:2512.13644)** — DexWM 은 인간 비디오에서 **손-객체** 상호작용을 finger-keypoint·hand-consistency 로 예측하는 hand-centric WM. RynnWorld-4D 는 손 특화 예측 대신 **장면 전역 RGB-DF**를 예측하며, dexterity 는 hardware(20-DOF hand) 로만 오고 손가락 수준 예측 표현은 없습니다.
- **vs Being-H0.7 (P5 pin, arXiv:2605.00078)** — Being-H0.7 은 픽셀을 생성하지 **않고** 잠재 공간에서 미래-인식을 내재화(사후 분기 감독)하는 반면, RynnWorld-4D 는 픽셀·깊이·흐름을 **명시적으로 생성**한 뒤 그 내부 잠재를 소비합니다. "픽셀 생성 회피 vs 픽셀 생성 후 잠재 재활용" 의 대비.

---

## ⚙️ 의사결정 함의

이 논문이 맞다면 P5 세계-모델 접합에서 다음이 구체적으로 바뀝니다.

- **D30 — 예측 모달에 광학 흐름(3D scene flow) 추가 검토.** surface normal·latent-only 대신 depth + optical flow 를 함께 예측해 명시적 3D 운동을 얻는 것이 정책(특히 운동 민감·정밀 과제)에 유의미한 이득(RGB+Flow ablation, AEPE 0.170)을 준다는 증거. 실행 시 config: 흐름 분기 추가 + 모달 손실 가중 `λ_flow`(warm-up 0.5 → 1.0 스케줄).
- **D28/D29 — "동결 WM = 예측적 비전 인코더" 레시피의 하이퍼파라미터 명세.** 세계 모델을 co-train 하지 않고 동결한 뒤, **고정 diffusion timestep(t=500)**, **특정 block(15)의 은닉 상태**, **분기 concat(3×3072-dim)**, **Flow Former 압축**, **flow-matching action head(N=4 ODE step, K=10 chunk)** 라는 재현 가능한 구성을 제공. 우리 스택에서 π backbone 을 예측 인코더로 재활용할 때 "어느 layer·어느 timestep 잠재를 뽑나"의 출발점.
- **아키텍처 — 이질 모달은 분기 분리 + JA + per-modality FFN.** Shared FFN 이 systemic collapse 를 낸다는 ablation 은, 여러 모달(비전/깊이/흐름, 나아가 촉각)을 다룰 때 flat 공유 대신 **모달별 FFN + cross-attention(JA)** 을 써야 한다는 P2(D10) 설계 지침을 보강. JA 는 3 layer 마다, zero-init OutProj + `tanh(g)` 게이트(g=1 init)로 saddle-point 회피.
- **실시간 예산 — 세계 모델 순전파가 프레임률 상한.** 정책 헤드(12ms)가 아니라 tri-branch backbone(990ms)이 89.5% 이므로, 세계-모델-기반 정책의 제어 주파수는 backbone 크기로 결정됨. action chunking(K=10) + 병렬 계획으로 planning 0.9Hz → effective 9Hz 로 끌어올리는 패턴이 참고점(단, System0 급 >500Hz 는 불가).

---

## ⚠️ 먼저 검증할 실패 모드

우리 스택(π backbone + Body/Hand expert + 촉각 융합 + System0)으로의 전이 위험을, 싼 점검부터:

1. **(가장 싼 점검) 행동-무조건 예측이 우리 과제를 결정하는가.** 세계 모델이 언어+이미지로만 조건화되므로, in-hand cube rotation(Phase 1) 처럼 같은 시각·지시에서 여러 회전 경로가 가능한 다중-모드 과제에서는 예측 미래가 실제 의도 행동과 어긋날 수 있습니다. 점검: 우리 시연 데이터에서 (동일 초기 관찰, 서로 다른 행동) 쌍의 비율을 세어, 미래가 underdetermined 한 정도를 먼저 정량화.
2. **pseudo-label 깊이·흐름의 우리 도메인 품질.** Depth Anything 3·DPFlow 가 dexterous hand 근접·self-occlusion·반사 물체에서 얼마나 정확한지. 점검: 소량 프레임에 대해 pseudo-depth 를 Sharpa/xhand 근접 장면에서 시각 확인 — 손가락 경계 depth 붕괴 여부.
3. **촉각/힘 부재의 상한.** 순수 시각 4D 로는 접촉 개시·slip·grasp 유지 신호가 없습니다. Hand-over 28.57% 라는 낮은 절대값이 이를 시사. 점검: 본 방법을 촉각 없이 접촉-집약 과제(예: tool trigger)에 붙였을 때 성공률 상한이 우리 요구를 넘는지 pilot.
4. **9Hz 제어의 접촉-집약 적합성.** System0(>500Hz) 은 물론이고 손가락 수준 정밀 조작에도 9Hz + K=10 open-loop 청크가 반응성을 못 맞출 수 있음. 점검: 우리 과제의 접촉 이벤트 시간 스케일(slip 발생~감지 지연)을 9Hz 업데이트 주기와 대조.
5. **단일 FPV 카메라 의존.** 3D scene flow 유도가 단일 카메라 $`\mathbf{K}`$ 에 묶여 있어 multi-cam 공간 grounding(P2/D8) 이 필요한 우리 셋업으로 곧바로 이전되지 않음. 점검: multi-view 를 쓰면 분기별 RoPE·intrinsic 처리가 어떻게 확장되는지 코드 확인.
6. **compute 규모.** Wan-2.2-5B backbone, 254.4M 프레임 사전학습, DeepSpeed ZeRO-2 — 우리가 이 규모 사전학습을 재현할지, 아니면 공개 가중치를 동결 인코더로만 쓸지(더 현실적) 결정 필요. 점검: 공개 HF 체크포인트를 그대로 동결 인코더로 로드해 소량 과제에 붙이는 minimal path 의 성립성부터 확인.

---

## 💡 컨텍스트 제안

- **P5 Tracked Literature 후보.** RynnWorld-4D 는 D30(예측 공간)에 "raw-pixel RGB-DF 생성 + 명시적 3D scene flow" 라는 현재 pin 에 없는 입장을, D29 에 "동결 WM → 역동역학 헤드" 2단계 decoupled 의 강한 사례를 추가합니다. 현재 P5 pin 은 8개 cap 이 꽉 차 있으므로, TesserAct 대비 우위($`\delta_{1}`$ 0.279→0.610, AEPE 제공)를 근거로 **methodology-base 등재** 또는 raw-pixel 브랜치(Ctrl-World) 자리와의 교체를 사람이 검토할 것을 제안합니다.
- **D31 재검토 트리거(제안만).** 본 논문은 **행동-무조건** 세계 모델 + 역동역학이 실세계 dexterous 양손에서 SOTA 를 냄을 보입니다. 이는 D31 의 v1(action-conditioned per-frame)과 §4 anti-topic(action-free 배제)에 대한 반례 성격의 증거이므로, "action-free future-prediction + inverse dynamics" 를 배제 대상이 아니라 비교군으로 승격할지 사람이 판단할 것을 제안합니다.
- context/ 파일은 수정하지 않았습니다.

---

> 💡 base 매핑은 `/implement-design analysis/2607.06559/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
