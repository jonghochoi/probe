# Paper Analysis — OSCAR: Omni-Embodiment Action-Conditioned World Model for Robotics

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | OSCAR: Omni-Embodiment Action-Conditioned World Model for Robotics |
| 저자 | Zhuoyuan Wu, Jun Gao |
| 링크 | [arXiv:2606.04463](https://arxiv.org/abs/2606.04463) · [HuggingFace](https://huggingface.co/zywu2115/OSCAR-2B) · [Website](https://wuzy2115.github.io/oscar-project-page/) |
| 발행일 / 버전 | 2026-06-03 (v1) · 2026-06-04 (v2) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-11 |
| 관련 Pillar | P5, P0 |
| 태그 | egocentric-data, flow-matching, dataset |
| 카탈로그 | benchmark/sim/OSCAR, dataset/robot/OSCAR_robot, dataset/human/OSCAR_human |

---

## 🧭 한 줄 요약 (TL;DR)

OSCAR 는 2D kinematic skeleton 렌더링을 단일 conditioning 표현으로 써서 4종 로봇 팔과 사람 손(MANO)을 한 모델에 담는 action-conditioned 비디오 world model 로, Cosmos-Predict2.5-2B 를 단일 GH200 GPU 에서 파인튜닝해 14B 급 baseline 을 능가하고, RoboArena 정책 순위를 실제 배포 성공률과 강하게 상관되도록 가상 평가(eval-in-imagination)합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 로봇 정책을 실제 하드웨어 없이 평가·강화학습할 수 있는, 액션을 정밀하게 따르면서 다양한 embodiment 로 일반화되는 action-conditioned 비디오 world model 을 만드는 것입니다.
- **기존 접근의 한계** — Latent-action 계열은 다중 embodiment 를 다루지만 압축된 latent 에서 시공간 모션을 추론해야 해 action following 이 부정확하고, dense pointmap/mesh 같은 explicit 렌더링은 정밀하지만 embodiment 별 appearance 에 과적합해 OOD 평가에서 무너집니다.
- **본 논문의 가설** — kinematic chain 만 의존하고 텍스처가 없는 2D skeleton 렌더링이면 정밀도와 cross-embodiment 일반화를 동시에 잡을 수 있고, embodiment 교체는 kinematic spec 만 갈아끼우면 된다는 것입니다.
- **왜 지금 중요한가** — 실로봇 정책 평가는 느리고 비싸며, RoboArena 같은 분산 실평가 leaderboard 가 등장한 지금 그것을 가상으로 재현하면 정책 개발 iteration 비용을 크게 줄일 수 있습니다.
- **데이터 측면 동기** — 기존 로봇 데이터셋은 환경·태스크 분포가 좁고(AgiBot 100만 클립도 거의 같은 장면 반복) 필터링이 안 돼 있어, 대규모로 큐레이션·필터·dedup 한 깨끗한 joint-training 코퍼스가 일반화의 전제 조건입니다.

---

## 🧩 핵심 기여

- **통일 conditioning 표현** — 2D kinematic skeleton 렌더링을 robot arm 과 human hand(MANO) 모두에 공통으로 쓰는 conditioning schema 로 채택해, 하나의 표현으로 4종 로봇 + 사람 손을 단일 모델에 담습니다.
- **대규모 표준화 데이터 파이프라인** — 5개 로봇 + 2개 egocentric human 데이터셋(원본 약 216만 episode)을 curate → filter → semantic dedup → caption 하는 4단계 파이프라인으로 18.0657만 episode 의 깨끗한 joint-training 셋을 만듭니다.
- **저자원 SOTA** — Cosmos-Predict2.5-2B 를 단일 GH200 GPU 에서 파인튜닝해, 14B 파라미터(Kinema4D)나 더 많은 GPU 를 쓰는 baseline 들을 action following·appearance·motion consistency 전반에서 능가합니다.
- **가상 정책 평가 실증** — OSCAR rollout 으로 RoboArena 의 7개 DROID generalist 정책을 평가했을 때 실제 배포 성공률·순위와 강한 상관(Pearson, MMRV)을 보여 eval-in-imagination 의 실효성을 입증합니다.
- **human→robot positive transfer** — 사람 egocentric 데이터를 섞어 학습하면 로봇-only 대비 일관되게 성능이 오르며, 로봇-only 에서 warm-start 하면 수렴이 빨라짐을 ablation 으로 보입니다.

---

## 🔑 기술 키워드

- **Action-conditioned world model** — 주어진 액션 시퀀스에 조건부로 미래 비디오 프레임(=환경의 다음 상태)을 예측하는 모델. OSCAR 의 본체로, 정책의 액션 결과를 가상으로 굴려 평가에 쓰입니다.
- **2D kinematic skeleton rendering** — URDF/MANO 의 kinematic tree 를 카메라로 투영해 검은 캔버스 위에 선·점으로만 그린 텍스처 없는 렌더링. embodiment 불변 conditioning 신호이자 이 논문의 핵심 표현입니다.
- **Rectified flow** — 노이즈 $`\epsilon`$ 와 타깃 latent $`z_0`$ 사이 속도장 $`v_\theta`$ 를 직선 보간으로 예측하도록 학습하는 flow-matching 목적식. Cosmos-Predict2.5 DiT 의 학습 손실입니다.
- **DiT (Diffusion Transformer)** — latent 패치를 토큰화해 denoise 하는 트랜스포머 백본. 여기서는 skeleton latent 와 noisy 비디오 latent 를 합쳐 입력받습니다.
- **WAN 2.1 VAE** — $`H{\times}W`$ 비디오를 spatio-temporal latent 으로 압축하는 video VAE. 타깃 비디오와 skeleton 을 같은 VAE 로 인코딩해 shape 를 정렬합니다.
- **MANO hand model** — 사람 손을 위한 파라메트릭 메시/토폴로지 모델. 로봇 URDF 자리에 $`(M,q_t,o_k)`$ 만 MANO 로 교체하면 동일 렌더링 파이프라인이 사람 손에도 적용됩니다.
- **Cross-embodiment conditioning** — 하나의 conditioning 인터페이스로 서로 다른 로봇/사람을 다루는 능력. skeleton 은 kinematic spec 교체만으로 이를 달성합니다.
- **Eval-in-imagination (virtual policy evaluation)** — 생성된 비디오 world 안에서 정책을 굴려 성공률·순위를 매기는 평가 패러다임. OSCAR 를 RoboArena 평가 proxy 로 쓰는 것이 그 사례입니다.
- **MMRV / Pearson r** — 가상 평가 순위·성공률이 실제와 얼마나 일치하는지 재는 rank-fidelity(MMRV↓, Spearman $`\rho\uparrow`$) / correlation($`r\uparrow`$) 지표. 가상 평가의 신뢰도를 정량화합니다.
- **Semantic deduplication** — SigLIP 시각 클러스터링 + trajectory RMS 검증의 2단계로 장면·모션이 모두 비슷한 클립만 중복으로 제거하는 절차. 다양성 보존이 목적입니다.

---

## 🔬 방법론

### 직관

OSCAR 의 출발점은 "정책을 평가하려면 정책이 낸 액션이 화면 어디서·언제 무엇을 일으키는지 비디오가 정확히 따라 그려야 한다"는 요구입니다. 문제는 액션을 비디오에 어떻게 주입하느냐인데, 기존엔 두 갈래가 있었습니다. 액션을 학습된 latent 한 덩어리로 압축해 넣으면 여러 로봇을 다룰 수 있지만 모델이 그 압축된 신호에서 정밀한 시공간 모션을 역추론해야 해 부정확하고, 반대로 로봇 메시·pointmap 을 픽셀 정렬해 그려 넣으면 정밀하지만 특정 로봇의 외형에 묶여 다른 로봇으로 못 넘어갑니다.

OSCAR 의 해법은 그 중간 — kinematic tree(관절 골격)를 카메라로 투영해 검은 배경 위에 선과 점으로만 그린 **skeleton 렌더링**입니다. 텍스처가 없으므로 모델은 "이 골격이 이렇게 움직이면 실제 로봇은 이렇게 움직인다"는 운동학↔외형 관계를 명시적으로 배워야 하고, 외형은 첫 RGB 프레임이 따로 고정해 주므로 골격은 오로지 모션만 지시합니다. 결정적으로 골격은 kinematic spec 만 갈아끼우면 Franka·KUKA·AgiBot·HSR 은 물론 사람 손(MANO)까지 같은 표현으로 그릴 수 있어, 사람 egocentric 비디오를 학습 데이터로 끌어올 길이 열립니다.

구현은 거대한 사전학습 비디오 모델(Cosmos-Predict2.5-2B)에 skeleton 비디오를 두 번째 RGB 스트림으로 frame-by-frame 정렬해 넣는 가벼운 파인튜닝입니다. 두 비디오(타깃, skeleton)를 같은 VAE 로 인코딩하고, 같은 shape 의 두 latent 를 토큰으로 임베딩해 더한 뒤 DiT 가 denoise 합니다. 이 단순함 덕에 단일 GH200 한 장으로 학습이 됩니다.

나머지 절반은 데이터입니다. 골격 conditioning 이 일반화하려면 모델이 다양한 장면·태스크·embodiment 를 봐야 하므로, 216만 개 원본 클립을 길이·정적카메라·유의미한 액션·골격 가시성으로 거르고, 시각+궤적 2단계로 의미적 중복을 제거해 18만 개의 다양성 높은 코퍼스로 압축합니다.

### 아키텍처

![Figure 2 — Method overview](https://arxiv.org/html/2606.04463/x3.png)

> "Figure 2: Method overview. OSCAR consists of three components: (1) Condition encoding encodes the first frame $`I_0`$ and rendered skeleton $`S_{1:T}`$ into latents using VAE; (2) Conditioning injection combines the skeleton latent with the noisy video latent; and (3) Video generation, where a DiT denoises the tokens and a VAE decoder decodes the final video." (§3)
> (한글 해설 — 첫 프레임과 skeleton 시퀀스를 같은 VAE 로 latent 화하고, skeleton latent 를 noisy 비디오 latent 와 합쳐 DiT 로 denoise 하는 3단계 구성이 OSCAR 의 전체 골격입니다.)

**Preliminaries (백본).** OSCAR 는 2B video DiT 인 Cosmos-Predict2.5 를 rectified-flow 목적으로 학습한 것 위에 올립니다.

> "We build on Cosmos-Predict2.5 [6], a 2B video Diffusion Transformer (DiT) trained with a rectified-flow objective. A WAN 2.1 VAE [22] first encodes an $`H{\times}W`$ video $`V_{1:T}`$ into a spatio-temporal latent $`z\in\mathbb{R}^{T^{\prime}\times H^{\prime}\times W^{\prime}\times d}`$." (§3.1)
> (한글 해설 — WAN 2.1 VAE 가 비디오를 시공간 latent 으로 압축하고, DiT 가 그 latent 패치를 denoise 하는 표준 video diffusion 스택을 그대로 백본으로 씁니다.)

image conditioning 시 Cosmos 는 첫 프레임을 고정합니다 — 매 denoising step 마다 첫 시간 위치의 latent 를 $`I_0`$ 의 clean VAE 인코딩으로 덮어쓰고 미래 프레임만 denoise 합니다. 이것이 외형을 첫 프레임에 앵커링하는 메커니즘입니다.

**Skeleton 렌더링.** URDF 모델 $`M`$ 의 kinematic tree $`(\mathcal{V}(M),\mathcal{E}(M))`$ 에서, 시각 $`t`$ 의 관절 구성 $`q_t`$ 에 forward kinematics 를 적용해 링크별 SE(3) pose 를 얻습니다.

$$\big\lbrace T_{k,t}\big\rbrace_{k=1}^{K}\;=\;\mathrm{FK}(q_{t},\,M)$$

각 링크의 canonical 점 $`o_k`$ 를 카메라 intrinsic $`K_{\mathrm{cam}}`$ 와 extrinsic $`T^{\mathrm{cam}}_{\mathrm{world}}`$ 로 픽셀에 투영합니다.

$$\big(u_{k,t},\,v_{k,t}\big)\;=\;\pi\!\Big(K_{\mathrm{cam}},\;T^{\mathrm{cam}}_{\mathrm{world}}\,T_{k,t}\,o_{k}\Big)$$

여기서 $`\pi`$ 는 표준 perspective projection 입니다. 투영된 kinematic tree 를 검은 캔버스에 rasterise 합니다.

$$S_{t}\;=\;\mathrm{Rasterise}\!\Big(\big\lbrace(u_{k,t},\,v_{k,t})\big\rbrace_{k=1}^{K},\;\mathcal{E}(M)\Big)$$

> "$`\mathrm{Rasterise}(\cdot)`$ operates entirely in pixel space: it draws a line segment between the projected endpoints of each edge in $`\mathcal{E}(M)`$ and a small filled circle at every projected vertex $`(u_{k,t},v_{k,t})`$. All other pixels remain black." (§3.2)
> (한글 해설 — 각 edge 는 선분, 각 vertex 는 작은 원으로만 그리고 나머지는 전부 검정 — 이 "가장 싼 기하 정보"가 텍스처 없이 모션만 지시하는 핵심입니다. gripper 개폐 상태도 visual indicator 로 함께 그립니다.)

**Conditioning Injection.** skeleton 시퀀스 $`S_{1:T}`$ 를 타깃과 frame-by-frame 정렬된 두 번째 RGB 비디오 스트림으로 DiT 에 줍니다. 타깃과 같은 WAN 2.1 VAE 로 skeleton latent $`z^s`$ 를 만들어(타깃 latent $`z^v_t`$ 와 동일 shape), 두 latent 를 각각 patch embedder $`\mathrm{PE}_v`$ / $`\mathrm{PE}_s`$ 로 DiT hidden 차원에 임베딩한 뒤 **토큰 텐서를 합산**해 denoising 입력으로 넣습니다.

**Extension to Human Hands.** $`S_{1:T}`$ 가 2D 관절 투영만 담으므로 같은 표현을 사람 손에 그대로 씁니다 — kinematic triple $`(M,q_t,o_k)`$ 만 MANO 로 교체합니다.

$$S^{\mathrm{human}}_{t}\;=\;\mathrm{Rasterise}\!\Big(\big\lbrace\pi\!\big(K_{\mathrm{cam}},\,T^{\mathrm{cam}}_{\mathrm{world}}\,T^{\mathrm{MANO}}_{k,t}\,o_{k}^{\mathrm{MANO}}\big)\big\rbrace_{k},\;\mathcal{E}(M^{\mathrm{MANO}})\Big)$$

> "Although a five-finger hand has more DoFs than a two-jaw gripper, both are rendered into the same 2D line drawings; the skeleton therefore constrains the coarse motion, while the pretrained video prior fills in plausible fine-grained visual details." (§3.2)
> (한글 해설 — 5지 손과 2조 gripper 의 DoF 차이는 둘 다 같은 2D 선화로 환원돼 사라지고, 골격은 거친 모션만 제약하며 세부 디테일은 사전학습 prior 가 채웁니다. 이로써 사람 egocentric 데모를 추가 학습셋으로 흡수합니다.)

![Figure 3 — Skeleton overlays for the eight training sources](https://arxiv.org/html/2606.04463/x4.png)

> "Figure 3: Skeleton overlays at video frames for the eight training sources. Each block shows four episodes from one source. Top row: DROID, RH20T-cfg5, RH20T-cfg7, InternData (four robot recordings). Bottom row: AgiBot G1, AIROA-MoMa, EgoDex, EPIC-Kitchens (humanoid and two human MANO sources)." (§3.2)
> (한글 해설 — 동일한 골격 렌더링이 4종 로봇과 2종 사람 손 소스에 모두 일관되게 입혀짐을 보여, "kinematic spec 만 교체"라는 cross-embodiment 주장을 시각화합니다.)

### 학습 목표 / 손실

학습 손실은 백본의 rectified-flow 목적식 그대로입니다 (Eq. 1):

$$\mathcal{L}_{\mathrm{RF}}\;=\;\mathbb{E}_{t,\,z_{0},\,\epsilon}\,\big\Vert v_{\theta}(z_{t},\,t,\,c)-(\epsilon-z_{0})\big\Vert_{2}^{2},\qquad z_{t}=(1-t)\,z_{0}+t\,\epsilon$$

> "The model is trained to predict a velocity field $`v_{\theta}`$ between the noise $`\epsilon\sim\mathcal{N}(0,I)`$ and the target latent $`z_{0}`$" (§3.1)
> (한글 해설 — $`z_t`$ 는 clean latent $`z_0`$ 와 노이즈 $`\epsilon`$ 의 선형 보간이고, 모델은 둘 사이 속도장 $`\epsilon-z_0`$ 를 예측합니다. $`c`$ 는 조건으로, OSCAR 에선 첫 프레임 + skeleton 토큰이 그 자리를 채웁니다. 별도의 액션-정렬 보조손실 없이 conditioning 주입만으로 액션을 따르게 한다는 점이 설계상 단순함의 핵심입니다.)

### 학습 셋업

> "We finetune from the pretrained Cosmos-Predict2.5-2B [6] checkpoint with AdamW [48] at learning rate $`3{\times}10^{-5}`$ and batch size $`16`$. Timesteps are sampled from a logit-normal distribution with reweighting, and we use shift parameter $`5`$." (§A.3)
> (한글 해설 — 사전학습 체크포인트에서 AdamW, lr $`3{\times}10^{-5}`$, batch 16 으로 파인튜닝하고, timestep 은 logit-normal + shift 5 로 샘플링합니다.)

- **embodiment 균형** — frequency-tempered weight $`w_{i}\propto n_{\mathrm{frames},i}^{1/T}`$ ($`T{=}3`$) 로 작은 소스를 per-source 계수 튜닝 없이 upweight 합니다.
- **window 샘플링** — 각 81-frame 학습 window 의 시작 프레임을 grasp/release 이벤트 쪽으로 편향 — open/close binary 신호(로봇 gripper openness, 사람은 정규화된 fingertip flexion)의 midpoint crossing 위에 trapezoid prior 를 둡니다.
- **classifier-free guidance** — 학습 중 확률 0.2 로 $`S_{1:T}`$ 를 zeros 로 대체하고, inference 시 guidance scale $`w{=}6`$ 을 씁니다.
- **2-stage 스케줄** — Stage 1 은 4종 로봇 embodiment 로 15k iteration, Stage 2 는 로봇+사람 전체 혼합으로 이어서 학습합니다.
- **하드웨어** — 단일 NVIDIA GH200 GPU.

**Latent-action baseline pathway (ablation 용, §A.4).** Table 3 의 "Latent action" 행은 Cosmos-Predict2.5 의 latent-action 조건 생성을 따릅니다. 각 팔을 7-D(3 translation + 3 Euler rotation + 1 gripper)로 표현하고, 직전 프레임 local 좌표계에서 frame-to-frame 차분을 취해(translation·rotation delta 를 ×20 스케일) 상태를 액션으로 변환합니다. bimanual(AgiBot G1)은 좌·우 7-D 를 concat, single-arm 은 앞 7-D 만 채우고 나머지 7-D 는 0 으로 둔 14-D 통합 벡터를 씁니다. 81-frame 당 80 transition → $`(80,14)`$ 텐서를 1120-D 로 flatten 해 두 MLP(GELU hidden width $`4D`$, $`D{=}2048`$)로 $`D`$-차원· $`3D`$-차원 토큰을 만들고, 전자는 timestep embedding 에, 후자는 adaLN modulation 신호에 매 프레임 더합니다.

---

## 📊 실험 설정과 결과

**셋업.** Cosmos-Predict2.5-2B 를 2-stage 로 파인튜닝하고, 4종 embodiment(Franka Panda, KUKA iiwa, AgiBot G1, Toyota HSR) × 6개 데이터셋에서 뽑은 200 클립 self-curated 벤치마크로 평가합니다. 7개 baseline 을 conditioning 방식별 — text-only(TesserAct, Cosmos-Predict2.5), latent-action(IRASim, Ctrl-World, EnerVerse-AC), explicit-geometry(Genie Envisioner, Kinema4D) — 로 비교하며, 공정성을 위해 모든 지표를 첫 49 프레임에서 Kinema4D 프로토콜대로 같은 GH200 위에서 측정합니다.

**Table 1 — 데이터 파이프라인 통계 (episode 수).**

| Source | Embodiment | Public | Filtered |
|---|---|---|---|
| RH20T (cfg5) | Franka Panda | 2,241 | 1,261 |
| RH20T (cfg7) | KUKA iiwa | — | — |
| InternData-A1 | Franka Panda | 630,000 | 2,233 |
| DROID | Franka Panda | 76,000 | 21,904 |
| AgiBot-Beta | AgiBot G1 | 1,003,672 | 65,720 |
| AIROA-MoMa | Toyota HSR | 25,469 | 3,712 |
| **Robot subtotal** | | **1,737,382** | **94,830** |
| EgoDex | human hand | 338,000 | 78,273 |
| EPIC-Kitchens | human hand | 89,977 | 7,554 |
| **Human subtotal** | | **427,977** | **85,827** |
| **Total** | | **2,165,359** | **180,657** |

> "After processing, we filtered out 180,657 episodes out of 2,165,359 source videos" (§4)
> (한글 해설 — 216.5만 원본 → 18.07만 episode 로 압축. 필터는 길이≥70프레임 / 정적 카메라 / 유의미한 액션 / 골격 가시성 4종이고, dedup 은 SigLIP cosine ≥0.95 클러스터링 후 64-step trajectory RMS 가 adaptive threshold 미만인 쌍만 중복 처리합니다.)

**Table 2 — baseline 정량 비교 (4 embodiment 평균).** OSCAR 는 2B 임에도 대부분 지표에서 최고/차상위입니다.

| Method | PSNR↑ | SSIM↑ | LPIPS↓ | tLPIPS↓ | FVD↓ | FID↓ | L2_latent↓ | FPS↑ |
|---|---|---|---|---|---|---|---|---|
| Cosmos-Predict2.5 | 14.78 | 0.563 | 0.370 | 0.022 | 18.01 | 47.59 | 0.435 | 0.292 |
| TesserAct | 16.26 | 0.730 | 0.277 | 0.055 | 24.50 | 51.90 | 0.364 | 0.343 |
| IRASim | 6.48 | 0.088 | 0.909 | 0.606 | 411.42 | 394.10 | 2.453 | 2.330 |
| Ctrl-World | 19.06 | 0.705 | 0.321 | 0.042 | 28.90 | 53.33 | 0.292 | 1.631 |
| EnerVerse-AC | 20.47 | 0.746 | 0.223 | 0.021 | 33.70 | 38.23 | 0.197 | 1.900 |
| Genie Envisioner | 23.29 | 0.838 | 0.140 | 0.007 | 15.37 | 22.92 | 0.129 | 1.382 |
| Kinema4D (14B) | 17.68 | 0.741 | 0.198 | 0.021 | 17.07 | 37.16 | 0.233 | 0.089 |
| **OSCAR (Ours, 2B)** | **24.24** | **0.846** | **0.094** | 0.015 | **7.08** | **15.07** | **0.096** | **2.214** |

> "Overall, OSCAR ranks best or second-best on most metrics and outperforms the 14B-parameter Kinema4D (OSCAR is only 2B)." (§5.2, Table 2)
> (한글 해설 — OSCAR 가 PSNR/SSIM/LPIPS/FVD/FID/L2_latent/FPS 에서 최고이고 tLPIPS 0.015 는 Genie Envisioner 0.007 다음입니다. 저자 3관찰: (i) text-only 가 액션을 정밀 기술 못해 최약, (ii) latent-action 은 학습 embodiment 에 갇혀 bimanual↔single-arm 전이 시 OOD, (iii) explicit·픽셀정렬 guidance 가 최강이며 dense pointmap 은 in-dist 과적합, skeleton 이 정확도/일반화 trade-off 최적.)

![Figure 4 — Qualitative comparison on two embodiments](https://arxiv.org/html/2606.04463/x12.png)

> "Figure 4: Qualitative comparison of action-conditioned video generation on two embodiments. Compared with five baselines, our method achieved much better visual quality with precise action following." (§5.2)
> (한글 해설 — AgiBot G1·DROID 두 embodiment 에서 5개 baseline 대비 OSCAR 의 시각 품질·action following 우위를 정성적으로 보여, Table 2 의 정량 우위를 픽셀 수준에서 뒷받침합니다.)

**Table 3 — ablation (conditioning 표현 · 데이터 구성).** 상단 블록(robot-only, 동일 데이터)은 conditioning 만, 하단 블록(동일 skeleton)은 사람 데이터 투입 시점만 바꿉니다.

| Aspect | Variant | PSNR↑ | SSIM↑ | LPIPS↓ | tLPIPS↓ | FVD↓ | FID↓ | L2_latent↓ |
|---|---|---|---|---|---|---|---|---|
| Condition | Latent action | 19.22 | 0.784 | 0.170 | 0.018 | 12.03 | 26.11 | 0.205 |
| Condition | Mesh rendering | 23.11 | 0.831 | 0.106 | 0.013 | 7.89 | 16.38 | 0.109 |
| Condition | Skeleton (canonical)⋆ | 23.48 | 0.832 | 0.106 | 0.015 | 7.69 | 16.37 | 0.117 |
| Data mix | +Human, from beginning | 23.87 | 0.842 | 0.097 | 0.014 | 7.65 | 15.72 | 0.100 |
| Data mix | +Human, warm-start⋆ | 24.24 | 0.846 | 0.094 | 0.015 | 7.08 | 15.07 | 0.096 |

> "Mesh and skeleton are statistically indistinguishable across all seven metrics, but mesh depends on robot-specific URDF assets. We choose skeleton rendering as it allows us to incorporate human data." (§5.3)
> (한글 해설 — conditioning ablation 의 함의: latent-action 은 액션을 못 따르고(모든 지표 열위), mesh 와 skeleton 은 7개 지표에서 통계적으로 구분 불가지만 mesh 는 robot-specific URLF 자산에 의존하므로, "사람 데이터를 흡수할 수 있다"는 점이 skeleton 선택의 결정적 이유입니다 — 정량 동률을 깨는 건 일반화 가능성입니다.)

> "Adding human data into the training data mixture consistently improves the performance over robot-only training, indicating positive transfer from human to robots. Moreover, when continuing from the robot-only model, warm-starting accelerates model convergence." (§5.3, Table 3)
> (한글 해설 — 데이터 ablation 의 함의: 사람 데이터 투입은 로봇-only(skeleton 23.48 PSNR) 대비 항상 개선되고(from-beginning 23.87 → warm-start 24.24), 로봇-only 에서 warm-start 하는 편이 처음부터 섞는 것보다 우수해 최종 채택됩니다 — human→robot positive transfer 의 직접 증거입니다.)

**Table 4 — 정책 평가 (RoboArena, 65 session × 7 policy).** OSCAR rollout 의 정책 순위·성공률을 실제와 비교합니다.

| Condition | MMRV ↓ | ρ ↑ | r ↑ | SISR_Δ (pp) ↓ |
|---|---|---|---|---|
| Latent action | 1.429 | +0.643 | **+0.867** | 1.98 |
| Mesh | 0.714 | +0.679 | +0.781 | 3.04 |
| **Skeleton** | **0.571** | **+0.750** | +0.852 | **1.73** |

> "For each episode, we autoregressively roll out OSCAR from the recorded first frame and the given robot action. We then prompt GPT-5 to evaluate the success rate for each episode and compute its Pearson correlation ($`r\uparrow`$) ... Our skeleton rendering provides the strongest correlation with the real-world deployment." (§5.4, Table 4)
> (한글 해설 — 7개 DROID 정책($`\pi_0`$-flow, $`\pi_0`$-FAST, PG-flow/FSQ/FAST/FAST+/Bin)을 autoregressive rollout → GPT-5(gpt-5-2025-08-07, high reasoning, 32프레임 512×288)로 성공 채점·pairwise 1,365 preference → Bradley–Terry. skeleton 이 MMRV 0.571·Spearman +0.750·SISR_Δ 1.73pp 로 rank fidelity 최강이며, Pearson r 만 latent-action(+0.867)이 근소 우위입니다. MMRV 범위는 $`[0,6]`$, SISR_Δ 는 실/예측 per-policy 성공률의 평균절대오차입니다.)

---

## ⚖️ 한계

- **카메라·kinematic 캘리브레이션 의존 (저자 명시)** — 데이터 규모가 per-dataset 카메라 intrinsic/extrinsic·kinematic 주석 품질에 묶입니다. 캘리브레이션 오차는 곧 skeleton↔RGB 정렬 오차로 직결돼, 신뢰 가능한 학습 데이터로 변환 가능한 raw 비디오의 양 자체를 제한합니다 — 데이터 파이프라인의 "정적 카메라만 유지" 필터(camera motion 은 future work 로 미룸)도 같은 뿌리의 제약입니다.
- **2B 백본 상한 (저자 명시)** — 2B 백본만 쓰므로 더 큰 백본은 fidelity·일반화를 더 올릴 수 있으나 더 많은 compute 가 필요합니다. 즉 현 SOTA 는 "저자원에서의 SOTA"이며 scaling 곡선의 끝이 아닙니다.
- **VLM-as-judge 평가의 순환성 (추론된 갭)** — 정책 성공률 채점·순위가 GPT-5 한 모델에 의존합니다. world model 이 만든 비디오를 또 다른 LLM 이 채점하는 구조라, world model 의 환각(없는 성공)과 judge 의 오판이 같은 방향으로 정렬되면 상관이 인위적으로 부풀 수 있고, judge 모델 교체 시 재현성이 흔들립니다.
- **open-loop autoregressive rollout (추론된 갭)** — 평가가 기록된 첫 프레임 + 주어진 액션으로 autoregressive 하게 굴러가는 open-loop 입니다. 정책-환경 closed-loop 상호작용(정책이 생성된 관측에 반응해 다음 액션을 내는)을 닫지 않으므로, 실제 배포에서 누적되는 폐루프 오차 동역학을 완전히 재현하진 못합니다.
- **skeleton 의 표현 손실 (추론된 갭)** — skeleton 은 텍스처·접촉력·물체 변형을 담지 않습니다. 골격이 거친 모션을 제약하고 나머지는 사전학습 prior 가 "그럴듯하게" 채우는 구조라, 미세 접촉(grasp 안정성, in-hand 재배치)의 물리적 정확성은 prior 의 환각에 맡겨집니다 — 정밀 dexterous 평가에서 약점이 될 수 있습니다.
- **정적 장면·짧은 horizon (추론된 갭)** — 49프레임에서 지표를 재고 정적 카메라만 학습하므로, 긴 horizon·이동 카메라·동적 배경에서의 일관성은 미검증입니다.

---

## ♻️ 재현성

- **코드/데이터/체크포인트** — 저자가 "We release code, data, and trained checkpoints; see our project page for more details" 로 전면 공개를 명시합니다. project page: <https://wuzy2115.github.io/oscar-project-page/>, 학습 체크포인트는 HuggingFace 에 공개: <https://huggingface.co/zywu2115/OSCAR-2B> (OSCAR-2B, Apache-2.0).
- **공개 데이터셋(companion)** — 파이프라인이 큐레이션·필터·dedup 후 OSCAR 통일 conditioning(skeleton overlay)으로 re-render 한 학습 코퍼스를 두 split 으로 HuggingFace 에 공개합니다: robot split <https://huggingface.co/datasets/zywu2115/OSCAR_robot> (다중 embodiment 로봇 teleoperation), human split <https://huggingface.co/datasets/zywu2115/OSCAR_human> (egocentric MANO hand). 둘 다 `license: other`, `arxiv:2606.04463` 태그.
- **백본** — Cosmos-Predict2.5-2B (공개 사전학습 체크포인트), WAN 2.1 VAE, SigLIP, Qwen3-VL-30B-A3B-Instruct(captioning), MoGe-v2 / CtRNet-X(카메라 추정), GPT-5(gpt-5-2025-08-07, 평가 judge) 등 외부 모델 의존이 명확히 기재됩니다.
- **데이터 소스** — DROID, RH20T(cfg5/cfg7), InternData-A1, AgiBot-Beta, AIROA-MoMa, EgoDex, EPIC-Kitchens 모두 공개 데이터셋 (asset license 는 §A.11).
- **하드웨어** — 학습·timing 모두 단일 NVIDIA GH200 GPU 로 명시돼 재현 진입장벽이 낮습니다.
- **하이퍼파라미터** — AdamW lr $`3{\times}10^{-5}`$, batch 16, logit-normal timestep + shift 5, CFG drop 0.2 / scale 6, 2-stage(15k + 혼합) 등 핵심 값이 §A.3 에 기재됩니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P5(World Model) — primary.** OSCAR 는 action-conditioned 비디오 world model 그 자체로 P5 의 핵심 표적입니다.
  - **D28(world-model 역할)** — OSCAR 는 **eval-in-imagination / 정책 순위 평가** 역할의 정면 사례입니다. P5 v1 은 "latent dynamics prior + future-prediction auxiliary"를 택하고 eval-in-imagination 을 deferred 로 두었는데, OSCAR 는 그 deferred 역할이 RoboArena 상관으로 실제 작동함을 보입니다 (pinned **Ctrl-World** 와 같은 raw-pixel 평가 분기).
  - **D30(예측 공간)** — OSCAR 는 **raw-pixel 비디오** 생성입니다. P5 v1 의 latent/3D-flow 선택과 정반대 — "raw-pixel 은 cost 로 deferred 하되 eval-in-imagination 현실성 위해 tracked" 라는 단서에 정확히 들어맞는 데이터 포인트입니다.
  - **D31(action conditioning)** — per-frame **explicit skeleton** conditioning 으로 action-conditioned 예측을 지지(P5 v1 의 action-conditioned 방향 지지). 단 LOME/DexWM 의 latent/keypoint 경로가 아니라 explicit 렌더링 경로입니다.
  - **D32(egocentric hand-object)** — EgoDex·EPIC-Kitchens 사람 손(MANO)을 robot 과 같은 표현으로 흡수 → P5 의 "egocentric human video 를 in-house ego 계획으로 잇는다"는 narrowing 과 직접 공명. 단 OSCAR 의 손은 **conditioning 신호**(골격)일 뿐 hand-object 접촉 동역학의 예측 표적은 아닙니다.
  - **D29(통합 아키텍처)** — OSCAR 는 VLA 백본의 auxiliary head 가 아니라 **standalone 비디오 모델**이라 P5 v1(공유 백본 auxiliary head)과 어긋납니다 — 정책과 co-train 되지 않는 외부 평가자입니다.
- **P0(VLA Datasets & Benchmarks) — secondary.** 4단계 데이터 파이프라인(curate/filter/dedup/caption)과 정책 평가 harness 는 P0 표적입니다. literature anchor 의 EgoDex·DROID·AgiBot World·RH20T 를 모두 끌어 쓰고, **D26(benchmark/eval 스코프)** 의 "world model 을 가상 eval harness 로" 라는 방향에 닿습니다(카탈로그 `benchmark/sim` 후보).
- **Identity 긴장/지지** — Identity 는 P5 를 "후기 단계 베팅"으로 두고 hand-centric·**latent/3D-flow·contact-relevant** 예측을 narrowing 으로 못 박습니다. OSCAR 는 raw-pixel·평가 proxy 라 그 narrowing 과 어긋나는 방향이지만, "사람 손까지 한 표현으로"라는 cross-embodiment·egocentric 축은 강하게 지지합니다 — 즉 **역할(평가자) 채택 후보**이지 **architecture 채택 후보**는 아닙니다.
- **경쟁자 함의** — P5 §5 pinned **Ctrl-World** 를 OSCAR 가 baseline 으로 직접 능가(Table 2)하므로, eval-in-imagination 분기의 핀 후보로 Ctrl-World 와 경쟁합니다.

---

## ✨ 핀 논문 대비 델타

P5 §5 의 raw-pixel / eval-in-imagination 핀은 **Ctrl-World**([arXiv:2510.10125](https://arxiv.org/abs/2510.10125), controllable generative WM, policy-ranking + data-augmentation) 입니다. OSCAR 의 진짜 새로움:

- **conditioning 표현** — Ctrl-World 는 latent-action 계열(Table 2 에서 OSCAR 가 모든 지표 우위)인데, OSCAR 는 **2D skeleton explicit** 렌더링으로 갈아타 cross-embodiment·human 흡수를 동시에 얻습니다.
- **cross-embodiment + human hand** — 단일 표현으로 4종 로봇 + MANO 사람 손을 한 모델에 담는 omni-embodiment 가 Ctrl-World 류 단일-셋업 WM 대비 결정적 차이입니다.
- **실평가 leaderboard 상관 실증** — RoboArena 7정책에서 MMRV/Pearson/SISR_Δ 로 실배포와의 상관을 수치로 보인 점이, "policy-ranking 가능"을 정성 주장하던 단계 대비 진전입니다.
- **저자원** — 단일 GH200·2B 로 14B(Kinema4D)·다GPU baseline 을 능가 — eval-in-imagination 의 진입 비용을 낮춥니다.

반대로 P5 의 latent/3D-flow 핀들(**VLA-JEPA**, **DexWM**, **AHEAD**)과는 예측 공간이 정반대라 델타가 아니라 **대안 노선**입니다 — OSCAR 는 그 노선들을 대체하지 않고 "평가자" 자리에서 보완합니다.

---

## ⚙️ 의사결정 함의

이 논문이 맞다면 우리 스택에서 바뀌는 것은 **policy** 가 아니라 **평가 인프라**와 **데이터 처리**입니다.

- **D28 평가 경로 추가** — `eval` 단계에 "world-model rollout 으로 정책 순위 매기기"를 후보로 올립니다. 구체 메트릭: **MMRV**(rank violation, 목표 ≤0.6 수준 — OSCAR skeleton 0.571), **Pearson r**(성공률 상관, ≥0.8 목표), **SISR_Δ**(per-policy 성공률 MAE, ≤2pp). judge 는 본문처럼 VLM(우리 경우 Claude/GPT 계열, high reasoning, 32-frame 샘플) 고정.
- **D32 conditioning 키** — 사람 egocentric 데이터를 학습에 흡수할 때 **MANO skeleton 렌더링**을 conditioning 표현 후보로 등록. config 키 수준에서는 `condition_repr ∈ {latent_action, mesh, skeleton}` 중 `skeleton`, kinematic spec 만 embodiment 별 교체.
- **데이터 파이프라인 하이퍼** — 우리 코퍼스 dedup 에 차용 가능한 구체 값: SigLIP cosine threshold **0.95**, trajectory **64-step** RMS adaptive threshold, 길이 **≥70 frame**, 정적 카메라 필터, frequency-tempered source weight $`w_i\propto n^{1/T}`$ ($`T{=}3`$). caption 은 VLM, DROID 류 긴 클립은 sampling fps 1–2 로 하향.
- **학습 레시피** — human→robot **warm-start**(로봇-only 선학습 후 혼합) 가 from-scratch 혼합보다 우수(24.24 vs 23.87 PSNR)하므로, 우리가 ego+robot 혼합 사전학습을 한다면 staged warm-start 를 기본으로.
- **바뀌지 않는 것** — OSCAR 는 standalone 평가자이지 dynamics prior 가 아니므로, P5 v1 의 "VLA 백본 auxiliary head(latent/3D-flow)" co-train 결정(D29/D30)은 이 논문으로 바뀌지 않습니다 — 별개 트랙으로 둡니다.

---

## ⚠️ 먼저 검증할 실패 모드

우리 스택(hand-centric, dexterous, 접촉 풍부)으로의 전이 위험을 싼 체크부터:

- **(가장 싼 체크) skeleton 이 손가락 접촉을 못 담는가** — OSCAR 의 골격은 2D 관절 투영뿐. 우리 핵심 태스크(in-hand 재배치, 도구 작동)는 손가락-물체 접촉이 결과를 가르는데, 골격만으론 접촉 상태가 비식별입니다. 우리 EgoDex 류 클립 5개에 MANO skeleton 을 입혀 "접촉 순간 골격이 동일하지만 결과가 다른" 쌍을 찾는 것만으로 한계가 드러납니다.
- **카메라 캘리브레이션 가용성** — 파이프라인은 신뢰 가능한 intrinsic/extrinsic 을 전제로 골격을 투영합니다. 우리 in-house ego 수집의 카메라 캘리브레이션 정밀도를 먼저 측정 — 정렬 오차가 크면 skeleton↔RGB 가 어긋나 학습 신호가 망가집니다(저자 한계와 동일 뿌리).
- **VLM judge 환각 정렬** — world model 의 "없는 성공" 환각과 judge 의 오판이 같은 방향이면 상관이 가짜로 높아집니다. 실로봇 ground-truth 가 있는 소규모 정책 셋에서 OSCAR 추정 SR vs 실측 SR 의 per-episode(평균 아닌) 오차 분포를 먼저 확인.
- **dexterous 정책 순위 변별력** — Table 4 는 DROID generalist(주로 grasp·pick) 정책 7개의 순위입니다. 우리가 평가할 정책들은 미세 접촉 품질로 갈리는데, 골격 기반 비디오가 그 미세 차이를 구분할 분해능이 있는지(접촉 실패가 픽셀로 보이는지) 미지수 — 가장 비싼 검증.
- **open-loop↔closed-loop 격차** — OSCAR 는 주어진 액션을 open-loop 로 굴립니다. 우리 정책은 생성 관측에 반응해야 하는데, closed-loop 로 닫으면 누적 환각이 발산할 위험. open-loop 상관이 좋아도 closed-loop 안정성은 별도 검증 필요.
- **embodiment 격차** — 본문은 Franka/KUKA/AgiBot/HSR 그리퍼·휴머노이드. 우리 Sharpa/xhand(22-DOF) 같은 고DoF 손은 학습 분포 밖이라, kinematic spec 만 교체한다고 곧바로 일반화되는지(사전학습 prior 가 22-DOF 손을 그럴듯하게 채우는지) 확인이 필요합니다.

---

## 💡 컨텍스트 제안

- **P5 §5 핀 후보** — eval-in-imagination / raw-pixel 분기에서 OSCAR 를 **Ctrl-World** 의 교체 또는 보완 핀으로 검토 제안. 근거: Table 2 에서 OSCAR 가 Ctrl-World 를 전 지표 능가하고, cross-embodiment + human-hand + RoboArena 실상관까지 더 넓은 증거를 제공. (단 Ctrl-World 는 controllable/data-augmentation 역할이 별도라 완전 대체는 신중.)
- **D26(benchmark/eval) 연동** — "world model 을 정책 eval harness 로"의 구체 프로토콜(MMRV/Pearson/SISR_Δ + VLM judge)을 P0 benchmark 스코프의 참조 사례로 등록 제안. 카탈로그 `benchmark/sim/OSCAR` 행 신설은 본 분석 메타에 이미 라우팅.
- **D30 단서 보강** — "raw-pixel 은 eval-in-imagination 현실성 위해 tracked" 단서에 OSCAR 를 raw-pixel 평가자의 실증 데이터 포인트로 각주 추가 제안 (예측 공간 v1 선택 자체는 불변).

---

> 💡 base 매핑은 `/implement-design analysis/2606.04463/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
