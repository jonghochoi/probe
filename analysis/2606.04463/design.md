# Design — OSCAR: Omni-Embodiment Action-Conditioned World Model for Robotics

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | OSCAR: Omni-Embodiment Action-Conditioned World Model for Robotics |
| 링크 | [arXiv:2606.04463](https://arxiv.org/abs/2606.04463) |
| 분석 문서 | [`analysis/2606.04463/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-11 |

---

## 🧮 데이터 계약

시간 축은 의미 단위로 기록합니다 — `T` = 학습 window 프레임 수(본문 81), `T'/H'/W'` = VAE latent 의 시공간 차원, `K` = kinematic tree 링크 수(embodiment 별 가변).

- **입력 (첫 프레임)** — $`I_0`$: shape `(B, 3, H, W)`, RGB uint8→[-1,1] 정규화 가정. 매 denoising step 에서 첫 temporal 위치 latent 를 $`I_0`$ 의 clean VAE 인코딩으로 덮어씀 (외형 앵커).
- **입력 (skeleton 비디오)** — $`S_{1:T}`$: shape `(B, 3, T, H, W)`, RGB. 검은 캔버스(전부 0) 위 kinematic tree 를 선분+원으로 rasterise. gripper 개폐는 visual indicator 로 동봉. 타깃과 frame-by-frame 정렬.
- **입력 (액션 → skeleton)** — 관절 구성 $`q_t`$ + URDF/MANO 모델 $`M`$ + 카메라 $`(K_{\mathrm{cam}}, T^{\mathrm{cam}}_{\mathrm{world}})`$. FK → SE(3) pose → perspective projection $`\pi`$ → rasterise. (Layer 1 에서 액션은 raw 텐서가 아니라 **렌더링된 골격 비디오**로 모델에 도달.)
- **출력 (생성 비디오)** — $`V_{1:T}`$: shape `(B, 3, T, H, W)`, native 해상도 `512×288` (평가 시). 첫 프레임 고정, 미래 프레임만 denoise.
- **잠재 표현** — $`z \in \mathbb{R}^{T'\times H'\times W'\times d}`$ (WAN 2.1 VAE). skeleton latent $`z^s`$ 는 타깃 latent $`z^v_t`$ 와 **동일 shape**.
- **(latent-action ablation 경로만)** — per-arm `7`-D(3 trans + 3 Euler rot + 1 gripper), bimanual concat / single-arm zero-pad 한 `14`-D, $`T-1=80`$ transition → `(80,14)` → flatten `1120`-D.

---

## 🧰 모듈 인터페이스

```python
def render_skeleton(q_t, M, o, K_cam, T_cam_world) -> Tensor:
    """관절 구성 q_t 와 kinematic 모델 M(URDF 또는 MANO)을 FK→투영→rasterise 해
    검은 캔버스 위 2D 골격 프레임 S_t (3,H,W) 를 만든다. embodiment 교체는
    (M, q_t, o) triple 만 바꾼다."""

def encode_condition(I_0, S_1T, vae) -> tuple[Tensor, Tensor]:
    """첫 프레임 I_0 와 골격 비디오 S_1T 를 동일 WAN 2.1 VAE 로 인코딩해
    (z_I0_clean, z_s) 를 반환. z_s 는 타깃 비디오 latent 와 동일 shape."""

def inject_condition(z_v_noisy, z_s, PE_v, PE_s) -> Tensor:
    """비디오 latent 와 skeleton latent 를 각각 patch embedder 로 DiT hidden 차원에
    임베딩한 뒤 토큰 텐서를 합산(sum)해 denoising 입력 토큰을 만든다."""

def dit_velocity(tokens, t, c) -> Tensor:
    """rectified-flow 속도장 v_theta(z_t, t, c) 예측. c = 첫 프레임 + skeleton 조건.
    CFG: 학습 중 p=0.2 로 S_1T 를 zeros 로 대체, 추론 guidance scale w=6."""

def rollout(I_0, action_seq, model) -> Video:
    """기록된 첫 프레임과 주어진 액션으로 autoregressive(open-loop) 비디오 rollout."""

def score_policy(video, instruction, vlm_judge) -> dict:
    """생성 비디오 32프레임을 VLM judge 에 전달 → {binary success, 0–100 progress,
    reason}. caption 은 미전달(human rater 가 보는 증거만). 정책 순위/성공률 산출."""
```

- `render_skeleton` — 외부 호출 계약: FK·카메라 intrinsic/extrinsic 정확도에 직접 의존(정렬 오차 = 학습 신호 오차).
- `inject_condition` — loss/optimizer 와의 관계: 합산된 토큰은 그대로 `dit_velocity` → `L_RF` 로 흐름. 별도 액션-정렬 보조손실 없음.
- `score_policy` — 평가 메트릭(MMRV/Pearson/SISR_Δ) 계산의 입력 생성기. (원문에 명시 없음 — 가정으로 메움: judge JSON 스키마 외 파싱 규칙은 본문 미상세.)

---

## ⛓️ 불변식·가정

- **(가정 1)** — skeleton latent $`z^s`$ 와 비디오 latent $`z^v_t`$ 는 **동일 shape**여야 함 (토큰 합산 가능 조건). 동일 WAN 2.1 VAE 사용이 이를 보장.
- **(가정 2)** — 첫 프레임 $`I_0`$ 가 외형·장면을 앵커하므로, conditioning 골격은 텍스처를 담지 않아도 됨 (외형/모션 책임 분리). 이 분리가 깨지면 골격이 외형까지 책임져 cross-embodiment 일반화가 무너짐.
- **(가정 3)** — embodiment 간 차이는 kinematic spec $`(M, q_t, o)`$ 에 **전부 흡수**됨 — 5지 손과 2조 그리퍼가 같은 2D 선화로 환원되어 단일 표현이 성립.
- **(가정 4)** — 카메라는 정적(학습 데이터 필터로 보장). camera motion 은 미지원 — 정적 카메라 가정이 깨지면 골격↔RGB 정렬이 시간축으로 흔들림.
- **(가정 5)** — VLM judge 의 성공 판정이 human rater 와 정렬됨 (eval-in-imagination 신뢰의 전제). world-model 환각과 judge 오판이 무상관이어야 상관 지표가 유효.

---

## 📊 하이퍼파라미터·손실

- 손실 식 (rectified flow, Eq. 1):

$$\mathcal{L}_{\mathrm{RF}}\;=\;\mathbb{E}_{t,\,z_{0},\,\epsilon}\,\big\Vert v_{\theta}(z_{t},\,t,\,c)-(\epsilon-z_{0})\big\Vert_{2}^{2},\qquad z_{t}=(1-t)\,z_{0}+t\,\epsilon$$

- 하이퍼:
  | 이름 | 값 | 출처 |
  |------|----|----|
  | optimizer | AdamW | §A.3 |
  | learning rate | $`3\times10^{-5}`$ | §A.3 |
  | batch size | `16` | §A.3 |
  | timestep 분포 | logit-normal + reweighting, shift `5` | §A.3 |
  | source weighting | $`w_i \propto n_{\mathrm{frames},i}^{1/T}`$, $`T{=}3`$ | §A.3 |
  | training window | `81` frames, 시작 프레임 grasp/release 편향(trapezoid prior) | §A.3 |
  | CFG drop prob | `0.2` (S_{1:T}→zeros) | §A.3 |
  | CFG guidance scale | `w=6` (inference) | §A.3 |
  | schedule | Stage1 `15k` iter(robot) → Stage2 robot+human 혼합 | §5.1, §A.3 |
  | dedup: SigLIP cosine | $`\ge 0.95`$ flag, 5프레임 임베딩 | §4.3 |
  | dedup: trajectory | `64`-step RMS < adaptive threshold | §4.3 |
  | filter: 최소 길이 | $`\ge 70`$ frames | §4.2 |
  | backbone | Cosmos-Predict2.5-2B, WAN 2.1 VAE | §3.1 |
  | 하드웨어 | 단일 NVIDIA GH200 GPU | §5.1 |
  | static-camera threshold | (원문 미명시 — "threshold"로만 기술) | §4.2 |
  | visible-skeleton threshold | (원문 미명시 — "threshold"로만 기술) | §4.2 |

---

## 🎯 평가 메트릭

생성 품질과 정책-평가 충실도 두 축:

- **생성 품질** — `PSNR↑` / `SSIM↑` / `LPIPS↓` (reconstruction), `tLPIPS↓` (temporal), `FVD↓` / `FID↓` / `L2_latent↓` (distribution), `FPS↑` (speed). 첫 `49` 프레임에서 Kinema4D 프로토콜대로 측정, 동일 GH200. 비교 baseline: Cosmos-Predict2.5, TesserAct, IRASim, Ctrl-World, EnerVerse-AC, Genie Envisioner, Kinema4D(14B). OSCAR(2B): PSNR 24.24 / SSIM 0.846 / LPIPS 0.094 / FVD 7.08 / FID 15.07.
- **정책 평가 충실도** — `MMRV↓` (range `[0,6]`, rank violation), Spearman $`\rho\uparrow`$, Pearson `r↑` (per-policy mean binary SR), $`\mathrm{SISR}_\Delta\downarrow`$ (pp, $`|\mathrm{SR}_{\mathrm{real}} - \mathrm{SR}_{\mathrm{pred}}|`$ MAE). RoboArena 65 session × 7 정책. skeleton: MMRV 0.571 / ρ +0.750 / r +0.852 / SISR_Δ 1.73pp.
- **judge** — GPT-5 (gpt-5-2025-08-07, high reasoning), 32 프레임 균등 샘플 @ `512×288`, task instruction 만(캡션 미전달), JSON {binary success, 0–100 progress, reason}. pairwise 1,365 preference → Bradley–Terry.

---

## ✨ 변경 의도 (intent)

OSCAR 의 변경 의도는 action-conditioned world model 의 conditioning 표현을 latent-action 과 dense geometry(mesh/pointmap)의 양극 사이에서 **2D kinematic skeleton 렌더링**으로 고정한 것입니다. latent-action 은 다중 embodiment 를 다루지만 압축 신호에서 모션을 역추론해 부정확하고, dense geometry 는 정밀하지만 embodiment appearance 에 과적합합니다. skeleton 은 kinematic chain 에만 의존하고 텍스처가 없어, (1) embodiment 교체를 kinematic spec 교체로 환원해 4종 로봇 + 사람 손(MANO)을 단일 표현으로 묶고, (2) 모델이 운동학↔실제 모션 관계를 명시 학습하도록 강제해 외형 과적합을 억제합니다. mesh 와 정량 동률이지만 URDF 자산 비의존 + human 데이터 흡수 가능이라는 점이 선택을 가릅니다. 이로써 단일 GH200·2B 로 14B/다GPU baseline 을 능가하고, eval-in-imagination 을 RoboArena 실상관까지 끌어올립니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 없음(직접 base 후보 부재). lerobot 의 6개 policy(`pi0`/`pi05`/`pi0_fast`/`smolvla`/`act`/`diffusion`)는 모두 **action policy**이며, OSCAR 는 video diffusion **world model**(Cosmos-Predict2.5-DiT 계열)이라 family 가 다릅니다. lerobot 에서 직접 매핑 가능한 부분은 (a) `datasets/` LeRobotDataset 포맷으로의 데이터 파이프라인(curate/filter/dedup) 단계와 (b) 정책 평가 harness 의 정책 측(평가 대상 policy)뿐이며, world-model 본체(skeleton conditioning + rectified-flow DiT)는 lerobot 좌표계에 base 가 없습니다 — `/implement-design` 에서 `🚧 매핑 불가` 가능성이 높습니다.

---

## 🚧 미해결 / 잠정

- static-camera filter threshold, visible-skeleton percentage threshold, dedup adaptive RMS threshold 의 구체 수치는 본문에 "threshold"로만 기술 — 값 미명시.
- 입력 정규화([-1,1] 등) 구체 규약은 백본(Cosmos/WAN VAE) 관례를 따른다고 가정 — 본문 명시 없음.
- 골격 rasterise 의 선/원 굵기·canvas 해상도, gripper visual indicator 의 정확한 그리기 규칙은 본문 미상세.
- VLM judge JSON 파싱·집계 규칙(부분점수 가중 등) 및 Bradley–Terry 추정 구현 세부는 본문 미상세.
- camera intrinsic/extrinsic 추정(MoGe-v2 / CtRNet-X) 실패 시 fallback 절차 미명시 — 저자도 캘리브레이션 가용성을 한계로 지목.
