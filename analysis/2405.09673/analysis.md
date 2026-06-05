# Paper Analysis — LoRA Learns Less and Forgets Less

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | LoRA Learns Less and Forgets Less |
| 저자 | Dan Biderman, Jacob Portes, Jose Javier Gonzalez Ortiz, Mansheej Paul, Philip Greengard, Connor Jennings, Daniel King, Sam Havens, Vitaliy Chiley, Jonathan Frankle, Cody Blakeney, John P. Cunningham |
| 링크 | [arXiv:2405.09673](https://arxiv.org/abs/2405.09673) · [HuggingFace](https://huggingface.co/LoRA-TMLR-2024) |
| 발행일 / 버전 | 2024-05-15 제출 · 2024-09-20 개정 · v2 (TMLR 게재본) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-05-28 |
| 관련 Pillar | P4 |
| 태그 | peft, forgetting |

---

## 🧭 한 줄 요약 (TL;DR)

LoRA 는 일반적인 저랭크 설정에서 코드·수학 같은 어려운 신규 도메인을 full finetuning 만큼 학습하지 못하지만(learns less), 대신 base 모델의 원래 능력을 더 잘 보존합니다(forgets less). 즉 학습량과 망각량은 LoRA 랭크로 조절되는 trade-off 관계입니다. 정작 full finetuning 이 찾는 가중치 변화량 $`\Delta`$ 는 전형적 LoRA 랭크보다 10–100배 높은 랭크를 가집니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — LoRA 가 full finetuning 대비 성능을 정말로 희생시키는지가 미해결입니다. 원 LoRA·QLoRA 논문은 동등하다고 보고했지만, 반대로 미달한다는 증거도 누적되어 결론이 갈립니다.
- **기존 접근의 한계** — LoRA 의 저랭크 가정은 "finetuning 이 base 가중치에 저랭크 섭동을 준다"는 가설에 근거하나, 그 가설은 현대 LLM 에게 쉬운 과제에서만 검증되었고 코드·수학처럼 어려운 도메인에서는 미검증입니다.
- **본 논문의 가설** — 파라미터를 적게 학습하는 LoRA 는 finetuning 된 모델이 base 모델에서 크게 벗어나지 못하도록 제약합니다. 그러니 신규 도메인 학습은 덜 되더라도 catastrophic forgetting(파국적 망각) 또한 덜하리라는 것입니다.
- **왜 지금 중요한가** — LLM finetuning 은 신규 도메인 특화가 base 능력 손실을 대가로 하는 continual learning(연속 학습)의 한 형태이며, 현대 LLM 의 망각을 정량 분석한 연구가 거의 없습니다. LoRA 의 망각 완화 효과부터 체계적으로 측정하는 일이 먼저입니다.

---

## 🧩 핵심 기여

- **CPT 에서의 명확한 학습 격차** — continued pretraining(CPT, 연속 사전학습)에서 코드·수학 모두 LoRA 가 모든 설정에서 full finetuning 에 미달하며, 데이터가 늘수록 격차가 벌어집니다. instruction finetuning(IFT)에서는 높은 랭크가 격차 대부분을 메웁니다.
- **망각 완화의 정량화** — LoRA 는 source 도메인 능력을 full finetuning 보다 일관되게 더 잘 보존하며, 망각의 정도는 LoRA 랭크로 제어됩니다.
- **정규화 기법 대비 우위** — LoRA 의 망각 완화는 weight decay(가중치 감쇠)·attention dropout 같은 고전 정규화보다 더 강력하며, 생성 다양성도 더 잘 유지합니다.
- **고랭크 섭동의 발견** — SVD 분석으로 full finetuning 이 찾는 $`\Delta`$ 가 전형적 LoRA 랭크 대비 10–100배 높은 랭크임을 보여, LoRA 의 성능 격차를 부분적으로 설명합니다.
- **실전 권고** — LoRA 는 하이퍼파라미터(학습률, target module, 랭크, scaling)에 매우 민감하며, 이를 적절히 설정하는 것이 full finetuning 에 근접하기 위한 전제 조건임을 보이고 best practice 를 제시합니다.

---

## 🔑 기술 키워드

- **LoRA (Low-Rank Adaptation)** — base 가중치를 얼린 채 그 위에 저랭크 보정 행렬 두 개($`A`$, $`B`$)만 학습하는 PEFT 기법. 큰 책을 통째로 다시 쓰는 대신 얇은 정오표만 끼워 넣는 방식. 본 논문의 비교 주체.
- **Full finetuning** — 모델의 모든 가중치를 갱신하는 표준 미세조정. LoRA 의 성능·망각 기준선.
- **Continued Pretraining (CPT)** — 라벨 없는 도메인 텍스트 수십억 토큰으로 이어서 사전학습하는 체제. 본 논문에서 LoRA 가 가장 크게 미달하는 영역.
- **Instruction Finetuning (IFT)** — 질문-답변 쌍으로 미세조정하는 체제. 높은 랭크 LoRA 가 full finetuning 을 따라잡을 수 있는 영역.
- **Forgetting (망각)** — 신규 도메인 학습 과정에서 base 모델의 원래 능력이 저하되는 현상. 극단적 형태가 catastrophic forgetting(파국적 망각).
- **모방 학습 (IL)** 아님 주의 — 여기서의 "learning"은 target 도메인 벤치마크 성능 향상을 가리키는 측정 지표이며, 본 논문은 텍스트 LLM 미세조정을 다룹니다.
- **Rank of perturbation** — $`\Delta = W_{\text{finetuned}} - W_{\text{pretrained}}`$ 의 SVD 상 유효 랭크. 변형의 "복잡도"를 재는 자. 90% 분산 설명에 필요한 특이벡터 수로 추정.
- **$`\alpha/r`$ scaling** — LoRA 보정의 크기를 정하는 스칼라. 본 논문은 높은 랭크에서 $`\alpha = 2r`$ 설정이 결정적이라고 봅니다.
- **Target modules** — LoRA 를 부착할 가중치 행렬 집합(attention 의 $`W_q,W_k,W_v,W_o`$ / FFN 의 $`W_{\text{gate}},W_{\text{up}},W_{\text{down}}`$). "All" 부착이 attention-only 보다 우수.
- **Distribution collapse** — full finetuning 이 base 대비 생성 다양성을 잃어 소수의 출력에 몰리는 현상. LoRA 가 이를 완화.

---

## 🔬 방법론

### 직관

이 논문의 설계 의도는 알고리즘 제안이 아니라 통제된 비교 측정입니다. 핵심 직관은 이렇습니다. "학습(target 도메인 향상)"과 "망각(source 도메인 저하)"을 같은 축 위에서 동시에 재면, LoRA 와 full finetuning 은 단순한 우열이 아니라 서로 다른 trade-off 점에 놓인다. 파라미터 수를 줄이는 것 자체가 finetuned 모델이 base 분포에서 멀리 벗어나지 못하게 하는 정규화로 작동한다는 가설을 두 도메인(코드·수학) × 두 체제(CPT·IFT)의 격자에서 검증합니다.

> "By training fewer parameters, LoRA is hypothesized to constrain the finetuned model from diverging significantly from the base model" (§1)
(LoRA 의 망각 완화 효과를 설명하는 중심 가설 — 적은 파라미터 학습이 base 모델로부터의 이탈을 구조적으로 억제한다는 것입니다.)

### 아키텍처

LoRA 는 사전학습 가중치 $`W_{\text{pretrained}} \in \mathbb{R}^{d \times k}`$ 를 얼리고 그 위에 저랭크 섭동 $`\Delta`$ 만 학습합니다.

$$W_{\text{finetuned}}=W_{\text{pretrained}}+\Delta$$

$$\Delta=\gamma_{r}AB,\quad A\in\mathbb{R}^{d\times r},\quad B\in\mathbb{R}^{r\times k}.$$

> "Most common implementations initialize $`A_{0}\sim\mathcal{N}(0,1),~{}B_{0}=0`$ and set the scalar $`\gamma_{r}=\alpha/r`$ with a controllable hyperparameter $`\alpha`$ ." (§2)
($`B`$ 를 0 으로 초기화해 학습 시작 시점에 $`\Delta = 0`$ 이 되도록 하고, 보정 크기는 $`\gamma_r = \alpha/r`$ 스칼라로 조절합니다. 사용자는 부착할 target module, 랭크 $`r \ll d,k`$, 그리고 $`\alpha`$ 를 고릅니다.)

target module 선택은 초기 LoRA 가 $`W_q,W_v`$ 만 겨냥했으나 이후 모든 transformer module 부착이 best practice 가 되었습니다.

> "Since then, it has become best practice to target all transformer modules" (§2)
(즉 self-attention 의 $`\{W_{q}^{(l)},W_{k}^{(l)},W_{v}^{(l)},W_{o}^{(l)}\}`$ 와 FFN 의 $`\{W_{\text{gate}}^{(l)},W_{\text{up}}^{(l)},W_{\text{down}}^{(l)}\}`$ 전부를 대상으로 합니다.)

![Figure 1 — LoRA vs full finetuning learning](https://arxiv.org/html/2405.09673/extracted/5869312/figures/fig1_learning.png)

> "Figure 1: LoRA performance scales by rank and underperforms full finetuning in code and math." (§4.1)
(코드·수학 양쪽에서 LoRA 의 target 도메인 성능이 랭크 순으로 정렬되며 full finetuning 에 미달함을 시각화한 그림으로, §4.1 의 핵심 주장을 떠받칩니다.)

### 학습 목표 / 손실

본 논문은 새 손실 함수를 제안하지 않고 표준 미세조정 목적(다음 토큰 예측 cross-entropy)을 LoRA 와 full finetuning 두 갈래로 최적화합니다. 분석의 무게는 학습 후 가중치 변화량 $`\Delta`$ 의 스펙트럼에 실립니다.

> "we perform a singular value decomposition to show that full finetuning barely changes the spectrum of the base model's weight matrices, and yet the difference between the two (i.e. the perturbation) is high rank." (§1)
(full finetuning 된 가중치의 스펙트럼은 base 와 거의 같지만, 그 차이인 섭동 $`\Delta`$ 자체는 고랭크라는 것이 SVD 분석의 핵심 결론입니다.)

90% 분산 설명에 필요한 랭크로 $`\Delta`$ 의 유효 랭크를 추정하며, 가장 이른 0.25B 토큰 체크포인트에서 이미 전형적 LoRA 랭크의 10–100배에 달합니다.

### 학습 셋업

- **모델** — Llama-2-7B 가 주 실험 대상입니다.
- **도메인 × 체제** — 코드/수학 × CPT/IFT 의 4 격자. CPT 데이터는 StarCoder-Python(20B 토큰으로 서브샘플)·OpenWebMath(14.7B 토큰, 20B 까지 반복), IFT 데이터는 Magicoder-Evol-Instruct-110K(72.97M 토큰)·MetaMathQA(395K 쌍, 약 103M 토큰).
- **샘플 효율 스윕** — IFT 는 1,2,4,8,16 epoch, CPT 는 0.25–20B 토큰 구간으로 학습 곡선을 측정. 각 조건마다 full finetuning 1개 + LoRA 3개($`r=16,64,256`$).
- **LoRA 설정** — 모든 transformer module 부착, $`\alpha=2r`$.
- **학습률** — 방법별 전수 학습률 스윕 후 비교(저자들이 결정적이라고 강조). LoRA 의 최적 학습률은 full finetuning 보다 한 자릿수 높으며 대체로 $`5e-5`$ ~ $`5e-4`$ 범위.

---

## 📊 실험 설정과 결과

학습 지표는 코드 HumanEval(pass@1, temperature=0.2, top_p=0.95, 0-shot, 문제당 50 생성)과 수학 GSM8K(test 1,319 샘플, temperature=0, 5-shot, pass@1)입니다. 망각 지표는 HellaSwag·ARC-Challenge·WinoGrande 세 벤치마크의 평균입니다.

| 설정 | 지표 | 최적 LoRA | Full finetuning |
|---|---|---|---|
| Code CPT | HumanEval | $`r=256`$, 20B 토큰에서 0.224 | 20B 토큰에서 0.263 (4B 에서 이미 0.218) |
| Code IFT | HumanEval | $`r=256`$ epoch 4 에서 0.498 | epoch 8 에서 0.497 |
| Math CPT | GSM8K | $`r=256`$, 16B 토큰에서 0.203 | 20B 토큰에서 0.293 (4B 에서 0.224) |
| Math IFT | GSM8K | $`r=256`$ epoch 8 에서 0.634 | epoch 4 에서 0.642 |
| Code CPT | 망각(낮을수록 보존, 높을수록 좋음) | $`r=256`$, 20B 에서 0.617 | 20B 에서 0.545 |
| Code IFT | 망각 | $`r=64`$ 에서 0.509 | 0.414 |

> "The best LoRA model, with rank $`r=256`$ , peaks at 20B tokens with HumanEval=0.224, roughly matching full finetuning with 4B tokens (HumanEval=0.218). Full finetuning reaches its peak HumanEval of 0.263 at 20B tokens." (§4.1, Table S1)
(Code CPT 에서 LoRA 최고 모델이 20B 토큰을 써서 겨우 full finetuning 의 4B 토큰 수준에 도달 — 큰 격차와 낮은 샘플 효율을 동시에 보여줍니다.)

> "With a high LoRA rank ( $`r=256`$ ), full finetuning performance can be matched (LoRA=0.498 in epoch 4, full finetuning=0.497 in epoch 8)." (§4.1, Table S5)
(Code IFT 에서는 높은 랭크 LoRA 가 full finetuning 을 사실상 따라잡습니다 — 체제에 따라 결론이 달라지는 핵심 근거.)

> "In code CPT (Table S2 ), at 20B tokens, full finetuning scores 0.545 versus 0.617 by LoRA $`r=256`$ . In code IFT (Table S6 ), full finetuning scores 0.414 versus 0.509 by LoRA $`r=64`$ ." (§4.2, Table S2, Table S6)
(망각 지표에서 LoRA 가 full finetuning 보다 일관되게 높은 점수(=더 잘 보존)를 기록합니다.)

![Figure 2 — LoRA forgets less](https://arxiv.org/html/2405.09673/extracted/5869312/figures/fig2_forgetting.png)

> "Figure 2: LoRA forgets less than full finetuning." (§4.2)
(망각 축(HellaSwag·ARC·WinoGrande 평균)에서 LoRA 가 full finetuning 대비 base 능력을 더 보존함을 4개 데이터셋에 걸쳐 보이는 그림입니다.)

학습-망각 trade-off 는 데이터셋마다 양상이 다릅니다. 일률적 우열은 내리기 어렵습니다.

> "it seems that LoRA can offer preferable learning-forgetting tradeoffs for code, while full finetuning can offer preferable tradeoffs for math." (§4.3)
(코드에서는 LoRA 가, 수학에서는 full finetuning 이 더 나은 trade-off 곡선을 그리며, LoRA 랭크는 그 곡선 위에서 위치를 정하는 제어 변수입니다.)

정규화 기법 및 다양성 비교에서:

> "LoRA, with the common $`r=16`$ , learns less and forgets less than all other models. LoRA $`r=256`$ , on the other hand, learns as much as the other methods while forgetting less." (§4.5)
(weight decay·attention dropout 는 full finetuning 만큼 학습하고 망각하는 반면, LoRA 는 망각을 더 강하게 억제합니다. full finetuning 은 생성 다양성이 붕괴(distribution collapse)되나 LoRA 는 base 와 full 사이에 위치합니다.)

고랭크 섭동 발견(SVD):

![Figure 6 — rank dynamics](https://arxiv.org/html/2405.09673/extracted/5869312/figures/svd_summary_starcoder_all.png)

> "The earliest checkpoint at 0.25B CPT tokens exhibits $`\Delta`$ matrices with a rank that is $`10-100\times`$ larger than typical LoRA ranks" (§4.6, Figure 6)
(가장 이른 체크포인트에서도 full finetuning 의 섭동 랭크가 전형적 LoRA 랭크의 10–100배이며, 데이터가 늘수록 더 커지고 MLP module 이 attention 보다 높은 랭크를 가집니다.)

하이퍼파라미터 권고:

> "we recommend: (a) using LoRA for instruction finetuning and not continued pretraining; (b) if GPU memory allows, targeting "All" transformer modules with a rank of $`256`$ , since ranks $`16-64`$ tend not to suffice for code tasks; (c) using $`\alpha=2r`$ , and (d) sweeping over learning rates between $`[1e-5,5e-4]`$ , picking the highest value that enables stable training." (§4.7)
(LoRA 실전 4대 권고 — IFT 한정 사용, All module + $`r=256`$, $`\alpha=2r`$, 안정적 최고 학습률 선택.)

---

## ⚖️ 한계

- **모델 규모 일반화 미검증** — 주 실험이 Llama-2-7B 단일 규모입니다. 70B 등 대형 모델에서 LoRA 가 더 효과적일 수 있다는 선행 단서를 인정하나, 규모 스케일링의 엄밀한 연구는 future work 로 남깁니다.
- **SVD 분석의 해석 제약** — full finetuning 이 고랭크 해를 "찾는다"는 것이 저랭크 해의 존재 가능성을 배제하지는 않습니다. 또한 SVD 분석은 CPT 에 대해서만 수행되어, IFT 에서는 full finetuning 섭동이 그만큼 고랭크가 아닐 수 있습니다.
- **도메인 범위** — 코드·수학 두 도메인, 영어 텍스트 LLM 에 국한됩니다. 멀티모달·로보틱스·비텍스트 모달리티로의 전이는 다루지 않습니다.
- **MetaMath 재현 격차** — MetaMathQA full finetuning 에서 본 논문은 GSM8K 0.642 를 얻었으나 원 MetaMath 논문은 0.665 를 보고 — 하이퍼파라미터 차이로 귀인합니다.

---

## ♻️ 재현성

- **코드·체크포인트** — 모델 체크포인트와 LoRA adapter 가 [github.com/danbider/lora-tradeoffs](https://github.com/danbider/lora-tradeoffs) 에 공개.
- **데이터** — StarCoder-Python, OpenWebMath, Magicoder-Evol-Instruct-110K, MetaMathQA 모두 공개 데이터셋(HuggingFace).
- **평가 하니스** — Code Generation LM Evaluation Harness(HumanEval) 및 LM Evaluation Harness(GSM8K, 망각 벤치마크) 등 표준 도구 사용으로 측정 재현 가능.
- **하드웨어** — 부록에 단일/다중 GPU 메모리·throughput 이론 분석(FSDP 포함)이 수록되나, 본문은 특정 학습 클러스터 스펙을 핵심 결과의 전제로 두지 않습니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

이 논문의 결과는 **P4 (VLM Pretraining Preservation)** 의 방법론 토대를 직접 떠받친다. P4 의 정체성은 "deploy 데이터로의 full fine-tuning 이 over-specialize 되어 사전학습 prior 를 침식한다"는 것인데, 본 논문은 그 침식(=forgetting)을 정량 측정하고 LoRA 가 이를 완화함을 보입니다.

- **D19 (VLM fine-tuning range)** — option (d) LoRA/adapter PEFT 의 근거 논문입니다. PROBE v1 은 (a) full freeze 이고 LoRA 는 deferred 후보이므로, 이 논문은 "freeze 가 불충분해 D19 가 (d) 로 이동할 때" 무엇을 기대·설정해야 하는지의 사전 지식입니다.
- **D20 (prior-preservation strategy)** — "LoRA-minimal" option 의 핵심 증거. LoRA 가 weight decay·dropout 보다 망각을 더 잘 막는다는 측정 결과가 D20 의 LoRA 경로를 수치로 뒷받침합니다.
- **D21 (staged training recipe)** — Stage 3(LoRA/top-layer 제한 FT) 진입 시의 설정 지침(랭크· $`\alpha`$ ·target module·학습률)을 제공합니다.
- **D23 (action representation × VLM preservation)** — 직접 다루지는 않습니다. 다만 "어려운 신규 도메인은 LoRA 저랭크로 학습이 안 된다"는 발견을 보면, 액션 표현 같은 신규 modality 학습 부담을 LoRA 에 얹는 것은 위험합니다.
- **Identity 지지/긴장** — Antagonist 가 아니라 P4 정체성을 **지지**합니다. 다만 PROBE 는 backbone 을 아예 얼리므로(D19a), 이 논문이 비교하는 두 극(LoRA vs full-FT) 모두 PROBE v1 의 freeze 보다 prior 보존에 불리하다는 점에서 직접 대응되지는 않습니다. §10 경쟁자 함의는 없습니다(텍스트 LLM 연구).

---

## ✨ 핀 논문 대비 델타

P4 핀 중 **VLM2VLA** ([arXiv:2509.22195], LoRA + NL-action, forgetting mitigation) 와 가장 가깝습니다. VLM2VLA 는 VLA 맥락에서 LoRA 로 망각을 완화하는 *적용* 사례입니다. 그 적용이 기대는 **기반 경험 법칙**을 길어 올린 원천이 바로 본 논문입니다. 핀과 구별되는 지점:

- **랭크를 trade-off 손잡이로 정량화** — VLM2VLA 는 LoRA 를 망각 완화 수단으로 채택하지만, 본 논문은 랭크가 학습량과 망각량을 동시에 움직이는 단일 조절 변수임을 4 격자에서 측정.
- **CPT vs IFT 의 분기** — LoRA 가 IFT 에서는 따라잡지만 CPT(어려운 신규 도메인 대량 학습)에서는 못 따라잡는다는 체제 의존성. 핀 논문에는 없는 구분.
- **고랭크 섭동의 SVD 증거** — full finetuning 의 $`\Delta`$ 가 고랭크라는 기제적 설명은 다른 P4 핀(π0, RT-2, MolmoAct2)들이 제시하지 않은 분석.
- **정규화·다양성 비교** — LoRA vs weight decay/dropout, 그리고 distribution collapse 완화는 핀들이 다루지 않는 부가 축.

---

## ⚙️ 의사결정 함의

이 논문이 맞다면, PROBE 가 D19 의 backbone 적응 방식을 (a) full freeze 대신 (d) LoRA 로 바꾸는 시나리오(Stage 3, D21)에서 다음 config 가 바뀝니다.

- **LoRA rank** — `r=256` 을 기본값으로 둡니다. 흔한 `r=16~64` 는 "어려운 신규 도메인"(코드·수학에 해당하는, 본 스택에서는 촉각/액션 같은 신규 modality 학습)에서 부족합니다.
- **LoRA scaling** — `lora_alpha = 2 * r` (= 512). HuggingFace `peft` 기본의 `alpha/r` scaling 이 고랭크를 깎아내리므로 명시적으로 $`\alpha=2r`$ 을 설정해야 합니다.
- **target_modules** — `"all-linear"`(attention + MLP 전부). attention-only 는 열등하며 이득의 상당 부분이 MLP 에서 나옵니다.
- **learning_rate** — full-FT 대비 한 자릿수 높게, `[1e-5, 5e-4]` 구간에서 안정 학습이 가능한 최고값. LoRA 는 학습률 민감도가 full-FT 보다 높습니다.
- **체제 선택** — LoRA 는 IFT 에 쓰고 CPT(대량 토큰 연속 사전학습)에는 쓰지 마십시오. 본 스택에서 D22 의 multi-embodiment co-pretrain(Stage 0½)을 LoRA 로 하려는 시도는 이 권고에 정면으로 어긋납니다 — co-pretrain 은 full-FT 영역.
- **평가 축 추가** — VLM 보존을 단일 지표가 아니라 "학습량(target 성공률) × 망각량(OOD/일반화 지표)"의 Pareto 로 보고, 랭크를 그 곡선 위에서 위치를 정하는 제어 변수로 다룹니다(D26 일반화 메트릭과 연결).

---

## ⚠️ 먼저 검증할 실패 모드

- **도메인 전이 불확실성** — 본 논문은 영어 텍스트 LLM(다음 토큰 예측)입니다. PROBE 의 backbone 적응은 새로운 modality(촉각 토큰, multi-cam 융합, flow-matching 액션 head)를 더하는 문제로, 텍스트 IFT 보다 어려운 **CPT 형 난도**에 가깝습니다. 그렇다면 LoRA 저랭크는 학습이 안 된다는 본 논문의 CPT 결론이 적용되어, D19(d) LoRA 경로 자체가 신규 modality 학습에는 부적합할 수 있습니다.
- **가장 싼 sanity check** — D19(a) full freeze + late-fusion(D19 v1 의 rationale: backbone 은 π-학습 modality 만 보고 적응 압력이 없음)이 유지되는 한 forgetting 경로는 수학적으로 차단되므로, 그 가정이 성립하는지(즉 신규 modality 가 backbone 입력에 직접 들어가지 않는지)부터 확인합니다. 이것이 성립하면 본 논문의 LoRA-vs-full 비교는 PROBE v1 에 비적용(freeze 가 두 극보다 우월)입니다.
- **랭크-규모 상호작용** — 본 논문 결론은 Llama-2-7B(텍스트) 기준입니다. PaliGemma-2B(π0 lineage)는 더 작고 modality 가 다르므로, "r=256·MLP 중심" 권고가 그대로 옮겨갈지는 소규모 ablation 으로 먼저 확인해야 합니다.

---

## 💡 컨텍스트 제안

- **P4 methodology base 추가 후보** — 본 논문(arXiv:2405.09673)을 P4 의 "methodology base"(continual learning / PEFT) 항목으로 추가 검토를 제안합니다. 현재 §8.4 핀은 모두 VLA/VLM 적용 논문이고, LoRA 의 학습-망각 trade-off 를 정량화한 *기반* PEFT 연구는 부재합니다. 다만 핀 8개 cap 을 넘기지 않도록 핀이 아닌 methodology base 라인(§8.1 의 FiLM/PCGrad 형식)으로 다는 것이 적절해 보입니다.
- **D19/D21 deferred trigger 보강 후보** — D19 (d) LoRA 와 D21 Stage 3 의 deferred 설명에, LoRA 채택 시 "r=256· $`\alpha=2r`$ ·all-linear·IFT 한정" 기본값을 본 논문 근거로 부기하는 것을 제안합니다(트리거 자체는 변경 없음).
- **Cross-pollination 기록** — §12 Month A(continual learning / forgetting / PEFT) 슬롯에 부합하는 크로스폴리네이션 후보입니다.

> 💡 base 매핑은 `/implement-design analysis/2405.09673/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
