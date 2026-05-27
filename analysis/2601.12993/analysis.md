# Paper Analysis — Being-H0.5: Scaling Human-Centric Robot Learning for Cross-Embodiment Generalization

> PROBE paper-analysis 모드 산출물. 단일 한글 문서이며 영문 1차 파일은
> 없습니다. 형식·이모지·용어 규칙은 `docs/STYLE.md` §5 / §4 를
> 정확히 따릅니다. 재실행 시 이 파일을 덮어씁니다.

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Being-H0.5: Scaling Human-Centric Robot Learning for Cross-Embodiment Generalization |
| 저자 | Hao Luo, Ye Wang, Wanpeng Zhang, Sipeng Zheng, Ziheng Xi, Chaoyi Xu, Haiweng Xu, Haoqi Yuan, Chi Zhang, Yiqing Wang, Yicheng Feng, Zongqing Lu (BeingBeyond / Peking University) |
| 링크 | [arXiv:2601.12993](https://arxiv.org/abs/2601.12993) |
| 발행일 / 버전 | 2026-01-19 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-05-27 |

---

## 🧭 한 줄 요약 (TL;DR)

InternVL-3.5 기반 Mixture-of-Transformers 위에 Mixture-of-Flow 액션 전문가를 얹는다. 그 위에 35,000시간·30개 embodiment 규모의 UniHand-2.0(사람 1인칭 영상 16K h + 로봇 14K h + VL 5K h)으로 사람 손동작과 로봇 제어를 *unified state-action space* 한 벡터로 묶어 사전학습하는 cross-embodiment VLA다. LIBERO 98.9 % / RoboCasa 53.9 % 와 5개 실로봇 일반화 성능을 한 체크포인트로 달성합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 형태가 다른 로봇(병렬 그리퍼·다지 손·다지 휴머노이드)을 한 체크포인트로 통제하면서 플랫폼별 데이터가 부족해도 새 하드웨어에 빠르게 적응하는 일반 정책을 세우는 일입니다.
- **기존 접근의 한계** — 기존 VLA는 한 플랫폼에 묶인 *monolingual speaker* 이며 embodiment 별 MLP head 로 차원을 맞추는 통상 전략은 공통 물리 prior 를 흡수하지 못해 cross-embodiment 일반화가 약합니다. 다지 손 데이터는 전체 코퍼스의 5 % 미만이라 데이터 측면에서도 묶입니다.
- **본 논문의 가설** — 사람의 손 상호작용 흔적이 *physical mother tongue* 로 작동해 모든 kinematic 변종에 공통된 물리 상식을 담는다. 사람 손 모션과 로봇 제어를 *공통 vocabulary* 로 묶으면 저자원 로봇이 데이터-풍부 플랫폼·사람 시연에서 motor skill 을 bootstrap 할 수 있다는 주장입니다.
- **왜 지금 중요한가** — 컨텍스트의 D19b·D22 라인업에 새로 핀된 Being-H0.5 는 "lineage = (init weight × further-pretrain corpus)" 단위를 명시적으로 흔드는 사례다. 사람 영상 16,000 시간을 사전학습 코퍼스의 절반에 올렸기 때문에 P4 의 lineage 비교 실험을 설계할 때 직접적인 기준점이 됩니다.

---

## 🧩 핵심 기여

- **UniHand-2.0** — 사람 1인칭 16,000 시간 + 로봇 14,000 시간 + VL 5,000 시간, 30 개 embodiment, 400 M 샘플 / 120 B 토큰 규모로 *embodied VLA pre-training* 의 최대 코퍼스. 전작 UniHand-1.0 대비 200× 확장.
- **Unified State-Action Space** — 사람 손(MANO)·이종 로봇 제어를 *semantic 슬롯* 으로 분해해 고정 차원 벡터 한 줄에 매핑. 회전은 Axis-Angle, 위치는 delta Cartesian, 통계 정규화 없이 *물리 단위 그대로* 학습.
- **Mixture-of-Transformers + Mixture-of-Flow 아키텍처** — 이해 전문가(Und.)와 액션 전문가(Act.)를 self-attention 으로만 결합하는 BAGEL 패턴 위에 액션 전문가를 *공통 dynamics 기초 층 + 라우팅 기반 specialized 전문가* 두 단계로 분해. MoE 의 sparse activation 으로 cross-embodiment capacity 를 확장.
- **Manifold-Preserving Gating (MPG)** — context feature $`H`$ 가 OOD 일 때 SWD 기반 reliability gate 로 *feature-conditioned residual* 만 줄이고 *ungated prior offset* 으로 안전한 fallback 을 제공해 flow denoising 의 jitter 를 억제.
- **Universal Async Chunking (UAC)** — embodiment 별 control 주기 $`\Delta t^{(e)}`$ 와 latency budget $`L^{(e)}`$ 에 맞춰 prefix/postfix 를 분할하고 postfix 에만 손실을 거는 RTC 의 cross-embodiment 확장. 한 체크포인트가 서로 다른 latency 의 로봇에서 동작.
- **실험 결과** — LIBERO 98.9 %, RoboCasa 53.9 %, 5 개 실로봇 generalist 가 specialist 에 근접하며 사전학습 없는 baseline 대비 전 카테고리 우위. 한 generalist 체크포인트가 데이터 한 점도 없는 unseen task–embodiment 쌍에서도 *non-zero zero-shot* 성공률을 보임.

---

## 🔑 기술 키워드

- **Vision-Language-Action (VLA)** — 영상·언어를 입력으로 받아 로봇 액션을 직접 내놓는 다중모드 모델. Being-H0.5 는 π0/π0.5 등과 같은 family 의 차세대 baseline.
- **Cross-embodiment generalization** — 하나의 정책이 형태가 다른 여러 로봇에서 동작하는 능력. 본 논문의 핵심 청구.
- **MANO** — 사람 손을 wrist 6-DoF + 손가락 관절 파라미터 집합으로 표현하는 표준 hand model. UniHand-2.0 의 사람 손 trace 는 HaWoR + MANO 로 추정.
- **Mixture-of-Transformers (MoT)** — BAGEL 계열 디자인. 멀티모달 시퀀스 전체를 한 self-attention 으로 묶되 *전문가별 weight 셋* 을 따로 두는 구조다. π0 의 VLM + Action Expert 구도를 일반화한 형태.
- **Mixture-of-Flow (MoF)** — 액션 전문가를 (i) 모든 입력 공유 *Foundation Experts* + (ii) Top-K 라우팅 *Specialized Experts* 두 층으로 쪼개 capacity 와 specialization 을 분리한 MoE 변종. 본 논문이 도입한 신규 디자인.
- **Rectified Flow / Flow Matching** — 가우시안 prior 와 데이터 분포 사이를 직선 보간하는 velocity field 를 학습하는 연속 액션 생성 기법. §4-2 글로서리의 "플로우 매칭" 그대로 사용.
- **Unified State-Action Space** — 모든 embodiment 의 state/action 을 고정 차원 벡터의 *semantic slot* 으로 분해해 표현하는 인터페이스. 사람 손까지 *generalized embodiment* 로 흡수합니다.
- **Embodiment-Specific Adaptation (ESA)** — 슬롯 단위로 따로 둔 lightweight adapter bank 에서 해당 embodiment 의 active 슬롯 인덱스 $`\mathcal{I}_e`$ 에 묶인 파라미터만 업데이트해 형태 간섭을 줄이는 post-training 기법.
- **Manifold-Preserving Gating (MPG)** — 관측 임베딩과 *noise-free action 임베딩 anchor* 사이의 Sliced-Wasserstein Distance 로 reliability gate $`g \in (0,1]`$ 를 계산해 feature 의존 보정만 줄이는 게이팅. DiG-Flow 의 output gating 과 달리 *projection 이전* 에 gate 를 곱해 variance reduction 이득을 본다.
- **Universal Async Chunking (UAC)** — Training-Time RTC 의 cross-embodiment 확장. embodiment 별 delay distribution $`\pi^{(e)}(d)`$ 에서 샘플한 $`d`$ 로 prefix/postfix 를 자르고 postfix 손실만 학습. 추론과 실행을 별도 thread 로 돌리는 dual-thread buffer 와 짝.
- **Masked Motion Token Prediction** — 연속 액션 chunk 와 *별개로* 사전학습된 motion tokenizer 로 quantize 한 토큰 일부를 마스킹·복원해 학습. flow-matching 회귀의 보조 prior 역할.
- **InternVL-3.5** — Being-H0.5 의 VLM backbone. 디코더-only 트랜스포머 구조의 공개 가중치 VLM. π0 line 의 PaliGemma-2B 와는 다른 lineage 라는 사실이 P4 관점에서 핵심.

---

## 🔬 방법론

### 직관

설계의 출발점은 두 문장에 압축됩니다.

> "We treat the vast library of human interaction acts as the “mother tongue”—the universal lingua franca of the physical world." (§1)
(한글 해설 — 사람 손 상호작용 데이터를 부족자원 로봇용 보조 데이터가 아니라 모든 embodiment 가 공유하는 기축 언어로 쓰겠다는 선언입니다. NLP 의 multilingual pretrain 비유를 그대로 가져온 셈입니다.)

> "By representing diverse robot actions as tokens in a shared physical vocabulary, we align disparate robot morphologies into a unified latent space, allowing low-resource, complex robots to bootstrap motor skills from data-rich platforms and human demonstrations." (§1)
(한글 해설 — 형태가 다른 로봇 action 을 *공유 어휘* 의 토큰으로 보고 capacity 가 큰 플랫폼의 prior 를 다지 손 같은 저자원 플랫폼이 빌려 쓰게 하겠다는 구체화입니다.)

여기서 두 축이 갈립니다. (1) *데이터* 축에서는 사람 영상 + 다양한 로봇 + VL 을 통째로 다중 모달 시퀀스 한 줄에 직렬화한다. (2) *모델* 축에서는 한 transformer 가 modality 별 전문가를 두되 Top-K 라우팅으로 specialization 도 동시에 수용하는 MoT + MoF 를 채택합니다. 디자인 전체가 "단일 token stream + 단일 backbone" 이 cross-embodiment 일반화의 토대라는 가설을 검증하려는 일관된 선택입니다.

### 아키텍처

![Figure 5 — Being-H0.5 overview (MoT + Unified State-Action Space + MoF)](https://arxiv.org/html/2601.12993/x5.png)

> "Figure 5: Overview of Being-H0.5. Being-H0.5 is a specialized MoT that disentangles multimodal understanding (Und. Expert) and action generation (Act. Expert) while maintaining coupling through shared attention mechanisms. A unified state–action space supports cross-embodiment pre-training by mapping human hand motion and diverse robot controls into semantically aligned slots. Our pre-training leverages UniHand-2.0 by serializing multimodal data into a unified QA-style format, with each modality allocated to the relevant branch. Finally, a Mixture-of-Flow design scales action capacity by combining shared foundation layers with routed specialized experts for embodiment/task-specific dynamics." (§5.1)
(한글 해설 — 좌측의 UniHand-2.0 데이터를 QA-style 직렬화로 입력하고 MoT 구조가 이해/액션 두 전문가를 self-attention 으로만 결합하며 액션 전문가 상단이 MoF 라우팅으로 분기되는 전체 흐름을 한 장에 담은 도식입니다.)

전체 아키텍처는 BAGEL 패턴을 따르는 MoT 구성이며, 주요 구성 요소를 정리하면 이렇습니다.

- **Multimodal Understanding Expert** — 고차원 perception 입력을 해석해 long-horizon planning, subgoal 생성, spatial reasoning 까지 책임.
- **Action Generation Expert** — 정책망 역할. 고수준 계획을 정밀 kinematic 출력으로 변환.
- **Shared self-attention** — 두 전문가가 *같은 token sequence* 를 처리하고 모든 transformer 층에서 self-attention 을 공유. 정보 흐름의 병목을 제거하는 것이 디자인 의도.
- **출력 paradigm** — 텍스트는 next-token prediction, 사람 손의 discrete motion 은 masked token prediction, 로봇 action 은 Rectified Flow 기반 *연속* 생성.
- **Backbone 초기화** — InternVL-3.5 에서 시작 (decoder-only). 백본 선택이 robotic 성능을 결정적으로 좌우한다고 본문에서도 직접 언급한다:

> "It is worth noting that the choice of the VLM backbone is critical, with empirical evidence suggests that the underlying visual features significantly dictate downstream VLA efficacy." (§5.1)
(한글 해설 — VLM lineage 가 downstream VLA 성능을 좌우한다는 진술. D19b 핀에 직접 매칭되는 주장입니다.)

#### Unified State-Action Space (§5.1.1)

> "We map parameters from the MANO hand model directly into this unified space. Specifically, the global wrist pose of the human hand is aligned with the robotic EEF subspace, while finger articulations are mapped to reserved “fine-manipulation” slots." (§5.1.1)
(한글 해설 — 사람 손을 *generalized embodiment* 로 흡수하는 핵심 결정. wrist 6-DoF 는 EEF subspace 에 정렬되고 손가락 관절은 별도 *fine-manipulation* 슬롯이 받습니다.)

표준화 규칙을 정리하면 이렇습니다.

- Cartesian 제어 — *world frame 기준 relative delta displacement* 로 expressed.
- 회전 — Axis-Angle 표기로 통일 (gimbal lock 회피, SE(3) 매니폴드 위 smooth interpolation).
- Joint-space 제어 — absolute radian.
- **통계 정규화 폐기** — `[-1, 1]` 스케일링을 명시적으로 거절하고 raw physical magnitude 를 유지. outlier filtering 만 적용.

#### Mixture-of-Flow (§5.1.2)

액션 전문가는 두 층 hierarchy 로 분해됩니다.

1. **Foundation Experts (Shared Dynamics)** — 초기 transformer block 들. reaching, grasping dynamics, collision avoidance 등 embodiment 와 task 에 불변인 motor primitive 를 인코딩.
2. **Specialized Experts (Embodiment & Task Routing)** — 상단 층은 학습 가능한 gating network 가 Top-K 전문가를 sparse 하게 활성화. embodiment 별 / task 별 specialization 을 sparse 하게 흡수.

> "During training, gradients for a specific task update only the relevant expert pathway, thereby preserving the weights of other localized skills." (§5.1.2)
(한글 해설 — task 별 gradient 가 *해당 expert 경로* 만 갱신하므로 다른 skill 의 weight 가 보존됩니다. 본질적으로 negative transfer 와 catastrophic forgetting 모두를 막는 안전 장치입니다.)

총 파라미터 수와 활성 파라미터 수가 분리되므로 NVIDIA Orin-NX 같은 edge 하드웨어에도 배포할 수 있다고 본문에서 명시합니다.

### 학습 목표 / 손실

#### 통합 시퀀스 모델링 (§5.2.1)

각 학습 샘플은 modality-tagged 세그먼트의 토큰 스트림으로 직렬화됩니다.

$$\mathcal{S}=[\mathbf{x}_{1},\mathbf{x}_{2},\dots,\mathbf{x}_{K}]$$

여기서 $`\mathbf{x}_k=\langle m_k, C_k\rangle`$ 이고 $`m_k\in\mathcal{M}=\{\text{vision, text, state, action}\}`$ 입니다. embodiment $`e`$ 별 raw 신호는 슬롯 매핑 함수로 통합 공간에 사영됩니다.

$$\mathbf{s}=\Phi_{e}(\mathbf{s}^{(e)}),\quad \mathbf{a}=\Phi_{e}(\mathbf{a}^{(e)})$$

학습 시에는 Physical Instruction Tuning 의 QA 포맷 $`[\mathcal{S}_Q;\mathcal{S}_A]`$ 으로 조직하고 손실은 응답 $`\mathcal{S}_A`$ 위에서만 계산.

#### Human-Centric Multi-Task Objective (§5.2.2)

세 task family 가 한 백본에 공존합니다.

- **motion generation** — vision/text/state → action chunk 예측 (메인 supervision).
- **motion description** — vision/state/action → text 예측 (의미 grounding).
- **motion continuation** — past observation + action history → future action chunk (시간적 일관성).

공동 손실:

$$\mathcal{L}=\lambda_{\text{text}}\mathcal{L}_{\text{text}}+\lambda_{\text{act}}\mathcal{L}_{\text{act}}$$

텍스트 손실은 표준 cross-entropy:

$$\mathcal{L}_{\text{text}}=-\sum_{i\in\Omega_{\text{text}}}\log p_{\theta}(y_{i}\mid\mathcal{S}_{<i})$$

#### Hybrid Human Motion Representation (§5.2.3)

연속 액션 회귀와 이산 토큰 예측을 같은 학습 인스턴스에서 동시에 감독합니다.

$$\mathcal{L}_{\text{act}}=\lambda_{1}\mathcal{L}_{\text{FM}}+\lambda_{2}\mathcal{L}_{\text{MASK}}$$

Rectified Flow 항은 target $`\mathbf{a}_i`$ 에 대해 $`\mathbf{x}_t=(1-t)\mathbf{x}_0+t\mathbf{a}_i`$ 의 선형 보간 경로를 사용:

$$\mathcal{L}_{\text{FM}}=\sum_{i\in\Omega_{\text{FM}}}\left\|v_{\theta}(\mathbf{x}_{t},t,c)-(\mathbf{a}_{i}-\mathbf{x}_{0})\right\|_{2}^{2}$$

> "By predicting these discrete tokens, the model learns the underlying “grammar” of hand motion, providing a structural scaffold that supports the continuous flow-matching head." (§5.2.3)
(한글 해설 — 이산 토큰 예측이 high-frequency 실행 노이즈를 걸러내는 *language-like abstraction* 으로 작동하며 연속 flow-matching head 의 안정화 scaffolding 역할을 한다는 설계 의도입니다.)

이산 마스킹 항은 codebook $`\mathbb{C}`$ 에 대한 cross-entropy:

$$\mathcal{L}_{\text{MASK}}=-\sum_{i\in\Omega_{\text{MASK}}}\log p_{\theta}(z_{i}\mid c)$$

#### Embodiment-Specific Adaptation (§5.3.1)

post-training 단계에서는 embodiment 의 active 슬롯 인덱스 $`\mathcal{I}_e`$ 에 묶인 *slot-wise adapter bank* $`\mathbf{W}_{\text{ESA}}\in\mathbb{R}^{K\times d_{\text{out}}\times d_{\text{in}}}`$ 만 업데이트:

$$\mathbf{W}_{\text{ESA}}^{(e)}\triangleq\{\mathbf{W}_{\text{ESA}}[k]:k\in\mathcal{I}_{e}\},\qquad \Delta\mathbf{W}_{\text{ESA}}[k]=\mathbf{0}\ \ \forall k\notin\mathcal{I}_{e}$$

embodiment 간 *partial overlap* 슬롯은 자동으로 파라미터를 공유하고 비공유 슬롯은 격리됩니다. 별도 head per robot 을 대체하는 디자인.

#### Manifold-Preserving Gating (§5.3.2)

![Figure 6 — MPG (left) and UAC (right) overview](https://arxiv.org/html/2601.12993/x6.png)

> "Figure 6: MPG and UAC Overview. Left (MPG): We compare observation embeddings with a reference action embedding (Train: ground truth; Inference: previous iterate) in the Sliced-Wasserstein Distance (SWD) space to obtain a discrepancy-guided gate $`g`$. The gate scales a feature-conditioned residual while an ungated learned prior offset provides a stable fallback, producing enhanced context features $`\tilde{H}`$ for the action expert. Right (UAC): Based on embodiment-specific dynamic delay $`d`$, each predicted action chunk is split into a committed prefix $`\mathbf{A}_{<d}`$ (already queued/executing) and a predicted postfix $`\mathbf{A}_{\geq d}`$. A dual-thread buffer enables asynchronous inference/execution across robots with heterogeneous latency budgets." (§5.3.2)
(한글 해설 — MPG 는 SWD 로 *context 신뢰도* 를 정량화해 feature-conditioned residual 만 줄이고 UAC 는 embodiment 별 latency 에 따라 prefix/postfix 를 자르는 두 trick 을 한 장에 도식화한 그림입니다.)

게이트의 작동 식을 적으면

$$\tilde{H}=H+\lambda\cdot\mathcal{P}_{\text{MPG}}\!\big(g\cdot\mathcal{E}_{\text{obs}}(H)\big)=H+\lambda g\,\mathbf{W}_{\text{MPG}}\mathcal{E}_{\text{obs}}(H)+\lambda\mathbf{b}_{\text{MPG}}$$

discrepancy 측정에는 sliced Wasserstein distance 를 채택합니다.

$$D(\mu_{\hat{H}},\mu_{\hat{Z}})\approx\frac{1}{M}\sum_{m=1}^{M}\left\|\text{sort}(\theta_{m}^{\top}\hat{H})-\text{sort}(\theta_{m}^{\top}\hat{Z})\right\|_{2}^{2}$$

게이트는 temperature-scaled exponential decay 로 정의:

$$g=\exp(-D/\tau)\in(0,1]$$

> "Unlike conventional output gating ( $`\tilde{H}=H+\lambda g\mathcal{R}(H)`$ in DiG-Flow), MPG applies the gate before the projection." (§5.3.2)
(한글 해설 — DiG-Flow 의 output gating 은 projected term + bias 양쪽에 gate 를 곱해 variance 가 커지는 반면 MPG 는 *projection 이전* 에 gate 를 곱하므로 ungated offset 이 분산에 기여하지 않습니다. variance reduction 의 핵심 차별점.)

stop-gradient 도 명시적으로 적용해 게이트가 *변수 학습 우회로* 로 악용되지 않도록 합니다.

#### Universal Async Chunking (§5.3.3)

embodiment $`e`$ 의 effective delay 는 $`\lceil L^{(e)}/\Delta t^{(e)}\rceil`$ 로 스케일링되며 학습 시 delay $`d\sim\pi^{(e)}(d)`$ 를 샘플:

$$d\sim\pi^{(e)}(d),\quad d\in\{0,1,\ldots,d_{\max}^{(e)}-1\}$$

per-token timestep:

$$t_{i}=\mathbf{1}[i<d]+\mathbf{1}[i\geq d]\cdot t_{\text{base}},\quad t_{\text{base}}\sim p(t)$$

손실은 postfix 위에서만 계산:

$$\mathcal{L}_{\text{UAC}}=\sum_{i\geq d}\left\|\hat{v}_{i}-v_{i}^{*}\right\|_{2}^{2}$$

배포는 dual-thread (제어 thread + 추론 thread) + 공유 ring buffer 구조로 비동기 실행을 보장. ring buffer 크기는 chunk 길이의 2× 이상으로 underflow 위험을 줄입니다.

### 학습 셋업

- **백본** — InternVL-3.5, 2 B 변종. RGB-only 입력 224 × 224. 멀티뷰(wrist + 3rd-person) 카메라.
- **사전학습 코퍼스** — UniHand-2.0 = 사람 1인칭 16,000 h + 로봇 14,000 h + VL 5,000 h, 400 M 샘플 / 120 B 토큰. 30 개 embodiment.
- **사람 손 추정 파이프라인** — HaWoR 로 MANO 파라미터 + 카메라 extrinsics 산출. Gemini-2.5 로 per-second + 10초 단위의 dual-level 의미 주석 생성. 4 단계 post-processing(언어 augment / motion-quality filter / manipulation-relevance filter / handedness debiasing) 적용.
- **데이터 컬렉션 시스템 UniCraftor** — Intel RealSense D435 머리 장착 + AprilTag PnP 기반 ground-truth 카메라 pose + hardware-synchronized 풋페달로 contact 시점 기록. 43 task / 200 시간 분량의 in-house 데이터.
- **시뮬레이션 데이터 캡** — 전체 pretraining mixture 의 26 % 이내로 시뮬레이션 데이터를 강제 제한 (Figure 3 좌측).
- **LIBERO 학습** — chunk size 8, packed sequence 7,680 tokens/GPU, effective batch 128, 45 k step, 4 × A800. generalist 는 LIBERO + RoboCasa 를 합쳐 약 2 × step.
- **RoboCasa 평가** — Human-50 few-shot 셋업 (task 당 50 demo), 24 task × 5 held-out scene × task 당 50 trial.
- **공개** — 가중치, 학습 파이프라인, 시뮬레이션 스크립트, 실세계 배포 인프라, 1,000 GPU-hour 사전학습 레시피를 공개 예정으로 명시.

---

## 📊 실험 설정과 결과

### LIBERO (Table 4)

> "We achieve … Being-H0.5 (specialist) 99.2 / 99.6 / 99.4 / 97.4 / 98.9 …" (§7.2, Table 4)
(한글 해설 — LIBERO 의 4 suite 와 평균에서 Being-H0.5 specialist 가 모든 비교 모델을 누른 결과입니다. 본 논문이 SoTA 라고 주장하는 핵심 숫자.)

| Method | L-Spatial | L-Object | L-Goal | L-Long | Average |
|---|---|---|---|---|---|
| Diffusion Policy | 78.5 | 87.5 | 73.5 | 64.8 | 76.1 |
| OpenVLA | 84.7 | 88.4 | 79.2 | 53.7 | 76.5 |
| π0 | 98.0 | 96.8 | 94.4 | 88.4 | 94.4 |
| GR00T-N1 | 94.4 | 97.6 | 93.0 | 90.6 | 93.9 |
| π0.5 | 98.8 | 98.2 | 98.0 | 92.4 | 96.9 |
| OpenVLA-OFT | 97.6 | 98.4 | 97.9 | 94.5 | 97.1 |
| X-VLA | 98.2 | 98.6 | 97.8 | 97.6 | 98.1 |
| EO1 | 99.7 | 99.8 | 99.2 | 94.8 | 98.2 |
| **Being-H0.5 (generalist)** | 97.0 | 98.2 | 99.0 | 96.2 | 97.6 |
| **Being-H0.5 (specialist)** | **99.2** | **99.6** | **99.4** | **97.4** | **98.9** |

(50 trial × task 평균. specialist 가 best 이며 generalist 도 OpenVLA-OFT 와 동급.)

### RoboCasa (Table 5)

> "We empirically demonstrate that Being-H0.5 achieves state-of-the-art results on simulated benchmarks, such as LIBERO (98.9%) and RoboCasa (53.9%) …" (§Abstract / §7.2.2, Table 5)
(한글 해설 — RoboCasa 24-task Human-50 few-shot 셋업에서 specialist 가 53.9 평균으로 신기록을 갱신했다는 본 논문의 두 번째 주력 숫자입니다.)

| Modality | Method | Pick & Place | Doors/Drawers | Others | Total Avg. |
|---|---|---|---|---|---|
| 3D | 3DA | 0.0 | 2.3 | 13.1 | 5.5 |
| 3D | DP3 | 1.5 | 41.7 | 32.0 | 22.8 |
| 3D | GWM | 14.8 | 54.3 | 49.8 | 39.3 |
| RGB (256×256) | BC | 4.3 | 47.0 | 42.2 | 28.9 |
| RGB (256×256) | GR00T-N1 | 18.6 | 50.2 | 39.1 | 36.0 |
| RGB (256×256) | π0.5 | 21.5 | 57.8 | 44.9 | 41.4 |
| RGB (256×256) | π0 | 14.0 | 53.1 | 58.5 | 42.4 |
| RGB (224×224) | **Being-H0.5 (generalist)** | 40 | 73 | 52 | 53.3 |
| RGB (224×224) | **Being-H0.5 (specialist)** | 36 | 71.7 | **57.6** | **53.9** |

(task 당 50 trial × 5 held-out scene. RGB-only 인데도 3D 입력 baseline 까지 압도.)

### 실로봇 5-embodiment 평가 (§7.1)

> "Being-H0.5-specialist performs best on most categories, as expected from embodiment-specific adaptation. Notably, Being-H0.5-generalist is only marginally behind on spatial, long-horizon, and bimanual categories." (§7.1.2)
(한글 해설 — specialist 가 카테고리 대부분에서 최고이며 generalist 의 격차도 spatial/long-horizon/bimanual 에서 거의 없을 정도로 좁습니다. 본문 수치가 "단일 체크포인트로 5 개 로봇 동시 배포가 가능하다"는 주장을 정량으로 뒷받침합니다.)

평가 embodiment 5종: PND Adam-U (31 DoF, dexterous hand) / Unitree G1 + LinkerBot O6 (26 DoF, dexterous) / FR3 + Inspire Hand (13 DoF, dexterous) / BeingBeyond D1 (14 DoF, dexterous) / LeRobot SO-101 (6 DoF, gripper). 10 task 를 spatial / long-horizon / bimanual / generalization 4 카테고리로 묶었고 task 당 30–60 분 시연을 수집.

> "Our model significantly outperforms existing VLAs, such as π0.5, across five physically distinct embodiments, which demonstrates superior cross-embodiment generalization regardless of structural complexity." (§1)
(한글 해설 — 5 개 실로봇 전반에서 π0.5 specialist 를 능가한다는 주장.)

### Ablation 1 — Masked Motion Token Prediction (Table 8)

> "Removing masked prediction leads to a clear drop in MWDS on both the lab-curated and in-the-wild splits." (§7.3.2, Table 8)
(한글 해설 — discrete masked motion objective 를 제거하면 lab/wild 양쪽 MWDS 가 떨어진다는 결과인데 본문 표는 *wild 0.20 → 0.28* 로 오히려 hybrid 가 *낮은* 수치를 보이는 일견 모순 표기를 그대로 두고 있습니다. 해석 주의: 본문 직전 문장은 MWDS 가 cos similarity 라 *높을수록 좋음* 이라고 명시하므로 표의 hybrid 쪽이 더 낮게 적힌 행은 caption 텍스트와 충돌합니다. 본 분석은 표 숫자만 인용하고 caption 의 정성 결론을 그대로 옮겨 본문에 명시된 그대로 둡니다.)

| Method | Lab ↑ | Wild ↑ |
|---|---|---|
| Hybrid (Ours) | 0.33 | 0.20 |
| w/o $`\mathcal{L}_{\text{mask}}`$ | 0.35 | 0.28 |

(원문 Table 8 표기를 그대로 둔다. 본문 caption 과 표 숫자의 정합성은 §⚖️ 한계 항목에서 별도 거론.)

### Ablation 2 — MPG + UAC (Figure 12)

> "Removing MPG+UAC hurts long-horizon and bimanual categories the most, where execution delay and unreliable context amplify compounding errors." (§7.3.3, Figure 12)
(한글 해설 — 사전학습·아키텍처를 고정하고 deployment-time 컴포넌트만 끄면 long-horizon 과 bimanual 카테고리에서 가장 큰 성능 손실이 발생한다는 결과. compounding error 를 deployment trick 으로 잡았다는 정량적 근거입니다.)

### Ablation 3 — Human-Centric Pretraining 효과 (§7.3.1)

> "We adopt the LIBERO 5-shot benchmark with a restricted 10K-step training window. By utilizing a minimal set of training samples, we can effectively isolate performance gains directly attributable to pretrained knowledge versus task-specific rote learning." (§7.3.1)
(한글 해설 — UniHand-2.0 사전학습이 *적응 단계 데이터 효율* 에 미치는 영향을 격리하려는 셋업입니다. Table 6/7 은 single-task vs multi-task 5-shot 양쪽에서 pretraining 효과를 정량화하며 MoF 와 frozen-layer 수 sweep 도 동시에 보고합니다.)

---

## ⚖️ 한계

- **저자가 밝힌 한계** — Masked motion 학습이 *fine-grained motion fidelity* 와 *abstraction-level behavior prior* 사이에서 trade-off 를 만들며 MWDS 같은 정량지표가 wild 분포에서 hybrid 의 손해를 시사한다고 본문 표에 적혀 있습니다. caption 의 *"clear drop in MWDS"* 진술과 Table 8 수치(hybrid 가 낮음)의 정합성은 본 분석 시점에서 *원문 그대로* 유지합니다. 발표 후 erratum 가능성 있음.
- **VLM lineage 명시의 불완전성** — 본문은 InternVL-3.5 라고만 적고 *further-pretrain 코퍼스* 의 정확한 mixing ratio·토크나이저·단계별 lr 등 lineage 식별에 필요한 세부는 GitHub release 로 이연. D19b 의 *(initial weight × corpus)* 2-tuple 비교 실험을 짜려면 코드 공개를 기다려야 합니다.
- **다지 손 데이터 비중의 잔존 약점** — 본문은 dexterous-hand 데이터가 전체의 5 % 미만이라는 일반적 문제를 지적한다. 다만 UniHand-2.0 의 30 개 embodiment 중 *dexterous hand 가 차지하는 시간 비율* 은 표로 명시되지 않아 P1 (Body/Hand 비대칭 학습) 측면에서 데이터 편향이 남습니다.
- **MoT 분해와 Body/Hand 비대칭 분해의 불일치** — MoT 는 *modality* 별 분해(이해/액션)이지 *해부학적* 분해(Body/Hand)는 아닙니다. Mixture-of-Flow 의 specialized expert 라우팅도 *embodiment / task* 단위라 finger-level 접촉 시멘틱이 명시적으로 토큰화되지는 않습니다.
- **System0 류의 저수준 안정화 모듈 부재** — MPG 가 *context-level* 안전 장치라면 slip / grasp 유지 같은 *하위 제어 루프* 수준의 안정화는 별도 모듈 없이 flow-matching 한 패스에 위임됩니다. 본문의 핵심 evaluation 에 dexterous in-hand rotation 같은 contact-rich 시연이 등장하지 않는 점과 맞물립니다.
- **실로봇 시연 분량의 한계** — task 당 30 ~ 60 분 demonstration 으로 일반화한다는 주장은 *bootstrap from pretraining* 의 성공에 의존한다. 그 결과 pretraining mix 외 분포에서 성능이 얼마나 유지될지를 보장할 폭이 좁습니다.

---

## ♻️ 재현성

- **공개 약속** — 본문 §1 에서 "model weights, training pipeline, and simulation scripts" 공개와 "real-world deployment infrastructure and a 1,000 GPU-hour pre-training recipe" 추가 공개를 명시.
- **데이터** — UniHand-2.0 은 자체 큐레이션 + 공개 ego/robot 데이터셋(Ego4D, EPIC-KITCHENS, Egocentric-10K, Open X-Embodiment, AgiBot-World, SO100-Community, InternData-M1, RoboMIND, RoboCOIN, LET …)의 조합. mixing 비율과 라이선스 호환 여부는 본문에서 일괄적으로 다루어지지 않음.
- **하드웨어 수집 시스템 UniCraftor** — 머리 장착 D435 + AprilTag + 풋페달. 부품 수준으로 본문에 묘사되어 재제작 가능.
- **학습 자원** — LIBERO specialist 학습이 4 × A800 GPU 에서 45 k step. 전체 사전학습 자원은 *1,000 GPU-hour 레시피* 라는 단일 숫자로만 표기.
- **arXiv 라이선스 / 코드 라이선스** — 본문에 명시된 라이선스 표기는 없으며 GitHub release 의 LICENSE 를 별도로 확인해야 합니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P4 (VLM Pretraining Preservation)** — Being-H0.5 는 §8.4 의 핀 논문이며 "InternVL-3.5 × UniHand-2.0" 이라는 *별도 lineage* 를 제공해 P4 의 D19b/D22 결정을 직접 흔듭니다.
- **P1 (Heterogeneous Body/Hand Action Expert)** — MoT 의 *이해/액션 분리* 와 MoF 의 *foundation/specialized 분리* 는 Body/Hand 비대칭과는 직교한 축의 분해이지만 π0 류 단일 액션 전문가 패턴 가운데 가장 야심찬 대안 중 하나입니다. D1(split form), D4(Body↔Hand info sharing), D7(π backbone integration) 의 비교군에 곧장 해당합니다.
- **D19 (VLM fine-tuning range)** — 본문은 MLLM 전체(visual encoder + projector 포함)를 *전 파라미터 freeze* 하고 액션 전문가만 학습하는 셋업을 ablation 의 베이스로 사용 (§7.3.1 Table 6, Figure 10/11). 우리 D19 v1 (full freeze + action experts only) 과 정확히 같은 posture 입니다.
- **D19b (VLM backbone lineage choice)** — context 의 핀 entry 가 "TBD (not disclosed; check GitHub config)" 였던 부분이 본문에서 InternVL-3.5 로 확정됩니다. corpus 측은 UniHand-2.0 (16K h ego video + 14K h robot manip + 5K h VL) 로 표기. 우리 v1 인 PaliGemma-2B × π0 mix 와는 *init weight·corpus 양쪽 다 다른* 비교군.
- **D22 (Multi-embodiment pretraining data)** — UniHand-2.0 은 30 embodiment × 13,817 시간의 로봇 데이터 + 16,000 시간 사람 영상을 합친 *가장 큰 catalog* 로 우리 D22 의 *지연된 데이터 catalog 구축* 산출물에 직접 반영됩니다.
- **D23 (Action representation × VLM preservation)** — Rectified Flow 연속 표현을 메인 path 로, masked motion token 을 보조 채널로 *동시에* 사용. 우리 v1 의 (iii) flow-matching head 와 (ii) NL-style action 을 결합한 새 *하이브리드* 카테고리를 제시.
- **D6 (Coordination direction & flow)** — MoT shared self-attention 은 두 전문가 사이를 *layer 마다 양방향* 으로 통신시키는 패턴이므로 우리 v1 의 *hierarchical body→hand* 와 비교군이 될 수 있습니다.
- **Identity 긴장** — 본 논문의 핵심 가설(*human motion = mother tongue*)은 우리 Identity 의 *Body/Hand 해부학 분해 + 구조적 입력 결합 + System0* 4-항 분해와 직교한 길을 택합니다. 곧 *cross-embodiment 일반화* 라는 다른 축에서 SoTA 를 달성하므로 우리의 *contact-precision 차별화 가설* 자체를 부정하지는 않습니다.
- **§10 경쟁자 함의** — §10.1 의 "VLA-only strong performers" 카테고리에 *후보로* 들어가는 antagonist evidence. dexterous in-hand rotation 같은 contact-rich 시연이 본문 평가에 등장하지 않아 *System0 필요성* 청구는 아직 직접적으로 도전받지 않습니다.

---

## ✨ 핀 논문 대비 델타

- **vs Being-H0 (§8.4 비 핀, [arXiv:2507.15597] 계열)** — UniHand-1.0 대비 200× 확장된 코퍼스, embodiment 가 1 류→30 류, 핵심 디자인이 *discrete motion token* 단일에서 *연속 flow + discrete mask 하이브리드* 로 전환, 새 아키텍처 MoT + MoF, deployment-time 컴포넌트 MPG / UAC 추가.
- **vs π0/π0.5 (P1·P4 핀)** — π 계열의 PaliGemma-2B × π in-house corpus 를 *완전히 다른 lineage* 인 InternVL-3.5 × UniHand-2.0 으로 대체했다. π0.5 의 hierarchical inference 가 *System1/System0 analog* 였다면 본 논문은 *MoT 의 self-attention 결합 + MoF 의 routing* 으로 더 fine-grained 한 capacity 분배를 시도. RoboCasa 53.9 vs π0.5 41.4 (12.5 pt) 의 격차는 *RGB-only* 라는 더 좁은 입력 조건에서 달성.
- **vs GR00T N1 (P4 핀, [arXiv:2503.14734])** — Eagle-2 × humanoid trajectories + 인간 비디오 + synthetic 라인업과 비교해 Being-H0.5 는 (a) 사람 영상 비중을 16,000 h 로 *대규모* 끌어올리고 (b) MoT 의 액션 전문가에 *MoE 라우팅* 을 추가했다는 점이 새 차별점입니다. 두 논문 모두 cross-embodiment 를 청구한다. 다만 GR00T-N1 은 dual-system, Being-H0.5 는 MoF 라우팅 sparse activation 으로 접근.
- **vs VLM2VLA (P4 핀, [arXiv:2509.22195])** — VLM2VLA 가 *Gemma-3-12B-IT LoRA + NL-style action* 으로 forgetting 을 완화한다면 Being-H0.5 는 *full freeze + adapter-bank + 연속 flow* 라는 정반대 디자인 결정으로 같은 forgetting 문제를 우회. D23 의 (ii) ↔ (iii) 두 옵션의 *극단 사례* 가 한 자리에 모인 셈.
- **vs MolmoAct2 (P4 핀, [arXiv:2605.02881])** — MolmoAct2 의 *per-layer KV-cache conditioning* 이 백본을 지키려고 고른 *주입 위치* 의 다양화라면 Being-H0.5 의 *MoT shared self-attention* 은 transformer 의 *각 층에서 modality 별 weight 분기* 라는 한층 더 강한 분리를 채택. backbone 보존 강도에서는 두 논문이 비슷하다. 다만 액션 전문가의 capacity 확장 전략(KV-cache 주입 vs sparse routing)은 직교합니다.

---

## ⚙️ 의사결정 함의

- **D19 (VLM FT range)** — v1 (a) full freeze 가 본 논문에서도 *베이스 셋업* 으로 채택됩니다. Figure 10/11 에서 *Action Expert 의 frozen layer 수 sweep* 결과가 함께 보고되므로 우리 ablation 셋업에 *MoF 류 specialized expert 의 부분 freeze* 한 칸을 추가할 근거가 생깁니다. 구체적으로 `train_cfg.action_expert.freeze_first_K_layers ∈ {0, 4, 8}` 같은 sweep 인자.
- **D19b (lineage)** — 핀 entry 의 *VLM init = TBD* 칸을 *InternVL-3.5* 로 채우는 업데이트가 필요합니다. PaliGemma 계열 외의 *decoder-only* 라인을 비교군에 둘 때 *2-pair 비교 실험* (v1 = PaliGemma-2B × π0 mix vs Being-H0.5 lineage) 의 차원이 *backbone 종류* 와 *코퍼스 종류* 양쪽임을 함께 명시합니다.
- **D22 (multi-embodiment data catalog)** — UniHand-2.0 의 표 1 row 들은 catalog 의 *direct row 후보* 로 그대로 끌어올 수 있습니다. *embodiment / hand DoF / arm DoF / camera config / hours* 5 칸이 본문에 명시되어 있어 `pretrain_data.md` 의 lineage-stacking 컬럼을 채우는 작업이 자동화 가능.
- **D23 (action representation × VLM preservation)** — Being-H0.5 는 *연속 flow + masked-token 보조* 의 하이브리드를 보였습니다. 우리 v1 (iii) flow-matching head 만 사용하던 결정에 *aux head 로 masked motion token 을 얹어 noise robustness 를 얻는다* 는 옵션이 새로 추가됩니다. ablation 인자: `loss.action.lambda_mask ∈ {0, 0.1, 0.5}`.
- **D6 (coordination flow)** — MoT 의 *layer 별 shared self-attention* 은 우리 v1 의 *body→hand single FiLM* 보다 훨씬 강한 양방향 결합이라 우리 deferred 후보 (B) cross-attention 의 *극단 사례* 로 평가 대상이 됩니다.
- **MPG / UAC** — flow-matching head 가 deploy 시 *context jitter* 에 취약하다는 문제를 인정한다면 MPG 의 *gate-before-projection + ungated bias* 구조는 우리 stack 에도 그대로 적용 가능한 *모듈형 안전장치* 입니다. UAC 는 D14 (System1↔System0 interface) 의 비동기 실행 패턴을 정형화한 reference 로 끌어 쓸 만합니다. 구체적으로 `policy.context_gate = "mpg"`, `policy.chunking = "uac"` 두 config flag.
- **데이터 normalization 결정** — *통계 정규화 없이 raw physical magnitude 유지* 라는 결정은 우리 D8 (finger/palm structured token) 의 normalization 방침과도 충돌 후보입니다. 데이터셋 전체 통계로 정규화할지 vs raw 단위 유지할지를 검증할 실험 한 줄이 추가됩니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **Cross-embodiment 일반화는 좋지만 contact-precision 에서는 손해를 본다는 가설** — 본 논문 평가는 *Pick & Place / Doors-Drawers / Open-Place-Close / Wipe / Bimanual hand-over* 등 *macro-motion 중심* task 가 대부분이며 in-hand rotation / tool articulation / dexterous insertion 같은 *contact-precision* 카테고리가 부재합니다. 우리 P5 의 in-hand cube rotation 벤치에서 *unified action space* 가 finger 별 슬립을 무력화하는지 확인하는 sanity check 가 가장 싸게 효과 큽니다 — Sharpa hand 에서 30 trial 로 slip count / pose stability 두 지표만 재면 됨.
- **MANO → unified slot 매핑이 *손가락별 접촉 시멘틱* 을 흐리는지** — wrist 6-DoF 는 EEF subspace 에 정렬되어 보존되는 반면, 손가락 articulation 이 "fine-manipulation 슬롯" 으로 *명시적으로 무엇* 인지 본문은 풀어 쓰지 않습니다. 우리 D8 의 *per-finger proprio-tactile 토큰* 과 충돌할 가능성. 검증법: Being-H0.5 의 손가락 슬롯에서 *finger-wise attention* 을 뽑아 contact 시점과의 상관을 측정.
- **InternVL-3.5 backbone 의 spatial reasoning 우위가 실제로 우리 contact-rich 셋업에서 유지되는가** — 본문은 *VLM backbone 선택이 robotic 성능을 dictate* 한다고 명시한다. 다만 검증 task 가 RGB-only macro-motion 중심입니다. dexterous in-hand rotation 처럼 *tactile-dominant* 한 셋업에서도 InternVL-3.5 의 visual prior 가 PaliGemma-2B × π0 mix 보다 유리한지는 별도 비교가 필요. 우리 lineage 비교 *2-pair* 실험 (D19b deferred) 의 *진입 trigger* 가 될 수 있습니다.
- **MPG / UAC 의 contribution 이 사전학습 없는 셋업에서도 유지되는가** — Ablation Figure 12 는 *Being-H0.5 사전학습 + post-training 전체* 를 두고 돌린 ablation 입니다. UniHand-2.0 사전학습 *없이* MPG / UAC 만 떼다 우리 stack 에 붙였을 때 same delta 가 재현되는지 확인하지 않으면 deployment trick 의 transferability 를 단정할 수 없습니다.
- **Masked motion prediction 의 표·caption 불일치** — Table 8 의 *MWDS Wild 0.20 (hybrid) vs 0.28 (w/o mask)* 숫자는 caption 의 정성 결론과 어긋납니다. 우리 데이터에서 동일 ablation 을 재현하기 전에는 *hybrid 권장* 을 그대로 도입하기 위험.

---

## 💡 컨텍스트 제안

- **§8.4 핀 entry 업데이트** — `Being-H0.5` row 의 *VLM init* 컬럼을 `TBD` → `InternVL-3.5 (decoder-only, ~2B)` 로 갱신 권장. 추가로 *Open-weight* 여부·라이선스·코드 공개 일정을 GitHub release 확인 후 D19b lineage 카탈로그에 반영. 본 분석은 *제안만* — `context/MASTER.md` 는 수정하지 않습니다.
- **analysis/_catalogs/vla.md 추가 row 후보** — 본 논문은 *open-weight* + *cross-embodiment* + *MoT/MoF + 연속 + 이산 hybrid* 조합이라 분류 카탈로그의 *Architecture / Training data / Action representation / Eval / Open-weight* 5 칸을 모두 새로 채울 수 있는 사례. 다음 분기 카탈로그 재밸런스 때 row 추가 검토.
- **analysis/_catalogs/pretrain_data.md 갱신** — UniHand-2.0 의 30 embodiment 표 1 row 들이 *lineage-stacking* 컬럼을 그대로 채울 수 있으므로 *데이터 catalog 빌드* 라는 D22 의 deferred 산출물을 본 논문을 seed 로 삼아 시작 가능. 단 mixing ratio 와 라이선스 호환성은 GitHub 공개 후 별도 확인.
- **D6 deferred trigger 후보** — Being-H0.5 의 *MoT shared self-attention* 이 5 embodiment 에서 강건한 결과를 보였으므로 우리 D6 deferred (B) cross-attention 의 *evidence 누적* 으로 한 줄 카운트 가능. trigger 자체는 우리 v1 FiLM 의 *bottleneck 관측* 이 떠야 점화.

---

> 💡 base 매핑은 `/foundry analysis/2601.12993/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
