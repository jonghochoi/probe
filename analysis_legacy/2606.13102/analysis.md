# Paper Analysis — FTP-1: A Generalist Foundation Tactile Policy Across Tactile Sensors for Contact-Rich Manipulation

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | FTP-1: A Generalist Foundation Tactile Policy Across Tactile Sensors for Contact-Rich Manipulation |
| 저자 | Chengbo Yuan, Zicheng Zhang, Mingjie Zhou, Wendi Chen, Yi Wang, Zhuoyang Liu, Dantong Niu, Shuo Wang, Hui Zhang, Wenkang Zhang, Yingdong Hu, Yuanqing Gong, Wanli Xing, Chuan Wen, Cewu Lu, Kaifeng Zhang, Yang Gao |
| 링크 | [arXiv:2606.13102](https://arxiv.org/abs/2606.13102) · [Website](https://ftp1-policy.github.io/) |
| 발행일 / 버전 | 2026-06-11 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-15 |
| 관련 Pillar | P2, P1, P4, P0 |
| 태그 | tactile, vla-arch, dexterity |
| 카탈로그 | models/vla/Standalone/FTP-1, dataset/mixed/FTP-1-Dataset |

<!-- 초록 abstract 의 "Pretrained models, datasets, training code" 가 공개 예정이라 명시되어
     있으나 프로젝트 페이지(https://ftp1-policy.github.io/)가 이 환경에서 HTTP 403 으로
     막혀 GitHub / HuggingFace 의 정확한 URL 을 확인하지 못했습니다. 날조하지 않고
     Website 링크만 적습니다. -->

---

## 🧭 한 줄 요약 (TL;DR)

FTP-1 은 모달리티·형상·해상도가 제각각인 21종 촉각 센서를 단일 **Morphology-Aware Tactile Token Space (MTTS)** 로 통일하고 **공유 tactile expert** 로 모델링한, 최초의 *cross-sensor 일반화 촉각 foundation policy* 입니다. 약 3,000시간 이종 촉각 데이터로 사전학습한 뒤, seen 센서에서 +17.2%, **사전학습에서 본 적 없는 unseen 센서에서도 +31%** 의 성공률 향상을 보여 촉각 조작 스킬이 센서 경계를 넘어 전이됨을 입증합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — Vision 기반 generalist policy(π0.5 등)는 대규모 사전학습으로 강력한 초기화를 얻었지만, 촉각 기반 policy 는 여전히 특정 embodiment·센서 셋업에 묶여 있어 generalist 패러다임이 부재합니다.
- **기존 접근의 한계** — 촉각 신호는 하드웨어마다 modality(image/array/state)·resolution·morphology·contact response 가 근본적으로 이질적이라, 한 센서에서 학습한 표현을 다른 센서로 공유하기 어렵습니다. 최근 사전학습 촉각 policy 도 제한된 센서/관측 포맷/embodiment 에 갇혀 있습니다.
- **본 논문의 가설** — 단일 촉각 policy 가 이종 촉각 경험을 흡수해, 사전학습에서 본 센서·embodiment 를 *넘어* 전이 가능한 촉각 조작 스킬을 학습할 수 있는가? (generalist foundation policy 패러다임을 촉각으로 확장)
- **왜 지금 중요한가** — 촉각은 contact-rich, fine-grained 조작의 핵심 감각이지만 generalist VLA 흐름에서 거의 누락되어 있습니다. 센서 종속성을 깨면 흩어진 촉각 데이터셋을 한데 모아 규모의 경제를 얻을 수 있습니다.

---

## 🧩 핵심 기여

- **FTP-1** — morphology-aware tactile tokenization(MTTS) + 공유 tactile expert 로, 다양한 센서·embodiment 에 걸쳐 전이 가능한 촉각 조작 스킬을 가진 최초의 generalist foundation tactile policy.
- **FTP-1-Dataset** — 26개 데이터 소스, 21종 촉각 센서, 인간+로봇 시연을 MTTS 인터페이스로 표준화한 약 3,000시간 규모의 이종 촉각 조작 데이터셋. 촉각 policy 학습의 공유 출발점을 제공.
- **촉각 지식 전이 입증** — seen 센서 +17.2%, unseen 센서 +31%(절대 성공률) 향상. NTP-1 대조 ablation 으로 이득이 데이터 분포 근접이 아니라 **전이 가능한 촉각 지식**에서 온다는 가설(Hypothesis 2)을 지지.
- **모듈러 multi-expert 설계** — 촉각을 VLM expert 에 adapter 로 주입하지 않고 *독립 tactile expert* 로 분리해, 사전학습 지식 보존 + unseen 센서 재사용 + 효율을 동시에 달성.

---

## 🔑 기술 키워드

- **MTTS (Morphology-Aware Tactile Token Space)** — 손가락·손바닥·F/T 등 24개 "기능 영역(functional area)" 슬롯으로 촉각을 표준화하는 공용 어댑터 — 센서가 달라도 같은 콘센트(슬롯)에 꽂히게 만드는 통일 인터페이스.
- **Heterogeneous tactile encoders** — image/array/state 세 관측 타입마다 다른 인코더(ViT+T3 / CNN / MLP)로 센서별 신호를 MTTS 토큰으로 사영하는 센서-특이 입력단.
- **Shared tactile expert** — 모든 센서의 촉각 토큰을 공동으로 모델링하는 300M Transformer expert — 센서 간 공통 촉각 동역학을 학습해 unseen 센서로 재사용되는 부분.
- **Multi-expert foundation policy** — VLM expert + flow-matching action expert + tactile expert 로 모달리티별 처리를 분리한 π0.5 계열 아키텍처.
- **Functional-area embedding** — 각 토큰이 어느 기능 영역(엄지팁/검지팁/손목 F/T 등)인지 알려주는 학습형 위치 임베딩(좌/우손 분리).
- **UAS (Unified Action Space)** — 좌/우팔·머리·보조 슬롯을 고정 길이 sparse 벡터로 묶어 이종 embodiment 의 제어 신호를 한 layout 으로 표현.
- **FAAS (Function–Actuator–Aligned Space)** — 기능적으로 유사한 손가락 관절을 같은 action 슬롯에 배정해 서로 다른 dexterous hand 의 손 동작 공간을 통일(UniDex 차용).
- **Adaptive RMSNorm proprioception injector** — proprioception 을 별도 토큰이 아니라 attention block 의 정규화 파라미터로 주입해 일반화·robust 를 높인 fusion 기법.
- **T3 encoder** — vision-tactile 사전학습으로 얻은 공유 image-tactile Transformer; FTP-1 의 image-type 분기 초기화에 사용.
- **NTP-1 (No-Tactile-Pretraining)** — 촉각 입력/아키텍처를 빼고 동일 데이터·셋업으로 사전학습한 대조 checkpoint — 이득의 출처를 분리하는 ablation 의 핵심 baseline.

---

## 🔬 방법론

### 직관

FTP-1 의 출발점은 단순합니다. Vision-language policy 가 대규모 이종 데이터를 한 모델로 빨아들여 강해진 것처럼, 촉각도 그렇게 만들 수 있어야 한다는 것입니다. 그런데 촉각에는 vision 에 없는 장벽이 있습니다 — GelSight 같은 카메라형 센서는 이미지를, 매트릭스형 센서는 압력 배열을, 힘-토크 센서는 저차원 상태 벡터를 내놓아 신호의 *형태 자체*가 다릅니다. 같은 "엄지 끝의 접촉"인데도 센서마다 표현이 달라 한 모델이 공유 표현을 배우기 어렵습니다.

FTP-1 의 해법은 두 단계입니다. 첫째, 센서가 무엇이든 그 신호를 손의 **기능 영역**(엄지팁, 검지팁, 손목 F/T 등 24개 슬롯)으로 분류해 같은 자리에 매핑하는 공용 토큰 공간(MTTS)을 정의합니다. 이때 "어느 손가락의 어느 부위인가"를 알려주는 학습형 임베딩을 더해 형상 정보를 보존합니다. 둘째, image/array/state 세 타입마다 전용 인코더로 raw 신호를 이 토큰으로 사영하되, 그 위에서 동작하는 **tactile expert 는 모든 센서가 공유**합니다. 그래서 새 센서가 와도 입력단 인코더만 새로 학습하고 공유 expert 는 그대로 재사용할 수 있습니다 — 이것이 unseen 센서 전이의 메커니즘입니다.

마지막으로 촉각을 어떻게 VLA 에 합칠지가 관건인데, FTP-1 은 촉각을 VLM expert 안으로 adapter 처럼 밀어 넣지 않습니다. 대신 별도의 tactile expert 를 두고 action expert 가 그쪽을 *바라보게(attend)* 합니다(단방향). 이렇게 하면 사전학습된 vision-language 지식을 흩트리지 않으면서 촉각 처리를 독립적으로 키울 수 있습니다.

### 아키텍처

전체 정책은 언어 지시 $`\ell`$, (멀티뷰) RGB 관측 $`\mathcal{I}_{t}`$, proprioception $`\mathbf{s}_{t}`$, 촉각 관측 $`\mathcal{X}_{t}`$ 을 받아 action chunk 를 예측합니다.

![Figure 2 — FTP-1 architecture](https://arxiv.org/html/2606.13102/x2.png)

> "Figure 2: Overview of FTP-1 architecture. Heterogeneous tactile observations are mapped into a unified tactile token space through sensor-specific encoders, processed by a shared tactile expert, and fused with vision-language and proprioceptive information for action generation." (§2)
(이종 촉각 관측이 센서-특이 인코더를 통해 통일 토큰 공간으로 들어가고, 공유 tactile expert 가 처리한 뒤 vision-language·proprioception 과 융합되어 action 을 생성하는 전체 파이프라인을 보여 줍니다.)

> "Given a language instruction $`\ell`$, (multi-view) RGB observations $`\mathcal{I}_{t}`$, proprioception $`\mathbf{s}_{t}`$, and tactile observations $`\mathcal{X}_{t}`$, FTP-1 predicts an action chunk $`\hat{\mathbf{A}}_{t:t+H-1}=\pi_{\theta}(\ell,\mathcal{I}_{t},\mathbf{s}_{t},\mathcal{X}_{t})`$" (§2)
(정책 $`\pi_{\theta}`$ 는 네 모달리티를 받아 길이 $`H`$ 의 action chunk 를 예측합니다.)

$$\hat{\mathbf{A}}_{t:t+H-1}=\pi_{\theta}(\ell,\mathcal{I}_{t},\mathbf{s}_{t},\mathcal{X}_{t})$$

여기서 $`\hat{\mathbf{A}}_{t:t+H-1}\in\mathbb{R}^{H\times D}`$, $`H`$ 는 action horizon, $`D`$ 는 사전 정의된 Unified Action Space(UAS)의 차원입니다.

**(1) MTTS — 통일 촉각 인터페이스 (§2.1).** 촉각 신호를 24개 functional area 로 조직하고 각 영역을 한 토큰으로 표현합니다.

> "MTTS organizes tactile signals into 24 functional areas [50], each represented by one token; the full definition is shown in Fig. 3. For in-hand tactile signals, we use slots 0-14 to represent different hand functional regions. For force/torque signals from wrists and fingers, we use slots 15-20. For parallel grippers, the two gripper-side sensors are mapped to the thumb-tip slot (slot 0) and index-fingertip slot (slot 1), reflecting their two-finger grasping function. Slots 21-23 are reserved for future use." (§2.1)
(슬롯 0–14 는 손 내부 기능 영역, 15–20 은 손목·손가락 F/T, 21–23 은 예약. 평행 그리퍼는 두 면 센서를 엄지팁(슬롯 0)·검지팁(슬롯 1)으로 매핑해 2지 파지 기능을 반영합니다.)

![Figure 3 — MTTS functional-area definition](https://arxiv.org/html/2606.13102/figure/definition_tactile_torque_function_area.png)

> "Figure 3: Tactile functional-area definition of MTTS." (§2.1)
(24개 기능 영역 슬롯이 손의 어느 부위·어느 F/T 채널에 대응하는지 정의한 그림으로, MTTS 가 "형상 인지(morphology-aware)"인 근거를 시각화합니다.)

각 토큰에는 모든 센서가 공유하는 학습형 functional-area embedding 을 더하며, 좌/우손은 별도 임베딩으로 구분합니다.

**(2) Heterogeneous tactile encoders (§2.2).** 센서별 신호를 MTTS 기능 영역으로 묶은 뒤 image / array / state 세 타입으로 분류해 각기 다른 인코더로 토큰화합니다.

> "For image-type inputs (e.g., GelSight [83]), we use a lightweight sensor-specific ViT [17] followed by a shared pretrained T3 Transformer tactile encoder [89] across sensors, and use the final [CLS] token as the tactile token. For array-type inputs (e.g., Contactile [63]), we use a CNN [66] to capture spatial tactile structure and compress each functional area into one token. For state-type inputs (e.g., force-torque), we Fourier-encode the raw state [31] and process it with a lightweight MLP." (§2.2)
(image 는 센서-특이 ViT → 공유 T3 Transformer 의 [CLS] 토큰, array 는 CNN, state 는 Fourier 인코딩 후 MLP 로 토큰화합니다. 같은 관측 shape 의 기능 영역끼리는 인코더를 공유해 센서-특이 파라미터를 줄입니다.)

상세(App. B.2): image 입력은 $`224\times 224`$ 로 resize 후 센서-특이 Transformer(depth=3, width=768, head=12) → 공유 Transformer(depth=9, width=768, head=12, T3 weight 로 초기화)를 거쳐 [CLS] 토큰을 사용합니다. array 입력 $`(H,W,D)`$ 는 신호 차원에 Fourier 인코딩을 적용·concat 후 3-layer CNN + 2-layer ReLU MLP, state 입력 $`(D,)`$ 는 Fourier 인코딩·concat 후 3-layer ReLU MLP 로 처리합니다. 모든 토큰은 LayerNorm → functional-area embedding 가산 → 2-layer GELU MLP 사영으로 tactile expert 입력 차원에 맞춥니다.

**(3) Shared tactile expert 로 모달리티 융합 (§2.3).** π0.5 위에 multi-expert 구조를 얹어, vision-language Transformer expert 의 출력을 flow-matching action expert 가 attend 하는 구조에 *독립 tactile expert* 를 추가합니다.

> "Unlike prior tactile-augmented VLA models that inject tactile inputs into the vision-language expert via lightweight adapters [88, 12, 30, 39], FTP-1 uses an independent tactile expert for extracted tactile tokens. This design (1) supports reuse pretrained shared tactile expert on unseen sensors during finetuning (Section 4.1), promotes transferable tactile manipulation skills, and (2) avoids disturbing pretrained vision-language knowledge." (§2.3)
(adapter 주입 대신 독립 tactile expert 를 두는 핵심 이유는 ① unseen 센서에서 공유 expert 재사용, ② 사전학습된 vision-language 지식 비교란입니다. action expert 는 tactile expert 를 attend 하지만 그 역은 아닙니다 — 단방향.)

tactile expert 는 300M Transformer 이며(상세 App. B.4: width 1024, depth 18, MLP 4096, head 8, head dim 256), MoE 기반 융합 등 더 복잡한 설계는 일관된 이득이 없어 가장 단순한 multi-expert 를 채택했다고 밝힙니다. 또한 proprioception 은 별도 토큰 대신 adaptive RMSNorm 으로 주입하는 편이 일반화·robust 에 유리했습니다(App. B.3).

**(4) UAS / FAAS — 통일 action 공간 (App. B.1).** 이종 embodiment 의 제어 신호를 고정 layout 으로 묶습니다.

> "For one control step, the predicted action is $`\mathbf{a}=[\mathbf{a}^{L},\mathbf{a}^{R},\mathbf{a}^{ego},\mathbf{a}^{sup}]\in\mathbb{R}^{D}`$ where $`\mathbf{a}^{L}`$ and $`\mathbf{a}^{R}`$ denote the left- and right-arm control signals, $`\mathbf{a}^{ego}`$ denotes the head-pose control signal, and $`\mathbf{a}^{sup}`$ provides supplementary slots for additional controls such as locomotion or waist motion." (App. B.1)
(좌/우팔 + 머리 + 보조 슬롯을 한 벡터로 묶고, embodiment 가 지원하는 슬롯만 채웁니다.)

각 팔 action 은 $`\mathbf{a}^{b}=[\mathbf{t}_{w}^{b},\mathbf{r}_{w}^{b},\mathbf{q}_{\mathrm{arm}}^{b},\mathbf{q}_{\mathrm{hand}}^{b}]`$ 로, 손목 translation $`\mathbf{t}_{w}^{b}\in\mathbb{R}^{3}`$, 6D 회전 $`\mathbf{r}_{w}^{b}\in\mathbb{R}^{6}`$, 팔 관절 $`\mathbf{q}_{\mathrm{arm}}^{b}\in\mathbb{R}^{7}`$, 손 관절 $`\mathbf{q}_{\mathrm{hand}}^{b}\in\mathbb{R}^{32}`$ 로 구성됩니다. 손 관절은 UniDex 의 FAAS 로 기능적으로 유사한 관절을 같은 슬롯에 배정합니다. 학습 시 지원되지 않는 차원은 마스크 $`\mathbf{M}\in\{0,1\}^{D}`$ 로 loss 에서 제외합니다.

### 학습 목표 / 손실

논문 본문은 손실 식을 명시하지 않습니다 — π0.5 기반의 flow-matching action expert 를 사용한다고만 기술합니다(즉 action chunk 에 대한 flow-matching/conditional 생성 목표를 따르되, 수식은 원문에 제시되지 않음). 학습 신호 관련 명시 사항만 정리하면:

- action expert 는 flow-matching Transformer 이며 tactile expert 를 attend(§2.3).
- state·action 정규화는 z-score normalization 을 채택(quantile 기반보다 contact-rich fine-grained action 생성 품질이 좋았음, App. B.4).
- UAS 마스크 $`\mathbf{M}`$ 로 미지원 action 차원을 loss 에서 제외(App. B.1).

(구체적 flow-matching loss 식은 원문에 명시 없음 — π0.5 의 목표를 차용.)

### 학습 셋업

![Figure 4 — FTP-1-Dataset overview](https://arxiv.org/html/2606.13102/x3.png)

> "Figure 4: Overview of the FTP-1-Dataset. The dataset aggregates 26 sources across human and robot manipulation, covering 21 tactile sensors with image-, array-, and state-based modalities, all organized under the MTTS interface for unified pretraining." (§2.4)
(26개 소스·21종 센서·3개 모달리티를 MTTS 로 통일한 데이터셋 구성을 보여 주며, FTP-1 의 "이종 데이터를 한 인터페이스로 빨아들인다"는 주장의 데이터 측 근거입니다.)

> "FTP-1 is pretrained on a large-scale heterogeneous tactile manipulation dataset (Fig. 4) aggregated from 26 sources, covering 21 distinct tactile sensors: 7 image-type, 5 array-type, and 9 state-type sensors." (§2.4)
(21종 센서 = image 7 + array 5 + state 9. 추가로 Sharpa North-FTP-1(약 4,000개 long-horizon dexterous 시연)을 자체 수집.)

- **데이터 비율** — 데이터 불균형 완화를 위해 소스별 sampling ratio 적용, 재샘플링 후 인간:dexterous-hand:gripper ≈ 20%:30%:50%, 총 약 3,000시간(App. C). 언어 주석은 GPT-4o 로 rewrite 해 다양성 확보. 정규화 통계는 데이터셋별 독립 계산.
- **사전학습** — π0.5 codebase 기반. vision encoder/tokenizer/VL expert/action expert 는 π0.5 로 초기화, tactile encoder/tactile expert/adaptive RMSNorm injector/action projector 는 scratch 학습. 48× NVIDIA H20, 50k step, global batch 768, lr $`1\times 10^{-4}\to 5\times 10^{-5}`$. (50k step 이후 성능 saturate — 촉각 데이터 다양성 한계 + π0.5 지식 보존과 촉각 학습 간 trade-off 추정.)
- **Optimizer** — AdamW. (Muon 도 시도 — offline action MSE·수렴은 크게 개선하나 real-robot rollout 의 일반화·robust 가 떨어져 최종은 AdamW.)
- **파인튜닝** — 8× NVIDIA A800, 데이터셋당 20k step, batch 64, lr $`5\times 10^{-5}\to 5\times 10^{-6}`$.
- **인프라** — 도메인별 데이터를 별도 GPU 에 배치해 GPU batch 내 동일 포맷 보장. 도메인-특이 모듈 gradient 는 독립 업데이트, 공유 모듈 gradient 는 병합 후 joint 업데이트.

---

## 📊 실험 설정과 결과

평가는 5개 하드웨어 셋업으로, FTP-1 사전학습 checkpoint 를 5개 독립 기관에 배포해 각자 다른 embodiment·task suite 에서 파인튜닝합니다. baseline 3종은 모두 π0.5 codebase 로 동일 규모·데이터·프로토콜로 구현됩니다.

- **π0.5** — 촉각 입력 없는 SOTA open-source VLA. (촉각의 이득 측정)
- **Tactile-VLA** — 별도 tactile expert 없이 촉각 토큰을 VLM expert 에 주입하는 adapter 식. (tactile-expert 설계 효과 측정)
- **FTP-π0.5** — FTP-1 아키텍처를 π0.5 weight 로 일부 초기화하되 FTP-1 사전학습은 안 한 것. (대규모 촉각 사전학습 기여 분리)

평가는 시뮬레이션 100 rollouts/task, real-robot 20 rollouts/task, 지표는 파인튜닝 후 성공률(%).

### Seen 센서 — 시뮬레이션 (UniVTAC)

| Method | Lift Bottle | Pull-out Key | Lift Can | Put Bottle | Insert Hole | Insert Tube | Avg. | Avg. w/o Lift |
|---|---|---|---|---|---|---|---|---|
| VITaL* | 72 | 47 | 8 | 32 | 25 | 34 | 36.33 | 34.5 |
| UniVTAC-ACT* | 71 | 46 | 29 | 31 | 25 | 56 | 43.00 | 39.5 |
| π0.5 | 97 | 38 | 72 | 16 | 31 | 41 | 49.16 | 31.5 |
| Tactile-VLA | 97 | 32 | 15 | 10 | 41 | 56 | 41.83 | 34.75 |
| FTP-π0.5 | 77 | 30 | 26 | 19 | 47 | 72 | 45.16 | 42 |
| **FTP-1** | **97** | **48** | 65 | **47** | **64** | **79** | **66.66** | **59.5** |

> "FTP-1 achieves the best performance under both metrics, with 66.66% overall success and 59.5% excluding the lift tasks, outperforming the second-best method by about +17.5% in both cases." (§3.3, Table 1)
(Lift Bottle/Can 은 촉각 없이도 π0.5 가 97%/72% 로 거의 풀려, lift 제외 평균을 별도 보고합니다. 두 지표 모두 FTP-1 이 2위 대비 약 +17.5%.)

### Seen 센서 — Real-robot (Sharpa North / Sharpa&Dexmate)

| Method | Draw Balloon | Fix Hand (Tear) | Fix Hand (Finish) | Twist Cap | Flip Book | Wipe Dish | Average |
|---|---|---|---|---|---|---|---|
| π0.5 | 35 | 70 | 35 | 40 | 65 | 30 | 45.3 |
| Tactile-VLA | 20 | 80 | 25 | 10 | 45 | 35 | 35.8 |
| FTP-π0.5 | 25 | 65 | 25 | 20 | 70 | 45 | 41.6 |
| **FTP-1** | **45** | **80** | **40** | **65** | **85** | **60** | **62.5** |

> "Surprisingly, $`\pi_{0.5}`$ ranks second with a 45.3% average success rate, outperforming the other two tactile-based baselines. This suggests that, without proper modality fusion, tactile inputs may hurt performance by interfering with the vision-language perception module" (§3.3, Table 2)
(촉각 baseline 2종(Tactile-VLA 35.8%, FTP-π0.5 41.6%)이 촉각 없는 π0.5(45.3%)보다 낮습니다 — 적절한 융합 없이 촉각을 넣으면 VL 인지를 교란해 오히려 해가 될 수 있음을 보여 줍니다. FTP-1 은 62.5% 로 1위.)

### Unseen 센서 — Real-robot (FlexivXense / TactileUMI)

| Method | Insert Hanoi | Insert USB | Wipe Board | Avg. |
|---|---|---|---|---|
| π0.5 | 25 | 0 | 20 | 15.0 |
| Tactile-VLA | 0 | 10 | 15 | 8.3 |
| FTP-π0.5 | 5 | 10 | 30 | 15.0 |
| **FTP-1** | **55** | **30** | **55** | **46.6** |

> "Our method achieves the highest success rate among all baselines, reaching 46.6%. Compared with FTP-$`\pi_{0.5}`$ (15%), it improves the success rate by +31.6%, demonstrating that pretraining on large-scale heterogeneous tactile manipulation data effectively improves finetuning performance under unseen sensor settings." (§4.1, Table 3)
(사전학습에서 본 적 없는 Xense(image)·Contactile(array) 센서에서도 FTP-1 46.6% vs FTP-π0.5 15% → +31.6%p. 입력단 인코더만 새로 학습하고 공유 expert/T3 chunk/functional-area embedding 을 재사용한 결과입니다. 단순히 촉각 분기만 추가한 π0.5(15%)는 FTP-π0.5 와 동급 — 적절한 fusion prior + 사전학습 지식이 없으면 촉각 추가가 도움이 안 됨.)

### Ablation — 이득의 출처 (NTP-1 대조, §4.2)

| Method | Lift Bottle | Pull-out Key | Lift Can | Put Bottle | Insert Hole | Insert Tube | Avg. | Avg. w/o Lift |
|---|---|---|---|---|---|---|---|---|
| FTP-π0.5 | 77 | 30 | 26 | 19 | 47 | 72 | 45.16 | 42 |
| NTP-1 | 88 | 38 | 66 | 32 | 31 | 45 | 50.00 | 36.5 |
| **FTP-1** | 97 | 48 | 65 | 47 | 64 | 79 | **66.66** | **59.5** |

![Figure 7 — FTP-1 vs NTP-1](https://arxiv.org/html/2606.13102/figure/ntp_experiment_result.png)

> "Figure 7: Comparison between FTP-1 and NTP-1 on UniVTAC and FlexivXense." (§4.2)
(촉각 입력·아키텍처만 뺀 동일 사전학습 checkpoint NTP-1 과 비교 — 두 가설(데이터 분포 근접 vs 전이 가능 지식)을 분리합니다.)

> "On FlexivXense, FTP-1 substantially outperforms NTP-1 by +37.5%, demonstrating that tactile-based pretraining is essential for transferring to the FlexivXense domain." (§4.2)
(UniVTAC 에서는 NTP-1 이 FTP-π0.5 를 능가 → FTP-1-Dataset 분포가 UniVTAC 에 가까움(Hypothesis 1 일부 성립). 그러나 NTP-1 은 여전히 FTP-1 에 못 미치고, unseen FlexivXense 에서는 FTP-1 이 NTP-1 을 +37.5% 압도 → **촉각 분기 사전학습 자체가 전이 가능 지식을 인코딩**한다는 Hypothesis 2 를 지지. 표상: NTP-1 의 Lift Can(66) 은 FTP-1(65) 과 비슷해 lift 류는 촉각 의존도가 낮음을 재확인하나, Insert Hole(31 vs 64)·Insert Tube(45 vs 79) 등 contact-rich insertion 에서 격차가 큽니다.)

### 정성 관찰

- FTP-1 은 Insert Hanoi 에서 reactive insertion(piece 가 어긋나면 촉각 피드백으로 삽입 속도를 늦춤)을 보이나 π0.5 는 그렇지 못함. Insert USB(100 시연)는 data efficiency 시험대 — 타 모델은 삽입 중 미세 떨림으로 성공률 저하. Wipe Board 는 안정적 누름 힘 유지 실패가 빈번.

---

## ⚖️ 한계

- **저수준 force/tactile servoing 미해결** — 저자 명시. FTP-1 은 일반 촉각 *지각(perception)* 에 집중하며 tactile/force 기반 servoing·제어는 다루지 않습니다. 즉 촉각을 표현·융합해 imitation action 을 개선할 뿐, 접촉 힘을 닫힌 루프로 *제어*하지는 않아 정밀 force-control task 의 상한이 제한됩니다.
- **사전학습 데이터 규모·다양성 한계** — 저자 명시. 50k step 이후 성능 saturate 가 데이터 다양성 한계 + π0.5 지식 보존 trade-off 에서 온다고 봅니다. 즉 현재 데이터로는 scaling 곡선이 일찍 꺾여, 더 큰 aggregation·co-training 없이는 추가 이득이 어렵습니다.
- **촉각이 오히려 해가 되는 fusion 민감성** — real-robot 에서 촉각 baseline(Tactile-VLA·FTP-π0.5)이 촉각 없는 π0.5 보다 낮았습니다. 이는 FTP-1 의 독립 expert 설계가 정답임을 보여 주지만, 동시에 *융합 설계가 조금만 틀려도 촉각이 독이 된다*는 취약성을 드러냅니다 — 방법의 robust margin 이 좁을 수 있습니다.
- **20 rollouts/real-task 의 통계적 박약** — real-robot 평가가 task 당 20회뿐이라 5%p 단위 차이의 신뢰구간이 넓습니다(예: Insert USB 0% vs 30% 도 시연 100개·20 rollout 기준). seen 센서 셋업도 2종(GelSight-Mini, Sharpa DTC)에 불과해 "seen" 일반화의 폭이 좁습니다.
- **MTTS 슬롯 매핑의 사람 개입** — 새 센서를 기능 영역 슬롯에 배정하는 작업은 사람이 정의합니다(평행 그리퍼→슬롯 0/1 등). 형상이 특이한 센서(다접촉 패드, 비손형 end-effector)에서 이 수작업 매핑이 모호해질 수 있고, 매핑 품질이 전이 성능을 좌우합니다.
- **π0.5 의존** — vision encoder/VL expert/action expert 를 모두 π0.5 로 초기화하므로, π0.5 prior 가 약한 도메인(비π embodiment, 비유럽/북미 데이터 분포)에서는 촉각 이득과 별개로 backbone 한계가 전이됩니다.

---

## ♻️ 재현성

- **코드/모델/데이터** — abstract 에 "Pretrained models, datasets, training code and more visualization" 가 [프로젝트 페이지](https://ftp1-policy.github.io/)에서 공개된다고 명시(이 분석 환경에서는 페이지가 HTTP 403 으로 막혀 GitHub/HF 정확 URL 미확인 — 날조 없이 보류).
- **하드웨어** — 사전학습 48× NVIDIA H20(50k step), 파인튜닝 8× NVIDIA A800(20k step/dataset). 대규모이나 학원/소규모 랩 재현은 부담.
- **데이터** — 26개 소스 중 다수가 기존 공개 데이터셋(RH20T, MotionTrans, FreeTacMan, exUMI, ViTaMIn, OpenTouch 등)이나 일부는 자체/협력 수집(Sharpa North-FTP-1 4,000 시연, OmniSharingDB(PaXini), EgoTac 시리즈)이라 완전 재현엔 제약.
- **벤치마크** — UniVTAC 는 공개 시뮬 벤치마크(공식 50 시연/task 프로토콜 차용)라 seen-sim 결과는 상대적으로 재현 용이.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P2(structured multimodal observation fusion) — 정면 적중, primary.** MTTS 는 P2 의 핵심 메커니즘과 거의 1:1 입니다. D11(proprio-tactile-force token construction)의 v1 — "per-finger proprio-tactile binding, swappable sensor head + common token format, no Sharpa lock-in" — 이 바로 FTP-1 의 functional-area 슬롯 + 센서별 인코더 + 공유 토큰 포맷입니다. D12(topology-aware encoding + hand-level aggregation)도 functional-area embedding(손가락/손 identity, 좌/우 분리) + 공유 expert 의 self-/cross-attention 으로 대응됩니다. D10(heterogeneous modality fusion beyond concat)의 "cross-attention/asymmetric fusion, not flat concat" 은 FTP-1 의 독립 tactile expert + adaptive RMSNorm proprioception 주입과 정렬됩니다. **특히 우리 near-term 하드웨어가 Sharpa Hand(D11 "no Sharpa lock-in" 비협상 항목)인데, FTP-1 이 Sharpa DTC 센서를 사전학습/평가에 포함**한 점은 직접적 실무 연결고리입니다.
- **P1(heterogeneous Body/Hand action expert) — 강한 지지.** UAS/FAAS 는 D2(Body output space = 손목/툴-플랜지 pose)·D3(Hand output space = finger joint)·D7(π backbone 통합/partition)와 맞닿고, multi-expert(VL+action+tactile) 분할은 D1(split form)의 "단일 ActionExpert + 강하게 분리된 latent" 비교군에 해당합니다.
- **P4(pretraining for data-efficient adaptation) — 지지.** "대규모 이종 사전학습 → minutes-of-data 파인튜닝" 이 P4 의 핵심 주장과 동형이며, π0.5 weight 부분 초기화 + scratch 모듈 분리는 D19(lineage + adaptation range)·D21(staged recipe)·D20(prior 보존; 독립 expert 로 VL 지식 비교란)과 닿습니다. saturate 분석은 D22(데이터 composition)에 직접 정보를 줍니다.
- **P0(VLA datasets & benchmarks) — 자료원.** FTP-1-Dataset 은 D25(tactile/torque data scouting)의 정확한 표적 — 흩어진 촉각/F-T 코퍼스를 한데 모은 가장 큰 aggregation 사례입니다. catalog 라우팅(`dataset/mixed/FTP-1-Dataset`)으로 전달.
- **P3(System0) — 경계.** FTP-1 의 저자 명시 한계("tactile/force servoing·control 미해결")가 정확히 P3 의 범위(접촉 안정화 RL)입니다. FTP-1 은 P3 를 *대체하지 않고* 그 상위 지각/표현 레이어를 채우는 보완재로 읽힙니다.
- **Identity** — "per-finger proprio-tactile binding beyond flat concat"(Identity 축 (2))을 강하게 지지. RL/correction-module 논쟁(Antagonist A/B)과는 무관(촉각은 VLA-level imitation 으로 처리).

---

## ✨ 핀 논문 대비 델타

- **vs. ViTacFormer (P2 핀, [arXiv:2506.15953], D10/D11)** — ViTacFormer 는 *단일 센서/embodiment* 의 cross-attention visuotactile 융합입니다. FTP-1 의 진짜 새로움은 21종 *이종* 센서를 하나의 morphology-aware 토큰 공간으로 통일하고 공유 expert 로 묶어 **cross-sensor·unseen-sensor 전이**를 최초로 보인 점입니다 — 융합 메커니즘이 아니라 *센서 일반화*가 델타.
- **vs. Sparsh (P2 methodology base, [arXiv:2410.24090])** — Sparsh 는 vision-tactile 쌍으로 학습한 촉각 *표상* foundation model 로, manipulation 에 end-to-end 최적화되지 않습니다. FTP-1 은 action-labeled 촉각 데이터로 *policy 자체*를 end-to-end 사전학습합니다(저자도 §A.3 에서 이 구분을 명시).
- **vs. DexViTac ([arXiv:2603.17851], D11/D12)·SaTA ([arXiv:2510.14647], Sharpa 하드웨어)** — 이들은 kinematic-grounded 촉각 인코딩 / 특정 Sharpa 셋업에 특화. FTP-1 은 동일한 kinematic/topology 인지(functional-area)를 *센서-불가지론적 generalist* 규모로 끌어올린 것이 차별점.
- **요약** — P2 핀 중 "cross-sensor 일반화 + foundation 규모 사전학습 + 독립 tactile expert" 를 한꺼번에 만족하는 첫 사례. 핀 교체 후보로 충분히 강함(아래 💡 참조).

---

## ⚙️ 의사결정 함의

- **D11 토큰 구성** — 우리의 "10 finger + 2 palm 토큰 + swappable sensor head + common token format" 설계를 FTP-1 의 **24-slot functional-area 스킴**으로 구체화/대체 검토. 특히 Sharpa Deform Map 을 image-type 으로 분류해 *센서-특이 ViT → 공유 T3 Transformer([CLS])* 경로에 태우는 것을 1차 구현안으로 채택 가능 — config 키: `tactile_encoder.type=image`, `shared_backbone=t3`, `functional_area_slots=24`.
- **D10 융합 위치** — proprioception 주입을 "별도 토큰" 대신 **adaptive RMSNorm**(AdaLN 계열)로 전환하는 실험. loss/metric 변화를 ForceFlow(우리 D10 핀)식 modal-masking 과 A/B.
- **D20 prior 보존 레버** — "촉각을 VLM expert 에 adapter 주입하지 말고 *독립 tactile expert* 로 분리(action expert 가 단방향 attend)" 를 prior-preservation 의 구조적 레버로 채택 — VL weight 동결/PEFT 와 결합.
- **D7 partition** — backbone 은 π0.5 초기화, tactile/action-projector 는 scratch 라는 partition 을 우리 π0/π0.5 스택에 그대로 매핑. optimizer 는 AdamW(논문이 Muon 의 일반화 저하를 보고 — 우리도 Muon 도입 시 *offline MSE 가 아니라 real-rollout 성공률*로 검증할 것).
- **D25 데이터** — FTP-1-Dataset(공개 시) 또는 그 구성 소스(RH20T-F/T, MotionTrans, FreeTacMan, exUMI 등)를 우리 사전학습 corpus 후보로 즉시 평가.

---

## ⚠️ 먼저 검증할 실패 모드

1. **(가장 싼 체크) Sharpa DTC ↔ 우리 Sharpa Hand 센서 일치 여부** — 논문이 쓴 "Sharpa DTC"(image-type)가 우리 Sharpa Hand 의 Deform Map(~320×240/fingertip @30Hz)과 같은 계열인지 spec 대조만으로 즉시 확인. 같다면 seen-sensor 경로(인코더+expert 재사용)를 그대로 받을 수 있고, 다르면 unseen-sensor 경로(인코더 scratch)로 떨어집니다.
2. **공개 checkpoint/코드 가용성** — 프로젝트 페이지가 실제로 weight·code 를 공개하는지(이 환경에선 403). 미공개면 "독립 tactile expert + MTTS" 를 우리가 scratch 재구현해야 하므로 비용이 급증 — 도입 전 반드시 확인.
3. **22-DOF Sharpa Hand 의 FAAS 매핑 가능성** — UAS 손 슬롯이 32 canonical joint 인데 우리 손(22-DOF, 손목 DOF 없음)을 FAAS 슬롯에 모호함 없이 매핑할 수 있는지. 손목 DOF 부재가 $`\mathbf{r}_{w}`$/$`\mathbf{t}_{w}`$ 슬롯과 충돌하지 않는지 점검.
4. **촉각이 독이 되는 fusion 취약성** — real-robot 에서 잘못된 융합이 촉각 없는 baseline 보다 *낮은* 성능을 냈으므로, 우리 스택에 MTTS 를 얹었을 때도 먼저 "촉각 ON vs OFF" A/B 로 *해가 되지 않는지*부터 확인(이득 측정 이전에 무해성 확인).
5. **데이터 규모 의존** — 이득이 3,000시간 사전학습에서 오는데(NTP-1 ablation), 우리가 그만한 촉각 데이터를 못 모으면 FTP-π0.5(사전학습 없는 동일 아키텍처) 수준에 머물 위험. 즉 "아키텍처만 차용"은 효과의 상당 부분을 놓칠 수 있음 — 공개 checkpoint 확보가 사실상 전제.
6. **π0.5 prior 미스매치** — backbone 이 π0.5 인데 우리 backbone lineage(P4 D19)가 다르면 multi-expert attend 경로의 사전학습 정렬이 깨질 수 있음.

---

## 💡 컨텍스트 제안

- **P2 핀 교체 후보** — FTP-1 을 P2 §5 Pinned 에 *Top/cross-sensor* 역할로 추가 검토(현재 8개 cap). cross-sensor 일반화 + foundation 규모를 단독으로 커버하는 핀이 없으므로, methodology-base 의 DexViTac/SaTA 중 하나를 내리고 FTP-1 을 올리는 quarterly rebalance 후보.
- **P0 §5 / catalog** — FTP-1-Dataset 을 `catalogs/datasets.md` 🔀 Mixed 에 등재(본 분석 카탈로그 라우팅으로 skeleton row 생성 예정). D25 tactile/torque 데이터 anchor 갱신 후보.
- **하드웨어 메모** — MASTER §4.1 의 "Tactile encoder uses swappable sensor head + common token format (P2)" 가정을 FTP-1 의 MTTS 가 실증함 — 설계 가정의 외부 증거로 기록 가치.
- context/ 파일은 수정하지 않았습니다(제안만).
