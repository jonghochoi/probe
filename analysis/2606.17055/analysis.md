# Paper Analysis — T-Rex: Tactile-Reactive Dexterous Manipulation

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | T-Rex: Tactile-Reactive Dexterous Manipulation |
| 저자 | Dantong Niu, Zhuoyang Liu, Zekai Wang 외 (UC Berkeley · NVIDIA · Stanford · Panasonic · La Sapienza · ItalAI) — Fei-Fei Li, Ken Goldberg, Jitendra Malik, Pieter Abbeel, Yuke Zhu, Danfei Xu, Jim Fan, Trevor Darrell 등 |
| 링크 | [arXiv:2606.17055](https://arxiv.org/abs/2606.17055) · [Website](https://tactile-rex.github.io/) |
| 발행일 / 버전 | 2026-06-15 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-16 |
| 관련 Pillar | P1, P2, P4, P0, P5 |
| 태그 | tactile, dexterity, vla-arch |
| 카탈로그 | dataset/robot/T-Rex, models/vla/Standalone/T-Rex |

---

## 🧭 한 줄 요약 (TL;DR)

T-Rex 는 저주파 visuomotor 계획과 고주파 촉각 반응을 하나의 **variable-rate Mixture-of-Transformer-Experts(MoT)** 안에서 비동기 cascaded flow matching 으로 분리하고, **per-finger 시공간 촉각 VQ-VAE 인코더** + **100시간 촉각 동기화 데이터셋** + 3단계 학습 레시피로 12개 contact-rich dexterous 태스크에서 최강 baseline 대비 평균 성공률을 30%p 이상 끌어올린 촉각 반응형 VLA 입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 카드 슬롯 삽입·자물쇠 열기처럼 인간에겐 쉬운 contact-rich 조작은 **즉각적 closed-loop 촉각 반응(tactile-reactive)** 을 요구하지만, 현행 VLA 는 비전 기반 제어 루프 속도로는 이 반응을 따라가지 못합니다.
- **기존 접근의 한계 (데이터)** — 정책 사전학습용 촉각 데이터가 희소해, 대규모 사전학습 패러다임은 사실상 vision-only 이고 force 변화·micro-slip·국소 변형 같은 물리 신호를 놓칩니다. 동기화된 visuo-tactile 데이터를 scratch 로 모으는 것은 비용이 금지적입니다.
- **기존 접근의 한계 (구조)** — 촉각 반응 제어는 고주파를 요구하나 표준 VLM backbone 은 저주파로 동작하는 **frequency mismatch** 가 있습니다. 기존 dual-system 은 빠른 motor 와 인지 reasoning 을 완전히 분리해 버리고, variable-rate diffusion policy 는 parallel-gripper 의 task-specific imitation 에 갇혀 있습니다.
- **본 논문의 가설** — 촉각 능력은 사전학습 단계가 아니라 전용 **mid-training** 단계에서 효율적으로 습득될 수 있으며, 저주파 action expert 와 고주파 tactile expert 를 **하나의 통합 foundation model** 안에서 비동기로 결합하면 기존 VLA 역량을 희생하지 않고 촉각 반응을 더할 수 있습니다.
- **왜 지금 중요한가** — 대규모 human egocentric 사전학습(EgoScale)으로 visuomotor prior 는 확보됐으나, 정밀 force 제어·deformable object 조작에서 여전히 실패합니다. 표준화된 촉각 반응 벤치마크와 데이터의 부재가 진전을 막아 왔고, T-Rex 가 그 셋을 동시에 채웁니다.

---

## 🧩 핵심 기여

- **T-Rex Dataset** — 207개 일상 물체 × 22개 motor primitive 를 조합한 **100시간 양손 dexterous 촉각 동기화 teleoperation 데이터셋**(7,755 에피소드, MIT 라이선스 공개 예정). task-specific 데모가 아니라 verb-noun 조합 기반 **compositional motor primitive** 로 설계해 데이터 효율을 높였습니다.
- **T-Rex Model** — 저주파 action expert + 고주파 tactile expert 로 제어를 분해한 **variable-rate MoT** backbone. 시공간 촉각 VQ-VAE 인코더가 force/contact 를 compact representation 으로 압축합니다.
- **Asynchronous Tactile-Reactive Cascaded Flow Matching** — flow-matching trajectory 를 고정 timestep $`\tau_{\mathrm{split}}`$ 에서 쪼개 action expert(상단 구간)와 tactile expert(하단 구간)가 동일 target 을 disjoint 구간에서 회귀, 무거운 visual network 를 우회한 고주파 refinement 를 실현합니다.
- **3-stage 학습 레시피** — 대규모 human egocentric 사전학습 → 촉각 grounded robot mid-training → skill-specific post-training 으로 human prior 를 robot 실행 가능 contact dynamics 로 점진 전이합니다.
- **실세계 벤치마크** — insertion·deformation·force-sensitive·bimanual 을 망라하는 **12개 contact-rich dexterous 태스크**. T-Rex 가 평균 성공률 65% 로 최강 baseline(EgoScale 35%) 대비 30%p 이상 우위.

---

## 🔑 기술 키워드

- **Tactile-Reactive Control** — 촉각 신호에 대한 즉각적 closed-loop 모터 반응. 비전 제어 루프보다 훨씬 빠른, "손가락이 미끄러짐을 느끼고 0.1초 안에 쥐는 힘을 고치는" 수준의 반응 제어.
- **Mixture-of-Transformer-Experts (MoT)** — 모달리티/역할별로 분리된 transformer expert 들이 공유 attention 으로 묶인 backbone. 여기선 latent / action / tactile 세 expert 가 한 몸을 이룹니다.
- **Variable-Rate Architecture** — 한 정책 안에서 expert 마다 다른 호출 빈도(action 은 chunk 당 1회, tactile 은 chunk 내 여러 offset)로 도는 구조. 저주파 계획 + 고주파 반응을 한 모델에 공존시키는 장치.
- **Cascaded Flow Matching** — flow-matching denoising 궤적을 한 점에서 잘라 두 네트워크가 앞·뒤 구간을 이어받아 적분하는 방식. "초벌 denoising 은 큰 모델, 마무리는 작고 빠른 모델" 의 직렬 분담.
- **Tactile VQ-VAE** — 손가락별 force 시계열을 학습된 codebook 의 이산 토큰으로 양자화하는 encoder. 센서 drift 에 강한 "촉각 단어장(vocabulary)" 을 만들어 고주파 noise 를 압축.
- **Deformation Map** — 지문 패드의 국소 피부 변위장을 담은 단일채널 공간 이미지. force 벡터가 잃는 edge·slip·shear 같은 contact geometry 를 보존하는 촉각 "사진".
- **Mid-training** — 사전학습과 task 미세조정 사이에 끼워, 사전학습이 못 본 모달리티(촉각)·실행 dynamics 를 대규모로 정렬시키는 중간 단계.
- **Egocentric Human Pre-training** — 1인칭 human 비디오(EgoScale, 22,889시간)에서 retargeted 손/팔 모션으로 visuomotor prior 를 distill 하는 사전학습.
- **KV-cache Reuse (asynchronous)** — slow expert 가 계산한 visual-language key/value 를 캐시해 fast tick 에서 재사용, 비전 타워 재실행 없이 촉각만으로 빠르게 refine 하는 amortization 기법.
- **Delay Augmentation** — 학습 시 촉각 스트림과 시각 캐시 사이의 시간 staleness 를 일부러 무작위로 주입해 배포 시의 비동기 지연 분포에 강건하게 만드는 증강.

---

## 🔬 방법론

### 직관

T-Rex 의 출발점은 단순한 관찰입니다. 손으로 하는 정교한 일은 "무엇을 할지" 를 정하는 느린 인지 과정과, "방금 미끄러졌으니 쥐는 힘을 고친다" 는 빠른 촉각 반사가 동시에 돌아갑니다. 표준 VLA 는 무거운 비전·언어 backbone 한 덩어리로 동작하므로 이 두 시간 스케일을 한 루프에 욱여넣어, 빠른 촉각 반응을 낼 수 없습니다. T-Rex 는 한 모델 안에 **느린 손(action expert)** 과 **빠른 손(tactile expert)** 을 두고, 느린 손이 큰 그림(visuomotor 계획)을 그리면 빠른 손이 그 위에서 실시간 촉각으로 마무리 붓질만 빠르게 반복하게 합니다.

핵심 트릭은 이 분담을 flow-matching denoising 의 "시간 축" 위에서 구현한 것입니다. 노이즈에서 깨끗한 action 으로 가는 denoising 궤적을 $`\tau_{\mathrm{split}}`$ 한 점에서 자르고, 상단(노이즈에 가까운 거친 구간)은 action expert 가, 하단(정답에 가까운 미세 구간)은 tactile expert 가 맡습니다. 거친 계획은 한 action chunk 당 한 번만 비싸게 계산하고, 미세 마무리는 비전 타워를 건드리지 않고 촉각 토큰 + 캐시된 시각 문맥만으로 chunk 안의 여러 시점에서 싸고 빠르게 다시 돌립니다. 그래서 "비동기(asynchronous)" 이고 "cascaded(직렬 이어받기)" 입니다.

촉각을 모델에 넣는 방식도 핵심입니다. 손가락별 force 시계열은 noise·drift 가 심하므로 그대로 넣지 않고, VQ-VAE 로 학습된 codebook 의 이산 토큰(손가락당 하나)으로 압축해 drift 에 강한 "촉각 단어" 로 바꿉니다. 동시에 force 벡터가 잃는 edge·slip 같은 공간 contact 정보는 deformation map 을 ResNet 으로 인코딩해 보존합니다. 두 흐름을 합쳐 tactile expert 가 소비합니다.

마지막으로 데이터·학습 측면의 직관은 "촉각은 사전학습이 아니라 중간학습에서 붙인다" 입니다. 촉각 동기화 데이터는 희소하므로, 비전·모션 prior 는 22,889시간의 human egocentric 비디오에서 받고, 100시간짜리 촉각 동기화 robot 데이터로 mid-training 하여 그 prior 를 실제 contact dynamics 에 정렬한 뒤, 태스크당 ~100 데모로 post-training 합니다.

### 아키텍처

![Figure 3 — T-Rex Model Architecture](https://arxiv.org/html/2606.17055/x3.png)

> "Figure 3: T-Rex Model Architecture. T-Rex uses a Mixture-of-Transformer-Experts (MoT) backbone with three experts: a latent expert for future visual prediction, an action expert for low-frequency action denoising, and a tactile expert for high-frequency tactile refinement. During inference, the tactile expert reuses cached visual-language context to asynchronously refine intermediate actions using spatial-temporal tactile features, enabling fast tactile-reactive closed-loop control." (§4.1)
> (한글 해설 — 세 expert(latent/action/tactile)가 MoT 로 묶이고, tactile expert 가 캐시된 시각·언어 문맥을 재사용해 비동기로 action 을 마무리하는 전체 구조를 시각화합니다.)

입력·출력 정의부터 봅니다.

> "The T-Rex policy $`\pi_{\theta}`$ receives RGB observations $`\mathbf{o}_{t}`$ , language instructions $`\ell`$ , tactile force history $`\mathbf{f}_{t-H_{f}:t}`$ , and tactile deformation maps $`\mathbf{d}_{t}`$ ." (§4)
> (한글 해설 — 멀티모달 문맥 $`\mathbf{c}_{t}=\{\mathbf{o}_{t},\ell,\mathbf{f}_{t-H_{f}:t},\mathbf{d}_{t}\}`$ 를 조건으로, horizon $`H`$ 의 미래 action chunk $`\mathbf{A}_{t:t+H}`$ 를 예측합니다.)

**MoT 세 expert.**
- **Latent expert** — 시각·언어 관찰을 처리해 **미래 visual representation 을 예측**, 시간적으로 grounded 된 문맥을 제공(world-model 성격의 보조 목표). backbone 은 Qwen3VL-2B.
- **Action expert** — 순수 noise 에서 중간 timestep $`\tau_{\mathrm{split}}`$ 까지 denoising 해 **저주파 action plan** 을 생성.
- **Tactile expert** — 캐시된 visual-language 문맥을 재사용하면서 $`\tau_{\mathrm{split}}`$ 에서 $`\tau=0`$ 까지 이어 denoising, **고주파 촉각 관찰로 action 을 refine** 해 최종 실행 chunk $`\mathbf{A}_{t:t+H}`$ 산출. FFN intermediate 가 1536 으로 축소된 경량 expert(0.62B).

**시공간 촉각 인코딩.** force 의 시간 dynamics 와 deformation 의 공간 신호를 함께 인코딩합니다.

> "A per-finger VQ-VAE compresses the recent force history $`\mathbf{f}_{t-15:t}`$ into compact temporal tokens, while the current force vector $`\mathbf{f}_{t}`$ is projected directly to preserve instantaneous contact information." (§4.1)
> (한글 해설 — 최근 16프레임 force 이력은 VQ-VAE 로 이산 토큰화하되, 현재 force 는 순간 contact 보존을 위해 직접 projection 하여 둘을 모두 씁니다.)

촉각 토큰 시퀀스는 Eq.(2) 로 구성됩니다:

$$\mathbf{z}^{\tau}_{t}=\bigl[\mathrm{Emb}_{\mathrm{vq}}\!\bigl(E_{f}(\mathbf{f}_{t-15:t})\bigr);\mathrm{Proj}_{f}(\mathbf{f}_{t});\mathrm{Proj}_{d}\!\bigl(E_{d}(\mathbf{d}_{t})\bigr)\bigr].$$

세 항은 각각 (i) VQ-VAE 가 인코딩한 force 이력의 양자화 임베딩, (ii) 현재 force 직접 projection, (iii) deformation map 을 conv encoder $`E_{d}`$ 로 뽑은 공간 특징의 projection 이며, 이들을 concat 해 tactile expert 의 입력 토큰을 이룹니다.

**VQ-VAE 동적 force 인코더(App. C).** 손가락별 6차원 force 를 $`T=16`$ 프레임 윈도로 모아, 1D temporal conv(2 strided block) → temporal mean-pool 로 256차원 임베딩을 만들고, 크기 $`K=64`$ codebook 의 최근접 코드로 양자화합니다. codebook 은 EMA 로 갱신하며 미사용 코드를 재시드해 collapse 를 방지하고, 비접촉 상태로의 collapse 를 막기 위해 **magnitude-weighted MSE** 로 고접촉 프레임에 더 큰 penalty 를 줍니다. conv weight 는 5개 손가락이 공유하고 **finger-identity 임베딩** 을 주입해 손가락당·손당 하나의 drift-robust 이산 토큰을 만듭니다(no-lock-in, cross-digit 확장성).

**Deformation 인코더(App. C).** 단일채널 변위장 $`\mathbf{d}_{t}`$ 를 ResNet-18 의 앞 3 residual stage 만 남겨 처리하고, 각 stage 뒤 $`3\times 3`$ conv 로 128 채널에 reproject 후 flatten·linear projection 합니다. 이 인코더는 self-supervised conv autoencoder 로 **사전학습 후 정책 학습 동안 frozen** 되어, trainable 파라미터를 늘리지 않고 안정적 geometry-aware contact 표현을 공급합니다.

### 학습 목표 / 손실

기본 골격은 conditional flow matching 입니다. clean action $`x_{0}=A_{t:t+H}`$, Gaussian noise $`x_{1}=\epsilon\sim\mathcal{N}(0,I)`$ 에 대해 vector field $`v_{\theta}(x_{\tau},\tau\mid c_{t})`$ 를 학습합니다(Eq.1):

$$\mathcal{L}_{\mathrm{FM}}(\theta)=\mathbb{E}\left[\left\|v_{\theta}(x_{\tau},\tau\mid c_{t})-(x_{1}-x_{0})\right\|^{2}\right]$$

**Shared Flow Target.** 두 expert 는 동일한 target 을 disjoint 구간에서 회귀합니다(Eq.3):

$$\mathbf{x}_{\tau}=(1-\tau)\,\mathbf{A}^{\mathrm{demo}}+\tau\,\boldsymbol{\epsilon},\qquad v^{\star}=\boldsymbol{\epsilon}-\mathbf{A}^{\mathrm{demo}}.$$

> "Both experts regress this identical target $`v^{\star}`$ over disjoint sub-intervals of $`\tau\in(0,1]`$ , conditioned on global multimodal contexts (upper segment) and localized tactile observations (lower segment), respectively." (§4.2)
> (한글 해설 — 동일 속도 target 을 공유하므로 두 expert 의 출력이 한 궤적으로 매끄럽게 이어지며, 상단은 전역 멀티모달 문맥, 하단은 국소 촉각 문맥에 조건화됩니다.)

**Training Protocol.** action expert 는 $`\tau_{\mathrm{act}}\sim\mathrm{Beta}(1.5,1.0)`$ 를 $`(0,1]`$ 전체에서, tactile expert 는 $`\tau_{\mathrm{tac}}=\tau_{\mathrm{split}}\cdot\tilde{\tau}`$ ($`\tilde{\tau}\sim\mathrm{Beta}(1.5,1.0)`$, $`(0,\tau_{\mathrm{split}}]`$)로 샘플합니다. 두 네트워크의 MSE 손실(Eq.6):

$$\mathcal{L}_{\mathrm{act}}=\bigl\lVert f_{\theta}^{\mathrm{act}}(\mathbf{x}_{\tau_{\mathrm{act}}},\tau_{\mathrm{act}})-v^{\star}\bigr\rVert^{2},\quad\mathcal{L}_{\mathrm{tac}}=\bigl\lVert f_{\theta}^{\mathrm{tac}}(\mathbf{x}_{\tau_{\mathrm{tac}}},\tau_{\mathrm{tac}};\,\mathrm{KV}_{\tau_{\mathrm{split}}})-v^{\star}\bigr\rVert^{2},$$

> "Notably, training the action expert across the full $`(0,1]`$ domain ensures it retains standalone competency of action generation and keeps consistency with the pretraining paradigm." (§4.2)
> (한글 해설 — action expert 를 전체 구간에서 학습시키는 것은, tactile expert 가 없어도 단독으로 동작 생성이 가능하도록 보장하고 사전학습 패러다임과의 일관성을 지키기 위한 설계입니다 — 기존 VLA 역량의 비파괴적 확장.)

전체 목표는 future-frame 시각 예측 손실까지 더합니다(Eq.7, $`\lambda_{\mathrm{tac}}=1.0`$, $`\lambda_{\mathrm{future}}=0.5`$):

$$\mathcal{L}=\mathcal{L}_{\mathrm{act}}+\lambda_{\mathrm{tac}}\,\mathcal{L}_{\mathrm{tac}}+\lambda_{\mathrm{future}}\,\mathcal{L}_{\mathrm{future}}$$

여기서 $`\mathrm{KV}_{\tau_{\mathrm{split}}}`$ 는 **detached slow-stream pass** 에서 추출됩니다(stop-gradient). App. B 는 conditioning 을 명시적으로 분리합니다: action expert 는 멀티모달 latent 문맥 $`\mathbf{c}^{\mathrm{vl}}`$ (head/wrist 카메라 + 언어 + future-prediction 토큰)에만, tactile expert 는 raw vision 을 전혀 보지 않고 고주파 촉각 토큰 $`\mathbf{c}^{\mathrm{tac}}`$ 와 `torch.no_grad` 로 얻은 캐시 $`\mathrm{KV}_{\tau_{\mathrm{split}}}`$ 에만 조건화됩니다.

**Cascaded Denoising Inference.** $`N=10`$ Euler step, $`\tau_{\mathrm{split}}=0.4`$. slow stream 은 chunk 당 1회, $`\mathbf{x}_{1}=\boldsymbol{\epsilon}`$ 에서 $`K_{\mathrm{slow}}=6`$ step 적분(Eq.4):

$$\hat{\mathbf{x}}_{\tau_{\mathrm{split}}}=\mathrm{Euler}\bigl(f_{\theta}^{\mathrm{act}};\,\mathbf{x}_{1},\,\tau{:}\,1{\to}0.4,\,K_{\mathrm{slow}}=6\bigr).$$

이후 경계 상태를 정지 시각 문맥 $`\mathrm{KV}_{\tau_{\mathrm{split}}}`$ 로 캐시. action chunk 길이 $`T_{a}=16`$ 에 대해 fast stream 은 chunk 내 offset $`\{0,4,8,12\}`$ 에서 자주 trigger 되어 무거운 visual network 를 우회하고 $`K_{\mathrm{fast}}=4`$ step 을 풉니다(Eq.5):

$$\mathbf{A}_{t:t+T_{a}}=\mathrm{Euler}\bigl(f_{\theta}^{\mathrm{tac}};\,\hat{\mathbf{x}}_{\tau_{\mathrm{split}}},\,\tau{:}\,0.4{\to}0,\,K_{\mathrm{fast}}=4\bigr).$$

KV 캐시는 $`\mathrm{KV}_{\tau_{\mathrm{split}}}=\bigl[\mathrm{KV}^{\mathrm{lat}}\big|\mathrm{KV}^{\mathrm{act}}_{\tau_{\mathrm{split}}}\bigr]`$ 로 구성되어 visual-language key/value 와 $`\tau_{\mathrm{split}}`$ 시점으로 재인코딩된 action position 을 함께 담습니다. 배포 시 fast tick 의 시각 캐시-촉각 스트림 간 staleness 를 위해 **delay augmentation** $`\delta\sim\mathrm{Uniform}\{0,4,8,12\}`$ 로 프레임 인덱스를 무작위 shift 해 배포 분포와 정확히 맞춥니다. 실제 로봇에서는 single-threaded request socket + 명시적 execution lock 으로 두 expert 를 직렬화해 thread safety 를 보장합니다(Algorithm 1).

### 학습 셋업

3단계 레시피(§4.3):
- **Large-scale Human Egocentric Pre-training** — EgoScale 를 따라 **22,889시간** egocentric human video 로 latent·action expert 를 사전학습. head-view 관찰로 시각·언어 표현을, retargeted human 팔/손 모션을 통합 action space 로 학습(tactile expert 없음).
- **Tactile-Grounded Robot Mid-training** — 100시간 촉각 동기화 양손 teleoperation 데이터로 action expert 를 robot 멀티뷰·실행 action 에 적응시키고 tactile expert 를 고주파 denoising refinement 로 학습.
- **Skill-Specific Post-training** — 태스크당 ~100 데모로 미세조정, mid-training 의 촉각 반응 행동을 보존하며 특정 태스크에 적응. mid-training 만으로도 zero-shot contact-rich 능력이 이미 나타납니다.

주요 config(Table 4): latent/action expert backbone **Qwen3VL-2B**(hidden 2048, 28 layers, 1.41B each), tactile expert 0.62B(FFN intermediate 1536), action dim **62**, action chunk **16**. inference timestep: action 6 / tactile 4. AdamW, peak LR $`1\times10^{-4}`$, cosine(min-LR), weight decay 0, grad clip 1.0, **24× NVIDIA H100**, DeepSpeed ZeRO-1, per-device batch 16, bf16.

---

## 📊 실험 설정과 결과

**셋업.** fixed-base 양손 **Dexmate Vega-1** + 두 개의 **22-DoF Sharpa Wave** dexterous hand. ZED head + 2 wrist 카메라(640×360), per-finger force 벡터 + deformation map. action 은 팔은 relative end-effector delta, 손가락은 absolute joint control. 12개 촉각 반응 태스크 각 16 trial(물체 위치·회전 무작위), progress-based rubric 으로 partial completion 반영, trial·task 평균 성공률 보고. baseline 6종: ViTacFormer, RDP, Tactile-VLA, EgoScale, $`\pi_{0.5}`$, $`\pi_{0.5}`$+tactile.

> "T-Rex achieves the highest average success rate across all task categories, outperforming the strongest baseline by more than 30% ." (§5.2, Table 1)
> (한글 해설 — 12개 전 태스크 평균에서 T-Rex 65% vs 최강 baseline EgoScale 35% 로 30%p 우위.)

**Table 1 — 12개 태스크 성공률(%), task당 16 rollout 후 task 평균:**

| Method | Flip Page | Transfer Egg | Wipe Plate | Apply Paste | Split Cup | Sort Mahjong | Open Lock | Refill Tablet | Acid-Base | Extract Card | Deal Poker | Screw Bulb | **Avg.** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ViTacFormer | 9 | 0 | 4 | 1 | 4 | 7 | 0 | 0 | 0 | 2 | 2 | 1 | **3** |
| RDP | 12 | 8 | 18 | 2 | 6 | 9 | 2 | 0 | 0 | 1 | 2 | 7 | **6** |
| Tactile-VLA | 38 | 14 | 24 | 0 | 21 | 27 | 8 | 0 | 9 | 4 | 11 | 18 | **15** |
| EgoScale | 68 | 44 | 34 | 38 | 33 | 36 | 19 | 12 | 43 | 41 | 28 | 18 | **35** |
| $`\pi_{0.5}`$ | 36 | 17 | 28 | 13 | 18 | 32 | 5 | 1 | 24 | 8 | 9 | 11 | **17** |
| $`\pi_{0.5}`$ + tactile | 8 | 9 | 27 | 2 | 4 | 14 | 2 | 0 | 7 | 3 | 0 | 0 | **6** |
| **Ours (T-Rex)** | **96** | **75** | **69** | **66** | **78** | **65** | **47** | **41** | **76** | **70** | **57** | **35** | **65** |

두 가지 관찰: (1) **대규모 사전학습이 필수** — scratch 학습 소형 정책(ViTacFormer 3, RDP 6)은 전반 부진. (2) **촉각 피드백이 contact-rich 에서 결정적** — 사전학습 VLA(EgoScale)도 정밀 contact 조정·force 행동에서 실패. 주목할 점은 사전학습 VLA 에 촉각을 **naive 하게 conditioning** 한 $`\pi_{0.5}`$+tactile 이 오히려 17→6 으로 **성능을 떨어뜨린다** 는 것 — 효과적 촉각 통합의 중요성을 방증합니다.

**Table 2 — 촉각 모달리티·구조 ablation(6개 대표 태스크 평균):**

| Configuration | Flip Page | Apply Paste | Split Cup | Open Lock | Extract Card | Screw Bulb | Average |
|---|---|---|---|---|---|---|---|
| Full Model (Ours) | 96 | 66 | 78 | 47 | 70 | 35 | **65** |
| w/o Tactile | 76 | 39 | 58 | 23 | 34 | 20 | 42 (−23%) |
| MLP Force + Deform | 89 | 58 | 72 | 44 | 58 | 29 | 58 (−7%) |
| Deform | 82 | 57 | 71 | 36 | 55 | 25 | 54 (−11%) |
| MLP Force + VQVAE Force | 92 | 63 | 65 | 38 | 67 | 28 | 59 (−6%) |
| w/o Async | 92 | 61 | 73 | 45 | 59 | 30 | 60 (−5%) |

per-ablation 읽기: **w/o Tactile(−23%)** 이 가장 큰 하락 → 촉각 자체가 최대 기여. **MLP Force + Deform(−7%)** 은 제안 VQ-VAE 시간 인코더를 경량 MLP 로 대체 시 손실 → 시간적 force 인코딩의 가치. **Deform only(−11%)** vs **Force only(−6%)** → 두 신호 모두 필요하되 force(VQ-VAE) 단독이 deform 단독보다 강함. **w/o Async(−5%)** → 비동기 refinement(저주파 계획/고주파 제어 분리)의 순수 기여 5%p.

> "When $`\tau_{\mathrm{split}}`$ is too small, the action expert provides insufficient visuomotor priors for downstream refinement; when $`\tau_{\mathrm{split}}`$ is too large, the tactile expert has limited capacity to incorporate tactile feedback." (§5.3, Figure 4)
> (한글 해설 — split step 은 중간값이 최적 — 너무 작으면 계획이 부족, 너무 크면 촉각 반영 여지가 부족. $`\tau_{\mathrm{split}}=0.4`$ 가 그 절충.)

**데이터 효율 & 레시피.**

![Figure 5 — Data Efficiency of T-Rex](https://arxiv.org/html/2606.17055/x5.png)

> "Figure 5: Data Efficiency of T-Rex. We show the success rate curve of different numbers of demonstrations. Blue: with our tactile-grounded T-Rex mid-training data; Green: without mid-training." (§5.3)
> (한글 해설 — post-training 데모를 10→200 으로 늘릴 때, 촉각 grounded mid-training(파랑)이 특히 low-data 영역에서 성능을 크게 끌어올려 downstream 데이터 요구량을 줄임을 보입니다.)

**Table 3 — 3단계 레시피 효과(6개 대표 태스크 평균 성공률 %):** 사전학습·mid-training 을 ablate 한 네 변형의 평균이 **18 → 34 → 45 → 65** 로 단조 증가하며, 두 단계 모두 기여하고 full recipe(human pretrain + tactile mid-train)가 최고(65)입니다. (원문 표의 체크 표시 셀은 텍스트 추출 시 누락되어 각 행의 pretrain/midtrain 조합 매핑은 §5.3 본문 서술 — "both stages contribute" — 에 근거합니다.)

추가로 100시간 촉각 grounded T-Rex 데이터셋 vs 동일 예산(100시간) 11개 task-specific 데이터셋 비교(Fig. 6)에서, 제안 데이터셋이 더 강한 일반화·zero-shot 전이를 보였습니다.

---

## ⚖️ 한계

- **하드웨어 병목 (저자 명시)** — 센서 distortion, 기기 간 calibration drift, whole-hand 조작용 dense palm sensing 부재가 촉각 반응 조작을 제약합니다. fingertip 만 감지하므로 손바닥·측면 접촉이 필요한 동작은 표현되지 않습니다.
- **Teleoperation 난이도 → long-horizon 한계 (저자 명시)** — 정밀 contact 조정·tight tolerance 가 필요한 long-horizon 태스크는 teleop 자체가 어려워, 저자도 RL·online interaction refinement 를 미래 과제로 둡니다. BC 의 distribution shift 가 transfer egg 의 부정확 위치 결정 같은 실패로 나타납니다(App. H).
- **절대 성공률의 천장 (추론)** — 평균 65% 는 baseline 대비 큰 우위지만 Screw Bulb(35), Refill Tablet(41), Open Lock(47) 등은 여전히 절반 이하입니다. App. H 의 실패는 object collision·slipping·multi-finger friction·excessive force 등 손가락 수준 coordination 부족을 드러내, contact-rich 의 본질적 어려움이 남아 있음을 보입니다.
- **Frozen deform 인코더의 표현 상한 (추론)** — deformation 인코더를 self-supervised 후 frozen 으로 쓰면 파라미터는 절약되나, 정책 task 분포에 맞춘 contact 특징을 학습하지 못해 새 물체/접촉 양식에서 표현 병목이 생길 수 있습니다.
- **비동기 staleness 의 본질적 위험 (추론)** — fast tick 이 정지된 시각 캐시 위에서 도므로, 빠른 시각 변화(물체가 굴러감)와 촉각 사이 정합이 깨질 수 있습니다. delay augmentation 으로 완화하나 staleness 분포를 벗어난 동역학에서는 취약할 수 있습니다.
- **VQ-VAE codebook 의 sensor 의존성 (추론)** — drift-robust 토큰화는 학습 시 본 force 분포·센서 특성에 묶입니다. 다른 촉각 센서/교정 상태로 옮기면 codebook 이 의미를 잃을 수 있어, 저자가 미래 과제로 든 heterogeneous sensor 통합 표현 필요성과 직결됩니다.

---

## ♻️ 재현성

- **코드** — 별도 코드 저장소 URL 은 본문에서 확인되지 않았습니다(프로젝트 페이지 `tactile-rex.github.io` 만 제시). 데이터 로더·전처리 스크립트는 데이터셋과 함께 공개 예정으로 명시.
- **데이터** — T-Rex Dataset(raw sensor streams + derived tactile representations + language annotations)을 **MIT 라이선스** 로 공개 예정. 7,755 에피소드 / 100시간 / 207 물체 / 22 motor primitive / 502 object-primitive 조합, median 에피소드 29.8s.
- **하드웨어** — Dexmate Vega-1 양손 로봇 + 22-DoF Sharpa Wave hand 2개, ZED 카메라 3대, Manus glove + VIVE tracker teleop. 저수준 300Hz, 고수준 30Hz, Pink(diff-IK) + Pinocchio/CasADi retargeting. 재현에는 동일 하드웨어 의존성이 큽니다.
- **연산** — 24× H100, DeepSpeed ZeRO-1. 사전학습은 22,889시간 EgoScale 코퍼스에 의존하여 사전학습 단계의 독립 재현 비용이 매우 높습니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

T-Rex 는 PROBE 의 핵심 가설 다수를 직접 건드리며, 특히 **타깃 하드웨어가 동일**(22-DoF Sharpa Wave + vision-based fingertip Deform Map ≈ MASTER §4.1 의 near-term Sharpa Hand)하여 transfer 평가가 이례적으로 직접적입니다.

- **P1(Heterogeneous Body/Hand Action Expert) — D5(input-modality + control-rate separation), D1(split form), D4(Body↔Hand information sharing)** — T-Rex 의 저주파 action expert + 고주파 tactile expert 의 **control-rate separation** 은 D5 의 정확한 주제입니다. PROBE 의 현재 D5 입장은 "(α) **shared rate**" 인데, T-Rex 는 split-rate 가 contact-rich 에서 +5%p(w/o Async ablation)를 준다는 직접 증거를 제시 — D5 재검토의 강한 신호. MoT 의 expert 간 KV-cache 공유는 D4(정보 공유)의 한 구현 형태입니다.
- **P2(Structured Multimodal Observation Fusion) — D11(proprio-tactile-force token construction), D10(fusion beyond concat), D12(topology-aware aggregation)** — per-finger VQ-VAE force 토큰 + Deform Map ResNet → 토큰화는 D11 v1("hardware-specific CNN on Deform Map → per-fingertip feature → finger token; swappable sensor head + common token format")과 거의 일대일 대응. conv weight 공유 + finger-identity 임베딩은 D12(finger/hand identity)의 직접 사례. $`\pi_{0.5}`$+tactile(naive concat) 의 성능 **하락** 은 D10("flat concat 거부")의 핵심 thesis 를 실증합니다.
- **P4(Pretraining for Data-Efficient Adaptation) — D21(staged recipe), D22(egocentric vs mixed composition)** — ego pretrain → tactile mid-train → post-train 의 3-stage 는 D21 의 staged recipe 골격과 일치하며, mid-training 으로 촉각을 "붙이는" 설계는 D21 의 Stage 2(VLM-stable + expert 학습) 변주로 읽힙니다. EgoScale 기반 egocentric-centric 사전학습은 D22(open ablation: egocentric vs mixed)에 egocentric 우위 증거를 더합니다.
- **P0(VLA Datasets & Benchmarks) — D25(tactile/torque data scouting), D26(benchmark scope), D24(priority data axis)** — 100시간 촉각 동기화 robot 데이터셋(MIT)은 D25 가 "first-class gap" 으로 다루는 희소 contact-modality 코퍼스의 정확한 대상이며, 12개 contact-rich 실세계 태스크는 D26(dexterous benchmark)의 후보입니다. `catalogs/datasets.md`(robot) 등재 대상.
- **P5(World Model) — D28(role), D30(prediction space)** — latent expert 의 **future visual representation 예측** 보조 목표는 P5 v1 의 "latent dynamics prior + future-prediction auxiliary co-trained with the VLA" 와 정확히 같은 역할 — raw-pixel 이 아닌 latent 예측이라는 점도 D30 의 선호와 부합.
- **P3(Hand-level System0) 관련성** — 고주파 tactile expert 는 PROBE 의 System0(저수준 contact 안정화)와 **기능적으로 유사**하나, T-Rex 는 이를 **RL 이 아닌 imitation flow-matching** 으로 구현합니다. PROBE 의 "System0 = RL only" 입장과 대비되는 대안적 증거점.

**Identity 지지/긴장** — "per-finger proprio-tactile binding beyond flat concat" 과 "control-rate separation" 을 동일 Sharpa 하드웨어에서 실증하므로 Identity 를 강하게 **지지**합니다. 단, T-Rex 의 분리축은 PROBE 의 anatomical **Body/Hand** 분리가 아니라 **action/tactile(속도)** 분리이고, 빠른 반응층을 RL 없이 imitation 으로 처리한다는 점이 PROBE 의 P3(System0-RL) 가정과 **긴장** 합니다.

---

## ✨ 핀 논문 대비 델타

- **vs ViTacFormer (P2 §5 핀, arXiv:2506.15953)** — ViTacFormer 는 ACT-style cross-attention visuotactile + future-tactile prediction 의 **task-specific** 정책입니다. T-Rex 는 이를 baseline 으로 직접 비교해 평균 3% → 65% 로 압도하며, 차별점은 (i) 대규모 ego 사전학습 + 촉각 mid-training, (ii) **async control-rate split**(ViTacFormer 엔 없음), (iii) **시간적 force VQ-VAE**(ViTacFormer 의 단순 6D force conditioning 대비). 즉 "촉각 fusion 구조" 자체보다 **사전학습·중간학습 레시피 + 속도 분리** 가 결정적이라는 새 증거.
- **vs ForceFlow (P2 §5 핀, asymmetric multimodal fusion)** — T-Rex 는 asymmetric fusion 을 **MoT + denoising 시간축 분할** 로 구현해, 모달리티 비대칭을 "어느 timestep 구간을 누가 맡는가" 로 환원한 점이 새롭습니다.
- **vs π0.5 (P4/P1 §5 핀, arXiv:2504.16054)** — 동일 셋업에서 $`\pi_{0.5}`$(17) 및 naive $`\pi_{0.5}`$+tactile(6)을 모두 능가. 단순히 촉각을 modality 로 추가하면 오히려 해롭고, 전용 expert + 전용 토큰화 + 중간학습이 있어야 이득이라는 점이 핀 대비 델타.
- **vs EgoScale (P0/P4 §5 EgoDex 계열, 사전학습 base)** — EgoScale(35)는 T-Rex 의 사전학습 토대이자 최강 baseline. 델타는 순수하게 **촉각 grounded mid-training + tactile-reactive 제어**(35 → 65), 즉 ego 사전학습이 준 visuomotor prior 를 contact dynamics 로 잇는 중간 단계의 기여를 격리해 보여줍니다.
- **vs SaTA / DexViTac (P2 §5 off-pin, Sharpa 하드웨어 + 촉각 인코딩)** — 동일 Sharpa Deform Map 경로지만, T-Rex 는 시간적 VQ-VAE 토큰화 + 비동기 고주파 expert 로 **반응성(reactivity)** 축을 추가한 점이 구별됩니다.

---

## ⚙️ 의사결정 함의

이 논문이 맞다면 PROBE 파이프라인에서 다음이 바뀝니다.

- **D5(control-rate separation) 재검토** — 현재 v1 "(α) shared rate" 를 **split-rate(저주파 action / 고주파 hand)** 후보로 승격 검토. 구체적으로: action expert 는 chunk 당 1회, hand/contact expert 는 chunk 내 offset $`\{0,4,8,12\}`$ 에서 재호출하는 비동기 스케줄을 ablation 변수로 추가. config 키: `tactile_expert.k_fast`, `split_tau`(=0.4 기본), `action_chunk=16`.
- **D11(proprio-tactile-force token) 구체화** — Deform Map CNN(우리 계획) 옆에 **per-finger force 시계열 VQ-VAE**(codebook `K=64`, window `T=16`, 6D force, magnitude-weighted MSE, EMA + dead-code reseed, finger-shared conv + finger-identity embed)를 토큰 구성에 추가하는 것을 검토. 이는 drift-robust 토큰화로 "swappable sensor head + common token format"(D11 non-negotiable)을 만족.
- **D10(fusion beyond concat) 강화 근거** — $`\pi_{0.5}`$+tactile 의 성능 하락은 flat-concat 금지(D10) 결정의 직접 증거. 촉각을 **별도 expert/조건화 경로**로 두는 설계를 default 로.
- **D21(staged recipe) 에 mid-training 단계 삽입 검토** — Stage 1(pretrain) 과 Stage 3(deploy adapt) 사이에 **촉각/contact grounded mid-training** 을 명시적 단계로 추가. loss term: `λ_tac=1.0`, future-prediction `λ_future=0.5`(P5 연동).
- **메트릭** — contact-rich 평가에서 progress-based partial-completion rubric 채택, w/o-Async / w/o-Tactile ablation 을 표준 보고 항목으로.

---

## ⚠️ 먼저 검증할 실패 모드

가장 싼 sanity check 부터:

- **(가장 쌈) 속도 분리의 실제 이득이 우리 태스크에서 5%p 안팎에 그칠 위험** — Table 2 의 w/o Async 는 −5% 로, 촉각 자체(−23%)보다 훨씬 작습니다. 우리 Phase 1(in-hand cube rotation)처럼 reactivity 요구가 낮은 태스크에선 split-rate 가 복잡성 대비 이득이 미미할 수 있음 → 먼저 **shared-rate vs split-rate 를 in-hand rotation 에서 단일 ablation** 으로 확인.
- **하드웨어는 같으나 backbone lineage 가 다름** — T-Rex 는 **Qwen3VL-2B** 백본이고 PROBE 는 **π(π0/π0.5, PaliGemma)** lineage(MASTER §4.3). KV-cache 재사용·MoT expert 분할이 π flow-matching action expert 구조 위에서 동일하게 성립하는지 미지수 → openpi action expert 를 두 구간으로 자르는 cascaded denoising 의 소규모 PoC 가 필요.
- **VQ-VAE codebook 의 센서 전이성** — codebook 은 학습 시 force 분포에 묶이므로, 우리 Sharpa 교정 상태·force 스케일이 다르면 토큰이 무의미해질 수 있음 → 우리 데이터로 VQ-VAE 를 재학습했을 때 codebook utilization·재구성 오차를 먼저 측정(저비용).
- **데이터 규모 의존성** — 100시간 촉각 동기화 + 22,889시간 ego 사전학습이 전제입니다. 우리의 in-house ego 수집·촉각 teleop 규모가 그 1/10 수준이면 mid-training 효과가 Fig.5 의 low-data 영역만큼 나오지 않을 수 있음 → 10/50/100 데모 곡선을 우리 셋업에서 재현.
- **비동기 staleness 의 sim/real gap** — delay augmentation 분포 $`\{0,4,8,12\}`$ 는 T-Rex 의 30Hz/300Hz 스택에 맞춘 것. 우리 제어 rate 가 다르면 staleness 분포를 다시 맞춰야 하며, 안 맞추면 frozen 시각 캐시-실시간 촉각 정합 붕괴로 빠른 동역학에서 실패 → 우리 control-loop 주기에 맞춘 delay 분포 재교정.
- **frozen deform 인코더의 우리 물체 분포 적합성** — self-supervised 후 frozen 가정이 우리 contact 양식(tool articulation 등)에서 표현 부족을 일으킬 수 있음 → frozen vs fine-tune 인코더의 소규모 비교.

---

## 💡 컨텍스트 제안

- **P0 `catalogs/datasets.md`(robot 섹션) 신규 등재 후보** — T-Rex Dataset(100h, 촉각 동기화, 양손 Sharpa Wave, MIT, arXiv:2606.17055). D25(tactile/torque 희소 코퍼스) 우선순위 항목 — 동일 타깃 하드웨어라 우리 데이터 포맷·토큰 설계의 직접 참조가 됩니다. (본 분석의 `카탈로그` 라우팅으로 skeleton row 제안.)
- **P1 §5 Tracked Literature 핀 검토** — control-rate separation 의 실증 사례로 T-Rex 를 D5 근거 항목에 추가 검토(현 핀 TwinBrainVLA(AsyMoT)와 함께 "asynchronous MoT" 라인).
- **D5 v1 재검토 트리거** — "(α) shared rate" 입장을 유지할지, split-rate 를 in-hand rotation ablation 으로 falsify 할지 결정 필요. 본 논문은 그 트리거를 당기는 첫 직접 증거입니다.
- **P3 가정 점검** — "fast reactive 층 = RL only" 가정에 대해, T-Rex 의 imitation-flow-matching tactile expert 가 RL 없이도 contact refinement 를 달성한다는 반례를 기록(결정 변경 제안이 아니라 가정 falsifier 후보로).
