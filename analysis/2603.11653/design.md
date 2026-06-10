# Design — Simple Recipe Works: Vision-Language-Action Models are Natural Continual Learners with Reinforcement Learning

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Simple Recipe Works: Vision-Language-Action Models are Natural Continual Learners with Reinforcement Learning |
| 링크 | [arXiv:2603.11653](https://arxiv.org/abs/2603.11653) |
| 분석 문서 | [`analysis/2603.11653/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-05-28 |

---

## 🧮 데이터 계약

이 논문은 새 아키텍처가 아니라 **연속 RL 학습 절차(레시피)** 를 제안하므로, GRPO + LoRA로 작업을 순차 적응시키는 학습 루프의 입출력이 곧 데이터 계약입니다.

- **입력(관측)** — 카메라 RGB 이미지 $`s_t`$: shape `(B, C, H, W)`, 자연어 지시 $`\ell`$ 토큰 시퀀스. (원문은 해상도/채널 수를 §3.1 수준에서 "camera images"로만 명시 — 구체 값은 base VLA 규약에 따름.)
- **입력(작업 흐름)** — 고정 순서의 작업열 $`\{\mathcal{T}_1,\dots,\mathcal{T}_T\}`$, 각 작업은 $`(\ell^k, r^k)`$ 쌍. $`T`$ = 4–5 (벤치마크별, §D Table 4).
- **출력(행동)** — 엔드이펙터 포즈 + 그리퍼 명령. LIBERO 계열은 7차원 행동 시퀀스(엔드이펙터 포즈 + 그리퍼 상태). 자기회귀형은 행동 토큰 시퀀스, 연속형은 flow ODE 적분 결과.
- **보상** — 희소 보상 $`r:\mathcal{S}\times\mathcal{A}\times\mathcal{L}\rightarrow\{0,1\}`$.
- **학습 신호 단위** — 에피소드 rollout. group size 8, rollout epochs 16 (§F).
- **정규화** — 행동/관측 정규화는 base VLA 규약 상속 (원문에 별도 명시 없음 — 가정으로 메움).

---

## 🧰 모듈 인터페이스

함수/클래스 시그니처 수준의 경계만 기록합니다. 핵심은 GRPO 손실, LoRA 어댑터 주입, 연속 학습 루프, 그리고 평가 지표 계산입니다.

```python
def grpo_loss(logp_new, logp_old, advantage, eps_low=0.20, eps_high=0.28):
    """GRPO clipped surrogate. ρ = exp(logp_new - logp_old), Â = (R - μ_R)/σ_R."""

def group_advantage(returns):
    """그룹 내 리턴을 표준화: Â = (R - μ_R) / σ_R (group size = 8)."""

def apply_lora(weight_W0, rank=32):
    """W = W0 + B A, B∈R^{d×r}, A∈R^{r×k}, r≪min(d,k). W0 고정, B·A만 학습."""

def flow_sde_sample(v_theta, x0, sigma_schedule):
    """연속형 VLA용: dx_t = v_θ(x_t,t) dt + σ_t dW_t 로 결정론적 flow를 확률 정책화."""

def sequential_finetune(policy, task_stream):
    """작업 k 도착 시 그 작업에만 GRPO+LoRA로 fine-tune. 이전 작업 데이터/환경 접근 없음."""

def eval_metrics(success_matrix_S, S0, held_out_H):
    """AVG, NBT, FWT, ZS 계산 (§B Eq.1–4)."""
```

- `sequential_finetune` — Seq. FT 레시피의 핵심. 망각 방지 장치(정규화/리플레이/격리) **없음**. 하이퍼파라미터 튜닝 없음(§4.1).
- `grpo_loss` — KL 계수 $`\beta = 0.0`$. 명시적 KL 페널티 대신 on-policy 샘플링의 암묵 정규화에 의존.
- `apply_lora` — backbone 동결, 저랭크 어댑터만 학습. 학습 후 $`W_{\text{new}}\leftarrow W_0+BA`$ 병합 가능.
- `eval_metrics` — ZS는 본 논문 도입 지표(held-out 작업 평균 성공률).

---

## ⛓️ 불변식·가정

- **(가정 1)** — on-policy 업데이트는 현재 정책 $`\pi_\theta`$ 가 이미 지지(support)를 가진 영역에서만 확률 질량을 재분배하며, $`\pi_0`$ 에서 거의 0 확률인 행동에 갑자기 높은 확률을 줄 수 없다. 따라서 forward KL $`\mathrm{KL}(\pi_\theta\|\pi_0)`$ 의 점진적 증가만 허용된다(§5.1). 이 성질이 깨지면(예: off-policy/SFT) 망각 억제가 무효.
- **(가정 2)** — 모델 차원 $`d`$ 가 충분히 커서 임의 두 단위벡터가 거의 직교($`\sqrt{d}\langle u,v\rangle\rightarrow\mathcal{N}(0,1)`$)하므로 대부분 방향의 그래디언트 업데이트가 사전학습 지식에 거의 영향을 주지 않는 "null space"가 존재한다. 작은 모델(12M)에서는 이 가정이 약해진다(Fisher energy 0.02 vs 0.16).
- **(가정 3)** — 희소 보상 RL의 에피소드당 정보량은 O(1) 비트로, rank-32 LoRA 용량(약 100M 파라미터)이 이를 흡수하기에 충분하다. 보상이 밀집해 에피소드당 정보가 길이에 비례하면 가소성 보존 논거가 깨진다(§5.2).
- **(가정 4)** — 세 요소(큰 사전학습 모델 · LoRA · on-policy RL)는 **상보적**이며 어느 하나라도 제거하면 망각이 급증한다(Table 3). on-policy RL 단독으로는 불충분(§5.1).
- **(가정 5)** — 모든 작업이 동일 상태·행동 공간을 공유하고, 작업 정체성은 자연어 지시 $`\ell`$ 로 관측 가능(latent 아님, §3.2).

---

## 📊 하이퍼파라미터·손실

- GRPO 손실 식 (§A):

$$\max_{\theta}\;\mathbb{E}_{(s_{t},a_{t})\sim\pi_{\theta_{\text{old}}}}\left[\min\!\left(\rho_{t}(\theta)\,\hat{A},\;\mathrm{clip}(\rho_{t}(\theta),1-\epsilon,1+\epsilon)\,\hat{A}\right)\right]$$

$$\rho_{t}(\theta)=\frac{\pi_{\theta}(a_{t}\mid s_{t},\ell)}{\pi_{\theta_{\text{old}}}(a_{t}\mid s_{t},\ell)},\quad\hat{A}=\frac{R-\mu_{R}}{\sigma_{R}}$$

- LoRA: $`W=W_{0}+BA`$, $`B\in\mathbb{R}^{d\times r}`$, $`A\in\mathbb{R}^{r\times k}`$, $`r\ll\min(d,k)`$.
- 연속형 VLA용 Flow-SDE: $`dx_{t}=v_{\theta}(x_{t},t)\,dt+\sigma_{t}\,dW_{t}`$.
- 망각 진단 — Fisher energy: $`E_{F}(\mathbf{g})=\frac{\mathbf{g}^{\top}\mathbf{F}\mathbf{g}}{\mathbf{g}^{\top}\mathbf{g}}=\frac{\sum_{d}f_{d}g_{d}^{2}}{\sum_{d}g_{d}^{2}}`$, 대각 근사 $`f_d=\mathbb{E}[g_d^2]`$, $`\max_d(f_d)`$ 로 정규화.

- 공유 하이퍼 (§F, Table 6):
  | 이름 | 값 | 출처 |
  |------|----|----|
  | Optimizer | AdamW | §F, Table 6 |
  | Learning rate | $`2\times10^{-5}`$ | §F, Table 6 |
  | AdamW $`\beta_1 / \beta_2`$ | `0.9 / 0.999` | §F, Table 6 |
  | AdamW $`\epsilon`$ | $`10^{-5}`$ | §F, Table 6 |
  | Gradient clip norm | `1.0` | §F, Table 6 |
  | Global batch size | `8192` | §F, Table 6 |
  | Discount $`\gamma`$ | `0.99` | §F, Table 6 |
  | GAE $`\lambda`$ | `0.95` | §F, Table 6 |
  | Clip ratio (low/high) | `0.20 / 0.28` | §F, Table 6 |
  | KL coefficient $`\beta`$ | `0.0` | §F, Table 6 |
  | Entropy bonus | `0.0` | §F, Table 6 |
  | Rollout epochs | `16` | §F, Table 6 |
  | Group size | `8` | §F, Table 6 |
  | LoRA rank | `32` | §F, Table 6 |

- 방법별 하이퍼 (§G, Table 7) — Seq. FT는 추가 하이퍼 없음. 참고: EWC $`\lambda=1\times10^6`$, ER/DER $`\lambda_{\mathrm{replay}}=0.03`$, SLCA slow/fast LR $`4\times10^{-6} / 4\times10^{-5}`$, RETAIN merge $`\lambda=0.5`$.

---

## 🎯 평가 메트릭

- **지표** — `AVG` (최종 평균 성공률, Eq.1) · **임계값** — 높을수록 좋음, 오라클(multitask)이 상한 · **비교 baseline** — Multitask Oracle.
- **지표** — `NBT` (망각, Eq.2) · **임계값** — 낮을수록 좋음, 본 논문 결과는 일관되게 < 2% (음수 가능) · **비교 baseline** — 0 = 망각 없음.
- **지표** — `FWT` (순방향 전이, Eq.3) · **임계값** — 양수가 유익한 전이 · **비교 baseline** — 작업 순서 의존.
- **지표** — `ZS` (held-out 성능, Eq.4) · **임계값** — 높을수록 좋음, Seq. FT가 오라클을 자주 상회 · **비교 baseline** — Multitask Oracle ZS, 초기 체크포인트 대비 $`\Delta\mathrm{ZS}`$.
- **메커니즘 진단** — `Fisher energy E_F` (큰 모델 0.02 vs 작은 모델 0.16), per-layer effective rank (LoRA 29.3±2.16 vs full-FT 208.6±148.5), nuclear norm (0.259 vs 0.609).

---

## ✨ 변경 의도 (intent)

기존 CRL 통념은 Seq. FT를 catastrophic forgetting에 취약한 하한으로 보고 정규화·리플레이·파라미터 격리 같은 복잡한 기법을 덧붙였습니다. 이 논문은 "큰 사전학습 VLA + LoRA + on-policy RL"이라는 조합에서는 그런 장치 없이 단순 Seq. FT만으로 stability–plasticity 트레이드오프가 재편됨을 실증하고 해부합니다. 핵심 변경은 알고리즘 추가가 아니라 **제거** — 망각 방지 장치와 하이퍼파라미터 튜닝을 모두 빼고, 망각 억제를 학습 동역학(목표·제약·용량의 시너지)에 맡기는 것입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — base 후보는 자기회귀형 토큰 정책(OpenVLA-OFT/OpenVLA 계열)과 flow-matching 정책 양쪽에 걸칩니다. lerobot family 중 `pi0` / `pi05`(flow-matching head + Flow-SDE 변형) 또는 자기회귀형이면 `smolvla` 와 가깝습니다. 다만 이 논문은 정책 아키텍처가 아니라 **GRPO 연속 학습 루프 + LoRA 어댑터 + 평가 지표**가 본질이므로, lerobot의 정책 클래스보다는 RL 학습 스크립트/`rtc` 및 LoRA 주입 지점에 매핑될 가능성이 높습니다.

---

## 🚧 미해결 / 잠정

- 관측/행동 텐서의 정확한 shape·정규화 통계는 원문이 "camera images / 7-dim action" 수준으로만 명시 — base VLA 규약을 따른다는 가정으로 메움.
- $`\sigma_t`$ 노이즈 스케줄의 구체 형태는 Flow-SDE(Chen et al., 2026) 참조로만 언급 — 원문에 수치 명시 없음.
- Seq. FT가 오라클보다 ZS에서 우위인 원인은 저자도 미해결("implicit regularization 가설")로 남김 — Layer 1 스펙으로 굳히지 않음.
- $`\Delta\mathrm{AVG}`$/$`\Delta\mathrm{ZS}`$ 의 정확한 정의(초기 체크포인트 대비 변화)는 §4.2 표 각주 수준 — 본 분석은 본문 표기 그대로 보존.
