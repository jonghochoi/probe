# Design — UniCross: Unified Cross-Skill Dexterous Manipulation Synthesis

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | UniCross: Unified Cross-Skill Dexterous Manipulation Synthesis |
| 링크 | [arXiv:2607.28198](https://arxiv.org/abs/2607.28198) |
| 분석 문서 | [`analysis/2607.28198/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-08-02 |

---

## 🧮 데이터 계약

시뮬레이션 상태 기반 정책이며 이미지·언어 모달리티가 없습니다. 시간 축은 제어 스텝(20 Hz) 단위이고, 정책은 단일 스텝 관측 → 단일 스텝 행동의 Markov 형태입니다(프레임 스태킹·recurrent 없음).

- **입력** — `hand_state`: shape `(B, 2 * n_joints)`, float32, $`[\mathbf{q}_{t},\mathbf{q}_{t-1}^{\text{target}}]`$ 연접. `n_joints` 는 손가락 관절 + 가상 손목 관절 6개의 합 (Allegro 16 + 6, MANO 20 + 6, Sharpa Wave 22 + 6). 정규화 방식 `(원문에 명시 없음 — 가정으로 메움)` — 관절 한계 기준 정규화로 가정합니다.
- **입력** — `object_state`: shape `(B, n_links * (1 + 1 + 3))`, float32, 링크별 `[contact_binary, contact_force_magnitude, distance_vector_to_nearest_surface_point]` 연접. `contact_binary` $`\in\{0,1\}`$ , 거리 벡터는 hand frame 기준으로 가정 `(원문에 명시 없음 — 가정으로 메움)`. 힘 크기 스케일링 `(원문에 명시 없음 — 가정으로 메움)`.
- **입력** — `objective_features`: shape `(B, 55)`, float32, `[task_mode_onehot(10), task_axis_hand_frame(3), pose_current(21), pose_target(21)]`. `pose_*` 는 `[x_o^h(3), q_o^h(4), x_o^r(3), q_o^r(4), x_h^r(3), q_h^r(4)]` 순의 위치 + 쿼터니언 6쌍.
- **출력** — `action`: shape `(B, n_joints)`, float32, 증분 명령. 정책 출력 자체의 범위 `(원문에 명시 없음 — 가정으로 메움)` — 관절별 스케일 $`\boldsymbol{\alpha}`$ 를 곱해 사용하므로 정규화 출력으로 가정합니다.
- **파생 출력** — `q_act`: shape `(B, n_joints)`, 목표 관절 위치, $`\mathbf{q}_{t}^{\text{act}}=\text{clamp}(\mathbf{q}_{t}^{\text{ref}}+\boldsymbol{\alpha}\cdot\mathbf{a}_{t},\mathbf{q}_{\min},\mathbf{q}_{\max})`$ 로 계산됩니다. 기준점 $`\mathbf{q}_{t}^{\text{ref}}`$ 는 손가락 관절에 대해 $`\mathbf{q}_{t-1}^{\text{act}}`$ , 가상 손목 관절에 대해 현재 목표 손목 자세 $`(\hat{\mathbf{x}}_{h}^{r},\text{euler}(\hat{\mathbf{q}}_{h}^{r}))`$ — 이 분기가 알고리즘의 핵심 비대칭입니다.
- **컨트롤러 경계** — `q_act` 는 PD 컨트롤러로 관절 토크로 변환되어 시뮬레이터에 인가됩니다. PD 게인 `(원문에 명시 없음 — 가정으로 메움)`.

---

## 🧰 모듈 인터페이스

```python
def build_observation(hand_state, object_state, objective_features) -> Tensor:
    """세 블록을 연접해 정책 입력 o_t = (s_h, s_o, g) 를 만든다."""

def encode_objective(objective_features) -> Tensor:
    """55-dim 목표 특징을 MLP([128, 64]) 로 인코딩한다. 나머지 두 블록은 인코딩하지 않는다."""

def policy_forward(hand_state, object_state, objective_embedding) -> Tensor:
    """main MLP([512, 256, 128]) 로 증분 행동 a_t 를 예측한다."""

def to_target_joint_positions(action, q_ref, alpha, q_min, q_max) -> Tensor:
    """q_act = clamp(q_ref + alpha * action, q_min, q_max). q_ref 는 손가락/손목에서 서로 다르다."""

def instantiate_targets(skill, state, t) -> ObjectiveFeatures:
    """스킬별 Tracked/Fixed/Free 배정에 따라 d^h 와 g_target 을 채운다 (§🧮 표 참조)."""

def compute_reward(state, targets, weights) -> Tensor:
    """r = r_goal + r_track + r_reg. 스킬 차이는 weights 와 targets 로만 들어간다."""

def distill(expert_policies, student_policy, env) -> None:
    """vanilla DAgger — student 롤아웃 상태에 대해 expert 행동을 질의하고 MSE 로 학습한다."""
```

- **`encode_objective`** — 목표 특징만 별도 인코더를 거칩니다. 손 상태·물체 상태는 raw 로 main MLP 에 들어가는 비대칭 구조입니다.
- **`instantiate_targets`** — 스킬 정의가 코드가 아닌 데이터(배정표)로 표현되는 지점입니다. 새 스킬 추가는 이 함수의 테이블에 행을 하나 더하는 것으로 끝나야 합니다.
- **`compute_reward`** — 보상 항 집합은 스킬 불변이고, 계수 벡터만 스킬 의존입니다(§📊 참조). 이 계약이 깨지면 통일 형식의 주장이 무너집니다.
- **`distill`** — expert query rate 100% 를 전제로 하므로, 질의 가능한 동일 규격 전문가가 존재해야 합니다. 전문가가 다른 형식(예: 모방 학습 정책)이면 이 인터페이스는 성립하지 않습니다.

---

## ⛓️ 불변식·가정

- **(가정 1) 스킬 = 목표 변수 배정** — 6개 목표 변수 $`(\hat{\mathbf{x}}_{o}^{h},\hat{\mathbf{q}}_{o}^{h},\hat{\mathbf{x}}_{o}^{r},\hat{\mathbf{q}}_{o}^{r},\hat{\mathbf{x}}_{h}^{r},\hat{\mathbf{q}}_{h}^{r})`$ 각각에 Tracked / Fixed / Free 를 배정하면 스킬이 완전히 정의됩니다. 관측 차원·행동 차원·보상 항 집합은 스킬에 따라 변하지 않습니다.
- **(가정 2) Free 는 항등적으로 보상 0** — Free 로 지정된 변수의 목표는 현재값으로 대입되므로 대응 추적 항이 0 이 됩니다. 즉 보상식을 재작성하지 않고 자유도를 해제할 수 있습니다.
- **(가정 3) 상대 표현의 위치 불변성** — root frame 이 에피소드 시작 손목 자세로 정의되므로, 세계 좌표 위치가 달라도 동일 정책이 동작합니다. 이 불변성이 깨지면(예: 절대 좌표 관측 추가) 손목 무작위 초기화 하의 일반화 주장이 무효화됩니다.
- **(가정 4) 물체 표현의 손 중심성** — 물체 정보가 링크 기준 접촉·거리 관계로만 들어오므로 표현 차원이 물체 기하에 독립입니다. 미학습 기하 일반화와 손 형상 교체가 모두 이 성질에 의존합니다.
- **(가정 5) 인핸드 목표는 1스텝 앞선 국소 목표** — 회전 $`\hat{\mathbf{q}}_{o,t}^{h}=\mathbf{R}(\omega_{\max}\Delta t,\mathbf{d}^{\text{h}})\cdot\mathbf{q}_{o,t}^{h}`$ , 이동 $`\hat{\mathbf{x}}_{o,t}^{h}=\mathbf{x}_{o,t}^{h}+v_{\max}\Delta t\cdot\mathbf{d}^{\text{h}}`$ 로 매 스텝 현재 상태에서 재생성됩니다. 절대 목표가 없어 무한 연속 운동이 가능하고, 대신 "얼마나 갔는가"는 보상이 아니라 평가에서만 측정됩니다.
- **(가정 6) 행동 기준점의 해부학적 분기** — 손가락은 직전 행동, 손목은 현재 목표 자세를 증분 기준점으로 씁니다. 이 분기를 없애면(양쪽 모두 직전 행동) 큰 진폭 손목 이동을 요구하는 스킬만 선택적으로 붕괴합니다.
- **(가정 7) 전문가 호환성** — 스킬 간 최적 행동이 상충하지 않아 동일 용량 단일 네트워크가 전부를 담을 수 있다는 가정. 증류 무손실성은 이 가정의 실험적 귀결이며, 상충하는 스킬이 추가되면 성립하지 않습니다.
- **(가정 8) 관측 가용성** — 링크-물체 거리 벡터와 두 프레임 물체 자세는 시뮬레이터 특권 정보입니다. 이 정보가 없는 환경에서는 알고리즘이 그대로 성립하지 않습니다.

---

## 📊 하이퍼파라미터·손실

**보상 (식 1)**

$$r_{t}=r_{t}^{\text{goal}}+r_{t}^{\text{track}}+r_{t}^{\text{reg}}$$

**목표 항 (식 2)**

$$r_{t}^{\text{goal}}=r_{t}^{\text{contact}}+r_{t}^{\text{motion}}$$

$$r_{t}^{\text{contact}}=\frac{1}{N}\sum_{i}^{N}(-w_{\text{dis}}\cdot d_{i}+w_{\text{con}}\cdot c_{i}+w_{\text{f}}\cdot f_{i})$$

$$r_{t}^{\text{motion}}=w_{\text{p}}\cdot\text{min}(\mathbf{v}_{o}^{h}\cdot\mathbf{d}^{\text{h}},v_{\max})$$

**추적 항 (식 3)**

```math
r_{t}^{\text{track}}=\begin{aligned} &w_{opr}\|\mathbf{x}_{o,t}^{r}-\hat{\mathbf{x}}_{o}^{r}\|^{2}+w_{oqr}\mathcal{A}(\mathbf{q}_{o,t}^{r},\hat{\mathbf{q}}_{o}^{r})\\ &+w_{oph}\|\mathbf{x}_{o,t}^{h}-\hat{\mathbf{x}}_{o}^{h}\|^{2}+w_{oqh}\mathcal{A}(\mathbf{q}_{o,t}^{h},\hat{\mathbf{q}}_{o}^{h})\\ &+w_{hpr}\|\mathbf{x}_{h,t}^{r}-\hat{\mathbf{x}}_{h}^{r}\|^{2}+w_{hqr}\mathcal{A}(\mathbf{q}_{h,t}^{r},\hat{\mathbf{q}}_{h}^{r}).\end{aligned}
```

**정규화 항 (식 4)**

$$r_{t}^{\text{reg}}=r_{t}^{\text{pose}}+r_{t}^{\text{vel}}+r_{t}^{\text{energy}}+r_{t}^{\text{drop}}$$

각 항은 $`r_{t}^{\text{pose}}=w_{\text{pose}}\sum_{i=1}^{N}(q_{i,t}-q_{i,0})^{2}`$ , $`r_{t}^{\text{vel}}=w_{\text{vel}}\|\dot{\mathbf{x}}_{h,t}\|^{2}+w_{\text{ang}}\|\boldsymbol{\omega}_{h,t}\|^{2}`$ , $`r_{t}^{\text{energy}}=w_{\tau}\|\boldsymbol{\tau}_{t}\|^{2}`$ , $`r_{t}^{\text{drop}}=w_{\text{drop}}\mathbb{I}_{\text{drop}}`$ 입니다.

**증류 손실** — student 롤아웃 상태에 대한 expert 행동과의 MSE (`imitation loss`).

**행동 변환**

$$\mathbf{q}_{t}^{\text{act}}=\text{clamp}(\mathbf{q}_{t}^{\text{ref}}+\boldsymbol{\alpha}\cdot\mathbf{a}_{t},\mathbf{q}_{\min},\mathbf{q}_{\max})$$

**보상 계수 (Table 8)**

| 이름 | 값 | 출처 |
|------|----|----|
| `w_dis` (grasp) | `20.0` | Table 8 |
| `w_dis` (other skills) | `0.2` | Table 8 |
| `w_con` (grasp) | `0.75` | Table 8 |
| `w_con` (other skills) | `0.075` | Table 8 |
| `w_f` (grasp) | `0.05` | Table 8 |
| `w_f` (other skills) | `0.005` | Table 8 |
| `w_p` (grasp & relocate) | `0.0` | Table 8 |
| `w_p` (rotation) | `1.0` | Table 8 |
| `w_p` (translation) | `10.0` | Table 8 |
| `w_opr` | `-5.0` | Table 8 |
| `w_oqr` | `-1.0` | Table 8 |
| `w_oph` | `-5.0` | Table 8 |
| `w_oqh` | `-1.0` | Table 8 |
| `w_hpr` | `-15.0` | Table 8 |
| `w_hqr` | `-3.0` | Table 8 |
| `w_pose` | `-0.3` | Table 8 |
| `w_vel` | `-0.5` | Table 8 |
| `w_ang` | `-0.05` | Table 8 |
| `w_tau` | `-0.1` | Table 8 |
| `w_drop` | `-10.0` | Table 8 |
| $`v_{\max}`$ , $`\omega_{\max}`$ , $`\boldsymbol{\alpha}`$ , $`\mathbf{q}_{\min}`$ / $`\mathbf{q}_{\max}`$ , 낙하 거리 임계 | `(원문 미명시)` | — |

**PPO (Table 6) · DAgger (Table 7) · 네트워크 · 시뮬레이션**

| 이름 | 값 | 출처 |
|------|----|----|
| `gamma` | `0.99` | Table 6 |
| `gae_lambda` | `0.95` | Table 6 |
| `learning_rate` (PPO) | `0.005` | Table 6 |
| `kl_threshold` | `0.02` | Table 6 |
| `truncate_gradients` | `True` | Table 6 |
| `max_grad_norm` | `1.0` | Table 6 |
| `mini_epochs` | `5` | Table 6 |
| `batch_size` (PPO) | `32768` | Table 6 |
| `episode_length` (rotation) | `400` | Table 6 |
| `episode_length` (other skills) | `64` | Table 6 |
| `horizon_length` (grasp & relocate) | `64` | Table 6 |
| `horizon_length` (rotation & translation) | `8` | Table 6 |
| `batch_size` (DAgger) | `16384` | Table 7 |
| `learning_rate` (DAgger) | `3.0e-4` | Table 7 |
| `max_epochs` | `3500` | Table 7 |
| `gradient_updates_per_epoch` | `100` | Table 7 |
| `rollout_steps` | `32` | Table 7 |
| `replay_buffer_size` | `1.0e6` | Table 7 |
| `expert_query_rate` | `100%` | Table 7 |
| objective encoder hidden | `[128, 64]` | Appendix A |
| main MLP hidden | `[512, 256, 128]` | Appendix A |
| simulation frequency | `120 Hz` | §3 |
| control frequency | `20 Hz` | §3 |
| 병렬 환경 수 · 총 학습 스텝 · 시드 수 | `(원문 미명시)` | — |

**도메인 랜덤화 (Appendix C)**

| 이름 | 값 | 출처 |
|------|----|----|
| object mass | `[0.002, 0.04]` kg | Appendix C |
| contact friction (손·물체 공통) | `[0.3, 3.0]` | Appendix C |
| joint position noise | $`\epsilon_{q}\sim\mathcal{U}(-0.02,0.02)`$ rad | Appendix C |
| 학습 중 외란력 | $`\mathbf{f}=2.0\,m_{\mathrm{obj}}\,\boldsymbol{\epsilon}_{f}`$ , $`\boldsymbol{\epsilon}_{f}\sim\mathcal{N}(\mathbf{0},\mathbf{I}_{3})`$ | Appendix C |
| 외란력 감쇠 / 교체 확률 | `0.9` / `0.25` (시뮬레이션 스텝당) | Appendix C |
| 평가용 외란력 크기 | $`[0,10m_{\mathrm{obj}}g]`$ | §4.4 |

---

## 🎯 평가 메트릭

- **지표** — `SR (%)` (성공률) · **임계값** — 스킬별 정의 아래 · **비교 baseline** — GraspXL(grasp), RotateIt(rotation), Yin et al.(translation), naive PD 손목 제어(relocation), 그리고 증류 전 10개 per-skill 전문가.
- **Grasp** — 성공 = 에피소드(75 스텝) 전 구간 낙하 없이 들어 올림. 50 스텝 후 손목에 고정 상방 힘 인가, 손목 초기 위치는 물체 위 5 cm, 물체당 무작위 테이블 자세 25개.
- **Relocate** — `SR` 성공 = 목표 자세 3 cm · 0.15 rad 이내 도달 + 무낙하. 보조 지표 `PE (cm)` · `AE (rad)` = 마지막 25 스텝 평균(무낙하 trial 한정). 목표 오프셋 x·y $`[-0.1,0.1]`$ m, z $`[0.2,0.4]`$ m, roll·pitch·yaw $`[-0.75,0.75]`$ rad.
- **Rotate** — 성공 = 400 스텝 내 각변위 $`\pi/2`$ rad 초과 + 무낙하. 보조 지표 `Rot. (rad)` = 무낙하 trial 평균 누적 회전각. 방향 6종 × 25 trial = 150 trial, 손목 자세 세계 좌표 무작위 초기화.
- **Translate** — 성공 = 50 스텝 내 선변위 5 cm 초과 + 무낙하. 보조 지표 `Trans. (cm)` = 무낙하 trial 평균 이동 거리. 방향 2종 × 25 trial = 50 trial.
- **Long-horizon** — `Overall SR` = grasp · relocate · in-hand 세 단계가 모두 성공한 시퀀스 비율(단일 정책 연속 실행). 참조값: Gr.+Re.+Rot. `87.4`, Gr.+Re.+Trans. `96.3`.
- **일반화 축** — 미학습 기하(구·육각기둥·팔각기둥), 손 형상(Allegro / MANO / Sharpa Wave, 물체 0.7배 스케일), 외란(무작위 방향 · $`[0,10m_{\mathrm{obj}}g]`$).
- **증류 품질 판정** — 전문가 대비 4스킬 전 항목 차이. 참조값(전문가 → 증류 정책 SR): grasp 99.0 → 98.7, relocate 99.1 → 99.0, rotate 99.1 → 98.8, translate 99.3 → 99.1.

---

## ✨ 변경 의도 (intent)

기존 손재주 조작 연구는 스킬을 **접촉 체제**로 구분해 왔습니다 — 지속적 강접촉이 필요한 잡기/옮기기와, 잦은 접촉 재구성이 필요한 인핸드 조작을 별개 문제로 두고 각각에 전용 행동 제약(제한된 행동 공간), 전용 셋업(손바닥을 위로 향한 고정 손목), 심지어 전용 손 형상을 부여했습니다. 그 결과 한 스킬이 도달한 상태가 다음 스킬의 유효 시작 상태가 되지 못해 장기 연쇄가 구조적으로 불가능했습니다. 본 Design 의 변경 의도는 구분 기준을 접촉에서 **손-물체 상대 운동**으로 옮기는 것입니다. 그러면 네 스킬은 "두 기준계(root / hand)에서 어떤 목표 변수를 추적·고정·자유화하는가"의 배정표 차이로 환원되고, 관측·행동·보상 규격을 하나로 유지할 수 있습니다. 이 통일의 대가로 per-skill 특화 성능을 잃지 않는다는 것(baseline 자신의 셋업에서도 우위), 그리고 형식이 같기 때문에 다중 전문가 증류가 특수 기법 없이 near-lossless 로 성립한다는 것이 검증 대상 주장입니다. 부수적으로 스킬 특화 가정이 사라지면서 손 형상 교체와 장기 연쇄가 별도 설계 없이 따라옵니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 대응 base 없음. 본 Design 은 시뮬레이터 내 on-policy RL(PPO) + DAgger 증류 파이프라인이며, `lerobot` 의 정책군(`pi0` / `pi05` / `pi0_fast` / `smolvla` / `act` / `diffusion`)은 모두 데이터셋 기반 모방 학습 정책이라 학습 루프·환경 인터페이스가 겹치지 않습니다. 부분 이식이 가능한 조각을 굳이 꼽자면 (a) 55차원 목표 특징을 별도 MLP 인코더로 처리한 뒤 main 네트워크에 합류시키는 조건부 구조, (b) 손가락/손목에 서로 다른 증분 기준점을 쓰는 행동 파라미터화 두 가지이며, 둘 다 정책 학습 알고리즘이 아니라 액션 헤드 설계 수준의 차용입니다. 실제 매핑 가부는 `/implement-design` 의 판단에 맡깁니다.

---

## 🚧 미해결 / 잠정

- **행동 스케일 $`\boldsymbol{\alpha}`$ · 관절 한계 · PD 게인 미명시** — 재현 시 손 모델 URDF 의 관절 한계와 시뮬레이터 기본 게인으로 채워야 합니다. 행동 스케일은 제어 주기와 결합되므로 주기를 바꾸면 재조정이 필요합니다.
- **$`v_{\max}`$ · $`\omega_{\max}`$ 미명시** — 운동 항 상한과 회전 목표 갱신 각속도의 실수값이 본문·부록 어디에도 없습니다. 이 둘은 인핸드 스킬의 목표 난도를 직접 결정하므로 재현 편차의 주요 원인이 될 수 있습니다.
- **낙하 판정 임계 미명시** — "모든 손 링크와 물체 사이 거리가 임계를 넘는지"로 정의되나 임계값이 없습니다.
- **정규화 규약 미명시** — 관측 각 블록(관절각, 접촉력 크기, 거리 벡터, 자세)의 정규화 방식이 기술되지 않았습니다. 접촉력 크기는 물체 질량 범위(2–40 g)에 강하게 의존하므로 스케일 가정이 결과에 영향을 줍니다.
- **거리 벡터의 기준 프레임 미명시** — hand frame 으로 가정했으나 본문은 프레임을 특정하지 않습니다.
- **학습 규모 미명시** — 병렬 환경 수, 총 학습 스텝, 시드 수, 학습 시간, GPU 사양이 전부 없습니다. 전문가 10개 + 증류 1회의 총 비용을 추정할 근거가 없습니다.
- **스킬 전환 정책 부재** — 어떤 스킬을 언제 실행할지 결정하는 상위 계층은 이 Design 범위 밖이며, 장기 연쇄 실험도 순서를 외부에서 주입한 조건입니다.
- **손목 자유도 전제** — 세 손 모두 6-DoF 가상 손목을 갖습니다. 손목 자유도가 없는 하드웨어로의 축약형(relocation 제외, rotation/translation 만)이 성립하는지는 원문에서 검증되지 않았습니다.
