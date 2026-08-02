# Paper Analysis — FM-VLA: Force-based Memory for Vision-Language-Action Models in Contact-Rich Manipulation

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | FM-VLA: Force-based Memory for Vision-Language-Action Models in Contact-Rich Manipulation |
| 저자 | Ruicheng Li, Qixiu Li, Ruichun Ma, Yu Deng, Lin Luo, Zhiying Du, Jianfeng Xiang, Huizhi Liang, Ruicheng Wang, Jiaolong Yang, Baining Guo (Tsinghua University · Microsoft Research · Fudan University · USTC) |
| 링크 | [arXiv:2607.18231](https://arxiv.org/abs/2607.18231) · [Website](https://qft-333.github.io/FM-VLA-Page/) |
| 발행일 / 버전 | 2026-07-20 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-08-02 |
| 관련 Pillar | P2, P1, P3, P4, P0 |
| 태그 | force, vla-arch, flow-matching |

<!-- 링크 검증 기록 (STYLE §5-4 정직성): arXiv abs/html 는 HTTP 200.
     Website(project page)는 논문 초록에 verbatim 으로 명시된 URL 이나, 본
     실행 환경의 네트워크 정책이 해당 호스트를 차단해 resolve 여부를
     확인하지 못했습니다. 실패한 호출과 상태를 verbatim 으로 기록합니다:
       curl -sS -o /dev/null -w "%{http_code}" -L "https://qft-333.github.io/FM-VLA-Page/"
       → curl: (56) CONNECT tunnel failed, response 403 / http_code 000
       curl -sS -o /dev/null -w "%{http_code}" -L "https://pages.github.com/"
       → http_code 000  (동일 차단 — 대조군)
     즉 404(부재)가 아니라 프록시 차단이며, URL 자체는 논문 본문에서
     그대로 옮긴 것으로 날조가 아닙니다. GitHub / HuggingFace 링크는 본문에
     언급이 없어 기재하지 않았습니다. -->

---

## 🧭 한 줄 요약 (TL;DR)

FM-VLA는 에피소드 전체의 손목 6축 wrench(힘·토크) 이력을 재구성 목표로 사전학습한 VAE 로 압축해 8개의 **force memory token** 으로 만들고, 이를 $`\pi_{0.5}`$ 플로우 매칭 액션 전문가의 suffix 에 붙여, 시각적으로 구분되지 않는 비-Markovian 접촉 과제(버튼 N회 누르기 등)를 푸는 첫 VLA 입니다. 시각 메모리 기반 baseline 대비 평균 성공률 53.7% → 83.3%, 추론 오버헤드는 +39.1 ms → +3.3 ms 로 뒤집습니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 대부분의 VLA 는 현재 관찰만으로 행동을 정하는 Markovian 정책이라, "버튼을 정확히 N번 눌렀는가", "어느 컵을 이미 열어봤는가" 처럼 **과거 상호작용 이력이 정답을 결정하는** 과제를 원리적으로 풀지 못합니다.
- **기존 접근의 한계** — 메모리를 붙인 선행 연구(MemoryVLA, MEM)는 전부 **시각/언어 토큰** 축에서만 메모리를 구성합니다. 버튼처럼 이동량이 미미한 접촉 사건은 화면에 아무 변화도 남기지 않아 시각 메모리가 원천적으로 관측하지 못하고, 과거 프레임을 저장·어텐션하는 비용이 토큰 길이와 지연을 함께 키웁니다.
- **힘을 쓴 선행 연구의 다른 한계** — ForceVLA, TA-VLA 계열은 힘/토크를 **현재 행동을 보정하는 순간 신호**로만 씁니다. 접촉이 성립했는지, 얼마나 세게 누르는지는 알지만 "몇 번 눌렀는지"를 축적하지 못하므로, 비-Markovian 의사결정에 필요한 장기 정보는 남지 않습니다.
- **본 논문의 가설** — 접촉 사건·힘 크기·반복 횟수 같은 상호작용 관련 정보는 힘 센서 시계열에 **직접적이고 모호하지 않게** 새겨지므로, 원시 wrench 이력을 압축한 표현을 액션 전문가에 조건으로 주면 시각 메모리보다 싸고 강한 시간 맥락을 얻는다는 것입니다.
- **왜 지금 중요한가** — 손목 6축 F/T 센서는 상용 양팔 플랫폼(AgiBot G1 등)에 기본 탑재되기 시작했고, $`\pi_{0.5}`$ 급 오픈 체크포인트의 플로우 매칭 액션 전문가는 suffix 토큰을 붙이는 방식의 확장을 쉽게 허용합니다. 즉 "저차원 고주파 접촉 스트림을 메모리로 쓴다"는 아이디어를 실제 로봇에서 저비용으로 검증할 조건이 갖춰졌습니다.

---

## 🧩 핵심 기여

- **힘 기반 메모리를 가진 최초의 VLA** — 저자들의 주장에 따르면 proprioceptive–wrench 스트림을 *순간 조건*이 아니라 *장기 메모리*로 취급한 첫 사례이며, 비-Markovian 접촉 집약적 과제에 대한 시간 추론을 가능하게 합니다.
- **Force-VAE (2단계 패러다임)** — 노이즈가 크고 비구조적인 장기 wrench 신호를 시계열 재구성 목표로 사전학습한 Perceiver-IO VAE 로 압축합니다. 라벨 없이 task-agnostic 잠재 공간을 얻고, end-to-end 주입 baseline 을 큰 폭으로 앞섭니다.
- **단기 상태 메모리와의 상보 설계** — 힘 이력만 조건으로 주면 접촉 전 반복 행동이라는 부작용이 생긴다는 관찰에서, 최근 0.9초 관절 상태 윈도우를 단일 토큰으로 붙이는 경량 projector 를 추가합니다.
- **RoPE 보존형 토큰 주입** — 메모리 토큰을 액션 전문가 suffix 의 **noisy-action 토큰 뒤**에만 붙여, base 정책 사전학습 당시의 RoPE 위치를 그대로 유지합니다.
- **실기 검증 + 효율** — 양팔 로봇 3개 접촉 과제에서 평균 83.3% (memoryless 27.8%, 시각 메모리 53.7%)를 달성하면서 추론 지연 증가는 3.3 ms 에 그칩니다.

---

## 🔑 기술 키워드

- **Wrench** — 3축 힘 + 3축 토크를 묶은 6차원 벡터. 손목 F/T 센서 한 개가 매 시점 내보내는 "접촉의 지문" 에 해당합니다.
- **Non-Markovian Policy** — 현재 관찰만으로는 정답 행동이 결정되지 않고 과거 이력이 필요한 정책. 같은 화면에서 "1번 더 누르기" 와 "그만두기" 가 갈리는 상황이 전형입니다.
- **Force Memory Token** — 에피소드 전체 wrench 이력을 압축한 소수(K=8)의 토큰. 액션 전문가에게 "지금까지 무슨 접촉이 몇 번 있었는지" 를 요약해 건네는 메모지 역할입니다.
- **Variational Autoencoder (VAE)** — 입력을 확률적 잠재 분포로 인코딩하고 복원하도록 학습하는 오토인코더. 여기서는 라벨 없이 힘 시계열의 거시 구조를 담는 잠재 공간을 만드는 데 씁니다.
- **Perceiver-IO** — 임의 길이 입력을 소수의 학습 가능한 latent query 로 cross-attention 하여 고정 크기로 줄이는 아키텍처. 100 Hz 급 긴 시계열을 8토큰으로 접는 압축기입니다.
- **Masked ELBO** — 패딩 프레임을 마스크로 제외한 재구성 항 + KL 정규화 항으로 구성한 VAE 학습 목표. 길이가 제각각인 이력을 배치로 묶기 위한 장치입니다.
- **Free Bits** — 잠재 차원별 KL 에 하한 $`\lambda`$ 를 두어 그 아래로 내려간 차원의 KL 기울기를 꺼버리는 정규화. posterior collapse (잠재가 전부 사전분포로 붕괴)를 막습니다.
- **Randomized Noise Pre-padding** — 학습 시 이력 앞에 임의 길이의 저진폭 가우시안 노이즈를 덧대는 증강. 모델이 "이력이 길다 = 에피소드가 많이 진행됐다" 는 지름길을 쓰지 못하게 막습니다.
- **Action-Expert Suffix** — 플로우 매칭 액션 전문가의 입력 시퀀스에서 noisy-action 토큰 뒤에 오는 구간. 메모리 토큰이 들어가는 유일한 자리이며, 이 위치 선택이 RoPE 보존의 핵심입니다.
- **Flow Matching** — 플로우 매칭 — 노이즈에서 데이터로 가는 속도장을 회귀 학습하는 생성 목표. $`\pi_{0.5}`$ 의 액션 청크 생성 방식이며 FM-VLA 도 이를 그대로 승계합니다.

---

## 🔬 방법론

### 직관

FM-VLA 의 출발점은 아주 단순한 관찰입니다. 로봇이 버튼을 세 번 눌러야 한다고 할 때, 카메라에는 세 번 모두 거의 같은 장면이 찍힙니다. 버튼의 이동 거리가 몇 mm 라서 시각적으로는 "눌렀다" 와 "안 눌렀다" 가 구분되지 않기 때문입니다. 반면 손목의 힘 센서에는 누를 때마다 뾰족한 충격 파형이 하나씩 찍힙니다. 즉 이 과제에서 "몇 번 눌렀는가" 라는 정보는 **영상이 아니라 힘 신호에만** 존재합니다.

그래서 이 논문은 메모리의 재료를 바꿉니다. 기존 메모리 VLA 가 과거 이미지 프레임을 저장했다면, FM-VLA 는 **에피소드가 시작된 순간부터 지금까지의 힘/토크 시계열 전체**를 메모리로 씁니다. 다만 이 신호를 그대로 넣을 수는 없습니다. 30 Hz 로 수천 프레임에 달하는 데다 노이즈가 심하고, 무엇보다 "이 파형에서 무엇이 중요한 사건인가" 라는 구조가 명시되어 있지 않기 때문입니다.

압축을 어떻게 배울 것인가가 핵심 설계 문제입니다. 논문은 정책과 함께 end-to-end 로 압축기를 학습시키는 소박한 방법이 잘 작동하지 않는다는 것을 먼저 확인하고, **2단계 방식**을 택합니다. 1단계에서는 정책과 무관하게 힘 시계열을 **복원**하도록 VAE 를 사전학습합니다. 복원을 잘 하려면 힘의 크기, 접촉 시작 시점, 사건의 개수 같은 거시 구조를 잠재에 담을 수밖에 없으므로, 과제 라벨 없이도 "접촉 사건을 세는 데 쓸 만한" 표현이 자연스럽게 생깁니다. 2단계에서는 이 인코더를 **얼려서** 잠재 평균만 뽑아 8개 토큰으로 만든 뒤, 액션 전문가에 조건으로 붙여 정책을 미세조정합니다.

여기에 한 가지 부작용 처리가 붙습니다. 힘 이력만 조건으로 주면, 아직 접촉하기 전 구간에서는 힘 신호가 사실상 비어 있어 정책이 방향을 잃고 같은 동작을 반복하는 현상이 나타납니다. 그래서 최근 0.9초의 관절 상태를 한 개 토큰으로 눌러 담아 함께 붙입니다. 요약하면 **"장기 = 힘(무슨 일이 있었나), 단기 = 관절 상태(지금 어디로 가고 있나)"** 라는 역할 분담입니다.

![Figure 1 — visual memory VLA vs FM-VLA](https://arxiv.org/html/2607.18231/x1.png)

> "Figure 1: Comparison between visual memory based VLA and FM-VLA, which incorporates force (wrench) based memory to enable temporal context understanding for non-Markovian, contact-rich manipulation tasks." (§1)
> (메모리의 *재료*를 시각 프레임에서 wrench 스트림으로 바꾼다는 본 논문의 한 문장짜리 주장을 시각화한 그림입니다.)

### 아키텍처

**문제 정식화와 두 스트림**

정책은 $`\pi(a_{t}\mid o_{t},l,h_{t})`$ 형태로, 기존 VLA 의 memoryless $`\pi(a_{t}\mid o_{t},l)`$ 에 시간 이력 $`h_{t}`$ 를 추가합니다. 이 $`h_{t}`$ 는 성격이 다른 두 proprioceptive 스트림으로 구성됩니다.

> "The first is a long-horizon wrench history $`\{f_{\tau}\}_{\tau=1}^{t}`$, where each $`f_{\tau}\in\mathbb{R}^{d_{f}}`$ with $`d_{f}=6`$ stacks the 3-axis force and 3-axis torque measured by a wrist-mounted six-axis force/torque (F/T) sensor; this stream captures accumulated contact events over an entire episode, providing temporal context for policy decision-making." (§3.1)
> (장기 스트림은 에피소드 시작부터 누적된 6차원 wrench 전체입니다. 길이가 시간에 따라 계속 늘어나는 **무한장 스트림**이라는 점이 뒤에 나오는 고정 K 토큰 압축과 pre-padding 증강의 이유가 됩니다.)

두 번째는 단기 관절 상태 윈도우 $`\{s_{\tau}\}_{\tau=t-W+1}^{t}`$ 이며, 각 $`s_{\tau}\in\mathbb{R}^{d_{s}}`$ 는 모든 팔의 관절 위치와 그리퍼 상태를 이어붙인 벡터입니다. 7-DoF 양팔 + 1-D 그리퍼 2개 구성에서는 $`d_{s}=16`$ 입니다. 두 스트림은 아래와 같이 concat 되어 $`h_{t}`$ 를 이룹니다 (식 1):

$$h_{t}\;=\;\big[\,\underbrace{\mathrm{Enc}_{\phi}\!\big(\{f_{\tau}\}_{\tau=1}^{t}\big)}_{\text{wrench history }Z_{f}\in\mathbb{R}^{K\times d_{h}}}\;\;\|\;\;\underbrace{\mathrm{Proj}_{\psi}\!\big(\{s_{\tau}\}_{\tau=t-W+1}^{t}\big)}_{\text{state history window}z_{s}\in\mathbb{R}^{d_{h}}}\,\big]$$

$`\mathrm{Enc}_{\phi}`$ 는 사전학습된 VAE 인코더로 무한장 wrench 이력을 차원 $`d_{h}`$ 의 고정 $`K`$ 토큰으로 압축하고, $`\mathrm{Proj}_{\psi}`$ 는 관절 상태 윈도우를 단일 토큰으로 보내는 경량 선형 사영입니다. 후자만 VLA 미세조정과 함께 end-to-end 로 학습됩니다.

**base 모델과 결합 지점**

> "We build FM-VLA based on $`\pi_{0.5}`$ [27], which consists of a VLM (PaliGemma [2] with a SigLIP [36] vision encoder), and a flow-matching [24] action expert." (§3.2)
> (base 는 오픈 체크포인트가 있는 $`\pi_{0.5}`$ 이며, VLM 은 현재 이미지·언어를 처리해 cross-attention 으로 액션 전문가를 조건화합니다. FM-VLA 의 신규 모듈은 VLM 쪽이 아니라 **액션 전문가 쪽에만** 들어갑니다 — 이 경계가 이 논문 설계의 중심축입니다.)

![Figure 2 — FM-VLA 전체 개요](https://arxiv.org/html/2607.18231/x2.png)

> "Figure 2: Overview. We augment a VLA with lightweight force-based temporal memory. Force/torque histories are encoded by a VAE encoder into latent representations, projected via MLP into force memory tokens that condition the flow matching action expert. A short-term state memory token is further appended to provide motion context." (§1)
> (wrench 이력 → 동결 VAE 인코더 → 사영 → force memory token → 액션 전문가 suffix 라는 단일 경로와, 그 옆에 붙는 단기 상태 토큰을 한 장으로 보여줍니다. 다만 캡션은 사영을 "MLP" 라 적고 §3.2.3 / §E.1 은 zero-init **선형** 레이어라고 적어 표기가 어긋납니다 — 아래 ⚖️ 한계 참조.)

**wrench 전처리 — EMA + 랜덤 노이즈 pre-padding**

원시 wrench 는 과제와 무관한 고주파 성분이 많아, 인과적 1차 EMA 로 평활합니다.

> "We apply a causal first-order exponential moving average $`\tilde{f}_{\tau}=\alpha f_{\tau}+(1-\alpha)\tilde{f}_{\tau-1}`$, which removes most noise while preserving onsets and peaks." (§3.2.1)
> (평활의 목적이 단순한 노이즈 제거가 아니라 **onset 과 peak 의 보존**이라는 점이 중요합니다. 접촉 개수 세기는 파형의 뾰족한 시작점에 전적으로 의존하므로, 과도한 저역통과는 곧 정보 파괴가 됩니다. 실제 값은 $`\alpha=0.3`$ 이며 100 Hz 센서를 30 Hz 로 다운샘플한 신호에 적용합니다(§E.1).)

두 번째 전처리는 이 논문에서 가장 미묘한 장치입니다.

> "We notice the length of the wrench history leaks temporal episode progress, letting the model shortcut on sequence length for action generation rather than utilizing signal temporal structure." (§3.2.1)
> (이력의 *길이* 자체가 "에피소드가 얼마나 진행됐는가" 를 누설합니다. 모델은 신호 내용을 읽는 대신 길이만 세는 지름길을 배울 수 있고, 그러면 접촉 횟수가 아니라 경과 시간에 반응하는 정책이 됩니다. 해법은 학습 시 이력 앞에 최대 10초(1000 프레임) 길이의 저진폭 가우시안 노이즈($`\sigma=0.05`$, quantile 정규화 후)를 임의 길이로 덧대 패딩–신호 경계를 흐리는 것이며, 추론 시에는 끕니다.)

**Force memory encoder (Force-VAE)**

> "We train a VAE on wrench time-series reconstruction as a task-agnostic encoder, producing a structured latent space that captures temporal patterns in contact events such as force magnitudes, contact counts, without requiring task-specific labels." (§3.2.2)
> (재구성이라는 목표가 라벨 없이도 "힘 크기·접촉 횟수" 를 잠재에 밀어 넣는 대리 감독 역할을 합니다. 이것이 뒤의 Q-Former/GRU ablation 을 이기는 근거로 제시됩니다.)

인코더·디코더 모두 소수의 학습 가능한 latent query 토큰 위에서 동작하는 Perceiver-IO 스택입니다. 처리 순서는 다음과 같습니다.

- **입력 정규화** — 이력 $`F=[f_{1},\ldots,f_{T}]\in\mathbb{R}^{T\times d_{f}}`$ 의 각 시점 신호를 **데이터셋 전체 통계 기준 quantile 정규화** 합니다. 과제별이 아니라 전역 통계라는 점이 task-agnostic 성격을 유지시킵니다.
- **토큰화** — 정규화된 신호를 입력 MLP 로 384차원에 사영하고 Fourier 위치 인코딩(32 bands, $`f_{\max}=1500`$)을 더해 wrench 토큰을 만듭니다.
- **인코딩** — cross-attention 2블록(1 head, head-dim 64)으로 wrench 토큰의 정보를 latent query 로 끌어오고, 그 뒤 10개의 latent self-attention 블록(8 heads, head-dim 32, dropout 0.1)이 latent 간 상호작용을 처리합니다.
- **사후분포 파라미터** — latent 별 선형 헤드가 posterior 를 내고 reparameterization 으로 샘플합니다 (식 2):

$$(\mu_{k},\log\sigma_{k}^{2})=\text{Head}_{\text{VAE}}\big(\text{Enc}_{\phi}(F)_{k}\big),\quad z_{k}=\mu_{k}+\sigma_{k}\odot\epsilon_{k},\;\;\epsilon_{k}\sim\mathcal{N}(0,I)$$

- **디코딩** — 시점별 Fourier 인코딩된 query 가 latent 토큰 $`Z`$ 에 cross-attention 하여 $`\hat{F}\in\mathbb{R}^{T\times d_{f}}`$ 를 복원합니다(2 cross-attention 블록, 8 heads).

결과 잠재는 $`Z\in\mathbb{R}^{K\times d_{z}}`$ 이며 실제 값은 $`K=8`$, $`d_{z}=96`$ 입니다.

**단기 상태 이력 — VAE 를 두 번 쓰지 않는 이유**

> "The action expert only needs to know “where the arms are and where they are heading”." (§3.2.2)
> (관절 상태는 힘과 달리 "최근 몇 프레임" 이면 역할이 충족되므로, 두 번째 VAE 를 두지 않고 사전학습 없는 경량 사영으로 충분하다는 판단입니다. 설계 비용을 모달의 시간 스케일에 맞춰 배분한 셈입니다.)

구체적으로는 매 제어 스텝 $`t`$ 에서 고정 stride 로 서브샘플한 $`S_{t}\in\mathbb{R}^{W\times d_{s}}`$ 를 뽑는데, 실제 설정은 stride 3 으로 최근 10 프레임, 즉 offsets $`\{-27,-24,-21,\ldots,-3,0\}`$ (30 Hz 기준 약 0.9초)입니다. 이를 flatten 하여 **zero-init 선형 레이어** 하나로 단일 토큰에 사영합니다. (본문 §3.2.2 는 이 윈도우가 "the last second of motion" 을 덮는다고 서술하고, §E.1 은 $`\approx 0.9\,`$s 로 명시합니다.)

**메모리 토큰 주입 위치**

동결된 인코더에서 **사후분포 평균 $`\mu_{f}\in\mathbb{R}^{K\times d_{z}}`$ 만** 취하고(추론 노이즈 없음), zero-init 선형 레이어로 $`d_{z}=96`$ 에서 액션 전문가 hidden width $`d_{h}`$ 로 올려 $`Z_{f}\in\mathbb{R}^{K\times d_{h}}`$ 를 만듭니다. 시퀀스 배치는 다음과 같습니다 (식 3):

$$\underbrace{[\,a_{k}^{(1)},\ldots,a_{k}^{(H)}\,]}_{\text{noisy-action tokens}}\;\|\;\underbrace{[\,Z_{f}^{(1)},\ldots,Z_{f}^{(K)}\,]}_{\text{wrench memory}}\;\|\;\underbrace{[\,z_{s}\,]}_{\text{state window}}$$

> "Placing both memory streams in the post-position keeps the noisy-action tokens at the same RoPE positions they had during base-policy pretraining." (§3.2.3)
> (이 한 문장이 주입 위치 선택의 전체 근거입니다. 메모리 토큰을 앞에 끼우면 30개 noisy-action 토큰이 전부 뒤로 밀려 사전학습 당시와 다른 RoPE 위치를 갖게 되고, base 정책이 이미 학습한 위치 의존 구조가 흐트러집니다. 뒤에 붙이면 기존 위치가 그대로 보존됩니다. 비교군인 TA-VLA 재구현이 힘 토큰을 noisy-action **앞**에 prepend 하는 것과 정확히 대비되는 선택입니다(§D).)

### 학습 목표 / 손실

학습은 2단계로 분리됩니다. 1단계는 정책과 무관하게 힘 표현만 학습하고, 2단계는 그 표현을 얼린 채 정책을 미세조정합니다.

**Stage 1 — Force-VAE 사전학습**

목표는 유효 프레임에 대한 마스크 재구성 항과, 잠재 차원별 free-bits 정규화 KL 항의 합입니다 (식 4):

$$\mathcal{L}_{\text{VAE}}=\frac{1}{\sum_{\tau}m_{\tau}\cdot d_{f}}\sum_{\tau=1}^{T}m_{\tau}\|f_{\tau}-\hat{f}_{\tau}\|^{2}\;+\;\beta\cdot\frac{1}{Kd_{z}}\sum_{k,j}\max\!\big(D_{\text{KL}}^{(k,j)},\lambda\big)$$

여기서 $`m_{\tau}\in\{0,1\}`$ 는 패딩 프레임을 가리는 마스크이고, $`D_{\text{KL}}^{(k,j)}`$ 는 $`\mathcal{N}(\mu_{k,j},\sigma_{k,j}^{2})`$ 와 표준정규 사전분포 사이의 차원별 KL 이며, $`\beta`$ 는 정규화 세기입니다.

> "the per-dimension free-bits floor $`\lambda`$ prevents posterior collapse by switching off the KL gradient on dimensions that already encode less than $`\lambda`$ nats" (§3.3)
> ($`\max(\cdot,\lambda)`$ 형태 덕분에 이미 $`\lambda`$ nats 미만을 담은 차원은 KL 기울기를 받지 않습니다. KL 항이 잠재를 전부 사전분포로 눌러버려 인코더가 아무 정보도 남기지 않게 되는 붕괴를, 접촉 사건 같은 희소 정보를 다루는 이 설정에서 특히 방지해야 합니다. 값은 $`\beta=1\times10^{-3}`$, $`\lambda=0.5`$ nats 입니다.)

과제별 데이터 크기 불균형은 **inverse-frequency task sampling** 으로 보정해, 하나의 VAE 를 전 과제 wrench 이력에 공동 사전학습합니다.

**Stage 2 — VLA 미세조정**

> "We freeze the force encoder and switch it to evaluation mode for fine-tuning on our dataset." (§3.3)
> (동결 + eval 모드 전환이므로 dropout 도 꺼지고, reparameterization 노이즈 없이 사후분포 평균만 씁니다. 즉 2단계에서 힘 표현은 **결정적 함수**로 고정되고, 학습 자유도는 사영 레이어와 정책 쪽에만 남습니다.)

$`\pi_{0.5}`$ 의 rectified-flow 레시피를 따라 데이터에서 깨끗한 액션 청크 $`a_{0}`$, 가우시안 노이즈 $`\epsilon\sim\mathcal{N}(0,I)`$, 노이즈 레벨 $`k\in[0,1]`$ 을 뽑아 $`a_{k}=(1-k)\,a_{0}+k\,\epsilon`$ 를 만들고, 직선 경로의 상수 속도 $`\epsilon-a_{0}`$ 를 예측하도록 학습합니다 (식 5):

$$\mathcal{L}=\mathbb{E}_{a_{0},\,\epsilon,\,k}\left[\big\|v_{\theta}(a_{k},k,c_{t},Z_{f},z_{s})-(\epsilon-a_{0})\big\|^{2}\right]$$

손실 형태 자체는 base $`\pi_{0.5}`$ 와 동일하고, 속도장 $`v_{\theta}`$ 의 조건 인자에 $`Z_{f}`$ 와 $`z_{s}`$ 가 추가된 것이 전부입니다. **새로운 보조 손실이 전혀 없다**는 점이 이 방법의 통합 비용을 낮추는 실질적 요인이며, 힘 예측 보조 헤드를 두는 TA-VLA 계열과 대비됩니다. 공동 학습 대상은 VLM 인코더, 플로우 매칭 액션 전문가, 단기 상태 사영 $`\mathrm{Proj}_{\psi}`$, wrench 잠재 사영 $`W_{f}`$ 이며, 힘 인코더만 동결입니다.

### 학습 셋업

- **플랫폼 / 데이터** — AgiBot G1 양팔 휴머노이드(7-DoF 팔 2개 + 1-DoF 그리퍼 2개), 각 손목에 100 Hz 6축 wrench 센서. 관찰은 머리 1대 + 손목 2대 RGB + proprioception. VR 기반 텔레오퍼레이션으로 Task 1/2/3 에 각각 200 / 350 / 200 시연을 수집했습니다.
- **초기화** — OpenPI 가 공개한 $`\pi_{0.5}`$ 체크포인트에서 시작해 Zhiyuan Challenge 데이터셋으로 추가 사전학습(batch 64, 150K steps, delta action 타깃)한 체크포인트를 모든 실험의 출발점으로 씁니다(§C).
- **Stage 1 하이퍼파라미터** — hidden/latent 384/384, $`d_{z}=96`$, $`K=8`$, encoder/decoder cross-attn depth 2/2, processor self-attn 10층, Fourier 32 bands, input dropout 0.2, attention dropout 0.1, AdamW $`(0.9,0.95)`$, grad-clip 1.0, peak LR $`3\times10^{-4}`$, warm-up 1,000, total 100,000 steps, batch $`64\times8=512`$, bf16.
- **Stage 2 하이퍼파라미터** — action chunk horizon $`H=30`$, action dim 32, 평가 시 flow-matching 10 step, force memory 토큰 8개, state-window taps 10(stride 3, 0.9 s), 뷰별 이미지 dropout $`p=0.4`$, quantile $`q_{01}/q_{99}`$ 정규화, AdamW, warm-up 1,000, peak LR $`5\times10^{-5}`$, total 50,000 steps, global batch 32, bf16, 8×A100 (40 GB).
- **공정성 통제** — 모든 baseline 이 동일 데이터·동일 정규화 통계·동일 LR 스케줄(1k warm-up, peak $`5\times10^{-5}`$, decay 없음, 50k steps)·동일 global batch 32·동일 이미지 dropout $`p=0.4`$ 로 후학습됩니다(§D). 힘 인코더 아키텍처만 바꾸는 ablation 도 Stage 2 레시피를 공유합니다(§E.4).

---

## 📊 실험 설정과 결과

### 과제와 성공 기준

세 과제 모두 "화면은 거의 그대로인데 정답은 이력에 달려 있는" 구조로 설계되었습니다.

| 과제 | 시연 수 | 시행 수 | 메모리가 필요한 이유 | 성공 판정 (§B.2) |
|---|---|---|---|---|
| Task 1: Find a Block Under Two Cups | 200 | 18 (앞 컵 9 / 뒤 컵 9) | 컵을 내려놓으면 장면이 원래대로 돌아와, 어느 컵을 이미 확인했는지 기억해야 함 | (i) 각 컵 1회 이하 들기 (ii) 블록이 왼손에 잡힘 (iii) 마지막 든 컵을 오른손이 내려놓음 |
| Task 2: Push Buttons | 350 | 18 ($`N\in\{1,2,3\}`$ 각 6) | 버튼 이동량이 미미해 시각 변화가 거의 없음 | 정확히 $`N`$ 회의 **가청 click** 후 그리퍼 개방. 과소·과다 모두 실패 |
| Task 3: Wipe Dishes | 200 | 18 ($`N\in\{1,2,3\}`$ 각 6) | 닦는 동안 장면 변화가 미미해 wrench 이력이 주 단서 | 좌 rim→우 rim 접촉 유지한 왕복 $`N`$ 회 후 그리퍼 개방 |

성공률 판정 자체에도 시간 조건이 붙습니다.

> "We use the success rate as the primary metric and consider a trial successful if the robot completes the task and reaches a stable termination (opened gripper, no motion for $`\sim`$ 3 s)." (§4.2)
> ("과제를 했는가" 뿐 아니라 "제때 멈췄는가" 까지 성공 조건에 넣었기 때문에, 이 벤치마크는 카운팅 능력을 직접 채점합니다. 무한 반복하는 정책은 동작을 수행하더라도 실패로 기록됩니다.)

### 주 결과 및 ablation (Table 1)

| Method | Task 1: Cups | Task 2: Buttons | Task 3: Wipe | Average |
|---|---|---|---|---|
| $`\pi_{0.5}`$ (no history) | 72.2 (13/18) | 11.1 (2/18) | 0.0 (0/18) | 27.8 |
| TA-VLA [40] | 50.0 (9/18) | 11.1 (2/18) | 5.6 (1/18) | 22.2 |
| $`\pi`$-MEM [32] | 77.8 (14/18) | 33.3 (6/18) | 50.0 (9/18) | 53.7 |
| *Modality ablation (VAE)* | | | | |
| Force history only | 55.6 (10/18) | 0.0 (0/18) | 22.2 (4/18) | 25.9 |
| State history only | 100.0 (18/18) | 11.1 (2/18) | 11.1 (2/18) | 40.7 |
| *Architecture ablation (Force + Short State History)* | | | | |
| FM-VLA (GRU) | 55.6 (10/18) | 38.9 (7/18) | 5.6 (1/18) | 33.3 |
| FM-VLA (Q-Former) | 100.0 (18/18) | 16.7 (3/18) | 55.6 (10/18) | 57.4 |
| **FM-VLA (VAE, ours)** | **100.0 (18/18)** | **72.2 (13/18)** | **77.8 (14/18)** | **83.3** |

> "FM-VLA consistently outperforms all baselines, achieving an average success rate of 83.3%." (§4.2, Table 1)
> (세 과제 평균값이며, 시각 메모리 baseline 53.7% 대비 +29.6%p, memoryless $`\pi_{0.5}`$ 27.8% 대비 +55.5%p 입니다.)

> "Notably, while the visual-memory baseline $`\pi`$-MEM shows moderate improvements on Cups and Wipe, it fails heavily on the Buttons task (33.3% vs. our 72.2%). This confirms that visual memory is insufficient for tasks lacking clear visual state changes." (§4.2, Table 1)
> (이 논문의 핵심 주장을 가장 직접적으로 지지하는 대비입니다. 시각 메모리가 유효한 과제(컵·닦기 — 물체 배치나 스펀지 위치가 조금은 보임)와 원리적으로 무효인 과제(버튼 — 변위가 없음)를 갈라놓았고, 후자에서만 격차가 두 배 이상 벌어집니다.)

주목할 만한 것은 TA-VLA 가 memoryless $`\pi_{0.5}`$ 보다도 **낮다**(22.2 vs 27.8)는 점입니다. 짧은 wrench 윈도우 + 미래 힘 예측 보조 헤드라는 구성이 이 비-Markovian 과제군에서는 도움이 되지 않을 뿐 아니라, Cups 과제에서 72.2→50.0 으로 오히려 해가 됩니다. 논문은 전자(장기 정보 부재)만 설명하고 후자의 퇴행 원인은 다루지 않습니다.

**per-ablation 판독 — 무엇을 분리하는가**

- **Force history only (25.9%)** — 장기 힘 메모리 단독의 값을 격리합니다. 놀랍게도 Buttons 에서 0.0% 로, 힘 정보가 가장 필요한 과제에서 완전히 실패합니다. 논문의 설명은 접촉 *전* 공간 인식 부재로 인한 불규칙한 pre-contact 동작이며, 이는 "메모리가 있어도 그 메모리를 쓸 자세에 도달하지 못하면 무의미하다" 는 뜻입니다.
- **State history only (40.7%)** — 관절 상태 단독. Cups 에서 100.0% 로 full 모델과 동일한데, 이는 Cups 가 사실 **공간 과제**임을 드러냅니다(어느 컵을 열었는지는 팔 궤적 이력에도 남습니다). 반대로 Buttons 11.1% / Wipe 11.1% 로 접촉 카운팅에는 무력합니다. 두 modality ablation 을 겹쳐 읽으면, 세 과제 중 **힘 메모리가 결정적인 것은 Buttons 와 Wipe 뿐**이라는 점이 드러납니다.
- **GRU (33.3%)** — 저용량 순환 요약기가 충분한가를 검사합니다. Wipe 5.6% 로 붕괴하며, 논문은 100 Hz 급 장기 시퀀스에서의 gradient 소실과 초기 접촉 사건 망각을 원인으로 듭니다. 다만 Buttons 38.9% 로 Q-Former(16.7%)보다 높아, 순위가 과제별로 뒤집힙니다.
- **Q-Former (57.4%)** — 토큰 예산($`K=8`$)과 suffix 위치를 FM-VLA 와 동일하게 맞추고, 차이를 (i) 동결 Perceiver-IO VAE 대신 cross-attention, (ii) wrench 재구성 사전학습 대신 정책과 함께 from-scratch 학습 두 가지로만 좁힌 대조군입니다. 즉 **"사전학습된 재구성 표현" 자체의 기여를 격리**하는 가장 깨끗한 비교이며, Buttons 16.7 → 72.2 의 격차가 그 값입니다.

> "By contrast, our VAE is pretrained on a continuous wrench reconstruction objective, which forces the latent space to encode macroscopic structure, e.g., force magnitudes, onset timings, and contact counts, in a few tokens, making task-relevant signals easy for the VLA action expert to extract." (§4.3)
> (재구성 목표가 "무엇을 담을지" 를 강제하는 대리 감독이라는 주장입니다. Q-Former 는 정책 손실만 받으므로 순간 피크에 과적합하고, VAE 는 신호 전체를 복원해야 하므로 거시 구조를 담을 수밖에 없다는 논리입니다.)

**토큰 수 ablation**

![Figure 3 — 토큰 수 ablation](https://arxiv.org/html/2607.18231/x3.png)

> "Figure 3: Token count ablation." (§4.3)
> (Wipe Dishes 과제에서 VAE latent 토큰 수 $`\{4,8,16,32\}`$ 를 훑은 결과로, 8 에서 정점을 이룹니다.)

> "4 tokens form an informational bottleneck, while 16 and 32 tokens unexpectedly degrade performance. We attribute this to distribution shift, as the pretrained $`\pi_{0.5}`$ action expert observes at most 50 tokens during training, so 32 extra force tokens exceed this limit and disrupt coherent action generation." (§4.3)
> (성능이 토큰 수에 단조 증가하지 않고 **base 정책의 사전학습 토큰 예산**이 상한을 만든다는 진단입니다. 즉 $`K`$ 는 표현 용량이 아니라 base 모델의 분포 유지 조건이 결정하는 값이며, base 를 바꾸면 최적값도 달라집니다.)

### 추론 효율 (Table 2)

| Method | Latency (ms) | $`\Delta`$ vs. base (ms) |
|---|---|---|
| $`\pi_{0.5}`$ (base) | 60.7 $`\pm`$ 0.3 | — |
| $`\pi`$-MEM [32] ($`K{=}5`$) | 99.8 $`\pm`$ 0.4 | +39.1 |
| $`\pi`$-MEM [32] ($`K{=}16`$) | 190.0 $`\pm`$ 1.0 | +129.3 |
| **FM-VLA (ours)** | **64.0 $`\pm`$ 0.4** | **+3.3** |

> "FM-VLA shows a 64 ms latency, introducing negligible 3 ms overhead on top of the base model, In comparison, $`\pi`$-MEM shows a 100 ms inference latency and 39 ms increase, due to the overhead of multiple RGB frames input to the vision/video encoder as memory." (§4.4, Table 2)
> (RTX 4090 기준입니다. 시각 메모리는 프레임 수에 비례해 비용이 늘어 $`K{=}16`$ 에서 +129.3 ms 까지 가지만, 힘 메모리는 6차원 시계열을 한 번 인코딩할 뿐이라 프레임 수와 무관하게 상수 비용에 가깝습니다. 성능·비용 두 축을 동시에 뒤집었다는 점이 이 표의 핵심입니다.)

![Figure 4 — 궤적과 힘 신호 시각화](https://arxiv.org/html/2607.18231/x4.png)

> "Figure 4: Trajectory and force signal visualization. For each task, we visualize the FM-VLA inference trajectory and a selected channel of force readings, with each frame’s time marked. FM-VLA correctly memorizes contact events and complete manipulation successfully." (§4.4)
> (과제별로 추론 궤적과 힘 채널 하나를 시간축에 나란히 놓아, 접촉 사건이 파형의 뾰족한 피크로 나타나고 그 개수가 행동 종료 시점과 대응함을 보이는 정성 근거입니다.)

---

## ⚖️ 한계

- **저자 명시 (1) — 고정 8토큰 병목** — 논문은 "수백 개 접촉 사건 규모의 매우 긴 지평" 에서는 계층적·적응적 압축이 필요할 수 있다고 인정합니다. 더 근본적인 문제는 §4.3 의 진단과 결합될 때 드러납니다. 토큰을 늘리는 것이 base 정책의 50토큰 예산 때문에 막혀 있으므로, "긴 지평 → 토큰 증가" 라는 자연스러운 확장 경로가 **base 모델에 의해 봉쇄**되어 있습니다. 계층적 압축이 필요하다는 저자의 처방은 선택이 아니라 구조적 강제입니다.
- **저자 명시 (2) — 시연 데이터로만 학습한 VAE** — Force-VAE 가 본 논문의 3개 과제 시연에서 나온 wrench 이력만 보고 학습됩니다. "task-agnostic 인코더" 라는 표현은 *과제 라벨을 쓰지 않는다*는 뜻이지 *과제 분포를 벗어난다*는 뜻이 아니며, 실제로는 3개 과제의 힘 분포에 특화된 잠재 공간일 가능성이 큽니다. 저자도 대규모 다양 F/T 코퍼스 사전학습이 성능을 더 높일 수 있다고 적습니다.
- **추론 갭 (1) — 단일 손목, 단일 팔의 힘만 사용** — §E.1 은 **오른손목** wrench 스트림만 쓴다고 명시합니다. 양팔 로봇이고 Task 1 은 양손 협응(오른손이 컵, 왼손이 블록)인데 왼손 접촉은 메모리에 전혀 들어가지 않습니다. 6차원 한 스트림이 전체 접촉 사건을 대표한다는 가정이 암묵적으로 깔려 있고, 손가락 단위 접촉이 있는 다지 손으로 가면 이 가정은 성립하지 않습니다.
- **추론 갭 (2) — 통계적 검정력** — 과제당 18 시행이고 성공률이 1/18 ≈ 5.6%p 단위로 양자화됩니다. 72.2%(13/18) vs 33.3%(6/18) 같은 큰 격차는 이 표본으로도 신뢰할 만하지만, Q-Former 57.4 vs GRU 33.3 같은 중간 격차나 Cups 100.0 vs 77.8 는 시행 수가 결론을 좌우할 여지가 있습니다. 반복 시드·신뢰구간이 보고되지 않습니다.
- **추론 갭 (3) — Force-only 붕괴의 미해명** — Force-only 가 Buttons 에서 0.0% 로, memoryless base(11.1%)보다도 낮습니다. "pre-contact 공간 인식 부재" 라는 설명은 성능 저하는 설명하지만 base 이하로 떨어지는 것까지 설명하지는 않습니다. 힘 토큰이 조건으로 들어올 때 정책이 능동적으로 해로운 사전(prior)을 학습할 가능성이 남아 있고, 이는 메모리 주입이 항상 안전한 증분은 아님을 시사합니다.
- **추론 갭 (4) — TA-VLA 퇴행의 미해명** — 위와 같은 맥락에서, TA-VLA 재구현이 Cups 에서 base 대비 72.2→50.0 으로 떨어진 것도 설명되지 않습니다. TA-VLA 는 힘 토큰을 noisy-action **앞에** prepend 하므로 RoPE 위치가 밀립니다. FM-VLA 의 post-position 근거(§3.2.3)와 나란히 놓으면 이 퇴행이 위치 선택 때문일 가능성이 크지만, 논문은 두 사실을 연결하는 통제 실험(같은 인코더, 위치만 변경)을 제시하지 않습니다. 즉 이 논문의 설계 결정 중 **가장 값싸고 가장 이식성 높은 요소(post-position)** 가 정작 직접 검증되지 않은 채 남습니다.
- **표기 불일치 — MLP vs 선형** — Figure 2 캡션은 잠재를 "projected via MLP into force memory tokens" 이라 적지만, §3.2.3 과 §E.1 은 zero-init **선형** 레이어라고 명시합니다. 재현 시 본문 쪽을 따르는 것이 안전하며, 그림 캡션은 개념 도식으로 읽어야 합니다.
- **평가 폭 — 과제 3개, 카운팅 편중** — 세 과제 중 둘(Buttons, Wipe)이 사실상 같은 능력(접촉 사건 카운팅)을 재는 변주이고, 나머지 하나(Cups)는 ablation 결과 관절 상태만으로 100% 가 나오는 공간 과제입니다. 결국 "힘 메모리" 의 고유 기여를 지지하는 독립 증거는 두 개의 카운팅 과제로 좁혀집니다. 힘 크기 추적, 접촉 품질 판단 등 카운팅이 아닌 힘 메모리 용례는 검증되지 않았습니다.

---

## ♻️ 재현성

- **코드 / 가중치** — 본문에 코드·체크포인트 공개 언급이 없습니다. 초록의 project page URL 만 제시되며, GitHub·HuggingFace 링크는 본문에 나타나지 않습니다.
- **데이터** — 자체 수집 텔레오퍼레이션 시연(200/350/200)이며 공개 계획 언급이 없습니다. 사전학습에 쓴 Zhiyuan Challenge 데이터셋과 base $`\pi_{0.5}`$ OpenPI 체크포인트는 외부 자산입니다.
- **명세 수준은 높음** — Appendix B(과제 규칙·성공 기준·정확한 언어 지시문 문자열), C(초기화), D(baseline 구현 상세 — TA-VLA 의 offsets $`\{-27,-24,\ldots,-3,0\}`$, 손실 가중 1.0/0.1, $`\pi`$-MEM 의 4층마다 temporal self-attention 삽입·파라미터 재사용까지), E(Table 3/4 전 하이퍼파라미터)가 이례적으로 상세합니다. 코드 없이도 사양 재구현이 가능한 수준의 정보량입니다.
- **하드웨어 재현성** — AgiBot G1 양팔 휴머노이드 + 손목 6축 F/T 100 Hz 가 필수 전제이며, 학습은 8×A100 (40 GB), 지연 측정은 RTX 4090 입니다. 실기 평가(과제당 18 시행)는 동일 하드웨어 없이 재현할 수 없습니다.
- **종합** — 사양 재현성은 높고, 결과 재현성은 하드웨어와 자체 데이터에 묶여 낮습니다. Force-VAE 자체는 6차원 시계열만 있으면 학습되므로 **공개 F/T 코퍼스(RH20T 등)로 부분 재현이 가능한 유일한 컴포넌트**입니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P2(구조적 멀티모달 관찰 융합) — 주 pillar.**
  - **D10(heterogeneous modality fusion beyond concat)** — 힘을 flat concat 이 아니라 **별도 인코더 → 전용 토큰 → suffix 주입** 경로로 융합합니다. PROBE v1 의 "cross-attention / asymmetric fusion" 방향과 정렬되며, 특히 "모달마다 그 모달의 시간 스케일에 맞는 인코더를 준다"(장기 힘 = 사전학습 VAE, 단기 상태 = 선형 사영)는 비대칭 설계의 구체적 사례입니다.
  - **D11(proprio-tactile-force token construction)** — 가장 직접적인 접점입니다. PROBE 의 D11 v1 은 **공간 축**(손가락별 proprio-촉각 결합, 10 finger + 2 palm 토큰)으로만 정의되어 있고 **시간 축 집약**이 없습니다. FM-VLA 는 같은 접촉 토큰 문제를 시간 축에서 풀어, D11 에 빠져 있던 차원을 보여줍니다. 또한 "contact-binary + slip-binary aux head" 라는 명시적 보조 감독 대신 **재구성 사전학습**이라는 무라벨 대안을 제시합니다.
  - **D9(action/dynamics-aware vision encoder)** — 직접 대상은 아니지만 레시피가 동형입니다. D9 이 "동역학을 담도록 사전학습한 *비전* 인코더" 를 선호하듯, FM-VLA 는 "동역학을 담도록 사전학습한 *힘* 인코더" 를 씁니다. 사전학습된 모달 인코더 > from-scratch 라는 명제가 힘 모달에서도 성립한다는 증거(Q-Former 57.4 → VAE 83.3)입니다.
  - **D8(multi-camera spatial-geometric grounding)** — 무관합니다. 본 논문은 카메라 3대를 쓰지만 공간 grounding 기여가 없습니다.
- **P1(이종 Body/Hand 액션 전문가) — 부 pillar.**
  - **D7(π backbone integration / partition)** — 매우 실용적인 접점입니다. $`\pi_{0.5}`$ 액션 전문가에 새 조건 스트림을 붙이면서 **RoPE 위치를 보존하는 suffix 배치**와 **zero-init 사영**을 쓰는 패턴은, PROBE 가 D7 v1 에서 "π0 액션 전문가를 slice 하고 양쪽을 FT" 할 때 그대로 재사용 가능한 통합 규약입니다.
  - **D5(input-modality + control-rate separation)** — 힘 100 Hz → 30 Hz 다운샘플, 상태 30 Hz stride 3, 정책은 30-step 청크라는 **모달별 시간 해상도 분리**의 구체 수치를 제공합니다. PROBE v1 은 "modality-separated + shared rate" 인데, 본 논문은 shared rate 를 유지하면서도 모달별 히스토리 길이를 다르게 가져가는 중간 형태입니다.
  - **D4/D1/D2/D3** — 액션 디코더는 32차원 단일 flow-matching 헤드(monolithic)로, Body/Hand 분리 차별화와는 **반대편 비교군**입니다. 그리퍼가 1-DoF 라 손가락 수준 기여는 없습니다.
- **P3(Hand-level System0, RL-scoped) — 개념적 접점, 계층은 다름.**
  - **D15(System0 input modality)** — PROBE 의 System0 입력 정의에 이미 "contact-state history" 가 들어 있습니다. FM-VLA 는 같은 재료(접촉 이력)를 **System1 레벨의 과제 진행 추적**에 씁니다. 즉 접촉 이력이 저수준 안정화와 고수준 진행 추적 **양쪽**에 쓰인다는 것을 보여주며, 두 계층이 같은 스트림을 다른 시간 스케일로 소비하는 설계(System0 = 수 ms 반응, System1 = 에피소드 요약)를 시사합니다.
  - **D13/D14/D16/D17/D18** — RL 이 전혀 없고 sim2real 도 없어(전 과정 실기 imitation) 무관합니다.
- **P4(데이터 효율 적응을 위한 사전학습) — 부 pillar, 긴장 있음.**
  - **D20(prior-preservation strategy)** — PROBE v1 은 "action-side adapter + 백본 무손상" 입니다. FM-VLA 의 zero-init 사영 + RoPE 보존 suffix 는 정확히 action-side adapter 계열의 prior 보존 장치이나, **VLM 인코더를 함께 미세조정**하므로 D19 v1 의 "(a) full VLM freeze" 와는 충돌합니다. 즉 보존 기법은 채택하되 보존 범위는 우리 선택보다 느슨합니다.
  - **D23(action representation × pretraining)** — 연속 flow-matching 헤드를 그대로 유지하며 조건만 추가하므로 v1 과 완전히 정렬됩니다. 새 보조 손실이 없다는 점이 이 정렬을 강화합니다.
  - **D21/D22** — 2단계(표현 사전학습 → 정책 미세조정) 구조 자체는 D21 의 staged recipe 사고와 닮았지만, 대상이 VLM 코퍼스가 아니라 힘 인코더라 직접 증거는 아닙니다.
- **P0(VLA 데이터셋 & 벤치마크) — 약한 tie, 그러나 수요 신호.**
  - **D25(tactile/force/torque data scouting)** — 본 논문의 Limitations 가 "대규모 다양 F/T 코퍼스로 VAE 를 사전학습하면 더 좋아질 것" 이라고 명시합니다. 이는 D25 가 "희소성을 first-class gap 으로 취급" 한 판단을 외부에서 확인해 주는 수요 신호입니다. 다만 본 논문 자체는 데이터를 공개하지 않으므로 P0 §4 anti-topic("데이터 미공개") 관점에서 자원 기여는 없습니다.
- **P5(World Model) — 무관.** 힘 이력을 *요약*할 뿐 미래를 *예측*하지 않으며, 행동 조건부 동역학 모델이 아닙니다. VAE 는 과거 재구성용이지 forward 예측용이 아닙니다.
- **Identity 긴장/지지** — PROBE Identity 는 "vision-dominant observation + flat concat" 을 antagonist 로 지목합니다. 본 논문은 시각 메모리가 원리적으로 관측 불가능한 과제군을 구성해 그 antagonist 를 **실기 성공률로 반증**했고(시각 메모리 33.3% vs 힘 메모리 72.2%), 접촉 모달의 독립적 필요성을 지지합니다. 반면 손가락 단위 접촉 귀속(D11 의 핵심)은 없고 손목 단일 6축이며, 액션 디코더는 monolithic 이라 Body/Hand 분리 주장과는 무관합니다. 즉 **관찰 축(P2)에서는 강한 지지, 디코더 축(P1)에서는 비교군**입니다.
- **경쟁자 함의** — Microsoft Research + Tsinghua 조합이 π 계열 오픈 체크포인트 위에 접촉 메모리를 얹는 저비용 경로를 이미 실기로 보였습니다. "접촉 스트림을 장기 메모리로 쓴다" 는 아이디어 자체는 선점되었다고 보아야 하며, PROBE 의 차별화 여지는 손가락 단위 귀속(D11) × 시간 축 결합이라는 아직 비어 있는 교차점입니다.

---

## ✨ 핀 논문 대비 델타

- **vs ForceFlow (P2 핀, [arXiv:2605.11048](https://arxiv.org/abs/2605.11048))** — ForceFlow 는 접촉 구동 플로우 매칭 + 비대칭 멀티모달 융합으로 D10 을 대표합니다. 둘 다 힘을 일급 모달로 다루지만 **시간 지평이 정반대**입니다. ForceFlow 계열은 현재 행동을 보정하는 순간/단기 조건이고, FM-VLA 는 에피소드 전체를 요약한 상태 메모리입니다. FM-VLA 의 진짜 신규성은 융합 방식이 아니라 **융합되는 신호의 시간 범위**입니다.
- **vs ViTacFormer (P2 핀, [arXiv:2506.15953](https://arxiv.org/abs/2506.15953))** — cross-attention 비주오택타일 융합 역시 per-step 융합입니다. FM-VLA 는 촉각 대신 손목 wrench 를 쓰고 공간 해상도를 포기하는 대신 시간 축을 얻습니다. 두 축(공간 귀속 ↔ 시간 축적)에서 상보적이며, 둘을 합친 설계는 아직 문헌에 없습니다.
- **vs DynaFLIP (P2 핀, [arXiv:2605.30350](https://arxiv.org/abs/2605.30350))** — DynaFLIP 은 "동역학을 담도록 사전학습한 인코더가 generic stem 보다 낫다" 를 비전 모달에서 주장합니다. FM-VLA 의 Q-Former ablation(57.4 vs 83.3)은 **같은 명제가 힘 모달에서도 성립**함을 보이는 독립 증거이며, D9 의 논거를 모달 밖으로 일반화합니다.
- **vs $`\pi_{0.5}`$ (P4 핀, [arXiv:2504.16054](https://arxiv.org/abs/2504.16054))** — base 그 자체입니다. 델타는 (i) 액션 전문가 suffix 에 8+1 메모리 토큰 추가, (ii) 힘 인코더 동결 2단계 학습, (iii) 손실식 무변경(조건 인자만 확장) 세 가지뿐이며, base 대비 순수 지연 증가는 +3.3 ms 입니다. "π 백본에 새 모달을 최소 침습으로 붙이는" 레시피의 참조 구현으로 읽는 것이 가장 실용적입니다.
- **vs RH20T (P0 핀, [arXiv:2307.00595](https://arxiv.org/abs/2307.00595))** — RH20T 는 PROBE 가 추적하는 희소한 6축 F/T 보유 코퍼스입니다. FM-VLA 는 그런 코퍼스가 **무엇에 쓰이는지**에 대한 첫 구체적 용례(범용 힘 잠재 공간 사전학습)를 제시하고, Limitations 에서 그것이 필요하다고 직접 요청합니다. D25 의 우선순위를 실행 가능한 과제로 바꿔 놓습니다.
- **vs MemoryVLA / MEM (핀 아님, 본 논문의 직접 경쟁자)** — 두 논문 모두 시각·언어 축 메모리이며, MEM 은 본 논문에서 $`\pi`$-MEM 으로 재구현되어 최강 baseline(53.7%)입니다. FM-VLA 의 주장은 이들을 대체한다는 것이 아니라 **관측 불가능한 사건에는 원리적으로 닿지 못한다**는 것으로, 두 메모리가 결합 가능한 상보재임을 시사합니다(결합 실험은 없음).

---

## ⚙️ 의사결정 함의

이 논문이 옳다면 우리 파이프라인에서 다음이 구체적으로 바뀝니다.

- **D11 에 시간 축 항목을 추가.** 현재 D11 v1 은 손가락별 공간 결합(10 finger + 2 palm 토큰)만 규정합니다. 여기에 **"접촉 이력 집약 토큰"** 을 별도 항목으로 세우고, 손가락 토큰이 매 스텝 관찰을 담당하는 동안 이력 토큰이 에피소드 요약을 담당하는 이중 구조를 검토해야 합니다. 구현 형태: 촉각/힘 시계열 → 사전학습 인코더 → `K` 개 memory token → 액션 전문가 suffix.
- **`K` 는 표현 용량이 아니라 base 토큰 예산으로 정한다.** FM-VLA 가 16·32 토큰에서 오히려 퇴행한 원인은 $`\pi_{0.5}`$ 액션 전문가가 학습 중 최대 50토큰만 봤다는 분포 이동입니다. 우리 스택은 Body/Hand 분리 헤드 + 손가락 토큰 12개가 이미 예산을 쓰므로, **접촉 메모리 토큰 예산을 정하기 전에 우리 base 체크포인트의 액션 전문가가 사전학습 중 실제로 본 최대 토큰 수를 먼저 측정**해야 합니다. 이는 하이퍼파라미터가 아니라 제약 조건입니다.
- **주입 위치는 noisy-action 토큰 뒤(post-position) + zero-init 사영.** D7(π 백본 통합) 의 실무 규약으로 채택 후보입니다. RoPE 위치 보존이라는 근거가 명확하고 비용이 0 이며, 앞에 prepend 한 TA-VLA 가 base 이하로 퇴행한 사실이 (통제 실험은 없지만) 방증입니다. 반대로 우리가 prepend 를 쓸 이유는 현재 없습니다.
- **전처리 3종을 접촉 이력 파이프라인의 기본값으로.** (i) 인과적 1차 EMA $`\alpha=0.3`$ — onset/peak 보존 조건, (ii) 데이터셋 전역 quantile 정규화($`q_{01}/q_{99}`$), (iii) **랜덤 노이즈 pre-padding**($`\sigma=0.05`$, 최대 1000 프레임, 추론 시 off). 특히 (iii)은 우리도 반드시 필요합니다 — 우리 과제 역시 시연 길이가 성공과 상관되므로 이력 길이 지름길이 그대로 발생합니다. 이 증강이 없으면 "메모리를 학습했다" 는 결과가 길이 세기의 착시일 수 있습니다.
- **표현 학습을 정책 학습에서 분리한다.** 접촉 인코더를 정책과 end-to-end 로 붙여 학습하지 말고, **재구성 목표로 먼저 사전학습 → 동결 → 사후분포 평균만 사용**하는 2단계를 기본 레시피로 둡니다. 손실식은 `L_VAE = masked_recon + β·mean(max(KL_per_dim, λ))`, 값은 `β=1e-3`, `λ=0.5` nats 를 출발점으로 삼습니다. free-bits 는 접촉처럼 희소한 사건에서 posterior collapse 를 막는 필수 항이지 선택 항이 아닙니다.
- **평가 프로토콜에 "제때 멈췄는가" 를 넣는다.** FM-VLA 의 성공 기준은 동작 완수 + 안정 종료(그리퍼 개방, ~3초 무동작)입니다. 우리 Phase 1 in-hand 회전 평가에도 목표 회전량 도달 후 **정지** 조건을 넣으면, 비-Markovian 능력을 별도 과제 없이 기존 과제 안에서 측정할 수 있습니다.
- **하지 말아야 할 것 — 힘 메모리 단독 조건화.** Force-only 가 Buttons 0.0% 로 memoryless base(11.1%)보다도 낮았습니다. 접촉 이력 토큰을 넣을 때는 반드시 단기 proprioception 윈도우를 함께 넣어야 하며, 이는 선택 항목이 아니라 안정성 조건입니다.

---

## ⚠️ 먼저 검증할 실패 모드

우리 스택(π 백본 + Body/Hand 분리 전문가 + 손가락 촉각 융합 + System0)으로의 전이 위험을, 가장 싼 점검부터.

1. **(가장 싼 점검) 우리 과제가 실제로 비-Markovian 인가.** FM-VLA 의 이득은 전부 "정답이 이력에 달린" 과제 설계에서 나옵니다. Phase 1 in-hand cube rotation 은 목표 회전량 도달 판정이 있으므로 비-Markovian 요소가 있지만, 회전각이 관찰에서 보인다면 Markovian 으로 충분할 수 있습니다. 점검: 기존 시연에서 (거의 동일한 관찰, 서로 다른 정답 행동) 쌍의 비율을 세어 비-Markovian 정도를 먼저 정량화. 이 비율이 낮으면 나머지 항목은 검토할 필요가 없습니다.
2. **손목 6축 → 손가락 다채널의 차원 폭발.** 본 논문의 입력은 $`d_{f}=6`$ 인 단일 스트림입니다. Sharpa Hand 는 지문당 ~320×240 Deform Map @30 Hz 로, 원시 차원이 4–5 자릿수 큽니다. 8토큰 96차원 병목이 그대로 옮겨질 리 없습니다. 점검: 손가락별 촉각을 먼저 저차원 접촉 특징(접촉 유무·법선력 추정·CoP)으로 줄인 뒤 그 시계열에 Force-VAE 를 적용하는 2단 압축이 성립하는지, 소량 데이터로 재구성 오차만 먼저 확인.
3. **토큰 예산 초과.** 우리 설계는 손가락 10 + 손바닥 2 토큰이 이미 관찰 쪽에 있고 Body/Hand 분리 헤드가 추가됩니다. 여기에 접촉 메모리 8토큰을 더하면 $`\pi_{0.5}`$ 급 base 의 50토큰 관측 이력을 넘길 수 있습니다. 점검: openpi 체크포인트 설정에서 액션 전문가의 사전학습 시퀀스 길이를 직접 읽어 남은 예산을 계산 — 코드 확인만으로 끝나는 점검입니다.
4. **VLM 미세조정 전제와 D19 freeze 의 충돌.** FM-VLA 는 VLM 인코더까지 함께 학습합니다. 우리 D19 v1 은 full VLM freeze 이므로, 메모리 토큰이 액션 전문가에만 들어가는 이 설계가 **백본 동결 상태에서도 같은 이득을 내는지**는 검증되지 않았습니다. 점검: 동결/미동결 두 조건에서 메모리 토큰 유무만 바꾸는 2×2 를 가장 작은 과제에서 먼저 돌립니다.
5. **에피소드 길이 스케일 차이.** 본 논문 과제는 수십 초 규모이고 접촉 사건이 최대 3회입니다. In-hand 회전은 접촉 사건이 초당 수 회 발생하는 **연속 접촉** 체제라, "사건을 센다" 는 잠재 구조가 아예 다른 통계를 만납니다. 점검: 우리 시연의 접촉 이벤트 밀도(초당 접촉 전이 횟수)를 세어 본 논문 체제와 자릿수를 비교.
6. **Force-VAE 의 도메인 특화.** 저자 스스로 3개 과제 시연으로만 학습했다고 인정합니다. 우리 과제로 옮길 때 인코더는 사실상 새로 학습해야 하며, 시연이 수백 개 규모면 100k step 사전학습이 과적합할 수 있습니다. 점검: RH20T 등 공개 F/T 코퍼스로 먼저 사전학습해 우리 데이터에서의 재구성 오차를 in-domain 학습본과 비교 — 코퍼스 전이 가능성을 정책 학습 전에 판정.
7. **왼손/다중 접촉원 누락.** 본 논문은 오른손목 하나만 씁니다. 양손 협응이나 손가락별 독립 접촉이 있는 우리 과제에서는 스트림이 여러 개이고, 이들을 한 VAE 에 concat 할지 스트림별 인코더를 둘지가 미결입니다. 점검: 다중 스트림을 채널 concat 한 단일 VAE 의 재구성 성능이 스트림별 VAE 대비 얼마나 나쁜지 오프라인 비교.
8. **결과의 통계적 견고성.** 과제당 18 시행, 시드 반복·신뢰구간 없음. 우리가 이 방법에 투자하기 전에 인용할 수치는 격차가 큰 것(Buttons 33.3 vs 72.2, Wipe 50.0 vs 77.8)에 한정하고, Q-Former vs VAE 의 중간 격차는 재현 근거로 삼지 않는 것이 안전합니다.
9. **코드 부재.** 공개 구현이 없어 세부(Perceiver-IO 구성, quantile 정규화 구현, 마스킹 처리)를 사양에서 복원해야 합니다. 점검: Appendix E 만으로 Force-VAE 를 재구현해 합성 임펄스 시계열의 접촉 횟수가 잠재에서 선형 분리되는지 확인 — 정책 없이 며칠 안에 끝나는 최소 재현 경로입니다.

---

## 💡 컨텍스트 제안

- **P2 Tracked Literature 등재 제안.** P2 핀은 현재 5편으로 cap 8 에 여유가 있습니다. FM-VLA 는 D11 에 **시간 축 접촉 토큰 구성**이라는 현재 핀 집합에 없는 축을, D9 에 "사전학습 모달 인코더 > from-scratch" 명제의 비전-외 독립 증거를 추가합니다. 핀 또는 methodology-base 등재를 사람이 검토할 것을 제안합니다.
- **D11 개정 후보 (제안만).** 현재 v1 은 공간 결합만 규정하고 시간 축이 비어 있습니다. "접촉 이력 집약(memory) 토큰" 을 v2 후보 항목으로 추가할지, 그리고 보조 감독을 현재의 contact-binary/slip-binary aux head 대신 **재구성 사전학습**으로 대체·병용할지가 판단 대상입니다.
- **D7 실무 규약 후보 (제안만).** "새 조건 스트림은 noisy-action 토큰 뒤에 붙이고 사영은 zero-init" 을 π 백본 통합의 기본 규약으로 명문화할지 검토를 제안합니다. 근거는 §3.2.3 의 RoPE 보존 논거이며, 반례 통제 실험이 논문에 없다는 점도 함께 기록되어야 합니다.
- **D25 우선순위 강화 근거.** 본 논문의 Limitations 는 대규모 F/T 코퍼스 사전학습을 명시적으로 요청합니다. D25 가 F/T 데이터 희소성을 first-class gap 으로 둔 판단을 뒷받침하는 외부 수요 신호로 기록할 만합니다.
- **Anti-topic 관점 확인.** 본 논문은 P0 §4 의 "데이터/벤치마크 미공개" 에 해당하나 P0 는 부 pillar 이며, 주 pillar P2 관점에서는 anti-topic 에 걸리지 않습니다(구조적 융합 기여 있음, 학습된 표현 있음).
- context/ 파일은 수정하지 않았습니다.

---

> 💡 base 매핑은 `/implement-design analysis/2607.18231/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
