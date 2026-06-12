# Design — TacForeSight: Force-Guided Tactile World Model for Contact-Rich Manipulation

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | TacForeSight: Force-Guided Tactile World Model for Contact-Rich Manipulation |
| 링크 | [arXiv:2606.11184](https://arxiv.org/abs/2606.11184) |
| 분석 문서 | [`analysis/2606.11184/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-12 |

---

## 🧮 데이터 계약

시간 축은 의미 단위로 기록합니다. `H` = 촉각 잠재 청크 길이(과거 프레임 수), $`\Delta`$ = 예측 시간 offset, `n` = wrench/촉각 sampling-rate 비율(본문 하드웨어에서 120/30 = 4), `K` = proprioception 이력 길이, `L` = 행동 청크 길이.

- **입력(촉각)** — `tactile_field`: shape `(B, H, 2, H_px, W_px, 3)`, float. 손가락 $`s\in\{L,R\}`$, 각 프레임 `35×20×3` 3D marker displacement map(본문 하드웨어). 정규화 통계 `(원문에 명시 없음 — 가정으로 메움)`.
- **입력(force)** — `wrist_wrench`: shape `(B, n*H, 6)`, float. 6축 force/torque, 촉각보다 `n×` 고주파. 정규화 `(원문에 명시 없음 — 가정으로 메움)`.
- **입력(시각)** — `rgb`: shape `(B, 3, H_img, W_img)`, float. 단일 손목 RGB. frozen DINOv2-small 입력 전처리(ImageNet 정규화로 가정).
- **입력(proprioception)** — `state`: shape `(B, K, d_s)`, float. 최근 `K` 프레임 로봇 상태. `d_s` `(원문 미명시)`.
- **WM 출력(잠재)** — `pred_tactile_latent` $`\hat{\mathbf{Z}}_{t}^{\mathrm{tac}}`$: shape `(B, H, D_z)`, float. 미래 촉각 잠재 청크(시간 offset $`\Delta`$).
- **정책 출력(행동)** — `action_chunk` $`\mathbf{A}_{t}`$: shape `(B, L, d_a)`, float. flow-matching으로 생성된 행동 청크.
- **중간(프레임 잠재)** — `z_t` $`\in\mathbb{R}^{D_z}`$: `[CLS]` frame-level 촉각 잠재. `D_z` `(원문 미명시 — 차원 값 없음)`.

---

## 🧰 모듈 인터페이스

```python
def tactile_tokenizer(tactile_field):  # (B,H,2,H_px,W_px,3) -> (B,H,D_z)
    """공유 CNN(Φ_sp) + pos/finger-id embedding + Transformer; [CLS]=frame 잠재 z_t."""

def force_encoder(wrist_wrench):  # (B,n*H,6) -> (B,H,D_c)
    """raw F/T 사영 + dilated causal 1D conv(WaveNet류) + causal downsample → 촉각 정렬 조건 c."""

def latent_dynamics_predictor(z_chunk, c_chunk):  # (B,H,D_z),(B,H,D_c) -> (B,H,D_z)
    """force-conditioned latent Transformer T_ψ; force는 AdaLN 주입; chunk forecasting(offset Δ)."""

def current_future_interaction(z_cur, z_fut):  # (B,H,D_z)x2 -> (B,D_z)
    """temporal embed 후 CA(Q=cur, K/V=fut) 잔차 → 시간평균 → future-aware h_tac."""

def adaptive_vt_fusion(h_img, h_tac):  # -> (B,D)
    """α=σ(MLP(h_tac)); h_vt=(1-α)⊙h_img + α⊙h_tac (채널 단위 게이트)."""

def flow_matching_head(h_vt, h_s, tau, A_noisy):  # -> velocity (B,L,d_a)
    """h_vt+h_s → condition y_t; temporal U-Net v_θ 가 속도장 회귀(추론은 ODE 적분)."""
```

- **tactile_tokenizer** — 입력 dual-finger 촉각, 출력 frame-level 잠재 시퀀스. 인코더 가중치 양 손가락 공유, finger-id embedding으로 좌/우 구분.
- **force_encoder** — 출력 조건 시퀀스는 촉각 latent와 시간 정렬. causal 구조로 미래 누출 차단.
- **latent_dynamics_predictor** — WM 핵심. 학습 시 `L_WM`(아래)로 감독, 학습 후 **동결**되어 정책에 잠재 공급.
- **current_future_interaction / adaptive_vt_fusion / flow_matching_head** — 정책 구성. `flow_matching_head`는 `L_FM`으로 학습.

---

## ⛓️ 불변식·가정

- (가정 1) **시간 인과성** — force_encoder의 dilated conv + downsample은 causal이어야 하며, 미래 wrench가 현재 조건에 새지 않습니다(누출 시 예측 평가가 무의미해짐).
- (가정 2) **force 선행성** — 전역 force 변화가 국소 촉각 변화를 시간적으로 앞섭니다(본문: 약 200 ms). 이 비대칭이 없으면 force conditioning의 이득이 사라집니다.
- (가정 3) **잠재 비붕괴** — SIGReg 없이는 촉각 잠재가 collapse할 수 있으므로, 잠재 분포가 등방 가우시안 구조에 가깝게 유지되어야 forecasting이 유효합니다.
- (가정 4) **chunk 시간 일관성** — 예측은 frame-wise one-step이 아니라 chunk 단위여서 인접 timestep 잠재가 시간적으로 매끄럽게 연결됩니다(1차 차분 손실이 이를 강제).
- (가정 5) **WM 동결의 분포 정합** — 정책 학습 시 WM이 동결되므로, 정책이 보는 접촉 분포가 WM 사전학습 분포 안에 있어야 예측 잠재가 신뢰 가능합니다.

---

## 📊 하이퍼파라미터·손실

- WM 예측 손실 (식 5):

$$\mathcal{L}_{\mathrm{pred}}=\mathrm{MSE}\left(\hat{\mathbf{Z}}_{t}^{\mathrm{tac}},\mathbf{Z}_{t}^{\mathrm{tac}}\right)+\lambda_{\mathrm{dyn}}\mathrm{MSE}\left(\nabla\hat{\mathbf{Z}}_{t}^{\mathrm{tac}},\nabla\mathbf{Z}_{t}^{\mathrm{tac}}\right)$$

- WM 최종 손실 (식 6):

$$\mathcal{L}_{\mathrm{WM}}=\mathcal{L}_{\mathrm{pred}}+\lambda_{\mathrm{sig}}\mathcal{L}_{\mathrm{sig}}$$

- 정책 flow-matching 손실 (식 12):

$$\mathcal{L}_{\mathrm{FM}}=\mathbb{E}_{\mathbf{A}_{t}^{(0)},\mathbf{A}_{t}^{(1)},\tau}\left[\left\|v_{\theta}\left(\mathbf{A}_{t}^{(\tau)},\tau,\mathbf{y}_{t}\right)-\mathbf{u}_{t}\right\|_{2}^{2}\right]$$

- 하이퍼:
  | 이름 | 값 | 출처 |
  |------|----|----|
  | `lambda_dyn` ($`\lambda_{\mathrm{dyn}}`$) | `1.00` | §IV-A2 |
  | `lambda_sig` ($`\lambda_{\mathrm{sig}}`$) | `0.09` | §IV-A2 |
  | WM 학습 step | `150k` | §IV-A2 |
  | WM 파라미터 | `11.8M` | §IV-A2 |
  | 정책 파라미터 | `68.9M` | §IV-A2 |
  | WM 사전학습 에피소드 | `2,700` | §IV-A2 |
  | wrench/촉각 rate 비율 `n` | `4` (120 Hz / 30 Hz) | §IV-A1 |
  | 추론 rate | `20 Hz` (RTX 4090D) | §I |
  | `H` (청크), $`\Delta`$ (offset), `D_z`, `D_c`, `L`, `d_a` | `(원문 미명시)` | — |
  | optimizer / lr / batch | `(원문 미명시)` | — |

---

## 🎯 평가 메트릭

- **정책 성능** — `task completion score` · 과제당 20회 시행 평균. Wiping/Swiping은 완료/목표 길이 비율, 2단계 과제(Adjustment/Locking)는 1단계 50%·전체 100%, Wire Insertion은 완전 삽입만 성공, 외란 설정은 복원+완료만 성공. 비교 baseline: DP / DP+Tactile+Force / KineDex / FoAR / RDP. Ours: nominal 5과제 평균 79.0%, 외란 3과제 평균 86.7%.
- **World model 예측 품질** — `MSE`↓ / `cosine similarity`↑ / `symmetric KL`↓. Wrist Wrench 조건이 `0.017 / 0.992 / 0.009`로 최고(무조건 `0.027 / 0.954 / 0.014`).
- **표현 분석** — 예측 잠재의 접촉 전이 선행성(약 200 ms), t-SNE 접촉 패턴 군집 분리, 외란 복원 시간(adaptive gate 유 `2.56 s` / 무 `4.06 s`).

---

## ✨ 변경 의도 (intent)

기존 contact-rich 정책이 force·촉각을 동시 입력으로 **반응적 융합**하는 데 그치는 반면, TacForeSight는 global force가 local tactile을 시간적으로 선행한다는 비대칭을 **명시적 예측**으로 전환합니다. force를 조건으로 미래 촉각 latent를 chunk 단위로 forecast하고, 그 예측을 current↔future cross-attention + 채널 단위 tactile gate로 정책에 "선행 접촉 사전"으로 주입함으로써, 외란 발생 시 반응이 아니라 **선제 복원**이 가능해지는 것이 핵심 차별점입니다. 고차원 픽셀/촉각 생성 대신 compact latent forecasting만 수행해 20 Hz 실시간성을 유지합니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 행동 헤드가 conditional flow matching + temporal U-Net 이므로 `diffusion`(Diffusion Policy, U-Net 백본) 또는 flow-matching 계열 `pi0`/`smolvla`의 action-head와 가장 가깝습니다. 단 TacForceWM(촉각 토크나이저 + force 인코더 + latent predictor)과 frozen DINOv2 인코더, 채널 게이트 융합은 lerobot 표준 정책에 없는 신규 모듈이라 base 위에 **추가 구성요소**로 얹는 형태가 됩니다. 정확한 매핑은 `/implement-design`이 판정.

---

## 🚧 미해결 / 잠정

- `H`(청크 길이), $`\Delta`$ (예측 offset), `D_z`/`D_c`(잠재 차원), `L`(행동 청크), `d_a`(행동 차원)가 본문에 수치로 명시되지 않아 Layer 1 스펙으로 고정 불가 — `(원문 미명시)`.
- optimizer / learning rate / batch size / LR 스케줄 미명시 — `(원문 미명시)`.
- 촉각·force·proprioception 정규화 통계 출처 미명시 — "데이터셋 전체 평균/표준편차"로 가정.
- `condition encoder`(h_vt+h_s → y_t)의 구체 구조와 temporal U-Net 깊이/채널 미명시.
- SIGReg 내부 sketch 차원·샘플 수 등 LeJEPA 차용 세부는 원 논문(arXiv:2511.08544) 의존 — 본문 단독으로 미확정.
