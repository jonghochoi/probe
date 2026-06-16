# Design — You Don't Need Strong Assumptions: Visual Representation Learning via Temporal Differences

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | You Don't Need Strong Assumptions: Visual Representation Learning via Temporal Differences |
| 링크 | [arXiv:2606.15956](https://arxiv.org/abs/2606.15956) |
| 분석 문서 | [`analysis/2606.15956/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-16 |

---

## 🧮 데이터 계약

TDV 는 비디오에서 두 인접 프레임을 받아 *다음 프레임의 표현*을 예측하는 self-supervised 사전학습입니다. 시간 축은 의미 단위로 — 한 step 은 stride 로 떨어진 인접 프레임 쌍 $`(x_t, x_{t+1})`$.

- **입력** — `frame`: $`x_t, x_{t+1}`$, shape `(B, 3, H, W)` (본문 `H=W=224`), float, fixed stride $`\Delta t`$ (본문 0.25s) 로 한 clip 에서 샘플. center crop only, 증강 없음.
- **입력(파생)** — `rgb_diff`: $`\Delta x_t = x_{t+1}-x_t`$, shape `(B, 3, H, W)`, float, 정규화/clipping 없음(본문 `RGB difference clipping: no`). 본질적으로 low-rank.
- **중간 표현** — $`z_t = f_\theta(x_t)`$ : shape `(B, n, D)`, $`n`$ = patch 수 + [CLS] 1, $`D`$ = ViT 임베딩 차원(ViT-S/B). patch size 14.
- **출력(예측)** — $`\hat z_{t+1} = z_t + \Delta z_t`$ : shape `(B, n, D)`. teacher 타깃 $`z^{\text{teacher}}_{t+1} = \bar f(x_{t+1})`$ (EMA, stop-grad), 동일 shape.
- **출력(다운스트림)** — 학습 종료 후 산출물은 frozen **frame encoder** $`f_\theta`$ (또는 teacher $`\bar f`$). dense spatial task 는 이 backbone 위에 task head(UperNet / CroCo-DPT 등)를 붙여 사용.

---

## 🧰 모듈 인터페이스

```python
def frame_encoder(x: Tensor) -> Tensor:        # f_θ (ViT)
    """프레임 x:(B,3,H,W) → 토큰 표현 z:(B,n,D). n = patch 수 + [CLS]."""

def motion_encoder(dx: Tensor, z_t: Tensor) -> Tensor:   # m_φ
    """RGB 차분 dx:(B,3,H,W) → 잠재 변화 Δz:(B,n,D).
       현재 프레임 임베딩 z_t 로 cross-attention conditioning."""

def tdv_step(x_t, x_tp1, f_student, m_phi, f_teacher) -> Tensor:
    """단일 학습 step (Algorithm 1): z_t=f_student(x_t);
       dx=x_tp1-x_t; dz=m_phi(dx, z_t); z_hat=z_t+dz;
       z_tgt=sg(f_teacher(x_tp1)); return L_mse + L_dino."""

def dino_loss(z_hat: Tensor, z_tgt: Tensor) -> Tensor:
    """student/teacher projection 분포 p_s,p_t (temp τ_s,τ_t, teacher centering)
       사이 cross-entropy. [CLS] + 모든 patch token 에 적용."""

def ema_update(f_teacher, f_student, tau: float) -> None:
    """θ̄ ← τ·θ̄ + (1-τ)·θ. teacher 는 gradient 없음."""
```

- **frame_encoder** — student/teacher 두 copy. student 만 경사하강, teacher 는 EMA. 입출력 모두 token 열.
- **motion_encoder** — `dx` 와 `z_t` 를 cross-attention 으로 결합(z_t 가 key/value, [CLS] 포함이 성능에 기여). loss: `L_mse` + `L_dino` 가 student 인코더와 함께 갱신.
- **additive composition** — 학습 파라미터 없는 $`z_t + \Delta z_t`$ 덧셈. 합성 결과가 MSE·DINO 양쪽 loss 의 예측측 인자.
- **collapse 방지 계약** — teacher centering(running mean) + EMA + DINO CE 가 함께 있어야 비자명 타깃 유지. 셋 중 하나라도 빠지면 collapse 위험(분석 Table 4).

---

## ⛓️ 불변식·가정

- **(인과 가정)** — 인접 프레임은 시간적으로 가깝고 비디오는 temporal consistency 가 높아, 다음 프레임의 표현은 현재 표현 + 모션으로 예측 가능. 깨지면(stride 가 너무 커 incoherent jump) 학습 신호 무의미.
- **(차분의 low-rank 성)** — $`\Delta x_t`$ 는 프레임 자체보다 본질적으로 저차원(배경 불변, 움직이는 영역만 비영). 이 가정이 모션 인코더가 외형이 아니라 *변화*에 집중하게 만드는 근거.
- **(가산 분해 가능성)** — 표현 공간에서 "내용 $`z_t`$" 와 "변화 $`\Delta z_t`$" 가 덧셈으로 합성 가능하다는 가정. 비선형 합성이 아니라 덧셈으로 충분하다는 구조적 제약.
- **(non-collapse 조건)** — teacher 분포가 student 와 충분히 다르게 유지(느린 EMA)되고 centering 으로 한 mode 쏠림이 방지되어야 trivial 상수 해를 피함.
- **(stride 적정 범위)** — stride 가 너무 작으면 $`\Delta x_t \approx 0`$ (무신호), 너무 크면 incoherent — 의미 있는 모션 구조를 담는 중간 범위가 존재해야 함.

---

## 📊 하이퍼파라미터·손실

- 전체 손실: $`\mathcal{L} = \lambda_{\text{mse}}\,\mathcal{L}_{\text{mse}} + \lambda_{\text{dino}}\,\mathcal{L}_{\text{dino}}`$
  - $`\mathcal{L}_{\text{mse}} = \| \hat z_{t+1} - \text{sg}(z^{\text{teacher}}_{t+1}) \|_2^2`$ (Eq.4, all tokens)
  - $`\mathcal{L}_{\text{dino}} = -\sum_k p_t^{(k)} \log p_s^{(k)}`$ (Eq.5, [CLS] + all patch tokens)

| 이름 | 값 | 출처 |
|------|----|----|
| $`\lambda_{\text{mse}}`$ | `1.5` | §C.3, Table C.2 |
| $`\lambda_{\text{dino}}`$ | `1.5` | §C.3, Table C.2 |
| $`\tau_s`$ (student temp) | `0.1` | §3.3 / Table C.2 |
| $`\tau_t`$ (teacher temp) | `0.1` | §3.3 / Table C.2 |
| EMA momentum $`\tau`$ | `0.99` | Table C.2 |
| Projection head dim `K` | `32768` | Table C.2 |
| Architecture | `ViT-S / ViT-B` | Table C.2 |
| Patch size | `14` | Table C.2 |
| Optimizer | `AdamW` | Table C.2 |
| Learning rate | `1e-4` | Table C.2 |
| LR schedule | `cosine` | Table C.2 |
| Warmup epochs | `0.5` | Table C.2 |
| Weight decay | `0.01` | Table C.2 |
| Batch size (images) | `256` | Table C.2 |
| Epochs / steps | `20` / `~200,000` | §C.2 |
| Input resolution | `224×224` | Table C.3 |
| Frames sampled / clip | `16` | Table C.3 |
| Time between frames (stride) | `0.25` | Table C.3 |
| RGB difference clipping | `no` | Table C.3 |
| Spatial cropping | `center crop only` | Table C.3 |
| Augmentations (flip/jitter/mask) | `none` | Table C.3 |
| teacher centering | running mean (on) | §3.3 |

---

## 🎯 평가 메트릭

- **지표(주)** — dense spatial: semantic segmentation `mIoU`/`mAcc`(UperNet, frozen backbone), optical flow `EPE`(↓, CroCo+DPT fine-tune), stereo depth `Avg Err`/`bad@0.5px`/`bad@1px`(↓). **비교 baseline** — DINO, iBOT (동일 SSv2 사전학습·동일 task head).
- **지표(모니터/proxy)** — online ImageNet KNN Top-5(`k=20`), collapse 조기 탐지용. collapse 시 near-chance 이하.
- **지표(semantic, 약점 확인)** — ImageNet KNN/linear Top-5, SSv2 action recognition Top-5(V-JEPA frozen probe). TDV 는 여기서 baseline 에 크게 뒤짐(설계상 예상).
- **임계값/판정** — "avoids collapse"가 1차 게이트(KNN 이 chance 수준이면 실패). dense task 는 baseline 대비 동률~우위.

---

## ✨ 변경 의도 (intent)

기존 self-supervised 표현 학습(DINO/iBOT/contrastive/MAE)은 augmentation·masking·cropping 같은 *불변성 강요* inductive bias 로 학습 신호를 만들고, 그 과정에서 downstream 에 필요한 정보(공간·모션)를 구조적으로 폐기합니다. TDV 의 변경 의도는 그 가정 전부를 빼고, *유일하게* "과거가 미래를 야기한다"는 인과 가정만 남기는 것입니다. 핵심 메커니즘은 모션을 *버리지 않고* 모션 인코더로 명시 모델링한 뒤 $`z_t+\Delta z_t`$ 가산 합성으로 다음 프레임 표현을 예측하게 하는 것 — 이로써 dorsal-stream(공간·시간 대응) 정보가 보존됩니다(optical flow·stereo 에서 baseline 우위로 발현). 반대급부로 invariance 가 없어 semantic(ventral) 표현은 약해지는, *의도된* trade-off 입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 직접 대응 base 없음. TDV 는 로봇 정책(action expert)이 아니라 *vision encoder 사전학습 레시피*라, `pi0`/`act`/`diffusion` 류 policy family 와 1:1 매핑되지 않음. 가장 가까운 접점은 vendor 의 `vla_jepa` baseline(JEPA 잠재 예측 계열) — TDV 의 teacher-student + 잠재 예측 구조와 사촌 관계이나, TDV 는 action-free·additive motion 분해라는 차이. 실질적으로는 *관측 backbone 사전학습 전처리*로 lerobot 외부에서 인코더를 만들어 frozen feed 하는 형태가 현실적이며, in-foundry 포팅은 `UNMAPPABLE` 가능성이 높음(최종 판정은 `/implement-design`).

---

## 🚧 미해결 / 잠정

- **모션 인코더 정확한 아키텍처/용량** — cross-attention conditioning 이라는 계약은 명시되나, 레이어 수·차원 등 구체 스펙은 본문 표에 없음(§B.1 은 "작을수록 KNN 단조 감소"만). (원문에 명시 없음 — 가정으로 메움)
- **projection head 구조 세부** — DINO head 를 따른다고만 하고 hidden dim/bottleneck 구체값은 미명시. (원문에 명시 없음 — 가정으로 메움)
- **MSE 를 all tokens 에 거는 정규화 방식** — Algorithm 1 은 "MSE over all tokens"라 하나 token-wise 평균/합 여부는 식 수준에서만. (원문에 명시 없음 — 가정으로 메움)
- **stride 의 task 별 최적값** — 0.25s 는 SSv2 기준값이며 다른 데이터에서의 적정 stride 는 미탐색(저자도 민감도만 경고).
- **scale 거동** — SSv2 초과 데이터에서 개선 실패(§6). 더 큰/고품질 비디오 + 재튜닝 시 거동은 미해결.
