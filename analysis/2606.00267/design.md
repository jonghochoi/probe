# Design — StressDream: Steering Video World Models for Robust Policy Evaluation and Improvement

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | StressDream: Steering Video World Models for Robust Policy Evaluation and Improvement |
| 링크 | [arXiv:2606.00267](https://arxiv.org/abs/2606.00267) |
| 분석 문서 | [`analysis/2606.00267/analysis.md`](./analysis.md) |
| 본문 확보 수준 | PDF 텍스트(pypdf) |
| Design 생성일 | 2026-07-02 |

---

## 🧮 데이터 계약

- **입력 — 관찰 히스토리** `o_hist`: `n` 개 카메라 RGB 프레임 시퀀스 (+ 고유수용성 상태 `q`). 조작 인스턴스: `3` 뷰 × `(192, 320, 3)` @ `5 Hz`; 주행 인스턴스: `1` 뷰 × `(576, 1024, 3)` @ `10 Hz`. dtype/정규화 `(원문에 명시 없음 — 가정으로 메움)` — WM 백본(SVD 계열 latent diffusion)의 VAE 인코더 규약을 따른다고 가정.
- **입력 — 행동 시퀀스** `a`: shape `(T_action,)` 평탄화 벡터. 주행: 8-dim (미래 waypoint 4개, top-down); 조작: 40-dim ( `8×H`, `H=5`, 관절 위치 + 그리퍼 명령).
- **입력 — 초기 노이즈** $`\epsilon \in \mathbb{R}^D`$, $`\epsilon \sim \mathcal{N}(0, I_D)`$. `D` 는 WM latent 비디오 차원 (주행 921,600 / 조작 57,600 / 통제 실험 1,024). 최적화의 유일한 자유 변수.
- **입력 — 텍스트 프롬프트** `l`: 목표 고임팩트 이벤트의 자연어 기술 + "Respond with a single word: Yes or No." 형식의 단답 지시.
- **입력 — 동결 모듈** — 행동 조건부 확산 비디오 WM $`f_\theta`$ (결정론적 probability-flow ODE 샘플러, denoising steps `K=50`), 미분가능 VLM 검증자 (조작: 3뷰 동시 입력).
- **출력** — 스티어링된 비디오 $`o^* = f_\theta(\epsilon^*, o_{\mathrm{hist}}, a)`$: latent $`z \in \mathbb{R}^{4 \times H/8 \times W/8}`$ → VAE 디코딩된 RGB 프레임 `H_pred` 장, 부수 출력으로 최고 의미 점수 $`\mathcal{C}^*`$ (스칼라).
- **출력 (정책 개선 트랙)** — 시연별 가중치 $`w \in \{1.0, 0.1\}`$: 스티어링 하에서도 성공이면 1.0, 실패로 스티어링되면 0.1. 정책 파인튜닝 손실·데이터 샘플링 양쪽에 곱해짐.

---

## 🧰 모듈 인터페이스

```python
def steer(f_theta, o_hist, a, l, m, eta, beta, pla_cfg) -> tuple[Video, float]:
    """Algorithm 1: 초기 노이즈를 m회 경사 상승으로 최적화해
    최고 의미 점수의 생성물 (o_star, C_star) 를 반환. f_theta/VLM 은 동결."""

def c_sem(o, l, vlm) -> float:
    """의미 목적식 (식 6): log p_VLM(yes|o,l) - log p_VLM(no|o,l).
    CLIP 계열 변형: sim(e_video, e_text(l+)) - sim(e_video, e_text(l-))."""

def c_pla(eps, lam1, lam2, lam3, iso_k, iso_perms, spec_bins) -> float:
    """그럴듯함 목적식: lam1*C_norm + lam2*C_iso + lam3*C_spec.
    노름 껍질 / 블록 등방성(무작위 치환 평균) / 스펙트럼 백색성."""

def grad_step(eps, o, l, beta, pla_cfg) -> Tensor:
    """식 8: g = beta * grad_o c_sem(o,l) + grad_eps c_pla(eps).
    좌표별 clamp(±0.3) → 전역 노름 클리핑(1.0). 모멘텀 없음."""

def shell_project(eps, threshold=3.0) -> Tensor:
    """| ||eps||_2 - sqrt(D) | > threshold 이면 eps *= sqrt(D)/||eps||_2."""

def weighted_finetune(policy, demos, weights) -> Policy:
    """가중 flow-matching 회귀: per-demo weight 를 손실과 샘플링에 적용해
    정책(π0.5 류)을 파인튜닝. weights 는 steer() 결과의 성공/실패 판정에서 유도."""
```

- `steer` 는 매 반복 `o_i = f_theta(eps_i, o_hist, a)` 전체 생성을 요구합니다 (반복당 denoising `K` 회 + 검증자 forward/backward 1회씩).
- `c_sem` 의 기울기는 비디오 공간에서 계산되고, `grad_step` 의 score-distillation 근사가 이를 스칼라 $`\beta`$ 배로 노이즈 기울기의 대리로 씁니다 — denoising 궤적 역전파는 호출 계약에 없음.
- `c_pla` 의 기울기는 노이즈에 직접 닿으므로 근사가 필요 없습니다.

---

## ⛓️ 불변식·가정

- (가정 1) — **샘플러 결정론**: 고정된 `(o_hist, a)` 에서 $`o = f_\theta(\epsilon, o_{\mathrm{hist}}, a)`$ 는 초기 노이즈의 결정론적·미분가능 함수여야 합니다 (probability-flow ODE / DDIM·EDM 계열). 확률적 샘플러(ancestral sampling)에서는 "노이즈 = 제어 변수" 전제가 무너집니다.
- (가정 2) — **전형 집합 통계**: 훈련 시 노이즈는 $`\mathcal{N}(0, I_D)`$ 표본이므로 $`\|\epsilon\|_2 \approx \sqrt{D}`$ (껍질 폭 $`\to 1/\sqrt{2}`$, 차원 무관), 블록 등방성 $`\widehat{\Sigma} \approx I_k`$, 평탄 파워 스펙트럼이 성립합니다. 최적화된 노이즈가 이 통계를 벗어나면 denoiser 가 미학습 입력을 받아 생성이 무효화됩니다.
- (가정 3) — **대각 Jacobian 근사**: denoiser Jacobian $`J_g^\tau \approx \rho_\tau I`$ → 샘플러 Jacobian 곱 $`\approx \beta I`$. 이 가정이 깨지는 아키텍처에서는 식 (7) 근사 기울기가 무의미해집니다 (경험적 근거만 있음; 역으로 50-step 전체 역전파는 정밀도 문제로 오히려 실패).
- (가정 4) — **WM 분포 지지**: 목표 이벤트가 WM 의 학습된 결과 분포에 존재해야만 스티어링이 생성할 수 있습니다 (base 모델은 충돌을 상상 불가). 따라서 WM 파인튜닝 데이터에 실패·희귀 이벤트가 포함되어야 합니다.
- (가정 5) — **검증자 미분가능성·판별력**: VLM 이 생성 비디오에서 목표 이벤트를 yes/no 토큰 확률로 판별할 수 있어야 하며 (조작에서는 멀티뷰 동시 입력 필수), 기울기 접근이 가능한 오픈소스 모델이어야 합니다.
- (가정 6) — **국소 정제 한계**: i.i.d. 가우시안 쌍 거리는 $`\sqrt{2D}`$ 에 집중하나 최적화 이동량은 그보다 훨씬 작음 — 알고리즘은 초기 노이즈 근방의 국소 탐색이며 전역 최악-사례 보장이 없습니다.

---

## 📊 하이퍼파라미터·손실

**스티어링 목적식** (전체 기준):

$$\mathcal{C}_{\mathrm{test}} = \mathcal{C}_{\mathrm{sem}} + \mathcal{C}_{\mathrm{pla}}$$

$$\mathcal{C}_{\mathrm{sem}}(o; l) = \log p_{\mathrm{VLM}}(\text{yes} \mid o, l) - \log p_{\mathrm{VLM}}(\text{no} \mid o, l)$$

$$\mathcal{C}_{\mathrm{pla}}(\epsilon) = \lambda_1 \mathcal{C}_{\mathrm{norm}}(\epsilon) + \lambda_2 \mathcal{C}_{\mathrm{iso}}(\epsilon) + \lambda_3 \mathcal{C}_{\mathrm{spec}}(\epsilon)$$

$$\mathcal{C}_{\mathrm{norm}}(\epsilon) := -\big(\|\epsilon\|_2 - \sqrt{D}\big)^2, \quad \mathcal{C}_{\mathrm{iso}}(\epsilon) := -\frac{1}{k}\big\|\widehat{\Sigma} - I_k\big\|_F^2, \quad \mathcal{C}_{\mathrm{spec}}(\epsilon) := -\frac{1}{B}\sum_{b=1}^{B}(\hat{p}_b - \bar{p})^2$$

**업데이트 규칙** (식 5 + 식 8 근사):

$$\epsilon_{i+1} = \epsilon_i + \eta \cdot \mathrm{clip}\big(\beta\, \nabla_{o_i} \mathcal{C}_{\mathrm{sem}}(o_i; l) + \nabla_{\epsilon_i} \mathcal{C}_{\mathrm{pla}}(\epsilon_i)\big)$$

**정책 개선 손실** — 가중 flow-matching 회귀 (인용 [13] 목적식): per-demo weight `w` 를 손실과 데이터 샘플링에 곱함. `w = 1.0` (스티어링 하 성공) / `w = 0.1` (스티어링 하 실패).

**하이퍼파라미터** (출처: 논문 Table 3 / 5 / 6, §B.5, §D.5):

| 이름 | 값 (주행 Vista / 조작 Ctrl-World / 통제 Dubins) | 출처 |
|------|----|----|
| `optimization_iterations` `m` | 20 / 10 / 10 | Table 5, 6, 3 |
| `step_size` $`\eta`$ | 1.0 / 1.0 / 1.0 | Table 5, 6, 3 |
| `grad_scale` $`\beta`$ | 300.0 / 100.0 / 10.0 | Table 5, 6, 3 |
| $`\lambda_1`$ (norm) | 0.5 / 0.2 / 1.0 | Table 5, 6, 3 |
| $`\lambda_2`$ (iso) | 10.0 / 0.1 / 0.5 | Table 5, 6, 3 |
| `iso_subvector_k` | 192 / 240 / 16 | Table 5, 6, 3 |
| `iso_permutations` | 1,000 / 1,000 / 100 | Table 5, 6, 3 |
| $`\lambda_3`$ (spec) | 100.0 / 100.0 / 5.0 | Table 5, 6, 3 |
| `spec_bins` `B` | `(원문 미명시)` | §4.2 |
| `grad_clamp` (좌표별) | `±0.3` | Alg. 1 |
| `grad_norm_clip` | 1.0 | Alg. 1 |
| `shell_proj_threshold` | 3.0 | §B.5 |
| `momentum` | 사용 안 함 | §B.5 |
| `denoising_steps` `K` | 50 / 50 / 5 | Table 5, 6, §C.1 |
| `cfg_scale` | 2.5 / 2.0 / — | Table 5, 6 |
| `demo_weight` (개선 트랙) | `{1.0, 0.1}` | §6.2 |
| `demos_per_task` / `ft_steps` (개선 트랙) | 40 / 10k (H100 1장) | §D.5 |
| `open_loop_horizon` (개선 트랙) | 16 | §D.5 |
| WM 파인튜닝 (조작) | lr `1e-6`, batch 64, 10,000 iter, 태스크당 궤적 100–250 | §D.1, Table 7 |
| WM 파인튜닝 (주행) | 13,750 iter, batch 256 | §D.1 |

---

## 🎯 평가 메트릭

- **지표** — 실패 검출 recall (참 실패 궤적 중 스티어링 상상이 실패로 판정되는 비율, 인간 판정) · **임계값** — StressDream 94% vs 베이스라인 54% (§1 verbatim "(54%→94%)") · **비교 baseline** — Nominal(N=1), Best-of-N(N=10)
- **지표** — 통제 실험 TPR / TNR (몬테카를로 10,000회 참 라벨 대비) · **임계값** — TPR·TNR 동시 高 (수치는 Fig. 2 그래프) · **비교 baseline** — Nominal, Best-of-N, Classifier Guidance, w/o $`\mathcal{C}_{\mathrm{pla}}`$
- **지표** — WorldModelBench: instruction following(0–3, 정렬) + physics adherence(0–5)·commonsense(0–2, 그럴듯함 대리); Gemini-3.0 판정(0–10); WorldLens subject/temporal consistency·depth discrepancy · **비교 baseline** — Best-of-N, w/o $`\mathcal{C}_{\mathrm{pla}}`$
- **지표** — 노이즈 전형성·OOD: chi-square 노름 로그확률, 등방성·스펙트럼 정칙자 값, flow-matching 잠재 OOD 점수 $`s_{\mathrm{OOD}} = \|\hat{w}\|_2^2`$ · **임계값** — 전 정칙화 제거 시 OOD 167→697 (Table 4)
- **지표** — 정책 성공률 (태스크당 20 실제 롤아웃, 6 태스크) · **임계값** — Robust 71% vs Nominal 39% · **비교 baseline** — 균일 가중(1.0) 파인튜닝

---

## ✨ 변경 의도 (intent)

기존 WM 기반 정책 평가·개선은 명목(nominal) 상상 — 분포에서 무작위로 뽑은 한 미래 — 에 의존해 드문 고임팩트 실패를 체계적으로 놓칩니다. StressDream 의 의도는 WM 을 재학습하지 않고, 생성이 초기 노이즈의 결정론적 함수라는 성질만으로 평가를 min-max(비관적)로 바꾸는 것입니다: VLM 토큰 확률이 "무엇을 향해"(추론 시점 텍스트로 지정된 이벤트)를 제공하고, 가우시안 전형 집합 정칙화가 "어디까지만"(WM 분포가 지지하는 범위)을 강제하며, score-distillation 근사가 이를 수백만 차원에서 실행 가능하게 만듭니다. classifier guidance(경로 왜곡으로 OOD 생성)·Best-of-N(0차 탐색의 표본 비효율)·보상 파인튜닝(기준별 재학습·분포 이탈) 대비, 동결 모델 + 임의 기준 + 그럴듯함 보존을 동시에 달성하는 것이 차별점입니다. 개선 트랙의 의도는 이 비관적 상상을 시연 라벨러로 써서, "우연히 성공한 위험 시연"의 영향력을 가중치 0.1 로 낮추는 것입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 직접 대응 base 없음에 가까움: 스티어링 대상인 생성형 비디오 WM(SVD 계열)이 lerobot 에 없습니다. 개념적 인접 지점은 (a) `diffusion` (Diffusion Policy) 의 action-space 초기 노이즈 + 결정론적 샘플러 (스티어링 루프의 축소 이식 후보), (b) `pi05` 의 flow-matching 파인튜닝 손실에 `per_demo_weight` 를 곱하는 가중 회귀 트랙 (WM 없이 매핑 가능한 절반). `vla_jepa` 는 비생성 latent 예측이라 부적합.

---

## 🚧 미해결 / 잠정

- 스펙트럼 백색성의 빈 수 `B` 값이 본문에 없음 — `(원문 미명시)`.
- 노이즈·프레임 텐서의 dtype/정규화 규약 미명시 — WM 백본(SVD VAE) 규약을 따른다고 가정으로 메움.
- $`\beta, \lambda_{1,2,3}`$ 의 튜닝 절차 미기술 ("tuned depending on the WM, noise dimension, and VLMs" 뿐) — 새 WM/VLM 조합에서는 재튜닝 필요, 절차는 잠정적으로 그럴듯함-정렬 트레이드오프 곡선 재작성으로 가정.
- Fig. 5 베이스라인 두 값(71% / 54%)의 막대-방법 대응이 PDF 텍스트 추출로 미확정 — §1 의 "(54%→94%)" 만 수치 앵커로 사용.
- Dubins 통제 실험은 전체 기울기를 사용한다고 명시(§C.1)되어 있으나 Table 3 에 $`\beta = 10.0`$ 이 기재됨 — 근사 미사용 시 $`\beta`$ 의 역할이 본문에서 모호.
- 자기회귀 롤아웃에서 세그먼트별 노이즈의 결합 최적화는 저자 스스로 미해결로 남김 (현재 구현은 순차 최적화).
- 조작 원격조작 파인튜닝 데이터·평가 세트의 공개 여부 미명시 — 재현 시 자체 수집 가정.
