# Paper Analysis — Drop-Then-Recovery: How Redundant Are Vision-Language-Action Models?

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Drop-Then-Recovery: How Redundant Are Vision-Language-Action Models? |
| 저자 | Guoheng Sun, Kaixi Feng, Shwai He, Xiaochuan Gong, Yexiao He, Ziyao Wang, Zheyu Shen, Wanghao Ye, Ramana Rao Kompella, Gaowen Liu, Ang Li (University of Maryland · Cisco Research) |
| 링크 | [arXiv:2606.27755](https://arxiv.org/abs/2606.27755) · [GitHub](https://github.com/s1ghhh/VLADrop) |
| 발행일 / 버전 | 2026-06-26 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-07-01 |
| 관련 Pillar | P4, P1, P2 |
| 태그 | vla-arch, peft |

---

## 🧭 한 줄 요약 (TL;DR)

사전학습된 VLM 에서 물려받은 VLA 의 **언어 백본은 표준 조작 벤치마크에 대해 극도로 과잉(redundant)** 이며, transformer block 을 물리적으로 제거한 뒤 recovery fine-tuning 하면(Drop-Then-Recovery) 언어 블록의 절반을 지워도 성능이 유지·향상되지만, **비전·액션 경로는 제거 내성이 훨씬 낮다** — 즉 현재 VLA 는 언어에 용량을 과배분하고 있고 벤치마크도 깊은 언어 grounding 을 요구하지 않는다는 진단입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — VLA 는 웹 스케일 VLM 백본(수 GB 파라미터)을 그대로 상속하지만, 조작 지시문은 "pick up the red cup" 처럼 짧고 정형적입니다. "닫힌 루프 제어에 VLA 모델이 실제로 얼마나 필요한가?"를 컴포넌트 단위로 측정하려 합니다.
- **기존 접근의 한계** — LLM/VLM 압축 문헌의 layer-dropping 지표(cosine similarity, magnitude, perplexity)는 **제거 직후의 즉각적 열화(importance)** 만 재고, fine-tuning 후 되살아나는 **recoverability** 를 예측하지 못합니다. 또한 대부분 recovery 없이(drop-only) 평가하는데, VLA 는 작은 액션 오차가 long-horizon 에서 누적돼 task 붕괴로 이어지므로 이 방식이 부적합합니다.
- **본 논문의 가설** — 컴포넌트별(비전 / 언어 / 액션) 제거-후-회복 내성에 **강한 비대칭**이 있고, 특히 언어 백본이 과잉이라는 가설. 즉 redundancy 는 파라미터 수가 아니라 **recovery 후 closed-loop task success** 로 측정해야 합니다.
- **왜 지금 중요한가** — VLA 를 Jetson 급 edge 로 배포하려면 latency·메모리 예산이 빡빡한데, 언어 용량이 과잉이라면 커널 특화 없이도(quantization·sparsity 와 달리) dense 모델을 그대로 줄여 hardware-agnostic 가속을 얻을 수 있습니다. 동시에 "벤치마크가 언어 이해를 제대로 시험하는가"라는 평가 설계 질문을 던집니다.

---

## 🧩 핵심 기여

- **VLA 언어 백본이 현행 조작 벤치마크에 대해 극도로 과대(over-sized)** 임을 여러 아키텍처에 걸쳐 실증 — 대부분의 언어 블록을 제거하고 회복해도 task success 손실이 거의 없습니다.
- **Drop-Then-Recovery (DTR)** — transformer block 을 물리적으로 제거(Drop)한 뒤 downstream task 로 fine-tuning(Recovery)하여, 제거된 용량이 닫힌 루프 제어에 실제로 필요했는지 측정하는 분석 프로토콜. 부산물로 회복 가능한 경우 더 작은 dense 모델을 얻습니다.
- **GateProbe** — 각 블록의 residual branch 에 가상 스칼라 게이트 $`\alpha_i`$ 를 걸고 task loss 의 게이트 민감도를 재는 one-shot importance 지표. 정적 지표 대비, 특히 극단적 압축(소수 언어 블록만 유지)에서 회복 가능한 블록 집합을 더 잘 고릅니다.
- **현행 VLA 벤치마크가 언어 grounding 을 과소 시험(under-test)** 한다는 진단 — 대규모 언어 블록 제거로부터 쉽게 회복된다는 사실은 표준 벤치마크가 풍부한 언어 이해를 요구하지 않음을 시사하며, 더 조합적(compositional)·긴 horizon 의 언어 조건 벤치마크가 필요함을 동기화합니다.

---

## 🔑 기술 키워드

- **VLA (Vision-Language-Action) model** — 시각 관측 + 자연어 지시를 받아 로봇 액션을 직접 예측하는 정책. 본 논문의 해부 대상이며, 비전 인코더 $`\mathcal{V}`$ · 언어 백본 $`\mathcal{L}`$ · 액션 헤드 $`\mathcal{A}`$ 세 경로로 분해합니다.
- **Drop-Then-Recovery (DTR)** — "먼저 떼어내고 나서 회복시켜본다" — 블록 제거를 controlled intervention 으로 삼는 2단계 분석 프로토콜(Drop → Recovery fine-tune).
- **GateProbe** — 각 블록에 가상 게이트를 상상으로 걸고 "이 게이트를 끄면 loss 가 얼마나 흔들리나"를 재는 one-shot 민감도 지표. 모델을 수정하지 않고 hook 으로 계산합니다.
- **Recoverability** — 제거된 모델이 recovery fine-tuning 후 도달하는 task 성능. 제거 직후 즉각 열화 정도인 **importance** 와 구분되는 핵심 축(큰 zero-shot 열화가 반드시 낮은 recoverability 를 뜻하진 않음).
- **Transformer block removal** — 개별 weight 를 건드리는 quantization/pruning 과 달리, residual 을 단락(short-circuit)시켜 블록 단위를 통째로 제거하고 남은 망을 dense 로 유지하는 구조적 압축.
- **Virtual gate sensitivity** — 게이트 $`\alpha_i`$ 를 실제로 넣지 않고 chain rule 로, downstream gradient 와 블록 residual contribution 의 내적으로 민감도를 얻는 계산 트릭.
- **Redundancy asymmetry** — 컴포넌트별 제거 내성의 비대칭: 언어는 관대(highly redundant), 비전·액션은 취약(less tolerant).
- **Joint-attention (dual-stream)** — $`\pi_{0.5}`$ 처럼 언어 백본과 액션 expert 가 병렬 스트림으로 각 layer 에서 concat 되어 shared attention 을 계산하는 구조. 언어 블록을 drop 해도 K/V projection 은 cross-attention 을 위해 남습니다.
- **Task Speedup vs Act. Speedup** — 단일 액션 생성 속도(Act.)와, 실패 에피소드의 step 증가까지 반영한 end-to-end 속도(Task = Act. Speedup / Step Ratio)를 구분하는 배포 관점 지표.

---

## 🔬 방법론

### 직관

이 논문의 핵심 질문은 단순합니다 — "VLA 가 물려받은 거대한 언어 두뇌가 정말 로봇 제어에 다 필요한가?" 파라미터 수만 보면 답할 수 없습니다. 웹 규모 언어 모델링에 유용한 블록이 로봇 제어에는 무의미할 수 있고, 반대로 아주 작은 액션 모듈이 long-horizon 오차 누적 때문에 결정적일 수 있기 때문입니다. 그래서 저자들은 "떼어내 본다(ablate)"는 실험 정신을 정밀하게 프로토콜화합니다.

방법은 두 단계입니다. **Drop** — 중요도가 낮은 transformer 블록 $`K`$ 개를 골라 residual 연결을 단락시켜 물리적으로 제거하면, FLOPs·메모리·latency 가 비례해서 줄어든 진짜 작은 dense 모델이 됩니다. **Recovery** — 이 작아진 모델을 downstream task 로 fine-tuning 합니다. 회복 후에도 task success 가 유지되면, 제거된 용량은 그 task 분포에 불필요했다는 결론입니다. 여기서 중요한 통찰은 "제거 직후 얼마나 나빠지나(importance)"와 "회복 후 얼마나 돌아오나(recoverability)"는 다른 축이라는 점 — 크게 무너져도 쉽게 회복되는 블록이 있습니다.

두 번째 조각은 **어떤 블록을 뗄지** 고르는 문제입니다. 기존 정적 지표는 회복 잠재력을 못 봅니다. GateProbe 는 각 블록의 residual 가지에 가상의 손잡이(게이트) $`\alpha_i`$ 를 상상으로 달아, $`\alpha_i=1`$ 이면 원래 모델, $`\alpha_i=0`$ 이면 그 블록을 끈 것과 같게 정의합니다. 그리고 task loss 가 이 손잡이에 얼마나 민감한지를 잽니다. 핵심 트릭은 게이트를 실제로 모델에 넣지 않아도, chain rule 로 "downstream gradient $`\partial\mathcal{L}/\partial h_i`$ 와 블록의 residual 기여 $`F_i(h_{i-1})=h_i-h_{i-1}`$ 의 내적"으로 이 민감도를 단 한 번의 forward-backward 로 얻는다는 것입니다.

실험적으로 이 프로토콜을 4개 VLA(π0.5, OpenVLA-OFT, Lingbot-VLA, GigaBrain-0) × 3개 벤치마크(LIBERO, LIBERO-Plus, RoboTwin 2.0) + 실물 로봇에 적용해, "언어는 관대, 비전·액션은 취약"이라는 일관된 비대칭을 보입니다.

### 아키텍처

VLA 모델을 비전 인코더 $`\mathcal{V}`$, 언어 백본 $`\mathcal{L}`$, 액션 헤드 $`\mathcal{A}`$ 로 보고, 세 컴포넌트에 걸친 droppable 블록 전체 집합을 정의합니다.

> "A VLA model consists of a vision encoder $`\mathcal{V}`$, a language backbone $`\mathcal{L}`$, and an action head $`\mathcal{A}`$, each built from stacked transformer blocks with residual connections." (§3)
(세 경로를 각각 residual 연결의 transformer 블록 스택으로 통일해 보므로, "블록 제거"라는 동일한 개입을 컴포넌트 간에 공정하게 비교할 수 있습니다.)

$$\mathcal{B}=\underbrace{\{B^{\mathcal{V}}_{1},\ldots,B^{\mathcal{V}}_{N_{V}}\}}_{\text{vision}}\;\cup\;\underbrace{\{B^{\mathcal{L}}_{1},\ldots,B^{\mathcal{L}}_{N_{L}}\}}_{\text{language}}\;\cup\;\underbrace{\{B^{\mathcal{A}}_{1},\ldots,B^{\mathcal{A}}_{N_{A}}\}}_{\text{action}}$$

각 블록 $`B_i`$ 는 residual 형태 $`h_{i}=h_{i-1}+F_{i}(h_{i-1};\,\theta_{i})`$ 를 따릅니다. 여기서 $`F_i`$ 가 블록의 변환, $`\theta_i`$ 가 그 파라미터입니다.

![Figure 1 — DTR overview](https://arxiv.org/html/2606.27755/x1.png)

> "Figure 1: Overview of DTR. A pretrained VLA model’s transformer blocks are ranked by importance, the least important are physically removed, and the smaller model is recovery fine-tuned." (§3)
(중요도 랭킹 → 물리적 제거 → 회복 fine-tuning 의 3-스텝 파이프라인을 한눈에 보여줍니다.)

**Dual-stream(joint-attention) 예외** — $`\pi_{0.5}`$ 처럼 언어 백본과 액션 expert 가 병렬 스트림으로 각 layer 에서 sequence 를 concat 해 shared attention 을 계산하는 구조에서는, 언어 블록을 drop 해도 파라미터가 전부 사라지지 않습니다(Appendix B).

> "The language block’s key projection ($`W_{K}`$), value projection ($`W_{V}`$), and input layer normalization must remain active, because the action expert still needs to cross-attend to language representations at this layer." (§Appendix B)
(K/V projection 과 input LN 은 액션 expert 의 cross-attention 을 위해 남기고, Q·O projection 과 MLP 전체만 제거 — 언어 hidden state 는 identity $`h_{i}^{\mathcal{L}}=h_{i-1}^{\mathcal{L}}`$ 로 통과합니다. 결과적으로 블록당 약 75%(Q, O, MLP)만 제거되며, 남은 K/V 는 recovery 중 cross-attention adapter 로 재활용됩니다. OpenVLA-OFT 처럼 액션 헤드가 분리된 MLP 인 구조에서는 언어 블록 제거 시 100% 제거됩니다.)

### 학습 목표 / 손실

**Stage 1 — Drop.** 중요도 지표 $`I`$ 와 목표 제거 수 $`K`$ 가 주어지면, 가장 덜 중요한 $`K`$ 개 블록을 선택·제거합니다.

$$\mathcal{S}=\mathrm{argsort}_{K}\bigl\{I(B_{i})\bigr\}_{B_{i}\in\mathcal{B}},\qquad\mathcal{M}_{\text{drop}}=\mathcal{M}\setminus\mathcal{S}$$

Drop 은 residual 을 단락시켜($`h_{i}=h_{i-1}`$) $`\theta_i`$ 를 버리므로, 어떤 하드웨어에서도 FLOPs·메모리·latency 가 비례 감소한 진짜 작은 dense 모델이 됩니다.

**Stage 2 — Recovery.** 제거된 모델을 downstream task 로 fine-tuning 합니다.

$$\theta^{*}=\arg\min_{\theta}\;\mathcal{L}_{\text{action}}\!\left(\pi_{\theta}(a\mid o,p),\;a^{\text{gt}}\right)$$

여기서 $`o`$ 는 관측, $`p`$ 는 언어 지시, $`a^{\text{gt}}`$ 는 시연 액션, $`\mathcal{L}_{\text{action}}`$ 은 액션 예측 손실(연속 액션의 MSE, diffusion 계열의 flow-matching 등)입니다.

> "Recovery is critical because in closed-loop control, even small degradations in action quality can compound into task failures over long horizons." (§3.1)
(회복 단계가 본 프로토콜의 정당성 근거 — 액션 오차의 long-horizon 누적 때문에 drop-only 평가는 VLA redundancy 를 과소·왜곡 측정합니다.)

**GateProbe — virtual gate sensitivity.** 각 블록의 residual 가지에 가상 스칼라 게이트 $`\alpha_i`$ 를 도입합니다.

$$\tilde{h}_{i}=h_{i-1}+\alpha_{i}\cdot F_{i}(h_{i-1};\,\theta_{i})$$

$`\alpha_i=0`$ 은 블록 $`B_i`$ 를 drop 한 것과 같고, $`\alpha_i=1`$ 은 원 모델을 복원합니다. GateProbe importance 점수는 이 게이트에 대한 task loss 의 기대 절대 민감도입니다.

$$I_{\text{gate}}(B_{i})=\mathbb{E}_{x\sim\mathcal{D}}\left[\left|\frac{\partial\mathcal{L}(x)}{\partial\alpha_{i}}\right|_{\alpha_{i}=1}\right]$$

핵심은 게이트를 모델에 실제로 넣지 않고 chain rule 로 계산할 수 있다는 것입니다.

$$\frac{\partial\mathcal{L}}{\partial\alpha_{i}}\bigg|_{\alpha_{i}=1}=\left\langle\frac{\partial\mathcal{L}}{\partial h_{i}},\;F_{i}(h_{i-1})\right\rangle$$

> "The score is thus the inner product of the downstream gradient and the block’s residual contribution, capturing both how much the block changes the representation and how much the downstream computation relies on that change." (§3.2)
($`\partial\mathcal{L}/\partial h_{i}`$ 는 이후 모든 layer 를 거쳐 역전파된 downstream gradient(backprop 에서 그대로 확보), $`F_{i}(h_{i-1})=h_{i}-h_{i-1}`$ 는 forward 에서 캐시한 residual 기여입니다. 두 항의 내적이라 "블록이 표현을 얼마나 바꾸는가"와 "downstream 이 그 변화에 얼마나 의존하는가"를 동시에 포착합니다.)

**Taylor 해석** — $`I_{\text{gate}}(B_i)`$ 는 블록 기여를 0으로 스케일할 때의 loss 변화의 1차 Taylor 근사입니다(Appendix D).

$$\mathcal{L}|_{\alpha_{i}=0}\approx\mathcal{L}|_{\alpha_{i}=1}-1\cdot\frac{\partial\mathcal{L}}{\partial\alpha_{i}}\bigg|_{\alpha_{i}=1}$$

$`|I_{\text{gate}}(B_i)|`$ 이 클수록 제거 시 즉각 loss 증가가 커서 더 중요하고 유지해야 함을 뜻합니다.

### 학습 셋업

- **구현(GateProbe)** — 게이트는 가상(virtual): 아키텍처를 바꾸거나 학습 파라미터를 넣지 않습니다. 각 블록 input norm 에 forward pre-hook 을 걸어 $`h_{i-1}, h_i`$ 를 캡처하고 `retain_grad()` 호출 후 표준 forward-backward 1회를 돌립니다. 작은 calibration set 1회 통과면 충분합니다(π0.5 · 18 블록 · calibration batch 64 × size 8, 단일 H200 에서 24.9 s).
- **모델 4종** — π0.5(dual-stream flow-matching, PaliGemma 언어 18층 + 별도 Gemma 액션 expert 18층, SigLIP 비전), OpenVLA-OFT(Llama-2-7B 32층 + SigLIP + MLP 액션 헤드, LoRA), Lingbot-VLA(Qwen2.5-VL-3B 36층 + Qwen2 액션 expert, flow-matching, 약 4B), GigaBrain-0(PaliGemma2-3B + Gemma2 26층, diffusion 액션 헤드, 약 3.5B).
- **벤치마크** — LIBERO(Spatial/Object/Goal/Long 4-suite, suite 당 10 task, task 당 20 trial; 메인 연구), LIBERO-Plus(배경·텍스처·시점·로봇 pose·언어·조명·noise·layout 섭동 확장), RoboTwin 2.0(양팔 조작, 강한 domain randomization).
- **회복 학습(LIBERO)** — π0.5: full fine-tuning, AdamW, global bsz 32, 30K steps, lr `5×10⁻⁵`(10K warmup 후 constant), bf16. OpenVLA-OFT: LoRA rank 32, L1 action regression, AdamW, bsz 16, 50K steps, lr `5×10⁻⁴`. Compute-matched 비교 시엔 dropped 모델의 compute 감소만큼 bsz·step 을 스케일하고 데이터·최적화 프로토콜은 고정합니다.

---

## 📊 실험 설정과 결과

### 컴포넌트 redundancy 비대칭 (Table 1)

importance 지표 편향을 배제하려 각 컴포넌트에 두 단순 전략을 독립 적용: **Drop Half**(홀수 인덱스 블록 전부 제거)와 **Keep 2**(첫·마지막 블록만 유지).

| Model | Setting | Component | Size | FLOPs | Avg. SR |
|---|---|---|---|---|---|
| OpenVLA-OFT | Baseline | — | 100% | 100% | 95.0 |
| OpenVLA-OFT | Drop Half | Vision | 96.4% | 95.6% | 83.9 |
| OpenVLA-OFT | Drop Half | **Language** | 55.5% | 55.0% | **98.3** |
| OpenVLA-OFT | Drop Half | Action* | 99.5% | 100.0% | 94.5 |
| OpenVLA-OFT | Keep 2 | Vision | 92.2% | 91.6% | 80.2 |
| OpenVLA-OFT | Keep 2 | **Language** | 16.6% | 15.6% | **95.1** |
| OpenVLA-OFT | Keep 2 | Action* | 99.3% | 99.9% | 89.0 |
| π0.5 | Baseline | — | 100% | 100% | 91.7 |
| π0.5 | Drop Half | Vision | 89.5% | 93.3% | 80.8 |
| π0.5 | Drop Half | **Language** | 60.6% | 57.9% | **93.3** |
| π0.5 | Drop Half | Action | 93.8% | 99.5% | 93.2 |
| π0.5 | Keep 2 | Vision | 79.8% | 87.0% | 62.4 |
| π0.5 | Keep 2 | **Language** | 30.0% | 25.1% | **91.0** |
| π0.5 | Keep 2 | Action | 88.9% | 99.1% | **26.2** |

> "On OpenVLA-OFT, Language Drop Half removes 44.5% of parameters while matching or exceeding the baseline SR (98.3% vs. 95.0%), whereas Vision removes only 3.6% but drops to 83.9%." (§4.2, Table 1)
(언어는 파라미터의 44.5% 를 지워도 baseline 을 넘고, 비전은 3.6% 만 지워도 83.9% 로 무너집니다 — 컴포넌트별 내성의 극명한 비대칭.)

> "Under extreme compression (Keep 2), Language remains close to baseline, while Vision and Action collapse to 62.4% and 26.2% respectively on $`\pi_{0.5}`$." (§4.2, Table 1)
(Keep 2 극단에서 π0.5 액션은 26.2% 로 붕괴 — 액션 경로가 가장 취약함을 보여, 이후 모든 실험은 언어 블록 제거에 집중합니다. 각 셀은 Spatial/Object/Goal/Long 4-suite 평균.)

### 제거 입도 (Table 2)

언어 백본 내에서 whole block vs MHA sublayer only vs MLP sublayer only 비교(Drop Half, LIBERO). OpenVLA-OFT 에서 block(98.3%) 이 MHA(91.9%)·MLP(65.6%) 를 크게 상회하고, π0.5 에서는 셋 다 93.3–94.1% 로 비슷하지만 block 이 가장 많이 압축합니다. 결론적으로 whole-block dropping 을 기본으로 채택합니다.

### 중요도 지표 비교 — GateProbe (Table 3, π0.5 / LIBERO)

| Setting | Metric | Avg. SR |
|---|---|---|
| Baseline | — | 91.7 |
| Drop-9 (9/18) | Taylor / IGIA† | 94.2 |
| Drop-9 | **GateProbe** | 94.0 |
| Drop-9 | Fisher | 91.8 |
| Drop-9 | CosSim | 90.2 |
| Drop-9 | PPL | 89.6 |
| Drop-9 | Magnitude | 88.0 |
| Drop-16 (16/18) | **GateProbe / Fisher†** | 92.2 |
| Drop-16 | Hessian | 88.3 |
| Drop-16 | Taylor | 85.2 |
| Drop-16 | Mag./CosSim/CosSim(c.)† | 81.9 |
| Drop-17 (17/18) | **GateProbe / Fisher / Hessian / IGIA / PPL†** | 88.7 |
| Drop-17 | Taylor | 84.4 |
| Drop-17 | Mag./CosSim/CosSim(c.)† | 83.8 |

> "GateProbe achieves the best or second-best at all four levels, with a growing advantage under aggressive compression ($`+`$3.9 at Drop-16, $`+`$4.3 at Drop-17)." (§4.4, Table 3)
(정적 지표(CosSim/Magnitude/PPL)는 싸지만 일관되게 열위, gradient 계열(Taylor/IGIA)은 중간 압축엔 좋지만 극단에서 무너집니다. GateProbe 는 4개 drop 레벨 모두 1–2위이며 공격적 압축일수록 이득이 커지는 게 핵심 셀링 포인트입니다. †는 그 레벨에서 동일 블록을 선택한 지표 묶음.)

### FLOPs-matched 처리량 (Table 4, π0.5 / LIBERO)

Drop 이 fine-tuning 앞에 오므로 dropped 모델은 step 당 더 싸고, 같은 compute 예산에 더 많은 iteration 을 돌릴 수 있습니다(bsz·step 스케일로 baseline 과 총 FLOPs 매칭).

| Setting | Size | FLOPs | Bsz | Steps | Avg. SR |
|---|---|---|---|---|---|
| Baseline | 100% | 100% | 32 | 30K | 91.7 |
| Drop-9 | 60.6% | 57.9% | 64 | 25.9K | 92.3 |
| Drop-12 | 47.5% | 43.8% | 64 | 34.2K | **93.7** |
| Drop-16 | 30.0% | 25.1% | 64 | 59.8K | 92.6 |
| Drop-17 | 25.6% | 20.4% | 64 | 73.5K | 91.0 |

Drop-9~16 모두 baseline 매칭·상회, Drop-12 가 최고(93.7%, `+2.0`). 언어 블록 1개만 남긴 Drop-17 도 91.0% 회복.

### Hardware-agnostic 가속 (Table 5, OpenVLA-OFT / LIBERO-Goal)

> "DTR-16 achieves 1.64$`\times`$ task speedup and also reduces memory by 42%." (§6.1, Table 5)
(DTR-16 은 100.0% SR(`+2.0`)·1.56× per-action·1.64× task speedup·42% 메모리 절감으로 세 축을 동시에 개선한 유일 방법. 대조적으로 zero-shot Block Drop 4 는 per-action 1.05× 로 빨라도 SR 78% 열화가 실패 step 을 부풀려 task speedup 0.72× — 오히려 느려집니다. 즉 recovery 학습은 유익할 뿐 아니라 필수.)

### Cross-benchmark robustness (Table 6, π0.5 / LIBERO-Plus)

compute-matched 설정으로 섭동 카테고리별 평가. 언어 redundancy 는 벤치마크를 가로질러 일관되나, 제거된 블록이 **물리적 일반화**에도 기여함이 드러납니다.

| Setting | Size | Camera | Robot | Language | Light | Avg. |
|---|---|---|---|---|---|---|
| Baseline | 100% | 85.4 | 60.3 | 70.9 | 91.5 | 81.4 |
| Drop-9 | 60.6% | 85.4 (-0.0) | 49.7 (-10.6) | 65.8 (-5.1) | 89.7 (-1.8) | 77.6 (-3.8) |
| Drop-12 | 47.5% | 81.8 (-3.6) | 43.0 (-17.3) | 59.7 (-11.2) | 86.9 (-4.6) | 73.0 (-8.4) |
| Drop-16 | 30.0% | 72.7 (-12.7) | 36.1 (-24.2) | 61.0 (-9.9) | 86.8 (-4.7) | 68.8 (-12.6) |
| Drop-17 | 25.6% | 73.7 (-11.7) | 32.1 (-28.2) | 62.3 (-8.6) | 83.3 (-8.2) | 68.0 (-13.4) |

> "on LIBERO-Plus, the largest degradation after dropping is not in the Language category ($`-`$5.1 at Drop-9) but in Robot ($`-`$10.6), which perturbs the arm’s initial pose." (§6.2, Table 6)
(Drop-9 에서 가장 큰 열화가 언어(-5.1)가 아니라 로봇 초기 pose 섭동(-10.6)이라는 점 — 언어 백본이 단순 지시엔 과잉이어도 물리적 섭동 일반화엔 기여함을 시사합니다. RoboTwin 2.0 에서도 Easy 변형은 -0.6% 인데 Hard 변형은 -6.6% 로 급락(Figure 4).)

### Cross-model 일관성 (Table 7)

| Model | Drop | Avg. SR |
|---|---|---|
| OpenVLA-OFT | 0/32 → 16/32 | 95.0 → **98.3** (+3.3) |
| π0.5 | 0/18 → 9/18 | 91.7 → 93.3 |
| GigaBrain-0 | 0/26 → 13/26 | 88.0 → 88.0 |
| Lingbot-VLA | 0/36 → 18/36 | 82.8 → 83.7 |

> "language redundancy is not scale-dependent but instead stems from a structural mismatch: VLA models inherit language capacity far beyond what short robotic instructions require." (§6.3, Table 7)
(4개 아키텍처 모두 언어 블록 절반 제거 후 baseline 매칭·상회. redundancy 가 규모 의존이 아니라 VLM→VLA 용량 불일치라는 구조적 원인에서 온다는 논지 — 다만 저자도 이는 LIBERO 포화(saturation) 탓도 일부 있다고 인정.)

### 실물 로봇 (Figure 2, 3)

![Figure 2 — Real-world setup and results](https://arxiv.org/html/2606.27755/x2.png)

> "Figure 2: Real-world experimental setup and main results." (§5)
(UFACTORY xArm 850 + G2 gripper, wrist RealSense D435 + 3인칭 카메라, Jetson Thor 구동. Meta Quest 3 teleop 10 Hz, 약 110K frame(약 600 grasp). warehouse parcel sorting: 변형 가능한 soft-body 패키지를 컨테이너에서 컨베이어/슬롯으로 이송.)

Env 1 에서 Drop-9(65.0%)가 full model(63.3%)을 근소 상회, Drop-16 은 55.0% 로 열화. Env 2 는 full 75.0% / Drop-9 71.7% / Drop-16 66.7% — 시뮬레이션 패턴(절반 제거는 유지, 2/18 유지는 중간 열화)을 재현.

![Figure 3 — Robustness under distribution shift](https://arxiv.org/html/2606.27755/x3.png)

> "Figure 3: Robustness under distribution shift. (a) Lighting perturbations. (b) Physical perturbations." (§5)
(6개 OOD(조명 pink/green/flashing, novel object, container 방향 변경, container 제거) 평가. mild 섭동(container 방향)엔 Drop-0/9/16 이 75%/70%/70% 로 근접하나, green light 에서 Drop-16 은 35%(vs full 50%), container 제거에서 40%(vs 60%)로 강섭동일수록 격차 벌어짐 — 제거된 언어 용량이 robustness 완충 역할.)

---

## ⚖️ 한계

- **벤치마크 포화(saturation)와 원인 혼입** — 저자 스스로 OpenVLA-OFT 의 `+3.3` 반등이 "부분적으로 LIBERO 포화 탓"이라 인정합니다. LIBERO 가 이미 95% 대 상단에 있으면 언어 제거의 "향상"은 redundancy 증명이라기보다 회복 학습 예산 재배분(같은 compute 로 더 많은 step)의 부산물일 수 있어, redundancy 주장과 벤치마크-용이성 주장이 분리되지 않습니다.
- **"redundancy" 정의가 task 분포에 종속** — recoverability 는 평가한 task 분포에 대해서만 성립합니다. LIBERO-Plus 의 Robot pose 섭동(-10.6)·RoboTwin Hard(-6.6%) 결과가 보여주듯, 같은 블록이 단순 지시엔 잉여지만 물리적 OOD 일반화엔 기여합니다. 따라서 "언어 백본이 redundant" 는 무조건적 명제가 아니라 "현행 벤치마크가 그것을 시험하지 않는다" 의 재진술에 가깝습니다.
- **언어 grounding 을 직접 측정하지 않음** — 논문은 "벤치마크가 언어 이해를 과소 시험한다"고 결론짓지만, 정작 조합적 지시·referring expression·long-horizon 언어 조건에서 dropped 모델이 무너지는지는 (LIBERO-Plus 의 Language 카테고리 외엔) 직접 실험하지 않습니다. 반례 벤치마크의 부재가 곧 언어 무용의 증거는 아닙니다.
- **Recovery 예산과 데이터가 회복량을 좌우** — DTR 은 downstream 시연으로 fine-tuning 하는데, 회복에 필요한 데이터·step 량이 drop 규모에 따라 급증합니다(Table 4: Drop-17 은 73.5K step). 배포 데이터가 "분 단위"로 희소한 환경(=본 프로젝트의 P4 전제)에서는 이 회복 비용이 병목이 될 수 있습니다.
- **GateProbe 의 calibration 의존성** — GateProbe 점수는 calibration set 분포에 종속(LIBERO-Plus·RoboTwin 은 dataset-specific profiling 으로 다른 블록을 선택, Table 10/11). 배포 분포가 calibration 과 어긋나면 잘못된 블록을 제거할 위험이 있고, 이 민감도는 정량화되지 않았습니다.

---

## ♻️ 재현성

- **코드** — 공개: [github.com/s1ghhh/VLADrop](https://github.com/s1ghhh/VLADrop) (초록·본문 명시).
- **모델·벤치마크** — 4개 VLA 모두 공개 체크포인트/구현 기반(π0.5·OpenVLA-OFT·Lingbot-VLA·GigaBrain-0), 벤치마크는 공개(LIBERO / LIBERO-Plus / RoboTwin 2.0). 학습 하이퍼파라미터는 Appendix H 에 표(Table 14/15)로 명시.
- **하드웨어** — profiling·latency 측정은 단일 H200 GPU 명시. 실물 로봇은 UFACTORY xArm 850 + G2 gripper + Jetson Thor + RealSense D435 로 구체적. teleop 데이터 규모(약 110K frame, 약 600 grasp) 명시.
- **미공개/모호** — GateProbe 의 kept-block lookup 은 LIBERO 는 표(Table 9)로 제공되나, 실물 로봇 데이터셋 자체는 산업 시나리오라 공개 여부 불명. drop index 는 dataset-specific 이라 신규 task 재현 시 재-profiling 필요.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P4(pretraining for data-efficient adaptation) — 1차.** 본 논문은 "사전학습 VLM 백본에서 물려받은 언어 용량이 과잉"이라는, P4 의 핵심 변수인 lineage·adaptation range 를 정면으로 건드립니다. D19(VLM backbone lineage + post-pretraining adaptation range)의 v1 선택이 "(a) 전체 VLM freeze + action expert 만 학습(prior 보존)"인데, 이 논문은 그 frozen VLM 의 언어 절반이 표준 task 엔 불필요할 수 있음을 시사 — freeze 대상 자체를 축소(언어 블록 pruning)하는 대안 축을 엽니다. D20(prior-preservation strategy)·D23(action representation × pretraining/preservation)과도 연결(GateProbe 로 어떤 블록을 보존/제거할지 결정).
- **P1(heterogeneous Body/Hand action expert) — 2차.** "future VLA architectures should allocate capacity more deliberately across language, vision, and action components" 는 P1 의 용량 배분 논지와 직결됩니다. 특히 **액션 경로가 제거에 가장 취약**(π0.5 Keep 2 Action 26.2%)하다는 결과는, 액션 expert 에 용량을 축소하지 말고 오히려 배분해야 한다는 D1(split form)·D7(π backbone integration/partition) 설계 직관을 데이터로 뒷받침합니다.
- **P2(structured multimodal observation fusion) — 3차.** **비전 경로가 언어보다 훨씬 제거에 취약**(비전 3.6% 제거로 83.9% 붕괴)하다는 결과는 "비전은 critical, 관측 elevation 은 낭비가 아니다"라는 P2 논지를 지지합니다.
- **Identity 긴장/지지** — Identity 는 "dexterity 를 VLA level 에서 직접 tackle" 하되 pretrained VLM/π weight 를 "deliberately composed pretraining recipe" 로 leverage 한다고 봅니다. 본 논문은 그 VLM 상속 용량의 상당 부분이 조작 task 엔 잉여일 수 있음을 실증해, "무엇을 상속하고 무엇을 버릴지"를 정밀하게 만드는 지지 근거입니다(단, 물리적 일반화 기여라는 반작용도 함께).
- **경쟁자 함의** — P4 §5 Tracked Literature 의 ConSFT(conservative adaptation)·π0.5 계열과 같은 lineage 위에서 작동하며, VLA 압축 계열(BitVLA, EfficientVLA, MoLe-VLA, SpecPrune-VLA, "Don't run with scissors")과 직접 경쟁·보완 관계입니다.

---

## ✨ 핀 논문 대비 델타

- **vs. π0.5 (P4 §5 methodology base / P1 §5)** — π0.5 는 dual-stream flow-matching VLA 를 *제안*하지만, 본 논문은 그 π0.5 를 *해부 대상*으로 삼아 언어 백본 18층 중 절반(Drop-9)을 지워도 성능이 유지됨을 보입니다. π0.5 가 "어떻게 만드나"라면, DTR 은 "그중 무엇이 실제로 필요한가"를 측정하는 직교적 기여.
- **vs. ConSFT (P4 §5 pinned)** — ConSFT 는 배포 SFT 단계에서 prior 를 *보존*(conservative importance weighting, ~20%p forgetting 감소)합니다. DTR 은 반대 방향 — 보존이 아니라 **제거**를 통해 무엇이 잉여인지 판별하고, 회복 fine-tuning 으로 되살립니다. 둘은 "adaptation 단계에서 무엇을 붙잡고 무엇을 놓을지"의 상보적 두 축.
- **진정으로 새로운 점** — (1) redundancy 를 파라미터 수가 아닌 **recovery 후 closed-loop task success** 로 재정의, (2) recoverability 를 예측하는 one-shot 지표 GateProbe(기존 정적/gradient 지표가 극단 압축에서 실패하는 지점을 메움), (3) 컴포넌트별 제거 내성의 **비대칭**(언어 관대 / 비전·액션 취약)을 4모델 × 3벤치마크 + 실물로 교차 검증. 기존 VLA 압축 논문(Jabbour et al. "pruning breaks VLA"; Grant et al. mechanistic study)이 redundancy 존재는 확인했으나 "각 컴포넌트가 얼마나, 어디까지 회복 가능한가"는 미해결로 남긴 부분을 정면으로 다룹니다.

---

## ⚙️ 의사결정 함의

- **D19(adaptation range) 대안 축 신설** — 현행 v1 "(a) 전체 VLM freeze". 본 논문이 맞다면, freeze 대상 언어 백본을 GateProbe 로 랭킹해 하위 절반을 제거한 **축소 VLM + action expert** 를 후보로 벤치마킹할 값어치가 있습니다. 구체 config: 언어 백본 layer 수(`num_hidden_layers`) 절반(π0-family PaliGemma 기준 18→9), recovery 시 compute-matched step 스케일.
- **액션 expert 용량은 보수적으로 유지·확대(P1 D7)** — 액션 경로가 가장 취약하므로, action expert 의 layer 수·hidden dim 을 압축 후보에서 제외하고 오히려 우선 배분. OpenVLA-OFT 액션 헤드 `d_h` 축소(4096→256)가 파라미터엔 0.7% 영향이나 성능은 크게 흔든다는 Appendix C 결과가 근거.
- **비전 인코더는 압축 대상 아님(P2)** — 비전 layer 제거는 비용 대비 성능 손실이 커(3.6% 절감 vs 11%p 하락) 압축 우선순위에서 제외. 관측 elevation 투자(multi-cam·tactile 토큰)를 정당화.
- **GateProbe 를 importance 지표로 채택 검토** — layer-dropping/skip 을 도입한다면 CosSim·Magnitude 대신 GateProbe(1 forward+backward, ~25s/H200)를 기본 지표로. loss term 은 우리 flow-matching action loss 로 그대로 대체 가능(`L_action`).
- **평가 프로토콜 보강** — LIBERO 류 포화 벤치마크만으로는 언어 용량 축소의 위험을 못 잡으므로, **Robot pose 섭동·Hard domain randomization·조합적 언어 지시**를 회귀 평가에 포함(LIBERO-Plus Robot 카테고리·RoboTwin Hard 를 gating 지표로).

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 체크) LIBERO 포화 vs 진짜 redundancy 분리** — 우리 데이터/task 는 in-hand reorientation·tool articulation 으로 LIBERO 보다 훨씬 dexterity-heavy 입니다. 먼저 baseline VLA 가 우리 task 에서 포화(>95%)인지 확인 — 포화가 아니라면 "언어 제거로 향상"이 재현될 이유가 약하고, redundancy 이득은 compute 재배분 효과로 축소될 수 있습니다.
- **dexterous·contact-rich task 로의 전이 미검증** — 본 논문 벤치마크는 pick-and-place·양팔 조작 중심이고, 언어는 짧고 정형적입니다. 손가락 단위 contact·in-hand 조작에서 언어 백본이 여전히 잉여인지는 별개 문제 — 특히 우리 Identity 의 tool articulation(trigger/tagging)은 지시 조합성이 더 높을 수 있어 언어 용량이 실제로 쓰일 가능성.
- **물리적 일반화 손실이 우리에게 치명적** — Table 6/Figure 3 은 제거된 언어 블록이 로봇 pose·조명·object OOD robustness 에 기여함을 보입니다. sim2real·System0 stabilization 을 노리는 우리 스택에선 이 robustness 완충 손실이 곧 grasp 실패로 이어질 수 있어, 언어 압축의 순이득이 음(-)일 수 있습니다.
- **π0/π0.5 dual-stream 특수성** — π0.5 는 언어 블록 drop 시 K/V projection 이 남아 실제 제거율이 ~75% 에 그칩니다(Appendix B). 우리가 π backbone 을 쓸 때 압축률·속도 이득이 논문의 dense-model 수치(OpenVLA-OFT 기준)보다 작을 수 있으므로, π-family 에서의 실측 FLOPs·latency 를 먼저 확인.
- **회복 데이터 예산 충돌** — Drop 규모가 커질수록 recovery step 이 급증(Drop-17: 73.5K)합니다. P4 의 "분 단위 배포 데이터로 adaptation" 전제와 상충 — 우리 배포 데이터 규모로 회복이 수렴하는지, drop 규모별 회복 곡선을 소규모로 먼저 측정.
- **GateProbe calibration 분포 어긋남** — dataset-specific profiling 이라(Table 10/11), calibration 을 우리 in-hand task 로 다시 뽑지 않으면 잘못된 블록을 제거할 위험. 재-profiling 비용(1 forward+backward)은 싸므로 반드시 우리 분포로 재계산.

---

## 💡 컨텍스트 제안

- **P4 §5 methodology base 후보** — 본 논문은 lineage/adaptation-range(D19)와 compression 을 잇는 드문 실증이라, P4 §5 "Methodology base (non-pinned)" 에 추가를 제안합니다(VLA 압축·용량 배분 map). pinned 교체까지는 근거 부족 — Jabbour et al.("Don't run with scissors")·Grant et al.(mechanistic study) 등 동류 압축 논문과 함께 tracked 후보군으로 관리 권장.
- **P1 D2/D7 evidence 로 인용 가치** — "action pathway 가 가장 취약" 결과는 액션 expert 용량 배분 결정(D1/D7)의 정량 근거로 유용하나, 이는 데이터포인트 추가일 뿐 Decision 이동을 요구하지는 않습니다.
- Decision/deferred trigger 이동 제안: 없음(현 v1 선택을 뒤집을 만큼의 dexterity-domain 증거는 아직 부족).

---

> 💡 base 매핑은 `/implement-design analysis/2606.27755/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
