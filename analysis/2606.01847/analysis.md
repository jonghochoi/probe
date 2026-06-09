# Paper Analysis — The Lie We Tell: Correcting the Euclidean Fallacy in Vision Language Action Policies via Score Matching on Tangent Space

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | The Lie We Tell: Correcting the Euclidean Fallacy in Vision Language Action Policies via Score Matching on Tangent Space |
| 저자 | Bing-Cheng Chuang, I-Hsuan Chu, Bor-Jiun Lin, YuanFu Yang, Min Sun, Chun-Yi Lee |
| 링크 | [arXiv:2606.01847](https://arxiv.org/abs/2606.01847) |
| 발행일 / 버전 | 2026-06-01 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-05 |
| 관련 Pillar | P1 |
| 태그 | vla-arch, flow-matching |

---

## 🧭 한 줄 요약 (TL;DR)

Diffusion 기반 VLA 정책이 SE(3) 포즈를 평평한 $`\mathbb{R}^{12}`$ 벡터로 다루는 관행("Euclidean Fallacy")을 지적하고 노이즈를 Lie 대수 $`\mathfrak{se}(3)`$ 의 twist 로 주입한 뒤 exponential map 으로 되돌리는 **Lie Diffuser Actor (LDA)** 를 제안해 manifold drift 제거·좌표계 equivariance·geodesic 최적성을 구조적으로 보장합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — Diffusion 기반 manipulation 정책이 SE(3) 강체 포즈를 $`\mathbb{R}^{12}`$ (회전행렬 평탄화 + 평행이동) 로 표현하고 가우시안 노이즈를 더하는 표준 방식이 회전군의 구조를 깬다는 점을 바로잡으려 합니다.
- **기존 접근의 한계** — Euclidean 노이즈를 더하면 (1) SO(3) 제약을 어기는 manifold drift, (2) 좌표 변환에 covariant 하지 않은 깨진 equivariance, (3) screw motion 을 못 살리는 비-geodesic 궤적이라는 세 실패 모드가 동시에 발생합니다.
- **본 논문의 가설** — 노이즈 주입과 score 예측을 곡면 manifold 위가 아니라 그 접공간(tangent space)인 평평한 Lie 대수에서 수행하고 exponential map 으로 manifold 에 되올리면 위 세 결함이 사후 보정 없이 구조상 사라집니다.
- **왜 지금 중요한가** — Trajectory-level diffusion 정책이 manipulation 의 SOTA 패러다임으로 자리잡았지만 한결같이 SE(3) 를 Euclidean 벡터로 파라미터화하고 사후 projection(SVD/quaternion 정규화)에 의존하고 있어, 표현 자체의 기하 결함이 long-horizon·정밀 회전 작업에서 누적 오차로 이어집니다.

---

## 🧩 핵심 기여

- Diffusion 기반 VLA 정책의 **Euclidean Fallacy** 를 식별·정식화하고 그로부터 manifold drift 와 좌표 변환 하의 깨진 equivariance 가 체계적으로 발생한다는 점을 보입니다.
- 세 가지 증명된 보장을 갖는 **Lie Diffuser Actor** 를 제안합니다 — 군 닫힘성에 의한 manifold drift 제거(Proposition 4.1), 좌표계 강건성을 위한 left-invariant equivariance(Theorem 4.2), kinematically 최적인 screw motion 을 내는 geodesic 궤적 생성(Proposition 4.3).
- CALVIN, OpenVLA-OFT(LIBERO Long), 실로봇 실험에서 일관된 개선을 보이며 미지의 workspace 로 zero-shot 일반화하는 결과로 intrinsic 기하 일관성의 실용 가치를 확인합니다.
- 3D Diffuser Actor 백본 위에서 (i) Euclidean baseline, (ii) Lie diffusion 만, (iii) GAT encoder 만, (iv) 둘 다 결합한 LDA 의 2×2 factorial ablation 으로 intrinsic 기하와 아키텍처 개선의 기여를 분리합니다.

---

## 🔑 기술 키워드

- **Euclidean Fallacy** — 곡면인 SE(3) 를 평평한 벡터 공간처럼 다루는 구조적 부정합. 지구본을 평면 지도처럼 취급해 직선을 그으면 실제 지표면에서 벗어나는 것과 같습니다.
- **SE(3)** — 3D 강체의 회전 $`R\in\mathrm{SO}(3)`$ 과 평행이동 $`\mathbf{t}\in\mathbb{R}^{3}`$ 을 묶은 6차원 Lie 군이자 곡률을 가진 Riemannian manifold. 로봇 그리퍼의 "위치 + 자세" 전체를 한 점으로 표현합니다.
- **Lie algebra $`\mathfrak{se}(3)`$** — SE(3) 의 항등원에 있는 접공간(평평한 6차원 벡터 공간). 가우시안 노이즈를 정의할 수 있는 "평평한 작업대" 역할을 하며 twist $`(\boldsymbol{\omega},\mathbf{v})`$ 로 표현됩니다.
- **Exponential map** — 평평한 접공간의 twist 를 곡면 위 유한 강체 변환으로 되돌리는 다리. 임의의 twist 에 대해 항상 유효한 SE(3) 원소를 내므로(surjective) 제약 위반이 원천 차단됩니다.
- **Left-invariant SDE** — 노이즈를 $`g_t = g_0\cdot\exp(\sigma_t\boldsymbol{\xi})`$ 처럼 군 곱(왼쪽 작용)으로 주입하는 확률미분방정식. 더하기 대신 곱하기로 노이즈를 넣어 manifold 를 벗어나지 않습니다.
- **Score matching** — 데이터 분포의 로그밀도 기울기(score)를 학습해 역확산으로 샘플을 생성하는 기법. 여기서는 score 를 접공간 $`\mathfrak{se}(3)`$ 값으로 예측합니다.
- **Manifold drift** — 회전행렬에 가우시안 노이즈를 더하면 확률 1로 비-직교 행렬이 되어 SO(3) 를 벗어나는 현상. 네트워크가 조작 의미 대신 기하 보정을 학습하게 만듭니다.
- **Equivariance / Adjoint $`\mathrm{Ad}_h`$** — workspace 를 $`h`$ 로 변환하면 출력도 그에 맞춰 변환되는 성질. score 가 $`s_\theta(h\cdot g,t)=\mathrm{Ad}_h(s_\theta(g,t))`$ 로 covariant 하게 변해 좌표계 선택에 무관해집니다.
- **Screw motion / Geodesic** — 축 둘레 회전과 그 축 방향 평행이동을 결합한 나선 운동(Chasles 정리). bi-invariant metric 하 SE(3) 의 최단 경로(geodesic)에 해당해 kinematically 자연스럽습니다.
- **3D Diffuser Actor** — 본 논문의 baseline 이자 백본. point cloud 인코더 + 3D relative attention denoising transformer 로 trajectory-level diffusion 을 수행하지만 Euclidean SE(3) 파라미터화를 씁니다.

---

## 🔬 방법론

### 직관

![Figure 1 — Euclidean Diffusion vs. Lie Diffusion](https://arxiv.org/html/2606.01847/x1.png)

> "Figure 1: Euclidean Diffusion vs. Lie Diffusion. (Top) Extrinsic diffusion treats the curved $`\mathrm{SE}(3)`$ manifold as flat $`\mathbb{R}^{n}`$, which causes drift and produces invalid geometries. (Bottom) The proposed Lie Diffuser Actor injects noise as tangent twists $`\boldsymbol{\xi}\in\mathfrak{se}(3)`$, ensuring that trajectories follow valid geodesics." (§1)
(한글 해설 — 위쪽 Euclidean diffusion 은 곡면을 평면으로 보고 직선 보간해 manifold 밖 무효 자세로 새고 아래쪽 LDA 는 노이즈를 접공간 twist 로 넣어 궤적이 유효한 geodesic 을 따르게 한다는 핵심 대비를 한 장으로 보여줍니다.)

핵심 통찰은 "노이즈를 곡면 위에서 직접 더하지 말고, 평평한 접공간에서 더한 뒤 곡면으로 되돌려라"입니다.

> "Standard Euclidean operations such as vector addition are geometrically undefined on this manifold. Adding two rotation matrices does not generally produce a valid rotation..." (§2.1)
(한글 해설 — 회전행렬끼리 더하면 일반적으로 유효한 회전이 아니게 되므로 manifold 위의 덧셈 자체가 정의되지 않는다는 점이 Euclidean 방식의 근본 결함입니다.)

> "Unlike curved manifold $`\mathrm{SE}(3)`$, the Lie algebra $`\mathfrak{se}(3)`$ is a flat vector space where standard linear operations are well-defined, making it the natural domain for adding Gaussian noise in diffusion models." (§2.1)
(한글 해설 — 가우시안 노이즈를 더할 수 있는 평평한 공간은 manifold 가 아니라 그 접공간인 Lie 대수라는 것이 설계의 출발점입니다.)

§3 의 동기 실험은 이 결함이 이론에 그치지 않음을 보입니다. 3D Diffuser Actor(9D 회전행렬 예측 + 사후 SVD 직교화)와 $`\mathfrak{so}(3)`$ 예측 후 exponential map 으로 매핑하는 본 방법을 직교성 오차 $`\epsilon_{\mathrm{orth}}=\|R^{\top}R-I\|_{F}`$ 로 비교했을 때, 본 방법이 중앙값 5.7%, P90 11.8%, P95 5.4%, P99 2.6% 낮은 위반을 기록했습니다.

### 아키텍처

![Figure 3 — Lie Diffuser Actor architecture](https://arxiv.org/html/2606.01847/x4.png)

> "Figure 3: The overall architectural details for the proposed Lie Diffuser Actor." (§4)
(한글 해설 — 멀티모달 관측 → geometric 인코딩 → iterative denoising → manifold-aware 예측으로 이어지는 전체 흐름을 보여주며 본 방법은 3D Diffuser Actor 의 prediction head 와 denoising loop 만 SE(3) 용으로 교체합니다.)

입력과 출력은 이렇습니다.

> "The robot receives visual observations $`\mathcal{V}=\{I_{1},\ldots,I_{K}\}`$ from $`K`$ cameras and a language instruction $`\mathcal{L}`$. The policy generates an end-effector trajectory $`\mathbf{g}=(g^{1},\ldots,g^{H})\in\mathrm{SE}(3)^{H}`$ over horizon $`H`$." (§2.2)
(한글 해설 — $`K`$ 대 카메라의 RGB-D 와 언어 명령을 받아 horizon $`H`$ 의 SE(3) 엔드이펙터 궤적을 생성하는 conditional generative model $`p_{\theta}(\mathbf{g}\mid\mathcal{V},\mathcal{L})`$ 을 학습합니다.)

아키텍처는 세 모듈로 나뉩니다.

1. **Geometric Context Encoding** — $`K`$ 대 카메라의 RGB-D 를 camera intrinsics/extrinsics 로 통합 point cloud 에 back-project 하고 graph attention transformer(GAT)로 geometric feature $`\mathbf{F}_{\mathrm{geo}}\in\mathbb{R}^{N\times d}`$ ($`N`$ = 비어있지 않은 voxel 수)를 얻습니다. 언어는 frozen CLIP text encoder 로 $`\mathbf{F}_{\mathrm{lang}}\in\mathbb{R}^{L\times d}`$ 로 인코딩한 뒤 cross-attention 으로 융합해 통합 context $`\mathcal{C}`$ 를 만듭니다.
2. **Iterative Denoising Transformer** — 각 denoising step 에서 현재 궤적 $`\mathbf{g}_{t}=(g_{t}^{1},\ldots,g_{t}^{H})`$ 와 sinusoidal time embedding $`\tau(t)`$ 를 받습니다. 각 포즈 $`g_{t}^{h}=(R_{t}^{h},\mathbf{t}_{t}^{h})`$ 는 평행이동의 학습된 positional embedding + 회전의 axis-angle 표현(전용 MLP) + gripper 상태 binary embedding 을 concat 해 토큰화합니다. self-attention 으로 horizon $`H`$ 의 시간 의존성을, cross-attention 으로 context $`\mathcal{C}`$ 를 주입합니다.
3. **Tangent Space Prediction Head** — 표준 Euclidean diffusion 과 갈리는 핵심 지점입니다. 각 waypoint 에 대해 ambient-space 노이즈가 아니라 Lie 대수의 6차원 twist $`\boldsymbol{\xi}^{h}=(\boldsymbol{\omega}^{h},\mathbf{v}^{h})`$ 을 각속도·선속도용 별도 MLP 로 예측합니다(SE(3) 의 semi-direct product 구조 반영). gripper 는 별도 sigmoid 분류기로 open/close 를 냅니다.

> "Critically, the predicted twist $`\boldsymbol{\xi}^{h}`$ lives in the flat tangent space $`\mathfrak{se}(3)`$ where Gaussian noise is well-defined, but the denoising update is performed on the manifold via the exponential map: $`g_{t-1}^{h}=g_{t}^{h}\cdot\exp(-\beta_{t}\boldsymbol{\xi}^{h})`$, where $`\beta_{t}`$ is the noise schedule." (§4.2.3)
(한글 해설 — 예측은 평평한 접공간에서 하되 갱신은 군 곱 + exponential map 으로 manifold 위에서 수행해 매 step 이 사후 projection 없이 유효한 강체 변환이 되도록 보장합니다.)

기하 구조의 핵심은 SE(3) 정의와 exponential map 입니다.

```math
\mathrm{SE}(3)=\left\{\begin{pmatrix}R&\mathbf{t}\\ \mathbf{0}^{\top}&1\end{pmatrix}:R\in\mathrm{SO}(3),\,\mathbf{t}\in\mathbb{R}^{3}\right\}
```

```math
\exp(\boldsymbol{\xi})=\begin{pmatrix}\exp_{\mathrm{SO}(3)}(\boldsymbol{\omega})&V(\boldsymbol{\omega})\mathbf{v}\\ \mathbf{0}^{\top}&1\end{pmatrix}
```

여기서 $`\exp_{\mathrm{SO}(3)}(\boldsymbol{\omega})=I+\frac{\sin\theta}{\theta}[\boldsymbol{\omega}]_{\times}+\frac{1-\cos\theta}{\theta^{2}}[\boldsymbol{\omega}]_{\times}^{2}`$ 는 Rodrigues 공식($`\theta=\|\boldsymbol{\omega}\|`$), $`V(\boldsymbol{\omega})=I+\frac{1-\cos\theta}{\theta^{2}}[\boldsymbol{\omega}]_{\times}+\frac{\theta-\sin\theta}{\theta^{3}}[\boldsymbol{\omega}]_{\times}^{2}`$ 는 회전과 평행이동의 결합을 설명하는 SO(3) 의 left Jacobian 입니다.

### 학습 목표 / 손실

Forward(노이즈 주입) 과정은 Euclidean 식과 intrinsic 식을 대비합니다.

$$\mathbf{x}_{t}=\mathbf{x}_{0}+\sigma_{t}\boldsymbol{\epsilon},\quad\boldsymbol{\epsilon}\sim\mathcal{N}(\mathbf{0},\mathbf{I})$$

$$g_{t}=g_{0}\cdot\exp(\sigma_{t}\boldsymbol{\xi}),\quad\boldsymbol{\xi}\sim\mathcal{N}(\mathbf{0},\mathbf{I}_{6})$$

연속 시간에서는 Stratonovich 형 left-invariant SDE 로 쓰입니다.

$$\mathrm{d}g_{t}=g_{t}\cdot\left(\sigma_{t}\sum_{i=1}^{6}E_{i}\circ\mathrm{d}W_{t}^{i}\right)$$

여기서 $`\{E_{i}\}_{i=1}^{6}`$ 은 $`\mathfrak{se}(3)`$ 의 정규직교 기저, $`\{W_{t}^{i}\}`$ 는 독립 Wiener 과정입니다. 이 구성이 manifold drift 를 원천 제거합니다.

> "The left-invariant SDE in Eq. (5) ensures $`g_{t}\in\mathrm{SE}(3)`$ for all $`t\in[0,T]`$ almost surely." (§4.1.1, Proposition 4.1)
(한글 해설 — 군 곱이 닫혀 있는 덕분에 forward 전 구간에서 샘플이 manifold 를 벗어나지 않음을 보장하는 첫 번째 근거입니다.)

역확산 SDE 와 equivariance 조건은 아래와 같습니다.

$$\mathrm{d}g_{t}=g_{t}\cdot\left(\sigma_{t}^{2}s_{\theta}(g_{t},t)\,\mathrm{d}t+\sigma_{t}\,\mathrm{d}\bar{\mathbf{B}}_{t}\right)$$

$$s_{\theta}(h\cdot g,t)=\mathrm{Ad}_{h}(s_{\theta}(g,t))$$

여기서 $`s_{\theta}:\mathrm{SE}(3)\times[0,T]\to\mathfrak{se}(3)`$ 는 $`\nabla_{\mathfrak{se}(3)}\log p_{t}`$ 를 근사하는 학습된 score 함수이고 adjoint 는 $`\mathrm{Ad}_{(R,\mathbf{p})}(\boldsymbol{\omega},\mathbf{v})=(R\boldsymbol{\omega},R\mathbf{v}+[\mathbf{p}]_{\times}R\boldsymbol{\omega})`$ 로 작용합니다.

> "When the score function is constant along the trajectory... the probability flow generates geodesics on $`\mathrm{SE}(3)`$ under the bi-invariant metric. These geodesics correspond to screw motions with constant angular and linear velocities." (§4.1.3, Proposition 4.3)
(한글 해설 — score 가 궤적을 따라 일정하면 probability flow 가 bi-invariant metric 하 geodesic = 등속 screw motion 을 낸다는 뜻입니다. 실제로는 score 가 변하지만 intrinsic 형식이 궤적을 geodesic 유사 거동으로 치우치게 해 angular jerk 가 줄어듭니다.)

학습 목표는 세 손실의 합입니다.

$$\mathcal{L}=\lambda_{\mathrm{s}}\mathbb{E}_{t,\boldsymbol{\xi}}\left[\sum_{h=1}^{H}\|s_{\theta}(g_{t}^{h},t)-\boldsymbol{\xi}^{h}\|^{2}\right]+\lambda_{\mathrm{p}}\mathcal{L}_{\mathrm{pos}}+\lambda_{\mathrm{g}}\mathcal{L}_{\mathrm{grip}}$$

> "The primary score matching term (weighted by $`\lambda_{\mathrm{s}}`$) trains the network to predict the noise twist $`\boldsymbol{\xi}^{h}`$ added during the forward process, directly implementing denoising score matching adapted to the manifold setting." (§4.2.4)
(한글 해설 — 주 항은 forward 에서 주입한 twist $`\boldsymbol{\xi}^{h}`$ 를 예측하는 manifold 판 denoising score matching, $`\mathcal{L}_{\mathrm{pos}}`$ 는 평행이동 MSE, $`\mathcal{L}_{\mathrm{grip}}`$ 은 gripper 상태 BCE 입니다. 세 가중치 $`\lambda_{\mathrm{s}},\lambda_{\mathrm{p}},\lambda_{\mathrm{g}}`$ 의 구체 값은 본문에 명시되지 않았습니다.)

### 학습 셋업

- **데이터** — 학습 demonstration 궤적 $`\mathbf{g}_{0}=(g_{0}^{1},\ldots,g_{0}^{H})`$ 에서 timestep $`t\sim\mathcal{U}(0,T)`$ 와 waypoint 별 노이즈 twist $`\boldsymbol{\xi}^{h}\sim\mathcal{N}(\mathbf{0},\mathbf{I}_{6})`$ 를 샘플링해 $`g_{t}^{h}=g_{0}^{h}\cdot\exp(\sigma_{t}\boldsymbol{\xi}^{h})`$ 로 노이즈 포즈를 만듭니다.
- **프레임워크 / 라이브러리** — PyTorch 구현, 3D Diffuser Actor 의 3D Denoising Transformer 백본 채택. 미분가능 Lie 군 연산·SE(3) 최적화에 **Theseus**(Pineda et al. 2022), GAT 에 **PyTorch Geometric**, SO(3) parallel sampling 에 Chen et al. (2025b) 방법을 차용했습니다.
- **하드웨어 / 비용** — 8-GPU 클러스터에서 약 60시간(총 480 GPU-hours) 학습. (Appendix E 에는 GPU 로 NVIDIA Titan Xp, CPU 로 Intel i7-8086K 가 명시되어 있으나, 이는 추론/평가용 장비 표기로 보입니다.)
- **옵티마이저 / 스케줄** — 옵티마이저 종류·learning rate·noise schedule 함수 형태는 본문에 명시되지 않았습니다(학습 budget 은 CALVIN 표 기준 300K–800K iteration).

---

## 📊 실험 설정과 결과

평가는 CALVIN(34개 스킬, 환경 A/B/C/D)의 long-horizon language-conditioned 프로토콜에서 이뤄집니다. ABC→D 는 A·B·C 학습 후 미지 환경 D 로의 zero-shot 전이, ABCD→D 는 네 환경 모두 학습입니다. 지표는 연속 5개 task 의 성공률 SR1–SR5 와 평균 task chain 길이(Average Length)입니다.

> "On CALVIN ABC$`\rightarrow`$D, LDA improves average task length from $`3.27`$ to $`3.51`$ ($`+7.3\%`$)." (§Abstract)
(한글 해설 — 대표 수치로, zero-shot ABC→D 에서 평균 chain 길이를 baseline 3.27 → 3.51 로 +7.3% 끌어올렸습니다.)

**CALVIN (Table 1)** — 2×2 ablation. SR1–SR5 와 평균 chain 길이:

| Setting | Method | SR1 | SR2 | SR3 | SR4 | SR5 | Avg Length |
|---|---|---|---|---|---|---|---|
| ABC→D | 3D Diffuser Actor (600K) | 92.2 | 78.7 | 63.9 | 51.2 | 41.2 | 3.27 |
| ABC→D | LDA (600K) w/o GAT Encoder | 89.6 | 78 | 66.6 | 55.7 | 46.9 | 3.368 |
| ABC→D | LDA (300K) w/o Lie Space Diffusion | 90.2 | 80.3 | 69.6 | 58.5 | 48.8 | 3.474 |
| ABC→D | LDA (300K) | 93.7 | 83.4 | 70.3 | 57.6 | 46.2 | 3.512 |
| ABCD→D | 3D Diffuser Actor (800K) | 90.3 | 77.3 | 65.8 | 53.8 | 41.6 | 3.288 |
| ABCD→D | LDA (300K) w/o GAT Encoder | 90.8 | 77.3 | 66.4 | 57.6 | 48.3 | 3.404 |
| ABCD→D | LDA (400K) w/o Lie Space Diffusion | 91.0 | 76.1 | 63.4 | 51.6 | 41.8 | 3.239 |
| ABCD→D | LDA (300K) | 90.6 | 80.4 | 71.1 | 62.6 | 53.7 | 3.584 |

> "the originally reported 400K result was 3.254." (§Table 1, 각주 1)
(한글 해설 — `w/o GAT Encoder` ABC→D 행은 baseline 학습 budget 을 맞추려 600K 로 재학습한 값이며 원래 보고된 400K 값은 3.254 였습니다. 표의 두 ablation 행은 학습 iteration 수가 서로 달라 직접 비교 시 주의가 필요합니다.)

ABCD→D 에서 Euclidean baseline 은 다양한 환경에서 학습 불안정·일반화 저하를 보인 반면 LDA 는 평균 chain 길이 3.584 로 가장 높았습니다.

**실로봇 (Table 2)** — 4개 task, task 당 20회 시도, 성공률(%):

| Method | Move Doll | Block in Box | Sort Blocks | Stack Cups |
|---|---|---|---|---|
| Baseline | 90 | 80 | 55 | 55 |
| Lie Diffuser | 100 | 75 | 75 | 60 |

> "The method attains perfect success on Move Doll Platform and substantial improvements on Sort Blocks and Stack Cups, where precise orientation control is critical." (§5.3)
(한글 해설 — 정밀 자세 제어가 필요한 task 에서 개선이 두드러지고 단순 삽입인 Put Block in Box 에서는 오히려 제약 없는 Euclidean 탐색이 약간 유리해 baseline 80 vs 75 로 동급 이하였습니다.)

**Cross-architecture (Table 4, OpenVLA-OFT / LIBERO Long)** — 3D Diffuser Actor 와 perceptual 요소를 전혀 공유하지 않는 7B VLA 의 MLP action head 에 Lie 형식을 이식해 이득이 아키텍처가 아니라 형식 자체에서 나옴을 검증합니다.

> "Holding the head fixed and varying only geometry, Lie Score Matching raises the success rate from 93.87(Euclidean) to 94.13. Both score-matching variants in turn exceed the 92.20 MLP baseline." (§C, Table 4)
(한글 해설 — head 를 고정하고 기하만 바꿨을 때 Euclidean 93.87 → Lie 94.13, 두 score-matching 변형 모두 MLP baseline 92.20 을 상회했습니다. 3 seed 평균, 500-trial LIBERO-Long 기준입니다.)

**Manifold 제약 위반 (Fig. 5, §5.4)** — 역확산 중 회전을 단위 quaternion 으로 $`\mathbb{S}^{3}`$ 에 투영해 추적했을 때, Euclidean 은 직교성 오차 $`\|\mathbf{R}^{\top}\mathbf{R}-\mathbf{I}\|_{F}`$ 가 $`\mathcal{O}(10^{0})`$ 까지 치솟고 quaternion norm 이 0.5–2.0 으로 흔들린 반면, Lie 는 부동소수점 정밀도 $`\sim 10^{-7}`$ 와 단위 norm 을 전 구간 유지했습니다.

![Figure 6 — Look-ahead Stability and Geodesic Jitter](https://arxiv.org/html/2606.01847/x13.png)

> "Figure 6: Look-ahead Stability and Geodesic Jitter. Geodesic jitter (angular distance in degrees) between consecutive look-ahead predictions $`\hat{x}_{0}^{(t)}`$ and $`\hat{x}_{0}^{(t-1)}`$ during reverse diffusion. The Euclidean baseline (red) exhibits up to two orders of magnitude higher jitter than LDA (teal), particularly in early diffusion steps." (§5.5)
(한글 해설 — 연속 look-ahead 예측 간 각거리(geodesic jitter)로 denoising 안정성을 측정했고 Euclidean 이 초기 step 에서 최대 두 자릿수 더 큰 jitter 를 보여 manifold drift 가 control 신호의 떨림으로 직결됨을 시각화합니다.)

---

## ⚖️ 한계

- **백본·벤치마크 범위의 제한** — 주 실험이 3D Diffuser Actor 한 백본 + CALVIN 에 집중되어 있고 large-scale VLA 와의 직접 비교는 "geometric 표현 연구라 데이터 규모가 다른 모델과는 비교 대상이 아니다"라며 의도적으로 제외했습니다. SOTA 절대 성능이 아니라 동일 아키텍처군 내 상대 개선을 주장하는 셈입니다.
- **Ablation 행의 iteration 불일치** — Table 1 의 ablation 변형들이 300K/400K/600K 로 학습 budget 이 달라, 일부 행(예: `w/o Lie Space Diffusion` 300K 가 평균 길이 3.474 로 full 3.512 에 근접)은 budget 차이가 교란 요인으로 남습니다.
- **실로봇 표본·범위** — task 4종 × 20 trial 로 표본이 작고 Put Block in Box 에서는 baseline 과 동급 이하여서 이득이 회전 결합이 강한 task 에만 한정됩니다.
- **하드웨어 표기의 모호성** — Appendix E 의 GPU(Titan Xp)와 "8-GPU 클러스터/480 GPU-hours"가 일관되게 정리되지 않아, 학습에 쓴 정확한 GPU 사양 재현이 어렵습니다.
- **Proposition 4.3 의 실효성** — geodesic 보장은 score 가 궤적을 따라 일정할 때만 엄밀히 성립하고 실제 학습된 score 는 변하므로 "geodesic 유사 거동으로 치우치는 편향" 수준의 약한 주장입니다.

---

## ♻️ 재현성

- **코드 / 모델** — 공개 코드·체크포인트 링크가 본문/메타에 명시되지 않았습니다(공식 repo 미확인). 다만 baseline 3D Diffuser Actor, Theseus, PyTorch Geometric 등 의존 프레임워크는 모두 공개되어 있어 재구현 경로는 비교적 명확합니다.
- **데이터** — 시뮬레이션은 공개 CALVIN(Mees et al. 2022) 과 LIBERO-Long 을 사용합니다. 실로봇 데이터는 kinesthetic teaching + autonomous replay 2단계로 task 당 50 demo 를 자체 수집했으며 공개 여부는 명시되지 않았습니다.
- **하드웨어** — 8-GPU 클러스터, 약 60시간(480 GPU-hours)으로 학습 비용을 보고했습니다.
- **수치 재현성** — CALVIN 표는 SR1–SR5 와 iteration 수까지 명시되어 재현 단서가 충분하나, 손실 가중치($`\lambda_{\mathrm{s}},\lambda_{\mathrm{p}},\lambda_{\mathrm{g}}`$), noise schedule, optimizer 등 하이퍼파라미터 일부가 비어 있습니다.

---

## 🎯 관련 Pillar / Decision (P# / P1)

- **P1 (Heterogeneous Body/Hand Action Expert) — D2 (Body output space) 직결.** PROBE 의 v1 D2 는 Body 출력을 (a) both-wrist / tool-flange **pose** 로 잡았습니다. 이 포즈가 곧 SE(3) 원소이므로 본 논문은 "그 SE(3) 포즈를 어떤 좌표계로 파라미터화·생성할 것인가"라는 D2 의 하위 질문에 기하학적 근거로 답합니다. Euclidean $`\mathbb{R}^{9/12}`$ flat 표현 대신 $`\mathfrak{se}(3)`$ twist 예측 + exponential map retraction 을 쓰면 manifold drift·좌표계 의존성이 사라진다는 주장입니다.
- **P1 — D3 (Hand output space) 와는 부분적 무관.** D3 의 v1 은 Hand 출력을 (i) **finger joint command**(관절각, $`\mathbb{R}^{n}`$)로 잡았습니다. finger 관절각은 SE(3) manifold 가 아니라 평평한 joint 공간이라 본 논문의 SE(3) 논변이 그대로 적용되지 않습니다. 그래서 이 논문의 "manifold-aware 표현" 이득은 **Body/wrist 포즈 쪽에 국한**되며 Hand expert 의 관절각 출력에는 직접 전이되지 않는다는 경계가 분명합니다.
- **Identity 긴장/지지** — PROBE 의 capability source 는 diffusion 이 아니라 **flow-matching action expert(π0/π0.5)** 입니다(MASTER §4.3). 본 논문은 diffusion/score-matching 에 한정되지만 §6 에서 스스로 Riemannian flow matching(Braun et al. 2024 등) 과의 연결을 언급하므로 "manifold 위 노이즈/transport" 라는 통찰은 flow-matching 백본에도 옮길 여지가 있습니다. 다만 본 논문은 flow matching 을 "deterministic transport 라 multimodality 포착이 부족할 수 있다"고 평가해 오히려 SDE 형식을 옹호합니다 — PROBE 의 flow-matching 선택과 미묘한 긴장입니다.
- **경쟁자/유사연구 함의 (P1 §7)** — P1 §7 Competitor 표에 직접 겹치는 항목은 없습니다. 본 논문은 anatomical Body/Hand split 류가 아니라 action **표현(geometry)** 축의 작업이라 §7 의 split-architecture 경쟁자들과는 직교합니다.

---

## ✨ 핀 논문 대비 델타

- **vs. Demystifying Action Space Design ([arXiv:2602.23408](https://arxiv.org/abs/2602.23408), P1 §5 핀, D2 evidence)** — 핀 논문은 13k+ 실 rollout 으로 "joint space = 안정성 / task space(EE pose) = 일반화" 라는 **거시적 action space 선택**을 경험적으로 가른 작업입니다. 본 논문의 진짜 새로움은 그 한 단계 **아래** — task space(EE pose)를 선택한 뒤 그 **SE(3) 포즈를 어떤 기하로 파라미터화·노이즈주입할 것인가**(flat $`\mathbb{R}^{12}`$ vs intrinsic $`\mathfrak{se}(3)`$)를 이론적 보장과 함께 다룬다는 점입니다. 핀 논문이 "어느 공간"을 묻는다면 본 논문은 "그 공간 위에서 어떻게 움직일/생성할 것인가"를 묻습니다 — 보완 관계이지 대체가 아닙니다.
- **vs. π0/π0.5 ([arXiv:2410.24164](https://arxiv.org/abs/2410.24164) / [arXiv:2504.16054](https://arxiv.org/abs/2504.16054), 백본 핀)** — π 계열의 flow-matching action expert 는 action 을 평평한 벡터로 두고 conditional vector field 를 학습합니다. 본 논문은 그 평평한 표현이 회전 성분에서 구조적 결함을 낸다는 점을 정량화(Fig. 5 의 $`10^{7}`$ 배 위반)함으로써 π 의 action 표현이 가진 결함을 드러냅니다. 다만 본 논문은 SDE/score-matching 으로 검증했을 뿐 flow-matching 에서 같은 효과가 나타나는지는 검증하지 않았습니다.

---

## ⚙️ 의사결정 함의

- **D2 (Body output space) 의 하위 스펙으로 "회전 표현" 변수를 추가.** 본 논문이 맞다면 PROBE 의 Body expert 가 내는 wrist/tool-flange 포즈의 **회전 성분 파라미터화**를 (현행 flat 6D/9D/quaternion 가정 대신) `axis-angle / $`\mathfrak{so}(3)`$ twist + exponential-map retraction` 로 바꾸는 방안을 검토해 볼 만합니다. 구체적으로는 action head 의 회전 출력 차원과 디코딩 함수(`exp_so3`)가 바뀌고 정규화 손실(SVD/quaternion-norm penalty)을 제거할 수 있습니다.
- **Flow-matching loss 의 manifold 판 검토.** π 백본의 flow-matching target 을 ambient $`\mathbb{R}^{n}`$ 에서 정의하는 대신, 회전 성분에 한해 Riemannian flow matching(접공간 vector field + exp retraction)로 바꾸는 ablation 을 1개 추가. 구체 config 키 후보: `action_rotation_repr ∈ {flat9d, rot6d, so3_tangent}`, `retraction ∈ {none, exp_so3}`.
- **새 진단 메트릭 도입.** 학습/추론 모니터링에 직교성 오차 $`\|R^{\top}R-I\|_{F}`$ 와 determinant 오차 $`|\det(R)-1|`$, geodesic jitter(연속 look-ahead 예측 간 각거리)를 추가해 회전 표현 변경의 효과를 baseline 대비 정량화. 이는 코드 한 함수로 측정 가능한 싼 지표입니다.
- **적용 범위 제한 명시.** 위 변경은 **Body/wrist SE(3) 포즈에만** 적용하고 Hand expert 의 finger joint 출력(D3, 평평한 관절각)에는 적용하지 않는다는 경계를 설계에 못 박아야 합니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 sanity check) Diffusion→Flow-matching 전이 미확인.** 본 논문의 모든 보장은 score-matching/SDE 위에서 증명됐고 PROBE 백본은 flow-matching 입니다. 먼저 할 일은 코드 변경 없이 **현행 π flow-matching 정책의 출력 회전에 대해 직교성 오차·quaternion norm 을 로깅**해, 우리 스택에서 실제로 manifold drift 가 유의미한 크기인지부터 확인하는 일입니다. 만약 우리 표현(예: 이미 6D rotation + Gram-Schmidt)에서 위반이 미미하면 이 논문의 이득은 전이되지 않습니다.
- **회전 결합 강도 의존성.** 실로봇 결과가 보여주듯 이득은 회전·평행이동 결합이 강한 task 에 국한됩니다. PROBE 의 in-hand reorientation/tool articulation 은 회전 dominant 라 잠재 이득이 클 수 있으나, 단순 pick-and-place 단계에서는 제약 없는 Euclidean 탐색이 오히려 유리할 수 있습니다(Put Block in Box 사례).
- **Theseus/PyG 의존성 비용.** 미분가능 SE(3) 연산을 위해 Theseus, GAT 를 위해 PyG 를 끌어오는데 π/openpi 스택과의 통합·학습 속도 영향이 미지수입니다. 작은 회전-only 합성 task 로 exponential-map retraction 의 forward/backward 비용부터 프로파일링하는 게 순서입니다.
- **Body/Hand 경계의 좌표계 정합.** D4(Body→Hand FiLM 정보 공유) 흐름에서 Body 의 SE(3)-tangent 출력과 Hand 의 joint-space 출력이 서로 다른 좌표계를 갖게 되어 FiLM 변조 입력의 표현 불일치가 새 실패 지점이 될 수 있습니다.

---

## 💡 컨텍스트 제안

- **P1 §5 핀 교체는 권장하지 않음(추적 등록 수준).** 본 논문은 anatomical Body/Hand split 이 아니라 action **표현 geometry** 축이라 P1 의 8-pin 핵심(split/decoder 계열)과 결이 다릅니다. 다만 D2(Body output space)의 "회전 표현" 하위 질문에 대한 **유일한 기하학적 reference** 이므로 P1 §5 "Methodology base (non-pinned)" 테이블에 *Lie Diffuser Actor (arXiv:2606.01847) — SE(3)-intrinsic action 파라미터화 / D2 회전표현 evidence* 로 1줄 추가를 제안합니다.
- **D2 의 deferred 후보에 "rotation parameterization" 축 신설 검토.** 현 D2 는 joint vs task(EE pose) 의 거시 선택만 다룹니다. 그 아래 "EE pose 의 회전 표현(flat9d / rot6d / so3-tangent)" 을 deferred 변수로 명시할지 사람의 판단을 구합니다.
- context/ 파일은 수정하지 않았습니다. 위는 제안일 뿐입니다.

> 💡 base 매핑은 `/implement-design analysis/2606.01847/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
