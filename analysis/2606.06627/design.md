# Design — What Matters When Cotraining Robot Manipulation Policies on Everyday Human Videos?

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | What Matters When Cotraining Robot Manipulation Policies on Everyday Human Videos? |
| 링크 | [arXiv:2606.06627](https://arxiv.org/abs/2606.06627) |
| 분석 문서 | [`analysis/2606.06627/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-10 |

---

## 🧮 데이터 계약

두 임베디먼트(human `H` / robot `R`)의 궤적을 같은 정책에 흘리되, action 경로는 임베디먼트별로 분리한다.

- **입력 (이미지)** — RGB: shape `(B, N_cam, 3, 224, 224)`, dtype float. 로봇은 egocentric + wrist 2-view, 인간은 egocentric 1-view(wrist 토큰 위치는 전부 마스킹). 공유 SigLIP ViT(patch 14) → 시각 토큰 `(B, N_tok, D)`. 이미지는 image-space scale alignment + resize 후 입력.
- **입력 (noisy action)** — flow-matching 으로 손상된 action chunk `(B, T_action, A_dim)`; 임베디먼트별 action encoder(3-layer MLP) → action 토큰 `(B, T_action, D)`.
- **입력 (proprioception)** — 임베디먼트별 proprio encoder(3-layer MLP) → proprio 토큰. (원문에 shape 명시 없음 — 가정으로 메움)
- **출력 (action)** — 임베디먼트별 flow-matching decoder → denoised action chunk. 로봇 `A_dim`: TCP 위치(3) + 회전 + 이산 grasp(ternary) $`g \in \{\text{open, close, no-op}\}`$. 인간 raw action 은 middle-finger 프레임 + `g_no-op` 로 매핑.
- **정규화** — action 은 데이터셋별 독립 mean-centering + 1–99 백분위 필터 + `±1` 스케일. 회전은 정규화 없음($`R \in \mathrm{SO}(3) \Rightarrow R_{ij} \in [-1,1]`$).

---

## 🧰 모듈 인터페이스

```python
def encode_image(rgb, embodiment) -> Tensor:
    """공유 SigLIP ViT — 전체 토큰 grid 유지(CLS 병목 없음). wrist 부재 시 마스킹."""

def encode_action(noisy_action, embodiment) -> Tensor:
    """임베디먼트별 3-layer MLP action encoder → action 토큰."""

def transfusion_attend(img_tokens, action_tokens) -> Tensor:
    """모달리티별 Q/K/V 투영(데이터셋 공유) + 모달리티별 FFN expert로
       시각·액션 토큰 token-level fusion self-attention."""

def decode_action(hidden, embodiment) -> Tensor:
    """임베디먼트별 flow-matching action decoder → denoised action chunk."""

def cotrain_batch(human_ds, robot_ds, B) -> Loss:
    """미니배치마다 두 데이터셋에서 각 B/2 독립 균등 샘플링(= 로봇 데이터 암묵 upweight)."""
```

- **공유** — 시각 encoder(SigLIP ViT), self-attention Q/K/V(모달리티별, 데이터셋 간 공유).
- **분리(임베디먼트별)** — action encoder, proprio encoder, flow-matching action decoder.
- **외부 계약** — flow-matching timestep 은 Beta(1.5, 1.0) 샘플; 손실은 conditional flow-matching imitation loss(아래).

---

## ⛓️ 불변식·가정

- (가정 1) **action support 일치** — 정렬·정규화 후 human/robot action 주변분포는 같은 support(`±1`)를 공유해야 cotraining 의 표현 공유가 성립한다.
- (가정 2) **motion gap 존재 → specialization 필수** — human/robot action chunk 가 충분히 구별 가능할 만큼 다르므로(자연 동작), 공유 deterministic encoder/decoder 로는 $`f_\theta(o_h)=f_\theta(o_r)`$ 불변 매핑이 불가능 → 임베디먼트별 weight 필요.
- (가정 3) **image-space scale 일치** — pinhole $`Z = \frac{f\Delta X}{\Delta u}`$ 하에서 두 카메라의 객체 픽셀 스케일이 정렬돼야 공유 시각 특징이 학습된다. 어긋나면 전이 이득 소멸.
- (가정 4) **head-frame 안정화** — action chunk 를 현재 head frame 으로 변환하면 머리 카메라 움직임이 만드는 multimodality 가 제거된다.
- (가정 5) **손 라벨 품질 게이팅** — 전이는 3D 손 포즈 오차에 단조 의존(noise↑ → SR↓).

---

## 📊 하이퍼파라미터·손실

- 손실 식 (개념): $`L = L_{\text{FM}}^{R}\cdot\frac{N_R+N_H}{N_R} + L_{\text{FM}}^{H}\cdot\frac{N_R+N_H}{N_H}`$
  - `L_FM` = single-dataset conditional flow-matching imitation loss(관측 `o_t`, action chunk `A_t`); 동수 독립 샘플링이 위 가중과 동치(§4.5).
- reprojection fine-tune 손실(TriHands 라벨링):

$$\mathcal{L}_{\text{proj}}=\sum_{i\in\mathcal{I}}\lVert{\mathbf{p}}_{i}^{2\mathrm{D}}-\pi_{{\mathbf{K}}}\!\big(\hat{{\mathbf{p}}}_{i}^{3\mathrm{D}}\big)\rVert_{1}$$

| 이름 | 값 | 출처 |
|------|----|----|
| Visual Encoder LR | $`3.0\times10^{-5}`$ | Table 6 |
| MoE Parameters LR | $`3.0\times10^{-4}`$ | Table 6 |
| Adam Betas | `(0.9, 0.95)` | Table 6 |
| Self-attention layers / heads / KV heads / head dim | `6 / 8 / 1 / 256` | Table 6 |
| SigLIP ViT (hidden / layers / heads / image / patch) | `1152 / 27 / 16 / 224 / 14` | Table 6 |
| Vision expert (hidden / interm) | `2048 / 4096` | Table 6 |
| Proprio / Action expert (hidden / interm) | `1024 / 4096` | Table 6 |
| Action/Proprio enc·dec MLP (layers / hidden / act) | `3 / 1024 / LeakyReLU` | Table 6 |
| Flow matching Beta (α, β) | `(1.5, 1.0)` | Table 6 |
| action 정규화 | mean-center + 1–99 pct + `±1` | §4.3 |
| 손 noise 주입 레벨 | `0.5× / 1.0×` fitted std | §5, Table 5 |

---

## 🎯 평가 메트릭

- **지표** — task success rate(%) · **임계값** — 저데이터(3-env)에서 HC vs RO 절대 격차(논문: 평균 +29.7%p, 범위 +20~48%p) · **비교 baseline** — Robot Only(RO), CLS-token, PiZero(공유 enc/dec), EgoBridge, EgoDex(데이터), HaWoR(단안 손).
- **세팅** — 과제당 robot env `{3,5,10}` × 50 demos, test 4 env × 15 rollout. 6 과제(Pick/Stack/Pull/Reorient/Book/Pour). CI: 95% Gaussian / Clopper-Pearson.
- **분석 지표** — 실패를 global(객체 미접근) vs local(수 cm 차) 로 분류 → local 우세 시 motion transfer 로 판정(H2). 손 오차: MPJPE / PA-MPJPE / W-MPJPE / WA-MPJPE(mm).

---

## ✨ 변경 의도 (intent)

자연 동작 인간 영상에서의 전이를 위해, lab 데이터용 통념(이미지 CLS-token 병목, 임베디먼트 공유 action encoder/decoder)을 *거부* 한다. 핵심은 "관측·액션은 정렬(image-space scale + MANO→TCP retarget + head-frame 안정화)하되, 네트워크는 임베디먼트별로 specialize(token-level fusion + 분리 action enc/dec) 하고, 로봇 데이터를 동수 샘플링으로 암묵 upweight"하는 것. prior art(Egomimic/Egobridge 의 정렬-우선, PiZero 의 공유 decoder)는 motion gap 이 작은 aligned 데이터를 가정하므로 자연 동작에선 전이를 막는다는 것이 이 설계의 반박 지점.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 후보 base: `pi0` / `pi05` family 와 가장 가깝다(conditional flow-matching action expert + ViT/SigLIP backbone). 단 본 설계의 차별점(임베디먼트별 분리 action enc/dec, token-level fusion, per-dataset 동수 샘플러, image-space scale 정렬 전처리)은 pi0 의 공유 action expert·표준 sampler 위에 *추가 분기* 로 얹어야 하며 그대로는 매핑되지 않을 수 있음.

---

## 🚧 미해결 / 잠정

- proprioception 입력 텐서 shape·차원이 본문에 명시되지 않아 "(원문에 명시 없음 — 가정으로 메움)" 로 둠.
- conditional flow-matching loss 의 정확한 식(velocity 회귀 형태)은 Appendix H 가 산문 서술이라 verbatim 수식 미확보 — 개념식으로만 기록.
- 로봇 action 의 회전 표현(쿼터니언/6D/행렬)이 본문에 명시되지 않음 — 정규화는 SO(3) 경계만 언급.
- 코드·가중치 공개 여부 미확인(웹사이트는 interactive viz 위주) → 구현 시 하이퍼는 Table 6 기준 재구성 가정.
