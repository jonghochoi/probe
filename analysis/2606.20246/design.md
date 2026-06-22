# Design — Finetuning Vision-Language-Action Models Requires Fewer Layers Than You Think

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Finetuning Vision-Language-Action Models Requires Fewer Layers Than You Think |
| 링크 | [arXiv:2606.20246](https://arxiv.org/abs/2606.20246) |
| 분석 문서 | [`analysis/2606.20246/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-22 |

---

## 🧮 데이터 계약

CLP 는 표준 VLA 의 입력/출력 텐서 계약을 **바꾸지 않는다** — 모델 깊이만 정적으로 줄인다. 별도로 pruning 결정을 위한 calibration 경로가 추가된다.

- **입력 (정책)** — `x_lang`: 토크나이즈된 언어 명령 `(B, L_text)`, int; `x_img`: RGB 관측 `(B, V, 3, H, W)`, float (V=카메라 수, backbone 정규화 그대로).
- **입력 (flow-matching head)** — `a_t`: 보간된 noisy action `(B, T_a, d_a)`, float, $`\mathbf{a}_{t}=(1-t)\epsilon+t\mathbf{a}`$ ; `t`: 시간 `(B,)` ∈ [0,1]; $`\epsilon\sim\mathcal{N}(\mathbf{0},\mathbf{I})`$ .
- **출력 (정책)** — 예측 velocity field `û_t = f_act(Z, a_t, t)`: `(B, T_a, d_a)`, float. action chunk 차원 `T_a × d_a` 은 backbone 별 native 값(원문에 절대 수치 명시 없음 — backbone 기본값 가정).
- **Pruning 부가 입력** — calibration set `D_cal`: 학습 episode 에서 뽑은 소량 표본(크기·구성 원문에 명시 없음 — "compact, sampled from training episodes" 만 명시). 모듈 `M` 별 layer activation `H̄^M_ℓ`: `(n_tokens, d)`, float (calibration 예제 token 을 concat).
- **불변 가정** — 같은 모듈 `M` 내 모든 transformer block 은 동일 hidden 차원 `d` 를 공유 → layer 제거 후 predecessor↔successor 단순 재연결 가능(reshape/projection 불필요).

---

## 🧰 모듈 인터페이스

```python
def compute_cka(H_prev: Tensor, H_cur: Tensor) -> float:
    """인접 layer hidden state 의 centered-linear-kernel CKA ∈ [0,1].
    CKA = |H_cur^T H_prev|_F^2 / (|H_prev^T H_prev|_F · |H_cur^T H_cur|_F)."""

def layer_redundancy_scores(module: Module, D_cal) -> list[float]:
    """calibration 1-pass 로 각 layer activation H̄^M_ℓ 추출 후
    s^M_ℓ = compute_cka(H̄^M_{ℓ-1}, H̄^M_ℓ), ℓ = 2..L_M 반환."""

def select_removal_set(scores: list[float], tau: float, k: int) -> set[int]:
    """s_ℓ >= tau 인 연속 layer 를 block 으로 묶고(B_M),
    각 block 의 첫 layer r(B) 를 anchor 로 보존,
    후보 풀 P_M = ∪(B \ {r(B)}) 에서 TopK(s_ℓ, k) 를 제거 집합 R_M 으로 반환."""

def remove_layers(policy: Policy, R: set[int], module: str) -> Policy:
    """module 의 R 에 속한 transformer block 제거 + 앞뒤 재연결.
    auxiliary 파라미터/loss 없이 native objective 로 곧장 fine-tune 가능한
    더 작은 policy 반환."""
```

- **`compute_cka`** — 입력 hidden `(n, d)` 두 개, 출력 스칼라. 직교변환·등방 스케일 불변.
- **`layer_redundancy_scores`** — 입력 prunable 모듈 + `D_cal`, 출력 길이 `L_M − 1` 점수열. forward 1회만 사용(학습 없음).
- **`select_removal_set`** — block 군집화(τ) → anchor 보존 → TopK(k). `|P_M| >= k` 가 되도록 τ 보정 필요.
- **`remove_layers`** — 정적 구조 변형. 호출 후 표준 flow-matching `L_FM` 으로 fine-tuning(manifold restoration 단계).
- **호출 순서** — prunable 모듈 `M`(VLM backbone / action head / VL-self-attention / DiT head)마다 독립 실행 → 모두 제거 후 단일 fine-tuning.

---

## ⛓️ 불변식·가정

- **(가정 1) 동일 hidden 차원** — 모듈 `M` 내 모든 block 의 입출력 hidden 차원이 같아야 layer 제거가 단순 재연결로 성립(projection 삽입 불필요).
- **(가정 2) 깊이-중복 존재** — 인접 layer CKA 가 1에 근접하는 contiguous high-similarity plateau 가 실제로 존재. 이것이 없으면(예: 모든 layer 가 큰 변환) 제거 후보 풀이 비어 압축 불가.
- **(가정 3) block 첫 layer = functional anchor** — 각 high-similarity block 의 초기 layer 가 그 block 입력 표현 확립에 임계적이라는 가설. 그래서 anchor 만 보존하고 후속을 제거.
- **(가정 4) calibration 분포 대표성** — `D_cal` 의 CKA 통계가 deploy 분포의 layer 중복도를 근사. calibration 이 편향되면 redundant 판정이 틀림.
- **(가정 5) manifold restorability** — pruning 직후 수축한 latent 공간이 downstream fine-tuning 으로 원본 표현 다양체에 근접 복원 가능. 복원이 안 되면 성능 회복 실패.

---

## 📊 하이퍼파라미터·손실

- **학습 손실 (변경 없음)** — $`\mathcal{L}_{\text{FM}}=\mathbb{E}_{t,\mathbf{a},\epsilon}[\,\|f_{\text{act}}(Z,\mathbf{a}_{t},t)-(\mathbf{a}-\epsilon)\|_{2}^{2}\,]`$ (Flow Matching, native). CLP 는 손실에 항을 추가하지 않음.
- **Pruning 기준식** — $`s^{\mathcal{M}}_{\ell}=\mathrm{CKA}(\bar{H}^{\mathcal{M}}_{\ell-1},\bar{H}^{\mathcal{M}}_{\ell})`$ ; block: $`s^{\mathcal{M}}_{\ell}\geq\tau`$ ; 후보 $`\mathcal{P}_{\mathcal{M}}=\bigcup_{B}(B\setminus\{r(B)\})`$ ; 제거 $`\mathcal{R}_{\mathcal{M}}=\mathrm{TopK}_{\ell\in\mathcal{P}_{\mathcal{M}}}(s^{\mathcal{M}}_{\ell},k_{\mathcal{M}})`$ .

  | 이름 | 값 | 출처 |
  |------|----|----|
  | $`\tau`$ (similarity threshold) | (원문 미명시 — $`\lvert\mathcal{P}_{\mathcal{M}}\rvert\geq k_{\mathcal{M}}`$ 되도록 보정) | §4 |
  | `k_M` (pruning budget, π0) | 12 layers (VLM+Action expert, 원본 18) | §A.1, Table 5 |
  | `k_M` (GR00T-N1.5 VLM) | 5 (원본 12) | Table 5 |
  | `k_M` (GR00T-N1.5 VL-self-attn) | 3 (원본 4) | Table 5 |
  | `k_M` (GR00T-N1.5 DiT head) | 8 (원본 16) | Table 5 |
  | `k_M` (SmolVLA) | 10 (VLM+Action expert, 원본 16) | Table 5 |
  | pruning ratio (flat 성능 한계) | 최대 50% | §5, Fig.3(a,b) |
  | calibration pass | 1 forward | §1, §4 |
  | LIBERO fine-tune steps | 100k, global batch 64 | §A.4 |
  | RoboCasa fine-tune steps | 100k (π0 batch 48, GR00T batch 32) | §A.4 |
  | SimplerEnv fine-tune steps | 200k, batch 32 | §A.4 |

---

## 🎯 평가 메트릭

- **지표** — task success rate (%) · **임계값** — pruned 가 unpruned baseline 에 근접/초과(≲1%p 손실 또는 저데이터에서 향상) · **비교 baseline** — full-scale 모델, training-free pruning(FastV/DivPrune/EfficientVLA/ADP/SpecPrune), training-adaptive(MoLe-VLA).
- **효율 지표** — model size / trainable params / training time(hours) / GFLOPs / inference speed(ms). 목표: GFLOPs 최대 50%↓, training 1.38–1.94×↓, speedup 1.39–1.47×.
- **selection 검증** — CKA vs MSE / Cosine / random / keep-first 의 success-rate 안정성(CKA 가 baseline 에 가장 근접해야 우월).
- **저데이터 정규화** — 동일 시연 수에서 pruned − full success Δ (양수면 정규화 효과). 예: LIBERO 10% 77.7→84.6, SimplerEnv 16.6→20.0.
- **manifold restoration** — pruning 직후 vs fine-tuning 후 hidden state PCA 분포의 base 모델 정렬도(정성 진단).

---

## ✨ 변경 의도 (intent)

기존 VLA 효율화는 두 갈래였다 — (i) training-free token pruning/caching 은 추론만 가속하고 비싼 downstream fine-tuning 은 그대로 두며, (ii) training-adaptive(dynamic routing/early-exit/distillation)는 보조 모듈·추가 학습목표로 핵심 구조를 바꿔 학습 알고리즘과 마찰한다. CLP 의 의도는 **fine-tuning 이전에 CKA 로 중복 layer 를 단 한 번의 forward pass 로 식별·정적 제거**하여, 보조 파라미터·distillation·런타임 routing 없이 학습·추론·메모리를 **동시에** 줄이는 것이다. 결과 모델은 깊이만 작아진 동일 아키텍처이므로 native flow-matching 목표로 곧장 fine-tune 되고, 저데이터에서는 용량 감소가 implicit regularizer 로 작동해 성능이 오히려 향상된다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — backbone-agnostic 한 정적 layer 제거 + 1-pass CKA calibration 유틸로 매핑됨. 후보 base: `pi0` / `pi05` / `smolvla` (논문이 직접 다룬 π0·SmolVLA 계열) 의 transformer block 스택에 `remove_layers` 를 적용 — VLM backbone layer list 와 flow-matching action expert layer list 양쪽이 표적. action head 가 DiT 형태(GR00T 계열)면 별도 모듈로 취급. `act`/`diffusion` 처럼 VLM backbone 이 없는 family 는 action 쪽 transformer 깊이에만 부분 적용 가능.

---

## 🚧 미해결 / 잠정

- **τ 값·보정 절차** — 원문이 구체 값/탐색법을 주지 않음. "$`\lvert\mathcal{P}_{\mathcal{M}}\rvert\geq k_{\mathcal{M}}`$ 되도록 보정"만 명시 → 구현 시 grid/binary search 로 가정.
- **calibration set 크기·구성** — "compact, sampled from training episodes" 외 절대 수치 없음 → 데이터셋 소량 무작위 표본으로 가정.
- **CKA activation 풀링** — token 차원 `n` 을 calibration 예제 전반으로 concat 한다고만 함; 토큰 subset 선택/정규화 세부 미명시.
- **action chunk 차원 `T_a × d_a`** — backbone native 값 사용, 본문에 절대 수치 명시 없음 → backbone 기본값 가정.
- **block anchor 보존의 일반성** — "첫 layer 보존" 은 가설(§A.1); 일부 backbone 에서 마지막 layer 가 더 중요한 경우의 처리 미검증.
