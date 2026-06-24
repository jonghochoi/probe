# Paper Analysis — Motion-Focused Latent Action Enables Cross-Embodiment VLA Training from Human EgoVideos

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Motion-Focused Latent Action Enables Cross-Embodiment VLA Training from Human EgoVideos |
| 저자 | Runze Xu, Yiluo Zhang, Jian Wang, Yu Wang, Jincheng Yu (Acknowledgement 기준 Tsinghua University 계열) |
| 링크 | [arXiv:2606.18955](https://arxiv.org/abs/2606.18955) |
| 발행일 / 버전 | 2026-06-17 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-24 |
| 관련 Pillar | P4, P0, P1, P2 |
| 태그 | vla-arch, egocentric-data, flow-matching |

<!-- 코드/프로젝트 페이지: 본문·초록·arXiv HTML 어디에도 GitHub/HuggingFace/Website 링크가
     없어 링크 행에는 arXiv 만 둡니다(없는 URL 날조 금지). 분류 cs.CV(주) / cs.RO. -->

---

## 🧭 한 줄 요약 (TL;DR)

라벨 없는 1인칭 사람 조작 영상에서 **물리 마스크로 동작과 배경을 분리한 Hybrid Disentangled VQ-VAE** 로 cross-embodiment 잠재 행동 코드북을 뽑고, 이것으로 VLM 을 사전학습한 뒤, **의도-지각 분리(intent-perception decoupling)** 로 다운스트림 적응 시 ~50개 궤적만으로 대규모 라벨 데이터로 학습한 SOTA VLA 에 필적하는 성능을 냅니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 일반화 VLA 학습은 정밀한 액션 라벨이 붙은 대규모 로봇 데이터(OXE, AgiBot)에 의존하는데, 수집 비용이 과도하고 로봇 플랫폼 간 운동학·물리 차이로 도메인 갭이 큽니다.
- **기존 접근의 한계** — 사람 영상을 쓰려는 EgoMimic·MotionTrans·H-RDT 류는 여전히 AR/VR 하드웨어로 캡처한 **명시적 손 동작 라벨**에 의존해, 라벨이 없는 인터넷 스케일 영상 대부분을 활용하지 못합니다.
- **잠재 행동의 얽힘 문제** — LAPA·IGOR 식 VQ-VAE 잠재 행동 코드북은 프레임 전이를 압축하지만 배경 변화·카메라 이동 같은 **task-무관 동역학**까지 함께 담아 사전학습 정책 품질을 떨어뜨립니다. UniVLA 는 언어로 task-centric 움직임을 유도하지만 사람 영상의 다양성 앞에서 정밀 분리가 어렵습니다.
- **본 논문의 가설** — 사람 영상을 "시각 배경"이 아니라 "행동 의도의 자연적 운반체"로 보고, 로봇 운동학에서 분리된 **embodiment-agnostic 모션 프리미티브** 코드북으로 VLM 을 먼저 사전학습하면, 실제 로봇 환경 노출 이전에 행동 의도 표현을 획득해 소수 궤적으로 적응이 가능합니다.
- **왜 지금 중요한가** — egocentric 사람 영상은 풍부·다양하지만 라벨이 없어 미활용 상태이고, 라벨 의존성을 끊는 것이 VLA 스케일 병목의 핵심이기 때문입니다.

---

## 🧩 핵심 기여

- **라벨 없는 사람 영상 사전학습 패러다임** — AR/VR 손 포즈 라벨 없이 1인칭 영상에서 cross-embodiment 행동 prior 를 학습하고, 다운스트림 ~50개 궤적만으로 "사람 행동 의도 → 로봇 실행"으로 전이합니다.
- **Hybrid Disentangled VQ-VAE** — 물리 마스크(SAM2 손 / RoboEngine 로봇 분할)를 inductive bias 로 써서 동작 동역학과 환경 배경을 별도의 이산 잠재 공간으로 분리(dual-path VQ)함으로써, 잠재 행동 공간이 순수 모션 패턴에 집중하도록 강제합니다.
- **의도-지각 분리(intent-perception decoupling) 적응 전략** — VLM 이 행동 의도를 예측하고, 별도의 **frozen DINOv2** 가 상태별 지각 특징을 액션 전문가에게 공급해 action hallucination(실시간 피드백 무시)을 줄입니다.
- **cross-embodiment 일관성 검증** — robot↔robot, human↔dual-arm robot 전이에서 LIBERO·RoboTwin 2.0·실로봇 평가 + CKA 정렬 분석으로 학습 표현의 높은 임베디먼트 간 일관성을 보입니다.

---

## 🔑 기술 키워드

- **Latent Action Representation** — 라벨 없는 영상에서 연속 프레임 전이를 이산 코드로 압축한 "행동의 알파벳" — 로봇 액션 라벨 없이도 행동 의도를 표현하는 중간 표현입니다.
- **Hybrid Disentangled VQ-VAE** — 동작용 코드북과 배경용 코드북을 따로 둔 이중경로 벡터 양자화 오토인코더 — 한 영상의 변화를 "무엇이 움직였나(동작)"와 "어디서(배경)"로 갈라 담습니다.
- **Mask-guided Reconstruction** — 전경(손/로봇 팔) 마스크 영역은 동작 코드로, 배경 영역은 배경 코드로만 복원하도록 손실을 비대칭 배분해 의미 분리를 강제하는 학습 기법입니다.
- **Cross-Embodiment Action Codebook** — 사람 손과 로봇 팔이 같은 행동을 하면 같은 토큰을 받도록 설계된 임베디먼트 무관 이산 코드 집합입니다.
- **Intent-Perception Decoupling** — "무엇을 하려는가(VLM 의도)"와 "지금 무엇이 보이는가(frozen 지각 인코더)"를 분리해 액션 전문가에 따로 주입하는 전략 — 모델이 실시간 관측을 무시하는 환각을 억제합니다.
- **Action Hallucination** — 정책이 실제 관측(예: 닫힌 용기)을 보지 않고 사전 의도대로만 행동해 실패하는 현상입니다.
- **Flow Matching Action Expert** — 노이즈에서 실제 액션으로의 속도장 $`v_\theta`$ 을 회귀해 멀티모달 액션 분포를 생성하는 디코더입니다.
- **DINOv2** — 자가지도로 학습된 frozen 시각 인코더(ViT-B/14-reg) — 여기서는 의도와 분리된 "객관적 물리 상태" 특징 공급원으로 사용됩니다.
- **CKA (Centered Kernel Alignment)** — 서로 다른 데이터셋/임베디먼트의 표현이 얼마나 정렬되어 있는지 0–1 로 재는 표현 유사도 지표입니다.

---

## 🔬 방법론

### 직관

이 논문의 출발점은 단순합니다. 로봇 액션 라벨은 비싸고 플랫폼마다 다르지만, "사람이 손으로 무언가를 조작하는 1인칭 영상"은 인터넷에 넘쳐납니다. 문제는 이 영상에 "어떤 관절을 얼마나 움직였다"는 액션 라벨이 없다는 점입니다. 그래서 저자들은 라벨 대신 **영상의 연속된 두 프레임 사이의 변화 자체를 행동의 단위로 보고, 그 변화를 이산 코드(토큰)로 압축**합니다. 이 코드가 곧 "행동 의도의 알파벳"이고, 사람 손이든 로봇 팔이든 같은 동작이면 같은 코드를 받도록 만드는 것이 목표입니다.

핵심 난점은 영상의 변화가 동작만 담지 않는다는 것입니다. 카메라가 흔들리거나 배경이 바뀌어도 프레임은 변하고, 순진한 VQ-VAE 는 이 잡음까지 코드에 욱여넣어 정책 품질을 떨어뜨립니다. 저자들은 여기에 **물리 마스크**라는 외부 신호를 끌어옵니다. SAM2(사람 손)나 RoboEngine(로봇 팔)으로 "움직이는 주체"를 분할해, 동작 코드는 전경 영역만 복원하도록, 배경 코드는 배경 영역만 복원하도록 손실을 갈라 줍니다. 결과적으로 동작 코드북과 배경 코드북이 의미적으로 분리되고, 행동 코드는 순수 모션에 집중하게 됩니다.

코드북이 만들어지면 두 번째 단계에서 **VLM 을 "관측+지시문 → 잠재 행동 토큰열"을 예측하도록 사전학습**합니다. 코드북을 VLM 어휘에 넣고(UniVLA 방식) 토큰을 자기회귀로 맞히게 하면, VLM 은 실제 로봇을 한 번도 보지 않고도 "이 장면에서 무엇을 하려 해야 하는가"라는 행동 의도를 배웁니다.

마지막 적응 단계의 통찰이 **의도-지각 분리**입니다. VLM 의 마지막 층 은닉상태를 모아 만든 의도 임베딩 $`f_{act}`$ 만으로 액션을 내면, 모델은 "닫힌 용기에 물건을 넣으려는" 식으로 실시간 관측을 무시하는 환각에 빠집니다. 그래서 의도는 VLM 이, **지금의 객관적 물리 상태는 별도의 frozen DINOv2** 가 따로 공급하도록 역할을 나눕니다. 이 둘과 proprioception 을 합쳐 flow matching 액션 전문가가 실제 제어를 생성합니다. 덕분에 50개 안팎의 로봇 궤적만으로도 적응이 됩니다.

### 아키텍처

![Figure 1 — Method overview](https://arxiv.org/html/2606.18955/x1.png)

> "Figure 1: Method overview. We propose a human-video-driven framework for training vision–language–action models." (§III-A)
(전체 파이프라인 — VQ-VAE 코드북 추출 → VLM 사전학습 → 소수 로봇 궤적으로 VLM+액션 전문가 공동 미세조정 — 의 세 단계를 시각화합니다.)

전체 프레임워크는 **3단계**입니다 (§III-A).

- **Stage 1 — Hybrid Disentangled VQ-VAE** — egocentric 영상에서 cross-embodiment 이산 행동 코드북 추출.
- **Stage 2 — VLM 사전학습** — 코드를 supervision 으로, 관측·언어 지시문 → 일반 행동 의도 매핑 학습.
- **Stage 3 — 다운스트림 적응** — 목표 로봇에서 소수 시연으로 미세조정, DINOv2 시각 피드백과 의도를 결합해 flow matching 으로 제어 명령 생성.

![Figure 2 — Hybrid Disentangled VQ-VAE](https://arxiv.org/html/2606.18955/x2.png)

> "Figure 2: Hybrid Disentangled VQ-VAE. The VQ-VAE model decomposes short-term visual changes into discrete action and background latent spaces via a dual-path vector quantization bottleneck." (§III-B)
(이중경로 양자화 병목으로 단기 시각 변화를 동작/배경 이산 공간으로 분해하고, mask-guided 디코더가 의미 분리를 강제하는 구조를 보여줍니다.)

**입력과 잠재 공간.** 인접 프레임열 $`V \in \mathbb{R}^{T \times C \times H \times W}`$ 가 주어지면 모델은 행동 공간 $`\mathbf{Z}_{act}`$ 와 배경 공간 $`\mathbf{Z}_{bg}`$ 의 두 독립 이산 잠재 공간을 학습합니다. 구현에서는 **고정 1초 간격의 인접 프레임 쌍**을 써서 물리적 동작에 의한 단기 시각 변화는 잡고 장기 장면 드리프트는 무시합니다.

- **인코더 (§III-B 1)** — frozen DINOv2 가 고차원 공간 특징 $`F \in \mathbb{R}^{T \times N \times D}`$ 를 뽑고, spatial-temporal transformer 가 프레임 간 변화를 모델링합니다. disentanglement 를 위해 두 학습 가능 query 집합 $`\mathbf{Q}_{act}`$, $`\mathbf{Q}_{bg}`$ 를 시각 패치와 concat 해 처리한 뒤 행동/배경 잠재로 분리 투영합니다.
- **이중경로 VQ 병목 (§III-B 2)** — 행동·배경 각각 독립 VQ 레이어. 행동 코드북 **크기 16** 으로 행동 query 특징을 양자화해 $`\mathbf{z}_{q}^{act}`$ 를, 배경 코드북 **크기 16** 으로 $`\mathbf{z}_{q}^{bg}`$ 를 만듭니다.

  > "Each pair of frames is represented by 4 discrete latent action tokens, which together encode the visual changes from manipulator interaction." (§III-B 2)
  (프레임 쌍 하나당 $`K = 4`$ 개의 이산 행동 토큰으로 표현됩니다 — 이 4-토큰이 뒤이은 VLM 예측 단위가 됩니다.)

- **Mask-guided 복원 (§III-B 3)** — 공유 디코더에 **세 가지 입력 조합**을 넣는 ablation-식 복원: (1) full — $`\mathbf{z}_{q}^{act}`$ + $`\mathbf{z}_{q}^{bg}`$ + 초기 프레임 특징 → 타깃 특징맵 전체 복원; (2) action ablation — $`\mathbf{z}_{q}^{act}`$ + 초기 프레임 → 모션 영향 영역만 복원; (3) background ablation — $`\mathbf{z}_{q}^{bg}`$ → 환경만 복원.

  > "the action path calculates reconstruction error only for foreground regions, such as the robot arm, while the background path is supervised by the background regions." (§III-B 3)
  (외부 마스크가 비대칭 supervision 을 제공해, 같은 공유 파라미터 공간 안에서 코드 타입별로 복원 영역을 강제 분리합니다. 사람 영상은 SAM2 로 손 전경 마스크를, 로봇 영상은 RoboEngine 으로 로봇 마스크를 생성합니다.)

### 학습 목표 / 손실

**Stage 1 — VQ-VAE 손실 (§III-B 4).** 복원·벡터양자화·commitment 의 가중합입니다 (식 1):

$$L_{\text{total}}=\lambda_{\text{recon}}L_{\text{recon}}+\lambda_{\text{vq}}L_{\text{vq}}+\lambda_{\text{commit}}L_{\text{commit}}$$

$`L_{recon}`$ 은 mask-guided 전경·배경·전역 특징 오차를 포함하고, $`L_{vq}`$ 는 인코더 출력과 코드북 항목의 유클리드 거리를 최소화하며, $`L_{commit}`$ 은 인코더 출력의 잦은 요동을 막아 학습을 안정화합니다. (각 $`\lambda`$ 값은 원문 미명시.)

**Stage 2 — VLM 사전학습 (§III-C).** 코드북을 VLM 어휘에 통합(UniVLA 방식)하고, 이미지 쌍 $`(I_{t}, I_{t+T})`$ 와 지시문 $`L`$ 에 대해 frozen VQ-VAE 인코더로 얻은 타깃 토큰열 $`\mathbf{z}_{act}=\{z^{(1)},\dots,z^{(K)}\}`$ ($`K=4`$) 를 자기회귀로 예측합니다.

> "The pre-training objective is to minimize the negative log-likelihood:" (§III-C)
(라벨 없는 사람 영상으로 행동 의도 예측만 학습하므로, 다운스트림 액션 전문가와의 공동 학습은 이 단계에서 불가능합니다 — 그래서 NLL 토큰 예측만 둡니다, 식 2.)

$$L_{pre}=-\mathbb{E}_{(L,I_{t},I_{t+T})\sim\mathcal{D}}\left[\sum_{k=1}^{K}\log P_{\theta}\left(z^{(k)}\mid z^{(<k)},I_{t},L\right)\right]$$

backbone 은 Prismatic VLM(Karamcheti et al., [12])으로, 관련 baseline 과 공정 비교를 위함입니다.

**Stage 3 — 다운스트림 적응 (§III-D).** transformer 기반 flow matching 디코더를 액션 전문가로 두고 **scratch 학습**합니다. VLM 이 생성한 행동 토큰의 마지막 층 은닉상태를 모아 의도 임베딩 $`f_{act}`$ 로 쓰고, VLM 은 **LoRA** 로 미세조정합니다. 멀티모달 컨텍스트는 의도·관측·proprioception 의 concat 입니다 (식 3):

$$F_{full}=\text{Concat}(f_{act},f_{obs},f_{proprio})$$

여기서 $`f_{obs}=DINO(I_{main})`$ 입니다. 액션 전문가 블록 내부에서 self-attention 이 액션 청크 내 시간 의존성을, cross-attention 이 멀티모달 컨텍스트를 액션열 예측에 통합합니다.

> "The model generates actions by predicting a vector field $`v_{\theta}`$ through an MLP head, with the flow matching loss:" (§III-D)
(MLP head 가 속도장 $`v_\theta`$ 를 예측하고, ground-truth 액션 $`a`$ 와 가우시안 노이즈 $`\epsilon`$ 사이의 직선 경로를 회귀합니다, 식 4.)

$$L_{flow}=\|v_{\theta}(x_{t},t,F_{full})-(a-\epsilon)\|^{2}$$

$`x_{t}`$ 는 flow step $`t`$ 의 노이즈 섞인 액션입니다. 추가로 사전학습과 동일한 cross-entropy $`L_{intent}`$ 로 잠재 행동 토큰 예측을 supervise 해, VLM 이 다운스트림 시연의 구체적 의도를 정확히 포착하게 합니다.

> "The final optimization objective is a joint loss that balances the intention prediction and the action execution:" (§III-D)
(의도 예측과 액션 실행을 가중치 $`\lambda_{intent}`$ 로 균형 잡는 결합 손실입니다, 식 5.)

$$L_{total}=L_{flow}+\lambda_{intent}L_{intent}$$

**의도-지각 분리의 근거 (§III-D).** VLM 시각 임베딩 대신 DINOv2 특징을 쓰는 이유가 이 논문의 핵심 설계 의도입니다.

> "We use DINO v2 features as the visual representation instead of VLM visual embeddings to decouple action intent from the observed physical state. Directly using VLM embeddings for control often leads to action hallucination, where the model ignores real-time feedback." (§III-D)
(VLM 임베딩은 의도와 지각이 뒤섞여 있어, 제어에 그대로 쓰면 "닫힌 용기에 물건을 넣으려는" 식으로 실시간 피드백을 무시합니다. 의도(VLM)와 객관 지각(frozen DINOv2)을 분리하면 이런 실패가 줄고 더 grounded 한 실행이 됩니다.)

### 학습 셋업

- **데이터 (사전학습)** — robot→robot 실험은 BridgeV2(WindowX) 3인칭 영상만, human→robot 실험은 EgoDex 영상만 사용(둘 다 액션 라벨 없음). 마스크는 BridgeV2 는 RoboEngine, EgoDex 는 SAM2.
- **입력 해상도 / 인코더** — 입력 이미지 `224×224`, frozen 인코더는 `DINOv2-ViT-B/14-reg`.
- **적응 학습** — LIBERO: task 당 50 궤적(3인칭 뷰만), Spatial/Object/Goal 은 30k step·batch 128, Long 은 40k step. RoboTwin 2.0: task 당 50 궤적, batch 32·30k step, 자기-가림 완화를 위해 wrist 뷰 추가 → $`f_{obs}=DINO([I_{main},I_{wrist}])`$. 실로봇: task 당 50 궤적, batch 32·20k step.
- **VLM 어휘 / 코드** — 행동 코드북 16, 프레임 쌍당 4 토큰, 1초 프레임 간격.

---

## 📊 실험 설정과 결과

평가는 세 축입니다 (§IV): (1) robot→robot (단일팔 영상 → 다른 임베디먼트), (2) human→dual-arm robot (라벨 없는 사람 영상 → 양팔 로봇), (3) 잠재 행동 표현 공간의 cross-embodiment 일관성 정량 분석.

### LIBERO — 단일팔 robot→robot (§IV-A, Table I)

BridgeV2(WindowX) 3인칭 영상으로만 VQ-VAE+VLM 사전학습, LIBERO(Franka)는 적응 단계에서만 노출. 4개 suite × 10 task, task 당 50 궤적(3인칭만), 각 task 20회 평가.

| Method | Spatial | Object | Goal | Long | Average |
|---|---|---|---|---|---|
| LAPA | 73.8 | 74.6 | 58.8 | 55.4 | 65.7 |
| Diffusion Policy | 78.3 | 92.5 | 68.3 | 50.5 | 72.4 |
| OpenVLA | 84.7 | 88.4 | 79.2 | 53.7 | 76.5 |
| SpatialVLA | 88.2 | 89.9 | 78.6 | 55.5 | 78.1 |
| pi0 * | 88.0 | 88.5 | 87.0 | 61.0 | 81.1 |
| pi0-fast * | 96.4 | 96.8 | 88.6 | 60.2 | 85.5 |
| villa-x * | 97.5 | 97.0 | 91.5 | 74.5 | 90.1 |
| UniVLA-Bridge | 90.0 | 86.0 | 90.5 | 86.0 | 88.1 |
| Ours w/o DINO | 91.0 | 81.0 | 88.5 | 81.0 | 85.4 |
| **Ours** | **95.5** | **94.0** | **93.5** | **84.0** | **91.8** |

`*` 표시는 post-training 시 wrist-mounted 카메라 관측을 쓴 방법입니다.

> "In contrast, our method excels in Goal and Long-horizon tasks, outperforming villa-x by 2.0% and 9.5% respectively." (§IV-A, Table I)
(villa-x·pi0-fast 가 Spatial/Object 에서 근소 우위지만 이는 wrist 카메라+명시적 액션 라벨 덕입니다. 반대로 본 방법은 Goal·Long 에서 앞서, 추출한 잠재 의도가 다단계 시퀀스의 high-level planning 에 더 강함을 시사합니다.)

핵심 ablation 은 **Ours vs Ours w/o DINO** (85.4 → 91.8). DINO 대신 VLM 시각 임베딩을 쓰면 평균 6.4%p 하락 — 의도-지각 분리의 효과를 robot→robot 에서 확인합니다. 특히 Object 에서 81.0→94.0 로 격차가 큽니다.

### RoboTwin 2.0 — human→dual-arm robot (§IV-B, Table II)

EgoDex 사람 영상만으로 사전학습, RoboTwin 2.0 Aloha-Agilex 양팔(clean mode)로 50 task 중 10개 선정 적응.

| Task | RDT | pi0 | ACT | DP | UniVLA | Ours w/o DINO | Ours (Freeze) | Ours |
|---|---|---|---|---|---|---|---|---|
| Adjust bottle | 81 | 90 | 97 | 97 | 87 | 87 | 83 | 97 |
| Grab roller | 74 | 96 | 94 | 98 | 80 | 87 | 50 | 90 |
| Place phone stand | 15 | 35 | 2 | 13 | 40 | 30 | 8 | 28 |
| Pick dual bottles | 42 | 57 | 31 | 24 | 58 | 58 | 42 | 52 |
| Place empty cup | 56 | 37 | 61 | 37 | 46 | 51 | 48 | 63 |
| Move can pot | 25 | 58 | 22 | 39 | 60 | 52 | 52 | 65 |
| Handover mic | 90 | 98 | 85 | 53 | 82 | 86 | 84 | 92 |
| Open laptop | 59 | 85 | 56 | 49 | 81 | 81 | 74 | 87 |
| Place object basket | 33 | 16 | 15 | 15 | 18 | 16 | 11 | 25 |
| Place burger fries | 50 | 80 | 49 | 72 | 84 | 80 | 72 | 78 |
| **Average** | 52.5 | 65.2 | 51.2 | 49.7 | 63.6 | 62.8 | 52.4 | **67.7** |

> "our method achieves performance comparable to state-of-the-art VLAs despite relying solely on unlabeled human videos for pre-training." (§IV-B, Table II)
(라벨 없는 사람 영상만으로 사전학습했는데도 대규모 액션-supervision VLA(pi0 65.2, RDT 52.5)와 동등 이상(67.7)입니다.)

ablation 두 가지의 읽기:
- **Ours w/o DINO (62.8)** — DINO 특징을 VLM 임베딩으로 바꾸면 4.9%p 하락. 의도-상태 분리가 실시간 피드백 기반 의도 조정에 기여함을 재확인.
- **Ours (Freeze) (52.4)** — 적응 시 VLM 을 동결하면 큰 폭 하락(특히 Grab roller 90→50)하나, 여전히 RDT(52.5)에 근접. 즉 VLM 의 잠재 행동 임베딩이 다운스트림에 결정적이지만, **사전학습만으로도 사람→로봇 의도가 직접 전이될 만큼** 효과적임을 보입니다.

### 실로봇 양팔 (§IV-B, Fig. 3)

ARX X5 leader → ARX R5 follower 텔레오퍼레이션, wrist fisheye 2 + 1인칭 RGB(20Hz), ARX R5 에 60Hz 배포. 3 task — 병 접시 위 놓기(단일팔), 전원 코드 뽑기(양팔 강체), 수건 접기(양팔 변형체) — 각 50 실궤적·batch 32·20k step. UniVLA 대비 의도 전이 우위. "Place Bottle" 만 낮은데, 병의 높은 무게중심으로 minor contact 에 쓰러지면 회복 불가(비가역 실패)이기 때문입니다.

### 잠재 행동 정렬 — CKA 분석 (§IV-C, Fig. 4)

domain subspace elimination 기반 정렬 분석: BridgeV2 로 코드북 생성 → BridgeV2(WindowX)+FurnitureBench(Franka) 혼합으로 VLM 사전학습 → 토큰별 은닉 임베딩 추출(각 20,000 쌍 샘플). logistic regression + PCA 로 domain 부분공간을 반복 제거한 뒤 CKA 측정(token centroid bootstrap 50회).

> "UniVLA exhibits lower consistency with a mean CKA of 0.8659, whereas our Motion-Focused Latent Action achieves a significantly higher alignment with a mean CKA of 0.9139." (§IV-C, Fig. 4(b))
(domain bias 제거 후에도 본 방법의 cross-embodiment 표현 정렬이 UniVLA 보다 유의하게 높아, 환경·임베디먼트 차이의 domain bias 를 더 잘 억제함을 정량 확인합니다.)

### 잠재 행동 시각화 (§IV-D, Fig. 5)

![Figure 5 — Latent Action Visualization](https://arxiv.org/html/2606.18955/x7.png)

> "Figure 5: Latent Action Visualization. Image pairs from different datasets with same latent codes. Despite different morphologies, robot arms and human hands are assigned the same action tokens." (§IV-D)
(BridgeV2+EgoDex 혼합 학습 후, 형태가 전혀 다른 로봇 팔과 사람 손이 같은 행동 패턴에서 같은 토큰을 받습니다 — 코드북이 임베디먼트를 가로질러 일관된 의미 구조를 가짐을 정성적으로 보입니다.)

---

## ⚖️ 한계

- **(저자 명시) 이산 코드북의 표현 용량 부족** — "its representation capacity remains insufficient for fine-grained manipulation tasks requiring high-precision control" (§V). 코드북 16·프레임당 4 토큰이라는 거친 양자화는 high-level 의도에는 충분하나 정밀 접촉 제어를 표현하기엔 너무 성깁니다. 미세 손가락 동작을 16개 슬롯으로 양자화하면 서로 다른 정밀 동작이 같은 코드로 붕괴할 수 있습니다.
- **물리 마스크 의존성** — 동작/배경 분리가 SAM2(손)·RoboEngine(로봇) 분할 품질에 전적으로 의존합니다. 가림·클러터·다물체 상호작용에서 마스크가 무너지면 동작 코드에 배경 잡음이 다시 섞여 disentanglement 가설 자체가 깨집니다. 또한 마스크가 "움직이는 손/팔"만 잡으므로 손에 쥔 **도구·물체의 동작**은 전경 정의에서 빠질 위험이 있습니다.
- **flat concat 멀티모달 융합** — 식 3의 $`F_{full}`$ 은 의도·관측·proprioception 의 단순 concat 입니다. 모달리티 간 구조적 결합(cross-attention/asymmetric)이 없어 접촉 의미의 모달 간 정렬은 액션 전문가의 attention 에 암묵적으로 위임됩니다.
- **적응 시 VLM unfreeze(LoRA)** — 다운스트림에서 VLM 을 LoRA 로 갱신합니다. 데이터 효율은 좋지만, 사전학습으로 얻은 일반 표현의 **망각(forgetting)·과특화** 측정이 본문에 없어, 50 궤적 적응이 일반성을 얼마나 보존하는지는 미검증입니다.
- **"50 궤적" 주장의 맥락** — 헤드라인 "~50 trajectories"는 **task 당** 수치입니다. LIBERO 한 suite 는 10 task × 50 = 500 궤적, RoboTwin 은 10 task × 50 = 500 궤적이 적응에 쓰입니다. 단일 task 적응 비용이 작다는 의미이지 전체 적응 예산이 50 궤적이라는 뜻은 아닙니다.
- **gripper/parallel-jaw 중심 평가** — LIBERO·RoboTwin·실로봇 task 모두 그리퍼·양팔 매크로 동작 중심이며, 다지(多指) 손재주·접촉 집약 task 가 없습니다. 손 중심 정밀성 주장에 대한 직접 근거는 부재합니다.

---

## ♻️ 재현성

- **코드/가중치** — arXiv HTML·초록·본문 어디에도 공개 코드/모델 링크가 없습니다(미공개로 보임).
- **데이터** — 전부 공개 데이터셋 사용: BridgeV2, EgoDex, LIBERO, RoboTwin 2.0, FurnitureBench. backbone 은 Prismatic VLM, frozen 인코더 `DINOv2-ViT-B/14-reg`, 분할은 SAM2 / RoboEngine.
- **하드웨어** — 실로봇은 ARX X5 leader / ARX R5 follower 양팔, wrist fisheye RGB 2 + 1인칭 RGB(20Hz), 60Hz 배포.
- **하이퍼파라미터 공개도** — step/batch/코드북 크기/토큰 수/프레임 간격은 명시되나, $`\lambda_{recon}/\lambda_{vq}/\lambda_{commit}/\lambda_{intent}`$ 구체 값, LoRA rank, 코드북 임베딩 차원 등은 미명시.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P4(VLM 사전학습 recipe 로 data-efficient adaptation) — 주 pillar.** 라벨 없는 egocentric 사람 영상을 사전학습 corpus 로 써서 ~50 궤적 적응을 달성하는 정확히 P4 의 핵심 레버입니다. **D22(pretraining data composition — egocentric vs mixed)** 의 OPEN 질문에 직접 닿는데, 본 논문은 단일 소스(BridgeV2 *또는* EgoDex) egocentric-only 사전학습이 작동함을 보입니다. **D21(staged recipe)** 의 "Stage 0 lineage → Stage 1 corpus 사전학습 → Stage 2 expert 학습 → Stage 3 적응" 골격과 3단계 파이프라인이 대응됩니다. **D23(action representation × pretraining)** 의 v1(연속 flow-matching head)과 액션 전문가가 일치합니다.
- **P0(VLA Datasets & Benchmarks) — 강한 보조.** **D24(egocentric 우선 데이터 축)** 를 실증: EgoDex(P0 핀)·BridgeV2 영상이 사전학습 입력이며, "데이터는 method 의 상류"라는 P0 정체성을 그대로 따릅니다.
- **P1(이종 Body/Hand action expert) — 부분 접점·긴장.** 액션 전문가는 존재하나 **단일(monolithic) flow-matching head** 로, Body/Hand 해부학적 분리가 없습니다. Identity 의 *Antagonist C*(arm/torso/finger 를 하나의 동질 공간으로 보는 monolithic decoder)에 해당하는 비교군 위치입니다. **D7(π backbone 통합)** 의 우리 선택(π0 slice)과 달리 Prismatic VLM + LoRA 슬라이스를 씁니다.
- **P2(구조적 멀티모달 관측 융합) — 부분 접점·긴장.** 의도-지각 분리에서 frozen DINOv2 를 "지각" 인코더로 따로 둔 점은 **D9(action/dynamics-aware encoder 경계 — observation 인코더는 P2)** 와 맞닿지만, DINOv2 는 action-aware 가 아닌 일반 geometry 인코더이고 융합은 flat concat 이라 **D10(concat 초월 융합)·D11(per-finger token)** 의 우리 방향과는 반대입니다. tactile/force 모달리티는 없습니다.
- **인접 — P5.** VQ-VAE 가 미래 프레임 특징을 재구성하는 latent action 학습은 latent world-action 계열(Being-H0.7)과 인접하나, 학습된 모델을 정책의 dynamics prior 로 결합하지 않고 사전학습 pseudo-label 생성에만 쓰므로 P5 의 "world model 을 stack 에 결합" 기여로 보기는 어렵습니다.
- **Identity** — 지지: P4 레버(egocentric 사전학습 → 소수 궤적 적응)와 P0 데이터 축의 직접 증거. 긴장: monolithic decoder, 적응 시 VLM unfreeze(우리 D19 v1=(a) 동결과 충돌), flat-concat, tactile 부재.

---

## ✨ 핀 논문 대비 델타

- **vs Being-H0.5([arXiv:2601.12993], P4 핀 — human-video-centric pretraining).** Being-H0.5 는 UniHand-2.0(VR 손 동작 라벨을 포함한 retarget corpus)으로 사전학습합니다. 본 논문의 진짜 델타는 **라벨이 전혀 없는 사람 영상**(AR/VR 손 포즈 라벨 없이 VQ-VAE 잠재 코드만)으로 동등 효과를 낸다는 점 — 라벨 의존성을 끊은 것이 핵심 차별점입니다.
- **vs UniVLA([arXiv:2505.06111], 가장 직접 baseline).** UniVLA 는 **언어**로 task-centric 움직임을 유도해 잠재 행동을 정제하지만, 본 논문은 **물리 마스크**(SAM2/RoboEngine)로 동작-배경을 명시 분리합니다. 결과적으로 cross-embodiment CKA 가 0.8659→0.9139 로 개선되고, dual-path(동작/배경 분리) 코드북이 추가 신규점입니다. UniVLA 가 코드북 grounding 에 로봇 측 궤적을 요구하는 것과 달리 로봇 라벨이 불필요합니다.
- **vs LAPA / villa-x([arXiv:2507.23682]).** villa-x 는 robot-specific state·action 을 자가지도에 통합해 grounding 하지만, 본 논문은 영상만 사용합니다(robot label-free). LIBERO Long 에서 villa-x 대비 +9.5%p.

---

## ⚙️ 의사결정 함의

- **D22(egocentric vs mixed) — 우리 OPEN ablation 에 신규 데이터포인트.** 단일 소스 egocentric-only 사전학습(EgoDex *또는* BridgeV2)만으로도 50-궤적 적응이 작동한다는 증거. "everything-mixed dump 가 꼭 필요한가"에 대해 **egocentric-only 가 충분조건일 수 있음**을 시사 — 다만 본 논문은 mixed 대조군을 직접 돌리지 않았으므로(혼합은 CKA 분석용으로만 사용) 우열 결론은 못 냅니다.
- **D19/D20(adaptation range·prior 보존) — 우리 v1(VLM 전면 동결)과 정면 대비.** 본 논문은 적응 시 **VLM 을 LoRA 로 갱신**합니다. 우리가 동결을 유지할지 LoRA 를 허용할지 결정할 때, 이 논문의 "Freeze" ablation(67.7→52.4)은 동결 시 성능 저하의 크기를 보여주는 직접 참고치입니다. 단, 망각 측정이 없어 동결의 *보존 이득*은 본 논문으로 답할 수 없습니다.
- **신규 config 후보** — (1) 적응 단계 **`λ_intent` 가중 cross-entropy 보조손실**: 액션 학습 중에도 잠재 의도 예측을 살려 의도 표류를 막는 lever; (2) **의도-지각 분리**: 액션 전문가 입력에서 "의도(VLM 은닉)"와 "지각(frozen DINOv2)"을 별도 채널로 분리해 action hallucination 억제 — 우리 액션 전문가 입력 설계(P2 D9/D10)에 시험 가능한 구체 레시피; (3) VQ-VAE **코드북 크기 16 / 토큰 수 4 / 1초 프레임 간격**은 우리가 손 중심으로 재현 시 곧장 표현력 병목이 될 후보값.
- **메트릭** — cross-embodiment 표현 품질을 **CKA(domain subspace 제거 후)** 로 정량화하는 프로토콜은, 우리가 사람→Sharpa 손 전이의 표현 정렬을 측정할 평가 도구로 차용 가능합니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 체크) 코드북 표현력의 손가락-DOF 병목.** 코드북 16·토큰 4 는 그리퍼 매크로엔 충분해도 22-DOF Sharpa 손의 미세 동작엔 부족할 공산이 큽니다. 사전학습 없이도 가능한 sanity: EgoDex 류 손 영상에 본 VQ-VAE 를 돌려 **코드 사용 엔트로피/충돌률**을 측정 — 정밀 손가락 동작들이 소수 코드로 붕괴하면 우리 손 중심 목표엔 곧장 부적합.
- **마스크 의존 disentanglement 의 in-hand 붕괴.** 우리 Phase 1(in-hand cube rotation)은 손이 물체를 **가린 채** 회전시키므로 SAM2 손 분할이 물체를 동작 전경에서 누락하거나 가림으로 실패하기 쉽습니다. 마스크가 무너지면 동작-배경 분리 가설이 깨져 코드북이 오염됩니다. 체크: 대표 in-hand 시퀀스 50장에 SAM2 를 돌려 손+물체 전경 IoU 확인.
- **tactile/force 부재 → 접촉 의미 미표현.** $`F_{full}`$ 에 촉각·F/T 가 없어 slip/grasp-retention 같은 접촉 신호가 표현되지 않습니다. 우리 P2(per-finger proprio-tactile)·P3(System0) 와 결합하려면 융합 경로 재설계가 선행되어야 합니다.
- **flat concat → per-finger attribution 상실.** 식 3의 단순 concat 은 우리 P2 anti-topic 입니다. 우리 스택에 그대로 이식하면 손가락별 접촉 귀속이 사라지므로, 이식 전 cross-attention 융합으로 교체 필요.
- **적응 시 VLM unfreeze 의 망각 미측정.** LoRA 적응이 사전학습 일반성을 얼마나 보존하는지 본문 근거가 없습니다. 우리 D19 동결 전략과 충돌하므로, 차용 시 prior-retention 메트릭(ConSFT 식)을 함께 붙여 검증해야 합니다.
- **1초 프레임 간격 = 매크로 의도, sub-policy-loop 반응 아님.** 잠재 행동이 1초 단위 macro intent 라, 우리 System0(접촉 유지용 sub-policy-loop 반응속도)이 요구하는 고주파 제어와는 시간 스케일이 다릅니다 — System0 의 supervision 으로는 부적합.
- **monolithic 액션 전문가 = 우리 P1 핵심을 다루지 않음.** Body/Hand 분리·정보 공유(D1/D4)에 대한 기여가 없으므로, 이 논문은 *데이터/사전학습* 레버로만 취하고 디코더 아키텍처는 우리 설계를 유지하는 게 맞습니다.

---

## 💡 컨텍스트 제안

- **P4 §5 methodology base 후보로 추적 제안** — "라벨 없는 egocentric 영상만으로 cross-embodiment 사전학습"은 Being-H0.5(라벨 의존)·UniVLA(로봇 grounding 필요)와 상보적인 데이터포인트입니다. 핀 8개 cap 을 건드리지 않는 비핀 methodology base 행으로 두는 것을 사람이 검토할 가치가 있습니다(자동 편집 안 함).
- **D22 OPEN ablation 근거 보강** — egocentric-only 단일 소스 사전학습의 작동 증거로 D22 의 "egocentric vs mixed" 논의에 인용 가능. 단 본 논문은 mixed 직접 대조가 없어 *결정* 근거로는 부분적입니다.
- **평가 도구 차용** — domain-subspace-제거 후 CKA 정렬 측정 프로토콜을 우리 사람→손 전이 표현 평가 도구로 P0/P4 측에서 검토 제안.
- (context/ 파일은 수정하지 않았습니다 — 위는 제안일 뿐입니다.)

---

> 💡 base 매핑은 `/implement-design analysis/2606.18955/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
