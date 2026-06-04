# Paper Analysis — Modular Sensory Stream for Integrating Physical Feedback in Vision-Language-Action Models

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Modular Sensory Stream for Integrating Physical Feedback in Vision-Language-Action Models |
| 저자 | Jimin Lee, Huiwon Jang, Myungkyu Koo, Jungwoo Park, Jinwoo Shin |
| 링크 | [arXiv:2604.23272](https://arxiv.org/abs/2604.23272) |
| 발행일 / 버전 | 2026-04-25 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-05-26 |
| 관련 Pillar | P2, P1, P4 |
| 태그 | force, flow-matching, vla-arch |

---

## 🧭 한 줄 요약 (TL;DR)

MoSS 는 사전학습 VLA 의 액션 전문가 옆에 모달리티별 디커플 스트림을 두고, 액션 스트림과는 오직 조인트 크로스-모달 셀프 어텐션 한 통로로만 맞물립니다. 두 단계 학습(Stage 1 사전학습 파라미터 동결 + Stage 2 공동 미세조정)에 미래 물리 신호 예측 보조 손실을 얹어, 촉각·토크 같은 이종 물리 피드백을 누적 가산으로 흡수합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 사전학습 VLA 에 촉각·토크 같은 이종 물리 센서를 어떻게 동시에 얹어 누적 성능 향상을 끌어낼 것인가. 저자들은 "하나의 모달리티만"이 아니라 "여러 모달리티의 결합" 자체가 골자라고 못박습니다.
- **기존 접근의 한계** — Tactile-VLA, ForceVLA, TA-VLA 같은 선행 연구는 한 신호만 다룹니다. 두 모달리티를 한꺼번에 넣으면 성능이 오히려 떨어지는 사례를 §4·표 1·표 6 이 정량적으로 짚습니다.
- **MoSS 의 가설** — 모달리티마다 디커플된 별도 스트림으로 처리하되, 조인트 크로스-모달 셀프 어텐션 한 통로로만 정보를 교환하고 학습은 두 단계로 쪼갭니다. 그러면 VLA 의 사전학습 prior 를 보존한 채 이종 신호가 서로를 보완하며 맞물립니다.
- **왜 지금 중요한가** — 접촉 집약 조작에서는 시각·언어만으로 미세한 힘 제어가 어렵습니다. 이 인식이 굳어지는 시점에, 다중 물리 모달리티를 동시에 받는 첫 통합 VLA 적응 프레임워크가 올라옵니다.

---

## 🧩 핵심 기여

- **MoSS (Modular Sensory Stream)** — 사전학습 VLA 의 액션 전문가 모듈 옆에 모달리티별로 독립된 스트림 $`\mathcal{A}_{\phi_i}`$ 를 두고, 조인트 크로스-모달 셀프 어텐션 층으로만 정보를 흘려 액션·물리 신호를 양방향으로 추론합니다. 저자들은 이 설계를 모달리티-불가지론적(modality-agnostic)이라고 표기합니다.
- **두 단계 학습 전략** — Stage 1 에서는 사전학습 액션 전문가 $`\mathcal{A}_{\psi}`$ 를 동결한 채 새 모달리티 스트림만 학습해 표현을 정렬합니다. Stage 2 에서 전체를 풀어 공동 미세조정합니다. 무작위 초기화된 스트림과 사전학습 스트림 사이의 그래디언트 간섭을 막아 주는 구실을 합니다.
- **미래 물리 신호 예측 보조 손실** — 각 물리 스트림이 과거 윈도우 $`{\mathbf{m}}_{t-H+1:t}^{(i)}`$ 를 입력으로 받아 미래 신호 $`{\mathbf{m}}_{t+1:t+H}^{(i)}`$ 를 회귀하는 보조 손실 $`\mathcal{L}_{\mathrm{phy}}`$ 를 둡니다. 접촉 동역학을 모델 내부로 끌어들이는 자기지도 신호입니다.
- **실증 결과** — 4 종 접촉 집약 실세계 과제(Unstack Cup, PnP Egg, Board Erase, Plug Insertion)에서 π0 와 GR00T N1.5 양쪽 백본 위로 평균 +18.9%p / +25.1%p 의 성공률 향상을 얻습니다. 다른 베이스라인이 두 신호를 합치면 떨어질 때, MoSS 만 +6.3%p 더 오릅니다.
- **추론 비용 분석** — 촉각+토크 두 모달리티를 동시에 받아도 GR00T N1.5 대비 추론 지연이 1.11× 에 그칩니다. 표 3 이 그 수치를 듭니다.

---

## 🔑 기술 키워드

- **VLA (Vision-Language-Action model)** — 시각·언어 입력에서 곧장 로봇 액션을 만드는 정책. MoSS 의 실험은 디퓨전 기반 VLA(π0, GR00T N1.5) 두 종 위에서 이뤄집니다.
- **액션 전문가 (action expert)** — VLM 백본의 표현을 받아 액션 청크를 예측하는 트랜스포머 헤드. MoSS 는 이 모듈을 건드리지 않고 옆에 스트림만 덧붙이는 비침습적 확장을 노립니다.
- **플로우 매칭 (flow matching)** — 노이즈 액션에서 원본 액션을 가리키는 벡터 필드를 회귀하는 조건부 생성 목적식. 액션 손실 $`\mathcal{L}_{\mathrm{act}}`$ 의 형태가 여기서 옵니다.
- **Joint cross-modal self-attention** — 액션 스트림과 각 물리 스트림의 Q·K·V 를 한데 이어 붙여 단일 스케일드 닷프로덕트 어텐션을 계산하는 양방향 결합 층. 모달리티 사이 정보 교환이 일어나는 유일한 통로입니다.
- **Decoupled modality streams** — 모달리티마다 액션 전문가 구조를 그대로 복제해 무작위 초기화하고, 어텐션 외 경로는 끊어 둔 병렬 스트림. 그래디언트 간섭을 가로막는 분리벽 노릇을 합니다.
- **AnySkin** — 비전 기반 fingertip 촉각 센서. 한 패드당 5 개 센싱 유닛이 각각 3축 힘을 재 15 차원을 만듭니다. 두 손가락이면 30 차원 관측치가 됩니다.
- **Joint torque sensing** — 로봇 팔 각 관절의 토크를 읽어 외력·접촉 상태를 추정하는 신호. Franka FR3 의 7 차원 토크 벡터가 그대로 입력으로 들어갑니다.
- **Future feedback prediction** — 미래 시각이 아닌 미래 *물리* 신호를 예측하게 만드는 보조 자기지도 과제. 접촉 동역학을 표현 안으로 끌어들이는 구실을 합니다.
- **Stage-wise training (Physical alignment → Joint fine-tuning)** — 신규 모달리티 도입 시 두 단계로 쪼개 학습하는 어댑터 적응 전략. 사전학습 prior 보존과 신규 표현 학습 사이의 trade-off 를 두 시간 구간에 나눠 담습니다.
- **Modality-agnostic adapter** — 한 프레임워크로 촉각·토크·기타 물리 신호를 같은 방식으로 끼우는 설계 원칙. 새 모달리티가 들어올 때 스트림 한 줄을 더하는 것으로 끝납니다.

---

## 🔬 방법론

### 직관

> "We propose MoSS, a modular sensory stream framework that adapts VLAs to leverage multiple sensory signals for action prediction." (§Abstract)
(여러 물리 신호를 *동시에* 받게 만드는 어댑터를 단일 프레임워크로 본 것이 출발점입니다. 모달리티별 특화 회로를 새로 만드는 대신, 같은 골격을 모달리티마다 복제하고 어텐션 한 곳에서만 섞습니다.)

> "This bidirectional design enables cross-modal reasoning (e.g., modulating actions based on tactile feedback or unexpected torques), while keeping other network components decoupled to prevent gradient interference." (§3.1)
(액션·물리 양방향 추론이 이 설계의 골자입니다. 어텐션 외 경로를 끊는 결정은 무작위 초기화된 새 스트림이 사전학습 액션 전문가를 망가뜨리지 못하게 막아 주는 안전핀입니다.)

![Figure 2 — MoSS architecture overview](https://arxiv.org/html/2604.23272/x2.png)

> "Figure 2: Overview of the proposed approach. We propose MoSS, a Modular Sensory Stream framework that integrates multiple physical sensory signals into VLAs. Building on a pretrained VLA, MoSS introduces a multimodal stream architecture that processes newly added physical signals (e.g., tactile and torque) in parallel. This figure illustrates a representative instantiation of MoSS with tactile and torque modalities, while the framework itself remains agnostic to the specific choice of physical signals. To ensure stable incorporation of these modality streams, we employ a two-stage training scheme and a future feedback prediction objective to further exploit physical signals." (§3)
(아키텍처·두 단계 학습·미래 예측 보조 손실이 한 장에 압축돼 있습니다. 저자들도 본문에서 같은 순서로 디테일을 풀어 갑니다.)

### 아키텍처

기본 디퓨전 기반 VLA 는 작업 지시 $`\ell`$ 와 시각 관측 $`{\mathbf{I}}_{t}`$ 를 VLM 백본 $`\mathcal{F}_{\theta}`$ 에 넣어 시각-언어 표현 $`{\mathbf{h}}_{t}`$ 를 만들고, 액션 전문가 $`\mathcal{A}_{\psi}`$ 가 고유수용감각 $`{\mathbf{s}}_{t}`$ 와 함께 길이 $`H`$ 액션 청크 $`{\mathbf{A}}_{t}=[{\mathbf{a}}_{t},{\mathbf{a}}_{t+1},\cdots,{\mathbf{a}}_{t+H-1}]`$ 를 병렬로 예측합니다. 조건부 플로우 매칭 손실은 다음과 같습니다.

$$\mathcal{L}=\mathbb{E}_{\tau,\epsilon}\left[\|({\mathbf{A}}_{t}-\epsilon)-\mathcal{A}_{\psi}({\mathbf{A}}_{t}^{\tau},{\mathbf{s}}_{t}~|~{\mathbf{h}}_{t})\|^{2}\right]$$

여기서 노이즈가 섞인 액션 청크는 $`{\mathbf{A}}_{t}^{\tau}=\tau{\mathbf{A}}_{t}+(1-\tau)\epsilon`$, 노이즈 $`\epsilon\sim\mathcal{N}({\mathbf{0}},{\mathbf{I}})`$, 시점 $`\tau\in[0,1]`$ 입니다.

MoSS 는 시점 $`t`$ 의 물리 센서 집합 $`{\mathbf{M}}=\{{\mathbf{m}}_{t}^{(i)}\in\mathbb{R}^{d_{i}}\}_{i=1}^{N}`$ 을 받아 모달리티 $`i`$ 마다 별도 스트림 $`\mathcal{A}_{\phi_{i}}`$ 를 둡니다. 액션 스트림과 물리 스트림은 다음과 같이 정의됩니다.

$$\begin{aligned} &\text{Action stream}:&&\mathcal{A}_{\psi}({\mathbf{A}}_{t}^{\tau},{\mathbf{s}}_{t}~|~\{{\mathbf{h}}_{t}\}\cup{\mathbf{M}})\\ &\text{Physical stream }i:&&\mathcal{A}_{\phi_{i}}({\mathbf{m}}_{t}^{(i)}~|~\{{\mathbf{h}}_{t},{\mathbf{A}}_{t}^{\tau},{\mathbf{s}}_{t}\}\cup{\mathbf{M}}\backslash\{{\mathbf{m}}_{t}^{(i)}\})\end{aligned}$$

> "In practice, we construct each new sensory stream $`\mathcal{A}_{\phi_{i}}`$ by mirroring the architecture of the original action expert module $`\mathcal{A}_{\psi}`$ and randomly initializing its parameters. We then replace the self-attention layers in each stream with joint cross-modal self-attention layers." (§3.1)
(같은 골격을 모달리티마다 복제하되, 셀프 어텐션을 조인트 크로스-모달 셀프 어텐션으로 갈아 끼웁니다. 이 한 줄이 결합의 전부입니다.)

각 층에서 액션 스트림($`i=0`$)을 포함한 모든 스트림의 $`\{{\mathbf{Q}}_{i},{\mathbf{K}}_{i},{\mathbf{V}}_{i}\}_{i=0}^{N}`$ 를 이어 붙여 공유 스케일드 닷프로덕트 어텐션을 계산합니다. 이 통로만이 모달리티 사이의 결합 지점입니다. 나머지 경로는 끊긴 채로 둡니다.

### 학습 목표 / 손실

예측 액션 $`\hat{{\mathbf{A}}}_{t}=\mathcal{A}_{\psi}({\mathbf{A}}_{t}^{\tau},{\mathbf{s}}_{t}~|~\{{\mathbf{h}}_{t}\}\cup{\mathbf{M}})`$ 에 대한 액션 플로우 매칭 손실은 다음과 같습니다.

$$\mathcal{L}_{\mathrm{act}}=\mathbb{E}_{\tau,\epsilon}\left[\left\|({\mathbf{A}}_{t}-\epsilon)-\hat{{\mathbf{A}}}_{t}\right\|^{2}\right]$$

각 모달리티 스트림은 과거 윈도우 $`{\mathbf{m}}_{t-H+1:t}^{(i)}`$ 를 받아 같은 호라이즌의 미래 신호 $`{\mathbf{m}}_{t+1:t+H}^{(i)}`$ 를 예측하도록 학습됩니다. 표기를 간단히 하려고 저자들은 입력 윈도우를 $`{\mathbf{m}}_{t}^{(i)}`$ 로 줄여 씁니다.

$$\mathcal{L}_{\mathrm{phy}}=\sum_{i=1}^{N}\mathbb{E}_{\tau,\epsilon_{i}}\left[\left\|({\mathbf{m}}_{t+1:t+H}^{(i)}-\epsilon_{i})-\hat{{\mathbf{m}}}_{t+1:t+H}^{(i)}\right\|^{2}\right]$$

전체 목적식은 두 손실의 가중 합입니다.

$$\mathcal{L}=\mathcal{L}_{\mathrm{act}}+\lambda_{\mathrm{phy}}\mathcal{L}_{\mathrm{phy}}$$

> "As described in Section 3.2, in Stage 1, we optimize only $`\mathcal{L}_{\mathrm{phy}}`$ while freezing the action expert. In Stage 2, we jointly optimize the full objective with respect to all parameters." (§3.3)
(두 단계에서 손실 사용이 달라지는 데가 골자입니다. Stage 1 은 새 스트림이 물리 신호의 동역학을 먼저 익히는 사전정렬 구간입니다. Stage 2 에서야 액션과 물리가 함께 그래디언트를 받습니다.)

저자들은 $`\lambda_{\mathrm{phy}}=0.1`$ 을 디폴트로 씁니다. 표 5 의 민감도 분석에서는 $`\lambda_{\mathrm{phy}}\in\{0.1,0.5\}`$ 구간 성능이 견고하고, $`\lambda_{\mathrm{phy}}=1.0`$ 에서는 액션 학습 신호가 묻혀 떨어진다는 수치를 듭니다.

### 학습 셋업

- **하드웨어** — 7-DoF Franka Research 3 팔 + Robotiq 2F-85 그리퍼, DROID 셋업을 따릅니다. 그리퍼 양쪽 손가락에 각각 AnySkin 촉각 센서를 부착해 한 손가락당 15 차원, 두 손가락 합쳐 30 차원 촉각 벡터를 얻습니다. 토크는 팔 7 관절에서 뉴턴-미터 단위로 7 차원입니다.
- **시각 입력** — 3자 카메라(third-person) + 손목 카메라, 둘 다 720×1280 해상도에서 224×224 로 리사이즈한 RGB 입니다. 깊이는 쓰지 않습니다.
- **액션 모드** — absolute joint position. 액션 청크 길이는 표에 적혀 있지 않습니다(원문 표기로는 $`H`$).
- **데이터** — 4 과제 합쳐 단일 consolidated 데이터셋, 과제별 100 개 시연입니다. 작업 지시(예: "Pick up the top red cup from the stack and place it next to the blue cup.")는 고정된 자연어 문장입니다.
- **베이스 VLA** — π0 는 full fine-tuning, GR00T N1.5 는 VLM 백본을 동결해 액션 전문가 측만 학습합니다. 단, Tactile-VLA 비교에서는 GR00T 도 VLM 까지 FT 합니다(촉각 토큰이 VLM 으로 곧장 들어가야 해서입니다).
- **옵티마이저·스케줄** — 표 4 verbatim:

| 항목 | GR00T N1.5 + MoSS | π0 + MoSS |
|------|-------------------|-----------|
| Optimizer | AdamW | AdamW |
| `β₁, β₂` | 0.95, 0.999 | 0.9, 0.95 |
| Weight decay | 1e-5 | 1e-10 |
| Learning rate | 1e-4 | 2.5e-5 |
| Scheduler | Cosine decay | Cosine decay |
| Warmup iterations | 3,000 | 1,000 |
| Batch size | 16 | 16 |
| Stage 1 iterations | 20,000 | 10,000 |
| Stage 2 iterations | 40,000 | 20,000 |

GR00T 는 총 60K, π0 는 총 30K 스텝이며, 최종 체크포인트로 평가합니다. 물리 손실 계수는 $`\lambda_{\mathrm{phy}}=0.1`$ 로 고정합니다.

---

## 📊 실험 설정과 결과

평가 과제는 네 종이며 모두 시각 단서만으로는 모호한 접촉 집약 조작입니다.

- **Unstack Cup** — 3 개 컵 더미에서 맨 위 빨간 컵 한 개만 꺼냅니다. 잡는 힘을 잘못 조절하면 여러 컵이 같이 들립니다. 크기 변형(대형·소형) 24 trial.
- **PnP Egg** — 깨뜨리지 않고 계란을 들어 그릇에 넣습니다. 위치 변형 24 trial.
- **Board Erase** — 화이트보드의 표시 영역을 지웁니다. 보드 높이 3 단계 × 지우개 색상 × 마커 색상 조합 24 trial.
- **Plug Insertion** — 손목 카메라 시야에서 종종 가려지는 콘센트에 플러그를 꽂습니다. 차저 3색 × 8 trial = 24 trial.

각 모델은 24 trial 로 측정한 성공률(%)을 내놓습니다. 표 1 의 주요 수치만 옮깁니다.

| Method | Tactile | Torque | Unstack Cup | PnP Egg | Board Erase | Plug Insertion | Avg. |
|---|---|---|---|---|---|---|---|
| GR00T N1.5 | ✗ | ✗ | 16.7 | 45.8 | 20.8 | 0.0 | 20.8 ± 4.1 |
| + Tactile-VLA | ✓ | ✗ | 29.2 | 45.8 | 33.3 | 12.5 | 30.2 ± 4.7 |
| + ForceVLA | ✓ | ✗ | 37.5 | 54.2 | 33.3 | 12.5 | 34.4 ± 4.8 |
| + MoSS (ours) | ✓ | ✗ | 45.8 | 66.7 | 41.7 | 16.7 | 42.7 ± 5.0 |
| + TA-VLA | ✗ | ✓ | 29.2 | 45.8 | 37.5 | 20.8 | 33.3 ± 4.7 |
| + MoSS (ours) | ✗ | ✓ | 33.3 | 50.0 | 41.7 | 25.0 | 37.5 ± 4.9 |
| **+ MoSS (ours)** | **✓** | **✓** | **54.2** | **66.7** | **50.0** | **25.0** | **49.0 ± 5.1** |
| π0 | ✗ | ✗ | 12.5 | 50.0 | 29.2 | 16.7 | 26.1 ± 4.5 |
| + Tactile-VLA | ✓ | ✗ | 16.7 | 50.0 | 37.5 | 12.5 | 29.2 ± 4.6 |
| + ForceVLA | ✓ | ✗ | 25.0 | 62.5 | 50.0 | 16.7 | 38.6 ± 5.0 |
| + MoSS (ours) | ✓ | ✗ | 29.2 | 62.5 | 41.7 | 20.8 | 38.6 ± 5.0 |
| + TA-VLA | ✗ | ✓ | 16.7 | 58.3 | 41.7 | 20.8 | 34.4 ± 4.8 |
| + MoSS (ours) | ✗ | ✓ | 20.8 | 62.5 | 54.2 | 29.2 | 41.7 ± 5.0 |
| **+ MoSS (ours)** | **✓** | **✓** | **29.2** | **66.7** | **58.3** | **29.2** | **45.9 ± 5.1** |

> "For example, for GR00T N1.5, we achieve an average improvement of 28.2% over the base model, with particularly strong gains on Unstack Cup (+37.5%) and Board Erase (+29.2%)." (§4.2, Table 1)
(GR00T 베이스 대비 평균 +28.2%p 향상이라는 수치는 두 모달리티(촉각+토크)를 다 켰을 때입니다. 한 모달리티만 켜도 베이스라인을 일관되게 추월합니다.)

> "Tactile-VLA, ForceVLA, and TA-VLA often degrade when an additional modality is introduced (e.g., Tactile-VLA drops from 30.2% to 20.9% when both tactile and torque are provided), whereas MoSS consistently improves as each new modality is added." (§4.2/§C.1, Table 6)
(표 6 은 결국 이 한 줄로 압축됩니다. 두 모달리티를 합치면 선행 연구는 -6 ~ -12%p 떨어지지만 MoSS 만 +6.3%p 더 올라갑니다.)

![Figure 4 — Example rollouts of real-world tasks](https://arxiv.org/html/2604.23272/x4.png)

> "Figure 4: Example rollouts of real-world tasks. We provide example rollouts of the designed tasks that critically depend on physical feedback (e.g., tactile or torque signals). While MoSS leverages physical feedback to successfully perform the tasks, GR00T N1.5 without physical feedback often have difficulties in (a), (b) regulating grasp force, (c) maintaining appropriate pushing force for contact, and (d) probing occluded geometry." (§4.2)
(롤아웃 비교가 정성적 근거입니다. 물리 피드백이 없으면 그립 강도·접촉 압력·차폐 기하 탐색에서 어떻게 실패하는지를 네 과제에서 차례로 보여 줍니다.)

추가 표를 옮깁니다.

**표 2 — Ablation study (GR00T N1.5 + MoSS).**

| Method | Unstack Cup | PnP Egg |
|---|---|---|
| MoSS (Ours) | 54.2 | 66.7 |
| w/o decoupling streams | 33.3 | 50.0 |
| w/o two-stage training | 37.5 | 58.3 |
| w/o future prediction | 45.8 | 58.3 |

> "For example, on the Unstack Cup task, it achieves 20.9% improvements over the naïve DiT baseline." (§4.3, Table 2)
(디커플 스트림을 빼고 단일 DiT 액션 전문가 안에서 물리 신호를 함께 예측시키면 Unstack Cup 성공률이 20.9%p 떨어집니다. 가산 효과를 지탱하는 것은 결국 디커플 구조입니다.)

**표 3 — 추론 지연 (GR00T N1.5 + MoSS).**

| Method | Tactile | Torque | Latency (ms, ↓) |
|---|---|---|---|
| GR00T N1.5 | ✗ | ✗ | 21.0 (1.00×) |
| + MoSS | ✓ | ✗ | 22.4 (1.06×) |
| + MoSS | ✗ | ✓ | 21.9 (1.04×) |
| + MoSS | ✓ | ✓ | 23.4 (1.11×) |

> "When both tactile and torque modalities are incorporated, latency increases by only 2.4 ms (1.11× slower than the base model), highlighting the efficiency of MoSS." (§4.3, Table 3)
(두 모달리티 풀 셋업에서도 액션 청크당 +2.4 ms 가 전부입니다. 어댑터 비용이 거의 공짜에 가깝다는 주장입니다.)

**표 5 — $`\lambda_{\mathrm{phy}}`$ 민감도.**

| $`\lambda_{\mathrm{phy}}`$ | Unstack Cup | PnP Egg |
|---|---|---|
| 0.1 | 13 / 24 | 18 / 24 |
| 0.5 | 12 / 24 | 16 / 24 |
| 1.0 | 7 / 24 | 10 / 24 |

> "We observe that performance is relatively robust across the range $`\lambda_{\mathrm{phy}}\in\{0.1,0.5\}`$, with peak performance at $`\lambda_{\mathrm{phy}}=0.1`$." (§B.1, Table 5)
(보조 손실이 너무 크면 액션 학습이 묻힙니다. 0.1 디폴트는 안전 마진이 좁다는 신호이기도 합니다.)

---

## ⚖️ 한계

- **2지 평행 그리퍼 한정** — Robotiq 2F-85 + AnySkin 촉각만 검증했습니다. 5지 다지 손이나 사람 손 수준 자유도에서 같은 결합이 통하는지는 본문 범위 밖입니다.
- **단일 팔 단일 환경** — Franka FR3 한 대 + DROID 셋업 한 곳에서만 평가합니다. 환경·로봇 변화에 대한 견고성은 다루지 않습니다.
- **24 trial 표본** — 과제당 24 trial 은 통계적으로 얇습니다. 본문도 ±4–5%p 표준편차를 함께 적지만, 베이스라인과의 작은 차이는 노이즈일 여지가 남습니다.
- **저자가 적은 실패 모드** — 초기 접근/그래스핑이 잘못되면 물리 피드백이 무력합니다. 플러그 삽입은 초기 그립이 어긋나면 회복하지 못한다고 §B.2 에서 자인합니다.
- **모달리티 수 확장의 정량적 한계 미확인** — 2 종 결합까지만 봅니다. 3 종 이상을 동시에 얹었을 때의 스케일링 한계는 범위 밖입니다.
- **사전학습 prior 외 모달리티 누락** — 비전·언어·고유수용감각·촉각·토크 외에 청각·온도 등 다른 물리 신호에는 손대지 않습니다.

---

## ♻️ 재현성

- **코드** — 본문 abstract 끝에 "The project page is available." 만 있고, 코드 공개 여부는 본문에 적혀 있지 않습니다. 프로젝트 페이지 URL 도 본문에 적시되지 않습니다.
- **데이터** — 자체 수집 실세계 시연(과제당 100 개). 공개 여부는 본문에 적혀 있지 않습니다.
- **하드웨어** — Franka Research 3 + Robotiq 2F-85 + AnySkin(2 패드) + Zed Mini 손목 스테레오 카메라, DROID 셋업과 호환됩니다.
- **베이스 모델** — π0 (Physical Intelligence, openpi 공개) 와 GR00T N1.5 (NVIDIA) 의 공식 구현을 따릅니다.
- **하이퍼파라미터** — 표 4 에 옵티마이저·LR·이터레이션·배치·웜업이 한 줄로 적혀 있어, base VLA 만 있으면 재구성이 어렵지 않은 수준입니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

MoSS 는 PROBE 의 다음 축들과 곧장 맞물립니다.

- **P2 (Structured Input-Modality Binding)** — 가장 강한 연결입니다. "모달리티별 디커플 스트림 + 조인트 크로스-모달 어텐션" 은 PROBE 가 D8(per-finger 구조적 토큰), D10(hand-level aggregation encoder), D11(촉각 인코더 후보) 에서 가정해 온 *모달리티별 분리·통합 회로* 와 같은 계열의 설계입니다. 다만 PROBE 의 분리 축이 *손가락/모달리티/팜* 인 반면, MoSS 는 *물리 모달리티 자체* 입니다.
- **P4 (VLM Pretraining Preservation)** — Stage 1 동결·Stage 2 해제 두 단계 학습은 D19(VLM FT range) v1(전체 freeze + 액션 전문가만 학습)·D20(prior-preservation strategy) 의 action-side adapter 패턴·D21(staged training recipe) 의 단계 구조와 곧장 정렬됩니다. MoSS 는 *액션 전문가 동결* 까지 가는 추가 한 단계를 보여 줍니다.
- **P1 (Heterogeneous Body/Hand Action Expert)** — 부분 연결. "스트림 추가만으로 액션 전문가 확장" 패턴은 D7(π backbone integration / partition) 의 *repurpose vs subdivide* 와는 다른 제 3 안(*append parallel streams*) 을 내놓습니다. 한 가지 단서는 분리 축이 신체 부위가 아니라 모달리티라는 점이어서 D1(Body/Hand split form) 으로 그대로 옮겨 적용할 수는 없습니다.
- **P3 (System0) 및 P5 (Evaluation)** — 거의 무관. RL 을 쓰지 않고 4 과제 24-trial 평가에 그쳐 falsifier 와의 연결고리가 없습니다.

**Identity 긴장/지지** — Identity 의 "VLA-level 에서 곧장 tackle" 노선을 *지지* 합니다. 사전학습 VLA 옆에 어댑터 스트림만 붙여 다중 물리 모달리티를 흡수하는 패턴이 monolithic decoder 한계 비판과 정렬되기 때문입니다. 한편 쓰는 하드웨어가 2지 평행 그리퍼라는 점은 PROBE 의 anti-topic("2-finger parallel-jaw grippers only") 과 형식상 충돌합니다. 그 anti-topic 의 예외 조건("(b) structured tactile/proprio binding") 에 해당해 in-scope 로 봅니다.

**§10 경쟁자 함의** — MoSS 는 §10 의 어떤 경쟁자/유사 연구와도 그대로 대응되지 않습니다. *VLA 적응 어댑터* 라는 카테고리에서 VLA-Adapter / VLM2VLA / TwinBrainVLA 와 나란히 섭니다.

---

## ✨ 핀 논문 대비 델타

핀 논문 중 가장 가까운 비교 대상은 다음 세 편입니다.

- **AdapTac ([arXiv:2505.13982](https://arxiv.org/abs/2505.13982), P2 핀)** — "Force-guided attention + future-force aux" 라는 역할은 MoSS 의 *future physical signal prediction* 보조 손실과 사실상 같은 아이디어입니다. MoSS 의 진짜 델타는 (a) *복수* 물리 모달리티로 일반화한 점, (b) 모달리티별 *디커플 스트림* 으로 분리한 점, (c) 두 단계 학습으로 prior 보존을 더한 데 있습니다. AdapTac 의 자연스러운 확장으로 읽힙니다.
- **TwinBrainVLA ([arXiv:2601.14133](https://arxiv.org/abs/2601.14133), P1 핀)** — "frozen generalist + trainable specialist" AsyMoT 패턴은 MoSS 의 Stage 1 동결 + 신규 스트림 학습과 같은 계열입니다. 델타는 두 가지입니다. specialist 가 *신체 부위* 가 아니라 *물리 모달리티* 라는 분리 축의 차이, 그리고 어텐션이 양방향(joint cross-modal) 이라는 차이.
- **VLA-Adapter ([arXiv:2509.09372](https://arxiv.org/abs/2509.09372), P4 핀)** — "Bridge Attention action-side adapter" 가 MoSS 의 *액션 전문가 옆 병렬 스트림* 과 한 카테고리에 속합니다. MoSS 의 델타는 어댑터를 *여러 개* 병렬로 두고 그들 사이에 조인트 어텐션을 추가했다는 점, 그리고 사전학습 prior 보존을 두 단계 학습으로 못박은 데 있습니다.

핀 논문이 *없는* 진짜 새로움 — "복수의 이종 물리 모달리티를 한 VLA 안에서 누적 가산으로 결합" 이라는 결과 그 자체. 표 1·표 6 은 선행 어댑터들이 *불가능했던* 결합 가산성을 한 줄로 검증합니다.

---

## ⚙️ 의사결정 함의

MoSS 의 결과가 맞다면 PROBE 의 다음 파이프라인 항목이 바뀝니다.

- **D8 per-finger 토큰 구성 + D10 hand-level aggregation 통합 방식** — "per-finger 토큰 N+2 개 → self-attention 풀링" 대신 *각 손가락(또는 팜)* 을 별도 스트림으로 두고, 액션 전문가와 *조인트 크로스-모달 셀프 어텐션* 으로만 결합하는 변종을 ablation 후보로 추가합니다. 구체 config 키: `action_expert.cross_modal_streams.fingers=10`, `action_expert.cross_modal_streams.palm=2`, `action_expert.joint_xattn=True`. 비교 baseline 은 D10 v1 의 (B) self-attention 풀링입니다.
- **D19 / D20 / D21 staged training** — 현재 v1 은 "Stage 1: VLM 정렬 → Stage 2: VLM-freeze + Body/Hand 학습 → Stage 3/4 deferred" 입니다. MoSS 결과는 *Stage 2 내부* 를 다시 둘로 쪼개 (2a) Body/Hand 헤드 *전체* 동결 + 신규 모달리티 스트림만 학습, (2b) 전체 해제 공동 미세조정 단계를 추가하는 변형이 가치 있음을 시사합니다. config 키: `train.stage2a.iters`, `train.stage2a.freeze_action_expert=True`, `train.stage2b.iters`.
- **D11 보조 손실 — future tactile prediction** — Touch Dreaming 계열의 deferred 항목을 MoSS 식 "$`\mathcal{L}_{\mathrm{phy}}=\sum_i \|\hat{m}^{(i)}_{t+1:t+H}-m^{(i)}_{t+1:t+H}\|^2`$" 로 구체화합니다. config 키: `loss.future_phys_pred=True`, `loss.lambda_phy=0.1`. 메트릭으로는 *contact-precision (slip count)* 가 D26 의 falsifier 와 곧장 맞물립니다.
- **D7 π backbone integration — repurpose vs subdivide 제 3 안** — *append parallel streams* 라는 옵션을 D7 의 sub-reading 에 추가 등록합니다. 이는 π0 의 액션 전문가를 *손대지 않고* Body/Hand 를 둘 다 *옆에 새로 붙이는* 구조입니다. 트레이드오프: π prior 최대 보존 대 새 스트림 초기화 비용. **CP1 코드 진입 시 비교 후보로 등록**.
- **falsifier 와의 연결** — D25 의 4-contribution ablation 에 "(c') future_phys_pred on/off" 한 줄을 더해 보조 손실 기여를 분리할 수 있습니다. 임계값은 ±5%p contact-precision 변화로 잡습니다.

---

## ⚠️ 먼저 검증할 실패 모드

MoSS 의 결과가 PROBE 스택으로 그대로 전이되지 않을 가능성과, 가장 싼 sanity check 를 묶어 둡니다.

- **하드웨어 격차 — 2지 그리퍼 → 다지 손** — MoSS 의 30 차원 촉각·7 차원 토크는 PROBE 의 Sharpa 22-DoF + Deform Map 200K+ 차원과 차원·동역학이 다릅니다. **싼 sanity check**: Sharpa Deform Map 을 fingertip-별 결과 force 벡터로 *압축* 한 단일 모달리티(저차원) 변형을 먼저 MoSS 식 단일 스트림으로 흘려 baseline 향상이 재현되는지 확인합니다. 표 1 의 단일 모달리티 컬럼이 대응 기준점입니다.
- **모달리티 수 1 종에서 무조건 향상 — 우리 셋업에서도 일관될까** — 단일 모달리티 변종도 일관되게 base 보다 오른다고 저자들은 적지만, 우리 cube rotation 과제는 본문 4 과제와 접촉 프로파일이 다릅니다. **싼 sanity check**: cube rotation 에서 *촉각 단일* MoSS 가 base 대비 향상 없으면, 다중 모달리티로 가는 명분이 약합니다. 24-trial 표본은 ±5%p 노이즈 한계이므로 30+ trial 을 권합니다.
- **두 단계 학습의 안정성 효과 — 우리 학습 곡선에서 재현될까** — 표 2 의 "w/o two-stage training" 은 Unstack Cup 에서 16.7%p 떨어집니다. **싼 sanity check**: Stage 1 (액션 헤드 동결) 의 *물리 손실 곡선* 이 plateau 에 도달하는지 학습 초기 5K 스텝에서 확인합니다. plateau 없이 발산하면 freeze 범위·LR 재조정이 필요합니다.
- **$`\lambda_{\mathrm{phy}}=0.1`$ 의 좁은 안전 마진** — 표 5 는 $`\lambda_{\mathrm{phy}}=1.0`$ 에서 큰 폭의 성능 저하를 짚습니다. **싼 sanity check**: 본격 학습 전 $`\lambda_{\mathrm{phy}}\in\{0.05, 0.1, 0.2\}`$ 그리드 1K-스텝 마이크로 스윕.
- **초기 접근/그래스핑 실패는 물리 피드백으로 못 메운다 (저자 자인)** — §B.2 가 자기 입으로 인정한 한계입니다. PROBE 의 in-hand rotation 과제는 접촉이 *이미* 형성된 상태에서 시작하므로 영향이 작지만, tool articulation (CP3) 에서는 같은 한계가 그대로 나타날 위험이 큽니다. **싼 sanity check**: CP3 진입 전 *grasping prior 정책* 의 별도 검증.

---

## 💡 컨텍스트 제안

- **§8.2 P2 핀 보강 후보 등록** — MoSS(arXiv:2604.23272)를 P2 의 *deferred candidate* 로 등록해 두기를 제안합니다. 현재 P2 핀은 8 종 한도가 차 있고(SaTA·TacFiLM·Sparsh·ViTacFormer·DexViTac·Touch Dreaming·AdapTac·XL-VLA), 분기별 rebalance 때 AdapTac 또는 Touch Dreaming 자리와 비교해 교체 여부를 결정합니다. 우위는 *복수 물리 모달리티 결합* 의 첫 통합 사례라는 데 있습니다.
- **§8.4 P4 핀 보강 후보 등록** — 두 단계 학습(Stage 1 액션 전문가 동결)이 D19/D21 의 1차 evidence 이므로 P4 deferred candidate 로 올립니다. VLA-Adapter 또는 PriorVLA 자리와 비교.
- **§6.3 D8/D10 deferred trigger 추가** — *모달리티별 디커플 스트림 + 조인트 크로스-모달 어텐션* 변종을 D8/D10 의 deferred 후보로 한 줄 적어 둡니다. 트리거: D10 v1(self-attention 풀링)이 in-hand rotation contact-precision 지표에서 baseline 대비 +5%p 미만일 때 / **CP1**.
- **§6.5 D19/D21 deferred — Stage 2 내부 분할** — 위 ⚙️ 의사결정 함의의 staged training 변형을 D21 의 deferred recipe 로 적어 둡니다. 트리거: Stage 2 학습 초반 (≤5K 스텝) 에 액션 전문가 그래디언트 노름이 발산할 때 / **CP1**.
- **anti-topic 예외 메모** — §7 의 "2-finger parallel-jaw grippers only" anti-topic 에 대해, MoSS 는 (b) structured tactile/proprio binding 조건으로 in-scope 입니다. 추후 비슷한 어댑터 논문의 일관된 처리를 위해 §7 본문에 *"VLA 적응 어댑터 논문은 평행 그리퍼 한정이어도 (a)~(d) 중 하나라도 만족 시 in-scope"* 한 줄 추가를 검토합니다.

> 💡 base 매핑은 `/implement-design analysis/2604.23272/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
