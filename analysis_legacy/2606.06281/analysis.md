# Paper Analysis — Multi-Resolution Tactile Imitation Learning for Contact-Rich Robotic Manipulation

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Multi-Resolution Tactile Imitation Learning for Contact-Rich Robotic Manipulation |
| 저자 | Rickmer Krohn, Erik Helmut, Niklas Funk, Jan Peters, Vignesh Prasad, Georgia Chalvatzaki (TU Darmstadt · Hessian AI · Robotics Institute Germany) |
| 링크 | [arXiv:2606.06281](https://arxiv.org/abs/2606.06281) · [Website](http://mitas-touch.github.io) |
| 발행일 / 버전 | 2026-06-04 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-08 |
| 관련 Pillar | P2, P1 |
| 태그 | tactile, flow-matching, dataset |

<!-- 본문은 arXiv HTML(LaTeXML, 2026-06-04 생성)에서 전문 확보. curl 실패 없음. -->

---

## 🧭 한 줄 요약 (TL;DR)

서로 다른 시간 해상도를 갖는 이종(heterogeneous) 촉각 센서 — 프레임 기반 GelSight Mini(고공간해상도)와 이벤트 기반 Evetac(고시간해상도) — 를 modality별 CNN stem + 트랜스포머 융합으로 토큰화하여 플로우 매칭 정책을 조건화하는 표현 프레임워크 MiTaS 를 제안합니다. 5개 접촉 집약적(contact-rich) 조작 과제에서 평균 성공률 80% 를 달성하여 vision-only(31%)·visuo-tactile(54%) 베이스라인을 크게 앞섭니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 국소 접촉 상태가 시각만으로는 신뢰성 있게 추정되지 않는 접촉 집약적 조작(삽입·나사 체결 등)을, 상호 보완적인 복수의 촉각 센서를 융합하여 모방 학습으로 푸는 것입니다.
- **기존 접근의 한계** — 대다수 프레임워크가 단일 촉각 modality 에만 의존합니다. GelSight 류 프레임 기반 센서는 고공간해상도를 주지만 충격·초기 슬립·고주파 진동 같은 프레임 사이의 빠른 접촉 변화를 놓칩니다.
- **본 논문의 가설** — 서로 다른 촉각 modality 는 접촉 상호작용의 상호 보완적 측면을 포착합니다 — 표준 vision 기반 센서는 접촉 기하의 공간 해상도를, 이벤트 기반 센서는 고주파 시간 동역학을 담당합니다.
- **왜 지금 중요한가** — Evetac·GelEvent 같은 이벤트 기반 촉각 카메라가 등장하여 고시간해상도 신호(초기 접촉, 슬립, 삽입 중 진동)를 잡을 수 있게 되었고, 이종 촉각의 융합이라는 미탐색 영역이 열렸습니다. 저자들이 밝힌 바로는 고전 vision 기반 촉각 센서와 이벤트 기반 촉각 센서를 결합한 첫 연구입니다.

---

## 🧩 핵심 기여

- 서로 다른 시간 해상도에서 동작하는 이종 촉각 센서 판독값을 추출·융합하는 새로운 아키텍처 — modality별 CNN stem + 트랜스포머 융합.
- multi-tactile co-training 기법 — 작은 외란에 대한 반응성이 핵심인 접촉 집약적 과제에서, 추론 시 Evetac 센서 없이도 visual-tactile 정책 성능을 끌어올림.
- egocentric RGB · vision 기반 · event 기반 촉각을 결합한 5개 접촉 집약적 조작 과제 multi-resolution 촉각 데이터셋.
- 5개 과제에서 평균 성공률 80% 달성(vision-only 31%, visuo-tactile 54% 대비), 단 30개 시연(demo)만으로 학습.

---

## 🔑 기술 키워드

- **MiTaS (Multi-Resolution Tactile Sensing)** — 시간 해상도가 다른 복수 촉각 센서를 하나의 표현 공간으로 융합해 정책을 조건화하는 본 논문의 프레임워크.
- **GelSight Mini** — 카메라가 탄성체 변형을 찍는 vision 기반 촉각 센서. 접촉 기하의 고공간해상도를 제공(25 Hz).
- **Evetac** — 픽셀별 밝기 변화 이벤트만 비동기로 출력하는 event 기반 촉각 센서. 고주파 접촉 동역학을 포착(200 Hz).
- **CNN stem** — 각 modality 를 전용 합성곱 망으로 토큰화하는 입력단. 카메라/GelSight 는 2D conv, Evetac 16프레임 스택은 3D conv.
- **Cross-attention conditioning** — 고차원 센서 토큰을 병목 없이 정책에 주입하는 조건화 방식. 액션 토큰이 query, 센서 토큰이 key/value.
- **Flow matching** — 노이즈→데이터의 직선 경로 위 속도장(velocity field)을 회귀해 액션 분포를 생성하는 학습 패러다임. 플로우 매칭.
- **DiT (Diffusion Transformer)** — 시간 조건부 속도장을 회귀하는 트랜스포머 액션 헤드.
- **AdaLN-Zero** — 플로우 시간 $`t`$ 의 임베딩으로 각 DiT 블록을 adaptive LayerNorm 변조하되, 투영을 0으로 초기화해 항등사상 근처에서 학습을 시작하는 시간 조건화.
- **Multi-tactile co-training** — 학습 시에만 고주파 Evetac 을 절반 배치에 주입해 표현 공간을 규제하고, 배포 시에는 Evetac 인코더를 완전히 제거하는 비대칭 공동학습.
- **Sparsh-X** — 본 논문이 비교한 멀티모달 촉각 트랜스포머 베이스라인. 8 unimodal + 4 fusion 층, attention bottleneck 융합.

---

## 🔬 방법론

### 직관

![Figure 1 — MiTaS 센서 구성](https://arxiv.org/html/2606.06281/figures/hero_mitas.png)

> "Figure 1: MiTaS combines an RGB camera (blue), a GelSight Mini (red) and an event-based Evetac sensor (yellow) mounted on the gripper. Our method fuses these multi-resolution tactile streams to condition a flow-matching policy, enabling improved control in contact-rich manipulation tasks such as key insertion." (§1)
(한글 해설 — 손잡이(gripper)에 장착된 세 종류 센서를 융합해 플로우 매칭 정책을 조건화한다는 전체 구상을 한 장에 보여줍니다.)

설계의 핵심 직관은 각 촉각 modality 가 접촉 상호작용의 서로 다른 측면을 담는다는 데 있습니다.

> "Our key insight is that different tactile modalities capture complementary aspects of contact-rich interactions: standard vision-based sensors provide high spatial resolution of contact geometry, while event-based sensors capture high-frequency temporal dynamics." (§1)
(한글 해설 — GelSight 는 "어디에 어떤 모양으로 닿았는가"(공간), Evetac 은 "방금 무슨 일이 빠르게 일어났는가"(시간)를 담당한다는 분업이 프레임워크 전체를 관통하는 가정입니다.)

특기할 점은 정책이 로봇 상태(proprioception)나 절대 위치를 입력받지 않는다는 것입니다.

> "We want to highlight that since the policy is neither conditioned on robot state nor expressed in absolute position space, it must infer the appropriate relative motion directly from high-dimensional multimodal sensory input." (§3)
(한글 해설 — 정책은 오직 멀티모달 센서 입력만으로 상대 운동(delta)을 추론해야 하며, 이는 촉각 표현의 질이 곧 성능 상한임을 뜻합니다.)

### 아키텍처

![Figure 2 — MiTaS 아키텍처 개요](https://arxiv.org/html/2606.06281/Mitas_viz_009.png)

> "Figure 2: Overview of the MiTaS architecture: Modality-specific CNN stems encode Vision, GelSight, and Evetac sensors into token embeddings. These tokens are fused through transformer-based attention mechanisms and form the condition for a flow matching policy. The policy does not receive the robot state and must infer the delta position prediction solely from sensor readings." (§3.1)
(한글 해설 — stem → 위치/modality 인코딩 → 트랜스포머 융합 → 플로우 매칭 정책 조건화로 이어지는 파이프라인 전체를 시각화합니다.)

**입력 관측.** 각 timestep 관측은 세 modality 의 결합입니다.

$$o_{t}=\bigl[O_{t}^{\text{vision}},\,O_{t}^{\text{gelsight}},\,O_{t}^{\text{evetac}}\bigr]$$

여기서 손목 카메라 $`O_{t}^{\text{vision}}\in\mathbb{R}^{2\times 128\times 128}`$ 는 25 Hz, GelSight $`O_{t}^{\text{gelsight}}\in\mathbb{R}^{2\times 120\times 160}`$ 는 25 Hz, Evetac $`O_{t}^{\text{evetac}}\in\mathbb{R}^{16\times 120\times 160}`$ 는 200 Hz 센서에서 timestep 당 16 이벤트 프레임을 쌓아 빠른 접촉 동역학을 담습니다. Vision·GelSight 는 $`[0,1]`$ 로, Evetac 은 $`[-\tfrac{1}{2},\tfrac{1}{2}]`$ 로 정규화하여 기본 회색 프레임(이벤트 없음)이 $`0.5`$ 가 아닌 $`0`$ 에 대응하도록 합니다.

**센서 stem.** 각 modality 는 전용 CNN stem 으로 토큰화됩니다.

> "Each modality is tokenised by a dedicated CNN-stem to extract a meaningful sensor-specific representation." (§3.1)
(한글 해설 — 손목 카메라는 RGB 2프레임을 채널 축으로 쌓고 4개 strided 2D conv → $`16\times 16`$ 격자의 $`D{=}256`$ 차원 토큰; GelSight stem 은 같은 설계를 $`120\times 160`$ 해상도에 적용해 $`12\times 16`$ 격자; Evetac 의 16프레임 스택은 4층 3D conv 로 시공간을 함께 압축해 $`12\times 16`$ 격자로 만듭니다. 3D-CNN 은 시간 커널 3–3–3–2, 시공간 stride 2, 마지막 (2×4×5) conv 로 시간 축을 붕괴시킵니다.)

**위치·modality 인코딩.** 평탄화 후 각 토큰 $`\mathbf{z}_{i}`$ 는 학습된 위치 벡터와 modality 임베딩으로 증강됩니다.

$$\mathbf{z}^{\prime}_{i}=\mathbf{z}_{i}+\mathbf{p}_{g(i)}+\mathbf{e}_{s(i)}$$

여기서 $`\mathbf{p}_{g(i)}`$ 는 토큰 격자 내 위치를, $`\mathbf{e}_{s(i)}`$ 는 source modality $`s(i)\in\{\text{vision},\text{gelsight},\text{evetac}\}`$ 를 인코딩합니다 — "공간상 어디"와 "어느 센서"를 분리합니다.

**센서 융합.** 증강된 토큰열은 multi-head self-attention · MLP · pre-normalization · residual 의 트랜스포머 인코더를 통과합니다.

> "The fusion transformer allows full self- and cross-attention of sensors, leading to rich multisensory features forming the conditioning for the policy." (§3.1)
(한글 해설 — 센서 간 전(全) self/cross-attention 으로 융합한 토큰 $`\mathbf{C}`$ 가 정책 조건화 입력이 됩니다.)

### 학습 목표 / 손실

정책 출력은 고정 길이 미래 명령열입니다.

$$\mathbf{A}_{t}=[\mathbf{a}_{t},\mathbf{a}_{t+1},\ldots,\mathbf{a}_{t+H-1}]\in\mathbb{R}^{H\times d_{a}}$$

개별 액션은 로봇 로컬 프레임의 delta 명령 $`\mathbf{a}=\Delta\mathbf{p}=[\Delta x,\Delta y,\Delta z,\Delta\psi]\in\mathbb{R}^{4}`$ 로 병진과 z축 yaw 회전을 제어하고 pitch·roll 은 고정합니다. 제어 루프는 예측한 $`H`$ 스텝 중 처음 $`n_{\mathrm{act}}\leq H`$ 만 실행한 뒤 재계획합니다.

조건부 플로우 매칭으로 학습합니다. 초기 노이즈 $`\mathbf{x}_{0}\sim\mathcal{N}(\mathbf{0},\mathbf{I})`$ 와 데이터 종점 $`\mathbf{x}_{1}=\bar{\mathbf{A}}`$ 사이의 직선 확률 경로와 일정 목표 속도장을 정의합니다.

$$\mathbf{x}_{t}=t\cdot\mathbf{x}_{1}+(1{-}t)\cdot\mathbf{x}_{0}, \qquad \mathbf{u}_{t}=\mathrm{d}\mathbf{x}_{t}/\mathrm{d}t$$

학습 목표는 네트워크 출력 $`\hat{\mathbf{v}}_{\theta}(\mathbf{x}_{t},t,\mathbf{C})`$ 가 이 목표 속도장을 회귀하도록 MSE 를 최소화하는 것입니다.

$$\|\hat{\mathbf{v}}_{\theta}(\mathbf{x}_{t},{t},\mathbf{C})-\mathbf{u}_{t}\|^{2}$$

추론은 노이즈에서 시작해 학습된 속도장을 명시적 Euler 적분합니다.

$$\mathbf{x}_{t+\Delta t}\leftarrow\mathbf{x}_{t}+\Delta{t}\,\hat{\mathbf{v}}_{\theta}(\mathbf{x}_{t},{t},\mathbf{C})$$

고정 스텝 $`\Delta t=1/K`$ 로 $`t\in[0,1)`$ 를 반복합니다.

**DiT 액션 헤드.** 각 horizon 슬롯을 $`D`$ 차원 토큰으로 선형 투영하고 chunk 위치 임베딩을 더해 $`\mathbf{X}_{t}\in\mathbb{R}^{H\times D}`$ 를 만든 뒤, $`L`$ 개 DiT 블록이 (i) 액션 토큰에 대한 self-attention, (ii) 조건 토큰 $`\mathbf{C}\in\mathbb{R}^{N_{\mathrm{cond}}\times D}`$ 에 대한 cross-attention, (iii) token-wise MLP 를 residual 로 적용합니다. query 는 액션 토큰, key/value 는 $`\mathbf{C}`$ 이며 두 스트림이 차원 $`D`$ 를 공유해 중간 투영 없이 cross-attention 합니다. 시간 조건화는 AdaLN-Zero 로 주어집니다.

$$\mathrm{AdaLN}(\mathbf{Y};\mathbf{\beta},\mathbf{\gamma})=\mathrm{LN}(\mathbf{Y})\odot(1+\mathbf{\gamma})+\mathbf{\beta}$$

블록별 MLP 가 self-attention·cross-attention·MLP 각각의 $`(\mathbf{\beta},\mathbf{\gamma},g)`$ 를 산출하고, 각 residual 갱신은 $`\mathbf{Y}\leftarrow\mathbf{Y}+g\,f(\mathrm{AdaLN}(\mathbf{Y};\mathbf{\beta},\mathbf{\gamma}))`$ 로 게이팅됩니다. AdaLN 투영과 최종 출력 헤드를 0으로 초기화해 항등사상 근처에서 시작합니다.

### 학습 셋업

- **하드웨어** — 7-DoF Franka Panda + Robotis RH-P12-RN 그리퍼. 손목 장착 Intel RealSense D435, 그리퍼 각 손가락에 GelSight Mini 와 Evetac. Cartesian impedance controller 로 구동.
- **데이터** — Spacemouse 텔레오퍼레이션으로 30개 전문가 시연 수집. 제어 주파수 15 Hz, 센서 프레임은 0.06 s 윈도우에서 균일 샘플링하여 관측 스텝당 센서 히스토리 구성.
- **co-training(§3.3)** — 각 학습 배치의 절반은 Evetac 관측 포함, 나머지 절반은 미포함으로 구성. 고주파 Evetac 동역학이 융합 망의 표현 공간을 형성하되, 모델은 Evetac 없이도 정확한 액션을 생성하도록 강제되어 visual-tactile 특징이 누락 특징을 잠재적으로 보상하도록 규제됩니다. 배포 시 Evetac 인코더는 완전히 제거됩니다.
- **주요 하이퍼파라미터(Table 6)** — batch 64, $`H=16`$, $`n_{\mathrm{act}}`$ 1–3, $`n_{\mathrm{obs}}=4`$, $`D=256`$, DiT depth $`L=10`$, heads 8, MLP ratio 4, dropout 0, FM noise $`\sigma=0`$, $`K=10`$, policy lr $`1\times 10^{-4}`$, encoder lr $`1\times 10^{-5}`$, weight decay $`1\times 10^{-6}`$, Adam betas $`(0.95,0.999)`$, cosine schedule, gradient clipping 1.0, action 정규화 minmax.

---

## 📊 실험 설정과 결과

5개 접촉 집약적 과제(Gear Assembly, Board Wiping, Lamp Installation, Key in Lock, Lightbulb Connection)에서 평가합니다. 베이스라인은 멀티모달 촉각 트랜스포머 Sparsh-X 와 vision-only 변형 ViT·ViT-CNN 입니다. 모든 모델은 동일한 DiT 플로우 매칭 헤드·동일 시연 데이터를 쓰고 센서 인코딩만 다릅니다. 정책마다 20회 평가하여 성공률을 보고합니다.

![Figure 4 — 과제별 성공률 비교](https://arxiv.org/html/2606.06281/x1.png)

> "Figure 4: MiTaS outperformes the multimodal baseline Sparsh-X and two vision-only ViT-baselines in every task. Vision-only models failed, due to occlusion and complex contact dynamics, highlighting the need for tactile sensing in contact-rich manipulation." (§4.2)
(한글 해설 — MiTaS 가 전(全) 과제에서 멀티모달·vision-only 베이스라인을 앞서며, vision-only 는 가림·복잡 접촉 동역학으로 실패함을 보입니다.)

> "MiTaS, with an average success rate of 80%, is able to solve all tasks consistently, while Sparsh-X (avg. 54%), with the same sensor setting, is not reliable in every task." (§4.2)
(한글 해설 — 동일 센서 설정(V+G+E)에서 MiTaS 80% vs Sparsh-X 54% — 아키텍처 차이만으로 26%p 격차입니다.)

**Table 1 — Policy success rate (%) (§4.2).** 열은 modality 조합(V=Vision, G=GelSight, E=Evetac).

| Task | MiTaS V+G+E | MiTaS V+G | MiTaS V+E | Sparsh-X V+G+E | Sparsh-X V+G |
|---|---|---|---|---|---|
| Gear | 90% | 45% | 0% | 50% | 25% |
| Board | 90% | 70% | 80% | 85% | 50% |
| Lamp | 80% | 65% | 65% | 70% | 55% |
| Key | 75% | 55% | 0% | 10% | 20% |
| Lightbulb | 65% | 20% | 40% | 55% | 15% |
| Avg. | 80% | 51% | 37% | 54% | 33% |

vision-only 변형은 ViT 31%, ViT-CNN 26% 로(Figure 4 본문), Key in Lock·Lightbulb 를 풀지 못합니다. Evetac 단독(V+E)은 특정 과제에서 유용하나 in-hand 물체 위치가 필요한 과제(Gear·Key 0%)에서 완전히 실패합니다.

> "Multi-resolution tactile feedback paired with suitable encoding enables a high success rate with only 30 demonstrations in these complex contact-rich manipulation tasks." (§4.2)
(한글 해설 — 단 30개 시연으로 고성공률을 달성, 데이터 효율을 강조합니다.)

**Table 2 — Co-training ablation at V+G (success in %) (§4.2).**

| Task | MiTaS V+G | MiTaS +Co-train | Δ | Sparsh-X V+G | Sparsh-X +Co-train | Δ |
|---|---|---|---|---|---|---|
| Gear | 45% | 55% | +10 | 25% | 15% | −10 |
| Board | 70% | 85% | +15 | 50% | 85% | +35 |
| Lamp | 65% | 60% | −5 | 55% | 70% | +15 |
| Key | 55% | 20% | −35 | 20% | 5% | −15 |
| Lightbulb | 20% | 45% | +25 | 15% | 10% | −5 |
| Avg. | 51% | 53% | +2 | 33% | 37% | +4 |

> "It boosted MiTaS performance in 3/5 tasks, while being helpful in 2/5 tasks for Sparsh-X." (§4.2)
(한글 해설 — co-training 은 만능이 아니며, Key in Lock 처럼 GelSight 의 in-hand 국소화 특징을 교란하는 과제에서는 성능을 떨어뜨립니다(−35).)

**파라미터·추론(Table 4, §A.2).** 정책 헤드는 모든 변형이 공유(13,701,508 params). MiTaS V+G+E 는 perception 10,764,824 / total 24,466,332 params, 644 tok/obs, RTX 4080·10 적분 스텝 기준 43.5 ms(180.5 Hz). Evetac 을 뺀 co-trained V+G 는 36.1 ms(230.1 Hz).

**어텐션 분석(§4.3).**

> "Figure 5 shows how the policy attends on vision during reaching, on Gelsight for the prolonged screwing motion and on all sensors during insertion." (§4.3)
(한글 해설 — 실행 액션 토큰의 cross-attention 을 시각화하면 과제 단계별로 센서 중요도가 이동함 — reaching 은 vision, 나사 체결은 GelSight, 삽입은 전 센서 — 이 multi-resolution 가설을 검증합니다.)

---

## ⚖️ 한계

- **단일 센서 쌍에 국한** — frame 기반 GelSight 와 event 기반 Evetac 한 쌍에만 융합을 검증했습니다. 다른 이종 센서 쌍·대체 촉각 기술로의 확장성은 추가 연구가 필요합니다.
- **텔레오퍼레이션 의존** — Spacemouse 기반 데이터 수집이 확장성을 근본적으로 제약합니다. human video·markerless hand tracking 등 대안 시연 소스가 향후 과제입니다.
- **4-DoF 액션 제약** — 정책이 선택적으로 4-DoF(병진 3 + yaw)로 제한됩니다. 풀 6-DoF 로 확장하려면 현재 관측에서 제외된 proprioceptive 로봇 상태를 통합해야 할 가능성이 높습니다.
- **반응성 상한** — 제어 루프의 15 Hz 재계획 주파수가 프레임워크 반응성의 상한을 둡니다. 고반응 정책 아키텍처와의 결합이 향후 방향입니다.
- **공개 평가 규모** — 과제당 20회 평가, 30개 시연으로 절대 표본이 작아 성공률 분산이 클 수 있습니다(저자 미명시, 명백한 갭).

---

## ♻️ 재현성

- **프로젝트 페이지** — http://mitas-touch.github.io 가 공개되어 있습니다(논문 본문 기준).
- **코드/데이터** — 본문에는 코드·데이터셋의 명시적 공개 라이선스/저장소 언급이 없습니다(기여 (3)에서 데이터셋을 소개하나 배포 경로는 본문 미명시). 논문 라이선스는 CC BY 4.0.
- **하드웨어** — Franka Panda 7-DoF + Robotis RH-P12-RN 그리퍼 + GelSight Mini + Evetac + RealSense D435 로 명시되어 재구성 가능. 다만 Evetac 은 비교적 특수 센서로 조달 장벽이 있습니다.
- **하이퍼파라미터** — Table 3(컨트롤러)·Table 6(학습)에 상세 수치 공개로 재현 정보가 풍부합니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P2 (Structured Input-Modality Binding) — primary.** 이 논문의 본체는 입력 modality 결합입니다. modality별 CNN stem + modality 임베딩 $`\mathbf{e}_{s(i)}`$ 분리는 D11(visuotactile/proprio-tactile 인코더 후보)·D8(구조적 토큰 구성)에, self-attention 융합 트랜스포머는 D10(hand-level aggregation encoder, v1=self-attention)에, cross-attention 조건화는 D12(multi-camera pre-fusion, v1=cross-attention fuser)에 직접 대응합니다. "swappable sensor head + common token format"(D11 비협상 조건)과도 정합 — 각 센서를 공통 토큰 포맷($`D=256`$)으로 통일합니다.
- **P1 (Heterogeneous Body/Hand Action Expert) — secondary.** 플로우 매칭 DiT 액션 헤드·action chunking·AdaLN-Zero 시간 조건화는 π0 계열(D7 backbone) 액션 전문가와 같은 계보입니다. 다만 body/hand 분할(D1)은 없고 단일 정책이므로 연결은 약합니다.
- **P3/P4 — 무관.** RL 요소(P3)·VLM backbone 및 prior 보존(P4)은 이 논문에 등장하지 않습니다. 처음부터(from scratch) imitation 학습이며 사전학습 VLM 을 쓰지 않습니다.
- **Identity 긴장/지지** — Identity 의 "structured finger/palm proprio-tactile 입력" 주장을 부분 지지하나, MiTaS 는 modality별(센서 종류별) 결합이지 **per-finger 결합은 아닙니다**. 즉 토큰을 "어느 센서"로 구분(modality 임베딩)할 뿐, "어느 손가락"으로 귀속(finger attribution)하지는 않습니다 — P2 차별화 가설의 절반만 구현.
- **경쟁자 함의(P2 §7)** — Sparsh-X 를 직접 베이스라인으로 두고 이김(80% vs 54%). Sparsh 는 P2 핀(arXiv:2410.24090)이자 경쟁/친족 모니터링 대상으로, "tactile foundation model" 대비 단순 멀티모달 트랜스포머 융합이 과제 특화 학습에서 더 나을 수 있다는 신호입니다.

---

## ✨ 핀 논문 대비 델타

- **vs Sparsh (P2 핀, arXiv:2410.24090) / Sparsh-X** — Sparsh 는 대규모 self-supervised 촉각 foundation 표현입니다. MiTaS 는 foundation 사전학습 없이, modality별 CNN stem + 단순 self-attention 융합을 **정책 목적과 end-to-end** 학습하여 동일 센서 설정에서 Sparsh-X(attention-bottleneck 융합)를 26%p 앞섭니다. 즉 "융합 메커니즘으로 bottleneck 대신 full self/cross-attention", "사전학습 대신 task-end-to-end"가 진정한 델타입니다.
- **vs ForceFlow (P2 핀, arXiv:2605.11048)** — 둘 다 접촉/촉각으로 플로우 매칭 정책을 조건화하나, ForceFlow 는 force/contact 구동에 비대칭 멀티모달 융합을 씁니다. MiTaS 의 새로움은 **시간 해상도가 다른 두 촉각 센서**(25 Hz GelSight + 200 Hz Evetac)를 명시적으로 결합하고, **train-only privileged 센서(Evetac)** 라는 비대칭 co-training 으로 추론 시 센서 수를 줄이는 점입니다.
- **vs ViTacFormer (P2 핀, arXiv:2506.15953)** — cross-attention visuotactile 융합이라는 공통점은 있으나, MiTaS 는 토큰을 per-finger 가 아닌 per-modality 로 결합하고, 이벤트 기반 고시간해상도 modality 를 추가했다는 점이 다릅니다.
- **새로움의 핵심** — (1) 고전 vision 기반 + event 기반 촉각의 첫 결합, (2) train-only 고주파 센서 co-training 으로 배포 비용 절감.

---

## ⚙️ 의사결정 함의

- **D11(visuotactile 인코더) 후보로 "modality 임베딩 + CNN stem + 공통 토큰 포맷" 패턴 채택 검토** — MiTaS 의 `modality embedding e_{s(i)}` 는 우리의 "swappable sensor head + common token format" 비협상 조건을 구현하는 구체 레시피입니다. 센서 교체 시 stem + modality 임베딩만 갈아끼우면 됩니다. 단, 우리는 여기에 **per-finger 위치 귀속**(D8/D9 topology-aware)을 추가해야 하며 MiTaS 의 격자 위치 임베딩 $`\mathbf{p}_{g(i)}`$ 은 손가락 정체성이 아닌 센서 내 공간 좌표만 인코딩합니다.
- **co-training 을 D11 보조 학습 신호로 채택 검토** — 고주파/특수 센서(예: 우리 스택의 Deform Map 고주파 채널)를 **학습 시에만** 절반 배치에 주입하고 배포 시 제거하는 비대칭 co-training 은, 추론 비용을 늘리지 않고 표현을 규제하는 저비용 옵션입니다. 구체적으로 `co_train_ratio=0.5`(배치 절반), `inference_sensors ⊂ train_sensors` 라는 config 키로 도입 가능합니다.
- **융합 메커니즘 선택의 증거** — D10(v1=self-attention)·D12(v1=cross-attention) 선택을 지지합니다. attention-bottleneck(Sparsh-X)보다 full self/cross-attention 융합이 26%p 우위라는 직접 비교는 우리 v1 기본값을 강화합니다.
- **주의해야 할 함의** — MiTaS 는 proprioception·절대 위치를 입력에서 제외했습니다. 우리 Identity 는 finger joint state 를 핵심 입력으로 두므로(D8 per-finger proprio-tactile), 이 논문의 "센서만으로 delta 추론" 셋업을 그대로 가져오면 **우리 가정과 충돌**합니다 — 채택 시 proprio 토큰을 추가해야 합니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **per-modality ≠ per-finger 결합의 전이 실패** — MiTaS 의 modality 임베딩은 센서 종류(vision/gelsight/evetac)만 구분합니다. 우리의 ~10 손가락 + 2 손바닥 토큰 결합(D8)은 "어느 손가락"이 핵심인데, MiTaS 격자 위치 임베딩을 손가락 정체성으로 곧바로 치환하면 의미가 어긋납니다. **가장 싼 sanity check** — MiTaS 토큰 구성에서 `e_{s(i)}` 를 finger-id 임베딩으로 바꾼 소규모 ablation 으로 contact attribution 이 유지되는지 먼저 확인.
- **30 demo·20 trial 통계 신뢰성** — 5% 단위 성공률(20회 중 N회)은 분산이 큽니다. co-training 의 −35(Key) 같은 큰 변동이 통계적으로 유의한지, 우리 스택에서 재현되는지 표본을 늘려 확인 필요.
- **Evetac 의존 신호의 하드웨어 특이성** — 200 Hz event 센서의 이득(Board Wiping 등 동적 과제)이 우리의 Deform Map(vision 기반 ~30 Hz)에는 고주파 채널이 없어 전이되지 않을 수 있습니다. co-training 이득의 원천이 "고주파 그 자체"인지 "추가 modality"인지부터 분리 검증.
- **로봇 상태 미입력 셋업의 비호환** — 우리는 proprio 를 필수 입력으로 가정하므로, MiTaS 의 "no robot state" 결과(특히 delta-only 액션 표현)가 proprio 포함 시에도 성립하는지 확인이 선결입니다.

---

## 💡 컨텍스트 제안

- **P2 §5 Tracked Literature 핀 교체 후보** — MiTaS([arXiv:2606.06281](https://arxiv.org/abs/2606.06281))는 (a) 이종 시간 해상도 촉각 융합의 첫 사례이고 (b) Sparsh-X 직접 우위라는 결정적 비교를 제공합니다. 현재 핀 중 역할이 겹치는 Touch Dreaming([arXiv:2604.13015], latent tactile prediction, D11 deferred) 자리에 신규 핀으로 승격하는 안을 사람에게 제안합니다(하드 캡 8 유지).
- **P2 §7 경쟁자 모니터링 갱신 후보** — Sparsh 행에 "Sparsh-X(멀티모달 확장)가 MiTaS 에 26%p 열세" 트리거를 추가하면, foundation-vs-task-end-to-end 논쟁의 추적 포인트가 됩니다.
- **신규 deferred 후보** — "train-only privileged 센서 co-training"을 D11 보조 학습 신호의 deferred 후보로 등록 제안(우리 Deform Map 고주파 채널·외부 force 센서에 적용 가능). 본 제안은 사람 검토용이며 context 파일은 수정하지 않았습니다.

---
