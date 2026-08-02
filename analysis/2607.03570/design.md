# Design — Cross-Embodiment Robot Manipulation via a Unified Hand Action Space

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Cross-Embodiment Robot Manipulation via a Unified Hand Action Space |
| 링크 | [arXiv:2607.03570](https://arxiv.org/abs/2607.03570) |
| 분석 문서 | [`analysis/2607.03570/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-08-02 |

---

## 🧮 데이터 계약

세 개의 계약으로 나뉩니다 — (1) 손별 구 구성(오프라인 1 회), (2) 정책 관측/액션(런타임 매 스텝), (3) 액션 → 관절각 디코딩(CIK).

**오프라인 구성 (손별 1 회)**

- **입력** — 로봇 손 URDF + 열린 손 자세(손가락 완전 신전, 손끝 법선이 손바닥 법선과 근사 정렬).
- **출력 (구 파라미터)** — 반지름 $`r=\frac{2l}{\pi}`$ (스칼라, $`l`$ = 손바닥 중심→손끝 평균 거리), 구 중심(손바닥 중심에서 바깥 손바닥 법선 방향 $`r`$ 이동), 구 프레임($`+z`$ = 바깥 손바닥 법선, $`+x`$ = 중지 방향, $`y`$ = 오른손 법칙).
- **출력 (표면 대응)** — 구 표면 균일 샘플점마다 $`(\theta,\phi)`$ + 바깥 법선, 그리고 손 내측 표면 최근접 투영점과의 대응. 샘플점 개수는 `(원문에 명시 없음 — 가정으로 메움)`.
- **출력 (관절 분류)** — 관절별 `lateral` / `encompassing` 라벨.
- **출력 (lateral lookup table)** — lateral 관절마다 $`q_{\text{lateral}}\mapsto\theta_{\text{fingertip}}`$ 매핑. 스윕 간격은 "uniform steps" 로만 기술되고 수치는 `(원문에 명시 없음 — 가정으로 메움)`.

**정책 관측 (런타임)**

- **입력 (hand configuration)** — 손가락 체인을 뿌리→손끝 7 개 등간격 점으로 이산화한 뒤 본문 정책은 **중간점 + 손끝 2 점**만 유지. 점별로 위치(FK), 선속도·각속도(Jacobian × 관절속도). 전부 정규 구 좌표계 표현 후 손별 반지름 $`r`$ 로 정규화. 손가락 5 개 기준 점 10 개 (4 손가락 손은 약지 관측 복제).
- **입력 (task state)** — 표준 인핸드 조작 관측군: goal rotation, object pose, object linear/angular velocity, 목표 방향과의 quaternion 차, 이전 액션. 원 관절값(joint positions/velocities)은 임베디먼트 간 의미·범위가 달라 **직접 사용하지 않습니다**.
- shape / dtype — 전체 관측 벡터의 최종 차원은 `(원문에 명시 없음 — 가정으로 메움)`. 개별 점당 위치 3 + 선속도 3 + 각속도 3.

**정책 액션 (런타임)**

- **출력** — 연속 벡터 shape `(B, 15)`: driving plane 별 $`\Delta\theta`$ 5 개 + plane 당 driving vector 2 개의 $`\Delta r`$ 10 개, 즉 $`5+2\times 5`$.
- **경계** — $`\Delta\theta`$ 는 손별 lookup table 의 극단값으로 클립. $`\Delta r`$ 은 구간 $`[-2,2]`$. driving vector 는 $`\phi=60^{\circ}`$, $`\phi=120^{\circ}`$ 에 고정 배치.
- **4 손가락 임베디먼트** — 약지 방위 위치에 평면을 하나 더 두어 5 평면을 유지하되, 약지 변형 계산 시 중복 평면의 $`\Delta\theta`$ / $`\Delta r`$ 을 **평균한 뒤** 보간.

**CIK 출력**

- **출력** — 손별 관절 목표 위치 $`\mathbf{q}`$ (차원 = 해당 손 DOF). 저수준 PD 제어기가 추종.

**실환경 배포 시 추가 계약 (비대칭 actor-critic)**

- **actor 관측** — 물체·손 관절의 **위치 정보만**.
- **critic 관측** — actor 관측 + 물체·손의 선속도·각속도까지 포함한 전체 상태 (학습 시에만).

---

## 🧰 모듈 인터페이스

```python
def create_hand_sphere(urdf, open_hand_config) -> (center, radius, frame):
    """URDF + 열린 손 자세에서 손별 정규 구를 자동 구성. r = 2l/pi,
       중심 = 손바닥 중심 + r * 바깥 손바닥 법선, +z = 손바닥 법선, +x = 중지 방향."""

def build_surface_correspondence(hand_surface, sphere_points) -> correspondence:
    """구 표면 균일 샘플점을 손 내측 표면 최근접점으로 투영해
       (표면점 -> (theta, phi)) 조밀 대응 생성. 자세 불변."""

def classify_joints(urdf, forward_kinematics) -> {joint_id: "lateral" | "encompassing"}:
    """관절을 전 가동범위로 스윕하며 손끝 (theta, phi, r) 변화로 지배 효과 판정.
       회전축이 손끝을 향하면 나머지 관절을 부분 굴곡시킨 뒤 재스윕."""

def build_lateral_lookup(joint_id, sphere, correspondence) -> table:
    """lateral 관절 값을 균일 스윕하며 각 값에서 기준(미변형) 구 위로
       encompassing 관절을 풀고, 그 결과 fingertip theta 를 기록."""

def deform_sphere(delta_theta, delta_r, plane_thetas, vector_phis) -> deformed_points:
    """driving plane 회전(lateral) + driving vector 반경 변위(radial)를
       (theta, phi) 파라미터 공간 보간으로 표면 전체 변형장으로 복원."""

def cascade_ik(deformed_points, correspondence, lookup_tables, classification) -> q:
    """1) lateral: theta_fingertip = theta_initial + delta_theta -> 표 조회.
       2) encompassing: 손가락별 근위->원위 1 회 통과, 관절마다 하위 링크
          목표점을 국소 프레임으로 옮겨 각도를 직접 계산. 반복 최적화 없음.
       사전 단계로 반경 좌표가 음수인 구 점은 폐기하고, 도달 가능 점이
       남지 않은 encompassing 관절은 완전 폐쇄 자세로 명령."""

def build_homogeneous_observation(q, qd, fk, jacobian, radius) -> obs:
    """손가락 체인 7 점 중 중간점 + 손끝의 위치/선속도/각속도를
       정규 구 좌표계로 표현하고 radius 로 정규화."""
```

- **create_hand_sphere / build_surface_correspondence / classify_joints / build_lateral_lookup** — 손별 오프라인 1 회. 산출물은 정책과 무관한 손 자산(asset)이며, 새 손을 추가하는 비용은 이 네 함수의 실행으로 한정됩니다.
- **deform_sphere → cascade_ik** — 매 정책 스텝 호출되는 런타임 경로(= Sphere Controller). 외부 호출 계약: 정책 출력 15 차원 → 변형된 구 → 관절 목표 $`\mathbf{q}`$ → 저수준 PD. 실환경 파이프라인에서 최대 150 Hz 로 동작하며 논문 셋업의 병목은 CIK 가 아니라 시리얼 통신과 AprilTag 포즈 추정이었습니다.
- **cascade_ik 는 미분 불가 경로** — lookup table 조회 + 대수 해로 구성되어 gradient 가 흐르지 않습니다. 손실은 **구 변형 공간에 정의**되어야 하며(RL 은 액션 공간이 곧 최적화 대상이라 문제되지 않음), 관절 공간 손실을 CIK 로 역전파하는 사용법은 논문에 근거가 없습니다.
- **build_homogeneous_observation** — 관측 파이프라인. 액션 통일만으로는 불충분하며, 관측도 같은 구 좌표계로 내려야 단일 정책이 여러 손에서 성립한다는 것이 논문의 명시적 전제입니다.
- **정책 (actor/critic)** — 은닉 $`[512,512,256,128]`$, ELU 활성. RSL-RL PPO. 실환경 배포용은 비대칭 actor-critic.

---

## ⛓️ 불변식·가정

- (가정 1) 손 표면점의 구면좌표 라벨 $`(\theta,\phi)`$ 는 **자세 불변**입니다. 3D 위치는 관절 상태에 따라 변하지만 라벨은 고정이므로 서로 다른 손이 하나의 좌표 도메인을 공유할 수 있습니다 — UHAS 전체를 지탱하는 핵심 불변식.
- (가정 2) 구의 북극이 손바닥 프레임에 **강체로 고정**되어 있으므로 극각 변형 $`\Delta\phi`$ 는 불필요하고, 변형은 $`(\Delta\theta,\Delta r)`$ 두 성분으로 충분합니다.
- (가정 3) 모든 관절은 손끝의 $`\theta`$ (lateral) 또는 $`(r,\phi)`$ (encompassing) 중 한쪽에 **지배적** 효과를 갖습니다. 이 이분법이 깨지면 lookup table 과 cascade 가 동시에 무효가 됩니다.
- (가정 4) UHAS 정식화에서 손가락들은 **기구학적으로 독립**이므로 lateral / encompassing 해를 손가락별로 순차·독립 계산할 수 있습니다.
- (가정 5) 반지름 $`r=\frac{2l}{\pi}`$ 는 손바닥 중심에서 손끝까지 약 $`90^{\circ}`$ 호를 덮으며, 구가 손의 자연스러운 파지 작업 공간 안에 놓이도록 합니다.
- (가정 6) 모든 거리를 손별 $`r`$ 로 정규화하면 척도 차이가 제거되어 손가락 수·기구 구조가 다른 손들이 하나의 단위 구 표현을 공유합니다. 손별 원 구 파라미터는 CIK 를 위해 보존됩니다.
- (가정 7) 음의 반경 변형은 오류가 아니라 **의도된 표현**입니다. CIK 호출 전에 반경 좌표가 음수인 구 점을 폐기하고, 도달 가능 점이 남지 않은 encompassing 관절은 완전 폐쇄로 명령합니다 — 격렬한 재배향에서 손가락을 빠르게 접기 위한 설계.
- (가정 8) 4 손가락 손은 약지 위치의 평면·관측을 **복제**해 5 손가락과 차원을 맞춥니다. 이는 손가락 개수만 정렬할 뿐 형상 차이를 흡수하지 않습니다.
- (가정 9) 액션 공간 표현력에는 **하한**이 있습니다. driving plane 3 개로는 과제가 수렴하지 않았습니다(4~5 개는 유사 성능).
- (가정 10) 통일은 **기구학 수준에 한정**됩니다. 저수준 PD 파라미터·액추에이터 동역학은 통일되지 않으며, 저자는 이를 명시적 한계로 듭니다.

---

## 📊 하이퍼파라미터·손실

**보상 (식 1)**

$$r=w_{d}\,d+w_{r}\,r_{\text{rot}}+w_{\text{lat}}\,p_{\text{lat}}+w_{\text{rad}}\,p_{\text{rad}}+b_{\text{success}}+p_{\text{fall}}$$

$`d`$ = 물체-목표 거리, $`r_{\text{rot}}`$ = 방향 정렬 보상, $`p_{\text{lat}}`$ / $`p_{\text{rad}}`$ = lateral / encompassing 관절 위치의 기준 자세 이탈 페널티, $`b_{\text{success}}`$ = 0.1 radian 허용 오차 내 목표 도달 시 보너스, $`p_{\text{fall}}`$ = 물체 낙하 페널티. 기본 보상 정식화는 NVIDIA Isaac Lab Reposing Cube 환경을 그대로 쓰고, 뒤의 두 페널티 항만 **임베디먼트 특화 착취 억제 목적**으로 추가된 것입니다.

| 이름 | 값 | 출처 |
|------|----|----|
| `w_d` (object-to-goal distance) | $`-10.0`$ | §B.1, Table 7 |
| `w_r` (orientation alignment) | $`1.0`$ | §B.1, Table 7 |
| `b_success` (reach goal bonus) | $`250`$ | §B.1, Table 7 |
| `p_fall` (fall penalty) | $`-100`$ | §B.1, Table 7 |
| `w_lat` (lateral joint position penalty) | $`-0.016`$ | §B.1, Table 7 |
| `w_rad` (encompassing joint position penalty) | $`-0.004`$ | §B.1, Table 7 |
| goal tolerance | `0.1 radian` | §B.1 |

**PPO (RSL-RL)**

| 이름 | 값 | 출처 |
|------|----|----|
| `num_steps_per_env` | `16` | §B.1, Table 6 |
| `empirical_normalization` | `True` | §B.1, Table 6 |
| hidden layer dimensions | $`[512,512,256,128]`$ | §B.1, Table 6 |
| activation | `ELU` | §B.1, Table 6 |
| initial action noise std | $`1.0`$ | §B.1, Table 6 |
| learning rate | $`5.0\times 10^{-4}`$ (adaptive) | §B.1, Table 6 |
| clip parameter | $`0.2`$ | §B.1, Table 6 |
| entropy coefficient | $`0.005`$ | §B.1, Table 6 |
| num. learning epochs | $`5`$ | §B.1, Table 6 |
| num. mini-batches | $`4`$ | §B.1, Table 6 |
| value loss coefficient | $`1.0`$ (clipped value loss `True`) | §B.1, Table 6 |
| discount factor $`\gamma`$ | $`0.99`$ | §B.1, Table 6 |
| GAE $`\lambda`$ | $`0.95`$ | §B.1, Table 6 |
| desired KL divergence | $`0.016`$ | §B.1, Table 6 |
| max. gradient norm | $`1.0`$ | §B.1, Table 6 |

**액션 공간 구성**

| 이름 | 값 | 출처 |
|------|----|----|
| driving planes | `5` (손가락당 1, 4 손가락 손은 약지 위치 1 개 추가) | §3.3, §4.1, §B |
| driving vectors per plane | `2` (어블레이션 1/2/3/4 중 채택) | §3.3, §4.2 Table 4 |
| driving vector 극각 위치 | $`\phi=60^{\circ}`$, $`\phi=120^{\circ}`$ | §B |
| 반경 변위 구간 | $`[-2,2]`$ | §B |
| 액션 차원 | `15` = $`5+2\times 5`$ | §3.3 |
| 손가락당 관측점 | `2` (중간점 + 손끝; 후보 7 점 중 선택) | §B, §E Table 9 |
| 실환경 제어 주파수 | `20 Hz` (LEAP 시리얼 대역폭 제약) | §D |
| CIK 실행 속도 | 최대 `150 Hz` | §3.4, §A |

**도메인 랜덤화 (Table 8)**

| 파라미터 | 범위 | 출처 |
|------|----|----|
| Object scale | $`[0.9,1.1]\times`$ nominal | §B.1, Table 8 |
| Object mass | $`[0.8,1.2]\times`$ nominal | §B.1, Table 8 |
| Object static friction | $`[0.2,0.3]`$ | §B.1, Table 8 |
| Object dynamic friction | $`[0.15,0.25]`$ | §B.1, Table 8 |
| Robot mass | $`[0.9,1.1]\times`$ nominal | §B.1, Table 8 |
| Robot static / dynamic friction | $`[0.75,1.0]`$ | §B.1, Table 8 |
| Joint friction | $`[0.9,1.1]\times`$ nominal | §B.1, Table 8 |
| Joint armature | $`[1.00,1.05]\times`$ nominal | §B.1, Table 8 |
| Joint effort limits | $`[0.9,1.1]\times`$ nominal | §B.1, Table 8 |
| Joint stiffness | $`[0.75,1.25]\times`$ nominal | §B.1, Table 8 |
| Joint damping | $`[0.75,1.25]\times`$ nominal | §B.1, Table 8 |
| Hand base inclination | $`15^{\circ}\pm 5^{\circ}`$ | §B.1, Table 8 |
| Driving vector 각 | $`\pm 15^{\circ}`$ | §B.1, Table 8 |

실환경 배포용 모델은 위 범위를 넓히고 시뮬레이션 속도 제한 자체도 랜덤화합니다(§D.1). 시스템 식별으로 얻은 LEAP 유효 게인은 모터 단위 100 당 $`K_{p}\approx 0.0786~\text{Nm/rad}`$, $`K_{d}\approx 0.0014~\text{Nm/(rad/s)}`$ 이며, 감쇠는 관측 동역학에 거의 영향이 없는 **거의 무감쇠 시스템**으로 식별되었습니다(§D).

**학습 예산**

| 이름 | 값 | 출처 |
|------|----|----|
| 밑바닥 학습 | 약 `4,500` iterations | §4.2 |
| 미지 손 미세조정 | `500` iterations | §4.2, Table 3 |
| 하드웨어 | 단일 `NVIDIA A5000` GPU | §4.2, §B.1 |
| 시뮬레이터 | `Isaac Sim 4.5.0` + PhysX, Isaac Lab Cube Reposing 개조판 | §B.1 |

---

## 🎯 평가 메트릭

- **지표 1** — `Average Consecutive Reorientations` · **임계값** — 첫 큐브 낙하 전까지의 연속 성공 재배향 횟수 평균, 시뮬레이션 최대 `10` · **비교 baseline** — 관절 위치·속도를 상태로 받아 관절 위치를 직접 예측하는 `Joint Control` 정책.
- **지표 2** — `Success Rate` · **임계값** — 개별 재배향 시도의 성공 비율(%). 목표 방향에 낙하 없이 도달하면 성공 · **비교 baseline** — 동일 `Joint Control`.
- **평가 프로토콜 (시뮬레이션)** — 에피소드당 목표 방향 `10` 개를 순차 달성. 큐브 낙하 시 환경 리셋 후 남은 시도 계속. 목표당 제한 시간 `30 초`. 전 결과 **1000 개 병렬 환경**에서 평가.
- **평가 프로토콜 (실환경)** — 큐브가 떨어질 때까지 정책 연속 실행. 손당 `10` 회 독립 시행, 시행별 낙하 전 연속 성공 횟수와 그 평균을 보고.
- **전이 설정 4 종** — `Single-Hand`(대상 손만) / `Joint Control`(베이스라인) / `Multi-Hand`(네 손 전체) / `Zero-shot`(대상 손 제외 학습, 미세조정 없음).
- **참조 수치 (본 논문 달성치)** — Single-Hand 성공률 99.1~99.8, Zero-shot 85.7~98.1, `+500 Iter` 미세조정 후 95.8~96.3. 실환경 최고 평균 연속 재배향 `2.0`(LEAP) / `2.1`(Allegro), 관절 제어 베이스라인 `0.6`(LEAP).
- **학습 시간 측정 규약** — 어블레이션의 `Training Time (h)` 은 "최대 평균 연속 재배향(10)의 90 % 도달에 필요한 반복 수" 기준.

---

## ✨ 변경 의도 (intent)

기존 다지 조작 정책은 액션을 해당 손의 관절 공간에 정의하므로 손이 바뀌면 액션의 의미 자체가 사라지고 정책을 처음부터 다시 학습해야 합니다. CrossFormer / Universal Actions 계열은 별도 액션 헤드나 잠재 액션, 정규화된 관절 표현으로 이 문제를 우회하지만 여전히 손 형상의 이질성(손가락 수, 관절 축 배치)을 표현 수준에서 흡수하지 못합니다. 본 설계의 의도는 액션의 정의 자체를 손에서 **떼어 내어**, 손바닥 앞에 URDF 로부터 자동 구성되는 정규 구를 놓고 "구를 어떻게 변형할지"만 정책이 지시하게 만드는 것입니다. 그 결과 액션 차원은 손 DOF 와 무관하게 15 로 고정되고, 손별 차이는 학습되지 않는 결정론적 디코더(CIK) 안으로 격리됩니다. 이 격리 덕분에 하나의 정책이 여러 손을 동시에 다루고(Multi-Hand), 학습에서 본 적 없는 손으로 zero-shot 전이하며, 새 손에는 밑바닥 학습의 약 1/9 예산(500 iteration)으로 적응할 수 있습니다. 대가는 두 가지입니다 — 통일이 기구학 수준에 한정되어 저수준 PD·액추에이터 동역학 차이는 여전히 DR 로 메워야 하고, 다중 손 학습은 "모든 손에서 안전한 움직임"만 남기므로 단일 손 최고 성능을 일부 포기합니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 정책 family 대응은 약합니다. UHAS 의 기여는 policy backbone 이 아니라 **액션 공간 정의 + 결정론적 액션 디코더**이므로, `pi0` / `pi05` / `act` / `diffusion` 중 어느 family 를 고르든 그 위에 얹히는 계층입니다. 매핑 후보는 정책 코드가 아니라 액션 후처리 경로(`processor` / `transforms` 계열)에 15 차원 구 변형 → 관절 목표 변환을 삽입하는 형태이며, 학습 측(RSL-RL PPO + Isaac Lab 환경)은 `lerobot` 범위 밖입니다. 실제 매핑 가능 여부는 `/implement-design` 의 판단에 맡깁니다.

---

## 🚧 미해결 / 잠정

- **구 표면 균일 샘플점 개수** — `(원문에 명시 없음 — 가정으로 메움)`. 대응 밀도가 CIK 정확도에 직결되지만 수치가 제시되지 않았습니다.
- **lateral lookup table 스윕 간격** — "uniform steps" 로만 기술되고 간격·표 크기 `(원문에 명시 없음 — 가정으로 메움)`.
- **보간 커널의 구체 형태** — $`\Delta\theta`$ 는 "이웃 driving plane 값의 보간", $`\Delta r`$ 은 "$`(\theta,\phi)`$ 공간의 2 차원 보간"으로만 기술되고 커널 종류(선형/RBF 등) `(원문에 명시 없음 — 가정으로 메움)`.
- **관절 분류의 "부분 굴곡" 각도** — 회전축이 손끝을 향하는 관절의 재스윕 시 나머지 관절을 얼마나 굽히는지 `(원문에 명시 없음 — 가정으로 메움)`.
- **전체 관측 벡터 차원** — 표준 관측군(goal rotation, object pose, 속도, quaternion 차, 이전 액션)과 표면점 관측을 합친 최종 차원이 명시되지 않아 `(원문에 명시 없음 — 가정으로 메움)`.
- **DR 대상 각도의 표기 불일치** — §B.1 본문은 "driving vector azimuthal angle $`\theta`$", Table 8 은 "Driving vector azimuthal angle ($`\phi`$)", §E 는 "driving vector polar angle $`\phi`$" 로 각각 다르게 적습니다. §3.2 정의($`\theta`$ = 방위각, $`\phi`$ = 극각) 기준으로 어느 각을 랜덤화했는지 원문만으로 확정 불가.
- **CIK 의 미분 불가성과 모방 학습 경로** — 논문 검증은 전부 RL 이므로 flow-matching / 액션 청크 예측 정책에 얹었을 때의 손실 정의·성능은 미검증 영역입니다. Design 상으로는 손실을 구 변형 공간에 정의하는 것만이 근거 있는 선택입니다.
- **에피소드 길이 / 리셋 규약의 세부** — 목표당 30 초 제한과 낙하 시 리셋은 명시되나, 스텝 단위 최대 에피소드 길이 `(원문에 명시 없음 — 가정으로 메움)`.
