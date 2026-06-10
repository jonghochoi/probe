# Design — RGB-S: Image-Aligned Tactile Saliency for Robust Dexterous Manipulation

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | RGB-S: Image-Aligned Tactile Saliency for Robust Dexterous Manipulation |
| 링크 | [arXiv:2606.08765](https://arxiv.org/abs/2606.08765) |
| 분석 문서 | [`analysis/2606.08765/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-10 |

---

## 🧮 데이터 계약

시간 축은 의미 단위(`T_obs` 관측 horizon, `T_action` 예측 chunk)로 기록합니다. `H,W` 는 이미지 해상도(논문 $`224\times224`$).

- **입력 (RGB)** — `I`: shape `(B, T_obs, n_cam, 3, H, W)`, float, ImageNet/사전학습 백본 정규화. center-crop 후 `224×224` resize.
- **입력 (proprioception)** — `s`: shape `(B, T_obs, 22)`, float (arm 6 + hand 16 joint). 정규화 통계는 (원문에 명시 없음 — 가정으로 메움: 데이터셋 평균/표준편차).
- **입력 (tactile)** — `f`: shape `(B, T_obs, M)`, float, `M=44`(taxel 32 + FSR 12). 노드별 스칼라 힘/접촉 강도. 정규화는 모듈 내부에서 $`\tilde{f}=\tanh(\gamma f/F_{\mathrm{limit}})`$.
- **입력 (kinematics / camera, 비학습)** — proprio `s` 로부터 FK; 센서 local offset `L_i`(고정), 카메라 외부 `R^c,t^c` + 내부 `K^c`(캘리브레이션 상수).
- **중간 산출 (saliency)** — `S`: shape `(B, T_obs, n_cam, 1, H, W)`, float `[0,1]` 범위(force-modulated, `max` 집계로 bounded).
- **증강 관측** — `X = Concat(I, S)`: shape `(B, T_obs, n_cam, 4, H, W)`.
- **출력 (action)** — `a`: shape `(B, T_action, 22)`, float (arm 6 + hand 16 target command). 백본별 horizon: BC-MLP `T_action=1`, ACT/DP `T_action≈16–24`.

---

## 🧰 모듈 인터페이스

```python
def render_tactile_saliency(f, s, cam_params, sensor_offsets,
                            sigma, gamma, f_limit, H, W) -> "S":
    """촉각 스칼라 f 를 FK+카메라 투영으로 이미지 평면 force-modulated
    Gaussian saliency map S (n_cam×1×H×W) 로 렌더링. 학습 파라미터 없음."""
```

- 역할: 식 (2)(3)(4) 의 deterministic 정합. 입력 = 촉각 `f`, proprio `s`, 카메라/센서 기하 상수. 출력 = saliency map `S`. loss/optimizer 와 무관(전처리).

```python
def rgbs_encoder_first_conv(I, S, W_rgb, W_s) -> "z":
    """첫 conv 를 3→4 채널로 확장. z = W_rgb * I + W_s * S.
    W_s 는 0 으로 초기화(zero-init), 학습 가능."""
```

- 역할: 식 (5). 사전학습 RGB 가중치 `W_rgb` + zero-init saliency 가중치 `W_s`. 이후 백본(ResNet-18 trunk)은 원본과 동일. 출력 feature map → spatial softmax(`K=32`) → 64-d/cam → linear+ReLU.

```python
def build_global_condition(rgbs_feats, other_modalities, T_obs) -> "g":
    """카메라별 RGB-S 특징 + 나머지 모달리티를 concat 해 관측 horizon
    길이의 global condition 시퀀스 g 를 구성."""
```

- 역할: downstream 정책(BC-MLP/ACT/DP)의 global condition. 손실은 정책 백본 소유(MSE / L1+KL / DDPM).

---

## ⛓️ 불변식·가정

- (가정 1) — **Zero-init 동일성**: $`\mathbf{W}_{s}=\mathbf{0}`$ 초기화 시 RGB-S 인코더 출력은 원본 RGB 인코더와 *기능적으로 동일*. 깨지면 사전학습 prior 보존 주장이 무효(식 5).
- (가정 2) — **기하 정합 유효성**: FK + 캘리브레이션 오차가 작아 투영 픽셀 $`\mathbf{p}^{c}_{i,t}`$ 가 실제 접촉 위치에 충분히 근접. Table 4 기준 가림 조건에서 offset < 25px 이내라야 이득 유지.
- (가정 3) — **이산 노드 + 스칼라 힘**: 촉각이 `M` 개 이산 노드의 스칼라 힘/강도로 표현 가능. 조밀 변형장 센서에는 직접 성립하지 않음.
- (가정 4) — **Bounded saliency**: $`\max`$ 집계 + $`\tanh`$ 정규화로 `S` 값이 겹침에도 `[0,1]` 유지.
- (가정 5) — **카메라 가시성**: 이미지 경계 밖 투영 노드는 폐기($`\mathcal{V}^{c}_{t}`$)되므로, 유효 saliency 는 카메라 시야 내 접촉에 한정.

---

## 📊 하이퍼파라미터·손실

- 정규화: $`\tilde{f}_{i,t}=\tanh\left(\gamma f_{i,t}/F^{i}_{\mathrm{limit}}\right)`$
- Saliency 렌더링: $`\mathbf{S}^{c}_{t}(u,v)=\max_{i\in\mathcal{V}^{c}_{t}}[\tilde{f}_{i,t}\exp(-((u-u^{c}_{i,t})^{2}+(v-v^{c}_{i,t})^{2})/(2\sigma^{2}))]`$
- 첫 레이어: $`\mathbf{z}^{c}_{t}=\mathbf{W}_{\mathrm{rgb}}\ast\mathbf{I}^{c}_{t}+\mathbf{W}_{s}\ast\mathbf{S}^{c}_{t}`$, $`\mathbf{W}_{s}=\mathbf{0}`$ at init
- 손실: 정책 백본 소유 — BC-MLP=MSE, ACT=L1 masked recon + KL, DP=DDPM(100 step)

  | 이름 | 값 | 출처 |
  |------|----|----|
  | `sigma_min` / `sigma_max` (sim) | `4` / `12` | §A.1, 식 (6) |
  | `gamma` (force scale) | (원문 미명시 — 수식 기호만) | §3.2 |
  | `F_limit` (센서 포화) | 센서별 상수 (원문 미명시) | §3.2 |
  | `K` (spatial softmax points) | `32` (→ 64-d/cam) | §3.3 |
  | image resolution | `224×224` | §A |
  | `M` (tactile nodes) | `44` (taxel 32 + FSR 12) | §A |
  | DP obs/pred/exec | `5 / 24 / 16` | Table 7 |
  | DP optimizer / lr / wd | `Adam` / `1e-4` / `1e-6` | Table 7 |
  | ACT lr | `1e-5` | Table 7 |
  | train steps / batch | `120K` / `64` | Table 7 |
  | DP U-Net channels | `[512,1024,2048]`, kernel `5` | Appendix E |

---

## 🎯 평가 메트릭

- **지표** — task success rate (%) · **조건** — Normal vs Occluded(과제 관련 영역 검은 마스크, 평가 시에만) · **비교 baseline** — Vision-Only / Concat / FiLM / CLIP-style / Cross-Attn.
- 핵심 주장 임계: 실제 로봇 가림 조건 +26.7%p (RGB-S 51.7% vs 최강 암시적 baseline Cross-Attn 25.0%, Table 2).
- 보조 분석: 렌더링 ablation(Table 3), 공간 정합 민감도(Table 4, offset 0/25/50/100px), 융합 위치(Table 5, early/intermediate/late), 효율(Table 6, ms/step).

---

## ✨ 변경 의도 (intent)

기존 비주오택타일 융합은 촉각-시각 대응을 latent 공간에서 *암시적으로* 학습(concat/FiLM/CLIP/cross-attention)하거나 *명시적 3D 점군*으로 들어 올립니다. RGB-S 는 제3의 노선 — 촉각을 FK+캘리브레이션으로 RGB 이미지 평면에 force-modulated Gaussian saliency 로 투영해, 학습 없이 기하적으로 시각-촉각 대응을 못 박습니다. 사전학습 2D 백본을 그대로 재사용하되 첫 conv 를 zero-init 채널로 확장해 prior 를 초기 시점에 보존하고, 3D 점군 분기의 depth 센싱·전처리 비용 없이 명시 grounding 의 가림 강건성을 얻습니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 논문 구현 자체가 LeRobot 기반(Appendix E)이라 매핑이 직접적입니다. downstream 정책은 `diffusion`(DP, 실제 로봇·ablation 주력) / `act`(ACT) family 와 가깝고, BC-MLP 는 경량 회귀 헤드. RGB-S 의 변경 지점은 정책이 아니라 **시각 인코더 입력단** — 관측 전처리에 saliency 렌더러를 추가하고 첫 conv(또는 patch-embed)를 4채널 zero-init 으로 확장하는 위치. 구체 base 좌표(file:line)는 `/implement-design` 가 결정.

---

## 🚧 미해결 / 잠정

- `gamma`(force scale)와 `F_limit`(센서 포화 한계) 의 실제 값은 본문에 수식 기호로만 등장 — 데이터/센서별 캘리브레이션으로 가정.
- 실제 환경 `sigma` 값(고정 vs force-dependent)은 §A.1 의 force-dependent 식 (6)이 sim 한정으로 기술됨 — 실제 로봇 `sigma` 설정 (원문에 명시 없음 — 가정으로 메움).
- proprioception/action 정규화 통계의 출처 미명시 — 데이터셋 전체 평균/표준편차로 가정.
- 카메라 view 수 `n_cam` = 실제 2(RealSense D435 ×2); 시뮬레이션 view 수는 명시 없음 — 동일 인터페이스로 가정.
- `K^c` 투영의 동차좌표 정규화(depth division) 세부는 식 (3)에서 $`\sim`$ 로만 표기 — 표준 핀홀 정규화로 가정.
