# Paper Analysis — RotVLA: Rotational Latent Action for Vision-Language-Action Model

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | RotVLA: Rotational Latent Action for Vision-Language-Action Model |
| 저자 | Qiwei Li, Xicheng Gong, Xinghang Li, Peiyan Li, Quanyun Zhou, Hangjun Ye, Jiahuan Zhou, Yadong Mu |
| 링크 | [arXiv:2605.13403](https://arxiv.org/abs/2605.13403) |
| 발행일 / 버전 | 2026-05-13 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-05-26 |
| 관련 Pillar | P2, P3 |
| 태그 | vla-arch, flow-matching |

---

## 🧭 한 줄 요약 (TL;DR)

RotVLA 는 cross-embodiment VLA 사전학습을 위해 latent action 을 이산 토큰이 아닌 $`{\rm SO}(n)`$ 회전군 원소로 연속·구성 가능하게 표현하고, 세 프레임 triplet 학습으로 frame-reconstruction 붕괴를 막은 뒤 flow-matching action expert 의 "latent planner"로 활용해 1.7B 파라미터로 LIBERO 98.2 %, RoboTwin2.0 89.6/88.5 % 를 달성한 VLA 프레임워크입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 이질적인 임바디먼트 / 라벨 없는 인간 비디오를 묶어 VLA 사전학습에 쓰려면 통일된 action 표현이 필요하고, 이를 제공하는 것이 Latent Action Model (LAM) 입니다.
- **기존 접근의 한계** — 주류 LAM 은 VQ-VAE 류 이산 양자화로 latent 를 토큰화합니다. 그래서 결함이 셋입니다. 첫째, 다음 프레임만 그대로 베끼는 자명해로 붕괴합니다. 둘째, 이어지는 물리 동작과 모순될 만큼 표현력이 제약됩니다. 셋째, 스케일·합성 개념이 빠진 비물리 잠재 공간에 머뭅니다.
- **본 논문의 가설** — latent action 을 $`{\rm SO}(n)`$ 원소로 두면 연속성·합성성·기하 구조의 의미를 얻고, 세 프레임 합성 손실을 추가하면 자명해 붕괴를 막아 진짜 dynamics 를 학습합니다.
- **왜 지금 중요한가** — π0.5 / UniVLA / GR00T-N1.6 처럼 flow-matching · 이산 latent action 을 채택한 동시대 VLA 들이 1.7B–9B 규모로 경쟁하는 시점에서, 작은 모델로 latent action 의 *표현 형식* 만 바꿔도 동급 이상 성능이 나온다면, 이는 latent 형식이 독립된 설계축이라는 단서로 읽힙니다.

---

## 🧩 핵심 기여

- $`{\rm SO}(n)`$ 위에 정의된 연속 회전 latent action 표현과 SVD 기반 orthogonal projection 으로 회전 다양체에 안전히 사영하는 학습 가능 모듈.
- 세 프레임 $`(I_t, I_{t+1}, I_{t+2})`$ 의 두 단계 latent action 합성이 두 단계 미래를 복원하도록 강제하는 **triplet learning framework** — 단일-스텝 reconstruction 만 쓰는 LAM 의 frame-copy 붕괴를 막는 핵심 장치.
- InternVL3.5-1B 백본 + 24-layer DiT flow-matching action expert 의 1.7B 통합 구조, 그리고 finetuning 시 latent action 을 "latent planner"로 쓰고 robot action 을 conditioning 으로 받는 **unified action expert** + **structured attention**.
- LIBERO 98.2 % (4 suite 평균), RoboTwin2.0 clean/randomized 89.6/88.5 %, 그리고 실제 ARX R5 듀얼암 로봇 3 태스크에서 $`\pi_{0.5}`$ 대비 일관된 우위.

---

## 🔑 기술 키워드

- **Latent Action Model (LAM)** — 두 프레임 사이의 "행동"을 픽셀 라벨 없이 latent 벡터로 추론하는 inverse/forward dynamics 쌍. 라벨 없는 비디오를 행동 데이터로 끌어다 쓰는 매개체입니다.
- **$`{\rm SO}(n)`$ rotational latent** — $`n \times n`$ 직교·정규 행렬 군. 회전은 합성하면 다시 회전이고 역원이 존재하므로 "행동의 합성"이 행렬 곱과 자연스럽게 일치합니다.
- **SoftVQ** — VQ-VAE 의 hard nearest-codeword 대신 codeword 들의 soft categorical 가중합을 쓰는 양자화. 코드북 구조는 유지하면서 latent 공간의 연속성을 보존합니다.
- **Triplet learning** — 두 단계 latent action 의 곱이 두 칸 뒤 프레임을 복원하도록 강제하는 손실 — "행동 두 번을 이어붙이면 정말 두 칸 미래에 도달해야 한다"는 합성 일관성 검증입니다.
- **Flow matching** — diffusion 의 velocity field 회귀 변형. $`x_\tau = \tau x + (1-\tau)x_0`$ 의 직선 보간 위에서 $`v_\theta`$ 가 $`x - x_0`$ 를 회귀하도록 학습해 안정적이고 빠른 샘플링을 얻습니다.
- **Latent planner / Unified action expert** — finetuning 시 latent action 과 robot action 을 한 flow-matching head 가 동시에 denoise 하되, latent 가 먼저 풀려 robot action 의 조건이 되는 구조. high-level intent 와 embodiment-specific control 을 한 모듈 안에서 분리합니다.
- **Rotate6D** — 회전을 9D rotation matrix 대신 6D 연속 표현으로 회귀하는 방법. 본 논문은 robot action 의 orientation 표기에 이를 채택해 rotational latent 와 형식을 맞춥니다.
- **Cross-embodiment pretraining** — Open X-Embodiment / AGIBOT-Beta / RoboMIND / RoboCOIN / Ego4D 등 1700+ 시간 데이터를 한 모델에 흘려 임바디먼트 차이를 latent action 의 공통 좌표계로 흡수합니다.

---

## 🔬 방법론

### 직관

> "We represent each latent action as an $`n \times n`$ rotation matrix." (§3.1)
> (latent 를 회전 행렬로 놓으면 연속성·합성성·역원이 공짜로 따라옵니다. 자유로운 토큰 임베딩과 달리 "행동을 두 번 적용한다"는 연산이 정확히 행렬 곱으로 정의되므로, 두 프레임 LAM 을 세 프레임 합성 검증으로 확장하는 길이 열립니다.)

> "Existing LAMs follow an encode–decode paradigm and model latent actions as discrete tokens. In contrast, RotVLA represents latent actions as elements of $`{\rm SO}(n)`$, providing continuity, compositionality, and structured geometry aligned with real-world action dynamics." (§1, Figure 2)
> (저자가 제시한 핵심 대비. VQ-VAE 토큰의 자명해 붕괴와 표현력 한계가 모두 latent 공간의 "이산성" 자체에서 비롯된다는 진단입니다.)

![Figure 2 — Existing LAMs vs RotVLA](https://arxiv.org/html/2605.13403/x2.png)

> "Figure 2: Illustration of existing LAMs (a) and RotVLA (b). Existing LAMs follow an encode–decode paradigm and model latent actions as discrete tokens. In contrast, RotVLA represents latent actions as ..." (§1)
> (좌: 기존 LAM 의 encode/decode + VQ 이산 토큰. 우: RotVLA 의 세 프레임 입력에 대한 SoftVQ + $`{\rm SO}(n)`$ projection + 합성 검증.)

### 아키텍처

![Figure 1 — RotVLA framework overview](https://arxiv.org/html/2605.13403/x1.png)

> "Figure 1: We introduce RotVLA, a Vision-Language-Action framework pretrained with a continuous rotational latent action on over 1700 hours of cross-embodiment robot and human video data." (§1)
> (전체 파이프라인: 좌측 LAM 이 두 프레임을 받아 $`{\rm SO}(n)`$ latent 를 뽑고, 우측 VLA 가 VLM 위에 flow-matching action expert 를 얹어 latent / robot action 을 같이 denoise.)

- **LAM 인코더 $`\mathcal{E}`$** — frozen DINOv2 [46] 로 프레임 특징을 추출하고 spatial-temporal transformer 로 후처리해 latent action 후보 행렬 $`M`$ 을 출력.
- **$`{\rm SO}(n)`$ projection $`\mathrm{Proj}(\cdot)`$** — $`M = U\Sigma V^\top`$ 의 SVD 를 통해 Frobenius 최단거리 회전행렬로 사영. 출력은 $`z_{t \to t+1} \in {\rm SO}(n)`$ 의 $`n \times n`$ 행렬, 본 논문은 $`n = 16`$.
- **SoftVQ 양자화** — projection 전 단계에서 codebook 들의 soft categorical 가중합으로 latent 를 안정화, KL 정규화 손실 $`\mathcal{L}_{\rm soft}`$ 를 동반.
- **LAM 디코더 $`\mathcal{D}`$** — 표준 transformer. $`(I_t, z_{t \to t+1})`$ 을 받아 $`\hat{I}_{t+1}`$ 을 복원.
- **항등원 anchor $`z_\mathcal{I}`$** — 같은 프레임 쌍에서 추출한 latent 의 배치 평균을 $`{\rm SO}(n)`$ 으로 사영한 값을 단위원으로 고정해 gauge ambiguity 를 제거.
- **VLM 백본** — InternVL3.5-1B (vision encoder 304 M + language model 752 M).
- **Action expert** — 24-layer Diffusion Transformer (DiT) flow-matching head (305 M). latent action head 290 M 별도. 총 1.7B.
- **Structured attention** — finetuning 시 latent action 토큰은 vision-language 토큰만 attend, robot action 토큰은 latent + vision-language 둘 다 attend. planner ↔ controller 의 정보 흐름을 명시적으로 분리.

### 학습 목표 / 손실

LAM 학습은 두 부분의 단일-스텝 reconstruction 과 두-스텝 합성 reconstruction 으로 구성됩니다.

- 단일-스텝: 두 인접 쌍 각각에 대해 $`\hat{I}_{t+1} = \mathcal{D}(I_t, z_{t \to t+1})`$, $`\hat{I}_{t+2} = \mathcal{D}(I_{t+1}, z_{t+1 \to t+2})`$ 의 픽셀 MSE.
- 두-스텝 합성: 두 latent 의 행렬 곱으로 두 칸 행동을 만든 뒤 $`I_t`$ 에 적용해 $`\hat{I}_{t+2}^{\rm comp}`$ 를 얻고 $`I_{t+2}`$ 와의 MSE.

> "$`\mathcal{L}_{\rm comp} = \|\hat{I}_{t+2}^{\rm comp} - I_{t+2}\|_{2}^{2}.`$" (§3.1)
> ($`I_t`$ 에 두 latent action 의 합성을 한 번에 적용했을 때 두 칸 미래가 복원되어야 한다는 합성 일관성 손실. 단일-스텝만으로는 frame-copy 자명해가 가능하지만, 이 항이 들어가면 두 latent 가 진짜 dynamics 의 부분이어야만 합성이 성립합니다.)

전체 LAM 손실은 다음과 같이 구성됩니다.

$$\mathcal{L}_{\rm triplet} = \mathcal{L}_{\rm single} + \mathcal{L}_{\rm comp} + \mathcal{L}_{\rm soft}$$

(원문에 명시 없음 — 세 항의 가중치는 본문에 가중치 계수가 명시되지 않아 합산 표기 그대로 두었습니다.)

RotVLA 사전학습은 latent action 만 대상으로 한 flow-matching 입니다.

> "$`v_\theta(z_\tau, \tau, h)`$, conditioned on the VLM features $`h`$, where $`z_\tau = \tau z_{t \to t+1} + (1-\tau) z_0, z_0 \sim \mathcal{N}(0, {\rm I}), \tau \in [0,1]`$" (§3.2)
> (직선 보간 noise schedule. velocity field 가 $`z_{t \to t+1} - z_0`$ 를 회귀.)

$$\mathcal{L}_{\rm FM} = \mathbb{E}_{\tau, z, z_0}\left[\|v_\theta(z_\tau, \tau, h) - (z_{t \to t+1} - z_0)\|_2^2\right]$$

Finetuning 은 $`x = (a, z_{t \to t+1})`$ 을 한 변수로 묶어 같은 flow-matching 을 적용합니다.

$$\mathcal{L}_{\rm LA\text{-}RA}^{\rm FM} = \mathbb{E}_{\tau, x, x_0}\left[\|v_\theta(x_\tau, \tau, h) - (x - x_0)\|_2^2\right]\quad(14)$$

### 학습 셋업

- **데이터** — cross-embodiment 로봇 + 인간 비디오 1700+ 시간 (Open X-Embodiment, AGIBOT-Beta, RoboMIND, RoboCOIN, Ego4D 등).
- **사전학습** — LAM, RotVLA 각각 200 k step, batch size 256.
- **Finetuning** — batch size 128. robot action 표기는 absolute end-effector pose + Rotate6D [50] orientation (rotational latent 와 형식 정합).
- **옵티마이저** — AdamW, learning rate 1e-4, weight decay 0.01. VLM 백본은 X-VLA [26] 의 reduced LR 전략, action expert 는 첫 5 k step 동안 VLM 을 frozen 한 채 warm-up.
- **하드웨어** — 8× NVIDIA H200 GPU 로 50 시간 사전학습. 추론은 H20 한 대에서 step 당 79 ms ($`\pi_{0.5}`$ 는 61 ms).
- **다운스트림** — LIBERO 는 4 suite 합쳐 80 k step 단일 다중태스크 모델; RoboTwin2.0 은 50 dual-arm 태스크 단일 모델로 학습 후 태스크당 100 rollout.

---

## 📊 실험 설정과 결과

LIBERO (4 suite) 와 RoboTwin2.0 (50 dual-arm task, clean / randomized) 두 시뮬레이션 벤치마크 + ARX R5 듀얼암 실제 로봇 3 태스크.

| Method | Size | LIBERO Spatial | Object | Goal | Long | Avg. | RoboTwin Clean | Rand. |
|---|---|---|---|---|---|---|---|---|
| OpenVLA-OFT | 7B | 97.6 | 98.4 | 97.9 | 94.5 | 97.1 | — | — |
| $`\pi_{0.5}`$ | 3B | 96.8 | 98.8 | 95.8 | 85.2 | 94.1 | 82.7 | 76.8 |
| GR00T-N1.6 | 3B | 97.7 | 98.5 | 97.5 | 94.4 | 97.0 | — | — |
| UniVLA | 9B | 95.4 | 98.8 | 93.6 | 94.0 | 95.4 | — | — |
| X-VLA | 0.9B | 98.2 | 98.6 | 97.6 | 97.8 | 98.1 | 72.8 | 72.8 |
| StarVLA | 4B | 97.8 | 98.6 | 96.2 | 93.8 | 96.6 | 88.2 | 88.3 |
| Motus | 8B | — | — | — | 97.8 | — | 88.7 | 87.0 |
| **RotVLA** | **1.7B** | **98.2** | **99.6** | **98.4** | **96.4** | **98.2** | **89.6** | **88.5** |

> "With only 1.7B parameters, RotVLA achieves 98.2% on LIBERO [12] and 89.6% / 88.5% on RoboTwin2.0 [13] benchmark." (§1, Table 1)
> (사이즈 대비 효율의 핵심 수치. X-VLA (0.9B) 와 비교하면 평균은 동률(98.2 vs 98.1)이지만 RoboTwin clean/rand 가 89.6/88.5 vs 72.8/72.8 로 큰 차이.)

> "In the two single-arm tasks, RotVLA achieves over 90% success rate." (§4.3)
> (실제 로봇 단일암 두 태스크에서 $`\pi_{0.5}`$ 대비 우위; 듀얼암 컵 적층에서는 실패율이 baseline 보다 현저히 낮다고 본문 서술.)

> "RotVLA achieves an inference latency of 79ms per step, compared to 61ms for $`\pi_{0.5}`$ [21]" (§4.3)
> (latent + robot action 을 동시에 푸는 추가 비용이 약 30 % 지연으로 측정.)

§4.4 의 분석은 두 가지 클레임을 수치로 뒷받침합니다. (1) Training stability — triplet 학습이 없는 baseline 은 다음 프레임에 동일 latent 를 재적용했을 때의 변화가 너무 작아 latent 가 motion 이 아니라 appearance 를 인코딩한다는 점을 Table 2 의 $`\hat{\rm MSE}'`$ 격차로 보임. (2) Representation expressiveness — LARY 벤치마크 linear probing 에서 기존 LAM 대비 회귀 오차는 낮고 분류 정확도는 높음 (§4.4, Table 3). cross-domain 적용 시 Ego4D 에서 뽑은 "오른쪽 이동" latent 가 Tian Qin, UR5, LIBERO (미학습) 까지 전이됨을 §4.4 Figure 4 로 시각화.

---

## ⚖️ 한계

- **이중 행동 디노이즈 비용** — latent + robot action 을 동시에 푸는 unified head 가 $`\pi_{0.5}`$ 대비 약 30 % 지연 (79 ms vs 61 ms / step) 을 유발합니다.
- **$`{\rm SO}(n)`$ 차원 $`n`$ 의 고정** — $`n = 16`$ 이 모든 임바디먼트 / 태스크에 적정한지 본문에서 sweep 되지 않았습니다.
- **action chunk = latent 차원** — latent action 이 horizon $`n`$ 의 action chunk 로 운용되어 $`n`$ 이 동시에 회전 차원·시간 호라이즌·표현력을 묶는 단일 하이퍼라는 점이 분리 가능성에 대한 논의 없이 남아 있을 뿐입니다.
- **항등원 anchor 가정** — 같은 프레임 쌍이 충분히 자주 등장한다는 데이터 가정 위에 단위원이 추정되며, 정지 프레임이 적은 데이터에선 어떻게 되는지 미검증.
- **실제 로봇 평가 폭** — ARX R5 단일·듀얼암 3 태스크에 그치며 in-hand reorientation / 도구 조작 같은 contact-rich 영역은 빠져 있습니다.
- **catastrophic forgetting 정량화 부재** — X-VLA 식 reduced-LR 전략을 그대로 차용하되 VLM prior 보존을 직접 재지는 않습니다.

---

## ♻️ 재현성

- **데이터** — Open X-Embodiment / AGIBOT-Beta / RoboMIND / RoboCOIN / Ego4D / LIBERO / RoboTwin 공개 데이터셋만 사용 (Acknowledgments).
- **모델** — InternVL3.5-1B [38] 백본은 공개. LAM·action expert 가중치 공개 여부는 본문에 명시되지 않음.
- **코드** — 공식 리포지토리 URL 이 본문에 명시되지 않음.
- **하드웨어** — 8× NVIDIA H200, 50 시간 사전학습. 추론은 H20 한 대로 step 당 79 ms.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **[P4](#ref-P4)** (VLM Pretraining Preservation) — VLM 백본 (InternVL3.5-1B) 을 reduced-LR 로만 학습하고 action expert 를 5 k step warm-up frozen 으로 시작하는 전략은 [D19](#ref-D19) 의 frozen-backbone + action-expert 패턴과 정합. 다만 본 논문이 prior 보존을 직접 재지 않아 P4 가설을 *지지하는 정황 증거* 수준에 머뭅니다.
- **[D23](#ref-D23)** (Action representation × VLM preservation) — v1 인 continuous flow-matching head 의 가장 가까운 동시대 인스턴스. 추가로 "latent action 자체를 flow-matching 으로 학습한 뒤 robot action 과 함께 unified flow-matching head 로 푼다" 는 layer 가 D23 의 옵션 공간을 한 단 확장합니다.
- **[P1](#ref-P1)** (Heterogeneous Body/Hand Action Expert) — 팔/손 분리는 아니지만, *planner (latent) ↔ controller (robot)* 의 structured attention 분리는 [D4](#ref-D4) / [D6](#ref-D6) 의 정보 흐름·조정 방향 논의에 *유추적* 함의를 줍니다 (분리 축이 다르므로 직접 채택이 아닌 비교 자료).
- **P2 / P3 / P5** — 촉각/객체 binding (P2), System0 RL (P3) 과 직접 연결 지점 없음. P5 는 LIBERO/RoboTwin 벤치마크 수치만 공유.
- **§10 경쟁자 함의** — UniVLA / GR00T-N1.6 / X-VLA / $`\pi_{0.5}`$ 모두 §10 의 "VLA-only strong performer" 라인. RotVLA 는 1.7B 라는 작은 사이즈로 동급 이상 결과를 내며 — 경쟁축은 모델 크기가 아니라 *latent 표현* 임을 드러냅니다.

---

## ✨ 핀 논문 대비 델타

- **[$`\pi_{0.5}`$](https://arxiv.org/abs/2504.16054) 대비** — $`\pi_{0.5}`$ 의 hierarchical inference 는 high-level "language plan → low-level action" 구조였다면, RotVLA 는 같은 자리에 *연속 회전 latent action* 을 끼워 planner 를 학습 가능한 잠재 변수로 끌어올립니다. 1.7B vs 3B 사이즈에서 LIBERO 평균 98.2 vs 94.1, RoboTwin clean 89.6 vs 82.7 로 우위.
- **VLA-Adapter ([arXiv:2509.09372](https://arxiv.org/abs/2509.09372)) 대비** — VLA-Adapter 의 Bridge Attention 이 VLM ↔ action 의 *수직* 정보 흐름을 다듬는다면, RotVLA 의 structured attention 은 *action-side 내부* 의 planner/controller 흐름을 분리하는 직교 축입니다.
- **MolmoAct2 ([arXiv:2605.02881](https://arxiv.org/abs/2605.02881)) 대비** — MolmoAct2 가 per-layer KV-cache conditioning 으로 backbone 수준에서 prior 를 보존한다면, RotVLA 는 backbone 을 reduced-LR 로만 만지고 prior 보존의 부담을 *latent action 의 임바디먼트-불변성* 으로 옮깁니다.
- **신규 영역 (핀 부재)** — 핀 라이브러리 §8 에는 LAM 계열 (UniVLA / GO-1 / LAPA / CLAM / villa-X) 이 핀으로 들어와 있지 않습니다. RotVLA 는 그 라인의 가장 최신 변형 중 하나로, "latent action 의 *형식*" 이라는 직교 설계축을 가장 명시적으로 다룹니다.

---

## ⚙️ 의사결정 함의

- **D23 옵션 공간 확장** — 현재 v1 (iii) continuous flow-matching head 위에 "latent action 을 별도 flow 로 학습 후 unified flow-matching" 이라는 변형 (iii-b) 를 deferred 후보로 등재합니다. 트리거: backbone 만으로 cross-embodiment prior 가 부족할 때 (D22 의 multi-embodiment 데이터 도입 트리거와 결합).
- **D4 정보 흐름 변형** — structured attention (latent → controller 단방향) 은 [D4](#ref-D4) deferred 의 cross-attention 옵션 (B) 의 비대칭 변형으로 참고. body→hand 의 정보 흐름 비대칭과 동일한 패턴이므로 [D6](#ref-D6) 의 hierarchical flow (a) 와도 정합.
- **action 표기 정합 (config 키)** — Rotate6D + abs EEF orientation 채택은 [D2](#ref-D2) (Body output space = wrist/flange pose) 와 정합. orientation 만큼은 9D rotation matrix 대신 6D 연속 표기를 쓰는 것이 학습 안정성에 유리하다는 정황 증거.
- **하이퍼파라미터** — VLM warm-up 5 k step, batch size 256/128, AdamW lr=1e-4, weight_decay=0.01 은 X-VLA / π 계열과 일관. 우리 셋업의 baseline 으로 그대로 가져다 씁니다.
- **메트릭 직접 채택** — Triplet stability 점검에 쓰인 $`\hat{\rm MSE}`$ vs $`\hat{\rm MSE}'`$ 격차는 [D25](#ref-D25) 의 "split 기여 falsifier" 와 무관하지만, latent 가 motion 을 인코딩하는지 appearance 를 인코딩하는지 가르는 진단 도구로 우리 ablation 에 보조 metric 으로 끼워 둘 만합니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **다지 hand 로의 전이 불확실** — 평가는 양 그리퍼·이중암 평행 그리퍼 기반의 ARX R5. 손가락 수십 자유도에 $`{\rm SO}(n)`$ latent 가 그대로 의미를 갖는지는 미검증. *가장 싼 sanity check*: 우리 Sharpa 데이터에서 latent action 을 추출해 [D26](#ref-D26) 의 coordination corr($`a_b`$,$`a_h`$) 와 latent 가 어떤 상관을 갖는지 본 뒤 진행.
- **$`{\rm SO}(n)`$ projection vs hand joint subspace 정합** — finger joint 의 회전군 구조는 평행 그리퍼나 EEF 6D 와 달리 chain 구조. n=16 회전이 손가락 동학을 표현하기 충분한지 보장 없음.
- **항등원 anchor 의 데이터 편향** — 우리 인-핸드 조작 데이터는 정지 프레임 비율이 낮습니다. anchor 추정이 noisy 해 latent 가 비편향 origin 을 갖지 못할 위험.
- **30 % 추론 지연** — 79 ms / step 은 듀얼암 정도에서 허용되지만 우리 System0 의 contact 안정화 루프 ([D14](#ref-D14)) 와 결합할 때 latency budget 을 깨뜨릴 수 있습니다 — [D26](#ref-D26) throughput metric 으로 확인 필요.
- **catastrophic forgetting 수치 부재** — VLM reduced-LR 만으로 prior 가 보존되는지는 본문이 직접 측정하지 않음. P4 의 가설을 따른다면, 우리는 generalization/OOD metric 으로 별도 측정해야 합니다 ([D25](#ref-D25) VLM-preservation 검증 조건).

---

## 💡 컨텍스트 제안

- §8.4 P4 핀 후보로 *cross-embodiment LAM* 한 자리 신설을 검토합니다. 현재 P4 핀에 LAM 계열이 없는데, RotVLA / UniVLA / villa-X 중 하나를 후보로 띄우는 편이 D23 옵션 공간의 누락을 메웁니다 — 트리거: [CP1](#ref-CP1) ablation 결과에서 frozen backbone + flow-matching 만으로 cross-embodiment 일반화가 부족함이 드러날 때.
- §8.1 P1 의 "정보 흐름 변형" 자료로 structured attention (planner→controller 단방향) 을 참고 자료로 등록 — 핀 교체 없이 D4 deferred 의 cross-attn 옵션 (B) 의 "비대칭 단방향" 변형을 정리할 때 그대로 인용합니다.
- §6.4 의 [D26](#ref-D26) 보조 metric 카탈로그에 "latent stability — single-step vs imagined-step MSE 격차" 추가 검토. baseline 비교가 아닌 LAM 진단 도구이므로 falsifier 가 아닌 보조 지표로만.

> 💡 base 매핑은 `/implement-design analysis/2605.13403/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
