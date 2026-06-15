# Design — APT: Action Expert Pretraining Improves Instruction Generalization of Vision-Language-Action Policies

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | APT: Action Expert Pretraining Improves Instruction Generalization of Vision-Language-Action Policies |
| 링크 | [arXiv:2606.12366](https://arxiv.org/abs/2606.12366) |
| 분석 문서 | [`analysis/2606.12366/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-15 |

---

## 🧮 데이터 계약

- **입력 — 시각** `v`: shape `(B, V, C, 256, 256)` (V = 카메라 수, wrist + 3rd-view), Qwen3-VL-2B-Instruct vision encoder 를 거쳐 visual token 으로 변환. 정규화는 VLM 전처리 표준.
- **입력 — 언어** `ℓ`: token id 시퀀스 `(B, L_text)`. Stage 1 에서는 action expert self-attention 에서 **완전 마스킹**, Stage 2 에서 unmask.
- **입력 — proprioception** `s_prop`: shape `(B, 10)`, 액션 표현과 동일한 카메라-프레임 10-DoF 벡터.
- **입력 — 액션 이력** `a_hist`: shape `(B, H, 10)`, `H=1` (history action length 1).
- **출력 — 액션** `a`: shape `(B, T_a, 10)`, `T_a=32` (action chunk). 10-DoF = 3D translation + 6D 연속 회전 + 1D 정규화 gripper width (`-1` 닫힘, `+1` 열림), SE(3) manifold, **카메라 좌표계** 표현. diffusion(DDPM 학습 100 step / DDIM 추론 20 step) 으로 생성.
- **정규화 가정** — gripper width 는 `[-1,+1]` 정규화. translation/rotation 의 데이터셋 통계 정규화는 (원문에 명시 없음 — 가정으로 메움: 데이터셋 전체 평균/표준편차).

---

## 🧰 모듈 인터페이스

```python
def va_prior_stage1(v, a_hist, s_prop, a_noisy, t) -> a_pred:
    """Stage 1: 언어 마스킹 상태에서 N/2 층만 활성, 순수 vision-action 함수.
       [h_v, h_a] = SelfAttn([v, a]) — VLM 파라미터 전부 동결."""

def vla_likelihood_stage2(v, ell, a_hist, s_prop, a_noisy, t) -> a_pred:
    """Stage 2: N/2 → N 층 보간 확장, 언어 unmask.
       [h_v, h_ell, h_a] = SelfAttn([v, ell, a]) — 상속 층은 Stage1 ckpt 초기화,
       신규 층은 랜덤. 전체 N 층 + (옵션) VLM joint FT."""

def gated_fusion(h_out_i, phi_i_vlm, w_hat_i) -> h_in_next:
    """VLM layer feature 를 learnable gate 로 action expert 층에 주입.
       h_in^{(i+1)} = h_out^{(i)} + sigmoid(w_hat_i) * phi_i_qwen3vl(v, ell)."""
```

- **`va_prior_stage1`** — 역할: shortcut 없는 VA prior 학습. 입력: 시각 + proprio + noisy action + denoise timestep. 출력: denoised action. 외부 계약: VLM frozen, 언어 토큰 attention 마스킹, denoise loss(diffusion) 와만 결합.
- **`vla_likelihood_stage2`** — 역할: 사전학습 prior 를 언어로 조향. 상속 `N/2` 층(PRoPE) + 신규 보간 `N/2` 층(mRoPE) = `N=20` 층. 외부 계약: 전체 층 joint 최적화(prior 동결 안 함), VLM 은 freeze 또는 joint FT 선택.
- **`gated_fusion`** — 역할: layer-wise VLM feature 흡수. 입력: 직전 층 출력 + 대응 VLM 중간 feature + learnable scalar. 출력: 다음 층 입력. 외부 계약: gate 스칼라는 학습 대상, FiLM(timestep) 과 별개 경로.

---

## ⛓️ 불변식·가정

- (가정 1) **데이터 불균형** — 대부분 시각 프레임에서 언어가 거의 결정적: $`H(\ell\mid\mathbf{v})\leq\epsilon`$. 이게 깨지면(언어가 진짜 다양) VA-prior 사전학습의 동기가 약해진다.
- (가정 2) **vision-action pair 균형** — 매 시각 프레임이 고유 액션과 1:1 라벨되어, vision-action 만 떼면 shortcut 유인이 없다.
- (가정 3) **prior 가 likelihood 의 하한** — $`\mathcal{L}_{\mathrm{VLA}}\leq\min-\mathbb{E}[\log\pi(\mathbf{a}\mid f_{\theta_{\mathrm{VA}}}(\mathbf{v}),\ell)]\leq\mathcal{L}_{\mathrm{VA}}`$. 손실이 prior 하한 아래로 더 줄 수 있어야 언어가 실제로 쓰인다.
- (가정 4) **층 보간 호환** — Stage 1 의 `N/2` 층 사이에 새 층을 끼워도 상속 표현이 보존됨(상속 층 PRoPE 유지가 전제).

---

## 📊 하이퍼파라미터·손실

- 손실 식: 표준 VLA NLL $`\min\;-\mathbb{E}_{(\mathbf{a},\mathbf{v},\ell)\sim\mathcal{D}_{\mathrm{VLA}}}[\log\pi(\mathbf{a}\mid\mathbf{v},\ell)]`$ 를 Bayesian 분해 $`\pi(\mathbf{a}\mid\mathbf{v},\ell)\propto\pi^{p}(\mathbf{a}\mid\mathbf{v})\cdot\mathcal{L}(\ell\mid\mathbf{v},\mathbf{a})`$ 로 두고, Stage 1=VA NLL, Stage 2=VLA NLL (diffusion denoising loss).
- 게이트 식: $`\mathbf{h}^{(i+1)}_{\text{in}}=\mathbf{h}^{(i)}_{\text{out}}+\sigma(\hat{w}_{i})\cdot\phi_{i}^{\text{Qwen3-VL}}(\mathbf{v},\ell)`$.
- 하이퍼:

  | 이름 | 값 | 출처 |
  |------|----|----|
  | `N` (action expert 층) | `20` | Appendix A |
  | `T_a` (action chunk) | `32` | Appendix A |
  | history action length | `1` | Appendix A |
  | action expert lr / wd | `1e-4` / `1e-2` | Appendix A |
  | VLM lr / wd (joint FT 시) | `1e-5` / `1e-10` | Appendix A |
  | batch size | `256` | Appendix A |
  | Stage 1 / Stage 2 iter | `100k` / `100k` | Appendix A |
  | diffusion (train / infer) | DDPM 100 step / DDIM 20 step | Appendix A |
  | encoder/decoder MLP | 2-layer, hidden `768` | Appendix A |
  | 입력 이미지 | `256×256` (wrist + 3rd) | Appendix A |
  | 사전학습 샘플 가중 | DROID:AgiBot:InternData:InternVLA = `5:5:4:1` | Appendix A |

---

## 🎯 평가 메트릭

- **지표** — task success rate (%) · **임계값** — OOD 언어 일반화 split 별 비교(SO/UO/UC/UOUE, LIBERO-PRO Pos/Task) · **비교 baseline** — $`\pi_{0}`$, $`\pi_{0.5}`$(KI), LangForce, OpenVLA, CaP-X.
- 설계 차원 ablation 축: `KI` × `2-Stage` × `Ft VLM` 의 조합으로 이득 출처를 분리(Table 2). 핵심 판정: 2-Stage+Ft VLM 이 최고, KI 는 비-필요조건.

---

## ✨ 변경 의도 (intent)

기존 연속-액션 VLA 는 action expert 를 랜덤 초기화에서 불균형 VLA 데이터로 joint 학습해 visual shortcut 에 빠지고, 이를 막으려 KI(stop-gradient) 나 웹-scale VL co-training 에 의존했다. APT 는 문제를 *초기화* 로 재정의해, 정책을 VA prior × VLA likelihood 로 Bayesian 분해하고 균형 데이터인 vision-action pair 만으로 action expert 를 먼저 사전학습한다. 결과적으로 별도 reasoning 데이터·gradient 차단 없이 OOD 언어 일반화를 얻으며, 잘 초기화된 prior 위에선 VLM joint FT 가 오히려 이득이 된다. gated fusion 은 VLM feature 를 덮어쓰지 않고 learnable gate 로 흡수해 사전학습된 VA prior 를 보존하는 것이 BayesVLA(prior 동결)·Token Insertion(직접 삽입) 대비 차별점.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 후보 base: diffusion 기반 연속 action expert + VLM 결합이라 `pi0` / `pi05` family 와 가장 가깝다. 다만 APT 는 (a) action expert 를 **언어 마스킹 상태로 사전학습**하는 2-stage 절차와 (b) layer-wise gated fusion(`sigmoid(w_hat)` per-layer VLM feature 주입) 이 핵심이라, `pi0` 의 단일-stage joint 학습 루프와 block-wise self-attention 구조에 이 두 메커니즘을 새로 얹어야 한다. `diffusion` policy 의 denoising 루프는 재활용 가능하나 VLM feature 주입 경로는 신규.

---

## 🚧 미해결 / 잠정

- translation/rotation 액션 정규화 통계의 출처가 본문에 없어 "데이터셋 전체 평균/표준편차" 로 가정.
- `phi_i_qwen3vl` 의 "등간격 $`N`$ 개 중간 feature 샘플링" 의 정확한 층 인덱스 매핑(20층 expert ↔ Qwen3-VL 층 수) 은 본문에 수치로 명시 없음.
- gate 스칼라 $`\hat{w}_{i}`$ 의 초기값이 본문에 명시 없음(가정: 0 근처 초기화로 초기엔 prior 우세).
- Stage 2 의 "interleaved attention layer 삽입" 시 신규 층의 파라미터 초기화 방식(랜덤 외 세부) 미명시.
- flow-matching head 로의 치환 가능성은 본 논문 범위 밖(원문은 DDPM/DDIM diffusion).
