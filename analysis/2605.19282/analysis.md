# Paper Analysis — Rethinking Muon Beyond Pretraining: Spectral Failures and High-Pass Remedies for VLA and RLVR

> PROBE analysis 모드 산출물. 단일 한글 문서이며, 영문 1차 파일은
> 없습니다. 형식·이모지·용어 규칙은 `docs/STYLE.md` §5 / §4 를
> 정확히 따릅니다. 재실행 시 이 파일을 덮어씁니다.

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Rethinking Muon Beyond Pretraining: Spectral Failures and High-Pass Remedies for VLA and RLVR |
| 저자 | Chongyu Fan, Gaowen Liu, Mingyi Hong, Ramana Rao Kompella, Sijia Liu (Michigan State University · Cisco · University of Minnesota · IBM Research) |
| 링크 | [arXiv:2605.19282](https://arxiv.org/abs/2605.19282) |
| 발행일 / 버전 | 2026-05-19 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-05-26 |

---

## 🧭 한 줄 요약 (TL;DR)

Muon 의 Newton–Schulz 균일 spectral whitening 이 VLA 의 저-rank action gradient 와 RLVR 의 저-SNR policy gradient 양쪽에서 잡음을 증폭한다는 점을 처음으로 짚어 내고, NS 다항식을 Promotion + Suppression 2단계로 재설계한 spectral high-pass 옵티마이저 Pion 을 제안합니다. 동일한 per-step 비용으로 VLA-Adapter / VLANeXt / π $`_{0.5}`$ 및 GRPO/GMPO Qwen3 학습에서 AdamW · Muon 를 모두 능가하며, RLVR 에서 Muon 이 collapse 하는 구간에서도 안정적으로 학습됩니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제**: Muon (Newton–Schulz 기반 spectral 옵티마이저) 이 LLM pretraining 에서는 검증됐지만, 사전학습 이후의 두 체제, 즉 (i) cross-modality VLA 학습과 (ii) verifiable reward 기반 RL(RLVR) 에서도 유효한지, 그리고 한계는 무엇인지를 묻습니다.
- **기존 접근의 한계**: Muon 의 `msign` 은 모든 singular value 를 $`1`$ 로 끌어올리는 균일 whitening 이라, action head 처럼 gradient 가 본질적으로 저-rank 인 모듈에서는 noise tail 까지 동급으로 증폭하고, RLVR 처럼 gradient SNR 이 낮은 체제에서는 정책을 빠르게 망가뜨립니다. Low-Rank Muon (LRMuon) 은 SVD/sketching 으로 대응 가능하지만 NS 대비 약 $`15\times`$ 학습시간을 요구해 확장성이 떨어집니다.
- **본 논문의 가설**: VLA 와 RLVR 의 실패는 "정보가 head 에 몰리고 tail 은 잡음" 이라는 공통 spectral 구조에서 비롯되므로, NS 다항식을 promotion(상위 증폭) + suppression(하위 감쇠) 의 high-pass 형태로 바꾸면 같은 비용에서 두 체제 모두 회복된다.
- **왜 지금 중요한가**: VLA 와 RLVR 이 사전학습 후속의 두 표준 단계로 자리잡고 있는데, 두 단계 모두에서 매트릭스 인식 옵티마이저는 거의 검증된 바가 없습니다. 옵티마이저 차원의 개입은 backbone 구조를 손대지 않고도 학습 효율을 끌어올릴 수 있는 직교축이라 영향 폭이 큽니다.

---

## 🧩 핵심 기여

- Muon 이 VLA(저-rank action gradient) 와 RLVR(저-SNR policy gradient) 에서 fundamental 한 한계를 보인다는 점을, erank · SNR 측정으로 처음 분리해 보입니다 (Sec. 4, Limitation 1·2).
- NS 한 step 을 SVD 로 인수분해하면 scalar 다항식 $`f(\sigma)=a\sigma+b\sigma^3+c\sigma^5`$ 의 reshape 임을 명시적으로 보이고(Appendix D), NS 재설계 문제를 다항식 계수 설계로 환원합니다.
- 그 위에서 Promotion 다항식 $`f_p`$(계수 $`(1.875,-1.25,0.375)`$) 와 Suppression 다항식 $`f_s`$(계수 $`(0,2.5,-1.5)`$) 를 닫힌 형태로 유도하고, $`k=5`$ NS step 을 $`(k_p,k_s)`$ 로 분할하는 단일 hyperparameter 만으로 high-pass cutoff 를 조정하는 Pion 을 제안합니다.
- Attention projection 을 head 차원으로 reshape 해 head 별로 독립 NS 를 돌리는 per-head 모드를 추가합니다. 이를 통해 사전학습 시점의 head 별 norm 이질성(Appendix G) 이 보존됩니다.
- VLA-Adapter / VLANeXt / 실로봇 π $`_{0.5}`$ + DROID, 그리고 Qwen3-1.7B/4B × GRPO·GMPO × MATH·GSM8K 까지 광범위 평가에서 Pion 이 AdamW · Muon 을 일관되게 추월하며, RLVR 에서 Muon 의 collapse 와 대조를 이룹니다.
- 역방향 ablation 으로 LPMuon(저역통과 변형) 을 만들어, Pion 의 이득이 단순 NS 구조가 아니라 "high-pass 방향" 자체에서 온다는 점을 분리해 보입니다.

---

## 🔑 기술 키워드

- **Muon**: Newton–Schulz 반복으로 모멘텀 행렬의 singular value 를 1 로 균일하게 정렬하는(=matrix sign) spectral 옵티마이저. SGD/AdamW 와 달리 가중치의 행렬 구조를 그 자체로 활용합니다.
- **Newton–Schulz (NS) iteration**: 행렬 sign 함수의 다항식 근사. 본문에서는 5차 다항식 $`a\sigma+b\sigma^3+c\sigma^5`$ 로 표현되며, 계수만 바꾸면 같은 비용으로 다른 spectral 변환이 됩니다.
- **msign / matrix sign**: $`\mathbf{U}\mathbf{V}^\top`$. SVD 의 모든 σ 를 1 로 두는 연산이며, 균일 spectral whitening 의 다른 이름입니다.
- **Effective rank (erank)**: 특이값 분포의 entropy 지수, $`\exp(H(\mathbf{p}))`$. "gradient 에너지가 몇 방향에 퍼져 있는가" 의 연속적 척도입니다.
- **Gradient SNR**: $`\|\mathbb{E}[\mathbf{G}]\|_F^2 / \mathbb{E}\|\mathbf{G}-\mathbb{E}[\mathbf{G}]\|_F^2`$. 배치 기대값 대비 변동의 비로, RLVR 잡음을 정량화하는 잣대입니다.
- **High-pass NS**: Pion 의 핵심. 큰 σ 는 1 에 고정하고 작은 σ 는 0 으로 끌어내리는 sharp cutoff 형태의 NS 다항식 시퀀스입니다.
- **Promotion / Suppression 다항식**: 각각 상위 σ 를 끌어올리는 단계와 하위 σ 를 끌어내리는 단계. (P1) $`f(1)=1`$, (P2) $`f'(1)=0`$ 등 boundary 조건으로 계수가 닫힌 형태로 결정됩니다.
- **Per-head 모드**: attention projection 행렬을 head 축으로 reshape 한 뒤 head 별로 NS 를 독립 적용. 사전학습으로 형성된 head 별 norm 이질성을 깨지 않기 위한 장치입니다.
- **VLA action head**: vision-language backbone 위에 얹는 연속 액션 출력 모듈. $`\ell_1`$-regression (VLA-Adapter) 과 flow-matching (VLANeXt, π $`_{0.5}`$) 의 두 갈래가 본 논문 실험 대상입니다.
- **RLVR (Reinforcement Learning with Verifiable Rewards)**: 규칙 기반 검증 가능한 보상으로 LLM 을 사후 학습하는 패러다임. GRPO, GMPO 가 대표 알고리즘이며, token 단위 supervision 인 SFT 와 달리 trajectory 단위 sparse 보상이 SNR 을 떨어뜨립니다.

---

## 🔬 방법론

### 직관

Muon 의 약점과 Pion 의 처방은 한 도식이 양쪽 약점을 같은 평면에 놓는 방식으로 잡힙니다. VLA 의 action gradient 든 RLVR 의 policy gradient 든, SVD 를 적용해 보면 정보는 *몇 개 leading singular value* 에 몰리고 나머지 tail 은 잡음입니다. Muon 의 `msign` 은 이 둘을 같은 magnitude($`=1`$) 로 들어 올리므로 잡음이 곧장 update 에 실립니다. 처방은 단순합니다. "큰 σ 는 손대지 않고, 작은 σ 는 죽이는" spectral high-pass 를 NS 단계에서 구현하면 됩니다.

> "Muon's $`\mathrm{msign}`$, by driving every $`\sigma_i`$ to $`1`$, lifts this tail to the same magnitude as the head and corrupts the update in both regimes." (§5)
> (요지: 두 체제의 실패를 하나의 spectral 원인으로 묶고, 처방의 방향—곧 high-pass—을 못박는 앵커 문장입니다.)

![Figure 1 — VLA 모듈별 erank 와 LIBERO 성공률](https://arxiv.org/html/2605.19282/x1.png)

> "Figure 1: Limitations of Muon in VLA training (VLA-Adapter on LIBERO Object). (a) Average per-module gradient erank (V/L/A) along the training trajectory" (§4)
> 맥락: vision/language 모듈의 gradient 는 고-rank, action 모듈은 일관되게 저-rank. 이 비대칭이 Muon 균일 whitening 의 첫 번째 한계를 시각화합니다.

### 아키텍처

Pion 은 Muon 의 모든 외부 흐름(모멘텀 누적, weight update 식)을 유지한 채 NS step 의 다항식만 바꾸는 drop-in 입니다. 한 NS step 은 SVD 로 다음과 같이 인수분해됩니다.

$$\mathbf{X}\;\leftarrow\;a\,\mathbf{X}+b\,\mathbf{X}\mathbf{X}^{\top}\mathbf{X}+c\,\mathbf{X}(\mathbf{X}^{\top}\mathbf{X})^{2}$$

> "the NS step preserves $`(\mathbf{U},\mathbf{V})`$ and independently reshapes each $`\sigma_i\in[0,1]`$ through the polynomial $`f(\sigma;\,a,b,c):=a\sigma+b\sigma^3+c\sigma^5`$." (§5)
> 풀어쓰면, NS 한 step 의 본질은 *스칼라 다항식 reshape* 입니다. 이후 모든 설계는 이 다항식 위에서 이루어집니다.

NS 총 $`k=5`$ step 을 다음 두 단계로 나눕니다.

- **Promotion 단계** ($`k_p`$ step): 모든 σ 를 단조 증폭합니다. 제약 (P1) $`f_p(1)=1`$, (P2) $`f_p'(1)=0`$, (P3) $`f_p''(1)\le 0`$, 그리고 $`[0,1]`$ 위 단조성에서 계수 $`(a_p,b_p,c_p)=(1.875,-1.25,0.375)`$ 가 나옵니다. 도함수는 perfect square $`f_p'(\sigma)=1.875(1-\sigma^2)^2\ge 0`$.
- **Suppression 단계** ($`k_s=k-k_p`$ step): 큰 σ 는 1 에 고정하고 작은 σ 는 0 으로 끌어내립니다. 제약 (P1)(P2) 에 $`f_s'(0)=0`$ 을 추가하면 계수 $`(a_s,b_s,c_s)=(0,2.5,-1.5)`$ 가 나옵니다.

$`k_p\in\{0,1,\ldots,5\}`$ 가 high-pass cutoff 를 조절하는 단일 hyperparameter 입니다. 본 논문은 경험적으로 $`k_s\ge 3`$ 의 Suppression-dominant 분할을 권장합니다.

![Figure 3 — NS 다항식 시각화 (Muon · Pion-Promotion · Pion-Suppression)](https://arxiv.org/html/2605.19282/x6.png)

> "Figure 3: Visualization of $`f(\sigma)`$ in (6) over $`\sigma\in[0,1]`$, with $`f(\sigma)=\sigma`$ shown as the identity reference." (§5)
> 요지: Muon 의 균일 mapping (a) 와 Pion 의 promotion (b), suppression (c), 합성 high-pass (d) 가 같은 좌표계에서 비교됩니다.

Per-head 모드는 attention projection $`\mathbf{W}_{\{Q,K,V,O\}}\in\mathbb{R}^{d\times d}`$ 를 head 차원으로 reshape 해 $`H`$ 개의 sub-block 으로 자른 뒤 각각 NS 를 돌리는 방식이며, 추가 비용은 없습니다.

### 학습 목표 / 손실

Pion 자체는 옵티마이저이므로 새로운 손실을 추가하지 않습니다. 가중치 update 는 Muon 형식을 그대로 따릅니다.

$$\mathbf{\Theta}_t=\mathbf{\Theta}_{t-1}-\eta\,\mathrm{msign}(\mathbf{M}_t),\quad \mathbf{M}_t=\mu\mathbf{M}_{t-1}+\mathbf{G}_t$$

> "where $`\eta>0`$ is the step size, and $`\mathrm{msign}(\cdot)`$ denotes a matrix sign operator, also known as gradient orthogonalization, which transforms the momentum $`\mathbf{M}_t`$ in the spectral domain by mapping its singular values to $`1`$ while preserving the singular vectors." (§3)
> 맥락: Pion 은 이 식에서 `msign` 만 high-pass NS 로 교체합니다. 손실, 스케줄러, 모멘텀 계수는 Muon 과 같습니다.

Pion 의 `msign` 자리에는 $`k_p`$ 번의 Promotion 다항식 적용 후 $`k_s`$ 번의 Suppression 다항식 적용이 들어갑니다. 입력은 Muon 처럼 사전에 $`\mathbf{X}\leftarrow\mathbf{X}/(\|\mathbf{X}\|_F+\epsilon)`$ 로 정규화돼 singular value 가 $`[0,1]`$ 에 갇힙니다.

### 학습 셋업

- **VLA**: VLA-Adapter($`\ell_1`$-regression) 와 VLANeXt(flow-matching) 를 LIBERO 4-suite 및 LIBERO-Plus 에서 학습/평가합니다. 옵티마이저 배치는 (i) AdamW 전역, (ii) Muon: 임베딩/출력층 제외 모든 2D 행렬 + 그 외 AdamW, (iii) Pion: action 2D 행렬에 Pion + vision/language 2D 에 Muon + 나머지 AdamW. 실로봇 평가는 π $`_{0.5}`$ + DROID, Franka Research 3, 세 grasp-and-place task, 20,000 step 학습 · 30 trial × 3 task.
- **RLVR**: Qwen3-1.7B / Qwen3-4B 를 GRPO (shao2024deepseekmath) 및 GMPO (zhao2025geometric) 로 사후학습합니다. 데이터는 MATH levels 3–5 학습 / MATH500 평가, GSM8K train / test. 옵티마이저 구조는 동일하고, Pion 은 per-head 모드를 씁니다.
- **k 분할**: 본문은 $`k=5`$ 고정, $`k_s\ge 3`$ 권장 (Suppression-dominant). 정확한 $`(k_p,k_s)`$ 는 Appendix H 에 task 별로 명시되어 있습니다.

---

## 📊 실험 설정과 결과

LIBERO Object 의 VLA-Adapter 학습은 Pion 의 가장 인상적인 step-efficiency 증거입니다.

> "reaching $`100\%`$ success rate on LIBERO Object after $`1{,}500`$ training steps with VLA-Adapter, vs. $`97.0\%`$ for Muon and only $`32.2\%`$ for AdamW." (Abstract, §6.2)
> 요지: 같은 1,500 step budget 에서 AdamW 는 30%대에 머무는 반면 Pion 은 saturate 합니다. action head 의 저-rank 구조에 high-pass 가 즉시 들어맞는다는 뜻입니다.

![Figure 5 — LIBERO 4-suite 성공률 및 Object 학습 곡선](https://arxiv.org/html/2605.19282/x12.png)

> "Figure 5: AdamW, Muon and Pion for VLA-Adapter on LIBERO. (a) Test success rates on LIBERO Object, Spatial, Goal and Long at the same training budget" (§6.2)
> 맥락: 4 suite 모두 Pion ≥ Muon > AdamW 순서이며, Object 학습곡선은 Pion 이 500 step 만에 95.4% 에 도달하는 step-efficiency 를 강조합니다.

| 평가 셋팅 | AdamW | Muon | Pion |
|---|---|---|---|
| LIBERO Object @1,500 step (VLA-Adapter) | 32.2% | 97.0% | 100% |
| LIBERO Object @500 step (VLA-Adapter, Pion) | — | — | 95.4% |
| 실로봇 Franka, 평균 (3 task, π $`_{0.5}`$, 20k step, 30 trial) | 31.1% | 38.9% | 85.6% |

> "Pion sharply outperforms both baselines on every task, lifting the average success rate from 31.1% (AdamW) and 38.9% (Muon) to 85.6%." (§6.2, Table 3)
> 풀어쓰면, 시뮬레이션 step-efficiency 가 실로봇으로 동일하게 전이된다는 확인입니다. 20k step 은 통상 AdamW-VLA 학습 대비 적은 budget 입니다.

LIBERO-Plus(분포 변동) 에서도 우위는 유지·증폭됩니다.

> "its advantage is preserved and amplified on the more challenging LIBERO-Plus split, notably under Language (+9%), Noise (+6%), and Robot (+6%) perturbations." (§6.2, Table 1)
> 해석: Muon 의 균일 whitening 이 비일반화 잡음 방향까지 증폭하는 반면, Pion 의 high-pass 는 분포 변동 robustness 도 함께 끌어올립니다.

RLVR 결과는 더 극단적입니다.

> "Muon consistently fails: accuracy remains near zero throughout training and often falls below the initial checkpoint." (§6.3, Fig. 6)
> 요지: GRPO/GMPO × Qwen3-1.7B/4B × MATH/GSM8K 의 8 조합 전부에서 Muon 은 collapse 합니다. 저-SNR gradient 가 Muon 의 균일 whitening 을 만났을 때 무슨 일이 벌어지는지 보여 주는 증거입니다.

> "LPMuon fails to train: as shown in Fig. 8-(b), its accuracy remains at the initial checkpoint, in stark contrast to Pion." (§6.3)
> 풀어쓰면, 같은 NS 골격에서 high-pass 를 low-pass 로 뒤집은 LPMuon 은 학습이 되지 않습니다. Pion 의 이득이 "spectral 방향 자체"에서 온다는 reverse ablation 입니다.

---

## ⚖️ 한계

- 실험 backbone 이 VLA-Adapter / VLANeXt / π $`_{0.5}`$ 와 Qwen3-1.7B/4B 로 한정됩니다. 더 큰 VLM 백본이나 다른 action head 패밀리(예: discrete diffusion, FAST tokenization)에서 동일하게 동작하는지는 미검증입니다 (저자 Appendix M 한계 명시).
- $`k_p`$ 가 단일 hyperparameter 라지만 task 별 최적값은 여전히 sweep 가 필요합니다. 본문은 $`k_s\ge 3`$ 만 권장할 뿐, 자동 선택 기준은 제시하지 않습니다.
- VLA 에서는 default 모드를, RLVR 에서는 per-head 모드를 권장하는데, "어떤 체제에 어떤 모드"의 결정 기준이 사후적이며 head-norm 이질성을 사전 진단해 자동으로 고르는 절차도 없습니다.
- LIBERO 와 GSM8K/MATH 는 매우 익숙한 셋이라, "AdamW 가 32%에 머무름" 같은 결과는 AdamW baseline 의 하이퍼 튜닝 강도에 민감합니다. Appendix H 외 추가 외부 검증이 필요합니다.
- Per-head 모드의 reshape 가 grouped-query / multi-query attention 처럼 head 수가 비대칭인 구조에서 어떻게 동작하는지는 논의가 부재합니다.

---

## ♻️ 재현성

- 코드: GitHub 및 Project Page 링크가 abstract 상단에 제시되어 있습니다(본문상 두 링크 모두 명시).
- 데이터: LIBERO / LIBERO-Plus / MATH / MATH500 / GSM8K 는 모두 공개 셋입니다. DROID 셋업의 real-robot trial 데이터는 일반적으로 비공개.
- 하드웨어: 실로봇 평가는 Franka Research 3 (DROID 셋업) 에서 3 grasp-and-place task. 시뮬레이션은 LIBERO/MuJoCo 기반.
- 알고리즘: 다항식 계수가 닫힌 형태로 유도되고(Appendix E) Pion full algorithm 이 Appendix F 에 명시되므로, Muon 구현이 있다면 다항식 계수만 교체해 재현할 수 있습니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P4 (VLM Pretraining Preservation) — 간접 지지**. Pion 의 per-head 모드는 "사전학습으로 형성된 head 별 norm 이질성을 깨지 않는다"는 동기에서 출발하며, D19(VLM FT range) · D20(prior-preservation strategy) 의 정신과 같은 방향입니다. 다만 backbone 자체를 freeze 하지 않으므로 D19(a) 의 증거 자체는 되지 않습니다.
- **P1 (Heterogeneous Body/Hand Action Expert) — 간접**. VLA-Adapter / VLANeXt / π $`_{0.5}`$ 는 §8.1 / §8.4 핀 논문 라인업과 그대로 겹칩니다. Pion 은 action 2D 행렬에만 Pion 을, V/L 에는 Muon 을 쓰는 "modality-wise optimizer assignment" 를 권장하는데, 이는 D1(arm-hand split) 의 구조적 분리와는 다른 *옵티마이저 차원의 분리* 이지만 같은 비대칭을 인정하는 증거가 됩니다.
- **D21 (Staged training recipe, P4) — 잠재 영향**. Stage 2 (VLM-freeze, Body/Hand experts 학습) 에서 옵티마이저로 AdamW 가 아닌 Pion(action head) + Muon(V/L) 을 쓰는 것이 step-efficiency 측면에서 매력적임을 시사합니다.
- **§8 Tracked Literature methodology base**: FiLM / PCGrad 와 같은 *방법론 base* 층의 후보. 어느 단일 Pillar 의 pinned 자리에 들어가기보다는, P1/P4 학습 recipe 의 옵티마이저 base 로 검토할 가치가 있습니다.
- **§10 Competitor 함의**: 없음. 본 논문은 optimizer 논문이라 §10 (VLA-only strong performers / Bounded RL) 와 곧장 경쟁하는 라인은 아닙니다.
- **Anti-topics 점검**: "RL reward-engineering for generalized full-task" 가 아닌 *옵티마이저 mechanics* 이므로 RLVR 부분도 anti-topic 에 걸리지 않습니다. VLA 부분 역시 arm-hand split / structured binding / VLM-preservation / System0 의 4 in-scope 조건과는 직교한 *학습 recipe* 층이라, 핀 자리는 아니되 methodology base 후보로는 수용 가능합니다.
- **Identity 긴장/지지**: 긴장 없음. heterogeneous-decoder claim 과는 무관합니다. 다만 step-efficiency 가 진짜라면 CP1 sim ablation 의 학습 cost 를 압축할 수 있어 *지지 방향* 입니다.

---

## ✨ 핀 논문 대비 델타

- **VLA-Adapter ([arXiv:2509.09372](https://arxiv.org/abs/2509.09372), §8.4 P4 pinned) 대비**: VLA-Adapter 는 Bridge Attention 으로 backbone 보존을 챙긴 *아키텍처* 기여입니다. 본 논문은 같은 VLA-Adapter 를 *학습 옵티마이저* 차원에서 가속합니다 (Object 1,500 step 에서 100% vs Muon 97% vs AdamW 32.2%). 두 기여는 직교하며 결합할 수 있습니다.
- **π $`_{0.5}`$ ([arXiv:2504.16054](https://arxiv.org/abs/2504.16054), §8.1/§8.4 pinned) 대비**: π $`_{0.5}`$ 는 backbone + hierarchical inference 가 핵심입니다. 본 논문은 π $`_{0.5}`$ 를 손대지 않고 finetuning 하면서 옵티마이저만 Pion 으로 바꿔 실로봇 31.1%→85.6% 를 보입니다. π $`_{0.5}`$ 의 학습 recipe 에 곧장 얹어 평가할 수 있는 보완입니다.
- **MolmoAct2 ([arXiv:2605.02881](https://arxiv.org/abs/2605.02881), §8.4) 대비**: MolmoAct2 는 per-layer KV-cache conditioning 으로 VLM 을 보호하고, 본 논문은 per-head NS reshape 로 사전학습 head 이질성을 보호합니다. *어디서 보존을 책임지는가* 라는 같은 질문에 다른 층(아키텍처 vs 옵티마이저)에서 답하는 자매 접근입니다.
- **PriorVLA ([arXiv:2605.10925](https://arxiv.org/abs/2605.10925), §8.4) 대비**: PriorVLA 는 frozen Prior Expert + Adaptation Expert 의 *모듈 분리* 로 prior 를 보존합니다. Pion 의 per-head 모드는 *동일 모듈 안에서 update 의 spectral 형태* 로 prior 를 보존하는데, 더 미세한 층에서 같은 목표를 추구하는 셈입니다.
- **§8 methodology base 대비**: FiLM, PCGrad, DQ-RISE 가 차지하던 "특정 학습 trick" 자리에 Muon · Pion 류 옵티마이저가 들어올 여지가 있습니다. PROBE 컨텍스트에 *옵티마이저 base* 가 명시되지 않은 상태이므로 새로운 카테고리 후보입니다.

---

## ⚙️ 의사결정 함의

- **Optimizer config 키 후보**: Stage 2 학습에서 `optimizer.body.cls = Muon`, `optimizer.hand.cls = Pion`, `optimizer.vlm.cls = Muon`, `optimizer.fallback.cls = AdamW` 같은 modality-wise 분리 설정을 도입합니다. 본 논문은 V/L=Muon, action=Pion, 그 외=AdamW 를 권장합니다.
- **Pion 하이퍼**: `pion.k = 5` (Muon per-step cost 보존), `pion.k_s ≥ 3` (Suppression-dominant), 초기값 후보 `pion.k_p = 1, pion.k_s = 4` (action head 저-rank 강도가 클수록 k_s 를 키웁니다).
- **Per-head 모드 트리거**: D19 가 (a) 전체 freeze 에서 (c)(d) 부분 unfreeze 로 이동하는 시점에, attention projection 에 한해 Pion per-head 모드를 활성화합니다. (지금 v1 에선 backbone freeze 이므로 곧장 영향이 발생하지는 않습니다.)
- **CP1 ablation 학습 budget**: VLA-Adapter Object 의 100% @1,500 step 결과가 우리 스택에서 재현되면, 4-contribution ablation (D25) 각 셀의 학습 step budget 을 줄여 운용 비용을 압축할 수 있습니다. step-efficiency 가 안 나오면 즉시 폐기.
- **Falsifier 지표 단단해짐**: D26 의 contact-precision (slip count, pose stability) 측정 전에, 옵티마이저 효과를 분리하기 위해 동일 backbone × AdamW vs Pion 의 1 차 비교 셀을 ablation 매트릭스에 한 줄 추가합니다. AdamW vs Muon vs Pion 3-way 가 부담스러우면 AdamW + Pion 만.
- **결정 모호함 회피**: Pion 의 per-head 모드가 grouped-query attention(우리 backbone 후보 중 일부, π 계열) 의 KV head 분배와 호환되는지 한 번 확인이 필요합니다. 호환되지 않으면 default 모드만 사용.

---

## ⚠️ 먼저 검증할 실패 모드

- **저-rank 가정 깨짐**: 우리 action head 는 D3(finger joint command) + D2(both-wrist pose) 의 비교적 풍부한 출력 공간에 D4 FiLM 을 결합한 구조입니다. Pion 이 가정하는 "action gradient 가 매우 저-rank" 가 우리 split-head 구조에서도 유지되는지부터 측정해야 합니다. *sanity check 1*: 본 논문의 erank 측정(eq. 4) 을 우리 baseline run 에서 한 시간 정도 돌려 보고 erank ≤ 3–5 면 청신호.
- **k_p / k_s sweep 비용**: 권장이 $`k_s\ge 3`$ 이지만 task 별 sweep 가 필요합니다. 첫 도입 시 $`(k_p, k_s) = (1,4)`$ 한 점만 고정해, AdamW baseline 대비 step-efficiency 가 1.5× 이상 안 나오면 폐기합니다. sweep 자체에 학습 비용을 태우지 않습니다.
- **per-head reshape 호환성**: π $`_{0.5}`$ / VLA-Adapter / VLANeXt backbone 의 attention 이 multi-head 표준이 아니면(예: GQA, MQA) reshape 정의가 ambiguous 합니다. 첫 단계는 default 모드만 적용합니다.
- **실로봇 step-efficiency 전이성**: 본 논문 Table 3 의 31.1→85.6 점프는 매우 큰데, 30 trial × 3 task 의 평균이라 variance 가 클 수 있습니다. 우리 in-hand rotation 실험에서는 50+ trial 기준이라, 곧장 비교하기 전에 *variance 측정* 부터.
- **RLVR 결론의 무관성**: System0(P3) RL 은 *지속적 정책 그래디언트* 가 아니라 *post-grasp 짧은 sub-loop* 입니다. Pion 의 RLVR 우위가 우리 System0 에 그대로 옮겨오는지는 별개 검증 사항이며, 우선 P1/P4 VLA training 으로만 효과를 검증합니다.

---

## 💡 컨텍스트 제안

- **§8 Tracked Literature methodology base 후보 신설**: 현재 §8.1 P1 의 "Methodology base" 줄에 FiLM / PCGrad / DQ-RISE 가 있고 §8.3 P3 에 Eureka 류 옵티마이저성 base 가 있어 base 층이 분산돼 있는 상태입니다. *학습 옵티마이저 base* (Muon, Pion 류) 를 별도 카테고리로 추가할지 검토합니다. 단, 1편으로 신설하기보다는 Muon (jordan2024muon) + Pion 의 2편이 모일 때 카테고리화하는 편이 합리적입니다.
- **D21 (Staged training recipe) 하위 노트 추가 제안**: Stage 2 학습에서 modality-wise optimizer assignment (action=Pion, V/L=Muon, else=AdamW) 를 *deferred candidate* 로 등재. Trigger: AdamW baseline 으로 Stage 2 가 in-distribution plateau 에 빨리 닿지 못할 때 / CP1.
- **§9 Researchers — 추가 후보**: Sijia Liu (Michigan State), Mingyi Hong (UMN) 의 spectral / matrix-aware optimizer 라인. 우리 핵심 분야는 아니지만 매트릭스 인식 옵티마이저 흐름을 따라가려면 follow 후보.
- **D25 4-contribution ablation 가벼운 보강**: falsifier 평가 비용을 줄이려면 옵티마이저 sweep(AdamW vs Pion) 한 셀을 ablation 안에 합치는 안을 검토 (우선순위 낮음. Pion 도입 후 별개 ablation 으로 분리하는 편이 깔끔할 수 있습니다).

> 💡 base 매핑은 `/implement-design analysis/2605.19282/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
