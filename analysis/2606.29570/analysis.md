# Paper Analysis — Hierarchical Policy Learning via Spectral Decomposition

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Hierarchical Policy Learning via Spectral Decomposition |
| 저자 | Shuxin Cao, Liquan Wang, Walker Byrnes, Yiye Chen, Yilun Du, Animesh Garg |
| 링크 | [arXiv:2606.29570](https://arxiv.org/abs/2606.29570) · [Website](https://causal-spectral-policies.github.io/) |
| 발행일 / 버전 | 2026-06-28 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-07-01 |
| 관련 Pillar | P1, P4 |
| 태그 | vla-arch, flow-matching, dexterity |

---

## 🧭 한 줄 요약 (TL;DR)

로봇 action chunk 을 DCT 로 주파수 영역에 옮기면 저주파는 거친 전역 이동(coarse), 고주파는 정밀 정렬·타이밍·접촉(fine)으로 자연 분리된다는 관찰에서 출발해, coarse 를 관측·언어로 먼저 예측하고 fine 을 "실현된 coarse 궤적"에 조건화해 생성하는 인과적 coarse-to-fine 정책 **Causal Spectral Policy (CSP)** 를 제안합니다. 정밀·장기 조작과 노이즈 시연에서 시간영역 baseline 대비 일관되게 우위를 보입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 조작은 장기 궤적 계획(coarse)과 미세 반응 제어(fine)의 결합인데, 기존 정책은 action 을 시간영역에서 직접·자기회귀적으로 예측하며 **모든 timestep 을 동등하게** 취급해 이 위계 구조를 명시적으로 담지 못합니다.
- **기존 접근의 한계** — chunk-based(diffusion/flow)와 autoregressive 모두 시간영역에서 균일 예측하여 temporal resolution 에 민감하고, 정밀·속도 민감 과제에서 무너집니다. 주파수 기반 선행연구(Quest/FAST/FreqPolicy)는 표현 효율에만 집중하고 coarse 계획과 fine 실행 사이의 **인과 관계를 명시적으로 모델링하지 않습니다**.
- **본 논문의 가설** — action 학습은 내재적 coarse-to-fine 시간 구조를 명시할 때 가장 효과적이며, 저주파(과제 의도)와 고주파(실행 보정)는 **서로 다른 인과적 역할**을 한다.
- **왜 지금 중요한가** — 텔레오퍼레이션 시연은 지연·대역폭·실행 변동성이 짧은-timescale 보정(고주파)에 불균형하게 실려, 시간영역 균일 학습이 고주파 노이즈에 지배되어 조건부 평균으로 붕괴합니다. 정밀 조작(hand-centric)일수록 이 붕괴가 실패로 직결됩니다.

---

## 🧩 핵심 기여

- action 학습의 **근본적 비대칭성**을 규명 — coarse·fine action 성분이 과제 실행에서 서로 다른 인과 역할을 담당함을 실증.
- 통제된 **주파수영역 개입(coefficient truncation)** 으로, 고주파 성분이 전체 motion energy 기여는 작지만 정밀성에는 필수임을 보임(real-robot dart 삽입 과제).
- **CSP** — action chunk 을 DCT 로 저/고주파로 분해하고, `low → high` 인과 의존(고주파는 실현된 저주파에 조건화, stop-gradient)으로 분리 모델링하는 spectral coarse-to-fine 정책 프레임워크를 제안·검증.
- **human-inspired teleoperation noise injection** — AR(1) drift + signal-dependent 변동 + 간헐적 corrective burst + phase-dependent 스케줄을 결합한 구조적 노이즈 증강을 제안, 노이즈 시연 하 강건성을 입증.

---

## 🔑 기술 키워드

- **Causal Spectral Policy (CSP)** — 주파수영역 coarse→fine 을 인과 순서로 예측하는 본 논문의 정책. "먼저 대략 어디로 갈지 정하고, 그 다음 그 경로 위에서 미세 보정을 얹는" 2단계 구조.
- **Discrete Cosine Transform (DCT)** — 시계열을 주파수 계수로 바꾸는 직교 가역 변환. action 을 "느린 큰 움직임 + 빠른 잔떨림"으로 정렬해 시간 스케일별 구조를 명시적으로 드러냄.
- **Coarse-to-fine factorization** — action 분포를 $`p(a^{\mathrm{coarse}})\,p(a^{\mathrm{fine}}\mid a^{\mathrm{coarse}})`$ 로 분해. 전역 계획을 먼저 확정하고 국소 보정을 그에 종속시키는 위계 분해.
- **Coefficient truncation** — 고주파 계수를 0 으로 잘라 역변환·재생하는 개입 실험. 특정 주파수 대역을 제거했을 때 과제 실행이 어떻게 망가지는지로 각 대역의 기능적 역할을 인과적으로 격리.
- **Stop-gradient (sg)** — 고주파 손실의 gradient 가 저주파 예측기로 역전파되지 않도록 차단하는 연산. fine 감독이 coarse 학습을 오염시키지 못하게 해 의도한 인과 방향을 강제.
- **Frequency split heuristic** — 시연 action 의 평균 power spectrum 누적 에너지가 임계(≈90%)를 넘는 최소 인덱스로 저/고주파 경계를 데이터 기반 선택. 어디까지가 "거친 움직임"인지를 데이터가 정하게 함.
- **Human-inspired noise injection** — 사람 텔레오퍼레이션의 시간상관 drift·신호의존 변동·간헐 보정을 흉내 낸 구조적 노이즈 증강. i.i.d. 잡음이 아니라 "사람이 실제로 흔드는 방식"으로 데이터를 오염시켜 강건성을 시험.
- **Signal-dependent motor variability** — 움직임 크기 $`|a_t|`$ 에 비례해 커지는 실행 변동. 신경과학의 signal-dependent noise 를 텔레오퍼레이션 모델에 이식.

---

## 🔬 방법론

### 직관

이 논문의 출발점은 아주 단순한 관찰입니다. 로봇 팔이 만드는 action 궤적을 그대로 두면 "큰 이동"과 "미세한 손끝 보정"이 한 신호에 뒤섞여 있어 정책이 둘을 구분하기 어렵습니다. 그런데 이 궤적을 DCT 로 주파수 영역에 옮기면, 저주파 계수는 목표를 향한 전역 접근 궤적을, 고주파 계수는 정밀 정렬·타이밍·접촉을 담당하도록 자연스럽게 갈라집니다. 저자들은 실제 로봇 dart 삽입 과제에서 고주파를 점점 잘라내 재생하는 실험으로 이를 확인합니다 — 고주파를 지우면 목표 근처까지는 가지만 중심에 꽂지 못합니다.

여기서 핵심 통찰은 두 대역이 **역할만 다른 게 아니라 인과적으로 비대칭**이라는 점입니다. 관측과 언어는 주로 "어디로 갈지"(coarse)를 결정하고, 일단 그 경로가 정해지면 미세 보정은 언어보다 "이미 실현된 거친 궤적"에 의존합니다. 그래서 CSP 는 저주파를 관측·언어에서 먼저 예측하고, 고주파를 그 저주파 예측에 조건화해 생성하는 2단계 인과 구조를 씁니다.

이 구조가 특히 빛나는 곳이 노이즈 시연입니다. 사람 텔레오퍼레이션 잡음은 대부분 고주파에 실립니다($`\eta^{\mathrm{low}}\approx 0`$, $`\eta^{\mathrm{high}}`$ 큼). 시간영역 균일 학습은 이 고주파 잡음이 손실을 지배해 예측기가 조건부 평균으로 붕괴하고 과제-필수 보정을 뭉개버립니다. CSP 는 고주파 예측을 실현된 저주파에 앵커해 감독의 모호성을 줄이므로, 잡음이 커도 예측 가능한 보정 구조를 학습할 수 있습니다.

### 아키텍처

![Figure 3 — hierarchical spectral policy overview](https://arxiv.org/html/2606.29570/figures/model.png)

> "Given observation $`o`$ and language instruction $`l`$ , the policy first predicts low-frequency action components that capture coarse task-level motion. Conditioned on the realized low-frequency trajectory, a second module predicts high-frequency corrective components. The final action sequence is reconstructed by concatenating frequency coefficients and applying the inverse discrete cosine transform (iDCT)." (§4)
> (한글 해설 — 저주파 예측기 → 고주파 예측기(저주파 조건) → 계수 결합 → iDCT 로 시간영역 action 복원의 2-trunk 파이프라인을 시각화합니다.)

- **입력** — 관측 $`o_t`$ (다시점 RGB), proprioception $`u_t`$ (end-effector pose + gripper state), frozen language encoder 투영 $`\ell`$. 모든 정책이 동일 튜플 $`(o_t,u_t,\ell)`$ 을 받으며, baseline 은 concat 후 시간영역 정책망에 넣고 CSP 는 perception encoder 로 $`N_{\mathrm{obs}}`$ 토큰으로 매핑.
- **action 표현** — 전문가 action $`a_t\in\mathbb{R}^{D_a}`$ (6D twist + 1 gripper). 길이-$`T`$ chunk 의 **첫 6 차원(twist)만** type-II DCT 로 주파수 계수 $`C_i\in\mathbb{R}^{T\times 6}`$ 로 변환(gripper 채널은 변환 없이 그대로 concat).
- **2-trunk 예측** — GPT-style trunk 1 이 $`(o,u,\ell)`$ 에서 저주파 슬라이스 $`C_i^{\mathrm{low}}`$ 를 예측, trunk 2 가 실현된 저주파에 조건화해 $`C_i^{\mathrm{high}}`$ 를 추론. 각 stage 8 layers, hidden 256, heads 4, block size 65.
- **복원** — $`C_i=[C_i^{\mathrm{low}},C_i^{\mathrm{high}}]`$ 를 iDCT 로 시간영역 action 으로 되돌리고 gripper 채널을 붙임.

### 학습 목표 / 손실

action chunk 분포를 시간 스케일에 걸쳐 coarse-to-fine 으로 분해합니다.

> "$`p(a_{t:t+t^{\prime}}\mid o_{t},l)=p(a^{\mathrm{coarse}}\mid o_{t},l)\;p(a^{\mathrm{fine}}\mid o_{t},a^{\mathrm{coarse}})`$" (§4.1, Eq. 1)
> (한글 해설 — coarse 는 관측·언어에만 의존하고, fine 은 관측과 "이미 정해진 coarse" 에 조건화됩니다. 언어는 fine 에 직접 들어가지 않는 것이 핵심 설계입니다.)

$$p(a_{t:t+t^{\prime}}\mid o_{t},l)=p(a^{\mathrm{coarse}}\mid o_{t},l)\;p(a^{\mathrm{fine}}\mid o_{t},a^{\mathrm{coarse}}).$$

DCT 는 직교 가역이므로 시간영역 모델링은 계수 모델링과 등가($`p(a_{t:t+t^{\prime}}\mid o_t,l)\equiv p(c\mid o_t,l)`$)입니다. cutoff $`\lambda\in(0,t^{\prime})`$ 로 계수를 저/고로 분할합니다.

```math
c=\begin{bmatrix}c^{\mathrm{low}}\\c^{\mathrm{high}}\end{bmatrix}=\begin{bmatrix}c_{0:\lambda}\\c_{\lambda:t^{\prime}}\end{bmatrix}
```

두 예측기의 인과 의존은 다음과 같이 인수분해됩니다.

> "$`p(c\mid o_{t},l)=p_{\mathrm{low}}(c^{\mathrm{low}}\mid o_{t},l)\;p_{\mathrm{high}}(c^{\mathrm{high}}\mid o_{t},c^{\mathrm{low}})`$" (§4.3, Eq. 2)
> (한글 해설 — 저주파는 관측·언어로, 고주파는 관측과 실현된 저주파 $`c^{\mathrm{low}}`$ 로 예측하는 방향성 의존입니다.)

$$p(c\mid o_{t},l)=p_{\mathrm{low}}(c^{\mathrm{low}}\mid o_{t},l)\;p_{\mathrm{high}}(c^{\mathrm{high}}\mid o_{t},c^{\mathrm{low}}).$$

학습은 저/고주파 계수에 대한 회귀 손실의 합입니다.

$$\mathcal{L}=\|\hat{c}^{\mathrm{low}}-c^{\mathrm{low}}\|_{2}^{2}+\|\hat{c}^{\mathrm{high}}-c^{\mathrm{high}}\|_{2}^{2}$$

여기서 $`\hat{c}^{\mathrm{low}}=p_{\mathrm{low}}(o_{t},l)`$, $`\hat{c}^{\mathrm{high}}=p_{\mathrm{high}}(o_{t},\mathrm{sg}(\hat{c}^{\mathrm{low}}))`$ 입니다.

> "The stop-gradient operator $`\mathrm{sg}(\cdot)`$ prevents fine-scale supervision from influencing coarse motion learning, enforcing the intended causal dependency." (§4.3)
> (한글 해설 — stop-gradient 가 없으면 고주파 손실이 저주파 예측기를 흔들어 인과 방향이 무너집니다. sg 는 이 방향성을 손실 수준에서 못 박는 장치입니다.)

**노이즈 강건성의 이론적 동기(Appendix 7.1.5)** — 텔레오퍼레이션 잡음 $`\tilde{a}=a+\varepsilon`$, $`\tilde{c}=c+\eta`$ ($`\eta=F\varepsilon`$)는 시간상관 drift 로 주로 짧은-timescale 에 실려 $`\eta^{\mathrm{low}}\approx 0`$, $`\eta^{\mathrm{high}}`$ 가 큽니다. 표준 IL 손실은 다음처럼 분해됩니다.

$$\mathbb{E}\!\left[\|\hat{c}-\tilde{c}\|_{2}^{2}\right]=\mathbb{E}\!\left[\|\hat{c}^{\mathrm{low}}-c^{\mathrm{low}}\|_{2}^{2}\right]+\mathbb{E}\!\left[\|\hat{c}^{\mathrm{high}}-(c^{\mathrm{high}}+\eta^{\mathrm{high}})\|_{2}^{2}\right].$$

> "When the variance of $`\eta^{\mathrm{high}}`$ is large, optimization becomes dominated by noisy high-frequency supervision." (§7.1.5)
> (한글 해설 — 고주파 잡음 분산이 크면 최적화가 그 잡음 항에 지배되어 예측기가 조건부 평균 $`\hat{c}^{\mathrm{high}}=\mathbb{E}[c^{\mathrm{high}}\mid o_t,l]`$ 로 붕괴, 과제-필수 보정을 뭉갭니다. CSP 는 $`p(c^{\mathrm{high}}\mid o_t,l)\to p(c^{\mathrm{high}}\mid o_t,c^{\mathrm{low}})`$ 로 앵커해 이 모호성을 줄입니다.)

### 학습 셋업

- **주파수 분할 선택**(§5.1.1, §7.3) — task·chunk length $`K`$ 마다 시연 action chunk 의 DCT 계수를 데모·차원에 걸쳐 제곱평균해 empirical power spectrum $`\bar{P}_k=\frac{1}{Nd}\sum_n\sum_d|c^{(n)}_{k,d}|^2`$ 을 구하고, 누적 에너지 $`E_k`$ 가 임계 $`\alpha\approx 0.9`$–$`0.98`$ 를 넘는 최소 인덱스 $`K_{\text{energy}}`$ 와 log-power 곡선의 최대 음곡률 지점 $`K_{\text{elbow}}`$ 중 큰 값 $`K_{\text{split}}=\max(K_{\text{energy}},K_{\text{elbow}})`$ 를 split 으로 사용(선택적으로 $`\{4,8,16,24,32\}`$ 로 snap).
  > "Across both benchmarks, this typically assigns the lowest $`\sim`$ 30% of frequency coefficients to the coarse component." (§5.1.1)
  > (한글 해설 — 통상 최저 ~30% 계수가 coarse 로 배정되며, 20–40% 범위에서 성능이 안정적이라 정확한 분할점에 민감하지 않습니다(Fig. 5).)
- **하이퍼파라미터(Table 5)** — action dim $`D_a`$ = 7 (6D twist + gripper), transformer hidden $`n_{\mathrm{embd}}`$ = 256, layers = 8 (per stage), heads = 4, block size = 65, "predict in frequency: Yes (twist only)", hierarchy = two-stage (low + high).
- **벤치마크** — LIBERO (LIBERO-90, LIBERO-10; 장기·언어조건), MimicGen (Stack/Stack3/Coffee/Square/Threading; 정밀 정렬·threading). chunk size $`K\in\{16,32,64\}`$ 로 temporal horizon 민감도 측정(execution horizon 은 고정), 2 seeds 평균.
- **실물** — Franka Emika Panda + 고정/손목 Logitech RGB 2대. 노이즈 실험은 no/moderate/high 3조건 학습 후 clean rollout 평가.

---

## 📊 실험 설정과 결과

### Table 1 — chunk size 별 시뮬레이션 성공률(%)

| Method | Libero-90 | Libero-10 | MimicGen Mean |
|---|---|---|---|
| **K=16** | | | |
| ACT | 90.7 | 70.5 | 51.5 |
| BAKU | 86.1 | 57.4 | 49.8 |
| DP-CNN | 83.0 | 64.6 | 58.5 |
| DP-Transformer | 77.0 | 60.6 | 53.8 |
| Action Binning | 92.1 | 73.8 | 57.8 |
| Freq-Autoregressive | 90.9 | 76.8 | 57.5 |
| **CSP (Ours)** | **91.9** | **80.8** | **65.5** |
| **K=64** | | | |
| ACT | 85.7 | 48.6 | 9.0 |
| BAKU | 75.4 | 35.1 | 17.3 |
| DP-CNN | 82.7 | 46.4 | 41.8 |
| DP-Transformer | 79.1 | 50.0 | 31.3 |
| Action Binning | 84.9 | 59.8 | 31.8 |
| Freq-Autoregressive | 85.9 | 60.5 | 32.0 |
| **CSP (Ours)** | **87.6** | **68.8** | **50.0** |

> "At chunk size 16, CSP achieves the highest mean success rate (65.5%), and at chunk size 64 it degrades gracefully to 50.0%, whereas ACT and BAKU collapse below 20%." (§5.1.3, Table 1)
> (한글 해설 — chunk length 를 늘려 look-ahead 를 키울 때 시간영역 baseline 은 MimicGen 정밀 과제에서 붕괴하지만 CSP 는 완만히 감쇠합니다. 핵심은 "긴 chunk 로도 성능 보존".)

### Table 3 — Counterfactual 개입(조건 구조 변형)

| 변형 | low 조건 | high 조건 | L90 K=16 | L90 K=32 | L10 K=16 | L10 K=32 |
|---|---|---|---|---|---|---|
| No language in coarse | $`o`$ | $`o,l,c^{low}`$ | 22.2 | 18.2 | 64.5 | 61.0 |
| No coarse in fine | $`o,l`$ | $`o`$ | 86.2 | 84.2 | 65.0 | 51.5 |
| **CSP (Ours)** | $`o,l`$ | $`o,l,c^{low}`$ | **91.6** | **90.4** | **81.0** | **75.0** |
| Reverse order | $`c^{high},o`$ | $`o,l`$ | 49.6 | 46.0 | 35.5 | 55.5 |
| Reverse order + language | $`c^{high},o,l`$ | $`o,l`$ | 80.3 | 66.8 | 49.5 | 46.0 |

> "Most importantly, reversing the dependency direction performs substantially worse than the proposed ordering, suggesting that the low-to-high frequency factorization is not interchangeable with a high-to-low alternative." (§5.1.4, Table 3)
> (한글 해설 — 저주파에서 언어를 빼면 대폭 하락(과제 의도가 coarse 에 실림), 고주파에서 coarse 조건을 빼도 하락(fine 은 실현된 coarse 에 의존), 방향을 뒤집으면 최악. 이는 low→high 순서가 임의 설계가 아니라 방향성 인과임을 반증적으로 지지합니다.)

### Table 2 — Ablation(노이즈 하 hierarchy/frequency 효과)

| Method | Stack | Coffee | Libero-10 |
|---|---|---|---|
| Frequency Diffusion | 81.3 | 56.3 | 61.3 |
| No Hierarchy | 73.8 | 77.5 | 56.3 |
| CSP | 75.0 | 82.5 | **74.0** |

Libero-90 Set A/B 의 No/Small/Large 노이즈 조건에서도 CSP 가 최고(Set A Large 87.5 vs No-Hierarchy 81.5 / Freq-Diffusion 73.0).

> "Removing the hierarchical structure or the causal factorization both leads to noticeable performance drops, particularly under noisy supervision." (§5.1.3, Table 2)
> (한글 해설 — spectral 표현만으로는 부족하고, hierarchy(위계)와 causal factorization(인과 분해) 둘 다 있어야 노이즈 강건성이 확보됨을 각 ablation 이 격리해 보여줍니다. Frequency Diffusion = spectral 유지·hierarchy 제거, No Hierarchy = 조건부 의존 제거.)

### Table 4 — 실물 로봇 성공률(성공/10)

| Task | DP | Baku | Action Binning | CSP |
|---|---|---|---|---|
| Press Enter Key | 1/10 | 8/10 | 10/10 | **10/10** |
| Press C | 0/10 | 3/10 | 5/10 | **8/10** |
| Stack uniform block | 6/10 | 6/10 | 9/10 | **9/10** |
| Stack thin block | 2/10 | 3/10 | 6/10 | **9/10** |
| Close candle lid | 3/10 | 5/10 | 3/10 | **7/10** |

> "In contrast, thin block stacking is substantially more challenging, with only $`\sim`$ 50% teleoperation success; demonstrations are longer and contain frequent high-frequency corrective motions. These interventions cause baseline methods to fail due to misalignment while our method achieves a 90% success rate." (§5.2, Table 4)
> (한글 해설 — 시연 자체가 노이즈가 큰 thin block(텔레오퍼레이션 성공 ~50%)에서 baseline 은 오정렬로 실패하나 CSP 는 90%. 시뮬레이션 이득이 실물로 일관 전이됩니다.)

### 주파수 truncation 개입(§3.2–3.3)

dart 삽입 과제에서 chunk $`K=64`$, cutoff $`\lambda`$ 로 상위 주파수 계수를 0 으로 잘라 재생:

![Figure 2 — dart insertion frequency cutoff](https://arxiv.org/html/2606.29570/figures/dartfigure.png)

> "As $`\lambda`$ decreases, coarse motion toward the target is preserved while fine alignment and contact accuracy degrade, highlighting the role of high-frequency components in precision execution." (§3.2)
> (한글 해설 — $`\lambda=40`$ 처럼 고주파를 많이 남기면 중심 명중, $`\lambda`$ 를 줄이면 목표 근처엔 가나 off-center, 저주파만 남기면 접촉 실패. 고주파가 정밀 정렬·접촉의 담당 대역임을 인과적으로 격리합니다.)

![Figure 1 — coarse-to-fine spectral structure](https://arxiv.org/html/2606.29570/figures/teaser.png)

> "Action sequences admit a coarse-to-fine structure in the spectral domain. CSP predicts low-frequency motion from observation and language, then generates high-frequency corrections conditioned on the coarse trajectory." (§1)
> (한글 해설 — 논문 전체의 thesis 를 요약하는 teaser: 주파수영역의 coarse→fine 인과 파이프라인.)

---

## ⚖️ 한계

- **주파수 분할의 task-별 휴리스틱 의존** — split 은 시연 power spectrum 의 누적 에너지 임계로 task·chunk 마다 별도 산정됩니다. 20–40% 범위에서 안정적이라 하나, 이는 결국 데이터-의존 전처리 하이퍼로, 시연 분포가 얇거나 multimodal 하면 spectrum 추정이 흔들려 분할이 어긋날 수 있습니다. cross-task/cross-embodiment 로 옮길 때 재추정이 필요합니다.
- **twist 6D 에만 DCT 적용, gripper 는 우회** — 주파수 분해는 6D twist 에만 걸고 gripper 채널은 변환 없이 그대로 붙입니다. 즉 접촉 개폐 같은 이산·비평활 신호는 spectral 위계 밖에 있어, 정작 "접촉 순간"의 정밀 타이밍은 이 프레임워크가 직접 다루지 않습니다. 고DoF 손(다지 관절)으로 확장 시 이 우회가 병목이 될 수 있습니다.
- **회귀(L2) 손실의 표현력** — 저/고주파 모두 단순 L2 회귀입니다. multimodal action 분포를 계수 공간의 점추정으로 뭉갤 위험이 있고, ablation 의 "Frequency Diffusion" 이 일부 셋업에서 경쟁력 있음(Stack 81.3)은 생성 헤드 선택이 열려 있음을 시사합니다. flow/diffusion 헤드와의 정면 비교는 부분적입니다.
- **2-stage 인과 순차성의 추론 비용/지연** — 고주파가 저주파 예측 완료에 조건화되므로 두 trunk 를 순차 실행합니다. 실시간 고주파 제어(반응 제어)가 필요한 과제에서 이 순차 의존이 지연을 유발할 수 있고, 논문은 추론 latency 를 정량화하지 않습니다.
- **노이즈 모델의 자기충족성** — 강건성 이득은 "고주파에 실리는 구조적 노이즈" 가정 위에서 성립하며, 노이즈 증강 역시 저자들이 설계한 human-inspired 모델입니다. 실제 텔레오퍼레이션 잡음이 이 스펙트럼 가정($`\eta^{\mathrm{low}}\approx 0`$)을 벗어나면(예: 저주파 drift·좌표계 편향) 이론적 동기가 약해집니다.

---

## ♻️ 재현성

- **코드/데이터** — 프로젝트 웹사이트([causal-spectral-policies.github.io](https://causal-spectral-policies.github.io/))가 존재하나, 본문에서 코드 repo·데이터셋 공개를 명시적으로 확인하지 못했습니다(현 시점 웹사이트만 확보). 벤치마크(LIBERO/MimicGen)는 공개 표준이라 시뮬레이션은 재현 가능성이 높습니다.
- **하드웨어** — 실물은 Franka Emika Panda + 고정/손목 Logitech RGB 2대로 명시. 아키텍처 하이퍼는 Table 5 로 공개(hidden 256, 8 layers/stage, heads 4, block 65).
- **레시피** — 주파수 분할 휴리스틱(§7.3), 노이즈 모델 파라미터(§7.1.4)가 Appendix 에 상세. 다만 옵티마이저·학습 스텝·seed 세부는 본문에서 완전히 확인되지 않아 완전 재현엔 저자 코드 공개가 관건입니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P1(heterogeneous Body/Hand action-expert)** — 이 논문의 핵심은 **action-space 표현·분해 아키텍처**로, P1 스카우팅 렌즈(action-expert / action-space architecture 계열)에 정면으로 들어옵니다. 특히 저주파(coarse 전역 이동)↔고주파(fine 접촉·정렬) 분해는 우리의 **Body(거친 macro 이동)↔Hand(접촉 정밀)** 해부학적 분리와 개념적으로 강하게 공명합니다. CSP 의 `low→high` 인과 흐름(고주파는 실현된 저주파에 조건화)은 D6(coordination direction & flow: **body→hand hierarchical**)과 D4(Body↔Hand information sharing)의 **주파수영역 대안 실현**으로 읽힙니다 — 우리는 이를 FiLM 으로 하지만, 여기서는 stop-gradient 조건화로 구현합니다.
- **P4(pretraining/preservation) D23(action representation)** — D23 v1 은 continuous flow-matching head 입니다. CSP 는 그 대안 축인 **spectral(DCT) coarse-to-fine action 표현**을 제시하며, 우리가 명시적으로 tracked 하는 FAST(Pertsch et al. 2025, DCT tokenization)의 연장선상에 있습니다. action-representation 선택지 지도에 "주파수 분해 + 인과 위계" 항목을 추가합니다.
- **Identity 지지/긴장** — Identity 는 "dexterity 를 VLA level 에서, 해부학적 Body/Hand 분해로" 주장합니다. CSP 는 *주파수축* 위계를 쓰지만 **해부학축**이 아니라는 점에서 우리와 다릅니다(긴장). 다만 "monolithic 균일 예측은 정밀 과제에서 무너진다"는 실증은 우리의 antagonist 비판을 강하게 지지합니다.
- **경쟁자 함의** — P1 Tracked Literature(§5)의 어떤 핀 논문도 주파수영역 coarse-to-fine 을 쓰지 않습니다. 정밀·노이즈 강건성을 action 표현만으로 끌어올린 사례라, Body/Hand 분해의 **비교군(comparison group)** 으로 유효합니다.

---

## ✨ 핀 논문 대비 델타

- **vs. π0 (P1/P4 핀, arXiv:2410.24164)** — π0 는 시간영역 연속 flow-matching action expert 입니다. CSP 는 action 을 **주파수영역에서 저/고로 분해하고 인과 순차 예측**한다는 점이 새롭습니다 — π0 의 "chunk 를 한 번에" 대비 "coarse 먼저, fine 을 coarse 에 조건화".
- **vs. Demystifying Action Space Design (P1 non-pinned, arXiv:2602.23408)** — 그 논문은 joint vs task/flange 등 *좌표계* 축의 action-space 를 실증합니다. CSP 는 좌표계가 아니라 **시간-주파수 축**에서 action 을 분해한다는, 직교하는 설계 차원을 엽니다.
- **vs. FAST (본문 인용, Pertsch et al. 2025)** — FAST 도 DCT 를 action tokenization 에 씁니다. CSP 의 델타는 tokenization 효율이 아니라 **coarse/fine 사이 인과 의존을 명시적으로 모델링**(stop-gradient `low→high`)한 점이며, counterfactual 로 그 방향성을 검증합니다.

---

## ⚙️ 의사결정 함의

- **D23 (action representation)** — 우리 파이프라인의 action head 를 순수 시간영역 flow-matching 으로 고정하기 전에, **DCT 기반 coarse/fine 분해**를 후보 축으로 명시적으로 올립니다. 구체 config 후보: action chunk 에 type-II DCT 적용(twist 채널), `frequency_split` = 시연 power-spectrum 누적 에너지 90–98% 임계로 산정, 저/고 계수에 분리 회귀 손실.
- **D6 / D4 (body→hand 흐름·정보 공유)** — CSP 의 `sg(low) → high` 조건화는 우리의 body→hand FiLM 조건화에 대한 **손실-수준 대안**입니다. 만약 hand head 를 body action 의 "실현값"에 조건화하고 stop-gradient 로 body 학습 오염을 막는 변형을 시험한다면, 이 논문의 counterfactual(Table 3)이 "방향을 뒤집으면 최악" 이라는 사전증거를 제공합니다 — body→hand 방향의 근거 보강.
- **노이즈 증강 레시피** — teleoperation 데이터로 학습할 때, 우리 데이터 파이프라인에 **human-inspired noise injection**(AR(1) drift + signal-dependent scale + phase-decay $`\lambda(t)`$)을 데이터 증강으로 추가하면 정밀 과제 강건성을 끌어올릴 수 있습니다. 특히 손끝 접촉(고주파)이 핵심인 dexterous 과제에 직접 관련.
- **평가 지표** — chunk length 를 키우며 정밀 과제 성공률의 감쇠 곡선을 baseline 대비로 재는 CSP 의 프로토콜(Table 1)을 우리 action-space 비교 평가에 채택할 만합니다("look-ahead 늘려도 성능 보존" 을 정량 지표화).

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 확인) spectrum 분리 가정의 성립 여부** — 우리 시연/타깃 embodiment 의 action chunk 을 DCT 로 변환해 power spectrum 을 그려, 저주파에 에너지가 몰리고 고주파에 노이즈가 실리는지 먼저 확인. 만약 우리 고DoF 손 데이터가 이 clean 한 분리를 보이지 않으면($`\eta^{\mathrm{low}}\approx 0`$ 가정 붕괴) CSP 의 이득 근거가 사라집니다.
- **gripper/이산 접촉 채널** — CSP 는 twist 6D 에만 DCT 를 겁니다. 우리 Hand output(finger joint command, D3)은 다지·접촉 이산 신호가 많아, 주파수 분해가 오히려 접촉 개폐 타이밍을 흐릴 수 있습니다. 손 관절에 DCT 를 그대로 적용하기 전, 접촉-이산 채널을 spectral 밖으로 빼는 우회가 필요한지 소규모로 검증.
- **다지 손의 chunk 길이·control rate** — 논문은 arm(Franka) twist 기준입니다. Hand System0(P3)의 고주파 안정화는 별도 control rate 를 쓸 수 있어, arm 용 chunk 길이·split 이 손에 그대로 전이되지 않습니다. D5(control-rate separation) 가정과 충돌 가능.
- **추론 지연** — 2-stage 순차 예측이 우리의 실시간 요구(특히 System0 접촉 안정화 루프)와 상충할 수 있습니다. 저주파→고주파 순차 latency 를 측정해, 반응 제어 대역에서 병목이 되는지 확인.
- **π backbone 통합** — CSP 는 GPT-style trunk 를 처음부터 학습합니다. 우리는 frozen π0 backbone + action expert(D7) 를 씁니다. spectral head 를 π 의 flow-matching expert 자리에 끼울 때, backbone prior 보존(D19 freeze)과 양립하는지 별도 확인 필요.

---

## 💡 컨텍스트 제안

- **P1 §5 non-pinned 후보** — 이 논문을 P1 Methodology base(non-pinned)에 "spectral coarse-to-fine action 표현 / body→hand 인과 흐름의 주파수영역 대안(D6/D23 evidence)" 역할로 추가 검토를 제안합니다(핀 교체는 아님 — 해부학축이 아니라 주파수축이므로 north star 와는 직교).
- **D23 tracked 변수** — "action representation" 선택지 지도에 **DCT coarse/fine 분해 + `low→high` 인과 위계**를 FAST 계열의 확장으로 명시 등재할 것을 제안합니다.
- (context/ 파일은 수정하지 않았습니다 — 위는 사람 판단용 제안입니다.)

> 💡 base 매핑은 `/implement-design analysis/2606.29570/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
