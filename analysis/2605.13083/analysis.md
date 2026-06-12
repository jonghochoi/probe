# Paper Analysis — TouchAnything: A Dataset and Framework for Bimanual Tactile Estimation from Egocentric Video

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | TouchAnything: A Dataset and Framework for Bimanual Tactile Estimation from Egocentric Video |
| 저자 | Jianyi Zhou, Ziteng Gao, Feiyang Hong, Zirui Liu, Guannan Zhang, Weisheng Dai, Ruichen Zhen, Chuqiao Lyu, Haotian Wu, Yinian Mao, Xushi Wang, Yuxiang Jiang, Wenbo Ding, Shuo Yang (Harbin Institute of Technology Shenzhen · Meituan Academy of Robotics · Tsinghua Shenzhen International Graduate School) |
| 링크 | [arXiv:2605.13083](https://arxiv.org/abs/2605.13083) · [Website](https://jianyi2004.github.io/TouchAnything-Website/) |
| 발행일 / 버전 | 2026-05-13 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-10 |
| 관련 Pillar | P0, P2 |
| 태그 | tactile, egocentric-data, dataset |
| 카탈로그 | dataset/human/EgoTouch |
| Design 적용 | 🚫 비대상 (dataset) |

---

## 🧭 한 줄 요약 (TL;DR)

Egocentric 비디오에 결여된 촉각(접촉·압력) supervision 을 vision 으로부터 직접 추론하기 위해, 머리 + 양손목 멀티뷰 RGB·양손 3D pose·dense 압력맵을 동기화한 대규모 데이터셋 **EgoTouch** (208 tasks / 1,891 episodes / ~2.1M frames) 을 구축하고, ego 뷰를 주입력으로 쓰되 손목 뷰를 inference 때 유연하게 활용하는 vision-to-touch 베이스라인 **TouchAnything** 을 함께 제시합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 대규모로 수집 가능한 egocentric 인간 비디오는 임바디드 학습의 핵심 자원이 되었지만, 접촉·힘·압력을 직접 알려주는 **촉각 모달리티가 거의 빠져 있어** 모델이 물리적으로 근거 있는 상호작용 동역학을 학습하기 어렵습니다.
- **기존 접근의 한계** — 고품질 촉각 하드웨어를 대규모 배치하는 것은 비싸고 침습적이며 확장이 어렵습니다. 즉 시각 데이터의 풍부함과 촉각 supervision 의 희소성이 정면으로 대비됩니다.
- **vision-to-touch 의 데이터 병목** — 기존 vision-to-touch 데이터셋은 단일 뷰이거나(`PressureVision`) 손-표면 접촉·단일 손가락 누름 같은 좁은 설정(`EgoPressure`)에 국한되어, 현실적인 양손 hand-object 조작을 다루지 못합니다.
- **본 논문의 가설** — egocentric 머리 뷰만으로는 접촉면이 손/물체에 의해 **가려지므로**(occlusion), 접촉면을 직접 관측하는 **손목 장착 카메라**를 보완 뷰로 더하면 촉각 추론의 모호성을 줄일 수 있습니다.
- **왜 지금 중요한가** — "촉각을 시각에서 추론할 수 있는가"가 성립하면, 대규모 ego 비디오에 확장 가능한 촉각 supervision 을 붙여 물리 근거 있는 임바디드 학습으로 연결할 수 있습니다.

---

## 🧩 핵심 기여

- **EgoTouch 데이터셋** — 양손 hand-object 상호작용을 위한 대규모 멀티뷰 egocentric 데이터셋. 208 tasks, 1,891 episodes, 머리 1 + 손목 2 카메라의 동기화 RGB, 양손 3D hand pose(42 joints), 양손 dense 연속 압력맵을 다양한 실내외 환경에서 제공.
- **멀티뷰 vision-to-touch 벤치마크** — seen / unseen object 평가 프로토콜 + 여러 카메라 뷰 구성을 정의해, 보완적 손목 뷰가 촉각 예측에 주는 영향을 체계적으로 분석 가능하게 함.
- **TouchAnything 베이스라인** — cross-view fusion + **view dropout** 학습으로 ego-only ~ 멀티뷰 입력을 유연하게 처리하고, 손목 뷰가 있을 때 촉각 예측을 개선하는 모델.
- **occlusion 해소 관점** — 손목 뷰가 ego 뷰에서 가려진 접촉면을 복원함을 정량/정성적으로 입증 (전체 기준 Contact IoU 상대 +5.0%, Volumetric IoU 상대 +6.1%).

![Figure 1 — EgoTouch 멀티뷰 + 동기화 촉각 개요](https://arxiv.org/html/2605.13083/x1.png)

> "Figure 1: EgoTouch combines egocentric and wrist-mounted views with synchronized 3D hand pose and dense tactile pressure maps, providing complementary visual evidence for learning contact-aware interactions." (§1)
(한글 해설 — 머리 뷰의 전역 맥락과 손목 뷰의 근접 접촉 관측, 그리고 동기화된 양손 압력맵이 어떻게 상호 보완 증거가 되는지를 한 장으로 보여줍니다.)

---

## 🔑 기술 키워드

- **Vision-to-touch prediction** — RGB 관측만으로 촉각(압력/접촉)을 추론하는 과제 — 비싼 촉각 센서를 시각으로 대체·확장하려는 시도.
- **Egocentric multi-view capture** — 머리(전역) + 양 손목(근접) 카메라로 동일 상호작용을 동시 촬영하는 wearable 셋업 — 한 손이 한 손을 가리는 양손 occlusion 을 다른 뷰로 메움.
- **Dense pressure map** — 손당 캐노니컬 $`21\times 21`$ 격자로 표현된 연속 압력 분포 — binary 접촉을 넘어 "어디에 얼마나" 눌렸는지의 dense supervision.
- **View dropout** — 학습 중 손목 뷰를 확률적으로 떨어뜨려 임의 뷰 부분집합에 견고하게 만드는 전략 — modality dropout 의 멀티뷰 버전.
- **Cross-view attention** — 뷰별 summary token 들 사이의 경량 attention 으로 보완 정보를 교환 — 가려진 ego 뷰에 손목 뷰의 접촉 정보를 주입.
- **Gated view fusion** — 뷰별 중요도 가중치를 softmax 로 학습해 누락/불확실 뷰에 강건한 fused feature 를 만드는 게이팅.
- **Pose-vision cross-attention** — 손 joint token 이 시각 patch 를 query 해 공간적으로 근거 있는 접촉 추론을 하는 융합 — joint→관련 시각 영역 매핑.
- **Contact-aware weighted loss** — 압력 > 0.1 인 접촉 픽셀에 큰 가중치를 줘 all-zero 붕괴를 막는 sparsity-aware 회귀 손실.
- **Volumetric IoU** — 압력 크기까지 반영하는 IoU — 2D 압력을 "압력 부피"로 보고 예측/정답 부피의 교집합/합집합.

---

## 🔬 방법론

### 직관

TouchAnything 의 목표는 단순합니다 — 여러 카메라 뷰와 양손 pose 를 입력받아 각 손의 dense 압력맵을 출력하는 것입니다. 핵심 난점은 두 가지입니다. (1) egocentric 머리 뷰에서는 실제로 압력이 가해지는 손바닥 면이 손이나 물체에 자주 가려지고, (2) 배치 환경마다 가용 카메라 구성이 달라집니다.

첫 난점에 대해, 손목에 장착한 fisheye 카메라가 접촉면을 근접에서 직접 본다는 점을 이용합니다. 다만 모든 뷰를 같은 backbone(공유 DINOv2)으로 인코딩하되 어느 카메라에서 왔는지를 view embedding 으로 구분하고, 뷰별 요약 토큰끼리 cross-view attention 으로 정보를 교환한 뒤 gated fusion 으로 합칩니다. 이렇게 하면 가려진 ego 뷰가 손목 뷰의 접촉 증거를 빌려올 수 있습니다.

두 번째 난점에 대해서는 학습 중 손목 뷰를 무작위로 떨어뜨리는 **view dropout** 을 씁니다. ego 뷰는 항상 유지하되 각 손목 뷰를 확률 $`p=0.3`$ 로 독립 드롭하면, 모델이 4가지 입력 구성(ego-only, ego+왼손목, ego+오른손목, 전체) 모두에 노출되어, 추론 때 구조 변경 없이 임의 뷰 부분집합으로 동작합니다.

마지막으로, 시각 특징과 손 pose 를 pose-vision cross-attention 으로 융합해 각 joint 가 자신과 관련된 시각 patch 에 attend 하게 하고, 42개 joint 특징을 양손(각 21 joint)으로 나눠 손당 $`21\times 21`$ 압력맵으로 디코딩합니다. 압력맵은 매우 희소하므로 접촉 픽셀에 더 큰 손실 가중치를 줘 all-zero 붕괴를 방지합니다.

### 아키텍처

프레임워크는 공유 시각 인코더 · cross-view fusion · pose-aware fusion · tactile decoder 로 구성됩니다.

> "Our framework consists of a shared visual encoder, a cross-view fusion module, a pose-aware fusion mechanism, and a tactile decoder, enabling joint modeling of appearance, geometry, and motion cues." (§3.2)
(한글 해설 — appearance(시각) · geometry(pose) · motion(temporal) 세 단서를 한 파이프라인에서 통합하는 것이 설계 의도입니다.)

![Figure 5 — 멀티뷰 촉각 예측 모델 아키텍처](https://arxiv.org/html/2605.13083/x4.png)

> "Figure 5: Architecture of the multi-view tactile prediction model. A shared backbone encodes each view with view embeddings. Cross-view attention and gated fusion produce unified visual features, which are combined with hand pose through pose-aware fusion and decoded into bilateral pressure maps." (§3.2)
(한글 해설 — 공유 backbone → cross-view attention → gated fusion → pose-aware fusion → bilateral decoder 의 전체 데이터 흐름을 보여줍니다.)

**(1) 멀티뷰 시각 인코더 — 공유 backbone + view embedding.** 모든 뷰를 공유 DINOv2-ViT-B/14 로 인코딩해 프레임당 $`N=256`$ 개 patch token (차원 $`D=768`$)을 뽑고, 카메라 정체성을 구분하는 학습형 view embedding $`\mathbf{e}_{v}`$ 을 더합니다.

$$\mathbf{F}_{v}=\text{DINOv2}(V_{v})+\mathbf{e}_{v},\quad\mathbf{F}_{v}\in\mathbb{R}^{T\times N\times D}$$

> "Sharing the backbone across views reduces the parameter count from $`3\times 86\text{M}`$ (separate encoders) to $`86\text{M}+3\times 768`$ (shared encoder + view embeddings), improving both efficiency and generalization." (§9.2)
(한글 해설 — 뷰마다 별도 인코더를 두지 않고 backbone 을 공유함으로써 파라미터를 크게 줄이고 일반화를 돕는다는 효율 논거입니다.)

**(2) Cross-view attention.** $`N\times|\mathcal{V}|`$ 토큰 전체에 대한 비싼 attention 대신, 뷰별 global average pooling 으로 summary token 을 뽑아 경량 cross-view transformer 를 적용합니다.

$$\mathbf{s}_{v}=\text{MeanPool}(\mathbf{F}_{v}),\quad[\hat{\mathbf{s}}_{1},\ldots,\hat{\mathbf{s}}_{|\mathcal{V}|}]=\text{CrossViewTransformer}([\mathbf{s}_{1},\ldots,\mathbf{s}_{|\mathcal{V}|}])$$

각 뷰 요약이 다른 뷰 요약에 attend 해, 손목 뷰가 ego 뷰에 가려진 접촉 영역을 알려줄 수 있습니다.

**(3) Gated view fusion.** 융합된 요약 토큰을 게이팅 네트워크에 통과시켜 뷰별 중요도 가중치를 학습하고, 원래 patch feature 들을 가중합합니다.

$$w_{v}=\text{softmax}\big(\text{MLP}(\hat{\mathbf{s}}_{v})\big),\quad\mathbf{F}^{fused}=\sum_{v\in\mathcal{V}}w_{v}\cdot\mathbf{F}_{v}$$

출력 $`\mathbf{F}^{fused}\in\mathbb{R}^{T\times N\times D}`$ 은 단일 뷰 feature 와 같은 shape 라 하류 모듈과 호환됩니다(누락 뷰에 강건).

**(4) Temporal transformer.** fused feature 에 windowed temporal transformer 를 적용해 grasping·sliding 같은 동역학을 포착합니다.

$$\mathbf{H}=\text{TemporalTransformer}(\mathbf{F}^{fused}),\quad\mathbf{H}\in\mathbb{R}^{T\times N\times D}$$

**(5) Pose encoder + pose-vision cross-attention.** 양손 pose $`\mathbf{P}\in\mathbb{R}^{T\times 42\times 3}`$ 을 transformer pose encoder 로 per-joint feature $`\mathbf{G}\in\mathbb{R}^{T\times 42\times D}`$ 로 인코딩한 뒤, 각 joint 가 시각 patch 를 query 하는 cross-attention 으로 공간적으로 근거 있는 융합을 합니다.

$$\mathbf{Z}=\text{CrossAttn}(Q{=}\mathbf{G},\;K{=}\mathbf{H},\;V{=}\mathbf{H}),\quad\mathbf{Z}\in\mathbb{R}^{T\times 42\times D}$$

**(6) Joint-level tactile decoder.** 42-joint feature 를 왼손(1–21)·오른손(22–42)으로 나눠 각각 MLP + reshape 로 $`21\times 21`$ 압력맵을 독립 디코딩하고, sigmoid 로 $`[0,1]`$ 범위를 보장합니다.

$$\hat{\mathbf{M}}^{left}_{t}=\sigma\big(\text{MLP}(\mathbf{Z}^{left}_{t})\big)\in[0,1]^{21\times 21},\quad\hat{\mathbf{M}}^{right}_{t}=\sigma\big(\text{MLP}(\mathbf{Z}^{right}_{t})\big)\in[0,1]^{21\times 21}$$

### 학습 목표 / 손실

가중 회귀 손실은 픽셀 단위 재구성 + 공간 정규화를 결합합니다.

$$\mathcal{L}=\lambda_{mse}\mathcal{L}_{MSE}+\lambda_{l1}\mathcal{L}_{L1}+\lambda_{tv}\mathcal{L}_{TV}(\hat{\mathbf{M}})$$

> "To address the sparsity of tactile maps and prevent the model from collapsing to all-zero predictions, we apply higher loss weights to contact regions where pressure exceeds a threshold (0.1). We use $`\lambda_{mse}=1.0`$ , $`\lambda_{l1}=0.5`$ , $`\lambda_{tv}=0.01`$ , and a contact-region weight of 3.0." (§3.3)
(한글 해설 — $`\mathcal{L}_{MSE}`$ · $`\mathcal{L}_{L1}`$ 은 압력 재구성 오차, $`\mathcal{L}_{TV}`$ 는 공간 smoothness 를 유도하며, 희소한 촉각맵에서 모델이 전부 0으로 붕괴하는 것을 막기 위해 접촉 픽셀(압력 > 0.1)에 가중치 3.0 을 줍니다.)

### 학습 셋업

> "The visual encoder is a frozen DINOv2-Base (ViT-B/14) backbone initialized from a pretrained checkpoint." (§4.1)
(한글 해설 — 시각 backbone 은 사전학습 가중치로 초기화 후 **frozen** 으로 둡니다 — 학습은 fusion/디코더 등 상부 모듈에 집중됩니다.)

- **입력 클립** — $`T=8`$ frames, frame interval 2, 3개 동기화 RGB 뷰(ego 1 + 손목 2), 모두 $`224\times 224`$ 리사이즈, 42 3D hand joints(WiLoR), 양손 $`21\times 21`$ 촉각맵을 $`[0,1]`$ 정규화.
- **옵티마이저** — AdamW, lr $`5\times 10^{-5}`$ , weight decay 0.05, betas $`(0.9,0.999)`$ , cosine schedule(warmup 10 epochs, min lr $`10^{-6}`$ ), 25 epochs.
- **분산 학습** — torchrun DDP, 기본 6 GPU × per-GPU batch 16 × grad accumulation 3 → effective batch 288.
- **증강** — glove color augmentation 확률 0.2.
- **view dropout** — 각 손목 뷰 독립 드롭 확률 $`p=0.3`$ , ego 뷰는 항상 유지.

---

## 📊 실험 설정과 결과

**데이터 split / 메트릭.** episode 단위 80/10/10 split(temporal leakage 방지), test 를 seen-object / unseen-object 로 분할. 메트릭은 PressureVision 을 따라 Temporal Accuracy↑ · Contact IoU↑ · Volumetric IoU↑ · MAE↓ 를 사용. Volumetric IoU 는 압력 크기를 반영합니다.

$$IoU_{vol}=\frac{\sum^{i,j}min(P_{i,j},\hat{P}_{i,j})}{\sum^{i,j}max(P_{i,j},\hat{P}_{i,j})}$$

**Main result (전체, 5 시나리오 평균).** Table 2 의 Overall 행 — 모든 method 가 동일 아키텍처·학습 레시피를 쓰고, 손목 뷰 유무만 다릅니다.

| 구성 | Seen C.IoU | Seen V.IoU | Seen MAE | Unseen C.IoU | Unseen V.IoU | Unseen MAE |
|---|---|---|---|---|---|---|
| Ego-only | 0.4792 | 0.4311 | 0.0456 | 0.4396 | 0.3743 | 0.0615 |
| Ego + wL | 0.5030 (↑5.0%) | 0.4575 (↑6.1%) | 0.0437 (↓4.2%) | 0.4499 (↑2.3%) | 0.3856 (↑3.0%) | 0.0601 (↓2.3%) |
| Ego + wR | 0.5024 (↑4.8%) | 0.4572 (↑6.1%) | 0.0437 (↓4.2%) | 0.4497 (↑2.3%) | 0.3854 (↑3.0%) | 0.0602 (↓2.1%) |
| Ego + wL + wR | 0.5030 (↑5.0%) | 0.4575 (↑6.1%) | 0.0436 (↓4.4%) | 0.4496 (↑2.3%) | 0.3852 (↑2.9%) | 0.0601 (↓2.3%) |

> "Overall, Ego + wL + wR improves Contact IoU from 0.4792 to 0.5030 and Volumetric IoU from 0.4311 to 0.4575 on seen objects, and from 0.4396 to 0.4496 and 0.3743 to 0.3852 on unseen objects, respectively." (§4.2, Table 2)
(한글 해설 — 손목 뷰 추가는 특히 접촉 위치(Contact IoU)와 압력 크기(Volumetric IoU)에서 일관된 개선을 줍니다. 단, unseen object 의 개선폭(~2–3%)은 seen(~5–6%)보다 작습니다.)

> "We also find that a single wrist view already captures much of the complementary evidence ... Thus, the main benefit comes from adding at least one contact-aware viewpoint, while the second wrist view provides additional gains mainly under stronger bimanual occlusion." (§4.2)
(한글 해설 — **한 개의 손목 뷰만으로도 보완 증거의 대부분이 확보**되고(Ego+wL 과 Ego+wL+wR 의 전체 수치가 거의 동일), 두 번째 손목 뷰의 추가 이득은 강한 양손 occlusion 상황에 한정됩니다 — fisheye 가 반대 손까지 종종 관측하기 때문.)

**시나리오별 읽기.** Temporal Accuracy 는 시나리오마다 들쭉날쭉하며 일부 unseen 설정(Workbench unseen ↓6.9~7.1%, Outdoor unseen ↓1.2%)에서는 손목 뷰가 오히려 떨어뜨립니다. 저자 해석:

> "Temporal Accuracy changes more modestly and varies across scenarios, suggesting that wrist views mainly help resolve where and how strongly contact occurs rather than simply whether contact occurs." (§4.2)
(한글 해설 — 손목 뷰의 이득은 "접촉이 일어났는가(whether)"보다 "어디에 얼마나 세게(where/how strongly)"의 해상에 집중됩니다. 접촉 onset/offset 의 시간 정확도는 크게 개선되지 않습니다.)

**Ablation 1 — view dropout (Table 3, seen split).** 각 행이 분리하는 것: dropout 없이 학습하면 전체 뷰에 과의존해 손목 뷰가 없을 때 급격히 무너지고, dropout 을 쓰면 부분 뷰에서도 견고합니다.

| Training | Ego-only V.IoU | Ego+wL/wR V.IoU | All-view V.IoU | ΔV (ego vs all) |
|---|---|---|---|---|
| No dropout | 0.3233 | 0.4073 | 0.4441 | −27.20% |
| w/ dropout | 0.4311 | 0.4573 | 0.4575 | −5.78% |

> "the relative performance drop ($`\Delta`$ V) between all-view and ego-only inference improves from -27.20% to -5.78% on the seen-object split." (§4.3, Table 3)
(한글 해설 — view dropout 의 핵심 효과는 절대 성능이 아니라 **뷰 누락에 대한 강건성**입니다: all-view 대비 ego-only 의 V.IoU 하락이 −27.20% → −5.78% 로 크게 완화됩니다. dropout 학습 시 ego+wL/wR 와 all-view 의 격차는 −0.04% 로 사실상 소멸.)

**Ablation 2 — data scaling (Figure 6).** 25/50/75/100% 로 학습량을 늘릴수록 Contact·Volumetric IoU 가 일관 상승하며 고데이터 구간에서도 saturate 하지 않습니다.

> "the improvement does not saturate at higher data regimes, suggesting that the proposed task remains data-hungry and can further benefit from larger-scale tactile datasets." (§4.3)
(한글 해설 — vision-to-touch 과제는 여전히 data-hungry — 더 큰 촉각 데이터셋이 추가 이득을 줄 여지가 있다는 신호로, 데이터셋 확장의 동기를 제공합니다.)

![Figure 7 — 손목 뷰가 가려진 접촉을 복원](https://arxiv.org/html/2605.13083/x6.png)

> "Figure 7: Multi-view wrist cameras recover occluded hand–object contact. Top: the egocentric view suffers from occlusion, while wrist-mounted views reveal the contact interface. Bottom: ego-only prediction misses contact in occluded regions, whereas multi-view prediction recovers accurate pressure distributions consistent with the ground truth." (§4.4)
(한글 해설 — ego-only 가 가려진 영역의 접촉을 놓치는 반면, 손목 뷰를 더한 멀티뷰 예측이 정답에 가까운 압력 분포를 복원함을 정성적으로 보여줍니다.)

**데이터셋 비교 (Table 1).** EgoTouch 는 in-the-wild · 양손 · 손목 뷰 · 실제 dense pressure 를 **동시에** 제공하는 첫 데이터셋이라고 주장합니다.

| Dataset | In-the-wild | Hand Pose | Contact | Wrist Views | Hands | Frames |
|---|---|---|---|---|---|---|
| EgoPressure [9] | ✗ | Est. | Pressure | ✗ | Single | 4.3M |
| EgoDex [14] | ✗ | Est. | Analytical | ✗ | Biman. | 90M |
| OpenTouch [25] | ✓ | Glove | Pressure | ✗ | Single | ~500k |
| **EgoTouch (Ours)** | ✓ | Glove + Est. | Pressure | ✓ | Biman. | 2.1M |

---

## ⚖️ 한계

- **Glove appearance bias (저자 명시)** — 모든 학습 데이터가 촉각 장갑 착용 상태로 수집되어, 장갑 고유의 외형이 학습되고 bare-hand 촉각 추정으로의 일반화가 제한됩니다. 시각 기반 추론이라 입력 분포(장갑 색/질감)에 강하게 묶이는 구조적 약점입니다.
- **Data-hungry · 미포화 (저자 명시)** — data scaling 이 saturate 하지 않았다는 것은 현재 성능이 데이터 상한에 도달하지 못했음을 뜻하며, 절대 IoU 가 ~0.50 수준(접촉 IoU 절반 정도)이라 dense 압력 추정의 정밀도 자체가 아직 낮습니다.
- **시각 단서 과의존 → 색 유사성에 취약 (저자 명시, Figure 12)** — 검은 장갑 × 검은 천처럼 저대비 상황에서 근접/occlusion 패턴을 접촉으로 **환각(hallucinate)** 합니다. 모델이 "시각적 근접"을 "접촉"으로 학습했음을 드러내며, depth/segmentation·temporal consistency 없이는 근접과 접촉을 분리하지 못합니다.
- **Temporal accuracy 미개선 (추론된 갭)** — 손목 뷰는 접촉의 공간/크기는 개선하나 onset/offset 시간 정확도는 거의 개선하지 못하고 일부 시나리오에선 악화됩니다. 즉 "언제 접촉이 시작/종료되는가"는 멀티뷰만으로 풀리지 않는 별개 문제입니다.
- **압력의 절대 캘리브레이션 부재 (추론된 갭)** — 출력이 $`[0,1]`$ 정규화 압력이라 절대 힘(N) 단위가 아니며, 장갑 센서 baseline 보정·broken column interpolation 등 전처리에 의존해 절대 force/torque supervision 으로 바로 쓰기 어렵습니다.
- **베이스라인의 단순성 (추론된 갭)** — frozen DINOv2 + 경량 fusion 의 "baseline"으로 명시되어, 멀티뷰 geometry 를 명시적으로 등록(3D registration)하지 않고 summary-token cross-attention 에 그칩니다 — 공간 기하 정보가 약하게만 활용됩니다.

---

## ♻️ 재현성

- **데이터/코드/벤치마크 공개 예정** — "We will publicly release the dataset, code, and benchmark" (§Abstract). Project page: https://jianyi2004.github.io/TouchAnything-Website/ (코드/데이터 링크는 공개 시점 확인 필요).
- **하드웨어 셋업 상세** — Appendix 8.1 에 head/wrist RGB 카메라, Rokoko mocap glove(양손 21 joints), custom pressure glove($`16\times16`$ tactile array/palm, 256-ch 8-bit @921600 baud), HTC Vive Tracker(6-DoF) 구성과 30Hz software 동기화 전략, 에피소드 디렉터리 구조(`chest.mp4`/`left.mp4`/`right.mp4`/`jq_pressure.json`/`rokoko_hands.json`/`vive_poses.json`)를 명시.
- **전처리 파이프라인** — 256-d raw → $`21\times21`$ hand-shaped grid 매핑(hand-specific JSON), 오른손 수평 미러링, first-frame baseline 차감, broken column interpolation, tactile/bending 분리 정규화, HDF5 변환(64 workers, gzip-4)까지 Appendix 8.2–8.3 에 기술 — 재현 가능 수준.
- **구현 디테일** — PyTorch, frozen DINOv2-ViT-B/14, WiLoR hand pose, AdamW/cosine/25 epochs, DDP 6 GPU(effective batch 288) 등 Appendix 9 에 상세.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P0(VLA Datasets & Benchmarks) — 주 연결.** EgoTouch 는 P0 가 first-class gap 으로 추적하는 **tactile / 접촉 모달리티 데이터**(D25(tactile·force·torque 데이터 스카우팅))의 직접적 신규 릴리스이며, egocentric 우선 데이터 축(D24(priority data axis = egocentric human video))과 정확히 일치합니다. 벤치마크(멀티뷰 vision-to-touch, seen/unseen 프로토콜)는 D26(benchmark/eval 스카우팅 범위)에 들어오고, 라이선스/사용성(D27) 측면에서 공개 예정이나 **장갑 기반 + 공개 라이선스 미확인** 상태라 ⚠️ 플래그가 필요합니다. `catalogs/dataset.md`(👤 human ego, tactile)와 `catalogs/benchmark.md`(✋ dexterous / 🧪 eval) 양쪽에 등재 후보.
- **P2(Structured Multimodal Observation Fusion) — 부 연결.** 멀티뷰 cross-view attention + gated fusion 은 D8(multi-camera spatial-geometric grounding)의 **경량 fallback(flat-concat 대체 cross-attention fuser)** 사례이고, view dropout 은 D10(heterogeneous modality fusion beyond concat)의 modality-dropout graceful degradation 과 정확히 같은 메커니즘입니다. pose-vision cross-attention 으로 joint 가 시각 patch 에 attend 하는 것은 D11(proprio-tactile-force token 구성)·D12(topology-aware hand-level aggregation)의 관점에서 "손 joint 를 접촉 토큰의 앵커로 쓰는" 구체 구현 참고가 됩니다.
- **Identity 지지/긴장.** Identity 의 "per-finger proprio-tactile binding, flat-concat 초월" 주장을 **데이터 측에서** 받쳐줍니다(촉각 supervision 의 희소성 해소). 단 본 논문은 **vision→touch 추론(인지)** 이지 정책/액션이 아니며, 출력이 손당 $`21\times21`$ palm 격자라 우리의 per-finger fingertip 촉각(Sharpa Deform Map)과 토폴로지가 다릅니다 — 직접 정책 입력이 아니라 데이터·표현 참고로 봐야 합니다.
- **경쟁자 함의.** P0 핀의 EgoDex(arXiv:2505.11709)·OpenTouch 대비, EgoTouch 는 **양손 + 손목 뷰 + 실제 dense pressure 동시 제공**을 차별점으로 내세웁니다(Table 1).

---

## ✨ 핀 논문 대비 델타

- **EgoDex(arXiv:2505.11709, P0 핀) 대비** — EgoDex 는 829h 대규모 egocentric dexterous + 3D hand tracking 이지만 **촉각이 없고 단일 ego 뷰**입니다. EgoTouch 는 규모는 훨씬 작으나(~20h / 2.1M frames) **실제 dense pressure supervision + 양 손목 보완 뷰**를 추가했다는 점이 진짜 델타입니다 — "촉각 결여"라는 EgoDex 류의 빈칸을 직접 메웁니다.
- **RH20T(arXiv:2307.00595, P0 핀, F/T) 대비** — RH20T 는 로봇 teleop + 6축 wrist F/T 의 접촉 모달리티 corpus 이나 **third-person 로봇 + wrist 단일 F/T**입니다. EgoTouch 는 **인간 egocentric + 손바닥 면 dense pressure map** 으로, 접촉의 공간 분포(어디를)까지 담는다는 점이 다릅니다(축: torque/force → spatial pressure).
- **종합 델타** — "egocentric × 양손 × 손목 뷰 × 실제 dense pressure" 의 동시 결합은 기존 P0 핀 어느 것도 제공하지 않던 조합입니다. 다만 **베이스라인 모델 자체의 신규성은 낮습니다**(공유 DINOv2 + 표준 cross-attention/gating) — 기여의 무게중심은 데이터셋/벤치마크입니다.

---

## ⚙️ 의사결정 함의

- **D25 / `catalogs/dataset.md` 업데이트** — EgoTouch 를 👤 human-ego × tactile 항목으로 등재하고, `License` 칸에 ❓(공개 예정·미확인) 또는 확인 후 마크, `Source`/`Facts` 에 "208 tasks / 1,891 ep / ~2.1M frames / head+dual-wrist RGB / 양손 42-joint pose / 양손 $`21\times21`$ pressure / 30Hz" 를 기록. 우리 ego 데이터 계획의 **촉각 보강 레퍼런스**로 핀 후보(쿼터 리밸런스 시).
- **데이터 수집 셋업 차용 검토** — head + dual-wrist 동기화 wearable 셋업(30Hz software sync, Vive Tracker 6-DoF, Rokoko glove)은 우리 in-house ego 수집 계획에 그대로 참고 가능. 특히 **손목 fisheye 카메라로 손바닥 접촉면 occlusion 을 메우는** 설계는 우리 멀티캠 grounding(P2 D8) 의 데이터 측 정당화가 됩니다.
- **표현/토큰 측면(P2)** — 손당 $`21\times21`$ canonical hand-shaped grid + 오른손 미러링으로 양손을 공통 좌표계에 두는 방식은, 우리 per-finger tactile token(D11)의 **canonicalization 규약** 설계에 직접 입력이 됩니다. 단 우리 타깃은 fingertip(Sharpa, ~320×240/fingertip)이라 palm-grid 와 격자 의미가 달라 그대로 쓰지 않고 토폴로지 매핑이 필요.
- **구체 하이퍼/메트릭** — vision-to-touch 보조 과제를 우리 파이프라인에 둘 경우, 손실은 `λ_mse=1.0, λ_l1=0.5, λ_tv=0.01, contact-weight=3.0(threshold 0.1)` 을 시작점으로, 메트릭은 Contact IoU / Volumetric IoU 를 채택 검토. view-dropout `p=0.3` 은 우리 멀티캠 modality-dropout 의 출발값 참고.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 체크) 모달리티 불일치** — 본 논문 출력은 **손바닥 $`21\times21`$ pressure grid**, 우리 타깃은 **fingertip vision-based Deform Map(~320×240/fingertip)**. 격자 의미·해상도·부착 위치가 달라, 데이터/표현을 정책에 직접 주입하기 전에 "이 압력 표현이 우리 fingertip 촉각으로 매핑 가능한가"를 먼저 따져야 합니다(대개 불가 → 표현 참고로만).
- **장갑 → bare-hand / sim 도메인 갭** — 학습 데이터가 촉각 장갑 외형에 묶여 있고(저자 명시 bias), 우리는 시뮬레이션(Isaac) + 로봇 핸드 도메인이라 시각 분포가 완전히 다릅니다. vision→touch 추론기를 그대로 전이하면 OOD 로 무너질 가능성이 큽니다.
- **인지 ≠ 제어** — 본 논문은 오프라인 vision-to-touch **추정**이지 폐루프 제어가 아닙니다. 우리 스택에서 촉각은 System0(P3) 의 폐루프 안정화 입력으로 쓰이는데, 추정된 압력의 **지연·노이즈·시간 정확도(Temporal Acc 미개선)** 가 폐루프 반응속도 요구를 못 맞출 수 있습니다.
- **절대 force 부재** — 출력이 $`[0,1]`$ 정규화 압력이라 slip 억제/grasp 유지 reward(P3) 가 필요로 하는 **절대 힘 단위/캘리브레이션**이 없습니다. 정규화 압력을 reward 신호로 쓰면 스케일 불일치가 생깁니다.
- **색 유사성 환각** — Figure 12 의 저대비 false-positive 는 우리 로봇 핸드(단색 그리퍼/손가락) 환경에서 더 빈번할 수 있습니다 — 적용 전 depth/segmentation 보강 또는 temporal smoothing 의 필요를 가정해야 합니다.
- **벤치마크 신뢰구간 부재** — Table 2 의 개선폭(~2–6%)에 분산/신뢰구간 보고가 없어, 단일 run 수치일 가능성이 있습니다. 우리 의사결정에 인용하기 전 반복 run 분산을 확인해야 합니다.

---

## 💡 컨텍스트 제안

- **`catalogs/dataset.md` 추가 후보** — EgoTouch 를 👤 human-ego × tactile 신규 항목으로 등재(D25). 라이선스 미확인이므로 ❓ 플래그.
- **P0 §5 핀 교체 검토(쿼터 리밸런스)** — tactile/접촉 corpus 가 RH20T(로봇 F/T) 1개뿐인데, **인간 egocentric dense pressure** 축은 비어 있습니다. EgoTouch 공개·라이선스 확인 시 OpenTouch 와 묶어 "egocentric tactile" 슬롯 신설을 고려할 만합니다(append 아님, 8핀 cap 내 교체).
- 그 외 Decision/trigger 이동 제안: 없음.

> 💡 본 논문은 Design 비대상(dataset)이라 foundry 매핑 대상이 아닙니다. 가치는 `카탈로그` 라우팅(`dataset/human/EgoTouch`)으로 전달됩니다.
