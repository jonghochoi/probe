# Paper Analysis — KineFuse: Kinematic-Aware Haptic Fusion for In-Hand Occluded-Object Pose Tracking

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | KineFuse: Kinematic-Aware Haptic Fusion for In-Hand Occluded-Object Pose Tracking |
| 저자 | Chanyoung Ahn, Jaesung Lee, Sungwoo Park, Donghyun Hwang |
| 링크 | [arXiv:2607.14842](https://arxiv.org/abs/2607.14842) · [Website](https://cold-young.github.io/kine-fuse/) |
| 발행일 / 버전 | 2026-07-16 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-07-21 |
| 관련 Pillar | P2, P3 |
| 태그 | tactile, force, dexterity |

---

## 🧭 한 줄 요약 (TL;DR)

In-hand 조작 중 손가락이 물체를 가리는 self-occlusion 상황에서, 이미 손에 존재하는 희소한 haptic 신호(proprioception·근위 F/T·binary contact)를 **손의 kinematic 구조를 보존하는 finger-level 토큰**으로 인코딩해 frozen 시각 pose tracker(FoundationPose)에 융합하면, per-frame 에서는 안 보이던 인코더 품질 차이가 sequential tracking 에서 최대 15배까지 증폭되어 occlusion 하 6D pose 추적과 downstream 조작 성공률을 크게 끌어올린다는 것을 보인 논문입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — Dexterous in-hand 조작은 연속적인 6D pose 추적을 요구하지만, 물체를 조작하는 바로 그 손가락이 카메라 시야에서 물체를 가려(self-occlusion) 시각 pose 추정이 정밀 제어가 가장 필요한 순간에 열화됩니다.
- **기존 접근의 한계** — 이를 multi-camera rig 나 가림이 적은 task 설계로 우회하면 하드웨어/파지 레퍼토리가 제약되고, GelSight·DIGIT 같은 dense 비전-촉각 센서에 의존하는 융합은 특수 하드웨어를 요구합니다. 다관절 손에 이미 있는 단순 haptic 신호(관절 proprioception·contact·F/T)는 접근성이 높지만, 쓰이더라도 대개 **flat vector 로 concat 되어** 센싱 지점 간 kinematic·공간 관계를 버립니다.
- **본 논문의 가설** — 핵심 질문은 "haptic 을 더할지"가 아니라 "**희소 haptic 을 어떻게 구조화할지**"이며, 손의 kinematic 구조(URDF)를 인코딩 단계에서 보존하면 occlusion robustness 가 개선된다는 가설입니다.
- **왜 지금 중요한가** — FoundationPose·BundleSDF 같은 강력한 시각 backbone 이 존재하지만 in-hand regime 의 약점을 그대로 노출하며, 최근 연구들이 최소 contact 신호조차 적절히 넣으면 occlusion 하 추정을 돕는다고 시사합니다. 평가 방법론(per-frame vs sequential)의 선택이 인코더 우열 판단 자체를 좌우한다는 점도 지금 짚어야 할 지점입니다.

---

## 🧩 핵심 기여

- **Kinematic-aware haptic encoder + 5-way ablation** — 희소 haptic 신호를 위한 URDF-aware finger-level 인코더를 제안하고, 점진적으로 kinematic 구조를 도입하는 5개 인코더 설계(Naive / FingerMLP / 16-token / KineFuse 등)를 체계적으로 비교합니다.
- **URDF spatial bias 를 갖춘 compact 4-token 표현** — 손가락 단위로 pooling 한 4개 토큰 + URDF 파생 그래프 bias 표현이 flat fusion 및 joint-level(16-token) 표현을 모두 능가함을 보입니다.
- **평가 레벨에 따른 gap 증폭 발견** — per-frame(1.12배)에서는 구분되지 않던 아키텍처 차이가 sequential tracking 에서 2배, downstream 조작에서 15배로 증폭되어, sequential 평가가 융합 아키텍처 평가에 필수임을 확립합니다.
- **학습된 융합 행동의 해석** — 구조화된 인코더가 명시적 감독 없이 **task-specific cross-modal gating** 을 학습함을 발견합니다: translation 은 vision 에만 의존하고 rotation 은 하나의 attention head 를 haptic 에 전담시킵니다.
- **downstream 검증** — 개선된 추적이 tool reorientation RL task 의 성공률을 높임을 보이고, 실세계 정성 데모를 제공합니다.

---

## 🔑 기술 키워드

- **FoundationPose** — CAD 모델 기반 render-and-compare 6D pose 추정/refinement 네트워크. 본 논문에서 frozen 시각 backbone 으로 그대로 재사용됩니다.
- **Render-and-compare refinement** — 현재 pose 가설로 mesh 를 렌더한 crop 과 관측 RGB-D crop 을 비교해 pose delta 를 회귀하는 방식. tracking 시 이전 프레임 추정을 초기 가설로 씁니다.
- **Finger-level tokenization** — 16개 관절 토큰을 손가락 4개 요약 토큰으로 압축하는 표현. "flat vector 대신 손 단위로 요약한다"는 아이디어의 핵심 단위입니다.
- **Intra-finger attention** — 같은 손가락 4관절 안에서만 attention 을 허용하는 마스크. 원위(fingertip) 센싱 신호를 F/T 센서가 없는 근위 관절로 전파시킵니다.
- **Cross-attention pooling** — learnable query 가 손가락별 관절 토큰을 attend 해 단일 요약 토큰을 뽑는 압축(16→4). 평균 대신 학습된 가중 요약입니다.
- **Graphormer** — 그래프 구조를 attention bias 로 주입하는 transformer 계열. 손가락 간 관계를 URDF 기하로 편향시키는 데 사용됩니다.
- **URDF spatial bias** — 손가락 쌍의 hop distance·opposition·adjacency 같은 손 기하 특성을 attention bias term 으로 변환. "엄지-검지가 마주본다" 같은 해부학적 관계를 모델에 알려주는 사전정보입니다.
- **6D pose tracking** — $`SE(3)`$ (translation 3 + rotation 3) 물체 자세를 프레임마다 이어 추정하는 문제. 오차가 프레임 간 누적되는 것이 핵심 난점입니다.
- **Norm dominance** — 한 모달리티의 토큰 norm 이 커져 다른 모달리티(vision)를 억눌러버리는 실패 양상. flat/joint-level 표현이 vision 을 억누르는 원인으로 지목됩니다.
- **Cross-modal gating** — 출력 성분(translation/rotation)별로 어느 모달리티를 얼마나 쓸지 attention 이 스스로 배분하는 현상. 본 논문이 감독 없이 창발함을 관찰합니다.

---

## 🔬 방법론

### 직관

문제는 단순합니다. 손으로 물체를 돌리는 동안 카메라는 손가락에 가려 물체를 제대로 못 봅니다. 그런데 손 자체는 관절 각도, 손끝 접촉 여부, 일부 관절의 힘/토크 같은 신호를 이미 알고 있습니다. 이 신호들을 "물체가 지금 대략 어디 있는지"의 힌트로 쓰면 가림에도 자세를 이어 추적할 수 있습니다. KineFuse 는 시각 tracker(FoundationPose)는 그대로 얼려 두고, 이 haptic 힌트를 인코딩하는 작은 모듈만 새로 붙입니다.

핵심 주장은 "haptic 을 더하느냐"가 아니라 "**어떻게 구조화하느냐**"입니다. 관절 16개를 그냥 한 벡터로 이어 붙이면(flat concat) 손의 형태 정보가 뭉개집니다. 대신 손의 kinematic 구조를 살려서 — 같은 손가락 안에서 정보를 먼저 나누고(intra-finger), 손가락 단위로 요약하고(4 토큰), 손가락 사이 관계는 URDF 기하로 편향된 그래프 attention 으로 처리 — 인코딩합니다. 손끝에만 있는 힘 센서 신호가 같은 손가락의 힘 센서 없는 관절로 자연스럽게 흐르게 하는 것이 intra-finger 마스크의 목적입니다.

또 하나의 통찰은 평가입니다. 저자들은 한 프레임만 보정하는 per-frame 평가로는 인코더 품질 차이가 거의 안 드러나지만(1.12배), 프레임을 이어 추적하면 작은 오차가 누적되어 차이가 2배로, 조작 성공률에서는 15배로 벌어진다는 것을 보입니다. 즉 융합 아키텍처의 우열은 sequential 조건에서만 제대로 보입니다.

마지막으로, 학습된 모델은 명시적 지시 없이도 "translation 은 vision 만, rotation 은 haptic 을 전담 head 로" 쓰는 물리적으로 해석 가능한 분업을 스스로 찾아냅니다.

### 아키텍처

**입력/출력.** 외부 tracking 시스템 없이 외부 RGB-D 카메라 하나로 in-hand 6D pose 를 추적합니다.

> "At each timestep $`t`$, the system receives an RGB-D observation $`I_{t}`$ and a sparse haptic observation $`h_{t}`$, and predicts the object pose $`\hat{T}_{t}\in SE(3)`$ in the camera frame." (§III-A)
> (매 스텝 RGB-D 관측과 희소 haptic 관측을 받아 카메라 좌표계의 물체 자세를 예측합니다. haptic 은 $`J`$-관절 손에서 $`\tau`$ 스텝 히스토리로 수집되어 $`h_{t}\in\mathbb{R}^{J\times\tau\times C}`$ 로 표현됩니다.)

셋업은 $`J{=}16`$, $`\tau{=}4`$ 입니다. 모든 관절은 proprioception(관절 위치 $`q`$ ·속도 $`\dot{q}`$)을 제공하고, 손끝에는 binary contact, 일부 지골 관절만 3축 근위 F/T 를 측정 가능 여부 flag 와 함께 제공합니다. F/T 를 갖춘 관절 집합은 $`\mathcal{S}_{\mathrm{FT}}\subset\{1,\dots,J\}`$ 이며 본 손에서는 4개 관절만 여기 속합니다 — 이 이질적 센싱 배치(관절 proprioception + 손끝 contact + 소수 관절 힘)가 "sparse haptic regime" 을 정의하고 구조화 인코딩의 동기가 됩니다. 알려진 물체 CAD 모델과 hand–eye calibration 을 가정합니다.

**시각 backbone.** FoundationPose refinement 네트워크를 그대로 씁니다. 현재 pose 가설 $`\tilde{T}_{t}`$ 로 mesh 를 렌더하고 관측 RGB-D 와 render-and-compare 하여, 공유 CNN 으로 시각 토큰 $`\mathbf{v}_{t}\in\mathbb{R}^{L\times D}`$ ($`L=400`$, $`20{\times}20`$ grid; $`D=512`$)을 만듭니다.

![Figure 2 — KineFuse 전체 파이프라인](https://arxiv.org/html/2607.14842/fig/f2_overview.png)

> "Figure 2: KineFuse framework. A shared visual encoder produces $`L{=}400`$ tokens from rendered and observed RGB-D crops; the Finger Graph Encoder maps 16-joint haptic signals to $`K{=}4`$ finger tokens. Both are concatenated and decoded by separate translation and rotation heads." (§III)
> (시각 토큰 400개와 haptic 4토큰을 concat 한 뒤 translation·rotation 두 head 로 분리 디코딩하는 것이 전체 구조임을 시각화합니다.)

**Haptic 인코더 (5-way).** 점진적으로 kinematic 구조를 도입하는 5개 설계를 비교합니다.

![Figure 3 — Haptic Graph Encoder 변형들](https://arxiv.org/html/2607.14842/fig/f2-1_ablation.png)

> "(a) Naive concatenates all joint features into a single token via linear projection; (b) FingerMLP groups joints by finger and applies per-finger MLPs followed by cross-finger self-attention, producing 4 tokens without kinematic bias; (c) 16-token applies intra-finger and inter-finger attention at the joint level without pooling, retaining all 16 tokens; (d) KineFuse (Ours) adds intra-finger attention, learned cross-attention pooling (16 $`\to`$ 4), and URDF-aware inter-finger graph attention." (§III-C)
> (a→d 로 갈수록 kinematic 구조가 더해집니다. 모든 변형은 동일한 관절 tokenization·융합 구조를 공유하고 haptic 인코딩만 다릅니다.)

KineFuse 인코더는 네 단계입니다.

1. **Joint tokenization** — 관절 $`j`$ 의 $`\tau`$-스텝 히스토리를 $`x_{t}^{(j)}\in\mathbb{R}^{28}`$ 로 flatten 하고 공유 2-layer MLP + LayerNorm 으로 토큰 공간에 매핑합니다.

$$\hat{z}_{t}^{(j)}=W_{2}\,\phi\!\left(\mathrm{LN}(W_{1}x_{t}^{(j)})\right)$$

여기서 $`W_{1}:\mathbb{R}^{28}\!\to\!\mathbb{R}^{512}`$, $`W_{2}:\mathbb{R}^{512}\!\to\!\mathbb{R}^{512}`$, $`\phi`$ 는 GELU 입니다. 그 뒤 learnable finger-identity·within-finger position 임베딩을 더해 관절 토큰 $`\mathbf{z}_{t}^{(0)}\in\mathbb{R}^{J\times 512}`$ 를 만듭니다.

$$z_{t}^{(j)}=\hat{z}_{t}^{(j)}+e_{\mathrm{finger}}(j)+e_{\mathrm{pos}}(j)$$

2. **Intra-finger attention** — finger-restricted 마스크로 두 self-attention layer 를 적용합니다.

$$\mathbf{z}_{t}^{(1)}=\mathrm{IntraAttn}(\mathbf{z}_{t}^{(0)};M_{\mathrm{finger}})$$

> "Each joint can attend only to the four joints of its own finger, allowing force and contact information available at distal sensing sites to propagate to proximal joints that lack direct force sensing." (§III-C)
> ($`M_{\mathrm{finger}}`$ 는 손가락 간 attention 을 차단하여, 손끝(원위) 센싱 신호가 힘 센서 없는 근위 관절로 전파되게 합니다 — sparse 센싱을 손가락 내부에서 메우는 장치입니다.)

3. **Finger-level pooling** — 손가락별 learnable query 가 그 손가락의 4개 관절 토큰을 cross-attention 으로 요약해 16→4 로 압축합니다.

$$\mathbf{f}_{t}=\mathrm{FingerPool}(\mathbf{z}_{t}^{(1)})\in\mathbb{R}^{4\times 512}$$

4. **Inter-finger graph attention** — 4개 손가락 토큰을 URDF 파생 spatial bias 를 더한 두 Graphormer-style layer(GET-Zero 의 embodiment-aware bias 설계 차용)로 처리합니다.

$$\mathbf{h}_{t}=\mathrm{InterAttn}(\mathbf{f}_{t};B)$$

$`B\in\mathbb{R}^{4\times 4\times H}`$ 는 학습된 multi-head attention bias 로, 각 손가락 쌍에 대해 URDF 에서 hop distance·opposition·adjacency 등 손 기하 특성을 뽑아 MLP 로 per-head bias 로 변환합니다. 최종 haptic 표현은 $`\mathbf{h}_{t}\in\mathbb{R}^{4\times 512}`$ 입니다.

### 학습 목표 / 손실

**융합.** 시각·haptic 토큰을 sequence 축으로 concat 합니다.

$$\mathbf{z}_{t}=[\,\mathbf{v}_{t};\mathbf{h}_{t}\,]\in\mathbb{R}^{(L+4)\times 512}. \quad (1)$$

이를 translation·rotation 각각의 single-layer transformer encoder 로 처리합니다.

$$\mathbf{z}_{t}^{\mathrm{trans}}=\mathrm{TransHead}(\mathbf{z}_{t}), \quad (2)$$
$$\mathbf{z}_{t}^{\mathrm{rot}}=\mathrm{RotHead}(\mathbf{z}_{t}). \quad (3)$$

각 sequence 를 mean-pool 후 출력 공간에 투영합니다.

$$\Delta\hat{\mathbf{t}}_{t}=\tanh\!\bigl(W_{\mathrm{trans}}\,\mathrm{mean}(\mathbf{z}_{t}^{\mathrm{trans}})\bigr)\odot\mathbf{n}_{t}, \quad (4)$$
$$\Delta\hat{\mathbf{r}}_{t}=W_{\mathrm{rot}}\,\mathrm{mean}(\mathbf{z}_{t}^{\mathrm{rot}}). \quad (5)$$

$`\Delta\hat{\mathbf{t}}_{t}\in\mathbb{R}^{3}`$ 는 translation update, $`\mathbf{n}_{t}`$ 는 단일 스텝 translation 크기를 제한하는 per-axis normalizer, $`\Delta\hat{\mathbf{r}}_{t}\in\mathbb{R}^{6}`$ 는 6D 표현의 rotation update 입니다. 두 update 모두 현재 가설의 egocentric frame 에서 예측되며, 최종 pose 는 합성 $`\hat{T}_{t}=\Delta\hat{T}_{t}\circ\tilde{T}_{t}`$ 로 얻습니다. 추론 시 2회 연속 refinement 를 적용하고, tracking 중 초기 가설은 이전 프레임 추정 $`\tilde{T}_{t}=\hat{T}_{t-1}`$ 입니다.

**Gating 을 버린 이유.** codebase 는 gated dual-head(haptic-only branch)를 지원하지만 채택하지 않았습니다.

> "we found that the confidence gate consistently saturated toward the haptic-only head, blocking visual gradients and collapsing to unimodal prediction." (§III-D)
> (confidence gate 가 haptic-only head 로 saturate 되어 시각 gradient 를 막고 unimodal 예측으로 붕괴했기 때문에, 보고된 결과는 모두 gating 없는 direct fusion 출력을 씁니다 — 융합 설계에서 명시적 gate 가 오히려 해로울 수 있다는 실전 관찰입니다.)

**손실.** 전체 목적은 pose MSE + ADD + 두 보조 기하 항입니다.

$$\mathcal{L}=\mathcal{L}_{\mathrm{pose}}+\lambda_{\mathrm{ADD}}\,\mathcal{L}_{\mathrm{ADD}}+\lambda_{\mathrm{attr}}\,\mathcal{L}_{\mathrm{attr}}+\lambda_{\mathrm{pen}}\,\mathcal{L}_{\mathrm{pen}}. \quad (6)$$

$`\mathcal{L}_{\mathrm{pose}}`$ 는 egocentric translation·rotation delta 의 MSE, $`\mathcal{L}_{\mathrm{ADD}}`$ 는 표준 ADD(Average Distance of Distinguishable model points) 손실, $`\mathcal{L}_{\mathrm{attr}}`$ 는 의도된 contact 영역 근처의 hand–object 근접성 유도, $`\mathcal{L}_{\mathrm{pen}}`$ 은 mesh 상호침투 penalty 입니다. 계수 $`\lambda_{\mathrm{ADD}},\lambda_{\mathrm{attr}},\lambda_{\mathrm{pen}}`$ 의 구체 값은 원문에 명시되지 않았습니다.

### 학습 셋업

**Two-stage 학습.**

> "In Stage 1, we pretrain the haptic encoder with a haptic-only pose prediction objective, ensuring that the haptic tokens carry a meaningful sparse-haptic representation before fusion." (§III-E)
> (Stage 1 에서 haptic 인코더를 haptic-only pose 예측으로 사전학습해 융합 전에 haptic 토큰이 의미 있는 표현을 갖게 합니다.)

Stage 2 에서는 pretrained FoundationPose 시각 가중치 + Stage 1 haptic 인코더를 결합해 전체 모델을 fine-tune 합니다. Stage 2 의 처음 3 warmup epoch 동안 시각 backbone 을 freeze 하고 이후 전 파라미터를 공동 최적화하며, **haptic branch 는 시각 backbone 대비 2.5배 학습률**을 씁니다.

**학습 pair.** FoundationPose refinement 프로토콜을 따라 GT pose $`T_{t}^{*}`$ 를 egocentric noise(rotation $`[1^{\circ},10^{\circ}]`$, translation $`[0.002,0.01]`$ m)로 교란해 가설 $`\tilde{T}_{t}`$ 를 만들고, 모델은 $`\tilde{T}_{t}`$ 를 $`T_{t}^{*}`$ 로 refine 하는 residual delta 를 예측합니다.

**데이터·augmentation.** IsaacLab 에서 clean·physically-occluded 조건의 in-hand reorientation trajectory 로 수집합니다. 관측 RGB-D 에 synthetic 직사각형 occlusion 을, force 채널에 domain randomization(multiplicative scaling·additive offset·Gaussian noise·stochastic dropout)을 적용합니다.

---

## 📊 실험 설정과 결과

**공통 셋업.** 모든 모델(V-only FoundationPose baseline 포함)은 동일한 학습 스케줄·데이터·augmentation 으로 fine-tune 되고 haptic 인코더만 다릅니다. position 오차(cm)·angular 오차(도)·ADD(cm)를 보고합니다. Task success 는 300 스텝 에피소드당 tip-target 정렬(2 cm·15도 이내) 성공 횟수 평균입니다. 하드웨어는 16-DOF 4-finger dexterous hand(손가락당 4관절), 손끝 4관절만 3축 F/T + binary contact, 손목 장착 RGB-D(실세계 RealSense D435i), 조작 물체는 CAD 알려진 pencil 형태입니다. 학습/정량 평가는 모두 IsaacLab 에서, clean(~2,000 frame)·occluded(~1,000 frame) 데이터로 수행합니다. 평가 시 물체 영역 중심으로 약 0/10/30/50/70/90 % 면적을 가리는 synthetic 직사각형 마스크를 sweep 합니다.

**Sequential open-loop tracking (Table I).** 프레임 $`t`$ 의 추정이 $`t{+}1`$ 을 초기화하여 오차가 누적됩니다.

> "KineFuse achieves 4.04 cm mean position error (2 times lower than V-only's 8.11 cm) and maintains constant angular error at 47.6 degrees $`\pm`$ 0.1 degree regardless of occlusion level, while V-only fluctuates between 54.9 and 79.4 degrees." (§IV-B, Table I)
> (KineFuse 는 모든 occlusion 레벨에서 최저 position 오차를 유지하며, occlusion 과 무관하게 각도 오차를 47.6도로 일정하게 유지합니다. V-only 는 각도가 54.9–79.4도로 요동칩니다.)

| Model | Metric | 0% | 10% | 30% | 50% | 70% | 90% |
|---|---|---|---|---|---|---|---|
| V-only | Pos (cm) | 8.30±.51 | 6.80±.25 | 9.12±.54 | 7.59±.45 | 9.68±.73 | 7.14±.44 |
| V-only | Ang (°) | 59.9±3.2 | 64.2±3.4 | 57.7±3.4 | 60.6±3.5 | 54.9±1.3 | 79.4±3.7 |
| Naive | Pos | 8.30±.04 | 7.76±.18 | 9.13±.21 | 10.1±.17 | 7.01±.20 | 5.57±.19 |
| Naive | Ang | 48.0±1.1 | 47.3±1.1 | 47.9±1.5 | 47.7±1.3 | 50.8±1.2 | 53.7±1.4 |
| FingerMLP | Pos | 5.01±.23 | 5.46±.32 | 5.35±.28 | 6.07±.34 | 4.84±.24 | 6.50±.62 |
| FingerMLP | Ang | 49.2±4.2 | 52.8±5.1 | 49.7±3.8 | 50.9±4.3 | 47.0±1.8 | 67.6±4.2 |
| 16-token | Pos | 5.84±.08 | 5.84±.08 | 5.81±.08 | 5.79±.08 | 5.80±.08 | 5.79±.08 |
| 16-token | Ang | 69.2±1.3 | 69.3±1.3 | 69.3±1.3 | 69.3±1.3 | 69.3±1.3 | 69.2±1.3 |
| **KineFuse** | Pos | **3.68±.14** | **3.49±.10** | **3.47±.12** | **4.17±.06** | **4.33±.06** | **5.11±.07** |
| **KineFuse** | Ang | **47.7±2.7** | **47.7±2.7** | **47.6±2.7** | **47.7±2.7** | **47.6±2.7** | **47.6±2.7** |

- **읽기** — position 에서 KineFuse 가 전 구간 최저이고, occlusion 이 40 % 를 넘어 vision-only 가 급격히 열화할 때 haptic-augmented 모델이 낮은 오차를 유지합니다. 흥미롭게 **16-token 은 position·angular 모두 occlusion 에 거의 불변**(각도 ~69.3도로 고착)인데, 이는 vision 을 사실상 무시하고 haptic 에만 의존해 "안정적이지만 나쁜" 지점에 갇혔음을 시사합니다(초록에서 지목한 norm dominance 로 vision 억압). Naive 는 각도는 안정화하나 position 은 V-only 수준이거나 더 나쁩니다.

**Gap 증폭 (기여 2).**

> "architectural differences invisible at the per-frame level (1.12 times) amplify to 2 times in tracking and 15 times in manipulation—establishing that sequential evaluation is necessary for meaningful assessment of fusion architectures." (§I)
> (per-frame 1.12배 → tracking 2배 → manipulation 15배. 한 프레임 refinement 로는 융합 아키텍처 우열을 구분할 수 없다는 방법론적 결론입니다.)

**Downstream manipulation (Table II).** 별도 학습한 RL reorientation policy 의 GT pose 관측을 추정 pose 로 대체합니다(policy 고정, pose source 만 교체). 단위는 에피소드당 성공 횟수.

| Pose Source | 0% | 10% | 30% | 50% | 70% | 90% |
|---|---|---|---|---|---|---|
| GT (upper bound) | 21.25 | — | — | — | — | — |
| V-only | 0.46±.16 | 0.63±.06 | 0.83±.24 | 1.58±.34 | 1.97±1.0 | 1.52±.18 |
| Naive V+H | 1.54±.47 | 1.40±.55 | 1.86±.58 | 1.53±.53 | 1.75±.40 | 2.00±.29 |
| FingerMLP | 1.63±.06 | 0.61±.14 | 0.79±.67 | 1.48±.19 | 5.04±2.1 | 2.45±.38 |
| 16-token | 0.27±.04 | 0.23±.03 | 0.33±.05 | 0.30±.04 | 0.29±.05 | 0.30±.10 |
| **KineFuse** | **4.61±1.3** | **4.47±1.4** | **4.72±.42** | **4.47±.83** | **5.10±.28** | **3.81±.85** |

> "cumulative tracking drift remains the primary bottleneck, reducing overall success to 9% of the ground-truth upper bound" (§IV-C)
> (KineFuse 가 전 occlusion 구간에서 최고 성공을 내지만, 누적 tracking drift 가 여전히 주요 병목이라 GT 상한 대비 9 % 수준에 머뭅니다. drift 를 temporal regularization·re-initialization 으로 다루는 것은 future work 로 남깁니다.)

- **읽기** — KineFuse 는 downstream 에서 V-only 대비 대략 3–10배 성공을 내며, 여기서 15배 gap 증폭이 가장 극적으로 드러납니다. 특히 **16-token 은 downstream 에서 최악(≈0.3)** 으로, tracking 에서 "안정적으로 나쁜" 표현이 조작에는 완전히 무용함을 보입니다. FingerMLP 는 70 % 에서 5.04 로 튀는 등 분산이 커 구조적 bias 없는 4-token 이 불안정함을 시사합니다.

**Ablation — 구조 vs 정보 기여 (§IV-D).** 추론 시 haptic 채널을 전부 0 으로 만들어도 성능이 유지되는지를 봅니다.

> "The result—nearly identical tracking to the full model, yet 2.3 times better than V-only provides direct evidence that the contribution is structural" (§IV-D)
> (haptic 을 0 으로 해도 full 모델과 거의 동일하고 V-only 보다 2.3배 좋습니다. 즉 기여의 상당 부분이 런타임 contact 내용이 아니라 **학습 시 kinematic topology 가 부여한 inductive bias**에서 오며, 이 bias 가 fusion transformer 의 visual attention 조직 방식을 재편해 haptic 제거 후에도 지속됩니다.)

- **함의** — 저자 주장: haptic 데이터로 한 번 학습해두면 센서 고장·새 end-effector 로 haptic 이 일시 부재해도 성능 저하 없이 배포 가능. cross-modal gating 관찰(Fig. 8): translation 은 100 % vision, rotation 은 75/25 % vision/haptic 로 attention 을 배분합니다.

**실세계 데모 (Table III).** GT pose 가 없어 AprilTag 대비 pose 오차를 proxy 로 보고합니다. 두 모델 모두 스텝이 쌓이면 오차가 증가하나, 초·중반 KineFuse 가 V-only 대비 현저히 낮습니다(예: step 0 에서 trans 11.9 → 1.4 mm, rot 6.7 → 2.5도; step 135 에서 trans 108.2 → 35.9 mm). 다만 후반(step 269)에는 rot 오차가 역전(94.3 → 131.5도)되어 실세계 장기 drift 는 여전히 취약합니다.

![Figure 6 — Tracking drift (30% occlusion)](https://arxiv.org/html/2607.14842/fig/tracking_error.png)

> "Figure 6: Tracking drift. Position and angular error over 149 tracking steps at 30% occlusion. KineFuse (V+H) stabilizes after step 20, while V-only (FP) diverges continuously." (§IV-C)
> (KineFuse 는 step 20 이후 안정화되지만 V-only 는 계속 발산해, 개선의 본질이 "누적 drift 억제"임을 보여줍니다.)

---

## ⚖️ 한계

- **누적 drift 가 여전히 지배적 병목** — 저자 스스로 downstream 성공이 GT 상한의 9 % 에 그치고 drift 가 주 병목이라 밝힙니다. per-frame 정확도를 높여도 sequential 오차 누적 자체를 끊는 메커니즘(temporal filter·re-init·loop closure)이 없어, 실세계 Table III 에서 후반 rotation 오차가 오히려 V-only 를 역전하는 지점이 생깁니다. tracking 개선이 곧 "장기 안정 추적"을 뜻하지 않음을 보여주는 대목입니다.
- **기여가 구조적 bias 라는 발견의 양날** — "haptic 을 0 으로 해도 2.3배 좋다"는 결과는 강력하지만, 동시에 **런타임 haptic 신호가 실제로 기여하는 몫이 작다**는 뜻이기도 합니다. 즉 이 논문의 이득 상당 부분은 "URDF 위상을 attention bias 로 주입한 정규화 효과"이지 "실시간 촉각 융합"이 아닐 수 있어, 진짜 contact-driven 추적을 원하는 응용에는 그대로 전이되지 않을 위험이 있습니다.
- **단일 물체·단일 손 검증** — 정량 평가가 pencil 형태 단일 물체 + 16-DOF 4-finger 손 하나에 국한됩니다. URDF spatial bias·opposition 관계는 손 형상에 의존하므로, 손가락 수/토폴로지가 다른 손이나 대칭성이 낮은 물체로의 일반화가 미검증입니다.
- **Sim 중심·소규모 데이터** — 학습/정량 평가가 IsaacLab(clean ~2k + occluded ~1k frame)으로, 데이터 규모가 작고 sim contact 모델(PhysX)의 근위 F/T 가 실 센서 점탄성 변형과 다릅니다. force 채널 domain randomization 은 있으나 실세계 정량 GT 가 없어(AprilTag proxy) sim2real gap 이 정량화되지 않았습니다.
- **F/T 센싱이 4관절로 매우 희소** — intra-finger attention 으로 원위→근위 전파를 설계했지만, 애초에 힘 센서가 손끝 4곳뿐이라 "구조로 메운다"는 주장의 한계가 센서 배치에 종속됩니다. 더 조밀한 촉각(GelSight류)과의 직접 비교가 없어, 구조화의 이득이 하드웨어 희소성의 함수인지 방법 자체의 함수인지 분리되지 않습니다.

---

## ♻️ 재현성

- **코드/모델** — arXiv HTML 본문에 GitHub 코드 링크가 명시되지 않았고, project page([cold-young.github.io/kine-fuse](https://cold-young.github.io/kine-fuse/))만 제공됩니다. 본문은 "codebase 가 gated dual-head 를 지원한다"고 언급해 코드 존재를 시사하나 공개 여부/URL 은 미확인입니다.
- **데이터** — IsaacLab 에서 자체 수집(clean ~2,000 frame, occluded ~1,000 frame). 공개 데이터셋이 아니라 재현 시 시뮬레이션 재구성이 필요합니다.
- **하드웨어** — 16-DOF 4-finger dexterous hand(손끝 4관절 3축 F/T + contact), 손목 장착 RealSense D435i(실세계). 특정 상용 손 플랫폼으로 보이나 본문에서 모델명이 익명 처리되어 있습니다.
- **하이퍼파라미터** — 학습률 비(haptic 2.5×), warmup 3 epoch, noise 범위, normalizer([0.01]³ m) 등 일부는 명시되나 손실 계수 $`\lambda`$ ·optimizer·batch·epoch 총량은 미명시입니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P2(Structured Multimodal Observation Fusion) — 정중앙 타격.** 본 논문 전체가 P2 의 명제 "flat concat 을 넘어 손 구조를 보존한 융합"을 실증합니다.
  - **D10(heterogeneous modality fusion beyond concat)** — Naive(flat concat)가 vision 을 norm dominance 로 억압한다는 발견은 D10 v1 의 "cross-attention/asymmetric fusion, not flat concat" 선택을 직접 지지합니다. 또한 gated dual-head 가 haptic-only 로 붕괴했다는 관찰은 "modality dropout for graceful degradation" 설계에 경고를 줍니다(명시적 confidence gate 는 위험).
  - **D11(proprio-tactile-force token construction)** — per-finger 토큰(4 토큰) + swappable-head 지향은 D11 v1 의 "per-finger proprio-tactile binding, swappable sensor head + common token format" 과 일치합니다. haptic 부재에도 성능 유지(구조적 bias)는 D11 non-negotiable "센서 변경 흡수" 를 강하게 뒷받침합니다.
  - **D12(topology-aware encoding + hand-level aggregation)** — URDF 파생 hop/opposition/adjacency bias + finger-identity 임베딩 + finger-level self/graph attention 은 D12 v1 의 "full topology-aware encoding(finger/hand identity, kinematic chain) + self-attention hand-level aggregation" 을 거의 그대로 구현한 사례입니다. **KineFuse 는 사실상 D12 v1 의 외부 검증**입니다.
- **P3(Hand-level System0 Module) — 부차적 지지.** 평가에 IsaacLab RL reorientation policy(D17 RL policy spec 스택과 동일)를 쓰고, tactile+force+proprio 를 입력으로(D15 System0 input modality) 다루며, force 채널 domain randomization(D18 sim2real)을 적용합니다. 다만 본 논문의 핵심은 System0 안정화가 아니라 pose 추적이라 지지는 방법론 참조 수준입니다.
- **Identity 지지/긴장** — Identity 의 "structured multimodal observation fusion — per-finger proprio-tactile binding beyond flat concat" 을 정면으로 지지합니다. 긴장 요소는 "기여가 구조적 bias" 라는 발견이 "실시간 촉각이 dexterity 를 끌어올린다" 는 우리 서사와 미묘하게 어긋난다는 점입니다(아래 ⚠️).
- **경쟁자 함의** — P2 §5 pinned 의 **ViTacFormer**(cross-attention visuotactile)와 non-pinned **DexViTac**(kinematic-grounded tactile encoding)이 가장 가까운 선행연구입니다.

---

## ✨ 핀 논문 대비 델타

- **vs. DexViTac(P2 §5 non-pinned, kinematic-grounded tactile encoding)** — 가장 가까운 핀. 두 논문 모두 촉각을 kinematic 구조에 grounding 하지만, KineFuse 의 신규성은 (1) **5-way 인코더 ablation** 으로 "구조 유무 × 토큰 수" 를 분리해 4-token+URDF-bias 가 flat/joint-level 을 이긴다는 것을 인과적으로 보인 점, (2) **URDF 를 Graphormer attention bias 로 명시 주입**(hop/opposition/adjacency)한 점, (3) **평가 레벨별 gap 증폭(1.12→2→15배)** 이라는 방법론적 발견입니다.
- **vs. ViTacFormer(P2 pinned, cross-attention visuotactile)** — ViTacFormer 는 dense 촉각 이미지의 cross-attention 융합에 초점. KineFuse 는 정반대로 **희소·저차원 embodied haptic(관절 4곳 F/T)** 을 대상으로 하고, dense 센서 대신 URDF 위상 자체를 정보원으로 삼아 "센서가 희소해도 구조로 메운다" 를 보인 점이 델타입니다.
- **공통적 신규성** — "haptic 을 0 으로 해도 이득이 남는다(구조적 inductive bias)" 라는 분리 실험은 두 핀 어디에도 없는, 융합 이득의 출처를 해부한 결과입니다.

---

## ⚙️ 의사결정 함의

- **D12 를 "정보 융합" 이 아니라 "정규화용 구조 bias" 로 재해석** — KineFuse 의 구조적-기여 발견이 맞다면, 우리 fusion encoder 에서 topology-aware bias(finger-identity 임베딩 + URDF hop/opposition bias term)는 촉각 신호 품질과 무관하게 **그 자체로 vision attention 을 재편하는 정규화 항**으로 작동합니다. → 구체적으로: hand-level aggregation self-attention 에 URDF-derived per-head bias `B ∈ R^{(F×F)×H}` 를 추가 config 로 도입하고, 촉각 없는 baseline 대비 ablation 을 기본 실험에 포함.
- **평가 프로토콜을 sequential 로 전환** — per-frame(single-step) 지표만으로 융합 아키텍처를 고르지 말 것. 우리 pose/observation 실험도 **open-loop sequential rollout + downstream RL success** 를 1급 지표로 채택(단일 프레임 metric 은 인코더 우열을 1.12배로만 구분).
- **명시적 confidence gate 지양** — modality gating 을 넣을 때 haptic-only 붕괴(gradient 차단) 위험이 실증됨. → gating 대신 direct concat-fusion + modality dropout 을 기본값으로, gate 도입 시 vision gradient norm 을 모니터.
- **"swappable sensor head" 의 근거 강화** — 학습 후 haptic 부재에도 성능 유지 → D11 의 sensor-head 교체 흡수 설계가 실측 근거를 얻음. 새 손/센서 전환 시 재학습 없이 haptic 채널 zero-fill 로 graceful degradation 을 시도할 수 있다는 가설 추가.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 sanity check) 구조적-기여 재현** — 우리 데이터로 KineFuse 식 인코더를 학습한 뒤 추론 시 촉각을 0-fill 해 성능이 유지되는지부터 확인. 유지되면 이득은 정규화 효과이고, 무너지면 우리 셋업은 런타임 촉각 의존형이라 논문 서사와 다름. 이 한 줄 실험이 이후 방향을 가릅니다.
- **손 토폴로지 의존성** — URDF spatial bias 는 4-finger·opposition 구조에 맞춰짐. Sharpa/xhand 처럼 손가락 수·DOF·opposition 관계가 다른 손에서는 hop/adjacency 특성이 재정의되어야 하며, bias MLP 가 다른 위상에 재학습 없이 전이될지 미지수. → 우리 손 URDF 로 bias 특성을 다시 뽑아 소규모 학습으로 이득 부호를 먼저 확인.
- **F/T 희소성 mismatch** — 논문은 손끝 4관절 F/T. 우리 near-term 하드웨어는 Sharpa Deform Map(vision-based fingertip tactile ~320×240)로 신호 밀도·물리량이 완전히 다름. intra-finger 전파가 "메울" 대상 자체가 달라, dense tactile 을 4-token 으로 압축하는 것이 오히려 정보 손실일 수 있음. → dense tactile 을 finger token 으로 pooling 할 때 per-frame ADD 로 정보 손실 상한을 먼저 측정.
- **Sim2real·drift** — Table III 에서 장기 rotation 오차가 역전됨. 우리 목표(tool articulation, 정밀 tip 정렬)는 장기 안정 추적을 요구하므로, drift 억제 메커니즘 없이 per-frame 이득만 이식하면 downstream 에서 붕괴할 위험. → temporal regularization/re-init 부재 시 실패하는 구간을 rollout 길이로 스캔.
- **FoundationPose 의존** — 시각 backbone 을 FoundationPose(CAD-known render-and-compare)로 전제. 우리 스택이 π 기반 관측 인코더(CAD-free)로 간다면 이 융합 도식은 그대로 옮겨지지 않고, "render-and-compare 토큰" 이 없는 곳에서 haptic 4-token 을 어디에 concat 할지 재설계 필요.

---

## 💡 컨텍스트 제안

- **P2 §5 Tracked Literature 핀 후보** — KineFuse 는 D11·D12 를 동시에 외부 검증하는 드문 사례이며, 특히 "구조적 inductive bias 로서의 topology-aware 촉각 인코딩" 이라는 각도는 현재 pinned/non-pinned 어디에도 없습니다. **DexViTac(non-pinned)를 KineFuse 로 교체하거나, hard cap 8 여유가 있으면 KineFuse 를 D12 검증 핀으로 승격**하는 것을 제안합니다(사람 결정).
- **P3** — 지지가 방법론 참조 수준이라 pin 변경은 불필요. 다만 "force 채널 domain randomization(multiplicative·offset·noise·dropout)" 레시피는 D18 sim2real 의 참고 항목으로 메모할 가치가 있습니다.
- context/ 파일은 수정하지 않았습니다.

> 💡 base 매핑은 `/implement-design analysis/2607.14842/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
