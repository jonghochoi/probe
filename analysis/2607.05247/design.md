# Design — Vision Pretraining for Dense Spatial Perception

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Vision Pretraining for Dense Spatial Perception |
| 링크 | [arXiv:2607.05247](https://arxiv.org/abs/2607.05247) |
| 분석 문서 | [`analysis/2607.05247/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-07-07 |

---

## 🧮 데이터 계약

- **입력 — image (view)**: shape `(B, 3, H, W)`, float32, ImageNet 정규화. global crop `256×256`(사전학습)·`512×512`(고해상 적응), local crop `112×112`. patch size `P=16`, 토큰 grid $`N = (H/P)\cdot(W/P)`$.
- **중간 — patch/class 토큰**: class 토큰 `(B, D)`, patch 토큰 `(B, N, D)`. ViT-g $`D\approx 1536`$ (원문 미명시, ViT-g 관례).
- **중간 — boundary field** (교사가 온라인 생성): 채널 $`c\in\{d, \theta, \phi^{1}, \phi^{2}\}`$, sub-token stride `s=2` 로 토큰당 `s×s` tile 위치. 각 위치·채널은 `K=32` bin 위 범주형 분포 `(…, 4, K)`.
- **중간 — boundary 토큰 마스크**: $`\mathcal{B} \subseteq \{1..N\}`$ (교사 경계가 지나가는 토큰), $`\mathcal{M}^{+} = \mathcal{M} \cup \mathcal{B}`$.
- **출력 — 학습 신호**: scalar 손실(식 아래). 추론 시 frozen backbone 의 patch/class feature `(B, N, D)` / `(B, D)` 가 downstream(depth·seg·VOS) linear/label-propagation head 의 입력.
- **corner 점** (frozen 단일 블록 ViT): 희소 점 집합, 교사 필드와 짝지어 선분 decode 에만 사용(backbone 학습 신호 아님).

---

## 🧰 모듈 인터페이스

```python
def boundary_head(patch_tokens):  # (B, N, D) -> per-channel bin logits
    """토큰별 3-layer MLP → s×s tile 위치로 unfold → 위치 feature ℓ2-정규화
       → 채널별 K개 unit-norm bin 프로토타입과 cosine 점수. 반환: (B, N, s*s, 4, K)."""

def make_boundary_targets(teacher, view, corner_pts):  # -> validated field + B set
    """교사 online 타깃 생성 4단계: (i) dense boundary field 예측,
       (ii) corner 점과 pairing, (iii) vote-aggregation 으로 후보 선분 L decode,
       (iv) a-contrario(NFA) 로 걸러 survivor 를 clean 필드로 re-render.
       반환: 범주형 타깃 필드 ȳ^c(p), 경계 토큰 집합 B (stop-gradient)."""

def soft_categorical_label(a_c, K, tau_l, circular=False):  # -> (K,)
    """검증된 교사 값 a^c(p) 를 bin 중심 거리 기반 soft one-hot 으로 인코딩.
       θ 채널은 circular=True (호 거리). 좁은 라벨(몇 bin 폭) 유지."""

def total_loss(student, teacher, view_pair, masks, targets):  # -> scalar
    """L = L_DINO + λ_i·L_iBOT + λ_b·L_bnd + λ_k·L_KoLeo.
       교사 분포·타깃은 centering+sharpening, stop-gradient. 스텝 후 EMA 업데이트."""
```

- `boundary_head` — dense head 인데 **경계 토큰에만** 적용(비용이 이미지 크기가 아니라 $`|\mathcal{B}|`$ 에 비례). bias-free unit-norm 선형층으로 logit 이 cosine(경계지어짐) → 붕괴 억제. 교사·학생 동일 설계, 교사는 EMA.
- `make_boundary_targets` — teacher-side 전 과정이 batched CUDA(per-image 루프·host sync 없음). label 구성 + circular arc-distance + categorical CE 를 fused kernel 로.
- `total_loss` — 경계 토큰은 `L_iBOT`(semantic)와 `L_bnd`(geometric) 이중 지도. non-boundary 위치 타깃 = **균등 무작위**(상수 배경 아님).

---

## ⛓️ 불변식·가정

- **(중복성)** 경계 필드는 over-parameterized — support 영역 $`S_\ell = \{p : d_p \leq \tau_d\}`$ 의 단일 픽셀도 전체 선분을 복원할 정보를 담는다. 이 many-pixels-one-segment 중복이 noisy·미학습 필드의 vote-aggregation decode 를 가능케 함(깨지면 부트스트랩 붕괴).
- **(corner 앵커)** corner 점이 고정되면 무작위 필드값조차 corner-앵커 선분으로 decode 된다(Finding 1). corner 없으면 어떤 decode 도 실패 — corner detector 강건성이 전제.
- **(범주형 안정성)** boundary 를 이산 bin 분포로 두면 semantic self-distillation 의 centering/sharpening 이 그대로 적용된다. 연속 회귀(`ℓ1`/`ℓ2`)는 EMA 루프에서 drift·collapse 하므로 금지.
- **(균등 = 귀무가설)** "구조 없음"은 bin 위 균등분포이며, 균등에서의 이탈이 곧 NFA(a-contrario)가 재는 증거. 배경 클래스 불필요, 검증이 표현에 native.
- **(라벨 폭)** soft 라벨은 좁아야 한다 — 과도 smoothing 은 모든 타깃을 균등으로 밀어 신호 소실. $`\tau_\ell`$ 가 이 폭을 지배.
- **(교사 우월성)** 교사가 좋은 경계 예측기일 필요는 없고, EMA 로 학생보다 "약간 나으면" 충분 — 타깃이 모델과 공진화.

---

## 📊 하이퍼파라미터·손실

- 전체 손실: $`L = L_{DINO} + \lambda_i\,L_{iBOT} + \lambda_b\,L_{bnd} + \lambda_k\,L_{KoLeo}`$
- 경계 손실: $`L_{bnd} = -\frac{1}{|B|} \sum_{p\in B} \sum_c \bar{y}^c(p)^\top \log \hat{y}^c(p)`$ (§3.3, Eq. 9)
- soft 라벨: $`\bar{y}^c_k(p) \propto \exp(-\delta^c(k, a^c(p))^2 / \tau_\ell)`$ (§3.3, Eq. 8)

| 이름 | 값 | 출처 |
|------|----|----|
| $`\lambda_i`$ (iBOT), $`\lambda_b`$ (boundary) | `1`, `1` | §4.3 |
| $`\lambda_k`$ (KoLeo) | `0.1` | §4.3 |
| `P` (patch size) | `16` | §3.2, §4.3 |
| `s` (boundary head stride) | `2` | §3.4, §4.3 |
| `K` (bin 수/채널) | `32` (PoC 128→32, quality-neutral) | §4.3 |
| boundary head | 3-layer per-token MLP, head dim `512` | §4.3 |
| backbone | ViT-g/16 ~1.1B, SwiGLU, RoPE(fp32), register 4 | §4.3 |
| optimizer / batch | AdamW / global `3072` | §4.3 |
| LR 스케일 | $`\sqrt{bs/1024}`$ × cosine (linear warmup) | §4.3 |
| weight decay | $`0.04 \to 0.2`$ (cosine) | §4.3 |
| teacher temp | $`0.04 \to 0.07`$ (첫 30k) | §4.3 |
| EMA 모멘텀 | $`0.994 \to 1.0`$ | §4.3 |
| 스케줄 | 300k 사전학습 + 100k Gram anchoring + 100k 고해상(512px) | §4.3 |
| crop | global `256`, local `112` px | §4.3 |
| $`\tau_\ell`$ (라벨 온도), $`\tau_d`$ (support 임계), NFA 임계 | (원문 미명시 — 값 비공개) | §3.3, App.B |

---

## 🎯 평가 메트릭

- **Dense depth (frozen + single linear decoder)** — $`\text{RMSE}\downarrow`$ (NYUv2, KITTI). 헤드라인: LingBot-Vision ViT-g NYUv2 `0.296`(7B DINOv3 `0.309` 상회). PoC 는 $`\delta_1\uparrow`$ 병기.
- **Semantic segmentation (frozen + single linear)** — `mIoU` (ADE20k / Cityscapes / VOC12).
- **Video object segmentation (training-free label propagation)** — `J&F-Mean` (DAVIS-2017, YouTube-VOS).
- **Global recognition** — ImageNet-1K `linear` / `k-NN` top-1(trade-off 축, 열위 허용).
- **Downstream depth completion** — $`\text{RMSE}\downarrow / D_{105}\uparrow`$ (14 벤치, block-mask/sparse/real-sensor). LingBot-Depth 2.0 = LingBot-Vision 인코더 초기화.
- **비교 baseline** — DINOv2 / DINOv3(및 7B·ViT-H+) / V-JEPA 2.1 / SigLIP 2 / AM-RADIOv2.5 (동일 patch-token 해상도 정합).

---

## ✨ 변경 의도 (intent)

기존 마스킹 사전학습(iBOT/MAE/JEPA)이 "무엇을 마스킹할지"에 예외 없이 **무작위**로 답하는 것을, 이미지의 **경계가 결정**하게 바꾸는 것이 핵심 변경입니다. (1) 교사가 스스로 발견한 경계 토큰을 학생 마스크에 강제로 넣어(boundary forcing) 가장 비중복적 정보를 복원 대상으로 만들고, (2) 마스킹 토큰을 geometry 로 라우팅해 경계 토큰엔 semantic + 범주형 geometric 이중 지도를, 나머지엔 semantic 만 부여합니다. 연속 필드 회귀의 붕괴는 **범주형 재파라미터화**로 피하고(centering/sharpening 상속), 균등분포가 곧 a-contrario 귀무가설이 되어 검증이 공짜로 딸려옵니다. 결과적으로 dense 공간 구조가 사전학습의 **목표 그 자체**가 되어, 후처리 upsampler·Gram anchoring 같은 retrofit 에 의존하던 dense 품질을 직접 최적화합니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 이 방법은 VLA 정책이 아니라 **frozen vision 인코더 사전학습 알고리즘**입니다. lerobot 의 정책 family(`pi0`/`pi05`/`smolvla`/`act`/`diffusion`) 중 직접 대응은 없고, 매핑 가능성은 두 갈래: (a) 사전학습된 LingBot-Vision 인코더를 정책의 **관측 vision backbone**(예: `smolvla`/`pi0` 의 image encoder 슬롯)으로 교체 — 학습 알고리즘 이식이 아니라 가중치 drop-in; (b) masked-boundary-modeling **사전학습 loop 자체**는 lerobot 의 정책 학습 스코프 밖(별도 SSL 파이프라인). `/implement-design` 가 실제 포팅 가능 여부를 판정 — drop-in 인코더 경로가 유일한 현실적 매핑, SSL 목표 자체는 `🚧 매핑 불가` 가능성 높음.

---

## 🚧 미해결 / 잠정

- $`\tau_\ell`$(라벨 온도)· $`\tau_d`$(support 임계)·NFA 임계·soft-label bin 폭의 구체 값이 본문/부록에 수치로 공개되지 않아 재현 시 재튜닝 필요(붕괴/신호소실 경계를 지배).
- corner-point detector(frozen 단일 블록 ViT)의 **사전학습·초기화 절차**가 본문에 얕게 서술 — 방법의 부트스트랩 전제인데 재현 스펙이 불완전.
- vote-aggregation decode 와 a-contrario 검증의 정확한 알고리즘 상수(App.B "Implementation constants")가 본문 텍스트로는 부분 노출 — 커스텀 CUDA 커널 공개 여부 미확정.
- ViT-g hidden dim `D`, prototype 수 `C`(DINO)·iBOT bin 수 등 일부 head 차원은 DINOv2/DINOv3 관례로 가정(원문 명시 없음).
- 사전학습 corpus(161M)·depth corpus(150M) 비공개 → 데이터-방법 이득 분리는 외부 독립 재현 불가.
