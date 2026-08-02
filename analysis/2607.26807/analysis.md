# Paper Analysis — Route by Kinematics, Act by Observation: Kinematics-Supervised Expert Routing in MoE-Augmented VLA

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Route by Kinematics, Act by Observation: Kinematics-Supervised Expert Routing in MoE-Augmented VLA |
| 저자 | Tianhang Yang, Yanze Zheng, Junjie Wang, Wei-Bin Kou, Ruotong Li, Yujiu Yang |
| 링크 | [arXiv:2607.26807](https://arxiv.org/abs/2607.26807) |
| 발행일 / 버전 | 2026-07-29 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-08-02 |
| 관련 Pillar | P1, P4, P2, P0 |
| 태그 | vla-arch, flow-matching, peft |

---

## 🧭 한 줄 요약 (TL;DR)

MoE-VLA 의 라우터가 실패하는 이유는 "어떤 expert 를 쓸지"를 결정하는 진짜 기준이 시각·언어 유사도가 아니라 **동작 기구학(kinematics)의 동형성**인데, 그 기구학 신호가 추론 시점에는 존재하지 않기 때문이라고 진단합니다. KinRT 는 학습 시에만 접근 가능한 action chunk 를 오프라인 클러스터링해 얻은 **kinematic archetype ID 를 라우터의 정답 라벨로 주입**하고(교차엔트로피 supervision), 추론 시에는 관측만으로 expert 를 배정하는 비대칭 브리지를 세워 RoboTwin 에서 23.26%, 자체 제작 DIYRobot 플랫폼에서 20.27% 상대 개선을 보고합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — VLA 의 과제 레퍼토리가 커질수록 과제별 기구학이 이질적이 되고, 이를 하나의 공유 파라미터 공간에 압축하면 gradient 간섭이 발생합니다. MoE 는 expert 특화로 이를 완화할 수 있지만, 그 이득 전부가 **라우터가 올바른 expert 를 고르는가**에 걸려 있습니다.
- **기존 접근의 한계 — 관측 기반 암묵 라우팅** — 통상의 sparsely-gated MoE 라우터는 backpropagation 만으로 학습되며 명시적 기준이 없습니다. 조작 도메인에서는 시각적으로 거의 동일한 장면이 전혀 다른 기구학을 요구하고("lifting the cup" vs "unscrewing the cap"), 시각적으로 다른 장면이 동일한 기구학을 공유하므로("pushing a plate" vs "pushing a book") 관측 유사도 기반 배정은 물리적으로 틀린 배정을 낳습니다.
- **기존 접근의 한계 — 라우터 붕괴** — NLP 에서도 암묵 라우팅은 expert 이용률 불균형과 의미가 모호한 특화를 낳는 것이 관측되어 있고, 기구학 이질성이 훨씬 심한 조작에서는 이 문제가 증폭됩니다. 논문은 실제로 Hi-MoE 가 다수 과제에서 0 성공으로 붕괴하는 것을 재현합니다.
- **본 논문의 가설** — 대부분의 의미적으로 다른 조작 과제가 소수의 **kinematic archetype** 으로 수렴한다(kinematic prototype collapse)면, 그 archetype ID 를 라우터의 지도 신호로 쓸 수 있습니다. 학습 시에만 존재하는 action 기구학을 특권 정보(privileged information)로 삼아 관측 공간으로 증류하면, 추론 시 관측만으로도 물리적으로 타당한 expert 배정이 가능하다는 것이 논문의 가설입니다.
- **왜 지금 중요한가** — π 계열을 포함한 최신 VLA 가 flow-matching action expert 를 표준화하면서 action head 의 용량 확장 수단으로 MoE 가 자연스러운 다음 수순이 되었고, 그 병목이 라우터라는 점이 실증적으로 드러나고 있습니다. 라우터를 **지도 학습 가능한 분류 문제**로 재정의하는 것은 추가 추론 비용 없이 적용 가능한 저비용 개입입니다.

---

## 🧩 핵심 기여

- **kinematic prototype collapse 현상 규명** — RoboTwin 의 이질적 8개 과제 162,545 프레임을 action-velocity 기술자로 클러스터링하면 4개의 기구학 archetype 으로 수렴함을 보이고, expert 수를 그 granularity 에 맞춰 설정합니다.
- **KinRT — 기구학 지도 명시 라우팅** — 오프라인 K-means 클러스터 ID 를 정답으로 라우터를 교차엔트로피로 학습시켜, 암묵적·관측 주도 라우팅을 명시적·기구학 주도 dispatching 으로 전환합니다.
- **비대칭 브리지(asymmetric bridging)** — 학습 시 action 공간의 특권 기구학 구조를 추론 시 관측 공간으로 증류합니다. LUPI 의 기존 로보틱스 적용이 *정책* 을 지도했다면, 본 논문은 *라우터* 를 지도한다는 점이 차별점입니다.
- **global routing + shared/routed 병렬 FFN** — 레이어별 독립 라우팅 대신 관측당 1회 라우팅해 18개 블록에 브로드캐스트하고, 각 블록 FFN 을 shared 분기(사전학습 FFN)와 routed 분기의 1/2·1/2 합성으로 대체합니다.
- **DIYRobot 플랫폼 + 벤치마크** — 3D 프린팅 기반 14-DoF 양팔 플랫폼(2,000 USD 미만)과 5개 과제 × 100 시연의 실세계 벤치마크를 구축하고 공개를 예고합니다.
- **광범위한 비교 실험** — dense VLA(OpenVLA / RDT-1B / π0 / π0.5), MoE-VLA(Hi-MoE / AdaMoE), 그리고 KinRT 를 여러 백본에 얹은 plug-in 변형까지 시뮬레이션 1,600회 + 실세계 250회 테스트로 비교합니다.

---

## 🔑 기술 키워드

- **Kinematic Archetype** — 의미가 서로 다른 과제들이 실제 관절 궤적 수준에서 수렴하는 소수의 "동작 원형". 예컨대 접시를 밀든 책을 밀든 팔이 그리는 궤적은 사실상 같은 부류라는 관찰이며, 본 논문에서 expert 1개가 담당하는 단위입니다.
- **Kinematic Prototype Collapse** — 의미적으로 이질적인 과제 집합이 기구학 공간에서는 소수 클러스터로 붕괴하는 현상. KinRT 의 전제이자, expert 개수를 정하는 근거입니다.
- **KinRT** — Kinematics-supervised explicit routing. 라우터를 "관측 → 기구학 원형" 분류기로 재정의한 학습 패러다임입니다.
- **Asymmetric Bridging Mechanism** — 학습 때만 쓸 수 있는 정보로 학습하고 추론 때는 없이 동작하도록 만드는 다리. 시험 전에만 정답지를 보고 시험장에서는 못 보는 상황에 대응하며, 여기서는 action 기구학이 그 정답지입니다.
- **Learning Using Privileged Information (LUPI)** — 특권 교사 / 학생 구도의 이론적 뿌리. 학습 시에만 주어지는 정보가 추론 시 일반화를 개선할 수 있다는 원리입니다.
- **Global Routing** — 레이어마다 따로 라우팅하지 않고 관측당 한 번 결정해 전 블록에 공유하는 방식. "이건 빨간 블록 핸드오버다"라는 판단은 레이어에 따라 달라지지 않는다는 논리에 기댑니다.
- **Mixture-of-Transformers (MoT)** — prefix(시각·언어) 스트림과 suffix(액션) 스트림이 스트림별 파라미터를 유지한 채 attention 으로만 상호작용하는 구조. π 계열 VLA 의 표준 골격입니다.
- **Shared-Routed Parallel FFN** — 사전학습 FFN 을 항상 켜두고(shared) 그 위에 선택된 expert FFN 을 더하는 잔차형 MoE 합성. expert 가 일반 능력을 처음부터 재학습하지 않고 증분 특화만 배우게 합니다.
- **Balanced Sampling Coefficient** — 소수 archetype 노출을 보장하기 위해 클래스 빈도의 거듭제곱으로 샘플 가중치를 주는 계수 $`\alpha`$. 경험 분포($`\alpha=0`$)와 균등 분포($`\alpha=1`$) 사이를 보간합니다.
- **Flow Matching** — 플로우 매칭. 노이즈에서 청정 action chunk 로 향하는 속도장을 회귀로 학습해 연속 액션을 생성하는 방식이며, KinRT 의 action generator 가 이 형태입니다.

---

## 🔬 방법론

### 직관

이 논문의 출발점은 아주 단순한 관찰입니다. MoE 를 VLA 에 붙이면 expert 마다 다른 동작 유형을 맡기고 싶어지는데, 정작 "지금 어떤 유형인가"를 결정하는 라우터는 카메라 이미지와 언어 지시만 봅니다. 그런데 컵을 드는 장면과 뚜껑을 돌려 여는 장면은 눈으로 보면 거의 같고, 접시를 미는 장면과 책을 미는 장면은 눈으로 보면 완전히 다릅니다. 정작 팔과 그리퍼가 그리는 궤적은 그 반대입니다. 라우터가 보는 신호와 라우터가 맞춰야 할 정답이 서로 어긋나 있는 셈입니다.

그렇다면 정답을 직접 알려주면 됩니다. 시연 데이터에는 실제 관절 궤적이 들어 있으니, 궤적을 잘라 모아 군집화하면 "이 구간은 왼팔 주도 준비 동작", "이 구간은 양팔 대진폭 협응" 같은 소수의 동작 원형이 나옵니다. 논문은 RoboTwin 의 8개 과제 16만여 프레임이 단 4개 원형으로 뭉친다는 것을 보이고, 이 군집 번호를 라우터의 정답 라벨로 씁니다. 라우터는 이제 "관측을 보고 이 순간의 동작 원형을 맞혀라"라는 분류 문제를 풉니다.

문제는 실제 로봇을 돌릴 때입니다. 그 순간에는 아직 action 이 없으므로 궤적 군집을 계산할 방법이 없습니다. KinRT 의 핵심은 이 비대칭을 정면으로 받아들이는 데 있습니다. 학습 때는 궤적이라는 "특권 정보"로 라우터를 가르치고, 배포 때는 그 가르침이 라우터 가중치 안에 남아 있으므로 관측만 넣어도 같은 결정을 재현합니다. 시험 전에만 정답지를 보고 시험장에서는 기억으로 푸는 구조이며, 논문은 이를 action 공간에서 관측 공간으로의 증류라고 부릅니다.

나머지는 이 아이디어를 얹을 자리를 고르는 문제입니다. 라우팅은 레이어마다 따로 하지 않고 관측당 한 번만 해서 전 블록에 공유하고, 각 블록의 FFN 은 사전학습 가중치를 항상 켜둔 shared 분기 위에 선택된 expert 를 더하는 형태로 바꿉니다. 이렇게 하면 expert 는 일반 능력을 처음부터 다시 배우지 않고 자기 담당 동작 원형에 대한 증분만 학습하면 됩니다.

### 아키텍처

![Figure 2 — KinRT 패러다임과 DIYRobot 플랫폼 개요](https://arxiv.org/html/2607.26807/thirteen.jpg)

> "Figure 2: Overview of the proposed KinRT paradigm and our newly introduced DIYRobot platform." (§Introduction)
(오프라인 기구학 클러스터링 → 라우터 지도 학습 → 관측 전용 추론이라는 3단 비대칭 브리지와, 평가에 쓰인 자체 제작 플랫폼을 한 장으로 요약한 그림입니다.)

**백본 골격** — 관측은 $`o=(\mathcal{I},\ell)`$ 로, 다중 뷰 이미지 $`\mathcal{I}`$ 와 언어 지시 $`\ell`$ 로 구성됩니다. 정책은 $`L=18`$ 개 블록의 Mixture-of-Transformers 이며, 두 스트림이 스트림별 attention projection 과 FFN 파라미터를 각자 유지한 채 연결된 prefix-suffix 시퀀스 위 attention 으로만 상호작용합니다.

> "In each block, a prefix stream encodes $`\mathcal{I}`$ into vision tokens by a frozen SigLIP and $`\ell`$ into language tokens through a frozen PaliGemma-2B, while a suffix stream generates action sequence through integrating Gemma-300M and the introduced MoE extension." (§KinRT’s Architecture and Design Philosophy)
(시각·언어 인코더는 얼어 있고 MoE 확장은 액션 스트림에만 들어갑니다 — 즉 KinRT 의 개입 지점은 backbone 이 아니라 action expert 의 FFN 층입니다. prefix 는 시각-언어 문맥 안에서 양방향으로 attend 하고, action 토큰은 prefix 전체와 action chunk 전체에 attend 해 연속 시퀀스를 병렬 예측합니다.)

**MoE FFN 합성** — action head 의 각 블록은 FFN 을 shared 분기와 routed 분기의 병렬 합성으로 대체합니다 (식 1):

$$\mathrm{FFN}_{\text{MoE}}(x)\!=\!\tfrac{1}{2}\,\mathrm{FFN}_{\text{shd}}(x)\!+\!\tfrac{1}{2}\sum\nolimits_{k=1}^{K}\tilde{w}_{k}\,\mathrm{FFN}_{e_{k}}(x)$$

여기서 $`\{e_{k}\}_{k=1}^{K}`$ 는 Top-K 로 선택된 expert 이고 $`\{\tilde{w}_{k}\}_{k=1}^{K}`$ 는 재정규화된 라우팅 가중치($`\sum_{k}\tilde{w}_{k}=1`$)입니다. shared 분기는 사전학습된 FFN 그 자체이며, $`N`$ 개의 expert FFN 은 백본 폭과 동일한 $`d_{\text{model}}=1024,\ d_{\text{mlp}}=4096`$ 로 새로 학습됩니다. $`(1/2,1/2)`$ 고정 가중치는 균등 사전분포로서 초기화 크기 불균형을 막는 장치입니다.

> "This residual design keeps the shared branch permanently active, and supplies a stable starting point before the MoE experts converge." (§KinRT’s Architecture and Design Philosophy)
(이 잔차형 설계의 실질적 효과는 "MoE 를 붙였을 때 초기 성능이 무너지지 않는다"는 것입니다. expert 가 수렴하기 전에도 사전학습 FFN 이 항상 출력을 만들어 주므로, expert 는 일반 능력을 재학습할 필요 없이 증분 특화만 배우면 됩니다.)

**3단 비대칭 브리지** — (i) 오프라인 action 궤적 클러스터링으로 소수 기구학 원형을 발견하고, (ii) 그 클러스터 ID 를 지도 라벨로 삼아 global router 를 학습하며, (iii) 배포 시에는 라우터가 오직 시각-언어 관측만으로 expert 를 dispatch 합니다.

### 기구학 archetype 클러스터링

![Figure 1 — kinematic archetype collapse](https://arxiv.org/html/2607.26807/kinematic_archetypes.jpg)

> "Figure 1: Illustration of kinematic archetype collapse." (§Introduction)
(의미적으로 이질적인 과제 집합이 기구학 공간에서는 소수 원형으로 뭉친다는, 논문 전체의 전제를 시각화한 그림입니다.)

**기술자 구성** — 미래 $`H`$ 스텝의 action 을 묶어 action chunk $`a_{0}\in\mathbb{R}^{H\times D}`$ 를 만들며, $`D`$ 는 $`[\text{Left Arm}\times 6\,|\,\text{Left Gripper}\times 1\,|\,\text{Right Arm}\times 6\,|\,\text{Right Gripper}\times 1]`$ 구조의 액션 차원입니다.

> "In our design, by setting the horizon $`H=50`$, the built action chunk is $`a_{0}\in\mathbb{R}^{50\times 14}`$, which jointly captures where the arms go and how they get there." (§Kinematic Archetype Clustering)
(위치와 속도를 한 기술자에 함께 담는 것이 이 설계의 핵심입니다 — "어디로 가는가"만으로는 같은 지점을 천천히 지나가는 동작과 빠르게 스치는 동작이 구분되지 않기 때문입니다.)

chunk 를 flatten 한 $`H\times D=700`$ 차원이 위치 특징, 인접 action 간 시간 차분을 flatten 한 $`(H-1)\times D=686`$ 차원이 속도 특징이며, 둘을 이어 붙여 1,386 차원 기술자를 얻습니다 (식 2):

$$\phi_{i}=\big[\,\mathrm{vec}(a^{(i)}_{0:H})\;\big\|\;\mathrm{vec}(a^{(i)}_{1:H}-a^{(i)}_{0:H-1})\,\big]\in\mathbb{R}^{1386}$$

여기서 $`i`$ 는 action step 인덱스입니다. 이후 관절·그리퍼 간 스케일 차이를 없애기 위해 표준화하고, 확장성을 위해 PCA 로 64 차원까지 축소한 뒤, 프레임 단위 K-means 로 프레임별 정수 원형 라벨 $`y_{i}\in\{1,2,\cdots,K\}`$ 를 얻어 오프라인 저장합니다.

**RoboTwin 에서 발견된 4개 원형** — 162,545 프레임에서 동작 패턴이 네 개로 붕괴합니다. Cluster 0(36.3%)은 왼팔 주도의 초·중반 준비 구간, Cluster 1(46.0%)은 오른팔 주도의 중·후반 실행 구간, Cluster 2(4.4%)는 대진폭 양팔 협응이라는 가장 복잡한 영역, Cluster 3(13.3%)은 특정 과제에 종속된 원형입니다.

> "Cluster 3 ($`13.3\%`$) is a task-specific archetype dominated by the red-block handover task." (§Kinematic Archetype Clustering)
(네 원형 중 하나가 사실상 단일 과제에 귀속된다는 점은 뒤에서 다룰 일반화 한계의 씨앗입니다 — archetype 집합이 데이터셋에 종속적일 수 있다는 신호입니다.)

> "We accordingly set the number of MoE experts $`N=4`$ to match the kinematic granularity, so that each expert can specialize in one kinematic prototype." (§Kinematic Archetype Clustering)
(expert 개수가 하이퍼파라미터가 아니라 데이터에서 유도된 값이라는 것이 이 설계의 주장입니다. 다만 $`K`$ 자체를 어떻게 골랐는지에 대한 절차나 ablation 은 본문에 없습니다.)

### 라우터 — 입력과 global routing

라우터의 입력을 무엇으로 둘지가 실무적으로 가장 민감한 선택인데, 논문은 원(raw) 시각-언어 임베딩을 명시적으로 배제합니다.

> "We observed in experiments that cosine similarity between raw visual-language embeddings reaches above $`0.95`$, thereby indicating that they are non-discriminative and can not serve as the input of the MoE router." (§Kinematics-Supervised Global Router)
(표현이 붕괴해 있으면 어떤 분류기를 얹어도 경계를 그을 수 없다는 진단입니다. 초기 스텝 action 역시 노이즈 때문에 변별력이 없어 후보에서 빠집니다.)

대신 prefix PaliGemma 의 유효 출력 토큰 전체를 masked mean pooling(패딩 무시)해 요약 벡터 $`c\in\mathbb{R}^{2048}`$ 를 만들고 이를 라우팅 입력으로 씁니다. 라우터는 이 벡터를 **단일 선형층** 하나로 로짓 $`g`$ 에 사상합니다. 학습 시에는 탐색 노이즈 $`\eta\!\sim\!\mathcal{N}(0,\sigma^{2})`$ 를 $`g`$ 에 주입하고(추론 시 비활성) 온도 스케일 softmax 를 적용합니다 (식 3):

$$p=\mathrm{softmax}((g+\eta)/\tau)$$

> "Routing decisions are observation-level instead of layer-specific." (§Kinematics-Supervised Global Router)
(레이어마다 독립적으로 라우팅하지 않는 이유는 판단의 성격 때문입니다 — "이것은 빨간 블록 핸드오버다"라는 명제는 어느 레이어에서든 동일하게 참이므로, 한 번 결정해 18개 블록에 브로드캐스트합니다. 라우터 1회 통과라는 효율 이득에 더해, 레이어별 독립 라우팅보다 안정적이라고 주장합니다.)

$`p`$ 기준 Top-K expert 를 고르고 확률을 재정규화해 $`\{\tilde{w}_{k}\}`$ 를 얻으며, 최종 배정 $`\{e_{1},\cdots,e_{K},\tilde{w}_{1},\cdots,\tilde{w}_{K}\}`$ 가 18개 레이어 전체에 공유됩니다.

### 학습 목표 / 손실

**라우터 지도 손실** — 비대칭 브리지의 핵심은 이 한 줄입니다. 프레임별 기구학 원형 라벨 $`y_{b}`$ 를 관측 $`o_{b}`$ 의 정답으로 삼아 교차엔트로피로 라우터를 학습합니다 (식 4):

$$\mathcal{L}_{\text{sup}}=-\sum\nolimits_{b}y_{b}\log\hat{y_{b}}$$

$`\hat{y_{b}}`$ 는 라우터의 예측 확률입니다.

> "Minimizing $`\mathcal{L}_{\text{sup}}`$ forces the router to recover kinematic structure from observation alone, thereby distilling the privileged action kinematic space into the visual-linguistic observation space." (§Kinematics-Supervised Global Router)
(라우터를 "관측 → 기구학" 회수 문제로 정의한 순간, MoE 의 고질적인 load collapse 문제가 표준 분류 문제의 클래스 불균형 문제로 치환됩니다. 그래서 다음 장치가 load-balancing loss 가 아니라 리샘플링입니다.)

**균형 샘플링** — 다수·소수 archetype 간 클래스 불균형을 완화하기 위해 리샘플링 가중치 $`\alpha`$ 를 도입합니다. 원형 라벨이 $`y_{i}`$ 인 샘플 $`i`$ 와 원형 $`k`$ 의 샘플 수 $`n_{k}`$ 에 대해 샘플 가중치는 $`w_{i}=n_{y_{i}}^{-\alpha}`$ 이고, 미니배치는 $`p_{i}=w_{i}/\sum_{j}w_{j}`$ 에 따라 복원 추출됩니다. 이때 원형 단위 주변 샘플링 확률은 다음과 같습니다.

$$P(y=k)=n_{k}^{1-\alpha}/\sum_{c}n_{c}^{1-\alpha}$$

> "We use $`\alpha=0.5`$ to ensure minority-prototype exposure while retaining part of the natural data distribution." (§Kinematics-Supervised Global Router)
(경험 분포($`\alpha=0`$)와 균등 분포($`\alpha=1`$) 사이의 중간값을 택한다는 뜻이며, 뒤의 ablation 이 이 중간값이 양 극단보다 낫다는 것을 뒷받침합니다.)

**액션 생성 손실** — action generator 는 플로우 매칭입니다. 청정 action $`a_{0}`$ 에 대해 $`\varepsilon\sim\mathcal{N}(0,I)`$ 와 $`t\sim\mathrm{Beta}(1.5,1)`$ 를 뽑아 노이즈 action 을 구성하고 (식 5), 목표 속도는 그 시간 미분입니다 (식 6).

$$x_{t}=t\cdot\varepsilon+(1-t)\,a_{0}$$

$$v_{t}={\partial x_{t}}/{\partial t}=\varepsilon-a_{0}$$

목표 속도가 $`t`$ 에 무관한 상수라는 점이 회귀를 단순·안정하게 만듭니다. 생성기는 MSE 로 최적화됩니다 (식 7):

$$\mathcal{L}_{act}=\mathbb{E}_{t,\,\varepsilon,\,a_{0}}\left\|\hat{v}_{\theta}(x_{t},t,o)-v_{t}\right\|^{2}$$

**추론 절차** — 관측당 추론은 1회 사전계산과 디노이징 루프로 분리됩니다. 사전계산에서 시각-언어 입력이 prefix 스트림을 한 번 통과해 풀링 문맥 $`c`$ 와 global 라우팅 결정 $`\{e_{1}^{\ast},\cdots,e_{K}^{\ast},\tilde{w}_{1}^{\ast},\cdots,\tilde{w}_{K}^{\ast}\}`$ 를 만들고, 이후 $`T`$ 스텝 루프가 선택된 expert 만 호출해 $`\hat{v}_{t}`$ 를 예측하며 $`\Delta t=1/T`$ 만큼 갱신합니다 (식 8):

$$x_{t-\Delta t}=x_{t}-\Delta t\,\hat{v}_{t}$$

학습된 속도가 노이즈 방향을 가리키므로 빼는 방향이 청정 action 쪽입니다. $`T`$ 스텝 후 결과가 청정 action 시퀀스 $`x_{0}`$ 에 근사 수렴합니다.

### 학습 셋업

| 항목 | 값 | 출처 |
|---|---|---|
| 초기화 | 각 모델의 공식 사전학습 체크포인트 | §Implementation |
| 파인튜닝 | full-parameter / LoRA / 양쪽 | §Implementation |
| LoRA rank | vision-language backbone 32 · action expert 64 | §Implementation |
| LoRA alpha | 1 | §Implementation |
| action horizon | 50 스텝 (flow-matching 전 정책 공통) | §Implementation |
| 최적화 스텝 | 10,000 | §Implementation |
| 배치 크기 | 32 (메모리 요구가 다른 모델은 gradient accumulation 으로 유효 배치 동일 유지) | §Implementation |
| 하드웨어 | NVIDIA L20 × 2 | §Implementation |
| expert 수 | 4 | §Implementation |
| 라우팅 | Top-1 | §Implementation |
| 라우터 손실 계수 | 0.05 | §Implementation |
| 균형 샘플링 가중치 | 0.5 | §Implementation |
| 부가 정규화 | 없음 (load-balancing / contrastive-routing / dead-expert 손실 미사용) | §Implementation |

> "No extra load-balancing, contrastive-routing, or dead-expert regularization losses are used." (§Experimental Setups and Evaluation Metrics)
(MoE 학습에서 관례적으로 붙는 보조 손실을 전부 뺐다는 선언입니다. 라우터가 지도 신호를 받는 순간 부하 균형이 손실 설계가 아니라 데이터 샘플링 문제로 이동한다는 이 논문의 관점이 여기에 드러납니다.)

---

## 📊 실험 설정과 결과

### 벤치마크 구성

| 항목 | RoboTwin | DIYRobot |
|---|---|---|
| 성격 | 시뮬레이션 | 실세계 (자체 제작 플랫폼) |
| 과제 수 | 8 | 5 |
| 세팅 | clean · random | clean only (long-tail 시연 의도적 수집) |
| 학습 시연 | 세팅당 과제별 50 → 총 800 | 과제별 100 → 총 500 |
| 테스트 | 세팅·과제당 100회 → 총 1,600회 | 과제당 50회 → 총 250회 |
| 지표 | 과제별 성공 횟수 + 전 과제 평균 | 동일 |

DIYRobot 플랫폼은 3D 프린팅으로 제작한 14-DoF 양팔 로봇이며 제작비가 2,000 USD 미만입니다. 5개 과제는 handover pen, pick box, rotate screwdriver, pull bottle, press button 입니다.

![Figure 4 — DIYRobot 5개 과제 시연](https://arxiv.org/html/2607.26807/combined_vertical.jpg)

> "Figure 4: Demonstrations of the five manipulation tasks performed on our DIYRobot platform, where the left-to-right sequence indicates the temporal progression of each operation." (§Main Results and Analyses)
(양팔 핸드오버부터 손목 주도 회전까지, 서로 다른 기구학 원형을 의도적으로 배치한 과제 구성임을 보여 줍니다.)

### 주 결과 — RoboTwin (Table 1)

각 셀은 `Clean / Random` 순 성공 횟수(100회 중)입니다.

| Models | Hand Block | Hang Mug | Move Can | Open Laptop | Place Shoes | Place Pad | Rotate Qrcode | Turn Switch | Avg. |
|---|---|---|---|---|---|---|---|---|---|
| OpenVLA | 0 / 0 | 0 / 0 | 2 / 4 | 28 / 29 | 0 / 0 | 0 / 0 | 0 / 0 | 3 / 2 | 4.1 / 4.4 |
| RDT-1B | 19 / 9 | 6 / 0 | 16 / 12 | 46 / 33 | 1 / 1 | 1 / 1 | 16 / 12 | 2 / 4 | 13.4 / 9.0 |
| π0-Full | 0 / 0 | 9 / 2 | 22 / 24 | 15 / 11 | 2 / 1 | 1 / 1 | 10 / 12 | 12 / 19 | 8.9 / 8.8 |
| π0-LoRA | 2 / 1 | 6 / 8 | 15 / 14 | 35 / 30 | 6 / 5 | 7 / 2 | 24 / 22 | 16 / 19 | 13.9 / 12.6 |
| π0.5-Full | 5 / 3 | 4 / 3 | 26 / 27 | 76 / 81 | 11 / 2 | 4 / 10 | 40 / 31 | 31 / 28 | 24.6 / 23.1 |
| π0.5-LoRA | 8 / 21 | 8 / 11 | 40 / 32 | 78 / 79 | 29 / 27 | 22 / 23 | 48 / 44 | 32 / 36 | 33.1 / 34.1 |
| Hi-MoE | 0 / 0 | 0 / 0 | 0 / 0 | 38 / 39 | 0 / 0 | 0 / 0 | 2 / 2 | 14 / 10 | 6.8 / 6.4 |
| AdaMoE | 7 / 4 | 14 / 8 | 40 / 36 | 95 / 86 | 5 / 7 | 8 / 9 | 51 / 50 | 37 / 35 | 32.1 / 29.4 |
| KinRT-OpenVLA | 1 / 0 | 2 / 0 | 14 / 7 | 36 / 42 | 0 / 0 | 0 / 0 | 2 / 0 | 6 / 3 | 7.6 / 6.5 |
| KinRT-Full(π0) | 1 / 2 | 4 / 6 | 10 / 7 | 43 / 33 | 1 / 1 | 5 / 3 | 11 / 19 | 14 / 15 | 11.1 / 10.8 |
| KinRT-LoRA(π0) | 12 / 6 | 5 / 6 | 9 / 6 | 56 / 57 | 1 / 5 | 1 / 1 | 12 / 16 | 30 / 18 | 15.8 / 14.4 |
| KinRT-AdaMoE | – / – | – / – | – / – | – / – | – / – | – / – | – / – | – / – | – / – |
| KinRT-Full | 34 / 22 | 12 / 2 | 38 / 28 | 84 / 83 | 28 / 24 | 18 / 10 | 40 / 34 | 34 / 28 | 36.0 / 28.9 |
| KinRT-LoRA | 18 / 17 | 19 / 10 | 40 / 34 | 84 / 82 | 44 / 41 | 34 / 32 | 44 / 51 | 43 / 43 | 40.8 / 38.8 |

### 주 결과 — DIYRobot (Table 1)

성공 횟수(50회 중)입니다.

| Models | Hand Pen | Pick Box | Rotate Screw | Pull Bottle | Press Button | Avg. |
|---|---|---|---|---|---|---|
| OpenVLA | 0 | 1 | 0 | 16 | 0 | 3.4 |
| RDT-1B | 0 | 3 | 0 | 6 | 4 | 2.6 |
| π0-Full | 9 | 19 | 18 | 24 | 0 | 14.0 |
| π0-LoRA | 0 | 2 | 15 | 18 | 0 | 7.0 |
| π0.5-Full | 19 | 31 | 33 | 39 | 26 | 29.6 |
| π0.5-LoRA | 10 | 22 | 26 | 23 | 1 | 16.4 |
| Hi-MoE | 0 | 1 | 0 | 34 | 5 | 8.0 |
| AdaMoE | 1 | 26 | 21 | 37 | 22 | 21.4 |
| KinRT-OpenVLA | 0 | 2 | 0 | 22 | 0 | 4.8 |
| KinRT-Full(π0) | 3 | 33 | 35 | 41 | 0 | 22.4 |
| KinRT-LoRA(π0) | 0 | 14 | 18 | 25 | 1 | 11.6 |
| KinRT-AdaMoE | 2 | 40 | 38 | 42 | 20 | 28.4 |
| KinRT-Full | 26 | 40 | 41 | 43 | 28 | 35.6 |
| KinRT-LoRA | 5 | 32 | 38 | 40 | 4 | 23.8 |

> "Extensive experiments demonstrate KinRT’s superiority over both dense and MoE-featured VLAs by more than 23.26% on RoboTwin benchmark and 20.27% on our introduced DIYRobot platform." (§Abstract)
(초록이 내세우는 두 숫자는 각각 RoboTwin clean 에서 KinRT-LoRA 40.8 대 π0.5-LoRA 33.1 (+7.7), DIYRobot 에서 KinRT-Full 35.6 대 π0.5-Full 29.6 (+6.0) 의 *상대* 개선율입니다. 절대 성공률 자체는 최고가 100회 중 40.8 로, 벤치마크 난이도가 높은 저성공률 구간에서의 비교임을 함께 읽어야 합니다.)

**RQ1 — dense VLA 대비.** 라우팅 이전에 dense 계열의 열화 패턴 자체가 논문의 동기를 뒷받침합니다.

> "Notably, dense models (e.g., OpenVLA, $`4.1/4.4`$ on RoboTwin and $`3.4`$ on DIYRobot) degrade severely as task kinematic heterogeneity grows, which corroborates our motivation that compressing disparate kinematics into a shared model space induces destructive parameter competition." (§Main Results and Analyses, Table 1)
(이질적 기구학을 하나의 파라미터 공간에 압축하면 파괴적 경쟁이 생긴다는 주장의 근거로 제시된 수치이며, 그 대안이 MoE 라는 것이 논지의 출발점입니다.)

**RQ2 — 암묵 라우팅 대비.** 이 비교가 논문의 핵심 대조군입니다. 최고 암묵 라우팅 경쟁자 AdaMoE 는 RoboTwin 32.1 / 29.4, DIYRobot 21.4 이고, KinRT-LoRA·KinRT-Full 이 각각 +8.7 / +9.4, +14.2 앞섭니다. 반대로 Hi-MoE 는 Move Can 에서 0 / 0 을 포함해 다수 과제에서 붕괴해 6.8 / 6.4, 8.0 에 그칩니다.

> "This collapse empirically confirms the failure mode we identified: implicitly learned routers driven purely by gradients degenerate expert assignments when facing kinematic heterogeneity, whereas supervising the router with kinematic archetype labels yields physically meaningful expert specialization." (§Main Results and Analyses, Table 1)
(MoE 를 붙였다고 항상 이득이 아니라 오히려 dense 보다 나빠질 수 있다는 것을 Hi-MoE 가 보여 주고, 그 차이를 만드는 변수로 라우터 지도 여부를 지목합니다. 다만 Hi-MoE / AdaMoE 는 KinRT 와 백본이 동일하지 않으므로 이 대조는 완전한 통제 실험은 아닙니다.)

**RQ3 — 백본 무관성(plug-in).** KinRT 를 다른 백본에 얹은 변형은 일관된 개선을 보입니다 — π0-LoRA 13.9 / 12.6 → 15.8 / 14.4, π0-Full 8.9 / 8.8 → 11.1 / 10.8, OpenVLA 4.1 / 4.4 → 7.6 / 6.5, DIYRobot 에서 AdaMoE 21.4 → 28.4 (+7.0).

> "These consistent improvements indicate that the performance gains stem from the kinematics-supervised routing paradigm rather than from any specific architectural choice, and that KinRT’s asymmetric bridging mechanism is broadly transferable to diverse backbone architectures." (§Main Results and Analyses)
(개선 *방향* 은 일관되지만 개선 *폭* 은 백본에 따라 크게 다릅니다. 특히 KinRT-OpenVLA 는 7.6 / 6.5 로 여전히 최하위권이라, "패러다임이 백본과 무관하다"는 주장은 순위 역전이 아니라 상대적 향상 일관성 수준으로 읽는 것이 정확합니다.)

**RQ4 — Sim2Real 과 LoRA / full FT 트레이드오프.** 이 절이 우리 스택에 가장 직접적인 함의를 갖습니다.

> "In simulation, KinRT-LoRA dominates ($`40.8/38.8`$ vs. $`36.0/28.9`$ for Full), while on the real DIYRobot platform the ordering reverses: KinRT-Full achieves $`35.6`$ against KinRT-LoRA’s $`23.8`$." (§Main Results and Analyses, Table 1)
(시뮬레이션에서는 PEFT 가, 실기에서는 full FT 가 이깁니다. 같은 역전이 π0.5 baseline 에서도 재현되므로(시뮬레이션 33.1 vs 24.6, 실기 16.4 vs 29.6) 메서드 고유 현상이 아니라 벤치마크 수준 현상이라는 것이 저자 해석입니다.)

> "This indicates a benchmark-level rather than method-level phenomenon: real-robot data collected on DIYRobot deviates substantially from the pretraining distribution, so the larger adaptation capacity of full fine-tuning becomes necessary to absorb the embodiment gap, whereas in simulation the parameter-efficient LoRA regularization mitigates overfitting to the limited demonstrations." (§Main Results and Analyses)
(사전학습 분포에서 멀수록 적응 용량이 필요하고, 가까우면서 시연이 적을수록 정규화가 필요하다는 해석입니다. 어느 쪽이든 "freeze / PEFT 가 항상 안전하다"는 기본값이 실기에서 깨질 수 있음을 시사합니다.)

**RQ5 — 어떤 기구학 영역에서 이득이 큰가.** 양팔 협응 과제 Handover Block 에서 KinRT-Full 이 34 / 22 인 반면 dense·MoE baseline 은 clean 세팅에서 전부 19 미만이고, 실세계 Handover Pen 에서도 KinRT-Full 26 대 대부분 baseline 저조(π0.5-Full 19 예외)입니다. 접촉 정밀 과제 Press Button 에서는 π0 계열과 π0.5-LoRA 가 0–1 로 사실상 실패하는 반면 KinRT-Full 이 28 로 최고입니다. 반면 원형이 공유되는 Open Laptop 에서는 84 / 83 으로 경쟁력을 유지합니다 — 특화가 공통 영역 성능을 희생하지 않았다는 근거로 제시됩니다.

### Ablation — 균형 샘플링 계수 (Table 2)

KinRT-LoRA @ RoboTwin, 100회 중 성공 횟수입니다.

| $`\alpha`$ | Hand Block | Hang Mug | Move Can | Open Laptop | Place Shoes | Place Pad | Rotate Qrcode | Turn Switch | Avg. |
|---|---|---|---|---|---|---|---|---|---|
| 0.0 | 16 | 9 | 49 | 84 | 24 | 22 | 37 | 34 | 34.4 |
| 0.5 | 18 | 19 | 40 | 84 | 44 | 34 | 44 | 43 | 40.8 |
| 1.0 | 34 | 22 | 45 | 72 | 25 | 17 | 39 | 39 | 36.6 |

> "The intermediate setting $`\alpha=0.5`$ achieves the best average success (40.8), clearly outperforming both extremes (34.4 for $`\alpha=0`$ and 36.6 for $`\alpha=1`$)." (§Ablation Studies, Table 2)
(이 행들이 분리해 내는 것은 "소수 원형 expert 의 학습 부족"과 "다수 원형 성능 희생" 사이의 트레이드오프입니다.)

행별로 읽으면 메커니즘이 선명합니다. $`\alpha=0`$ (균형 없음)에서는 소수 원형에 대응하는 expert 가 과소 학습되어 그 원형에 의존하는 과제가 무너집니다 — Place Shoes 24, Place Pad 22 로 최적 설정 대비 각각 20, 12 낮습니다. 반대로 $`\alpha=1`$ (완전 균등)에서는 경험 분포가 과도하게 왜곡되어 다수 동작 패턴이 희생됩니다 — Open Laptop 이 84 에서 72 로 떨어지는 것이 저자가 직접 지목한 증거입니다. 흥미롭게도 Hand Block(34)과 Hang Mug(22)는 $`\alpha=1`$ 에서 최고치인데, 이 두 과제가 소수 원형(Cluster 2 대진폭 양팔 협응 4.4%, Cluster 3 13.3%)에 얹혀 있다는 해석과 정합적입니다. 즉 $`\alpha`$ 는 평균을 올리는 스칼라가 아니라 **어떤 과제군을 살릴지 고르는 손잡이** 입니다.

### Ablation — 클러스터링 소스 (Table 3)

라우터의 지도 라벨을 만드는 클러스터링 입력을 바꾼 실험입니다. KinRT-LoRA @ RoboTwin.

| Sources | Hand Block | Hang Mug | Move Can | Open Laptop | Place Shoes | Place Pad | Rotate Qrcode | Turn Switch | Avg. |
|---|---|---|---|---|---|---|---|---|---|
| VLM | 2 | 6 | 38 | 68 | 10 | 8 | 18 | 24 | 21.8 |
| Range | 2 | 6 | 18 | 68 | 4 | 6 | 50 | 36 | 23.8 |
| Arm | 2 | 2 | 22 | 74 | 8 | 8 | 58 | 40 | 26.8 |
| Task | 22 | 6 | 30 | 58 | 2 | 2 | 42 | 46 | 26.0 |
| Velocity | 8 | 6 | 26 | 68 | 18 | 12 | 42 | 36 | 27.0 |
| Action | 14 | 12 | 20 | 68 | 34 | 12 | 60 | 44 | 33.0 |
| Action & Velocity | 18 | 19 | 40 | 84 | 44 | 34 | 44 | 43 | 40.8 |

> "Clustering on VLM embeddings (i.e., visual-linguistic similarity) performs worst ($`21.8`$), empirically confirming our core hypothesis that semantic proximity does not imply kinematic isomorphism." (§Ablation Studies, Table 3)
(라벨을 시각-언어 유사도로 만들면 21.8 로 최하위입니다 — 논문의 전제인 "의미 근접성 ≠ 기구학 동형성"을 가장 직접적으로 검증하는 행입니다.)

행별 판독:

- **Range(23.8) / Arm(26.8)** — 동작 범위, 팔 사용 여부 같은 거친 기구학 추상은 VLM 보다 낫지만 제한적입니다. 좌우 편향(laterality)만 잡고 시간 구조를 버리기 때문입니다.
- **Task(26.0)** — 사람이 붙인 과제 정체성 라벨은 기구학적으로 동일한 과제를 합치지도, 이질적인 과제를 나누지도 못합니다. 다만 Hand Block 22 처럼 개별 과제에서는 이따금 이깁니다.
- **Action(33.0) vs Velocity(27.0)** — 절대 위치 구성이 속도 프로파일보다 원형 변별 정보를 더 많이 담습니다.
- **Action & Velocity(40.8)** — 단일 최고 소스(Action) 대비 +7.8. 두 신호가 공간 배치와 동작 템포라는 상보적 정보를 담고 있어 결합 시 물리적으로 가장 일관된 분할이 나온다는 것이 저자 해석입니다.

![Figure 3 — action-velocity 공간과 시각-언어 관측 공간의 관계](https://arxiv.org/html/2607.26807/pair_similarity_heatmap.jpg)

> "Figure 3: Demonstrations of the relationship between action-velocity space and visual-linguistic observation space." (§Ablation Studies)
(Table 3 의 순위를 설명하는 메커니즘 그림 — 풀링된 VLM 특징과 PCA 투영 action-velocity 특징 간 쌍별 코사인 유사도의 결합 밀도입니다.)

> "First, the VLM similarity axis is severely collapsed: virtually all demonstration pairs fall within the narrow band $`[0.96,1.00]`$, meaning that the VLM representation is highly collapsed, with most demonstration pairs exhibiting near-identical cosine similarity." (§Ablation Studies)
(VLM 축이 폭 0.04 구간에 몰려 있다는 것은 그 축 위에서는 어떤 경계도 그을 수 없다는 뜻입니다.)

> "Second, and more critically, at any fixed VLM similarity, the kinematic similarity spans nearly the entire range $`[-0.75,1.0]`$, with the global density mass centered around zero." (§Ablation Studies)
(같은 VLM 유사도를 가진 쌍들이 기구학적으로는 거의 전 구간에 퍼져 있다는 것이 핵심입니다 — 관측 유사도가 기구학에 대해 사실상 무정보임을 보여 주며, 클러스터별 패널에서는 기구학 유사도 분포가 뚜렷하게 압축되어 클러스터링이 동작상 일관된 그룹을 잘라냈음을 뒷받침합니다.)

---

## ⚖️ 한계

본문에 별도의 Limitations 절이 없어, 아래는 저자가 결론에서 명시한 향후 과제 하나와 본문에서 추론된 갭들입니다.

- **라우터 정확도가 한 번도 보고되지 않음** — 논문의 중심 주장은 "관측만으로 기구학 원형을 회수할 수 있다"인데, 그 회수가 얼마나 잘 되는지에 대한 직접 지표(원형 예측 정확도 / 혼동행렬)가 어디에도 없습니다. 최종 성공률만으로는 "라우터가 잘 맞혔기 때문"인지 "expert 를 4개 더 얹어 용량이 늘었기 때문"인지 분리되지 않습니다. shared 분기가 항상 켜져 있고 $`(1/2,1/2)`$ 가중치가 고정이라 라우팅이 무작위여도 성능이 크게 무너지지 않을 수 있으므로, **라우터 라벨 셔플 ablation** 이 빠진 것은 실질적 공백입니다.
- **라우터 입력의 자기모순** — 논문은 원 시각-언어 임베딩의 코사인 유사도가 0.95 를 넘어 변별력이 없다고 배제해 놓고, 그 대안으로 같은 PaliGemma 의 출력 토큰을 mean pooling 한 벡터를 씁니다. Figure 3 의 붕괴 관측 자체가 "pooled VLM features" 에 대한 것이므로, 붕괴한 표현 위에 선형층 하나를 얹어 4-way 분류가 되는 이유가 설명되지 않습니다. 여기서 실제로 작동하는 것은 표현의 변별력이 아니라 지도 신호가 만든 결정 경계일 수 있고, 그렇다면 일반화 근거가 약해집니다.
- **expert 수가 데이터에서 유도되었다는 주장의 순환성** — $`N=4`$ 는 K-means 결과에 맞춘 값이지만, $`K`$ 자체를 어떻게 골랐는지(elbow / silhouette / 사전 지정)는 본문에 없고 $`N`$ 에 대한 ablation 도 없습니다. 클러스터링 소스는 ablate 했으나 클러스터 *개수* 는 하지 않았으므로, "granularity 를 데이터가 정했다"는 서술은 아직 검증되지 않은 설계 선택입니다.
- **archetype 의 데이터셋 종속성** — Cluster 3(13.3%)이 red-block handover 라는 단일 과제에 지배된다고 명시되어 있습니다. 즉 발견된 원형 집합은 보편적 동작 어휘가 아니라 이 데이터 혼합에 특유한 분할일 수 있으며, 데이터셋이 바뀌면 재클러스터링과 재학습이 필요합니다. expert 가 다른 데이터셋으로 전이되는지는 다루지 않습니다.
- **관측당 Top-1 hard switch 의 시간적 취약성** — 라벨은 프레임 단위인데 라우팅 결정은 관측당 1회이고 18개 레이어 전체에 공유됩니다. 50 스텝 chunk 가 두 원형의 경계를 걸치는 순간(준비 → 실행 전이)에 대한 평활화·히스테리시스·혼합 장치가 없어, 원형 전이 구간에서 결정이 진동할 여지가 있습니다. 결론이 예고한 "adaptive expert activation" 이 정확히 이 지점입니다.
- **"Top-1 routing to enable one expert for each token" 서술의 모순** — 구현 절은 토큰 단위 라우팅처럼 읽히지만 방법론 절은 관측 단위 global routing 을 명시합니다. 두 서술은 양립하지 않으며, 어느 쪽이 실제 구현인지에 따라 재현 결과가 달라집니다.
- **비교의 통제 부족** — Hi-MoE / AdaMoE 는 KinRT 와 백본·파라미터 수가 동일하지 않고, 무엇보다 접미사 없는 "KinRT-Full / KinRT-LoRA" 가 어떤 백본 위에 세워졌는지가 본문에 명시되지 않습니다(아키텍처 서술은 PaliGemma-2B + Gemma-300M 이지만 π0.5 라는 명시는 없음). 헤드라인 수치의 비교 기준이 불확정입니다.
- **단일 시행·무편차 보고** — 모든 수치가 성공 *횟수* 한 값이며 시드 반복, 표준편차, 신뢰구간이 없습니다. RoboTwin 세팅당 100회는 성공률 30% 부근에서 표준오차가 약 4.6%p 수준이므로, RQ3 의 plug-in 이득(예: π0 13.9 → 15.8, +1.9)은 노이즈와 구분되지 않을 수 있습니다.
- **"negligible additional inference cost" 의 미검증** — 결론이 추가 추론 비용이 무시할 만하다고 주장하지만 지연시간·메모리·활성 파라미터 수치가 제시되지 않습니다. Top-1 이면 FLOPs 증가는 작아도 expert FFN 4개가 상주하므로 메모리는 늘고, 이는 온보드 배포에서 실제 제약이 됩니다.
- **라우터 온도와 탐색 노이즈 미명시** — 온도 $`\tau`$ 와 탐색 노이즈 $`\sigma`$ 는 "accordingly 설정 가능"이라고만 적혀 있고 값이 없습니다. 라우터의 엔트로피와 expert 이용률을 직접 좌우하는 하이퍼파라미터가 비어 있어, 재현 시 이 두 값의 탐색이 필요합니다.
- **그리퍼 로봇 기반 검증** — 기구학 기술자의 액션 차원이 팔 6 + 그리퍼 1 × 2 = 14 이며, 두 벤치마크 모두 다지 손이 아닌 평행 그리퍼 양팔 플랫폼입니다. "기구학 이질성"이 팔 매크로 동작 수준에서 정의된 결과이므로, 손가락 수준 접촉 집약적 조작으로의 확장은 미검증입니다.

---

## ♻️ 재현성

- **코드** — 미공개. 초록과 DIYRobot 절 모두 "will be open-sourced" / "will publicly release" 로 예고만 되어 있고, 본문에 저장소 URL 이 없습니다. 현재 시점 기준 코드 기반 재현은 불가합니다.
- **하드웨어 플랫폼** — DIYRobot 의 드라이버 코드와 3D 프린팅 설계 파일을 벤치마크와 함께 공개하겠다고 명시했습니다. 14-DoF 양팔, 제작비 2,000 USD 미만이라는 사양은 소규모 연구팀 재현이 현실적인 수준입니다.
- **데이터** — RoboTwin 은 공개 벤치마크이며 나머지 세팅(랜덤 시드 등)은 공식 권장값을 따랐다고 밝혔습니다. DIYRobot 벤치마크(5과제 × 100 시연)는 공개 예정입니다.
- **학습 자원** — NVIDIA L20 2장, 10,000 스텝, 배치 32 로 소규모 랩에서 재현 가능한 규모입니다.
- **명시된 하이퍼파라미터** — expert 4개, Top-1, 라우터 손실 계수 0.05, 균형 샘플링 0.5, LoRA rank 32/64 · alpha 1, horizon 50.
- **누락된 하이퍼파라미터** — 라우터 온도 $`\tau`$, 탐색 노이즈 $`\sigma`$, 학습률·옵티마이저·스케줄, LoRA 적용 모듈 목록, 디노이징 스텝 수 $`T`$, K-means 의 $`K`$ 선택 절차와 시드, 접미사 없는 KinRT 의 백본 정체.
- **라이선스** — arXiv 게재본은 CC BY-NC-ND 4.0 으로, 상업적 이용·파생물 배포에 제약이 있습니다. 공개 예정 코드·플랫폼의 라이선스는 미상입니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P1(Heterogeneous Body/Hand Action Expert) — 주 Pillar.** 본 논문은 action expert 내부를 어떻게 분할할 것인가에 대한 정면 제안이므로 P1 의 comparison group 에 정확히 들어갑니다. 다만 분할 축이 우리와 다릅니다 — 우리는 **해부학적** 분할(Body / Hand)을 놓고, KinRT 는 **기구학 국면(regime)** 분할을 놓습니다. `D1`(split form; v1 = 공유 트렁크 + body/hand 분리 헤드)에 대해 KinRT 는 "제3의 축"을 제시하는 셈이고, 두 축은 배타적이지 않으므로 중첩 가능성이 곧 설계 질문이 됩니다. `D4`(Body↔Hand 정보 공유; v1 = FiLM 단일 지점)와도 접점이 있습니다 — KinRT 의 라우팅 결정은 그 자체로 저차원 조건 신호이므로, FiLM 의 조건 입력에 archetype ID 를 추가하는 변형이 자연스럽게 도출됩니다. `D7`(π 백본 통합/분할; v1 = π0 action expert 를 슬라이스해 양쪽 FT)에 대해서는 "action expert 의 FFN 만 MoE 로 교체하고 backbone 은 동결"이라는 구체적 통합 지점을 제공합니다.
- **P4(Pretraining for Data-Efficient Adaptation).** RQ4 의 LoRA↔full FT 역전이 `D19`(VLM 백본 lineage 및 적응 범위; v1 = (a) VLM 전면 동결 + action expert 만)에 직접적인 반증 압력을 겁니다 — 사전학습 분포에서 먼 실기 데이터에서는 적응 용량이 필요하다는 관측이기 때문입니다. 다만 KinRT 자체는 backbone(SigLIP·PaliGemma-2B)을 동결한 채 action head 만 확장하므로 `D20`(prior-preservation 전략; v1 = action-side adapter + conservative SFT)의 "action-side adapter" 계열과 오히려 정합적입니다. `D23`(action representation × pretraining; v1 = 연속 flow-matching head)과도 정합적입니다 — KinRT 의 생성기는 그대로 flow matching 입니다.
- **P2(Structured Multimodal Observation Fusion).** Figure 3 과 라우터 입력 논의는 P2 의 문제의식을 외부에서 실증한 자료입니다. 풀링된 VLM 표현의 쌍별 코사인 유사도가 [0.96, 1.00] 에 붕괴해 있다는 관측은 `D8`(다중 카메라 공간-기하 grounding; v1 = 통합 3D 일관 임베딩) 및 `D10`(concat 초월 이종 모달 융합; v1 = cross-attention / asymmetric fusion)이 겨냥하는 "flat 한 시각 중심 관측은 정보를 잃는다"는 주장의 정량적 근거로 쓸 수 있습니다. 반대 방향의 함의도 있습니다 — 우리 관측이 구조화되어 이미 변별력이 있다면, KinRT 의 전제(관측이 붕괴해 있으므로 외부 지도가 필요)가 우리 스택에서는 약해집니다.
- **P0(VLA Datasets & Benchmarks).** DIYRobot 은 `D26`(벤치마크/eval 스카우팅 범위)의 실세계 suite 후보입니다. 다만 `D27`(라이선스/사용성 기준; v1 = permissive 선호, NC 는 플래그)에 비추면 게재본이 CC BY-NC-ND 4.0 이고 코드·데이터 라이선스가 미상이라 현 시점에는 추적만 하고 핀은 보류하는 것이 맞습니다. 또한 평행 그리퍼 양팔 플랫폼이라 `D25`(촉각/힘/토크 데이터)의 접촉 모달리티 공백을 메우지는 못합니다.
- **관계 없음 — P3 / P5.** 본 논문에는 RL 요소가 없어 System0 관련 결정(D13–D18)과 무관하고, 예측 모델·world model 요소도 없어 D28–D32 와도 무관합니다. 억지로 연결하지 않습니다.
- **Identity 긴장/지지** — **지지**: "dexterity 는 correction 모듈이 아니라 VLA level 에서 다뤄야 한다"는 Identity 주장과 완전히 같은 편입니다. KinRT 는 frozen VLA 위에 residual 을 붙이지 않고 action expert 내부를 재설계합니다. **긴장**: Identity 가 요구하는 분할 기준은 *해부학* 인데 KinRT 는 *동작 통계* 로 분할합니다. 동작 통계 기반 분할이 더 잘 통한다면, 해부학적 분할이 사전 지식으로서 최선인가라는 질문이 열립니다 — 다만 Table 3 의 Task 행(26.0)이 보여 주듯 사람이 부여한 범주가 데이터 유도 범주보다 열등했다는 것이지, 해부학적 분할을 직접 부정한 증거는 아닙니다.
- **경쟁자 함의** — P1 의 Tracked Literature 중 LaMP(dual-expert gated cross-attention)와 가장 가까운 위치이며, "게이트를 어떻게 학습시킬 것인가"라는 같은 질문에 서로 다른 답을 냅니다. π0 / π0.5 는 여기서 baseline 이자 KinRT 가 얹히는 대상으로 등장합니다.

---

## ✨ 핀 논문 대비 델타

- **vs π0 ([arXiv:2410.24164](https://arxiv.org/abs/2410.24164), P1·P4 핀 / 백본)** — π0 의 action expert 는 단일 dense FFN 이고, KinRT 는 그 FFN 을 shared + routed 병렬 합성으로 교체합니다. 생성기(flow matching)와 MoT 골격은 그대로이므로, 델타는 *액션 헤드의 조건부 희소화* 한 지점에 국한됩니다. 이 좁은 개입 범위가 오히려 이식 비용이 낮다는 실무적 장점입니다.
- **vs LaMP ([arXiv:2603.25399](https://arxiv.org/abs/2603.25399), P1 핀 / D4 deferred)** — 둘 다 복수 expert 와 게이트를 씁니다. LaMP 의 게이팅은 손실을 통한 **암묵** 학습이고, KinRT 의 게이팅은 오프라인 라벨에 의한 **명시적 지도** 입니다. 진정으로 새로운 것은 mixture 구조가 아니라 *게이트에 정답이 존재한다고 선언하고 그 정답을 action 공간에서 제조한 것* 입니다.
- **vs Dexora ([arXiv:2605.18722](https://arxiv.org/abs/2605.18722), P1 핀 / 고DoF 양팔 레퍼런스)** — Dexora 가 고DoF 양팔 action space 자체를 다룬다면, KinRT 는 action space 를 건드리지 않고 같은 space 를 시간 축에서 국면 분할합니다. 두 접근은 직교하며 동시 적용이 가능합니다.
- **vs Shared-Autonomy Arm-Hand VLA / DexGrasp-VLA ([arXiv:2511.00139](https://arxiv.org/abs/2511.00139), P1 핀 / 해부학적 분할)** — 분할 축의 정면 대비입니다. DexGrasp-VLA 계열은 arm / hand 라는 신체 구조로 나누고, KinRT 는 왼팔 주도 / 오른팔 주도 / 양팔 대진폭 / 과제 특이라는 동작 국면으로 나눕니다. KinRT 의 Cluster 0·1 이 사실상 좌우 팔 지배성으로 갈린다는 점은 흥미롭게도 두 축이 부분적으로 상관됨을 시사합니다.
- **vs ConSFT ([arXiv:2605.08879](https://arxiv.org/abs/2605.08879), P4 핀 / 보수적 적응)** — ConSFT 가 적응 *단계* 에서 prior 를 지키는 방법이라면, KinRT 는 backbone 을 아예 건드리지 않고 action head 용량만 늘려 같은 목표에 접근합니다. 다만 KinRT 의 RQ4 는 실기에서 full FT 가 이겼다고 보고하므로, 보수적 적응의 유효 범위에 대한 반례 후보로도 읽힙니다.
- **vs Demystifying Action Space Design ([arXiv:2602.23408](https://arxiv.org/abs/2602.23408), P1 methodology base)** — 그 논문이 action *공간* 선택(joint vs task)이 안정성·일반화를 가른다고 보였다면, KinRT 는 공간을 고정한 채 *모델* 을 action 통계로 분할합니다. "action 표현이 아키텍처 결정을 규정한다"는 같은 흐름의 다른 층위입니다.
- **정직한 평가** — 진짜 새로운 것은 LUPI 를 **정책이 아니라 라우터** 에 적용한 지점 하나입니다. 클러스터링(K-means + PCA), MoE FFN, flow matching, global routing 은 모두 기성 부품이며, 논문의 기여는 조합과 지도 신호의 출처에 있습니다.

---

## ⚙️ 의사결정 함의

이 논문이 옳다면 우리 파이프라인에서 다음이 바뀝니다.

- **오프라인 전처리 단계 신설** — 학습 전에 데이터셋 전체를 순회해 프레임별 원형 라벨을 만들어 저장하는 단계가 생깁니다. 구체적으로 `chunk_horizon=50`, 위치 특징 = flatten(chunk), 속도 특징 = flatten(인접 차분), 표준화 → `pca_dim=64` → `KMeans(n_clusters=K)`. 산출물은 `(episode_id, frame_idx) → prototype_id` 매핑이며 데이터셋 아티팩트로 버전 관리되어야 합니다(데이터가 바뀌면 라벨도 무효화).
- **손실 항 추가** — 총 손실이 $`\mathcal{L}=\mathcal{L}_{act}+\lambda_{\text{sup}}\mathcal{L}_{\text{sup}}`$ 형태가 되고 `router_loss_coef = 0.05` 가 v1 값입니다. 이 값은 flow-matching MSE 대비 라우터 CE 의 스케일에 민감하므로 우리 데이터에서 재탐색 대상입니다.
- **샘플러 교체** — 균등 셔플 대신 $`w_{i}=n_{y_{i}}^{-\alpha}`$ 가중 복원추출 샘플러(`balanced_sampling_alpha = 0.5`)를 씁니다. Table 2 가 보여 주듯 이 값은 평균이 아니라 *어떤 과제군을 살릴지* 를 결정하므로, 우리의 phase 1 목표(in-hand 회전)가 소수 원형에 해당한다면 $`\alpha`$ 를 0.5 보다 높여야 할 수 있습니다.
- **action expert 구조 변경** — 각 블록 FFN 을 `0.5 * FFN_shared + 0.5 * Σ w_k FFN_expert_k` 로 교체하고 `num_experts = 4`, `top_k = 1`, expert 폭은 백본과 동일(`d_model=1024`, `d_mlp=4096`). shared 분기는 사전학습 가중치로 초기화하고 학습 대상에 포함합니다. D7 v1(π0 action expert 슬라이스)과 겹치는 지점이므로, Body/Hand 헤드 분할과 expert 분할이 곱해질 때의 파라미터 예산을 먼저 계산해야 합니다.
- **라우터 모듈 추가** — `router_input = masked_mean_pool(prefix_tokens)`(우리 스택에서는 구조화 융합 임베딩이 후보), `router = nn.Linear(d_c, num_experts)`, 학습 시 `logits += N(0, σ²)` 후 `softmax(logits / τ)`. $`\tau`$ 와 $`\sigma`$ 는 원문 미명시이므로 우리가 정해야 하는 값입니다.
- **평가 지표 추가** — 논문이 보고하지 않은 **라우터 원형 예측 정확도** 를 우리는 1급 지표로 기록해야 합니다(held-out episode 기준 top-1 accuracy + 클래스별 recall + expert 이용률 히스토그램). 이 지표 없이는 성공률 개선의 귀인이 불가능합니다.
- **적응 범위 재검토 트리거** — RQ4 의 역전은 D19 v1(전면 freeze)에 대한 명시적 재검토 트리거입니다. 실기 데이터가 사전학습 분포에서 멀다면 freeze/PEFT 가 오히려 손해라는 관측이므로, 우리 실기 전환 시점에 `freeze / LoRA(rank 32-64) / full` 3-way 비교를 최소 1개 과제에서 돌리는 것을 릴리즈 게이트에 넣습니다.
- **부가 손실 제거 가능성** — load-balancing / dead-expert 정규화 손실 없이도 동작했다는 보고는, 우리가 MoE 를 도입할 때 튜닝 표면을 줄일 수 있다는 뜻입니다. 단 이는 라우터가 지도 신호를 받는다는 전제 위에서만 성립합니다.

---

## ⚠️ 먼저 검증할 실패 모드

싼 것부터 순서대로 배치했습니다. 앞의 세 항목은 **학습을 한 번도 돌리지 않고** 확인 가능합니다.

1. **(0.5시간, 학습 없음) 우리 데이터에 kinematic prototype collapse 가 존재하는가** — 논문의 전제 자체가 우리 데이터에서 성립하지 않을 수 있습니다. 기존 시연 로그로 $`\phi_{i}`$ 기술자를 만들고 $`K=2\ldots 12`$ 에 대해 silhouette / inertia 곡선을 그려 봅니다. 뚜렷한 elbow 가 없다면 expert 분할의 근거가 사라지고, 그 자체로 이 논문을 우리 스택에 적용하지 않을 근거가 됩니다. RoboTwin 은 162,545 프레임인데 우리 초기 데이터는 그보다 훨씬 작으므로, 클러스터당 샘플 수가 expert 학습에 충분한지도 같은 계산에서 나옵니다.
2. **(1시간, 학습 없음) Figure 3 재현 — 우리 관측은 이미 변별력이 있는가** — KinRT 의 전제는 "관측 표현이 붕괴해 있다"입니다. 우리의 구조화 융합 임베딩(P2 D8/D10 경로)과 action-velocity PCA 특징 간 쌍별 코사인 결합 밀도를 그려 봅니다. VLM 축이 [0.96, 1.00] 이 아니라 넓게 퍼져 있다면 암묵 라우팅으로도 충분할 수 있고, KinRT 의 이득 대부분이 우리 스택에서는 사라집니다. 이것이 가장 비용 대비 정보량이 큰 체크입니다.
3. **(0.5시간, 학습 없음) 손 자유도가 기술자에서 익사하는가** — 논문의 액션 차원은 팔 6 + 그리퍼 1 이지만 우리는 손가락 관절이 20개 이상입니다. 표준화 후 PCA-64 를 태우면 팔 매크로 동작의 분산이 손가락 미세 동작을 덮을 가능성이 큽니다. 전체 벡터 기준 클러스터링과 손 부분 벡터만의 클러스터링을 각각 돌려 클러스터 배정이 얼마나 달라지는지(ARI)를 비교합니다. 크게 다르다면 기술자를 팔/손으로 분리하거나 손 부분에 가중치를 줘야 합니다.
4. **(1일, 소규모 학습) 라우터 라벨 셔플 대조군** — 논문에 없는 실험이며, 우리가 도입 전에 반드시 해야 하는 확인입니다. 동일 구조에서 (a) 정상 라벨, (b) 무작위 셔플 라벨, (c) 라우터 손실 0(순수 암묵) 세 조건을 비교합니다. (a)와 (b)의 차이가 작다면 이득의 출처는 지도 라우팅이 아니라 expert 추가 용량 + 항상 켜진 shared 분기이며, 그렇다면 훨씬 단순한 dense 폭 확장으로 대체하는 것이 낫습니다.
5. **(1일) 원형 전이 구간의 결정 진동** — 라우팅이 관측당 1회 hard switch 이므로, 준비 → 실행 경계에서 연속 스텝의 라우팅 결정이 얼마나 자주 바뀌는지 로깅합니다. 전이 구간에서 스텝마다 expert 가 바뀌면 action chunk 간 불연속이 생기고, 이는 접촉 유지가 중요한 우리 과제(도구 조작, in-hand 회전)에서 곧바로 실패로 이어집니다. 완화책은 Top-2 소프트 혼합 또는 라우팅 결정의 시간 평활입니다.
6. **(2일) 해부학 분할 × 기구학 분할의 곱셈 비용** — D1 v1(공유 트렁크 + Body/Hand 헤드) 위에 expert 4개를 얹으면 헤드별 FFN 이 4배가 됩니다. 파라미터·메모리 증가와 헤드당 유효 데이터량 감소를 먼저 표로 계산하고, 필요하면 (a) Hand 헤드에만 MoE 적용, (b) 공유 트렁크에만 적용 중 하나로 축소합니다. "무시할 만한 추론 비용"이라는 논문 주장은 검증되지 않았으므로 우리 쪽에서 실측해야 합니다.
7. **(2일) 동결 backbone 에서 라우터가 학습되는가** — D19 v1 은 VLM 전면 동결입니다. 라우터 입력이 동결된 prefix 표현이라면 라우터는 그 표현을 개선할 수 없고 선형 분류기 하나로 4-way 를 풀어야 합니다. 동결 상태에서 held-out 원형 예측 정확도가 다수 클래스 baseline(우리 데이터에서 최대 클래스 비율)을 유의미하게 넘는지 먼저 확인합니다. 넘지 못하면 라우터 입력을 구조화 융합 임베딩 쪽으로 옮기거나 라우터를 2층 MLP 로 키워야 합니다.
8. **(실기 전환 시) LoRA↔full FT 역전의 재현 여부** — RQ4 의 역전이 우리 하드웨어에서도 나타나면 D19 v1(freeze)이 실기에서 최적이 아닐 수 있습니다. 실기 데이터 확보 직후 1개 과제에서 freeze / LoRA / full 3-way 를 돌려 우리 사전학습 분포와 실기 분포의 거리를 실측 대리 지표로 삼습니다.
9. **(장기) archetype 의 데이터 종속성** — Cluster 3 이 단일 과제에 지배되었듯, 우리 원형도 phase 1 과제(cube 회전)에 종속될 수 있습니다. phase 2(도구 조작) 데이터 추가 시 클러스터가 재편되면 expert 를 재학습해야 하므로, 원형 라벨 버전과 체크포인트 버전을 함께 고정하는 운영 규약이 필요합니다.

---

## 💡 컨텍스트 제안

사람이 판단할 후보만 적습니다 — `context/` 파일은 수정하지 않았습니다.

- **P1 §5 Methodology base 추가 후보** — KinRT (arXiv:2607.26807) 를 `D1` / `D4` 의 comparison-group 근거로 non-pinned methodology base 행에 추가하는 안. 핀(현재 4/8)으로 올릴지는 코드 공개 이후 재판단을 권합니다. 관련성 요약: "기구학 클러스터 ID 로 라우터를 지도하는 MoE action head — 해부학적 분할의 대안 축".
- **`D4` 추적 항목 확장 제안** — 현재 v1 은 FiLM 단일 지점입니다. "라우팅 결정(archetype ID)을 조건 신호로 쓰는 supervised gating" 을 LaMP 와 나란히 deferred 후보로 병기해 두는 것을 제안합니다. 결정 변경이 아니라 후보 목록 확장입니다.
- **`D19` 재검토 트리거 문구 제안** — v1 의 "insufficiency trigger" 에 "실기 데이터 분포가 사전학습 분포에서 멀 때 freeze/PEFT 가 full FT 에 역전당한다는 외부 관측(본 논문 RQ4)" 을 트리거 예시로 명기하는 안. 현 시점에서 v1 을 바꿀 근거는 아닙니다 — 단일 플랫폼·단일 시행 관측이기 때문입니다.
- **P0 `D26` 추적 후보 (핀 아님)** — DIYRobot 벤치마크(14-DoF 양팔, 5과제 × 100 시연, 제작비 2,000 USD 미만, 공개 예정)를 관찰 목록에 올리되, `D27` 라이선스 기준상 게재본이 CC BY-NC-ND 4.0 이고 코드·데이터 라이선스가 미상이므로 **공개 및 라이선스 확인 전까지 핀 보류** 를 권합니다. 평행 그리퍼 플랫폼이라 `D25` 의 촉각/토크 공백은 메우지 못합니다.
- **P2 근거 자료 추가 제안** — Figure 3 의 "풀링 VLM 표현 쌍별 코사인 [0.96, 1.00] 붕괴 + 동일 유사도에서 기구학 유사도 [-0.75, 1.0] 전 구간 분산" 관측은 `D8` / `D10` 의 동기를 외부에서 정량화한 드문 자료입니다. P2 §5 의 methodology base 에 이 근거로 기록해 두는 것을 제안합니다.
- **핀 교체 제안 없음** — 현 시점에서 P1 / P4 의 핀을 교체할 근거는 없습니다. 코드 미공개 + 단일 시행 보고 + 라우터 정확도 미보고라는 세 조건이 해소되기 전에는 methodology base 수준의 추적이 적정합니다.

> 💡 base 매핑은 `/implement-design analysis/2607.26807/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
