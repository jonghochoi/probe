# Paper Analysis — PhysisForcing: Physics Reinforced World Simulator for Robotic Manipulation

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | PhysisForcing: Physics Reinforced World Simulator for Robotic Manipulation |
| 저자 | Peiwen Zhang, Yufan Deng, Shangkun Sun, Juncheng Ma, Duomin Wang, Jonas Du, Zilin Pan, Ye Huang, Hao Liang, Songyan Huang, Ruihua Zhang, Enze Xie, Ming-Yu Liu, Daquan Zhou (DA Group, Peking University · NVIDIA 등) |
| 링크 | [arXiv:2606.28128](https://arxiv.org/abs/2606.28128) · [Website](https://dagroup-pku.github.io/PhysisForcing.github.io/) |
| 발행일 / 버전 | 2026-06 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-07-01 |
| 관련 Pillar | P5, P0 |
| 태그 | vla-arch, flow-matching, egocentric-data |

---

## 🧭 한 줄 요약 (TL;DR)

PhysisForcing 은 로봇 조작 영상 생성기의 물리적 타당성을 학습 시점(training-time)에 끌어올리는 프레임워크로, **물리 정보가 밀집한 영역(manipulator·물체·접촉부·움직임)만 골라** DiT 중간 특징에 (1) 점 궤적 연속성을 강제하는 pixel-level trajectory alignment 손실과 (2) 동결된 V-JEPA 2 인코더의 토큰 관계 행렬을 모사하는 semantic-level relational alignment 손실을 추가합니다. 추론 비용 증가 없이 R-Bench·PAI-Bench·EZS-Bench 전반과 downstream 정책 성공률까지 일관되게 개선합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 영상 생성 모델을 embodied world simulator 로 쓰려면 photorealism 만으로 부족하고, 특히 접촉이 잦은(contact-rich) 조작에서 물리적으로 타당한 동역학이 필요합니다. 그러나 일반·로봇 특화 영상 생성기 모두 불연속 궤적·물체 관통·반중력 운동 같은 물리 위반을 낸다는 것이 문제입니다.
- **기존 접근의 한계 (재구성 목적)** — 로봇 특화 world model 은 조작 데이터로 task 적합성은 높이지만 대개 reconstruction 목적으로 학습되어 물리적으로 중요한 영역과 배경 픽셀을 **균등하게(uniformly)** 취급합니다.
- **기존 접근의 한계 (기하·선호 정렬)** — depth·tracking·3D 구조 같은 기하 단서는 국소(local) 운동 일관성만 잡고, preference/reward 정렬(DPO·GRPO)은 신호가 희소하고 국소화가 약하며 사후(post-hoc) 교정이라 시각 품질을 희생할 수 있습니다.
- **본 논문의 가설** — 물리적 타당성은 본질적으로 **계층적(hierarchical)**(픽셀 수준 국소 운동 + 의미 수준 관계)이고 **국소적(localized)**(manipulator·접촉부 주변에 집중)이므로, 이 두 성질을 반영한 region-focused 계층 정렬을 학습에 주입하면 지역/전역 오류를 함께 억제할 수 있습니다.
- **왜 지금 중요한가** — Wan·Cosmos 급 대규모 diffusion 영상 백본이 로봇 world model 로 부상하는 국면에서, 추론 비용 없이 백본-불문(model-agnostic)으로 물리 정합성을 얹는 학습 레시피는 데이터 증강·정책 학습의 신뢰성을 좌우합니다.

---

## 🧩 핵심 기여

- 로봇 영상 생성의 물리적 타당성을 **계층적·영역 집중(region-focused) 정렬 문제**로 정식화하고, 그 근거로 물리 오류가 접촉부·전경(foreground)에 몰린다는 관찰을 제시합니다.
- **PhysisForcing** — 학습 시점에 physics-informative 영역을 추출하고, 그 위에서 pixel-level 궤적 정렬과 semantic-level 관계 정렬을 DiT 중간 특징에 동시에 부과하는 프레임워크를 제안합니다.
- **Physics-informative Region Extraction** — CoTracker3 밀집 궤적의 운동 크기에 depth 기반 전경 가중을 곱해 적응 임계값으로 시공간 마스크 $`\mathbf{M}^{\mathrm{phy}}`$ 를 만듭니다.
- **두 상보적 손실** — 점 궤적을 참조 궤적에 맞추는 $`\mathcal{L}^{\mathrm{phy}}_{\mathrm{pix}}`$ (국소 실패 억제)와 동결 video encoder 의 토큰 관계 행렬을 모사하는 $`\mathcal{L}^{\mathrm{phy}}_{\mathrm{sem}}`$ (전역 관계 오류 복구)가 서로 다른 오류 모드를 겨냥해 stack 됩니다.
- **세 백본·세 벤치마크 검증 + downstream** — Wan2.2-I2V-A14B / Wan2.2-TI2V-5B / Cosmos3-Nano 전반에서 개선하며, WorldArena action-planner 폐루프 성공률과 Fast-WAM 정책 성공률까지 끌어올립니다. 보조 모델은 학습에서만 쓰고 추론에서 폐기해 **추론 비용 증가 0**.

---

## 🔑 기술 키워드

- **Embodied video generation / world simulator** — 로봇 행동을 조건으로 미래 프레임을 그려내는 영상 생성 모델을 환경 시뮬레이터로 쓰는 패러다임. 본 논문이 물리 정합성을 강화하려는 대상.
- **Physics-informative region** — manipulator·조작 물체·접촉부·움직이는 부위처럼 물리 증거가 밀집한 전경 영역. 감독 신호를 이곳에 집중시키는 것이 핵심 설계.
- **Pixel-level trajectory alignment** — DiT 특징으로 예측한 점 궤적을 CoTracker3 참조 궤적에 맞추는 손실. 궤적 불연속·접촉 위반 같은 국소 오류를 억제.
- **Semantic-level relational alignment** — 동결 video encoder 의 토큰-토큰 유사도 행렬을 DiT 특징의 관계 행렬이 모사하도록 정렬. gripper–물체 결합 같은 전역 상호작용 일관성을 유도.
- **DiT (Diffusion Transformer)** — flow-matching 으로 학습되는 트랜스포머형 영상 확산 백본. 정렬 손실은 그 중간 블록(middle layer) 특징에 부과.
- **V-JEPA 2** — 픽셀이 아닌 마스킹된 시공간 특징을 예측해 학습한 self-supervised video encoder. 여기서는 관계 행렬의 semantic teacher(측정 공간)로 사용.
- **CoTracker3** — 트랜스포머 기반 점 추적기. 참조 영상에서 밀집 2D 궤적을 뽑아 pixel-level 손실의 지도(supervision)와 마스크 생성에 사용.
- **Flow matching loss** — diffusion 백본의 기본 생성 목적함수 $`\mathcal{L}_{\mathrm{FM}}`$. 두 물리 손실이 여기에 가중합으로 더해짐.
- **WorldArena action planner** — world model 을 inverse dynamics model 과 짝지어 예측 rollout 을 행동으로 디코딩해 시뮬레이터에서 폐루프 실행·평가하는 프로토콜.
- **World Action Model (Fast-WAM)** — 영상 DiT 를 백본으로 쓰는 world-action 정책. PhysisForcing 학습 백본을 drop-in 교체해 downstream 정책 성능을 측정.

---

## 🔬 방법론

### 직관

PhysisForcing 의 출발점은 단순한 관찰입니다. 생성된 로봇 영상의 물리 오류는 화면 전체에 고르게 퍼져 있지 않고 로봇 손·접촉부·움직이는 물체처럼 **전경의 좁은 영역**에 몰려 있습니다. 그런데 기존 reconstruction 학습은 배경 픽셀과 이 결정적 영역을 똑같이 취급하므로 물리 신호가 희석됩니다. 그래서 저자들은 먼저 "어디를 봐야 하는가"를 정하는 마스크를 만들고, 그 영역에만 물리 감독을 집중시킵니다.

집중할 영역이 정해지면 두 종류의 오류를 서로 다른 손실로 나눠 잡습니다. 하나는 **국소 운동** 오류(예: gripper 가 순간이동하듯 튀는 궤적 불연속)로, 이는 DiT 특징에서 각 점의 궤적을 뽑아 참조 궤적과 좌표 단위로 맞춰 억제합니다. 다른 하나는 **전역 관계** 오류(예: 밀었는데 물체가 안 움직이거나 잡은 물체가 떠내려감)로, 이는 개별 점이 아니라 영역 사이 "관계"의 문제라 좌표 손실로는 잡기 어렵습니다.

전역 관계를 위해 저자들은 이미 물체·상호작용 중심 구조를 학습한 동결 video encoder(V-JEPA 2)를 **측정 자(尺, measurement space)** 로 씁니다. 인코더가 만든 토큰 간 유사도 행렬을 정답 관계 구조로 보고, DiT 특징의 관계 행렬이 이를 닮도록 정렬합니다. 절대 특징값이 아니라 관계(행렬)를 맞추므로 두 표현 공간의 스케일 차이에 둔감합니다.

마지막으로 이 모든 보조 모델(추적기·depth·encoder)은 학습 때만 참조 영상에 돌려 타깃을 만들고 추론에서는 전부 버립니다. 따라서 배포된 생성기는 원본과 동일한 비용으로 돌면서 물리적으로 더 타당한 영상을 냅니다.

### 아키텍처

![Figure 2 — PhysisForcing 전체 구조](https://arxiv.org/html/2606.28128/figs/Fig2_Method.png)

> "Figure 2: Overall architecture of PhysisForcing Our method introduces hierarchical physics alignment during video generation training, enforcing both pixel-level motion consistency (trajectory continuity, contact dynamics) and semantic-level relational consistency (spatio-temporal relations among the robot, object, and scene)." (§3)
> (한글 해설 — 참조 영상에서 물리 마스크를 뽑고, 그 마스크가 pixel-level 궤적 정렬과 semantic-level 관계 정렬 두 갈래를 동시에 규제하는 이중 계층 구조를 시각화합니다.)

입력은 영상 $`V\in\mathbb{R}^{T\times C\times H\times W}`$ 이고, 파이프라인은 세 부분으로 나뉩니다.

- **Physics-informative Region Extraction (§3.1)** — 참조 영상에서 CoTracker3 로 밀집 궤적 $`\mathcal{P}=\{\mathbf{p}_{i}^{1:T}\}_{i=1}^{N}`$ ($`N=H\times W`$) 을 얻고, 운동 크기·전경 가중을 결합해 적응 임계값으로 시공간 마스크 $`\mathbf{M}^{\mathrm{phy}}\in\{0,1\}^{T\times H\times W}`$ 를 만듭니다.
- **Pixel-level 모듈 (§3.2)** — DiT 중간 블록 hidden feature $`\mathbf{H}^{l}`$ 를 경량 MLP $`\phi(\cdot)`$ 로 정제해 프레임별 특징 맵 $`\hat{\mathbf{F}}\in\mathbb{R}^{T\times C\times H\times W}`$ 로 reshape, 첫 프레임 특징을 query·나머지를 key 로 삼아 유사도 기대값으로 점 위치를 예측합니다.
- **Semantic-level 모듈 (§3.3)** — 같은 $`\mathbf{H}^{l}`$ 를 또 다른 MLP $`\psi(\cdot)`$ 로 동결 encoder 공간에 사영·리사이즈해 토큰 관계 행렬을 인코더의 관계 행렬에 맞춥니다.

두 손실은 모두 **하나의 중간(middle-layer) DiT 블록** 특징에 부과됩니다(§4.4 Table 6 에서 층 선택을 ablation). 저자 구현(Wan2.2-I2V-A14B 기준)에서 그 층은 block 20(width 5120)이며, encoder 는 $`32\times16\times16`$ 토큰 격자를 반환하고 DiT 특징을 같은 격자로 리샘플해 토큰을 index-정렬합니다.

### 학습 목표 / 손실

**(1) 물리 영역 추출 (§3.1).** 각 점의 국소 운동 크기는 인접 프레임 변위의 합으로 정의됩니다.

$$a_{i}=\sum_{t=1}^{T-1}\left\|\mathbf{p}_{i}^{t+1}-\mathbf{p}_{i}^{t}\right\|_{2}$$

> "where a larger $`a_{i}`$ indicates stronger local motion." (§3.1, Eq. 1)
> (한글 해설 — $`a_{i}`$ 가 클수록 그 점의 국소 운동이 강하다는 뜻이며, 이것만으로는 배경 흔들림도 잡히므로 전경 가중이 필요합니다.)

첫 프레임 depth $`D_{0}`$ 로 전경 가중 $`r_{i}`$ 와 물리 점수 $`q_{i}`$ 를 계산합니다.

$$r_{i}=\frac{1}{D_{0}(\mathbf{p}_{i}^{0})+\epsilon},\quad q_{i}=a_{i}\cdot r_{i}$$

> "A larger $`q_{i}`$ indicates a trajectory with both strong local motion and high foreground relevance." (§3.1, Eq. 2)
> (한글 해설 — 가까운(=$`D_{0}`$ 작은) 전경일수록 $`r_{i}`$ 가 커져, 운동이 강하면서 전경에 가까운 궤적이 높은 $`q_{i}`$ 를 받습니다.)

궤적별 점수의 평균을 적응 임계값으로 삼아 마스크를 만들고, 선택된 궤적을 프레임에 투영해 시공간 마스크로 rasterize 합니다.

$$\mathbf{M}^{\mathrm{phy}}_{i}=\mathbb{I}\left(q_{i}\geq\frac{1}{N}\sum_{j=1}^{N}q_{j}\right)$$

$$\mathbf{M}^{\mathrm{phy}}_{t}\left(\left\lfloor\mathbf{p}_{i}^{t}\right\rceil\right)=1,\quad\text{if }\mathbf{M}^{\mathrm{phy}}_{i}=1,\quad t=1,\dots,T$$

**(2) Pixel-level 궤적 정렬 (§3.2).** 첫 프레임 특징을 query $`\mathbf{Q}=\hat{\mathbf{F}}_{0}`$, 이후 프레임을 key $`\mathbf{K}_{t}=\hat{\mathbf{F}}_{t}`$ 로 두고, 각 query 점의 특징을 프레임 $`t`$ 의 모든 위치와 비교해 유사도 맵을 얻습니다.

$$\mathbf{s}_{i}^{t}(\mathbf{x})=\frac{\mathbf{Q}(\mathbf{p}_{i}^{0})^{\top}\mathbf{K}_{t}(\mathbf{x})}{\sqrt{C}},\quad\mathbf{x}\in\Omega$$

유사도 맵을 공간 방향으로 정규화하고 좌표 기대값으로 예측 위치를 구합니다.

$$\hat{\mathbf{p}}_{i}^{t}=\sum_{\mathbf{x}\in\Omega}\mathrm{Softmax}_{\mathbf{x}}\left(\mathbf{s}_{i}^{t}(\mathbf{x})\right)\mathbf{x}$$

> "Finally, the predicted trajectories are supervised by the reference trajectories extracted from the reference video using CoTracker3." (§3.2)
> (한글 해설 — 예측 궤적 $`\mathcal{P}_{\mathrm{pred}}`$ 를 CoTracker3 참조 궤적 $`\mathcal{P}_{\mathrm{gt}}`$ 에 맞추되, 물리 마스크로 상호작용 영역에만 손실을 건다는 것이 핵심입니다.)

$$\mathcal{L}^{\mathrm{phy}}_{\mathrm{pix}}=\frac{1}{|\mathbf{M}^{\mathrm{phy}}|}\left\|\mathbf{M}^{\mathrm{phy}}\odot\left(\mathcal{P}_{\mathrm{pred}}-\mathcal{P}_{\mathrm{gt}}\right)\right\|_{2}^{2}$$

**(3) Semantic-level 관계 정렬 (§3.3).** 동결 video encoder $`\Phi_{u}`$ 로 타깃 표현을, DiT hidden feature 를 MLP $`\psi`$ 로 사영·리사이즈해 학생 표현을 만듭니다.

$$\mathbf{F}^{u}=\Phi_{u}(\mathcal{V}),\quad\hat{\mathbf{F}}^{u}=\mathrm{Resize}\left(\psi(\mathbf{H}^{l})\right)$$

물리 마스크를 토큰 해상도로 리사이즈해 두 표현에서 같은 토큰 집합 $`\mathcal{M}`$ ($`K`$ 개)을 고르고, 각 측의 쌍별 코사인 관계 행렬을 계산합니다.

$$\hat{\mathbf{R}}(i,j)=\frac{\hat{\mathbf{F}}^{\mathcal{M}}_{i}\cdot\hat{\mathbf{F}}^{\mathcal{M}}_{j}}{\left\|\hat{\mathbf{F}}^{\mathcal{M}}_{i}\right\|_{2}\left\|\hat{\mathbf{F}}^{\mathcal{M}}_{j}\right\|_{2}},\quad\mathbf{R}(i,j)=\frac{\mathbf{F}^{\mathcal{M}}_{i}\cdot\mathbf{F}^{\mathcal{M}}_{j}}{\left\|\mathbf{F}^{\mathcal{M}}_{i}\right\|\left\|\mathbf{F}^{\mathcal{M}}_{j}\right\|}$$

두 관계 행렬의 원소별 L1 차이를 최소화합니다.

$$\mathcal{L}^{\mathrm{phy}}_{\mathrm{sem}}=\frac{1}{K^{2}}\sum_{i=1}^{K}\sum_{j=1}^{K}\left|\hat{\mathbf{R}}(i,j)-\mathbf{R}(i,j)\right|$$

**(4) 전체 목적 (§3.4).** flow matching 손실에 두 물리 손실을 가중합으로 더합니다.

$$\mathcal{L}=\mathcal{L}_{\mathrm{FM}}+\lambda_{\mathrm{pix}}\mathcal{L}^{\mathrm{phy}}_{\mathrm{pix}}+\lambda_{\mathrm{sem}}\mathcal{L}^{\mathrm{phy}}_{\mathrm{sem}}$$

> "All auxiliary models are used only during training and are discarded at inference. Thus, PhysisForcing introduces no extra inference cost." (§3.4)
> (한글 해설 — 추적기·depth·encoder 는 참조 영상에 대해서만 실행되어 타깃을 만들 뿐, 배포 모델에는 남지 않아 추론 오버헤드가 0 입니다.)

### 학습 셋업

- **데이터** — 대규모 RoVid-X 데이터셋의 필터링 부분집합. 다양한 embodiment·task·환경을 아우르는 4M 로봇 영상 클립에서 motion-score·task-level 중복 제거·clip-text 정렬 필터링으로 약 **500K 고품질 클립**을 남깁니다.
- **백본 3종** — Wan2.2-I2V-A14B(MoE, 27B 총 / 14B active), Wan2.2-TI2V-5B(단일 5B), Cosmos3-Nano(~16B MoT, Qwen3-VL-8B 기반).
- **Wan 계열 하이퍼** — 입력 $`640\times 480`$, 최대 81 프레임, 20K steps, global batch 128, AdamW, lr $`1\times 10^{-5}`$. Wan2.2-I2V-A14B 는 high-noise expert 에서 초기화해 **high-noise expert 만** 미세조정하되 전체 $`t`$ 범위에 적용(원 MoE 라우팅에서 이탈).
- **Cosmos3-Nano** — LoRA 로, 공식 image-to-video post-training 설정을 따라 $`720`$p 해상도·최대 $`189`$ 프레임에서 학습.
- **보조 모델(모두 동결)** — semantic teacher 는 V-JEPA 2 ViT-L/16(`vitl-fpc64-256`, hidden $`1024`$); 클립을 $`64\times256\times256`$ 로 리샘플해 $`32\times16\times16`$ 토큰 격자를 반환(tubelet 2, patch 16), mask 선택 토큰은 최대 $`K{=}512`$. 참조 궤적은 CoTracker3 offline, 첫 프레임에 $`25\times25`$ (625점) query 격자. 전경 가중용 depth 는 Depth-Anything-V2 ViT-L(~335M), 첫 프레임에만 실행.

---

## 📊 실험 설정과 결과

평가는 세 embodied 영상 생성 벤치마크에서 이뤄집니다: **R-Bench**(650 image-text pairs, task-oriented + embodiment-specific), **PAI-Bench** 로봇 도메인 생성 트랙(PAI-Bench-G, 174 real-world pairs), **EZS-Bench**(196 unseen robot-task-scene, 학습-독립 zero-shot OOD). 비교군은 open-source(HunyuanVideo·LTX·Wan), commercial(Wan2.6·Seedance·Veo·Kling·Sora), robotics-specific(Cosmos·DreamGen·Vidar·Abot-PhysWorld 등)입니다.

![Figure 1 — 영상 생성·정책 학습에 대한 PhysisForcing 효과](https://arxiv.org/html/2606.28128/figs/Fig1_Teaser.png)

> "Figure 1: Impacts of PhysisForcing on video generation and robotics policy learning. Our method introduces hierarchical physics alignment during video generation training, enforcing both pixel-level motion consistency and semantic-level relational coherence. This dual-level supervision enables generation of robotic manipulation videos that are not only visually realistic but also physically plausible and useful for downstream robot action modeling. In the generation benchmarks (R-Bench, PAI-Bench, EZS-Bench), PF-Cosmos denotes Cosmos3-Nano trained with PhysisForcing; the WorldArena results use the Wan2.2-TI2V-5B world model trained with PhysisForcing." (§1)
> (한글 해설 — 생성 품질(세 벤치마크)과 downstream 정책·폐루프 계획 양쪽에서 동시에 이득이 난다는 본 논문의 핵심 주장을 요약한 티저입니다.)

### R-Bench (Table 1)

세 백본 모두에서 base → vanilla finetune(ft) → PhysisForcing(PF) 순으로 개선됩니다.

| 모델 | Avg. | Tasks | Embodiments |
|---|---|---|---|
| Wan2.2-TI2V-5B (base) | 38.0 | 33.1 | — |
| Wan2.2-TI2V-5B (ft) | 44.8 | 39.6 | — |
| **+ PhysisForcing** | **47.5** | 43.4 | — |
| Wan2.2-I2V-A14B (base) | 50.7 | 38.1 | — |
| Wan2.2-I2V-A14B (ft) | 57.9 | 52.3 | — |
| **PF-Wan** | **62.0** | 56.4 | — |
| Cosmos3-Nano (base) | 58.4 | 55.0 | — |
| Cosmos3-Nano (ft) | 61.5 | 57.8 | — |
| **PF-Cosmos** | **63.8** | 58.9 | — |
| (참고) Wan2.6 (commercial 최강) | 60.7 | 54.6 | — |

> "PF-Cosmos attains the best overall score (63.8, $`+9.2\%`$ over base), surpassing all baselines including the strongest commercial model Wan2.6 (60.7), while PF-Wan reaches 62.0 ($`+22.3\%`$ over base), the second best overall, with consistent gains holding on Wan2.2-TI2V-5B as well." (§4.2, Table 1)
> (한글 해설 — PF-Cosmos 63.8 은 상용 최강 Wan2.6(60.7)를 포함한 전 baseline 을 제치는 최고 종합 점수이며, PF-Wan 62.0 은 base 대비 +22.3%(ft 대비 +7.1%)입니다.)

### PAI-Bench / EZS-Bench

> "PhysisForcing improves both backbones over vanilla finetuning (Wan2.2-I2V-A14B: $`79.9\!\rightarrow\!81.7`$; Cosmos3-Nano: $`84.0\!\rightarrow\!85.2`$). PF-Cosmos attains the best overall average (85.2), surpassing the strongest commercial model Wan2.5 (81.0) and robotics-specific baseline Abot-PhysWorld (84.9)." (§4.2)
> (한글 해설 — PAI-Bench 로봇 도메인에서 PF-Cosmos 85.2 가 상용 Wan2.5(81.0)·로봇 특화 Abot-PhysWorld(84.9)를 넘습니다.)

> "PhysisForcing again improves both backbones over vanilla finetuning (Wan2.2-I2V-A14B: $`79.0\!\rightarrow\!80.5`$; Cosmos3-Nano: $`80.3\!\rightarrow\!81.1`$), with PF-Cosmos achieving the best overall average (81.1), outperforming Abot-PhysWorld (80.3) and all other baselines." (§4.2)
> (한글 해설 — 학습-독립 zero-shot EZS-Bench(OOD)에서도 두 백본이 ft 대비 향상되고 PF-Cosmos 81.1 이 최고로, 물리 정렬이 학습 분포 밖으로도 전이됨을 시사합니다.)

### 정책 학습 / world model (Table 2·3)

PhysisForcing 로 학습한 Wan2.2-TI2V-5B 를 Fast-WAM 의 video DiT 로 drop-in 교체해 RoboTwin 2.0 6 task 를 단일 정책으로 학습, 각 200 rollouts 평가합니다.

| Task | Baseline | PhysisForcing | $`\Delta`$ |
|---|---|---|---|
| place_empty_cup | 41.5 | 63.0 | +21.5 |
| press_stapler | 49.0 | 60.0 | +11.0 |
| grab_roller | 58.5 | 63.0 | +4.5 |
| shake_bottle | 97.5 | 94.5 | -3.0 |
| adjust_bottle | 93.0 | 93.0 | 0.0 |
| stack_bowls_two | 69.5 | 63.0 | -6.5 |
| **Average** | **68.2** | **72.8** | **+4.6** |

> "As shown in Table 2, it improves the average success rate from $`68.2\%`$ to $`72.8\%`$, with the largest gains on contact-rich placing and pressing (place_empty_cup $`41.5\%\!\rightarrow\!63.0\%`$, press_stapler $`49.0\%\!\rightarrow\!60.0\%`$)." (§4.3, Table 2)
> (한글 해설 — 접촉이 많은 placing/pressing 에서 큰 이득이 나지만, shake/stack 일부 task 는 소폭 하락해 접촉-집중 감독의 편향을 드러냅니다.)

> "PhysisForcing lifts the average closed-loop success rate from $`16.0\%`$ to $`24.0\%`$, surpassing all world-model planners including the strongest baseline WoW ($`20.5\%`$)." (§4.3, Table 3)
> (한글 해설 — WorldArena action-planner 프로토콜(공유 IDM 이 예측 rollout 을 행동으로 디코딩)에서 폐루프 성공률이 16.0→24.0 으로, world model 로서의 실효성을 보입니다.)

### Ablation (Table 4·5·6)

- **성분 분해 (Table 4)** — Wan5B ft 44.8 기준 $`\mathcal{L}^{\mathrm{phy}}_{\mathrm{pix}}`$ 단독 47.2, $`\mathcal{L}^{\mathrm{phy}}_{\mathrm{sem}}`$ 단독 46.2, 결합 47.5. A14B 에서도 57.9 → (pix)60.7 / (sem)60.0 / (둘) 62.0.

> "$`\mathcal{L}^{\mathrm{phy}}_{\mathrm{pix}}`$ gives the larger single-loss gain because it directly suppresses trajectory discontinuity, the most common local failure, whereas $`\mathcal{L}^{\mathrm{phy}}_{\mathrm{sem}}`$ mainly repairs global relational errors such as broken contact, so the two target different error modes and stack." (§4.4, Table 4)
> (한글 해설 — pixel 손실은 가장 흔한 국소 실패(궤적 불연속)를, semantic 손실은 전역 관계 오류(접촉 파괴)를 서로 다르게 겨냥하므로 상보적으로 누적됩니다.)

- **영역 집중 (Table 5)** — ft 44.8 → 균등 감독(w/o region focus) 46.0 → 물리 영역 집중 47.5. 특히 Tasks 차원이 $`35.4\!\rightarrow\!38.9`$ 로 가장 크게 오릅니다. 배경·준정적 영역이 물리 신호를 희석함을 보여줍니다.
- **정렬 층 (Table 6, Wan5B, PAI 로봇 도메인)** — layer 10 = 83.9, **15 = 85.2**, 20 = 84.1, 25 = 83.2. 중간 블록이 최적(초기=얕은 appearance, 후기=노이즈 예측에 특화되어 조종 곤란).
- **학습 동역학 (Fig. 6)** — 두 손실 모두 매 checkpoint 에서 vanilla ft 를 능가하고, 20k 에서 85.2(+4.1)로 정점 뒤 완만히 하락하나 30k 에서도 +3.7 로 선두 유지.

---

## ⚖️ 한계

- **백본 능력 상한에 종속(저자 명시)** — PhysisForcing 은 미세조정 레시피라 하부 백본의 능력 천장을 물려받습니다. Wan2.2·Cosmos3 계열은 여전히 world knowledge 와 long-horizon 시간 추론이 제한적이라, 어떤 fine-tuning 도 도달 가능한 물리 타당성에 한계가 있습니다. 다만 제약이 model-agnostic 이라 더 강한 백본에서는 복리로 커질 것으로 봅니다.
- **접촉-집중 감독의 부작용(추론된 갭)** — 물리 마스크가 운동·전경에 집중하므로, 이미 잘 되던 task(shake_bottle 97.5→94.5, stack_bowls_two 69.5→63.0)에서 downstream 성공률이 오히려 떨어졌습니다. 감독 재분배가 저운동·정밀 정렬형 task 를 상대적으로 희생할 수 있음을 시사합니다.
- **참조 궤적·depth 품질 의존(추론된 갭)** — pixel 손실과 마스크는 CoTracker3·Depth-Anything-V2 출력에 좌우됩니다. 반사·투명·저텍스처·심한 가림에서 tracker/depth 가 흔들리면 마스크가 엉뚱한 영역을 선택하거나 잘못된 궤적을 정답으로 강제할 위험이 있습니다.
- **semantic teacher 표현 편향(추론된 갭)** — 관계 행렬 타깃이 V-JEPA 2 의 토큰 구조에 묶여 있어, 인코더가 잘 표현하지 못하는 상호작용(예: 미세한 손가락-물체 접촉, 도구 사용)은 semantic 손실이 감독하지 못할 수 있습니다.
- **평가 지표의 물리성 간접성(추론된 갭)** — R-Bench/PAI/EZS 점수는 물리 위반을 직접 세는 지표라기보다 종합 품질 점수라, "물리 타당성 개선"이 지표 상승의 어느 만큼을 설명하는지 분해가 제한적입니다.
- **접촉 물리의 명시적 모델 부재(추론된 갭)** — 힘·마찰·질량 같은 물리량을 명시적으로 다루지 않고 궤적 연속성과 관계 일관성이라는 **대리(proxy)** 신호로만 물리를 유도하므로, 대리와 실제 접촉 역학이 어긋나는 상황(예: 정확히 붙어 보이지만 실제로는 미끄러지는 grasp)까지 보장하지는 못합니다.

---

## ♻️ 재현성

- **코드/결과** — 프로젝트 페이지 `https://dagroup-pku.github.io/PhysisForcing.github.io/` 에 코드·추가 결과 공개 안내(구체 릴리스 범위는 페이지 확인 필요; 논문 본문상 research-only 릴리스 언급).
- **보조 모델** — 전부 공개 checkpoint: V-JEPA 2 ViT-L/16(`vitl-fpc64-256`), CoTracker3(offline), Depth-Anything-V2(ViT-L). 하이퍼(격자 25×25, K≤512, 토큰 32×16×16 등)가 Appendix A 에 명시되어 재구성 가능.
- **백본** — Wan2.2-I2V-A14B / Wan2.2-TI2V-5B 는 open-source, Cosmos3-Nano 는 NVIDIA 계열. lr·batch·steps·해상도·프레임 수가 명시됨.
- **데이터** — RoVid-X(4M) 의 필터링 부분집합(~500K). 필터 기준(motion-score·중복 제거·clip-text 정렬)은 서술되나 정확한 임계값·클립 목록은 미공개로 완전 재현에는 데이터 접근이 관건.
- **미명시** — $`\lambda_{\mathrm{pix}}`$ · $`\lambda_{\mathrm{sem}}`$ 손실 가중, $`\epsilon`$ 값, MLP $`\phi/\psi`$ 구조는 본문에 수치가 드러나지 않습니다.

---

## 🎯 관련 Pillar / Decision (P#/D#)

- **P5(World Model) — 정면 대상.** 본 논문은 action-conditioned 로봇 조작 영상 생성기를 world simulator 로 강화하는 연구로 P5 의 핵심 스코프에 정확히 놓입니다.
  - **D28(world-model role)** — 여기서 world model 은 데이터 증강용 시뮬레이터 + WorldArena action-planner + Fast-WAM 정책 백본으로 쓰입니다. P5 v1 은 "latent dynamics prior + future-prediction auxiliary(독립 planner 아님)"인데, PhysisForcing 은 **standalone 생성기/planner** 계열이라 v1 과 결이 다릅니다(P5 §3 의 raw-pixel deferred 항목에 대응).
  - **D30(prediction space)** — P5 v1 은 **latent / 3D-flow** 예측을 택하고 raw-pixel 영상 생성을 (비용상) 보류하되 eval-in-imagination 현실감용으로 tracked 상태로 둡니다. PhysisForcing 은 정확히 그 **raw-pixel 분기**의 최신 사례이며, "물리 정합을 학습에 주입"함으로써 raw-pixel 의 신뢰성 약점을 직접 겨냥합니다.
  - **D31(action conditioning)** — action-conditioned 영상/정책 실험(RoboTwin 2.0)으로 P5 v1(per-frame action-conditioned)과 정합.
  - **D32(egocentric hand-object)** — 본 논문은 3인칭 로봇 조작 중심이라 P5 가 우선하는 **egocentric 인간 영상 기반 hand-object** 축과는 어긋납니다(§4 anti-topics 의 3인칭 object-centric down-weight 에 해당). 단 손가락 수준 dexterity 가 아닌 gripper/arm 접촉이 주라 hand-centric 정체성과의 거리도 있습니다.
- **P0(Data) — 부차 연결.** RoVid-X(4M→500K) 필터링 파이프라인과 R-Bench/PAI/EZS 벤치마크 사용은 P0 의 데이터·벤치마크 스카우팅 범위(D26)와 접점이 있으나, 데이터셋·벤치마크 자체를 기여하지는 않습니다.
- **Identity 긴장/지지** — MASTER Identity 는 P5 를 "후기 단계 capability bet, hand-object·egocentric·latent/3D-flow 중심"으로 좁혀 둡니다. 본 논문은 **raw-pixel·3인칭·gripper** 축이라 정체성 우선순위와는 여러 지점에서 어긋나며, "raw-pixel 생성보다 contact-relevant latent 예측" 이라는 P5 의 명시적 우선순위와 대비되는 대안 증거로서 가치가 있습니다.
- **경쟁자 함의** — P5 §5 Tracked 의 raw-pixel 대표 핀은 **Ctrl-World**(controllable generative WM, eval-in-imagination). PhysisForcing 은 같은 raw-pixel 계열에서 "학습 시점 물리 정합"이라는 축을 추가한 경쟁·보완재입니다.

---

## ✨ 핀 논문 대비 델타

- **vs. Ctrl-World(P5 §5 raw-pixel 핀, [arXiv:2510.10125](https://arxiv.org/abs/2510.10125))** — Ctrl-World 는 raw-pixel WM 의 **제어 가능성(controllability)** 과 eval-in-imagination/데이터 증강에 방점이 있습니다. PhysisForcing 이 새로 가져오는 것은 **물리 타당성을 학습-시점 손실로 강제**하는 축(궤적 정렬 + 관계 정렬)이며, 특히 물리 신호를 접촉·전경 영역에 **국소화**한다는 점이 신규입니다.
- **vs. VLA-JEPA / ThinkJEPA(P5 §5, JEPA latent 계열)** — 이들은 V-JEPA 2 예측 임베딩을 **정책 prior/latent WM** 자체로 씁니다. PhysisForcing 은 V-JEPA 2 를 예측 백본이 아니라 **동결 semantic teacher(관계 행렬 측정 공간)** 로 재활용해, latent WM 을 만드는 대신 raw-pixel 생성기를 규제하는 데 씁니다 — 같은 인코더의 다른 용법.
- **vs. Abot-PhysWorld / MIND-V(preference·reward 정렬)** — DPO/GRPO 계열은 물리 위반을 **사후 교정**하고 신호가 희소·약국소화입니다. PhysisForcing 은 사후가 아니라 **학습 중 예방**이며, dense 한 점 궤적·토큰 관계 감독으로 국소화가 강합니다(Table 5 가 영역 집중의 이득을 입증).
- **한마디** — "raw-pixel WM 에 계층적·영역집중 물리 감독을 붙인 최초급 학습 레시피" 라는 점이 핀 대비 진짜 델타입니다.

---

## ⚙️ 의사결정 함의

- **D30 raw-pixel 분기 재평가 근거** — P5 가 raw-pixel 생성을 비용상 보류했으나, PhysisForcing 은 **추론 비용 0**(보조 모델 학습-only)으로 물리 정합을 얹을 수 있음을 보입니다. 우리가 raw-pixel eval-in-imagination 을 시험한다면, $`\mathcal{L}^{\mathrm{phy}}_{\mathrm{pix}}`$ · $`\mathcal{L}^{\mathrm{phy}}_{\mathrm{sem}}`$ 를 flow-matching 손실에 더하는 두 loss term + 물리 마스크가 구체적 채택 후보입니다.
- **semantic teacher 로 V-JEPA 2 재활용** — 우리 스택이 이미 JEPA 계열(D30) 을 tracked 하므로, V-JEPA 2 토큰 관계 행렬을 **관계 정렬 타깃**으로 쓰는 방식은 latent WM 과 별개로 즉시 이식 가능한 부품입니다. config 축: alignment 층 index(중간 블록; Table 6 에서 15 최적), $`K{\le}512`$ mask 토큰 수, 토큰 격자 $`32\times16\times16`$.
- **손실 가중 하이퍼** — 도입 시 $`\lambda_{\mathrm{pix}}`$ · $`\lambda_{\mathrm{sem}}`$ 가 핵심 튜닝 노브이나 본문 미명시라 sweep 대상. Table 4 상 pixel 손실이 단독 이득이 커 초기값을 pixel 우위로 두는 것이 합리적.
- **하지 말아야 할 것** — 마스크를 전 프레임 균등 감독으로 쓰면 이득이 47.5→46.0 로 줄어드므로(Table 5), **영역 집중**을 유지해야 함. 또한 접촉-집중 감독이 저운동 정밀 task 를 희생(Table 2 회귀)하므로 hand-centric 정밀 조작 평가를 반드시 병행.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 sanity check) 지표 vs 물리 분해** — 우리 task 에서 개선이 "물리 위반 감소"에서 오는지, 일반 화질 상승에서 오는지 먼저 분해. R-Bench 류 종합 점수가 아니라 **접촉 위반·관통·grasp 유지** 같은 물리 전용 지표로 재측정하지 않으면 전이 판단이 불가.
- **3인칭→egocentric·hand-centric 전이** — 논문은 3인칭 로봇·gripper/arm 중심. 우리의 egocentric 인간 영상·per-finger 접촉으로 옮기면, CoTracker3/Depth-Anything-V2 가 손가락 자기가림(self-occlusion)·근접 손-물체 접촉에서 무너져 마스크·궤적 품질이 급락할 수 있음. 소규모 ego 클립에 두 보조 모델만 먼저 돌려 마스크 시각화로 확인.
- **semantic teacher 미표현 상호작용** — V-JEPA 2 가 미세 손가락-물체 접촉을 토큰 관계로 잘 담지 못하면 $`\mathcal{L}^{\mathrm{phy}}_{\mathrm{sem}}`$ 이 dexterity 에 무신호. 관계 행렬을 hand-object 접촉 유무에 대해 검증(예: 접촉 프레임에서 gripper-물체 토큰 유사도가 실제로 상승하는지).
- **저운동 정밀 task 회귀** — Table 2 에서 stack/shake 가 하락. 우리의 정밀 삽입·정렬형 hand task 에서 접촉-집중 감독이 오히려 해가 될 수 있으니, 도입 전후를 정밀 task subset 에서 A/B.
- **손실 가중 민감도** — $`\lambda`$ 미명시라, 잘못 설정 시 flow-matching 을 압도해 화질/다양성 붕괴 위험. 작은 값에서 시작해 물리 지표–화질 trade-off 곡선을 먼저 그릴 것.
- **데이터 스케일 의존** — 500K 클립 규모에서의 결과라, 우리의 소규모 deploy 데이터에서 두 손실이 과적합을 악화시키지 않는지(Fig. 6 의 20k 후 하락 경향) 학습 곡선으로 조기 확인.

---

## 💡 컨텍스트 제안

- **P5 §5 Methodology base 후보로 tracking 제안** — PhysisForcing 은 P5 v1 의 latent/3D-flow 우선(D30)과 어긋나는 **raw-pixel 분기 + 학습-시점 물리 정합**의 대표 사례입니다. 핀 교체까지는 이르지 않되, Ctrl-World(raw-pixel 핀) 옆에 "물리 정합 학습 레시피(추론 비용 0)" 참고 항목으로 §5 methodology base 에 올릴 것을 사람에게 제안합니다. (context 파일은 수정하지 않았습니다.)
- **D30 deferred trigger 관찰 포인트** — "raw-pixel 을 언제 다시 볼 것인가"의 트리거로, 본 논문의 "추론 비용 0 물리 정합" 증거를 기록해 두면 향후 eval-in-imagination 실험 시점 결정에 유용합니다.

---

> 💡 base 매핑은 `/implement-design analysis/2606.28128/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
