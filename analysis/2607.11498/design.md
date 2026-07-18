# Design — See like a Robot: Robot-Centric Pointmaps for Vision-Language-Action Models

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | See like a Robot: Robot-Centric Pointmaps for Vision-Language-Action Models |
| 링크 | [arXiv:2607.11498](https://arxiv.org/abs/2607.11498) |
| 분석 문서 | [`analysis/2607.11498/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-07-18 |

---

## 🧮 데이터 계약

시간 축은 의미 단위(`T_action` = action chunk 길이)로 기록합니다. `N_cam` 은 카메라 수(sim 3, real 2).

- **입력** — `rgb`: shape `(B, N_cam, 3, H, W)`, float, 백본 native 해상도로 정규화(SigLIP 전처리).
- **입력** — `depth`: shape `(B, N_cam, H, W)`, float(미터), 픽셀별 metric depth (`D_c`).
- **입력** — `intrinsics`: shape `(B, N_cam, 3, 3)`, float, 카메라 `K_c`.
- **입력** — `extrinsics`: shape `(B, N_cam, 4, 4)` 또는 `(R_c, t_c)`, float, camera→robot base 강체변환.
- **입력** — `ee_position`: shape `(B, 3)`, float(미터), 로봇 base 프레임 end-effector 위치 `t_EE`.
- **파생(입력 대체)** — `pointmap` (`P^EE_c`): shape `(B, N_cam, 3, H, W)`, float(미터), 로봇 base 프레임 3D 좌표를 EE 위치로 감산해 재중심화. RGB 와 동일 그리드.
- **입력** — `proprioception`: shape `(B, D_proprio)`, `language`: token 시퀀스 (백본 계약 그대로).
- **출력** — `action`: shape `(B, T_action, D_action)`, end-effector delta chunk. sim `T_action=50`(execute 25), real `T_action=20`(execute 10).

---

## 🧰 모듈 인터페이스

```python
def build_robot_centric_pointmap(
    depth,        # (B, N_cam, H, W)  metric depth D_c
    intrinsics,   # (B, N_cam, 3, 3)  K_c
    extrinsics,   # (B, N_cam, R_c, t_c)  camera->robot base
    ee_position,  # (B, 3)  t_EE (robot base frame)
) -> "pointmap":  # (B, N_cam, 3, H, W)  P^EE_c, EE-centered
    """RGB-D 를 카메라프레임 lift(Eq.1) → 로봇프레임 변환(Eq.2)
       → EE 재중심화(Eq.3). 그리드 H×W 보존, 픽셀당 XYZ 1개."""

def encode_and_fuse(
    rgb,       # (B, N_cam, 3, H, W)
    pointmap,  # (B, N_cam, 3, H, W)
    rgb_encoder,      # f_theta (pretrained SigLIP tower)
    pointmap_encoder, # g_phi (동일 아키텍처, f_theta 가중치로 init)
) -> "visual_tokens":  # (B, N_cam*N_tok, d)  z_c
    """z_c = f_theta(I_c) + g_phi(P^EE_c). element-wise add,
       토큰 shape 불변(추가 토큰 없음). z_c 가 RGB 토큰을 대체."""
```

- `build_robot_centric_pointmap` — 순수 기하 변환, 학습 파라미터 없음. calibration(`K_c, R_c, t_c`)과 `t_EE` 를 요구. 손실/옵티마이저와 무관.
- `encode_and_fuse` — `pointmap_encoder`(`g_phi`)는 RGB 인코더와 **동일 아키텍처**, 초기 가중치는 `f_theta` 복제. 출력 `z_c` 는 백본 VLA 의 시각 입력 슬롯에 그대로 주입(다운스트림 language·action expert 계약 불변).

---

## ⛓️ 불변식·가정

- (가정 1) — **좌표 불변성**: 동일 물리 점은 카메라 시점과 무관하게 동일한 로봇프레임 좌표 `P^R_c(u,v)` 를 가진다(픽셀 위치 `(u,v)` 만 변함). 이 성질이 깨지면 시점 강건성 근거가 무효.
- (가정 2) — **그리드 대응**: pointmap 은 RGB 와 동일한 `H×W` 격자에 픽셀당 정확히 하나의 XYZ 를 담아, RGB 토큰과 위치별 1:1 대응한다(element-wise add 의 전제).
- (가정 3) — **calibration 가용성**: 학습·테스트 모두에서 정확한 `K_c, R_c, t_c` 와 `t_EE` 가 프레임마다 존재한다. 없으면 pointmap 구성 불가.
- (가정 4) — **공통 원점**: 액션이 EE 의 움직임(delta)으로 정의되므로 EE-centered pointmap 의 목표 좌표는 곧 그리퍼가 이동해야 할 변위와 같은 원점을 공유한다.
- (가정 5) — **인코더 전이성**: RGB 로 사전학습된 시각 인코더 가중치가 XYZ 이미지(pointmap) 인코딩에도 유용한 초기값이 된다.

---

## 📊 하이퍼파라미터·손실

- 손실 식: `L = L_backbone(action | z_c, proprio, language)` — 백본 VLA 의 원래 액션 예측 손실을 그대로 사용. pointmap 전용 손실 항 **없음**.
- pointmap 구성:
  - $`P_{c}^{\mathrm{cam}}(u,v)=D_{c}(u,v)K_{c}^{-1}[u,v,1]^{\top}`$  (Eq. 1)
  - $`P_{c}^{\mathrm{R}}(u,v)=R_{c}P_{c}^{\mathrm{cam}}(u,v)+t_{c}`$  (Eq. 2)
  - $`P^{\mathrm{EE}}_{c}(u,v)=P_{c}^{\mathrm{R}}(u,v)-t_{\mathrm{EE}}`$  (Eq. 3)
- 융합: $`z_{c}=f_{\theta}(I_{c})+g_{\phi}(P^{\mathrm{EE}}_{c})\in\mathbb{R}^{N_{\mathrm{tok}}\times d}`$  (Eq. 4)
- 하이퍼:
  | 이름 | 값 | 출처 |
  |------|----|----|
  | `optimizer` | AdamW | §B.1, Table 6 |
  | `peak_lr` | `1e-4` | §B.1, Table 6 |
  | `lr_schedule` | cosine, 5% linear warmup | §B.1, Table 6 |
  | `precision` | bfloat16 | §B.1, Table 6 |
  | `effective_batch_size` | 64 | §B.1, Table 6 |
  | `train_steps` (π0.5 / SmolVLA) | 20k / 60k | §B.1, Table 6 |
  | `action_chunk` sim / real | 50 (exec 25) / 20 (exec 10) | Table 6 |
  | `control_freq` (real) | 20 Hz | §B.3, Table 6 |
  | `fusion` | element-wise add | §3, Table 6 |
  | `ee_centering` | True | §3 (Eq. 3), §4.3 |
  | `pointmap_encoder_init` | RGB encoder (f_theta) 복제 | §3 |
  | `vision_tower` | SigLIP | §B.1 |

---

## 🎯 평가 메트릭

- **지표** — task success rate (SR, %) · **임계값** — sim task당 50 episode 평균, real 카메라조건당 15 rollout 평균, 단일 최종 체크포인트(best 선택 없음) · **비교 baseline** — 동일 백본 RGB-only(입력만 다름), camera-aware(KYC/OC-VLA), 3D-augmented(GeoVLA/PointVLA), point cloud policy(FP3/DP3).
- **핵심 판별 프로토콜** — 실로봇 **seen/unseen 카메라 배치**: unseen 에서 RGB-only 대비 degradation gap(본 논문 18.3 vs 11.6) 및 margin 확대(+5.0→+11.7)가 관측표현 효과의 결정 지표.
- **통제 축** — `Fixed vs Rand.` 평가 시점의 SR 하락폭 $`\Delta`$ (EE centering 시 `-0.3` vs base `-2.0`).

---

## ✨ 변경 의도 (intent)

기존 3D-aware VLA 는 전용 3D 인코더/기하 전문가(GeoVLA, PointVLA)를 붙이거나 기하를 2D 로 재렌더링해, 사전학습 시각 가중치를 상속하지 못하거나 추론마다 별도 stage 를 더합니다. camera-aware 노선(KYC의 Plücker, OC-VLA의 camera-frame 액션)은 입력을 여전히 카메라뷰 이미지로 남겨 장면이 로봇프레임으로 표현되지 않습니다. 본 설계는 관측을 **픽셀당 로봇프레임 XYZ 이미지(pointmap)** 로 사전 변환하고 RGB 인코더를 복제한 tower 로 인코딩해 **element-wise 덧셈** 으로 융합합니다. 그 결과 (1) 전용 3D 인코더·voxel·추가 토큰이 없고, (2) 사전학습 2D 시각 가중치를 그대로 재사용하며, (3) 배포 시에도 metric 3D 입력을 유지합니다. 핵심은 "정책에 좌표 변환을 학습시키지 말고 입력에서 미리 풀어라"이며, EE centering 으로 관측·액션의 원점을 일치시켜 시점·위치 변화에 강건해집니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 후보 base: `smolvla` (논문 백본과 직접 일치) 및 `pi05`/`pi0` family. 본 논문이 정확히 이 두 백본(π0.5, SmolVLA)의 시각 입력만 교체하는 형태라 매핑 적합성이 높음. 개입 지점은 (a) RGB-D→pointmap 전처리(processor/transform 단), (b) 두 번째 SigLIP tower(RGB 인코더 가중치로 init), (c) 시각 토큰 element-wise add. calibration/EE pose 를 dataset 계약에 추가해야 함.

---

## 🚧 미해결 / 잠정

- **주입 위치** — pointmap 을 action expert 대비 어디에 주입할지(§6 저자 명시 미ablate). 본 설계는 "RGB 토큰과 동일 지점 element-wise add" 만 고정.
- **정규화 통계** — pointmap XYZ(미터)의 정규화 방식이 본문에 명시되지 않아 "데이터셋 전체 범위/표준편차 기반" 으로 가정(원문에 명시 없음 — 가정으로 메움).
- **N_tok/d 구체값** — 백본별 토큰 수·차원은 SigLIP·백본 설정에 종속되며 본문에 수치 미명시.
- **point cloud 샘플링 예산** — 비교의 단일 예산(카메라당 1024점 / DP3 4096점)은 결론의 조건. Layer 1 스펙 외.
- **depth 정규화·결측 처리** — real 센서 depth 의 결측/노이즈 마스킹 규칙이 본문에 없어 미확정.
