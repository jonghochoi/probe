# Paper Analysis — See like a Robot: Robot-Centric Pointmaps for Vision-Language-Action Models

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | See like a Robot: Robot-Centric Pointmaps for Vision-Language-Action Models |
| 저자 | Byungkun Lee, Dongyoon Hwang, Dongjin Kim, Hojoon Lee, Minho Park, Jaegul Choo |
| 링크 | [arXiv:2607.11498](https://arxiv.org/abs/2607.11498) · [Website](https://davian-robotics.github.io/pointmap/) |
| 발행일 / 버전 | 2026-07-13 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-07-18 |
| 관련 Pillar | P2, P4 |
| 태그 | vla-arch, sim2real |

---

## 🧭 한 줄 요약 (TL;DR)

VLA 는 관측을 카메라 좌표계에서 받지만 액션은 로봇 좌표계에서 정의되어 "관측–액션 프레임 불일치"가 생기며, 데이터가 다양한 카메라 시점을 aggregate 할수록 이 불일치의 일반화가 어려워집니다. 본 논문은 각 픽셀에 로봇 좌표계 3D 좌표를 담은 **robot-centric pointmap** 을 관측으로 제공해, 사전학습 2D VLA 의 $`H\times W`$ 그리드를 유지한 채 최소 구조 변경으로 로봇 좌표계 기하를 주입합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — VLA 의 액션은 로봇 base 좌표계(task-space end-effector command)에서 정의되는데, 대부분의 VLA 는 장면을 카메라 좌표계(RGB / depth)로 관측합니다. 관측 프레임과 액션 프레임이 어긋나는 **frame mismatch** 가 존재합니다.
- **기존 접근의 한계** — 고정 시점에서는 정책이 단일 관측→액션 사상만 외우면 되므로 이 불일치가 무해합니다. 그러나 대규모 데이터셋이 서로 다른 카메라 셋업의 시연을 aggregate 하면, 정책은 여러 시점의 관측을 로봇 좌표계 액션으로 사상하는 법을 *일반화* 해야 하고 여기서 성능이 무너집니다.
- **본 논문의 가설** — 관측을 애초에 로봇 좌표계 3D 기하로 표현해 정책에 넘겨주면, 정책이 시점별 사상을 스스로 학습할 부담이 사라져 시점 변화에 강건해집니다.
- **왜 지금 중요한가** — 대규모 로봇 데이터가 기관·시점을 넘나들며 합쳐지는 흐름(OXE 류) 속에서, depth 나 point cloud 는 3D 를 주지만 사전학습 2D VLA 가 기대하는 $`H\times W`$ 이미지 그리드를 깨뜨려 매끄러운 통합이 어렵습니다. 그리드를 보존하면서 로봇 좌표계 기하를 주는 표현이 비어 있었습니다.

---

## 🧩 핵심 기여

- **Robot-centric pointmap 입력** — 각 픽셀이 로봇 base 좌표계의 3D 좌표를 담는 이미지 형태의 pointmap 을 VLA 입력으로 도입. RGB 의 $`H\times W`$ 레이아웃을 그대로 유지해 사전학습 2D VLA 에 최소 구조 변경으로 통합됩니다.
- **Point cloud 전용 인코더 불필요한 융합** — pointmap 을 RGB 인코더와 동일 아키텍처의 별도 tower(RGB 인코더로 초기화)로 인코딩하고, 그 토큰을 대응하는 RGB 토큰에 **element-wise 덧셈** 으로 융합. voxel 모듈·전용 3D 인코더·추가 토큰 시퀀스가 전혀 없습니다.
- **End-effector centering** — pointmap 을 현재 end-effector 위치 기준으로 재중심화해, 관측과 액션 공간이 공통 원점을 공유하도록 만들어 시점 강건성을 높입니다.
- **설계 선택의 통제된 분석(RQ1–RQ4)** — camera 정보 조건화 vs. 사전 변환, 이미지형 pointmap vs. point cloud, base 원점 vs. EE 원점, 학습 시점 변화량 증가에 대한 강건성을 각각 통제 실험으로 격리.
- **사전학습 VLA 두 종에서 검증** — RoboCasa 에서 $`\pi_{0.5}`$ +7.6, SmolVLA +4.2 점 개선; 실로봇에서 미학습 카메라 배치일 때 RGB 대비 이득이 +5.0 → +11.7 로 확대.

---

## 🔑 기술 키워드

- **Robot-centric pointmap** — 각 픽셀이 그 픽셀에 보이는 장면 점의 로봇 좌표계 3D 좌표(XYZ)를 담는 이미지. "RGB 대신 색 자리에 로봇 기준 위치를 채운 사진"으로, 이 논문의 핵심 관측 표현.
- **Frame mismatch** — 관측이 정의된 좌표계(camera)와 액션이 정의된 좌표계(robot base)가 다른 상태. 본 논문이 없애려는 근본 문제.
- **Pointmap** — 이미지 그리드를 유지한 채 픽셀당 하나의 3D 좌표를 담는 현대 3D 비전의 표준 표현. point cloud 와 달리 $`H\times W`$ 픽셀 대응을 보존.
- **End-effector centering** — pointmap 좌표를 현재 그리퍼 위치 기준 상대좌표로 바꾸는 것. 서로 다른 위치의 동일 동작을 원점 근처로 모아 시점·위치 의존성을 줄임.
- **Plücker rays** — 각 픽셀을 지나는 3D 광선을 카메라 intrinsics·extrinsics 로부터 인코딩한 6차원 표현. "카메라가 어디서 어떻게 보는지"만 알려주는, pointmap 없이 정보를 조건화하는 baseline.
- **Element-wise token fusion** — pointmap 토큰을 RGB 토큰에 concat 이 아니라 같은 그리드 위치끼리 더하는 방식. 공간 대응을 보존하고 토큰 수를 늘리지 않음.
- **Viewpoint generalization** — 학습에서 본 적 없는 카메라 배치로 배포될 때 성능을 유지하는 능력. 본 논문 실로봇 seen/unseen 프로토콜의 평가 축.
- **Pretrained 2D VLA** — RGB 이미지·언어로 사전학습된 정책 백본($`\pi_{0.5}`$, SmolVLA). pointmap 이 이 백본의 시각 경로와 사전학습 가중치를 그대로 재사용한다는 점이 설계의 핵심.

---

## 🔬 방법론

### 직관

핵심 문제는 "정책이 보는 세계"와 "정책이 행동하는 세계"의 좌표계가 다르다는 것입니다. 정책은 카메라가 찍은 그림을 보지만, 내놓는 명령은 로봇 몸통을 기준으로 한 3D 이동입니다. 카메라가 한 자리에 고정되어 있으면 정책은 "이 그림에는 저 명령"이라는 대응 하나만 외우면 되지만, 학습 데이터가 여러 기관·여러 카메라 각도에서 모이면 각도마다 대응이 달라져 정책이 이 대응 관계 자체를 일반화해야 합니다.

본 논문의 해법은 문제를 정책 안이 아니라 입력 단계에서 미리 푸는 것입니다. depth 와 카메라 보정값이 있으면 각 픽셀이 실제로 로봇 기준 어디에 있는지를 사전에 계산할 수 있습니다. 이렇게 계산한 로봇 좌표계 3D 좌표를 원래 이미지와 똑같은 격자 모양으로 담으면, 카메라가 어디로 움직이든 같은 물리적 점은 항상 같은 좌표값을 갖게 됩니다. 즉 시점이 바뀌어도 관측의 "숫자"가 안정적입니다.

이 표현이 강력한 이유는 형태를 바꾸지 않기 때문입니다. point cloud 처럼 격자를 버리면 사전학습된 2D 인코더를 못 쓰고 전용 3D 모듈이 필요하지만, pointmap 은 RGB 와 같은 $`H\times W`$ 그림이라 RGB 인코더를 복제해 그대로 쓰고, 나온 토큰을 RGB 토큰에 자리별로 더하기만 하면 됩니다. 여기에 좌표 원점을 현재 그리퍼로 옮기는 한 번의 뺄셈을 더하면, "그리퍼가 목표까지 얼마나 가야 하는가"라는 액션에 직접 대응하는 관측이 되어 시점·위치 변화에 더 강건해집니다.

### 아키텍처

![Figure 1 — Robot-centric pointmap 개념](https://arxiv.org/html/2607.11498/x1.png)

> "Figure 1: Robot-centric pointmaps provide 3D geometry aligned with robot-frame actions. Large-scale training data is collected from diverse camera viewpoints around the robot. Robot-centric pointmaps preserve the dense $`H\times W`$ grid expected by pretrained 2D VLAs while providing robot-centric 3D geometry." (§1)
(한글 해설 — 다양한 시점으로 수집된 데이터에서도 pointmap 은 그리드를 유지하면서 로봇 좌표계 기하를 제공한다는, 논문 전체의 그림 한 장 요약.)

입력은 RGB-D 관측이며, 출력은 액션 chunk(end-effector delta)입니다. RGB 는 기존 시각 tower 로, pointmap 은 그와 동일 구조의 별도 tower 로 인코딩된 뒤 토큰 단계에서 융합됩니다.

> "We first lift each RGB-D observation into 3D within its camera frame, then transform it into the shared robot frame in which actions are defined, while preserving the RGB image's $`H\times W`$ layout." (§1)
(한글 해설 — pointmap 구성의 3단계: 카메라 프레임 lift → 로봇 프레임 변환 → 그리드 보존.)

![Figure 3 — RGB-D → camera-frame → robot-frame pointmap 구성](https://arxiv.org/html/2607.11498/x3.png)

> "Figure 3: RGB-D observations are lifted into camera-frame pointmaps and transformed into robot-frame pointmaps." (§3)
(한글 해설 — Eq. (1)–(2) 의 lift·변환 파이프라인을 시각화한 그림.)

### 학습 목표 / 손실

pointmap 자체는 별도 손실을 도입하지 않습니다. 손실은 백본 VLA 의 원래 액션 예측 목표를 그대로 사용하고, pointmap 은 오직 시각 입력을 대체·보강합니다. 핵심 수식은 손실이 아니라 관측 표현의 구성입니다.

해상도 $`H\times W`$, 카메라 $`c`$ 의 intrinsics $`K_{c}`$, 카메라→로봇 base 회전 $`R_{c}`$ ·평행이동 $`t_{c}`$, 픽셀별 depth $`D_{c}`$ 가 주어질 때, 먼저 각 픽셀을 카메라 프레임의 3D 점으로 lift 합니다.

> "We first lift each pixel into a 3D point in the camera frame," (§3)
(한글 해설 — pinhole 역투영: depth 를 곱하고 intrinsics 역행렬을 적용.)

$$P_{c}^{\mathrm{cam}}(u,v)=D_{c}(u,v)K_{c}^{-1}[u,v,1]^{\top}.$$

이어 camera-to-robot 변환으로 로봇 base 프레임 좌표로 옮깁니다.

> "We then apply the camera-to-robot transform to express the point in the robot base frame," (§3)
(한글 해설 — extrinsics $`(R_{c}, t_{c})`$ 를 적용한 강체변환. 결과 $`P_{c}^{\mathrm{R}}`$ 는 RGB 와 같은 $`H\times W`$ 그리드에 픽셀당 하나의 3D 좌표를 갖습니다.)

$$P_{c}^{\mathrm{R}}(u,v)=R_{c}P_{c}^{\mathrm{cam}}(u,v)+t_{c}.$$

> "The same physical scene point receives the same robot-frame coordinate regardless of the camera viewpoint, although the pixel $`(u,v)`$ where it appears may change." (§3)
(한글 해설 — 시점 불변성의 핵심 진술. 물리 점의 좌표값은 시점과 무관하게 동일하고, 그 점이 나타나는 픽셀 위치만 달라집니다. 이것이 시점 강건성의 수학적 근거입니다.)

마지막으로 pointmap 을 현재 end-effector 위치 $`t_{\mathrm{EE}}`$ 로 재중심화합니다.

> "We additionally re-center the pointmap on the current end effector," (§3)
(한글 해설 — 모든 점을 현재 그리퍼 위치의 상대좌표로 바꾸는 단순 뺄셈.)

$$P^{\mathrm{EE}}_{c}(u,v)=P_{c}^{\mathrm{R}}(u,v)-t_{\mathrm{EE}},$$

> "Because actions are defined as motions of that end effector, the observation and the action space now share a common origin." (§3)
(한글 해설 — 액션이 EE 의 움직임으로 정의되므로, EE centering 은 관측과 액션이 같은 원점을 공유하게 만들어 목표 좌표가 곧 그리퍼가 이동해야 할 변위가 됩니다.)

**Pointmap-RGB 융합.** pointmap 이 RGB 와 같은 그리드이므로 동일 아키텍처의 시각 인코더로 처리합니다.

> "We use a separate pointmap encoder $`g_{\phi}`$, initialized from the RGB encoder $`f_{\theta}`$, to map $`P^{\mathrm{EE}}_{c}`$ into tokens with the same shape as the RGB tokens." (§3)
(한글 해설 — pointmap 인코더 $`g_{\phi}`$ 는 RGB 인코더 $`f_{\theta}`$ 의 가중치로 초기화되어 사전학습 시각 표현을 재사용합니다. 별도 tower 지만 새 아키텍처는 아닙니다.)

토큰은 대응하는 RGB 토큰에 element-wise 로 더해집니다.

$$z_{c}=f_{\theta}(I_{c})+g_{\phi}(P^{\mathrm{EE}}_{c})\in\mathbb{R}^{N_{\mathrm{tok}}\times d},$$

여기서 $`f_{\theta}`$ 는 RGB 인코더, $`I_{c}`$ 는 카메라 $`c`$ 의 RGB 이미지입니다. 융합 토큰 $`z_{c}`$ 가 원래 RGB 토큰을 대체해 VLA 의 시각 입력이 됩니다.

> "... because pointmap tokens are added onto the RGB tokens rather than concatenated, it introduces no extra tokens." (§1)
(한글 해설 — concat 이 아닌 덧셈이므로 토큰 시퀀스 길이가 늘지 않고 point cloud 전용 인코더·voxel 모듈도 없습니다. 이것이 "minimal architectural change" 의 실체입니다.)

### 학습 셋업

- **백본** — 사전학습 VLA 두 종 $`\pi_{0.5}`$ 와 SmolVLA. 각 백본에서 RGB 단독 vs. RGB+pointmap 두 정책은 시각 입력만 다릅니다. 시각 tower 는 SigLIP.
- **통제 분석(§4)** — 대신 base PaliGemma 체크포인트에서 초기화한 $`\pi`$-style 아키텍처(action expert 는 from scratch)를 써서 대규모 로봇 사전학습을 confounder 에서 제거.
- **최적화** — AdamW, peak LR $`10^{-4}`$, cosine 스케줄 + 5% linear warmup, bfloat16, effective batch size 64.
- **스텝** — $`\pi_{0.5}`$ 20k, SmolVLA 60k (통제 분석은 30k).
- **액션** — end-effector delta chunk. sim: chunk 50(25 실행), real: chunk 20(10 실행), 제어 20 Hz.
- **데이터** — sim: RoboCasa 24 atomic task × 50 human demo, 50 episode 평가. real: Franka Research 3 + RealSense(wrist D405 + external D435i), 4 task × 3 카메라 배치 × 15 demo = 180 demo. real pointmap 은 RealSense stereo depth + 일회성 hand-eye calibration 으로 구성되어 센서 노이즈를 포함.

---

## 📊 실험 설정과 결과

평가지표는 task success rate(SR, %)이며, sim 은 task 당 50 episode, real 은 카메라 조건당 15 rollout, 모두 단일 최종 체크포인트로 보고(방법별 best 체크포인트 선택 없음)합니다.

### 통제 분석 (§4, RoboCasa, $`\pi`$-style + PaliGemma init, 30k step)

**RQ1 — camera 정보 조건화 vs. 사전 변환 (Table 1).**

| Input | D | K | E | Transform | SR |
|---|---|---|---|---|---|
| RGB | – | – | – | None | 27.9 |
| RGB + Plücker | – | ✓ | ✓ | Learned | 28.7 |
| RGB + Plücker + Depth | ✓ | ✓ | ✓ | Learned | 31.6 |
| RGB + Pointmap | ✓ | ✓ | ✓ | Pre-computed | 34.7 |

> "RGB + Pointmap reaches 34.7, even though it is constructed from the same depth, intrinsics, and extrinsics available to RGB + Plücker + Depth." (§4.1, Table 1)
(한글 해설 — 마지막 두 행은 같은 depth·보정값을 쓰고 로봇 프레임 기하를 *사전 계산* 하느냐만 다릅니다. 3.1점 격차(34.7 vs 31.6)가 "정책에 추론을 맡기지 말고 미리 변환하라"는 사전 계산의 순수 이득을 격리합니다.)

**RQ2 — 이미지형 pointmap vs. point cloud (Table 2).**

| Input | 3D encoder | Fusion | SR |
|---|---|---|---|
| RGB | – | – | 27.9 |
| RGB + Point cloud | MLP | concat | 24.2 |
| RGB + Point cloud | PTv3 | concat | 32.8 |
| RGB + Pointmap | – | concat | 30.7 |
| RGB + Pointmap | – | add | 34.7 |

> "This raises success from 30.7 to 34.7. RGB + pointmap with element-wise addition also outperforms both the lightweight point cloud baseline with an MLP encoder (24.2) and the pretrained point cloud baseline with Point Transformer v3 (32.8)." (§4.2, Table 2)
(한글 해설 — 그리드 보존이 핵심인 이유는 element-wise 덧셈을 가능케 하기 때문입니다. 같은 3D 점이라도 concat(30.7)보다 add(34.7)가 높고, 강한 전용 인코더 PTv3(32.8)조차 add 형 pointmap 에 뒤집니다. point cloud 는 그리드 대응이 없어 add 자체가 불가능합니다.)

**RQ3 — base 원점 vs. EE 원점 (Table 3).**

| Input | Fixed | Rand. | $`\Delta`$ |
|---|---|---|---|
| RGB | 27.9 | 25.8 | $`-2.1`$ |
| RGB + Pointmap (base) | 34.7 | 32.7 | $`-2.0`$ |
| RGB + Pointmap (EE) | 36.9 | 36.6 | $`\mathbf{-0.3}`$ |

![Figure 5 — EE centering 이 상호작용 목표를 공통 원점 근처로 모음](https://arxiv.org/html/2607.11498/x5.png)

> "Figure 5: End-effector centering concentrates interaction targets near a common origin. (a) Target coordinates are broadly distributed in the robot-base frame but cluster near the origin in the end-effector-centered frame. (b) Two example tasks show that targets with different robot-base coordinates lie near the end-effector-centered origin at grasp." (§4.3)
(한글 해설 — base 프레임에서 흩어진 목표 좌표가 EE 프레임에서는 원점 근처로 모여, 같은 동작을 요구하는 상호작용이 일관된 국소 기하를 갖게 됨을 보이는 그림.)

> "The robot-base-centered pointmap drops by 2.0 points ( $`34.7\to32.7`$ ), whereas the end-effector-centered pointmap drops by only 0.3 points ( $`36.9\to36.6`$ )." (§4.3, Table 3)
(한글 해설 — 평가 시점을 randomize 하면 base 원점은 2.0점 하락하지만 EE 원점은 0.3점만 하락. EE centering 이 목표의 절대 workspace 위치 의존성을 줄여 시점 강건성을 만든다는 증거.)

**RQ4 — 학습 시점 변화량 증가에 대한 강건성 (Fig 6).**

![Figure 6 — 학습 시점 변화량이 커질수록 RGB 는 하락, RGB+Pointmap 은 안정](https://arxiv.org/html/2607.11498/x6.png)

> "Figure 6: Effect of training-time camera viewpoint variation. RGB performance drops as viewpoint variation increases, while RGB + Pointmap remains stable." (§4.4)
(한글 해설 — No/Low/High 세 수준의 카메라 randomization 에서 두 입력의 성능 추이를 비교.)

> "RGB falls 9.6 points ( $`34.5\%\to24.9\%`$ ) from no to high variation, whereas RGB + pointmap falls only 1.8 ( $`37.6\%\to35.8\%`$ )." (§4.4, Fig 6)
(한글 해설 — 시점 변화가 커질수록 RGB-only 학습은 크게 어려워지는 반면 pointmap 은 거의 평탄. "로봇 프레임 기하가 시점 변화를 흡수한다"는 가설의 직접 지지.)

### 사전학습 VLA 본실험 (§5)

**Sim — RoboCasa (fixed viewpoint, 24 task, SR %; Table 4).**

| Method | Avg. | Doors | Drawers | Coffee | Pick-and-place | Turn objects |
|---|---|---|---|---|---|---|
| FP3 (point cloud policy) | 42.8 | 79.0 | 74.0 | 54.7 | 21.8 | 32.0 |
| OC-VLA | 56.3 | 80.0 | 80.0 | 42.0 | 50.5 | 48.9 |
| KYC | 59.1 | 86.5 | 86.0 | 51.3 | 48.2 | 51.4 |
| GeoVLA | 57.1 | 81.0 | 80.0 | 45.3 | 49.8 | 50.3 |
| PointVLA | 57.3 | 87.5 | 85.0 | 44.0 | 46.3 | 50.3 |
| $`\pi_{0.5}`$ | 55.3 | 79.5 | 83.0 | 40.7 | 46.0 | 50.6 |
| $`\pi_{0.5}`$ + pointmap | **62.9** | 90.0 | 90.0 | 58.0 | 52.8 | 53.4 |
| SmolVLA | 37.2 | 68.0 | 63.0 | 39.3 | 6.5 | 46.6 |
| SmolVLA + pointmap | **41.4** | 80.0 | 77.0 | 38.0 | 12.8 | 43.4 |

> "For $`\pi_{0.5}`$, the 24-task average rises from $`55.3`$ to $`62.9`$, with gains across all five task categories. For SmolVLA, it rises from $`37.2`$ to $`41.4`$." (§5.1, Table 4)
(한글 해설 — 규모·action expert 가 다른 두 백본 모두에서 개선되어 특정 아키텍처에 종속되지 않음을 시사. 최강 camera-aware baseline KYC(59.1)와 최강 3D-augmented baseline PointVLA(57.3)도 pointmap 붙은 $`\pi_{0.5}`$(62.9) 아래. 단, SmolVLA 는 Coffee(-1.3)·Turn objects(-3.2) 두 카테고리에서 소폭 하락해 이득이 균일하지는 않습니다.)

**Real — Franka, seen/unseen 카메라 (SR %, task당 15 rollout; Table 5).**

| Eval. camera | Model | Avg. | Pick-and-place | Stack blocks | Open drawer | Close drawer |
|---|---|---|---|---|---|---|
| Seen | DP3 | 63.3 | 60.0 | 40.0 | 60.0 | 93.3 |
| Seen | $`\pi_{0.5}`$ | 73.3 | 80.0 | 53.3 | 73.3 | 86.7 |
| Seen | $`\pi_{0.5}`$ + pointmap | **78.3** | 86.7 | 60.0 | 73.3 | 93.3 |
| Unseen | DP3 | 48.3 | 33.3 | 33.3 | 40.0 | 86.7 |
| Unseen | $`\pi_{0.5}`$ | 55.0 | 40.0 | 26.7 | 66.7 | 86.7 |
| Unseen | $`\pi_{0.5}`$ + pointmap | **66.7** | 53.3 | 46.7 | 73.3 | 93.3 |

> "Its margin over RGB therefore widens from $`+5.0`$ at the seen placement to $`+11.7`$ at the unseen one." (§5.2, Table 5)
(한글 해설 — seen 에서 RGB 대비 +5.0(78.3 vs 73.3)이던 이득이 미학습 배치(unseen)에서 +11.7(66.7 vs 55.0)로 확대. RGB-only 는 18.3점 붕괴, pointmap 은 11.6점만 하락. 3D 입력을 쓰는 DP3 도 unseen 에서 RGB-only 와의 격차가 +10.0→+6.7 로 좁혀지고 Stack blocks 에서는 역전(33.3 vs 26.7)해, "3D 입력이 RGB 보다 시점 변화에 강하다"는 방향을 반대편에서 재확인.)

---

## ⚖️ 한계

- **주입 위치·사전학습 상호작용 미탐구(저자 명시)** — pointmap 을 action expert 대비 어디에 주입할지, 사전학습 recipe 와 어떻게 상호작용하는지를 ablate 하지 않아 최적 결합 방식이 미결. element-wise add 라는 단일 융합점만 검증되어, 백본 내부 layer 별 주입의 이득/손실은 열려 있습니다.
- **Point cloud 비교의 단일 샘플링 예산(저자 명시)** — point cloud baseline 은 카메라당 1024점(또는 DP3 4096점) 한 예산만 비교. 더 큰 예산이면 격차가 좁혀질 수 있어, "이미지형 우위" 결론의 강도가 예산에 조건적입니다.
- **calibration 의존(저자 명시)** — pointmap 은 학습·테스트 모두에서 교정된 intrinsics·extrinsics 를 요구합니다. calibration 이 없거나 부정확한 셋업(특히 eye-in-hand 만 있거나 미보정 다기관 데이터)에서는 표현 자체를 구성할 수 없어 적용 범위가 제한됩니다.
- **카메라 변화의 축이 좁음(저자 명시)** — 실험은 카메라 *배치/extrinsics* 변화에 집중하고, 카메라 *개수* 나 *FoV* 변화는 다루지 않습니다. 배포 시 카메라 수가 달라지는 실전 시나리오로의 전이는 미검증.
- **depth 품질에 대한 민감도(추론)** — real pointmap 은 stereo depth + 일회성 hand-eye calibration 으로 만들어져 센서 노이즈를 담습니다. depth 오차와 calibration drift 가 로봇 좌표계 좌표에 직접 전파되므로, sim(정확한 기하) 대비 real 이득이 왜 작아지는지(seen +5.0)의 부분 원인일 수 있습니다. 논문은 이 민감도를 정량화하지 않았습니다.
- **SmolVLA 이득의 비균일성(추론)** — SmolVLA 는 두 카테고리에서 오히려 하락(Table 4)해, pointmap 이득이 백본 용량·action expert 구조에 따라 달라짐을 시사. 작은 백본에서는 추가 시각 tower 가 용량을 분산시킬 가능성.

---

## ♻️ 재현성

- **코드** — 프로젝트 웹사이트([davian-robotics.github.io/pointmap](https://davian-robotics.github.io/pointmap/))는 존재하나, 본문에서 공식 코드 릴리스 여부는 명시되지 않았습니다. baseline(KYC, OC-VLA, GeoVLA, PointVLA)은 공식 코드가 없어 저자가 $`\pi_{0.5}`$ 위에 재구현.
- **데이터** — sim 은 공개 벤치마크 RoboCasa(24 atomic task, task당 50 human demo). real 은 자체 수집 180 demo(공개 여부 불명).
- **하드웨어** — Franka Research 3 + RealSense D405(wrist) + D435i(external), Meta Quest 3 VR teleop. 학습은 effective batch 64, bfloat16, $`\pi_{0.5}`$ 20k / SmolVLA 60k step 으로 상세 명시(Table 6)되어 재현 정보는 비교적 충실.
- **주의** — 대부분의 baseline 이 재구현이라, 절대 SR 비교는 저자 재구현 충실도에 의존합니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P2(구조화된 멀티모달 관측 융합) — D8(multi-camera spatial-geometric grounding) 정면**. 본 논문의 robot-centric pointmap 은 D8 이 겨냥하는 "시점을 가로질러 정합되는 공유 3D 장면 표현"의 한 구현입니다. 다만 D8 v1 의 pin(VGGT/eVGGT-style feed-forward 기하 인코더)과는 설계 철학이 정반대 — 별도 기하 인코더로 그리드를 버리는 대신, **그리드를 보존해 사전학습 2D 가중치를 재사용** 합니다.
- **P2 — D9(action/dynamics-aware vision encoder) 긴장**. D9 v1 은 generic SigLIP stem 대신 action/dynamics-aware(DynaFLIP) 또는 geometry-distilled(eVGGT) 인코더를 선호합니다. 본 논문은 정확히 그 generic SigLIP tower 를 (RGB·pointmap 두 개로 복제해) 유지하면서, 인코더를 바꾸지 않고 *입력* 을 로봇 좌표계 기하로 바꿔 유사 목표(시점·기하 강건성)를 달성 — D9 의 "인코더 교체" 노선에 대한 저비용 대안입니다.
- **P2 — D10(fusion beyond concat) 부분 지지**. element-wise add > concat(30.7→34.7) 결과는 "flat concat 을 넘어서라"는 D10 방향을 지지하되, cross-attention 이 아니라 *공간 대응 기반 덧셈* 이라는 가장 가벼운 형태로 지지합니다.
- **P4(데이터 효율 적응 사전학습) — D19(backbone lineage & adaptation range) / D20(prior-preservation) 부수 접점**. 백본이 $`\pi_{0.5}`$ / SmolVLA(P4 lineage anchor)이고, pointmap 인코더를 RGB 인코더 가중치로 초기화해 **사전학습 시각 prior 를 재사용** 하는 점은 D20 의 "prior 보존" 정신과 정렬. 다만 본 논문의 기여는 adaptation 전략이 아니라 관측 표현이라 P4 는 부차적.
- **P0** — RoboCasa 는 평가 벤치마크로만 쓰이며 데이터/벤치마크 기여는 아님(P0 무관).
- **Identity** — hand-centric dexterity 는 직접 다루지 않습니다(pick-and-place·drawer·coffee 류 arm-level task). "관측 elevation: 공간 정보를 유지·정합" 이라는 P2 Identity tie 는 강하게 지지하지만, per-finger contact·tactile 은 부재.

---

## ✨ 핀 논문 대비 델타

- **vs. VGGT / eVGGT (P2 D8 핀)** — 두 핀은 multi-view 를 feed-forward 로 통합해 unified 3D 임베딩을 만들지만 이미지 그리드 구조를 버립니다. 본 논문의 진짜 델타는 **"3D 를 이미지 그리드 형태로 유지"** 라는 정반대 선택으로, 전용 기하 인코더 없이 사전학습 RGB 인코더를 그대로 복제·재사용한다는 점입니다. 즉 "geometry grounding" 이라는 목표는 공유하되, "새 인코더 vs. 입력 변환"에서 후자를 택합니다.
- **vs. DynaFLIP (P2 D9 핀)** — DynaFLIP 은 인코더를 action/dynamics-aware 로 바꾸는 노선. 본 논문은 인코더를 건드리지 않고 입력만 로봇 좌표계로 바꿔 시점 강건성을 얻는, 훨씬 저침습적 대안. 두 노선은 orthogonal 해 결합 가능성이 있습니다(dynamics-aware 인코더 + robot-frame pointmap 입력).
- **새로움의 핵심** — 기존 3D-aware VLA(GeoVLA, PointVLA)는 전용 3D 모듈/전문가를 붙여 사전학습 가중치를 상속하지 못하는데, 본 논문은 "픽셀당 로봇 좌표계 XYZ 이미지 + element-wise add" 라는 최소 변경으로 이를 우회한 점이 진정한 델타(RoboCasa 에서 두 baseline 을 상회).

---

## ⚙️ 의사결정 함의

- **D8 재정식화 후보** — "unified 3D 임베딩(VGGT-style)" 을 D8 의 유일 경로로 두는 대신, **"robot-frame pointmap 입력(그리드 보존) vs. feed-forward 기하 인코더(그리드 파괴)"** 를 D8 내부의 명시적 비교 축으로 승격. 우리 스택이 사전학습 2D VLA 가중치 재사용을 중시한다면 pointmap 입력 경로가 저비용 우선순위 후보.
- **구체적 config 함의** — 관측 파이프라인에 `pointmap` modality 를 추가: 픽셀당 XYZ(로봇 base 프레임), `ee_centering=True`(현재 EE 위치 감산), 별도 시각 tower 는 RGB 인코더 가중치로 init, 융합은 `fusion=elementwise_add`(concat 아님, 토큰 수 불변). calibration 입력(`K, R, t`)이 데이터 계약에 필수로 추가됨.
- **손실/하이퍼는 불변** — 백본 액션 손실을 그대로 쓰므로 새 loss term 없음. 바뀌는 것은 *입력 텐서 계약* 과 *시각 인코더 초기화 소스* 뿐. AdamW LR $`10^{-4}`$, cosine+5% warmup, chunk 50/execute 25(sim) 같은 값이 실용 기준선.
- **평가 프로토콜 함의** — 우리 실로봇 평가에 **seen/unseen 카메라 배치** 프로토콜을 도입하면 시점 강건성을 정량화 가능. RGB-only 대비 unseen 에서의 degradation gap(본 논문 18.3 vs 11.6)이 관측 표현 선택의 결정적 지표.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 체크) calibration 가용성** — 우리 데이터/셋업에 정확한 카메라 intrinsics·extrinsics 와 EE pose 가 매 프레임 있는가? 없으면 pointmap 자체를 구성할 수 없어 방법이 성립하지 않습니다. eye-in-hand 만 있거나 미보정 다기관 데이터라면 즉시 탈락 — 코드 한 줄 없이 데이터 스키마만 확인하면 판별됩니다.
- **depth 품질 전이** — 본 논문 이득은 sim(정확 기하)에서 크고 real(센서 depth)에서 작아집니다(seen +5.0). 우리 depth 센서 노이즈·결측(반사·투명 물체)이 크면 로봇 좌표계 좌표에 직접 오차가 실려 이득이 사라질 수 있습니다. 저비용 검증: 소수 시연으로 pointmap 시각화해 좌표 노이즈 육안 점검.
- **hand-centric task 로의 전이** — 검증 task 는 모두 arm-level(pick-and-place, drawer, coffee)이며 접촉풍부 손가락 조작이 없습니다. EE centering 은 "그리퍼–목표 변위" 가정에 기대는데, 다지 손의 손가락별 접촉에서는 단일 EE 원점이 부적절할 수 있습니다. 우리 dexterity 목표로의 전이는 별도 검증 필요.
- **작은 백본에서의 용량 분산** — SmolVLA 는 일부 카테고리에서 하락. 우리 백본이 작다면 두 번째 시각 tower 가 용량을 갉아 순이득이 음수일 수 있습니다. sanity check: 소규모 백본에서 RGB vs RGB+pointmap 을 소수 task 로 먼저 비교.
- **단일 시점 데이터에서의 무효** — 이 방법의 이득은 학습 데이터가 *여러 시점* 을 aggregate 할 때 커집니다(Fig 6). 우리 데이터가 사실상 고정 시점이라면 frame mismatch 가 무해해 pointmap 이 순수 오버헤드가 될 수 있습니다. 데이터의 시점 분산부터 측정.

---

## 💡 컨텍스트 제안

- **P2 D8 v1 확장 검토(사람 판단 필요)** — D8 v1 이 VGGT/eVGGT 기반 "unified 3D 임베딩(그리드 파괴)" 을 기본 경로로 두는데, 본 논문은 "그리드 보존 robot-frame pointmap 입력" 이라는 유력한 대안 노선을 제시합니다. D8 결정에 "사전학습 2D 가중치 재사용 우선 시 pointmap-입력 경로" 를 tracked alternative 로 추가하는 것을 제안(결정 변경이 아니라 비교군 확장).
- **P2 Tracked Literature 후보** — 현재 P2 pin 은 VGGT·eVGGT·DynaFLIP·ForceFlow·ViTacFormer(8개 상한 중 5개). 본 논문은 D8 의 "저침습 그리드보존" 반대극 대표로 후보 가치가 있으나, hand-centric/tactile 축이 없어 우선순위는 사람 판단에 맡깁니다.
- context 파일은 편집하지 않았습니다.

> 💡 base 매핑은 `/implement-design analysis/2607.11498/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
