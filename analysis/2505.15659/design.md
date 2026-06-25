# Design — FLARE: Robot Learning with Implicit World Modeling

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | FLARE: Robot Learning with Implicit World Modeling |
| 링크 | [arXiv:2505.15659](https://arxiv.org/abs/2505.15659) |
| 분석 문서 | [`analysis/2505.15659/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-25 |

---

## 🧮 데이터 계약

학습·추론 시 모델이 입출력하는 텐서를 모달리티별로 정의합니다. 시간 축은 의미 단위(`H`·`M`·`L`·`K`)로만 적습니다.

- **입력 — VL 임베딩** $`\phi_{t}=VL(o_{t})`$: 현재 관측(멀티뷰 이미지 + 언어)을 action-aware 임베딩 모델로 인코딩. shape `(B, M, D)`, dtype `float32`. `M=32`(Q-former query token 수), `D`는 임베딩 차원. DiT의 cross-attention 조건.
- **입력 — proprioceptive state** $`q_{t}`$: shape `(B, D_q)`, dtype `float32`. state encoder(2-layer MLP)로 토큰화 → state token 1개.
- **입력 — noised action chunk** $`A_{t}^{\tau}=\{\tau a_{t}+(1-\tau)\epsilon\}_{t}^{t+H}`$: shape `(B, H, D_a)`, dtype `float32`. action encoder(2-layer MLP)로 토큰화. `H`는 액션 청크 길이(=미래 horizon), `D_a`는 액션 차원(임바디먼트별).
- **입력 — learnable future tokens**: shape `(B, M, D)`, dtype `float32`. `nn.Embedding(M, D)` 학습 파라미터, `M=32`. 액션 스트림과 self-attention으로만 상호작용하는 별도 스트림.
- **입력 — flow timestep** $`\tau`$: shape `(B,)`, dtype `float32`. $`p(\tau)=\text{Beta}(\frac{s-\tau}{s};1.5,1)`$, `s=0.999`.
- **입력 (학습 only) — 미래 관측 임베딩** $`\phi_{t+H}=g(o_{t+H})`$: shape `(B, M, D)`, dtype `float32`. *frozen* target 임베딩 모델 출력. alignment 타깃이며 gradient 없음(`requires_grad=False`).
- **출력 — velocity field** $`V_{\theta}(\phi_{t},A_{t}^{\tau},q_{t})`$: shape `(B, H, D_a)`, dtype `float32`. 디노이징 방향 $`\epsilon-A_{t}`$ 근사. action decoder(2-layer MLP)가 DiT의 action token 위치 출력에서 디코드.
- **출력 — predicted future embedding**: shape `(B, M, D)`, dtype `float32`. layer `L`의 future token 활성을 MLP(`embedding_decode`)로 사영한 값. alignment loss 계산용.
- **출력 — action chunk** $`A_{t}=(a_{t},\dots,a_{t+H})`$: shape `(B, H, D_a)`. 추론 시 $`A_{t}^{0}\sim\mathcal{N}(\mathbf{0},\mathbf{I})`$ 에서 `K=4` 스텝 forward Euler 적분으로 생성.
- **정규화 가정** — 이미지는 SigLIP2 patch 전처리(`256×256` → 256 patch token). action `a`·state `q`는 데이터셋 통계로 정규화(원문에 명시 없음 — 가정으로 메움).

---

## 🧰 모듈 인터페이스

```python
def vl_embed(obs) -> Tensor:
    """action-aware vision-language 임베딩 모델.
    SigLIP2(vision+text) → 256 patch + 32 lang token → concat(288)
    → 4-layer self-attention → Q-former(32 learnable query)
    → 32 compressed VL token. 멀티카메라 입력에 자연 일반화."""
    # 반환: shape (B, M=32, D)

def target_vl_embed(future_obs) -> Tensor:
    """미래 관측의 alignment 타깃 임베딩. 구조는 vl_embed 와 동일하나
    EMA 로만 갱신되고 gradient 없음(requires_grad=False)."""
    # 반환: shape (B, M=32, D)  (no grad)

def state_embed(state) -> Tensor:
    """proprioception → state token. 2-layer MLP."""

def action_embed(noisy_action, timestep) -> Tensor:
    """noised action chunk + flow timestep → action tokens. 2-layer MLP."""

def dit(sa_tokens, vl_tokens) -> Tensor:
    """flow-matching Diffusion Transformer. sa_tokens =
    concat([state_token, action_tokens, future_tokens]) 에 self-attention,
    vl_tokens 에 cross-attention(GR00T N1 식 교차 구조).
    layer L 의 future-token 활성을 별도로 노출."""
    # 반환: per-token DiT 출력 + layer-L future-token 활성 f_θ ∈ (B, M, D)

def action_decode(dit_out_action_slice) -> Tensor:
    """action token 위치 출력 → velocity. 2-layer MLP.
    L_fm 의 예측 V_θ."""

def embedding_decode(dit_out_future_slice) -> Tensor:
    """layer-L future-token 활성 → predicted future embedding. 2-layer MLP."""

def fm_loss(v_pred, actions, noise) -> Tensor:
    """L_fm = ||V_θ - (ε - A_t)||^2.  velocity target = actions - noise."""

def align_loss(predict_embedding, target_embedding) -> Tensor:
    """L_align = 1 - cos(predict_embedding, target_embedding).
    target 은 target_vl_embed(future_obs), no grad."""

def total_loss(L_fm, L_align, lam=0.2) -> Tensor:
    """L = L_fm + lam * L_align."""

def ema_update(target_params, policy_vl_params, rho=0.995):
    """θ_target ← ρ·θ_target + (1-ρ)·θ_policy_vl_embedding.
    매 gradient step 후 호출."""

def euler_rollout(dit, phi_t, q_t, K=4) -> Tensor:
    """A_t^0 ~ N(0,I) → K-step forward Euler:
    A_t^{τ+1/K} = A_t^τ + (1/K)·V_θ(φ_t, A_t^τ, q_t)."""
```

- **학습 의존** — `vl_embed` → `dit` → (`action_decode`→`fm_loss`) + (`embedding_decode` + `target_vl_embed`→`align_loss`) → `total_loss` → backward → `ema_update`.
- **추론 의존** — `vl_embed` → `euler_rollout`(future token·alignment 경로는 forward에 남으나 손실 계산만 생략). target 임베딩 모델은 추론에 불필요.
- **액션-프리 데이터 인터페이스** — 액션 라벨이 없는 인간 ego 비디오 배치는 `fm_loss`를 끄고 `align_loss`만 활성화(`obs`·`future_obs`만 필요).

---

## ⛓️ 불변식·가정

- **(future token 개수 일치)** — 입력 future token 수와 target 임베딩 출력 token 수가 같은 `M=32`, 같은 차원 `D`여야 코사인 정렬이 token-wise로 성립합니다. $`f_{\theta}\rightarrow\mathbb{R}^{B\times M\times D}`$, $`g\rightarrow\mathbb{R}^{B\times M\times D}`$ 가 동일 shape이라는 것이 핵심 불변식입니다.
- **(두 스트림 분리)** — flow-matching 스트림(state+action token)과 alignment 스트림(future token)은 *별도 흐름*이며 DiT 내부에서 self-attention으로만 상호작용합니다. 이 분리가 깨지면 alignment가 액션 예측 capacity를 직접 침식합니다.
- **(target frozen + EMA)** — alignment 타깃 $`\phi_{t+H}`$ 은 gradient가 흐르지 않고 정책 인코더의 EMA로만 천천히 갱신됩니다($`\rho=0.995`$). target에 gradient가 흐르면 trivial collapse(양쪽이 같은 상수로 수렴)가 발생합니다.
- **(alignment layer 정합)** — alignment를 거는 내부 layer `L`은 액션 디노이징 과정과 정합돼야 합니다. 너무 이른 layer(예: 8개 중 4번째)는 성능을 떨어뜨립니다 — "layer 6/8"은 *비율*이지 절대 인덱스가 아닙니다.
- **(미래 관측 = 청크 끝)** — 정렬 타깃 관측 시점은 액션 청크 끝 $`t+H`$ 입니다. `H`(청크 길이)가 곧 예측 horizon이므로, `H`가 바뀌면 정렬이 담는 미래의 시간 범위도 바뀝니다.
- **(target 임베딩의 정보성)** — action-aware 임베딩이 행동에 유용한 미래 단서를 실제로 담는다고 가정합니다. 범용 SigLIP2도 작동하나(7% 향상), action-supervised 임베딩이 최적이라는 것이 본 가정의 근거입니다.

---

## 📊 하이퍼파라미터·손실

손실 식(verbatim — 원문 §2 식 (1), §3 식 (2)–(3)):

$$\mathcal{L}_{\textit{fm}}(\theta)=\mathbb{E}_{\tau}\left[\|V_{\theta}(\phi_{t},A_{t}^{\tau},q_{t})-(\epsilon-A_{t})\|^{2}\right]$$

$$\mathcal{L}_{\textit{align}}(\theta)=-\mathbb{E}_{\tau}\left[cos(f_{\theta}(\phi_{t},A_{t}^{\tau},q_{t}),g(\phi_{t+H})\right]$$

$$\mathcal{L}=\mathcal{L}_{fm}+\lambda\mathcal{L}_{align}$$

EMA 타깃 갱신(§4.4):

$$\theta_{\text{target\_vl\_embedding}}\leftarrow\rho\theta_{\text{target\_embedding}}+(1-\rho)\theta_{\text{policy\_vl\_embedding}}$$

| 이름 | 값 | 출처 |
|------|----|------|
| future / query token 수 `M` | `32` | §3.2, Appendix A |
| alignment 적용 layer `L` | `6` (DiT 8 layer 중 6번째) | §4.4 |
| alignment loss 가중 $`\lambda`$ | `0.2` | §3.1, §4.4 |
| EMA 계수 $`\rho`$ | `0.995` (스윕 `{0.99, 0.995, 0.999, 1.0}`) | §4.4 |
| 디노이징 스텝 `K` | `4` | §2 |
| flow timestep 분포 | $`\text{Beta}(\frac{s-\tau}{s};1.5,1)`$, `s=0.999` | §2, Appendix C |
| VL 인코더 | SigLIP2 (`siglip2-large-patch16-256`) | §3.2, Appendix A |
| 이미지 해상도 | `256×256` → 256 patch token | Appendix A |
| 언어 token 수 | `32` | Appendix A |
| fusion self-attention layer 수 | `4` (→ 288 fused token) | §3.2, Appendix A |
| action-aware 학습용 DiT 블록 수 | `8` | §3.2 |
| SigLIP2-타깃 ablation 미래 시점 | `t+16` (raw 256 / 2×2 pool 64 token) | §4.4 |
| 임베딩 사전학습 | 256×H100, batch `8192`, `150k` step | Appendix C |
| 멀티태스크 학습 | 32×H100, batch `1024`, `80k` step | Appendix C |
| Optimizer | AdamW ($`\beta_1{=}0.95, \beta_2{=}0.999, \epsilon{=}\text{1e-8}`$) | Appendix C |
| weight decay / schedule | `1e-5` / cosine (warmup ratio `0.05`) | Appendix C |
| 사전학습 코퍼스 | GR00T N1 + OXE 7종, 169.5M frame / ~2,989.5 h | Appendix B, Table 3 |
| 액션 차원 `D_a` / state 차원 `D_q` | (원문에 명시 없음 — 임바디먼트별) | §2 |
| 임베딩 차원 `D` | (원문에 명시 없음 — 가정으로 메움) | §3.1 |

`L_fm`과 `L_align`은 $`\lambda=0.2`$ 단일 가중으로 합산됩니다. action loss 내부는 velocity target $`\epsilon-A_{t}`$ 의 MSE이고, align loss 내부는 `1 - cosine_similarity`(Appendix D pseudocode)입니다.

---

## 🎯 평가 메트릭

- **지표** — 멀티태스크 성공률 · **임계값** — RoboCasa 24 평균 `70.1%`, GR1 24 평균 `55.0%`(prior 대비 최대 `26%↑`) · **비교 baseline** — Policy Only, UWM, GR00T N1 (Scratch), Diffusion Policy (§4.1, Table 1).
- **지표** — 데이터-제한 post-training 성공률 · **임계값** — 100 traj/task에서 RoboCasa `+10%`, 1000 traj에서 cross-embodiment 임베딩 `71.3%` ≈ in-domain `70.2%` · **비교 baseline** — policy-only post-train(§4.2, Figure 6).
- **지표** — 실 GR-1 휴머노이드 성공률 · **임계값** — 최대 `95.1%`, baseline 대비 평균 `+14%` (4 태스크, 태스크당 8 reference 초기 프레임) · **비교 baseline** — policy-only(§4.2).
- **지표** — 신규 물체 일반화 성공률(부분점수 0.5) · **임계값** — 1 robot traj/object `최대 60%`, 10 traj + 인간 ego 비디오 `80%`(액션-only baseline의 ~2배) · **비교 baseline** — action-labeled-only(§4.3, Figure 7).
- **지표** — target 임베딩 ablation · **임계값** — No FLARE `43.9`, SigLIP2 `49.6`, SigLIP2(avg-pool) `50.9`, action-aware `55.0` · **비교 baseline** — No FLARE loss(§4.4, Table 2).
- **지표** — alignment layer / $`\lambda`$ / EMA $`\rho`$ robustness · **임계값** — layer 4 조기 적용 시 하락, $`\lambda=0.2`$ · $`\rho=0.995`$ 최적, $`\rho=0.99`$ 최악, $`\rho=1.0`$ 도 baseline 상회 · **비교 baseline** — policy-only(§4.4, Figure 8·9).

---

## ✨ 변경 의도 (intent)

FLARE는 VLA의 sparse action supervision과 generative world model의 비싼 픽셀 rollout 사이를 가르는 *제3의 길*입니다. 미래 정보를 픽셀 reconstruction이 아니라 *액션 디노이징 망의 은닉 상태*에서 future token 활성을 뽑아 미래 관측 임베딩과 코사인 정렬하는 것으로 주입합니다. prior art와의 차이는 세 가지입니다. 첫째, REPA가 이미지 diffusion의 *현재* 표현을 정렬한 데 비해, FLARE는 *정책*의 *미래* 임베딩을 정렬합니다(implicit latent world model). 둘째, full-frame reconstruction을 제거해 대형 생성 모델·추론 지연을 떼고, 픽셀 디테일에 capacity가 새지 않게 합니다 — 그 결과 UWM 같은 픽셀-latent 생성형을 최대 26% 상회합니다. 셋째, alignment 손실이 액션을 요구하지 않으므로 액션-프리 인간 ego 비디오를 자연스러운 학습 신호로 흡수합니다. 구조 변경이 "토큰 몇 개 추가 + 한 layer 정렬 손실"로 최소화되어 π0 / GR00T N1 같은 표준 flow-matching VLA에 *minimum-delta*로 얹힌다는 점이 설계의 정체성입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 후보 base: `pi0` / `pi05`(flow-matching action expert + DiT, self/cross-attention 교차 구조)가 가장 가깝습니다. 핵심 변경 3가지: (i) 액션·state 토큰 시퀀스에 `M=32` learnable future token 추가, (ii) 지정 내부 layer(`L`)의 future-token 활성을 슬라이스 → MLP 사영, (iii) frozen(EMA-updated) target 임베딩과의 코사인 alignment loss를 $`\mathcal{L}=\mathcal{L}_{fm}+0.2\,\mathcal{L}_{align}`$ 으로 손실에 add. action-aware target 임베딩(SigLIP2 + Q-former)은 별도 사전학습 컴포넌트로, lerobot의 VL 인코더 스택과 교체/병치 매핑이 필요합니다. `act` / `diffusion` 패밀리는 flow-matching DiT 구조가 아니라 base 후보 부적합. `smolvla`는 capacity가 작아 비교 후보로만.

---

## 🚧 미해결 / 잠정

- **임베딩 차원 `D` · 액션/state 차원 `D_a`·`D_q`** — 식에 기호만 등장, 구체 값은 원문에 명시 없음(임바디먼트별) — 가정으로 메움.
- **action / state 정규화 통계 출처** — 데이터셋 평균/표준편차 가정. 본문에 정규화 절차 명시 없음 — 가정으로 메움.
- **alignment layer `L`의 절대 인덱스 이식 규칙** — "8 layer 중 6번째" 비율만 명시. 다른 깊이의 backbone(또는 Body/Hand 분할 디코더)으로 옮길 때의 인덱스 선택 규칙은 명시 없음 — 재탐색 필요.
- **미래 horizon `H`의 정확한 값** — 액션 청크 길이 = `H` = 미래 시점이나, 메인 실험의 `H` 절대값은 본문에 명시 없음(SigLIP2 ablation만 `t+16` 명시) — 잠정.
- **future token ↔ embedding 디코더 가중 공유 여부** — `embedding_decode`(2-layer MLP)와 `action_decode`가 독립인지 일부 공유인지 명시 없음 — 독립 가정으로 메움.
- **EMA 갱신 대상 파라미터 범위** — pseudocode는 `target_vl_embedding`의 EMA만 명시. Q-former·DiT 블록까지 EMA 범위에 포함되는지(vs vision-language 인코더만) 본문에 명확치 않음 — VL 임베딩 인코더 한정으로 가정.
- **anti-collapse 장치 부재** — alignment이 frozen 타깃과의 코사인뿐이라 collapse 방지 정규화가 없습니다(후속 Being-H0.7는 norm/rank 정규화 도입). token 수 확대 시 collapse 거동은 본문에 보고 없음 — 잠정.
