# Paper Analysis — Being-H0.7: A Latent World-Action Model from Egocentric Videos

> PROBE analysis 모드 산출물. 단일 한글 문서이며, 영문 1차 파일은
> 없습니다. 형식·이모지·용어 규칙은 `docs/STYLE.md` §5 / §4 를
> 정확히 따릅니다. 재실행 시 이 파일을 덮어씁니다.

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Being-H0.7: A Latent World-Action Model from Egocentric Videos |
| 저자 | Hao Luo, Wanpeng Zhang, Yicheng Feng, Sipeng Zheng, Haiweng Xu, Chaoyi Xu, Ziheng Xi, Yuhui Fu, Zongqing Lu (BeingBeyond Team) |
| 링크 | [arXiv:2605.00078](https://arxiv.org/abs/2605.00078) |
| 발행일 / 버전 | 2026-04-30 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-05-27 |

---

## 🧭 한 줄 요약 (TL;DR)

미래 프레임을 생성하지 않고도 *미래 관측에서 뽑은 임베딩*과 *현재만 보는 latent query*를 같은 잠재 공간에서 정렬해 행동에 유용한 예측 구조를 심는 dual-branch VLA. 6개 시뮬레이션과 12개 실로봇 태스크에서 SOTA를 유지하면서 픽셀 예측의 학습·추론 비용은 떼버린 latent world-action model입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — VLA의 한 발 앞에 *세계가 어떻게 진행할지*에 대한 예측 신호를 주입하되, 비싼 비디오 생성·픽셀 롤아웃에 손대지 않으면서 단일 forward pass로 끝나는 정책을 만드는 것이 본 논문의 과제입니다.
- **기존 접근의 한계** — 표준 VLA는 sparse한 액션 감독에 시각 단서의 *shortcut*만 잡고 동역학·접촉·진행도를 표현하지 못하며 최근 world-action model 계열은 픽셀 비디오 생성을 끼워 training·inference 양쪽에 큰 비용을 얹습니다. 픽셀 미래는 행동과 약하게 연결돼 있어 텍스처·조명에 capacity가 새기 쉽습니다.
- **본 논문의 가설** — 행동에 유용한 미래 신호는 *픽셀이 아닌 latent 공간*에서 정렬돼야 충분하며 미래 정보는 *학습 시에만* 들어와도 추론 시 deployable한 prior branch가 그 효과를 그대로 옮겨받을 수 있다는 주장입니다.
- **왜 지금 중요한가** — 비디오 생성 기반 WAM이 강력한 prior 후보로 부상하는 한편 deployment latency가 발목을 잡고 있어, "pixel-free latent reasoning"이 두 진영의 약점을 동시에 풀 수 있는 가설이 됩니다. 동시에 Being-H0.5(핀 P4)·UniHand 2.0이 대규모 인간 ego 비디오 사전학습 인프라를 이미 깔아 둔 상태라 검증 시점이 도래했습니다.

---

## 🧩 핵심 기여

- **Latent world-action 프레임워크** — VLA의 perception–action 사이에 학습 가능한 latent query를 끼워 *명시적인* reasoning 공간을 만들고 그 위에서 future-aware 구조를 조직합니다.
- **Dual-branch joint alignment** — deployable한 prior branch와 *training-only* posterior branch를 짝지어, 미래 관측을 frozen ViT + Perceiver resampler로 압축한 임베딩을 latent query 자리에 끼워 prior와 hidden-state-wise로 정렬합니다.
- **효율적인 단일 시퀀스 구현** — Mixture-of-Transformers backbone에 두 branch를 하나의 시퀀스로 packing하고 dual-branch attention mask + identical positional ID로 backbone을 한 번만 돌리면서 두 reasoning 경로를 구조적으로 맞춥니다.
- **Anti-collapse 정규화** — norm regularizer와 spectral entropy 기반 rank regularizer로 정렬된 latent state의 magnitude shrinkage·directional collapse를 차단합니다.
- **실증** — LIBERO·LIBERO-plus·RoboCasa·GR1·CALVIN·RoboTwin 2.0 6종 sim에서 SOTA 또는 동등 성능 + Linkerbot O6 손이 달린 3종 실로봇 12 태스크에서 5개 능력 suite 전부 1위, UAC로 3–4 ms/step 구간 deployment 달성.

---

## 🔑 기술 키워드

- **Visual-Language-Action (VLA) model** — 시각·언어·로봇 관측을 받아 액션을 곧장 내뱉는 generalist 정책 패밀리. Being-H0.7는 VLA의 입출력 인터페이스는 그대로 두고 *중간 reasoning 공간*만 늘립니다.
- **World-Action Model (WAM)** — 미래 비디오 등 환경 진행을 명시적으로 모델링해 액션과 결합하는 라인. 본 논문은 픽셀 WAM의 비용을 떼고 *latent* WAM으로 갈아탑니다.
- **Latent reasoning queries** — 액션 청크 바로 앞에 박는 학습 가능한 $`Q\in\mathbb{R}^{K\times d}`$. context와 action 사이에서 task·interaction 정보를 흡수하는 "생각 슬롯"이라고 보면 됩니다.
- **Prior / Posterior branch** — prior는 현재 context만으로 latent를 추론하는 deploy용 경로, posterior는 학습 시 미래 관측 임베딩을 같은 자리에 꽂아 *암묵적 supervision*을 흘려 주는 학습 전용 경로입니다.
- **Joint alignment loss** — 두 branch의 정렬 대상 layer hidden state를 Frobenius norm으로 맞추는 손실. posterior가 본 미래를 prior가 *현재만으로* 흉내 내도록 잡아당깁니다.
- **Mixture-of-Transformers (MoT)** — 액션/상태는 Action Expert, 그 외 신호는 Understanding Expert로 분기시키는 두 expert 백본 구조. Being-H0.5에서 이어받은 패턴을 그대로 사용합니다.
- **Dual-branch attention mask** — 같은 시퀀스 안에서 prior·posterior 토큰이 서로의 latent 자리를 보지 못하도록 막는 마스킹. 두 branch는 alignment loss로만 연결됩니다.
- **Flow matching action head** — Gaussian noise에서 정답 액션까지의 속도장을 회귀하는 생성 모델. 디퓨전 대비 적은 적분 스텝으로 액션 청크를 만들어 청크-단위 추론 비용을 누릅니다.
- **V-JEPA2.1 / InternVL3.5 / Qwen3** — 시각 인코더(V-JEPA2.1), 언어·시각 understanding expert(InternVL3.5), action expert backbone(Qwen3) — Being-H0.7가 그대로 가져다 쓰는 외부 사전학습 모델 3종입니다.
- **Universal Async Chunking (UAC)** — Being-H0.5 도입 후 0.7에서 강화된 client-side scheduler. action 청크의 prefix는 잠그고 suffix만 갱신해 inference latency·jitter를 흡수합니다.

---

## 🔬 방법론

![Figure 1 — Being-H0.7 latent reasoning + latent WAM overview](https://arxiv.org/html/2605.00078/x1.png)

> "Figure 1: Latent reasoning and latent world-action model. Left: Learnable latent queries are inserted to form a latent reasoning space that progressively organizes intermediate hidden states and guides action generation through propagation. Right: Through joint alignment between the dual-branch design, the model learns to reason with future information at inference time, turning into a latent world-action model." (§3.1)
(한글 해설 — 좌측은 latent query를 끼워 만든 reasoning 공간이 layer를 따라 정보를 모으는 그림, 우측은 prior–posterior 두 branch가 같은 latent 자리에서 만나 alignment로 결합되는 학습 도식입니다.)

### 직관

논문이 본인 가설을 가장 단단하게 못 박는 문장은 다음 두 줄입니다.

> "future information should shape the policy's internal reasoning, but it need not be reconstructed as pixels." (§1)
(한글 해설 — 행동에 도움이 되는 미래는 *어떤 픽셀 그림*이 아니라 *어떤 결정에 쓰일 단서*다. 픽셀 수준 재구성을 떼고 latent 수준 정렬만으로 충분하다는 입장입니다.)

> "subsequent observations serve as privileged supervision during training, not as a deployment-time requirement." (§1)
(한글 해설 — RMA식 "특권 teacher" 어법을 그대로 빌려 와, 미래 관측을 학습 시점에만 보는 *teacher 신호*로 정의합니다. 추론 시 posterior는 통째로 들어내는 deployable 경계가 이 한 줄에 들어 있습니다.)

설계의 핵심은 두 분리입니다. (1) "미래를 본다"와 "미래를 픽셀로 그린다"를 분리해, 행동에 쓸 정보만 latent로 압축합니다. (2) "정보를 흘려주는 길"과 "추론 시 돌아가는 길"을 분리해, 추론 시 비용은 prior branch 단일 forward로 고정한다는 점입니다.

### 아키텍처

![Figure 2 — Being-H0.7 dual-branch MoT architecture](https://arxiv.org/html/2605.00078/x2.png)

> "Figure 2: Being-H0.7 Architecture. We pack the prior and posterior branches into a single MoT sequence with shared context, where the two branches are optimized simultaneously. The posterior branch replaces latent queries with future embeddings, and the two branches are coupled by hidden-state alignment and lightweight regularization. A dual-branch attention mask is applied to isolate prior and posterior branches while preserving access to the shared context for efficient training." (§3.3)
(한글 해설 — 두 branch가 같은 context 토큰을 공유한 채 한 MoT 시퀀스 안에 packed되어 있고, latent 자리에서만 분기 + alignment + 정규화로 묶이는 단일-forward 학습 구조를 한 장에 정리한 그림입니다.)

입력 시퀀스는 식 (1)로 정의됩니다.

$$S=\big[x;\,o_{-H:0};\,s;\,Q;\,a_{0:T}\big]$$

여기서 $`x`$ 는 instruction, $`o_{-H:0}`$ 는 horizon $`H`$ 의 관측 컨텍스트, $`s`$ 는 상태, $`Q\in\mathbb{R}^{K\times d}`$ 는 $`K`$ 개의 latent query, $`a_{0:T}`$ 는 길이 $`T`$ 의 액션 청크입니다(§3.1).

Posterior branch에서는 같은 latent 자리에 미래 관측 임베딩을 넣습니다.

$$z^{\mathrm{post}}=E(\tilde{o}_{0:T})\in\mathbb{R}^{K\times d}$$

$`E`$ 는 frozen ViT + Perceiver resampler로 구성된 temporal encoder이고, 출력 개수 $`K`$ 와 차원 $`d`$ 는 prior latent query와 정확히 매칭됩니다(§3.2).

MoT 백본은 Being-H0.5의 구조를 이어받아 *Action Expert + Understanding Expert*로 갈라집니다.

> "We adapt a Mixture-of-Transformers (MoT) structure like Being-H0.5, where action and state vectors are processed with a specific Action Expert and other signals are processed by a larger Understanding Expert." (§3.3)
(한글 해설 — 액션·상태 신호는 작은 Action Expert에, 명령·관측·언어는 큰 Understanding Expert에 흘려 두 expert의 capacity를 비대칭으로 잡습니다.)

두 branch를 한 시퀀스에 packing하는 정합 장치는 세 가지입니다. (i) context 토큰은 prior·posterior 모두에서 가시화하지만 두 branch의 latent 토큰은 서로 보지 못하도록 *dual-branch attention mask*를 씌웁니다. (ii) 대응하는 prior·posterior 토큰 위치에는 *동일한 positional ID*를 부여해 Transformer layer를 따라가도 두 자리가 구조적으로 맞물려 있게 합니다. 한편 coupling은 alignment loss로만 이뤄지고 cross-branch attention은 없습니다.

### 학습 목표 / 손실

미래 정보를 latent에 박아 넣는 핵심은 prior–posterior 정렬 손실입니다(식 (3)).

$$\mathcal{L}_{\mathrm{align}}=\frac{1}{L}\sum_{\ell=1}^{L}\frac{1}{|h_{\ell}|}\left\|h_{\ell}^{\mathrm{prior}}-h_{\ell}^{\mathrm{post}}\right\|_{F}^{2}$$

$`h_{\ell}^{\mathrm{prior}}`$ 와 $`h_{\ell}^{\mathrm{post}}`$ 는 정렬 대상 $`\ell`$ -번째 layer의 latent reasoning 자리 hidden state, $`L`$ 은 정렬 layer 수, $`\|\cdot\|_{F}`$ 는 Frobenius norm, $`|h_{\ell}|`$ 은 해당 layer hidden state의 스칼라 원소 수입니다(§3.2).

액션 생성에는 prior·posterior 양쪽에 flow matching loss를 답니다(식 (4)).

$$\mathcal{L}_{\mathrm{FM}}=\mathcal{L}_{\mathrm{FM}}^{\mathrm{prior}}+\mathcal{L}_{\mathrm{FM}}^{\mathrm{post}},\quad\text{where}\ \mathcal{L}_{\mathrm{FM}}^{\mathrm{prior}}=\left\|v_{\theta}^{\mathrm{prior}}(a_{t},c,q)-u_{t}\right\|_{2}^{2},\quad\mathcal{L}_{\mathrm{FM}}^{\mathrm{post}}=\left\|v_{\theta}^{\mathrm{post}}(a_{t},c,z^{\mathrm{post}})-u_{t}\right\|_{2}^{2}$$

여기서 $`a_{t}=ta+(1-t)\epsilon`$, $`u_{t}=a-\epsilon`$, $`t\in[0,1]`$, $`\epsilon\sim\mathcal{N}(0,I)`$, $`c=[x;\,o_{-H:0};\,s]`$ 는 두 branch가 공유하는 현재 컨텍스트, $`q`$ 는 학습 가능한 latent query, $`z^{\mathrm{post}}`$ 는 미래 임베딩입니다.

Latent collapse를 막기 위해 두 종류의 anti-collapse 정규화가 들어갑니다. Norm regularizer는 식 (5)와 같이 magnitude shrinkage를 차단합니다.

$$\mathcal{R}_{\mathrm{norm}}(h)=\left[\mathrm{ReLU}(\tau-\|h\|_{2})\right]^{2}$$

$`\tau`$ 는 사전 정의된 threshold입니다(§3.3).

Spectral diversity 항은 정렬된 latent state들을 random $`n`$ -차원 부분공간에 사영해 row-normalize한 $`\hat{H}`$, Gram matrix $`G=\hat{H}\hat{H}^{\top}`$ 의 고유값 $`\{\lambda_{i}\}_{i=1}^{M}`$, 정규화 spectrum $`p_{i}=\lambda_{i}/\sum_{j}\lambda_{j}`$ 로 정의됩니다(식 (6)).

$$\mathcal{R}_{\mathrm{rank}}(H)=\sum_{i=1}^{M}p_{i}\log p_{i}$$

이 *음의* spectral entropy를 최소화하면 spectrum이 평탄해져 directional collapse를 막습니다. 두 항을 합쳐(식 (7)) $`\mathcal{R}_{\mathrm{norm}}`$ 과 $`\mathcal{R}_{\mathrm{rank}}`$ 의 가중 합을 사용합니다.

$$\mathcal{L}_{\mathrm{reg}}=w_{\mathrm{norm}}\mathcal{R}_{\mathrm{norm}}+w_{\mathrm{rank}}\mathcal{R}_{\mathrm{rank}}$$

최종 목적은 식 (8)에서 세 항을 더한 형태입니다.

$$\mathcal{L}=\mathcal{L}_{\mathrm{FM}}+w_{\mathrm{align}}\mathcal{L}_{\mathrm{align}}+\mathcal{L}_{\mathrm{reg}}$$

### 학습 셋업

- **백본** — Being-H0.5 위에 InternVL3.5를 understanding expert, Qwen3를 action expert로 얹습니다. context·future 양쪽 시각 인코더는 V-JEPA2.1로 통일하되, context-frame encoder만 학습 가능 상태로 풉니다(§4.1).
- **관측 해상도** — context image 224×224, future frame 256×256(§4.1).
- **시간/토큰 차원** — observation horizon $`H=4`$, 액션 청크 길이 $`T=20`$, latent query 수 $`K=16`$. posterior 임베딩 개수도 16으로 일대일 매칭(§4.1).
- **정렬 layer 수** — 마지막 $`L=9`$ Transformer layer에 prior–posterior alignment를 적용(§4.1).
- **손실 가중** — $`w_{\mathrm{align}}=10^{-3}`$, $`w_{\mathrm{norm}}=w_{\mathrm{rank}}=10^{-4}`$ (§4.1).
- **데이터** — UniHand 2.0의 통합 시퀀스 포맷에 따른 *human + robot manipulation 혼합* 사전학습. 텍스트 생성 태스크와도 호환되는 포맷이지만 본 단계에서는 액션 생성에 집중(§3.3, §4.1).
- **Post-training** — task-specific demonstration 위에서 action loss + alignment loss만 켜고 anti-collapse 정규화는 끕니다. sequence packing으로 실효 global batch ≈ 128 trajectory chunk(§4.1).
- **추론** — posterior branch와 보조 인코더(미래 ViT + Perceiver)를 통째로 떼고 prior만 forward. 미래 프레임 생성·픽셀 롤아웃 없음(§3.2, §1).
- **Deployment** — Being-H0.5에서 가져온 latency-aware UAC를 prior branch 위에 그대로 얹어 client-side prefix-lock / suffix-update로 3–4 ms/step 구간을 확보(§4.3.3).

---

## 📊 실험 설정과 결과

평가는 6 시뮬레이션 벤치마크와 3 실로봇 플랫폼·12 태스크·5 능력 suite로 구성됩니다. sim 결과 핵심 수치는 다음과 같이 인용됩니다.

> "Across all six simulation benchmarks, Being-H0.7 achieves state-of-the-art overall performance, maintaining the highest average rank as detailed in Table 1." (§4.2.2)
(한글 해설 — LIBERO, LIBERO-plus, LIBERO-plus∗, RoboCasa-50, GR1, CALVIN, RoboTwin 2.0의 6 벤치마크 평균에서 1위라는 표 1 요약입니다.)

| 벤치마크 | Being-H0.7 (3B) | 직전 SOTA (모델·값) | 출처 |
|---|---|---|---|
| LIBERO | 99.2 | 98.9 (Being-H0.5, 2B) | §4.2.2, Table 1 |
| LIBERO-plus | 82.1 | 80.5 (ABot-M0, 4B) | §4.2.2, Table 1 |
| LIBERO-plus∗ (FT) | 84.8 | 84.1 (MINT-4B) | §4.2.2, Table 1 |
| RoboCasa-50 | 62.1 | 67.1 (Cosmos-Policy, 2B) | §4.2.2, Table 1 |
| GR1 | 49.2 | 58.3 (ABot-M0) | §4.2.2, Table 1 |
| CALVIN ABCD→D | 4.67 | 4.63 (UniVLA / Being-H0.5) | §4.2.2, Table 1 |
| CALVIN ABC→D | 4.48 | 4.48 (Being-H0.5) | §4.2.2, Table 1 |
| RoboTwin 2.0 Easy / Hard | 90.2 / 89.6 | 92.9 / 91.6 (LingBot-VA, 5B) | §4.2.2, Table 1 |

본문이 강조하는 *vector-level robustness* 와 *long-horizon* 결과는 다음 두 진술로 박힙니다.

> "On RoboTwin 2.0, Being-H0.7 demonstrates remarkable robustness in complex bimanual manipulation, sustaining an 89.6% success rate under severe visual domain randomization, with merely a 0.6% performance drop compared to the clean setting (90.2%)." (§4.2.2)
(한글 해설 — clean → 강도 높은 시각 도메인 랜덤화로 갈 때 단 0.6 % 포인트만 떨어지는 점이 latent reasoning이 *시각 변화에 무관한* 추론을 잡았다는 증거로 인용됩니다.)

> "Finally, on CALVIN, Being-H0.7 proves its capacity for multi-task long-horizon execution and zero-shot environment generalization, successfully completing an average of 4.67 and 4.48 tasks in a row (out of 5) on the ABCD $`\to`$ D and ABC $`\to`$ D splits, respectively." (§4.2.2)
(한글 해설 — 5개 연속 instruction 중 4.5개 이상을 끝까지 실행해 zero-shot 환경 D에서도 long-horizon 일관성을 유지함을 보고합니다.)

실로봇 평가는 PND Adam-U(19 body DoF + Linkerbot O6 양손, 총 31 DoF, 20 Hz), Unitree G1(14 arm + 12 hand = 26 DoF, 10 Hz), Franka FR3(7 arm + 6 hand = 13 DoF, 20 Hz) 3 플랫폼에서 진행됩니다(§4.3.1, Table 2). 12개 태스크는 dynamic scene / physical reasoning / motion reasoning / long-horizon / generalization 5개 능력 suite로 분류되며 각 태스크 20 blind trial로 정책 endpoint를 가린 채 success-rate를 측정합니다(§4.3.2).

![Figure 5 — Real-world suite-level success rates](https://arxiv.org/html/2605.00078/x5.png)

> "Figure 5: Suite-level real-robot success rates (%). Comparison of Being-H0.7, Being-H0.5, $`\pi`$ 0.5, and Fast-WAM on the five ability-oriented task suites. Each task is evaluated over 20 blind trials, and each suite score is averaged over all tasks carrying the corresponding suite tag." (§4.3.3)
(한글 해설 — 5개 능력 suite 모두에서 Being-H0.7이 다른 베이스라인 3종을 앞선다는 본문 핵심 그림으로, "한 코너에 몰린 우위가 아니라 전 영역 우위"라는 §4.3.3 결론의 근거입니다.)

본문은 능력별로 다음과 같이 결과를 정리합니다.

> "The clearest margin appears on Dynamic Scene, and the same ordering largely carries over to Motion Reasoning. These suites contain the most timing-sensitive tasks in the benchmark, including catching a fast rolling ball, racket-based redirection, pouring into a moving receptacle, and conveyor-based interaction." (§4.3.3)
(한글 해설 — 시간 민감 태스크가 모인 dynamic / motion suite에서 격차가 가장 크다는 진술입니다. Fast-WAM이 baseline 중 가장 강한 라인인데 Being-H0.7가 그보다 더 앞선다는 비교가 같은 문단에 따라옵니다.)

> "Being-H0.7 stays ahead on both suites, showing that the learned world-action prior supports fast reaction and also maintains causal consistency through longer and more physically constrained manipulation chains." (§4.3.3)
(한글 해설 — physical / long-horizon suite에서도 Being-H0.5가 가장 가까운 baseline이며 Being-H0.7이 일관되게 우위를 유지한다는 점을 못 박습니다.)

Inference cost 측면에서 핵심 진술은 다음과 같습니다.

> "The most visible effect is that the UAC-enabled Being-H variants move into the 3–4 ms/step regime while keeping the same GPU memory footprint as their non-UAC counterparts." (§4.3.3)
(한글 해설 — UAC 적용으로 step당 3–4 ms 구간에 진입하면서 GPU 메모리는 그대로라는 점, 즉 latent reasoning을 더해도 deployment cost는 늘지 않는다는 시스템 레벨 결론입니다.)

Latent reasoning 자체의 시각화는 다음과 같이 정성적으로 검증됩니다.

> "Although Being-H0.7 does not explicitly reconstruct future frames during inference, the resulting visualizations in Figure 6 suggest that its latent representations already capture predictive information about how the world will evolve." (§4.3.3)
(한글 해설 — prior branch의 hidden state + 현재 관측을 외부 video generation model에 조건으로 넣었을 때 그럴듯한 미래가 나오는 정성 결과로, "픽셀을 직접 그리지 않아도 latent에 미래 정보가 들었다"는 정성 증거입니다.)

---

## ⚖️ 한계

- **시뮬에서 SOTA를 *전부* 잡지는 않습니다** — RoboCasa(67.1 % Cosmos-Policy vs 62.1 % Being-H0.7), GR1(58.3 % ABot-M0 vs 49.2 %), RoboTwin Easy/Hard(92.9/91.6 LingBot-VA vs 90.2/89.6)에서는 다른 모델이 앞섭니다(Table 1). 평균 1위지만 *모든 벤치마크에서의* 1위는 아닙니다.
- **Latent collapse 위험을 정규화로 가립니다** — alignment loss만으로는 trivial 해(zero state 등)가 가능하다고 저자도 인정하고 norm·rank 정규화를 도입합니다(§3.3). 두 가중치가 어떻게 결정됐는지 ablation 없이 단일 값($`10^{-4}`$)으로 제시됩니다.
- **Posterior 인코더가 frozen ViT + Perceiver resampler에 묶여 있습니다** — 미래 임베딩 품질이 V-JEPA2.1 사전학습에 의존하며 ViT를 학습 가능 상태로 풀거나 다른 인코더로 바꿀 때 alignment loss 곡선이 어떻게 변하는지에 대한 분석은 본문에 없습니다.
- **태스크별 ablation이 비어 있습니다** — $`K=16`$, $`L=9`$, $`H=4`$, $`T=20`$ 의 선택 근거가 제시되지 않고 정확한 값을 사용한 단일 셋업만 보고됩니다(§4.1).
- **실로봇 비교군이 좁습니다** — Figure 5는 Being-H0.5, π0.5, Fast-WAM 세 baseline만 비교하며 sim에서 Table 1에 등장한 다수 baseline(MINT, ABot-M0, LingBot-VA 등)은 실로봇 결과 비교 대상에서 빠집니다.
- **저자가 자기 한계로 언급하는 부분은 본문에 명시 없음** — Conclusion 단락(§5)은 약점을 열거하지 않습니다. 위 항목은 본문 수치·설계 결정에서 도출한 *명백한 갭*입니다.

---

## ♻️ 재현성

- **프로젝트 페이지** — `https://research.beingbeyond.com/being-h07` (§서두 `\webpage` 매크로).
- **코드/체크포인트 공개 여부** — 본문에 명시 없음. Being-H0.5(arXiv:2601.12993) 라인이 자체 채널을 가지므로 후속 공개 가능성은 있으나 본 논문은 공개 일정·라이선스를 언급하지 않습니다.
- **데이터** — 사전학습 데이터는 *UniHand 2.0* 의 통합 포맷(Being-H0.5 인용)입니다 — 약 35k h × 30 embodiment, 400M+ 샘플 / 120B 토큰(P4 §8.4 핀 참조). 후처리(post-training) 단계는 *task-specific demonstration*만 사용한다고 명시(§4.1).
- **하드웨어** — PND Adam-U / Unitree G1 + AMO whole-body controller / Franka FR3 + Linkerbot O6 hand 6-DoF(상용 가용). Unitree G1에서는 별도 AMO controller가 50 Hz body-loop을 잡고 hand는 정책이 직접 제어합니다(§4.3.1).
- **외부 의존 모델** — InternVL3.5(understanding), Qwen3(action), V-JEPA2.1(시각). 모두 외부 사전학습 가중치이며 다운로드 경로는 본문에 명시 없음.
- **컴퓨트 / 학습 시간** — 정확한 GPU 시간·노드 수·총 step 수는 본문에 명시 없음.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P1 (Heterogeneous Body/Hand Action Expert)** — Being-H0.7의 MoT는 *Understanding Expert + Action Expert* 비대칭 분할이고 PROBE의 *Body/Hand* 분할과는 *축이 다른* 분리입니다. 즉 직접 매핑되지는 않지만 (i) 큰 backbone + 작은 action expert + 정렬 가능한 reasoning 자리라는 *구조 패턴* 자체가 D1(split form) v1 hybrid의 합리성을 뒷받침합니다. (ii) D7(π backbone 통합) 의사결정에서, π0 대신 *최근 open-weight 백본(InternVL3.5 + Qwen3)* 위에서 MoT를 굴리는 lineage 예시로 인용 가능합니다.
- **P2 (Structured Input-Modality Binding)** — 본 논문은 입력 모달리티 결합이 P2의 *손가락 단위 구조적 토큰*과 결이 다르지만 latent query 자리에 *별도의 의미 슬롯*을 박는 패턴은 D8/D10이 토큰 시퀀스를 만든 뒤에도 "토큰 옆에 reasoning 슬롯을 둘 것인가"라는 보조 질문을 새로 던집니다. v1을 흔들 정도는 아닙니다.
- **P3 (Hand-level System0 RL)** — 무관. Being-H0.7은 RL을 한 줄도 쓰지 않고 imitation + flow matching으로 끝납니다. 다만 *dynamic scene / motion reasoning suite*에서 reactive 성공률이 latent reasoning만으로 끌어올려졌다는 §4.3.3 결과는 PROBE D14(System1/System0 인터페이스) 토론에서 "RL 없이 latent reasoning만으로 reactive 성능이 어디까지 가는가"라는 antagonist 데이터 포인트로 인용 가능합니다.
- **P4 (VLM Pretraining Preservation)** — *직접 관련도가 가장 높은 핀 영역*입니다. (i) **D19b (VLM lineage)** — InternVL3.5 + Qwen3 + V-JEPA2.1 조합은 §8.4의 PaliGemma·Eagle-2·Qwen3-VL 라인업과 나란히 놓을 lineage 후보입니다. (ii) **D20 (prior-preservation strategy)** — frozen ViT를 posterior 인코더로만 쓰고 context 인코더는 trainable로 두는 *비대칭 freeze* 패턴이 등장합니다. 또한 **D22 (multi-embodiment pretraining data)** 측면에서 UniHand 2.0이 그대로 본 논문의 사전학습 데이터셋이며 Being-H0.5와 데이터·포맷을 공유한다. 마지막으로 **D23 (action representation)** 에서 flow matching head v1 선택을 다시 한 번 보강(prior·posterior 양쪽 모두 flow matching).
- **P5 (Task Definition & Falsifiable Evaluation)** — Grouped Blind Ensemble 평가 패턴이 직접 적용됩니다.

  > "We deploy all compared policies through a unified black-box inference server. This protocol keeps the surrounding execution stack identical across methods. For each task, we pre-define a set of scene layouts and initial conditions, then randomize both the tested policy endpoint and the rollout order during evaluation. The operator records task success using a fixed binary criterion defined for that task while the active policy endpoint remains hidden." (§4.3.2)
  (한글 해설 — D26 v1의 *operator-blinding* 프로토콜과 거의 같은 정의로, PROBE 실로봇 평가 설계 시 직접 인용 가능한 외부 사례입니다.)

- **Identity 긴장/지지** — Identity의 *VLA-level 직접 손대기* 입장과 정합합니다. correction module이 아니라 *backbone 안에 reasoning 자리*를 새로 박는다는 점이 antagonist A(correction module 분포 종속)와 결을 같이합니다.
- **§10 경쟁자 함의** — Being 라인(0.5 핀, 0.7 후속)이 *VLM·VLA-only*만으로 6 sim에서 SOTA·12 실로봇에서 5/5 suite 1위를 가져간다는 점은 §10.1 Genesis AI 라인과 같은 antagonist evidence입니다. *RL 없이도 reactive·long-horizon이 다 잡힌다*는 강한 주장이며, System0 필요성 진영의 *반대편* 데이터 포인트로 모니터링 가치가 큽니다.

---

## ✨ 핀 논문 대비 델타

- **vs. Being-H0.5 ([arXiv:2601.12993](https://arxiv.org/abs/2601.12993))** — P4 핀. 0.5는 *cross-embodiment 통합 시퀀스 포맷(UniHand 2.0) + MoT* 으로 cross-embodiment 사전학습을 정립했고 0.7는 그 위에 *latent reasoning + dual-branch joint alignment* 라는 한 층을 새로 올립니다. 측정 가능한 새로움은 LIBERO 98.9 → 99.2, LIBERO-plus 78.5 → 82.1, RoboCasa-50 53.5 → 62.1, GR1 (—)→49.2, RoboTwin Easy/Hard (—)→90.2/89.6입니다. 추론 비용은 같은 UAC 위에서 3–4 ms/step으로 유지(§4.3.3). 0.5는 핀 유지 가능, 0.7는 *후속*으로 §8.4 후보지만 0.5와 동일 라인이라 핀 교체는 부적절합니다(§13 quarterly 재밸런스에서 다룰 항목).
- **vs. π0 / π0.5 ([arXiv:2410.24164](https://arxiv.org/abs/2410.24164) · [arXiv:2504.16054](https://arxiv.org/abs/2504.16054))** — π 계열은 flow matching head를 정립한 backbone 핀. Being-H0.7도 flow matching action expert를 그대로 쓰지만 (i) backbone을 PaliGemma → InternVL3.5 + Qwen3로 갈아탔고, (ii) action expert 앞에 *명시적 latent reasoning 자리* 를 끼웠습니다. π0.5의 *hierarchical inference* 는 high-level → low-level decomposition이고, Being-H0.7의 prior–posterior는 *현재 vs 미래 정보 access* decomposition이라는 점에서 직교합니다.
- **vs. MolmoAct2 ([arXiv:2605.02881](https://arxiv.org/abs/2605.02881))** — P4 핀. MolmoAct2는 *per-layer KV-cache* 로 VLM을 보존합니다. Being-H0.7은 *latent query 자리에 미래 임베딩을 끼워* VLM을 우회적으로 활용합니다. 두 접근 모두 "VLM을 깨지 않고 새 supervision을 흘려 보낸다"는 동일 목표를 다른 길로 풉니다. 묶어서 D20 prior-preservation 후보 비교 시 함께 인용할 가치.
- **vs. 다른 World-Action 핀 후보들 (DreamZero, Cosmos-Policy, LingBot-VA, Fast-WAM — Table 1 인용 [12,13,14,15])** — 모두 *픽셀 미래* 라인. Being-H0.7는 같은 RoboCasa·RoboTwin에서 Cosmos-Policy(67.1 → 62.1)·LingBot-VA(92.9 → 90.2)에 사실은 *밀리는 항목*이 있지만 *5/5 suite 1위 + 3–4 ms/step* 라는 *시스템 레벨 우위* 로 결론을 가져갑니다. PROBE 관점에서 핀 후보가 아닌 *antagonist comparison* 라인.
- **vs. TwinBrainVLA ([arXiv:2601.14133](https://arxiv.org/abs/2601.14133))** — P1 핀(AsyMoT frozen generalist + trainable specialist). Being-H0.7도 MoT라는 expert 분할을 갖지만 *frozen vs trainable 비대칭* 보다는 *capacity 비대칭* 이 강조됩니다. AsyMoT가 *어떤 expert를 얼린다*는 결정인 반면, Being-H0.7은 *어떤 자리에 reasoning slot을 박는다*는 결정이라 직접 비교가 어렵습니다.

핀 교체 의제는 없습니다. **0.5 핀 유지 + 0.7는 동일 라인의 후속 메모로 §8.4 옆 자리에 트래킹**, 그리고 §10 §10.1(antagonist evidence) 모니터링 라인에 *Being 0.x → 0.7 진행 속도* 를 한 줄 추가하는 정도가 적절합니다.

---

## ⚙️ 의사결정 함의

- **D7 (π backbone 통합)** — Being-H0.7은 π 백본 *없이* InternVL3.5 + Qwen3 + V-JEPA2.1 위에서 MoT를 굴립니다. PROBE의 v1(슬라이스 + FT) 결정을 흔들 정도는 아니지만 §14.B의 *π 변종 / 코드베이스 선택* 항목에서 "open-weight 백본 + MoT 라인"을 alternative branch로 메모할 가치가 있습니다. CP1 코드 진입에서 §14.C A/B 둘 다 막힐 때 *Being-H0.7-style open-weight stack*이 백업 path로 등록됩니다.
- **D19b (VLM lineage)** — InternVL3.5(understanding) + Qwen3(action) + V-JEPA2.1(시각) 3-요소 lineage가 새로운 데이터 포인트입니다. §8.4 lineage 표에 *cross-pollination 형태*로 추가 검토 — 핀 교체 후보는 아니지만 lineage-attributable 진단 시 비교 후보 풀에 들어옵니다.
- **D20 (prior-preservation strategy)** — *비대칭 freeze* 패턴(context encoder trainable, future encoder frozen)이 새로운 후보입니다. 본 논문 자체는 "prior preservation" 어휘를 쓰지 않지만 frozen ViT가 posterior 쪽에서만 평가되는 구조는 *VLM 가중치 보존이 필요한 시점에 deployable branch와 supervision branch를 분리*하는 일반 패턴으로 확장 가능합니다. v1(action-side adapter) 결정 자체는 유지하되, D19 trigger 발화 시 비교 후보로 등록.
- **D23 (action representation)** — flow matching head v1 결정을 *VLM 백본이 다른* lineage(InternVL3.5/Qwen3)에서도 강하게 보강합니다. prior·posterior 두 branch가 모두 flow matching인 점은 *flow matching head가 supervision 강도에 robust*하다는 외부 증거입니다. 차원별 가중·timestep 분포 등 구체 키 변경은 없습니다.
- **D26 (evaluation protocol)** — *unified black-box inference server + endpoint randomization + 20 blind trial / task* 가 그대로 D26 v1의 Grouped Blind Ensemble 정의와 들어맞습니다. PROBE 실로봇 평가 진입 시 본 논문의 §4.3.2 프로토콜을 *외부 비교 인용*으로 그대로 차용 가능합니다. 코드/스펙 인용 메모로 D26 deferred 항목에 등록.
- **D14 (System1↔System0 인터페이스)** — Being-H0.7의 UAC(client-side prefix-lock / suffix-update)는 PROBE의 *System1 청크 출력 + System0 sub-loop* 구조와 직접 닮은 deployment 패턴입니다. D14 v1(binary on/off bypass) 결정 자체는 유지하되, *deployment 단의 prefix-lock 디자인*은 D14의 *후속 deployment layer*로 메모할 가치가 있습니다.
- **새 후보 항목: latent reasoning slot** — D8/D10이 만든 토큰 시퀀스에 *별도의 reasoning slot*을 박을지 여부가 새로운 design 질문으로 추가됩니다. 본 논문이 보고하는 dynamic / motion suite 우위는 *현재 컨텍스트로부터 미래 단서를 latent에 모은다*는 메커니즘 효과로 해석되며 PROBE의 in-hand reorientation에서도 동일한 *short-horizon 미래 reasoning* 자리가 필요할 가능성이 있습니다. 단, v1 후보에 올리려면 ablation이 더 필요합니다(본 논문에는 $`K`$, $`L`$ ablation 없음).

종합하면 본 논문은 **P4 lineage·deployment 패턴·D26 평가 프로토콜**의 세 영역에서 PROBE의 *defaults*에 직접 데이터 포인트를 추가합니다. P1 anatomical 분리와 P3 System0 RL 진영을 흔들지는 않으며 오히려 *RL 없이 latent reasoning만으로 reactive·long-horizon이 어디까지 가는가*라는 antagonist 데이터로 §10 모니터링 자리에 박힙니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **Latent collapse가 정규화로만 가려졌을 가능성** — $`\mathcal{R}_{\mathrm{norm}}`$ / $`\mathcal{R}_{\mathrm{rank}}`$ 의 ablation은 본문에 없습니다. PROBE에 latent reasoning slot을 도입할 때, 정규화 ON/OFF · $`w_{\mathrm{norm}}/w_{\mathrm{rank}}`$ 스윕으로 collapse 여부와 *liberalized alignment loss curve*가 어떻게 흘러가는지 먼저 측정해야 합니다. 가장 싼 sanity check — 동일 데이터에서 $`Q`$ 차원 $`K`$ 를 4·8·16·32로 바꿔 alignment loss와 task success가 *flat band*를 보이는지 확인.
- **Posterior 인코더(V-JEPA2.1) 의존도** — frozen ViT + Perceiver resampler가 미래 임베딩을 만들고 이 임베딩의 *분포*가 prior가 학습해야 할 *teacher signal*입니다. ViT를 다른 인코더로 바꿨을 때 alignment loss curve가 무너진다면, latent WAM의 효과는 V-JEPA2.1의 pretraining에 *bound*된 것일 수 있습니다. 가장 싼 sanity check — 사전 ablation에서 future encoder를 (a) V-JEPA2.1, (b) frozen CLIP, (c) trainable scratch ViT로 바꿔 prior branch 성능 격차를 측정.
- **MoT capacity 분할이 우리 데이터 규모에서 작동할지** — InternVL3.5 (큰 understanding expert) + Qwen3 (작은 action expert)는 *대규모 사전학습 + 대규모 robot mix*를 전제로 합니다. PROBE의 v1 sim ablation 규모(태스크당 50~1000 trial)에서는 큰 understanding expert가 *underconstrained*해 overfit할 위험이 있습니다. 가장 싼 sanity check — 첫 ablation은 *동일 backbone*에서 latent reasoning slot ON/OFF로만 비교, expert capacity 자체는 변수에서 분리.
- **Future embedding의 temporal horizon이 PROBE 태스크와 안 맞을 가능성** — 본 논문은 $`H=4`$ obs + $`T=20`$ action chunk를 미래 horizon으로 잡고 이 구간의 ViT 임베딩을 posterior 입력으로 씁니다. *in-hand reorientation*은 의미 있는 *미래 변화*가 손가락 micro-motion 수준에서 일어나므로, 20-step 미래 frame이 *contact event*를 담을 만큼 충분히 시간 해상도를 잡지 못할 수 있습니다. 가장 싼 sanity check — sim에서 *contact event 시점*을 라벨로 잡아 ViT 임베딩이 정말 그 시점을 *separable* 하게 표현하는지 t-SNE/probing으로 확인.
- **prior branch가 deployable해도 *training cost*는 두 배 가까이 든다** — 한 시퀀스에 두 branch를 packing해 단일 forward를 쓰지만 시퀀스 길이 자체는 2배($`K`$ extra) + alignment 대상 layer가 last $`L=9`$라서 backward 비용이 늘어납니다. 본 논문은 step time 보고가 deployment에 집중되어 있고 *training step time*은 명시 없음. PROBE에 도입할 때 사전 학습 시 GPU 시간 견적이 부풀 가능성이 있어, *training-time cost monitoring*을 D21 stage 정의에 미리 메모해 두는 것이 안전합니다.
- **System0 자리에 들어갈 RL 신호와의 호환성** — Being-H0.7의 prior branch는 *flow matching*으로 액션을 만들고 추론 시 단일 청크를 내뱉습니다. PROBE의 System0이 사이에 끼어들면 (i) latent reasoning이 만든 *current context only* 추론이 sub-loop RL 액션과 *충돌*할 수 있고, (ii) UAC의 prefix-lock 규약이 System0의 *실시간 finger override*와 부딪힐 수 있습니다. 가장 싼 sanity check — UAC client schema에 *partial prefix override*가 가능한지(논문은 "never rewrites the already committed prefix"라고 못 박음, §4.3.3) 미리 확인.

---

## 💡 컨텍스트 제안

- **§8.4 (P4 Pinned)** — 현재 Being-H0.5가 핀입니다. Being-H0.7은 *동일 라인의 후속* 이라 핀 교체는 부적절하지만 §8.4 표 아래에 "**0.7 = 0.5 + latent reasoning slot + dual-branch alignment**"라는 한 줄 메모를 D19b lineage 추적용으로 추가 검토할 만합니다(quarterly rebalance 후보).
- **§10.1 (VLA-only strong performers / antagonist evidence)** — Genesis AI 라인과 별도로, "**Being-Beyond 라인 (Being-H0 → 0.5 → 0.7)**"을 *RL 없이 latent reasoning만으로 reactive·long-horizon을 잡는 antagonist evidence*로 한 줄 추가 검토. *Watch trigger* — "0.7 후속에서 in-hand reorientation 같은 dexterous *finger-level* 태스크로 확장될 때" — 이 시점에서 P3 System0 필요성 진영이 직접 시험됩니다.
- **§14.B (Implementation Feasibility Unclarities)** — *코드베이스 선택* 항목에서 "open-weight VLM (InternVL/Qwen 계열) + MoT" 라인을 π 백본의 alternative branch로 메모 추가 검토. 본 논문이 *PaliGemma 외 lineage*에서도 SOTA 결과가 가능함을 보여 줍니다.
- **D14 deferred 항목** — 현재 D14 v1은 *binary on/off bypass*. Being-H0.7의 UAC가 *deployment layer*의 prefix-lock / suffix-update 패턴을 정립했으므로, "System1 청크 출력의 prefix-lock + System0 sub-loop가 한 buffer에 공존하는 schema" 검토를 D14 deferred 항목 아래에 한 줄 메모 추가 — *Trigger*: 실로봇 진입 시 System1↔System0 timing jitter가 측정 가능해질 때.
- **D26 deferred 항목** — Being-H0.7 §4.3.2의 *unified black-box inference server + endpoint randomization + 20 blind trial / task* 프로토콜을 PROBE 실로봇 평가 직접 인용 후보로 D26 메모에 추가.

context/MASTER.md는 절대 수정하지 않습니다. 위 항목은 사람이 검토할 후보 제안입니다.

> 💡 base 매핑은 `/implement analysis/2605.00078/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
