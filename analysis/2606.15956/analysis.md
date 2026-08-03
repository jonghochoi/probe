# Paper Analysis — You Don't Need Strong Assumptions: Visual Representation Learning via Temporal Differences

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | You Don't Need Strong Assumptions: Visual Representation Learning via Temporal Differences |
| 저자 | Ninad Daithankar\*, Alexi Gladstone\*, Yann LeCun, Heng Ji (UIUC · NYU; \*equal contribution) |
| 링크 | [arXiv:2606.15956](https://arxiv.org/abs/2606.15956) · [GitHub](https://github.com/ninaddaithankar/TDV) · [Website](https://temporal-difference-vision.github.io) |
| 발행일 / 버전 | 2026-06-14 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-16 |
| 관련 Pillar | P2, P5 |
| 태그 | egocentric-data |

---

## 🧭 한 줄 요약 (TL;DR)

증강·마스킹·크롭 같은 강한 inductive bias 없이, "과거가 미래를 야기한다"는 인과(causality) 가정만으로 비디오에서 시각 표현을 학습하는 self-supervised paradigm **TDV(Temporal Difference in Vision)** 를 제안합니다. 프레임 인코더와 모션 인코더를 함께 학습해 **현재 프레임 표현 + 인코딩된 모션 = 다음 프레임 표현** 이 되도록 강제하며, 강한 가정 없이도 dense spatial task(segmentation·optical flow·stereo depth)에서 DINO/iBOT 에 필적하거나 일부 능가합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 현대 self-supervised 시각 표현 학습(DINO/iBOT 등)은 라벨은 버렸지만 여전히 augmentation·masking·cropping 같은 강한 inductive bias 에 의존합니다. 이런 가정 없이도 학습이 되는 표현 패러다임을 찾는 것이 목표입니다.
- **기존 접근의 한계** — 저자들은 "가정은 근사적으로만 맞는 믿음을 인코딩하므로 scale 이 커지면 학습 가능한 것을 제한하는 병목이 된다"고 봅니다. 실제로 데이터 규모가 커질수록 최적 inductive bias 강도가 감소함을 실험으로 확인합니다(Figure 3).
- **본 논문의 가설** — augmentation/masking 류 가정 대신 **인과(causality)** — 원인이 결과에 선행하며 가까운 미래는 과거로부터 예측 가능하다 — 라는, *근사적이 아니라 정확히 맞는* 도메인 무관 가정을 쓰면 collapse 없이 충분한 학습 신호를 얻을 수 있다.
- **왜 지금 중요한가** — "약한 가정이 scale 에서 이긴다"는 deep learning 의 큰 흐름(supervised → weakly-supervised → self-supervised)의 다음 단계로, 시각 표현 학습에서 남은 마지막 inductive bias 까지 제거하는 첫 시도라는 위치를 주장합니다.
- **왜 비디오인가** — 인과는 본질적으로 시간 축을 요구하므로, 정적 이미지 데이터가 아니라 연속 프레임이 있는 **비디오**에서 이미지 인코더를 학습해야 한다는 결론으로 이어집니다(이는 표현 학습의 관행과 다른 선택).

---

## 🧩 핵심 기여

- **TDV 패러다임 제안** — augmentation/masking/contrastive/raw-pixel reconstruction 없이, 인과 가정만으로 비디오에서 표현을 학습하는 첫 self-supervised 방법.
- **프레임-모션 공동 인코더 + 가산 잠재 합성(additive latent composition)** — 프레임 인코더 $`f_\theta`$ 와 모션 인코더 $`m_\phi`$ 를 함께 학습해 $`\hat z_{t+1}=z_t+\Delta z_t`$ 가 다음 프레임의 (teacher) 표현과 일치하도록 강제. 모션을 *버리는*(invariance) 대신 *명시적으로 모델링*.
- **collapse 방지를 위한 DINO 스타일 teacher-student + patch-level 확장** — EMA teacher 를 타깃으로 쓰고, DINO cross-entropy 를 [CLS] 뿐 아니라 patch token 에도 적용해 공간적으로 일관된 표현을 유도.
- **dense spatial task 경쟁력 입증** — 강한 가정 없이도 ViT-S/B 에서 optical flow·stereo depth 의 다수 지표에서 DINO/iBOT 를 능가하고 semantic segmentation 은 근소한 차로 필적.
- **"가정 강도 ↓ as data ↑" 실증** — masking 비율을 가정 강도의 연속 proxy 로 써, 데이터가 늘수록 최적 masking 비율이 감소함을 ImageNet subset 으로 보여 TDV 의 동기를 정당화.

---

## 🔑 기술 키워드

- **TDV (Temporal Difference in Vision)** — 강화학습의 Temporal Difference 학습을 시각 표현에 유추한 이름. "현재 상태 + 변화 = 다음 상태"를 잠재 공간에서 강제하는 비디오 self-supervised 표현 학습.
- **Inductive bias** — 모델에 미리 심어 둔 가정(증강 불변성, 마스킹, 크롭 등). 저자 주장의 핵심은 "scale 이 커질수록 이 가정들이 병목이 된다".
- **Causality assumption** — "원인이 결과에 선행하고 가까운 미래는 과거로 예측 가능"이라는, 도메인 무관하고 *정확히 맞는다*고 주장하는 약한 가정. TDV 의 유일한 가정.
- **Motion encoder** — 두 인접 프레임의 RGB 차분 $`\Delta x_t`$ 을 받아 잠재 공간의 변화 $`\Delta z_t`$ 로 매핑하는 인코더. 비디오 코덱의 모션 벡터를 잠재 공간으로 옮긴 학습형 아날로그.
- **Additive latent composition** — 다음 프레임 표현을 $`\hat z_{t+1}=z_t+\Delta z_t`$ 의 단순 덧셈으로 합성. 내용(프레임 인코더)과 변화(모션 인코더)를 깔끔히 분리.
- **Self-distillation / teacher-student (DINO)** — 학생을 천천히 따라가는 EMA teacher 가 예측 타깃을 공급. 같은 인코더로 타깃을 만들 때 생기는 collapse(모든 표현이 한 점으로 붕괴)를 막는 장치.
- **Representation collapse** — 인코더가 모든 입력을 동일 상수 표현으로 보내 손실은 낮지만 의미 없는 해로 수렴하는 실패 모드. TDV 가 가장 경계하는 대상.
- **Dense spatial task** — semantic segmentation, optical flow, stereo depth 처럼 patch 수준 공간·시간 대응을 요구하는 과제. 뇌의 dorsal stream(어디/어떻게)에 대응, semantic(ventral, 무엇)과 구분.
- **RGB difference $`\Delta x_t`$** — 인접 프레임 화소 차분. 배경은 거의 불변이라 본질적으로 low-rank 이며, 움직이는 영역만 비영(非零) 신호를 남김.

---

## 🔬 방법론

### 직관

TDV 의 출발점은 "표현 학습에서 가정을 줄일수록 scale 에서 더 멀리 간다"는 믿음입니다. DINO 같은 최신 기법도 결국 "증강한 두 view 는 같아야 한다", "마스킹해도 비슷해야 한다" 같은 *불변성* 가정을 깔고 있고, 이 가정들은 데이터가 커지면 오히려 학습을 제한하는 병목이 됩니다. 그렇다면 가정을 다 빼면 되느냐 하면, 그 순간 학습 신호가 사라져 표현이 붕괴(collapse)합니다. 그래서 저자들이 던지는 질문은 "collapse 를 막을 만큼은 되지만 가장 약한 가정은 무엇인가"입니다.

그 답으로 저자들은 *인과*를 택합니다 — 과거는 미래를 예측한다. 이 가정은 특정 도메인(이미지의 증강 종류)에 묶이지 않고, 근사가 아니라 *정확히* 맞다고 주장합니다(다음 프레임을 예측하라는 목적은 어떤 정보도 버리라고 강요하지 않으므로, 불변성 목적처럼 downstream 에 필요한 정보를 구조적으로 폐기하지 않음). 인과는 시간 축을 요구하므로 자연히 정적 이미지가 아니라 **비디오**에서 학습하게 됩니다.

구체적으로는 "현재 프레임을 인코딩한 표현에, 프레임 사이 변화를 인코딩한 모션을 더하면 다음 프레임의 표현이 된다"는 단순 원리를 강제합니다. 핵심 통찰은 인접 프레임의 화소 차분 $`\Delta x_t`$ 이 프레임 자체보다 **본질적으로 저차원(low-rank)** 이라는 점 — 배경은 거의 안 변하고 움직이는 부분만 신호를 남기므로, 모션 인코더가 외형 전체가 아니라 *변화*에만 집중하도록 압박합니다. 이는 키프레임 + 프레임 간 델타로 비디오를 표현하는 고전 코덱(MPEG)의 잠재 공간 학습형 버전으로 볼 수 있습니다.

collapse 는 같은 프레임 인코더가 타깃까지 만들기 때문에 생기는데(모두 상수로 보내면 손실 0), DINO 식 EMA teacher-student 와 prototype 분포에 대한 cross-entropy 로 이를 직접 처벌합니다.

### 아키텍처

![Figure 1 — TDV 프레임·모션 인코딩 직관](https://arxiv.org/html/2606.15956/fig/tdv_intuition.png)

> "Figure 1: TDV Frame and Motion Encoding Intuition. TDV learns to encode frames such that the current frame's representation, when added to a learned motion encoding, predicts the next frame's representation. Because video has high temporal consistency, the raw RGB pixel difference between frames is intrinsically lower rank than the frames themselves, shown here as the edge outlines of a dog and a frisbee. The motion encoder compresses these high-dimensional RGB differences into abstract motion-level features." (§1)
> (한글 해설 — 강아지·프리스비의 윤곽선만 남는 RGB 차분이 프레임 전체보다 저차원이라는, 모션 인코더가 *변화*에만 집중하게 되는 근거를 시각화합니다.)

![Figure 2 — TDV 아키텍처](https://arxiv.org/html/2606.15956/fig/tdv_full_architecture.png)

> "Figure 2: TDV Architecture. TDV predicts the next frame's representation by adding a learned motion vector to the current frame's representation. Left (student): the frame encoder embeds the current frame, while the motion encoder turns the raw pixel difference between frames into a latent motion shift, conditioned on the current frame via cross-attention. Their sum is the predicted representation of the next frame. Right (teacher): an EMA copy of the frame encoder embeds the true next frame to supply the target. Two losses act on the prediction: a mean-squared error on the representations enforces the causal next-frame constraint, and a DINO-style [15] cross-entropy on the projection heads prevents collapse. Stop-gradients block the teacher from receiving gradients." (§3.2)
> (한글 해설 — student(프레임+모션 인코더)와 EMA teacher(타깃 공급), 두 손실(MSE + DINO CE), stop-gradient 의 전체 데이터 흐름을 한 장으로 보여줍니다.)

입출력과 모듈 분해는 다음과 같습니다.

**(1) 표현 공간 학습 — 프레임 인코더.** 각 프레임 $`x_t`$ 를 token 임베딩 열로 매핑하는 프레임 인코더 $`f_\theta`$ (ViT) 를 둡니다.

$$z_{t}=f_{\theta}(x_{t})\in\mathbb{R}^{n\times D}$$

> "we first need a way to map the frames from RGB space into a meaningful representation space. We therefore learn a frame encoder $`f_{\theta}`$ that maps each frame $`x_{t}`$ to a sequence of token embeddings" (§3.2)
> (한글 해설 — $`n`$ 은 공간 patch 수 + [CLS] token 1개, $`D`$ 는 임베딩 차원입니다. 인과 원리가 이 임베딩 공간에서의 제약으로 번역됩니다.)

**(2) 표현 공간에서의 변화 인코딩 — 모션 인코더.** 화소 차분 $`\Delta x_t = x_{t+1}-x_t`$ 를 잠재 변화 $`\Delta z_t`$ 로 매핑하되, 같은 화소 변화도 맥락에 따라 의미가 다르므로 현재 프레임 임베딩 $`z_t`$ 로 **cross-attention conditioning** 합니다.

$$\Delta z_{t}=m_{\phi}(\Delta x_{t};\,z_{t})$$

> "Since the same pixel-level change can carry different semantic meanings depending on visual context, we condition the motion encoder on the current frame's embedding $`z_{t}`$ via cross-attention, grounding the motion prediction in the semantic state of the current frame" (§3.2)
> (한글 해설 — 모션 예측을 현재 장면의 의미 상태에 묶어, 동일한 픽셀 이동이 맥락에 맞는 잠재 변화로 해석되게 합니다. ablation 에서 cross-attention 의 [CLS] 포함이 성능에 유의하게 기여.)

**(3) 가산 잠재 합성.** 다음 프레임 표현 예측은 단순 덧셈으로 환원됩니다.

$$\hat{z}_{t+1}=z_{t}+\Delta z_{t}$$

> "This decomposition of $`\hat{z}_{t+1}`$ into $`z_{t}`$ and $`\Delta z_{t}`$ cleanly separates the goal into two objectives: the frame encoder is responsible for learning the content in a frame, and the motion encoder learns how that content evolves over time." (§3.2)
> (한글 해설 — 내용(프레임 인코더)과 변화(모션 인코더)의 책임을 깔끔히 분리하는 것이 이 덧셈 구조의 설계 의도입니다.)

**(4) collapse 방지 — teacher-student.** 타깃 $`z_{t+1}`$ 도 학습 중인 같은 인코더가 만들기에, 모두 상수로 collapse 하면 손실이 trivial 하게 0 이 됩니다. 이를 막기 위해 DINO 식으로 student(경사하강)와 teacher(student 의 EMA, gradient 없음)를 분리하고, teacher 가 타깃 $`z^{\text{teacher}}_{t+1}`$ 을 공급하며 prototype 분포에 cross-entropy 를 겁니다.

> "if all frames map to the same representation, the distributions become identical across frames and the cross-entropy loss increases, forcing the encoder to maintain discriminative representations." (§3.2)
> (한글 해설 — collapse 시 분포가 프레임 간 동일해져 CE 가 오히려 커지므로, 인코더가 변별력 있는 표현을 유지하도록 직접 처벌합니다. teacher 의 느린 EMA 가 student 와의 차이를 유지해 trivial 해를 막습니다.)

### 학습 목표 / 손실

**Temporal prediction loss.** 예측된 다음 프레임 임베딩과 teacher 타깃 사이의 MSE 로 인과 제약을 직접 감독합니다.

$$\mathcal{L}_{\text{mse}}=\left\|\hat{z}_{t+1}-\text{sg}(z^{\text{teacher}}_{t+1})\right\|_{2}^{2}$$

> "This is enforced via a mean-squared error between the predicted next-frame embedding $`\hat{z}_{t+1}=z_{t}+\Delta z_{t}`$ and the teacher-encoded target $`z^{\text{teacher}}_{t+1}`$" (§3.3)
> (한글 해설 — $`\text{sg}(\cdot)`$ 은 stop-gradient 로, 이 손실이 teacher 가 아니라 모션 인코더와 student 프레임 인코더만 갱신하게 합니다. ablation 상 MSE 손실 제거 시 학습이 붕괴.)

**Self-distillation loss.** collapse 를 막는 DINO 식 cross-entropy 를 student/teacher projection 분포 $`p_s, p_t`$ 사이에 걸되, 원판 DINO 와 달리 [CLS] 뿐 아니라 **patch token 전체**에 적용해 patch 수준 공간 일관성을 유도합니다.

$$\mathcal{L}_{\text{dino}}=-\sum_{k}p_{t}^{(k)}\log p_{s}^{(k)}$$

> "we apply this loss over both the [CLS] token and the patch tokens, encouraging spatially consistent representations at the patch level beyond what the original DINO formulation provides." (§3.3)
> (한글 해설 — $`k`$ 는 projection head 의 $`K`$ prototype 차원 인덱스. 실전에서 $`\tau_t=\tau_s=0.1`$, teacher 분포는 running-mean centering 으로 dimensional collapse 를 방지.)

**전체 목표.** 두 손실의 가중합입니다.

$$\mathcal{L}=\lambda_{\text{mse}}\,\mathcal{L}_{\text{mse}}+\lambda_{\text{dino}}\,\mathcal{L}_{\text{dino}}$$

> (한글 해설 — 본문 Table C.2 기준 $`\lambda_{\text{mse}}=\lambda_{\text{dino}}=1.5`$. Algorithm 1 에 따르면 MSE 와 DINO CE 모두 *all tokens* 에 대해 계산됩니다.)

### 학습 셋업

- **사전학습 데이터** — Something-Something V2 (SSv2): "approximately 220,000 short egocentric video clips depicting hand-object interactions" (§C.2). DINO/iBOT 도 동일 데이터에 각자의 증강을 튜닝해 공정 비교.
- **아키텍처** — ViT-S / ViT-B. TDV patch size 14 (DINO/iBOT 16). projection head dim 32768 (DINO 1024, iBOT 8192).
- **옵티마이저·스케줄** — AdamW, batch size 256, cosine LR. TDV LR 1e-4(DINO/iBOT 5e-4), warmup 0.5 epoch(DINO/iBOT 10), weight decay 0.01, EMA momentum $`\tau`$=0.99, $`\tau_s=\tau_t`$=0.1. 약 200,000 step(20 epoch), 최종 체크포인트 보고.
- **시간 샘플링** — 입력 224×224, clip 당 16 프레임, time between frames 0.25(고정 stride), RGB difference clipping 없음, center crop only, horizontal flip·color jitter·masking **모두 없음**(Table C.1/C.3 — TDV 만 temporal frame sampling 사용, 나머지 augmentation 칸은 전부 ×).
- **하드웨어** — NCSA Delta / DeltaAI (§7, §D.4).

---

## 📊 실험 설정과 결과

평가는 의도적으로 **dense spatial task**(dorsal-stream, 어디/어떻게)에 집중합니다. 저자들은 linear probe·KNN·action recognition 같은 semantic(ventral, 무엇) 지표가 공간·시간 표현 품질을 제대로 못 잰다고 보고, segmentation·optical flow·stereo depth 를 주 평가로 삼습니다. 모든 모델은 SSv2 사전학습 후 frozen backbone(또는 flow/depth 는 end-to-end fine-tune)으로 비교합니다.

**Semantic Segmentation (UperNet, frozen backbone; mIoU/mAcc ↑).**

| Method | Arch | ADE20K mIoU | ADE20K mAcc | Cityscapes mIoU | Cityscapes mAcc |
|---|---|---|---|---|---|
| iBOT | ViT-S | 10.60 | 14.53 | 39.34 | 45.36 |
| DINO | ViT-S | 10.71 | 14.64 | 39.85 | 45.68 |
| **TDV** | ViT-S | 10.54 | 14.48 | 37.54 | 43.09 |
| iBOT | ViT-B | 9.94 | 13.65 | 38.94 | 44.31 |
| DINO | ViT-B | 10.48 | 11.14 | 39.97 | 43.09 |
| **TDV** | ViT-B | 9.57 | 10.70 | 36.21 | 42.59 |

> "On semantic segmentation, TDV achieves results comparable to DINO and iBOT, trailing behind by a small margin on both mIoU … and mAcc … as shown in Table 2." (§4.2, Table 2)
> (한글 해설 — ADE20K 는 거의 동률, Cityscapes 는 ~2 mIoU 뒤짐. 저자는 local crop 부재로 인한 semantic context 부족을 잔여 격차의 원인으로 추정.)

**Optical Flow & Stereo Depth (fine-tune; EPE·Err 모두 ↓).**

| Method | Arch | Sintel EPE(clean) | Sintel EPE(final) | SceneFlow Avg Err | bad@0.5px | bad@1px |
|---|---|---|---|---|---|---|
| iBOT | ViT-S | 11.31 | 11.27 | 3.50 | 65.51 | 44.91 |
| DINO | ViT-S | 13.03 | 12.92 | 3.64 | 63.25 | 45.30 |
| **TDV** | ViT-S | **9.84** | **10.75** | 4.25 | **56.89** | **39.70** |
| iBOT | ViT-B | 11.66 | 11.82 | 3.75 | 62.49 | 44.18 |
| DINO | ViT-B | 11.63 | 11.28 | 3.91 | 62.97 | 44.64 |
| **TDV** | ViT-B | **10.97** | 11.85 | 3.98 | **54.62** | **37.33** |

> "On optical flow, TDV consistently outperforms both DINO and iBOT on EPE … On stereo depth, TDV achieves lower 'bad' pixel rates at both the 0.5px and 1px thresholds across both architectures … The slightly higher average disparity error suggests that while TDV makes fewer large mistakes, it can still struggle to recover precise depth in ambiguous regions where semantic context would otherwise help." (§4.2, Table 3)
> (한글 해설 — optical flow EPE 와 stereo "bad pixel" 비율에서 TDV 가 일관 우위. 단 stereo 평균 disparity 오차는 약간 높아 — 큰 실수는 적지만 모호 영역의 정밀 depth 회복은 약함. TDV 가 명시적으로 프레임 간 표현 변화를 예측해 국소 모션 구조를 보존한 결과로 해석.)

**Ablations (SSv2 사전학습; ImageNet KNN Top-5 ↑ + collapse 여부).**

| Setup | KNN(Top-5) | Avoids Collapse |
|---|---|---|
| Full TDV recipe | **17.05** | ✓ |
| No Temperature | 15.85 | ✓ |
| No Centering | 11.15 | ✓ |
| No [CLS] in Cross Attention | 10.78 | ✓ |
| No Centering or Sharpening | 10.68 | ✓ |
| No DINO Loss on [CLS] | 10.66 | ✓ |
| RoPE instead of Positional Enc. | 10.25 | ✓ |
| **No Motion Encoder** | 1.87 | ✗ |
| **No MSE Loss** | 1.58 | ✗ |

> "removing the motion encoder or MSE loss causes training collapse, identifying them as critical components." (§4.3, Table 4)
> (한글 해설 — per-ablation 읽기: ① 모션 인코더·MSE 제거 → collapse(가장 치명적). 특히 모션 인코더를 빼고 DINO loss 만으로 연속 프레임 불변성만 걸면 학습 자체가 안 됨 → "변화를 명시적으로 모델링"이 필수임을 분리 입증. ② centering 제거(−5.9)가 temperature sharpening 제거(−1.2)보다 훨씬 큰 손해 → centering 이 분포가 한 mode 로 쏠리는 미묘한 collapse 를 막음. ③ cross-attention 의 [CLS] 포함·[CLS] DINO loss 가 모션 예측을 전역 장면에 grounding 해 유의미 기여. ④ 절대 위치 인코딩이 RoPE 보다 일관 우위.)

**가정 강도 vs 데이터 규모 (동기 실험; Figure 3).**

> "With just $`0.1\%`$ of ImageNet, the best performing masking ratio is $`50\%`$ … However, as the amount of data increases, $`30\%`$ masking eventually outperforms $`50\%`$ masking … as data increases, the optimal amount of assumptions made, represented here as masking ratio, decreases." (§4.1)
> (한글 해설 — masking 비율을 가정 강도의 연속 proxy 로 사용. 데이터 0.1%→100% 로 갈수록 최적 masking 이 50%→30% 로 약해짐 → "약한 가정이 scale 에서 이긴다"는 TDV 의 핵심 동기를 실증.)

**semantic 한계 (Table B.1; ImageNet KNN·linear, SSv2 action recog Top-5 ↑).** TDV 는 semantic 지표에서 DINO/iBOT 에 크게 뒤집니다 — ViT-B 에서 ImageNet KNN 17.05 vs DINO 40.89 / iBOT 38.75. 저자는 invariance 학습용 inductive bias(local/global crop) 부재 때문이며 *설계상 예상된* 결과라고 명시합니다.

**Table 1 (DINO bias 제거).** DINO 의 증강을 점진 제거하면 KNN 이 24.63→0.84 로 떨어지고 결국 collapse(- random crop on both G) 하는 반면, TDV 는 그런 증강 없이도 collapse 를 피함(8.79). "naive 하게 bias 만 빼면 신호가 없어 붕괴한다"는 동기를 직접 보강.

---

## ⚖️ 한계

- **semantic 표현 약함 (저자 명시).** invariance 용 증강(local/global crop)이 없어 ImageNet KNN/linear·action recognition 이 DINO/iBOT 대비 절반 이하. dorsal(공간/모션)은 강하지만 ventral(의미)은 약한, 표현의 *편향된 강점*이 분명합니다. 의미 카테고리 판별이 필요한 downstream 에는 그대로 쓰기 어렵습니다.
- **SOTA 미달 (저자 명시).** dense spatial task 에서 "필적"하지만 전 영역 SOTA 는 아님. 저자도 "강한 가정 없는 표현 학습의 *첫 시도*로서 예상된" 격차라며 후속 recipe 개선에 기댑니다 — 즉 현재로선 검증된 우위가 아니라 *방향성*의 입증입니다.
- **scale 이 동기와 어긋남 (저자 명시·핵심 긴장).** 논문의 대전제는 "약한 가정이 scale 에서 이긴다"인데, 정작 SSv2 보다 큰 비디오로 키웠을 때 성능이 *개선되지 않았습니다*(§6, §B.1). 저자는 고품질 대규모 오픈 비디오 부재 + SSv2 에 튜닝된 하이퍼파라미터 탓으로 돌리지만, 이는 *주장된 가장 큰 장점이 아직 실증되지 않았다*는 의미라 논문 논지의 약한 고리입니다.
- **인접 prior(MAE/DINOv2) 위에서 frame 인코더를 풀면 표현이 악화 (추론·§B.1).** 기존 사전학습 인코더를 frame 인코더로 초기화해 unfreeze 한 채 계속 학습하면 표현이 *나빠집니다*. frozen 채 모션 인코더만 학습하면 임베딩 델타를 (MAE 약 90%, DINOv2 약 60%) 회복 — TDV 목적이 *고정* backbone 위 모션 학습으로는 양립하지만, 표현 *개선* 수단으로는 아직 아님.
- **모션 인코더 용량 병목 (추론·§B.1).** 모션 인코더를 줄이면 KNN 이 단조 감소 — 학습 신호가 모션 인코더 용량에 묶여 있어, frame 인코더에 닿는 신호의 병목이 됩니다. 효율(경량 모션 인코더로 비디오 코덱처럼 쓰겠다는 §5 비전)과 표현 품질이 상충.
- **"정확히 맞는 가정"이라는 철학적 주장의 검증 불가성 (추론).** "인과는 근사가 아니라 정확히 맞다"는 핵심 논거는 학습 *목적*의 성질에 대한 주장(불변성을 강요하지 않음)으로 좁게 정의되어 있어, 실험적으로 직접 반증하기 어렵습니다. 강점이자 약점.

---

## ♻️ 재현성

- **코드** — 공개. [github.com/ninaddaithankar/TDV](https://github.com/ninaddaithankar/TDV), 프로젝트 페이지 [temporal-difference-vision.github.io](https://temporal-difference-vision.github.io).
- **데이터** — 공개 표준 벤치마크만 사용: SSv2(사전학습), ImageNet-1k(KNN/linear/동기 실험), ADE20K·Cityscapes(seg), MPI-Sintel·FlyingChairs·FlyingThings3D(flow), SceneFlow(stereo).
- **하이퍼파라미터** — Appendix C(Table C.2/C.3)에 모델·옵티마이저·데이터/시간 샘플링 값 전부 명시. Algorithm 1 에 단일 step 의사코드 제공.
- **평가 프로토콜** — V-JEPA(action recog frozen probe), UperNet/MMSegmentation(seg), CroCo+Midway Networks+DPT(flow) 등 표준 프로토콜을 baseline 과 동일 설정으로 사용.
- **하드웨어** — NCSA Delta / DeltaAI(§D.4 compute resources 명시).
- License: CC BY 4.0.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P2(Structured Multimodal Observation Fusion) — D9(action/dynamics-aware vision encoder) 가 일차 접점.** TDV 는 본질적으로 *비디오에서 동역학(모션)을 명시적으로 분리해 학습한 vision encoder* 입니다. D9 의 v1 은 "generic SigLIP/ImageNet stem 보다 DynaFLIP 류 action/dynamics-aware 인코더를 선호". TDV 는 motion 을 잠재 변화 $`\Delta z_t`$ 로 모델링하므로 D9 가 노리는 "scene 이 (행동/시간에 따라) 어떻게 변하는지를 이미 인코딩한 표현"의 *자기지도 사전학습 레시피* 후보입니다. optical flow·stereo 에서 DINO/iBOT 를 이긴 것은 P2 가 중시하는 dorsal-stream 공간·시간 대응 품질을 직접 증거합니다.
- **P5(World Model) — D30(prediction space=latent) / D28(latent dynamics prior) 와 구조적으로 유사하나 경계선.** $`\hat z_{t+1}=z_t+\Delta z_t`$ 는 *잠재 공간 forward prediction* 으로, JEPA 계열(저자 LeCun)의 latent world model 과 같은 가족입니다. 다만 **action-conditioned 가 아니라 passive 비디오의 implicit motion** 만 쓰므로, P5 의 핵심 narrowing(action-conditioned, egocentric, hand-object)과 §4 anti-topic("action-free … no action conditioning")에 *부분적으로* 걸립니다. 즉 방법론 base 로서의 가치는 크지만 P5 의 pinned 자격(action 조건화)에는 미달.
- **Identity 긴장/지지** — Identity 의 P2 축("encoder action-aware")을 지지. 반면 dexterity·VLA·hand 와의 직접 연결은 없고(로봇 정책·액션 출력 없음), SSv2 가 "hand-object interaction egocentric" 라는 점만 P0/P5 의 egocentric 우선순위와 약하게 맞닿습니다.
- **경쟁자 함의** — VLA 정책 경쟁자는 아니며, P2 의 *관측 인코더 선택지*(DynaFLIP·eVGGT)와 같은 층위의 대안 표현 학습 레시피로 분류됩니다.

---

## ✨ 핀 논문 대비 델타

- **vs DynaFLIP (P2 D9 pin, arXiv:2605.30350).** DynaFLIP 은 image-language-3D flow 의 *tri-modal* 동역학 인식을 (언어·flow 라벨 등) 추가 신호로 학습합니다. TDV 의 델타는 **어떤 modal 라벨·증강·언어도 없이** 인접 프레임 RGB 차분만으로 동역학을 분리한다는 점 — 더 약한 가정, 더 적은 supervision. 다만 manipulation/3D-flow 에 직접 맞춰진 DynaFLIP 과 달리 TDV 는 일반 비디오 표현이라 contact/manipulation 특화는 없음.
- **vs VLA-JEPA (P5 D30 pin, arXiv:2602.10098) / ThinkJEPA (arXiv:2603.22281).** 둘 다 JEPA 잠재 예측 world model 이라는 같은 철학(LeCun 계보)을 공유합니다. TDV 의 차별점은 (a) 예측을 *덧셈 합성* $`z_t+\Delta z_t`$ 으로 명시 분해해 "내용 vs 변화"를 구조적으로 분리, (b) 목표가 *정책 prior* 가 아니라 *순수 시각 인코더 표현 품질*, (c) action-conditioning 부재. 즉 VLA-JEPA 가 "robot action head 로 가는 latent prior"라면 TDV 는 "action 없는 latent 표현 자체"입니다.
- **요지** — TDV 의 진짜 새로움은 *supervision/inductive bias 최소화* 라는 축이며, 우리 핀 논문들은 대부분 이 축에서 TDV 보다 강한 가정을 깔고 있습니다.

---

## ⚙️ 의사결정 함의

- **P2 D9 의 후보군에 "TDV-style temporal-difference 사전학습"을 추가.** 관측 인코더를 generic stem 대신 동역학 인식 인코더로 갈 때, DynaFLIP(라벨 필요)·eVGGT(geometry distill) 외에 *라벨 없는 비디오 자기지도* 옵션으로 TDV 를 비교군에 넣을 수 있습니다. 구체 config: 우리 egocentric hand-object 비디오에서 `motion_encoder` + `additive composition` + `λ_mse=λ_dino=1.5`, `τ_s=τ_t=0.1`, patch-level DINO loss 로 인코더를 사전학습 → 그 backbone 을 P2 fusion 에 frozen feed.
- **단, semantic 약점이 결정적 제약.** 우리 VLA 는 언어 조건·객체 의미 grounding 이 필요하므로, TDV 표현을 *단독* vision backbone 으로 쓰면 ventral(의미) 결손이 risk. 함의는 "TDV 를 메인 backbone 으로 교체"가 아니라 **보조 dynamics-aware 분기 / 모션 특징 공급원**으로 한정.
- **§B.1 의 "frozen backbone + motion encoder only" 결과가 가장 실용적 레버.** 기존 사전학습 인코더(DINOv2/우리 VLM stem)를 *frozen* 으로 두고 TDV 모션 인코더만 얹으면 임베딩 델타를 60–90% 회복 → 우리 backbone 을 건드리지 않고 *모션/시간 예측 보조 신호*를 붙이는 P5-auxiliary(D28) 형태가 가장 저비용 진입점입니다.
- **바뀌는 구체값** — 관측 인코더 선택 시 평가 메트릭에 optical flow EPE / stereo bad-pixel 같은 dorsal-stream 지표를 추가(현재 semantic 위주 평가의 사각지대 보강).

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 체크) semantic grounding 결손.** 우리 stack 은 언어·객체 의미 조건이 필수인데 TDV 표현은 KNN/linear 가 절반 이하. → 가장 싼 sanity check: 우리 데이터에서 frozen TDV 특징으로 객체/언어 retrieval 또는 linear probe 를 돌려 의미 분별력이 임계 이하면 메인 backbone 후보에서 즉시 제외.
- **scale 미실증.** 논문 스스로 SSv2 보다 큰 비디오에서 개선이 안 됐다고 보고. 우리 egocentric 코퍼스는 SSv2 보다 클 가능성이 높아, "데이터 늘리면 좋아진다"는 전제가 우리 환경에서 *역전*될 수 있음. → 소규모/대규모 두 subset 에서 같은 recipe 의 KNN 추세를 먼저 비교.
- **action-conditioning 부재 → P5 로 그대로 못 옮김.** TDV 모션은 *passive* 비디오의 implicit motion 이라 로봇 action 으로 조건화돼 있지 않음. 우리 D31(action-conditioned) 요구와 충돌 → world-model 용도로 쓰려면 action 을 모션 인코더 conditioning 에 주입하는 비자명한 개조가 선행돼야 하며, 그 전엔 P5 pin 후보 아님.
- **stride(time between frames) 민감도.** 본문 §C.3 가 stride 가 너무 작으면 차분 ≈ 0, 너무 크면 incoherent jump 라고 경고. 우리 손-물체 접촉의 빠른 미세 모션과 SSv2 의 0.25s stride 가 안 맞을 수 있음 → 우리 데이터의 프레임레이트·모션 스케일에 맞춘 stride 재튜닝이 collapse/무신호를 가르는 지점.
- **모션 인코더 용량 ↔ 효율 상충.** 표현 품질이 모션 인코더 크기에 단조 의존 → "경량 모션 인코더로 효율적 비디오 인코딩"이라는 매력 포인트를 취하면 표현 품질이 떨어짐. 우리 추론 예산 안에서 두 목표가 양립하는지 먼저 측정.
- **collapse 취약성.** 강한 가정을 다 뺀 만큼 centering·EMA·MSE 중 하나만 어긋나도 collapse(Table 4). 우리 데이터/하이퍼로 옮기면 재튜닝 비용이 크고, online KNN collapse 모니터링이 필수.

---

## 💡 컨텍스트 제안

- **P2 §5 methodology base(non-pinned) 후보로 TDV 등재 검토.** D9(action/dynamics-aware encoder)의 *라벨 없는 자기지도* 대안으로, DynaFLIP/eVGGT 와 다른 supervision 축을 대표. pin 승격까지는 아니어도 비교군 가치 있음. (핀 교체는 사람 판단 — 제안만.)
- **P5 §5 methodology base 후보(보류 권고).** JEPA 잠재 예측 계열이지만 action-free 라 §4 anti-topic 에 걸리므로 *pin 부적격*. ThinkJEPA/JEPA-VLA 와 같은 줄의 "방법론 base, action 조건화 시 재검토" 메모로만.
- context/ 파일은 수정하지 않았습니다 — 위는 제안일 뿐입니다.

> 💡 base 매핑은 `/implement-design analysis/2606.15956/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
