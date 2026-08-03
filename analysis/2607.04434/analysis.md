# Paper Analysis — RoboDojo: A Unified Sim-and-Real Benchmark for Comprehensive Evaluation of Generalist Robot Manipulation Policies

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | RoboDojo: A Unified Sim-and-Real Benchmark for Comprehensive Evaluation of Generalist Robot Manipulation Policies |
| 저자 | Tianxing Chen, Yue Chen, Zixuan Li, Junyuan Tang, Kailun Su, Haoran Lu 외 다수 (공동 1저자·프로젝트 리더 다수) · 교신저자 Mingyu Ding, Wenbo Ding, Ping Luo, Masayoshi Tomizuka (HKU·UC Berkeley·THU·PKU·Stanford·MIT·UNC·CMU·NUS·NTU·CUHK 등 18개 기관 협업) |
| 링크 | [arXiv:2607.04434](https://arxiv.org/abs/2607.04434) · [GitHub](https://github.com/RoboDojo-Benchmark/RoboDojo) · [Website](http://robodojo-benchmark.com/) |
| 발행일 / 버전 | 2026-07-05 제출 · 2026-07-08 개정 (v3) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-07-09 |
| 관련 Pillar | P0, P3, P5 |
| 태그 | sim2real, dataset |

<!-- 본문은 arXiv HTML(전문, v3)로 확보. 모든 수치는 본문/표에서 받은 그대로 인용.
     retrieval ladder:
       1. curl --fail "https://arxiv.org/abs/2607.04434"   → 200 (메타/초록)
       2. curl --fail "https://arxiv.org/html/2607.04434"  → 200 (전문 HTML, ~1MB)
     figure hotlink 은 arXiv HTML src 의 버전 세그먼트(v3) 를 stripping 하여
     https://arxiv.org/html/2607.04434/<file> 형태로 기록. -->

---

## 🧭 한 줄 요약 (TL;DR)

RoboDojo 는 시뮬레이션 42개 task(5개 능력 차원)와 실세계 18개 task(3개 embodiment)를 하나의 정책 인터페이스·평가 파이프라인으로 묶은 sim-and-real 통합 벤치마크로, Isaac Sim heterogeneous 병렬 시뮬레이션·원격 클라우드 실로봇 평가(RoboDojo-RealEval)·30개 정책 통합 인프라(XPolicyLab)·hidden-layout anti-gaming 리더보드를 함께 제공합니다. 30개 최신 generalist 정책을 돌린 결과 최고 정책조차 시뮬 평균 성공률 8.80%·실세계 12.8%에 그쳐 사람(각 76.03%·100.0%)과의 격차가 크며, generalization·precision·memory·open-semantic 전 차원에서 현재 정책이 신뢰 가능한 일반 조작에서 멀다는 진단 신호를 드러냅니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — generalist 로봇 조작 정책은 빠르게 발전했지만, 이들의 능력을 체계적·포괄적으로 진단할 평가 체계가 부족합니다. 대다수 벤치마크는 단순·단기·기술 협소 task 에 의존하고 능력 커버리지가 제한적입니다.
- **기존 접근의 한계 (1) 진단 커버리지** — task 변주가 주로 객체·배치·언어 표현 수준에 머물러 유사한 조작 패턴을 공유하므로, generalization·memory·precision·open-semantic·sequential 실행·bimanual 협응 같은 서로 다른 도전 축을 분리 진단하지 못합니다.
- **기존 접근의 한계 (2) sim vs real 분리** — 평가가 시뮬레이션 단독 또는 실세계 단독으로 나뉩니다. 시뮬레이션은 확장 가능하나 접촉 dynamics·구동 오차·지각 노이즈 같은 물리 배포 요인을 못 담고, 실세계 평가는 비싸고 느리며 표준 하드웨어·리셋 절차·프로토콜 부재로 재현이 어렵습니다.
- **본 논문의 가설** — 확장 가능한 시뮬레이션 진단과 재현 가능한 실세계 검증을 하나의 공유 정책 인터페이스로 결합하면, 정책을 "한 번 통합해" sim 과 real 양쪽에서 최소 적응으로 평가하는 통합 평가 루프를 세울 수 있다는 것입니다.
- **왜 지금 중요한가** — π0.5, RDT2, LDA-1B 등 VLA/foundation 정책이 급증하는 가운데, 집계 성공률 하나가 아니라 능력별로 실패 모드를 구조적으로 진단하고 sim→real 배포 전이를 표준 조건에서 측정할 공용 플랫폼이 필요한 시점입니다.

---

## 🧩 핵심 기여

- **sim-and-real 통합 평가 시스템** — 공유 정책 인터페이스·평가 파이프라인 위에서 시뮬레이션과 실세계 테스트를 함께 지원. heterogeneous 병렬 시뮬레이션(빠른 피드백) + RoboDojo-RealEval(표준화·재현·원격 물리 평가).
- **RoboDojo Benchmark** — 시뮬 42 task(5개 능력 차원: Generalization·Memory·Long-Horizon·Precision·Open) + 실세계 18 task(3개 embodiment: ARX X5·Piper·Piper X), 24개 조작 skill 커버.
- **XPolicyLab** — 30개 대표 정책을 공유 코드베이스로 통합해 데이터 포맷·전처리·학습·배포·평가를 표준화(각 정책의 내부 아키텍처는 보존). "한 번 통합, sim+real 평가".
- **공개 리더보드 + 체계적 분석** — 30개 정책을 시뮬(2026-07-03 동결)·10개 정책을 실세계에서 평가하고, 능력별 실패 모드·human-teleop 격차·sim–real 순위 불일치를 6+6개 finding 으로 정리.
- **부수 산출: 학습 데이터셋** — 시뮬 3,500 traj(20.66h)·실세계 1,800 traj(17.91h)의 bimanual 조작 데이터를 25 Hz 로 함께 공개(정책 통합·재현용).

---

## 🔑 기술 키워드

- **Generalist manipulation policy** — 하나의 정책이 다양한 객체·장면·언어 지시에 걸쳐 조작을 수행하도록 설계된 VLA/foundation 정책. RoboDojo 의 평가 대상.
- **Sim-and-real unified benchmark** — 시뮬레이션 진단과 실세계 검증을 하나의 정책 인터페이스·프로토콜로 묶은 평가 체계. "시뮬에서 빠르게 iterate, real 에서 배포 전이 확인"을 한 루프로.
- **Heterogeneous parallel simulation** — 공유 vectorized 인터페이스로 여러 환경을 동시에 step 하되, 각 환경이 서로 다른 객체·기하·distractor 수·배치를 독립 샘플링하는 병렬화. 동일 template 을 복제하는 homogeneous 병렬과 대비.
- **Capability dimension** — 객체·배치 변주가 아니라 서로 다른 조작 도전(generalization/memory/precision/long-horizon/open)을 분리 측정하는 진단 축. 집계 성공률 뒤에 숨은 능력 불균형을 드러냄.
- **RoboDojo-RealEval** — 하드웨어·workspace·조명·리셋 절차·평가 프로토콜·배포 인터페이스를 표준화하고 원격 클라우드 접속을 제공하는 실세계 평가 시스템. layout replay 로 초기 조건을 재현.
- **XPolicyLab** — 이질적 정책을 공용 데이터/학습/배포 표준으로 감싸 "한 번 통합"하게 만드는 인프라. 언어모델의 통합 하니스를 로봇 정책으로 옮긴 발상.
- **Hidden-layout verification** — 공개 layout 에 대한 overfitting·hand-tuning·leaderboard gaming 을 줄이려 공식 평가 때 비공개 layout 을 추가로 돌리는 anti-gaming 일관성 체크.
- **Score vs success rate** — success rate 는 이진 완료, score 는 부분 진행(intermediate sub-step)을 포착하는 이원 지표. 둘의 격차가 "부분 성공하나 최종 완료 실패"를 진단.
- **Homogeneous leader-follower teleoperation** — 리더 arm 이 팔로워 로봇과 같은 embodiment 인 실세계 시연 수집 방식. teleop 명령 공간을 배포 embodiment 와 정렬해 안정적 시연을 확보.

---

## 🔬 방법론

> 본 논문은 학습 알고리즘이 아니라 **평가 벤치마크·인프라** 논문입니다. 따라서 이 절은 학습 목표/손실 대신 (1) 벤치마크 구성, (2) 시뮬·실세계 시스템 아키텍처, (3) 평가·anti-gaming 프로토콜로 분해합니다.

### 직관

RoboDojo 의 출발점은 "generalist 정책은 빠르게 좋아지는데, 무엇이 얼마나 좋아졌는지 말해줄 자가 없다"는 진단 공백입니다. 기존 벤치마크의 task 변주는 대개 배경·객체·문장을 바꾸는 수준이라 분포 강건성은 재지만 근본적으로 같은 조작 패턴을 반복하고, 그래서 "이 정책은 memory 가 약한가, precision 이 약한가"를 분리해 말해주지 못합니다. RoboDojo 는 이를 5개 능력 차원(Generalization·Memory·Long-Horizon·Precision·Open)으로 명시적으로 쪼갠 42개 시뮬 task 로 대체합니다.

두 번째 통찰은 sim 과 real 이 상보적이며 어느 한쪽만으로는 부족하다는 것입니다. 시뮬레이션은 싸고 확장 가능해 빠른 iteration 에 적합하지만 접촉·구동·지각 노이즈 같은 물리 배포 현실을 못 담고, 실세계는 직접적이지만 표준 하드웨어·리셋·프로토콜이 없으면 재현이 불가능합니다. RoboDojo 는 둘을 하나의 공유 정책 인터페이스(XPolicyLab)로 묶어 "한 번 통합하면 양쪽에서 평가"되게 만들고, 실세계 쪽은 하드웨어·조명·리셋·프로토콜을 물리적으로 표준화한 RoboDojo-RealEval 로 재현성을 확보합니다.

세 번째 통찰은 평가 자체가 병목이 되어선 안 된다는 것입니다. 다양한 장면을 병렬로 돌리되 각 병렬 환경이 서로 다른 장면 구성을 갖는 heterogeneous 병렬화로 처리량을 끌어올리고, 실세계는 원격 클라우드 평가로 checkpoint·코드를 공개하지 않고도 표준 rig 에서 돌릴 수 있게 합니다. 마지막으로, 공개 layout 에 대한 gaming 을 막기 위해 비공개(hidden) layout 검증을 공식 리더보드 게시 조건에 넣습니다.

### 벤치마크 구성 (task dimensions)

시뮬레이션 42 task 는 ARX X5 bimanual 플랫폼(두 arm base 간격 0.6 m) 위에 5개 능력 차원으로 조직됩니다.

- **Generalization (12 task)** — 배경·조명·clutter·타깃 객체의 unseen 변주에 대한 강건성. RoboTwin 2.0 대비 더 강한 장면 randomization 과 조밀한 clutter(RoboTwin 2.0 최대 10개 → RoboDojo 최대 25개 clutter 객체). wooden-table overfitting 을 줄이려 100개 보조 DLC(domain-randomized) trajectory 를 data-level augmentation 으로 추가.
- **Memory (6 task)** — 부분 관측(partially observable) 상황에서 과거 관측 기반 non-Markovian 결정. 예: `match_and_pick_from_conveyor`(컨베이어에서 사라진 객체의 category 를 기억해 이후 후보 중 매칭 픽), `imitate_sorting_sequence`(다른 arm 의 배치 순서를 관찰·기억·재현).
- **Long-Horizon (8 task)** — 의존적 sub-step 시퀀스 완수. 예: `classify_objects`(여러 객체를 대응 위치로 분류, 넓은 workspace 로 양팔 handover 유발).
- **Precision (8 task)** — 엄격한 공간·모션 정확도. 예: `insert_tubes`(좁은 구멍에 tube 를 연속 삽입, 작은 localization/궤적 오차로 실패).
- **Open (8 task)** — 학습 데이터에 다른 맥락으로 등장한 skill 을 요구하는 unseen task 명세. open-semantic grounding·skill recombination·language-conditioned transfer 평가. **학습 셋에서 제외**되어 순수 전이만 측정.

실세계 18 task 는 embodiment 당 6개씩 3개(ARX X5·Piper·Piper X)에 분산됩니다. sim–real 을 1:1 매칭하지 않으며(직접 sim2real transfer 측정이 목적이 아님), 대신 접촉 집약 상호작용·정밀 정렬·다객체 조작·부분 관측 같은 물리 배포 도전을 노출하는 상보적 평가 설정입니다.

![Figure 2 — RoboDojo task overview](https://arxiv.org/html/2607.04434/x5.png)

> "Figure 2: Task Overview of RoboDojo. RoboDojo includes 42 simulation tasks and 18 real-world tasks for evaluating generalist robot manipulation policies. The simulation tasks are organized into five capability dimensions: Generalization, Memory, Long-Horizon, Precision, and Open, enabling efficient capability-oriented diagnosis. The real-world tasks assess policy behavior under challenging and reproducible physical deployment conditions. Together, these tasks cover diverse manipulation skills, spatial configurations, and bimanual coordination patterns across simulation and the real world." (§3)
> (한글 해설 — 5개 능력 차원 시뮬 task 와 3 embodiment 실세계 task 의 전체 배치를 한 장에 요약한 그림으로, "객체·배치 변주 초월"이라는 벤치마크 설계 의도를 시각화합니다.)

### 시스템 아키텍처

시스템은 세 축 — 시뮬레이션 플랫폼, RoboDojo-RealEval, XPolicyLab — 으로 나뉩니다.

**시뮬레이션 플랫폼** 은 NVIDIA Isaac Sim + Isaac Lab 을 백엔드로, MagicSim 인프라(모듈형 manager 아키텍처·config 기반 장면 구성) 위에 세워집니다. 각 task 는 asset·layout·초기 분포·randomization 범위·성공 조건을 정의한 modular YAML 로 인스턴스화되어 task 명세와 simulator 실행을 분리합니다. reset 시 객체·pose·articulation·clutter·조명·배경 텍스처를 deterministic seed 로 샘플링해 다양하지만 재현 가능한 장면을 생성합니다. rigid·articulated·deformable asset(Meshy AI 재구성·ClothesNet 등)을 통합 인터페이스로 다루며, 자동 합성은 cuRobo v2 motion planner 로 `grasp`·`place`·`handover`·`insert` 등 저수준 skill 을 조합하고, 어려운 task 는 VR teleoperation 으로 수집합니다.

핵심은 **heterogeneous 병렬화** 입니다.

> "RoboDojo therefore supports heterogeneous parallel simulation. Multiple environments are stepped under a shared vectorized interface, while each environment maintains an independently sampled scene configuration." (§4.1.3)
> (한글 해설 — 공유 vectorized 인터페이스로 여러 환경을 함께 step 하되 각 환경이 독립 장면 구성을 갖는 것이 핵심입니다. 동일 template 을 복제하는 homogeneous 병렬은 pose·seed 만 다르므로 generalist 평가에 필요한 장면 다양성을 못 주는데, RoboDojo 는 객체 category·기하·distractor 수·articulation 구조·layout 을 환경마다 다르게 두어 속도와 다양성을 동시에 확보합니다.)

**RoboDojo-RealEval** 은 arm·카메라·조명·workspace 의 상대 pose 를 모듈형 구조물로 고정하고, scene reset·정책 실행·비상 정지·영상 수집·클라우드 채점을 위한 touchscreen web 인터페이스를 제공합니다. 평가 시 target layout 이미지와 live 관측을 투명 overlay 로 겹쳐 매 trial 전 초기 조건을 복원합니다. ARX X5·Piper·Piper X 3개 embodiment 를 지원하고 local·원격 클라우드 평가를 모두 제공합니다.

![Figure 7 — RoboDojo-RealEval system](https://arxiv.org/html/2607.04434/x10.png)

> "Figure 7: Overview of the RoboDojo-RealEval system. RoboDojo-RealEval provides a standardized physical platform for reproducible real-world robot manipulation evaluation, with controlled workspace geometry, fixed robot and camera mounts, stable lighting, a touchscreen evaluation interface, and support for three collaborative bimanual embodiments." (§4.2)
> (한글 해설 — 실세계 평가의 우연적 변동(조명·로봇 배치·카메라 pose·리셋 정확도)을 물리적으로 고정하는 표준화 rig 로, "실로봇 평가의 재현성"이라는 본 벤치마크의 두 번째 기둥을 구현합니다.)

**XPolicyLab** 은 서로 다른 데이터 포맷·전처리·학습 스크립트·action 표현·런타임을 공용 변환 도구·학습 template·배포 절차·평가 스크립트로 표준화하되 각 정책의 내부 아키텍처는 보존합니다. 30개 정책을 공유 코드베이스로 통합해 관측-액션 인터페이스로 정책 서버와 sim/real 을 연결, "시뮬에서 iterate → 원격 실세계 배포"를 최소 적응으로 잇습니다.

### 평가·anti-gaming 프로토콜

시뮬은 42 task × 50 episode(총 2,100 episode)로 평가하며, Generalization 12 task 는 50 episode 를 25 standard + 25 random 으로 분할합니다. 전체 성능은 task 수가 많은 차원의 지배를 막기 위해 **5개 차원 평균**으로 계산합니다. 대부분 정책은 3개 random seed × 50 trial/task(= 150 trial/task)로 학습·평가합니다. 실세계는 task 당 10 trial, layout replay 로 초기 조건을 통일하고, 3명의 평가자가 double-blind 로 채점(최종 = 3인 평균)합니다.

리더보드는 비영리 재단(AI MMLab Club)이 상업 자금 없이 학계 파트너와 공동 운영합니다. 공식 게시는 (1) 공식 온라인 평가 시스템 사용, (2) 시뮬 3-seed mean/std·실세계 3 embodiment 전부, (3) **hidden-layout 검증 통과**, (4) checkpoint·학습/배포 코드·config·재현 지침을 XPolicyLab 로 공개, (5) 평가 영상 공개를 요구합니다.

> "To reduce overfitting, hand-tuning, and leaderboard gaming on public layouts, submitted models are additionally evaluated on hidden verification layouts during official evaluation." (§3.3)
> (한글 해설 — 공개 layout 에 대한 hand-tuning·gaming 을 억제하는 hidden-layout 보조 일관성 체크로, 재현·공정성을 리더보드 게시 조건에 못 박는 anti-gaming 설계입니다.)

---

## 📊 실험 설정과 결과

실험은 (1) 벤치마크가 드러내는 정책 한계, (2) 평가 효율(throughput·wall-clock), (3) 평가 안정성(cross-GPU·repeat) 세 갈래입니다.

**시뮬레이션 리더보드 (score / success rate %)** — 상위권 일부 + 사람 참조. 5개 차원 평균이 Average.

| 정책 | Generalization | Precision | Long-Horizon | Memory | Open | Average |
|---|---|---|---|---|---|---|
| Hy-Embodied-0.5-VLA | 11.77 / 8.39 | 13.81 / 8.00 | 25.74 / 14.92 | 13.37 / 12.11 | 0.65 / 0.58 | **13.07 / 8.80** |
| Spatial Forcing | 14.12 / 9.33 | 17.33 / 10.58 | 23.26 / 14.58 | 5.43 / 4.11 | 1.78 / 1.58 | 12.38 / 8.04 |
| $`\pi_{0.5}`$ | 13.37 / 8.17 | 12.40 / 5.50 | 23.54 / 14.67 | 5.78 / 4.56 | 1.98 / 1.67 | 11.41 / 6.91 |
| X-VLA | 10.48 / 6.78 | 18.32 / 12.00 | 16.53 / 9.75 | 4.76 / 3.56 | 0.55 / 0.50 | 10.13 / 6.52 |
| X-WAM | 7.39 / 3.33 | 6.72 / 1.83 | 17.47 / 9.08 | 6.32 / 4.67 | 0.57 / 0.25 | 7.69 / 3.83 |
| Human Expert (Teleop) | 90.05 / 87.83 | 68.06 / 64.00 | 83.63 / 74.25 | 75.25 / 74.33 | 85.13 / 79.75 | **80.42 / 76.03** |

> "Even the best-performing policy achieves only an $`8.80\%`$ average success rate and a $`13.07`$ average score, far below human experts, who reach a $`76.03\%`$ success rate and an $`80.42`$ score under the same evaluation protocol." (§6.1)
> (한글 해설 — 최고 정책조차 시뮬 평균 SR 8.80%로 사람 76.03%에 크게 못 미칩니다. task 는 사람에게 실행 가능하므로, 이 격차는 벤치마크 난이도가 아니라 정책 능력의 갭임을 뜻합니다. 능력별로 강점이 흩어져(Spatial Forcing↔Generalization, X-VLA↔Precision) 균형 잡힌 generalist 는 부재합니다.)

**차원별 판독 (per-dimension reading)**:
- **Generalization** — 장면 randomization 이 거의 전 정책에 걸쳐 광범위한 성능 붕괴를 일으킵니다. Standard→Random 상대 하락이 대부분 70~100%.
- **Precision** — X-VLA 가 최고(12.00% SR)이나, 전역 task 실행이 강하다고 국소 정밀 제어가 따라오지 않음(open-loop 실행·action jitter 관측). off-trajectory 보정 부재가 핵심 실패 모드.
- **Long-Horizon** — 상대적으로 강한 차원이나 최고도 15% 미만. score–SR 격차는 "부분 단계는 완료하나 최종 목표 도달 실패"를 뜻함(skill composition·stage 전환·오차 복구 결여).
- **Memory** — 명시적 memory 구조(EventVLA KEM)·world-model 예측(X-WAM)이 도움되나 sparse 증거 회수엔 부족. Hy-Embodied 가 embodied pretraining·action prior 로 최고(12.11% SR).
- **Open** — 사실상 미해결. 최고 π0.5 도 1.67% SR. semantic-to-action grounding 전 파이프라인이 취약.

**Standard vs Random 붕괴 (Table 3, score)**:

| 정책 | Standard | Random | 상대 하락 |
|---|---|---|---|
| Hy-Embodied-0.5-VLA | 21.98 | 1.57 | 92.9% |
| Spatial Forcing | 21.25 | 6.98 | 67.2% |
| $`\pi_{0.5}`$ | 20.92 | 5.82 | 72.2% |

> "Hy-Embodied-0.5-VLA obtains the highest Standard score of $`21.98`$, but drops to $`1.57`$ under Random, corresponding to a $`92.9\%`$ relative drop." (§6.1)
> (한글 해설 — Standard 강자가 Random 에서 92.9% 무너지는 반면 Spatial Forcing 은 명시적 3D spatial grounding 으로 하락을 67.2%로 줄입니다. spatial 표현 정렬이 장면 변동 강건성에 도움되나 절대 Random score 최고도 6.98 에 그쳐 여전히 취약합니다.)

**실세계 리더보드 (overall score / success rate %)** — 상위 3 + 사람.

| 정책 | Overall (score / SR) |
|---|---|
| $`\pi_{0.5}`$ | 22.9 / 12.8 |
| InternVLA-A1 | 12.0 / 7.2 |
| GalaxeaVLA (G0) | 9.0 / 4.4 |
| Human Teleop | 100.0 / 100.0 |

> "The best-performing policy, $`\pi_{0.5}`$, achieves only a $`12.8\%`$ overall success rate and a $`22.9`$ score across 18 real-world tasks, while human teleoperation reaches a $`100.0\%`$ success rate and a $`100.0`$ score on all tasks and embodiments." (§6.2)
> (한글 해설 — 실세계에서도 최고 정책이 12.8% SR 에 그치며, sim–real 순위가 부분적으로만 정렬됩니다(InternVLA-A1·GalaxeaVLA 는 실세계에서 시뮬보다 상대적으로 상승). 이는 RoboDojo 가 paired sim2real 벤치가 아니라 상보적 진단 설정임을 뒷받침합니다.)

**평가 효율 (Table 4, 8×RTX 4090)**:

| 설정 | Frames | Time | Avg. Speed |
|---|---|---|---|
| Heterogeneous parallel, zero action | 1,640,000 | 5h 53m | 77.4 interactions/s |
| Non-heterogeneous parallel, zero action | 1,640,000 | 11h 22m | 40.0 interactions/s |
| Heterogeneous parallel + $`\pi_{0.5}`$ inference | 1,640,000 | 7h 07m | 64.0 interactions/s |
| Non-heterogeneous + $`\pi_{0.5}`$ inference | 1,640,000 | 11h 38m | 39.2 interactions/s |
| RoboTwin 2.0 zero-action | 3,100,000 | 19h 19m | 44.6 interactions/s |

> "Under zero-action rollouts, RoboDojo achieves 77.4 interactions/s, compared with 40.0 interactions/s under non-heterogeneous parallel simulation, yielding a $`1.94\times`$ speedup." (§6.3.1)
> (한글 해설 — heterogeneous 병렬화가 zero-action 에서 1.94배, π0.5 추론 포함 end-to-end 에서 1.63배 처리량을 냅니다. RoboTwin 2.0 대비 더 높은 해상도(640×480 vs 320×240)에서도 정규화 처리량이 높습니다.)

실세계는 18-task 평가를 202.0분(약 3.4시간, 180 trial)에 완료하며 task 당 평균 11.2분입니다.

> "As shown in Table 5, RoboDojo-RealEval completes the 18-task real-world evaluation in 202.0 minutes, corresponding to approximately 3.4 hours for 180 physical trials." (§6.3.2)
> (한글 해설 — 표준 리셋·local RTX 4090 배포·통합 인터페이스가 실세계 벤치마킹의 운영 부담을 줄여, 전면 물리 평가를 유지하면서도 비교적 빠른 피드백을 줍니다.)

**평가 안정성** — cross-GPU(3×RTX 4090, layout 0, 3 seed): SR 표준편차 최대 1.1pp·score 최대 1.07, 전체 평균 SR≤0.5pp. 실세계 3회 반복: overall SR 표준편차 최대 1.3pp·score 최대 1.2. task 수준에선 접촉 집약·다단계 task 에서 분산이 크나 집계 수준에서 평균화됩니다.

**데이터셋 규모** — 시뮬 학습: 35개 task dir·3,500 traj·1,859,602 frame·20.66h @ 25Hz(34개 training task + 1 DLC, task 당 100 traj, Open 제외). 실세계: 1,800 traj·1,611,841 frame·17.91h @ 25Hz(3 embodiment × 6 task × 100 demo, 4명 operator, embodiment 당 600 traj). 관측은 head 1 + wrist 2 카메라 640×480 RGB(시뮬은 RGB-D).

---

## ⚖️ 한계

- **저자 명시: 실세계 커버리지 부분성** — RoboDojo-RealEval 은 현재 시뮬 리더보드의 부분집합(10개 정책)만 평가하며 sim–real 순위 정렬은 부분적입니다. paired sim2real 벤치가 아니므로 "시뮬 점수가 실세계 배포성을 얼마나 예측하는가"의 정량 답은 아직 열려 있습니다.
- **저자 명시: 확장성 로드맵의 미완** — dexterous hand·humanoid whole-body·tactile·mobile manipulation 은 향후 릴리스 계획일 뿐 현 벤치마크에 없습니다(§7). 즉 현재 RoboDojo 는 **parallel-jaw bimanual(ARX X5/Piper) 조작에 국한**됩니다.
- **(추론된 갭) 촉각·힘 모달리티 부재** — 관측은 RGB(-D) + robot state 뿐이며 tactile/force/torque 채널이 없습니다. 접촉 정밀·slip·grasp 유지 같은 hand-level 진단 축을 측정할 수단이 프레임워크에 없어, 접촉 집약 task 도 시각·자세 오차로만 실패를 귀인합니다.
- **(추론된 갭) 낮은 성능 천장(floor effect)** — 최고 정책이 시뮬 8.8%·실세계 12.8% SR 이라 대부분 셀이 한 자릿수입니다. 능력 차원별 진단 신호는 유효하나, 신호가 이렇게 바닥에 눌려 있으면 개선 delta 를 통계적으로 잡기 어렵고 순위가 소수 성공 사례에 민감해질 수 있습니다(안정성 표에서 특정 task 분산이 큰 이유).
- **(추론된 갭) 재현의 하드웨어 종속** — 실세계 재현성은 표준화한 물리 rig(특정 arm·카메라·조명·workspace)에 묶여 있습니다. 시뮬 벤치와 리더보드는 공개되나, RoboDojo-RealEval 을 직접 재현하려면 동일 하드웨어 구축이 전제되어 사실상 원격 클라우드 평가로만 접근 가능합니다.
- **(추론된 갭) asset 라이선스 불투명** — asset 이 online repo·Meshy AI 재구성·ClothesNet 등 이질적 출처에서 오며 본문은 통합 라이선스를 명시하지 않습니다. 다운스트림 재사용 전 출처별 라이선스 확인이 필요합니다.

---

## ♻️ 재현성

- **코드 / 벤치마크** — 시뮬 벤치마크와 실세계 평가 플랫폼의 구조 설계를 오픈소스로 공개(`https://github.com/RoboDojo-Benchmark/RoboDojo`, XPolicyLab 별도 코드베이스). 다만 본문은 구체 라이선스(Apache/MIT/CC 등)를 명시하지 않음 — 사용 전 확인 필요.
- **데이터** — 시뮬 3,500 traj(20.66h)·실세계 1,800 traj(17.91h) bimanual 데이터를 정책 통합·학습용으로 공개(25 Hz, head+2 wrist 카메라).
- **리더보드** — `http://robodojo-benchmark.com/leaderboard` 공개(2026-07-03 동결, 지속 업데이트). 게시 조건에 checkpoint·코드·config·재현 지침·평가 영상 공개 + hidden-layout 검증 포함.
- **하드웨어** — 시뮬 8×RTX 4090(+π0.5 추론 A800). 실세계 3개 collaborative bimanual embodiment(ARX X5·Piper·Piper X) + 표준화 RealEval rig, 원격 클라우드 접속.

---

## 🎯 관련 Pillar / Decision (P# / D#)

본 논문은 벤치마크/평가 하니스라 **P0(VLA Datasets & Benchmarks)** 에 가장 직접 닿고, Isaac 스택으로 **P3(Hand-level System0 RL)** 의 시뮬 인프라와, Memory/World-Model 정책 평가로 **P5(World Model)** 에 부차적으로 닿습니다.

- **D26(benchmark/eval scouting scope) — 가장 직접적.** D26 v1 은 "dexterous + contact-rich manipulation 벤치마크와 VLA eval 하니스; sim(ManiSkill/Isaac Lab/Robocasa)과 real(RoboArena-class) 양쪽 추적"을 명시합니다. RoboDojo 는 정확히 그 **sim(Isaac Lab) + real(RoboDojo-RealEval, RoboArena-class 원격) 통합** 후보이며, 5개 능력 차원 진단·hidden-layout anti-gaming·human-teleop 참조까지 갖춘 강한 추적 대상입니다. **단, D26 이 우선하는 "in-hand-rotation / articulated-tool(CATFA precedent)" 은 현 RoboDojo 에 없습니다** — parallel-jaw bimanual 이라 우리 정체성의 dexterous-hand 축을 못 잽니다(→ ⚠️).
- **D27(license/usability bar) — 부분 지지·주의.** 오픈소스 벤치마크 + 공개 데이터셋 + 비영리 거버넌스는 D27 의 permissive 선호와 정렬되나, 본문이 통합 라이선스를 명시하지 않고 asset 출처가 이질적이라 D27 의 "per-dataset license + lineage 기록" 기준으로는 확인 전 ⚠️ 로 취급해야 합니다.
- **P3(D18, System0 sim2real) 부차 연결** — RoboDojo 는 우리 System0 학습 스택과 같은 **Isaac Sim + Isaac Lab**(MASTER §4.2) 위에서 heterogeneous 병렬 시뮬레이션을 구현합니다. 우리 System0 RL 은 정책 평가가 아니라 접촉 안정화 RL 이라 목적은 다르나, "환경마다 독립 장면 구성 + 공유 vectorized 인터페이스"의 병렬화 패턴은 우리 sim 평가/DR 처리량에 참고가 됩니다.
- **P5(D28 world-model role, D30 prediction space) 부차 연결** — Memory 차원은 world-model/예측 정책(X-WAM·GigaWorld-Policy·Fast-WAM·AHA-WAM)이 이론상 유리해야 할 곳입니다. 그러나 §6.1 Finding 5 는 X-WAM 이 Memory SR 4.67%에 그치고 "predictive pretraining 이 temporal continuity 는 도우나 사라진 sparse 증거의 회수·유지엔 부족"하다고 진단합니다 — 우리 P5 베팅(action-conditioned egocentric hand-object WM)에 대한 **외부 falsifier 참조**입니다.

**Identity 긴장** — 우리 정체성의 평가 축은 *dexterous hand + per-finger tactile/force + 접촉 정밀*입니다. RoboDojo 는 *parallel-jaw bimanual + 시각 관측 only* 라, 인프라·방법론 참조로는 유용하나 우리 hand-centric 진단을 대체하지 못합니다(보완 관계, 지지 아님).

**경쟁자/watch 함의** — 직접 경쟁자는 아니며, 향후 dexterous-hand·tactile 확장(§7)이 실제 릴리스되면 P0 의 identity-relevant 벤치마크로 승격 후보가 됩니다(watch trigger).

---

## ✨ 핀 논문 대비 델타

- **vla-eval([arXiv:2603.13966], P0 핀) 대비** — vla-eval 은 *sim-only + success-rate-only* 통합 하니스로 "평가 실행을 싸고 재현 가능하게"에 집중합니다. RoboDojo 의 새로움은 (1) **실세계(RoboDojo-RealEval 원격 클라우드)까지 통합**, (2) **5개 능력 차원 진단**(vla-eval 은 success-rate 단일), (3) **human-teleop 참조 상한**, (4) **hidden-layout anti-gaming**, (5) **학습 데이터셋 동반 공개**입니다. XPolicyLab 는 vla-eval 의 "한 번 통합" 발상을 sim+real 로 확장한 대응물입니다.
- **ManiSkill 3([arXiv:2410.00425], P0 핀) 대비** — ManiSkill 3 은 SAPIEN 기반 고처리량 sim 벤치로 **dexterous hand 를 포함**합니다. RoboDojo 는 Isaac Sim(SAPIEN 아님) 기반이고 실세계를 더하지만 **dexterous hand 가 없어**(parallel-jaw), 역설적으로 우리 identity 의 dexterity 축은 ManiSkill 3 쪽이 더 잘 덮습니다. RoboDojo 의 우위는 sim–real 통합·능력 차원 진단·anti-gaming 거버넌스입니다.
- **요약 델타** — "평가 메트릭을 깊게"가 아니라 "**sim 과 real 을 하나의 인터페이스로 묶고, 능력 축으로 쪼개고, 물리 재현성·anti-gaming 을 리더보드에 제도화**"한 벤치마크. 우리 핀(vla-eval/ManiSkill 3)과 경쟁이 아니라 sim+real 통합·거버넌스 측면에서 상보적입니다.

---

## ⚙️ 의사결정 함의

- **평가 지표: score + success rate 이원화 채택** — RoboDojo 의 핵심 진단 도구는 부분 진행(score)과 이진 완료(SR)의 격차입니다. 우리 in-hand-rotation/tool-articulation 데모 평가에서도 최종 성공률만이 아니라 **sub-step 부분 점수**를 함께 리포트하면 "부분 성공하나 완료 실패" 실패 모드를 잡을 수 있습니다(구체 지표: `sub_step_score` + `success_rate`).
- **능력 차원 분해 리포팅** — 집계 SR 대신 우리 falsifier 도 능력 축(예: 접촉 안정성·pose 정밀·memory·generalization)으로 쪼개 리포트. RoboDojo 의 "차원 평균(task 수 가중 아님)"은 task 수가 많은 축의 지배를 막는 좋은 집계 규칙 — 우리 ablation 집계에 차용 검토.
- **Isaac Lab heterogeneous 병렬화 패턴** — 우리 System0 RL/sim 평가에서 "환경마다 독립 장면 구성 + 공유 vectorized step"을 적용하면 clutter/DR 다양성을 유지하며 처리량을 올릴 수 있습니다(RoboDojo zero-action 1.94배 참조). 구체 lever: env 클론 대신 per-env scene config 샘플링.
- **anti-gaming: hidden-layout 예약** — 우리 sim ablation config 도 학습·튜닝에서 격리된 **held-out layout 집합**을 예약해, overfitting 을 우리 자체 검증에 내장.
- **데이터 포맷 참조** — 25 Hz·head+2 wrist·640×480·robot state 이원(EE pose + joint) 은 우리 실로봇 수집 스키마의 참조점(단, 우리는 여기에 per-finger tactile/force 채널을 추가해야 함 — RoboDojo 에 없는 축).
- **P5 falsifier 참조 고정** — action-conditioned WM 을 우리 stack 에 넣을 때, RoboDojo-Memory 유형의 sparse-evidence-recall task 는 WM 이득이 나타나야 할 곳입니다. 현 WM 정책의 낮은 Memory SR(X-WAM 4.67%)을 "아직 미해결" 기준선으로 기록.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 체크) dexterous hand·tactile 부재로 우리 identity 축 측정 불가** — RoboDojo 는 ARX X5/Piper *parallel-jaw* bimanual + 시각 관측 only 입니다. 5분 체크: task 목록(`insert_tubes`·`stack_bowls`·`hang_mugs` 등)이 모두 gripper 조작인지, tactile/force 채널이 관측에 있는지 확인 → 없음 확정 → "우리 hand-centric 평가 벤치로는 부적합, 인프라/방법론 참조로만 활용" 전제로 사용.
- **성능 floor effect** — 최고 SR 이 한 자릿수라, 우리가 정책을 통합해 돌려도 baseline SR 이 노이즈 바닥(안정성 표의 task 분산 1~2pp 수준)에 눌릴 위험. 채택 전 체크: 우리 대상 task 의 baseline SR 이 seed 간 표준편차보다 유의하게 높은가? 아니면 delta 검출 불가.
- **RoboDojo-RealEval 하드웨어 종속** — 실세계 평가는 표준화 rig(특정 arm·카메라·조명)를 전제로 하고 원격 클라우드로만 접근. 우리 Sharpa/xhand 기반 hand-centric rig 와 embodiment 가 달라 실세계 재현은 불가, 리더보드 소비만 가능.
- **Isaac 버전·asset 재사용성** — 우리 System0 스택과 같은 Isaac Sim/Lab 이지만 MagicSim/cuRobo v2 의존·asset 라이선스(Meshy AI/ClothesNet)가 우리 쪽으로 그대로 이식 가능한지 불명. 병렬화 패턴은 아이디어 수준 차용, 코드 직수입은 비용 검증 후.
- **라이선스 게이트** — 본문에 통합 라이선스 미명시. 데이터셋/코드 사용 전 GitHub repo 의 실제 LICENSE 확인(D27 usability bar) — 미확인 상태로는 downstream 사용 금지.

---

## 💡 컨텍스트 제안

- **P0 §5 핀 후보(D26)** — RoboDojo 를 vla-eval·ManiSkill 3 과 함께 "sim+real 통합 벤치마크" 레퍼런스로 §5 추적 검토 제안. 역할: "Isaac Lab sim + RoboDojo-RealEval 원격 real, 5개 능력 차원 진단, hidden-layout anti-gaming, human-teleop 상한". **제약 명시: parallel-jaw only → dexterous-hand identity 에 부분 적합** (현 8핀 한도 내 교체 여부는 사람 판단).
- **D26 노트 보강 제안** — D26 v1 의 "real(RoboArena-class)" 옆에 "RoboDojo-RealEval(원격 클라우드 표준화 rig, 3 embodiment) = sim+real 통합 real 후보; 단 dexterous hand 없음" 한 줄 추가 검토.
- **watch trigger 등록 제안** — §7 확장 로드맵(dexterous hand·tactile·humanoid·mobile)이 실제 릴리스되면 P0 identity-relevant 벤치로 재평가. tactile 축이 붙는 순간 P2/P3 연결도 발생.
- context/MASTER.md·context/P0.md 는 수정하지 않았습니다 — 위는 모두 제안입니다.
