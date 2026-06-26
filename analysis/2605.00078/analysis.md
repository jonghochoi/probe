# Paper Analysis — Being-H0.7: A Latent World-Action Model from Egocentric Videos

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Being-H0.7: A Latent World-Action Model from Egocentric Videos |
| 저자 | Hao Luo, Wanpeng Zhang, Yicheng Feng, Sipeng Zheng, Haiweng Xu, Chaoyi Xu, Ziheng Xi, Yuhui Fu, Zongqing Lu (BeingBeyond Team) |
| 링크 | [arXiv:2605.00078](https://arxiv.org/abs/2605.00078) · [Website](https://research.beingbeyond.com/being-h07) |
| 발행일 / 버전 | 2026-04-30 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-26 |
| 관련 Pillar | P5, P4 |
| 태그 | vla-arch, egocentric-data, flow-matching |

---

## 🧭 한 줄 요약 (TL;DR)

Being-H0.7은 미래 프레임을 생성하지 않으면서도 미래-인식(future-aware) 추론을 VLA에 내재화하는 잠재 세계-행동 모델로, 훈련 시에만 사용되는 사후(posterior) 분기가 미래 관찰로부터 잠재 쿼리를 감독하여 추론 시에는 오직 현재 문맥만으로 예측적 잠재 상태를 생성합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — VLA가 관찰에서 행동으로 직접 매핑할 때 희소한 행동 감독이 "단축 경로(shortcut mapping)"를 조장하며, 접촉·객체 동역학·과제 진행도에 대한 중간 표현 대신 시각 단서에 과적합되는 현상을 해결합니다.
- **기존 접근의 한계** — 픽셀 수준 미래 예측(image-then-act WAM)은 행동 생성과 무관한 텍스처·조명·배경까지 모델링하는 데 계산 비용을 낭비하며, 훈련 비용이 크고 추론 시 추가 레이턴시가 발생합니다. Fast-WAM처럼 테스트 시 롤아웃을 제거하더라도 비디오 생성 훈련의 불안정성과 비용을 그대로 상속합니다.
- **본 논문의 가설** — 미래 정보는 행동 생성을 위한 잠재 공간을 형성하는 데 사용되어야 하며, 픽셀로 재구성될 필요가 없습니다. 학습 가능한 잠재 쿼리를 인식과 행동 사이에 두고 사후 분기(미래 관찰 임베딩)와 함께 정렬하면, 배포 시에는 사전(prior) 분기만으로 미래-인식 추론이 가능합니다.
- **왜 지금 중요한가** — 대규모 에고센트릭 비디오를 활용한 사전학습이 가능해지고(Being-H0.5 등), WAM 계열이 부상하는 시점에서 계산 효율과 예측적 추론을 동시에 달성하는 아키텍처 프레임워크가 필요합니다.
- **우리 맥락의 의미** — P5(World Model)의 핵심 방향인 잠재 세계-행동 모델의 구체적 구현 예이며, 동시에 P4(Pretraining for Data-Efficient Adaptation)에서 추적하는 Being-H 계보(Being-H0.5 → Being-H0.7)의 최신 결과입니다.

---

## 🧩 핵심 기여

- **잠재 추론 공간 도입** — 학습 가능한 잠재 쿼리 집합 $`Q \in \mathbb{R}^{K \times d}`$ 를 멀티모달 컨텍스트와 행동 토큰 사이에 삽입하여, 추론 과정에서 과제·상호작용 관련 정보를 압축된 중간 상태로 점진적으로 조직합니다.
- **미래-정보 쌍 분기 설계(future-informed dual-branch design)** — 배포 가능한 사전 분기(prior branch)와 훈련 전용 사후 분기(posterior branch)를 단일 MoT 시퀀스에 패킹하여 미래 임베딩이 잠재 쿼리를 지도합니다.
- **잠재 공간 정렬 손실** — 두 분기의 잠재 추론 위치에서 은닉 상태를 직접 점별 정렬(Frobenius norm MSE)하여 사전 분기가 현재 문맥만으로 미래-인식 잠재 상태를 추론하도록 유도합니다.
- **붕괴 방지 정규화** — 노름 보존(norm preservation)과 스펙트럼 다양성(spectral diversity)을 통한 경량 anti-collapse 정규화로 잠재 공간의 방향 붕괴·크기 소실을 방지합니다.
- **광범위한 검증** — 6개 시뮬레이션 벤치마크 SOTA 달성 및 3개 실제 로봇 플랫폼(PND Adam-U, Unitree G1, Franka FR3) 12개 과제에서 5개 능력별 suite 전체 1위를 달성합니다.

---

## 🔑 기술 키워드

- **Latent World-Action Model** — 미래 프레임을 생성하지 않고 잠재 공간에서 미래-인식 추론을 수행하는 세계-행동 모델의 새로운 패러다임.
- **Learnable Latent Queries** — 인식과 행동 사이에 삽입된 학습 가능한 슬롯으로, 반복적인 Transformer 전파를 통해 행동 지향 중간 표현을 조직합니다.
- **Prior Branch** — 현재 문맥만으로 잠재 상태를 추론하는 배포 가능한 분기.
- **Posterior Branch** — 미래 관찰 임베딩을 잠재 쿼리 위치에 대체하여 훈련 시에만 사용되는 특권 감독 분기.
- **Dual-Branch Attention Mask** — 공유 컨텍스트 토큰은 양쪽 분기에 보이되, 두 분기 전용 토큰은 서로 attend하지 못하도록 격리하는 이중 마스크.
- **Mixture-of-Transformers** — 액션과 상태 벡터는 Action Expert로, 나머지 신호는 Understanding Expert로 처리하는 이종(heterogeneous) Transformer 구조.
- **Perceiver Resampler** — 동결된 ViT로 인코딩된 미래 관찰을 $`K`$ 개의 잠재 임베딩으로 압축·집계하는 모듈 (사후 분기에서 사용).
- **Anti-Collapse Regularization** — 잠재 상태의 크기 소실(norm collapse)을 막는 $`\mathcal{R}_{\mathrm{norm}}`$ 과 방향 붕괴(directional collapse)를 막는 $`\mathcal{R}_{\mathrm{rank}}`$ 를 결합한 경량 정규화.
- **Universal Async Chunking** — 추론 지연과 제어 주파수를 분리하는 비동기 청크 배포 프로토콜로, Being-H0.5에서 도입되어 3–4 ms/step 체제를 실현합니다.
- **Flow Matching** — 플로우 매칭(flow-matching) — 선형 확률 경로를 따른 속도장 예측으로 행동 청크를 생성하는 VLA 행동 헤드.

---

## 🔬 방법론

### 직관

VLA는 현재 관찰을 행동으로 직접 매핑하기 때문에 "미래가 어떻게 전개될지"를 내부적으로 표현하지 않습니다. 한편 기존 세계-행동 모델(WAM)은 미래 프레임을 픽셀로 생성한 뒤 행동을 결정하는데, 이는 행동과 무관한 시각적 세부사항(텍스처, 조명)까지 모델링하는 데 계산 자원을 낭비합니다.

Being-H0.7의 핵심 통찰은 "미래 정보가 행동을 개선하려면 픽셀로 재구성될 필요가 없다"는 것입니다. 대신 학습 가능한 잠재 쿼리 $`K`$ 개를 멀티모달 컨텍스트 토큰과 행동 토큰 사이에 끼워 넣어, Transformer 순전파 과정에서 이 쿼리들이 점진적으로 행동-지향 중간 표현을 조직하도록 합니다. 추론 시에는 이 쿼리들이 현재 관찰만으로 미래-인식 잠재 상태를 추론합니다.

문제는 "미래-관련 단서"에 대한 명시적 레이블이 없다는 점입니다. 이를 해결하기 위해 훈련 시에만 작동하는 **사후(posterior) 분기**를 도입합니다. 사후 분기는 잠재 쿼리 자리를 미래 관찰 임베딩으로 대체하며, 이 분기의 잠재 추론 위치 은닉 상태가 사전(prior) 분기의 것과 같아지도록 정렬 손실을 적용합니다. 결과적으로 사전 분기는 사후 분기가 미래 관찰로부터 추출한 "행동에 유용한 미래 정보"를 현재 컨텍스트만으로 모사하는 법을 배웁니다. 배포 시에는 사후 분기를 완전히 제거하므로 추가 추론 비용이 없습니다.

이 구조는 V-JEPA 계열이 "예측 대상을 레이블 없이 미래 관찰로부터 암묵적으로 정의한다"는 통찰과 맥을 같이 하지만, 잠재 쿼리를 행동 생성 직전 위치에 명시적으로 배치하고 두 분기를 동시에 최적화한다는 점에서 구별됩니다.

### 아키텍처

**기반 모델 및 MoT 구조**

Being-H0.7은 Being-H0.5 위에 구축됩니다. Understanding Expert로 InternVL3.5, Action Expert로 Qwen3를 사용하는 Mixture-of-Transformers(MoT) 구조를 채택하며, 시각 인코더로는 V-JEPA2.1을 사용합니다(컨텍스트 프레임 인코더는 학습 가능, 미래 프레임 인코더는 동결).

**입력 시퀀스**

> "We insert a set of latent queries $`Q\in\mathbb{R}^{K\times d}`$ before the action chunk, yielding the augmented sequence $`S=\big[x;\,o_{-H:0};\,s;\,Q;\,a_{0:T}\big]`$" (§3.1)

여기서 $`x`$ 는 언어 지시, $`o_{-H:0}`$ 는 관찰 히스토리(horizon $`H=4`$ ), $`s`$ 는 로봇 상태, $`Q`$ 는 학습 가능한 잠재 쿼리( $`K=16`$ ), $`a_{0:T}`$ 는 행동 청크( $`T=20`$ )입니다. 잠재 쿼리는 컨텍스트와 행동 사이의 인터페이스 역할을 하며, 레이어-바이-레이어 Transformer 전파를 통해 정보를 집약합니다.

**사전 분기(prior branch) — 배포 가능**

잠재 쿼리 $`Q`$ 가 현재 컨텍스트에서 행동-유용 잠재 상태를 추론하며, 배포 시 이 분기만 실행됩니다.

**사후 분기(posterior branch) — 훈련 전용**

> "We replace the latent queries in the posterior branch with a compact set of future embeddings of the same shape, so that the two branches remain structurally aligned at the latent reasoning positions." (§3.2)

미래 관찰 $`\tilde{o}_{0:T}`$ 는 동결된 ViT로 인코딩된 뒤 Perceiver Resampler로 집약됩니다:

$$z^{\mathrm{post}}=E(\tilde{o}_{0:T})\in\mathbb{R}^{K\times d}$$

여기서 $`E`$ 는 동결 ViT + Perceiver Resampler로 구성된 시간적 시각 인코더입니다. $`K`$ 와 $`d`$ 는 사전 분기의 잠재 쿼리와 동일하여 두 분기의 잠재 추론 위치가 구조적으로 대응됩니다.

사후 분기는 어떤 미래 정보가 행동 결정에 실제로 유용한지를 암묵적으로 드러내며, 사전 분기가 그것을 현재 컨텍스트만으로 모사하도록 유도하는 특권 교사(privileged teacher) 역할을 합니다.

**이중 분기 주의 마스크**

> "Shared context tokens are visible to both branches, while the prior and posterior branch tokens are not allowed to attend to each other." (§3.3)

두 분기 전용 토큰이 상호 attend하지 못하도록 격리하되, 공유 컨텍스트는 양 분기에 공개합니다. 또한 대응하는 사전·사후 토큰 위치에 동일한 위치 ID를 할당하여 구조적 정렬을 보장합니다.

단일 MoT 순전파 내에서 두 분기를 처리함으로써 컨텍스트 계산을 공유하고 훈련 효율을 높입니다.

![Figure 1 — Latent reasoning and dual-branch design](https://arxiv.org/html/2605.00078/x1.png)

> "Figure 1: Latent reasoning and latent world-action model. Left: Learnable latent queries are inserted to form a latent reasoning space that progressively organizes intermediate hidden states and guides action generation through propagation. Right: Through joint alignment between the dual-branch design, the model learns to reason with future information at inference time, turning into a latent world-action model." (§3)
(좌측은 잠재 쿼리가 컨텍스트와 행동 사이에서 중간 추론 공간을 구성하는 구조를, 우측은 사전·사후 분기 정렬을 통해 미래-인식 잠재 세계-행동 모델로 전환되는 과정을 시각화합니다.)

![Figure 2 — Being-H0.7 Architecture](https://arxiv.org/html/2605.00078/x2.png)

> "Figure 2: Being-H0.7 Architecture. We pack the prior and posterior branches into a single MoT sequence with shared context, where the two branches are optimized simultaneously. The posterior branch replaces latent queries with future embeddings, and the two branches are coupled by hidden-state alignment and lightweight regularization. A dual-branch attention mask is applied to isolate prior and posterior branches while preserving access to the shared context for efficient training." (§3.3)
(두 분기가 단일 MoT 시퀀스에 패킹되어 효율적으로 학습되는 전체 아키텍처를 보여줍니다.)

### 학습 목표 / 손실

**플로우 매칭 손실**

사전·사후 분기 모두에 플로우 매칭 목표를 적용합니다. 정답 행동 청크 $`a`$, 플로우 시간 $`t \in [0,1]`$, 가우시안 노이즈 $`\epsilon \sim \mathcal{N}(0,I)`$ 에 대해 보간 행동 $`a_t = ta + (1-t)\epsilon`$, 목표 속도 $`u_t = a - \epsilon`$ 를 정의합니다. 두 분기의 결합 플로우 매칭 손실은:

$$\mathcal{L}_{\mathrm{FM}}=\mathcal{L}_{\mathrm{FM}}^{\mathrm{prior}}+\mathcal{L}_{\mathrm{FM}}^{\mathrm{post}},\quad\text{where}\ \mathcal{L}_{\mathrm{FM}}^{\mathrm{prior}}=\left\|v_{\theta}^{\mathrm{prior}}(a_{t},c,q)-u_{t}\right\|_{2}^{2},\quad\mathcal{L}_{\mathrm{FM}}^{\mathrm{post}}=\left\|v_{\theta}^{\mathrm{post}}(a_{t},c,z^{\mathrm{post}})-u_{t}\right\|_{2}^{2}$$

플로우 매칭은 사전·사후 양 분기가 각각의 조건(현재 잠재 쿼리 vs 미래 임베딩)으로부터 같은 정답 행동을 예측하도록 학습함으로써, 두 branch가 행동 예측에 유용한 정보를 잠재 공간에서 공유하도록 간접적으로 유도합니다.

**잠재 정렬 손실**

$`\ell`$ 번째 정렬 레이어에서 사전 분기와 사후 분기의 잠재 은닉 상태 $`h_\ell^{\mathrm{prior}}`$, $`h_\ell^{\mathrm{post}}`$ 에 대해 점별(point-wise) 정렬 손실을 적용합니다:

$$\mathcal{L}_{\mathrm{align}}=\frac{1}{L}\sum_{\ell=1}^{L}\frac{1}{|h_{\ell}|}\left\|h_{\ell}^{\mathrm{prior}}-h_{\ell}^{\mathrm{post}}\right\|_{F}^{2}$$

여기서 $`L`$ 은 정렬 레이어 수(마지막 $`L=9`$ 레이어), $`\|\cdot\|_F`$ 는 프로베니우스 노름입니다. 이 손실이 사전 분기의 잠재 쿼리가 사후 분기의 미래-인식 임베딩과 같아지도록 직접 강제하는 핵심 메커니즘입니다.

**붕괴 방지 정규화**

**노름 보존** — 잠재 상태 $`h`$ 의 크기가 임계값 $`\tau`$ 아래로 줄어드는 것을 방지합니다:

$$\mathcal{R}_{\mathrm{norm}}(h)=\left[\mathrm{ReLU}(\tau-\|h\|_{2})\right]^{2}$$

**스펙트럼 다양성** — 한 분기의 잠재 은닉 상태 집합 $`H \in \mathbb{R}^{M \times n}`$ 을 랜덤 $`n`$ 차원 부분 공간에 투영, 행 단위 정규화 $`\hat{H}`$ 로부터 그람 행렬 $`G = \hat{H}\hat{H}^\top`$ 을 계산하고 고유값 $`\{\lambda_i\}`$ 로부터 정규화 스펙트럼 $`p_i = \lambda_i / \sum_j \lambda_j`$ 를 정의합니다:

$$\mathcal{R}_{\mathrm{rank}}(H)=\sum_{i=1}^{M}p_{i}\log p_{i}$$

이 음의 스펙트럼 엔트로피를 최소화하면 더 평탄한 스펙트럼을 유도하여 방향 붕괴를 억제합니다. 이 두 정규화는 잠재 정렬 손실만 적용할 때 발생할 수 있는 trivial solution(크기가 0으로 수렴하거나 모든 쿼리가 같은 방향으로 붕괴하는 현상)을 방지합니다.

**최종 훈련 목표**

$$\mathcal{L}=\mathcal{L}_{\mathrm{FM}}+w_{\mathrm{align}}\mathcal{L}_{\mathrm{align}}+\mathcal{L}_{\mathrm{reg}}$$

여기서 $`\mathcal{L}_{\mathrm{reg}} = w_{\mathrm{norm}}\mathcal{R}_{\mathrm{norm}} + w_{\mathrm{rank}}\mathcal{R}_{\mathrm{rank}}`$ 이고, 가중치는 $`w_{\mathrm{align}}=10^{-3}`$, $`w_{\mathrm{norm}}=w_{\mathrm{rank}}=10^{-4}`$ 입니다.

### 학습 셋업

> "Being-H0.7 is built on top of Being-H0.5, with InternVL3.5 as the understanding expert and Qwen3 as the action expert. For consistent visual embedding spaces across context and future observations, we adopt V-JEPA2.1 for both visual encoders, while keeping the context-frame encoder trainable." (§4.1)

Being-H0.5의 MoT + UniHand 2.0 데이터 포맷 위에 잠재 세계-행동 모델 구조를 추가한 것입니다. 컨텍스트와 미래 프레임에 동일한 V-JEPA2.1을 사용함으로써 두 분기의 시각 임베딩 공간을 일관되게 유지합니다.

**사전학습 설정**
- 관찰 호라이즌: $`H=4`$
- 행동 청크 길이: $`T=20`$
- 잠재 쿼리 수: $`K=16`$
- 정렬 레이어: 마지막 $`L=9`$ Transformer 레이어
- 컨텍스트 이미지: $`224 \times 224`$ 로 리사이즈
- 미래 프레임: $`256 \times 256`$ 으로 리사이즈
- 데이터: UniHand 2.0 포맷 기반 인간·로봇 조작 궤적 혼합
- 배치: 유효 글로벌 배치 크기 ≈ 128 궤적 청크(시퀀스 패킹 사용)
- 가중치: $`w_{\mathrm{align}}=10^{-3}`$, $`w_{\mathrm{norm}}=w_{\mathrm{rank}}=10^{-4}`$

**다운스트림 사후학습(post-training)**
- 행동 생성 목표 + 잠재 정렬 손실만 최적화
- anti-collapse 정규화자는 미적용
- 태스크별 시연 데이터로 파인튜닝

**모델 크기**: 3B 파라미터

---

## 📊 실험 설정과 결과

### 시뮬레이션 벤치마크 — 6개

> "Across all six simulation benchmarks, Being-H0.7 achieves state-of-the-art overall performance, maintaining the highest average rank as detailed in Table 1." (§4.2.2)

| 벤치마크 | Being-H0.7 | Being-H0.5 (2B) | Fast-WAM (6B) | π0 (3B) | LingBot-VA (5B) |
|---|---|---|---|---|---|
| LIBERO | **99.2%** | 98.9% | 97.6% | 94.4% | — |
| LIBERO-plus (zero-shot) | **82.1%** | 78.5% | — | 53.6% | — |
| LIBERO-plus∗ (fine-tuned) | **84.8%** | 83.1% | — | — | — |
| RoboCasa-50 | **62.1%** | 53.5% | — | 42.4% | — |
| GR1 | 49.2% | — | — | — | — |
| CALVIN ABCD→D | **4.67** | 4.63 | — | — | — |
| CALVIN ABC→D | **4.48** | 4.48 | — | — | — |
| RoboTwin 2.0 Easy/Hard | 90.2%/89.6% | — | 91.9%/91.8% | — | 92.9%/91.6% |

- RoboTwin 2.0 Easy→Hard 하락폭: **0.6%p** (Being-H0.7 기준)으로 도메인 랜덤화 강건성이 높습니다.
- GR1(인간형 로봇 양손 조작): ABot-M0(58.3%), starVLA(48.8%) 대비 49.2%로 경쟁력 있음.

> "Being-H0.7 reaches a 99.2% average success rate [on LIBERO] ... On RoboCasa, our model achieves an exceptional 62.1% success rate." (§4.2.2)

### 실제 로봇 실험 — 12개 과제

**플랫폼 및 설정**

| 플랫폼 | 유형 | Body DoF | 손 | 총 DoF | 카메라 | 정책 주파수 |
|---|---|---|---|---|---|---|
| PND Adam-U | 상체 인간형 | 19 | Linkerbot O6 (6 DoF) | 31 | 에고뷰 2개 | 20 Hz |
| Unitree G1 | 양손 인간형 | 14 | Linkerbot O6 (6 DoF) | 26 | 에고뷰 1개 | 10 Hz |
| Franka FR3 | 단일 암 탁상형 | 7 | Linkerbot O6 (6 DoF) | 13 | 외부 1개 + 손목 1개 | 20 Hz |

Unitree G1 백엔드에는 사전학습된 AMO 컨트롤러(50 Hz 전신 균형 제어)가 통합되어, 상체 정책 인터페이스는 동일하게 유지하면서 안정적인 전신 실행을 제공합니다.

**5개 능력별 suite 결과**

> "Being-H0.7 leads on all five suites, spanning reactive, physical, sequential, and generalization-oriented tasks across all three embodiments." (§4.3.3)

- **Dynamic Scene** — 빠르게 굴러가는 공 잡기, 이동 용기에 붓기, 컨베이어 피킹 등 타이밍-민감 과제. Fast-WAM이 베이스라인 중 가장 강하며, Being-H0.7이 추가 마진을 확보.
- **Physical Reasoning** — 피펫 이송, 깔때기 붓기, 의류 접기, 망치-못 등 물리적 결과 예측. Being-H0.5가 가장 가까운 베이스라인.
- **Motion Reasoning** — 궤적 예측·상대 속도·접촉 타이밍 강조. Dynamic Scene과 순서 유사.
- **Long Horizon** — 신발 트리 삽입→박싱, 패키지 스캔→분류 등 다단계 목표 일관성.
- **Generalization** — 배치·높이·용기·객체 인스턴스 변화 하에서의 일반화. π0.5와 Being-H0.5도 경쟁력 있음.

**추론 비용**

> "UAC-enabled Being-H variants move into the 3–4 ms/step regime while keeping the same GPU memory footprint as their non-UAC counterparts." (§4.3.3)
(UAC(Universal Async Chunking) 적용 시 Being-H 계열은 3–4 ms/step 체제에서 동작하며, 테스트 시 미래 생성이 필요한 WAM 대비 추론 오버헤드 없이 배포됩니다.)

![Figure 5 — Suite-level real-robot success rates](https://arxiv.org/html/2605.00078/x5.png)

> "Figure 5: Suite-level real-robot success rates (%). Comparison of Being-H0.7, Being-H0.5, π0.5, and Fast-WAM on the five ability-oriented task suites. Each task is evaluated over 20 blind trials, and each suite score is averaged over all tasks carrying the corresponding suite tag." (§4.3.3)
(Being-H0.7이 5개 suite 전체에서 선두를 유지함을 보여줍니다.)

![Figure 6 — Visualization of the Latent Reasoning](https://arxiv.org/html/2605.00078/x6.png)

> "Figure 6: Visualization of the Latent Reasoning." (§4.3.3)
(현재 관찰과 사전 분기의 잠재 은닉 상태를 함께 조건으로 비디오 생성 모델에 제공하면 미래 상태를 합성할 수 있음을 보여 주며, 잠재 표현이 미래 예측 정보를 실제로 포착하고 있음을 시사합니다.)

---

## ⚖️ 한계

- **사후 분기의 미래 관찰 요구** — 훈련 시에도 미래 관찰이 필요하므로, 미래 프레임이 없는 데이터셋에서는 사후 분기를 적용할 수 없습니다. 데이터 수집 파이프라인이 사전학습에 적합한 형태로 미래 프레임을 포함해야 한다는 추가 제약이 생기며, 이는 범용 로봇 데이터셋 활용을 제한할 수 있습니다.
- **잠재 정렬의 간접성** — 픽셀 수준 미래를 복원하지 않으므로 "어떤 미래 정보가 캡처되었는지"를 직접 검증하기 어렵습니다. Figure 6의 시각화(잠재 상태를 조건으로 비디오 생성)는 간접적 증거이며, 내부 표현이 어떤 predictive factor를 인코딩하는지 해석이 쉽지 않습니다. 잠재 공간의 어떤 차원이 접촉·동역학·어포던스에 대응하는지 불명확합니다.
- **아블레이션 미공개** — 본문에 $`K`$ (잠재 쿼리 수), $`L`$ (정렬 레이어 수), $`w_{\mathrm{align}}`$, 정규화 가중치 등에 대한 아블레이션이 보고되지 않아 각 설계 결정의 기여도가 불명확합니다.
- **일부 시뮬레이션 벤치마크에서 비경쟁** — RoboTwin 2.0과 RoboCasa에서 Fast-WAM(6B)이나 LingBot-VA(5B)가 Being-H0.7(3B)보다 높거나 유사한 경우도 있어, 모델 크기 영향이 분리되지 않습니다. 잠재 접근이 픽셀 기반 WAM 대비 항상 우위는 아닙니다.
- **에고센트릭 데이터 의존성** — Being-H0.5의 UniHand 2.0 포맷(에고센트릭 중심 혼합 데이터)에 의존하므로, 에고센트릭 관점이 없거나 제한적인 환경에서의 전이는 검증되지 않았습니다.
- **훈련 복잡도 및 하이퍼파라미터 민감도** — $`w_{\mathrm{align}}`$, anti-collapse 임계값 $`\tau`$, 정렬 레이어 수 $`L`$ 의 민감도가 보고되지 않아, 다른 태스크나 데이터 분포에서 재현성이 불확실합니다.

---

## ♻️ 재현성

- **코드** — 논문 기준 공개 코드 미확인. 웹사이트(https://research.beingbeyond.com/being-h07)에서 추가 공개 예정 가능성 있으나 현재 미검증.
- **모델 가중치** — 공개 미확인.
- **데이터** — UniHand 2.0 데이터 포맷 기반 사전학습(Being-H0.5에서 도입); 실제 데이터셋 미공개.
- **하드웨어** — 훈련 하드웨어 상세 미명시. 배포 플랫폼은 PND Adam-U, Unitree G1, Franka FR3(Linkerbot O6 손 공통).
- **재현 수준** — 아키텍처와 손실 공식은 충분히 상세하게 기술되어 있으나, 아블레이션 없음 + 코드 미공개로 독립 재현은 어렵습니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

Being-H0.7은 **P5(World Model)** 와 **P4(VLM 사전학습 보존)** 에 직접 관련됩니다.

**P5(World Model)**
- **D28(world-model role)** — v1 결정 "latent dynamics prior + future-prediction auxiliary, co-trained with VLA"와 정확히 일치합니다. Being-H0.7은 사후 분기를 훈련 보조 신호로 사용하며, 추론 시 standalone planner나 eval-in-imagination이 아닌 VLA 내장 잠재 동역학 사전으로 작동합니다.
- **D29(integration architecture)** — v1 결정 "auxiliary head on the shared VLA backbone (Being-H0.7 style)"의 직접적인 구현 레퍼런스입니다. 단일 MoT forward pass 내 이중 분기 처리 구조가 v1 선택을 구체화합니다.
- **D30(prediction space)** — v1 결정 "latent / 3D-flow prediction"을 지지합니다. 픽셀 재구성 없이 잠재 공간에서 미래-인식 표현을 구성하는 방식이 "contact-relevant latent prediction"의 실현입니다.
- **D31(action conditioning)** — 명시적 per-frame action conditioning보다는 미래 관찰 임베딩을 통한 간접 conditioning이므로 v1(LOME/DexWM lineage)과는 부분 합치입니다.
- **D32(egocentric hand-object WM)** — 에고센트릭 인간 비디오(UniHand 2.0)로 사전학습하므로 v1 방향과 일치합니다. 단, 손-객체 세부 world model이라기보다는 범용 조작 잠재 world-action 모델에 가깝습니다.

**P4(VLM 사전학습 보존)**
- **D19(VLM backbone lineage)** — Being-H0.5 기반이므로 P4에서 추적 중인 Being-H 계보의 연장입니다. InternVL3.5(understanding expert) + Qwen3(action expert) + V-JEPA2.1(visual encoder) 조합이 공개됩니다.
- **D22(pretraining data composition)** — UniHand 2.0(에고센트릭 중심 혼합 데이터)을 계속 활용. 에고센트릭-centric corpus의 효과를 Being-H0.7이 추가 검증합니다.

**Identity 긴장/지지** — P5 세계 모델의 역할이 "미래 예측 auxiliary"로 설정된 Identity와 일치합니다. 픽셀 생성 없이 잠재 공간에서 동역학 사전을 학습한다는 방향이 "contact-relevant latent prediction"에 수렴합니다. 다만 Being-H0.7은 손-객체 특화 세계 모델이 아니라 범용 조작 정책이므로, D32의 "hand-object-interaction 세계 모델" 특화와는 거리가 있습니다.

---

## ✨ 핀 논문 대비 델타

**vs. Being-H0.5 (P4 핀 논문, arXiv:2601.12993)**
- Being-H0.5가 cross-embodiment 사전학습 레시피와 UniHand 2.0 데이터 포맷을 제공했다면, Being-H0.7은 그 위에 잠재 세계-행동 모델링 메커니즘(이중 분기 + 잠재 정렬 + anti-collapse 정규화)을 추가합니다.
- 시뮬레이션 전반에서 Being-H0.5 대비 꾸준한 개선(LIBERO 98.9→99.2%, RoboCasa 53.5→62.1%)이 확인됩니다.
- 실제 로봇 5개 suite 전체에서 Being-H0.7이 Being-H0.5를 앞섭니다.

**vs. Fast-WAM (P5 비핀, arXiv:2603.16666)**
- Fast-WAM은 훈련 시 비디오 공동학습을 유지하되 테스트 시 롤아웃을 제거합니다. Being-H0.7은 훈련 시에도 픽셀 생성 없이 잠재 정렬만으로 미래 정보를 주입하므로 훈련 비용이 더 가볍습니다.
- Dynamic Scene과 Motion Reasoning에서 Being-H0.7이 Fast-WAM보다 우위이나, RoboTwin 2.0에서는 Fast-WAM이 앞섭니다.

**vs. VLA-JEPA (P5 핀 논문, arXiv:2602.10098)**
- VLA-JEPA는 JEPA 스타일의 2단계(사전학습 → 행동 헤드 파인튜닝)로 잠재 예측을 활용하는 반면, Being-H0.7은 이중 분기를 단일 forward pass에서 동시 학습합니다. Being-H0.7은 잠재 추론 쿼리를 행동 생성 직전에 명시적으로 배치한다는 점에서 더 직접적인 행동-잠재 결합을 구현합니다.

---

## ⚙️ 의사결정 함의

1. **D29(integration architecture) 구체화** — "auxiliary head on the shared VLA backbone (Being-H0.7 style)"이 단순한 방향 기술에서 구체적 구현으로 격상됩니다. 단일 MoT forward pass 내 이중 분기 패킹 + `dual_branch_attention_mask`가 v1 선택의 구현 레퍼런스가 됩니다.

2. **D30(prediction space) 실험적 확인** — 잠재 예측이 픽셀 예측 대비 훈련 효율과 성능을 동시에 달성할 수 있음을 Being-H0.7이 실증합니다. "latent / 3D-flow" 예측 방향의 정당성이 강화됩니다.

3. **정렬 하이퍼파라미터 초기 기준점** — $`w_{\mathrm{align}}=10^{-3}`$, $`w_{\mathrm{norm}}=w_{\mathrm{rank}}=10^{-4}`$, $`K=16`$, $`L=9`$ (마지막 9개 레이어 정렬)를 초기 config 기준점으로 사용할 수 있습니다.

4. **V-JEPA2.1 시각 인코더** — 컨텍스트와 미래 프레임 모두에 V-JEPA2.1을 사용하는 것이 "일관된 시각 임베딩 공간" 유지에 효과적임을 시사합니다. P2(structured multimodal observation fusion) D9(action/dynamics-aware vision encoder) 선택 시 참고 가능합니다.

5. **UAC 배포 프로토콜** — 3–4 ms/step 체제 확인. 세계 모델 추론 비용 없이 예측적 이점을 달성한다는 것이 P5 세계 모델 통합 시 배포 가능성의 핵심 설계 원칙임을 재확인합니다.

---

## ⚠️ 먼저 검증할 실패 모드

1. **손(hand) 특화 조작 전이 — 가장 저비용 확인** — Being-H0.7 실험은 Linkerbot O6(6 DoF) 손을 사용하는 범용 조작 태스크입니다. 우리 스택의 Sharpa Hand(22 DoF, 비주오택타일)나 xhand로 전이 시 손 DoF 수 및 proprio-tactile 입력 형식 미스매치가 발생합니다. $`K=16`$ 잠재 쿼리가 훨씬 높은 DoF의 손 명령을 충분히 조직할 수 있는지 확인이 필요합니다. 가장 싼 sanity check: Linkerbot O6으로 수행된 Being-H0.7의 손 조작 성공률 vs. 동일 과제를 더 단순한 베이스라인으로 달성 가능한지 비교.

2. **사후 분기용 미래 프레임 수집 파이프라인** — 에고센트릭 데이터에서 미래 관찰 $`\tilde{o}_{0:T}`$ 를 일관되게 추출하는 데이터 파이프라인이 필요합니다. 기존 수집 데이터에 미래 프레임이 표준 포맷으로 포함되어 있는지, 또는 추가 전처리가 필요한지 가장 먼저 확인해야 합니다.

3. **잠재 쿼리 수 $`K`$ 민감도** — $`K=16`$ 이 다양한 태스크 복잡도에서 충분한지 아블레이션 데이터가 없습니다. 손의 22 DoF를 커버하려면 더 많은 쿼리가 필요할 수 있으며, 이는 계산 비용과 트레이드오프입니다.

4. **정렬 손실 가중치 안정성** — $`w_{\mathrm{align}}=10^{-3}`$ 가 우리 데이터 분포(에고센트릭 + 손 중심 조작)에서 훈련을 불안정하게 만들 가능성이 있습니다. 특히 손 조작은 미래 예측 신호가 팔 조작보다 더 다양하고 노이즈가 많을 수 있습니다.

5. **anti-collapse 정규화 없는 다운스트림 파인튜닝** — 사후학습 시 $`\mathcal{L}_{\mathrm{reg}}`$ 를 제거하면 잠재 공간이 태스크 특화 fine-tuning 과정에서 붕괴될 위험이 있습니다. 우리의 소규모 시연 데이터(분 단위)로 파인튜닝 시 이 위험이 더 클 수 있습니다.

6. **에고센트릭 관점 가정** — Being-H0.7의 미래 프레임 인코더(V-JEPA2.1)와 잠재 정렬이 에고센트릭 관점으로 최적화되어 있습니다. 외부 카메라(exo-view) 중심 환경에서의 성능 저하 가능성을 확인해야 합니다.

---

## 💡 컨텍스트 제안

1. **D29 서술 구체화 후보** — `context/P5.md` D29의 "Being-H0.7 latent world-action style" 서술이 이제 구체적 구현 레퍼런스를 갖추었습니다. 단일 MoT forward pass 내 이중 분기 + dual-branch attention mask + 잠재 정렬이 v1 구현 방식으로 명시될 수 있습니다.

2. **Being-H0.7 피닝 상태 확인** — `context/P5.md` §5 핀 목록에 Being-H0.7이 이미 등재되어 있습니다. 분석 결과 D28/D29/D30과의 정렬이 확인되었으므로 현행 Role 설명(`Prior/Posterior latent reasoning (D28/D29)`)이 적절합니다.

3. **V-JEPA2.1 시각 인코더 추적 제안** — InternVL3.5 + Qwen3 + V-JEPA2.1 조합이 Being-H0.7에서 사용됩니다. P2(structured multimodal observation fusion) D9(action/dynamics-aware vision encoder) 후보로 V-JEPA2.1을 `catalogs/models.md`에 추가 검토할 수 있습니다.

> 💡 base 매핑은 `/implement-design analysis/2605.00078/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
