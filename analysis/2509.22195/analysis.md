# Paper Analysis — Actions as Language: Fine-Tuning VLMs into VLAs Without Catastrophic Forgetting

> PROBE analysis 모드 산출물. 단일 한글 문서이며, 영문 1차 파일은
> 없습니다. 형식·이모지·용어 규칙은 `docs/STYLE.md` §5 / §4 를
> 정확히 따릅니다. 재실행 시 이 파일을 덮어씁니다.

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Actions as Language: Fine-Tuning VLMs into VLAs Without Catastrophic Forgetting |
| 저자 | Asher J. Hancock, Xindi Wu, Lihan Zha, Olga Russakovsky, Anirudha Majumdar (Princeton University) |
| 링크 | [arXiv:2509.22195](https://arxiv.org/abs/2509.22195) |
| 발행일 / 버전 | 2025-09-26 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-05-28 |

---

## 🧭 한 줄 요약 (TL;DR)

저수준 로봇 액션을 자연어 문자열로 다시 표현해 fine-tuning 데이터를 VLM의 사전학습 분포에 정렬시키면, 별도 액션 디코더나 토큰 사전 개조 없이 **LoRA만으로** VLM을 VLA로 바꿔도 catastrophic forgetting을 피할 수 있다는 것이 핵심 주장입니다. 그 결과 co-training 없이도 VQA 능력의 85% 이상을 유지하면서 다국어·오픈월드 추론이 필요한 OOD 조작 과제로 zero-shot 일반화가 가능합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — VLM을 로봇 teleoperation 데이터로 fine-tuning해 VLA를 만들 때, 액션 예측 능력을 얻는 대가로 VLM의 기반 추론·멀티모달 이해가 손상되는 catastrophic forgetting을 막는 것입니다.
- **기존 접근의 한계** — 가장 흔한 해법인 web 데이터 co-training은 분포 불일치를 근본적으로 해소하지 못하고, robot/web 혼합 비율이라는 튜닝 까다로운 하이퍼파라미터와 막대한 연산 비용을 추가로 떠안깁니다.
- **본 논문의 가설** — forgetting의 근본 원인은 VLM의 인터넷 규모 사전학습 코퍼스와 로봇 fine-tuning 데이터 사이의 **분포 불일치**이며, 이를 *데이터 레벨*에서 먼저 해소하면 LoRA만으로 backbone을 거의 건드리지 않고 적응할 수 있다는 것입니다.
- **왜 지금 중요한가** — VLA가 생성주의 정책의 지배적 패러다임이 되면서, 좁은 로봇 데이터에 과적합돼 새 물체·언어 변형·분산물에 일반화하지 못하는 사례가 반복적으로 보고되고 있어, "행동을 배우되 세계 지식을 잃지 않는" 방법이 generalist policy의 전제 조건으로 부상했습니다.

---

## 🧩 핵심 기여

- **행동의 언어 표현(actions as language)** — 저수준 로봇 모방 데이터를 텍스트로 번역해 VLA fine-tuning 데이터를 VLM의 사전학습 분포에 정렬시킴으로써 forgetting을 완화합니다. 고수준 추론뿐 아니라 end-effector 이동 같은 **저수준 액션까지** 언어로 표현하고, 별도 액션 디코더를 전혀 쓰지 않는 점이 선행 연구와의 차별점입니다.
- **지식 보존형 재라벨링·학습 파이프라인** — Gemini 2.5로 기존 로봇 데이터셋을 subtask / motion plan / action chunk의 3계층 자연어로 자동 재라벨링하고, 이를 표준 supervised fine-tuning(cross-entropy) 과제로 캐스팅해 LoRA로만 학습하는 확장 가능한 방법론을 제시합니다.
- **행동·추론 능력의 실증 검증** — 800회 이상의 실제 로봇 실험과 다수 VQA 벤치마크로, VLM2VLA가 base 모델 성능의 85% 이상을 유지하면서 학습 시 보지 못한 물체·언어 지시로의 일반화를 달성함을 보입니다.
- **action 표현 ablation** — 동일 데이터·동일 학습에서 액션을 "least likely token"으로 표현한 변형(VLM2VLA-AT)과 비교해, 언어 표현이 정책 학습에 더 효과적임을 분리 검증합니다.

---

## 🔑 기술 키워드

- **VLA (Vision-Language-Action model)** — VLM backbone을 로봇 제어용으로 fine-tuning한 정책. 본 논문의 출발점이자 catastrophic forgetting이 발생하는 무대입니다.
- **Catastrophic forgetting** — 좁은 새 과제(로봇 데이터)에 적응하는 동안 사전학습으로 얻은 범용 지식이 덮어쓰여 사라지는 현상. 본 논문이 막으려는 핵심 표적입니다.
- **LoRA (Low-Rank Adaptation)** — 원 가중치를 동결한 채 저차원 행렬만 학습하는 PEFT 기법. backbone을 최소 교란하므로 forgetting 방지의 도구가 되지만, fine-tuning 데이터가 사전학습 표현에 가까워야 효과를 냅니다.
- **Distribution mismatch (분포 불일치)** — VLM 사전학습 코퍼스(이미지-텍스트)와 로봇 데이터(연속 액션 벡터) 사이의 표현 공간 간극. 본 논문은 이 간극을 forgetting의 근본 원인으로 지목합니다.
- **Actions as language** — 연속 액션을 VLM의 기존 어휘 안의 자연어 문자열("move forward by 4.2 centimeters")로 표현하는 방식. 분포 불일치를 데이터 레벨에서 해소하는 핵심 장치입니다.
- **Action tokenization (least likely token)** — 연속 액션을 VLM이 거의 쓰지 않는 토큰에 사상하는 기존 VLA 전략. 본 논문의 ablation(VLM2VLA-AT) 비교군입니다.
- **Co-training** — 로봇 데이터에 비로봇(VQA·캡션) 데이터를 섞어 정규화하는 forgetting 완화 표준 기법. 본 논문이 "불필요하다"고 도전하는 대상입니다.
- **3계층 reasoning (subtask / motion plan / action chunk)** — 고수준 하위과제 → 중수준 방향성 운동 계획 → 저수준 액션 청크로 이어지는 위계적 VQA 추론 사슬. 모두 언어로 표현됩니다.
- **Verifier (검증기)** — 각 action 사이클 후 subtask 완료 여부를 판정해 재시도/다음 진행을 결정하는 폐루프 모듈. 본 논문에서는 Gemini 2.5 Pro가 담당합니다.

---

## 🔬 방법론

### 직관 (Intuition)

핵심 통찰은 "LoRA가 forgetting을 막을 수 있지만, 그 효과는 fine-tuning 데이터가 모델의 사전학습 표현에 충분히 가까울 때만 성립한다"는 것입니다. 그래서 모델 쪽(아키텍처·토큰 사전)을 바꾸는 대신, **데이터 쪽**을 VLM의 표현 공간으로 끌어옵니다.

> "Our key insight is that while parameter-efficient methods like Low-Rank Adaptation (LoRA) [15] can avert catastrophic forgetting, their effectiveness relies on the fine-tuning data being sufficiently close to the model's pretrained representations." (§1)
> (LoRA의 forgetting 방지 효과가 "데이터가 사전학습 표현에 가까울 것"이라는 전제에 의존한다는 점을 명시 — 이 전제를 데이터 재표현으로 충족시키는 것이 논문 전체의 설계 의도입니다.)

> "We therefore propose resolving this representational mismatch at the data level." (§1)
> (불일치를 모델이 아니라 데이터 레벨에서 푼다는 선언 — model-agnostic하고 구현이 단순하다는 강점의 근거입니다.)

이 직관은 Fig. 3의 측정으로 뒷받침됩니다. Gemma-3-12B-IT는 액션을 언어로 표현했을 때 임의 토큰에 사상했을 때보다 유의하게 높은 log-probability를 부여합니다.

![Figure 3 — 언어 표현 vs 토큰 표현의 액션 확률 분포](https://arxiv.org/html/2509.22195/x3.png)

> "Figure 3: Distribution of action probabilities under Gemma-3-12B-IT before fine-tuning on robot teleoperation data. The model assigns significantly higher log-probabilities to actions represented as language compared to those defined by explicit tokenization modifications, e.g., least likely token assignment." (§1)
> (fine-tuning 이전부터 backbone이 "언어로 쓴 액션"을 자연스럽게 받아들인다는 것 — 데이터 정렬 가설의 직접 증거입니다.)

### 아키텍처

입력은 멀티모달 이미지-텍스트 토큰 시퀀스, 출력은 텍스트 토큰 시퀀스입니다. 즉 별도 액션 디코더 없이 단일 VLM(transformer)이 전 추론 위계를 책임지는 monolithic 구조입니다. 모든 관측은 RGB 이미지 공간에 존재합니다.

VLM2VLA는 액션 예측을 3단계 VQA 위계 추론으로 구성합니다. 주 과제를 $`N`$ 개 step(인덱스 $`i`$)으로 분해합니다.

- **High-Level Subtask Prediction ($`l_{i}`$)** — 관측 $`\bar{o}_{i}`$ 와 언어 지시 $`L`$ 이 주어지면, 주 과제 완수에 필요한 즉각 하위과제 $`l_{i}`$ 를 기술합니다.
- **Mid-Level Motion Planning ($`m_{i}`$)** — 현재 subtask와 관측을 조건으로, end-effector 기준의 공간 정보가 담긴 운동 계획 $`m_{i}`$ 를 생성합니다. 'move left', 'move down and slightly forward'처럼 **방향성 묘사만** 담는 거친 표현으로, VLM의 잠재 공간 추론 강점을 활용하려는 의도적 선택입니다.
- **Low-Level Action Generation ($`\bar{a}_{i}`$)** — 현재 subtask와 motion plan을 조건으로, 로봇에 직접 실행할 가변 길이 action chunk $`\bar{a}_{i}`$ 를 생성합니다. action chunk는 "리스트의 리스트"이며 각 내부 리스트가 각 DoF의 명령을 텍스트로 담습니다. 본 연구는 병진(translational) DoF만 다룹니다.

![Figure 4 — 로봇 궤적을 자연어 3계층으로 재라벨링하는 파이프라인](https://arxiv.org/html/2509.22195/x4.png)

> "Figure 4: VLM2VLA's pipeline for annotating existing robot datasets $`\mathcal{D}_{\text{rob}}`$ into $`\mathcal{D}_{\text{lan}}`$ described via natural language. We use Gemini 2.5 [3] to decompose each trajectory into sub-trajectories, each with an associated subtask, motion plan, and action chunk." (§3)
> (원 로봇 데이터셋 $`\mathcal{D}_{\text{rob}}`$ 를 자연어 데이터셋 $`\mathcal{D}_{\text{lan}}`$ 으로 변환하는 핵심 데이터 큐레이션 단계를 시각화 — Gemini 2.5가 궤적을 sub-trajectory로 쪼개고 각 단계에 subtask·motion plan·action chunk를 붙입니다.)

추론 시(§3.1.1)에는 초기 관측 $`\bar{o}_{0}`$ 로 $`N`$ 개 subtask를 한 번에 생성해 rollout 동안 고정하고, 매 action-generation 사이클 끝에서 verifier가 현재 subtask 재시도 또는 다음 진행을 판정하는 폐루프로 운용합니다. verifier는 Gemini 2.5 Pro를 사용합니다.

### 학습 목표 / 손실

포착하려는 분포는 $`p_{\theta}(\bar{a}_{i},m_{i},l_{i}|\bar{o}_{i},L)`$ 이며, 다음과 같이 분해됩니다.

$$p_{\theta}(\bar{a}_{i},m_{i},l_{i}|\bar{o}_{i},L)=\underbrace{p_{\theta}(l_{i}|\bar{o}_{i},L)}_{\text{1) Subtask Prediction}}\underbrace{p_{\theta}(m_{i}|l_{i},\bar{o}_{i})}_{\text{2) Motion Planning}}\underbrace{p_{\theta}(\bar{a}_{i}|m_{i},l_{i},\bar{o}_{i})}_{\text{3) Action Generation}}$$

