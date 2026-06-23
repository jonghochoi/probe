# Design — LaST-HD: Learning Latent Physical Reasoning from Scalable Human Data for Robot Manipulation

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | LaST-HD: Learning Latent Physical Reasoning from Scalable Human Data for Robot Manipulation |
| 링크 | [arXiv:2606.23685](https://arxiv.org/abs/2606.23685) |
| 분석 문서 | [`analysis/2606.23685/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-23 |

---

## 🧮 데이터 계약

시간 축은 의미 단위(`N_lat`, `T_action`)로 기록합니다. `D_action` 은 embodiment-specific(dual-arm gripper `14`/`16`, dual-arm + WUJI 다지 손 `54`).

- **입력 — 이미지** — `(B, V, 3, 384, 384)`, V = 3 시점(head 1 + wrist 2), float, SigLIP-Large 정규화. SigLIP 으로 $`f_{\text{img}}\in\mathbb{R}^{N_{\text{img}}\times d_{v}}`$ 추출 후 MLP 로 LLM hidden 차원에 투영.
- **입력 — 언어** — 토큰 id 시퀀스 `(B, L_text)`, 언어 지시 $`\mathbf{l}`$.
- **입력 — 잠재 타깃** — $`\mathbf{z}^{\mathrm{GT}}`$: `(B, N_lat, d_l)`, float. **frozen world model 에서 오프라인 precompute** 되어 일반 입력처럼 로드(학습 시 추가 forward 없음).
- **입력 — proprioception / action history** — embodiment-specific(원문에 shape 명시 없음 — 가정으로 메움).
- **출력 — action chunk** — $`\mathbf{a}_{t:t+H-1}`$: `(B, T_action, D_action)`, float, 플로우 매칭 디코딩. relative translation + Euler-angle rotation + (그리퍼) binary command / (다지 손) joint angle.
- **출력 — 잠재 추론 토큰** — $`\hat{\mathbf{z}}`$: `(B, N_lat, d_l)`, float, reasoning expert 의 autoregressive 출력.

---

## 🧰 모듈 인터페이스

```python
def world_model_latent_target(obs_images, action_chunk) -> Tensor:
    """frozen action-conditioned WM → 잠재 ground-truth (B, N_lat, d_l). 오프라인 1회."""

def latent_aligner(wm_deep_unet_feat) -> Tensor:
    """가장 깊은 U-Net layer(마지막 denoising step) 특징 → MLP 투영(d_l) → flatten → adaptive avg pool → N_lat 토큰."""

def reasoning_expert(img_tokens, text_tokens) -> Tensor:
    """autoregressive 잠재 상태 z_hat (B, N_lat, d_l) 예측. MoT 의 reasoning 분기."""

def action_expert(img_tokens, text_tokens, shared_attn_ctx) -> Tensor:
    """flow matching 으로 action chunk (B, T_action, D_action) 예측. MoT 의 action 분기."""
```

- **world_model_latent_target / latent_aligner** — 학습 전 오프라인 단계. WM 은 cross-attention 으로 매 layer 에 action chunk 주입. 출력은 $`\mathcal{L}_{\mathrm{latent}}`$ 의 타깃이며 정책 inference 경로에는 들어가지 않음.
- **reasoning_expert** — 출력 $`\hat{\mathbf{z}}`$ 가 $`\mathcal{L}_{\mathrm{latent}}`$(cosine)로 지도됨. shared attention 으로 action_expert 에 컨텍스트 제공.
- **action_expert** — $`\mathcal{L}_{\mathrm{act}}`$(flow matching)로 지도. reasoning expert 의 잠재 추론을 shared attention 으로 수신.
- **MoT 결합** — reasoning/action 두 expert 는 단일 decoder-only transformer(24-layer)를 분리한 것이며 shared attention 으로 결합.

---

## ⛓️ 불변식·가정

- (가정 1) **물리 불변성** — 같은 task 의 인간·로봇 궤적은 형태가 달라도 같은 물리 법칙을 따르므로, action-conditioned forward-dynamics 표현이 형태 무관 공유 공간을 형성한다(정렬의 수학적 전제).
- (가정 2) **unpaired 충분성** — 인간·로봇 시연이 엄밀히 paired 일 필요 없음. action label 이 약한 anchor 로 작동해 unpaired 데이터로도 잠재가 정렬됨.
- (가정 3) **방향 정렬만 강제** — $`\mathcal{L}_{\mathrm{latent}}`$ 가 cosine 유사도 기반이라 잠재 벡터의 방향만 정렬하고 norm 은 자유(크기 불변성 가정).
- (가정 4) **타깃 정적성** — WM 은 frozen 이고 잠재 타깃은 오프라인 precompute 되므로, 학습 동안 타깃 분포가 변하지 않음(target drift 없음).
- (가정 5) **target-embodiment 사전학습 포함** — WM 사전학습 혼합에 deploy embodiment 데이터가 포함되어야 정렬 타깃 품질이 유지됨.

---

## 📊 하이퍼파라미터·손실

- **잠재 정렬 손실** (cosine similarity):

$$\mathcal{L}_{\mathrm{latent}}=\sum_{t=1}^{N_{\mathrm{lat}}}\left(1-\frac{\hat{\mathbf{z}}_{t}\cdot\mathbf{z}_{t}^{\mathrm{GT}}}{\lVert\hat{\mathbf{z}}_{t}\rVert\lVert\mathbf{z}_{t}^{\mathrm{GT}}\rVert}\right).$$

- **전체 목적함수**:

$$\mathcal{L}_{\mathrm{loss}}=\mathcal{L}_{\mathrm{act}}+\lambda\mathcal{L}_{\mathrm{latent}},$$

- **online correction 배치** (balanced replay):

$$\mathcal{B}=\mathcal{B}_{\mathrm{prev}}\cup\mathcal{B}_{\mathrm{dagger}},|\mathcal{B}_{\mathrm{prev}}|=|\mathcal{B}_{\mathrm{dagger}}|.$$

| 이름 | 값 | 출처 |
|------|----|----|
| `N_lat` (shared latent length) | `4` (16이 최고 성능, 지연 절충으로 4 채택) | §4.3, Table 7 |
| WM denoising steps (타깃 추출) | `2` (2/5/10 차이 미미) | Appendix D, Table 6 |
| $`\lambda`$ (action/latent 균형) | `(원문 미명시)` | §3.4 |
| online correction epochs | `1–2` | §3.4 |
| 이미지 해상도 | `384×384` (3 views) | §4.1 |
| 사전학습 혼합 | 400K traj / 28M frame (OXE + DROID + RoboMIND) | Appendix C |
| $`N_{\text{img}}`$, $`d_{v}`$, $`d_{l}`$ | `(원문 미명시)` | §3.1 |
| $`\mathcal{L}_{\mathrm{act}}`$ | flow matching action loss | §3.4 |

---

## 🎯 평가 메트릭

- **지표** — task completion success rate · **프로토콜** — task 당 20 rollout, in-domain + 3개 일반화 시나리오(unseen Position / Object / Background) · **비교 baseline** — $`\pi_{0.5}`$, Cosmos-Policy, LaST0.
- **핵심 임계값** — in-domain 평균 0.73(LaST-HD) vs 0.62($`\pi_{0.5}`$); 일반화 Global Avg 0.56(w/ unseen HD) vs 0.30(zero-shot baseline); online correction 으로 60 trajectory(20분)에 90%+ / Unseen Object·Background 100%.
- **ablation 지표** — 잠재 타깃 종류(WM action-conditioned vs SigLIP vs WM-only vs W/o Latent), 데이터 소스(OOL Glove vs bare-hand vs Real-12/60 vs UMI), denoising steps, latent length.

---

## ✨ 변경 의도 (intent)

직전작 LaST0 는 reasoning expert 의 잠재 타깃으로 **미래 SigLIP 이미지 특징**(외형 진화)을 썼습니다. LaST-HD 의 변경은 이를 **action-conditioned world model 의 forward-dynamics 특징**(물리적 결과)으로 교체한 것입니다. action conditioning 이 약한 anchor 가 되어, 운동학·외형이 다른 인간·로봇 unpaired 궤적이 같은 잠재 추론 공간으로 정렬됩니다. WM 은 행동 예측이 아니라 잠재 지도 타깃 생성기로만(leakage·비압축 회피) frozen·offline 으로 격리되어, co-training 비용 없이 cross-embodiment 정렬을 제공합니다. 결과적으로 사람 손 데이터만으로 새 객체·장면·위치 일반화가 가능해지고, mixed co-training + 사람 손 online correction 의 2단계 레시피로 소량 데이터 빠른 적응을 달성합니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — action expert(플로우 매칭 action chunk)는 `pi0` / `pi05` / `smolvla` family 와 가깝습니다. 다만 **reasoning/action MoT 분리 + 외부 action-conditioned WM 의 cosine 잠재 지도**는 어느 lerobot baseline 에도 없는 신규 보조 구조라, action expert 만 부분 매핑되고 잠재 정렬 head + WM 타깃 파이프라인은 신규 추가가 필요합니다(매핑 불가 가능성 존재 — `/implement-design` 가 판정).

---

## 🚧 미해결 / 잠정

- $`\lambda`$(action/latent 손실 균형 계수) 값이 원문에 명시되지 않음.
- world model [31] 의 정확한 정체·아키텍처가 명명되지 않음(U-Net 기반 video diffusion 으로 추정 — 가장 깊은 U-Net layer·denoising step 언급에 근거).
- $`N_{\text{img}}`$, $`d_{v}`$, $`d_{l}`$ 의 구체 수치, vision→LLM MLP·MLP aligner 구조 세부가 미명시.
- WM fine-tuning 의 옵티마이저/스케줄/스텝, MoT 사전학습·SFT 의 LR·배치 등 학습 하이퍼파라미터가 미명시.
- proprioception 입력의 정확한 shape·정규화가 미명시(embodiment 별로 다름).
