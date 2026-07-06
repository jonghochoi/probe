# Design — VT-WAM: Visual-Tactile World Action Model for Contact-Rich Manipulation

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | VT-WAM: Visual-Tactile World Action Model for Contact-Rich Manipulation |
| 링크 | [arXiv:2607.02503](https://arxiv.org/abs/2607.02503) |
| 분석 문서 | [`analysis/2607.02503/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-07-06 |

---

## 🧮 데이터 계약

시간 축은 의미 단위(`T_v`, `T_t`, `S_a`)로 기록합니다. 토큰 수 $`N_v, N_t, F_v`$ 및 개별 차원 다수는 원문 미명시 — 가정으로 메웁니다.

- **입력 — 시각** $`\mathbf{O}^{v}`$: shape `(B, T_v, 3, H, W)`, uint8→정규화 `float32`; 손목 카메라 RGB, `H=W=128` (§IV-A2). Wan2.2 video VAE 인코딩 후 patchify → 시각 토큰 $`\mathbf{X}_v`$ `(B, N_v, d)`.
- **입력 — 촉각** $`\mathbf{O}^{t}`$: shape `(B, T_t, 6, H_t, W_t)`, `float32`; 두 촉각 표면의 3D 변형장, `H_t=35, W_t=20` (§IV-A1, 채널 6 = 2 표면 × 3D). 사전학습 tactile VAE(OmniVTA) 인코딩 → 촉각 토큰 $`\mathbf{X}_t`$ `(B, N_t, d)`.
- **입력 — 행동** $`\mathbf{A}`$: shape `(B, S_a, D_a)`, `float32`; 선형 투영 → 행동 토큰 $`\mathbf{X}_a`$ `(B, S_a, d)`. `D_a` = xArm7 관절 + 그리퍼 (원문 미명시).
- **입력 — 언어·상태**: 언어 지시 $`c`$ (토큰 시퀀스), proprioception $`\mathbf{s}`$ `(B, D_state)`; cross-attention으로 각 전문가에 공급.
- **출력 — velocity fields**: $`\hat{\mathbf{f}}^{v}, \hat{\mathbf{f}}^{t}, \hat{\mathbf{f}}^{a}`$ — 각 모달리티 토큰과 동일 shape, flow matching target에 회귀.
- **제어 출력**: 행동 청크 $`\mathbf{A}`$ `(B, S_a, D_a)`; visual-cache 추론 모드에서 10 denoising step으로 생성 (§IV-A2).
- **동기화/샘플링**: 모든 스트림 30Hz 리샘플 (§IV-A2).

---

## 🧰 모듈 인터페이스

```python
def visual_tactile_action_tokenize(O_v, O_t, A, c, s):
    """세 모달리티를 토큰으로 인코딩. 시각=Wan2.2 VAE+patchify,
    촉각=사전학습 tactile VAE(OmniVTA), 행동=선형 투영.
    언어·proprio 는 cross-attention 공급용으로 별도 반환."""
    # -> X_v (B,N_v,d), X_t (B,N_t,d), X_a (B,S_a,d), ctx(c,s)

def asymmetric_mot_attention(Q, K, V, M):
    """MoT 레이어: [v;t;a] 순 concat 된 Q/K/V 에 블록별 마스크 M 적용.
    P = softmax(QKᵀ/√d + M); Y = P V. 반환 = 갱신된 v/t/a 토큰."""
    # -> Y (B, N_v+N_t+S_a, d)

def build_block_mask(F_v, N_v, N_t, S_a):
    """비대칭 리드아웃 마스크. 허용=0, 차단=-inf.
    action→{first-frame visual anchor, full tactile}; visual→visual only;
    tactile→{first-frame visual anchor, tactile}."""
    # -> M (L_tot, L_tot), L_tot = N_v+N_t+S_a

def avtag_loss(Q_a, K_v, K_t, contact_mask):
    """훈련 전용. sg(K_vt) 로 보조 어텐션 P_vt 구성 → 행동 토큰별
    상대 시각/촉각 가중치 p_v/p_t → 접촉 구간 hinge ranking."""
    # -> scalar L_AVTAG

def flow_matching_loss(f_hat, f_star, lambdas):
    """모달리티별 velocity MSE 의 가중합 L_Flow."""
    # -> scalar L_Flow

def visual_cache_inference(O_v_current, O_t, A_noise, ctx):
    """배포 모드: 현재 시각을 first-frame anchor 로 캐시, 미래 시각 예측 제거.
    촉각·행동 latent 만 Asymmetric MoT Attention 으로 디노이징."""
    # -> action_chunk (B, S_a, D_a)
```

- **`asymmetric_mot_attention`** — Q/K/V는 각 전문가가 자기 스트림에서 계산 후 `[v;t;a]` 순 concat. 마스크 `M`이 정보 흐름을 결정 (§III-A/B).
- **`build_block_mask`** — 세 전문가별 6개 블록 규칙(§III-B 수식). 훈련=미래 시각 토큰 포함, 추론=미래 시각 토큰 제거.
- **`avtag_loss`** — `sg(·)` = stop-gradient (시각·촉각 key 표현 보존). `contact_mask` = 뚜렷한 촉각 변형으로 식별한 접촉 구간 행동 토큰 $`\mathcal{C}`$.

---

## ⛓️ 불변식·가정

- **(불변식 1)** 어텐션 마스크 `M`의 항은 0(허용) 또는 $`-\infty`$(차단) 뿐이며, 시각 전문가 행은 촉각·행동 열을 항상 차단한다 — 시각 표현이 국소 접촉·미래 행동에 오염되지 않아야 한다 (§III-B).
- **(불변식 2)** 행동·촉각 전문가는 시각 토큰 중 첫 프레임 앵커($`F_v`$ 열)만 attend하고 나머지 시각 열은 차단 — visual-cache 추론이 훈련 마스크와 동일 정보 접근을 갖는다 (§III-B).
- **(가정 3)** AVTAG의 stop-gradient로 보조 어텐션 그래디언트는 행동 query만 갱신하고 시각·촉각 key는 주 flow matching 목적함수로만 최적화된다 (§III-C).
- **(가정 4)** hinge 손실 $`\max(0, p_v-p_t)`$ 는 $`p_t \geq p_v`$ 에서 0 — 촉각을 시각 이상으로만 끌어올리고 과도 강제하지 않는다 (§III-C).
- **(가정 5, 원문에 명시 없음 — 가정으로 메움)** 접촉 구간 $`\mathcal{C}`$ 판정은 촉각 변형 magnitude에 대한 임계값 기반이며, 임계값은 데이터셋 통계로 정해진다고 가정.

---

## 📊 하이퍼파라미터·손실

- **주 손실 (flow matching)**:

$$L_{\mathrm{Flow}}=\lambda_{v}L_{v}+\lambda_{t}L_{t}+\lambda_{a}L_{a},\quad L_{m}=\mathbb{E}\|\hat{\mathbf{f}}^{m}-\mathbf{f}_{m}^{*}\|^{2}\ (m\in\{v,t,a\})$$

- **보조 손실 (AVTAG)**:

$$L_{\mathrm{AVTAG}}=\mathbb{E}_{r\in\mathcal{C}}\left[\max\left(0,\;p_{v}(r)-p_{t}(r)\right)\right],\qquad p_{m}(r)=\frac{\alpha_{m}(r)}{\alpha_{v}(r)+\alpha_{t}(r)}$$

- **전체 목적함수**: $`L_{\mathrm{Train}}=L_{\mathrm{Flow}}+\lambda_{\mathrm{AVTAG}}L_{\mathrm{AVTAG}}`$

| 이름 | 값 | 출처 |
|------|----|----|
| `lambda_v`, `lambda_t`, `lambda_a` | `1`, `1`, `1` | §IV-A2 |
| `lambda_AVTAG` | `0.05` | §IV-A2 |
| optimizer | `AdamW` | §IV-A2 |
| learning rate | `1e-4` | §IV-A2 |
| weight decay | `1e-2` | §IV-A2 |
| precision | `bf16` mixed | §IV-A2 |
| gradient clip | `1.0` | §IV-A2 |
| LR schedule | cosine decay, `5%` warmup | §IV-A2 |
| denoising steps (inference) | `10` | §IV-A2 |
| visual backbone | Wan2.2-5B (pretrained) | §IV-A2 |
| tactile/action expert | 1B-scale DiT (각각) | §IV-A2 |
| 궤적 수 / 과제 | `100` (kinesthetic teaching) | §IV-A2 |
| 샘플링 주파수 | `30 Hz` | §IV-A2 |
| `N_v, N_t, F_v, S_a, D_a` | (원문 미명시) | — |

---

## 🎯 평가 메트릭

- **과제 성공률** — 표면 상호작용: 점수 $`\{0,0.5,1\}`$ (0.5 = 목표 영역 절반 이상), 제약 삽입: 이진 $`\{0,1\}`$; 과제·방법당 20회 독립 시행 평균 (§IV-B2).
- **비교 baseline** — DP+Tactile, RDP, $`\pi_{0.5}`$, OmniVTLA, Fast-WAM (§IV-A3). 주 목표치: Fast-WAM 45.00% → VT-WAM 71.67% (+26.67%p).
- **촉각 예측 품질** — 변형 크기 오차 $`l_2\downarrow`$ (전체 3D 변형장), 방향 일관성 $`\cos\uparrow`$ (비영 변형 영역); baseline exUMI/UVA 대비 (§IV-C2, Table II).

---

## ✨ 변경 의도 (intent)

기존 시각-촉각 정책은 촉각을 행동 예측의 *입력*으로만 넣고 촉각 변형의 시간축 *동역학*을 모델링하지 않아, 조밀한 시각에 편향되어 촉각을 저활용합니다. VT-WAM은 (1) 촉각 변형 예측을 시각·행동과 함께 단일 flow matching 목적함수로 승격하여 접촉 진화가 행동에 직접 정보를 주게 하고, (2) 행동 토큰이 전체 촉각에는 붙되 시각은 첫 프레임 앵커에만 붙는 비대칭 MoT 마스크로 배포 시 미래 시각 예측을 제거하며, (3) 접촉 구간 전용 hinge ranking 손실(AVTAG)로 추론 아키텍처를 바꾸지 않고 시각-지배 편향만 훈련 시 교정한다는 점에서 prior WAM(시각 전용 Fast-WAM)과 시각-촉각 융합 정책(OmniVTLA/ViTacFormer) 양쪽과 다릅니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 후보 base: flow-matching 행동 전문가 + 멀티모달 토큰 융합이라 `pi0` / `pi05` family가 가장 가깝습니다. 다만 VT-WAM은 세 모달리티 velocity head를 공동 학습하는 MoT 백본 + 촉각/시각 예측 브랜치가 추가로 필요해, 표준 `pi0`의 단일 action-expert를 넘어 촉각·시각 전문가와 비대칭 마스크를 신설해야 합니다. AVTAG 보조 손실은 백본 무관이라 어텐션 맵 접근이 가능한 임의 base에 얹을 수 있습니다.

---

## 🚧 미해결 / 잠정

- 토큰 수 $`N_v, N_t, F_v`$, 행동 청크 길이 $`S_a`$, 행동 차원 $`D_a`$, proprio 차원이 본문에 명시되지 않아 데이터 계약에서 심볼로만 남김.
- 접촉 구간 $`\mathcal{C}`$ 판정의 정확한 임계값·통계가 미명시 — "뚜렷한 촉각 변형" 서술만 있어 magnitude 임계값 가정으로 메움.
- flow matching target $`\mathbf{f}_m^{*}`$ 의 확률 경로(선형 여부)·시간 샘플링 분포가 본문에 세부 미명시.
- tactile VAE 구조·사전학습 방식은 OmniVTA(외부 논문) 의존이라 본 논문 범위 밖.
- visual-cache 추론에서 첫 프레임 시각 앵커의 캐싱·재사용 구현 세부(예: 앵커 갱신 주기)가 미명시.
