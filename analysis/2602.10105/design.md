# Design — DexImit: Learning Bimanual Dexterous Manipulation from Monocular Human Videos

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | DexImit: Learning Bimanual Dexterous Manipulation from Monocular Human Videos |
| 링크 | [arXiv:2602.10105](https://arxiv.org/abs/2602.10105) |
| 분석 문서 | [`analysis/2602.10105/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-10 |

> 본 Design 은 정책 학습 모델이 아니라 **데이터 생성 파이프라인**(영상 → 로봇
> 데이터)의 Layer 1 스펙입니다. 학습 가능한 손실은 grasp 합성 최적화 목적함수가
> 유일하며, 다운스트림 정책(DP3)은 본 파이프라인의 *소비자*이지 구성요소가
> 아닙니다.

---

## 🧮 데이터 계약

- **입력 (영상)** — `video`: RGB 프레임열 $`V=\{I_{i}\}_{i=0}^{K}`$, frame rate $`f`$ → 일정 rate $`f_{t}`$ 로 리샘플 ($`V_{t}`$). 추가 정보(depth·intrinsics·extrinsics) 없음. dtype uint8, shape `(K_t, H, W, 3)`.
- **중간 (재구성)** — 손 궤적 $`\{p_{h}^{t}\}_{t=0}^{K_{t}}`$, 객체 궤적 $`\{p_{o}^{t}\}_{t=0}^{K_{t}}`$: per-frame $`SE(3)`$ pose (좌/우 손 $`h_0,h_1`$, 객체 $`o_i,\ i=0..N_o`$). near-metric scale (단위 ≈ m). world 좌표계 정렬(원점 $`x=0.6`$).
- **중간 (스케줄)** — embodiment 별 action queue $`\{\mathcal{A}_{i}\}_{i=1}^{N}`$, $`\mathcal{A}_{i}\in\mathbb{R}^{T}`$ (시간축 길이 $`T`$, 빈 슬롯 0).
- **출력 (source data)** — 로봇 양손 trajectory: end-effector pose 열 $`\{p_{\text{ee},\mathcal{E}_\tau}^{t}\}`$ + 선택된 grasp $`g^{*}`$ (손 translation $`\mathbf{t}_h`$ · rotation $`\mathbf{R}_h`$ · joint angle $`\mathbf{q}_h`$). XHand 등 dexterous hand joint command 좌표계.
- **출력 (증강 데이터셋)** — source 1 개 → 데모 ~100 개. 관측 = 3D point cloud (object pose/scale·camera pose·sensor noise 증강 적용). dtype float32.
- **정규화 가정** — scale: source = 1.0 기준 상대. point cloud 좌표는 world frame. (구체 정규화 통계는 원문에 명시 없음 — 가정으로 메움.)

---

## 🧰 모듈 인터페이스

```python
def reconstruct_4d(video, f, f_t) -> tuple[HandTraj, ObjTraj, T_c2w]:
    """단안 영상 → near-metric 손/객체 SE(3) 궤적 + world 변환.
    VLM 객체식별 → SAM2 segmentation → depth(ST2) + 손크기 prior scale →
    SAM3D 3D생성 + Wilor 손pose → FoundationPose++ 6D pose → world 정렬."""

def estimate_scale(hand_pcd, hand_mesh) -> float:
    """align-render-align: s = PCA(occlusion_free_mesh) / PCA(hand_pcd)."""

def world_transform(table_mask, hand0_p0, hand1_p0, obj_bbox) -> SE3:
    """z=테이블 법선, x=양손 수직이등분의 z-직교 투영, y=오른손계,
    원점=객체 AABB 중심 → 작업영역(x=0.6)."""

def schedule_actions(N, T, task_list) -> dict[int, ActionQueue]:
    """Action-Centric Scheduling (Algorithm 1): priority queue 로
    Task/Subaction(pregrasp/grasp/motion/release)을 embodiment×시간축 배치."""

def synthesize_grasp(obj_mesh, com, active_contacts, target_wrenches, demo_hand_pose) -> Grasp:
    """force-closure(BODex) 최적화로 grasp 후보 G_oi 생성 →
    시연 손pose 거리 d 로 정렬 → stability rollout 통과 첫 후보 = g*."""

def plan_motion(p_o_t, p_o_tprime, p_ee_t) -> Pose:
    """keyframe 상대변환 T = (p_o_t)^-1 p_o_tprime 를 rigid 손-객체에 적용 →
    target end-effector pose p_ee_tprime."""

def augment(source_traj) -> list[Demo]:
    """object pose/scale[0.8,1.2](grasp/motion 재생성 금지) + camera pose +
    point-cloud drop/normal-noise → 학습용 데모셋."""

def filter_data(t_pred, rendered_video) -> bool:
    """VLM(Qwen3-VL)이 예측 설명 t_pred 와 렌더 영상 V_synth 일치 여부 판정."""
```

- 각 모듈은 직렬 의존(앞 단계 출력 = 뒤 단계 입력). `synthesize_grasp` 는 `schedule_actions` 의 `pregrasp` 분기에서 호출. `plan_motion` 은 `motion`/`grasp` 분기에서 호출.

---

## ⛓️ 불변식·가정

- (가정 1) **손 크기 prior** — 인간 손 크기의 분산이 작아 단일 scale anchor 로 metric scale 근사가 가능. 깨지면(장갑/아동/비표준 손, 손 비가시) near-metric 재구성 전체 무효.
- (가정 2) **rigid object** — SAM3D 3D 생성이 강체 기하를 가정. deformable/articulated 객체에는 적용 불가.
- (가정 3) **grasp 후 rigid 손-객체** — `plan_motion` 은 grasp 이후 손과 객체를 단일 강체로 간주. in-hand 재배향(상대 운동) 발생 시 무효.
- (가정 4) **테이블 평면 존재** — world $`z`$-축이 테이블 법선으로 정의되므로 tabletop 세팅 필수(mobile/비평면 미지원).
- (가정 5) **scale 증강의 supervision 일관성** — scale 별 grasp/motion 을 **고정**(finger articulation 만 조정)해야 일관 supervision 유지. 재생성 시 conflicting supervision 으로 학습 불안정(§IV-D ablation 으로 입증).
- (가정 6) **stability 판정** — grasp 는 시뮬 rollout 의 point-cloud 오차 $`\text{error}(g)<\epsilon`$ 일 때만 채택.

---

## 📊 하이퍼파라미터·손실

- **Grasp 합성 목적함수 (Eq. 4)**:

$$\min_{\mathbf{g},\,\{\mathbf{f}_{\mathbf{c}}\}}\quad\kappa_{w}\sum_{j=1}^{J}\Big\|\lambda\mathbf{w}_{j}-\sum_{{\mathbf{c}}\in\mathcal{C}}\mathbf{G}_{\mathbf{c}}(\mathbf{g})\mathbf{f}_{\mathbf{c}}\Big\|_{2}^{2}+\kappa_{\text{con}}\sum_{{\mathbf{c}}\in\mathcal{C}}\psi(d_{M}(\mathbf{p}_{\mathbf{c}}))+\kappa_{\text{coll}}\,\Phi_{M}(\mathbf{g})+\kappa_{\text{hh}}\,\Phi_{\text{hh}}(\mathbf{g})$$

- **Grasp ranking 거리 (Eq. 10)**: $`d(g,p_{\mathcal{E}_{\tau}}^{t})=\sum_{h\in\mathcal{E}_{\tau}}\lambda_{t}\|\Delta\mathbf{t}_{h}\|_{2}+\lambda_{r}\theta_{h}`$
- **Stability 오차 (Eq. 15)**: $`\text{error}(g)=\frac{1}{P}\sum_{p=1}^{P}\big\|\mathcal{P}_{\text{target}}^{(p)}-\mathcal{P}_{\text{sim}}^{(p)}\big\|_{2}`$

| 이름 | 값 | 출처 |
|------|----|----|
| `object_scale_aug` | `[0.8, 1.2]` | §III-D |
| `point_drop_ratio` (본문) | `30%` 제거 + 법선 30% 섭동 | §III-D |
| `point_keep_ratio` (부록) | `0.85` (=15% 제거) | §A.2, Eq. (19) |
| `noise_sample_ratio` (부록) | `15%` 표본 | §A.2 |
| `normal_noise σ` (부록) | `0.015` | §A.2, Eq. (20) |
| `kNN object δ` | `(원문 미명시)` | §A.2, Eq. (18) |
| `stability threshold ε` | `(원문 미명시)` | §A.1, Eq. (15) |
| `κ_w, κ_con, κ_coll, κ_hh` | `(원문 미명시)` | §III-C, Eq. (4) |
| `λ_t, λ_r` (ranking 가중) | `(원문 미명시)` | §A.1, Eq. (10) |
| world 원점 $`x`$ | `0.6` | §III-A |
| 데모 수 / source | `~100` | §IV-B |

> ⚠️ 본문(§III-D, 30%/30%)과 부록(§A.2, 0.85 keep·15%·σ=0.015) 사이 관측 noise
> 수치 불일치 — 구현 시 부록 값 우선 권장.

---

## 🎯 평가 메트릭

- **지표** — `data usability rate` (물리적으로 타당 + training-ready 샘플 비율) · **측정** — 입력 영상 품질 4 수준 × task 난이도 4 수준 격자(§IV-A, Figure 3).
- **지표** — `4D reconstruction success rate` · **임계값** — 최고 82% (ST2+FPose) · **비교** — TA+RANSAC 38%, VGGT+PCR 32%, ST2+PCR 76% (§IV-A, Table I).
- **지표** — `task success rate` (정책 평가) · **비교 baseline** — RigVid [46], DexMan [22] · 결과: short-horizon 100%, long-horizon Pot 78%, Stack Cups 52% (§IV-B, Table II).
- **지표** — `runtime` · **값** — 단일 영상 ≈ 4 분(영상 길이 5/10/20s → 173/201/257s) (§A.3, Table III).
- **지표(zero-shot 실세계)** — 4 meta-task 성공률 + 3 augmentation ablation(w/o scale aug · regen grasp · w/o obj pcd noise) (§IV-D, Figure 6).

---

## ✨ 변경 의도 (intent)

DexImit 의 차별점은 **embodiment gap 을 데이터 생성 이전 단계에서, depth·카메라 정보 없이 닫는다**는 데 있습니다. 직접 사전학습(시각/액션 gap 노출)이나 RL 추종(trajectory noise 민감)과 달리, 인간 손 크기 prior 로 near-metric 재구성을 확보하고 force-closure grasp + keyframe planning 으로 재구성 noise 를 액션으로 누적 전파시키지 않습니다. 여기에 Action-Centric Scheduling 으로 임의 horizon·양손 조합을 충돌 없이 배치해, 기존 방법이 막혔던 long-horizon·fine-grained 양손 task 까지 물리적으로 타당한 데이터로 합성합니다. scale 증강 시 grasp/motion 을 고정(finger articulation 만 조정)하는 설계가 supervision 일관성을 보존하는 핵심 의도입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 본 산출물은 **데이터 생성 파이프라인**이라 lerobot 의 policy family(`pi0`/`act`/`diffusion` 등)에 직접 대응하지 않습니다. 가장 가까운 접점은 출력 형식(LeRobotDataset 호환 양손 dexterous trajectory + point-cloud 관측)과 데이터 증강 단계이며, 학습 측은 DP3(3D point-cloud diffusion)에 해당해 lerobot 의 `diffusion` family 와 관측 modality(2D 이미지 vs 3D point cloud)가 달라 직접 매핑은 제한적입니다. base 후보 단정 어려움 — `/implement-design` 가 매핑 불가 판정을 낼 가능성 높음.

---

## 🚧 미해결 / 잠정

- grasp 합성 가중치 $`\kappa_{\bullet}, \lambda, \lambda_t, \lambda_r`$, stability 임계값 $`\epsilon`$, kNN $`\delta`$ 값이 원문에 없어 비워둠.
- 관측 noise 증강 수치가 본문(30%/30%)과 부록(15%·σ=0.015)에서 불일치 — Layer 1 으로 단일화하지 못하고 둘 다 기록.
- point cloud / 액션의 정규화 통계 출처가 원문에 명시 없어 가정으로 메움.
- DP3 학습 하이퍼파라미터(스텝·옵티마이저·스케줄)는 본문 미상술 — 본 Design 범위 밖(다운스트림 소비자).
- Eq. 1 의 동차변환 행렬 전개는 본문에서 표 형태로만 제시되어 LaTeX 원문을 정확히 확보하지 못함 — $`\mathbf{R}_{c\rightarrow w}, \mathbf{t}_{c\rightarrow w}`$ 분해 사실만 기록.
