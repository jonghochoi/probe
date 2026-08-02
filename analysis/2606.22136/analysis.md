# Paper Analysis — Wh0: Generative World Models as Scalable Sources of Egocentric Human Hand Manipulation Data

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Wh0: Generative World Models as Scalable Sources of Egocentric Human Hand Manipulation Data |
| 저자 | Yangtao Chen, Zixuan Chen, Peiyang Wang, Yong-Lu Li, Jing Huo, Jieqi Shi, Yang Gao (Shanghai Innovation Institute · Nanjing University · Shanghai Jiaotong University) |
| 링크 | [arXiv:2606.22136](https://arxiv.org/abs/2606.22136) · [Website](https://chenyt31.github.io/wh0.github.io/) |
| 발행일 / 버전 | 2026-06-20 · v2 (2026-06-23) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-08-02 |
| 관련 Pillar | P5, P4, P0, P1 |
| 태그 | egocentric-data, dataset, dexterity |

<!-- 본문 확보 이력 (verbatim):
       1. curl --fail -sS "https://arxiv.org/abs/2606.22136"   → HTTP 200 (메타/초록/버전 이력 확보)
       2. curl --fail -sS "https://arxiv.org/html/2606.22136"  → HTTP 200 (261 KB, 본문 + 부록 A–C 전문)
     전문(arXiv HTML) 확보이므로 (B) 섹션에 (본문 미확보) 마커를 붙이지 않습니다.
     `링크` 행의 Website 는 초록 마지막 문장에 원문 그대로 기재된 프로젝트
     페이지입니다. 다만 curl -L "https://chenyt31.github.io/wh0.github.io/" 는
     이 실행 환경의 프록시에서 `curl: (56) CONNECT tunnel failed, response 403`
     으로 차단되어 실제 도달 여부를 확인하지 못했습니다(호스트 정책 차단이며
     404 아님). GitHub / HuggingFace 링크는 논문 본문에 명시되지 않아 생략합니다. -->

---

## 🧭 한 줄 요약 (TL;DR)

세상을 시뮬레이션하는 대신 **데이터를 찍어내는 공장**으로 생성 비디오 world model 을 쓰자는 논문입니다. 배포 로봇의 실제 작업대 사진을 초기 프레임으로 삼아 egocentric 사람 손 조작 영상 50k 편(WM-H)을 합성하고, 손 재구성으로 3D 액션 라벨을 붙인 뒤 실로봇 teleoperation 400 건과 co-training 하여, 18개 실세계 다지 조작 태스크에서 VITRA baseline 의 zero-shot 성공률을 8.3% → 38.9% 로 끌어올립니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 다지(dexterous) 조작을 객체·장면·태스크에 걸쳐 일반화시키려면 대규모 데이터가 필요한데, 현존 데이터 원천은 모두 *규모* 와 *배포 정합성* 중 하나를 포기합니다. 이 트레이드오프 자체를 깨는 새 데이터 원천을 만드는 것이 목표입니다.
- **기존 접근의 한계** — teleoperation 은 배포와 정합하지만 비싸고 플랫폼 종속적이며, 시뮬레이션은 확장되지만 sim-to-real gap 이 남고, 실제 egocentric 영상은 확장되지만 **scene gap**(일상 환경 ≠ 로봇 작업 공간)과 **embodiment gap**(사람 손 ≠ 로봇 다지 손)이 그대로 남습니다.
- **본 논문의 가설** — 생성 비디오 world model 의 가치는 로봇 동역학을 정확히 시뮬레이션하는 데 있지 않고, 언어·객체·장면을 조건으로 **다양한 사람-객체 상호작용 영상을 주문형으로 생성**하는 데 있습니다. 따라서 장면·객체·태스크·손 외형을 *설계 변수* 로 놓으면, 데이터 규모가 사람의 노동이 아니라 GPU 연산에 비례해 늘어납니다.
- **왜 지금 중요한가** — Wan-I2V, Qwen-Image-Edit, Qwen3-VL 같은 상용급 생성/편집 모델과 HaWoR 급 egocentric 손 재구성기가 동시에 성숙해, "생성 → 편집 → 라벨링" 전 구간을 사람 개입 없이 자동화할 수 있게 되었습니다.
- **차별점(선행 world-model 활용과의 구분)** — 기존 연구가 world model 을 환경 동역학 시뮬레이터, 로봇 궤적 비디오 생성기, retargeting 용 손 생성기, 미래 예측 정책의 백본으로 썼다면, 본 논문은 오직 **제어 가능한 사람 손 데이터 생성기**로만 씁니다.

---

## 🧩 핵심 기여

- **World model 의 역할 재정의** — 생성 비디오 world model 을 dexterous VLA 의 *post-training 데이터 공급원* 으로 정식화하고, 그 확장성이 사람 노동이 아니라 GPU 연산에 묶인다는 점을 비용 수치(1k 영상당 5.44 GPU-hour)와 함께 제시합니다.
- **WM-H 데이터셋** — egocentric 조작 영상 + 언어 지시 + 3D 손 모션 주석으로 구성된 50k 샘플 데이터셋. 명사 h-index 201, 형용사 h-index 117 로 어휘 폭과 빈도 커버리지를 동시에 확보합니다.
- **배포 정합 2축 설계** — (a) **scene alignment**: 배포 카메라·시점·해상도로 촬영한 실제 작업대 이미지를 초기 프레임으로 강제, (b) **embodiment alignment**: 생성된 사람 손 프레임 일부를 로봇 손 외형으로 편집해 같은 궤적을 두 외형으로 렌더링. 두 축 모두 ablation 으로 기여도가 분리 측정됩니다.
- **실세계 검증** — Unitree G1 + Inspire hands, 18개 태스크 × 20 trial zero-shot 평가에서 teleop-only post-training 대비 8.3% → 38.9% (4.7배). 실제 egocentric 영상(HOI4D)으로 co-train 한 변형(21.4%)보다도 높습니다.
- **사전학습 prior 해금(unlock) 분석** — WM-H 는 다지 스킬을 처음부터 학습시키는 것이 아니라, **사람 영상 사전학습이 이미 갖고 있던 조작 prior 를 활성화·정렬**한다는 3원 ablation(사전학습 × teleop × WM-H)을 제시합니다.

---

## 🔑 기술 키워드

- **Generative video world model** — 언어·이미지 조건으로 미래 영상을 만들어내는 생성 모델. 본 논문에서는 "다음에 무슨 일이 일어날지 예측하는 물리 엔진"이 아니라 "주문한 장면을 찍어주는 촬영 스튜디오"로 쓰입니다.
- **WM-H** — 그 스튜디오가 찍어낸 50k 편짜리 egocentric 사람 손 조작 영상 데이터셋(언어 지시 + 3D 손 포즈 주석 포함).
- **Scene alignment** — 생성 영상의 배경을 *실제 배포 작업대 사진* 으로 못 박는 장치. 촬영 시 사람 손을 관심 영역에 놓아 손 크기·객체 스케일·카메라 거리의 기준자(scale anchor) 역할을 하게 합니다.
- **Embodiment alignment** — 같은 조작 궤적을 사람 손 외형과 로봇 손 외형 두 벌로 렌더링해, 정책이 "누가 하는가"가 아니라 "무슨 동작인가"에 집중하게 만드는 외형 불변성 장치.
- **MANO action space** — 사람 손 파라메트릭 모델(15-DoF 관절 회전 + 손목 pose)로 정의한 공용 액션 공간. 사람과 로봇이 같은 좌표계로 말하게 만들어 retargeting 을 학습 밖으로 밀어냅니다.
- **HaWoR** — egocentric 영상에서 손을 검출하고 MANO 파라미터 + 손목 pose 를 회귀하는 손 모션 재구성기. 생성 영상에 *사후* 액션 라벨을 붙이는 라벨러입니다.
- **Hand-Object Distance (HO)** — 정책이 예측한 손목 액션과 추정된 목표 객체 위치 사이 거리(cm). 태스크 성공률의 대체 지표가 아니라 "언어 조건 객체 grounding" 프록시입니다.
- **Instruction h-index** — 지시문 다양성 지표. $`h`$ 라면 최소 $`h`$ 개 단어가 각각 최소 $`h`$ 개 샘플에 등장한다는 뜻으로, 어휘 *수* 만 늘리는 방식과 달리 빈도 커버리지까지 강제합니다.
- **Co-finetuning (Co-FT)** — 여러 데이터 원천을 한 배치 안에서 비율로 섞어 동시에 fine-tuning 하는 방식. 단일 원천 fine-tuning(FT)과 표에서 명시적으로 구분됩니다.
- **VITRA** — 대규모 실생활 사람 활동 영상으로 사전학습한 VLA. 본 논문의 초기화 가중치이자 주 비교 baseline 입니다 ([arXiv:2510.21571](https://arxiv.org/abs/2510.21571)).

---

## 🔬 방법론

### 직관

이 논문의 출발점은 "world model 을 로봇 시뮬레이터로 쓰지 말자"는 다소 도발적인 선택입니다. 생성 비디오 모델에게 정확한 접촉 물리를 기대하면 실망하지만, 부엌 조명 아래 사람 손이 사과를 집어 통에 넣는 장면을 *그럴듯하게 무한히* 만들어 달라고 하면 잘 해냅니다. 그래서 저자들은 물리 정확도를 요구하는 대신, 다양성과 제어 가능성만 가져다 쓰기로 합니다.

문제는 그렇게 만든 영상을 그대로 학습에 쓰면 기존 egocentric 영상과 똑같은 두 개의 간극이 남는다는 점입니다. 첫째, 배경이 우리 로봇의 작업대가 아닙니다. 둘째, 화면 속 손이 로봇 손이 아닙니다. 이 논문의 핵심 조작은 이 두 간극을 *생성 단계에서 설계 변수로 바꿔버리는* 것입니다. 배경은 실제 배포 카메라로 찍은 우리 작업대 사진을 초기 프레임으로 넣어 고정하고(scene alignment), 손은 다 만들어진 영상의 일부 프레임에서 외형만 로봇 손으로 갈아끼웁니다(embodiment alignment). 후자가 특히 영리한데, 포즈·위치·객체 운동·장면 구성을 그대로 두고 외형만 바꾸므로 **동일한 궤적에 대한 두 벌의 시각적 표현**이 공짜로 생깁니다. 정책 입장에서는 "손 모양이 바뀌어도 같은 액션"이라는 불변성을 직접 배우게 되는 셈입니다.

액션 라벨은 어디서 올까요. 생성된 것은 픽셀뿐이므로 라벨이 없습니다. 여기서 저자들은 "왜 로봇 손 영상이 아니라 사람 손 영상을 생성하는가"라는 질문에 답합니다. 사람 손 재구성 기술은 이미 성숙해 있어서, 만들어진 영상에 손 재구성기를 돌리면 3D 손 모션을 꽤 신뢰성 있게 뽑아낼 수 있습니다. 즉 **생성은 사람 손으로, 라벨링은 기성 재구성기로, 외형만 로봇으로** — 이 세 갈래 분업이 파이프라인 전체를 자동화 가능하게 만드는 지점입니다.

마지막으로 이 데이터를 어떻게 쓰느냐가 남습니다. 합성 데이터만으로 학습하면 배포 로봇 고유의 제약(실제 관절 한계, 실제 카메라 노이즈, 실제 접촉)이 빠집니다. 그래서 400 건의 실제 teleoperation 데이터를 함께 섞되, 데이터 *양* 은 125:1 로 합성 쪽이 압도적인 반면 배치 *샘플링 비율* 은 로봇 데이터를 크게 오버샘플링합니다. 실험이 최종적으로 보여주는 그림은, WM-H 가 새 손재주를 가르치는 것이 아니라 **사람 영상 사전학습이 이미 품고 있었지만 소량 로봇 데이터로는 꺼낼 수 없던 능력을 꺼내주는 열쇠** 라는 것입니다.

### 데이터 생성 파이프라인 (WM-H)

파이프라인의 설계 원칙은 한 문장으로 못 박혀 있습니다.

> "The scalability of the pipeline mainly depends on GPU compute rather than human labor." (§3)
(사람의 촬영·주석 노동이 병목이 아니라 GPU 시간이 병목이라는 선언입니다. 데이터 규모를 늘리는 행위가 "사람을 더 고용한다"에서 "카드를 더 돌린다"로 바뀌는 것이 이 논문이 파는 가치의 본체입니다.)

![Figure 2 — WM-H data synthesis pipeline](https://arxiv.org/html/2606.22136/x2.png)

> "Figure 2: The overview of WM-H data synthesis pipeline." (§3)
(지시문 생성 → 장면 정렬 이미지 편집 → image-to-video 생성 → 로봇 손 편집 → 손 모션 추출의 5단계 흐름을 한 장에 보여줍니다.)

- **(1) 지시문 생성 — 이중 에이전트** — 첫 번째 에이전트가 LLM 으로 파지 가능한 객체 명사와 속성 형용사를 계속 발굴해 후보 어휘 풀을 넓히고, 두 번째 에이전트가 **저빈도 단어를 우선 샘플링** 해 `pick the {adj} {noun}` 같은 구조 템플릿으로 지시문을 조립합니다. 데이터베이스가 단어 사용 빈도를 추적하고 중복 지시문을 거릅니다(§A.1: 모든 기존 단어가 최소 사용 임계치에 도달했을 때만 어휘 확장이 트리거됨). 그 결과가 다음 수치입니다.

  > "Despite being much smaller than large-scale human video datasets [30, 19, 42, 24], WM-H achieves broad manipulation-relevant coverage, with a noun h-index of 201 and an adjective h-index of 117 across pick, place, and grasp instructions." (§3)
  (h-index 를 다양성 지표로 쓴 것은 "희귀어 롱테일로 어휘 수만 부풀리기"를 막기 위해서입니다. 명사 201 은 최소 201개 명사가 각각 최소 201개 샘플에 등장했다는 뜻이라, 폭과 깊이가 동시에 보장됩니다.)

- **(2a) 장면 정렬 이미지 편집** — 배포 작업 공간의 배경 이미지를 **배포 카메라로, 정책 입력과 동일한 시점·해상도** 로 촬영합니다. 촬영 시 관심 상호작용 영역에 사람 손을 하나 놓아둡니다.

  > "During capture, we place a human hand in the target interaction region as a scale anchor, providing references for hand size, object scale, and camera-to-workspace distance." (§3)
  (생성 모델은 절대 스케일 개념이 없어 손이 접시만 하게 나오기 쉽습니다. 프레임 안에 실제 손을 미리 넣어두면 이후 생성이 그 크기를 기준으로 자기 정합을 맞추므로, 별도 카메라 캘리브레이션 없이 스케일을 주입하는 값싼 트릭입니다.)

  이후 Qwen-Image-Edit 으로 지정 객체를 장면에 삽입해 초기 프레임을 만듭니다. 편집 위치를 국소화하기 위해 이미지에 사각 가이드 영역을 그리고(중심은 도달 가능 영역 내에서 무작위 샘플, 다중 객체는 겹치지 않게 순차 샘플), 그 사각형은 최종 이미지에서 제거됩니다. 적은 편집 스텝 + 낮은 CFG scale + Lightning LoRA 가속을 씁니다(§A.2).

- **(2b) Image-to-video 생성** — Wan-I2V-A14B 로 편집된 이미지를 애니메이션합니다. 생성 모션의 정확도를 높이기 위해 Qwen3-VL 로 "기대되는 손-객체 상태 변화" 서술을 만들어 비디오 프롬프트 뒤에 덧붙입니다. 카메라는 고정, 1인칭 top-down 시점, 단일 작용 손이 프레임 하단에서 진입하며, 동작 완료 후 손은 정지하도록 프롬프트에 명시됩니다(§A.3). 대규모 합성을 위해 **LightX2V LoRA 어댑터로 추론을 4 스텝** 까지 줄입니다.

- **(2c) 로봇 손 편집** — embodiment alignment 의 실체입니다.

  > "For embodiment alignment, we treat a robotic dexterous hand as a hand entity with a different visual appearance." (§3)
  (로봇 손을 "다른 운동학을 가진 다른 기계"가 아니라 "외형만 다른 손"으로 취급하겠다는 선언입니다. 이 환원이 성립하는 덕분에 문제 전체가 이미지 편집으로 축소됩니다.)

  > "This renders the same manipulation trajectory with both human and robot hand appearances, encouraging the policy to focus on action semantics rather than executor identity." (§3)
  (같은 궤적의 짝(pair)을 만들기 때문에, 정책은 외형 변화에 대해 액션 표현이 변하지 않도록 압력을 받습니다. §5.3 의 action-feature cosine similarity 측정이 바로 이 불변성을 직접 잽니다.)

  구현은 고정 간격·고정 오프셋으로 프레임을 성기게(sparsely) 샘플해 각 프레임을 독립적으로 Qwen-Image-Edit 에 넣는 방식이며, 편집 대상은 손 외형으로 제한됩니다(포즈·위치·스케일·배경·구성 유지). 목표 외형은 "흰 등껍질, 검은 손바닥, 검은 손끝, 은색 로봇 전완"으로 명시되고, 만화/플라스틱/CGI 느낌을 억제하는 negative prompt 가 함께 걸립니다(§A.4).

- **(3) 모션 추출** — 생성된 사람 손 영상에서 3D 손 포즈를 액션 라벨로 추출합니다. 왜 로봇 손이 아니라 사람 손을 생성하는지의 근거가 여기 있습니다.

  > "Generating human rather than robot manipulation videos is important here: human hand reconstruction is comparatively mature, making it feasible to recover reliable motion supervision from generated videos at scale." (§3)
  (파이프라인이 성립하는 진짜 이유는 생성 품질이 아니라 **라벨러의 성숙도** 입니다. 로봇 손 영상을 직접 생성했다면 대규모로 신뢰할 만한 액션 라벨을 붙일 방법이 없었을 것입니다.)

  HaWoR 가 프레임마다 손을 검출한 뒤 MANO 파라미터와 손목 pose 를 회귀하며, 손목 pose 는 카메라 공간에, 관절 pose 는 MANO 파라미터 공간에 둡니다. 필요 시 MegaSAM 의 카메라 트래킹으로 프레임별 예측을 비디오 카메라 궤적에 결합합니다.

### 아키텍처

![Figure 3 — Policy architecture and data composition](https://arxiv.org/html/2606.22136/x3.png)

> "Figure 3: Policy architecture and data composition. Top: A VITRA-style policy denoises actions in the unified MANO space, conditioned on PaliGemma cognition features, FoV, and current hand state. Bottom: Pretraining mixture (VITRA-1M, Ego4D-dominant) and post-training mixtures: Wh0 uses 28% teleop and 68% WM-H, heavily oversampling robot data per-sample given 400 teleop vs. 50k WM-H samples." (§4)
(위쪽이 정책 구조, 아래쪽이 사전학습/사후학습 데이터 믹스를 나란히 보여주는 그림으로, 이 논문에서 "아키텍처"보다 "데이터 구성"이 더 큰 설계 변수임을 시각적으로 드러냅니다.)

정책은 VITRA 계열 VLA 를 그대로 채택합니다. PaliGemma 비전-언어 백본이 현재 관측과 언어 지시를 인코딩하고(시점 단서를 위한 보조 토큰으로 FoV 를 함께 넣음), 그 특징이 diffusion 기반 액션 디코더를 조건화해 현재 손 상태로부터 미래 손 모션을 예측합니다. 부록의 구현 세부는 다음과 같습니다(§B.1).

- **백본** — PaliGemma2-3B. 2D FoV 토큰을 MLP 로 백본 hidden size 에 사영해 입력 시퀀스에 포함.
- **cognition token** — 별도의 학습 가능한 토큰을 입력에 덧붙이고, 그 최종 hidden state 를 액션 디코더의 조건 특징으로 뽑습니다.
- **상태 표현** — 카메라 프레임에서 손목 translation + Euler angle + 손별 15-DoF MANO 관절 회전(본 연구는 오른손 중심).
- **액션 디코더** — diffusion 기반 **DiT-B**, chunk 당 미래 16 스텝 예측, 액션 차원 102 (MANO 손 공간).

액션 공간은 현재 관측 $`o_{t}`$ 의 카메라 좌표계에서 다음과 같이 정의됩니다 (식 1).

$$a_{t}=[\Delta t^{l},\Delta r^{l},\theta_{h}^{l},\Delta t^{r},\Delta r^{r},\theta_{h}^{r}]\in\mathbb{R}^{102}$$

여기서 $`\Delta t,\Delta r\in\mathbb{R}^{3}`$ 는 연속 프레임 사이의 상대 손목 translation 과 rotation(Euler angle), $`\theta_{h}\in\mathbb{R}^{15\times 3}`$ 는 15-DoF MANO 손 모델의 국소 프레임 관절 회전입니다. 위첨자 $`l,r`$ 은 좌/우 손을 뜻하며 본 논문은 오른손 조작에 집중합니다.

사람-로봇 정합의 핵심은 정규화 통계를 어디서 가져오느냐입니다.

> "We retarget robot joints to MANO and reuse the per-joint normalization parameters precomputed by VITRA [30] from large-scale human videos. This avoids robot-specific normalization from limited data and keeps robot actions aligned with the human action space." (§4)
(400건짜리 로봇 데이터로 정규화 통계를 내면 그 통계 자체가 소표본 노이즈에 오염되고, 더 나쁘게는 사전학습된 사람 액션 분포와 좌표가 어긋나 prior 가 무력화됩니다. 사람 영상에서 미리 계산된 통계를 그대로 재사용하는 선택은 "로봇 데이터를 사람 공간으로 끌어올린다"는 이 논문의 정합 전략을 정규화 층위에서 관철한 것입니다.)

§B.2 는 여기에 세부를 덧붙입니다. 로봇 시연의 상태·액션은 먼저 로봇 base 프레임에서 카메라 프레임으로 변환되고, 손목 회전은 MANO 규약에 맞게 보정되며, 로봇 관절각은 사람 손/MANO 공간으로 retarget 됩니다. 정책 내부적으로는 상태·액션이 통합 VITRA 공간(state 차원 212, action 차원 102)으로 padding 되지만 **사람 손 관련 차원만 활성** 입니다.

### 학습 목표 / 손실

diffusion 액션 디코더는 noise-prediction MSE 손실로 학습됩니다 (식 2).

$$\mathcal{L}_{\mathrm{MSE}}=\mathbb{E}_{\epsilon\sim\mathcal{N}(0,1),\,i}\left[\left\|\hat{\epsilon}_{i}-\epsilon\right\|_{2}^{2}\right]$$

여기서 $`\hat{\epsilon}_{i}`$ 는 diffusion 스텝 $`i`$ 에서 예측된 노이즈입니다. 손실 자체에는 어떠한 정합 항(alignment term)·대조 항·정칙화 항도 추가되지 않습니다 — 즉 **scene / embodiment alignment 는 손실 함수가 아니라 데이터 분포로만 구현** 되며, 이는 이 논문이 알고리즘이 아니라 데이터 레시피 논문임을 보여주는 가장 분명한 신호입니다.

### 학습 셋업

- **초기화** — VITRA 사전학습 가중치. VITRA 는 Ego4D, Epic-Kitchens, EgoExo4D, Something-Something-V2 로 사전학습되어 사람 손-객체 상호작용에 대한 강한 prior 를 갖습니다(§4).
- **데이터 믹스** — 다음 문장이 사후학습 레시피의 전부입니다.

  > "We then co-finetune on a 125:1 mixture of 50k WM-H samples and 400 real teleoperated robot demonstrations." (§4)
  (데이터 *보유량* 비가 125:1 이라는 뜻이며, 배치 *샘플링* 비율은 그와 정반대 방향으로 로봇 데이터를 끌어올립니다. 두 숫자를 혼동하면 레시피를 잘못 재현하게 되는 지점입니다.)

  배치 구성은 teleop 28% / WM-H 68% / WM-H EA 4% (EA = embodiment alignment 를 위해 로봇 손으로 편집된 WM-H 프레임)입니다. 저자들의 해석은 희소한 로봇 데이터를 오버샘플링해 embodiment 특이 신호를 안정적으로 공급하고, WM-H 는 일반화에 필요한 시각·의미 다양성을 공급한다는 것입니다.
- **최적화** — 비전 인코더는 동결하고 나머지 백본 + diffusion 액션 디코더를 갱신합니다. learning rate $`1\times 10^{-5}`$ (백본·디코더 공통), weight decay `0.1`, optimizer betas $`(0.9,0.95)`$, gradient clipping `1.0`, 최대 `40k` 스텝. 이미지 증강은 적용하지 않습니다(§B.3).
- **하드웨어** — NVIDIA H200 4장, GPU 당 배치 64 → 총 배치 256.
- **diffusion 설정** — 학습 시 100 diffusion step, squared-cosine 노이즈 스케줄.

  > "For each batch, we repeat diffusion training 8 times with independently sampled noise and timesteps." (§B.3)
  (같은 배치를 8번 반복하며 노이즈·타임스텝만 새로 뽑는 방식으로, 데이터 로딩 비용을 늘리지 않고 diffusion 목적의 유효 샘플 수를 8배로 늘리는 값싼 장치입니다. 400건짜리 로봇 데이터를 다루는 소데이터 레짐에서 특히 의미가 큽니다.)
- **추론** — RTX 4090 한 장, DDIM 샘플링 10 스텝, classifier-free guidance scale `5.0`.
- **생성 비용** — 1k 영상당 약 5.44 GPU-hour.

---

## 📊 실험 설정과 결과

### 실험 설정

- **로봇 플랫폼** — Unitree G1 휴머노이드 + Inspire 다지 손 + 머리 장착 egocentric 카메라. 모든 비교 방법이 동일 하드웨어·카메라·저수준 제어 인터페이스를 공유합니다(§5.1).
- **학습 데이터** — Apple Vision Pro 로 수집한 전문가 궤적 400건(seen 태스크·배경, 주로 pick-and-place).
- **평가 프로토콜** — 4개 장면에 걸친 18개 태스크(파지 / 놓기 / 객체 특이 상호작용), 태스크당 20 trial, 객체 pose 와 장면 무작위화, 주 지표는 성공률. 모든 정책은 **태스크별 시연 없이 zero-shot** 평가됩니다.
- **평가 태스크 목록** — 삼각대 파지, 콜라 캔을 검은 상자에, 로봇 그리퍼 터치, 장갑을 주황 통에, 종이컵 파지, 물병을 파란 볼에, 사과를 주황 통에, 사과를 주황 통에서 꺼내기, 수건 파지, 주전자를 주황 통에, 테이블 닦기, 흰-초록 음료를 서랍에, 콜라 캔을 서랍에, 리모컨 파지, 빵 파지, 티슈를 노란 바구니에, 사과를 노란 바구니에, 줄자 파지 (§C.1).
- **평가 프로토콜의 두 단서** — (a) 다단계 태스크에는 **stage-conditioned instruction** 을 씁니다. 평가자가 현재 손-객체 상태(reaching/grasping/placing)에 맞는 다음 지시문만 제공하며 수동 제어·액션 보정은 없습니다. (b) 배포 시 모든 방법에 공통으로 **grasping prior** 를 겁니다.

  > "We therefore apply a simple grasping prior during the pre-contact phase: finger joints are constrained to move monotonically toward closure until a stable grasp is reached." (§C.1)
  (고차원 손 액션의 단기 노이즈로 물체 근처에서 손이 되열리는 현상을 억제하는 규칙 기반 보정입니다. 모든 비교군에 동일 적용되므로 상대 비교는 공정하지만, 보고된 절대 성공률에는 정책이 아닌 이 규칙의 기여가 섞여 있습니다.)
- **HO 평가셋** — LLM 으로 unseen 지시문을, 이미지 편집 모델로 unseen 객체를 합성해 구성하고, world-model 궤적에서 3D 목표 객체 위치를 추정합니다. 잘못된 에피소드를 수동 필터링한 뒤 최종 약 5k 에피소드입니다(§C.2).

### Q1 — 실세계 zero-shot 성능 (Table 1)

| Method | Pretraining | Adaptation Data | Strategy | Success Rate (%) ↑ |
|---|---|---|---|---|
| $`\pi_{0.5}`$ | Robot | Teleop | FT | $`7.78_{\scriptscriptstyle\pm 15.6}`$ |
| VITRA | Human | Teleop | FT | $`8.3_{\scriptscriptstyle\pm 8.6}`$ |
| VITRA Real Version | Human | Teleop + Real Ego | Co-FT | $`21.4_{\scriptscriptstyle\pm 23.4}`$ |
| Wh0 | Human | Teleop + WM-H | Co-FT | $`\mathbf{38.9}_{\scriptscriptstyle\pm 19.8}`$ |

> "On a Unitree G1 humanoid with Inspire dexterous hands, under zero-shot evaluation, the strong VLA baseline VITRA [30] post-trained only on robot data without test-task demonstrations achieves an 8.3% success rate, while co-training with WM-H improves it to 38.9%, a 4.7 $`\times`$ gain." (§1)
(헤드라인 수치입니다. 다만 baseline 8.3% 는 "강한 VLA"라는 수식에 비해 절대치가 매우 낮아, 이 평가 셋업 자체가 zero-shot 으로는 대단히 어렵다는 사실도 함께 읽어야 합니다.)

> "The conventional paradigm adapts pretrained policies via robot post-training alone, but $`\pi_{0.5}`$ and VITRA show limited instruction-following in our experiments, suggesting that post-training on limited robot data overfits to seen tasks and weakens pretraining generalization." (§5.2)
(400건 규모의 post-training 이 *능력을 더하는* 것이 아니라 *일반화를 깎는* 방향으로 작동한다는 진단입니다. 이 진단이 맞다면 문제는 데이터 부족이 아니라 **소데이터 사후학습의 과적합** 이며, 해법도 "로봇 데이터를 더 모은다"가 아니라 "사후학습 분포를 넓힌다"가 됩니다.)

- **VITRA Real Version 의 위치** — WM-H 대신 실제 egocentric 사람 손 영상(HOI4D)으로 co-train 한 변형이며, 21.4% 로 teleop-only 대비 크게 개선되지만 Wh0(38.9%)에는 미치지 못합니다. §B.4 에 따르면 HOI4D 는 100 프레임 단위를 한 에피소드로 묶어 언어 주석 1개를 부여하는 방식으로 5,511 에피소드를 만들고, 로봇 데이터와 `1:1` 균형 믹스로 학습합니다. 즉 이 비교는 "합성 ego 데이터 vs 실촬 ego 데이터"를 **동일 co-train 프레임 안에서** 직접 대질한 셈이라, 본 논문에서 가장 가치 있는 비교군입니다.
- **$`\pi_{0.5}`$ 의 표준편차 ±15.6** — 평균 7.78% 에 비해 편차가 두 배 이상이라, 18개 태스크 중 극소수에서만 성공하고 나머지는 0에 가깝다는 분포를 시사합니다.

### Q2 — WM-H 의 어떤 속성이 중요한가 (Table 2)

| Variant | HO (human) ↑ | HO (robot) ↑ | Task Succ. ↑ |
|---|---|---|---|
| No model | $`18.9_{\scriptscriptstyle\pm 2.8}`$ | $`18.9_{\scriptscriptstyle\pm 2.8}`$ | – |
| Teleop only | $`16.2_{\scriptscriptstyle\pm 3.3}`$ | $`16.2_{\scriptscriptstyle\pm 3.3}`$ | $`8.3_{\scriptscriptstyle\pm 8.6}`$ |
| w/o scene align. | $`14.9_{\scriptscriptstyle\pm 2.7}`$ | $`14.3_{\scriptscriptstyle\pm 2.5}`$ | $`20.0_{\scriptscriptstyle\pm 24.7}`$ |
| w/o emb. align. | $`\mathbf{10.2}_{\scriptscriptstyle\pm 2.5}`$ | $`13.8_{\scriptscriptstyle\pm 3.6}`$ | $`34.7_{\scriptscriptstyle\pm 18.0}`$ |
| WM-H 5k | $`11.9_{\scriptscriptstyle\pm 2.8}`$ | $`10.5_{\scriptscriptstyle\pm 3.2}`$ | $`27.8_{\scriptscriptstyle\pm 21.8}`$ |
| WM-H 25k | $`11.4_{\scriptscriptstyle\pm 2.5}`$ | $`9.9_{\scriptscriptstyle\pm 2.6}`$ | $`32.5_{\scriptscriptstyle\pm 23.5}`$ |
| Wh0 (50k) | $`10.6_{\scriptscriptstyle\pm 2.0}`$ | $`\mathbf{9.6}_{\scriptscriptstyle\pm 1.8}`$ | $`\mathbf{38.9}_{\scriptscriptstyle\pm 19.8}`$ |

> "Table 2: Ablation Study: effects of deployment alignment and WM-H scale on robot-object grounding and task success. HO = Hand-Object Distance (cm)." (§5.3, Table 2)
(HO 는 cm 단위 거리라 낮을수록 좋은 지표인데, Table 2 헤더의 화살표는 ↑ 로 표기되어 있습니다. §C.2 의 서술과 Table 3 의 ↓ 표기를 함께 보면 **낮을수록 좋음** 이 맞으며, Table 2 의 ↑ 는 원문 표기 그대로 옮겨둔 것입니다.)

> "Lower distance indicates better instruction-conditioned object grounding." (§C.2)
(방향성의 근거 문장입니다.)

행별 판독:

- **`No model` (18.9)** — 정책 없이 초기 pose 를 그대로 둔 기준선. 모든 grounding 수치는 이 값에서 얼마나 내려왔는지로 읽어야 합니다.
- **`Teleop only` (16.2 / 8.3%)** — 400건 사후학습만으로는 grounding 이 18.9 → 16.2 로 겨우 2.7 내려갑니다. 사실상 언어 조건 객체 지향이 거의 학습되지 않았다는 뜻입니다.
- **`w/o scene align.` (14.9 / 14.3 / 20.0%)** — 장면 정합을 뺐을 때 손-객체 상호작용 패턴은 여전히 공급되므로 성공률은 8.3% → 20.0% 로 오르지만, 장면 분포와 시점이 배포와 어긋나 grounding·성공률 모두 상한이 눌립니다. **scene alignment 의 기여분은 20.0 → 38.9 (약 19점)** 로 두 정합 축 중 더 큽니다.
- **`w/o emb. align.` (10.2 / 13.8 / 34.7%)** — 이 행이 가장 해석이 풍부합니다. 사람 손 외형에서의 grounding 은 **10.2 로 전체 최고**(볼드)인데, 로봇 손 외형에서는 13.8 로 급격히 나빠집니다.

  > "Without embodiment alignment, the model performs well under the human-hand appearance, but degrades under the robot-hand appearance and achieves lower task success than full Wh0, indicating that its grounding does not reliably transfer to robot embodiment." (§5.3)
  (사람 외형 최고점을 찍고도 성공률이 낮다는 것은, 이 정책이 "사람 손이 보이는 장면"에 특화되어 배포 시 실제 로봇 손이 화면에 들어오는 순간 grounding 이 무너진다는 뜻입니다. embodiment alignment 의 값어치는 grounding 을 *더 잘하게* 만드는 것이 아니라 **외형이 바뀌어도 무너지지 않게** 만드는 데 있습니다 — HO(human)↔HO(robot) 격차가 3.6 에서 1.0 으로 줄어드는 것이 그 증거입니다.)

- **규모 ablation (5k → 25k → 50k)** — 27.8% → 32.5% → 38.9%, HO(robot) 10.5 → 9.9 → 9.6 으로 두 지표가 단조 개선됩니다. 다만 §B.4 에 따르면 `WM-H 5k` 만 샘플링 비가 `R:W-EA:W = 1:0.06:0.94` 로 다르고 25k·50k 는 `0.28:0.04:0.68` 로 동일하므로, 5k → 25k 구간의 차이에는 규모 외에 믹스 비율 변화가 섞여 있습니다.

  > "Finally, increasing WM-H scale consistently improves both grounding metrics and real-world success, showing that aligned data becomes more effective as it scales." (§5.3)
  (핵심 주장은 "규모가 는다"가 아니라 "**정합된** 데이터가 규모에 따라 더 효과적이 된다"입니다. 정합 없이 늘린 데이터의 스케일링 곡선은 측정되지 않았으므로, 이 주장은 정합 조건부로만 검증된 상태입니다.)

![Figure 6 — Effect of scene and embodiment alignment](https://arxiv.org/html/2606.22136/x6.png)

> "Figure 6: Effect of scene and embodiment alignment. Top: Without scene alignment, generated videos drift from the target workspace (left); with it (ours), they stay anchored. Middle: Embodiment alignment edits selected frames to a robot hand while preserving pose and motion. Right: Action-feature cosine similarity under original vs. edited appearance." (§5.3)
(오른쪽 패널의 action-feature cosine similarity 가 embodiment alignment 의 작동 기제를 직접 시각화합니다 — 외형이 바뀌어도 액션 특징이 유지되는지를 재는, Table 2 의 HO(human)↔HO(robot) 격차와 짝을 이루는 측정입니다.)

### Q3 — 사전학습 prior 해금 (Table 3)

| Variant | Human Pretrain | Teleop | WM-H | Hand-Object Dist. (cm) ↓ | Task Success ↑ |
|---|---|---|---|---|---|
| No model (initial pose) | – | – | – | $`18.9_{\scriptscriptstyle\pm 2.8}`$ | – |
| PaliGemma pretrain, Teleop | ✗ | ✓ | ✗ | $`14.3_{\scriptscriptstyle\pm 2.0}`$ | $`0.8_{\scriptscriptstyle\pm 2.6}`$ |
| PaliGemma pretrain, Teleop + WM-H | ✗ | ✓ | ✓ | $`12.7_{\scriptscriptstyle\pm 1.4}`$ | $`0.6_{\scriptscriptstyle\pm 1.6}`$ |
| Human pretrain | ✓ | ✗ | ✗ | $`13.1_{\scriptscriptstyle\pm 1.8}`$ | $`0.0`$ |
| Human pretrain, Teleop | ✓ | ✓ | ✗ | $`16.2_{\scriptscriptstyle\pm 3.3}`$ | $`8.3_{\scriptscriptstyle\pm 8.6}`$ |
| Wh0 | ✓ | ✓ | ✓ | $`\mathbf{10.6}_{\scriptscriptstyle\pm 2.0}`$ | $`\mathbf{38.9}_{\scriptscriptstyle\pm 19.8}`$ |

> "These results are consistent with WM-H helping activate and align pretrained human manipulation priors, rather than learning dexterous skills from scratch." (§5.4)
(이 표의 진짜 메시지는 **WM-H 가 단독으로는 아무 가치가 없다** 는 것입니다. 사람 영상 사전학습 없이 WM-H 를 넣으면 성공률이 0.8% → 0.6% 로 오히려 내려갑니다 — grounding(14.3 → 12.7)은 개선되는데도 말입니다.)

행별 판독:

- **`Human pretrain` 단독 (13.1 / 0.0%)** — grounding 은 좋은데 성공률은 정확히 0입니다. 사람 손 모션 prior 는 "어디로 손을 뻗어야 하는지"는 알지만 로봇에 그대로 배포할 수는 없다는 뜻으로, 저자들은 이를 VITRA 의 평가와 일관된 결과로 봅니다.
- **`Human pretrain, Teleop` (16.2 / 8.3%)** — 여기서 grounding 이 사전학습 단독의 13.1 에서 **16.2 로 악화** 됩니다. 성공률은 0.0% → 8.3% 로 오르므로, 400건 teleop 사후학습은 배포 가능성을 사는 대가로 언어 조건 grounding 을 일부 파괴한다는 해석이 가능합니다. 이것이 이 논문 전체에서 P4 관점으로 가장 중요한 관측입니다.
- **`Wh0` (10.6 / 38.9%)** — 세 요소를 모두 결합했을 때만 grounding 과 성공률이 동시에 최고입니다. 즉 WM-H 의 역할은 teleop 사후학습이 깎아먹은 grounding 을 복원하면서 배포 가능성은 유지하는 것입니다.
- **grounding ↛ 성공률** — `PaliGemma pretrain, Teleop + WM-H` 는 grounding 12.7 로 `Human pretrain, Teleop`(16.2)보다 훨씬 좋은데 성공률은 0.6% 대 8.3% 로 반대입니다. HO 지표만 보고 판단하면 정반대 결론에 도달한다는 명확한 경고입니다.

### 생성 영상 품질 — user study (Table 4)

72명의 AI 실무자 대상 사용자 연구입니다.

| Part | Dimension | N | Result | Δ from real |
|---|---|---|---|---|
| A | AI judged as real | 355 | 37.7% | – |
| | Judgment cue: visual smoothness / artifacts | 710 | 19.4% | – |
| | Judgment cue: hand appearance & motion | 710 | 34.9% | – |
| | Judgment cue: physics, layout & contact | 710 | 45.6% | – |
| B | Object correctness | 1,420 | $`3.97\pm 1.22`$ | 1.03 |
| | Instruction alignment | 1,420 | $`4.18\pm 1.09`$ | 0.82 |
| | Hand-object interaction | 1,420 | $`3.95\pm 1.19`$ | 1.05 |
| | Physical plausibility | 1,420 | $`3.78\pm 1.30`$ | 1.22 |
| | Training suitability | 1,420 | $`3.57\pm 1.31`$ | 1.43 |
| C | Pose consistency | 355 | $`4.30\pm 0.85`$ | – |
| | Contact preservation | 355 | $`4.25\pm 0.84`$ | – |

> "Under these higher-level evaluation criteria, 37.7% of AI-generated videos (134/355 trials) were perceived as real recordings, demonstrating that a substantial portion of synthetic samples already exhibits strong realism in scene layout, physical plausibility, and manipulation performance." (§A.5)
(37.7% 는 "생성 영상의 3분의 1 이상이 실촬로 오인되었다"는 뜻이지만, 뒤집으면 62.3% 는 합성으로 간파되었다는 뜻이기도 합니다. 데이터 공장의 품질 상한을 재는 숫자로 읽는 편이 정확합니다.)

- **평가 차원별 순위가 시사하는 것** — 지시문 정합(4.18)이 가장 높고 **training suitability(3.57)가 가장 낮습니다**. 실제 데이터 ceiling 을 5.0 으로 가정한 Δ 열에서도 training suitability 의 격차(1.43)가 최대입니다. 즉 평가자들이 가장 미덥지 않게 본 항목이 하필 "학습 데이터로서의 적합성" 이라는, 이 논문의 용도 그 자체입니다. (§A.5 는 real-video ceiling 5.0 이 직접 측정된 값이 아니라 가정값임을 명시합니다.)
- **Part C (편집 전후 정합)** — pose consistency 4.30, contact preservation 4.25 로 로봇 손 편집이 원래 포즈·접촉을 대체로 보존한다는 결과이며, embodiment alignment 가 "같은 궤적의 두 외형"이라는 전제를 실제로 만족함을 뒷받침합니다.
- **판단 단서 분포** — 물리·레이아웃·접촉 단서 45.6% > 손 외형·모션 34.9% > 저수준 시각 아티팩트 19.4%. 평가자들이 깜빡임·왜곡 같은 표면 결함보다 의미·물리 일관성으로 판단했다는 뜻이라, Part A 의 37.7% 를 다소 엄격한 조건에서 얻은 값으로 읽을 수 있습니다.

### 데이터 믹스 비율 전체 (Table 5)

| Model / Setting | Dataset Sampling Ratio |
|---|---|
| $`\pi_{0.5}`$ | $`R=1`$ |
| VITRA | $`R=1`$ |
| VITRA Real Version | $`R:\mathrm{HOI4D}=1:1`$ |
| w/o scene alignment | $`R:W\text{-EA}:W=0.28:0.04:0.68`$ |
| w/o embodiment alignment | $`R:W=0.4:1`$ |
| WM-H 5k | $`R:W\text{-EA}:W=1:0.06:0.94`$ |
| WM-H 25k | $`R:W\text{-EA}:W=0.28:0.04:0.68`$ |
| PaliGemma pretrain, Teleop | $`R=1`$ |
| PaliGemma pretrain, Teleop + WM-H | $`R:W\text{-EA}:W=0.28:0.04:0.68`$ |
| Human pretrain, Teleop | $`R=1`$ |
| Wh0 (50k) | $`R:W\text{-EA}:W=0.28:0.04:0.68`$ |

$`R`$ 은 teleop 로봇 데이터, $`W`$ 는 WM-H, $`W`$ -EA 는 embodiment-aligned WM-H 입니다. `w/o embodiment alignment` 행이 `R:W = 0.4:1` 로 다른 ablation 과 비율 체계가 다르다는 점은 유의해야 합니다 — EA 항이 빠지면서 비율이 재조정되어, 이 행의 비교는 "EA 데이터 제거" 단일 변인 통제가 아닙니다.

---

## ⚖️ 한계

- **생성 품질이 곧 supervision 품질의 상한** — 저자들이 직접 열거한 한계 목록입니다.

  > "Wh0 remains limited by video generation quality, hand reconstruction accuracy, human-robot morphology mismatch, dependence on strong pretraining, and task scope." (§6)
  (다섯 항목 중 앞 두 개는 파이프라인 내부 오류가 라벨 노이즈로 그대로 전파된다는 구조적 문제입니다. 생성기가 물리적으로 불가능한 상호작용을 만들면 재구성기는 그것을 성실하게 3D 궤적으로 옮겨 적고, 정책은 그 궤적을 정답으로 학습합니다 — 파이프라인 어디에도 물리 타당성 게이트가 없습니다.)

- **실패 모드의 5개 유형이 모두 라벨 노이즈로 귀결** — §A.6 은 이미지 편집 오류(객체 배치 오류·아티팩트·크롭), 물리적으로 불가능한 상호작용(손이 객체를 관통, 비현실적 파지 포즈), 상호작용 전후 시각 상태 불일치, 실행 불가능한 무의미 지시문, 손 편집 실패(포즈 미보존·장면 객체 변형)를 열거합니다. 이 중 어느 것도 자동 검출·필터 단계가 명시되지 않아, 50k 중 얼마가 오염되었는지에 대한 정량 수치가 없습니다.

  ![Figure 7 — Representative WM-H failure cases](https://arxiv.org/html/2606.22136/x7.png)

  > "Figure 7: Qualitative visualization of representative WM-H failure cases. Each panel highlights typical issues such as image editing errors, physically implausible hand-object interactions, temporal inconsistencies, instruction misalignment, and imperfect robot-hand embodiment alignment." (§A.6)
  (실패 사례가 정성 그림 한 장으로만 제시되고 빈도·필터링 비율이 없다는 점이 이 논문의 재현 관점 최대 공백입니다.)

- **강한 사전학습에 대한 의존이 방법의 전제 조건** — 저자 스스로 가장 명확히 인정하는 한계입니다.

  > "WM-H also provides little benefit without a human-video-pretrained backbone, indicating that it complements rather than replaces large-scale pretraining." (§6)
  (Table 3 이 이를 뒷받침합니다 — PaliGemma 사전학습만 있는 백본에 WM-H 를 넣으면 성공률이 0.8% → 0.6%. 즉 WM-H 는 독립적인 데이터 자산이 아니라 **특정 사전학습 계보에 결합해야만 작동하는 촉매** 이며, 이는 데이터셋의 이식성을 크게 제한합니다.)

- **embodiment alignment 가 외형에만 작동** — 로봇 손을 "외형만 다른 손"으로 환원한 설계 선택의 대가입니다. 편집은 픽셀 외형을 바꿀 뿐 로봇 손의 운동학·크기·워크스페이스를 반영하지 않으므로, 사람 손으로는 가능하지만 실제 Inspire 손으로는 불가능한 파지 포즈가 여전히 정답 라벨로 남습니다. 저자들도 로봇 손이 더 커서 실행 중 의도치 않게 객체를 건드린다고 §6 에서 인정합니다.

- **평가 지표의 순환성** — HO 평가셋은 world-model 궤적에서 목표 객체 위치를 추정해 구성됩니다(§C.2). 즉 **데이터를 만든 생성기가 평가 기준도 만든** 구조라, WM-H 로 학습한 정책이 그 분포에서 유리할 소지가 구조적으로 존재합니다. 저자들이 지표의 성격을 스스로 제한한 것은 정직하지만, 순환성 자체는 다뤄지지 않습니다.

  > "Since this metric does not evaluate finger-level dexterity, it should be viewed as a grounding metric rather than a complete task-success metric: low distance is usually necessary, but not sufficient, for successful manipulation." (§C.2)
  (손목 도달 거리만 재므로 손가락 수준의 손재주는 전혀 측정되지 않습니다. 정작 이 저장소가 관심 있는 접촉 집약적 능력은 이 지표의 사각지대에 있습니다.)

- **태스크 범위가 단일팔 pick-and-place** — 18개 태스크는 파지·놓기·테이블 닦기 수준이며, 저자들도 bimanual·도구 사용·장기 지평 태스크로의 확장을 향후 과제로 남깁니다. 생성 파이프라인이 "손이 하단에서 진입해 동작 후 정지"라는 고정 프롬프트 템플릿에 묶여 있어(§A.3), 인핸드 재배향처럼 손 내부에서 오래 지속되는 조작은 애초에 생성 대상이 아닙니다.

- **표준편차가 평균에 육박** — Wh0 의 38.9±19.8, `w/o scene align.` 의 20.0±24.7 처럼 18개 태스크 간 편차가 매우 큽니다. 평균 성공률 개선이 전 태스크에 고르게 분포하는지, 몇 개 쉬운 태스크에 몰려 있는지 구분할 수 없어 일반화 주장의 강도가 약해집니다.

- **배포 규칙의 기여도 미분리** — 모든 방법에 monotonic closure grasping prior 를 동일 적용하므로 비교는 공정하지만, 이 규칙 없이 정책 단독 성공률이 얼마인지는 보고되지 않습니다. 다지 손 정책의 순수 능력치를 판단할 수 없습니다.

---

## ♻️ 재현성

- **코드 / 데이터** — 초록 말미에 "Videos and open-source code can be found on our project website" 로 공개를 명시하며 프로젝트 페이지 URL(<https://chenyt31.github.io/wh0.github.io/>)을 제시합니다. 다만 본 분석 실행 환경의 프록시가 해당 호스트를 차단해(`curl: (56) CONNECT tunnel failed, response 403`) 실제 코드·WM-H 공개 여부와 라이선스는 확인하지 못했습니다. 논문 본문에 GitHub / HuggingFace 주소는 별도로 기재되어 있지 않습니다.
- **의존 구성요소** — Wan-I2V-A14B(생성), Qwen-Image-Edit(장면·손 편집), Qwen3-VL(동역학 서술 생성), LightX2V / Lightning LoRA(가속), HaWoR(손 재구성), MegaSAM(카메라 트래킹), MANO(손 모델), PaliGemma2-3B(백본), VITRA(초기 가중치 + 정규화 통계). 모두 외부 공개 모델이지만 **정규화 통계는 VITRA 가 사전 계산한 값을 그대로 재사용** 하므로, VITRA 산출물 접근 없이는 액션 공간을 동일하게 맞추기 어렵습니다.
- **프롬프트 공개도** — §A.1–A.4 에 어휘 확장, 장면 편집, Qwen3-VL 동역학 서술, I2V 생성, 로봇 손 편집(positive/negative)의 프롬프트 템플릿이 전문 그대로 실려 있어 파이프라인 재현성은 높은 편입니다. 반면 편집 스텝 수·CFG scale 은 "small number of steps", "low CFG scale" 로만 서술되어 구체 값이 없습니다.
- **학습 하이퍼파라미터** — §B.3 에 lr / weight decay / betas / grad clip / 최대 스텝 / 배치 / diffusion 스텝 / 스케줄 / 추론 설정이 모두 명시되어 있어 정책 학습 측 재현성은 양호합니다.
- **하드웨어** — 학습 H200 × 4, 추론 RTX 4090 × 1. 로봇은 Unitree G1 + Inspire hands + Apple Vision Pro teleoperation. 생성 비용은 1k 영상당 5.44 GPU-hour 로 명시됩니다.
- **미공개 항목** — 50k 중 필터링으로 폐기된 비율, HO 평가셋의 수동 필터링 기준, 편집 프레임 샘플 간격·오프셋의 구체 값.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P5(World Model) — 주 pillar.** 본 논문은 P5 의 **D28**(world-model role)에 대해 v1 이 "tracked" 로만 적어둔 *data-augmentation / rollout synthesis* 역할을 정면으로 승격시키는 사례입니다. v1 의 선택은 "latent dynamics prior + future-prediction auxiliary 를 VLA 와 co-train" 인데, Wh0 는 world model 을 **학습하지도, 정책에 붙이지도 않고** 오직 오프라인 데이터 공장으로만 씁니다 — 즉 D28 의 대안 축을 실증한 논문입니다. **D30**(prediction space)에서는 v1 의 latent / 3D-flow 선호와 정반대로 **raw-pixel 비디오 생성** 을 택했고, **D31**(action conditioning)에서도 v1 의 per-frame action-conditioned 예측과 달리 **action-free 생성 후 사후 손 재구성으로 라벨을 붙이는** 방식이라 두 Decision 모두와 충돌합니다. 반면 **D32**(egocentric hand-object world model)에는 정확히 부합합니다 — egocentric 1인칭 손-객체 상호작용이 생성 대상 그 자체입니다. **D29**(integration architecture)는 해당 없음: 통합 아키텍처가 없습니다.
- **P4(VLM 사전학습 보존 / 데이터 효율 적응).** **D22**(pretraining data composition — egocentric vs mixed, `OPEN`)에 직접적인 세 번째 선택지를 제공합니다. 지금까지 열려 있던 축이 "egocentric-only vs everything-mixed" 였다면, 본 논문은 "**합성 egocentric**"이라는 축을 추가하고, 실촬 ego(HOI4D 21.4%) 대비 합성 ego(38.9%)가 *배포 정합만 확보하면 우세할 수 있음* 을 실측합니다. **D21**(staged recipe)에서는 사람 영상 데이터를 Stage 1 사전학습이 아니라 **Stage 3 배포 적응 단계의 co-train 파트너** 로 배치하는 변형을 제시합니다. **D19**(lineage & adaptation range)에는 경고로 작용합니다 — v1 의 (a) full VLM freeze 와 달리 본 논문은 비전 인코더만 동결하고 나머지 백본 + 액션 디코더를 갱신하며, 그럼에도 Table 3 은 사후학습이 grounding 을 13.1 → 16.2 로 훼손함을 보여줍니다. **D20**(prior-preservation strategy)에 대해서는 손실 항이나 trust region 없이 **데이터 믹스만으로 prior 를 보존·복원** 하는 접근을 제시합니다 — ConSFT 류 보수적 SFT 와 직접 경쟁하는 대안입니다. **D23**(action representation)은 부분 부합: 연속 액션이지만 flow matching 이 아니라 DDPM/DDIM diffusion 입니다.
- **P0(VLA Datasets & Benchmarks).** WM-H 는 **D24**(priority data axis = egocentric 중심)의 정의 범위를 넓히는 사례입니다 — "촬영된" egocentric 만 세던 축에 "생성된" egocentric 이 들어옵니다. **D27**(license / usability bar)에는 새 종류의 리스크를 얹습니다: 합성 corpus 의 사용 가능성은 데이터셋 라이선스뿐 아니라 **생성기(Wan / Qwen-Image-Edit) 가중치의 라이선스와 출력물 조항** 에 종속됩니다. **D25**(tactile/force 데이터)에는 기여가 없습니다 — 비디오 파이프라인이라 촉각·힘 라벨이 원리적으로 생성 불가입니다. **D26**(benchmark scope)은 해당 없음: 18개 태스크는 사내 평가셋이며 공개 벤치마크가 아닙니다.
- **P1(Heterogeneous Body/Hand Action Expert).** 약한 연결입니다. 액션 공간이 MANO 15-DoF 관절 회전 + 손목 상대 pose 로 **D3**(hand output space = finger joint command)와 **D2**(body output space = wrist pose)의 분해와 우연히 같은 구조를 갖지만, 본 논문에는 Body/Hand 전문가 분리가 없습니다 — 단일 DiT-B 디코더가 102차원을 한꺼번에 뱉는 monolithic 구조로, P1 §4 의 비교군에 해당합니다.
- **Identity 긴장/지지.** **지지**: "사전학습 구성이 소량 배포 데이터를 충분하게 만든다"는 P4 명제의 강한 실증이며, 특히 "소량 로봇 데이터 사후학습이 오히려 일반화를 깎는다"는 진단은 Identity 의 pretraining-first 관점과 정확히 일치합니다. **긴장**: 본 저장소의 차별화 주장은 손 수준 접촉 정밀도인데, Wh0 의 데이터에는 촉각·힘·접촉력이 원리적으로 없고 평가 지표(HO)도 손목 거리만 잽니다. 이 논문이 여는 문은 "grounding·일반화"이지 "손재주"가 아닙니다.
- **경쟁자 함의.** P5 핀 중 Ctrl-World(raw-pixel WM 의 data-augmentation 분기)와 역할이 가장 가깝고, DexWM·LOME·Being-H0.7 과는 "world model 을 예측기로 쓸 것인가, 데이터 공장으로 쓸 것인가"라는 축에서 정면으로 갈립니다. P0 핀 중 EgoDex·Ego-Exo4D 같은 실촬 ego corpus 와는 대체 관계이며, 비교군 `VITRA Real Version` 이 쓴 HOI4D(P0 methodology base)와의 대질이 그 대체 가능성을 직접 측정합니다.

---

## ✨ 핀 논문 대비 델타

- **vs Ctrl-World (P5 핀, raw-pixel WM / data-augmentation 분기)** — Ctrl-World 는 로봇 데이터로 *controllable world model 을 학습* 해 policy ranking 과 rollout 합성에 씁니다. Wh0 는 world model 을 **학습하지 않고** 기성 I2V 모델을 그대로 쓰며, 생성 대상도 로봇 rollout 이 아니라 **사람 손 영상** 입니다. 액션 라벨을 조건 입력이 아니라 *사후 재구성* 으로 얻는다는 점이 가장 큰 구조적 차이입니다.
- **vs DexWM (P5 최상위 핀)** — DexWM 은 사람 영상에서 hand-conditioned 상호작용 동역학을 모델링하는 **예측기** 입니다. Wh0 는 예측을 전혀 하지 않고 데이터만 만듭니다. 같은 "egocentric hand-object" 재료(D32)를 쓰면서 D28 의 역할 축에서 정반대에 서는 짝입니다.
- **vs Being-H0.7 / LOME (P5 핀, latent · action-conditioned)** — 두 핀 모두 action-conditioned latent 예측(D30/D31 의 v1 방향)입니다. Wh0 는 action-free raw-pixel 생성이라 D30/D31 양쪽에서 반대 극단이며, 그럼에도 실로봇 성능을 냈다는 점에서 v1 선택의 배타성을 약화시키는 반례로 기능합니다.
- **vs EgoDex / Ego-Exo4D / HOI4D (P0)** — 실촬 ego corpus 는 규모는 크지만 배포 장면·embodiment 와 어긋납니다. Wh0 의 델타는 **corpus 를 배포 장면에 맞춰 주문 제작** 한다는 것이며, `VITRA Real Version`(HOI4D 5,511 에피소드, `R:HOI4D=1:1`) 21.4% 대 Wh0 38.9% 가 그 델타의 크기입니다. 다만 이 비교는 HOI4D 를 100프레임 단위로 자른 저자 측 전처리에 의존하므로 실촬 corpus 일반에 대한 판정은 아닙니다.
- **vs Being-H0.5 (P4 핀, human-video-centric pretraining)** — Being-H0.5 는 사람 영상을 **사전학습 corpus** 로 씁니다(UniHand-2.0 ~35k h). Wh0 는 같은 재료를 **사후학습 co-train 파트너** 로 옮기고, 그 결과 D21 의 stage 배치가 달라집니다. 두 논문을 합치면 "사람 영상은 Stage 1 과 Stage 3 어디에 넣어야 하는가"라는 새 질문이 생깁니다.
- **vs π0.5 (P4/P1 핀)** — 본 논문의 Table 1 에 π0.5 가 로봇 데이터 사전학습 baseline 으로 직접 등장해 7.78% 를 기록합니다. 사람 영상 사전학습 계보(VITRA 8.3%)와 로봇 데이터 계보(π0.5 7.78%)가 이 zero-shot 다지 셋업에서는 **둘 다 실패한다** 는 것이, 계보 선택(D19)보다 사후학습 데이터 구성(D22)이 지배적 변수라는 본 논문의 주장을 뒷받침합니다.

---

## ⚙️ 의사결정 함의

이 논문이 맞다면 우리 파이프라인에서 다음이 바뀝니다.

- **D22 의 open ablation 에 세 번째 arm 추가** — 현재 "egocentric-only vs everything-mixed" 2지 구도에 **`synthetic-egocentric` (world-model 생성 ego corpus)** 를 추가합니다. 최소 실험 형태는 실촬 ego corpus 와 동일 에피소드 수의 합성 corpus 를 같은 co-train 비율로 붙여 성공률·grounding 을 대질하는 것으로, 본 논문의 `VITRA Real Version` vs `Wh0` 대조를 그대로 복제하면 됩니다.
- **co-train 샘플링 비율을 명시적 config 키로 승격** — 데이터 *보유량* 비(125:1)와 *배치 샘플링* 비(`R:W-EA:W = 0.28:0.04:0.68`)를 분리해 관리해야 합니다. Stage 3 배포 적응 레시피(D21)에 `sampler.weights = {teleop: 0.28, synth: 0.68, synth_ea: 0.04}` 형태의 키를 도입하고, 희소 실로봇 데이터의 오버샘플링 배율을 명시적 하이퍼파라미터로 둡니다.
- **정규화 통계의 출처를 config 로 고정** — 액션·상태 정규화 통계를 배포 데이터에서 계산하지 않고 **사전학습 corpus 에서 사전 계산된 per-joint 통계를 재사용** 하도록 `norm_stats.source = pretrain_corpus` 를 강제합니다. 소량 배포 데이터로 통계를 다시 뽑는 순간 사전학습 prior 와 좌표가 어긋난다는 것이 본 논문의 명시적 주장입니다(§4).
- **외형 불변성 증강을 Stage 2/3 에 추가** — 배치의 소수 비율(본 논문 4%)을 **손 외형만 편집한 프레임** 으로 채우는 증강을 도입합니다. 우리 스택에서는 생성 편집 대신 렌더링(Sharpa 손 메시 오버레이) 또는 실촬 사람 손/로봇 손 페어로 대체 가능하며, 검증 지표는 본 논문이 쓴 **동일 궤적 · 외형 변경 시 action-feature cosine similarity** 입니다.
- **새 평가 지표 도입 — grounding 과 성공률의 분리** — Hand-Object Distance(cm)에 상당하는 "언어 조건 객체 grounding" 프록시를 평가 하네스에 추가하되, **성공률과 반드시 함께** 봅니다. Table 3 의 `PaliGemma pretrain, Teleop + WM-H`(HO 12.7 / 성공률 0.6%) 사례가 단일 지표 판단의 위험을 정량적으로 보여줍니다. 기준선은 "정책 없음(초기 pose)" 값이며, 우리 셋업에서는 world-model 궤적이 아니라 **실측 객체 위치** 로 정의해 순환성을 제거해야 합니다.
- **사후학습 회귀(regression) 게이트 신설** — Table 3 의 13.1 → 16.2 (사전학습 단독 → teleop 사후학습) 은 사후학습이 grounding 을 훼손할 수 있음을 보여줍니다. D20 의 보존 전략 평가에 "**사후학습 전후 grounding 지표 비회귀**"를 통과 조건으로 넣고, 회귀가 관측되면 conservative SFT 강도를 올리거나 co-train 데이터 폭을 넓히는 분기를 둡니다.
- **생성 예산의 1차 근사** — 1k 영상당 5.44 GPU-hour 이므로 50k 규모는 단순 환산 약 272 GPU-hour(원문에 총량 명시 없음, 본 분석의 산술 환산)입니다. H200 4장 기준 약 3일 수준으로, "사람 촬영 대비 싸다"는 주장의 실제 비용 눈금을 우리 예산 판단에 쓸 수 있습니다.

---

## ⚠️ 먼저 검증할 실패 모드

가장 싼 확인부터 순서대로 나열합니다.

1. **(가장 싼 체크 — 문헌만으로 판정) 우리 lineage 에서 촉매가 작동하지 않을 위험.** Table 3 이 보여주는 전제 조건은 *사람 영상 사전학습된 백본* 입니다. PaliGemma 사전학습 백본에 WM-H 를 넣으면 성공률 0.8% → 0.6%. 그런데 D19 v1 의 lineage 는 **PaliGemma-2B × π0 mix(openpi)** — 즉 *로봇 데이터* 사전학습 계보입니다. 이 논문의 레시피를 우리 lineage 에 그대로 가져오면 Table 3 의 실패 행에 앉게 될 가능성이 큽니다. 합성 ego 데이터를 검토하기 전에 **우리 백본이 사람 영상 prior 를 갖고 있는지** 부터 확정해야 하며, 없다면 VITRA 급 사람 영상 further-pretrain 이 선행 조건입니다. 본 논문 채택 여부를 가르는 단일 최대 리스크입니다.
2. **(문서 확인) 프로젝트 페이지 도달성과 공개 범위.** 코드·WM-H·생성 프롬프트가 실제로 공개되었는지, WM-H 라이선스와 생성기(Wan / Qwen-Image-Edit) 출력물 조항이 우리 사용(연구·사내 학습)에 허용되는지 확인합니다. 본 분석 환경에서는 프록시 차단으로 확인하지 못했습니다. NC 조항이나 출력물 제한이 있으면 D27 기준에서 즉시 탈락합니다.
3. **(반나절) 태스크 난이도 축의 불일치.** 18개 태스크는 파지·통에 넣기·테이블 닦기이며, 우리 Phase 1(인핸드 큐브 재배향)·Phase 2(도구 조작)와는 다른 축입니다. 더 결정적으로, 생성 프롬프트가 "손이 하단에서 진입 → 동작 → 정지"로 고정되어 있어(§A.3) **인핸드 조작 영상은 애초에 생성 대상이 아닙니다**. 우리 태스크군을 이 파이프라인으로 만들 수 있는지부터 프롬프트 수준에서 검증해야 합니다.
4. **(반나절) 촉각·힘 모달리티의 원리적 부재.** WM-H 는 비디오 + 재구성 손 포즈뿐이라 촉각·관절 토크·접촉력 라벨이 0입니다. P2 D11(proprio-tactile-force 토큰)과 P3(System0)에는 어떤 신호도 공급하지 못하므로, 이 데이터는 **관측 융합·접촉 안정화 축에는 기여 불가** 로 명확히 선을 그어야 합니다. 우리 차별화 주장의 본체가 손 수준 접촉이라는 점에서 이 한계는 치명적입니다.
5. **(1–2일) MANO 사영으로 인한 정보 손실.** 액션 공간이 MANO 15-DoF × 3 인데, 우리 근시일 하드웨어는 Sharpa Hand 22-DOF(손목 DOF 없음)입니다. 로봇 관절 → MANO retarget 이 우리 손의 자유도 일부를 표현하지 못하면, 사전학습 prior 를 얻는 대가로 손가락 정밀도를 잃습니다. 가장 싼 검증은 **Sharpa 관절 궤적 → MANO → 역retarget 왕복 오차** 를 오프라인으로 재보는 것으로, 데이터 한 줄 만들지 않고 판정 가능합니다.
6. **(1–2일) 외형 정합의 재료 확보.** embodiment alignment 는 "우리 로봇 손의 사실적 외형"을 편집 모델이 그려낼 수 있어야 성립합니다. 본 논문은 흰 등껍질/검은 손바닥의 일반적 로봇 손 외형을 텍스트로 기술했지만, Sharpa Hand 나 사내 커스텀 손은 편집 모델의 사전지식에 없습니다. 참조 이미지 기반 편집이 가능한지, 아니면 렌더링 오버레이로 대체해야 하는지를 먼저 확인해야 합니다.
7. **(수일) 평가 프로토콜의 비교 불가능성.** stage-conditioned instruction(평가자가 단계마다 다음 지시문을 투입)과 monotonic closure grasping prior 가 모든 결과에 깔려 있습니다. 우리 평가가 단일 지시문·규칙 없는 순수 정책이라면 38.9% 를 그대로 비교 기준으로 삼을 수 없습니다. 우리 하네스에 같은 두 장치를 넣을지 여부를 먼저 결정해야 합니다.
8. **(수일) 라벨 노이즈 비율의 미지수.** §A.6 의 5개 실패 유형에 대해 발생 빈도·필터링 비율이 전혀 보고되지 않았습니다. 우리가 자체 생성 파이프라인을 만든다면 **자동 필터(물리 타당성 판정기 / 재구성 신뢰도 임계값)를 먼저 설계** 하고, 필터 통과율을 파이프라인의 1차 지표로 삼아야 합니다. 필터 없이 규모만 늘리면 노이즈도 같이 스케일합니다.
9. **(수일) 규모 스케일링 주장의 교란.** `WM-H 5k` 만 샘플링 비가 `1:0.06:0.94` 로 다르므로(§B.4 Table 5), 5k → 25k 개선분에는 규모와 믹스 비율이 섞여 있습니다. 우리 재현 시에는 믹스 비율을 고정한 채 규모만 바꾸는 통제된 스케일링 곡선을 다시 그려야 합니다.
10. **(비용 검증) 태스크 간 편차.** ±19.8 은 태스크별 성공률이 0% 와 90% 사이에 흩어져 있을 수 있음을 뜻합니다. 태스크별 분해가 논문에 없으므로, 우리 재현에서는 **평균이 아니라 태스크별 분포** 를 1차 보고 단위로 삼아 "몇 개 쉬운 태스크가 평균을 끌어올린 것" 인지 구분해야 합니다.

---

## 💡 컨텍스트 제안

사람이 판단할 후보만 적으며, `context/` 파일은 수정하지 않았습니다.

- **P5 §5 핀 교체 검토 (D28)** — 현재 P5 핀은 8/8 로 가득 차 있습니다. Wh0 는 D28 의 "data-augmentation (rollout synthesis) tracked" 항목을 실증한 첫 사례이며 실로봇 결과까지 갖췄으므로, 같은 raw-pixel / 데이터 활용 분기를 대표하는 **Ctrl-World** 자리와의 교체를 검토할 만합니다. 다만 Ctrl-World 는 eval-in-imagination 역할도 겸하므로 단순 교체는 커버리지 손실 위험이 있습니다.
- **D28 문구 보강 제안** — v1 의 "데이터 증강(rollout synthesis) tracked" 를 "**사람 손 데이터 생성(human-hand data engine)**" 까지 포함하도록 넓히는 안. 현행 문구는 *로봇 rollout* 합성만 상정하는데, 본 논문이 보여준 축은 로봇이 아니라 사람 손 데이터입니다.
- **D22 (`OPEN`) 에 세 번째 arm 등록 제안** — "egocentric-only vs everything-mixed" 에 **`synthetic-egocentric`** 을 명시적 후보로 추가. 본 논문은 이 arm 이 실촬 ego 대비 우위일 수 있다는 첫 실측을 제공합니다(21.4% vs 38.9%, 동일 co-train 프레임).
- **D27 (license/usability bar) 확장 제안** — 합성 corpus 에 대해서는 데이터셋 라이선스만이 아니라 **생성기 가중치의 라이선스 + 출력물 사용 조항** 까지 기록 항목에 추가. 기존 바(Apache-2.0 / CC-BY / MIT 선호)만으로는 합성 데이터의 사용 가능성을 판정할 수 없습니다.
- **P0 §5 methodology base 추가 후보** — WM-H 가 실제 공개될 경우, "world-model 생성 egocentric corpus" 유형의 첫 항목으로 methodology base 표에 등재 검토. 다만 재현성 §의 미확인 사항(공개 여부·라이선스)이 해소된 뒤가 적절합니다.
- **P4 D21 에 회귀 게이트 제안** — Stage 3 배포 적응 단계에 "사후학습 전후 grounding 비회귀" 조건을 추가하는 안. 본 논문 Table 3 의 13.1 → 16.2 관측이 근거입니다.

---

> 💡 base 매핑은 `/implement-design analysis/2606.22136/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
