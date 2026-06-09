# Design — Spatial Forcing: Implicit Spatial Representation Alignment for Vision-language-action Model

> PROBE design 산출물 (Layer 1, vendor-agnostic). 단일 한글 문서이며,
> 영문 1차 파일은 없습니다. `/analyze-paper` 가 `analysis/<id>/analysis.md` 와
> 함께 자동 생성합니다 — 알고리즘 명세를 base 좌표계 없이 추출합니다.
> base 매핑은 `/implement-design` 단계에서 이루어집니다. 형식·이모지·용어 규칙은
> `docs/STYLE.md` §6 / §4 를 정확히 따릅니다. 재실행 시 이 파일을
> 덮어씁니다.

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Spatial Forcing: Implicit Spatial Representation Alignment for Vision-language-action Model |
| 링크 | [arXiv:2510.12276](https://arxiv.org/abs/2510.12276) |
| 분석 문서 | [`analysis/2510.12276/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-09 |

---

## 🧮 데이터 계약

SF 는 기존 VLA 학습 그래프에 "학습 전용" 정렬 분기를 더하는 알고리즘입니다. 입력/출력은 학습 시점 기준이며, 추론 시 정렬 분기는 제거됩니다.

- **입력 (멀티뷰 이미지)** — `images`: shape `(B, V, 3, H, W)`, float, base VLA 정규화 그대로. `V` = 카메라 뷰 수 (VGGT 가 멀티뷰 전제).
- **입력 (언어 명령)** — `instruction`: `M` linguistic 토큰, base tokenizer 규약.
- **중간 표현 (정렬 source)** — `x_visual`: VLA 의 `align_layer` 출력 visual 토큰, shape `(B, N, D_vla)`. `N` = visual 토큰 수.
- **target 표현 (정렬 대상, 동결)** — `f3d`: VGGT backbone latent, shape `(B, N, D_3d)`. 픽셀 위치가 `x_visual` 토큰과 대응되도록 정렬됨. positional embedding `E` (shape `(N, D_3d)`) 가 더해짐.
- **출력 (action)** — `actions`: shape `(B, K, A)` (base VLA action expert 출력 그대로; `A` = action 차원). dtype·정규화 base 규약.
- **출력 (정렬 손실)** — `L_align`: scalar. 학습 손실에만 기여, action 출력 텐서 형태에 영향 없음.

---

## 🧰 모듈 인터페이스

```python
def vggt_target(images) -> "Tensor (B, N, D_3d)":
    """동결된 VGGT 로 멀티뷰 이미지의 backbone latent(공간 표현)를 추출.
       prediction head 가 아닌 transformer backbone latent 를 반환."""

def align_projector(x_visual) -> "Tensor (B, N, D_3d)":
    """VLA visual 토큰을 BatchNorm(Γ) → 2-layer MLP 로 투영해
       target 과 feature 차원을 맞춤. 학습 전용 모듈."""

def alignment_loss(x_visual, f3d, pos_emb) -> "scalar":
    """proj = align_projector(x_visual); target = f3d + pos_emb
       반환: -mean_i cosine_similarity(proj_i, target_i)."""

def sf_total_loss(L_action, L_align, alpha) -> "scalar":
    """L_action + alpha * L_align. alpha 기본 0.5."""
```

- **vggt_target** — 외부 호출 계약: VGGT 가중치는 동결(no grad), 학습 내내 frozen target. 멀티뷰 입력 필요.
- **align_projector** — source(VLA) 측만 학습. base VLA 의 `align_layer` 에서 visual 토큰을 가로채는 forward hook 형태로 구현 가능.
- **alignment_loss** — cosine similarity 기반. target 에 positional embedding 을 더한 뒤 정렬(순서 보존).
- **sf_total_loss** — 기존 action 손실과 가중 합. optimizer 는 base VLA 와 align_projector 파라미터를 함께 갱신(중간 VLM 층이 trainable 이어야 정렬 신호가 backbone 에 전파됨).

---

## ⛓️ 불변식·가정

- **(가정 1)** — 3D 정보는 VLA 의 visual 임베딩 안에 implicit 하게 표현될 수 있으며, action 토큰은 auto-regressive 과정에서 그 공간 단서를 흡수한다.
- **(가정 2)** — VGGT backbone latent 는 그 자체로 충분한 공간 정보를 담아 3D supervision 신호로 쓸 수 있다(prediction head 출력 불필요).
- **(가정 3)** — "깊지만 가장 깊지 않은" 중간층(예: 32층 중 24층, ≈0.75 depth) 정렬이 최적이다. 가장 깊은 층은 vision-특화 특징을 잃어 시각 target 정렬에 부적합하다.
- **(가정 4)** — target 표현에 positional embedding 을 더해야 auto-regressive 내 토큰 상대 위치 순서가 보존되어 long-horizon 성능이 유지된다.
- **(가정 5)** — 정렬은 표현의 "관계 기하(분포 형태)" 를 맞추되 cluster 중심은 분리되어, source modality 정체성을 잃지 않는다(표현 붕괴 없음).
- **(가정 6)** — source 토큰과 target 표현은 픽셀 위치 기준으로 대응 가능하다.

---

## 📊 하이퍼파라미터·손실

- 정렬 손실: `L_align = -(1/N) Σ_i S[ MLP·Γ(x^V_i), f^3D_i(I) + E ]` (S = cosine similarity, Γ = batch normalization).
- 전체 손실: `L_SF = L_action + α · L_align`.

| 이름 | 값 | 출처 |
|------|----|----|
| `α` (alignment 가중치) | `0.5` | §A, Tab. 3 (0/0.02/0.1/0.5/2.5/12.5 중 최적) |
| `align_layer` | 24 (of 32) | §2.3, Tab. 2 (layer sweep 1/8/16/24/32) |
| target 모델 | VGGT backbone latent + PE | §2.1, §2.3, Tab. 2 |
| projector | BatchNorm(Γ) + 2-layer MLP | §2.3 |
| similarity | cosine | §2.3 |
| base (LIBERO) | OpenVLA-OFT, 8×H100, 150k iter | §3.1 |
| base (RoboTwin) | $`\pi_{0}`$ + LoRA, 1×H100, 30k iter | §3.1 |
| 데이터 스케줄러 (data-eff 실험) | cosine-annealing | §3.3 |

---

## 🎯 평가 메트릭

- **지표** — `success rate (SR, %)` · **벤치마크** — LIBERO(Spatial/Object/Goal/Long, 각 500 trial) · RoboTwin(easy 100 / hard 300 trial) · 실로봇(AgileX 양손) · **비교 baseline** — base VLA(OpenVLA-OFT / $`\pi_{0}`$), explicit 3D VLA(GeoVLA·3D-CAVLA·SpatialVLA).
- **효율 지표** — 동일 SR 도달까지의 training iteration(수렴 3.8×) 과 데이터량(5.9× / 동일 데이터 +25.8%p).
- **진단 지표** — depth probing(VLA 동결 + DPT head 학습으로 임베딩 공간정보량 정량화), t-SNE(정렬 정도·표현 붕괴 여부).
- **핵심 수치** — LIBERO 평균 SR 98.5(SF) vs 97.1(OpenVLA-OFT base) vs 98.1(3D-CAVLA, 추가 3D 센서).

---

## ✨ 변경 의도 (intent)

기존 3D VLA 가 명시적 3D 입력(depth·point cloud) 또는 2D→3D 추정에 의존해 센서 노이즈·하드웨어 이질성·estimator 성능에 종속되었던 반면, SF 는 **학습 시점에만** VLA 의 중간 visual 표현을 사전학습 3D foundation model 의 latent 에 cosine 정렬시켜 공간 인지를 implicit 하게 주입합니다. 구조 변경·추가 입력·추론 비용이 전혀 없어 임의의 VLA 에 플러그인 가능하며, 표현 distillation 으로 데이터 효율과 수렴 속도까지 끌어올리는 것이 차별점입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 후보 base: `pi0` family 와 가장 가까움(논문이 RoboTwin 에서 $`\pi_{0}`$ + LoRA 를 직접 사용). 정렬 분기는 VLM backbone 중간층(visual 토큰)에서 forward hook 으로 가로채는 형태가 자연스럽고, action expert(flow-matching) 는 그대로 둔 채 보조 손실만 더하는 구조. VGGT target 추출기는 외부 동결 모델로 학습 그래프에 부착.

---

## 🚧 미해결 / 잠정

- `D_vla`, `D_3d`, `N`(visual 토큰 수), `V`(뷰 수) 구체 값은 base VLA·VGGT 구성에 종속 — (원문에 명시 없음 — base 설정 따름).
- positional embedding `E` 의 정확한 형태(학습형 vs 고정형)는 본문에 Ranftl et al. 참조만 있어 (원문에 명시 없음 — 가정으로 메움): DPT 계열 positional embedding 으로 가정.
- source 토큰 ↔ target 픽셀 위치 대응의 구체적 매핑(다운샘플 비율·정렬 방식)은 (원문에 명시 없음 — 가정으로 메움).
- `L_action` 의 구체 형(L1/L2/cross-entropy/flow-matching) 은 base 모델별로 다름(OpenVLA-OFT vs $`\pi_{0}`$) — base 규약 따름.
- 멀티뷰가 없는 단일 카메라 셋업에서의 VGGT target 구성 방식은 (원문에 명시 없음).
