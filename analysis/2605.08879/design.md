# Design — Preserving Foundational Capabilities in Flow-Matching VLAs through Conservative SFT

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Preserving Foundational Capabilities in Flow-Matching VLAs through Conservative SFT |
| 링크 | [arXiv:2605.08879](https://arxiv.org/abs/2605.08879) |
| 분석 문서 | [`analysis/2605.08879/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-05-26 |

---

## 🧮 데이터 계약

ConSFT 는 데이터 파이프라인을 바꾸지 않습니다 — *손실 계층 위에서만* 작동하므로 입력·출력 텐서는 기존 flow-matching VLA 의 표준 계약을 그대로 따릅니다.

- **입력 (백본 동일)** — 이미지·언어·proprioception·(선택) tactile. shape 은 채택 backbone ($`\pi_{0}`$ / $`\pi_{0.5}`$ / GR00T-N1.6-3B) 의 기존 계약을 따름. (원문에 ConSFT 고유 입력 텐서 명세 없음 — 손실 변경만이 본 알고리즘의 범위.)
- **출력 (백본 동일)** — flow-matching 정책이 예측하는 action chunk: `(B, T_action, D_action)`, dtype `float32`. 정규화는 데이터셋 통계.
- **손실 계산 보조 입력** — per-sample 표준 flow-matching loss 스칼라 텐서 `loss_per_sample: shape (B,), dtype float32`. 이로부터 `omega: shape (B,), dtype float32` 가 stop-gradient 로 산출됩니다.
- **스케줄러 상태** — 학습 step `t: int64` 와 총 step `T: int64` 를 입력으로 받아 동적 온도 `tau(t): float32` 를 산출.

---

## 🧰 모듈 인터페이스

함수 시그니처 수준의 책임 분해. 구현은 비웠고, vendor file:line 은 들어가지 않습니다.

```python
def consft_weight(
    loss_per_sample: Tensor,   # (B,) float32, per-sample flow-matching loss
    tau: float,                # current temperature (scalar)
    kappa: float = 25.0,       # scaling factor on the loss
    omega_min: float = 1e-3,   # numerical floor on the weight
) -> Tensor:
    """샘플별 신뢰도 가중치 ω = max(ω_min, exp(-κ · L_SFT / τ)). stop-gradient 적용."""
```

```python
def consft_loss(
    loss_per_sample: Tensor,   # (B,) float32, per-sample flow-matching loss
    tau: float,
    kappa: float = 25.0,
    omega_min: float = 1e-3,
) -> Tensor:
    """ConSFT 목적함수: mean( sg(ω) · L_SFT ). 백본 forward/backward 계약 무변경."""
```

```python
def consft_temperature(
    step: int,                 # 현재 global step t
    total_steps: int,          # 총 스케줄 step T
    tau_start: float = 0.003,
    tau_end: float = 5.0,
    lam: float = 0.8,          # exponential decay rate λ
    c_curvature: float = 3.5,  # curvature factor c (>1.0)
    eps: float = 1e-8,
) -> float:
    """단조 증가 온도 스케줄. Eq. 11–12 의 ρ(t)·τ(t) 산출."""
```

- 호출 계약 — 학습 루프는 (1) 기존 flow-matching head 로 `loss_per_sample` 산출 → (2) `consft_temperature(step, T, …)` 로 `tau` 계산 → (3) `consft_loss(loss_per_sample, tau, …)` 를 backward 대상으로 사용. 옵티마이저·grad-clip·FSDP shard 정책은 기존 그대로.
- 외부 의존성 — 사전학습 데이터 버퍼 없음, 참조 네트워크 없음, low-rank 어댑터 없음. *forward 그래프에 추가되는 노드는 element-wise exp 와 stop-gradient 두 개뿐.*

---

## ⛓️ 불변식·가정

- **(가정 1) Flow-matching loss = ELBO + const (sample-independent)** — Eq. 3 의 핵심 가정. probability-flow ELBO 와 flow-matching MSE 가 노이즈 스케줄 상수 `` $`c`$ `` 차이만큼 다르며, 그 `` $`c`$ `` 는 정책 파라미터·샘플과 무관해야 likelihood ratio 가 손실 차의 지수로 환원됩니다.
- **(가정 2) Ideal expert assumption** — `` $`\mathcal{L}_{\mathrm{behavior}}=0`$ ``. 실제 시연이 약간의 epistemic noise `` $`\epsilon_{\mathrm{min}}>0`$ `` 를 갖더라도 global scalar 로 흡수돼 minibatch 내 *상대* gradient 방향이 보존된다는 Appendix B.1 의 논거에 의존.
- **(가정 3) FIM 은 양의 준정부호 (PSD)** — `` $`\mathcal{R}(g)=g^{\top}Fg\geq 0`$ ``. 이로부터 스칼라 `` $`\omega\in(0,1]`$ `` 의 quadratic 감쇠가 모든 curvature `` $`F`$ `` 에 대해 성립.
- **(가정 4) per-sample loss 와 gradient magnitude 의 양의 상관** — 고 손실 샘플이 큰 gradient 를 만들어 forgetting risk 의 주범이 된다. ConSFT 의 risk 억제는 여기에 그대로 기댄다.
- **(가정 5) stop-gradient 보존** — `` $`\omega`$ `` 는 backward 그래프에서 leaf scalar 여야 함. autograd 추적이 새면 ω 자체가 학습 대상이 되어 weight 가 0 으로 붕괴.
- **(가정 6) shape 4 변수의 task-agnostic 성질** — `` $`\lambda=0.8,\, c=3.5,\, \kappa=25.0,\, \omega_{\mathrm{min}}=0.001`$ `` 가 task 와 데이터 규모를 가로질러 고정 가능하다는 실험적 주장 (Appendix C.1).

---

## 📊 하이퍼파라미터·손실

**손실 식 (Eq. 5)**

$$\mathcal{J}_{\mathrm{ConSFT}}(\theta)=\mathrm{sg}\left[\exp\left(-\frac{\mathcal{L}_{\mathrm{SFT}}(\theta)}{\tau}\right)\right]\cdot\mathcal{L}_{\mathrm{SFT}}(\theta).$$

실효 가중치 (floor 포함):

$$\omega(\theta)=\max\!\left(\omega_{\mathrm{min}},\ \exp\!\left(-\kappa\,\frac{\mathcal{L}_{\mathrm{SFT}}(\theta)}{\tau(t)}\right)\right).$$

온도 스케줄 (Eq. 11, 12):

$$\rho(t)=\frac{\exp\!\left(-\lambda\!\left[\min\!\left(\frac{t}{T},1\right)\right]^{c}\right)-\exp(-\lambda)}{1-\exp(-\lambda)},\qquad \tau(t)=\min\!\left(\frac{\tau_{\mathrm{start}}}{\max(\rho(t),\epsilon)},\ \tau_{\mathrm{end}}\right).$$

Forgetting risk (Eq. 6, 7):

$$\mathcal{R}(g_{\mathrm{ConSFT}})=\omega^{2}\,\mathcal{R}(g_{\mathrm{SFT}})=\exp\!\left(-\frac{2\mathcal{L}_{\mathrm{SFT}}(\theta)}{\tau}\right)\,g_{\mathrm{SFT}}^{\top}F\,g_{\mathrm{SFT}}.$$

Sparsity 메트릭 (Eq. 8, `` $`\delta=10^{-3}`$ ``, `` $`\epsilon=10^{-8}`$ ``):

$$S=\frac{1}{N}\sum_{i=1}^{N}\mathbb{I}\!\left(\frac{|(\Theta_{\mathrm{ft}})_{i}-(\Theta_{\mathrm{pre}})_{i}|}{|(\Theta_{\mathrm{pre}})_{i}|+\epsilon}<\delta\right).$$

**하이퍼파라미터**

| 이름 | 값 | 출처 |
|---|---|---|
| `tau_start` (`` $`\tau_{\mathrm{start}}`$ ``) | `0.003` | §C.2, Table 5 |
| `tau_end` (`` $`\tau_{\mathrm{end}}`$ ``) | `5.0` | §C.2, Table 5 |
| `kappa` (`` $`\kappa`$ ``) | `25.0` | §C.1, Table 5 |
| `lambda` (`` $`\lambda`$ ``) | `0.8` | §C.1, Table 5 |
| `c_curvature` (`` $`c`$ ``) | `3.5` | §C.1, Table 5 |
| `omega_min` (`` $`\omega_{\mathrm{min}}`$ ``) | `0.001` | §C.1, Table 5 |
| `decay_steps` (`` $`T`$ ``) | `2000` | §C.1, Table 5 |
| `numerical_eps` | `1e-8` | §C.1 (분모 안정화) |
| `sparsity_delta` (`` $`\delta`$ ``) | `1e-3` | §A.3, Eq. (8) |
| Adam β | `(0.9, 0.95)` | §C.2, Table 5 |
| Adam ε | `1e-8` | §C.2, Table 5 |
| Learning rate | `2.5e-5` | §C.2, Table 5 |
| Weight decay | `1e-10` | §C.2, Table 5 |
| Max grad-norm | `1.0` | §C.2, Table 5 |
| Global batch | `1024` | §C.2, Table 5 |
| Micro batch / GPU | `32` | §C.2, Table 5 |
| Hardware | `8× A100 80GB + FSDP` | §C.2, Table 5 |

shape 4 개 (`lambda`, `c_curvature`, `kappa`, `omega_min`) 는 이 논문의 전 실험에서 고정됐고, task-specific 으로 튜닝되는 것은 `tau_start` 와 `decay_steps` 둘뿐이다 (§C.1 "Hyperparameter robustness").

---

## 🎯 평가 메트릭

- **지표 — Target task success rate** · **임계값** — vanilla SFT 와 동률 이상 (예: $`\pi_{0}`$ LIBERO-Spatial 90%) · **비교 baseline** — vanilla SFT.
- **지표 — Prior task average success rate** (held-out suite 평균) · **임계값** — vanilla SFT 대비 절대 +20%p 이상 · **비교 baseline** — SFT, LwF (KL/MSE), ER (1:1 replay), LoRA (r=16).
- **지표 — Absolute drop from base** (`` $`\downarrow`$ ``) · **임계값** — `` $`\downarrow \le 0.15`$ `` (LIBERO 평균) 가 본 논문 ConSFT 도달치 · **비교 baseline** — base model 의 zero-shot.
- **지표 — Global update sparsity `` $`S`$ ``** (Eq. 8, `` $`\delta=10^{-3}`$ ``) · **임계값** — vanilla SFT 의 약 70% 수준 (PPO 는 약 85%) 보다 *늦게* 붕괴하는 곡선 형태 · **비교 baseline** — vanilla SFT 의 sparsity 시계열.
- **지표 — Layer-wise sparsity profile** (Attention / MLP) · **임계값** — Attention/MLP 모두 layer-wise sparsity 가 임계 step (early phase) 이전에 50% 이상 유지 · **비교 baseline** — vanilla SFT 의 dense overwrite 패턴.
- **지표 — Real-world prior task success (test-tube + 의미 grasping, $`\pi_{0.5}`$ 단일팔)** · **임계값** — target 70% 도달 시점에 prior task 평균 절대 +20%p · **비교 baseline** — vanilla SFT, LwF.

평가 프로토콜 (§5.1) — *모든 비교군이 같은 target 성공률에 도달한 시점* 에 prior 를 측정해 forgetting 만 격리한다. (원문 표 1: 87~95% 구간; 표 2: 같은 target 값으로 정렬.)

---

## ✨ 변경 의도 (intent)

ConSFT 는 prior art 의 두 라인 — (a) PPO clip 으로 trust-region 을 *명시* 하는 RL 류, (b) LwF/ER/LoRA 처럼 *추가 자원* (참조망/사전 데이터/저랭크 어댑터) 으로 prior 를 묶는 anti-forgetting 류 — 모두에 대해 "추가 자원 없이 trust-region 의 *효과* 만 가져온다" 는 단일 목표를 갖습니다. 핵심은 *RL forgetting 완화의 인과가 advantage 가중이 아니라 update sparsity 임* 을 실증한 §3 의 ablation, 그리고 sparsity 를 만드는 메커니즘이 "고손실 샘플의 그래디언트 억제" 임을 FIM-quadratic 으로 형식화한 §4 의 분석입니다. 결과적으로 백본·데이터 파이프라인·옵티마이저를 일체 건드리지 않고 *손실 한 줄* 만 바꿔, 메모리 오버헤드 0 으로 PriorVLA / VLM2VLA / VLA-Adapter 류의 prior-preservation 효과에 도달한다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 후보 base: `pi0` / `pi05` family. 두 백본 모두 flow-matching head 의 표준 SFT loss 가 명시되어 있어, *동일 loss 위에 $`\omega = \mathrm{sg}(\exp(-\mathrm{loss}/\tau))`$ 를 곱하는 in-place 변경* 으로 매핑 가능. `smolvla` 도 후보지만 본 논문 검증 backbone 은 아님. `act` / `diffusion` 은 flow-matching 이 아니므로 Eq. 3 의 ELBO 환원 가정이 그대로 성립하지 않아 *직접* 매핑은 불가, 손실 가중 아이디어만 차용 가능.

---

## 🚧 미해결 / 잠정

- per-sample loss 텐서의 *세부 형상* — flow-matching denoise timestep 별 loss 를 어떻게 1 샘플당 스칼라로 reduce 하는지는 본문에 명시 없음. (Eq. 5 는 sample-level scalar 로 표기.) → 가정: timestep 평균.
- shape 4 변수 (λ, c, κ, ω_min) 가 *고정 가능* 하다는 주장은 LIBERO/RoboTwin 두 도메인에서만 검증. dexterous hand / sim2real 도메인 전이 시 재튜닝 필요 여부 미정.
- $`\mathcal{L}_{\mathrm{behavior}}=0`$ oracle 가정이 sample 의존적 demo noise 분포에서도 무해한지 — Appendix B.1 의 "global scalar 흡수" 논증은 sample-iid noise 가정에 가까움.
- ODE 적분 trajectory 의 multi-step 추론 오차에 대한 형식적 상한은 *없음* (저자 본인 §6 한계 명시).
- 코드 공개 여부 — 프로젝트 페이지 [tyzhang2907.github.io/ConservativeSFT](https://tyzhang2907.github.io/ConservativeSFT/) 만 본문 명기. (본문에 누락 — 추정으로 채움: 페이지 직접 확인 필요.)
- $`\pi_{0}`$/$`\pi_{0.5}`$ 모두 같은 hyperparameter set 으로 통하는지 — Table 5 는 단일 표만 제시. backbone 별 ablation 부재.
