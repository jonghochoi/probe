# Paper Analysis — Adaptive Capacity Allocation for Vision Language Action Fine-tuning

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Adaptive Capacity Allocation for Vision Language Action Fine-tuning |
| 저자 | Donghoon Kim, Minji Bae, Unghui Nam, Gyeonghun Kim, Suyun Lee, Kyuhong Shim, Byonghyo Shim |
| 링크 | [arXiv:2603.07404](https://arxiv.org/abs/2603.07404) |
| 발행일 / 버전 | 2026-03-08 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-07 |
| 관련 Pillar | P4, P1 |
| 태그 | peft, vla-arch, continual |

---

## 🧭 한 줄 요약 (TL;DR)

VLA 미세조정에서 LoRA의 핵심 손잡이인 rank는 언어모델과 달리 robotics 전이에서 훨씬 크고 (task·layer·모듈마다) 들쭉날쭉해, 단일 고정 rank가 구조적으로 부적합합니다. LoRA-SP(Select–Prune)는 고정 rank 대신 입력·레이어별로 capacity를 동적으로 할당하는 SVD-형 파라미터화 + router를 도입해, 누적 에너지 목표 $`\eta`$ 로 활성 rank를 자동 결정함으로써 $`\pi_0`$ ·SmolVLA 양 backbone에서 표준 LoRA 대비 multi-task 성공률을 최대 31.6%p 끌어올리며 full fine-tuning에 필적합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 사전학습된 VLA를 미지의 임바디먼트·작업·환경으로 전이할 때 PEFT(특히 LoRA)가 표준이지만, capacity를 결정하는 rank를 어떻게 정해야 하는지가 불명확합니다. 단일 고정 rank가 모든 상황에 최적이지 않다는 점을 해결하려 합니다.
- **기존 접근의 한계** — 언어모델 미세조정은 작은 rank($`r\in\{4,8\}`$)로 충분하지만, VLA 전이는 본질적 rank가 더 높고($`r\approx 128`$ 또는 near-full) task마다 달라, 고정 rank LoRA·LoRA-MoE·AdaLoRA 모두 일관된 우위를 내지 못합니다. 최적 rank를 찾으려면 grid search(brute sweep)에 의존해야 합니다.
- **본 논문의 가설** — 활성 rank를 입력·레이어별로 데이터 조건부로 할당하면, 이질적 작업이 공유 부분공간을 두고 경쟁(cross-task interference)하는 문제를 줄이고 positive transfer를 늘릴 수 있다는 것입니다.
- **왜 지금 중요한가** — 미지 임바디먼트(예: 사전학습에 없는 AgileX PiPER 팔)로의 전이는 kinematics·perception geometry·workspace scale을 모두 바꿔 요구 rank를 끌어올리며, multi-task 설정에서 이 mismatch가 악화됩니다. rank를 매번 sweep하는 비용이 rank-adaptive 프레임워크의 필요성을 부각합니다.

---

## 🧩 핵심 기여

- robotics 전이의 본질적 rank가 언어모델보다 높고 가변적임을 rank–성능 곡선과 gradient의 spectral 분석으로 실증하고, rank 선택을 spectral 근사 오차 $`\sqrt{1-E(k)}`$ 제어 문제로 정식화했습니다 (Eckart–Young–Mirsky 기반).
- 고정 rank 갱신 $`\Delta W = BA`$ 를 입력 조건부 SVD-형 $`\Delta W(x)=U\,\mathrm{diag}(s(x))\,V`$ 로 일반화하고, 작은 router가 비음(nonnegative) 점수를 singular value처럼 출력하는 **LoRA-SP**를 제안했습니다.
- 누적 제곱 점수 에너지 $`E(k)\ge\eta`$ 로 활성 vector 집합을 고르는 **Select** 단계와, spectral loss $`\mathcal{L}_{\text{spec}}=1-E_k(x)`$ 로 에너지를 소수 방향에 집중시키는 **Prune** 단계를 결합했습니다.
- 미지 7-DoF AgileX PiPER 팔에서 수집한 4개 실로봇 조작 작업· $`\pi_0`$ ·SmolVLA 두 backbone에서, 표준 LoRA 대비 multi-task 성공률을 $`\pi_0`$ 23.3%p·SmolVLA 31.6%p 개선하고 full FT에 필적 또는 상회함을 보였습니다.
- 모듈별로 요구 rank가 크게 다름(vision tower 高 / language·action 低)을 layer-wise 분포로 시각화해, 단일 global rank의 한계와 적응적 할당의 이점을 정량화했습니다.

---

## 🔑 기술 키워드

- **LoRA (Low-Rank Adaptation)** — 가중치 갱신을 저차원 곱 $`\Delta W=BA`$ 로 제약하는 표준 PEFT. 본 논문이 일반화하는 출발점이며 주 baseline입니다.
- **Intrinsic dimension / intrinsic rank** — 목표 성능을 내는 데 필요한 최소 갱신 capacity. 본 논문은 robotics 전이의 본질적 rank가 언어보다 높고 가변적이라는 점을 핵심 동기로 삼습니다.
- **Rank-adaptive fine-tuning** — 고정 rank 대신 데이터·레이어 조건부로 활성 rank를 바꾸는 미세조정 패러다임. LoRA-SP의 정체성입니다.
- **SVD-style parameterization** — $`U\,\mathrm{diag}(s(x))\,V`$ 처럼 좌우 basis와 대각 점수로 갱신을 표현하는 형태. router 점수가 데이터 조건부 singular value 역할을 합니다.
- **Router / vector-level gating** — 입력별로 각 basis vector의 점수를 내는 경량 2-layer MLP. MoE의 expert 단위가 아니라 vector 단위로 게이팅해 활성 rank를 세밀하게 조절합니다.
- **Cumulative spectral energy** — 상위 $`k`$ singular value의 누적 제곱 에너지 $`E(k)`$. 활성 집합 크기와 근사 오차를 직접 잇는 지표입니다.
- **Energy target (η)** — 활성 rank를 결정하는 누적 에너지 임계값. 근사 오차의 명시적 tolerance 손잡이로, accuracy–efficiency 균형을 직접 조정합니다.
- **Spectral loss** — $`\mathcal{L}_{\text{spec}}=1-E_k(x)`$. 선택된 vector에 에너지를 집중시켜 활성 rank를 점진적으로 줄이는 정규화 항입니다.
- **Cross-task interference** — 이질적 작업이 공유 adapter 부분공간을 두고 경쟁해 성능이 저하되는 현상. 고정 rank 공유의 핵심 실패 모드입니다.
- **Eckart–Young–Mirsky theorem** — 절단 SVD가 Frobenius norm 기준 최적 저차원 근사임을 보장하는 정리. rank–오차 연결의 이론적 근거입니다.

---

## 🔬 방법론

### 직관

![Figure 1 — Rank–performance curves: LLM vs VLA](https://arxiv.org/html/2603.07404/x1.png)

> "Figure 1: Rank–performance curves (accuracy/success relative to full fine-tuning; 1.0 = full FT). LLM (LLaMA-7B) reaches near-full-FT performance with very small ranks ($`r\in\{4,8\}`$), whereas VLA ($`\pi_{0}`$-3.5B) improves steadily and only approaches parity around $`r\approx 128`$, consistent with a higher intrinsic dimension in the VLA transfer setting." (§I)
(한글 해설 — 언어모델은 작은 rank로 full FT에 도달하지만 VLA는 $`r\approx 128`$ 까지 올라가야 한다는, 본 논문 전체의 동기를 한 장에 못 박는 그림입니다.)

핵심 직관은 "rank를 고른다는 것은 곧 spectral 근사 오차를 통제하는 것"이라는 관찰입니다. VLA 전이는 본질적 rank가 높고 task·모듈마다 달라 단일 고정 rank가 부적합하므로, 입력·레이어별로 필요한 만큼의 방향만 활성화하면 효율과 정확도를 동시에 잡을 수 있다는 것입니다.

> "We generalize this low-rank form by replacing $`BA`$ with SVD-style parameterization $`U\,\mathrm{diag}(s(x))\,V`$ where $`U`$ and $`V`$ define a vector bank (basis) and the router outputs nonnegative singular-value-like scores $`s(x)\in\mathbb{R}^{r}`$." (§I)
(한글 해설 — 고정 rank 곱 $`BA`$ 를 좌우 basis bank + 데이터 조건부 점수로 분해하는 것이 LoRA-SP의 설계 핵심임을 명시합니다.)

### 아키텍처

![Figure 5 — LoRA-SP (Select–Prune) overview](https://arxiv.org/html/2603.07404/x5.png)

> "Figure 5: LoRA-SP (Select–Prune). (I) Overview: a wide vector bank $`(U,V)`$ is trained together with a router on the backbone $`W_{0}`$. (II) Select: the router produces vector-level scores that act as singular values, forming an input- and layer-conditioned update $`\Delta W=U\,\Sigma(x)\,V`$; the histogram illustrates the spectral energy distribution across vectors. (III) Prune: only the smallest set of basis vectors whose cumulative energy exceeds the target $`\eta`$ are kept, progressively reducing the active rank while maintaining accuracy." (§III-B)
(한글 해설 — wide bank 학습 → vector별 점수 산출(Select) → 누적 에너지 임계로 활성 집합 절단(Prune)의 3단계 파이프라인을 한 장에 담은 메서드 개요입니다.)

- **입력** — 레이어 입력 $`x\in\mathbb{R}^{d_{\text{in}}}`$ (각 모듈의 활성화). backbone 가중치 $`W_0`$ 는 동결.
- **Vector bank** — 모듈별 $`U\in\mathbb{R}^{d_{\text{out}}\times r}`$, $`V\in\mathbb{R}^{r\times d_{\text{in}}}`$, 초기 rank $`r=128`$ (wide initialization).
- **Router** — 2-layer MLP. $`h_1(x)=\phi(W_1 x+b_1)`$, $`s(x)=W_2 h_1(x)+b_2\in\mathbb{R}^{r}_{\ge 0}`$ (비음 점수).
- **갱신** — $`\Sigma(x)=\mathrm{diag}(s(x))`$, $`\Delta W(x)=U\,\Sigma(x)\,V`$. 순방향은 $`(W_0+\Delta W(x))x = W_0 x + U\,\Sigma(x)\,V x`$.
- **활성 집합 선택** — 점수를 $`s_i(x)^2`$ 기준 내림차순 정렬 후 누적 에너지가 $`\eta`$ 를 넘는 최소 $`k`$ 까지만 유지, 나머지는 0으로 절단.
- **출력** — 입력·레이어별로 활성 rank $`k`$ 가 달라지는 적응적 저차원 갱신.

### 학습 목표 / 손실

활성 rank 선택의 근거가 되는 spectral 항등식 (Eckart–Young–Mirsky):

$$\frac{\|A-A_{k}\|_{F}}{\|A\|_{F}} = \sqrt{\,1-E(k)\,}$$

> "if $`E(k)`$ denotes the cumulative energy of the top-$`k`$ singular values (Eq. 3), then the best rank-$`k`$ approximation achieves error $`\sqrt{1-E(k)}`$ (Eq. 4). Thus, choosing ranks in LoRA is equivalent to controlling these spectral error." (§III-A)
(한글 해설 — rank 선택이 곧 상대 Frobenius 근사 오차 통제와 동치임을 보이는 핵심 명제로, $`\eta`$ 가 오차 tolerance 손잡이가 되는 근거입니다.)

누적 에너지 정의:

$$E_{k}(x)=\frac{\sum_{i=1}^{k}s_{i}(x)^{2}}{\sum_{j=1}^{r}s_{j}(x)^{2}}$$

> "The effective rank $`k`$ is chosen as the smallest index satisfying $`E_{k}(x)\geq\eta`$, and the singular values beyond $`k`$ are zeroed. Because $`E_{k}(x)`$ bounds the relative approximation error as $`\sqrt{1-E_{k}(x)}`$ (Eq. 4), $`\eta`$ serves as an explicit tolerance knob (e.g., $`\eta=0.99`$ implies $`\leq 0.1`$ error)." (§IV-C)
(한글 해설 — $`\eta`$ 가 클수록 더 많은 vector를 살려 오차를 줄이고, 작을수록 활성 rank를 공격적으로 줄입니다.)

Spectral loss:

$$\mathcal{L}_{\text{spec}}(x)=1-E_{k}(x)$$

> "This creates a reinforcement loop: once a vector is selected, $`\mathcal{L}_{\text{spec}}`$ pushes its singular value higher, making it even more likely to be selected again. Over training, singular-value mass is gradually shifted toward a small stable set of directions, while the task loss prevents collapse to trivial solutions." (§IV-D)
(한글 해설 — 선택된 방향의 점수를 키우는 양의 피드백 루프로, 학습이 진행될수록 에너지가 소수 안정 방향에 집중되어 활성 rank가 줄어듭니다. 붕괴는 task loss가 막습니다.)

전체 손실:

$$\mathcal{L} = \mathbb{E}[\mathcal{L}_{\text{task}}] + 10^{-2}\,\mathbb{E}[\mathcal{L}_{\text{spec}}] + 10^{-3}\,\mathbb{E}[\mathcal{L}_{\text{router}}]$$

> "where $`\mathcal{L}_{\text{task}}`$ is the main objective (e.g., flow matching), and $`\mathcal{L}_{\text{router}}`$ includes balance [8] and $`z`$-loss [25] terms." (§IV-E)
(한글 해설 — main task loss는 flow matching이며, spectral·router 정규화는 각각 $`10^{-2}`$ · $`10^{-3}`$ 의 작은 가중치로 더해집니다. router loss는 Switch Transformer balance loss + z-loss로 구성됩니다.)

### 학습 셋업

- **Backbone** — $`\pi_0`$ (PaLIGemma 기반, 3.5B 규모) 및 SmolVLA (SmolVLM-2 기반). 두 backbone 모두에 동일 조건으로 LoRA-SP 적용.
- **하이퍼파라미터** — 초기 rank $`r=128`$, 에너지 목표 $`\eta=0.9`$, spectral loss 가중치 $`10^{-2}`$, router loss 가중치 $`10^{-3}`$.
- **데이터** — AgileX PiPER 7-DoF 팔로 human teleoperation 수집. 4개 작업 × 120 episode = 총 480 시연. 작업별 side-view + wrist-mounted 두 RGB 카메라.
- **비교 baseline** — Full FT, 표준 LoRA($`r=128`$), LoRA-MoE(top-1 / weighted-sum), AdaLoRA. 모두 동일 조건에서 학습.
- (옵티마이저·스케줄·학습 step 등 세부는 원문에 명시 없음.)

---

## 📊 실험 설정과 결과

평가는 4개 실로봇 작업(Open / Pour / Press / Pick-Place)의 task 성공률(%)이며, single-task·multi-task 두 학습 체제로 측정합니다.

**Table I — multi-task 성공률 (활성 rank·학습 파라미터 비율 포함, 발췌)**

| Backbone | Strategy | Trainable/Total (%) | Active Rank | Open | Pour | Press | Pick-Place |
|---|---|---|---|---|---|---|---|
| $`\pi_0`$ | LoRA ($`r=128`$) | 9.1 | 128 | 73.3 | 26.7 | 80.0 | 60.0 |
| $`\pi_0`$ | LoRA-MoE (weighted) | 9.2 | 128 | 46.7 | 60.0 | 93.3 | 80.0 |
| $`\pi_0`$ | AdaLoRA | 9.1 | 76 | 20.0 | 6.7 | 40.0 | 60.0 |
| $`\pi_0`$ | Full FT | 100.0 | Full | 80.0 | 86.7 | 80.0 | 86.7 |
| $`\pi_0`$ | **LoRA-SP** | 9.2 | 76 | 80.0 | 80.0 | 93.3 | 80.0 |
| SmolVLA | LoRA ($`r=128`$) | 17.0 | 128 | 40.0 | 20.0 | 93.3 | 86.7 |
| SmolVLA | LoRA-MoE (weighted) | 17.2 | 128 | 60.0 | 80.0 | 100.0 | 66.7 |
| SmolVLA | AdaLoRA | 17.0 | 60 | 6.7 | 0.0 | 40.0 | 20.0 |
| SmolVLA | Full FT | 100.0 | Full | 73.3 | 86.7 | 100.0 | 86.7 |
| SmolVLA | **LoRA-SP** | 17.1 | 60 | 86.7 | 86.7 | 100.0 | 93.3 |

> "It improves average success rates over standard LoRA by 23.3% on $`\pi_{0}`$ and 31.6% on SmolVLA, while often matching the performance of full fine-tuning." (§V-B, Table I)
(한글 해설 — 표준 LoRA 대비 평균 성공률을 $`\pi_0`$ 23.3%p·SmolVLA 31.6%p 끌어올리며, 더 작은 활성 rank(76 / 60)로 full FT에 필적합니다.)

> "While the success rate in single-task training improves with the rank, that in multi-task training collapses regardless of ranks." (§V-B, Table II)
(한글 해설 — single-task에서는 rank를 키우면 성능이 오르지만, multi-task에서는 rank를 아무리 키워도 붕괴합니다. task별 최적 rank 차이 + 공유 부분공간 간섭이 원인으로 분해됩니다.)

**Table IV — energy target $`\eta`$ ablation ($`\pi_0`$, multi-task)**

| $`\eta`$ | Active Rank | Open | Pour | Press | Pick-Place |
|---|---|---|---|---|---|
| 0.5 | 30 | 6.7 | 13.3 | 93.3 | 13.3 |
| 0.7 | 46 | 53.3 | 80.0 | 100.0 | 53.3 |
| 0.8 | 56 | 80.0 | 86.7 | 100.0 | 60.0 |
| 0.9 | 60 | 86.7 | 86.7 | 100.0 | 93.3 |
| 0.99 | 114 | 80.0 | 86.7 | 100.0 | 100.0 |

> "performance saturates around $`\eta=0.9`$, and setting $`\eta=0.99`$ nearly doubles the effective rank with marginal additional gains." (§V-C, Table IV)
(한글 해설 — $`\eta`$ 를 키울수록 활성 rank가 커지지만 성능은 $`\eta=0.9`$ 부근에서 포화하며, $`\eta=0.99`$ 는 rank를 60→114로 거의 두 배로 키우고도 이득이 미미합니다. $`\eta`$ 가 accuracy–efficiency 균형의 직접 손잡이임을 확인합니다.)

![Figure 6 — Layer-wise active rank distribution](https://arxiv.org/html/2603.07404/x6.png)

> "Figure 6: Layer-wise distributions of active rank learned by LoRA-SP on validation data. ... The vision tower consistently requires the highest ranks, the action expert shows wide variability, while the language model layers remain comparatively low and stable." (§V-A)
(한글 해설 — vision tower는 일관되게 높은 rank, action expert는 변동 폭이 크고, language model은 낮고 안정적입니다. 모듈별 capacity 이질성이 단일 global rank의 한계를 드러냅니다.)

**Table III — spectral loss ablation (활성 rank V, L, A = vision, language, action)**

> "removing the spectral loss significantly increases active rank, especially in the language module where the active rank rises from 35 to 107." (§V-C, Table III)
(한글 해설 — spectral loss 제거 시 활성 rank가 (84, 35, 34)→(83, 107, 57)로 특히 language 모듈에서 급증하고 성공률도 떨어집니다. spectral loss가 task-무관 방향을 잘라 효율과 성능을 동시에 지킵니다.)

---

## ⚖️ 한계

- **실험 규모가 작음** — 4개 작업·단일 임바디먼트(AgileX PiPER)·작업당 120 episode로, 다양한 임바디먼트/대규모 작업군으로의 일반화는 미검증입니다.
- **성공률 분산** — 작업당 평가 횟수(15회 추정, 성공률이 6.7% 단위)가 작아 수치 변동이 큽니다. 통계적 유의성·표준편차 보고가 없습니다.
- **추론 비용 주장 미정량** — "compact adapter가 inference cost를 낮춘다"고 했으나 실측 지연/메모리 수치는 제시되지 않습니다(활성 rank가 입력별로 변하는 동적 게이팅의 실제 런타임 이득은 별도 검증 필요).
- **router 하이퍼 민감도** — balance loss·z-loss 가중치, $`\phi`$ 활성화, router 폭 등 세부가 본문에 충분히 명시되지 않아 재현 시 sweep 부담이 남습니다.
- **다른 PEFT와의 비교 폭** — DoRA·VeRA 등 다른 rank-적응/저메모리 PEFT와의 비교는 없습니다.

---

## ♻️ 재현성

- **코드** — 공개 저장소 링크가 본문/메타에 명시되지 않았습니다(GitHub·프로젝트 페이지 미발견).
- **데이터** — 자체 수집 실로봇 시연(480 episode, AgileX PiPER). 공개 여부 언급 없음.
- **하드웨어** — AgileX PiPER 7-DoF 팔, side-view + wrist RGB 2-카메라. backbone은 공개 $`\pi_0`$(openpi 계열)·SmolVLA로 접근 가능.
- **핵심 하이퍼** — 초기 rank 128, $`\eta=0.9`$, spectral/router 가중치 $`10^{-2}`$/$`10^{-3}`$ 는 명시되어 재구현의 출발점은 확보됩니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P4 (VLM Pretraining Preservation) — 핵심 연결.** D19(VLM FT range)에서 명시한 선택지 중 `(c) LoRA-adapter` 경로를 정면으로 다룹니다. 현재 v1은 `(a) full freeze + action experts only`이지만, P4 Decision Log는 Stage 3로 LoRA를 deferred 후보로 둡니다(D21). 본 논문은 그 deferred 경로를 실로봇· $`\pi_0`$ 에서 정량화한 자료입니다.
- **D20 (prior-preservation strategy)** — LoRA-SP의 "cross-task interference 감소 → generalization 향상" 주장은 prior 보존의 한 메커니즘(공유 부분공간 오염 억제)으로 읽힙니다. 다만 본 논문은 backbone forgetting/prior 보존을 직접 측정하지 않고 multi-task 성공률만 봅니다 — 보존 효과는 간접 추정입니다.
- **D23 (action-rep × VLM preservation)** — task loss를 "e.g., flow matching"으로 두어 우리 v1(iii) 연속 flow-matching head와 정합합니다. LoRA-SP는 action head 형태와 직교(orthogonal)하게 adapter 층에만 작용하므로 D23 선택을 바꾸지 않습니다.
- **P1 (Heterogeneous Body/Hand Action Expert) — 부차적.** Fig.6의 "vision tower 高-rank / action expert 변동 / language 低-rank" 모듈별 capacity 이질성은, action-side adapter를 어디에 얼마나 둘지(D4/D7 split-as-adapter) 결정에 직접적 증거가 됩니다.
- **경쟁자 함의 (P4 §7)** — baseline에 든 AdaLoRA·LoRA-MoE는 우리가 추적하는 PEFT 계열이며, 본 논문은 "LLM 기반 importance score(AdaLoRA)가 VLA 적응에 misalign"한다는 반례를 제공합니다. ConSFT(conservative SFT, π0-tested)와는 보완 관계 — 한쪽은 adapter capacity 할당, 다른 쪽은 full-SFT trust-region 보존.

---

## ✨ 핀 논문 대비 델타

- **vs VLM2VLA (핀, [arXiv:2509.22195](https://arxiv.org/abs/2509.22195))** — VLM2VLA는 모든 linear 모듈에 *고정 rank* LoRA + NL-action으로 forgetting을 완화합니다. LoRA-SP의 진정한 새로움은 rank를 고정하지 않고 **입력·레이어별로 활성 rank를 데이터 조건부로 자동 할당**하고, 그 선택을 spectral 근사 오차($`\eta`$)에 이론적으로 묶었다는 점입니다 — "어떤 rank를 쓸지"를 hyperparameter sweep에서 학습 가능한 router로 옮겼습니다.
- **vs ConSFT (핀, [arXiv:2605.08879](https://arxiv.org/abs/2605.08879))** — ConSFT는 full-SFT 위에 conservative importance weighting(trust region)으로 ~20%p forgetting을 줄입니다. LoRA-SP는 PEFT(저파라미터) 영역에서 cross-task interference를 capacity 할당으로 줄이는, 직교적 축입니다. 둘은 "보존을 어디서 거는가"(파라미터 budget vs 갱신 방향)가 다릅니다.
- **vs π0/π0.5 (핀)** — backbone을 그대로 쓰되 미지 임바디먼트(PiPER) 전이에서 frozen-backbone+고정 adapter가 부족함을, rank 측면에서 처음으로 spectral 분석으로 진단합니다.
- **새로움의 핵심** — robotics 전이의 본질적 rank가 (i) 언어보다 높고 (ii) 모듈·task·임바디먼트마다 가변적이라는 **측정된 사실**과, 이를 다루는 **vector-level(여기서 활성 rank를 token·layer별로 조절) 게이팅 + spectral loss** 조합. 기존 핀 중 어느 것도 활성 rank를 입력 조건부로 동적 할당하지 않습니다.

---

## ⚙️ 의사결정 함의

이 논문이 맞다면 우리 파이프라인에서 바뀌는 것:

- **D19 LoRA 경로를 켤 경우 고정 rank를 쓰지 말 것.** 만약 Stage 3(LoRA)로 가면, 단일 `lora_rank`(예: 16/32) 대신 초기 `r=128` + energy target `eta=0.9` 의 LoRA-SP 식 동적 할당을 우선 후보로 둡니다. 즉 새 config 키 `peft.energy_target (η)`·`peft.init_rank (r)`·`peft.spectral_loss_weight (1e-2)`·`peft.router_loss_weight (1e-3)` 가 추가됩니다.
- **모듈별 차등 capacity.** Fig.6 근거로, vision tower에 높은 rank·language/action expert에 낮은 rank를 배정하는 것이 효율적입니다. 우리 split-heads(D4/D7)를 adapter로 쓸 때 action expert 쪽 rank를 굳이 크게 잡을 필요가 없다는 사전(prior)을 줍니다.
- **손실 항 추가.** task loss(flow matching)에 `L_spec = 1 - E_k(x)`(가중치 $`10^{-2}`$)와 router balance+z-loss(가중치 $`10^{-3}`$)를 더합니다. flow-matching head와 충돌하지 않습니다(D23 유지).
- **평가 지표.** multi-task 성공률뿐 아니라 **활성 rank(per-token 평균)**를 효율 지표로 함께 로깅 — accuracy–efficiency trade-off를 $`\eta`$ sweep 없이 추적할 수 있습니다.
- **baseline 정리.** AdaLoRA를 우리 PEFT 후보에서 우선순위 하향 — VLA에서 LLM-기반 importance score가 misalign한다는 반례 확보.

---

## ⚠️ 먼저 검증할 실패 모드

- **가장 싼 sanity check — 단일 임바디먼트·소규모(4 task) 결과의 통계적 견고성.** 작업당 평가 횟수가 작아 31.6%p 개선이 분산에 묻힐 수 있습니다. 우리 셋업에서 채택 전, seed·평가 횟수를 늘려 표준편차를 먼저 확인합니다.
- **동적 게이팅의 런타임 비용.** 입력별로 활성 rank가 달라지면 batched inference에서 sparsity를 살리기 어려워 실제 지연이 고정 rank보다 나빠질 수 있습니다. 우리 실시간 제어 루프(System1/System0 control rate)에서 wall-clock을 먼저 측정해야 합니다 — "compact = 빠름"이 자동 성립하지 않습니다.
- **router 추가 학습의 불안정성.** balance/z-loss·spectral loss가 flow-matching task loss와 경쟁하면 수렴이 흔들릴 수 있습니다. 작은 데이터(우리 초기 demo)에서 router collapse(소수 vector로 조기 붕괴) 여부를 모니터링합니다.
- **prior 보존의 간접성.** 본 논문은 multi-task 성공률만 보고 backbone forgetting을 직접 측정하지 않습니다. 우리 P4 관심사(VLM prior 보존)에 쓰려면, LoRA-SP 적용 후 VLM 일반 능력(예: 언어/시각 prior) 저하를 별도 측정해야 — 성공률 개선이 보존을 보장하지 않습니다.
- **backbone 의존성.** $`\pi_0`$ ·SmolVLA에서만 검증됐고, 우리가 쓸 $`\pi_0/\pi_{0.5}`$(openpi) 정확 버전·모듈 구조에서 spectral rank 분포가 다를 수 있습니다.

---

## 💡 컨텍스트 제안

- **P4 §7 Competitor / Kindred Monitoring 추가 후보** — LoRA-SP를 "rank-adaptive PEFT" 항목으로 추적 등재 검토. overlap: PEFT로 cross-task interference 완화 / difference: 우리 frozen-backbone+split-heads 대비 동적 adapter capacity / watch trigger: 코드 공개 시 추론 비용 실측·다임바디먼트 일반화 결과. (현재 핀 8개 cap이 차 있어 §7 추적 행으로만 제안.)
- **D21 Stage 3(LoRA) 메모 보강 후보** — "LoRA로 갈 경우 고정 rank가 아니라 energy-target 기반 동적 할당(LoRA-SP)을 우선 검토"라는 단서를 deferred 후보 설명에 덧붙이는 것을 제안합니다.
- 위는 모두 사람 결정용 제안이며, 어떤 context/ 파일도 본 분석에서 수정하지 않았습니다.
