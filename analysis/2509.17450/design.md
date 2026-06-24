# Design — Learning Dexterous Manipulation with Quantized Hand State

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Learning Dexterous Manipulation with Quantized Hand State |
| 링크 | [arXiv:2509.17450](https://arxiv.org/abs/2509.17450) |
| 분석 문서 | [`analysis/2509.17450/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-24 |

---

## 🧮 데이터 계약

시간 축은 의미 단위(`chunk_size` $`C`$)로 기록합니다. 손 차원 $`D_h`$ 는 본 논문에서 6(ROHand 6-DoF), 팔 차원 $`D_a`$ 는 RISE 의 end-effector pose 차원(원문 미명시, 통상 9–10)입니다.

**(1) VQ-VAE 학습 단계**
- **입력** — `hand_state` $`s^{(h)}`$: shape `(B, D_h)`, float, raw 손 관절/상태 값. (정규화 통계는 원문에 명시 없음 — 가정으로 메움: 데이터셋 전체 평균/표준편차)
- **출력** — `hand_state_recon` $`\hat{s}^{(h)}`$: shape `(B, D_h)`, float. 부산물: 인코더 latent $`z_e`$, 양자화 코드 $`z_q`$, 통합 codebook 인덱스 ∈ `{0..K-1}` (`K=16`).

**(2) Relabel 단계 (전처리, 학습 불필요)**
- **입력** — demonstration trajectory $`\{(o_i, s_i^{(a)}, s_i^{(h)})\}_i`$.
- **출력** — relabeled trajectory $`\{(o_i,(s_i^{(a)}, z_i^{(h)}))\}_i`$. $`z_i^{(h)}`$ 는 PCA-재정렬된 연속 스칼라 인덱스 (실수값, `{0..K-1}` 범위; chunk diffusion 에서 연속 회귀 대상).

**(3) Base visuomotor policy 단계**
- **입력** — `observation` $`o_i`$: RISE 형식(두 카메라 융합·워크스페이스 크롭 point cloud). shape/정규화는 base RISE 를 따름(원문 미명시).
- **출력** — action chunk $`\{(s_{i+k}^{(a)}, z_{i+k}^{(h)})\}_{k=1}^{C}`$: shape `(B, C, D_a + 1)`. 팔은 연속 pose, 손은 단일 연속 인덱스 채널.
- **추론 후처리** — 예측 $`\hat{z}^{(h)}`$ → nearest code `idx = round(ẑ^(h))` → codebook lookup 으로 $`s^{(h)}_{\text{idx}}`$ retrieve → 실행.

---

## 🧰 모듈 인터페이스

```python
def train_residual_vqvae(hand_states, codebook_size=4, num_layers=2):
    """손 상태 single-step 집합을 2-layer residual VQ-VAE 로 이산화. 통합 codebook(K=16) 반환."""

def reindex_codes_pca(codebook_states):
    """raw 6-DoF 손 상태(코드 대표값)에 PCA 적용 → 제1주성분 투영값으로 코드를 연속 재정렬.
       반환: code_index -> ordered_continuous_index 매핑."""

def relabel_dataset(trajectories, vqvae, reindex_map):
    """각 손 action a^(h) 를 양자화·재정렬된 연속 인덱스 z^(h) 로 교체한 trajectory 반환."""

def quantize_to_action(z_hat, codebook):
    """예측 연속 손 인덱스 ẑ^(h) -> nearest code idx=[ẑ^(h)] -> 손 상태 s^(h)_idx 실행값 retrieve."""
```

- `train_residual_vqvae` — 손실은 §📊 의 VQ-VAE 식. 출력 codebook 은 reindex·relabel·추론 후처리가 공유하는 단일 사전.
- `reindex_codes_pca` — **raw state 공간**에서 PCA(아니면 불변식 위배). VQ latent 공간 금지.
- `relabel_dataset` — 학습 불필요 전처리. base policy 의 손 출력 채널을 연속 스칼라 1개로 축소.
- `quantize_to_action` — 추론 시에만 호출. base policy 학습/손실에는 미개입(gradient 미통과).

---

## ⛓️ 불변식·가정

- (가정 1) — 손 모션의 지배적 변화는 raw 손 상태의 **제1주성분 1차원**으로 충분히 포착된다(continuous relaxation 의 전제). explained variance ratio 가 낮으면 무효.
- (가정 2) — 재정렬 후 **인접 코드 인덱스는 유사한 손 자세**에 대응한다(작은 예측 오차 → 작은 손 형상 변화). 이 단조성이 깨지면 nearest-code 사상이 불안정.
- (가정 3) — 팔과 손은 **동일 생성 패러다임(diffusion)** 으로 공동 생성된다. 손을 별도 classification head 로 떼면 gradient flow 충돌로 학습 붕괴(DQ-RISE-C 반례, 2.50%).
- (가정 4) — 과제별 손 action 분포는 $`K=16`$ 이산 코드로 재구성 가능(저-DoF·소수 패턴 과제 전제). 고-DoF·연속 재배향 과제에서는 위배 가능.
- (가정 5) — 손의 작은 부정확은 허용되나 팔의 작은 부정확은 치명적이라는 비대칭(손만 양자화하는 근거).

---

## 📊 하이퍼파라미터·손실

- VQ-VAE 손실 식:

$$\mathcal{L}=\|s^{(h)}-\hat{s}^{(h)}\|_{2}^{2}+\beta\|\text{sg}[z_{e}]-z_{q}\|_{2}^{2}+\gamma\|z_{e}-\text{sg}[z_{q}]\|_{2}^{2}$$

  ($`\text{sg}[\cdot]`$: stop-gradient, $`z_e`$: 인코더 latent, $`z_q`$: 양자화 코드.)

- Base policy diffusion 손실: 원문에 별도 식 없음 — RISE 의 diffusion 학습 목표를 그대로 사용(손 인덱스 채널을 팔 action 과 동일 회귀).

- 하이퍼:
  | 이름 | 값 | 출처 |
  |------|----|----|
  | `num_layers` (residual VQ-VAE) | `2` | §IV-A |
  | `codebook_size` (per layer) | `4` | §IV-A |
  | `K` (통합 코드 수) | `16` | §IV-A |
  | `beta` (commitment) | `1.67` | §IV-A |
  | `gamma` (codebook usage) | `1.67` | §IV-A |
  | VQ-VAE optimizer | `Adam` | §IV-A |
  | VQ-VAE learning rate | `3e-4` | §IV-A |
  | VQ-VAE batch size | `256` | §IV-A |
  | VQ-VAE epochs | `1500` | §IV-A |
  | demos per task | `50` | §IV-A |
  | chunk size `C` | (원문 미명시 — RISE 기본값) | §III-D |
  | policy 하이퍼 일반 | "follow RISE" | §IV-A |

---

## 🎯 평가 메트릭

- **지표** — task phase 별 success rate + 전체 평균 success rate · **임계값** — DQ-RISE 평균 `85.83%` (RISE `55.00%` / RISE-S `61.67%` / DQ-RISE-C `2.50%` 대비) · **비교 baseline** — RISE(결합), RISE-S(분리 diffusion), DQ-RISE-C(diffuse 후 분류)
- **프로토콜** — 과제당 20 trial, 매 trial 전 물체 위치 무작위화, 6개 실환경 과제.
- **Ablation 지표** — continuous relaxation(재인덱싱) on/off 비교(Open Jar). teleoperation user study: success rate / 완료시간(s) / 평균 rank.

---

## ✨ 변경 의도 (intent)

기존 visuomotor policy 는 팔·손 action 을 하나의 결합 공간에 합쳐(naive 결합) 고-DoF 손이 공간을 지배하거나, 둘을 따로 예측(naive 분리)해 협응을 깹니다. 본 알고리즘은 **손 single-step 상태를 $`K`$-코드로 양자화해 차원을 줄이되**(손=패턴 기억, 팔=localization 이라는 기능 분리), 그 이산 코드를 raw-state PCA 로 **연속 재정렬**해 팔 action diffusion 과 **동일 생성 과정에 통합**합니다. 핵심 차별점은 (1) action chunk 가 아닌 state 단위 양자화, (2) VQ latent 가 아닌 raw-state PCA 재인덱싱으로 코드에 연속·해석가능 순서 부여, (3) classification 대신 연속 회귀로 두어 단일 diffusion 의 gradient flow 일관성 보존입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — base RISE 는 point cloud 입력 diffusion policy 이므로 family 상 `diffusion`(Diffusion Policy)에 가장 가깝습니다(`pi0`/`smolvla` 의 VLM-flow 계열과는 입력·생성 방식이 다름). 단 lerobot 의 `diffusion` 은 2D 이미지 기반이라 point cloud 인코더는 직접 대응이 없습니다. 본 논문 기여의 핵심(손 상태 VQ 양자화 + PCA 재인덱싱 + relabel)은 base 와 무관한 **데이터 전처리 + action 채널 재정의** 이므로, base 정책 종류와 독립적으로 이식 가능합니다. 실제 매핑·UNMAPPABLE 판정은 `/implement-design` 가 수행합니다.

---

## 🚧 미해결 / 잠정

- chunk size $`C`$, diffusion step 수, base policy 세부 하이퍼는 "RISE 를 따른다" 로 위임되어 본문에 직접 값이 없습니다.
- 손 상태 정규화 통계의 출처가 본문에 없어 "데이터셋 전체 평균/표준편차" 로 가정했습니다.
- codebook 이 과제별로 학습되는지(=다과제 공유 가능 여부)가 본문에서 단정되지 않습니다("K=16 per task" 표현에 근거한 추정).
- residual VQ-VAE 의 latent 차원·인코더/디코더 구조 세부가 명시되지 않았습니다.
- base policy diffusion 손실에서 연속 손 인덱스 채널의 가중치/정규화가 팔 채널과 동일한지 명시되지 않았습니다.
