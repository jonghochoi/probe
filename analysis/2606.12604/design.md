# Design — EgoEngine: From Egocentric Human Videos to High-Fidelity Dexterous Robot Demonstrations

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | EgoEngine: From Egocentric Human Videos to High-Fidelity Dexterous Robot Demonstrations |
| 링크 | [arXiv:2606.12604](https://arxiv.org/abs/2606.12604) |
| 분석 문서 | [`analysis/2606.12604/analysis.md`](./analysis.md) |
| 본문 확보 수준 | PDF 텍스트(PyMuPDF) |
| Design 생성일 | 2026-06-15 |

> EgoEngine 은 "egocentric 인간 영상 → 실행 가능 로봇 시연" 데이터 생성 엔진입니다.
> Layer 1 알고리즘 기여는 (A) action branch 의 object-centric trajectory
> optimization + MCTS-style adaptive mode switching(Replay/MPC/RL), (B) visual
> branch 의 occlusion-aware differential-rendering blending, (C) 생성 데이터의
> HPT flow-matching policy distillation 세 부분으로 분해됩니다.

---

## 🧮 데이터 계약

엔진은 단일 학습 모델이 아니라 *입력 영상 → 출력 (관측, 행동) 쌍* 변환기이므로, 데이터 계약은 파이프라인 I/O 로 기술합니다. 시간 축은 chunk 단위(`H` control step) + 의미 단위(`T` = 클립 길이)로 표기.

- **입력 (egocentric 영상)** — RGB frame `(T, H_img, W_img, 3)` + per-frame 3D hand pose `(T, 21, 3)`(21 keypoint) + 손목 방향 `(T, 3, 3)` ∈ SO(3). source: Aria Gen2(원문). normalization: ImageNet(policy 입력 시).
- **입력 (digital twin, 파생)** — depth map `(T, H_img, W_img)`(FoundationStereo), arm-hand mask + object mask `(T, H_img, W_img)`(SAM2), object 6D 궤적 `{T_o^t} (T, 4, 4)` ∈ SE(3)(FoundationPose), object mesh(외부 제공).
- **출력 (action branch)** — 실행 가능 로봇 궤적 `ã = {a_t} (T, d_a)`. action 공간 = floating Cartesian wrist pose + XHand finger joint(원문: floating base abstraction + finger joints). dtype float32.
- **출력 (visual branch)** — 로봇 관측 영상 `õ^(r) = {õ_t^(r)} (T, H_img, W_img, 3)` + proprioception.
- **출력 (distillation 데이터셋)** — `D̃_robot = {(õ, ã)}` 동기화 쌍. policy 학습 입력.

---

## 🧰 모듈 인터페이스

```python
def build_digital_twin(rgb, hand_pose, wrist_rot, object_mesh) -> DigitalTwin:
    """RGB+hand pose 에서 depth(FoundationStereo)·mask(SAM2)·object 6D 궤적
    (FoundationPose)을 복원해 두 branch 의 공통 grounding 공간을 반환."""

def human_centric_retarget(hand_pose, wrist_rot, robot_model) -> ReferenceTraj:
    """fingertip+wrist pose 를 IK(Eq.1, MINK)로 풀어 reference 로봇 궤적
    τ_ref = {q*_t} 생성. joint limit·self-collision 제약 하 L2 정렬."""

def optimize_chunk(chunk, ref_traj, obj_traj, mode) -> (RobotTraj, feasible):
    """단일 chunk 를 mode∈{Replay, MPC, RL} 로 정제. object pose tracking
    error(Eq.2) 기반 reward + early termination. RL 은 residual πϕ(PPO)."""

def adaptive_mode_switch(ref_traj, obj_traj, H=20) -> RobotTraj:
    """chunk 별 Replay→MPC→RL escalation. two-chunk window 로 현재+다음
    chunk 동시 검사 후 현재 chunk 만 실행(MCTS-style 휴리스틱 탐욕 탐색)."""

def visual_blend(robot_traj, frames, masks) -> RobotObsVideo:
    """human removal(Inpaint-Anything v2) + occlusion-aware two-pass
    differential rendering(Eq.3) → blending(Eq.4)로 로봇 관측 영상 합성."""

def distill_policy(dataset) -> Policy:
    """D̃_robot 으로 HPT(ResNet18 stem + token fusion encoder) + flow-matching
    decoder 정책을 ℓ2 regression(Eq.5) 학습. closed-loop controller."""
```

- 모듈 간 계약: `build_digital_twin` 출력이 action·visual branch 의 단일 진입점. action branch(`retarget`→`adaptive_mode_switch`)와 visual branch(`visual_blend`)는 같은 digital twin 위에서 독립 실행되나, `visual_blend` 는 action branch 의 로봇 궤적을 렌더 입력으로 받음(순서 의존). 두 출력이 `distill_policy` 로 합류.

---

## ⛓️ 불변식·가정

- (가정 1) **object pose 추종 ⇒ task 재현** — 영상에서 추적한 object 6D 궤적 $`T^t_o`$ 를 로봇이 시뮬에서 재현하면 task 가 보존된다는 object-centric 가정. tracking error $`e_t`$ 가 작으면 task-aligned.
- (가정 2) **reference 궤적은 유효한 motion prior** — retargeting 된 $`\tau^{ref}`$ 가 (실행은 실패할지언정) RL/MPC 정제의 초기점으로 충분히 가깝다는 가정. residual $`a_t = a^{base}_t + \delta a_t`$ 가 작은 보정으로 feasibility 회복 가능해야 함.
- (가정 3) **chunk 분해 가능성** — long-horizon trajectory 가 길이 `H` chunk 로 분해 가능하고, two-chunk window 검사로 국소 최소를 충분히 회피한다는 가정.
- (가정 4) **early-termination 경계 = reward 척도 일치** — $`\sqrt{\lambda_R (e^t_R)^2 + \lambda_p (e^t_p)^2}`$ 가 dense reward 와 feasibility 임계 $`C`$ 를 동시에 정의(같은 score). $`C`$ 는 reference object motion 에서 설정(탐색 대상 아님).
- (가정 5) **opaque object two-pass 불변** — differential rendering 의 두 pass 에서 object geometry 가 opaque 로 동일하므로, 차이 mask 가 정확히 가시 로봇 픽셀만 남긴다는 렌더링 가정(Eq.3).
- (가정 6) **moderate 외형 mismatch 허용** — distill policy(특히 object-centric visual encoder)가 blending 합성 관측과 실로봇 관측 간 외형 차이를 견딘다는 가정(ablation Table 4 근거).

---

## 📊 하이퍼파라미터·손실

- IK retargeting(Eq.1): $`L = L_{tip} + \lambda_w L_{wrist}`$
- object tracking reward(Eq.2/C.3): $`r^t_{obj} = C - \sqrt{\lambda_R (e^t_R)^2 + \lambda_p (e^t_p)^2}`$
- human-mimic(C.5): $`r^t_{human} = -(\beta_x \|x_t - x^{retar}_t\|^2_2 + \beta_R d_R(R_t, R^{retar}_t)^2 + \beta_q \|q_t - q^{retar}_t\|^2_2)`$
- smoothness(C.6): $`r^t_{smooth} = -\|a_t - a_{t-1}\|^2_2`$
- contact(C.7): $`r^t_{contact} = c_{contact} \cdot \mathbb{1}(C^t_{thumb} \wedge C^t_{other})`$
- lifting(C.8): $`r^t_{lift} = \lambda_z (z^t_o - z^0_o)`$
- residual: $`a_t = a^{base}_t + \delta a_t`$, $`\delta a_t \sim \pi_\phi(\cdot | s_t)`$
- flow-matching(D.1): $`x_\tau = \tau a_0 + (1-\tau) a_1`$, target velocity $`\frac{dx_\tau}{d\tau} = a_0 - a_1`$
- distillation(Eq.5): $`\min_\theta \mathbb{E}[\|\pi_\theta(\tilde{o}) - \tilde{a}\|^2_2]`$

| 이름 | 값 | 출처 |
|------|----|----|
| chunk 길이 `H` | 20 control step | §C.1 |
| optimization window | 2 chunk(현재+다음) | §C.1 |
| RL 알고리즘 | PPO (RSL-RL 계열) | §3.2.2, [51] |
| flow-matching 추론 step | 10 (Euler) | §D.2 |
| visual stem | ResNet-18(GAP 직전 truncate) + ImageNet norm | §D.1 |
| Aria object position threshold | 0.08 m | §C.2 |
| Aria object rotation threshold | 2.5 rad | §C.2 |
| Aria contact reward scale | 2.0 | §C.2 |
| Aria base-pos / base-rot reward | 0.2 / 1.0 | §C.2 |
| Aria joint reward scale | 0.0 | §C.2 |
| Aria smoothness reward scale | 0.8 | §C.2 |
| Aria 랜덤 rollout 수 | 8 | §C.2 |
| Aria noise scale (pos/rot/joint) | 0.045 / 1.0 / 0.8 | §C.2 |
| Aria object mass scale | [0.8, 1.2] | §C.2 |
| Aria workspace xy offset | [−0.015, 0.015] | §C.2 |
| TACO rotation threshold(task별) | 0.9 / 1.2 / 1.5 rad | §C.2 |
| $`\lambda_p`$, $`\lambda_R`$, $`\beta_x`$, $`\beta_R`$, $`\beta_q`$, $`c_{contact}`$, $`\lambda_z`$, $`\lambda_w`$, $`C`$ | `(원문에 수치 명시 없음 — 일부 task별 threshold 만 제시)` | §3.2, §C.2 |

---

## 🎯 평가 메트릭

- **action fidelity** — `SR`(전 reference horizon 무위반 완주 비율, C.10) · `Step`(normalized rollout 완주 비율, C.11) · `Reward`(perfect 대비 object-tracking reward ratio, C.12) · `Cost`(성공 trajectory timestep 당 평균 simulation step, C.13, device-agnostic). 비교 baseline: Mink(Replay)/Spider(MPC)/H2S2R(RL).
- **visual fidelity** — Fréchet Distance(ResNet18/VGG16/DINOv2 last-layer feature). baseline: Human Video / EgoMimic / VACE / Phantom.
- **downstream policy** — 실로봇 SR(고정 rollout trial). baseline: Human Video / Phantom / Real Robot teleoperation.
- **action 품질** — SPARC(Spectral Arc Length) smoothness(E.1; 값 높을수록 부드러움). 임계값 없음(상대 비교).

---

## ✨ 변경 의도 (intent)

prior art(단순 retargeting replay, full-RL refinement, inpainting-only/blending-only video editing)는 visual gap 또는 action gap 중 하나만, 또는 전 trajectory 에 균일하게 강한 solver 를 적용해 비용이 폭증했습니다. EgoEngine 의 의도는 두 가지입니다. (1) **두 gap 을 하나의 object-centric digital twin 위에서 동시에** 메워, 관측과 행동을 정합·쌍으로 생성합니다. (2) **chunk 별 적응적 solver escalation**(Replay→MPC→RL)으로 "필요한 곳에만 비용을 쓴다" — 쉬운 구간은 Replay/MPC, contact-rich 어려운 구간만 RL — 이를 통해 full-RL 동등 품질을 절반 수준 비용으로 달성하고 long-horizon 일수록 이득이 커집니다. 핵심 주장은 executable action 생성이 downstream zero-shot 성능의 1차 결정 요인이라는 것입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — EgoEngine 자체는 *데이터 생성 엔진*이라 lerobot policy family 에 직접 대응하지 않습니다. 다만 마지막 distillation 단계(HPT + flow-matching decoder + ℓ2/flow-matching action regression)는 `pi0`/`pi05`/`smolvla`(flow-matching action expert) family 와 개념적으로 가깝습니다. action branch(IK retargeting + residual RL + MCTS-style mode switching)와 visual branch(differential rendering blending)는 lerobot 의 정책 학습 범위 밖 별도 데이터 파이프라인이라 foundry 매핑 대상에서 빠질 가능성이 높습니다 — `/implement-design` 가 portable 부분(예: distillation policy head 또는 데이터 전처리)만 매핑할지 판단.

---

## 🚧 미해결 / 잠정

- reward 계수 $`\lambda_p`$ · $`\lambda_R`$ · $`\beta_*`$ · $`c_{contact}`$ · $`\lambda_z`$ · $`\lambda_w`$ 및 임계 $`C`$ 의 절대 수치가 원문에 통합 명시되지 않음 — task별 position/rotation threshold(§C.2)만 제시. 구현 시 가정 필요.
- MPC 의 short-horizon sample 수·탐색 budget, RL residual policy 의 network/학습 step 수가 본문에 정량 미명시.
- HPT encoder 의 token 수(visual/proprio query token, context token), transformer hidden dim, action horizon `T` 길이가 본문에 정량 미명시("fixed number" 로만 기술).
- digital twin 의 object mesh 출처/획득 방식은 ground-truth mesh 전제(§3.1, A.3) — 임의 in-the-wild 영상으로의 자동화(SAM3D)는 미실증 future work.
- "feasible / sufficiently improved rollout" 판정 임계(mode escalation trigger)의 구체 값이 본문에 명시 없음 — early-termination 경계 `C` 와의 관계만 정성 기술.
