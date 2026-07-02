# Paper Analysis — StressDream: Steering Video World Models for Robust Policy Evaluation and Improvement

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | StressDream: Steering Video World Models for Robust Policy Evaluation and Improvement |
| 저자 | Junwon Seo, Sushant Veer, Ran Tian, Wenhao Ding, Apoorva Sharma, Karen Leung, Edward Schmerling, Marco Pavone, Andrea Bajcsy (CMU · NVIDIA Research · UW · Stanford) |
| 링크 | [arXiv:2606.00267](https://arxiv.org/abs/2606.00267) · [GitHub](https://github.com/CMU-IntentLab/StressDream) · [Website](https://junwon.me/StressDream/) |
| 발행일 / 버전 | 2026-05-29 · v1 |
| 본문 확보 수준 | PDF 텍스트(pypdf) |
| 분석 생성일 | 2026-07-02 |
| 관련 Pillar | P5 |
| 태그 | flow-matching |

<!-- 본문 확보 기록 (§5-4 honesty):
     curl --fail -sS "https://arxiv.org/html/2606.00267"    → HTTP 404
     curl --fail -sS "https://arxiv.org/html/2606.00267v1"  → HTTP 404
     curl --fail -sS "https://ar5iv.labs.arxiv.org/html/2606.00267" → HTTP 403
     pdftotext 미설치 → pypdf 로 arXiv PDF(43p) 전문 텍스트 추출 성공.
     PDF-only 확보이므로 규칙에 따라 figure hotlink 는 생략합니다.
     GitHub / Website URL 은 논문 본문(초록 및 p.18 "Codes are available at
     https://github.com/CMU-IntentLab/StressDream") 에 명기된 것을 그대로
     옮겼으며, 실행 환경의 네트워크 정책(proxy HTTP 403)으로 외부 도달
     검증은 불가했습니다 — 날조 아님. -->

---

## 🧭 한 줄 요약 (TL;DR)

StressDream 은 확산 기반 비디오 세계 모델(WM)의 생성이 초기 노이즈의 결정론적 함수라는 성질을 이용해, 추론 시점에 텍스트로 지정한 고임팩트 이벤트(작업 실패·충돌)를 향해 초기 노이즈를 경사 최적화로 스티어링하되 — VLM 의 yes/no 토큰 확률을 미분가능 의미 목적식으로, 고차원 가우시안 전형 집합(typical set) 통계를 그럴듯함 정칙화로 사용하여 — "일어날 법하면서 최악인" 상상을 생성하고, 이를 통해 실패 검출 recall 을 54%→94% 로, 재가중 파인튜닝된 π0.5 정책 성공률을 39%→71% 로 끌어올립니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 행동 조건부 비디오 WM 은 미래 관찰의 *분포*를 학습하지만, 정책 평가·개선은 통상 명목(nominal) 상상 1개에 의존합니다. 같은 행동에서도 여러 미래가 가능할 때(봉지를 높은 곳에서 떨어뜨리면 쏟아질 수도, 아닐 수도), 드물지만 고임팩트인 결과를 명목 샘플링이 놓칩니다.
- **기존 접근의 한계** — 무작위 샘플링(Best-of-N)은 드문 실패를 찾는 데 비효율적이고, classifier guidance 는 denoising 궤적을 직접 왜곡해 비현실 생성을 만듭니다. 보상 파인튜닝은 기준(criterion)마다 재학습이 필요하고 원 분포에서 이탈할 수 있습니다.
- **핵심 도전 과제** — 노이즈 공간이 극도로 고차원( `≈1M` 차원, 주행 WM)이라, 최적화가 장면 의존적 목표 이벤트를 추론하면서도 노이즈가 분포 밖(OOD)으로 밀려나 비현실 영상을 만드는 것을 막아야 하며, 반복적 denoising 전 과정의 역전파는 비용·기울기 소실 문제가 있습니다.
- **본 논문의 가설** — 결정론적(probability-flow ODE) 샘플러에서 생성의 모든 확률성은 초기 노이즈에 있으므로, (a) VLM 토큰 확률로 미분가능한 의미 기울기를 얻고 (b) 가우시안 전형 집합 통계(노름·등방성·스펙트럼 백색성)를 유지하면, 초기 노이즈 최적화만으로 "WM 분포가 지지하는" 최악 사례를 겨냥해 생성할 수 있습니다.
- **왜 지금 중요한가** — Vista(주행)·Ctrl-World(조작) 급 SOTA 비디오 WM 이 정책 평가·개선의 시뮬레이터로 쓰이기 시작한 시점에서, 명목 상상 기반 평가는 낙관 편향을 갖습니다. 분포를 학습해 놓고 분포를 활용하지 않는 간극을 추론 시점 기법 하나로 메웁니다.

---

## 🧩 핵심 기여

- **초기 노이즈 최적화로서의 WM 스티어링 정식화** — 강건 정책 평가를 min-max 문제(외부: 행동 선택, 내부: 최악-사례 노이즈 탐색)로 정의하고, 내부 최적화를 초기 노이즈에 대한 1차 경사 상승으로 풉니다.
- **의미 목적식** $`\mathcal{C}_{\mathrm{sem}}`$ — VLM(Qwen-VL 계열)에 목표 이벤트 텍스트를 주고 yes/no 단일 토큰 로그확률 차이를 미분가능 점수로 사용, 장면 의존적 이벤트를 추론 시점에 자유롭게 지정합니다.
- **그럴듯함 목적식** $`\mathcal{C}_{\mathrm{pla}}`$ — 고차원 가우시안 전형 집합의 세 통계(노름 집중·블록 등방성·스펙트럼 백색성)를 정칙화하고, 각 정칙자의 집중 부등식(Laurent–Massart, Bernstein 계열)을 증명해 "전형 노이즈에서는 벌점이 작다"를 보장합니다.
- **score-distillation 기울기 근사** — denoiser Jacobian 이 근사적으로 대각이라는 관찰을 이용해 $`\nabla_\epsilon \mathcal{C} \approx \beta \nabla_o \mathcal{C}`$ 로 대체, 50-step denoising 역전파 없이 검증자 역전파만으로 최적화를 가능하게 합니다 (전체 기울기는 오히려 실패함을 실증).
- **강건 평가·개선의 실증** — 참 동역학을 아는 Dubins car 통제 실험에서 "가능할 때만" 실패를 상상함을 보이고, Vista·Ctrl-World 에서 실패 검출 recall 54%→94%, 스티어링된 상상으로 재가중 파인튜닝한 π0.5-DROID 성공률 39%→71% 를 달성합니다.

---

## 🔑 기술 키워드

- **Video World Model** — 행동 시퀀스를 조건으로 미래 관찰(비디오)을 생성하는 학습된 물리 시뮬레이터. 본 논문에서는 스티어링의 대상이 되는 동결된 기반 모델입니다.
- **Initial Noise Optimization** — 확산 모델의 결정론적 샘플러에서 초기 가우시안 노이즈가 곧 "어떤 샘플이 나올지"를 정하는 제어 변수라는 점을 이용해, 모델 가중치는 두고 노이즈만 경사 최적화하는 추론 시점 정렬 기법.
- **Typical Set** — 고차원 가우시안에서 확률 *질량*이 몰리는 얇은 껍질( `‖ε‖₂ ≈ √D` ). 밀도가 최대인 영점 벡터는 사실상 절대 샘플링되지 않는다는, 밀도≠질량 구분이 정칙화 설계의 근거입니다.
- **VLM Guidance** — VLM 이 생성 비디오를 보고 "목표 이벤트가 일어났는가"를 yes/no 토큰 확률로 채점, 그 로그확률 차이를 통해 고차원 노이즈로 흘려보내는 미분가능 의미 기울기.
- **Score Distillation** — denoising 전 과정을 역전파하는 대신 denoiser Jacobian 을 스칼라 배 항등행렬로 근사해, 생성물에 대한 기울기를 초기 노이즈 기울기의 대리로 쓰는 근사법.
- **Pessimistic Imagination** — 같은 관찰·행동 입력에서 최악의(실패) 미래를 우선 상상하는 것. 강건(min-max) 정책 평가의 내부 최적화에 해당합니다.
- **Best-of-N Sampling** — 최적화 없이 N개 상상을 뽑아 최고 점수를 취하는 0차(zeroth-order) 탐색 베이스라인. 동일 예산에서 StressDream 보다 드문 이벤트 발견에 비효율적임이 비교축입니다.
- **Classifier Guidance** — denoising 스텝마다 분류기 기울기를 주입하는 고전적 스티어링. 궤적 자체를 왜곡해 비현실(OOD) 생성을 만드는 대조군으로 쓰입니다.
- **Ctrl-World** — DROID 셋업에서 학습된 조작용 제어가능 생성형 WM (3 카메라 · 5프레임 예측). 본 논문 조작 실험의 기반 WM 입니다.
- **Weighted Regression** — 실패로 스티어링된 시연에 가중치 0.1, 강건한 시연에 1.0 을 주어 π0.5 를 파인튜닝하는 정책 개선 목적식.

---

## 🔬 방법론

### 직관

비디오 세계 모델로 정책을 평가할 때 보통은 상상(imagination)을 한 번 굴려 보고 성공/실패를 판정합니다. 그러나 물리 상호작용의 미래는 본질적으로 다봉(multimodal)입니다 — 열린 커피 봉지를 높은 곳에서 떨어뜨리면 콩이 쏟아질 수도, 운 좋게 안 쏟아질 수도 있습니다. WM 은 이 분포를 이미 학습하고 있는데, 명목 샘플 하나(혹은 몇 개)만 보는 평가는 낙관 편향을 갖고 드문 고임팩트 실패를 놓칩니다.

StressDream 의 출발점은 결정론적 샘플러(probability-flow ODE)를 쓰는 확산 WM 에서는 조건(관찰 히스토리·행동)이 고정되면 생성 비디오가 초기 노이즈만의 함수라는 사실입니다. 즉 "어떤 미래가 나올지"는 초기 노이즈를 고르는 문제이고, 이는 무작위 추첨 대신 경사 최적화로 풀 수 있습니다. 목표 이벤트는 추론 시점에 텍스트로 지정합니다("커피콩이 쏟아지는가?"). VLM 에게 생성 비디오를 보여주고 yes/no 한 토큰의 확률 차이를 점수로 삼으면, 이 점수는 미분가능하므로 노이즈까지 기울기를 흘려보낼 수 있습니다.

문제는 노이즈 공간이 수만~수백만 차원이라는 점입니다. 아무 제약 없이 점수만 올리면 노이즈가 가우시안의 "전형 집합" — 질량이 몰려 있는 얇은 껍질 — 을 벗어나고, 훈련 때 본 적 없는 입력을 받은 denoiser 는 비현실적 영상(차가 사라지거나 형체가 뭉개지는)을 만듭니다. 그래서 노름·등방성·스펙트럼 백색성이라는 세 가지 가우시안 표본 통계를 벌점으로 걸어 노이즈를 전형 집합 안에 붙잡아 둡니다. 여기에 denoising 전 과정을 역전파하는 대신 출력에 대한 기울기를 스칼라 배로 근사해 쓰는 트릭이 더해져 실용적 비용으로 동작합니다.

결과적으로 평가 측면에서는 "일어날 법한 최악"을 찾아내는 비관적(pessimistic) 상상이 가능해지고 — WM 분포가 지지하지 않는 이벤트(끈적한 캔디 쏟기, 닫힌 봉지에서 쏟기)는 스티어링해도 생성되지 않습니다 — 개선 측면에서는 스티어링 하에서 실패하는 시연의 가중치를 낮춰 정책을 파인튜닝함으로써, 우연히 성공했을 뿐 위험한 행동 대신 강건한 행동을 선호하게 만듭니다.

### 아키텍처

**행동 조건부 확산 WM (배경, §2)**

행동 조건부 비디오 WM $`f_\theta`$ 는 관찰 히스토리와 미래 행동 시퀀스를 조건으로 미래 관찰 분포를 모델링합니다 (식 1):

$$o \sim f_\theta(\cdot \mid o_{\mathrm{hist}}, a), \quad o := o_{t:t+H},\ o_{\mathrm{hist}} := o_{t-h:t},\ a := a_{t:t+H}$$

각 관찰은 `n` 개 카메라 이미지와 고유수용성 상태 $`q`$ 로 구성됩니다. 확산 WM 은 데이터와 표준 가우시안 노이즈 사이의 변환을 학습하며 (식 2):

$$x_\tau = \alpha_\tau x + \sigma_\tau \epsilon, \quad x_0 := o,\ x_T := \epsilon \sim \mathcal{N}(0, I_D)$$

생성은 노이즈 예측기 $`g_\theta^\tau`$ 를 이용한 역방향 결정론적 업데이트의 반복입니다 (식 3):

$$d_\tau(x_\tau, o_{\mathrm{hist}}, a) := x_{\tau-1} = \frac{\alpha_{\tau-1}}{\alpha_\tau}\big(x_\tau - \sigma_\tau\, g_\theta^\tau(x_\tau, o_{\mathrm{hist}}, a)\big) + \sigma_{\tau-1}\, g_\theta^\tau(x_\tau, o_{\mathrm{hist}}, a)$$

> "Thus, all stochasticity in generation is governed by the initial noise, implying that selecting the initial noise controls which video is generated from the WMs." (§2)

(이 문장이 방법 전체를 떠받치는 관찰입니다 — probability-flow ODE 하에서 $`o = f_\theta(\epsilon, o_{\mathrm{hist}}, a)`$ 는 초기 노이즈의 결정론적·미분가능 함수이므로, "어떤 미래를 상상할지"가 노이즈 선택 문제로 환원됩니다.)

**min-max 강건 평가 정식화 (§3)**

같은 행동 아래 여러 미래가 가능할 때, 강건한 정책은 그럴듯한 결과 분포 전체를 고려해야 합니다 (식 4):

$$a^* = \arg\min_{a \in \mathcal{A}} \max_{\epsilon \in \mathbb{R}^D} \mathcal{C}_{\mathrm{test}}\big(f_\theta(\epsilon, o_{\mathrm{hist}}, a)\big)$$

> "where the inner optimization chooses a Gaussian noise to steer the WM generation toward a worst-case plausible future that maximizes the criterion, while the outer optimization selects a robust action sequence that keeps the criterion low across plausible futures, even under worst-case outcomes." (§3)

(내부 최적화 = 비관적 상상 생성(본 논문의 기여), 외부 최적화 = 행동 선택(샘플링 기반 솔버든 정책 학습이든 무엇이든 가능)이라는 역할 분담입니다. 노이즈를 매번 평가하려면 비싼 denoising 이 필요하므로 무작위 재샘플링 대신 미분가능 기준의 기울기로 초기 노이즈를 직접 경사 상승합니다 — 식 5:)

$$\epsilon_{i+1} = \epsilon_i + \eta\, \nabla_{\epsilon_i}\big[\mathcal{C}_{\mathrm{test}}(o_i)\big], \quad o_i = f_\theta(\epsilon_i, o_{\mathrm{hist}}, a)$$

전체 기준은 의미 목적식과 그럴듯함 목적식의 합 $`\mathcal{C}_{\mathrm{test}} = \mathcal{C}_{\mathrm{sem}} + \mathcal{C}_{\mathrm{pla}}`$ 입니다 (§4).

**전체 알고리즘 (Algorithm 1, §B.5)**

매 반복마다 (1) 현재 노이즈로 비디오 생성, (2) VLM 점수 계산, (3) 근사 의미 기울기 $`g_{\mathrm{vlm}} = \beta \cdot \nabla_{o_i} \mathcal{C}_i`$ 와 정칙화 기울기 $`g_{\mathrm{reg}} = \nabla_{\epsilon_i} \mathcal{C}_{\mathrm{pla}}(\epsilon_i)`$ 를 합산, (4) 좌표별 클리핑( `±0.3` ) 후 전역 노름 클리핑( `1.0` ), (5) 경사 상승, (6) 노이즈 노름이 전형 껍질 $`\sqrt{D}`$ 에서 `3.0` 이상 벗어나면 껍질로 사영, (7) 최고 점수 생성물을 기억해 반환합니다. 모멘텀은 누적 업데이트가 노이즈를 전형 집합 밖으로 밀어낼 수 있어 사용하지 않습니다. 껍질 사영 임계 `3.0` 은 가우시안 노름의 표준편차가 고차원에서 약 `0.707` 로 수렴(Corollary 2)하므로 전형 표본의 99.99% 이상을 포함하는 보수적 값입니다.

### 학습 목표 / 손실

**의미 목적식 — VLM 기울기 (§4.1)**

추론 시점 텍스트 프롬프트 $`l`$ (예: "the coffee beans spill")에 대해, VLM 이 yes / no 단일 토큰을 출력하도록 프롬프팅하고 로그 토큰 확률 차이를 점수로 정의합니다 (식 6):

$$\mathcal{C}_{\mathrm{sem}}(o; l) = \log p_{\mathrm{VLM}}(\text{yes} \mid o, l) - \log p_{\mathrm{VLM}}(\text{no} \mid o, l)$$

> "Using the VLM’s single-token probabilities makes the objective differentiable, providing rich gradient signals for optimizing high-dimensional noise that generates an inference-time target event." (§4.1)

(태스크별 보상 모델을 새로 학습하는 대신 인터넷 스케일로 학습된 VLM 의 일반 비디오 이해력을 미분가능 채점기로 전용합니다. 저자들은 스크래치 학습 보상 모델보다 VLM 기준이 reward hacking 에 훨씬 강건하다고 보고합니다 — §F.) CLIP 계열(X-CLIP)을 쓸 때는 긍정/부정 프롬프트 임베딩과 비디오 임베딩의 코사인 유사도 차이 $`\mathcal{C}_{\mathrm{sem}}(o) = \mathrm{sim}(e_{\mathrm{video}}(o), e_{\mathrm{text}}(l_+)) - \mathrm{sim}(e_{\mathrm{video}}(o), e_{\mathrm{text}}(l_-))`$ 를 사용합니다 (§B.3).

> "We find that using all three camera views simultaneously is essential for reliable scoring: for the same scene and text prompt, using a single viewpoint leads to substantially poorer failure-event detection." (§B.3)

(조작 도메인에서 VLM 검증자에게 3개 카메라 뷰를 동시에 입력하는 것이 신뢰할 만한 채점의 전제 조건이라는 실무적 발견입니다. 단일 뷰로는 실패 이벤트 검출이 크게 나빠지며, CLIP 계열은 조작 장면 이해에 비효과적이라 도메인별로 검증자를 달리 택합니다 — 주행은 Wolf 로 파인튜닝된 Qwen2.5-VL + X-CLIP, 조작은 Qwen3-VL.)

**그럴듯함 목적식 — 전형 집합 정칙화 (§4.2, §B.1–B.2)**

$$\mathcal{C}_{\mathrm{pla}}(\epsilon) = \lambda_1 \mathcal{C}_{\mathrm{norm}}(\epsilon) + \lambda_2 \mathcal{C}_{\mathrm{iso}}(\epsilon) + \lambda_3 \mathcal{C}_{\mathrm{spec}}(\epsilon)$$

> "Importantly, in high dimensions, the typical set is not the same as the region of highest probability density: some noise vectors, such as the zero vector, may have high density but are extremely unlikely to be sampled from the Gaussian prior (See Appendix B.1 for more details)." (§4.2)

(정칙화 설계의 이론적 핵심입니다 — 밀도(likelihood)가 아니라 질량(typicality)을 지켜야 하며, 그래서 단일 노름 벌점이 아니라 가우시안 표본 통계 여러 개를 동시에 정칙화합니다. 기존 노이즈 최적화 연구들이 노름 정칙화만으로 충분하다고 본 것과 달리, 고차원 비디오 WM 에서는 추가 통계가 중요함을 실증합니다.)

**노름 집중** — $`\|\epsilon\|_2^2 \sim \chi_D^2`$ 이므로 노름은 $`\sqrt{D}`$ 껍질에 집중합니다:

$$\mathcal{C}_{\mathrm{norm}}(\epsilon) := -\big(\|\epsilon\|_2 - \sqrt{D}\big)^2$$

**블록 등방성** — 노름이 전형이어도 좌표 간 국소 상관이 남을 수 있으므로, $`\epsilon`$ 의 좌표를 무작위 치환 후 $`m`$ 개 부분벡터 $`\epsilon_i \in \mathbb{R}^k`$ ( $`D = mk`$ )로 분할하고 경험적 2차 모멘트가 항등에 가깝도록 벌점을 겁니다 (여러 무작위 치환에 대해 평균):

$$\mathcal{C}_{\mathrm{iso}}(\epsilon) := -\frac{1}{k}\big\|\widehat{\Sigma} - I_k\big\|_F^2, \quad \widehat{\Sigma} = \frac{1}{m}\sum_{i=1}^{m} \epsilon_i \epsilon_i^\top$$

**스펙트럼 백색성** — 좌표 공간에서 전형이어도 주파수 영역 인공물이 생길 수 있으므로, 각 공간 슬라이스의 2D DFT 파워 $`P = |F(\epsilon)|^2`$ 를 $`B`$ 개 주파수 빈으로 평균한 $`\hat{p}_b`$ 의 분산을 최소화합니다:

$$\mathcal{C}_{\mathrm{spec}}(\epsilon) := -\frac{1}{B}\sum_{b=1}^{B}(\hat{p}_b - \bar{p})^2, \quad \bar{p} = \frac{1}{B}\sum_{b'=1}^{B} \hat{p}_{b'}$$

세 정칙자 각각에 대해 "가우시안 전형 표본에서는 높은 확률로 벌점이 작다"는 집중 부등식을 증명합니다 (Lemma 1–3: Laurent–Massart 부등식, Bernstein 계열 부등식, 빈별 union bound; §B.2). 특히 노름 껍질의 절대 폭은 차원과 무관하게 $`\mathrm{std}(R) \to 1/\sqrt{2}`$ 로 일정합니다 (Corollary 2).

**기울기 근사 — score distillation (§4.3, §B.4)**

정확한 노이즈 기울기는 모든 denoising 스텝의 Jacobian 곱을 요구합니다. Ahn et al. 의 관찰(denoiser Jacobian 이 근사적으로 대각·항등 배수)을 따라 샘플러 Jacobian 전체를 스칼라 $`\beta`$ 로 흡수합니다 (식 7):

$$\nabla_\epsilon \mathcal{C}_{\mathrm{test}}(o) \approx \beta\, \nabla_o \mathcal{C}_{\mathrm{test}}(o), \quad o = f_\theta(\epsilon, o_{\mathrm{hist}}, a)$$

> "This approximation only requires backpropagation through the differentiable criterion function, avoiding full backpropagation through the iterative denoising process." (§4.3)

(50-step denoising 역전파는 H100 80GB 에서 gradient checkpointing 을 써도 비실용적인 반면, 이 근사는 검증자(VLM) 역전파만 필요합니다.) 최종 업데이트 기울기는 (식 8):

$$\nabla_\epsilon \mathcal{C}_{\mathrm{test}}(o) = \beta\, \nabla_o \mathcal{C}_{\mathrm{sem}}(o; l) + \nabla_\epsilon \mathcal{C}_{\mathrm{pla}}(\epsilon)$$

> "Fig. 14 shows that the approximate gradient successfully increases the VLM score, whereas optimization with the full gradient fails to improve it." (§B.4)

(주목할 반전 결과입니다 — 전체 기울기 계산이 가능한 Ctrl-World 에서조차 근사 기울기가 이기며, 저자들은 50-step 역전파의 유한 정밀도 기울기 소실과 저정밀 denoising 연산을 원인으로 추정합니다. 근사가 "타협"이 아니라 실질적으로 더 나은 선택이라는 뜻입니다.)

### 학습 셋업

**WM 파인튜닝 (§6, §D.1)** — 기반 WM 을 그대로 쓰지 않고 태스크 관련 데이터로 소량 파인튜닝하는 것이 전제 조건입니다:

> "We find that fine-tuning the base checkpoints of the video world models is important for plausibly imagining task-relevant rare events, such as collisions or coffee-bean spills, and for aligning the train- and test-time distributions to improve video quality." (§D.1)

(스티어링은 WM 분포가 지지하는 결과만 끌어낼 수 있으므로, 실패·충돌이 분포에 들어 있도록 만드는 파인튜닝 데이터 구성이 방법의 숨은 전제입니다. 주행은 PAI-AV + nuScenes + Nexar 충돌 데이터로 13,750 iteration(batch 256), 조작은 성공·실패를 모두 포함한 태스크당 약 150개 원격조작 궤적으로 10,000 iteration(lr `1e-6`, batch 64) 파인튜닝합니다. 태스크별 궤적 수: Block Stack 250 / Knife Put 170 / Stacked Utensil Pick 200 / Coffee Bean Pour 100 / Open Coffee Bag 170 / Open Candy Bag 150 — Table 7.)

**WM·스티어링 하이퍼파라미터 (Table 3, 5, 6)**

| 항목 | Vista (주행) | Ctrl-World (조작) | Dubins car (통제 실험) |
|------|------|------|------|
| 카메라 수 | 1 | 3 | 1 (렌더링) |
| 이미지 해상도 | `576×1024×3` | `192×320×3` | `128×128×3` |
| 비디오 주파수 | `10 Hz` | `5 Hz` | — |
| 예측 horizon | 25 | 5 | 1 |
| 노이즈 차원 `D` | 921,600 | 57,600 | 1,024 |
| 행동 차원 | 8 (미래 waypoint 4개) | 40 ( `8×H`, 관절 위치+그리퍼) | 1 (연속 각속도) |
| Denoising steps | 50 | 50 | 5 |
| CFG scale | 2.5 | 2.0 | — |
| 최적화 iterations | 20 | 10 | 10 |
| Step size $`\eta`$ | 1.0 | 1.0 | 1.0 |
| 기울기 스케일 $`\beta`$ | 300.0 | 100.0 | 10.0 |
| $`\lambda_1`$ (norm) | 0.5 | 0.2 | 1.0 |
| $`\lambda_2`$ (iso) | 10.0 | 0.1 | 0.5 |
| 등방성 부분벡터 크기 `k` | 192 | 240 | 16 |
| 등방성 치환 횟수 | 1,000 | 1,000 | 100 |
| $`\lambda_3`$ (spec) | 100.0 | 100.0 | 5.0 |

계수들( $`\beta, \lambda_1, \lambda_2, \lambda_3`$ )은 WM·노이즈 차원·VLM 에 따라 튜닝되며(§4.3), WM 간 최대 100배 차이가 나는 점이 이식 시 유의점입니다. 검증자는 주행에 Wolf 파인튜닝 Qwen2.5-VL-7B-Instruct + X-CLIP, 조작에 Qwen3-VL-4B-Instruct(3뷰 동시 입력)를 사용합니다.

**비용 (§B.6, Table 1)** — 시간 복잡도는 Best-of-N 의 $`N(K \mathcal{T}_{\mathrm{denoise}} + \mathcal{T}_{\mathrm{verifier}})`$ 대비 StressDream 이 $`N(K \mathcal{T}_{\mathrm{denoise}} + 2\mathcal{T}_{\mathrm{verifier}})`$ — 검증자 역전파 1회만 추가됩니다 (근사 없이는 $`2K \mathcal{T}_{\mathrm{denoise}}`$ 로 뜀).

> "In practice, using Vista [11] with $`K = 50`$ denoising steps on a single H100 GPU, a single generation takes approximately 1–2 minutes, while noise optimization with $`N = 20`$ iterations takes about 30 minutes." (§B.6)

(지배 비용은 비디오 생성 자체이므로, WM 이 빨라지면(shortcut/consistency 모델) 스티어링도 그대로 빨라지는 구조입니다.)

**정책 개선 셋업 (§6.2, §D.5)** — π0.5-DROID 를 태스크당 40개 전문가 시연으로 가중 회귀(weighted flow-matching) 파인튜닝합니다. 각 시연의 상상 롤아웃을 실패 방향으로 스티어링한 뒤, 스티어링 하에서도 성공으로 남는 궤적에 가중치 1.0, 실패로 스티어링되는 궤적에 0.1 을 부여합니다 (손실과 데이터 샘플링 양쪽에 적용). 손 목 카메라 + 3인칭 카메라 2뷰, 관절 위치 행동, 10k step (H100 1장), 추론 시 open-loop 행동 horizon 16 입니다. 참고로 동일 셋업에서 diffusion policy 를 스크래치 학습하면 성능이 낮았다고 보고합니다.

---

## 📊 실험 설정과 결과

**실험 축 요약**

| 축 | WM / 정책 | 셋업 | 핵심 지표 | 결과 |
|---|---|---|---|---|
| 통제 실험 (§5) | 자체 SVD 계열 소형 WM | Naughty Dubins car (확률 `p=0.2` 제어 부호 반전), 평가 5,000 궤적 | 실패 검출 TPR / TNR | StressDream 만 높은 TPR·TNR 동시 달성; $`\mathcal{C}_{\mathrm{pla}}`$ 제거·CG 는 TNR 붕괴 (Fig. 2) |
| 강건 평가 — 주행 (§6.1) | Vista (파인튜닝) | PAI-AV 8개 안전-critical 이벤트 100쌍 + Nexar 충돌 200클립 | WMB target alignment / video quality, Gemini 판정 | 정렬 점수에서 Best-of-N 압도, $`\mathcal{C}_{\mathrm{pla}}`$ 가 품질 보존 (Fig. 4, 19) |
| 강건 평가 — 조작 (§6.1) | Ctrl-World (파인튜닝) | 6개 접촉 집약 태스크, 실패 궤적 100개 | 실패 검출 recall (인간 판정) | 54% → 94% (Fig. 5) |
| 정책 개선 (§6.2) | π0.5-DROID | 태스크당 40 시연 가중 파인튜닝, 태스크당 20 롤아웃 | 실제 로봇 성공률 | Nominal 39% → Robust 71% (Fig. 8) |

**통제 실험 — 가능할 때만 실패를 상상 (§5)**

참 동역학( $`s_{t+1} = s_t + \Delta t\,[v \cos(\theta_t),\ v \sin(\theta_t),\ \delta_t a_t]`$, $`\delta_t \in \{-1, 1\}`$ 이 확률 0.2 로 반전 — 식 9)을 아는 Dubins car 에서, 10,000회 몬테카를로로 낙인한 참 실패 가능성 대비 WM 상상의 실패 검출을 평가합니다. StressDream 은 높은 TPR(실패 가능 궤적을 실제로 검출)과 높은 TNR(안전 궤적을 오검출하지 않음)을 동시에 달성하는 유일한 방법입니다. 낙관적 스티어링 ablation(§C.2)에서도 참 최적 안전 점수 0.55 대비 정칙화 포함 시 0.53 으로 근접하는 반면, 정칙화 제거 시 1.66 으로 참 동역학이 지지하지 않는 수준까지 과잉 스티어링됩니다 (Fig. 16).

**정칙화 ablation — 노이즈 통계와 OOD 점수 (§C.3, Table 4)**

| Method | Norm Conc. ↑ | Isotropy ↓ | Spectral White. ↓ | OOD Score ↓ |
|---|---|---|---|---|
| Nominal | −7.6 | 0.02 | 0.03 | 167.1 |
| Best-of-N | −7.6 | 0.02 | 0.03 | 167.4 |
| Classifier Guidance | −7.6 | 0.02 | 0.03 | 194.5 |
| StressDream | −6.3 | 0.02 | 0.00 | 171.7 |
| StressDream (w/o all reg.) | −717.6 | 0.83 | 0.36 | 696.6 |
| StressDream (w/o norm) | −31.7 | 0.08 | 0.06 | 206.1 |
| StressDream (w/o iso) | −5.6 | 0.03 | 0.11 | 187.3 |
| StressDream (w/o spec) | −6.3 | 0.00 | 0.11 | 172.2 |

세 정칙자를 모두 쓴 StressDream 은 노이즈 통계·잠재 OOD 점수(flow-matching 밀도 대리) 모두 명목 생성 수준을 유지하고, 정칙화 전면 제거는 OOD 점수를 4배( `167→697` ) 폭증시킵니다. 개별 제거도 각각 OOD 를 높여 세 통계가 상보적임을 보입니다. 흥미롭게도 classifier guidance 는 초기 노이즈 통계는 정상( `−7.6` )이지만 OOD 점수가 194.5 로 오릅니다 — 경로 왜곡이 노이즈가 아닌 생성물 수준에서 분포를 이탈시킨다는 진단입니다.

**강건 평가 — 실패 검출 recall (§6.1)**

> "(ii) on state-of-the-art video world models for autonomous driving [11] and robotic manipulation [12], STRESSDREAM enables robust policy evaluation by detecting high-impact outcomes, such as task failures, with substantially higher recall (54%→94%); and (iii) this robust evaluation improves policy by promoting robust actions that avoid potential failures, increasing the success rate of a Vision-Language-Action (VLA) policy [20] (39%→71%)." (§1)

(본 논문의 두 headline 수치입니다. Fig. 5 는 Nominal(N=1) / Best-of-N(N=10) / StressDream 세 막대에 71% / 54% / 94% 를 표기하는데, PDF 텍스트 추출로는 베이스라인 두 값(71·54)의 막대 대응을 확정할 수 없어 위 §1 인용의 "54%→94%" 를 수치 앵커로 삼습니다. StressDream = 94% 는 확정.)

> "STRESSDREAM detects task-failure events in imagination with higher recall, whereas random generations are often overly optimistic and miss possible failures, as shown in Fig. 5." (§6.1)

(같은 관찰·행동 입력에서 무작위 상상은 낙관 편향으로 실패를 놓치고, 스티어링은 실패 가능성을 드러냅니다. 태스크별 세부(Fig. 22)에서도 전 태스크에서 recall 우위이며, 데이터에 성공으로 낙인된 궤적 일부도 실패로 스티어링되는데 — 저자들은 부분 관찰 하에서 "우연히 성공한 위험 행동"이므로 이를 단순 false positive 로 볼 수 없다고 논증합니다.)

**그럴듯함 보존 — 지지되지 않는 이벤트는 생성 불가 (§6.1, §E.3)**

> "Fig. 6 shows that the base model cannot imagine collision outcomes even with steering, achieving lower target-alignment scores than random sampling from the collision-finetuned model." (§6.1)

(스티어링이 환각 생성기가 아니라는 핵심 통제 실험입니다 — 충돌 데이터로 파인튜닝하지 않은 base Vista 는 스티어링해도 충돌을 상상하지 못합니다. 즉 StressDream 은 WM 분포가 지지하는 이벤트만 끌어냅니다.)

> "Imaginations are grounded in plausible outcomes: when target outcomes are not supported by the WM distribution, e.g., spilling sticky candies or from a closed bag, STRESSDREAM does not imagine them." (§6.1, Fig. 3)

(조작에서도 동일한 성질이 확인됩니다 — 열린 커피 봉지에서는 쏟아짐을 상상하지만, 끈적한 캔디·닫힌 봉지에서는 쏟아짐 프롬프트를 줘도 상상하지 않습니다. 물리적 개연성 판단이 WM 분포에 위임되어 있다는 뜻입니다.)

주행 정량 평가(Fig. 4, 19)에서는 WMB instruction-following(0–3)과 Gemini-3.0 판정(0–10) 모두에서 스티어링 스텝에 따라 정렬 점수가 상승하며 Best-of-N 을 상회하고, $`\mathcal{C}_{\mathrm{pla}}`$ 없이 최적화하면 WMB physics adherence(0–5)·commonsense(0–2) 및 WorldLens 의 subject/temporal consistency·depth discrepancy 가 유의미하게 악화됩니다. 롱테일 이벤트 발견(§E.2)에서는:

> "Even with 40 samples, Best-of-N sampling does not match the target-alignment score achieved by STRESSDREAM." (§E.2)

(1차 경사 탐색이 0차 무작위 탐색보다 드문 이벤트 발견에 표본 효율적이라는 정량 근거 — StressDream 은 20 스텝, Best-of-N 은 40 샘플입니다.)

**정책 개선 (§6.2, §E.4)**

> "we fine-tune π0.5-DROID with 40 successful demonstrations per task using a weighted regression objective [13], and compare two settings: Nominal π FT 0.5 , which assigns a uniform weight of 1.0 to all trajectories, and Robust π FT 0.5 , which assigns weight 1.0 to trajectories that remain successful under steering toward task failures and weight 0.1 to trajectories that fail in steered imaginations." (§6.2)

(개선 메커니즘은 단순한 시연 재가중입니다 — 스티어링된 비관적 상상이 "이 시연은 그럴듯한 결과 분포에 실패를 포함한다"는 라벨러 역할을 하고, 그 시연의 손실·샘플링 가중치를 0.1 로 낮춥니다.) 태스크당 20 롤아웃 실제 로봇 평가에서 Robust 39%→71% (Fig. 8), 태스크별(Fig. 26)로도 6개 태스크 전부에서 Nominal 대비 우위입니다. Robometer 점수(Fig. 21)로도 스티어링된 상상이 베이스라인 대비 일관되게 낮은 task-progress/success 를 받아 "비관성"이 정량 확인됩니다.

---

## ⚖️ 한계

- **그럴듯함 = WM 분포 지지, 물리적 개연성 아님** — 저자 명시 한계입니다. 정칙화가 지키는 것은 "노이즈가 가우시안 전형 집합 안"이라는 성질이고, 생성의 물리성은 전적으로 기반 WM 품질에 위임됩니다. WM 이 애초에 비물리적 영상을 내면 그 안에서 스티어링하고, WM 훈련 분포에 없는 실제 위험은 상상하지 못합니다.

> "Thus, our notion of plausibility is limited to what the WM supports, and does not necessarily imply physical plausibility in the real world, underscoring the need for diverse robot data to train high-fidelity WMs with physically consistent predictions." (§7)

(이 한계는 방법의 전제 조건과 동전의 양면입니다 — §D.1 에서 실패 포함 데이터로 WM 을 파인튜닝해야 했던 이유이며, 성공-only 데이터로 학습된 WM 위에서는 비관적 스티어링 자체가 성립하지 않습니다.)

- **국소 정제이지 전역 탐색이 아님** — i.i.d. 가우시안 쌍의 거리가 $`\sqrt{2D}`$ 에 집중하는 반면 최적화 전후 노이즈 거리는 그보다 훨씬 작다는 자체 분석으로, 탐색이 초기 노이즈 근방의 국소 정제임을 인정합니다. 초기화가 나쁘면 존재하는 최악 사례를 놓칠 수 있고, Best-of-N 과의 결합·가치 함수 유도를 확장 방향으로 남깁니다.

> "The optimization in STRESSDREAM should be viewed as a local refinement of the initial noise rather than a global search over all possible futures." (§F)

- **프롬프트 의존성과 reward hacking** — 목표 이벤트를 텍스트로 지정해야 하므로 효과가 프롬프트 품질에 의존하고, 점수만 오르고 생성은 의미 있게 변하지 않는 reward hacking 이 발생할 수 있습니다 (VLM 기준이 스크래치 보상 모델보다 강건하다고는 하나 소거되지는 않음).
- **런타임** — 상상 1회에 수 분, Vista 20-iteration 최적화에 약 30분 (H100 1장). 온라인·폐루프 용도는 불가능하고 오프라인 평가·데이터 재가중 전용입니다. 자기회귀 롤아웃에서는 세그먼트별 노이즈를 순차 최적화할 뿐 결합 최적화는 미해결입니다.
- **(추론된 갭) 평가의 인간 의존과 규모** — 조작 실패 검출은 인간 판정, 정책 개선은 태스크당 20 롤아웃·단일 embodiment(DROID 셋업)로, 통계적 규모가 크지 않습니다. recall 의 상대 비교는 설득력 있으나 절대 수치의 재현 분산은 미지수입니다.
- **(추론된 갭) 기울기 근사의 이론 공백** — 대각 Jacobian 가정은 경험적 관찰(Ahn et al. 인용)에 기대며, "전체 기울기가 오히려 실패한다"는 결과(Fig. 14)는 실용적으로는 희소식이지만 근사가 왜 잘 되는지의 원리적 이해는 열려 있습니다. WM 아키텍처가 바뀌면(예: latent 예측형) 근사 유효성을 재검증해야 합니다.
- **(추론된 갭) 하이퍼파라미터 이식성** — $`\beta`$ 와 $`\lambda`$ 계수가 WM 간 최대 100배 차이( `β: 10→300`, `λ₂: 0.1→10` )로, 새 WM·새 VLM 조합마다 상당한 튜닝이 필요해 보입니다. 튜닝 절차 자체는 본문에 기술되지 않습니다.

---

## ♻️ 재현성

- **코드** — 공개: `https://github.com/CMU-IntentLab/StressDream` (p.18 명기; 본 분석 환경의 네트워크 정책으로 도달 검증은 불가). 기반 WM 은 공개 저장소를 사용합니다: Vista(`OpenDriveLab/Vista`), Ctrl-World(`Robert-gyj/Ctrl-World`), 정책은 openpi 의 π0.5-DROID(`Physical-Intelligence/openpi`).
- **데이터** — 주행: PAI-AV(HuggingFace `nvidia/PhysicalAI-Autonomous-Vehicles`), nuScenes, Nexar Collision Prediction Dataset — 모두 공개. 조작: DROID(공개) + 자체 수집 원격조작 궤적(태스크당 100–250개, 성공·실패 포함) — 공개 여부 본문 미명시. 평가용 큐레이션(주행 100 이벤트 쌍 + 충돌 200클립, 조작 실패 100궤적)도 공개 여부 미명시.
- **모델·검증자** — Qwen2.5-VL-7B-Instruct(Wolf 파인튜닝), X-CLIP, Qwen3-VL-4B-Instruct 등 오픈소스 VLM 사용 (기울기 필요로 API 모델 배제). 평가 판정자는 WorldModelBench, WorldLens, Robometer, Gemini-3.0.
- **하드웨어** — H100 80GB 단일 GPU 기준 런타임 보고; 연산은 PSC Bridges-2 (NSF ACCESS) 지원.
- **재현 리스크** — 자체 원격조작 파인튜닝 데이터와 인간 판정 기반 조작 평가가 비공개일 경우 조작 축 수치 재현은 어렵고, 주행 축(공개 데이터 + WMB)은 상대적으로 재현 가능성이 높습니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P5(World Model) — 주 pillar.** 본 논문은 WM 을 새로 제안하지 않고 *기존 생성형 WM 을 정책 평가·개선에 쓰는 방식*을 바꾸는 usage-layer 기법으로, P5 의 role 결정들에 직접 닿습니다.
  - **D28(world-model role)** — v1 은 "latent dynamics prior + future-prediction auxiliary 를 공동 학습"이고 **eval-in-imagination 은 명시적 deferred 역할**입니다. StressDream 은 그 deferred 역할이 활성화될 때의 평가 프로토콜을 바꾸는 증거입니다: 명목 상상 기반 평가는 낙관 편향(recall 54%)이 있으므로, eval-in-imagination 을 하려면 비관적(min-max) 스티어링을 함께 채택해야 한다는 것. 또한 "스티어링된 상상 → 시연 재가중 파인튜닝" 루프는 data-augmentation/policy-improvement 역할(D28 tracked)의 구체적 레시피입니다.
  - **D30(prediction space)** — v1 은 latent / 3D-flow 예측이고 raw-pixel 은 "eval-in-imagination 현실성 용도로 tracked" 상태입니다. StressDream 은 raw-pixel 확산 WM 의 초기 노이즈·결정론적 샘플러 구조에 *의존*하는 기법이므로, deferred raw-pixel 분기의 효용을 높이는 쪽으로 증거를 보탭니다 — 역으로 우리 v1 latent(JEPA 계열) 선택에는 직접 이식되지 않습니다 (⚠️ 참조).
  - **D31(action conditioning)** — 행동 조건부 WM(Vista waypoint, Ctrl-World 관절 위치)이 전제이므로 v1 방향과 일치. 새 결정 변화는 없습니다.
  - **D29 / D32** — 통합 아키텍처·egocentric hand-object 축은 건드리지 않습니다 (추론 시점 기법이므로 integration 무관, 데이터는 DROID 3인칭 셋업).
- **Identity 지지** — "RL-as-core 불가, generalized task 는 reward-engineering 불가"라는 우리 Identity 와 정합적입니다: 본 논문은 정책 개선을 RL 이 아닌 *가중 모방(weighted flow-matching)* 으로 수행하고, 보상 함수 대신 VLM 검증자 + WM 상상을 씁니다. 반면 주행 절반은 P5 anti-topic(driving world models)에 해당하나, 조작 절반(Ctrl-World + π0.5 실제 로봇 평가)이 manipulation eval 요건을 충족해 pillar 관련성이 성립합니다.
- **P1–P4, P0** — 직접 닿는 Decision 없음. π0.5 파인튜닝은 등장하지만 lineage·recipe·보존 전략(P4 D19–D23)에 대한 기여가 아니라 개선 대상일 뿐입니다.

---

## ✨ 핀 논문 대비 델타

- **vs. Ctrl-World (P5 §5 핀, raw-pixel branch / eval-in-imagination)** — 가장 직접적인 비교축입니다. Ctrl-World 는 제어가능 생성형 WM 자체와 "명목 상상으로 정책 평가·데이터 증강"이라는 사용법을 제공했습니다. StressDream 은 *바로 그 Ctrl-World 를 동결한 채* 위에 얹혀, 명목 상상을 min-max 최악-사례 상상으로 바꿉니다. 델타는 WM 이 아니라 WM 의 *추론 시점 활용 계층*: 분포를 학습해 놓고 점추정만 쓰던 간극을 초기 노이즈 최적화로 메운 것이 새롭습니다.
- **vs. Being-H0.7 / VLA-JEPA / AHEAD (P5 핀, latent 계열)** — 직교합니다. 이들은 WM 을 정책 안에 *통합*(잠재 예측 보조/prior)하는 반면, StressDream 은 외부 생성형 WM 을 정책 *바깥에서* 평가자로 씁니다. latent 계열에는 최적화할 초기 노이즈·결정론적 샘플러가 없어 기법이 그대로 이식되지 않는다는 점이 오히려 중요한 델타 정보입니다.
- **vs. World Guidance (P5 핀)** — 조건 공간 world modeling 으로 행동 생성을 돕는 방향(생성 시점)이고, StressDream 은 평가·데이터 가중 방향(검증 시점)입니다. 역할이 겹치지 않습니다.
- **부가 델타** — 정책 개선의 가중 회귀 목적식 자체는 인용 [13](VLAW, Guo et al.)의 것이고, StressDream 의 기여는 가중치를 결정하는 신호를 "명목 상상"에서 "비관적 스티어링 상상"으로 바꾼 부분입니다.

---

## ⚙️ 의사결정 함의

- **D28 deferred(eval-in-imagination) 활성화 시 평가 프로토콜에 비관성 요건 추가** — WM 기반 정책 평가를 도입한다면 지표를 "명목 상상 성공률 상관"이 아니라 **실패 검출 recall**(참 실패 궤적 중 상상이 실패를 드러내는 비율)로 잡고, 명목/Best-of-N/스티어링 세 모드를 비교 리포트해야 합니다. 본 논문 기준 명목 평가는 recall 을 최대 40%p 손해봅니다.
- **WM 파인튜닝 데이터 계약에 "실패 포함" 조항** — 스티어링이든 아니든, 평가용 WM 은 실패·위험 결과가 분포에 들어가도록 태스크당 O(100–250) 궤적 규모의 성공+실패 혼합 데이터로 파인튜닝해야 합니다 (base 모델은 스티어링해도 충돌을 상상하지 못함 — Fig. 6). 우리 P0/P4 데이터 수집 계획에서 실패 궤적을 버리지 말고 별도 태깅해 보관하는 것이 구체적 액션입니다.
- **시연 재가중이라는 저비용 정책 개선 레버** — `demo_weight ∈ {1.0, 0.1}` 을 flow-matching 파인튜닝 손실·샘플링에 곱하는 것만으로 39%→71% 를 얻었습니다. 이 레버는 WM 스티어링 없이도 임의의 위험 라벨(휴리스틱, 인간 태깅)로 즉시 시험 가능하며, 우리 π 계열 적응 단계(P4 D21 Stage 3)의 config 에 `per_demo_weight` 훅을 미리 뚫어 둘 가치가 있습니다.
- **VLM-as-verifier 설계 규칙** — 검증자를 쓴다면 (a) yes/no 단일 토큰 로그확률 차이로 점수화(미분가능·API 모델 배제), (b) 멀티뷰 동시 입력 필수(단일 뷰 검출 급락), (c) CLIP 계열은 조작 장면에 비효과적 — 이 세 가지가 그대로 우리 스택의 검증자 스펙이 됩니다.
- **스티어링 도입 시 config 블록** — `{opt_iters: 10–20, step_size: 1.0, beta: 100–300, lambda_norm/iso/spec, iso_k, iso_perms, grad_clip: ±0.3, grad_norm_clip: 1.0, shell_proj_threshold: 3.0, momentum: none}` — 특히 모멘텀 금지와 껍질 사영은 놓치기 쉬운 안정화 장치입니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 검증) VLM 검증자가 손가락 수준 실패를 볼 수 있는가** — 본 논문의 실패 이벤트는 물체 수준(쏟아짐·낙하·전도)입니다. 우리의 실패 모드는 per-finger 접촉 상실·슬립·인핸드 회전 실패로 훨씬 미세합니다. WM 없이도 지금 확인 가능: 손 조작 실패 영상 몇 개에 Qwen3-VL yes/no 토큰 채점을 돌려 `192×320` 급 해상도에서 슬립/파지 실패가 분리되는지 봅니다. 분리 안 되면 이 파이프라인 전체가 우리 도메인에서 무너집니다.
- **D30 표현 불일치 — latent WM 에는 이식 불가** — 우리 v1 예측 공간은 latent/3D-flow(JEPA 계열)로, 최적화할 가우시안 초기 노이즈도 결정론적 확산 샘플러도 없습니다. StressDream 채택은 곧 deferred raw-pixel 분기(Ctrl-World 류)를 평가 전용으로 별도 운용한다는 결정이며, 그 컴퓨트·데이터 비용을 먼저 산정해야 합니다.
- **WM 충실도 전제 — 손-물체 접촉 동역학** — Ctrl-World 는 팔 수준 tabletop 셋업입니다. 22-DOF 손의 접촉 결과(미세 슬립, 마찰 변화)를 raw-pixel WM 이 분포로 담을 수 있는지 자체가 미검증이고, "plausibility = WM 지지"라는 한계 때문에 WM 이 못 담으면 스티어링은 조용히 아무것도 못 찾습니다(false negative). 싼 대리 실험: 우리 실패 포함 원격조작 데이터 소량으로 Ctrl-World 급 WM 을 파인튜닝해 실패 상상 재현율부터 측정.
- **런타임 예산** — 상상 1회 수 분 × 시연 수백 개 × 스티어링 10–20 iteration 이면 시연 재가중 한 번에 GPU-일 단위입니다. 오프라인 배치 전용으로만 계획하고, 폐루프 평가·System0(P3) 등 실시간 경로에는 배제해야 합니다.
- **하이퍼파라미터 재튜닝 비용** — $`\beta`$ · $`\lambda`$ 가 WM 마다 100배 스케일로 다르므로, 새 WM/VLM 조합에서 그럴듯함-정렬 트레이드오프 곡선(Fig. 4 류)을 다시 그려야 합니다. 튜닝 실패 시 reward hacking(점수만 상승)과 과잉 스티어링(비현실 실패 상상 → 멀쩡한 시연 강등)이 양방향 위험입니다.

---

## 💡 컨텍스트 제안

- **P5 §5 Methodology base (non-pinned) 에 StressDream 추가 제안** — 근거: D28 의 deferred 역할(eval-in-imagination)이 활성화되는 순간 필요해질 "비관적 평가 프로토콜"의 현재 최선 레퍼런스이고, 핀 논문 Ctrl-World 와 직접 결합되는 usage-layer 기법이기 때문입니다. 항목 예: `| StressDream | arXiv:2606.00267 | 초기 노이즈 최적화로 생성형 WM 을 최악-사례로 스티어링; eval-in-imagination 강건화 + 시연 재가중 (D28/D30) |`. 핀 교체는 불필요합니다 (WM 자체 기여가 아니므로 8핀 캡을 소모할 사안 아님).
- **Decision 변경 제안 없음** — D28/D30 의 v1(latent 우선, raw-pixel deferred)을 뒤집을 증거는 아닙니다. 다만 D30 의 raw-pixel tracked 사유("eval-in-imagination 현실성")에 "비관적 스티어링 가능성"이 근거로 하나 추가된 상태라는 점을 기록해 둘 만합니다.

---

> 💡 base 매핑은 `/implement-design analysis/2606.00267/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
