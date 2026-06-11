# Paper Analysis — Unified Video-Action Joint Denoising for Dexterous Action and Data Generation

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Unified Video-Action Joint Denoising for Dexterous Action and Data Generation |
| 저자 | Dingrui Wang, YuAn Wang, Jinkun Liu, Yue Zhang, Mattia Piccinini, Yu Sun, Johannes Betz (TU Munich · ByteDance · Tsinghua) |
| 링크 | [arXiv:2606.03868](https://arxiv.org/abs/2606.03868) |
| 발행일 / 버전 | 2026-06-02 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-10 |
| 관련 Pillar | P5, P0, P1 |
| 태그 | dexterity, flow-matching, egocentric-data |
| 카탈로그 | models/wam/Donk (ByteDance)/Donk |

---

## 🧭 한 줄 요약 (TL;DR)

기존 World Action Model 은 "관측 조건부 정책" $`p(\mathrm{video},\mathrm{action}\mid\mathrm{text},\mathrm{observation})`$ 로 분포를 좁혀 버리는데, Donk 는 이를 *옵션화된 관측* $`p(\mathrm{video},\mathrm{action}\mid\mathrm{text},\mathrm{optional\ observation})`$ 로 넓혀 **하나의 video diffusion transformer 가 이미지가 있으면 dexterous 정책(TI2VA), 없으면 텍스트만으로 video+MANO 행동 쌍을 찍어내는 데이터 엔진(T2VA)** 으로 동시에 작동하게 만든 통합 joint denoising 모델입니다. OakInk2 에서 hand RMSE·궤적 오차 SOTA 를 달성하면서 Wan 기반 비디오 품질도 유지합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — dexterous manipulation 은 손-물체 접촉, 접촉 타이밍, 물체 운동을 미세하게 맞춰야 하는데, 액션만 예측하는 VLA 는 그 액션이 *장면을 어떻게 바꾸는지*에 대한 감독을 받지 못합니다. 비디오 미래와 손 궤적을 한 모델에서 동시에 생성·정렬하는 것이 과제입니다.
- **기존 접근의 한계** — 현재 WAM 들은 사실상 관측 조건부 정책(TI2VA)으로만 정식화되어, 비디오 파운데이션 모델이 가진 넓은 상호작용 prior 를 "초기 관측이 주어졌을 때"라는 한 단면으로 좁혀 씁니다. 또한 액션 예측을 비디오 생성에 무작정 끼워 넣으면 사전학습된 비디오 토큰 표현을 망가뜨리고, 비디오를 먼저 만든 뒤 액션을 추출하는 post-hoc 파이프라인은 시간적 어긋남·오차 누적을 낳습니다.
- **본 논문의 가설** — 초기 관측은 video-action 생성의 *필수 조건이 아니라 여러 조건 맥락 중 하나*일 뿐이며, 같은 action-aligned 생성 모델이 조건 맥락을 바꿔 정책이자 데이터 생성기로 함께 동작할 수 있다는 것입니다.
- **왜 지금 중요한가** — dexterous 용 paired robot visual-action 궤적은 teleoperation·calibration·정밀 주석 비용이 커 희소한 반면, 대규모 human-object interaction 비디오와 text-conditioned video prior 는 풍부합니다. T2VA 분기는 이 풍부한 prior 를 *구조화된 action-aligned 감독*으로 변환하는 길을 엽니다.

---

## 🧩 핵심 기여

- **T2VA 정식화** — 언어만으로 paired interaction video + 공간 정렬된 hand-action 궤적을 합성하는 text-to-video-action 생성을 dexterous manipulation 에 대해 처음으로 정식화하고, 이를 *텍스트 전용 데이터 엔진*으로 제안합니다.
- **Donk — 통합 joint denoising 모델** — video diffusion transformer 위에서 video token 과 MANO hand-action token 을 flow-matching 으로 *함께* denoise 하여, 관측 조건부 TI2VA 정책 학습과 텍스트 조건부 T2VA 데이터 생성을 한 모델이 모두 지원합니다.
- **Video-Preserving Joint Attention** — 비디오 query 는 비디오 토큰만 보고, action/anchor query 는 전체 시퀀스를 보는 비대칭 마스크로, 사전학습된 Wan 비디오 prior 를 흔들지 않으면서 손 동작을 비디오 롤아웃에 정렬합니다.
- **Anchor-Map Controller** — 초기 hand-camera anchor(첫 프레임 MANO 상태 + 카메라 intrinsics)를 색상 코딩된 MANO 스켈레톤 이미지로 렌더링해, gate 가 0 에서 시작하는 first-frame 주입으로 손의 image-plane 위치·포즈를 명시적으로 제어합니다.
- **실증** — TI2VA 정책으로 OakInk2 에서 최고 hand RMSE(0.238)·wrist 궤적 오차를 얻고 LPIPS 0.2992 의 비디오 충실도를 유지하며, T2VA 데이터 엔진으로도 경쟁력 있는 비디오 품질과 시공간 정렬된 MANO 행동을 같은 학습 레시피로 생성합니다.

---

## 🔑 기술 키워드

- **World Action Model (WAM)** — 비디오 파운데이션 모델 위에 액션 정책을 얹어 미래 시각 관측과 액션을 *함께* 예측하는 계열. Donk 는 WAM 의 정렬된 prior 를 정책뿐 아니라 데이터 생성 공간으로도 재활용합니다.
- **TI2VA / T2VA** — text-image-to-video-action(이미지 조건부 정책) vs text-to-video-action(텍스트 전용 데이터 엔진). 같은 denoiser 의 두 conditioning 모드입니다.
- **Joint video-action denoising** — video latent token 과 action token 을 하나의 transformer 안에서 동시에 denoise 하는 방식. 중간 표현 없이 시공간 정렬을 한 패스에서 보장합니다.
- **Flow matching** — Gaussian noise → 정답까지의 속도장(velocity)을 회귀하는 생성 패러다임. Donk 는 video velocity 와 action velocity 를 함께 예측합니다.
- **MANO** — 손을 저차원 파라미터(포즈+형상)로 표현하는 parametric hand model. Donk 의 action 은 normalized bimanual MANO 궤적입니다.
- **Hand-camera anchor ($`g_0`$)** — 첫 프레임 MANO 상태 $`s_0`$ + 카메라 intrinsics $`K`$. 손 geometry 를 카메라 뷰로 투영하는 기하 스캐폴드입니다.
- **Anchor map** — anchor 를 색상 코딩 MANO 스켈레톤 이미지로 렌더링한 뒤 frozen Wan VAE 로 인코딩한 latent. 손 위치·포즈의 명시적 제어 신호입니다.
- **Video-preserving attention mask** — 비디오 query 가 새로 추가된 action/anchor 토큰을 보지 못하게 막아 사전학습 비디오 prior 를 보존하는 비대칭 마스크.
- **Teacher-prior regularization** — frozen Wan teacher 의 video velocity 를 모방시켜 시각 생성 경로를 안정화하는 항. 이미지 조건이 유지될 때만 적용됩니다.
- **Wan2.2 TI2V-5B** — Donk 의 초기화 백본인 video diffusion transformer. VAE·text encoder·대부분 블록은 freeze 하고 action/anchor 인터페이스와 소수 layer 만 학습합니다.

---

## 🔬 방법론

### 직관

Donk 의 출발점은 "기존 WAM 이 너무 많이 좁혔다"는 분포적 관점입니다. 비디오 파운데이션 모델은 인간-물체 상호작용, 접촉 동역학, 물체 운동에 대한 넓은 prior 를 갖는데, 이걸 "지금 이 장면을 봤을 때 다음 행동"이라는 관측 조건부 정책으로 정식화하면 그 넓은 분포의 한 단면만 쓰게 됩니다. Donk 는 초기 이미지를 *필수가 아니라 옵션*으로 두어, 같은 모델이 이미지가 있으면 정책처럼, 없으면 언어만으로 상호작용 데이터를 찍어내는 엔진처럼 작동하게 만듭니다.

핵심 설계는 비디오와 손 행동을 *같은 미래의 두 시점*으로 보고 한 transformer 안에서 함께 denoise 하는 것입니다. 다만 사전학습된 Wan 비디오 생성기는 매우 비싸고 깨지기 쉬운 자산이라, 액션 토큰을 끼워 넣되 비디오 스트림은 최대한 원래 계산에 가깝게 보존해야 합니다. 그래서 (1) 비디오 query 는 비디오만 보고 action/anchor query 만 전체를 보는 비대칭 attention, (2) gate 가 0 에서 시작하는 anchor 주입, (3) frozen teacher 모방 항 — 세 가지 보존 장치를 둡니다.

마지막 퍼즐은 "텍스트만 주면 손이 화면 어디에 어떤 포즈로 있어야 하는가"입니다. 언어·이미지 조건만으로는 손의 image-plane 위치 제어가 약하기 때문에, 첫 프레임 hand-camera anchor 를 색상 코딩 MANO 스켈레톤으로 렌더링해 명시적 기하 신호로 주입합니다. T2VA 에서는 관측이 없으니 가벼운 text-conditioned initializer 가 그럴듯한 초기 hand-camera 상태를 샘플해 이 anchor 를 채웁니다.

### 아키텍처

![Figure 2 — Unified training framework](https://arxiv.org/html/2606.03868/x2.png)

> "Figure 2: Unified training framework." (§3)
> (이 그림이 TI2VA(이미지 조건)와 T2VA(텍스트 전용)가 동일한 hand-camera anchor 인터페이스와 공유 denoiser 를 거치는 통합 학습 구조를 시각화합니다.)

**통합 분포.** 언어 $`c`$, 비디오 $`V_{0:T}`$, 정렬된 미래 손 궤적 $`A_{1:T}`$ (고정 horizon $`T>0`$) 에 대해 Donk 는 단일 조건부 분포를 모델링합니다.

> "Donk models a unified conditional video-action distribution" (§3.1)
> (시각 conditioning 모드 $`I_{\star}`$ 와 초기 hand-camera anchor $`g_0`$ 를 조건으로 두는 하나의 생성 분포로 정책과 데이터 엔진을 동시에 담습니다.)

$$p_{\theta}(V_{0:T},A_{1:T}\mid c,I_{\star},g_{0}),\qquad I_{\star}\in\{I_{0},\varnothing\}$$

여기서 $`I_{\star}`$ 는 시각 conditioning 모드(첫 이미지 $`I_0`$ 사용 또는 $`\varnothing`$)를, $`g_0`$ 는 첫 프레임 MANO 상태와 카메라 intrinsics 로 손 geometry 를 카메라 뷰로 투영하는 방법을 결정합니다.

**TI2VA 정책 모드.** 첫 이미지가 현재 장면을 grounding 하고 미래 롤아웃을 예측합니다.

$$p_{\theta}^{\mathrm{policy}}(V_{1:T},A_{1:T}\mid c,I_{0},g_{0})\triangleq p_{\theta}(V_{1:T},A_{1:T}\mid c,I_{\star}=I_{0},g_{0})$$

**T2VA 데이터 엔진 모드.** 초기 이미지가 없어, 언어와 초기화된 anchor $`\tilde{g}_0`$ 만으로 전체 롤아웃을 생성합니다.

$$p_{\theta}^{\mathrm{engine}}(V_{0:T},A_{1:T}\mid c,\tilde{g}_{0})\triangleq p_{\theta}(V_{0:T},A_{1:T}\mid c,I_{\star}=\varnothing,\tilde{g}_{0})$$

> "Here $`\tilde{g}_{0}`$ provides only a plausible first-frame geometric scaffold; it is not a future action plan or trajectory-level condition." (§3.1)
> ($`\tilde{g}_0`$ 는 첫 프레임 기하 스캐폴드일 뿐 미래 행동 계획이 아니므로, 데이터 엔진이 답을 미리 보고 베끼는 것이 아니라는 점을 못 박습니다.)

**잠재 공간 표현.** 비디오는 사전학습된 Wan VAE 잠재공간으로 인코딩하고, 액션은 normalized 연속 bimanual MANO 궤적으로 두며 invalid/missing 손은 학습 중 마스킹합니다.

$$x^{\star}=\mathcal{E}(V_{0:T})$$

**토큰화와 conditioning.** Wan2.2 TI2V-5B 로 초기화한 transformer denoiser 를 쓰고, Wan stem 이 video latent 를 patchify 한 video token 에 더해 경량 action·anchor encoder 로 미래 MANO 궤적과 초기 anchor 를 임베딩합니다.

$$z=[z^{\mathrm{video}},z^{\mathrm{action}},z^{\mathrm{anchor}}]$$

원래 Wan head 가 비디오를, 경량 action head 가 MANO 액션을 예측합니다. 이미지 conditioning 은 잠재공간에서 주입됩니다 — $`I_{\star}=I_0`$ 일 때 VAE 인코딩된 첫 이미지가 첫 video latent 프레임을 대체하고 timestep 0 을 부여받으며, $`I_{\star}=\varnothing`$ 이면 이 대체가 생략됩니다.

> "During training, we drop $`I_{0}`$ with probability $`0.30`$, so both conditioning modes share the same backbone, token layout, and objectives." (§3.2)
> (학습 중 30% 확률로 첫 이미지를 드롭해 정책 모드와 엔진 모드가 같은 백본·토큰 레이아웃·목표를 공유하도록 만드는 것이 두 모드 통합의 실질적 트릭입니다.)

**Video-Preserving Joint Attention.**

![Figure 3 — Video-preserving attention mask](https://arxiv.org/html/2606.03868/x3.png)

> "Figure 3: Video-preserving attention mask." (§3.2)
> (비디오 query 는 비디오 토큰만, action/anchor query 는 전체 시퀀스를 보는 비대칭 마스크 패턴을 시각화합니다.)

> "video queries attend only to video tokens, whereas action and anchor queries attend to the full sequence." (§3.2)
> (완전 joint attention 은 비디오 토큰이 새 action/anchor 토큰까지 attend 하게 해 사전학습 비디오 prior 를 교란할 수 있어, 시각 스트림을 Wan 원래 계산에 가깝게 유지하는 비대칭 설계를 택합니다.)

**Anchor-Map Controller.** 언어·이미지 conditioning 만으로는 손의 image-plane 위치·포즈 제어가 약하므로, anchor $`g_0=(s_0,K)`$ 를 색상 코딩 MANO 스켈레톤 이미지 $`M_0=\mathcal{R}(g_0)`$ 로 렌더링한 뒤 frozen Wan VAE 로 latent anchor map $`m_0=\mathcal{E}(M_0)`$ 을 얻습니다. 경량 adapter $`G_{\mathrm{anc}}`$ 가 patchify 된 anchor latent 를 Wan token 공간으로 사상하고, 선택된 layer $`\ell\in\mathcal{S}`$ 마다 layer-specific MLP 가 anchor hint 를 만듭니다.

$$C=G_{\mathrm{anc}}(\mathrm{Patch}(m_{0})),\qquad H_{\ell}=\mathrm{MLP}_{\ell}(C),\quad\ell\in\mathcal{S}$$

이 hint 는 gated first-frame 주입으로 *첫 프레임 비디오 토큰에만* 더해집니다.

$$z^{\mathrm{video}}_{\ell,0}\leftarrow z^{\mathrm{video}}_{\ell,0}+\gamma_{\ell}H_{\ell},\qquad z^{\mathrm{video}}_{\ell,t>0}\leftarrow z^{\mathrm{video}}_{\ell,t>0}$$

> "The gates $`\gamma_{\ell}`$ are initialized to zero, so training starts from the pretrained Wan behavior." (§3.2)
> (gate 를 0 으로 초기화해 학습이 사전학습 Wan 동작에서 출발하도록 하고, anchor 가 초기 조건일 뿐이므로 hint 를 첫 프레임에만 적용하는 보존-우선 설계입니다.)

T2VA 에서는 관측이 없으므로 경량 text-conditioned initializer 가 첫 프레임 hand-camera 상태의 경험 분포를 학습해 $`\tilde{g}_0`$ 를 instantiate 하고, 이는 오직 초기 anchor map $`M_0=\mathcal{R}(\tilde{g}_0)`$ 렌더링에만 쓰입니다.

### 학습 목표 / 손실

denoiser 는 video·action velocity $`(\hat{v}_{x},\hat{v}_{a})`$ 를 예측하고 flow-matching target $`(v_{x},v_{a})`$ 로 감독됩니다. 주 목표는 video-flow matching 과 masked action-flow matching 입니다.

$$\mathcal{L}_{\mathrm{video}}=\|\hat{v}_{x}-v_{x}\|_{2}^{2},\qquad\mathcal{L}_{\mathrm{action}}=\frac{\|M_{a}\odot(\hat{v}_{a}-v_{a})\|_{2}^{2}}{\max(\sum M_{a},1)}$$

여기서 $`M_a`$ 는 invalid hand 차원을 마스킹합니다. 손-물체 상호작용 영역을 강조하기 위해, rendered hand 영역 주변의 video-flow 오차에 가중치를 주는 hand-focused video loss $`\mathcal{L}_{\mathrm{gaze}}`$ 를 추가로 씁니다.

또한 frozen Wan teacher prior 로 시각 생성 경로를 안정화합니다. teacher 는 같은 video latent·text 조건을 받아 video velocity $`\hat{v}_{x}^{\,\mathrm{tea}}`$ 를 예측합니다.

$$\mathcal{L}_{\mathrm{prior}}=\|\hat{v}_{x}-\hat{v}_{x}^{\,\mathrm{tea}}\|_{2}^{2}$$

> "This term is applied only when the image condition is kept, preventing the text-only branch from imitating an image-conditioned teacher without access to the image." (§3.3)
> (teacher 항을 이미지 조건이 유지될 때로 한정해, 이미지를 못 보는 텍스트 전용 분기가 이미지 조건부 teacher 를 억지로 흉내 내지 않게 막습니다.)

전체 목표는 가중합입니다.

$$\mathcal{L}_{\mathrm{Donk}}=\lambda_{v}\left(\mathcal{L}_{\mathrm{video}}+\lambda_{g}\mathcal{L}_{\mathrm{gaze}}\right)+\lambda_{a}\mathcal{L}_{\mathrm{action}}+\lambda_{p}\mathcal{L}_{\mathrm{prior}}$$

action·anchor 인터페이스(anchor-map adapter 포함)는 이 목표로 end-to-end 학습되며, T2VA 용 text-conditioned initializer 는 첫 프레임 기하 스캐폴드 제공만을 위해 별도로 학습됩니다.

### 학습 셋업

- **데이터셋** — VITRA-1M (Li et al. 2025a).
- **하드웨어 / 분산** — 64× NVIDIA Hopper GPU (VRAM 96GB), PyTorch FSDP2. GPU 당 1 clip 처리, effective batch size 64 clips.
- **정밀도 / 옵티마이저** — bfloat16, AdamW, constant learning rate $`2\times 10^{-5}`$, $`(\beta_1,\beta_2)=(0.9,0.999)`$, $`\epsilon=10^{-8}`$, weight decay 0.01, gradient clipping 1.0.
- **freeze 범위** — text encoder · VAE · teacher · 대부분 Wan 블록은 freeze 하고, action·anchor 인터페이스, anchor-map adapter, action head, 소수 Wan layer 만 학습합니다.

---

## 📊 실험 설정과 결과

### TI2VA 액션 정확도 (OakInk2)

OakInk2 first-person view 벤치마크에서 모든 방법이 예제당 10 futures 를 샘플하고, EgoMAN 을 따라 ADE·FDE·DTW(미터) + wrist rotation error ROT(도) + hand RMSE 를 best-of-$`K`$ ($`K\in\{5,10\}`$) 로 보고합니다(모두 lower-is-better).

| Method | Hand RMSE↓ | ADE K5↓ | ADE K10↓ | FDE K5↓ | FDE K10↓ | DTW-S K5↓ | DTW-S K10↓ | DTW-L K5↓ | DTW-L K10↓ | ROT K5↓ | ROT K10↓ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| VITRA | 0.444 | 0.067 | 0.065 | 0.108 | 0.105 | 0.062 | 0.060 | 0.039 | 0.038 | **15.15** | **14.64** |
| Being-H0-1B | 0.587 | 0.118 | 0.107 | 0.131 | 0.120 | 0.118 | 0.107 | 0.098 | 0.090 | 40.52 | 38.18 |
| Being-H0-8B | 0.615 | 0.082 | 0.075 | 0.098 | 0.092 | 0.081 | 0.074 | 0.064 | 0.057 | 31.16 | 29.98 |
| DreamZero-alike | 0.262 | 0.062 | 0.057 | 0.100 | 0.094 | 0.059 | 0.054 | 0.040 | 0.037 | 20.48 | 19.00 |
| **Donk-TI2VA** | **0.238** | **0.055** | **0.049** | **0.090** | **0.079** | **0.052** | **0.046** | **0.032** | **0.029** | 16.05 | 14.95 |

> "Donk-TI2VA gives the best hand pose and wrist-translation results among the compared methods. … VITRA is slightly better on wrist rotation, but Donk remains close while being substantially stronger on position and finger pose." (§4.1, Table 1)
> (위치(ADE/FDE)·DTW 두 변형 모두에서 일관된 우위는 단순 endpoint 가 아니라 전체 궤적의 공간 추적이 좋아졌음을 뜻하며, ROT 에서만 VITRA(15.15/14.64)에 근소하게 뒤집니다.)

### Conditioning ablation (Table 2)

| Variant | Gaze | State | Hand RMSE↓ | ADE K10↓ | ROT K10↓ |
|---|---|---|---|---|---|
| Donk-TI2VA (full) | ✓ | ✓ | 0.238 | 0.049 | 14.95 |
| Donk-TI2VA (wo Gaze) | ✗ | ✓ | 0.258 | 0.053 | 16.21 |
| Donk-TI2VA (base) | ✗ | ✗ | 0.262 | 0.057 | 19.00 |

> "State conditioning alone already improves the base model on all metrics. Adding the hand-focused cue gives the full model, which further improves hand RMSE, trajectory error, and rotation error." (§4.1, Table 2)
> (base→+State 의 이득(0.262→0.258 RMSE, 19.00→16.21 ROT)이 +Gaze 의 추가 이득(→0.238, →14.95)보다 큽니다 — state expert 가 주된 레버, gaze 모듈은 작지만 일관된 보조 이득. base 행이 Table 1 의 DreamZero-alike 와 동일 수치라는 점은 Donk 의 무-조건 변형이 그 baseline 과 같은 출발점임을 시사합니다.)

### TI2VA 비디오 품질 (EgoDex 프로토콜)

LOME 평가(EgoDex 기반, 1000 samples, 17 frames, 832×480)에서 프레임 충실도(PSNR/SSIM/LPIPS)·의미(CLIP-I/CLIP-S)·시간(tLPIPS)·분포(FVD)를 봅니다.

| Method | PSNR↑ | SSIM↑ | LPIPS↓ | CLIP-I↑ | CLIP-S↑ | tLPIPS↓ | FVD↓ |
|---|---|---|---|---|---|---|---|
| Wan2.2-TI2V-5B | 19.50 | 0.7855 | 0.3061 | 0.9119 | 0.2004 | 0.0429 | 81.87 |
| Wan2.1-I2V-14B | 19.47 | 0.7742 | 0.3252 | 0.9090 | 0.2053 | 0.0472 | **68.97** |
| Wan2.1-VACE-14B | 17.16 | 0.7220 | 0.4067 | 0.8551 | **0.2187** | **0.0197** | 103.85 |
| **Donk-TI2VA** | **19.84** | **0.7908** | **0.2992** | **0.9172** | 0.1982 | 0.0340 | 75.13 |

> "Donk-TI2VA has the best PSNR, SSIM, LPIPS, and CLIP-I among the matched runs. Pure video baselines still lead on some video-only metrics: Wan2.1-I2V has the lowest FVD, and Wan2.1-VACE has the best CLIP-S and tLPIPS." (§4.2, Table 3)
> (액션 스트림을 끼워도 비디오 측이 저하되지 않는다는 핵심 주장 — 다만 14B 순수 비디오 baseline 이 FVD(68.97)·CLIP-S(0.2187)·tLPIPS(0.0197) 일부 비디오 전용 지표는 여전히 앞섭니다. Donk 는 5B 초기화임을 감안하면 frame fidelity 4 개를 가져간 것이 핵심 이득입니다.)

![Figure 4 — TI2VA alignment examples](https://arxiv.org/html/2606.03868/x4.png)

> "Figure 4: TI2VA alignment examples. Example (a) features part of the hand is missing at the beginning, while example (b) features hand occlusion and fluid interaction. Example (c) features height change and tool interaction." (§4.2)
> (부분 가림·유체 상호작용·도구 조작 같은 까다로운 상황에서도 예측 액션이 손 운동을 따라가며 안정적임을 보이는 정성 예시입니다.)

### T2VA 시각·의미 품질 (Table 4)

open video baseline 은 paired action 을 생성하지 못해 비디오 지표로만 비교합니다. VLM judge 는 100 EgoDex 샘플의 video·instruction 을 VLM 에 보내 instruction-following 정렬을 0–5 로 채점한 값입니다.

| Method | Input | FVD↓ | VLM judge↑ | CLIP-S↑ | tLPIPS↓ |
|---|---|---|---|---|---|
| Wan2.2-5B-I2V | text | 306.2 | 1.59 | 0.2508 | **0.0147** |
| **Donk-T2VA** | text | **191.1** | **2.37** | **0.2572** | 0.0215 |

> "Donk-T2VA maintains competitive visual and semantic quality compared to the off-the-shelf model. It lowers FVD while improving the VLM judge score" (§4.3, Table 4)
> (텍스트만 주어 paired video-action 을 샘플하는 데이터 엔진 모드에서도 FVD(306.2→191.1)·VLM judge(1.59→2.37)·CLIP-S 가 개선됩니다 — tLPIPS 는 다소 나빠져 시간적 flicker 측면의 trade-off 가 보입니다.)

![Figure 5 — T2VA rollouts with text only](https://arxiv.org/html/2606.03868/x5.png)

> "Figure 5: T2VA rollouts with only text as input." (§4.3)
> (실험실 manipulation 분포 밖의 야외 동물 상호작용·화재 비상 시나리오 등도 텍스트만으로 paired 롤아웃을 샘플할 수 있음을 보이는, 데이터 엔진의 일반화 정성 예시입니다.)

---

## ⚖️ 한계

- **5B vs 14B 비디오 전용 baseline 의 격차** — 저자 스스로 Wan2.1-I2V(FVD 68.97)·VACE(CLIP-S/tLPIPS)가 일부 비디오 전용 지표에서 앞선다고 밝힙니다. Donk 는 5B 초기화라 분포-수준 FVD·시간적 매끄러움에서 더 큰 모델에 밀리며, action head 추가가 시간 일관성(tLPIPS)에 일부 비용을 지운다는 신호가 T2VA(0.0147→0.0215)에서 보입니다.
- **VLM judge 의 신뢰도** — T2VA 의 핵심 품질 지표가 "VLM 에게 0–5 채점" 인데 샘플 100 개에 불과하고, judge 모델·프롬프트가 명시되지 않아 절대 점수(2.37/5)의 의미와 재현성이 약합니다. instruction-following 을 LPIPS/FVD 같은 reference 기반 지표로 검증하지 못한 영역입니다.
- **데이터 엔진의 순환 검증 부재** — T2VA 의 진짜 가치는 "생성한 paired video-action 으로 정책을 학습했을 때 성능 향상" 인데, 본 논문은 생성물의 시각·의미 품질만 보고할 뿐 *생성 데이터로 downstream 정책을 학습한 closed-loop 결과가 없습니다*. 데이터 엔진 주장의 가장 결정적 증거가 비어 있습니다.
- **초기화 initializer 의 분포 편향** — T2VA 의 $`\tilde{g}_0`$ 는 학습 데이터(VITRA-1M)의 첫 프레임 hand-camera 경험 분포에서 샘플되므로, 분포 밖 프롬프트(Fig. 5 의 야외/비상)에서는 그럴듯하지만 물리적으로 부정합한 초기 손 포즈를 줄 위험이 있고 이에 대한 정량 평가가 없습니다.
- **real-robot 실행 부재** — 모든 평가가 offline 궤적 오차·비디오 지표이고 실제 dexterous hand 에서의 실행/접촉 성공률이 없습니다. ADE/FDE(미터) 개선이 실제 grasp/접촉 성공으로 전이되는지는 미검증입니다.
- **호환 baseline 의 작은 풀** — OakInk2 비교군이 VITRA·Being-H0·DreamZero-alike 4 종으로 좁고, "DreamZero-alike" 는 재구현 추정 표기라 정확한 비교 기준이 불투명합니다.

---

## ♻️ 재현성

- **코드 / 가중치** — arXiv abstract·HTML 어디에도 GitHub·HuggingFace·프로젝트 페이지 링크가 없습니다 (분석 시점 미공개로 추정).
- **데이터** — 학습은 VITRA-1M (Li et al. 2025a) 으로 외부 데이터셋. 평가는 OakInk2 (first-person view) + LOME/EgoDex 프로토콜 (1000 samples, 17 frames, 832×480) 으로 공개 자원에 의존합니다.
- **백본** — Wan2.2 TI2V-5B 초기화. Wan VAE·text encoder·teacher 는 frozen.
- **하드웨어** — 64× NVIDIA Hopper 96GB, FSDP2. 재현에 대규모 자원이 필요합니다.
- **하이퍼파라미터** — 옵티마이저·LR·batch 등 학습 셋업은 명시되나, loss 가중치 $`(\lambda_v,\lambda_g,\lambda_a,\lambda_p)`$, anchor 주입 layer 집합 $`\mathcal{S}`$, horizon $`T`$, MANO 정규화 통계는 본문에 수치가 없습니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P5(World Model) — 주 pillar.** Donk 는 video+action 을 함께 예측하는 전형적 WAM 이며 P5 의 거의 모든 Decision 을 정면으로 건드립니다. **D28**(world-model role: latent dynamics prior + future-prediction auxiliary)에 대해 Donk 는 *role 을 확장* — 정책일 뿐 아니라 **data-augmentation/데이터 엔진**(D28 에서 "tracked" 로 적힌 rollout synthesis)을 first-class 로 승격합니다. **D29**(integration architecture)에서 Donk 는 핀 WorldVLA(2506.21539)와 같은 *fully unified* 단일 모델 계열이되, autoregressive 가 아니라 **single-stream joint denoising** 으로 D29 의 "attention-mask interference risk" 를 video-preserving mask 로 직접 다룹니다. **D31**(action conditioning)은 per-frame action-conditioned 라 v1 과 정렬되나, **D30**(prediction space)에서는 Donk 가 **raw-pixel video 생성**이라 v1 의 "latent/3D-flow 우선, raw-pixel deferred" 와 *정면 충돌*합니다 — Donk 는 v1 이 보류한 raw-pixel 분기의 강력한 사례입니다. **D32**(egocentric hand-object)는 MANO bimanual + egocentric VITRA/EgoDex 로 정확히 일치합니다.
- **P0(VLA Datasets & Benchmarks) — 부 pillar.** T2VA 데이터 엔진은 **D24**(priority data axis: egocentric human video–centric)의 논리를 *생성 측*으로 확장합니다 — 비싼 paired robot 궤적 대신 풍부한 human-object 비디오 prior 를 action-aligned 감독으로 변환. 평가에 P0 top 핀 **EgoDex**(2505.11709)와 **LOME** 프로토콜을 직접 사용합니다.
- **P1(Heterogeneous Body/Hand Action Expert) — 약한 접점.** action 을 별도 head + 비대칭 attention 으로 분리한 점은 P1 의 "강하게 분리된 action latent" 와 느슨히 닿지만, Donk 는 body/hand 해부학적 분리가 아니라 video/action 분리라 P1 의 핵심 주장과는 거리가 있습니다.
- **Identity 긴장/지지** — Identity 의 "VLA-level 에서 dexterity tackle" 과 P5 의 "raw-pixel 보다 latent/3D-flow" 기조에 대해, Donk 는 *raw-pixel WAM 도 dexterous 행동 정확도를 끌어올릴 수 있다*는 반례적 증거라 D30 v1 가정을 시험합니다.
- **경쟁자 함의** — P5 핀 중 WorldVLA(통합 VLA+WM), Being-H0.7(latent), LOME(eval 프로토콜로 본 논문이 차용), 그리고 baseline 으로 등장한 VITRA·Being-H0 와 직접 경쟁/비교 관계입니다.

---

## ✨ 핀 논문 대비 델타

- **vs WorldVLA(2605 P5 핀, D29 대안)** — WorldVLA 는 autoregressive 로 action·image 를 *상호* 예측하며 attention-mask 로 간섭을 푸는데, Donk 는 autoregressive 가 아니라 **flow-matching single-stream joint denoising** 으로 같은 통합 목표를 달성하고, mask 를 "비디오 prior 보존"(video-preserving) 방향으로 비대칭 설계합니다. 진정 새로운 점은 **하나의 conditioning 스위치(이미지 drop 0.30)로 정책↔데이터 엔진을 전환**하는 정식화입니다.
- **vs Being-H0.7(2605.00078 P5 핀, D30 latent)** — Being-H0.7 는 *픽셀을 안 만들고* latent 정렬로 비용을 떼는 반대 방향 베팅인데, Donk 는 정확히 그 반대로 **raw-pixel 비디오를 명시적으로 생성**하면서 그 생성물 자체를 데이터로 재활용합니다 — "픽셀이 비싸다"는 Being-H0.7 의 전제를 데이터 엔진 유틸리티로 상쇄하려는 시도입니다.
- **vs LOME(2603.27449 P5 핀, D31/D32)** — LOME 은 action-conditioned egocentric WM 인데, 본 논문은 LOME 을 *평가 프로토콜로 차용*(EgoDex 기반 LOME evaluation)하면서, 생성 측에서 paired action 까지 내는 점에서 한 발 더 나갑니다.
- **vs DexWM(2512.13644 P5 top 핀)** — DexWM 은 finger-keypoint + hand-consistency 예측의 hand-object WM 인데, Donk 는 keypoint 가 아니라 **full MANO bimanual 궤적**을 video 와 동시 생성하고 anchor-map 으로 image-plane geometry 를 명시 제어한다는 점이 다릅니다.

---

## ⚙️ 의사결정 함의

- **D30(prediction space) 재검토 트리거** — 우리 v1 은 raw-pixel 을 cost 로 보류했지만, Donk 는 raw-pixel WAM 이 hand RMSE 0.444→0.238 수준 이득을 줄 수 있음을 보입니다. 다만 *데이터 엔진으로서의 closed-loop 이득*은 미검증이므로, raw-pixel 채택이 아니라 **"latent vs raw-pixel" 비교 실험의 우선순위를 올리는** 정도가 합리적 함의입니다.
- **데이터 파이프라인 — T2VA 합성 데이터 옵션** — P0/P4 의 corpus 구성에 "text→paired video+MANO 합성" 분기를 *후보*로 추가할 수 있습니다. 구체 레버: 생성 데이터의 비율(real:synthetic mix), 그리고 합성 궤적의 품질 게이트로 `VLM judge ≥ θ` / `FVD ≤ θ` 같은 필터 임계값.
- **action 표현 — MANO bimanual** — Donk 는 action 을 normalized continuous bimanual MANO 로 두고 invalid 손을 $`M_a`$ 로 마스킹합니다. 우리 stack(Sharpa/xhand)은 MANO 가 아니라 관절각 공간이라, MANO→관절각 retarget 또는 MANO 를 중간 표현으로 둘지의 결정이 선행되어야 합니다.
- **보존 장치 차용** — video-preserving attention mask + zero-init gated 주입 + frozen teacher prior 라는 3 종 보존 레시피는, 우리 P4 의 prior-preservation(D20) 관점에서 "사전학습 백본에 새 modality head 를 붙일 때의 표준 안전장치" 로 직접 차용 가능한 구체 패턴입니다 (loss 항 $`\mathcal{L}_{\mathrm{prior}}`$, gate $`\gamma_\ell=0`$ 초기화).

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 체크) 코드·가중치 미공개** — 분석 시점 공개 repo 가 없어 재현 비용이 큽니다. 가장 먼저 GitHub/HF 공개 여부와 VITRA-1M 접근 가능성을 확인해야 합니다. 미공개면 우리 차용은 *논문 레시피 재구현* 수준이 됩니다.
- **MANO ↔ 우리 hand embodiment 불일치** — Donk action 공간은 MANO(인간 손 파라미터)인데 Sharpa(22-DOF)/xhand 는 관절각 공간입니다. MANO 궤적이 우리 hand 로 retarget 될 때 손가락 DOF·운동학 차이로 접촉 정밀도가 깨질 수 있어, retarget 오차를 먼저 정량화해야 합니다.
- **데이터 엔진 유틸리티의 미검증** — "생성 데이터로 정책 성능이 오른다"는 핵심 주장의 closed-loop 증거가 논문에 없습니다. 우리가 T2VA 합성 데이터를 도입하기 전에, 소규모 합성→정책 학습 ablation 으로 *실제로 downstream 이득이 있는지*를 먼저 확인해야 합니다 (없으면 비싼 비디오 생성 파이프라인이 무의미).
- **raw-pixel 비용** — 64× Hopper 96GB 학습 규모는 우리 자원과 큰 격차입니다. raw-pixel WAM 의 학습·추론 비용이 dexterous 정책 deployment latency 예산을 초과할 위험이 있어, 추론 시 비디오 생성을 생략·축소(Being-H0.7 식)할 수 있는지 검토가 필요합니다.
- **first-person/MANO 평가의 전이성** — OakInk2 first-person + EgoDex 는 인간 ego 도메인입니다. ADE/FDE(미터) 개선이 우리 로봇 hand 의 실제 grasp/접촉 성공으로 전이되는지 sim 또는 real 에서 별도 검증이 필요합니다.

---

## 💡 컨텍스트 제안

- **P5 §5 Tracked Literature — 핀 후보로 검토.** Donk 는 "통합 video-action WAM + 데이터 엔진" 이라는 새 축(D28 role 확장 + D30 raw-pixel 분기 + D29 non-AR 통합)을 동시에 건드려, 현재 raw-pixel 분기를 대표하는 핀이 Ctrl-World 뿐인 상황에서 **dexterous-특화 raw-pixel WAM 의 데이터-엔진 사례**로 추가 가치가 있습니다. 하드 캡 8 을 감안해 *교체 후보*로 사람에게 판단을 넘깁니다.
- **D28 의 "data-augmentation(rollout synthesis) tracked" 항목 격상 검토.** Donk 는 이 tracked 항목을 모델의 *first-class 두 번째 역할*로 승격한 첫 dexterous 사례라, D28 v1 문구에서 data-augmentation 의 위상을 재검토할 근거가 됩니다.
- (context/ 파일은 수정하지 않았습니다 — 위는 제안일 뿐입니다.)

---

> 💡 base 매핑은 `/implement-design analysis/2606.03868/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