여기서 $`\theta`$ 는 로봇 정책의 가중치입니다. 이 매개변수화는 멀티모달 이미지-텍스트 입력 토큰 시퀀스를 받아 출력 텍스트 토큰 시퀀스를 예측하는 transformer에 그대로 대응합니다.

> "In summary, we transform our original robot dataset of state-action pairs into a dataset of image-text pairs, thereby casting robotic control as a standard supervised fine-tuning task. We fine-tune the Gemma-3-12B-IT model [1] using LoRA applied to all its linear modules using the cross-entropy loss." (§3.2)
> (액션을 언어로 바꾼 덕분에 로봇 제어가 표준 supervised fine-tuning으로 환원되고, 손실은 통상 텍스트 생성의 cross-entropy 하나뿐 — 별도 액션 손실·디코더가 없다는 것이 방법의 단순성을 보장합니다.)

### 학습 셋업

- **데이터** — BridgeData v2 중 주 과제 지시가 붙은 부분집합을 $`\mathcal{D}_{\text{rob}}`$ 로 사용. Gemini 2.5가 각 궤적을 3계층 자연어로 재라벨링해 $`\mathcal{D}_{\text{lan}}`$ 구성. 로봇의 base frame 좌표계(각 축이 DoF에 대응)를 프롬프트로 제공해 상대 end-effector 이동 주석 품질을 높였습니다.
- **데이터 전처리(§6.2)** — 단일 축 기준 임계 2.5cm(부호 변화 없이) 및 절대 임계 5cm로 action을 청킹해 더 큰 크기의 이동만 남깁니다(이 단계가 없으면 그럴듯한 motion plan에도 불구하고 액션 예측이 미미해지는 경향 관찰). 추가로 (1) subtask 완료 positive/negative 예시 $`(\bar{o}_{i},\bar{o}_{j},l_{i})`$, (2) 이동 방향(left/right/none) 예측을 보조 신호로 증강합니다.
- **모델 / PEFT** — Base: Gemma-3-12B-IT. 모든 linear module에 LoRA 적용. Rank $`r=16`$, $`\alpha=32`$, target modules = `q_proj, k_proj, v_proj, o_proj, up_proj, down_proj, gate_proj`. 정밀도 bfloat16.
- **옵티마이저 / 스케줄** — AdamW(β1=0.9, β2=0.999, ε=1e-8), learning rate 5e-5, linear decay. Effective global batch size 8(per-device 1 × grad accumulation 2 × 4 GPU), max sequence length 1024. 1 epoch 학습으로 충분했다고 보고.
- **하드웨어 / 프레임워크** — 단일 노드 4× NVIDIA A100, 약 300 GPU-hours. TRL + Accelerate + DeepSpeed ZeRO Stage 2, PEFT(LoRA).

