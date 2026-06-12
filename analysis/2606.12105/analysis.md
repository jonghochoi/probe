# Paper Analysis — DAM-VLA: Decoupled Asynchronous Multimodal Vision Language Action model

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | DAM-VLA: Decoupled Asynchronous Multimodal Vision Language Action model |
| 저자 | Pankhuri Vanjani, Zhuoyue Li, Jakub Suliga, Moritz Reuss, Gianluca Geraci, Xinkai Jiang, Rudolf Lioutikov (Intuitive Robots Lab, KIT · NVIDIA · Robotics Institute of Germany) |
| 링크 | [arXiv:2606.12105](https://arxiv.org/abs/2606.12105) · [Website](https://intuitive-robots.github.io/DAM-VLA/) |
| 발행일 / 버전 | 2026-06-10 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-11 |
| 관련 Pillar | P2, P1, P4 |
| 태그 | vla-arch, force, peft |

---

## 🧭 한 줄 요약 (TL;DR)

VLA 가 vision-language 사전학습에서 물려받은 **단일 동기 클럭(synchronous clock)** 이 물리적 상호작용의 다중-rate 구조와 어긋난다는 진단 위에서, DAM-VLA 는 **모달리티별 latent buffer 를 각 센서 rate 로 갱신**하고 action head 가 이를 매 제어 스텝 연속적으로 읽되, 고주파 모달리티(force/torque)는 **gated cross-attention(GCA)** 으로 주입해 사전학습 backbone 을 건드리지 않는다. 7 개 contact-rich 실로봇 태스크에서 최강 동기 baseline 대비 평균 성공률을 2 배 이상(95.2% vs 40.95%) 끌어올리면서 100 Hz 제어를 유지한다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 현행 VLA 는 vision·force·proprioception·tactile 을 매 고정 timestep 에 함께 인코딩하는 **동기(synchronous) 처리**를 쓴다. 이는 VLM 에서 물려받은 단일 클럭이며, 센서마다 정보가 의미를 갖는 rate 와 horizon 이 다른 물리 세계와 근본적으로 어긋난다.
- **기존 접근의 한계** — 동기 클럭은 (1) 느린 모달리티(비전)를 oversample 하고 (2) 빠른 모달리티(force)를 undersample 하며 (3) 가장 느린 모달리티의 관측 번들이 도착할 때까지 action 생성을 막아 유효 제어 주파수를 바닥에 묶는다. force-torque 는 100–500 Hz, RGB 는 3–10 Hz 로 정보가 들어오는데 한 클럭이 둘 다를 망친다.
- **본 논문의 가설** — 모달리티별로 **시간 처리를 분리(decouple)** 해 각자 센서 rate 로 갱신·유지하면 더 강한 표현과 더 robust 한 제어가 나온다. Decoupling 은 두 축 — *asynchrony*(각 모달리티를 자기 센서 rate 로 처리) + *temporal context*(각 모달리티가 자기 의미 horizon 만큼의 buffer 유지) — 로 구성된다.
- **왜 지금 중요한가** — 동기 클럭에서 단순히 제어 주파수만 올리면(naive frequency scaling) 동일 프레임에 서로 다른 action label 이 붙어 모순 학습 신호가 생기고 성능이 오히려 떨어진다(21.9% < 40.95%). 병목이 controller rate 가 아니라 **아키텍처**임을 보이며, 멀티-rate VLA 설계가 contact-rich dexterity 의 실용 경로임을 주장한다.

---

## 🧩 핵심 기여

- **비동기 멀티모달 아키텍처** — 각 모달리티 스트림이 자기 자연 주파수로 독립 갱신되고, 신호의 의미 horizon 에 맞춰 크기를 정한 모달리티별 temporal context window 를 갖는 decoupled 처리 설계.
- **비동기 표현을 통한 성능 향상** — 각 센서의 자연 정보 구조를 보존해 동기 baseline 보다 높은 성공률의 멀티모달 표현을 학습. 평균 성공률 +54.25%p.
- **추론 지연 감소** — action 생성을 느린 모달리티 갱신 주기(주기적 VLM 재인코딩)에서 분리해, 정책이 제어 주파수로 연속 동작하며 end-to-end latency 를 낮추고 유효 제어 주파수를 올림.
- **통합 메커니즘이 표현 품질을 좌우함을 분리 검증** — 동일 정보(force+memory)를 flat concat 으로 넣은 X-VLA$`_{AFM}`$(54.3%) 대비 GCA 의 DAM-VLA(95.2%) 격차로, "정보 자체"가 아니라 "정보가 사전학습 backbone 에 *어떻게* 들어가는가"가 이득을 만든다는 점을 입증(RQ4).

---

## 🔑 기술 키워드

- **Synchronous clock / fixed clock** — 모든 입력을 한 박자에 맞춰 인코딩하는 단일 시계. VLM 에서 물려받은 가정이며, 본 논문이 깨려는 대상.
- **Asynchronous decoupling** — 모달리티마다 갱신 시점을 따로 두는 것. 오케스트라가 한 메트로놈이 아니라 악기별 호흡으로 연주하는 것에 가깝다.
- **Per-modality latent buffer** — 모달리티별로 마지막 인코딩 결과(토큰열)를 캐싱해 두는 저장소. 갱신 이벤트 사이에는 캐시를 그대로 읽어 action head 가 매 스텝 소비.
- **Gated Cross-Attention (GCA)** — 새 모달리티 토큰을 사전학습 self-attention 에 섞지 않고, gate 로 조절되는 cross-attention 잔차로 action 토큰에만 주입하는 어댑터. Flamingo 의 zero-init gated XA 에서 영감.
- **Global gate vs. input-dependent gate** — 시각 메모리는 에피소드 내내 유효하므로 입력과 무관한 학습 스칼라 gate($`\tanh(\alpha)`$), force 는 접촉 국면에서만 유효하므로 입력 의존 sigmoid gate 로 게이팅.
- **Force/torque as high-frequency modality** — 100–500 Hz 로 접촉 transient 를 포착하는 대표적 고주파 모달리티. 본 논문에서는 Franka 내부 추정치(7-D joint-torque)를 사용.
- **Action chunking / execution horizon $`s`$** — 한 번의 추론으로 생성하는 action 시퀀스 길이. $`s`$ 가 클수록 open-loop 실행이 길고 replanning 빈도는 낮아짐.
- **Redundant-frame bias** — 동기 클럭에서 비전을 제어 rate 로 upsample 할 때 동일 프레임이 서로 다른 action label 과 짝지어져 정책이 머뭇거리는 작은 동작만 내는 학습 병리.
- **X-VLA** — soft-prompted cross-embodiment VLA backbone (arXiv:2510.10274). DAM-VLA 의 모든 구성이 공유하는 토대 모델.

---

## 🔬 방법론

### 직관

DAM-VLA 의 출발점은 단순한 관찰이다 — 카메라는 초당 몇 장의 정보만 새로 주지만 접촉 힘은 초당 수백 번 바뀐다. 그런데 기존 VLA 는 이 둘을 같은 박자에 묶어 인코딩하므로, 비전은 똑같은 장면을 매 스텝 다시 계산하느라 연산을 낭비하고(redundant compute), force 는 의미 있는 변화 대부분을 놓치며(undersample), 결정적으로 모든 모달리티가 도착할 때까지 action 을 못 내 제어가 느려진다.

해법은 "각 모달리티가 자기 센서 rate 로 갱신되고, 자기 의미 horizon 만큼만 기억하게 두자"는 것이다. 구현은 **모달리티별 latent buffer** 다. 비전은 4 스텝마다 한 번 인코딩해 그 결과를 buffer 에 채워 두고, 그 사이에는 캐시를 그대로 읽는다. force·proprioception 은 매 제어 스텝 buffer 를 갱신한다. action head 는 buffer 전체를 매 스텝 연속으로 읽으므로, action 생성이 어느 개별 모달리티의 인코딩 일정에도 막히지 않는다.

두 번째 핵심은 "새 고주파 모달리티를 사전학습 backbone 에 *어떻게* 넣는가"다. 토큰을 그냥 이어붙이면(flat concat) 사전학습 self-attention 이 한 번도 본 적 없는 토큰을 처리하게 되어 기존 표현이 망가진다. DAM-VLA 는 대신 **gated cross-attention** 을 backbone 의 4 번째 블록마다 끼워, 0 으로 초기화된 잔차로 action 토큰에만 새 정보를 주입한다. 학습 초기에는 기여가 0 이고 점진적으로 자라므로 사전학습 가중치를 건드리지 않는다.

마지막으로 gate 의 형태를 모달리티 신호 구조에 맞춘다. 시각 메모리는 에피소드 내내 유효하므로 입력과 무관한 전역 gate 를, force 는 접촉 순간에만 유효하므로 입력에 따라 열리고 닫히는 gate 를 쓴다. 이로써 명시적 접촉 검출 없이도 "언제 force 가 정보적인가"를 네트워크가 학습한다.

### 아키텍처

![Figure 1 — synchronous vs asynchronous concept](https://arxiv.org/html/2606.12105/figures/concept_figure.png)

> "Standard synchronous VLAs operate on a single slow clock, missing critical high-frequency contact transients. In contrast, DAM-VLA updates each modality asynchronously at its natural sensor rate, successfully capturing fast dynamics and enabling smooth, continuous control." (§1, Figure 1)
> (동기 VLA 가 느린 단일 클럭으로 고주파 접촉 transient 를 놓치는 반면, DAM-VLA 는 모달리티별 자연 rate 로 비동기 갱신해 빠른 동역학을 포착한다는 본 논문의 핵심 대립 구도를 한 장으로 시각화.)

**입력 모달리티와 rate.** 정책은 $`M`$ 개 이질 센서 모달리티 $`\mathcal{M}=\{m_{1},\ldots,m_{M}\}`$ 를 받으며, 실험 구성은 3인칭 scene 카메라 25 Hz, wrist 카메라 25 Hz, force/torque 100 Hz(Franka 내부 센서), proprioception 100 Hz, 그리고 에피소드 동안 정적인 language instruction 이다.

> "We decouple each modality's update rate from the control rate, maintaining a per modality latent context $`z_{\mathrm{m}}`$ in a shared buffer. ... The action head is conditioned on this latent buffer, so that action generation is not blocked by individual modality's update rate." (§3.1)
> (각 모달리티의 갱신 rate 를 제어 rate 에서 떼어내 공유 buffer 의 모달리티별 latent context 로 유지하고, action head 를 이 buffer 에 조건화함으로써 action 생성을 개별 모달리티 갱신에서 해방시키는 것이 문제 정식화의 핵심.)

![Figure 2 — DAM-VLA architecture](https://arxiv.org/html/2606.12105/figures/architect_mod.png)

> "Each modality stream encodes tokens into independent latent buffers at their sensor rate ... The action expert reads all buffers continuously via parallel GCA pathways, a global-gate pathway for visual memory and an input-dependent gate pathway for force/torque, adding new modalities through dedicated cross-attention modules that preserve the pretrained self-attention structure." (§3.2, Figure 2)
> (모달리티별 독립 buffer + action expert 가 병렬 GCA 경로로 모든 buffer 를 연속 read 하되, 시각 메모리는 전역 gate, force/torque 는 입력 의존 gate 를 쓰는 dual-pathway 구조를 보여주는 메인 아키텍처 다이어그램.)

**비동기 데이터 수집.** 모든 스트림을 한 timestamp 로 동기화해 기록하지 않고, 각 모달리티를 자기 센서 rate 로 독립 수집해 모달리티별 timestamp 와 함께 저장한다. 학습 시 각 action label 에 대해 모달리티별 고정 history window 를 자연 해상도로 가져온다 — 비전은 25 Hz 로 16 프레임(≈0.64 s 의 의미적 시각 맥락), proprioception·force 는 100 Hz 로 각 96 샘플(≈0.96 s 의 고해상도 상태·접촉 history).

**Multimodal asynchronous latent buffer.** 공유 buffer 를 다음과 같이 정의한다.

$$\mathcal{B}=\{Z^{m}\}_{m\in\mathcal{M}}, \qquad Z^{m}\in\mathbb{R}^{N_{m}\times d}$$

각 $`Z^{m}`$ 은 모달리티별 rate 로 refresh 된다. 매 추론 스텝에서 각 $`Z^{m}`$ 의 토큰은 *처리되되 소비되지 않는다(processed but not consumed)* — 추론 주파수가 센서 갱신보다 빠르면 같은 입력을 다시 읽는다. 모달리티별 처리는:

1. **Language tokens** — 에피소드마다 시작 시 1 회 인코딩.
2. **Visual tokens** — primary·wrist 카메라를 vision-language encoder 로 patch 토큰화. 의미적으로 동일한 프레임의 중복 재인코딩을 피하려 시각 encoder 를 **4 추론 스텝마다** 호출.
3. **Proprioception tokens** — joint state 를 X-VLA 처럼 action 토큰과 concat 하되 100 Hz 제어 rate 로 읽어 비동기 buffer 에서 인코딩·처리.
4. **Force tokens** — joint-torque 를 EMA(exponential moving average)로 smoothing 한 뒤 rolling buffer 에 누적. **GRU** 가 이 buffer 를 인코딩하고 force register 에 대한 cross-attention 이 $`Z^{ft}`$ 로 압축, 시각 일정과 무관하게 매 제어 스텝 갱신.

또한 sparse 갱신 사이의 시각 맥락을 위해 **단기 시각 메모리**를 둔다 — 매 시각 갱신마다 새 frame embedding 을 최근 $`K`$ 개 rolling buffer 에 추가하고, GRU 인코딩 + learned-query cross-attention 으로 $`N_{\mathrm{mem}}`$ 토큰 $`Z^{\mathrm{mem}}`$ 으로 압축. 한 스냅샷이 아니라 $`K`$ 프레임을 요약하므로 추론 갱신 사이에 상수로 유지되어도 유효.

### 학습 목표 / 손실

DAM-VLA 의 핵심은 별도 손실항 추가가 아니라 **dual-pathway GCA 조건화 메커니즘**이다. action expert 의 4 번째 transformer 블록마다 두 병렬 GCA 경로를 삽입한다.

**(1) 시각 메모리 경로 — 전역 gate.** 압축된 시각 메모리 토큰 $`Z^{\mathrm{mem}}`$ 이 zero-init 잔차로 action 토큰을 조건화:

$$Z^{(\ell+1)}=Z^{(\ell)}+\tanh(\alpha)\;\mathrm{CA}\!\bigl(\mathrm{LN}(Z^{(\ell)}),\;Z^{\mathrm{mem}}\bigr)$$

> "where $`\alpha`$ is a learned scalar initialized to zero so the pathway contributes nothing at the start of training and grows gradually without disrupting pretrained representations. A global gate is appropriate here because temporal visual context is relevant throughout the complete episode." (§3.2, Eq. 1)
> ($`\alpha`$ 를 0 으로 초기화해 학습 초기 경로 기여가 없고 점진적으로 자라 사전학습 표현을 깨지 않으며, 시각 맥락은 에피소드 내내 유효하므로 입력 무관 전역 gate 가 적합하다는 설계 근거.)

**(2) 추가 모달리티 경로 — 입력 의존 gate.** force 토큰 $`Z^{\mathrm{ft}}`$ 은 같은 삽입점에 입력 의존 gate 로:

$$Z^{(\ell+1)}=Z^{(\ell)}+\sigma\!\bigl(W\,\bar{z}^{\mathrm{ft}}\bigr)\;\mathrm{CA}\!\bigl(\mathrm{LN}(Z^{(\ell)}),\;Z^{\mathrm{ft}}\bigr)$$

여기서 $`\bar{z}^{\mathrm{ft}}`$ 은 mean-pooled force 토큰이고 sigmoid gate 는 near-closed 로 초기화.

> "A static gate would be driven open by contact-phase gradients and closed by free-space gradients, converging to a compromise that either leaks noise during free motion or under-weights force during contact. The input-dependent gate lets the network learn when force is informative without requiring explicit contact detection." (§3.2)
> (정적 gate 는 접촉 국면과 자유공간 gradient 사이에서 타협점에 수렴해 잡음 누설 또는 force 과소가중 중 하나로 귀결되므로, 입력 의존 gate 로 명시적 접촉 검출 없이 "force 가 언제 정보적인가"를 학습시킨다는 동기.)

**(3) 직교성 보장.** 결정적으로 force 는 메모리 갱신 *이전* action 토큰 $`Z^{(\ell)}`$ 을 query 해 순수 가산 delta 를 계산한다.

$$\Delta^{\mathrm{ft}}=\mathrm{CA}\!\bigl(\mathrm{LN}(Z^{(\ell)}),\;Z^{\mathrm{ft}}\bigr)-Z^{(\ell)}$$

> "that is added on top of the memory update, keeping the two conditioning pathways orthogonal and preventing cross-modal entanglement. The force gate responds to raw contact state, not to a signal already mixed with visual memory context to ensure reactive response at high frequency." (§3.2, Eq. 3)
> (메모리 갱신 위에 더해 두 경로를 직교 유지하고 cross-modal 엉킴을 막으며, force gate 가 시각 메모리와 이미 섞인 신호가 아니라 raw 접촉 상태에 반응하게 해 고주파 반응성을 보장한다는 설계 의도.)

이 GCA 설계는 Flamingo 의 zero-init gated cross-attention 에서 영감을 받았으며(§3.2, [1]), "사전학습 가중치를 그대로 두고 새 모달리티가 action 토큰에만 잔차 보정을 주입"하는 것이 목적이다.

### 학습 셋업

> "During training, all modalities are first aligned to a common 100 Hz timeline for consistent action labeling. Visual observations are then sampled with stride $`S`$, recovering a sparse history matching the camera's sensor rate, while force is sampled consecutively at the full 100 Hz." (§3.2)
> (학습 시 일관된 action labeling 을 위해 모든 모달리티를 공통 100 Hz timeline 에 먼저 정렬한 뒤, 비전은 stride $`S`$ 로 sparse 샘플링하고 force 는 100 Hz 연속 샘플링해 추론 시 buffer 동작을 그대로 모사.)

- **백본** — X-VLA [31] (arXiv:2510.10274), soft-prompted cross-embodiment VLA. 모든 구성이 동일 backbone·학습 데이터·태스크 split 공유.
- **로봇/센서** — Franka Emika Panda 7-DoF + Robotiq 2F-85 parallel-jaw gripper, DROID-style 플랫폼(3인칭 + wrist 카메라). force/torque 는 외부 센서가 아닌 Franka 내부 추정 14-D(7 joint-torque + 6-D wrench + gripper current) 중 **7-D joint-torque 만** 사용. proprioception 8-D(7 joint position + gripper). action 8-D(7 joint position + 1 gripper). 데이터는 LeRobot-style 포맷, 태스크당 50–60 에피소드.
- **하이퍼파라미터(Table 3)** — learning rate $`2\times 10^{-4}`$, global batch 192, training steps 20,000. 학습 하드웨어 NVIDIA GH200 480GB, 추론 하드웨어 RTX 4060 Ti. backbone training = vision encoder + action expert finetune. visual rate 25 Hz, control 100 Hz, force 100 Hz, proprio 100 Hz, history 용 visual stride $`S=8`$, GCA 삽입 = action expert 의 매 4 번째 transformer 층. 추론 시 visual token 은 1 회 계산·캐시되고 VLM 은 4 추론 스텝마다 refresh.
- **실행** — asynchronous delay-aware execution [20] + horizon-dependent replanning([15], FASTER) 사용.

---

## 📊 실험 설정과 결과

7 개 contact-rich 실로봇 태스크(Scarf folding, Whiteboard cleaning, Button pressing, Handwash top press, Socket insertion, Sweep beads, Lego arranging)에서 태스크당 15 trial 로 성공률(%)을 측정. 네 가지 RQ 로 구조화 — (RQ1) 동기 처리가 성능을 제약하는가/단순 frequency scaling 으로 해결되는가, (RQ2) 비동기 decoupling 자체의 효과, (RQ3) 고주파 모달리티+메모리의 추가 이득, (RQ4) 통합 메커니즘이 성능에 미치는 영향.

### Table 2 — 구성별 태스크 성공률(%)

| Model | Scarf | Whiteboard | Button | Handwash | Lego | Socket | Sweep | **Avg.** |
|---|---|---|---|---|---|---|---|---|
| X-VLA 25 (동기 baseline) | 80.0 | 86.7 | 13.3 | 0.0 | 0.0 | 6.7 | 100.0 | **40.95** |
| X-VLA 100 (naive high-freq) | 80.0 | 13.3 | 6.7 | 0.0 | 0.0 | 0.0 | 53.3 | **21.9** |
| X-VLA$`_{AFM}`$ (concat baseline) | 100.0 | 73.3 | 13.3 | 86.7 | 0.0 | 6.7 | 100.0 | **54.3** |
| DAM-VLA$`_{/F/M}`$ (async alone) | 80.0 | 66.7 | 40.0 | 20.0 | 0.0 | 6.7 | 66.7 | **40.0** |
| DAM-VLA$`_{/F}`$ (memory만) | 100.0 | 73.3 | 86.7 | 40.0 | 0.0 | 6.7 | 100.0 | **58.1** |
| DAM-VLA$`_{/M}`$ (force만) | 100.0 | 86.7 | 86.7 | 80.0 | 13.3 | 13.3 | 86.7 | **66.7** |
| **DAM-VLA (full)** | 100.0 | 100.0 | 93.3 | 100.0 | 93.3 | 80.0 | 100.0 | **95.2** |

> "Across seven contact-rich real-world manipulation tasks, DAM-VLA more than doubles the average success rate of the strongest synchronous baseline (95.2% vs. 40.95%) while sustaining smooth, reactive 100 Hz control." (Abstract)
> (full DAM-VLA 95.2% 가 최강 동기 baseline(X-VLA 25, 40.95%)을 2 배 이상 넘으면서 100 Hz 반응 제어를 유지 — 논문의 헤드라인 수치.)

**RQ1 — 동기 처리는 frequency scaling 으로도 천장에 막힌다.**

> "Increasing control frequency to 100 Hz drops average success further to 21.9%, with degradation across almost all tasks. Notably, sweep falls from 100% to 53.3% and whiteboard from 86.7% to 13.3%, showing that higher frequency actively hurts even on tasks where the synchronous baseline was strong." (§4.2)
> (제어 주파수를 100 Hz 로 올리면 평균이 21.9% 로 *더* 떨어지고, sweep 100→53.3, whiteboard 86.7→13.3 처럼 강하던 태스크도 악화 — 병목이 controller rate 가 아니라 아키텍처임을 보이는 핵심 근거. 동일 프레임이 다른 action label 과 짝지어지는 redundant-frame bias 가 원인.)

**RQ2 — 비동기 decoupling 만으로 naive scaling 의 손실을 회복.** DAM-VLA$`_{/F/M}`$(40.0%)은 force·memory 없이 비동기만으로 X-VLA 25(40.95%)에 근접하고 X-VLA 100(21.9%)을 크게 상회. button 13.3→40.0, handwash 0.0→20.0 처럼 동기 baseline 이 전혀 못 풀던 태스크를 열기 시작하나, 메모리 경로가 없어 sweep(66.7 vs 100.0) 등 시각 의존 태스크에는 일부 퇴행.

**RQ3 — 센서 rate 별 추가 모달리티가 decoupled 토대 위에 누적.** 40.0%(decoupled) → X-VLA$`_{AFM}`$ 54.3 → DAM-VLA$`_{/F}`$ 58.1 → DAM-VLA$`_{/M}`$ 66.7 → full 95.2. memory 단독(DAM-VLA$`_{/F}`$)은 scarf·sweep 100% 지만 contact-critical 에서 부족(Lego 0%), force 단독(DAM-VLA$`_{/M}`$)은 button 86.7·handwash 80.0 지만 46.67% rollout 에서 접촉 사실을 기억 못 해 반복 press. full 모델이 force-유도 접촉 + memory-안정 sequencing 으로 두 실패 모드를 동시 해소(Lego 93.3, socket 80.0).

**RQ4 — GCA 가 새 모달리티 하에서 사전학습 표현을 보존.**

> "X-VLA AFM has the same force and memory inputs as DAM-VLA but concatenates them into one flat token sequence. Despite identical information, it degrades across all tasks (54.3% vs 95.2%). Pushing unseen new tokens through pretrained self-attention disrupts the backbone's visual-language features." (§4.2)
> (동일 force·memory 정보를 flat concat 으로 넣은 X-VLA$`_{AFM}`$ 은 모든 태스크에서 퇴행(54.3 vs 95.2) — 정보가 아니라 *주입 방식*이 이득을 만든다는 본 논문의 가장 결정적인 분리 실험. concat 은 사전학습 self-attention 에 미본 토큰을 밀어넣어 visual-language feature 를 망가뜨린다.)

### 모션 평활성 / 실행 시간(Appendix D–E)

| 지표 (Sweep) | X-VLA 100 | X-VLA$`_{AFM}`$ | DAM-VLA$`_{/F/M}`$ | DAM-VLA$`_{/F}`$ | DAM-VLA$`_{/M}`$ | DAM-VLA |
|---|---|---|---|---|---|---|
| SPARC (낮을수록 매끄러움) | 25.04 | 10.47 | 16.83 | 10.98 | 10.6 | **8.1** |
| Tracking lag (s, 낮을수록 빠름) | 0.135 | 0.124 | 0.139 | 0.128 | 0.127 | **0.118** |

> "Among 100 Hz methods, where all configurations share the same update period, DAM-VLA achieves the lowest lag (0.116 s). ... DAM-VLA completes Sweep episodes faster than all other configurations (22.5 s on average), ruling out the possibility that lower lag simply reflects slower, easier-to-follow motion." (§Appendix D)
> (100 Hz 군 내에서 DAM-VLA 가 최저 SPARC(8.1)·최저 lag 와 최단 Sweep 에피소드(22.5 s)를 동시 달성 — 낮은 lag 가 단지 느린 동작 때문이 아니라 genuine decisiveness 임을 보강. 본문 §4.2 의 X-VLA 25 제외 100 Hz 군 lag 는 0.116 s 로 인용.)

**Replanning 빈도(Appendix F).** 200 Hz controller 에서 execution horizon $`s=22`$(8 Hz)· $`s=6`$(17 Hz) 모두 Handwash·Whiteboard 100% 성공하나, $`s=22`$ 가 더 fluid. 17 Hz 초과($`s<6`$)에서는 sparse 시각 갱신에도 VLM 인코딩 latency 가 병목이 되어 성능 저하.

---

## ⚖️ 한계

- **chunk 내 force-기반 action 보정 부재 (저자 명시)** — DAM-VLA 는 force 를 *표현 향상*에만 쓰고 chunk 내 action 수정에는 쓰지 않는다. 그래서 socket(80%)처럼 매우 contact-heavy 한 태스크에서 작은 정렬 오차가 chunk 중간에 교정되지 않는다. 메커니즘상 force 는 GCA 잔차로 다음 chunk 의 표현을 바꿀 뿐, 이미 생성된 open-loop action 시퀀스를 닫힌 루프로 되돌리지 못한다 — 진정한 고주파 반응성을 위해서는 chunk-내 closed-loop 보정이 필요하다(저자가 "direct next step" 으로 지목).
- **비전의 부분적 decoupling (저자 명시)** — 카메라가 장면 변화가 아니라 고정 타이머(4 스텝)로 갱신된다. 장면이 빠르게 바뀌는 순간엔 stale 한 시각 buffer 를 읽고, 정적인 순간엔 불필요하게 재인코딩한다. 변화 감지 trigger 로 VLM 을 호출하면 닫히는 갭이나, 본 구현은 단순 주기 호출에 머문다.
- **단일 backbone·단일 로봇 검증 (추론된 갭)** — 모든 결과가 X-VLA + Franka Panda + 2F-85 parallel-jaw gripper 단일 설정. 비동기/GCA 이득이 다른 backbone(π0/π0.5 등)이나 high-DoF dexterous hand 로 옮겨갈지는 미검증. 특히 force 가 7-DoF arm 의 joint-torque 추정치라, 다지 손의 per-finger tactile/force 같은 *공간적으로 분산된* 접촉 신호에서도 같은 dual-gate 설계가 통할지는 별개 문제다.
- **force 신호의 품질·차원 (추론된 갭)** — 전용 F/T 센서 없이 Franka 내부 추정 7-D joint-torque 만 사용. 저자는 이를 "특수 하드웨어 없이도 이득"의 근거로 제시하나, 역으로 mean-pooled scalar gate($`\bar{z}^{\mathrm{ft}}`$)가 풍부한 접촉 분포를 단일 스칼라로 압축하므로 per-finger 접촉 attribution 이 필요한 dexterity 에는 정보 병목이 될 수 있다.
- **메모리·force 의 상호보완성이 태스크 의존적 (추론된 갭)** — ablation 에서 memory 단독·force 단독은 서로 다른 실패 모드(반복 press vs 접촉 종료 실패)를 보이고 full 에서만 둘이 상쇄된다. 두 경로의 직교성(Eq. 3) 가정이 깨지는 — 즉 시각 맥락과 접촉이 강하게 결합된 — 태스크에서는 가산 delta 분해가 최적이 아닐 수 있다.

---

## ♻️ 재현성

- **코드** — 본문/메타에 코드 저장소 링크 명시 없음. Project website(intuitive-robots.github.io/DAM-VLA/)만 제공, 코드 공개 여부 불확실(미확인 — 날조 금지).
- **데이터** — 자체 수집 실로봇 데이터(LeRobot-style 포맷, 태스크당 50–60 에피소드, 7 태스크). 공개 여부 본문 미명시.
- **하드웨어** — Franka Emika Panda 7-DoF + Robotiq 2F-85, DROID-style 카메라 셋업(3인칭 + wrist). force = Franka 내부 7-D joint-torque 추정(전용 F/T 센서 불필요). 학습 NVIDIA GH200 480GB, 추론 RTX 4060 Ti — 추론 하드웨어가 소비자급(4060 Ti)이라 배치 비용은 낮음.
- **하이퍼파라미터** — Table 3 에 전 항목 명시(LR, batch, steps, rate, stride, GCA 삽입점)되어 학습 레시피 재현은 비교적 명확. backbone X-VLA 는 공개(arXiv:2510.10274).

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P2(구조적 멀티모달 관측 융합) — 주축.** 본 논문의 헤드라인 RQ4(GCA vs flat concat, 95.2 vs 54.3)는 정확히 **D10(heterogeneous modality fusion beyond concat — cross-attention/asymmetric fusion, not flat concat)** 의 직접 증거다. force 토큰 구성(GRU + cross-attention 압축 → $`Z^{ft}`$, EMA smoothing)은 **D11(proprio-tactile-force token construction)** 의 한 인스턴스이며, "global gate vs input-dependent gate" 의 비대칭 융합은 우리 D10 의 "asymmetric fusion(ForceFlow-style modal masking/AdaLN)" 선택과 메커니즘적으로 같은 계열. **단, 본 논문에는 P2 의 다른 두 축 — D8(multi-camera spatial-geometric grounding)·D9(action/dynamics-aware encoder) — 이 없다.** 카메라는 generic VL encoder 로 per-view 처리되고 3D registration 이 없으며, 이는 우리 P2 가 antagonist 로 지목한 "flat per-camera concat" 에 머문다.
- **P1(이질 Body/Hand action expert).** **D5(input-modality + control-rate separation)** 와 정면으로 맞물린다. 우리 D5 v1 = "(ii) modality-separated + (α) **shared** rate" 인데, DAM-VLA 는 modality-separated + **rate-separated(async)** 로, D5 의 미선택 대안(rate 분리)을 실증한 첫 강한 증거다. 또 **D7(π backbone integration / partition — slice action expert + FT)** 와도 닿는다 — GCA 를 action expert 의 4 번째 블록마다 삽입하고 사전학습 self-attention 을 보존하는 방식은 D7 의 "partition" 설계와 같은 문제(어디를 건드리고 어디를 얼릴 것인가)를 다룬다. **D4(Body↔Hand information sharing via FiLM)** 의 conditioning-layer 관점에서도 input-dependent sigmoid gate 는 FiLM 계열 변조의 사촌.
- **P4(데이터 효율 적응 사전학습).** GCA 의 zero-init gated cross-attention 은 **D20(prior-preservation strategy)** 의 전형적 메커니즘이다 — "backbone 가중치를 그대로 두고 어댑터로만 새 정보 주입". 우리 D20 v1 = "action-side adapter(D4/D7 split heads = adapter) + conservative SFT" 인데, DAM-VLA 는 Flamingo-style gated XA 어댑터로 동일 목표를 달성하며 **D19(adaptation range — VLM freeze + action experts only)** 의 "사전학습 prior 보호" 논리와 정렬. 다만 DAM-VLA 는 vision encoder + action expert 를 finetune 하므로 완전 freeze 는 아니다.
- **Identity 지지/긴장.** Identity 의 "structured multimodal observation fusion — flat-concat 초월" 주장을 강하게 *지지*. 동시에 Identity 가 RL 을 System0 에만 가두는 것과 달리, DAM-VLA 는 RL 없이 imitation 만으로 force 반응성을 얻어 — 우리 P3(System0 RL)가 정말 필요한지에 대한 *대안 가설*을 제기(긴장).
- **경쟁자 함의.** X-VLA(arXiv:2510.10274)를 backbone 으로 쓴 KIT Intuitive Robots Lab 결과. force-VLA 계열(TA-VLA, ForceVLA2, TacVLA, FAVLA, FD-VLA)을 §2 에서 "force 를 동기 융합" 으로 묶어 차별화 — 우리 P2 Tracked 의 ForceFlow/ViTacFormer 와 같은 문제 공간에서 "비동기 + GCA" 라는 새 축을 연다.

---

## ✨ 핀 논문 대비 델타

- **vs ForceFlow (P2 §5 pin, arXiv:2605.11048)** — ForceFlow 는 contact-driven flow matching + asymmetric multimodal fusion(V2F handover)으로 *동기* 프레임 내 비대칭 융합을 한다. DAM-VLA 의 진짜 새로움은 융합을 **시간 축으로 비동기화**한 점 — force 가 비전과 다른 rate 로 buffer 를 갱신하고 action head 가 이를 매 제어 스텝 연속 read 한다. ForceFlow 의 "어느 모달리티가 어느 모달리티를 query 하나"(비대칭)에 DAM-VLA 는 "각 모달리티가 *언제* 갱신되나"(비동기)를 더한다.
- **vs ViTacFormer (P2 §5 pin, arXiv:2506.15953)** — cross-attention visuotactile 융합이라는 메커니즘은 공유하나, ViTacFormer 는 단일 클럭 동기 cross-attention. DAM-VLA 는 (1) 모달리티별 latent buffer 로 rate 를 분리하고 (2) gate 형태를 신호 구조(전역 vs 입력의존)에 맞춰 차별화하며 (3) zero-init 잔차로 backbone 보존을 명시 — "융합 메커니즘이 표현 품질을 좌우한다"(RQ4)는 분리 실험이 핵심 델타.
- **vs FiLM (P1/P2 §5, arXiv:1709.07871)** — input-dependent sigmoid gate 는 FiLM 의 feature-wise 변조 계보지만, DAM-VLA 는 변조를 cross-attention 잔차에 적용하고 gate 를 near-closed 초기화해 학습 초기 안정성을 확보한 점이 다르다.
- **순수 새로움** — P2/P4 어느 pin 도 다루지 않은 "**single synchronous clock 자체가 VLM 으로부터 물려받은 잘못된 가정**" 이라는 진단과, 이를 모달리티별 buffer + dual-gate GCA 로 푸는 통합 레시피. naive frequency scaling 이 *해롭다*(21.9 < 40.95)는 반례도 우리 Tracked 에 없던 증거.

---

## ⚙️ 의사결정 함의

- **D10(P2) — 융합 메커니즘 기본값을 "concat → gated cross-attention 잔차" 로.** 본 논문은 동일 정보라도 concat 이 사전학습 표현을 망가뜨린다는 직접 증거(95.2 vs 54.3)를 준다. 우리 멀티모달 융합 구현에서 force/tactile 토큰을 backbone self-attention 에 append 하지 말고, `tanh(α)`·`σ(W·z̄)` zero-init gate 의 GCA 어댑터로 action expert 의 매 N 번째 층(논문 N=4)에 삽입하는 것을 v1 기본 설계로 채택 검토.
- **D11(P2) — force/tactile 토큰 구성 레시피.** `force_encoder = GRU(EMA(rolling_buffer)) → cross_attention(force_registers) → Z_ft`, gate = `sigmoid(W · mean_pool(Z_ft))`. tactile 도 같은 패턴으로 per-finger register 화 가능(단, mean-pool 스칼라 gate 는 per-finger attribution 을 잃으므로 우리 D12 topology-aware 요구와 충돌 — 주의).
- **D5(P1) — control-rate separation 을 "shared → async" 로 재고할 트리거.** D5 v1 의 shared-rate 가정에 대해, DAM-VLA 는 rate 분리가 contact-rich 에서 +54%p 를 줄 수 있음을 보인다. 우리 스택에서 force/proprio 를 vision 보다 높은 rate 로 buffer 갱신하는 비동기 옵션을 `obs_buffer.refresh_rate[modality]` 같은 config 키로 추가하는 ablation 을 고려.
- **D20(P4) — prior-preservation 의 후보 메커니즘 추가.** 현 D20 v1(action-side split-head adapter)에 "zero-init gated cross-attention(Flamingo-style)" 을 동급 후보로 등록. 핵심 하이퍼: gate 초기값(α=0, sigmoid near-closed), 삽입 주기(매 4 층), 그리고 force-는-pre-memory-token-query(Eq. 3)라는 직교성 제약.
- **구체 수치 앵커** — visual stride `S=8`, GRU+XA 압축 토큰 `N_mem`, GCA 삽입 주기 4, replanning horizon `s∈{6,22}`(17/8 Hz), LR `2e-4`, batch 192, steps 20k 가 우리 재현 시 출발 하이퍼.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 체크) parallel-jaw → dexterous hand 전이.** DAM-VLA 의 force 는 7-DoF arm 의 joint-torque 추정이고 action 은 8-D(7 joint + 1 gripper). 우리의 22-DOF Sharpa Hand 에서는 per-finger 접촉이 *공간적으로 분산*되는데, mean-pooled scalar gate(Eq. 2)가 이를 단일 게이팅으로 뭉개면 손가락별 접촉 attribution 이 사라진다. **먼저** P2 D11/D12 의 per-finger token 을 GCA 의 single-scalar gate 가 아니라 per-finger gate 로 바꿔야 하는지 sim 에서 1 일 내 확인.
- **backbone 의존성.** 모든 이득이 X-VLA 위에서 측정됐다. 우리 backbone 은 π0/π0.5(PaliGemma-2B) 계열이라 action expert 구조·층수·attention 패턴이 다르다. GCA "매 4 층 삽입" 이 π0 action expert 에 그대로 옮겨지는지(층수·차원 정합), zero-init gate 가 flow-matching head 와 충돌 없는지 먼저 toy FT 로 확인.
- **chunk 내 보정 부재의 dexterity 비용.** 저자가 socket 80% 의 원인으로 지목한 "chunk-내 force 보정 없음" 은 in-hand reorientation 같은 우리 Phase 1 태스크에서 더 치명적일 수 있다(미세 미끄러짐이 chunk 중간 교정 필요). 이는 정확히 우리 **P3 System0** 이 메우려는 갭 — DAM-VLA 식 "표현만 향상" 이 System0 RL 을 *대체* 못 함을 시사하므로, 둘을 경쟁이 아닌 보완으로 배치할지 결정 필요.
- **redundant-frame bias 의 재현 조건.** "naive 100 Hz 가 해롭다" 는 결론은 vision 을 zero-order-hold 로 upsample 한 특정 학습 셋업의 산물이다. 우리가 vision 을 애초에 비동기로 두면 이 병리는 발생하지 않으므로, baseline 비교 시 "동기 upsample" 을 straw-man 으로 과대평가하지 않도록 주의.
- **force = joint-torque 추정의 noise floor.** 전용 F/T 센서 없이 내부 추정치를 EMA smoothing 해 쓴다. 우리 Sharpa 의 vision-based Deform Map tactile 은 noise 특성·latency 가 전혀 달라, EMA 시정수와 GRU buffer 길이를 그대로 옮기면 안 됨 — 모달리티별 buffer horizon(96 샘플/0.96 s)을 우리 센서로 재튜닝해야.

---

## 💡 컨텍스트 제안

- **P2 §5 Tracked Literature 추가 후보** — DAM-VLA 를 **D10/D5 비동기 융합** 증거로 비핀(methodology base) 등록 제안. ForceFlow·ViTacFormer 가 *동기* 비대칭 융합을 커버하는 반면, "비동기 멀티-rate 융합 + GCA 사전학습 보존" 축은 현 pin 에 공백. (핀 cap 8 유지 위해 교체가 아닌 non-pinned 추가 권장.)
- **D5(P1) deferred trigger 메모** — "control-rate separation: shared → async" 를 deferred 후보로 기록 제안. 현 v1(shared rate)은 단순성 우선 선택이나, DAM-VLA 의 +54%p 증거는 contact-rich 본격 진입 시 재방문 트리거가 될 수 있음.
- **D20(P4) 후보 확장 메모** — prior-preservation 후보에 "zero-init gated cross-attention adapter" 추가 제안(현 action-side split-head adapter 와 동급 후보).
- 그 외 핀 교체/Decision 이동 제안 없음. (context/ 파일은 수정하지 않았습니다.)

> 💡 base 매핑은 `/implement-design analysis/2606.12105/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
