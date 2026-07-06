# Paper Analysis — VT-WAM: Visual-Tactile World Action Model for Contact-Rich Manipulation

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | VT-WAM: Visual-Tactile World Action Model for Contact-Rich Manipulation |
| 저자 | Shuai Tian, Yupeng Zheng, Yuhang Zheng, Songen Gu, Yujie Zang, Yuxing Qin, Weize Li, Haoran Li, Wenchao Ding, Dongbin Zhao (CASIA · UCAS · TARS Robotics · NUS · Fudan) |
| 링크 | [arXiv:2607.02503](https://arxiv.org/abs/2607.02503) · [Website](https://vt-wam.github.io/) |
| 발행일 / 버전 | 2026-07-02 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-07-06 |
| 관련 Pillar | P5, P2, P0 |
| 태그 | vla-arch, tactile, flow-matching |

---

## 🧭 한 줄 요약 (TL;DR)

VT-WAM은 미래 시각 예측·촉각 변형(deformation) 예측·행동 예측을 하나의 flow matching 프레임워크에서 공동 학습하는 시각-촉각 World Action Model로, 비대칭 MoT 어텐션으로 첫 프레임 시각 앵커와 시간축 촉각 동역학을 연결하고 접촉 구간 전용 어텐션 유도 손실(AVTAG)로 행동 쿼리가 촉각 증거에 의존하도록 강제하여 6개 실제 접촉 리치(contact-rich) 과제에서 71.67% 평균 성공률을 달성합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 접촉 리치 조작은 국소 변형·압력·미끄러짐·마찰에 반응해야 하지만, 이 단서들은 시간축으로 희소하고(temporally sparse) 시각 관찰에서는 잘 보이지 않아 vision-centric 정책이 접촉 상황에서 신뢰성을 잃습니다.
- **기존 접근의 한계** — 기존 시각-촉각 정책은 촉각 관찰을 행동 예측에 직접 입력으로 넣기만 할 뿐, 행동 생성 중 촉각 변형의 *동역학*을 거의 모델링하지 않습니다. 게다가 시각은 대부분 프레임에서 조밀한(dense) 정보를 주는 반면 촉각은 짧은 접촉 구간에서만 유효해, 공동 학습 시 신경망이 시각 증거에 편향(visual-dominance bias)되고 촉각이 저활용됩니다.
- **본 논문의 가설** — 행동 예측을 촉각 진화(tactile evolution)와 *결합(couple)* 하면 정책이 접촉 구간에서 촉각 변화를 활용할 수 있습니다. World Action Model(WAM)이 행동과 비디오 예측을 결합하는 능력을 촉각 변형 동역학으로 확장하는 것이 핵심 아이디어입니다.
- **왜 지금 중요한가** — WAM 계열(Fast-WAM, UWM, DreamZero 등)이 시각 동역학을 행동 예측에 결합하며 부상하는 시점에서, 접촉이 지배하는 과제로 확장하려면 시각을 넘어선 촉각 동역학이 필요합니다.
- **우리 맥락의 의미** — P5(World Model)의 action-conditioned 예측 auxiliary 방향과 P2(구조화된 멀티모달 관찰 융합)의 촉각-시각 비대칭 융합을 한 논문에서 동시에 건드리는 사례입니다.

---

## 🧩 핵심 기여

- **시각-촉각-행동 공동 flow matching** — 미래 시각 예측·촉각 변형 예측·행동 예측을 단일 flow matching 목적함수 안에서 결합하여, 촉각 변형 동역학이 행동 예측에 직접 정보를 주도록 합니다.
- **Asymmetric MoT Attention** — 행동 토큰이 접촉 진화를 위해 전체 촉각 시퀀스에는 attend하되 전역 맥락을 위해서는 *첫 프레임 시각 앵커에만* attend하는 비대칭 리드아웃(readout). 미래 시각 예측을 배포 시 제거하는 visual-cache 추론 모드를 가능케 합니다.
- **Contact-Gated AVTAG** — 접촉 구간에서 상대 촉각 어텐션이 상대 시각 어텐션보다 낮은 경우를 벌하는 훈련 전용 hinge ranking 손실로, 추론 시 아키텍처를 바꾸지 않고 시각 편향을 완화합니다.
- **실제 로봇 검증** — 6개 실제 접촉 리치 과제(표면 상호작용 3 + 제약 삽입 3)에서 71.67% 평균 성공률로 Fast-WAM 대비 +26.67%p, OmniVTLA 대비 +35.84%p 우위를 보이며, ablation으로 촉각 동역학 모델링과 접촉 구간 유도 각각의 기여를 확인합니다.

---

## 🔑 기술 키워드

- **World Action Model (WAM)** — 미래 상태 예측을 행동 예측에 통합하는 정책 계열로, 현재 관찰에서 곧바로 행동을 뽑는 VLA와 달리 "다음에 무엇이 일어나는가"를 함께 학습합니다.
- **Visual-Tactile World Action Model** — WAM을 촉각 변형 동역학까지 확장하여 접촉 진화가 행동 예측에 직접 개입하도록 한 본 논문의 모델.
- **Mixture-of-Transformers (MoT)** — 모달리티별 전문가(expert)를 두되 어텐션 레이어에서 토큰을 교류시키는 희소·확장형 멀티모달 백본 구조.
- **Asymmetric MoT Attention** — 시각·촉각·행동 전문가 간 정보 흐름을 블록별 어텐션 마스크로 비대칭 제어하여, 행동 토큰이 첫 프레임 시각 + 전체 촉각에만 접근하도록 하는 리드아웃.
- **Visual-Cache Inference** — 현재 시각 관찰을 첫 프레임 앵커로 캐싱하고 미래 시각 예측을 제거하여 촉각·행동 latent만 디노이징하는 배포용 추론 모드.
- **AVTAG (Action-Visual-Tactile Attention Guidance)** — 접촉 구간에서 행동 쿼리가 촉각 증거에 더 attend하도록 유도하는 훈련 전용 보조 어텐션 손실.
- **Hinge Ranking Loss** — 상대 시각 어텐션이 상대 촉각 어텐션을 초과할 때만 벌점을 주고 역전되면 0이 되는 순위형 손실.
- **Contact Gating** — 뚜렷한 촉각 변형으로 식별한 접촉 구간 행동 토큰에만 보조 손실을 적용하는 게이팅 방식.
- **Flow Matching** — 선형 확률 경로의 속도장(velocity field)을 회귀하여 시각·촉각·행동 토큰을 함께 생성하는 학습 목적함수.
- **Tactile Deformation Field** — 촉각 표면의 3D 변형장을 시퀀스로 예측하는 대상으로, 압력 집중·접촉 이동 같은 국소 접촉 패턴을 담습니다.

---

## 🔬 방법론

### 직관

VT-WAM의 출발점은 "접촉 리치 과제에서 결정적 정보는 시각이 아니라 촉각인데, 촉각은 짧은 접촉 순간에만 존재해 학습이 그것을 무시하기 쉽다"는 관찰입니다. 시각은 거의 모든 프레임에서 조밀하게 화면 정보를 주지만, 촉각 변형은 접촉이 일어나는 짧은 구간에만 유효한 신호로 나타납니다. 이 시간축 불균형 때문에 공동 학습 손실은 시각에만 의존해도 충분히 줄어들고, 정작 접촉이 중요한 순간의 촉각은 저활용됩니다.

이를 풀기 위해 저자들은 두 갈래의 설계를 씁니다. 첫째, 행동 예측을 촉각 *진화*와 묶습니다. 단순히 촉각을 입력으로 넣는 것이 아니라, 촉각 변형이 앞으로 어떻게 바뀔지를 예측하는 World Action Model의 틀 안에서 시각·촉각·행동을 하나의 flow matching으로 함께 생성합니다. 둘째, 세 모달리티의 정보 교류를 대칭이 아니라 *비대칭*으로 설계합니다. 시각은 전역 장면 맥락만 주면 되므로 행동 토큰은 첫 프레임 시각 앵커에만 붙고, 촉각은 접촉 진화를 담으므로 전체 시퀀스에 붙습니다. 이 비대칭 덕분에 배포 시 미래 시각 예측(비싸고 불필요한 latency 원인)을 통째로 떼어낼 수 있습니다.

그래도 공동 학습은 여전히 시각으로 기울 수 있으므로, 세 번째 장치인 AVTAG가 훈련 시에만 작동해 "접촉 구간에서는 촉각에 더 attend하라"는 압력을 어텐션 맵에 직접 겁니다. 이 손실은 추론 시 아키텍처를 전혀 바꾸지 않으면서, 접촉이 물리적으로 유의미한 순간에만 촉각 우선순위를 학습시킵니다.

### 아키텍처

![Figure 2 — VT-WAM 개요](https://arxiv.org/html/2607.02503/x2.png)

> "Figure 2: Overview of VT-WAM. (a) Joint visual-tactile-action flow matching with three modality-specific experts connected by Asymmetric MoT Attention. (b) Attention masks in Asymmetric MoT Attention during training and inference. (c) Contact-gated AVTAG applies a training-only hinge ranking loss that encourages action queries to prioritize tactile evidence during contact phases." (§III)
(한글 해설 — 세 모달리티 전문가와 이들을 잇는 비대칭 MoT 어텐션, 훈련/추론 마스크, 그리고 접촉 게이트 AVTAG의 세 축이 전체 그림을 구성합니다.)

VT-WAM은 시각-촉각-행동 전문가(visual-tactile-action expert) 구조를 씁니다. 시각 전문가는 손목 카메라 토큰을 전역 장면 맥락으로, 촉각 전문가는 촉각 변형 토큰에서 국소 접촉 진화를, 행동 전문가는 시각·촉각 증거로부터 행동 청크를 예측합니다.

> "The visual expert encodes wrist camera tokens as global scene context, the tactile expert models local contact evolution from tactile deformation tokens, and the action expert predicts the action chunk from visual and tactile evidence." (§III-A)
(한글 해설 — 세 전문가의 역할 분담이 명확히 나뉘며, 이 분담이 뒤이은 비대칭 마스크 설계의 근거가 됩니다.)

모달리티별 토큰화는 다음과 같습니다.

- **시각** — 손목 카메라 시퀀스 $`\mathbf{O}^{v}\in\mathbb{R}^{T_{v}\times 3\times H\times W}`$ 를 Wan2.2 video VAE로 인코딩하고 patchify하여 시각 토큰 $`\mathbf{X}_{v}\in\mathbb{R}^{N_{v}\times d}`$ 생성.
- **촉각** — 촉각 변형 시퀀스 $`\mathbf{O}^{t}\in\mathbb{R}^{T_{t}\times 6\times H_{t}\times W_{t}}`$ (두 촉각 표면의 3D 변형장)를 OmniVTA를 따른 사전학습 tactile VAE로 촉각 토큰 $`\mathbf{X}_{t}\in\mathbb{R}^{N_{t}\times d}`$ 로 인코딩.
- **행동** — 행동 청크 $`\mathbf{A}\in\mathbb{R}^{S_{a}\times D_{a}}`$ 를 선형 투영하여 행동 토큰 $`\mathbf{X}_{a}\in\mathbb{R}^{S_{a}\times d}`$ 생성.
- **언어·proprioception** — 언어 지시 $`c`$ 와 proprioceptive 상태 $`\mathbf{s}`$ 는 cross-attention으로 각 전문가에 공급.

$`l`$-번째 Asymmetric MoT Attention 레이어에서 각 전문가는 자기 토큰 스트림으로부터 Q/K/V를 계산하고, 시각·촉각·행동 순서로 concat합니다.

$$\mathbf{Q}^{(l)}=[\mathbf{Q}_{v}^{(l)};\mathbf{Q}_{t}^{(l)};\mathbf{Q}_{a}^{(l)}],\quad \mathbf{K}^{(l)}=[\mathbf{K}_{v}^{(l)};\mathbf{K}_{t}^{(l)};\mathbf{K}_{a}^{(l)}],\quad \mathbf{V}^{(l)}=[\mathbf{V}_{v}^{(l)};\mathbf{V}_{t}^{(l)};\mathbf{V}_{a}^{(l)}]$$

이후 마스킹된 어텐션을 수행합니다.

$$\mathbf{P}^{(l)}=\mathrm{Softmax}\left(\frac{\mathbf{Q}^{(l)}(\mathbf{K}^{(l)})^{\top}}{\sqrt{d}}+\mathbf{M}\right),\qquad \mathbf{Y}^{(l)}=\mathbf{P}^{(l)}\mathbf{V}^{(l)}$$

여기서 $`\mathbf{M}`$ 은 어떤 query 토큰이 어떤 key 토큰에 attend할 수 있는지를 결정하는 블록별 마스크입니다 (허용 = 0, 차단 = $`-\infty`$). Asymmetric MoT Attention 레이어들을 지난 뒤, 모달리티별 투영 헤드가 각 토큰의 velocity field를 flow matching 목적함수 하에서 예측합니다.

### 아키텍처 — Asymmetric MoT Attention (비대칭 마스크)

비대칭 설계는 두 요구에서 나옵니다. (1) 손목 카메라는 주로 전역 맥락을 주고 촉각이 접촉 상호작용의 핵심 증거이므로 행동 예측은 촉각 시퀀스에 접근해야 하고, (2) 미래 시각 토큰을 디노이징하는 것은 배포 시 불필요한 latency를 유발합니다.

> "VT-WAM therefore uses an asymmetric readout: action tokens attend to the tactile sequence for contact dynamics, but attend only to the first-frame visual tokens for global context." (§III-B)
(한글 해설 — 이 한 문장이 비대칭 리드아웃의 설계 의도를 못 박습니다: 촉각은 전체, 시각은 첫 프레임만.)

토큰은 $`[\mathbf{X}_{v};\mathbf{X}_{t};\mathbf{X}_{a}]`$ 순서로 패킹되며, $`F_{v}`$ = 첫 프레임 시각 토큰 수, $`N_{v}`$ = 전체 시각 토큰 수, $`N_{t}`$ = 촉각 토큰 수, $`S_{a}`$ = 행동 토큰 수입니다. 마스크의 행은 갱신되는 query, 열은 정보원 key입니다.

- **시각 전문가** — 촉각·행동 key를 차단하여 국소 접촉 변형과 미래 행동이 시각 표현을 바꾸지 못하게 합니다.

$$\mathbf{M}_{v\rightarrow t}=-\infty\cdot\mathbf{1}_{N_{v}\times N_{t}},\qquad \mathbf{M}_{v\rightarrow a}=-\infty\cdot\mathbf{1}_{N_{v}\times S_{a}}$$

- **촉각 전문가** — 시각 토큰 중 첫 프레임 앵커만 보이게 하여 촉각 동역학을 전역 맥락에 접지(ground)하되 미래 시각 의존을 막고, 행동 key도 차단합니다.

$$\mathbf{M}_{t\rightarrow v}=[\mathbf{0}_{N_{t}\times F_{v}}\mid-\infty\cdot\mathbf{1}_{N_{t}\times(N_{v}-F_{v})}],\qquad \mathbf{M}_{t\rightarrow a}=-\infty\cdot\mathbf{1}_{N_{t}\times S_{a}}$$

- **행동 전문가** — 첫 프레임 시각 앵커와 전체 촉각 시퀀스를 노출하여, control에 쓰이는 visual-cache 추론 모드와 일치시킵니다.

$$\mathbf{M}_{a\rightarrow v}=[\mathbf{0}_{S_{a}\times F_{v}}\mid-\infty\cdot\mathbf{1}_{S_{a}\times(N_{v}-F_{v})}],\qquad \mathbf{M}_{a\rightarrow t}=\mathbf{0}_{S_{a}\times N_{t}}$$

훈련 시에는 세 갈래를 하나의 joint flow matching으로 함께 최적화하고, 추론 시에는 미래 시각 토큰을 제거하여 촉각·행동만 디노이징합니다. 이로써 접촉 동역학 모델링을 보존하면서 미래 시각 예측 비용을 피합니다.

### 학습 목표 / 손실 — Contact-Gated AVTAG

Asymmetric MoT Attention이 행동 토큰의 촉각 접근을 *허용*하더라도, 공동 학습은 여전히 시각 증거를 선호할 수 있습니다. 시각은 대부분 프레임에서 조밀하고 촉각은 짧은 접촉 구간에만 유효하기 때문입니다. AVTAG는 이 불균형을 완화하는 훈련 전용 보조 어텐션 목적함수입니다.

행동 query에서 시각·촉각 key로의 보조 어텐션 분포를 구성하되, 시각·촉각 key 표현을 직접 바꾸지 않기 위해 $`\mathbf{K}_{\mathrm{vt}}=[\mathbf{K}_{v};\mathbf{K}_{t}]`$ 에 stop-gradient를 적용합니다.

$$\mathbf{P}_{\mathrm{vt}}=\mathrm{Softmax}\left(\frac{\mathbf{Q}_{a}\mathrm{sg}(\mathbf{K}_{\mathrm{vt}})^{\top}}{\sqrt{d}}\right)$$

각 행동 토큰 $`r\in\{1,\ldots,S_{a}\}`$ 에 대해 시각·촉각 key로 배분된 보조 어텐션을 합산합니다.

$$\alpha_{v}(r)=\sum_{j\in\mathrm{visual}}\mathbf{P}_{\mathrm{vt}}[r,j],\qquad \alpha_{t}(r)=\sum_{j\in\mathrm{tactile}}\mathbf{P}_{\mathrm{vt}}[r,j]$$

이를 상대 시각·촉각 어텐션 가중치로 정규화합니다.

$$p_{v}(r)=\frac{\alpha_{v}(r)}{\alpha_{v}(r)+\alpha_{t}(r)},\qquad p_{t}(r)=\frac{\alpha_{t}(r)}{\alpha_{v}(r)+\alpha_{t}(r)}$$

뚜렷한 촉각 변형으로 식별한 접촉 구간 행동 토큰 집합 $`\mathcal{C}`$ 에만 hinge ranking 손실을 적용합니다.

$$L_{\mathrm{AVTAG}}=\mathbb{E}_{r\in\mathcal{C}}\left[\max\left(0,\;p_{v}(r)-p_{t}(r)\right)\right]$$

> "This hinge ranking loss penalizes visual-dominant attention during contact phases, and incurs no penalty once $`p_{t}(r)\geq p_{v}(r)`$." (§III-C)
(한글 해설 — 접촉 구간에서 상대 촉각 어텐션이 상대 시각 어텐션 이상이 되는 순간부터는 벌점이 사라지므로, 촉각을 "과도하게" 강제하지 않고 시각-지배만 교정합니다.)

### 학습 목표 / 손실 — Flow Matching 목적함수

세 전문가가 각자의 velocity field를 예측하는 joint flow matching 손실입니다.

$$L_{\mathrm{Flow}}=\lambda_{v}L_{v}+\lambda_{t}L_{t}+\lambda_{a}L_{a}$$

$$L_{v}=\mathbb{E}\|\hat{\mathbf{f}}^{v}-\mathbf{f}_{v}^{*}\|^{2},\quad L_{t}=\mathbb{E}\|\hat{\mathbf{f}}^{t}-\mathbf{f}_{t}^{*}\|^{2},\quad L_{a}=\mathbb{E}\|\hat{\mathbf{f}}^{a}-\mathbf{f}_{a}^{*}\|^{2}$$

여기서 $`\hat{\mathbf{f}}^{v}, \hat{\mathbf{f}}^{t}, \hat{\mathbf{f}}^{a}`$ 는 예측 velocity field, $`\mathbf{f}_{v}^{*}, \mathbf{f}_{t}^{*}, \mathbf{f}_{a}^{*}`$ 는 flow matching target입니다. AVTAG를 켜면 전체 훈련 목적함수는 다음과 같습니다.

$$L_{\mathrm{Train}}=L_{\mathrm{Flow}}+\lambda_{\mathrm{AVTAG}}L_{\mathrm{AVTAG}}$$

### 학습 셋업

> "VT-WAM uses pretrained Wan2.2-5B [20] as the visual backbone and uses 1B-scale DiT models for the tactile and action experts." (§IV-A2)
(한글 해설 — 시각 백본은 5B 규모의 사전학습 비디오 모델이고, 촉각·행동 전문가는 각 1B DiT입니다 — 전체 규모가 상당합니다.)

- **데이터** — 과제별 100개 전문가 궤적을 인간 kinesthetic teaching으로 수집. 시각·촉각·proprioception·행동 스트림을 동기화하고 30Hz로 리샘플.
- **손실 가중치** — $`\lambda_{v}=\lambda_{t}=\lambda_{a}=1`$, $`\lambda_{\mathrm{AVTAG}}=0.05`$.
- **옵티마이저** — AdamW, learning rate $`1\times 10^{-4}`$, weight decay $`1\times 10^{-2}`$, bf16 혼합 정밀도, gradient clipping 1.0, 5% warmup 후 cosine decay.
- **하드웨어** — NVIDIA A100 (80GB) GPU에서 훈련. 추론 평가는 원격 A100 서버, 행동 예측에 10 denoising step.
- **플랫폼** — 7-DoF xArm7 + Robotiq 2F-85 병렬 그리퍼, 손목 카메라($`128\times 128`$ RGB @30Hz), 그리퍼 손가락 안쪽 표면에 장착한 두 개의 Xense 촉각 센서(각 $`35\times 20`$ 3D 변형장 @30Hz).

---

## 📊 실험 설정과 결과

평가는 6개 실제 접촉 리치 과제로, 표면 상호작용(wipe board / wipe vase / peel cucumber)과 제약 삽입(insert plug / swipe card / insert tube) 두 체제로 나뉩니다. 과제·방법마다 20회 독립 시행. 표면 상호작용은 점수 $`\{0,0.5,1\}`$ (0.5 = 목표 영역 절반 이상 완료), 제약 삽입은 이진 $`\{0,1\}`$.

### 주요 결과 (Table I)

| Method | Wipe Board | Wipe Vase | Peel Cucumber | 표면 Avg. | Insert Plug | Swipe Card | Insert Tube | 삽입 Avg. | Average |
|---|---|---|---|---|---|---|---|---|---|
| DP + Tactile | 30% | 20% | 25% | 25.00% | 5% | 35% | 15% | 18.33% | 21.67% |
| RDP | 45% | 60% | 40% | 48.33% | 15% | 35% | 10% | 20.00% | 34.17% |
| $`\pi_{0.5}`$ | 40% | 35% | 35% | 36.67% | 30% | 45% | 10% | 28.33% | 32.50% |
| OmniVTLA | 45% | 30% | 25% | 33.33% | 40% | 35% | 40% | 38.33% | 35.83% |
| Fast-WAM | 70% | 55% | 45% | 56.67% | 20% | 55% | 25% | 33.33% | 45.00% |
| **VT-WAM** | **90%** | **85%** | **70%** | **81.67%** | **60%** | **70%** | **55%** | **61.67%** | **71.67%** |

> "Compared with the strongest baseline Fast-WAM [29], VT-WAM improves the success rate from 45.00% to 71.67%, corresponding to an absolute gain of 26.67%." (§IV-C1, TABLE I)
(한글 해설 — 최강 baseline인 시각 전용 WAM(Fast-WAM) 대비 절대 +26.67%p로, 초록의 수치와 일치합니다.)

> "$`\pi_{0.5}`$ achieves 36.67% success rate, while OmniVTLA achieves only 33.33% despite using tactile input." (§IV-C1)
(한글 해설 — 표면 상호작용에서 촉각을 *입력으로만* 쓰는 OmniVTLA가 촉각 없는 $`\pi_{0.5}`$ 보다 오히려 낮아, "촉각을 입력으로만 넣는 것은 상호작용 동역학 모델링에 불충분"하다는 논지를 뒷받침합니다.)

특히 insert tube는 투명 튜브라 시각 정렬이 불안정해 접촉 기반 보정이 필수인데, VT-WAM이 55%로 Fast-WAM(25%)·OmniVTLA(40%) 대비 크게 앞섭니다.

### 촉각 변형 예측 품질 (Table II)

joint inference 모드에서 시각·촉각을 함께 예측하고, OmniVTA를 따라 변형 크기 오차($`l_{2}`$, 전체 3D 변형장) 와 방향 일관성($`\cos`$, 비영(non-zero) 변형 영역)으로 평가합니다.

| Method | $`l_{2}\downarrow`$ | $`\cos\uparrow`$ |
|---|---|---|
| exUMI | 0.091 | 0.618 |
| UVA | 0.083 | 0.667 |
| **VT-WAM** | **0.077** | **0.749** |

> "VT-WAM achieves lower deformation error and higher directional consistency than the baseline models, indicating that the tactile expert learns meaningful contact deformation dynamics." (§IV-C2, TABLE II)
(한글 해설 — 촉각 전문가가 압력 집중·접촉 이동 같은 국소 접촉 패턴을 실제로 예측함을 정량적으로 뒷받침합니다.)

### Ablation (Table III) — wipe vase / insert tube

| Model | Description | Wipe Vase | Insert Tube |
|---|---|---|---|
| $`M_{0}`$ | Fast-WAM | 55% | 25% |
| $`M_{1}`$ | $`M_{0}`$ + Sym. ($`T`$ Seq.) | 65% | 40% |
| $`M_{2}`$ | $`M_{0}`$ + Asym. ($`T_{0}`$) | 40% | 30% |
| $`M_{3}`$ | $`M_{0}`$ + Asym. ($`T`$ Seq.) | 70% | 50% |
| $`M_{4}`$ | **VT-WAM: $`M_{3}`$ + AVTAG** | **85%** | **55%** |

- **Ablation 1 (촉각 동역학을 어떻게 넣는가)** — $`M_{1}`$ (대칭 MoT + 촉각 시퀀스 예측)이 $`M_{0}`$ 대비 55→65% / 25→40%로 향상하나, 대칭 융합은 추론 시 미래 시각·촉각 예측이 필요해 계산 비용이 큽니다. $`M_{2}`$ (비대칭, 첫 촉각 프레임만)는 40%/30%로 오히려 떨어지지만 $`M_{3}`$ (비대칭, 전체 촉각 시퀀스)는 70%/50%로 올라, **행동 예측이 초기 촉각 상태가 아니라 시간축 촉각 진화로부터 이득을 본다**는 점을 격리합니다.
- **Ablation 2 (AVTAG의 효과)** — $`M_{3}`$ 와 $`M_{4}`$ 는 동일한 Asymmetric MoT Attention을 쓰고 차이는 오직 훈련 시 AVTAG뿐인데, 70→85% / 50→55%로 향상. **이득이 훈련 중 학습된 더 나은 접촉-인식 촉각 어텐션에서 온다**는 것을 확인합니다.

![Figure 6 — AVTAG 접촉 복구](https://arxiv.org/html/2607.02503/pics/VTWAM_fig6.png)

> "Figure 6: AVTAG promotes tactile attention for contact recovery during vase wiping. The red and blue curves denote relative tactile and visual attention weights $`p_{t}`$ and $`p_{v}`$ from the action expert, and the dashed curve denotes the contact force $`|F_{z}|`$ for visualization only." (§IV-D)
(한글 해설 — 지지면을 아래로 내려 접촉을 끊는 교란 상황에서, AVTAG가 없으면 어텐션이 시각에 정적으로 고정되어 접촉 손실에 반응하지 못하고, AVTAG가 있으면 접촉 구간에서 촉각 어텐션이 올라가 접촉을 재확립합니다.)

---

## ⚖️ 한계

- **개별 과제 특화 (multi-task 미탐구)** — 저자 스스로 밝히듯 모든 방법이 과제별로 각각 학습되고(과제당 100 궤적), 다중 과제 학습과 scaling law는 미탐구입니다. 접촉의 정밀 모델링을 위해 과제 특화를 택했다는 것인데, 이는 일반화·전이 능력에 대한 증거를 전혀 제공하지 못한다는 뜻이고 실제 배포에서 가장 비싼 미지수입니다.
- **접촉 구간 식별의 임계값 미명시** — $`\mathcal{C}`$ 는 "뚜렷한 촉각 변형(pronounced tactile deformation)"으로 정의될 뿐, 어떤 임계값·통계로 접촉 구간을 판정하는지 본문에 수치가 없습니다. AVTAG의 전체 효과가 이 게이팅 품질에 달려 있으므로, 임계값 민감도가 재현의 핵심 변수인데 공개되지 않았습니다.
- **평가 규모의 협소함** — 6개 과제 각 20회 시행이라 5%p 단위 차이가 시행 1회에 해당해, 개별 셀(예: insert tube 50%→55%)의 통계적 유의성이 약합니다. Ablation은 2개 과제로만 수행되어 결론의 일반성이 제한됩니다.
- **무거운 시각 백본 의존** — Wan2.2-5B + 두 개의 1B DiT는 6B+ 규모로, A100 훈련·원격 A100 추론을 전제합니다. visual-cache 추론으로 미래 시각 예측은 뗐지만 5B 시각 인코더 자체는 매 스텝 필요하며, 실시간 제어 latency·온보드 배포 가능성에 대한 정량 보고가 없습니다.
- **평행 그리퍼 국한** — 촉각이 병렬 2지 그리퍼의 두 표면에서 온 평면 변형장이라, 손가락별 접촉 귀속(attribution)이나 다지 손의 국소 접촉 구조에 대한 증거가 없습니다. "촉각 동역학이 유용하다"는 주장은 이 단순 접촉 형상에서만 검증되었습니다.
- **tactile VAE 사전학습 의존** — 촉각 토큰화가 OmniVTA의 사전학습 tactile VAE에 의존해, 새 센서/모달리티로 옮길 때 이 인코더를 다시 확보·재학습해야 하는 이식 부담이 잠재합니다.

---

## ♻️ 재현성

- **코드/모델** — 프로젝트 웹사이트([vt-wam.github.io](https://vt-wam.github.io/))만 명시되며, 논문 본문에 코드/체크포인트 공개 언급은 없습니다(분석 시점 미확인). 촉각 tactile VAE는 OmniVTA(별도 논문)에 의존.
- **데이터** — 과제별 100 궤적을 자체 kinesthetic teaching으로 수집한 비공개 실로봇 데이터. 공개 데이터셋 아님.
- **하드웨어** — xArm7 + Robotiq 2F-85 + Xense 촉각 센서 2개 + 손목 카메라. A100(80GB) 훈련, 원격 A100 추론. 하드웨어 사양은 명시적이나 특정 센서(Xense)·백본(Wan2.2-5B) 확보가 재현 전제.
- **핵심 하이퍼파라미터** — 손실 가중치, 옵티마이저, denoising step 등은 §IV-A2에 명시되어 재현에 유리하나, 접촉 게이팅 임계값·토큰 수($`N_v, N_t, F_v, S_a`$)·청크 길이 등 다수 세부가 미명시입니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P5(World Model) — 정면 대상.** VT-WAM은 그 자체로 World Action Model이며 D28(world-model role — dynamics prior + future-prediction auxiliary co-trained)의 "행동과 공동 학습되는 미래 예측 auxiliary" 방향의 구체 사례입니다. 다만 우리 v1은 auxiliary를 *잠재/3D-flow* 예측으로 좁혔는데(D30), VT-WAM은 시각 latent + 촉각 변형장을 예측하므로 접촉 관련(3D 변형) 예측을 포함하는 점에서 D30과 부분 정합합니다. D29(integration architecture)에서 VT-WAM은 "공유 백본 위 auxiliary head"와 "완전 통합"의 중간 — 세 모달리티 전문가를 하나의 flow matching 백본에 MoT로 묶는 형태로, Being-H0.7식 auxiliary와 WorldVLA식 통합 사이의 설계점입니다. D31(action conditioning — per-frame action-conditioned)과도 정합(joint 행동+동역학).
- **P2(구조화된 멀티모달 관찰 융합) — 강한 부차 대상.** Asymmetric MoT Attention은 D10(cross-attention/asymmetric fusion, flat concat 아님)의 직접 사례이고, AVTAG는 "촉각 저활용 방지"라는 D10/D11의 동기와 정확히 같은 문제를 훈련 손실로 공략합니다. tactile VAE 토큰화는 D11(proprio-tactile-force token construction)의 한 형태이나, 우리가 요구하는 손가락별 귀속과는 거리가 있습니다.
- **P0(VLA Datasets & Benchmarks) — 약한 접점.** D25(tactile/torque data scouting) 관점에서 3D 촉각 변형장 데이터 스트림을 다루나, 데이터셋 자체 기여는 없어 접점은 방법론 쪽입니다.
- **Identity 긴장/지지** — *지지*: "촉각 저활용은 손실/어텐션 설계로 교정해야 한다"는 우리 P2 논지(flat concat 초월)를 강하게 지지합니다. *긴장*: 병렬 그리퍼 + 평면 촉각이라 우리의 dexterous **hand** + 손가락별 tactile 접지와 하드웨어 전제가 다릅니다.
- **경쟁자 함의** — Fast-WAM(P5 §5 anti-topic 인접 baseline)·OmniVTLA·OmniVTA 계열이 촉각-WAM 경쟁군을 형성하며, VT-WAM은 이 군의 최신 SOTA로 P5 추적 대상 후보입니다.

---

## ✨ 핀 논문 대비 델타

- **vs Being-H0.7 (P5 §5 Top pin, [arXiv:2605.00078](https://arxiv.org/abs/2605.00078))** — Being-H0.7은 미래 *시각* 관찰을 사후(posterior) 분기로 잠재 감독하여 픽셀 생성 없이 미래-인식 추론을 얻습니다. VT-WAM의 진짜 새로움은 **촉각 변형 동역학을 예측 대상 모달리티로 승격**하고, 접촉 구간 전용 hinge ranking 손실(AVTAG)로 촉각 어텐션을 강제한다는 점입니다. Being-H0.7이 시각-미래 축을 잠재화했다면 VT-WAM은 촉각-미래 축을 추가하고 접촉 게이팅을 도입했습니다.
- **vs 시각-전용 WAM(Fast-WAM, D28 baseline)** — Fast-WAM은 시각 동역학만 모델링하고 test-time 미래 상상을 제거한 WAM입니다. VT-WAM은 그 위에 촉각 시퀀스 예측 + 비대칭 리드아웃 + AVTAG를 쌓은 상속형으로, ablation의 $`M_0 \to M_4`$ 궤적이 정확히 그 델타를 보여줍니다.
- **vs ForceFlow / ViTacFormer (P2 §5 pins)** — 이들은 비대칭·cross-attention 시각-촉각 *융합*을 관찰 입력 단에서 수행합니다. VT-WAM의 차별점은 촉각을 입력이 아니라 *예측 대상 동역학*으로 다루고(WAM 확장), 융합 편향을 손실로 교정한다는 점입니다.

---

## ⚙️ 의사결정 함의

- **AVTAG를 촉각 저활용 방지 레버로 채택 검토(P2 D10/D11).** 우리 스택이 vision + proprio + tactile + force를 cross-attention으로 융합할 때 촉각이 저활용되는 문제를, 별도 모달리티 dropout뿐 아니라 **접촉 구간 전용 hinge ranking 보조 손실**($`\lambda_{\mathrm{AVTAG}}=0.05`$ 수준의 작은 가중치)로 공략할 수 있습니다. 이는 백본·인코더 선택과 독립적이라 이식 비용이 낮은 편입니다. 신설 config 키 후보: `aux_tactile_attention_weight`, `contact_gate_threshold`.
- **World-model auxiliary의 "비대칭 리드아웃" 패턴(P5 D29/D30).** 미래 시각 예측 비용을 배포 시 제거하되 접촉 동역학 예측은 보존하는 visual-cache 추론은, 우리가 P5에서 걱정하는 "WAM auxiliary의 추론 비용" 문제에 대한 구체적 해법입니다. auxiliary head를 훈련 시에만 켜고 추론 시 마스크로 끊는 설계를 D29 통합 아키텍처 결정에 반영할 수 있습니다.
- **접촉 구간 게이팅 메트릭.** contact-phase 식별(촉각 변형 크기 임계값)은 우리 System0/접촉 관련 로직(P3 인접)과도 공유 가능한 신호이며, 촉각 변형 magnitude/방향 일관성($`l_2`$/$`\cos`$)을 촉각 예측 품질 메트릭으로 채택할 후보입니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **[가장 싼 체크] 병렬 그리퍼 → 다지 손 촉각 형상 전이.** VT-WAM의 촉각은 두 평면 표면의 3D 변형장입니다. 우리 Sharpa Deform Map(손가락별 ~320×240)로 옮길 때 tactile VAE 토큰화가 10 손가락 + 2 손바닥 토큰(D11) 구조로 확장 가능한지, 단일 tactile VAE가 손가락별 귀속을 유지하는지 먼저 데스크 체크. 확장 불가면 AVTAG의 "촉각 vs 시각" 이분 어텐션이 손가락별로 세분화되어야 해 손실 정의부터 재설계 필요.
- **접촉 게이팅 임계값의 이식성.** $`\mathcal{C}`$ 판정 임계값이 미명시라, 우리 센서의 변형 스케일·노이즈에서 접촉 구간을 안정적으로 식별할 수 있는지 소규모 로그 분석으로 확인. 임계값이 과제/센서마다 튜닝되어야 하면 자동화 파이프라인에서 취약점.
- **백본 이질성.** VT-WAM은 Wan2.2-5B 비디오 백본 위에서 검증되었는데 우리는 π(π0/π0.5) 계보를 씁니다. AVTAG는 어텐션 맵에 걸리는 손실이라 백본 무관하지만, "미래 시각 예측을 flow matching으로 함께 학습"하는 부분은 π 백본에 시각 velocity head를 붙일 수 있어야 성립 — 백본 개조 범위 사전 확인.
- **단일 과제 특화의 일반화 한계.** 과제당 100 궤적 개별 학습이라, 우리의 다중 과제·data-efficient adaptation(P4) 전제와 충돌합니다. AVTAG/비대칭 리드아웃이 다중 과제·사전학습 체제에서도 촉각 저활용을 교정하는지는 논문이 보여주지 못했으므로, 이식 시 소규모 다중 과제 셋에서 촉각 어텐션 활용도를 먼저 측정해야 합니다.
- **평가 노이즈.** 5%p = 20회 중 1회라, 개별 ablation 셀을 근거로 설계를 확정하지 말고 다회 반복·더 넓은 과제군에서 재확인 필요.

---

## 💡 컨텍스트 제안

- **P5 §5 Tracked Literature 후보(non-pinned methodology base).** VT-WAM은 Fast-WAM 계열을 촉각 동역학으로 확장한 최신 시각-촉각 WAM으로, P5의 촉각-WAM 축을 대표합니다. 다만 P5 pin 상한(8)이 차 있어 즉시 pin보다는 methodology base 행에 "VT-WAM ([arXiv:2607.02503](https://arxiv.org/abs/2607.02503)) — 촉각 변형 동역학을 예측하는 시각-촉각 WAM + 접촉 게이트 어텐션 유도(D28/D30)"로 추가를 제안합니다.
- **P2 §5 non-pinned 후보.** AVTAG(접촉 구간 hinge ranking으로 촉각 저활용 교정)는 D10 "촉각 저활용 방지" 논지의 강한 실증이므로, P2 methodology base에 병기 후보입니다. 최종 판단은 사람이 결정하시면 됩니다.

> 💡 base 매핑은 `/implement-design analysis/2607.02503/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
