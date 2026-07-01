# Design — Hierarchical Policy Learning via Spectral Decomposition

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Hierarchical Policy Learning via Spectral Decomposition |
| 링크 | [arXiv:2606.29570](https://arxiv.org/abs/2606.29570) |
| 분석 문서 | [`analysis/2606.29570/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-07-01 |

---

## 🧮 데이터 계약

- **입력 — 관측** — $`o_t`$: 다시점 RGB, perception encoder 를 거쳐 $`N_{\mathrm{obs}}`$ 토큰. (해상도·카메라 수 원문 미명시 — 실물은 고정 + 손목 RGB 2대.)
- **입력 — proprioception** — $`u_t\in\mathbb{R}^{d_u}`$: end-effector pose + gripper state.
- **입력 — 언어** — $`\ell\in\mathbb{R}^{d_\ell}`$: frozen language encoder 투영 출력 1개(또는 소수) 토큰.
- **입력 — 전문가 action(학습 타깃)** — action chunk $`A_i=\{a_i,\ldots,a_{i+T-1}\}`$, 각 $`a_t\in\mathbb{R}^{D_a}`$, $`D_a=7`$ (6D twist + 1 gripper).
- **중간 표현 — spectral 계수** — twist 6채널에 type-II DCT(시간축) → $`C_i\in\mathbb{R}^{T\times 6}`$. cutoff $`\lambda`$(= `K_split`)로 $`C_i^{\mathrm{low}}=c_{0:\lambda}`$, $`C_i^{\mathrm{high}}=c_{\lambda:T}`$ 분할.
- **출력** — 예측 계수 $`\hat{C}_i=[\hat{C}_i^{\mathrm{low}},\hat{C}_i^{\mathrm{high}}]`$ → iDCT 로 시간영역 twist 복원, gripper 채널은 DCT 없이 그대로 concat → 최종 action chunk `(B, T, 7)`.
- **정규화** — action 정규화 통계 출처 원문 미명시 — `(원문에 명시 없음 — 가정으로 메움)` (데이터셋 전체 통계 가정).

---

## 🧰 모듈 인터페이스

```python
def dct_split(a_chunk, freq_split):        # a_chunk: (B, T, 6) twist only
    """type-II DCT along time, split into low/high coefficient slices."""
    # returns (c_low: (B, freq_split, 6), c_high: (B, T-freq_split, 6))

def low_predictor(obs_tokens, proprio, lang) -> c_low_hat:  # (B, freq_split, 6)
    """GPT-style trunk: coarse spectral coefficients from (o, u, l)."""

def high_predictor(obs_tokens, proprio, sg_c_low) -> c_high_hat:  # (B, T-freq_split, 6)
    """GPT-style trunk: fine coefficients conditioned on stop-grad(c_low_hat)."""

def idct_reconstruct(c_low_hat, c_high_hat, gripper) -> action_chunk:  # (B, T, 7)
    """concat low+high coeffs, inverse DCT on twist, append gripper channel."""

def frequency_split(demo_actions, K, alpha=0.9) -> int:   # data-driven K_split
    """empirical mean power spectrum → max(K_energy, K_elbow), optional snap."""
```

- **`low_predictor` / `high_predictor`** — 두 개의 독립 trunk(각 8 layers, hidden 256, heads 4). high 는 low 예측의 **stop-gradient** 사본에만 조건화(인과 방향 강제).
- **`frequency_split`** — 학습 전 1회 산정하는 전처리. task·chunk length $`K`$ 마다 별도.
- **loss 계약** — 두 예측기의 계수 회귀 손실 합(§📊). 옵티마이저와의 관계: 단일 backward 로 학습하되 sg 가 high→low gradient 경로를 차단.

---

## ⛓️ 불변식·가정

- (가정 1) **DCT 직교성** — $`F`$ 는 orthonormal 이라 $`\|\hat{a}-a\|_2^2=\|\hat{c}-c\|_2^2`$, 즉 계수공간 학습이 시간영역과 등가·가역. 이 성질이 깨지면 계수 회귀가 action 오차를 대변하지 못함.
- (가정 2) **주파수-스케일 대응** — 고정 control frequency 하에서 주파수 $`k`$ 의 계수는 대략 $`1/k`$ 시간 스케일 변동에 대응(저주파=느린 전역, 고주파=빠른 국소).
- (가정 3) **노이즈의 고주파 편재** — 텔레오퍼레이션 잡음 $`\eta=F\varepsilon`$ 이 $`\eta^{\mathrm{low}}\approx 0`$, $`\eta^{\mathrm{high}}`$ 큼. CSP 강건성 논증의 전제(깨지면 조건화 이득 소멸).
- (가정 4) **인과 비대칭** — 관측·언어는 주로 coarse 를 결정, fine 은 실현된 coarse 에 종속(언어는 fine 에 직접 개입하지 않음). counterfactual(Table 3)로 지지.
- (가정 5) **coarse 의 시연간 일관성** — 전역 task-level 이동은 데모간 일관, fine 보정은 변동 큼(spectral 분리의 데이터 근거).

---

## 📊 하이퍼파라미터·손실

- 손실 식: $`\mathcal{L}=\|\hat{c}^{\mathrm{low}}-c^{\mathrm{low}}\|_{2}^{2}+\|\hat{c}^{\mathrm{high}}-c^{\mathrm{high}}\|_{2}^{2}`$, with $`\hat{c}^{\mathrm{high}}=p_{\mathrm{high}}(o_t,\mathrm{sg}(\hat{c}^{\mathrm{low}}))`$ (Eq. 3).
- 인수분해: $`p(c\mid o_t,l)=p_{\mathrm{low}}(c^{\mathrm{low}}\mid o_t,l)\,p_{\mathrm{high}}(c^{\mathrm{high}}\mid o_t,c^{\mathrm{low}})`$ (Eq. 2).
- 하이퍼:

  | 이름 | 값 | 출처 |
  |------|----|----|
  | Action dim $`D_a`$ | 7 (6D twist + gripper) | §7.4, Table 5 |
  | Transformer hidden $`n_{\mathrm{embd}}`$ | 256 | Table 5 |
  | # Transformer layers | 8 (per stage) | Table 5 |
  | # Attention heads | 4 | Table 5 |
  | Block size | 65 | Table 5 |
  | Predict in frequency | Yes (twist only) | Table 5 |
  | Hierarchy | Two-stage (low + high) | Table 5 |
  | Frequency split 임계 $`\alpha`$ | ≈0.9–0.98 (누적 에너지) | §7.3 |
  | coarse 계수 비율 (통상) | 최저 ~30% (안정범위 20–40%) | §5.1.1, Fig. 5 |
  | Chunk size $`K`$ | {16, 32, 64} (평가) | §5.1 |
  | 손실 가중 (low vs high) | weighted sum (구체 가중치 원문 미명시) | §7.4 |
  | 옵티마이저 / LR / steps | (원문에 명시 없음 — 가정으로 메움) | — |

---

## 🎯 평가 메트릭

- **지표** — task success rate (%) · **임계값** — chunk length 증가 시 감쇠 완만성(정밀 과제 보존) · **비교 baseline** — ACT, BAKU, Diffusion Policy(DP-CNN/DP-Transformer), Action Binning, Frequency-Autoregressive.
- **벤치마크** — LIBERO-90 / LIBERO-10 (장기·언어조건), MimicGen (Stack/Stack3/Coffee/Square/Threading; 정밀), 실물 Franka (typing/stacking/assembly).
- **강건성 축** — no / small / large human-inspired noise 3조건 학습 → clean rollout 평가.

---

## ✨ 변경 의도 (intent)

기존 chunk-based·autoregressive 정책은 action 을 시간영역에서 균일하게 예측해 전역 계획(coarse)과 국소 보정(fine)을 얽어버립니다. 본 설계의 핵심 변경은 (1) action 을 DCT 로 주파수영역에 옮겨 coarse/fine 을 **표현 수준에서 명시 분리**하고, (2) 고주파를 실현된 저주파에 조건화하는 **방향성 인과 인수분해**(stop-gradient 로 강제)를 도입한 점입니다. FAST 류가 DCT 를 tokenization 효율에 쓴 것과 달리, 여기서는 coarse↔fine 의 인과 의존 자체를 학습 대상으로 삼아 노이즈 시연 하에서 fine 감독의 모호성을 줄이고 조건부-평균 붕괴를 회피합니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — action 표현·손실을 바꾸는 설계이므로, 연속 action chunk 를 예측하는 `act`(transformer chunk 예측) 또는 `diffusion` family 에 가장 가깝습니다. twist-only DCT 전처리 + 2-stage 계수 예측 head 를 action head 자리에 끼우는 형태. π-계열(`pi0`) 의 flow-matching expert 를 spectral 회귀 head 로 대체하는 변형도 후보이나 backbone freeze 양립성 확인 필요.

---

## 🚧 미해결 / 잠정

- 저/고주파 손실의 **가중치**가 본문에 수치로 명시되지 않음("weighted sum" 만 언급) — 동일 가중 가정.
- **옵티마이저·학습률·스텝·seed 개수(2 이상)** 세부 미명시 — 완전 재현엔 저자 코드 필요.
- **perception/language encoder 의 구체 구조**(어떤 backbone, frozen 범위) 부분 명시 — language encoder 는 frozen 으로만 기술.
- gripper 이산 채널을 spectral 밖으로 우회하는 처리의 정확한 구현(concat 시점·정규화)은 개략만 기술.
- action 정규화 통계 출처 미명시 — 데이터셋 전체 통계 가정.
