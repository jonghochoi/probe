# Paper Analysis — Can VLA Models Learn from Real-World Data Continually without Forgetting?

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Can VLA Models Learn from Real-World Data Continually without Forgetting? |
| 저자 | Jiarun Zhu, Yijun Hong, Xiaoquan Sun, Zetian Xu, Mingqi Yuan, Zhiyong Wang, Wenjun Zeng, Jiayu Chen |
| 링크 | [arXiv:2605.26820](https://arxiv.org/abs/2605.26820) · [GitHub](https://github.com/Agentic-Intelligence-Lab/ContinualVLA) · [Website](https://agentic-intelligence-lab.org/Never) |
| 발행일 / 버전 | 2026-05-26 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-05 |
| 관련 Pillar | P4 |
| 태그 | continual, forgetting, dataset |

---

## 🧭 한 줄 요약 (TL;DR)

시뮬레이션이 아닌 실제 로봇의 이질적인 4개 작업을 순차로 학습시키면 VLA 모델($`\pi_{0.5}`$ 기준)이 심각한 catastrophic forgetting을 겪습니다. 그러나 단 20% 규모의 experience replay에 더해 replay 빈도와 action normalization 일관성만 제대로 맞추면 망각이 거의 사라지고 심지어 joint training까지 능가합니다. 핵심은 정교한 알고리즘이 아니라 흔히 간과되던 구현 디테일이 연속 학습의 성패를 가른다는 데 있습니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — VLA 모델을 실제 배치 환경에서 평생(lifelong) 운용하려면 새 기술을 계속 습득하면서 이전에 배운 행동을 잃지 않아야 합니다. 이 실환경 연속 학습 능력이 실제로 가능한지를 검증합니다.
- **기존 접근의 한계** — 기존 연속 학습 연구는 LIBERO처럼 임바디먼트·시뮬레이터·action space가 고정된 좁은 벤치마크에 묶여 있어 분포 변화가 작아 망각을 과소평가합니다. 또한 replay의 강건성이 사전학습 중복(LIBERO가 다수 VLA 사전학습 데이터에 포함됨)으로 오염됐을 가능성이 있습니다.
- **본 논문의 가설** — VLA의 망각이 알고리즘 설계 실패에서 오는지, 아니면 분포 불일치·normalization drift·최적화 불균형 같은 간과된 구현 요인에서 오는지를 실환경에서 가려냅니다.
- **왜 지금 중요한가** — 기존 프로토콜은 인과성을 위반합니다. 여러 연구가 전체 task stream에 대한 global 통계(예: normalization 파라미터)를 순차 학습 *이전에* 미리 계산해 미래 정보를 누설하므로 보고된 성공은 실제 배치에서 불가능한 특권적 정보 환경의 산물일 수 있습니다.

---

## 🧩 핵심 기여

- 강체 pick-and-place부터 변형체 접기까지 object geometry·파지 전략·motion primitive가 크게 다른 4개 순차 조작 작업(각 500 trajectory)으로 구성된 **실환경 연속 학습 데이터셋**을 구축했습니다.
- 이 데이터셋에서 VLA 모델이 이질적인 실환경 시연을 순차 학습할 때 심각한 catastrophic forgetting을 겪음을 실측으로 확인했습니다.
- experience replay의 효과를 실환경 순차 데이터에서 평가해 선행 연구가 간과해 온 **replay 빈도**와 **action normalization 전략**이라는 구현 디테일이 연속 학습 과정을 크게 좌우함을 보였습니다.
- 잘 설정된 순차 학습 + 적당한 replay가 동일 데이터 예산 하에서 **joint multi-task training을 능가**함을 보였고 joint training의 실패를 gradient interference·representation domination·loss scale 불균형으로 분해했습니다.

---

## 🔑 기술 키워드

- **Catastrophic forgetting** — 새 작업을 배우면서 이전 작업 성능이 급락하는 현상. 본 논문이 실환경 VLA 순차 학습에서 처음으로 정량 측정하는 대상입니다.
- **Continual learning** — 비정상(non-stationary) 작업 흐름에 학습기가 이전 능력을 유지하며 순차 적응하는 설정. stability·plasticity·generalization 세 축으로 평가됩니다.
- **Experience Replay (ER)** — 과거 시연 일부를 버퍼에 저장해 새 데이터와 섞어 학습하는 표준 연속 학습 기법. 본 논문이 실환경에서 그 유효 조건을 해부하는 주 무대입니다.
- **Action normalization** — 로봇 action을 학습 전 표준화하는 통계 $`(\mu_k, \sigma_k)`$. 연속 설정에서 이 기준을 작업마다 바꾸느냐 고정하느냐가 ER 성패를 가르는 핵심 변수로 드러납니다.
- **Replay frequency** — 각 step에서 replay 버퍼를 추출할 확률 $`f_r`$. 너무 높으면 새 작업 학습을 억누르고 너무 낮으면 보존이 약해지는 U자형 민감도를 보입니다.
- **Buffer ratio** — replay 버퍼 용량을 단일 작업 데이터셋 대비 비율로 정한 값 $`B`$. 보존되는 경험의 다양성을 주로 통제합니다.
- **Negative Backward Transfer (NBT)** — 이전 작업의 성능 저하를 평균한 망각 지표. 양수일수록 후속 학습이 과거 작업을 더 망친다는 뜻이며 낮을수록 좋습니다.
- **Forward Transfer (FT)** — 순차 학습이 새 작업 습득을 돕는지(양수) 방해하는지(음수, plasticity 손실)를 단일 작업 baseline 대비로 재는 지표입니다.
- **Stability–plasticity trade-off** — 과거 지식 보존(안정성)과 새 작업 적응(가소성)이 상충하는 딜레마. replay 빈도가 이 트레이드오프를 조절하는 손잡이로 작동합니다.

---

## 🔬 방법론

### 직관

![Figure 1 — Overview of real-world continual VLA learning](https://arxiv.org/html/2605.26820/x1.png)

> "Figure 1: Overview of our investigation into real-world continual VLA learning. We collect a real-world sequential manipulation dataset of four heterogeneous tasks and study whether VLA models can adapt to them sequentially without forgetting." (§1)
(한글 해설 — 4개 이질 작업 stream과 학습 절차, 그리고 세 가지 핵심 발견(순차 FT의 심각한 망각 / 적당한 replay의 완화 / 구현 요인이 성패를 가름)을 한 장에 요약한 그림입니다.)

이 논문의 출발점은 "VLA의 망각이 알고리즘 문제인가, 아니면 간과된 구현 요인의 문제인가"라는 질문입니다. 기존 시뮬레이션 벤치마크는 분포 변화가 작아 망각을 과소평가하므로 평가 자체를 물리 세계로 옮겨 배치 현실적 제약 아래에서 다시 묻습니다.

> "These issues raise questions about whether current findings generalize to realistic settings and reveal an unexamined question: whether forgetting in VLA models stems primarily from algorithmic design failures or from overlooked factors such as distributional inconsistency, normalization drift, and optimization imbalance under real-world sequential data." (§1)
(한글 해설 — 분포 불일치·normalization drift·최적화 불균형이라는 "간과된 요인" 가설을 명시한 문장으로, 본 논문 전체의 문제의식을 못 박습니다.)

### 아키텍처

학습은 부분관측 마르코프 결정과정(POMDP)으로 정식화됩니다.

> "we model robot learning as a partially observable Markov decision process (POMDP) defined by the tuple $`\mathcal{M}=(\mathcal{S},\mathcal{O},\mathcal{A},P,\Omega,R,\gamma)`$." (§3.1)
(한글 해설 — 상태·관측·action·전이·관측함수·보상·할인으로 정의되는 POMDP로 놓고 전문가 시연 데이터셋 위에서 supervised fine-tuning을 수행합니다.)

기반 정책은 $`\pi_{0.5}`$ 이며 그 표준 SFT 셋업을 그대로 따릅니다. 입력은 멀티뷰 RGB 관측(손목 2대 + 외부 2대, 480 $`\times`$ 640, 30 Hz)이고 출력은 6관절 + gripper를 갖춘 AgileX PiPER 팔의 action(horizon 10)입니다.

연속 설정은 순차 도착하는 $`K`$ 개 작업 $`\{T_1, T_2, \dots, T_K\}`$ 의 시퀀스로 정의되며 각 작업 $`T_k`$ 는 전문가 시연 데이터셋 $`\mathcal{D}_k`$ 를 갖습니다. 목표는 $`k`$ 번째 작업까지 학습한 뒤에도 본 적 있는 모든 작업에서 잘 동작하는 정책 $`\pi_{\theta}`$ 입니다.

replay 버퍼 $`\mathcal{B}`$ 는 총 $`M = B \cdot |\mathcal{D}_k|`$ 에피소드 용량을 가지며 본 적 있는 작업들에 균등 배분됩니다.

> "the buffer capacity is allocated equally across datasets $`\{\mathcal{D}_{1},\dots,\mathcal{D}_{k}\}`$, so that each task retains at most $`\lfloor M/(k-1)\rfloor`$ episodes when training on the $`k`$-th task, with the constraint that at least one episode per task is preserved." (§5.1)
(한글 해설 — 작업 수가 늘어도 작업당 최소 1개 에피소드는 보존하면서 균형 잡힌 과거 작업 커버리지를 유지하는 버퍼 배분 규칙입니다.)

### 학습 목표 / 손실

SFT는 음의 로그우도(NLL) 손실을 최소화합니다.

> "the goal of supervised fine-tuning (SFT) is to learn a policy $`\pi_{\bm{\theta}}`$ that minimizes the following negative log-likelihood (NLL) loss" (§3.1)
(한글 해설 — 관측 조건부 action 우도를 최대화하는 표준 모방 학습 목표로, 연속 학습 단계에서도 동일하게 적용됩니다.)

$$L_{\rm SFT}=\mathbb{E}_{(\mathbf{o},\mathbf{a})\sim\mathcal{D}}\left[-\log\pi_{\mathbf{\theta}}(\mathbf{a}|\mathbf{o})\right]. \quad (1)$$

평가는 세 가지 상보적 지표를 씁니다. 먼저 최종 체크포인트에서 전체 작업의 평균 정규화 점수입니다.

$$\bar{\rho}_{K}=\frac{1}{K}\sum_{i=1}^{K}\rho_{i,K}. \quad (2)$$

여기서 $`\rho_{i,j}`$ 는 $`j`$ 번째 작업까지 학습한 모델로 $`i`$ 번째 작업을 평가한 점수입니다. 망각은 Negative Backward Transfer로 측정합니다.

$$\mathrm{NBT}_{i}=\frac{1}{K-i}\sum_{j=i+1}^{K}\bigl(\rho_{i,i}-\rho_{i,j}\bigr), \quad (3)$$

> "a positive $`\mathrm{NBT}_{i}`$ indicates that performance on task $`i`$ degrades after learning subsequent tasks." (§3.2)
(한글 해설 — 작업 $`i`$ 를 막 배운 직후 점수 $`\rho_{i,i}`$ 대비 이후 학습으로 떨어진 정도의 평균으로, 양수면 망각이 일어났다는 뜻입니다.)

새 작업 습득에 대한 순차 학습의 도움/방해는 Forward Transfer로 잽니다.

$$\mathrm{FT}_{i}=\rho_{i,i}^{(\mathrm{CL})}-\rho_{i}^{(\mathrm{single})}, \quad (4)$$

여기서 $`\rho_{i,i}^{(\mathrm{CL})}`$ 는 연속 학습 시퀀스 안에서 작업 $`i`$ 를 막 학습한 점수이고 $`\rho_{i}^{(\mathrm{single})}`$ 는 단일 작업 baseline입니다.

replay 빈도는 하이퍼파라미터 $`f_r \in (0,1)`$ 로 통제합니다.

> "with probability $`f_{r}`$, we draw from the replay buffer $`\mathcal{B}`$; with probability $`1-f_{r}`$, we draw from the dataset of the current task." (§5.1)
(한글 해설 — 각 step에서 확률 $`f_r`$ 로 과거 버퍼를, $`1-f_r`$ 로 현재 작업 데이터를 뽑습니다. replay 도입 후에도 현재 작업에 4,000 step의 유효 최적화를 보장하기 위해 총 학습 예산은 $`4000/(1-f_r)`$ 로 늘립니다.)

### 학습 셋업

$`\pi_{0.5}`$ 를 기반 정책으로 쓰고 그 표준 SFT 설정을 따릅니다. AdamW 옵티마이저 + cosine decay(peak learning rate $`5\times 10^{-5}`$, warmup 200 step, $`5\times 10^{-6}`$ 까지 감쇠), batch size 128, EMA decay 0.998, action horizon 10이며 각 작업은 4,000 step 학습합니다. 각 체크포인트는 작업별 rubric으로 평가하고 원점수를 그 작업의 최대 점수로 나눠 0–100으로 정규화합니다.

action normalization은 두 전략을 비교합니다. Strategy-I은 첫 작업의 통계 $`(\mu_1, \sigma_1)`$ 를 학습 내내 고정해 일관된 action space를 보장하고 Strategy-II는 작업마다 개별 통계 $`(\mu_k, \sigma_k)`$ 를 써서 normalization 기준이 흔들립니다. 기본값은 Strategy-I입니다. 기본 replay 설정은 $`B=0.2`$, $`f_r=0.2`$ 이며 버퍼 비율 $`B \in \{0.002, 0.02, 0.2\}`$, replay 빈도 $`f_r \in \{0.05, 0.1, 0.2, 0.5\}`$ 스윕을 추가로 돌립니다.

---

## 📊 실험 설정과 결과

핵심 비교 결과는 다음과 같습니다(§4.3, §5.2, Table 1). B는 버퍼 비율, f_r은 replay 빈도이며 점수는 최종 작업 학습 후 4개 작업에서 측정한 정규화 점수입니다.

| Category | Method | B | f_r | D1 | D2 | D3 | D4 | Avg ↑ | NBT ↓ | FT ↑ |
|---|---|---|---|---|---|---|---|---|---|---|
| Baselines | Single-task | – | – | 100.0 | 97.5 | 100.0 | 52.0 | 87.4 | – | – |
| Baselines | Joint training | – | – | 95.0 | 85.0 | 13.3 | 88.0 | 70.3 | – | – |
| No Replay | Sequential FT | 0 | 0 | 15.0 | 25.0 | 13.3 | 96.0 | 37.3 | +80.0 | -50.0 |
| Buffer Size | ER | 0.002 | 0.2 | 90.0 | 60.0 | 100.0 | 92.0 | 85.5 | +1.9 | +6.9 |
| Buffer Size | ER | 0.02 | 0.2 | 96.3 | 80.0 | 86.7 | 82.0 | 86.3 | +8.2 | +7.5 |
| Buffer Size | ER (default) | 0.2 | 0.2 | 96.3 | 97.5 | 90.0 | 90.0 | 93.5 | +5.0 | +11.8 |
| Replay Frequency | ER | 0.2 | 0.05 | 95.0 | 75.0 | 93.3 | 78.0 | 85.3 | +4.8 | +0.5 |
| Replay Frequency | ER | 0.2 | 0.1 | 98.8 | 57.5 | 96.7 | 80.0 | 83.3 | +4.6 | +2.7 |
| Replay Frequency | ER | 0.2 | 0.5 | 100.0 | 80.0 | 80.0 | 92.0 | 88.0 | -13.6 | -14.7 |

> "Sequential FT achieves only 15.0 on $`\mathcal{D}_{1}`$ (down from 100.0 single-task baseline), 25.0 on $`\mathcal{D}_{2}`$ (down from 97.5), and 13.3 on $`\mathcal{D}_{3}`$ (down from 100.0)." (§4.3, Table 1)
(한글 해설 — 마지막에 학습해 아직 망각 대상이 아닌 $`\mathcal{D}_4`$ 를 제외하면 평균이 17.8로, 단일 작업 baseline 99.2 대비 폭락합니다. NBT $`+80.0`$ 은 사실상 전면적 망각을 뜻합니다.)

![Figure 3 — Forgetting matrices under sequential fine-tuning](https://arxiv.org/html/2605.26820/x3.png)

> "Figure 3: Forgetting matrices under sequential fine-tuning. Without ER (left), all previously learned tasks collapse to near-zero performance, confirming severe catastrophic forgetting. With appropriately configured ER (right panels), forgetting is largely eliminated across all tasks." (§5.2)
(한글 해설 — replay 없는 순차 FT에서 이전 작업이 0에 가깝게 붕괴하지만, 적절히 설정한 ER이 모든 작업에서 망각을 거의 제거함을 forgetting matrix로 시각화합니다.)

experience replay는 적은 예산으로 망각을 거의 제거합니다.

> "under the default configuration ( $`B=0.2`$, $`f_{r}=0.2`$ ), all four tasks remain within 10 percentage points of their single-task baselines, and average NBT drops from 80.0 (No ER) to 5.0." (§5.2, Table 1)
(한글 해설 — 단일 작업 데이터의 20%, 학습 step의 20%만으로 NBT가 80.0에서 5.0으로 내려가 적당한 replay 예산이 망각을 거의 없앤다는 핵심 수치입니다.)

![Figure 4 — U-shaped sensitivity to buffer size and replay frequency](https://arxiv.org/html/2605.26820/x4.png)

> "Figure 4: Replay effectiveness exhibits a U-shaped sensitivity to buffer size and replay frequency. Overly frequent replay ( $`f_{r}=0.5`$ ) impairs new-task acquisition, particularly for fragile tasks such as the press button task." (§5.2)
(한글 해설 — replay 빈도가 너무 높으면(0.5) press button 같은 취약 작업의 새 학습을 억누르고 너무 낮거나(0.05) 버퍼가 작으면(0.002) hang cup처럼 다양한 replay가 필요한 작업의 보존이 약해집니다. 최적점은 $`B=0.2, f_r=0.2`$ 입니다.)

action normalization 일관성의 효과는 Table 2에 나타납니다.

| Norm Stats | D1 | D2 | D3 | D4 | Avg |
|---|---|---|---|---|---|
| Strategy-I (default) | 96.3 | 97.5 | 90.0 | 90.0 | 93.5 |
| Strategy-II (Individual stats) | 94.8 | 0.0 | 0.0 | 0.0 | 23.7 |
| Strategy-II (stack bowl's stats) | 94.8 | 42.5 | 66.7 | 28.0 | 58 |

> "Thus, action normalization consistency is not a minor detail but a critical factor that can determine whether ER succeeds or collapses entirely." (§5.2, Table 2)
(한글 해설 — 작업별 통계(Strategy-II)를 쓰면 stack bowl 이외 작업이 0.0으로 붕괴합니다. replay 데이터와 현재 데이터가 서로 다른 normalization 기준으로 섞여 동일 action(예: gripper 닫힘)이 다른 정규화 값으로 매핑되면서 모델이 안정적 action space를 세우지 못하기 때문입니다.)

연속 학습 파이프라인은 joint training도 능가합니다.

> "the continual learning pipeline with replay consistently matches or exceeds joint training across all four tasks, especially for the press button task, where joint training collapses to 13.3." (§5.2, Table 1)
(한글 해설 — joint training은 gradient interference·representation domination·task imbalance 세 메커니즘으로 실패하는 반면 순차 학습은 작업을 단계별로 분리 습득하고 replay가 과거를 보존해 "한 번에 많은 데이터가 항상 최적"이라는 통념을 반박합니다.)

---

## ⚖️ 한계

- **단일 로봇·소수 작업** — 저자가 명시한 한계로 모든 실험이 단일 AgileX PiPER 플랫폼의 4개 대표 작업에 한정됩니다. 일반성을 확보하려면 더 많은 임바디먼트와 넓은 작업 분포로 확장해야 합니다.
- **replay 중심의 좁은 기법 범위** — 주로 replay 기반 연속 학습과 normalization 일관성만 다루며, 정규화·파라미터 격리 등 다른 연속 적응 전략과 대규모 long-horizon 시나리오는 향후 과제로 남깁니다.
- **소규모 데이터** — 작업당 500 trajectory, 총 4개 작업의 비교적 짧은 stream이라 수십~수백 작업의 장기 평생 학습으로 외삽되는지는 미검증입니다.
- **평균 지표의 함정** — 저자 스스로 평균 점수가 개별 작업의 극단적 실패를 가릴 수 있다고 경고하며 작업별 비교에 주로 의존합니다. 단일 평균만 보면 결론이 왜곡될 수 있습니다.
- **base 정책 고정** — 모든 결과가 $`\pi_{0.5}`$ 한 백본에 묶여 있어, 다른 VLA 아키텍처(자기회귀 토큰형, 다른 action head)에서 동일 결론이 재현되는지는 확인되지 않았습니다.

---

## ♻️ 재현성

- **코드** — `github.com/Agentic-Intelligence-Lab/ContinualVLA` 공개(초록 명시). 프로젝트 페이지 `agentic-intelligence-lab.org/Never` 동반.
- **데이터** — 4개 실환경 순차 조작 작업(각 500 trajectory)으로 구성된 신규 데이터셋. 작업별 다단계 채점 rubric이 Appendix A에 상세 명시(Stack Bowl 4단계, Hang Cup 4단계, Press Button 3단계, Fold Towel 5단계).
- **하드웨어** — AgileX PiPER 6관절 + gripper 경량 팔, 손목 2대 + 외부 2대 카메라(RGB 480 $`\times`$ 640, 30 Hz)의 멀티뷰 teleoperation 플랫폼.
- **하이퍼파라미터** — base 정책($`\pi_{0.5}`$), 옵티마이저(AdamW + cosine decay), learning rate, batch size, EMA, action horizon, 학습 step, replay 스윕 범위가 §4.2·§5.1에 명시되어 재현 가능. 라이선스는 arXiv perpetual non-exclusive.

---

## 🎯 관련 Pillar / Decision (P# / D#)

이 논문은 **P4(VLM Pretraining Preservation)** 와 `context/MASTER.md` §8 Cross-pollination Budget의 **Month A(continual learning / catastrophic forgetting / PEFT)** 축에 정면으로 닿습니다. P4 Anti-topics가 "VLA-preservation 맥락 밖의 연속 학습/PEFT는 크로스폴리네이션으로만"이라고 규정하므로 본 논문은 $`\pi_{0.5}`$ 백본에 대한 forgetting을 직접 다룬다는 점에서 P4 본류에 해당합니다.

- **[D21] Staged training recipe** — P4의 D21은 Stage 0 lineage 선택 → Stage 1 VLM alignment 유지 → Stage 2 VLM-freeze + Body/Hand expert 학습의 단계적 레시피입니다. 본 논문은 배치 데이터가 *순차로* 도착할 때 Stage 2 이후 어떤 일이 벌어지는지(이질 작업 누적 시 전면 망각)를 실증합니다. D21의 단계 구조를 "한 번 학습"에서 "순차 누적 학습"으로 확장할 때 어떤 위험이 따르고 어떤 처방(modest replay + normalization 고정)이 듣는지를 그대로 보여 줍니다.
- **[D23] Action representation × VLM preservation** — v1은 (iii) continuous flow-matching head이며 $`\pi_{0.5}`$ 가 바로 그 계열입니다. 본 논문의 핵심 발견인 "action normalization 일관성이 ER 성패를 가른다"는 flow-matching action space의 정규화 기준 안정성 문제로, D23 선택과 직접 맞물립니다.
- **[D19] VLM fine-tuning range** — v1은 (a) full freeze + action expert만 학습입니다. 본 논문은 백본 freeze 여부 자체를 다루지 않고 SFT 전반(action expert 포함 전체 정책)을 순차 학습하므로 D19 결정과는 부분적 거리만 있으나, "freeze로 보존되는 prior와 별개로 action 측 망각이 일어난다"는 점은 곧 D19 freeze만으로는 망각을 막을 수 없다는 뜻입니다.
- **Identity 긴장/지지** — PROBE Identity는 RL을 capability source로 쓰지 않고 IL(flow-matching)을 주 학습 신호로 삼습니다. 본 논문 역시 IL(SFT) 기반 연속 학습이므로 Identity와 충돌하지 않고 오히려 IL 경로에서 망각을 다루고 보존 처방을 보탭니다.
- **§7 경쟁자 함의** — P4 §7의 watch trigger 중 ConSFT의 "forgetting-mitigation, π0/π0.5-tested" 맥락과 직접 닿습니다. 본 논문은 같은 $`\pi_{0.5}`$ 위에서 알고리즘적 규제(conservative SFT) 대신 단순 replay + 구현 디테일로 더 큰 망각 제거를 보고하므로 비교 관찰 대상입니다.

P1(아키텍처)·P2(구조적 입력)·P3(System0)의 결정에는 직접 닿지 않습니다.

---

## ✨ 핀 논문 대비 델타

- **ConSFT([arXiv:2605.08879]) 대비** — ConSFT는 trust-region conservative SFT로 importance weighting을 적용해 $`\pi_0`$/$`\pi_{0.5}`$ 에서 약 20%p 망각을 줄입니다. 본 논문은 동일 $`\pi_{0.5}`$ 백본에서 **알고리즘 규제 없이** 단순 experience replay(20% 예산)만으로 NBT를 80.0→5.0으로 내리고 더 나아가 "구현 디테일(replay 빈도·normalization 일관성)이 알고리즘 설계보다 망각을 더 깊이 좌우한다"는 정반대 강조점을 제시합니다. P4 핀 중 "보존 *전략*"에 치우친 빈자리에 "보존 *구현 요인*" 축을 채웁니다.
- **$`\pi_0`$/$`\pi_{0.5}`$([arXiv:2410.24164], [arXiv:2504.16054]) 대비** — π 핀들은 백본·flow-matching·co-training 레시피를 제공하지만 순차 배치 적응 과정의 망각을 정량화하지 않습니다. 본 논문은 $`\pi_{0.5}`$ 를 실환경 4작업 stream에서 직접 돌려 NBT/FT를 측정해, "π 백본이 그대로면 순차 학습에서 망각이 어떻게 일어나는가"라는 빈 데이터를 채웁니다.
- **동시기 직접 경쟁작 — liu2026pretrained([arXiv:2603.03818])** — 본문이 인용하며 비판적으로 대조하는 "Pretrained VLAs are surprisingly resistant to forgetting" 연구입니다. 본 논문은 그 강건성 주장이 시뮬레이션(LIBERO) 사전학습 중복으로 오염되었을 수 있다고 지적하고 실환경·causality 준수 프로토콜에서는 망각이 여전히 심각함을 보여 차별화합니다.
- **이미 분석된 hu2026simple([arXiv:2603.11653]) 대비** — 그 논문은 큰 VLA + LoRA + on-policy RL의 시너지가 망각을 막는다고 주장합니다. 본 논문은 **IL/SFT 경로**에서 **RL 없이** replay + normalization 일관성으로 같은 목표(망각 제거)에 도달하며 시뮬이 아닌 실환경에서 측정한다는 점이 핵심 차이입니다.

---

## ⚙️ 의사결정 함의

이 논문이 우리 스택에 맞다면, 배치 데이터가 순차 누적되는 시나리오에서 D21 staged recipe를 안전하게 확장하기 위한 **구체적 기본 설정값**이 생깁니다.

- **action normalization 통계 동결** — 가장 큰 함의입니다. 우리 파이프라인이 deploy 작업을 순차로 추가할 때 lerobot/openpi의 데이터셋별 normalization 통계 계산을 **작업마다 재계산하지 말고 첫 작업의 $`(\mu_1, \sigma_1)`$ 로 고정**(Strategy-I)해야 합니다. 작업별 통계(Strategy-II)는 평균 93.5→23.7로 붕괴합니다. 구체 config: 정규화 통계 산출 단계에서 `normalization_stats`를 첫 작업 시점에 freeze하는 플래그를 둡니다.
- **experience replay 기본값** — 순차 학습 시 `buffer_ratio B = 0.2`, `replay_frequency f_r = 0.2`, 작업당 최소 1 에피소드 보존, 총 step 예산 $`4000/(1-f_r)`$ 보정을 출발점으로 삼습니다. $`f_r = 0.5`$ 처럼 과한 replay는 새 작업 학습을 억눌러(FT $`-14.7`$) 금물입니다.
- **causality 준수 평가 프로토콜** — 우리 평가에서 normalization 같은 global 통계를 전체 task stream에 대해 미리 계산하면 미래 정보 누설입니다. 순차 학습 평가 시 통계·버퍼는 현재 시점까지의 데이터로만 산출하도록 평가 스크립트를 고정합니다.
- **진단 지표 추가** — 작업별 NBT($`\rho_{i,i}-\rho_{i,K}`$)와 FT를 ablation 계측에 추가하고 단일 평균에 의존하지 않고 작업별 점수로 망각의 구조(visual similarity·action primitive overlap 축)를 봅니다.

모호하지 않게: 순차 deploy 적응으로 이동한다면 normalization 통계 동결 + ($`B=0.2`$, $`f_r=0.2`$) replay + 작업별 NBT/FT 추적이 첫 실험 설정의 기본값이 됩니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **우리 스택에는 순차 적응 단계가 아직 없음** — 가장 싼 sanity check. 현재 D21 레시피는 π prior에서 Body/Hand expert를 *한 번* 학습하는 구조이지 deploy 작업을 순차 누적하지 않습니다. 본 논문의 처방은 "순차 task arrival"을 전제하므로 우리 파이프라인에 그 단계가 실제로 존재하는지부터 확인합니다 — 없으면 본 논문은 *미래* 배치 단계의 사전 대비 자료입니다.
- **저차원 gripper vs 22-DOF 손** — 본 논문 action space는 6관절 + gripper입니다. normalization 일관성 붕괴(동일 gripper 닫힘이 다른 정규화 값으로 매핑)는 저차원에서 관찰된 현상으로 Sharpa Hand(22-DOF) 같은 고차원 손 action space에서 같은 강도로 나타날지는 별도 검증이 필요합니다. 싼 점검: 우리 손 action의 작업별 $`(\mu_k, \sigma_k)`$ 분산이 실제로 큰지 먼저 측정합니다.
- **소규모·소작업 외삽** — 작업당 500 traj, 4작업 결과입니다. 우리의 in-hand reorientation·tool articulation처럼 contact-rich·long-horizon 작업이 더 많이 누적될 때 $`B=0.2`$ 버퍼가 충분한 다양성을 보존하는지는 미보장입니다.
- **base 정책 차이** — $`\pi_{0.5}`$ 표준 SFT 결과입니다. 우리의 heterogeneous Body/Hand expert split(D1)이나 structured tactile 입력(P2)이 더해진 구조에서 replay·normalization 민감도가 동일하게 재현되는지는 확인되지 않았습니다.

---

## 💡 컨텍스트 제안

- **§8 Cross-pollination Month A 후보로 기록 권장** — 본 논문은 "continual learning / catastrophic forgetting / PEFT (P4 adjacency)" 정의에 정확히 부합하는 이번 달 크로스폴리네이션 1편으로 적합합니다. 단, $`\pi_{0.5}`$ 백본을 직접 다루므로 P4 본류로 분류해도 무방합니다.
- **P4 §7 경쟁자 모니터링에 추가 검토** — ConSFT와 동일 $`\pi_{0.5}`$·동일 forgetting-mitigation 목표를 다른 수단(replay + 구현 디테일)으로 공략하는 kindred work로, 다음 rebalance 시 §7 표에 watch trigger("실환경 continual VLA 벤치마크 결과")와 함께 올리는 안을 제안합니다.
- **D21 평가 프로토콜 보강 제안** — 순차 누적 학습으로 D21을 확장할 경우 causality 준수(통계 미리 계산 금지)와 normalization 통계 동결을 평가 프로토콜의 명시 항목으로 추가하는 안을 검토합니다. (제안만 — `context/` 파일은 수정하지 않습니다.)

> 💡 base 매핑은 `/implement-design analysis/2605.26820/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