---

## 📊 실험 설정과 결과

평가는 세 질문(Q1 멀티모달 이해 보존, Q2 in-distribution 조작 성능, Q3 추론 일반화)에 답하도록 설계되었습니다. 로봇 평가는 toy kitchen 환경의 6-DoF WidowX 250S 팔에서 과제당 30 trial(다국어 Pick Up -T는 3개 언어 × 30 = 90 trial)로 수행했습니다. 비교군은 토큰화 기반 SOTA VLA인 OpenVLA, 그 reasoning 변형 ECoT이며, co-trained VLA로 MolmoAct·$`\pi_{0.5}`$, action 표현 ablation으로 VLM2VLA-AT를 둡니다.

![Figure 2 — 기존 VLA의 과적합 vs VLM2VLA의 세계 지식 보존](https://arxiv.org/html/2509.22195/x2.png)

> "Figure 2: Traditional VLA training procedures often overfit to the robot training data, sacrificing their original reasoning capabilities for low-level action prediction (center). In contrast, VLM2VLA (right) preserves the world understanding of the nominal VLM (left), allowing the model to reason about potential safety risks instead of just motor commands." (§1)
> (기존 VLA는 저수준 액션 예측을 위해 추론 능력을 희생하지만, VLM2VLA는 원 VLM의 세계 이해를 보존한다는 논문의 핵심 대비를 시각화합니다.)

**Q1 — 멀티모달 이해 (VQA, Table 1)**

| Method | #Params | MMMU | MMStar | MME | OCRBench | MMB-en | TextVQA | DocVQA | AI2D | ChartQA | RealWorldQA |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Prismatic VLM | 7b | 35.0 | 38.8 | 1456.6 | 32.0 | 66.2 | 42.5 | 17.5 | 54.6 | 16.7 | 30.8 |
| OpenVLA | 7b | 26.3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| ECoT | 7b | 26.6 | 0 | 0 | 0.01 | 3.7 | 0 | 0 | 0 | 0 | 25.6 |
| Gemma-3-12B-IT | 12b | 46.0 | 46.3 | 1182.3 | 75.0 | 76.9 | 68.9 | 80.6 | 78.5 | 55.1 | 50.6 |
| VLM2VLA-AT | 12b | 45.9 | 45.2 | 1082.2 | 65.5 | 70.9 | 64.2 | 74.6 | 74.1 | 41.8 | 44.5 |
| **VLM2VLA (Ours)** | 12b | 42.7 | 48.0 | 1391.7 | 63.9 | 68.5 | 64.9 | 78.4 | 74.0 | 58.3 | 43.3 |
| MolmoAct | 7b | 28.4 | 1.2 | 1224.5 | 52.7 | 55.1 | 57.5 | 58.7 | 2.0 | 55.9 | 8.6 |
| $`\pi_{0.5}`$ | 3b | 24.0 | 21.7 | 1061.9 | 6.8 | 6.8 | 10.0 | 4.6 | 27.0 | 5.1 | 2.7 |

> "In contrast, VLM2VLA experiences only minor losses in performance across all VQA benchmarks, thereby conclusively answering Q1." (§4.1)
> (OpenVLA·ECoT가 대부분 벤치마크에서 0점에 수렴하며 forgetting을 겪는 반면, VLM2VLA는 backbone 대비 소폭 손실에 그칩니다.)

> "Moreover, our policy averts catastrophic forgetting, retaining over 85% of the base model's performance across challenging VQA benchmarks." (§1)
> (base 모델 성능의 85% 이상 유지 — 이 논문의 대표 정량 주장입니다.)

> "On the other hand, the significantly lower performance of $`\pi_{\text{0.5}}`$ across most VQA benchmarks underscores that co-training is not a guaranteed solution to catastrophic forgetting." (§4.1)
> (co-training을 쓴 $`\pi_{0.5}`$ 조차 VQA에서 크게 낮아, co-training이 forgetting의 보장된 해법이 아님을 시사 — P4 관점에서 주목할 반례입니다.)

또한 VLM2VLA-AT(토큰 표현 ablation)도 VQA 점수는 비슷해, **forgetting 완화는 주로 LoRA 학습 방식에 기인**하며 action 표현 선택은 VQA가 아니라 *하류 로봇 일반화*에서 갈린다고 해석합니다.

**Q2·Q3 — 로봇 조작 (Fig. 5, Fig. 6)**

ID(Pick Up, Pick and Place)에서는 더 큰 Open-X-Embodiment로 학습한 OpenVLA가 최고 성능이나, VLM2VLA도 경쟁력 있는 성공률로 Q2에 답합니다. 과제 복잡도가 오를수록 순수 반응형 OpenVLA의 이점은 줄어듭니다(복합 과제에서 첫 subtask는 성공하나 둘째를 시도하지 않음). OOD에서 차이가 가장 뚜렷합니다.

> "In the multilingual translation experiment (Pick Up - T), our method significantly outperforms both OpenVLA and ECoT." (§4.2.1)
> (스페인어·중국어·힌디어 지시를 암묵 번역해야 하는 다국어 OOD 과제에서 VLM2VLA가 두 비교군을 크게 능가 — §4.1에서 보존된 다국어 능력의 직접 적용입니다.)

> "Here, VLM2VLA is the only model to achieve a meaningful success rate." (§4.2.1)
> ('Ash Ketchum 위 물체 집기' 과제(대중문화 인물 인식 + 공간 추론 결합)에서 VLM2VLA만이 의미 있는 성공률 — 보존된 세계 지식의 zero-shot 활용으로 Q3에 긍정 답변.)

> "...VLM2VLA-AT struggles with multilingual commands and scores only half as well as VLM2VLA in the 'Pick Up the Item Above Ash Ketchum' task (achieving a success rate of just 30% to our model's 60%)." (§4.2.2)
> (action 표현 ablation은 VQA가 멀쩡해도 OOD 조작에서 절반 수준(30% vs 60%)으로 떨어져, "언어 표현"이 latent 세계 지식과 액션을 잇는 핵심임을 보입니다.)

**추론 지연 (Table 3, N=30)**

| 통계 | 값 |
|---|---|
| Median | 6.1 s |
| Mean | 10.5 s |
| Std | 14.3 s |
| IQR | 5.0 – 6.7 s |
| Min / Max | 3.8 s / 48.8 s |

> "...the median run-time required for one cycle of action generation was 6.1 seconds, though subject to high variance..." (§5.1)
> (자기회귀 텍스트 생성 기반이라 본질적으로 느리며, 약 10%의 재시도(출력 포맷 불량)와 일부 >45초 trial이 높은 분산의 원인입니다.)

---

## ⚖️ 한계

- **추론 지연** — 자기회귀 생성으로 1 action 사이클 median 6.1초, 분산 큼. 실시간 제어에 부적합하며 가속 디코딩이 미해결 과제입니다.
- **병진 제어로 제한 (Dexterity 부재)** — 본 연구는 병진 end-effector 제어만 다뤄, 회전 등 정밀 액션이 필요한 다지/접촉 집약적 조작은 배제됩니다. motion plan 입자도 거칠어 더 세밀한 언어 주석이 필요합니다. **PROBE 관점에서 가장 큰 갭.**
- **단일 embodiment** — 특정 로봇(WidowX, 상대 위치 제어)에 한정. joint angle 같은 다른 저수준 제어로는 바로 옮겨가지 못합니다(저자는 언어 매개 cross-embodiment를 향후 방향으로 제시).
- **외부 verifier 의존** — subtask 전환을 별도 Gemini 2.5 Pro verifier에 의존해 추론을 더 느리게 만들며, base VLM 자체를 verifier로 학습시키는 시도는 실패했다고 보고.
- **평가 범위** — 전 과제가 'pick up'/'pick and place'류이고 BridgeData v2 toy kitchen 환경에 한정. 모델 크기(12B vs 비교군) 교란 변수도 저자 스스로 인정.

---

## ♻️ 재현성

- **코드 / 사이트** — 프로젝트 페이지 `https://vlm2vla.github.io/` 에 추가 정보·영상·코드 공개 명시.
- **데이터** — 공개 BridgeData v2 부분집합 + Gemini 2.5 기반 재라벨링 파이프라인(프롬프트·전처리 임계·토큰 매핑이 부록 6에 상세 기재).
- **모델** — Gemma-3-12B-IT(공개 가중치) + LoRA. 하이퍼파라미터 전체가 Table 4에 명시되어 재현 친화적.
- **하드웨어** — 학습: 4× A100, 약 300 GPU-hours, 1 epoch. 평가: 6-DoF WidowX 250S + Realsense D435, NVIDIA A100 추론.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P4 (VLM Pretraining Preservation) — 정중앙.** 이 논문은 이미 `context/MASTER.md` §8.4에 P4 핀 논문으로 등재(arXiv:2509.22195)되어 있으며, "VLM init = Gemma-3-12B-IT (LoRA on all linear modules) × BridgeData v2 NL-formatted" 라인으로 D19b lineage 카탈로그에 들어가 있습니다.
- **[D19] VLM fine-tuning range** — v1은 (a) full freeze + action experts only. 본 논문은 (d) **LoRA** 경로의 가장 강한 실증으로, D19 deferred trigger("frozen backbone representation insufficient for new modality combos")가 발화했을 때 가장 먼저 참조할 레퍼런스입니다.
- **[D20] Prior-preservation strategy** — 본 논문은 "LoRA-minimal (VLM2VLA, NL-style action)" 옵션 그 자체입니다. 현재 standby이나, D19가 freeze를 벗어나는 순간 D20의 1순위 후보 메커니즘입니다.
- **[D23] Action representation × VLM preservation** — v1은 (iii) flow-matching head. 본 논문은 (ii) **NL-style action representation**의 직접 사례이며, D23 deferred("D20 moves to LoRA-minimal/VLM2VLA path")의 트리거 논문으로 MASTER.md에 이미 명시되어 있습니다.
- **Identity 긴장** — PROBE Identity는 (iii) flow-matching 연속 액션 전문가 + backbone 미동결 보존을 택합니다. VLM2VLA는 정반대 축(별도 디코더 없이 NL 토큰 + LoRA)을 취하므로, "어느 쪽이 prior를 더 잘 보존하면서 dexterity까지 가능한가"의 핵심 대립항입니다. 단, VLM2VLA가 병진 제어에 그쳐 dexterity를 명시적으로 배제한 점은 PROBE의 다지 조작 Identity와 직접 충돌하지 않고 오히려 보완적 증거가 됩니다.
- **§10 경쟁자 함의** — Antagonist C(monolithic decoder) 계열에 속하나, "post-hoc correction"이 아니라 데이터 정렬로 접근하므로 Anti-topic 배제 대상은 아닙니다(P4 forgetting 분석 명시 → in-scope).
- **건드리지 않는 부분** — P1(Body/Hand split), P2(구조적 입력 결합), P3(System0 RL)와는 직접 관련이 없습니다(액션 디코더 아키텍처·촉각·접촉 RL을 다루지 않음).

---

## ✨ 핀 논문 대비 델타

기준 핀 논문은 같은 P4의 **π0 / π0.5**(arXiv:2410.24164 / 2504.16054)와 **RT-2**(arXiv:2307.15818)입니다.

- **π0/π0.5 대비** — π 계열은 PaliGemma backbone + flow-matching 액션 전문가 + (π0.5는) co-training으로 일반화를 확보합니다. VLM2VLA는 **액션 전문가·co-training을 모두 제거**하고 데이터 재표현 + LoRA만으로 같은 목표(forgetting 회피)를 노린다는 점이 진정한 델타입니다. 특히 본 논문 Table 1은 $`\pi_{0.5}`$ 의 VQA 점수가 낮다는 반례를 제시해 "co-training ≠ forgetting 보장 해법"이라는 주장을 실증합니다.
- **RT-2 대비** — RT-2는 web/robot co-FT로 prior를 유지하지만 막대한 co-training 비용을 전제합니다. VLM2VLA는 co-training을 명시적으로 부정하고, "값비싼 혼합 데이터 없이 데이터 레벨 정렬"이라는 더 싼 대안을 주장합니다.
- **새로움의 핵심** — *저수준 액션까지* 언어로 표현하고 *액션 디코더를 전혀 두지 않는* 점. 기존 reasoning VLA(ECoT 등)는 고수준 추론만 언어로 두고 액션은 토큰/디코더로 처리했습니다.

---

## ⚙️ 의사결정 함의

이 논문이 맞다면 PROBE의 P4 파이프라인에서 다음이 바뀔 수 있습니다.

- **D19 트리거 시 1순위 경로 확정** — frozen backbone이 새 모달리티 조합(촉각 + 구조적 토큰)에 부족하다고 판명되면, full-FT가 아니라 **LoRA(rank 16, α 32, all linear modules: `q/k/v/o/up/down/gate_proj`, lr 5e-5, AdamW)** 를 D19(d)의 구체적 기본값으로 채택할 근거가 생깁니다. 이는 막연한 "LoRA 검토"를 수치화된 config로 전환합니다.
- **`co_train_ratio` 하이퍼파라미터 회피** — D21 Stage 3/4에서 co-training mixture ratio 튜닝(수많은 학습·실평가 필요)을 도입하기 전에, "데이터 정렬 + LoRA"가 co-training을 대체할 수 있는지를 먼저 검증하는 분기를 추가할 가치가 있습니다. 검증 지표는 VQA 보존율(base 대비 ≥85%)입니다.
- **D23 분기의 비용/이득 재평가** — 단, PROBE는 dexterity(회전·접촉)를 핵심으로 두는데 VLM2VLA는 병진만 다루므로, **NL-style action(D23 (ii))을 채택하면 finger joint·rotation 같은 고차원 연속 명령을 텍스트로 표현해야 하고 추론 지연(median 6.1s)이 sub-policy-loop 속도 요구(P3 System0)와 정면 충돌**합니다. 따라서 D23 v1(flow-matching head) 유지가 합리적이며, VLM2VLA는 "VLM 보존 측정 프로토콜"(VQA 보존율)을 빌려오는 용도로 더 가치 있습니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **가장 싼 sanity check — 추론 지연** — VLM2VLA의 median 6.1초/사이클은 PROBE의 in-hand 회전(5초 episode, 고주파 finger loop)과 양립 불가입니다. NL-action 경로를 고려하기 전에 "우리 과제의 control rate 요구 vs 자기회귀 텍스트 생성 지연"을 책상 위 계산만으로 먼저 기각/통과시킬 수 있습니다.
- **병진→다지 전이 실패** — 이 방법의 검증은 전부 4-DoF 병진 pick-and-place입니다. 22-DOF Sharpa Hand의 회전·접촉 명령을 자연어로 표현했을 때 Gemini 주석 품질과 정밀도가 유지되는지는 전혀 검증되지 않았습니다. 저자도 dexterity를 명시적 한계로 인정.
- **보존 측정의 표면성** — VQA 점수 보존이 곧 "조작에 유용한 prior 보존"인지는 VLM2VLA-AT 사례(VQA는 보존되나 OOD 조작은 절반)가 경고합니다. PROBE가 VQA 보존율을 P4 falsifier로 차용한다면, 반드시 *조작 OOD 성공률*과 함께 측정해야 합니다.
- **backbone 불일치** — VLM2VLA는 Gemma-3-12B-IT 기반이고 PROBE v1 lineage는 PaliGemma-2B × π0 mix입니다. LoRA 효과·NL-action 친화성이 backbone lineage에 의존할 수 있어, 결과를 그대로 PROBE 스택에 이식할 수 없습니다.

---

## 💡 컨텍스트 제안

- **핀 유지** — 이미 P4 핀(§8.4)이자 §10 Antagonist 맥락에 등재돼 있어 신규 핀 교체 제안은 없습니다. 다만 §8.4 표의 VLM2VLA 역할 설명에 **"co-training 불필요성의 실증 반례(특히 $`\pi_{0.5}`$ VQA 저하)"** 를 한 줄 보강하면 D20/D21 의사결정 시 근거가 더 또렷해집니다(사람이 판단·반영).
- **방법론 참조 후보** — 본 논문의 "VQA 보존율(base 대비 %)" 측정 프로토콜은 `analysis/_catalogs/vlm-prior-preservation.md`의 forward-KL 측정 프로토콜과 상호 보완적입니다. 동 문서에 VLM2VLA의 행동-언어 정렬을 "데이터 레벨 분포 정렬" 사례로 cross-link하는 것을 제안드립니다(사람이 판단).
- **나머지** — D1–D18, D24–D26 등 다른 Decision과의 연결은 없습니다(연결 날조 금지).

> 💡 base 매핑은 `/implement analysis/2509.22195/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
