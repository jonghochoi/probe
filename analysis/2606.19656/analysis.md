# Paper Analysis — DF-ExpEnse: Diffusion Filtered Exploration for Sample Efficient Finetuning

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | DF-ExpEnse: Diffusion Filtered Exploration for Sample Efficient Finetuning |
| 저자 | Calvin Luo, Chen Sun, Shuran Song (Brown University · Stanford University REALab) |
| 링크 | [arXiv:2606.19656](https://arxiv.org/abs/2606.19656) · [Website](https://df-expense.github.io) |
| 발행일 / 버전 | 2026-06-17 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-30 |
| 관련 Pillar | P3, P4, P1 |
| 태그 | flow-matching, vla-arch, forgetting |

---

## 🧭 한 줄 요약 (TL;DR)

사전학습된 diffusion/flow policy 를 RL 로 finetuning 할 때, diffusion 의 multimodal 샘플 집합을 "탐색할 가치가 있는 후보 공간"으로 보고 critic ensemble 의 min-value UCB 로 탐색 관심도를 매겨 실행 행동을 고르는 **online 탐색(action selection) 기법** DF-ExpEnse 를 제안합니다. 여기에 초기 사전학습 정책 샘플을 후보에 섞는 **BC-SR** 와 fleet 전체 통계로 관심도를 정규화하는 **fleet normalization** 을 더해, 추가 모듈 없이 critic ensemble 만 재활용하면서 finetuning sample-efficiency 를 일관되게 끌어올립니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 사전학습된 generative control policy(diffusion policy)를 self-collected online 경험으로 RL finetuning 할 때, **online 경험 수집의 질**이 sample efficiency 를 좌우합니다. 어떻게 하면 더 적은 환경 상호작용으로 정책을 개선할 수 있는가가 핵심입니다.
- **기존 접근의 한계** — UCB·ensemble 기반 탐색은 모든 행동을 일일이 평가·랭킹해야 해 **이산 행동 공간**에서만 tractable 합니다. 로봇 제어의 **연속 행동 공간**에서는 모든 행동을 망라적으로 평가하는 것이 불가능합니다.
- **본 논문의 가설** — diffusion policy 의 **multimodal 모델링 능력**이 연속 행동 공간을 "기본 품질을 만족하면서 공간을 넓게 커버하는, 열거 평가 가능한 소수의 후보 집합"으로 자연스럽게 필터링해 준다면, 그 후보 위에서 UCB 식 탐색을 다시 적용할 수 있습니다.
- **왜 지금 중요한가** — (1) diffusion policy 가 offline 시연을 강한 behavior prior 로 바꿔 RL finetuning 의 출발점이 되었고, (2) 시뮬레이터 병렬화·실세계 로봇 fleet 이 online 수집을 대규모로 확장하면서, 양(quantity)뿐 아니라 **집단 협력으로 질(quality)을 높이는** 탐색 전략이 처음으로 현실적 레버가 되었습니다.
- **부수 동기 — 협력적 탐색** — fleet 의 각 에이전트가 독립적으로 추론하면 서로 비슷하거나 중복된 데이터를 동시에 모읍니다. 실시간 cross-fleet 통신으로 집단 차원의 다양·고품질 경험 수집을 유도할 여지가 있습니다.

---

## 🧩 핵심 기여

- **DF-ExpEnse (탐색 기법)** — diffusion policy 샘플 집합을 후보 공간으로 필터링하고, critic ensemble 의 min-value + α·std (min-value UCB) 로 각 후보의 **탐색 관심도(exploration interest)** 를 매겨 최대 관심 행동을 실행하는 online action-selection 기법. 기존 RL finetuning 위에 seamless 하게 얹힙니다.
- **BC-SR (Behavior Cloning Sampling Regularization)** — finetuning 이 진행되며 정책이 소수 mode 로 수렴해 탐색이 무너지는 것을 막기 위해, 후보 집합에 **초기 사전학습 정책** $`\pi^{dp}_{\theta_{\text{init}}}`$ 의 샘플 $`p`$ 개를 강제로 섞어 multimodal prior 를 inference 시점에 보존합니다.
- **Fleet normalization** — 병렬 fleet 의 각 에이전트가 critic ensemble 예측 통계를 실시간 공유하고, 자기 후보의 value·disagreement 를 fleet 전체 분포로 z-정규화한 뒤 선택함으로써 **집단 협력 탐색**을 구현합니다.
- **추가 모듈 불필요** — E3B·Plan2Explore 가 별도 transition dynamics 모델을 요구하는 것과 달리, DF-ExpEnse 는 RL 최적화에 이미 쓰이는 critic ensemble 을 online inference 에 **재활용**할 뿐입니다. 평가(test-time) 시에는 비활성화되어 추가 추론 비용이 없습니다.
- **범용성·일관성 검증** — DSRL(noise selection RL) 과 ResFiT(residual RL) 두 finetuning 전략에 결합해, RoboMimic·OpenAI Gym·DexMimicGen 의 조작·이동·양손 조작 태스크 전반에서 vanilla 및 대안 탐색 baseline 대비 일관된 sample-efficiency 이득을 보입니다.

---

## 🔑 기술 키워드

- **Diffusion Policy** — offline 시연을 action-space 생성 모델로 학습해 강한 multimodal behavior prior 를 만드는 visuomotor 정책. 본 논문에서는 이 multimodal 성질이 연속 행동 공간을 후보로 "필터링"하는 핵심 도구입니다.
- **Exploration Interest** — 한 후보 행동의 탐색 가치를 정량화한 점수. value 추정(품질) 과 critic disagreement(불확실성) 의 선형결합으로 정의됩니다.
- **UCB (Upper Confidence Bound)** — "추정값 + 불확실성 보너스"가 가장 큰 선택지를 고르는 고전 bandit 전략. DF-ExpEnse 는 overestimation 을 줄이려 ensemble **mean 대신 min** 을 쓰는 min-value 변형을 적용합니다.
- **Critic Ensemble** — 같은 (s, a) 를 여러 Q-함수로 평가하는 집합. min 은 value(품질), std(disagreement) 는 불확실성을 동시에 제공해 별도 모듈 없이 탐색 신호를 만듭니다.
- **BC-SR (Behavior Cloning Sampling Regularization)** — 후보 집합에 초기 사전학습 정책 샘플을 섞어 multimodal prior 의 망각을 막는 inference-time 정규화. 최적화 손실항이 아니라 후보 구성을 직접 건드린다는 점이 BC regularization 과 다릅니다.
- **Fleet Normalization** — 병렬 에이전트 간 critic 예측 통계를 공유해 자기 후보의 value·disagreement 를 fleet 전체 분포로 z-정규화하는 협력 탐색 메커니즘.
- **DSRL (Diffusion Steering RL)** — diffusion policy 를 freeze 한 채 deterministic 샘플링에 넣을 **input noise 선택 정책**(SAC)을 RL 로 학습하는 finetuning 기법. 본 논문의 main 토대.
- **ResFiT (Residual Finetuning)** — frozen diffusion policy 의 출력에 더할 **residual** 을 RL 로 학습하는 대안 finetuning 기법. DF-ExpEnse 범용성 검증용 두 번째 토대.
- **Max-Q** — 후보 중 추정 value 가 최대인 행동만 고르는 exploitative 선택( $`\alpha=0`$ 인 DF-ExpEnse 와 등가). 본 논문의 핵심 baseline.
- **Sample-Efficient Finetuning** — 같은 양의 환경 상호작용(timestep) 으로 더 높은 성공률/리워드에 도달하는 것. 본 논문의 평가 축.

---

## 🔬 방법론

### 직관

DF-ExpEnse 의 출발점은 단순합니다. 좋은 탐색은 "품질이 높은 행동"과 "불확실해서 더 알아봐야 할 행동" 사이의 균형을 찾는 것인데, 이 둘은 RL 최적화에 이미 쓰이는 critic ensemble 하나로 동시에 얻을 수 있습니다. 여러 Q-함수의 **최솟값**은 모든 critic 이 공통으로 인정하는 보수적 품질이고, 그 **표준편차**는 critic 들이 얼마나 의견이 갈리는지(=불확실성)입니다. 둘을 더한 값이 가장 큰 행동을 고르면 "다들 괜찮다고 보지만 정확한 값에는 이견이 있는, 즉 고품질이면서 덜 탐색된" 행동을 뽑게 됩니다.

문제는 연속 행동 공간에서 모든 행동을 이렇게 평가할 수 없다는 점입니다. DF-ExpEnse 의 두 번째 통찰은, diffusion policy 가 본래 multimodal 분포를 모델링하므로 거기서 몇 개만 샘플링하면 "기본 품질을 갖추면서 공간을 넓게 커버하는, 열거 평가가 가능한 소수 후보"가 공짜로 생긴다는 것입니다. 즉 diffusion 샘플 집합이 탐색을 위한 합리적 검색 공간 역할을 합니다.

세 번째로, finetuning 이 길어지면 정책이 점점 소수 mode 로 수렴해 후보들이 한 mode 에 몰리고 탐색이 무의미해집니다. 이를 막으려 **초기 사전학습 정책**에서 뽑은 샘플을 후보에 강제로 섞습니다(BC-SR). 마지막으로, 병렬 fleet 에서는 각 에이전트가 자기 후보의 점수를 fleet 전체 통계로 정규화해, 집단 전체 맥락에서 상대적으로 더 가치 있거나 불확실한 행동을 골라 중복 수집을 피합니다(fleet normalization). 이 모든 절차는 online 수집 때만 작동하고, 평가 때는 꺼져 추가 비용이 없습니다.

### 아키텍처

![Figure 1 — DF-ExpEnse 개요](https://arxiv.org/html/2606.19656/content/figures/dfexpense.png)

> "Figure 1: DF-ExpEnse Overview. At each timestep, DF-ExpEnse selects an exploratory action to execute by performing three steps. First, (a) filters the continuous action space by generating multiple samples from the diffusion policy. Then, (b) estimates exploration interest in each action with respect to quality and uncertainty using an ensemble. Lastly, (c) normalizes exploration interest across the fleet and selects the action with the maximum interest to execute." (§1)
(한글 해설 — 본 논문의 세 단계 파이프라인(필터 → 관심도 추정 → fleet 정규화·선택)을 한 장으로 보여주며, 아래 손실/식 절들이 이 세 단계를 각각 형식화합니다.)

DF-ExpEnse 는 매 timestep 두 모델 컴포넌트만 씁니다. offline behavior cloning 으로 초기화된 diffusion policy $`\pi^{dp}_{\theta}`$ 와, 무작위 초기화 가능한 $`K`$-크기 Q-함수 ensemble $`Q_{[1...K]}`$ 입니다.

> "The critic ensemble, which is normally utilized during policy gradient updates, can be reused during this online inference step to help identify actions of exploratory interest to the agent." (§3.1)
(한글 해설 — 핵심 설계 결정은 최적화에만 쓰이던 critic ensemble 의 용도를 online inference 까지 확장한 것으로, 별도 탐색 모듈을 도입하지 않는 비용 우위의 근거입니다.)

**(a) 후보 필터링.** 현재 상태 $`\mathbf{s}`$ 조건으로 diffusion policy 에서 $`M`$ 개 후보를 i.i.d. 샘플링합니다.

$$\left[\mathbf{a}_{1},\dots,\mathbf{a}_{M}\right]\sim\pi^{dp}_{\theta}(\mathbf{a}\mid\mathbf{s})$$

> "DF-ExpEnse thus essentially treats the modes estimated by the diffusion policy, approximated by sampled outputs, as a reasonable constrained space over which to search for an exploratory action worth attempting in the environment." (§1)
(한글 해설 — 샘플 집합을 diffusion 이 추정한 mode 들의 근사로 보고, 그 위를 탐색 검색 공간으로 삼는다는 것이 방법 전체의 토대입니다.)

**(c) 선택·실행.** (관심도 식은 아래 손실 절) 관심도 최대 후보를 골라 실행합니다.

$$\mathbf{a}^{\star}\leftarrow\mathrm{arg\,max}_{\mathbf{a}\in[\mathbf{a}_{1},\dots,\mathbf{a}_{M}]}\left[e_{1},\dots,e_{M}\right]$$

수집된 경험은 그대로 off-the-shelf RL 기법(DSRL/ResFiT)의 optimization 에 들어갑니다. DF-ExpEnse 는 **online 수집 단계만** 바꾸고 최적화 스킴·데이터 양은 동일하게 유지하므로, 성능 향상은 전적으로 "수집 데이터의 질" 차이로 귀속됩니다.

### 학습 목표 / 손실

**탐색 관심도 (Eq. 2).** 각 후보의 관심도 $`e_{m}`$ 은 value 추정과 critic disagreement 의 선형결합입니다.

$$e_{m}=\min\left(Q_{[1...K]}(\mathbf{a}_{m},\mathbf{s})\right)+\alpha*\text{std}\left(Q_{[1...K]}(\mathbf{a}_{m},\mathbf{s})\right)$$

> "Intuitively, if an action is roundly agreed upon to be of good quality by all critics in that the minimum estimation is high, but there is substantial disagreement amongst the critics as to what the exact value is, it is most likely a high-quality but underexplored action worth executing" (§3.1)
(한글 해설 — min 항이 "모두가 동의하는 보수적 품질", std 항이 "critic 간 이견 = 불확실성"을 잡아내며, $`\alpha`$ 는 불확실성 가중치입니다. value 를 ensemble min 으로 잡는 것은 overestimation 억제를 위한 선택입니다.)

> "We note that when $`\alpha=0`$ , the agent performs exploitative behavior, consistently selecting the action candidate with the highest estimated value at each timestep." (§3.1)
($`\alpha=0`$ 이면 순수 exploitation 으로, EMaQ·Q-Chunking 과 동일하며 본 논문의 **Max-Q** baseline 과 등가입니다.)

**BC-SR (Eq. 4–5).** finetuning 중 mode collapse 를 막기 위해, 정규화 정수 $`p\leq M`$ 에 대해 후보 집합의 일부를 **초기 사전학습 정책** 샘플로 덮어씁니다.

$$\left[\hat{\mathbf{a}}_{1},\dots,\hat{\mathbf{a}}_{p}\right]\sim\pi^{dp}_{\theta_{\text{init}}}(\mathbf{a}\mid\mathbf{s})$$

$$\left[\hat{\mathbf{a}}_{1},\dots,\hat{\mathbf{a}}_{p},\dots,\mathbf{a}_{M}\right]$$

> "in order to foster continued exploration throughout finetuning we propose regularizing the set of action candidates with samples from the initial offline-pretrained diffusion policy, denoted by $`\pi^{dp}_{\theta_{\text{init}}}`$ , which we expect to preserve more multimodal action modeling." (§3.2)
(한글 해설 — 손실항이 아니라 **후보 구성**을 직접 정규화한다는 것이 BC regularization 과의 결정적 차이입니다.)

> "Thus, BC-SR encourages the agent not to forget multimodal priors from offline pretraining during online inference." (§3.2)
(한글 해설 — DSRL 처럼 diffusion 가중치를 안 건드리는 경우, 학습된 noise selector 를 우회해 Gaussian noise 를 직접 넣어 $`\pi^{dp}_{\theta_{\text{init}}}`$ 샘플을 생성합니다 — §4.4.)

**Fleet normalization (Eq. 6–12).** 크기 $`N`$ fleet 에서 각 에이전트 $`n`$ 은 자기 상태 $`\mathbf{s}_{n}`$ 조건으로 $`M`$ 후보를 뽑아, 매 timestep $`N\times M`$ 개 행동이 모입니다. 각 후보의 value·disagreement 를 계산한 뒤 **fleet 전체** 통계로 z-정규화합니다.

$$\bar{v}_{n,m}=\frac{v_{n,m}-\text{avg}(\left[v_{1,1},...,v_{N,M}\right])}{\text{std}(\left[v_{1,1},...,v_{N,M}\right])}$$

$$\bar{d}_{n,m}=\frac{d_{n,m}-\text{avg}(\left[d_{1,1},...,d_{N,M}\right])}{\text{std}(\left[d_{1,1},...,d_{N,M}\right])}$$

$$\bar{e}_{n,m}=\bar{v}_{n,m}+\alpha*\bar{d}_{n,m}$$

> "The key insight is that having each agent share their individual critic ensemble prediction terms with other members in real-time as summarized statistics can help contextualize the exploration interest of each candidate set against the rest of the fleet, and lead to improved collective decision-making." (§3.3)
(한글 해설 — 로컬 후보 점수를 글로벌 fleet 분포로 재척도화해, 집단 맥락에서 상대적으로 더 불확실·가치 있는 행동을 고르게 만드는 것이 협력 탐색의 본질입니다.)

각 에이전트는 정규화된 관심도 $`\bar{e}_{n,m}`$ 의 argmax 후보를 실행합니다.

### 학습 셋업

- **RL 알고리즘** — main 은 **DSRL (Noise Aliasing)**: diffusion policy 를 freeze 하고 DDIM 식 deterministic 샘플링에만 접속하며, 그 입력 noise 를 만드는 **SAC** noise selector 를 RL 로 학습합니다. SAC 구현은 Stable-Baselines3 를 재사용합니다. 두 번째는 **ResFiT**(residual 학습).
- **DF-ExpEnse 의 개입 범위** — vanilla DSRL/ResFiT 의 **online 수집 단계만** 확장하고, 데이터 양과 최적화 하이퍼파라미터는 동일하게 유지합니다(부록 A 에서 base 와 다른 값만 `*` 로 표시). 평가 rollout 때는 DF-ExpEnse 를 끕니다.
- **base policy** — DSRL 실험은 DPPO 공개 checkpoint(및 Square 별도 재학습본) 재사용. DSRL 에 없던 **Tool Hang** 은 자체 학습 — flow policy(π0 식), action horizon 8, 10 Euler integration steps. ResFiT 실험은 ResFiT 사전학습 전략을 재사용(proprioception + 전 RGB 뷰 조건, 100 denoising steps, action seq 길이 16).
- **기본 하이퍼파라미터** — candidate set $`M=3`$, critic ensemble $`K=10`$, fleet $`N=4`$, BC-SR $`p=1`$, disagreement 계수 $`\alpha=0.5`$. (DSRL 기본은 ensemble 2 / fleet 4 였으나, online inference 재활용 시 더 큰 ensemble 이 이득.)
- **자원** — Brown University CCV 계산 자원. NSF IIS-2433429 / IIS-2543166, Brown Seed Award, NVIDIA Academic Grant 부분 지원.

---

## 📊 실험 설정과 결과

본 논문의 정량 결과는 모두 **timestep 대비 학습 곡선(figure)** 으로만 제시되며 본문에 단일 수치 표가 없습니다. 따라서 아래는 (1) 실험 설계·하이퍼파라미터 표와 (2) figure 에서 본문이 명시적으로 진술한 정성·서수 결론을 정리합니다(수치 추론·보정 없음).

**실험 매트릭스**

| 환경 | 태스크 | RL 토대 | 지표 |
|---|---|---|---|
| RoboMimic (조작) | Lift · Can · Square · Tool Hang | DSRL | 성공률 vs. timestep (sparse 0-1 reward) |
| OpenAI Gym (이동) | HalfCheetah-v2 · Hopper-v2 · Walker2D-v2 | DSRL | ground-truth reward score vs. timestep |
| DexMimicGen (양손 조작) | Can Sort · Box Cleanup · Coffee | ResFiT | binary 성공률 vs. timestep |

> "In evaluations for all tasks across all environments, numerical results are reported as averages over 100 rollouts, generated purely from the agent throughout stages of finetuning." (§4.2)
(평가는 100 rollout 평균, 모든 곡선은 3 random seed 의 mean ± std.)

**DSRL 기본 하이퍼파라미터 (Table 1–3, 발췌)**

| Hyperparameter | RoboMimic (Lift/Can/Square/Tool Hang) | Gym (Hopper/Walker2D/HalfCheetah) | Common |
|---|---|---|---|
| Action chunk size | 4 / 4 / 4 / 8* | 4 / 4 / 4 | — |
| Critic Ensemble Size | 10* (전 태스크) | 10* / 2 / 10* | — |
| Discount factor | 0.99 / 0.99 / 0.999 / 0.99* | 0.99 | — |
| $`\pi_{\mathrm{dp}}`$ inference denoising steps | 8 / 8 / 8 / 10* | 5 | — |
| Learning rate | — | — | 0.0003 |
| Batch size | — | — | 256 |
| Target update rate ($`\tau`$) | — | — | 0.005 |
| Fleet size | — | — | 4 |

(`*` = base DSRL 대비 변경값. Tool Hang 은 전적으로 신규라 task 하이퍼파라미터 전체를 새로 제안. "true sample efficiency" 평가를 위해 모든 태스크에서 initial step 수집 0.)

**핵심 결론 (figure 본문 진술)**

- **RoboMimic** — Lift 는 태스크가 쉽고 초기 정책 성능이 높아 모든 방법이 비슷; 더 어려운 Can/Square/Tool Hang 에서 DF-ExpEnse 가 baseline 을 크게 상회.
  > "Of note is that Max-Q underperforms against even vanilla DSRL across all the manipulation tasks." (§4.5)
  (Max-Q 의 exploitative 성향이 미탐색 critic 을 만족시키는 suboptimal mode 로 빠르게 붕괴해, 품질·다양성이 함께 무너지기 때문이라고 가설.)
- **대안 탐색 baseline 대비** — DF-ExpEnse 는 E3B(E3B-State / E3B-DINO) 와 Plan2Explore 를 일관되게 상회. E3B 는 state encoding 에 민감(DINO prior 가 현실적 시각 태스크에서 유리)한 반면 DF-ExpEnse 는 어떤 state embedding 품질에도 의존하지 않음. 게다가 E3B·Plan2Explore 는 별도 dynamics 모델이 필요하지만 DF-ExpEnse 는 불필요.
- **BC-SR ablation (Fig. 4)**
  > "removing BC-SR from DF-ExpEnse consistently decreases sample efficiency, while adding BC-SR to Max-Q significantly improves performance." (§4.6)
  (BC-SR 를 뺀 DF-ExpEnse 와 BC-SR 를 더한 Max-Q 의 곡선이 둘 사이에 위치 — multimodality 보존이 후보 필터링의 핵심임을 보임. 단 Max-Q+BC-SR 가 DF-ExpEnse 에 완전히 도달하진 못해, disagreement 항·fleet 정규화의 추가 기여를 시사.)
- **Fleet normalization ablation (Fig. 5)** — 동일 크기 fleet 을 **상호 고립**으로 돌린 것 대비, fleet normalization 이 전 평가에서 일관되게 sample efficiency 향상.
- **컴포넌트 크기 ablation (Fig. 6, Can)**
  > "using 2 critics results in significantly decreased sample efficiency performance. Performance appears to saturate with 5 critics, which achieves comparable performance to using the default size of 10." (§4.8)
  (critic ensemble: 2 → 나쁨, 5 ≈ 10 포화. candidate set: 3 → 5 약간 개선이나 대체로 포화(큰 샘플은 중복 mode). fleet: 클수록 좋고 단일 에이전트면 효과 없음.)
- **Fleet size 확장 (App. B)**
  > "Interestingly, with a fleet size of 16, the Max-Q selection algorithm completely collapses across all three seeds." (§B)
  (DF-ExpEnse 는 모든 fleet 크기에서 vanilla DSRL·Max-Q 를 안정적으로 상회.)
- **설계 결정 robustness (App. D/E)** — value 추정을 ensemble min 대신 **mean** 으로 바꿔도 성능 비슷(§D). action selection 을 argmax 대신 V-GPS 식 **exploration-weighted sampling** 으로 바꿔도 대체로 비슷하나 Square 에서 장기 발산 → argmax 를 기본값으로 채택(§E).

![Figure 2 — Baseline 비교 (DSRL)](https://arxiv.org/html/2606.19656/content/figures/dfexpense_dsrl_results.png)

> "Figure 2: Baseline Comparisons. We compare DF-ExpEnse against vanilla DSRL, a Max-Q selection scheme, as well as other exploration baselines on RoboMimic manipulation and OpenAI Gym locomotion tasks, averaged over three random seeds." (§3.3)
(한글 해설 — RoboMimic(1행)·Gym(2행) 곡선으로, 같은 timestep 에서 DF-ExpEnse 가 더 높은 성공률/리워드에 도달함을 시각화합니다.)

![Figure 6 — 컴포넌트 크기 ablation](https://arxiv.org/html/2606.19656/content/figures/size_ablation.png)

> "Figure 6: Studying Component Sizes. We ablate the critic ensemble size, action candidate sample size, and fleet size for the RoboMimic Can task. We find that DF-ExpEnse benefits from a larger ensemble and fleet size, and exhibits saturation with increases to the sample set." (§4.8)
(한글 해설 — 세 size 하이퍼파라미터의 민감도를 한 장에 정리하며, ensemble·fleet 은 클수록, sample set 은 포화함을 보입니다.)

---

## ⚖️ 한계

- **매 timestep 탐색의 낭비 (저자 명시, App. F)** — 현재 DF-ExpEnse 는 모든 timestep 에서 후보 샘플링·평가를 수행합니다. 이미 숙달된 구간(예: insertion 태스크의 pick-and-move)에서는 탐색이 무의미하거나 오히려 suboptimal 할 수 있어, 상태·숙달도 조건부로 **언제 탐색할지**를 동적으로 정하는 것이 미해결입니다. 추론 비용이 $`M`$(및 fleet 통신)에 비례하므로 실시간 제어에서 비용 문제로 직결됩니다.
- **fleet 통신의 현실성 (저자 명시, App. F)** — fleet normalization 은 매 timestep 모든 에이전트가 통계를 **실시간 동기 공유**해야 합니다. 실세계 분산 배치에서는 latency·거리 때문에 전체 통신이 비현실적이고, sharding + 로컬 정규화로 쪼개야 한다고 저자도 인정합니다. fleet=16 에서 이미 Can 태스크 이득이 포화하는 점이 이 절충을 뒷받침합니다.
- **off-policy 비정상성 가정** — fleet 의 모든 에이전트가 동일 critic ensemble 을 공유하고 동일 replay buffer 로 학습하는 구조를 암묵 전제합니다. 이질적 정책/임베디먼트 fleet 이나 비공유 critic 환경에서는 fleet 통계의 의미가 무너질 수 있는데, 논문은 동질 fleet 만 다룹니다.
- **희소·잘 정형화된 reward 환경** — 평가는 모두 명확한 reward(성공률·ground-truth score)가 있는 sim 태스크입니다. DF-ExpEnse 의 탐색 신호는 critic value 에 전적으로 의존하므로, reward 가 매우 희소하거나 critic 이 초기에 신뢰 불가한 장기 horizon 실세계 태스크에서 disagreement 항이 noise 를 좇을 위험을 다루지 않습니다.
- **BC-SR 의 prior 신선도 가정** — BC-SR 는 $`\pi^{dp}_{\theta_{\text{init}}}`$ 가 "더 multimodal 하다"고 가정합니다. 그러나 초기 정책 자체가 narrow(소수 시연·단일 mode)했다면 BC-SR 가 주입하는 후보도 다양성이 없어, 정규화 효과가 사라질 수 있습니다. 논문은 $`p=1`$ 한 값만 쓰고 $`p`$ sweep·prior 다양성 측정을 제시하지 않습니다.
- **diffusion sampling 비용 vs. 후보 수 균형** — 후보 $`M`$ 을 키우면 탐색 공간은 넓어지나 매 timestep diffusion 추론을 $`M`$ 회 해야 합니다. 100-step denoising base policy(ResFiT 실험)에서는 이 비용이 상당한데, sample set 이 3→5→7 에서 포화한다는 결과는 "비싼 추론을 키워도 이득이 빠르게 사라짐"을 뜻합니다.

---

## ♻️ 재현성

- **코드** — 프로젝트 페이지 [df-expense.github.io](https://df-expense.github.io) 가 공개되어 있으나, 본문에 명시적 GitHub 코드 링크 진술은 없습니다(페이지 내 공개 여부는 미확인 — 날조하지 않음). 토대 기법(DSRL, ResFiT, DPPO)과 SAC 구현(Stable-Baselines3)은 모두 공개 코드를 재사용합니다.
- **base checkpoint** — DSRL 실험은 DPPO 공개 checkpoint 재사용(Square 만 별도 재학습), Tool Hang 만 자체 학습. ResFiT 실험은 ResFiT 사전학습 전략 재사용. 재현 시 외부 공개 checkpoint 에 대한 의존이 큽니다.
- **하이퍼파라미터** — 부록 A 의 Table 1–3 에 RoboMimic·Gym 별 DSRL 하이퍼파라미터와 공통 하이퍼파라미터가 base 대비 변경점(`*`) 표기와 함께 제공됩니다. DexMimicGen(ResFiT) 측 하이퍼파라미터는 "vanilla ResFiT 와 동일"로만 기술됩니다.
- **벤치마크** — RoboMimic·OpenAI Gym·DexMimicGen 모두 공개 sim suite. 100 rollout 평균 · 3 seed 로 통계 절차가 명시됩니다. License CC BY 4.0.
- **하드웨어** — 전 실험이 sim 기반이며 실세계 로봇 실험은 없습니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P3(Hand-level System0 RL — 저수준 contact 안정화 RL) — 1차.** DF-ExpEnse 는 사전학습 generative policy 의 **RL finetuning sample efficiency** 를 높이는 탐색 기법으로, P3 가 다루는 "RL 로 정책을 다듬는" 영역과 정면으로 맞닿습니다. 다만 결이 다릅니다 — P3/System0 는 **PPO·GPU-parallel Isaac Lab·tactile+finger-state·contact reward**(D17)로 좁혀진 vision-excluded 안정화 sub-loop 인 반면, DF-ExpEnse 는 **off-policy SAC·critic ensemble·full-task reward** 기반 전체 정책 finetuning 입니다. 따라서 D17(System0 RL policy spec) 에 직접 매핑되기보다, "RL finetuning 시 탐색을 어떻게 할까"라는 메타 레이어를 더합니다.
- **P4(Pretraining for Data-Efficient Adaptation — prior 보존) — 2차.** BC-SR 는 D20(prior-preservation strategy) 의 **inference-time 변종**입니다. D20 의 conservative SFT 가 최적화 손실로 prior 를 지키는 것과 달리, BC-SR 는 초기 사전학습 정책 샘플을 후보에 섞어 **추론 시점에** multimodal prior 의 망각을 막습니다. "online finetuning 중 사전학습 prior 를 잃지 않는다"는 목표가 P4 의 핵심 긴장과 정확히 같습니다.
- **P1(Heterogeneous Body/Hand Action Expert — action expert) — 보조.** 토대 정책이 **diffusion/flow policy**(Tool Hang 은 π0 식 flow policy, 10 Euler step)라 D23(action representation = 연속 flow-matching head) 의 v1 선택과 정렬됩니다. DF-ExpEnse 자체는 action expert **구조**를 바꾸지 않으므로 D1–D7 split 결정에는 중립입니다.
- **Identity 긴장/지지** — MASTER Identity 는 "RL-as-core 는 generalized dexterity 의 답이 아니며, 선도사는 RL 을 **deploy-ready fine-tuning(π RLT)** 으로만 쓴다"고 못 박습니다. DF-ExpEnse 는 정확히 이 **deploy-ready fine-tuning** 카테고리에 속하는 기법으로, Identity 의 "RL = 능력 원천이 아니라 다듬기 단계" 입장을 **지지**합니다. 동시에 PROBE 의 RL 은 System0(contact 안정화)으로 **confine** 되어 있으므로, DF-ExpEnse 처럼 전체 정책을 RL finetuning 하는 것은 PROBE 스택의 RL 범위 밖이라는 **경계 긴장**도 있습니다.
- **경쟁자 함의** — 토대인 DSRL·ResFiT·DPPO 는 P3/P4 의 어느 Tracked Literature 핀에도 없는 "diffusion policy RL finetuning" 계열입니다. PROBE 가 deploy fine-tuning 단계를 구체화할 때 참조군으로 떠오를 수 있으나, 현재 pin 과 직접 경쟁하지는 않습니다.

---

## ✨ 핀 논문 대비 델타

- **vs. ConSFT (P4 D20 핀, arXiv:2605.08879)** — ConSFT 는 **deploy SFT 의 손실항**(conservative importance weighting, trust-region)으로 forgetting 을 ~20%p 줄이는 **최적화 단계** 기법입니다. DF-ExpEnse 의 BC-SR 는 같은 "prior 보존" 목표를 **inference 시점의 후보 구성**으로 달성합니다 — 손실을 건드리지 않고 초기 정책 샘플을 섞는다는 점이 진정으로 새롭습니다. 둘은 상호 배타가 아니라 직교(SFT 손실 보존 + inference 후보 보존)합니다.
- **vs. HORA / VE2VF (P3 핀)** — P3 핀들은 모두 **PPO·sim2real·contact reward** 의 in-hand 안정화 RL 입니다. DF-ExpEnse 는 reward·태스크 구조에 무관한 **off-policy 탐색(action selection) 메타 기법**으로, "어떤 RL 을 쓸까"가 아니라 "RL 수집을 어떻게 더 효율적으로 할까"라는 새 축을 더합니다. P3 핀 어디에도 critic-ensemble UCB 기반 후보 선택·fleet 협력 탐색은 없습니다.
- **순수 신규 축 — fleet 협력 탐색** — PROBE 의 어느 pillar pin 도 "병렬 fleet 이 critic 통계를 실시간 공유해 협력 탐색한다"는 개념을 갖고 있지 않습니다. 이는 PROBE 의 GPU-parallel RL(System0, 8k–16k env) 와 자원 가정은 겹치나 목적(협력 탐색 vs. 단순 throughput)이 다른, 명확히 새로운 아이디어입니다.

---

## ⚙️ 의사결정 함의

- **BC-SR 를 D20 prior-preservation 의 보조 레버로 검토** — 만약 PROBE 가 향후 Body/Hand expert 를 RL 로 deploy-finetuning 한다면, online 수집 후보에 **초기(freeze 된) 정책 샘플을 $`p`$ 개 섞는 inference-time 정규화**를 D20 의 conservative SFT 와 병행할 수 있습니다. 구체 config: `bc_sr_p`(기본 1), `candidate_set_size M`(기본 3) — diffusion/flow expert 면 거의 무비용으로 얹힙니다.
- **critic ensemble 크기 재설정** — DF-ExpEnse 의 핵심 교훈은 "ensemble 을 **최적화뿐 아니라 online inference 의 탐색 신호로** 쓰면 더 큰 ensemble(2→10)이 이득"이라는 점입니다. PROBE 가 System0 RL(D17, PPO) 에 critic ensemble 을 도입한다면, 탐색용 재활용을 전제로 `critic_ensemble_size ≥ 5` 와 disagreement 가중치 `α=0.5` 를 출발점으로 잡을 수 있습니다(단 PPO 는 on-policy 라 SAC 식 critic-ensemble UCB 가 그대로 이식되진 않음 — 아래 실패 모드 참조).
- **fleet normalization 을 System0 GPU-parallel 학습에 적용 가능성** — PROBE 의 System0 는 이미 8k–16k 병렬 env 를 씁니다. fleet normalization 은 이 대규모 병렬을 단순 throughput 이 아니라 **협력 탐색**으로 쓰는 레시피를 제공합니다. 다만 contact-stabilization 의 reward 가 dense·국소적이라 fleet-z-정규화 이득이 RoboMimic 만큼 클지는 실험 대상입니다.
- **Max-Q 회피** — exploitative greedy 선택(Max-Q)이 manipulation 에서 vanilla 보다도 나쁘고 fleet=16 에서 붕괴한다는 결과는, "value 최대 후보만 고르는" 단순 inference-time steering 을 PROBE 가 채택하지 않을 근거가 됩니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 점검) on-policy(PPO) vs. off-policy(SAC) 불일치** — DF-ExpEnse 의 critic-ensemble UCB 후보 선택은 **off-policy SAC** 의 안정적 Q-함수 ensemble 을 전제합니다. PROBE 의 System0 는 **PPO(on-policy)** 라 critic 이 현재 정책 분포에서만 의미 있고 임의 후보 행동의 off-policy Q 평가가 부정확합니다. 코드 한 줄 없이 먼저 확인할 것: "우리 RL 은 임의 후보 행동에 신뢰할 Q 를 줄 수 있는가?" 답이 아니오면 DF-ExpEnse 의 핵심 메커니즘이 그대로는 전이되지 않습니다.
- **diffusion/flow expert 의 multimodality 실재 여부** — DF-ExpEnse 의 전제는 "샘플 몇 개가 공간을 넓게 커버한다"입니다. PROBE 의 Hand expert 가 소수 시연으로 학습돼 사실상 unimodal 이라면, $`M`$ 개 샘플이 한 mode 에 몰려 후보 필터링·BC-SR 가 무의미해집니다. 점검: 사전학습 expert 에서 $`M=8`$ 샘플을 뽑아 action-space 분산/모드 수를 측정.
- **contact reward 의 dense·국소성** — System0 의 reward(slip 억제·grasp 유지)는 dense 하고 시간적으로 국소적입니다. DF-ExpEnse 가 이득을 본 RoboMimic 은 sparse 0-1 trajectory reward 라, "탐색이 의미 있는 구간"이 길게 존재합니다. dense contact reward 에서는 critic disagreement 항이 줄 신호가 약하거나 noise 일 수 있어, $`\alpha`$ 이득이 사라질 위험을 먼저 sim 에서 확인해야 합니다.
- **추론 지연 예산** — System0 는 sub-policy-loop **반응 속도**가 존재 이유입니다. 매 timestep $`M`$ 회 diffusion 추론 + fleet 통신은 이 지연 예산과 충돌합니다. 점검: 단일 후보 추론 지연 × $`M`$ 가 System0 제어 주기 안에 드는지 — 안 들면 DF-ExpEnse 는 (저자도 인정한) "탐색을 언제 할지" 게이팅 없이는 System0 에 부적합.
- **fleet 동질성·임베디먼트 가정** — fleet normalization 은 모든 에이전트가 같은 critic·같은 임베디먼트·같은 태스크 분포를 공유한다고 가정합니다. PROBE 가 이질적 하드웨어(Sharpa / xhand / 자체 hand)나 다른 태스크를 섞은 fleet 을 돌리면 fleet 통계의 z-정규화가 의미를 잃습니다. 가장 싼 점검: 동질 sim fleet 으로 ablation 을 먼저 재현한 뒤에만 이질 fleet 을 시도.
- **value overestimation 의 min 의존** — min-value UCB 는 critic ensemble 이 충분히 다양해야 overestimation 을 억제합니다. ensemble 이 작거나(2) 상관이 높으면 min 이 보수성을 잃고 disagreement 가 noise 가 됩니다(논문도 2-critic 붕괴를 보고). PROBE 도입 시 ensemble 다양성(독립 초기화·다른 데이터 순서)을 먼저 확보해야 합니다.

---

## 💡 컨텍스트 제안

- **P4 §5 methodology base 후보** — BC-SR 는 D20(prior-preservation) 의 **inference-time** 변종이라는 점에서 ConSFT(손실-단계 보존)와 직교하는 참조입니다. 핀 교체까지는 불필요하나, P4 의 "preservation 레버" 논의에 *non-pinned methodology base* 로 1줄 추가해 둘 가치가 있습니다 — "BC-SR (arXiv:2606.19656): online RL finetuning 중 후보 집합에 초기 정책 샘플을 섞는 inference-time prior 보존".
- **P3 §5 methodology base 후보** — "RL finetuning 의 탐색/sample-efficiency" 라는 메타 축이 현재 P3 핀(모두 contact-stabilization RL)에 비어 있습니다. PROBE 가 deploy fine-tuning 단계를 구체화하면 DF-ExpEnse(+ 토대 DSRL/ResFiT)를 그 축의 참조로 둘 수 있습니다 — 단 PPO↔SAC 불일치(위 실패 모드)를 함께 메모.
- **그 외** — Decision/deferred trigger 이동 제안 없음. context/ 파일은 수정하지 않았습니다.
