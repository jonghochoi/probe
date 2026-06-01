# Paper Analysis — VLA-Adapter: An Effective Paradigm for Tiny-Scale Vision-Language-Action Model

> PROBE analysis 모드 산출물. 단일 한글 문서이며, 영문 1차 파일은
> 없습니다. 형식·이모지·용어 규칙은 `docs/STYLE.md` §5 / §4 를
> 정확히 따릅니다. 재실행 시 이 파일을 덮어씁니다.

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | VLA-Adapter: An Effective Paradigm for Tiny-Scale Vision-Language-Action Model |
| 저자 | Yihao Wang, Pengxiang Ding, Lingxiao Li, Can Cui, Zirui Ge, Xinyang Tong, Wenxuan Song, Han Zhao, Wei Zhao, Pengxu Hou, Siteng Huang, Yifan Tang, Wenhui Wang, Ru Zhang, Jianyi Liu, Donglin Wang (BUPT · Westlake University · Zhejiang University · OpenHelix Team · HKUST-Guangzhou) |
| 링크 | [arXiv:2509.09372](https://arxiv.org/abs/2509.09372) |
| 발행일 / 버전 | 2025-09-11 · v2 (2025-09-22 개정) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-05-28 |

---

## 🧭 한 줄 요약 (TL;DR)

대규모 VLM 사전학습 없이도, VLM의 **모든 레이어**에서 뽑은 Raw 특징과 학습형 ActionQuery 특징을 **Bridge Attention** 으로 액션 공간에 주입하면 0.5B급 초소형 백본만으로 SOTA급 성능과 최고 추론 속도가 나온다 — 저자들이 이를 실증했습니다. 핵심은 "어떤 조건(레이어·타입)이 VL→A 브리징에 본질적인가"를 체계적으로 규명한 뒤, 그 발견을 경량 Policy 설계로 옮긴 것입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — VLA 모델이 인지(vision-language) 공간을 액션 공간으로 잇는 "브리징" 방식 자체를 체계적으로 분석하고, 대형 VLM과 대규모 로봇 데이터 사전학습 의존을 줄이는 것입니다.
- **기존 접근의 한계** — 현 VLA는 대형 VLM + OXE/DROID 규모의 사전학습을 요구해 학습 비용·VRAM·추론 지연(throughput)이 모두 큰 병목입니다.
- **본 논문의 가설** — VLM의 어떤 레이어·어떤 타입의 특징을 조건으로 쓰느냐가 성능을 좌우하며, "최적 조건을 자율적으로 주입"하면 백본을 키우지 않고도 성능을 낼 수 있다는 가설입니다.
- **왜 지금 중요한가** — 단일 소비자급 GPU에서 8시간 학습으로 강력한 VLA를 만들 수 있다면 VLA 배포 장벽이 크게 낮아지며, 백본 동결(frozen) 시에도 동작한다는 점은 VLM 사전학습 보존 논의(P4)와 직접 맞닿습니다.

---

## 🧩 핵심 기여

- VLA 분야에서 **브리징 패러다임이 액션 생성에 미치는 영향을 처음으로 체계 분석**하고, VLA 설계에 대한 몇 가지 핵심 발견(중간층 Raw / 심층 ActionQuery / 전 레이어 우월)을 제시했습니다.
- VLM의 Raw 잠재와 ActionQuery 잠재를 **Bridge Attention** 으로 통합해 VL→A 모달리티 갭을 효과적으로 잇는 경량 Policy 네트워크를 제안했습니다 (Policy 단독 97.3M, 전체 학습 파라미터 197.2M).
- **0.5B 백본 + 로봇 데이터 사전학습 없음** 조건에서 LIBERO·CALVIN·실세계 과제 전반에 걸쳐 SOTA급 성공률을, 작은 규모와 낮은 튜닝 비용으로, 그것도 219.2Hz라는 최고 추론 속도로 냈습니다.

---

## 🔑 기술 키워드

- **VLA-Adapter** — 대형 백본 대신 "조건 주입 어댑터"로 성능을 내는 브리징 패러다임. VLM은 그대로 두고 액션 쪽 Policy만 정교하게 설계한 접근입니다.
- **Raw latent ($`\mathcal{C}_{t}^{\mathcal{R}}`$)** — VLM이 직접 내보내는 비전·언어 표현. 저자들에 따르면 이 중 중간층이 액션에 더 유용합니다.
- **ActionQuery latent ($`\mathcal{C}_{t}^{\mathcal{AQ}}`$)** — VLM 시퀀스에 삽입된 학습형 쿼리 토큰의 출력. 멀티모달 정보를 능동적으로 빨아들이는 "빈 잔" 역할이며, 심층일수록 더 풍부해집니다.
- **Bridge Attention** — Raw 조건과 ActionQuery 조건을 각각 cross-attention 으로, 액션 잠재 자신을 self-attention 으로 묶는 3-어텐션 모듈. VL→A 매핑의 핵심 다리입니다.
- **Ratio $`g`$ (injection degree)** — Raw 특징 주입량을 조절하는 학습형 스칼라. 0으로 초기화하고 $`\tanh(g)`$ 로 범위를 [-1,1] 로 묶어 학습 안정성을 확보합니다(FiLM/게이팅 계열의 변주).
- **Prismatic-VLMs** — DINOv2 + SigLIP 비전 인코더에 LLM을 얹은 VLM 설계 공간. 본 논문 백본의 기반 아키텍처입니다.
- **L1-based Policy** — 플로우 매칭/디퓨전 대신 L1 회귀 손실로 액션 청크를 직접 예측하는 경량 정책 헤드. 본 논문이 채택한 기본형입니다.
- **액션 청크 (action chunk, $`H`$)** — 한 번에 예측하는 $`H`$-스텝 액션 묶음. 본 논문은 $`H=8`$ 을 사용합니다.
- **백본 동결 (frozen backbone)** — VLM 가중치를 고정한 채 ActionQuery 와 Policy 만 학습. VLM 사전학습 보존(P4) 관점에서 핵심 실험입니다.

---

## 🔬 방법론

### 직관

핵심 통찰은 "VLA의 성능 병목은 백본 크기가 아니라 **VL 정보를 액션으로 옮기는 다리의 설계**" 라는 것입니다. 저자들은 먼저 두 개의 질문 — (1.1) VLM의 어느 레이어 특징이 Policy에 유효한가, (1.2) ActionQuery 특징이 Raw 특징보다 나은가 — 을 LIBERO-Long에서 실측해 세 가지 발견을 도출합니다.

> "Regarding $`\mathcal{C}_{t}^{\mathcal{R}}`$ , the middle-layer latent performs better than the deep-layer latent." (§3.2)
(Raw 특징은 심층으로 갈수록 의미(semantic) 편향이 강해져 액션 생성에는 오히려 불리하고, 중간층이 이미지·텍스트를 고루 통합해 더 유용합니다.)

> "Regarding $`\mathcal{C}_{t}^{\mathcal{AQ}}`$ , deep-layer latent performs better than other-layer latent." (§3.2)
(ActionQuery는 from-scratch로 학습되므로, 심층에서 멀티모달 정보를 더 많이 누적해 액션 생성에 유리합니다 — Raw와 정반대 경향.)

> "Multi-layer features perform better. We observed that using all-layer features generally outperforms a single layer." (§3.2)
(레이어 선택이라는 설계 부담을 없애고도 단일 레이어보다 전 레이어를 쓰는 편이 보편적으로 낫습니다 — 이것이 Bridge Attention이 "전 레이어 × 두 타입"을 모두 주입하는 근거입니다.)

전 레이어 ActionQuery가 평균적으로 우월하지만, 중간층 Raw가 일부 어려운 서브태스크에서 더 잘합니다(Table 1). 이 때문에 둘을 함께 쓰면서 Raw의 주입량만 학습으로 조절하는 설계로 이어집니다.

### 아키텍처

![Figure 3 — VLA-Adapter framework](https://arxiv.org/html/2509.09372/x3.png)

> "Figure 3: The proposed VLA framework. The key components are the effective condition exploration and Attention design. “Attention” specifically includes cross attention with conditions and self attention with itself. In the “Unified VLA-Adapter Framework”, “Attention” is the Bridge Attention as shown in Section 3.3. Four conditions about “layer” and “type” are given on the right." (§3.1)
(VLM이 만들어내는 두 종류·여러 레이어의 조건을 Policy의 각 레이어에 주입하는 전체 골격을 보여줍니다 — "어떤 조건을 쓸지" 와 "어떻게 주입할지" 가 설계의 두 축입니다.)

**백본·입력.** VLM은 Prismatic-VLMs 구조(DINOv2 + SigLIP 비전, Qwen2.5-0.5B 언어)이며 $`M`$ 개 레이어를 가집니다. 타임스텝 $`t`$ 에서 입력은 다음과 같습니다.

> "the input into VLM consists of $`\{\mathcal{X}_{t}^{v},\mathcal{X}_{t}^{g},\mathcal{L}_{t},\mathcal{AQ}_{t}\}`$ : the 3rd-view image $`\mathcal{X}_{t}^{v}`$ , the gripper image $`\mathcal{X}_{t}^{g}`$ , the instruction $`\mathcal{L}_{t}`$ , and additional ActionQuery $`\mathcal{AQ}_{t}`$ ." (§3.1)
(3인칭 시점 이미지·그리퍼 이미지·언어 지시·학습형 ActionQuery 가 VLM에 함께 들어가고, 출력으로 지정 레이어의 Raw 잠재 $`\mathcal{C}_{t}^{\mathcal{R}}`$ 와 ActionQuery 잠재 $`\mathcal{C}_{t}^{\mathcal{AQ}}`$ 가 Policy의 조건으로 나옵니다.)

**백본 규모.** 백본을 키워도 이득이 제한적임을 보이려고 Prismatic-VLM(Qwen2.5-0.5B), Prismatic-VLM(LLaMA2-7B), 로봇 데이터로 사전학습된 OpenVLA-7B 세 가지로 실험했고, 효율을 노려 기본 백본은 Qwen2.5-0.5B 로 고정했습니다.

**Policy 구조.** 설계를 단순하게 가져가려고 L1 기반 Policy를 쓰며, Policy 레이어 수를 VLM과 동일하게($`M=24`$) 둡니다. 각 레이어는 Bridge Attention + FFN 으로 구성됩니다. 입력은 다음과 같습니다.

> "At $`t`$ -th timestep, the input to Policy includes: $`\{\mathcal{C}_{t}^{\mathcal{R}},\mathcal{C}_{t}^{\mathcal{AQ}},{\bf A}^{\tau=0}_{t},\mathcal{P}_{t}\}`$ ." (§3.3)
(각 레이어의 두 조건, 전부 0으로 초기화된 $`H`$-스텝 초기 액션 $`{\bf A}^{0}_{t}`$, 그리고 고유감각 상태 $`\mathcal{P}_{t}`$ 가 입력입니다. 초기 액션은 LN+MLP로, proprio는 2-layer MLP로 임베딩 $`\sigma_{0}(\mathcal{P}_{t})`$ 가 됩니다.)

![Figure 5 — Policy with Bridge Attention](https://arxiv.org/html/2509.09372/x5.png)

> "Figure 5: The Policy with Bridge Attention. The Policy parameters are only 97M when the backbone is Qwen2.5-0.5B. Each-layer $`\mathcal{C}_{t}^{\mathcal{R}}`$ and $`\mathcal{C}_{t}^{\mathcal{AQ}}`$ are integrated in Bridge Attention with the corresponding-layer action latent. Bridge Attention maps VL to Action to the greatest extent. The degree of $`\mathcal{C}_{t}^{\mathcal{R}}`$ injection is learnable, ensuring the performance and stability of training." (§3.3)
(각 레이어의 Raw·ActionQuery 조건이 대응 레이어 액션 잠재와 Bridge Attention 안에서 결합되며, Raw 주입 정도를 학습형으로 둬 학습이 흔들리지 않게 하면서 성능을 끌어올립니다.)

**Bridge Attention.** 한 모듈은 두 개의 cross-attention 과 한 개의 self-attention 으로 구성됩니다.

- 첫 cross-attention: Raw $`\mathcal{C}_{t}^{\mathcal{R}}`$ 를 MLP $`\sigma_{1}`$ 로 $`K_{1},V_{1}`$ 로 만들고, 액션 잠재 $`\widetilde{\bf{A}}^{\tau}_{t}`$ 를 $`Q_{1}`$ 으로 써서 $`\text{CA}_{1}`$ 을 얻습니다.
- 둘째 cross-attention: ActionQuery $`\mathcal{C}_{t}^{\mathcal{AQ}}`$ 를 proprio $`\sigma_{0}(\mathcal{P}_{t})`$ 와 concat 한 뒤 MLP $`\sigma_{2}`$ 로 $`K_{2},V_{2}`$ 로 만들고, $`\widetilde{\bf{A}}^{\tau}_{t}`$ 를 $`Q_{2}`$ 로 써서 $`\text{CA}_{2}`$ 를 얻습니다.
- self-attention: $`\widetilde{\bf{A}}^{\tau}_{t}`$ 를 $`Q,K,V`$ 로 써서 $`\text{SA}`$ 를 얻습니다.

Raw 주입량은 학습형 Ratio $`g`$ 로 조절합니다.

> "$`g`$ is initialized to 0 value, and the $`\tanh`$ activation function is utilized $`\tanh(g)\in[-1,1]`$ to prevent extreme values from destabilizing the distribution." (§3.3)
($`g`$ 를 0으로 초기화하고 $`\tanh`$ 로 [-1,1] 에 가둬 극단값이 분포를 흔들지 못하게 합니다 — 학습 초기에는 Raw 영향을 0에서 출발시켜 안정성을 확보하는 게이팅입니다.)

세 어텐션을 concat 해 $`\widehat{\bf{A}}_{t}^{\tau}`$ 를 만듭니다.

$$\widehat{\bf{A}}_{t}^{\tau}=[\text{CA}_{1}\left(\widetilde{\bf{A}}^{\tau}_{t},\sigma_{1}(\mathcal{C}_{t}^{\mathcal{R}})\right)\cdot\tanh(g),\text{CA}_{2}(\widetilde{\bf{A}}^{\tau}_{t},\sigma_{2}[\mathcal{C}_{t}^{\mathcal{AQ}},\sigma_{0}({\mathcal{P}_{t}})]),\text{SA}\left(\widetilde{\bf{A}}^{\tau}_{t},\widetilde{\bf{A}}^{\tau}_{t}\right)].$$

이후 residual FFN을 거쳐 $`\widetilde{\bf A}^{\tau+1}_{t}`$ 가 되고, 이 과정을 반복해 $`\widetilde{\bf A}^{M-1}_{t}`$ 를 얻은 뒤 LN+MLP로 최종 액션 청크 $`{\bf A}^{M-1}_{t}`$ 를 산출합니다. (DiT 기반 Policy 변형도 설계했으나 L1 기반이 성능에서도 속도에서도 대체로 앞서 L1을 기본으로 채택했습니다 — Appendix B.)

### 학습 목표 / 손실

학습은 end-to-end이며 Policy는 from-scratch로 학습합니다. 목적함수는 L1 회귀입니다.

$$\min_{\theta}\mathcal{J}(\theta)=\mathbb{E}_{\mathbf{A}_{t},\mathcal{C}_{t}^{\mathcal{R}},\mathcal{C}_{t}^{\mathcal{AQ}},{\sigma_{0}}({\mathcal{P}_{t}}),\tau}\Big[\big\|\pi_{\theta}(\mathbf{A}_{t}^{\tau},\mathcal{C}_{t}^{\mathcal{R}},\mathcal{C}_{t}^{\mathcal{AQ}},{\sigma_{0}}({\mathcal{P}_{t}}),\tau)-\mathbf{A}_{t}\big\|_{1}\Big].$$

(예측 액션과 ground-truth 궤적 $`{\bf A}_{t}`$ 의 L1 거리만 최소화합니다 — 디퓨전 노이즈 스케줄이나 플로우 매칭 없이 회귀로 끝내는 단순한 목표입니다.)

### 학습 셋업

- **옵티마이저·스케줄**: AdamW + LoRA 스킴, learning rate `1e-4`, cosine-annealing + warmup, batch size 16, max training step 150,000, warmup step 10% (Table F1).
- **하드웨어**: 4× NVIDIA H100 (메인 실험). 제안 패러다임 덕에 단일 소비자급 GPU에서 8시간 학습이 가능하다고 주장합니다.
- **하이퍼파라미터 (Table F2)**: 백본 Qwen2.5-0.5B, 레이어 $`\tau/M=24`$, ActionQuery 64개, hidden size 896, attention head 8, action chunk $`H=8`$, VLM 중간 레이어 1–24 전부 사용, Policy 학습 파라미터 97.3M, VLA-Adapter 전체 학습 파라미터 197.2M.

---

## 📊 실험 설정과 결과

평가 벤치마크는 LIBERO(Spatial/Object/Goal/Long, 서브태스크당 50회), CALVIN ABC→D(제로샷 일반화, Avg. len 0–5), 그리고 6-DOF Synria Alicia-D + 1-DOF 그리퍼 실세계 과제입니다.

| 항목 | VLA-Adapter (0.5B) | 비교 대상 | 비고 |
|---|---|---|---|
| LIBERO 평균 | 97.3 | OpenVLA-OFT(7B) 97.1 / π0(3B) 94.2 / GR00T N1(2B) 93.9 | Table 5 |
| LIBERO-Long | 95.0 | OpenVLA-OFT 94.5 / VLA-OS(0.5B) 66.0 | Table 5 |
| CALVIN Avg. len | 4.42 | OpenVLA-OFT 4.10 / VPP 4.33 | Table 6 |
| 처리량 (Throughput) | 219.2 Hz | OpenVLA-OFT 71.4 / OpenVLA 4.2 | Table 4 |
| 지연 (Latency) | 0.0365 s | OpenVLA-OFT 0.1120 / OpenVLA 0.2396 | Table 4 |
| 동결 백본 성공률 | 86.4 | SmolVLA 77.0 / OpenVLA-OFT 0.0 | Table 3 (LIBERO-Long) |
| VLA-Adapter-Pro 평균 | 98.5 (LIBERO) / 4.50 (CALVIN) | — | Table 5/6 |

> "VLA-Adapter, using only a tiny-scale backbone, can achieve performance comparable to OpenVLA-OFT with 14 $`\times`$ larger." (§4.2, Table 5)
(0.5B 백본으로 14배 큰 7B 모델(OpenVLA-OFT)에 필적하는 LIBERO 성능을 냈고, 동급 0.5B VLA-OS 대비 LIBERO-Long에서 29.0% 우위를 보였습니다.)

> "Even if the backbone freezes, VLA-Adapter still performs strongly." (§4.1, Table 3)
(백본을 동결하면 OpenVLA-OFT는 0.0으로 붕괴하지만 VLA-Adapter는 86.4를 유지합니다 — ActionQuery와 Policy만 from-scratch로 학습하기 때문입니다.)

이 차이의 원인은 Appendix H에서 코드 수준으로 확인됩니다. OpenVLA-OFT의 학습형 토큰은 "마스크" 형태로 0으로 초기화되어 백본 동결 시 학습되지 않는 반면, VLA-Adapter의 ActionQuery는 VLM 시퀀스의 지정 위치에 삽입되어 attention에 참여하는 진짜 학습형 토큰이므로 백본이 얼어도 from-scratch로 학습됩니다.

설계 근거는 조건 타입 절제(Table 7)에서 직접 드러납니다.

> "using both all-layer Raw and ActionQuery achieves superior performance" (§4.5, Table 7)
(Last-layer Raw=85.8, Last ActionQuery=90.2, 중간층 Raw=88.4, 전 레이어 Raw=90.6, 전 레이어 ActionQuery=92.6, 전 레이어 Raw+ActionQuery=95.0 — 두 타입을 모두 전 레이어로 쓸 때 최고입니다.)

게이팅 설계는 주입 정도 절제(Table 8)에서 확인됩니다. Raw=$`\tanh(g)`$ + ActionQuery=1 조합이 95.0 으로, Raw=1·ActionQuery=1(91.4), Raw=1·ActionQuery=$`\tanh(g)`$(91.0), 둘 다 $`\tanh(g)`$(92.6) 보다 우수합니다. ActionQuery는 그대로 완전 주입하고 Raw만 학습형으로 선별 주입하는 것이 최선임을 보입니다. ActionQuery 토큰 수는 64개에서 성능과 효율이 모두 가장 좋습니다(Figure 8).

---

## ⚖️ 한계

- **저자 명시 한계** — (1) 대규모 임베디드 데이터 사전학습이 없고 규모가 작아 실세계 시스템에서의 일반화가 더 개선되어야 합니다. (2) Policy가 만드는 액션 품질은 VLM이 제공하는 조건과 그 사용 방식에 의존합니다. (3) 학습 과정이 비교적 단순(L1 회귀)하며, 강화학습 등 복잡한 과정은 향후 과제로 남깁니다.
- **하드웨어 협소** — 실세계 검증이 6-DOF 팔 + 1-DOF 그리퍼에 한정됩니다. 다지 손(dexterous hand)·촉각·접촉 집약적 과제는 전혀 다루지 않습니다.
- **L1 회귀의 모드 평균화** — 멀티모달 액션 분포에서 L1/회귀 헤드는 모드 평균으로 정밀도가 떨어질 수 있는데, 본 논문은 이 점을 정량 분석하지 않았습니다(DiT 변형과의 비교는 Appendix B에 간략히만 있음).
- **벤치마크 편중** — 핵심 발견(레이어·조건 분석)이 대부분 LIBERO-Long 단일 벤치마크에서 도출되어 일반성 주장에 다소 의존이 큽니다.

---

## ♻️ 재현성

- **코드/프로젝트**: 프로젝트 페이지 https://vla-adapter.github.io/ 공개. 백본은 Prismatic-VLMs(공개) + Qwen2.5-0.5B(공개), 비교 기준 OpenVLA-OFT 코드(GitHub `moojink/openvla-oft`)를 인용·재실행했습니다.
- **데이터**: LIBERO, CALVIN ABC→D 모두 공개 벤치마크. 실세계 데이터는 자체 수집(Synria Alicia-D).
- **하드웨어/하이퍼파라미터**: 4× H100 명시, Table F1/F2 에 학습 스텝·lr·batch·레이어·토큰 수까지 구체적으로 공개되어 재현 가능성이 높습니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

이 논문은 `context/MASTER.md` 에 **이미 추적 중인 논문**입니다 — P4 §8.4의 "VLA-Adapter (Bridge Attention)", D19b의 "Prismatic-VLM + Qwen2.5-0.5B × LIBERO + CALVIN (adapter-only), minimal-backbone path", D20의 "action-side adapter (VLA-Adapter Bridge Attention)" 옵션이 모두 이 논문을 가리킵니다.

- **P4 (VLM 사전학습 보존)** — 여기에 정면으로 맞닿습니다. **D19**(VLM FT 범위) v1 = (a) 완전 동결 + 액션 전문가만 학습, **D20**(prior-preservation) v1 = action-side adapter, **D23**(액션 표현) v1 = (iii) flow-matching. VLA-Adapter는 D19(a)+D20(action-side adapter)의 **구체적 성공 사례**이자, D23에서 PROBE가 택한 flow-matching의 **L1-회귀 대안**입니다.
- **P1 (이종 Body/Hand 액션 전문가)** — Bridge Attention의 "Raw cross-attn × 학습형 $`\tanh(g)`$ 게이트" 는 **D4**(Body↔Hand 정보 공유, v1=FiLM, cross-attn 지연 후보)와 **D7**(π 백본 통합/분할)의 방법론 참조가 됩니다. 단, 해부학적 split이 아니라 단일 액션 전문가 설계라는 점에서 P1의 핵심 주장과는 결이 다릅니다.
- **Identity 긴장/지지** — Identity는 "보정 모듈은 VLA 출력 주변 local distribution 에 한정되어 ceiling을 못 넘는다"고 주장합니다(Antagonist A). VLA-Adapter는 frozen VLA 위의 어댑터이지만, 후처리 보정이 아니라 **전 레이어 특징을 액션 공간으로 직접 브리징**하는 설계라 단순 correction/residual 과는 구분됩니다 — 다만 백본을 동결한 채 어댑터만 키운다는 점에서 P4의 "동결 백본으로 충분한가" 질문에 곧바로 데이터가 됩니다.
- **§10 경쟁자 함의** — OpenHelix(Cui et al.) 등 본 논문 저자진의 dual-system VLA 계열과 연결되며, P4 competitor(§8.4 demote 후 P4.md §8 추적)로서 위치가 유지됩니다.

---

## ✨ 핀 논문 대비 델타

- **π0 ([arXiv:2410.24164](https://arxiv.org/abs/2410.24164)) 대비** — π0도 전 레이어 Raw 특징을 쓰지만 액션 헤드가 flow-matching이고 대형 백본(3B)을 전제합니다. VLA-Adapter는 동일한 "전 레이어 특징" 아이디어에 **학습형 ActionQuery 타입을 추가**하고, 두 타입을 Bridge Attention으로 결합하며 0.5B 백본 + 사전학습 없음으로 내려간 점이 새롭습니다.
- **OpenVLA-OFT([arXiv:2502.19645](https://arxiv.org/abs/2502.19645)) 대비** — OFT는 last-layer 학습형 쿼리를 쓰는데, VLA-Adapter는 (1) 전 레이어 + (2) Raw·ActionQuery 두 타입 동시 + (3) Raw 주입의 학습형 게이팅으로 차별화하며, 특히 **백본 동결 시 OFT는 0.0으로 붕괴하지만 VLA-Adapter는 86.4** 라는 점이 핵심 델타입니다(Appendix H의 코드 수준 원인 규명 포함).
- **기존 P4 핀과의 관계** — VLM2VLA([arXiv:2509.22195](https://arxiv.org/abs/2509.22195))는 LoRA + NL-action으로 망각을 완화하는 경로(D20→D23(ii))인 반면, VLA-Adapter는 **백본을 건드리지 않고(또는 완전 동결) 액션 쪽 어댑터만으로** prior를 보존하는 경로로, D20 v1(action-side adapter)에 그대로 대응하는 실증입니다.

---

## ⚙️ 의사결정 함의

이 논문이 맞다면 PROBE의 학습 파이프라인에서 다음이 바뀝니다.

- **D19(a) 완전 동결의 전제 수정** — "백본 동결 + 액션 전문가만 학습" 이 동작하려면 **last-layer 특징만으로는 부족**하고(OFT frozen=0.0), VLM의 **중간/전 레이어 특징을 액션 전문가에 주입**해야 합니다. PROBE의 π0 슬라이스(D7)에서 액션 전문가가 백본의 마지막 hidden state만 받는 구조라면, **레이어별 cross-attention 주입**을 설계 옵션으로 올립니다.
- **구체적 config 키** — (1) 액션 전문가의 cross-attention key/value 소스를 `last_hidden_state` → `all_hidden_states[1:M]` 로 확장, (2) Raw 특징 주입에 학습형 스칼라 `ratio_g`(init 0, `tanh` 클램프) 추가, (3) D5(입력 모달리티)에서 proprio 임베딩을 ActionQuery 측 cross-attn의 KV에 concat. 
- **D4(Body↔Hand) 방법론 보강** — v1 FiLM $`(\gamma,\beta)`$ 대신/병행해, $`a_b`$ 를 Hand 헤드 cross-attn의 조건으로 주입하고 그 주입량을 $`\tanh(g)`$ 로 게이팅하는 변형이 "단일 지점 정보 병목" 우려(D4 deferred trigger)에 대한 경량 대안이 됩니다.
- **D23 비교군 확보** — flow-matching(v1) vs L1-회귀(VLA-Adapter)의 정밀도/속도 트레이드오프가 in-hand rotation 같은 접촉 집약 과제에서 어떻게 갈리는지를 4-contribution 절제(D25)의 보조 축으로 추가할 수 있습니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **그리퍼→다지 손 전이 미검증** — 모든 결과가 1-DOF 그리퍼 + LIBERO/CALVIN 입니다. 22-DOF Sharpa Hand의 finger joint command(D3)·촉각(P2) 같은 고차원·접촉 집약 출력에서 ActionQuery 64개 + 97M Policy 용량이 충분한지는 아직 검증되지 않았습니다. **가장 싼 체크**: PROBE의 π0 스택에서 액션 청크 차원만 그리퍼→다지 손으로 키워 LIBERO류 sim에서 학습 수렴/성공률이 유지되는지 먼저 확인.
- **L1 회귀의 모드 평균화** — in-hand rotation처럼 멀티모달·다봉 액션 분포에서 L1 헤드는 모드를 평균으로 뭉갭니다. 접촉 정밀도(slip count, pose stability — D25 falsifier)가 떨어질 위험이 있습니다. **체크**: 동일 데이터로 flow-matching 헤드 vs L1 헤드의 접촉 정밀도 지표를 직접 비교.
- **"전 레이어 주입"의 단일-벤치마크 의존** — 레이어·조건 발견이 LIBERO-Long 중심이라, PROBE의 접촉 과제로 그대로 전이될지는 아직 검증되지 않았습니다. **체크**: 우리 데이터에서 last-layer vs all-layer 주입의 성공률 델타를 작은 절제로 먼저 측정한 뒤 Bridge Attention 채택 여부 결정.
- **동결 백본 + from-scratch Policy의 데이터 요구량** — frozen이 동작하는 건 197M Policy를 충분한 벤치마크 데이터로 from-scratch 학습했기 때문입니다. PROBE의 초기 소량 실데이터 상황에서 동일 효과가 날지 의문이며, **VLM 사전학습 prior를 버리는 셈**이 될 위험이 있습니다(P4 정체성과 충돌 가능).

---

## 💡 컨텍스트 제안

- **핀 승격 후보** — VLA-Adapter는 현재 P4 핀에서 demote 되어 `context/P4.md` §8 competitor로만 추적됩니다(§8.4 주석). 그러나 "동결 백본 + action-side adapter(D20 v1)" 를 곧장 실증하고 frozen=86.4 vs OFT frozen=0.0 이라는 D19/D20 핵심 증거를 내놓으므로, 다음 분기 rebalance 시 **P4 핀 재승격 또는 D20 근거 문헌으로의 고정**을 안건으로 올립니다.
- **D19/D20 근거 업데이트 제안** — D19(a) 완전 동결 rationale("late fusion → 백본은 π-trained 모달리티만 봄")에 "단, 액션 전문가는 last-layer가 아니라 중간/전 레이어 특징을 받아야 frozen이 동작한다(VLA-Adapter Appendix H)" 라는 단서 조항 추가를 제안합니다.
- 위 제안은 사람이 판단할 사항이며, `context/MASTER.md` 는 수정하지 않았습니다.

> 💡 base 매핑은 `/implement-design analysis/2509.09372/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
