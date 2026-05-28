# Design — Rethinking Muon Beyond Pretraining: Spectral Failures and High-Pass Remedies for VLA and RLVR

> PROBE design 산출물 (Layer 1, vendor-agnostic). 단일 한글 문서이며,
> 영문 1차 파일은 없습니다. `/analyze-paper` 가 `analysis/<id>/analysis.md` 와
> 함께 자동 생성합니다 — 알고리즘 명세를 base 좌표계 없이 추출합니다.
> base 매핑은 `/implement` 단계에서 이루어집니다. 형식·이모지·용어 규칙은
> `docs/STYLE.md` §6 / §4 를 정확히 따릅니다. 재실행 시 이 파일을
> 덮어씁니다.

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Rethinking Muon Beyond Pretraining: Spectral Failures and High-Pass Remedies for VLA and RLVR |
| 링크 | [arXiv:2605.19282](https://arxiv.org/abs/2605.19282) |
| 분석 문서 | [`analysis/2605.19282/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-05-26 |

---

## 🧮 데이터 계약

본 알고리즘은 옵티마이저 단위 모듈이므로 robot/VLA 입력 텐서가 아니라 *gradient/momentum 행렬* 이 입력입니다.

- **입력** — `momentum`: 모멘텀 누적치 $`\mathbf{M}\in\mathbb{R}^{m\times n}`$ (각 layer 의 2D weight 모양), dtype `float32` (혹은 모델과 동일 fp 정밀도; NS 안정성 위해 fp32 권장), 정규화 없음 (NS 내부에서 Frobenius 정규화).
- **입력** — `weight`: 현재 weight $`\mathbf{\Theta}\in\mathbb{R}^{m\times n}`$, dtype 모델 정밀도.
- **입력** — `gradient`: 현재 stochastic gradient $`\mathbf{G}\in\mathbb{R}^{m\times n}`$, dtype 모델 정밀도.
- **입력 (per-head 모드 전용)** — `head_dim`: attention projection 의 head 분할 정보 `(num_heads, head_dim)`. reshape 시 $`\mathbb{R}^{d\times d}\to\mathbb{R}^{H\times d_h\times d}`$ 로 head 차원 분리.
- **출력** — `weight_next`: 갱신된 weight $`\mathbf{\Theta}'\in\mathbb{R}^{m\times n}`$, dtype 모델 정밀도. `weight_next = weight - lr · highpass_NS(momentum)` 의 형태.
- **내부 상태** — 매 step 의 정규화된 momentum $`\mathbf{X}\leftarrow \mathbf{M}/(\|\mathbf{M}\|_F+\epsilon)`$, singular value 가 $`[0,1]`$ 범위. 출력 update direction 의 spectral norm 은 $`\approx 1`$ (suppression 후 leading σ 가 1 에 고정).

---

## 🧰 모듈 인터페이스

```python
def pion_step(
    weight: Tensor,          # (m, n) — 현재 가중치
    grad: Tensor,            # (m, n) — 현재 stochastic gradient
    momentum_buffer: Tensor, # (m, n) — 이전 step 까지의 momentum
    lr: float,
    momentum_coef: float,    # μ
    k_p: int,                # Promotion step 수
    k_s: int,                # Suppression step 수 (총 NS step = k_p + k_s, default k=5)
    per_head: bool = False,
    num_heads: int | None = None,  # per_head=True 일 때 필수
    eps: float = 1e-7,
) -> tuple[Tensor, Tensor]:  # (weight_next, momentum_next)
    """Pion 한 step. Muon 과 동일한 컨트롤 플로우, NS 내부 다항식만 high-pass."""

def highpass_ns(
    X: Tensor,               # (m, n) (또는 per-head 시 (H, d_h, n))
    k_p: int,
    k_s: int,
    promotion_coefs: tuple[float, float, float] = (1.875, -1.25, 0.375),
    suppression_coefs: tuple[float, float, float] = (0.0,   2.5,  -1.5),
    eps: float = 1e-7,
) -> Tensor:
    """
    1) X <- X / (||X||_F + eps)
    2) Promotion 다항식 f_p 를 k_p 회 in-place:  X <- a X + b X X^T X + c X (X^T X)^2
    3) Suppression 다항식 f_s 를 k_s 회 in-place
    4) 반환 — Muon msign 자리의 대체 행렬
    """

def ns_polynomial_step(
    X: Tensor,
    a: float, b: float, c: float,
) -> Tensor:
    """단일 NS 다항식 step: a X + b (X X^T X) + c (X (X^T X)^2)."""
```

- 모듈 책임 — `pion_step` 은 학습 루프가 호출하는 외부 API, `highpass_ns` 는 NS 다항식 시퀀스, `ns_polynomial_step` 은 한 step 의 5차 다항식 적용.
- 외부 호출 계약 — gradient/loss 와는 무관(옵티마이저는 backward 결과만 받음). LR 스케줄러는 일반 cosine/linear 사용 가능 — Muon 과 동일 인터페이스.
- **per-head 모드** — `X` 가 attention projection 일 때 `(d, d) → (num_heads, d_h, d)` 로 reshape 후 `vmap` 또는 batched matmul 로 `highpass_ns` 적용. 나머지 단계 동일.

---

## ⛓️ 불변식·가정

- (가정 1) — Frobenius 정규화 직후 $`\mathbf{X}`$ 의 모든 singular value 는 $`[0,1]`$ 에 갇힌다 ($`\|\mathbf{X}\|_2 \le \|\mathbf{X}\|_F \le 1`$).
- (가정 2) — NS 한 step 은 $`(\mathbf{U},\mathbf{V})`$ 를 보존하고 각 $`\sigma_i`$ 를 스칼라 다항식 $`f(\sigma)=a\sigma+b\sigma^3+c\sigma^5`$ 로 독립 reshape 한다.
- (가정 3, Promotion) — $`f_p(1)=1`$, $`f_p'(1)=0`$, $`f_p''(1)\le 0`$ 가 동시에 성립 → σ=1 이 maximum 이며 unstable 하지 않음.
- (가정 4, Promotion 단조성) — $`f_p'(\sigma)\ge 0`$ on $`[0,1]`$ — 본 논문 권장 계수에서는 $`f_p'(\sigma)=1.875(1-\sigma^2)^2`$ 로 perfect square.
- (가정 5, Suppression) — $`f_s(1)=1`$, $`f_s'(1)=0`$, $`f_s'(0)=0`$ — 원점 근처에서 1차 항이 0 이라 고차 항이 작은 σ 를 0 으로 끌어당긴다.
- (가정 6, gradient 구조) — Pion 의 이득은 momentum 행렬의 spectrum 이 "leading 소수의 informative head + long noisy tail" 구조를 가질 때 실현된다. 이 구조가 없으면 Muon 대비 우위가 보장되지 않는다 (VLA action 모듈·RLVR policy gradient 에서는 성립).
- (가정 7, per-head) — attention projection 의 head dim 이 명확히 정의돼 있고 (standard MHA), $`d = H\cdot d_h`$ 로 정확히 나뉜다. GQA / MQA 처럼 K/V head 수가 Q 와 다른 경우는 본 논문에 명시 없음 — 가정으로 메움 필요.
- (가정 8, per-step cost) — $`k=k_p+k_s=5`$ 고정 시 Pion 의 per-step FLOP 은 Muon 과 같다.

---

## 📊 하이퍼파라미터·손실

본 알고리즘은 손실을 추가하지 않습니다. 외부 loss 는 원 모델 그대로 (VLA: $`\ell_1`$-regression 또는 flow-matching; RLVR: GRPO/GMPO objective).

- 가중치 update 식: $`\mathbf{\Theta}_t = \mathbf{\Theta}_{t-1} - \eta \cdot \text{highpass\_NS}(\mathbf{M}_t)`$
- Momentum 식: $`\mathbf{M}_t = \mu\,\mathbf{M}_{t-1} + \mathbf{G}_t`$
- NS 다항식: $`f(\sigma;a,b,c)=a\sigma+b\sigma^3+c\sigma^5`$

| 이름 | 값 | 출처 |
|------|----|------|
| `k` (총 NS step) | `5` | §5, Pion algorithm |
| `k_p` (Promotion step) | `{0,1,…,5}`, 권장 `k_p` 작게 | §5 (단일 hyperparameter) |
| `k_s` (Suppression step) | `k - k_p`, 권장 `≥ 3` | §5 |
| `(a_p, b_p, c_p)` | `(1.875, -1.25, 0.375)` | Eq. (7) |
| `(a_s, b_s, c_s)` | `(0, 2.5, -1.5)` | Eq. (8) |
| `μ` (momentum coef) | (원문에 구체 명시 없음 — Appendix H 참조 필요) | §3 |
| `η` (learning rate) | (원문에 구체 명시 없음 — Appendix H 참조 필요) | §3 |
| `ε` (Frobenius 정규화 작은 상수) | `≥ 0` (값 미명시) | §3 |
| Optimizer 배치 (VLA) | action 2D → Pion, vision/language 2D → Muon, 기타 → AdamW | §6.1 |
| Optimizer 배치 (RLVR) | 전 2D → Pion (per-head), 기타 → AdamW | §6.1, §5 |
| 모드 (VLA) | default (per-head 아님) | §5, §6.2 |
| 모드 (RLVR) | per-head | §5, §6.3 |

---

## 🎯 평가 메트릭

이 알고리즘 자체는 옵티마이저이므로 *외부 task 메트릭* 으로 평가합니다.

- **VLA 성공률 (LIBERO 4-suite)** — `success_rate` (%). 비교 baseline: AdamW, Muon. 임계값 — 본 논문은 LIBERO Object 1,500 step 에서 Pion 100% vs Muon 97% vs AdamW 32.2% 보고.
- **VLA robustness (LIBERO-Plus)** — perturbation 별 성공률. 임계값 — Language·Noise·Robot perturbation 에서 Pion 이 Muon 대비 각각 +9%p, +6%p, +6%p.
- **실로봇 성공률 (Franka, π $`_{0.5}`$, 3 task × 30 trial)** — `success_rate` (%). 비교 baseline: AdamW (31.1%), Muon (38.9%) → Pion 85.6%.
- **RLVR accuracy (MATH500, GSM8K test)** — `accuracy` (%). 비교 baseline: AdamW (양의 학습 곡선), Muon (≈0%로 collapse), Pion (AdamW 추월).
- **Gradient SNR (진단용)** — $`\text{SNR}(\mathbf{G}) = \|\mathbb{E}[\mathbf{G}]\|_F^2 / \mathbb{E}\|\mathbf{G}-\mathbb{E}[\mathbf{G}]\|_F^2`$. SFT 대비 GRPO 가 낮음을 보이는 데 사용 (§4, Fig. 2-(a)).
- **Effective rank (진단용)** — $`\text{erank}(\mathbf{G}) = \exp(H(\mathbf{p}))`$ where $`p_i = \sigma_i / \sum_j \sigma_j`$. 모듈별 gradient 의 저-rank 정도 측정 (§4, Eq. 4).
- **학습 효율 (진단)** — 동일 budget 에서 도달 success rate (Fig. 5-(b)) 또는 동일 목표 도달 step (실로봇 20,000 step).

---

## ✨ 변경 의도 (intent)

Pion 은 Muon 의 "균일 spectral whitening (모든 σ → 1)" 을 "spectral high-pass (큰 σ → 1, 작은 σ → 0)" 로 대체합니다. SVD 나 sketching 을 쓰지 않고, NS 다항식 계수를 closed-form 제약으로 재유도해 *같은 per-step 비용* 으로 구현합니다. 기존 LRMuon 류 (top-k SVD/sketching) 가 약 $`15\times`$ 학습 비용을 요구하던 문제를 NS 다항식 교체만으로 해결한다는 점이 결정적 차이입니다. 한편 attention projection 을 head 차원으로 reshape 해 head 별 norm 이질성을 보존하는 per-head 모드는 RLVR 에서 Muon collapse 를 회복시키는 보조 장치입니다. 이 변경은 손실·스케줄·모델 구조를 건드리지 않는 drop-in optimizer 이므로 실무 도입 비용을 가장 낮춰 줍니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 후보 base 없음 (lerobot 은 policy/training entry point 중심이고 옵티마이저 자체는 PyTorch 표준에 의존). 실제 매핑은 `policies/*/configuration_*.py` 의 optimizer config 와 `optim/optimizers.py` 류에 Pion 클래스를 추가하는 형태가 될 가능성이 높음 — `/implement` 단계에서 확인.

---

## 🚧 미해결 / 잠정

- `μ` (momentum coefficient), `η` (learning rate), `ε` (Frobenius 정규화 상수) 가 본문 §5 에 표로 정리되어 있지 않음 — Appendix H 의 task 별 표를 별도로 파싱해야 확정할 수 있음. 현재는 원문에 명시가 없어 Appendix 를 참조해야 한다고 보류해 둡니다.
- VLA / RLVR 각각의 `(k_p, k_s)` 권장 조합이 본문 §5 에서는 "k_s ≥ 3" 의 일반 가이드만 제시 — task 별 정확한 값은 Appendix H 의 표를 확인해야 함.
- per-head 모드의 reshape 가 grouped-query attention (GQA) / multi-query attention (MQA) 구조 (Q, K, V head 수가 비대칭) 에서 어떻게 정의되는지 본문에 명시되지 않음 — Qwen3 의 attention 변형 여부에 따라 가정 필요.
- LPMuon (reverse ablation) 의 정확한 계수는 Appendix L 이 제약 다항식 최적화 결과로 제시함 — Layer 1 Design 에서는 "fitted polynomial coefficients" 수준으로만 표기하고 값은 Appendix L 참조로 보류합니다.
- Pion 의 default 모드 vs per-head 모드 선택 기준이 본문에서는 사후적 (VLA=default, RLVR=per-head) — head-norm 이질성을 사전 측정해 자동 선택하는 절차는 없음.
