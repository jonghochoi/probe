# Paper Analysis — G$`^3`$VLA: Geometric inductive bias for Vision-Language-Action Models

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | G$`^3`$VLA: Geometric inductive bias for Vision-Language-Action Models |
| 저자 | Yue Peng, Yongzhe Zhao, Artur Habuda, Khuyen Pham, Yanheng Zhu, Tran Nguyen Le, Fares Abu-Dakka, Li Guo |
| 링크 | [arXiv:2606.24472](https://arxiv.org/abs/2606.24472) · [Website](https://sites.google.com/view/g3vla) |
| 발행일 / 버전 | 2026-06-23 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-28 |
| 관련 Pillar | P2, P4, P1 |
| 태그 | vla-arch, sim2real |

---

## 🧭 한 줄 요약 (TL;DR)

사전학습된 VLA 의 backbone·action space·imitation 목적함수를 일절 건드리지 않고, **calibrated 카메라 기하(intrinsic ray embedding + PRoPE 투영 위치 인코딩 + 양방향 cross-view fusion)** 를 visual-token 스트림에 주입하는 경량 모듈 G$`^3`$VLA 를 제안합니다. 기하 supervision 은 GT point map 또는 confidence-gated $`\pi^{3}`$X teacher 증류로 주며, $`\pi_{0}`$ 위에서 LIBERO·RoboCasa24·RoboTwin2.0·실로봇 전반에 일관된 향상(특히 공간·물체 민감 task)을 보입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — VLA 의 visual token 은 사전학습 VLM 의 의미 지식은 물려받지만, 좌표는 여전히 2D 이미지 픽셀에 묶여 있어 로봇 카메라의 **calibrated 기하(intrinsics·extrinsics)** 를 활용하지 못합니다. 특히 multi-camera 셋업에서 뷰들이 알려진 K·T 로 기하적으로 결합돼 있음에도 독립 이미지로 처리됩니다.
- **기존 접근의 한계** — PerAct/RVT/Act3D 처럼 명시적 3D(voxel·point cloud)를 쓰는 방법은 공간 정밀도는 높지만 사전학습 VLM 의미를 못 살리고 task-specific 아키텍처가 됩니다. SpatialVLA/3D-VLA 같은 bridging 은 3D 센서 입력·대규모 공간 사전학습·action 표현 변경을 요구합니다.
- **본 논문의 가설** — calibrated 카메라 기하를, backbone·action space·imitation 목적함수를 바꾸지 않고 **visual-token 경로의 경량 inductive bias** 로만 노출해도 공간 일반화를 끌어올릴 수 있다.
- **왜 지금 중요한가** — $`\pi^{3}`$ ·VGGT·DUSt3R 같은 feed-forward visual-geometry teacher 가 등장해, depth 센서·수동 3D annotation 없이도 dense point map 을 공급할 수 있게 되었습니다. 이로써 기하 supervision 을 사실상 공짜로 distill 할 수 있는 환경이 마련됐습니다.

---

## 🧩 핵심 기여

- **VLA 의 기하 갭 식별** — 사전학습 VLA 의 2D-grounded visual token 과, 정밀 manipulation 에 필요한 calibrated 공간 구조 사이의 불일치를 명시적으로 짚습니다.
- **G$`^3`$VLA 모듈** — ray embedding + PRoPE + cross-view fusion 으로 calibrated 카메라 기하를 사전학습 VLA 의 token 경로에 주입하되, **action space·imitation 목적함수는 불변** 으로 두는 backbone-preserving 경로.
- **$`\pi^{3}`$X 기하 증류** — confidence-gated dense point map 을 teacher 로 쓰는 2-stage 절차로, 수동 3D annotation 없이 기하 모듈을 supervise.
- **다중 아키텍처 검증** — $`\pi_{0}`$ / $`\pi_{0.5}`$ 에서 일관된 향상 + GR00T 1.5(two-tower)에서의 혼합 결과로, "geometry-aware token 이 action 생성 경로에 얼마나 직접 닿는가" 가 효과를 좌우한다는 분석을 제시.

---

## 🔑 기술 키워드

- **VLA (Vision-Language-Action model)** — 이미지·언어·action 을 한 시퀀스로 모델링하는 generalist manipulation policy. 본 논문의 개조 대상(base = $`\pi_{0}`$).
- **Geometric inductive bias** — 카메라 calibration 이라는 사전 지식을 모델 구조에 미리 새겨 넣어, action supervision 만으로 암묵 학습되던 기하를 명시적으로 제공하는 것.
- **Intrinsic-conditioned ray embedding** — 각 패치 토큰에 $`K^{-1}`$ 로 역투영한 시선 방향(viewing ray)을 태깅하는 임베딩. "이 픽셀이 실제로 어느 방향을 보는가" 를 토큰에 새깁니다.
- **PRoPE (Projective Positional Encoding)** — 카메라 모델(K·T)에서 유도한 투영 변환을 attention 의 query/key/value 에 가하는 위치 인코딩. 외형 유사도가 아니라 기하 관계로 cross-view attention 을 정렬합니다.
- **Bidirectional cross-view fusion** — frame attention(뷰 내부) → cross-view attention(뷰 간 양방향)의 2단계 융합. 카메라 스트림 간 기하 컨텍스트를 교환합니다.
- **Point map** — 픽셀마다 (ray 좌표, log-$`z`$ depth)를 담은 dense 3D 구조 표현. 본 논문에서 기하 증류의 supervision target.
- **$`\pi^{3}`$X (geometry teacher)** — RGB 만으로 dense point map 을 예측하는 feed-forward visual-geometry 모델. depth 센서 없이 confidence 까지 내주는 offline teacher.
- **Confidence-gated distillation** — teacher 의 confidence logit 을 hard threshold($`\tau=0.1`$)로 게이트해, 신뢰 가능한 픽셀만 증류 loss 에 기여시키는 방식.
- **Two-stage training curriculum** — Stage 1(기하 모듈만 학습, distillation 우세) → Stage 2(전체 unfreeze, action loss 우세)의 단계적 학습.
- **Auxiliary point head** — 융합 토큰에서 dense point map 을 디코딩하는 학습 전용 head. 추론 시 폐기되어 배포 비용이 없습니다.

---

## 🔬 방법론

### 직관

G$`^3`$VLA 의 핵심 발상은 "VLA 를 다시 학습시키지 말고, 카메라가 이미 알고 있는 기하를 그냥 토큰에 끼워 넣자" 입니다. 보통 VLA 는 여러 카메라 이미지를 각각 독립적으로 인코딩해 토큰을 만들고, 카메라의 intrinsics(K)·extrinsics(T)는 버립니다. 그래서 "왼쪽 카메라의 이 픽셀과 오른쪽 카메라의 저 픽셀이 같은 3D 점을 본다" 같은 관계를 action supervision 만으로 힘겹게 암묵 학습해야 합니다.

이 논문은 그 관계를 명시적으로 토큰에 새깁니다. 첫째, 각 패치 토큰에 $`K^{-1}`$ 로 계산한 시선 방향(ray)을 더해 "이 토큰이 실제 공간에서 어느 방향을 보는지" 를 알려 줍니다. 둘째, PRoPE 라는 투영 위치 인코딩으로 cross-view attention 이 외형이 아니라 카메라 기하를 기준으로 뷰들을 정렬하게 합니다. 셋째, 이 융합을 backbone 인코더 출력과 action model 사이의 얇은 층에서만 수행해 사전학습 가중치를 보존합니다.

문제는 이 새 기하 모듈이 처음엔 무작위 초기화 상태라 action loss 의 희박한 신호만으로는 학습이 느리다는 점입니다. 그래서 $`\pi^{3}`$X 라는 외부 기하 teacher 가 RGB 에서 dense point map 을 뽑아 주고, 이를 보조 head 가 흉내 내도록 dense 한 증류 신호를 줍니다. 학습은 2단계로, 먼저 기하 모듈만 teacher 에 정렬시킨 뒤(Stage 1), 전체를 풀어 action loss 가 주도하게 합니다(Stage 2). 추론 시에는 teacher 도 보조 head 도 호출되지 않아, 배포 모델은 RGB·proprio·언어·calibration 만 받는 원래 VLA 그대로입니다.

### 아키텍처

policy 는 control step 마다 언어 instruction $`l`$, proprioceptive state $`s_{t}`$, 그리고 $`V`$ 개 뷰의 RGB $`\{I_{t}^{v}\}_{v=1}^{V}`$ 와 각 뷰의 intrinsic $`K^{v}`$ · extrinsic $`T^{v}`$ 를 받아 action chunk 를 예측합니다.

$$\pi_{\theta}(a_{t:t+H-1}\mid l,\,s_{t},\,\{I_{t}^{v},K^{v},T^{v}\}_{v=1}^{V}).$$

> "Standard VLAs discard $`K^{v},T^{v}`$ and process each view independently. G3VLA preserves this calibration by inserting a Camera-Aware Geometric Module into the visual-token stream before action prediction (Fig. 1), leaving the pretrained backbone, action space, and imitation objective unchanged." (§3)
> (표준 VLA 가 버리는 calibration 을, G$`^3`$VLA 는 action 예측 직전의 visual-token 스트림에 Camera-Aware Geometric Module 을 끼워 보존합니다. backbone·action space·imitation 목적함수는 그대로 둡니다.)

![Figure 1 — G3VLA 개요](https://arxiv.org/html/2606.24472/x1.png)

> "Figure 1: G3VLA overview. (A) Geometric inductive bias is injected into VLA visual tokens via intrinsic-conditioned ray embeddings ( $`K^{-1}`$ ) and bidirectional cross-view fusion with PRoPE, leaving the pretrained backbone and action objective unchanged. (B) Stage 1 distills dense point maps from $`\pi^{3}`$ X to pretrain the geometry modules; Stage 2 fine-tunes the full policy under action and distillation losses jointly." (§1)
> (이 그림이 (A) 토큰 경로에 기하를 주입하는 구조와 (B) 2-stage 학습이라는 논문의 두 축을 한 장에 시각화합니다.)

사전학습 vision encoder 는 뷰당 $`P`$ 개 패치 토큰 $`z_{p}^{v}\in\mathbb{R}^{d}`$ 를 만드는데, 이는 2D 외형·위치는 담지만 물리적 시선 방향이나 뷰 간 기하 관계는 담지 못합니다. 모듈 $`F_{\psi}`$ 가 calibration-조건부 변환으로 그 구조를 더합니다.

$$h_{1:P}^{1:V}=F_{\psi}\!\left(z_{1:P}^{1:V},\;\{K^{v},T^{v}\}_{v=1}^{V}\right).$$

$`F_{\psi}`$ 는 세 부품으로 구성됩니다.

**(1) Intrinsic-conditioned ray embedding.** 같은 픽셀 $`(x,y)`$ 도 intrinsic 이 다르면 다른 물리적 시선 방향에 대응합니다 — 2D 위치 임베딩이 못 푸는 모호성입니다. homogeneous 픽셀 $`u=(x,y,1)^{\top}`$ 의 정규화 ray 는 $`\tilde{r}^{\,v}(u)=(K^{v})^{-1}u`$ 이고, pinhole 모델이 세 번째 좌표를 고정하므로 앞 두 성분이 metric depth 가정 없이 image-plane ray 좌표를 정의합니다.

$$R^{v}(x,y)=\bigl[\tilde{r}^{\,v}(x,y,1)\bigr]_{1:2}\in\mathbb{R}^{2}.$$

> "A learnable embedding $`G_{\phi}`$ projects this ray map to the patch grid and adds it to the encoder output before cross-view fusion, ensuring all downstream attention operates on intrinsic-aware tokens" (§3.1)
> (학습 가능한 $`G_{\phi}`$ 가 ray map 을 패치 그리드로 투영해 인코더 출력에 더합니다. 이후 모든 attention 이 intrinsic-aware 토큰 위에서 동작하게 만드는 장치입니다.)

$$z_{0,p}^{v}=z_{p}^{v}+G_{\phi}(R^{v})_{p}.$$

구현상 $`G_{\phi}`$ 는 **zero-init projection** 이라 finetuning 시작 시 더해지는 항이 0 이 되어 사전학습 거동을 보존하고, ray 신호는 ViT 내부가 아니라 인코더 뒤·LLM 앞에 들어가 ViT 특징을 건드리지 않습니다(Appendix A).

**(2) PRoPE.** ray embedding 은 카메라별 국소 시선 방향만 담고 뷰 간 관계는 못 담습니다. PRoPE 는 per-view intrinsic $`K^{v}`$, camera-to-world $`T^{v}`$, 패치 위치에서 query/key/value 용 고정 투영 변환을 유도해, cross-view attention 이 외형 유사도가 아니라 카메라-모델 기반 투영 관계에 접근하게 합니다.

**(3) Bidirectional cross-view fusion.** 두 단계로 진행됩니다. **Frame Attention** 은 각 카메라 스트림 내부에서만 토큰을 처리해 뷰-국소 구조를 보존하고, **Cross-View Attention** 은 뷰·패치 차원을 flatten 해 모든 유효 토큰이 PRoPE 를 위치 신호로 양방향 attend 하게 합니다.

$$H=\mathrm{Fusion}_{\psi}\!\left(Z;\;\{K^{v},T^{v}\}_{v=1}^{V}\right),$$

여기서 $`Z`$ 는 ray-augmented per-view 토큰을 모은 것이고, $`H`$ 는 사전학습 VLA 가 기대하는 동일한 token 인터페이스로 action model 에 넘어가는 융합 시퀀스입니다. padding 된 무효 뷰는 frame·cross-view attention 전반에서 마스킹됩니다.

### 학습 목표 / 손실

기하 모듈은 scratch 초기화라 action loss 의 희박한 task-level gradient 만 받습니다. 그래서 dense 보조 기하 증류 목적과 2-stage 커리큘럼을 도입합니다.

**보조 point head.** 융합 토큰(VLA projection 직전)에 붙는 head 가 패치 토큰을 $`H_{p}\!\times\!W_{p}`$ 그리드로 reshape 한 뒤 경량 transformer + conv upsampler 로 디코딩해, 픽셀당 ray 좌표 $`\hat{q}_{u}^{v}\!\in\!\mathbb{R}^{2}`$ 와 log-$`z`$ depth $`\hat{d}_{u}^{v}\!\in\!\mathbb{R}`$ 를 예측합니다. 이 head 는 추론 시 폐기됩니다.

target 은 두 출처 중 하나입니다. 시뮬레이터처럼 GT depth 가 있으면 validity mask $`m_{u}^{v}=1`$ 로 전 픽셀을 쓰고, 없으면 $`\pi^{3}`$X 를 offline teacher 로 써 per-pixel target + confidence logit $`c_{u}^{v}`$ 를 얻어 hard gate 로 변환합니다.

$$m_{u}^{v}=\mathbf{1}\!\left[\sigma(c_{u}^{v})>\tau\right],$$

> "with $`\tau=0.1`$ . The distillation loss is unified across both modes" (§3.2)
> (게이트 임계 $`\tau=0.1`$. confidence 가 soft reweighting 이 아니라 "어느 픽셀을 신뢰할지" 를 고르는 hard 선택자로 작동하며, 증류 loss 식은 GT·teacher 두 모드에서 동일합니다.)

$$\mathcal{L}_{\mathrm{distill}}=\frac{\displaystyle\sum_{v,u}m_{u}^{v}\!\left(\tfrac{1}{2}\lVert\hat{q}_{u}^{v}-q_{u}^{v}\rVert_{2}^{2}+(\hat{d}_{u}^{v}-d_{u}^{v})^{2}\right)}{\displaystyle\sum_{v,u}m_{u}^{v}+\epsilon}.$$

ray 좌표는 $`\tfrac{1}{2}`$ 가중 L2, log-$`z`$ depth 는 L2 이며, 분모의 $`\sum m + \epsilon`$ 으로 유효 픽셀 수에 정규화합니다(게이트로 픽셀이 적게 살아남아도 스케일이 폭주하지 않게).

**Two-stage curriculum.** action loss 와 distillation loss 를 결합합니다.

$$\mathcal{L}=\lambda_{\mathrm{act}}\,\mathcal{L}_{\mathrm{act}}+\lambda_{\mathrm{distill}}\,\mathcal{L}_{\mathrm{distill}},$$

> "where $`\mathcal{L}_{\mathrm{act}}`$ is the base VLA's action objective, left unchanged—in our $`\pi_{0}`$ instantiation, the original flow-matching loss." (§3.2)
> ($`\mathcal{L}_{\mathrm{act}}`$ 는 base VLA 의 action 목적함수를 그대로 둔 것 — $`\pi_{0}`$ 인스턴스에서는 원래 flow-matching loss 입니다. 즉 imitation 목적함수 자체는 손대지 않습니다.)

- **Stage 1 (기하 모듈 사전학습)** — ray embedding·cross-view fusion·보조 point head 만 업데이트, backbone 은 frozen, distillation loss 우세. 기하 모듈을 dense teacher 신호에 정렬시킨 뒤 action 목적이 인계받게 합니다.
- **Stage 2 (전체 policy finetuning)** — Stage 1 checkpoint 에서 전 파라미터 unfreeze, action loss 우세, distillation 은 경량 기하 regularizer 로 잔류. 추론 시 $`\pi^{3}`$X 도 보조 head 도 쿼리하지 않습니다.

### 학습 셋업

- **입력 해상도/토큰** — $`\pi_{0}`$ 실험은 $`224\times 224`$ 입력, SigLIP 패치로 뷰당 $`16\times 16`$(=256) 패치 토큰. ray map 의 zero-init projection 을 SigLIP 출력에 더한 뒤 cross-view fusion → frame attention → 단일 global cross-view attention 1층(PRoPE 위치 신호).
- **보조 head 세부** — 뷰당 256 토큰을 $`16\times 16`$ 으로 reshape, hidden 512, transformer 2블록(8 head, 2D RoPE, QK norm, MLP ratio 4, LayerScale init 0.01), transposed-conv 3단(채널 256·128·64) + bilinear 로 $`224\times 224`$ 로 업샘플, zero-init 출력 head 2개(ray·log-$`z`$).
- **teacher cache** — main LIBERO recipe 는 변환된 LeRobot episode 에서 offline 생성. RGB 를 $`224\times 224`$ 로 resize, intrinsic 도 동일 해상도로 스케일, 각 프레임을 $`\pi^{3}`$X 인코더/디코더/point head 에 통과시켜 raw 2채널 ray 좌표 + pre-exponential log-$`z`$ + confidence logit 을 캐싱.
- **옵티마이저/스케줄(Table 6)** — AdamW($`\beta_{1}=0.9`$, $`\beta_{2}=0.95`$, $`\epsilon=10^{-8}`$, weight decay 무시 수준), global grad clip 1.0, global batch 32, bfloat16. 두 stage 모두 cosine LR decay. Stage 1: 5k step, $`\lambda_{\mathrm{act}}=0.1`$, $`\lambda_{\mathrm{distill}}=1.0`$, warmup 500, LR $`2.5\times10^{-5}\rightarrow2.5\times10^{-6}`$. Stage 2: 30k step, $`\lambda_{\mathrm{act}}=1.0`$, $`\lambda_{\mathrm{distill}}=0.05`$, warmup 1k, 동일 LR 범위.

---

## 📊 실험 설정과 결과

평가는 세 질문에 답합니다: (1) 카메라-aware 기하 모듈이 표준 시뮬 VLA 벤치마크에서 manipulation 을 향상시키는가? (2) LIBERO 류 tabletop 너머 다양한 가정 환경으로 일반화되는가? (3) 어떤 기하 부품·supervision 출처가 중요한가? Base 는 $`\pi_{0}`$, 추가로 $`\pi_{0.5}`$ ·GR00T 1.5. 모든 시뮬 결과는 3회 독립 평가의 산술평균입니다(seed 7 고정, LIBERO 는 task 당 50 rollout).

### LIBERO 메인 ($`\pi_{0}`$)

| Suite | $`\pi_{0}`$ Baseline | G$`^3`$VLA ($`\pi^{3}`$X) | G$`^3`$VLA (GT) | Gain |
|---|---|---|---|---|
| Goal | 87.4 | 88.4 | 88.4 | +1.0 |
| Spatial | 85.2 | 88.6 | 89.2 | +4.0 |
| Object | 89.4 | 93.4 | 94.4 | +5.0 |
| L-10 | 76.5 | 77.6 | 80.4 | +3.9 |
| Average | 84.6 | 87.0 | 88.1 | +3.5 |

> "With ground-truth geometric supervision, G3VLA (GT) increases the macro-average success rate from 84.6% to 88.1%, corresponding to a +3.5 point absolute gain. The largest gains occur on LIBERO-Object and LIBERO-Spatial, where success improves by +5.0 and +4.0 points respectively" (§4.2, Table 1)
> (GT supervision 으로 매크로 평균이 84.6→88.1(+3.5), 최대 향상은 Object(+5.0)·Spatial(+4.0) — 물체 위치·공간 관계 reasoning 이 필요한 task 가 calibrated 기하의 이득을 가장 크게 봅니다. teacher 증류판 $`\pi^{3}`$X 도 평균 87.0 으로 GT 없이도 유효.)

### 광역 벤치마크 ($`\pi_{0}`$)

| Benchmark | Method | Success |
|---|---|---|
| RoboCasa24 | $`\pi_{0}`$ Baseline | 34.2 |
| RoboCasa24 | G$`^3`$VLA ($`\pi^{3}`$X) | 36.5 |
| RoboCasa24 | G$`^3`$VLA (GT) | 37.1 |
| RoboTwin2.0 | $`\pi_{0}`$ Baseline | 44.0 |
| RoboTwin2.0 | G$`^3`$VLA ($`\pi^{3}`$X) | 41.0 |
| RoboTwin2.0 | G$`^3`$VLA (GT) | 49.0 |

> "RoboTwin2.0 exposes a teacher-supervision failure case: G3VLA (GT) improves the handover-block task from 44.0% to 49.0%, whereas G3VLA ( $`\pi^{3}`$ X) drops to 41.0%. We attribute this gap to unreliable offline $`\pi^{3}`$ X point-map targets in visually clean synthetic scenes" (§4.2, Table 2)
> (RoboTwin2.0 handover_block 에서 GT 는 44→49 로 오르지만 teacher 증류는 41 로 **하락** — 시각적으로 깨끗한 합성 장면에서 offline $`\pi^{3}`$X target 이 불안정해진 탓. 즉 "calibrated 기하 자체는 유효하나, teacher-distilled 기하는 domain mismatch 에 민감" 하다는 양날.)

RoboCasa24 task-family 분해(Table 7)는 GT 가 Pick&Place 13.1→18.1%, Others 39.5→42.0% 로 끌고, Doors/Drawers 는 53.3→54.2% 로 거의 평탄함을 보여, 향상이 task family 별로 불균등함을 드러냅니다.

### 백본 일반화 ($`\pi_{0.5}`$ / GR00T 1.5)

| Suite | $`\pi_{0.5}`$ Official | $`\pi_{0.5}`$ Reprod. | G$`^3`$VLA ($`\pi^{3}`$X) |
|---|---|---|---|
| Spatial | 98.0 | 98.8 | 98.2 |
| Object | 99.0 | 98.4 | 99.0 |
| Goal | 98.2 | 94.4 | 98.0 |
| L-10 | 91.4 | 91.8 | 92.8 |
| Avg. | 96.7 | 95.9 | 97.0 |

| Suite | GR00T 1.5 Baseline | G$`^3`$VLA (GT) | G$`^3`$VLA ($`\pi^{3}`$X) |
|---|---|---|---|
| Spatial | 96.6 | 94.2 | 96.6 |
| Object | 97.0 | 97.0 | 99.0 |
| Goal | 95.4 | 94.2 | 95.8 |
| L-10 | 90.6 | 92.6 | 89.6 |
| Avg. | 94.90 | 94.50 | 95.25 |

> "On GR00T 1.5's two-tower architecture, where the diffusion policy reaches visual features via cross-attention to a frozen VLM rather than consuming tokens directly, the effect is asymmetric (Table 4): G3VLA ( $`\pi^{3}`$ X) improves the macro average from 94.90% to 95.25%, while G3VLA (GT) does not (94.50%)." (§4.3, Table 4)
> ($`\pi_{0.5}`$ 는 거의 saturation(reprod. 95.9→97.0)에서 소폭 추가 향상으로 backbone 호환성 확인. GR00T 1.5 의 two-tower 구조에서는 diffusion policy 가 frozen VLM 에 cross-attention 으로만 접근해 geometry token 이 attention 병목을 한 번 더 거치므로 신호가 감쇠 — 효과가 비대칭. "기하 주입 이득은 geometry-aware token 이 action 생성에 얼마나 직접 참여하는가" 에 의존한다는 핵심 가설의 근거.)

### Ablation ($`\pi_{0}`$, LIBERO, Figure 3)

| 변형 | 평균 Success | Δ vs G$`^3`$VLA($`\pi^{3}`$X) 87.0 |
|---|---|---|
| w/o Ray | 85.0 | −2.0 (최대 단일 부품 손실) |
| w/o PRoPE | 85.9 | −1.1 |
| 1-Stage | 86.3 | −0.7 |
| G$`^3`$VLA ($`\pi^{3}`$X) | 87.0 | — |
| G$`^3`$VLA (GT) | 88.1 | +1.1 (supervision 출처 상한) |

> "Removing ray embeddings reduces average success from 87.0% to 85.0% ( $`\Delta`$ = $`-`$ 2.0), the largest single-component drop. Removing PRoPE reduces it to 85.9% ( $`\Delta`$ = $`-`$ 1.1)." (§4.4)
> (ray embedding 제거가 −2.0 으로 가장 큰 단일 부품 손실, PRoPE 제거 −1.1 — 두 부품은 상보적(ray 는 패치별 시선 방향, PRoPE 는 calibrated 뷰 간 관계). 2-stage→1-stage 는 −0.7 로 커리큘럼도 측정 가능한 비용. supervision 은 GT 가 $`\pi^{3}`$X 보다 +1.1 우위지만, $`\pi^{3}`$X 도 baseline 대비 +2.4 를 회수해 depth 부재 시 실용적 대안.)

### 실로봇 (bimanual UR5)

![Figure 2 — 실로봇 셋업](https://arxiv.org/html/2606.24472/x2.png)

> "Figure 2: Real-World experimental setup on bimanual UR5 robotic arm bench. Two tasks are used for evaluation: Pick and Place Test Tube (in blue), and Pouring Nut (in green)." (§4.1)
> (한 팔은 manipulation, 다른 팔이 context 카메라를 10개 위치로 옮기며 viewpoint shift 만을 분리해 평가하는 셋업입니다.)

> "incorporating geometric priors consistently improves OOD performance across checkpoints, increasing $`\pi_{0}`$ from 70.8–75.0 to 83.3–87.5 and improving overall success from 82.5–85.0 to 90.0–92.5." (§4.5, Table 5)
> (Pouring Nut 에서 $`\pi_{0}`$+GT 가 OOD(unseen 카메라 뷰 11–13)를 70.8–75.0→83.3–87.5 로 끌어올림. 학습에 없던 카메라 viewpoint 일반화에서 calibrated 기하가 가장 크게 기여 — test-tube task 의 $`\pi_{0.5}`$ OOD 도 25K 에서 25→50, 30K 에서 41.7→58.3. action space 변경·추론 시 명시적 3D 없이 얻은 이득.)

---

## ⚖️ 한계

- **Calibration 정확도 의존** — 저자 명시. 방법이 정확한 intrinsics·extrinsics 를 가정하므로 calibration drift, 동기화 오차, train–test mismatch 에 취약합니다. ray embedding 과 PRoPE 가 둘 다 K·T 를 직접 입력으로 쓰므로, calibration 오차는 기하 신호를 그대로 오염시켜 인덕티브 바이어스가 오히려 잘못된 prior 가 될 수 있습니다.
- **Teacher target 품질** — 저자 명시. $`\pi^{3}`$X teacher 는 occlusion·반사·blur·약한 prior 뷰에서 target 이 부정확하며, gating 은 bias 를 줄이되 제거하지 못합니다. RoboTwin2.0 의 GT 49.0 vs $`\pi^{3}`$X 41.0(baseline 44.0 보다도 낮음)이 이 위험을 실증 — 깨끗한 합성 장면에서 teacher 가 오히려 해가 됩니다.
- **아키텍처 의존성** — 저자 명시. two-tower(GR00T 1.5)처럼 action model 이 geometry-aware token 을 직접 소비하지 않고 cross-attention 으로만 닿으면 이득이 감쇠합니다. 즉 이 방법의 효과는 token 인터페이스가 action 경로에 직결된 single-stream 계열($`\pi_{0}`$/$`\pi_{0.5}`$)에 한정될 수 있어, 적용 전 backbone 의 token→action 경로 구조를 먼저 따져야 합니다.
- **action-space 결함은 미해결** — 저자 명시. visual-token 표현만 바꾸므로 action space·demonstration 부족·약한 language–action grounding 에 뿌리를 둔 실패는 손대지 못합니다. 기하 향상은 "공간·물체 민감 task" 에 국한되며 long-horizon 조합(L-10)·고수준 의미 실패에는 상대적으로 작은 이득(+3.9)에 그칩니다.
- **offline 비용** — 저자 명시. teacher cache 생성과 보조 head 학습이 offline 비용을 추가합니다(배포 시엔 불필요). 추론 부담은 없지만, 우리 스택에 적용할 경우 LeRobot episode 전체에 대한 $`\pi^{3}`$X forward + cache 저장 파이프라인이 선행돼야 합니다.
- **단일 task RoboTwin 진단** — 추론된 갭. RoboTwin2.0 평가가 handover_block 단일 task 라 bimanual·다카메라(>2 view) 일반화 주장의 표본이 좁습니다.

---

## ♻️ 재현성

- **코드** — 공식 GitHub repo 는 본문/메타에서 확인되지 않습니다(project page 만 명시: https://sites.google.com/view/g3vla). 본 분석 시점 기준 코드 공개 여부는 미확인.
- **데이터/벤치마크** — LIBERO, RoboCasa24, RoboTwin2.0 등 공개 시뮬 벤치마크 + 자체 수집 실로봇 데이터(UR5, task 당 120 episode, $`10\times10`$ cm 워크스페이스 그리드). teacher 는 공개 $`\pi^{3}`$X.
- **하드웨어** — 실로봇은 bimanual Universal Robots UR5 워크벤치(한 팔 manipulation + 한 팔 context 카메라).
- **하이퍼파라미터** — Appendix D 에 2-stage 스케줄·옵티마이저·배치가 명시돼 있어 재현 가능성은 비교적 높으나, $`\pi^{3}`$X teacher 버전 및 LIBERO→LeRobot 변환·이미지 회전 컨벤션 세부가 정확한 재현의 관건.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P2(structured multimodal observation fusion) · D8(multi-camera spatial-geometric grounding)** — 정중앙 타격. G$`^3`$VLA 는 calibrated 다카메라 기하를 token 경로에 주입하는 방법으로 D8 의 핵심 질문(뷰 간 cross-registration 을 어떻게 살릴 것인가)에 직접 답합니다. 다만 D8 v1 의 "geometry-grounded 인코더 → **unified 3D-consistent 임베딩**, flat per-camera concat **대체**" 와 달리, G$`^3`$VLA 는 token 인터페이스를 그대로 두고 ray+PRoPE inductive bias 를 **더하는** 경량 노선 — D8 의 대안 설계점입니다.
- **P2 · D9(action/dynamics-aware vision encoder)** — 부분 긴장. D9 v1 은 generic SigLIP stem 을 geometry-distilled 인코더(eVGGT)로 **교체** 권고지만, G$`^3`$VLA 는 SigLIP 을 유지(frozen)하고 인코더 **뒤** 에 기하 증류를 보조 head 로 붙입니다. 즉 "인코더 교체 없이 기하를 주입" 하는 중간 경로로, D9 의 교체 비용을 피하는 절충안.
- **P4(데이터 효율 적응을 위한 사전학습) · prior-preservation 레버** — zero-init projection(시작 시 항이 0), Stage 1 backbone freeze 로 사전학습 거동을 명시적으로 보존합니다. P4 의 "VLM prior 보존" 하위 레버와 메커니즘이 통합니다(다만 P4 headline 인 corpus·lineage·recipe 는 아님).
- **P1(heterogeneous Body/Hand action expert)** — 약한 지지. action space·imitation 목적함수 불변을 강조하므로 P1 의 action-expert 설계와 직교(충돌 없이 결합 가능). G$`^3`$VLA 는 관측 측, P1 은 decoder 측.
- **Identity 지지/긴장** — Identity 의 "structured multimodal observation fusion — multi-camera spatial-geometric grounding(flat concat 초월)" 주장을 직접 지지합니다. 단, 우리 셋업의 핵심인 **per-finger proprio-tactile binding** 은 다루지 않아(순수 비전 기하), observation elevation 의 절반(공간 축)만 커버.

---

## ✨ 핀 논문 대비 델타

- **vs VGGT([arXiv:2503.11651], P2 §5 Top 핀)** — VGGT 는 feed-forward 로 multi-view 3D(camera/point/depth/track)를 **예측하는 인코더 자체** 입니다. G$`^3`$VLA 는 그런 geometry teacher($`\pi^{3}`$X, VGGT 계열)를 **소비** 해, 사전학습 VLA token 에 증류로 기하를 주입할 뿐 인코더를 교체하지 않습니다 — "geometry 모델을 어떻게 만드나" 가 아니라 "이미 있는 VLA 에 어떻게 끼우나" 가 새로움.
- **vs eVGGT / Geometry-Aware Vision Encoder([arXiv:2509.15880], P2 §5 핀)** — eVGGT 는 기하를 **인코더에 distill 해 stem 을 대체** 하는 노선입니다. G$`^3`$VLA 의 진짜 델타는: 인코더는 그대로 두고 (i) ray embedding + PRoPE 라는 token-level inductive bias 와 (ii) 추론 시 폐기되는 보조 point head 증류로만 기하를 넣어, **action space·목적함수 불변 + zero-init 으로 사전학습 거동 보존** 을 동시에 달성한다는 점. eVGGT 가 "더 나은 기하 인코더" 라면, G$`^3`$VLA 는 "기존 VLA 를 안 깨고 기하를 더하는 어댑터" 입니다.
- **vs DynaFLIP([arXiv:2605.30350], P2 §5 핀)** — DynaFLIP 은 image-language-3D flow 의 action/dynamics-aware 표현(시간·동역학 축)인 반면, G$`^3`$VLA 는 정적 단일 프레임의 multi-view calibration(공간 축)에 집중 — 상보적이며 결합 여지가 있습니다.

---

## ⚙️ 의사결정 함의

- **D8 설계 분기** — "geometry-grounded 인코더로 flat concat 을 통째 교체(D8 v1)" 외에, **token 경로에 ray+PRoPE bias 를 더하는 경량 어댑터** 를 D8 의 대안 후보로 올릴 수 있습니다. 우리 base 가 $`\pi_{0}`$/$`\pi_{0.5}`$ 계열(single-stream, token→action 직결)이면 G$`^3`$VLA 식 주입이 직접 호환 — GR00T 류 two-tower 보다 이득이 큼이 본 논문의 결론.
- **구체 config 변경(우리 파이프라인 적용 시)** — (1) vision encoder 출력과 action expert 사이에 `ray_embed`(zero-init projection) + `cross_view_fusion`(frame attn → global cross-view attn, PRoPE 위치 신호) 층 삽입, (2) 학습 전용 `aux_point_head`(hidden 512, transformer 2블록, transposed-conv 256/128/64 → 224 upsample) 추가, (3) loss 에 `lambda_distill` 항 신설, (4) 2-stage 스케줄 도입 — Stage 1 `lambda_act=0.1, lambda_distill=1.0, steps=5k, backbone frozen`, Stage 2 `lambda_act=1.0, lambda_distill=0.05, steps=30k, unfreeze all`, (5) teacher gate `tau=0.1`.
- **데이터 전처리** — LIBERO/LeRobot episode 에 대해 $`\pi^{3}`$X(또는 GT depth)로 per-view point map cache(2채널 ray + log-$`z`$ + confidence)를 offline 선생성. 우리 다카메라 셋업의 intrinsics·extrinsics(forward kinematics 로 extrinsic 추정 가능)를 관측에 함께 실어야 함.
- **평가 메트릭 추가** — viewpoint-OOD success(학습에 없던 카메라 위치)를 별도 트랙으로. 본 논문에서 이득이 ID 보다 OOD 에서 크게 나므로, 우리 vla-eval 에 "unseen camera pose" split 을 추가하면 기하 모듈의 가치를 직접 측정 가능.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 점검) calibration 가용성** — 우리 데이터 파이프라인에 per-frame intrinsics·extrinsics 가 실제로 저장/접근 가능한지 먼저 확인. ray embedding·PRoPE 둘 다 K·T 를 입력으로 요구하므로, calibration 메타가 없으면 방법 자체가 성립하지 않습니다. (LeRobot 변환 시 카메라 파라미터가 누락되기 쉬움.)
- **two-tower 여부** — 우리 backbone 의 token→action 경로가 직결인지 cross-attention 병목인지 확인. GR00T 1.5 처럼 frozen VLM 에 cross-attention 으로만 닿는 구조면 GT 증류조차 이득이 사라졌으므로(94.90→94.50), 적용 전 이 구조 점검이 필수.
- **teacher domain mismatch** — 우리 데이터가 시각적으로 깨끗한 합성/단순 장면이면 $`\pi^{3}`$X teacher target 이 RoboTwin2.0 처럼 baseline 보다도 해로울 수 있음(44→41). 소규모 sanity: 몇 개 episode 에 teacher point map 을 시각화해 confidence gate 통과율과 target 품질을 눈으로 검증한 뒤 전면 cache.
- **이득의 task 의존성** — 본 논문 이득은 spatial/object 민감 task 에 집중(+4.0/+5.0)되고 long-horizon(L-10 +3.9)·goal(+1.0)은 작음. 우리 dexterous hand task 가 공간 정밀도 bottleneck 인지(=기하 이득 큼) 아니면 contact/grasp bottleneck 인지(=기하 무관) 먼저 분류. 후자라면 P2 의 tactile 축(D11)이 우선.
- **multi-camera 전제** — 본 방법의 핵심 가치는 다카메라 cross-view fusion 에서 나옵니다. 단일 카메라(혹은 base+wrist 2뷰만)인 셋업에서는 cross-view 항이 약해 ray embedding 의 단독 기여(+2.0 수준)만 남을 수 있음.
- **hand 도메인 부재** — 모든 실험이 arm/gripper(UR5, LIBERO)이며 dexterous hand·per-finger contact 가 전무. 공간 기하 prior 가 손가락 수준 접촉 정밀도로 전이되는지는 본 논문이 보장하지 않음.

---

## 💡 컨텍스트 제안

- **P2 §5 핀 후보** — G$`^3`$VLA([arXiv:2606.24472])는 D8 의 "인코더 교체 없는 token-level 기하 주입" 이라는 별도 설계점을 대표하며, eVGGT(교체 노선)와 직접 대비됩니다. 현 핀이 모두 "더 나은 기하 인코더" 쪽이므로, "사전학습 VLA 보존형 어댑터" 축의 대표로 비-핀 methodology base 등재를 사람에게 제안합니다(8핀 cap 고려 시 append 아닌 교체 검토).
- **D8 v1 보강** — D8 v1 이 "unified 3D-consistent 임베딩으로 flat concat 대체" 단일 노선인데, 본 논문은 "token 인터페이스 보존 + ray/PRoPE bias 추가" 라는 lower-risk 대안이 $`\pi_{0}`$ 계열에서 +3.5 를 낸다는 증거를 줍니다. D8 deferred candidate 로 "어댑터형 기하 주입" 을 명시해 둘 가치가 있습니다. (사람 판단 사항 — context 파일은 수정하지 않았습니다.)
