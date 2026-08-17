# Paper Analysis — UniTac: A Unified Multimodal Model for Cross-Sensor Tactile Understanding and Generation

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | UniTac: A Unified Multimodal Model for Cross-Sensor Tactile Understanding and Generation |
| 저자 | Jiahang Tu, Fengyu Yang, Chenyang Ma, Xihang Yu, Ziyao Zeng, Shaokai Wu, Hanbin Zhao, Zhi Tao, Chao Zhang, Hui Qian, Alex Wong (Zhejiang University · Yale University · University of Oxford · MIT · Shanghai Jiaotong University · UNIX AI) |
| 링크 | [arXiv:2606.31451](https://arxiv.org/abs/2606.31451) |
| 발행일 / 버전 | 2026-06-30 · v1 (ECCV 2026 accepted) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-07-02 |
| 관련 Pillar | P2, P0, P3 |
| 태그 | tactile, dataset, flow-matching |

---

## 🧭 한 줄 요약 (TL;DR)

UniTac 은 촉각 데이터 취득을 "비접촉(센서 구성) → 접촉(물체 물성)" 2단계 전이로 모델링하고, 센서 수준 정보와 물체 수준 정보를 분리 인코딩·분리 감독하는 **최초의 촉각 통합 멀티모달 모델(UMM)** 입니다. 5개 공개 비주오택타일 데이터셋(약 400K 클립·1.6M 프레임)을 합쳐 학습해 촉각 이해(PHYSICLEAR-Test 평균 66.51)와 크로스-센서 촉각 생성(SSIM 0.836 / PSNR 19.93) 모두에서 SOTA 를 주장하며, 생성 데이터만으로 센서 간 도메인 갭(Digit→GelSight 50.00%→99.37%)을 메울 수 있음을 보입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 이해(understanding)와 생성(generation)을 한 모델에 통합하는 UMM 패러다임을 촉각 도메인으로 확장하는 것. 촉각에서는 물체 수준 의미(표면 기하·경도·거칠기)와 센서 수준 구성(조명·겔 변형·카메라 파라미터)이 **함께** 신호의 의미를 결정하므로, 두 수준을 동시에 모델링해야 센서를 넘나드는 이해·생성이 가능하다는 것이 출발점입니다.
- **기존 접근의 한계 (이해)** — 기존 touch-language 모델은 PHYSICLEAR(482개 터치 비디오)처럼 소규모 자체 수집 데이터로 학습됩니다. 공개된 대규모 촉각 데이터셋(합계 400K+ 클립, 1.6M 프레임)이 존재함에도 각각 고립되어 사용되어 촉각 의미 표현이 제한됩니다.
- **기존 접근의 한계 (생성)** — 기존 촉각 생성 연구(Touch2Touch 등)는 특정 센서 쌍 간 변환에 머물러, 다양한 센서 유형을 가로지르는 일반화 가능한 크로스-센서 합성을 다루지 못했습니다. 또한 대부분의 촉각 연구가 이해와 생성을 별개 문제로 취급합니다.
- **본 논문의 가설** — 촉각 취득은 카메라의 단일 노출과 달리 비접촉 단계(센서 구성 포착)와 접촉 단계(그 구성 아래에서의 물체 물성 기록)로 이루어지므로, 센서 수준·물체 수준의 **이중 표현(dual-level representation)** 을 명시적으로 분리해 학습하면 이해와 생성이 서로를 강화한다는 가설입니다.
- **왜 지금 중요한가** — 촉각 센서 하드웨어가 빠르게 진화하고 있어 새 센서마다 대규모 데이터 재수집이 필요한 상황입니다. 센서 구성을 조건으로 둔 생성 모델이 있으면 새 센서용 데이터를 합성해 적응 비용을 줄일 수 있습니다.

---

## 🧩 핵심 기여

- **촉각 도메인 최초의 UMM** — 센서 수준 구성과 물체 수준 의미를 공동 모델링해 촉각 이해와 생성을 단일 프레임워크로 통합한 UniTac 을 제안합니다.
- **Dual-Level Mixture Comprehension (DLMC)** — 물체 물성 서술(object property description)과 센서 식별(sensor identification)이라는 두 감독 태스크로 대규모 멀티센서 학습을 수행해, "물체에 따라 변하는 것"과 "센서에 따라 변하는 것"을 분리(disentangle)하도록 유도합니다.
- **2단계 정렬 생성 (Two-Stage Aligned Generation)** — MLLM 없이 병렬 학습 가능한 재구성(reconstruction) 단계와, MLLM 출력을 촉각 잠재공간에 정렬하는 센서 인지 정렬(sensor-aware alignment) 단계로 생성 학습을 분해합니다.
- **Sensor-Prior Sampling Strategy (SPSS)** — classifier-free guidance 의 무조건(unconditional) 분기를 센서 조건(비접촉 상태) 분기로 교체해, 비접촉→접촉 전이를 물리적으로 일관되게 시뮬레이션하는 샘플링 전략입니다.
- **실로봇 검증** — 실 로봇 플랫폼에서 촉각 이해(직물 선택 파지)와 생성 데이터의 실용성(크로스-센서 grasp 분류 증강)을 검증했습니다.

---

## 🔑 기술 키워드

- **Unified Multimodal Model (UMM)** — 이해(인식·추론)와 생성(합성)을 한 backbone 에서 함께 수행하는 모델 계열. 본 논문은 이 패러다임을 시각·텍스트 밖의 촉각으로 처음 확장합니다.
- **Visuo-tactile sensor** — 비주오택타일 센서. GelSight·Digit·Duragel 처럼 겔의 변형을 내장 카메라로 촬영해 촉각을 이미지 형태로 기록하는 센서 — 촉각 신호에 조명·마커 배치 같은 "센서 지문"이 함께 찍힙니다.
- **Dual-level representation** — 촉각 잠재 표현을 물체 수준 성분( $`\mathbf{Z}_{i}^{\text{obj}}`$ , 경도·거칠기)과 센서 수준 성분( $`\mathbf{Z}_{i}^{\text{sen}}`$ , 조명·겔 특성)으로 분해하는 이중 표현.
- **Sensor token** — 센서 유형마다 5개씩 배정되는 학습 가능한 토큰. 센서 고유 특성을 담는 "센서 신분증" 역할로, 생성 조건과 센서 식별 감독의 매개체입니다.
- **Touch encoder (AnyTouch)** — 대규모 멀티센서 촉각 비디오·이미지로 사전학습된 ViT-B/16 인코더. 768차원 잠재 토큰을 출력하며 UniTac 의 촉각 입력 관문입니다.
- **Object property description** — 접촉한 물체의 거칠기·경도·질감 3개 촉각 차원을 언어로 서술하게 하는 물체 수준 감독 태스크.
- **Sensor identification** — 어떤 촉각 센서로 찍었는지 답하게 하는 센서 수준 감독 태스크. 조명 색·마커 배치·겔 탄성 같은 센서 단서에 민감해지도록 강제합니다.
- **Rectified Flow Matching** — 플로우 매칭(flow matching)의 직선 경로 형태. 가우시안 노이즈와 목표 잠재를 잇는 선형 보간 경로의 상수 속도장을 회귀해, 노이즈 스케줄 없이 결정적 ODE 샘플링을 수행합니다.
- **Classifier-Free Guidance (CFG)** — 조건 분기와 무조건 분기의 속도장 차이를 스케일 $`s`$ 로 증폭하는 표준 조건부 샘플링 기법. SPSS 가 교체 대상으로 삼는 baseline 입니다.
- **Sensor-Prior Sampling Strategy (SPSS)** — CFG 의 무조건 분기를 "비접촉 센서 상태" 조건 분기로 바꿔, 샘플링 자체가 비접촉→접촉 전이를 따라가게 만드는 본 논문의 샘플링 전략.

---

## 🔬 방법론

### 직관

비주오택타일 센서가 찍는 촉각 이미지에는 항상 두 가지가 겹쳐 있습니다. 하나는 "무엇을 만졌는가"(물체의 경도·거칠기·질감)이고, 다른 하나는 "무엇으로 만졌는가"(센서의 조명 색, 겔 탄성, 마커 배치)입니다. 같은 물체라도 GelSight 로 만지면 마커 변위 패턴으로, Digit 으로 만지면 색 줄무늬 변화로 기록됩니다. 기존 모델들은 이 둘을 뭉뚱그려 배우기 때문에, 한 센서에서 배운 지식이 다른 센서로 옮겨가지 못하고, 생성 모델은 어떤 센서의 신호를 합성해야 하는지 알 길이 없었습니다.

UniTac 의 핵심 아이디어는 촉각 데이터가 만들어지는 물리 과정 자체를 모델 구조에 새기는 것입니다. 촉각 취득은 항상 "비접촉 상태"(센서만 보임 — 센서 구성 정보)에서 "접촉 상태"(센서 구성 위에 물체 물성이 얹힘)로 넘어가는 순서를 따릅니다. 그래서 잠재 표현을 센서 성분과 물체 성분으로 분해하고, 이해 학습에서는 두 성분을 각각 언어로 답하게 하는 두 태스크(물성 서술 / 센서 식별)로 분리를 강제하며, 생성 샘플링에서는 "센서만 조건" 분기에서 출발해 "센서+물체 조건" 방향으로 유도함으로써 비접촉→접촉 전이를 흉내 냅니다.

학습 파이프라인은 세 부분으로 나뉩니다. (1) 촉각 인코더의 잠재를 그대로 조건으로 받아 촉각 신호를 복원하는 디코더 재구성 학습 — MLLM 이 필요 없어 (2) 와 병렬로 돌릴 수 있습니다. (2) MLLM 을 두 이해 태스크로 미세조정하는 DLMC 학습. (3) MLLM 의 텍스트 의미 출력(쿼리 임베딩)을 촉각 잠재공간으로 사상하는 DiT projector 정렬 학습 — 이때 MLLM 출력에는 센서 단서가 없으므로 인코더의 sensor token 을 이어 붙여 센서 인지를 회복시킵니다. 결과적으로 "텍스트 설명 + 원하는 센서"를 주면 그 센서의 물리 특성에 맞는 촉각 이미지·비디오가 합성됩니다.

### 아키텍처

![Figure 3 — UniTac 아키텍처 개요](https://arxiv.org/html/2606.31451/x3.png)

> "Figure 3: Overview of the UniTac architecture. UniTac unifies tactile understanding and generation across sensors by jointly modeling sensor-level configurations and object-level semantics. The Touch Encoder extracts static and dynamic contact features, while the Multimodal Large Language Model (MLLM) integrates tactile and textual modalities for joint reasoning over object- and sensor-level information (Sec. 3.1). The Sensor-Aware DiT Projector and Touch Decoder perform two-stage tactile generation (Sec. 3.2), combining data reconstruction with sensor-aware alignment between MLLM embeddings and tactile representations. In addition, a sensor-prior-based sampling strategy (Sec. 3.3) models the transition from non-contact to contact, achieving realistic cross-sensor tactile synthesis." (§3)
(4개 모듈 — Touch Encoder / MLLM / Sensor-Aware DiT Projector / Touch Decoder — 이 이해와 생성 파이프라인에서 어떻게 이어지는지를 한 장으로 보여주는 본 논문의 설계 요약 그림입니다.)

본 논문의 설계 의도를 못 박는 앵커 문장은 서론에 있습니다.

> "Unlike visual cameras that capture a natural image in a single exposure, tactile data acquisition inherently involves two stages: a non-contact stage capturing sensor configuration and a contact stage recording object-level physical properties under that configuration" (§1)
(촉각은 "한 번의 노출"이 아니라 비접촉→접촉의 2단계 과정이라는 이 관찰이, 이중 표현·이중 감독·SPSS 샘플링까지 아키텍처 전체를 관통하는 제1원리입니다.)

**Touch Encoder** — AnyTouch 아키텍처(ViT-B/16)를 채택하며, 대규모 멀티센서 촉각 비디오·이미지로 사전학습되어 이질 센서 전반의 공간·시간 특징을 추출합니다.

> "In addition, the encoder incorporates a set of learnable sensor tokens, where each sensor type is associated with five tokens to encode sensor-specific characteristics. The encoder outputs 768-dimensional latent tokens containing object-level semantics and sensor-level configurations." (§0.A.1)
(센서 유형당 5개의 학습 토큰이 "센서 신분증"으로 작동합니다. 이 sensor token 이 뒤의 정렬 단계·SPSS 샘플링에서 센서 조건의 원천이 되므로, 인코더가 곧 크로스-센서 메커니즘의 심장입니다. 출력 잠재는 768차원입니다.)

**MLLM backbone** — Qwen-VL 2.5 기반 3B/7B 두 구성을 사용하며, Qwen-VL 의 visual projector 를 촉각 임베딩 어댑터(tactile embedding adaptor)로 교체해 촉각 잠재 토큰을 텍스트 시퀀스에 통합합니다. 3B 가 이미 이해 성능이 충분해 생성 backbone 으로는 3B 를 채택하고(전체 생성 모델 약 5B 파라미터), 이해 벤치마크에는 7B 도 보고합니다.

주어진 비주오택타일 비디오 $`V_{i}`$ 와 텍스트 $`T_{i}`$ 에 대해 사전학습 촉각 인코더가 토큰열 $`\mathbf{Z}_{i}=E_{\text{touch}}(V_{i})\in\mathbb{R}^{L_{v}\times d}`$ 를 만들고, 이를 특수 마커로 텍스트 스트림에 접합합니다.

> "We then splice these tokens into the MLLM text stream using two special markers `<T_VID>` and `</T_VID>`" (§3.1)
(촉각 토큰을 언어 시퀀스 안의 한 구간으로 끼워 넣는 token-splice 방식입니다 — 별도의 cross-attention 융합 모듈이 아니라, LLM 의 self-attention 이 촉각·텍스트를 함께 처리하게 두는 UMM 표준 설계입니다.)

**Sensor-Aware DiT Projector** — NextDiT(24-layer diffusion transformer)로, MLLM 의 의미 임베딩과 인코더의 sensor prior 를 결합해 텍스트 표현을 촉각 잠재공간으로 연속 정렬하는 조건부 속도장을 학습합니다.

**Touch Decoder** — 이미지 생성은 SANA 디퓨전 아키텍처로 512 × 512 촉각 이미지를, 비디오 생성은 디코더를 Wan v2.2 로 교체해 448 × 448 해상도 13프레임 시퀀스를 합성합니다. 센서 인지 조건화 메커니즘은 두 경우 동일하게 유지됩니다.

### 학습 목표 / 손실 — Dual-Level Mixture Comprehension (§3.1)

이해 학습의 입력 시퀀스는 $`X_{i}=[\texttt{<T\_VID>},\ \mathbf{Z}_{i},\ \texttt{</T\_VID>},\ \Pi_{i},\ T_{i}]`$ 형태이며, $`\Pi_{i}`$ 는 두 이해 목표(물성 서술 / 센서 식별) 중 하나를 지정하는 지시 프롬프트입니다. 표준 next-token prediction 으로 최적화합니다 (식 1):

$$\mathcal{L}=-\sum_{t=2+L_{v}+|\Pi_{i}|}^{|X_{i}|-1}\log p_{\theta}(x_{i,t+1}\mid x_{i,\leq t})$$

시작 인덱스가 $`2+L_{v}+|\Pi_{i}|`$ 인 것은 마커·촉각 토큰·프롬프트 구간을 건너뛰고 **정답 텍스트 토큰만** 예측 대상으로 삼는다는 뜻입니다 (Algorithm 1 의 NextTokenLoss 도 동일하게 텍스트 시작 인덱스부터 누적합니다).

**물체 수준 감독** — Octopi 를 따라 거칠기·경도·질감 3개 촉각 차원으로 물체를 서술합니다. 프롬프트는 "Describe the physical properties of the contacted surface", 기대 출력은 "The surface feels soft and slightly rough, with small bumpiness." 형태입니다 (§0.A.2).

**센서 수준 감독** — 프롬프트 "Identify which tactile sensor captured this video" 에 "Captured by a GelSight Mini sensor." 로 답하게 합니다 (§0.A.2).

> "The same next-token prediction loss applies, driving the MLLM to learn sensor-related variations such as lighting, gel elasticity, and imaging resolution." (§3.1)
(같은 손실 형태이지만 감독 목표가 다릅니다 — 조명·겔 탄성·해상도처럼 물체와 무관하게 센서에 따라 변하는 변인에 민감해지도록 강제해, 표현이 센서 축을 명시적으로 갖게 만듭니다.)

두 태스크는 가중합으로 통합됩니다 (식 2):

$$\mathcal{L}_{\text{DLMC}}=\mathcal{L}_{\text{prop}}+\lambda_{\text{sen}}\,\mathcal{L}_{\text{sen}}$$

여기서 $`\lambda_{\text{sen}}>0`$ 이 두 목표의 균형을 잡으며, 본 실험 기본값은 $`\lambda_{\text{sen}}=0.1`$ 입니다 (§0.A.2).

> "Through this dual-level supervision, UniTac learns to disentangle what changes with the object from what changes with the sensor, leading to more accurate tactile understanding." (§3.1)
(이중 감독의 목적을 요약하는 문장입니다 — "물체에 따라 변하는 것"과 "센서에 따라 변하는 것"의 분리가 곧 크로스-센서 일반화의 기반이라는 주장입니다.)

### 학습 목표 / 손실 — Two-Stage Aligned Generation (§3.2)

**Stage I: Reconstruction.** MLLM 과 독립적으로 촉각 도메인 안에서 생성 prior 를 학습하는 단계입니다.

> "the latent representation $`\mathbf{Z}_{i}`$ extracted from the touch encoder inherently contains two types of information" (§3.2)
(인코더 잠재가 애초에 두 성분의 합성이라는 전제 — $`\mathbf{Z}_{i}=[\mathbf{Z}_{i}^{\text{obj}},\,\mathbf{Z}_{i}^{\text{sen}}]`$ 로 표기됩니다.)

> "where $`\mathbf{Z}_{i}^{\text{obj}}`$ encodes object-level semantics such as hardness and roughness, and $`\mathbf{Z}_{i}^{\text{sen}}`$ represents sensor-level configurations including illumination and gel properties." (§3.2)
(이 분해가 이후 SPSS 의 두 조건 분기 — 센서만 / 센서+물체 — 를 가능하게 하는 구조적 토대입니다.)

이 잠재 토큰을 touch decoder $`D_{\text{touch}}`$ 에 조건으로 넣어 촉각 신호를 재구성합니다. Algorithm 2 기준으로 비접촉 프레임 $`V_{i}^{\text{sen}}`$ 과 접촉 프레임 $`V_{i}^{\text{sen+obj}}`$ 를 각각 인코딩하고, Bernoulli( $`p_{\text{drop}}`$ ) 확률로 조건을 센서-단독 잠재로 떨어뜨려( $`F_{i}^{\text{cond}}\leftarrow Z_{i}^{\text{sen}}`$ ) 학습합니다 — 이 조건 드롭이 있어야 추론 시 SPSS 의 "센서만 조건" 분기가 유효합니다.

> "As this stage does not involve the MLLM backbone, it can be trained in parallel with the Dual-Level Mixture Comprehension task to improve training efficiency." (§3.2)
(재구성 학습이 MLLM 과 분리되어 있어 DLMC 와 병렬로 돌릴 수 있다는 학습 효율 설계입니다.)

**Stage II: Sensor-Aware Alignment.** 촉각 서술 $`T_{i}`$ 와 $`N`$ 개 touch query 로 MLLM 출력 쿼리 임베딩 $`\mathbf{\hat{Q}}_{i}=E_{\text{MLLM}}(T_{i},\mathbf{Q}_{i})\in\mathbb{R}^{N\times d}`$ 를 얻습니다.

> "which primarily encode object-level semantics consistent with the described physical attributes of the surface, but lack explicit sensor cues" (§3.2)
(텍스트에서 나온 임베딩에는 물체 의미만 있고 센서 단서가 없다는 문제 제기입니다 — 촉각 서술문에 "어떤 센서로 찍었는지"는 보통 적혀 있지 않기 때문입니다.)

그래서 사전학습 인코더의 sensor token $`\mathbf{S}`$ 를 이어 붙여 조건 표현 $`\mathbf{F}_{i}=[\mathbf{\hat{Q}}_{i};\mathbf{S}]`$ 를 만들고 (Algorithm 2 에서는 $`\mathrm{MLP}_{\text{sen}}`$ 으로 사영한 $`S^{\prime}`$ 사용), DiT projector 가 가우시안 prior 를 촉각 잠재 $`\mathbf{Z}_{i}`$ 로 옮기는 조건부 속도장 $`v_{\theta}(\cdot|t,\mathbf{F}_{i})`$ 를 학습합니다. rectified flow 정식화에 따라 노이즈 $`\mathbf{z}\sim\mathcal{N}(0,I)`$ 와 목표 잠재를 잇는 선형 보간 경로를 정의하고 (식 3):

$$\mathbf{x}_{t}=(1-t)\,\mathbf{z}+t\,\mathbf{Z}_{i},\qquad t\in[0,1]$$

그 목표 속도는 상수 벡터입니다 (식 4):

$$\mathbf{u}_{t}=\frac{d\mathbf{x}_{t}}{dt}=\mathbf{Z}_{i}-\mathbf{z}.$$

projector 는 조건부 rectified flow matching 손실을 최소화합니다 (식 5):

$$\mathcal{L}_{\text{align}}^{\text{RF}}=\mathbb{E}_{t\sim\mathcal{U}(0,1),\mathbf{z}\sim\mathcal{N}(0,I),\,\mathbf{Z}_{i}}\!\bigl\|v_{\theta}(\mathbf{x}_{t}|t,\mathbf{F}_{i})-(\mathbf{Z}_{i}-\mathbf{z})\bigr\|_{2}^{2}.$$

> "This alignment bridges the MLLM semantic output and the touch encoder representations, enabling the model to generate tactile signals that are both semantically faithful and sensor-consistent." (§3.2)
(정렬 단계의 존재 이유 — 의미 충실성(텍스트)과 센서 일관성(sensor token)을 동시에 만족하는 잠재를 만드는 다리 역할입니다.)

### Sensor-Prior Sampling Strategy (§3.3)

표준 CFG 는 무조건 분기와 조건 분기의 차이를 증폭합니다 (식 6):

$$\hat{v}_{\theta}(\mathbf{x}_{t},c)=v_{\theta}(\mathbf{x}_{t}|t,\varnothing)+s\big[v_{\theta}(\mathbf{x}_{t}|t,c)-v_{\theta}(\mathbf{x}_{t}|t,\varnothing)\big]$$

> "However, in tactile generation, the unconditional prior $`v_{\theta}(\mathbf{x}_{t}|t,\varnothing)`$ does not accurately represent the non-contact initialization, as tactile signals are inherently dependent on the sensor configuration." (§3.3)
(촉각에는 "조건 없는 상태"라는 것이 물리적으로 존재하지 않는다는 지적입니다 — 접촉이 없어도 센서 자체의 조명·겔 상태는 항상 찍히므로, 무조건 분기는 실제 초기 상태(비접촉 센서 상태)를 대변하지 못합니다.)

그래서 무조건 분기를 비접촉 상태를 명시적으로 인코딩한 센서 조건 prior 로 교체합니다 (식 7):

$$\hat{v}_{\theta}(\mathbf{x}_{t}|t,\;\mathbf{Z}_{i}^{\text{obj}},\mathbf{Z}_{i}^{\text{sen}})=v_{\theta}(\mathbf{x}_{t}|t,\;\mathbf{Z}_{i}^{\text{sen}})+s\big[v_{\theta}(\mathbf{x}_{t}|t,\;\mathbf{Z}_{i}^{\text{obj}},\mathbf{Z}_{i}^{\text{sen}})-v_{\theta}(\mathbf{x}_{t}|t,\;\mathbf{Z}_{i}^{\text{sen}})\big]$$

> "This design enforces a physically consistent transition, where the first item respects the sensor configuration and the second item incorporates contact semantics." (§3.3)
(첫 항(센서 prior 분기)이 비접촉 과정 — 센서 구성 존중 — 을, 둘째 항이 같은 센서 상태 아래에서의 접촉 의미 주입을 맡습니다. 샘플링 궤적 자체가 비접촉→접촉 전이를 재연하는 셈입니다.)

추론 파이프라인(Algorithm 3–4)은 2단 직렬입니다: (1) DiT projector 가 텍스트+쿼리에서 정렬 잠재 $`\tilde{Z}_{i}^{\text{obj+sen}}`$ 를 표준 flow 적분으로 생성하고, (2) touch decoder 가 비접촉 이미지 $`V_{i}^{\text{sen}}`$ 를 인코딩한 $`Z_{i}^{\text{sen}}`$ 을 센서 prior 분기로 삼아 SPSS 유도( $`s=1.5`$ )로 최종 촉각 신호를 합성합니다. 각 생성 궤적은 50 rectified-flow 스텝을 사용합니다 (§0.A.3).

### 학습 셋업

- **데이터** — AnyTouch 가 조직한 5개 공개 데이터셋: Touch and Go, Tacquad, TVL, SSVTP, PHYSICLEAR. SSVTP 를 제외한 모두가 촉각 비디오-텍스트 쌍을 포함합니다.

> "We preprocess and unify them into a consistent format comprising approximately 400K video clips and 1.6M frames with aligned text annotations." (§4.1)
(고립되어 쓰이던 공개 데이터셋들을 하나의 학습 코퍼스로 통합한 것 자체가 이해 성능 주장의 절반을 차지하는 재료입니다.)

> "We filter the contact frames with tactile deformations by calculating the difference between each tactile image and the corresponding background frame in these datasets." (§4.1)
(배경(비접촉) 프레임과의 차분으로 접촉 프레임을 선별합니다 — 비접촉/접촉 구분이 데이터 전처리 수준에서부터 파이프라인에 들어와 있습니다.)

- **3단계 학습** — 재구성(이미지: 약 20 epochs · batch 512 · ZeRO-1 · lr 1e-4, 5000-step 워밍업 후 cosine 으로 1e-5 감쇠 / 비디오: batch 8 · gradient accumulation 16 · gradient clipping max-norm 1 · ZeRO-2)과 DLMC 가 병렬로 진행되고, 두 단계 수렴 후 NextDiT projector 정렬(100 epochs · batch 512 · lr 1e-4, 동일 워밍업)을 학습합니다 (§0.A.2).
- **하드웨어** —

> "All stages are trained under bf16 mixed precision. Experiments are conducted on a cluster equipped with 8 × NVIDIA A800 (80 GB) GPUs, managed by Accelerate for distributed optimization." (§0.A.2)
(8×A800 80GB — 대학 연구실 수준에서 재현 가능한 규모입니다.)

---

## 📊 실험 설정과 결과

**평가 프로토콜** (§4.1) — 이해는 PHYSICLEAR-Test 벤치마크에서 단순 지각(경도·거칠기·질감 분류)과 복합 추론 — Property Comparison (PC), Property-Object Matching (POM), Property Superlative Selection (PSS) — 을 측정합니다. 생성은 GVST·TextToucher 를 따라 60K 생성 촉각 이미지를 ground truth 와 비교해 SSIM·PSNR 로 평가합니다.

### 촉각 이해 (Table 1)

| Type | Model | Method | PC ↑ | POM ↑ | PSS ↑ | Hardness ↑ | Roughness ↑ | Texture ↑ | Average ↑ |
|---|---|---|---|---|---|---|---|---|---|
| Und. Only | GPT-4o | AR | 30.87 | 22.62 | 38.05 | 31.37 | 30.48 | 36.51 | 31.65 |
| | Qwen2.5-VL-7B | AR | 21.47 | 19.92 | 23.05 | 25.73 | 33.33 | 26.62 | 25.01 |
| | Gemini-2.5-Pro-Exp | AR | 26.71 | 23.47 | 25.06 | 29.19 | 28.44 | 32.18 | 27.50 |
| | LLaVA-OneVision-7B | AR | 35.42 | 29.11 | 28.44 | 33.33 | 32.18 | 36.51 | 32.49 |
| | Octopi-7B | AR | 45.50 | 22.22 | 48.00 | 64.10 | 73.92 | 87.17 | 57.31 |
| Und. and Gen. | TokenFlow-7B | AR | 38.05 | 29.48 | 32.56 | 47.68 | 38.70 | 48.31 | 39.13 |
| | JanusPro-7B | AR + Diff | 30.18 | 26.71 | 38.05 | 41.63 | 35.82 | 45.37 | 36.29 |
| | BLIP3o-3B | AR + Diff | 26.71 | 21.47 | 32.18 | 36.51 | 32.18 | 48.00 | 32.84 |
| | UniTac-3B (Ours) | AR + Diff | 54.97 | 42.13 | 58.90 | 51.28 | 76.92 | 79.48 | 60.61 |
| | UniTac-7B (Ours) | AR + Diff | 57.30 | 64.61 | 59.22 | 61.53 | 74.35 | 82.05 | 66.51 |

> "UniTac-7B achieves the highest overall score of 66.51, surpassing all previous models." (§4.2, Table 1)
(범용 VLM(GPT-4o 31.65, Gemini 27.50)이 촉각 추론에서 사실상 무작위 수준에 머무는 반면, 촉각 특화 학습을 한 UniTac-7B 가 평균 66.51 로 최고치입니다.)

> "On the three reasoning-oriented tasks, i.e., PC, POM, and PSS, UniTac-7B improves over the strongest UMM baseline Octopi-7B by 11.80, 42.39, and 11.22 points, respectively." (§4.2)
(이득이 균일하지 않고 추론형 태스크(PC/POM/PSS)에 집중되어 있습니다 — 특히 POM +42.39점. 반면 단순 분류(Hardness 61.53 vs Octopi 64.10, Texture 82.05 vs 87.17)에서는 Octopi-7B 가 오히려 앞서는 항목도 있어, UniTac 의 강점은 지각이 아니라 촉각 관측을 물리·의미 개념으로 접지(grounding)한 뒤의 추론에 있습니다.)

![Figure 4 — 센서별 물체 물성 서술 정성 결과](https://arxiv.org/html/2606.31451/x4.png)

> "Figure 4: Object property description of tactile videos across various tactile sensors. UniTac generates object-aware tactile descriptions that align with physical properties of the contacted materials." (§4.2)
(학습 태스크인 물성 서술이 다양한 센서 입력에서 물리적으로 그럴듯한 서술을 내는지를 보여주는 정성 결과로, CD 의 단단하고 매끈한 표면과 봉제 인형의 부드럽고 보풀한 질감을 구별합니다.)

### 촉각 생성 (Table 2)

| Type | Model | Digit SSIM ↑ | Digit PSNR ↑ | Gelsight SSIM ↑ | Gelsight PSNR ↑ | Gelsight Mini SSIM ↑ | Gelsight Mini PSNR ↑ | Duragel SSIM ↑ | Duragel PSNR ↑ | Avg SSIM ↑ | Avg PSNR ↑ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Gen. Only | GVST | 0.841 | 18.72 | 0.655 | 14.58 | 0.883 | 18.90 | 0.429 | 14.98 | 0.762 | 18.43 |
| | UniTouch | 0.859 | 18.17 | 0.636 | 14.18 | 0.851 | 18.63 | 0.440 | 14.31 | 0.769 | 17.71 |
| | PixArt-α | 0.877 | 18.10 | 0.641 | 14.09 | 0.869 | 18.77 | 0.446 | 14.36 | 0.785 | 17.74 |
| | TextToucher | 0.901 | 20.90 | 0.662 | 15.42 | 0.896 | 20.38 | 0.473 | 16.36 | 0.816 | 18.65 |
| Und. and Gen. | TokenFlow-7B | 0.834 | 17.47 | 0.628 | 14.04 | 0.758 | 15.67 | 0.431 | 12.72 | 0.726 | 15.35 |
| | JanusPro-7B | 0.854 | 20.18 | 0.653 | 15.34 | 0.894 | 19.67 | 0.464 | 17.73 | 0.753 | 18.46 |
| | BLIP3o-7B | 0.821 | 16.30 | 0.618 | 13.46 | 0.746 | 14.74 | 0.405 | 10.92 | 0.713 | 13.66 |
| | UniTac | 0.915 | 21.26 | 0.683 | 16.28 | 0.946 | 24.56 | 0.472 | 18.44 | 0.836 | 19.93 |

> "UniTac achieves the highest average performance of 0.836 SSIM and 19.93 PSNR, surpassing all state-of-the-art generative and unified models." (§4.3, Table 2)
(생성 전용 모델(TextToucher 0.816/18.65)까지 포함해 평균 최고치입니다. 다만 표를 뜯어 보면 Duragel SSIM 은 TextToucher(0.473)가 UniTac(0.472)을 근소하게 앞서는 등, 우위가 모든 셀에서 성립하는 것은 아닙니다.)

> "We also observe that all models perform relatively lower on Duragel due to unstable acquisition conditions and significant variation in sensor calibration and gel state." (§4.3)
(Duragel 은 수집 조건이 불안정해 촉각 외형과 물성 사이의 패턴 자체가 흔들리는 센서로, 모든 모델의 성능 하한을 만듭니다 — 센서 데이터 품질이 이 접근의 상한을 정한다는 신호입니다.)

![Figure 6 — 센서별 촉각 이미지 생성 정성 비교](https://arxiv.org/html/2606.31451/x6.png)

> "Figure 6: Qualitative comparison of tactile image generation across various tactile sensors. UniTac consistently generates realistic and physically coherent tactile images across diverse sensors and configurations." (§4.3)
(같은 센서 유형이라도 개체가 다른 Digit-1/Digit-2 의 구성 차이까지 구별해 생성하는 반면, 다른 UMM 은 센서 상태를 잘못 그리거나 공간 충실도를 잃는다는 주장의 시각적 근거입니다.)

**비디오 생성** — 디코더만 교체하고 조건화 메커니즘은 유지한 채 시간적으로 일관된 촉각 비디오를 합성합니다.

> "we extend UniTac to tactile video generation by replacing the touch decoder with Wan v2.2" (§4.3)
(backbone·조건화를 건드리지 않고 디코더 교체만으로 이미지→비디오로 확장된다는 것은 sensor-aware 조건화 설계의 모듈성 증거입니다. 접촉 시작과 압력 전파, dot-grid 변위의 시간 일관성이 유지된다고 보고합니다.)

### Ablation (Table 3 + 부록)

| Component | PHYSICLEAR | SSIM | PSNR |
|---|---|---|---|
| UniTac | 60.61 | 0.836 | 19.93 |
| w/o Sensor Identification | 57.38 | 0.822 | 19.91 |
| w/o Dual-Level Comprehension | 26.52 | 0.758 | 18.14 |
| w/o DiT Projector | 60.61 | 0.794 | 19.25 |
| w/o Sensor-Prior Sampling | 60.61 | 0.817 | 19.49 |

> "Removing the Sensor Identification objective causes a clear drop on PHYSICLEAR (from 60.61 to 57.38), indicating that explicitly modeling sensor-level configurations substantially enhances the UMM’s ability to interpret tactile data across various tactile sensors." (§4.4, Table 3)
(각 행이 분리하는 것 — sensor identification 제거는 이해 -3.23점(생성은 거의 불변)으로 "센서 축 감독이 이해에 기여"함을, Dual-Level Comprehension 전체 제거는 26.52 로 붕괴(표준 Qwen-VL 수준)해 "촉각 이해가 생성의 의미 prior 이기도 함"(SSIM 0.836→0.758)을 보입니다. 반대로 DiT Projector·SPSS 제거는 이해에 영향이 없고(60.61 유지) 생성 충실도만 깎아, 이해 경로와 생성 경로가 설계대로 분리되어 있음을 확인합니다.)

**λ_sen 스윕** (§0.B.2, Table B) — $`\lambda_{\text{sen}}`$ ∈ {0.01, 0.05, 0.1, 0.5, 1} 에서 PHYSICLEAR 58.27 / 59.36 / **60.61** / 59.84 / 58.12, SSIM 0.818 / 0.826 / **0.836** / 0.829 / 0.817 로 0.1 이 최적입니다. 센서 감독이 너무 약하면(0.01) 센서 축 분리가 안 되고, 너무 강하면(1) 물성 추론이 밀려나는 양방향 트레이드오프입니다.

**쿼리 수** (§0.B.4, Table D) — 16→64 쿼리로 SSIM 0.820→0.836 개선, 128/256 은 이득이 미미( $`\leq 0.03`$ PSNR)해 기본값 64 를 채택합니다.

**SPSS vs CFG** (§0.B.5, Table E) —

> "Vanilla CFG achieves its best performance at $`s=1.5`$, with 0.817 SSIM and 19.49 PSNR. Under the same guidance scale, SPSS improves the results to 0.836 SSIM and 19.93 PSNR." (§0.B.5, Table E)
(guidance scale 을 통제한 비교입니다 — SPSS 의 이득이 스케일 조정이 아니라 무조건 분기를 센서 prior 로 교체한 데서 온다는 분리 증거. SPSS 자체도 $`s`$ ∈ {1.0, 1.5, 2.0, 3.0, 5.0, 7.5} 스윕에서 1.5 가 최적(0.836)이고 과대 유도(7.5)는 0.791 로 퇴화합니다.)

### 실로봇 검증 (§4.5, §0.B.1)

![Figure 8 — 직물 비교 파지 실험](https://arxiv.org/html/2606.31451/x8.png)

> "Figure 8: The robot compares two visually similar fabrics through the Property Comparison task, identifies the smoother one as more suitable for baby skin contact. Tactile differences between the two materials are magnified for clarity." (§4.5)
(시각적으로 거의 같은 두 직물에서 촉각으로만 구별 가능한 부드러움 차이를 Property Comparison 태스크로 판별해 파지 대상을 고르는, 이해 능력의 실환경 시연입니다. 플랫폼은 Tracer 모바일 베이스 + 듀얼 암 + end-effector 장착 GelSight Mini, ROS Noetic 기반입니다 (§0.A.4).)

**언어 유도 직물 선택·파지** (Table 4) — 세 정책 변형 비교. VLA(RGB-only), VTLA-real(실시간 GelSight 관측 사용), VTLA-pred(추론 시 실촉각 없이 RGB/state 에서 촉각 표현을 예측해 조건화).

> "All settings are implemented based on $`\pi_{0.5}`$" (§0.B.1)
(정책 backbone 은 π0.5 입니다 — UniTac 자체가 정책이 아니라, 촉각 표현이 정책에 주는 이득을 재는 실험 설계입니다.)

| Method | Selection Success ↑ | Grasping Success ↑ | Overall Success ↑ |
|---|---|---|---|
| VLA | 11/20 (55%) | 6/20 (30%) | 4/20 (20%) |
| VTLA-real | 20/20 (100%) | 19/20 (95%) | 19/20 (95%) |
| VTLA-pred | 18/20 (90%) | 16/20 (80%) | 16/20 (80%) |

> "VTLA-predict, while not using real-time tactile input during inference, still substantially outperforms VLA, suggesting that predicted tactile representations preserve useful physical cues for contact-aware manipulation." (§4.5)
(주목할 결과입니다 — 촉각 센서 없이도 "예측된 촉각 잠재"를 조건으로 쓰는 것만으로 20%→80% 로 뜁니다. 촉각 정보의 이득 대부분이 표현 수준에서 이미 확보된다는 뜻입니다.)

**미학습 크기 컵 변형 파지** (§0.B.1, Table A) — 작은 컵으로 학습하고 더 큰 미학습 컵에서 목표 변형 1 cm 압축을 평가합니다.

| Method | Lift Success ↑ | Target Deform. Success ↑ | Overall Success ↑ |
|---|---|---|---|
| VLA | 18/20 (90%) | 0/20 (0%) | 0/20 (0%) |
| VTLA-real | 20/20 (100%) | 20/20 (100%) | 20/20 (100%) |
| VTLA-pred | 19/20 (95%) | 18/20 (90%) | 18/20 (90%) |

(RGB-only 정책은 들어올리기는 90% 성공하지만 목표 변형 제어는 0% — 시각은 "어디를 잡을지"는 배워도 접촉 상태·힘 제어에는 직접 접근하지 못한다는 분리 증거입니다. 촉각 예측만 조건화해도 90% 로 회복됩니다.)

**생성 데이터의 크로스-센서 전이 효용** (Table 5, Table F) —

| Data | Digit Grasp(%) | Gelsight Grasp(%) |
|---|---|---|
| Digit | 98.89 | 50.00 |
| Digit+UniTac-Gelsight | 99.07 | 99.37 |

> "By augmenting the training set with UniTac-generated GelSight samples, the GelSight accuracy improves to 99.37%, while Digit performance remains stable (99.07%)." (§4.5, Table 5)
(Digit 만으로 학습한 grasp 분류기는 GelSight 에서 50%(우연 수준)로 무너지는데, UniTac 생성 GelSight 샘플 증강만으로 99.37% 까지 복구됩니다 — 실데이터 재수집 없는 센서 적응이라는 실용 주장의 핵심 수치입니다.)

부록 Table F 는 이 결과가 Digit→GelSight 방향에 국한되지 않음을 보입니다: GelSight→Duragel 에서 target 53.11%→94.48%(실데이터 상한 96.20%), Duragel→Digit 에서 52.46%→95.75%(상한 97.42%). 생성 증강이 실데이터 상한에 1–2%p 차이까지 접근하되, source 정확도는 소폭 하락합니다(98.84→96.12, 97.89→96.02).

---

## ⚖️ 한계

- **픽셀 충실도 지표와 물리 정합성의 간극** — 생성 평가가 SSIM/PSNR 에 의존합니다. 이 지표는 외형 유사도를 재는 것이지 접촉 기하·힘 분포의 물리적 올바름을 보증하지 않으며, 생성 데이터의 downstream 검증도 이진에 가까운 grasp 분류라 판별 난이도가 낮습니다. 슬립 검출·힘 회귀처럼 물리 정보를 실제로 소비하는 태스크에서의 효용은 미검증입니다.
- **"크로스-센서"의 실질 범위** — 센서 일반화의 메커니즘이 센서 유형별 학습 sensor token(5개/유형)과 target 센서의 비접촉 참조 이미지에 의존합니다. 즉 학습에 포함된 센서들 사이의 전이이지, 한 번도 본 적 없는 센서로의 zero-shot 일반화가 아닙니다. 새 센서는 결국 sensor token 을 학습할 만큼의 데이터가 필요한데, 그 양이 얼마인지는 논문이 답하지 않습니다.
- **저품질 센서에서의 붕괴** — 저자들이 직접 인정하듯 Duragel 처럼 수집 조건이 불안정한 센서에서는 모든 모델(UniTac 포함)의 성능이 크게 낮습니다(SSIM 0.472 vs GelSight Mini 0.946). 재구성 결과도 Duragel 은 불안정합니다 (§0.C.1). 촉각 외형-물성 매핑의 분산이 큰 센서에서는 이중 표현 분리 자체가 흔들린다는 신호로, 접근의 상한이 센서 데이터 품질에 묶여 있습니다.
- **이해의 수준이 비디오-수준 의미 서술** — 이해 태스크가 클립 단위의 물성 서술·비교(거칠기/경도/질감)로, 시간 해상도가 필요한 접촉 동역학(슬립 onset, 힘 미세 변화)의 추정과는 결이 다릅니다. 촉각 "이해" SOTA 라는 주장이 조작 제어에 필요한 촉각 상태 추정 능력을 의미하지는 않습니다.
- **실로봇 평가의 규모** — 실로봇 검증이 태스크 2종(직물 선택, 컵 변형 파지) × 20 rollout 규모이고, VTLA 변형의 구현 상세(촉각 예측기 구조, 학습 데이터 규모)가 부록 수준으로만 기술됩니다. 통계적 신뢰구간 없이 20회 시행 비율만 보고됩니다.
- **벤치마크 크기** — 이해 평가의 중심인 PHYSICLEAR-Test 는 482개 터치 비디오 코퍼스 계열의 소규모 벤치마크로, 66.51 vs 57.31 급 격차의 일반화 가능성은 더 큰 평가셋에서 재확인이 필요합니다. λ_sen 스윕 해설(§0.B.2)이 0.5 를 "a small $`\lambda_{\text{sen}}`$" 으로 지칭하는 등 본문 서술에 사소한 혼선도 있습니다(표 기준 최적은 0.1).

---

## ♻️ 재현성

- **코드** — 공개 저장소 링크 없음. 부록 서두에 "we submit the source code in the “UniTac” folder" 라고 밝혀 심사용 supplementary 로만 제출된 상태입니다 (§0.A). GitHub/프로젝트 페이지가 확인되지 않아 현시점 제3자 재현은 구성 요소 재조립에 의존합니다.
- **데이터** — 학습 코퍼스는 전부 공개 데이터셋(Touch and Go, Tacquad, TVL, SSVTP, PHYSICLEAR — AnyTouch 조직)이고, 벤치마크(PHYSICLEAR-Test)도 공개되어 있어 데이터 접근성은 좋습니다.
- **구성 요소** — touch encoder(AnyTouch), MLLM(Qwen-VL 2.5 3B/7B), 이미지 디코더(SANA), 비디오 디코더(Wan v2.2), projector(NextDiT/Lumina) 모두 공개 가중치·아키텍처 기반이라 재구축 난이도는 중간입니다. 다만 tactile embedding adaptor, $`p_{\text{drop}}`$ , MLLM 미세조정 범위 등 세부는 미명시입니다.
- **하드웨어** — 8 × NVIDIA A800 (80 GB), bf16, Accelerate — 규모는 재현 가능한 수준입니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P2(구조적 다중모달 관측 융합) / D11(proprio-tactile-force 토큰 구성) — 가장 강한 접점** — D11 의 v1 은 "swappable sensor head + common token format"(Sharpa lock-in 금지)입니다. UniTac 의 sensor token(유형당 5개) + 공용 768-d 잠재 형식 + sensor identification 감독은 정확히 이 "센서 교체 가능성"을 표현 수준에서 달성하는 메커니즘의 실증입니다 — 센서 축을 명시적 토큰·감독으로 분리하면 물체 수준 표현이 센서를 넘어 공유된다는 증거(Table 3: sensor id 제거 시 -3.23점)를 제공합니다.
- **P2 / D10(concat 을 넘는 이질 모달리티 융합) — 긴장** — UniTac 의 촉각-언어 융합은 `<T_VID>` 마커로 토큰을 텍스트 스트림에 접합하는 token-splice, 즉 D10 이 넘어서려는 flat concat 계열입니다. UniTac 은 융합 구조가 아니라 감독 설계(DLMC)로 성능을 얻으므로, D10 의 "구조적 cross-attention 융합" 논지를 지지하지도 반박하지도 않습니다 — 융합 대상이 정책 관측이 아닌 언어 추론이라 비교 축이 다릅니다.
- **P0(VLA 데이터셋·벤치마크) / D25(tactile/force/torque 데이터 스카우팅)** — 두 방향의 접점: (1) 고립된 5개 공개 촉각 데이터셋을 400K 클립·1.6M 프레임의 단일 코퍼스로 통합한 전례 — D25 가 "희소성을 1급 갭"으로 취급하는 촉각 코퍼스의 실질 규모 상한을 보여줍니다. (2) 생성 증강으로 센서 갭을 메우는 결과(Table 5/F: 50%→99.37%) — 촉각 데이터 희소성의 부분 대체재로서 "생성"이라는 새 축을 엽니다.
- **P3(Hand-level System0) / D15(System0 입력 모달리티)·D18(System0 sim2real) — 간접** — System0 의 촉각 입력 자체는 ms-급 저수준 신호라 UniTac 의 비디오-수준 이해와 직접 연결되지 않습니다. 다만 MASTER §4.2 가 미결로 둔 visuotactile sim 렌더링(Sharpa Deform Map sim-side rendering, protocol TBD)에 대해, 센서 조건부 촉각 생성이 "학습된 촉각 시뮬레이터"라는 대안 경로가 될 수 있습니다 — D18 의 DR 파이프라인에 생성 촉각 데이터를 섞는 형태.
- **P5(World Model) — 비접점 명시** — UniTac 의 생성은 텍스트·센서 조건부 합성이지 액션 조건부 forward dynamics 가 아니므로 D28–D32 를 건드리지 않습니다. 단, 부록의 VTLA-pred(RGB/state 에서 촉각 표현을 예측해 정책을 조건화, 20%→80%)는 "예측된 접촉 표현이 정책에 유용하다"는 점에서 P5 의 잠재 예측 철학과 공명하는 방증이지만, 논문 내 위치는 부록 실험 1건입니다.
- **Identity 관점** — "per-finger proprio-tactile binding" 을 요구하는 우리 Identity 와 달리 UniTac 은 단일 센서 뷰의 전역 표현입니다. 지지점은 "촉각을 1급 모달리티로 격상 + 센서 하드웨어 lock-in 회피"라는 방향성이고, 긴장점은 손가락별 공간 귀속(attribution)이 전혀 없다는 것입니다.

---

## ✨ 핀 논문 대비 델타

- **vs ViTacFormer (P2 핀, arXiv:2506.15953)** — ViTacFormer 는 정책 내부의 cross-attention 비주오택타일 융합(제어를 위한 융합)이고, UniTac 은 정책 밖의 촉각 표현·생성 UMM(이해·합성을 위한 통합)입니다. 진정 새로운 것: 센서 수준/물체 수준의 명시적 분리 감독과, 그 분리를 그대로 생성 조건으로 재사용하는 이해↔생성 왕복 구조.
- **vs Sparsh (P2 methodology base, arXiv:2410.24090)** — Sparsh 는 자기지도 촉각 표현(SSL foundation model)으로 언어·생성이 없습니다. UniTac 의 델타는 (1) 언어 접지(물성 서술·비교 추론), (2) 크로스-센서 생성, (3) sensor token 이라는 조작 가능한 센서 축입니다. 반면 표현 학습 자체는 AnyTouch 사전학습을 그대로 가져오므로 인코더 수준 기여는 없습니다.
- **vs RH20T (P0 핀, arXiv:2307.00595)** — RH20T 는 실수집 F/T 코퍼스(데이터 공급의 정공법)입니다. UniTac 은 "촉각 데이터를 더 모으는" 대신 "이미 있는 데이터를 통합하고 부족한 센서 도메인은 생성으로 채우는" 보완 축을 제시합니다 — D25 의 희소성 문제에 대한 수집 외 대안.

---

## ⚙️ 의사결정 함의

- **D11 tactile head 초기화 후보** — 우리 tactile encoder 를 백지에서 학습하는 대신 AnyTouch-계열 멀티센서 사전학습 가중치(ViT-B/16, 768-d)로 초기화하는 옵션이 실증 근거를 얻습니다. 구체적으로: D11 의 "hardware-specific CNN on Deform Map" 앞단은 유지하되, 출력을 768-d common token format 에 맞추고 사전학습 잠재공간과 정렬하는 구성.
- **sensor-identification 보조 손실 추가** — 우리 촉각 인코더 학습에 `L_total = L_task + λ_sen * L_sensor_id` 형태의 센서 식별 보조 head 를 추가하는 것은 비용이 거의 없는 레버입니다( $`\lambda_{\text{sen}}=0.1`$ 이 검증된 시작점). Sharpa → xhand → 자체 핸드로 센서가 바뀔 우리 로드맵에서, 센서 축을 표현에서 명시적으로 분리해 두는 것이 D11 의 "no Sharpa lock-in" 을 학습 신호 수준에서 구현합니다.
- **센서 교체 시 데이터 재수집 예산** — 핸드/센서 교체 시점에 "이전 센서 데이터 + 생성 증강"으로 태스크 헤드를 재학습하는 경로를 기본 후보로 추가할 수 있습니다. 채택 판정 메트릭은 UniTac 의 프로토콜 그대로: target-센서 분류/검출 정확도가 실데이터 상한 대비 몇 %p 이내로 복구되는가 (Table F 기준 1–2%p).
- **VTLA-pred 형 predicted-tactile conditioning** — 촉각 센서가 없거나 신뢰도가 낮은 구간에서 RGB/proprio 로부터 촉각 잠재를 예측해 Hand expert 를 조건화하는 보조 경로(20%→80% 근거)를 D11 의 aux head(contact-binary/slip-binary) 확장 후보로 기록할 가치가 있습니다 — 단 π0.5 기반 20-rollout 근거이므로 채택이 아닌 추적 수준.

---

## ⚠️ 먼저 검증할 실패 모드

- **Deform Map 도메인 갭 (가장 싼 체크 먼저)** — UniTac/AnyTouch 의 센서 집합은 전부 광학 겔 센서(RGB-이미지형)입니다. Sharpa Deform Map 은 ~320×240 변형 맵으로 신호 통계가 다릅니다. 체크: 공개 AnyTouch 인코더에 Deform Map 프레임을 넣어 선형 프로브(재질 분류)와 sensor-token 유사도 분포를 확인 — GPU 몇 시간 규모. 여기서 무너지면 이 논문의 우리 스택 관련성은 "설계 패턴 참고"로 격하됩니다.
- **미학습 센서 적응 비용** — "크로스-센서"가 학습된 센서 간 전이임을 감안하면, 새 센서(자체 핸드)에 필요한 최소 데이터량이 관건입니다. 체크: 공개 데이터셋에서 한 센서를 통째로 held-out 하고 소량(수백 프레임)으로 sensor token 만 미세조정했을 때 생성/식별 품질이 복구되는지.
- **생성 데이터의 물리 정합성** — grasp 이진 분류(Table 5)는 외형 통계만 맞아도 통과할 수 있는 약한 검증입니다. 체크: 생성 촉각 데이터로 슬립 검출 또는 접촉력 회귀(F/T 라벨이 있는 RH20T-류 소규모 셋)를 학습해 실데이터 학습 대비 격차 측정 — 여기서 격차가 크면 D18 sim2real 경로(학습된 촉각 시뮬레이터)로는 부적합.
- **실시간성** — 이해 모델이 3B/7B, 생성이 50 flow 스텝입니다. 우리 제어 루프(Deform Map 30Hz, System0 는 그 이상)에는 직접 못 들어갑니다. 체크: 표현만 떼어 쓰는 구성(인코더 + sensor token, MLLM 제외)의 지연 측정 — UniTac 의 가치가 온라인이 아닌 오프라인(데이터 생성·라벨링·평가)에 있음을 전제로 파이프라인을 설계해야 합니다.
- **per-finger 귀속 부재** — 단일 센서 뷰 전역 표현이라 D12(topology-aware encoding) 요구인 손가락별 귀속과 결이 다릅니다. 체크: 10 fingertip + 2 palm 멀티뷰 구성에서 sensor token 방식이 "손가락 위치 token" 으로 일반화되는지는 완전 미검증 — 소규모 사내 파일럿 전에는 가정으로만 취급.

---

## 💡 컨텍스트 제안

- **P2 §5 methodology base 에 UniTac 추가 검토** — D11 의 "swappable sensor head + common token format" 에 대한 최초의 대규모 실증(sensor token + 분리 감독 + 크로스-센서 생성)으로, 핀 교체 없이 methodology base 행 추가를 제안합니다. 같은 맥락에서 UniTac 의 인코더 원천인 AnyTouch ([arXiv:2502.12191](https://arxiv.org/abs/2502.12191)) 를 D11 사전학습 후보로 함께 기록할 가치가 있습니다.
- **P0 D25 각주 제안** — D25 가 "촉각 코퍼스 희소성 = 1급 갭" 으로 두는 전제에, "센서 조건부 생성 증강이 부분 대체재가 될 수 있음 (UniTac Table 5/F: 실데이터 상한 -1–2%p)" 을 추적 항목으로 덧붙이는 것을 제안합니다 — Decision 변경이 아닌 증거 각주 수준.
- **MASTER §4.2 visuotactile sim 항목** — Sharpa Deform Map sim 렌더링 protocol TBD 에 대한 대안 경로로 "학습된 촉각 생성 모델" 트랙(UniTac-류)을 후보 목록에 추가할 것을 제안합니다. 채택 전제 조건은 위 ⚠️ 의 Deform Map 도메인 갭 체크 통과입니다.

---
