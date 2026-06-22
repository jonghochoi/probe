# Design — EgoInfinity: A Web-Scale 4D Hand-Object Interaction Data Engine for Any-View Robot Retargeting and Video-to-Action Robot Learning

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | EgoInfinity: A Web-Scale 4D Hand-Object Interaction Data Engine for Any-View Robot Retargeting and Video-to-Action Robot Learning |
| 링크 | [arXiv:2606.17385](https://arxiv.org/abs/2606.17385) |
| 분석 문서 | [`analysis/2606.17385/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-22 |

> Design 대상은 본 논문의 **포팅 가능한 알고리즘 기여** — SE(3)-equivariant flow-matching **root-frame estimator $`\Phi`$** (cross-embodiment 리타게터의 핵심)입니다. 데이터 엔진의 perception 컴포넌트(MoGe-2 / Flow3r / WiLoR / SAM-x / FoundationPose++ 등)는 모두 외부 공개 모델 조합이라 Layer 1 알고리즘이 아니며, interaction-aware refinement는 규칙 기반 후처리이므로 §⛓️ 불변식·§✨ 변경 의도에서만 다룹니다.

---

## 🧮 데이터 계약

- **입력 (hand trajectory)** — per-hand 텐서 shape `(T, 7)`, dtype float32. 7 = 3D position `(x,y,z)` + unit quaternion `(w,x,y,z)`, camera frame. bilateral 이므로 `{L, R}` 두 텐서. `T = 60` frame (2초 @ 30fps; 추론 시 sliding window).
- **입력 (gravity, optional)** — `(3,)` 단위 벡터 $`{}^{c}\mathbf{g}`$, camera frame. 불가용 시 0 벡터, 학습 시 30% 확률로 drop.
- **입력 (flow state)** — noisy root frame $`({}^{c}\mathbf{R}^{r}_{\tau}, {}^{c}\mathbf{t}^{r}_{\tau}) \in SE(3)`$, flow time $`\tau \in [0,1]`$.
- **VN 인코딩** — 각 hand timestep → 5 VN 채널 `(T, 5, 3)`: `[centered position, R[:,0], R[:,1], R[:,2], gravity]` (Eq. 6). 입력 전 bilateral centroid $`\mathbf{c} = \text{mean}(2T \text{ positions})`$ 를 빼 translation 제거.
- **출력** — root frame $`{}^{c}\mathbf{p}^{r} = ({}^{c}\mathbf{R}^{r}, {}^{c}\mathbf{t}^{r}) \in SE(3)`$. flow-matching 이므로 분포 $`p({}^{c}\mathbf{p}^{r}\mid \mathbf{x})`$ 에서 다중 hypothesis 샘플. rotation 은 6D(2-vector Gram–Schmidt) → `SO(3)`, translation 은 body-frame offset `v (3,)` 예측 후 $`{}^{c}\mathbf{t}^{r} = {}^{c}\mathbf{R}^{r}\mathbf{v} + \mathbf{c}`$.
- **정규화 가정** — position 은 centroid-centered (절대 카메라 좌표 회귀 회피). quaternion 은 unit norm. 시간 축은 의미 단위(`T_window = 60`), 절대 timestamp 아님.

---

## 🧰 모듈 인터페이스

```python
def encode_hand_vn(hand_traj_LR, gravity, centroid) -> "Tensor (T, d, 3)":
    """좌/우 hand (T,7) 를 VN 5채널로 인코딩 → VN-Linear(5,d) 독립 projection →
       channel concat → VN-Linear(2d,d) fuse. centroid 제거로 translation-equivariance."""

def root_flow_velocity(traj_feat, root_state_tau, tau) -> "(R_vel, t_vel)":
    """noisy root state 를 4채널 VN 인코딩 → VN-Linear(4,d) → sinusoidal τ-MLP scale →
       traj_feat 에 가산 → VN-Transformer(L,H,d_ff) → time mean-pool (d,3) →
       rotation/translation head 가 flow velocity 예측."""

def sample_root_frames(traj_feat, n_steps=20, n_samples=K) -> "list[SE(3)]":
    """prior R0~U(SO(3)), t0~N(c, 0.5^2 I) 에서 시작, learned ODE 를 N Euler step 적분.
       window 별 다중 hypothesis 반환."""

def select_root_hypothesis(hypotheses, hand_traj, robot_model) -> "SE(3)":
    """k-means 군집 → translation linear / rotation SLERP 보간 → 각 후보를 downstream
       IK 로 스코어링(IK convergence·residual·manipulability·joint-limit margin·smoothness)
       → 최선 선택."""
```

- $`\Phi`$ 는 robot-specific: 로봇마다 별도 weight. finger joint 는 이 경로 밖에서 MANO keypoint → robot-specific geometry mapping 으로 별도 retarget.

---

## ⛓️ 불변식·가정

- **(SE(3)-equivariance)** — $`\mathbf{G}\cdot\Phi(\mathbf{x}) = \Phi(\mathbf{G}\cdot\mathbf{x})`$ for all $`\mathbf{G}\in SE(3)`$ (Eq. 1). 이 성질이 깨지면 any-view robustness 의 근거가 사라짐. VN 레이어 + centroid centering 으로 구조적 보장(학습된 성질 아님).
- **(rotation-equivariance via VN)** — 모든 내부 geometric feature 가 3D 벡터 collection 으로 표현되어 SO(3)-equivariance 가 layer 단위로 유지.
- **(거의-정적 카메라)** — exo→ego 변환을 3D 강체 reframing 으로 처리 가능하다는 가정. body-mounted/hand-held 영상은 범위 밖(online SLAM 미수행).
- **(root 모호성의 다봉성)** — 같은 손 운동이 여러 torso pose 에 대응 → 결정론적 회귀로 평균내면 무효. flow-matching 분포 모델링이 필수.
- **(static-camera reference root)** — 추론 시 각 후보를 "full trajectory 에 걸친 static reference root frame"으로 IK 스코어링(§B.3).

---

## 📊 하이퍼파라미터·손실

- 손실 식: flow-matching velocity regression — 본문은 "predicts the velocity field for both rotation and translation" 로만 기술, 정확한 loss 형태(예: conditional flow-matching MSE)는 **(원문에 명시 없음 — 가정으로 메움: $`\mathbb{E}\lVert v_\theta(x_\tau,\tau) - (x_1-x_0)\rVert^2`$ 형태의 CFM objective)**.
- prior: $`{}^{c}\mathbf{R}^{r}_{0}\sim\mathcal{U}(SO(3))`$, $`{}^{c}\mathbf{t}^{r}_{0}\sim\mathcal{N}(\mathbf{c}, 0.5^{2}\mathbb{I})`$.

| 이름 | 값 | 출처 |
|------|----|----|
| `d` (channel width) | 128 | §B.1, Tab. 5 |
| `H` (attention heads) | 4 | §B.1, Tab. 5 |
| `L` (transformer layers) | 4 | §B.1, Tab. 5 |
| `d_ff` (FFN hidden) | 512 | §B.1, Tab. 5 |
| dropout | 0.1 | §B.1, Tab. 5 |
| input VN channels / hand | 5 | §B.1, Tab. 5 |
| `N` (inference Euler steps) | 20 | §4.1, §B.1 |
| epochs / steps-per-epoch | 500 / 20 | §B.2, Tab. 6 |
| batch size | 1024 | §B.2, Tab. 6 |
| optimizer / LR / grad clip | Adam / `1e-3` / 1.0 | §B.2, Tab. 6 |
| `T` / `f` (window) | 60 frame / 30 fps | §B.2, Tab. 6 |
| `N_ctrl` (control points) | 7 | §B.2, Tab. 6 |
| gravity dropout | 0.30 | §4.2 |

---

## 🎯 평가 메트릭

- **지표** — `IK Rate` (per-frame IK 성공률) · **임계값** — 높을수록 좋음 (보고치 0.706–0.821) · **비교 baseline** — 본문에 외부 baseline 없음(자체 embodiment 간 비교만).
- **지표** — `Pos./Ori. Error` (IK target↔달성 pose, $`\ell_2`$ cm / geodesic °) · 보고치 2.86–10.27 cm / 6.73–12.17°.
- **지표** — `Manipulability` $`\sqrt{\det(JJ^{\top})}`$ · `Joint-Limit Margin` (rad) · `Smoothness` (평균 제곱 관절속도 $`\dot{q}`$).
- 데이터 엔진 측 정량 메트릭(perception fidelity 수치 표)은 본문 제시 없음 — 주로 정성·통계(Fig. 4) 검증.

---

## ✨ 변경 의도 (intent)

기존 cross-embodiment 리타게팅은 dexterous hand·parallel gripper·humanoid upper-body 등 특정 embodiment class 를 가정하고, demonstration 과 target 이 정렬될 때만 잘 동작합니다. EgoInfinity 의 차별점은 **전신 pose 복원을 포기**하고 손 궤적만으로 robot-specific **kinematic root frame** 을 추정하는 것입니다. 손만 보이는 임의 시점 영상에서도 동작하며(partial-body), root 의 모호성을 flow-matching 다봉 분포로 모델링한 뒤 IK 점수로 후보를 고릅니다. SE(3)-equivariance(VN)로 시점별 재학습을 없앤 것이 핵심 — "exact kinematic imitation" 대신 "functional motion transfer" 로 문제를 재정의해 web-scale·any-view 로 확장합니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 직접 대응 family 없음. lerobot 정책(`pi0`/`smolvla`/`act`/`diffusion`)은 image+state→action policy 인 반면, 본 알고리즘은 **데이터 전처리/리타게팅** 단계(hand traj → robot joint traj)로 policy 학습 *이전* 에 위치. flow-matching 메커니즘은 `pi0`/`diffusion` 의 flow/diffusion 헤드와 개념적으로만 유사하고, VN-equivariant SE(3) backbone·IK 후처리·sim procedural data gen 은 lerobot 에 base 가 없어 `/implement-design` 에서 `🚧 매핑 불가`(UNMAPPABLE) 가능성이 높음. 데이터 변환 유틸리티로 본다면 `datasets/transforms/` 계열에 신규 모듈로 얹는 것이 후보.

---

## 🚧 미해결 / 잠정

- flow-matching loss 의 정확한 형태(CFM vs rectified flow, time schedule)가 본문에 미명시 — 위 §📊 에 가정으로 표기.
- finger retarget 의 "geometry-based, robot-specific mapping" 구체 알고리즘 미명시.
- `K` (hypothesis 샘플 수), k-means cluster 수, sliding-window stride 의 구체 값 미명시(stride 는 "조정 가능"으로만 기술).
- rotation head 의 "invariant MLP" 내부 구조 및 translation $`\dot{\mathbf{v}}`$ head 의 정확한 layer 구성 부분 명시.
- IK 스코어링의 가중치(IK convergence·residual·manipulability·margin·smoothness 결합식) 미명시.
