# Design — RotVLA: Rotational Latent Action for Vision-Language-Action Model

> PROBE design 산출물 (Layer 1, vendor-agnostic). 단일 한글 문서이며,
> 영문 1차 파일은 없습니다. `/analyze-paper` 가 `analysis/<id>/analysis.md` 와
> 함께 자동 생성합니다 — 알고리즘 명세를 base 좌표계 없이 추출합니다.
> base 매핑은 `/implement` 단계에서 이루어집니다. 형식·이모지·용어 규칙은
> `docs/STYLE.md` §6 / §4 를 정확히 따릅니다. 재실행 시 이 파일을
> 덮어씁니다.

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | RotVLA: Rotational Latent Action for Vision-Language-Action Model |
| 링크 | [arXiv:2605.13403](https://arxiv.org/abs/2605.13403) |
| 분석 문서 | [`analysis/2605.13403/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-05-26 |

---

## 🧮 데이터 계약

LAM 학습 단계와 VLA 사전학습/finetuning 단계의 입출력을 분리해 기록합니다.

**LAM 단계 입출력**

- **입력** — `frame_triplet`: shape `(B, 3, C, H, W)`, dtype `float32`, DINOv2 정규화. 시간 간격은 `interval=k` (원문에 명시 없음 — 가정으로 메움).
- **출력** — `latent_action`: shape `(B, 2, n, n)`, dtype `float32`, 각 행렬이 ${\rm SO}(n)$ 위에 사영됨 (orthogonal, det = +1). `n = 16`.
- **부산물** — `reconstructed_frame`: shape `(B, 2, C, H, W)` (단일-스텝), `composed_frame`: shape `(B, C, H, W)` (두-스텝 합성).

**RotVLA 사전학습**

- **입력 (관측)** — `frame_pair`: `(B, 2, C, H, W)` + `instruction_tokens`: `(B, L)`.
- **입력 (감독)** — LAM 으로 추출한 `latent_action`: `(B, n, n)`.
- **출력** — flow-matching velocity 예측 `v_theta`: shape `(B, n, n)`.

**Finetuning (downstream control)**

- **입력 (관측)** — `frame_pair`: `(B, 2, C, H, W)` + `instruction_tokens`: `(B, L)` + `proprio` (선택; 원문에 명시 없음 — 가정으로 메움).
- **입력 (감독)** — `latent_action`: `(B, n, n)` + `robot_action_chunk`: shape `(B, N, d)`, dtype `float32`, abs EEF (xyz) + Rotate6D orientation. horizon `N = n = 16` (chunk horizon 이 latent 차원과 같다고 본문이 명시).
- **출력** — `unified velocity`: latent 영역 `(B, n, n)` + robot 영역 `(B, N, d)`, 한 head 가 동시에 회귀.

---

## 🧰 모듈 인터페이스

LAM, RotVLA, Unified Action Expert 의 세 경계 인터페이스를 둡니다 — base 좌표는 포함하지 않습니다.

```python
def lam_encode(frames: Tensor) -> Tensor:
    """프레임 쌍을 ${\rm SO}(n)$ latent action 으로 매핑."""
    # frames: (B, 2, C, H, W) → SoftVQ → SVD projection
    # return: (B, n, n) — orthogonal, det = +1
```

```python
def lam_decode(frame: Tensor, latent: Tensor) -> Tensor:
    """latent action 을 프레임에 적용해 다음 프레임 복원."""
    # frame: (B, C, H, W), latent: (B, n, n)
    # return: (B, C, H, W)
```

```python
def so_n_project(matrix: Tensor) -> Tensor:
    """SVD-based orthogonal projection onto SO(n)."""
    # M = U @ S @ V^T → return U @ V^T (with det fix)
```

```python
def lam_triplet_loss(frames: Tensor) -> dict:
    """triplet (I_t, I_{t+1}, I_{t+2}) 위에서 단일·합성·softVQ 손실 합산."""
    # frames: (B, 3, C, H, W)
    # return: {"single": L_single, "comp": L_comp, "soft": L_soft, "total": L_triplet}
```

```python
def rotvla_flow_matching_loss(z_target: Tensor, h: Tensor) -> Tensor:
    """latent action 영역의 flow-matching velocity 회귀."""
    # z_target: (B, n, n) — LAM 으로 사전 추출한 감독 신호
    # h: (B, T_h, D)     — VLM 컨텍스트
    # return: scalar
```

```python
def unified_action_expert(z_target: Tensor, a_target: Tensor, h: Tensor) -> Tensor:
    """latent + robot action 을 한 flow-matching head 로 동시 denoise.

    구조적 attention 규약:
      latent 토큰  → vision-language 토큰만 attend
      robot 토큰   → latent + vision-language 토큰 모두 attend
    """
```

- **외부 호출 계약** — `lam_encode` / `lam_decode` 의 비주얼 백본은 LAM 학습 동안 DINOv2 를 동결해 사용합니다. RotVLA 의 VLM 백본은 학습률을 낮춰 학습 가능 상태로 두고, action expert 는 처음 5 k 스텝 동안 VLM 을 동결한 채 워밍업합니다.

---

## ⛓️ 불변식·가정

- **(I1) Orthogonality + det = +1** — `lam_encode` 의 출력 행렬은 모든 step 에서 ${\rm SO}(n)$ 위에 있어야 합니다 ($M^\top M = I$, $\det M = +1$). projection 단계에서 매 호출마다 강제합니다.
- **(I2) Closure / 합성 일치** — $\mathrm{Proj}(z_{t \to t+1} \cdot z_{t+1 \to t+2})$ 를 두 칸 latent action 으로 정의합니다. 행렬 곱은 ${\rm SO}(n)$ 안에서 닫혀 있고 결합법칙이 성립합니다.
- **(I3) Identity anchor** — 동일 프레임 쌍 $(I_t, I_t)$ 에서 추출한 latent 의 배치 평균을 ${\rm SO}(n)$ 으로 사영한 값 $z_\mathcal{I}$ 가 단위원 역할을 합니다. 데이터에 정지 또는 거의 정지에 가까운 프레임 쌍이 충분히 자주 등장해야 하고, 이 가정이 깨지면 게이지 자유도가 남아 학습이 표류합니다.
- **(I4) Frame-copy 자명해 차단** — 단일-스텝 loss 만으로는 latent 가 다음 프레임 픽셀을 직접 인코딩하는 자명해로 빠질 수 있습니다. $\mathcal{L}_{\rm comp}$ 가 들어가야 latent 가 dynamics 의 *부분* 으로만 의미를 갖습니다.
- **(I5) Latent horizon = chunk horizon = n** — finetuning 에서 latent 차원 $n$ 은 robot action chunk horizon 과 같습니다. $n$ 을 바꾸면 두 값이 함께 움직입니다.
- **(I6) Structured attention 비대칭** — robot action 토큰의 query 가 latent 토큰의 key/value 를 본다는 단방향성. 반대 방향이 열리면 finetuning 시 latent 가 robot label 을 그대로 베껴 사전학습된 임바디먼트-불변 의미가 깨집니다.

---

## 📊 하이퍼파라미터·손실

**손실 식**

- LAM 학습: $\mathcal{L}_{\rm triplet} = \mathcal{L}_{\rm single} + \mathcal{L}_{\rm comp} + \mathcal{L}_{\rm soft}$
  - $\mathcal{L}_{\rm single} = \|\hat{I}_{t+1} - I_{t+1}\|_2^2 + \|\hat{I}_{t+2} - I_{t+2}\|_2^2$
  - $\mathcal{L}_{\rm comp} = \|\hat{I}_{t+2}^{\rm comp} - I_{t+2}\|_2^2$
  - $\mathcal{L}_{\rm soft}$ — SoftVQ codebook KL (계수 원문 미명시)
- RotVLA 사전학습: $\mathcal{L}_{\rm FM} = \mathbb{E}[\|v_\theta(z_\tau, \tau, h) - (z_{t \to t+1} - z_0)\|_2^2]$
- Finetuning: $\mathcal{L}_{\rm LA\text{-}RA}^{\rm FM} = \mathbb{E}[\|v_\theta(x_\tau, \tau, h) - (x - x_0)\|_2^2]$, $x = (a, z_{t \to t+1})$

**하이퍼**

| 이름 | 값 | 출처 |
|------|----|----|
| `latent_dim n` | `16` | §4.1 |
| `VLM backbone` | `InternVL3.5-1B` | §3.2, §4.1 |
| `action expert depth` | `24-layer DiT` | §4.1 |
| `total params` | `1.7B` (vision 304M + LM 752M + action 305M + LAM 290M) | §4.1 |
| `pretrain steps` | `200k` | §4.1 |
| `pretrain batch` | `256` | §4.1 |
| `finetune batch` | `128` | §4.1 |
| `optimizer` | `AdamW` | §4.1 |
| `learning rate` | `1e-4` | §4.1 |
| `weight decay` | `0.01` | §4.1 |
| `action expert warm-up` | `first 5k steps, VLM frozen` | §4.1 |
| `VLM LR strategy` | `reduced LR (X-VLA [26] recipe)` | §4.1 |
| `robot action representation` | `abs EEF (xyz) + Rotate6D orientation` | §4.1 |
| `pretraining data` | `1700+ h cross-embodiment + human video` | §1, §4.1 |
| `pretrain hardware` | `8× NVIDIA H200, 50 h` | §4.1 |
| `flow-matching noise schedule` | `linear: x_τ = τ x + (1-τ) x_0, x_0 ~ N(0, I), τ ∈ [0,1]` | §3.2, §3.3 |
| `frame interval k` | (원문에 명시 없음 — 가정으로 메움) | §3.1 |
| `triplet loss coefficients` | (원문에 명시 없음 — 가정으로 메움) | §3.1 |

---

## 🎯 평가 메트릭

- **지표** — `LIBERO 4-suite avg. success rate` · **임계값** — RotVLA 98.2 % · **비교 baseline** — X-VLA 98.1 %, $\pi_{0.5}$ 94.1 %, OpenVLA-OFT 97.1 %.
- **지표** — `RoboTwin2.0 clean / randomized success rate` · **임계값** — 89.6 / 88.5 % · **비교 baseline** — StarVLA 88.2 / 88.3, Motus 88.7 / 87.0, $\pi_{0.5}$ 82.7 / 76.8.
- **지표** — `real-world ARX R5 success rate` · **임계값** — 단일암 두 태스크 >90 % · **비교 baseline** — $\pi_{0.5}$.
- **지표** — `inference latency / step` · **임계값** — 79 ms (H20 1 GPU) · **비교 baseline** — $\pi_{0.5}$ 61 ms.
- **LAM 진단 지표 (§4.4 Table 2)** — `next-frame MSE` vs `imagined-frame MSE'`. triplet 학습은 두 값의 격차를 키우고, baseline 은 줄임 (latent 가 motion 이 아닌 appearance 를 인코딩한다는 증거).
- **LAM 표현력 (§4.4 Table 3, LARY 벤치마크 [51])** — linear probing 의 regression error (낮을수록 좋음) + classification accuracy (높을수록 좋음).

---

## ✨ 변경 의도 (intent)

기존 LAM (VQ-VAE) 이 보이는 세 결함 — 자명해 붕괴, 표현력 제약, 비물리적 latent 공간 — 은 모두 latent 공간의 *이산성* 에서 비롯된다는 진단 위에 서 있습니다. RotVLA 는 latent 를 ${\rm SO}(n)$ 회전군 원소로 두어 연속성·구성성·기하적 의미를 동시에 확보하고, 두 단계 합성 reconstruction 손실을 추가해 단일-스텝만 보는 baseline 의 frame-copy 자명해를 차단합니다. 다운스트림에서는 같은 latent 를 상위 계획자(high-level planner)로 재해석해 통합 flow-matching head 에 robot action 과 함께 묶고, 구조화된 attention 으로 계획자→제어기 단방향 흐름을 강제합니다. 이렇게 해서 1.7B 라는 작은 규모로 동시대 3–9B VLA 들을 LIBERO·RoboTwin 양 벤치마크에서 동률 이상으로 따라잡습니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 후보 base: `pi0` / `pi05` (flow-matching action expert + VLM 백본의 분리) 와 가장 가까움. RotVLA 의 unified flow-matching action head 는 `pi0` 의 action expert 패턴 위에 latent 차원을 추가한 형태로 매핑 가능. LAM 자체 (DINOv2 + spatial-temporal transformer + SoftVQ + SVD projection) 는 `lerobot` 내 대응 family 가 없어 신규 모듈 (`processor` 의 별도 hook 또는 외부 사전학습 산출물 로딩) 형태로 들어갑니다. VLM 백본 (InternVL3.5-1B) 은 vendored 스냅샷에 들어 있지 않으므로 `/implement` 단계에서 별도 어댑터로 대체합니다.

---

## 🚧 미해결 / 잠정

- 프레임 간격 $k$ 의 구체 값은 본문에 빠져 있고, "interval $k$" 표기만 등장합니다.
- $\mathcal{L}_{\rm triplet}$ 의 세 항 ($\mathcal{L}_{\rm single}$, $\mathcal{L}_{\rm comp}$, $\mathcal{L}_{\rm soft}$) 가중치 계수는 명시가 없습니다.
- SoftVQ codebook 크기·차원 등 세부 구성은 본문에서 확인할 수 없습니다 (Appendix 인용만).
- LAM decoder transformer 의 layer 수·width 등 세부 구성은 언급되지 않습니다.
- robot action 의 dimensionality $d$ 가 임바디먼트별로 다른지, padding/normalization 규약이 어떻게 통일되는지는 본문에 드러나지 않아 가정으로 메웠습니다 (`d = 7` 단일 EEF, `d = 14` 이중 EEF 같은 임바디먼트별 분리).
- VLM 학습 가능 파라미터 비율 (reduced LR 의 실제 배수) 은 수치로 제시된 곳이 없습니다.
- 코드·사전학습 가중치 공개 여부는 본문 어디에도 적혀 있지 않습니다.
