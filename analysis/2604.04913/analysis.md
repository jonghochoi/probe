# Paper Analysis — A Frame is Worth One Token: Efficient Generative World Modeling with Delta Tokens

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | A Frame is Worth One Token: Efficient Generative World Modeling with Delta Tokens |
| 저자 | Tommie Kerssies, Gabriele Berton, Ju He, Qihang Yu, Wufei Ma, Daan de Geus, Gijs Dubbelman, Liang-Chieh Chen (Amazon · Eindhoven University of Technology · Johns Hopkins University) |
| 링크 | [arXiv:2604.04913](https://arxiv.org/abs/2604.04913) · [Website](https://deltatok.github.io) |
| 발행일 / 버전 | 2026-04-06 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-15 |
| 관련 Pillar | P5 |
| 태그 | flow-matching |

<!-- 태그 주의: 통제 어휘(STYLE §5-7)에 `world-model` 이 없어 본 논문(생성형
     world model)에 정직히 맞는 태그가 없습니다. BoM 단일-패스 생성이 diffusion/
     flow 의 대체재라는 "연속 생성 목표" 슬롯으로서 least-wrong 인 `flow-matching`
     을 authored — 어휘 확장 제안은 §💡 컨텍스트 제안 참조(2605.26379 선례). -->

---

## 🧭 한 줄 요약 (TL;DR)

연속 두 프레임의 VFM(DINOv3) 특징 차분을 **단 하나의 연속 "delta token"** 으로 압축하는 토크나이저(DeltaTok)와, 그 토큰 위에서 Best-of-Many 목표로 **단일 forward pass 에 다양한 미래를 동시에 생성**하는 world model(DeltaWorld)을 제안해, 기존 생성형 world model 대비 파라미터 35배·FLOPs 2,000배를 줄이면서 dense forecasting 정확도를 끌어올립니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 미래는 본질적으로 불확실하므로 world model 은 **여러 개의 그럴듯한 미래**를 정확하고 *효율적으로* 생성해야 합니다. 그런데 결정론적(discriminative) world model 은 미래를 평균내 단일 예측으로 붕괴시키고, 생성형(generative) world model 은 너무 비쌉니다.
- **기존 접근의 한계 (결정론)** — VFM 특징공간에서 동작하는 최근 world model 은 파라미터를 크게 줄였지만 대부분 결정론적이라, 불확실성하에서 조건부 평균으로 수렴해 distinct 한 미래 사건을 표현하지 못합니다.
- **기존 접근의 한계 (생성형)** — 기존 생성형 world model 은 (i) 픽셀 충실도에 최적화된 표현공간을 쓰고, (ii) 미래 하나를 만드는 데도 여러 번의 순차 forward pass(diffusion denoising / autoregressive)를 요구하며, (iii) 연속 프레임의 시공간 중복을 활용하지 못해 비효율적입니다.
- **본 논문의 가설** — 연속 프레임은 구조적·저차원적으로만 달라지므로(배경은 정적, 일부만 변화), 프레임 간 *변화*만 단일 token 으로 압축하면 비디오를 3D 시공간 표현에서 **1D 시간 시퀀스**로 축약할 수 있고, 그러면 다중 미래 학습/추론이 tractable 해집니다.
- **왜 지금 중요한가** — 자율주행·로봇처럼 다중 에이전트 상호작용을 예측해야 하는 의사결정에는 "다양한 미래의 효율적 생성"이 직접적 병목이며, VFM 특징공간 예측이 픽셀 재구성보다 적은 파라미터로 더 나은 dense forecasting 을 보인다는 흐름과 맞물립니다.

---

## 🧩 핵심 기여

- **DeltaTok** — 연속 두 프레임의 VFM 특징 차이를 단 하나의 연속 delta token 으로 인코딩하는 토크나이저. $`512\times512`$ 입력에서 토큰 수를 약 $`1{,}024\times`$ 줄여 공간 모델링 자체를 제거하고 비디오를 순수 시간 시퀀스로 만듭니다.
- **DeltaWorld** — delta token 시퀀스 위에서 동작하는 컴팩트한 생성형 world model. 단일 forward pass 로 여러 그럴듯한 미래를 동시에 생성합니다.
- **Best-of-Many(BoM) 적용** — 결정론적 DINO-world 를 단일-패스 생성형으로 확장하는 단순한 학습 목표(K 개 노이즈 쿼리 중 GT 에 가장 가까운 하나만 지도)를 차용·검증.
- **효율성** — 기존 생성형 world model(Cosmos) 대비 파라미터 $`35\times`$, FLOPs $`2{,}000\times`$ 절감하면서 best 예측이 모든 메트릭에서 Cosmos 를 능가.
- **delta token 의 일반성** — discriminative DINO-world 및 다른 아키텍처(DINO-Foresight)에 끼워 넣어도 성능을 유지(토큰 $`2048\times`$ 감소)함을 부록에서 추가 입증.

---

## 🔑 기술 키워드

- **DeltaTok** — 두 프레임 특징을 받아 그 *차이*만 한 개 토큰으로 짜내는 인코더-디코더 — 비디오 코딩의 interframe(delta) 압축을 VFM 특징공간으로 옮긴 것.
- **delta token** — 프레임 $`t{-}1`$ 을 $`t`$ 로 바꾸는 변환만 담은 단일 연속 벡터 $`z_t \in \mathbb{R}^{D}`$ — "무엇이 변했는가"만 기록하므로 장면 전체 재인코딩보다 정보량이 훨씬 적음.
- **Best-of-Many (BoM)** — K 개 stochastic 입력으로 K 개 미래를 뽑고 GT 에 가장 가까운 하나만 역전파하는 학습 목표 — "여러 번 던지고 가장 잘 맞은 것만 칭찬"하는 단일-패스 다중가설 학습.
- **VFM feature space** — 픽셀이 아니라 frozen vision foundation model 의 patch 토큰 위에서 예측하는 것 — 다운스트림(segmentation/depth)이 이미 쓰는 특징공간이라 무관한 픽셀 디테일을 모델링할 필요가 없음.
- **DINO-world** — 본 논문이 출발점으로 삼는, DINO 특징공간에서 동작하는 결정론적 video world model(재구현해서 베이스라인으로 사용).
- **discriminative vs generative world model** — 전자는 단일 결정론적 미래(조건부 평균으로 붕괴), 후자는 다양한 미래 분포를 표본화 — 본 논문은 전자를 후자로 값싸게 바꾸는 것이 목표.
- **frame compression** — delta 가 아니라 한 프레임 전체 특징맵을 단일 frame token 으로 압축하는 중간 단계 — capacity 부족으로 delta 압축에 밀림(ablation 의 step 2).
- **single-pass diverse generation** — diffusion 의 반복 denoising 없이 서로 다른 노이즈 쿼리를 서로 다른 미래로 한 번에 사상하는 추론 방식.
- **dense forecasting benchmark** — 미래 프레임에 대한 segmentation mIoU / depth RMSE 로 world model 을 평가하는 프로토콜(VSPW·Cityscapes·KITTI, short 약 0.2s / mid 약 0.6s).
- **Cosmos** — 픽셀 재구성용 latent 공간에서 동작하는 대형 생성형 world model — 본 논문의 주 비교 대상(4B/12B + 7B diffusion decoder).

---

## 🔬 방법론

### 직관

DeltaWorld 의 출발점은 "미래는 하나가 아니다"라는 관찰입니다. 결정론적 world model 은 가능한 미래들을 평균낸 흐릿한 한 장을 내놓는데, 이는 실제로는 일어나지 않는 미래입니다. 그래서 저자들은 모델이 여러 미래를 *뽑게* 만들고 싶어 하지만, 표준 생성기법(diffusion)은 미래 하나당 수십 번의 forward pass 가 들어 비쌉니다. 핵심 아이디어 1: **Best-of-Many** — 노이즈가 다른 K 개의 쿼리를 한 번에 통과시켜 K 개의 미래를 만들고, 정답에 가장 가까운 하나만 학습 신호로 쓰면, 단 한 번의 forward pass 로 "서로 다른 입력 → 서로 다른 미래" 매핑을 배웁니다.

그런데 미래 하나가 여전히 $`H\times W`$ 개의 공간 토큰이라면 K 개를 뽑는 비용이 큽니다. 핵심 아이디어 2: **프레임을 토큰 한 개로 압축**합니다. 연속한 두 프레임은 배경이 그대로이고 일부만 바뀌므로, 프레임 전체가 아니라 *바뀐 부분*만 인코딩하면 됩니다. DeltaTok 은 이전 프레임 특징 $`x_{t-1}`$ 을 조건으로 받아 현재 프레임 $`x_t`$ 와의 차이를 단 하나의 delta token $`z_t`$ 로 짜냅니다. 디코더는 $`x_{t-1}`$ 에 $`z_t`$ 를 적용해 $`x_t`$ 를 복원합니다.

이렇게 하면 비디오가 "프레임당 토큰 하나"의 1D 시간 시퀀스가 되고, predictor 는 공간 모델링을 전혀 하지 않은 채 다음 delta token 만 예측하면 됩니다. 부수 효과로 정확도도 오릅니다: delta 공식은 "변화 없음 = 이전 프레임 유지"라는 자연스러운 prior 를 내장하므로, 모델은 *무엇이 변하는지*만 배우면 됩니다. BoM(다양성)과 delta 압축(효율+정확도)을 결합한 것이 DeltaWorld 입니다.

### 아키텍처

**Preliminaries (DINO-world predictor).** Frozen VFM $`\phi`$ 가 각 프레임 $`v_i \in \mathbb{R}^{H' \times W' \times 3}`$ 을 patch 토큰 grid $`x_i = \phi(v_i) \in \mathbb{R}^{H \times W \times D}`$ 로 임베딩합니다. predictor $`f`$ 는 단일 learnable query $`q`$ 가 context $`X_{1:t}`$ 에 cross-attention 하는 Transformer block 스택으로, 각 공간위치의 미래 patch 토큰을 예측합니다.

$$\hat{x}_{t+1,h,w}=f\!\left(q,\,X_{1:t},\,T_{1:t},\,\tau_{t+1},\,h,\,w\right)\in\mathbb{R}^{D}.$$

> "It uses a stack of Transformer blocks applying cross-attention from a single learnable query embedding $`q`$ to the context $`X_{1:t}`$" (§3.1)
> (predictor 의 본체는 학습된 쿼리 하나가 과거 특징에 cross-attention 하는 구조이며, 위치별 positional embedding 이 위치 의존 예측을 보장합니다. 이 단일 쿼리를 노이즈 쿼리로 바꾸는 것이 생성형화의 출발점입니다.)

**Best-of-Many.** 단일 쿼리 $`q`$ 를 K 개의 Gaussian 노이즈 쿼리로 교체합니다.

$$q^{k}\sim\mathcal{N}(\mu,\Sigma),\qquad k=1,\dots,K$$

각 쿼리가 공간위치 전체에 공유되어 K 개 예측을 만들고,

$$\hat{x}_{t+1,h,w}^{k}=f\!\left(q^{k},\,X_{1:t},\,T_{1:t},\,\tau_{t+1},\,h,\,w\right)\in\mathbb{R}^{D}.$$

**DeltaTok 토크나이저.** 연속 autoencoder 설계입니다. 인코더 $`g`$ 가 이전·현재 프레임 특징과 learnable embedding $`z_{\mathrm{init}}`$ 을 받아 delta token 을 만들고, 디코더 $`h`$ 가 이전 프레임으로부터 현재 프레임을 복원합니다.

$$z_{t}=g(x_{t-1},x_{t},z_{\mathrm{init}})\in\mathbb{R}^{D},\qquad \hat{x}_{t}=h(x_{t-1},z_{t}).$$

> "the encoder now takes both $`x_{t-1}`$ and $`x_{t}`$ to produce a single delta token $`z_{t}`$ that encodes the change between them" (§3.4)
> (delta 압축의 정의식입니다. 프레임 압축(§3.3)의 $`z_t=g(x_t,z_{\mathrm{init}})`$ 와 달리 이전 프레임을 조건으로 받아 "장면 전체"가 아니라 "변환"만 담게 되므로 단일 토큰의 capacity 안에 더 정확히 들어갑니다. encoder/decoder 모두 self-attention Transformer(ViT-B), 인코더는 per-frame embedding 으로 이전/현재 토큰을 구분합니다. Figure 3 이 이 인코더-디코더 구조를 시각화합니다.)

**DeltaWorld.** Frozen DeltaTok 과 predictor $`f`$ 를 결합합니다. 각 입력 시퀀스 앞에 black frame 을 prepend 해 첫 delta token $`z_1`$ 이 첫 실프레임의 *절대* 특징을 인코딩하게 합니다. predictor 는 과거 delta token 시퀀스 $`Z_{1:t}`$ 위에서 다음 delta token 을 예측합니다.

$$\hat{z}_{t+1}=f(q^{k},Z_{1:t},T_{1:t},\tau_{t+1}).$$

> "Each input sequence is prepended with a black frame so that the first delta token $`z_{1}`$ effectively encodes the absolute features of the first real frame." (§3.4)
> (delta 토큰은 상대 표현이라 절대 기준이 필요하며, 검은 프레임을 첫 이전-프레임으로 두는 트릭으로 시퀀스 첫 토큰이 절대 특징을 담게 합니다. 공간 특징맵은 디코더로 $`\hat{x}_{t+1}=h(x_{t},\hat{z}_{t+1})`$ 처럼 필요할 때만 복원합니다.)

단일 토큰 시퀀스 덕분에 DINO-world 의 block-causal mask 와 3D RoPE 가 불필요해져, predictor 는 표준 causal(대각) mask 와 1D RoPE(헤드당 앞 60차원 회전, 뒤 4차원 비회전)로 단순화됩니다. 노이즈 쿼리는 $`\mathcal{N}(0,\,0.02^{2}I)`$ 에서 표본화합니다.

### 학습 목표 / 손실

**BoM 손실.** K 개 예측 중 GT 에 가장 가까운 $`k^\star`$ 만 지도합니다.

```math
\begin{split}&k^{\star}=\arg\min_{k}\sum_{h,w}\ell\!\left(x_{t+1,h,w},\,\hat{x}_{t+1,h,w}^{k}\right);\\ &L_{\text{BoM}}=\sum_{h,w}\ell\!\left(x_{t+1,h,w},\,\hat{x}_{t+1,h,w}^{k^{\star}}\right),\end{split}
```

> "Only the prediction closest to the ground truth is supervised" (§3.2)
> (이 argmin-then-supervise 가 BoM 의 전부입니다. 서로 다른 노이즈를 서로 다른 미래로 사상하도록 유도하되 단일-패스 효율을 유지합니다. DeltaWorld 에서는 이 손실이 *delta token 공간*에서 계산되어 디코딩 없이 best 후보를 고를 수 있습니다. $`\ell`$ 은 smooth L1, $`\beta=0.1`$.)

**토크나이저 재구성 손실.** DeltaTok 은 world model 학습 *전에* 별도로 MSE 로 학습됩니다.

$$L_{\mathrm{tok}}=\|\,x_{t}-\hat{x}_{t}\,\|^{2}.$$

> "DeltaTok is trained using the same reconstruction loss as for frame compression, with frame pairs $`(x_{t-1},x_{t})`$ drawn from the same uniform timestamp-sampling procedure used for predictor training." (§3.4)
> (토크나이저는 frame-pair 재구성만으로 학습되며, 추론 frame rate 가 토큰 하나가 담는 변화량을 조절합니다 — 거의 정적 장면이면 이전 프레임을 대부분 유지, 큰 전환이면 절대 압축에 가깝게 동작.)

### 학습 셋업

- **VFM** — DINOv3 ViT-B(patch $`16\times16`$), frozen. 토크나이저·predictor 모두 단순화를 위해 ViT-B 구성(스케일 제약은 없음).
- **데이터** — DINO-world 와 유사한 다양 도메인 비디오 약 $`\sim`$4M 샘플(대부분 $`640\times360`$, 평균 11s, 16 FPS). DINO-world 의 $`\sim`$66M 대비 훨씬 작음(Table A). 평가셋(VSPW/Cityscapes/KITTI)은 학습셋에 미포함.
- **토크나이저 학습** — 50K iters, MSE, AdamW, lr $`10^{-3}`$(5K warmup 후 constant), weight decay $`10^{-4}`$, batch 1,024, grad-norm clip $`10^{-2}`$, 해상도별 별도 학습.
- **predictor 학습** — AdamW, lr $`10^{-4}`$(5K warmup 후 constant), weight decay $`4\times10^{-1}`$, smooth L1($`\beta{=}0.1`$), batch 1,024, sequence length 8 frames, grad clip 없음. 메인 300K iters(ablation 100K), 이후 $`10\times`$ 낮은 lr 로 5K iters fine-tune.
- **BoM K** — 메인 $`K{=}256`$($`512\times512`$), ablation $`K{=}16`$($`256\times256`$).
- **temporal offset** — $`\Delta\tau`$ 를 $`[1/25,\,1/3]`$ 초에서 uniform 표본화. augmentation 은 scale 0.6–1.0, aspect 3:4–4:3 random resized crop(시퀀스 전체 일관 적용).
- **하드웨어** — 8× NVIDIA H200, BF16 mixed precision, torch.compile.

---

## 📊 실험 설정과 결과

**평가 프로토콜.** dense forecasting benchmark(DINO-world)로 short(약 0.2s, 직접 예측) / mid(약 0.6s, 3-step autoregressive rollout) 정확도를 segmentation mIoU·depth RMSE 로 측정. 4-frame context, frozen VFM 특징에 학습한 linear seg/depth head 를 예측 미래 특징에 적용. 테스트시 20 표본을 뽑아 **best**(GT 에 가장 가까운 표본)와 **mean**(특징공간 평균 후 head 적용) 둘 다 보고.

**Table 2 — 효율적 생성형 world model 로 가는 단계별 ablation** (mid ~0.6s mIoU, $`256\times256`$, best-of-20, 괄호는 mean):

| Step | GFLOPs ↓ | Time ↓ | Mem ↓ | VSPW ↑ | Cityscapes ↑ |
|---|---|---|---|---|---|
| (0) Discriminative | 959 | 1.0× | 1.0× | 44.8 | 45.4 |
| (1) BoM training | 12013 | 4.9× | 1.0× | 47.0 (39.4) | 46.8 (31.1) |
| (2) Frame compress | 6315 | 0.4× | 0.2× | 45.7 (40.3) | 42.7 (35.5) |
| (3) Delta compress | 6721 | 0.5× | 0.2× | 46.8 (44.4) | **48.7 (45.5)** |

> "DeltaWorld substantially improves over step (2) on both best and mean metrics … its best predictions match or exceed BoM without any compression in step (1) (+1.9 mIoU on Cityscapes, within 0.2 mIoU on VSPW), while its mean mIoU recovers to the level of the discriminative baseline … (44.4 vs. 44.8 on VSPW and 45.5 vs. 45.4 on Cityscapes)." (§4.4)
> (단계별 읽기 — step 1: BoM 으로 best 는 오르지만 mean 이 급락(Cityscapes 45.4→31.1)하고 학습시간 5× 증가, 다수 표본이 한 클래스로 붕괴. step 2: frame 압축이 BoM 표본화를 한 자릿수 이상 빠르게(메모리 0.2×) 만들고 디코더가 붕괴를 억제해 mean 회복하나 capacity 부족으로 best/mean 모두 baseline 이하. step 3: delta 압축이 best·mean 둘 다 끌어올려 best 는 무압축 BoM 을 따라잡고 mean 은 결정론 baseline 수준 회복.)

**Table 3 — Dense forecasting 메인 결과** ($`512\times512`$, 생성형은 best-of-20, 괄호는 mean; VSPW/City mIoU ↑, KITTI RMSE ↓):

| Model | GFLOPs | VSPW Short | VSPW Mid | City Short | City Mid | KITTI Short | KITTI Mid |
|---|---|---|---|---|---|---|---|
| Copy last (하한) | — | 51.2 | 44.3 | 53.5 | 39.6 | 3.76 | 4.86 |
| DINO-world † | $`5.8\times10^{3}`$ | 54.0 | 47.9 | 62.0 | 49.8 | 3.16 | 4.07 |
| Cosmos-4B ‡ | $`6.0\times10^{7}`$ | 51.1 (49.7) | 47.0 (44.5) | 55.1 (54.9) | 49.1 (48.4) | 3.82 (3.75) | 4.08 (4.14) |
| Cosmos-12B ‡ | $`6.4\times10^{7}`$ | 51.7 (50.7) | 47.7 (45.5) | 55.3 (56.0) | 53.3 (51.2) | 3.72 (3.71) | 4.01 (4.14) |
| **DeltaWorld (Ours)** | $`3.1\times10^{4}`$ | **55.4 (53.7)** | **50.1 (46.7)** | **65.8 (63.9)** | **55.4 (51.3)** | **3.00 (3.17)** | **3.88 (4.17)** |
| Present (상한) | — | 58.4 | 58.4 | 70.5 | 70.5 | 2.79 | 2.79 |

> "despite Cosmos using roughly $`2{,}000\times`$ more FLOPs, its performance generally lags behind DeltaWorld, with DeltaWorld's best surpassing that of Cosmos across all metrics, while achieving stronger mean scores across nearly all metrics." (§4.6, Table 3)
> (DeltaWorld 의 best 가 모든 메트릭에서 Cosmos 를 능가하고 mean 도 거의 모든 메트릭에서 우위입니다. ‡ 표시대로 Cosmos 두 변형 모두 별도 7B diffusion decoder 가 FLOPs 를 지배합니다. best-mean 격차가 Cosmos 보다 일관되게 커, 표본 다양성이 더 의미 있음을 시사합니다.)

> "Compared to the single prediction of the discriminative DINO-World, DeltaWorld's mean scores are modestly better on Cityscapes and modestly worse on VSPW and KITTI." (§4.6)
> (결정론 DINO-world 의 단일 예측과 비교하면 mean 은 Cityscapes 에서 약간 우위, VSPW/KITTI 에서 약간 열위 — 즉 다중표본이 결정론이 못 잡는 현실적 모드를 덮되 평균품질은 동급임을 보여 줍니다.)

**Table B — FLOPs 분해** (mid, 4-frame context, ViT-B, $`256\times256`$, GFLOPs). DeltaWorld 에서 backbone($`4\times47.185{=}188.74`$)·DeltaTok encoder($`4\times96.930{=}387.72`$)는 *한 번만* 돌고, per-sample 비용은 predictor(4-frame 0.26)와 DeltaTok decoder(46.12)뿐입니다. 20 표본 생성시 predictor 는 전체 추론 FLOPs 의 **0.5%** 에 불과(반면 step 1 무압축 BoM 에서는 97%).

**Table C — discriminative DINO-world 에 delta token** (mid, $`256\times256`$): Delta compression 이 DINO-world(VSPW 44.8/City 45.4) 대비 VSPW 44.6(-0.2)·City 46.9(+1.5)로 동급 이상이면서 학습시간 0.5×·메모리 0.2×.

**Table D — DINO-Foresight 에 delta token** (Cityscapes, $`448\times896`$): delta 변형이 원본(10240 토큰, seg mid 59.8)과 동급(5 토큰, seg mid 60.0)을 **토큰 $`2048\times`$ 감소**로 달성.

**Figure 5 — BoM K 스케일링.** 학습 쿼리 $`K`$ 를 키우면 (eval 쿼리 $`>1`$ 에서) best 가 포화 없이 계속 향상하고, mean 은 약간 하락하나 $`K{=}64`$ 이후 안정 — 다양성이 평균품질을 해치지 않음을 보입니다.

![Figure 6 — Diverse sampled futures](https://arxiv.org/html/2604.04913/x1.png)

> "Figure 6: Diverse sampled futures. Top row: four context frames and the future frame. Bottom row: four sampled DeltaWorld predictions and the oracle. In this VSPW example, the pedestrian's position and ego-camera motion lead to multiple plausible futures." (§4.6)
> (단일 forward pass 가 보행자 위치·ego 카메라 모션이 다른 *복수의* 그럴듯한 미래를 만들어 냄을 시각화 — 결정론 모델이 평균낼 다양성을 표본으로 보존한다는 핵심 주장의 정성 근거.)

---

## ⚖️ 한계

- **분포 모델링의 원리 부재(저자 명시)** — BoM 은 diffusion 의 denoising 처럼 데이터 분포와의 원리적 연결이 없습니다. 표본 미래의 분포가 실제 확률을 근사한다는 보장이 없고, 커버리지가 학습시 탐색한 $`K`$ 에 제한되며 쿼리공간의 다양한 활용을 강제하는 메커니즘도 없습니다. 즉 "best 는 좋지만 그 표본들이 진짜 미래 *확률*을 반영하는가"는 미해결입니다.
- **오차 누적(저자 명시)** — delta 토큰은 상대 표현이라 절대 특징맵 복원이 이전 특징에 *반복 조건부 디코딩*을 요구합니다. 토크나이저 재구성 단계에서 오차가 누적돼 feature drift 가 날 수 있고, predictor 의 추가 오차가 multi-step autoregressive rollout 에서 더 증폭됩니다(autoregressive video generation 의 알려진 난제). 저자는 GT 가 아닌 *자기 복원본*에 대해 delta 를 순차 계산하는 완화책을 제안만 합니다.
- **단일 토큰 capacity 의 근본 천장(추론)** — 프레임당 한 토큰은 표현력 상한이 분명합니다. delta 가 frame 압축보다 낫지만, 변화가 크거나(빠른 모션·장면 전환) 공간적으로 분산된 미세 변화가 많은 장면에서는 한 토큰이 부족할 수 있습니다 — 본 벤치마크의 짧은 horizon(0.2–0.6s)·중간 frame rate 가 이 한계를 가렸을 여지가 있습니다.
- **VFM·재구현 의존(추론)** — 모든 결과가 DINOv3 특징공간 + *자체 재구현* DINO-world 위에서 나옵니다(공식 코드/데이터 미공개). 베이스라인이 저자 재구현이라 절대 수치의 외부 재현 가능성이 재구현 충실도에 묶입니다.
- **암묵적 action 의 미검증(추론)** — "쿼리공간이 암묵적 action conditioning 일 수 있다"는 흥미로운 관찰이지만 어떤 action 정량 평가도 없습니다 — 제어 가능성은 아직 가설입니다.

---

## ♻️ 재현성

- **코드 / 가중치** — 본문이 `deltatok.github.io` 에 "Code & weights" 공개를 명시(Website). 정확한 GitHub 레포 URL 은 본문에 직접 표기되지 않아 본 메타에는 Website 만 기재.
- **데이터** — 학습 코퍼스($`\sim`$4M, 대부분 $`640\times360`$)는 비공개. 평가셋(VSPW·Cityscapes·KITTI)과 split(Eigen test 등), task head 구성은 부록에 상세 명시.
- **하이퍼파라미터** — 토크나이저/predictor 학습 스케줄·옵티마이저·loss·augmentation·RoPE 차원·초기화(truncated normal $`\sigma{=}0.02`$, Layer Scale $`10^{-5}`$)까지 Appendix A 에 충실히 기재 — 재구현 난이도는 낮은 편.
- **하드웨어** — 8× H200, BF16, torch.compile 로 명시.

---

## 🎯 관련 Pillar / Decision (P# / D#)

본 논문은 **P5(World Model)** 에 직접 닿되, 여러 P5 Decision 과 *지지와 긴장*이 엇갈립니다.

- **D30(prediction space) — 강한 지지.** P5 의 v1 은 "**latent / 3D-flow** 예측(contact-relevant, compute-bounded)"이고 VLA-JEPA 가 그 pinned 인스턴스입니다. DeltaWorld 는 픽셀이 아니라 DINOv3 *특징공간*에서, 게다가 한 발 더 나아가 **특징 차분(delta)** 만 예측합니다 — latent-prediction 노선의 극단적 token-efficient 변형으로, D30 의 "compute-bounded latent" 논거를 보강합니다.
- **D28(world-model role) — 부분 지지/긴장.** P5 v1 role 은 "VLA 와 *co-trained* 된 dynamics prior + future-prediction auxiliary(standalone planner 아님)"입니다. DeltaWorld 는 *standalone* 생성형 forecaster 라 role 이 다르지만, "생성형 future-prediction auxiliary 를 어떻게 값싸게 만드나"라는 D28 의 효율 측면에 직접 기여합니다(BoM 단일-패스).
- **D29(integration architecture) — 긴장.** P5 v1 은 "shared VLA backbone 위 auxiliary head". DeltaWorld 는 VLA 와의 통합이 전혀 없는 독립 모델이라 통합 아키텍처 관점에서는 직접 매핑되지 않습니다.
- **D31(action conditioning) — 직접 긴장.** P5 v1 은 "**action-conditioned**(per-frame action) 예측"이고 §4 anti-topic 은 action-free next-frame 예측을 *명시적으로 배제*합니다. DeltaWorld 는 action-free 이며, action 은 노이즈 쿼리의 "암묵적 conditioning" 가설로만 존재합니다.
- **D32(egocentric hand-object) — 긴장(anti-topic).** 평가가 VSPW(일반)·Cityscapes/KITTI(**주행**)로, P5 anti-topic 의 "driving / navigation world models" 및 "world models with no manipulation evaluation" 두 범주에 정확히 들어갑니다. hand-object·egocentric manipulation eval 이 전무합니다.

**Identity 긴장/지지.** P5 Identity 는 "action-conditioned, egocentric, hand-object world model — contact-relevant latent/3D-flow 예측"입니다. DeltaWorld 의 *방법론*(특징공간 생성, delta token, BoM)은 Identity 의 "latent over pixel" 축을 강하게 지지하지만, *대상 도메인*(action-free, 주행/일반 비디오)은 Identity 와 정면으로 어긋납니다 — 즉 **방법 전이 관심**이지 도메인 정합이 아닙니다.

**경쟁자 함의.** DeltaWorld 는 본질적으로 DINO-world(P5 Tracked 와 인접한 feature-space WM 계보)의 *생성형* 확장이며, Cosmos(대형 pixel-space 생성형 WM)를 효율·정확도로 압도합니다 — "큰 생성형 WM 없이도 다양한 미래를 값싸게"라는 메시지가 Ctrl-World(raw-pixel 생성형) 노선에 압박을 줍니다.

---

## ✨ 핀 논문 대비 델타

- **vs VLA-JEPA(arXiv:2602.10098, P5 pinned).** VLA-JEPA 는 JEPA latent **결정론** world model(leakage-free latent state 예측)입니다. DeltaWorld 의 진짜 신규성은 (1) 같은 feature-space 노선을 **생성형**으로 만든 점(BoM, 단일 패스 다중 미래)과 (2) latent 를 프레임당 *한 개 토큰*, 그것도 *차분* 토큰으로 극단 압축한 점입니다. VLA-JEPA 가 "어떤 latent 를 예측하나"라면 DeltaWorld 는 "그 latent 를 얼마나 적게, 그리고 다양하게 예측하나"에 답합니다.
- **vs Ctrl-World(arXiv:2510.10125, P5 pinned).** Ctrl-World 는 controllable **raw-pixel** 생성형 WM(eval-in-imagination)입니다. DeltaWorld 는 동일한 "생성형·다양한 미래" 목표를 픽셀이 아닌 VFM 특징공간 + 단일-패스로 달성해, 파라미터 $`35\times`$ ·FLOPs $`2{,}000\times`$ 를 줄입니다 — 생성형 WM 의 비용 곡선을 바꾸는 델타.
- **vs Being-H0.7 / WorldVLA(P5 pinned).** 두 핀은 모두 VLA 와 *통합된* (latent world-action / 통합 autoregressive) 모델입니다. DeltaWorld 는 action·VLA 통합이 없는 순수 forecaster 라 통합 측면의 신규성은 없고, 대신 그들이 차용할 수 있는 **token-efficiency 빌딩블록**(delta token + BoM)을 제공합니다.

---

## ⚙️ 의사결정 함의

본 논문이 맞다면 우리의 **latent dynamics prior / future-prediction auxiliary**(D28/D30) 설계에서 두 가지 구체적 레버가 바뀝니다.

- **예측 표적을 "절대 특징"에서 "delta 특징"으로.** auxiliary head 가 다음 프레임의 full 특징맵 대신 $`z_t = g(x_{t-1}, x_t, z_{\mathrm{init}})`$ 형태의 *차분 토큰*을 예측하도록 바꾸면, (a) auxiliary 의 토큰 예산을 프레임당 1 토큰까지 줄이고(컨텍스트·rollout 비용 급감), (b) "변화 없음 = 이전 프레임 유지"라는 free prior 를 얻습니다. config 영향: world-model auxiliary 의 `prediction_target = delta_token`, 토크나이저를 frozen 사전학습 모듈로 추가.
- **결정론 auxiliary 를 BoM 으로 생성형화.** 기존 future-prediction auxiliary(smooth L1 회귀)에 `K` 개 노이즈 쿼리 + argmin-best 지도를 끼우면 diffusion 없이 단일 패스로 다양한 미래를 얻습니다. 새 하이퍼: `bom_K`(train, 시작값 16–64; Figure 5 상 $`K{\ge}64`$ 에서 mean 안정), 노이즈 쿼리 분포 $`\mathcal{N}(0, 0.02^2 I)`$, loss `L_BoM = smooth_l1(β=0.1)` 를 *latent/delta 공간*에서 계산(디코딩 불요). 메트릭: best-of-N 과 mean 을 분리 보고해 "다양성 vs 평균품질"을 동시에 추적.

다만 이 함의는 **방법론 차용**에 한정됩니다 — 우리 대상은 action-conditioned egocentric hand-object 이므로, delta token·BoM 을 우리 스택에 들일 때는 반드시 action 조건(D31)을 추가하고 manipulation eval 로 재검증해야 합니다(아래 ⚠️).

---

## ⚠️ 먼저 검증할 실패 모드

가장 싼 sanity check 부터:

1. **단일 delta token 이 손-접촉 디테일을 보존하는가 (가장 싼 체크).** 우리 egocentric hand-object 특징(또는 DINOv3 특징)에서 DeltaTok 을 학습해, 프레임당 1 토큰 재구성의 MSE 를 *손/접촉 영역에 한정*해 full-spatial 대비 측정. 주행/일반 장면(글로벌·저주파 변화)과 달리 손가락 pose·접촉점은 공간적으로 국소·고주파라, 한 토큰이 평균내 날려버릴 위험이 큼 — 여기서 무너지면 나머지는 의미 없음.
2. **action-free 가정의 붕괴.** 본 논문은 action 없이도 "그럴듯한 다양성"을 보이지만, 우리는 *action-conditioned* 예측(D31)이 필요. 노이즈 쿼리를 action embedding 으로 대체했을 때 BoM 의 best-supervision 이 여전히 동작하는지(특정 action 쿼리가 항상 best 가 돼 mode collapse 하지 않는지)부터 확인.
3. **horizon·frame rate 민감도.** 결과는 0.2–0.6s, 중간 frame rate. 우리 manipulation 은 더 긴 horizon·빠른 접촉 dynamics 일 수 있어, delta 토큰이 담는 변화량이 과포화되면 best/mean 모두 급락. $`\Delta\tau`$ 와 rollout depth 를 우리 데이터 통계로 스윕.
4. **autoregressive feature drift.** delta 의 반복 디코딩 + predictor 오차가 multi-step rollout 에서 누적(저자 명시). 우리의 긴 rollout 에서 feature drift 가 task head(접촉/grasp 판정)를 무너뜨리는지, 저자 제안대로 "자기 복원본 기준 순차 delta" 완화책이 필요한지 측정.
5. **VFM 의존성.** delta token 의 효과가 DINOv3 특징의 부드러운 시간 구조에 기댈 수 있음 — 우리가 다른 backbone(예: 다른 VFM/VLA encoder)을 쓰면 frame 간 차분이 저차원이라는 전제가 깨질 수 있어, 우리 backbone 특징에서 "연속 프레임 차분의 유효 랭크"를 먼저 확인.
6. **BoM 분포 보정 부재.** best 만 좋고 mean·다양성 보정이 약하면(원리적 분포 목표 부재), 우리가 eval-in-imagination 으로 policy 를 랭킹할 때 잘못된 미래에 과신할 수 있음 — best-of-N 외에 표본 분포 캘리브레이션 지표를 추가.

---

## 💡 컨텍스트 제안

- **P5 Tracked Literature — non-pinned methodology base 후보로만.** DeltaWorld(delta token + BoM, feature-space *생성형* WM)는 VLA-JEPA(latent 결정론)·Ctrl-World(pixel 생성형)의 빈 칸 — "feature-space 생성형 + token-efficiency" — 을 메우는 방법론 base 입니다. 다만 평가가 주행/일반 비디오·action-free 라 **P5 §4 anti-topic("driving" + "no manipulation eval")** 에 해당하므로, *pinned* 승격이 아니라 §5 의 "Methodology base(non-pinned)"에 (DINO-world 계보를 잇는 token-efficient WM 으로) 추가하는 선만 제안합니다. 최종 판단은 사람.
- **D30 보강 메모.** "latent 예측"의 한 극단으로 *delta(차분) 예측*을 D30 의 deferred 후보 어휘에 기록해 두는 것을 제안 — VLA-JEPA latent 대비 token-efficiency 트레이드오프를 추적하기 위함.
- **태그 어휘 확장(STYLE §5-7) 재확인.** 본 논문도 통제 태그 어휘에 `world-model` 슬롯이 없어 least-wrong `flow-matching` 으로 우회했습니다(2605.26379 선례와 동일). 어휘에 `world-model` 추가 검토를 다시 제안합니다. (docs/STYLE.md 미수정 — 사람 결정.)

---

> 💡 base 매핑은 `/implement-design analysis/2604.04913/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
