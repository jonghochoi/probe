# Design — DexPIE: Stable Dexterous Policy Improvement from Real-World Experience

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | DexPIE: Stable Dexterous Policy Improvement from Real-World Experience |
| 링크 | [arXiv:2606.09615](https://arxiv.org/abs/2606.09615) |
| 분석 문서 | [`analysis/2606.09615/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-07-21 |

---

## 🧮 데이터 계약

**입력 (Actor / Critic 공통 관찰)**

- **이미지** — 다중 카메라 RGB 2 시점(전면 global D415 + 손목 close-range D435). 각 `(B, 3, 224, 224)`, 원본 640×480 → 224×224 bilinear. 25 Hz 동기.
- **Proprioception** — 로봇 상태(arm EEF / hand joint). shape `(B, D_proprio)`, dtype float32. 정규화 통계 출처는 원문 미명시.
- **Optimality 조건** — $`I_{t}\in[0,1]`$ (연속). sinusoidal 임베딩 후 proprio·시각 특징과 concat. 학습 시 확률 `p_m=0.3` 로 null 마스킹.

**출력 (행동)**

- **행동 청크** — `(B, H=24, D_action)`. 행동 공간 = **relative EEF action(arm)** ⊕ **absolute joint action(dexterous hand, Inspire RH56DFX 6-DoF)** concat. arm 은 현재 관찰 기준 상대 변위, hand 는 절대 관절 명령.
- **비동기 padding** — 배포 시 이전 청크의 남은 행동을 현재 관찰 $`o_{t+m}`$ 좌표계로 변환해 다음 청크의 relative-action prefix 로 concat(최대 지연 `n=4`).

**Critic 출력**

- **Value 분포** — $`p_{\phi}(V\mid o_{t})`$: `(B, B_bins=201)` softmax 분포. value 는 분포 기댓값으로 산출.

---

## 🧰 모듈 인터페이스

```python
def actor_diffusion(obs, proprio, optimality_I, eta) -> Tensor:
    """optimality-조건 U-Net DDPM 디퓨전 정책. R3M 시각 인코더 + sinusoidal(I)
       + proprio concat 조건. relative-EEF ⊕ absolute-hand-joint 청크(H=24) 예측."""

def critic_distributional(obs, proprio) -> Tensor:
    """동결 R3M 특징 + proprio → 4-layer MLP → B=201 value bin softmax.
       value = Σ v_b · p_b (분포 기댓값)."""

def continuous_optimality(advantage, q_low, q_high, alpha) -> Tensor:
    """f = sigmoid(alpha*(A - q_low)/(q_high - q_low)). q_low/q_high 는
       데이터셋-수준 advantage quantile. 비음·단조증가 → 개선 보장."""

def staged_dagger_collect(policy, env) -> Trajectories:
    """rollout 을 초기 상태 + 선택된 중간 stage 에서 초기화. 실패 시 동일 stage
       복원 후 개입 → 실패-교정 쌍 수집. exploring-starts 근사."""

def human_following_intervene(T_v_t0, T_ee_t0, T_v_t) -> SE3:
    """개입: ΔT_v = (T_v_t0)^-1 · T_v_t; T_ee = T_ee_t0 · ΔT_v.
       hand 는 retargeted glove action 으로 대체(전환 시 smoothing)."""

def async_relative_padding(A_t, o_t, o_tm) -> Tensor:
    """training-time RTC 확장: A_t 의 남은 행동을 o_t→o_tm 좌표계로 변환,
       다음 청크 A_{t+1} 의 relative prefix 로 사용. 학습 시 앞 i(0≤i≤n)개 마스킹."""
```

- **Actor ↔ Critic** — critic 은 먼저 오프라인 데이터셋(데모 + 자율 rollout + 개입)에서 학습해 advantage 추정과 데이터셋-수준 quantile(`q_low`, `q_high`)을 산출; 그 뒤 actor 를 optimality-조건으로 개선. loss 는 분리(critic CE / actor DDPM).
- **Optimality 부여 규칙** — 데모·인간개입 구간에는 `I_t = 1` 직접 부여; 그 외 자율 rollout 은 `I_t = f(advantage)`.
- **Optimizer** — AdamW($`\beta_{1}=0.95`$, $`\beta_{2}=0.999`$, lr `1e-4`), actor bs 256 / critic bs 512.

---

## ⛓️ 불변식·가정

- **(개선 보장 조건)** — optimality 함수 $`f`$ 는 advantage 의 **비음·단조증가** 함수여야 product-policy 개선(참조 정책 대비)이 성립(cfgRL 정리). sigmoid 는 이 조건을 만족하며 유계.
- **(quantile 상대화)** — `q_low`, `q_high` 를 데이터셋-수준 advantage **분위수**로 잡아 advantage 절대 스케일에 무관해야 함. 고정 임계값이면 스케일 변동에 취약.
- **(시간 정렬)** — 배포 rollout 이 데모 행동 스트림과 시간적으로 정렬되어야 critic 이 일관된 정책이 유도한 value 를 학습. 정렬이 깨지면(동기 추론의 action stall) 이질적 혼합 value 로 credit assignment 가 불안정.
- **(상대 좌표 재참조)** — 비동기 prefix 는 남은 행동을 현재 관찰 좌표계로 변환한 **상대** 행동이어야 연속 스트림이 성립. 절대 좌표면 관찰 시점 불일치로 stall.
- **(중간 앵커)** — staged DAgger 의 후반-단계 궤적이 short-horizon return 을 제공해 long-horizon value 추정을 짧은 하위문제로 분해. 초기 상태만 초기화하면 후반 상태 value 관측이 희소.
- **(다봉 value)** — 이질적 초기상태·행동정책·결과품질이 다봉 return 분포를 유도하므로 분포형 critic(soft label + CE) 필요. 스칼라 회귀는 평균화로 붕괴.
- **(시각 관찰 충분성 — 잠정)** — critic 이 시각+proprio 만으로 실패 원인을 귀속할 수 있어야 함. 원인이 관찰에 안 보이면(테이블 충돌, 접촉/힘) 오귀속 → 정책 전파. 원문은 이런 궤적 **필터링**을 임시 대응으로 제시.

---

## 📊 하이퍼파라미터·손실

- 연속 optimality 함수 (Eq. 7):

$$f\!\left(A^{\pi_{\mathrm{ref}}}(o_{t},a_{t})\right)=sig\left(\frac{\alpha\left(A^{\pi_{\mathrm{ref}}}(o_{t},a_{t})-q_{\mathrm{low}}\right)}{q_{\mathrm{high}}-q_{\mathrm{low}}}\right)$$

- Actor 손실 (Eq. 8), optimality-조건 DDPM:

$$\mathcal{L}_{\mathrm{actor}}=\mathbb{E}_{\mathcal{D},\eta}\left[\left\|\boldsymbol{\epsilon}-\boldsymbol{\epsilon}_{\theta}\left(\tilde{\mathbf{a}}_{t:t+h},o_{t},I_{t},\eta\right)\right\|_{2}^{2}\right]$$

- Critic 손실 (Eq. 6), Gaussian soft label 과의 cross-entropy:

$$\mathcal{L}_{critic}(\phi)=\mathbb{E}_{(\tau,t)\sim\mathcal{D}}\left[H\left(\mathbf{q}(\tau,t),p_{\phi}(V\mid o_{t})\right)\right]$$

- 보상 (Eq. 9): $`r_{t}=0`$ (성공 종료), $`-C_{\mathrm{fail}}`$ (실패 종료), $`-1`$ (그 외); $`C_{\mathrm{fail}}`$ = 과제별 최대 에피소드 길이.
- Advantage: $`A^{\pi}(o_{t},a_{t})=\sum_{l=t}^{t+N-1}\gamma^{l-t}r_{l}+\gamma^{N}V^{\pi}(o_{t+N})-V^{\pi}(o_{t})`$.

| 이름 | 값 | 출처 |
|------|----|----|
| `q_low`, `q_high` | `0.6`, `0.8` (advantage quantile) | A.3 |
| `alpha` (optimality 온도) | `5` | A.3 |
| `beta` (guidance strength) | `1.5` | A.3 |
| `p_m` (optimality mask) | `0.3` | A.3 |
| `p_m^pre` (action-prefix mask) | `0.9` | A.3 |
| `H` (action chunk) | `24` | A.3 |
| `n` (async 최대 지연) | `4` steps | A.3 |
| `N` (N-step return) | `24` | A.3 |
| denoising steps (inference) | `10` | A.3 |
| `B` (critic value bins) | `201` | A.3 |
| `gamma` (discount) | `1` | A.3 |
| MC return 정규화 | 최대 에피소드 길이로 정규화 후 `[-1, 0]` clip | A.3 |
| optimizer | AdamW $`\beta_{1}=0.95`$, $`\beta_{2}=0.999`$, lr `1e-4` | A.3 |
| batch size | actor `256`, critic `512` | A.3 |
| epochs | actor `300`, critic `250` | A.3 |
| 인코더 | R3M (actor 학습 / critic 동결) | A.3 |
| 제어 주파수 | `25` Hz | A.1 |

---

## 🎯 평가 메트릭

- **지표** — Success Rate(%), **50 회 시행** 기준, 사후학습 1 iteration 후.
- **과제** — Task A(병 pick-and-place) / Task B(서랍 열기+티슈 배치) / Task C(뚜껑 열기+캔디 배치). 모두 long-horizon dexterous.
- **비교 baseline** — 참조 BC 디퓨전 정책(warm-start), HG-DAgger(성공 rollout 만 모방), RECAP(이진 optimality 라벨, `q_low=0.6`).
- **임계값(달성)** — DexPIE +37%(vs 참조, 종합, 최대) · 비동기 vs 동기 +14%(Task B) · staged vs 표준 DAgger +8%(Task C). (per-task 절대 성공률은 원문 Fig. 5 막대그래프로만 제시 — 텍스트 미추출.)

---

## ✨ 변경 의도 (intent)

DexPIE 는 실세계 배포 경험으로 dexterous 정책을 개선하는 사후학습 프레임워크로, 세 축에서 선행연구를 넘습니다. (1) 개입 시스템 — incremental EEF 제어의 비직관성을 human-as-follower(개입 전 로봇 자세 정렬) leader-follower 방식으로 대체해 임의 상태에서의 dexterous 교정을 가능케 합니다. (2) 데이터·정렬 — staged DAgger 로 중간 단계 앵커를 확보해 long-horizon credit assignment 를 분해하고, 상대 행동 공간의 비동기 추론(training-time RTC 확장)으로 배포 rollout 을 데모와 시간 정렬해 demonstration-deployment gap 을 줄입니다. (3) 핵심 알고리즘 신규성 — RECAP 의 **이진** optimality 라벨을 **연속** sigmoid optimality 로 대체(Eq. 7)해 행동 품질의 상대 순서를 보존하고, 이를 product-policy/CFG 관점(디퓨전 정책을 optimality 로 조건화)으로 안정 개선합니다. 지수 매핑이 소수 고-advantage 샘플에 신호를 몰아주는 것과 달리 sigmoid 의 매끄럽고 유계한 성질이 강건한 세밀 개선을 제공한다는 것이 차별 논거입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — Actor 는 U-Net DDPM 디퓨전 정책이므로 `diffusion` family 가 base 후보로 가장 가깝습니다. 다만 DexPIE 의 핵심 신규성(분포형 critic, 연속 optimality-conditioning, CFG-through-optimality, staged DAgger + 상대공간 비동기 추론)은 lerobot 의 기존 순수-BC `diffusion` 정책에 직접 대응하는 모듈이 없어, critic·optimality·async 파이프라인은 별도 사후학습 래퍼로 이식해야 할 가능성이 큼(`/implement-design` 가 매핑 가능성 판정). `rtc` 컴포넌트가 비동기 추론 부분과 부분적으로 대응할 수 있음.

---

## 🚧 미해결 / 잠정

- 관찰(proprio)·행동(relative EEF ⊕ absolute joint)의 정규화 통계 출처가 본문 미명시 — "데이터셋 전체 평균/표준편차" 로 가정 필요.
- `D_proprio` / `D_action` 의 정확한 차원(UR5 EEF 표현 방식 + Inspire hand 관절 수 매핑)이 본문에 수치로 명시되지 않음.
- staged DAgger 의 "중간 단계(intermediate stage)" 선택이 **수동**이라, 어느 stage 를 앵커로 고르는지의 알고리즘적 규칙은 Layer 1 스펙으로 굳혀지지 않음(원문도 사람이 선택).
- 보상 설계가 π\*_0.6 의 progress-based reward 를 "따른다"고만 하고 progress 정의 세부는 본 논문에 재기술되지 않음 — 재현 시 π\*_0.6 참조 필요.
- Gaussian soft label 의 폭 $`\sigma`$ 값이 본문에 명시되지 않음(식 (4)에 기호만 등장).
- flow-matching backbone(π 계열)으로의 optimality-conditioning + CFG 이식 방식은 원문 범위 밖(DDPM 기준 설계).
