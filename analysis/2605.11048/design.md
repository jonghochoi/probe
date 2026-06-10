# Design — ForceFlow: Learning to Feel and Act via Contact-Driven Flow Matching

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | ForceFlow: Learning to Feel and Act via Contact-Driven Flow Matching |
| 링크 | [arXiv:2605.11048](https://arxiv.org/abs/2605.11048) |
| 분석 문서 | [`analysis/2605.11048/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-05-26 |

---

## 🧮 데이터 계약

관측 $`\mathcal{O}_{t}=\{I_{\text{arm},t},I_{\text{fix},t},\mathbf{q}_{t},\mathbf{F}_{t}^{\text{hist}}\}`$ 와 hybrid action $`\mathbf{a}_{t}=[\Delta\mathbf{p}_{t},\hat{\mathbf{f}}_{t+1}]`$ 의 계약입니다.

- **입력 — RGB (arm view)**: shape `(B, T_obs, 3, 240, 320)`, dtype `float32`, normalization mean=0.5/std=0.5 → `[-1, 1]`
- **입력 — RGB (fix/global view)**: shape `(B, T_obs, 3, 240, 320)`, dtype `float32`, normalization mean=0.5/std=0.5 → `[-1, 1]`
- **입력 — proprioception**: shape `(B, T_obs, 7)`, dtype `float32`, MinMax normalization (6D EE pose + 1D gripper)
- **입력 — force history**: shape `(B, H_force, 6)`, dtype `float32`, MinMax normalization (3D force + 3D torque, `H_force = 10`)
- **입력 — flow time step**: scalar $`k \in [0, 1]`$, dtype `float32`, Fourier embedding (scale 0.2, untrainable)
- **출력 — hybrid action chunk**: shape `(B, T_action, 13)`, dtype `float32`, MinMax denormalize (6D delta pose + 1D gripper + 6D next-force, `T_action = 64`)
- **실행 시 controller 전송**: action chunk 의 앞 7D $`[\Delta p; \text{gripper}]`$ 만 robot controller 로. 뒤 6D `f_hat` 은 학습 신호 전용으로 *송신하지 않음*
- **V2F handover 인터페이스 — VLM 입력**: `(I_fix, language_instruction)` → 픽셀 좌표 `(u_hat, v_hat)` (회귀 출력, dtype `float32`)
- **V2F handover 인터페이스 — deprojection**: `(u_hat, v_hat, depth_map, camera_intrinsics, camera_extrinsics)` → robot base frame 의 3D waypoint $`p_{\text{approach}} \in \mathbb{R}^3`$
- **T_obs (observation horizon)** = 2 (Table 6), **T_action (action horizon)** = 64

---

## 🧰 모듈 인터페이스

```python
def vlm_pointing(I_fix: Tensor, instruction: str) -> Tuple[float, float]:
    """글로벌 뷰 + 자연어 → target keypoint 픽셀 (u_hat, v_hat). VQA fine-tune VLM."""

def v2f_deproject(uv: Tuple[float, float], depth: Tensor, K: Tensor, T_cam2base: Tensor) -> Tensor:
    """픽셀 + depth + intrinsics + extrinsics → robot base frame 3D approach waypoint."""

def v2f_trigger(ee_pose: Tensor, p_approach: Tensor, eps: float) -> bool:
    """positional 도달 판정 (strict). True 시 motion planner → ForceFlow 인계."""

def force_encoder(F_hist: Tensor) -> Tensor:
    """(B, H_force, 6) → (B, 128). 2-layer MLP."""

def lowdim_encoder(q: Tensor) -> Tensor:
    """(B, T_obs, 7) → (B, T_obs, 64) → flatten 후 (B, 64*T_obs). 2-layer MLP, hidden 64→64."""

def visual_encoder(I_arm: Tensor, I_fix: Tensor) -> Tensor:
    """듀얼 뷰 ResNet-18 → spatial feature 시퀀스 c_seq ∈ (B, S_seq, D_seq=512). pooling 없음."""

def aggregate_vec(F_emb: Tensor, q_emb: Tensor) -> Tensor:
    """force-centric 글로벌 벡터 c_vec ∈ (B, D_vec=256). 64*T_obs + 128 → 256."""

def dit_block(x, k_emb, c_vec, c_seq) -> Tensor:
    """1D DiT block: AdaLN(c_vec) modulates LN statistics every layer + cross-attn over c_seq.
       SiLU activation. dim=384, heads=6."""

def velocity_field(a_k: Tensor, k: float, c_vec: Tensor, c_seq: Tensor) -> Tensor:
    """v_θ(a_k, k, c_vec, c_seq). DiT-1D depth 12 → MLP head → (B, T_action, 13)."""

def flow_matching_loss(v_pred: Tensor, u_target: Tensor) -> Tensor:
    """MSE(v_pred, a1 - a0). target drift는 상수 (linear path)."""

def ode_sample(c_vec: Tensor, c_seq: Tensor, solver: str = "deterministic") -> Tensor:
    """a1 ~ N(0, I) 에서 출발해 dk: 1→0 으로 ODE 적분. 결과 a0 = [Δp; gripper; f_hat]."""

def controller_dispatch(a0: Tensor) -> Tensor:
    """a0 의 앞 7D만 robot controller. 6D f_hat은 *송신 금지*, 학습 평가용 보존."""
```

- `vlm_pointing` 는 task 별 VQA 데이터 (수동 annotation `(u_gt, v_gt)`) 로 fine-tune 됨. base VLM 모델명은 **(원문에 명시 없음 — 가정으로 메움)**. 본 논문은 별도로 Embodied-R1 (Yuan et al. 2025) 를 OOD spatial 평가의 high-level planner 로 사용했다고 명시.
- `aggregate_vec` 의 합산 구성은 `(64 × H_obs) + 128 = 256` (Table 6 의 "Total Vector Dim 256 = 64×H_o + 128").
- `dit_block` 의 *AdaLN 위치* 는 "every network layer" 라고만 명시. 정확히는 `scale/shift` 두 set 만인지, `scale/shift/gate` 세 set 인지의 표준 DiT 변형 여부는 **(원문에 명시 없음 — 가정으로 메움; DiT 원형의 scale/shift/gate 3-set 으로 가정 가능)**.
- `velocity_field` 의 head 는 MLP (Table 6 "Head Type: MLP").
- `flow_matching_loss` 외 보조 loss term 은 *없음*. joint prediction 의 force MSE 는 별도 head 없이 hybrid action 의 force 차원에 그대로 포함되어 `L_FM` 에 흡수됩니다.
- 옵티마이저 / 스케줄 / hardware 는 §📊 항목에 정리.

---

## ⛓️ 불변식·가정

- (불변식 1) **Hybrid action 의 force 차원은 controller 로 전송되지 않는다.** 실행 시 `controller_dispatch` 는 앞 7D 만 송신합니다 — 위반 시 모델이 force-control 루프에 직접 개입해 안정성 가정이 무너집니다.
- (불변식 2) **V2F handover trigger 는 positional criterion 만으로 발화.** contact 확률·force threshold 같은 다른 신호는 사용하지 않으며, trigger 가 한 번 발화하면 episode 내 *되돌아가지 않음*.
- (불변식 3) **Linear probability path.** 보간은 $`\mathbf{a}_{t}^{k}=(1-k)\mathbf{a}_{t}^{0}+k\mathbf{a}_{t}^{1}`$, target drift 는 상수 $`\mathbf{u}_{t}^{k}=\mathbf{a}_{t}^{1}-\mathbf{a}_{t}^{0}`$. 비선형 path 로의 일반화는 가정에 포함되지 않음.
- (불변식 4) **Force history window 길이 $`H=10`$** 는 SR 의 결정 요인. 1-step 으로 줄이면 SR 이 약 85% → 55% 로 무너지므로 (Table 5) $`H_{\text{force}} \ge 10`$ 이 사실상 hard constraint.
- (가정 1) **Action / state normalization 은 MinMax**, 이미지 normalization 은 `[-1, 1]` (mean=std=0.5) (Table 6). 정규화 통계의 데이터셋 split 출처는 원문에 명시되지 않아 *train split 전체의 per-dim min/max* 로 가정.
- (가정 2) **ODE solver 는 deterministic numerical solver** 만 명시. step 수 (`Sampling Steps`) 는 "Variable, inference-time adjustable" 로 명시되어 hyperparameter 로 노출.
- (가정 3) **V2F deprojection 의 camera calibration 정확도** 는 episode 내내 유효하다고 가정. 카메라 흔들림 / re-calibration drift 는 본 framework 범위 밖.
- (가정 4) **Force / torque sensor 는 6D, 30 Hz 수집과 동기**. 본 framework 는 high-fidelity F/T 가정에 의존 (저자 명시 한계).

---

## 📊 하이퍼파라미터·손실

손실:

$$\mathcal{L}_{\text{FM}}(\theta)=\mathbb{E}_{k,\mathbf{a}_{t}^{0},\mathbf{a}_{t}^{1}}\left\|v_{\theta}(\mathbf{a}_{t}^{k},k,c_{\text{vec}},c_{\text{seq}})-\mathbf{u}_{t}^{k}\right\|^{2}$$

joint prediction 의 force-MSE 는 별도 weight 없이 hybrid action 13D 의 MSE 에 *자연 포함* 됩니다 (별도 $`\lambda`$ 없음).

| 이름 | 값 | 출처 |
|------|----|----|
| `T_obs` (observation horizon $`H_{o}`$) | 2 | Table 6 |
| `T_action` (action horizon $`H_{a}`$) | 64 | Table 6 |
| `H_force` (force history length) | 10 | Table 6, §3.1 |
| `state_dim` | 7 (6D pose + 1D gripper) | Table 6 |
| `force_dim` | 6 (3D force + 3D torque) | Table 6 |
| `action_dim` | 13 (6D pose + gripper + 6D force) | Table 6 |
| Image resolution | $`320\times 240`$ | Table 6 |
| Visual backbone | ResNet-18 (pretrained, dual view) | Table 6 |
| Image embedding | $`2\times 256`$ | Table 6 |
| Low-dim encoder | 2-layer MLP, hidden 64→64 | Table 6 |
| Force encoder | 2-layer MLP, $`(H_{\text{force}}\times 6)\to 128`$ | Table 6 |
| Total vector dim $`D_{\text{vec}}`$ | 256 ($`64\times H_{o} + 128`$) | Table 6 |
| Sequence embedding $`D_{\text{seq}}`$ | 512 (dual-view image embedding) | Table 6 |
| DiT model dim | 384 | Table 6 |
| Attention heads | 6 | Table 6 |
| Transformer depth | 12 | Table 6 |
| Head type | MLP | Table 6 |
| Cross-attention | Yes (visual-to-action) | Table 6 |
| AdaLN | Yes | Table 6 |
| Timestep embedding | Fourier (scale 0.2, untrainable) | Table 6 |
| Activation | SiLU (Swish) | Table 6 |
| Dropout | 0.0 | Table 6 |
| Diffusion algorithm | Flow Matching (continuous-time) | Table 6 |
| Sampling steps | Variable (inference-time adjustable) | Table 6 |
| Normalization (state/action) | MinMax | Table 6 |
| Image normalization | mean=0.5, std=0.5 → $`[-1,1]`$ | Table 6 |
| Optimizer | AdamW ($`\beta_{1}=0.9,\beta_{2}=0.999`$, weight decay 0.01) | §A.2 |
| LR schedule | cosine, start $`1\times 10^{-4}`$ | §A.2 |
| Batch size | 64 (grad accumulation 1, effective 64) | Table 6, §A.2 |
| Max steps | 100,000 | Table 6 |
| Precision | bf16-mixed | Table 6 |
| Gradient clip | $`\|\nabla\|=1.0`$ | §A.2 |
| Checkpoint interval | 5,000 steps | Table 6 |
| Demonstrations / task | 50–100 (30 Hz teleop) | §A.2 |
| Random seed | 0 | Table 6 |

V2F approach stage 의 VLM 학습 hyperparameter (LR, batch, epoch, base VLM) 는 **(원문에 명시 없음 — 가정으로 메움)**.

---

## 🎯 평가 메트릭

- **지표 — Success Rate (SR)** · **임계값** — 과제별 완료 기준 (insertion 성공, wiping 청결 등) 충족 시 1, 아니면 0. 20 trial 평균 (%) · **비교 baseline** — $`\pi_{0.5}`$ / ACT / Diffusion Policy / ForceVLA / ForceFlow (w/o Force). ForceFlow 평균 81.67% (Table 1).
- **지표 — Force Fidelity ($`\mathcal{J}_{\text{force}}`$, MAE Cost, 단위 N)** · 식:

$$\mathcal{J}_{\text{force}}=\frac{1}{N}\sum_{i=1}^{N}\left|\hat{F}_{\text{policy}}^{(i)}-F_{\text{expert}}\right|$$

- $`N=20`$ trial.
- Short-Horizon Contact tasks: $`\hat{F}=\max_{t}\|\mathbf{f}_{t}\|`$ (peak contact force).
- Continuous Contact tasks: $`\|\mathbf{f}_{t}\|>5\text{N}`$ 구간의 평균 effective force.
- 낮을수록 좋음. 비교 baseline: 위와 동일. ForceFlow 평균 8.23 N (Table 2).
- **지표 — Stability across trials** · 20 trial 의 max/avg contact force 표준편차 (Figure 5). 정량 임계값은 명시되지 않으며, *시각적으로* 진동·스파이크 부재로 판정.
- **지표 — Force prediction temporal alignment** · Figure 6 의 predicted (red) vs measured (blue) 곡선 시각 정렬. 정량 metric 은 명시되지 않음.
- **지표 — Physical OOD SR** (Table 3): unseen tool/object 로 10 trial. Press / Clean WB / Clean Vase.
- **지표 — Spatial OOD SR** (Table 4): train 과 disjoint 한 workspace. V2F 필수. Press / Plug / Clean WB.
- **Task suite (6)**: Stamping, Plug Insertion, Press Button, USB Insertion (short-horizon), Clean Whiteboard, Clean Vase (continuous).

---

## ✨ 변경 의도 (intent)

이 모델의 차별점은 multimodal fusion 을 일부러 비대칭으로 짠 것입니다. 기존 force-aware 정책 (ForceVLA, Reactive Diffusion Policy, TacDiffusion) 은 force/tactile 을 vision 과 *대칭으로* fuse 해 modal masking 에 노출됩니다. 반면 ForceFlow 는 force 를 AdaLN 으로 모든 DiT 레이어의 통계를 modulate 하는 *글로벌 정규화 신호* 로 격상시키고, vision 은 cross-attention 의 *선택적인 spatial 참조* 로 강등합니다. 여기에 motion 과 next-step force 의 joint prediction 을 hybrid action 으로 묶어 force–motion coupling 을 학습 목표에 직접 박았습니다. Task 수준에서는 V2F handover 로 *공간 일반화 (VLM)* 와 *접촉 일반화 (ForceFlow)* 의 책임을 갈라놓아 한 정책 안에서 서로의 학습을 망치는 *mutual degradation* 을 끊었습니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — `diffusion` family 와 가장 가깝습니다. ForceFlow 는 flow matching backbone + DiT 1D + AdaLN 글로벌 조건 + cross-attn visual 의 구조로, lerobot 의 Diffusion Policy / Pi0 family 의 *DiT-스타일 conditioning* 와 인접합니다. 다만 세 점이 base 와 직접 매핑되지 않는 부분이 있습니다. hybrid action 에 next-force 6D 가 포함됩니다. AdaLN 의 조건 벡터가 *force-centric* 으로 설계됩니다. cross-attn 의 sequence condition 이 *듀얼 뷰 시퀀스 보존* (pooling 없음) 입니다. 후보: `diffusion` 또는 (있다면) `pi0_fast` / flow-matching 기반 base. V2F 의 VLM pointing 단계는 별도 모듈로 lerobot 의 *policy* 범위 바깥 (planner) 에 둡니다.

---

## 🚧 미해결 / 잠정

- **VLM base 모델·fine-tune 레시피 미명시.** V2F pointing 의 base VLM 모델명·LR·epoch·VQA dataset 크기. (Embodied-R1 은 spatial OOD 평가에 별도로 쓰였음.)
- **AdaLN 의 표준 변형** (scale/shift 2-set 또는 scale/shift/gate 3-set). DiT 원형은 3-set; 본 논문은 미명시.
- **ODE solver step 수의 권장값.** "Variable, inference-time adjustable" 만 명시.
- **F/T sensor 모델명·sampling rate** 가 명시되지 않음. teleop 은 30 Hz 명시이나 force 채널 rate 는 미명시 (history 10-step 가정).
- **Cross-attention 의 query/key/value 구성** (action 토큰이 query, visual sequence 가 key/value 인 표준 패턴으로 추정되지만 원문에 명시는 없음).
- **Force prediction loss weight 분리 여부.** hybrid action 13D MSE 안에 force 6D 가 포함되는 구조라 별도 $`\lambda`$ 가 없는 것으로 보이나, *implicit weight = force dim ratio* (6/13) 인지에 대한 명시는 없음.
- **Image normalization 의 ImageNet mean/std 미사용 사유.** ResNet-18 pretrained 임에도 `[-1,1]` 정규화를 쓰는 점이 표준 ImageNet 통계와 다른 선택이지만 사유 미명시.
- **Stage 전환 (V2F trigger) 의 positional tolerance $`\epsilon`$** 가 수치로 제시되지 않음.
- **각 task 의 verifier (성공 판정 logic)** 가 §A.1 의 정성 설명을 넘는 정량 임계값으로 제시되지 않음.
