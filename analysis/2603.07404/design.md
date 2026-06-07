# Design — Adaptive Capacity Allocation for Vision Language Action Fine-tuning

> PROBE design 산출물 (Layer 1, vendor-agnostic). 단일 한글 문서이며,
> 영문 1차 파일은 없습니다. `/analyze-paper` 가 `analysis/<id>/analysis.md` 와
> 함께 자동 생성합니다 — 알고리즘 명세를 base 좌표계 없이 추출합니다.
> base 매핑은 `/implement-design` 단계에서 이루어집니다. 형식·이모지·용어 규칙은
> `docs/STYLE.md` §6 / §4 를 정확히 따릅니다. 재실행 시 이 파일을
> 덮어씁니다.

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Adaptive Capacity Allocation for Vision Language Action Fine-tuning |
| 링크 | [arXiv:2603.07404](https://arxiv.org/abs/2603.07404) |
| 분석 문서 | [`analysis/2603.07404/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-07 |

---

## 🧮 데이터 계약

LoRA-SP는 backbone 내부 선형 레이어에 끼우는 adapter이므로, 데이터 계약은 "한 레이어의 입출력" 단위로 정의됩니다(모달리티 단위가 아니라 레이어 단위).

- **입력** — 레이어 활성화 `x`: shape `(B, …, d_in)`, dtype float (backbone과 동일 precision). 정규화는 backbone 내부 규약을 따름(adapter는 추가 정규화 없음).
- **출력** — 갱신된 활성화: shape `(B, …, d_out)`. `y = W_0 x + ΔW(x) x`, 여기서 `ΔW(x) = U diag(s(x)) V`.
- **router 점수** — `s(x)`: shape `(B, …, r)`, dtype float, 비음(nonnegative, `∈ ℝ^r_{≥0}`). 초기 `r = 128`.
- **task 입출력(상위 backbone 계약)** — VLA 정책 입력은 멀티뷰 RGB(side-view + wrist) + 언어 instruction + (선택) proprioception, 출력은 action chunk. action head 손실은 flow matching. (원문은 backbone 표준 계약을 그대로 사용 — 세부 shape 명시 없음.)

---

## 🧰 모듈 인터페이스

```python
def lora_sp_router(x: Tensor) -> Tensor:
    """입력 x 로부터 vector별 비음 점수 s(x) ∈ R^r_{>=0} 산출 (2-layer MLP).
       h1 = phi(W1 x + b1); s = W2 h1 + b2 (비음 보장 활성화)."""

def select_active_rank(s: Tensor, eta: float) -> Tensor:
    """s_i^2 내림차순 누적 에너지 E_k 가 eta 를 처음 넘는 최소 k 까지 유지,
       나머지 인덱스의 점수를 0 으로 마스킹한 sigma(x) 반환."""

def lora_sp_forward(x: Tensor, W0: Tensor, U: Tensor, V: Tensor,
                    router, eta: float) -> Tensor:
    """y = W0 x + U @ diag(select_active_rank(router(x), eta)) @ V @ x."""

def spectral_loss(s: Tensor, eta: float) -> Tensor:
    """L_spec = 1 - E_k(x), 선택된 활성 집합의 누적 에너지 비율의 여(餘)."""
```

- **router** — 입력별·레이어별 점수 산출. 외부 호출: 없음(레이어 로컬). 출력은 select 단계로 전달.
- **select_active_rank** — 점수→활성 마스크. energy target `eta` 가 유일 외부 손잡이. 추론·학습 양쪽에서 동일하게 적용.
- **lora_sp_forward** — backbone 선형 레이어를 감싸는 wrapper. `W0` 동결, `U`/`V`/router만 학습.
- **spectral_loss** — select 결과를 받아 정규화 항 산출. 전체 손실에서 `1e-2` 가중.
- **router_loss** — balance loss + z-loss (전체 손실에서 `1e-3` 가중). MoE 라우팅 정규화 관례 차용.

---

## ⛓️ 불변식·가정

- (가정 1) — Eckart–Young–Mirsky: 절단 SVD `A_k = U Σ_k V^T` 는 Frobenius norm 기준 rank-`k` 최적 근사이며 상대 오차는 `√(1 - E(k))`. 이 항등식이 `eta`→오차 연결의 토대(원문 §III-A Proposition, 증명 포함).
- (가정 2) — router 점수 `s(x)` 는 비음이어야 함(singular value 역할). 음수 점수가 나오면 에너지·근사 오차 해석이 깨짐.
- (가정 3) — 초기 rank `r` 이 task-relevant 방향을 모두 덮을 만큼 충분히 넓어야 함(wide initialization, 본문 `r=128`). 너무 좁으면 prune이 capacity를 복구하지 못함.
- (가정 4) — task loss가 trivial collapse(소수 vector로의 조기 붕괴)를 막는다는 균형 가정. spectral loss만으로는 붕괴 위험이 있어 task loss와의 경쟁이 필수.
- (가정 5) — backbone `W0` 동결. adapter만 학습하므로 prior는 갱신 방향(`U diag(s) V`)으로만 변형됨.

---

## 📊 하이퍼파라미터·손실

- 누적 에너지: `E_k(x) = (Σ_{i=1}^k s_i(x)^2) / (Σ_{j=1}^r s_j(x)^2)` (Eq. 12)
- 활성 rank: `k = min{ k : E_k(x) ≥ η }`, 그 너머 singular value는 0 (§IV-C)
- 근사 오차 경계: `‖A - A_k‖_F / ‖A‖_F = √(1 - E(k))` (Eq. 4)
- spectral loss: `L_spec(x) = 1 - E_k(x)` (Eq. 13)
- 전체 손실: `L = E[L_task] + 1e-2 · E[L_spec] + 1e-3 · E[L_router]` (Eq. 14)
- 갱신: `ΔW(x) = U diag(s(x)) V`, `s(x) = W2 φ(W1 x + b1) + b2` (Eq. 9–11)

| 이름 | 값 | 출처 |
|------|----|----|
| `r` (초기 rank, 모든 모듈) | `128` | §IV-C |
| `η` (energy target) | `0.9` | §V-A, Table IV |
| `L_spec` 가중치 | `1e-2` | §IV-E, Eq. (14) |
| `L_router` 가중치 | `1e-3` | §IV-E, Eq. (14) |
| `L_task` | flow matching | §IV-E |
| `L_router` 구성 | balance loss [8] + z-loss [25] | §IV-E |
| router 구조 | 2-layer MLP (활성화 `φ`) | §IV-C, Eq. (10) |
| 옵티마이저 / 스케줄 / step | (원문에 명시 없음 — 가정으로 메움) | — |
| router 폭(hidden dim) / `φ` 구체형 | (원문에 명시 없음 — 가정으로 메움) | — |

---

## 🎯 평가 메트릭

- **지표** — task 성공률(%) · **임계값** — 표준 LoRA·Full FT 대비 비교(절대 임계 없음) · **비교 baseline** — Full FT, LoRA(`r=128`), LoRA-MoE(top-1 / weighted-sum), AdaLoRA
- **효율 지표** — Active Rank(per-token, 전 레이어 평균) + Trainable/Total 파라미터 비율(%). LoRA-SP는 `π0` active rank 76 / SmolVLA 60으로 full FT에 필적
- **핵심 수치** — 표준 LoRA 대비 multi-task 평균 성공률 `π0` +23.3%p, SmolVLA +31.6%p (§V-B, Table I)
- **체제** — single-task vs multi-task 학습 양쪽에서 성공률 측정(Table II); `η` ablation으로 accuracy–efficiency trade-off 곡선 보고(Table IV)

---

## ✨ 변경 의도 (intent)

고정 rank LoRA는 robotics 전이의 높고 가변적인 본질적 rank를 단일 hyperparameter로 강제해, 이질적 task가 같은 저차원 부분공간을 공유하며 간섭(cross-task interference)을 일으킵니다. LoRA-SP는 `ΔW=BA` 를 SVD-형 `U diag(s(x)) V` 로 일반화하고, 작은 router가 입력·레이어별로 비음 점수(=데이터 조건부 singular value)를 내게 한 뒤, 누적 에너지 `E_k(x)≥η` 로 활성 rank를 자동 절단합니다. 여기에 spectral loss가 에너지를 소수 방향에 집중시켜 활성 rank를 점진적으로 줄입니다. 결과적으로 "어떤 rank를 쓸지"라는 sweep 문제를 학습 가능한 capacity 할당으로 바꿔, 모듈별 차등 capacity(vision 高 / language·action 低)를 데이터로부터 발견하고 간섭을 줄여 multi-task 일반화를 끌어올립니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — adapter는 backbone 선형 레이어 wrapper이므로 특정 policy family에 묶이지 않습니다. 검증된 backbone이 `π0`(PaLIGemma 기반)·SmolVLA이므로 `pi0` / `smolvla` family와 가장 가깝고, action head 손실이 flow matching이라 `pi0`/`pi05` 계열 정합. PEFT/LoRA 주입 지점(attention·MLP 선형층)과 학습 손실에 `L_spec`·`L_router` 항을 더하는 부분이 매핑 핵심.

---

## 🚧 미해결 / 잠정

- 옵티마이저·learning rate·스케줄·총 학습 step·batch size 가 원문에 명시되지 않음 — `/implement-design` 단계에서 foundry 기본값으로 가정 필요.
- router의 hidden dimension, 비음 보장 활성화의 구체형(`φ` 및 출력 비음화 방식)이 본문에 불명확 — Eq. (10)은 `s∈ℝ^r_{≥0}` 만 명시.
- `L_router` 의 balance loss·z-loss 정확한 정의/계수가 인용([8],[25])으로만 제시됨 — 재구현 시 원 논문 정의 필요.
- adapter를 주입하는 정확한 모듈 집합(어느 선형층에 LoRA-SP를 거는지)이 명시되지 않음 — Fig.6은 vision tower/language/action expert에 모두 적용됨을 시사.
- 동적 활성 rank의 실제 추론 비용(런타임/메모리) 절감이 정량화되지 않음 — Layer 1 스펙으로 굳히지 못함.
