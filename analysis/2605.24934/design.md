# Design — HumanEgo: Zero-Shot Robot Learning from Minutes of Human Egocentric Videos

> PROBE design 산출물 (Layer 1, vendor-agnostic). 단일 한글 문서이며,
> 영문 1차 파일은 없습니다. `/analyze-paper` 가 `analysis/<id>/analysis.md` 와
> 함께 자동 생성합니다 — 알고리즘 명세를 base 좌표계 없이 추출합니다.
> base 매핑은 `/implement` 단계에서 이루어집니다. 형식·이모지·용어 규칙은
> `docs/STYLE.md` §6 / §4 를 정확히 따릅니다. 재실행 시 이 파일을
> 덮어씁니다.

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | HumanEgo: Zero-Shot Robot Learning from Minutes of Human Egocentric Videos |
| 링크 | [arXiv:2605.24934](https://arxiv.org/abs/2605.24934) |
| 분석 문서 | [`analysis/2605.24934/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-05-27 |

---

## 🧮 데이터 계약

학습·추론 시 정책이 입출력하는 텐서를 모달리티별로 한 줄씩 정의합니다. 시간 축은 의미 단위(`K` = `chunk_size`)로만 적습니다.

- **입력 — RGB 이미지**: shape `(B, 3, 240, 320)`, dtype `float32`, [0,1] 정규화. 추론 시에는 인페인팅 없이 원본 로봇 카메라 프레임을 그대로 씁니다(학습 단계에서만 LaMa 인페인팅 + 가상 그리퍼 렌더를 적용). 16×16 patch embedding으로 컨텍스트화.
- **입력 — ICT 토큰 시퀀스**: shape `(B, N_ent, 29)`, dtype `float32`. `N_ent`는 가변 — 최소 2(양손) + 태스크별 물체 수. 각 토큰 구성: `[τ(1) ‖ ^REF T_E(9) ‖ ^E T_LH(9) ‖ ^E T_RH(9) ‖ g(1)]`. SE(3) → 9-D 평탄화 = 정규화 translation(3) + 6-D rotation(6). 정규화 통계는 (원문에 명시 없음 — 데이터셋 전체 평균/표준편차로 가정).
- **입력 — Flow time t**: shape `(B,)`, dtype `float32`, `t ~ U(0,1)`.
- **입력 — Noise sample x₀**: shape `(B, K, D_a)`, dtype `float32`, `x₀ ~ N(0, I)`.
- **출력 — Velocity field v_θ**: shape `(B, K, D_a)`, dtype `float32`. 학습 시 타깃은 `x₁ - x₀`.
- **출력 — 양손 액션 청크 x₁**: shape `(B, K, D_a)` with `K=50`, `D_a = 2 × (3 + 6 + 1) = 20` (양손 × {3-D translation + 6-D rotation + 1-D binary grasp logit}).
- **출력 — 보조 헤드 (object motion)**: shape `(B, K, 9)` per manipulated object, 6-DoF 미래 궤적(translation 3 + rotation 6).
- **출력 — 보조 헤드 (2D trace)**: shape `(B, K, 3, 2)`, 정규화 image 좌표로 anchor keypoint 3개 × K 스텝.
- **출력 — 보조 헤드 (latent consistency)**: shape `(B, K, 29)`, ICT 손 토큰의 K-스텝 후 상태.
- **추론 후처리** — translation은 데이터셋 통계로 역정규화, 6-D rotation은 normalize-then-Gram–Schmidt로 SO(3)에 사영, grasp logit은 sigmoid → any-over-horizon 규칙(τ=0.6).

---

## 🧰 모듈 인터페이스

```python
def hand_track(frames, mps_keypoints, slam_pose):
    """Aria MPS 3D keypoint를 월드 좌표로 lift하고 Savitzky-Golay + EMA로 스무딩 후
    엄지·검지 가상 평행 그리퍼의 (T_ee, g) 추출."""
    # 반환: T_ee ∈ SE(3) per-frame, g ∈ [0,1] (deployment 시 binarize)

def object_track(frames, prompt, K_intrinsic, slam_pose):
    """Grounding DINO → SAM2 → CoTracker3 → 삼각측량으로 2D→3D contour keypoint,
    Orient-Anything V2로 회전 추정. 파지 구간은 kinematic latching으로 손에 묶음."""
    # 반환: T_obj ∈ SE(3) per-frame per-object

def build_ict(entities, ref_frame):
    """각 엔티티 k에 대해 ICT_k = [τ ‖ ^REF T_E ‖ ^E T_LH ‖ ^E T_RH ‖ g] (29-D) 구성.
    ref_frame은 (a) anchor 모드: 최초 파지 물체, (b) camera 모드: 카메라 좌표계."""
    # 반환: tokens shape (N_ent, 29)

def policy_forward(rgb, ict_tokens, x_t, t) -> velocity:
    """6-layer · 8-head · embed 384 transformer decoder.
    Self-attn: 액션 청크 토큰끼리. Cross-attn: (RGB patch + sinusoidal t-embed)
    와 (ICT 토큰을 384채널로 선형 사영한 시퀀스) 결합 컨텍스트.
    Region attention의 가우시안 spotlight w(u,v)로 image cross-attn을 가중."""
    # 반환: velocity ∈ (B, K, D_a)

def aux_heads(context, ict_tokens):
    """공유 컨텍스트 인코더에서 분기하는 3종 보조 헤드:
    object_motion (9-D × K), visual_foresight (3×2 × K, 얕은 deconv stack),
    temporal_consistency (29-D × K, masked MSE)."""

def fm_loss(velocity, x0, x1, weights=(5, 1, 10)):
    """L_FM = E_t [w_p ||Δp||² + w_r ||Δr||² + w_g ||Δg||²], Δ = v - (x1-x0).
    x_t = (1-t)x0 + t x1, t ~ U(0,1)."""

def euler_rollout(policy, ict_tokens, rgb, steps=20, K=50):
    """fixed-step Euler: x_{t+Δt} = x_t + v_θ(x_t, t, s_t) Δt, Δt = 1/20.
    한 forward pass에 K=50 스텝 양손 액션 청크 생성. position EMA(α=0.5),
    quaternion SLERP, trajectory-overlap blend(=12)로 후처리."""

def safety_cage(target_delta):
    """위치 ≤ 0.08 m/cycle, 회전 ≤ 0.02 rad/cycle 클램프."""
```

- 모듈 간 의존: `hand_track`, `object_track` → `build_ict` → `policy_forward` ↔ `aux_heads`. 학습 단계에서 `policy_forward`는 `fm_loss`로, `aux_heads`는 자체 MSE/masked MSE로 갱신.
- 외부 호출: 학습 라벨은 모두 perception pipeline에서 자동 추출 — 추가 라벨링 불필요.
- 컨트롤러 — 10 Hz 재계획, step stride 2(실효 5 Hz), look-ahead 25 스텝, grasp는 any-over-horizon (τ=0.6) + optional grasp-latch.

---

## ⛓️ 불변식·가정

- **(시점/임바디먼트 불변)** — ICT의 entity-local 좌표는 카메라·그리퍼 외형·배경에 불변이어야 합니다. 학습-시 사람 손과 추론-시 로봇 그리퍼 사이에 visual 갭이 있더라도 ICT의 numerical 분포가 같을 때 정책이 zero-shot으로 동작합니다.
- **(스테레오 깊이 가용)** — 손 keypoint의 metric depth가 ±1 cm 이내로 잡혀야 ICT의 ^REF·^E 변환이 의미를 가집니다. 단안 RGB만 쓰면 5~11 cm 깊이 오프셋이 ICT 기준 프레임에 쌓여 정책 학습이 무너집니다(부록 E.1).
- **(파지 구간 강체 가정)** — kinematic latching `T_obj^t = T_hand^t · (T_hand^{t₀})⁻¹ · T_obj^{t₀}` 은 파지 시점 `t₀` 이후 물체와 손이 강체로 결합된다고 봅니다. in-hand re-grasp나 sliding이 일어나면 무효입니다.
- **(보조 라벨 노이즈 < 정책 학습 신호)** — object motion · 2D trace · latent consistency 헤드는 perception pipeline의 자동 라벨에 기대므로, 라벨 노이즈가 supervision 신호보다 작아야 보조 손실이 정책을 무너뜨리지 않습니다.
- **(grasp 이진화 임계)** — deployment 시 grasp 스칼라 `g` 는 사람 엄지-검지 거리 정규화 값이고, 로봇 그리퍼의 닫힘/열림 임계가 학습 시 사람 핀치 임계와 맞물려야 합니다(원문은 binarize at deployment만 명시, 임계 값은 명시 없음 — 가정으로 메움).
- **(액션 청크 내 연속성)** — `K=50` 스텝 청크가 한 forward pass에서 만들어지고 look-ahead 25 step으로 latency를 가린다 — 청크 내부 인접 timestep 차분이 controller 추종 범위 안에 든다는 운동학적 가정에 기댑니다.

---

## 📊 하이퍼파라미터·손실

손실 식 (verbatim):

$$\mathcal{L}=\mathcal{L}_{\text{FM}}+\lambda_{\text{OM}}\,\mathcal{L}_{\text{OM}}+\lambda_{\text{2D}}\,\mathcal{L}_{\text{2D}}+\lambda_{\text{LC}}\,\mathcal{L}_{\text{LC}}$$

$$\mathcal{L}_{\text{FM}}=\mathbb{E}_{t,\,\mathbf{x}_{0},\,\mathbf{x}_{1}}\Big[w_{p}\left\|\Delta\mathbf{p}\right\|^{2}+w_{r}\left\|\Delta\mathbf{r}\right\|^{2}+w_{g}\left\|\Delta g\right\|^{2}\Big]$$

| 이름 | 값 | 출처 |
|------|----|------|
| 위치 손실 가중 `w_p` | `5` | §3.4, 부록 C.1, Table 1 |
| 회전 손실 가중 `w_r` | `1` | §3.4, 부록 C.1, Table 1 |
| Grasp 손실 가중 `w_g` | `10` | §3.4, 부록 C.1, Table 1 |
| Object-dynamics 헤드 가중 (pos/rot) | `0.5 w_p` / `0.5 w_r` | 부록 C.1, Table 1 |
| Visual-foresight 헤드 가중 `w_f` | `20` | 부록 C.1, Table 1 |
| Temporal-consistency 헤드 가중 `w_c` | `[0.1, 1.0]` | 부록 C.1, Table 1 |
| `λ_OM`, `λ_2D`, `λ_LC` | (원문 식 (3)에서 기호로만 정의; 구체 값은 위 헤드별 가중과 동일계열로 보고) | §3.4 식 (3), 부록 C.1 |
| 프레디션 호라이즌 `K` | `50` | 부록 F, Table 1 |
| ICT 토큰 차원 | `29` | §3.3 식 (1) |
| Transformer layers / heads / embed | `6` / `8` / `384` | 부록 C.1, Table 1 |
| Dropout | `0.05` | 부록 C.1, Table 1 |
| RGB patch / 입력 해상도 | `16 × 16` / `240 × 320` | 부록 C.1, Table 1 |
| Optimizer | AdamW | 부록 C.1, Table 1 |
| 베이스 학습률 | `1 × 10⁻⁴` | 부록 C.1, Table 1 |
| Warmup steps / min-LR ratio | `200` / `0.05` | 부록 C.1, Table 1 |
| Batch size / Epochs | `32` / `400` | 부록 C.1, Table 1 |
| Gradient-norm clip / EMA decay | `1.0` / `0.999` | 부록 C.1, Table 1 |
| 액션 타깃 노이즈 `σ_pos` / `σ_rot` | `1 mm` / `0.5°` | 부록 C.1, Table 1 |
| Sub-step 보간 확률 | `0.5` | 부록 C.1, Table 1 |
| ODE 적분 스텝 수 | `20` (Euler) | §3.4, §D.2 |
| Region attention spotlight | `w(u,v) = exp(-((u-u₀)² + (v-v₀)²) / (2σ²))`, `σ` learnable | 부록 C.1 식 (8) |
| State-noise injection | per-channel `Σ_s` on (pos, 6-D rot, grasp) | 부록 C.1 |
| Controller re-plan rate | `10 Hz` | §D.2 |
| Step stride / look-ahead | `2` (실효 5 Hz) / `25` | §D.2 |
| Grasp threshold | `0.6` (any-over-horizon, optional latch) | §D.2 |
| Position smoothing α / quaternion blend | `0.5` (EMA) / SLERP, overlap blend `12` | §D.2 |
| Safety cage (per-cycle) | 위치 `≤ 0.08 m` / 회전 `≤ 0.02 rad` | §D.2 |
| 데이터 — 태스크당 사람 영상 시간 | `30 min` (스케일 실험: `15 min`, `7~8 min`도 보고) | §3.1, §4.2 |
| 데이터 — Aria RGB / SLAM | `30 fps · 2 MP` / `2 cam · 30 fps · VGA` | 부록 F, Table 1 |

---

## 🎯 평가 메트릭

- **지표** — 실세계 성공률(%) · **임계값** — 4 태스크 평균 ≥ 90 % (논문 보고 92.5 %) · **비교 baseline** — EgoZero / Point Policy / ZeroMimic / Track2Act / SPOT / ACT (matched-time teleoperation)
- **지표** — 데이터 시간 vs 성공률 곡선 · **임계값** — `8 min` 사람 영상이 `30 min` ACT 텔레오퍼레이션을 동률/상회 · **비교 baseline** — Serve Bread on ACT (30 min) = 52.5 %
- **지표** — OOD 조건별 성공률 · **임계값** — 9 조건 평균 85~91.25 % 유지 · **비교 baseline** — 학습 분포 내 성공률(92.5 %) 대비 대규모 하락 없음
- **지표** — Input ablation (Water Flowers) · **임계값** — ICT 추가로 7.5 % → 85 % 이상 (Δ ≥ +75 pp) · **비교 baseline** — 사람 RGB only
- **지표** — Auxiliary objective ablation (15 min 데이터) · **임계값** — 세 보조 손실 결합 시 `+25 pp` · **비교 baseline** — flow matching only
- **지표** — 손 트래커 비교 (Serve Bread) · **임계값** — Aria-MPS 95 % vs 단안 RGB ≤ 45 % · **비교 baseline** — WiLoR / HaMeR / MediaPipe
- **지표** — Reference frame ablation · **임계값** — 저데이터 anchor frame 우위, 대데이터 camera frame 동률/우위 · **비교 baseline** — anchor frame vs camera frame on same data budget
- **시행 횟수** — 태스크당 40회, 랜덤 초기 물체 위치(§4 기본).

---

## ✨ 변경 의도 (intent)

본 알고리즘은 *손 ∨ 물체*의 단일 표현(EgoZero의 point cloud, Point Policy의 sparse keypoint, ZeroMimic의 wrist trajectory, Track2Act의 2D track, SPOT의 SE(3) object pose)을 *손 ∧ 물체*의 *상호 관계*로 갈아엎습니다. 또 supervision sparsity 문제를 *세 공간(3D 물리·2D 시각·잠재)* 에서의 *forward dynamics 예측* 보조 손실로 메워, 분 단위 시연 한 편에서 다중 작업 신호를 뽑아냅니다. flow matching은 fast multi-modal 액션 생성의 *수단*이고, ICT(표현) + dense aux(supervision)가 데이터 효율의 *원인* — 이 점이 본 논문의 ablation으로 못 박힌 메시지입니다. 동시간 텔레오퍼레이션을 -41 %p 차이로 이긴 실측치는 "사람 1인칭 영상은 *값싼 대체재*가 아니라 *우월한 학습 소스*"라는 강한 클레임을 떠받칩니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 후보 base: `pi0` / `pi05` (flow matching action expert 패밀리)와 구조적으로 가장 가깝습니다. 다만 HumanEgo는 VLM 백본 없이 *경량 transformer decoder + RGB patch + ICT 토큰* 컨텍스트만으로 굴러가므로, π 패밀리에서 VLM 부분을 떼고 ICT 토큰을 새 입력 스트림으로 붙이는 *축소 변형* 매핑이 자연스럽습니다. 액션 청크 호라이즌 `K=50`, Euler 20-step 적분, dimension-wise 손실 가중은 그대로 가져다 씁니다. 양손 통합 액션이라 lerobot의 single-arm 가정과 차원만 맞추면 곧장 붙습니다. ACT 베이스라인이 본문에 함께 등장하지만 `act` 패밀리는 *비교 대상*이지 매핑 후보가 아닙니다.

---

## 🚧 미해결 / 잠정

- ICT의 SE(3) → 9-D 평탄화에서 translation 정규화 통계 출처 — (원문에 명시 없음 — 데이터셋 전체 mean/std로 가정).
- `λ_OM`, `λ_2D`, `λ_LC` 의 절대값 — 본문 식 (3)은 기호로만 정의하고, 부록 C.1은 헤드별 *내부* 가중치(`0.5 w_p`, `w_f=20`, `w_c∈[0.1, 1.0]`)만 줍니다. 두 가중치 계열이 동일 스케일인지 별개 곱셈 인자인지 명시 없음 — 가정으로 메움.
- Grasp 이진화 임계값(사람 핀치 거리 정규화 결과를 deployment에서 0/1로 자르는 cut-off) — 부록 B.3은 정규화 절차만 적고 정확한 임계는 원문에 명시 없음 — 가정으로 메움.
- 보조 헤드 visual_foresight의 "anchor keypoint 3개" 선택 규칙 — 부록 C.1은 `K×3×2` shape만 명시하고 3개 선정 휴리스틱은 비공개 — 가정으로 메움.
- Latent consistency 헤드의 "K steps ahead" 마스킹 패턴 — masked MSE라고만 표기, 마스크 정의는 원문에 명시 없음 — 가정으로 메움.
- 본 논문의 *bimanual* 통합 액션 차원이 PROBE의 body/hand anatomical 분리(D1)와 어떻게 정렬되는지 — 본 Design은 양손 통합 단일 transformer로 그대로 두고, anatomical 분리는 별도 Design 변환 단계에서 정합니다.
- 손 추적 백엔드의 *대체 가능성* — 본 Design은 Aria MPS를 전제로 썼고, 다른 멀티-카메라 rig + MANO 추정기 조합이 동등한 metric 정확도를 줄지는 (원문에 명시 없음 — 외부 검증 필요).
