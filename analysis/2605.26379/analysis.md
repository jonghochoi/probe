# Paper Analysis — When Does LeJEPA Learn a World Model?

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | When Does LeJEPA Learn a World Model? |
| 저자 | David Klindt, Yann LeCun, Randall Balestriero |
| 링크 | [arXiv:2605.26379](https://arxiv.org/abs/2605.26379) · [GitHub](https://github.com/klindtlab/lejepa-identifiability) |
| 발행일 / 버전 | 2026-05-25 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-10 |
| 관련 Pillar | P5, P4 |
| 태그 | flow-matching |

<!-- 본문은 arXiv HTML 파이프라인으로 전문 확보. 태그는 통제 어휘
     (vla-arch/forgetting/peft/tactile/force/egocentric-data/dexterity/
     flow-matching/optimizer/continual/sim2real/dataset) 중 이 이론
     논문에 정직하게 맞는 것이 거의 없어, JEPA latent-prediction(WM 표현학습)
     계열에 가장 근접한 보조 표지로 flow-matching 1개만 부착. 정확히 맞는
     world-model/ssl 태그가 어휘에 없음 — §💡 컨텍스트 제안에 어휘 확장 제안. -->

---

## 🧭 한 줄 요약 (TL;DR)

LeJEPA(정렬 손실 + isotropic-Gaussian 정규화 SIGReg)는 비선형 관측에서 세계의 잠재변수를 **선형으로 복원(linear identifiability)** 하며, 정상·가법잡음 전이를 갖는 광범위한 world 클래스 안에서 **이 보장이 성립하는 유일한 잠재분포는 Gaussian** 임을 증명한다. 즉 "JEPA 표현이 언제 World Model 이 되는가"라는 질문에 *잠재변수의 선형 복원이 곧 World Model* 이라는 수학적 기준을 제시한다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 자기지도학습(SSL)으로 얻은 표현이 *언제* 세계의 잠재 구조를 충실히 담은 World Model 이 되는가? 저자들은 그 기준을 "표현이 세계의 잠재변수를 **선형으로** 복원하는 순간"으로 못 박는다.
- **기존 접근의 한계** — JEPA 계열에는 identifiability(복원 보장) 결과가 전무했다. 기존 방법은 암묵적 collapse 방지(stop-gradient teacher, 공분산 정규화 등)에 의존해 embedding 분포가 명시되지 않았고, 비선형 ICA 는 추가 구조 없이는 원천적으로 불가능(unidentifiable)하기 때문이다.
- **본 논문의 가설** — collapse 를 *명시적* Gaussian 정규화(SIGReg)로 막는 LeJEPA 라면, 정렬 손실과 결합해 표현이 잠재변수의 선형(직교) 함수로 강제되고, 그 보장은 잠재분포가 Gaussian 일 때만(필요충분) 성립한다.
- **왜 지금 중요한가** — World Model 을 VLA·로봇 제어에 접합하려면 "표현이 진짜 세계 상태인가"를 보장해야 planning·linear probing 이 의미를 갖는다. 본 논문은 경험적으로 성공한 LeJEPA 레시피를 *증명*으로 승격시켜 World Model 설계의 이론적 토대를 제공한다.

---

## 🧩 핵심 기여

- **JEPA 최초의 identifiability 정리** — LeJEPA 가 Gaussian world 에서 잠재변수를 회전/반사 단위로 선형 복원함을 증명(Thm 5.1, forward).
- **Gaussian 유일성(converse)** — §3.1 의 world 클래스(독립·정상·가법잡음) 안에서 linear identifiability 를 주는 잠재분포는 **Gaussian 이 유일**함을 증명(Thm 5.2). 고전 ICA 의 "Gaussian 에서만 분리가 실패한다"는 서사를 **정확히 뒤집는다**.
- **근사 identifiability** — 두 목적함수가 정확히 만족되지 않아도 복원 오차가 정렬 갭 $`\delta`$ 와 whitening 오차 $`\varepsilon`$ 에 대해 연속적으로(graceful) 열화함을 정량 bound 로 제시(Thm 5.3).
- **최적 latent planning** — 직교 identifiability 가 성립하면 학습 latent 에서 짠 계획이 *참* world 에서 짠 계획과 수학적으로 동일(같은 action·같은 value)함을 증명(Thm 5.4).
- **Lean 4 형식 검증** — 다섯 정리 전부를 Lean 4 + Mathlib 으로 `sorry` 0 으로 기계 검증(일부 표준 보조정리는 axiom 으로 인용).
- **2D~1024차원 실험** — Gaussian 최적성, 분포 sweep, 근사 bound, pixel 기반 로봇 제어(DMC Reacher) planning 까지 이론을 경험적으로 검증.

---

## 🔑 기술 키워드

- **JEPA (Joint-Embedding Predictive Architecture)** — 픽셀이 아닌 *표현 공간*에서 예측하도록 학습하는 SSL 구조. 동일 콘텐츠의 두 view 가 비슷한 embedding 을 갖도록 끌어당기되 collapse 를 막는다.
- **LeJEPA** — collapse 를 isotropic Gaussian 정규화(SIGReg)로 *명시적*으로 막는 JEPA 변종. 본 논문이 이론적으로 분석하는 대상 "Learner".
- **SIGReg (Sketched Isotropic Gaussian Regularization)** — embedding 분포를 표준 Gaussian 으로 밀어붙이는 정규화. 슬라이스된 경험적 특성함수를 Gaussian target 과 비교해 벌점.
- **Linear identifiability** — 학습 표현이 참 잠재변수를 단순 대칭(회전 등)을 제외하고 선형으로 복원한다는 보장. linear probing 이 잠재변수를 정확히 읽어낼 *필요* 조건.
- **OU (Ornstein–Uhlenbeck) transition** — Gaussian 주변분포를 보존하는 유일한 가법잡음 전이 $`z'=\rho z+\sqrt{1-\rho^2}\,\eta`$. positive pair 를 만드는 world 의 전이 모델.
- **Hermite polynomials** — Gaussian 변수 함수의 자연 직교기저(Fourier 모드의 Gaussian 판). 표현을 선형/이차/삼차 … 성분으로 분해해 비선형도를 측정.
- **Transition operator / spectral decomposition** — 전이 $`z\to z'`$ 가 함수에 작용하는 선형 연산자 $`T`$. 고유함수 $`\varphi_k`$ 와 고유값 $`\lambda_k`$ 가 "두 view 에서 가장 예측 가능한 특징"을 정렬한다.
- **Whitening** — $`\mathrm{Cov}(h(z))=I_n`$ 으로 embedding 을 무상관·단위분산화. 거리 최소화를 상관 최대화와 등가로 만드는 제약.
- **Slow feature analysis (SFA)** — 시간적으로 가장 천천히 변하는(가장 자기상관 높은) 특징을 뽑는 고전 기법. JEPA 목적이 경험적으로 SFA 를 복원한다는 연결고리.

---

## 🔬 방법론

### 직관

질문은 단순합니다. "관측은 세계의 그림자일 뿐(플라톤의 동굴)"인데, 우리가 학습한 표현 $`h=f\circ g`$ 가 *언제* 그림자 뒤의 진짜 잠재변수 $`z`$ 를 되살리는가? 저자들의 답은 "표현이 $`z`$ 의 **선형 함수**일 때, 즉 $`h(z)=Qz`$ ($`Q`$ 는 회전/반사) 일 때"입니다. 완벽 복원은 isotropic Gaussian 의 회전 대칭 때문에 불가능하므로, 회전 단위까지의 선형 복원이 현실적으로 바랄 수 있는 최선이며 이것이 linear probing 이 동작할 필요조건입니다.

핵심 메커니즘은 "정렬(alignment) 손실이 비선형성을 벌점한다"는 것입니다. World 가 두 view $`(z,z')`$ 를 $`\rho`$ 만큼 상관된 Gaussian 으로 내놓을 때, 표현이 비선형이면 두 view 간 상관이 *반드시* 떨어집니다. Hermite 분해로 보면 $`d`$ 차 비선형 성분은 전이를 통과하며 상관이 $`\rho^d`$ 로 감쇠하고, $`\rho<1`$ 이므로 고차 성분은 더 심하게 깎입니다. 따라서 상관을 최대화(=정렬 손실 최소화)하려면 표현은 1차(선형) 성분에 전 분산을 몰아야 하며, 그 결과 $`h(z)=Qz`$ 가 유일한 최적해가 됩니다.

여기서 Gaussian 이 *왜* 특별한지가 converse 입니다. 일반 잠재분포에서도 전이 연산자의 가장 느린 고유함수는 항상 단조(monotonic)라 단조변환 단위의 identifiability 는 줍니다. 하지만 그 고유함수가 **affine(선형)** 이려면 잠재분포의 score 함수 $`(\log p)'`$ 가 선형이어야 하고, 그 조건을 만족하는 분포는 Gaussian 뿐입니다. 즉 "선형 복원"이라는 목표 자체가 Gaussian 을 유일하게 선택합니다.

마지막으로 이것이 로봇·제어에 갖는 의미는 planning 입니다. $`h(z)=Qz`$ 이면 학습 latent 는 참 latent 의 직교 재좌표일 뿐이므로, 회전불변 비용으로 짠 계획(예: 직선 goal-reaching, LQR)은 참 world 의 계획과 같은 action·같은 value 를 냅니다. 표현이 World Model 이 되는 순간, 그 위의 planner 가 "공짜로" 따라온다는 것이 4번째 정리입니다.

### 아키텍처 — World 와 Learner

![Figure 1 — LeJEPA가 World Model을 학습한다](https://arxiv.org/html/2605.26379/figures/fig_lejepa_demo.jpg)

> "Figure 1: LeJEPA learns the World Model. (left) The world has independent Gaussian latent variables . (center) An unknown nonlinear process scrambles them into the data we observe. (right) LeJEPA recovers the latent variables up to rotation. We prove this is the unique optimum." (§1)
(왼쪽 독립 Gaussian 잠재변수 → 가운데 비선형 mixing 으로 entangle 된 관측 → 오른쪽 LeJEPA 가 회전 단위로 복원하는 전체 구도를 시각화합니다.)

**World (생성 과정).** 세계는 잠재변수 $`z\in\mathbb{R}^n`$ (위치·속도·색·조명 등 자유도)를 갖고, 미지의 비선형 과정 $`g`$ 가 관측 $`x=g(z)`$ 를 만듭니다. 우리는 $`z`$ 를 직접 보지 못합니다. World 클래스는 세 가정으로 정의됩니다 — (a) **독립** 잠재변수, (b) view 간 생성과정 불변(**정상성**), (c) **가법잡음** 전이.

> "We never observe $`z`$ directly. Instead, an unknown process $`g`$ generates the data we see: $`x=g(z)`$ ." (§3)
(관측은 잠재변수 $`z`$ 의 비선형 사상 $`g`$ 를 거친 "그림자"이며, 표현 $`f`$ 의 목표는 $`g`$ 를 되돌리는 것입니다.)

**Gaussian World (§3.1.1).** 위 틀 안에서 잠재분포를 $`z\sim\mathcal{N}(0,I_n)`$ 로 특정합니다(주어진 평균·공분산의 최대엔트로피 분포; 중심극한정리로 task 잠재변수는 Gaussian 으로 수렴하는 경향). 정상성 + 가법잡음 + Gaussian 은 전이를 **OU 채널**로 유일하게 강제합니다 (식 1):

$$z^{\prime}=\rho\,z+\sqrt{1-\rho^{2}}\,\eta$$

여기서 $`\eta\sim\mathcal{N}(0,I_n)`$ 는 $`z`$ 와 독립인 가법잡음($`\eta\perp z`$)이고, $`\rho\in(0,1)`$ 가 두 view 의 상관을 조절하며, $`\mathbb{E}[z']=0`$, $`\mathrm{Var}(z')=I_n`$, $`\mathrm{Cov}(z,z')=\rho I_n`$ 임을 확인할 수 있습니다. Gaussian 은 이런 채널이 주변분포를 보존하는 유일한 분포입니다(컨볼루션의 고정점).

**Learner (§3.2).** 표현은 합성사상 $`h=f\circ g:\mathbb{R}^n\to\mathbb{R}^n`$ 으로 특징지어지며, LeJEPA 는 두 항으로 학습됩니다 — positive pair 를 끌어당기는 **정렬(alignment)** 손실과, embedding 분포를 Gaussian 으로 만들어 collapse 를 막는 **Gaussianity(SIGReg)** 정규화 (식 2):

$$\min_{h}\mathcal{L}(h)=\underbrace{\mathbb{E}\!\left[\|h(z^{\prime})-h(z)\|^{2}\right]}_{\textbf{Alignment}}\qquad\text{s.t.}\qquad\underbrace{h(z)\sim\mathcal{N}(0,I_{n})}_{\textbf{Gaussianity}}$$

이 논문은 SIGReg 가 *성공한* 상황($`h(z)`$ 가 target Gaussian 과 일치)을 모델링하며, $`h`$ 에 대해서는 측도가능성(measurability) 외에는 아무것도 요구하지 않습니다 — 따라서 결과는 출력차원이 $`n`$ 인 임의의 신경망에 적용됩니다. whitening 으로 $`\mathbb{E}[\|h(z)\|^2]=n`$ 이 고정되어, 거리 최소화는 상관 최대화와 등가가 됩니다 (식 3):

$$\mathcal{L}(h)=2n-2\sum_{i=1}^{n}\mathbb{E}\!\left[h_{i}(z^{\prime})\,h_{i}(z)\right]$$

> "minimizing distance is equivalent to maximizing correlation between the two views." (§3.2)
(질문이 "측도보존 $`h`$ 중 positive pair 상관을 가장 높이는 것은 무엇인가"로 환원됩니다 — 답이 선형입니다.)

### 학습 목표 / 손실 — 스펙트럼 분석과 forward 정리

**전이 연산자와 Hermite 기저(§4).** 전이 $`z\to z'`$ 는 함수에 작용하는 선형 연산자 $`(Th_i)(z)=\mathbb{E}[h_i(z')\mid z]`$ 를 유도하며, 고유함수 $`\varphi_k`$ 와 고유값 $`1=\lambda_0>\lambda_1\geq\cdots\geq 0`$ 을 갖습니다. Gaussian world 에서 고유함수는 **Hermite 다항식** $`\{\mathrm{He}_k\}`$ 로 닫힌 형태이고, $`d`$ 차 Hermite 의 고유값은 정확히 $`\rho^d`$ 입니다(Mehler 공식).

> "any nonlinear distortion of the representation strictly reduces the correlation between positive pairs ." (§4)
(임의의 함수 $`h_i`$ 를 선형/이차/삼차 … 성분으로 분해하고 각 분산비를 $`w_1,w_2,\ldots`$ 라 하면, 비선형 성분은 상관을 *엄격히* 깎습니다.)

핵심 부등식(spectral bound, 식 4):

$$\mathbb{E}\!\left[h_{i}(z^{\prime})\,h_{i}(z)\right]=w_{1}\cdot\rho+w_{2}\cdot\rho^{2}+w_{3}\cdot\rho^{3}+\cdots\;\leq\;\rho$$

등호는 $`w_1=1`$ (즉 $`h_i`$ 가 선형)일 때만 성립합니다. $`\sum_d w_d=1`$ 이고 $`\rho^d\leq\rho`$ 이므로 가중평균이 $`\rho`$ 를 넘지 못한다는 단순한 논증입니다.

**forward 정리(Thm 5.1).** 식 (3)을 통해 손실 최소화는 $`\sum_i\mathbb{E}[h_i(z')h_i(z)]`$ 최대화와 등가이고, 식 (4)에 의해 각 항이 $`\leq\rho`$, 등호는 선형일 때뿐입니다. 등호에서 $`h(z)=Qz`$ ($`Q`$ 는 단위노름 행; Gaussianity 가 $`QQ^\top=I_n`$ 을 강제해 직교)가 되고, 전이는 직접 대입으로 $`h(z')=\rho\,h(z)+\sqrt{1-\rho^2}\,Q\eta`$ 가 되어 $`Q\eta\sim\mathcal{N}(0,I_n)`$ 으로 보존됩니다.

> "Any representation satisfying the two LeJEPA objectives must recover a rotation/reflection of the true latent variables and the true transition dynamics." (§5.1)
(잔여 모호성은 isotropic Gaussian 에 내재한 전역 회전뿐이며, 표현은 "World Model 전체를 학습할 수밖에 없습니다".)

증명의 엔진은 Hermite 생성함수로 얻는 noise 작용입니다 (식 21):

$$\mathbb{E}_{\eta}\!\left[\mathrm{He}_{k}(z^{\prime})\right]=\rho^{k}\,\mathrm{He}_{k}(z)$$

App. E 에는 Dirichlet energy + Mazur–Ulam 정리를 쓰는 대안 증명($`\rho\to 1`$ regime)도 제시됩니다.

### 학습 목표 / 손실 — converse·근사·planning

**converse(Thm 5.2): Gaussian 유일성.** forward 는 $`\mathrm{Cov}(h(z))=I_n`$ (whitening) 만 썼습니다. 그렇다면 흰(white) 분포면 아무거나 되는가? 아닙니다. 가법잡음 하에서 Sturm–Liouville 이론은 고유함수를 점점 진동하는 순서로 정렬하고, 첫 고유함수는 항상 단조라 *단조변환 단위* identifiability 만 줍니다.

> "Demanding an affine eigenfunction forces the score function $`(\log p)^{\prime}`$ of the latent distribution to be linear." (§5.2)
(선형 identifiability 는 이 고유함수가 affine 이길 요구하고, 그것은 score 함수를 선형으로 강제하는데, 선형 ODE 를 풀면 다음이 나옵니다 (식 33).)

$$\log p(z_{i})=-\frac{\lambda}{2K}\left(z_{i}+\frac{b}{a}\right)^{2}+C$$

즉 $`\log p`$ 가 이차식 → **Gaussian**. 성분별 논증이며 잠재변수 독립성이 결론을 결합분포로 들어올립니다.

**근사 identifiability(Thm 5.3).** 실제로는 두 목적이 근사적으로만 만족됩니다. 정렬 갭 $`\delta`$ 와 whitening 오차 $`\varepsilon`$ 에 대해 복원 오차가 연속적으로 열화합니다 (식 52):

$$\mathbb{E}[\|h(z)-Qz\|^{2}]\;\leq\;\left(\varepsilon+\frac{\delta}{2\rho(1-\rho)}\right)^{\!2}+\frac{\delta}{2\rho(1-\rho)}$$

> "In practice the first dominates, so recovery error scales as $`\delta/2\rho(1-\rho)`$ : alignment is hard, whitening essentially free." (§5.3)
(두 항이 모두 $`\delta=\varepsilon=0`$ 에서 사라져 Thm 5.1 을 회복하며, 실무에서는 정렬 항이 지배적입니다 — whitening 은 사실상 공짜.)

**최적 latent planning(Thm 5.4).** 직교 identifiability 가 planning 에 무엇을 사주는가:

> "trajectories planned in the learned latent are mathematically identical to trajectories planned in the true world, with the same actions and the same value." (§5.4)
(LQR 의 경우 학습 latent 의 최적 gain $`\hat{K}`$ 에 대해 $`\hat{a}_t=-\hat{K}\hat{z}_t=-Kz_t`$ 가 되어, 회전불변 비용은 참 world 와 학습 latent 사이를 *수정 없이* 전이합니다.)

### 학습 셋업

- **인코더** — 4-layer MLP, hidden 256, GELU (2D/scaling 실험). pixel 실험(Reacher)은 CNN 인코더.
- **mixing $`g`$** — norm-dependent rotation(spiral), sinusoidal shear, parabolic shear, RealNVP coupling layer(전부 diffeomorphism). scaling 실험은 RealNVP mixing + matched RealNVP 인코더(실패가 표현력이 아닌 최적화 탓이도록).
- **positive pair** — 식 (1)의 OU 전이로 online 생성(매 step 새 샘플, 무한데이터 regime).
- **손실** — $`\mathcal{L}=\lambda\,\mathcal{L}_{\mathrm{SIG}}+(1-\lambda)\,\mathcal{L}_{\mathrm{inv}}`$, $`\mathcal{L}_{\mathrm{inv}}=\frac{1}{B}\sum_i\|f(x_i)-f(x_i')\|^2`$.
- **스케줄** — 전반부 constant LR → 후반부 cosine decay to zero. 평가는 고정 1만 점에서 $`h=f\circ g`$ 의 양방향 linear $`R^2`$, 직교오차 $`\|\hat{Q}^\top\hat{Q}-I\|_F/\sqrt{n}`$, 근사 bound 양($`\varepsilon,\delta`$).

---

## 📊 실험 설정과 결과

네 정리에 1:1 대응하는 검증입니다 — 6.1 forward, 6.2 converse, 6.3 근사 bound, 6.4 planning.

![Figure 3 — 2D 시뮬레이션](https://arxiv.org/html/2605.26379/x1.png)

> "Figure 3: 2D Simulations. Points colored by the polar angle and radius of the ground-truth latent variables $`z\sim\mathcal{N}(0,I_{2})`$ (like Fig. 1 ). Observations ( a-c left) $`x=g(z)`$ after nonlinear mixing: parabolic shear, sinusoidal shear, RealNVP coupling layer. Learned embeddings ( a-c right): LeJEPA recovers the isotropic Gaussian structure up to rotation, consistent with Thm. 5.1 ." (§6.1)
(네 가지 비선형 mixing 모두에 대해 LeJEPA 가 회전 단위로 isotropic Gaussian 구조를 되살림을 색지도로 보여줍니다.)

**6.1 — forward / scaling (Table 1).** 잠재차원을 $`N\in\{2^1,\ldots,2^{10}\}`$ 으로 sweep, 세 Gaussian-강제 목적(SIGReg, VICReg, InfoNCE)을 같은 setup 에서 비교.

| $`N`$ | $`R^2(x\to z)`$ (mixing) | SIGReg | VICReg | InfoNCE |
|---|---|---|---|---|
| 2 | 0.781 | 0.999998 | 0.999996 | 0.950961 |
| 64 | 0.737 | 0.999966 | 0.999968 | 0.648496 |
| 128 | 0.739 | 0.999938 | 0.999942 | 0.566955 |
| 1024 | 0.763 | 0.999561 | 0.999582 | 0.720241 |

> "SIGReg and VICReg maintain $`R^{2}>0.999`$ up to $`N{=}1024`$ ; InfoNCE matches at low $`N`$ but degrades at scale under fixed kernel width $`\sigma{=}1`$ ." (§6.1, Table 1)
(mixing 자체는 강하게 비선형($`R^2(x\to z)\approx 0.73`$)인데도 batch-statistic 추정기(SIGReg/VICReg)는 1024차원까지 거의 완벽 복원; pair-based InfoNCE 는 고정 kernel 폭에서 규모가 커지면 무너집니다 — Thm 5.1 의 이상적 지점에서 벗어날 때만 방법 간 격차가 드러남.)

**6.2 — converse (Fig 4b, Table 2).** 잠재분포를 generalized normal 족($`\alpha\to 0`$ heavy-tail, $`\alpha=1`$ Laplace, $`\alpha=2`$ Gaussian, $`\alpha\to\infty`$ uniform)으로 sweep 하면 선형 복원이 $`\alpha=2`$ 에서 *날카롭게* 정점을 찍습니다(세 목적 모두). 또 DMC Reacher(2D 관절각 $`z=(\theta_0,\theta_1)`$, MuJoCo 64×64 렌더링)에서 두 조건을 비교:

| 조건 | $`\rho`$ / stride | 총 $`R^2(h\to z)`$ | 비고 |
|---|---|---|---|
| OU (Gaussian) | $`\rho=0.99`$ | **0.95** | 두 관절 선형 복원 |
| Trajectory (RL policy) | $`\delta=8`$ | $`<0.5`$ (이방성) | 비-Gaussian· $`\rho_0\neq\rho_1`$ ·관절한계 wrapping |

> "Table 2 (left) shows that OU pairs attain $`R^{2}=0.95`$ at $`\rho=0.99`$ , with the two joint dimensions linearly recovered. In contrast, real trajectories break the Gaussian assumption ... total $`R^{2}`$ never exceeds $`0.5`$ , consistent with Thm. 5.2 ." (§6.2, Table 2)
(*같은 물리계·같은 렌더링 파이프라인*인데 isotropic(OU) 샘플링은 identifiability 를 주고, goal-directed RL 정책 trajectory 는 주변분포가 저엔트로피 영역으로 collapse 해 깨집니다 — 데이터 분포가 이론의 가정을 만족하느냐가 결정적.)

![Figure 4 — 실험 결과 종합](https://arxiv.org/html/2605.26379/x2.png)

> "Figure 4: Experimental Results. a) Bound Verification. ... b) Gaussian Optimality. Linear recovery, $`R^{2}(h\to z`$ ), peaks at Gaussian, illustrating Thm. 5.2 . ... (c) Control cost ... The Gaussian encoder is statistically indistinguishable from the oracle; the Trajectory encoder is biased upward. (d) Control cost decreases with linear identifiability $`R^{2}`$ ..." (§6)
(a 근사 bound 가 대각선 아래(성립), b Gaussian 최적성, c/d planning 비용이 identifiability 와 단조 연동됨을 한 장에 모읍니다.)

**6.3 — 근사 bound (Fig 4a).** 각 run 에서 $`\varepsilon=\|\mathrm{Cov}(h(z))-I\|_F`$, 정렬 갭 $`\delta`$, bound $`D+(\varepsilon+D)^2`$, 실제 복원오차 $`\min_{Q\in O(n)}\mathbb{E}[\|h(z)-Qz\|^2]`$ 를 계산. grid search·2D·scaling·분포 sweep 전반에서 bound 가 성립하며, **training loss 가 identifiability 의 신뢰할 만한 proxy** 라는 실무적 따름정리를 얻습니다(소수의 위반은 유한표본 추정잡음과 일치).

**6.4 — planning (Fig 4c,d; Fig 5).** goal-reaching 에서 latent 직선 $`\hat{z}_0\to\hat{z}^*`$ 가 비용최소 경로입니다. $`h(z)\approx Qz`$ 인 인코더는 latent 직선이 참 latent 의 *거의 직선* 으로 decode 되지만, 그렇지 않으면 같은 계획이 굽은 경로를 만듭니다.

![Figure 5 — Latent 공간 planning](https://arxiv.org/html/2605.26379/x3.png)

> "Figure 5: Linear Identifiability Enables Latent-Space Planning. ... top) Oracle (joint-space straight line). middle) Gaussian encoder ($`\rho=0.99`$) tracks the oracle (overlaid) closely. bottom) RL trajectory encoder (stride $`\delta=8`$) deviates." (§6.4)
(Gaussian 인코더의 직선 latent 계획은 oracle 급 관절공간 궤적으로 decode 되고, Trajectory 인코더는 제어비용을 부풀립니다.)

> "Across all models, control cost tracks linear identifiability $`R^{2}`$ monotonically (right)." (§6.4)
(linear identifiability 가 "충실한 World Model 을 쓸모 있는 planner 로 바꾸는 구조적 성질"이라는 본 논문의 결론을 직접 뒷받침합니다.)

---

## ⚖️ 한계

- **차원 정합 가정 $`m=n`$ (저자 명시).** 정리는 인코더 출력차원이 참 잠재차원과 같다고 가정합니다. $`m<n`$ 이면 Gaussianity 제약이 어느 부분공간을 고를지 결정하지 못해 superposition 이 생기고, $`m>n`$ 이면 잉여 차원이 collapse 하거나 redundancy 를 인코딩해야 합니다. 실제 JEPA 는 임베딩 차원(예: DINOv3 768)이 알 수 없는 참 잠재차원과 거의 항상 불일치하므로, 이 가정은 *이론↔실무*의 가장 큰 간극입니다.
- **Gaussian 잠재 가정의 검증 불가능성(저자 명시).** 실세계 잠재변수가 Gaussian 인지는 관측만으로는 알 수 없습니다. 저자는 "최대엔트로피·중심극한정리"로 옹호하지만, 이는 고전 ICA 의 비-Gaussian 가정과 마찬가지로 *구조적 가정*이지 검증된 사실이 아닙니다. Reacher 의 RL trajectory 결과가 보여주듯 실데이터는 쉽게 이 가정을 깹니다.
- **population·전역최적 진술(저자 명시).** 결과는 표본무한·전역최적에서의 진술입니다. Thm 5.3 이 연속적 열화를 보이지만, 그것이 *표본 수*나 *학습 동역학*에 따라 어떻게 scale 하는지는 다루지 않습니다 — SGD 가 실제로 그 전역최적에 도달하는지는 별개 문제.
- **상태(state) 측만 다룸 — 전이는 미해결(추론된 갭).** 본 정리는 인코더가 잠재 *상태*를 복원함만 보장합니다. action-conditioned 전이 $`\hat{p}(\hat{z}'\mid\hat{z},a)`$ 는 여전히 데이터에서 학습해야 하며(App. D.2), 그 identifiability 는 "persistent excitation(행동이 모든 latent 방향을 탐색)"이라는 *다른* 조건을 요구하는 진행 중 연구입니다. VLA/로봇 World Model 의 핵심인 forward dynamics 보장은 이 논문 범위 밖.
- **단순 world 클래스(추론된 갭).** 독립·정상·가법잡음(OU)이라는 가정은 깔끔하지만, 접촉이 많은 손-물체 조작처럼 비정상·비가법·강한 종속을 갖는 실제 dynamics 와는 거리가 있습니다. Thm 5.3 의 graceful degradation 이 위안이지만, 가정이 *크게* 어긋날 때의 bound 는 느슨합니다.

---

## ♻️ 재현성

- **코드** — 공개. Lean 4 형식 증명 프로젝트가 [github.com/klindtlab/lejepa-identifiability](https://github.com/klindtlab/lejepa-identifiability) 에 있으며 Lean 4 v4.28.0 + Mathlib v4.28.0(8,032 build targets, 0 error, 0 `sorry`)로 컴파일됩니다.
- **증명 검증** — 다섯 결과(Thm 5.1 Hermite 증명, Thm 5.2 Gaussian 유일성, App. E Dirichlet 증명, Thm 5.3 근사 bound, Thm 5.4 planning)를 기계 검증. Hermite 다항식·Mazur–Ulam·균등가중 AM-GM 등 Mathlib 에 정확한 형태가 없는 표준 결과는 출처를 단 Lean axiom 으로 도입(축약 추론 사슬은 전부 검증).
- **실험** — mixing 함수·인코더 구조(4-layer MLP/256/GELU, RealNVP)·하이퍼(λ·ρ grid, gennorm α sweep)·평가지표가 App. H 에 상세 기술. 데이터는 online 합성(무한데이터). pixel 실험은 DMC Reacher(MuJoCo) + RL episode 10k.
- **하드웨어** — CSHL GPU cluster(NIH grant S10OD028632-01) 사용 명시.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P5(World Model) — 정면.** 본 논문은 P5 의 핵심 질문 "JEPA 표현이 언제 World Model 이 되는가"에 *수학적 기준*을 제공합니다. 특히 D30(prediction space — latent/JEPA 예측)의 v1 선택을 이론적으로 정당화하고, D28(world-model role — latent dynamics prior)의 전제(표현이 참 상태를 담아야 prior 가 유효)를 떠받칩니다. P5 의 pinned 문헌이 전부 *경험적* JEPA World Model 인 데 반해, 이건 그 토대 이론입니다.
- **P4(VLM 사전학습 보존/레시피) — 부차.** LeJEPA/SIGReg 는 본질적으로 SSL *사전학습* 목적이며, Discussion 은 "자기지도 사전학습에서는 isotropic random walk 에 가까운 exploration 이 이론이 다루는 regime 을 유지한다"고 명시 — 즉 *사전학습 데이터 수집 분포*에 대한 처방을 줍니다(P4 D22 corpus 구성과 직접 연결).
- **Identity 긴장/지지** — 우리 스택의 Identity 는 "World Model 은 후기단계(later-phase) 베팅"입니다. 이 논문은 그 베팅의 *전제조건*(표현 충실성)을 명료화하지만, action-conditioned 전이 보장은 미해결로 남겨 "지금 당장 도입" 근거는 되지 못합니다 — Identity 의 phasing 과 일치.
- **경쟁자 함의** — Yann LeCun(JEPA 진영) 의 이론적 정당화로, P5 §5 의 VLA-JEPA·JEPA-VLA·ThinkJEPA 같은 JEPA-계 경쟁자들이 *왜* 동작하는지를 설명합니다. raw-pixel 생성 World Model(Ctrl-World 등) 대비 latent-JEPA 노선에 이론적 무게를 실어줍니다.

---

## ✨ 핀 논문 대비 델타

P5 §5 의 핀 **VLA-JEPA(Sun et al., arXiv:2602.10098)** 와 비교하면 결정적으로 다릅니다. VLA-JEPA 는 JEPA latent World Model + 2-stage action head 를 *경험적으로* 제안하고 "leakage-free latent state prediction, camera/background shift 에 robust" 함을 보입니다. 본 논문은 **그 robustness·identifiability 가 언제 보장되는지의 정리**입니다 — "JEPA 가 동작한다"가 아니라 "JEPA(=LeJEPA)가 Gaussian latent·정상 OU 전이일 때 *유일하게* 선형 복원한다"는 필요충분 조건. 또 핀 ThinkJEPA/JEPA-VLA(V-JEPA2 기반)가 *비디오* 예측을 쓰는 것과 달리, 본 논문은 모달리티-불문의 추상 world 위에서 SIGReg 의 Gaussian 정규화가 갖는 *특수한* 역할(VICReg 2차모멘트·InfoNCE 와의 위계)을 분리해 보입니다. 한마디로 P5 의 모든 JEPA 핀이 "어떻게"라면, 이건 "언제·왜"입니다.

---

## ⚙️ 의사결정 함의

이 논문이 맞다면 P5 latent World Model 도입 시 다음이 바뀝니다.

- **정규화 선택 = SIGReg(full Gaussian) 우선.** D30 latent 예측에 collapse 방지 정규화를 붙일 때, VICReg(2차모멘트)·InfoNCE(pair-based) 대신 **SIGReg** 를 기본값으로. 근거: scaling 에서 SIGReg/VICReg 가 $`R^2>0.999`$ 유지하되 SIGReg 가 비-Gaussian latent 에 더 robust(더 넓은 plateau), InfoNCE 는 고정 kernel 폭 $`\sigma=1`$ 에서 고차원 붕괴.
- **사전학습 데이터 분포에 isotropy 제약.** P4 corpus 구성에서, World Model objective 를 co-train 한다면 *수집 분포가 isotropic random walk(OU)에 가깝도록* exploration/샘플링을 설계. Reacher 결과: 같은 물리계라도 goal-directed policy 데이터는 identifiability 를 $`R^2<0.5`$ 로 깸. → 데이터 수집 단계에 "isotropic exploration ratio" 같은 명시적 config 키 후보.
- **training loss 를 identifiability proxy 로 모니터링.** 별도 probe 없이 $`\mathcal{L}_{\mathrm{SIG}}+\mathcal{L}_{\mathrm{inv}}`$ 값과 whitening 오차 $`\varepsilon`$ ·정렬 갭 $`\delta`$ 를 로깅하면 "표현이 World Model 인가"를 대리 측정 가능(Thm 5.3 + App. H.9).
- **하이퍼 sweet spot.** 2D grid 기준 best 는 $`\lambda\in\{10^{-3},5\times10^{-3}\}`$, $`\rho\in\{0.9,0.95\}`$. $`\lambda`$ 가 너무 크면($`0.5`$) collapse, $`10^{-4}`$ 미만이면 Gaussianity 부족. → latent-WM 보조헤드의 정규화 가중치 초기값 가이드.

---

## ⚠️ 먼저 검증할 실패 모드

우리 손-중심 dexterous 스택으로 전이되지 않을 이유를, 싼 점검부터:

1. **(가장 쌈) 차원 불일치 $`m\neq n`$.** 우리 VLA 임베딩(수백~수천 차원)은 참 잠재차원과 절대 같지 않음. 이론의 $`m=n`$ 가정이 깨지므로 "선형 복원" 보장이 그대로 오지 않음. → 점검: 작은 toy(알려진 $`n`$)에서 $`m`$ 을 의도적으로 키워 $`R^2(h\to z)`$ 가 얼마나 떨어지는지 먼저 측정.
2. **데이터 분포가 OU 가 아님.** 우리 데이터는 goal-directed 시연(텔레오퍼레이션)이라 marginals 가 저엔트로피 영역으로 collapse — Reacher 의 Trajectory 조건과 *정확히* 같은 실패. isotropic exploration 데이터가 없으면 identifiability 가정 자체가 성립 안 함. → 점검: 기존 시연 데이터의 latent marginal Gaussianity(예: gennorm $`\alpha`$ 적합)와 autocorrelation $`\rho`$ 추정.
3. **접촉 dynamics 의 비가법·비정상성.** 손-물체 접촉은 충돌·마찰로 가법잡음·정상성 가정을 강하게 위반. OU 채널 가정 밖이라 spectral 논증의 Hermite 닫힘이 깨짐. → 점검: 단일 접촉 에피소드에서 transition 이 가법 Gaussian 으로 근사되는지 잔차 분석.
4. **상태만 보장, 전이는 미보장.** 우리가 원하는 것은 action-conditioned forward dynamics(D31)인데 이 논문은 인코더(상태)만 다룸. planning 보장(Thm 5.4)도 *전이모델이 별도로 학습되어 좌표 일관성을 유지*한다는 전제 위에서만 성립. → 점검: latent 인코더 freeze 후 별도 transition head 의 $`a`$-conditioned 예측오차가 좌표 회전에 불변인지.
5. **전역최적 도달 가정.** 정리는 전역최적의 진술이고 SGD 가 거기 도달한다는 보장은 없음. 우리의 큰 backbone·유한 데이터에서 정렬 갭 $`\delta`$ 가 충분히 작아지지 않으면 식 (52)의 bound 가 느슨해 복원 무의미. → 점검: 학습 종료 시 $`\delta,\varepsilon`$ 실측이 이론적 "유용" 범위에 드는지.

---

## 💡 컨텍스트 제안

- **P5 §5 methodology-base 추가 후보.** 본 논문(arXiv:2605.26379)을 P5 의 *non-pinned methodology base* 로 추가 제안 — JEPA latent-WM(D30) 노선 전체의 *이론적 토대*이자 SIGReg vs VICReg vs InfoNCE 정규화 선택의 근거. 핀 8개(hard cap)를 건드리지 않고 "Methodology base(non-pinned)" 표에 LeJEPA-identifiability 행으로. (사람 판단 필요; context 파일은 미수정.)
- **D30 rationale 보강.** D30(prediction space = latent/3D-flow)의 v1 선택에 "JEPA latent 예측은 Gaussian latent·isotropic exploration 조건에서 선형 identifiability 가 *증명*됨(2605.26379)"이라는 근거 한 줄을 deferred-rationale 후보로.
- **태그 어휘 확장 제안(STYLE §5-6).** 통제 태그 어휘에 `world-model`·`ssl`(또는 `jepa`) 후보 추가 검토 — 본 논문처럼 World Model/SSL 이론 papers 가 현 어휘(vla-arch…dataset)에 정직하게 맞지 않음. (docs/STYLE.md 는 미수정; 사람 결정.)
