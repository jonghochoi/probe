# Design — Do as I Do: Dexterous Manipulation Data from Everyday Human Videos

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Do as I Do: Dexterous Manipulation Data from Everyday Human Videos |
| 링크 | [arXiv:2606.19333](https://arxiv.org/abs/2606.19333) |
| 분석 문서 | [`analysis/2606.19333/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-22 |

---

## 🧮 데이터 계약

본 알고리즘은 정책을 학습하지 않는 **데이터 생성 파이프라인**입니다. 입력은 영상 한
편, 출력은 로봇 실행 가능한 손-팔 궤적입니다.

- **입력 (영상)** — `video`: shape `(T, H, W, 3)`, dtype `uint8`, 단안 RGB 프레임열
  (ego/exo, in-the-wild·생성형 비디오 포함). 정규화는 각 비전 파운데이션 모델의 기본 전처리.
- **중간 (복원, §3.1)**
  - 손 자세 (HaWoR): MANO-계열 손 파라미터 시퀀스, near metric-space, shape `(T, …)`.
  - 물체 형상: anchor 프레임 고정 메시 $`\bar{x}^{s}`$ (단일, 시간 불변).
  - 물체 자세: $`x^{p}_{k}\in \mathrm{SE}(3)`$ 프레임별 6-DoF 시퀀스, shape `(T, 6)` (회전+병진).
  - 카메라: depth + intrinsics (MoGe), 중력 정렬 변환(GeoCalib).
- **중간 (정렬)** — 손-물체 스케일 정렬 후 단일 near metric-space 의 4D 손-물체 궤적.
- **출력 (retargeting, §3.2)** — `robot_traj`: 22-DoF 로봇 손 + 팔 제어 시퀀스, 시뮬레이션
  내 dynamically-feasible. 의미 단위 시간축은 `horizon` (3.0 s) · plan 주기 `ctrl_dt` (0.5 s).
  최종은 실 배포용 손 관절 명령 + 팔 IK(50 Hz).

---

## 🧰 모듈 인터페이스

```python
def reconstruct(video) -> HandObjectTrajectory:
    """단안 RGB 영상 → 4D 손-물체 궤적 (§3.1).
    내부: SAM 3 분할 → MoGe depth/intrinsics → SAM 3D 메시 →
    HaWoR 손 추적 + guided-diffusion 물체 추적 → 손-물체 정렬 → GeoCalib 중력정렬."""

def track_object_guided(frames, anchor_shape, prev_pose) -> SE3:
    """SAM 3D flow-matching 추론을 형상=anchor·자세=이전프레임 쪽으로 블렌딩(Eq.1).
    프레임당 N 후보 샘플 → weighted SE(3) clustering + mask-IoU consensus 선택."""

def align_hand_object(hand_recon, obj_recon) -> AlignedTrajectory:
    """손 스케일을 GT 로 보고 centroid z-비율 k 로 물체 translation 스케일링(최소제곱)."""

def retarget(reference_traj) -> RobotTrajectory:
    """MPPI-style annealed sampling-based optimization (SPIDER 기반) + 3종 혁신:
    warmup steps · random force perturbation · transition reward (§3.2)."""

def kinematic_reference(hand_traj) -> RobotTrajectory:
    """mink 로 fingertip 위치 매칭 — dynamics-aware 단계의 초기 reference 생성."""
```

- `reconstruct` — 영상 → 4D 손-물체 궤적. 외부 호출: SAM 3 / SAM 3D / MoGe / HaWoR / GeoCalib.
- `track_object_guided` — 단일 이미지 생성기를 비디오 트래커로 재용도화. diffusion backbone
  재호출 없이 후보 선택(consensus filtering).
- `retarget` — reference → 로봇 궤적. 외부: MuJoCo Warp 시뮬, CoACD(convex decomp), mink(초기 reference).
- 모든 모듈은 파지 prior·물체 카테고리·장면 복원 가정을 두지 않음 (general-purpose 계약).

---

## ⛓️ 불변식·가정

- (가정 1) **강체 물체** — 물체 형상 $`\bar{x}^{s}`$ 는 시간 불변(anchor 프레임에서 고정). 비강체는 무효.
- (가정 2) **형상-자세 latent 공유** — SAM 3D 결합분포에서 형상·자세가 같은 latent space 를 공유 →
  형상 고정 + 자세만 추론이 성립.
- (가정 3) **준정확 metric depth** — 단안 depth 가 near metric. 손-물체 정렬의 centroid z-비율
  스케일링 $`k=z^{\mathrm{H}}_{\mathrm{hand}}/z^{\mathrm{M}}_{\mathrm{hand}}`$ 가 이에 의존.
- (가정 4) **손 스케일 = GT** — 손 복원 스케일을 ground-truth 로 두고 물체를 거기에 정렬.
- (가정 5) **물리 robustness** — 올바른 상호작용은 작은 외란(random force)에 강건해야 함 →
  perturbation 으로 local minimum 탈출 유도.
- (가정 6) **전이 임계 분리** — reference 손-물체 거리 threshold $`\epsilon`$ 로 "rest"/"in-hand"
  스테이지를 분리할 수 있음 (transition reward 의 전제).

---

## 📊 하이퍼파라미터·손실

**Guided diffusion 물체 추적 (Eq. 1, §3.1):**

$$x^{s}_{t}=(1-\alpha_{s})(x^{s}_{t-\Delta}+\Delta v^{s}_{\theta})+\alpha_{s}\,z^{s}_{\mathrm{ref}}(t),\quad x^{p}_{t}=(1-\alpha_{p})(x^{p}_{t-\Delta}+\Delta v^{p}_{\theta})+\alpha_{p}\,z^{p}_{\mathrm{ref}}(t)$$

- target interpolant: $`z^{s}_{\mathrm{ref}}(t)=(1-t)\,\epsilon^{s}+t\,\bar{x}^{s}`$,
  $`z^{p}_{\mathrm{ref}}(t)=(1-t)\,\epsilon^{p}+t\,x^{p}_{k-1}`$.
- 손-물체 정렬: $`\mathbf{obj}_{\mathrm{target}}=\mathbf{c}^{\mathrm{H}}_{\mathrm{hand}}+k\,(\mathbf{c}^{\mathrm{M}}_{\mathrm{obj}}-\mathbf{c}^{\mathrm{M}}_{\mathrm{hand}})`$.

**Retargeting 보상:** 물체(위치·방향) + 손(위치·방향·관절) tracking + 침투 페널티 + transition 페널티.

| 이름 | 값 | 출처 |
|------|----|----|
| `num_samples` | `1024` | §App.B, Table 4 |
| `max_num_iterations` | `32` | Table 4 |
| `horizon` | `3.0` (s) | Table 4 |
| `ctrl_dt` | `0.5` (s, 2 Hz plan) | Table 4 |
| `sim_dt` | `0.005` (s, 200 Hz) | Table 4 |
| `knot_dt` | `0.2` | Table 4 |
| `pos_noise_scale` / `rot_noise_scale` / `joint_noise_scale` | `0.01` / `0.01` / `0.1` | Table 4 |
| `first_ctrl_noise_scale` / `last_ctrl_noise_scale` / `final_noise_scale` | `1.0` / `4.0` / `0.01` | Table 4 |
| `pos_rew_scale` / `rot_rew_scale` | `1.0` / `0.3` | Table 4 |
| `base_pos_rew_scale` / `base_rot_rew_scale` / `joint_rew_scale` | `0.1` / `0.03` / `0.01` | Table 4 |
| `terminal_rew_scale` | `10.0` | Table 4 |
| `penetration_penalty_scale` | `3000.0` | Table 4 |
| `transition_penalty_scale` | `0.5` | Table 4 |
| `num_perturb_samples` | `4` | Table 4 |
| `perturb_force_scale` / `perturb_torque_scale` | `0.5` / `0.5` | Table 4 |
| `perturb_prob` / `perturb_continue_prob` | `0.05` / `0.95` | Table 4 |
| 형상 guidance $`\alpha_s`$ | `[0.9, 1]` 고정 | §3.1 |
| 자세 guidance $`\alpha_p`$ | adaptive (2D point-track 회전속도 유도) | §3.1 |
| warmup steps `H` | horizon 과 동일 길이(= reference 앞에 H 스텝 prepend); 구체 수치 (원문에 명시 없음 — 가정으로 메움) | §3.2 |
| 자세 후보 수 `N` | (원문에 명시 없음 — 가정으로 메움) | §3.1 |
| transition threshold $`\epsilon`$ | (원문에 명시 없음 — 가정으로 메움) | §3.2 |

---

## 🎯 평가 메트릭

- **복원** — `F-5` / `F-10` (↑) · `Chamfer distance` (↓) on DexYCB·HOI4D · 비교 baseline:
  FoundationPose / Any6D / MCC-HO / G-HOP 등 (Table 2). in-the-wild 는 human preference (67% win).
- **Retargeting** — `Success rate` (↑) · `mean position error E_pos` (↓) · `mean orientation error` (↓).
  성공 판정: mean position error 가 임계 미만 (정확 임계값은 원문 §4.1 도표 절단으로 미확보).
  비교 baseline: SPIDER(= Annealed Sampling), 컴포넌트 점진 추가 ablation (Table 3).

---

## ✨ 변경 의도 (intent)

기존 dynamics-aware retargeting(SPIDER 등)은 MoCap 급 clean reference(GT 손-물체 자세)를
가정합니다. Do as I Do 는 단안 RGB 복원에서 나오는 **noisy·시간 불연속·심한 손-물체
오정렬** reference 를 입력으로 받는 더 어려운 설정을 정조준하고, 이를 견디는 세 general-purpose
장치 — warmup(불능 초기상태·미탐색 horizon 시작부 해소), random force perturbation(불안정
local minimum 탈출), transition reward(임계 집기/놓기 보강) — 를 추가합니다. 물체 추적도
이미지→3D 생성기(SAM 3D)를 guided flow-matching 으로 비디오 트래커화해 occlusion·저해상도에
강건합니다. 결과적으로 파지 prior·물체 카테고리·장면 가정 없이 인터넷 영상→실 로봇 rollout 을 닫습니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 본 논문은 정책(policy) 기여가 아니라 **데이터 생성 파이프라인**(비전
  파운데이션 모델 복원 + MuJoCo Warp sampling-based retargeting)입니다. lerobot 의 7개 policy
  family(`pi0`/`pi05`/`pi0_fast`/`smolvla`/`act`/`diffusion`/`vla_jepa`) 중 매핑되는 base 가
  없습니다 — 출력물(retargeted 궤적)을 LeRobotDataset 형식으로 적재하는 *데이터 수입(import)*
  경로가 유일한 접점이며, 알고리즘 자체는 foundry 외부(MuJoCo Warp + 비전 FM 스택)에 있습니다.
  `/implement-design` 의 per-foundry `UNMAPPABLE` 판정이 예상됩니다.

---

## 🚧 미해결 / 잠정

- warmup steps `H` 의 구체 수치 — "horizon 과 동일 길이를 prepend" 로만 기술, 정확 스텝 수 미명시.
- 자세 후보 수 `N` 과 weighted SE(3) clustering 의 거리 가중치·임계 — 본문 미명시.
- transition threshold $`\epsilon`$ 구체값 — "reference 손-물체 거리 threshold" 로만 기술.
- 성공 판정 position error 임계값 — 원문 §4.1 의 정의 문장이 도표에 의해 절단되어 정확값 미확보.
- adaptive $`\alpha_p`$ 유도식 — 2D point-track 회전속도에서 유도한다고만 기술, 정확 매핑식 미명시.
