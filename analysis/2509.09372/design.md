# Design — VLA-Adapter: An Effective Paradigm for Tiny-Scale Vision-Language-Action Model

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
| 원문 제목 (영문) | VLA-Adapter: An Effective Paradigm for Tiny-Scale Vision-Language-Action Model |
| 링크 | [arXiv:2509.09372](https://arxiv.org/abs/2509.09372) |
| 분석 문서 | [`analysis/2509.09372/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-09 |

---

## 🧮 데이터 계약

시간 축은 의미 단위(`chunk_size` $`H`$, VLM/Policy 층 수 $`M`$)로 기록합니다.

- **입력 — 3rd-view 이미지** `X^v`: shape `(B, 3, H_img, W_img)`, float, VLM
  비전 인코더(DINOv2 + SigLIP) 정규화 가정.
- **입력 — gripper 이미지** `X^g`: shape `(B, 3, H_img, W_img)`, float, 동일
  비전 정규화.
- **입력 — instruction** `L`: 토큰 시퀀스 `(B, L_text)`, int(token id).
- **입력 — ActionQuery** `AQ`: 학습 임베딩 `(B, N_aq, d)`, `N_aq=64`(기본),
  `d=896`(hidden size). VLM 시퀀스에 삽입되어 attention 참여.
- **입력 — proprioception** `P`: shape `(B, d_proprio)`, float. 2-layer MLP →
  `σ0(P)` 임베딩 `(B, d)`. (원문에 `d_proprio` 명시 없음 — 임베디먼트별 가정.)
- **입력 — 초기 액션** `A^{τ=0}`: 전부-0, shape `(B, H, d_action)`, `H=8`.
  LN+MLP → `Ã^0` `(B, H, d)`.
- **VLM 출력 조건 — Raw latent** `C^R`: 층별 `(B, M, S_v, d)` 또는 대응 층
  주입용 `(B, S_v, d)` × `M`. `M=24` (intermediate layers 1–24).
- **VLM 출력 조건 — ActionQuery latent** `C^AQ`: 층별 `(B, N_aq, d)` × `M`.
- **출력 — 액션 청크** `A^{M-1}`: shape `(B, H, d_action)`, float, `H=8`. (정규화
  통계는 원문 미명시 — 데이터셋 표준화 가정.) `d_action` 은 임베디먼트 의존
  (LIBERO/CALVIN/실로봇 8-dim 보고).

---

## 🧰 모듈 인터페이스

base 좌표(file:line)는 들어오지 않습니다 — 호출 계약만 기록합니다.

```python
def vlm_backbone(X_v, X_g, L, AQ) -> tuple[list[Tensor], list[Tensor]]:
    """동결(또는 LoRA) VLM. 층별 Raw latent C^R 와 ActionQuery latent C^AQ 를
    반환. 기본 백본 Qwen2.5-0.5B(Prismatic), M=24 층. 백본 동결 시 C^R/C^AQ 만
    조건으로 흐르고 VLM 파라미터는 학습되지 않음(ActionQuery 임베딩은 학습)."""

def bridge_attention(A_tau, C_R, C_AQ, sigma0_P, g) -> Tensor:
    """한 Policy 층의 핵심 블록. 두 cross-attn + 한 self-attn.
      CA1: Q=Ã^τ, (K,V)=σ1(C^R)          → Raw 주입, 출력에 tanh(g) 곱
      CA2: Q=Ã^τ, (K,V)=σ2([C^AQ, σ0(P)]) → ActionQuery+proprio 주입(비율 1)
      SA : Q=K=V=Ã^τ                       → self
    세 결과를 concat → Â^τ. 반환 후 residual FFN 으로 Ã^{τ+1}."""

def policy_forward(C_R_layers, C_AQ_layers, P, A0) -> Tensor:
    """L1 기반 Policy. Policy 층 수 = VLM 층 수(M=24). τ-번째 층은 대응하는
    VLM τ-층의 (C^R, C^AQ) 를 받음. 최종 Ã^{M-1} 을 LN+MLP 로 액션 청크
    A^{M-1} (B,H,d_action) 로 사상. 총 trainable 97.3M(Policy) / 197.2M(전체)."""

def gate(g) -> Tensor:
    """학습 스칼라 g(0 초기화)에 tanh 적용 → [-1,1]. Raw 주입량 자율 조절,
    분포 안정화. CA1 출력에만 곱해지는 비대칭 게이트."""
```

- `vlm_backbone` — VLM. 외부 호출 계약: 출력 조건은 Policy 의 층별 입력.
- `bridge_attention` — Policy 층 내부 단위. `g` 는 layer-local 학습 파라미터.
- `policy_forward` — L1 손실(아래 📊)과 직접 연결. 옵티마이저 AdamW.
- `gate` — Raw 전용. ActionQuery 측 비율은 상수 1(게이트 없음).

---

## ⛓️ 불변식·가정

- **(가정 1)** — Policy 층 수와 VLM 층 수가 같다($`M=24`$). τ-번째 Policy 층은
  반드시 τ-번째 VLM 층의 조건을 받는 1:1 대응. 이 정렬이 깨지면 "전층 조건" 의
  의미가 사라짐.
- **(가정 2)** — Raw 게이트는 0 으로 초기화되어야 한다. $`g=0 \Rightarrow \tanh(g)=0`$ 이므로 학습 초기 Raw 기여=0(=ActionQuery 위주)에서 출발 → 안정적 warm-start. 비-0 초기화는 분포 붕괴 위험(저자 설계 의도).
- **(가정 3)** — Raw 와 ActionQuery 의 주입 비대칭(Raw=$`\tanh(g)`$, AQ=1)이
  최적이다. ablation(Table 8)에서 이 조합만 95.0, 나머지는 ≤92.6. 둘 다 게이트
  또는 둘 다 상수면 성능 저하.
- **(가정 4)** — ActionQuery 개수는 멀티모달 집약과 중복 사이 균형점(기본 64).
  너무 적으면 집약 부족, 너무 많으면 간섭(Figure 8).
- **(가정 5)** — 액션 분포가 L1 회귀로 충분히 표현 가능(주로 단봉)하다는 암묵
  가정. 다봉 접촉 전략에서는 mode-averaging 위험(분석 ⚖️ 참조).
- **(가정 6)** — 백본 동결이 성능을 유지하려면 "전층 조건 + 어댑터" 가 필수.
  마지막 층 표현만으로는 로봇 사전학습 없는 백본에서 불충분(§4.1 결론).

---

## 📊 하이퍼파라미터·손실

- **손실 식 (L1 회귀, Eq. 2)**:

$$\min_{\theta}\mathcal{J}(\theta)=\mathbb{E}_{\mathbf{A}_{t},\mathcal{C}_{t}^{\mathcal{R}},\mathcal{C}_{t}^{\mathcal{AQ}},\sigma_{0}(\mathcal{P}_{t}),\tau}\Big[\big\|\pi_{\theta}(\mathbf{A}_{t}^{\tau},\mathcal{C}_{t}^{\mathcal{R}},\mathcal{C}_{t}^{\mathcal{AQ}},\sigma_{0}(\mathcal{P}_{t}),\tau)-\mathbf{A}_{t}\big\|_{1}\Big]$$

- **Bridge Attention 융합 (Eq. 1)**:

$$\widehat{\mathbf{A}}_{t}^{\tau}=\left[\text{CA}_{1}\left(\widetilde{\mathbf{A}}^{\tau}_{t},\sigma_{1}(\mathcal{C}_{t}^{\mathcal{R}})\right)\cdot\tanh(g),\ \text{CA}_{2}\left(\widetilde{\mathbf{A}}^{\tau}_{t},\sigma_{2}[\mathcal{C}_{t}^{\mathcal{AQ}},\sigma_{0}(\mathcal{P}_{t})]\right),\ \text{SA}\left(\widetilde{\mathbf{A}}^{\tau}_{t},\widetilde{\mathbf{A}}^{\tau}_{t}\right)\right]$$

- 하이퍼:

  | 이름 | 값 | 출처 |
  |------|----|----|
  | Backbone | Qwen2.5-0.5B (Prismatic VLM) | §F.2, Table F2 |
  | Layer ($`\tau`$ / $`M`$) | 24 | §F.2, Table F2 |
  | Number of ActionQuery ($`N_{aq}`$) | 64 | §F.2, Table F2 |
  | Hidden size ($`d`$) | 896 | §F.2, Table F2 |
  | Attention head | 8 | §F.2, Table F2 |
  | Action chunk ($`H`$) | 8 | §F.2, Table F2 |
  | Intermediate layers of VLM | 1–24 | §F.2, Table F2 |
  | Policy trainable params | 97.3M | §F.2, Table F2 |
  | Total trainable params | 197.2M | §F.2, Table F2 |
  | Optimizer | AdamW + LoRA | §F.1 |
  | Learning rate | 1e-4 | §F.1, Table F1 |
  | LR schedule | cosine-annealing + warmup | §F.1 |
  | Warmup step | 전체의 10% | §F.1, Table F1 |
  | Batch size | 16 | §F.1, Table F1 |
  | Max training step | 150,000 | §F.1, Table F1 |
  | Hardware | 4× NVIDIA H100 | §4 |
  | Raw 게이트 $`g`$ 초기값 | 0 (→ $`\tanh(g)=0`$) | §3.3 |

---

## 🎯 평가 메트릭

- **지표** — `Success Rate` (0–100, 높을수록 좋음; subtask 당 50 회 반복) ·
  **임계값** — LIBERO Avg 97.3 (Pro 98.5) / LIBERO-Long 95.0 · **비교 baseline**
  — OpenVLA-OFT(7B) 97.1, π0(3B) 94.2, SmolVLA(2.2B) 88.8, VLA-OS(0.5B) 85.6.
- **지표** — `Avg. len` (CALVIN ABC→D, 0–5, 연속 완료 길이) · **임계값** — 4.42
  (Pro 4.50) · **비교 baseline** — OpenVLA-OFT 4.10, VPP 4.33, Seer Large 4.28.
- **지표** — `Throughput` (Hz, ↑) / `Latency` (Sec, ↓), 8-dim action chunk ·
  **임계값** — 219.2 Hz / 0.0365s · **비교 baseline** — OpenVLA-OFT 71.4 Hz /
  0.1120s, OpenVLA 4.2 Hz.
- **지표(동결 백본)** — `Success Rate` · **임계값** — 86.4 · **비교 baseline** —
  OpenVLA-OFT 0.0, SmolVLA 77.0.

---

## ✨ 변경 의도 (intent)

기존 bridging 은 (a) VLM 의 어느 *한* 층 표현(last 또는 intermediate)이나 (b)
학습 query 중 *하나만* 을 액션 조건으로 썼습니다(π0=전층 Raw, OFT=마지막층
ActionQuery, GR00T N1=중간층 Raw). VLA-Adapter 의 변경 의도는 **VLM 전층의 Raw
와 ActionQuery 를 *동시에*, 대응 Policy 층에 1:1 주입하되, Raw 만 0-초기화
$`\tanh(g)`$ 게이트로 자율 선별 주입** 하는 것입니다. 이로써 (1) 최적 층 선택을
없애 설계를 범용화하고, (2) 의미 편향된 깊은 Raw 의 해악을 게이트로 억제하며,
(3) 로봇 사전학습 없는 0.5B·동결 백본에서도 7B 급 SOTA 와 추론 속도 1 위를
달성합니다. 액션 헤드는 플로우 매칭/디퓨전이 아닌 단순 L1 회귀를 채택(저자
실험상 DiT 대비 우월).

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 후보 base: 액션 디코더 패턴은 `smolvla`(동결-VLM + 경량 액션
  전문가) family 와 가장 가깝고, 전층 조건 탭/액션 전문가 구조는 `pi0`/`pi05`
  의 action-expert 분기와도 인접합니다. 단 손실이 flow-matching 이 아니라 L1
  회귀이고, Bridge Attention(2 cross + 1 self + Raw 전용 tanh 게이트)은 기존
  foundry 의 액션 전문가에 *추가 모듈* 로 들어가는 형태라 1:1 매핑은 아닐 수
  있습니다. 실제 매핑 가부는 `/implement-design` 가 판단.

---

## 🚧 미해결 / 잠정

- **`d_proprio` / `d_action` 의 정확한 차원** — 임베디먼트별로 다르고 본문에
  스칼라 명시 없음(LIBERO/CALVIN/실로봇 action chunk 는 8-dim 보고). 데이터셋
  의존으로 가정.
- **액션/관측 정규화 통계의 출처** — 본문 미명시 → "데이터셋 전체 평균/표준편차"
  로 가정.
- **`σ1`/`σ2` MLP 의 층수·차원** — Bridge Attention 내 투영 MLP 의 구체 구성은
  본문에 수치 없음(VLA-Adapter 는 세 attention 투영층을 *공유* 해 97MB, Pro 는
  분리해 207MB 라는 정성 정보만 Appendix I).
- **CA₂ 의 proprio concat 위치·기여** — ActionQuery 와 concat 후 σ2 통과는
  명시되나 proprio 단독 ablation 부재 → 비중 불명.
- **"단일 컨슈머 GPU 8 시간" 학습 구성** — abstract 주장이나 본문에 그 정확한
  하드웨어·step·백본 구성 명시 없음. 본 Design 의 하드웨어 행은 본문 4× H100
  기준.
- **DiT 기반 Policy 세부** — 대안으로만 언급(Appendix B), L1 채택으로 본 Design
  스펙에서는 제외.
