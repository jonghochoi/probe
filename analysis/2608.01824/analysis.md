# Paper Analysis — ReTouch: Empowering Contact-Rich Dexterous Manipulation with Online-Refined Tactile Prediction

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | ReTouch: Empowering Contact-Rich Dexterous Manipulation with Online-Refined Tactile Prediction |
| 저자 | Shiqi Zhang, Xin Zhang, Yedong Shen, Jiajun Deng, Yuxuan Gao, Sha Zhang, Yuan Zhang, Kaixue Long, Jiajia Wu, Jia Pan, Yao Li, Yanyong Zhang |
| 링크 | [arXiv:2608.01824](https://arxiv.org/abs/2608.01824) |
| 발행일 / 버전 | 2026-08-03 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-08-12 |
| 관련 Pillar | P2, P5, P1, P0 |
| 태그 | tactile, vla-arch, dexterity |

<!-- 모든 curl 호출 성공: arxiv.org/abs/2608.01824 (HTTP 200),
     arxiv.org/html/2608.01824 (HTTP 200). 그림 5장 모두 HTTP 200,
     최대 603,919 bytes 로 GitHub camo 프록시 상한(약 5 MB) 이내. -->

---

## 🧭 한 줄 요약 (TL;DR)

ReTouch는 다지 손의 조밀한 taxel 신호를 손가락별 5개 패치 구조로 인코딩하고, 미래 촉각 latent를 "한 번 예측하고 마는 forecast"가 아니라 실행 중 촉각 피드백으로 계속 갱신되는 **제어 상태(control state)** 로 다루는 π0 기반 VLA입니다. 실제 XHand–UR7e 플랫폼의 7개 접촉 집약적 과제에서 최강 베이스라인 대비 표준 조건 +18.4%p, 도전 조건 +23.8%p를 기록했습니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 다지 조작에서는 어느 손가락이 접촉했는지, 물체가 미끄러지는지, 다지 접촉이 안정적인지를 연속 추적해야 하는데 시각만으로는 접촉 위치·힘·파지 안정성을 신뢰성 있게 드러낼 수 없습니다. 손-물체 가림(occlusion)이 접촉 영역을 가리는 다지 조작에서 이 지각 공백이 특히 큽니다.
- **기존 접근의 한계 (표현)** — 다지 손은 조밀한 촉각 관찰을 만들지만 과제와 관련된 접촉은 특정 손가락·특정 지문 영역에 희소하게 국소화되어 있습니다. 기존 방법은 촉각을 평탄화해 범용 토큰으로 만들거나 손가락별 시간축 힘 이력을 압축해버려, 손가락 단위 공간 구조가 사라집니다.
- **기존 접근의 한계 (시간)** — 미끄러짐·접촉 이동·실행 오차 때문에 접촉 상태는 빠르게 변하므로, 액션 청크 시작 시점에 만든 미래 촉각 예측은 실행 도중 **낡아버립니다(stale)**. 기존 predictive-reactive 방법은 빠른 피드백을 행동 수정에만 쓰고 예측 자체를 고속 촉각 주기마다 재추정하지 않습니다.
- **본 논문의 가설** — 미래 촉각 예측을 고정된 forecast가 아니라 **재귀적으로 유지되는 제어 상태**로 두고 남은 행동과 함께 갱신하면, 접촉 변화와 실행 오차에 대한 강건성이 올라갑니다.
- **왜 지금 중요한가** — 촉각 VLA가 direct-fusion → reactive → predictive → predictive-reactive로 빠르게 계층화되는 국면에서, 남은 공백이 "예측 참조값 자체의 갱신 주기"라는 점을 정면으로 겨냥한 논문입니다.
- **우리 맥락의 의미** — P2(구조적 입력-모달리티 결합)의 손가락별 토큰 구성과 P5(World Model)의 latent 미래 예측 auxiliary를 한 스택 안에서 동시에 검증한, 드문 실제-로봇 사례입니다.

---

## 🧩 핵심 기여

- **Tactile-Patch Encoder** — 손가락당 120개 3축 force taxel을 tip / center / base / left / right 5개 기능적 패치로 나누고 finger-identity + patch-position 임베딩을 더해, 손가락 단위 접촉 topology를 보존한 채 프레임당 촉각 토큰을 5개로만 노출합니다.
- **3-head 인코더 사전학습** — 패치별 접촉 상태(BCE), contact-gated 평균 3D force(회귀), 패치 간 접촉 강도 분포(CE)를 손가락 토큰 하나에서 복원하도록 사전학습해, 압축 토큰이 국소 접촉 정보를 잃지 않도록 강제합니다.
- **Hindsight–Foresight 학습** — 학습 전용 특권 브랜치(HAE)가 정답 미래 촉각으로 만든 "행동에 유의미한" latent를 타깃으로 주고, 배포용 브랜치(FAE)가 현재 관찰만으로 그 latent를 예측하도록 stop-gradient cosine 정렬로 학습합니다. 고차원 taxel 재구성을 하지 않는 것이 설계 요점입니다.
- **온라인 촉각 예측 정제** — 9 Hz VLM 캐시 컨텍스트 위에서 FAE가 36 Hz로 돌며, 직전 호출의 latent 접두부를 이월받아 미래 촉각 latent와 남은 액션 청크를 **동시에** 갱신합니다. 방향성 어텐션 마스크로 촉각 예측이 항상 행동 생성보다 앞서도록 강제합니다.
- **XHT-Dataset + 실제 로봇 검증** — XHand–UR7e에서 7개 접촉 집약 과제 900개 실증 시연을 수집하고, 표준 조건 83.6% (최강 베이스라인 대비 +18.4%p), 도전 조건 73.1% (+23.8%p)를 폐루프 실제 로봇 평가로 보고합니다.

---

## 🔑 기술 키워드

- **Tactile-Patch Encoder** — 손가락 하나의 조밀한 taxel 배열을 "지문 부위별 5칸 서랍"으로 나눠 요약한 뒤 하나의 손가락 토큰으로 접는 인코더. 어느 부위가 얼마나 눌렸는지가 토큰 안에 남습니다.
- **Patch-Informed Tokenizer** — 패치별 국소 응답에 손가락 정체성·패치 위치 임베딩을 더해 투영하고, 5개 패치 특징을 하나의 손가락 토큰으로 집약하는 모듈.
- **Hindsight Action Expert (HAE)** — 학습 때만 존재하며 정답 미래 촉각을 볼 수 있는 특권 교사 브랜치. 행동 생성 목적함수로 최적화되므로 그 내부 표현이 곧 "행동에 유의미한 미래 촉각" 타깃이 됩니다.
- **Foresight Action Expert (FAE)** — 배포 시 남는 유일한 브랜치. 현재·과거 촉각과 캐시된 의미 컨텍스트만으로 미래 촉각 latent를 추론하고 액션 청크를 생성합니다.
- **Tactile Foresight Queries** — 미래 촉각 latent를 뽑아내는 학습 가능한 질의 토큰. 정제 단계에서는 경과분에 해당하는 접두부가 직전 예측으로 대체됩니다.
- **Online Tactile Prediction Refinement** — 미래 촉각 예측을 고정 forecast가 아니라 새 촉각 관찰이 들어올 때마다 갱신되는 실행 시점 상태로 유지하는 방식.
- **Directional Attention Mask** — 촉각 질의는 행동 토큰을 볼 수 없고 행동 토큰은 갱신된 촉각 latent를 볼 수 있게 하는 단방향 마스크. 행동 정보가 촉각 예측으로 새는 것을 막습니다.
- **Blocking Refinement** — 정제 결과가 돌아올 때까지 마지막 명령을 유지하는 실행 스케줄. 지연 반영을 허용하는 non-blocking 대안보다 7.8%p 높습니다.
- **Soft Contact Weight** — 힘 크기를 시그모이드에 통과시켜 얻는 연속 접촉 가중치. 이진 접촉 판정 대신 약한 접촉도 부드럽게 반영합니다.
- **XHT-Dataset** — XHand–UR7e 플랫폼에서 수집한 7개 접촉 집약 과제 900개 시연 집합. 시각·언어·로봇 상태·행동과 5지 조밀 촉각 스트림을 함께 담습니다.

---

## 🔬 방법론

### 직관

ReTouch가 겨냥하는 문제는 두 가지이고, 둘 다 "촉각을 어떻게 다루느냐"에 대한 것입니다. 첫째는 공간의 문제입니다. 다지 손의 촉각 센서는 손가락마다 수백 개의 값을 쏟아내지만, 실제로 과제를 좌우하는 접촉은 "엄지 끝이 미끄러진다" 같은 아주 국소적인 사건입니다. 이 신호를 통째로 평탄화해 하나의 벡터로 밀어 넣으면, 정책은 "지금 어딘가 눌렸다"는 것만 알 뿐 "어느 손가락 어느 부위가 눌렸는가"를 잃습니다. ReTouch는 손가락별로 지문면을 끝·중앙·기저·좌·우 다섯 구획으로 자르고, 각 구획의 접촉 통계를 뽑은 뒤 손가락 정체성과 구획 위치를 임베딩으로 붙입니다. 정책이 보는 것은 여전히 손가락당 토큰 하나뿐이지만, 그 토큰 안에는 다섯 구획의 접촉 분포가 복원 가능한 형태로 남아 있습니다.

둘째는 시간의 문제이고 이쪽이 논문의 본체입니다. 최근 촉각 정책들은 "앞으로 촉각이 어떻게 될지"를 예측해 행동 생성을 돕습니다. 그런데 이 예측은 보통 액션 청크가 시작될 때 한 번 만들어지고, 그 청크가 실행되는 동안 그대로 쓰입니다. 문제는 접촉 상태가 청크 길이보다 훨씬 빠르게 변한다는 점입니다. 물체가 미끄러지거나 손가락이 밀리면, 청크 시작 시점의 예측은 곧 현실과 어긋난 채로 남은 행동을 잘못된 방향으로 끌고 갑니다. 기존 predictive-reactive 방법도 빠른 촉각 피드백으로 *행동*은 다시 뽑지만, 그 행동이 참조하는 *예측*은 낡은 것 그대로입니다.

ReTouch의 답은 예측을 "예보"가 아니라 "상태"로 바꾸는 것입니다. 미래 촉각 latent를 실행 중 계속 들고 다니면서, 새 촉각 관찰이 들어올 때마다 이미 지나간 구간의 latent는 직전 예측을 그대로 이월하고 아직 오지 않은 구간만 다시 추론합니다. 그리고 그렇게 갱신된 예측을 조건으로 남은 행동을 다시 만듭니다. 이 갱신은 무거운 VLM을 다시 돌리지 않고 가벼운 액션 전문가만 재호출해서 이루어지므로, 시각-언어 추론은 9 Hz로, 촉각 예측과 행동 수정은 36 Hz로 분리되어 돌아갑니다.

마지막 장치는 "무엇을 예측할 것인가"에 대한 것입니다. 미래 taxel 값을 그대로 맞히는 것은 비싸고, 맞혀 봐야 행동에 쓸모없는 성분까지 포함합니다. 그래서 학습 시에만 정답 미래 촉각을 볼 수 있는 특권 브랜치(HAE)를 두고, 그 브랜치가 *행동 생성 목적함수로* 학습될 때 내부에 생기는 표현을 타깃으로 삼습니다. 행동을 잘 만들기 위해 필요한 만큼의 미래 촉각 정보만 자동으로 걸러지는 셈입니다. 배포용 브랜치(FAE)는 이 타깃을 코사인 거리로 따라가도록 학습되고, 실제 배포에서는 특권 브랜치가 통째로 제거됩니다.

### 아키텍처

![Figure 1 — ReTouch overview](https://arxiv.org/html/2608.01824/intro.png)

> "Figure 1: Overview of ReTouch. Left: the Tactile-Patch Encoder organizes raw dexterous-hand tactile signals into structured tactile patch features. Middle: fixed tactile forecasts can diverge from the actual contact state after slippage, while ReTouch continually refines tactile predictions using the latest tactile feedback and updates action chunks accordingly. Right: XHT-Dataset: seven real-world contact-rich tasks on XHand–UR7e under standard and challenging settings." (§1)
(한글 해설 — 가운데 패널이 논문 전체의 주장을 한 장으로 보여줍니다. 미끄러짐 이후 고정 forecast가 실제 접촉 상태에서 벌어지는 그림이 곧 "예측을 상태로 유지해야 한다"는 논거입니다.)

![Figure 2 — ReTouch framework](https://arxiv.org/html/2608.01824/framework.png)

> "Figure 2: Framework of ReTouch. The Tactile-Patch Encoder structures future tactile signals for a training-only Hindsight Action Expert, whose action-relevant targets supervise the deployable VLM–Foresight Action Expert (FAE) pathway. At deployment, the FAE refines future tactile latents and the remaining action chunk using cached VLM context and latest tactile feedback." (§3.1)
(한글 해설 — 학습 경로(HAE, 정답 미래 촉각 사용)와 배포 경로(VLM–FAE)가 분리되어 있고, 둘을 잇는 것이 latent 정렬 손실 하나라는 점이 이 그림의 핵심입니다.)

전체 실행 구조는 주파수 분리에서 출발합니다.

> "ReTouch decouples low-frequency vision-language reasoning from high-frequency tactile prediction and action updates during execution." (§3.1)
(한글 해설 — 시각-언어 추론과 촉각-행동 갱신을 같은 주기에 묶지 않겠다는 선언이며, 뒤따르는 캐시 컨텍스트 설계와 9 Hz / 36 Hz 분리가 모두 여기서 파생됩니다.)

- **저주파 경로 (VLM, 9 Hz)** — $`k`$ 번째 저주파 갱신에서 VLM이 의미 컨텍스트 $`c_{k}`$ 를 캐시하고, 청크 시작 시점 로봇 상태 $`s_{k}`$ 와 함께 이후 고주파 제어를 조건화합니다.
- **고주파 경로 (FAE, 36 Hz)** — 매 고주파 호출 $`t`$ 에서 FAE는 관찰된 촉각 컨텍스트 $`\mathcal{T}_{t}`$ 와 직전 호출에서 이월된 미래 촉각 latent를 받아, 정제된 $`\hat{Z}_{t}^{+}`$ 와 갱신된 액션 청크 $`\hat{A}_{t}`$ 를 함께 내놓습니다.
- **정책 인터페이스** — 시각은 손목 카메라 1대 + 고정 외부 카메라 2대이며, 모든 뷰는 종횡비 보존 패딩으로 `224×224` 로 리사이즈되고 $`[-1,1]`$ 로 정규화됩니다. 상태·행동 공간은 UR7e 관절 6 + XHand 관절 12 = 18차원 절대 관절 위치 명령입니다.
- **촉각 입력 텐서** — 프레임당 손가락 5개 × taxel 120개 × 3축, 즉 $`\tau_{t}\in\mathbb{R}^{5\times 120\times 3}`$ 이고, 직전 9프레임과 현재 프레임을 합친 10프레임 창을 씁니다.

$$\mathcal{T}_{t}=[\tau_{t-9},\ldots,\tau_{t}]\in\mathbb{R}^{10\times 5\times 120\times 3}.$$

### 아키텍처 — Tactile-Patch Encoder

패치 분할의 설계 의도는 다음 한 문장에 못 박혀 있습니다.

> "To preserve finger-wise local contact topology in dexterous-hand tactile signals, the Tactile-Patch Encoder partitions the 120 3D force taxels on each finger into five functional patches corresponding to the tip, center, base, left, and right regions." (§3.2)
(한글 해설 — 분할 기준이 학습된 클러스터가 아니라 손가락 해부학에 대응하는 *고정* 기능 영역이라는 점이 중요합니다. 즉 이 구조는 데이터에서 발견되는 것이 아니라 사전 지식으로 주입됩니다.)

taxel $`j`$ 의 3D force 읽기값을 $`\tau_{t}^{i,j}=(f_{x},f_{y},f_{z})`$, 패치 $`p`$ 에 배정된 taxel 집합을 $`\mathcal{P}_{i,p}`$ 라 할 때 패치 집약은 다음과 같습니다 (식 1).

```math
\begin{array}[]{rcl}u_{t}^{i,p}&=&\mathrm{Agg}\left(\{\tau_{t}^{i,j}\mid j\in\mathcal{P}_{i,p}\}\right)\\[2.0pt]
&=&\left[\bar{\tau}_{t}^{i,p};m_{t}^{i,p};a_{t}^{i,p};q_{t}^{i,p}\right].\end{array}
```

여기서 $`\bar{\tau}_{t}^{i,p}`$ 는 contact-gated 평균 3D force, $`m_{t}^{i,p}`$ 는 성분별 최대 절대 force, $`a_{t}^{i,p}`$ 와 $`q_{t}^{i,p}`$ 는 각각 접촉 면적과 접촉 강도입니다. 네 통계는 "얼마나 세게 / 어느 방향으로 / 얼마나 넓게 / 최대 얼마나" 를 한 벡터에 담는 구성으로, 이 네 축이 뒤에 나오는 3-head 사전학습의 복원 대상과 정확히 짝을 이룹니다.

부록의 구체 수식을 보면 이 통계들이 **경성 접촉 판정 없이** 계산된다는 점이 드러납니다 (식 10).

$$w_{j}=\sigma\!\left(\frac{\|\mathbf{f}_{j}\|_{2}-\theta_{c}}{\gamma_{c}}\right),\qquad W_{p}=\sum_{j\in\mathcal{I}_{p}}w_{j}.$$

각 taxel의 힘 크기를 임계 $`\theta_{c}`$ 기준 시그모이드에 통과시켜 연속 가중치를 만들고, 패치 단위 합 $`W_{p}`$ 를 얻습니다. 이렇게 하면 약한 접촉이 이진 임계에서 잘려나가지 않고 부드럽게 반영됩니다. 이 가중치로 계산되는 패치 통계는 다음과 같습니다 (식 11).

```math
\begin{aligned}
\bar{\mathbf{f}}_{p}&=\frac{\sum_{j\in\mathcal{I}_{p}}w_{j}\mathbf{f}_{j}}{\max(W_{p},\epsilon)}, &\qquad \mathbf{m}_{p}&=\mathrm{max}_{j\in\mathcal{I}_{p}}|\mathbf{f}_{j}|,\\
a_{p}&=\frac{W_{p}}{|\mathcal{I}_{p}|}, &\qquad q_{p}&=\max_{j\in\mathcal{I}_{p}}\|\mathbf{f}_{j}\|_{2},
\end{aligned}
```

접촉 면적 $`a_{p}`$ 가 "가중치 합 / taxel 수"로 정의된다는 점이 중요합니다. 절대 면적이 아니라 패치 내 활성 비율이므로, 센서 해상도가 달라도 스케일이 보존됩니다. 하이퍼파라미터는 인코더 사전학습 시 $`\theta_{c}=0.5`$, 정책 학습 시 $`\theta_{c}=1.0`$ 이며 $`\gamma_{c}=0.5`$, $`\epsilon=10^{-6}`$ 입니다. 사전학습에서 임계를 낮게 잡아 약한 접촉까지 학습시키고, 정책 학습에서는 높여 잡음을 거르는 2단 구성입니다.

![Figure 6 — XHand taxel-to-patch maps](https://arxiv.org/html/2608.01824/finger_patch.png)

> "Figure 6: Fixed XHand taxel-to-patch maps for (a) the T30 thumb sensor and (b) the T16 sensors used by the other four fingers. Each color denotes one spatial patch." (§A.2)
(한글 해설 — 엄지는 T30, 나머지 네 손가락은 T16으로 센서 배치가 다르지만 패치 수는 5로 통일되어 있어, 하드웨어 이질성이 토큰 포맷 아래로 흡수됩니다.)

패치 특징에서 손가락 토큰으로 가는 집약은 학습된 어텐션 풀링입니다 (식 12).

```math
\begin{aligned}
e_{p}&=g\!\left(\mathrm{SiLU}(\mathbf{h}_{p})\right)+\log(a_{p}+\epsilon),\\
\alpha_{p}&=\frac{\exp(e_{p})}{\sum_{r=1}^{5}\exp(e_{r})},\qquad p=1,\ldots,5,\\
\mathbf{z}&=\mathrm{LN}\!\left(\sum_{p=1}^{5}\alpha_{p}\mathbf{h}_{p}\right).
\end{aligned}
```

풀링 로짓에 $`\log(a_{p}+\epsilon)`$ 항이 더해지는 것이 이 식의 요점입니다. 접촉 면적이 큰 패치에 로그 스케일로 사전 편향을 주어, 학습 초기부터 "실제로 닿은 구획"에 가중이 쏠리도록 유도합니다. 서술자 투영은 $`8\!\rightarrow\!256\!\rightarrow\!1024`$ SiLU MLP이고, 시간축으로는 학습된 스칼라 가중치로 직전 9프레임을 손가락별로 풀링한 뒤 현재 프레임 토큰은 history / current 타입 임베딩을 따로 붙여 유지해 총 10개 입력 토큰을 만듭니다. Hindsight 인코딩에서는 4스텝짜리 연속 구간 4개가 20개의 미래 촉각 토큰을 만듭니다.

토큰 예산 측면에서 이 설계의 결론은 다음 문장입니다.

> "This design preserves finger-wise local contact topology while exposing only five tactile tokens per frame to the policy." (§3.2)
(한글 해설 — 구조 보존과 토큰 예산을 동시에 만족시켰다는 주장이며, 이후 "w/o Tactile-Patch Encoder" ablation의 -14.5%p가 이 문장의 실험적 근거가 됩니다.)

### 학습 목표 / 손실 — 인코더 사전학습

압축 토큰이 국소 정보를 실제로 담고 있는지를 강제하는 장치가 3-head 사전학습입니다.

> "To encourage each compact finger token to retain recoverable contact information from all five regions, we pretrain the Tactile-Patch Encoder with three prediction heads." (§3.2)
(한글 해설 — 5개 패치를 토큰 1개로 접었을 때 정보가 살아남는지를 "복원 가능한가"로 검증하겠다는 것이며, 세 헤드는 각각 분포·힘·접촉이라는 서로 다른 축을 맡습니다.)

세 헤드는 손가락 토큰 하나에서 (a) 패치 간 상대 접촉 강도 분포, (b) 패치별 contact-gated 평균 3D force, (c) 패치별 접촉 상태를 예측하며 각각 cross-entropy, force regression, binary cross-entropy로 학습됩니다 (식 2).

$$\mathcal{L}_{\mathrm{TPE}}=\lambda_{\mathrm{dist}}\mathcal{L}_{\mathrm{CE}}+\lambda_{\mathrm{force}}\mathcal{L}_{\mathrm{force}}+\lambda_{\mathrm{contact}}\mathcal{L}_{\mathrm{BCE}}.$$

접촉 타깃은 $`y_{p}=\mathbf{1}(q_{p}>\theta_{c})`$ 이고, 분포 타깃은 $`y_{p}q_{p}`$ 를 패치 간 정규화하되 활성 패치가 하나도 없으면 균등 분포를 씁니다. 접촉 손실 가중치는 $`0.5`$ 이며, force 항은 세 개의 Smooth-$`L_{1}`$ 항으로 분해됩니다 (식 13).

$$\mathcal{L}_{\mathrm{force}}=\mathcal{L}_{\mathrm{active}}+0.5\,\mathcal{L}_{\mathrm{magnitude}}+0.25\,\mathcal{L}_{\mathrm{inactive}},$$

각각 활성 패치의 force 벡터, 활성 패치의 force 크기, 비활성 패치의 0 force를 회귀하며 활성/비활성 패치는 따로 정규화됩니다. 접촉 데이터는 대부분의 패치가 비접촉이라는 극단적 불균형을 갖는데, 비활성 항 가중치를 $`0.25`$ 로 낮추고 정규화를 분리한 것이 그 대응입니다. 사전학습이 끝나면 세 헤드는 버려지고 인코더 가중치만 정책 모델 초기화에 쓰인 뒤 정책과 함께 end-to-end 최적화됩니다.

### 학습 목표 / 손실 — Hindsight–Foresight 정렬

예측 대상을 taxel이 아니라 latent로 잡은 이유가 다음 문장에 있습니다.

> "Given the structured tactile patch features, we learn future tactile latents that capture contact information relevant to action generation, without reconstructing high-dimensional taxel-level future signals." (§3.3)
(한글 해설 — 미래 촉각을 픽셀 단위로 맞히는 세계 모델 계열과 갈라지는 지점입니다. 행동에 쓰이는 성분만 남기겠다는 선택이고, 그 "쓰이는 성분"을 사람이 정의하지 않고 행동 손실이 정의하게 만든 것이 다음 장치입니다.)

HAE는 정답 미래 촉각에 접근하는 특권 학습 브랜치입니다. 정렬 레이어 $`\ell`$ 에서 hindsight 타깃을 뽑습니다 (식 3).

$$Z_{t,\ell}^{+,\mathrm{hid}}=\mathrm{HAE}_{\ell}\big(c_{k},s_{k},\mathcal{T}_{t},E_{\phi}(\tau_{t:t+H}^{+})\big),$$

여기서 $`\tau_{t:t+H}^{+}`$ 는 지평 $`H`$ 에 걸친 정답 촉각 시퀀스이며 학습 시에만 사용 가능합니다. 이 타깃이 "행동에 유의미"한 이유는 다음과 같습니다.

> "Because the HAE is optimized with the action generation objective, its future tactile representations capture contact information relevant to subsequent actions." (§3.3)
(한글 해설 — 타깃의 유용성을 별도 손실로 정의하지 않고, 행동 손실로 학습된 표현을 그대로 타깃으로 쓴다는 우회가 이 설계의 핵심 트릭입니다. 사람이 "어떤 촉각 정보가 중요한가"를 손으로 지정할 필요가 없어집니다.)

FAE는 배포 가능한 조건화 경로만 씁니다. 학습 가능한 Tactile Foresight Queries $`Q^{\mathrm{fore}}`$ 로 미래 촉각 latent를 추론합니다 (식 4).

$$\hat{Z}_{t,\ell}^{+}=\mathrm{FAE}_{\ell}\big(c_{k},s_{k},\mathcal{T}_{t},Q^{\mathrm{fore}}\big).$$

두 latent의 정렬은 stop-gradient가 걸린 코사인 거리입니다 (식 5).

$$\mathcal{L}_{\mathrm{align}}=d_{\mathrm{cos}}\big(g_{\psi}(\hat{Z}_{t,\ell}^{+}),\mathrm{sg}(Z_{t,\ell}^{+,\mathrm{hid}})\big),$$

$`g_{\psi}`$ 는 FAE 표현을 HAE latent 공간으로 보내는 투영, $`d_{\mathrm{cos}}`$ 는 평균 코사인 거리, $`\mathrm{sg}(\cdot)`$ 는 stop-gradient입니다. stop-gradient가 없으면 HAE 타깃이 FAE가 맞히기 쉬운 쪽으로 붕괴할 수 있으므로, 이 항은 선택이 아니라 필수 장치입니다. 구현상 HAE와 FAE는 각각 18-layer Transformer(hidden width 1024, 8 head)이고 정렬 레이어는 $`\ell=12`$, 투영기는 $`1024\!\rightarrow\!1024\!\rightarrow\!1024`$ SiLU MLP, 정렬 가중치는 $`0.1`$ 입니다.

> "During deployment, both the HAE and the alignment projector are removed, and only the FAE is retained for inference." (§3.3)
(한글 해설 — 배포 비용에는 특권 브랜치가 전혀 실리지 않습니다. 대신 학습 시에는 18-layer Transformer 두 개를 동시에 돌려야 하므로 학습 측 비용이 두 배 가까이 듭니다.)

### 아키텍처 — 온라인 정제 루프

> "ReTouch therefore maintains future tactile latents as execution-time states that are continually refined using incoming tactile feedback." (§3.4)
(한글 해설 — 논문의 명제를 한 문장으로 담은 앵커입니다. "예측"이라는 명사를 "상태"로 바꾸는 것이 곧 기여이며, 이후 모든 ablation이 이 문장을 검증합니다.)

초기 호출 이후의 질의 구성은 마스크 혼합입니다 (식 6).

$$\widetilde{Q}_{t}^{\mathrm{fore}}=M_{t}\odot\mathrm{sg}\big(\hat{Z}_{t-1}^{+}\big)+(1-M_{t})\odot Q^{\mathrm{fore}},$$

$`M_{t}`$ 는 액션 청크에서 이미 경과한 구간에 해당하는 latent 접두부를 선택합니다. 즉 지나간 구간은 직전 예측을 그대로 이월(stop-gradient)하고, 남은 구간만 학습된 질의로 다시 추론합니다. 초기 호출에서는 $`M_{t}=0`$ 이므로 전부 $`Q^{\mathrm{fore}}`$ 에서 시작합니다. 예측과 행동의 동시 갱신은 다음과 같습니다 (식 7).

$$\big(\hat{Z}_{t}^{+},\hat{A}_{t}\big)=\mathrm{FAE}_{\theta}\big(c_{k},s_{k},\mathcal{T}_{t},\widetilde{Q}_{t}^{\mathrm{fore}}\big),$$

한 번의 FAE 호출이 정제된 촉각 latent와 갱신된 액션 청크를 동시에 내놓는다는 점이 "predictive-reactive" 계열과의 분기점입니다. 이때 순서를 강제하는 것이 방향성 마스크입니다.

> "The Tactile Foresight Queries can attend to the cached semantic context, robot state, observed tactile context, and carried-over latent prefix, but not to action tokens." (§3.4)
(한글 해설 — 촉각 예측이 행동 토큰을 보지 못하게 막아, 같은 호출 안에서 촉각 예측이 먼저 결정되고 행동이 그것을 참조하는 인과 순서를 만듭니다. 반대로 두면 행동 정보가 촉각 latent로 새어 예측이 자기충족적으로 변합니다.)

학습과 배포는 같은 비동기 스킴을 씁니다. 학습 시 액션 청크 내부에서 임의의 offset을 샘플링해 그 시점의 촉각 컨텍스트·이월 latent 접두부·행동 감독을 구성하고, 배포 시에는 고주파 제어율로 FAE를 반복 호출합니다.

> "Each invocation regenerates the action chunk, but only the unexecuted suffix after the current offset is applied." (§3.4)
(한글 해설 — 매번 16스텝 전체를 재생성하되 실행된 접두부는 버리므로, 청크 경계와 정렬이 유지된 채 남은 구간만 교체됩니다.)

구체적으로 액션 청크는 $`\hat{A}^{(o)}_{t}\in\mathbb{R}^{16\times 18}`$ 이고, offset $`o\in\{4,8,12\}`$ 에서 재생성되며 $`\hat{A}^{(o)}_{t}[o{:}16]`$ 만 적용됩니다. 실행 스케줄은 blocking입니다.

> "Full ReTouch uses blocking refinement: at each update offset, execution holds the last command until the updated action chunk is returned." (§A.3)
(한글 해설 — 정제 결과를 기다리며 마지막 명령을 유지하는 방식이고, 이 선택이 non-blocking 대비 7.8%p를 만듭니다. 즉 "언제 반영되는가"가 성능에 직접 걸려 있습니다.)

주파수는 다음과 같이 실측에서 유도된 값입니다.

> "With one full VLM–FAE pass and three cached-context FAE refinements per cycle, the measured latencies correspond to 9.02 complete cycles and 36.08 FAE passes per second, reported as 9 Hz and 36 Hz in the main text." (§A.4)
(한글 해설 — 9 Hz / 36 Hz는 설계 목표치가 아니라 RTX 5090 실측 지연에서 역산된 수치이며, 통신·명령 실행·컨트롤러 스케줄링 오버헤드는 제외되어 있습니다.)

### 학습 목표 / 손실 — 정책 전체

정책 학습은 두 전문가의 flow matching, 미래 촉각 latent 정렬, 임의 offset 갱신 목적을 함께 최적화합니다 (식 8).

$$\mathcal{L}_{\mathrm{policy}}=\mathcal{L}_{\mathrm{act}}^{\mathrm{hid}}+\mathcal{L}_{\mathrm{act}}^{\mathrm{fore}}+\lambda_{\mathrm{align}}\mathcal{L}_{\mathrm{align}}+\mathcal{L}_{\mathrm{update}}.$$

$`\mathcal{L}_{\mathrm{update}}`$ 는 임의 중간 offset에서 행동과 latent 정렬 감독을 적용하는 항으로, 학습 분포와 배포 시 실행 상태를 일치시키는 역할을 합니다. Hindsight 타깃에는 stop-gradient가 걸려 정렬 목적이 hindsight 표현으로 역전파되지 않습니다.

행동 생성은 π 계열 flow matching입니다. 정규화된 액션 청크 $`a`$ 에 대해 $`\varepsilon\sim\mathcal{N}(0,I)`$ 와 $`t=0.001+0.999\tilde{t}`$ ($`\tilde{t}\sim\mathrm{Beta}(1.5,1)`$)를 샘플링하고, $`x_{t}=t\varepsilon+(1-t)a`$, $`u=\varepsilon-a`$ 로 두어 HAE와 FAE가 같은 $`(x_{t},t)`$ 를 받아 $`u`$ 를 MSE로 회귀합니다. 추론은 $`t=1`$ 에서 $`0`$ 까지 10-step explicit Euler이며, **같은 청크 내 모든 정제 호출은 초기 action-noise 샘플을 재사용합니다** — 이 재사용이 없으면 정제마다 다른 노이즈에서 출발해 궤적이 튀게 됩니다.

### 학습 셋업

- **2단 학습** — Tactile-Patch Encoder를 20k step 사전학습 → 세 헤드 제거 → 두 Action Expert의 (구조는 동일하나 파라미터는 독립인) 인코더를 사전학습 가중치로 초기화 → 정책과 end-to-end 최적화. 인코더는 정책 학습 첫 5k step 동안 동결 후 해제됩니다.
- **정책 학습** — 7개 과제 전체에 대해 단일 정책을 80k step 공동 학습. 액션 지평 16 step, 촉각 이력 창 9프레임(현재 포함 10프레임), 학습 시 청크 내부 offset을 $`\{4, 8, 12\}`$ 에서 균등 샘플링.
- **최적화** — 인코더 사전학습 / 정책 학습 global batch size 각각 32 / 8. AdamW, gradient clipping 1.0, warmup 1k step, cosine decay $`2.5\times 10^{-5}\rightarrow2.5\times 10^{-6}`$. NVIDIA A800 8장, bfloat16 mixed precision.
- **증강** — 세 뷰 모두 brightness / contrast / saturation 강도 $`0.3`$ / $`0.4`$ / $`0.5`$ color jitter. base view로 지정된 외부 뷰 1개에만 면적 95% 유지 random crop과 $`\pm 5^{\circ}`$ random rotation 추가.
- **백본** — π0 사전학습 체크포인트에서 초기화.

> "ReTouch is initialized from a pretrained $`\pi_{0}`$ checkpoint and fine-tuned during policy training." (§A.1)
(한글 해설 — VLM 동결이 아니라 정책 학습 중 fine-tune입니다. 사전학습 prior 보존에 대한 별도 측정은 논문에 없습니다.)

- **데이터 분할** — XHT-Dataset 900개 중 100개 궤적을 held-out offline test set으로 떼어내고(인코더 사전학습·정책 학습 모두에서 제외) 나머지 800개를 공통 학습 풀로 씁니다. 분할은 촉각 창·액션 청크 샘플링 이전에 궤적 수준에서 정의됩니다.
- **데이터 수집 리그** — UR7e 팔 + XHand 5지 손, 손목 카메라 1대 + 고정 외부 카메라 2대. 원격조작 시 VIVE tracker가 손목 자세 목표를, MANUS glove가 손가락 동작을 기록합니다.

---

## 📊 실험 설정과 결과

### 평가 프로토콜

방법당 과제별 20회 실제 로봇 시행이며, 주 지표는 정규화 과제 점수(%)입니다. 여기서 **"성공률"의 정의가 통상적 이진 성공률이 아니라는 점**은 결과 해석에 결정적입니다.

> "Accordingly, “Success Rate” in the main paper denotes the mean normalized task score (%); except for Button Press, it is a graded task-completion score rather than binary completion frequency." (§B.3)
(한글 해설 — Button Press를 제외한 6개 과제는 단계별 부분 점수 합입니다. 예컨대 Bottle Grasp는 15 cm 이상 들어 올리면 0.5, 3초 유지하면 추가 0.5입니다. 부분 점수는 완전 실패와 절반 성공을 구분해 주지만, 이진 성공률과 직접 비교하면 마진이 과대평가됩니다.)

앞 5개 과제는 60초, Liquid Transfer와 Cabinet Retrieval은 120초 타임아웃이며, 타임아웃 내 재시도·재파지는 사람 개입 없이 허용됩니다. 채점은 현장에서 단일 평가자가 고정 rubric으로 수행합니다.

### 표준 조건 주 결과 (Table 1)

| Method | Pipette Press | Bottle Grasp | Cob Grasp | Sponge Wipe | Button Press | Cabinet Retrieval | Liquid Transfer | Avg. |
|---|---|---|---|---|---|---|---|---|
| RDP | 46.5 | 65.0 | 45.0 | 50.0 | 5.0 | 10.0 | 0.0 | 31.6 |
| ViTacFormer | 66.5 | 25.0 | 35.5 | 17.5 | 20.0 | **67.5** | 0.0 | 33.1 |
| $`\pi_{0}`$ | 12.5 | 80.0 | 80.0 | 10.0 | 65.0 | 35.5 | 36.5 | 45.6 |
| $`\pi_{0}`$ + tactile | 31.5 | 52.5 | 87.5 | 25.0 | 45.0 | 37.5 | 27.5 | 43.8 |
| $`\pi_{0.5}`$ | 29.5 | 75.0 | 82.5 | 35.0 | 45.0 | 47.5 | 46.0 | 51.5 |
| $`\pi_{0.5}`$ + tactile | 47.0 | 60.0 | 92.0 | 20.0 | 60.0 | 42.5 | 50.0 | 53.1 |
| Tactile-VLA | 84.5 | 82.5 | 95.5 | 62.5 | **85.0** | 5.0 | 41.5 | 65.2 |
| **ReTouch (Ours)** | **86.0** | **95.0** | **100.0** | **87.5** | **85.0** | 62.5 | **69.0** | **83.6** |

> "ReTouch achieves the highest macro-average success rate of 83.6%, outperforming Tactile-VLA, the strongest single baseline on average, by 18.4 percentage points." (§4.2, Table 1)
(한글 해설 — 7개 중 5개에서 1위, Button Press 공동 1위이며 Cabinet Retrieval 하나만 ViTacFormer(67.5)에 62.5로 뒤집니다. 저자도 이 과제를 예외로 명시합니다.)

가장 결정적인 관찰은 우리 D10(flat concat을 넘어선 이질 모달리티 융합) 논거와 직결됩니다.

> "First, directly adding tactile observations to pretrained VLA baselines has inconsistent effects: the average success rate of $`\pi_{0}`$ decreases from 45.6% to 43.8%, whereas that of $`\pi_{0.5}`$ increases from 51.5% to 53.1%." (§4.2, Table 1)
(한글 해설 — 촉각을 평탄화해 proprioception에 concat하기만 하면 오히려 성능이 떨어질 수 있다는 실측입니다. "촉각을 넣는 것"과 "촉각을 구조적으로 넣는 것"의 차이가 부호를 바꾸는 수준이라는 점이 이 표의 가장 값비싼 정보입니다.)

또 하나 눈여겨볼 것은 베이스라인들의 극단적 과제 의존성입니다. ViTacFormer는 Cabinet Retrieval에서 67.5로 최고인데 Bottle Grasp에서는 25.0, Liquid Transfer에서는 0.0입니다. Tactile-VLA는 정반대로 Cabinet Retrieval에서 5.0으로 붕괴합니다. 즉 이 벤치마크에서 "평균 최강 베이스라인"은 과제별로 존재하지 않으며, ReTouch의 진짜 주장은 최고점이 아니라 분산 축소에 가깝습니다.

### 도전 조건 (Table 2)

| Method | Height (Sponge) | Position (Cob) | Lighting (Liquid) | Pull (Bottle) | Avg. |
|---|---|---|---|---|---|
| ViTacFormer | 0.0 | 24.5 | 1.5 | 5.0 | 7.8 |
| RDP | 0.0 | 10.0 | 0.0 | 30.0 | 10.0 |
| Tactile-VLA | 25.0 | 30.5 | 39.5 | 45.0 | 35.0 |
| $`\pi_{0.5}`$ | 12.5 | 86.0 | 40.0 | 50.0 | 47.1 |
| $`\pi_{0.5}`$ + tactile | 15.0 | 80.5 | 46.5 | 55.0 | 49.3 |
| **ReTouch** | **42.5** | **98.5** | **66.5** | **85.0** | **73.1** |

각 열이 서로 다른 실패 축을 분리합니다. Height는 학습 높이 7.5 / 9 / 10.5 cm에 대해 held-out 2.5 / 5 cm로 접촉 기하를 바꾸고, Position은 학습 영역 밖 위치, Lighting은 프로젝터로 만든 동적 조명(시각만 교란), Pull은 안정 파지 후 사람이 아래로 잡아당겨 물체를 빼내고 자율 재파지를 요구합니다.

> "The largest gain occurs under post-grasp pulling disturbances, where ReTouch achieves 85.0%, exceeding the strongest baseline at 55.0% by 30.0 percentage points." (§4.3, Table 2)
(한글 해설 — 파지 확립 이후 손가락 힘 분포를 직접 흔드는 교란이며, 설계 동기와 가장 정확히 맞물리는 열입니다. 반대로 Height 열은 42.5로 절대값이 낮아, 접촉 기하가 학습 분포를 벗어나면 여전히 절반 이상 실패합니다.)

Lighting 열(66.5 vs 46.5, +20.0%p)은 촉각이 시각 교란에 대한 대체 정보원으로 작동한다는 근거이지만, 도전 조건 전반에서 ViTacFormer(7.8)와 RDP(10.0)가 사실상 붕괴한다는 점도 함께 읽어야 합니다. 이 두 베이스라인은 과제별로 따로 학습된 task-specific 정책이라 분포 이동에 원래 취약합니다.

### Ablation (Table 3)

| Variant | Pipette Press | Bottle Grasp | Cob Grasp | Sponge Wipe | Button Press | Cabinet Retrieval | Liquid Transfer | Avg. |
|---|---|---|---|---|---|---|---|---|
| Full ReTouch | 86.0 | **95.0** | **100.0** | **87.5** | 85.0 | **62.5** | 69.0 | **83.6** (0.0) |
| w/o intra-chunk refinement | 74.0 | 62.5 | 95.0 | **87.5** | 40.0 | 22.5 | 38.5 | 60.0 (-23.6) |
| w/o tactile-prediction refinement | 83.0 | 85.0 | 83.0 | 82.5 | **90.0** | 32.5 | 22.5 | 68.4 (-15.2) |
| w/o future tactile prediction | 68.0 | 87.5 | 84.5 | 65.0 | 80.0 | 50.0 | 38.0 | 67.6 (-16.0) |
| non-blocking joint refinement | **94.0** | 80.0 | 98.5 | 85.0 | 65.0 | 45.0 | 63.0 | 75.8 (-7.8) |
| w/o Tactile-Patch Encoder | 56.5 | 87.5 | 95.5 | 52.5 | 75.0 | 40.0 | **76.5** | 69.1 (-14.5) |

각 행이 무엇을 분리하는지 한 줄씩 읽으면 다음과 같습니다.

- **w/o intra-chunk refinement (-23.6%p)** — 청크 내부 갱신을 통째로 제거해 청크 시작 시점의 예측·행동만으로 16스텝을 끝까지 실행합니다. 가장 큰 하락이지만, 이 변형은 촉각 정제와 행동 재추론을 *동시에* 없애므로 두 효과가 섞여 있습니다.

  > "Removing intra-chunk refinement of both tactile predictions and actions causes the largest degradation, reducing the average success rate by 23.6 percentage points." (§4.4, Table 3)
  (한글 해설 — 이 숫자는 "청크 내부에서 무언가를 다시 하는 것"의 총 가치이지, 촉각 latent 정제만의 기여가 아닙니다.)

- **w/o tactile-prediction refinement (-15.2%p)** — 행동 재추론은 유지하되 촉각 예측만 청크 시작 값으로 고정합니다. 위 행과의 차이(60.0 → 68.4)가 "행동 재추론만의 가치 8.4%p", 이 행과 full의 차이(15.2%p)가 "촉각 정제만의 가치"에 해당합니다.
- **w/o future tactile prediction (-16.0%p)** — 미래 촉각 토큰과 정렬 손실을 통째로 제거하고 촉각 조건 행동 갱신만 남깁니다. 앞 행(68.4)과 0.8점 차이라는 점이 논문의 가장 날카로운 관찰입니다.

  > "The 0.8-point difference suggests that a fixed one-shot tactile prediction provides limited benefit and that the main gain comes from continually refining future tactile predictions with the latest feedback." (§4.4, Table 3)
  (한글 해설 — 고정된 미래 촉각 예측은 없는 것과 거의 같다는 뜻입니다. 촉각 예측 모듈을 붙였는데 갱신하지 않는 설계는 계산만 늘리고 이득이 없다는, 설계 선택에 직접 쓰이는 결론입니다.)

- **non-blocking joint refinement (-7.8%p)** — 실행을 멈추지 않고 병렬로 갱신해 결과가 약 한 스텝 늦게 반영됩니다. 체크포인트는 full과 동일하고 실행 스케줄만 다릅니다. 즉 7.8%p는 순수하게 **반영 지연 1스텝의 비용**입니다.
- **w/o Tactile-Patch Encoder (-14.5%p)** — 구조화 인코더를 raw 촉각 평탄화 + MLP로 대체합니다.

  > "This variant reduces the average success rate by 14.5 percentage points to 69.1%, supporting the benefit of preserving finger identity and local contact regions in tactile representations." (§4.4, Table 3)
  (한글 해설 — 나머지 아키텍처를 모두 유지한 채 토큰 구성만 바꾼 통제된 비교이며, D11/D12의 구조적 토큰 구성 주장에 가장 직접적인 근거입니다. 다만 Liquid Transfer에서는 이 변형이 76.5로 full(69.0)을 앞섭니다.)

### 구조화 인코딩 진단 (Figure 4, Table 5)

![Figure 4 — patch-wise force reconstruction](https://arxiv.org/html/2608.01824/figure4.png)

> "Figure 4: Example of structured tactile patch encoding across the five fingers. Ground-truth values are patch-wise magnitudes of contact-strength-weighted mean forces; predicted values are reconstructed from the corresponding finger-level tactile tokens by the tactile-summary head." (§4.2)
(한글 해설 — 손가락 토큰 하나에서 5개 패치 힘을 되살릴 수 있다는 것이 압축 손실이 작다는 시각적 증거입니다.)

사전학습 구성 비교(held-out offline test set):

| Category | Metric | Single-head (Force only) | Balanced three-head (Contact + Force + Distribution) |
|---|---|---|---|
| Contact prediction | Contact F1 ↑ | 0.9980 | **0.9999** |
| Patch distribution | Canonical patch-distribution KL ↓ | 0.1648 | **0.0048** |
| Patch force reconstruction | Active-force vector L2 ↓ | 2.1939 | **0.8801** |
| Patch force reconstruction | Active-force direction cosine ↑ | 0.4089 | **0.8071** |
| Patch force reconstruction | Inactive-force magnitude ↓ | **0.0094** | 0.0260 |
| Patch force reconstruction | Force-strength Pearson correlation ↑ | 0.7878 | **0.8643** |

가장 큰 격차는 방향 코사인(0.4089 → 0.8071)과 분포 KL(0.1648 → 0.0048)입니다. 힘 하나만 회귀시키면 크기는 맞히지만 **방향**은 절반도 못 맞힌다는 뜻이고, 미끄러짐 판단이 접선 방향 힘에 실린다는 점을 생각하면 이 항목은 단순한 지표 개선이 아닙니다. 반대로 비활성 패치 크기만은 single-head가 낫습니다(0.0094 vs 0.0260) — 힘만 회귀하면 "안 닿은 곳은 0"을 더 깨끗하게 학습하기 때문입니다. 저자는 이 진단의 범위를 스스로 제한합니다.

> "This diagnostic evaluates encoder pretraining quality and does not by itself establish downstream manipulation gains." (§D.2)
(한글 해설 — 인코더 품질과 조작 성능 사이의 연결은 이 표가 아니라 Table 3의 -14.5%p 행이 담당한다는 자기 한정입니다.)

### 재귀 정제의 격리 진단 (Figure 5, Table 6)

![Figure 5 — refinement effect across contact phases](https://arxiv.org/html/2608.01824/figure5.png)

> "Figure 5: Effect of online refinement of future tactile predictions across contact phases on future tactile latent similarity (top) and remaining-action MSE (bottom). Results at $`t_{0}`$ are omitted since both methods are identical before refinement." (§4.2)
(한글 해설 — 접촉 이전에는 두 방식이 사실상 동일하고, 접촉 이후에만 격차가 벌어지며 갱신 횟수와 함께 커진다는 것이 이 그림의 주장입니다.)

| Phase | Metric | One-shot | ReTouch | $`\Delta_{\mathrm{avg}}`$ | $`\Delta_{4}`$ | $`\Delta_{8}`$ | $`\Delta_{12}`$ |
|---|---|---|---|---|---|---|---|
| Pre-contact | Latent cosine ↑ | **0.98542** | 0.98506 | -0.037% | +0.011% | +0.023% | -0.149% |
| Pre-contact | Action-suffix MSE ↓ | 0.01435 | **0.01433** | +0.134% | +0.196% | -0.108% | +0.327% |
| Pre-contact | Arm-suffix MSE ↓ | **0.00221** | 0.00222 | -0.427% | -0.133% | -0.543% | -0.554% |
| Pre-contact | Hand-suffix MSE ↓ | 0.02042 | **0.02039** | +0.165% | +0.211% | -0.085% | +0.385% |
| In-contact | Latent cosine ↑ | 0.93879 | **0.94732** | +0.908% | +0.693% | +1.148% | +0.880% |
| In-contact | Action-suffix MSE ↓ | 0.02100 | **0.02055** | +2.139% | +1.317% | +2.074% | +2.764% |
| In-contact | Arm-suffix MSE ↓ | **0.00339** | 0.00340 | -0.196% | -0.099% | -0.243% | -0.221% |
| In-contact | Hand-suffix MSE ↓ | 0.02981 | **0.02913** | +2.272% | +1.395% | +2.205% | +2.937% |

부호 규약은 "양수 = 선호 방향으로의 변화"입니다. 접촉 시작은 임의의 3축 taxel 벡터 $`L_{2}`$ 크기가 데이터셋 고유 단위로 $`\theta_{\mathrm{onset}}=1.0`$ 을 넘는 최초 프레임으로 정의되며 시간적 지속 조건은 적용하지 않습니다.

> "After contact, ReTouch continually revises its future predictions using tactile feedback, improving the mean latent cosine similarity by 0.908% and reducing the overall action error by 2.139% relative to the one-shot variant." (§4.2)
(한글 해설 — 실제 로봇 ablation의 15.2%p와 대비하면 격리 진단의 효과 크기는 두 자릿수가 아니라 소수점 수준입니다. 이 간극을 논문은 조정하지 않으며, 아래 ⚖️ 한계에서 다시 다룹니다.)

우리 스택 관점에서 이 표의 가장 값진 행은 arm / hand 분해입니다. 재귀 정제는 **hand-suffix MSE만 개선**하고(in-contact +2.272%) arm-suffix MSE는 두 위상 모두에서 오히려 악화시킵니다(in-contact -0.196%, pre-contact -0.427%). 촉각 피드백이 손가락 자유도에는 유효 신호이고 팔 자유도에는 잡음에 가깝다는, Body/Hand 분리 설계에 직접 쓰이는 증거입니다.

### 지연 (Table 4)

| Inference stage | Latency (ms) |
|---|---|
| Initial VLM–FAE pass | 52.25 |
| Cached-context FAE refinement | 19.54 |

전체 VLM–FAE 1회 + 캐시 컨텍스트 FAE 정제 3회가 한 주기이며, 이 실측이 9 Hz / 36 Hz의 근거입니다. 다만 통신·명령 실행·컨트롤러 측 스케줄링 오버헤드는 제외된 모델 계산 시간만의 값입니다.

### 데이터

> "XHT-Dataset contains 900 successful demonstrations across the seven tasks. We hold out 100 trajectories as a held-out offline test set, excluding them from both Tactile-Patch Encoder pretraining and ReTouch policy training." (§B.2)
(한글 해설 — 과제당 평균 약 128개 시연이며, 학습 풀은 800개입니다. ReTouch·Tactile-VLA·π 계열은 7개 과제 공동 학습, RDP와 ViTacFormer는 과제별 학습이라는 비대칭이 있습니다.)

---

## ⚖️ 한계

- **격리 진단과 실제 로봇 효과 크기의 간극** — 재귀 latent 정제만을 분리한 offline 진단은 in-contact 기준 latent cosine +0.908%, action MSE +2.139%인데, 같은 기능을 제거한 실제 로봇 ablation은 -15.2%p입니다. 소수점대 예측 정확도 개선이 두 자릿수 성공률로 증폭되는 메커니즘을 논문은 설명하지 않습니다. 폐루프에서는 작은 오차가 누적·발산한다는 통상적 설명이 가능하지만 검증되지 않았고, 그렇다면 실제 이득의 상당 부분이 latent 정제가 아니라 **재추론 빈도 자체**에서 왔을 가능성이 남습니다.
- **blocking 실행의 숨은 비용** — full 모델은 정제 결과가 돌아올 때까지 마지막 명령을 유지합니다. 이 정지가 없으면 7.8%p를 잃는다는 것은 뒤집어 말해 정책이 "잠깐 멈춤"이 허용되는 준정적(quasi-static) 과제에 맞춰져 있다는 뜻입니다. 동적 접촉 과제나 컴플라이언스 컨트롤러가 끼어 있는 스택에서는 명령 유지가 그대로 힘 스파이크가 될 수 있습니다.
- **지표 정의가 마진을 부풀립니다** — Button Press를 제외한 6개 과제는 단계별 부분 점수이므로, +18.4%p는 "20회 중 3.7회 더 성공"이 아니라 "평균 단계 진행도가 18.4% 더 높다"입니다. 완료율 기준 우위는 이 수치보다 작을 수 있고, 논문은 이진 완료율을 병기하지 않습니다.
- **통계적 뒷받침 부재** — 과제당 20 rollout, 시드 반복 없음, 신뢰구간 없음입니다. Table 3에서 non-blocking이 Pipette Press를 94.0으로 full(86.0)보다 잘하고, w/o Tactile-Patch Encoder가 Liquid Transfer에서 76.5로 full(69.0)을 앞서는 등 행 간 역전이 여러 곳에서 나타나는데, 20회 표본에서 이 정도 진폭은 잡음과 구분되지 않습니다.
- **단일 평가자 채점** — 현장에서 한 명의 평가자가 고정 rubric을 적용합니다. "본 뒤 남은 검은 자국이 있는가" 같은 판정이 들어가는 Sponge Wipe에서는 블라인드 처리 없는 단일 채점이 편향 위험을 남깁니다.
- **Cabinet Retrieval 회귀** — 유일하게 뒤진 과제(62.5 vs ViTacFormer 67.5)이자 시각 가림 하의 다단계 과제입니다. 저자는 예외로 언급만 하고 원인을 분석하지 않는데, 촉각 예측이 도움이 되지 않는 과제 부류(접촉이 결과를 좌우하지 않고 서랍 열기 같은 기구학적 단계가 지배하는 경우)를 시사합니다.
- **특권 브랜치의 학습 비용** — HAE는 배포에서 제거되지만 학습 중에는 18-layer / hidden 1024 Transformer 한 벌이 추가로 돌아갑니다. 정답 미래 촉각을 요구하므로 실시간 로그가 완비된 데이터셋에서만 가능하며, 이 오버헤드에 대한 절제 실험(예: HAE 없이 self-distillation)은 없습니다.
- **접촉 기하 일반화의 절대 수준** — 도전 조건에서 Height 42.5, Lighting 66.5로, 상대 우위는 크지만 절대값은 여전히 절반 안팎입니다. 학습 높이 7.5–10.5 cm에서 2.5–5 cm로의 외삽이 여전히 대부분 실패한다는 사실은 촉각 정제가 시각적 공간 일반화를 대체하지 못함을 보여줍니다.
- **모달리티 범위의 협소함** — 손끝 force taxel만 쓰고 손목 6축 F/T, 관절 토크, 미끄러짐 라벨은 없습니다. 미끄러짐이 설계 동기의 절반인데 정작 미끄러짐을 직접 감독하는 신호는 파이프라인에 없고, 접촉 상태 이진 판정만 사전학습 헤드로 들어갑니다.
- **π0.5 촉각 베이스라인의 공정성** — $`\pi_{0.5}`$+tactile은 촉각 프레임을 평탄화해 proprioception과 붙인 뒤 **256개 bin으로 이산화해 텍스트 상태 필드로 직렬화**합니다. 조밀한 연속 접촉 신호를 텍스트 토큰으로 밀어 넣는 구성이라 촉각 활용의 하한에 가깝고, 이 베이스라인 대비 마진은 과대평가되기 쉽습니다.

---

## ♻️ 재현성

- **코드** — 공개 저장소가 논문 및 arXiv 페이지에서 확인되지 않습니다 (`원문에 명시 없음`). 라이선스는 논문 자체가 CC BY 4.0입니다.
- **데이터** — XHT-Dataset(900 시연, 7과제, 100 궤적 held-out)은 논문의 기여로 제시되지만 배포 경로·라이선스에 대한 언급이 확인되지 않습니다 (`원문에 명시 없음`). 재현에는 데이터 공개가 필수인데 현재로서는 확인 불가입니다.
- **하드웨어** — 학습은 NVIDIA A800 8장, bfloat16. 배포 지연 측정은 NVIDIA RTX 5090. 로봇 리그는 UR7e + XHand 5지 손, 손목 RGB 1대 + 고정 외부 RGB 2대, 원격조작은 VIVE tracker(손목) + MANUS glove(손가락).
- **재현 가능한 부분** — 하이퍼파라미터 명세는 상세합니다: 사전학습 20k step / 정책 80k step, batch 32 / 8, AdamW + clip 1.0 + warmup 1k + cosine $`2.5\times 10^{-5}\rightarrow2.5\times 10^{-6}`$, 정렬 레이어 $`\ell=12`$ · 가중치 $`0.1`$, 접촉 임계 $`\theta_{c}=0.5`$ / $`1.0`$, $`\gamma_{c}=0.5`$, offset $`\{4,8,12\}`$, 10-step Euler. 베이스라인 6종의 적응 방식도 부록 C에 기술되어 있어, 데이터만 있으면 아키텍처 재구현 자체는 가능한 수준입니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P2(구조적 멀티모달 관찰 융합) — 주 pillar.**
  - **D11**(proprio-tactile-force 토큰 구성) — 가장 직접적인 타격점입니다. 우리 v1은 "손가락별 proprio-tactile 결합, 손가락 10 + 손바닥 2 토큰, 하드웨어별 CNN → 지문별 특징 → 손가락 토큰, 교체 가능한 센서 헤드 + 공통 토큰 포맷, contact-binary + slip-binary 보조 헤드(경량)"입니다. ReTouch는 이 구성의 거의 모든 요소를 실제 로봇에서 검증했습니다 — 손가락당 토큰 1개, 고정 패치 맵으로 흡수한 센서 이질성(T30 엄지 / T16 나머지), contact-binary 보조 헤드. 다만 **slip-binary 헤드는 없습니다**.
  - **D12**(topology-aware 인코딩 + 손 단위 집약) — finger-identity + patch-position 임베딩이 곧 topology 주입이고, 패치 어텐션 풀링($`\log a_{p}`$ 편향 포함)이 손가락 내 집약입니다. 우리 v1의 (B) 손가락/손바닥 토큰 self-attention은 손 *간* 집약 층위이므로 계층이 다르고 상충하지 않습니다.
  - **D10**(concat을 넘어선 이질 모달리티 융합) — $`\pi_{0}`$+tactile의 45.6 → 43.8 하락과 w/o Tactile-Patch Encoder의 -14.5%p가 flat-concat 반대 논거의 정량 근거입니다. 지금까지 P2가 확보한 근거 중 가장 통제된 비교에 가깝습니다.
  - **D8 / D9**(다중 카메라 기하 접지 / action-aware 인코더) — 무관합니다. 손목 1 + 외부 2 카메라를 쓰지만 기하 접지도, dynamics-aware 인코더도 없습니다. 이 논문은 P2의 (b)축만 다룹니다.
- **P5(World Model).**
  - **D28**(월드모델 역할) — 미래 촉각 예측을 정책과 공동 학습되는 auxiliary로 쓰는 v1 선택과 정확히 일치하며, 독립 플래너가 아닙니다.
  - **D30**(예측 공간) — "taxel 재구성 없이 latent만" 이라는 선택이 latent 예측 v1의 촉각 판 사례입니다. 다만 3D-flow가 아니라 행동 손실이 정의한 latent라는 점이 다릅니다.
  - **D31**(action conditioning) — **반례로 기록할 가치가 있습니다.** ReTouch는 방향성 마스크로 행동 토큰이 촉각 latent에 영향을 주지 못하게 *차단*합니다. 우리 v1의 "per-frame action-conditioned 예측"과 반대 방향이며, 두 설계가 목적이 다르다는(예측 자체의 자기충족 방지 vs 동역학 학습) 분기를 명시해 둘 필요가 있습니다.
  - **D32**(egocentric hand-object WM) — 무관합니다. 인간 ego 비디오를 쓰지 않고 로봇 원격조작 시연만 씁니다.
- **P1(이질적 Body/Hand Action Expert).**
  - **D5**(입력 모달리티 + 제어율 분리) — 우리 v1은 "(ii) 모달리티 분리 + (α) 공유 제어율"인데, ReTouch는 9 Hz / 36 Hz **분리 제어율**로 -23.6%p 규모의 근거를 제시합니다. (α) 공유 제어율 선택에 대한 가장 구체적인 반증 후보입니다.
  - **D1 / D4**(분할 형태 / Body↔Hand 정보 공유) — ReTouch에는 Body/Hand 분리가 없습니다(단일 18차원 관절 공간). 그런데 Table 6의 arm / hand 분해가 **분리를 지지하는 근거를 우연히 제공합니다**: 촉각 정제는 hand-suffix MSE만 개선하고 arm-suffix MSE는 양 위상 모두에서 악화시킵니다.
  - **D7**(π 백본 통합) — π0 체크포인트에서 초기화 후 fine-tune으로, 우리 v1(π0 action expert 슬라이스 + 양측 FT)과 방향은 같으나 분할 없이 통짜입니다.
  - **D2 / D3**(Body / Hand 출력 공간) — Body는 우리 v1의 both-wrist / tool-flange pose가 아니라 **절대 관절 위치**라 상이합니다. Hand는 손가락 관절 명령으로 우리 v1과 일치합니다.
- **P3(Hand-level System0).**
  - **D14 / D15**(System1↔System0 인터페이스 / 입력 모달리티) — 긴장 관계입니다. ReTouch는 촉각 기반 고속 접촉 반응 루프를 RL System0 없이 **모방 학습만으로 VLA 내부에 36 Hz로 구현**하고, 후파지 당김 교란에서 85.0%로 자율 재파지까지 해냅니다. "슬립/파지 유지는 RL이 필요한 유일 지점"이라는 우리 Identity 주장에 대한 직접적 반례 후보입니다. 다만 ReTouch의 36 Hz는 System0가 겨냥하는 sub-policy-loop 대역(수백 Hz)보다 훨씬 느리므로, 반증이라기보다 "System0가 필요한 대역의 하한을 어디로 잡아야 하는가"를 되묻습니다.
- **P0(VLA Datasets & Benchmarks).**
  - **D25**(촉각/토크 데이터 스카우팅) — XHT-Dataset은 5지 조밀 taxel 스트림을 담은 드문 접촉 모달리티 코퍼스이므로 우선 플래그 대상입니다. 다만 공개 여부가 확인되지 않아 현 시점에 pin 후보로 올릴 수 없습니다.
  - **D27**(라이선스/사용성 기준) — 데이터 라이선스 미확인이므로 기준 미달 상태로 기록합니다.
- **P4(데이터 효율 적응을 위한 사전학습)** — 실질적 연결이 없습니다. π0에서 fine-tune하지만 lineage 비교도, prior 보존 측정도, 데이터 구성 레버도 없습니다. D19 / D20에 대한 증거는 이 논문에서 얻을 수 없습니다.
- **Identity 지지 / 긴장** — 지지: "모놀리식 디코더 + 시각 지배 관찰"이 다지 조작에서 부족하다는 주장에 정량 근거를 더합니다. 긴장: 접촉 안정화가 RL 없이도 IL 내부 고속 루프로 상당 부분 달성된다는 점, 그리고 Body/Hand 분리 없이도 83.6%가 나온다는 점.
- **경쟁 함의** — P2 §5의 ViTacFormer 핀이 이 논문에서 재현 베이스라인으로 33.1% (ReTouch 83.6%)를 기록했습니다. 다지 손 촉각 표현·미래 촉각 예측이라는 두 축 모두에서 ViTacFormer가 후속 연구에 추월당한 상태입니다.

---

## ✨ 핀 논문 대비 델타

- **vs. ViTacFormer (P2 핀, arXiv:2506.15953)** — ViTacFormer도 미래 촉각을 예측하지만 (a) 예측 대상이 손가락별 3D 합력 + 시간 차분의 30차원 관찰이고, (b) 청크 시작 시 한 번 예측하며, (c) cross-modal 표현 학습이 목적입니다. ReTouch의 새로움은 세 지점 모두입니다 — 예측 대상을 *행동 손실이 정의한 latent*로 바꾸고, 그 latent를 실행 중 재귀 갱신하며, 손가락 내부를 5패치로 더 잘게 구조화합니다. 같은 플랫폼 재현 비교(33.1 vs 83.6)까지 딸려 있습니다.
- **vs. ForceFlow (P2 핀, arXiv:2605.11048)** — ForceFlow의 비대칭성은 모달리티 간 비대칭 융합(modal masking / AdaLN)인 반면, ReTouch의 비대칭성은 **같은 forward 호출 안의 시간적/인과적 비대칭**(촉각 예측이 행동보다 먼저)입니다. 축이 다르므로 배타적이지 않고 결합 가능합니다.
- **vs. DexViTac (P2 방법론 기반, arXiv:2603.17851)** — DexViTac은 기구학적 접지(kinematic grounding)로 촉각을 인코딩합니다. ReTouch의 패치 분할은 기구학이 아니라 **센서 레이아웃 기반 고정 맵**이라 더 단순하고 하드웨어 종속적입니다. 우리 D12(팜 상대 지문 자세, kinematic chain)는 DexViTac 쪽에 가깝고, ReTouch는 그 하위 층(지문면 내부 구획)을 채웁니다.
- **vs. SaTA (P2 방법론 기반, arXiv:2510.14647)** — SaTA는 Sharpa Wave에서 FiLM 기반 공간-촉각 조건화를 씁니다. ReTouch는 FiLM 대신 토큰화 + 어텐션 풀링이며, 무엇보다 **사전학습된 촉각 인코더**를 별도 단계로 두고 그 품질을 offline 지표로 진단합니다(Table 5). SaTA에 없는 것이 이 진단 층입니다.
- **vs. π0 (P1 핀, arXiv:2410.24164)** — ReTouch는 π0 파생이며, 논문 자체가 π0 / π0+tactile / π0.5 / π0.5+tactile 네 변형을 같은 플랫폼에서 측정해 줍니다(45.6 / 43.8 / 51.5 / 53.1). π0 계열에 촉각을 단순 부착했을 때의 상한을 알려주는 참조점으로서 가치가 있습니다.
- **vs. AHEAD (P5 핀, arXiv:2606.02486) / VLA-JEPA (P5 핀, arXiv:2602.10098)** — 두 핀 모두 latent 예측 월드모델이지만 예측 대상이 시각 latent입니다. ReTouch는 같은 JEPA류 구조(특권 타깃 + stop-gradient + 코사인 정렬)를 **촉각 latent**에 적용하고, 결정적으로 그 latent를 **실행 중 재귀 갱신되는 상태**로 씁니다. P5 핀 어디에도 "예측을 제어 상태로 유지한다"는 축은 없습니다.
- **vs. DexWM (P5 핀, arXiv:2512.13644)** — DexWM은 인간 ego 비디오에서 손-물체 동역학을 학습합니다. ReTouch는 인간 비디오를 쓰지 않고 로봇 시연만 쓰므로 D32 축에서는 겹치지 않습니다.
- **vs. RH20T (P0 핀, arXiv:2307.00595)** — RH20T는 손목 6축 F/T를 가진 접촉 코퍼스입니다. XHT-Dataset은 손목 F/T가 아니라 **지문 taxel**을 담아 모달리티가 보완적이지만, 900 시연 규모는 사전학습 스케일에 한참 못 미치고 공개 여부도 미확인이라 핀 후보는 아닙니다.

---

## ⚙️ 의사결정 함의

이 논문이 맞다면 우리 파이프라인에서 바뀌는 것:

- **D11 토큰 구성에 "패치" 중간 층을 넣습니다.** 현재 v1은 Deform Map → CNN → 지문별 특징 → 손가락 토큰의 3단인데, 여기에 **지문면 내부 5구획(tip / center / base / left / right) 풀링**을 넣어 4단으로 만듭니다. Sharpa Deform Map은 약 320×240 이미지이므로 taxel 집합 대신 고정 ROI 격자로 구획을 정의합니다. 구획별 서술자는 논문 식 (11)을 그대로 이식 — contact-gated 평균 3D 변위, 성분별 최대, 활성 비율 `a_p`, 최대 크기 `q_p`. 신설 config: `tactile.patch_per_finger=5`, `tactile.patch_layout=fixed_roi_grid`.
- **촉각 인코더 사전학습 단계를 신설합니다.** 정책 학습 이전에 3-head 목적으로 사전학습: `loss.tpe = lambda_dist * CE + lambda_force * force + lambda_contact * BCE`, `lambda_contact=0.5`, `loss.force = active + 0.5*magnitude + 0.25*inactive` (Smooth-L1, 활성/비활성 개별 정규화). 신설 키: `tactile_encoder.pretrain_steps=20000`, `tactile_encoder.freeze_policy_steps=5000`, `tactile.contact_threshold_pretrain=0.5`, `tactile.contact_threshold_policy=1.0`, `tactile.contact_gamma=0.5`.
- **D11의 보조 헤드 목록을 수정합니다.** 현재 "contact-binary + slip-binary"인데, ReTouch의 근거가 있는 것은 contact-binary와 **패치 간 접촉 강도 분포(CE)** 이고 slip-binary는 근거가 없습니다. 분포 헤드를 추가하고 slip-binary는 라벨 확보 문제와 함께 별도 검토로 내립니다. 이유: single-head 대비 방향 코사인 0.4089 → 0.8071로 개선되는 항목이 곧 미끄러짐 판단에 쓰이는 접선 방향 정보입니다.
- **D12 집약에 면적 편향 항을 넣습니다.** 패치 풀링 로짓에 `+ log(a_p + eps)` 를 더하는 형태(식 12)로, 접촉 면적이 큰 구획에 사전 가중을 줍니다. 우리 손가락/손바닥 토큰 self-attention 위쪽은 유지합니다.
- **D5 제어율 분리를 재검토 대상으로 올립니다.** 현행 (α) 공유 제어율 대신 `vlm_update_hz=9` / `action_expert_hz=36` 의 2단 스킴을 후보로 두고, 액션 지평 16 · 정제 offset `{4,8,12}` · **blocking 실행**을 기본값으로 잡습니다. non-blocking은 -7.8%p이므로 기본값이 아닙니다.
- **손실에 미래 촉각 latent 정렬 항을 추가합니다.** `loss.tactile_latent_align` = HAE 타깃(stop-gradient)에 대한 평균 코사인 거리, 가중치 `0.1`, 정렬 레이어 `align_layer=12`. 학습 전용 HAE 브랜치와 `1024→1024→1024` SiLU 투영기가 함께 필요합니다.
- **어텐션 마스크에 방향성 제약을 넣습니다.** 촉각 foresight query → action token 방향을 차단하고 그 역만 허용. Body/Hand 분리 스택에서는 마스크가 3자(촉각 latent / Body head / Hand head) 관계로 확장되므로, 우선 Hand head만 촉각 latent를 참조하게 두는 변형이 첫 후보입니다 (근거: Table 6에서 arm-suffix MSE는 정제로 악화).
- **평가 지표를 추가합니다.** held-out 궤적에서 offset별 `latent_cosine`과 `action_suffix_mse`를 pre-contact / in-contact로 나눠 기록. 접촉 시작은 `theta_onset=1.0`(raw taxel L2, 데이터셋 고유 단위, 지속 조건 없음). 그리고 **arm / hand suffix MSE를 반드시 분리 기록**합니다 — 합산 지표는 팔의 악화를 손의 개선이 가려버립니다.
- **π0 flow-matching 설정 하나를 고정합니다.** 같은 청크 내 모든 정제 호출이 **초기 action-noise 샘플을 재사용**하도록 강제 (`flow.reuse_chunk_noise=true`). 이 항목이 없으면 정제마다 다른 노이즈에서 출발해 청크 접합부가 불연속해집니다.

---

## ⚠️ 먼저 검증할 실패 모드

싼 것부터.

1. **센서 모달리티 불일치 (비용: 로그 데이터 + 반나절).** XHand는 손가락당 120개 이산 3축 force taxel, Sharpa는 지문당 약 320×240 vision-based Deform Map입니다. 식 (10)–(11)의 통계는 taxel 단위 force 벡터를 전제합니다. **가장 싼 체크**: 기록된 Deform Map 로그 몇 분 분량으로 5구획 서술자를 계산하고 3-head를 offline 사전학습해 contact F1이 논문 수준(0.9999)에 근접하는지만 봅니다. 정책 학습 없이 인코더만으로 판정 가능합니다. 여기서 방향 코사인이 0.5를 넘지 못하면 패치 구조 이식 자체가 실패입니다.
2. **36 Hz 실현 가능성 (비용: forward 지연 측정 1회).** 19.54 ms는 18-layer / hidden 1024 FAE를 RTX 5090에서 측정한 값이고 통신·컨트롤러 오버헤드가 빠져 있습니다. **체크**: 우리 π0 슬라이스 Body/Hand expert의 캐시 컨텍스트 forward 지연을 우리 GPU에서 재고, 여기에 로봇 통신 왕복을 더해 27.7 ms(36 Hz) 예산 안에 드는지 확인합니다. 넘으면 offset을 `{8}` 하나로 줄인 축소판부터 시작합니다.
3. **blocking 실행과 컨트롤러의 상호작용 (비용: 컨트롤러 루프 계측).** 정제 대기 중 마지막 명령을 유지하는 방식은 UR7e 위치 제어에서는 무해하지만, 컴플라이언스 컨트롤러가 끼면 유지 구간이 힘 적분으로 나타납니다. **체크**: 36 Hz로 약 20 ms 명령 유지를 인위로 넣고 지령 jitter와 접촉력 스파이크를 계측합니다. 스파이크가 나오면 non-blocking(-7.8%p)을 감수하거나 유지 대신 이전 청크 보간을 씁니다.
4. **효과의 귀인이 틀렸을 위험 (비용: ablation 2개).** 논문 자체의 68.4 vs 67.6 (0.8점)은 "고정 예측은 없는 것과 같다"를 말하지만, 동시에 offline 진단의 효과 크기는 2.139%입니다. 우리 스택에서 이득의 출처가 latent 정제인지 단순 재추론 빈도인지 먼저 갈라야 합니다. **체크**: 촉각 예측 모듈 없이 **행동만 offset `{4,8,12}` 에서 재추론**하는 변형을 먼저 돌립니다. 이것만으로 대부분의 이득이 나오면 HAE/FAE 이중 브랜치(학습 비용 약 2배)는 지불할 이유가 없습니다. 이 순서를 뒤집으면 가장 비싼 것을 먼저 만들게 됩니다.
5. **Body 자유도 악화 (비용: 이미 있는 지표 분해).** Table 6에서 정제는 arm-suffix MSE를 두 위상 모두 악화시킵니다. 우리는 Body가 both-wrist / tool-flange pose(D2)라 관절 공간보다 촉각 상관이 더 약할 가능성이 큽니다. **체크**: 정제 신호를 Hand head에만 붙인 변형과 양쪽에 붙인 변형을 offline MSE로 비교합니다. 실제 로봇 롤아웃 없이 판정됩니다.
6. **행동 공간 불일치 (비용: 설계 검토).** ReTouch의 청크 접미부 교체는 18차원 **절대 관절 위치** 공간에서 이뤄집니다. 우리 D2는 flange pose이므로 접미부 교체 시 자세 연속성(특히 회전 표현)의 성질이 다릅니다. **체크**: 기존 시연 궤적에서 offset 4/8/12 접미부 교체를 오프라인으로 시뮬레이션해 flange pose 궤적의 불연속(각속도 점프)을 계측합니다.
7. **동결 VLM과의 호환성 (비용: 학습 1회).** ReTouch는 π0에서 fine-tune하지만 우리 D19 v1은 VLM 전면 동결입니다. 동결 상태에서 캐시 의미 컨텍스트는 그대로 쓸 수 있지만, 촉각 분기가 전부 액션 전문가 안에 들어가야 합니다. **체크**: 동결 백본 + FAE 경로만으로 최소 1개 과제에서 학습이 수렴하는지 확인합니다. 수렴하지 않으면 D19를 흔들지 말고 촉각 인코더 출력을 액션 전문가 입력으로만 제한하는 축소판을 씁니다.
8. **데이터 규모 (비용: 없음, 계획 검토).** 과제당 약 128개 시연으로 나온 결과입니다. 우리 in-hand 재배향 / 도구 조작 과제는 접촉 다양성이 훨씬 크므로 같은 규모에서 재현되리라 가정할 수 없습니다. **체크**: 논문의 과제 중 우리 Phase 1(인핸드 큐브 회전)에 가장 가까운 것이 없다는 사실을 먼저 인정하고, Bottle Grasp / Cob Grasp 계열(파지 유지)로 대리 검증합니다.
9. **미끄러짐 감독의 부재 (비용: 라벨링 파일럿).** 설계 동기는 미끄러짐인데 파이프라인에 미끄러짐 라벨이 없고 접촉 이진 판정만 있습니다. 우리 D11의 slip-binary 헤드를 유지하려면 라벨이 필요합니다. **체크**: 파지 유지 시연 소량에 미끄러짐 구간을 수동 라벨하고, 접촉 강도 분포 헤드의 출력만으로 그 구간이 분리되는지 봅니다. 분리되면 별도 slip 헤드가 불필요합니다.

---

## 💡 컨텍스트 제안

사람이 판단할 항목만 적습니다 (`context/` 파일은 수정하지 않았습니다).

- **P2 §5 핀 교체 검토 — ViTacFormer → ReTouch.** ViTacFormer는 D10/D11 근거로 핀되어 있으나, 이 논문에서 같은 플랫폼 재현 시 33.1% (ReTouch 83.6%)이고 구조적 촉각 토큰·미래 촉각 예측 양쪽에서 추월당했습니다. 다만 ReTouch는 코드/데이터 공개가 확인되지 않으므로, 즉시 교체보다 **ReTouch를 방법론 기반(non-pinned)에 추가하고 다음 분기 재조정 때 교체 판단**을 권합니다.
- **D11 v2 후보.** 보조 헤드 목록을 `contact-binary + slip-binary` 에서 `contact-binary + patch-distribution(CE) + force-regression` 으로 바꾸고, slip-binary는 라벨 확보 여부에 종속된 별도 항목으로 내리는 안. 근거는 Table 5의 방향 코사인 0.4089 → 0.8071. 아울러 토큰 구성에 "지문면 내부 5구획" 중간 층을 명시하는 안.
- **D5 revisit trigger 신설 검토.** (α) 공유 제어율에 대한 첫 정량 반례입니다(9/36 Hz 분리, intra-chunk 갱신 제거 시 -23.6%p). D5를 `OPEN` 으로 승격할지, 아니면 "제어율 분리는 P3 System0 도입 시점에 재검토"라는 트리거만 달지 사람이 결정할 사안입니다.
- **D31 분기 기록.** ReTouch는 행동 → 촉각 예측 방향을 *차단*하는 설계이며, 우리 v1의 action-conditioned 예측과 반대입니다. D31 문구에 "예측을 제어 참조값으로 쓸 때는 action-conditioning이 자기충족 위험을 만든다"는 분기 조건을 남겨두는 안.
- **D25 플래그 (핀 아님).** XHT-Dataset(900 시연 / 7과제 / 5지 조밀 taxel)을 접촉 모달리티 코퍼스 후보로 기록하되, **공개 경로·라이선스 미확인**이므로 D27 기준 미달 상태로 표시하고 공개 시 재평가.
- **P3 Identity 긴장 기록.** "슬립/파지 유지는 RL이 필요한 유일 지점"이라는 주장에 대해, 36 Hz IL 루프만으로 후파지 당김 교란 재파지 85.0%가 나왔다는 반례가 생겼습니다. System0의 존재 이유를 "IL이 못 하는 일"이 아니라 "IL 루프가 닿지 못하는 대역(수백 Hz)"으로 재서술할지 검토를 권합니다.
