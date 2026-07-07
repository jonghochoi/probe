# Paper Analysis — Vision Pretraining for Dense Spatial Perception

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Vision Pretraining for Dense Spatial Perception |
| 저자 | Zelin Fu, Bin Tan, Changjiang Sun, Shaohui Liu, Kecheng Zheng, Yinghao Xu, Xing Zhu, Yujun Shen, Nan Xue |
| 링크 | [arXiv:2607.05247](https://arxiv.org/abs/2607.05247) · [GitHub](https://github.com/robbyant/lingbot-vision) · [HuggingFace](https://huggingface.co/collections/robbyant/lingbot-vision) · [Website](https://technology.robbyant.com/lingbot-vision) |
| 발행일 / 버전 | 2026-07-06 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-07-07 |
| 관련 Pillar | P2, P5 |
| 태그 | dataset |

---

## 🧭 한 줄 요약 (TL;DR)

self-distillation(DINO/iBOT) 기반 시각 사전학습에서 "무엇을 마스킹할지"를 무작위가 아니라 **경계(boundary)** 가 결정하게 만들고, 교사가 스스로 온라인으로 생성·검증한 **범주형 경계 필드(categorical boundary field)** 를 마스킹된 경계 토큰의 추가 지도 신호로 라우팅하는 masked boundary modeling 을 제안합니다. 이를 1B ViT-g 로 스케일한 LingBot-Vision 은 dense 공간 예측(NYUv2 depth linear-probe RMSE 0.296)에서 7배 큰 7B DINOv3(0.309)를 앞서고, 그 인코더를 갈아끼운 것만으로 LingBot-Depth 1.0 → 2.0 을 이끌어 14개 depth completion 벤치마크에서 선두 성능을 냅니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 물리 지능(physical intelligence)에는 픽셀에서 구조화·계량적·행동가능(actionable)한 dense 공간 표현을 복원하는 능력이 필요하지만, 현대 시각 파운데이션 모델은 semantic invariance 를 우선해 세밀한 공간 이해가 상대적으로 약합니다.
- **기존 접근의 한계** — shape 와 boundary 는 통상 "지각의 출력"으로 취급되어 전용 head 와 값비싼·모호한 annotation 에 묶이므로, 대규모 사전학습의 **native 학습 신호**로는 거의 쓰이지 못했습니다. self-distillation·cross-modal alignment·masked reconstruction 모두 dense 공간 품질을 간접적으로만 얻습니다.
- **본 논문의 가설** — boundary 와 shape discontinuity 는 예측해야 할 출력이 아니라 dense 표현 학습을 조직하는 **근본 신호**이며, 라벨·외부 edge detector·사전학습 backbone 없이 raw 이미지로부터 부트스트랩할 수 있다는 것입니다.
- **왜 지금 중요한가** — frozen 인코더가 world model 과 로봇 정책의 지각 기질(perception substrate)이 되어가는 흐름에서, geometry 의 오류는 "벤치마크 점수 하락"이 아니라 "잘못된 행동"으로 직결됩니다(저자 §2.1).

---

## 🧩 핵심 기여

- **Boundary-centric 사전학습 관점** — boundary 를 downstream 출력이 아니라 self-supervised 사전학습의 native 학습 신호로 격상하고, 인간 라벨·외부 edge detector·사전학습 backbone 없이 raw 이미지에서 부트스트랩할 수 있음을 보입니다.
- **Masked boundary modeling** — 교사가 발견한 boundary 토큰을 학생의 마스킹 집합에 강제로 넣고(boundary forcing), 마스킹된 토큰을 geometry 로 라우팅해 semantic 추상화와 geometric 민감성의 충돌을 **협력**으로 바꿉니다.
- **경계 필드의 범주형 재파라미터화(categorical reparameterization)** — 연속 boundary 필드를 per-pixel 분류로 바꿔 dense self-distillation 을 안정화하고, a-contrario 검증을 추가 비용 없이 얻습니다.
- **스케일·증류·downstream 이전** — 1B ViT-g LingBot-Vision 으로 스케일해 최대 7배 큰 모델을 dense 공간 지각에서 능가하고, ViT-L/B/S 로 증류하며, 인코더 교체만으로 LingBot-Depth 2.0 을 만들어 14개 depth completion 벤치마크에서 선두를 냅니다.

---

## 🔑 기술 키워드

- **Masked Boundary Modeling** — "무엇을 마스킹하고 무엇을 복원할지"를 이미지의 경계가 결정하게 하는 self-supervised 패러다임. 본 논문의 핵심 방법입니다.
- **Self-Distillation (DINO / iBOT)** — EMA 교사의 분포를 학생이 view/마스킹 넘어 맞추도록 학습하는 SSL 계열. 본 논문의 baseline 골격이며, 여기에 geometric 채널을 덧댑니다.
- **Boundary Forcing** — 교사가 예측한 경계가 지나가는 토큰을 무작위 마스크 위에 강제로 추가하는 것. 가장 복원 불가능한(비중복) 정보를 골라 마스킹합니다.
- **Boundary Field (Attraction Field)** — 희소한 선분 집합을 픽셀별 속성 벡터(거리·방향·양 끝점 각도)로 lift 한 dense 지도. 소수 픽셀만으로 전체 선분을 복원할 만큼 중복적입니다.
- **Categorical Reparameterization** — 연속 필드 값을 이산 bin 위 분포로 바꿔 회귀를 per-pixel 분류로 재구성하는 것. EMA 루프에서 continuous regression 이 붕괴하는 문제를 회피합니다.
- **A-contrario Validation (NFA)** — "구조 없음" 귀무가설(방향이 균등분포) 대비 후보 선분의 support 가 우연으로 설명되기 어려울 때만 채택하는 파라미터-free 검증. 범주형 균등분포가 곧 귀무가설이 되어 무료로 딸려옵니다.
- **Geometry Routing** — 마스킹된 토큰 중 경계 토큰은 geometric(boundary) 목표로, 나머지는 semantic(iBOT) 목표로 나눠 지도하는 것. semantic 목표가 약한 지점에 well-posed 신호를 공급합니다.
- **Online Target Generation** — 교사가 매 스텝 boundary 필드를 예측→corner 점과 짝지어 후보 선분 decode→a-contrario 로 걸러 clean 타깃을 re-render 하는 파이프라인. annotation 없이 타깃이 모델과 공진화합니다.
- **Corner-Point Anchoring** — 무작위 필드값조차 corner 점만 고정되면 corner-앵커 선분으로 decode 된다는 성질(Finding 1). 학습 첫 스텝부터 쓸 만한 경계를 확보해 부트스트랩을 가능케 합니다.
- **Gram Anchoring** — 긴 스케줄에서 patch-level dense feature 가 열화하는 것을 막기 위해 학생 patch feature 의 Gram 행렬을 과거 교사 스냅샷에 앵커링하는 DINOv3 기법. 본 논문도 100k iter 채택합니다.

---

## 🔬 방법론

### 직관

이 논문의 출발점은 하나의 관찰입니다. iBOT·MAE·JEPA 등 모든 마스킹 사전학습은 "어떤 토큰을 가릴까"라는 질문에 한결같이 **무작위**로 답합니다. 그런데 무작위 마스킹은 내용에 무지해서, 주변으로 쉽게 복원되는 평평한 내부 토큰이든 이웃으로는 채울 수 없는 경계 토큰이든 똑같이 취급합니다. 경계 토큰은 이미지에서 가장 정보 밀도가 높고 가장 덜 중복적인 영역인데, 무작위 마스킹은 정작 그 토큰을 자주 놓칩니다. 저자들은 이미지의 구조, 즉 경계가 무엇을 가리고 그 자리에서 무엇을 복원할지를 정하게 만듭니다.

방법은 두 개의 톱니로 맞물립니다. 첫째, **boundary forcing**: 교사가 스스로 예측한 경계가 지나가는 토큰을 무작위 마스크 위에 강제로 추가해, 학생이 그 경계 geometry 를 주변 맥락만으로 복원하도록 강요합니다. 둘째, **geometry routing**: 마스킹된 토큰 중 경계 토큰은 semantic(iBOT) 목표에 더해 **명시적 geometric 목표**로도 지도하고, 나머지는 표준 semantic 목표만 받습니다. 두 지역이 만나는 경계에서 semantic 코드워드는 본질적으로 모호하므로, geometric 목표는 바로 그 자리, 기존 마스킹이 가장 약한 자리에 well-posed 신호를 공급합니다. 그래서 boundary-aware 표현과 semantic 표현이 경쟁하지 않고 **공진화**합니다.

여기엔 닭-달걀 문제가 있습니다. 경계를 가리려면 경계가 어디인지 이미 알아야 하는데, 무작위 초기화된 망은 그것을 모릅니다. 두 가지 장치가 이 매듭을 풉니다. (1) 저자들이 채택한 **경계 필드**는 소수 픽셀만으로 전체 선분을 복원할 만큼 중복적이라, corner 점만 고정하면 학습되지 않은 무작위 필드값조차 그럴듯한 선분으로 decode 됩니다(Finding 1). (2) 연속 필드를 그대로 회귀하면 EMA 루프에서 붕괴하므로, 필드를 이산 bin 위 **범주형 분포**로 바꿔 분류 문제로 재구성합니다. 그러면 semantic self-distillation 을 지탱하는 centering·sharpening 을 그대로 물려받고, 균등분포가 곧 a-contrario 귀무가설이 되어 검증까지 공짜로 딸려옵니다.

### 아키텍처

![Figure 2 — boundary-forcing masking (panel c)](https://arxiv.org/html/2607.05247/figures/overview/cube_mask_bnd.png)

> "Figure 2: Boundary-centric masked modeling on a toy scene. (a) An input image and its patch grid. (b) Random masking is content-agnostic: most hidden patches are flat and recoverable from context, while the boundary-bearing patches largely escape the mask. (c) Boundary-forcing masking adds every boundary-bearing patch to the random mask, so the structure of the scene is exactly what the student must reconstruct. (d) The boundary field that supervises boundary tokens, encoded as per-pixel categorical distributions over discretized distance and orientation bins. During pretraining the boundary field is predicted online by the teacher itself, without human labels or external detectors; every masked token follows the semantic self-distillation objective, and boundary tokens additionally match the categorical boundary target." (§3)
(무작위 마스킹(b)이 경계 토큰을 놓치는 반면, boundary-forcing(c)은 모든 경계 토큰을 마스크에 추가해 "장면의 구조 그 자체"를 복원 대상으로 만든다는 핵심 대비를 보여줍니다.)

**골격.** 학생 $`f_{\theta}`$ 와 동일 구조의 교사 $`f_{\bar{\theta}}`$ 를 두고, 교사 가중치는 학생의 EMA 입니다.

$$\bar{\theta}\leftarrow\lambda\,\bar{\theta}+(1-\lambda)\,\theta$$

> "with momentum $`\lambda`$ annealed toward $`1`$ during training." (§3.1)
(모멘텀 $`\lambda`$ 는 학습이 진행되며 1 로 annealing 됩니다. 이미지당 global crop 2개 + 저해상 local crop 여러 개를 샘플하고, ViT 가 각 view 를 class 토큰 $`\mathbf{z}^{\texttt{cls}}`$ 과 patch 토큰열 $`\{\mathbf{z}^{\texttt{p}}_{i}\}_{i=1}^{N}`$ 로 인코딩합니다.)

**경계 토큰 정의와 강제.** ViT 는 토큰 수준에서 동작하므로, 픽셀별 edge 대신 각 토큰에 boundary 속성을 붙입니다. 교사가 예측한 경계를 픽셀 지도로 rasterize 하고, 토큰 grid 로 max-pool 해 경계가 지나가는 토큰 집합을 얻습니다.

$$\mathcal{B}=\big\{\,i\in\{1,\dots,N\}:\text{a predicted boundary intersects }\mathrm{patch}(i)\,\big\}$$

> "We then force $`\mathcal{B}`$ into the student's masked set, on top of the random mask $`\mathcal{M}`$ of Sec. 3.1" (§3.2)
(무작위 마스크 $`\mathcal{M}`$ 위에 경계 집합 $`\mathcal{B}`$ 를 합쳐 $`\mathcal{M}^{+}=\mathcal{M}\cup\mathcal{B}`$ 를 만듭니다. 토큰 한 개의 패치는 $`P\times P`$, $`P{=}16`$ 이며, 경계 토큰은 semantic 과 geometric 두 타깃을 동시에 받습니다.)

**경계 head.** 경계 필드는 sub-token 해상도에 살지만 backbone 은 토큰당 feature 하나를 냅니다. 이 간극을 convolution 없이 잇는 경량 head 를 붙입니다.

> "Each patch token is processed independently by a small MLP, and its output is expanded and rearranged into an $`r\times r`$ tile of positions at stride $`s=P/r`$ (we use $`s{=}2`$), so a token literally unfolds into the dense positions it covers." (§3.4)
(토큰 하나가 자신이 덮는 dense 위치들로 "펼쳐집니다". 각 위치 feature 를 $`\ell_{2}`$-정규화한 뒤, 채널별로 $`K`$ 개 학습 bin 프로토타입과의 cosine 유사도로 점수화합니다 — bias 없는 unit-norm 선형층이라 모든 logit 이 경계지어진 cosine 이 되어 DINO projection head 처럼 붕괴를 막습니다. 교사·학생이 이 head 설계를 공유하고 교사는 EMA 사본입니다.)

**온라인 타깃 생성.** 매 iteration, 교사는 global view 를 4단계로 타깃 필드로 바꿉니다.

![Figure 5 — validated target field (panel d)](https://arxiv.org/html/2607.05247/figures/overview/cube_boundary.png)

> "Figure 5: Online generation of boundary targets (toy example). Even when the teacher's boundary field is noisy, as it is early in training (b), the holistic parameterization lets the many weak per-pixel votes in a segment's support region aggregate into coherent candidate segments anchored at corner points (c), together with spurious candidates such as face diagonals and background chords. The a-contrario test then discards unsupported candidates, and the survivors are re-rendered into the clean target field that supervises the student (d). Boundary targets thus emerge from raw images, with only a frozen single-block corner-point detector fixed (Sec. 3.4)." (§3.4)
((i) dense 경계 필드 예측 → (ii) frozen 단일 블록 ViT 로 corner 점 localize → (iii) vote 집계로 후보 선분 $`L`$ decode → (iv) a-contrario 로 걸러 survivor 를 clean 타깃 필드로 re-render. 이 re-render 된 필드만 학생을 지도하므로 근거 없는 구조는 교육 신호가 되지 않고, 필드가 매 스텝 EMA 교사에서 재생성되어 타깃이 모델과 공진화합니다.)

### 학습 목표 / 손실

**DINO (이미지 수준).** projection head $`h`$ 가 class 토큰을 $`C`$ 개 프로토타입 분포로 매핑하고, 교사 분포는 centering·sharpening 후 학생이 view 넘어 맞춥니다.

$$\mathbf{p}^{\texttt{t}}=\mathrm{softmax}\!\left(\frac{h_{\bar{\theta}}(\mathbf{z}^{\texttt{cls}})-\mathbf{c}}{\tau_{t}}\right),\qquad\mathbf{p}^{\texttt{s}}=\mathrm{softmax}\!\left(\frac{h_{\theta}(\mathbf{z}^{\texttt{cls}})}{\tau_{s}}\right)$$

$$\mathcal{L}_{\texttt{DINO}}=-\,\mathbf{p}^{\texttt{t}}\!\big(\mathbf{x}^{(1)}\big)^{\!\top}\log\mathbf{p}^{\texttt{s}}\!\big(\mathbf{x}^{(2)}\big)$$

(불일치 view 쌍에 대해 합하며 교사에는 stop-gradient. 온도는 $`\tau_{t}<\tau_{s}`$ 이고, 교사 분포의 centering(또는 Sinkhorn–Knopp)이 상수 분포로의 붕괴를 막습니다.)

**iBOT (patch 수준).** 마스킹 부분집합 $`\mathcal{M}`$ 의 학생 patch 예측을, 대응하는 교사의 unmasked 토큰 분포로 distill 합니다.

$$\mathcal{L}_{\texttt{iBOT}}=-\frac{1}{|\mathcal{M}|}\sum_{i\in\mathcal{M}}\mathbf{q}^{\texttt{t}}_{i}{}^{\!\top}\log\mathbf{q}^{\texttt{s}}_{i},\qquad\mathbf{q}_{i}=\mathrm{softmax}\!\big(\frac{g(\mathbf{z}^{\texttt{p}}_{i})-\mathbf{c}_{\rm iBOT}}{\tau}\big)$$

**경계 필드 → 범주형 라벨.** 채널 $`c\in\{d,\theta,\phi^{1},\phi^{2}\}`$ 마다 값 범위를 $`K`$ 개 bin 으로 이산화하고, 검증된 교사 값 $`a^{c}(p)`$ 를 soft 범주 라벨로 인코딩합니다.

$$\bar{y}^{c}_{k}(p)\;\propto\;\exp\!\Big(\!-\,\delta^{c}\big(k,\,a^{c}(p)\big)^{2}\big/\tau_{\ell}\Big),\qquad k=1,\dots,K$$

> "where $`\delta^{c}`$ is the distance from the center of bin $`k`$ to the value $`a^{c}(p)`$ and $`\tau_{\ell}`$ a label temperature. For the orientation channel $`\theta`$, whose range wraps at $`2\pi`$, the bins are circular and $`\delta^{\theta}`$ is an arc distance." (§3.3)
(방향 채널 $`\theta`$ 는 $`2\pi`$ 에서 wrap 하므로 bin 이 circular 이고 $`\delta^{\theta}`$ 는 호(arc) 거리입니다. 라벨은 일부러 좁게(몇 bin 폭) 둡니다 — 과도한 smoothing 은 모든 타깃을 균등분포로 밀어 신호를 지웁니다.)

**경계 손실.** forcing 마스크가 고른 경계 위치 $`\mathcal{B}`$ 에서의 채널별 cross-entropy 입니다.

$$\mathcal{L}_{\texttt{bnd}}=-\frac{1}{|\mathcal{B}|}\sum_{p\in\mathcal{B}}\;\sum_{c}\;\bar{y}^{c}(p)^{\!\top}\log\hat{y}^{c}(p)$$

**전체 목표.** 학생은 boundary-forced 마스크 $`\mathcal{M}^{+}`$ 아래 global view 를 처리하며 다음을 최소화합니다.

$$\mathcal{L}\;=\;\mathcal{L}_{\texttt{DINO}}\;+\;\lambda_{\texttt{i}}\,\mathcal{L}_{\texttt{iBOT}}\;+\;\lambda_{\texttt{b}}\,\mathcal{L}_{\texttt{bnd}}\;+\;\lambda_{\texttt{k}}\,\mathcal{L}_{\texttt{KoLeo}}$$

> "$`\mathcal{L}_{\texttt{iBOT}}`$ is computed over all masked tokens in $`\mathcal{M}^{+}`$, and $`\mathcal{L}_{\texttt{bnd}}`$ is computed over the boundary positions of $`\mathcal{B}\subset\mathcal{M}^{+}`$, so boundary tokens receive both losses, realizing the dual supervision of Sec. 3.2." (§3.5)
(iBOT 은 $`\mathcal{M}^{+}`$ 전체 마스킹 토큰에, boundary 는 $`\mathcal{B}`$ 에 계산되어 경계 토큰이 두 손실을 다 받습니다. 마지막 KoLeo 는 배치 내 class-token feature 를 퍼뜨리는 정규화입니다. 모든 교사 값은 stop-gradient 이며 boundary 브랜치에 별도 정규화는 붙이지 않습니다.)

### 왜 경계 필드인가 — 검증 가능성 (edge map 이 아니라 line segment)

![Figure 4 — vote-aggregation decoding (panel d)](https://arxiv.org/html/2607.05247/figures/overview/field_votes.png)

> "Figure 4: The boundary field at a glance. (a) Image boundaries are modeled as straight line segments; curved boundaries are chains of short segments. (b) The boundary field lifts the sparse segments into a dense map: every pixel near a segment stores its distance $`d`$ to the segment and three angles $`(\theta,\phi^{1},\phi^{2})`$ that locate the segment from that pixel; parallel segments share the same orientation color in $`\theta`$. (c) The encoding is deliberately redundant: any single pixel $`p`$ in a segment's support region carries enough information to reconstruct the entire segment. (d) Conversely, segments are decoded by letting all support pixels vote and aggregating the votes (orange strokes: individual noisy votes; dark lines: aggregated segments), which remains reliable even when individual values are noisy." (§3.3)
(선분은 support 픽셀들이 함께 지지하는 단일 가설이라 "구조 없음(방향 균등)" 귀무가설로 검증할 수 있는 반면, edge 픽셀은 고립된 필터 응답이라 임의 임계값으로만 취사선택됩니다. self-distillation 에서 교사 예측이 학생 타깃이 되므로, 검증되지 않은 edge 는 hallucinated 구조를 되먹임하지만 검증된 선분은 타깃을 깨끗이 유지합니다.)

경계 필드의 픽셀 속성 벡터는 $`\mathbf{a}(p)=\big(d_{p},\;\theta_{p},\;\phi^{1}_{p},\;\phi^{2}_{p}\big)`$ 로, support 영역 $`S_{\ell}=\{p:d_{p}\leq\tau_{d}\}`$ 의 어떤 단일 픽셀도 전체 선분을 복원할 정보를 담습니다. 이 many-pixels-one-segment 중복성이 (1) 학습되지 않은 필드의 decode(Finding 1)와 (2) noisy 예측에 대한 decode 강건성을 동시에 가능케 합니다.

### 학습 셋업

- **Backbone.** ViT-g/16 ~1.1B 파라미터, SwiGLU FFN, fp32 계산 RoPE, register 토큰 4개. PoC(§3.6)는 ViT-L/16.
- **경계 head.** 3-layer per-token MLP, 출력 stride $`s{=}2`$ 에서 head 차원 512, 학습 tile 위치 임베딩, 채널당 $`K{=}32`$ bin. frozen corner 점 detector 는 단일 블록 ViT(backbone 보다 수 자릿수 작음).
- **손실 가중.** $`\lambda_{\texttt{i}}=\lambda_{\texttt{b}}=1`$, KoLeo $`\lambda_{\texttt{k}}=0.1`$. non-boundary 위치 타깃은 상수 배경이 아니라 균등 무작위 라벨로 채워 trivial all-background 해를 제거.
- **최적화.** AdamW, global batch 3072, 300k iteration. base LR 은 $`\sqrt{\mathrm{bs}/1024}`$ 규칙으로 스케일 후 cosine 감쇠(linear warmup). weight decay 0.04→0.2(cosine), 교사 온도 0.04→0.07(첫 30k), EMA 모멘텀 0.994→1.0.
- **3단계 스케줄(DINOv3 따름).** 300k 사전학습 → 100k Gram anchoring → 100k 고해상 512px 적응. crop 은 global 256 / local 112 px. DINOv3(1M+100k+30k @ bs 4096) 대비 총 샘플의 1/3 미만.
- **데이터.** 2B raw 에서 curate 한 ~161M(160.75M) 코퍼스, 약 5/6 가 retrieval-curated. DINOv2 파이프라인(단일 DINOv2 ViT-B 검색 인코더)을 자체 소스에 구현. DINOv2 의 LVD-142M 급, DINOv3 의 LVD-1689M 보다 한 자릿수 작음.
- **증류.** frozen ViT-g 가 EMA 교사를 대체해 300M ViT-L / 86M ViT-B / 21M ViT-S 로 증류(학생당 300k iter + 512px 100k, Gram anchoring 생략).

---

## 📊 실험 설정과 결과

### PoC — ImageNet-1K, ViT-L/16 (설계 절제)

> "over the matched DINO+iBOT baseline, ImageNet-1K $`k`$-NN top-1 rises from 81.6% to 82.4%, while NYUv2 $`\delta_{1}`$ improves from 81.4% to 84.9% and RMSE drops from 0.474 to 0.440." (§3.6, Table 1)
(동일 설정 baseline 대비 global 의미(k-NN)와 dense geometry(depth)가 **동시에** 향상 — trade-off 가 아니라 공진화라는 §3.2 의 주장을 뒷받침합니다.)

| 변형 (ViT-L/16) | IN-1K k-NN top-1 ↑ | NYUv2 δ₁ ↑ | NYUv2 RMSE ↓ |
|---|---|---|---|
| DINO+iBOT baseline | 81.6% | 81.4% | 0.474 |
| + categorical boundary target (geometric only) | 81.8% | 84.4% | 0.446 |
| + dual supervision (iBOT loss on boundary tokens) | 82.0% | 84.7% | 0.443 |
| + RoPE backbone (final recipe) | **82.4%** | **84.9%** | **0.440** |
| w/ boundary forcing, semantic target only | 81.4% | 81.2% | 0.481 |

- **절제 읽기 — categorical boundary target 이 active ingredient.** 이것만 추가해도 dense 향상 대부분(+3.0 δ₁, RMSE 0.474→0.446)을 분류 손실 없이 확보합니다.
- **dual supervision 은 보완적.** +0.2 k-NN·+0.3 δ₁ 로, semantic·geometric 목표가 경쟁이 아니라 보완임을 확인.
- **RoPE 는 방법과 직교한 backbone 현대화.** +0.4 k-NN·+0.2 δ₁ 로, 방법이 아니라 backbone 개선분입니다(스케일 recipe 로 이월).
- **핵심 대조 — "어디를 마스킹"만으론 부족.** boundary forcing 하되 semantic 타깃만 복원하면 baseline 이하(δ₁ 81.2%, RMSE 0.481). "마스크는 *어디서* 구조를 만나는지, 범주형 목표는 *무엇을* 복원하는지를 정하며, 이득은 후자에서 온다"는 것이 핵심 메시지입니다.

### Dense 시각 태스크 (Table 2, frozen + single-linear decoder)

| Method | Param. | NYUv2↓ | KITTI↓ | ADE20k | Citysc. | VOC |
|---|---|---|---|---|---|---|
| Web-DINO | 7B/14 | 0.466 | 3.158 | 42.7 | 68.3 | 76.1 |
| DINOv3 | 7B/16 | 0.309 | 2.346 | 55.9 | 81.1 | 86.6 |
| V-JEPA 2.1 ViT-G | 2B/16 | 0.307 | 2.461 | 47.9 | 73.5 | 85.0 |
| AM-RADIOv2.5 | 1B/14 | 0.340 | 2.918 | 53.0 | 78.4 | 85.4 |
| DINOv2 | 1B/14 | 0.372 | 2.624 | 49.5 | 75.6 | 83.1 |
| DINOv3 ViT-H+ | 0.8B/16 | 0.352 | 2.635 | 54.8 | 79.5 | 85.8 |
| V-JEPA 2.1 ViT-g | 1B/16 | 0.350 | 2.601 | 47.8 | 71.8 | 84.7 |
| **LingBot-Vision ViT-g** | **1B/16** | **0.296** | 2.552 | 53.5 | 79.6 | **87.5** |

> "With a 1B-parameter ViT-g/16 backbone, LingBot-Vision attains the best NYUv2 RMSE of the entire table (0.296), ahead of the 7B-parameter DINOv3 (0.309) and the 2B-parameter V-JEPA 2.1 (0.307), with 7$`\times`$ and 2$`\times`$ fewer parameters respectively." (§5.1.2, Table 2)
(NYUv2 depth 는 전 표 최고이며 7배·2배 큰 모델을 앞섭니다. 저자 분석: linear decoder 는 표현이 이미 인코딩한 것만 읽어낼 수 있으므로, 표면 내부는 매끄럽고 occlusion 경계에서 급변하는 feature 를 요구하는 depth 가 boundary 사전학습의 이득이 가장 큰 regime 입니다.)

- **segmentation.** ADE20k 는 distilled DINOv3 ViT-H+ 에 1.3 mIoU 뒤지고(53.5 vs 54.8), Cityscapes 는 대등·VOC12 는 앞섭니다. 동급 DINOv2 대비 세 벤치 모두 +4 mIoU 이상. 남은 격차는 7B teacher 증류·전용 dense 목표를 쓴 DINOv3 계열뿐입니다.
- **patch 16 의 불리 감수.** patch-14 경쟁자보다 거친 토큰 grid 로 이 수치를 냅니다.

### Video 이해 (Table 3, training-free label propagation)

| Method | Param. | DAVIS J&F | YT-VOS J&F |
|---|---|---|---|
| DINOv3 | 7B/16 | 71.1 | 74.1 |
| DINOv3 ViT-H+ | 0.8B/16 | 71.1 | 74.0 |
| V-JEPA 2.1 ViT-g | 1B/16 | 68.1 | 72.3 |
| DINOv2 | 1B/14 | 63.9 | 65.6 |
| **LingBot-Vision ViT-g** | 1B/16 | 70.0 | 73.5 |

(7B DINOv3·distilled ViT-H+ 와 대등하고 나머지 전 모델을 앞섭니다. 동급 DINOv2 대비 +6.1/+7.9, video 로 학습한 V-JEPA 2.1 조차 -1.9/-1.2 뒤집니다 — frozen feature 의 시간 일관성이 강하다는 증거.)

### 전역 인식 (Table 4/5) — 알려진 trade-off

- **Flagship ImageNet-1K (Table 4).** LingBot-Vision 86.32 linear / 83.39 k-NN 로 DINOv2(87.00/83.68)와 대등, DINOv3-7B(87.87/85.68)·SigLIP 2(87.33/84.75)에 뒤집니다. 저자 해석: 남은 격차가 이미지 수준 인식에 집중되며 dense 는 우세 — 모델 용량을 국소 구조에 투자한 결과의 trade-off.
- **증류 계열 (Table 5).** ViT-L LingBot 은 NYU 0.310 으로 7B DINOv3(0.309)와 사실상 동률. "0.3B student 가 7B DINOv3 의 NYUv2 정확도를 ~23배 적은 파라미터로 맞춘다"는 것이 헤드라인 주장입니다.

### Downstream 페이오프 — LingBot-Depth 2.0 (Table 6/7/8)

![Figure 9 — LingBot-Depth 2.0 on mirror and glass scenes](https://arxiv.org/html/2607.05247/x1.png)

> "Figure 9: LingBot-Depth 2.0 on mirror and glass scenes. Each group shows the input RGB, the raw sensor depth and the refined depth for consecutive frames of a captured sequence, together with front and top views of the refined point cloud. The raw depth is missing exactly on the hardest surfaces: window panes, a glass balustrade and reflective floors return no measurements. The completed regions form flat, contiguous planes in the point clouds and remain stable over time." (§6)
(active depth 센서의 고전적 실패 사례(거울·유리)에서 raw depth 가 통째로 비는 자리를, 2.0 이 시간적으로 안정된 평면 geometry 로 채웁니다 — boundary-aware 인코더의 downstream 서명.)

masked depth modeling(MDM) recipe 는 그대로 두고 **인코더 초기화와 curated 데이터 규모** 두 가지만 바꿔 1.0→2.0 을 만듭니다.

- **인코더 절제 (Table 6).** 동일 MDM 파이프라인을 서로 다른 초기화로 학습 시, LingBot-Vision 인코더가 DINOv2·DINOv3 초기화를 거의 모든 벤치에서 능가. block-mask 최난도(DIODE-Indoor)에서 격차 최대(ViT-L 0.094 vs DINOv2 0.152, ViT-g 0.083 vs 0.118).
- **양적 결과 (Table 8, block/sparse).** ViT-L 2.0 이 8개 중 7개에서 최고 RMSE. 최난도에서 도약 폭이 큼 — block-mask DIODE-Indoor RMSE 반감(0.132→0.062), DIODE-Outdoor 3.404→2.440.
- **실센서 (Table 7).** 8개 카메라 구성 중 6개 최고, 투명 물체 ClearGrasp 에서 특히 강함(RMSE 0.010·0.012).
- **데이터 스케일 복리 (Fig. 8).** MDM 학습셋을 3M→150M 로 키우면 모든 초기화가 단조 개선되되 LingBot-Vision 초기화가 매 규모에서 선두 유지 — "더 나은 사전학습이 씻겨나가지 않고 복리로 쌓인다"(better pretraining compounds).

---

## ⚖️ 한계

- **전역 인식 열위는 구조적 trade-off.** 이미지 수준 분류(Table 4)에서 DINOv3-7B·SigLIP 2 에 일관 열위입니다. 저자 스스로 "용량을 국소 구조에 투자한 결과"라 인정하며, 이는 semantic invariance 가 필요한 하위 태스크(예: 순수 인식 head)에는 불리할 수 있습니다.
- **corner-point detector 라는 숨은 의존.** "annotation-free"를 표방하지만 파이프라인은 frozen 단일 블록 ViT corner detector 를 상시 고정합니다. 이것이 어떻게 사전학습(또는 별도 학습)되었는지, 얼마나 강건한지, 새 도메인(비자연 이미지)에서도 corner 를 잘 잡는지는 방법의 부트스트랩 전제(Finding 1)를 좌우하는데 본문 서술이 얕습니다.
- **a-contrario·voting 하이퍼의 민감도 불투명.** support 임계 $`\tau_{d}`$, 라벨 온도 $`\tau_{\ell}`$, bin 수 $`K`$, NFA 임계 등 검증·라벨링 하이퍼가 붕괴/신호 소실 경계를 정하는데(라벨이 넓으면 균등분포로 붕괴), 이들의 민감도 스윕이 제시되지 않아 재튜닝 비용을 가늠하기 어렵습니다.
- **선분(직선) 프리미티브의 편향.** 경계를 직선 선분(곡선은 짧은 선분의 사슬)으로 모델링하므로, 곡률이 지배적이거나 texture-heavy·유기적 형상이 많은 도메인에서 선분 프리미티브가 얼마나 충실한지는 검증되지 않았습니다.
- **비교의 공정성 주석.** 강한 dense baseline(DINOv3 ViT-H+, AM-RADIO)은 증류/다중 teacher 이득을 받는다고 저자가 명시하지만, 반대로 LingBot-Vision 은 depth-편향 downstream(NYUv2)을 헤드라인으로 삼아 자신에게 유리한 축을 강조하는 프레이밍이 있습니다. KITTI(야외, occlusion 경계 적음)에서 격차가 좁아지는 것이 이를 방증합니다.
- **자체 curated 코퍼스·평가셋.** 161M 사전학습 코퍼스와 LingBot depth 평가셋(1,751 프레임/35 장면)이 사내 자산이라, 데이터-방법 이득의 분리를 외부에서 독립 검증하기 어렵습니다(저자는 "데이터가 아니라 목표에서 온 이득"이라 주장하나 코퍼스 자체는 비공개).

---

## ♻️ 재현성

- **모델 공개.** "we release the pretrained models of LingBot-Vision to the community"(§7). GitHub(`robbyant/lingbot-vision`) · HuggingFace collection · 프로젝트 웹사이트가 존재합니다(본 분석 시점에 사전학습 가중치 공개 범위·라이선스는 미확인).
- **데이터 부분 공개.** LingBot-Depth 의 curated 3M 샘플은 공개되었으나(§6.1), LingBot-Vision 의 161M 사전학습 코퍼스와 150M depth 코퍼스는 사내 자산으로 비공개.
- **코드/커스텀 커널.** 경계 라벨·cross-entropy fused kernel, corner-line pairing·a-contrario 의 batched CUDA 재구현이 성능·효율의 핵심인데(§4.2), 이 커널 공개 여부는 본문에 명시되지 않습니다.
- **하드웨어/예산.** ViT-g 3단계(300k+100k+100k @ bs 3072) + 학생 3종 증류. GPU 수·wall-clock 은 미명시.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P2(구조적 멀티모달 관측 융합) — D9(action/dynamics-aware vision encoder)가 1차 접점.** D9 는 "generic SigLIP/ImageNet stem 대신 dynamics-aware(DynaFLIP) 또는 geometry-distilled(eVGGT) 인코더를 선호"한다는 결정입니다. LingBot-Vision 은 depth-native·boundary-grounded frozen 인코더로, 우리 관측 인코더 후보군(eVGGT/DINOv3)의 **직접 경쟁자**입니다. dense geometry(depth/occlusion 경계)를 명시적으로 인코딩한다는 점에서 D9 의 "geometry-grounded" 축과 정렬됩니다. D8(multi-camera spatial-geometric grounding, VGGT-류 다시점)와는 부분 정렬 — LingBot-Vision 은 단일 시점 dense feature 라 다시점 3D 정합(camera/point/track)은 제공하지 않습니다.
- **P5(World Model) — 지각 기질로서의 2차 접점.** 저자가 명시적으로 "frozen encoders are becoming the perception substrate of world models and robot policies, where an error in geometry is a wrong action"(§2.1)이라 프레이밍합니다. LingBot-Vision 자체는 world model 이 아니라(D28–D32 의 예측·action-conditioning 을 제안하지 않음), P5 world model 의 관측 백본 후보로만 관련됩니다. 순수 지원 관계.
- **Identity 지지/긴장.** 우리 Identity 는 "vision-dominant 관측을 넘어서는 구조적 융합"을 지향합니다(P2). LingBot-Vision 은 vision **단일** 인코더의 품질을 극한으로 올리는 방향이라, "관측 elevation"의 vision 축은 강하게 지지하지만 proprio/tactile/force 융합(D10–D12)은 다루지 않습니다 — 우리 스택의 vision 인코더 슬롯을 채우는 후보이지, 융합 문제 자체의 해답은 아닙니다.
- **P0(데이터).** 161M 코퍼스·depth 평가셋 curation 이 있으나 비공개·비-egocentric·비-tactile 이라 P0 의 우선 데이터 축(D24 egocentric/tactile)과 어긋납니다 — 접점 약함.

## ✨ 핀 논문 대비 델타

- **vs. eVGGT (P2 D8/D9 핀, geometry-distilled 인코더).** eVGGT 는 VGGT geometry 를 조작용으로 증류해 다시점 3D 정합을 빠르게 제공합니다. LingBot-Vision 은 다시점 geometry 를 명시적으로 풀지 않는 대신, **단일 시점 dense feature 의 경계/depth 충실도**를 self-supervised 로 직접 최적화합니다. "geometry 를 어디서 얻나"가 다릅니다 — eVGGT 는 다시점 supervision 증류, LingBot-Vision 은 라벨 없는 boundary 부트스트랩. depth linear-probe 에서 후자가 DINOv3-7B 를 앞서는 것이 신규점.
- **vs. DynaFLIP (P2 D9 핀, tri-modal-dynamics 인코더).** DynaFLIP 은 image-language-3D flow 의 **dynamics(움직임)** 를 인코딩합니다. LingBot-Vision 은 정적 이미지의 **static geometry(경계·형상)** 를 인코딩 — action-aware 는 아니지만 dense 공간 충실도는 더 직접적입니다. 두 축(dynamics-aware vs geometry-native)은 상보적이며, 우리 인코더 선택에서 경쟁이 아니라 조합 대상일 수 있습니다.
- **핀 대비 진짜 새로운 것.** "무엇을 마스킹할지를 경계가 정하게 하고, 교사가 스스로 검증한 범주형 경계 필드를 마스킹 토큰의 추가 타깃으로 라우팅"하는 SSL 목표 자체가 신규입니다. 우리 핀 어느 것도 마스킹 위치를 내용-구조로 결정하지 않습니다.

## ⚙️ 의사결정 함의

- **인코더 후보 리스트에 추가.** D9(action/dynamics-aware vision encoder) 결정에서 우리의 관측 vision 인코더 후보에 **LingBot-Vision(ViT-S/B/L 증류판)** 을 DINOv3·eVGGT·DynaFLIP 과 나란히 올립니다. 특히 depth/occlusion-경계 충실도가 중요한 접촉-풍부 조작에서, frozen linear-probe depth 우위(NYU 0.296)는 우리가 downstream 에서 얻고 싶은 정확한 속성입니다.
- **구체 config 레버.** 만약 P2 관측 스택에서 vision 인코더 backbone 을 교체 실험한다면, config 키는 `vision_encoder = {dinov3, evggt, lingbot_vision_vitl}` 같은 스위치가 됩니다. 크기-정확도 관점에서 **0.3B ViT-L 증류판**이 7B DINOv3 급 depth 를 ~23배 적은 파라미터로 낸다는 주장은, 온-로봇 지연/메모리 예산에 직접적인 함의를 줍니다(작은 인코더 채택 근거).
- **downstream depth 헤드가 있다면.** eVGGT-류 geometry head 나 depth-conditioned 관측이 파이프라인에 있으면, "인코더 초기화만 바꿔 depth completion 이 계단식 개선"(LingBot-Depth 1.0→2.0)이라는 결과는 인코더 교체가 값싼 레버임을 시사합니다.
- **채택 조건.** 단, 우리 조작 관측은 in-hand/egocentric·근접·저조도·모션블러가 많아, ImageNet-급 자연 이미지로 사전학습한 인코더의 dense feature 가 우리 도메인에서 유지되는지가 관문입니다(아래 실패 모드).

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 체크) frozen linear-probe 도메인 이전.** 공개 ViT-L/S 증류판을 받아 우리 로봇 카메라 프레임 소수에 대해 frozen feature 의 PCA 맵(Fig.6 재현)만 눈으로 확인 — in-hand 근접·손 가림·모션블러에서 경계가 여전히 crisp 한지. speckle/blocky 로 무너지면 이 도메인엔 부적합.
- **corner detector 의 도메인 강건성.** 방법의 부트스트랩이 frozen corner detector 에 의존하므로, 우리 도메인(질감 적은 손·단색 물체·반사면)에서 corner 가 희소하면 경계 부트스트랩이 실패할 수 있습니다. 이는 우리가 재학습할 경우의 위험이며, frozen 인코더만 쓸 경우엔 무관.
- **patch-16·해상도 정합.** LingBot-Vision 은 patch 16·512px 적응입니다. 우리 관측 해상도/patch grid 와 어긋나면 dense readout 이 손상될 수 있어, 우리 파이프라인의 토큰 grid 에 맞춰 재적응이 필요한지 확인.
- **전역 semantic 약점의 하류 영향.** 우리 VLA backbone 이 인코더 feature 에서 semantic 판별(물체 식별/언어 grounding)을 요구한다면, LingBot-Vision 의 이미지 수준 인식 열위(Table 4)가 병목이 될 수 있습니다 — dense geometry 는 얻되 semantic 은 별도 스트림으로 보강해야 할 수 있습니다.
- **depth 특화의 과적합 위험.** 헤드라인 우위가 depth(NYUv2)에 집중되고 KITTI 에서 좁아지는 패턴은, "occlusion 경계 밀도가 높은 실내 장면"에 이득이 편중됨을 시사합니다. 우리 조작 장면의 경계 밀도가 낮으면(넓은 테이블·단색 배경) 이득이 희석될 수 있습니다.
- **공개 범위·라이선스.** 가중치/코드/커스텀 커널의 실제 공개 범위와 라이선스가 상용/연구 사용에 맞는지 — 채택 전 확인해야 할 사무적 관문(openpi Apache-2.0 스택과의 호환).

## 💡 컨텍스트 제안

- **P2 §5 non-pinned 후보로 추적 제안.** LingBot-Vision(arXiv:2607.05247)을 P2 methodology base 목록에 "geometry-native SSL 인코더(depth-strong frozen features), D9 후보" 역할로 올리는 것을 제안합니다. eVGGT(핀)·DynaFLIP(핀)과 상보적이며, 특히 depth 충실도 축에서 DINOv3-7B 를 넘는 유일 후보라 D9 결정의 대안 근거로 유용합니다. (핀 교체가 아니라 non-pinned 추적 — 로봇 조작 도메인 이전 검증 전이므로.)
- 그 외 Decision(D8/D10–D12)·다른 pillar 이동 트리거는 없음. context 파일은 수정하지 않았습니다.

> 💡 base 매핑은 `/implement-design analysis/2607.05247/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
