# Paper Analysis — VLA-Adapter: An Effective Paradigm for Tiny-Scale Vision-Language-Action Model

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | VLA-Adapter: An Effective Paradigm for Tiny-Scale Vision-Language-Action Model |
| 저자 | Yihao Wang, Pengxiang Ding, Lingxiao Li, Can Cui, Zirui Ge, Xinyang Tong, Wenxuan Song, Han Zhao, Wei Zhao, Pengxu Hou, Siteng Huang, Yifan Tang, Wenhui Wang, Ru Zhang, Jianyi Liu, Donglin Wang |
| 링크 | [arXiv:2509.09372](https://arxiv.org/abs/2509.09372) · [Website](https://vla-adapter.github.io/) |
| 발행일 / 버전 | 2025-09-11 (v1) · 2025-09-22 (v2) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-09 |
| 관련 Pillar | P4, P1 |
| 태그 | vla-arch, peft |
| 카탈로그 | models/vla/Standalone/VLA-Adapter |

---

## 🧭 한 줄 요약 (TL;DR)

로봇 데이터 사전학습 없이, 동결된 0.5B VLM 의 **모든 중간층에서 뽑은 Raw 표현
과 ActionQuery 표현을 Bridge Attention 으로 액션 공간에 주입**하는 경량 Policy
만으로 7B 급 VLA 와 동급 또는 그 이상의 SOTA 성능을 달성하고, 동시에 가장
빠른 추론 속도를 보인다는 주장입니다. 즉 "대형 VLM + 대규모 사전학습"
의존을 어댑터 설계로 대체할 수 있음을 보입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — VL(시각-언어) 표현을 액션(A) 공간으로 *어떻게* 잇느냐
  (bridging) 라는, VLA 에서 가장 본질적이지만 거의 논의되지 않은 질문을
  체계적으로 규명하고, 그 답을 경량 어댑터로 구현합니다.
- **기존 접근의 한계** — 현재 VLA 는 대규모 임베디드 데이터(OXE, DROID)로 VLM
  을 사전학습해야 성능이 나오므로 학습 비용·VRAM·추론 지연이 크고, 대형 백본에
  의존합니다.
- **본 논문의 가설** — 어떤 *조건(condition)* 을 액션 공간에 주입하느냐가
  핵심이며, VLM 의 **중간층 Raw + 전층 ActionQuery** 를 적절히 결합하면 작은
  백본·동결 백본으로도 충분한 다리를 놓을 수 있다는 가설입니다.
- **왜 지금 중요한가** — VLA 배포 장벽(GPU 메모리, 학습 시간, 추론 throughput)
  이 실사용을 가로막는 상황에서, 단일 컨슈머 GPU 8 시간 학습이라는 비용 구조는
  현장 채택 가능성을 직접 바꿉니다.

---

## 🧩 핵심 기여

- **bridging 패러다임의 체계적 분석 (저자 주장 최초)** — VLM 의 어느 층·어느
  타입(Raw vs ActionQuery)의 조건이 액션 생성에 유효한지 4 분면으로 분해해
  Key Finding 1–3 을 제시합니다.
- **Bridge Attention Policy** — 전층 Raw($`\mathcal{C}_t^{\mathcal{R}}`$)와 전층
  ActionQuery($`\mathcal{C}_t^{\mathcal{AQ}}`$)를 두 개의 cross-attention + 한 개의
  self-attention 으로 통합하고, Raw 주입량을 학습 가능한 게이트 $`\tanh(g)`$ 로
  자율 조절하는 경량(97M) 디코더입니다.
- **Tiny-scale·동결 백본에서 SOTA** — 0.5B Qwen2.5 백본으로 LIBERO 평균 97.3,
  CALVIN ABC→D Avg.len 4.42 를 기록하며 14× 큰 OpenVLA-OFT 와 동급, 백본을
  완전히 동결해도 86.4 의 성능을 유지합니다.
- **추론 효율 SOTA** — 219.2 Hz throughput / 0.0365s latency 로 보고된 VLA 중
  가장 빠르며, 단일 컨슈머 GPU 8 시간 학습을 주장합니다.

---

## 🔑 기술 키워드

- **Bridge Attention** — VL 조건과 액션 잠재 사이에 놓는 "다리": 두 cross-attn(Raw·AQ) + 한 self-attn 을 묶은 단일 어텐션 블록으로, 본 논문 Policy 의 핵심 단위입니다.
- **ActionQuery** — 처음부터 학습되는 쿼리 토큰(기본 64 개). VLM 시퀀스에 삽입되어 멀티모달 정보를 능동적으로 집약하는 인터페이스 역할을 합니다.
- **Raw features** — VLM 중간층에서 직접 추출한 시각-언어 표현($`\mathcal{C}_t^{\mathcal{R}}`$). 의미 정보에 치우친 깊은 층보다 중간층이 액션에 더 유효하다는 발견의 대상입니다.
- **All-layer conditioning** — 단일 층이 아니라 VLM 24 개 층 각각의 latent 를 대응하는 Policy 층에 1:1 로 주입하는 방식. 최적 층 선택을 생략하면서 성능이 더 좋다는 것이 Key Finding 3 입니다.
- **Learnable injection gate** — Raw 주입 비율을 0 으로 초기화한 학습 파라미터 $`g`$ 에 $`\tanh`$ 를 씌워 $`[-1,1]`$ 로 제한, 학습 안정성을 지키며 자율적으로 Raw 기여도를 조절합니다.
- **Frozen backbone VLA** — VLM 을 동결하고 ActionQuery + Policy 만 from-scratch 학습. 대규모 사전학습 없는 작은 백본의 핵심 전제이며 P4(VLM 사전학습 보존) 의 정면 증거입니다.
- **L1-based Policy** — 플로우 매칭/디퓨전 대신 ground-truth 액션과의 L1 회귀로 액션 청크를 직접 예측하는 단순 디코더. 저자 실험상 DiT 보다 빠르고 성능도 우위입니다.
- **Tiny-scale backbone** — Prismatic VLM 위 Qwen2.5-0.5B. 7B 급 대형 백본 의존을 줄이려는 본 논문의 무게중심입니다.

---

## 🔬 방법론

### 직관

VLA-Adapter 는 "큰 VLM 을 로봇 데이터로 사전학습해야 성능이 나온다" 는 통념을
버리고, 동결된 작은 VLM(0.5B) 위에 가벼운 Policy 하나만 새로 학습해 7B 급 성능을
내려는 시도입니다. 출발점은 백본을 키우는 것이 아니라, 시각-언어 표현을 액션으로
어떻게 잇느냐(bridging) 라는 질문 자체입니다.

저자는 이 다리를 두 개의 축으로 분해합니다. 첫째, 무엇을 조건으로 줄 것인가 —
VLM 의 표현을 그대로 가져오는 Raw 와, 액션을 위해 새로 학습하는 ActionQuery 토큰.
둘째, 그 조건을 어느 층에서 뽑을 것인가 — 마지막 층, 중간 층, 아니면 전층. 이
두 축을 실제로 측정해 보면 Raw 는 중간 층이, ActionQuery 는 깊은 층이 유리하고,
층을 고르지 않고 전층을 모두 쓰면 최적 층 탐색 없이도 오히려 더 좋아집니다.

이 발견을 Bridge Attention 이라는 한 블록으로 굳힙니다. 각 Policy 층이 대응하는
VLM 층의 Raw 와 ActionQuery 를 동시에 받되, Raw 는 학습 가능한 게이트로 "필요한
만큼만" 섞고 ActionQuery 는 그대로 받는 비대칭 구조입니다. 액션은 플로우 매칭이나
디퓨전 없이 가장 단순한 형태의 회귀로 예측합니다. 그 결과 백본을 완전히 동결한 채
ActionQuery 와 Policy 만 학습해도 동작합니다.

효과는 곧 배포 비용입니다. 0.5B 동결 백본 + 97M Policy 라는 구성은 단일 GPU 학습과
보고된 VLA 중 가장 빠른 추론으로 이어지며, "대형 VLM + 대규모 로봇 사전학습" 의존을
어댑터 설계로 대체할 수 있다는 것이 이 논문의 메시지입니다.

### 조건 탐색 (4 분면 분석)

방법론의 출발은 VLA 의 배포 병목을 어댑터 설계로 정면 공략하겠다는 동기입니다.

> "However, when confronted with high-dimensional control environments, VLA models still face several bottlenecks, including reliance on large-scale VLMs, slow fine-tuning speed, high GPU memory (VRAM) consumption, and low inference efficiency (throughput) ..." (§1)
(VLA 의 4 대 병목 — 대형 VLM 의존, 느린 파인튜닝, 높은 VRAM, 낮은 추론 효율 —
을 어댑터 설계로 동시에 공략하겠다는 동기 진술입니다.)

이를 위해 bridging 을 (i) 조건 타입(Raw vs ActionQuery)과 (ii) 추출 층(last /
intermediate / all)의 4 분면으로 나눠 LIBERO-Long 에서 실측하고, 다음 세 발견을
도출해 Bridge Attention 설계의 근거로 삼습니다.

> "Key Finding 1. Regarding $`\mathcal{C}_t^{\mathcal{R}}`$, the middle-layer latent performs better than the deep-layer latent." (§3.2)
(Raw 는 *중간층* 이 깊은 층보다 낫습니다 — 깊은 층은 의미 정보에 치우쳐 액션
생성에 덜 유효하고, 중간층이 이미지·텍스트를 더 풍부하게 통합합니다.)

> "Key Finding 2. Regarding $`\mathcal{C}_t^{\mathcal{AQ}}`$, deep-layer latent performs better than other-layer latent." (§3.2)
(ActionQuery 는 처음부터 학습되므로 *깊은 층* 이 멀티모달 정보를 더 잘 집약합니다
— Raw 와 정반대의 층 선호.)

> "Key Finding 3. Multi-layer features perform better." (§3.2)
(전층 사용이 단일 층보다 일반적으로 우수하며, 최적 층 탐색 비용도 없앱니다 —
설계를 범용화하는 근거입니다.)

![Figure 3 — VLA-Adapter framework](https://arxiv.org/html/2509.09372/x3.png)

> "Figure 3: The proposed VLA framework. The key components are the effective condition exploration and Attention design. “ Attention ” specifically includes cross attention with conditions and self attention with itself. In the “ Unified VLA-Adapter Framework ”, “ Attention ” is the Bridge Attention as shown in Section 3.3 . Four conditions about “layer” and “type” are given on the right." (§3.1)
(전체 프레임워크 — 왼쪽 VLM 이 층별 Raw·ActionQuery latent 를 내보내고, 오른쪽
Policy 가 이를 조건으로 액션을 생성합니다. 오른쪽의 4 가지 조건 분면이 §3.2
분석의 대상입니다.)

### 아키텍처

**백본 (VLM).** Prismatic-VLMs 구조를 따르며, 기본 백본은 Qwen2.5-0.5B 입니다.
입력은 3rd-view 이미지·gripper 이미지·instruction·ActionQuery 의 네 가지이며,
DINOv2 + SigLIP 이 비전 임베딩을, 토크나이저가 언어를 처리합니다.

> "At timestep $`t`$, the input into VLM consists of $`\{\mathcal{X}_{t}^{v},\mathcal{X}_{t}^{g},\mathcal{L}_{t},\mathcal{AQ}_{t}\}`$ ... The outputs are the specified-layer Raw latent $`\mathcal{C}_{t}^{\mathcal{R}}`$ and ActionQuery latent $`\mathcal{C}_{t}^{\mathcal{AQ}}`$. They serve as the conditions for Policy." (§3.1)
(VLM 의 출력은 두 종류의 조건 latent 입니다 — 층별 Raw($`\mathcal{C}_t^{\mathcal{R}}`$)
와 ActionQuery($`\mathcal{C}_t^{\mathcal{AQ}}`$). 둘 다 Policy 의 조건으로 들어갑니다.)

**백본 스케일 실험.** 0.5B(Qwen2.5)·7B(LLaMA2 Prismatic)·OpenVLA-7B(로봇
사전학습) 세 백본을 비교한 결과, 스케일을 키워서 얻는 이득이 제한적이어서
효율을 위해 0.5B 를 기본값으로 채택합니다.

**Policy (L1 기반).** Policy 층 수를 VLM 층 수와 동일(M=24)하게 두고, 각
Policy 층이 대응하는 VLM 층의 조건을 받습니다. 입력은
$`\{\mathcal{C}_{t}^{\mathcal{R}},\mathcal{C}_{t}^{\mathcal{AQ}},\mathbf{A}^{\tau=0}_{t},\mathcal{P}_{t}\}`$
이며, $`\tau`$ 는 Policy 층 인덱스($`0\leq\tau\leq M-1`$)입니다.

- 초기 액션 $`\mathbf{A}^{0}_{t}`$ 는 H-step 의 전부-0 벡터로, LN+MLP 를 거쳐
  $`\widetilde{\mathbf{A}}^{0}_{t}`$ 가 됩니다.
- proprioception $`\mathcal{P}_{t}`$ 는 2-layer MLP 로 $`\sigma_0(\mathcal{P}_t)`$ 임베딩이 됩니다.
- 각 층은 Bridge Attention + residual FFN 으로 구성되며, 출력은 H-step 액션 청크 $`\mathbf{A}^{M-1}_{t}`$ 입니다.

![Figure 5 — Policy with Bridge Attention](https://arxiv.org/html/2509.09372/x5.png)

> "Figure 5: The Policy with Bridge Attention. The Policy parameters are only 97M when the backbone is Qwen2.5-0.5B. Each-layer $`\mathcal{C}_t^{\mathcal{R}}`$ and $`\mathcal{C}_t^{\mathcal{AQ}}`$ are integrated in Bridge Attention with the corresponding-layer action latent. Bridge Attention maps VL to Action to the greatest extent. The degree of $`\mathcal{C}_t^{\mathcal{R}}`$ injection is learnable, ensuring the performance and stability of training." (§3.3)
(Policy 는 단 97M 파라미터. 각 층의 Raw·ActionQuery 가 대응 액션 latent 와
Bridge Attention 으로 통합되며, Raw 주입 정도는 학습 가능합니다.)

**Bridge Attention (핵심 단위).** 두 개의 cross-attention 과 한 개의
self-attention 으로 구성됩니다.

1. **CA₁ (Raw 주입)** — $`\mathcal{C}_t^{\mathcal{R}}`$ 를 MLP $`\sigma_1`$ 로
   $`K_1,V_1`$ 로, 액션 latent $`\widetilde{\mathbf{A}}^{\tau}_{t}`$ 를 $`Q_1`$ 로
   써서 $`\text{CA}_1(\widetilde{\mathbf{A}}^{\tau}_{t},\sigma_1(\mathcal{C}_t^{\mathcal{R}}))`$.
2. **CA₂ (ActionQuery + proprio 주입)** — $`\mathcal{C}_t^{\mathcal{AQ}}`$ 를
   $`\sigma_0(\mathcal{P}_t)`$ 와 concat 후 MLP $`\sigma_2`$ 로 $`K_2,V_2`$, 액션
   latent 를 $`Q_2`$ 로.
3. **SA (self-attention)** — $`\widetilde{\mathbf{A}}^{\tau}_{t}`$ 가 $`Q,K,V`$ 모두.

핵심은 Raw 기여를 학습 게이트로 조절하는 부분입니다.

> "To selectively inject certain $`\mathcal{C}_t^{\mathcal{R}}`$ into the action space of the Policy, we introduce a learning parameter Ratio $`g`$ to modulate the influence of $`\text{CA}_1`$ ... $`g`$ is initialized to 0 value, and the $`\tanh`$ activation function is utilized $`\tanh(g)\in[-1,1]`$ to prevent extreme values from destabilizing the distribution." (§3.3)
(게이트 $`g`$ 는 0 으로 초기화 → 학습 초기에는 Raw 기여가 0(=ActionQuery 위주)
에서 출발하고, $`\tanh`$ 로 $`[-1,1]`$ 에 가둬 분포 붕괴를 막습니다. 즉 Raw 는
"필요한 만큼만" 자율적으로 끌어오는 잔차 신호입니다.)

세 어텐션을 concat 해 $`\widehat{\mathbf{A}}_{t}^{\tau}`$ 를 얻습니다 (식 1):

$$\widehat{\mathbf{A}}_{t}^{\tau}=\left[\text{CA}_{1}\left(\widetilde{\mathbf{A}}^{\tau}_{t},\sigma_{1}(\mathcal{C}_{t}^{\mathcal{R}})\right)\cdot\tanh(g),\ \text{CA}_{2}\left(\widetilde{\mathbf{A}}^{\tau}_{t},\sigma_{2}[\mathcal{C}_{t}^{\mathcal{AQ}},\sigma_{0}(\mathcal{P}_{t})]\right),\ \text{SA}\left(\widetilde{\mathbf{A}}^{\tau}_{t},\widetilde{\mathbf{A}}^{\tau}_{t}\right)\right]$$

이후 residual FFN 으로 $`\widetilde{\mathbf{A}}^{\tau+1}_{t}`$ 를 얻고, M-1 층까지
반복한 뒤 LN+MLP 로 액션 청크 $`\mathbf{A}^{M-1}_{t}`$ 를 출력합니다.

> 주: 식 (1) 에서 ActionQuery(CA₂) 의 주입 비율은 1 로 고정이고 Raw(CA₁) 만
> $`\tanh(g)`$ 로 조절합니다 — 이 비대칭이 §4.5 ablation(Table 8)의 핵심 결론과
> 직결됩니다.

**DiT 변형 (보조).** DiT(Diffusion Transformer) 기반 Policy 도 설계했으나, 본
논문 초점이 아니며 L1 기반이 성능·추론 속도에서 일반적으로 우월하다고 보고하고
최종적으로 L1 을 채택합니다 (Appendix B).

### 학습 목표 / 손실

end-to-end 로 학습하며 Policy 는 from-scratch 입니다. 손실은 단순 L1 회귀입니다
(식 2):

$$\min_{\theta}\mathcal{J}(\theta)=\mathbb{E}_{\mathbf{A}_{t},\mathcal{C}_{t}^{\mathcal{R}},\mathcal{C}_{t}^{\mathcal{AQ}},\sigma_{0}(\mathcal{P}_{t}),\tau}\Big[\big\|\pi_{\theta}(\mathbf{A}_{t}^{\tau},\mathcal{C}_{t}^{\mathcal{R}},\mathcal{C}_{t}^{\mathcal{AQ}},\sigma_{0}(\mathcal{P}_{t}),\tau)-\mathbf{A}_{t}\big\|_{1}\Big]$$

> "The training is conducted end-to-end, with the Policy trained from scratch. ... We train VLA-Adapter model $`\pi_{\theta}(\cdot)`$ with the objective:" (§3.4)
(플로우 매칭/디퓨전 노이즈 스케줄이 아니라 GT 액션 trajectory $`\mathbf{A}_t`$ 와의
L1 거리를 최소화하는 가장 단순한 형태입니다. 조건·proprio·층 인덱스 $`\tau`$ 에
대해 기대값을 취합니다.)

### 학습 셋업

- **옵티마이저** — AdamW, **LoRA 스킴** 적용 (§F.1).
- **학습률 / 스케줄** — 1e-4, cosine-annealing + warmup(전체의 10%).
- **배치 / 스텝** — batch 16, 최대 150,000 step.
- **하드웨어** — 학습·실험은 4× NVIDIA H100 (§4). 별도로 "단일 컨슈머 GPU 8
  시간" 학습이 가능하다고 abstract 에서 주장합니다 (두 진술은 다른 셋업임에
  유의).
- **하이퍼파라미터** (§F.2, Table F2):

  | 항목 | 값 |
  |---|---|
  | Backbone | Qwen2.5-0.5B |
  | Layer ($`\tau`$ / $`M`$) | 24 |
  | Number of ActionQuery | 64 |
  | Hidden size | 896 |
  | Attention head | 8 |
  | Action chunk ($`H`$) | 8 |
  | Intermediate layers of VLM | 1–24 |
  | Policy trainable params | 97.3M |
  | VLA-Adapter total trainable | 197.2M |

---

## 📊 실험 설정과 결과

평가는 시뮬레이션 LIBERO(Spatial/Object/Goal/Long) + CALVIN ABC→D(zero-shot
일반화) + 실제 로봇(6-DOF Synria Alicia-D)으로 구성됩니다. 지표는 Success
Rate(0–100)와 CALVIN 의 Avg.len(0–5)입니다. 각 subtask 는 50 회 반복 평가합니다.

### LIBERO 전체 성능 (Table 5)

| Method | Params(B) | Spatial | Object | Goal | Long | Avg. |
|---|---|---|---|---|---|---|
| OpenVLA-OFT (RSS) | 7 | 97.6 | 98.4 | 97.9 | 94.5 | 97.1 |
| π0 (RSS) | 3 | 96.8 | 98.8 | 95.8 | 85.2 | 94.2 |
| GR00T N1 | 2 | 94.4 | 97.6 | 93.0 | 90.6 | 93.9 |
| SmolVLA | 2.2 | 93.0 | 94.0 | 91.0 | 77.0 | 88.8 |
| VLA-OS | 0.5 | 87.0 | 96.5 | 92.7 | 66.0 | 85.6 |
| Diffusion Policy | — | 78.3 | 92.5 | 68.3 | 50.5 | 72.4 |
| **VLA-Adapter (Ours)** | **0.5** | 97.8 | 99.2 | 97.2 | 95.0 | **97.3** |
| **VLA-Adapter-Pro (Ours)** | **0.5** | 99.6 | 99.6 | 98.2 | 96.4 | **98.5** |

> "VLA-Adapter, using only a tiny-scale backbone, can achieve performance comparable to OpenVLA-OFT with 14 $`\times`$ larger. ... VLA-Adapter has a notable advantage of 29.0% over VLA-OS with the same-scale backbone on LIBERO-Long." (§4.2, Table 5)
(0.5B 백본으로 14× 큰 OpenVLA-OFT(7B)와 동급 평균(97.3 vs 97.1)을 내고, 같은
0.5B 의 VLA-OS 대비 LIBERO-Long 에서 95.0 vs 66.0 으로 29.0%p 앞섭니다 — 디코더
설계의 효과를 같은-스케일 비교로 분리한 핵심 수치.)

### bridging 패러다임의 필요성 (Table 2 · Table 3)

세 백본(B1=Qwen2.5-0.5B, B2=LLaMA2-7B, B3=OpenVLA-7B 로봇 사전학습)에서
OpenVLA-OFT 의 bridging 방식과 자사 방식을 LoRA 파인튜닝으로 비교합니다.

| 백본 (LoRA FT) | +OFT | +Ours |
|---|---|---|
| B1 (0.5B, no robot-pretrain) | 85.8 | 95.0 (9.2%↑) |
| B2 (7B, no robot-pretrain) | 87.5 | 95.2 (7.7%↑) |
| B3 (OpenVLA-7B, robot-pretrain) | 94.5 | 95.4 (0.9%↑) |

> "VLA-Adapter improvement is obvious when VLMs without robotic pre-training." (§4.1, Table 2)
(로봇 사전학습이 *없는* 백본(B1/B2)일수록 자사 어댑터의 이득이 큽니다 —
사전학습된 B3 에선 마지막 층 표현이 이미 액션 도메인에 맞아 단순 MLP 로도 충분해
이득이 0.9%p 로 줄어듭니다. 즉 어댑터는 "사전학습 부재를 보상"하는 장치라는
해석.)

백본을 **완전 동결**했을 때(ActionQuery+Policy 만 from-scratch):

| Frozen 백본 | OpenVLA-OFT | SmolVLA | VLA-Adapter |
|---|---|---|---|
| Success Rate (%) | 0.0 | 77.0 | **86.4** |

> "Fortunately, VLA-Adapter remains effective when the backbone is frozen. Only the ActionQuery and Policy are trained from scratch." (§4.1)
(OpenVLA-OFT 는 동결 시 0.0 으로 완전 붕괴 — Appendix H 에 따르면 OFT 의 학습
토큰이 mask(전부-0) 형태로 VLM 에 입력되어 동결 시 학습되지 않기 때문. 반면
VLA-Adapter 의 ActionQuery 는 VLM 시퀀스에 삽입돼 attention 에 참여하는 독립
학습 토큰이라 동결 백본에서도 86.4 를 유지합니다. 이것이 P4 의 정면 증거.)

### 추론 효율 (Table 4)

| Efficiency | OpenVLA | OFT (wo $`\mathcal{X}_t^{g}`$, $`\mathcal{P}`$) | OpenVLA-OFT | VLA-Adapter |
|---|---|---|---|---|
| Throughput (Hz) ↑ | 4.2 | 109.7 | 71.4 | **219.2** |
| Latency (Sec) ↓ | 0.2396 | 0.0729 | 0.1120 | **0.0365** |

(8-dim action chunk 기준. VLA-Adapter 가 가장 빠른 throughput·최저 latency 를
기록 — gripper 이미지·proprio 를 빼 가장 빠르게 만든 OFT 변형(109.7 Hz)보다도
2× 빠릅니다.)

### CALVIN ABC→D zero-shot 일반화 (Table 6)

| Method | Params(B) | Avg. len ↑ |
|---|---|---|
| OpenVLA-OFT | 7 | 4.10 |
| UniVLA | 7 | 3.80 |
| VPP | 1.5 | 4.33 |
| Seer Large | 0.57 | 4.28 |
| **VLA-Adapter (Ours)** | 0.5 | **4.42** |
| **VLA-Adapter-Pro (Ours)** | 0.5 | **4.50** |

(ABC 환경 학습 → D 환경 평가의 zero-shot 셋업에서 Avg.len 4.42 로 7B OFT(4.10)
와 1.5B VPP(4.33)를 앞섭니다 — 작은 백본이 일반화에서 손해를 보지 않는다는
주장의 근거.)

### Ablation — 조건 4 분면이 왜 둘 다 필요한가

![Figure 4 — four conditions comparison](https://arxiv.org/html/2509.09372/x4.png)

> "Figure 4: Comparison of four conditions in the VLA-Adapter framework on the LIBERO-Long. Blue and Green lines are single-layer $`\mathcal{C}_{t}^{\mathcal{R}}`$ and single-layer $`\mathcal{C}_{t}^{\mathcal{AQ}}`$ ... Blue and Green columns are all-layer $`\mathcal{C}_{t}^{\mathcal{R}}`$ and all-layer $`\mathcal{C}_{t}^{\mathcal{AQ}}`$ ..." (§3.2)
(Raw 의 층별 곡선은 중간층에서, ActionQuery 의 곡선은 깊은 층에서 정점을 찍어
Key Finding 1·2 를 시각화합니다.)

**조건 타입 비교 (Table 7, LIBERO-Long SR).** 기존 대표 패러다임을 한 표로
재현합니다.

| Layer | Raw | ActionQuery | Style | SR ↑ |
|---|---|---|---|---|
| Last | ✓ | ✗ | RoboVLMs | 85.8 |
| Last | ✗ | ✓ | OpenVLA-OFT | 90.2 |
| Intermediate | ✓ | ✗ | GR00T N1 | 88.4 |
| All | ✓ | ✗ | π0 | 90.6 |
| All | ✗ | ✓ | N/A | 92.6 |
| All | ✓ | ✓ | **VLA-Adapter** | **95.0** |

> "This result demonstrates that using both all-layer Raw and ActionQuery achieves superior performance, indirectly validating the superiority of our bridge paradigm." (§4.5, Table 7)
(각 행이 실제 기존 연구의 bridging 방식에 대응합니다 — π0=전층 Raw(90.6),
OFT=마지막층 AQ(90.2), GR00T N1=중간층 Raw(88.4). 전층 AQ 단독(92.6)이 이미
이들을 앞서고, 전층 Raw+AQ 결합(95.0)이 최고. Bridge Attention 의 "둘 다" 설계가
정당화됩니다.)

**주입 정도 ablation (Table 8).** Raw·AQ 의 게이트 조합을 바꿔 비대칭 설계를
검증합니다.

| # | Raw 주입 | ActionQuery 주입 | SR (%) |
|---|---|---|---|
| 1) **VLA-Adapter** | $`\tanh(g)`$ | 1 | **95.0** |
| 2) | 1 | 1 | 91.4 |
| 3) | 1 | $`\tanh(g)`$ | 91.0 |
| 4) | $`\tanh(g)`$ | $`\tanh(g)`$ | 92.6 |

