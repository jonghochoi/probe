# Paper Analysis — APT: Action Expert Pretraining Improves Instruction Generalization of Vision-Language-Action Policies

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | APT: Action Expert Pretraining Improves Instruction Generalization of Vision-Language-Action Policies |
| 저자 | Kechun Xu, Zhenjie Zhu, Anzhe Chen, Rong Xiong, Yue Wang (Zhejiang University · Zhejiang Humanoid Robot Innovation Center) |
| 링크 | [arXiv:2606.12366](https://arxiv.org/abs/2606.12366) · [Website](https://xukechun.github.io/papers/APT/) |
| 발행일 / 버전 | 2026-06-10 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-15 |
| 관련 Pillar | P4, P1 |
| 태그 | vla-arch, forgetting |
| 카탈로그 | models/vla/Standalone/APT |

---

## 🧭 한 줄 요약 (TL;DR)

연속-액션 VLA 의 OOD 언어 일반화 실패를 "랜덤 초기화된 action expert 가 불균형 데이터에서 visual shortcut 으로 빠져 VLM 을 망가뜨린다"로 진단하고, 정책을 $`\pi^{p}(\mathbf{a}\mid\mathbf{v})`$ (VA prior) × $`\mathcal{L}(\ell\mid\mathbf{v},\mathbf{a})`$ (VLA likelihood) 로 Bayesian 분해해 **Stage 1 에서 언어 없이 action expert 를 vision-action prior 로 사전학습**한 뒤 Stage 2 에서 gated fusion 으로 언어를 주입하는 2-stage 학습법 APT 를 제안한다. 잘 초기화된 action prior 만 있으면 knowledge insulation(stop-gradient) 없이 VLM 을 함께 finetune 해도 언어 일반화가 더 좋아진다는 것이 핵심 주장.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 사전학습 VLM 에 연속-액션 expert 를 결합한 VLA 가 in-distribution 에선 강하지만, 미학습 paraphrase·새 객체·compositional 지시 같은 OOD 언어 일반화에서 무너지는 문제를 푼다.
- **기존 접근의 한계** — discrete-token VLA 는 VL co-training 으로 언어 능력을 보존하지만 연속 dexterous 제어에 약하고, 연속-액션 expert 는 사전학습도 co-training 데이터도 없이 불균형 VLA 데이터만으로 랜덤 초기화에서 학습돼 visual shortcut 에 빠진다.
- **기존 처방의 부작용** — 최근 연구는 이 손상을 막으려 action expert→VLM gradient 를 끊는 knowledge insulation(KI)을 쓰지만, 이는 in-distribution 언어 추종만 지키고 OOD task 일반화 간극을 메우지 못한다.
- **본 논문의 가설** — gradient 손상의 근원은 "랜덤 초기화된 action expert × 불균형 데이터"이므로, vision-action pair(본질적으로 균형) 만으로 action expert 를 먼저 사전학습하면 shortcut 경향이 풀리고 언어 추종이 좋아진다.
- **왜 지금 중요한가** — $`\pi`$ ·GR00T 계열 연속-액션 VLA 가 표준이 된 지금, "사전학습 데이터(웹 reasoning) 없이도 VLA 데이터 안에서 action expert 를 사전학습할 수 있는가"는 P4(VLM 사전학습 보존) 의 핵심 미해결 지점을 정면으로 친다.

---

## 🧩 핵심 기여

- VLA 정책을 language-agnostic VA prior 와 language-conditioned VLA likelihood 로 Bayesian 분해하고, "vision-action pair 는 균형이라 shortcut 유인이 없다"는 관찰로 **기존 VLA 데이터 안에서의 action expert 사전학습**을 원리적으로 정당화한다.
- 단일 네트워크 안에서 Stage 1(언어 마스킹 $`N/2`$ 층 VA prior) → Stage 2(층 보간 확장 $`N`$ 층 + 언어 주입) 으로 구현되는 2-stage 학습 절차를 제시한다.
- VLM 의 layer-wise 중간 feature 를 **learnable gate $`\sigma(\hat{w}_{i})`$ 로 조절해 action expert 각 self-attention 층에 주입**하는 gated fusion action expert 설계를 제안한다.
- action expert 사전학습이 $`\pi`$-style·GR00T-style 등 주류 아키텍처에 모두 이식되어 일관된 OOD 언어 일반화 이득을 준다는 것을 시뮬·실물에서 광범위 검증한다.
- KI(stop-gradient) 가 언어 일반화의 **필요조건이 아님**을 보인다 — 잘 초기화된 action prior 위에서는 VLM 까지 joint finetune 하는 편이 오히려 더 좋다.

---

## 🔑 기술 키워드

- **Vision-Language-Action (VLA) policy** — 시각·언어를 받아 로봇 액션을 내는 정책 $`\pi(\mathbf{a}\mid\mathbf{v},\ell)`$. 본 논문은 VLM + 연속 action expert 결합형을 대상으로 한다.
- **Action Expert** — VLM 위에 얹혀 연속 액션을 생성하는 (보통 diffusion/flow) 생성 모듈. 본 논문에서 "사전학습 대상"이 되는 주인공.
- **Vision-Action (VA) Prior** — 언어 없이 시각만으로 액션 분포를 모델링하는 prior $`\pi^{p}(\mathbf{a}\mid\mathbf{v})`$. 매 프레임마다 액션이 1:1 라벨되어 데이터가 균형이라 shortcut 이 안 생긴다.
- **VLA Likelihood** — VA prior 위에서 언어를 주입해 액션 분포를 특정 task 로 조향하는 항 $`\mathcal{L}(\ell\mid\mathbf{v},\mathbf{a})`$.
- **Visual Shortcut** — 언어를 우회하고 시각 단서만으로 액션을 예측하는 퇴화 해. 불균형 데이터에서 vision-only 정책이 full VLA 보다 손실이 $`\epsilon`$ 만큼만 크기에 gradient 가 이쪽으로 쏠린다.
- **Knowledge Insulation (KI)** — action expert → VLM 으로 흐르는 gradient 를 끊어 사전학습 언어 표현 손상을 막는 stop-gradient 처방($`\pi_{0.5}`$ 채택). 본 논문은 이게 필요조건이 아니라고 반박.
- **Gated Fusion** — VLM layer feature $`\phi_{i}^{\text{Qwen3-VL}}`$ 를 learnable scalar gate $`\sigma(\hat{w}_{i})`$ 로 가중해 action expert 각 층에 더하는 주입 방식. VA prior 를 보존하면서 의미 feature 를 흡수.
- **Block-wise Causal Self-Attention** — vision·language·action 토큰을 한 시퀀스로 합쳐 블록 단위 causal mask 로 처리하는 attention. Stage 1 은 언어 토큰을 전부 마스킹해 vision-action 함수로 축소.
- **PRoPE / mRoPE** — Stage 1 의 (카메라 extrinsic 을 위치 임베딩에 넣는) Projective PE 와 Stage 2 신규 층의 Multimodal RoPE. 상속 층은 액션 이해를, 삽입 층은 언어 정렬을 맡는다.
- **Two-Stage Layer Expansion** — Stage 1 의 $`N/2`$ 층 사이에 새 attention 층을 보간해 $`N`$ 층으로 확장하는 방식. 원래 층은 Stage 1 체크포인트로 초기화, 신규 층이 언어 조건화를 전담.

---

## 🔬 방법론

### 직관

APT 의 출발점은 "왜 연속-액션 VLA 는 말을 안 듣는가"에 대한 데이터 관점의 진단이다. 하나의 trajectory 는 수십~수백 개의 vision-action 프레임을 공유하지만 언어 지시는 단 한 줄이다. 그래서 시각-액션 다양성이 언어보다 최소 $`T`$ 배 풍부하고, 랜덤 초기화된 action expert 는 "이 그림이면 이 동작"이라는 시각 지름길로 학습을 끝내버린다. 언어는 학습 신호에 거의 기여하지 않으니 무시되고, 그 와중에 나오는 noisy gradient 가 VLM 의 언어 표현까지 오염시킨다.

핵심 아이디어는 이 문제를 "초기화의 문제"로 재정의하는 것이다. 정책을 베이즈 규칙으로 *언어 없는 prior* 와 *언어 likelihood* 로 쪼개면, prior 부분 $`\pi^{p}(\mathbf{a}\mid\mathbf{v})`$ 은 매 프레임이 고유 액션과 짝지어진 **균형 데이터**라 shortcut 유인 자체가 없다. 따라서 언어를 주입하기 *전에* action expert 를 이 VA prior 로 충분히 사전학습해 두면, 이미 일관된 visuomotor 분포를 가진 상태에서 출발하게 된다.

언어는 그 다음 단계에서 들어온다. likelihood 학습은 "바닥부터 액션 생성을 배우면서 동시에 언어를 grounding"하는 어려운 문제가 아니라, "이미 학습된 액션 분포를 특정 지시에 맞게 미세 조향"하는 훨씬 쉬운 문제가 된다. 이를 한 네트워크 안에서 구현하기 위해 Stage 1 은 $`N/2`$ 층·언어 마스킹으로 prior 를 학습하고, Stage 2 는 그 사이에 새 층을 끼워 $`N`$ 층으로 늘린 뒤 언어를 풀어 likelihood 를 학습한다. VLM feature 는 덮어쓰기가 아니라 gate 로 조절해 주입하므로 prior 가 보존된다.

![Figure 1 — APT 가 지시 추종을 가능케 함](https://arxiv.org/html/2606.12366/x1.png)

> "Figure 1: Action expert pretraining (APT) enables effective instruction following." (§1)
(랜덤 초기화 action expert 가 visual shortcut 으로 빠져 VLM 을 오염시키는 기존 경로 대비, 사전학습된 action prior 가 언어 추종을 살린다는 본 논문의 핵심 주장을 한 장으로 시각화.)

### 아키텍처

입력은 시각 관측 $`\mathbf{v}`$, 언어 지시 $`\ell`$, 액션 $`\mathbf{a}`$ 이며, VLM backbone 으로 **Qwen3-VL-2B-Instruct** 를 쓴다. action expert 는 $`N=20`$ 층의 Transformer 기반 diffusion 모델이다.

액션 토큰 시퀀스는 세 부분으로 구성된다 — $`\mathbf{a}=[\mathbf{a}^{\text{hist}},\;\mathbf{s}^{\text{prop}},\;\mathbf{a}^{\text{noisy}}]`$ — 각각 실행된 액션 이력, 현재 proprioception 상태, 디노이즈 대상 noisy 액션 토큰이다. 디노이징 timestep 은 FiLM 으로 각 attention 층에 주입된다.

> "At each denoising step, visual tokens $`\mathbf{v}`$ , language tokens $`\ell`$ , and action tokens $`\mathbf{a}`$ are concatenated into a single sequence and processed via block-wise causal self-attention." (§3.3)
(VLM 과 action expert 가 분리된 cross-attention 이 아니라, 모든 모달리티를 한 시퀀스로 합쳐 블록 causal mask 로 처리하는 $`\pi`$-style self-attention 계열 설계임을 못 박는 문장.)

핵심 설계는 layer-wise gated fusion 이다. action expert 의 $`N`$ 개 층에 대응해 Qwen3-VL 에서 등간격으로 $`N`$ 개 중간 feature 를 뽑아, $`(i{+}1)`$-번째 층 입력에 gate 로 더한다.

$$\mathbf{h}^{(i+1)}_{\text{in}}=\mathbf{h}^{(i)}_{\text{out}}+\sigma(\hat{w}_{i})\cdot\phi_{i}^{\text{Qwen3-VL}}(\mathbf{v},\ell)$$

여기서 $`\hat{w}_{i}`$ 는 learnable scalar, $`\sigma(\cdot)`$ 는 sigmoid 로, 각 VLM 층이 action expert 에 미치는 영향을 조절하는 게이트다. 첫 층 입력은 VLM 의 input embedding 을 직접 받는다 — $`\mathbf{h}_{\text{in}}^{0}=\phi_{0}^{\text{Qwen3-VL}}(\mathbf{v},\ell)`$.

> "we use Qwen3-VL as our VLM backbone and inject its intermediate features into every self-attention layer of the action expert." (§3.3)
(얕은 공간 feature 와 깊은 의미 feature 를 모두 흡수하되, action expert 가 self-attention 으로 독자적 vision-language 경로도 유지하게 하려는 의도. GR00T 식 "마지막 층 feature 만 cross-attention"과 대비된다.)

![Figure 3 — Action Expert 설계 (gated fusion)](https://arxiv.org/html/2606.12366/x3.png)

> "Figure 3: Action Expert Design. VLM features are injected into action expert via gated fusion. The action expert processes multimodal tokens by self-attention." (§3.3)
(층별 gate 로 VLM feature 를 더하고, vision·language·action 토큰을 self-attention 으로 함께 처리하는 expert 내부 구조도.)

### 학습 목표 / 손실

표준 VLA 목적은 데이터셋 $`D_{\mathrm{VLA}}`$ 의 negative log-likelihood 최소화다.

$$\min\;-\mathbb{E}_{(\mathbf{a},\mathbf{v},\ell)\sim\mathcal{D}_{\mathrm{VLA}}}\bigl[\log\pi(\mathbf{a}\mid\mathbf{v},\ell)\bigr]$$

APT 는 이 정책을 Bayesian factorization 으로 분해한다.

$$\pi(\mathbf{a}\mid\mathbf{v},\ell)\;\propto\;{\pi^{p}(\mathbf{a}\mid\mathbf{v})}\cdot{\mathcal{L}(\ell\mid\mathbf{v},\mathbf{a})}$$

> "The key observation is that although full VLA triplets suffer from language-vision imbalance, vision-action pairs alone are well-balanced and do not create shortcut incentives." (§3.2)
(전체 triplet 은 불균형이지만 vision-action pair 만 떼면 매 프레임이 고유 액션과 짝지어져 균형이라는 것이 사전학습을 가능케 하는 결정적 관찰.)

**shortcut 의 정보이론적 근거(Appendix B).** 표준 VLA 손실은 조건부 엔트로피 하한에 수렴한다 — $`\mathcal{L}_{\mathrm{VLA}}=H(\mathbf{a}\mid\mathbf{v},\ell)`$. 데이터 불균형 가정 $`H(\ell\mid\mathbf{v})\leq\epsilon`$ (대부분 프레임에서 시각만 보면 언어가 거의 결정됨) 하에서, vision-only 정책의 손실 $`\mathcal{L}_{\mathrm{VA}}=H(\mathbf{a}\mid\mathbf{v})`$ 은 full VLA 와 $`\epsilon`$ 차이밖에 안 난다.

$$\mathcal{L}_{\mathrm{VLA}}\leq\mathcal{L}_{\mathrm{VA}}\leq\mathcal{L}_{\mathrm{VLA}}+\epsilon$$

> "Since the vision-only policy is simpler (it does not depend on $`\ell`$ ), gradient descent on the VLA objective from a random action expert is biased toward this vision-only solution." (§B.1)
(vision-only 해가 거의 같은 손실에 더 단순하므로, 랜덤 초기화에서의 경사하강이 구조적으로 shortcut 쪽으로 편향된다는 것 — APT 가 막으려는 바로 그 메커니즘.)

**2-stage 가 shortcut 을 피하는 이유.** Stage 1 은 언어를 아예 조건으로 안 받으니 정의상 shortcut 이 아니라 원하는 VA 정책 그 자체다. Stage 2 는 그 위에서 언어 조건 정책을 학습한다.

$$\mathcal{L}_{\mathrm{VLA}}\leq\min-\mathbb{E}[\log\pi(\mathbf{a}|f_{\theta_{\mathrm{VA}}}(\mathbf{v}),\ell)]\leq\mathcal{L}_{\mathrm{VA}}$$

만약 언어가 완전히 무시되면 우변 부등식이 $`\mathcal{L}_{\mathrm{VA}}`$ 에서 tight 해지는데, 손실이 더 줄어들 수 있다는 사실이 곧 네트워크가 언어를 쓰도록 gradient 가 유인한다는 의미가 된다.

### 학습 셋업

> "After Stage 1 pretraining, we expand to the action expert from $`N/2`$ to $`N`$ attention layers by inserting an interleaved attention layer after each of the original $`N/2`$ layers." (§3.3)
(Stage 1 은 $`N/2`$ 층만 활성·언어 완전 마스킹 → $`[\mathbf{h}_{v},\mathbf{h}_{a}]=\mathrm{SelfAttn}([\mathbf{v},\mathbf{a}])`$ 순수 vision-action 함수. Stage 2 는 각 층 뒤에 보간 층을 삽입해 $`N`$ 층으로 늘리고 언어 마스크를 풀어 $`[\mathbf{h}_{v},\mathbf{h}_{\ell},\mathbf{h}_{a}]=\mathrm{SelfAttn}([\mathbf{v},\ell,\mathbf{a}])`$.)

> "Unlike BayesVLA that freezes the prior in Stage 2, APT jointly optimizes all $`N`$ layers with the full pretraining dataset, allowing the prior and likelihood to co-adapt toward a better equilibrium under large-scale data." (§3.3)
(BayesVLA 는 Stage 2 에서 prior 를 동결하지만, APT 는 상속 층까지 전부 함께 최적화해 prior 와 likelihood 가 대규모 데이터에서 공진화하도록 둔 점이 차이.)

- **액션 표현** — SE(3) manifold 위 10차원 (3D translation + 6D 연속 회전 + 정규화 gripper width, $`-1`$ 닫힘/$`+1`$ 열림). 모든 pose 를 **카메라 좌표계**로 표현해 이종 embodiment 간 equivariance 확보.
- **네트워크** — VLM=Qwen3-VL-2B-Instruct, action expert $`N=20`$ 층, encoder/decoder 는 2-layer MLP(hidden 768), action chunk $`T_{a}=32`$, history length 1, 입력 이미지 $`256\times256`$ (wrist + 3rd-view).
- **위치 인코딩** — Stage 1 은 PRoPE, Stage 2 상속 층은 PRoPE 유지·신규 층은 mRoPE.
- **옵티마이저** — AdamW, action expert lr $`10^{-4}`$ / wd $`10^{-2}`$; VLM joint FT 시 VLM lr $`10^{-5}`$ / wd $`10^{-10}`$; batch 256; Stage 1·2 각 100k iteration.
- **디퓨전** — 학습 DDPM 100 step, 추론 DDIM 20 step.
- **사전학습 데이터** — DROID(78,544 traj) : AgiBotWorld-Alpha(>1M traj) : InternData-A1(~630k) : InternVLA-M1(244k) 를 $`5{:}5{:}4{:}1`$ 가중으로 샘플.

---

## 📊 실험 설정과 결과

검증 축은 셋 — (1) action expert 사전학습의 효과, (2) 정책의 지시 일반화, (3) 아키텍처 설계 타당성. 시뮬은 LIBERO-PRO(LIBERO 에 Pos/Task 섭동 추가) 와 Rigid Object Pick-Place(IsaacSim, SO/UO/UC/UOUE) 두 벤치, 실물은 Agilex Cobot(Piper arm) 으로 수행.

### LIBERO-PRO (success rate %)

| Method | Spatial Pos | Spatial Task | Object Pos | Object Task | Goal Pos | Goal Task | Long Pos | Long Task | Avg |
|---|---|---|---|---|---|---|---|---|---|
| OpenVLA | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| $`\pi_{0}`$ | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| $`\pi_{0.5}`$ | 20 | 1 | 17 | 1 | 38 | 0 | 8 | 1 | 11 |
| LangForce | 11 | 48 | 10 | 10 | 4 | 11 | 2 | 15 | 14 |
| CaP-X | 12 | 14 | 22 | 18 | 26 | 17 | – | – | – |
| APT | 44 | 48 | 7 | 10 | 23 | 11 | 6 | 3 | 19 |
| APT (Ft VLM) | 62 | 62 | 24 | 17 | 10 | 20 | 12 | 12 | 27 |

> "OpenVLA and $`\pi_{0}`$ achieve 0% success under both perturbations, confirming that direct joint training collapses to visual shortcuts and fails once language matters." (§4.1.3, Table 1)
(랜덤 초기화 joint 학습은 Pos·Task 모두 0% — 언어가 중요해지는 순간 완전 붕괴. $`\pi_{0.5}`$ 는 KI 로 Pos 는 회복하나 Task(OOD) 는 거의 0.)

LangForce 는 Task 에서 $`\pi_{0.5}`$ 를 넘지만 Pos 에서 급락한다(언어-액션 결합을 과하게 강제해 layout 변화 적응에 필요한 시각 단서를 억눌러서). APT 는 초기화 측면에서 이 trade-off 를 해소해 평균 19, APT(Ft VLM)은 27 로 둘 다 능가. 예외는 Goal-Pos(장애물 회피가 강조되는 subsuite)로 $`\pi_{0.5}`$ 보다 낮다.

### Rigid Object Pick-Place (rate %) — 설계 차원 ablation

| Method | KI | 2-Stage | Ft VLM | SO | UO | UC | UOUE |
|---|---|---|---|---|---|---|---|
| $`\pi_{0}`$ | | | ✓ | 42 | 30 | 26 | 16 |
| $`\pi_{0.5}`$ | ✓ | | ✓ | 84 | 70 | 86 | 50 |
| APT | | | ✓ | 88 | 56 | 66 | 34 |
| APT | ✓ | | | 90 | 58 | 40 | 40 |
| APT | ✓ | ✓ | | 96 | 74 | 90 | 62 |
| APT | | ✓ | ✓ | 98 | 84 | 92 | 58 |

> "Combining KI with 2-Stage surpasses $`\pi_{0.5}`$ without any VL reasoning data, directly attributing the gain to action expert pretraining." (§4.1.3, Table 2)
(KI+2-Stage(96/74/90/62) 가 웹 reasoning 데이터 없이 $`\pi_{0.5}`$(84/70/86/50) 를 넘음 → 이득의 출처는 action expert 사전학습. KI 만(90/58/40/40) 추가하는 건 Ft VLM 단독(88/56/66/34) 대비 뚜렷한 이득이 없어, "gradient 차단만으로는 일반화 실패가 안 풀린다".)

> "replacing KI with joint VLM finetuning while retaining 2-Stage achieves the best overall result, confirming that KI is not a necessary condition." (§4.1.3, Table 2)
(2-Stage+Ft VLM(98/84/92/58) 가 최고 — 잘 초기화된 action prior 위에서는 VLM 을 함께 학습하는 편이 오히려 일반화를 끌어올린다는 본 논문의 가장 도발적 주장.)

### 추가 ablation (Figure 4·5)

- **아키텍처 이식성** — 2-Stage 학습은 $`\pi`$-style·GR00T-style 거의 모든 설정에서 일반화를 개선. 이득은 APT·GR00T-style 에서 가장 크고 $`\pi`$-style 에서 작은데, $`\pi`$-style 은 매 self-attention 층에 원본 VLM feature 를 그대로 써 사전학습된 action 표현 보존이 덜 효과적이기 때문.
- **대규모 사전학습** — 사전학습 없이 task-specific 데이터만으로 2-stage 를 돌려도(w/o Pretraining) 의미 있는 일반화는 회복되나, UO·UOUE(미학습 카테고리·환경) 에서 크게 뒤처짐 → 다양한 action prior 는 대규모 이종 데이터에서만 얻어진다.
- **언어 주입 방식** — gated fusion 이 Token Insertion(사전학습된 VA prior 층에 언어 토큰을 직접 꽂는 방식) 을 전 차원에서 능가, 특히 UO·UOUE 에서 격차 최대. Token Insertion 은 사전학습된 VA 분포를 급격히 흔들어 prior 를 부분 망각.

### 부가 벤치 (Appendix)

- **원본 LIBERO (Table 4)** — APT 평균 96.1%(Spatial 98.4 / Object 99.4 / Goal 96.4 / Long 90.2)로 $`\pi_{0.5}`$(96.9) 와 동급, $`\pi_{0}`$(94.2)·UniVLA(95.2) 초과. in-distribution 능력을 희생하지 않음을 확인(우월 주장은 아님).
- **LIBERO-Plus (Table 5)** — 7개 섭동축 평균 71.6% 로 최고(X-VLA 71.4 근소 상회). object layout 80.1%(최고)·lighting 93.6%(최고), language 77.6%(2위)·background 92.3%(2위). visual-shortcut 정책이 무너지는 layout·language 축에서 강함.

### 실물 (Table 3, successes/trials)

| Method | PP-SO | PP-UO | PP-UOUC | PP-UOUCUE | Clutter-SO | Clutter-UC | Clutter-UO | Clutter-UOUE |
|---|---|---|---|---|---|---|---|---|
| $`\pi_{0.5}`$ | 27/30 | 11/20 | 9/20 | 16/40 | 18/30 | 18/30 | 4/10 | 3/10 |
| APT | 29/30 | 17/20 | 16/20 | 28/40 | 25/30 | 22/30 | 7/10 | 6/10 |

> "The results diverge dramatically: $`\pi_{0.5}`$ nearly collapses, while APT maintains strong performance." (§4.2.3)
(compositional **task chaining**(여러 task 를 한 prompt 로 연결) 에서 $`\pi_{0.5}`$ 는 첫 task 만 과실행하고 둘째로 전이 못 함 — APT 는 명시적 분할 없이 연쇄 task 를 수행. 단일 지시 coaching 에서는 둘 다 거의 동률이라, 차이는 "단일 task 이해"가 아니라 "한 prompt 내 sub-instruction 파싱·전환"에서 발생.)

per-object 세부(Table 7·8)는 APT 의 우위가 색·형태가 distractor 와 겹치는 미학습 객체(grape vs eggplant, 좁은 bottle) 의 grounding 에서 가장 크게 벌어짐을 보인다. UOUE clutter 의 failure Sankey(Figure 15)는 $`\pi_{0.5}`$ 가 $`10\to8\to5\to3\to3`$, APT 가 $`10\to9\to8\to6\to6`$ 으로 push→grasp 전이에서 격차 최대.

---

## ⚖️ 한계

- **장기 메모리 부재(저자 명시)** — 멀티스텝 진행을 추적하는 명시적 long-horizon memory 가 없어, 다단계 진행 상태 추적이 필요한 task 일반화에 한계. task chaining 에서 APT 도 "현재 sub-task 종료 감지" 실패(잡고도 계속 push, T1 의 close-box 생략) 가 남아, gated fusion 이 sub-task *경계* 까지 해결하진 못함을 시사.
- **tabletop 한정(저자 명시)** — 평가가 테이블탑 조작에 국한. locomotion·mobile manipulation 으로의 확장은 미검증. 액션 표현이 10-DoF SE(3)+gripper 라 손가락 수준 dexterity·contact-rich 조작은 다루지 않음.
- **균형 가정의 취약성(추론)** — VA prior 의 정당화는 $`H(\ell\mid\mathbf{v})\leq\epsilon`$ (시각만 보면 언어가 거의 결정됨) 라는 데이터 불균형 가정에 의존한다. 만약 데이터가 균형(같은 장면에서 언어가 진짜 다양) 이라면 사전학습의 이론적 동기가 약해진다 — 이 가정이 자기 corpus 에서 성립하는지부터 측정해야 한다.
- **prior↔likelihood 공진화의 양날(추론)** — BayesVLA 와 달리 Stage 2 에서 prior 층을 동결하지 않고 함께 최적화하는데, 이는 "더 나은 equilibrium" 이득과 "어렵게 얻은 VA prior 를 다시 흔들 위험" 을 동시에 가진다. 대규모 데이터에서만 안전한지, 저데이터에서 prior 가 무너지는지의 경계가 본문에 없다.
- **gated fusion 의 VLM 의존(추론)** — 설계가 Qwen3-VL 의 layer-wise 중간 feature 접근에 의존한다. 백본을 바꾸면(예: PaliGemma 계열) 층별 feature 추출·등간격 샘플링·gate 보정을 다시 설계해야 하므로 이식 비용이 0 이 아니다.
- **공정 비교의 한계(추론)** — 실물에서 $`\pi_{0.5}`$ 는 joint-space 액션, APT 는 카메라-프레임 액션으로 표현이 달라, 이득의 일부가 사전학습이 아니라 액션 표현 차이에서 올 가능성을 완전히 배제하지 못한다.

---

## ♻️ 재현성

- **코드/가중치** — 별도 GitHub/HuggingFace 링크는 본문·메타에서 확인되지 않고, project page([xukechun.github.io/papers/APT](https://xukechun.github.io/papers/APT/)) 만 제공. 공개 코드 여부는 미확인.
- **데이터** — 사전학습은 모두 공개 데이터셋 조합(DROID, AgiBotWorld-Alpha, InternData-A1, InternVLA-M1), 가중·iteration·옵티마이저 하이퍼는 Appendix A 에 상세 기재되어 절차 재현 가능.
- **하드웨어** — VLM Qwen3-VL-2B-Instruct, 실물은 Agilex Cobot + Piper arm + ORBBEC DaBai 카메라 2대($`640\times480`$ RGB-D). 시뮬은 IsaacSim 기반 Rigid Object Pick-Place + LIBERO 계열.
- **벤치마크** — LIBERO / LIBERO-Plus / LIBERO-PRO / Rigid Object Pick-Place 모두 공개 또는 선행연구 기반.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P4(VLM 사전학습 보존) — primary.** APT 는 D20(prior-preservation strategy) 과 D21(staged pretraining + adaptation recipe) 을 정면으로 친다. 우리의 D20 v1 은 "action-side adapter(split heads) + 적응 단계 conservative SFT", D21 v1 은 "Stage0 lineage → Stage1 corpus 사전학습 → Stage2 VLM-stable + Body/Hand expert → Stage3 conservative 적응"인데, APT 는 보존을 *적응 단계*가 아니라 *사전학습 단계*에서 VA-prior 초기화로 달성하는 직교적 처방을 제시한다. 또 D19(adaptation range) v1 의 "(a) full VLM freeze" 기본값에 대해, "잘 초기화된 action prior 위에선 VLM joint FT 가 freeze 보다 낫다"는 반례 증거를 던진다. D23(action representation × pretraining) — diffusion action expert 를 VA prior 로 사전학습하는 경로는 우리의 flow-matching head 결정과 표현은 다르나 "action head 를 사전학습 대상으로 본다"는 관점이 새롭다.
- **P1(이종 action expert) — secondary.** gated fusion(layer-wise VLM feature × learnable gate 주입) 은 D7(π backbone integration / partition) 과 D4(Body↔Hand information sharing, v1=FiLM) 의 설계 공간에 직접 들어온다. APT 의 gate $`\sigma(\hat{w}_{i})`$ 는 우리가 D4 에서 채택한 FiLM 식 조건화와 같은 계열의 메커니즘이며, "VLM feature 를 덮어쓰지 않고 게이트로 흡수"하는 방식은 split head 에도 차용 가능.
- **Identity 지지/긴장** — Identity 의 "data-efficient adaptation through the VLM pretraining recipe, prior-preservation as one downstream lever" 와 강하게 정렬. 다만 APT 는 손가락 수준 dexterity·tactile 을 다루지 않아(테이블탑 10-DoF), 우리의 hand-centric 코어와는 적용 영역이 어긋난다.
- **경쟁자 함의** — P4 pin 인 $`\pi_{0.5}`$(KI co-training) 의 KI 를 "필요조건 아님"으로 반박, ConSFT(적응 단계 보존) 와는 개입 *단계*가 다른 경쟁/보완 관계.

---

## ✨ 핀 논문 대비 델타

- **vs $`\pi_{0.5}`$ (P4 pin)** — $`\pi_{0.5}`$ 는 웹-scale reasoning 데이터 co-training + KI(stop-gradient) 로 언어 능력을 보존한다. APT 는 **VL reasoning 데이터 없이, KI 없이** VLA 데이터 안의 vision-action pair 만으로 action expert 를 사전학습해 더 나은 OOD 언어 일반화를 얻고, 이득의 출처를 ablation 으로 action 사전학습에 귀속시킨다(Table 2).
- **vs ConSFT (P4 pin)** — ConSFT 는 *적응(SFT)* 단계에서 per-sample conservative weight 로 prior 를 보존한다. APT 는 *사전학습* 단계에서 VA-prior 초기화로 애초에 shortcut 을 막는다 — 같은 "prior 보존" 목표를 다른 학습 단계에서 푼다.
- **vs BayesVLA (본문 핵심 비교)** — 둘 다 prior×likelihood Bayesian 분해를 쓰지만, BayesVLA 는 pre-/post-contact 분해라 이종 데이터셋 확장성이 약하고 Stage 2 에서 prior 를 동결한다. APT 는 분해를 *action 사전학습 관점*으로 일반화하고 prior 를 함께 공진화시킨다.
- **vs LangForce** — LangForce 는 action-instruction 상호정보 최대화로 언어 추종을 강제하나 seen-task 추종에 집중해 OOD 에 약하고 Pos(layout 변화) 에서 급락. APT 는 초기화로 trade-off 자체를 해소.

---

## ⚙️ 의사결정 함의

- **D21(staged recipe) 에 "VA-prior 사전학습" 서브스테이지 추가 검토** — 우리 recipe 의 Stage 2(VLM-stable + Body/Hand expert 학습) 앞에, 언어 토큰을 마스킹하고 vision + proprio 만으로 Body/Hand expert 를 사전학습하는 단계를 끼우는 안. 구체 config: `language_mask=True`, 활성 층 `N/2`, 그 뒤 보간 층 삽입으로 `N` 확장.
- **D20(prior preservation) 에 gated fusion 후보 추가** — VLM feature 를 expert 에 주입할 때 덮어쓰기 대신 `gate = sigmoid(learnable_scalar)` per-layer 게이트를 두는 안. D4 의 FiLM 조건화와 같은 계열이라 split head 에 자연스럽게 얹힌다.
- **D19(adaptation range) 의 freeze 기본값 재검증 트리거** — "잘 초기화된 action prior 가 있으면 VLM joint FT > freeze" 라는 APT 증거는 v1=(a) full freeze 를 흔든다. 측정 가능한 판정: action expert 사전학습 *후* `vlm_lr=1e-5, vlm_wd=1e-10` 로 joint FT 했을 때 freeze 대비 prior-retention/OOD 지표가 개선되는지.
- **주의** — APT 의 action expert 는 diffusion(DDPM/DDIM)이고 우리는 flow-matching(D23 v1) 이다. 사전학습 *관점*은 표현-무관하게 차용 가능하나, gated fusion 의 "층 보간 확장 + 언어 마스킹" 구현 디테일은 우리 expert 구조에 맞게 재설계해야 한다.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 체크) 데이터 불균형 가정 측정** — APT 의 이론적 동기는 $`H(\ell\mid\mathbf{v})\leq\epsilon`$ 이다. 우리 corpus(egocentric-centric + robot) 에서 "같은 시각 프레임에 얼마나 다양한 언어가 붙는가"를 추정해 $`P(\ell\mid\mathbf{v})`$ 가 실제로 one-hot 에 가까운지 먼저 확인한다. 균형이면 사전학습 이득이 작아진다.
- **백본 이식성** — gated fusion 은 Qwen3-VL 의 등간격 layer-wise feature 에 의존한다. 우리 lineage 인 $`\pi_{0}`$/PaliGemma 백본이 action expert 에 층별 feature 를 노출하는 구조인지, $`\pi`$-style block-wise self-attention 위에서 gate 주입이 의미를 갖는지 확인. (논문 자체가 $`\pi`$-style 에선 이득이 가장 작다고 보고 — 우리 백본 계열에서 효과 감소 위험.)
- **저데이터/적응 단계 안정성** — APT 이득의 큰 몫은 1M+ traj 대규모 사전학습에서 온다(w/o Pretraining 은 UO·UOUE 에서 크게 하락). 우리 목표는 "배포 시 수분 데이터" 이므로, 사전학습 없이 task-specific 데이터만으로 2-stage 를 돌렸을 때 prior 가 오히려 무너지지 않는지(공진화의 양날) 부터 본다.
- **액션 표현/embodiment 정합** — APT 는 카메라-프레임 10-DoF SE(3)+gripper 표현 + PRoPE(카메라 extrinsic 필요) 를 쓴다. 우리 22-DoF hand + flow-matching head 와 표현·DoF 가 달라, 사전학습 prior 가 손가락 수준 contact-rich 분포를 담는지 미지. 먼저 Body(arm/wrist) 액션에만 VA-prior 사전학습을 적용해 보고 Hand expert 로 확장.
- **dexterity·tactile 공백** — 본 논문은 tactile/force 모달리티가 전혀 없는 테이블탑 pick-place 다. 우리의 per-finger proprio-tactile binding(P2) 토큰이 추가되면 "vision-action pair 가 균형"이라는 전제 자체가 달라질 수 있어, 사전학습 균형 논리가 tactile 토큰 포함 시에도 유지되는지 검증 필요.

---

## 💡 컨텍스트 제안

- **P4 §5 methodology base 후보** — APT(arXiv:2606.12366) 를 "사전학습 단계 prior 보존(VA-prior pretraining)" 증거로 비-pin methodology base 에 추가 검토. ConSFT(적응 단계 보존) 와 짝지어 "보존을 어느 단계에서 푸는가"의 대조군으로 유용. (pin 8개 cap 은 유지 — 교체가 아니라 base 행 추가 제안.)
- **D19 deferred trigger 후보** — "action expert 사전학습이 선행되면 VLM joint FT 가 freeze 를 능가" 가설을 D19=(a) freeze 의 *insufficiency trigger* 후보로 기록 제안. 단, 우리 lineage·flow-matching·dexterity 조건에서 재현되는지 위 실패 모드 검증이 선행 조건.
- context/ 파일은 수정하지 않았습니다. 위는 제안일 뿐입니다.

> 💡 base 매핑은 `/implement-design analysis/2606.12366/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
