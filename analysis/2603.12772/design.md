# Design — PVI: Plug-in Visual Injection for Vision-Language-Action Models

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | PVI: Plug-in Visual Injection for Vision-Language-Action Models |
| 링크 | [arXiv:2603.12772](https://arxiv.org/abs/2603.12772) |
| 분석 문서 | [`analysis/2603.12772/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-16 |

---

## 🧮 데이터 계약

- **입력 — 언어 지시** `l`: 토큰화된 instruction (base VLA 인터페이스 그대로).
- **입력 — 다시점 이미지** $`\{I_v\}_{v=1}^{V}`$: VLM 백본 입력. shape `(B, V, 3, H, W)`, uint8/정규화는 base VLA 전처리 따름.
- **입력 — 보조 관측** (PVI 전용): V-JEPA2 경로는 4 fps 로 샘플한 `n_frames` 비디오 클립 `(B, n_frames, 3, H, W)` (기본 8, 최적 2–4); DINOv2 경로는 단일 이미지 `(B, 3, H, W)`.
- **입력 — proprioception / noisy action 토큰**: base DiT 의 초기 토큰 $`\mathbf{h}_{0}\in\mathbb{R}^{M\times D}`$ 로 인코딩·concat (`M` = 토큰 수, `D` = hidden dim). main·copy 양쪽 공통 입력.
- **중간 — VLM 임베딩** `z_vl` ∈ `(B, S, D)`: main DiT 조건 입력 (S = 시퀀스 길이).
- **중간 — 보조 특징** `z_aux` shape `(B, L, d_E)`: frozen encoder `E` 출력, $`\mathbf{z}_{\mathrm{aux}}\in\mathbb{R}^{L\times d_E}`$ (`L` = 보조 시퀀스 길이, `d_E` = encoder 차원). projection 후 `z̃_aux` shape `(B, L, D)`.
- **출력 — 행동 시퀀스** `a = (a_1,…,a_H)`: horizon `H` 의 연속 행동, flow-matching velocity 적분으로 생성. dtype float, 정규화는 base VLA 의 action 통계 따름 (원문 명시 없음 — 가정으로 메움).

---

## 🧰 모듈 인터페이스

```python
def extract_aux_features(E_frozen, obs) -> Tensor:  # (B, L, d_E)
    """frozen 보조 encoder E 로 원시 관측(비디오/이미지)에서 고정차원 특징 시퀀스 추출."""

def project_aux(z_aux, W_proj_zero_init) -> Tensor:  # (B, L, D)
    """z̃_aux = z_aux @ W_proj. W_proj 는 zero-init, trainable. DiT 임베딩 공간으로 매핑."""

def pvi_copy_block(f_copy_i, h_copy_prev, z_aux_tilde) -> Tensor:  # (B, M, D)
    """main DiT i-번째 블록의 trainable 복제본. 조건 입력만 z_vl→z̃_aux 로 치환,
       나머지 아키텍처/조건화 메커니즘은 동일. main 가중치로 초기화."""

def pvi_inject(f_main_i, h_main_prev, z_vl, h_copy_i, Z_i_zero_init) -> Tensor:  # (B, M, D)
    """h_main_i = f_main_i(h_main_prev, z_vl) + Z_i(h_copy_i).
       Z_i 는 zero-init 선형 주입 layer. frozen main 경로 보존 + layer-wise 잔차 주입."""
```

- **`extract_aux_features`** — frozen `E` (V-JEPA2 / DINOv2), gradient 차단. base VLA 와 독립.
- **`project_aux`** — trainable, zero-init $`\mathbf{W}_{\mathrm{proj}}\in\mathbb{R}^{d_E\times D}`$. 학습 시작 시 copy branch 에 0 조건 신호.
- **`pvi_copy_block`** — `N` 개 블록, main DiT 가중치로 초기화, trainable. 조건만 `z̃_aux`.
- **`pvi_inject`** — frozen `f_main_i` 출력에 `Z_i(h_copy_i)` 를 더함. `Z_i` 만 trainable·zero-init. 손실/optimizer 와의 관계: 표준 flow-matching 손실의 gradient 만 받음(보조 supervision 없음).

---

## ⛓️ 불변식·가정

- **(초기 동일성)** `W_proj = 0` ∧ 모든 `Z_i = 0` 이면, 학습 step 0 에서 `h_main_i = f_main_i(h_main_prev, z_vl)` 로 원본 VLA 와 **기능적으로 동일** — 보조 경로가 main 을 교란하지 않음.
- **(구조 정렬)** copy branch 는 main DiT 의 아키텍처·조건화 메커니즘(cross-attention / AdaLN / conditional-concat)을 **정확히 보존**해야 함 — `z_vl` 자리에 `z̃_aux` 만 치환. 깨지면 main 가중치 초기화의 prior 이점이 사라짐.
- **(frozen 불변)** VLM·main DiT·보조 encoder `E` 는 학습 내내 frozen. trainable = {`W_proj`, `{f_i^copy}`, `{Z_i}`, embodiment state/action adapter} 뿐.
- **(encoder-agnostic)** `E` 는 원시 관측 → 고정차원 $`\mathbf{z}_{\mathrm{aux}}\in\mathbb{R}^{L\times d_E}`$ 만 만족하면 무엇이든 가능 (시간적/정적 표현 모두).

---

## 📊 하이퍼파라미터·손실

- 손실 식 (base flow-matching 그대로, 변경 없음):

$$\mathcal{L}=\mathbb{E}_{t,\boldsymbol{\epsilon}}\Big[\big\|\hat{v}_{\theta}(\mathbf{a}_{t},t,\mathbf{z}_{\mathrm{vl}})-(\mathbf{a}-\boldsymbol{\epsilon})\big\|_{2}^{2}\Big]$$

  with $`\mathbf{a}_{t}=(1-t)\boldsymbol{\epsilon}+t\mathbf{a}`$, $`\boldsymbol{\epsilon}\sim\mathcal{N}(\mathbf{0},\mathbf{I})`$, $`t\in[0,1]`$.
- 추론: 순수 노이즈에서 `K`-step Euler 적분.

| 이름 | 값 | 출처 |
|------|----|----|
| 보조 encoder `E` | V-JEPA2 (기본) / DINOv2 / 둘 결합 | §3.3, §4.2 |
| `n_frames` (V-JEPA2) | 8 (main) · **2–4 최적** | §4.3, Table 2 |
| `fps` (보조 샘플링) | 4 | §4.1 |
| `W_proj` 초기화 | zero | §3.3 |
| `{Z_i}` 초기화 | zero | §3.4, Eq. (6) |
| copy branch 초기화 | main DiT 사전학습 가중치 복제 | §3.5 |
| demo / task | 50 | §4.1 |
| eval rollout / task | 100 (무작위 초기조건) | §4.1 |
| optimizer / lr / step / batch | (원문에 명시 없음 — 부록 0.A.2 미확보) | — |
| flow steps `K` | (원문에 명시 없음 — 가정으로 메움) | — |

---

## 🎯 평가 메트릭

- **지표** — task 성공률(%) · **측정** — task 당 100 rollout(무작위 초기조건) 평균 · **비교 baseline** — fine-tuned GR00T N1.5.
- **단일-task (20 task)** — base 35.70% → PVI 59.70% (+24.00pp). 대안 주입(Concat 43.60 / ControlNet 34.35 / ControlVLA 37.00 / ReferenceNet 37.40) 대비 우위.
- **encoder 비교 (10 task)** — base 39.8% → DINOv2 56.8% / V-JEPA2 69.4% / 결합 68.9%.
- **multi-task** — 20-task 61.15→69.15 (+8.00pp), 50-task 61.32→63.56 (+2.24pp).

---

## ✨ 변경 의도 (intent)

PVI 의 핵심은 base VLA 를 전혀 건드리지 않고(백본 수정·재사전학습·다단계 학습 없이) 보조 시각 표현을 action expert 에 보태는 것입니다. 기존 주입법은 입력단 concat(맥락 확장 → full FT 필요)·attention 단 주입·단일 잔차 등으로 갈렸는데, PVI 는 **main DiT 를 통째로 복제한 copy branch(보조 특징을 조건으로)** + **layer-wise zero-init 잔차** 의 조합으로 (a) 사전학습 feature-처리 prior 를 물려받고 (b) 초기 동일성을 보장하며 (c) 매 layer 에서 점진적으로 보조 정보를 통합합니다. 동일 데이터·예산에서 다른 주입 설계를 크게 앞서는 이유는 이 dual-conditioning 구조 자체에 있습니다. 부차적 기여는 encoder-agnostic 슬롯으로 "무엇을 주입할지"(시간 vs 정적)를 통제 비교할 수 있게 한 점입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — base 후보는 flow-matching DiT action expert 를 갖는 `pi0` / `pi05` family 와 가장 가깝습니다 (PVI 는 cross-attention/AdaLN 조건화 DiT 를 전제). PVI 는 새 정책이 아니라 **기존 expert 를 감싸는 wrapper**(copy branch + zero-init injection layer)이므로, lerobot 의 해당 policy 모듈 위에 trainable side-branch 를 얹는 형태로 매핑될 가능성. copy branch 의 조건 입력을 VLM 임베딩에서 보조 특징으로 치환(`z_vl` → `z̃_aux`)하는 것이 핵심이며, `act` / `diffusion` 처럼 cross-attention 조건화가 아닌 family 는 이 치환 가정이 어긋날 수 있어 후보에서 멀어집니다.

---

## 🚧 미해결 / 잠정

- optimizer / learning rate / 총 step / batch size / 하드웨어는 부록 0.A.2(Training Setup)에 있으나 HTML 본문 텍스트로 미확보 — `(원문에 명시 없음)` 으로 비움.
- flow-matching 추론 step 수 `K` 의 구체 값 미명시.
- action 정규화 통계의 출처 미명시 — base VLA(GR00T N1.5) 의 action 통계를 따른다고 가정.
- copy branch 가 non-cross-attention 조건화(AdaLN/conditional-concat) base 에서 어떻게 `z_vl` → `z̃_aux` 치환되는지는 "same principle applies" 로만 서술 — 구체 매핑은 base 별로 잠정.
- 추론 시 copy branch(=main DiT 복제) + 보조 encoder forward 의 연산/메모리 오버헤드 수치 미확보(부록 0.A.3 cost-stats 미확보).
