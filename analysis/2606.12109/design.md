# Design — Bridging the Morphology Gap: Adapting VLA Models to Dexterous Manipulation via Intent-Conditioned Fine-Tuning

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Bridging the Morphology Gap: Adapting VLA Models to Dexterous Manipulation via Intent-Conditioned Fine-Tuning |
| 링크 | [arXiv:2606.12109](https://arxiv.org/abs/2606.12109) |
| 분석 문서 | [`analysis/2606.12109/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-11 |

---

## 🧮 데이터 계약

InDex 는 두 stage 가 서로 다른 입출력 계약을 가진다. 공통 입력은 multi-view RGB + proprio + language.

- **입력 (관측)** — `images`: dual-view RGB(head global + wrist egocentric), shape `(B, 2, 3, H, W)`, uint8→정규화. `language`: token 시퀀스. `state` (proprio): `q_curr` 관절 상태, shape `(B, D_state)`. 관측 history = 4 step(`Observation Steps=4`).
- **출력 — Stage 1 (alignment)** — `a_arm`: 6-DoF arm reaching 명령 `(B, T, 6)`; `q_hand`: coarse 6-DoF hand 형상 `(B, T, 6)` → §3.2 로 스칼라 $`\gamma`$ (virtual grasp intent) `(B, T, 1)` 로 추상화. action expert terminal projection 차원 $`1 \to 6`$ 확장.
- **출력 — Stage 2 (adaptation)** — `a_dex`: fine-grained 손가락 관절 명령. prediction horizon `T=12`, 실행은 앞 `8` step(`Execution Steps=8`). 전체 action dim `12 (6_arm + 6_hand)`.
- **중간 표현** — `z_vis`: frozen VLM 시각 임베딩(독립 visual encoder 없이 backbone 에서 직접 추출); $`\gamma \in [0,1]`$: 스칼라 grasp intent.
- **정규화** — $`\gamma`$ 는 하드웨어별 `d_max`(pre-grasp 최대 개구)·`d_min`(완전 폐구)으로 min-max 정규화. arm/hand 회귀 타깃의 정규화 통계는 원문 미명시.
- **시간 축** — `chunk_size = Prediction Horizon = 12`, `obs_steps = 4`, `exec_steps = 8`. 제어 주파수 20 Hz(데이터 수집 기준).

---

## 🧰 모듈 인터페이스

```python
def task_space_intent(q_hand: Tensor) -> Tensor:        # (B,...,6) -> (B,...,1)
    """FDH-6 6-DoF 관절을 thumb-finger 거리 d_v 로 환산 후 γ∈[0,1] 로 정규화 (Eq. 1-2)."""

def stage1_align(obs: Obs) -> tuple[Tensor, Tensor]:
    """LoRA 주입된 π0.5 action expert: arm 6-DoF a_arm + coarse hand 6-DoF q_hand 예측.
       VLM backbone freeze, self-attention 에만 LoRA(rank16/alpha32). 손실 = Eq.3."""

def stage2_diffusion_head(z_vis: Tensor, q_curr: Tensor, gamma: Tensor,
                          k: int, a_k: Tensor) -> Tensor:
    """frozen backbone 표현 z_vis + proprio + intent γ 조건의 ε_θ 노이즈 예측.
       역확산 Eq.4 로 a_dex^0 복원, DDIM 샘플링. 손실 = Eq.5(MSE on noise)."""
```

- **`task_space_intent`** — forward kinematics `FK(·)` 로 thumb 끝 `p_th`, 4-finger 중심 `p̄_f` 산출 → 거리 → 정규화. 학습 파라미터 없음(순수 기구학 변환).
- **`stage1_align`** — 입력=관측, 출력=(arm action, hand intent). 외부 계약: VLM 동결, LoRA target=action expert self-attention, optimizer=AdamW, cosine LR decay 30k step. composite regression loss.
- **`stage2_diffusion_head`** — Stage 1 완료 후 backbone 전면 freeze(offline feature encoder 로 재활용). 조건 벡터 $`(\mathbf{z}_{vis}, \mathbf{q}_{curr}, \gamma)`$. K-step 역확산, DDIM 가속. loss=주입 noise 와 예측 noise 의 MSE.

---

## ⛓️ 불변식·가정

- (가정 1) — 다지 손의 grasp 진행이 thumb–finger 중심 거리라는 **1차원 manifold 로 충분히 표현** 된다(개폐로 환원 가능한 task 한정). 이 가정이 깨지면 intent 승계 전체가 무효.
- (가정 2) — `d_max`(pre-grasp)·`d_min`(완전 작동)이 하드웨어별로 **고정·기지(旣知)** 이며 $`d_{min} \le d_v \le d_{max}`$ 를 만족해 $`\gamma \in [0,1]`$ 보장.
- (가정 3) — Stage 1 정렬이 끝난 backbone 표현 `z_vis` 가 Stage 2 학습 전 구간에서 **불변(frozen)** — diffusion head 는 stationary 한 조건 분포 위에서 학습된다.
- (가정 4) — low-frequency(vision-language alignment)와 high-frequency(dexterous control) 학습 신호가 **같은 step 에서 섞이면 gradient 가 충돌** 하므로 시간축 분리가 필요(Coupled ablation 이 입증).
- (가정 5) — 인간 시연 분포가 multi-modal 이며 deterministic regression 으로는 평균-붕괴(manifold collapse) → diffusion 의 stochastic 디코딩이 필요.

---

## 📊 하이퍼파라미터·손실

- 손실 — Stage 1 (식 3):

$$\mathcal{L}_{total}=\lambda_{arm}\mathbb{E}\left[\left\|\mathbf{a}_{arm}^{*}-\hat{\mathbf{a}}_{arm}\right\|_{2}^{2}\right]+\lambda_{intent}\mathbb{E}\left[\left\|\mathbf{q}_{hand}^{*}-\hat{\mathbf{q}}_{hand}\right\|_{2}^{2}\right]$$

  Stage 2 (식 5):

$$\mathcal{L}_{diff}=\text{MSE}\left(\epsilon^{k},\epsilon_{\theta}(\bar{\alpha}_{k}\mathbf{a}_{dex}^{0}+\bar{\beta}_{k}\epsilon^{k},\mathbf{z}_{vis},\mathbf{q}_{curr},\gamma,k)\right)$$

- 역확산 (식 4):

$$\mathbf{a}_{dex}^{k-1}=\alpha_{k}\left(\mathbf{a}_{dex}^{k}-\eta_{k}\epsilon_{\theta}(\mathbf{z}_{vis},\mathbf{q}_{curr},\gamma,\mathbf{a}_{dex}^{k},k)\right)+\sigma_{k}\mathcal{N}(0,I)$$

  | 이름 | 값 | 출처 |
  |------|----|----|
  | `LoRA rank r` | `16` | §4.2, Table 1 |
  | `LoRA alpha` $`\alpha`$ | `32` | §4.2, Table 1 |
  | `learning_rate` | `5e-5` | §4.2, Table 1 |
  | `optimizer` | `AdamW` | §4.2, Table 1 |
  | `prediction_horizon` | `12` | §4.2, Table 1 |
  | `observation_steps` | `4` | §4.2, Table 1 |
  | `execution_steps` | `8` | §4.2, Table 1 |
  | `action_dim` | `12 (6_arm + 6_hand)` | §4.2, Table 1 |
  | `precision` (Stage 1) | `BF16` | §4.2 |
  | `lr_schedule` (Stage 1) | `cosine decay, 30k steps` | §4.2 |
  | $`\lambda_{arm}`$, $`\lambda_{intent}`$ | (원문 미명시) | §3.3 |
  | `K` (diffusion steps), $`\alpha_k/\eta_k/\sigma_k`$ schedule | (원문 미명시 — DDIM 사용만 명시) | §3.4 |
  | `d_max`, `d_min` | (원문 미명시 — 하드웨어별 보정값) | §3.2 |

---

## 🎯 평가 메트릭

- **지표** — `SR_reach` / `SR_grasp` / `SR_task` (3단계 누적 성공률 %) · **임계값** — reaching 은 target 거리 $`\epsilon`$ 이내, grasp 은 slip-free 안정 파지, task 는 전체 시퀀스 완수 · **비교 baseline** — MLP, BC-RNN, ACT, DP / OpenVLA, UniVLA, $`\pi_{0.5}`$.
- **프로토콜** — task 당 100 independent trial 평균, episode 최대 500 step, domain randomization(초기 물체 pose·조명). 4 task: Lift, Stack, Pick & Place, Nut Assembly.
- **결과 기준점** — $`\pi_{0.5}`$+InDex 평균 `92.8/88.3/85.8`; 최강 baseline $`\pi_{0.5}`$* `76.0/56.0/50.3`. ablation: w/o Intent 17.0 · Coupled 21.5 · MLP Head 47.5 · full 85.8 (task SR %).

---

## ✨ 변경 의도 (intent)

monolithic end-to-end fine-tuning 은 단일 backbone 이 low-frequency semantic 토큰을 high-DoF 연속 action 으로 직접 매핑하다 catastrophic forgetting + action manifold collapse 를 겪는다. InDex 는 (1) 사전학습된 1-DoF parallel grasp 출력을 버리지 않고 연속 virtual grasp intent $`\gamma`$ 로 **재해석(cross-morphology semantic inheritance)** 하고, (2) 학습을 시간축으로 2-stage 분리 — Stage 1 은 LoRA 로 backbone 을 arm+intent 에 정렬, Stage 2 는 backbone 을 freeze 한 채 intent-conditioned diffusion head 만 손가락 관절에 적응 — 해 low-freq/high-freq gradient 충돌을 끊고 prior 를 보존한다. 별도 visual encoder 없이 frozen backbone 표현을 직접 재사용해 sample 효율을 끌어올린다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — backbone 은 `pi05`(π0.5) family 와 직결(LoRA target = action expert self-attention, terminal projection 1→6 확장). Stage 2 손가락 head 는 `diffusion`(Diffusion Policy) family 의 conditional denoising head 와 가까움 — `pi05` + `diffusion` 두 family 를 결합·접합하는 형태의 매핑이 후보. intent 스칼라 conditioning 은 FiLM/concat 조건 주입으로 처리.

---

## 🚧 미해결 / 잠정

- $`\lambda_{arm}`$ / $`\lambda_{intent}`$ 가중 비율이 본문에 없어 Stage 1 composite loss 의 균형점을 가정해야 함.
- diffusion step 수 `K`, variance schedule $`\alpha_k/\eta_k/\sigma_k`$, DDIM step 수가 미명시 — Diffusion Policy 기본값으로 가정 필요.
- `d_max` / `d_min` 의 구체값과 측정 절차(FDH-6 기준)가 미명시 — 하드웨어 캘리브레이션으로 메워야 함.
- arm/hand 회귀 타깃의 정규화 통계(mean/std) 출처 미명시.
- `z_vis` 가 backbone 의 어느 layer/토큰에서 추출되는지(마지막 hidden state 가정), proprio `q_curr` 의 정확한 차원 구성이 본문에 미상.
- LoRA 가 self-attention 의 어느 projection(Q/K/V/O)에 적용되는지 세부 미명시.
