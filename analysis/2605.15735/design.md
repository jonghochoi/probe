# Design — UAM: A Dual-Stream Perspective on Forgetting in VLA Training

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
| 원문 제목 (영문) | UAM: A Dual-Stream Perspective on Forgetting in VLA Training |
| 링크 | [arXiv:2605.15735](https://arxiv.org/abs/2605.15735) |
| 분석 문서 | [`analysis/2605.15735/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-05-26 |

---

## 🧮 데이터 계약

- **입력 — 관찰 이미지** `I_t`: shape `(B, V, 3, H, W)`, dtype `float32 / bf16`, 정규화는 백본 VLM(Bagel/Qwen-VL 계열)의 ImageNet-style mean/std. ALOHA real 실험은 `V=3`(primary + left wrist + right wrist), 원본 해상도 `640×480`(4:3, §11.1). 시뮬레이션에서는 `V=1`.
- **입력 — 언어 지시** `L`: tokenized string, shape `(B, T_L)`, 백본 VLM 의 tokenizer 와 동일. byte-level / SentencePiece 가정은 백본 의존.
- **입력 — 시점 상태(proprioception)** `s_t`: shape `(B, D_state)`, action expert 에 직접 주입 (§9.1 의 $`\pi_0`$-style 와 동일 위치). dtype `float32`, 정규화 통계는 (원문에 명시 없음 — 데이터셋 mean/std 가정).
- **출력 — 액션 청크** `a_{t:t+H}`: shape `(B, H, D_act)`. ALOHA bimanual 의 경우 `D_act` 는 양손 joint + gripper. Calvin `H=10`, RoboTwin `H=16` (3-step subsample → effective horizon 48), real-robot `H=24` (§12).
- **출력 — 보조 목표 관찰** `\hat{I}_{t+1}`: shape `(B, 3, H, W)`, $`\mathcal{L}_{\text{wm}}`$ 학습 시에만 사용. 단일 step denoising 으로 *전체 이미지 재구성을 수행하지 않고* 중간 표상만 활용한다고 본문(§13)이 명시.
- **토큰 라우팅 계약** — ViT 인코딩 토큰 → semantic expert($`E_{\text{sem}}`$), VAE 인코딩 토큰 → dorsal expert($`E_{\text{dor}}`$). Semantic token grid: ViT patch 14 → `14×18 = 252` tokens (640×480 입력 기준). Dorsal token grid: VAE stride 16 → `12×16 = 192` tokens (§11.1).
- **시간 축** — 모든 시퀀스는 `chunk_size = H`, action sampling stride 는 데이터셋별. 절대 시점 좌표 미사용.

---

## 🧰 모듈 인터페이스

```python
def semantic_expert(I_t, L, theta_sem) -> Z_sem:
    """ViT 토큰을 처리하는 사전학습 VLM 경로. ventral(What) 표상을 산출."""

def dorsal_expert(X_dor, theta_dor) -> Z_dor:
    """VAE 토큰을 처리하는 사전학습 generative UMM 경로. dorsal(Where/How) 시각 표상을 산출.
    X_dor ∈ {I_t (visual tokens), q (learnable queries)} 중 UAM 채택안은 visual tokens."""

def action_expert(Z_sem, Z_dor, s_t, theta_act) -> a_chunk:
    """MoT 결합으로 두 시각 경로 + proprio 를 받아 flow-matching 으로 액션 청크 생성."""

def visual_dynamics_head(Z_dor_internal, theta_wm) -> I_hat_next:
    """Dorsal expert 내부 표상에서 다음 시점 관찰을 예측하는 보조 head.
    BagelVLA 의 단일 step denoising 메커니즘을 사용 — 전체 이미지 복원이 아닌
    중간 표상을 통한 학습 신호 부과."""

def UAM_forward(I_t, L, s_t) -> (a_chunk, I_hat_next):
    Z_sem = semantic_expert(I_t, L, theta_sem)
    Z_dor = dorsal_expert(I_t, theta_dor)            # visual tokens 변형
    a_chunk = action_expert(Z_sem, Z_dor, s_t, theta_act)
    I_hat_next = visual_dynamics_head(Z_dor, theta_wm)   # training only
    return a_chunk, I_hat_next
```

- 세 expert 는 동일한 self-attention layer 깊이를 공유하되 parameter set 이 분리된 *parallel MoT* 결합. 토큰 간 정보 교환은 attention mask 로 제어 (§9, Fig. 7).
- Action expert 는 flow-matching (BagelVLA 의 dual flow-matching framework + single-step denoising, §9.3) 을 사용.
- `theta_sem`, `theta_dor` 모두 *frozen 이 아니며 gradient 가 흐름* (원문 핵심: "no parameter freezing, no gradient stopping").

---

## ⛓️ 불변식·가정

- (가정 1) — **인코더 분리 불변식**: ViT 가 생성한 시각 토큰은 오직 $`E_{\text{sem}}`$ 로, VAE 가 생성한 시각 토큰은 오직 $`E_{\text{dor}}`$ 로 라우팅한다. 동일 입력 이미지를 두 인코더가 *독립적으로* 임베딩하는 것이 dual-pathway 구조의 핵심.
- (가정 2) — **Prior 결합 불변식**: $`E_{\text{sem}}`$ 와 $`E_{\text{dor}}`$ 의 초기 가중치는 같은 UMM 패밀리(원문 채택안 = Bagel) 출신이어야 한다. 본문 §9.3 가 PaliGemma 적용을 제외한 근거 — 이해와 생성 사이에 광범위한 추가 정렬("extensive additional alignment between multimodal understanding and generation")이 필요하다는 점 — 가 이 가정.
- (가정 3) — **보조 손실 활성화 불변식**: $`\lambda > 0`$ 이어야 Dorsal 경로가 *load-bearing* 해진다. §3.3 Variant 3a vs 3b 비교에서 확인된다.
- (가정 4) — **MoT 라우팅 불변식**: 세 expert 를 동일 attention layer 깊이로 정렬해 같은 토큰 시퀀스를 공유 attention 으로 처리한다 (parallel routing). 직렬 결합으로는 본 논문의 정량 주장이 성립하지 않음.
- (가정 5) — **단일 step denoising 가정**: 추론 시 world-model expert 가 전체 이미지를 재구성하지 않고 첫 번째 denoising step 의 중간 표상만 사용한다(§13). 이 가정이 깨지면 latency 비용이 본문 보고치(1500 ms)를 크게 초과.
- (가정 6) — **정규화 통계 출처** — (원문에 명시 없음 — 가정으로 메움) 액션·proprio 정규화는 학습 데이터셋 전체 평균/표준편차로 가정.

---

## 📊 하이퍼파라미터·손실

손실 식:

$$\mathcal{L}_{\text{total}}=\mathcal{L}_{\text{act}}+\lambda\mathcal{L}_{\text{wm}}(\hat{I}_{t+1},I_{t+1})$$

- $`\mathcal{L}_{\text{act}}`$ — flow-matching action loss (BagelVLA 의 dual flow-matching 변형). 구체 weight scheduling 은 (원문 미명시).
- $`\mathcal{L}_{\text{wm}}`$ — goal observation prediction loss. 단일 step denoising 출력 vs 다음 시점 관찰 간 거리.

Forgetting metric (학습 손실이 아니라 평가 지표):

$$\Delta(f_{\text{VLA}})\;=\;1-\frac{S(f_{\text{VLA}})}{S(f_{\text{VLM}})}$$

하이퍼파라미터:

| 이름 | 값 | 출처 |
|------|----|----|
| `lr (Qwen 계열)` | `1e-5` | §8, §12 |
| `lr (PaliGemma 계열)` | `5e-5` | §8, §12 |
| `train_steps (Calvin / RoboTwin / real)` | `30,000` | §12 |
| `effective_batch_size (Calvin)` | `192` (8× A800) | §12 |
| `chunk_size H (Calvin)` | `10` | §12 |
| `chunk_size H (RoboTwin)` | `16` (3-step subsample → horizon 48) | §12 |
| `chunk_size H (real-robot)` | `24` | §12 |
| `num_demos (real-robot)` | `3,000` ALOHA bimanual | §4 |
| `dorsal_init` | Bagel 사전학습 체크포인트 | §4, §9.3 |
| `vlm_init` | Bagel 사전학습 체크포인트 | §4, §9.3 |
| `action_expert size` | `2B` MoT | Tab. 4 |
| `dorsal_expert size` | `7B` MoT | Tab. 4 |
| `vlm_expert size` | `7B` | Tab. 4 |
| `lambda (\mathcal{L}_{wm} 가중)` | (원문 미명시) | §3.3 |
| `vit_patch_size` | `14` (→ 252 tokens) | §11.1 |
| `vae_stride` | `16` (→ 192 tokens) | §11.1 |
| `parallel framework` | FSDP + packed datasets | §12 |
| `optimizer` | (원문 미명시 — AdamW 가정) | §12 |

---

## 🎯 평가 메트릭

- **지표** — `Forgetting (Δ)` · **임계값** — *Δ ≤ 0.05* (95%+ 보존) · **비교 baseline** — 원본 VLM 점수 $`S(f_{\text{VLM}})`$
  - 측정 벤치마크: MMMU, MME-P, MME-S, MMBench, MM-Vet, MathVista, MMStar, TextVQA (Tab. 2).
- **지표** — `Simulated Action Accuracy` · **임계값** — Calvin ABC-D 1,000 task × length 5 의 평균 task completion length · **비교 baseline** — Qwen-$`\pi_0`$ (2-expert), Variant 2a (VLM-init Dorsal), Variant 3a (Gen-init no WM).
- **지표** — `RoboTwin Success Rate` · **임계값** — 16-task × 100 trial × unseen instructions 의 평균 success rate · **비교 baseline** — 동일 6-variant sweep.
- **지표** — `Real-world OOD Success Rate` · **임계값** — ALOHA bimanual 각 task type 20회 / randomized initial pose · **비교 baseline** — Qwen-$`\pi_0`$ 2-expert + Variant 2a (VLM-init Dorsal). OOD 카테고리: unseen objects / unseen object-target compositions / unseen distractors / language variation (pinyin, Chinese-English code-mixing, fully Chinese).
- **지표** — `Inference Latency` · **임계값** — single-step latency (ms) · **비교 baseline** — $`\pi_{0.5}`$ (250 ms), Qwen7B + MLP (1000 ms), Qwen7B-$`\pi_0`$ (1300 ms). UAM 보고치: 1500 ms.
- **정성 지표** — Attention map 시각화로 What/How 분기의 emergent 발생 확인 (§4.3, §11). 정량 임계 없음 — 가설 검증용.

---

## ✨ 변경 의도 (intent)

기존 VLA 망각 완화 두 갈래 — VLM freeze 와 VL co-training — 를 *대증적 처방* 으로 진단하고, 망각의 *구조적 원인* 인 단일 인코더 병목을 architectural separation 으로 해체합니다. 한 축은 Bagel 같은 *이해+생성 결합* 사전학습의 generative prior 를 *제어 경로*로 돌려 의미 경로 부담을 덜어주는 일이고, 다른 한 축은 visual-dynamics 보조 손실로 그 경로에 *중간 추론*(장면이 어떻게 변하는가)을 떠맡깁니다. 그래서 frozen·gradient-stop·VL replay 없이 end-to-end action-only 학습만으로 95%+ VLM 보존이 가능해지고, OOD 일반화에서 비교군 최고치를 달성합니다. 결국 의미 보존을 데이터·동결 문제에서 *구조 문제로 재정의* 한 것이 이 설계의 의도입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 후보 base: `pi0` / `pi0_fast` family 와 가까움 — flow-matching action expert + MoT 결합 패턴이 직접 일치. 단 lerobot 표준 PI0 는 2-expert (VLM + action) 이며, UAM 은 *세 번째 generative expert 와 별도 VAE 인코더 + visual-dynamics head* 가 신규 추가되어야 함. 또한 lerobot 의 표준 vision tower 는 단일 인코더 — `processor` 단에서 ViT/VAE 이중 인코딩 분기 추가가 필요. `smolvla` / `act` / `diffusion` family 는 매핑 곤란.

---

## 🚧 미해결 / 잠정

- visual-dynamics 손실 가중 $`\lambda`$ 의 구체 값이 본문에 미명시 — 가정으로 비워둠.
- Dorsal expert 의 layer 수 / hidden dim 등 세부 hyper-architecture 는 Bagel 체크포인트 구조에 종속이며 본문 단독으로 재구성 불가.
- Optimizer 종류 (AdamW 가정) 및 LR warmup/decay schedule 미명시.
- Action 및 proprio 정규화 통계의 정확한 출처 미명시 — 데이터셋 전체 평균/표준편차로 가정.
- `single-step denoising` 의 정확한 수식 / step skipping schedule 은 BagelVLA([hu2026bagelvla])의 별도 인용에 의존 — 본문만으로는 완전 명세 불가.
- Real-world OOD 평가의 task 별 시도 횟수 외 평가자 blinding 여부는 본문에 명시 없음.
- Tactile / proprioceptive 입력은 본 논문 범위 밖 — PROBE 측에서 P2 모달리티를 합칠 때 어느 expert 로 라우팅할지는 UAM 본문 결정 사항이 아님.
