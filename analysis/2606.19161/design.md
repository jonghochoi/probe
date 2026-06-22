# Design — HT-Bench: Benchmarking and Learning Dexterous Full-Hand Tactile Representations with Egocentric Vision

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | HT-Bench: Benchmarking and Learning Dexterous Full-Hand Tactile Representations with Egocentric Vision |
| 링크 | [arXiv:2606.19161](https://arxiv.org/abs/2606.19161) |
| 분석 문서 | [`analysis/2606.19161/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-22 |

> 대상 알고리즘은 **HandTouch** — factorized vector-quantized 비전–촉각 인코더와 그 점진 3단계(공간 → 교차모달 → 시간) 학습 절차입니다. HT-Bench(벤치마크/데이터)는 평가 환경이며 Design 대상이 아닙니다.

---

## 🧮 데이터 계약

- **입력 (촉각)** — `tactile_map`: shape `(B, 1, 224, 224)`, dtype `float32`, $`\mathbf{t}\in[0,1]`$ 정규화(단일채널 압력 맵). (§4.1)
- **입력 (시각)** — `rgb_frame`: shape `(B, 3, H, W)`, dtype `float32`. frozen 사전학습 ViT로 인코딩되어 시각 맥락 특징 $`\mathbf{F}_{v}`$ 가 됨. 해상도 `(H, W)` 는 원문에 명시 없음 — 가정으로 메움(`224×224`). (§4.2)
- **입력 (Stage 2 손 식별)** — `hand_id` ∈ {left, right} → 학습 가능한 hand-specific token $`\mathbf{t}_{\mathrm{hand}}`$. (§4.2)
- **입력 (Stage 3 시퀀스)** — $`\mathbf{v}_{T-2:T}`$ (시각 맥락) + $`\mathbf{t}_{T-2:T-1}`$ (과거 촉각 이력). 정확한 윈도 길이 표기는 본문에서 $`\mathbf{v}_{T-2}`$ / $`\mathbf{t}_{T-2}`$ 로 축약되어 모호 — `(원문에 명시 없음 — 가정으로 메움: 직전 2~3 프레임)`. (§4.3)
- **중간 표현** — 패치 토큰 → 8-layer ViT → 연속 잠재 $`\mathbf{Z}_{e}\in\mathbb{R}^{N\times D}`$ → factorized VQ → 양자화 토큰 $`\mathbf{Z}_{q}`$. codebook $`\mathcal{C}=\{\mathbf{e}_i\}_{i=1}^{K}\subset\mathbb{R}^{d}`$, $`K=2048`$, $`d\ll D`$. (§4.1)
- **출력** — 재구성/복원/예측된 촉각 맵 $`\hat{\mathbf{t}}`$ (또는 $`\hat{\mathbf{t}}_{\mathrm{cm}}`$, $`\hat{\mathbf{t}}_{T}`$): shape `(B, 1, 224, 224)`, dtype `float32`, $`[0,1]`$ 범위.

---

## 🧰 모듈 인터페이스

```python
def tactile_tokenizer(t: Tensor) -> Tensor:
    """(B,1,224,224) 촉각 맵을 conv projection + 위치임베딩으로 비중첩 패치 토큰화."""

def vit_encoder(tokens: Tensor) -> Tensor:
    """8-layer ViT: 패치 토큰 -> 연속 잠재 Z_e (B,N,D)."""

def factorized_vq(z_e: Tensor, codebook: Tensor, W_in, W_out) -> tuple[Tensor, Tensor, dict]:
    """W_in 으로 코드북 공간 투영 후 최근접 코드로 양자화(Eq.1), W_out 으로 복귀.
       반환: z_q, 인덱스, VQ 손실 항(codebook/commitment) + EMA 사용통계."""

def codebook_restart(codebook, usage_ema, tau, active_feats) -> Tensor:
    """누적 사용빈도 < tau 인 죽은 코드를 현재 배치 active 투영특징 + 등방 가우시안으로 재초기화."""

def tactile_decoder(z_q: Tensor, vis_ctx: Tensor | None) -> Tensor:
    """attention block + conv upsampling 으로 촉각 맵 복원. vis_ctx 주어지면 cross-attention 주입."""

def visual_context(v: Tensor, frozen_vit) -> Tensor:
    """동기화 RGB 프레임 -> frozen ViT -> 시각 맥락 특징 F_v (key/value 로 사용)."""

def cross_modal_inpaint(t_masked, F_v, hand_token) -> Tensor:
    """촉각 토큰=query, F_v=key/value 인 cross-attention + MLP 로 가린 촉각 복원 (Eq.4)."""

def temporal_predict(v_seq, t_seq) -> Tensor:
    """시각 맥락 + 촉각 이력을 공유 이산 공간에 투영해 t_T 예측 (Eq.5)."""
```

- 호출 계약: VQ 모듈은 손실 항(Eq. 2의 2·3항)을 인코더/디코더와 **공동 최적화**로 되돌립니다. `codebook_restart` 는 Stage 1·2 동안 매 학습스텝(또는 주기) 활성. `visual_context` 의 ViT는 전 단계에서 **frozen**(gradient 미전파).

---

## ⛓️ 불변식·가정

- (가정 1) 촉각 맵은 $`[0,1]`$ 단일채널 224×224로 정규화되어 있어야 함 — 압력 스케일/해상도가 다르면 codebook 공간과 cIoU/RMSE 절대값이 비교 불가.
- (가정 2) 시각 ViT는 **frozen** — 시각 특징은 고정 prior로만 주입되고 촉각 측만 학습됨(교차모달 정렬이 시각 표현을 망가뜨리지 않는다는 전제).
- (가정 3) 공유 codebook이 단계 간 **불변** — Stage 1에서 학습한 이산 토큰 공간을 Stage 2·3가 재사용/미세조정하므로, 코드북 붕괴(collapse)가 일어나면 세 단계 전체가 무효.
- (가정 4) Stage 2 손실에서 $`\lambda_{\mathrm{mask}}>\lambda_{\mathrm{vis}}`$ — 가린 영역 복원을 가시영역보다 강하게 가중해야 vision-conditioned 합성 능력이 학습됨.
- (가정 5) RGB와 촉각 프레임은 **타이트하게 동기화**되어 있어야 함 — cross-modal/temporal 목표가 시간정렬된 paired 데이터를 전제.

---

## 📊 하이퍼파라미터·손실

- 손실 식:
  - Stage 1: $`\mathcal{L}_{\text{stage1}}=\|\mathbf{t}-\hat{\mathbf{t}}\|^{2}_{2}+\|\mathbf{Z}_{q}-\mathrm{sg}[\mathbf{W}_{\text{in}}\mathbf{Z}_{e}]\|_{2}^{2}+\beta\|\mathrm{sg}[\mathbf{Z}_{q}]-\mathbf{W}_{\text{in}}\mathbf{Z}_{e}\|_{2}^{2}`$ (Eq. 2)
  - Stage 2: $`\mathcal{L}_{\text{stage2}}=\lambda_{\text{vis}}\|(\mathbf{1}-\mathbf{M})\odot(\mathbf{t}-\hat{\mathbf{t}}_{\text{cm}})\|^{2}_{2}+\lambda_{\text{mask}}\|\mathbf{M}\odot(\mathbf{t}-\hat{\mathbf{t}}_{\text{cm}})\|^{2}_{2}+\text{(VQ 항)}`$ (Eq. 4)
  - Stage 3: $`\mathcal{L}_{\mathrm{stage3}}=|\mathbf{t}_{T}-\hat{\mathbf{t}}_{T}|_{2}^{2}`$ (Eq. 5)
  - masking 커리큘럼: $`P_{\mathrm{full}}(\gamma)=p_{\min}+\dfrac{(p_{\max}-p_{\min})}{1+\exp[-12(\gamma-0.5)]}`$ (Eq. 3)

- 하이퍼:
  | 이름 | 값 | 출처 |
  |------|----|----|
  | `K` (codebook 크기) | `2048` | §4.1 |
  | `d` (factorized 병목) | `d ≪ D` (구체값 미명시) | §4.1 |
  | ViT 인코더 깊이 | `8 layers` | §4.1 |
  | 입력 촉각 해상도 | `1×224×224`, `[0,1]` | §4.1 |
  | $`\beta`$ (commitment 가중치) | (원문 미명시) | §4.1, Eq. 2 |
  | $`\lambda_{\text{vis}}`$ / $`\lambda_{\text{mask}}`$ | (원문 미명시; $`\lambda_{\text{mask}} > \lambda_{\text{vis}}`$) | §4.2, Eq. 4 |
  | $`p_{\min}`$ / $`p_{\max}`$ | (원문 미명시) | §4.2, Eq. 3 |
  | $`\tau`$ (restart 임계) | (원문 미명시) | §4.1 |
  | 커리큘럼 sigmoid 기울기 | `12`, 중심 $`\gamma=0.5`$ | §4.2, Eq. 3 |
  | optimizer / lr / 배치 / epoch / GPU | (원문 미명시) | — |

---

## 🎯 평가 메트릭

- **지표** — `Hit@1` / `Recall@5` (retrieval, SSIM 랭킹 vs. 임베딩 cosine 랭킹) · **임계값** — 높을수록 좋음 · **비교 baseline** — ViT-based (최강 baseline: 94.27 / 74.65)
- **지표** — `RMSE` (full `F-` / hole `H-`) · **임계값** — 낮을수록 좋음 · **비교 baseline** — ViT-based(inpainting test F-RMSE 0.022) → Ours 0.010
- **지표** — `cIoU` $`=\frac{\sum_{i,j}\min(P_{i,j},\hat{P}_{i,j})}{\sum_{i,j}\max(P_{i,j},\hat{P}_{i,j})}`$ (접촉 영역 IoU) · **임계값** — 높을수록 좋음 · **비교 baseline** — inpainting test F-cIoU 0.762 → Ours 0.911
- **평가 split** — standard test + task-level OOD(한 태스크 hold-out). 4개 태스크: similarity retrieval / masked inpainting / RGB→Tac synthesis / multimodal frame prediction.

---

## ✨ 변경 의도 (intent)

HandTouch는 촉각 표현을 단일 목표로 한 번에 학습하지 않고, **공유 이산 codebook** 위에서 공간(VQ 재구성)→교차모달(시각 주입 inpainting)→시간(frame prediction)의 점진 커리큘럼으로 분해해 학습합니다. 순수 VQ-VAE가 재구성만으로 fine-grained 구조 단서를 잃는 약점을, 정렬·시간 목표를 단계적으로 얹어 보완하는 것이 prior art 대비 핵심 차이입니다. 또한 full-hand 촉각의 좌우 거울 대칭을 hand-specific token으로, 부위 단위 정보 손실을 Regional/Complete dual masking 커리큘럼으로 명시적으로 다룹니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — HandTouch는 정책(action decoder)이 아니라 **관측측 촉각 인코더 / 표현 사전학습 모듈**입니다. `pi0`/`act`/`diffusion` 등 정책 family에 직접 대응하지 않으므로, lerobot의 processor / observation encoder 경로(촉각 입력을 토큰화·인코딩하는 전처리 단)에 사전학습된 인코더로 끼워넣는 형태가 후보입니다. 단 lerobot 베이스라인에 full-hand 촉각 맵 인코더가 없으면 `/implement-design` 가 `UNMAPPABLE` 판정을 낼 수 있습니다(그 경우에도 본 vendor-agnostic Design 은 유효).

---

## 🚧 미해결 / 잠정

- factorized 병목 차원 $`d`$, commitment 가중치 $`\beta`$, masking 확률 $`p_{\min}`$/$`p_{\max}`$, restart 임계 $`\tau`$, $`\lambda_{\text{vis}}`$/$`\lambda_{\text{mask}}`$ 구체값 — 원문 미명시(가정 없이 비워둠).
- Stage 3 시퀀스 윈도 길이 — 본문이 $`\mathbf{v}_{T-2}`$ / $`\mathbf{t}_{T-2}`$ 로 축약 표기해 정확한 프레임 수 모호 — `(가정: 직전 2~3 프레임)`.
- frozen 시각 ViT의 구체 backbone(어떤 사전학습 가중치) — 원문 미명시.
- 디코더의 정확한 attention block 수·upsampling 구조 — "attention blocks and convolutional upsampling" 외 상세 미명시.
- optimizer / lr / batch / epoch / 하드웨어 — 전부 원문 미명시(재현 시 별도 탐색 필요).
