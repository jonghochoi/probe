# Paper Analysis — FLARE: Robot Learning with Implicit World Modeling

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | FLARE: Robot Learning with Implicit World Modeling |
| 저자 | Ruijie Zheng, Jing Wang, Scott Reed, Johan Bjorck, Yu Fang, Fengyuan Hu, Joel Jang, Kaushil Kundalia, Zongyu Lin, Loic Magne, Avnish Narayan, You Liang Tan, Guanzhi Wang, Qi Wang, Jiannan Xiang, Yinzhen Xu, Seonghyeon Ye, Jan Kautz, Furong Huang, Yuke Zhu, Linxi Fan (NVIDIA GEAR 외) |
| 링크 | [arXiv:2505.15659](https://arxiv.org/abs/2505.15659) · [Website](https://research.nvidia.com/labs/gear/flare) |
| 발행일 / 버전 | 2025-05-21 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-25 |
| 관련 Pillar | P5, P4, P1 |
| 태그 | vla-arch, flow-matching, egocentric-data |

---

## 🧭 한 줄 요약 (TL;DR)

미래 프레임을 생성하지 않고도, 액션 디노이징 DiT에 학습 가능한 *future token* 몇 개를 끼워 그 은닉 상태를 미래 관측의 잠재 임베딩과 코사인 정렬하는 것만으로 *암묵적 세계 모델*을 심는 경량 VLA 확장입니다. 단일 팔·휴머노이드 멀티태스크 imitation 벤치마크 두 종에서 SOTA(베이스라인 대비 최대 26%↑)를 찍고, 액션 라벨 없는 인간 ego 비디오와의 co-training으로 단 한 개의 로봇 demo만으로 신규 물체 일반화를 끌어올립니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — VLA 정책이 액션을 내놓을 때 "다음에 세계가 어떻게 진행될지"라는 예측 구조를 함께 학습시키되, 고비용 비디오 생성을 끼우지 않고 표준 VLA 구조와 완전 호환되는 가벼운 레시피로 이를 달성하는 것이 본 논문의 과제입니다.
- **기존 접근의 한계** — 미래 *비주얼 프레임*을 액션과 함께 생성하는 최근 world-model 계열은 고화질 예측에 대형 생성 모델이 필요해 연산·지연을 키우고, 픽셀 재구성과 액션 예측이 모델 capacity를 두고 경쟁해 학습 효율을 희석합니다.
- **본 논문의 가설** — 행동에 유용한 미래 신호는 *픽셀이 아니라 compact latent 공간*에서 정렬돼도 충분하며, 그 정렬을 액션 디노이징 망의 은닉 상태에 직접 걸면 정책이 미래를 *암묵적으로* 추론하면서 액션을 생성한다는 가설입니다.
- **왜 지금 중요한가** — flow-matching VLA(π0 / GR00T N1)가 표준 backbone으로 자리 잡고 REPA식 표현 정렬이 diffusion 수렴을 가속하는 것이 입증된 시점이라, "REPA를 *미래*·*정책*으로 옮긴다"는 단순 조합이 픽셀 WM의 비용 없이 그 이점을 흡수할 수 있는 검증 시점이 도래했습니다.

---

## 🧩 핵심 기여

- **Future Latent Representation Alignment(FLARE)** — diffusion / flow-matching 정책에 latent-space world modeling을 future-alignment 목표로 주입하되 full-frame reconstruction을 제거한 경량 확장. 액션 디노이징 망의 은닉 상태에서 미래 관측의 compact 표현을 예측합니다.
- **최소 구조 변경** — 표준 VLA 시퀀스에 학습 가능한 *future token* 몇 개만 추가하면 되어, π0 / GR00T N1 같은 기존 아키텍처에 그대로 얹을 수 있습니다.
- **Action-aware future embedding model** — SigLIP2 인코더 + Q-former로 관측을 32 토큰으로 압축하되 *액션 flow-matching으로 end-to-end 학습*해, 미래 예측 타깃이 행동 관련 정보만 담도록 한 별도 사전학습 컴포넌트.
- **멀티태스크 SOTA** — RoboCasa(24 태스크, 단일 팔) + GR-1(24 태스크, 휴머노이드) 두 벤치마크에서 prior policy learning 대비 최대 26% 우위, 실 GR-1에서 최대 95.1% 성공률.
- **액션-프리 인간 비디오 활용** — 액션 라벨이 없는 GoPro ego 비디오에는 alignment loss만 걸어 co-train, 신규 기하의 물체에 대해 단일 로봇 demo만으로 일반화를 크게 끌어올립니다.

---

## 🔑 기술 키워드

- **Future Latent Representation Alignment (FLARE)** — 미래 관측의 잠재 임베딩과 액션 디노이징 망의 은닉 상태를 정렬해, 픽셀을 그리지 않고도 정책에 "다음에 무슨 일이 벌어질지"를 심는 핵심 학습 목표.
- **Implicit world modeling** — 미래 프레임을 명시적으로 생성(reconstruction)하지 않고, 행동에 유용한 정보만 latent 정렬로 흡수하는 세계 모델링 방식.
- **Representation Alignment (REPA)** — text-to-image diffusion의 수렴을 가속하려 DiT 내부 표현을 외부 인코더 표현과 정렬하던 기법. FLARE는 이를 *현재*가 아닌 *미래* 관측으로, 이미지가 아닌 *정책*으로 옮깁니다.
- **Diffusion Transformer (DiT) policy** — flow-matching으로 액션 청크를 생성하는 트랜스포머 정책. self-attention + cross-attention 교차 구조의 GR00T N1 형식을 그대로 토대로 씁니다.
- **Flow matching** — Gaussian noise에서 정답 액션까지의 속도장을 회귀하는 생성 모델. $`K=4`$ 스텝 forward Euler 적분으로 청크를 생성합니다.
- **Learnable future tokens** — 입력 시퀀스에 추가하는 $`M`$ 개의 학습 토큰. self-attention으로 액션 스트림과 상호작용하며 미래 임베딩을 예측하는 별도 스트림을 형성합니다.
- **Action-aware embedding model** — SigLIP2 + Q-former로 관측을 32 토큰으로 압축하되 액션 flow-matching으로 end-to-end 학습해, "행동 관련 정보만" 담은 미래 예측 타깃을 만드는 모델.
- **Q-former** — 학습 query 토큰으로 가변 길이 토큰열을 고정 크기로 압축하는 모듈. 멀티카메라 입력에 자연스럽게 일반화됩니다.
- **EMA target update** — 미래 예측 타깃 임베딩 모델을 정책 인코더의 지수이동평균으로 천천히 따라가게 해, 사전학습-다운스트림 분포 이동을 흡수하면서 타깃 안정성을 확보 ($`\rho=0.995`$).
- **Action-free co-training** — 액션 라벨 없는 인간 ego 비디오에는 alignment loss만 걸어 latent dynamics를 학습하고, 소수 로봇 demo로 신규 물체에 일반화하는 학습 방식.

---

## 🔬 방법론

![Figure 1 — FLARE vs 표준 flow-matching 정책 비교](https://arxiv.org/html/2505.15659/x1.png)

> "Figure 1: Comparison of FLARE to a conventional flow-matching (or diffusion) policy. FLARE can train using both action flow-matching and future latent alignment objectives, leading to improved performance as well as enabling learning from video-only data such as human ego-view demonstrations." (§1)
(한글 해설 — 표준 정책은 action flow-matching 한 길로만 학습하는 반면, FLARE는 future latent alignment 한 길을 병렬로 더해 성능을 올리고, 액션이 없는 인간 ego 비디오까지 학습 신호로 끌어들일 수 있음을 한 장에 대비한 그림입니다.)

### 직관

FLARE의 가설은 두 문장에 박혀 있습니다.

> "At its core, FLARE predicts a compact representation of the robot's future observation from the hidden states of the action denoising network." (§1)
(한글 해설 — 핵심은 "미래를 픽셀로 그린다"가 아니라 "미래 관측을 *작은 임베딩으로* 예측한다"이며, 그 예측을 별도 모듈이 아니라 *액션을 디노이징하는 바로 그 망의 은닉 상태*에서 뽑아낸다는 점입니다. 세계 모델과 정책이 같은 망을 공유하는 셈입니다.)

> "We introduce Future LAtent REpresentation Alignment (FLARE), a lightweight yet highly effective extension to diffusion or flow-matching policies that introduces latent-space world modeling via a future alignment objective, eliminating the need for full-frame reconstruction." (§1)
(한글 해설 — full-frame reconstruction을 떼는 것이 설계의 정수입니다. 픽셀 재구성을 빼면 (i) 대형 생성 모델·추론 지연이 사라지고 (ii) 디테일·텍스처에 capacity가 새지 않아 행동에 필요한 추상 표현만 남습니다.)

설계는 두 단계로 나뉩니다. 먼저 *action-aware한 관측 임베딩 모델*을 사전학습해 미래 예측의 타깃을 만듭니다. 그다음 액션 디노이징 DiT에 *future token* 몇 개를 추가해, 그 토큰의 중간 layer 활성을 미래 관측 임베딩과 정렬하도록 co-train합니다. 기존 VLA 구조에 토큰 몇 개를 더하는 것이 전부라 적용이 쉽고, 액션 라벨이 없는 데이터(인간 비디오)에서도 정렬 손실만 따로 켤 수 있어 활용 폭이 넓습니다.

### 아키텍처

![Figure 2 — FLARE 아키텍처](https://arxiv.org/html/2505.15659/x2.png)

> "Figure 2: FLARE architecture. State and action token embeddings are concatenated into a sequence with learnable future token embeddings. The flow matching DiT blocks perform self-attention on this sequence, and cross-attention to the current vision and text observation embeddings. At a middle layer, the activations corresponding to the future token embeddings are used to compute a future latent alignment loss, which is the cosine similarity with vision-language embeddings from a future observation." (§3)
(한글 해설 — state·action 토큰과 future 토큰을 한 시퀀스로 묶어 DiT가 self-attention으로 처리하고, 현재 관측 임베딩에는 cross-attention으로 조건을 답니다. 중간 layer에서 future 토큰 자리의 활성만 슬라이스해 미래 관측 임베딩과 코사인 유사도로 맞추는 것이 핵심 도식입니다.)

입력 시퀀스는 세 구성요소로 이뤄집니다.

> "To enable the latent representation within the DiT blocks to predict future latent states, we add $`M`$ learnable future token embeddings to the input sequence, such that the sequence contains three components: (1) the current proprioceptive state $`q_{t}`$ encoded via a state encoder, (2) noised action chunk $`A_{t}^{\tau}=\{\tau a_{t}+(1-\tau)\epsilon\}_{t}^{t+H}`$ encoded by an action encoder, and (3) a set of $`M`$ learnable future tokens." (§3.1)
(한글 해설 — proprioception $`q_{t}`$, 노이즈가 섞인 액션 청크 $`A_{t}^{\tau}`$, 그리고 $`M`$ 개의 future token이 한 시퀀스를 이룹니다. future token은 액션 스트림과 *self-attention으로만* 상호작용하는 별도 흐름입니다.)

미래 정렬은 중간 layer에서 일어납니다.

> "Next, we slice out the intermediate DiT representations corresponding to the $`M`$ future tokens at an internal layer $`L`$, project those features using an MLP, and finally align these with the frozen vision-language embeddings of the future observation $`\phi_{t+H}`$." (§3.1)
(한글 해설 — layer $`L`$ 에서 future token 자리의 활성을 잘라 MLP로 사영한 뒤, *frozen* 미래 관측 임베딩 $`\phi_{t+H}`$ 과 정렬합니다. 미래 관측은 액션 청크 끝 시점 $`t+H`$ 의 관측이고, 타깃 임베딩은 학습 중 gradient가 흐르지 않습니다.)

REPA와의 차이가 본 논문의 정체성을 가릅니다.

> "Our approach is similar to how Representation Alignment (REPA) [11] is applied to improve text-to-image diffusion models, but with several important differences arising from the setting of latent world modeling. First, we align a DiT policy with future embeddings, rather than embeddings of the current observation. Second, our architecture adds learnable future tokens, so that the flow matching and alignment proceed along separate streams within the DiT, which interact via self-attention." (§3.1)
(한글 해설 — REPA는 이미지 diffusion DiT의 *현재* 표현을 외부 인코더 표현과 정렬했지만, FLARE는 (i) *미래* 임베딩과 정렬하고 (ii) flow-matching 스트림과 alignment 스트림을 *분리된 두 흐름*으로 두어 self-attention으로만 섞습니다. 이 분리가 "액션 예측 능력을 유지하면서 내부적으로 미래를 추론"하게 하는 장치입니다.)

### 학습 목표 / 손실

배경이 되는 flow-matching부터 정리합니다(§2). 관측 $`o_{t}`$ 의 vision-language 임베딩을 $`\phi_{t}=VL(o_{t})`$ 로, proprioception을 $`q_{t}`$, 전문가 액션 청크를 $`A_{t}=(a_{t},\dots,a_{t+H})`$ 로 둡니다. flow-matching timestep $`\tau\in[0,1]`$ 과 노이즈 $`\epsilon\sim\mathcal{N}(\mathbf{0},\mathbf{I})`$ 로 노이즈 섞인 청크를 만듭니다.

$$A_{t}^{\tau}=\tau A_{t}+(1-\tau)\epsilon$$

모델 예측 $`V_{\theta}(\phi_{t},A_{t}^{\tau},q_{t})`$ 은 디노이징 방향 $`\epsilon-A_{t}`$ 을 근사하도록 다음 손실로 학습됩니다(식 1).

$$\mathcal{L}_{\textit{fm}}(\theta)=\mathbb{E}_{\tau}\left[\|V_{\theta}(\phi_{t},A_{t}^{\tau},q_{t})-(\epsilon-A_{t})\|^{2}\right]$$

timestep은 $`p(\tau)=\text{Beta}\left(\frac{s-\tau}{s};1.5,1\right)`$ ($`s=0.999`$, Black et al.)에서 샘플링하고, 추론 시에는 $`A_{t}^{0}\sim\mathcal{N}(\mathbf{0},\mathbf{I})`$ 에서 시작해 $`K`$ 스텝 forward Euler로 정제합니다.

$$A_{t}^{\tau+1/K}=A_{t}^{\tau}+\frac{1}{K}V_{\theta}(\phi_{t},A_{t}^{\tau},q_{t})$$

GR00T N1을 따라 $`K=4`$ 로 고정합니다. FLARE가 더하는 핵심은 future latent alignment 목표입니다(식 2). $`B`$ 는 batch, $`D`$ 는 임베딩 차원입니다.

$$\mathcal{L}_{\textit{align}}(\theta)=-\mathbb{E}_{\tau}\left[cos(f_{\theta}(\phi_{t},A_{t}^{\tau},q_{t}),g(\phi_{t+H})\right]$$

여기서 $`f_{\theta}\rightarrow\mathbb{R}^{B\times M\times D}`$ 은 layer $`L`$ 의 $`M`$ 개 future token 활성을, $`g\rightarrow\mathbb{R}^{B\times M\times D}`$ 은 미래 관측 $`\phi_{t+H}`$ 의 인코더 출력을 냅니다. 즉 미래 token 활성과 미래 관측 임베딩의 *코사인 유사도를 최대화*(음수 부호로 최소화)합니다. 전체 손실은 두 항의 가중 합입니다(식 3).

$$\mathcal{L}=\mathcal{L}_{fm}+\lambda\mathcal{L}_{align}$$

> "Empirically, we found $`\lambda=0.2`$ worked the best in our experiments." (§3.1)
(한글 해설 — alignment 항 가중 $`\lambda=0.2`$ 가 최적. §4.4 ablation에서 layer 인덱스·계수 robustness를 함께 분석합니다.)

### 학습 셋업

![Figure 3 — action-aware 임베딩 모델의 데이터 mixture](https://arxiv.org/html/2505.15659/x3.png)

> "Figure 3: Data mixture of pretrained action-aware vision language embedding model" (§3.2)
(한글 해설 — 미래 예측 타깃이 되는 action-aware 임베딩 모델을 GR00T N1 + 7종 Open X-Embodiment 데이터로 cross-embodiment 사전학습함을 요약한 그림입니다.)

- **Action-aware 임베딩 모델 (§3.2, Appendix A)** — SigLIP2(`siglip2-large-patch16-256`)의 vision·text 인코더로 `256×256` 이미지를 256 patch token, 명령을 32 language token으로 인코딩 → 4-layer self-attention으로 288 fused token 생성 → Q-former로 $`M=32`$ query token으로 압축. action-awareness를 위해 8개 DiT 블록을 붙여 액션 flow-matching으로 end-to-end 학습합니다.

  > "To ensure action-awareness, we train the vision language embedding end-to-end with the regular action flow-matching objective to predict the robot's actions by attaching 8 DiT blocks." (§3.2)
  (한글 해설 — 일반 목적 임베딩이 아니라 *액션을 실제로 예측하도록* 학습해, latent token에 task 관련 정보가 반드시 담기게 한 것이 핵심 설계입니다.)

- **사전학습 코퍼스 (Appendix B, Table 3)** — GR-1 in-house(real, 88.4 h) + GR-1 simulation(1,742.6 h) + DROID·RT-1·Language Table·Bridge-v2·MUTEX·Plex·RoboSet(OXE 7종). 본문은 "approximately 2,000 hours"로 표기하나 Table 3 합계는 169.5M frame · 2,989.5 h입니다.
- **옵티마이저 (Appendix C)** — 임베딩 사전학습: 256×H100, batch 8192, 150k step, AdamW($`\beta_{1}=0.95,\beta_{2}=0.999,\epsilon=\text{1e-8}`$), weight decay 1e-5, cosine schedule(warmup ratio 0.05). 멀티태스크 FLARE: 32×H100, batch 1024, 80k step(나머지 동일).

**EMA 타깃 갱신 (§3.2, §4.4).** 사전학습-다운스트림 분포 이동을 흡수하기 위해 타깃 임베딩 모델을 완전 frozen 두지 않고 정책 인코더의 EMA로 갱신합니다.

$$\theta_{\text{target\_vl\_embedding}}\leftarrow\rho\theta_{\text{target\_embedding}}+(1-\rho)\theta_{\text{policy\_vl\_embedding}}$$

$`\rho\in\{0.99,0.995,0.999,1.0\}`$ 중 $`\rho=0.995`$ 가 최적입니다.

---

## 📊 실험 설정과 결과

평가는 RoboCasa(24 단일 팔 태스크) + GR-1 tabletop(24 휴머노이드 태스크) 두 멀티태스크 시뮬레이션 + 실 GR-1 휴머노이드로 구성됩니다. §4.1에서는 *공정 비교를 위해 사전학습 임베딩을 쓰지 않고* in-domain multitask 데이터로만 임베딩을 80k step 학습합니다.

> "First, FLARE consistently outperforms all baseline methods, including both the policy-only baselines and UWM." (§4.1, Table 1)
(한글 해설 — Diffusion Policy·UWM·GR00T N1(Scratch)·정책-only 모두를 일관되게 상회. 특히 픽셀-latent 생성형 baseline인 UWM 대비 우위가 핵심입니다.)

| Task group | FLARE | Policy Only | UWM | GR00T N1 (Scratch) | Diffusion Policy |
|---|---|---|---|---|---|
| RoboCasa — Pick and Place | 53.2% | 43.8% | 35.6% | 44.1% | 29.2% |
| RoboCasa — Open & Close Doors / Drawers | 88.8% | 78.7% | 82.0% | 80.0% | 78.7% |
| RoboCasa — Others | 80.0% | 75.2% | 74.2% | 69.6% | 61.3% |
| **24 RoboCasa Tasks Average** | **70.1%** | 61.9% | 60.8% | 60.6% | 51.7% |
| GR1 — Pick and Place | 58.2% | 46.6% | 30.1% | 51.8% | 40.4% |
| GR1 — Articulated | 51.3% | 47.4% | 38.4% | 42.8% | 50.1% |
| **24 GR1 Tasks Average** | **55.0%** | 44.0% | 29.5% | 45.1% | 40.9% |

(출처: §4.1, Table 1. UWM은 80k step에서 성능이 아직 상승 중이라 다른 방법의 5배인 400k step까지 학습한 결과입니다. 각 체크포인트는 태스크당 50 episode 평가, 최종 5 체크포인트 중 최댓값을 보고.)

GR1 평균 기준 FLARE 55.0% vs UWM 29.5%로, 초록의 "up to 26%" 우위는 이 구간에 해당합니다. 또한 *정책-only로 160k step* 학습해도 44.1%에 머물러(80k와 차이 없음), 향상이 단순 추가 학습 step의 산물이 아님을 명시합니다.

> "Second, even when trained with only the policy objective, FLARE still achieves performance on par with GR00T N1 initialized from scratch, despite GR00T N1 using a larger VLM backbone." (§4.1)
(한글 해설 — Q-former 기반 임베딩이 더 작은 backbone으로도 GR00T N1(Scratch)과 동급 성능을 내, 임베딩 자체의 action-relevant 정보 포착력을 방증합니다.)

**데이터 효율 post-training (§4.2, Figure 6).** §3.2의 cross-embodiment 사전학습 임베딩을 *미래 예측 타깃*으로만 쓰고(FLARE는 vision-language 임베딩만 warm-start), unseen 임바디먼트/태스크에서 데이터-제한 post-train합니다.

> "Notably, although the pretrained embedding model has never seen RoboCasa tasks during pretraining, using it as the future embedding achieves comparable performance with 1000 trajectories to an embedding model trained exclusively on the 24 RoboCasa arm tasks (71.3% vs. 70.2% as reported in Section 4.1)." (§4.2)
(한글 해설 — RoboCasa를 *한 번도 못 본* cross-embodiment 임베딩이 in-domain 임베딩과 동급(71.3% vs 70.2%)이라, 미래 타깃이 도메인-전이된다는 강한 증거입니다. 100 trajectory/task의 데이터-제한 조건에서는 RoboCasa에서 10% 향상.)

> "On the real GR-1 humanoid robot, we achieve a success rate of up to 95.1%, averaging 14% higher than the baseline method." (§4.2)
(한글 해설 — 실 GR-1 4 태스크(apple·can·bottled water·cucumber, 태스크당 8 reference 초기 프레임)에서 최대 95.1%, baseline 대비 평균 14%p 우위. 정성적으로는 손 근처에 놓인 캔/물병을 baseline은 쳐서 넘어뜨리는 반면 FLARE는 우회·상회 후 파지합니다.)

**액션-프리 인간 ego 비디오 (§4.3, Figure 7).** 신규 기하 물체 5종에 대해, 물체당 GoPro 인간 ego demo 150개 + 로봇 teleop demo 소수를 혼합해 학습합니다.

> "For real-robot demonstrations with actions, we apply both the action flow-matching loss and the future alignment objective. In contrast, for the human egocentric videos without action labels, we rely solely on the future alignment loss to learn the latent dynamics." (§4.3)
(한글 해설 — 핵심 분리. 액션이 있는 로봇 demo는 FM+align 둘 다, 액션이 *없는* 인간 비디오는 align만 켭니다. alignment 손실이 액션을 요구하지 않으므로 라벨 없는 비디오가 자연스럽게 학습 신호가 됩니다.)

> "When provided with 10 trajectories per object, and jointly trained with human videos, FLARE further improves to an 80% success rate—roughly doubling the performance of a baseline trained solely on action-labeled data." (§4.3)
(한글 해설 — 물체당 로봇 trajectory 1개만으로도 최대 60%, 10개 + 인간 비디오 co-train 시 80%로 *액션-only baseline의 약 2배*. 파지엔 성공·바구니 적재 실패 시 부분 점수 0.5를 부여한 채점입니다.)

**Ablation (§4.4).** 타깃 임베딩 모델 선택(GR1 벤치마크):

| Method | Success Rate (%) |
|---|---|
| No FLARE loss | 43.9 |
| SigLIP2 | 49.6 |
| SigLIP2 (Average Pooled) | 50.9 |
| Action-aware Embedding | 55.0 |

(출처: §4.4, Table 2. 범용 SigLIP2 타깃(timestep $`t+16`$, raw 256 token 또는 2×2 average-pool 64 token)도 baseline 대비 7% 향상하나, 도메인 특화 action-aware 임베딩이 최적입니다. FLARE 프레임워크가 teacher 인코더에 robust함을 보여 줍니다.)

> "However, we do notice that applying the alignment objective too early—e.g., at layer 4—leads to a notable drop in performance, highlighting the importance of aligning the future prediction objective with the action denoising process." (§4.4)
(한글 해설 — alignment를 8개 layer 중 6번째에 거는 것이 기본. 너무 이른 layer 4는 성능을 떨어뜨립니다. EMA는 $`\rho=0.995`$ 가 최적, $`\rho=0.99`$ 가 최악(잦은 타깃 갱신 불안정), $`\rho=1.0`$ (EMA 없음)도 baseline은 상회합니다.)

---

## ⚖️ 한계

- **저자 자술 한계 — pick-and-place·imitation에 국한** — 본문(§6)이 직접 인정하듯, 실 휴머노이드 실험은 pick-and-place에 머물고 더 fine-grained한 dexterous 조작과 RL 통합은 미래 과제로 남깁니다. 즉 *손가락 단위 접촉 정밀도*가 요구되는 태스크에서 future-latent 신호가 유효할지는 미검증입니다.
- **신규 물체 일반화도 소수 expert demo 의존** — 같은 §6에서, 신규 물체 일반화가 여전히 소량의 expert demo를 필요로 해, demo 수집이 어려운 세팅에서는 확장성이 제한된다고 밝힙니다.
- **통제된 GoPro ego 비디오만** — 인간 ego 데이터가 head-mounted GoPro로 *통제된 환경*에서 수집됩니다(§6). in-the-wild 대규모 ego 모션으로의 확장은 미래 과제이며, 현재 결과의 도메인 갭은 robot 관측과 가까운 통제 ego에 한정됩니다.
- **타깃이 holistic VL 임베딩이라 접촉 정보 분리성 불명** — 미래 예측 타깃이 *프레임 전체*의 vision-language 임베딩($`\phi_{t+H}`$)입니다. 이는 텍스처·전역 장면에는 강하나, 손가락 micro-motion·접촉 이벤트 같은 국소 동역학이 임베딩 차원에 *separable*하게 담기는지는 본문이 검증하지 않습니다(추론된 갭).
- **Collapse 방지 장치 부재** — alignment이 *frozen(EMA) 타깃*과의 코사인 유사도라, 표현 collapse 가능성이 구조적으로 존재합니다. Being-H0.7류가 도입한 norm/rank anti-collapse 정규화가 FLARE에는 없으며, token 수 $`M`$ 을 키울 때의 collapse 거동은 보고되지 않습니다(추론된 갭).
- **공정성 통제의 비대칭** — UWM만 5배(400k) step을 받았고 나머지는 80k입니다(§4.1). 저자는 UWM이 80k에서 미수렴이라 보정했다고 설명하나, 학습-예산 정규화 방식이 방법마다 다른 점은 비교의 잡음 요인으로 남습니다.

---

## ♻️ 재현성

- **코드 / 체크포인트** — 본문은 project webpage / blogpost(`https://research.nvidia.com/labs/gear/flare`)만 명시하고, 코드·가중치 공개 일정·라이선스는 언급하지 않습니다(NVIDIA GEAR).
- **데이터** — 임베딩 사전학습은 GR00T N1 humanoid(real GR-1 88.4 h + simulation 1,742.6 h) + OXE 7종(DROID·RT-1·Language Table·Bridge-v2·MUTEX·Plex·RoboSet), Table 3 합계 169.5M frame·2,989.5 h(본문 표기 "approximately 2,000 hours"). 인간 ego: 물체당 GoPro 150 demo, 5 신규 물체. 평가 벤치마크 RoboCasa·GR-1 tabletop은 GR00T N1 인용.
- **하드웨어 / 컴퓨트** — 임베딩 사전학습 256×H100(batch 8192, 150k step), 멀티태스크 FLARE 32×H100(batch 1024, 80k step). 실 평가는 GR-1 휴머노이드 로봇.
- **하이퍼파라미터** — $`M=32`$ future/query token, alignment layer $`L=6/8`$, $`\lambda=0.2`$, EMA $`\rho=0.995`$, 디노이징 $`K=4`$. AdamW($`\beta_{1}=0.95,\beta_{2}=0.999`$), weight decay 1e-5, cosine schedule(warmup 0.05).
- **의사코드** — Appendix D에 FLARE 학습 루프 Python-style pseudocode 제공(action_loss = MSE(action_outputs, velocity), flare_loss = 1 − cosine_similarity(predict_embedding, embedding_to_align), loss = action_loss + lambda·flare_loss).

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P5(World Model) — primary.** FLARE는 P5의 핵심 베팅을 그대로 구현하는 외부 사례입니다.
  - **D28(world-model 역할 — latent dynamics prior + future-prediction auxiliary co-trained)** — FLARE는 standalone planner가 아니라 정책과 *co-train되는 future-prediction auxiliary*입니다. D28 v1과 정확히 일치하는 instantiation입니다.
  - **D29(통합 아키텍처 — 공유 backbone 위 auxiliary head)** — future token + alignment head를 *같은 DiT* 에 끼우는 단일-backbone 구조라, D29 v1의 "auxiliary head on shared VLA backbone"을 직접 지지합니다. WorldVLA식 unified autoregressive 경로(D29 alternative)와 대비되는 데이터 포인트입니다.
  - **D30(예측 공간 — latent over raw-pixel)** — full-frame reconstruction을 명시적으로 제거하고 latent VL 임베딩과 정렬해, "픽셀보다 latent" v1을 강하게 보강합니다. 단, FLARE의 타깃은 *holistic VL 임베딩*이지 P2/DynaFLIP식 3D-flow가 아니라는 점에서 D30의 *3D-flow* 가지와는 결이 다릅니다.
  - **D31(action conditioning)** — future token이 액션 디노이징 DiT 안에서 noised action과 self-attention으로 섞이므로 예측이 *action-aware*합니다. 다만 per-frame 명시적 action conditioning(LOME/DexWM류)보다는 *암묵적* conditioning입니다.
  - **D32(egocentric hand-object WM)** — 액션-프리 인간 ego 비디오를 alignment-only로 co-train해 human ego → policy를 직접 연결, in-house ego 취득 계획(P0(데이터 스카우팅)/P4)과 정합합니다.
- **P4(데이터 효율 적응을 위한 사전학습) — 강한 secondary.**
  - **D19(VLM lineage + adaptation range)** — GR00T N1 / Eagle VLM lineage 위에서 SigLIP2 + Q-former action-aware 임베딩을 cross-embodiment 사전학습. P4 §5(Tracked Literature) / `catalogs/models.md` lineage 후보 풀에 추가할 데이터 포인트입니다.
  - **D20(prior-preservation 전략)** — *EMA 타깃*($`\rho=0.995`$)으로 예측 타깃을 천천히 따라가게 하는 패턴은, action-side adapter / ConSFT와 *다른 축*의 preservation 후보입니다(타깃 임베딩의 안정성 보존).
  - **D21(staged recipe)** — Stage 1 cross-embodiment 임베딩 사전학습 → Stage 2 정책 + latent WM + action loss co-train(임베딩 warm-start)의 2단계 레시피.
  - **D22(데이터 구성 — egocentric vs mixed) — OPEN** — OXE + GR-1 sim/real + 인간 ego 혼합. 액션-프리 ego co-training은 D22의 *egocentric-centric* 베팅에 직접 증거를 더합니다.
  - **D23(action representation)** — flow-matching head($`K=4`$, Beta timestep)로 v1을 보강.
- **P1(Heterogeneous Body/Hand Action Expert) — 비교군.** FLARE는 *단일 homogeneous* flow-matching DiT(GR00T N1 구조)로, PROBE의 Body/Hand 분할과 *반대* 축입니다. 따라서 D1(split form)에서는 monolithic 비교군이지만, "학습 토큰을 별도 스트림으로 추가하고 self-attention으로 섞는" 패턴 자체는 D4(Body↔Hand 정보 공유)·D7(backbone 통합/분할) 설계 시 참조 가치가 있습니다.
- **P2(Structured Multimodal Observation Fusion) — 약한 비교군.** Q-former가 멀티카메라 입력을 32 토큰으로 *flat*하게 압축("naturally generalizes to multi-camera inputs")하나, geometry-grounded가 아니므로 D8(multi-camera spatial-geometric grounding) 관점에서는 antagonist에 가깝습니다.
- **P3(System0 RL) — 무관.** RL을 쓰지 않고 imitation + flow-matching으로 종결합니다(§6에서 RL 통합을 미래 과제로 명시).
- **Identity 긴장/지지** — Identity의 "(VLA-level에서 직접 tackle)" + "(4) VLM 사전학습 recipe를 통한 data-efficient adaptation" + P5 world-model 베팅과 정합합니다. 다만 anatomically heterogeneous Body/Hand 분할(P1)은 *없는* monolithic 구조라, 그 축에서는 비교군입니다.
- **경쟁자 함의** — NVIDIA GEAR(GR00T lineage). FLARE의 future-latent alignment은 이후 Being-H0.7(P5 핀)의 dual-branch joint alignment로 일반화된 *직계 선행 연구*라, P5 핀 라인의 계보 추적에서 출발점으로 모니터링 가치가 큽니다.

---

## ✨ 핀 논문 대비 델타

- **vs. Being-H0.7([arXiv:2605.00078](https://arxiv.org/abs/2605.00078), P5 핀)** — *직접 계보 관계*입니다. FLARE(2025-05)는 future token 활성을 layer 6에서 미래 VL 임베딩과 *코사인* 정렬하는 단일 스트림 + EMA 타깃입니다. Being-H0.7(2026-04)은 이를 *prior/posterior 이중 branch* + 마지막 $`L=9`$ layer Frobenius 정렬 + norm/rank anti-collapse 정규화로 일반화합니다. 진정한 새로움(Being-H0.7 입장)은 "단일 future-token 정렬 → dual-branch + multi-layer + collapse 방지"이고, 역으로 FLARE는 *더 단순·이른* instantiation입니다. PROBE 관점에서 둘은 같은 latent-alignment 가족의 *최소 형태(FLARE)*와 *완성 형태(Being-H0.7)* 양 끝점입니다.
- **vs. VLA-JEPA([arXiv:2602.10098](https://arxiv.org/abs/2602.10098), P5 핀)** — VLA-JEPA는 JEPA latent WM을 *두 단계*(JEPA 사전학습 → action head fine-tune)로 분리하고 masked latent 예측을 self-supervise합니다. FLARE는 *단일 단계 co-train*이며 타깃이 *action-aware하게 학습된* VL 임베딩이라, "타깃을 어떻게 만드는가"(self-supervised masked vs action-supervised)에서 직교합니다.
- **vs. WorldVLA([arXiv:2506.21539](https://arxiv.org/abs/2506.21539), P5 핀)** — WorldVLA는 action·image 상호 예측의 *unified autoregressive* VLA+WM(D29 alternative)입니다. FLARE는 생성을 *명시적으로 회피*하는 implicit latent auxiliary(D29 v1)로, 두 핀이 D29의 양대 경로를 각각 대표합니다.
- **vs. GR00T N1([arXiv:2503.14734](https://arxiv.org/abs/2503.14734), P4 핀)** — FLARE는 GR00T N1의 flow-matching DiT 위에 alignment 목표를 *덧붙인* 형태입니다. 정책-only FLARE가 GR00T N1(Scratch)과 동급(§4.1)이고, alignment를 켜면 그 위로 향상이 쌓입니다. 즉 FLARE = GR00T N1 backbone + future-latent auxiliary.
- **vs. UWM(본 논문 main baseline, [4])** — UWM은 미래 프레임의 VAE latent와 액션을 diffusion으로 *함께 생성*합니다. FLARE는 같은 RoboCasa/GR1에서 UWM을 일관되게 상회(GR1 55.0% vs 29.5%)하며, "픽셀-latent 생성 vs latent 정렬"의 직접 head-to-head 승리입니다. PROBE D30(pixel vs latent) 결정의 핵심 증거.

핀 교체 의제는 없습니다. FLARE는 *P5 핀 라인(Being-H0.7 / VLA-JEPA)의 선행 연구*로서 P5 §5 methodology-base(비핀)에 추가 검토할 가치가 있으며, UWM 대비 latent-over-pixel 승리는 D30 메모에 인용 후보입니다.

---

## ⚙️ 의사결정 함의

- **D28 / D29 / D30(world-model 역할·통합·예측 공간)** — FLARE는 v1 기본값에 직접 증거를 더합니다. 구체 레시피: 액션 DiT 시퀀스에 $`M=32`$ future token 추가 → layer $`L=6/8`$ 활성 슬라이스 → MLP 사영 → frozen 미래 VL 임베딩과 코사인 정렬 → $`\mathcal{L}=\mathcal{L}_{fm}+0.2\,\mathcal{L}_{align}`$. 픽셀 생성형 UWM 대비 최대 ~26% 우위가 "latent over pixel"(D30 v1)의 정량 근거입니다.
- **D20(prior-preservation)** — 새 후보 패턴: *EMA 타깃 임베딩*(정책 인코더의 지수이동평균). PROBE에서는 "deploy fine-tuning 중 인코더가 drift할 때 미래-예측 타깃을 어떻게 안정화할 것인가"에 매핑됩니다. 구체 키: EMA $`\rho`$ — ablation에서 $`\rho=0.99`$(너무 빠름)이 최악, $`\rho=1.0`$(frozen)도 baseline 상회, $`\rho=0.995`$ 최적.
- **D22(데이터 구성 — egocentric vs mixed)** — *액션-프리 ego co-training* 레시피가 명확합니다: 로봇 demo에는 FM+align, 인간 ego 비디오에는 align-only. 이는 egocentric-centric 코퍼스 베팅(D22 open ablation)에 "라벨 없는 ego가 alignment만으로 일반화를 끌어올린다"는 실증을 더합니다.
- **D23(action representation)** — flow-matching head + $`K=4`$ 디노이징 + Beta($`\frac{s-\tau}{s};1.5,1`$) timestep이 v1을 재확인합니다. 구체 변경 키는 없습니다.
- **D9(action/dynamics-aware vision encoder, P2 인접)** — action-aware 임베딩을 *미래 예측 타깃*으로 쓴다는 발상은, P2의 action-aware encoder 선택을 "다운스트림 액션으로 supervise된 임베딩"으로 좁히는 한 갈래를 제시합니다(단, 본 논문은 geometry-grounded가 아님).

종합하면 FLARE는 **P5(D28–D30 latent-auxiliary 경로)**, **P4(D20 EMA preservation·D22 ego co-train)** 두 영역에서 PROBE defaults에 정량 데이터 포인트를 더합니다. P1 anatomical 분할과 P3 System0 RL 진영은 흔들지 않으며, monolithic DiT라는 점에서 P1 비교군으로 박힙니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **미래 타깃이 손가락-접촉 동역학을 분리하지 못할 위험** — FLARE의 타깃은 시점 $`t+H`$ 의 *holistic VL 임베딩*입니다. in-hand reorientation처럼 의미 있는 미래가 손가락 micro-motion·접촉 이벤트 수준에서 일어나는 태스크에서는, SigLIP2류 프레임 임베딩이 그 국소 변화를 담지 못할 수 있습니다. *가장 싼 sanity check* — sim 롤아웃에서 접촉 이벤트 시점을 라벨로 잡아, action-aware 임베딩이 그 시점을 t-SNE/probing으로 *separable*하게 표현하는지부터 확인.
- **Body/Hand 분할 시 future token의 attach 지점 불명** — FLARE는 monolithic DiT를 전제로 합니다. PROBE가 Body/Hand로 분할하면 $`M`$ 개 future token을 (i) 공유 trunk에만 붙일지 (ii) hand head에 직접 붙일지가 미정입니다. *가장 싼 sanity check* — 분할 디코더에서 future token을 공유 trunk에만 attach해 alignment가 hand head 성능을 끌어올리는지 ON/OFF 비교.
- **EMA 타깃 불안정 (소규모 데이터)** — $`\rho=0.99`$ 가 최악이었던 것은 잦은 타깃 갱신 불안정 때문입니다. PROBE의 v1 ablation 규모(태스크당 50~1000 trial)에서는 타깃 drift가 더 클 수 있어, $`\rho`$ 스윕을 *초기*에 돌려 collapse/불안정 band를 먼저 측정해야 합니다.
- **표현 collapse(anti-collapse 부재)** — alignment이 frozen(EMA) 타깃과의 코사인 유사도뿐이라, token 수 $`M`$ 을 키우거나 layer를 깊게 가져갈 때 trivial 해로 수렴할 위험이 있습니다(Being-H0.7는 norm/rank 정규화로 차단). *가장 싼 sanity check* — $`M`$ 을 8·16·32·64로 바꿔 정렬된 활성의 effective rank / norm이 무너지지 않는지 모니터.
- **인간 ego ↔ 로봇 임베딩 도메인 갭** — alignment-only ego co-training이 전이되려면 인간 ego 임베딩 분포가 로봇 임베딩 분포와 겹쳐야 합니다. 통제된 head-mounted GoPro는 in-the-wild ego와 다르므로, ego-only alignment에 의존하기 전 *human vs robot 임베딩 도메인 갭*을 먼저 측정(예: MMD/probing).
- **미래 horizon $`H`$ 의 부정합** — 미래 관측이 액션 청크 끝 $`t+H`$ (SigLIP2 ablation에서 $`t+16`$)입니다. 접촉 집약 손가락 태스크의 의미 있는 미래 horizon은 tabletop pick-place보다 훨씬 짧을 수 있어, future-frame offset 스윕이 필요합니다.
- **layer 인덱스 민감도** — alignment layer가 너무 이르면(layer 4) 성능이 떨어졌습니다(§4.4). PROBE backbone 깊이가 다르면 "$`L=6/8`$" 비율을 그대로 옮길 수 없으므로, 분할 디코더 깊이에 맞춰 layer 인덱스를 재탐색해야 합니다.

---

## 💡 컨텍스트 제안

- **P5 §5(Tracked Literature, methodology-base)** — FLARE([arXiv:2505.15659](https://arxiv.org/abs/2505.15659))를 비핀 methodology-base로 추가 검토: "REPA식 future-latent alignment을 flow-matching DiT에 implicit WM auxiliary로 건 최초 형태; D28/D29/D30; Being-H0.7 dual-branch의 직계 선행 + UWM(pixel-latent 생성) 대비 head-to-head 승리." 핀 cap(8)이 가득 차 있어 *핀 교체가 아닌* 계보 메모로 적합합니다.
- **D30 메모(pixel vs latent)** — FLARE vs UWM의 정량 비교(GR1 55.0% vs 29.5%)를 "latent 정렬 > 픽셀-latent 생성"의 인용 근거로 D30 deferred 메모에 추가 검토.
- **D20 후보(prior-preservation)** — *EMA 타깃 임베딩*($`\rho=0.995`$, $`\rho=0.99`$ 불안정) 패턴을 ConSFT·action-side adapter와 나란히 D20 비교 후보로 등록 검토.
- **D22 증거(egocentric co-training)** — 액션-프리 인간 ego 비디오에 alignment-only를 거는 레시피를 D22(egocentric vs mixed) open ablation의 실증 데이터 포인트로 메모 추가 검토.

context/MASTER.md 및 context/P#.md 는 절대 수정하지 않습니다. 위 항목은 사람이 검토할 후보 제안입니다.

> 💡 base 매핑은 `/implement-design analysis/2505.15659/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
