# Paper Analysis — Heterogeneous Tactile Transformer

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Heterogeneous Tactile Transformer |
| 저자 | Jianxin Bi, Qiang Wang, Jayaram Reddy, Kelvin Lin, Soibkhon Khajikhanov, Ruihan Gao, Harold Soh (National University of Singapore · Carnegie Mellon University · Smart Systems Institute, NUS) |
| 링크 | [arXiv:2606.29948](https://arxiv.org/abs/2606.29948) · [Website](https://jxbi1010.github.io/htt-gh-page/) |
| 발행일 / 버전 | 2026-06-29 제출 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-07-01 |
| 관련 Pillar | P2, P0, P3 |
| 태그 | tactile, force, dataset |

<!-- 본문 확보 retrieval ladder 기록 (verbatim):
  1. curl --fail "https://arxiv.org/abs/2606.29948"   → 200 (메타/초록 확보)
  2. curl --fail "https://arxiv.org/html/2606.29948"  → 200 (전문 확보, 260KB)
  모든 수치/인용은 arXiv HTML 본문에서 받은 그대로. -->

---

## 🧭 한 줄 요약 (TL;DR)

HTT 는 서로 raw 출력 구조가 다른 이종(optical-based vs array-based) 촉각 센서를 **센서별 인코더 + 공유 transformer trunk** 구조로 묶고, **per-modality masked reconstruction(MAE) + paired 센서 간 cross-modal alignment** 로 자가지도(self-supervised) 사전학습하는 촉각 백본입니다. 이를 위해 UMI 로 수집한 4개 센서·`1.6`M 동기화 paired frame 규모의 HPT 데이터셋을 함께 공개하며, object classification·force·slip·실제/시뮬 조작 task 에서 학습된 표현이 새 task 와 **사전학습에서 보지 못한 새 센서**로 전이됨을 보입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 촉각 센서는 본질적으로 이종적입니다. 한 센서에서 학습한 모델을 다른 센서에 그대로 쓸 수 없어, 다양한 촉각 데이터를 대규모로 모아 접촉 집약적(contact-rich) 조작 정책을 학습하기 어렵습니다.
- **기존 접근의 한계** — 촉각 표현학습은 대부분 GelSight 류 optical 센서에 집중되어 있고(T3, SITR, AnyTouch 등), optical 데이터만으로 학습한 모델은 array-based 신호를 직접 받지 못하며 고주파 force/slip cue 가 중요한 task 에 약합니다.
- **본 논문의 가설** — optical 과 array-based 센서를 **공유 latent 공간에 정렬**하되 각 센서 클래스의 구조와 강점은 보존하면, 두 센서 계열을 모두 다루는 이종 촉각 백본을 만들 수 있다는 것입니다.
- **왜 지금 중요한가** — 시간·공간적으로 동기화된 optical + array-based 촉각 데이터셋이 지금까지 없었고(대부분 optical-only), UMI 기반 저비용 paired 수집으로 이 공백을 메울 수 있게 되면서 이종 촉각 사전학습이 처음으로 실증 가능해졌습니다.

---

## 🧩 핵심 기여

- **HPT 데이터셋** — optical(GelSight Mini, 9DTact) + array-based(Xela, TAC-02) 4개 센서에 걸친 `1.6`M paired frame 대규모 촉각 데이터셋. UMI 로 수집한 시간·접촉 동기화 cross-sensor 데이터를 이종 촉각 표현학습 연구용으로 제공합니다.
- **HTT 프레임워크** — MAE 방식 masked reconstruction 과 **양방향 cross-sensor prediction** 을 결합해 이종 촉각 센서에 걸친 공유 표현을 학습하는 self-supervised 프레임워크.
- **포괄적 평가** — 촉각 지각(object classification / force estimation / slip detection), 시뮬(ManiFeel Peg Insertion·Bulb Installation), 실제 로봇(toy screw·grasp tofu) 3계층에서 전이성과 새 센서 적응을 검증. 특히 실제 로봇 task 는 **사전학습에서 보지 못한 Sharpa 손끝 센서**로 zero-shot 적용해 백본으로서의 재사용성을 확인합니다.

---

## 🔑 기술 키워드

- **Heterogeneous tactile sensors** — 서로 transduction 원리·출력 형식이 다른 촉각 센서군. 본 논문은 optical-based(이미지)와 array-based/taxel(시계열 force) 두 계열을 대상으로 삼습니다.
- **Optical tactile sensor** — GelSight·9DTact 처럼 탄성체 변형을 카메라로 찍어 접촉 형상·질감을 추론하는 센서. 공간 정보는 풍부하나 프레임률에 제약.
- **Array-based (taxel) sensor** — Xela·TAC-02 처럼 분산 감지 소자로 force/pressure 를 직접 측정하는 센서. 고주파·force 민감하나 공간 해상도가 낮음.
- **Masked Autoencoder (MAE)** — 입력 토큰의 일부만 보고 가린 토큰을 복원하도록 학습하는 자가지도 방식. 각 센서가 자기 raw 신호에서 구조·물리 특징을 뽑도록 하는 per-modality 목표.
- **Cross-modal alignment** — paired 센서 간에 한 센서의 표현으로 다른 센서의 가려진 표현을 예측하게 해, 서로 다른 모달리티를 공유 latent 공간에 정렬하는 목표.
- **Shared transformer trunk** — 센서별 인코더가 뽑은 토큰 임베딩을 공통 latent 공간에서 처리하는 단일 transformer. downstream 에서 인코더와 함께 재사용되는 백본 본체.
- **Stop-gradient (sg)** — alignment 회귀 타깃에 gradient 를 끊어 표현 붕괴(collapse)를 막는 장치. BYOL/SimSiam 계열의 붕괴 방지 트릭.
- **Cross-attention predictor** — source 임베딩 + 가시(visible) target 임베딩을 받아 가려진 target 임베딩을 예측하는 cross-attention transformer. 정렬 손실의 예측기.
- **Universal Manipulation Interface (UMI)** — 로봇 없이 in-the-wild 로 조작 데이터를 수집하는 그리퍼 인터페이스. 여기서는 두 센서를 마주보게 장착해 동기화 paired 촉각을 수집하는 도구.
- **Phased alignment schedule** — 초기 warmup 동안 정렬 손실 가중치 `` $`\alpha_{t}`$ `` 를 0 으로 두어 인코더가 센서별 특징을 먼저 학습하게 하고, 이후 최대값까지 램프업하는 단계적 스케줄.

---

## 🔬 방법론

### 직관

HTT 가 푸는 근본 문제는 "촉각 센서마다 데이터 구조가 달라 표현을 공유할 수 없다"는 것입니다. optical 센서는 이미지를 내놓고 array 센서는 감지 소자별 시계열을 내놓기 때문에, 하나의 인코더로 둘을 삼킬 수 없습니다. 발상은 두 단계로 나뉩니다 — 먼저 센서마다 전용 인코더로 자기 신호를 토큰화·인코딩하되, 그 위에 **공유 trunk** 를 두어 모두 같은 임베딩 차원의 공통 latent 로 사영합니다. 그러면 구조는 센서별로 보존하면서도 표현 공간은 하나로 묶입니다.

학습 목표도 두 갈래입니다. 첫째, 각 센서가 자기 raw 신호에서 쓸 만한 특징을 뽑도록 MAE 식으로 일부 토큰을 가리고 복원시킵니다(per-modality). 둘째, 마주보게 장착돼 **동시에 같은 접촉을 측정한** paired 센서를 이용해, 한 센서의 표현으로 상대 센서의 가려진 표현을 예측하게 합니다(cross-modal). 이 정렬이 optical 의 풍부한 공간 정보와 array 의 force cue 를 서로 결속시켜, 어느 한 센서만으로는 못 얻는 표현을 만듭니다.

핵심 설계 안전장치가 두 개 있습니다. 하나는 **stop-gradient** — 정렬의 회귀 타깃에 gradient 를 끊어 두 표현이 서로를 향해 붕괴하는 것을 막습니다. 다른 하나는 **단계적 스케줄** — 처음엔 정렬을 끄고 MAE 만으로 센서별 특징을 먼저 세운 뒤 정렬을 켜며, 그마저도 gradient 를 인코더 출력에서 차단해 정렬이 인코더가 아니라 predictor·trunk 만 갱신하도록 합니다. 즉 "센서별 강점 보존"과 "공유 정렬"이 충돌하지 않게 학습 경로를 물리적으로 분리한 것입니다.

![Figure 1 — HTT 프레임워크 개요](https://arxiv.org/html/2606.29948/x1.png)

> "Figure 1: Heterogeneous Tactile Transformer (HTT). HTT is pretrained on the Heterogeneous Paired Tactile (HPT) dataset, which consists of $`1.6`$ M synchronized paired frames across four distinct sensors with a UMI device. HTT adopts sensor-specific encoders and a shared transformer trunk as core modules. Data from each sensor is patchified, fed into a sensor-specific encoder, and forwarded to the shared transformer trunk. During pretraining, decoders are used to reconstruct each sensors' input data and cross-sensor predictors are used to predict masked target sensor embedding — aligning the shared latent space across heterogeneous sensors." (§4)
> (한글 해설 — 센서별 인코더 → 공유 trunk → (복원용 decoder + 정렬용 cross-sensor predictor) 의 두 갈래 학습 경로가 이 그림 한 장에 압축돼 있습니다. downstream 에서는 decoder·predictor 를 버리고 인코더+trunk 만 씁니다.)

### 아키텍처

HTT 는 MAE 설계를 따르며 센서별 인코더·디코더, 공유 trunk, cross-modal predictor 로 구성됩니다. 구조적 호환을 위해 모든 센서 임베딩은 동일한 embedding 차원에서 작동하도록 사영됩니다.

> "Each training instance comprises synchronized multi-sensor data captured within a fixed $`\tau=0.2\,\text{s}`$ temporal interaction window." (§4.1)
> (한글 해설 — 학습 인스턴스의 기본 단위가 `` $`\tau=0.2\,\text{s}`$ `` 접촉 윈도우이며, 이 안에서 서로 다른 센서의 프레임 수가 다르게 잡힙니다(optical 은 프레임, taxel 은 고주파 시계열).)

입력 토큰화는 센서 계열별로 다릅니다.

> "For optical-based sensors, individual frames are resized to $`224\times 224`$ and tokenized into non-overlapping spatial patches following standard Vision Transformer (ViT). For array-based sensors, the high-frequency multi-dimensional time series is tokenized into non-overlapping temporal patches. For all modalities, we subtract raw tactile signal with a non-contact reference frame before processing by model." (§4.1)
> (한글 해설 — optical 은 ViT 식 공간 패치, array 는 시간 패치로 토큰화하고, 모든 모달리티는 **비접촉 기준 프레임을 뺀** 배경 제거 신호를 입력으로 씁니다 — 접촉으로 인한 변화만 남겨 인코더 부담을 줄입니다.)

아키텍처는 네 종류 모듈로 구성됩니다. 센서 집합을 `` $`\mathcal{I}`$ ``, `` $`i\in\mathcal{I}`$ `` 라 할 때:

- **Encoders (`` $`\mathcal{E}_{i}`$ ``)** — 센서별 인코더. optical 은 ViT, array 는 self-attention transformer 로 토큰을 임베딩합니다.
- **Shared Trunk (`` $`\mathcal{T}`$ ``)** — 토큰 임베딩을 공유 latent 공간에서 처리하는 단일 transformer trunk.
- **Decoders (`` $`\mathcal{D}_{i}`$ ``)** — masked reconstruction 을 담당하는 센서별 디코더.
- **Predictors (`` $`\mathcal{P}_{ij}`$ ``)** — source 임베딩과 가시 target 임베딩으로부터 가려진 target 임베딩을 예측하는 cross-attention transformer.

세부 구성(Appendix A.1): 모든 모듈이 embedding 차원 `` $`D=192`$ `` · 어텐션 head `` $`3`$ `` 개를 공유하고, optical 인코더·디코더는 depth `` $`3`$ ``, taxel 인코더는 depth `` $`2`$ ``, 공유 trunk 는 depth `` $`9`$ ``, cross-modal predictor 는 depth `` $`3`$ `` 입니다. CLS 토큰은 쓰지 않고 trunk 는 입력 토큰 시퀀스를 그대로 유지합니다. optical 입력(`` $`224\times 224\times 3`$ ``, 크기 `` $`2`$ `` 의 time tubelet `` $`2`$ ``)은 tubelet 당 `` $`196`$ `` 토큰, taxel 입력(20 또는 40 프레임)은 길이 `` $`4`$ `` 의 시간 패치로 나뉘어 Xela `` $`5`$ `` 토큰 / TAC-02 `` $`10`$ `` 토큰이 됩니다.

### 학습 목표 / 손실

**(1) MAE Reconstruction.** 센서별 인코더 `` $`\mathcal{E}_{i}`$ `` 와 공유 trunk `` $`\mathcal{T}`$ `` 가 가시 토큰 `` $`\mathbf{x}^{i}_{v}`$ `` 만 처리하고, 센서별 디코더 `` $`\mathcal{D}_{i}`$ `` 가 가려진 토큰 `` $`\mathbf{x}^{i}_{m}`$ `` 을 복원합니다. 손실은 모달리티에 대해 평균됩니다.

$$\mathcal{L}_{\text{MAE}}=\mathbb{E}_{i\sim\mathcal{I}}\left[\left\|\mathcal{D}_{i}\bigl(\mathcal{T}(\mathcal{E}_{i}(\mathbf{x}^{i}_{v}))\bigr)-\mathrm{norm}(\mathbf{x}^{i}_{m})\right\|_{2}^{2}\right],$$

> "where $`\mathrm{norm}(\cdot)`$ denotes the per-patch normalization (zero-mean, unit-variance) applied to the target as in standard MAE training. This reconstruction constraint forces the encoder-trunk system to retain high-fidelity localized details necessary to restore missing spatial or temporal signals." (§4.2)
> (한글 해설 — 타깃 `` $`\mathbf{x}^{i}_{m}`$ `` 은 표준 MAE 처럼 패치 단위 zero-mean·unit-variance 정규화(`` $`\mathrm{norm}(\cdot)`$ ``)를 거치며, 이 복원 제약이 인코더-trunk 가 국소 공간·시간 디테일을 보존하게 강제합니다.)

**(2) Cross-Modal Alignment.** 순서쌍 `` $`(i,j)`$ `` 에 대해, source 전체 임베딩과 가시 target 임베딩으로 가려진 target 임베딩을 예측합니다. `` $`\mathbf{z}^{i}=\mathcal{T}(\mathcal{E}_{i}(\mathbf{x}^{i}))`$ ``, `` $`\mathbf{z}^{j}=\mathcal{T}(\mathcal{E}_{j}(\mathbf{x}^{j}))`$ `` 를 각각 source·target 임베딩이라 하고 target 을 가시·가림 성분 `` $`\mathbf{z}^{j}_{v}`$ ``, `` $`\mathbf{z}^{j}_{m}`$ `` 으로 나눕니다.

$$\mathcal{L}_{\text{Align}}=\mathbb{E}_{(i,j)\sim\mathcal{S}}\bigl\|\mathcal{P}_{ij}(\mathbf{z}^{i},\mathbf{z}^{j}_{v})-\mathrm{sg}[\mathbf{z}^{j}_{m}]\bigr\|_{2}^{2}.$$

> "To prevent representation collapse, a stop-gradient $`\mathrm{sg}[\cdot]`$ is applied to the regression target. The alignment loss is averaged over the set $`\mathcal{S}`$ of all ordered sensor pairs in the dataset." (§4.2)
> (한글 해설 — predictor `` $`\mathcal{P}_{ij}`$ `` 가 `` $`\mathbf{z}^{j}_{m}`$ `` 을 예측하되 타깃에 stop-gradient(`` $`\mathrm{sg}[\cdot]`$ ``)를 걸어 두 표현이 서로를 향해 붕괴하는 것을 막고, 손실은 모든 순서쌍 집합 `` $`\mathcal{S}`$ `` 에 대해 평균합니다.)

**(3) Joint Pretraining.** 두 손실을 시간 의존 계수 `` $`\alpha_{t}`$ `` 로 결합합니다.

$$\mathcal{L}_{\text{HTT}}=\mathcal{L}_{\text{MAE}}+\alpha_{t}\cdot\mathcal{L}_{\text{Align}},$$

> "$`\alpha_{t}=0`$ during an initial warmup period so the encoders and trunk first develop sensor-specific features via MAE alone, after which $`\alpha_{t}`$ is ramped to its maximum value $`\alpha_{\max}=0.1`$. To further protect those features, we block alignment gradients at the encoder outputs, so that $`\mathcal{L}_{\text{Align}}`$ updates only the predictors $`\mathcal{P}_{ij}`$ and the shared trunk $`\mathcal{T}`$, while the encoders $`\mathcal{E}_{i}`$ are updated solely by $`\mathcal{L}_{\text{MAE}}`$." (§4.2)
> (한글 해설 — warmup 동안 `` $`\alpha_{t}=0`$ `` 으로 MAE 만 돌려 센서별 특징을 먼저 세운 뒤 `` $`\alpha_{\max}=0.1`$ `` 까지 램프업하고, 정렬 gradient 를 인코더 출력에서 차단해 인코더는 오직 MAE 로만, trunk·predictor 만 정렬로 갱신되게 학습 경로를 분리합니다.)

사전학습 후 디코더 `` $`\mathcal{D}_{i}`$ `` 와 predictor `` $`\mathcal{P}_{ij}`$ `` 는 버리고, 센서 인코더 `` $`\mathcal{E}_{i}`$ `` 와 공유 trunk `` $`\mathcal{T}`$ `` 만 downstream 에 사용합니다.

### 학습 셋업

- **데이터** — HPT paired unlabeled interaction data. UMI 로 마주보게 장착한 두 센서 쌍(Pair A: Xela ↔ 9DTact, Pair B: TAC-02 ↔ GS Mini)에서 press/twist/slide 를 포함한 unscripted 상호작용으로 수집. 사전학습 데이터와 평가 데이터는 **겹치지 않습니다**.
- **마스킹 비율** — MAE 재구성은 optical `` $`0.75`$ `` / taxel `` $`0.60`$ ``; cross-modal 예측은 predictor 가 full source 를 받고 target mask ratio optical `` $`0.90`$ `` / taxel `` $`0.80`$ `` 로 예측.
- **최적화** — AdamW, learning rate `` $`3\times 10^{-4}`$ ``, batch size `` $`256`$ `` paired sample/step. 처음 `` $`2{,}000`$ `` step 동안 `` $`3\times 10^{-6}`$ `` 에서 linear warmup 후 나머지 step 에 cosine decay 로 `` $`3\times 10^{-6}`$ `` 로 복귀. gradient clip `` $`1.0`$ ``.
- **단계 스케줄** — 총 `` $`50{,}000`$ `` step. 정렬 손실 가중치를 `` $`0`$ `` 에서 시작해 첫 `` $`20{,}000`$ `` step 동안 선형 증가시키고 이후 `` $`\alpha=0.1`$ `` 로 고정.

---

## 📊 실험 설정과 결과

평가는 Q1–Q5 로 조직됩니다 — Q1(HTT 사전학습이 이종 센서에서 유용한 표현을 주는가), Q2(distinct task 로 전이되는가), Q3(cross-sensor alignment 의 이득), Q4(contact-rich 정책 학습 부양), Q5(사전학습에서 못 본 새 센서 적응). 비교군은 **Scratch**(사전학습 없음), **T3**·**SITR**(optical-only 사전학습 표현), **MAE(ours)**(정렬 없는 HTT 변형), **HTT(ours)**(full).

### Object classification (20-class top-1 accuracy, %)

| Method | Xela | TAC-02 | 9DTact | GSMini | Overall |
|---|---|---|---|---|---|
| Scratch | 48.90 ± 1.45 | 22.49 ± 0.78 | 65.63 ± 1.73 | 53.13 ± 2.60 | 47.54 ± 1.64 |
| T3 | n/a | n/a | 51.44 ± 26.25 | 59.26 ± 5.25 | 55.35 ± 15.75 |
| SITR | n/a | n/a | 81.34 ± 4.41 | 74.31 ± 7.14 | 77.83 ± 5.78 |
| MAE (ours) | 56.68 ± 0.99 | 26.16 ± 0.43 | 90.08 ± 0.54 | 88.59 ± 0.71 | 65.38 ± 0.67 |
| HTT (ours) | 52.41 ± 0.84 | 26.20 ± 1.60 | 94.84 ± 1.61 | 91.35 ± 1.08 | 66.20 ± 1.28 |

> "On the two optical-based sensors, HTT outperforms the strongest baseline (SITR) by $`13.5\%`$ on 9DTact and $`17\%`$ on GSMini. T3 transfers poorly to 9DTact, suggesting that pretraining on a similar set of optical-based sensors does not generalize well to different optical-based sensors." (§5.2, Table 1)
> (한글 해설 — optical 센서에서 HTT 가 최강 baseline SITR 을 크게 앞서며(9DTact +13.5%, GSMini +17%), T3 는 9DTact 로 전이가 나빠 optical 끼리도 센서 차이로 표현이 무너짐을 보입니다.)

> "Alignment improves accuracy on the optical-based sensors ($`+4.8\%`$ on 9DTact, $`+2.8\%`$ on GSMini), but underperforms on Xela ($`-4.3\%`$). We attribute this asymmetry to an information imbalance between the paired modalities." (§5.2, Table 1)
> (한글 해설 — HTT vs MAE 차이가 정렬의 순효과입니다 — optical 은 상대 force cue 로 이득을 보지만, 정보량이 적은 Xela 는 짝지어진 optical 표현으로 살짝 끌려가 오히려 손해(-4.3%)를 봅니다. 분류 수준에서 정렬 효과는 혼재.)

### Force estimation (3D MAE, N ↓) & Slip detection (Macro-F1, % ↑)

![Figure 2 — force/slip 데이터 수집과 통계](https://arxiv.org/html/2606.29948/x2.png)

> "Figure 2: Force/slip data collection and dataset statistics. A1. A tactile sensor and a $`6`$ -D F/T sensor are mounted on a robot arm; a probe rig contacts the tactile sensor while synchronized tactile frames and ground-truth force are recorded for the force-estimation and slip-detection splits. A2. Example tactile frames collected with the four probe geometries. B1. The force range spans up to $`40`$ N normal and $`14`$ N shear. B2. Slip labels are heavily imbalanced ( $`13.6\%`$ static, $`1.2\%`$ incipient, $`85.2\%`$ slide), making the rare static and incipient classes challenging to detect." (§3.1)
> (한글 해설 — force/slip split 은 UMI paired 수집이 아니라 4종 probe rig + 6-D F/T 센서로 별도 수집됩니다(distribution shift 의 근거). slip 라벨이 85.2% slide 로 심하게 불균형해 macro-F1 로 평가하는 이유를 이 그림이 뒷받침합니다.)

| | Force: Xela | TAC-02 | 9DTact | GSMini | Overall | Slip: Xela | TAC-02 | 9DTact | GSMini | Overall |
|---|---|---|---|---|---|---|---|---|---|---|
| Scratch | 1.225 | 0.705 | 1.255 | 1.260 | 1.111 | 29.80 | 31.77 | 31.00 | 32.00 | 31.14 |
| T3 | n/a | n/a | 2.678 | 1.197 | 1.938 | n/a | n/a | 31.27 | 38.25 | 34.76 |
| SITR | n/a | n/a | 1.085 | 1.373 | 1.229 | n/a | n/a | 41.77 | 36.36 | 39.07 |
| MAE | 0.762 | 0.516 | 0.574 | 0.803 | 0.664 | 54.46 | 33.45 | 49.70 | 68.86 | 51.62 |
| HTT | 0.695 | 0.508 | 0.606 | 0.736 | 0.636 | 54.21 | 45.45 | 53.09 | 72.65 | 56.35 |

> "The optical-only baselines often fail to transfer: T3 doubles the 9DTact force MAE relative to Scratch ($`2.678`$ vs $`1.255`$), SITR worsens force on GSMini ($`1.373`$ vs $`1.260`$) ... an issue our objective avoids because HTT pretraining is anchored to force-rich array data through cross-sensor pairing." (§5.3, Table 2)
> (한글 해설 — optical-only 표현은 force-sensitive task 로 전이가 무너지지만(T3 는 9DTact force MAE 를 Scratch 대비 2배로 악화), HTT 는 cross-sensor pairing 으로 array 의 force 정보에 앵커돼 이를 피합니다.)

> "HTT also outperforms MAE on three of four sensors in both tasks, with the largest gain on slip detection ($`+12.0`$ macro-F1 on TAC-02). ... cross-modal alignment binds these complementary signals across paired optical and array sensors, yielding a representation that resists collapsing onto the dominant class under heavy imbalance." (§5.3, Table 2)
> (한글 해설 — physics-grounded task 에서는 정렬 효과가 뚜렷해집니다 — slip 은 force cue + 세밀한 공간 접촉 특징을 모두 요구하는데, 정렬이 이 둘을 결속해 heavy imbalance(85.2% slide) 하에서도 다수 클래스로 붕괴하지 않는 표현을 만듭니다. TAC-02 slip 에서 MAE 대비 +12.0 macro-F1.)

### 실제 로봇 (Sharpa hand · Franka, camera-free)

![Figure 3 — 실제 toy screw / grasp tofu 실험](https://arxiv.org/html/2606.29948/x3.png)

> "Figure 3: Real World Toy Screw and Grasp Tofu Experiments. Left: Task setup and tactile image from the Sharpa finger tip. Middle: Final rotation of screw; more than 600 degrees (close to tight) is considered success. Right: Grasp tofu completion status (20 rollouts), slip is the most common failure mode. On both tasks, our HTT representations achieve the best results." (§5.4.1)
> (한글 해설 — camera-free Sharpa hand 셋업에서 HTT 임베딩이 두 접촉 집약 task 모두 최고 성공률을 내는 것을 시각화합니다. screw 는 600도 이상 회전, tofu 는 slip 이 주 실패 모드.)

관측 조건 3종 비교 — `qpos`(22-D 손 관절만, 촉각 없음), `wrench`(qpos + 손끝 5개 센서의 6-D force), `HTT`(qpos + 손끝 촉각의 HTT 임베딩). **Sharpa 손끝 센서는 사전학습에 없던 센서로, 9DTact 인코더를 그대로 적용한 zero-shot 적응입니다.**

> "Without tactile feedback, the qpos-only policy collapses on both tasks ($`5\%`$ on each) ... Adding $`6`$ -D wrench improves performance (screw: $`50\%`$ , tofu: $`35\%`$ ), and replacing the wrench with HTT embeddings improves further (screw: $`95\%`$ , tofu: $`55\%`$ )." (§5.4.1)
> (한글 해설 — 촉각 없이는 두 task 모두 5% 로 붕괴, raw 6-D wrench 로 개선(screw 50% / tofu 35%), wrench 를 HTT 임베딩으로 교체하면 더 개선(screw 95% / tofu 55%)됩니다.)

> "in $`19/20`$ rollouts the policy maintains grip across 2 rotation cycles and tightens the screw fully, whereas the wrench policy loses contact during the second cycle and stalls ... which a $`6`$ -D wrench vector cannot represent but HTT embeddings can." (§5.4.1)
> (한글 해설 — screw 의 주기적 regrip 은 "손 pad 위 어디에서 접촉이 일어나고 어떻게 이동하는가"라는 공간 접촉 특징을 요구하는데, 6-D wrench 벡터는 이를 담지 못하고 HTT 임베딩은 담습니다. tofu 에서는 slip 이 주 실패(wrench 12/20, HTT 8/20)이고 wrench 는 1/20 으로 tofu 를 으깨는 반면 HTT 는 한 번도 으깨지 않습니다.)

### ManiFeel 시뮬 (success rate, 3 seeds × 50 rollouts)

| Method | Peg Insertion | Bulb Installation |
|---|---|---|
| tacRGB | 0.21 ± 0.02 | 0.72 ± 0.04 |
| T3 | 0.23 ± 0.02 | 0.73 ± 0.06 |
| SITR | 0.35 ± 0.01 | **0.77 ± 0.04** |
| HTT(RGB) | 0.44 ± 0.04 | **0.77 ± 0.02** |
| HTT(FF) | **0.48 ± 0.12** | 0.76 ± 0.02 |

> "both HTT (RGB) and HTT(FF) outperforms baselines in peg insertion. Performance converges near $`0.77`$ for all methods in bulb installation, HTT is also among the best performing models." (§5.4.2, Table 3)
> (한글 해설 — TacFF 인코더는 pretrained shared chunk 를 백본으로 새 인코더·디코더를 초기화해 MAE 로 학습한 것으로, peg insertion 에서 HTT 가 baseline 을 앞서고 bulb 는 모두 0.77 부근으로 포화합니다. 촉각 모달리티에 무관한 접촉 임베딩임을 재확인.)

---

## ⚖️ 한계

- **저자 명시 — 센서 계열 커버리지 제한** — 사전학습이 optical·array 두 계열에만 한정됩니다. magnetic/fluid 기반 등 다른 감지 계열로 정렬을 확장하는 것이 다음 과제로 남는데, 이는 곧 현재 백본이 "이종"이라 해도 **두 축뿐인 이종**이라는 뜻이고, 새 계열 추가 시 정렬 효과가 유지될지는 미검증입니다.
- **저자 명시 — cross-family 페어링만 존재** — paired 데이터가 전부 optical ↔ array 교차 계열이라, **같은 계열 두 센서(optical↔optical 등)를 짝지었을 때** 정렬이 어떻게 작동하는지는 탐구되지 않았습니다. 계열 내 정렬이 오히려 표현을 동질화해 이득이 줄 가능성도 열려 있습니다.
- **저자 명시 — 공간 대응 부재** — HPT 는 센서를 시간·접촉으로만 짝지을 뿐 기하 공간으로는 짝짓지 않습니다. optical 의 어느 패치가 array 의 어느 taxel 에 대응하는지를 명시적으로 모델링하지 않아, 정렬이 "전역 임베딩 수준"에 머물고 finer-grained 접촉 대응은 놓칩니다.
- **추론된 갭 — array 센서 성능 자체가 낮음** — Table 1 에서 TAC-02 는 어느 방법이든 26% 안팎(20-class), Xela 도 최대 57% 수준으로, 절대 성능이 낮아 array 센서에서의 표현 품질이 태생적으로 약합니다. 정렬이 optical 은 돕지만 Xela 는 오히려 해치는(-4.3%) 비대칭도 여기서 비롯되며, "정보량 적은 센서가 상대에게 끌려가는" 리스크가 구조적으로 남습니다.
- **추론된 갭 — 정렬 이득의 조건 의존성** — 정렬 효과가 task 성격에 강하게 의존합니다(분류에선 혼재, force/slip 에선 뚜렷). "언제 정렬을 켜야 이득인가"에 대한 사전 판단 기준이 없어, downstream task 마다 MAE-only vs HTT 를 실측 비교해야 하는 부담이 남습니다.
- **추론된 갭 — 소규모 실제 평가** — 실제 로봇 결과가 task 2종·rollout 20회 규모로, screw 95% 같은 큰 이득이 통계적으로 얼마나 견고한지(신뢰구간·seed 변동) 본문에서 확인하기 어렵습니다.

---

## ♻️ 재현성

- **코드 / 데이터 / 체크포인트** — 초록·본문에서 "will be released upon publication" 로 명시. 프로젝트 페이지([Website](https://jxbi1010.github.io/htt-gh-page/))가 공개 창구로 안내되나, 분석 시점 기준 아직 미공개(공개 예정).
- **하이퍼파라미터** — Appendix A.1 에 아키텍처 depth/차원, 패치·마스킹 비율, 옵티마이저·스케줄이 상세히 명시되어 재현 스펙은 비교적 완비. baseline(Scratch/T3/SITR) 세부는 Appendix B.
- **하드웨어 / 데이터 수집** — UMI 기반 3D 프린트 모듈 셸로 두 센서를 마주보게 장착하는 저비용 셋업. force/slip 라벨은 6-D F/T 센서 + 4종 probe rig 로 수집하고, slip 은 friction-coefficient 시계열에 two-sided Page CUSUM change-point detector 를 적용해 static/incipient/gross 3클래스로 라벨링(Appendix D).

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P2(구조적 멀티모달 관측 융합) — 핵심 연결.** HTT 는 이종 촉각 센서에 걸친 **learned 공유 표현**을 만드는 백본으로, D11(proprio-tactile-force token construction — "swappable sensor head + common token format")의 정확한 청사진에 해당합니다. 센서별 인코더 + 공유 trunk = "swappable head + common token format" 그 자체이며, cross-modal alignment 는 D10(heterogeneous modality fusion beyond concat — cross-attention/asymmetric fusion)의 사전학습판 근거입니다. 우리 P2 anti-topic("tactile hardware design without a learned representation")과 정반대로 **표현을 학습**하는 논문이라 지지 방향으로 정합.
- **P0(VLA Datasets & Benchmarks) — HPT 데이터셋.** `1.6`M paired frame 규모의 optical+array 동기화 촉각 데이터셋으로, D25(tactile/force/torque data scouting — 희소성을 first-class gap 으로 취급)에 직결됩니다. RH20T(wrist F/T)와 달리 **손끝급 optical+taxel 동기화**라는 결이 다른 희소 촉각 코퍼스이며, 공개 시 P0 카탈로그(`catalogs/datasets.md`) 등록 후보.
- **P3(System0 접촉 안정화) — slip/force 지각.** HTT 가 slip detection·force estimation 에서 baseline 을 크게 앞서는데, D15(System0 관측: tactile + finger joint state)·D18(physics-grounded 접촉 표현)의 관측 인코더 후보로 읽힙니다. 특히 slip 3클래스(static/incipient/gross) 라벨링과 macro-F1 개선은 System0 의 slip 억제 reward 설계에 직접적인 참고.
- **Identity 지지** — MASTER Identity 의 "structured multimodal observation fusion — per-finger proprio-tactile binding beyond flat concat" 축을 표현학습 차원에서 뒷받침. camera-free 로 촉각만으로 contact-rich task 를 푸는 실증은 "dexterity 는 접촉에 달렸다"는 전제를 강화합니다.
- **경쟁자 함의** — P2 §5 비핀 Sparsh(Meta FAIR, "tactile foundation model, D11 pretraining deferred")의 직접 경쟁·후속선상. HTT 는 Sparsh 가 미룬 "이종 센서 통합 사전학습"을 optical+array 로 실제 수행했다는 점에서, D11 pretraining deferred 트리거를 앞당길 후보.

---

## ✨ 핀 논문 대비 델타

- **vs Sparsh(P2 §5 비핀, tactile foundation model)** — Sparsh 는 optical 계열 촉각 파운데이션 모델로 pinned 되어 있으나 "D11 pretraining deferred" 상태입니다. HTT 는 여기서 **optical + array-based 를 하나의 백본에 통합**하고, self-supervised 목표에 **paired-data cross-modal alignment** 를 추가했다는 점이 진짜 새로움입니다. optical-only 표현(T3/SITR)이 force/slip 으로 전이 실패하는 것을 실증하고, cross-sensor pairing 으로 이를 회피합니다.
- **vs ViTacFormer(P2 핀, cross-attention visuotactile fusion)** — ViTacFormer 는 vision↔tactile 을 정책 안에서 cross-attention 으로 융합하는 supervised 경로입니다. HTT 는 융합 대상이 **tactile↔tactile(이종 센서 간)**이고, 정책과 무관한 **self-supervised 사전학습**으로 재사용 백본을 만든다는 점이 다릅니다.
- **vs RH20T(P0 핀, wrist F/T 코퍼스)** — RH20T 는 로봇 wrist 6-axis F/T 를 담은 희소 코퍼스입니다. HPT 는 손끝급 **optical + array taxel 동기화 paired** 데이터라 촉각 세밀도와 이종성 축이 근본적으로 다르며, D25 의 "새 contact-modality release" 로서 상보적.
- **vs UniForce / UniTac / Touch-to-touch(Related Work 인용)** — UniForce 도 UMI 로 이종 촉각을 동기 수집하나 latent force 예측에 집중, UniTac 은 non-vision 센서 간 공유 표현, Touch-to-touch 는 일방향 매핑. HTT 는 **재사용 가능한 일반 표현**을 optical↔array cross-modal alignment 로 학습하고 지각+조작 전이까지 평가한다는 폭이 차별점.

---

## ⚙️ 의사결정 함의

- **D11 tactile 인코더 설계** — "센서별 인코더 + 공유 trunk + common token format" 를 우리 tactile 브랜치의 기본 골격으로 채택 검토. 구체 config: 인코더 depth(optical 3 / taxel 2), 공유 trunk depth 9, `embed_dim=192`, `num_heads=3`, no CLS token, 비접촉 기준 프레임 background subtraction 전처리.
- **사전학습 손실 항** — 우리 tactile 사전학습에 `L_MAE`(패치 정규화 타깃, mask 0.75 optical / 0.60 taxel) + `alpha_t · L_Align`(stop-gradient 타깃, target mask 0.90 optical / 0.80 taxel) 도입 검토. 특히 `alpha_t` **phased schedule**(warmup 20k step 동안 0→선형증가, 이후 `alpha=0.1` 고정) 과 **인코더 출력에서 alignment gradient 차단**은 "센서별 강점 보존" 을 위한 직접 이식 가능한 레버.
- **slip 보조 헤드** — D11 의 "contact-binary + slip-binary aux heads (light)" 설계에 HTT 의 slip 3클래스(static/incipient/gross) 라벨링·macro-F1 평가 프로토콜을 참고. slip 은 force cue + 공간 접촉 특징을 동시 요구하므로 정렬 손실이 특히 유효.
- **하이퍼파라미터** — AdamW `lr=3e-4`, `batch=256` paired, warmup 2k step(`3e-6`→`3e-4`) + cosine decay, grad clip `1.0`, 총 50k step 을 tactile 사전학습 기본값 후보로 기록.
- **평가 메트릭 선택** — 촉각 표현 품질 측정 지표로 (a) 20-class object classification top-1, (b) 3D force MAE(N, ↓), (c) slip macro-F1(%, imbalance 강함 → accuracy 아닌 macro-F1) 3종을 우리 tactile 백본 회귀 스위트로 채택 검토.

---

## ⚠️ 먼저 검증할 실패 모드

- **[가장 싼 체크] 센서 하드웨어 불일치** — HTT 는 GelSight Mini/9DTact/Xela/TAC-02 로 학습됐고 우리 근거리 계획은 **Sharpa Deform Map**(~320×240/손끝 @30Hz, vision-based)입니다. 논문의 zero-shot 적용은 Sharpa 손끝에 **9DTact 인코더를 그대로** 얹은 것이므로, 우리 Sharpa 데이터 소량으로 "9DTact 인코더 zero-shot 임베딩이 유의미한 접촉 신호를 담는지"부터 먼저 확인해야 합니다(가장 저렴한 sanity check).
- **array 센서 취약성 전이** — Table 1 에서 array 센서(TAC-02 26%, Xela 57%) 절대 성능이 낮고 정렬이 Xela 를 -4.3% 로 해칩니다. 우리 스택이 array-based force 채널을 쓴다면, 정렬이 그 채널을 optical 쪽으로 끌어당겨 오히려 열화시킬 위험 → **modality dropout / 비대칭 정렬 가중치**로 완충 필요(D10 modality dropout 과 정합).
- **데이터 미공개 리스크** — HPT·코드·체크포인트가 "upon publication" 공개 예정이라 분석 시점엔 재현 불가. 손실·하이퍼는 Appendix 로 재구현 가능하나, **paired 수집 하드웨어(UMI + 마주보기 셸)** 없이는 cross-modal alignment 학습 데이터를 우리가 자체 생성해야 하며 이는 비용이 큼.
- **공간 대응 부재의 하방** — HTT 정렬은 시간·접촉 페어링만 쓰고 공간 대응이 없어, per-finger/palm **spatial attribution**(우리 D11·D12 의 핵심)을 직접 제공하지 않습니다. HTT 임베딩을 그대로 쓰면 "어느 손끝의 어느 위치 접촉"이라는 topology-aware 정보가 임베딩에 암묵적으로만 섞여, D12(topology-aware encoding) 요구와 어긋날 수 있음.
- **정렬 이득의 task 의존성** — 분류에선 정렬 이득이 혼재하므로, 우리 tactile 사전학습에 `L_Align` 도입 전에 **MAE-only vs +Align 을 우리 downstream(grasp 유지/slip 억제)에서 실측 비교**해 정렬이 실제로 이득인지부터 확인해야 합니다.
- **camera-free 전제** — 실제 로봇 이득이 "카메라 없음"이라는 극단 셋업에서 측정됐습니다. 우리 스택은 multi-camera spatial grounding(P2 D8)을 함께 쓰므로, 비전이 있을 때 HTT 촉각 임베딩의 marginal 이득이 얼마나 남는지는 별도 검증 대상.

---

## 💡 컨텍스트 제안

- **P0 §5 / catalogs** — HPT 데이터셋을 D25(tactile/torque scouting) 신규 릴리스로 **공개 시점에** `catalogs/datasets.md` 등록 후보로 대기 표시(현재 미공개라 즉시 핀 교체는 보류). RH20T(wrist F/T)와 상보적인 "손끝 optical+array 동기화" 축.
- **P2 §5** — Sparsh("D11 pretraining deferred") 옆에 HTT 를 **비핀 methodology-base 후보**로 추가 검토. Sparsh 가 미룬 이종 센서 통합 사전학습을 실제 수행한 후속선상이라, D11 pretraining deferred 트리거를 재검토할 근거. (핀 캡 8 준수 — 즉시 승격보다 후보 등재 제안.)
- 그 외 Decision 이동/트리거 변경 제안 없음. context 파일은 수정하지 않았습니다.
