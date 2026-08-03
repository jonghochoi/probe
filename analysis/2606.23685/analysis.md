# Paper Analysis — LaST-HD: Learning Latent Physical Reasoning from Scalable Human Data for Robot Manipulation

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | LaST-HD: Learning Latent Physical Reasoning from Scalable Human Data for Robot Manipulation |
| 저자 | Jiaming Liu, Yinxi Wang, Chenyang Gu, Siyuan Qian, Xiangju Mi, Hao Chen, Jiawei Chen, Qingpo Wuwu, Xiaoqi Li, Nuowei Han, Yiming Zhang, Xuheng Zhang, Yang Yue, Yeqing Yang, Lei Wang, Peng Jia, Hao Tang, Shanghang Zhang |
| 링크 | [arXiv:2606.23685](https://arxiv.org/abs/2606.23685) · [Website](https://siriyep.github.io/last-hd-project-page/) |
| 발행일 / 버전 | 2026-06-22 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-23 |
| 관련 Pillar | P5, P0, P4, P1 |
| 태그 | vla-arch, egocentric-data, dexterity |

---

## 🧭 한 줄 요약 (TL;DR)

LaST-HD 는 인간 손과 로봇 시연을 **공유 잠재 추론 공간**에서 정렬해 사람 손 데이터로부터 로봇 행동을 학습하는 "reasoning-before-acting" VLA 입니다. 핵심은 짝지어지지 않은(unpaired) 인간·로봇 궤적으로 학습한 **action-conditioned world model** 의 forward-dynamics 특징을 잠재 추론 expert 의 지도(supervision) 타깃으로 쓰는 것으로, 인간 운동학을 모방하지 않고도 형태(morphology)에 무관한 물리 동역학을 내재화합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 로봇 원격조작(teleoperation) 데이터는 수집 비용이 크고 하드웨어 오버헤드가 큽니다. 풍부하고 확장 가능한 사람 손 시연을 로봇 행동 학습으로 전이하되, 단순 기하 retargeting 을 넘어 인간·로봇 사이의 **물리 동역학 정렬**까지 다루는 것이 목표입니다.
- **기존 접근의 한계** — 운동학 retargeting / 형태 변환은 인간 손 자세를 로봇 관절 공간에 직접 사상(mapping)할 뿐이고, 사람 손을 또 하나의 cross-embodiment 변종으로 보고 공동 학습(co-training)하는 최신 VLA 들도 **데이터 규모에 민감하거나 물리 동역학 정렬을 간과**합니다.
- **본 논문의 가설** — VLA 의 물리 추론(physical reasoning)을 **중간 인터페이스**로 삼으면, action-level 공동 학습보다 사람 손 시연을 로봇 행동 학습으로 더 잘 전이할 수 있다는 것입니다.
- **왜 지금 중요한가** — VLA 가 open-world 일반화를 풀려면 대규모 사람 손 데이터 활용이 critical 해졌고, 저비용 고정밀 데이터 수집 장치와 결합하면 target-domain 로봇 데이터 없이 새 객체·장면·위치로 일반화가 가능해집니다.

---

## 🧩 핵심 기여

- **LaST-HD 패러다임** — 인간 손·로봇 데이터를 공유 잠재 물리 추론 공간에서 정렬해 형태 무관(morphology-agnostic) 행동 학습을 가능하게 하는 human-to-robot action learning 패러다임. reasoning-before-acting VLA 를 확장합니다.
- **World model 을 정렬 다리(alignment bridge)로 사용** — 짝지어지지 않은 인간·로봇 궤적으로 학습한 action-conditioned world model 의 forward-dynamics 특징을 잠재 추론 expert 의 명시적 ground-truth 타깃으로 추출. action label 을 약한 anchor 로 쓰는 것이 핵심.
- **OOL Glove** — 100 g 미만의 저비용 IMU 기반 모션캡처 장갑. 21개 손-손목 keypoint 를 sub-millimeter RMS 오차로 추적하고, 그리퍼·다지 손 모두에 retarget 가능한 보편적 행동 지도를 제공.
- **Mixed-to-human 학습 레시피** — (1) 혼합 인간-로봇 co-training 으로 사람 손 시연만으로 새 객체·장면·위치 일반화 개선, (2) 실패 상태에서 사람 손 online correction post-training 으로 20분(60 trajectory) 데이터만으로 90% 이상 정확도 달성.

---

## 🔑 기술 키워드

- **LaST-HD** — Latent Spatio-Temporal reasoning for Human-hand Data. 사람 손 데이터를 잠재 물리 추론 공간에서 정렬해 로봇 행동으로 옮기는 VLA 프레임워크.
- **Reasoning-before-acting VLA** — 행동을 내기 전에 먼저 "task-relevant 물리 동역학"을 압축 잠재 추론으로 산출하는 패러다임. 사람이 손을 뻗기 전 머릿속으로 결과를 그려보는 것과 유사.
- **Action-conditioned World Model** — 시각 관측 + action chunk 를 입력받아 미래 물리적 결과(future frame)를 예측하는 동역학 모델. 본 논문에서는 행동 예측이 아니라 **잠재 지도 타깃 생성기**로만 쓰입니다.
- **Human-to-Robot Latent Alignment** — 운동학이 다른 인간·로봇 궤적을 같은 잠재 공간으로 투영해, "사과를 밀면 형태와 무관하게 비슷한 물체 운동이 생긴다"는 물리 불변성으로 정렬하는 전략.
- **Mixture-of-Transformers (MoT)** — 하나의 decoder-only transformer 를 reasoning expert 와 action expert 로 분리한 VLA backbone. 두 expert 는 shared attention 으로 정보를 주고받습니다.
- **Latent CoT (Chain-of-Thought)** — 텍스트가 아닌 잠재 토큰 시퀀스로 수행하는 사고 사슬. reasoning expert 가 autoregressive 하게 $`N_{\text{lat}}`$ 개 잠재 상태를 예측.
- **Flow matching action loss** — action expert 가 연속 행동 chunk 를 생성할 때 쓰는 플로우 매칭 손실 $`\mathcal{L}_{\mathrm{act}}`$.
- **OOL Glove (Out-of-Lab Glove)** — 외골격 없이 native 인간 손 동작을 직접 기록하는 초경량 IMU 장갑. 로봇 teleop 대비 4–5배 빠른 수집.
- **Mixed-to-human recipe** — 혼합 인간-로봇 co-training → 사람 손 online correction 의 2단계 점진적 학습 레시피.
- **Human-hand online correction** — 실패 빈발 상태에서 teleop 대신 사람 손 corrective 시연을 OOL Glove 로 수집해 balanced replay 로 적응시키는 post-training.

---

## 🔬 방법론

### 직관

LaST-HD 의 출발점은 "사람 손 데이터는 풍부하지만, 인간 손과 로봇 팔의 형태 차이(embodiment gap) 때문에 직접 전이가 어렵다"는 문제입니다. 기존 방식은 인간 손 자세를 로봇 관절로 직접 옮기거나(운동학 retargeting), 인간 데이터와 로봇 데이터를 action 수준에서 섞어 학습(co-training)했는데, 전자는 기하적 사상에 그치고 후자는 도메인 불일치에 취약합니다. LaST-HD 의 통찰은 **"행동을 흉내내지 말고, 행동의 물리적 결과를 정렬하라"** 입니다.

이를 위해 LaST-HD 는 행동을 내기 전에 잠재 추론(latent reasoning)을 먼저 수행하는 VLA 를 쓰고, 그 잠재 추론이 무엇을 학습해야 하는지를 **별도의 action-conditioned world model** 로부터 가져옵니다. world model 은 "현재 화면에서 이 행동을 하면 다음에 무슨 일이 일어나는가"를 예측하도록 학습되는데, 인간이든 로봇이든 같은 물리 법칙을 따르므로(사과를 밀면 누가 밀어도 사과는 비슷하게 굴러갑니다) 그 예측 특징은 형태에 무관한 공유 표현이 됩니다. 이 특징을 잠재 추론의 정답으로 삼으면, 인간 손 시연과 로봇 시연이 같은 잠재 공간으로 모입니다.

중요한 설계 선택은, world model 을 **행동 예측이 아니라 잠재 지도(supervision)에만** 쓴다는 점입니다. world model 의 특징은 효율적 제어를 하기엔 충분히 압축되어 있지 않고, action conditioning 이 정보 누출(leakage)을 일으킬 수 있기 때문입니다. 또한 이 잠재 타깃은 **오프라인으로 미리 계산**되어 학습 시 일반 입력처럼 로드되므로, world model 을 정책과 함께 공동 학습할 필요가 없습니다.

![Figure 1 — LaST-HD 개요](https://arxiv.org/html/2606.23685/x1.png)

> "Figure 1: Overview of LaST-HD. LaST-HD aligns human-hand and robot demonstrations through action-conditioned latent physical reasoning, enabling morphology-agnostic action learning under a progressive mixed-to-human training recipe." (§1)
(이 그림은 인간 손·로봇 시연이 action-conditioned 잠재 물리 추론을 통해 정렬되고, UMAP 상에서 같은 task 의 인간·로봇 궤적이 구조적으로 겹치는 모습을 시각화합니다.)

본 논문의 동기를 한 문장으로 못 박는 anchor 는 다음과 같습니다.

> "Can we use the physical reasoning of VLA models as an intermediate interface to better transfer human-hand demonstrations into robot action learning?" (§1)
(VLA 의 물리 추론을 인간 손 데이터 전이의 "중간 인터페이스"로 쓰자는 것이 전체 설계의 출발점입니다 — action 을 직접 정렬하는 대신 물리 추론 잠재를 정렬합니다.)

### 아키텍처

LaST-HD 는 Janus-Pro 위에 구축된 **Mixture-of-Transformers (MoT) VLA** 입니다. 입력/출력과 모듈 분해는 다음과 같습니다.

- **입력** — 언어 지시 $`\mathbf{l}`$ 과 시각 관측 $`\mathbf{I}_{t}\in\mathbb{R}^{H\times W\times 3}`$ ( `H = W = 384` ). 정책 $`\pi_{\theta}`$ 은 action chunk $`\mathbf{a}_{t+1:t+H}\sim\pi_{\theta}(\cdot\mid\mathbf{I}_{t},\mathbf{l})`$ 를 예측.
- **Vision encoder** — SigLIP-Large 로 시각 특징 $`f_{\text{img}}\in\mathbb{R}^{N_{\text{img}}\times d_{v}}`$ 추출 후 MLP 로 LLM hidden space 에 투영. ( $`N_{\text{img}}`$ = 시각 토큰 수, $`d_{v}`$ = 시각 임베딩 차원.)
- **VLA backbone** — DeepSeek-LLM 1.5B 의 24-layer decoder-only transformer 를 MoT 정책으로 재구성. 두 expert 로 분리:
  - **Reasoning expert** — autoregressive 하게 잠재 상태 시퀀스 $`\mathcal{Z}\in\mathbb{R}^{N_{\text{lat}}\times d_{l}}`$ 예측 ( $`N_{\text{lat}}`$ = 추론 토큰 수, $`d_{l}`$ = LLM hidden 차원).
  - **Action expert** — 플로우 매칭으로 action chunk $`\mathbf{a}_{t:t+H-1}`$ 예측.
- **Shared attention** — reasoning expert 의 잠재 추론 지식을 action expert 로 전달하는 통로. 형태 무관 물리 추론 prior 를 action 예측 직전에 주입하는 인터페이스 역할.

![Figure 2 — 프레임워크](https://arxiv.org/html/2606.23685/x2.png)

> "Figure 2: Framework. (a) LaST-HD aligns human-hand and robot data through an action-conditioned world model, which converts predicted physical consequences into denoised future-frame features as latent supervision for the reasoning expert. The aligned latent CoT conditions the action expert through shared attention for action generation." (§3.2)
(world model → 잠재 지도 → reasoning expert → shared attention → action expert 의 데이터 흐름, OOL Glove 수집 플랫폼(b), mixed-to-human 레시피(c)를 한 장에 종합합니다.)

### Human-to-Robot Latent Alignment (핵심)

이 절이 논문의 심장입니다. **World model 을 정렬 다리로** 사용합니다.

> "we fine-tune an action-conditioned world model [31], on a mixed dataset of glove-collected human and real-robot demonstrations. Importantly, demonstrations from the two domains need not be strictly paired." (§3.2)
(인간·로봇 데이터가 **짝지어질 필요가 없다**는 점이 결정적입니다 — paired 데이터 수집은 비싸고 비현실적인데, action label 이 약한 anchor 역할을 하므로 unpaired 로도 정렬이 가능합니다.)

타깃 추출 절차: 시각 관측을 world model 에 입력하고 연속 action chunk 를 매 layer 의 cross-attention 으로 주입합니다. 마지막 denoising step 에서 **가장 깊은 U-Net layer** 의 특징을 추출(predictive physical dynamics 를 담고 domain-invariant)하고, MLP aligner 로 $`d_{l}`$ 차원에 투영 → flatten → adaptive average pooling 으로 $`N_{\text{lat}}`$ 개 잠재 토큰으로 압축합니다. 이 토큰이 reasoning expert 의 명시적 ground-truth $`\mathbf{z}^{\mathrm{GT}}_{t}`$ 가 됩니다.

왜 world model 을 행동 예측이 아니라 잠재 지도로만 쓰는지가 중요한 설계 결정입니다.

> "Notably, we use the world model for latent supervision rather than direct action prediction, since its latent features are not sufficiently compact for efficient control, and action conditioning may introduce information leakage." (§3.2)
(world model 특징은 제어에 쓰기엔 압축이 부족하고, action conditioning 을 행동 예측에 직접 쓰면 정답 action 이 누출될 수 있어, **잠재 지도 타깃 생성기**로만 격리해 사용합니다.)

정렬이 작동하는 이유(물리 불변성):

> "Since both embodiments obey the same physical laws—for example, pushing an apple produces similar object motion regardless of embodiment—action-conditioned prediction encourages latent alignment around shared task semantics and physical dynamics." (§3.2)
(미래-프레임 *시각* 표현은 외형 변화를 주로 잡지만, action-conditioned forward-dynamics 표현은 상호작용의 **물리적 결과**를 인코딩하므로, 형태가 달라도 같은 task semantics·물리 동역학으로 잠재가 모입니다 — 이것이 SigLIP 미래-프레임 타깃 대비 LaST-HD 의 차별점입니다.)

### 학습 목표 / 손실

잠재 추론 expert 는 정렬된 잠재 타깃으로 지도됩니다. 예측 잠재 토큰 $`\hat{\mathbf{z}}_{t}`$ 와 타깃 $`\mathbf{z}^{\mathrm{GT}}_{t}`$ 사이 **cosine similarity loss**:

$$\mathcal{L}_{\mathrm{latent}}=\sum_{t=1}^{N_{\mathrm{lat}}}\left(1-\frac{\hat{\mathbf{z}}_{t}\cdot\mathbf{z}_{t}^{\mathrm{GT}}}{\lVert\hat{\mathbf{z}}_{t}\rVert\lVert\mathbf{z}_{t}^{\mathrm{GT}}\rVert}\right).$$

$`N_{\mathrm{lat}}`$ 개 잠재 토큰 각각에 대해 (1 − cosine 유사도)를 합산하므로, 방향 정렬만 강제하고 크기(norm)는 자유롭게 둡니다. action expert 는 플로우 매칭 action loss $`\mathcal{L}_{\mathrm{act}}`$ 로 실행 가능한 로봇 행동을 생성하도록 학습됩니다. 전체 목적함수:

$$\mathcal{L}_{\mathrm{loss}}=\mathcal{L}_{\mathrm{act}}+\lambda\mathcal{L}_{\mathrm{latent}},$$

여기서 $`\lambda`$ 가 action 지도와 잠재 지도의 균형을 맞춥니다. 이 목적함수는 사전학습과 downstream fine-tuning 양쪽에 동일하게 적용됩니다.

### OOL Glove (데이터 수집)

OOL Glove 는 저비용·저지연·확장 가능한 사람 손 데이터 수집을 위한 장치입니다. 외골격/햅틱 장갑이 강체 링크·케이블로 자연스러운 손 동작을 제약하는 반면, OOL Glove 는 장갑 하나당 100 g 미만의 초경량 설계로 native 손 운동학을 보존합니다.

- **하드웨어** — 6개 compact IMU 기반 6-DoF 센싱 모듈로 20개 손 keypoint + 1개 손목 keypoint 를 통합 hand-centric 좌표계에서 추적. 200 Hz 초과 동작, 10 ms 미만 지연, keypoint 당 sub-millimeter 평균 RMS 위치 오차.
- **수집 셋업** — 손목 장착 2개 + head/chest 장착 1개 시점. 언어 지시·관측·정밀 손-손목 상태로 구성된 동기화 multimodal 궤적.
- **retarget** — native 손 궤적을 통합 hand-centric 표현으로 사상. 그리퍼 명령은 손끝 거리에서 유도, 다지 손 관절각은 인간 손 keypoint 간 상대 공간관계 기반 inverse-kinematics retargeting 으로 해결.

> "It also enables 4-5 $`\times`$ faster data collection than robot teleoperation on standard tasks, while avoiding signal loss." (§3.3)
(teleop 대비 4–5배 빠른 수집이 "scalable human data"라는 제목의 근거입니다 — 중간 제어 인터페이스(master arm/space mouse) 없이 손 동작을 직접 기록하기 때문입니다.)

![Figure 5 — OOL Glove 하드웨어 및 수집 셋업](https://arxiv.org/html/2606.23685/x5.png)

> "Figure 5: OOL Glove hardware and human-native data collection setup. (a) Lightweight glove hardware with six compact IMU-based sensing modules. (b) Natural manipulation demonstrations are collected with synchronized egocentric vision, wrist 6-DoF tracking, and glove-based hand kinematics." (§A.1)
(장갑 하드웨어·자연스러운 손-물체 상호작용 수집·metric keypoint 재구성의 세 단계를 보여줍니다.)

### 학습 셋업 (Mixed-to-Human 레시피)

**Stage 1 — Mixed Human-Robot Co-training.** 먼저 혼합 인간 손·로봇 궤적으로 action-conditioned world model 을 학습하고, 미래 프레임에 해당하는 world-model 특징을 형태 무관 지도로 삼습니다. world model 은 downstream task 마다 재학습할 필요가 없고, **사전학습에 target-embodiment 데이터를 포함하는 것으로 충분**합니다(예: OOL Glove 데이터 + Tianji dual-arm 데이터). co-training 동안 LaST-HD 는 인간 손·로봇 궤적 양쪽으로 최적화됩니다.

**Stage 2 — Human-Hand Online Correction Post-training.** co-training 후 실제 로봇에 LaST-HD 를 배치해 rollout 하며 실패 빈발 상태를 식별하고, teleop 대신 OOL Glove 로 **사람 손 corrective 시연**을 수집합니다. 이 단계에서 world model 은 frozen 입니다.

> "To incorporate new corrective knowledge while avoiding catastrophic forgetting, we post-train LaST-HD for only 1–2 epochs with balanced replay." (§3.4)
(망각(catastrophic forgetting) 방지를 위해 1–2 epoch 만, 이전 buffer 와 DAgger buffer 를 동량 샘플링하는 balanced replay 로 post-train 합니다.)

각 배치는 이전 데이터 buffer $`\mathcal{D}_{\mathrm{prev}}`$ 와 사람 손 DAgger buffer $`\mathcal{D}_{\mathrm{dagger}}`$ 에서 동량 샘플링:

$$\mathcal{B}=\mathcal{B}_{\mathrm{prev}}\cup\mathcal{B}_{\mathrm{dagger}},|\mathcal{B}_{\mathrm{prev}}|=|\mathcal{B}_{\mathrm{dagger}}|.$$

**대규모 사전학습** — MoT 모델은 OXE / DROID / RoboMIND 에서 큐레이션한 **400K trajectory, 28M frame** 혼합으로 사전학습됩니다. 다만 prior VLA baseline 과의 공정 비교를 위해 LaST-HD MoT 모델은 실제 로봇 궤적으로만 사전학습하고, action-conditioned world model 은 OOL Glove 인간 손 + 실제 로봇 궤적 양쪽으로 사전학습합니다. world model 은 학습 후 frozen 되어 잠재 ground-truth 타깃을 **오프라인 precompute** 합니다.

---

## 📊 실험 설정과 결과

**평가 셋업** — 3개 embodiment × 6개 실제 task: dual-arm 그리퍼 (Galaxea R1 Lite: Unscrew Bottle Cap, Organize Box / Tianji Marvin: Sort Fruits, Put Items to Bag and Zip) + 다지 손 (Marvin + 20-DoF WUJI hand: Pour Water, Grasp with a Clamp). 모든 셋업은 3개 `384×384` 시점(head ZED 2i + wrist Insta360 GO 3S 2개). task 당 100 in-domain 로봇 teleop + 50 OOL Glove 시연, task 당 20 rollout 평가. baseline 은 LaST0(latent-CoT VLA), $`\pi_{0.5}`$(강력 VLA 정책), Cosmos-Policy(world-action 모델).

### In-domain 결과 (Table 1)

> "both LaST-HD variants achieve the highest average success rates across six complex tasks." (§4.2, Table 1)
(LaST-HD(100 robot)와 LaST-HD Mix-HD(50 robot + 50 glove) 모두 평균 최고 성공률. 특히 multi-step task 와 high-DoF 다지 조작에서 격차가 벌어집니다.)

| Method | Unscrew Cap | Organize Box | Sort Fruits | Put & Zip | Pour Water | Grasp Clamp | Avg |
|---|---|---|---|---|---|---|---|
| $`\pi_{0.5}`$ | 0.70 | 0.70 | 0.85 | 0.75 | 0.30 | 0.40 | 0.62 |
| Cosmos-Policy | 0.75 | 0.50 | 0.85 | 0.60 | 0.20 | 0.20 | 0.52 |
| LaST0 | 0.80 | 0.70 | 0.75 | 0.60 | 0.40 | 0.50 | 0.63 |
| **LaST-HD** | 0.85 | 0.70 | **0.95** | 0.80 | **0.60** | 0.45 | **0.73** |
| LaST-HD (Mix-HD) | 0.85 | 0.70 | 0.85 | 0.80 | 0.40 | 0.45 | 0.68 |

(앞 2개 task = Galaxea R1 Lite, 가운데 2개 = Tianji Marvin, 뒤 2개 = Marvin + WUJI. Mix-HD 는 6개 중 4개에서 LaST-HD 와 동급 — 즉 OOL Glove 시연이 로봇 시연을 효과적으로 대체합니다.)

### 일반화 결과 (Table 2)

3개 일반화 시나리오(Position / Object / Background)의 **시나리오별 평균 + Global Avg**. "w/ unseen HD" = in-domain 로봇 100 + unseen 시나리오당 사람 손 60 시연으로 학습. 나머지는 in-domain 체크포인트의 zero-shot.

| Method | Position | Object | Background | Global Avg |
|---|---|---|---|---|
| $`\pi_{0.5}`$ (zero-shot) | 0.12 | 0.36 | 0.43 | 0.30 |
| Cosmos-Policy (zero-shot) | 0.13 | 0.28 | 0.38 | 0.26 |
| LaST0 (zero-shot) | 0.15 | 0.32 | 0.43 | 0.30 |
| LaST-HD Mix-HD (zero-shot) | 0.15 | 0.35 | 0.43 | 0.31 |
| LaST0 (w/ unseen HD) | 0.33 | 0.49 | 0.58 | 0.46 |
| **LaST-HD (w/ unseen HD)** | **0.41** | **0.58** | **0.68** | **0.56** |

> "LaST-HD (w/ unseen HD) improves the average success rate to 58%, outperforming the previous SOTA $`\pi_{0.5}`$ by 22% and showing that physical latent reasoning supports robust semantic understanding and adaptive contact patterns." (§4.2, Table 2)
(Unseen Object 에서 58% — zero-shot $`\pi_{0.5}`$(36%) 대비 22%p 향상. 저비용 사람 손 데이터만으로 새 시나리오 일반화를 끌어올린다는 핵심 주장의 근거입니다.)

### Human-Hand Online Correction (Figure 3a)

> "With 20 human-hand trajectories, the success rate reaches 100% for Unseen Background, while with 60 human-hand trajectories, it reaches 100% for Unseen Object." (§4.2)
(Sort Fruits 점진 평가: 60 trajectory 수집에 단 20분. Unseen Position 도 60%→80% 로 단조 증가.)

![Figure 3 — 온라인 보정 / 주요 ablation / attention map](https://arxiv.org/html/2606.23685/x3.png)

> "Figure 3: (a) Success rate under online correction with varying amounts of correction data. (b) Main ablation studies on LaST-HD design choices. (c) Visualization of latent-token attention maps." (§4.3)
(소량 사람 손 보정 데이터로 빠르게 적응하고, ablation·attention map 으로 설계 선택의 근거를 제시합니다.)

### Ablation (§4.3, Appendix D)

**잠재 정렬 전략 (Figure 3b 좌).** LaST-HD vs WM-only(action conditioning 없는 world-model 타깃) vs SigLIP(LaST0 식 미래 SigLIP 이미지 특징 타깃) vs W/o Latent(잠재 추론 제거).

> "removing latent reasoning causes a clear performance drop from 73% to 60%, showing that action-level co-training alone cannot fully exploit human-hand demonstrations." (§4.3)
(잠재 추론을 빼면 73%→60% — action-level co-training 만으로는 사람 손 데이터를 충분히 활용 못 함. action-conditioned world-model 타깃이 SigLIP·WM-only 대비 최고 성능.)

**데이터 소스 효과 (Table 5).** 동일 LaST-HD 레시피 하 60 시연 비교 (LaST-HD OOL Glove = 0.73 기준):

| 데이터 소스 | Real-60 | Real-12 | Bare hand | UMI | Palm view |
|---|---|---|---|---|---|
| Success Rate | 0.75 | 0.60 | 0.63 | 0.65 | 0.67 |

(OOL Glove 0.73 은 vision-based bare-hand 0.63 을 상회. 동일 수집 시간 기준 Real-12(0.60) 대비 +13%p, Real-60(0.75) 과 동급. 손목 카메라를 thumb-index web 공간 근처에 두면 palm-view(0.67)보다 우수. UMI(0.65)는 2-finger 라 다지 손 retarget 불가가 한계.)

**World-model denoising step (Table 6).** 2→0.73, 5→0.72, 10→0.76 — 차이 미미해 효율 위해 2-step 채택.

**Shared latent length (Table 7).** 2→0.67, 4→0.73, 8→0.67, 12→0.70, 16→0.78 — 16 이 최고지만 autoregressive 디코딩 지연 때문에 성능/효율 절충으로 **4** 채택.

---

## ⚖️ 한계

- **잠재 추론이 실시간이 아님(저자 명시).** autoregressive 잠재 CoT 가 추론 지연을 유발해 $`N_{\text{lat}}`$ 을 4로 제한할 수밖에 없습니다(16이 최고 성능). 저자는 fast-slow 시스템 설계나 추가 잠재 압축을 future work 로 제시합니다. 동적·접촉 집약 task 에서 지연은 곧 실패로 이어질 수 있어, 잠재 추론의 비용이 실배치를 제약하는 구조적 약점입니다.
- **다지 손 task 의 낮은 천장.** Grasp Clamp 는 in-domain 에서도 0.45 에 그치고, 실패 분석은 grasp point 선택 부정확·접촉력 부정확으로 인한 object slipping 을 지목합니다. world model 이 시각 위주로 학습되어 **접촉력/마찰 같은 미세 동역학을 잠재에 담지 못하는** 한계로 읽힙니다.
- **유체 task 의 예측 불가성(저자 명시).** Pour Water 는 흐르는 액체의 stochastic 동역학을 예측하기 어려워 spilling 으로 실패합니다 — forward-dynamics 잠재가 강체 운동에 맞춰져 있어 유체로 외삽되지 않는다는 신호입니다.
- **embodiment 별 heuristic retargeting(저자 명시).** 현재 hand-to-robot retargeting 은 손마다 수작업 heuristic 사상이라 새 로봇 손마다 새 retargeting 파이프라인을 구축해야 합니다. 저자도 retargeting 품질이 사전학습·SFT 전반에 critical 하다고 인정하며, learnable retargeting 을 future work 로 둡니다 — 새 하드웨어 도입 비용이 높습니다.
- **공정성을 위한 데이터 비대칭(추론된 갭).** baseline 과의 공정 비교를 위해 MoT 모델은 로봇 데이터로만 사전학습되지만, 누적된 2,000시간 이상 OOL Glove 데이터를 사전학습에 넣은 full-스케일 성능은 보고되지 않습니다. 장치의 진짜 상한은 미공개입니다.
- **world model 의 target-embodiment 의존(추론된 갭).** "사전학습에 target-embodiment 데이터를 포함하면 충분"하다는 것은, 역으로 사전학습 분포 밖 embodiment 에는 정렬 타깃 품질이 보장되지 않는다는 뜻입니다.

---

## ♻️ 재현성

- **코드/가중치** — 공개 GitHub/HuggingFace 저장소는 본문·초록에서 확인되지 않습니다. Project page (`https://siriyep.github.io/last-hd-project-page/`) 만 제시됩니다. 코드/가중치 공개 여부 불명.
- **데이터** — OOL Glove 인간 손 데이터셋(2,000시간 이상, Table 4: 가사 45.7% / 정밀 1.6% / 변형체 49.3% / 모바일 조작 3.4%)은 **"향후 고품질 데이터셋 공개 예정"**으로만 언급되어 현재 미공개입니다. 사전학습 혼합(Table 3, OXE/DROID/RoboMIND 계열)은 공개 데이터셋 조합입니다.
- **하드웨어** — OOL Glove 사양은 Appendix A 에 상세(6 IMU, 21 keypoint, 200 Hz, <10 ms, sub-mm RMS, <100 g)하나 제작 도면/BOM 은 제시되지 않습니다. 평가 로봇(Galaxea R1 Lite, Tianji Marvin, WUJI hand)·카메라(ZED 2i, Insta360 GO 3S)는 상용 부품.
- **모델 구성** — Janus-Pro + DeepSeek-LLM 1.5B(24-layer) + SigLIP-Large 로 명시. world model 은 [31] action-conditioned WM 을 fine-tune(U-Net 기반 video diffusion 추정). baseline 구현 세부는 Appendix F.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P5(action-conditioned world model 통합) — 주축.** LaST-HD 는 P5 의 핵심 변수 다수를 직접 건드립니다. `D28`(world-model 역할: latent dynamics prior / future-prediction auxiliary), `D29`(통합 아키텍처), `D30`(prediction space), `D31`(action conditioning), `D32`(egocentric hand-object WM). 다만 v1 D28 의 "정책과 **co-train**" 선택과 달리, LaST-HD 는 WM 을 **frozen·offline-precompute 한 잠재 타깃 생성기**로 격리합니다 — VLA-JEPA 식 two-stage decoupled 경로(D29 변종)에 가깝되, action conditioning(D31)과 cross-embodiment 정렬을 더한 형태. prediction space 는 latent(D30 v1 과 일치), action-conditioned(D31 v1 과 일치). egocentric hand-object(D32)도 충족.
- **P0(VLA Datasets & Benchmarks).** `D24`(egocentric 인간 영상 우선 데이터축) — OOL Glove 가 정확히 그 축의 신규 수집 장치. `D27`(라이선스/사용성 기준) — 데이터셋·코드 미공개라 현재 카탈로그 적격성 미달.
- **P4(데이터 효율 적응 사전학습).** `D20`(prior-preservation 전략) — online correction 의 **balanced replay**($`|\mathcal{B}_{\mathrm{prev}}|=|\mathcal{B}_{\mathrm{dagger}}|`$, 1–2 epoch)가 망각 완화 레버. `D21`(staged 레시피) — mixed co-train → online correction 의 2단계 구조. `D22`(데이터 구성: egocentric vs mixed, **OPEN**) — LaST-HD 는 **mixed** 를 택하고 "50 robot + 50 glove ≈ 100 robot"(Table 1)를 보여 OPEN 질문에 직접 증거 제공. `D23`(action representation) — 플로우 매칭 head(v1 과 일치).
- **P1(이질적 Body/Hand action expert) — 비교군.** MoT 의 expert 분리는 **reasoning/action** 축이지 우리 Identity 의 **Body/Hand** 축이 아닙니다. 다지 손 행동 공간(`D3`, WUJI 20-DoF, $`\mathbb{R}^{54}`$)은 닿지만, 본 논문은 anatomical 분해를 다루지 않습니다.
- **Identity 긴장/지지** — VLA-level 에서 dexterity 를 다룬다는 점(world-model 잠재 정렬 + 사람 데이터 효율)은 P5/P0/P4 를 강하게 **지지**합니다. 반면 (a) 관측이 평면적 multi-camera + proprio 로 **P2 의 구조적 multimodal fusion·per-finger 촉각 결합 부재**, (b) **System0(P3) 부재**, (c) reasoning/action MoT 분리(≠ Body/Hand)라는 점에서 우리 핵심 thesis 와는 축이 다릅니다.
- **경쟁자 함의** — $`\pi_{0.5}`$(P4 핀)는 본 논문에서 baseline 으로 패배(in-domain 0.62 vs 0.73, global 일반화 0.30 vs 0.56). LaST0 는 같은 저자의 직전 작으로 가장 직접적 비교군(SigLIP 타깃 → WM 타깃 교체).

---

## ✨ 핀 논문 대비 델타

- **vs VLA-JEPA (P5 핀, [arXiv:2602.10098](https://arxiv.org/abs/2602.10098)).** 둘 다 latent-prediction WM 으로 정책을 leakage 인지적으로 지도합니다. 진정한 새로움: (1) LaST-HD 의 WM 은 **명시적 action-conditioned**(VLA-JEPA 의 JEPA 는 action-free 잠재 예측), (2) headline 이 **unpaired 인간↔로봇 cross-embodiment 정렬**(VLA-JEPA 는 단일 embodiment 의 카메라/배경 robustness).
- **vs DexWM (P5 top 핀, [arXiv:2512.13644](https://arxiv.org/abs/2512.13644)).** DexWM 은 인간 영상에서 손-물체 WM 을 학습해 finger-keypoint/hand-consistency 를 예측하는 predictive 모델. LaST-HD 의 WM 은 U-Net diffusion 미래-프레임 생성기를 **별도 VLA 의 reasoning expert 잠재 타깃 생성기로만** 쓰며, 추론 시 WM 은 행동을 계획·예측하지 않습니다.
- **vs Being-H0.7 (P5 핀, [arXiv:2605.00078](https://arxiv.org/abs/2605.00078)).** 둘 다 ego 데이터에서 잠재 추론. 새로움: LaST-HD 는 잠재 CoT 를 정책 자체의 잠재 rollout 이 아니라 **action-conditioned forward-dynamics 특징**(외부 WM)으로 지도하고, cosine 정렬 목적함수를 명시.
- **vs LaST0 ([51], 같은 저자 직전작).** LaST0 는 미래 **SigLIP 이미지 특징**(외형 진화)을 잠재 타깃으로 씁니다. LaST-HD 는 이를 action-conditioned WM forward-dynamics 특징으로 교체 → 물리 동역학 정렬 + cross-embodiment 가능. SigLIP ablation 이 정확히 이 A/B(LaST-HD > SigLIP 타깃 변종). (LaST0 의 arXiv id 는 본문에서 확인 불가라 표기 보류.)
- **vs EgoDex (P0 top 핀, [arXiv:2505.11709](https://arxiv.org/abs/2505.11709)).** EgoDex 는 Vision Pro 기반 vision 3D 손 추적(829시간). OOL Glove 는 **IMU 장갑 기반**(sub-mm RMS, 자체 ablation 에서 vision-based bare-hand 63% 대비 73%로 더 정밀)이고 그리퍼·다지 손 모두 retarget 가능(2,000시간+).
- **vs ConSFT (P4 핀, [arXiv:2605.08879](https://arxiv.org/abs/2605.08879)).** ConSFT 는 trust-region 보수적 importance-weighted SFT 로 망각을 줄입니다. LaST-HD 의 online correction 은 더 단순한 **balanced replay**(이전/신규 동량 샘플링, 1–2 epoch) — replay 기반 prior 보존이라는 다른 메커니즘.

---

## ⚙️ 의사결정 함의

- **WM 을 잠재 타깃으로 쓰는 구체적 레시피(P5 D30/D31).** 우리 stack 에 world model 을 보조로 넣는다면, LaST-HD 는 WM 의 action-conditioned forward-dynamics 특징(가장 깊은 U-Net layer, 마지막 denoising step)을 reasoning expert 의 **cosine 잠재 타깃**으로 쓰되 행동 예측엔 쓰지 말라(leakage)고 처방합니다. 구체 config: 기존 플로우 매칭 $`\mathcal{L}_{\mathrm{act}}`$ 에 $`\lambda\,\mathcal{L}_{\mathrm{latent}}`$(cosine) 추가; 잠재 길이 `N_lat = 4`(16이 최고이나 지연 절충); 타깃 추출 denoising step = 2(품질 손실 없이 데이터셋 구축 가속).
- **오프라인 precompute 통합(P5 D28/D29).** WM 을 frozen 으로 두고 잠재 타깃을 오프라인 계산하면 **co-training compute 없이** WM 통합이 가능 — v1 D28 의 "co-trained" 선택에 대한 구체적·저비용 대안 ablation 후보.
- **데이터 구성 OPEN 질문(P4 D22)의 증거.** mixed 인간-로봇 co-training(50 robot + 50 glove ≈ 100 robot, in-domain)은 사람 손 데이터를 섞어도 native 로봇 능력이 저하되지 않고 일반화가 오름을 보입니다 — egocentric-vs-mixed OPEN ablation 의 직접 데이터 포인트.
- **deploy 적응 망각 레버(P4 D20).** balanced replay($`|\mathcal{B}_{\mathrm{prev}}|=|\mathcal{B}_{\mathrm{dagger}}|`$, 1–2 epoch)를 ConSFT 보수적 SFT 와 비교할 후보 — 단순하고 구현 비용이 낮음.
- **데이터 수집 옵션(P0 D24).** OOL Glove 식 IMU 장갑(retarget 가능, teleop 대비 4–5배 빠름)은 in-house ego 수집 계획의 한 옵션 — EgoDex 식 vision-based Vision Pro 와는 다른 정밀도/비용 프로파일.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 체크) 촉각/힘 부재.** LaST-HD 는 vision(3 RGB) + proprio 만 쓰고, 우리 차별점인 per-finger proprio-tactile 결합(P2)·System0 접촉 안정화(P3)가 없습니다. Grasp Clamp 0.45 와 실패 분석(object slipping, 부정확 접촉력)은 정확히 우리 System0 가 겨냥하는 retention 문제. **체크: 관측에 촉각 토큰을 추가했을 때 vision 으로 학습된 WM 잠재 타깃이 그 정보를 반영하는가, 아니면 무시하는가.**
- **WM 의 target-embodiment 의존.** "사전학습에 target embodiment 포함 시 충분"은 곧 분포 밖 손(Sharpa 22-DoF)에는 정렬 타깃 품질 미보장. **체크: deploy embodiment 가 WM 사전학습에서 빠졌을 때 오프라인 잠재 타깃 품질이 어떻게 저하되는가(소규모 holdout).**
- **손마다 heuristic retargeting.** 새 로봇 손마다 retargeting 파이프라인 신규 구축이 필요하고 품질이 SFT 에 critical. Sharpa Hand 로 21 keypoint → 관절 IK retarget 은 비자명. **체크: 글러브 데이터에 투자하기 전, 소수 Sharpa grasp 의 retargeting RMS 부터 측정.**
- **잠재 추론 비실시간 × System0.** autoregressive 잠재 CoT 지연(저자가 `N_lat` 을 4로 제한한 이유)은 sub-policy-loop 반응이 필요한 System0 와 충돌. **체크: fast-slow 분리 없이 잠재 CoT 와 System0 빠른 루프가 공존 가능한가.**
- **lineage 불일치.** LaST-HD 는 Janus-Pro + DeepSeek-LLM 1.5B 기반으로, 우리 PaliGemma×π0(P4 D19) lineage 와 다릅니다. shared-attention reasoning/action MoT 설계가 π0 위로 깔끔히 이식되지 않을 수 있음. **체크: action expert 재학습 없이 reasoning expert 를 π0 에 bolt-on 할 수 있는가.**

---

## 💡 컨텍스트 제안

- **P5 §5 methodology base 후보.** LaST-HD 는 action-conditioned 잠재 WM 을 **오프라인 잠재-지도 타깃**으로 쓰는 구체적 인스턴스(co-training 과 구별되는 decoupled D28/D29 변종)이고, 인간↔로봇 cross-embodiment 정렬 각도는 현 8개 핀 전부와 다릅니다. 핀 cap(8)이 꽉 차 있으므로 핀 교체가 아니라 **methodology base(non-pinned)** 등재를 제안합니다.
- **P0 미공개 추적 항목.** OOL Glove + 예고된 2,000시간 인간 손 데이터셋은 공개 시 `catalogs/datasets.md`(👤 human) 등재 후보 — 현재 미공개라 카탈로그 미적격(그래서 본 분석은 `카탈로그` 라우팅을 비웁니다). vision-based EgoDex 와 구별되는 **glove 기반 수집** 옵션으로 메모.
- **P4 D22 OPEN ablation 데이터.** LaST-HD 의 mixed≈robot-only(in-domain) 증거는 D22 의 egocentric-vs-mixed deferred 논의에 인용할 만한 구체 데이터 포인트.
- 위 제안은 모두 사람 검토용이며, 본 분석은 `context/` 파일을 수정하지 않습니다.
