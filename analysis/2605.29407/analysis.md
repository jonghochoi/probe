# Paper Analysis — Phase-Conditioned Imitation Learning with Autonomous Failure Recovery for Robust Deformable Object Manipulation

> PROBE analysis 모드 산출물. 단일 한글 문서이며, 영문 1차 파일은
> 없습니다. 형식·이모지·용어 규칙은 `docs/STYLE.md` §5 / §4 를
> 정확히 따릅니다. 재실행 시 이 파일을 덮어씁니다.

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Phase-Conditioned Imitation Learning with Autonomous Failure Recovery for Robust Deformable Object Manipulation |
| 저자 | Dayuan Chen, Kai Tang, Yukuan Zhang, Kazuhiro Kosuge, Yasuhisa Hirata (Tohoku University · The University of Hong Kong) |
| 링크 | [arXiv:2605.29407](https://arxiv.org/abs/2605.29407) |
| 발행일 / 버전 | 2026-05-28 · v1 (IEEE/ASME Transactions on Mechatronics 게재 승인) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-02 |

---

## 🧭 한 줄 요약 (TL;DR)

ACT 같은 모방 학습 정책이 추론 시 Markovian 가정에 묶여 겪는 state aliasing(시각적으로 비슷한 관측이 상반된 동작을 요구하는 상황)을, 작업 phase 를 FiLM 으로 ACT 인코더에 주입해 단일 정책을 phase 별로 분화함으로써 해소합니다. 여기에 시각·힘·자세를 융합한 phase 예측기를 얹어 접촉 실패를 실시간 감지하고 복구 궤적을 자동 발동하는 폐루프 계층 구조로, 양팔 T-shirt 걸기 작업의 성공률을 56% 에서 87% 로 끌어올립니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 케이블·의류 같은 변형체 조작(DOM)은 무한 자유도·심한 자기 가림·비선형 접촉 동역학 때문에 해석적 모델링이 어렵습니다. 데이터 기반 모방 학습이 대안이지만, 장기 시야(long-horizon) 작업에서 실행 중 실패를 스스로 복구하지 못합니다.
- **기존 접근의 한계** — ACT·Diffusion Policy 류는 추론 시 현재 관측을 미래 동작으로 직접 사상하는 Markovian 가정에 의존합니다. 그래서 삽입(Phase 1)과 복구(Phase 9)처럼 시각적으로 닮았지만 정반대 궤적(전진 vs 후퇴)을 요구하는 단계가 섞이면 모순된 동작을 평균내 진동하거나 멈춥니다. 이는 데이터 부족이 아니라 구조적 모호성입니다.
- **본 논문의 가설** — phase 를 명시적 조건으로 주입하면 한 정책이 단계별로 다른 행동을 내면서도 단계 간 공통 동역학(접근·삽입·후퇴)을 공유할 수 있습니다. 단, 단순 토큰 주입은 1200+ 시각 토큰 속에 희석되므로 FiLM 으로 인코더의 모든 층을 변조해야 효과가 있다는 것이 핵심 가설입니다.
- **왜 지금 중요한가** — 가림으로 인해 시각만으로는 스내깅(snagging) 같은 접촉 실패가 성공과 거의 구별되지 않습니다. 힘 피드백을 phase 예측에 넣으면 이 "보이지 않는" 실패를 잡아 자율 복구를 닫힌 루프로 만들 수 있고, 이것이 실행 단계 강건성의 병목입니다.

---

## 🧩 핵심 기여

- phase 를 명시적 동역학 사전(dynamics prior)으로 삼아 ACT 인코더에 FiLM 으로 주입하는 phase-conditioned 모방 학습 구조입니다. 토큰 수준 조건화와 달리 phase 별 특징 추출을 강제해, 모순된 동작 궤적이 섞인 멀티태스크 데이터에서도 시각 state aliasing 을 해소합니다.
- 멀티모달 피드백(시각·힘·자세)을 융합한 phase 예측기를 폐루프 실패 복구 메커니즘에 결합합니다. 시각만으로는 모호한 물리적 접촉 실패(스내깅 등)를 자율 감지하고 복구 정책을 발동해 실행 단계 강건성을 확보합니다.
- 컴플라이언스 실행에는 하이브리드 임피던스 컨트롤러를, 힘 인지 데이터 수집에는 양방향(bilateral) 햅틱 원격조작을 결합한 통합 메카트로닉스 플랫폼까지 함께 갖춥니다.
- 양팔 T-shirt 걸기/벗기기 작업에서 폐루프 시스템이 걸기 성공률을 56% → 87% 로 개선함을 실제 로봇으로 검증하고, FiLM 이 phase 별로 잘 분리된 특징 표현을 만든다는 점도 t-SNE 로 확인합니다.

---

## 🔑 기술 키워드

- **State aliasing** — 시각적으로 거의 같은 관측이 서로 다른(때로 상반된) 동작을 요구하는 현상. 같은 사진을 보고 "밀어라"와 "빼라"가 동시에 정답이 되는 상황으로, Markovian 정책이 평균/진동 동작으로 무너지는 원인입니다.
- **FiLM (Feature-wise Linear Modulation)** — 조건 벡터로부터 $`(\gamma,\beta)`$ 를 만들어 중간 특징에 채널별 affine 변환 $`\gamma\odot h+\beta`$ 를 거는 조건화 기법. 본 논문은 이를 ACT 인코더의 매 층 LayerNorm·MLP 출력에 적용합니다.
- **ACT (Action Chunking with Transformers)** — CVAE + 트랜스포머 인코더-디코더로 행동 청크를 예측하는 모방 학습 정책. 본 논문의 베이스 정책이며, 인코더에만 phase 조건을 겁니다.
- **Action chunking** — 한 번에 미래 $`N_{h}`$ 스텝의 동작 시퀀스를 통째로 예측하는 방식. 매 스텝 재계획보다 부드럽고 누적 오차에 강합니다.
- **Phase conditioning** — 작업을 의미 단위 단계(phase)로 쪼개 단계 라벨을 정책의 조건으로 주는 것. 한 정책이 단계별로 다른 "성격"을 갖되 공통 운동 기술은 공유하게 합니다.
- **Multi-modal phase predictor** — 시각·힘(wrench)·자세를 융합해 현재 phase 를 실시간 분류하는 네트워크. 정책의 동결 백본을 공유하며, 힘 신호로 시각이 놓치는 접촉 실패를 잡습니다.
- **Hybrid impedance controller** — 보간 궤적과 증분(incremental) 명령을 $`\alpha`$, $`\beta`$ 로 혼합해 암묵적 힘 제어 거동을 내는 컴플라이언스 컨트롤러(Inc-IC). 그리퍼 개폐 상태로 힘 지향/순수 임피던스 모드를 전환합니다.
- **Bilateral haptic teleoperation** — 실시간 힘 센서 값을 컨트롤러 진동으로 되돌려 조작자가 접촉 상태를 느끼며 시연을 모으는 원격조작. 힘-컴플라이언스 전략이 암묵적으로 데이터에 녹아듭니다.
- **Temporal ensembler** — ACT 가 겹치는 행동 청크의 예측을 시간축으로 가중 평균해 부드러운 명령을 만드는 장치. 본 논문은 phase 전환마다 이를 리셋합니다.
- **Deformable object manipulation (DOM)** — 천·케이블처럼 형상이 무한 자유도로 변하는 물체의 조작. 자기 가림과 비선형 접촉으로 해석적 모델링이 어려운 분야입니다.

---

## 🔬 방법론

### 직관

핵심 직관은 "phase 를 명시적 조건으로 주되, 그 조건이 절대 희석되지 않게 박는다"입니다. 장기 시야 작업에서는 성공 삽입과 실패 복구처럼 시각적으로 닮은 단계가 정반대 궤적을 요구합니다. Markovian 정책은 이 모순을 평균내 무너지므로, 단계 정보를 특징 추출 단계에서부터 분리해야 합니다.

> "This is not a problem of insufficient data, but a structural ambiguity that requires explicit conditioning to resolve." (§1)
> (한글 해설 — 저자는 state aliasing 이 데이터를 더 모은다고 풀리는 문제가 아니라 명시적 조건화가 있어야 풀리는 구조적 모호성임을 못 박습니다. 이것이 phase 를 단순 입력이 아니라 변조 신호로 다루는 이유입니다.)

phase 를 추가 토큰으로 넣으면 네 대의 카메라에서 나온 1200+ 시각 토큰의 self-attention 속에 묻혀 영향력이 사라지므로, 저자는 토큰 대신 FiLM 을 택했습니다.

![Figure 1 — failure recovery architecture overview](https://arxiv.org/html/2605.29407/pics/system_overview.png)

> "Figure 1: Failure recovery architecture: a phase detector controlling the task process, a phase conditioned policy generating the deterministic behaviors, and a hybrid impedance controller guaranteeing the dynamic adaptivity." (§1)
(한글 해설 — phase 감지기(작업 흐름 제어)·phase 조건 정책(결정론적 행동 생성)·하이브리드 임피던스 컨트롤러(동적 적응성)라는 세 역할 분담을 한 장으로 보여 줍니다. 본문이 말하는 폐루프 계층 구조의 전경입니다.)

### 아키텍처

시스템은 세 계층으로 구성됩니다 — (중간) phase 조건 ACT 정책, (상위) phase 예측·실패 복구, (하위) 하이브리드 임피던스 컨트롤러.

![Figure 2 — hierarchical control architecture](https://arxiv.org/html/2605.29407/x1.png)

> "Figure 2: Hierarchical Control Architecture. The system is organized into three levels: (Top) The decision layer uses multi-modal feedback to determine the current phase ..." (§3)
(한글 해설 — 상위 결정 계층이 멀티모달 피드백으로 현재 phase 를 정하고, 그 phase 가 중간 정책을, 정책 출력이 하위 컨트롤러를 구동하는 위→아래 흐름을 도식화합니다.)

중간 계층(ACT 정책)은 네 장의 RGB 이미지를 공유 ResNet-18 백본에 통과시켜 특징 맵을 $`(4H^{\prime}W^{\prime})\times d_{\text{model}}`$ 토큰으로 펴고 2D 사인 위치 임베딩을 더합니다. 양팔 엔드이펙터 자세( $`\mathbb{R}^{20}`$ , 6D 회전 사용)와 wrench( $`\mathbb{R}^{12}`$ )는 각각 선형층으로 $`d_{\text{model}}`$ 에 투영하고, phase 라벨은 학습된 임베딩으로 매핑합니다. 이렇게 모은 토큰을 $`(4H^{\prime}W^{\prime}+4)\times d_{\text{model}}`$ 시퀀스로 합쳐 트랜스포머 인코더에 넣으면, 그 안에서 FiLM 이 각 층을 변조합니다.

CVAE 인코더가 스타일 변수 $`z`$ 를 만들며, 학습 시에는 정답 행동 시퀀스를 인코딩해 잠재 분포를 배우고 추론 시에는 $`z`$ 를 prior 평균으로 두어 결정론적으로 디코딩합니다. 디코더는 표준 ACT 구조로, 고정 위치 쿼리가 cross-attention 으로 인코더 출력을 참조해 길이 $`N_{h}`$ 의 행동 청크를 출력합니다.

> "$`a_{t}=[a_{t,L}^{\top},a_{t,R}^{\top}]^{\top}\in\mathbb{R}^{20}`$" (§3.A)
(한글 해설 — 출력 동작은 좌/우 양팔 명령을 이어 붙인 20차원 벡터입니다. 각 팔은 위치 $`\mathbb{R}^{3}`$ · 6D 방향 $`\mathbb{R}^{6}`$ · 그리퍼 명령 $`\mathbb{R}^{1}`$ 으로 구성됩니다.)

상위 계층(phase 예측기)은 학습된 ACT 정책의 이미지 백본과 자세/wrench 투영층을 동결 상태로 공유합니다. 카메라별 특징 맵은 global average pooling 으로 $`1\times d_{\text{model}}`$ 까지 압축하고, 양팔 자세·wrench 도 같은 차원으로 투영합니다. 여기에 Task ID 임베딩을 더해 탐색 공간을 제약하는데('걸기 시작'과 '벗기 종료'처럼 시각이 닮은 phase 를 구분하기 위함), 전체를 $`1\times 7d_{\text{model}}`$ 벡터로 합치면 MLP 가 phase 로짓을 뽑고 softmax 로 확률화합니다. phase 전환 시 ACT temporal ensembler 를 리셋하고 1초 저역통과 필터로 잘못된 전환을 억제합니다.

> "Involving force feedback in the phase predictor, therefore compensates for the inherent limitation of vision-only detection." (§3.B)
> (한글 해설 — 스내깅·재밍 같은 접촉 실패는 가림 때문에 카메라상 성공과 구별되지 않지만 힘 영역에서는 스파이크나 비정상 지속력으로 뚜렷한 시그니처를 남깁니다. 그래서 힘 피드백이 시각 전용 감지의 한계를 보완한다는 것이 상위 계층 설계의 근거입니다.)

하위 계층(하이브리드 임피던스 컨트롤러)은 15 Hz 로 예측된 목표 자세 $`\mathbf{x}_{pred}`$ 를 직접 실행하지 않고 두 명령 스트림을 혼합합니다. 첫째는 $`\mathbf{x}_{pred}`$ 를 고주파 부드러운 궤적 $`\mathbf{x}_{intp}`$ 로 보간하고, 둘째는 증분 명령 $`\Delta\mathbf{x}_{icnc}=\mathbf{x}_{pred}-\mathbf{x}_{obs}`$ 를 현재 자세에 더해 $`\mathbf{x}_{inc}`$ 를 만듭니다. 두 파라미터 $`\alpha`$ 와 $`\beta`$ 가 이를 혼합해 암묵적 힘 제어 거동을 냅니다(Inc-IC).

> "The parameter $`\beta`$ switches the control mode based on the gripper state." (§3.C)
> (한글 해설 — 그리퍼가 닫히면(물체 접촉 가정) 힘 지향 모드로 컴플라이언스를 높이고, 열리면 순수 임피던스 제어로 되돌려 변동 접촉력으로 인한 드리프트를 막습니다. 즉 접촉 여부를 그리퍼 상태로 추정해 컴플라이언스를 켜고 끕니다.)

### 학습 목표 / 손실

본문은 별도의 새 손실식을 제시하지 않습니다. 정책은 표준 ACT 학습(행동 재구성 + CVAE 의 KL 정규화)을 따르고, 여기에 FiLM 변조와 phase 임베딩을 인코더 경로에 더합니다. phase 예측기는 phase 로짓에 대한 분류(softmax) 문제로 따로 학습하며, 복구 시연(Phase 8/9/10)은 DAgger 방식으로 정책 학습 데이터에 포함됩니다.

> "We apply FiLM to the encoder rather than the decoder for two reasons." (§3.A)
> (한글 해설 — ① state aliasing 은 지각 수준에서 발생하므로 행동 생성 이전에 시각적으로 닮은 입력을 서로 다른 특징으로 사상해야 하고, ② 디코더를 phase 무관하게 두면 접근·삽입·후퇴 같은 저수준 공통 동역학을 단계·작업 간 공유해 데이터 효율이 오릅니다. 인코더 변조의 직접 근거입니다.)

### 학습 셋업

phase-conditioned ACT 정책은 640×480 RGB 입력, 청크 크기 $`N_{h}=50`$ 으로 학습합니다. 인코더 4층 + 디코더 2층, 히든 차원 $`d_{\text{model}}=512`$, 60 epoch, 배치 8, 4 GPU, 고정 학습률 $`1\times 10^{-5}`$ 입니다. 데이터는 햅틱 원격조작으로 수집했으며, 추론은 15 Hz 였지만 데이터는 30 Hz 로 기록했습니다. 두 작업 각각 정상 시연 100 에피소드(걸기 0.85시간, 벗기 0.71시간), 각 실패 복구 시나리오(Phase 8/9/10) 30 에피소드씩(각 2.3 / 1.4 / 5.2분)을 추가 수집했습니다. 작업은 걸기 5 phase(0–4), 벗기 3 phase(5–7)로 분해하고, phase 전환은 Quest 컨트롤러 버튼으로 수동 라벨링했습니다.

---

## 📊 실험 설정과 결과

하드웨어는 양팔 DENSO VS-087(각각 ATI Axia80-M8 F/T 센서 + Robotiq 2F-85 그리퍼 + Realsense D405 손목/435i 전방/455 상단 카메라)입니다. 학습은 RTX 6000 Ada 4장, 추론·phase 예측·임피던스 제어는 RTX 4090 단일 머신(Ubuntu 22.04 · ROS2)에서 돌립니다. 작업은 양팔 T-shirt 걸기/벗기이며 복구 phase 는 가장 빈번한 운동학적 실패에서 도출했습니다 — Phase 8(삽입 스내깅 → 흔들기), Phase 9(대형 정렬 실패 → 전역 리셋/후퇴), Phase 10(공중 미끄러짐 → 동적 재파지).

전체 작업 성공률(Table I, 작업당 N=100)은 다음과 같습니다.

| Task | Total Trails | Natural Success | Failure Occurrences | Detection Rate | Recovery Success | Final Success Rate |
|---|---|---|---|---|---|---|
| Hanging | 100 | 56 | 44 | 40/44 (90.91%) | 31/40 (78.9%) | 87% |
| Taking off | 100 | 88 | 12 | 8/12 (66.67%) | 4/8 (50%) | 92% |

> "our closed-loop system successfully recovered from 40 of 44 contact failures during hanging and from 4 of 8 during takeoff, thereby significantly improving the success rates to 87% and 92%, respectively." (§4.D, Table I)
> (한글 해설 — 복구 메커니즘이 없는 개루프 기준 성공률은 걸기 56% · 벗기 88% 입니다. 폐루프가 걸기에서 44건 중 40건을 감지·31건 복구해 87% 로, 벗기는 92% 로 끌어올립니다. 단 Phase 10(벗기)의 복구율 50% 는 제한된 공간 지각으로 인한 파지 실패 탓이라고 밝힙니다.)

실행 단계 강건성 ablation(Table II, 걸기 작업 단독)은 FiLM 의 기여를 분리합니다. Nominal 20회, Misalignment(3–5cm 수동 변위) 10회, Snagging(수동 유발) 10회입니다.

| Model | | Nominal | Misalign. | Snagging |
|---|---|---|---|---|
| A | ACT | 8/20 (40%) | 0/10 (0%) | 1/10 (10%) |
| B | ACT-R | 16/20 (80%) | 1/10 (10%) | 5/10 (50%) |
| C | ACT-MR | 9/20 (45%) | 0/10 (0%) | 6/10 (60%) |
| D | ACT-MR+Phase Tok | 12/20 (60%) | 0/10 (0%) | 2/10 (20%) |
| E | ACT-MR+Phase FiLM (Ours) | 18/20 (90%) | 8/10 (80%) | 10/10 (100%) |

> "Model D adds the phase label as an input token. While nominal performance partially recovers (60%), snagging recovery drops sharply (20%), misalignment remains unchanged, indicating that the phase signal is diluted among the 1200+ visual tokens during self-attention ..." (§4.D, Table II)
> (한글 해설 — 토큰 주입(모델 D)은 nominal 만 일부 회복하고 misalignment 는 그대로 0% 입니다. 같은 phase 신호를 FiLM 으로 매 층 변조한 모델 E 는 90% / 80% / 100% 로 전 조건에서 일관되게 앞섭니다. "토큰은 희석되고 FiLM 은 박힌다"는 핵심 가설의 정량 근거입니다.)

> "Model C, trained on both hanging and taking-off data, degrades nominal performance below even the single-task baseline A (45% vs. 40%)." (§4.D)
> (한글 해설 — 조건화 없이 모순 작업 데이터를 합치면(모델 C) 새로운 aliased state 가 늘어 단일 작업 베이스라인보다도 떨어집니다. 데이터를 단순히 키우는 것이 오히려 해로울 수 있다는 결과입니다.)

t-SNE 분석(Figure 8)은 동일 200개 관측을 7개 phase 라벨로 각각 통과시킨 1400개 임베딩을 비교합니다. 토큰 주입(모델 D)은 phase 간 임베딩이 심하게 엉키지만, FiLM(모델 E)은 phase 별로 잘 분리된 군집을 이루며 특히 복구 phase(8, 9)가 정상 phase 에서 멀리 떨어진 타이트한 군집을 형성합니다.

> "Notably, the recovery phases (8, 9) form tight, isolated clusters far from the nominal phases, confirming that FiLM enables the encoder to switch between distinct perceptual modes rather than merely appending a condition signal that can be diluted by visual features." (§4.D.3)
> (한글 해설 — FiLM 이 LayerNorm·중간 활성을 직접 변조하므로 같은 관측이 phase 에 따라 근본적으로 다른 특징으로 바뀝니다. 조건 신호를 덧붙이는 수준이 아니라 인코더의 지각 모드 자체를 전환한다는 시각적 증거입니다.)

---

## ⚖️ 한계

- **시스템 성능이 phase 예측기 정확도에 묶임** — 모델 E 의 nominal 실패 2건은 잘못된 phase 예측에서 비롯됐고, 스내깅 복구 10건 중 5건은 의도한 Phase 8(국소 흔들기)이 아니라 Phase 9(전역 리셋)로 실행됐습니다. 저자가 향후 개선 방향으로 직접 지목합니다.
- **Phase 10(벗기 공중 미끄러짐) 복구율 50%** — 시스템의 제한된 공간 지각에서 오는 파지 실패가 주원인입니다.
- **동적 실행 한계** — 청크에서 3·5번째 동작만 뽑아 빠르게 실행하면 부드러움·정밀도가 떨어지고, temporal ensembler 의 평활화를 우회해 jerky 해지며 물체를 학습 분포 밖(OOD) 상태로 밀어 넣습니다. 벗기 작업에서는 총 실행 시간이 오히려 길어졌습니다.
- **일반화 강건성 미해결** — 본 연구가 다루는 것은 실행 단계 강건성뿐입니다. 색·재질·형상이 다른 의류 적응(일반화 강건성)은 대상이 아닙니다. RGB 입력 + 단일 T-shirt 학습이라 외형이 바뀌면 재학습 없이는 성능이 크게 떨어집니다.
- **수동 phase 라벨링 의존** — 시연 수집 중 조작자가 버튼으로 phase 전환을 직접 라벨했고, 새 의류 확장 시 phase 라벨 시연 재수집 + 재학습이 필요합니다.

---

## ♻️ 재현성

- **코드/영상** — 프로젝트 페이지 공개: https://leledeyuan00.github.io/phaser/ ("PHASER"). 본문은 코드·영상 공개를 명시하나 데이터셋 공개 여부는 따로 밝히지 않습니다.
- **하드웨어** — 양팔 DENSO VS-087, ATI Axia80-M8 F/T, Robotiq 2F-85, Realsense D405/435i/455, Meta Quest Pro(햅틱 원격조작)까지 기종을 구체적으로 적어 두었습니다.
- **학습 자원/하이퍼파라미터** — RTX 6000 Ada 4장 학습, 4090 추론, $`N_{h}=50`$ · $`d_{\text{model}}=512`$ · 4 enc/2 dec · 60 epoch · batch 8 · lr $`1\times 10^{-5}`$ 등 재현에 필요한 수치를 모두 밝혀 놓았습니다.
- **데이터 규모** — 작업당 정상 100 에피소드 + 실패 복구 시나리오별 30 에피소드(상기 수치)까지 명시했습니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **D4 (Body↔Hand 정보 공유, P1)** — 가장 직접적입니다. D4 v1 은 "FiLM with $`a_b`$ → ($`\gamma,\beta`$) modulating hand head input, **single point**"입니다. 본 논문은 같은 FiLM 계열 기법을 트랜스포머 인코더의 **매 층**에 적용했을 때, 단일 토큰/단일 지점 주입(모델 D, Phase Tok)을 압도함을 정량·t-SNE 로 보입니다. 이는 D4 의 FiLM 선택을 지지하는 동시에, 그 deferred 트리거인 "multi-layer depth → trigger: single-point info bottleneck (cf. MolmoAct2 per-layer KV)"의 정량 근거로 쓸 수 있습니다.
- **방법론 베이스 FiLM ([arXiv:1709.07871])** — D4 의 FiLM 원전을 ACT 인코더 phase 조건화로 확장한 §8.1 methodology base 사례입니다.
- **P3 / System0 (D13·D14)** — 힘 신호로 접촉 실패(스내깅/슬라이딩)를 감지해 복구를 발동하는 폐루프는, System1 이 슬립/접촉 위기 구간에 저수준 안정화를 켜는 System0 게이팅(D14 binary on/off)의 IL 판 유사물입니다. 다만 PROBE 의 System0 은 RL 접촉 안정화 서브루프인 반면 본 논문의 복구는 IL phase 라는 점이 본질적 차이입니다.
- **D3 / D16 (임피던스 출력)** — D3 deferred (iii) impedance, D16 deferred (ii) impedance 와 맞닿습니다. 그리퍼 상태로 힘 지향/순수 임피던스 모드를 전환하는 $`\beta`$ 설계가 구체적 참고점입니다.
- **D11 (P2, FiLM 촉각)** — §8.2 의 SaTA·TacFiLM 이 촉각을 FiLM 으로 융합하는 것과 같은 조건화 계열입니다. 본 논문의 조건 신호가 촉각이 아니라 이산 phase 라벨이라는 점만 다릅니다.
- **D25 / D26 (P5 평가)** — 기여를 한 요소씩 떼는 ablation(복구 데이터 / 멀티태스크 / 토큰 / FiLM)과 교란 하 성공률 측정은 D25 4기여 ablation·D26 robustness(섭동 하 성공 하락, CATFA) 측정 방식과 방법론적으로 정렬됩니다.
- **Identity 긴장** — 본 논문은 양팔 + Robotiq 2F-85 **평행 그리퍼** + 변형체(천) 작업으로, "hand-centric dexterous manipulation"이라는 정체성과 §7 anti-topic("2-finger parallel-jaw grippers only")에 도메인상 정면으로 걸립니다. 가치는 도메인이 아니라 기법(FiLM 변조·힘 기반 실패 감지·임피던스·요소별 ablation)에 한정됩니다.

---

## ✨ 핀 논문 대비 델타

- **FiLM ([arXiv:1709.07871], §8.1 methodology base) 대비** — 원전 FiLM 은 언어 조건으로 시각 백본을 변조해 시각 추론/멀티태스크를 돕습니다. 본 논문은 (1) 조건 신호를 **이산 phase 라벨**로 두고, (2) **ACT 트랜스포머 인코더의 매 층 LayerNorm·MLP** 를 변조하며, (3) 토큰 주입 대비 우위를 t-SNE 로 시각화한다는 점이 새롭습니다. 특히 "단일 토큰은 1200+ 시각 토큰 속에 희석되고 per-layer FiLM 은 박힌다"는 정량 비교는 D4 가 직접 끌어 쓸 수 있는 증거입니다.
- **SaTA ([arXiv:2510.14647]) · TacFiLM ([arXiv:2603.14604]) 대비** — 둘은 촉각을 FiLM 으로 융합합니다. 본 논문은 같은 변조 메커니즘을 phase(작업 단계)에 적용해 state aliasing 해소에 쓴다는 점에서 조건 신호의 의미가 다릅니다.
- **π0.5 ([arXiv:2504.16054]) 대비** — π0.5 는 VLA 고/저수준 계층화입니다. 본 논문의 계층(정책 / phase 예측기 / 임피던스 컨트롤러)은 "고수준 결정 + 저수준 컴플라이언스 실행"이라는 결은 닮았지만 구성 요소와 학습 신호(전부 IL)가 다릅니다.

---

## ⚙️ 의사결정 함의

- **D4 — single-point FiLM 의 잠재적 병목을 정량화** — 본 논문은 조건이 self-attention 토큰으로 희석될 때 per-layer FiLM 변조가 토큰 주입을 압도함(snagging 20% → 100%, misalign 0% → 80%)을 보입니다. PROBE 에 적용하면, D4 deferred 트리거 "hand head restructured to transformer"가 발동되면(즉 hand head 가 다토큰 트랜스포머가 되면) $`a_b`$ 조건을 단일 FiLM 지점이 아니라 **hand head 트랜스포머의 매 층에 per-layer FiLM** 으로 거는 쪽으로 설계를 옮겨야 합니다. 구체 config: `hand_head.film.per_layer = true`(가칭) 수준의 변경이 후보입니다.
- **P3 / D14 — 힘 시그니처를 System0 게이팅 트리거로** — 본 논문은 양팔 외력 합의 스파이크로 스내깅을 감지합니다. PROBE 의 System1↔System0 binary `maintain_grasp` 게이트(D14)와 슬립 감지(D17 reward)에 "힘/촉각 영역 스파이크 임계"라는 비용 낮고 구체적인 트리거 신호를 제시합니다.
- **D3 / D16 — 그리퍼/접촉 상태 게이팅 컴플라이언스** — 접촉 시(닫힘) 힘 지향, 비접촉 시(열림) 순수 임피던스로 전환하는 $`\beta`$ 설계는, Hand 출력을 impedance 로 두는 deferred 옵션을 켤 때 "접촉 상태로 강성 모드를 전환"하는 구체적 레시피로 차용 가능합니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **per-layer FiLM 우위가 우리 hand head 에 전이되지 않을 위험** — 본 논문의 FiLM 우위는 **1200+ 시각 토큰** 인코더에서 단일 토큰이 희석되기 때문입니다. PROBE 의 hand head 는 ~10 손가락 + 2 손바닥 토큰(D8) 규모의 MLP/경량 트랜스포머라 희석 압력이 훨씬 작습니다. 가장 빠른 검증: hand head 토큰 수에서 단일 FiLM 지점 vs per-layer FiLM 의 격차가 실제로 벌어지는지 소규모 ablation 으로 먼저 확인합니다(토큰이 적으면 격차가 사라질 수 있음).
- **IL 복구 phase 가 정체성과 충돌** — 본 논문의 복구는 수동 phase 라벨 + 시나리오별 시연 재수집에 의존합니다. 이는 일반화 다지 조작에는 확장되지 않으며, PROBE 가 슬립/파지 유지에만 RL(System0)을 쓰는 이유와 정확히 반대 방향입니다. "복구를 IL phase 로 만든다"를 그대로 채택하면 reward-engineerable 영역에만 RL 을 한정한다는 정체성과 충돌하므로, 차용은 "힘 기반 트리거 신호"에 한정해야 합니다.
- **F/T wrench 신호 ≠ 손끝 촉각** — 본 논문의 감지는 손목 6축 F/T 의 합력 스파이크입니다. PROBE 의 슬립 감지는 손끝 촉각(Deform Map)입니다. 우선순위 검증: 손끝 촉각이 스내깅/슬립에 대해 양팔 합력 스파이크에 견줄 만한 깨끗한 시그니처를 주는지부터 확인합니다.

---

## 💡 컨텍스트 제안

핀 교체는 제안하지 않습니다 — 본 논문은 평행 그리퍼·변형체 도메인이라 anti-topic 영역이며 P1–P5 어느 핀 슬롯의 도메인과도 맞지 않습니다. 그래도 **FiLM 방법론 증거**로서의 가치는 분명하므로, 다음을 사람 판단에 올립니다.

- **§8.1 methodology base FiLM 항목의 보조 증거로 비핀(non-pin) 기록 검토** — "토큰 주입은 희석되고 per-layer FiLM 은 박힌다 + t-SNE phase 분리"는 D4 의 single-point vs multi-layer 논쟁(deferred 트리거)에 외부 정량 근거로 곧장 쓸 수 있습니다. 핀이 아니라 D4 노트 또는 catalogs 의 FiLM 참고 자료 수준에서 인용 후보로 둘 만합니다.
- 본 제안은 기록 후보일 뿐이며 `context/MASTER.md` 는 수정하지 않았습니다.

> 💡 base 매핑은 `/implement-design analysis/2605.29407/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
