# Paper Analysis — TAIL: Task-specific Adapters for Imitation Learning with Large Pretrained Models

> PROBE analysis 모드 산출물. 단일 한글 문서이며, 영문 1차 파일은
> 없습니다. 형식·이모지·용어 규칙은 `docs/STYLE.md` §5 / §4 를
> 정확히 따릅니다. 재실행 시 이 파일을 덮어씁니다.

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | TAIL: Task-specific Adapters for Imitation Learning with Large Pretrained Models |
| 저자 | Zuxin Liu, Jesse Zhang, Kavosh Asadi, Yao Liu, Ding Zhao, Shoham Sabach, Rasool Fakoor (CMU · USC · Amazon Web Services) |
| 링크 | [arXiv:2310.05905](https://arxiv.org/abs/2310.05905) |
| 발행일 / 버전 | 2023-10-09 · v2 (2024-03-08 개정) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-05-28 |

---

## 🧭 한 줄 요약 (TL;DR)

대규모 사전학습 정책 모델을 새로운 제어 과제 스트림에 적응시킬 때, 전체 미세조정(FFT) 대신 LoRA·Bottleneck·Prefix 같은 파라미터 효율적 어댑터(PEFT)를 끼워 넣어 전체 파라미터의 약 1%만 학습하고도 최고 적응 성능을 얻으면서 catastrophic forgetting을 피하는 연속 모방 학습(continual imitation learning) 프레임워크 TAIL을 제안합니다. 세 가지 통합 방식을 동일 조건에서 비교한 결과 LoRA(병렬 통합)가 가장 우수합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 대규모 사전학습 모델을 로봇 제어처럼 데이터가 희소하고 연산이 비싼 영역에서, 끊임없이 들어오는 새 과제에 데이터 효율적으로 *연속 적응*시키는 방법을 찾는다.
- **기존 접근의 한계** — 전체 미세조정(FFT)은 자원 소모가 크고 소량 데이터에서 과적합하며, 사전학습 특징을 왜곡해 이전 과제를 잊는 catastrophic forgetting과 적응 가소성(plasticity) 상실을 유발합니다. 반대로 특징을 동결한 채 헤드만 바꾸는 FPF는 표현력이 부족해 분포 밖·복잡 과제에 약합니다.
- **본 논문의 가설** — 언어 모델 영역의 PEFT 기법(소수 파라미터만 추가)을 의사결정 모델에 옮기면, 사전학습 특징을 보존하면서 망각 없이 새 과제를 흡수할 수 있다.
- **왜 지금 중요한가** — 사전학습 모델을 과제마다 통째로 복제·미세조정하는 방식은 저장·연산 측면에서 비현실적이며, 실세계 로봇은 과제가 순차적으로 늘어나는 연속학습 환경에 놓이기 때문입니다.

---

## 🧩 핵심 기여

- 연속 모방 학습을 위한 통합 어댑터 프레임워크 **TAIL** 을 제안하고, 언어 영역의 세 가지 대표 PEFT 통합 방식(병렬=LoRA, 순차=Bottleneck Adapter, 접두 토큰=Prefix/Prompt-Tuning)을 의사결정 모델에 동일 조건으로 이식·비교합니다.
- LIBERO 기반의 다양한 연속학습 과제 묶음(Kitchen 사전학습 40과제 + Spatial/Goal/Object/Living Room/Study Room 5개 적응 묶음 + LIBERO-10 장기 과제)에서 FFT·ER·EWC·PackNet·FPF 등 표준 적응 기법과 광범위하게 비교합니다.
- **TAIL + LoRA** 가 FFT 대비 학습 파라미터 약 1%만으로 최고 적응 성능을 달성하면서 catastrophic forgetting을 피하고 적응 가소성을 보존함을 실증합니다 (LIBERO-10 BWT = 0, 즉 망각 없음).
- 통합 방식별 성능 서열(LoRA > Prefix > Bottleneck > RoboAdapter)을 제시하고, 어텐션 내부/주변에 가중치를 끼우는 위치가 성능에 결정적임을 분석합니다.

---

## 🔑 기술 키워드

- **PEFT (Parameter-Efficient Fine-Tuning)** — 사전학습 가중치는 대부분 동결하고 소수의 새 파라미터만 학습하는 적응 기법군. TAIL이 토대로 삼는 기법군으로, 큰 모델에 "작은 부속"만 갈아 끼우는 방식이다.
- **LoRA (Low-Rank Adaptation)** — 가중치 행렬에 저랭크 행렬 $`{\mathbf{W}}_{down}`$, $`{\mathbf{W}}_{up}`$ 를 *병렬로 더하는* 방식. 본 논문에서 가장 우수한 통합 스타일로 확인됩니다.
- **Bottleneck Adapter** — 피드포워드 뒤에 down→비선형→up 병목층을 *순차적으로* 삽입하는 방식. "정보 필터"처럼 동작하지만 파라미터·지연이 더 큽니다.
- **Prefix Token (Prefix/Prompt-Tuning)** — 입력 시퀀스 앞에 학습 가능한 가상 토큰을 붙여 과제 기술자로 쓰는 방식. Transformer 전용이며 LoRA 다음으로 우수합니다.
- **Continual Imitation Learning (연속 모방 학습)** — 과제가 순차적으로 들어오고 이전 과제 데이터에 더는 접근할 수 없는 모방 학습(IL) 설정. catastrophic forgetting과 forward/backward transfer가 핵심 평가축입니다.
- **Catastrophic forgetting (파국적 망각)** — 새 과제를 학습하며 이전 과제 성능이 무너지는 현상. TAIL이 어댑터로 과제 지식을 격리해 방지하려는 표적입니다.
- **Adaptation plasticity (적응 가소성)** — 모델이 새 과제를 빠르게 흡수하는 능력. 과도한 FFT가 이를 깎는다는 것이 본 논문의 주요 동기입니다.
- **FiLM (Feature-wise Linear Modulation)** — 언어 과제 임베딩으로 관측 토큰을 $`(\gamma,\beta)`$ 변조해 입력을 융합하는 층. 본 논문의 입력 융합 모듈로 사용됩니다.
- **FWT / BWT (Forward / Backward Transfer)** — 새 과제 최대 성공률(FWT)과 이전 과제 성공률 변화(BWT)로 연속학습을 계측하는 LIBERO 지표. 둘 다 높을수록 좋습니다.

---

## 🔬 방법론

### 직관

핵심 직관은 "사전학습 모델의 표현은 그대로 두고, 과제별 지식은 작은 어댑터 안에만 가두자"입니다. FFT는 모델 전체를 움직여 사전학습 특징을 왜곡하고 망각을 부르지만, 사전학습 모델은 낮은 내재 차원(intrinsic dimension)만으로도 효과적으로 학습되므로 저랭크 부속만 추가해도 충분하다.

> "TAIL introduces a small set of new weights, serving as a lightweight plugin to address specific tasks." (§4)
(TAIL은 새 과제마다 소수의 새 가중치를 가벼운 플러그인으로 끼워 넣을 뿐, 사전학습 표현 자체는 건드리지 않는다는 설계 선언입니다.)

> "By optimizing the behavior cloning loss in Eq. 1 w.r.t $`\mathbf{\omega}_{k}`$ while keeping the pretrained weights frozen, the policy adapts to $`\mathcal{T}_{k}`$ without interfering with previous tasks." (§4.2)
(사전학습 가중치 $`\mathbf{\theta}`$ 를 동결한 채 어댑터 가중치 $`\mathbf{\omega}_{k}`$ 만 학습하므로, 새 과제 적응이 이전 과제와 간섭하지 않는다는 망각 회피의 수학적 근거입니다.)

### 아키텍처

![Figure 1 — multi-modal transformer policy + 3 fine-tuning paradigms](https://arxiv.org/html/2310.05905/x1.png)

> "Figure 1: (a): The multi-modal, transformer policy architecture we utilize for pretraining. We encode language task descriptions with a pretrained CLIP instruction encoder and image observations with a pretrained CLIP spatial encoder. We additionally encode state observations (not pictured) which, along with the observation embeddings, are embedded into a sequence of tokens used by the temporal decoder transformer to predict single-step action distributions. We include an input fusion module to explicitly combine the task embedding with the observation token sequence for better instruction-following ability. (b): The three types of fine-tuning paradigms we test, with TAIL at the bottom right." (§3)
(전체 정책 골격(왼쪽)과 FFT/FPF/TAIL 세 적응 패러다임(오른쪽)을 한눈에 보여 줍니다 — 정책은 CLIP 인코더 + FiLM 융합 + GPT-2 시간 디코더로 구성됩니다.)

- **입력 인코더** — 언어 지시는 사전학습된 CLIP 텍스트 인코더로, 이미지 관측은 사전학습된 CLIP 공간 인코더로 인코딩합니다. 상태(joint state) 관측도 별도로 인코딩합니다. 실험에서는 CLIP-base(각 12 Transformer 층)를 사용합니다.
- **입력 융합** — FiLM 층으로 언어 과제 임베딩과 관측 토큰을 명시적으로 융합해 지시 추종 능력을 높입니다.
- **시간 백본** — 표준 GPT-2 디코더(실험에서는 6층)가 이전 타임스텝의 토큰화된 관측을 attend 하여 단일 스텝 연속 액션 분포를 출력합니다.
- **어댑터 삽입 위치** — 사전학습 단계에서는 동결된 CLIP 인코더에 어댑터를 추가하고 나머지(GPT-2·융합·헤드)는 완전 학습합니다. 적응 단계에서는 CLIP 인코더와 GPT-2 디코더를 동결하고, 그들의 어댑터 + 융합 모듈 + 정책 헤드만 학습합니다.

![Figure 2 — three weight integration styles](https://arxiv.org/html/2310.05905/x2.png)

> "Figure 2: Demonstration of three weight integration styles of TAIL for a Transformer block: sequential (bottleneck adapter), parallel (LoRA), and prefix token (prefix/prompt-tuning)." (§4.1)
(하나의 Transformer 블록에 세 통합 방식이 각각 어디에 끼워지는지를 도식화합니다 — 병렬(LoRA)은 가중치 옆에, 순차(Bottleneck)는 FFN 뒤에, 접두 토큰은 입력 시퀀스 앞에 삽입됩니다.)

세 통합 방식은 사전학습 가중치 행렬 $`{\mathbf{W}}\in\mathbb{R}^{d\times k}`$ ($`h_{out}={\mathbf{W}}^{\top}h_{in}`$)에 대해 다음과 같이 정의됩니다.

- **병렬 통합 (LoRA)** — 저랭크 $`{\mathbf{W}}_{down}\in\mathbb{R}^{d\times r}`$, $`{\mathbf{W}}_{up}\in\mathbb{R}^{r\times k}`$ ($`r\ll\min(d,k)`$)를 원래 가중치에 병렬로 더합니다. 멀티헤드 어텐션의 $`W_{Q}`$, $`W_{V}`$ 투영에 주로 적용합니다.
- **순차 통합 (Bottleneck Adapter)** — FFN 뒤에 down→비선형 $`\phi`$→up 병목층을 직렬로 붙입니다. 필터 역할이지만 LoRA보다 큰 병목 크기가 필요하고 지연이 늘어납니다.
- **접두 토큰 통합 (Prefix/Prompt-Tuning)** — 학습 가능한 가상 토큰 $`\mathbf{p}\in\mathbb{R}^{m\times d}`$ 를 입력 시퀀스 $`\mathbf{s}`$ 앞에 붙여 $`\mathbf{S}=[\mathbf{p};\mathbf{s}]\in\mathbb{R}^{(m+n)\times d}`$ 로 확장합니다.

### 학습 목표 / 손실

표준 행동 복제(behavioral cloning) 손실을 사용하되, TAIL에서는 전체 파라미터 $`\mathbf{\theta}`$ 대신 어댑터 가중치 $`\mathbf{\omega}`$ 에 대해 최적화합니다 (모델은 $`\hat{\mathbf{\theta}}=\{\mathbf{\theta},\mathbf{\omega}\}`$ 로 매개화되며 $`\mathbf{\theta}`$ 는 동결).

기본 BC 최적화 목표 (Eq. 1):

$$\hat{\mathbf{\theta}}=\min_{\mathbf{\theta}}\sum_{k=1}^{K}\underset{s_{t},a_{t}\sim\mathcal{D}_{k}}{\mathbb{E}}\left[\sum_{t=0}^{l_{k}}\mathcal{L}\left(\pi(a|s_{\leq t},\mathcal{T}_{k};\mathbf{\theta}),a_{k}^{t}\right)\right]$$

여기서 $`\mathcal{L}`$ 은 지도 액션 예측 손실(MSE 또는 음의 로그가능도), $`l_{k}`$ 는 과제 $`\mathcal{T}_{k}`$ 시연 길이, $`K`$ 는 과제 수입니다.

LoRA 통합 (Eq. 2):

$$h_{out}={\mathbf{W}}^{\top}h_{in}+\alpha{\mathbf{W}}_{up}^{\top}{\mathbf{W}}_{down}^{\top}h_{in}$$

$`\alpha`$ 는 과제별 조정량을 조절하는 하이퍼파라미터이며, $`\Delta{\mathbf{W}}={\mathbf{W}}_{up}^{\top}{\mathbf{W}}_{down}^{\top}`$ 의 열은 과제별 지식을 담은 새 기저로 해석됩니다.

Bottleneck Adapter 통합 (Eq. 3):

$$h_{out}={\mathbf{W}}_{up}^{\top}\phi\left({\mathbf{W}}_{down}^{\top}({\mathbf{W}}^{\top}h_{in})\right)$$

$`\phi`$ 는 비선형 활성입니다.

### 학습 셋업

- **데이터** — 과제당 50개 인간 시연(40 학습 / 10 검증), 학습에서 보지 못한 초기 상태의 10개 장면에서 성공률 평가. 한 과제 묶음 내 모든 과제를 동시에 학습·평가해 난이도를 높이고, 묶음당 어댑터 1개를 사용합니다.
- **사전학습 / 적응** — Kitchen(40과제)에서 수렴까지 100 에폭 사전학습 후, (1) Spatial→Goal→Object→Living Room→Study Room 순차 적응(각 100 에폭), (2) LIBERO-10 장기 과제 각각 50 에폭 적응. 각 실험은 3개 시드.
- **최적화** — AdamW + 선형 LR 스케줄러, 학습률 1e-4. 배치 크기는 방법별 상이(EWC 10, FFT·ER 14, TAIL 18). 5 에폭마다 8 에피소드로 평가.
- **어댑터 설정 (AdapterHub 기본값 기반)** — LoRA: rank $`r=8`$, scaling $`\alpha=8`$, Q/V 투영에 적용. Prefix: 토큰 길이 30, 안정화를 위해 $`r=16`$ 저랭크 표현. Bottleneck: 병목 크기 32, 어텐션 출력과 중간 FFN에 적용. RoboAdapter: 특정 층(0,1,5,6,10,11)에만 FFN 뒤 삽입, 병목 크기 64로 두 배.

---

## 📊 실험 설정과 결과

평가 지표는 과제 묶음별 평균 성공률, 그리고 연속학습용 Forward Transfer(FWT)·Backward Transfer(BWT)입니다. 환경은 LIBERO 로봇 조작 연속학습 벤치마크(6-DOF 팔 + 평행 그리퍼, 2개 시점 RGB + joint state + 언어 지시)입니다.

> "TAIL with LoRA can achieve the best post-adaptation performance with only 1% of the trainable parameters of full fine-tuning while avoiding catastrophic forgetting and preserving adaptation plasticity in continual learning settings." (§Abstract)
(LoRA 기반 TAIL이 FFT 학습 파라미터의 약 1%만으로 최고 적응 성능 + 무망각 + 가소성 보존을 동시에 달성한다 — 이 논문의 핵심 결과다.)

> "LoRA performs best across all tasks, underscoring the benefits of the parallel integration approach." (§5.3, Fig. 4)
(통합 방식 비교에서 병렬 통합인 LoRA가 모든 과제에서 최고 — 사전학습 모델이 IL 과제에서 갖는 내재 차원이 매우 낮다는 뜻이다.)

LIBERO-10 장기 과제 적응 결과 (Table 1, 평균, 높을수록 좋음):

| 분류 | 방법 | FWT ↑ | BWT ↑ |
|------|------|-------|-------|
| Conventional | Full Fine-Tuning | 0.48 ± 0.10 | -0.55 ± 0.21 |
| Conventional | Experience Replay | 0.45 ± 0.09 | -0.49 ± 0.23 |
| Conventional | EWC | 0.30 ± 0.16 | -0.43 ± 0.20 |
| TAIL (Ours) | LoRA | 0.70 ± 0.10 | 0 (무망각) |
| TAIL (Ours) | Prefix | 0.51 ± 0.15 | 0 (무망각) |
| TAIL (Ours) | Bottleneck | 0.46 ± 0.11 | 0 (무망각) |
| TAIL (Ours) | RoboAdapter | 0.42 ± 0.13 | 0 (무망각) |

> "TAIL again performs best, with perfect backward transfer and forward transfer capabilities significantly better than the baselines" (§5.3, Table 1)
(TAIL 계열은 모두 BWT=0(완전 무망각)이며, LoRA는 FWT 0.70으로 FFT(0.48)·ER(0.45)·EWC(0.30)를 크게 앞섭니다. 관습적 기법은 모두 큰 음의 BWT로 이전 과제를 심하게 잊는다.)

학습 파라미터·메모리 효율 (Table 3, FFT 대비):

| 구성요소 | Full Fine-Tuning | LoRA | RoboAdapter | Bottleneck | Prefix |
|------|------|------|------|------|------|
| CLIP (Spatial & Task) | 149.62M | 0.49M | 1.29M | 1.31M | 0.58M |
| GPT2 (Temporal) | 21.78M | 0.69M | 0.40M | 0.40M | 0.24M |
| Fusion + policy head | 0.84M | 0.84M | 0.84M | 0.84M | 0.84M |
| Total | 172.24M | 2.02M (1.17%) | 2.53M (1.47%) | 2.55M (1.48%) | 1.66M (0.93%) |

![Figure 5 — continual learning success rates over 6 stages](https://arxiv.org/html/2310.05905/x5.png)

> "Figure 5: Success rates on the pretraining stage on 40 tasks in the LIBERO Kitchen scene and 5 adaptation stages, each with 8 tasks over 100 epochs, which are continuously evaluated in subsequent stages (shaded area)." (§5.3)
(사전학습 + 5단계 순차 적응 과정에서 각 단계 성공률을 추적 — 이후 단계에서도 이전 과제(음영)를 재평가하는데, TAIL은 망각 없이 성능을 그대로 유지한다.)

또한 FFT는 가장 낮은 학습 손실을 달성하지만 검증 손실이 몇 에폭 만에 급등(소량 데이터 과적합·사전학습 특징 왜곡)하며, circle-back 실험(Table 2)에서 이전 과제 재방문 시 같은 데이터로 재학습해도 성능이 급락합니다. TAIL은 적은 학습 파라미터(Occam's razor) 덕에 과적합 저항이 강합니다.

---

## ⚖️ 한계

- **저자 명시** — TAIL 효과는 기반 모델 특징 품질에 크게 의존합니다. 사전학습 인코더(CLIP)를 미세조정하면 niche 도메인·희소 데이터에서 FFT가 CLIP 특징을 오염시켜 성능이 떨어지므로, 동결 CLIP + 자체 사전학습 골격에서 가장 잘 작동합니다.
- **과제 식별 가정** — 추론 시 어느 어댑터를 활성화할지 과제 식별(묶음당 어댑터 1개)을 알아야 합니다. 과제 경계가 모호하거나 자동 라우팅이 필요한 단일 배포 정책에는 그대로 적용되지 않습니다.
- **모델 규모** — 백본이 CLIP-base + 6층 GPT-2(총 172M)로 비교적 작습니다. 수십억 파라미터급 VLA에서 동일 랭크·배치 설정이 유지될지는 본문 범위 밖입니다.
- **모달리티 범위** — 모든 과제가 동일 모달리티(RGB·joint·언어) 안의 새 *과제*일 뿐, 새로운 *센서 모달리티*(예: 촉각) 추가는 다루지 않습니다. 평행 그리퍼 조작에 한정되어 접촉 집약적 다지 조작은 없습니다.

---

## ♻️ 재현성

- **벤치마크** — 공개된 LIBERO 연속학습 벤치마크(Liu et al., 2023a)를 사용하며, 과제 묶음 구성(Kitchen 40 + 5 적응 묶음 + LIBERO-10)을 명세합니다.
- **하이퍼파라미터** — Appendix B에 어댑터 설정(AdapterHub 기반), 옵티마이저(AdamW), 학습률(1e-4), 에폭·배치·시드(3개)를 구체적으로 기재해 재현 가능성이 높습니다.
- **코드/데이터** — 본문에서 별도 코드 저장소 URL을 본 추출에서 확인하지 못했습니다(프로젝트 페이지 가능성 있음 — 미확인). 사용된 기반 모델(CLIP, GPT-2), 어댑터 구현(AdapterHub)은 모두 공개 자산입니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P4 (VLM 사전학습 보존) — 정면 직결**. TAIL은 PEFT(LoRA/Bottleneck/Prefix)로 사전학습 특징을 동결·보존하며 catastrophic forgetting을 피하는 연속 적응 방법으로, P4의 핵심 주제와 곧장 겹칩니다. 구체적으로:
  - **D19 (VLM FT 범위)** — 옵션 (d) LoRA/adapter PEFT 및 (a) full freeze + action experts only 의 직접 실증. TAIL은 "동결 백본 + 소수 어댑터"가 FFT보다 우월하다는 것을 수치로 입증한다.
  - **D20 (prior-preservation strategy)** — 옵션 중 LoRA-minimal / action-side adapter 의 근거. TAIL은 어댑터가 과제 지식을 격리해 백본 분포를 건드리지 않음을 BWT=0 으로 입증합니다.
  - **D21 (staged training recipe)** — Stage 3 "LoRA / top-layer 제한 FT" 의 레시피·하이퍼파라미터 참고(rank 8, α 8, Q/V 적용).
  - **D23 (action representation × VLM preservation)** — TAIL은 연속 액션 분포 헤드를 쓰며 백본을 액션 토큰 예측기로 끌어들이지 않아, v1 (iii) flow-matching head 와 "VLM을 의미 역할에 유지" 철학을 공유합니다(단 TAIL 자체는 flow matching이 아닌 BC 헤드).
- **P1 (이종 Body/Hand 액션 전문가) — 부분 지지**. TAIL의 입력 융합이 **FiLM** 인데, 이는 **D4 v1**(FiLM with $`a_b`$ → $`(\gamma,\beta)`$)의 메커니즘 선택과 동일 계열입니다. FiLM이 멀티모달 정책 융합에서 실효를 낸다는 점을 다시 입증하는 사례다.
- **Identity 긴장/지지** — Identity의 "VLM-pretraining preservation" 축을 직접 지지합니다. 다만 TAIL의 어댑터는 "동결 VLA 위에 얹는 부속"이라는 점에서 Antagonist A(보정/잔차 모듈은 분포 한정)와 형식이 닮아 보일 수 있으나, TAIL은 *과제 적응*용 PEFT이지 출력 보정 모듈이 아니므로 직접 충돌하지는 않습니다 — 오히려 P4 보존 도구로 분류됩니다.
- **§10 경쟁자 함의** — 직접적 경쟁 제품은 아니며, P4 방법론 레퍼런스(VLA-Adapter / PriorVLA / VLM2VLA 계열)와 같은 PEFT 가족에 속합니다.

---

## ✨ 핀 논문 대비 델타

- **vs VLM2VLA ([arXiv:2509.22195], P4 핀)** — VLM2VLA는 대형 VLM(Gemma-3-12B)에 LoRA *단일* 경로 + NL-style action을 적용한 망각 완화 연구입니다. TAIL은 그보다 2년 앞선(2023) 연구로, LoRA·Bottleneck·Prefix를 **동일 조건에서 머리를 맞대고 비교(head-to-head ablation)** 하여 "왜 LoRA인가"의 근거를 제공합니다. VLM2VLA가 전제로 깔고 들어가는 PEFT 선택의 비교 실험을 TAIL이 채워 줍니다.
- **vs π0 / π0.5 ([arXiv:2410.24164], [arXiv:2504.16054], P4 핀)** — π0 계열은 frozen-backbone + action-expert 패턴을 대형 VLA 스케일에서 채택합니다. TAIL은 동일 철학(특징 보존 + 소수 학습 파라미터)을 *연속학습* 축에서 명시적으로 검증하고 망각 지표(BWT)·가소성·과적합까지 정량화한다는 점이 새롭습니다.
- **vs RT-2 ([arXiv:2307.15818], P4 핀)** — RT-2는 web/robot co-FT로 prior를 보존하는 반면, TAIL은 데이터·연산 효율적 PEFT로 보존합니다. "co-training 없이도 동결+어댑터로 보존 가능"하다는 점이 델타입니다.
- **진정으로 새로운 점** — 의사결정/IL 도메인에서 세 PEFT 통합 스타일을 *연속학습 망각·가소성·파라미터 효율* 세 축으로 동시에 측정하고 서열화(LoRA > Prefix > Bottleneck > RoboAdapter)한 점, 그리고 통합 *위치*(어텐션 내부/주변 vs FFN 뒤)가 성능에 결정적임을 짚은 점입니다.

---

## ⚙️ 의사결정 함의

- **D19 → (d) LoRA 경로의 구체 기본값 확보**. v1 (a) full freeze가 새 모달리티 조합에 불충분해 D19가 (d)로 이동할 경우, TAIL은 즉시 쓸 출발 설정을 제공합니다: **LoRA `rank r=8`, `scaling α=8`, 어텐션 $`W_Q`$/$`W_V`$ 투영에 적용**. 이는 우리 D19(d) trigger 발화 시 첫 실험 하이퍼파라미터의 강한 prior가 됩니다.
- **D20 → action-side adapter 선택의 망각 지표 근거**. v1 "action-side adapter(split head가 곧 adapter)" 의 정당성을 BWT=0 실증으로 보강합니다. D20 활성 시 평가 메트릭에 **BWT(이전 과제 성공률 변화)** 를 명시적으로 추가하는 편이 좋습니다.
- **D21 → Stage 3 레시피 키 채움**. deferred Stage 3 "LoRA / top-layer 제한 FT" 의 구체 레시피(AdamW, LR `1e-4`, 어댑터를 attention Q/V에 삽입, 묶음당 어댑터 1개)를 그대로 가져다 쓰면 됩니다.
- **D26 / 평가 — 망각·가소성 메트릭 도입**. 우리 falsifier가 contact-precision 위주인데, P4 보존 검증에는 TAIL식 **FWT/BWT + circle-back(이전 과제 재방문) 성능 드롭** 측정 프로토콜을 추가하면 "full-FT 대비 OOD/generalization 비퇴행"(D25 VLM-preservation 검증)이 비로소 정량화됩니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **새 모달리티(촉각)에서의 표현력 부족 — 가장 싼 점검**. TAIL은 동일 모달리티 안의 새 *과제*만 다룹니다. 우리 스택은 CLIP/π 백본이 사전학습하지 않은 **촉각(tactile)** 이라는 새 모달리티를 도입하므로, 동결 백본 + 저랭크 LoRA(r=8)가 진짜 새 모달리티를 충분히 표현하지 못할 위험이 큽니다. → 가장 싼 sanity check: 촉각 토큰을 추가한 소규모 과제에서 r=8 LoRA vs 더 큰 rank vs 부분 unfreeze의 성공률을 비교.
- **모델 규모 전이 불확실성**. 172M(CLIP-base+GPT-2)에서 통한 rank 8 / batch 18 설정이 π0(3.3B)급에서 그대로 유효한지 미지수. → 점검: π0 action-expert에 동일 rank 비율을 맞춘 소규모 LoRA로 LIBERO-유사 단순 과제 재현부터.
- **과제 식별/어댑터 스위칭 부재**. TAIL은 묶음당 어댑터 1개를 추론 시 명시적으로 골라 켭니다. 우리의 단일 배포 다지 정책에는 어댑터 라우터가 없으므로, "어떤 어댑터를 언제 켤지"가 그대로 옮겨오지 않습니다. → 점검: 단일 어댑터로 여러 과제를 동시에 담을 때의 간섭(D1 split과의 상호작용) 측정.
- **그리퍼→다지 갭**. LIBERO는 평행 그리퍼·비접촉집약 과제로, 접촉 정밀도(slip/pose stability) 신호가 없습니다. PEFT가 contact-precision까지 보존·향상하는지는 전혀 검증되지 않았습니다.

---

## 💡 컨텍스트 제안

- **P4 방법론 base 후보로 TAIL 추가 검토 (제안만)**. `context/MASTER.md` §8.4 P4 핀은 8개로 가득 차 있으나(하드캡), TAIL은 PEFT 통합 스타일 *비교* 레퍼런스로서 D19/D20/D21에 직접 쓰일 수 있는 방법론 base 후보입니다. P4에 별도 "Methodology base" 줄(P1/P3가 가진 것과 같은)을 두고 TAIL([arXiv:2310.05905])을 LoRA rank/α·삽입 위치 레시피 출처로 명기하는 것을 제안합니다.
- **D26 메트릭 확장 후보**. P4 보존 검증용으로 TAIL식 **FWT/BWT + circle-back drop** 을 D26 "VLM-preservation validated by generalization/OOD metric not regressing" 항목의 구체 측정 도구로 채택할지 검토 제안. (Decision 본문 수정은 사람 몫 — 여기서는 제안만.)
- 핀 교체는 제안하지 않습니다(TAIL은 2023년 작으로, VLM2VLA가 더 최신·대형 VLM 사례이므로 핀은 유지하고 TAIL은 방법론 base로 두는 편이 적절).

> 💡 base 매핑은 `/implement analysis/2310.05905/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
