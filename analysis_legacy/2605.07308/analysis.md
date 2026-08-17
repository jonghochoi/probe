# Paper Analysis — AT-VLA: Adaptive Tactile Injection for Enhanced Feedback Reaction in Vision-Language-Action Models

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | AT-VLA: Adaptive Tactile Injection for Enhanced Feedback Reaction in Vision-Language-Action Models |
| 저자 | Xiaoqi Li, Muhe Cai, Jiadong Xu, Juan Zhu, Hongwei Fan, Yan Shen, Guangrui Ren, Hao Dong |
| 링크 | [arXiv:2605.07308](https://arxiv.org/abs/2605.07308) |
| 발행일 / 버전 | 2026-05-08 · v2 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-05-26 |
| 관련 Pillar | P4, P3, P2 |
| 태그 | tactile, vla-arch |

---

## 🧭 한 줄 요약 (TL;DR)

사전학습된 VLA (vanilla 기준 GO-1) 위에 학습형 Tactile Gate 와 Adaptive Cross-Attention 을 끼워 넣어, 비접촉 구간에서는 원래 VLA 의 입력·구조를 한 글자도 건드리지 않고 접촉이 시작될 때만 촉각 토큰을 query 자리에 주입하는 Adaptive Tactile Injection 패턴을 제안합니다. 동시에 시각·언어 슬로우 스트림과 촉각 패스트 스트림을 3:1 비율로 분리해 0.04 초 폐루프를 만들었고, 학습 시 촉각을 본 모델이 추론 시 촉각이 없어도 vanilla 수준을 유지한다는 modality-agnostic 강건성도 함께 보고합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 사전학습된 VLA 에 접촉이 잦은 조작용 촉각 신호를 어떻게 끼워 넣어야, 시각 기반 grounding 같은 사전학습 능력을 망가뜨리지 않고도 접촉 구간에서 정밀한 반응을 얻을 수 있는가. 학습할 때 본 촉각 신호가 추론 시 사라져도 정책이 무너지지 않게 하려면 무엇이 더 필요한가.
- **기존 접근의 한계** — 사전학습 데이터셋에는 촉각이 거의 없어, 다운스트림 파인튜닝 단계에서 새 모달리티를 끼워 넣게 됩니다. 토큰 시퀀스를 그대로 늘리면 사전학습 시 보지 못한 분포가 들어오고, 그 결과 grasp localization 같은 시각 grounding 능력이 오히려 떨어집니다. 더해서 VLA 의 추론 지연이 커서 고주파 촉각 신호에 제때 반응하지 못합니다.
- **본 논문의 가설** — 시각과 촉각은 본디 서로를 보완합니다. 시각은 비접촉 구간에서 위치 잡기를 책임지고, 촉각은 접촉이 시작된 뒤에만 끼어들면 됩니다. 따라서 (1) 접촉 여부를 학습형 게이트로 판단하고, (2) 게이트가 켜진 순간에만 액션 전문가의 cross-attention query 를 촉각 토큰으로 바꿔치우며, (3) 슬로우-패스트 스트림으로 촉각을 고주파 처리하면 사전학습 표현을 보존하면서도 접촉 반응을 빠르게 끌어올릴 수 있다는 주장입니다.
- **왜 지금 중요한가** — VLA 가 generalist 로 굳어 가는 흐름에서 contact-rich 영역이 마지막 남은 빈 칸으로 떠올랐습니다. Tactile-VLA, TLA, VTLA, RDP 등 촉각 결합 시도가 연달아 나왔지만 대체로 사전학습 능력 침식 문제를 정면으로 다루지 않았고, 본 논문이 그 빈 자리를 채워 PROBE 의 P4 (VLM 사전학습 보존) 정면 증거와 맞물립니다.

---

## 🧩 핵심 기여

- **Adaptive Tactile Injection** — 학습형 Tactile Gate (BCE 로 학습된 MLP 이진 분류기) + Adaptive Cross-Attention 의 조합으로, 비접촉 구간에서는 vanilla VLA 와 동일한 입력·구조를 유지하고 접촉 구간에서만 액션 전문가의 cross-attention query 를 state 토큰에서 촉각 토큰으로 전환합니다.
- **Tactile Reaction Dual-Stream** — VLM 슬로우 스트림(저주파, 시각·언어)과 촉각 패스트 스트림(고주파, 촉각)을 분리해 폐루프 응답을 0.04 초 이내로 달성합니다. 패스트:슬로우 = 3:1 비율로 운용합니다.
- **Modality-agnostic 강건성** — 학습 시 촉각을 받았던 동일 가중치가 추론 시 촉각 없이 돌아가도 vanilla VLA 와 비슷한 성능을 유지합니다. contact-rich 인 Stamp 태스크에서는 오히려 약간 더 잘 합니다.
- **포맷별 비교** — force 6D > marker 2D > visual-tactile image 순으로 성능이 갈리는 ablation 을 함께 제시합니다. 저자들은 이 결과를 가지고, 사전학습 표현이 흔들리는 정도가 촉각 토큰 차원에 비례한다는 가설을 밀어붙입니다.
- **실세계 검증** — AgiBot Genie1 + GO-1 백본 위에서 4 개 contact-rich 태스크 (Unzip Bag · Stamp · Wipe Vase · Unscrew Lid) 와 2 개 비접촉 태스크 (Pick & Place · Open Drawer) 를 직접 평가합니다.

---

## 🔑 기술 키워드

- **Vision-Language-Action (VLA) Model** — 이미지·언어·proprioception 입력에서 액션 청크를 직접 산출하는 엔드-투-엔드 정책 군. 본 논문의 vanilla 는 AgiBot World 로 사전학습된 GO-1 입니다.
- **Tactile Gate** — 촉각 토큰에서 접촉/비접촉을 판별하는 학습형 이진 분류기. 사람 손이 신호등 보고 멈췄다 갈지 결정하듯, 모델이 촉각을 들여보낼지 끊을지를 결정합니다.
- **Adaptive Cross-Attention** — 동일 cross-attention 모듈이 게이트 상태에 따라 query 를 다르게 받는 구조. 게이트가 꺼져 있으면 state 토큰, 켜져 있으면 촉각 토큰이 query 가 됩니다.
- **Tactile Reaction Dual-Stream** — 슬로우 (VLM) · 패스트 (촉각) 처리 빈도를 분리한 이중 스트림. Gr00t-N1 의 dual-system 사상을 시각이 아니라 촉각으로 옮긴 변형으로 읽힙니다.
- **액션 전문가 (Action Expert)** — π0 계열에서 도입된 flow-matching 기반 액션 디코더 모듈. 본 논문에서는 GO-1 의 DiT 액션 전문가를 그대로 물려받고 cross-attention 안쪽만 손봅니다.
- **Flow Matching** — 노이즈 액션에서 원본 액션으로 가는 벡터 필드를 회귀하는 조건부 액션 분포 학습 목적식. π0 라인의 표준 채택으로, 본 논문도 GO-1 으로 상속합니다.
- **Resultant Force (3D normal + 3D tangential)** — 본 논문이 가장 선호하는 촉각 포맷. 접촉 표면의 법선·전단 성분을 6D 벡터 하나로 요약해 토큰 수와 차원을 동시에 줄입니다.
- **Visual-Tactile (V-T) Image / Marker 2D / Force 6D** — 비교된 세 가지 촉각 포맷. V-T 이미지는 Sparsh 인코더, marker 2D 는 추적 마커 변위, force 6D 는 합력 벡터입니다.

---

## 🔬 방법론

### 직관

> "Drawing inspiration from the complementary characteristics of visual and tactile modalities, where vision facilitates contextual localization and tactile provides precise contact feedback, we argue that the model should preserve its pretrained VLA structure in non-contact phases while introducing tactile feedback only upon contact to better utilize pretrained representations." (§1)
(이 한 문장이 논문 전체의 설계 의도를 잡아 줍니다. 비접촉에서는 사전학습된 표현을 그대로 두고, 접촉이 시작될 때만 촉각을 끼워 넣자는 분리 원칙이 Tactile Gate · Adaptive Cross-Attention · Dual-Stream 세 모듈을 한꺼번에 묶어 줍니다.)

> "Surprisingly, the latter not only fails to improve performance but even causes noticeable inaccuracies in grasp localization." (§3.2)
(촉각을 그냥 토큰으로 추가해 보면 오히려 성능이 떨어집니다. 액션 전문가의 attention map 이 대상 물체에서 주변부로 흩어지는 모습이 attention 시각화로 잡혔고, 이게 본 논문의 "직접 주입은 사전학습을 망가뜨린다" 라는 핵심 직관의 근거입니다.)

![Figure 3 — Attention shift induced by naive tactile injection](https://arxiv.org/html/2605.07308/x2.png)

> "Figure 3: Intuition. We visualize the attention maps in the Action Expert module to examine how the model's attention distribution and action reasoning vary across downstream finetuning strategies, contrasting settings with and without tactile feedback." (§3.2)
(왼쪽이 vanilla, 오른쪽이 촉각을 그냥 토큰으로 끼워 넣은 변종입니다. 후자에서 attention 이 잡아야 할 대상에서 빗겨 나가는 모습이 한눈에 보입니다. 저자들이 Adaptive Tactile Injection 을 왜 만들었는지 그림 한 장으로 보여주는 셈입니다.)

### 아키텍처

![Figure 2 — Framework of AT-VLA](https://arxiv.org/html/2605.07308/x1.png)

> "Figure 2: Framework of AT-VLA. The tactile gate adaptively determines whether tactile tokens should be used as conditional inputs for action generation within the Action Expert module. When the tactile gate is inactive, all input modalities of the Action Expert operate at the same frequency. When activated, the tactile signal is processed at a higher frequency to enable rapid and precise action adjustments." (§2)
(전체 아키텍처 도식입니다. 위쪽은 슬로우 스트림(VLM), 아래쪽은 패스트 스트림(촉각 인코더), 오른쪽은 액션 전문가입니다. Tactile Gate 가 패스트 스트림 결과를 받아 켜짐/꺼짐을 결정하면, Adaptive Cross-Attention 이 그 신호에 맞춰 query 자리를 바꿉니다.)

전체 정책은 다음과 같이 정의됩니다.

$$A=\pi_{\theta}(I,L,T,S).$$

여기서 $`I=\{I_{h},I_{r},I_{l}\}`$ 는 head/right wrist/left wrist 카메라 영상, $`L`$ 은 언어 명령, $`T`$ 는 촉각 (법선 3D + 전단 3D 합력), $`S`$ 는 robot proprioception, $`A`$ 는 양팔 14-DoF end-effector pose action chunk 입니다.

**Vanilla VLA 베이스.** GO-1 [arXiv:2503.06669](https://arxiv.org/abs/2503.06669) 을 그대로 물려받습니다. VLM 백본은 InternVL-2B, 액션 전문가는 DiT, 액션 손실 $`\mathcal{L}_{a}`$ 의 형태도 GO-1 그대로입니다.

**Tactile Encoder.** 합력 6D 입력을 받는 가벼운 MLP 스택이 촉각 토큰 $`\mathbf{z}_{T}`$ 를 만듭니다. 본 논문은 패스트 스트림 지연을 줄이기 위해 의도적으로 가볍게 잡았다고 명시합니다.

**Tactile Gate.** $`\mathbf{z}_{T}`$ 를 받아 contact/non-contact 이진 분류 score 를 출력하는 MLP. 학습 시에는 에피소드별로 사람이 0/1 라벨을 붙이고 BCE 손실 $`\mathcal{L}_{g}`$ 로 지도합니다. 추론 시 score 가 임계값 (예: 0.5) 을 넘으면 게이트가 켜집니다.

**Adaptive Cross-Attention.** vanilla GO-1 의 cross-attention 모듈에서는 image 토큰 $`\mathbf{z}_{I}`$ · text 토큰 $`\mathbf{z}_{L}`$ 이 key/value, state 토큰 $`\mathbf{z}_{S}`$ 가 query 입니다. 본 논문은 key/value 와 모듈 구조는 그대로 두고 query 자리만 게이트 상태에 따라 바꿉니다.

> "To maintain consistency with the vanilla VLA and preserve its pretrained representations, the state token is used as the query when the tactile gate is inactive, and is replaced by the tactile token $`z_{T}`$ when the gate is active." (§3.2)
(query 자리만 바꿔치우면 attention 출력 차원도 그대로고 사전학습된 key/value 표현도 손상되지 않습니다. 게이트 OFF 구간에서는 vanilla 와 한 비트도 다르지 않게 만드는 트릭입니다.)

**Tactile Reaction Dual-Stream.** 입력 처리 빈도를 두 갈래로 가릅니다. 슬로우 스트림은 VLM 으로 시각·언어를 저주파 처리해 액션 전문가의 cross-attention key/value 로 흘려 보내고, 패스트 스트림은 촉각만 고주파로 처리해 query 자리로 흘려 보냅니다. 따라서 액션 전문가의 입력은 비동기 빈도 + 이종 모달리티 라는 두 가지 특성을 동시에 갖습니다.

> "Building on previous action chunking strategies, the visual and language observation at time step $`t_{n}`$ can provide guidance for a future horizon of action steps ( $`t_{n}`$ : $`t_{n+H}`$ ). Consequently, slow stream's output serves as a latent condition that temporally guides action generation across the following $`H`$ time steps." (§3.3)
(슬로우 스트림의 출력 한 번이 future action horizon $`H`$ 스텝 동안 잠재 조건으로 살아남고, 그 사이 패스트 스트림은 가장 최근 촉각 입력에 기반해 매 스텝 액션을 갱신합니다. 결과적으로 한 번의 시각·언어 추론이 여러 번의 촉각 갱신을 견딥니다.)

### 학습 목표 / 손실

전체 손실은 단순 가중합입니다.

$$\mathcal{L}=\mathcal{L}_{a}+\lambda_{1}*\mathcal{L}_{g}$$

여기서 $`\mathcal{L}_{a}`$ 는 GO-1 의 액션 손실 (flow-matching 라인 그대로), $`\mathcal{L}_{g}`$ 는 Tactile Gate 의 BCE 손실입니다. $`\lambda_{1}=0.01`$ 로, 두 손실 스케일을 맞춥니다.

> "All objectives are trained simultaneously, under the overall supervision $`\mathcal{L}=\mathcal{L}_{a}+\lambda_{1}*\mathcal{L}_{g}`$ , $`\lambda_{1}`$ is set to 0.01 to balance different losses' scale." (§3.4)
(추가 손실이 단 하나뿐인 단출한 멀티태스크 학습입니다. 게이트를 별도 사전학습 단계 없이 액션과 함께 한 번에 학습시키므로 구현 부담이 크게 줄어듭니다.)

### 학습 셋업

- **하드웨어** — AgiBot Genie1 (양팔 7-DoF), 전면 카메라 1 대 + 양 손목 카메라 각 1 대. 촉각은 Xense Robotics 의 그리퍼-탑재 센서. 텔레오퍼레이션은 VR 헤드셋.
- **데이터** — 태스크별 30~50 개 시연을 직접 수집. 평가에는 태스크당 15 회 시도.
- **태스크** — contact-rich 4 종 (Unzip Bag · Stamp · Wipe Vase · Unscrew Lid) + non contact-rich 2 종 (Pick & Place · Open Drawer).
- **추론 빈도** — 게이트 OFF 시 슬로우·패스트 동일 빈도, 게이트 ON 시 패스트:슬로우 = 3:1 비율로 운용 (Gr00t-N1 [arXiv:2503.14734](https://arxiv.org/abs/2503.14734) · Fast-in-Slow [arXiv:2506.01953](https://arxiv.org/abs/2506.01953) 와 동일 사상). 폐루프 응답 시간은 0.04 초 이내라고 보고합니다.
- **베이스라인** — GO-1 (vanilla) · π0.5 [arXiv:2504.16054](https://arxiv.org/abs/2504.16054) · VTLA · RDP. 단 VTLA 는 공식 코드가 없어 DexVLA 코드베이스 위에서 자체 재현했고, RDP 는 Diffusion Policy 위에 PCA-감축된 marker 입력만 받습니다. VTLA · RDP 는 사전학습이 없어 contact-rich 구간만 떼어 평가했다고 명시합니다.

---

## 📊 실험 설정과 결과

**Contact-rich 4 태스크 성공률 (Table 1).** 모든 수치는 sub-task progression 기반.

| Method | Unzip Bag Overall | Stamp Overall | Wipe Vase Overall | Unscrew Lid Overall |
|---|---|---|---|---|
| GO-1 | 0.20 | 0.13 | 0.07 | 0.27 |
| $`\pi_{0.5}`$ | 0.0 | 0.20 | 0.33 | 0.46 |
| **AT-VLA (Ours)** | **0.33** | **0.46** | **0.67** | **0.53** |
| VTLA (contact-only) | 0.00 | 0.13 | 0.60 | 0.80 |
| RDP (contact-only) | 0.06 | 0.40 | 0.33 | 0.87 |

> "Compared with state-of-the-art VLA models GO-1 and $`\pi_{0.5}`$ , which are trained without tactile feedback, our model demonstrates comparable performance during the pre-contact manipulation phase, indicating that it effectively preserves the pretrained knowledge in aspects such as visual grounding and semantic reasoning required for reliable object grasping. During the contact-rich stage, AT-VLA achieves an improvement over them, clearly demonstrating the necessity of tactile signals for complex manipulation tasks." (§4.2)
(사전학습 보존 + 접촉 반응 향상이라는 두 마리 토끼를 동시에 잡았다는 결론 문장. 단 Unscrew Lid 는 VTLA · RDP 보다 낮은데, 본 논문은 그 이유를 "we manually set the robot in an ideal grasping pose before rotating the lid" 라고 비교 셋업의 차이로 돌립니다.)

**Modality-agnostic 강건성 (Table 2).** 동일 가중치, 추론 시 촉각 공급 여부만 다르게.

| Method | Pick Place | Open Drawer | Stamp | AVG. |
|---|---|---|---|---|
| GO-1 | 1.0 | 0.93 | 0.13 | 0.68 |
| $`\pi_{0.5}`$ | 1.0 | 0.93 | 0.20 | 0.70 |
| AT-VLA w/o. tactile | 1.0 | 0.93 | 0.20 | 0.70 |
| AT-VLA w/. tactile | 1.0 | 0.93 | 0.46 | **0.79** |

> "Interestingly, AT-VLA (w/o tactile) even shows a slight performance improvement over its vanilla model GO-1." (§4.3)
(추론 시 촉각이 없어도 학습 시 본 촉각 덕에 vanilla 보다 약간 더 잘 합니다. 가중치 단계에서 cross-modal 상관이 이미 내재화되었다는 저자들의 해석입니다. PROBE 입장에서 보면 D19·D20 "사전학습 보존" 전략의 사후 검증으로 읽을 만한 결과입니다.)

**Ablation (Table 3).** 네 contact-rich 태스크 평균.

| Variant | Tactile Gate | Adaptive Cross-Attn | Direct Incorp. | Reaction Dual-Stream | Format | AVG. |
|---|---|---|---|---|---|---|
| Ex0 (Vanilla GO-1) | - | - | - | - | - | 0.22 |
| Ex1 (Direct tactile, 6D) | - | - | ✓ | ✓ | F6D | 0.13 |
| Ex2 (Gate + Adaptive, V-T) | ✓ | ✓ | - | ✓ | V-T | 0.39 |
| **Ex3 (Ours, F6D)** | ✓ | ✓ | - | ✓ | F6D | **0.50** |
| Ex4 (Direct, Marker 2D) | - | - | ✓ | - | M2D | 0.05 |
| Ex5 (Ours w/o Dual-Stream, M2D) | ✓ | ✓ | - | - | M2D | 0.32 |
| Ex6 (Direct, V-T) | - | - | ✓ | - | V-T | 0.02 |
| Ex7 (Ours w/o Dual-Stream, V-T) | ✓ | ✓ | - | - | V-T | 0.40 |

> "From Rows Ex0–Ex3 in Tab. 3, we verify the contribution of each proposed component … This configuration achieves a significant 17% improvement over the vanilla VLA, demonstrating the effectiveness of the tactile gate in preserving the pretrained knowledge of the model." (§4.4.1)
(분해해 보면 Adaptive Tactile Injection 만으로 +17%p, Reaction Dual-Stream 을 얹어 추가 +11%p. 본 논문의 두 축 기여가 거의 비슷한 무게로 누적된 셈입니다.)

> "Moreover, we observe that the force 6D modality achieves the best performance, followed by marker 2D, and then the visual-tactile image. We hypothesize that higher-dimensional tactile inputs may excessively perturb the pretrained representation space, as they introduce a larger number of tactile tokens." (§4.4.2)
(촉각 포맷 차원이 낮을수록 사전학습 표현을 덜 흔든다는 흥미로운 가설입니다. D11 의 "촉각 인코더 후보" 선택지에서 Sparsh 같은 고차원 V-T 표현이 vanilla 분포를 어지럽힐 위험을 정량화한 첫 사례로 읽어도 됩니다.)

![Figure 4 — Execution progress on four contact-rich tasks](https://arxiv.org/html/2605.07308/x3.png)

> "Figure 4: Visualization. We visualize the execution progress of four typical contact-rich tasks." (§4.3)
(Unzip Bag · Stamp · Wipe Vase · Unscrew Lid 각각의 자율 실행 스냅숏입니다. 본 논문이 어떤 종류의 접촉 집약 행동을 목표로 삼는지 한눈에 잡힙니다.)

---

## ⚖️ 한계

- **백본·하드웨어 종속성** — vanilla VLA 를 GO-1 으로 고정했고, GO-1 의 사전학습 데이터셋 (AgiBot World) 과 동일 하드웨어 (AgiBot Genie1) 라는 사실을 명시적으로 가정으로 깔고 있습니다. 다른 백본이나 다른 하드웨어에 이식할 가능성은 본문에서 다루지 않습니다.
- **Unscrew Lid 의 grip slippage** — 본 논문의 유일한 baseline-열세 케이스. "occasionally leading to failure cases where the gripper slips during unscrewing" (§4.2) 라고 인정합니다. 접촉을 시점별로 미세 조정해야 하는 구간에서, 촉각 토큰 자체에 머무는 본 모델의 패스트 스트림만으로는 부족할 수 있다는 신호로 읽힙니다.
- **수동 라벨 의존** — Tactile Gate 학습을 위해 사람이 에피소드별로 contact/non-contact 프레임을 0/1 로 라벨링합니다. 본문에 자동 라벨링이나 self-supervised gate 학습 대안은 없습니다.
- **고차원 촉각 페널티** — Sparsh 같은 사전학습 V-T 인코더가 (논문 결과로 보면) 오히려 손해입니다. 본 논문은 이를 "토큰 수가 많아 사전학습 표현이 더 크게 흔들리기 때문" 으로 해석할 뿐, structured/finger-bound 인코딩으로 차원을 흩지 않고도 토큰을 줄이는 대안은 다루지 않습니다.
- **시뮬 평가 부재** — 모든 평가가 실세계에서 진행됩니다. 시드 일관성, 통계 분산, ablation 신뢰구간을 보기 어렵습니다. 시드별 15 trials 라는 적은 표본도 한계입니다.

---

## ♻️ 재현성

- **프로젝트 페이지** — `https://sites.google.com/view/at-vla` 로 본문에 명시. 코드 공개 여부는 본문에서 단정하지 않습니다.
- **베이스라인 재현 수준** — VTLA 는 공식 구현이 없어 DexVLA 코드베이스로 자체 재현. RDP 는 Diffusion Policy 위에 PCA 마커 입력. 비교 셋업은 본 논문이 직접 설정한 contact-only 평가라 그대로 옮기기는 어려운 구조입니다.
- **데이터** — 자체 수집한 30~50 demos/task. 공개 여부는 본문에서 다루지 않습니다.
- **하드웨어 의존** — AgiBot Genie1 + Xense Robotics 촉각 센서가 사실상 필수. 다른 다지 손 (Sharpa, xhand 등) 으로 옮기려면 촉각 인코더와 액션 공간을 다시 짜야 합니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

`context/MASTER.md` 기준 관련 항목을 매핑합니다.

- **P4 (VLM 사전학습 보존) — 핵심 지지/긴장 모두 강함.** 저자들은 촉각 토큰을 그대로 추가하면 사전학습 attention 분포가 흩어진다는 음의 결과를 정량·시각적으로 보입니다 (Ex0→Ex1 에서 -9%p, Fig. 3 attention map). 이 결과는 D19 v1 "full VLM freeze + action experts only" 와 D20 v1 "action-side adapter" 의 사상에 정합합니다. 다만 본 논문은 freeze 가 아니라 액션 전문가까지 FT 하면서도 cross-attention query 자리만 게이트로 바꾸는 방식으로 보존을 달성합니다. PROBE 의 D19 보존 메커니즘과 다른 길이지만 같은 목표를 향합니다.
- **P3 (Hand-level System0 모듈) — 사상은 강하게 겹치되 수단이 다름.** Dual-Stream 의 패스트:슬로우 3:1 비동기 추론은 PROBE D14 "System1↔System0 binary on/off 인터페이스" 의 사상 직속. 단 본 논문의 패스트 스트림은 BC + BCE 로 학습된 지도 학습 모듈이지 RL 이 아닙니다. PROBE 의 System0 가 (slip 억제 / grasp 유지처럼) reward-engineerable 한 영역에만 RL 을 두기로 한 결정과 직접 충돌하진 않지만 "BC + 게이트만으로 어디까지 가능한가" 라는 반증 신호로 읽힙니다. 결국 P3 입장에서 System0 RL 의 필요성을 다시 한 번 정당화해야 하는 압박이 들어오는 셈입니다.
- **P2 (구조적 입력-모달리티 결합) — 부분 관련.** 본 논문은 손가락-바인딩 같은 PROBE D8 식 구조화 없이 단일 합력 6D 벡터 한 덩어리로 촉각을 토큰화합니다. 그럼에도 force 6D 가 V-T image · marker 2D 를 모두 앞섰다는 결과는 D11 v1 "tactile feature 옵션 비교" 에 directly 입력 가능한 데이터점입니다. 동시에 본 논문이 finger-wise attribution 을 시도조차 하지 않은 사실은 PROBE 의 차별점으로 남습니다.
- **P1 (Heterogeneous Body/Hand Action Expert) — 약한 관련.** 본 논문에는 body/hand 분리가 없습니다. 양팔 14-DoF 를 단일 액션 전문가가 산출합니다. 단 Dual-Stream 의 "느린 시각·언어 / 빠른 촉각" 비동기 분리는 D5 (input-modality + control-rate separation) 의 deferred 트리거 "finger precision needs higher-frequency loop than body" 에 대한 외부 실증 사례로 활용 가능합니다.
- **§10 경쟁자 함의.** Tactile-VLA · TLA · TA-VLA · VTLA · RDP 가 본 논문의 비교군으로 한자리에 모였습니다. 이 중 PROBE §10 에 핀된 항목은 아직 없으나, 사실상 PROBE 의 "tactile-VLA 가족" 경쟁군 전체와 정면 대응한 논문입니다. 특히 vendor 측면에서 IMCopilot / Sharpa 와 동일 사상 (VLA + 접촉 정밀화) 의 비-Sharpa 계열 변종으로 자리합니다.
- **Identity 긴장/지지.** "VLA-level 에서 직접 dexterity 를 tackle" 한다는 PROBE Identity 와 정확히 같은 자리에 섭니다. 단 본 논문의 dexterity 는 양팔 그리퍼 + 합력 6D 수준입니다. PROBE 가 겨냥하는 multi-finger / 손가락 contact-rich 영역에 비하면 한 단계 위 추상화입니다. **VLA-level 사전학습 보존 + 패스트 촉각 스트림** 이라는 두 축은 그대로 채택 가능, **단일 액션 전문가 + 그리퍼 합력 토큰** 부분은 PROBE 의 P1·P2 으로 elevating 해야 할 외부 사례로 자리매김합니다.

---

## ✨ 핀 논문 대비 델타

- **π0 [arXiv:2410.24164](https://arxiv.org/abs/2410.24164) / π0.5 [arXiv:2504.16054](https://arxiv.org/abs/2504.16054) 대비** — π0.5 의 hierarchical inference 가 시각·언어 두 축의 단계화였다면, 본 논문은 같은 사상을 시각 vs 촉각 으로 비틀어 옮깁니다. π0.5 가 본 논문의 비교군으로 등장해 GO-1 보다 낮은 Unzip Bag 점수를 받았다는 사실도 그대로 데이터점이 됩니다.
- **TwinBrainVLA [arXiv:2601.14133](https://arxiv.org/abs/2601.14133) 대비** — TwinBrainVLA 가 "frozen generalist + trainable specialist" 의 AsyMoT 구조였다면, 본 논문은 "frozen-equivalent (vanilla VLA 구조 그대로) + gated specialist injection" 의 query-자리 교체 방식. 모듈을 새로 얹지 않고 attention query 만 교체하는 식이라, 사전학습 보존 강도는 본 논문 쪽이 더 깊습니다.
- **VLA-Adapter [arXiv:2509.09372](https://arxiv.org/abs/2509.09372) / PriorVLA [arXiv:2605.10925](https://arxiv.org/abs/2605.10925) / VLM2VLA [arXiv:2509.22195](https://arxiv.org/abs/2509.22195) 대비** — 이들이 "어떻게 adapter 를 끼울까" 였다면, 본 논문은 "언제 끼울까 (게이트)" 와 "어디에 끼울까 (query 자리만)" 두 결을 추가합니다. 시간축·구조축 통제를 동시에 거는 형태가 핀 논문에는 부재합니다.
- **MolmoAct2 [arXiv:2605.02881](https://arxiv.org/abs/2605.02881) 대비** — MolmoAct2 가 per-layer KV-cache 조건화로 VLM 을 보존했다면, 본 논문은 attention 의 query 자리만 시간 조건부로 갈아치워 동일 보존 효과를 노립니다. PROBE D19 deferred 후보 (selective unfreeze / LoRA / per-layer KV) 옆에 "query-슬롯 게이트 교체" 라는 새 옵션을 데이터점으로 얹을 수 있습니다.
- **ViTacFormer [arXiv:2506.15953](https://arxiv.org/abs/2506.15953) / DexViTac [arXiv:2603.17851](https://arxiv.org/abs/2603.17851) / AdapTac [arXiv:2505.13982](https://arxiv.org/abs/2505.13982) / SaTA [arXiv:2510.14647](https://arxiv.org/abs/2510.14647) / Sparsh [arXiv:2410.24090](https://arxiv.org/abs/2410.24090) 대비** — P2 핀들은 모두 "촉각을 어떻게 잘 토큰화할까" 에 집중합니다. 본 논문은 정반대로 "토큰 차원을 낮춰 사전학습을 덜 흔드는 쪽이 이긴다" 라는 음의 신호를 던집니다 (force 6D > marker 2D > V-T image). 핀 사이의 가설을 직접 충돌시키는 카운터 데이터점.
- **HORA [arXiv:2210.04887](https://arxiv.org/abs/2210.04887) / AnyRotate [arXiv:2405.07391](https://arxiv.org/abs/2405.07391) 대비** — P3 핀의 RL 라인이 "사전학습 없이 접촉 안정화" 였다면, 본 논문은 "사전학습된 VLA 그대로 두고 접촉 반응만 BC 로 끼워 넣기". RL 의 필요성 자체를 antagonist 입장에서 흔드는 외부 증거.

---

## ⚙️ 의사결정 함의

- **D5 (input-modality + control-rate separation) 의 deferred 트리거 보강** — v1 은 "shared rate", deferred 트리거는 "finger precision needs higher-frequency loop than body". 본 논문은 양팔 그리퍼 수준에서도 촉각 패스트 스트림 (slow:fast = 1:3) 만으로 0.04 초 폐루프가 성능을 의미 있게 끌어올린다는 직접 증거를 내놓습니다. PROBE 의 실로봇 데모(in-hand rotation 실세계) 에서 finger 수준 control rate 분리의 deferred 발동 조건을 명문화할 때, "3:1 비동기 추론, 패스트 스트림은 촉각만, 슬로우 스트림 한 번이 future $`H`$ 스텝의 조건으로 살아남음" 이라는 구체 하이퍼파라미터를 가져올 수 있습니다.
- **D11 (tactile feature 옵션) 의 비교 우선순위 조정** — 본 논문 결과 (force 6D > marker 2D > V-T image) 를 그대로 받으면 PROBE 의 Sharpa Deform Map (비전 기반 320×240 / fingertip) 라인이 dangerous default 일 위험이 있습니다. **단** 본 논문이 finger-wise structured binding 을 시도하지 않은 채로 비교한 결과라는 사실을 잊으면 안 됩니다. PROBE D8 (per-finger proprio-tactile binding, 10+2 토큰) 식으로 토큰 수를 통제해 둔다면 V-T 표현도 살아남을 여지가 있습니다. **의사결정 함의는 "V-T 인코더를 쓰려면 먼저 토큰 수를 finger 토큰으로 묶어야 한다" 라는 사전 조건을 D11 Non-negotiable 에 추가하는 것입니다.**
- **D14 (System1↔System0 interface) v1 보강** — v1 "binary on/off, bypass-when-off" 가 본 논문의 Tactile Gate 와 사상이 같습니다. 본 논문은 **임계값 0.5 + BCE 지도** 라는 구체 하이퍼파라미터까지 제시. PROBE 의 D14 deferred (continuous blend, 트리거 = 하드 스위칭 finger-command discontinuity at 실로봇 데모) 에 본 논문의 0.5 임계값을 v1 의 안전한 시작점으로 명시할 수 있습니다.
- **D19 (VLM FT 범위) / D20 (prior-preservation strategy) — v1 freeze 의 사후 검증.** 본 논문 Ex1 (-9%p) → Ex2 (+17%p, gate + adaptive cross-attn) 는 "토큰 시퀀스를 단순 augmentation 하면 사전학습이 망가진다" 는 강한 외부 증거. PROBE v1 의 full-freeze + action-side adapter 노선이 본 논문의 query-슬롯 교체보다 더 보수적이므로, v1 은 안전하게 유지하되 새 modality 추가 시 본 논문 패턴 (key/value 는 사전학습된 채 그대로, query 만 게이트로) 을 D19 deferred 옵션의 한 자리에 추가할 가치가 있습니다.
- **D26 (평가 메트릭) — modality-agnostic 메트릭 추가 후보.** 본 논문 Table 2 의 "동일 가중치 · 추론 시 촉각 OFF" 비교는 PROBE 의 robustness 메트릭에 자연스럽게 끼울 수 있습니다 — "촉각 센서 fault 시 vanilla 대비 drop 폭" 을 D26 robustness 항목 (실로봇 데모 단계 이후) 에 명시적 sub-metric 으로 추가 가능. 본 논문 결과를 그대로 받으면 임계값은 "vanilla 와 동등 (≥0.7 평균 유지)".

---

## ⚠️ 먼저 검증할 실패 모드

- **Sharpa Deform Map 로의 직접 전이 실패** — 본 논문의 force 6D 우위는 "토큰 수가 적어 사전학습 표현을 덜 흔든다" 라는 해석에 기댑니다. PROBE 가 채택한 Sharpa Deform Map 은 320×240×fingertip 의 고차원 V-T 이미지에 가깝습니다. 본 논문의 결과를 무비판적으로 받으면 PROBE 의 D11 가설 ("hardware-specific CNN on Deform Map → per-fingertip feature → 손가락 토큰") 자체가 흔들립니다. **싼 sanity check** — 시뮬 환경에서 동일 baseline (vanilla π0 freeze + 액션 전문가 FT) 위에 (a) Deform Map 을 그대로 토큰화 vs (b) Deform Map → CNN → fingertip 토큰 (D8 식 finger binding) 두 변종을 두고 in-hand rotation 단일 태스크에서 attention map / 성공률 drop 을 측정. 만약 (a) 가 vanilla 보다 더 떨어지면 본 논문의 음의 신호가 PROBE 스택에서도 재현된 것이고, D11 Non-negotiable 에 "토큰 수 통제" 명시 사유가 됩니다.
- **BC + 게이트만으로 slip 억제 가능 가설** — 본 논문은 "패스트 스트림에 RL 없이도 0.04 초 폐루프 + BCE 게이트만으로 충분" 이라는 antagonist 신호를 보냅니다. 하지만 Unscrew Lid 의 자체 실패 모드 ("gripper slips during unscrewing") 가 정확히 PROBE P3 System0 가 메우려는 자리입니다. **싼 sanity check** — 본 논문 Reaction Dual-Stream 만 떼어내 PROBE 의 in-hand rotation 시뮬에 이식하고, 동일 task 에서 (a) BC 패스트 스트림만 vs (b) BC + System0 PPO 라인을 비교. 본 논문 식 BC-only 패스트 스트림이 slip count / pose stability (D26 메트릭) 를 만족 못 시키면 P3 System0 RL 필요성 정당화의 직접 증거가 됩니다.
- **수동 contact 라벨의 우리 스택 비호환** — 본 논문은 사람이 에피소드별로 0/1 contact 프레임 라벨링을 합니다. PROBE 의 D11 보조 헤드 (contact-binary + slip-binary aux head) 가 이미 같은 의미의 라벨을 요구하지만, PROBE 는 hardware contact 신호 (Sharpa fingertip 접촉 임계 + tactile-image energy) 로 자동 추출하는 쪽이 자연스럽습니다. **싼 sanity check** — 본 논문 식 사람 라벨 vs hardware 자동 라벨 두 가지로 게이트를 학습해 게이트 AUROC 와 다운스트림 태스크 성공률을 비교. 자동 라벨이 충분히 잘 작동하면 PROBE 는 본 논문 라벨링 부담을 우회합니다.
- **단일 게이트 vs finger-wise 다중 게이트의 미해결 비교** — 본 논문은 그리퍼 단일 합력 → 단일 게이트 구조. PROBE 의 손가락 10 개 + 손바닥 2 토큰 구조에서는 "어느 손가락이 접촉했는가" 를 finger-wise 다중 게이트로 분해할 여지가 있습니다. 본 논문은 이 옵션을 다루지 않으므로, PROBE 측에서 D8 finger binding 위에 게이트 다중화 vs 단일화를 직접 비교 실험으로 붙여 봅니다. 단일 게이트로 출발하되 finger-wise 게이트 deferred 트리거 (contact-rich finger 가 episode 내 2 개 이상으로 나뉘는 비율) 를 D14 옆에 명시 후보로 추가할 만합니다.

---

## 💡 컨텍스트 제안

- **§8.4 (P4 핀) 후보로 추가 검토** — 현재 P4 핀 8 종 (π0 / π0.5 / VLM2VLA / RT-2 / VLA-Adapter / PriorVLA / Multi-Embodiment / MolmoAct2) 모두 "어떻게 끼울까" 계열. 본 논문은 "언제 / 어디 슬롯에 끼울까" 라는 직교 축의 첫 사례라 핀 교체 후보로 강합니다. 가장 약한 핀과 교체하는 안을 권장합니다. 다만 P4 핀은 hard cap 8 이라, 어떤 항목을 빼야 할지는 사람이 판단합니다 (sketch 안: Multi-Embodiment Pretraining Data 가 D22 활용도 가장 낮음).
- **§10.3 (Architectural siblings — P1 split) 가 아니라 새 카테고리 "tactile-VLA injection siblings" 신설 검토** — 본 논문 + Tactile-VLA + TLA + TA-VLA + VTLA 가족이 한 줄로 모니터링 대상에 떠올랐습니다. §10.1 (VLA-only strong performers) 옆에 §10.5 (tactile-VLA injection — 본 논문 + Tactile-VLA + TLA + TA-VLA 가족 + RDP) 항목 신설 권장. 본 논문이 사실상 그 카테고리의 SOTA 로 자리하므로 베이스라인-Watch 의 자연스러운 anchor.
- **D11 Non-negotiable 항목 추가 후보** — 현재 (1) no Sharpa lock-in, (2) preserve contact-relevant features 두 줄. 본 논문 발견에 비추어 (3) "촉각 토큰 수를 finger 토큰 단위로 통제 (raw V-T 이미지를 그대로 token sequence 에 푸는 것 금지)" 를 추가 후보로 검토하고자 합니다. PROBE D8 식 binding 을 사후적으로 정당화하는 항목이기도 합니다.
- **D14 v1 라인에 본 논문 임계값 명시** — 현재 v1 "binary on/off" 만. 본 논문이 제공한 "BCE 손실 + threshold 0.5 + λ = 0.01 멀티태스크" 구체 하이퍼파라미터를 v1 의 "안전한 첫 시작점" 으로 한 줄 명시하면 구현 진입 시 시행착오를 줄입니다.
- **D26 robustness sub-metric 추가** — Table 2 의 "modality-agnostic" 비교를 PROBE 평가 프로토콜의 robustness 카테고리에 sub-metric 으로 흡수. "동일 가중치 · 추론 시 촉각 OFF 시 평균 성공률 drop ≤ 10%p" 같은 임계값으로 본 논문 결과를 PROBE 데이터점으로 변환 가능.
