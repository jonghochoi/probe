# Paper Analysis — Real-Time Execution of Action Chunking Flow Policies

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Real-Time Execution of Action Chunking Flow Policies |
| 저자 | Kevin Black, Manuel Y. Galliker, Sergey Levine (Physical Intelligence · UC Berkeley) |
| 링크 | [arXiv:2506.07339](https://arxiv.org/abs/2506.07339) · [GitHub](https://github.com/Physical-Intelligence/real-time-chunking-kinetix) |
| 발행일 / 버전 | 2025-06-09 (v1) · 2025-12-05 (v2) · NeurIPS 2025 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-07-06 |
| 관련 Pillar | P1, P3 |
| 태그 | vla-arch, flow-matching |

논문의 프로젝트 페이지(`pi.website/research/real_time_chunking`)는 본문에 명시되어 있으나 현재 환경의 네트워크 정책에서 응답을 확인하지 못해(연결 실패) 링크 행에서 제외했습니다. GitHub 저장소는 확인 완료(HTTP 200, raw README).

---

## 🧭 한 줄 요약 (TL;DR)

RTC(Real-Time Chunking)는 flow/diffusion 기반 VLA 를 **재학습 없이 inference-time 알고리즘만으로** 비동기 실시간 실행하게 만드는 방법입니다. 현재 chunk 를 실행하는 동안 다음 chunk 를 미리 생성하되, 추론 지연 동안 반드시 실행될 앞부분 액션을 "freeze" 하고 나머지를 인페인팅으로 이어 붙여, chunk 경계의 불연속·정지(pause) 문제를 제거하고 +200ms 의 주입 지연에도 성능 저하 없이 동작합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 수십억 파라미터 VLA 는 한 번의 추론에 수십~수백 ms 가 걸리는데, 로봇 제어는 실시간(예: 50Hz, 20ms 주기)을 요구합니다. Action chunking 은 이 격차를 부분적으로만 메우며, chunk 경계에서 정지(synchronous)나 분포 밖(OOD) 급가속(naive async)을 남깁니다.
- **기존 접근의 한계** — 동기 추론은 chunk 사이에 눈에 보이는 멈춤을 만들어 학습 분포와 다른 동역학을 유발하고, temporal ensembling 은 서로 다른 전략(mode)의 액션을 평균해 유효하지 않은 액션을 만들 수 있으며, BID 는 rejection sampling 으로 연속성을 얻지만 계산량이 큽니다. 추론 속도 최적화 계열은 forward pass 1회 미만으로는 내려갈 수 없습니다.
- **본 논문의 가설** — 실시간 chunking 을 **인페인팅 문제**로 보면 해결됩니다. 이전 chunk 와 겹치는 구간을 (부분적으로) 고정된 관측처럼 취급해 새 chunk 를 조건부 생성하면, 연속성과 반응성을 동시에 확보할 수 있습니다.
- **왜 지금 중요한가** — 로봇 데이터셋이 커질수록 최적 VLA 도 커지므로(스케일링 법칙) 지연은 구조적으로 사라지지 않습니다. 원격/클라우드 추론까지 고려하면 지연 강건성은 배포 필수 요건입니다.
- **평가 공백** — 기존 시뮬 모방학습 벤치마크는 준정적(quasi-static)이라 pseudo open-loop 전략으로 이미 포화 상태입니다. 저자들은 동적 과제 12개의 Kinetix 벤치마크를 새로 만들어 지연 강건성을 측정합니다.

---

## 🧩 핵심 기여

- **RTC 알고리즘** — diffusion/flow 기반 action chunking 정책의 비동기 실시간 실행을 위한 inference-time 시스템. 재학습·레시피 변경이 전혀 없습니다.
- **인페인팅 정식화** — 학습 없는 이미지 인페인팅 기법(Pokle et al. 의 ΠGDM 계열)을 액션 chunk 이어붙이기에 최초로 적용하고, 제어 문제 특유의 적은 denoising 스텝(`n=5`)에서 필요한 **guidance weight clipping** ( $`\beta`$ ) 을 추가했습니다.
- **Soft masking** — 겹치는 구간 전체( $`H-s`$ )에 지수 감쇠 가중치를 주어 cross-chunk 연속성을 강화하는 확장. hard masking 대비 낮은 지연 영역에서 성능이 좋습니다.
- **동적 벤치마크** — Kinetix 시뮬레이터 기반 12개 동적 과제(던지기·받기·균형) 벤치마크를 신설해, 지연 0–4 스텝 하에서 정량 비교를 제공합니다.
- **실기 검증** — $`\pi_{0.5}`$ VLA 를 베이스로 양팔 조작 6개 과제(모바일 2개 포함), 480 에피소드 / 28시간의 실기 평가에서 모든 지연 조건 최고 처리량(throughput)을 달성하고, +100/+200ms 주입 지연에서도 저하가 없음을 보였습니다.

---

## 🔑 기술 키워드

- **Action chunking** — 한 번의 추론으로 미래 액션 여러 개( $`H`$ 개)를 묶어 내보내는 방식 — 문장을 단어가 아니라 구(phrase) 단위로 말하는 것과 비슷하며, 시간적 일관성을 얻는 대신 반응성을 잃습니다.
- **Real-time chunking (RTC)** — 본 논문의 방법. 현재 chunk 실행 중에 다음 chunk 를 생성하되, 실행이 확정된 앞부분을 고정하고 나머지를 인페인팅합니다.
- **Inference delay** — $`d:=\lfloor\delta/\Delta t\rfloor`$ , 관측 수신부터 새 chunk 가용까지 걸리는 제어 스텝 수. 본 논문 실기 기준 $`d\approx 6`$ (LAN)에서 $`d\approx 16`$ (+200ms 주입)까지 평가합니다.
- **Execution horizon** — 한 chunk 에서 실제로 실행하는 액션 수 $`s`$ . $`d\leq s\leq H-d`$ 제약을 받으며, 짧을수록 closed-loop 에 가깝습니다.
- **Flow matching** — 플로우 매칭. 노이즈에서 데이터로 향하는 속도장을 학습해 적분으로 샘플을 생성하는 생성 모델링 — 강을 거슬러 올라가는 물길 지도를 배우는 것에 비유할 수 있습니다. RTC 는 이 반복 적분 과정에 개입합니다.
- **Inpainting** — 이미지의 지워진 부분을 주변과 일관되게 채우는 생성 기법. 여기서는 "이미 실행이 확정된 액션 접두부"를 그림의 남은 부분처럼 두고 뒷부분을 채웁니다.
- **Pseudoinverse guidance** — ΠGDM. denoising 각 스텝에 그래디언트 기반 보정항을 더해 최종 생성물이 목표(마스킹된 관측)와 일치하도록 유도하는 기법. RTC 인페인팅의 수학적 기반입니다.
- **Soft masking** — 마스크 $`\mathbf{W}`$ 를 0/1 이 아닌 실수 가중치로 두고, 미래로 갈수록 이전 chunk 에 대한 "주의"를 지수적으로 줄이는 본 논문의 확장.
- **Guidance weight clipping** — guidance 계수를 $`\beta`$ 로 상한 clip 하는 본 논문의 추가 장치. $`\tau=0`$ 에서 무한대가 되는 가중치를 유한하게 만들고, 적은 denoising 스텝에서의 발산을 막습니다.
- **Temporal ensembling** — 과거에 예측된 여러 chunk 에서 같은 timestep 의 액션들을 평균해 실행하는 기존 평활화 기법(ACT 계열). 다봉(multi-modal) 분포에서는 유효 액션의 평균이 유효하지 않을 수 있다는 것이 본 논문의 반례입니다.

---

## 🔬 방법론

### 직관

VLA 로 로봇을 움직일 때 가장 흔한 실행 방식은 "chunk 하나 실행 → 멈춤 → 다음 chunk 추론 → 실행"의 동기(synchronous) 방식입니다. 이 멈춤은 단순히 느린 것이 아니라, 학습 데이터에는 없던 동역학(정지 상태)을 만들어 정책을 분포 밖으로 밀어냅니다. 반대로 멈추지 않으려고 실행 중에 미리 다음 chunk 를 뽑아 두는 naive 비동기 방식은, 새 chunk 가 이전 chunk 와 다른 전략(예: 장애물 위로 vs 아래로)을 골랐을 때 이어붙는 지점에서 급격한 방향 전환을 일으킵니다.

RTC 의 핵심 아이디어는 이 문제를 이미지 인페인팅과 같은 구조로 보는 것입니다. 추론에 $`d`$ 스텝이 걸린다면, 새 chunk 의 앞 $`d`$ 개 액션은 어차피 이전 chunk 의 액션이 실행될 운명입니다. 그렇다면 그 부분을 "이미 그려진 그림"으로 고정(freeze)하고, 나머지를 그 고정부와 자연스럽게 이어지도록 생성하면 됩니다. flow/diffusion 모델은 반복 denoising 과정에 guidance 항을 더하는 것만으로 이런 조건부 생성이 가능하므로, 정책을 재학습할 필요가 전혀 없습니다.

여기에 두 가지 실전 장치가 붙습니다. 첫째, 고정 구간( $`d`$ 개)만 조건으로 걸면 $`d`$ 가 작을 때 guidance 신호가 약해 새 chunk 가 여전히 전략을 바꿔버리므로, 겹치는 구간 전체( $`H-s`$ 개)에 지수 감쇠 가중치를 주는 soft masking 으로 연속성을 강화합니다. 둘째, 제어 문제는 denoising 스텝이 5회 수준으로 적어 guidance 가중치가 폭주하기 쉬우므로 상한 $`\beta`$ 로 clip 합니다. 마지막으로 전체 시스템은 추론을 백그라운드 스레드에서 돌리고, 과거 지연의 버퍼로 다음 지연을 보수적으로 예측해 freeze 길이를 정합니다.

> "In this work, we present real-time chunking (RTC), which poses asynchronous action chunking as an inpainting problem. Our algorithm generates the next action chunk while executing the previous one, freezing the actions that are guaranteed to be executed (due to inference delay) and “inpainting” the rest." (§1)

(설계 의도를 못 박는 앵커 문장 — 비동기 실행의 연속성 문제를 "고정부 + 인페인팅"으로 환원한다는 선언입니다.)

> "It is applicable to any diffusion- [22] or flow-based [36] VLA, and operates purely at inference time, requiring no changes to existing training recipes." (§1)

(적용 조건의 전부입니다 — 반복 denoising 을 쓰는 정책이기만 하면 되고, 학습 파이프라인은 건드리지 않습니다.)

### 문제 설정 — action chunking 과 추론 지연

Action chunking 정책 $`\pi(\mathbf{A}_{t}|\mathbf{o}_{t})`$ 는 관측 $`\mathbf{o}_{t}`$ 에서 미래 액션 chunk $`\mathbf{A}_{t}=[\mathbf{a}_{t},\mathbf{a}_{t+1},...,\mathbf{a}_{t+H-1}]`$ 를 생성합니다( $`H`$ = prediction horizon). 실행 시에는 앞 $`s\leq H`$ 개만 실행합니다( $`s`$ = execution horizon).

> "Chunked execution ensures temporal consistency at the expense of reactivity. A long execution horizon reduces a policy’s responsiveness to new information, while a short one increases the likelihood of mode-jumping, jerky behavior resulting from discontinuities between chunks." (§2)

(chunking 의 근본 트레이드오프 — $`s`$ 를 늘리면 둔해지고, 줄이면 chunk 경계 불연속이 잦아집니다. RTC 는 이 트레이드오프의 후자 비용을 제거하는 장치입니다.)

flow 정책의 chunk 생성은 표준 가우시안 노이즈 $`\mathbf{A}_{t}^{0}`$ 에서 시작해 학습된 속도장 $`\mathbf{v}_{\pi}`$ 를 $`\tau=0`$ 에서 1까지 적분합니다 (식 1):

$$\mathbf{A}_{t}^{\tau+\frac{1}{n}}=\mathbf{A}_{t}^{\tau}+\frac{1}{n}\mathbf{v}_{\pi}(\mathbf{A}_{t}^{\tau},\mathbf{o}_{t},\tau)$$

여기서 $`\tau\in[0,1)`$ 는 flow matching timestep, $`n`$ 은 denoising 스텝 수입니다. diffusion 정책도 inference-time 에 flow 정책으로 변환해 사용할 수 있다고 명시합니다(§2).

지연의 단위는 제어 스텝으로 정의됩니다.

> "We define $`d:=\lfloor\delta/\Delta t\rfloor`$ and call this quantity the inference delay, corresponding to number of controller timesteps between when $`\mathbf{o}_{t}`$ is received and when $`\mathbf{A}_{t}`$ is available." (§2)

( $`\delta`$ 는 chunk 생성에 걸리는 실제 시간, $`\Delta t`$ 는 제어 주기입니다. 비동기 실행에서 새 chunk 의 앞 $`d`$ 개 액션은 도착 전에 이미 시점이 지나가 버리므로 사용할 수 없다는 것이 알고리즘 전체의 출발점입니다.)

지연이 왜 구조적인 문제인지도 구체 수치로 못 박습니다.

> "For example, with an RTX 4090 GPU, the 3 billion parameter $`\pi_{0}`$ VLA spends 46ms on the KV cache prefill alone, before any denoising steps [5], and targets a 50Hz control frequency ( $`\Delta t=20`$ ms)." (§2)

(가장 낙관적인 로컬 추론에서도 KV prefill 하나가 제어 주기 2배를 넘습니다. 원격 추론이면 네트워크 지연이 더해지고, OpenVLA 를 추론 최적화한 선행 연구도 A100 에서 321ms 였다고 인용합니다 — "한 스텝 안에 추론을 끝낸다"는 전제 자체가 현대 VLA 에서는 성립하지 않습니다.)

![Figure 2 — chunk 경계 bifurcation 문제](https://arxiv.org/html/2506.07339/x2.png)

> "Figure 2: An illustration of a typical bifurcation between consecutive chunks. Inference is started between timesteps 3 and 4. The original chunk that was executing, $`\{a_{t}\}`$ (black), had planned to go above the obstacle while the newly generated chunk $`\{a_{t}^{\prime}\}`$ (red) goes below the obstacle. However, $`\{a_{t}^{\prime}\}`$ is not available until $`d=7`$ steps later. A naive asynchronous algorithm might jump from $`a_{10}`$ to $`a_{11}^{\prime}`$ , inducing a very high, out-of-distribution acceleration. Temporal ensembling [68], i.e., interpolating between chunks, reduces the acceleration but produces poor actions." (§2)

(이 그림이 문제의 전부를 시각화합니다 — 다봉 분포에서 연속 chunk 가 서로 다른 전략으로 분기(bifurcation)하면, naive 전환은 OOD 급가속을, 평균화(TE)는 두 전략 사이의 "장애물 관통" 액션을 만듭니다.)

### 인페인팅 기반 chunk 생성 (ΠGDM + guidance clipping)

> "Our key insight is to pose real-time chunking as an inpainting problem." (§3)

(새 chunk 가 이전 chunk 와 "호환"되려면 겹치는 timestep 의 남은 액션들을 조건으로 써야 하고, 이는 이미지의 지워진 영역을 채우는 인페인팅과 동형이라는 통찰입니다.)

RTC 는 학습 없는 이미지 인페인팅 알고리즘(Pokle et al. [48], 기반은 pseudoinverse guidance ΠGDM [55])을 차용합니다. 각 denoising 스텝의 속도장에 guidance 보정항을 더해, 최종 생성물이 목표 $`\mathbf{Y}`$ (마스킹된 이전 chunk)와 일치하도록 유도합니다 (식 2–4):

$$\mathbf{v}_{\Pi\text{GDM}}(\mathbf{A}^{\tau}_{t},\mathbf{o}_{t},\tau)=\mathbf{v}(\mathbf{A}^{\tau}_{t},\mathbf{o}_{t},\tau)+\min\left(\beta,\frac{1-\tau}{\tau\cdot r^{2}_{\tau}}\right)\left(\mathbf{Y}-\widehat{\mathbf{A}^{1}_{t}}\right)^{\top}\mathrm{diag}(\mathbf{W})\;\frac{\partial\widehat{\mathbf{A}^{1}_{t}}}{\partial\mathbf{A}^{\tau}_{t}}$$

$$\widehat{\mathbf{A}^{1}_{t}}=\mathbf{A}^{\tau}_{t}+(1-\tau)\mathbf{v}(\mathbf{A}^{\tau}_{t},\mathbf{o}_{t},\tau)$$

$$r^{2}_{\tau}=\frac{(1-\tau)^{2}}{\tau^{2}+(1-\tau)^{2}}$$

각 항의 의미는 다음과 같습니다. $`\widehat{\mathbf{A}^{1}_{t}}`$ 는 현재 노이즈 상태 $`\mathbf{A}^{\tau}_{t}`$ 에서 속도장을 한 번에 끝까지 적분했다고 가정한 **최종 chunk 의 1-스텝 추정치**입니다(식 3). guidance 항은 이 추정치와 목표 $`\mathbf{Y}`$ 의 차이를 마스크 $`\mathbf{W}`$ 로 가중한 뒤, 추정치의 야코비안을 통해 현재 상태로 되끌어온(vector-Jacobian product) 그래디언트입니다 — 즉 "이대로 denoising 이 끝나면 고정부와 얼마나 어긋날지"를 미리 계산해 매 스텝 궤도를 수정합니다. $`\mathbf{Y}`$ , $`\mathbf{A}_{t}`$ , $`\mathbf{W}`$ 는 표기 남용으로 $`HM`$ 차원 벡터로 취급되며( $`M`$ = 액션 차원), guidance 항은 역전파로 계산 가능합니다(§3.1).

> "The guidance weight clipping, $`\beta`$ , is our addition; we found that without it, the algorithm became unstable with the small number of denoising steps commonly used in control problems (see A.2 for an ablation)." (§3.1)

(원 논문 [48]은 $`n=100`$ 스텝의 이미지 인페인팅이라 문제가 없었지만, 제어는 $`n=5`$ 수준입니다. 식 2의 계수 $`\frac{1-\tau}{\tau\cdot r^{2}_{\tau}}`$ 는 $`\tau=0`$ 에서 무한대가 되므로, clip 없이는 첫 스텝부터 chunk 가 발산합니다. 부록 A.2 의 ablation 에서 $`\beta`$ 가 너무 크면 최대 가속도(OOD 지표)가 커지고, $`\beta=5`$ 이상에서는 성능의 한계 이득이 없어 보수적으로 5를 채택했습니다.)

> "Based on a simulated ablation (Figure 7, top right), we set $`\beta`$ to a conservative value of 5." (§A.2)

(clipping 은 안정성 장치이자 사실상 유일하게 새로 튜닝된 스칼라입니다.)

### Soft masking — cross-chunk 연속성 강화

고정부 $`d`$ 개만 조건으로 쓰는 naive(hard) 인페인팅은 $`d`$ 가 작을 때 guidance 신호가 약해 새 chunk 가 여전히 전략을 바꿀 수 있습니다.

> "Our solution, illustrated in Figure 3, is to give our policy more cross-chunk continuity by considering not just the first $`d`$ overlapping actions, but all $`H-s`$ overlapping actions." (§3.2)

(이전 chunk 와 겹치는 모든 구간을 활용하되, 확실히 실행될 앞부분은 강하게, 먼 미래는 약하게 조건을 겁니다 — "확정된 과거는 사실, 먼 계획은 참고"라는 가중의 직관입니다.)

마스크 $`\mathbf{W}`$ 는 0/1 이 아닌 실수 가중치로 설정됩니다 (식 5):

```math
\mathbf{W}_{i}=\begin{cases}1&\text{if }i<d\\ c_{i}\frac{e^{c_{i}}-1}{e-1}&\text{if }d\leq i<H-s\\ 0&\text{if }i\geq H-s\end{cases}\quad\text{where}\;\;c_{i}=\frac{H-s-i}{H-s-d+1},\;\;i\in\{0,\ldots,H-1\}.
```

앞 $`d`$ 개(freeze 구간)는 가중치 1, 이전 chunk 와 겹치지 않는 마지막 $`s`$ 개는 0, 중간 구간은 1에서 0으로 지수 감쇠합니다.

> "Intuitively, $`\mathbf{W}`$ modulates the “attention” paid to each corresponding action from the previous chunk." (§3.2)

(부록 A.4 의 스케줄 ablation 에서 지수 감쇠가 전반적으로 최고였고 선형 감쇠가 근소하게 뒤따랐습니다 — 스케줄 모양 자체보다 "중간 구간을 조건에 포함하는 것"이 본질임을 시사합니다.)

![Figure 4 — hard vs soft masking 비교](https://arxiv.org/html/2506.07339/x4.png)

> "Figure 4: A comparison of naive inpainting (hard masking) and our proposed soft masking method: note that hard masking does not match the frozen region very well and produces faster changes in direction." (§3.2)

(hard masking 은 고정부와의 정합조차 불완전하고 방향 전환이 급합니다 — soft masking 이 단순한 미관 개선이 아니라 정합 품질 자체를 올린다는 근거 그림입니다.)

### 전체 시스템 (Algorithm 1)

![Figure 3 — RTC 의 이전 chunk 주의(attention) 다이어그램](https://arxiv.org/html/2506.07339/x3.png)

> "Figure 3: A diagram illustrating how action generation attends to the previous action chunk in real-time chunking. If inference starts after the execution of $`a_{-1}`$ and the inference delay is $`d=4`$ , then the newly generated chunk will not be available until after $`a_{3}`$ is consumed. Therefore, $`a_{0:3}`$ are “frozen” and are attended to with a full guidance weight of 1. In the intermediate region, $`a_{4:10}`$ , actions from the previous chunk are available but may be updated, since inference will have finished before $`a_{4}`$ is needed. This region is attended to with an exponentially decreasing guidance weight. Finally, the last $`s=5`$ actions are beyond the end of the previous chunk, and need to be freshly generated. The execution horizon, $`s`$ , is a hyperparameter constrained by $`d\leq s\leq H-d`$ ." (§2)

(freeze / 지수 감쇠 / 신규 생성의 3구간 구조와 실시간 제약 $`d\leq s\leq H-d`$ 를 한 장에 요약한 시스템 다이어그램입니다.)

Algorithm 1 은 세 부분으로 구성됩니다 (§3.3):

- **GetAction** — 컨트롤러가 매 $`\Delta t`$ 마다 호출. 현재 chunk 에서 액션 하나를 소비하고 최신 관측을 공유 상태에 기록합니다(뮤텍스 보호).
- **InferenceLoop** — 백그라운드 스레드. $`t\geq s_{\text{min}}`$ 이 되면 이미 실행된 $`s=t`$ 개를 잘라낸 $`\mathbf{A}_{\text{prev}}`$ 와 최신 관측으로 GuidedInference 를 호출하고, 완료 즉시 $`\mathbf{A}_{\text{cur}}`$ 를 새 chunk 로 교체합니다. 지연은 크기 $`b`$ 의 과거-지연 버퍼의 **최댓값**으로 보수적으로 예측합니다.
- **GuidedInference** — 식 5로 $`\mathbf{W}`$ 를 계산하고 $`\mathbf{A}_{\text{prev}}`$ 를 길이 $`H`$ 로 right-pad 한 뒤, 매 스텝 식 3의 denoising 함수를 명시적으로 정의해 vector-Jacobian product 를 역모드 자동미분으로 계산하고 식 1로 적분합니다.

> "It forecasts the next delay, $`d`$ , by keeping a buffer of past delays. The execution horizon, $`s`$ , can change from chunk to chunk; the user provides a minimum desired horizon, $`s_{\text{min}}`$ , and the actual horizon for a given chunk is $`\max(d,s_{\text{min}})`$ where $`d`$ is the delay encountered when computing the next chunk." (§3.3)

(execution horizon 이 고정 하이퍼가 아니라 지연에 적응하는 런타임 변수라는 점이 실전 시스템다운 부분입니다 — 지연이 커지면 자동으로 더 길게 실행하고, freeze 구간도 그만큼 늘어납니다.)

### 학습 셋업

RTC 자체는 학습이 없습니다(inference-time only). 실험에 쓰인 정책의 학습 셋업은 다음과 같습니다.

- **시뮬레이션(§4.1)** — Kinetix 12개 동적 과제. RPO 로 환경당 6개 시드의 expert 정책을 학습해 1M transition 데이터셋을 생성하고, 여기에 액션 가우시안 노이즈를 더해 closed-loop 보정이 필수가 되도록 했습니다.

> "We then train action chunking flow policies with a prediction horizon of $`H=8`$ and a 4-layer MLP-Mixer [61] architecture for 32 epochs." (§4.1)

(시뮬 정책은 VLA 가 아니라 소형 flow 정책입니다 — 알고리즘 자체의 성질을 지연 0–4 스텝 스윕으로 검증하기 위한 통제 실험 설계입니다.)

- **실기(§4.2, §A.7)** — $`\pi_{0.5}`$ base 모델에서 과제별 fine-tuning(8×H100, 약 24시간). 추론은 RTX 4090 1장, bfloat16, $`n=5`$ denoising 스텝, LAN 원격 추론(WebSocket).

---

## 📊 실험 설정과 결과

### 시뮬레이션 벤치마크 (Kinetix, 12개 동적 과제)

force 기반 제어라 "멈춰서 기다리기"가 불가능한 동적 환경에서, 지연 0–4 스텝( $`H=8`$ 의 최대치)을 스윕하며 naive async / BID( $`N=32`$ , $`K=3`$ ) / TE 와 비교했습니다. 데이터 포인트당 2048 롤아웃, 95% Wilson score 구간을 보고합니다.

> "TE performs poorly across the board, even with an inference delay of $`d=0`$ , illustrating the multi-modality of our benchmark—averages of valid actions are not necessarily valid." (§4.1)

(TE 의 실패는 지연 때문이 아니라 평균화 자체의 결함입니다 — 다봉 액션 분포에서 두 유효 전략의 평균은 무효 전략일 수 있습니다.)

> "RTC shows the most robustness to inference delays, outperforming BID, and the gap widens with increasing delay; note that BID uses significantly more compute than RTC by sampling batches of 64 action chunks, 32 from a strong model and 32 from a weak model." (§4.1)

(경쟁 방법 중 유일하게 연속성 확보에 성공하면서 계산량은 훨씬 적습니다 — rejection sampling(BID) 대비 guidance 기반 인페인팅의 효율 우위입니다.)

> "Additionally, we find that hard masking somewhat underperforms soft masking, particularly when $`d`$ is smaller, supporting our claims in Sec. 3.2." (§4.1)

(soft masking ablation — $`d`$ 가 작을수록 hard mask 의 guidance 신호가 약해진다는 §3.2 의 주장과 정합합니다.)

또한 execution horizon 스윕(지연 1 고정)에서는 RTC 와 BID 만이 $`s`$ 를 줄일수록 단조 증가하는 성능을 보여, RTC 가 closed-loop 보정을 온전히 활용함을 보였습니다.

![Figure 5 — 지연·execution horizon 스윕 결과](https://arxiv.org/html/2506.07339/x14.png)

> "Figure 5: Top left: Kinetix environments; each involves getting a green object on the left to touch a blue one on the right. Bottom left: Execution horizon vs. solve rate with a fixed inference delay of 1. Only RTC and BID take full advantage of faster updates, showing strictly increasing performance with decreasing execution horizon. Right: Inference delay vs. solve rate with a fixed execution horizon of $`s=\max(d,1)`$ . RTC outperforms all baselines. Furthermore, soft masking (Sec. 3.2) improves performance at lower inference delays and execution horizons. Each data point represents 2048 trials, and 95% Wilson score intervals are shaded in." (§4.1)

(핵심 정량 결과 — 지연이 커질수록 RTC 와 나머지의 격차가 벌어지고, soft masking 의 이득은 저지연 구간에 집중됩니다.)

### 실기 결과 ( $`\pi_{0.5}`$ , 양팔 6개 과제)

> "We use $`\pi_{0.5}`$ ( $`H=50`$ , $`\Delta t=20`$ ms) with $`n=5`$ denoising steps, giving a model latency of 76ms for the baselines and 97ms for RTC." (§4.2)

(RTC 의 guidance 역전파가 모델 지연을 76→97ms 로 늘립니다. 여기에 LAN 원격 추론 10–20ms 가 더해져 기본 $`d\approx 6`$ 이고, +100ms/+200ms 주입 시 $`d\approx 11`$ / $`d\approx 16`$ 이 됩니다.)

과제 구성 (에피소드당 완료한 substep 수를 정수 점수로 채점, 과제·방법당 10 trial, 총 480 에피소드 / 28시간):

| 과제 | Steps | Cutoff |
|------|-------|--------|
| Light candle | 5 | 40s |
| Plug ethernet | 6 | 120s |
| Make bed (mobile) | 3 | 200s |
| Shirt folding | 1 | 300s |
| Batch folding | 4 | 300s |
| Dishes in sink (mobile) | 8 | 300s |

비교군은 Synchronous( $`s=25`$ 실행 후 정지), TE sparse( $`s=25`$ 비동기 + TE 평활), TE dense(가능한 한 자주 추론, $`s=d`$ )입니다. BID 는 시뮬에서 이미 열세인 데다 $`\pi_{0.5}`$ 적용 시 지연이 RTC 의 2.3배라 실기 비교에서 제외했습니다.

> "In average task throughput, a measurement of both speed and performance, RTC achieves the best score at all inference delays with a statistically significant result at +100 and +200ms." (§4.2)

(headline 결과 — throughput = 완료 비율 / 에피소드 시간. 속도와 성공률을 한 지표로 본 것입니다.)

> "RTC is completely robust to injected delay, showing no degradation, whereas synchronous degrades linearly and both TE variants do not run at all due to causing such high oscillations that the robot’s protective stop is triggered (see videos)." (§4.2)

(+200ms 에서도 저하 zero — 반면 TE 계열은 진동으로 보호 정지가 걸려 아예 실행 불가였습니다. 지연 강건성이 RTC 의 고유 성질임을 보여줍니다.)

> "In light candle, the most precision-sensitive task—and also the only one without retrying—RTC shows a large advantage in final score, reflecting a higher overall success rate." (§4.2)

(재시도가 불가능한 정밀 과제(성냥 켜기)에서 최종 점수 자체가 크게 앞섭니다 — chunk 경계 불연속이 정밀 조작의 실패 원인이며 RTC 가 그것을 제거한다는 가장 직접적인 증거입니다. 재시도가 허용되는 과제에서도 RTC 는 에피소드 초반에 더 많은 진행을 달성해, 같은 최종 점수라도 실수와 재시도가 적음을 보입니다.)

![Figure 6 — 실기 과제별 누적 진행 결과](https://arxiv.org/html/2506.07339/x15.png)

> "Figure 6: Top: Controller steps (equivalent to elapsed time with inference pauses removed multiplied by 50Hz) vs. cumulative progress for each task, aggregated across all delays. Progress is measured in discrete steps corresponding to the subsections of each task. Left: Time (including inference pauses) vs. cumulative progress aggregated across all tasks. The x-axis is log scale to better show progress during both short and long-horizon tasks. Right: Inference delay vs. average throughput, defined as the proportion of task completed divided by duration of episode averaged over episodes. Error bars are $`\pm 1`$ SEM. Average throughput gives a balanced view of both speed and performance for each method. Neither TE variant can run at +100 or +200ms of injected latency, causing such high oscillations that the robot’s protective stop is triggered." (§4.2)

(controller step 축(추론 정지 시간 제거) 기준으로도 RTC 가 더 빠릅니다 — 즉 단순히 멈춤이 없어서 빠른 것이 아니라, 실행 궤적의 품질 자체가 좋아 같은 스텝 수로 더 많이 진행합니다.)

### 지연 측정 (부록 A.3)

Table 1 (RTX 4090, bfloat16, $`n=5`$ , $`\pi_{0.5}`$ 기준 방법별 on-GPU 지연):

| Method | Latency |
|--------|---------|
| RTC (ours) | 97ms |
| BID with `N=16` (no forward model) | 115ms |
| BID with `N=16` (shared backbone) | 169ms |
| BID with `N=16` (full) | 223ms |
| Vanilla $`\pi_{0.5}`$ | 76ms |

Table 3 (모델 추론 지연 구성요소별 분해):

| Component | Time (no RTC) | Time (with RTC) |
|-----------|---------------|-----------------|
| Image encoders (SigLIP) | 18ms | 18ms |
| LLM prefill (Gemma 2B) | 44ms | 44ms |
| Denoising step (x5) | 14ms | 35ms |
| Total | 76ms | 97ms |

RTC 의 오버헤드는 전적으로 denoising 스텝의 역전파에서 나오며, 스텝당 2.5배입니다(§A.3, Table 3). 전체 시스템 지연(§A.3, Table 2)은 non-mobile 108.76 ± 2.34ms, mobile 138.98 ± 6.71ms (네트워크·이미지 리사이즈·기타 포함)입니다.

### 추가 ablation (부록 A.2, A.4)

- **$`\beta`$ ablation** — 시뮬 벤치마크에서 $`\beta=5`$ 이상 증가는 한계 이득 없음. $`n=5`$ 에서 $`\beta`$ 가 크면 같은 노이즈에서 생성한 chunk 가 발산하고, $`d=15`$ / $`n=5`$ 의 325개 chunk 배치에서 $`\beta`$ 가 클수록 최대 가속도(2차 차분, OOD 프록시)가 증가합니다(§A.2, Figure 7).
- **감쇠 스케줄** — 지수 감쇠가 최고, 선형이 근소한 차이로 2위(§A.4, Figure 8 좌).
- **Diffuser 식 인페인팅과 비교** — denoising 마다 해당 구간을 목표 값으로 덮어쓰는 더 싼 방식도 이득은 있으나 guidance 기반에 뒤집니다(§A.4, Figure 8 우).

---

## ⚖️ 한계

- **계산 오버헤드 (저자 명시)** — guidance 의 vector-Jacobian product 때문에 denoising 스텝당 2.5배의 지연이 붙습니다(76→97ms). 역설적으로 "지연을 다루는 방법이 지연을 늘리는" 구조라, 지연 자체가 아니라 지연의 *해악*을 없애는 방법임을 이해해야 합니다. 모델이 더 커지거나 스텝 수가 늘면 오버헤드도 비례해 커집니다.

> "However, this work is not without limitations: it adds significant computational overhead compared to methods that sample directly from the base policy, and it is applicable only to diffusion- and flow-based policies." (§6)

- **적용 범위 (저자 명시)** — 반복 denoising 계열(diffusion/flow)에만 적용됩니다. autoregressive/VQ/BPE 토큰 계열 VLA(π0-FAST 류)에는 이 형태의 인페인팅 guidance 를 걸 수 없습니다.
- **동적 실기 검증 부재 (저자 명시)** — 시뮬 벤치마크에는 locomotion 이 포함되지만 실기는 조작 과제뿐이며, 더 동적인 실기 세팅은 future work 입니다.
- **반응성의 하한은 여전히 $`d`$ (추론된 갭)** — freeze 구간은 정의상 새 관측을 반영할 수 없으므로, 관측 반영 지연의 하한은 $`d\cdot\Delta t`$ (실기 기준 약 120–320ms)로 남습니다. RTC 는 chunk 경계의 *불연속*을 없애는 것이지, 시스템의 *반응 시간*을 줄이는 것이 아닙니다.
- **연속성 guidance 와 전략 전환의 긴장 (추론된 갭)** — soft masking 은 새 chunk 를 이전 chunk 의 전략에 붙들어 둡니다. 관측이 "지금 전략을 버리고 다시 잡아야 한다"고 말하는 상황(실패한 파지 직후 등)에서는 이 관성이 교정을 한 chunk 만큼 늦출 수 있습니다. 논문은 재시도 행동이 잘 나온다고 보고하지만( $`\pi_{0.5}`$ 의 성질), guidance 강도와 교정 속도의 트레이드오프 자체는 정량화되지 않았습니다.
- **guidance 는 근사 (추론된 갭)** — ΠGDM 보정은 정확한 조건부 사후분포 샘플링이 아니라 1-스텝 추정 기반 근사이며, $`\beta`$ clip 은 그 근사를 더 거칠게 만듭니다. hard/soft/스케줄/ $`\beta`$ 의 상호작용이 과제 분포에 따라 재튜닝을 요구할 수 있습니다.
- **실기 통계의 폭 (추론된 갭)** — 과제·방법·지연 조합당 10 trial 이라, throughput 의 유의성은 +100/+200ms 에서만 성립합니다. 기본 지연( $`d\approx 6`$ )에서의 우위는 방향은 일관되나 통계적으로는 약합니다.

---

## ♻️ 재현성

- **코드** — 시뮬레이션 실험 코드 공개: [GitHub](https://github.com/Physical-Intelligence/real-time-chunking-kinetix) (§A.6). 실기 시스템( $`\pi_{0.5}`$ + 원격 추론 스택)은 비공개입니다.
- **데이터** — 시뮬 데이터는 공개 코드로 재생성 가능(RPO expert → 1M transition). 실기 fine-tuning 데이터는 비공개.
- **하드웨어** — 실기: 양팔 6-DoF + parallel jaw gripper(모바일 포함), 추론 RTX 4090 1장(bfloat16), 학습 8×H100 약 24시간/과제(§A.7). 시뮬: 전체 파이프라인이 H100 몇 시간 수준으로 가볍습니다.
- **알고리즘 자체의 재현성** — Algorithm 1 의사코드 + 하이퍼 전부(Table 4: $`n=5`$ , $`H=8/50`$ , $`s_{\text{min}}=25`$ , $`\beta=5`$ , $`b=10`$ )가 명시되어 있고 재학습이 필요 없어, flow 정책만 있으면 이식 난도는 낮습니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P1(이종 Body/Hand 액션 전문가) / D5(입력 모달리티·제어율 분리) — 직접 관련.** D5 v1 은 Body/Hand **공유 제어율**(α)입니다. RTC 는 공유율 chunked 실행의 배포층을 규정하는 방법으로, 우리 스택의 flow 기반 액션 전문가(D23 연계)가 실기에서 어떤 실행 전략을 쓸지에 대한 사실상의 기본값 후보입니다. 특히 $`d\leq s\leq H-d`$ 제약은 chunk 길이 $`H`$ 설계(D5 의 제어율 선택과 결합)에 정량 하한을 제공합니다.
- **P1 / D7(π backbone 통합·분할) — 직접 관련.** 본 논문은 $`\pi_{0.5}`$ 실행 인프라를 다루므로, D7 v1(π0 액션 전문가 슬라이스 + 양측 FT)로 만든 정책의 배포 경로에 그대로 얹힙니다. RTC 는 아키텍처를 건드리지 않으므로 D7 선택과 독립적으로 채택 가능합니다.
- **P3(Hand-level System0 모듈) / D13(System0 역할·작동 영역), D14(System1↔System0 인터페이스) — 경계 규정.** RTC 는 System1(VLA)의 반응 지연 하한이 $`d\cdot\Delta t`$ (실기 120–320ms)임을 정량화합니다. 즉 **RTC 를 써도 sub-chunk 시간 스케일의 접촉 이벤트(slip 등)는 System1 이 커버할 수 없고**, 이는 System0 의 존재 이유를 강화합니다. 동시에 System1 측 실행이 매끄러워지므로, System0 게이팅(D14)이 "System1 의 chunk 경계 잡음"까지 흡수할 필요는 없어집니다 — 두 모듈의 책임 경계가 깨끗해집니다. Related Work 의 System1/System2 계층 VLA 논의에서 저자들도 이 계열과 자신들의 방법이 직교(orthogonal)함을 명시합니다.
- **P4(사전학습 기반 데이터 효율 적응) — 간접.** π lineage( $`\pi_{0.5}`$ , D19 v1 의 연장)의 실행층이라는 점에서 접점이 있으나, 사전학습 구성·보존에는 기여가 없습니다. D19–D23 을 움직이지 않습니다.
- **P0, P2, P5** — 접점 없음. 데이터셋/벤치마크 기여는 Kinetix 12과제이지만 이는 동적 *제어* 벤치마크로 P0 의 스카우팅 범위(사전학습 corpus·접촉 데이터)에 들지 않고, 관측 융합·월드모델과도 무관합니다.
- **Identity 정합** — RTC 는 frozen VLA 위의 보정/residual 모듈(Antagonist A)이 **아닙니다**. 같은 정책의 같은 분포에서 샘플링하는 inference-time 절차라 "VLA ceiling 을 넘는 척하는 보정 모듈" 비판에 걸리지 않으며, 오히려 VLA-level 로 승부하는 우리 Identity 의 배포 실현 가능성(실시간성)을 받쳐 줍니다.

---

## ✨ 핀 논문 대비 델타

- **vs π0 ([arXiv:2410.24164](https://arxiv.org/abs/2410.24164), P1 핀)** — π0 는 flow 액션 전문가와 50Hz 제어를 제시했지만 실행은 동기 추론(멈춤 포함)이 기본입니다. RTC 는 그 실행 공백을 메우는 후속으로, 같은 π 계보에서 나온 **실행층(inference-time execution layer)** 기여입니다. 아키텍처·학습 델타는 없습니다.
- **vs π0.5 ([arXiv:2504.16054](https://arxiv.org/abs/2504.16054), P4 핀·P1 methodology base)** — π0.5 를 base 정책으로 그대로 사용하며, 본 논문의 델타는 순수하게 "그 정책을 어떻게 실시간으로 돌리는가"입니다. π0.5 의 open-world 일반화 주장과 독립적입니다.
- **vs LaMP / Dexora / DexGrasp-VLA (P1 핀)** — 이들은 액션 전문가의 *구조*(dual-expert, arm/hand 분할)를 다루고, RTC 는 *실행*을 다룹니다. 서로 배타적이지 않고 조합 가능합니다.
- **커버리지 공백** — 현재 P1–P5 어느 핀도 추론 지연·비동기 실행·chunk 경계 연속성을 다루지 않습니다. RTC 는 이 축의 첫 진입 논문입니다 (가장 가까운 선행 BID 는 핀 목록에 없으며, 본 논문 실험에서 RTC 에 열세).

---

## ⚙️ 의사결정 함의

- **배포 실행 전략의 기본값** — 우리 스택의 Body/Hand flow 전문가(D23 v1 continuous flow-matching head) 실기 배포 시, 동기 추론 대신 RTC 형 비동기 실행을 기본값으로 두는 것이 합리적입니다. 도입 파라미터는 논문 값에서 시작: `n_denoise=5`, `beta=5`, `s_min=H/2`, `delay_buffer=10`. 오픈소스 `lerobot` 에는 이미 `policies/rtc` 모듈이 존재하므로 도입 비용이 낮습니다.
- **chunk 길이 $`H`$ 의 정량 설계 규칙** — 실시간 제약 $`d\leq s\leq H-d`$ 에서, 우리 하드웨어의 실측 $`d`$ (모델 지연 + Deform Map 전처리 + 네트워크)를 먼저 재고 $`H > 2d`$ 를 보장해야 합니다. 우리는 π0.5 대비 Hand 전문가·촉각 토큰이 추가되므로 $`d`$ 는 논문의 6보다 커질 가능성이 높습니다 — $`H=50`$ 유지 여부를 실측 후 결정해야 합니다.
- **System0 게이팅 창의 수치화 (D13/D14)** — System0 가 커버해야 하는 반응 창을 "RTC freeze 구간 = $`d\cdot\Delta t`$ "로 명시적으로 정의할 수 있습니다. System1 이 어떤 실행 전략을 쓰든 이 창 안의 slip 대응은 구조적으로 불가능하므로, System0 의 발동 조건·대역 설계(D14 binary gate)의 요구 사양이 됩니다.
- **평가 지표 추가** — 데모 과제 평가에 (1) **average throughput**(완료 비율/에피소드 시간)과 (2) **최대 가속도(2차 차분)** 를 넣는 것이 좋습니다. 전자는 속도·성공률을 한 번에 보는 지표로 Phase 1 인핸드 회전 평가에 그대로 이식 가능하고, 후자는 chunk 경계 OOD 잡음의 싼 프록시로 논문이 직접 검증한 지표입니다.
- **guidance 역전파 예산** — RTC 채택 시 denoising 스텝당 2.5배 지연을 GPU 예산에 반영해야 합니다. 우리 이중 전문가(Body/Hand) 구조에서는 VJP 가 두 head 를 모두 통과하므로 오버헤드가 논문보다 커질 수 있습니다 — 지연 예산표에 "RTC 세율" 항목을 추가해 관리해야 합니다.

---

## ⚠️ 먼저 검증할 실패 모드

1. **[가장 싼 체크] 지연 실측과 $`H`$ 제약 확인** — 우리 파이프라인(π backbone + Body/Hand 전문가 + 촉각 토큰)의 end-to-end $`\delta`$ 를 RTX 급 GPU 에서 프로파일링하고 $`d=\lceil\delta/\Delta t\rceil`$ 산출. $`d > H-s_{\text{min}}`$ 이면 RTC 이전에 $`H`$ 재설계가 선행되어야 합니다. 반나절 작업.
2. **VJP 오버헤드의 스케일링** — 22-DOF 핸드 + 양팔이면 액션 차원 $`M`$ 이 논문(6-DoF×2+gripper)보다 큽니다. guidance 역전파가 스텝당 2.5배보다 더 나빠지는지 lerobot `rtc` 모듈로 벤치마크. 실패 시 대안: Diffuser 식 덮어쓰기 인페인팅(성능은 낮지만 역전파 불필요, §A.4)으로 강등.
3. **접촉 구간에서의 freeze 유해성** — RTC 의 freeze 는 in-hand 조작 중 slip 이벤트에 대한 대응을 최소 $`d`$ 스텝 늦춥니다. Phase 1 인핸드 회전 시뮬(Isaac)에서 "RTC 유/무 × System0 유/무" 2×2 를 돌려, RTC 의 연속성 이득이 접촉 상황에서 유지되는지 / System0 없이 slip 이 늘어나는지 확인해야 합니다.
4. **전략 전환 관성** — soft masking 이 파지 실패 후 재시도(regrasp) 같은 급격한 전략 전환을 지연시키는지. 파지 실패를 유도한 시나리오에서 재시도까지의 평균 스텝 수를 RTC 유/무로 비교. 논문은 다봉 전환이 *필요 없는* 연속 과제 중심이라 이 리스크가 가려져 있을 수 있습니다.
5. **증거 범위의 한계** — 실기 증거는 parallel jaw gripper 양팔이고 시뮬은 2D Kinetix 입니다. 다지 핸드(고차원 액션, 접촉 다이내믹스)에서의 검증은 전무하므로, "RTC 가 다지 조작에서도 성능을 올린다"는 명제는 우리가 처음 검증하는 것으로 취급해야 합니다.
6. **위치 제어 전제** — 실기 결과는 위치 제어 + 저수준 컨트롤러 전제입니다. System0 가 토크/전류 레벨로 개입하는 우리 설계에서는 RTC(위치 chunk)와 System0(토크 개입)의 합성 지점에서 논문이 다루지 않은 상호작용이 생깁니다 — D14 인터페이스 설계 시 명시적으로 다뤄야 합니다.

---

## 💡 컨텍스트 제안

- **P1 §5 methodology base(non-pinned)에 추가 제안** — `RTC (Real-Time Chunking) | arXiv:2506.07339 | flow VLA 비동기 실시간 실행층; D5 제어율·chunk 설계의 지연 제약 근거 + D7 π lineage 배포 경로`. 핀 교체까지는 불요(아키텍처 기여가 아니라 실행층이므로 non-pinned 이 적절)하다고 판단합니다.
- **P3 D13/D14 rationale 보강 제안** — System0 요구 사양에 "System1 반응 지연 하한 $`d\cdot\Delta t`$ (RTC 기준 실기 120–320ms, arXiv:2506.07339)"를 인용 근거로 추가하면, System0 의 존재 이유가 외부 정량 근거로 받쳐집니다. Decision 변경은 아니며 근거 추가입니다.
- Decision v1 자체를 움직일 필요는 없습니다 — 본 논문은 D5/D7/D13/D14 의 현 선택과 모두 양립합니다.
