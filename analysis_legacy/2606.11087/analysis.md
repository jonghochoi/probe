# Paper Analysis — Test-Time Gradient Guidance of Flow Policies in Reinforcement Learning

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Test-Time Gradient Guidance of Flow Policies in Reinforcement Learning |
| 저자 | Zhiyuan Zhou, Andy Peng, Charles Xu, Qiyang Li, Tobias Springenberg, Kevin Frans, Sergey Levine |
| 링크 | [arXiv:2606.11087](https://arxiv.org/abs/2606.11087) · [GitHub](https://github.com/zhouzypaul/qgf) |
| 발행일 / 버전 | 2026-06-09 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-10 |
| 관련 Pillar | P1, P4, P3 |
| 태그 | flow-matching, dexterity |

---

## 🧭 한 줄 요약 (TL;DR)

QGF(Q-Guided Flow)는 BC 로 학습한 **flow 정책의 가중치를 전혀 건드리지 않고**, 테스트 시점에 한 번의 큰 Euler 스텝으로 근사한 *denoised action* 에서 평가한 critic gradient 만으로 denoising 매 스텝을 high-value 방향으로 밀어주는 test-time RL 알고리즘입니다. actor-critic 공동 학습의 불안정성을 회피하면서도, 비싼 best-of-N 샘플링이나 BPTT guidance 보다 더 좋은 성능과 더 좋은 모델-크기 확장성을 보입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — diffusion/flow 같은 표현력 높은 연속 제어 정책은 BC(supervised) 환경에서는 안정적으로 스케일하지만, 이를 RL 파이프라인에 넣어 *정책 개선* 을 하려 하면 학습이 매우 어려워집니다. 본 논문은 "공급된 supervised 학습은 그대로 두고, **테스트 시점 연산만으로** 정책을 value 함수에 대해 최적화할 수 있는가?" 를 묻습니다.
- **기존 접근의 한계** — flow 정책을 RL 로 개선하려면 (i) 전용 학습 목표를 설계하거나 (ii) 긴 denoising 과정을 통째로 역전파(BPTT)해야 하는데, 둘 다 잘 알려진 불안정성과 확장성 저하를 일으킵니다. 가장 단순한 test-time 대안인 best-of-N(BFN) 샘플링은 고차원 action 공간에서 비용이 폭증합니다.
- **본 논문의 가설** — critic gradient 를 *noisy action* 에서 직접 쓰면 critic 이 학습된 적 없는 OOD 영역을 건드려 편향되고, 전체 ODE 를 역전파하면(BPTT) 분산이 커집니다. 대신 **단일 1차(Euler) 근사로 얻은 denoised action 에서 critic gradient 를 평가하면** 저분산·저비용이면서도 더 잘 최적화되리라는 것이 핵심 가설입니다.
- **왜 지금 중요한가** — action chunking(고차원 action) 기반 offline RL 이 기본 OGBench 데이터셋에서 이미 포화되고, 100M~1B 규모 대형 데이터셋과 대형 모델로 옮겨가는 추세에서, actor-critic 의 불안정성 없이 **모델 크기에 따라 안정적으로 좋아지는** 정책 추출법이 실용적 가치를 갖습니다.

---

## 🧩 핵심 기여

- **QGF gradient estimator (식 9)** — noisy action 에서의 critic gradient(OOD) 도, 전체 denoising 역전파(BPTT) 도 피하면서, 단일 큰 Euler 스텝으로 근사한 denoised action $`\hat{a}_1`$ 에서 critic gradient 를 평가하는 test-time guidance 추정량을 제안합니다.
- **두 개의 "거친 근사" 가 오히려 더 낫다는 분석** — (i) Jacobian $`J=\partial\hat{a}_1/\partial a_t`$ 을 항등행렬로 대체하고 (ii) denoised action 을 1차 근사하는 두 선택이 단순 타협이 아니라, 더 낮은 분산과 더 나은 *mode 선택* 으로 이어져 "정확한" 대응물(QGF-Jacobian, QGF-chain)을 능가함을 보입니다.
- **광범위한 offline RL 벤치마크 검증** — OGBench 의 single-task / goal-conditioned 설정 모두에서 기존 test-time RL(QFQL·BPTT·RobustQ·GradStep·CFGRL·BFN)을 능가하고, 강력한 train-time SOTA(FQL·EDP·QAM·DAC·QSM+BC)와 대등하거나 약간 우위임을 보입니다.
- **확장성과 critic-agnostic 성질** — 모델 크기 확장에서 train-time baseline(QAM)보다 훨씬 잘 확장(800k→3.2M 에서 약 4× 도약)되고, IQL critic 뿐 아니라 QAM 기반 bootstrapping critic 등 *다른 종류의 value 함수* 와도 동작하며 더 좋은 critic 일수록 더 좋아집니다.

---

## 🔑 기술 키워드

- **QGF (Q-Guided Flow)** — flow 정책의 denoising 매 스텝에 "한 발 앞서 본" denoised action 의 Q-gradient 를 더해 방향을 트는 test-time RL 알고리즘. 정책 가중치는 학습 후 고정.
- **Flow matching** — Gaussian noise 에서 데이터 분포로 가는 시간의존 velocity field $`v_\theta(x,t)`$ 를 ODE 로 적분해 샘플을 만드는 생성 모델. 본 논문의 reference 정책이 이 형태입니다.
- **Classifier guidance** — 생성 과정의 score 에 외부 분류기(여기서는 학습된 $`Q`$)의 gradient 를 더해 원하는 조건 쪽으로 샘플을 유도하는 기법. QGF 는 분류기 자리에 critic 을 끼운 변형입니다.
- **OOD gradient** — denoising 중간의 *noisy action* $`a_t`$ 에서 직접 계산한 $`\nabla_{a_t}Q(s,a_t)`$. critic 이 본 적 없는 영역이라 편향된 guidance 를 줍니다.
- **BPTT gradient** — noisy action 을 ODE 로 끝까지 denoise 한 뒤 그 전체 적분을 역전파해 얻는 $`\nabla_{a_t}Q(s,\mathrm{ODE}(a_t))`$. 원리상 정확하지만 비싸고 노이즈에 민감(고분산)합니다.
- **First-order (Euler) approximation** — 전체 denoising 대신 현재 velocity 를 따라 한 번에 $`\hat{a}_1=a_t+(1-t)v_\theta`$ 로 점프해 clean action 을 근사하는 것. QGF gradient 평가점입니다.
- **Implicit Q-Learning (IQL)** — 데이터셋 action 만으로 거의 최적 정책의 $`Q`$ 를 in-sample 로 학습(expectile 회귀)하는 offline RL 기법. 정책 샘플 없이 critic 을 학습해 value-학습과 policy-추출을 분리합니다.
- **Behavior-regularized RL** — offline 에서 OOD value exploit 을 막기 위해 정책을 behavior 정책 쪽으로 KL 정규화하는 목표. 그 closed-form 해가 QGF 유도의 출발점입니다.
- **Best-of-N (BFN) sampling** — 정책에서 $`N`$ 개 action 을 뽑아 critic 이 최고로 매기는 것을 고르는 test-time 추출법. 효과적이지만 denoising 을 $`N`$ 번 굴려 비쌉니다.
- **Action chunking** — 한 번에 길이 $`h`$ 의 action 시퀀스를 출력해 하나씩 실행하는 설정($`h=5`$). 고차원 action 분포라 정책-추출법 비교의 좋은 testbed 입니다.

---

## 🔬 방법론

### 직관

QGF 의 출발점은 "RL 정책 학습이 불안정한 이유는, 끊임없이 바뀌는 critic 을 최대화하도록 actor 를 *같이* 학습시키기 때문" 이라는 관찰입니다. 그래서 QGF 는 actor 를 표준 BC(flow matching)로만 학습해 고정해 두고, critic 도 따로 학습한 뒤, **둘을 학습 시점에 결합하지 않습니다.** 대신 추론할 때만, critic 의 gradient 로 BC 정책의 샘플링을 high-value 쪽으로 살짝 유도합니다. 이는 분류기 자리에 학습된 $`Q`$ 를 끼운 classifier guidance 와 같은 구조입니다.

문제는 flow 정책이 action 을 한 번에 만들지 않고 noise 에서 시작해 여러 denoising 스텝으로 만든다는 점입니다. 가장 단순하게는 중간의 *noisy action* 에서 $`Q`$ 의 gradient 를 쓰면 되지만, critic 은 깨끗한(denoised) action 에서만 학습됐으므로 그 영역의 gradient 는 신뢰할 수 없습니다(저자 표현 "OOD gradient"). 반대로 noisy action 을 ODE 로 끝까지 denoise 한 뒤 그 전 과정을 역전파(BPTT)하면 원리상 맞지만 비싸고 노이즈에 극도로 민감합니다.

QGF 의 핵심 트릭은 그 중간입니다. 현재 noisy action $`a_t`$ 에서 velocity 를 한 번만 따라가 "한 발 앞선" clean action 을 **단일 큰 Euler 스텝으로** $`\hat{a}_1=a_t+(1-t)v_\theta`$ 처럼 근사하고, 그 점에서 critic gradient 를 평가합니다. 이렇게 하면 critic 은 항상 (근사적으로) 깨끗한 action 에서 질의되어 OOD 를 피하고, 전체 ODE 를 역전파하지 않아 싸고 저분산입니다.

더 놀라운 부분은 두 개의 "거친 근사" 가 단순 타협이 아니라는 점입니다. denoised action 까지의 Jacobian 을 통째로 항등행렬로 버리고, 전체 denoising 대신 1차 근사만 써도, 오히려 "정확한" 버전들보다 성능이 좋습니다. 저자들은 이를 (i) 추정량의 분산이 더 낮고, (ii) 데이터셋 분포 전체를 정확히 따르도록 강제되지 않아 좋은 *mode 만 골라잡는* 능력 덕분이라고 설명합니다.

### 아키텍처

![Figure 1 — QGF 개요](https://arxiv.org/html/2606.11087/x1.png)

> "Figure 1: We propose QGF (Q-Guided Flow), an RL algorithm that guides denoising steps of a policy trained via flow matching with critic gradient at test time. Our critic gradient estimator avoids both taking gradient at noisy action not seen during training and performing expensive, high-variance backpropagation through time, and performs better than other test-time RL methods while being competitive with the best train-time baseline." (§1)
> (한글 해설 — denoising 매 스텝에서 reference velocity 에 critic gradient 를 가중합해 action 을 high-value 방향으로 밀어주는 전체 구조를 한 장으로 보여줍니다.)

구성 요소는 셋입니다.

- **Reference flow 정책 $`\hat{\pi}(a\mid s)`$** — state 로 조건화된 velocity field $`v_\theta(s,a,t)`$. 표준 flow matching(식 2)으로만 학습되고 추론 중에는 고정됩니다.
- **Critic $`Q(s,a)`$** — IQL 로 in-sample 학습. value-학습과 policy-추출을 완전히 분리하기 위해 in-sample 알고리즘을 일부러 선택했습니다. QGF 알고리즘 자체는 reference 정책·critic 의 *학습 방식에 불가지론적(agnostic)* 입니다.
- **Guidance 결합** — denoising 적분 시 reference velocity 에 critic gradient 항을 가중치 $`1/\beta`$ 로 더합니다.

행동-정규화(KL) RL 목표(식 1)의 closed-form 해가 유도의 토대입니다.

> "It is well-known in the literature that the solution to this optimization problem is given via the closed form:" (§4)
> (한글 해설 — 개선된 정책이 reference 정책에 $`\exp(Q)^{1/\beta}`$ 를 곱한 형태라는, guidance 정당화의 출발 식입니다.)

$$\pi(a\mid s)\propto\hat{\pi}(a\mid s)\cdot\exp(Q(s,a))^{1/\beta}$$

이를 score 형태로 옮기면(식 4), 개선 정책의 score 는 reference score 에 $`Q`$ gradient 를 더한 것이 됩니다.

$$\nabla_{a}\log\pi(a\mid s)=\nabla_{a}\log\hat{\pi}(a\mid s)+1/\beta\cdot\nabla_{a}Q(s,a)$$

선행연구를 따라 이를 중간 denoising 스텝의 noisy action $`a_t`$ 로 확장합니다(식 5).

$$\nabla_{a_{t}}\log\pi(a_{t}\mid s)\approx\nabla_{a_{t}}\log\hat{\pi}(a_{t}\mid s)+1/\beta\cdot\nabla_{a_{t}}Q(s,a_{t})$$

여기서 guidance 항 $`\nabla_{a_t}Q(s,a_t)`$ 가 바로 문제의 "OOD gradient" 입니다.

> "This gradient can be unreliable since the critic $`Q(s,a)`$ is only trained on the denoised action space and querying it at out-of-distribution noisy actions may require the gradient of the Q-function to be correct far from its training data, which is not generally guaranteed." (§4)
> (한글 해설 — critic 이 깨끗한 action 에서만 학습됐으므로 noisy action 에서의 gradient 는 보장되지 않고, $`a_t`$ 자체가 유효한 action 이 아닐 수도 있습니다.)

원칙적 대안은 noisy action 의 $`Q`$ 를 그 denoised 버전의 $`Q`$ 로 정의(식 6)하고 그 gradient(BPTT)를 쓰는 것입니다.

$$Q(s,a_{t}):=Q(s,\text{ODE}(a_{t}))$$

하지만 이 BPTT gradient 는 비싸고, 작은 섭동 $`a_t+\epsilon`$ 에 대해 gradient 방향이 크게 흔들리는 고분산 추정량입니다(Fig. 3).

![Figure 2 — 1D tri-modal 예시](https://arxiv.org/html/2606.11087/x2.png)

> "Figure 2: Illustrative example of 1D denoising process mapping Gaussian noise to a tri-modal distribution, with $`Q`$ defined as negative L2 distance to the optimal action $`a^{*}`$. We compare the base BC flow and three critic-gradient guidance methods (BPTT, OOD, QGF) across three guidance weights. While BPTT and QGF converge to $`a^{*}`$, guidance with the OOD gradient $`\nabla_{a_{t}}Q(s,a_{t})`$ does not result in the optimal solution. Further, Fig. 14 shows BPTT can be highly unstable." (§4)
> (한글 해설 — OOD gradient 는 guidance 가중치를 아무리 키워도 잘못된 mode 로 편향되고, BPTT 는 수렴은 하나 불안정함을 1D didactic 예시로 시각화합니다.)

### 학습 목표 / 손실 (그리고 QGF 추정량 유도)

reference 정책은 표준 flow matching 손실(식 2)로만 학습합니다.

$$\mathcal{L}_{\mathrm{FM}}(\theta)=\mathbb{E}_{t\sim\mathcal{U}[0,1],\,x_{0}\sim p_{0},\,x_{1}\sim p_{1}}\left[\left\|v_{\theta}(x_{t},t)-(x_{1}-x_{0})\right\|^{2}_{2}\right]$$

critic 은 IQL 로 학습합니다 — $`Q`$ 는 TD 타깃 $`r+\gamma V_\psi(s')`$ 에 회귀하고, $`V_\psi`$ 는 expectile 회귀로 $`Q`$ 의 상위 expectile($`\tau=0.9`$)에 맞춥니다.

핵심은 **test-time gradient 추정량** 입니다. 전체 ODE 를 풀지 않고, 단일 큰 Euler 스텝으로 denoised action 을 근사합니다(식 7).

> "we can obtain a cheap, first-order approximation to the ODE solution by taking a single large Euler integration step, following the local velocity field at action $`a_{t}`$ all the way to a denoised action" (§5)
> (한글 해설 — 현재 시점 $`t`$ 의 velocity 를 그대로 $`(1-t)`$ 만큼 따라가 한 번에 clean action 으로 점프하는, 가장 싼 1차 근사입니다.)

$$\hat{a}_{1}=a_{t}+v_{\theta}(s,a_{t},t)\cdot(1-t)$$

그러면 ground-truth gradient 를 chain rule 로 근사할 수 있고(식 8), 이는 $`Q`$ gradient 와 denoised→noisy Jacobian 의 곱입니다 — 이를 **QGF-Jacobian** 추정량이라 부릅니다.

$$\nabla_{a_{t}}Q(s,a_{1})\approx\nabla_{a_{t}}Q(s,\hat{a}_{1})=\left(\frac{\partial\hat{a}_{1}}{\partial a_{t}}\right)^{\top}\nabla_{\hat{a}_{1}}Q(s,\hat{a}_{1})$$

그런데 Jacobian $`J=\partial\hat{a}_1/\partial a_t`$ 은 $`v_\theta`$ 를 미분해야 해서 ill-behaved 하기 쉽습니다. 이를 **항등행렬로 통째로 대체**($`J\approx\hat{J}:=I`$)하면 성능이 더 좋아집니다 — 이것이 **QGF** 추정량(식 9)입니다.

$$\nabla_{a_{t}}Q(s,a_{1})\approx\hat{J}^{\top}\,\nabla_{\hat{a}_{1}}Q(s,\hat{a}_{1})\quad\text{where}\quad \hat{a}_{1}=a_{t}+v_{\theta}(s,a_{t},t)\cdot(1-t),\ \hat{J}=I$$

> "Empirically, we find that $`J`$ can be ill-behaved since it requires differentiating through $`v_{\theta}(s,a_{t},t)`$, and replacing it with the identity entirely ($`J\approx\hat{J}:=I`$) yields better performance" (§5)
> (한글 해설 — Jacobian 을 포함하면 노이즈 민감도가 커져 "$`Q`$-optimizer" 로서 더 나빠지므로, 버리는 쪽이 저분산·고성능입니다 — Fig. 3·4 가 이를 뒷받침합니다.)

1차 근사 자체도 단순 편의가 아닙니다. 전체 denoising chain($`a_1=\mathrm{ODE}(a_t)`$, "QGF-chain")보다 1차 근사가 더 좋은 이유를 mode 선택으로 설명합니다.

> "We hypothesize this is due to QGF being better at mode selection: following the full denoising process of the base BC flow restricts the denoised action to cover the full dataset distribution, while QGF allows deviation from the exact dataset distribution and allows the flow to choose only certain modes of the dataset distribution." (§5)
> (한글 해설 — 전체 denoising 은 정책을 데이터셋 분포 전체에 묶지만, 1차 근사는 거기서 벗어나 좋은 mode 만 고르도록 허용해, BC 정책을 더 나은 action 으로 유도합니다.)

**Algorithm 1 (QGF 추론)** — 입력: state $`s`$, reference flow $`v_\theta`$, critic $`Q`$, guidance 가중치 $`1/\beta`$, 스텝 $`\delta=1/T`$.

1. $`a_0\sim\mathcal{N}(0,I)`$ 초기화.
2. $`t=0,\delta,2\delta,\dots,1-\delta`$ 에 대해 반복:
   - (1차 근사 denoise) $`\hat{a}_1\leftarrow a_t+(1-t)\,v_\theta(s,a_t,t)`$
   - (QGF gradient 추정) $`g\leftarrow\nabla_{\hat{a}_1}Q(s,\hat{a}_1)`$
   - (Q guidance 적분) $`a_{t+\delta}\leftarrow a_t+\delta\cdot\big(v_\theta(s,a_t,t)+\tfrac{1}{\beta}\,g\big)`$
3. $`a_1`$ 반환.

### 학습 셋업

- **벤치마크** — OGBench 의 7개 환경(각 5 task): `scene`, `puzzle-4x4`(p44), `puzzle-4x5`(p45), `puzzle-4x6`(p46), `cube-triple`(c3), `cube-quadruple`(c4), `cube-octuple`(c8). offline RL 설정.
- **action chunking** — chunk 크기 $`h=5`$. 정책이 길이 $`h`$ action 시퀀스를 출력해 하나씩 실행 → 고차원 action 분포.
- **데이터셋 규모** — 기본 OGBench(1M~3M transition)는 action chunking offline RL 에서 이미 포화되므로 **100M transition** 데이터셋 사용. p46·c8 은 stress test 로 **1B transition** 도, p45·p46 은 sparse-reward 설정도 추가.
- **공통 하이퍼파라미터(Table 1)** — batch 1024, discount $`\gamma=0.999`$, IQL expectile $`\tau=0.9`$, flow steps 10, offline 학습 $`5\times10^5`$ 스텝, lr 3e-4, critic/actor 망 `[1024,1024,1024,1024]`, critic ensemble 2(`min` 집계).
- **guidance 가중치 $`\tau_g`$(=$`1/\beta`$)** — 도메인별로 튜닝, 탐색 범위 `{0.004, 0.008, 0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.12}`(Table 3·5).

---

## 📊 실험 설정과 결과

본 논문의 정량 결과는 모두 **막대그래프(Figure)** 로 보고되며 본문에 수치 표는 없습니다(Table 1~5 는 하이퍼파라미터 표). 따라서 아래는 그림 캡션과 본문이 명시한 정성/배수 주장만 인용합니다.

| 실험 (Figure) | 설정 | 핵심 결과 (본문/캡션 표현 그대로) |
|---|---|---|
| Fig. 5 — single-task offline RL | 20 tasks, 10 seeds, 500k steps | QGF 가 모든 test-time 방법을 능가, 최고 train-time 방법과 대등 |
| Fig. 6/7 — test-time compute 확장 | BFN 계열 비교 | BFN 은 QGF/GradStep 대비 FLOPs 가 orders of magnitude 큼; QGF+BFN(N=4)이 BFN(N=16) 매칭 |
| Fig. 8 — goal-conditioned RL | 25 tasks, 10 seeds, 1M steps | 가장 쉬운 task 는 baseline 에 뒤지나, 어려운 task 에서 일관 최고 |
| Fig. 9 — 모델 크기 확장 | c3 5 tasks, vs QAM | 800k→3.2M 에서 QGF 약 4× 도약, QAM 정체 |
| Fig. 10 — critic 종류 | 20 tasks, 4 seeds | QAM 기반 critic + QGF 가 IQL 기반 QGF·QAM bootstrapping 모두 상회 |

> "Figure 5: Offline RL performance at $`500`$k training steps (20 tasks, 10 seeds): QGF beats all previous test-time methods and is competitive with the best training-time method." (§6.3)
> (한글 해설 — QGF 가 gradient 기반(QFQL·BPTT·RobustQ)·CFGRL·GradStep 등 test-time 군을 확실히 앞서고, train-time SOTA 와 대등함을 보이는 메인 결과입니다.)

![Figure 5 — single-task offline RL 성능](https://arxiv.org/html/2606.11087/x5.png)

> "QGF also outperforms QGF-Jacobian, showing that not using the Jacobian in the gradient estimator improves performance, which is also confirmed later in Fig. 9 on harder OGBench tasks." (§6.3)
> (한글 해설 — Jacobian 을 버린 식 9 가 포함한 식 8(QGF-Jacobian)보다 낫다는 핵심 ablation 으로, 어려운 task 일수록 격차가 더 커집니다.)

**gradient estimator 분산 분석(Fig. 3·4).** Fig. 3 는 각 추정량 $`G`$ 에 대해 $`\cos(G(s,a_t),G(s,a_t+\epsilon))`$ 를 측정 — 1 에 가까울수록 노이즈에 둔감합니다.

> "Figure 3: Sensitivity of different gradient estimators to noise in the action space: ... Our proposed gradient estimator has the least variance and least sensitivity to noise. Averaged over $`20`$ tasks and $`4`$ seeds." (§4)
> (한글 해설 — QGF 가 OOD·BPTT·QGF-Jacobian·QGF-chain 중 가장 저분산이며, 이 저분산이 더 나은 $`Q`$-최적화(Fig. 4)·성능으로 이어진다는 인과 연결의 핵심 증거입니다.)

![Figure 3 — gradient estimator 노이즈 민감도](https://arxiv.org/html/2606.11087/x3.png)

**test-time compute 확장(Fig. 7).** QGF+BFN 변형은 QGF 에서 $`N`$ action 을 뽑아 critic 으로 최고를 고릅니다.

> "while BFN (N=4) alone uses drastically more test-time compute than QGF, it actually performs worse, indicating that QGF is a more effective value maximizer on its own. With even more test-time compute, BFN (N=16) catches up ... However, when given more compute, QGF+BFN is able to beat QGF, and match BFN (N=16) with a smaller test-time compute budget, only requiring $`4`$ samples instead of $`16`$." (§6.3)
> (한글 해설 — QGF 단독이 BFN(N=4)보다 적은 연산으로 더 좋고, QGF+BFN(N=4)이 BFN(N=16)을 매칭 — gradient guidance 가 단순 샘플링보다 연산 효율적임을 보입니다.)

**모델 크기 확장(Fig. 9).**

> "when scaling the model size from 800k parameters to 3.2M parameters, QAM does not improve while QGF experiences a nearly $`4\times`$ jump in performance. When we increase the model size past a certain threshold (e.g., 12.7M parameters), both methods experience overfitting, though QGF suffers less while QAM results in a policy that is unable to complete the task." (§6.4)
> (한글 해설 — actor 를 진화하는 critic 에 맞춰 학습하지 않으므로 QGF 가 모델 크기 확장에서 안정적 — train-time QAM 은 같은 확장에서 이득이 없습니다.)

**critic 종류(Fig. 10).**

> "QGF using the QAM-based $`Q`$ function performs much better than IQL-based QGF, and also performs better than QAM with $`Q`$ bootstrapping." (§6.5)
> (한글 해설 — QGF 가 critic 학습 방식에 불가지론적이며, 더 좋은 critic 을 주면 그대로 더 좋아지는 plug-in 정책-추출법임을 보입니다.)

**goal-conditioned 확장(Fig. 8).** 가장 긴 horizon 의 어려운 task 5종에서 BPTT·QFQL 대비 평가. 가장 쉬운 p45 에서는 QFQL 에 뒤지지만, 어려워질수록 일관되게 최고이며, 이때 critic 은 DQC(Decoupled Q-Chunking)로 학습한 IQL value 를 사용합니다.

---

## ⚖️ 한계

- **대형 critic 의 gradient 비용(저자 명시)** — QGF 는 critic gradient 를 denoising 매 스텝마다 평가합니다. critic 이 대형 모델이면 gradient 계산 자체가 비싸져, best-of-N 대비의 연산 우위가 줄어들 수 있습니다. denoising step 수($`T`$, 본 실험 10)에 비례해 critic backward 가 늘어나는 구조라, 큰 백본에선 inference latency 가 실질 병목이 됩니다.
- **reference 정책 품질 의존(저자 명시)** — QGF 는 base BC 모델의 출력을 *조정* 할 뿐이라, base 가 under-trained 이거나 데이터 분포를 잘 못 담으면 test-time 개선 여지가 작습니다. 즉 데이터 커버리지가 나쁜 영역은 guidance 로도 구제되지 않습니다.
- **Jacobian/1차 근사의 이론적 근거 부재(추론된 갭)** — "Jacobian 을 항등으로 버리고 1차 근사가 더 낫다" 는 발견은 강력하지만 본질적으로 경험적입니다. 저자도 근사 gradient 가 종종 충분하다는 선행연구를 인용할 뿐, *언제 무너지는지* 의 경계 조건은 제시하지 않습니다. mode 선택이 유리하게 작동하는 분포 형태와 그렇지 않은 형태의 구분이 불명확합니다.
- **guidance 가중치 $`\tau_g`$ 의 민감도(추론된 갭)** — Fig. 20 은 $`\tau_g`$ 를 키우면 성능이 급격히 좋아지다가, 과도하면 action 을 manifold 밖으로 밀어 다시 나빠진다고 명시합니다. 본 실험은 도메인별로 $`\tau_g`$ 를 튜닝했는데(Table 3), 이 튜닝이 환경마다 다르다는 점은 "train-time 하이퍼 튜닝을 없앴다" 는 강점을 부분적으로 상쇄합니다 — 튜닝 부담이 학습→추론으로 옮겨갔을 뿐입니다.
- **OOD gradient exploit 의 평가 함정(추론된 갭)** — Appendix D 에 따르면 OOD gradient 는 critic 을 OOD action 에서 exploit 해 *더 높은 $`Q`$ 값* 을 만들지만 실제 성능은 나쁩니다. 즉 "$`Q`$-optimizer 로서의 우수성" 과 "실제 성공률" 의 상관은 OOD 영역에서 깨집니다 — QGF 의 우수성 근거인 Fig. 4($`Q`$-value)도 이 단서를 조심해서 읽어야 합니다.

---

## ♻️ 재현성

- **코드** — 공식 구현 공개: [github.com/zhouzypaul/qgf](https://github.com/zhouzypaul/qgf).
- **데이터** — OGBench(공개 벤치마크)의 100M·1B transition 데이터셋 사용. single-task / goal-conditioned 설정 모두 OGBench 표준.
- **하이퍼파라미터** — Table 1~5 에 공통/도메인별 하이퍼파라미터와 baseline 튜닝 범위가 상세히 명시(batch· $`\gamma`$ ·expectile·flow steps·망 크기· $`\tau_g`$ 탐색 범위 등).
- **하드웨어** — 본문/부록에서 학습 하드웨어 사양은 확인되지 않았습니다(원문 미명시). seed 수(10/4)와 step 수(500k/1M)는 명시.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P1(이종 Body/Hand action expert) — 직접 관련.** QGF 의 reference 정책은 state-조건 flow matching velocity field 에 action chunking($`h=5`$)을 얹은 형태로, PROBE 의 Body/Hand action expert 가 채택할 flow-matching 디코더(D7: π0 action expert slice + FT)와 동일 계열입니다. QGF 는 그 디코더를 재학습하지 않고 *추출 단계만* 바꾸는 plug-in 이라, action-expert 아키텍처 결정을 건드리지 않으면서 goal-directed 행동을 얻는 도구가 될 수 있습니다.
- **P4(데이터 효율 적응을 위한 사전학습) — 철학적 지지.** QGF 의 핵심 주장은 "안정적 supervised(BC) 정책 학습을 그대로 둔다(leaving stable supervised policy training intact)" 입니다. 이는 D20(prior-preservation strategy)의 극단형입니다 — 가중치를 **전혀** 갱신하지 않으므로 forgetting 이 구조적으로 0 입니다. 즉 QGF 는 "test-time guidance = zero-forgetting 적응" 이라는 한 점을 P4 의 preservation 스펙트럼에 추가합니다.
- **P3(System0 RL) — 긴장 + 부분 지지.** Identity 의 Antagonist B 는 "RL-as-core 는 generalized dexterity 의 해답이 아니다(generalized task 는 reward-engineerable 하지 않다)" 이고, PROBE 는 RL 을 System0 contact-stabilization 으로만 한정합니다(D13–D18). QGF 는 *primary* flow 정책에 RL 개선을 가하는 방법이라 이 한정과 표면적으로 충돌합니다. 그러나 QGF 는 actor-critic 공동 학습을 *하지 않는* test-time 방식이라, "RL 의 불안정성을 stack 에 들이지 않으면서 value 신호를 쓰는" 제3의 경로를 제시합니다 — 다만 reward/critic 이 필요하다는 전제는 여전해, reward-engineerable 하지 않은 generalized task 에는 그대로 적용되지 않습니다.
- **경쟁자/Tracked Literature 함의** — P3 의 pinned 인 HORA/Beyond Binary 류는 actor-critic PPO 계열이고, QGF 는 그와 다른 "value-guided test-time 추출" 패러다임이라 직접 경쟁이라기보다 *대안 축* 입니다. P1 의 backbone π0(flow-matching action expert)와는 디코더를 공유하므로 결합 가능성이 높습니다.

---

## ✨ 핀 논문 대비 델타

- **π0([arXiv:2410.24164], P1 pin) 대비** — π0 는 flow-matching action expert 를 *학습* 하는 backbone 이고, QGF 는 그렇게 학습된 flow 정책을 **재학습 없이 추론 시 개선** 하는 직교적 레이어입니다. π0 가 만든 정책 위에 critic 만 추가로 붙이면 QGF 를 얹을 수 있어, 둘은 경쟁이 아니라 합성 관계입니다.
- **Dexora / Demystifying Action Space([arXiv:2602.23408], P1) 대비** — 이들은 action-space/디코더 *설계* 의 경험 증거를 제공하지만 RL 정책 개선은 다루지 않습니다. QGF 는 같은 action-chunking·고차원 action 설정을 공유하면서 "추출법" 축에서 새롭습니다.
- **P3 pin(HORA·Beyond Binary·VE2VF) 대비** — 이들은 contact-stabilization 을 actor-critic RL(PPO)·teacher-student distill 로 푸는 *train-time* 방법입니다. QGF 는 critic gradient 를 test-time guidance 로만 쓰는 새 패러다임으로, "정책을 critic 에 맞춰 학습시키지 않는다" 는 점이 진정한 델타입니다.

---

## ⚙️ 의사결정 함의

- **새 추출-단계 옵션 추가.** Body/Hand flow action expert(D7) 위에 IQL critic 을 별도 학습해 두면, 추론 시 Algorithm 1 의 한 줄 — velocity 에 $`\tfrac{1}{\beta}\nabla_{\hat{a}_1}Q(s,\hat{a}_1)`$ 를 가산 — 만으로 goal-directed action 추출을 켤 수 있습니다. 바뀌는 구체 항목: 추론 루프에 `guidance_weight`($`\tau_g=1/\beta`$, 후보값 `{0.004…0.12}`)와 1차 근사 denoise 점 $`\hat{a}_1=a_t+(1-t)v_\theta`$ 평가가 추가됩니다.
- **forgetting 메트릭 관점의 baseline.** D20(prior-preservation) 평가에서 QGF 는 "가중치 갱신 0" 의 상한 reference 로 쓸 수 있습니다 — 어떤 PEFT/적응이 QGF 의 zero-update 대비 얼마나 prior 를 잃는지를 측정하는 기준점.
- **denoising step 수 trade-off.** flow steps(본 논문 10)는 QGF 에서 critic backward 횟수를 직접 결정합니다. PROBE 가 π0 류를 쓸 때 inference step 수를 줄이면 QGF 비용도 비례해 줄지만, 1차 근사의 품질과 trade-off 가 생깁니다 — `num_flow_steps` 를 latency 예산과 함께 튜닝 대상으로 둬야 합니다.
- **critic-agnostic 이므로 value 설계는 분리 결정.** QGF 는 IQL·QAM-bootstrapping 등 어떤 critic 과도 동작하고 더 좋은 critic 일수록 좋아지므로, "어떤 critic 을 학습하나" 는 QGF 도입과 독립적으로 결정할 수 있습니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 check) reward/critic 자체가 없는 task.** QGF 는 학습된 $`Q`$ 를 *반드시* 요구합니다. PROBE 의 generalized dexterity task 는 reward-engineerable 하지 않다는 것이 Identity 전제이므로, critic 을 학습할 신호가 없으면 QGF 는 적용 불가합니다. → 먼저 "이 task 에 in-sample 학습 가능한 critic 이 있나?" 부터 확인.
- **OGBench(저차원 상태) ↔ 고차원 시각/촉각 관측 간극.** 본 실험은 proprioceptive state 기반 OGBench 입니다. PROBE 의 critic 은 multi-cam + per-finger tactile(P2) 위에서 학습돼야 하는데, 이런 고차원·OOD 빈발 관측에서 critic gradient 의 신뢰도와 저분산이 유지될지 미검증입니다. → 작은 실제 데이터로 $`\nabla_{\hat{a}_1}Q`$ 의 노이즈 민감도(Fig. 3 방식)부터 재현.
- **action chunking 차원 ↔ 손가락 고DOF action.** 본 논문 $`h=5`$ 의 고차원성은 OGBench manipulation 기준입니다. Sharpa 22-DOF hand 의 chunk 는 차원이 훨씬 커, 1차 Euler 근사 $`\hat{a}_1`$ 의 품질이 떨어지고 critic landscape 가 더 비볼록해질 위험이 있습니다. → 단순 in-hand cube 회전 데이터에서 QGF 의 $`Q`$-value 향상이 실제 성공률과 상관하는지 확인(Appendix D 의 OOD exploit 함정 주의).
- **$`\tau_g`$ 도메인 튜닝 비용.** 환경별 $`\tau_g`$ 가 필요(Table 3)하다는 점은, PROBE 의 다양한 task 마다 재튜닝을 요구할 수 있습니다. → 하나의 task 군에서 $`\tau_g`$ 민감도 곡선(Fig. 20)을 그려 "공통값으로 충분한가" 를 먼저 본다.
- **critic gradient latency.** π0 급 대형 백본을 critic 으로 쓰면 매 denoising step 의 backward 가 실시간 제어 주기를 깰 수 있습니다. → 추론 step 수 × critic backward 시간을 측정해 제어 주파수 예산 안에 드는지부터 확인.

---

## 💡 컨텍스트 제안

- **P1 §5 methodology base 후보(약한 제안).** QGF 는 P1 의 flow-matching action expert(π0)와 직접 합성 가능한 "test-time value-guided 추출" 레이어로, 핀 교체까지는 아니어도 P1 의 non-pinned methodology base 에 한 줄 추가를 고려할 만합니다(action-expert 재학습 없이 RL 개선을 얹는 직교 레이어).
- **P4 D20 reference point(약한 제안).** prior-preservation 평가의 "가중치 갱신 0" 상한 reference 로 QGF 를 명시해 두면, PEFT/적응 기법의 forgetting 을 재는 기준점이 생깁니다.
- 그 외 핀 교체·Decision 이동 트리거 변경 제안은 **없음** (QGF 는 RL-as-core 한정(P3)·heterogeneous decoder 결정(P1 D1–D7)을 바꿀 근거를 제공하지 않습니다).

---
