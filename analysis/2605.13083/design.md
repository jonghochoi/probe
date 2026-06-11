# Design — TouchAnything: A Dataset and Framework for Bimanual Tactile Estimation from Egocentric Video

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | TouchAnything: A Dataset and Framework for Bimanual Tactile Estimation from Egocentric Video |
| 링크 | [arXiv:2605.13083](https://arxiv.org/abs/2605.13083) |
| 분석 문서 | [`analysis/2605.13083/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-10 |

---

## 🧮 데이터 계약

시간 축은 클립 단위 $`T`$ (논문 기본 $`T=8`$, frame interval 2). 뷰 집합 $`\mathcal{V}\subseteq\{V^{ego},V^{wL},V^{wR}\}`$ 는 임의 부분집합(ego 는 항상 포함).

- **입력 — Multi-view RGB**: 뷰별 `(B, T, 3, 224, 224)`, float, $`224\times224`$ 리사이즈. 가용 뷰만 전달(누락 뷰는 마스킹/생략).
- **입력 — Bimanual hand pose** `P`: shape `(B, T, 42, 3)`, float (WiLoR/Rokoko 42 joints = 양손 21+21). 단위는 원문 명시 없음(Vive 좌표계 정렬, `aligned_to_vive`).
- **출력 — Bilateral pressure map** `M̂`: shape `(B, T, 2, 21, 21)`, float, sigmoid 로 $`[0,1]`$ 정규화. 채널 2 = (left, right), 각 손 canonical $`21\times21`$ hand-shaped grid.
- **GT 압력 전처리** — raw 256-d(논리적 $`16\times16`$) → hand-specific JSON 매핑으로 $`21\times21`$ grid, 오른손 수평 미러링, invalid 위치 NaN, first-frame baseline 차감(조건부), broken column interpolation, tactile/bending 분리 정규화 후 $`[0,1]`$.
- **시각 토큰** — 공유 DINOv2-ViT-B/14 → 프레임당 `N=256` patch tokens, dim `D=768`.

---

## 🧰 모듈 인터페이스

```python
def shared_vision_encoder(views: dict[str, Tensor]) -> dict[str, Tensor]:
    """각 뷰를 frozen DINOv2-ViT-B/14 로 인코딩 후 학습형 view embedding e_v 가산.
       반환: 뷰별 F_v (B, T, N=256, D=768)."""

def cross_view_attention(F: dict[str, Tensor]) -> dict[str, Tensor]:
    """뷰별 MeanPool → summary s_v, 경량 CrossViewTransformer 로 뷰 간 정보 교환.
       반환: 보정된 summary ŝ_v."""

def gated_view_fusion(F: dict[str, Tensor], s_hat: dict[str, Tensor]) -> Tensor:
    """w_v = softmax(MLP(ŝ_v)) 가중치로 patch feature 가중합.
       반환: F_fused (B, T, N, D) — 단일 뷰와 동일 shape (누락 뷰 강건)."""

def temporal_transformer(F_fused: Tensor) -> Tensor:
    """windowed temporal transformer 로 시간 동역학 포착. 반환: H (B, T, N, D)."""

def pose_encoder(P: Tensor) -> Tensor:
    """양손 pose (B,T,42,3) → per-joint feature G (B,T,42,D)."""

def pose_vision_fusion(G: Tensor, H: Tensor) -> Tensor:
    """CrossAttn(Q=G, K=H, V=H) — 각 joint 가 관련 시각 patch 에 attend.
       반환: Z (B,T,42,D)."""

def tactile_decoder(Z: Tensor) -> Tensor:
    """Z 를 left(1–21)/right(22–42) 로 분할, 각 MLP+reshape+sigmoid.
       반환: M̂ (B,T,2,21,21) in [0,1]."""
```

- 손실/옵티마이저 계약: `tactile_decoder` 출력 `M̂` 과 GT `M` 으로 contact-aware weighted regression(아래 📊) 계산, AdamW + cosine schedule 로 backward(시각 backbone 은 frozen → no grad).

---

## ⛓️ 불변식·가정

- (가정 1) — ego 뷰는 학습·추론 모두 **항상 존재**한다(view dropout 이 ego 를 절대 드롭하지 않음). 이것이 깨지면 입력 정합·gating 정규화가 무효.
- (가정 2) — `gated_view_fusion` 출력 `F_fused` 의 shape 는 가용 뷰 수와 무관하게 단일 뷰와 동일 `(B,T,N,D)` 이어야 한다(하류 모듈 호환 + 누락 뷰 graceful degradation).
- (가정 3) — 양손 압력맵은 공통 canonical hand-shaped 좌표계를 공유한다(오른손 미러링). 좌/우가 같은 격자 의미를 가진다는 전제가 decoder 의 weight-tie 해석을 가능케 함.
- (가정 4) — 촉각 GT 는 극히 희소(대부분 0)하다 → 가중치 없는 회귀는 all-zero 로 붕괴한다(접촉 가중 손실의 정당화).
- (가정 5) — 뷰 간 시간 동기화가 frame-level 로 정확하다(30Hz 공통 timeline) — cross-view/pose-vision fusion 이 동일 시점 가정에 의존.

---

## 📊 하이퍼파라미터·손실

- 손실 식:

$$\mathcal{L}=\lambda_{mse}\mathcal{L}_{MSE}+\lambda_{l1}\mathcal{L}_{L1}+\lambda_{tv}\mathcal{L}_{TV}(\hat{\mathbf{M}})$$

  접촉 픽셀(압력 > 0.1)에 contact-region weight 적용(all-zero 붕괴 방지). $`\mathcal{L}_{TV}`$ 는 공간 smoothness.

- 평가 지표 식 (Volumetric IoU):

$$IoU_{vol}=\frac{\sum^{i,j}min(P_{i,j},\hat{P}_{i,j})}{\sum^{i,j}max(P_{i,j},\hat{P}_{i,j})}$$

- 하이퍼:

  | 이름 | 값 | 출처 |
  |------|----|----|
  | $`\lambda_{mse}`$ | `1.0` | §3.3 / §9.6 |
  | $`\lambda_{l1}`$ | `0.5` | §3.3 / §9.6 |
  | $`\lambda_{tv}`$ | `0.01` | §3.3 / §9.6 |
  | `contact_weight` | `3.0` | §3.3 / §9.6 |
  | `contact_threshold` | `0.1` | §3.3 / §9.6 |
  | `view_dropout_p` (각 손목 뷰) | `0.3` | §3.3 / §4.1 / §9.5 |
  | `T` (clip 길이) | `8` (interval 2) | §4.1 |
  | optimizer | `AdamW`, betas `(0.9,0.999)` | §9.6 |
  | learning rate | `5e-5` (cosine, warmup 10ep, min `1e-6`) | §4.1 / §9.6 |
  | weight decay | `0.05` | §4.1 |
  | epochs | `25` | §4.1 |
  | effective batch | `288` (6 GPU × 16 × accum 3) | §9.6 |
  | backbone | frozen `DINOv2-ViT-B/14` (`N=256`, `D=768`) | §4.1 / §9.2 |
  | glove color aug | `p=0.2` | §9.6 |

---

## 🎯 평가 메트릭

- **지표** — `Temporal Accuracy`↑ / `Contact IoU`↑ / `Volumetric IoU`↑ / `MAE`↓ (PressureVision [34] 따름)
- **임계값** — 접촉 이진화 $`\text{pressure} > \tau`$ (Contact detection 보조 과제); Contact IoU 는 Volumetric IoU 의 상한
- **비교 baseline** — `Ego-only`(손목 뷰 없는 동일 아키텍처); 보고는 상대 % 변화(↑/↓ vs Ego-only)
- **프로토콜** — episode 단위 80/10/10 split, test 를 seen-object / unseen-object 로 분할; 동일 checkpoint 로 ego-only·single-wrist·full multi-view 를 같은 split·전처리·메트릭에서 비교

---

## ✨ 변경 의도 (intent)

기존 vision-to-touch(PressureVision: 단일 RGB / EgoPressure: 단일 ego·손-표면)는 egocentric 양손 조작에서 접촉면이 가려지면 모델 용량과 무관하게 무너진다. TouchAnything 의 의도는 **모델을 키우는 대신 접촉면을 직접 보는 손목 뷰를 보완 입력으로 추가**하고, 그 뷰를 cross-view attention + gated fusion 으로 ego 뷰에 주입하는 것이다. 동시에 배치 환경마다 카메라 구성이 다른 현실을 위해 **view dropout** 으로 단일 모델이 임의 뷰 부분집합(ego-only ~ full)에서 구조 변경 없이 동작하게 한다 — 즉 "occlusion 은 더 나은 모델이 아니라 보완 시점으로 푼다 + 시점 가용성은 dropout 으로 흡수한다"가 핵심 차별점이다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 직접 대응 base 없음. 본 과제는 정책(action) 학습이 아니라 **vision-to-touch 회귀(perception)** 이라 `pi0`/`act`/`diffusion` 등 action-expert family 와 목적이 다름. 굳이 매핑하면 멀티뷰 이미지 인코딩 + 토큰 fusion 부분이 VLA 의 observation encoder 와 유사하나, 출력이 action chunk 가 아니라 $`21\times21`$ 압력맵이라 decoder/loss 가 비호환. `/implement-design` 에서 `🚧 매핑 불가` 가 합리적 결과일 수 있음.

---

## 🚧 미해결 / 잠정

- hand pose `P` 의 단위/정규화 통계는 본문에 수치로 명시되지 않음(Vive 좌표계 정렬만 기술) — 구현 시 데이터셋 통계로 가정 필요.
- `cross-view transformer`/`temporal transformer`/`pose encoder` 의 레이어 수·헤드 수 등 세부 폭은 원문 미명시(경량(lightweight)이라고만 기술).
- `gated_view_fusion` 에서 `softmax` 가 뷰 축 정규화인지 채널별인지 식 (5) 만으로는 잠정 — 뷰 축 가중(∑ w_v · F_v)로 해석.
- 압력의 절대 단위/캘리브레이션 부재(정규화 $`[0,1]`$) — 절대 force supervision 으로 쓰려면 별도 매핑 필요(가정으로 메움).
- Project page 외 코드/데이터 라이선스는 공개 시점 미확인 — "공개 예정"으로만 잠정 기록.
