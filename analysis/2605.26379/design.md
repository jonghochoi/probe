# Design — When Does LeJEPA Learn a World Model?

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
| 원문 제목 (영문) | When Does LeJEPA Learn a World Model? |
| 링크 | [arXiv:2605.26379](https://arxiv.org/abs/2605.26379) |
| 분석 문서 | [`analysis/2605.26379/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-10 |

> 주: 본 논문은 *이론(identifiability) 논문* 입니다. 산출물은 학습 알고리즘
> (LeJEPA 손실 + OU pair 생성 + SIGReg) 과 검증용 평가 절차가 명세의 핵심이며,
> 새로운 신경망 아키텍처 자체는 제안하지 않습니다(인코더는 임의 측도가능 사상).
> 따라서 "모듈 인터페이스"는 학습/평가 루프 수준의 계약으로 기술합니다.

---

## 🧮 데이터 계약

세계는 잠재 $`z\in\mathbb{R}^{n}`$ 를 비선형 $`g`$ 로 관측 $`x=g(z)`$ 으로 사상하고,
학습기는 $`y=f(x)`$ 로 되돌립니다. 분석 대상은 합성 $`h=f\circ g`$.

- **입력 (latent)** — `z`: shape `(B, n)`, float, `z ~ N(0, I_n)` (Gaussian world 가정). `n` = 참 잠재차원.
- **입력 (positive pair)** — `z_prime`: shape `(B, n)`, OU 전이 $`z'=\rho z+\sqrt{1-\rho^2}\,\eta`$, `eta ~ N(0, I_n)`, `eta ⊥ z`. `rho ∈ (0,1)`.
- **관측** — `x = g(z)`, `x_prime = g(z_prime)`: shape `(B, d_obs)` (2D 예제는 `d_obs=2`; pixel 예제 Reacher 는 `(B,3,64,64)`).
- **출력 (embedding)** — `y = f(x)`: shape `(B, m)`, float. 정리는 **`m = n`** 을 가정(차원 정합). whitening 으로 `Cov(f(x)) = I_m` 목표, `f(x) ~ N(0, I_m)` 목표.
- **정규화 가정** — embedding 은 표준 Gaussian target 으로 정규화(SIGReg). latent 는 표준정규(평균 0, 단위 공분산). 데이터는 online 합성(무한데이터, 매 step 새 샘플).

---

## 🧰 모듈 인터페이스

```python
def ou_positive_pair(z, rho):
    """z ~ N(0,I_n) 로부터 OU 전이로 positive pair z'를 생성.
    z' = rho*z + sqrt(1-rho^2)*eta,  eta~N(0,I_n), eta⊥z.  (Eq.1)"""

def alignment_loss(f_x, f_xprime):
    """정렬 손실: mean ||f(x) - f(x')||^2.  (Eq.2 Alignment 항)"""

def sigreg_loss(f_x):
    """SIGReg: embedding 경험분포를 표준 Gaussian 으로 미는 정규화.
    슬라이스된 경험적 특성함수 vs Gaussian target 의 편차를 벌점."""

def lejepa_loss(f_x, f_xprime, lam):
    """L = lam * L_SIG(f_x) + (1-lam) * L_inv(f_x, f_xprime).  (Eq.75)"""

def linear_identifiability_R2(h_z, z):
    """OLS 로 z->h, h->z 선형적합 후 양방향 R^2 반환(평가 전용)."""

def orthogonality_error(Qhat, n):
    """||Qhat^T Qhat - I_n||_F / sqrt(n)  (직교성 진단, 평가 전용)."""
```

- **`ou_positive_pair`** — world 의 전이를 구현. `rho` 가 두 view 상관을 조절. 입력 `z (B,n)` → 출력 `z' (B,n)`.
- **`alignment_loss` / `sigreg_loss`** — LeJEPA 두 항. SIGReg 의 정확한 estimator 는 Balestriero & LeCun(LeJEPA, [7]) 의 sliced characteristic-function 페널티(원문은 "성공한 상황"만 모델링하므로 내부 식은 인용으로 위임).
- **`lejepa_loss`** — 두 항을 `lam ∈ [0,1]` 으로 결합. 옵티마이저는 이 스칼라를 최소화.
- **평가 모듈(`linear_identifiability_R2`, `orthogonality_error`)** — 학습에 들어가지 않음. 고정 평가셋(1만 점)에서 $`h=f\circ g`$ 의 복원 품질을 측정하는 *진단* 계약.

---

## ⛓️ 불변식·가정

- **(가정 1) 차원 정합** — 인코더 출력차원 = 참 잠재차원 ($`m=n`$). $`m\neq n`$ 이면 선형 identifiability 보장 무효(§7 한계).
- **(가정 2) Gaussian 잠재** — $`z\sim\mathcal{N}(0,I_n)`$. converse(Thm 5.2): 이 world 클래스에서 선형 identifiability 를 주는 *유일* 분포. score 함수 $`(\log p)'`$ 가 선형이어야 함.
- **(가정 3) 정상·가법잡음·독립 전이** — 전이는 OU 채널(Eq.1), 정상성 + 가법잡음 + Gaussian 의 유일 해. 성분별 독립.
- **(불변식) 등호조건** — $`\mathbb{E}[h_i(z')h_i(z)]=w_1\rho+w_2\rho^2+\cdots\leq\rho`$, 등호 ⟺ $`h_i`$ 선형(Eq.4). 분산비 $`\sum_d w_d^{(i)}=1`$.
- **(불변식) 최적해 직교성** — 최적에서 $`h(z)=Qz`$ 이고 Gaussianity 가 $`QQ^\top=I_n`$ 강제(직교/반사).
- **(불변식) 근사 안정성** — 복원오차 $`\leq(\varepsilon+\tfrac{\delta}{2\rho(1-\rho)})^2+\tfrac{\delta}{2\rho(1-\rho)}`$ (Eq.52); $`\delta=\varepsilon=0`$ 에서 Thm 5.1 회복.
- **(planning 불변식) 좌표 일관성** — $`h(z)=Qz`$ 이면 회전불변 비용·LQR gain 이 $`\hat{a}_t=-\hat{K}\hat{z}_t=-Kz_t`$ 로 참 world 와 동일(Thm 5.4). 단, 전이모델·비용이 학습 좌표에서 *상호 일관*하게 명세될 때.

---

## 📊 하이퍼파라미터·손실

- 손실 식: $`\mathcal{L}=\lambda\,\mathcal{L}_{\mathrm{SIG}}+(1-\lambda)\,\mathcal{L}_{\mathrm{inv}}`$, with $`\mathcal{L}_{\mathrm{inv}}=\tfrac{1}{B}\sum_i\|f(x_i)-f(x_i')\|^2`$.
- 정렬-상관 등가식: $`\mathcal{L}(h)=2n-2\sum_i\mathbb{E}[h_i(z')h_i(z)]`$ (whitening 하).

| 이름 | 값 | 출처 |
|------|----|----|
| `lambda` (정규화 가중) | best `1e-3` ~ `5e-3`; sweep `{1e-6,1e-5,1e-4,1e-3,5e-3,1e-2,5e-2,1e-1,5e-1}` | §H.6 |
| `rho` (OU 상관) | best `0.9`~`0.95`; sweep `{0.3,0.5,0.7,0.8,0.9,0.95,0.99}` | §H.6 |
| collapse 임계 | `lambda=0.5` → collapse ($`R^2\approx0`$); `lambda<1e-4` → identifiability 부족 | §H.6 |
| 인코더 | 4-layer MLP, hidden `256`, GELU (2D/scaling); CNN (Reacher pixel) | §H.2 |
| `n` (latent dim) sweep | `{2^1, …, 2^10}` (RealNVP mixing + matched encoder) | §6.1 |
| LR 스케줄 | 전반부 constant → 후반부 cosine decay to 0 | §H.4 |
| 평가셋 크기 | 고정 `10,000` 점 | §H.5 |
| 잠재분포 sweep | generalized normal `alpha ∈ {2^-3,…,2^5}` (`alpha=2` Gaussian) | §H.7 |
| 옵티마이저 / batch `B` / epochs | (원문에 명시 없음 — 가정으로 메움; online 무한데이터 regime 만 명시) | §H.4 |

---

## 🎯 평가 메트릭

- **지표** — `Linear R^2 (bidirectional)`: OLS 로 $`\hat z=Az+b`$, $`\hat h=Bh+c`$ 적합 후 $`R^2(z\to h)`$, $`R^2(h\to z)`$ · **임계값** — `R^2 → 1` 이면 선형 identifiability 성립(scaling 에서 SIGReg/VICReg `>0.999` @ N=1024) · **비교 baseline** — SIGReg vs VICReg vs InfoNCE.
- **지표** — `Orthogonality error` $`\|\hat Q^\top\hat Q-I_n\|_F/\sqrt{n}`$ · **임계값** — `→0` 이면 직교(Thm 5.1 일치; best `≈0.15`).
- **지표** — `근사 bound 양`: 공분산편차 $`\varepsilon=\|\mathrm{Cov}(h(z))-I\|_F`$, 정렬갭 $`\delta`$(≥0 clamp), 직교복원오차 $`\min_{Q\in O(n)}\mathbb{E}[\|h(z)-Qz\|^2]`$(SVD) · **임계값** — 실측오차 ≤ 이론 bound(Fig.4a 대각선 아래).
- **지표** — `Control cost` (planning): $`K=30`$ start-goal pair, path length `≥1`(ideal `1`) · **임계값** — Gaussian 인코더는 oracle 과 통계적으로 구분 불가 · **비교 baseline** — oracle(joint-space 직선) vs Trajectory 인코더.
- **실무 corollary** — training loss 가 identifiability 의 신뢰 proxy(§H.9).

---

## ✨ 변경 의도 (intent)

기존 JEPA/SSL identifiability 연구는 표현을 매끄러운 diffeomorphism 으로 제약하거나(비선형 ICA 계열) 분포를 명시하지 않았다. 본 설계의 의도는 **embedding 분포를 명시적 isotropic Gaussian(SIGReg)으로 고정**함으로써, 임의의 측도가능 인코더에 대해 "정렬 손실 최소화 = 선형(직교) 복원"을 *유일 최적해*로 만드는 것이다. Hermite 스펙트럼 분해가 비선형 성분을 $`\rho^d`$ 로 벌점하는 것이 핵심 기제이며, 고전 ICA 와 정반대로 *Gaussian* 이 identifiability 를 *가능케 하는* 유일 분포가 된다. 결과적으로 학습 latent 가 참 world 의 직교 재좌표가 되어, 그 위 planning/probing 이 수정 없이 전이된다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 직접적 base family 없음. LeJEPA 는 VLA action policy(pi0/pi05/act/diffusion)가 아니라 *표현학습(SSL/JEPA) objective* 라, lerobot 의 정책 family 와는 결이 다름. 가장 가까운 접점은 *인코더 사전학습 보조손실*로서 SIGReg+OU-pair alignment 를 비전 백본 위에 얹는 형태이나, lerobot 에 JEPA/SIGReg 모듈이 없으므로 신규 손실/데이터로더 추가가 필요(매핑 가능성 낮음 — `/implement-design` 이 판정).

---

## 🚧 미해결 / 잠정

- **SIGReg 내부 estimator** — 원문은 "SIGReg 가 성공한 상황"만 모델링하고 구체식은 LeJEPA 원논문([7])에 위임. sliced characteristic-function 페널티의 정확한 형태·슬라이스 수는 본문 미명시 — 구현 시 [7] 참조 필요.
- **옵티마이저·batch·step 수** — online 무한데이터 regime 만 명시, 구체 옵티마이저/배치/총 step 은 원문 미명시(가정으로 메움).
- **`m≠n` 동작** — 차원 불일치 시 거동은 open problem 으로 남김(superposition / redundancy). Layer 1 스펙으로 굳히지 못함.
- **action-conditioned 전이** — 본 논문은 인코더(상태)만 보장. 전이모델 $`\hat p(\hat z'\mid\hat z,a)`$ identifiability 는 persistent-excitation 조건 하 진행 중 연구로, 본 Design 범위 밖.
- **비-OU/비정상 dynamics** — 접촉이 많은 실제 조작 dynamics 로의 일반화는 Thm 5.3 graceful degradation 외에는 미명세.
