# Design — Safe and Steerable Geometric Motion Policies for Robotic Dexterous Manipulation

> PROBE design 산출물 (Layer 1, vendor-agnostic). 단일 한글 문서이며,
> 영문 1차 파일은 없습니다. `/analyze-paper` 가 `analysis/<id>/analysis.md` 와
> 함께 자동 생성하며, 알고리즘 명세를 base 좌표계 없이 추출합니다.
> base 매핑은 `/foundry` 단계에서 진행합니다. 형식·이모지·용어 규칙은
> `docs/STYLE.md` §6 / §4 를 정확히 따릅니다. 재실행 시 이 파일을
> 덮어씁니다.

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Safe and Steerable Geometric Motion Policies for Robotic Dexterous Manipulation |
| 링크 | [arXiv:2605.21811](https://arxiv.org/abs/2605.21811) |
| 분석 문서 | [`analysis/2605.21811/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-05-26 |

---

## 🧮 데이터 계약

SafePBDS 는 *학습된 모델* 이 아니라 *online QP 컨트롤러* 입니다. 따라서 입력 / 출력도 텐서가 아니라 매 제어 스텝의 상태와 가속도 명령입니다. 시간 축은 제어 스텝 `t`, batch 차원은 쓰지 않습니다.

- **입력 (상태)** — `(sigma, sigma_dot) ∈ T_sigma M`. shape `(m,)` 와 `(m,)`, dtype `float64` (QP solver 정밀도 가정). 정규화 가정 없음 — 원시 joint 좌표. 예: Franka 7-DOF + Allegro 16-DOF 결합 시 `m = 23`, IHR 모드 (arm 분리 제어) 시 `m = 16`.
- **입력 (behavior tasks)** — list of `(f_i, g_i, Phi_i, F_D_i, w_i)`, `i = 1..K`. `f_i: M → N_i` task map (forward kinematics + manifold 변환), `g_i` task manifold Riemannian metric, `Phi_i: N_i → R` potential, `F_D_i: TN_i → T*N_i` dissipative force, `w_i` weighting pseudometric on `TN_i`. *사용자가 사전에 디자인.*
- **입력 (safety tasks)** — list of `(f_j, h_0_j, kappa_j)`. `h_0_j: N_j → R` safety function (safe set 은 superlevel set `{h_0_j ≥ 0}`), `kappa_j = (kappa_1_j, kappa_2_j)` ECBF gain (또는 BCBF 의 경우 추가 `epsilon, mu_x, alpha`). ECBF / BCBF 인덱스 `J_E`, `J_B` 로 분리.
- **입력 (control tasks, 선택)** — list of `(f_l, g_l, w_l, u_l)`. `u_l ∈ T*N_l` force-like 입력. `L = 0` 이면 autonomous, `L > 0` 이면 steered.
- **출력 (가속도 명령)** — `sigma_ddot ∈ T_sigma M`. shape `(m,)`, dtype `float64`. 이 값을 lower-level tracker (joint impedance 컨트롤러 등) 가 받아 토크 명령으로 옮깁니다.
- **외부 인터페이스 (perception, FSM)** — runtime 에 task map 안의 *target* 들 (object pose, goal pose, finger contact target 등) 이 외부에서 채워집니다. 실로봇 인스턴스화에서는 FoundationPose (객체 자세 10 Hz) + Segment Anything (분할) + URDF 기반 FK 가 표준 구성. PROBE 인스턴스화에서는 *상위 정책* 의 출력이 이 자리에 들어옵니다.
- **단위 / 가정** — 가속도 단위는 `rad/s^2` (회전 자유도), `m/s^2` (병진). manifold 위 사상 `f_i` 의 정의역·치역은 사용자가 좌표계와 단위를 사전에 정해야 일관성이 깨지지 않습니다.

---

## 🧰 모듈 인터페이스

```python
def pullback_ecbf_constraint(sigma, sigma_dot, f, h_0, kappa) -> (A_row, b_scalar):
    """task manifold ECBF 를 configuration 가속도에 대한 선형 부등식으로 환원.

    반환: A_row · sigma_ddot ≥ b_scalar 형태의 half-space.
    수식: ∂(h_0∘f)/∂σ^i · σ̈^i ≥ -∂²(h_0∘f)/∂σ^i∂σ^j · σ̇^i σ̇^j
                                  - κ_2 · ḣ_0 - κ_1 · h_0
    """

def pullback_bcbf_constraint(sigma, sigma_dot, f, g, h_0, epsilon, mu_x, alpha
                              ) -> (A_row, b_scalar):
    """BCBF candidate h(x, ẋ) = h_0(x) - (ε/2)·‖ẋ - μ_x‖_N^2 의 시간 미분
    (Lemma IV.2, 식 45) 이 음수가 되지 않게 강제하는 선형 부등식."""

def assemble_safe_set(sigma, sigma_dot, ecbf_tasks, bcbf_tasks) -> Polytope:
    """모든 safety task 의 half-space inequality 를 교차해 A_safe 를 만든다."""

def autonomous_qp(sigma, sigma_dot, behavior_tasks, A_safe) -> a_bar:
    """QP 1 — 자율 안전 가속도.

    minimize over a ∈ A_safe:
        Σ_i 1/2 · ‖Z_i(a) - S_i(σ̇)‖²_{F_i* w_i}
    return: a_bar (autonomous safe acceleration).
    """

def steered_qp(sigma, sigma_dot, behavior_tasks, control_tasks, a_bar, A_safe
                ) -> sigma_ddot:
    """QP 2 — action-steered 가속도.

    minimize over a ∈ A_safe:
        Σ_i 1/2 · ‖Z_i(a) - S_i(σ̇)‖²_{F_i* w_i}
      + Σ_l 1/2 · ‖Z_l(a) - Z_l(a_bar) - sharp_g_l(u_l)‖²_{F_l* w_l}
    return: σ̈ (control 입력이 0 이면 a_bar 와 동일).
    """

def safepbds_control_step(sigma, sigma_dot,
                          behavior_tasks, ecbf_tasks, bcbf_tasks,
                          control_tasks=None) -> sigma_ddot:
    """Algorithm 1 — 매 제어 스텝의 두-QP 파이프라인.
       1) A_safe ← T_σ M
       2) for j in ECBF: A_safe ∩= pullback_ecbf_constraint(...)
       3) for j in BCBF: A_safe ∩= pullback_bcbf_constraint(...)
       4) a_bar ← autonomous_qp(...)
       5) if control_tasks: σ̈ ← steered_qp(..., a_bar)
          else:             σ̈ ← a_bar
       6) return σ̈
    """

def sharp_operator(u, g) -> v:
    """musical isomorphism ♯: T*N → TN, 좌표상 v = g^{-1} · u."""

def task_finite_state_machine(state, contact_events) -> active_task_weights:
    """그래스핑 / IHR 단계 별 task subset 활성화 + force-closure 변형 선택.
       Section VIII-B 의 FSM 역할. 본 논문에서는 task / weight gating 만 다룬다."""
```

- 모든 task 는 *사용자가 사전에 디자인* 합니다. 학습 단계가 없습니다.
- `autonomous_qp` 와 `steered_qp` 는 모두 *convex* QP 이므로 표준 솔버 (OSQP / qpSWIFT / quadprog 등) 로 풀 수 있습니다. solver 호출 인터페이스는 (원문에 명시 없음 — 가정으로 메움).
- `pullback_ecbf_constraint` 는 `f` 의 1·2 차 편미분을 요구하므로 자동미분 또는 analytic Jacobian/Hessian 이 필요합니다. URDF + symbolic FK 또는 jax/torch.autograd 가 자연스러운 후보입니다 (원문 미명시).
- FSM 은 task 가중치 게이팅만 다루며, *학습된 정책* 이 아닙니다. PROBE 인스턴스화에서는 *상위 VLA 출력* 이 FSM 자리를 대신할 수 있습니다.
- `safepbds_control_step` 는 lower-level joint impedance / position 컨트롤러와 *직렬* 로 연결됩니다. 본 컨트롤러의 출력은 가속도 명령이고, 토크 명령은 별도 tracker 가 만듭니다.

---

## ⛓️ 불변식·가정

- (가정 1) **Surjective submersive task map** — 모든 safety task map `f: M → N` 은 surjective submersion. 다지 손 (fully actuated 또는 over-actuated) 에서 자연스럽게 성립. underactuated 시스템은 framework 밖 (Assumption 1).
- (가정 2) **Safety function 의 regular value** — `h_0: N → R` 은 `0` 을 regular value 로 갖는 매끄러운 함수. 즉 `h_0 = 0` 위에서 미분이 만끄럽게 정의됨 (Definition III.3).
- (가정 3) **ECBF gain 의 stability** — pullback ECBF 의 gain `(kappa_1, kappa_2)` 는 행렬 `F - G κ^T` 의 모든 고유값이 음수 조건 (식 19) 을 만족해야 forward invariance 가 보장됨. 단순 양수 gain 으로는 충분하지 않을 수 있음.
- (가정 4) **BCBF parameter ε 의 양수** — `h(x, ẋ) = h_0(x) - (ε/2)·‖ẋ - μ_x‖_N^2` 의 `ε > 0`. ε 가 너무 크면 안전 집합이 협소해지고, 너무 작으면 BCBF 의 *속도장 추종* 효과가 약화됨.
- (가정 5) **QP feasibility** — 모든 active safety task 의 half-space 교차 `A_safe` 가 *비어 있지 않음*. 다중 안전 제약이 *동시에 활성* 일 때 인공적으로 비어버릴 가능성. recovery 는 BCBF 가 더 robust 하지만 absolute 보장 아님 (XI.3 recovery 실험).
- (가정 6) **Lower-level tracker 의 가속도 추종** — SafePBDS 출력은 *가속도 명령*. 실제 토크 명령으로의 매핑은 별도 joint impedance / inverse dynamics 컨트롤러에 위임 (Kinematic policy 한계).
- (가정 7) **Action input 의 *zero recovers autonomous*** — control task `u_l = 0` 이면 식 (48) 의 둘째 항이 사라져 `σ̈ = a_bar` 가 됨. 이 invariant 는 policy 결합 시 *backout safety* 의 근거.
- (가정 8) **Action input 의 *safety preservation*** — 임의의 `u_l` 에 대해서도 `A_safe` 제약은 같은 inequality 로 보존됨. 이 invariant 가 깨지면 framework 의 주장 전체가 무효 (식 48 의 `a ∈ A_safe` 조건 명시).
- (가정 9) **연속 trajectory** — Remark 6 — 안전 집합의 preimage `f^{-1}(C_0)` 가 비연결일 수 있지만 trajectory 가 *연속* 이라 각 연결 성분의 forward invariance 가 개별적으로 작동.

---

## 📊 하이퍼파라미터·손실

본 컨트롤러는 *학습 손실이 없습니다*. 매 스텝의 QP objective 와 inequality 가 손실 자리에 들어갑니다.

- **QP 1 objective (식 10):**

  $$\ddot{\sigma}(t)=\underset{a\in\mathcal{A}_{\mathrm{safe}}}{\arg\min}\ \sum_{i=1}^{K}\frac{1}{2}\lVert Z_{i}(a)-S_{i}(\dot{\sigma}(t))\rVert^{2}_{F_{i}^{*}w_{i}}$$

- **QP 2 objective (식 48):**

  $$\ddot{\sigma}(t)=\underset{a\in\mathcal{D}_{\dot{\sigma}(t)}\cap\mathcal{A}_{\mathrm{safe}}}{\arg\min}\ \sum^{K}_{i=1}\frac{1}{2}\lVert Z_{i}(a)-S_{i}(\dot{\sigma}(t))\rVert^{2}_{F_{i}^{*}w_{i}}+\sum^{L}_{l=1}\frac{1}{2}\lVert Z_{l}(a)-Z_{l}(\bar{a})-u_{l}^{\sharp}\rVert^{2}_{F_{l}^{*}w_{l}}$$

- **Pullback ECBF inequality (Theorem IV.1):**

  $$\frac{\partial(h_{0}\circ f)}{\partial\sigma^{i}}\ddot{\sigma}^{i}\geq-\frac{\partial^{2}(h_{0}\circ f)}{\partial\sigma^{i}\partial\sigma^{j}}\dot{\sigma}^{i}\dot{\sigma}^{j}-\kappa_{2}\dot{h}_{0}-\kappa_{1}h_{0}$$

- **BCBF candidate (식 25):**

  $$h(x,\dot{x})=h_{0}(x)-\frac{\varepsilon}{2}\left\|\dot{x}-\mu_{x}\right\|_{N}^{2}$$

- **하이퍼:**

  | 이름 | 값 | 출처 |
  |------|----|----|
  | `m` (config dim, 그래스핑) | `23` | §VIII-B |
  | `m` (config dim, IHR 모드) | `16` | §VIII-B |
  | `K` (behavior tasks, 그래스핑) | 명시 안 됨; joint damping + 핑거 끌어당김 + centroid alignment 등 | §VIII-B |
  | `L` (control tasks, 그래스핑) | `4 × 1 + 3 = 7` (per-finger 1D + 3D centroid) | §VIII-C1 |
  | `ECBF tasks` (그래스핑) | 84 | §VIII-B |
  | `ECBF tasks` (IHR) | 61 | §VIII-B |
  | Arm control rate | `20 Hz` | §VIII-A |
  | Object pose 추적 rate | `10 Hz` (FoundationPose) | §VIII-A |
  | `kappa_1, kappa_2` (ECBF gain) | 사용자 디자인; 식 (19) 의 eigenvalue 조건 | §III-C1, §IV-B |
  | `epsilon` (BCBF) | 사용자 디자인; > 0 | §III-C2, §IV-C |
  | `mu_x` (BCBF safe velocity field) | 사용자 디자인; (원문 디테일 §III-C2) | §III-C2 |
  | `alpha` (BCBF class-K∞^e fn) | 사용자 디자인 | §III-C2 |
  | `w_i` (behavior task weight pseudometric) | 사용자 디자인 | §III-B |
  | `g_i` (task manifold metric) | 사용자 디자인 | §III-B |
  | 시뮬레이션 success rate (4-finger 그래스핑) | `111/120 = 92.5%` | §VIII-C2 |
  | 시뮬레이션 success rate (3-finger 그래스핑) | `34/36 = 94.4%` | §VIII-C2 |
  | IHR yaw rotation | `> 360°` (양방향) | §VIII-D3 |
  | $`\mathbb{S}^{2}`$ run configurations | 12 (Table II) | §VI, Table II |
  | $`\mathrm{SO}(3)`$ random tracking trials | 50 (8 cm obstacle, 5 cm clearance reject) | §VII-A |
  | $`\mathrm{SO}(3)`$ rotation range | `30°–150°` | §VII-A |
  | min $`h_{\text{obs}}`$ (full system) | `+0.010` (50/50 safe) | §VII-A |
  | min $`h_{\text{obs}}`$ (ECBF ablation) | `-0.080` (11/50 violation) | §VII-A |
  | IHR DFS branching factor | `≤ 36` (3 movable fingers × 12 grid) | §VIII-D1 |
  | IHR object tilt 수용 임계 | `< 10°` | §VIII-D1 |
  | IHR perturbation 하중 (정적) | `≤ 98 g` | §VIII-D2 |
  | IHR perturbation 하중 (스윙) | `70 g loose` | §VIII-D2 |
  | QP solver | (원문에 명시 없음 — 가정으로 메움) | — |
  | Optimizer for ML 학습 | *없음 — 학습 단계 없음* | — |

---

## 🎯 평가 메트릭

- **지표** — `Obstacle safety` (min `h_obs` over trajectory) · **임계값** — `≥ 0` (safe) · **비교 baseline** — ECBF-removed ablation (joint limit ECBF 만 유지).
- **지표** — `4-finger grasping success rate` · **임계값** — 객체 lift 성공 (success), 손가락 1 개 미접촉 lift (partial 0.5), 그 외 (failure 0) · **비교 baseline** — 명시적 baseline 없음 (본 논문이 첫 결과 보고).
- **지표** — `3-finger grasping success rate` · **임계값** — 4-finger 기준과 동일하나 *지정 손가락 제외* · **비교 baseline** — 4-finger 동일 framework, ECBF 변형 + 1D action 만 교체.
- **지표** — `Per-object 6/6 success rate` · **임계값** — 객체별 6 회 trial 전부 success · **비교 baseline** — 정량 평가의 *분포* 측면 측정 (15/20 객체 perfect).
- **지표** — `Palm-down IHR yaw rotation` · **임계값** — `> 360°` 양방향 · **비교 baseline** — RL 기반 palm-up IHR (HORA, AnyRotate 등) 와 *task 종속성* 만 비교.
- **지표** — `IHR robustness across conditions` · **임계값** — 동일 plan 으로 (i) static no-load, (ii) static +98 g, (iii) swinging +70 g 세 조건 모두 360° · **비교 baseline** — 본 논문 자체 ablation.
- **지표** — `Chart invariance` (정성) · **임계값** — 두 chart 의 trajectory 가 great circle 위에서 겹침 · **비교 baseline** — flat metric (chart 의존성 노출).
- **지표** — `Safety recovery` (정성) · **임계값** — unsafe 시작 상태에서 안전 집합으로 복귀 · **비교 baseline** — ECBF (수렴 빠름) vs BCBF (속도장 추종 동안 더 매끄러운 복귀).

---

## ✨ 변경 의도 (intent)

SafePBDS 는 원조 PBDS 의 *두 한계* (soft safety, no high-level steering) 를 동시에 푸는 *기하학적으로 일관된* 확장입니다. 기여는 두 가지입니다. (1) task manifold 안전 조건을 configuration 가속도의 *선형* 부등식으로 환원하는 pullback CBF 구성, (2) 안전 집합을 깨지 않으면서 상위 정책의 force-like 입력을 residual 로 흡수하는 task manifold action interface. 이 둘이 *동일한 두-QP 파이프라인* 안에 자연스럽게 맞물립니다. 학습 단계 없이 *수작업 task 디자인 비용* 만 지불하면, 23-DOF 다지 손에서 force closure 그래스핑과 *model-based palm-down IHR 360°* 까지 닿는다는 사실이 evidence 로 드러납니다. RL 기반 stabilization layer 가 다지 조작의 *유일한* 해법인지에 대해 *대안* 을 제시하며, 동시에 RL · VLA 같은 상위 정책과 결합할 때의 *certifiable contract* (입력 0 = autonomous, 임의 입력 = safety 보존) 를 명시적으로 보장합니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 후보 base: lerobot 의 6 정책군 (`pi0` / `pi05` / `pi0_fast` / `smolvla` / `act` / `diffusion`) 중 어디에도 1:1 매핑되지 않습니다. SafePBDS 는 (a) ML 학습이 *전혀 없는* model-based online QP 컨트롤러, (b) 입력이 텐서가 아니라 (sigma, sigma_dot) + task 디자인 명세, (c) 출력이 가속도 명령 (토크 아님) 이라 lerobot 의 policy interface (`select_action(observation) → action`) 과 *데이터 흐름 자체가* 다릅니다. 부분 매핑 후보는 lerobot 의 `rtc` 또는 `transforms` / `processor` 레이어 *밖* 에 SafePBDS 를 *외부 controller* 로 두고, lerobot policy 출력을 task manifold action interface 의 `u_l` 입력으로 흘리는 *통합 어댑터* 입니다. 다만 lerobot 코드 변경량을 보면 `/foundry` 단계의 합당한 출력은 `🚧 매핑 불가` 또는 *adapter-only patch* 입니다.

---

## 🚧 미해결 / 잠정

- QP solver 선택 (OSQP / qpSWIFT / quadprog 등) 과 warm-start 전략은 본문 명시 없음.
- `f_i` 의 Jacobian / Hessian 산출 방법 (analytic vs autograd) 미명시. Allegro + Franka 의 forward kinematics 표현은 URDF 기반 가정.
- 84 개 ECBF task / 61 개 ECBF task 의 *전체 enumeration* 은 Appendix XIII.2 에 위임 (본 분석에는 옮기지 않음).
- CBF gain `(kappa_1, kappa_2)` 의 task 별 구체 값은 본문에 일괄 표로 정리되지 않고 Appendix 에 분산. v1 구체 수치는 (원문에 명시 없음 — 가정으로 메움).
- BCBF 의 `mu_x` 설계 절차 (safe velocity field 의 구체 구성) 는 [29, 46] 등 참고문헌에 위임된 부분이 있음. ECBF 보다 사용자 디자인 부담이 더 큼.
- Wrist pose sampler / candidate filter 의 알고리즘 (clearance, reachability, aperture fit 기준) 은 §VIII-C1 의 정성 기술 + Appendix XIV 로 위임.
- IHR DFS 트리 서치의 priority queue · balance constraint 의 구체 수치는 §VIII-D1 의 정성 기술 + Appendix XV 로 위임.
- 4-phase 프리미티브 (LIFTING / TRAVERSING / DROPPING / ADJUSTING) 의 task weight 스케줄과 transition 조건은 §VIII-D1 + Appendix XV.2 로 위임.
- `force closure ECBF` 의 $`l^*`$ metric 계산은 [22] 에 위임.
- 코드·체크포인트·재현 가능한 task 디자인 명세 (config) 의 공개 여부는 본문 명시 없음. 프로젝트 페이지 [tml.stanford.edu/safe-pbds](https://tml.stanford.edu/safe-pbds) 는 demo video 안내만 확인됨.
- Action interface 의 *상위 정책 연동 예시* 는 본 논문 범위 밖 (future work 에 명시). PROBE 가 HandExpert / BodyExpert 의 출력을 `u_l` 로 매핑하는 구체 규칙은 별도 design 필요.
