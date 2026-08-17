# Paper Analysis — Spatial Forcing: Implicit Spatial Representation Alignment for Vision-language-action Model

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Spatial Forcing: Implicit Spatial Representation Alignment for Vision-language-action Model |
| 저자 | Fuhao Li, Wenxuan Song, Han Zhao, Jingbo Wang, Pengxiang Ding, Donglin Wang, Long Zeng, Haoang Li |
| 링크 | [arXiv:2510.12276](https://arxiv.org/abs/2510.12276) · [Website](https://spatial-forcing.github.io/) |
| 발행일 / 버전 | 2025-10-14 · v2 (2025-10-17 최종 수정) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-09 |
| 관련 Pillar | P4, P2 |
| 태그 | vla-arch, peft |

---

## 🧭 한 줄 요약 (TL;DR)

VLA 의 중간층 visual 임베딩을 사전학습된 3D foundation model(VGGT) 의 geometric 표현에 cosine alignment 시키는 보조 손실 하나만 추가해, 명시적 3D 입력(depth·point cloud) 이나 depth estimator 없이 VLA 에 공간 인지를 implicit 하게 주입하는 학습 전략(Spatial Forcing) 입니다. 추론 시 추가 구조·연산이 전혀 없으면서 LIBERO SOTA, 최대 3.8× 빠른 수렴, 큰 데이터 효율 개선을 동시에 달성합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 대부분의 VLA 는 2D 데이터만으로 사전학습된 VLM 위에 올라가 있어 정확한 공간 인지(spatial awareness) 가 결여되어 있고, 이는 3D 물리 세계에서의 정밀 동작을 저해합니다.
- **기존 접근의 한계** — depth map / point cloud 같은 명시적 3D 센서 입력을 넣는 방식(Explicit 3D VLA)은 센서 노이즈·하드웨어 이질성·기존 데이터셋의 불완전한 depth 커버리지에 발목 잡히고, 2D 이미지에서 3D 를 추정하는 방식은 depth estimator 성능에 종속됩니다.
- **본 논문의 가설** — 3D 정보는 VLA 의 visual 임베딩 안에 implicit 하게 내재될 수 있으며, 그렇게 되면 action 토큰이 auto-regressive 과정에서 3D 단서를 자연히 흡수할 수 있다고 가정합니다.
- **관찰적 근거** — depth probing 실험에서 2D 만으로 학습된 visual 임베딩은 의미 있는 공간 구조를 만들지 못함을 보여, 현 VLA 의 공간 표현 능력 부족을 정량적으로 드러냅니다.
- **왜 지금 중요한가** — 실로봇 데이터가 희소한 상황에서, 추론 비용 0 으로 공간 정밀도와 데이터 효율을 동시에 끌어올리는 범용·확장 가능한 학습 패러다임에 대한 수요가 큽니다.

---

## 🧩 핵심 기여

- **Spatial Forcing (SF)** — VLA 의 중간 visual 토큰을 사전학습 3D foundation model(VGGT) 의 latent 표현에 정렬시키는 단순·효과적 alignment 전략 제안. 명시적 3D 입력도, depth estimator 도 불필요.
- **Implicit 3D VLA 라는 제3 패러다임** — Explicit 3D(센서 입력) / depth-estimation 방식과 구분되는, 표현 정렬만으로 공간 인지를 주입하는 새로운 계열 정의(Fig. 2).
- **중간층 정렬의 깊이 의존성 규명** — "깊지만 가장 깊지는 않은" 층(32층 중 24층) 정렬이 최적임을 ablation 으로 확인.
- **SOTA 성능 + 효율** — LIBERO 에서 추가 3D 센서 없이 평균 98.5% 로 explicit 3D 방법(GeoVLA·3D-CAVLA) 과 동등·상회, 학습 수렴 최대 3.8× 가속, 데이터 효율 최대 5.9× 개선.
- **추론 비용 0** — 학습된 모델은 추론 시 일반 VLA 와 동일하게 동작(추가 구조·연산 없음) — 기존 VLA 에 플러그인 가능한 높은 적용성.

---

## 🔑 기술 키워드

- **Spatial Forcing (SF)** — VLA 의 중간 visual 임베딩을 3D foundation model 표현에 맞추도록 "강제(forcing)"하는 보조 정렬 손실. 시험문제 정답지를 직접 보여주는 대신, 잘 푸는 모범생의 풀이 과정(표현)을 따라 하게 만드는 방식.
- **VGGT (Visual Geometry Grounded Transformer)** — 여러 2D 이미지로부터 카메라 파라미터·point map·depth·3D track 등 3D 속성을 한 번에 출력하는 feed-forward 3D foundation model. 본 논문은 그 prediction head 가 아니라 transformer backbone 의 latent 를 supervision 신호로 사용.
- **Representation Alignment** — 두 모델의 임베딩이 같은 기하학적 관계 구조를 갖도록 cosine similarity 로 맞추는 것. 단순 복제가 아니라 "표현의 manifold" 를 모사.
- **Depth Probing** — VLA 파라미터를 동결한 채 DPT head 만 학습해 visual 임베딩 → depth map 변환을 시도, 임베딩에 담긴 공간 정보량을 측정하는 linear-probing 류 진단 실험.
- **Implicit 3D VLA** — 명시적 3D 입력 없이 표현 정렬만으로 공간 인지를 획득하는 VLA 패러다임 (Explicit 3D / depth-estimation 과 구분되는 본 논문의 분류).
- **Alternating-Attention** — VGGT 가 frame-wise self-attention 과 global self-attention 을 번갈아 적용해 프레임 내부와 전역을 동시에 보게 하는 메커니즘.
- **Positional Embedding (PE)** — 정렬 대상(target) 표현에 더해, auto-regressive VLA 안에서 토큰 간 상대 위치 순서를 보존하기 위한 추가 임베딩. long-horizon 성능에 특히 기여.
- **Auto-regressive token generation** — VLA 가 선행 visual·language 토큰을 조건으로 action 토큰을 순차 생성하는 구조. 따라서 visual 토큰의 표현 품질이 action 품질을 좌우.

---

## 🔬 방법론

### 직관

SF 의 출발점은 단순한 진단입니다. 오늘날 VLA 의 머리(VLM) 는 인터넷의 2D 이미지로만 똑똑해졌기 때문에, 사진 속 사물이 "얼마나 멀리, 어떤 3차원 형상으로" 놓여 있는지를 잘 모릅니다. 그런데 로봇은 바로 그 3D 공간 감각으로 움직여야 합니다. 기존 해법은 로봇에게 depth 카메라나 point cloud 같은 "3D 안경"을 직접 씌워 주는 것이었지만, 안경은 비싸고(센서 노이즈·기종마다 다름) 도수가 맞지 않을 때(데이터에 depth 가 없거나 추정기가 부정확) 오히려 시야를 흐립니다.

SF 의 아이디어는 안경을 씌우는 대신 "공간을 잘 보는 모범생(VGGT)" 의 머릿속 표현을 보고 따라 배우게 하는 것입니다. 학습 중에만, VLA 의 중간층 시각 표현이 VGGT 가 같은 이미지를 보고 만든 기하학적 표현과 닮도록 cosine similarity 로 끌어당깁니다. 핵심은 VGGT 의 정답(depth 숫자)을 베끼는 게 아니라 표현의 "구조(관계 기하)"를 닮게 한다는 점이며, t-SNE 분석은 정렬 후 VLA 표현이 target 과 거의 같은 분포 형태를 가지면서도 cluster 중심은 분리되어 있어 — 즉 공간 구조는 흡수하되 자기 시각 모달리티의 정체성은 잃지 않음 — 을 보여줍니다.

또 하나의 직관은 "어느 층을 가르칠 것인가" 입니다. 너무 얕은 층을 묶으면 이후 층에서 공간 정보가 다시 흩어지고, 너무 깊은 층은 이미 vision-특화 특징을 잃고 modality-무관 공간으로 수렴해 시각 supervision 을 받아들이기 어렵습니다. 그래서 "깊지만 가장 깊지는 않은" 중간(32층 중 24층) 을 정렬하는 것이 최적입니다. 마지막으로, 이 모든 것은 학습 시에만 작동하므로 추론 때는 일반 VLA 와 똑같아 추가 비용이 0 입니다.

### 아키텍처

![Figure 1 — Spatial Forcing overview](https://arxiv.org/html/2510.12276/x1.png)

> "Figure 1: Our proposed method, Spatial Forcing (SF), implicitly forces VLA models to acquire spatial-aware knowledge. (a) SF aligns intermediate visual embeddings of VLAs with geometric representations from pretrained 3D foundation models. (b) Our simple yet effective strategy yields significant improvements in training efficiency and test accuracy. (c) Depth probing proves that our SF brings spatial information into the aligned representations, further enhancing 3D perception." (§1)
(SF 의 세 축 — (a) 중간층 정렬 메커니즘, (b) 학습 효율·정확도 동시 향상, (c) depth probing 으로 입증된 공간 정보 주입 — 을 한 장으로 요약합니다.)

![Figure 2 — 3D VLA paradigm comparison](https://arxiv.org/html/2510.12276/x2.png)

> "Figure 2: Comparison among different paradigms for 3D VLAs." (§2.2)
(depth 센서 입력(a), 2D→3D 추정(b) 대비, SF 는 표현 정렬만으로 공간을 주입하는 제3 패러다임임을 시각화합니다.)

- **기반 VLA 구조** — VLM 은 causal attention 층을 쌓아 다음 토큰을 auto-regressive 하게 생성합니다. 입력은 세 모달리티로 처리됩니다. 멀티뷰 이미지는 DINOv2/SigLIP 같은 사전학습 visual encoder 로 $`N`$ 개 visual 토큰 $`\{\mathbf{x}_{t}^{\mathcal{V}}\}_{t=1}^{N}`$, 명령 텍스트는 $`M`$ 개 linguistic 토큰 $`\{\mathbf{x}_{t}^{\mathcal{L}}\}_{t=1}^{M}`$, 그리고 이들을 조건으로 $`K`$ 개 action 토큰 $`\{\mathbf{x}_{t}^{\mathcal{A}}\}_{t=1}^{K}`$ 이 생성됩니다.
- **action expert $`\mathcal{G}`$** — action 토큰을 실제 동작으로 매핑하는 trainable head (two-layer MLP 또는 flow-matching head).
- **target 모델 (VGGT)** — 멀티뷰 이미지 $`\mathcal{I}`$ 를 받아 pixel-level 공간 표현 $`f^{\mathrm{3D}}(I)`$ 을 출력. prediction head 가 아닌 transformer **backbone latent** 이 supervision 신호로 쓰이며, 정렬 대상에는 positional embedding $`E`$ 가 더해져 auto-regressive 순서가 보존됩니다.
- **정렬 모듈 (학습 전용)** — VLA 의 per-pixel visual 토큰 $`\mathbf{x}^{\mathcal{V}}_{i}`$ 를 batch normalization $`\Gamma`$ → two-layer MLP 로 투영해 차원을 맞춘 뒤, target 표현과 cosine similarity 로 정렬. 추론 시에는 이 모듈 전체가 제거됩니다.

> "we hypothesize that the 3D information is implicitly embedded within the visual embeddings of VLAs. Such embeddings would allow action tokens to acquire 3D cues through the auto-regressive mechanism during inference." (§2.2)
(이 가설이 SF 의 설계 의도를 못 박습니다 — visual 토큰에 3D 가 implicit 하게 담기면, 별도 3D 분기 없이 action 토큰이 auto-regressive 흐름에서 공간 단서를 흡수합니다.)

> "the latent representation extracted from the VGGT transformer backbone inherently encodes rich spatial information and is sufficient to serve as the 3D supervision signal." (§2.1)
(왜 VGGT 의 prediction head 출력(depth 등) 이 아니라 backbone latent 를 쓰는지의 근거입니다 — latent 자체가 이미 충분한 공간 정보를 담고 있다고 봅니다.)

### 학습 목표 / 손실

기반 VLA 의 token 생성과 action 생성은 다음과 같이 정의됩니다.

$$\mathbf{x}_{t}\sim p_{\theta}(\mathbf{x}_{t}\mid\mathbf{x}_{<t})$$

$$\mathbf{x}_{t}^{\mathcal{A}}\sim p_{\theta}\big(\mathbf{x}_{t}^{\mathcal{A}}\mid\{\mathbf{x}_{i}^{\mathcal{V}}\}_{i=1}^{N},\{\mathbf{x}_{j}^{\mathcal{L}}\}_{j=1}^{M},\mathbf{x}_{<t}^{\mathcal{A}}\big)$$

표준 action 손실은 action expert $`\mathcal{G}`$ 출력과 정답 동작 $`A_{gt}`$ 간 손실입니다.

$$\mathcal{L}_{\mathrm{action}}=\mathcal{L}[\mathcal{G}(\{\mathbf{x}_{t}^{\mathcal{A}}\}_{t=1}^{K}),A_{gt}]$$

> "Eq. (1) illustrates that the visual tokens as intermediate scene representations play a crucial role in generating action tokens and could be supervised properly." (§2.1)
(여기서 핵심 통찰이 나옵니다 — visual 토큰이 action 생성의 병목이므로, 이를 직접 supervise 할 여지가 있다는 것이 SF 의 진입점입니다.)

SF 의 핵심인 alignment 손실은 VLA visual 토큰(투영본) 과 3D target 표현 사이 cosine similarity 를 최대화(음수로 최소화)합니다.

$$\mathcal{L}_{\mathrm{align}}=-\frac{1}{N}\sum_{i=1}^{N}\mathcal{S}[\mathrm{MLP}\cdot\Gamma(\mathbf{x}^{\mathcal{V}}_{i}),f^{\mathrm{3D}}_{i}(I)+E]$$

여기서 $`\mathcal{S}[\cdot,\cdot]`$ 는 cosine similarity, $`f^{\mathrm{3D}}_{i}(I)`$ 는 visual 토큰 $`\mathbf{x}^{\mathcal{V}}_{i}`$ 의 픽셀 위치에 대응하는 공간 표현입니다.

최종 목표는 두 손실을 가중치 $`\alpha`$ 로 결합합니다.

$$\mathcal{L}_{\mathrm{SF}}=\mathcal{L}_{\mathrm{action}}+\alpha\mathcal{L}_{\mathrm{align}}$$

> "We found that supervising relatively deep but not the deepest layers is most effective in enhancing action performance. The reason is probably that the deeper layers lose more vision-specific features, making them less amenable to the supervision of target spatial representations" (§2.3)
(정렬 층 선택의 설계 원칙입니다 — 가장 깊은 층은 vision-특화 특징을 잃어 시각 target 정렬을 받아들이지 못하므로, 중간-깊은 층(32층 중 24층) 이 최적입니다.)

> "During inference, the VLA model trained in the SF manner operates identically to a standard VLA without SF, introducing no additional structures or computational overhead, thereby highlighting SF's high applicability." (§2.3)
(SF 의 실용성 핵심 — 정렬 모듈은 학습 전용이라 추론 비용이 0 이고, 어떤 VLA 에도 끼워 넣을 수 있습니다.)

### 학습 셋업

- **base 모델** — LIBERO 에서는 OpenVLA-OFT(Prismatic VLM, SigLIP+DINOv2 fused vision backbone, OXE 사전학습), RoboTwin 에서는 $`\pi_{0}`$(PaliGemma backbone) 를 base 로 사용.
- **하드웨어·스케줄** — OpenVLA-OFT + SF 는 8×NVIDIA H100 에서 150k iteration. $`\pi_{0}`$ + SF 는 LoRA 로 1×H100 에서 30k iteration. ablation 은 자원 제약상 single H100.
- **target 표현** — VGGT backbone latent + positional embedding. SigLIP / DINOv2 를 target 으로 한 비교군도 존재(§3.3).
- **정렬 층** — VLM backbone 32 causal attention 층 중 24층.
- **가중치** — $`\alpha=0.5`$ (Appendix A, Tab. 3 기준 최적).

---

## 📊 실험 설정과 결과

평가 벤치마크는 시뮬레이션의 LIBERO(4 suite: Spatial / Object / Goal / Long, 각 10 task × 500 demo) 와 RoboTwin(real-to-sim 양손, easy/hard), 그리고 실로봇(AgileX 양손) 입니다. 지표는 success rate(SR) 입니다.

### LIBERO SOTA 비교 (Table 1)

| Method | Spatial | Object | Goal | Long | Average |
|---|---|---|---|---|---|
| Diffusion Policy (2D) | 78.3 | 92.5 | 68.3 | 50.5 | 72.4 |
| Octo (2D) | 78.9 | 85.7 | 84.6 | 51.1 | 75.1 |
| OpenVLA (2D) | 84.7 | 88.4 | 79.2 | 53.7 | 76.5 |
| $`\pi_{0}`$ (2D) | 96.8 | 98.8 | 95.8 | 85.2 | 94.2 |
| UniVLA (2D) | 96.5 | 96.8 | 95.6 | 92.0 | 95.2 |
| OpenVLA-OFT (2D) | 97.6 | 98.4 | 97.9 | 94.5 | 97.1 |
| SpatialVLA (Explicit 3D) | 88.2 | 89.9 | 78.6 | 55.5 | 78.1 |
| GeoVLA (Explicit 3D) | 98.4 | 99.0 | 96.6 | 96.6 | 97.7 |
| 3D-CAVLA (Explicit 3D) | 98.2 | 99.8 | 98.2 | 96.1 | 98.1 |
| **Spatial Forcing (Ours, Implicit 3D)** | **99.4** | **99.6** | **98.8** | **96.0** | **98.5** |

> "without requiring additional 3D inputs, our SF achieves comparable performance with those methods that benefit from extra 3D sensor inputs (e.g., GeoVLA and 3D-CAVLA)." (§3.2, Table 1)
(SF(평균 98.5) 가 추가 3D 센서를 쓰는 explicit 3D 방법(GeoVLA 97.7, 3D-CAVLA 98.1) 을 입력 없이 동등·상회한다는 점이 핵심 주장입니다.)

### Component Analysis (Table 2, single H100)

ablation 은 single H100 기준이라 base 평균이 92.7 로 위 표(8×H100, 97.1) 와 다릅니다. 각 ablation 의 분리 변수만 읽습니다.

| 구분 | 설정 | Spatial | Object | Goal | Long | Average |
|---|---|---|---|---|---|---|
| base (no SF) | — | 96.8 | 94.8 | 92.8 | 86.2 | 92.7 |
| target 표현 | SigLIP | 95.2 | 94.8 | 94.0 | 91.8 | 94.0 |
| target 표현 | DINOv2 | 93.4 | 95.2 | 93.8 | 93.8 | 94.1 |
| target 표현 | VGGT w/o PE | 97.8 | 100.0 | 96.6 | 84.4 | 94.7 |
| target 표현 | VGGT (+PE) | 97.2 | 99.2 | 96.8 | 94.2 | 96.9 |
| 정렬 층 | layer 1 | 96.8 | 99.4 | 99.0 | 83.0 | 94.6 |
| 정렬 층 | layer 8 | 96.2 | 98.4 | 95.6 | 92.4 | 95.7 |
| 정렬 층 | layer 16 | 97.4 | 98.8 | 95.8 | 83.2 | 93.8 |
| 정렬 층 | layer 24 | 97.2 | 99.2 | 96.8 | 94.2 | 96.9 |
| 정렬 층 | layer 32 | 98.8 | 99.4 | 96.2 | 84.8 | 94.8 |
| 데이터량 | 1% | 32.8 | 67.8 | 44.8 | 23.6 | 42.3 |
| 데이터량 | 5% | 73.2 | 83.4 | 80.6 | 66.0 | 75.8 |
| 데이터량 | 100% | 97.2 | 99.2 | 96.8 | 94.2 | 96.9 |

- **target 표현 ablation** — SigLIP·DINOv2 target 도 base 대비 향상(94.0/94.1) 하나, 3D 로 학습된 VGGT target 이 96.9 로 최고. "표현 정렬" 자체가 범용 패러다임이되, 3D 이해 보강이 결정적임을 분리합니다.
- **PE 효과** — VGGT w/o PE 는 long-horizon 에서 급락(84.4) 하지만 PE 추가 시 94.2 로 회복. auto-regressive 내 토큰 상대 위치 보존이 long-horizon 에 load-bearing 임을 보입니다.
- **정렬 층 ablation** — layer 24 가 평균 96.9 로 최적. 너무 얕은(1·8·16) 층이나 가장 깊은(32) 층은 특히 long-horizon(83~84) 에서 무너집니다. "깊지만 가장 깊지 않은" 층 주장을 수치로 뒷받침.
- **데이터 효율** — 5% 데이터만으로 75.8 달성. 1% 에서는 42.3 으로 급락해, 극저데이터 영역의 하한도 함께 드러냅니다.

> "achieving the same success rates 3.8 $`\times`$ more quickly than the base model." (§3.3)
(학습 수렴 가속 — 같은 SR 도달까지 base 대비 3.8배 빠릅니다(Fig. 5a).)

> "It also achieves 25.8% higher success rates in terms of the same data amounts and reaches 5.9 $`\times`$ more efficient in terms of the same success rates." (§3.3)
(데이터 효율 — 동일 데이터량에서 +25.8%p, 동일 SR 도달에 5.9배 적은 데이터(Fig. 5b).)

### 가중치 $`\alpha`$ ablation (Table 3, Appendix A)

| $`\alpha`$ | 0 | 0.02 | 0.1 | 0.5 | 2.5 | 12.5 |
|---|---|---|---|---|---|---|
| SR (%) | 73.2 | 92.2 | 92.8 | 93.6 | 86.6 | 81.2 |

> "the model performs best under the $`\alpha=0.5`$, which is the default setting in all other experiments." (§A)
($`\alpha`$ 가 작으면(0) 효과 없음, 너무 크면(12.5) visual 모달리티가 불안정해져 action 예측을 해칩니다 — 0.5 가 최적의 균형점입니다.)

### 표현 정렬의 성질 (t-SNE, Fig. 5c)

![Figure 5 — efficiency & t-SNE](https://arxiv.org/html/2510.12276/x5.png)

> "Figure 5: (a) We report the success rates vs. training iterations before and after representation alignment. (b) We report the success rate vs. training data before and after representation alignment. (c) The aligned representation exhibits almost the same distribution shape as the target." (§3.3)
(학습/데이터 효율 곡선과 함께, 정렬된 VLA 표현이 target 과 거의 같은 분포 형태를 가지면서도 중심은 분리됨(표현 붕괴 없음) 을 시각화합니다.)

### 실로봇 (AgileX 양손)

![Figure 6 — real-world experiments](https://arxiv.org/html/2510.12276/x6.png)

> "Figure 6: Real-world Experiments. (a) A set of single-arm tasks across various visual and spatial conditions. For each task, we train a unified model to face all variations and report the success rate. (b) Dual-arm tasks to measure the spatial horizontal balance ability. (c) Top-view robot setup." (§4)
(실로봇은 6-DoF Piper × 2 + 1-DoF gripper, primary + wrist 2 카메라. single-arm 40 demo / bimanual 20 demo 의 극저데이터 학습입니다.)

> "Our SF reaches 47.5% higher success rates than the base model because SF captures the underlying spatial relationships rather than overfitting the spurious correlations." (§4.2)
(stack glass cups(투명컵·조명 변화) 에서 +47.5%p — 배경·조명 같은 shortcut 이 아닌 공간 관계를 학습했음을 시사하며, place green block(높이 변화) 에서는 85% 를 달성합니다.)

---

## ⚖️ 한계

- **공간 정밀도의 종류가 "장면(scene)-level" 에 치우침** — target 인 VGGT 는 멀티뷰 RGB 로부터 카메라·depth·point map 등 장면 기하를 산출합니다. 따라서 SF 가 주입하는 공간 인지는 물체 위치·상대 배치·height 같은 macro 공간 추론에 강하지, 손가락-물체 접촉 같은 micro·접촉 기하에는 직접적 신호가 없습니다. 향상이 "object localization / spatial relationship" 사례에 집중되는 것도 이 메커니즘의 자연스러운 귀결입니다.
- **target 모델 의존성** — 성능 상한이 VGGT 표현 품질에 종속됩니다. VGGT 가 약한 도메인(반사·투명·비정형 표면, 단안·근접 클로즈업) 에서는 정렬 신호 자체가 오염될 수 있고, 본 논문은 VGGT 실패 영역에서의 SF 행동을 다루지 않습니다.
- **정렬 층의 backbone 종속성** — 최적 층(24/32) 은 Prismatic 32층 backbone 에 맞춘 값입니다. 층 수·구조가 다른 VLM 에서는 재탐색이 필요하며, 본 논문은 OpenVLA-OFT 외 backbone 에 대한 층 sweep 을 제시하지 않아 일반화 비용이 가려져 있습니다.
- **멀티뷰·VGGT 학습 비용** — 추론은 0 비용이지만 학습 시 매 배치마다 VGGT forward(멀티뷰 입력 필요) 가 추가됩니다. 단일 카메라만 있는 셋업이나 VGGT 의 멀티뷰 가정이 깨지는 데이터에서의 적용성은 논의되지 않았습니다.
- **저데이터 하한** — 1% 데이터에서 42.3 으로 급락해, SF 가 데이터 효율을 끌어올리지만 극저데이터에서는 여전히 무너집니다. "데이터 효율 개선" 주장이 통하는 구간(≥5%) 의 경계가 분명히 존재합니다.

---

## ♻️ 재현성

- **코드 / 프로젝트** — 프로젝트 페이지 [spatial-forcing.github.io](https://spatial-forcing.github.io/) 공개. (본문에서 별도 코드 저장소 URL 은 확인되지 않아 여기 명시하지 않습니다.)
- **base 모델** — OpenVLA-OFT, $`\pi_{0}`$ 모두 공개 모델. target VGGT 도 공개 3D foundation model.
- **벤치마크** — LIBERO, RoboTwin 모두 공개. 모든 학습·평가는 official setting 을 따른다고 명시.
- **하드웨어** — 학습: 8×H100(OpenVLA-OFT 150k), 1×H100(π0 LoRA 30k), ablation single H100. 실로봇: AgileX 양손(6-DoF Piper ×2 + 1-DoF gripper, 3 카메라).
- **하이퍼파라미터** — $`\alpha=0.5`$, 정렬 층 24/32, target = VGGT backbone latent + PE 등 핵심 값이 본문·appendix 에 공개.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P4(VLM 사전학습 보존)** — 본 논문의 전제 "2D 만으로 사전학습된 VLM 은 공간 인지가 결여" 가 P4 의 문제의식과 직결됩니다. SF 는 backbone 의 중간 표현을 보조 손실로 형성(shaping) 하는 학습-측 전략으로, D20(prior-preservation strategy) 의 후보 도구입니다. 특히 t-SNE 결과의 "표현 붕괴 없이(원 modality 정체성 유지) 공간 구조만 흡수" 는 D20 이 요구하는 "능력 추가 ↔ 사전학습 표현 손상 방지" 의 균형 자체를 다룹니다. 다만 SF 는 사전 prior 를 *보존* 하기보다 결여된 능력을 *주입* 하는 방향이라, 보존 전략으로 해석할 때 polarity 에 주의가 필요합니다.
- **P4 / D19(VLM fine-tuning range)** — SF 는 중간층 VLM 표현을 supervise 하므로 해당 층이 trainable 해야 합니다. 우리 v1 의 D19(a)(full VLM freeze + action expert only) 와는 직접 충돌하며, 적용하려면 부분 학습이 전제됩니다.
- **P4 / D23(action representation × VLM preservation)** — action expert 는 MLP 또는 flow-matching head 둘 다 호환되어, 우리의 D23(iii)(continuous flow-matching head) 과 양립합니다. 즉 head 형태와 무관하게 끼울 수 있는 직교적 보조 손실입니다.
- **P2(구조적 입력-모달리티 결합)** — SF 는 visual 토큰을 공간 표현으로 "관측 격상" 시키는 표현-측 접근입니다. P2 의 multi-camera pre-fusion(D12) 과 같은 멀티뷰 입력을 전제(VGGT 가 멀티뷰 필요) 하며, "관측을 명시적으로 공간화" 한다는 점에서 P2 의 observation-elevation 철학과 결이 같습니다. 단 P2 의 핵심인 finger/palm tactile binding 은 다루지 않습니다.
- **Identity 지지/긴장** — 우리 Identity 는 dexterity 를 VLA-level 에서 직접 tackle 하자는 것이고, SF 는 "correction 모듈을 붙이지 않고 VLA 내부 표현을 직접 개선" 한다는 점에서 철학적으로 지지적입니다. 긴장은 SF 의 공간 신호가 손-접촉(hand-level) 이 아닌 팔-장면(body-level) 정밀도에 치우친다는 점입니다.

---

## ✨ 핀 논문 대비 델타

- **vs. ConSFT([arXiv:2605.08879](https://arxiv.org/abs/2605.08879), P4 핀)** — ConSFT 는 conservative importance weighting 으로 기존 prior 를 *지키는* trust-region SFT 입니다. SF 는 정반대로 외부 3D foundation model 표현을 끌어와 *결여된 공간 능력을 더하는* alignment 입니다. 둘 다 학습-측 정규화지만 방향(보존 vs 주입) 이 대칭적이라 결합 가능성이 흥미롭습니다.
- **vs. UAM([arXiv:2605.15735](https://arxiv.org/abs/2605.15735), P4 핀)** — UAM 은 Ventral/Dorsal dual-stream 이라는 *구조* 로 VLM 을 보존합니다. SF 는 구조를 전혀 바꾸지 않고 학습 손실 하나로 해결하며 추론 비용이 0 이라는 점이 결정적 차별점입니다.
- **vs. VLM2VLA([arXiv:2509.22195](https://arxiv.org/abs/2509.22195))** — VLM2VLA 는 LoRA + NL-action 으로 언어 prior 망각을 줄입니다. SF 는 언어가 아닌 *공간/3D* 표현 결여를 cross-model 표현 distillation 으로 메운다는 점에서 다른 축의 문제를 다룹니다.
- **진정으로 새로운 점** — 기존 P4 핀 중 어느 것도 "사전학습된 3D foundation model 의 latent 를 중간층 정렬 target 으로 삼는 cross-model representation distillation" 을 공간 인지 주입에 쓰지 않았습니다. "깊지만 가장 깊지 않은 층" 의 정렬 효과 규명도 새로운 경험칙입니다.

---

## ⚙️ 의사결정 함의

- **새 loss term 추가 후보** — 학습 파이프라인에 `L_align` (cosine, target = VGGT backbone latent + PE) 을 가중치 `alpha=0.5` 로 더하는 옵션. config 키 수준: `align_loss_weight=0.5`, `align_target=VGGT`, `align_layer_idx≈0.75×depth` (32층 기준 24), `align_proj = BN + 2-layer MLP`, `cosine_similarity`.
- **D21(staged training recipe) 보강** — SF 는 Stage 2(Body/Hand expert 학습) 의 보조 손실로 끼워 데이터 효율(최대 5.9×)·수렴(3.8×) 을 끌어올리는 저비용 레버가 될 수 있습니다. 실로봇 데이터가 희소한 in-hand 데모(Phase 1) 의 데이터 예산을 줄이는 직접적 함의.
- **D19 와의 충돌 해소 필요** — 적용하려면 정렬 대상 중간층이 학습되어야 하므로, D19(a) full freeze 와 양립 불가. "backbone 부분 학습 + SF" 라는 변형이 필요하며, 이는 D19 재검토 트리거가 될 수 있습니다.
- **메트릭** — 도입 효과는 동일 SR 도달까지의 iteration/데이터량(효율) 과 long-horizon SR 로 측정. depth probing 을 진단 지표로 채택 가능(임베딩 공간정보량 정량화).

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 체크) 손-접촉 정밀도로 전이되는가** — SF 검증은 OpenVLA-OFT(LIBERO 그리퍼)·π0(RoboTwin 양손) 으로, 모두 그리퍼/팔이며 다지 손이 아닙니다. VGGT 의 장면 기하 신호는 물체 위치·배치(=Body expert 영역) 를 돕지, 손가락-물체 접촉(=Hand expert·차별화 주장) 을 직접 돕지 않을 공산이 큽니다. 가장 싼 확인: in-hand reorientation 처럼 *손에 가려 물체가 occlusion 되는* 태스크에서도 SF 이득이 남는지 소규모 검증.
- **freeze 정책 충돌** — 우리 v1 은 D19(a) full VLM freeze 입니다. SF 는 중간 VLM 층 학습을 요구하므로 그대로는 적용 불가. 먼저 "backbone freeze 하에 action-expert 측 표현만 정렬" 변형이 의미 있는 신호를 주는지 확인 필요(원 논문에는 없는 셋업).
- **멀티뷰·VGGT 가정** — VGGT 는 멀티뷰 입력을 전제합니다. 우리 셋업(다카메라이긴 하나 손 클로즈업·tactile 중심) 에서 VGGT latent 가 신뢰할 만한지, 특히 손이 시야를 가리는 프레임에서 target 이 오염되지 않는지 점검.
- **정렬 층 재탐색 비용** — 최적 층(24/32) 은 backbone 종속. π(PaliGemma) 계열에서는 층 sweep 이 필요하며, 잘못된 층은 long-horizon 을 오히려 해칩니다(layer 16·32 의 long 급락 사례).
- **target 도메인 갭** — 우리 대상(반사·투명·소형 부품 조작) 에서 VGGT 자체가 약하면 정렬이 noise injection 이 됩니다. VGGT 의 우리 도메인 depth/point 품질을 먼저 정성 확인하는 것이 정렬 도입 전 sanity check.

---

## 💡 컨텍스트 제안

- **P4 §5 추적 문헌 후보** — SF 를 D20(prior-preservation/표현-shaping strategy) 의 추적 문헌 후보로 등재 검토. 단 "보존" 이 아닌 "공간 능력 주입" 이므로, ConSFT(보존) 와 짝지어 *상보적* 도구로 기술하는 것이 정확합니다.
- **D21 deferred 후보** — "VGGT representation-alignment 보조 손실" 을 staged recipe 의 데이터-효율 레버로 deferred 등록(Phase 1 데이터 예산 절감 목적). 트리거: in-hand 데모에서 데이터 부족이 병목이 될 때.
- **D19 재검토 노트** — SF 적용은 중간층 학습을 전제하므로, full-freeze(D19a) 고수 시 SF 는 배제됨을 의사결정 로그에 남겨둘 것을 제안.
- (context/ 파일은 수정하지 않았습니다 — 위는 제안일 뿐입니다.)

---