> "From 1) and 4), $`\mathcal{C}_{t}^{\mathcal{AQ}}`$ aggregates multimodal information, which is beneficial for action generation; it needs to be injected fully into Policy. This result confirms that the Bridge Attention is effective." (§4.5, Table 8)
(1) vs 2): Raw 를 1 로 풀로 주입하면(91.4) 오히려 떨어지므로 Raw 는 게이트로
"선별 주입" 해야 합니다. 1) vs 3)/4): AQ 는 게이트로 줄이면(91.0/92.6) 손해이므로
풀로 주입해야 합니다. 즉 **Raw=학습 게이트, AQ=고정 1** 의 비대칭이 최적이라는
직접 증거.)

**ActionQuery 개수 (Figure 8).** 1/4/8/16/64/128/256/512 를 스윕한 결과 64 가
최적 — 너무 적으면 멀티모달 집약이 약해지고, 너무 많으면 중복으로 간섭합니다.

![Figure 8 — number of ActionQuery](https://arxiv.org/html/2509.09372/x8.png)

> "Figure 8: Comparison of the different numbers of ActionQuery. The blue line shows the result of using only the last-layer ActionQuery. The red star shows the result of the full VLA-Adapter." (§4.5)
(개수-성능 곡선이 64 부근에서 정점을 찍고 이후 하락 — 64 를 성능·효율의 균형점
으로 선택한 근거입니다.)

### 실제 로봇 (Figure 7, 정성)

6-DOF Synria Alicia-D + 1-DOF gripper, Logitech C920e(3rd-view) + RealSense
D405(gripper). pick-and-place, lateral block relocation, block stacking,
long-horizon(spoon→cup→plate) 4 범주를 각 10 회 평균하며 ACT·OFT 변형과
비교합니다. 수치 표는 본문에 없고 막대그래프로만 제시됩니다(미확보 수치는
인용하지 않음).

---

## ⚖️ 한계

**저자 명시 한계 (§6)**

- **일반화의 미성숙** — 대규모 임베디드 사전학습이 없고 스케일이 작아, 실제
  로봇 시스템에서의 일반화는 개선이 필요하다고 직접 인정합니다.
- **조건 품질 의존** — Policy 가 생성하는 액션 품질이 VLM 이 제공하는 조건과 그
  사용 방식에 종속됩니다 — 조건이 빈약하면 어댑터도 한계.
- **단순 학습 과정** — 학습이 L1 회귀로 비교적 단순하며, RL 등 복잡한 과정은
  미탐구 영역으로 남깁니다.

**추론된 갭 (본 분석)**

- **평가 도메인이 그리퍼-팔에 한정** — LIBERO/CALVIN/실로봇 모두 평행 그리퍼
  (1-DOF) + 6-DOF 팔. 다지(多指) 손·접촉 집약 과제에서의 거동은 전혀 검증되지
  않았습니다. 우리 스택(22-DOF Sharpa, 촉각)으로의 외삽 근거가 0 입니다.
- **L1 vs 플로우 매칭의 표현력** — L1 회귀는 멀티모달 액션 분포(여러 정답
  궤적)를 평균으로 뭉갤 위험이 있습니다. LIBERO 류 단봉 분포에서는 문제없으나,
  손재주 조작의 다봉 접촉 전략에서 한계가 드러날 수 있습니다. 저자도 DiT 를
  대안으로 두었으나 "초점 아님"으로 비교를 Appendix 로 미뤘습니다.
- **"동결이면 OFT 가 0.0" 의 일반화 위험** — Table 3 의 0.0 은 특정 구현(mask
  토큰)의 산물(Appendix H)이지 "last-layer 표현은 동결 시 무용" 의 일반 명제가
  아닙니다. 우리 백본(π0/PaliGemma)은 OFT 와 토큰 처리 방식이 달라 그대로
  외삽되지 않습니다.
- **proprioception 의 비중 불명** — CA₂ 에서 ActionQuery 와 proprio 를 concat 해
  넣지만, proprio 단독 기여를 분리하는 ablation 이 없습니다. 손 관절·촉각이
  핵심인 우리 설정에선 이 부분이 가장 불확실합니다.
- **VLM 사전학습 보존(forgetting) 측정 부재** — 백본을 동결하므로 "망각" 은
  정의상 0 이지만, 그 대가로 VLM 의 의미 지식이 액션에 *얼마나* 전달되는지(prior
  활용도)는 정량화되지 않습니다 — P4 관점에서 동결이 보존인지 사장(死藏)인지
  구분이 안 됩니다.

---

## ♻️ 재현성

- **본문 확보** — arXiv HTML 전문 확보. 방법·하이퍼파라미터(Appendix F)·아키텍처
  코드 스니펫(Appendix H/I)까지 공개되어 재현 정보는 비교적 풍부합니다.
- **프로젝트 페이지** — [vla-adapter.github.io](https://vla-adapter.github.io/)
  존재(본문·abstract 에 명시). 본 분석 시점 코드/가중치 리포지토리 URL 은 본문
  에서 확정되지 않아 링크에 포함하지 않았습니다(날조 금지 원칙).
- **데이터** — LIBERO(공개), CALVIN ABC→D(공개) 표준 벤치마크. 실로봇 데이터는
  자체 수집(미공개로 추정).
- **하드웨어** — 학습 4× H100(150k step, batch 16). abstract 의 "단일 컨슈머
  GPU 8 시간" 은 별도 셋업으로, 본문에 그 구체 구성은 명시되지 않았습니다.
- **VLA-Adapter-Pro** — Appendix I 에 핵심 아키텍처 코드 공개(투영층 분리 +
  RoPE 추가, FiLM 제거, 파라미터 ~207MB). 본편 대비 LIBERO 97.3→98.5,
  CALVIN 4.42→4.50.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P4 (VLM 사전학습 보존) — 1차 연결.** 본 논문은 P4 §5 Tracked Literature 에
  이미 "VLA-Adapter (Bridge Attention)" 로 추적 중인 논문입니다(2026-05 rebalance
  에서 핀 강등, 추적 유지).
  - **D19 (VLM FT range)** — v1 선택은 (a) 전체 VLM 동결 + 액션 전문가만.
    VLA-Adapter 의 frozen-backbone 86.4 결과(Table 3)는 **D19(a) 가 실제로 강한
    성능을 낼 수 있다는 정면 증거** 입니다. 단, "마지막 층만 MLP" 가 아니라
    "전층 조건 + 어댑터" 가 있어야 한다는 *조건부* 지지입니다.
  - **D20 (prior-preservation strategy: action-side adapter)** — v1 은 "P1 의
    분할 헤드 = 어댑터, 백본 무손상". VLA-Adapter 는 바로 그 패턴의 강화판 —
    백본 동결 + 전층(1–24) Raw·ActionQuery 를 탭하는 풍부한 액션측 어댑터입니다.
    우리 D20 의 "분할 헤드만" 보다 *조건 탭이 두텁다* 는 점이 가장 큰 차이.
  - **D19 (백본 lineage)** — Qwen2.5-0.5B Prismatic(로봇 사전학습 없음)은
    `models.md` 의 tiny-lineage 후보를 한 점 추가합니다.
- **P1 (이종 Body/Hand 액션 전문가) — 2차 연결.**
  - **D4 (Body↔Hand 정보 공유, v1=FiLM)** — VLA-Adapter-Pro 코드가 명시적으로
    `# FiLM is useless` 라고 적고 FiLM 변조를 제거(Appendix I)했습니다. 맥락은
    다르지만(조건 변조 vs body→hand) **D4 의 FiLM 선택에 대한 경계 신호** 입니다.
  - **D7 (π 백본 통합/분할, v1=π0 액션 전문가 슬라이스)** — VLA-Adapter 는 π 를
    슬라이스하지 않고 별도 Policy 를 붙이되 *Policy 층=VLM 층(24)* 1:1 대응을
    택합니다. D7 과 다른 통합 방식의 구체 예시.
  - **D23 (action representation, v1=continuous flow-matching)** — VLA-Adapter
    는 L1 회귀를 채택하고 자사 실험상 DiT 보다 우월하다고 보고 — v1 의 플로우
    매칭 선택과 *긴장* 관계(아래 ⚙️ 참조).
- **Identity 긴장/지지** — Identity 는 "dexterity 를 VLA-level 에서, 보정 모듈이
  아니라 직접" 설계하자는 입장. VLA-Adapter 의 어댑터는 "동결 VLA 위 보정/주입"
  에 가까워 *Antagonist A(보정/잔차 모듈)* 의 색채가 있으나, 보정이 아니라 *액션
  생성 본체* 를 처음부터 학습한다는 점에서 분포-한정 비판을 일부 비껴갑니다 —
  경계선상의 사례.

---

## ✨ 핀 논문 대비 델타

- **vs π0 ([arXiv:2410.24164](https://arxiv.org/abs/2410.24164), P4/P1 핀)** —
  π0 는 전층 Raw 만 조건으로 쓰는 bridging(Table 7 에서 90.6)입니다. VLA-Adapter
  의 진짜 새로움은 (1) **전층 ActionQuery 를 Raw 와 동시에** 쓰고(둘 다=95.0),
  (2) Raw 만 학습 게이트 $`\tanh(g)`$ 로 비대칭 주입하며, (3) 이를 0.5B 동결
  백본에서 구현했다는 점입니다. π0 는 플로우 매칭, VLA-Adapter 는 L1.
- **vs SmolVLA ([arXiv 추적], frozen-VLM 전용 연구)** — frozen 셋업 직접 비교에서
  86.4 vs 77.0 (Table 3). "동결 VLM 으로도 VLA 를 만든다" 는 같은 목표에서 전층
  조건 + Bridge Attention 이 더 나은 다리임을 보입니다.
- **vs UAM ([arXiv:2605.15735](https://arxiv.org/abs/2605.15735), P4 핀)** — UAM
  은 *동결 없이* dual-stream(Ventral/Dorsal)으로 prior 를 보존. VLA-Adapter 는
  정반대 극단 — *완전 동결 + tiny 백본 + 액션측 어댑터*. D19(a) freeze 전제의
  강한 증거이자, UAM 이 도전하는 "freeze 가 정말 필요한가" 질문의 반대편 데이터점.
- **vs OpenVLA-OFT (본문 주 비교군)** — OFT 는 마지막 층 학습 토큰(mask 형태).
  VLA-Adapter 는 전층 + 독립 ActionQuery 토큰으로, 특히 *동결 시* OFT(0.0)와
  결정적으로 갈립니다.

---

## ⚙️ 의사결정 함의

- **D20 어댑터 설계 — "전층 조건 탭" 을 후보로 승격.** 현재 우리 D20 은 "P1 분할
  헤드 = 어댑터(백본 무손상)" 인데, VLA-Adapter 는 *마지막 층이 아니라 VLM 전층
  (1–24)의 Raw + ActionQuery 를 대응 Policy 층에 1:1 주입* 하는 것이 동결 백본의
  성능을 끌어올린 핵심임을 보입니다. → **구체 액션**: Body/Hand 액션 전문가에
  조건을 줄 때 `condition_layers = "all"` (전층 탭) vs `"last"` 를 ablation 으로
  넣고, Raw 측에만 `tanh` 게이트(0 초기화) 파라미터를 추가하는 것을 검토.
- **D19 동결 전제 — 조건부로 강화.** "동결해도 86.4" 는 D19(a) 를 지지하나,
  *조건이 전층 + 어댑터일 때만* 성립합니다. → **구체 메트릭**: 우리 freeze
  실험에서 `last-layer-only` baseline 을 반드시 함께 돌려, 동결 성능이 어댑터
  덕인지 백본 덕인지 분리(Table 3 의 OFT=0.0 교훈).
- **D23 액션 표현 — L1 vs flow-matching 재검토 트리거.** VLA-Adapter 는 L1 이
  DiT 보다 빠르고 성능도 낫다고 보고. 우리 v1 은 flow-matching(π 일관). →
  **구체 키**: 손재주 조작의 *다봉 접촉 전략* 에서 L1 의 mode-averaging 이
  문제되는지 소규모 비교(`action_head: {l1, flow_matching}`) — LIBERO 류 단봉
  과제 결과(이 논문)를 우리 도메인에 그대로 옮기지 말 것.
- **D4 FiLM — 약한 negative 신호 기록.** VLA-Adapter-Pro 가 FiLM 을 "useless" 로
  제거. → 우리 D4(FiLM body→hand)의 검증 우선순위를 올리되, *맥락이 다름* (조건
  변조 ≠ body→hand 변조)을 명심하고 직접 실험으로만 판단.
- **추론 예산** — 219.2 Hz / 0.0365s 는 System1 정책 루프 예산에 여유를 의미.
  단 8-dim 평행 그리퍼 기준이므로 22-DOF 손 + 촉각 입력 시 재측정 필요.

---

## ⚠️ 먼저 검증할 실패 모드

가장 싼 sanity check 부터.

1. **(가장 쌈) 평행 그리퍼 → 다지 손 도메인 갭** — 모든 결과가 1-DOF gripper +
   6-DOF 팔. 우리의 22-DOF 손/촉각으로 전이된다는 근거가 0. **체크**: 코드를
   끌어오기 전, 액션 차원만 우리 손 DOF 로 바꾼 toy 회귀로 L1 head 가
   고차원 손 관절을 안정적으로 맞추는지부터 확인(데이터 없이 합성 trajectory).
2. **L1 mode-averaging** — 단봉 분포(LIBERO)에서의 95.0 이 다봉 접촉 전략에서
   재현될지 불확실. **체크**: 동일 상태에서 두 가지 유효 grasp 가 있는 합성
   과제로 L1 vs flow-matching 의 분포 붕괴를 비교(소규모, 반나절).
3. **동결 백본 prior 활용도** — "freeze=86.4" 가 우리 π0/PaliGemma 백본에서도
   성립하는지는 토큰 처리 방식이 달라 불명. **체크**: 우리 백본에서 전층 조건
   탭 어댑터 vs 마지막층 MLP 를 frozen 으로 비교 — OFT 가 0.0 이었던 함정 재현
   여부 확인.
4. **proprio·촉각의 비중** — CA₂ 가 ActionQuery+proprio concat 인데 proprio 단독
   ablation 부재. 손 관절+촉각이 핵심인 우리 설정에서 이 입력 경로가 병목일 수
   있음. **체크**: proprio 채널을 0 으로 마스킹한 ablation 으로 어댑터의 proprio
   의존도 측정.
5. **(가장 비쌈) 학습 안정성** — 게이트 $`g`$=0 초기화 + $`\tanh`$ 가 우리 고DOF·
   다손실 셋업에서도 분포 붕괴를 막는지. **체크**: 실제 우리 데이터로 학습해
   $`\tanh(g)`$ 궤적이 발산/포화하지 않는지 로깅(가장 늦게, 데이터 준비 후).

---

## 💡 컨텍스트 제안

- **P4 §5 / P1 §5 추적 메모 갱신 제안 (핀 교체는 아님)** — VLA-Adapter 는 이미
  P4 추적 항목입니다. 본 분석으로 드러난 두 디테일을 추적 메모에 반영 제안:
  (1) "전층(1–24) 조건 탭 + Raw 전용 $`\tanh(g)`$ 게이트" 가 동결-백본 성능의
  핵심이라는 점(D20 후보 강화), (2) VLA-Adapter-Pro 가 **FiLM 을 제거**했다는
  점(D4 경계 신호).
- **D23 재검토 트리거 후보** — "L1 > DiT (이 논문 셋업)" 는 우리 flow-matching
  기본값(D23 v1-iii)을 *반증하지 않지만*, 손재주 다봉 과제에서의 L1 한계를 우리가
  직접 측정하기 전까진 "단봉 벤치마크 결과" 로만 취급하자는 메모.
- context/ 파일은 수정하지 않았습니다. 위는 사람 검토용 제안입니다.

---

> 💡 base 매핑은 `/implement-design analysis/2509.09372/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
