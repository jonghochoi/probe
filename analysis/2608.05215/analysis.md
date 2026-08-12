# Paper Analysis — VLAff: Vision-Language-Affordance Model for Unified Actionable Affordances

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | VLAff: Vision-Language-Affordance Model for Unified Actionable Affordances |
| 저자 | Jihoon Oh, Kento Kawaharazuka, Kei Okada (The University of Tokyo, JSK) |
| 링크 | [arXiv:2608.05215](https://arxiv.org/abs/2608.05215) |
| 발행일 / 버전 | 2026-08-05 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-08-12 |
| 관련 Pillar | P0, P4, P2, P1 |
| 태그 | egocentric-data, dataset, vla-arch |

논문 각주에 `Accepted for publication in the 2026 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)` 가 명시되어 있어, arXiv preprint 가 아니라 IROS 2026 채택본입니다. 코드 저장소·프로젝트 페이지·데이터셋 배포 URL 은 본문·각주·초록 어디에도 제시되지 않았으므로 `링크` 행은 arXiv 하나뿐입니다 (♻️ 재현성 참조).

---

## 🧭 한 줄 요약 (TL;DR)

VLAff 는 egocentric 인간 영상에서 **어디를 만질지(visual heatmap)· 어떻게 쥘지(MANO grasp pose)· 어떻게 움직일지(6D trajectory)** 라는 세 종류의 actionable affordance 를 한꺼번에 뽑아내는 자동 추출 파이프라인(EgoAffordance, 204,025 episode)을 만들고, 그 위에 세 modality 를 **하나의 VLM 이 특수 토큰으로 동시에 예측**하는 통합 모델을 올린 논문입니다. 결과적으로 visual affordance 예측에서 SOTA 를 얻고(IoU 0.121 · KLD 2.517), 실환경 zero-shot 조작 평균 성공률 68.0 % 로 기존 최강 baseline VidBot(52.0 %)을 16 %p 앞섭니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 인간 영상은 인터넷 규모로 이미 존재하지만, 로봇과 신체 구조가 달라(embodiment mismatch) 그대로 정책 학습에 쓸 수 없습니다. 본 논문은 그 간극을 **embodiment-agnostic 한 object-centric affordance** 라는 중간 표현으로 메우려 합니다.
- **기존 접근의 한계** — 인간 영상에서 암묵적 표현(R3M · MVP · VIP 계열)을 학습하는 방향은 해석이 어렵고 로봇 액션으로 직접 옮기기 어렵습니다. 반대로 명시적 affordance 를 쓰는 계열은 실험실 정적 환경의 고급 센서 데이터에 의존하거나, heatmap · grasp · trajectory 중 **한 가지 modality 만** 다루거나 2D 이미지 공간에 갇혀 있습니다.
- **본 논문의 가설** — 세 affordance 를 **하나의 프레임워크에서 함께 학습하면 cross-modal 상관이 잡혀** 개별 modality 성능까지 올라가고, 그 결과가 실제 로봇 실행으로 곧장 변환된다는 것입니다. Table II 의 visual affordance SOTA 가 이 가설의 검증 지점으로 설계되어 있습니다.
- **왜 지금 중요한가** — 3D SfM · hand mesh 복원 · 개방 어휘 분할 같은 컴퓨터 비전 요소기술이 최근에서야 "라벨 없는 ego 영상에서 3D 손 궤적을 자동으로 뽑을 수 있는" 수준에 도달했습니다. 즉 데이터 규모의 병목이 사람 라벨링에서 파이프라인 정확도로 이동했고, 200K episode 급 자동 구축이 처음으로 현실적이 되었습니다.
- **설계 제약** — 저자들이 스스로 세운 조건은 (1) 인간 영상만으로 구축 가능할 것, (2) 로봇 action label 없이 zero-shot 실행까지 이어질 것, (3) 사람 팔·손이 화면에 남지 않도록 agent-agnostic 장면을 만들 것(ego segmentation + inpainting)입니다.

---

## 🧩 핵심 기여

- **EgoAffordance 데이터셋** — egocentric 인간 영상에서 visual affordance mask · MANO hand pose · camera(hand) trajectory 를 **동시에** 갖춘 최초 규모의 corpus. 204,025 episode, 5,782,431 visual heatmap, 11,612,524 trajectory sequence.
- **자동 affordance 추출 파이프라인** — hand-object detector → 물체 분할 → 2D keypoint → 접촉 영역 산출 → tracking → MANO 복원 → ego segmentation + inpainting → monocular depth → intrinsics 추정 → camera pose 추정 → 3D hand trajectory tracking 의 단계 조합. 사람 라벨 없이 3D actionable affordance 를 생산합니다.
- **VLAff 통합 모델** — VLM 어휘에 `<SEG>` · `<GRASP>` · `<p0>…<pN-1>` 특수 토큰을 추가해, 하나의 Qwen2.5-VL 백본이 heatmap · 96-D MANO grasp · 자기회귀 trajectory 를 함께 예측하도록 만든 구조.
- **object-centric 정규화** — heatmap 의 peak 를 3D anchor point 로 투영하고 grasp/trajectory 를 그 anchor 기준 좌표계로 옮겨, embodiment 가 달라도 전이 가능한 표현을 만듭니다.
- **추론 시점 궤적 보정 2종** — GPT 급 VLM 을 상위 플래너로 써서 첫 궤적 토큰의 방향 벡터를 조건화하는 in-context guidance, 그리고 $`K`$ 개 후보를 뽑아 복셀 충돌 + 방향 정렬 복합 목적으로 고르는 sampling-based selection.
- **다운스트림 2종 실증** — Fetch · PR2 실기 zero-shot 조작(실환경 평균 68.0 %)과, 예측 affordance 를 dense reward 로 쓰는 실환경 RL 가이드 학습.

---

## 🔑 기술 키워드

- **Actionable Affordance** — "어디를(where) · 어떻게 쥐고(how to grasp) · 어떻게 움직일지(how to move)" 세 가지를 함께 담은 affordance 정의. 기존 affordance 가 지도 위의 압정 하나였다면, 이쪽은 압정 + 손 모양 + 이동 경로가 붙은 한 장의 작업 지시서에 해당합니다.
- **MANO** — 손을 저차원 파라미터(전역 손목 회전 + 15개 국소 관절 회전)로 표현하는 표준 파라메트릭 손 메쉬 모델. 본 논문에서는 각 회전을 6D 회전 표현으로 적어 $`\mathbf{A}_{g}\in\mathbb{R}^{96}`$ 가 됩니다.
- **Visual Affordance Heatmap** — 이미지 각 픽셀이 상호작용 지점일 확률을 담은 지도 $`\mathbf{A}_{v}\in\mathbb{R}^{H\times W}`$. 이번 논문에서 세 modality 중 가장 성능을 좌우하는 축으로 밝혀집니다.
- **Object-Centric Anchor** — heatmap 의 최댓값 픽셀을 depth 와 intrinsics 로 3D 에 올린 점. grasp 와 trajectory 를 이 점 기준 상대 좌표로 바꿔 embodiment 간 전이를 가능하게 하는 정규화 원점입니다.
- **Spatial Binning** — 연속 6D 포즈 공간을 이산 구간으로 쪼개 각 구간을 하나의 토큰으로 삼는 양자화. 연속값 회귀 대신 언어 모델의 자기회귀 예측기를 그대로 재사용하기 위한 장치입니다.
- **SEG Token** — LISA 계열에서 가져온 분할용 특수 토큰. 이 토큰의 임베딩이 분할 디코더로 흘러 픽셀 단위 확률을 만듭니다.
- **DINOv2** — 자기지도 학습 기반 밀집 시각 특징 추출기. VLM 자체 vision encoder 가 약한 세밀 공간 grounding 을 보강하는 보조 인코더로 붙습니다.
- **Soft Dice Loss** — 전경 픽셀이 극소수인 불균형 분할에서 쓰는 겹침 기반 손실. 본 논문은 $`s=1.0`$, $`p=1.5`$ 로 부드러운 경계를 다룹니다.
- **In-Context Trajectory Guidance** — 상위 VLM 이 $`\{-1,0,1\}^{3}`$ 방향 벡터를 주고, 그 방향 근처에서 첫 궤적 토큰을 샘플링하도록 유도하는 추론 시점 개입. 지도를 읽는 사람이 "일단 앞쪽으로"라고 첫걸음만 잡아 주는 것과 같습니다.
- **Agent-Agnostic Scene** — ego segmentation 으로 촬영자의 손·팔을 지우고 inpainting 으로 메운 장면. 모델이 "사람 손이 보이는 프레임"이라는 편향을 학습하지 않게 하려는 전처리입니다.

---

## 🔬 방법론

### 직관

이 논문이 붙잡는 핵심 관찰은 단순합니다. 인간 영상에는 로봇 액션 라벨이 없지만, **물체 쪽에서 보면 라벨이 이미 들어 있습니다**. 어떤 사람이 냄비 뚜껑 손잡이를 잡고 위로 들어올렸다면, 그 영상은 "손잡이가 상호작용 지점이고, 손 모양은 이러했으며, 궤적은 위쪽이었다"는 사실을 이미 담고 있습니다. 사람 손과 로봇 그리퍼는 다르지만, **물체 쪽에 새겨진 이 정보는 신체 구조와 무관**합니다. 그래서 정책을 직접 배우는 대신 이 물체 중심 정보를 배우고, 실행 시점에 로봇 몸에 맞게 번역하자는 것이 전체 전략입니다.

문제는 이 정보를 영상에서 꺼내는 일입니다. 논문의 전반부(§III)는 순수하게 이 추출 파이프라인입니다. ego 영상에서 접촉이 일어나는 순간의 프레임을 VLM 으로 골라내고, 손·물체 검출기와 분할 모델로 접촉 영역을 계산하고, 손 메쉬 복원으로 그 순간의 손 자세를 얻고, 단안 깊이 추정과 카메라 포즈 추정으로 3D 손 궤적을 복원합니다. 중간에 한 가지 미묘한 처리가 들어가는데, 사람 손과 팔을 화면에서 지우고 그 자리를 그림으로 메워 버립니다. 그러지 않으면 모델이 "사람 손이 물체 근처에 있는 이미지"만을 조건으로 학습하게 되어, 손이 없는 로봇 시점 이미지에서는 작동하지 않기 때문입니다.

후반부(§IV)는 이렇게 얻은 세 종류의 정답을 **한 모델이 동시에** 배우게 만드는 부분입니다. 여기서 저자들이 택한 방법은 새 아키텍처를 짜는 것이 아니라, 이미 언어와 이미지를 잘 이해하는 VLM 의 어휘에 세 개의 새 단어를 추가하는 것입니다. `<SEG>` 는 "여기서 히트맵을 그려라", `<GRASP>` 는 "여기서 손 자세를 내놓아라", `<p0>` 부터 시작하는 궤적 토큰들은 "여기서부터 이동 경로를 한 칸씩 말해라"에 해당합니다. 앞의 두 개는 토큰 임베딩을 전용 디코더에 흘려보내고, 궤적은 아예 공간을 구간으로 쪼개 토큰화했기 때문에 언어 모델이 다음 단어를 예측하듯 그대로 뱉어냅니다. 이렇게 하면 세 예측이 같은 문맥 표현을 공유하므로, 히트맵이 가리키는 지점과 손 모양과 궤적 방향이 서로 모순되지 않게 학습됩니다 — 이것이 논문이 말하는 cross-modal 상관입니다.

마지막 한 가지 현실적 문제가 남습니다. 모델은 2D 이미지 한 장과 문장만 보고 3D 궤적을 말해야 하므로, 물리적으로 말이 안 되는 경로(벽을 통과하거나 반대 방향으로 미는)를 뱉을 수 있습니다. 논문은 이를 학습으로 풀지 않고 **추론 시점 두 개의 안전장치**로 처리합니다. 하나는 상위 VLM 에게 "이 과제는 대략 어느 방향이냐"를 물어 첫 궤적 토큰만 그 방향 근처에서 뽑는 것이고, 다른 하나는 여러 후보를 뽑아 놓고 장면 포인트 클라우드를 복셀로 만들어 충돌하지 않는 것을 고르는 것입니다.

![Figure 1 — VLAff 개요: ego 영상 → actionable affordance → 로봇 조작](https://arxiv.org/html/2608.05215/overview.png)

> "Fig. 1: We present VLAff, a Vision-Language-Affordance model that learns actionable affordances such as visual, grasp, trajectory from large-scale egocentric human videos to enable robot manipulation across diverse tasks." (§I)
(왼쪽의 인간 영상 입력에서 오른쪽 로봇 실행까지가 한 줄로 이어져, 세 affordance 가 중간 표현으로 놓이는 논문의 전체 구도를 한 장에 담고 있습니다.)

### 문제 정식화

논문은 과제를 멀티모달 예측 문제로 못 박고 시작합니다. 입력은 RGB 이미지 $`\mathbf{I}\in\mathbb{R}^{H\times W\times 3}`$ 와 자연어 지시 $`\mathbf{L}`$ 이고, 출력은 세 개의 상호보완적 표현입니다 (식 1):

$$f_{\text{VLAff}}(\mathbf{I},\mathbf{L})=(\mathbf{A}_{v},\mathbf{A}_{g},\mathbf{A}_{t})$$

각 항의 정의는 본문 표기 그대로 다음과 같습니다.

- **visual affordance** — $`\mathbf{A}_{v}\in\mathbb{R}^{H\times W}`$, 장면 내 관련 영역의 확률 분포를 나타내는 히트맵.
- **grasp affordance** — $`\mathbf{A}_{g}\in\mathbb{R}^{96}`$, MANO 파라미터로 표현된 grasp pose. 전역 손목 회전 + 15개 국소 관절 회전이며 각각 6D 회전 표현을 씁니다 ($`(1+15)\times 6=96`$).
- **trajectory affordance** — $`\mathbf{A}_{t}\in\mathbb{R}^{T\times 6}`$, 상호작용 이후 손의 궤적. 각 waypoint 는 translation(3D) + rotation(3D)이고 $`T`$ 는 waypoint 개수입니다.

세 출력을 하나의 좌표계로 묶는 장치가 anchor point 입니다.

> "To generate object-centric actionable affordances, we first identify the peak interaction point from the visual affordance heatmap. We then project this 2D point to 3D space using the camera intrinsics and depth information to obtain 3D anchor point." (§III-A)
(히트맵의 최댓값이 단순히 시각화 결과가 아니라 **나머지 두 modality 의 좌표 원점**이라는 뜻입니다. 이 구조 때문에 히트맵이 틀리면 grasp 와 trajectory 도 같이 틀어지는 직렬 의존이 생기고, 실제로 §V-B3 ablation 에서 히트맵 제거 시 학습이 완전히 실패하는 결과로 나타납니다.)

> "This object-centric formulation enables effective transfer of learned human manipulation strategies across different embodiments, as the complete affordance representation provides both the where (visual), how (grasp), and motion (trajectory) information necessary for execution." (§III-A)
(embodiment 이전 가능성의 근거를 "물체 기준 좌표계 + 세 정보의 완결성"에 두는 설계 선언입니다. 로봇 쪽 액션 공간을 전혀 가정하지 않기 때문에, 뒤에서 gripper 로 실행할 때 별도의 retargeting 단계가 필요해집니다.)

### 데이터 추출 파이프라인

§III-B 는 사람 라벨 없이 위 세 정답을 만드는 절차이며, 각 단계가 서로 다른 사전학습 모델에 의존합니다.

- **데이터 준비** — ego 영상 데이터셋의 기존 언어 설명 · 시간 주석을 활용해 상호작용 시점 주변 프레임 $`\{I_{t}\}`$ 를 샘플링한 뒤, 사전학습 대형 VLM 에 서브샘플 프레임을 질의해 접촉 keyframe $`\{I_{c}\}`$ · action label · 물체 범주 · 상호작용 손 정보를 얻습니다. 즉 keyframe 선택 자체가 VLM 판단에 위임되어 있습니다.
- **hand-object 상호작용 추출** — keyframe 에 hand-object detector 로 손·물체 bounding box 를 얻고, 물체 마스크와 2D hand keypoint 를 뽑은 뒤 **fingertip keypoint 와 물체 마스크의 교집합**으로 접촉 영역을 정의하고 이를 추적합니다. 접촉 정의가 기하학적 교집합 규칙이라는 점이 중요합니다 — 실제 접촉력이 아니라 화면상 겹침입니다.
- **3D 손 복원 + 시각 편향 제거** — MANO 파라미터로 손 자세·형상을 복원하고, ego 시점 편향을 줄이기 위해 ego segmentation → inpainting 을 수행합니다.
- **ego-centric SfM** — inpaint 된 프레임에 단안 깊이 추정을 돌리고, intrinsics 가 없는 영상은 추정합니다. 이어서 카메라 포즈를 추정하되 **물체 마스크와 ego 마스크로 동적 영역을 걸러내** 정적 배경만으로 포즈를 풉니다. 마지막으로 추정된 포즈와 깊이로 3D 손 궤적을 추적해 접촉 전·후 운동 패턴을 모두 확보합니다.

> "We generate object masks [44] and extract 2D hand keypoints [45]. Contact regions are identified by computing the intersection between fingertip keypoints and object masks, then tracked [46]." (§III-B)
(접촉의 ground truth 가 "손끝 키포인트가 물체 마스크 안에 들어왔는가"라는 2D 판정이라는 사실이 여기서 확정됩니다. 촉각·힘 센서가 아니라 시각 기하만으로 정의되므로, 접촉의 존재는 잡아내되 접촉의 세기·안정성은 데이터에 원리적으로 담기지 않습니다.)

### 아키텍처

![Figure 2 — VLAff 모델 구조: vision encoder + VLM + 3종 디코더](https://arxiv.org/html/2608.05215/model_architecture.png)

> "Fig. 2: VLAff model architecture showing the integration of vision encoder, VLM, and specialized decoders for visual, grasp, and trajectory affordance prediction." (§IV)
(하나의 VLM 시퀀스 안에 세 특수 토큰이 함께 놓이고, 그중 두 개만 별도 디코더로 빠져나가는 비대칭 구조가 그림의 요점입니다.)

구조의 출발점은 사전학습 VLM 을 **affordance 토큰으로 확장**하는 것입니다.

> "To enable unified learning of visual, grasp, and trajectory affordances, we extend a pre-trained vision-language model (VLM) with specialized affordance tokens." (§IV)
(새 백본을 설계하지 않고 어휘 확장 + 디코더 부착으로 끝낸다는 선언이며, 덕분에 VLM 의 언어·상식 능력이 그대로 남습니다. 반대로 말하면 affordance 예측 성능의 상당 부분이 백본 선택에 종속됩니다.)

세 토큰의 역할은 다음과 같이 갈립니다.

- **`<SEG>` (Visual Affordance Token)** — VLM 어휘에 추가되는 분할 토큰. LISA 방식을 따라 이 토큰 임베딩이 분할 디코더로 흘러 픽셀 단위 affordance 확률을 만듭니다.
- **`<GRASP>` (Grasp Token)** — MANO 손 파라미터를 인코딩하는 토큰. VLM 을 fine-tune 해 언어 지시와 손 구성 사이의 연관을 학습시키며, 96차원 $`\mathbf{A}_{g}`$ 를 예측합니다.
- **`<p0>, …, <pN-1>` (Trajectory Tokens)** — 6D 포즈 공간(3D translation + 3D rotation)을 spatial binning 으로 이산화해 만든 궤적 어휘. 학습 시 연속 waypoint 를 최근접 bin 인덱스로 변환하고, 모델은 토큰 시퀀스를 예측한 뒤 다시 연속 6D 포즈로 디코딩합니다.

> "By introducing these specialized affordance tokens, the model enables joint learning across all three affordance modalities and captures rich correlations between visual interaction regions, grasp configurations, and motion patterns." (§IV)
(joint learning 의 메커니즘이 "공유 파라미터"가 아니라 **하나의 자기회귀 시퀀스 안에 세 토큰이 공존한다**는 데 있다는 설명입니다. 세 예측이 같은 문맥 임베딩을 조건으로 하므로 어텐션을 통해 서로를 볼 수 있습니다.)

모듈 구성은 네 부분입니다.

- **VLM** — 이미지와 언어 지시를 받아 시퀀스 전체 토큰의 문맥 임베딩을 생성합니다. 궤적 토큰은 위치 $`t`$ 까지의 문맥을 조건으로 다음 토큰을 예측하는 자기회귀 방식으로 생성되며, end-of-trajectory 토큰이 나오거나 최대 길이에 도달할 때까지 이어집니다.
- **Vision Encoder** — VLM 자체 인코더의 세밀 공간 grounding 한계를 보완하기 위해 **DINOv2 를 추가 인코더로 병렬 부착**합니다. 논문은 이를 "VLM 의 추론 능력에 더 강한 시각 grounding 을 보완하는" 구성으로 설명합니다.
- **Visual Affordance Decoder** — DINOv2 특징 $`\mathbf{F}_{v}`$ 와 `<SEG>` 토큰 임베딩 $`\mathbf{h}_{seg}`$ 를 융합하고, 일련의 업샘플링·융합 레이어를 거쳐 최종 히트맵 $`\mathbf{A}_{v}\in\mathbb{R}^{H\times W}`$ 를 만듭니다.
- **Grasp Decoder** — `<GRASP>` 토큰 임베딩 $`\mathbf{h}_{grasp}`$ 를 받아 전역 손목 회전 + 15개 국소 관절 회전을 6D 표현으로 예측해 96차원 $`\mathbf{A}_{g}`$ 를 구성합니다.

> "While VLMs excel at general knowledge and reasoning capabilities, they often exhibit limitations in fine-grained visual grounding tasks that require precise spatial understanding." (§IV-A)
(DINOv2 를 왜 굳이 하나 더 붙였는지에 대한 유일한 근거 문장입니다. 뒤의 §V-B1 에서 성능 우위의 두 요인 중 하나로 "DINOv2 의 part-aware 특징"을 지목하므로, 이 보조 인코더는 장식이 아니라 핵심 주장 중 하나입니다 — 다만 DINOv2 유무 ablation 은 논문에 없습니다.)

### 학습 목표 / 손실

세 modality 가 각각 다른 성격의 문제이므로 손실도 세 종류로 나뉩니다.

**Visual Affordance Loss** — 히트맵 예측의 극심한 전경/배경 불균형을 다루기 위해 Soft Dice Loss 를 씁니다 (식 2):

$$\mathcal{L}_{visual}=1-\frac{2\sum_{i,j}(\mathbf{A}_{v}^{pred}(i,j))^{p}\cdot(\mathbf{A}_{v}^{gt}(i,j))^{p}+s}{\sum_{i,j}(\mathbf{A}_{v}^{pred}(i,j))^{p}+\sum_{i,j}(\mathbf{A}_{v}^{gt}(i,j))^{p}+s}$$

여기서 $`\mathbf{A}_{v}^{pred}`$ 와 $`\mathbf{A}_{v}^{gt}`$ 는 예측·정답 히트맵, $`s=1.0`$ 은 smoothing factor, $`p=1.5`$ 는 부드러운 경계 처리를 위한 power parameter 입니다. 지수 $`p`$ 가 1 보다 크다는 점이 이 손실의 특징으로, 확률값을 제곱 이상으로 눌러 애매한 중간 확신 픽셀의 기여를 줄이고 확신이 높은 영역만 겹침 계산에 반영되게 만듭니다. affordance 히트맵이 물체 전체가 아니라 손잡이 같은 국소 부위를 가리켜야 한다는 요구와 맞물린 선택입니다.

**Grasp Affordance Loss** — grasp pose 는 연속값 회귀이므로 Smooth L1 을 씁니다 (식 3):

$$\mathcal{L}_{grasp}=\frac{1}{J}\sum_{k=1}^{J}f(x_{k}),\quad x_{k}=\mathbf{A}_{g}^{pred}[k]-\mathbf{A}_{g}^{gt}[k]$$

$`J=96`$ 이고 $`f(x)=0.5x^{2}`$ if $`|x|<1`$, 그렇지 않으면 $`|x|-0.5`$ 입니다. 6D 회전 표현 96개 성분을 **차원별 독립 스칼라로 취급**하는 손실이라는 점에 주의가 필요합니다 — 회전 다양체 위의 측지 거리가 아니라 유클리드 성분 오차이므로, 손 자세의 물리적 유사도와 손실값이 정확히 비례하지는 않습니다.

**Trajectory Affordance Loss** — 궤적은 토큰 예측 문제로 환원되었으므로 자기회귀 언어 모델의 표준 Cross-Entropy 를 그대로 씁니다 (식 4):

```math
\mathcal{L}_{traj}=-\frac{1}{T}\sum_{t=1}^{T}\log P(\texttt{<pi>}_{t}^{gt}|\mathbf{I},\mathbf{L},\texttt{<p*>}_{1:t-1})
```

$`\texttt{<pi>}_{t}^{gt}`$ 는 위치 $`t`$ 의 정답 궤적 토큰입니다. 이 형태가 뜻하는 바는 궤적 오차가 **기하 거리가 아니라 bin 분류 오차**로 측정된다는 것입니다. 인접 bin 을 틀리는 것과 반대편 bin 을 틀리는 것이 같은 벌점을 받으므로, bin 해상도 설정이 궤적 품질에 직결됩니다.

**Total Loss** — 세 손실의 가중합입니다 (식 5):

$$\mathcal{L}_{total}=\lambda_{v}\mathcal{L}_{visual}+\lambda_{g}\mathcal{L}_{grasp}+\lambda_{t}\mathcal{L}_{traj}$$

$`\lambda_{v}`$, $`\lambda_{g}`$, $`\lambda_{t}`$ 는 각 modality 기여를 조절하는 가중 하이퍼파라미터라고만 서술되고, **구체적 값은 본문·표 어디에도 제시되지 않습니다** `(원문 미명시)`. 세 손실의 스케일이 서로 다르므로(Dice 는 $`[0,1]`$, Smooth L1 은 무계, CE 는 어휘 크기 의존) 이 값들은 재현에 결정적인데, 공개되지 않은 상태입니다.

### 추론 시점 궤적 샘플링 전략

§IV-C 는 학습이 아니라 추론 시점 개입입니다. 문제의식은 명확합니다 — 2D 이미지와 문장만으로 3D 궤적을 뱉으면 물리적으로 타당하지 않은 경로가 나올 수 있다는 것입니다.

**In-Context Trajectory Guidance.** 상위 VLM(GPT 계열)에게 과제 프롬프트와 상호작용 물체를 주고 ego(카메라) 좌표계의 3D 방향 벡터 $`[d_{x},d_{y},d_{z}]`$ 를 받습니다. 각 성분은 $`\{-1,0,1\}`$ 로 제한되며 $`d_{x}`$ 는 수평(오른쪽 $`+1`$), $`d_{y}`$ 는 수직(아래 $`+1`$), $`d_{z}`$ 는 깊이(카메라에서 멀어지는 전방 $`+1`$)이고 $`0`$ 은 해당 축 무운동을 뜻합니다. 예컨대 $`[0,0,1]`$ 은 밀기, $`[1,0,-1]`$ 은 오른쪽 뒤로 당기기입니다. 이 유도는 **첫 궤적 토큰에만** 적용되며, 초기 xyz 위치 토큰을 정규화·스케일된 방향 벡터 주변에서 샘플링합니다 (식 6):

$$\mathbf{p}_{1}\sim\mathcal{N}(\mathbf{p}_{contact}+s\cdot\frac{\mathbf{d}_{guide}}{\|\mathbf{d}_{guide}\|},\sigma^{2}\mathbf{I})$$

$`\mathbf{p}_{contact}`$ 는 상호작용 지점, $`\mathbf{d}_{guide}`$ 는 VLM 이 준 방향 벡터, $`s`$ 는 스케일 인자, $`\sigma`$ 는 샘플링 분산을 조절합니다. 첫 토큰만 건드리는 이유는 자기회귀 구조상 첫 토큰이 이후 전체 궤적의 조건이 되기 때문이며, 나머지 세밀한 형태는 인간 시연에서 학습한 분포에 맡긴다는 의도입니다.

> "This approach enables our model to produce trajectories that align with high-level task understanding while maintaining fine-grained spatial details learned from human demonstrations." (§IV-C)
(상위 의미 이해는 외부 VLM 이, 국소 운동 패턴은 학습된 분포가 담당하는 역할 분담을 명시합니다. 뒤집어 보면 궤적의 대역적 방향성이 학습된 모델 자체로는 충분히 신뢰되지 않는다는 자기 진단이기도 합니다.)

**Sampling-Based Trajectory Selection.** nucleus sampling(top-p filtering)으로 $`K`$ 개 후보 궤적을 뽑고, 충돌 회피와 방향 정렬을 균형 잡는 복합 목적으로 최적 후보를 고릅니다. 충돌 검사는 3D 공간을 복셀화해 장면 포인트 클라우드와 깊이 맵에서 점유된 복셀에 궤적 waypoint 가 닿는지 확인하는 방식이며, 복합 목적값이 가장 낮은 궤적이 최종 출력이 됩니다. $`K`$ · top-p 값 · 복합 목적의 가중치는 `(원문 미명시)` 입니다.

### 학습 셋업

- **백본** — 기본 VLM 은 Qwen2.5-VL, 추가 vision encoder 는 DINOv2 입니다.
- **학습 데이터** — 최종 EgoAffordance 는 204,025 episode / 5,782,431 visual heatmap / 11,612,524 trajectory sequence 이며, 세밀한 visual affordance 예측을 위해 HANDAL 과 SceneFun3D 의 물체 수준 affordance 주석을 추가로 섞습니다.
- **소스 ego 데이터셋** — 본문은 "egocentric video datasets" 라고만 쓰고 어떤 코퍼스를 실제로 소비했는지 열거하지 않습니다 `(원문 미명시)`. Table I 의 비교 표에 H2O · HOI4D · EPIC-KITCHENS · HD-EPIC · Ego4D · Ego-Exo4D 가 등장하지만, 이는 데이터셋 비교표이지 소스 명세가 아닙니다.
- **옵티마이저 · 학습률 · 배치 · 스케줄 · 학습 하드웨어 · 학습 시간 · 토큰 어휘 크기 $`N`$ · waypoint 수 $`T`$ · $`\lambda`$ 값** — 모두 `(원문 미명시)` 입니다. IROS 8쪽 포맷의 제약으로 보이지만, 재현 관점에서는 치명적인 공백입니다.

---

## 📊 실험 설정과 결과

평가는 네 축입니다 — visual affordance 예측 품질, 궤적 생성 유효성, zero-shot 조작, affordance-guided 정책 학습.

### 데이터셋 비교 (Table I)

논문이 EgoAffordance 의 위치를 주장하는 표입니다. 기존 corpus 는 visual affordance 계열(Contact 만 ✓)과 egocentric HOI 계열(Hand Pose / Camera Traj 만 ✓)로 갈려 있고, 세 주석을 모두 갖춘 것은 EgoAffordance 뿐이라는 구성입니다.

| Type | Dataset | Frame | Inst (Act) | Obj | Contact | Hand Pose | Camera Traj |
|---|---|---|---|---|---|---|---|
| Visual Affordance | UMD | 30K | 7 | 17 | ✓ | ✗ | ✗ |
| Visual Affordance | AGD20K | 23.8K | 36 | 50 | ✓ | ✗ | ✗ |
| Visual Affordance | IIT-AFF | 8.8K | 9 | 10 | ✓ | ✗ | ✗ |
| Visual Affordance | ADE-Aff | 10K | 7 | 150 | ✓ | ✗ | ✗ |
| Visual Affordance | HOVA-500K | 500K | 675 | 1.7K | ✓ | ✗ | ✗ |
| Egocentric HOI | H2O | 571K | 36 | 8 | ✗ | ✓ | ✓ |
| Egocentric HOI | HOI4D | 2.4M | 800 | 16 | ✗ | ✓ | ✓ |
| Egocentric HOI | EPIC-KITCHENS | 11.5M | 125 | 331 | ✗ | ✗ | ✓ |
| Egocentric HOI | HD-EPIC | 4.4M | 1.2K | 17K | ✗ | ✗ | ✓ |
| Egocentric HOI | Ego4D | 3.7M | 1.7K | 4.3K | ✗ | ✗ | ✓ |
| Egocentric HOI | Ego-Exo4D | 1.4M | 4.5K | - | ✗ | ✓ | ✓ |
| Actionable Affordance | EgoAffordance (Ours) | 5.6M | 1.7K | 16.4K | ✓ | ✓ | ✓ |

프레임 수만 보면 EPIC-KITCHENS(11.5M) · HD-EPIC(4.4M) · Ego4D(3.7M) 가 EgoAffordance(5.6M)와 같은 자릿수이며, 이 표의 주장은 **규모가 아니라 주석 완결성**입니다. 물체 범주 16.4K 는 HD-EPIC(17K) 다음이고 나머지를 크게 앞섭니다.

### Visual Affordance 예측 (Table II)

테스트셋은 각 egocentric video 데이터셋에서 무작위 추출한 500 scene 입니다. 지표는 IoU(히트맵을 $`[0,1]`$ 정규화 후 0.5 임계로 이진화해 겹침 측정) · NSS · SIM · KLD 이며, LISA 는 affordance 히트맵을 직접 내지 않으므로 분할 마스크를 $`[0,1]`$ 로 정규화해 비교했습니다.

| Method | IoU ↑ | NSS ↑ | SIM ↑ | KLD ↓ |
|---|---|---|---|---|
| VRB | 0.013 | -0.032 | 0.052 | 6.942 |
| UAD | 0.063 | 1.095 | 0.097 | 5.687 |
| 3DOI | 0.012 | 0.742 | 0.034 | 4.252 |
| LISA | 0.113 | 1.342 | 0.025 | 3.886 |
| Ours | **0.121** | **1.542** | **0.142** | **2.517** |

> "VLAff achieves state-of-the-art performance across all segmentation-based metrics, demonstrating the effectiveness of our unified affordance learning approach." (§V-B1, Table II)
(네 지표 모두에서 1위라는 주장이며 실제 수치도 그렇습니다. 다만 격차의 성격이 지표마다 다릅니다 — IoU 는 LISA 대비 0.113 → 0.121 로 근소하고, SIM 은 0.097 → 0.142, KLD 는 3.886 → 2.517 로 큽니다. 즉 **이진화 후 겹침**보다 **확률 분포로서의 형태**에서 우위가 훨씬 뚜렷합니다. affordance 히트맵을 하류에서 anchor point 추출에 쓰는 본 논문 구조에서는 분포 형태 쪽이 실사용에 더 가까운 지표입니다.)

절대 수치 자체는 낮다는 점도 함께 읽어야 합니다. 최고 IoU 가 0.121 이라는 것은 이진 마스크 기준으로는 정답 영역과 12 % 남짓만 겹친다는 뜻이며, 저자들도 이 값을 절대 성능이 아니라 상대 비교로만 사용합니다.

논문이 밝히는 baseline 별 실패 원인과 자기 우위의 귀인은 다음과 같습니다.

- **VRB** — 밀집 히트맵이 아니라 이산 접촉점을 예측하므로 세밀한 국소화가 제한됨.
- **UAD** — 렌더링된 물체 이미지로 학습되어 어수선한 실환경에서 취약함.
- **LISA** — 물체·인스턴스 수준 분할 데이터로 학습되어 특정 접촉점이 아니라 **물체 전체**를 예측하는 경향.

> "We attribute VLAff's superior performance to two key factors: (1) the integration of DINOv2's part-aware visual features, which enable fine-grained localization of interaction regions, and (2) training on our large-scale, diverse EgoAffordance dataset spanning multiple domains and object categories." (§V-B1)
(우위의 원인을 두 가지로 귀인하지만, **둘 중 어느 쪽이 얼마나 기여했는지 분리하는 ablation 이 없습니다.** DINOv2 제거 실험도, 데이터 규모 스케일링 곡선도 제시되지 않아 이 문장은 해석이지 측정이 아닙니다.)

![Figure 3 — 실환경 visual affordance 예측 정성 비교](https://arxiv.org/html/2608.05215/visual_affordances.png)

> "Fig. 3: Visual affordance prediction results in the wild. We show visual affordance predictions from VLAff and baseline methods on diverse manipulation scenarios. VLAff demonstrates superior localization of interaction regions compared to existing methods." (§V-A)
(LISA 가 물체 전체를 칠하고 VLAff 는 손잡이 수준으로 좁힌다는 위 분석을 눈으로 확인시켜 주는 그림입니다. IoU 격차가 작은데도 실사용 차이가 크다는 주장의 정성적 근거에 해당합니다.)

### Zero-Shot 조작 (Table III)

시뮬레이션은 IsaacGym 상에서 Ag2Manip 환경에 포함된 PartManip · FrankaKitchen · ManiSkill 과제 중 10개 가사 과제를, 실환경은 Fetch 와 PR2 모바일 매니퓰레이터로 실제 주방 5개 과제를 각각 과제당 10회 시행합니다. 어떤 방법도 과제별 추가 학습을 하지 않습니다. baseline 은 grasp pose 를 직접 내지 않으므로 GraspNet 으로 gripper pose 를 만들고, VLAff 는 예측된 hand pose 에서 retargeting 으로 gripper pose 를 추정합니다.

| Method | T01 | T02 | T03 | T04 | T05 | T06 | T07 | T08 | T09 | T10 | Sim Avg | T11 | T12 | T13 | T14 | T15 | Real Avg |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RAM | 40 | 20 | 50 | 80 | 90 | 40 | 40 | 60 | 90 | 0 | 51.0 | 60 | 20 | 20 | 20 | 0 | 24.0 |
| VRB | 20 | 10 | 60 | 70 | 90 | 30 | 50 | 50 | 80 | 20 | 48.0 | 60 | 40 | 20 | 20 | 0 | 28.0 |
| GFlow | 10 | 10 | 60 | 100 | 90 | 60 | 70 | 50 | 90 | 10 | 55.0 | 80 | 20 | 20 | 20 | 0 | 28.0 |
| VidBot | 70 | 80 | 80 | 100 | 100 | 70 | 100 | 100 | 100 | 50 | **85.0** | 100 | 60 | 60 | 40 | 0 | 52.0 |
| Ours | 70 | 60 | 70 | 100 | 100 | 80 | 90 | 100 | 100 | 60 | 83.0 | 100 | 60 | 80 | 60 | 40 | **68.0** |

시뮬 과제: T01 Open Hinge Cabinet · T02 Open Slide Cabinet · T03 Open Microwave · T04 Close Microwave · T05 Pick Up Kettle · T06 Open Dish Washer · T07 Lift Lid · T08 Pull Drawer · T09 Close Hinge Cabinet · T10 Turn Faucet. 실환경 과제: T11 Open Drawer · T12 Pick Up Bucket · T13 Open Pot Lid · T14 Take Pan · T15 Pick Up Kettle.

> "In simulation tasks, VLAff achieves an average success rate of 83.0%, demonstrating strong generalization performance close to VidBot [26] (85.0%), the current state-of-the-art zero-shot manipulation framework." (§V-B2, Table III)
(시뮬에서는 2위라는 사실을 저자들이 먼저 인정합니다. 이 정직한 배치가 뒤의 실환경 주장을 강화하는 구조입니다.)

> "VidBot's strong overall performance in simulation can be attributed to its ability to access spatial input such as depth, enabling the model to directly leverage spatial characteristics for manipulation planning, which is particularly beneficial in controlled simulation environments." (§V-B2)
(시뮬 열세의 원인을 "VidBot 은 깊이 입력을 직접 받는다"로 설명합니다. 곧 VLAff 의 RGB-only 입력이 통제된 환경에서는 불리하게 작용한다는 자기 진단이며, 이 진단은 실환경에서 뒤집힙니다.)

> "Notably, VLAff demonstrates superior performance on real-world tasks, achieving an average success rate of 68.0%, 16 percentage points higher than VidBot's 52.0%." (§V-B2, Table III)
(논문의 핵심 실증입니다. 대규모 실환경 ego 영상으로 학습했다는 데이터 선택이 통제되지 않은 실제 장면에서 회수된다는 주장이며, sim→real 순위 역전 자체가 증거로 쓰입니다.)

과제별로 뜯어보면 격차의 출처가 분명합니다.

- **T15 Pick Up Kettle** — 전 baseline 이 0 인데 VLAff 만 40 입니다. 같은 과제의 시뮬 버전(T05)에서는 모든 상위 방법이 90–100 이므로, 이 과제는 **실환경 고유의 어려움**(주전자 손잡이라는 좁은 접촉 부위 + 어수선한 배경)을 측정하는 셀이고 정확히 여기서만 VLAff 가 점수를 냅니다.
- **T13 Open Pot Lid (80 vs 60)** · **T14 Take Pan (60 vs 40)** — 손잡이 국소화가 성패를 가르는 과제군에서 일관되게 앞섭니다.
- **T02 Open Slide Cabinet (60 vs 80)** · **T03 Open Microwave (70 vs 80)** — 시뮬 열세는 이 두 과제에 집중되어 있고, 둘 다 깊이 정보가 유리한 대형 관절체 조작입니다.
- **T10 Turn Faucet** — 시뮬 전 과제 중 최난도로, VLAff 60 이 최고이며 RAM 은 0, GFlow 는 10 입니다.

> "Our failure cases primarily stem from incorrect initial direction sampling during trajectory generation, which can be improved through better integration of scene context and spatial reasoning." (§V-B2)
(실패의 주 원인을 §IV-C 의 첫 토큰 방향 샘플링으로 지목합니다. 즉 in-context guidance 가 성능의 상한을 만드는 지점이기도 하다는 자기 진단입니다.)

![Figure 4 — 실기 로봇 조작 실험: 생성된 affordance 와 실행](https://arxiv.org/html/2608.05215/experiment.png)

> "Fig. 4: Robot manipulation experiments. We visualize the generated affordances and their application to real robot manipulation tasks." (§V-B2)
(예측된 히트맵·grasp·궤적이 실제 Fetch/PR2 실행으로 이어지는 경로를 시각화한 그림으로, Table III 실환경 열의 정성적 대응물입니다.)

### Affordance-Guided 조작 학습 (Fig. 5, ablation)

영상에서 배운 affordance 와 물리 환경 사이의 간극을 메우기 위해, 예측 affordance 를 사전지식으로 쓰는 실환경 RL 을 돌립니다. 보상은 두 성분입니다 — (1) VLM 이 과제 성공/실패를 판정하는 sparse 성공 보상, (2) 예측된 접촉점과 궤적에 기반한 dense affordance guidance 보상(세부는 supplementary). Ablation 은 실환경 "Open Fridge" 과제에서 전체 modality 사용 대비 한 번에 하나씩 제거하는 구성입니다.

| 구성 | 결과 (§V-B3 서술 기준) |
|---|---|
| 전체 modality | 가장 좋은 성능을 가장 효율적으로 달성 |
| visual heatmap 제거 | 학습 episode 수와 무관하게 **성공적 조작에 완전히 실패** |
| grasp pose 제거 | 상대적으로 영향이 작음 |
| trajectory 제거 | (본문은 세 modality 가 상호보완적이라고만 서술; 개별 수치 미제시) |

> "Most critically, when the visual affordance heatmap is removed, the model completely fails to achieve successful manipulation regardless of the number of training episodes, demonstrating that visual affordance is absolutely essential for manipulation learning as it provides the most important cues for object interaction by indicating where to make contact." (§V-B3)
(세 modality 가 대등한 삼각형이 아니라 **히트맵이 뿌리이고 나머지가 가지**라는 구조를 밝힌 결과입니다. §III-A 의 anchor point 설계를 떠올리면 당연한 귀결이기도 합니다 — 히트맵의 peak 가 나머지 두 modality 의 좌표 원점이므로, 히트맵이 없으면 grasp 와 trajectory 는 기준점을 잃습니다.)

> "Interestingly, grasp pose plays a less significant role in manipulation learning, which we attribute to the fundamental morphological differences between human hands and robot grippers—the exact hand configuration from human demonstrations does not directly transfer to gripper-based manipulation." (§V-B3)
(본 저장소 관점에서 이 논문에서 가장 중요한 한 문장입니다. 96차원 MANO grasp 라는 논문의 세 기둥 중 하나가, **실행 embodiment 가 2지 그리퍼이기 때문에** 효용이 낮았다는 고백입니다. 이는 grasp affordance 자체의 무용함이 아니라 평가 embodiment 의 선택 문제이며, 다지 손으로 실행했을 때의 값은 논문에 없습니다.)

Fig. 5 는 SVG 학습 곡선으로 제시되며, 각 구성의 성공률 수치나 episode 수는 본문에 텍스트로 나오지 않습니다 `(원문 미명시)`.

---

## ⚖️ 한계

- **저자 명시 한계 — 물리적으로 타당하지 않은 궤적** — 결론부에서 "occasional generation of implausible trajectories that may not respect physical constraints" 를 유일한 한계로 적고, 3D scene-aware 아키텍처를 향후 과제로 제시합니다. 근본 원인은 학습 신호에 물리가 전혀 들어 있지 않다는 데 있습니다 — 궤적 손실은 bin 분류 CE 이므로 "관통 불가" 같은 제약이 학습으로 들어올 경로가 없고, 그래서 §IV-C 의 추론 시점 복셀 충돌 검사라는 사후 필터로 막고 있습니다. 필터는 충돌은 걸러도 동역학적 타당성(속도·가속·접촉력)은 판정하지 못합니다.
- **DINOv2 기여가 미측정** — §V-B1 은 성능 우위의 절반을 DINOv2 의 part-aware 특징에 귀속시키지만 해당 인코더를 뺀 대조군이 없습니다. VLM 단독으로 어디까지 가는지, 즉 이 논문의 핵심 아키텍처 선택이 실제로 필요한지가 논문 내부에서 검증되지 않습니다.
- **"unified 가 개별보다 낫다"는 핵심 가설의 직접 검증 부재** — §V-B1 은 통합 학습이 visual affordance 성능을 높인다는 가설이 검증되었다고 선언하지만, 비교 대상은 **다른 논문의 다른 모델들**입니다. 같은 백본·같은 데이터로 visual affordance 만 학습한 단일 modality 대조군이 없어, 성능 우위가 통합 학습에서 왔는지 데이터 규모에서 왔는지 구분되지 않습니다. 논문의 이름을 건 주장이 가장 약하게 검증된 지점입니다.
- **접촉 정의가 시각 기하에 한정** — ground truth 접촉은 fingertip keypoint 와 물체 마스크의 교집합입니다. 이 정의로는 "닿았다"는 잡히지만 얼마나 세게, 어느 방향으로, 얼마나 안정적으로 잡았는지는 원리적으로 담기지 않습니다. 즉 EgoAffordance 는 접촉의 **위치 정보**만 있는 corpus 이며, 접촉의 **동역학**은 비어 있습니다.
- **파이프라인 오차의 누적과 미측정** — 데이터 생성이 VLM keyframe 선택 → 검출 → 분할 → keypoint → MANO → inpainting → 단안 깊이 → intrinsics 추정 → 카메라 포즈 → 3D tracking 의 9단 파이프라인인데, **정답 라벨의 정확도 검증이 논문에 전혀 없습니다.** 어떤 단계가 얼마나 틀리는지, 최종 3D 궤적의 오차가 몇 cm 인지 알 수 없어 데이터 품질이 블랙박스입니다. 200K episode 라는 규모 주장이 품질 주장과 분리되어 있습니다.
- **소스 코퍼스 미명세 → 라이선스·재현 불가** — 어떤 ego 데이터셋을 얼마나 소비했는지 본문에 없습니다. Ego4D · Ego-Exo4D 계열은 게이트가 걸린 코퍼스이므로, 소스 명세가 없으면 EgoAffordance 를 배포할 수 있는지 자체가 불확실합니다.
- **재현에 필요한 하이퍼파라미터 공백** — $`\lambda_{v},\lambda_{g},\lambda_{t}`$, 궤적 bin 수 $`N`$, waypoint 수 $`T`$, 후보 수 $`K`$, top-p, 옵티마이저·학습률·하드웨어가 모두 비어 있습니다. 세 손실의 스케일이 이질적이라 $`\lambda`$ 값은 재현 성패를 가르는 변수인데 공개되지 않았습니다.
- **통계적 검정력** — zero-shot 은 과제당 10회, 실환경은 5개 과제뿐입니다. 실환경 평균 68.0 % 대 52.0 % 는 총 50회 대 50회 시행에서 나온 차이이고, 시드·재시도 분산이 없습니다. T15(40 vs 0)처럼 한 셀이 평균에 8 %p 를 기여하는 구조라 과제 구성에 민감합니다.
- **grasp modality 의 가치가 gripper 평가에 갇힘** — §V-B3 이 grasp pose 의 기여를 낮게 보고했지만, 실행 로봇이 Fetch·PR2 의 2지 그리퍼이므로 이는 grasp affordance 의 한계라기보다 **평가 embodiment 의 한계**입니다. 논문은 다지 손 실행을 전혀 다루지 않아, 96-D MANO 출력이라는 설계의 값어치가 논문 안에서는 측정될 수 없는 구조입니다.
- **object-centric 표현의 단일 접촉점 가정** — anchor 가 히트맵의 peak **하나**이므로, 양손 조작이나 한 손 안에서도 여러 접촉 부위가 역할을 나누는 상황(도구 파지 후 손가락 조작)은 표현 자체가 담지 못합니다. 데이터 파이프라인이 상호작용 손 정보를 뽑기는 하지만, 최종 표현은 단일 anchor + 단일 grasp 로 축약됩니다.

---

## ♻️ 재현성

- **코드** — 본문·각주·초록 어디에도 저장소 링크나 프로젝트 페이지가 없습니다. IROS 채택 각주만 있고 공개 계획 언급도 없습니다.
- **데이터** — EgoAffordance 배포 URL·라이선스·소스 코퍼스 구성이 모두 미제시입니다. 추출 파이프라인의 각 단계는 인용 번호로 지시되지만, 어떤 구현·체크포인트·임계값을 썼는지는 서술되지 않습니다.
- **모델 하이퍼파라미터** — 백본(Qwen2.5-VL)과 보조 인코더(DINOv2) 이름만 확정적이고, 파라미터 규모·학습 설정·손실 가중치·토큰 어휘 설계는 비어 있습니다.
- **평가 프로토콜** — 상대적으로 구체적입니다. 테스트셋 규모(데이터셋당 500 scene), 지표 정의(IoU 임계 0.5, NSS/SIM/KLD), 시뮬 플랫폼(IsaacGym + Ag2Manip 환경, PartManip/FrankaKitchen/ManiSkill 출처), 시행 횟수(과제당 10회), 실기 플랫폼(Fetch · PR2)이 명시되어 재현 시 비교 조건은 맞출 수 있습니다.
- **baseline 처리** — baseline 이 grasp 를 내지 않아 GraspNet 으로 gripper pose 를 생성하고, VRB 는 2D 궤적을 RAM 전략으로 3D 로 올리며, LISA 는 마스크를 $`[0,1]`$ 정규화합니다. 이 보정들이 명시되어 있어 비교 조건은 추적 가능합니다.
- **보조 자료** — affordance guidance 보상 설계는 supplementary material 로 미뤄져 있고, arXiv HTML 본문에는 포함되어 있지 않습니다.
- **총평** — 논문은 **읽고 아이디어를 가져올 수는 있지만 재구현할 수는 없는** 상태입니다. 데이터셋이 핵심 기여인데 배포 경로가 없다는 점이 가장 큰 공백입니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P0(VLA Datasets & Benchmarks) — 주 pillar.** 본 논문의 1차 기여물이 데이터셋(EgoAffordance)이고 축이 egocentric 이므로 P0 정중앙입니다.
  - `D24`(priority data axis — egocentric 인간 영상 중심) — 강한 지지 사례입니다. "ego 영상만으로 로봇 실행까지 이어지는가"를 zero-shot 실기로 검증했고, 실환경에서 sim 우위 방법을 역전시켰습니다. 다만 EgoDex 같은 우리 핀과 성격이 다릅니다 — EgoDex 는 Vision Pro 로 **측정된** 3D 손 추적을 제공하는 반면, EgoAffordance 는 in-the-wild 영상에서 **추정된** 3D 손 궤적입니다. D24 의 "egocentric" 안에 측정 기반과 추정 기반이라는 하위 축이 있다는 것이 이 논문이 드러낸 지점입니다.
  - `D25`(tactile / force / torque 데이터 스카우팅) — **정면 반례이자 D25 가 지목한 공백의 실증**입니다. 5.6M 프레임 규모에서도 접촉이 "손끝 keypoint ∩ 물체 마스크"라는 2D 기하로만 정의됩니다. 즉 ego 영상 파이프라인은 규모를 아무리 키워도 접촉 세기·안정성을 만들어내지 못하며, D25 가 촉각/힘 코퍼스를 별도 1급 축으로 둔 판단을 강화합니다.
  - `D26`(benchmark / eval scouting scope) — 부분 관련. Ag2Manip 환경(PartManip · FrankaKitchen · ManiSkill 조합) 위의 10개 가사 과제 + 실기 5과제라는 zero-shot 평가 셋이 제시되지만, 우리가 우선하는 in-hand rotation / articulated-tool 축과는 겹치지 않습니다.
  - `D27`(license / usability bar) — 경보 사례입니다. 배포 URL·라이선스·소스 코퍼스가 모두 미제시이므로 현재 기준으로는 **사용 가능성 미확인** 상태로 기록되어야 합니다.
- **P4(Pretraining for Data-Efficient Adaptation) — 부 pillar.**
  - `D22`(pretraining data composition — egocentric vs mixed, **OPEN**) — 가장 직접적 관련입니다. 순수 ego 영상 기반 corpus 하나로 실환경 일반화를 얻었다는 증거이므로 "egocentric-centric" 쪽 근거가 됩니다. 단, 이 논문이 학습한 것은 액션 정책이 아니라 affordance 예측기입니다 — 관측→행동 매핑이 아니라 관측→중간 표현 매핑이므로, D22 가 다루는 VLA 사전학습 corpus 논쟁에 그대로 대입하기는 어렵습니다.
  - `D19`(VLM backbone lineage & adaptation range) — 참조점. lineage 는 Qwen2.5-VL 이며, 우리 tracked 후보인 Qwen-VLA · Xiaomi-Robotics-0 와 같은 Qwen 계열입니다. adaptation range 는 우리 v1 의 `(a) full VLM freeze` 와 달리 **VLM fine-tuning** 입니다(`<GRASP>` 토큰 학습을 위해 VLM 을 fine-tune 한다고 §IV 가 명시). prior 보존 측정은 전혀 없습니다.
  - `D23`(action representation × pretraining/preservation) — 대조 사례. 우리 v1 은 `(iii) 연속 flow-matching head` 인데, 본 논문은 6D 포즈를 spatial binning 으로 이산화해 자기회귀 토큰으로 예측합니다. 두 표현의 우열을 다룬 실험은 논문에 없지만, "궤적 오차가 기하 거리가 아니라 bin 분류 오차로 측정된다"는 구조적 부작용이 D23 논의에 쓸 만한 반례 재료입니다.
  - `D20`(prior-preservation strategy) / `D21`(staged pretraining + adaptation recipe) — 직접 건드리지 않습니다. 단계별 recipe 도, 사전학습 prior 보존 측정도 없습니다.
- **P2(Structured Multimodal Observation Fusion) — 약한 관련.**
  - `D9`(action/dynamics-aware vision encoder) — 흥미로운 대조입니다. 우리 v1 은 generic stem 대신 action/dynamics-aware(DynaFLIP) 또는 geometry-distilled(eVGGT) 인코더를 선호합니다. 본 논문은 그 어느 쪽도 아닌 **DINOv2(자기지도 generic 인코더)** 를 VLM 인코더에 병렬로 덧붙여 세밀 grounding 을 얻었다고 주장합니다. 다만 ablation 이 없어 반례로 삼기에는 증거가 약합니다.
  - `D8`(multi-camera spatial-geometric grounding) — 반대 방향 사례. 입력이 단일 RGB 이며, 저자 스스로 시뮬 열세의 원인을 "VidBot 은 깊이를 직접 받는데 우리는 아니다"로 설명합니다. 즉 공간 정보 부족이 성능 손실로 관측된 사례이고, D8 의 문제의식과 같은 방향의 증거입니다.
  - `D10`(heterogeneous modality fusion beyond concat) / `D11`(proprio-tactile-force token construction) / `D12`(topology-aware encoding) — 건드리지 않습니다. 촉각·힘·고유수용 입력이 아예 없는 vision-language-only 모델입니다.
- **P1(Heterogeneous Body/Hand Action Expert) — 약한 관련.**
  - `D3`(Hand output space) — 우리 v1 은 `(i) finger joint command` 입니다. 본 논문의 grasp affordance 는 96-D MANO(전역 손목 회전 + 15 국소 관절 회전, 6D 표현)로 **손 자세를 관절 공간에 가까운 파라미터로 내놓는** 사례이므로, "손 출력은 관절 명령"이라는 방향과 정합적입니다. 다만 이는 액션이 아니라 목표 자세 예측입니다.
  - `D2`(Body output space) — 간접 지지. 논문의 궤적은 손목 6D 포즈 시퀀스이며, 우리 v1 의 `(a) both-wrist / tool-flange pose` 와 같은 표현 층위입니다. Body 궤적을 wrist pose 로 두면 인간 영상 유래 궤적을 직접 소비할 수 있다는 실무적 근거가 하나 늘었습니다.
  - `D1` · `D4` · `D5` · `D6` · `D7` — 건드리지 않습니다. action expert 아키텍처, Body↔Hand 정보 공유, 제어율, π 백본 통합 어느 것도 다루지 않는 논문입니다.
- **P3(Hand-level System0 Module) — 관련 없음.** RL 이 등장하지만(affordance-guided 실환경 RL) 이는 과제 수준 정책 학습이며, P3 가 정의한 System0(비전 배제, 촉각+관절 상태 기반 접촉 안정화)과 층위가 다릅니다. P3 anti-topic 의 "generalized full-task RL reward-engineering" 에 해당합니다.
- **P5(World Model) — 관련 없음.** SfM 과 깊이 추정은 정적 3D 재구성이며, action-conditioned 예측 모델이 아닙니다.
- **Identity 긴장 / 지지** — 지지 쪽은 명확합니다. "human video 기반 corpus 가 dexterity 의 상류 레버"라는 우리 전제에 실기 증거를 하나 더합니다. 긴장 쪽이 더 중요합니다 — 논문 스스로 "grasp pose 는 인간 손과 로봇 그리퍼의 형태 차이 때문에 기여가 작았다"고 적었는데, 이것은 **다지 손을 쓰지 않으면 인간 손 데이터의 가장 값진 절반이 버려진다**는 뜻입니다. 우리 Identity 가 다지 손을 전제한다는 점에서, 이 논문의 약점이 오히려 우리 방향의 논거가 됩니다.
- **경쟁자 함의** — P0 §5 핀 중 EgoDex 와 직접 경쟁 관계가 아니라 보완 관계입니다(측정 기반 vs 추정 기반). Ego-Exo4D · Ego4D · HOI4D 는 본 논문의 비교 대상이자 잠재적 소스이므로, EgoAffordance 가 공개되면 "같은 원본 위에 affordance 라벨 층이 하나 더 얹힌" 파생 자산이 됩니다.

---

## ✨ 핀 논문 대비 델타

- **vs EgoDex ([arXiv:2505.11709](https://arxiv.org/abs/2505.11709), P0 핀 · Top)** — EgoDex 는 Vision Pro 로 **측정된** 3D 손/손가락 추적을 829시간 규모로 제공합니다. 본 논문의 델타는 측정 장비 없이 **in-the-wild 영상에서 추정만으로** 같은 종류의 3D 정보를 만들고, 여기에 EgoDex 에 없는 **visual affordance mask** 를 얹었다는 점입니다. 반대 방향의 델타도 분명합니다 — EgoDex 는 손가락 관절 정확도가 보장되지만 EgoAffordance 는 검증되지 않았습니다. 두 자산은 "정확도 대 다양성" 축에서 정반대에 놓입니다.
- **vs Ego-Exo4D ([arXiv:2311.18259](https://arxiv.org/abs/2311.18259), P0 핀)** — Ego-Exo4D 는 원본 영상 + hand pose + camera trajectory 를 주지만 contact 주석이 없습니다(Table I). 본 논문의 델타는 그 위에 **접촉 영역 라벨 층**을 자동 생성해 얹은 것이며, 즉 Ego-Exo4D 계열을 대체하는 것이 아니라 그 위에 쌓이는 파생 라벨입니다.
- **vs HOI4D ([arXiv:2203.01577](https://arxiv.org/abs/2203.01577), P0 methodology base)** — HOI4D 는 4D hand-object 상호작용을 정밀 주석하지만 16개 물체 범주로 좁습니다. EgoAffordance 는 16.4K 범주로 세 자릿수 넓지만 주석이 자동 생성이라 정밀도가 미검증입니다. 재차 같은 트레이드오프 축입니다.
- **vs UniHand-2.0 / Being-H0.5 ([arXiv:2601.12993](https://arxiv.org/abs/2601.12993), P0 · P4 핀)** — UniHand-2.0 은 인간 손 데이터를 30개 embodiment 로 **retarget** 해 로봇 손 액션 라벨을 만듭니다. 본 논문은 retarget 을 데이터 구축 단계에 두지 않고 **실행 시점으로 미룹니다** — 물체 중심 affordance 를 저장하고, 실행할 때 해당 로봇에 맞춰 gripper pose 를 추정합니다. embodiment 결합 시점이 다르다는 것이 델타의 본질이며, 우리 D22 논의에서 "corpus 를 어느 표현 층위로 저장할 것인가"라는 별개 축을 만듭니다.
- **vs VidBot (논문 내 최강 baseline · 미핀)** — 본 논문이 스스로 밝히듯 VidBot 은 깊이 입력을 직접 쓰고 시뮬에서 85.0 % 로 앞섭니다. 델타는 두 가지입니다 — (1) 세 affordance 를 **통합 예측**한다는 점(VidBot 은 3D 액션 예측 중심), (2) 실환경 대규모 ego 학습으로 어수선한 장면에서 16 %p 를 회수한다는 점.
- **vs RH20T ([arXiv:2307.00595](https://arxiv.org/abs/2307.00595), P0 핀 · D25 앵커)** — 델타가 아니라 **공백의 대비**입니다. RH20T 가 희소하게 제공하는 6축 손목 F/T 가 본 논문에는 전혀 없습니다. 5.6M 프레임과 RH20T 의 힘 라벨이 서로 다른 종류의 부족을 메우고 있음을 보여 주는 대조군입니다.

---

## ⚙️ 의사결정 함의

- **P0 pin 표에 "추정 기반 ego affordance" 행을 신설** — 현재 P0 §5 는 데이터셋을 축(👤 ego / 🤖 robot / 🔀 mixed)으로만 분류합니다. 본 논문은 같은 ego 축 안에서 **측정(EgoDex) vs 추정(EgoAffordance)** 이라는 품질 축이 별도로 필요함을 보여 줍니다. 실무적으로는 pin 표에 `주석 출처` 열(측정 / 자동추정 / 사람라벨)을 추가하고, 자동추정 항목에는 라벨 정확도 검증 유무를 함께 기록하는 것이 맞습니다.
- **`D22` 사전학습 corpus 에 affordance 라벨 층을 별도 변수로 분리** — 지금 D22 는 "egocentric vs mixed" 를 데이터 **출처** 축으로만 봅니다. 본 논문은 같은 ego 영상이라도 그 위에 어떤 중간 라벨(heatmap / grasp / trajectory)을 얹느냐가 하류 성능을 가른다는 사례이므로, corpus 명세에 `annotation_layers: [contact_heatmap, hand_pose, wrist_traj]` 같은 필드를 추가해 출처와 라벨을 독립적으로 관리해야 합니다.
- **사전학습 보조 헤드 후보로 contact-heatmap 예측을 등록** — §V-B3 의 "히트맵 제거 시 완전 실패" 는 접촉 위치 예측이 조작 학습의 가장 강한 사전지식이라는 뜻입니다. 우리 스택에서는 P4 Stage 1 (사전학습) 단계에 `aux_head: contact_heatmap` 을 붙이고 손실을 `L_total += lambda_contact * L_dice(contact_heatmap)` 형태로 더하는 안이 직접적 후보가 됩니다. Soft Dice 의 파라미터는 논문 값 `dice_smooth: 1.0`, `dice_power: 1.5` 를 출발점으로 씁니다.
- **`D9` 인코더 결정에 "VLM 인코더 + 보조 dense 인코더 병렬" 옵션 추가** — 현재 D9 v1 은 단일 인코더 선택(action/dynamics-aware 또는 geometry-distilled) 프레임입니다. 본 논문은 VLM 자체 인코더를 두고 그 **옆에** dense 인코더를 하나 더 붙이는 구성을 씁니다. config 로는 `vision_encoders: [vlm_native, dinov2]` + `fusion: decoder_side` 이며, 우리 D9 선택지에 "교체" 외에 "병렬 부착" 이 있다는 것을 명시적으로 기록해야 합니다. 비용은 인코더 하나만큼의 추가 순전파입니다.
- **`D23` 궤적 표현 비교 실험 항목 추가** — 본 논문의 discrete bin + AR CE 와 우리 v1 의 continuous flow-matching 을 같은 데이터로 비교하는 항목을 백로그에 넣습니다. 측정 지표는 성공률이 아니라 **궤적 기하 오차**(waypoint 별 위치 RMSE, 회전 측지 오차)여야 합니다 — bin CE 는 기하 오차와 단조 관계가 아니므로 이 지표에서 두 표현의 차이가 드러납니다.
- **다지 손 grasp affordance 의 가치 측정을 우리 쪽 고유 실험으로 확정** — §V-B3 이 남긴 공백(2지 그리퍼라 MANO grasp 가 덜 중요했다)은 우리 Sharpa Hand / xhand 스택에서 정확히 반대 결과가 나올 수 있는 지점입니다. 평가 항목: 동일 과제에서 (a) heatmap only, (b) heatmap + MANO grasp → 22-DOF retarget 의 성공률 차이. 이 하나의 실험이 "다지 손이 필요하다"는 Identity 주장에 외부 논문이 만들어 준 검증 슬롯입니다.
- **`D25` 우선순위 유지 근거 갱신** — 본 논문은 vision-only ego 파이프라인이 200K episode 규모에서도 접촉 세기를 만들어내지 못한다는 실증입니다. 촉각/F/T 코퍼스 스카우팅의 우선순위를 낮출 이유가 없다는 근거로 기록합니다.
- **`D27` 사용 가능성 판정에 "배포 경로 미제시" 상태를 추가** — 현재 D27 은 라이선스 등급(permissive / gated / NC) 축입니다. 본 논문처럼 **라이선스 이전에 배포 URL 자체가 없는** 사례를 담을 상태값(`배포 미공개`)이 필요합니다. 그렇지 않으면 "gated" 와 "존재하지 않음" 이 같은 칸에 들어갑니다.

---

## ⚠️ 먼저 검증할 실패 모드

가장 싼 확인부터 나열합니다.

1. **데이터셋 자체를 못 받을 가능성 (0원, 즉시).** EgoAffordance 의 배포 URL·라이선스·소스 코퍼스가 전부 미제시입니다. 저자 메일(`{oh, kawaharazuka, k-okada}@jsk.imi.i.u-tokyo.ac.jp`)로 배포 계획을 문의하는 것이 이 논문 전체를 활용 가능 자산으로 만들지 결정합니다. 답이 "미공개"라면 아래 항목 대부분이 무의미해지고, 이 논문은 **파이프라인 설계 참고**로만 남습니다.
2. **접촉 라벨이 우리에게 필요한 종류가 아닙니다 (0원, 논문 재독으로 확정).** 우리 P2 `D11` 은 손가락별 촉각 토큰과 접촉 세기를 요구하는데, 이 데이터의 접촉은 "손끝 keypoint ∩ 물체 마스크"라는 2D 판정입니다. **결론은 이미 나와 있습니다** — EgoAffordance 는 D11 의 학습 신호로 쓸 수 없고, 접촉 **위치** 사전학습에만 쓸 수 있습니다. 이 경계를 먼저 문서화하지 않으면 후속 스카우팅이 잘못된 기대를 안고 갑니다.
3. **자동 라벨의 정확도가 미검증입니다 (중간 비용).** 논문에 3D 손 궤적 오차 수치가 전혀 없습니다. 우리가 이 corpus 를 사전학습에 쓰려면, 정답이 있는 소규모 집합(EgoDex 처럼 측정 기반 ego 데이터)에 같은 파이프라인을 돌려 추정 궤적과 측정 궤적의 오차를 재는 교차 검증이 선행되어야 합니다. cm 단위 오차가 크면 wrist pose 사전학습 신호로서 가치가 급감합니다.
4. **retargeting 손실이 우리 손에서는 다르게 나타납니다.** 논문의 §V-B3 결과("grasp 기여 작음")는 2지 그리퍼 retarget 을 통과한 뒤의 값입니다. 우리는 22-DOF Sharpa Hand 이므로 MANO 15 관절 → 22-DOF 매핑이 필요하고, 여기서 새 오차원이 생깁니다. **가장 싼 검증**: 학습 없이, EgoAffordance 형태의 MANO 파라미터 몇 백 개를 우리 손 URDF 로 retarget 해 관절 한계 위반률과 자세 재현 오차를 재는 것입니다. 이 수치가 나쁘면 grasp affordance 를 그대로 소비할 수 없습니다.
5. **anchor 단일점 가정이 우리 과제와 충돌합니다.** 본 논문 표현은 히트맵 peak 하나를 원점으로 삼습니다. 우리 Phase 2 flagship 인 도구 조작(도구를 쥔 채 손가락으로 트리거 조작)은 **접촉점이 최소 둘**이고 역할이 다릅니다. 이 표현을 그대로 가져오면 Phase 1(in-hand cube rotation)에도 맞지 않습니다 — 회전 중 접촉점이 계속 바뀌기 때문입니다. 즉 이 affordance 표현의 적용 범위는 우리 과제 스펙트럼에서 **접근·초기 파지 구간까지**이며, 그 경계를 먼저 못 박아야 합니다.
6. **VLM fine-tuning 이 우리 `D19` freeze 방침과 충돌합니다.** 논문은 `<GRASP>` 토큰 학습을 위해 VLM 을 fine-tune 합니다. 우리 v1 은 `(a) full VLM freeze + action experts only` 입니다. 특수 토큰을 어휘에 추가하려면 최소한 임베딩 행렬은 학습해야 하므로, "freeze" 의 정의에 **어휘 확장 예외를 둘 것인가**를 먼저 결정해야 합니다. 저비용 검증: 임베딩 행만 학습하고 나머지를 동결한 상태에서 `<SEG>` 급 토큰이 학습되는지 소규모로 확인.
7. **discrete bin 궤적이 우리 제어 해상도를 못 따라갈 위험.** 궤적이 spatial binning 으로 이산화되므로 해상도가 bin 수에 갇힙니다. 논문은 bin 수 $`N`$ 을 밝히지 않았습니다. 우리 Body 출력이 wrist SE(3) 포즈라면 필요한 위치 해상도는 mm 급인데, 전역 공간을 균등 binning 하면 그 해상도가 나오지 않습니다. **사전 계산으로 판정 가능**: 우리 작업 공간 크기 ÷ 목표 해상도로 필요한 bin 수를 계산해 어휘 크기가 현실적인지 확인합니다.
8. **in-context guidance 가 외부 상용 VLM 의존입니다.** §IV-C 는 GPT 급 모델을 상위 플래너로 호출합니다. 우리 실기 루프에 외부 API 를 넣는 것은 지연·가용성·재현성 모두에서 문제입니다. 논문의 실패 원인 1위가 이 방향 샘플링이라는 점까지 감안하면, 이 구성요소는 **가져오지 않고** 우리 백본의 언어 능력으로 대체하거나 방향 사전지식을 다른 경로로 넣는 설계가 필요합니다.
9. **평가 embodiment 격차 — 논문 수치가 우리 예측치가 아닙니다.** Fetch·PR2 는 이동 베이스 + 단순 그리퍼이고, 과제는 서랍·냉장고·주전자 같은 대형 관절체입니다. 우리 과제(in-hand rotation, 도구 조작)와 겹치는 셀이 하나도 없습니다. 이 논문의 68.0 % 는 우리 스택 성능의 어떤 예측값도 아니며, 인용 시 그 경계를 명시해야 합니다.
10. **사전학습 보조 헤드 도입의 비용 대비 효과 (가장 비쌈, 마지막).** ⚙️ 에서 제안한 `contact_heatmap` 보조 헤드는 실제로 붙여 봐야 값이 나옵니다. 그 전에 3번(라벨 정확도)과 5번(표현 적용 범위)이 통과해야 하며, 통과하더라도 우리 데이터가 아니라 EgoAffordance 로 사전학습한 히트맵 헤드가 우리 실기 장면(로봇 시점 · 다지 손)에서 전이되는지는 별도 문제입니다. 순서상 마지막입니다.

---

## 💡 컨텍스트 제안

- **`D25`(P0) 근거 보강 기록 제안** — Decision 자체는 그대로 두되, "vision-only ego 파이프라인은 200K episode 규모에서도 접촉 세기를 산출하지 못한다(본 논문 §III-B 의 keypoint ∩ mask 접촉 정의)" 를 D25 의 근거 사례로 남겨 두시길 제안드립니다. 규모로 촉각 공백을 메울 수 있다는 반론이 나올 때 직접 인용 가능한 반증입니다.
- **P0 §5 Methodology base 추가 제안** — 본 논문([arXiv:2608.05215](https://arxiv.org/abs/2608.05215))을 **핀이 아니라** methodology base 행으로 추가하는 안을 제안드립니다. 배포 URL·라이선스가 없어 `D27` 기준으로 아직 자산이 아니므로 핀 8칸을 쓸 단계는 아니지만, "ego 영상 → 자동 actionable affordance" 파이프라인의 참조 구현으로는 가치가 있습니다. 배포가 확인되면 핀 승격을 재검토하는 조건부 제안입니다.
- **`D27`(P0) 에 `배포 미공개` 상태값 추가 제안** — 현재 라이선스 등급 축(permissive / gated / NC)만으로는 본 논문처럼 **라이선스 이전에 배포 경로가 없는** 사례를 표현할 수 없습니다. v1 bullet 에 상태값 하나를 추가하는 소폭 개정을 제안드립니다.
- **`D24`(P0) 에 하위 축 명시 제안** — "egocentric 인간 영상 중심" 안에 **측정 기반 3D 손 추적(EgoDex 계열) vs 영상 추정 기반(본 논문 계열)** 이라는 품질 하위 축이 있음을 v1 서술에 한 구절 추가하는 것을 제안드립니다. 두 계열의 트레이드오프(정밀도 대 다양성)가 정반대라 같은 칸에 두면 스카우팅 판정이 흔들립니다.
- **`D22`(P4, OPEN) 에 라벨 층 변수 추가 제안** — 현재 open 항목은 "everything-mixed dump vs egocentric-only" 라는 출처 축입니다. 여기에 **"corpus 를 어느 표현 층위로 저장할 것인가"**(원시 영상 / retarget 된 로봇 액션 / 물체 중심 affordance)라는 두 번째 열린 변수를 추가하시길 제안드립니다. 본 논문과 UniHand-2.0 은 embodiment 결합 시점이 정반대인 두 극단이며, 이 축은 D22 의 현재 서술에 잡혀 있지 않습니다.
- **`D9`(P2) 선택지 확장 제안** — v1 은 인코더 **교체** 프레임입니다. 본 논문의 "VLM 자체 인코더 + DINOv2 병렬 부착" 을 세 번째 선택지로 명시하는 것을 제안드립니다. 다만 논문에 DINOv2 ablation 이 없어 증거 강도는 약하므로, deferred candidate 로 기록하는 정도가 적절합니다.
- **`D19`(P4) freeze 정의 명확화 제안** — v1 의 `(a) full VLM freeze` 가 **어휘/임베딩 확장까지 금지하는지**가 현재 문구로는 판정되지 않습니다. 본 논문처럼 특수 토큰을 추가하는 설계를 검토하려면 이 경계가 필요하므로, v1 bullet 에 한 구절을 덧붙이는 문구 조정을 제안드립니다. Decision 선택 자체는 바꾸지 않습니다.
