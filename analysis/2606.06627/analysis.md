# Paper Analysis — What Matters When Cotraining Robot Manipulation Policies on Everyday Human Videos?

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | What Matters When Cotraining Robot Manipulation Policies on Everyday Human Videos? |
| 저자 | Richard Li, Aditya Prakash, Andrew Wen, Saurabh Gupta, Yilun Du, Pulkit Agrawal |
| 링크 | [arXiv:2606.06627](https://arxiv.org/abs/2606.06627) · [Website](https://richardrl.github.io/what-matters-cotraining-human-videos/) |
| 발행일 / 버전 | 2026-06-04 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-10 |
| 관련 Pillar | P0, P4, P1, P2 |
| 태그 | egocentric-data, vla-arch, flow-matching |
| 카탈로그 | dataset/human/TriHands |

---

## 🧭 한 줄 요약 (TL;DR)

"일상 인터넷 영상"으로 로봇 정책을 cotraining 할 때 무엇이 전이를 가능케 하는지를, 정제된 lab 영상이 아니라 자연스러운 동작 + 고품질 삼각측량 3D 손 라벨을 가진 프록시 데이터셋(TriHands, 532 영상·28시간)으로 통제 실험한다. 결론은 (1) 손 포즈 품질이 전이를 좌우하지만, (2) 정확한 손이 있어도 자연 동작이 만드는 *motion gap* 때문에 vision·policy 네트워크가 임베디먼트별로 specialize 하지 않으면 전이가 막힌다는 것 — 이를 image-space scale 정렬 + token-level fusion + 임베디먼트별 action encoder/decoder + 로봇 데이터 upweighting 으로 풀어 저(低)로봇데이터 구간에서 절대 성공률 +29.7%p 를 얻는다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 텔레오퍼레이션 시연은 비싸고 RL 은 보상 설계·탐색·sim2real 때문에 스케일이 어렵다. 풍부한 인터넷 인간 영상을 로봇 정책 cotraining 에 쓰고 싶지만, *어떤 요인이 그런 영상에서 로봇으로의 전이를 가능케 하는지* 가 미해결 문제다.
- **기존 접근의 한계 — 모듈형 파이프라인** — 인터넷 영상을 affordance·2D track·3D pose 같은 중간 표현으로 분해해 쓰는 방식은 정책을 여러 단계로 쪼개 end-to-end cotraining 의 단순함·확장성을 못 누린다.
- **기존 접근의 한계 — aligned lab 데이터 의존** — end-to-end cotraining 을 성공시킨 선행연구(Egomimic/Egobridge)는 동작을 로봇처럼 연출하고 동일 카메라·전용 하드웨어로 정확한 3D 손을 얻은 *aligned* 데이터에 의존한다. 인터넷 영상의 비제약 동작·이종 카메라·과제 불일치·노이즈 손 라벨과는 본질적으로 다르다.
- **본 논문의 가설** — 인터넷 영상의 핵심 난점(egocentric 시점, 자연 동작, 카메라·과제 불일치)을 보존하되 extrinsic 카메라로 고품질 손을 삼각측량한 *프록시* 셋업에서 연구하면, 전이의 병목을 (1) 3D 손 포즈 품질, (2) 자연 동작·과제 불일치가 만드는 action gap 두 축으로 분리·규명할 수 있다.
- **왜 지금 중요한가** — 강력한 3D 손 포즈 추정기가 최근에야 등장했고, 이 병목들을 짚어두면 후속 연구가 (예: 손 추정기 학습데이터 확장으로) 정확히 그 지점을 공략할 수 있다. "오늘 당장 인터넷 영상에 쓸 방법"이 아니라 "그 regime 를 여는 길의 지도"가 목표다.

---

## 🧩 핵심 기여

- **TriHands 데이터셋** — EgoExo4D 의 532개 요리 영상을 멀티뷰 삼각측량으로 재처리해 자연 동작 + 정확한 3D 손 라벨을 가진 304만 프레임(28시간, 30fps) 데이터셋을 구축. lab 대규모 데이터(EgoDex)보다 *작아도* 로봇 전이가 더 좋음을 보인다.
- **손 라벨 품질 ↔ 전이 인과 규명** — 동일 영상에 대해 삼각측량 손 vs 최신 단안(monocular) 추정기(HaWoR) 를 비교하고, 보정된 Gaussian noise 를 손에 단계적으로 주입(0.5×/1.0×)해 *전이가 손 품질에 단조 의존* 함을 정량화.
- **Image-space scale 정렬** — 서로 다른 카메라(초점거리·FOV)로 찍힌 데이터셋을 cotraining 할 때 객체의 *이미지 공간 스케일* 불일치가 간과돼 온 문제임을 지적하고, 단순한 extent-matched pinhole 재투영으로 전이를 크게 끌어올림(선도 VLA 도 안 다루는 요인).
- **임베디먼트 specialization 필수성** — image bottleneck(CLS-token)·공유 action decoder 같은 lab 데이터용 통념 설계가 자연 동작 데이터에선 전이를 *막는다* 는 것을 ablation 으로 보이고, token-level fusion + 임베디먼트별 action encoder/decoder + 로봇 데이터 upweighting 의 cotraining recipe 를 제안.
- **대규모 실측 평가** — 532 인간 영상 + 3,000 로봇 시연으로 6개 실세계 과제를 학습, 3,480회 실측 rollout. 저로봇데이터 구간에서 절대 +29.7%, 데이터가 늘어도 지속 이득을 보고.

---

## 🔑 기술 키워드

- **Human-Robot Cotraining** — 인간 영상과 로봇 궤적을 한 정책에서 동시에 학습시키는 방식. 본 논문의 분석 대상이자 recipe 가 겨냥하는 셋업이다.
- **Conditional Flow Matching** — Gaussian noise 와 정답 action chunk 를 잇는 확률 경로의 벡터장을 회귀로 학습하는 연속 액션 생성기. 본 정책의 action expert 생성 방식(π 계열과 동일).
- **Multi-view Triangulation (DLT)** — 여러 카메라의 2D 키포인트를 직접선형변환으로 3D 로 복원하는 고전 기법. TriHands 의 고품질 3D 손 라벨을 만드는 핵심 도구다.
- **MANO** — 손을 관절·형상 파라미터로 표현하는 표준 손 메시 모델. 인간 손 포즈를 로봇 action 공간으로 retarget 하는 출발점이다(middle finger proximal 관절 프레임 사용).
- **TCP (Tool Center Point)** — 그리퍼의 기준점·자세. 로봇 action 공간의 정의 단위이자 인간 손을 매핑할 표적 프레임이다.
- **Token-level Fusion** — ViT 이미지 토큰 전체 grid 를 noisy action 토큰과 공유 attention 으로 결합하는 방식. CLS-token 병목과 달리 임베디먼트별 시각 이해 specialize 를 허용한다.
- **Transfusion-inspired MoE FFN** — 시각·액션 토큰에 모달리티별 FFN expert 를 두는 트랜스포머 설계. 임베디먼트 specialization 을 가능케 하는 아키텍처 토대다.
- **Image-space Scale Alignment** — 초점거리·FOV 다른 카메라 간 객체의 픽셀 크기를 맞추는 전처리. pinhole 식으로 로봇 카메라 extrinsic 을 조정해 공유 특징 학습을 돕는다.
- **HaWoR** — 단안 영상에서 손 포즈를 추정하는 최신(SOTA) 추정기. 삼각측량 손의 비교군이자 "손 품질↔전이" 인과 실험의 노이즈 대표값이다.

---

## 🔬 방법론

### 직관

핵심 긴장은 *정렬(alignment)* 과 *specialization* 사이에 있습니다. 인간과 로봇이 같은 물체를 같은 자세로 볼 때 정책이 같은 표현을 학습하도록 관측·액션을 정렬하면 positive transfer 가 생기지만, 자연 동작 인간 데이터는 로봇과 동작 자체가 너무 달라서(motion gap) 표현을 *억지로* 정렬하면 오히려 해롭습니다. 그래서 이 논문은 "관측·액션은 정렬하되, 네트워크는 임베디먼트별로 갈라지게 둔다"는 두 갈래 전략을 씁니다.

첫째 축은 *정렬* 입니다. 이종 카메라가 만드는 이미지 스케일 차이를 pinhole 기하로 보정하고(image-space scale alignment), MANO 손을 로봇 TCP 프레임으로 retarget 해 두 action 분포가 같은 support 를 갖게 만듭니다. 머리 카메라가 움직여 생기는 극심한 multimodality 는 모든 포즈를 현재 head frame 으로 변환해 안정화합니다.

둘째 축은 *specialization* 입니다. 이상적인 cross-embodiment 정책이라면 공유 encoder 가 인간·로봇 관측을 같은 latent 로 보내고 공유 decoder 가 같은 action 을 내야 하지만, motion gap 이 크면 이 가정은 *반드시* 깨집니다. 따라서 이미지 토큰을 단일 벡터로 뭉개는 CLS-token 병목 대신 토큰 grid 전체를 쓰는 token-level fusion, 그리고 임베디먼트별로 분리된 action encoder/decoder 를 둡니다.

셋째로, 인간 데이터가 훨씬 많아 학습을 지배하지 않도록, 미니배치마다 두 임베디먼트에서 *같은 수* 를 독립 샘플링해 로봇 데이터를 암묵적으로 upweight 합니다. 이 세 가지가 합쳐져 자연 동작 인간 영상에서도 의미 있는 motion transfer 가 나옵니다.

![Figure 1 — 시스템 개요 + rollout](https://arxiv.org/html/2606.06627/images/teaser3.jpg)

> "Figure 1: Top: System diagram showing data processing and policy cotraining steps. Bottom: Rollouts from cotrained policy manipulating unseen objects in unseen scenes." (§1)
(데이터 처리(삼각측량·정렬) → cotraining → unseen 객체/장면 일반화라는 전체 파이프라인을 한 장으로 요약한 그림.)

### 아키텍처

**데이터 스트림 (§4.1)** — 인간은 egocentric 머리 카메라, 로봇은 그와 유사 위치의 egocentric 카메라를 쓴다(센서 크기·초점거리는 크게 다름). 로봇은 6-DOF AgileX Piper 팔 + parallel-jaw 그리퍼이고 action 공간은 TCP 포즈 + 이산 grasp 명령이다.

> "Concretely, we define $`{}^{R}{\mathbf{a}}=\bigl({}^{\text{camera}}{\mathbf{p}}^{\text{TCP}},{}^{\text{camera}}{\mathbf{R}}^{\text{TCP}},g\bigr)`$ , where $`g`$ is a discrete ternary variable representing open , close , and no-op grasp commands." (§4.1)
(로봇 action 은 카메라 프레임 기준 TCP 위치 $`{}^{\text{camera}}{\mathbf{p}}^{\text{TCP}}`$ · 회전 $`{}^{\text{camera}}{\mathbf{R}}^{\text{TCP}}`$ 와 open/close/no-op 세 값을 갖는 이산 grasp $`g`$ 로 구성된다.)

**Cross-embodiment 트랜스포머 (§4.4, Supp. I)** — Transfusion 영감의 설계로, 시각·액션 토큰에 *분리된 FFN expert* 를 둔다. 공유 SigLIP ViT encoder $`E_{\mathrm{img}}`$ 가 이미지를 $`N\times D`$ 시각 토큰으로, 임베디먼트별 action encoder $`E_{\mathrm{act}}^{d}`$ 가 noisy action 을 $`T\times D`$ 토큰으로 만들고, 둘을 한 시퀀스로 concat 해 self-attention 에 넣는다(token-level fusion). self-attention 의 Q/K/V 투영은 *모달리티별로만* 공유되고 데이터셋(임베디먼트) 간에도 공유된다.

> "$`\mathbf{H}^{d}=\mathrm{softmax}(\mathbf{Q}^{d}(\mathbf{K}^{d})^{\top}/\sqrt{D})\mathbf{V}^{d}`$ . This design allows image and action tokens to attend jointly." (§Supp. I)
(시각·액션 토큰이 한 attention 안에서 상호 참조하도록 cross-modality self-attention 을 계산한다. 출력 $`\mathbf{H}^{d}`$ 는 임베디먼트별 flow-matching action decoder $`G_{\mathrm{act}}^{d}`$ 로 들어가 denoised action 을 낸다.)

로봇 궤적엔 egocentric + wrist 카메라 두 이미지를, 인간 궤적엔 egocentric 만 주고 wrist 스트림 토큰 위치는 전부 마스킹한다. ViT 이미지 토큰 grid 는 그대로 유지(image bottleneck 없음)하며, action·proprioception encoder/decoder 는 3-layer MLP(LeakyReLU)다.

![Figure 2 — conditional flow matching 입출력 구조](https://arxiv.org/html/2606.06627/x1.png)

> "Figure 2: Input-output diagram for inference over human and robot data in our conditional flow matching architecture. Images shown with image-space alignment and resize. Color denotes weight sharing." (§4)
(색이 weight 공유 범위를 나타내며, 시각 토큰은 공유·action 경로는 임베디먼트별로 갈라지는 specialization 구조를 시각화한 그림.)

### 학습 목표 / 손실

**TriHands 손 라벨 (§3)** — 강한 3D 손 base model 을 소수의 부분 2D 키포인트로 fine-tune 한 뒤 멀티뷰 삼각측량한다. fine-tune 손실은 reprojection L1:

$$\mathcal{L}_{\text{proj}}=\sum_{i\in\mathcal{I}}\lVert{\mathbf{p}}_{i}^{2\mathrm{D}}-\pi_{{\mathbf{K}}}\!\big(\hat{{\mathbf{p}}}_{i}^{3\mathrm{D}}\big)\rVert_{1}$$

> "$`\mathcal{L}_{\text{proj}}=\sum_{i\in\mathcal{I}}\lVert{\mathbf{p}}_{i}^{2\mathrm{D}}-\pi_{{\mathbf{K}}}\!\big(\hat{{\mathbf{p}}}_{i}^{3\mathrm{D}}\big)\rVert_{1}`$ , where $`\pi_{{\mathbf{K}}}`$ is the projection operator with intrinsics $`{\mathbf{K}}`$ , and $`\mathcal{I}`$ is the set of joints with 2D annotations." (§3)
(예측 3D 관절 $`\hat{\mathbf{p}}_{i}^{3\mathrm{D}}`$ 을 intrinsic $`\mathbf{K}`$ 로 투영($`\pi_{\mathbf{K}}`$)한 2D 와 라벨 2D 의 L1 거리. 2D 주석이 있는 관절 집합 $`\mathcal{I}`$ 에서만 합산하며, 단 4,407 프레임(최종 우측 손 프레임의 0.144% 미만)으로 충분.)

**Image-space scale 정렬 (§4.2)** — pinhole 식 $`Z=\frac{f\Delta X}{\Delta u}`$ 에서, 같은 3D 크기 $`\Delta X`$ 라도 초점거리 $`f`$ ·깊이 $`Z`$ 가 다르면 픽셀 크기 $`\Delta u`$ 가 달라진다. 인간 fisheye 를 pinhole 로 undistort 하고 로봇 카메라를 인간 손목 중앙 깊이 $`z_{\text{human}}`$ 에 두되, FOV 차이를 보정해 깊이를 재설정한다:

$$z_{\text{robot}}=z_{\text{human}}\frac{f_{s}H_{c}}{f_{c}H_{s}}$$

> "translating it to depth $`z_{\text{robot}}=z_{\text{human}}\frac{f_{s}H_{c}}{f_{c}H_{s}}`$ , where $`H_{c},H_{s}`$ are image heights and $`f_{c},f_{s}`$ the focal lengths" (§4.2)
($`H_c,H_s`$ 는 이미지 높이, $`f_c,f_s`$ 는 초점거리. 카메라를 $`90^\circ`$ 회전시켜 넓은 FOV 로 세로 범위를 담고, 이 깊이 조정으로 3D scene extent 는 유지한 채 이미지 스케일을 맞춘다.)

**Action 공간 정렬 (§4.3)** — MANO "middle finger proximal" 관절 프레임을 로봇 TCP 프레임에 맞춰 회전해 인간 action 을 매핑한다. 머리 카메라 움직임이 만드는 multimodality 는 포즈를 현재 head frame 으로 변환해 안정화한다:

$$\mathbf{a}_{t},\ldots,\mathbf{a}_{t+H}={}^{c_{t}}\!\mathbf{a}^{t},\ldots,{}^{c_{t}}\!\mathbf{T}^{w}\,{}^{w}\!\mathbf{T}^{c_{t+H}}\,{}^{c_{t+H}}\!\mathbf{a}^{t+H}$$

> "We resolve this by mean-centering each dataset independently, filtering to the 1st–99th percentiles, and scaling to $`\pm 1`$ . Rotations need no normalization since $`R\in\mathrm{SO}(3)\Rightarrow R_{ij}\in[-1,1]\;\forall i,j\in\{1,2,3\}.`$" (§4.3)
(잔여 분포 bias 는 데이터셋별 독립 mean-centering + 1–99 백분위 필터 + $`\pm 1`$ 스케일로 해소. 회전은 $`\mathrm{SO}(3)`$ 원소라 정규화 불필요.)

**가중 cotraining 손실 (§4.5, Supp. H)** — 미니배치마다 두 임베디먼트에서 같은 수를 독립 샘플링한다. 이는 uniform 샘플링 대비 로봇 손실을 $`\frac{N_{R}+N_{H}}{N_{R}}`$, 인간 손실을 $`\frac{N_{R}+N_{H}}{N_{H}}`$ 로 가중하는 것과 동치다.

> "This scheme is equivalent to weighting the robot loss by $`\frac{N_{R}+N_{H}}{N_{R}}`$ and the human loss by $`\frac{N_{R}+N_{H}}{N_{H}}`$ relative to a uniform sampling strategy." (§4.5)
(로봇 데이터셋 $`N_R`$ 이 인간 $`N_H`$ 보다 훨씬 작으므로 이 동일-수 샘플링이 로봇 데이터 영향력을 증폭 — 유해한 표현 정렬을 막는다.)

### 학습 셋업

- **데이터** — 인간: TriHands 532 영상(전 영상 RGB 사용) + 삼각측량/단안 손 action. 로봇: 과제당 10개 환경 × 50 시연 = 500 demos/task(scaling law 가이드라인 따름). 6개 과제(Pick / Stack / Pull / Reorient / Book / Pour).
- **백본/아키텍처** — SigLIP ViT(hidden 1152, 27 layer, patch 14, image 224) + self-attention 6 layer(head 8, head dim 256). Vision expert hidden 2048, action/proprio expert hidden 1024.
- **옵티마이저** — Adam(β=(0.9, 0.95)), Visual encoder LR $`3.0\times10^{-5}`$, MoE 파라미터 LR $`3.0\times10^{-4}`$. Flow matching 의 timestep 은 Beta(α=1.5, β=1.0) 분포에서 샘플.
- **하드웨어/규모** — 304만 우측 손 프레임 생성, 3,480회 실측 rollout 평가.

---

## 📊 실험 설정과 결과

네 가설을 검증한다 — **H1**: 인간 데이터 cotraining 이 새 객체·배경 zero-shot 일반화를 높인다. **H2**: 인간 데이터가 *coarse 시각 특징* 이 아니라 *motion 지식* 을 전이한다. **H3**: 손 품질↑ → 전이↑. **H4**: 임베디먼트 specialization 허용 → 로봇 성능↑.

**핵심 결과 (Table 2, 3-env 저데이터 구간):**

| Method | 3 envs | 5 envs | 10 envs |
|---|---|---|---|
| HC (Human Cotraining) | 41.7±12.1% | 53.6±12.7% | 66.1±10.5% |
| RO (Robot Only) | 12.0±8.2% | 32.5±14.5% | 53.6±13.4% |

> "From Table 2 , we observe consistent gains across all robot data regimes using our recipe, with the largest improvements in the low-data setting: human cotraining improves absolute success rates by $`20\%`$ – $`48\%`$ at the 3-env level (Figure 5 )." (§6)
(저로봇데이터(3-env)에서 격차가 가장 크고(절대 +20~48%p, 평균 +29.7%p), 로봇 데이터가 늘수록 좁혀지지만 — same-task·same-distribution 시연을 받는 RO 가 강해지므로 — zero-shot 저데이터 이득은 RL post-training 과 결합 시 실용적.)

**Recipe·baseline 비교 (Table 1, 3-env, 모두 TriHands cotrain except RO):**

| 설정 | Mean | Pick | Stack | Pull | Reorient | Book | Pour |
|---|---|---|---|---|---|---|---|
| Ours | 41.5±12.1% | 50.0 | 48.0 | 63.0 | 38.0 | 23.0 | 26.7 |
| Robot Only | 12.0±8.2% | 30.0 | 10.0 | 15.0 | 11.7 | 0.00 | 5.00 |
| CLS-token (vs token fusion) | 14.7±18.6% | 0.00 | 6.67 | 61.7 | 5.00 | 6.67 | 8.33 |
| EgoDex (vs TriHands) | 19.4±13.4% | 33.3 | 45.0 | 18.3 | 8.33 | 11.7 | 0.00 |
| HaWoR (vs TriHands) | 24.7±16.9% | 53.3 | 10.0 | 48.3 | 15.0 | 20.0 | 1.70 |
| EgoBridge (vs BC) | 16.6±10.7% | 28.0 | 10.0 | 35.0 | 20.0 | 0.00 | 6.67 |
| PiZero (vs sep. enc/dec) | 17.5±6.0% | 21.7 | 21.7 | 23.3 | 15.0 | 20.0 | 3.30 |

per-ablation 읽기:

- **CLS-token vs token fusion** — Pull(61.7)만 빼고 전 과제에서 token fusion 이 압도. motion gap 이 커서 인간·로봇 action chunk 가 뚜렷이 다르므로, 토큰 grid 를 유지해야 시각 이해를 임베디먼트별로 specialize 할 수 있다.
- **공유 vs 분리 encoder/decoder (PiZero)** — PiZero(공유 encoder/decoder)는 평균 17.5%로, action encoder/decoder 를 untie 하면 6개 중 5개 과제에서 큰 향상.
- **TriHands vs EgoDex** — TriHands 가 *5배 적은 시간* 에도 전 과제에서 EgoDex 를 능가 → 절대량보다 *scene diversity* 가 중요하다는 시사.
- **EgoBridge** — CLS-token baseline 대비 4/6 과제에서 개선되나 BC-only recipe 엔 못 미침. action 유사도 기반 optimal transport 손실이 큰 action gap 에서 신뢰성이 떨어지기 때문.

> "We visually analyze the errors and find $`100\%`$ of the Robot Only errors on 5/6 tasks are local errors. On these tasks, Human Cotraining outperforms Robot Only $`82.8\pm 11.4\%`$ to $`29.2\pm 13.7\%`$ , indicating motion transfer." (§6)
(H2 검증 — RO 실패의 100%가 객체 근처까지는 가는 *local* 오류인 5/6 과제에서 HC 가 RO 를 크게 앞서므로, coarse 시각 전이가 아니라 *미세 motion 전이* 가 일어난다는 증거. 단 가장 복잡한 Pour 는 RO 가 servo 조차 못해 이 논증 적용 불가.)

**손 품질·정렬 ablation (Table 3 등):**

| 항목 | 값 |
|---|---|
| HaWoR 손 오차 (MPJPE / PA-MPJPE / W-MPJPE / WA-MPJPE, mm) | 185.67 / 15.72 / 161.85 / 77.86 |
| Noise 0.0× / 0.5× / 1.0× (Mean SR) | 48.3±19.6% / 30.0±13.1% / 20.0±6.5% |
| Extent-Matched Pinhole (Ours) | 51.2% [39.8, 62.6] |
| Medium / Heavy Misalignment Pinhole | 40.0% / 25.0% |
| Robot-Only | 26.2% [17.0, 37.3] |

> "Monocular-estimated hands performance is worse when averaged across tasks compared to the triangulated hands (Table 1 ). However, the mean success rate for HaWoR is still higher than Robot Only ( $`24.7\%`$ vs $`11.9\%`$ ) (Table 2 )." (§6)
(H3 — 단안 손은 삼각측량 손보다 못하지만 RO 보다는 높다: 노이즈 손도 일부 이득. noise 주입 시 전이가 *단조* 로 악화(48.3→30.0→20.0)해 "손 품질↑→전이↑"를 인과적으로 확인.)

> "Scale-aligning the human fisheye images with an extent-matched pinhole camera doubles performance over Robot Only (Table 5 ); a heavily-misaligned pinhole yields no transfer benefit." (§6)
(image-space scale 정렬이 RO 대비 성능을 2배(26.2→51.2%)로 — 심하게 어긋난 pinhole 은 전이 이득이 0. cotraining 의 숨은 전제 조건임을 보임.)

![Figure 5 — 과제별 HC vs RO 스케일링](https://arxiv.org/html/2606.06627/images/line_plots_with_ci_and_grid_lines_and_scaling_curves.jpg)

> "Figure 5: Per-task comparison between human cotraining with triangulated hands and robot-only training (95% Clopper-Pearson CI)." (§5)
(6개 과제 각각에서 로봇 환경 수(3/5/10)를 늘려가며 HC 와 RO 의 성공률 곡선을 비교 — 저데이터 구간 격차가 가장 크다는 본문 주장을 시각화.)

---

## ⚖️ 한계

- **프록시 셋업 — 인터넷 영상 직접 적용 불가** — 저자 스스로 "오늘 당장 인터넷 영상에 쓸 방법이 아니다"라고 못 박는다. TriHands 의 고품질 손은 *extrinsic 멀티뷰 카메라* 삼각측량의 산물이며, 단안 인터넷 영상엔 그런 ground-truth 가 없다. 즉 이 논문은 손 추정기가 충분히 좋아졌을 때의 *상한* 을 보여줄 뿐, 전이 파이프라인이 단안에서 바로 돈다는 보장은 아니다.
- **복잡 과제에서 motion transfer 불확실** — Pour(가장 복잡) 과제에선 RO 가 객체까지 servo 도 못해 motion transfer 논증 자체가 성립하지 않는다. 저자는 kinematic retargeting 의존과 큰 motion gap 때문에 복잡 과제에서 recipe 가 덜 효과적일 수 있다고 인정한다 — retargeting 이 손가락·접촉 디테일을 버리는 데서 오는 구조적 한계로 보인다.
- **단일 그리퍼 임베디먼트** — 로봇은 6-DOF 팔 + parallel-jaw 그리퍼 하나다. MANO 손 → TCP + ternary grasp 매핑은 다지(多指) 손의 자유도를 통째로 버린다. "손 영상으로 손 정책을 배운다"기보다 "손 궤적으로 *그리퍼 도달·파지* 를 배운다"에 가깝다.
- **정렬에 대한 민감도** — image-space scale 정렬이 어긋나면(heavy misalignment) 전이 이득이 0 으로 사라진다. 즉 recipe 의 이득은 카메라 기하 보정이라는 *수작업 전처리* 의 정확도에 강하게 의존하며, 카메라 셋업이 바뀔 때마다 재보정이 필요하다.
- **cotraining 이지 staged pretraining 이 아님** — 인간·로봇을 한 번에 co-train 하는 단일 단계 학습이다. "대규모 pretraining → 소량 deploy 데이터 적응"이라는 data-efficient adaptation regime 과는 다른 셋업이라, 이득이 그 regime 로 그대로 옮겨갈지는 별도 검증이 필요하다.
- **vision + proprio 만, 접촉 모달리티 없음** — tactile/force 입력이 없어 post-contact 정밀 조작(미끄럼·파지 유지)은 다루지 않는다. 본 분석 대상 과제도 대부분 quasi-static pick/place 계열이다.

---

## ♻️ 재현성

- **데이터셋** — TriHands 는 EgoExo4D(⚠️ gated) 의 532 영상을 재처리한 파생물. 손 라벨·삼각측량 파이프라인은 Appendix A–C 에 상술(DLT + nonlinear refinement, reprojection 임계 필터, 0.4s 선형 보간). EgoExo4D 라이선스에 종속되므로 직접 재배포 여부는 불명확.
- **코드/모델** — 프로젝트 웹사이트([richardrl.github.io/what-matters-cotraining-human-videos](https://richardrl.github.io/what-matters-cotraining-human-videos/))에 interactive visualization 이 있으나, 본문에 코드·가중치 공개 명시는 확인되지 않음(arXiv HTML 기준).
- **하드웨어** — 6-DOF AgileX Piper + parallel-jaw 그리퍼, egocentric + wrist 카메라. 카메라 사양·정렬 유도는 Appendix D, F 에 기재.
- **하이퍼파라미터** — Table 6 에 모델·학습 하이퍼(LR, Adam β, ViT/expert 차원, flow matching Beta 분포 등) 상세 공개 → 아키텍처 재구성은 가능한 수준.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P0(VLA Datasets & Benchmarks) — 가장 직접적.** TriHands 는 P0 가 추적하는 *egocentric 인간 영상 + 3D 손 추적* 데이터셋의 정확한 표본이다. **D24**(priority data axis = egocentric 인간 영상 중심)를 정면으로 지지하고, "TriHands < EgoDex 규모지만 전이 우위(scene diversity > scale)"는 corpus 선정 기준에 직접적인 증거다. **D27**(license/usability bar): EgoExo4D 파생이라 ⚠️ gated — 라이선스 종속 리스크가 P0 의 usability 바와 맞물린다. EgoDex·Ego-Exo4D 둘 다 P0 핀 논문이라 비교축이 정확히 겹친다.
- **P4(Pretraining for Data-Efficient Adaptation) — 강함.** **D22**(pretraining data composition: egocentric vs mixed — *OPEN ablation*)에 실증 데이터를 준다: "인간 ego 영상 cotraining 이 저로봇데이터에서 큰 이득, 규모보다 scene diversity"라는 결과는 egocentric-centric 가설을 지지하되, 단일 단계 cotraining 이라는 점은 staged 와 구분된다. **D23**(action representation = 연속 flow-matching head, v1=iii)와 정확히 일치하는 conditional flow matching 정책이다.
- **P1(Heterogeneous Body/Hand Action Expert) — 구조적 지지.** 핵심 발견(공유 action encoder/decoder 가 motion gap 에서 전이를 막고, *분리* 가 필수)은 **D4**(Body↔Hand 정보 공유)·**D7**(π backbone partition)의 "이질적 latent 분리" 논지를 *임베디먼트 축* 에서 재확인한다. 단 이 논문의 분리는 인간 vs 로봇 임베디먼트 분리이지 우리의 body vs hand 분리는 아니다.
- **P2(Structured Multimodal Observation Fusion) — 부분적.** image-space scale alignment + token-level fusion(CLS-token 병목 거부)은 **D8**(multi-camera spatial-geometric grounding)·flat-pooling 거부 논지와 결이 같다. 다만 본 논문은 멀티뷰 *기하 grounding* 이 아니라 단일 ego 카메라의 *스케일 정렬* 이라 P2 의 3D-consistent 임베딩 주장과는 층위가 다르다.
- **Identity 긴장/지지** — "supervision elevation 을 인간 영상에서"라는 점은 Identity 의 data-efficient adaptation 지향과 합치하나, 그리퍼-only·tactile 부재라 hand-level 접촉 elevation(차별화 주장)과는 거리가 있다. 경쟁자 함의: PiZero(=π0 계열 공유 decoder)를 명시적으로 누르는 결과라, π backbone 의 *공유 action decoder* 관행에 대한 반례로 P1/P4 비교군에 추가할 가치가 있다.

---

## ✨ 핀 논문 대비 델타

- **P0 핀 EgoDex 대비** — EgoDex(829h lab egocentric, Vision Pro 추적)는 *연출된* 동작·제한된 scene diversity 인 반면, TriHands 는 자연 동작·다양한 장면(28h)으로 *직접 head-to-head 에서 전 과제 우위* 를 보인다. "lab 대규모 > 자연 소규모"라는 암묵 가정을 깨는 새 증거.
- **P0 핀 Ego-Exo4D 대비** — TriHands 는 Ego-Exo4D 를 *재료* 로 삼되 2D 키포인트 병목을 3D model-based 추정기 + 멀티뷰 삼각측량으로 교체해 손 라벨 품질을 끌어올린 파생 데이터셋. "Ego-Exo4D 기본 3D 손은 cotraining 에 쓰기엔 부정확"이라는 점이 새롭다(Appendix A 의 라벨 비교).
- **P4 핀 Being-H0.5 대비** — Being-H0.5 가 UniHand-2.0(~35k h) 대규모 human-video pretraining 이라면, 본 논문은 *cotraining* 셋업에서 "무엇이 전이를 만드는가"를 ablation 으로 분해한다. 절대 규모가 아니라 손 품질·image scale·임베디먼트 specialization 이라는 *메커니즘* 을 지목한 점이 델타.
- **P4 baseline PiZero(π0) 대비** — π0 계열의 공유 action encoder/decoder 가 자연 동작 cotraining 에선 오히려 전이를 막는다는 반례를 제공(분리 시 5/6 과제 향상). 핀이 아니라 비교군이지만, π lineage 채택 시 *공유 decoder* 를 그대로 두면 안 된다는 구체적 경고.

---

## ⚙️ 의사결정 함의

이 논문이 맞다면 우리 cotraining/pretraining 파이프라인에서 다음이 바뀝니다:

- **action encoder/decoder 를 임베디먼트별로 untie** — 인간 ego 영상을 섞을 때 PiZero 식 공유 decoder 를 쓰지 말 것(평균 17.5% → 분리 시 41.5%). P1 D7 partition 을 "body/hand 축"뿐 아니라 "데이터 소스(human/robot) 축"으로도 분리하는 옵션을 검토.
- **CLS-token 병목 금지, token-level fusion 채택** — ViT 토큰 grid 를 단일 벡터로 pooling 하지 말고 noisy action 토큰과 공유 attention. config: 이미지 토큰 전부 유지 + 모달리티별 FFN expert(`vision_expert`/`action_expert` 분리).
- **image-space scale alignment 를 전처리 단계로 추가** — 인간/로봇 카메라 초점거리·FOV 가 다르면 $`z_{\text{robot}}=z_{\text{human}}\frac{f_{s}H_{c}}{f_{c}H_{s}}`$ 로 깊이 재설정 + extent-matched pinhole undistort. 이 정렬 없이는 전이 이득이 사실상 0.
- **데이터셋별 동일-수 독립 샘플링(= 로봇 upweight)** — 미니배치당 human/robot 동수 샘플링으로 로봇 손실을 $`\frac{N_R+N_H}{N_R}`$ 가중. sampler 를 per-dataset 균등으로 바꾸는 한 줄 변경.
- **action 정규화: 데이터셋별 mean-center + 1–99 백분위 필터 + ±1 스케일** — 두 분포의 support 를 맞추되 회전은 정규화하지 않음(SO(3) 자연 경계).
- **손 품질을 전이의 *게이팅 변수* 로 취급** — D22 corpus 결정 시 "손 라벨 품질"을 별도 축으로 기록. 단안 추정기(HaWoR류)도 RO 보단 낫지만 1초 예측 지평에서 depth 노이즈가 지배하므로, 손 추정기 품질이 corpus 가치의 상한을 정한다.
- **D22(ego vs mixed) 증거 갱신** — "scale 보다 scene diversity"가 egocentric-centric 가설을 지지. 단 *단일 단계 cotraining* 결과이므로 staged pretrain→adapt 로의 이전은 별도 ablation 필요.

---

## ⚠️ 먼저 검증할 실패 모드

우리 스택(22-DOF Sharpa 손 + tactile)으로 전이가 막힐 수 있는 이유를, 가장 싼 검사부터:

- **(가장 싼 검사) action 공간 차원 점검** — 이 논문 action 은 TCP 6-DOF + ternary grasp 다. 우리 HandExpert 출력은 손가락 관절 명령(다지 자유도). MANO→TCP retargeting 은 손가락 DOF 를 *통째로 버리므로*, 이 recipe 의 "손 전이"는 우리의 per-finger dexterity 전이로 직결되지 않는다. 우리 손 출력 공간에 MANO 관절을 보존 매핑할 수 있는지부터 확인.
- **kinematic retargeting 의 손가락 디테일 손실** — 저자도 복잡 과제에서 retargeting 의존이 발목을 잡는다고 인정. in-hand reorientation(Phase 1) 같은 접촉 풍부 과제는 retargeting 으로 표현 안 되는 손가락 미세 motion 이 본질이라, 이 cotraining 이 *그* 신호를 전이할지 의문.
- **tactile/force 부재** — recipe 는 vision+proprio 만 검증됨. P2/P3 의 접촉 모달리티(per-finger tactile 토큰)와 cotraining 이 호환되는지, 인간 영상엔 없는 tactile 스트림을 어떻게 마스킹·정렬할지 미검증(논문의 wrist-stream 마스킹과 유사한 처리가 필요).
- **image-space 정렬의 우리 카메라 적용성** — 우리 셋업(multi-cam spatial grounding, P2)은 단일 ego 카메라 스케일 정렬과 층위가 다르다. 정렬이 어긋나면 이득이 0 이 되는 민감도를, 우리 멀티뷰 셋업에서 먼저 sanity-check.
- **단일 단계 cotraining ≠ 우리 staged 레시피** — D21 은 대규모 pretrain → 소량 conservative adaptation(ConSFT) 다. 이 논문의 동수 샘플링 upweight 가 "freeze backbone + action expert 만 학습"(D19 v1) 상황에서도 같은 이득을 줄지 별도 확인 필요.

---

## 💡 컨텍스트 제안

- **P0 `catalogs/dataset.md`(👤 human 섹션) 신규 항목 후보** — TriHands(532 영상·28h·304만 우측 손 프레임, EgoExo4D 파생, 멀티뷰 삼각측량 3D 손, AgileX Piper 전이 검증). License 는 EgoExo4D 종속 ⚠️ gated 로 표기 권장. 사람이 큐레이션 판단할 항목으로만 제안합니다(파일 직접 수정 안 함).
- **P0 D24 evidence 보강** — "scene diversity > raw hours"(TriHands 5× 적은 시간에 EgoDex 전 과제 우위)는 egocentric priority axis 의 정량 근거. 핀 교체보다는 D24 rationale 의 보조 증거로 기록 검토.
- **P4 D22(OPEN) 입력** — egocentric vs mixed 결정에 "손 라벨 품질"을 *제3의 축* 으로 추가하는 것을 제안. 현재 D22 는 ego/mixed 비율만 보지만, 본 논문은 라벨 품질이 전이의 게이팅 변수임을 보임.
- **P1/P4 비교군 추가 후보** — PiZero(공유 action decoder)에 대한 본 논문의 반례를, 공유 vs 분리 decoder 논쟁(D7)의 tracked 비교군으로 둘지 검토. 핀은 아님.

> 💡 base 매핑은 `/implement-design analysis/2606.06627/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
