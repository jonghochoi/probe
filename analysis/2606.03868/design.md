# Design — Unified Video-Action Joint Denoising for Dexterous Action and Data Generation

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Unified Video-Action Joint Denoising for Dexterous Action and Data Generation |
| 링크 | [arXiv:2606.03868](https://arxiv.org/abs/2606.03868) |
| 분석 문서 | [`analysis/2606.03868/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-10 |

---

## 🧮 데이터 계약

시간 축은 고정 horizon `T` 의 의미 단위로 기록합니다 (절대 프레임 인덱스 아님). 비디오는 Wan VAE 잠재공간으로 인코딩된 토큰 시퀀스, 액션은 normalized bimanual MANO 궤적입니다.

- **입력 — 언어** `c`: 토큰화된 instruction (text encoder frozen). shape `(B, L_text)`.
- **입력 — 초기 이미지(옵션)** $`I_\star \in \{I_0, \varnothing\}`$ : 첫 프레임 RGB. VAE 인코딩 후 첫 video latent 프레임을 대체하고 timestep 0 부여. 학습 시 확률 `0.30` 으로 drop.
- **입력 — hand-camera anchor** `g_0 = (s_0, K)`: 첫 프레임 MANO 상태 `s_0` + 카메라 intrinsics `K`. T2VA 에서는 initializer 가 `g̃_0` 를 instantiate.
- **입력(파생) — anchor map** `M_0 = R(g_0)`: 색상 코딩 MANO 스켈레톤 이미지 → frozen Wan VAE → latent `m_0 = E(M_0)`.
- **출력 — 비디오** $`V_{0:T}`$ (또는 정책 모드 $`V_{1:T}`$ ): Wan VAE latent $`x^\star = \mathcal{E}(V_{0:T})`$ , raw-pixel 디코딩 가능. dtype bfloat16.
- **출력 — 액션** $`A_{1:T} = a^\star`$ : normalized continuous bimanual MANO 궤적. invalid/missing 손은 마스크 `M_a` 로 처리. shape `(B, T, D_mano_bimanual)` (정확한 `D` 원문 미명시).
- **토큰 레이아웃** — `z = [z_video, z_action, z_anchor]` (Eq. 5).

---

## 🧰 모듈 인터페이스

```python
def donk_denoiser(z_video, z_action, z_anchor, c, t, mode) -> tuple:
    """video token + action token 을 joint denoise. (v̂_x, v̂_a) velocity 예측.
       mode ∈ {'TI2VA', 'T2VA'} 는 이미지 conditioning 유무로만 갈림."""

def video_preserving_attention(q, k, v, token_kind) -> Tensor:
    """video query → video token 만, action/anchor query → 전체 시퀀스 attend
       (비대칭 마스크, Fig. 3). 사전학습 Wan 비디오 prior 보존."""

def anchor_map_controller(m_0, layers_S) -> dict:
    """C = G_anc(Patch(m_0)); 각 ℓ∈S 에 H_ℓ = MLP_ℓ(C).
       gated first-frame 주입: z_video[ℓ,0] += γ_ℓ · H_ℓ (γ_ℓ init 0)."""

def text_anchor_initializer(c) -> g_tilde_0:
    """T2VA 전용. 첫 프레임 hand-camera 경험 분포 학습 → g̃_0 instantiate.
       오직 초기 anchor map 렌더링에만 사용 (denoiser 와 별도 학습)."""

def wan_teacher(x_t, c) -> v_x_tea:
    """frozen Wan teacher. 같은 video latent·text 로 video velocity 예측
       (이미지 조건 유지 시에만 prior loss 에 사용)."""
```

- **denoiser** — 입력: 토큰 `z`, 조건 `c`/`I_⋆`/`g_0`, flow timestep `t`. 출력: `(v̂_x, v̂_a)`. Wan2.2 TI2V-5B 초기화, 원 Wan head=video, 경량 action head=MANO.
- **anchor encoder / adapter `G_anc`** — patchified `m_0` → Wan token 공간 → layer-wise hint `H_ℓ`. action·anchor 인터페이스와 함께 end-to-end 학습.
- **teacher** — frozen; `L_prior` 의 target 제공. gradient 흐르지 않음.
- **freeze 계약** — text encoder · VAE · teacher · 대부분 Wan 블록 frozen; action/anchor 인터페이스 · anchor-map adapter · action head · 소수 Wan layer 만 학습.

---

## ⛓️ 불변식·가정

- (가정 1) — **conditioning 스위치 불변** — 이미지 drop 확률 `0.30` 으로 TI2VA(`I_⋆=I_0`)와 T2VA(`I_⋆=∅`)가 동일 백본·토큰 레이아웃·목표를 공유. 두 모드는 별개 파이프라인이 아닌 같은 분포의 두 단면.
- (가정 2) — **anchor 는 초기 조건일 뿐** — `g_0` 는 첫 프레임 기하만 규정하며 미래 궤적 조건이 아니다. 따라서 anchor hint 는 첫 프레임 비디오 토큰에만 주입 (`t>0` 은 불변).
- (가정 3) — **비디오 prior 보존** — video query 가 action/anchor 토큰을 attend 하지 않으면 사전학습 Wan 시각 생성 분포가 유지된다 (video-preserving mask 의 전제).
- (가정 4) — **gate 영-초기화** — $`\gamma_\ell = 0`$ 에서 시작해 학습 초기 동작이 사전학습 Wan 과 동일.
- (가정 5) — **teacher 적용 범위** — `L_prior` 는 이미지 조건 유지 시에만 활성 (텍스트 전용 분기가 이미지 조건부 teacher 를 모방하지 않도록).
- (가정 6) — **MANO 정규화** — action 은 normalized continuous MANO; invalid 손 차원은 `M_a` 로 마스킹. 정규화 통계 출처는 원문 미명시.

---

## 📊 하이퍼파라미터·손실

- 손실 식 (verbatim, Eq. 8–10):
  - $`\mathcal{L}_{\mathrm{video}} = \|\hat{v}_x - v_x\|_2^2`$
  - $`\mathcal{L}_{\mathrm{action}} = \|M_a \odot (\hat{v}_a - v_a)\|_2^2 / \max(\sum M_a, 1)`$
  - $`\mathcal{L}_{\mathrm{prior}} = \|\hat{v}_x - \hat{v}_x^{\,\mathrm{tea}}\|_2^2`$ (이미지 조건 유지 시에만)
  - $`\mathcal{L}_{\mathrm{gaze}}`$ — rendered hand 영역 주변 video-flow 오차 가중 (식 명시 없음)
  - $`\mathcal{L}_{\mathrm{Donk}} = \lambda_v (\mathcal{L}_{\mathrm{video}} + \lambda_g \mathcal{L}_{\mathrm{gaze}}) + \lambda_a \mathcal{L}_{\mathrm{action}} + \lambda_p \mathcal{L}_{\mathrm{prior}}`$

- 하이퍼:
  | 이름 | 값 | 출처 |
  |------|----|----|
  | 초기화 백본 | Wan2.2 TI2V-5B | §3.2 |
  | 이미지 drop 확률 | `0.30` | §3.2 |
  | optimizer | AdamW | §4 |
  | learning rate | $`2\times 10^{-5}`$ (constant) | §4 |
  | $`(\beta_1, \beta_2)`$ | `(0.9, 0.999)` | §4 |
  | $`\epsilon`$ | $`10^{-8}`$ | §4 |
  | weight decay | `0.01` | §4 |
  | gradient clip | `1.0` | §4 |
  | precision | bfloat16 | §4 |
  | effective batch | 64 clips (GPU당 1 clip × 64 GPU) | §4 |
  | 하드웨어 | 64× NVIDIA Hopper 96GB, FSDP2 | §4 |
  | $`\gamma_\ell`$ 초기값 | `0` | §3.2, Eq. (7) |
  | $`(\lambda_v, \lambda_g, \lambda_a, \lambda_p)`$ | (원문 미명시) | Eq. (10) |
  | anchor 주입 layer 집합 `S` | (원문 미명시) | §3.2 |
  | horizon `T` | (원문 미명시) | §3.1 |
  | flow-matching schedule | (원문 미명시) | §3.3 |

---

## 🎯 평가 메트릭

- **TI2VA 액션 (OakInk2, first-person)** — `Hand RMSE` · `ADE` · `FDE` · `DTW-S` · `DTW-L` (미터, lower↓) · `ROT` (도, geodesic, lower↓). best-of- $`K`$ , $`K\in\{5,10\}`$ , 예제당 10 futures. baseline: VITRA, Being-H0-1B/8B, DreamZero-alike. Donk-TI2VA: RMSE **0.238**, ADE K10 **0.049**.
- **TI2VA 비디오 (EgoDex/LOME, 1000 samples, 17 frames, 832×480)** — `PSNR↑` `SSIM↑` `LPIPS↓` `CLIP-I↑` `CLIP-S↑` `tLPIPS↓` `FVD↓`. baseline: Wan2.2-TI2V-5B / Wan2.1-I2V-14B / Wan2.1-VACE-14B. Donk: LPIPS **0.2992**, PSNR **19.84**.
- **T2VA (text-only)** — `FVD↓` `VLM judge↑` (0–5, 100 EgoDex 샘플) `CLIP-S↑` `tLPIPS↓`. baseline: Wan2.2-5B-I2V. Donk-T2VA: FVD **191.1**, judge **2.37**.
- **임계값** — 명시적 pass/fail threshold 없음; baseline 대비 상대 우위로 채점.

---

## ✨ 변경 의도 (intent)

기존 WAM 은 관측 조건부 정책 `p(video,action | text,observation)` 로 분포를 좁혔는데, Donk 는 초기 관측을 *옵션* 으로 두어 `p(video,action | text, optional observation)` 로 넓히고, 같은 single-stream joint denoiser 가 이미지 유무에 따라 정책(TI2VA)이자 데이터 엔진(T2VA)으로 작동하게 만듭니다. WorldVLA 식 autoregressive 통합과 달리 flow-matching 으로 video·action token 을 함께 denoise 하며, 사전학습 Wan 비디오 prior 를 (a) video-preserving 비대칭 attention, (b) zero-init gated anchor 주입, (c) frozen teacher prior loss 세 장치로 보존하면서 action head 를 얹는 것이 핵심 차별점입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 정밀 매핑은 어려움. Donk 는 video diffusion transformer(Wan2.2 5B) 기반 raw-pixel WAM 으로 lerobot 의 어떤 baseline(`pi0`/`pi05`/`smolvla`/`act`/`diffusion`)과도 백본 계열이 다릅니다. 가장 가까운 접점은 flow-matching action head 관점에서 `pi0`(flow-matching action expert)이지만, video 생성 스트림·Wan VAE·teacher prior 는 lerobot 에 대응물이 없어 부분 매핑에 그칩니다. `/implement-design` 이 최종 매핑 가능성을 판정합니다.

---

## 🚧 미해결 / 잠정

- loss 가중치 $`(\lambda_v, \lambda_g, \lambda_a, \lambda_p)`$ 와 $`\lambda_g`$ 의 $`\mathcal{L}_{\mathrm{gaze}}`$ 식 — 원문 미명시.
- anchor 주입 layer 집합 `S`, horizon `T`, MANO action 차원 `D`, 정규화 통계 — 원문 미명시 (가정으로 메움).
- `L_gaze` 의 정확한 가중 방식 ("rendered hand 영역 주변 가중") — 정성 서술만 있고 식 없음.
- T2VA initializer 의 구조·학습 손실 — "lightweight text-conditioned initializer" 외 상세 없음.
- flow-matching noise schedule · inference step 수 — 원문 미명시.
- 코드/가중치 미공개 → 구현 검증의 ground-truth 부재.
