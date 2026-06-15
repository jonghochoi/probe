# Design — FTP-1: A Generalist Foundation Tactile Policy Across Tactile Sensors for Contact-Rich Manipulation

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | FTP-1: A Generalist Foundation Tactile Policy Across Tactile Sensors for Contact-Rich Manipulation |
| 링크 | [arXiv:2606.13102](https://arxiv.org/abs/2606.13102) |
| 분석 문서 | [`analysis/2606.13102/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-15 |

---

## 🧮 데이터 계약

시간 축은 의미 단위(`T_action` = action horizon $`H`$)로 기록합니다. 배치 `B`.

- **입력 — 언어** `ℓ`: 토큰화된 instruction (GPT-4o rewrite 로 다양화된 자연어). shape `(B, L_text)`, int token ids.
- **입력 — RGB** `I_t`: (멀티뷰) 이미지, shape `(B, N_cam, 3, H_img, W_img)`. π0.5 vision encoder 전처리 따름.
- **입력 — proprioception** `s_t`: 상태 벡터, shape `(B, D_state)`. Fourier 인코딩 후 z-score 정규화(데이터셋별 통계).
- **입력 — 촉각** `X_t`: 센서별 raw 신호를 MTTS 기능 영역으로 그룹화한 가변 집합. 영역별 관측 타입 ∈ {image `(H,W,C)` / array `(H,W,D)` / state `(D,)`}. image 는 `224×224` resize.
- **출력 — action chunk** $`\hat{\mathbf{A}}_{t:t+H-1}`$: shape `(B, H, D)`, UAS layout(좌/우팔 + 머리 + 보조). z-score 정규화 공간에서 예측, 미지원 차원은 마스크 $`\mathbf{M}\in\{0,1\}^{D}`$ 로 제외. flow-matching 으로 생성.
- **MTTS 토큰** (내부 계약): 24개 functional-area 슬롯, 영역당 1 토큰. 슬롯 0–14 손 내부 영역, 15–20 손목·손가락 F/T, 21–23 예약. 평행 그리퍼는 슬롯 0(엄지팁)·1(검지팁)에 매핑. 좌/우손 별도 functional-area embedding.

---

## 🧰 모듈 인터페이스

```python
def tactile_encoder(x_area, obs_type: str) -> Tensor:  # -> (B, d_token)
    """한 functional-area 신호를 MTTS 토큰 1개로 사영. obs_type ∈ {image, array, state}.
       image: sensor-specific ViT(depth3,w768,h12) -> shared T3 Transformer(depth9,w768,h12) [CLS].
       array: signal-dim Fourier-encode+concat -> 3-layer CNN -> 2-layer ReLU MLP.
       state: Fourier-encode+concat -> 3-layer ReLU MLP.
       동일 shape 의 영역끼리 인코더 공유."""

def mtts_assemble(area_tokens: dict[int, Tensor], hand: str) -> Tensor:  # -> (B, N_slot, d)
    """영역 토큰을 24-slot 으로 배치, LayerNorm -> 공유 functional-area embedding 가산
       (좌/우손 분리) -> 2-layer GELU MLP 로 tactile expert 차원 정렬."""

def proprio_injector(s_t, t_flow) -> Tensor:  # adaptive RMSNorm 파라미터
    """proprio Fourier-encode -> 3-layer ReLU MLP -> LayerNorm,
       flow-matching timestep feature 와 concat -> attention block 에 adaptive RMSNorm 주입."""

def policy(ℓ, I_t, s_t, X_t) -> Tensor:  # -> (B, H, D) action chunk
    """VLM expert(image+language) -> action expert(flow-matching) 가
       tactile expert(300M Transformer; MTTS 토큰 처리) 를 단방향 attend.
       VLM/action expert = π0.5 초기화, tactile expert/injector/projector = scratch."""
```

- **tactile expert** — width 1024, depth 18, MLP 4096, head 8, head dim 256(≈300M). 모든 센서 공유; action expert 가 attend, 역방향 없음.
- **호출 계약** — action expert ← (VLM expert 출력) + (tactile expert 출력) attend; loss 는 action chunk 의 flow-matching 목표(UAS 마스크 적용).

---

## ⛓️ 불변식·가정

- (가정 1) 서로 다른 센서의 동일 functional-area(예: "엄지팁")는 같은 슬롯·같은 공유 임베딩을 받으므로, tactile expert 가 학습한 슬롯-수준 접촉 표현은 센서-불가지론적이다 — 이 가정이 깨지면 cross-sensor/unseen 전이가 무효.
- (가정 2) 모든 센서 신호는 image/array/state 세 타입 중 하나로 환원 가능하며, 같은 관측 shape 의 영역은 동일 인코더로 처리해도 무방하다(공통 촉각 동역학 가정).
- (가정 3) action expert→tactile expert 의 단방향 attention 으로 충분 — 촉각이 VLM 의 vision-language prior 를 역으로 교란하지 않아야 prior 가 보존된다.
- (가정 4) z-score 정규화가 contact-rich fine-grained action 생성에 quantile 기반보다 적합(데이터셋별 독립 통계).
- (가정 5) 이종 embodiment 의 손 관절은 FAAS 기능 슬롯으로 모호함 없이 매핑 가능(UniDex 가정 차용).

---

## 📊 하이퍼파라미터·손실

- 손실 식: flow-matching action 생성 목표 + UAS 마스크 `M` (구체적 식은 원문에 명시 없음 — π0.5 목표 차용).
- 하이퍼:

  | 이름 | 값 | 출처 |
  |------|----|----|
  | tactile expert (w/d/MLP/head/head-dim) | `1024 / 18 / 4096 / 8 / 256` (~300M) | App. B.4 |
  | image enc (sensor-specific ViT) | `depth=3, width=768, head=12` | App. B.2 |
  | image enc (shared T3 Transformer) | `depth=9, width=768, head=12` | App. B.2 |
  | MTTS 슬롯 수 | `24` (0–14 손, 15–20 F/T, 21–23 예약) | §2.1 |
  | UAS dim 구성 | $`\mathbf{t}_w\in\mathbb{R}^3,\ \mathbf{r}_w\in\mathbb{R}^6,\ \mathbf{q}_{arm}\in\mathbb{R}^7,\ \mathbf{q}_{hand}\in\mathbb{R}^{32}`$ (팔별) | App. B.1 |
  | optimizer | `AdamW` (Muon 은 일반화 저하로 기각) | App. B.4 |
  | normalization | z-score (state·action) | App. B.4 |
  | pretrain | 48× H20, 50k step, batch 768, lr $`1\times10^{-4}\to 5\times10^{-5}`$ | App. D |
  | finetune | 8× A800, 20k step/dataset, batch 64, lr $`5\times10^{-5}\to 5\times10^{-6}`$ | App. D |
  | 데이터 mixture | human:dexhand:gripper ≈ 20:30:50, ~3,000h, 26 src, 21 sensor | §2.4, App. C |
  | 초기화 partition | VLM/action expert = π0.5 / tactile·injector·projector = scratch | App. D |

---

## 🎯 평가 메트릭

- **지표** — task 성공률(%). 시뮬 100 rollouts/task, real-robot 20 rollouts/task.
- **임계값/비교** — seen 센서 평균 대비 +17.2%(real, Table 2), unseen 센서 +31%(Table 3); UniVTAC sim 2위 대비 +17.5%(Table 1). NTP-1 대조로 전이-지식 출처 검증(FlexivXense +37.5%).
- **비교 baseline** — π0.5(촉각 無), Tactile-VLA(adapter 주입), FTP-π0.5(아키텍처만, 사전학습 無), NTP-1(촉각 분기 사전학습 無).

---

## ✨ 변경 의도 (intent)

기존 촉각 정책은 특정 센서/embodiment 에 묶여 데이터가 파편화되고, 촉각 강화 VLA 는 촉각을 VLM expert 에 adapter 로 주입해 prior 를 교란하거나 효율이 낮았습니다. FTP-1 은 (1) 센서 형태 차이를 손 기능 영역 기반 통일 토큰 공간(MTTS) + 타입별 이종 인코더로 흡수하고, (2) 모든 센서가 공유하는 독립 tactile expert 를 두어 vision-language prior 를 건드리지 않으면서 센서 간 공통 촉각 동역학을 학습합니다. 이 두 선택의 결과로, 입력단 인코더만 새로 학습하면 사전학습에서 본 적 없는 센서로도 공유 expert 를 재사용해 촉각 조작 스킬을 전이할 수 있다는 점이 prior art 대비 본질적 차이입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — π0.5 계열 multi-expert + flow-matching action expert 구조이므로 `pi05`(또는 `pi0`) family 와 가장 가깝습니다. 다만 (a) 독립 tactile expert(300M Transformer)와 (b) MTTS 토큰화 + 이종 촉각 인코더, (c) adaptive RMSNorm proprioception 주입은 base 에 없는 신규 모듈이라 추가 구현이 필요합니다. T3 사전학습 weight 의존성도 별도 확보 대상.

---

## 🚧 미해결 / 잠정

- flow-matching loss 의 구체적 수식이 원문에 명시되지 않아 π0.5 목표를 차용한 것으로 가정.
- MTTS 24-slot 의 정확한 영역 라벨(슬롯 2–14 의 손가락/관절 대응)은 Fig. 3 이미지로만 정의되어, 텍스트 좌표가 없습니다(구현 시 그림 참조 필요).
- 멀티뷰 카메라 수 `N_cam`, 이미지 해상도 `H_img/W_img`, proprio 차원 `D_state` 등은 embodiment 별로 달라 일반 스펙에 고정값 미명시.
- T3 shared Transformer 의 공개 weight 출처/라이선스는 본문에서 인용 번호로만 제시.
