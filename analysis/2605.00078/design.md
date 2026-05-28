# Design — Being-H0.7: A Latent World-Action Model from Egocentric Videos

> PROBE design 산출물 (Layer 1, vendor-agnostic). 단일 한글 문서이며
> 영문 1차 파일은 없습니다. `/analyze-paper` 가 `analysis/<id>/analysis.md` 와
> 함께 자동 생성합니다 — 알고리즘 명세를 base 좌표계 없이 추출합니다.
> base 매핑은 `/implement` 단계에서 이루어집니다. 형식·이모지·용어 규칙은
> `docs/STYLE.md` §6 / §4 를 정확히 따릅니다. 재실행 시 이 파일을
> 덮어씁니다.

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Being-H0.7: A Latent World-Action Model from Egocentric Videos |
| 링크 | [arXiv:2605.00078](https://arxiv.org/abs/2605.00078) |
| 분석 문서 | [`analysis/2605.00078/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-05-27 |

---

## 🧮 데이터 계약

학습·추론 시 모델이 입출력하는 텐서를 모달리티별로 한 줄씩 정의합니다. 시간 축은 의미 단위(`H`·`T`·`K`·`L`)로만 적습니다.

- **입력 — instruction `x`**: 자연어 토큰 시퀀스. shape `(B, N_x)`, dtype `int64`(tokenizer id). Understanding Expert(InternVL3.5)의 텍스트 토크나이저로 토큰화.
- **입력 — context observations `o_{-H:0}`**: shape `(B, H, 3, 224, 224)`, dtype `float32` ([0,1] 정규화). horizon `H=4`. context 인코더는 V-JEPA2.1 ViT(*trainable*) → patch token sequence → Understanding Expert.
- **입력 — state `s`**: 로봇 proprioception. shape `(B, D_s)`, dtype `float32`. `D_s`는 임바디먼트별 (예 PND Adam-U 31, Unitree G1 26, Franka FR3 13).
- **입력 (학습 only) — future observations `\tilde{o}_{0:T}`**: shape `(B, T, 3, 256, 256)`, dtype `float32`. action chunk와 매칭되는 미래 RGB 프레임. frozen V-JEPA2.1 ViT → Perceiver resampler가 `K=16` 임베딩으로 압축.
- **입력 — latent queries `Q`**: shape `(B, K, d)`, dtype `float32`. learnable parameter, `K=16`. prior branch의 reasoning 슬롯.
- **입력 (학습 only) — future embeddings `z^post`**: shape `(B, K, d)`, dtype `float32`. posterior branch의 reasoning 슬롯 자리에 들어가는 *teacher* 입력. `Q`와 일대일 매칭(같은 `K`, `d`).
- **입력 — flow time `t`**: shape `(B,)`, dtype `float32`, `t ~ U(0,1)`.
- **입력 — noised action `a_t`**: shape `(B, T, D_a)`, dtype `float32`. `a_t = t·a + (1-t)·ε`, `ε~N(0,I)`.
- **출력 — velocity field**: shape `(B, T, D_a)`, dtype `float32`. prior branch는 `v_θ^prior(a_t, c, q)`, posterior branch는 `v_θ^post(a_t, c, z^post)`. 학습 시 target은 `u_t = a - ε`.
- **출력 — action chunk `a_{0:T}`**: shape `(B, T, D_a)`, `T=20`. `D_a`는 임바디먼트별 (예 G1: 26, FR3: 13). 추론 시 prior branch만 사용해 flow matching ODE를 적분.
- **출력 — aligned hidden states**: 마지막 `L=9` Transformer layer에서 latent reasoning 위치의 hidden state. shape `(B, K, d)` per layer per branch. alignment loss 계산용으로만 노출, 외부 인터페이스 없음.
- **정규화 가정** — context image는 [0,1] 정규화 후 V-JEPA2.1 patch embedding. proprioception `s`는 데이터셋 평균/표준편차로 정규화(원문에 명시 없음 — 가정으로 메움). action `a`는 데이터셋 통계로 zero-mean/unit-variance 정규화(원문에 명시 없음 — UniHand 2.0 표준 포맷 가정).

---

## 🧰 모듈 인터페이스

```python
def context_encode(x, o_minus_H_to_0, s) -> Tensor:
    """instruction tokens + context RGB(V-JEPA2.1) + state를 Understanding Expert
    토큰 시퀀스로 인코딩. context_frame encoder는 trainable."""
    # 반환: shape (B, N_ctx, d) — instruction + image patches + state token

def future_encode(future_o_0_to_T) -> Tensor:
    """frozen V-JEPA2.1 ViT → Perceiver resampler → K=16 future embeddings.
    학습 시에만 호출."""
    # 반환: shape (B, K, d) — posterior 슬롯에 들어갈 z^post

def mot_forward(ctx_tokens, latent_slot, state_tok, noised_action, t,
                attn_mask, pos_ids) -> Tensor:
    """Mixture-of-Transformers 백본: action/state는 Action Expert,
    그 외는 Understanding Expert. 두 expert는 같은 시퀀스를 공유.
    학습 시 prior·posterior 두 branch를 한 시퀀스에 packing,
    dual-branch attention mask로 latent 슬롯끼리 차단.
    대응 위치에 identical positional ID."""
    # 반환: velocity v_θ ∈ (B, T, D_a) + per-layer hidden states h_l
    #       at aligned layer indices (last L=9).

def prior_branch_step(ctx, Q, state, a_t, t) -> Tensor:
    """deployable 경로. context + 학습된 Q를 latent 슬롯에 꽂아 mot_forward 호출."""

def posterior_branch_step(ctx, z_post, state, a_t, t) -> Tensor:
    """학습 전용 경로. future embedding을 latent 슬롯에 꽂아 mot_forward 호출."""

def align_loss(h_prior_per_layer, h_post_per_layer) -> Tensor:
    """L_align = (1/L) Σ_l (1/|h_l|) ||h_l^prior - h_l^post||_F^2,
    마지막 L=9 layer에서만 적용."""

def fm_loss(v_prior, v_post, a, eps, t) -> Tensor:
    """L_FM = ||v_prior - u_t||^2 + ||v_post - u_t||^2,
    u_t = a - eps, a_t = t·a + (1-t)·eps."""

def reg_norm(h, tau) -> Tensor:
    """R_norm(h) = (ReLU(tau - ||h||_2))^2, latent state magnitude shrinkage 차단."""

def reg_rank(H, n) -> Tensor:
    """H ∈ R^{M×n}: M latent state collection의 random n-subspace projection.
    row-normalize → Gram G = H H^T → eigenvalues {λ_i} → p_i = λ_i/Σ λ_j.
    R_rank(H) = Σ p_i log p_i (negative spectral entropy 최소화)."""

def total_loss(L_FM, L_align, R_norm, R_rank,
               w_align=1e-3, w_norm=1e-4, w_rank=1e-4) -> Tensor:
    """L = L_FM + w_align L_align + w_norm R_norm + w_rank R_rank."""

def euler_rollout(prior_branch, ctx, Q, state, steps=N_ode) -> Tensor:
    """flow matching ODE 적분으로 action chunk 생성. 본문에 적분 스텝 수
    명시 없음 — Euler step 수는 (원문에 명시 없음 — 가정으로 메움)."""

def uac_client(action_chunk_buffer, control_freq, inference_thread):
    """Being-H0.5에서 가져온 client-side scheduler. control thread는
    committed prefix에서 robot_freq로 액션을 popping;
    inference thread는 buffer가 trigger 이하로 떨어지면 다음 chunk 요청.
    UAC는 prefix를 절대 다시 쓰지 않고 *suffix만* stitching."""
```

- **모듈 간 의존** — 학습 시 `context_encode`·`future_encode` → `prior_branch_step`·`posterior_branch_step`(한 시퀀스 packing) → `align_loss`·`fm_loss`·`reg_norm`·`reg_rank` → `total_loss`. 추론 시 `context_encode` → `prior_branch_step` → `euler_rollout` → `uac_client`.
- **외부 호출** — pre-trained weights: InternVL3.5(understanding), Qwen3(action), V-JEPA2.1(시각). 모두 black-box 가중치 로딩이고, fine-tuning 범위는 §4.1에서 명시한다(context-frame V-JEPA2.1는 trainable, future-frame V-JEPA2.1는 frozen).
- **post-training 인터페이스** — `total_loss`에서 `R_norm`, `R_rank` 두 항을 OFF, `L_align`은 ON 유지. *action 손실 + alignment 손실만*으로 task-specific demonstration 위에서 fine-tune. sequence packing으로 효과 batch ≈ 128 trajectory chunk.

---

## ⛓️ 불변식·가정

- **(latent 자리 일대일 매칭)** — prior `Q`와 posterior `z^post`는 같은 시퀀스 위치, 같은 개수(`K`), 같은 hidden dimension(`d`), 같은 positional ID를 공유한다고 가정합니다. layer를 따라가도 두 자리가 구조적으로 맞물려 있어야 alignment loss가 의미를 갖습니다.
- **(branch 간 직접 attention 차단)** — prior latent 토큰과 posterior latent 토큰은 dual-branch attention mask로 서로를 보지 못하도록 막습니다. 두 branch는 오직 alignment loss를 통해서만 연결되며, 이 가정이 깨지면 posterior 정보가 prior로 *leakage*되어 추론 시점 deployable 보장이 무너집니다.
- **(추론 시 posterior 제거 가능)** — alignment loss로 충분히 학습된 prior는 posterior branch와 future encoder 일체를 떼어내도 추론할 수 있다고 가정합니다. 즉, posterior pathway에 의존하는 정보가 prior branch hidden state에 모두 흡수되었다는 가정입니다.
- **(latent collapse 차단)** — alignment loss만으로는 두 branch가 동일한 trivial 해(예: zero state)로 수렴할 수 있으므로, `R_norm`은 임계값 `tau` 이상의 magnitude를, `R_rank`는 평탄한 spectrum을 강제하는 역할을 합니다. 두 정규화가 모두 켜진 상태에서만 latent reasoning이 *비-trivial*입니다.
- **(미래 임베딩 정보성)** — frozen ViT + Perceiver resampler 결과 `z^post`가 행동에 유용한 미래 단서를 실제로 담는다고 가정합니다. 가정이 깨지면 posterior가 *informative target*이 되지 못해 alignment loss가 의미를 잃습니다.
- **(action chunk continuity)** — UAC가 client-side buffer에서 *committed prefix*는 다시 쓰지 않고 *suffix만* stitching하므로, 인접 청크 boundary의 차분이 controller 추종 한계 안에 있다고 가정합니다. 청크 길이 `T=20`과 robot control frequency(20/10 Hz)의 정합성이 이 가정에 깔립니다.
- **(MoT capacity 분할의 정합성)** — Understanding Expert는 instruction·observation·context를, Action Expert는 action·state를 각각 처리한다는 분할이 UniHand 2.0 통합 시퀀스 포맷의 토큰 type 식별자와 정확히 맞물린다는 것이 전제입니다.

---

## 📊 하이퍼파라미터·손실

손실 식(verbatim — 원문 식 (1)–(8)):

$$\mathcal{L}=\mathcal{L}_{\mathrm{FM}}+w_{\mathrm{align}}\mathcal{L}_{\mathrm{align}}+\mathcal{L}_{\mathrm{reg}}$$

$$\mathcal{L}_{\mathrm{FM}}=\mathcal{L}_{\mathrm{FM}}^{\mathrm{prior}}+\mathcal{L}_{\mathrm{FM}}^{\mathrm{post}},\quad\mathcal{L}_{\mathrm{FM}}^{\mathrm{prior}}=\left\|v_{\theta}^{\mathrm{prior}}(a_{t},c,q)-u_{t}\right\|_{2}^{2},\quad\mathcal{L}_{\mathrm{FM}}^{\mathrm{post}}=\left\|v_{\theta}^{\mathrm{post}}(a_{t},c,z^{\mathrm{post}})-u_{t}\right\|_{2}^{2}$$

$$\mathcal{L}_{\mathrm{align}}=\frac{1}{L}\sum_{\ell=1}^{L}\frac{1}{|h_{\ell}|}\left\|h_{\ell}^{\mathrm{prior}}-h_{\ell}^{\mathrm{post}}\right\|_{F}^{2}$$

$$\mathcal{R}_{\mathrm{norm}}(h)=\left[\mathrm{ReLU}(\tau-\|h\|_{2})\right]^{2},\quad\mathcal{R}_{\mathrm{rank}}(H)=\sum_{i=1}^{M}p_{i}\log p_{i},\quad\mathcal{L}_{\mathrm{reg}}=w_{\mathrm{norm}}\mathcal{R}_{\mathrm{norm}}+w_{\mathrm{rank}}\mathcal{R}_{\mathrm{rank}}$$

| 이름 | 값 | 출처 |
|------|----|------|
| 관측 horizon `H` | `4` | §4.1 |
| 액션 chunk 길이 `T` | `20` | §4.1 |
| latent query 수 `K` | `16` | §4.1 |
| alignment layer 수 `L` | `9` (마지막 9개 Transformer layer) | §4.1 |
| context 이미지 해상도 | `224 × 224` | §4.1 |
| future 이미지 해상도 | `256 × 256` | §4.1 |
| alignment loss 가중 `w_align` | `1 × 10⁻³` | §4.1 |
| norm regularizer 가중 `w_norm` | `1 × 10⁻⁴` | §4.1 |
| rank regularizer 가중 `w_rank` | `1 × 10⁻⁴` | §4.1 |
| norm threshold `tau` | (원문에 명시 없음 — 가정으로 메움) | §3.3 식 (5) |
| rank projection 차원 `n` | (원문에 명시 없음 — 가정으로 메움) | §3.3 식 (6) |
| rank 수집 latent state 수 `M` | (원문에 명시 없음 — 가정으로 메움) | §3.3 식 (6) |
| Understanding Expert backbone | InternVL3.5 | §4.1 |
| Action Expert backbone | Qwen3 | §4.1 |
| Context visual encoder | V-JEPA2.1 (trainable) | §4.1 |
| Future visual encoder | V-JEPA2.1 (frozen) | §4.1 |
| Future aggregator | Perceiver resampler → `K` 출력 | §3.2 식 (2) |
| Effective post-training global batch | `≈ 128` trajectory chunks (sequence packing) | §4.1 |
| Optimizer / 학습률 / 스케줄 | (원문에 명시 없음 — 가정으로 메움) | §4.1 |
| Pretraining data | UniHand 2.0 (mixed human + robot manipulation) | §3.3, §4.1 |
| Flow matching ODE 적분 스텝 | (원문에 명시 없음 — 가정으로 메움) | §3.3 |
| Deployment scheduler | UAC (Universal Async Chunking) | §4.3.3 |
| Inference step time (UAC enabled) | `3–4 ms/step` | §4.3.3 |
| Action expert로 흘려보내는 토큰 type | action, state | §3.3 |
| Understanding Expert로 흘려보내는 토큰 type | instruction, observation, latent query (prior) / future embedding (posterior) | §3.3 |

`λ_*` 류의 추가 가중 항은 본문 식 (1)–(8)에 등장하지 않습니다. `L_FM` 내부에 prior·posterior가 *동일 가중치(1:1)* 로 합산됩니다.

---

## 🎯 평가 메트릭

- **지표** — 시뮬레이션 평균 성공률 / CALVIN 평균 task 수 · **임계값** — 6 벤치마크 평균 1위 유지 (LIBERO 99.2, LIBERO-plus 82.1, LIBERO-plus∗ 84.8, RoboCasa-50 62.1, GR1 49.2, CALVIN 4.67/4.48, RoboTwin 2.0 90.2/89.6) · **비교 baseline** — π0, π0-FAST, X-VLA, UniVLA, gr00t-N1.6, π0.5, starVLA, MINT-4B, ABot-M0, LingBot-VLA, Being-H0.5, UWM, UVA, VPP, DreamVLA, JEPA-VLA, VLA-JEPA, LingBot-VA, Cosmos-Policy, Fast-WAM (Table 1).
- **지표** — RoboTwin 2.0 Hard 하락 폭 · **임계값** — clean 대비 ≤ `0.6 %p` drop (90.2 → 89.6, 시각 도메인 랜덤화 강도 max) · **비교 baseline** — same model on clean(Easy) split.
- **지표** — CALVIN long-horizon 평균 task 수 · **임계값** — ABCD→D 4.67 / ABC→D 4.48 (5 instruction sequence 중) · **비교 baseline** — UniVLA(4.63/4.41), Being-H0.5(4.63/4.48), DreamVLA(4.44 on ABC→D).
- **지표** — Real-robot suite-level 성공률 (5개 능력 suite) · **임계값** — 5/5 suite 1위 유지(dynamic scene / physical reasoning / motion reasoning / long-horizon / generalization) · **비교 baseline** — Being-H0.5, π0.5, Fast-WAM (Figure 5).
- **지표** — Real-robot trial 프로토콜 · **임계값** — task당 `20` blind trial, endpoint randomization, fixed binary success criterion · **비교 baseline** — unified black-box inference server 위 동일 stack(§4.3.2).
- **지표** — Inference cost · **임계값** — UAC 적용 시 `3–4 ms/step`, GPU memory footprint는 non-UAC 대비 동일 · **비교 baseline** — non-UAC Being variants(§4.3.3, Figure 7).
- **지표** — Latent reasoning 정성 검증 · **임계값** — prior branch hidden state + current observation을 외부 video generation model에 조건으로 넣었을 때 plausible future frame 생성 · **비교 baseline** — same generator with random/ablated latent(§4.3.3, Figure 6).

---

## ✨ 변경 의도 (intent)

본 알고리즘은 VLA의 sparse action supervision과 world-action model의 비싼 pixel rollout 사이를 가르는 *제3의 길*입니다. 미래 정보를 픽셀 reconstruction이 아닌 latent reasoning 위치 alignment로 흘려보내, 학습 시에는 미래를 본 posterior가 *teacher*가 되고 추론 시에는 통째로 제거됩니다. 이렇게 해서 (i) VLA의 단일 forward / fast inference / pixel-free deployment를 유지하면서 (ii) WAM의 *anticipatory* supervision을 받습니다. 핵심 새로움은 세 가지입니다. 첫째, latent query 슬롯이 명시적 reasoning interface로 박혀 attention propagation을 따라 task-relevant 정보를 모읍니다. 둘째, prior/posterior 두 branch를 같은 시퀀스에 packing하고 dual-branch mask와 identical positional ID로 단일 forward에 묶었습니다. 셋째, latent collapse를 norm + spectral entropy 두 축으로 차단했습니다. Being-H0.5의 MoT + UniHand 2.0 기반을 그대로 이어받아 latent reasoning 한 층만 새로 얹는 *minimum-delta* 설계로, real-world에서도 같은 UAC deployment stack을 재사용해 3–4 ms/step을 유지합니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 후보 base: `pi0` / `pi05` (flow matching action expert + MoT-style 시퀀스 패밀리)와 가장 가깝습니다. 그 위에 (i) latent query 슬롯을 액션 청크 앞에 삽입, (ii) posterior branch를 학습 전용 *parallel* 시퀀스로 추가, (iii) dual-branch attention mask + alignment loss + norm/rank 정규화를 손실 함수에 add — 세 변경이 핵심입니다. `pi05`는 hierarchical inference가 있어 별도의 high-level reasoning layer가 본 논문의 latent reasoning slot과 겹칠 수 있으므로, `/implement` 단계에서 차별점을 별도로 매핑합니다. `act` / `diffusion` 패밀리는 backbone 구조가 달라 base 후보 부적합. `smolvla`는 capacity가 작아 비교 후보로만.

---

## 🚧 미해결 / 잠정

- **norm threshold `tau` · spectral diversity의 random projection 차원 `n` · 수집 state 수 `M`** — 식 (5)·(6)에 기호만 등장, 구체 값은 원문에 명시 없음 — 가정으로 메움.
- **flow matching ODE 적분 스텝 수** — Euler·Heun 등 적분기 종류와 step 수가 §3.3·§4.1에 명시 없음 — 가정으로 메움.
- **Optimizer / 학습률 / scheduler / pretraining hyperparameters** — §4.1은 `w_align`, `w_norm`, `w_rank`, `H`, `T`, `K`, `L`만 적시. AdamW 여부·lr·warmup·총 step·노드 수·총 GPU 시간 모두 원문에 명시 없음 — 가정으로 메움.
- **UniHand 2.0의 본 논문 변종 정확한 mixing 비율** — Being-H0.5 인용으로 데이터 포맷·규모(~35k h × 30 embodiment)는 외부로 떠넘기지만 Being-H0.7 학습 시 사용된 세부 mixing 비율 / curriculum은 명시 없음.
- **Action chunk 차원 `D_a`의 임바디먼트별 매핑** — sim 벤치마크와 real-robot 플랫폼이 모두 다른 액션 공간을 가지므로 unified 26-DoF G1 interface 등으로 *padding*하는지 *per-embodiment head*를 두는지 본문에 명시 없음 — UniHand 2.0의 unified action space 가정으로 메움.
- **`align_loss`가 정렬하는 layer 인덱스 선택 규칙** — "마지막 `L=9`개 layer"만 명시. 총 layer 수(InternVL3.5 깊이) 및 부분 정렬(예: 마지막 9개 중 3개 건너뛰기 등) 가능성은 명시 없음 — 모든 마지막 9개 가정으로 메움.
- **post-training 단계의 alignment 적용 여부 / 정규화 OFF 명시** — §4.1은 "action-generation 손실 + latent alignment 손실만" "anti-collapse regularizer는 적용하지 않음"이라고 적습니다. UAC + 청크 길이 등 *다른* 모든 하이퍼파라미터가 사전학습과 동일한지는 명시 없음 — 가정으로 메움.
- **Posterior 인코더의 Perceiver resampler 깊이·헤드 수** — `K=16` 출력 차원만 명시, 내부 layer 수·learnable query 수·attention head 수 모두 명시 없음 — Perceiver IO 표준값 가정으로 메움.
- **PROBE의 *Body/Hand* 분할과 본 논문의 *Action Expert / Understanding Expert* 분할의 정합** — 두 분할 축이 직교에 가까워 그대로 매핑되지 않습니다. anatomical 분리는 별도 Design 변환 단계에서 정합 필요.
