# Design — RealDexUMI: A Wearable Universal Manipulation Interface for Dexterous Robot Learning

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | RealDexUMI: A Wearable Universal Manipulation Interface for Dexterous Robot Learning |
| 링크 | [arXiv:2606.06033](https://arxiv.org/abs/2606.06033) |
| 분석 문서 | [`analysis/2606.06033/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-10 |

---

## 🧮 데이터 계약

시간 축은 의미 단위로 표기합니다. action chunk 길이 $`C`$ = `chunk_size`(ACT 기본 20), 미래 step index $`k\in\{1,\dots,C\}`$.

- **입력 (관측 $`o_t`$, Eq. 1)**
  - `image`: in-hand RGB $`I_t`$ — shape `(B, 3, 256, 256)`, float, 리사이즈됨. (원문은 $`\mathbb{R}^{256\times256\times3}`$ — HWC; 정규화 통계는 원문 미명시.)
  - `tactile`: fingertip 신호 $`S_t^{\mathrm{tactile}}`$ — shape `(B, 5, 10, 4)`, 5개 손끝 × 10×4 piezoresistive 배열. dtype·정규화 원문 미명시.
  - `hand_state`: 구동 손 관절 state $`q_t^{\mathrm{hand}}`$ — shape `(B, 6)`, float (6 actuated DoF).
  - (관측에 **절대 pose 미포함** — tracker pose $`T_t`$ 는 라벨 생성에만 사용.)
- **출력 (액션 chunk $`\hat{A}_t`$, Eq. 3–4)**
  - 단일 step 라벨 $`a_{t,k}=[\Delta p_{t,k},\Delta r_{t,k},u^{\mathrm{hand}}_{t+k}]`$ — shape `(B, C, d_a)`.
    - $`\Delta p_{t,k}`$: hand-frame 상대 translation, `(B, C, 3)`.
    - $`\Delta r_{t,k}`$: 상대 rotation vector(axis-angle), `(B, C, 3)`.
    - $`u^{\mathrm{hand}}_{t+k}`$: 실행 가능한 손 command, `(B, C, 6)` (glove 캡처, hand command 공간과 동일 차원).
  - 따라서 $`d_a = 12`$ (3+3+6), single-hand 기준. bimanual 은 per-hand concat → 관측·액션 모두 2배.

---

## 🧰 모듈 인터페이스

```python
def relative_action_label(T: "SE3[B,T_total]", t: int, C: int) -> "Tensor[B,C,6]":
    """현재 hand-frame pose 기준 미래 상대 변위 라벨 생성.
    ΔT_{t,k} = T_t^{-1} T_{t+k}; (Δp, Δr=rotvec)로 분해해 반환 (Eq. 2)."""

def policy_forward(obs: "Obs(image,tactile,hand_state)") -> "Tensor[B,C,12]":
    """π_θ(o_t): 관측 → 미래 액션 chunk Â_t (Eq. 4).
    백본 = ACT (main) / Diffusion Policy (보조). 절대 pose 미사용."""

def deploy_target_pose(T_hat_t: "SE3[B]", dT_hat: "SE3[B,C]") -> "SE3[B,C]":
    """배포 시 로봇 목표 pose 합성: T̂_target = T̂_t · ΔT̂ (§4.2).
    이후 robot-side IK + 저수준 컨트롤러가 실현; 손 command 는 직접 실행."""
```

- **`relative_action_label`** — tracker pose 스트림만 입력, 관측과 독립. 출력은 hand-frame 상대 변위(절대 좌표 소거). 정책 학습 라벨의 EE 부분 생성.
- **`policy_forward`** — 관측 3종(image/tactile/hand_state)만 입력, 절대 pose 차단. 출력 chunk 의 EE 부분은 상대 변위, 손 부분은 실행 가능 command. ACT loss(action-prediction L1) + KL(latent) 와 결합.
- **`deploy_target_pose`** — 정책과 분리된 배포 경계. embodiment 별로 IK·저수준 컨트롤러만 교체, 정책·end-effector 인터페이스는 고정.

---

## ⛓️ 불변식·가정

- **(가정 1) 공유 모듈 zero-gap** — 수집 시 사람이 착용한 end-effector 모듈과 배포 시 로봇에 장착한 모듈이 동일해, in-hand 관측·접촉면·촉각·손 command 분포가 수집/배포 간 일치. 깨지면(다른 손/카메라) deployable dexterity 보장이 무효.
- **(가정 2) isomorphic 1:1 매핑** — glove 의 6 sensed DoF 가 hand 의 6 actuated DoF 와 선형 1:1 대응. retarget-free 의 전제이며, DoF 불일치 시 성립하지 않음.
- **(가정 3) 상대 액션 좌표 불변성** — $`\Delta T_{t,k}=T_t^{-1}T_{t+k}`$ 가 수집 시점 전역 자세·로봇 base 와 독립. 이 불변성이 cross-embodiment·initial-pose 일반화의 수학적 근거.
- **(가정 4) IK 실현 가능성** — 배포 로봇이 $`\hat{T}_t\Delta\hat{T}_{t,k}`$ 를 자기 IK 로 도달 가능(workspace·특이점 내). 깨지면 동일 checkpoint 전이가 실패.
- **(가정 5) action–state 대응** — 접촉으로 제약된 측정 state 와 실행 의도 command 의 불일치가 유의미한 접촉 신호를 담음. state-as-action 으로 대체하면 접촉 회복 supervision 소실.

---

## 📊 하이퍼파라미터·손실

- 손실 식: action-prediction **L1 loss** (EE 상대 변위 + 손 command) + ACT 의 **KL** latent 항. (원문은 명시 식 없이 ACT 기본 채택; KL weight = 10.)

- 하이퍼 (ACT, main):
  | 이름 | 값 | 출처 |
  |------|----|----|
  | `action_horizon` (C) | 20 | §D, Table 6 |
  | `executed_action_steps` | 20 | §D, Table 6 |
  | `image_obs_horizon` | 1 | §D, Table 6 |
  | `proprio_obs_horizon` | 1 | §D, Table 6 |
  | `obs_resolution` | $`256\times256`$ | §D, Table 6 |
  | `vision_encoder` | ResNet-18 (ImageNet pretrained) | §D, Table 6 |
  | `transformer_dim` | 512 | §D, Table 6 |
  | `transformer_layers` | 4 enc / 1 dec | §D, Table 6 |
  | `attention_heads` | 8 | §D, Table 6 |
  | `act_latent_dim` | 32 | §D, Table 6 |
  | `kl_weight` | 10 | §D, Table 6 |
  | `optimizer` | AdamW | §D, Table 6 |
  | `learning_rate` | $`1\times10^{-5}`$ | §D, Table 6 |
  | `betas` | $`(0.9, 0.999)`$ | §D, Table 6 |
  | `weight_decay` | $`1\times10^{-4}`$ | §D, Table 6 |
  | `batch_size` | 128 | §D, Table 6 |
  | `training_steps` | 200k | §D, Table 6 |
  | `grad_clip_norm` | 10 | §D, Table 6 |
  | `demos_per_task` | 200 | §5 |

- 보조 백엔드 (Diffusion Policy): action horizon 32, U-Net channels $`(512,1024,2048)`$, Adam lr $`1\times10^{-4}`$, betas $`(0.95,0.999)`$, weight decay $`1\times10^{-6}`$, cosine LR(500 warmup), 100 diffusion/inference steps, DDPM, squared-cosine beta, $`\epsilon`$-prediction, 100k steps. (§D, Table 6)

---

## 🎯 평가 메트릭

- **지표** — full-task success rate (전체 과제 완수 = 이진 성공), 8개 실로봇 과제 평균 · **임계값** — RealDexUMI 88.75% (ACT) / 70.00% (w/o tactile) / 51.25% (state-as-action) / 63.75% (Diffusion Policy) · **비교 baseline** — w/o tactile, state-as-action ablation + collection-time 비교(AVP teleop, Manus retargeting, 사람 맨손 reference).
- 부수 지표 — initial-pose 강건성(20/20), cross-embodiment success(FR3/RM65/Adam-U, Table 3), cumulative subgoal completion(부록 Table 8), collection-time success rate + 완료시간(Fig 7, 5분 초과 = 실패).
- 평가 프로토콜 — 과제·세팅당 20 real-robot trial, 주 평가 robot = Franka FR3 + 동일 end-effector 모듈.

---

## ✨ 변경 의도 (intent)

기존 dexterous 수집(mocap glove retarget / exoskeleton-state / arm-attached)이 "포착된 dexterity" 를 최적화한다면, RealDexUMI 는 **배포 가능한 dexterity** 를 최적화합니다. 핵심 변경은 두 가지: (1) 수집 인터페이스와 배포 로봇 손을 **동일 모듈**로 공유해 retarget·visual-inpainting 후처리를 제거하고 관측·접촉·command 를 정의상 정렬(zero-gap), (2) 손 액션 라벨을 측정 **state** 가 아니라 isomorphic glove 가 캡처한 실행 가능한 **command** 로 두고, EE 모션은 hand-frame **상대 변위**로 표현. 전자는 데이터 충실도를, 후자는 cross-embodiment·initial-pose 일반화를 만들어냅니다. 모델(ACT/DP)은 기성품 — 기여는 데이터·액션 표현 정렬에 있습니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 백본이 **ACT** 이고 보조로 **Diffusion Policy** 이므로 `act` / `diffusion` family 와 직접 정렬됨. 다만 본 논문 기여의 본질(공유 하드웨어 모듈 · isomorphic glove · 6-DoF tracker 상대 라벨)은 코드가 아닌 데이터 수집·액션 표현 계층이라, lerobot 매핑 가능 부분은 (a) `tactile (5,10,4)` 관측 + 6-D hand_state 의 입력 계약, (b) hand-frame 상대 EE 변위 + hand command 의 액션 표현(`(B,C,12)`)으로 한정. 하드웨어·glove 매핑은 foundry 범위 밖.

---

## 🚧 미해결 / 잠정

- 이미지/촉각 정규화 통계 출처가 원문에 없어 "데이터셋 전체 평균/표준편차" 가정으로 메움.
- 정확한 손실 함수 형태(EE 변위와 hand command 의 가중·항 결합)는 ACT 기본을 따른다고만 명시 — 식 verbatim 부재, `(원문에 명시 없음 — 가정으로 메움)`.
- rotation vector $`\Delta r`$ 의 정확한 표현(axis-angle vs Lie algebra)이 본문에 명시되지 않아 axis-angle 로 가정.
- bimanual 시 per-hand 관측 concat 순서·동기화 세부는 부록 수준이며 Layer 1 스펙으로 굳히지 않음.
- 코드 공개 여부 미명시 — `/implement-design` 시 참조 구현 없음 전제.
