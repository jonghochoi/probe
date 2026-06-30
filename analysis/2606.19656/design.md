# Design — DF-ExpEnse: Diffusion Filtered Exploration for Sample Efficient Finetuning

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | DF-ExpEnse: Diffusion Filtered Exploration for Sample Efficient Finetuning |
| 링크 | [arXiv:2606.19656](https://arxiv.org/abs/2606.19656) |
| 분석 문서 | [`analysis/2606.19656/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-30 |

---

## 🧮 데이터 계약

DF-ExpEnse 는 사전학습 generative policy 의 가중치·입출력 계약을 **바꾸지 않고**, online 경험 수집 단계의 **action selection 만** 가로채는 wrapper 입니다. 시간 축은 절대 step 이 아니라 `T_action`(diffusion 한 번이 내는 action chunk horizon) 과 후보 인덱스 `M`, fleet 인덱스 `N` 으로 표현합니다.

**입력**

- **상태** `s`: shape `(B, D_state)` (또는 정책이 요구하는 멀티모달 관측 dict — 이미지/proprio/언어). dtype·정규화는 base diffusion policy 의 계약을 그대로 상속.
- **diffusion/flow policy** `pi_dp`: 상태 조건부 action 분포 sampler. 한 호출이 action chunk `(B, T_action, D_action)` 를 냄. DSRL 통합 시 noise selector 를 거치고, ResFiT 통합 시 base + residual 을 더함(부록 G/H).
- **초기 정책** `pi_dp_init`: BC-SR 용 freeze 된 사전학습 정책(또는 noise selector 우회 + Gaussian noise). 계약은 `pi_dp` 와 동일.
- **critic ensemble** `Q_[1..K]`: 상태-행동 입력에 scalar 를 내는 Q-함수 `K` 개. RL 토대(SAC/residual)가 최적화에 쓰는 그 ensemble 을 재사용.

**출력**

- **실행 행동** `a_star`: shape `(B, T_action, D_action)`, dtype float. 후보 집합에서 (fleet-정규화) 탐색 관심도 argmax 로 선택된 단일 행동.
- **(부수) 후보별 점수** $`e_m`$ / $`\bar{e}_{n,m}`$: shape `(N, M)`, dtype float. 선택용 내부 값(로깅 가능).
- **replay 튜플** `(s, a_dp, a_star, r, s')`: RL 토대의 buffer 계약에 그대로 추가(`a_dp` 는 noise/residual 학습용 중간 산물).

---

## 🧰 모듈 인터페이스

base 좌표(file:line) 없이 함수 시그니처 수준의 호출 계약만 기록합니다.

```python
def sample_candidates(pi_dp, s, M: int) -> Tensor:
    """현재 상태 s 조건으로 diffusion/flow policy 에서 M 개 후보를 i.i.d. 샘플 (Eq. 1).
       반환 shape (M, B, T_action, D_action). 연속 행동 공간을 'tractable 후보 집합'으로
       필터링하는 단계 — DF-ExpEnse 전체의 토대."""

def apply_bc_sr(candidates: Tensor, pi_dp_init, s, p: int) -> Tensor:
    """후보 집합의 앞 p(<=M) 개를 초기 사전학습 정책 샘플로 덮어씀 (Eq. 4–5).
       multimodal prior 의 inference-time 보존 — mode collapse 방지.
       p=0 이면 무연산. 반환 shape 동일."""

def exploration_interest(Q_ensemble, candidates: Tensor, s, alpha: float) -> Tensor:
    """각 후보의 value(min over ensemble) + alpha*disagreement(std over ensemble) (Eq. 2).
       alpha=0 이면 순수 exploitation(Max-Q). 반환 (M,) 또는 (N, M)."""

def fleet_normalize(v: Tensor, d: Tensor, alpha: float) -> Tensor:
    """fleet 전체(N x M) value·disagreement 를 각각 z-정규화한 뒤 결합 (Eq. 9–11).
       v, d: shape (N, M) → 반환 bar_e: shape (N, M).
       N=1 이면 정규화가 무의미(고립 에이전트)."""

def select_action(candidates: Tensor, scores: Tensor) -> Tensor:
    """관심도 argmax 후보를 선택 (Eq. 3 / 12). (선택) score 가중 sampling 대안 가능(App. E).
       반환 a_star: shape (B, T_action, D_action)."""

def df_expense_step(pi_dp, pi_dp_init, Q_ensemble, states, *, M, K, p, alpha) -> Tensor:
    """fleet 한 timestep 의 전체 절차: 각 에이전트 후보 샘플 → BC-SR → value/std →
       fleet 정규화 → per-agent argmax. base RL 의 optimize() 는 변경 없음."""
```

- 호출 계약: `df_expense_step` 은 RL 토대의 **online rollout 루프 안**에서 `policy.act(s)` 를 대체합니다. optimization( $`Q`$ 업데이트, noise/residual 정책 업데이트)은 토대 그대로(부록 G/H Algorithm 1/2 의 27–28행).
- critic ensemble 은 **읽기 전용 재활용** — DF-ExpEnse 는 Q 를 학습하지 않고 평가에만 씁니다(학습은 토대 담당).
- fleet 통신 계약: `fleet_normalize` 는 매 timestep 전 에이전트의 `(v, d)` 를 모으는 **동기 all-gather** 를 전제. 비동기/분산 환경에서는 latency 가정이 깨짐(🚧 참조).

---

## ⛓️ 불변식·가정

- **(가정 1) 데이터 양·최적화 불변** — DF-ExpEnse 는 수집되는 timestep 수와 RL 최적화 스킴을 vanilla 와 **동일하게** 유지해야 한다. 성능 차이를 "수집 데이터의 질"로만 귀속시키는 논문의 인과 주장이 이 불변식에 의존한다. 수집량이나 update 규칙이 바뀌면 ablation 해석이 무효가 된다.
- **(가정 2) 후보 multimodality** — `sample_candidates` 가 내는 `M` 개 후보는 "기본 품질을 만족하면서 행동 공간을 넓게 커버"해야 한다. 정책이 unimodal 로 붕괴하면 모든 후보가 한 mode 에 몰려 선택이 무의미해진다(BC-SR 는 이 가정을 방어하는 장치이지 보장은 아님).
- **(가정 3) critic 의 off-후보 평가 신뢰성** — `Q_[1..K]` 는 정책이 실제로 내지 않은 임의 후보 행동에 대해서도 의미 있는 value/disagreement 를 줘야 한다. off-policy critic(SAC) 에서 성립하며, on-policy(PPO) critic 에서는 깨질 수 있다.
- **(가정 4) min-value 의 overestimation 억제** — ensemble min 이 보수적 value 로 기능하려면 critic 들이 충분히 다양(독립 초기화)해야 한다. ensemble 이 작거나(2) 상관이 높으면 min 이 보수성을 잃고 std 가 noise 가 된다(2-critic 붕괴 결과).
- **(가정 5) fleet 동질성** — fleet z-정규화는 모든 에이전트가 **같은 critic·같은 임베디먼트·같은 태스크 분포**를 공유한다고 가정한다. 이질 fleet 에서는 `(v, d)` 분포가 섞이지 않아 정규화가 의미를 잃는다.
- **(가정 6) test-time 비활성 등가성** — 평가 rollout 에서 DF-ExpEnse 를 끄면 정책 행동이 vanilla 와 한 비트도 다르지 않아야 한다(공정 비교 + 추가 추론비용 0 의 전제).

---

## 📊 하이퍼파라미터·손실

DF-ExpEnse 는 **자체 손실항이 없습니다** — 최적화 손실은 전적으로 RL 토대(부록 G/H)에서 옵니다. DF-ExpEnse 가 더하는 것은 selection 식(아래)과 5개 하이퍼파라미터입니다.

- **탐색 관심도 (Eq. 2)**

$$e_{m}=\min\left(Q_{[1...K]}(\mathbf{a}_{m},\mathbf{s})\right)+\alpha*\text{std}\left(Q_{[1...K]}(\mathbf{a}_{m},\mathbf{s})\right)$$

- **fleet 정규화 관심도 (Eq. 9–11)** — $`\bar{e}_{n,m}=z(v_{n,m})+\alpha*z(d_{n,m})`$, 여기서 $`z(\cdot)`$ 는 fleet 전체 $`N\times M`$ 통계의 z-score
- **선택 (Eq. 3 / 12)** — 관심도 argmax 후보 $`\mathbf{a}^{\star}`$ 를 실행(fleet 시 $`\bar{e}_{n,m}`$ 기준)
- **BC-SR (Eq. 4–5)** — 후보 앞 $`p`$ 개를 `pi_dp_init` 샘플로 치환

- **하이퍼파라미터**

  | 이름 | 값 | 출처 |
  |------|----|----|
  | `candidate_set_size` (`M`) | `3` (default; ablation 5·7 포화) | §4.4, §4.8 |
  | `critic_ensemble_size` (`K`) | `10` (default; 5 에서 포화, 2 면 붕괴) | §4.4, §4.8 |
  | `fleet_size` (`N`) | `4` (default; 클수록 이득, 1 이면 무효) | §4.4, §4.8 |
  | `bc_sr_p` (`p`) | `1` | §4.4 |
  | `disagreement_weight` ($`\alpha`$) | `0.5` | §4.4 |
  | value 추정 | `min` over ensemble (mean 도 동등 — App. D) | §3.1, §D |
  | action selection | `argmax` (weighted sampling 도 대체로 동등 — App. E) | §3.1, §E |
  | (토대) RL 알고리즘 | DSRL=SAC noise selector / ResFiT=residual | §4.1 |
  | (토대) learning rate | `0.0003` | Table 3 |
  | (토대) batch size | `256` | Table 3 |
  | (토대) target update ($`\tau`$) | `0.005` | Table 3 |
  | (토대) discount ($`\gamma`$) | `0.99` (Square 0.999) | Table 1 |
  | action chunk size | `4` (Tool Hang 8) | Table 1 |
  | `pi_dp` inference denoising steps | `8` (RoboMimic) / `5` (Gym) / `10` (Tool Hang flow) | Table 1–2 |
  | initial collected steps | `0` (true sample-efficiency) | §A |

---

## 🎯 평가 메트릭

- **지표** — 환경 timestep 대비 **성공률(success rate)** · **임계값** — 동일 timestep 에서 vanilla(DSRL/ResFiT) 및 Max-Q·E3B·Plan2Explore 대비 ≥ 우위(곡선 상회) · **비교 baseline** — vanilla DSRL/ResFiT, Max-Q($`\alpha=0`$), E3B-State, E3B-DINO, Plan2Explore (RoboMimic·DexMimicGen).
- **지표** — timestep 대비 **ground-truth reward score** · **임계값** — 동일 timestep 에서 baseline 상회 · **비교 baseline** — vanilla DSRL, Max-Q (OpenAI Gym 이동).
- **지표** — **component-size 민감도**(ensemble/candidate/fleet) · **임계값** — ensemble 5≈10·2 붕괴, candidate 3≈5≈7 포화, fleet 클수록↑·1 무효 · **비교 baseline** — default(M3/K10/N4) (RoboMimic Can).
- **측정 프로토콜** — 100 rollout 평균 · 3 random seed mean±std · DF-ExpEnse 는 **test-time 비활성**(공정 비교 + 추가 추론비용 0).

---

## ✨ 변경 의도 (intent)

기존 UCB·ensemble 탐색은 모든 행동을 일일이 평가해야 해 이산 행동 공간에 묶여 있었고, 연속 공간에서는 별도 정책 ensemble 로 후보를 만들거나(Lee/Shi) value 최대만 고르는(EMaQ·Q-Chunking·Max-Q) 방식에 그쳤습니다. DF-ExpEnse 의 핵심 전환은 **diffusion policy 의 multimodal 성질 자체를 연속 공간의 필터**로 보는 것입니다 — 별도 후보 생성기를 두지 않고 정책에서 몇 개 샘플하면 "기본 품질 + 넓은 커버리지"의 열거 가능한 후보가 공짜로 생깁니다. 그 위에서 critic ensemble 을 (최적화뿐 아니라) **online inference 의 탐색 신호**로 재활용해 min-value UCB(품질=min, 불확실성=std)로 점수를 매깁니다 — E3B·Plan2Explore 가 요구하는 별도 dynamics 모델이 필요 없습니다. 여기에 두 보강이 붙습니다. BC-SR 는 finetuning 중 mode collapse 를 막으려 **초기 정책 샘플을 후보에 직접 섞어**(손실항이 아니라 후보 구성으로) multimodal prior 를 inference 시점에 보존하고, fleet normalization 은 병렬 fleet 을 단순 throughput 이 아니라 **협력 탐색**으로 전환해 — 각 에이전트가 자기 후보를 fleet 전체 분포로 z-정규화함으로써 — 집단 차원의 중복 수집을 피합니다. 결과적으로 추가 학습 모듈·test-time 비용 없이 finetuning sample-efficiency 만 끌어올리는, 토대 RL 에 직교로 얹히는 wrapper 가 됩니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — DF-ExpEnse 자체는 정책 **구조**를 바꾸지 않는 online RL 수집 wrapper 라, lerobot 의 imitation 학습 policy 라인(`pi0`/`diffusion`/`act`)에 직접 대응되는 base 가 없습니다. 가장 가까운 정렬점은 (1) 후보 샘플러로서 `diffusion` 또는 `pi0`(flow-matching) policy 의 sampling 경로, (2) critic ensemble·SAC 를 제공하는 외부 RL 토대(DSRL/ResFiT/rtc 계열) — lerobot 표준에는 critic·replay·RL 루프가 부재하므로 `vendor/lerobot/` 만으로는 부분 매핑(후보 샘플링)만 가능하고 RL 토대는 별도. `/implement-design` 가 `🚧 매핑 불가`(RL finetuning 루프 부재)를 낼 가능성이 높습니다.

---

## 🚧 미해결 / 잠정

- **on-policy 토대로의 이식** — 논문은 off-policy(SAC) critic ensemble 만 다룹니다. PPO 등 on-policy 토대에서 critic 의 임의-후보 Q 평가가 신뢰 가능한지가 본문에 없어, 그대로 이식 시 가정 3 검증이 선결입니다.
- **`p` sweep·prior 다양성** — BC-SR 는 `p=1` 한 값만 보고합니다. `p` 증가 효과, 초기 정책의 실제 multimodality 측정이 본문에 없어 "초기 정책이 더 multimodal"이라는 전제가 가정으로 남습니다.
- **탐색 게이팅 부재** — 매 timestep 탐색이 기본이며, 숙달 구간에서 탐색을 끄는 조건부 게이팅은 future work 로만 언급(App. F). Layer 1 스펙에는 "항상 켜짐"으로 굳혔습니다.
- **fleet 통신 모델** — 동기 all-gather 를 전제하나 실세계 분산의 latency·sharding 처리는 미명시. 로컬 클러스터 정규화는 future work(App. F).
- **DexMimicGen(ResFiT) 하이퍼파라미터** — "vanilla ResFiT 와 동일"로만 기술되어 구체 값이 본문에 없음(원문에 명시 없음 — 가정으로 메움: ResFiT 원논문 설정 상속).
- **diffusion 추론 비용 vs. `M`** — 100-step denoising base 에서 후보 `M` 회 샘플링의 실시간 비용이 본문에 정량화되지 않음. sample set 포화 결과는 큰 `M` 의 비효율을 시사.
