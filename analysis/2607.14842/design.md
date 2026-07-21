# Design — KineFuse: Kinematic-Aware Haptic Fusion for In-Hand Occluded-Object Pose Tracking

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | KineFuse: Kinematic-Aware Haptic Fusion for In-Hand Occluded-Object Pose Tracking |
| 링크 | [arXiv:2607.14842](https://arxiv.org/abs/2607.14842) |
| 분석 문서 | [`analysis/2607.14842/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-07-21 |

---

## 🧮 데이터 계약

시간 축은 절대 스텝이 아니라 haptic 히스토리 길이 $`\tau`$ 로 기록합니다. `F=4`(손가락 수), `J=16`(관절 수), `L=400`(시각 토큰), `D=512`(토큰 차원)는 본 논문 셋업이며 손 하드웨어에 종속됩니다.

- **입력 — RGB-D 관측** `I_t`: 현재 pose 가설 $`\tilde{T}_{t}`$ 로 렌더한 crop + 관측 crop. shape `(B, ., H_c, W_c)`, render-and-compare 쌍. FoundationPose crop 정규화 가정을 그대로 승계.
- **입력 — haptic** `h_t`: shape $`(B, J{=}16, \tau{=}4, C)`$, per-joint feature `C`. 관절 히스토리 flatten 시 per-joint `(B, J, 28)` → $`C\cdot\tau = 28`$ (본 논문 `C=7`). proprioception(위치 $`q`$ · 속도 $`\dot{q}`$)은 전 관절, binary contact 는 손끝, 3축 F/T 는 $`\mathcal{S}_{\mathrm{FT}}\subset\{1,\dots,J\}`$ 의 4개 관절 + availability flag. force 채널은 학습 시 domain randomization(scaling·offset·noise·dropout) 정규화 가정.
- **입력 — pose 가설** $`\tilde{T}_{t}\in SE(3)`$: tracking 시 $`\tilde{T}_{t}=\hat{T}_{t-1}`$(이전 프레임 추정). 학습 시 GT $`T_{t}^{*}`$ 에 egocentric noise(rot `[1°,10°]`, trans `[0.002,0.01]` m)를 주입해 생성.
- **출력 — translation delta** $`\Delta\hat{\mathbf{t}}_{t}\in\mathbb{R}^{3}`$: egocentric frame, `tanh`-bounded 후 per-axis normalizer `n_t`(`[0.01,0.01,0.01]` m) 곱.
- **출력 — rotation delta** $`\Delta\hat{\mathbf{r}}_{t}\in\mathbb{R}^{6}`$: 6D 회전 표현, egocentric frame.
- **출력 — refined pose** $`\hat{T}_{t}=\Delta\hat{T}_{t}\circ\tilde{T}_{t}`$. 추론 시 2회 연속 refinement.

---

## 🧰 모듈 인터페이스

```python
def joint_tokenizer(h_t) -> "z0":            # (B, J, τ, C) -> (B, J, 512)
    """관절 히스토리 flatten(28) -> 2-layer MLP+LN(GELU) -> +finger_id emb +within-finger pos emb."""

def intra_finger_attn(z0, M_finger) -> "z1": # (B, J, 512) -> (B, J, 512)
    """finger-restricted mask 로 2 self-attn layer. 같은 손가락 4관절 안에서만 attend(원위 F/T -> 근위 전파)."""

def finger_pool(z1) -> "f_t":                # (B, J=16, 512) -> (B, F=4, 512)
    """손가락별 learnable query 가 그 손가락 관절 토큰을 cross-attention 요약(16->4)."""

def inter_finger_graph_attn(f_t, B_bias) -> "h_t":  # (B, 4, 512), bias (4,4,H) -> (B, 4, 512)
    """URDF spatial bias(hop/opposition/adjacency -> MLP -> per-head bias)를 더한 2 Graphormer layer."""

def visuo_haptic_fuse(v_t, h_t) -> "(Δt̂, Δr̂)":     # concat -> 별도 trans/rot transformer -> mean-pool -> proj
    """z=[v_t; h_t] (L+4, 512). TransHead/RotHead 각각 single-layer encoder, mean-pool 후 선형 투영."""
```

- `joint_tokenizer` — 외부 호출: finger-identity·within-finger position 임베딩 테이블(learnable). loss 무관, 순수 인코딩.
- `intra_finger_attn` — 외부 호출: `M_finger`(block-diagonal 마스크, 손 구조로 고정). gradient 는 tokenizer 로 역전파.
- `finger_pool` — 외부 호출: 손가락당 1개 learnable query. `F` 개 요약 토큰 생성.
- `inter_finger_graph_attn` — 외부 호출: `B_bias` 는 URDF 기하 → MLP 로 생성되는 학습 파라미터. `S_FT`·손 토폴로지에 종속.
- `visuo_haptic_fuse` — 외부 호출: 시각 backbone(frozen FoundationPose refiner)의 `v_t`. 손실은 $`\mathcal{L}_{\mathrm{pose}}`$(MSE) $`+\,\lambda_{\mathrm{ADD}}\mathcal{L}_{\mathrm{ADD}}+\lambda_{\mathrm{attr}}\mathcal{L}_{\mathrm{attr}}+\lambda_{\mathrm{pen}}\mathcal{L}_{\mathrm{pen}}`$. gated dual-head 는 haptic-only 붕괴로 미채택(direct fusion).

---

## ⛓️ 불변식·가정

- (가정 1) `M_finger` 는 block-diagonal — 관절 `j` 는 자기 손가락 4관절에만 attend. 이 마스크가 깨지면(cross-finger 누출) 원위→근위 sparse-force 전파 구조가 무효화되고 flat fusion 으로 퇴화.
- (가정 2) haptic 토큰 수 `F(=4)` ≪ 시각 토큰 수 `L(=400)`. 융합 sequence 에서 haptic 토큰 norm 이 vision 을 지배(norm dominance)하지 않아야 vision 이 억압되지 않음 — joint-level(16-token) 표현이 실패한 원인.
- (가정 3) URDF spatial bias 는 손 형상에 대해 시불변(static). hop distance·opposition·adjacency 가 에피소드 내 고정이라는 rigid-hand 가정 위에서만 per-head bias 가 의미를 가짐.
- (가정 4) 두 delta 는 현재 가설의 egocentric frame 에서 예측되고 $`\hat{T}_{t}=\Delta\hat{T}_{t}\circ\tilde{T}_{t}`$ 로 합성 — 잔차(residual) 학습이 성립하려면 초기 가설이 GT 근방(noise 범위 `[1°,10°]`, `[0.002,0.01]` m)이어야 함.
- (가정 5) 구조적 inductive bias 는 런타임 haptic 부재에도 지속 — 추론 시 haptic 0-fill 해도 V-only 대비 2.3배 우위 유지(학습 시 topology 가 visual attention 을 재편했다는 가정).

---

## 📊 하이퍼파라미터·손실

- 손실 식:

$$\mathcal{L}=\mathcal{L}_{\mathrm{pose}}+\lambda_{\mathrm{ADD}}\,\mathcal{L}_{\mathrm{ADD}}+\lambda_{\mathrm{attr}}\,\mathcal{L}_{\mathrm{attr}}+\lambda_{\mathrm{pen}}\,\mathcal{L}_{\mathrm{pen}}$$

  `L_pose` = egocentric trans/rot delta 의 MSE, `L_ADD` = ADD(distinguishable model points), `L_attr` = hand–object 근접성 유도, `L_pen` = mesh 상호침투 penalty.

- 하이퍼:
  | 이름 | 값 | 출처 |
  |------|----|----|
  | `J` (관절 수) | `16` | §III-A |
  | $`\tau`$ (haptic 히스토리) | `4` | §III-A |
  | per-joint flatten 차원 | `28` | §III-C |
  | `F` (finger 토큰) | `4` | §III-C |
  | 시각 토큰 `L` / 차원 `D` | `400` (`20×20`) / `512` | §III-B |
  | `S_FT` (F/T 관절 수) | `4` | §III-A |
  | intra-finger attn layer | `2` | §III-C |
  | inter-finger Graphormer layer | `2` | §III-C |
  | pose noise (rot / trans) | `[1°,10°]` / `[0.002,0.01]` m | §III-E |
  | per-axis trans normalizer `n_t` | `[0.01,0.01,0.01]` m | §IV-A |
  | 추론 refinement 반복 | `2` | §III-D |
  | haptic branch LR 배율 | `2.5×` (vs 시각 backbone) | §III-E |
  | Stage 2 backbone freeze warmup | `3` epoch | §III-E |
  | $`\lambda_{\mathrm{ADD}}, \lambda_{\mathrm{attr}}, \lambda_{\mathrm{pen}}`$ | (원문 미명시) | §III-E |
  | optimizer / batch / epoch 총량 | (원문 미명시) | — |

---

## 🎯 평가 메트릭

- **지표** — position error(cm) · angular error(°) · ADD(cm) · **임계값** — task success = 300 스텝 에피소드당 tip-target 정렬(≤2 cm & ≤15°) 성공 횟수 · **비교 baseline** — V-only(FoundationPose), Naive(flat concat), FingerMLP(구조 bias 없는 4-token), 16-token(pooling 없는 joint-level).
- **필수 프로토콜** — per-frame 단독 지표 금지. open-loop **sequential tracking**(프레임 `t` 추정이 `t+1` 초기화) + **downstream RL manipulation success**(policy 고정, pose source 만 교체)를 1급 지표로. occlusion sweep 0/10/30/50/70/90 %.
- **구조 vs 정보 ablation** — 추론 시 haptic 채널 0-fill 성능을 필수 리포트(구조적 기여 분리).

---

## ✨ 변경 의도 (intent)

희소 embodied haptic(관절 proprioception·손끝 contact·소수 관절 F/T)을 flat vector 로 concat 하는 대신, 손의 kinematic 구조(URDF)를 인코딩 단계에서 보존합니다. 핵심 차별점 세 가지: (1) **compact finger-level tokenization** — 16 관절을 4 손가락 토큰으로 cross-attention pooling 하여, 시각 토큰(400) 대비 소수 토큰으로 norm dominance 를 피함(flat/joint-level 은 vision 억압으로 실패); (2) **intra-finger 마스크 전파** — 손끝에만 있는 F/T·contact 를 같은 손가락의 힘 센서 없는 근위 관절로 흘려 sparse 센싱을 손가락 내부에서 메움; (3) **URDF-derived Graphormer bias** — hop/opposition/adjacency 를 per-head attention bias 로 명시 주입. 결과적으로 이득의 상당 부분이 런타임 촉각 내용이 아니라 **학습 시 topology 가 부여한 inductive bias**(visual attention 재편)에서 오며, 이는 haptic 제거 후에도 지속됩니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 직접 대응 base 없음. KineFuse 는 정책(policy)이 아니라 **CAD-known render-and-compare 6D pose tracker(frozen FoundationPose)에 붙는 haptic 인코더 + 융합 모듈**이라, `pi0`/`smolvla`/`act`/`diffusion` 등 policy family 와 아키텍처 정합성이 낮습니다. `/implement-design` 에서 `🚧 매핑 불가(UNMAPPABLE)` 판정이 유력. 다만 **finger-level tokenization + intra-finger 마스크 + topology-aware graph bias** 라는 관측-인코더 패턴은 lerobot 정책의 proprio/tactile 입력 전처리에 개념적으로 이식 가능한 후보(observation encoder 수준)로만 기록합니다.

---

## 🚧 미해결 / 잠정

- 손실 계수 $`\lambda_{\mathrm{ADD}}, \lambda_{\mathrm{attr}}, \lambda_{\mathrm{pen}}`$, optimizer·batch·총 epoch, backbone/haptic 절대 학습률 값이 본문에 없어 스펙으로 굳히지 못함(구현 시 sweep 대상).
- per-joint feature `C` 구성(위치·속도·contact·F/T·flag 의 정확한 채널 배열)이 "$`28 = C\cdot\tau`$, $`\tau=4`$ → `C=7`" 로 추정될 뿐 원문에 채널 명세 없음 — 가정으로 메움.
- URDF spatial bias 의 정확한 특성 집합(hop/opposition/adjacency 외 추가 항)과 bias MLP 구조가 미명시.
- 시각 backbone(FoundationPose)의 crop 크기 `H_c×W_c`·정규화 통계는 FoundationPose 프로토콜 승계로 가정(원문 재기술 없음).
- `S_FT` 를 넘어서는 손 토폴로지(손가락 수·opposition 관계)로의 bias 전이 가능 여부는 미해결 — 손별 재학습 필요 여부가 열린 문제.
