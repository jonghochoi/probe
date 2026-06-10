# Design — The Lie We Tell: Correcting the Euclidean Fallacy in Vision Language Action Policies via Score Matching on Tangent Space

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | The Lie We Tell: Correcting the Euclidean Fallacy in Vision Language Action Policies via Score Matching on Tangent Space |
| 링크 | [arXiv:2606.01847](https://arxiv.org/abs/2606.01847) |
| 분석 문서 | [`analysis/2606.01847/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-05 |

---

## 🧮 데이터 계약

시간 축은 절대 좌표가 아닌 의미 단위(`H` = action horizon, waypoint 수)로 기록합니다.

- **입력 (관측)** — `vision`: $`K`$ 대 카메라 RGB-D → 통합 point cloud. GAT 인코딩 후 geometric feature `F_geo`: shape `(B, N, d)`, `N` = 비어있지 않은 voxel 수, `d` = feature dim (원문에 구체 값 명시 없음).
- **입력 (언어)** — `language`: 명령 텍스트 → frozen CLIP text encoder → `F_lang`: shape `(B, L, d)`, `L` = 토큰 수.
- **입력 (노이즈 포즈)** — `g_t`: 현재 궤적 추정 `(B, H)` 의 SE(3) 원소열 (각 원소는 $`4\times 4`$ homogeneous matrix, 또는 `(R, t)` 쌍). 회전 `R`: `(B, H, 3, 3)`, dtype float32, 제약 $`R^{\top}R=I,\ \det R=1`$; 평행이동 `t`: `(B, H, 3)`.
- **입력 (diffusion time)** — `t`: 스칼라 timestep → sinusoidal embedding $`\tau(t)`$: shape `(B, d_t)`.
- **출력 (score / twist)** — 각 waypoint 당 6D twist $`\xi = (\omega, v)`$: shape `(B, H, 6)`, dtype float32, 평평한 $`\mathfrak{se}(3)`$ 값(접공간). 각속도 $`\omega`$: `(B, H, 3)`, 선속도 `v`: `(B, H, 3)` 은 별도 MLP 출력.
- **출력 (gripper)** — `(B, H, 1)`, sigmoid → binary open/close.
- **정규화 가정** — 노이즈 twist $`\xi \sim N(0, I_6)`$ (표준정규, 좌표축 독립). 평행이동 입력의 positional embedding 정규화 통계 출처는 원문에 명시 없음.

---

## 🧰 모듈 인터페이스

```python
def geometric_context_encoder(rgbd, intrinsics, extrinsics, language) -> Context:
    """K대 RGB-D를 통합 point cloud로 back-project → GAT로 F_geo,
       frozen CLIP로 F_lang, cross-attention 융합 → 통합 context C."""

def denoising_transformer(g_t, tau_t, context) -> Twist:
    """현재 SE(3) 궤적 g_t (B,H) + time embedding + context C 를 받아
       각 waypoint의 tangent-space twist ξ=(ω,v) ∈ R^6 와 gripper logit 예측.
       포즈 토큰화: translation positional embedding + rotation axis-angle(MLP)
       + gripper binary embedding 을 concat."""

def exp_se3(xi) -> SE3:
    """xi=(ω,v) ∈ se(3) → SE(3) 강체 변환. Rodrigues + left Jacobian V(ω).
       임의 입력에 대해 항상 유효한 SE(3) 원소를 반환(surjective)."""

def reverse_step(g_t, xi_pred, beta_t, noise=None) -> SE3:
    """manifold 위 retraction 갱신: g_{t-1} = g_t · exp(-β_t · ξ_pred)
       (+ stochastic 항). 사후 projection/정규화 불필요."""

def forward_noising(g_0, sigma_t, xi) -> SE3:
    """학습용 노이즈 주입: g_t = g_0 · exp(σ_t · ξ), ξ ~ N(0, I_6)."""
```

- **외부 호출 계약** — `exp_se3` 는 미분가능해야 함(원문은 Theseus 로 구현). `denoising_transformer` 출력은 손실 함수의 score-matching 타깃 $`\xi`$ 와 동일 좌표(접공간)에서 비교됨.

---

## ⛓️ 불변식·가정

- **(불변식 1) 군 닫힘성** — 임의 twist $`\boldsymbol{\xi}\in\mathfrak{se}(3)`$ 에 대해 $`\exp(\boldsymbol{\xi})\in\mathrm{SE}(3)`$ 이고 SE(3) 는 곱에 닫혀 있으므로, forward·reverse 전 구간에서 모든 중간 포즈가 manifold 위에 존재하며(Proposition 4.1), $`R^{\top}R=I,\ \det R=1`$ 가 사후 보정 없이 항상 성립.
- **(불변식 2) Left-invariant equivariance** — 최적 score 에 대해 임의 강체변환 $`h`$ 에서 $`s_{\theta}(h\cdot g,t)=\mathrm{Ad}_{h}(s_{\theta}(g,t))`$ (Theorem 4.2). score 가 body-fixed frame 에서 동작해 좌표계 선택에 무관.
- **(가정 3) Geodesic bias** — score 가 궤적을 따라 일정($`s_{\theta}=\boldsymbol{\xi}^{*}`$)하면 probability flow 가 bi-invariant metric 하 geodesic(등속 screw motion)을 생성(Proposition 4.3). 실제 학습 score 는 변하므로 "geodesic 유사 거동으로의 bias" 라는 약한 형태로만 성립.
- **(가정 4) 적용 범위** — 위 성질은 SE(3) **포즈** 출력에 한정. 평평한 joint-angle 출력에는 manifold 논변이 적용되지 않음 (분석 §🎯 의 D3 경계).

---

## 📊 하이퍼파라미터·손실

- 손실 식 (Eq. 8):

$$\mathcal{L}=\lambda_{\mathrm{s}}\mathbb{E}_{t,\boldsymbol{\xi}}\left[\sum_{h=1}^{H}\|s_{\theta}(g_{t}^{h},t)-\boldsymbol{\xi}^{h}\|^{2}\right]+\lambda_{\mathrm{p}}\mathcal{L}_{\mathrm{pos}}+\lambda_{\mathrm{g}}\mathcal{L}_{\mathrm{grip}}$$

  - 주 항: 접공간 denoising score matching (예측 twist vs 주입 twist $`\xi`$).
  - `L_pos`: 평행이동 성분 MSE.
  - `L_grip`: gripper 상태 binary cross-entropy.

- Forward / reverse 식:
  - forward: $`g_{t}=g_{0}\cdot\exp(\sigma_{t}\boldsymbol{\xi})`$, $`\boldsymbol{\xi}\sim\mathcal{N}(\mathbf{0},\mathbf{I}_{6})`$
  - reverse(이산): $`g_{t-\Delta t}=g_{t}\cdot\exp(\sigma_{t}^{2}s_{\theta}(g_{t},t)\Delta t+\sigma_{t}\sqrt{\Delta t}\,\boldsymbol{\zeta})`$, $`\boldsymbol{\zeta}\sim\mathcal{N}(\mathbf{0},\mathbf{I}_{6})`$
  - head 갱신: $`g_{t-1}^{h}=g_{t}^{h}\cdot\exp(-\beta_{t}\boldsymbol{\xi}^{h})`$

- 하이퍼:

  | 이름 | 값 | 출처 |
  |------|----|----|
  | $`\lambda_s`$ (score matching 가중) | (원문 미명시) | §4.2.4, Eq. (8) |
  | $`\lambda_p`$ (position 가중) | (원문 미명시) | §4.2.4, Eq. (8) |
  | $`\lambda_g`$ (gripper 가중) | (원문 미명시) | §4.2.4, Eq. (8) |
  | $`\sigma_t`$ (noise schedule) | 함수 형태 원문 미명시 | §2.2, §4.1.1 |
  | `H` (action horizon) | (원문 미명시) | §2.2 |
  | 학습 iteration | 300K–800K (셋업별) | §Table 1 |
  | 옵티마이저 / lr | (원문 미명시) | — |
  | 학습 비용 | 8-GPU, ~60h (480 GPU-hours) | §E.0.3 |

---

## 🎯 평가 메트릭

- **지표 (성능)** — `Success Rate SR1–SR5` · **임계값** — task chain 연속 성공 · **비교 baseline** — 3D Diffuser Actor (CALVIN); OpenVLA-OFT MLP head (LIBERO Long).
- **지표 (성능)** — `Average task chain Length` · CALVIN ABC→D 에서 3.27 → 3.512, ABCD→D 에서 3.288 → 3.584.
- **지표 (성능)** — `LIBERO-Long Success Rate` (500-trial, 3 seed) · 92.20 (MLP) → 93.87 (Euclidean SM) → 94.13 (Lie SM).
- **지표 (실로봇)** — task 당 20 trial 성공률(%): Move Doll 90→100, Block in Box 80→75, Sort Blocks 55→75, Stack Cups 55→60.
- **지표 (기하 진단)** — 직교성 오차 $`\|\mathbf{R}^{\top}\mathbf{R}-\mathbf{I}\|_{F}`$, determinant 오차 $`|\det(\mathbf{R})-1|`$, quaternion norm $`\|\mathbf{q}\|`$ (유효 = 1), geodesic jitter $`d_{\mathrm{geo}}(\hat{x}_{0}^{(t)},\hat{x}_{0}^{(t-1)})`$ (연속 look-ahead 간 각거리, degree) · **임계값** — Euclidean $`\mathcal{O}(10^{0})`$ vs Lie $`\sim 10^{-7}`$.

---

## ✨ 변경 의도 (intent)

표준 diffusion 정책이 SE(3) 포즈를 평평한 $`\mathbb{R}^{12}`$ 벡터로 두고 ambient-space 가우시안 노이즈를 더하는 것과 달리, 본 알고리즘은 노이즈 주입과 score 예측을 곡면의 접공간 $`\mathfrak{se}(3)`$ 에서 수행하고 exponential map 으로 manifold 에 retraction 합니다. prediction head 가 ambient noise 대신 tangent twist 를 예측하고 갱신이 덧셈 대신 군 곱이 되면, manifold drift 를 제거하고 좌표계 equivariance 와 geodesic 최적성을 사후 projection(SVD/quaternion 정규화) 없이 확보합니다. 인코더·denoising 백본은 3D Diffuser Actor 를 그대로 두고 head 와 denoising loop 만 바꾸는 최소 침습 설계입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 후보 base: `diffusion` family 와 가장 가까움(trajectory-level diffusion + denoising head). 단, 본 논문 백본은 3D point-cloud + 3D relative attention(3D Diffuser Actor)이라 lerobot 의 이미지-기반 `diffusion` policy 와 관측 파이프라인이 다름 — 매핑 시 핵심 이식 대상은 **action head 의 회전 표현(flat → so3-tangent + exp retraction)과 score-matching 손실**이고, point-cloud 인코더 전체 이식은 이 설계의 범위를 넘음. flow-matching 계열(`pi0`/`pi05`/`smolvla`)로의 이식은 SDE→Riemannian flow matching 변환을 동반하는 별도 연구 과제.

---

## 🚧 미해결 / 잠정

- 손실 가중치 $`\lambda_s, \lambda_p, \lambda_g`$ 의 구체 값이 본문에 없어 빈칸으로 둠.
- noise schedule $`\sigma_t`$(및 $`\beta_t`$)의 함수 형태·범위가 명시되지 않음.
- action horizon `H`, feature dim `d`, voxel 수 `N` 등 텐서 shape 의 구체 값 미명시.
- 옵티마이저 종류·learning rate·warmup 등 최적화 셋업 미명시.
- 공개 코드/체크포인트 링크 미확인 — `exp_se3` 의 정확한 수치 구현(작은 각도 Taylor 분기 등)은 Theseus 관행을 따른다고 가정.
