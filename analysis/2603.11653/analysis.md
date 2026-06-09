# Paper Analysis — Simple Recipe Works: Vision-Language-Action Models are Natural Continual Learners with Reinforcement Learning

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Simple Recipe Works: Vision-Language-Action Models are Natural Continual Learners with Reinforcement Learning |
| 저자 | Jiaheng Hu, Jay Shim, Chen Tang, Yoonchang Sung, Bo Liu, Peter Stone, Roberto Martín-Martín |
| 링크 | [arXiv:2603.11653](https://arxiv.org/abs/2603.11653) · [GitHub](https://github.com/UT-Austin-RobIn/continual-vla-rl) |
| 발행일 / 버전 | 2026-03-12 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-05-28 |
| 관련 Pillar | P4 |
| 태그 | continual, forgetting, vla-arch |

---

## 🧭 한 줄 요약 (TL;DR)

큰 사전학습 VLA에 LoRA를 얹어 on-policy RL(GRPO)로 작업을 순차 fine-tuning하면, 별다른 망각 방지 기법 없이도 망각이 거의 없고 가소성과 zero-shot 일반화까지 유지되어 정교한 CRL 기법들을 자주 능가합니다. 큰 사전학습 모델·LoRA·on-policy RL 세 요소가 맞물리면서 학습이 안정됩니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 진화하는 환경에서 스스로 개선하는 임바디드 에이전트를 위해, VLA 모델을 비정상(non-stationary) 작업 흐름에 순차 적응시키는 Continual Reinforcement Learning(CRL)을 어떻게 안정적으로 수행할지를 다룹니다.
- **기존 접근의 한계** — 연속 학습의 통념상 단순 Sequential Fine-Tuning(Seq. FT)은 catastrophic forgetting에 취약하므로, 정규화·리플레이·파라미터 격리 같은 복잡한 CRL 기법이 필요하다고 여겨졌습니다. 그러나 이런 기법은 가소성 손실(plasticity loss)이라는 대가를 치르며 stability–plasticity 딜레마에 묶입니다.
- **본 논문의 가설** — 수십억 파라미터의 사전학습 VLA + 파라미터 효율적 적응(LoRA) + on-policy RL이라는 조합에서는, 이 통념이 깨지고 단순 Seq. FT가 오히려 강력하게 동작할 수 있다고 봅니다.
- **왜 지금 중요한가** — VLA의 RL post-training이 자기개선 경로로 부상한 시점에, "복잡한 CRL 없이도 된다"는 결론은 평생 적응(lifelong adaptation)의 확장 가능한 최소 레시피를 제시합니다.

---

## 🧩 핵심 기여

- VLA 3종(OpenVLA-OFT, Pi-0, OpenVLA)과 5개 평생 RL 벤치마크에 걸쳐 8개 CRL 알고리즘을 체계적으로 비교한 실증 연구를 수행했습니다.
- LoRA를 적용한 단순 Seq. FT가 높은 가소성, 2% 미만(때로는 음수)의 망각, 강한 zero-shot 일반화를 동시에 달성하며, 더 정교한 CRL 기법들을 자주 능가함을 보였습니다.
- 망각 억제가 큰 사전학습 모델·LoRA·on-policy RL 세 요소의 시너지에서 나오며, 각 요소가 **목표(objective)·제약(constraints)·용량(capacity)** 이라는 상보적 관점에서 망각을 줄임을 ablation으로 분리·입증했습니다.
- 카메라·조명·로봇 위치 perturbation, 물리 엔진/모델 변경, 작업 순서 변경 등 통제된 변형 전반에서 이 현상이 일관되게 유지됨을 보였습니다.
- Fisher energy, per-layer effective rank, 정보이론적 가소성 분석 등 메커니즘 분석과 오픈소스 구현을 제공했습니다.

---

## 🔑 기술 키워드

- **Continual Reinforcement Learning (CRL)** — 비정상 작업 흐름에 강화학습 에이전트가 이전 능력을 유지하며 순차 적응하는 설정. 이 논문이 대상으로 삼는 문제 틀입니다.
- **Sequential Fine-Tuning (Seq. FT)** — 새 작업이 올 때마다 망각 방지 장치 없이 그 작업에만 fine-tuning하는 가장 단순한 방법. 통상 CRL의 하한(lower bound)으로 쓰이지만 이 논문에서는 강력한 후보로 재평가됩니다.
- **Catastrophic forgetting** — 새 작업을 배우며 이전 작업 성능이 급락하는 현상. 이 논문이 "큰 VLA + RL + LoRA에서는 거의 일어나지 않는다"고 주장하는 대상입니다.
- **Stability–plasticity dilemma** — 과거 지식 보존(안정성)과 새 작업 적응(가소성)이 상충하는 딜레마. 세 요소의 시너지가 이 트레이드오프를 재편한다는 것이 핵심 메시지입니다.
- **LoRA (Low-Rank Adaptation)** — 사전학습 가중치 $`W_0`$ 를 고정하고 저랭크 행렬 곱 $`BA`$ 만 학습하는 PEFT 기법. 업데이트를 좁은 부분공간으로 제한해 망각을 억제하는 한 축입니다.
- **GRPO (Group Relative Policy Optimization)** — 그룹 내 보상 표준화로 advantage를 추정하는 안정적 policy-gradient 기법. 이 논문의 on-policy RL 백본입니다.
- **On-policy RL** — 현재 정책이 만든 샘플로만 학습하는 RL. policy gradient가 기존 지지(support) 밖으로 확률 질량을 급격히 못 옮기게 해 암묵적 KL 정규화를 만든다는 점이 망각 억제의 한 축입니다.
- **Negative Backward Transfer (NBT)** — 망각(forgetting) 지표. 작업을 막 학습한 직후 대비 전체 학습 종료 후의 성능 저하를 평균한 값으로, 낮을수록 좋습니다.
- **Zero-Shot Success (ZS)** — 학습에 쓰지 않은 held-out 작업에 대한 최종 성능. VLA의 사전학습 일반화 능력 보존을 측정하기 위해 이 논문이 도입한 지표입니다.
- **Fisher energy** — 현재 작업 그래디언트 방향에서 사전학습 작업 Fisher 정보 행렬의 Rayleigh 몫. 값이 높을수록 새 작업이 기존 지식을 더 크게 간섭한다는 곡률 척도입니다.

---

## 🔬 방법론

### 직관

![Figure 1 — Large VLAs as Natural Continual Learners](https://arxiv.org/html/2603.11653/x1.png)

> "Large VLAs as Natural Continual Learners. We show that the synergy between pre-trained VLA, on-policy RL, and LoRA is enough to overcome catastrophic forgetting while maintaining plasticity, enabling simple Sequential Fine-Tuning to achieve surprisingly good performance." (§1, Figure 1)
(한글 해설 — 논문의 핵심 주장을 한 장에 압축한 그림으로, 세 요소의 시너지만으로 망각을 이기면서 가소성을 유지한다는 메시지를 시각화합니다.)

이 논문의 출발점은 "복잡한 CRL 기법이 정말 필요한가"라는 의심입니다. 통념과 달리, 큰 사전학습 VLA에 LoRA로 on-policy RL을 적용하면 단순 순차 학습만으로도 망각이 거의 발생하지 않는다는 관찰에서 시작합니다.

> "Rather than exacerbating instability, these components collectively make continual adaptation more stable, while synergistically preserving the learning plasticity." (§1)
(한글 해설 — 세 구성요소가 불안정을 키우기는커녕 오히려 적응을 안정화하면서 가소성을 함께 보존한다는, 본 논문의 메커니즘 가설입니다.)

### 아키텍처

작업은 유한 horizon의 언어 조건부 MDP로 정식화됩니다.

> "We formulate each task in VLA post-training as a finite-horizon, language-conditioned Markov Decision Process (MDP)" (§3.1)
(한글 해설 — 각 작업을 상태·행동·전이·horizon·초기분포·언어 지시·희소 보상으로 정의되는 MDP로 놓습니다.)

$$\mathcal{M}=(\mathcal{S},\mathcal{A},P,H,\mu_{0},\ell,r)$$

여기서 $`\ell\in\mathcal{L}`$ 은 자연어 지시이고 $`r:\mathcal{S}\times\mathcal{A}\times\mathcal{L}\rightarrow\{0,1\}`$ 은 희소 보상입니다. 모든 작업은 동일한 상태·행동 공간을 공유하며, 상태는 카메라 이미지, 행동은 로봇 엔드이펙터 포즈와 그리퍼 명령으로 구성됩니다. 정책 $`\pi_{\theta}(a_{t}\mid s_{t},\ell)`$ 는 누적 보상을 최대화하도록 학습됩니다.

연속 설정에서는 에이전트가 에이전트의 통제를 벗어난 고정 순서로 $`T`$ 개 작업 $`\{\mathcal{T}_{1},\dots,\mathcal{T}_{T}\}`$ 을 순차 학습하며, 작업 $`k`$ 까지의 목표는 본 적이 있는 작업들의 평균 리턴을 최대화하는 것입니다.

$$\max_{\theta}J_{\mathrm{CRL}}(\theta)=\frac{1}{k}\sum_{j=1}^{k}\mathbb{E}_{\pi_{\theta}}\left[\sum_{t=1}^{H}r^{j}\right]$$

> "The agent learns each task purely through interacting with the environment, without access to any demonstrations." (§3.2)
(한글 해설 — 시연 없이 환경 상호작용만으로 학습하며, 작업 $`k`$ 학습 시 이전 작업의 데이터·환경에 접근할 수 없다는 CRL의 정의적 제약입니다.)

LoRA는 사전학습 가중치 $`W_{0}\in\mathbb{R}^{d\times k}`$ 를 고정하고 저랭크 행렬 곱만 학습합니다.

$$W=W_{0}+BA$$

여기서 $`B\in\mathbb{R}^{d\times r}`$, $`A\in\mathbb{R}^{r\times k}`$ 이고 랭크 $`r\ll\min(d,k)`$ 입니다. 학습 후 $`W_{\text{new}}\leftarrow W_{0}+BA`$ 로 병합할 수 있습니다.

### 학습 목표 / 손실

on-policy RL 백본으로 GRPO를 사용합니다. 직전 정책 $`\pi_{\theta_{\text{old}}}`$ 에서 trajectory를 샘플링한 뒤 다음을 최적화합니다.

$$\max_{\theta}\;\mathbb{E}_{(s_{t},a_{t})\sim\pi_{\theta_{\text{old}}}}\left[\min\!\left(\rho_{t}(\theta)\,\hat{A},\;\mathrm{clip}(\rho_{t}(\theta),1-\epsilon,1+\epsilon)\,\hat{A}\right)\right]$$

$$\rho_{t}(\theta)=\frac{\pi_{\theta}(a_{t}\mid s_{t},\ell)}{\pi_{\theta_{\text{old}}}(a_{t}\mid s_{t},\ell)},\quad\hat{A}=\frac{R-\mu_{R}}{\sigma_{R}}$$

여기서 $`R`$ 은 샘플링된 trajectory의 에피소드 리턴이고, $`\mu_{R},\sigma_{R}`$ 은 샘플 그룹 내 리턴의 평균과 표준편차입니다(§A). 자기회귀 토큰형 VLA는 행동 토큰 시퀀스에 직접 GRPO를 적용하고, flow/diffusion 행동 헤드를 쓰는 연속형 VLA는 결정론적 ODE $`\frac{dx_{t}}{dt}=v_{\theta}(x_{t},t)`$ 에 Flow-SDE 형식의 제어된 가우시안 노이즈 $`dx_{t}=v_{\theta}(x_{t},t)\,dt+\sigma_{t}\,dW_{t}`$ 를 주입해 확률적 정책으로 바꾼 뒤 동일한 policy gradient를 적용합니다.

평가는 표준 연속 학습 지표를 사용합니다. 최종 평균 성공률 AVG, 망각 NBT, 순방향 전이 FWT, 그리고 본 논문이 도입한 held-out 성능 ZS입니다.

$$\text{NBT}=\frac{1}{T-1}\sum_{j=1}^{T-1}\left(S_{j,j}-S_{T,j}\right)$$

$$\text{ZS}=\frac{1}{|\mathcal{H}|}\sum_{h\in\mathcal{H}}S^{\text{held}}_{T,h}$$

> "Unlike in classic continual RL, VLA contain strong zero-shot performance on unseen tasks even before any training occur." (§B)
(한글 해설 — VLA는 학습 전부터 미지 작업에 강한 zero-shot 성능을 가지므로, 이를 보존·향상하는 능력을 별도 지표 ZS로 측정하려는 동기에서 나왔습니다.)

### 학습 셋업

모든 방법이 동일한 핵심 하이퍼파라미터(네트워크 구조, 학습률, 배치 크기, 옵티마이저, LoRA 랭크, GRPO 하이퍼파라미터)를 Yu et al. (2025a)의 기본 설정에서 그대로 상속합니다. 방법별 하이퍼파라미터(EWC 계수, Replay 계수 등)는 원논문 값의 한 자릿수 범위에서 로컬 스윕해 최적값을 고릅니다.

> "Notably, we do not do any hyperparameter tuning for Sequential Fine-Tuning." (§4.1)
(한글 해설 — Seq. FT에는 하이퍼파라미터 튜닝을 전혀 하지 않았다는 점으로, 단순함이 곧 강함이라는 메시지를 셋업 단계에서부터 강조합니다.)

GRPO + LoRA(rank 32)를 기본으로 하며, 작업당 3개 시드로 평균 ± 표준오차를 보고합니다. 공유 하이퍼파라미터는 옵티마이저 AdamW, 학습률 $`2\times 10^{-5}`$, gradient clip norm 1.0, global batch size 8192, 할인 $`\gamma=0.99`$, GAE $`\lambda=0.95`$, clip ratio 0.20/0.28, KL 계수 $`\beta=0.0`$, entropy bonus 0.0, rollout epoch 16, group size 8입니다(§F, Table 6). 각 base 모델은 소량의 in-domain 데이터로 SFT해 초기 성공률을 0이 아니게 맞춥니다.

---

## 📊 실험 설정과 결과

세 LIBERO 벤치마크(libero-object/spatial/long-horizon)에서 측정한 주요 수치는 다음과 같습니다(§4.2, Table 1).

| Benchmark / Method | AVG ↑ | NBT ↓ | FWT ↑ | ZS ↑ |
|---|---|---|---|---|
| libero-spatial · Seq. FT | 81.2 ± 0.4 | 0.3 ± 0.5 | 3.9 ± 1.5 | 57.1 ± 1.1 |
| libero-spatial · Multitask (Oracle) | 85.8 ± 0.2 | – | – | 51.2 ± 0.7 |
| libero-object · Seq. FT | 93.2 ± 0.7 | 1.0 ± 0.7 | 7.1 ± 0.8 | 25.4 ± 0.2 |
| libero-object · Multitask (Oracle) | 95.7 ± 0.7 | – | – | 27.6 ± 1.3 |
| libero-long-horizon · Seq. FT | 89.8 ± 0.9 | -2.4 ± 1.0 | 0.5 ± 0.1 | 86.6 ± 0.2 |
| libero-long-horizon · Multitask (Oracle) | 90.5 ± 0.8 | – | – | 85.2 ± 0.5 |

> "we observe little performance degradation on previously learned tasks, with the NBT metric consistently showing less than 2% of (and sometimes even negative) forgetting." (§4.2)
(한글 해설 — 망각 지표 NBT가 일관되게 2% 미만, 때로는 음수라는 핵심 수치로, "거의 망각이 없다"는 주장의 직접 근거입니다.)

> "Sequential Fine-Tuning consistently preserves strong zero-shot generalization capabilities, and often outperforms the multi-task oracle." (§4.2)
(한글 해설 — Seq. FT의 ZS가 오라클을 자주 능가한다는 관찰로, 단순 순차 학습이 일반화를 깎기는커녕 오히려 키운다고 주장합니다.)

ablation은 세 요소를 하나씩 제거했을 때의 붕괴를 보여줍니다(§5.1, Table 3, libero-spatial).

| Ablation | AVG ↑ | NBT ↓ | ZS ↑ |
|---|---|---|---|
| Seq. FT (Original) | 81.2 ± 0.4 | 0.3 ± 0.5 | 57.1 ± 1.1 |
| SFT instead of RL | 29.9 ± 2.3 | 78.7 ± 1.9 | 1.1 ± 0.9 |
| Smaller Policy | 13.1 ± 0.9 | 11.4 ± 3.7 | 0.0 ± 0.0 |
| Without LoRA | 7.3 ± 5.2 | 40.9 ± 11.8 | 0.0 ± 0.0 |

![Figure 5 — Ablation on VLA, on-policy RL, and LoRA](https://arxiv.org/html/2603.11653/x8.png)

> "Figure 5: Ablation shows that VLA, on-policy RL, and LoRA are all crucial to avoid forgetting. Here, we show the retention curve for SFT to visualize the catastrophic forgetting that can occur." (§5.1)
(한글 해설 — 세 요소 중 무엇을 빼도 망각이 폭증함을 보이는 ablation 그림으로, SFT로 바꾸면 NBT가 78.7%까지 치솟는 붕괴를 시각화합니다.)

저자들은 메커니즘 분석을 정량 근거로 뒷받침합니다.

> "On the large OpenVLA-OFT model, the average $`E_{F}`$ is only 0.02, indicating very little interference between the task gradient and pretrained knowledge. However, on the small policy, $`E_{F}`$ jumps to 0.16, which likely explains the catastrophic forgetting that occurs with small models." (§5.1)
(한글 해설 — Fisher energy가 큰 모델 0.02 vs 작은 모델 0.16으로, 큰 사전학습 모델의 고차원 null space가 간섭을 줄인다는 가설의 정량 근거입니다.)

> "By contrast, LoRA (with rank 32) produces a nearly uniform pattern across layers: the mean effective rank is 29.3, with a tiny standard deviation of 2.16." (§5.1)
(한글 해설 — full fine-tuning의 layer별 effective rank 평균 208.6(표준편차 148.5)과 대비해, LoRA가 layer별 업데이트 기하를 균일하게 제약함을 보이는 수치입니다. nuclear norm도 0.259 vs 0.609로 LoRA가 더 낮습니다.)

저자들은 가소성 보존을 정보이론으로 설명합니다.

> "policy gradient methods such as GRPO learn based on the advantage function, which only provides O(1) bits of information for each episode under a sparse reward setup." (§5.2)
(한글 해설 — 희소 보상 RL은 에피소드당 O(1) 비트만 제공하므로, rank-32 LoRA의 약 100M 파라미터가 5만 rollout 정보를 흡수하기에 충분하다는 논거입니다. 반면 supervised 학습은 에피소드당 정보가 길이에 비례해 LoRA의 가소성을 잠식합니다.)

또한 가장 큰 AVG 격차(약 5%)를 보인 영역에서, 최저 성능 작업의 학습 에피소드를 두 배로 늘리는 것만으로 오라클과 동급에 도달했습니다(§5.4, Figure 6) — 격차가 국소 최적 함정 때문이 아님을 시사합니다.

---

## ⚖️ 한계

- **물리 로봇 검증 부재** — 모든 실험이 시뮬레이션(LIBERO, RoboCasa, ManiSkill) 기반이며, sim-to-real이나 real-world RL로의 확장은 향후 과제로만 언급됩니다.
- **작업 수·규모의 제약** — 벤치마크당 4–5개 작업의 비교적 짧은 연속 흐름이며, 수백 작업 규모의 장기 평생 학습까지 외삽되는지는 검증되지 않았습니다(ManiSkill은 실험 예산을 위해 4개 작업으로 제한).
- **ZS 우위의 미해결 설명** — Seq. FT가 오라클보다 일반화에서 일관된 우위를 보이는 현상을 저자도 "definitive explanation이 없다"며 implicit regularization 가설로만 남겨둡니다.
- **희소 보상·작업 정의 의존성** — O(1) 비트 가소성 논거는 희소 보상 설정에 묶여 있어, 밀집 보상이나 더 정보량 큰 보상 구조에서 결론이 유지될지는 불확실합니다.
- **세 요소 동시 충족 가정** — on-policy RL 단독으로는 불충분하며 큰 사전학습 모델·LoRA가 함께 필요하다고 명시하므로, 셋 중 하나라도 약화되면 결론이 깨집니다.

---

## ♻️ 재현성

- **코드** — `github.com/UT-Austin-RobIn/continual-vla-rl` 공개(초록·각주 명시). RLinf(Yu et al., 2025a) 인프라 위에 구축.
- **모델** — OpenVLA-OFT, Pi-0, OpenVLA 등 공개 VLA를 base로 사용.
- **벤치마크** — LIBERO(libero-object/spatial/long), RoboCasa, ManiSkill 등 공개 시뮬레이션 환경. 작업/held-out 분할과 자연어 지시가 §H에 명시.
- **하이퍼파라미터** — 공유·방법별 하이퍼파라미터가 §F–G(Table 6–7)에 표로 정리되어 재현 가능. 라이선스 CC BY 4.0.

---

## 🎯 관련 Pillar / Decision (P# / D#)

이 논문은 **P4(VLM Pretraining Preservation)** 와 §12 Cross-pollination Budget의 **Month A(continual learning / catastrophic forgetting / PEFT)** 축에 정면으로 닿습니다.

- **[D19] VLM fine-tuning range** — v1은 (a) full freeze이고 (d) LoRA는 deferred(트리거: 고정 백본 표현이 부족할 때)입니다. 본 논문은 "큰 사전학습 모델 + LoRA + on-policy RL"이 망각을 거의 일으키지 않는다는 직접 증거로, D19의 LoRA 경로가 prior 보존과 양립할 수 있음을 시사합니다.
- **[D20] Prior-preservation strategy** — D20은 D19가 freeze를 벗어나는 순간 활성화되는 standby 결정입니다. 본 논문의 forward-KL 암묵 정규화 논거(on-policy RL이 $`\pi_0`$ 지지 밖으로 질량을 급격히 못 옮김)는 D20이 발화했을 때 채택할 수 있는 메커니즘 후보입니다.
- **[D23] Action representation × VLM preservation** — 본 논문은 자기회귀 토큰형 VLA(OpenVLA/OFT)에서 적용한 RL이 주 무대지만, Flow-SDE로 flow-matching VLA(Pi-0)에도 동일 결론이 확장됨을 보입니다. 이는 v1 (iii) flow-matching head 선택과 RL post-training의 호환성을 뒷받침합니다.
- **Identity 긴장/지지** — PROBE Identity는 RL을 capability source가 아닌 deploy-ready fine-tuning(π RLT)으로 제한하고, RL의 유일한 자리를 System0 접촉 안정화로 좁힙니다. 본 논문은 RL을 "작업 적응 + 망각 억제"의 핵심 수단으로 쓰므로 Identity의 RL 범위 주장과는 긴장 관계입니다. 다만 본 논문의 RL은 작업 성공이라는 보상이 정의된 시뮬레이션 작업에 한정되며, generalized 다지 조작의 capability source 주장은 아니므로 직접 충돌은 아닙니다.
- **§10 경쟁자 함의** — §10.2 "Bounded RL-in-VLA precedents"(π RLT / RECAP, DexterityGen) 맥락의 watch trigger인 "RL-as-capability (not fine-tuning) 결과"에 부분적으로 닿습니다. 단, 본 논문은 사전학습 prior를 전제로 한 적응이므로 from-scratch capability 주장이 아닙니다.

이 논문은 P1·P2·P3의 아키텍처/입력/System0 결정에는 직접 닿지 않습니다.

---

## ✨ 핀 논문 대비 델타

- **VLM2VLA([arXiv:2509.22195]) 대비** — VLM2VLA는 supervised 환경에서 LoRA + NL-action으로 망각을 완화합니다. 본 논문은 같은 LoRA 축을 쓰되 **on-policy RL이 SFT보다 본질적으로 덜 망각한다**는 점(SFT 대체 시 NBT 0.3%→78.7%)을 추가해, 망각 억제가 PEFT만이 아니라 학습 목표(RL vs SFT)에서도 비롯됨을 분리합니다. P4 핀 중 RL 측면의 빈자리를 메웁니다.
- **π0 / π0.5([arXiv:2410.24164], [arXiv:2504.16054]) 대비** — π 핀들은 백본·flow-matching·계층 추론을 제공하지만 연속 RL 적응 과정에서 일어나는 망각을 정량화하지 않습니다. 본 논문은 Pi-0를 포함한 3개 VLA에서 NBT/ZS를 직접 측정해 "freeze 없이도 LoRA-RL이 prior를 지킨다"는 빈 데이터를 채웁니다.
- **MolmoAct2([arXiv:2605.02881]) 대비** — MolmoAct2는 구조적 장치(per-layer KV-cache conditioning)로 VLM을 보존합니다. 본 논문은 구조 변경 없이 **학습 동역학(고차원 null space + 저랭크 제약 + on-policy 암묵 KL)** 만으로 보존이 일어남을 보여 보존의 또 다른 축을 제시합니다.
- **동시기 직접 경쟁작** — 본문이 인용하는 Liu et al. (2026), "Pretrained VLAs are surprisingly resistant to forgetting in continual learning"([arXiv:2603.03818])은 거의 동일 주제의 concurrent work입니다. 본 논문은 여기에 **on-policy RL의 역할**과 세 요소 분해를 더한 점이 차별점입니다.

---

## ⚙️ 의사결정 함의

이 논문이 우리 스택에 맞다면, **D19를 freeze(a)에서 LoRA(d)로 옮기는 deferred 트리거가 발화했을 때의 안전성 근거**가 생깁니다. 구체적으로 다음이 바뀝니다.

- **D21 staged recipe의 Stage 3(LoRA/top-layer 제한 FT) 진입 비용 재평가** — 기존엔 Stage 2(freeze) plateau + 일반화 손실이 트리거였으나, 본 논문은 LoRA-RL이 일반화(ZS)를 오히려 키운다고 보고하므로 Stage 3 진입의 일반화 리스크를 낮춥니다.
- **구체 config 키** — LoRA를 도입한다면 `lora_rank = 32`, 학습률 `2e-5`, GRPO `clip_ratio = 0.20/0.28`, `kl_coef(β) = 0.0`, `group_size = 8`, `rollout_epochs = 16`(§F Table 6)을 출발점으로 삼는다. 특히 `β = 0.0`(명시적 KL 페널티 없음)은 "on-policy 샘플링 자체가 암묵적 KL 정규화"라는 본 논문 논거와 정합적입니다.
- **새 진단 지표 도입** — 망각 위험을 사전 진단하는 지표로 **Fisher energy $`E_{F}(\mathbf{g})`$** 와 **per-layer effective rank / nuclear norm**을 우리 ablation 계측에 추가한다. $`E_{F}`$ 가 0.02 수준이면 freeze 없이도 LoRA-FT가 prior를 지킬 가능성이 높다는 사전 신호로 쓴다.
- **P5 falsifier(D25)와의 연결** — "VLM-preservation을 full-FT 대비 일반화/OOD 미회귀로 검증"하는 D25 조건에, ZS 지표와 $`E_{F}`$ 계측을 구체 측정 절차로 채택한다.

모호하지 않게: 만약 우리가 LoRA-RL 경로로 이동한다면 위 하이퍼파라미터 세트 + $`E_{F}`$/effective-rank 진단 + ZS 추적이 첫 실험 설정의 기본값이 됩니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **on-policy 보상 정의 불가** — 본 논문의 망각 억제는 **작업 성공 보상이 정의된** 시뮬 작업에 의존합니다. PROBE의 generalized 다지 조작은 reward-engineerable하지 않으므로(Identity Antagonist B), RL-기반 망각 억제 메커니즘 자체가 우리의 주 학습 신호(flow-matching IL)에는 적용되지 않을 가능성이 있습니다. **가장 싼 sanity check**: 우리 파이프라인의 capability source는 RL이 아니라 IL이라는 점을 먼저 확인 — 이 논문의 결론은 "RL post-training 단계"에만 전이됩니다.
- **모델 규모 의존성** — 망각 억제가 큰 모델(7B OpenVLA-OFT)의 고차원 null space에 기댑니다(Fisher energy 0.02 vs 12M 모델 0.16). 우리의 action expert(π0 기준 0.315B 수준)나 System0 정책처럼 작은 모듈에서는 같은 보호가 작동하지 않을 우려가 있습니다. 싼 점검: 우리 action expert 규모에서 $`E_{F}`$ 를 측정해 0.02급인지 0.16급인지 먼저 확인합니다.
- **희소 보상 한정 가소성 논거** — O(1) 비트 논거는 희소 보상 가정이므로, System0의 밀집 보상(slip/접촉 안정성)에서는 에피소드당 정보량이 커져 LoRA 가소성 결론이 깨질 수 있습니다.
- **시뮬 한정 결과** — 모든 수치가 시뮬 기반이라 real-world RL의 분포 변화·노이즈에서 NBT < 2%가 유지될지는 미검증입니다.
- **다른 PEFT/백본 일반화** — LoRA rank 32와 GRPO 특정 설정에 묶인 결과로, 다른 PEFT나 백본 lineage(D19)에서 동일 시너지가 재현될지는 별도 확인이 필요합니다.

---

## 💡 컨텍스트 제안

- **§12 Cross-pollination Month A 후보로 기록 권장** — 본 논문은 "continual learning / catastrophic forgetting / PEFT (P4 adjacency)" 정의에 정확히 부합하는 이번 달 크로스폴리네이션 1편으로 적합합니다.
- **P4 핀 교체 검토 (deferred)** — 현재 P4 핀(8개)은 보존 *전략*에 치우쳐 있습니다. 본 논문(또는 동시기 [arXiv:2603.03818])은 "보존이 학습 동역학에서 자연 발생"하는 축을 대표하므로, 다음 분기 rebalance 시 RT-2처럼 비교적 오래된 핀과의 교체 후보로 검토합니다. (제안만 — `context/MASTER.md`는 수정하지 않습니다.)
- **D25 falsifier 측정 절차 보강 제안** — VLM-preservation 검증에 ZS 지표 + Fisher energy $`E_{F}`$ + per-layer effective rank를 정량 측정 항목으로 추가하는 안을 D26 평가 프로토콜 논의에 올립니다.

> 💡 base 매핑은 `/implement-design analysis/2603.11653/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
