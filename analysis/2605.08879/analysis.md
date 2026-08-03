# Paper Analysis — Preserving Foundational Capabilities in Flow-Matching VLAs through Conservative SFT

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Preserving Foundational Capabilities in Flow-Matching VLAs through Conservative SFT |
| 저자 | Tianyi Zhang, Shaopeng Zhai, Haoran Zhang, Fuxian Huang, Qi Zhang (Shanghai Artificial Intelligence Laboratory) |
| 링크 | [arXiv:2605.08879](https://arxiv.org/abs/2605.08879) |
| 발행일 / 버전 | 2026-05-09 · v2 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-05-26 |
| 관련 Pillar | P4, P1 |
| 태그 | forgetting, flow-matching, vla-arch |

---

## 🧭 한 줄 요약 (TL;DR)

ConSFT 는 flow-matching VLA 의 SFT 손실에 $`\omega=\exp(-\mathcal{L}_{\mathrm{SFT}}/\tau)`$ 라는 per-sample 신뢰도 가중치를 stop-gradient 로 곱하는 SFT 변형. 참조 네트워크나 사전 데이터 없이도 PPO trust-region 에 맞먹는 sparse update 로 catastrophic forgetting 을 완화한다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — flow-matching VLA ($`\pi_{0}`$, $`\pi_{0.5}`$, GR00T-N1.6-3B) 를 downstream task 에 vanilla SFT 로 fine-tune 하면 사전학습 능력이 평균 40~60% 절대 성공률로 무너지는 catastrophic forgetting 이 발생한다.
- **기존 접근의 한계** — Experience Replay 는 사전학습 corpora 접근(통상 비공개) 이 필요하고, KL Regularization (LwF) / FPO 류는 active·reference 네트워크를 병렬로 돌려야 해 메모리·연산이 두 배이며, LoRA 는 plasticity 를 깎는다. PPO 의 trust-region clip 은 잘 듣지만 flow-matching 의 closed-form likelihood 부재 탓에 probability-flow ODE 적분을 매 스텝 풀어야 한다.
- **본 논문의 가설** — RL 의 forgetting 완화는 advantage 가중이 아니라 *trust-region clip 으로 인한 parameter update sparsity* 자체에서 온다. 결국 SFT 손실에 confidence 기반 scalar 가중만 곱해도 같은 sparse-update 동역학을 재현할 수 있다는 것.
- **왜 지금 중요한가** — π0 계열 flow-matching VLA 가 사실상 표준 백본이 된 지금, 사전학습 데이터 없이 prior 를 보존하는 SFT 처방은 P4(VLM Pretraining Preservation) 의 가장 중요한 미해결 과제 (D19~D23) 와 바로 그 지점을 짚는다.

---

## 🧩 핵심 기여

- flow-matching VLA 에서 catastrophic forgetting 이 *dense parameter overwrite* 와 상관관계가 있음을 실증하고, PPO clipping 이 >99% layer sparsity 를 유도해 능력을 보존함을 보였다 (Table 1, Figure 1).
- Flow Policy Optimization 의 exponential loss-difference 근사로 trust-region 의 importance ratio 를 SFT 안으로 가져와, "ideal expert 의 손실은 0" 이라는 oracle 치환과 stop-gradient 로 ConSFT 목적 (Eq. 5) 을 유도.
- Fisher Information Matrix 기반 forgetting risk 가 $`\omega^{2}`$ 로 quadratic 하게 감쇠한다는 분석적 상한 (Eq. 7) 을 제시하고, demonstration noise 가 있어도 global scalar 로 흡수돼 동역학이 깨지지 않음을 Appendix B 에서 보였다.
- 세 backbone × 두 벤치마크 (LIBERO, RoboTwin) 마다 target task 수행은 vanilla SFT 와 동률 이상이면서 prior retention 평균을 20% 절대 마진으로 끌어올렸고, prior-data-free 라는 점에서 ER 을 능가했다 (Table 2, 3).
- 실물 $`\pi_{0.5}`$ + 단일팔 테스트튜브 전이 과제에서 vanilla SFT 가 보이는 z-축 spatial drift (gripper 가 너무 높은 위치에서 닫히는 현상) 가 ConSFT 에서는 사라짐을 case study 로 제시.

---

## 🔑 기술 키워드

- **Flow-Matching VLA** — 연속시간 vector field 를 회귀해 action chunk 를 생성하는 VLA. $`\pi_{0}`$, $`\pi_{0.5}`$, GR00T 가 채택. 이산 토큰 정책과 달리 $`\log\pi`$ 가 closed-form 으로 나오지 않는다.
- **Catastrophic Forgetting** — downstream fine-tuning 동안 사전학습 능력이 무너지는 현상. 본 논문에서는 LIBERO-Object 같은 held-out 스위트 성공률이 58%→2% 로 떨어지는 식.
- **Trust Region / PPO Clipping** — importance ratio $`r(\theta)`$ 를 $`[1-\epsilon, 1+\epsilon]`$ 구간 밖에서 잘라 파라미터 이탈을 막는 RL 안전벨트. 본 논문이 모방하려는 동역학의 원본.
- **Parameter Update Sparsity** — 사전학습 가중치 대비 상대 변화가 임계값 $`\delta`$ 이하인 파라미터 비율 (Eq. 8). >99% 면 layer 가 거의 그대로라는 의미.
- **Conservative Importance Weight** — $`\omega = \exp(-\mathcal{L}_{\mathrm{SFT}}/\tau)`$. 모델이 자신 없는(loss 가 큰) 샘플의 그래디언트를 지수적으로 죽여 무절제한 업데이트를 차단하는 스칼라 게이트.
- **Stop-Gradient (sg)** — $`\omega`$ 를 미분 대상에서 빼 weight 처럼 다루기 위한 연산. 가중치 자체가 학습 목표가 되는 것을 막는다.
- **Forgetting Risk (FIM-quadratic)** — $`\mathcal{R}(g)=g^{\top} F g`$. Fisher Information $`F`$ 가 양의 준정부호라는 사실만으로 $`\omega`$ 배 그래디언트는 risk 를 $`\omega^{2}`$ 배로 줄인다는 정량적 상한.
- **Temperature Annealing** — $`\tau`$ 를 학습 진행에 따라 단조 증가시켜 후반에는 vanilla SFT 로 복귀시키는 스케줄 (Eq. 11, 12). 초반 보수성, 후반 적응성.
- **Experience Replay (ER) / LwF / LoRA** — anti-forgetting 비교군. 각각 사전 데이터 버퍼, KL/MSE 정규화, low-rank 어댑터.

---

## 🔬 방법론

### 직관

ConSFT 의 출발 직관은 "RL 이 SFT 보다 덜 잊는 진짜 이유는 advantage 가 아니라 *trust-region clip* 으로 인한 업데이트의 구조적 sparsity" 라는 관찰 (§3.2, Table 1). 그런데 flow-matching 정책은 closed-form likelihood 가 없어 PPO clip 을 그대로 못 쓴다. 저자들은 FPO 류의 exponential-loss-difference 근사로 importance ratio 를 우회하고, SFT 가 "이상적 전문가 분포 ($`\mathcal{L}_{\mathrm{behavior}}=0`$)" 라고 가정하면 ratio 가 $`\exp(-\mathcal{L}_{\mathrm{SFT}}/\tau)`$ 한 줄로 정리됨을 보인다. 이 스칼라를 stop-gradient 로 곱해 두면 자신 없는 샘플의 학습 신호가 지수적으로 죽고, FIM-quadratic 으로 정의한 forgetting risk 는 $`\omega^{2}`$ 배로 자동 감쇠한다.

> "Our empirical ablation isolates the explicit trust-region constraint, rather than advantage weighting or on-policy sampling alone, as the indispensable stabilizer in flow-matching action spaces." (§3.2)
> (clip 자체가 stabilizer 라는 게 ConSFT 의 설계 근거 — advantage 가 아니라 boundary 가 가장 중요한 축이다.)

### 아키텍처

ConSFT 는 백본을 건드리지 않는다. 학습 루프 안의 손실 한 줄 교체로 충분하다.

- **입력 / 출력** — 기존 flow-matching VLA ($`\pi_{0}`$ / $`\pi_{0.5}`$ / GR00T-N1.6-3B) 의 입출력 그대로. 추가 모듈·참조 네트워크·버퍼 없음.
- **per-sample loss head** — minibatch 의 샘플마다 표준 flow-matching loss $`\mathcal{L}_{\mathrm{SFT}}(\theta)`$ 를 먼저 계산한다.
- **conservative weight gate** — 같은 손실 값에 stop-gradient 를 씌운 뒤 $`\omega = \exp(-\mathcal{L}_{\mathrm{SFT}}(\theta)/\tau(t))`$ 를 산출. 학습 그래프상 leaf scalar 로만 들어간다.
- **temperature scheduler** — 전역 step $`t`$ 와 총 step $`T`$ 로 정규화된 decay factor $`\rho(t)`$ (Eq. 11) → 동적 온도 $`\tau(t)=\min(\tau_{\mathrm{start}}/\max(\rho(t),\epsilon),\tau_{\mathrm{end}})`$ (Eq. 12). 후반에는 $`\omega \to 1`$ 로 수렴해 vanilla SFT 와 같아진다.
- **분산 학습** — 8× A100 (80GB) FSDP, global batch 1024, micro 32/GPU. 추가 메모리 오버헤드 0.

![Figure 1 — Sparsity across SFT / PPO-NoClip / PPO](https://arxiv.org/html/2605.08879/x1.png)

> "Figure 1: Parameter update sparsity across optimization objectives. (Left) Global sparsity progression. Trust-region constraints (PPO) reduce the update scope compared to unconstrained SFT. (Right) Layer-wise sparsity profiles. PPO yields $`>99\%`$ sparsity in core Attention and MLP weights." (§3.3)
> (RL forgetting 완화의 인과가 advantage 가 아니라 sparsity 라는 본 논문의 으뜸 관찰을 시각화한 그림.)

### 학습 목표 / 손실

표준 SFT 손실은 모든 샘플에 균일한 가중치 1 을 준다. ConSFT 는 이 자리에 confidence-aware 스칼라 $`\omega`$ 를 끼워 넣습니다.

> "$`r(\theta)\approx\frac{\exp(\mathrm{ELBO}_{\theta})}{\exp(\mathrm{ELBO}_{\mathrm{behavior}})}=\frac{\exp(-\mathcal{L}_{\theta}+c)}{\exp(-\mathcal{L}_{\mathrm{behavior}}+c)}=\exp\left(\mathcal{L}_{\mathrm{behavior}}-\mathcal{L}_{\theta}\right).`$" (§4.1, Eq. 3)
> (Flow-matching 손실이 ELBO 의 노이즈 스케줄 상수 차이로 환원되기 때문에 likelihood ratio 가 손실 차의 지수로 깔끔하게 떨어집니다.)

ideal expert 가정 $`\mathcal{L}_{\mathrm{behavior}}=0`$ 과 온도 $`\tau>0`$ 을 넣어 보수적 가중치를 얻습니다:

$$\omega_{\mathrm{ConSFT}}(\theta)=\exp\left(\frac{\mathcal{L}_{\mathrm{behavior}}-\mathcal{L}_{\mathrm{SFT}}(\theta)}{\tau}\right)=\exp\left(-\frac{\mathcal{L}_{\mathrm{SFT}}(\theta)}{\tau}\right).$$

stop-gradient 를 입힌 최종 목적:

$$\mathcal{J}_{\mathrm{ConSFT}}(\theta)=\mathrm{sg}\left[\exp\left(-\frac{\mathcal{L}_{\mathrm{SFT}}(\theta)}{\tau}\right)\right]\cdot\mathcal{L}_{\mathrm{SFT}}(\theta).$$

FIM 분석 (Eq. 6, 7):

$$\mathcal{R}(g)=g^{\top}Fg, \qquad \mathcal{R}(g_{\mathrm{ConSFT}})=\omega^{2}\cdot\mathcal{R}(g_{\mathrm{SFT}})=\exp\left(-\frac{2\mathcal{L}_{\mathrm{SFT}}(\theta)}{\tau}\right)\mathcal{R}(g_{\mathrm{SFT}}).$$

> "Equation 7 reveals the mathematical mechanism of ConSFT. For unfamiliar transitions where $`\mathcal{L}_{\mathrm{SFT}}(\theta)`$ is large, the exponential coefficient exponentially decays toward zero." (§4.2)
> (loss 와 gradient magnitude 의 양의 상관을 quadratic 으로 끊어 forgetting risk 의 상한을 만든다는 해석.)

온도 스케줄 (Appendix C.1, Eq. 11–12):

$$\rho(t)=\frac{\exp\left(-\lambda\left[\min\left(\frac{t}{T},1\right)\right]^{c}\right)-\exp(-\lambda)}{1-\exp(-\lambda)}, \qquad \tau(t)=\min\left(\frac{\tau_{\mathrm{start}}}{\max(\rho(t),\epsilon)},\tau_{\mathrm{end}}\right).$$

실효 가중치는 floor 를 둔 $`\omega(\theta)=\max(\omega_{\mathrm{min}},\exp(-\kappa\,\mathcal{L}_{\mathrm{SFT}}(\theta)/\tau))`$ 로 정의해 heavy-tailed 시연에서도 gradient vanishing 을 피한다.

### 학습 셋업

- **백본** — $`\pi_{0}`$, $`\pi_{0.5}`$, GR00T-N1.6-3B (모두 flow-matching VLA).
- **벤치마크** — LIBERO (Spatial / Object / Goal) + RoboTwin (Indep / Single-Arm / Coord). 평가 프로토콜: target 성공률이 baseline 과 비슷한(87~95%) 시점까지 학습 후 held-out 으로 retention 측정.
- **하드웨어** — 8× NVIDIA A100 (80GB) + FSDP, global batch 1024, micro 32.
- **옵티마이저** — Adam, β=(0.9, 0.95), eps $`1.0\times 10^{-8}`$, LR $`2.5\times 10^{-5}`$, weight decay $`1.0\times 10^{-10}`$, grad-norm 1.0.
- **ConSFT 온도** — $`\tau_{\mathrm{start}}=0.003`$, $`\tau_{\mathrm{end}}=5.0`$, $`c=3.5`$, $`\lambda=0.8`$, $`\kappa=25.0`$, $`\omega_{\mathrm{min}}=0.001`$, $`T=2000`$ step. shape 4 개 ($`\lambda, c, \kappa, \omega_{\mathrm{min}}`$) 는 모든 실험에서 고정, task-specific 은 $`\tau_{\mathrm{start}}`$ 와 $`T`$ 둘뿐.
- **PPO 비교군 (§3, Appendix A.1)** — sparse reward $`r\in\{0,1\}`$, 1 train + 4 rollout worker 비동기, ODE step $`K=4`$, action chunk 5, clip $`\epsilon=0.2`$, GAE $`\lambda=0.95`$, $`\gamma=0.99`$, actor LR $`1.0\times 10^{-6}`$, critic LR $`1.0\times 10^{-5}`$.

---

## 📊 실험 설정과 결과

요는 표 두 개. Table 2 (세 백본 × 두 벤치마크) 와 Table 3 (LIBERO 에서 LwF/ER/LoRA/ConSFT 비교).

**Table 2 — LIBERO (target = Spatial, held-out = Object, Goal). $`\pi_{0}`$ base 부분:**

| Method | Target Spatial | Object | Goal | Avg prior |
|---|---|---|---|---|
| $`\pi_{0}`$ Base | 0.25 ± 0.097 | 0.58 ± 0.035 | 0.40 ± 0.035 | 0.49 ± 0.025 |
| $`\pi_{0}`$ SFT | 0.90 ± 0.067 | 0.02 ± 0.010 (↓0.56) | 0.16 ± 0.026 (↓0.24) | 0.09 ± 0.014 (↓0.40) |
| $`\pi_{0}`$ ConSFT | 0.90 ± 0.067 | 0.32 ± 0.033 (↓0.26) | 0.35 ± 0.034 (↓0.05) | 0.34 ± 0.024 (↓0.15) |
| $`\pi_{0.5}`$ SFT | 1.00 | 0.18 (↓0.62) | 0.28 (↓0.46) | 0.23 (↓0.54) |
| $`\pi_{0.5}`$ ConSFT | 1.00 | 0.46 (↓0.34) | 0.40 (↓0.34) | 0.43 (↓0.34) |
| GR00T SFT | 0.70 | 0.42 (↓0.46) | 0.55 (↓0.35) | 0.49 (↓0.40) |
| GR00T ConSFT | 0.63 | 0.56 (↓0.32) | 0.62 (↓0.28) | 0.59 (↓0.30) |

> "ConSFT limits the LIBERO-Object drop to $`\downarrow 26\%`$ while matching SFT's exact target-task performance on LIBERO-Spatial ($`90\%`$)." (§5.2)
> (동일 target 도달 시점에서 prior retention 만 끌어올렸다는 데 주목. risk attenuation 의 실측 증거.)

**Table 2 — RoboTwin ($`\pi_{0}`$ 부분):**

| Method | Indep. | Single-Arm | Coord. | Avg prior |
|---|---|---|---|---|
| Base | 0.10 | 0.57 | 0.30 | 0.44 |
| SFT | 0.55 | 0.27 (↓0.30) | 0.00 (↓0.30) | 0.14 (↓0.30) |
| ConSFT | 0.60 | 0.43 (↓0.14) | 0.13 (↓0.17) | 0.28 (↓0.16) |

> "ConSFT preserves these held-out capabilities, retaining a $`13\%`$ success rate on RoboTwin-Coord. for $`\pi_{0}`$ … achieves a $`60\%`$ success rate on RoboTwin-Indep., slightly outperforming the unconstrained SFT baseline ($`55\%`$)." (§5.2)
> (구조적 분포 이동(독립 → 협조) 에서도 target 이 오히려 약간 올라가면서 retention 이 보존됩니다.)

**Table 3 — LIBERO 에서 anti-forgetting baseline 들 ($`\pi_{0}`$, target = Spatial):**

| Method | Spatial | Object | Goal | Avg prior |
|---|---|---|---|---|
| Base | 0.25 | 0.58 | 0.40 | 0.49 |
| LwF (KL/MSE) | 0.80 | 0.10 (↓0.48) | 0.00 (↓0.40) | 0.05 (↓0.44) |
| ER (1:1 replay) | 0.90 | 0.20 (↓0.38) | 0.16 (↓0.24) | 0.18 (↓0.31) |
| LoRA (r=16) | 0.90 | 0.10 (↓0.48) | 0.38 (↓0.02) | 0.24 (↓0.25) |
| ConSFT | 0.90 | 0.32 (↓0.26) | 0.35 (↓0.05) | 0.34 (↓0.15) |

> "ConSFT bypasses the need for external data buffers or low-rank structural bottlenecks. It achieves the highest average prior capability retention across both domains ($`34\%`$ and $`28\%`$) while matching or exceeding the target-task performance of all baselines." (§5.3)
> (사전 데이터 없는 regime 에서 ER 까지 앞지른다는 강한 주장. 본 논문이 P4 핀 후보가 되는 결정적 근거.)

![Figure 2 — Layer-wise sparsity over training steps](https://arxiv.org/html/2605.08879/x2.png)

> "Figure 2: Evolution of layer-wise update sparsity across training steps. Vanilla SFT (left) drives a rapid, early collapse in parameter sparsity, resulting in dense global overwrites. ConSFT (right) structurally delays this shift, enforcing a controlled and uniformly decaying optimization trajectory." (§5.4)
> (ConSFT 가 PPO 만큼 엄격하진 않지만 sparsity 붕괴 시점을 늦춰 retention–convergence 균형점을 잡는다는 메커니즘 그림.)

![Figure 3 — Real-world test-tube transfer retention](https://arxiv.org/html/2605.08879/x3.png)

> "Figure 3: Capability retention in physical deployments. Following downstream adaptation to the test-tube target task (controlled at 70% target success), unconstrained adaptation baselines (vanilla SFT, LwF) exhibit severe degradation of pre-trained capabilities. In contrast, ConSFT achieves the highest prior task retention among all baselines in a prior-data-free regime, maintaining robust performance even under visually cluttered conditions ( w/ interference )." (§5.5)
> (실물 $`\pi_{0.5}`$ + 단일팔에서 vanilla SFT 의 z-축 spatial drift 가 ConSFT 로 해소되는 사례.)

---

## ⚖️ 한계

- **저자 명시** — 신뢰도 낮은 샘플의 그래디언트를 직접 죽이는 구조이므로 *완전히 새로운 motor primitive* 를 학습할 때 target 수렴이 느려집니다 (§6 첫 한계).
- **저자 명시** — 파라미터 공간 deviation 은 묶지만 *flow-matching ODE 의 multi-step 추론 궤적 오차* 에 대한 형식적 상한은 제공하지 않습니다 (§6 둘째 한계).
- ideal-expert 가정 ($`\mathcal{L}_{\mathrm{behavior}}=0`$) 은 Appendix B.1 의 "global scalar 로 흡수" 논증에 의존합니다. 시연 노이즈가 sample 의존적으로 분포가 다를 경우 그 논증이 깨질 수 있는데, 그 경우는 실험으로 검증되지 않았습니다.
- 비교군 LwF 가 MSE-via-velocity-field 한 가지로만 인스턴스화돼 있어, 본격 KL/score-matching 정규화 (예: ReinFlow 류) 와의 직접 비교는 빠져 있습니다.
- LIBERO-Goal 에서 LoRA 가 $`\downarrow 0.02`$ 로 ConSFT 의 $`\downarrow 0.05`$ 를 앞서는 suite 가 존재합니다 — 평균이 아닌 task-level 에서는 일관된 우위는 아님.

---

## ♻️ 재현성

- **코드** — 프로젝트 페이지 [tyzhang2907.github.io/ConservativeSFT](https://tyzhang2907.github.io/ConservativeSFT/) 가 본문에 명기. 코드 공개 여부·라이선스는 페이지 자체를 봐야 확인 가능 (본문에는 명시 없음).
- **데이터** — LIBERO (공개), RoboTwin (공개). ER 비교군은 "pre-training corpora" 가 필요하다고만 적혀 있어 ConSFT 자체는 사전 데이터를 요구하지 않습니다 (§5.3 서술 일치).
- **하드웨어** — 8× A100 (80GB), FSDP. PPO 비교군은 5× A100 (1 train + 4 rollout).
- **하이퍼파라미터** — Table 4 (PPO), Table 5 (ConSFT) 에 모두 명시. shape 변수 4 개는 task-agnostic 고정, task-specific 은 $`\tau_{\mathrm{start}}`$, $`T`$ 둘.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P4 (VLM Pretraining Preservation) — 직격**. D19 (VLM FT range), D20 (prior-preservation strategy), D21 (staged training recipe), D23 (action representation × VLM preservation) 의 deferred trigger 와 직접 맞물립니다. 특히 D20 의 deferred 옵션 "LoRA-minimal / 액션 측 어댑터 / co-FT" 외에 *손실-가중치만으로* prior 를 지키는 네 번째 길을 제시합니다. 초기 sim ablation 에서 D19 가 (a) freeze 에서 벗어나야 할 때, ConSFT 는 "freeze 안 풀고 full-FT 가까운 plasticity 를 얻는" 절충안이 될 수 있습니다.
- **P1 (Heterogeneous Body/Hand Decoder) — 보조**. D7 (π backbone integration / partition) 의 slice-and-FT 전략에서, Hand expert 쪽이 contact-rich 신규 분포에 노출될 때 Body expert 와 백본의 prior 를 보호하는 손실로 채택 가능합니다. 단, ConSFT 자체는 백본 분할과 무관 — *어떤* flow-matching VLA 든 손실 한 줄 교체로 적용됩니다.
- **4-contribution ablation** — D25 의 (e) "+VLM-preservation" 조건을 ConSFT 로 인스턴스화할 후보. 현재 (e) 는 추상적 명세에 머물러 있는데, ConSFT 는 추가 파라미터·데이터 없이 정의되므로 ablation 의 깔끔한 한 축이 됩니다.
- **§10 경쟁자 함의** — antagonist A (correction-residual on frozen VLA) 의 "frozen 으로 prior 보호" 라인을, ConSFT 는 "frozen 없이도 prior 보호 가능" 으로 약하게 만듭니다. 다만 본 논문은 dexterous hand 가 아닌 LIBERO/RoboTwin 의 거시 manipulation 만 평가하므로 contact-precision 차원의 antagonist 무력화는 아직 미검증.

---

## ✨ 핀 논문 대비 델타

- **VLM2VLA ([arXiv:2509.22195](https://arxiv.org/abs/2509.22195), P4 핀)** — VLM2VLA 는 LoRA + NL-style action 으로 "구조" 를 손대 forgetting 을 완화합니다. ConSFT 는 *구조를 안 건드리고 손실만* 손댄다는 점에서 직교 — 두 방법을 합칠 수 있는 후보.
- **PriorVLA ([arXiv:2605.10925](https://arxiv.org/abs/2605.10925), P4 핀)** — frozen Prior Expert + Adaptation Expert 라는 *이중 네트워크* 로 prior 를 보존. ConSFT 는 같은 목표를 *단일 네트워크 + scalar gate* 로 푼다는 점이 핵심 델타. 메모리 측면에서 ConSFT 가 압도적이며, 두 접근의 직접 head-to-head 비교는 아직 부재.
- **VLA-Adapter ([arXiv:2509.09372](https://arxiv.org/abs/2509.09372), P4 핀)** — action-side adapter 로 백본을 보호. ConSFT 는 adapter 도 없이 동일 효과를 노립니다.
- **RT-2 ([arXiv:2307.15818](https://arxiv.org/abs/2307.15818), P4 핀)** — web/robot co-FT 로 prior 회복. ConSFT 는 web 데이터 0 으로 같은 retention 을 주장한다는 점이 가장 큰 차이.
- **HORA / AnyRotate (P3 핀)** — 무관 (System0 RL 영역).
- **Demystifying Action Space Design (P1 핀)** — 무관 (action space 자체).

→ 핀 후보 우선순위: **P4 에서 PriorVLA 와 동급, 혹은 더 가볍다**. 다만 contact-precision 평가가 없어 P4 핀 8 슬롯 안에 들이려면 maintainer 의 "메모리 0 prior 보호" 가치 판단이 필요.

---

## ⚙️ 의사결정 함의

이 논문이 맞다면 PROBE 학습 파이프라인에서 다음이 구체적으로 바뀝니다.

- **`training.loss` 모듈** — π0 / π0.5 백본 학습 손실에 `consfter_weight = stop_gradient(exp(-flow_loss / tau))` 한 줄을 곱해 `loss = consfter_weight * flow_loss` 로 교체. 표준 flow-matching 손실 자리에 들어가는 in-place 변경이라 백본·어댑터 코드 무수정.
- **새 하이퍼파라미터 키** — `consft.tau_start = 0.003`, `consft.tau_end = 5.0`, `consft.kappa = 25.0`, `consft.lambda = 0.8`, `consft.c_curvature = 3.5`, `consft.omega_min = 0.001`, `consft.decay_steps = 2000`. shape 4 개는 고정, task-specific 은 `tau_start` 와 `decay_steps` 둘만 튜닝.
- **D19 v1 (full freeze) → D19 deferred 진입 시의 백업** — Stage 2 가 plateau 에 도달해 D19 (d) LoRA 로 가야 할 때, ConSFT 를 *먼저* 끼워 보는 분기점을 추가. 메모리 추가 비용 0 이므로 구현 진입 전 prerequisite 으로 추가해도 일정 부담 없음.
- **D25 4-contribution ablation 의 (e) 조건** — "+VLM-preservation" 을 "freeze + ConSFT 손실" 로 인스턴스화. 기존 (e) 가 추상적이었던 부분을 구체 손실로 못 박을 수 있습니다.
- **메트릭 추가** — Eq. 8 의 relative-deviation sparsity $`S`$ (`δ=10⁻³`) 를 학습 중 layer-wise 로 로깅. catastrophic forgetting 의 *조기 신호* 로 활용 (Fig. 1, 2 의 곡선이 이걸 보여줍니다).
- **System0 (P3) 와는 무관** — RL 영역이라 변동 없음.

모호한 부분(검증할 것): "flow-matching loss = ELBO + const" 라는 FPO 류 근사가 π0.5 + Sharpa 시뮬레이션의 액션 청크 길이·denoise step 에서도 동일하게 성립하는지. Eq. 3 의 상수 $`c`$ 가 정말 sample 독립인지 확인 필요.

---

## ⚠️ 먼저 검증할 실패 모드

PROBE 스택으로 전이될 때 의심할 점과 가장 싼 sanity check 순서:

1. **dexterous hand 의 contact-rich tail 에서도 sparse update 가 충분한가** — 본 논문 실험은 모두 거시 manipulation (pick/place/grasping/dual-arm). dexterous 의 in-hand 재배향처럼 *fingertip-level fine motor* 가 핵심인 task 에서는 새로운 primitive 학습이 본질적이라, ConSFT 의 "low-confidence sample 억제" 가 학습을 막을 수 있습니다 → 가장 싼 체크: LIBERO 가 아닌 *xhand in-hand 회전 50 trial sim* 에서 vanilla SFT vs ConSFT target convergence 곡선 비교 (1 GPU, 2~4시간).
2. **temperature schedule 의 task-agnostic 주장** — shape 4 변수를 고정한 채 PROBE 도메인 (sim2real, tactile-heavy) 에서 그대로 통하는가? 가장 싼 체크: τ_start ∈ {0.001, 0.003, 0.01} 그리드 3 점만 돌려 retention–target 균형 변화 확인.
3. **시연 노이즈가 sample 별로 다를 때** — Sharpa 텔레옵 데이터는 finger 별 노이즈 분포가 크게 다릅니다. Appendix B.1 의 "global scalar 흡수" 가정이 깨지는 지점인데, 본 논문은 검증하지 않았습니다 → 가장 싼 체크: finger 별 loss 분산을 학습 중 로깅, ConSFT 가중치가 특정 finger 만 만성적으로 죽이는지 모니터.
4. **Hand expert 의 Body↔Hand FiLM (D4) 와의 상호작용** — Body 쪽 gradient 가 Hand expert 의 $`\omega`$ 와 결합돼 비대칭 가중을 만들 가능성. 가장 싼 체크: D4 FiLM on/off × ConSFT on/off 2×2 ablation 을 LIBERO 단일 task 에서 먼저.
5. **flow-matching 외 backbone (autoregressive π0-FAST) 으로의 전이** — 본 논문은 closed-form likelihood 부재가 출발점인데, autoregressive 라면 PPO clip 을 그냥 쓰면 됩니다. ConSFT 가 autoregressive VLA 에서도 SFT 위 개선이 되는지는 본 논문 범위 밖.

---

## 💡 컨텍스트 제안

- **P4 (D20) deferred 후보에 "scalar-weighted SFT" 추가** — 현재 D20 의 deferred 옵션은 LoRA-minimal / web-co-FT / Bridge Attention 셋입니다. ConSFT 류 *손실 가중* 을 네 번째 라인으로 명시하면, 초기 sim ablation 에서 Stage 2 plateau 가 왔을 때 어댑터 도입 없이 시도할 가장 가벼운 선택지가 생깁니다.
- **§8.4 P4 Pinned 후보** — PriorVLA / VLM2VLA 와 함께 또는 둘 중 하나를 대체해 ConSFT 를 핀 후보로 고려. "prior-data-free + 메모리 0" 이라는 차별점이 명확합니다. 단, dexterous contact-precision 검증이 없다는 점은 분명히 약점. 다음 분기 rebalance 때 결정 권고.
- **D25 falsifier 의 (e) 조건 명세화** — 현재 "+VLM-preservation" 이 추상적인데, ConSFT 손실을 default 인스턴스로 못 박으면 ablation 재현성과 비교 가능성이 올라갑니다.
- **§10.2 "Bounded RL-in-VLA precedents" 확장 검토** — ConSFT 는 RL 이 아니지만 "RL 의 trust-region 효과를 SFT 로 옮긴 것" 이므로, "RL = capability source 가 아닌 fine-tuning 도구" 라는 antagonist 프레임을 *더 약화* 시키는 증거이기도 합니다. RL 의 핵심 장점을 RL 없이 얻는다면 P3 System0 의 정당화 논거 (slip/grasp 가 reward-engineerable 한 유일 지점) 는 그대로 유지되지만, "다른 곳엔 RL 안 쓴다" 의 정당화는 한층 단단해집니다.
