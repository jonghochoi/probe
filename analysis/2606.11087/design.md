# Design — Test-Time Gradient Guidance of Flow Policies in Reinforcement Learning

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Test-Time Gradient Guidance of Flow Policies in Reinforcement Learning |
| 링크 | [arXiv:2606.11087](https://arxiv.org/abs/2606.11087) |
| 분석 문서 | [`analysis/2606.11087/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-10 |

---

## 🧮 데이터 계약

QGF 는 추론-시점 알고리즘으로, reference flow 정책과 critic 의 *학습* 은 표준(flow matching · IQL)이며 본 Design 은 추론 경로를 계약으로 굳힙니다.

- **입력** — `state` $`s`$: shape `(B, D_s)`, float. OGBench proprioceptive state(정규화 가정은 원문 미명시 — dataset 통계 가정).
- **입력** — `noisy action` $`a_t`$: shape `(B, h * D_a)`, float. action chunk(길이 $`h=5`$)를 평탄화한 고차원 벡터. $`a_0\sim\mathcal{N}(0,I)`$.
- **입력** — `flow time` $`t\in[0,1]`$: scalar(스텝 $`\delta=1/T`$, $`T`$=flow steps=10).
- **모듈 산출** — `velocity` $`v_\theta(s,a_t,t)`$: shape `(B, h * D_a)`, float.
- **모듈 산출** — `critic gradient` $`g=\nabla_{\hat{a}_1}Q(s,\hat{a}_1)`$: shape `(B, h * D_a)`, float.
- **출력** — `denoised action` $`a_1`$: shape `(B, h * D_a)`, float. 정책 분포 $`\pi_\theta(a\mid s)`$ 의 유효 샘플로 환경에서 하나씩 실행.

---

## 🧰 모듈 인터페이스

```python
def qgf_sample(s, v_theta, Q, guidance_weight, T) -> Tensor:
    """QGF 추론: reference flow 를 critic gradient 로 유도해 high-value action 을 샘플 (Algorithm 1)."""

def first_order_denoise(a_t, v, t) -> Tensor:
    """단일 큰 Euler 스텝으로 clean action 근사: a_hat_1 = a_t + (1 - t) * v (식 7)."""

def qgf_grad(Q, s, a_hat_1) -> Tensor:
    """근사 denoised action 에서 critic gradient 평가 (식 9, Jacobian = I): grad_{a_hat_1} Q(s, a_hat_1)."""
```

- `qgf_sample` — 책임: 추론 루프 전체. 입력 $`s`$, $`v_\theta`$(reference flow), $`Q`$(critic), `guidance_weight`($`\tau_g=1/\beta`$), $`T`$(flow steps); 출력 `a_1`. 외부 계약: `v_theta`·`Q` 의 *학습 방식에 불가지론적* (BC flow + IQL 이 기본값일 뿐).
- `first_order_denoise` — 책임: ODE 전체 적분을 대체하는 1차 근사. Jacobian 을 항등으로 두므로 `a_hat_1` 은 gradient 평가점일 뿐 적분 경로에 직접 쓰이지 않음.
- `qgf_grad` — 책임: critic 을 (근사적으로) 깨끗한 action 에서만 질의해 OOD gradient 회피. `Q` 의 backward 1회 호출.

---

## ⛓️ 불변식·가정

- (가정 1) — critic $`Q(s,a)`$ 는 denoised(clean) action 공간에서만 학습됐다. 따라서 gradient 평가점 $`\hat{a}_1`$ 은 항상 clean action 근방이어야 한다(noisy $`a_t`$ 에서 직접 질의 금지) — 이 불변식이 깨지면 OOD gradient 가 되어 편향.
- (가정 2) — Jacobian $`J=\partial\hat{a}_1/\partial a_t`$ 를 항등행렬 $`I`$ 로 대체해도 gradient 방향이 충분히 보존된다(저자 경험적 발견; 더 낮은 분산을 줌).
- (가정 3) — 1차 Euler 근사 $`\hat{a}_1=a_t+(1-t)v_\theta`$ 가 전체 ODE 해 $`\mathrm{ODE}(a_t)`$ 의 *충분히 좋은 mode-선택적* 대용이다 — 데이터셋 분포 전체 커버보다 좋은 mode 선택이 유리.
- (가정 4) — guidance 가중치 $`\tau_g=1/\beta`$ 가 적정 범위 내에 있다. 과도하면 action 이 manifold 밖으로 밀려(off-manifold) 성능이 다시 하락(Fig. 20).
- (가정 5) — reference BC 정책이 데이터 분포를 충분히 잘 표현한다. base 가 under-trained 이면 test-time 개선 여지가 작음(원문 한계).

---

## 📊 하이퍼파라미터·손실

- KL-정규화 RL 목표의 closed-form 해(식 3): $`\pi(a|s) \propto \hat\pi(a|s) \cdot \exp(Q(s,a))^{1/\beta}`$
- reference 정책 손실(식 2, flow matching): $`L_{\mathrm{FM}} = \mathbb{E}[ \| v_\theta(x_t, t) - (x_1 - x_0) \|_2^2 ]`$
- QGF gradient 추정량(식 9): $`\nabla_{a_t} Q(s, a_1) \approx \hat I^\top \nabla_{\hat a_1} Q(s, \hat a_1)`$, where $`\hat a_1 = a_t + v_\theta(s, a_t, t)\cdot(1-t)`$, $`\hat I = I`$
- denoising guidance 적분(Algorithm 1): $`a_{t+\delta} = a_t + \delta\cdot( v_\theta(s, a_t, t) + (1/\beta)\cdot g )`$, $`g = \nabla_{\hat a_1} Q(s, \hat a_1)`$

| 이름 | 값 | 출처 |
|------|----|----|
| `guidance_weight` (τ_g = 1/β) | 도메인별 튜닝, 범위 `{0.004,0.008,0.01,0.02,0.04,0.06,0.08,0.1,0.12}` | §6, Table 3·5 |
| `flow_steps` (T) | 10 | Table 1 |
| `action_chunk_horizon` (h) | 5 | §6.1, Table 1 |
| `discount` (γ) | 0.999 | Table 1 |
| `IQL_expectile` (τ) | 0.9 | Table 1 |
| `batch_size` | 1024 | Table 1 |
| `learning_rate` | 3e-4 | Table 1 |
| `offline_train_steps` | 5×10⁵ | Table 1 |
| `critic/actor_net` | [1024, 1024, 1024, 1024] | Table 1 |
| `critic_ensemble` | 2 (aggregate `min`) | Table 1 |
| guidance 학습률(GradStep 등 baseline) | (QGF 자체엔 없음 — gradient 는 velocity 에 직접 가산) | §5 |

---

## 🎯 평가 메트릭

- **지표** — OGBench task success(정규화 성능) · **임계값** — (절대 임계값 원문 미명시; 막대그래프 비교) · **비교 baseline** — test-time: BFN·GradStep·QFQL·BPTT·CFGRL·RobustQ; train-time: FQL·EDP·QAM·DAC·QSM+BC
- **보조 지표** — gradient 노이즈 민감도 $`\cos(G(s,a_t), G(s,a_t+\epsilon))`$ (Fig. 3); denoised action 의 $`Q`$-value (Fig. 4, 단 OOD exploit 함정 주의); test-time FLOPs (Fig. 6)
- **프로토콜** — single-task 20 tasks/10 seeds/500k steps; goal-conditioned 25 tasks/10 seeds/1M steps; 모든 비교군에 동일 IQL critic 사용

---

## ✨ 변경 의도 (intent)

기존 flow-정책 RL 은 (i) noisy action 에서 critic gradient 를 써 OOD 편향을 겪거나 (ii) 전체 denoising 을 역전파해 고분산·고비용·불안정합니다. QGF 의 변경 의도는, 단일 큰 Euler 스텝으로 근사한 *clean* action $`\hat{a}_1`$ 에서만 critic gradient 를 평가하고 denoised→noisy Jacobian 을 항등으로 버려, OOD 질의도 BPTT 도 피한 **저분산·저비용** guidance 추정량을 얻는 것입니다. 결과적으로 BC 정책 학습은 그대로 두고(actor-critic 공동 학습의 불안정성 제거) 추론 시점에만 reward 최적화를 적용해, 모델 크기 확장성과 critic-agnostic 한 plug-in 성질을 확보합니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — reference 정책이 state-조건 flow-matching velocity field + action chunking 이므로 `pi0` / `pi05`(flow-matching action expert) family 와 가장 가깝습니다. 다만 QGF 본체는 *추론 루프 수정 + 별도 critic* 이라, 정책 학습 코드 변경보다 sampling/inference 경로에 guidance 항을 삽입하는 형태로 매핑될 가능성이 높습니다. critic(`Q`) 학습은 lerobot 의 기존 BC 정책 family 밖이라 추가 구성요소가 필요합니다.

---

## 🚧 미해결 / 잠정

- state/action 정규화 통계의 출처가 본문에 없어 "데이터셋 전체 평균/표준편차" 로 가정.
- 정량 결과가 전부 막대그래프라 절대 success 임계값·수치를 Layer 1 스펙으로 굳히지 못함(분석 문서 §📊 참조).
- 학습 하드웨어 사양(GPU 종류/수, 학습 시간) 원문 미명시.
- goal-conditioned 실험의 DQC critic(Decoupled Q-Chunking) 세부 — $`h_c, h_a, \kappa_b, \kappa_d`$ 는 DQC 논문 인용 값으로, 본 논문 자체 튜닝이 아님(Table 4).
- $`\beta`$(=$`1/\tau_g`$)의 환경-독립 공통값 존재 여부 미해결 — 도메인별 튜닝이 필요(Table 3).
