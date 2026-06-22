# Paper Analysis — HT-Bench: Benchmarking and Learning Dexterous Full-Hand Tactile Representations with Egocentric Vision

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | HT-Bench: Benchmarking and Learning Dexterous Full-Hand Tactile Representations with Egocentric Vision |
| 저자 | Yuzhe Huang, Jiaping Wu, Jiaming Jiang, Hezhe Lin, Aikebaier Aierken, Yunlong Wang, Kun Cheng, Ziyuan Jiao, Yuanxin Zhong |
| 링크 | [arXiv:2606.19161](https://arxiv.org/abs/2606.19161) |
| 발행일 / 버전 | 2026-06-17 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-22 |
| 관련 Pillar | P2, P0 |
| 태그 | tactile, egocentric-data, dexterity |
| 카탈로그 | benchmark/dexterous/HT-Bench |

---

## 🧭 한 줄 요약 (TL;DR)

촉각 센서·임베디먼트 이질성 때문에 보편 벤치마크가 불가능하다는 전제를 우회해, **egocentric 비전 + full-hand 촉각**이라는 확장 가능한 한 축으로 좁힌 대규모 멀티태스크 벤치마크 **HT-Bench**(RGB 10M·촉각 7.8M 프레임, 226 태스크)와, 공간→교차모달→시간의 3단계로 점진 학습하는 vector-quantized 비전–촉각 인코더 **HandTouch**를 제안합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 촉각 표현 학습(tactile representation learning)을 공정하게 평가할 수단이 없습니다. 센서 설계·데이터 포맷·로봇 임베디먼트가 제각각이라 비전처럼 표준화된 백본·벤치마크가 부재합니다.
- **기존 접근의 한계** — 기존 촉각 평가는 좁은 태스크나 특정 센서에 묶여 있어 "어떤 인코더가 dexterous full-hand 촉각의 표현 백본으로 적합한가"라는 선결 질문에 답하지 못합니다.
- **본 논문의 가설** — 모든 센서/임베디먼트 불일치를 해소하는 보편 벤치마크를 세우는 대신, **egocentric 비전 + full-hand 촉각** 조합으로 좁히면 확장 가능하고 의미 있는 평가축을 만들 수 있다는 것입니다.
- **왜 지금 중요한가** — 비전 중심 인식에서 멀티모달 로봇 정책으로 패러다임이 옮겨가며 접촉이 풍부한(contact-rich) 추론과 정밀 dexterous 조작에서 촉각이 점점 중요해지고 있으나, 이를 키울 대규모 학습·평가 기반이 비어 있습니다.

---

## 🧩 핵심 기여

- **HT-Bench** — egocentric 비전과 full-hand 촉각을 동기화한 대규모 멀티태스크 벤치마크. 약 10M RGB 프레임 + 7.8M 촉각 프레임, 226 태스크, 다중 씬(home / 전자 워크벤치 / 화학 실험실 / 리테일 / 야외 등).
- **3관점 평가 설계** — 촉각 표현이 (1) 의미 있는 접촉 기하를 인코딩하는지, (2) 촉각 관측을 시각 정보와 정렬하는지, (3) unseen 태스크로 일반화하는지를 본다.
- **4개 평가 태스크** — fine-grained tactile similarity retrieval, masked tactile inpainting, vision-to-tactile synthesis(RGB→Tac), multimodal tactile frame prediction.
- **Task-level OOD split** — 한 상호작용 태스크를 통째로 OOD 평가용으로 빼고, 나머지를 9:1로 train/test 분할해 unseen-task 일반화를 직접 측정.
- **HandTouch** — factorized vector quantization 기반 비전–촉각 인코더. 공간(VQ 재구성)→교차모달(masked inpainting)→시간(frame prediction)의 점진 3단계 학습으로 구조적·시각접지·시간인지 표현을 동시에 획득.
- **실증 우위** — 대표 촉각 인코더 baseline 대비 retrieval Recall@5 74.65→85.23%, inpainting RMSE 0.022→0.010 등 다수 지표 SOTA.

---

## 🔑 기술 키워드

- **Full-hand tactile sensing** — 지문(fingertip) 한 점이 아니라 손 전체(손가락·손바닥)에 분산된 접촉을 동시에 기록하는 촉각 감지 — 본 논문의 데이터·평가가 묶이는 설정.
- **Egocentric vision** — 1인칭(손 시점) 시각 관측 — 상호작용 중심의 시각 맥락을 자연스럽게 담아 촉각과 짝지어집니다.
- **Vector quantization (VQ)** — 연속 잠재 특징을 공유 codebook의 이산 토큰으로 양자화하는 기법 — 촉각 관측을 공유 이산 토큰 공간에 사상하는 HandTouch의 코어.
- **Factorized vector quantizer** — codebook 차원 $`d`$ 를 인코더 차원 $`D`$ 보다 낮게(병목) 두고 입력/출력 projection으로 오가는 VQ 변형 — 더 압축적이고 강건한 이산 공간을 위한 장치.
- **Codebook collapse / restart** — VQ에서 소수 코드만 자주 쓰이고 나머지가 죽는 현상과, EMA 사용 빈도를 추적해 죽은 코드를 재초기화하는 대응 — 코드북 활용도를 유지.
- **Cross-modal masked tactile inpainting** — 촉각 맵 일부(또는 전부)를 가리고 남은 촉각 + 시각 단서로 복원하는 자기지도 과제 — 비전–촉각 정렬을 학습시키는 Stage 2 목표.
- **Vision-to-tactile synthesis (RGB-to-Tactile)** — 단일 RGB 관측만으로 대응 촉각 압력 분포를 예측 — "보면 느낌이 떠오른다"는 교차모달 통합을 모사한 평가 태스크.
- **contact IoU (cIoU)** — 예측·정답 압력 맵의 픽셀별 min/max 합 비로 접촉 영역 일치도를 재는 지표 — RMSE가 놓치는 접촉 패턴 일치를 포착.
- **Curriculum dual masking** — Regional Random Masking과 Complete Masking을 학습 진행도에 따라 비율 조정하는 마스킹 커리큘럼 — 국소 inpainting에서 시각조건부 합성으로 난이도를 점증.
- **Hand-specific token** — 좌/우손을 구분하는 학습 가능 토큰 — 좌우 거울 대칭에서 오는 기하적 모호성을 줄이는 장치.

---

## 🔬 방법론

### 직관

HandTouch의 발상은 "촉각 표현 학습을 한 번에 풀지 말고, HT-Bench가 평가하려는 능력을 그대로 닮은 순서로 단계화하자"는 것입니다. 먼저 촉각 맵 자체의 공간 구조(어느 손가락·손바닥이 어떻게 눌렸는지)를 이산 토큰으로 압축해 익히고(공간), 다음으로 같은 순간의 시각 프레임을 단서로 끌어와 가려진 촉각을 복원하며 비전과 촉각을 정렬하고(교차모달), 마지막으로 과거 촉각·시각 시퀀스로부터 다음 촉각 프레임을 예측해 접촉의 시간 변화를 잡습니다(시간).

핵심 장치는 **공유 이산 코드북**입니다. 연속 촉각 특징을 codebook의 가까운 코드로 바꿔치기(quantize)해, 모든 단계가 같은 토큰 공간 위에서 동작하도록 묶습니다. 이렇게 하면 단계가 바뀌어도 표현 공간이 유지되고, 이산화 자체가 잡음에 강한 압축으로 작동합니다. 다만 VQ는 소수 코드만 쓰이는 collapse에 취약하므로, 사용 빈도를 추적해 죽은 코드를 되살리는 restart를 둡니다.

비전 주입은 가벼운 cross-attention으로 이뤄집니다. 시각 프레임을 얼린(frozen) ViT로 인코딩한 특징을 key/value로, 촉각 토큰을 query로 삼아 "보이는 것"으로 "가려진 촉감"을 채웁니다. 또 좌/우손이 거울처럼 닮아 생기는 혼동을 막으려고 손을 가리키는 작은 토큰을 더합니다.

### 아키텍처

입력은 정규화된 단일채널 촉각 맵과 동기화된 RGB 프레임이고, 출력은 (단계별로) 재구성/복원/예측된 촉각 맵입니다.

![Figure 1 — HT-Bench / HandTouch 개요](https://arxiv.org/html/2606.19161/x1.png)

> "Figure 1: Overview of HT-Bench. 1. HT-Bench pairs egocentric vision with full-hand tactile data to provide a scalable benchmark for dexterous tactile representation learning. It contains 10M RGB frames and 7.8M tactile frames collected from diverse manipulation tasks. 2. HandTouch learns a shared discrete tactile representation through progressive spatial, cross-modal, and temporal training, and 3. is evaluated on fine-grained tactile similarity retrieval, masked tactile inpainting, vision-to-tactile synthesis, and multimodal tactile frame prediction under task-level out-of-distribution splits." (§1)
> (한글 해설 — 데이터(좌)·HandTouch 3단계 학습(중)·4개 평가 태스크(우)의 전체 구도를 한 장에 담아, 벤치마크와 방법이 같은 능력 축으로 정렬됨을 보여줍니다.)

토큰화·인코더 구성은 다음과 같습니다.

> "Given a normalized tactile map $`\mathbf{t}\in[0,1]^{1\times 224\times 224}`$ , a convolutional projection layer tokenizes it into non-overlapping patches." (§4.1)
> (한글 해설 — 촉각 맵을 224×224 단일채널로 정규화한 뒤 컨볼루션 projection으로 비중첩 패치 토큰을 만듭니다.)

> "After adding learnable positional embeddings, the patch tokens are processed by an 8-layer Vision Transformer (ViT) encoder, producing continuous latent features $`\mathbf{Z}_{e}\in\mathbb{R}^{N\times D}`$ ." (§4.1)
> (한글 해설 — 학습 가능한 위치 임베딩을 더한 패치 토큰을 8-layer ViT가 처리해 연속 잠재특징 $`\mathbf{Z}_{e}`$ 를 냅니다.)

이산화는 병목 차원을 둔 factorized VQ로 합니다.

> "Let $`\mathcal{C}=\{\mathbf{e}_{i}\}_{i=1}^{K}\subset\mathbb{R}^{d}`$ denote the shared codebook of size $`K=2048`$ with a lower bottleneck dimension $`d\ll D`$ ." (§4.1)
> (한글 해설 — 크기 $`K=2048`$ 의 공유 코드북을 인코더 차원보다 낮은 병목 차원 $`d`$ 에 두어 압축적·강건한 이산 공간을 만듭니다.)

좌우손 모호성과 비전 주입 처리는 Stage 2에서 추가됩니다.

> "The synchronized visual frame $`\mathbf{v}`$ is encoded by a frozen pre-trained ViT to extract visual context features $`\mathbf{F}_{v}`$ ." (§4.2)
> (한글 해설 — 동기화된 시각 프레임은 **얼린** 사전학습 ViT로 인코딩되어, 촉각 복원에 주입할 시각 맥락 특징 $`\mathbf{F}_{v}`$ 가 됩니다 — 비전 인코더는 학습되지 않습니다.)

> "we additionally introduce a learnable hand-specific token $`\mathbf{t}_{\mathrm{hand}}\in\{\mathbf{t}_{\mathrm{left}},\mathbf{t}_{\mathrm{right}}\}`$ to reduce geometric ambiguity caused by lateral mirroring." (§4.2)
> (한글 해설 — 좌/우손이 거울처럼 닮아 생기는 기하 모호성을 줄이려 손을 지정하는 학습 토큰을 더합니다.)

![Figure 3 — HandTouch 3단계 학습 파이프라인](https://arxiv.org/html/2606.19161/x2.png)

> "Figure 3: Training pipeline of HandTouch. Stage 1: Learning spatial topologies of tactile graphics via unimodal self-attention reconstruction and vector quantization with a shared codebook. Stage 2: Reconstructing highly corrupted tactile images under a dynamic regional/complete masking scheme, guided by visual priors injected through cross-attention. Stage 3: Forecasting the current tactile distribution $`\mathbf{t}_{T}`$ based on sequential visual context $`\mathbf{v}_{T-2:T}`$ and past tactile histories $`\mathbf{t}_{T-2:T-1}`$ . Modules with flame icons are actively trained in each phase." (§4)
> (한글 해설 — Stage 1 공간 재구성, Stage 2 시각 priors 주입 inpainting, Stage 3 시간 예측의 3단계와, 각 단계에서 실제 학습되는(불꽃) 모듈을 시각화합니다.)

### 학습 목표 / 손실

**Stage 1 — Vector-Quantized Tactile Reconstruction.** $`j`$ 번째 패치 임베딩 $`\mathbf{z}_{e}^{(j)}`$ 을 입력 projection $`\mathbf{W}_{\text{in}}`$ 으로 코드북 공간에 보낸 뒤 최근접 코드로 양자화합니다.

$$\mathbf{z}_{q}^{(j)}=\mathbf{e}_{k},\quad\text{where }k=\arg\min_{i}\|\mathbf{W}_{\text{in}}\mathbf{z}_{e}^{(j)}-\mathbf{e}_{i}\|_{2}^{2}$$

(식 1)

양자화 토큰은 출력 projection $`\mathbf{W}_{\text{out}}`$ 로 인코더 임베딩 공간으로 되돌려 디코더로 전달됩니다. Stage 1 손실은 재구성 항 + VQ codebook/commitment 항입니다.

$$\mathcal{L}_{\text{stage1}}=\|\mathbf{t}-\hat{\mathbf{t}}\|^{2}_{2}+\|\mathbf{Z}_{q}-\mathrm{sg}[\mathbf{W}_{\text{in}}\mathbf{Z}_{e}]\|_{2}^{2}+\beta\|\mathrm{sg}[\mathbf{Z}_{q}]-\mathbf{W}_{\text{in}}\mathbf{Z}_{e}\|_{2}^{2}$$

(식 2)

여기서 $`\mathrm{sg}[\cdot]`$ 은 stop-gradient, $`\beta`$ 는 commitment loss 가중치입니다. 첫 항은 픽셀 재구성, 둘째 항은 코드북을 인코더 출력으로 끌어오는 항, 셋째 항은 인코더 출력이 코드에 commit하도록 하는 항입니다(표준 VQ-VAE 손실을 factorized projection 위에 얹은 형태).

codebook collapse 대응:

> "Codebook entries whose cumulative usage falls below a restart threshold $`\tau`$ are reinitialized using randomly sampled active projected features from $`\mathbf{W}_{\mathrm{in}}\mathbf{Z}_{e}`$ in the current batch, with small isotropic Gaussian noise added for exploration." (§4.1)
> (한글 해설 — EMA로 사용 빈도를 추적해 임계 $`\tau`$ 아래로 떨어진 죽은 코드를, 현재 배치의 활성 projected 특징에서 샘플링해 작은 등방성 가우시안 잡음과 함께 되살립니다.)

**Stage 2 — Cross-Modal Masked Tactile Inpainting.** 손 부위(엄지·검지·중지·손바닥) 단위로 가리는 Regional Random Masking과 전부 가리는 Complete Masking을 커리큘럼으로 섞습니다. Complete Masking 확률은 학습 진행도 $`\gamma\in[0,1]`$ 에 대한 시그모이드로 증가합니다.

$$P_{\mathrm{full}}(\gamma)=p_{\min}+\frac{(p_{\max}-p_{\min})}{1+\exp[-12(\gamma-0.5)]}$$

(식 3)

나머지 확률 $`1-P_{\mathrm{full}}(\gamma)`$ 가 Regional Random Masking에 배정되어, 학습이 진행될수록 국소 inpainting에서 시각조건부 합성으로 목표가 옮겨갑니다. Stage 2 손실은 가시영역/마스크영역 재구성 + Stage 1 VQ 항입니다.

$$\mathcal{L}_{\text{stage2}}=\lambda_{\text{vis}}\|(\mathbf{1}-\mathbf{M})\odot(\mathbf{t}-\hat{\mathbf{t}}_{\text{cm}})\|^{2}_{2}+\lambda_{\text{mask}}\|\mathbf{M}\odot(\mathbf{t}-\hat{\mathbf{t}}_{\text{cm}})\|^{2}_{2}+\|\mathbf{Z}_{q}-\mathrm{sg}[\mathbf{W}_{\text{in}}\mathbf{Z}_{e}]\|_{2}^{2}+\beta\|\mathrm{sg}[\mathbf{Z}_{q}]-\mathbf{W}_{\text{in}}\mathbf{Z}_{e}\|_{2}^{2}$$

(식 4)

$`\mathbf{M}\in\{0,1\}^{1\times 224\times 224}`$ 은 이진 occlusion 마스크(1=가려진 픽셀), $`\odot`$ 은 Hadamard 곱, $`\hat{\mathbf{t}}_{\mathrm{cm}}`$ 은 교차모달 복원 출력입니다. 가려진 영역 복원을 더 강조하려 $`\lambda_{\mathrm{mask}}>\lambda_{\mathrm{vis}}`$ 로 둡니다. codebook restart는 이 단계에서도 유지됩니다.

**Stage 3 — Multimodal Tactile Frame Prediction.** 최근 시각 관측 $`\mathbf{v}_{T-2}`$ 와 과거 촉각 궤적 $`\mathbf{t}_{T-2}`$ 로부터 시점 $`T`$ 의 촉각 분포 $`\hat{\mathbf{t}}_{T}`$ 를 예측합니다.

$$\mathcal{L}_{\mathrm{stage3}}=|\mathbf{t}_{T}-\hat{\mathbf{t}}_{T}|_{2}^{2}$$

(식 5)

이 단계에서는 prediction 모듈·공유 코드북·디코더가 fine-tune됩니다.

### 학습 셋업

- **데이터** — HT-Bench(약 10M RGB · 7.8M 촉각 프레임, 226 태스크). 기존 오픈소스 촉각/visuo-tactile 데이터셋(Song et al. 2025; Zhou et al. 2026)에 신규 수집 real-world full-hand 촉각 시퀀스를 합쳐 구성. task-level OOD split(한 태스크 hold-out, 나머지 9:1 train/test).
- **점진 학습** — Stage 1(촉각 단일모달 재구성) → Stage 2(시각 주입 inpainting) → Stage 3(시간 예측). 각 단계에서 학습되는 모듈은 불꽃 아이콘으로 표시(나머지·시각 ViT는 frozen).
- **하드웨어 / 옵티마이저 / 스케줄** — 원문에 명시 없음(에폭·배치·learning rate·GPU 미기재).

---

## 📊 실험 설정과 결과

baseline은 촉각 인식·조작에서 흔히 쓰이는 인코더 4종 — CNN-based(Lee et al. 2026), ResNet-18(Calandra et al. 2018), VQ-VAE-based(Xu et al. 2025), ViT-based(Zhao et al. 2024)이며, 모두 동일 train split에서 사전학습되고 동일 HT-Bench 프로토콜로 평가됩니다(§5). retrieval은 SSIM 기준 1-vs-20 랭킹과 임베딩 cosine 랭킹을 비교(Hit@1, Recall@5), inpainting/synthesis는 RMSE와 cIoU로 측정합니다. `F-`/`H-`는 각각 full map / masked hole 영역 지표입니다.

**Retrieval (1-vs-20)**

| Model | Hit@1 ↑ | Rec@5 ↑ |
|---|---|---|
| ResNet-18 | 92.13 | 72.85 |
| CNN-based | 89.61 | 70.09 |
| VQ-VAE | 63.60 | 51.98 |
| ViT-based | 94.27 | 74.65 |
| **Ours (HandTouch)** | **99.27** | **85.23** |

**Masked Tactile Inpainting (Test / OOD)**

| Model | Test F-RMSE ↓ | Test F-cIoU ↑ | Test H-RMSE ↓ | Test H-cIoU ↑ | OOD F-RMSE ↓ | OOD F-cIoU ↑ | OOD H-RMSE ↓ | OOD H-cIoU ↑ |
|---|---|---|---|---|---|---|---|---|
| ResNet-18 | 0.025 | 0.742 | 0.025 | 0.742 | 0.041 | 0.727 | 0.056 | 0.620 |
| CNN-based | 0.030 | 0.684 | 0.030 | 0.684 | 0.047 | 0.715 | 0.068 | 0.538 |
| VQ-VAE | 0.042 | 0.570 | 0.042 | 0.570 | 0.053 | 0.630 | 0.068 | 0.499 |
| ViT-based | 0.022 | 0.762 | 0.033 | 0.662 | 0.056 | 0.615 | 0.065 | 0.522 |
| **Ours** | **0.010** | **0.911** | **0.024** | **0.758** | **0.039** | **0.768** | 0.066 | 0.565 |

**Vision-to-Tactile Synthesis (RGB→Tac, Test / OOD)**

| Model | Test F-RMSE ↓ | Test F-cIoU ↑ | OOD F-RMSE ↓ | OOD F-cIoU ↑ |
|---|---|---|---|---|
| ResNet-18 | 0.038 | 0.624 | 0.084 | 0.445 |
| CNN-based | 0.036 | 0.642 | 0.083 | 0.447 |
| VQ-VAE | 0.060 | 0.456 | **0.081** | 0.408 |
| ViT-based | 0.038 | 0.628 | 0.083 | 0.446 |
| **Ours** | **0.031** | **0.705** | 0.082 | **0.459** |

핵심 수치 주장:

> "Compared with the strongest baseline, the ViT-based encoder, HandTouch improves Hit@1 from 94.27% to 99.27% and Recall@5 from 74.65% to 85.23%." (§5.1, Table 2)
> (한글 해설 — 최강 baseline인 ViT 대비 retrieval에서 임베딩 공간이 fine-grained 구조 유사성을 더 잘 보존함을 보입니다.)

> "Specifically, it obtains a full-map RMSE of 0.010 and a full-map cIoU of 0.911, substantially outperforming all baselines." (§5.1, Table 2)
> (한글 해설 — 표준 test split의 masked inpainting에서 full-map 재구성 오차를 크게 낮추고 접촉 일치도를 끌어올립니다.)

cIoU의 정의는 다음과 같습니다.

$$\mathrm{cIoU}=\frac{\sum_{i,j}\min(P_{i,j},\hat{P}_{i,j})}{\sum_{i,j}\max(P_{i,j},\hat{P}_{i,j})}$$

> "$`P_{i,j}`$ and $`\hat{P}_{i,j}`$ denote the ground-truth and predicted pressure values at pixel $`(i,j)`$ , respectively." (§5.1)
> (한글 해설 — 픽셀별 압력의 min/max 합 비로, RMSE가 못 잡는 접촉 영역의 형태 일치를 측정합니다.)

> "On the standard test split, HandTouch reduces the full-map RMSE to 0.031 and improves cIoU to 0.705, outperforming CNN-, ResNet-, VQ-VAE-, and ViT-based baselines." (§5.1, Table 2)
> (한글 해설 — RGB만으로 촉각 압력 분포를 합성하는 cross-modal 태스크에서도 우위를 보입니다.)

**Ablation/세부 reading (지표 행별 함의):**
- **Retrieval에서 VQ-VAE만 급락**(Hit@1 63.60, Rec@5 51.98) — 재구성 지향 이산 잠재만으로는 fine-grained 매칭에 중요한 미세 구조 단서를 잃는다는 신호. HandTouch가 같은 VQ 계열이면서 retrieval 최고치를 내는 것은 단계적 정렬/시간 목표가 이 손실을 상쇄함을 시사.
- **OOD hole-region에서 ResNet-18 역전** — HandTouch는 OOD full-map은 최고(F-RMSE 0.039 / F-cIoU 0.768)지만, OOD H-RMSE 0.066은 ResNet-18(0.056)에 밀림. unseen 태스크의 심하게 손상된 국소 영역 복원은 여전히 약점(§5.1 본문도 명시).
- **RGB→Tac OOD RMSE에서 VQ-VAE가 근소 우위(0.081 vs 0.082)** 하나 cIoU는 크게 열세(0.408 vs 0.459) — VQ-VAE는 더 매끄러운(픽셀 오차 작은) 예측을 내지만 날카로운 국소 접촉 패턴을 못 잡음을 시사.

> "Under the OOD setting, HandTouch achieves the highest cIoU of 0.459, indicating better cross-modal generalization to unseen tasks." (§5.1, Table 2)
> (한글 해설 — RGB→Tac OOD에서 접촉 일치도 기준으로는 일반화가 가장 좋습니다.)

**Multimodal Tactile Frame Prediction** (baseline이 단일프레임 인코더라 별도 트랙으로 보고):

> "It achieves accurate prediction on the test split (RMSE: 0.031, cIoU: 0.677) and maintains reasonable performance under OOD tasks, demonstrating its ability to model temporal contact dynamics during continuous interaction." (§5.1)
> (한글 해설 — 시각 맥락 + 촉각 이력으로 다음 촉각 프레임을 예측하는 시간 트랙에서 합리적 성능을 보입니다.)

---

## ⚖️ 한계

- **보편 벤치마크가 아님(저자 명시)** — HT-Bench는 egocentric 비전 + full-hand 촉각이라는 한 설정에 한정되어, fingertip optical 촉각·force/torque·skin-like taxel array·비손형 임베디먼트를 다루지 않습니다. 즉 "촉각 표현 백본" 결론은 이 데이터 분포 안에서만 유효하며, 다른 센서 모달리티로의 외삽은 보장되지 않습니다.
- **ablation이 예비 수준(저자 명시)** — 대규모 사전학습·멀티태스크 평가 비용 때문에 codebook·masking curriculum·cross-attention fusion·hand token·temporal 모듈의 기여를 분리하는 분석이 미흡합니다. 따라서 3단계 학습의 어느 요소가 이득의 주원인인지, 단순 ViT 대비 어디서 +가 나는지가 인과적으로 규명되지 않았습니다.
- **표현 수준 평가에 머묾(저자 명시)** — retrieval/inpainting/synthesis/prediction은 모두 표현의 구조·교차모달·시간 이해를 보지만, 실제 로봇 다운스트림 성능(grasp 조정·slip 대응·접촉풍부 조작)을 직접 측정하지 않습니다. 표현 지표 우위가 정책 성능으로 이어진다는 증거가 비어 있습니다.
- **타이트하게 동기화된 paired 데이터 의존(저자 명시)** — 시각·full-hand 촉각의 동기 수집은 정밀 캘리브레이션·유지보수를 요구해 확장 비용이 큽니다. 데이터 파이프라인이 곧 진입장벽입니다.
- **(추론) 하이퍼/셋업 미공개로 재현성 약화** — 본문은 $`K=2048`$, $`d\ll D`$, 8-layer ViT 외에 $`\beta`$ · $`\lambda_{\text{vis}}`$ · $`\lambda_{\text{mask}}`$ · $`p_{\min}`$ · $`p_{\max}`$ · $`\tau`$ ·옵티마이저·스케줄·GPU를 명시하지 않아, 보고된 수치를 독립 재현하기 어렵습니다.
- **(추론) 정규화·압력 스케일이 데이터셋 특정적** — 촉각 맵을 $`[0,1]`$ 단일채널 224×224로 정규화한 전제가 특정 센서/리그의 압력 표현에 묶여 있어, cIoU/RMSE의 절대값이 다른 촉각 포맷과 직접 비교되기 어렵습니다.

---

## ♻️ 재현성

- **본문 확보** — arXiv HTML 전문 확보(2606.19161v1, CC BY 4.0).
- **코드 / 데이터** — 본문·메타에 공개 GitHub/HuggingFace/프로젝트 URL이 확인되지 않습니다(존재 시 추후 갱신 필요). HT-Bench 데이터 공개 여부·라이선스·다운로드 경로는 원문에 명시되지 않음.
- **하드웨어** — full-hand 촉각 센싱 리그·수집 환경의 구체 사양(센서 종류·해상도·샘플레이트) 미기재. 촉각 맵은 224×224 단일채널로 정규화되어 사용.
- **학습 설정** — $`K=2048`$, factorized 병목 $`d\ll D`$, 8-layer ViT encoder만 명시. 그 외 손실 가중치·마스킹 확률 범위·restart 임계·옵티마이저·스케줄·연산자원은 미공개.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P2(structured multimodal observation fusion)** — 본 논문의 HandTouch는 비전–촉각 인코더로, P2의 D10(heterogeneous modality fusion beyond concat)·D11(proprio-tactile-force token construction)·D12(topology-aware encoding + hand-level aggregation)에 직접 닿습니다. cross-attention으로 시각을 촉각에 주입하는 방식은 P2 핀 논문 **ViTacFormer**(cross-attention visuotactile)와 같은 계열이며, full-hand를 손가락/손바닥 부위 단위로 마스킹하는 Regional Masking은 "per-finger/palm contact attribution preserved"라는 P2 의도와 정렬됩니다.
- **P0(VLA datasets & benchmarks)** — HT-Bench 자체가 D26(benchmark/eval scouting scope)의 대상이며, full-hand 촉각 대규모 corpus는 D25(tactile/torque data scouting), egocentric 우선은 D24(priority data axis)와 연결됩니다. 다만 데이터/코드 공개·라이선스가 본문에 없어 D27(license/usability bar)은 미충족 상태로 보류.
- **Identity 긴장/지지** — Identity는 촉각 인코더가 "swappable sensor head + common token format"이어야 한다고 못 박는데(P2), HandTouch의 공유 이산 codebook은 그 "common token format"의 한 구현 후보로 **지지** 신호입니다. 반대로 우리 타깃 하드웨어는 **fingertip** 기반(Sharpa Deform Map ~320×240/지문)인데 HT-Bench는 **full-hand map** 설정이라, 센서 모달리티 불일치가 **긴장**으로 남습니다.
- **경쟁자 함의** — P2 Tracked Literature의 ViTacFormer 대비 "대규모 멀티태스크 벤치마크 + 이산 토큰 인코더"라는 새 비교축을 제공. 직접 정책 경쟁자는 아님(표현 학습 단계).

---

## ✨ 핀 논문 대비 델타

- **vs. ViTacFormer (P2 핀, cross-attention visuotactile)** — ViTacFormer가 cross-attention 비주오택타일 융합을 정책/시퀀스 맥락에서 다뤘다면, HandTouch는 (1) **공유 이산 codebook(factorized VQ)** 위에 표현을 세우고, (2) 공간→교차모달→시간의 **점진 3단계 자기지도** 커리큘럼으로 학습하며, (3) full-hand를 손가락/손바닥 부위로 마스킹하는 **Regional/Complete dual masking**을 도입한 점이 새롭습니다.
- **vs. 기존 촉각 벤치마크(Sparsh/AnyTouch 2/OpenTouch 등, Table 1)** — full-hand 지원 + 멀티태스크 + 멀티씬 + **task-level OOD split**을 동시에 충족하는 첫 구성으로 제시됩니다(저자 주장, Table 1).
- **순수 VQ-VAE 촉각 인코더 대비** — 같은 이산화 계열이지만 retrieval에서 VQ-VAE가 급락하는 반면 HandTouch는 정렬/시간 목표를 더해 SOTA를 회복 — "재구성만으로는 부족"을 같은 실험에서 보여줍니다.

---

## ⚙️ 의사결정 함의

- **촉각 토큰 포맷(D11)** — 우리 per-finger proprio-tactile token 구성에서 "연속 임베딩 vs. **공유 이산 codebook**" 선택지가 생깁니다. 채택 시 구체 config: codebook 크기 `K`(논문 2048), factorized 병목 `d`, commitment 가중치 `β`(Eq. 2), codebook restart 임계 `τ` + EMA 사용추적이 새 하이퍼로 추가됩니다.
- **자기지도 사전학습 목표(D10/D12)** — 촉각 인코더를 정책 학습 전 **masked tactile inpainting + RGB→Tac synthesis**로 사전학습하는 보조 단계를 둘 수 있습니다. loss term으로 Eq. (4)의 `λ_vis`/`λ_mask`(masked 영역 강조: `λ_mask > λ_vis`)와 Eq. (3)의 masking 커리큘럼 확률 `p_min`/`p_max`가 도입됩니다.
- **평가 지표 추가** — 촉각 복원/합성 품질에 **cIoU**(접촉 영역 IoU)를 RMSE와 병행 도입. RMSE만 보면 매끄러운 예측이 과대평가되는 함정을 피하는 보조 지표로 유용.
- **데이터 우선순위(D24/D25)** — full-hand 촉각 + egocentric paired 대규모 corpus가 실재(또는 곧 공개)하면 P0 스카우팅에서 우선 검토 대상. 단, 라이선스·다운로드 가능성(D27) 확인이 선결.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 체크) 센서 모달리티 불일치** — HT-Bench는 224×224 full-hand 압력 맵 설정. 우리 타깃은 fingertip optical(Sharpa Deform Map, ~320×240/지문)입니다. codebook/인코더를 가져오기 전에, 우리 촉각 표현을 "손 전체 단일 맵"으로 렌더할 수 있는지부터 확인해야 합니다(불가하면 아키텍처가 그대로 이식 안 됨).
- **데이터/코드 미공개 리스크** — 공개 repo가 확인되지 않아, HT-Bench 데이터·가중치 없이는 사전학습 이득을 직접 재현 불가. 우리 데이터로 재학습 시 보고 수치는 참조용에 불과.
- **표현 우위 ≠ 정책 우위** — 모든 평가가 표현 수준(retrieval/inpainting/synthesis/prediction). 우리 스택에 붙일 땐 "촉각 인코더 품질 → dexterous 정책 성공률" 전이가 입증되지 않았으므로, 우리 in-hand reorientation 같은 다운스트림에서 별도 측정 필요.
- **하이퍼 미공개로 인한 재현 변동성** — `β`·`λ`·`p_min/max`·`τ`·옵티마이저·스케줄이 비어 있어, 3단계 학습을 재구성하면 우리 환경에서 성능 재현이 흔들릴 수 있습니다. 단계별 frozen/trainable 모듈 경계만이라도 먼저 고정해 ablation 비용을 줄여야 합니다.
- **이산 codebook collapse** — restart 메커니즘 없이 VQ를 옮기면 코드북 붕괴로 표현력이 무너질 수 있습니다. EMA 사용추적 + restart를 같이 이식하는 것이 전제입니다.

---

## 💡 컨텍스트 제안

- **P0/P2 후보 추적 등재 제안** — HT-Bench를 P0 §5 benchmark 추적군의 "full-hand 촉각 + egocentric 멀티태스크 벤치마크" 후보로, HandTouch를 P2 §5의 visuotactile 인코더 비교군(ViTacFormer 인접)으로 추적 검토. 단, 데이터/코드 공개 확인 전까지는 D27 미충족으로 표시. (context 파일은 수정하지 않으며 제안만 남깁니다.)

> 💡 base 매핑은 `/implement-design analysis/2606.19161/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
