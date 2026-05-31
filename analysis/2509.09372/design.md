# Design — VLA-Adapter: An Effective Paradigm for Tiny-Scale Vision-Language-Action Model

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
| 원문 제목 (영문) | VLA-Adapter: An Effective Paradigm for Tiny-Scale Vision-Language-Action Model |
| 링크 | [arXiv:2509.09372](https://arxiv.org/abs/2509.09372) |
| 분석 문서 | [`analysis/2509.09372/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-05-28 |

---

## 🧮 데이터 계약

타임스텝 $`t`$ 기준. 시간 축은 액션 청크 길이 $`H`$ (본문 $`H=8`$), Policy/VLM 레이어 수 $`M`$ (본문 $`M=24`$) 로 표기합니다.

- **입력** — 3인칭 이미지 $`\mathcal{X}_{t}^{v}`$: shape `(B, 3, Hpx, Wpx)`, RGB; VLM 비전 인코더(DINOv2 + SigLIP) 입력 정규화 (원문에 픽셀 통계 명시 없음 — 인코더 기본값 가정).
- **입력** — 그리퍼 이미지 $`\mathcal{X}_{t}^{g}`$: shape `(B, 3, Hpx, Wpx)`, RGB; 동일 정규화.
- **입력** — 언어 지시 $`\mathcal{L}_{t}`$: 토큰 시퀀스 `(B, L_text)`, int token id.
- **입력** — ActionQuery $`\mathcal{AQ}_{t}`$: 학습형 임베딩 `(B, N_aq, d)`, `N_aq=64`, `d=896` (hidden size).
- **입력** — 고유감각 상태 $`\mathcal{P}_{t}`$: shape `(B, d_proprio)`, float; 2-layer MLP $`\sigma_{0}`$ 로 proprio 임베딩 매핑 (정규화 통계 원문 미명시 — 데이터셋 평균/표준편차 가정).
- **입력** — 초기 액션 $`{\bf A}^{0}_{t}`$: shape `(B, H, d_action)`, **전부 0으로 초기화**; LN+MLP로 $`\widetilde{\bf A}^{0}_{t}`$ 임베딩.
- **VLM 중간 산출 (Policy 조건)** — Raw 잠재 $`\mathcal{C}_{t}^{\mathcal{R}}`$ 와 ActionQuery 잠재 $`\mathcal{C}_{t}^{\mathcal{AQ}}`$: 레이어 1–$`M`$ 전부에서 추출, 레이어별로 대응 Policy 레이어에 주입.
- **출력** — 액션 청크 $`{\bf A}^{M-1}_{t}`$: shape `(B, H, d_action)`, 연속값 (그리퍼 검증 시 `d_action=7` + gripper; 원문은 action chunk 8 dimensions 명시).

---

## 🧰 모듈 인터페이스

```python
def vlm_forward(x_v, x_g, lang_tokens, action_query) -> tuple[list[Tensor], list[Tensor]]:
    """Prismatic-VLM(DINOv2+SigLIP+Qwen2.5-0.5B) 전방 통과.
    레이어 1..M 각각의 Raw 잠재 C_R[l] 와 ActionQuery 잠재 C_AQ[l] 를 반환."""

def bridge_attention(a_latent, c_raw_l, c_aq_l, proprio_emb, g) -> Tensor:
    """한 Policy 레이어의 핵심. 두 cross-attn + 한 self-attn 결합.
    CA1: Q=a_latent, KV=sigma1(c_raw_l), 출력 * tanh(g) 로 게이팅.
    CA2: Q=a_latent, KV=sigma2(concat[c_aq_l, proprio_emb]).
    SA : Q=K=V=a_latent.
    셋을 concat 해 A_hat 반환."""

def policy_forward(C_R, C_AQ, A0, proprio) -> Tensor:
    """M 레이어 스택. 각 레이어 = bridge_attention + residual FFN.
    레이어 l 의 조건은 C_R[l], C_AQ[l]. 최종 LN+MLP 로 H-step 액션 청크 반환."""
```

- **`vlm_forward`** — 백본은 동결(frozen) 또는 LoRA 학습 둘 다 지원. 출력은 **전 레이어** hidden 으로, last-layer 만 쓰면 frozen 시 붕괴(분석 §📊 Appendix H).
- **`bridge_attention`** — `sigma1`, `sigma2` 는 MLP projection. 극경량화를 위해 세 어텐션 행렬의 projection layer를 공유(VLA-Adapter, 97MB); Pro 버전은 분리 + RoPE(207MB).
- **`policy_forward`** — Policy 레이어 수 = VLM 레이어 수($`M`$). L1 회귀 헤드로 종료. DiT 기반 변형도 존재(Appendix B)하나 기본은 L1.

---

## ⛓️ 불변식·가정

- (가정 1) — Policy 레이어 수는 VLM 레이어 수와 동일($`M`$)하며, Policy 레이어 $`\tau`$ 는 VLM 레이어 $`\tau`$ 의 조건을 받는다 ($`0\leq\tau\leq M-1`$).
- (가정 2) — Raw 주입 게이트 $`g`$ 는 0으로 초기화되고 $`\tanh(g)\in[-1,1]`$ 로 클램프된다 — 학습 초기 Raw 영향이 0에서 출발해 분포 안정성을 보장한다.
- (가정 3) — ActionQuery 는 VLM 시퀀스에 삽입되어 attention 에 참여하는 진짜 학습형 토큰이어야 한다(마스크형 0-토큰이 아님). 그래야 백본 동결 시에도 from-scratch 학습이 가능하다.
- (가정 4) — ActionQuery 주입 정도는 1(완전 주입), Raw 주입 정도만 학습형 $`\tanh(g)`$ — 절제 실험(Table 8)이 이 조합을 최적으로 지지한다.
- (가정 5) — 초기 액션은 전부 0 텐서이며, 모델은 회귀로 한 번에 $`H`$-스텝 청크를 산출한다(반복적 denoising 아님, L1 기본형 기준).

---

## 📊 하이퍼파라미터·손실

- 손실 식 (L1 회귀, Eq. (2)):

$$\min_{\theta}\mathcal{J}(\theta)=\mathbb{E}_{\mathbf{A}_{t},\mathcal{C}_{t}^{\mathcal{R}},\mathcal{C}_{t}^{\mathcal{AQ}},{\sigma_{0}}({\mathcal{P}_{t}}),\tau}\Big[\big\|\pi_{\theta}(\mathbf{A}_{t}^{\tau},\mathcal{C}_{t}^{\mathcal{R}},\mathcal{C}_{t}^{\mathcal{AQ}},{\sigma_{0}}({\mathcal{P}_{t}}),\tau)-\mathbf{A}_{t}\big\|_{1}\Big].$$

- Bridge Attention 결합 (Eq. (1)):

$$\widehat{\bf{A}}_{t}^{\tau}=[\text{CA}_{1}\left(\widetilde{\bf{A}}^{\tau}_{t},\sigma_{1}(\mathcal{C}_{t}^{\mathcal{R}})\right)\cdot\tanh(g),\text{CA}_{2}(\widetilde{\bf{A}}^{\tau}_{t},\sigma_{2}[\mathcal{C}_{t}^{\mathcal{AQ}},\sigma_{0}({\mathcal{P}_{t}})]),\text{SA}\left(\widetilde{\bf{A}}^{\tau}_{t},\widetilde{\bf{A}}^{\tau}_{t}\right)].$$

- 하이퍼:

  | 이름 | 값 | 출처 |
  |------|----|----|
  | `backbone` | Qwen2.5-0.5B (Prismatic-VLM) | §3.1, Table F2 |
  | `Layer (τ/M)` | 24 | Table F2 |
  | `Number of ActionQuery` | 64 | Table F2, §4.5 |
  | `Hidden size` | 896 | Table F2 |
  | `Attention head` | 8 | Table F2 |
  | `Action chunk (H)` | 8 | Table F2 |
  | `Intermediate layers of VLM` | 1–24 (전 레이어) | Table F2 |
  | `Policy trainable params` | 97.3M | Table F2 |
  | `VLA-Adapter total trainable params` | 197.2M | Table F2 |
  | `optimizer` | AdamW | §F.1 |
  | `tuning scheme` | LoRA (백본) / 동결 변형 지원 | §F.1, Table 3 |
  | `learning rate` | 1e-4 | Table F1 |
  | `scheduler` | cosine-annealing + warmup | §F.1 |
  | `warmup step` | 10% | Table F1 |
  | `batch size` | 16 | Table F1 |
  | `max training step` | 150,000 | Table F1 |
  | `Ratio g init` | 0 (`tanh` 클램프) | §3.3 |
  | `hardware` | 4× NVIDIA H100 | §4 |

---

## 🎯 평가 메트릭

- **지표** — Success Rate (0–100) · **벤치마크** — LIBERO (Spatial/Object/Goal/Long) · **비교 baseline** — OpenVLA-OFT(7B), π0(3B), GR00T N1(2B), SmolVLA, VLA-OS(0.5B) (Table 5)
- **지표** — Avg. len of completed tasks (0–5) + 연속 성공 수 · **벤치마크** — CALVIN ABC→D 제로샷 일반화 · **비교 baseline** — OpenVLA-OFT, VPP, Seer (Table 6)
- **지표** — Throughput (Hz, ↑) / Latency (Sec, ↓) · **임계값** — VLA-Adapter 219.2Hz / 0.0365s (Table 4)
- **지표** — 동결 백본 성공률 · **임계값** — VLA-Adapter 86.4 vs OpenVLA-OFT 0.0 vs SmolVLA 77.0 (LIBERO-Long, Table 3)
- **절제 축** — (1) ActionQuery 개수(1~512, 최적 64), (2) 조건 타입(레이어×Raw/AQ, Table 7), (3) 주입 정도(Table 8)

---

## ✨ 변경 의도 (intent)

prior art는 VL→A 브리징에서 단일 선택(예: π0 = 전 레이어 Raw + flow-matching, OpenVLA-OFT = last-layer ActionQuery)을 했지만, 어느 레이어·어느 타입이 본질적인지에 대한 체계 분석이 없었습니다. VLA-Adapter는 "중간층 Raw는 멀티모달 통합에, 심층 ActionQuery는 누적 정보에 유리하고, 전 레이어가 보편적으로 낫다"는 발견을 근거로, **두 타입을 전 레이어에서 동시에** Bridge Attention(2 cross-attn + 1 self-attn)으로 결합하되 Raw 주입만 학습형 게이트 $`\tanh(g)`$ 로 선별합니다. 그 결과 0.5B 백본 + 로봇 데이터 사전학습 없음으로 7B급 성능과 최고 추론 속도를 내고, 백본 동결 시에도 동작합니다(last-layer만 쓰는 OFT는 동결 시 붕괴).

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 후보 base: `smolvla` family 와 가장 가깝습니다(소형 백본 + 동결 VLM 연구 계열, 본문이 SmolVLA를 직접 비교군으로 사용). 액션 헤드 측면에서는 flow-matching 의 `pi0`/`pi05` 와 대비되는 L1-회귀 + cross-attention adapter 구조이므로, `pi0` 의 action expert를 Bridge Attention(전 레이어 cross-attn + 학습형 ratio g)로 치환하는 변형 매핑도 가능 후보입니다.

---

## 🚧 미해결 / 잠정

- 이미지 해상도·픽셀 정규화 통계는 원문에 명시 없음 — 비전 인코더(DINOv2/SigLIP) 기본값으로 가정.
- proprio 정규화 통계 출처가 본문에 없어 "데이터셋 전체 평균/표준편차" 로 가정.
- `d_action` 의 정확한 값은 임베디먼트 의존(본문 실세계는 6-DOF + 1-DOF 그리퍼, action chunk 8 dimensions 명시) — 다지 손 매핑 시 재설정 필요.
- LoRA rank/alpha 등 세부 설정은 본문 미명시(Hu et al. 2022 인용만).
- `sigma1`/`sigma2`/`sigma0` MLP의 정확한 층 폭·깊이는 부분 명시(proprio는 2-layer MLP) — 나머지는 가정으로 메움.
- DiT 기반 Policy 변형의 조건 변조(conditional modulation) 세부는 Appendix B에 있으나 본 Design은 기본 L1 경로만 고정.
