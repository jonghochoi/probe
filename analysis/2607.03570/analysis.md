# Paper Analysis — Cross-Embodiment Robot Manipulation via a Unified Hand Action Space

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Cross-Embodiment Robot Manipulation via a Unified Hand Action Space |
| 저자 | Luis Felipe Casas, Robert Teal, Keval Shah, Abhijit Tadepalli, Wanxin Jin, Yu Xiang (UT Dallas · Arizona State University) |
| 링크 | [arXiv:2607.03570](https://arxiv.org/abs/2607.03570) · [Website](https://irvlutd.github.io/UHAS/) |
| 발행일 / 버전 | 2026-07-03 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-08-02 |
| 관련 Pillar | P1, P3, P2 |
| 태그 | dexterity, sim2real |

<!-- 링크 검증 메모: `https://arxiv.org/abs/2607.03570` (HTTP 200) 과
     `https://arxiv.org/html/2607.03570` (HTTP 200) 은 정상 확보했습니다.
     Website 는 논문 각주 1 에 verbatim 으로 명시된 저자 프로젝트 페이지
     (`Data, code, and videos for the project are available at
     https://irvlutd.github.io/UHAS/`) 이나, 본 실행 환경의 네트워크 정책상
     `curl -L https://irvlutd.github.io/UHAS/` 가
     `curl: (56) CONNECT tunnel failed, response 403` 으로 차단되어
     직접 도달을 확인하지 못했습니다 (404 가 아니라 프록시 차단).
     GitHub / HuggingFace 링크는 본문에 URL 이 명시되어 있지 않아
     날조하지 않고 생략합니다. -->

---

## 🧭 한 줄 요약 (TL;DR)

로봇 손의 행동을 관절 공간이 아니라 **정규 구(canonical sphere) 표면의 기하학적 변형**으로 표현하는 공유 액션 공간 UHAS 와, 그 변형을 각 손의 관절각으로 되돌리는 경량 역기구학 알고리즘 CIK 를 제안합니다. Allegro · LEAP · Shadow · MANO 네 손에서 단일 정책으로 인핸드 큐브 재배향을 학습하고, 학습에서 제외된 손으로의 zero-shot 전이와 500 iteration 급속 미세조정, 실제 로봇 배포까지 보입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 다지 손 조작 정책은 특정 손 하드웨어의 관절 공간에 묶여 있어 손을 바꾸면 정책을 다시 학습해야 합니다. 손마다 손가락 수·관절 수·관절 축 배치가 모두 달라, 서로 다른 플랫폼 사이에서 학습된 행동을 옮길 공통 인터페이스가 없습니다.
- **기존 접근의 한계** — 대규모 로봇 학습 시스템과 데이터셋은 대부분 평행 그리퍼에 쏠려 있고, 다지 손 시스템은 임베디먼트별 액션 공간·데이터셋·재학습 절차에 의존합니다. CrossFormer · Universal Actions · XL-VLA 같은 cross-embodiment 연구도 별도 액션 헤드나 잠재 액션, 혹은 정규화된 *관절 공간* 표현에 머물러 손 형상 자체의 이질성을 흡수하지 못합니다.
- **본 논문의 가설** — 손이 기계적으로 아무리 달라도 물체를 다룰 때는 **물체 중심 작업 공간 주변의 공간적 접촉 패턴**으로 상호작용한다는 관찰이 성립하므로, 그 공통 기하를 구 표면으로 놓고 행동을 "구의 변형"으로 정의하면 형상에 무관한 공유 액션 공간을 얻을 수 있다는 가설입니다.
- **왜 지금 중요한가** — 로봇 파운데이션 모델 방향에서는 이질적 플랫폼 사이의 데이터 공유와 정책 확장이 병목입니다. 손 단계에서 공유 액션 공간이 성립하면 손별 데이터가 하나의 좌표계로 합쳐지고, 새 손이 들어와도 처음부터 재학습하지 않아도 됩니다.
- **기하 표현의 선행 근거** — D(R,O) Grasp 나 RobotFingerPrint(RFP) 처럼 그리퍼 표면과 정규 구 사이 대응을 세워 cross-embodiment 파지를 푸는 흐름이 이미 있습니다. 본 논문은 그 구 대응을 파지 표현에서 **액션 공간 자체**로 밀어 올립니다.

---

## 🧩 핵심 기여

- 로봇 손의 행동을 정규 구의 변형으로 모델링하는 기하 기반 액션 표현 **Unified Hand Action Space (UHAS)** 를 제안합니다. URDF 만 주어지면 손별 구(중심·반지름·정규 방향)를 자동 구성하고, 반지름 $`r`$ 로 정규화해 단위 구 위의 척도 불변 표현을 얻습니다.
- 구 표면과 손 내측 표면 사이의 **조밀한 구면좌표 대응(unified hand surface correspondence)** 을 세웁니다. 손 자세가 바뀌어도 각 표면점의 구면좌표 $`(\theta,\phi)`$ 는 불변이므로, 서로 다른 손이 하나의 구면좌표 도메인을 공유합니다.
- 구 표면 전체의 점별 변형 대신 **driving plane(측면 변형 $`\Delta\theta`$) + driving vector(반경 변형 $`\Delta r`$)** 라는 희소 제어 프리미티브로 변형장을 매개화하고 보간으로 복원합니다. 5 plane × 2 vector 구성에서 15 차원 연속 액션이 됩니다.
- 변형된 구를 임베디먼트별 관절각 $`\mathbf{q}`$ 로 되돌리는 **Cascade Inverse Kinematics (CIK)** 를 제안합니다. 관절을 lateral / encompassing 으로 분류하고, 전자는 사전 계산 lookup table 로 상수 시간에, 후자는 근위→원위 1 회 순차 통과로 풀어 반복 수치 최적화를 제거합니다. 실환경 파이프라인에서 최대 150 Hz 로 동작합니다.
- 네 손(Allegro · LEAP · Shadow · MANO)에서 인핸드 큐브 재배향을 시뮬레이션 · 실환경 양쪽으로 검증하고, **다중 손 단일 정책 · zero-shot 전이 · 500 iteration 미세조정 · 실제 LEAP/Allegro 배포**를 함께 보고합니다.

---

## 🔑 기술 키워드

- **Unified Hand Action Space (UHAS)** — 손의 행동을 관절각이 아니라 손바닥 앞에 놓인 정규 구의 변형으로 적는 공유 액션 좌표계. 손가락을 직접 지시하는 대신 "손이 감싸는 공(ball)을 어떻게 찌그러뜨릴지"를 지시하는 방식입니다.
- **Cascade Inverse Kinematics (CIK)** — 변형된 구를 손별 관절각으로 되돌리는 역기구학. 반복 최적화 없이 관절을 역할별로 나눠 한 번씩만 순차적으로 푸는 것이 특징입니다.
- **Driving plane** — 구 중심을 지나고 고정 방위각 $`\theta_{\text{plane}}`$ 에 놓인 평면. 회전시키면 그 방향의 측면 변형 $`\Delta\theta`$ 가 정해집니다. 손가락 하나에 평면 하나가 할당됩니다.
- **Driving vector** — 각 driving plane 안에서 고정 극각 $`\phi`$ 에 놓인 제어점의 반경 변위. 손가락이 구를 얼마나 파고들거나 벌어질지를 정하는 손잡이입니다.
- **Lateral joint** — 손끝의 방위각 $`\theta`$ 를 주로 바꾸는 관절, 즉 손가락을 좌우로 벌리고 모으는 관절.
- **Encompassing joint** — 손끝의 반경 거리 $`r`$ 와 극각 $`\phi`$ 를 주로 바꾸는 관절, 즉 손가락을 구부려 구 표면을 감싸게 하는 관절.
- **Unified hand surface correspondence** — 구 표면 샘플점을 손 내측 표면으로 투영해 만든 조밀 대응. 자세가 변해도 각 점의 구면좌표는 그대로라 손 사이 공통 주소 체계로 쓰입니다.
- **Homogeneous observation** — 원 관절값 대신 손가락 체인 위 표면 대응점의 위치·속도를 정규 구 좌표계로 표현하고 반지름으로 정규화한 관측. 손마다 다른 관절 의미·수치 범위 문제를 없앱니다.
- **Average Consecutive Reorientations** — 큐브가 처음 떨어지기 전까지 연속 성공한 재배향 횟수의 평균(시뮬레이션 최대 10). 성공률과 달리 장기 안정성을 잡아내는 지표입니다.
- **MANO Human Hand** — 사람 손 형상을 파라미터화한 표준 모델. 본 논문에서는 5 손가락 시뮬레이션 임베디먼트 중 하나로 쓰이며, zero-shot 전이의 원천 손 역할도 합니다.

---

## 🔬 방법론

### 직관

이 논문의 출발점은 단순한 관찰 하나입니다. 손의 기계 구조는 제각각이지만, 물체를 쥐고 굴릴 때 손이 하는 일은 결국 "손바닥 앞의 어떤 공간을 손가락들이 둘러싸고 조이거나 벌리는" 동작으로 요약됩니다. 그렇다면 정책이 지시해야 할 것은 관절 몇 번을 몇 도 돌릴지가 아니라, **그 둘러싸는 공간의 모양을 어떻게 바꿀지**여도 됩니다.

그래서 손바닥 앞에 가상의 공(정규 구)을 하나 띄웁니다. 이 공은 URDF 만 있으면 자동으로 만들어집니다 — 손바닥 중심에서 손끝까지 평균 거리를 재고, 그 값으로 반지름을 정하고, 손바닥 법선 방향으로 밀어 배치한 뒤, 손별 크기 차이를 없애려고 반지름으로 나눠 단위 구로 정규화합니다. 손가락 표면의 각 점은 이 공 표면의 어느 위치에 대응하는지 한 번 기록해 두며, 손을 아무리 구부려도 그 대응 좌표는 변하지 않습니다. 결국 4 손가락 Allegro 와 5 손가락 Shadow 가 똑같은 "공 표면 주소 체계"를 쓰게 됩니다.

정책은 이 공을 찌그러뜨리는 명령만 내립니다. 다만 표면 전체를 점별로 지시하면 차원이 폭발하므로, 손가락마다 하나씩 배정한 평면(driving plane)을 회전시켜 좌우 변형을, 그 평면 위 두 개의 제어점(driving vector)을 밀고 당겨 반경 변형을 지시하고, 나머지 표면은 보간으로 채웁니다. 손가락 다섯 개 기준 15 개 숫자면 충분합니다.

남은 문제는 찌그러진 공을 실제 관절각으로 되돌리는 일입니다. 일반적인 수치 역기구학은 실시간 제어에 너무 느리므로, 이 논문은 관절을 역할로 나눕니다. 손가락을 좌우로 벌리는 관절은 미리 만들어 둔 표에서 값을 바로 꺼내 쓰고, 손가락을 감아 쥐는 관절은 뿌리에서 손끝 방향으로 한 번만 훑으며 순서대로 각도를 확정합니다. 반복 최적화가 전혀 없어 최대 150 Hz 로 돌아갑니다.

![Figure 1 — Sphere deformation mapped to multiple hand embodiments](https://arxiv.org/html/2607.03570/x1.png)

> "Figure 1: In our unified hand action space, an action is represented as the deformation of a canonical sphere. A deformed sphere is mapped to hand configurations of various embodiments (LEAP [27], Allegro [36], MANO Human [25] and Shadow [31])." (§1)
(한글 해설 — 하나의 변형된 구가 네 개의 서로 다른 손 자세로 동시에 사상되는 그림으로, "액션은 손이 아니라 구에 정의된다"는 논문 전체의 주장을 한 장으로 요약합니다.)

### 아키텍처

**1. 손별 구 자동 생성 (§3.1).** URDF 에서 열린 손 자세의 손바닥·손끝 좌표계를 식별하고, 손가락 뿌리 위치를 평균해 손바닥 중심을, 그 중심에서 손끝까지 평균 거리 $`l`$ 을 구합니다. 반지름은 $`r=\frac{2l}{\pi}`$ 로 정의되는데, 이는 손바닥 중심에서 손끝까지가 대략 $`90^{\circ}`$ 호에 해당하도록 맞춘 값입니다.

> "The sphere radius is defined as $`r=\frac{2l}{\pi}`$ , placing the sphere within the natural grasping workspace of the hand and approximately covering a $`90^{\circ}`$ arc from the palm center to the fingertips." (§3.1)
(한글 해설 — 반지름을 임의로 고르지 않고 손의 자연스러운 파지 작업 공간에 걸치도록 기하학적으로 유도한 점이 핵심입니다. 이 한 줄 덕분에 손 크기가 달라도 구가 항상 "손가락이 모이는 자리"에 놓입니다.)

구 중심은 손바닥 중심에서 바깥쪽 손바닥 법선 방향으로 거리 $`r`$ 만큼 이동한 지점에 둡니다. 정규 방향은 $`+z`$ 축을 바깥쪽 손바닥 법선에, $`+x`$ 축을 중지 방향에 맞추고 $`y`$ 축은 오른손 법칙으로 정합니다. 마지막으로 구 좌표계의 모든 거리를 손별 반지름 $`r`$ 로 나눠 단위 구로 정규화합니다 — 이 정규화가 척도 차이를 지우는 지점이며, 손별 원래 구 파라미터는 CIK 가 다시 쓰기 위해 보존됩니다.

![Figure 2 — Automatic sphere creation from a URDF](https://arxiv.org/html/2607.03570/x2.png)

> "Figure 2: Illustration of the process of creating a sphere for a robotic hand given its URDF." (§3.1)
(한글 해설 — 손바닥 중심 추정 → 반지름 산출 → 법선 방향 배치 → 단위 구 정규화로 이어지는 §3.1 의 네 단계를 순서대로 보여줍니다. 이 과정이 전부 자동이라는 점이 새 손을 붙이는 비용을 결정합니다.)

**2. 통합 손 표면 대응 (§3.2).** 구 표면에 점을 균일 샘플링하고 각 점의 구면좌표 $`(\theta,\phi)`$ 와 바깥쪽 법선을 계산합니다. $`\theta`$ 는 방위각(azimuthal), $`\phi`$ 는 극각(polar)입니다. 이 점들을 손 내측 표면의 가까운 점으로 투영해 손바닥·손가락 표면과의 조밀 대응을 만듭니다.

> "Although the 3D locations of the hand surface points vary under different hand configurations, their associated spherical coordinates remain unchanged, as shown in Fig. 3 (d)." (§3.2)
(한글 해설 — 이것이 UHAS 를 성립시키는 불변식입니다. 3D 위치는 자세에 따라 움직이지만 구면좌표 라벨은 고정이므로, 서로 다른 손이 같은 좌표 도메인 위에서 대화할 수 있습니다.)

![Figure 3 — Unified hand surface correspondence](https://arxiv.org/html/2607.03570/x3.png)

> "Figure 3: Construction of the unified hand surface correspondence." (§3.2)
(한글 해설 — (a) 구 표면 균일 샘플링 → (b) 구면좌표·법선 계산 → (c) 손 내측 표면 투영 → (d) 자세 변화에도 좌표 라벨 유지, 라는 §3.2 의 자세 불변 대응 구성을 시각화합니다.)

**3. 구 변형 액션 공간 (§3.3).** 정규화된 기준 구 위 점의 구면좌표를 $`(\theta,\phi,r)`$ 로 두고 변형 전 $`r=1`$ 로 둡니다. 변형은 $`(\Delta\theta,\Delta r)`$ 두 성분만 씁니다 — 구의 북극이 손바닥 프레임에 강체로 고정되어 있기 때문에 극각 변형을 따로 둘 필요가 없다는 논리입니다.

- **driving plane** — 구 중심을 지나고 고정 방위각 $`\theta_{\text{plane}}`$ 에 놓인 유한 개의 평면. 측면 변형 성분 $`\Delta\theta`$ 를 제어합니다.
- **driving vector** — 각 평면 안 고정 극각 $`\phi`$ 위치의 제어점들이 갖는 반경 변위. 반경 변형 성분 $`\Delta r`$ 을 매개화합니다.
- **보간 복원** — 표면 전 지점의 $`\Delta\theta`$ 는 이웃 driving plane 값의 보간으로, $`\Delta r`$ 은 $`(\theta,\phi)`$ 파라미터 공간에서의 2 차원 보간으로 얻습니다.

> "If we use five driving planes with two driving vectors per plane, it results in a 15-dimensional continuous action representation, i.e., $`5+2\times 5`$ ." (§3.3)
(한글 해설 — 22-DOF 급 손도 15 차원 연속 벡터 하나로 지시된다는 뜻이며, 이 차원 수가 손 개수와 무관하게 고정된다는 점이 cross-embodiment 정책을 가능하게 하는 실질적 조건입니다. 실제로 driving plane 은 손가락에 정렬해 배치합니다.)

![Figure 4 — Sphere deformation parameterization](https://arxiv.org/html/2607.03570/x4.png)

> "Figure 4: Sphere deformation parameterization in the Unified Hand Action Space (UHAS). (a) Initial configuration of four driving planes. (b) Rotating the driving planes controls the lateral deformation $`\Delta\theta`$ . (c) Radial displacement of the driving vectors controls $`\Delta r`$ . (d) The final deformed sphere reconstructed through interpolation." (§3.3)
(한글 해설 — 액션 벡터의 각 성분이 구 위에서 정확히 무엇을 움직이는지를 (a)–(d) 로 분해해 보여줍니다. 정책 출력의 물리적 의미를 확인할 때 가장 먼저 볼 그림입니다.)

**4. Cascade Inverse Kinematics (§3.4, §A).** 변형된 구가 주어지면 §3.2 대응을 통해 각 손 표면점의 목표 위치가 곧바로 정해지고, CIK 는 그 목표를 만족하는 $`\mathbf{q}`$ 를 계산합니다.

- **관절 분류** — URDF 기준 열린 손 자세에서 관절을 하나씩 전 가동범위로 훑으며 순방향 기구학(FK)으로 손끝 구면좌표 $`(\theta,\phi,r)`$ 변화를 기록해 lateral / encompassing 으로 자동 분류합니다. 관절 회전축이 손끝을 향하는 경우에는 나머지 관절을 부분적으로 굽힌 뒤 다시 훑어 지배적 효과를 판정합니다. 손별로 한 번만 수행합니다.
- **lateral 관절 lookup table** — 각 lateral 관절을 균일 간격으로 훑으며, 값을 고정한 채 변형되지 않은 기준 구 위에서 encompassing 관절을 풀고, 그 결과 손끝 방위각 $`\theta_{\text{fingertip}}`$ 을 기록해 $`q_{\text{lateral}}\mapsto\theta_{\text{fingertip}}`$ 매핑을 저장합니다. 추론 시에는 목표 각을 계산한 뒤 표에서 바로 꺼냅니다.

$$\theta_{\text{fingertip}}=\theta_{\text{initial}}+\Delta\theta$$

여기서 $`\theta_{\text{initial}}`$ 은 손가락의 중립(가동범위 중앙) 자세에 해당합니다. 표는 손별로 오프라인 1 회 생성되며 런타임에는 상수 시간 조회입니다.

- **encompassing cascade** — lateral 관절이 확정된 뒤, 각 손가락의 기구학 체인을 따라 근위→원위 순서로 encompassing 관절을 하나씩 풉니다. 관절 $`i`$ 마다 이미 확정된 부모 관절값으로 FK 를 돌려 해당 관절과 그 하위 링크의 목표 구 표면점들을 관절 $`i`$ 의 국소 좌표계로 옮긴 뒤, 그 점들을 변형된 구 표면에 얹는 각도를 직접 계산합니다. 반복 수치 최적화 없이 한 번의 순방향 통과로 끝납니다.
- **Sphere Controller** — 구 변형 매개화 + CIK 를 합친 최종 제어기. 정책이 매 스텝 $`\Delta\theta`$ / $`\Delta r`$ 을 내면 CIK 가 저수준 제어기로 보낼 관절 위치를 반환합니다. 손가락들은 UHAS 정식화에서 기구학적으로 독립이므로 손가락별로 순차·독립 해결됩니다.

> "Because each joint is solved exactly once in a single forward pass with no iterative numerical optimization, the cascade remains extremely lightweight." (§A)
(한글 해설 — CIK 의 속도 이점은 근사나 병렬화가 아니라 문제 구조를 분해한 데서 나옵니다. 관절당 정확히 한 번만 푼다는 성질이 150 Hz 를 만들고, 실환경 병목은 CIK 가 아니라 LEAP 손 시리얼 통신과 AprilTag 물체 포즈 추정이었다고 명시합니다.)

![Figure 5 — Joint classification and the CIK cascade](https://arxiv.org/html/2607.03570/x5.png)

> "Figure 5: We classify hand joints into (a) lateral joints and (b) encompassing joints and; (c) Illustration of the cascade inverse kinematics algorithm on a deformed sphere." (§3.4)
(한글 해설 — CIK 의 두 단계(표 조회로 끝나는 lateral, 근위→원위 순차 통과인 encompassing)가 관절 분류에서 어떻게 갈라지는지를 보여줍니다.)

**5. 관측 공간 (§B).** 액션뿐 아니라 관측도 정규화해야 단일 정책이 성립합니다. 원 관절값은 손마다 의미와 수치 범위가 달라 직접 쓸 수 없으므로, 손가락 체인을 뿌리에서 손끝까지 7 개 등간격 점으로 이산화하고 각 점의 부모 관절을 정규 구 위 최근접 표면 대응으로 정합니다. 위치는 FK 로, 선속도·각속도는 현재 관절 상태에서 평가한 Jacobian 으로 계산합니다. 본문 정책들은 이 중 **중간점과 손끝 두 점만** 유지하며, 모든 위치·속도는 정규 구 좌표계로 표현하고 손별 반지름 $`r`$ 로 정규화합니다. 4 손가락 손은 약지 관측을 복제해 5 손가락과 차원을 맞춥니다.

> "However, raw joint values cannot be used directly because their semantic meaning and numerical ranges vary significantly across embodiments, hindering cross-embodiment transfer." (§B)
(한글 해설 — 액션만 통일해서는 부족하다는 진술입니다. 관측 쪽에서도 같은 기하 좌표계로 내려야 정책 입력의 의미가 손 사이에서 보존됩니다.)

**6. 액션 세부 규약 (§B).** driving plane 은 손끝마다 하나씩 붙이고 초기 방위각을 해당 손끝의 구면 $`\theta`$ 에 정렬합니다. 4 손가락 임베디먼트에는 약지 방위 위치에 평면을 하나 더 넣어 5 평면 구조를 맞추되, 약지 변형 계산 시 중복 평면의 $`\Delta\theta`$ / $`\Delta r`$ 을 평균한 뒤 보간합니다. lateral 액션은 손별 lookup table 의 극단값으로 제한되고, driving vector 는 평면당 2 개를 $`\phi=60^{\circ}`$ 와 $`\phi=120^{\circ}`$ 에 두며 반경 변위 구간은 $`[-2,2]`$ 입니다.

> "Prior to invoking the Cascade Inverse Kinematics (CIK) algorithm, we discard all sphere points whose radial coordinate $`r`$ is negative. If an encompassing joint has no reachable points remaining after this filtering step, the joint is commanded to its fully closed configuration." (§B)
(한글 해설 — 음의 반경을 허용한 것은 버그가 아니라 의도된 설계입니다. 구를 뒤집을 정도의 극단 변형을 "손가락 완전 폐쇄" 명령으로 해석하게 만들어, 격렬한 재배향 동작에서 손가락을 빠르게 접을 수 있도록 한 것입니다.)

### 학습 목표 / 손실

정책은 RSL-RL 의 PPO 구현으로 학습합니다. 보상은 NVIDIA Isaac Lab 의 기본 Reposing Cube 환경 정식화를 그대로 쓰되, 임베디먼트 특화 착취(예: lateral 관절만 과도하게 쓰고 encompassing 관절을 방치하는 정책)를 억제하기 위해 **관절 위치 정규화 항 두 개**를 추가합니다.

$$r=w_{d}\,d+w_{r}\,r_{\text{rot}}+w_{\text{lat}}\,p_{\text{lat}}+w_{\text{rad}}\,p_{\text{rad}}+b_{\text{success}}+p_{\text{fall}}$$

여기서 $`d`$ 는 물체-목표 거리, $`r_{\text{rot}}`$ 은 방향 정렬 보상, $`p_{\text{lat}}`$ 과 $`p_{\text{rad}}`$ 는 각각 lateral / encompassing 관절 위치가 기준 자세에서 벗어난 정도의 페널티입니다 (식 1). $`b_{\text{success}}`$ 는 0.1 radian 허용 오차 안으로 목표에 도달했을 때 주는 큰 양의 보너스, $`p_{\text{fall}}`$ 은 물체 낙하 시의 음의 페널티입니다.

> "To discourage embodiment-specific exploitation—such as policies that rely predominantly on lateral joint motion while underutilizing encompassing joints—we augment the original reward with two additional regularization terms." (§B.1)
(한글 해설 — 이 두 항은 성능 튜닝이 아니라 **cross-embodiment 일반화를 위한 정규화**입니다. 특정 손에만 있는 관절 자유도로 과제를 편법 해결하면 그 정책은 다른 손으로 옮겨가지 못하기 때문입니다. §F.1 의 Allegro→Shadow 실패가 정확히 이 실패 양상의 실증입니다.)

| 보상 항 (Table 7) | 스케일 |
|---|---|
| Object-to-goal distance ($`w_{d}`$) | $`-10.0`$ |
| Orientation alignment ($`w_{r}`$) | $`1.0`$ |
| Reach goal bonus ($`b_{\text{success}}`$) | $`250`$ |
| Fall penalty ($`p_{\text{fall}}`$) | $`-100`$ |
| Lateral joint position penalty ($`w_{\text{lat}}`$) | $`-0.016`$ |
| Encompassing joint position penalty ($`w_{\text{rad}}`$) | $`-0.004`$ |

### 학습 셋업

전 모델을 단일 NVIDIA A5000 GPU 에서, Isaac Sim 4.5.0 + PhysX 위의 커스텀 NVIDIA Isaac Lab Cube Reposing 환경으로 학습합니다. 정책·가치망은 은닉 차원 $`[512,512,256,128]`$ 의 경량 actor-critic 이고 활성함수는 ELU 입니다.

| PPO 하이퍼파라미터 (Table 6) | 값 |
|---|---|
| Num. steps per environment | 16 |
| Empirical normalization | True |
| Hidden layer dimensions | $`[512,512,256,128]`$ |
| Activation function | ELU |
| Initial action noise std. | $`1.0`$ |
| Learning rate | $`5.0\times 10^{-4}`$ (adaptive) |
| Clip parameter | $`0.2`$ |
| Entropy coefficient | $`0.005`$ |
| Num. learning epochs | $`5`$ |
| Num. mini-batches | $`4`$ |
| Value loss coefficient | $`1.0`$ (clipped value loss True) |
| Discount factor ($`\gamma`$) | $`0.99`$ |
| GAE parameter ($`\lambda`$) | $`0.95`$ |
| Desired KL divergence | $`0.016`$ |
| Max. gradient norm | $`1.0`$ |

도메인 랜덤화(DR)는 물체 속성(스케일 $`[0.9,1.1]\times`$, 질량 $`[0.8,1.2]\times`$, 정지 마찰 $`[0.2,0.3]`$, 운동 마찰 $`[0.15,0.25]`$), 로봇 속성(질량 $`[0.9,1.1]\times`$, 마찰 $`[0.75,1.0]`$, 관절 마찰 $`[0.9,1.1]\times`$, armature $`[1.00,1.05]\times`$, effort limit $`[0.9,1.1]\times`$, 강성·감쇠 $`[0.75,1.25]\times`$), 손 자세·액션 공간(손 기저 경사 $`15^{\circ}\pm 5^{\circ}`$, driving vector 각 $`\pm 15^{\circ}`$)에 걸칩니다. 손 기저 경사 랜덤화는 큐브가 손바닥 특정 영역으로 미끄러져 안착한다는 가정에 정책이 기대는 것을 막고, 물체 스케일 랜덤화는 손가락 형상 차이에서 오는 손가락 끼임(finger entrapment)을 완화한다고 설명합니다.

실환경 배포용 모델은 별도 처리를 추가합니다. LEAP 손의 시리얼 통신 대역폭 제약으로 **학습·배포 모두 20 Hz 제어 주파수**를 씁니다. 서보 제어 법칙은 $`\text{current}(t)=K_{p}\Delta\theta(t)-K_{d}\Delta\dot{\theta}(t)`$ 로 모델링했는데, 이를 시뮬레이터의 암시적 PD 토크 액추에이터에 그대로 옮기면 실제 움직임이 재현되지 않아 무작위 목표 위치를 명령하며 $`K_{p}`$ / $`K_{d}`$ 를 바꾸는 방식으로 시스템 식별을 수행했습니다.

> "The system identification revealed that the LEAP Hand motors behave as a nearly undamped system, with damping having a negligible effect on the observed dynamics." (§D)
(한글 해설 — 제조사 스펙과 실제 유효 게인이 달랐다는 보고이며, 유효 $`K_{p}`$ 는 모터 단위 100 당 약 $`0.0786~\text{Nm/rad}`$, 유효 $`K_{d}`$ 는 약 $`0.0014~\text{Nm/(rad/s)}`$ 로 식별됐습니다. 원인은 모터의 전류 기반 위치 제어 모드로 지목합니다.)

실환경 학습에는 DR 범위를 넓히고 속도 제한 자체도 랜덤화하며, **비대칭 actor-critic** 을 채택합니다 — actor 는 물체·관절의 위치 정보만, critic 은 물체·손의 선속도·각속도까지 포함한 전체 상태를 받습니다. 실세계 센싱·통신 잡음에 강한 위치 피드백 중심 정책을 유도하려는 설계입니다. 물체 포즈는 6 면에 각 4 개씩 총 24 개의 tag36h11 AprilTag 을 붙인 3D 프린트 큐브를 $`848\times 480`$ 해상도 60 Hz 적외선 스트림으로 추적해 추정하며, 최소 3 개 태그가 보일 때만 포즈를 발행합니다.

---

## 📊 실험 설정과 결과

### 과제와 지표

시뮬레이션은 NVIDIA Isaac Lab 의 Repose Cube 환경을 sphere controller 용으로 개조해 4 손가락 Leap · Allegro 와 5 손가락 Shadow · MANO 네 손에서 돌립니다. 에피소드마다 큐브의 목표 방향 10 개를 순차적으로 맞춰야 하고, 큐브가 떨어지면 환경을 리셋한 뒤 남은 시도를 이어갑니다. 실환경에서는 큐브가 떨어질 때까지 정책을 연속 실행합니다. 시뮬레이션·실환경 모두 목표 하나당 제한 시간은 30 초입니다.

지표는 두 가지입니다. Average Consecutive Reorientations 는 첫 낙하 전까지 연속 성공한 재배향 횟수의 평균(시뮬레이션 최대 10)이고, Success Rate 는 개별 재배향 시도의 성공 비율입니다. 시뮬레이션 결과는 전부 **1000 개 병렬 환경**에서 평가합니다. 베이스라인은 관절 위치·속도를 상태로 받아 관절 위치를 직접 예측하도록 학습한 정책입니다.

### 주요 결과 (Table 1)

| Test Hand | Single-Hand | Joint Control | Multi-Hand | Zero-shot |
|---|---|---|---|---|
| Allegro | 99.1 / 9.6 $`\pm`$ 1.7 | 98.5 / 9.2 $`\pm`$ 2.2 | 99.2 / 9.5 $`\pm`$ 1.9 | 95.3 / 7.7 $`\pm`$ 3.4 |
| LEAP | 99.7 / 9.8 $`\pm`$ 1.1 | 98.6 / 9.3 $`\pm`$ 1.2 | 99.1 / 9.5 $`\pm`$ 1.9 | 95.5 / 7.7 $`\pm`$ 3.5 |
| Shadow | 99.3 / 9.6 $`\pm`$ 1.6 | 98.0 / 9.1 $`\pm`$ 1.9 | 98.7 / 9.2 $`\pm`$ 2.3 | 85.7 / 4.4 $`\pm`$ 3.7 |
| MANO | 99.8 / 9.9 $`\pm`$ 1.0 | 99.6 / 9.8 $`\pm`$ 1.4 | 99.5 / 9.8 $`\pm`$ 1.2 | 98.1 / 8.9 $`\pm`$ 2.6 |

(Success Rate / Average Consecutive Reorientations. Single-Hand = 해당 손만으로 학습, Joint Control = 해당 손에서 학습한 관절 공간 베이스라인, Multi-Hand = 네 손 전체로 학습, Zero-shot = 대상 손을 제외하고 학습.)

> "The proposed UHAS representation achieves consistently strong performance across all hands and generally outperforms the joint-space baseline in both task success and long-horizon stability." (§4.2, Table 1)
(한글 해설 — 다만 격차 자체는 크지 않습니다. 성공률 기준 Allegro 99.1 vs 98.5, Shadow 99.3 vs 98.0 처럼 1 %p 안팎이며, 네 손 모두 이미 98 % 이상 포화 구간에 있습니다. 이 표의 진짜 정보는 "UHAS 가 관절 제어보다 강하다"보다 **"추상화 계층을 하나 끼워도 단일 손 성능을 잃지 않는다"** 는 쪽입니다.)

Multi-Hand 열은 손별 전용 정책과 사실상 동등한 수치를 보이며(예: Allegro 99.2 / 9.5 vs Single-Hand 99.1 / 9.6), 단일 공유 정책이 네 손을 동시에 다룰 수 있음을 뒷받침합니다. Zero-shot 열은 손마다 편차가 큽니다 — MANO 98.1 / 8.9 는 거의 손실이 없는 반면 Shadow 는 85.7 / 4.4 로 연속 재배향 횟수가 절반 이하로 떨어집니다.

### 형상 교차 일반화 (Table 2)

| Test Hand | Train: Shadow + MANO (5-finger) | Train: Allegro + LEAP (4-finger) |
|---|---|---|
| Allegro (4F) | 66.2 / 1.9 $`\pm`$ 1.9 | 99.7 / 9.8 $`\pm`$ 1.2 |
| LEAP (4F) | 80.8 / 3.7 $`\pm`$ 3.6 | 99.8 / 9.9 $`\pm`$ 0.98 |
| Shadow (5F) | 98.6 / 9.3 $`\pm`$ 2.1 | 83.2 / 4.0 $`\pm`$ 4.0 |
| MANO (5F) | 99.7 / 9.8 $`\pm`$ 1.3 | 95.0 / 7.6 $`\pm`$ 3.5 |

> "Although a performance gap remains compared to in-distribution performance, the transferred policies achieve substantial success on unseen hands, demonstrating that the proposed UHAS representation generalizes across different finger counts and kinematic structures." (§4.2, Table 2)
(한글 해설 — 손가락 개수를 건너뛰는 전이는 명백히 비용이 큽니다. 5→4 방향에서 Allegro 는 66.2 / 1.9 로 연속 재배향이 사실상 2 회 수준까지 붕괴합니다. "substantial success" 라는 표현은 성공률 기준이며, 장기 안정성 지표로 읽으면 in-distribution 대비 1/5 수준입니다. 두 지표를 함께 보게 만든 설계가 여기서 값을 합니다.)

### 미지 손 미세조정 (Table 3)

| Target Hand | Zero-shot | +500 Iter |
|---|---|---|
| Allegro | 95.3 / 7.7 $`\pm`$ 3.4 | 96.3 / 8.1 $`\pm`$ 3.3 |
| LEAP | 95.5 / 7.7 $`\pm`$ 3.5 | 96.2 / 8.0 $`\pm`$ 3.3 |
| Shadow | 85.7 / 4.4 $`\pm`$ 3.7 | 95.8 / 7.8 $`\pm`$ 3.5 |

> "Starting from a policy trained solely on MANO, we finetune the policy on each target hand for only 500 iterations, compared to approximately 4,500 iterations required for training from scratch." (§4.2, Table 3)
(한글 해설 — 약 9 분의 1 예산으로 zero-shot 격차를 상당 부분 메웁니다. 특히 zero-shot 이 가장 나빴던 Shadow 가 85.7 / 4.4 → 95.8 / 7.8 로 가장 크게 회복하는데, 이는 "표현은 이미 옮겨졌고 남은 것은 손별 미세 보정"이라는 해석을 지지하는 가장 강한 증거입니다. 다만 여전히 in-distribution 99.3 / 9.6 에는 못 미칩니다.)

### 어블레이션 — 평면당 driving vector 개수 (Table 4)

| # Driving Vectors | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Success Rate | 98.0 | 98.7 | 99.5 | 98.1 |
| # Reorientations | 8.8 $`\pm`$ 2.6 | 9.3 $`\pm`$ 2.0 | 9.6 $`\pm`$ 1.5 | 9.1 $`\pm`$ 2.4 |
| Training Time (h) | 5.3 | 4.5 | 6.5 | 5.5 |

이 어블레이션이 격리하는 것은 **반경 방향 액션의 표현력**입니다. 1 개는 손가락 하나의 굽힘 프로파일을 하나의 반경 변위로만 지시하므로 제어 유연성이 부족하고, 그 결과 성능도 낮으면서 학습 시간(5.3 h)은 오히려 2 개(4.5 h)보다 깁니다 — 즉 표현력 부족이 학습 난이도로 되돌아옵니다. 3 개는 최고 성능(99.5 / 9.6)이지만 학습 시간이 6.5 h 로 가장 길고, 4 개는 액션 공간 복잡도만 키우고 성능은 오히려 내려갑니다. 학습 시간은 "최대 평균 연속 재배향(10)의 90 % 도달에 필요한 반복 수"로 측정했습니다. 저자는 성능-시간 절충으로 2 개를 최종 채택합니다.

### 어블레이션 — 손가락당 관측점 개수 (Table 9, §E)

| # Observation Points | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Success Rate | 98.8 | 98.7 | 99.0 | 99.1 |
| # Reorientations | 9.3 $`\pm`$ 2.1 | 9.3 $`\pm`$ 2.0 | 9.4 $`\pm`$ 1.8 | 9.5 $`\pm`$ 1.8 |
| Training Time (h) | 4.9 | 4.5 | 4.8 | 4.7 |

관측 밀도를 격리한 어블레이션인데, 1 → 4 로 늘려도 성공률은 98.7~99.1 사이에서 거의 움직이지 않습니다. 저자는 DR 을 적용하면 이 이득이 무시할 수준이 되면서 학습·추론 비용만 늘어난다고 보고 손끝 + 중간점 2 개를 채택합니다. **관측을 더 주는 것보다 액션 표현력이 병목**이었다는 뜻으로, Table 4 와 대비해 읽을 때 의미가 살아납니다.

### 어블레이션 — driving plane 개수 (Table 10, §E)

| # Driving Planes | 4 | 5 |
|---|---|---|
| Shadow | 99.5 / 9.7 $`\pm`$ 1.5 | 99.3 / 9.6 $`\pm`$ 1.6 |
| Shadow (Zero-shot) | 86.9 / 4.8 $`\pm`$ 3.8 | 85.7 / 4.4 $`\pm`$ 3.7 |
| MANO | 99.6 / 9.8 $`\pm`$ 1.3 | 99.8 / 9.9 $`\pm`$ 1.0 |
| MANO (Zero-shot) | 98.0 / 8.7 $`\pm`$ 2.9 | 98.1 / 8.9 $`\pm`$ 2.6 |

4 평면(약지·소지 평면 병합)과 5 평면이 사실상 동률이며 Shadow 는 오히려 4 평면이 근소 우위입니다. 저자는 큐브 재배향 과제에서 소지가 거의 쓰이지 않기 때문이라고 해석합니다. 3 평면은 아예 수렴하지 못했다고 보고하는데, 이는 **액션 공간 표현력에 하한이 존재**한다는 뜻입니다.

> "It is important to note that the small difference observed between 4 and 5 planes may be specific to this reposing task, the particular reward formulation and the reference cube position used." (§E)
(한글 해설 — 저자 스스로 이 어블레이션의 외적 타당성을 제한합니다. 평면 개수의 적정값이 과제·보상 설계에 종속된다는 뜻이므로, 다른 과제로 옮길 때 이 결론을 그대로 들고 가면 안 됩니다.)

### 어블레이션 — 도메인 랜덤화 (Table 11, §E)

| Test Hand | Without Randomization | With Randomization |
|---|---|---|
| Allegro | 96.7 / 8.2 $`\pm`$ 3.1 | 95.3 / 7.7 $`\pm`$ 3.4 |
| LEAP | 95.3 / 7.6 $`\pm`$ 3.4 | 95.5 / 7.7 $`\pm`$ 3.5 |
| Shadow | 80.1 / 3.6 $`\pm`$ 3.6 | 85.7 / 4.4 $`\pm`$ 3.7 |
| MANO | 97.1 / 8.4 $`\pm`$ 2.9 | 98.1 / 8.9 $`\pm`$ 2.6 |

> "Randomization during training consistently improves zero-shot transfer, particularly for hands with larger morphological differences from the training set." (§E)
(한글 해설 — 표를 그대로 읽으면 "consistently" 는 과합니다. Allegro 는 랜덤화 없는 쪽이 96.7 / 8.2 로 더 낫고 LEAP 은 사실상 동률입니다. 실제 이득은 Shadow(80.1 → 85.7)에 집중되어 있어, 정확한 진술은 "학습 분포에서 형상 차이가 큰 손에서만 효과가 나타난다" 입니다.)

### 일대다 zero-shot 일반화 (Table 12, §F.1)

| Source \ Target | Allegro | LEAP | Shadow | MANO |
|---|---|---|---|---|
| Allegro | 99.1 / 9.6 $`\pm`$ 1.7 | 55.4 / 1.1 $`\pm`$ 1.5 | 8.7 / 0.1 $`\pm`$ 0.3 | 17.5 / 0.0 $`\pm`$ 0.13 |
| LEAP | 95.3 / 7.8 $`\pm`$ 3.3 | 99.7 / 9.8 $`\pm`$ 1.1 | 65.8 / 1.8 $`\pm`$ 1.9 | 87.0 / 4.7 $`\pm`$ 3.7 |
| Shadow | 35.6 / 0.4 $`\pm`$ 0.7 | 59.4 / 1.6 $`\pm`$ 2.2 | 99.3 / 9.6 $`\pm`$ 1.6 | 97.6 / 8.7 $`\pm`$ 2.7 |
| MANO | 33.0 / 0.4 $`\pm`$ 0.68 | 31.0 / 0.4 $`\pm`$ 0.67 | 36.2 / 0.5 $`\pm`$ 0.9 | 99.8 / 9.9 $`\pm`$ 1.0 |

이 표는 본문 Table 1 의 zero-shot 열(세 손으로 학습)이 실제로는 **다중 소스 학습 덕분**임을 드러냅니다. 단일 소스만 쓰면 전이가 무너집니다 — Allegro → Shadow 는 8.7 / 0.1, MANO → LEAP 은 31.0 / 0.4 로 사실상 실패입니다.

> "For example, the Allegro-trained policy relies heavily on the hand’s distinctive lateral joints to perform cube rotations. Because Shadow and MANO lack equivalent lateral actuation, this policy fails almost completely on those hands." (§F.1)
(한글 해설 — §B.1 의 lateral / encompassing 페널티 항이 왜 필요했는지를 정확히 설명하는 실패 사례입니다. 액션 공간이 통일되어 있어도 정책은 특정 손에만 있는 자유도를 착취할 수 있고, 그 순간 표현의 공유성은 무의미해집니다.)

저자는 가동범위와 작업 공간이 넓은 손일수록 소스로서 더 잘 일반화한다고 정리합니다. LEAP 이 네 손 중 가동범위가 가장 넓어 소스로서 최고 성능을 내며, Shadow → MANO(97.6 / 8.7)와 MANO → Shadow(36.2 / 0.5)의 비대칭은 손가락 수가 같아도 기구학적 유연성이 전이 방향을 결정함을 보입니다.

### 실환경 결과 (Table 5, Table 13)

| Method (LEAP Hand, 10 trials) | MEAN |
|---|---|
| Baseline (Joint Control) | 0.6 |
| UHAS (Zero-Shot) | 0.9 |
| UHAS (Trained on Multi-Hand) | 1.1 |
| UHAS (Trained on LEAP Hand) | 2.0 |

| Method (Allegro Hand, 10 trials) | MEAN |
|---|---|
| UHAS (Zero-Shot) | 0.8 |
| UHAS (Trained on Multi-Hand) | 2.1 |
| UHAS (Trained on Allegro Hand) | 2.1 |

> "We observe a significant performance gap between simulation and the real world despite our efforts on system identification and domain randomization." (§4.3)
(한글 해설 — 시뮬레이션 9.5~9.9 회 vs 실환경 최고 2.0~2.1 회로, 4~5 배 격차입니다. 저자가 이를 먼저 인정하고 시작한다는 점은 신뢰할 만하지만, 이 논문의 실환경 증거는 "관절 베이스라인보다 낫다"(0.6 → 2.0) 수준이지 "실용적 다지 조작을 달성했다"가 아닙니다.)

LEAP 실험에서 흥미로운 역전이 나타납니다 — 다중 손 학습 모델(1.1)이 단일 LEAP 학습 모델(2.0)보다 낮습니다.

> "We attribute this to the fact that single-hand training allows the policy to exploit the specific workspace and kinematics of the LEAP Hand, whereas multi-hand training forces the network to learn only movements that are feasible and safe across all hands." (§4.3)
(한글 해설 — cross-embodiment 일반성과 임베디먼트별 최고 성능이 정면으로 상충한다는 진술입니다. 다중 손 학습은 모든 손에서 안전한 움직임만 남기므로 정책이 보수적으로 수렴하며, 저자는 경량 actor-critic 구조가 이 보수성을 키웠다고 봅니다. Allegro 실험(Table 13)에서는 다중 손과 단일 손이 2.1 로 동률이라 이 역전이 손별로 일관되지는 않습니다.)

### 본문 표기 관련 메모

본문 §4.2 의 "Cross-Morphology Generalization" 과 "Finetuning on Unseen Hands" 두 문단이 **모두 `Table 3` 을 인용**하지만, 캡션 기준으로 전자는 Table 2, 후자가 Table 3 입니다. 위 표들은 캡션 번호를 기준으로 정리했습니다. 원문 수치는 변형 없이 그대로 옮겼습니다.

---

## ⚖️ 한계

- **(저자 명시) 저수준 PD 파라미터 민감성** — 저자는 다지 조작 성능이 저수준 PD 제어기 파라미터에 매우 민감해 손 사이 강건한 전이를 위해 광범위한 DR 이 필요하다고 밝힙니다. 이는 UHAS 의 추상화가 **기구학 수준에서만 임베디먼트를 통일**하고 동역학·액추에이터 수준은 전혀 통일하지 못한다는 뜻입니다. 구 좌표계는 "손가락 끝을 어디에 둘지"를 공유할 뿐, 그 자세를 만들어 내는 토크 응답은 손마다 다른 채로 남습니다.
- **(저자 명시) 보상·RL 하이퍼파라미터 민감성** — 큐브 재배향 과제가 보상 설계와 RL 하이퍼파라미터에 민감하다고 인정합니다. §E 의 평면 개수 결론이 과제·보상·기준 큐브 위치에 종속된다는 단서와 합치면, 이 논문의 어블레이션 결론 상당수는 **이 과제 안에서만 유효**하다고 읽는 편이 안전합니다.
- **(저자 명시) 형상 차이가 큰 전이에서의 성능 저하** — 4 손가락 ↔ 5 손가락처럼 형상이 크게 다르면 성능이 떨어진다고 밝히며, Table 2 의 66.2 / 1.9 가 그 실증입니다. 4 손가락 손의 약지 평면 복제라는 해법은 손가락 *개수*만 맞출 뿐 **형상 차이 자체를 흡수하지 못하는 자리 채우기**에 가깝습니다.
- **(추론) 액션 공간이 표현할 수 있는 조작의 범위가 미검증** — 구 변형은 $`(\Delta\theta,\Delta r)`$ 두 성분만 쓰고 극각 $`\phi`$ 변형은 북극이 손바닥에 고정되어 있다는 이유로 제외됩니다. 큐브를 손바닥 위에서 굴리는 과제에서는 타당하지만, 정밀 집기(pinch)나 도구 손잡이 조작처럼 손가락이 구 표면을 벗어난 배치를 요구하는 동작은 이 매개화 안에 표현이 없습니다. 논문 전체가 **단일 과제(큐브 재배향)로만 검증**되어 이 경계가 어디인지 알 수 없습니다.
- **(추론) CIK 는 학습 경로가 아니라 고정 디코더** — lookup table 조회 + 순차 대수 해로 구성되어 있어 정책에서 관절까지 gradient 가 흐르지 않습니다. RL 에서는 문제되지 않지만, 액션 청크를 예측하는 모방 학습·flow matching 계열 정책에 얹으려면 손실이 관절 공간에 정의될 수 없다는 제약이 생깁니다.
- **(추론) 베이스라인이 하나뿐** — 비교군은 "관절 위치를 직접 예측하는 정책" 단 하나입니다. 인용된 cross-embodiment 표현(CrossFormer, Universal Actions, One Hand to Rule Them All)이나 정규화 관절 공간(retargeting 계열) 같은 **대안 통일 표현과의 직접 비교가 없어**, "구가 최선의 통일 좌표계인가"는 검증되지 않은 채 남습니다.
- **(추론) 실환경 증거의 얕은 깊이** — 손당 10 회 시행, 지표는 첫 낙하 전 연속 성공 횟수 하나뿐이고 시행 간 분산이 큽니다(Allegro 다중 손 모델은 8 회와 0 회가 공존). 표본 크기와 분산을 감안하면 실환경 평균값 사이 1.1 vs 2.0 같은 차이는 통계적 결론으로 삼기 어렵습니다.
- **(추론) 표기 일관성** — §2 Related Work 는 같은 약어를 "Universal Hand Action Space (UHAS)" 로 두 차례 쓰는 반면 제목·초록·§3 은 "Unified Hand Action Space" 입니다. 또 DR 설명(§B.1)은 랜덤화 대상을 "driving vector azimuthal angle $`\theta`$", Table 8 은 "Driving vector azimuthal angle ($`\phi`$)", §E 는 "driving vector polar angle $`\phi`$" 로 적어 **각도 기호와 명칭이 세 곳에서 서로 어긋납니다**. §3.2 정의($`\theta`$ = 방위각, $`\phi`$ = 극각)를 기준 삼으면 어느 각을 랜덤화했는지 원문만으로는 확정할 수 없습니다.

---

## ♻️ 재현성

- **코드 / 데이터 / 영상** — 각주 1 에 `Data, code, and videos for the project are available at https://irvlutd.github.io/UHAS/` 로 프로젝트 페이지가 명시되어 있습니다. 본 분석 실행 환경의 네트워크 정책상 해당 호스트에 도달하지 못해(프록시 403) 공개 범위·라이선스는 직접 확인하지 못했습니다. 논문 본문에 GitHub / HuggingFace URL 은 별도로 제시되어 있지 않습니다.
- **하드웨어 산출물** — LEAP 손의 검지·중지·약지 뿌리 관절을 추가 나사로 고정하는 보강 베이스와 엄지 뿌리 커스텀 부착물을 3D 프린트해 사용했고, 둘 다 논문과 함께 공개 예정이라고 밝힙니다(§D.2).
- **시뮬레이션 스택** — Isaac Sim 4.5.0 + PhysX, NVIDIA Isaac Lab 의 Cube Reposing 환경 개조판, RSL-RL PPO 구현. PPO 하이퍼파라미터(Table 6), 보상 스케일(Table 7), DR 범위(Table 8)가 전부 표로 제시되어 재현 가능한 수준입니다.
- **연산 자원** — 전 모델이 단일 NVIDIA A5000 GPU 로 학습되며 학습 시간은 4.5~6.5 시간대(어블레이션 기준)입니다. 밑바닥 학습은 약 4,500 iteration, 미세조정은 500 iteration 입니다. 대규모 클러스터가 필요 없다는 점에서 재현 장벽이 낮습니다.
- **미공개 세부** — 손별 lookup table 의 샘플링 간격, 구 표면 균일 샘플링 점 개수, 관절 분류 시 "부분 굴곡" 각도, 보간 커널의 구체 형태는 본문에 수치가 없습니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

본 논문은 PROBE 의 **P1(Heterogeneous Body/Hand Action Expert)** 에 1 차로, **P3(Hand-level System0 Module, RL-scoped)** 와 **P2(Structured Multimodal Observation Fusion)** 에 2 차로 닿습니다.

- **P1 / D3(Hand output space)** — D3 의 v1 은 `(i) finger joint command` 입니다. 본 논문은 손 출력 공간을 관절 명령이 아니라 **임베디먼트 무관 기하 좌표(15 차원 구 변형)** 로 두고, 관절 명령은 CIK 라는 결정론적 디코더가 만들어 내는 구조를 제시합니다. 즉 D3 의 대안 축을 하나 새로 여는 논문이며, "손 출력 = 관절 명령"이라는 v1 선택을 정면으로 반박하지는 않되 **손 하드웨어 교체 시의 비용**이라는 새 평가 기준을 들고 옵니다.
- **P1 / D2(Body output space)** — 직접 대상은 아니지만 논리 구조가 같습니다. D2 가 팔에서 "관절 공간 vs 태스크 공간"을 고른 것과 마찬가지로, UHAS 는 손에서 "관절 공간 vs 기하 공간"을 고르는 문제입니다. P1 §5 의 methodology base 인 Demystifying Action Space Design(arXiv:2602.23408)이 팔에 대해 제공한 증거의 손 버전에 해당합니다.
- **P1 / D5(입력 모달리티 + 제어율 분리)** — 부분적으로만 닿습니다. 정책은 20 Hz, CIK 는 최대 150 Hz 로 동작하지만 CIK 는 학습되지 않는 고정 디코더이므로 D5 가 뜻하는 *학습된* 계층 간 제어율 분리와는 다릅니다. 이 구분은 명확히 해 둘 필요가 있습니다.
- **P3 / D17(System0 RL 정책 스펙)·D18(System0 Sim2Real)·D13(System0 역할)** — 과제 자체가 `MASTER.md` §3.5 Phase 1 의 "in-hand cube rotation" 과 동일하고, 스택도 Isaac Lab + PPO 로 D17 v1 과 같습니다. 보상 항 구성(Table 7), PPO 설정(Table 6), DR 범위(Table 8), 실환경용 비대칭 actor-critic, 시스템 식별 절차는 모두 D17·D18 의 직접 참고값입니다. 다만 본 논문의 RL 은 System0 급 안정화 하위 루프가 아니라 **과제 전체 학습기**입니다.
- **P2 / D12(topology-aware encoding + hand-level aggregation)** — homogeneous observation 은 D12 v1 의 "손가락/손 정체성, 손바닥 상대 손끝 자세, 기구학 체인"을 구 좌표계 하나로 구현한 구체 사례입니다. 손가락 체인을 7 점으로 이산화하고 부모 관절을 구 표면 대응으로 정하는 방식은 D11 의 "공통 토큰 형식" 논의와도 맞물리지만, **촉각·힘 모달리티가 전혀 없어** D10·D11 의 핵심(이종 모달리티 융합, per-finger 촉각 결합)은 건드리지 않습니다.
- **Identity 긴장/지지** — 논문은 강화학습을 과제 전체의 능력 원천으로 씁니다. 이는 Identity 의 Antagonist B("RL-as-core for generalized dexterity")에 정면으로 걸립니다. 다만 과제가 인핸드 큐브 재배향이라는 reward-engineerable 영역이라 P3 의 정당화 범위 안에 있고, 무엇보다 **UHAS 라는 액션 표현 자체는 학습 알고리즘과 독립**이라 Identity 의 VLA-level 주장과 충돌하지 않고 흡수될 수 있습니다. 표현은 가져오되 "RL 이 과제를 학습한다"는 프레이밍은 채택 대상이 아닙니다.
- **하드웨어 관점의 직접 지지** — `MASTER.md` §4.1 은 근시일 Sharpa Hand(22-DOF), 중기(2H 2026+) **사내 커스텀 손(스펙 TBD)** 을 명시하고 "Sharpa 특화 락인 회피"를 설계 제약으로 둡니다. 손 액션 공간이 하드웨어 교체를 견디는지가 실제 리스크이므로, 본 논문은 그 리스크에 대한 첫 번째 구체적 대응책입니다.
- **건드리지 않는 축** — VLM·언어·사전학습이 전혀 없어 **P4 는 무관**하고, 데이터셋·벤치마크 기여가 아니므로 **P0 도 무관**합니다(프로젝트 페이지 데이터 공개는 재현 자산이지 corpus 기여가 아닙니다). 예측 모델이 없어 **P5 도 무관**합니다.

---

## ✨ 핀 논문 대비 델타

- **Demystifying Action Space Design(arXiv:2602.23408) 대비 (P1 D2 evidence)** — 이 논문은 13k+ 실 rollout 으로 관절 공간(안정성) vs 태스크 공간(일반화)의 절충을 재고, **하나의 로봇 안에서** 좌표계를 고르는 문제를 다룹니다. UHAS 의 진짜 델타는 좌표계를 바꾼 것이 아니라 **좌표계를 임베디먼트 사이에 공유 가능하게 만든 것**입니다. 관절 공간이든 태스크 공간이든 손이 바뀌면 다시 정의되지만, 정규 구는 URDF 로부터 자동 재구성되어 같은 15 차원 의미를 유지합니다.
- **Dexora(arXiv:2605.18722) 대비 (P1 핀)** — Dexora 는 오픈소스 고 DoF 양팔 VLA 로 Body/Hand 액션 공간의 참조점을 제공하지만, 손 출력은 여전히 그 하드웨어의 관절 명령입니다. UHAS 의 델타는 **손 출력 공간 자체의 이식성**이며, Dexora 의 손 헤드 출력을 구 변형으로 바꾸는 것은 원리적으로 직교하는 변경입니다.
- **DQ-RISE(arXiv:2605.03363) 대비 (P1 methodology base)** — 팔-손 액션 공간 분리라는 문제의식은 공유하지만 분리는 *한 임베디먼트 안에서*의 분리입니다. UHAS 는 분리가 아니라 통합 축(임베디먼트 간)을 다루므로 두 논문은 경쟁이 아니라 조합 관계입니다.
- **HORA(arXiv:2210.04887) 대비 (P3 핀)** — 과제(인핸드 재배향), 스택(Isaac + PPO + DR), 지표 구성이 거의 같습니다. HORA 의 델타 축은 특권 정보 → 고유수용감각 distillation 과 RMA 기반 적응이고, UHAS 는 **distillation·teacher-student 를 전혀 쓰지 않습니다**. UHAS 의 델타는 학습 알고리즘이 아니라 액션·관측 좌표계이며, 두 델타는 서로 겹치지 않아 **결합 가능**합니다(구 좌표계 위에서 RMA 를 돌리는 구성).
- **Beyond Binary(arXiv:2605.28812) 대비 (P3 핀)** — Beyond Binary 는 *관측* 쪽을 물리 기반 표현(CoP)으로 정렬해 Sim2Real 을 얻습니다. UHAS 는 *액션* 쪽을 기하 표현으로 정렬해 cross-embodiment 를 얻습니다. 정렬이라는 전략은 같고 적용 축이 반대라, 두 논문을 합치면 "관측·액션 양쪽이 하드웨어 무관"이라는 구성이 나옵니다 — PROBE 관점에서 가장 흥미로운 조합입니다.
- **π0(arXiv:2410.24164) 대비 (P1 backbone)** — 비교 대상이 아닙니다. UHAS 에는 VLM·언어·flow matching 이 없고 정책은 은닉 $`[512,512,256,128]`$ MLP actor-critic 입니다. 다만 π0 계열 액션 전문가의 **출력 공간**을 구 변형으로 바꾸는 시나리오는 P1 D3 의 열린 선택지로 남습니다.
- **종합** — 핀 대비 단일 최대 델타는 "**손 하드웨어가 바뀌어도 재정의되지 않는 액션 좌표계를 URDF 만으로 자동 구성하고, 학습 없는 경량 IK 로 되돌린다**" 입니다. 반대로 델타가 *아닌* 것도 분명합니다 — RL 알고리즘, 과제, 보상, DR, Sim2Real 절차는 모두 P3 핀들이 이미 확립한 관행의 재사용입니다.

---

## ⚙️ 의사결정 함의

- **D3(Hand output space) — 손 출력 공간에 어댑터 계층 도입 검토** — 현재 v1 은 HandExpert 가 손가락 관절 명령을 직접 냅니다. 본 논문이 맞다면 `hand_action_space ∈ {joint, sphere_deformation}` 형태의 스위치를 두고, `sphere_deformation` 일 때 HandExpert 출력 차원을 손 DOF(Sharpa 22)에서 **고정 15**(driving plane 5 × $`\Delta\theta`$ + driving vector 10 × $`\Delta r`$)로 바꾼 뒤 CIK 를 후단 디코더로 붙이는 구성이 가능합니다. 판단 기준은 성능이 아니라 **하드웨어 교체 시 재학습 비용**입니다.
- **D3 판단을 위해 실제로 측정해야 할 값** — "Sharpa 22-DOF 궤적을 UHAS 로 투영했다가 CIK 로 복원했을 때의 관절 공간 재구성 오차". 이 값이 크면 15 차원 병목이 우리 손의 표현력을 깎는다는 뜻이고, 작으면 어댑터 도입 비용이 사실상 없다는 뜻입니다. 이 한 숫자가 D3 대안 채택 여부를 가릅니다.
- **D12(topology-aware encoding) — 관측 토큰의 좌표 기준 후보** — D12 v1 의 "손바닥 상대 손끝 자세" 를 구체화할 후보로, 손가락 체인 등간격 점 중 **중간점 + 손끝 2 점의 위치·속도를 정규 구 좌표계로 표현하고 반지름 $`r`$ 로 정규화**하는 방식을 등록할 수 있습니다. §E 어블레이션은 손가락당 관측점을 4 개까지 늘려도 이득이 미미하다고 보고하므로(98.8 → 99.1), 토큰 수를 늘리는 방향에 비용을 쓰지 말라는 실증 근거이기도 합니다.
- **D11(proprio-tactile-force 토큰 구성) — 공통 토큰 형식의 주소 체계 후보** — D11 의 비협상 조건은 "Sharpa 락인 금지 + 접촉 관련 특징 보존"입니다. 구면좌표 $`(\theta,\phi)`$ 는 자세·손 형상에 무관한 라벨이므로, **촉각 토큰의 위치 주소를 taxel 인덱스가 아니라 $`(\theta,\phi)`$ 로 부여**하면 센서 헤드가 바뀌어도 토큰 형식이 유지됩니다. 본 논문은 촉각을 전혀 다루지 않으므로 이는 논문의 주장이 아니라 우리 쪽 파생 가설로 명시해 둡니다.
- **D17(System0 RL 정책 스펙) — 직접 복사 가능한 설정값** — 은닉 $`[512,512,256,128]`$ + ELU, lr $`5.0\times 10^{-4}`$ adaptive, desired KL $`0.016`$, clip $`0.2`$, entropy $`0.005`$, $`\gamma=0.99`$, $`\lambda=0.95`$, epochs 5, mini-batches 4, steps/env 16, empirical normalization True, 초기 action noise std $`1.0`$. Phase 1 인핸드 큐브 회전 데모의 초기 설정으로 그대로 쓸 수 있는 값들입니다.
- **D17 — 보상 항 추가 후보** — Isaac Lab 기본 보상 위에 **관절 그룹별 기준 자세 이탈 페널티**를 얹는 발상(lateral $`-0.016`$ / encompassing $`-0.004`$)은 우리 쪽에도 그대로 유효합니다. 목적은 성능이 아니라 정책이 특정 관절군만 착취하는 것을 막는 데 있으며, 손 교체를 전제하는 우리 로드맵에서는 필수에 가깝습니다.
- **D18(System0 Sim2Real) — 실환경 배포 구성** — actor 는 위치 정보만, critic 은 속도까지 받는 **비대칭 actor-critic**, 시뮬레이션 속도 제한 도입 및 그 제한값 자체의 랜덤화, 통신 대역폭에 맞춘 제어 주파수 고정(본 논문 20 Hz)은 D18 에 추가할 구체 항목입니다. 다만 Table 11 이 보이듯 DR 의 이득은 손 형상 차이가 클 때만 나타나므로, **DR 범위를 무조건 넓히는 것이 답이 아니라**는 점도 함께 기록해야 합니다.
- **평가 메트릭 — Phase 1 데모 지표 확정** — `MASTER.md` §3.5 Phase 1 의 "measurable falsifier" 를 **Success Rate + Average Consecutive Reorientations(최대 10, 목표당 30 초 제한, 1000 병렬 환경)** 2 개로 고정할 것을 제안합니다. 성공률만 보면 98~99 % 포화 구간에서 아무 정보가 없고, 연속 재배향 횟수가 실제 차이를 드러낸다는 것이 Table 1~2 의 반복된 교훈입니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 확인) Sharpa URDF 에서 구 자동 생성이 되는가** — §3.1 은 "손가락이 완전히 펴지고 손끝 법선이 손바닥 법선과 대략 정렬되는 열린 손 자세"를 전제로 손바닥 중심·손끝 프레임을 식별합니다. Sharpa 22-DOF 의 엄지가 강하게 대향(opposed)되어 있으면 이 전제가 깨져 구 중심·반지름이 엉뚱하게 잡힙니다. URDF 만 있으면 30 분 안에 확인 가능하며, 실패하면 나머지 모든 논의가 무의미해지므로 반드시 첫 번째입니다.
- **(두 번째) 관절 분류가 이분법으로 안정적인가** — CIK 는 모든 관절이 lateral 또는 encompassing 중 하나로 *지배적으로* 분류된다고 가정합니다. 논문조차 회전축이 손끝을 향하는 관절에는 "나머지를 부분 굴곡시킨 뒤 재측정"이라는 예외 절차를 둡니다. 22-DOF + 결합 축을 가진 손에서 분류가 자세 의존적으로 흔들리면 lookup table 과 cascade 가 동시에 무효가 됩니다. 검증: 각 관절을 전 가동범위로 훑으며 $`(\theta,\phi,r)`$ 변화량 비율을 기록하고, 지배 비율이 애매한 관절 개수를 셉니다.
- **(세 번째) 15 차원 병목이 우리 과제 범위를 자르는가** — 구 변형은 $`\Delta\theta`$ / $`\Delta r`$ 만 쓰고 극각 변형은 제외합니다. Phase 1 큐브 회전에서는 문제없겠지만 **Phase 2 도구 관절 조작(태깅 머신·트리거 도구)** 은 손가락이 도구 손잡이를 감싸고 한두 손가락만 독립적으로 트리거를 당기는, 구 표면 변형으로 표현하기 어려운 동작입니다. 검증: 기록된 도구 조작 궤적을 UHAS 로 투영→CIK 복원했을 때의 관절 오차를 측정합니다. 오차가 크면 UHAS 는 Phase 1 전용 도구로 범위를 좁혀야 합니다.
- **(네 번째) 촉각이 들어갈 자리가 없다** — UHAS 관측은 순수 기하량(위치·속도)이며 촉각·힘 채널이 전혀 없습니다. P2 의 per-finger 촉각 결합과 P3 의 System0 입력(D15: 촉각 + 관절 위치·속도·토크)이 이 좌표계 위에서 성립하는지는 논문이 답하지 않습니다. 검증: Deform Map 접촉점을 구면좌표 $`(\theta,\phi)`$ 로 사상할 수 있는지 오프라인 확인. 불가하면 UHAS 는 액션 쪽에만 쓰고 관측 쪽은 별도 좌표계를 유지해야 합니다.
- **(다섯 번째) 학습 불가능한 디코더와 flow matching 의 충돌** — CIK 는 lookup table + 대수 해로 gradient 가 흐르지 않습니다. D23 의 v1 은 연속 flow-matching 헤드이고 액션 청크를 예측하는데, 손실을 구 변형 공간에 정의하면 관절 공간 오차를 직접 최적화할 수 없고, 관절 공간에 정의하면 CIK 를 통과할 수 없습니다. 논문의 검증은 전부 RL(액션 공간이 곧 최적화 대상) 환경이라 **모방 학습 경로의 증거가 0** 입니다. 검증: 소량 데모로 구 변형 타깃을 지도 학습해 재구성 오차를 먼저 봅니다.
- **(여섯 번째) 다중 임베디먼트 학습의 보수화** — 실환경 LEAP 에서 다중 손 정책(1.1)이 단일 손 정책(2.0)보다 나빴습니다. 우리 로드맵은 "지금 Sharpa, 나중에 사내 손"이라 동시에 여러 손을 다룰 필요가 없으므로, UHAS 의 값어치는 동시 일반화가 아니라 **교체 시점의 500 iteration 급속 적응**에 있습니다. 이 구분을 흐리면 손해만 보는 채택이 됩니다.
- **(일곱 번째) 실환경 성능 절대치의 낮음을 과제 난이도로 오독하지 말 것** — 최고 성능이 평균 2.0~2.1 회 연속 재배향입니다. 이 숫자를 우리 Phase 1 목표선으로 잡으면 목표가 지나치게 낮아지고, 반대로 시뮬레이션 9.8 을 목표로 잡으면 도달 불가능합니다. 자체 베이스라인(관절 공간 정책)을 같은 하드웨어에서 먼저 재고 상대 비교로 판단해야 합니다.
- **(여덟 번째) 동역학 수준의 미통일** — 저자 스스로 PD 파라미터 민감성을 한계로 듭니다. 구 좌표계는 기구학만 통일하므로, Sharpa → 사내 손 전환에서 액추에이터 특성이 크게 달라지면 액션 공간이 같아도 정책은 전이되지 않습니다. 검증: 손 교체 시나리오를 시뮬레이션에서 PD 게인만 크게 바꿔 모사하고 zero-shot 성능 저하를 먼저 측정합니다.

---

## 💡 컨텍스트 제안

- **P1 / D3 deferred 대안 등록 제안** — D3 v1(`(i) finger joint command`)을 유지하되, "임베디먼트 무관 기하 액션 공간(구 변형) + 학습 없는 IK 디코더" 를 *deferred 대안*으로 기록할 것을 제안합니다. 트리거 예시: "사내 커스텀 손 스펙이 확정되어(`MASTER.md` §4.1 중기 항목) 손 교체가 실제 일정에 오를 때" 또는 "Sharpa 궤적의 UHAS 투영-복원 관절 오차가 허용치 이내로 확인될 때".
- **P1 §5 methodology base 추가 후보** — 본 논문(arXiv:2607.03570)을 P1 의 **methodology base(비핀)** 로 추가할 것을 제안합니다. Demystifying Action Space Design 이 팔 액션 공간 증거를 맡는 자리에 대응해, 손 액션 공간의 cross-embodiment 축 증거를 맡는 위치입니다. 핀 승격은 권하지 않습니다 — VLA 도 Body/Hand 분할도 없어 P1 의 north star 와 거리가 있습니다(P1 핀은 4/8 로 여유가 있으나 그 여유는 VLA-level 후보에 남겨 두는 편이 낫습니다).
- **P2 / D11 공통 토큰 형식 논의에 좌표 후보 추가 제안** — 구면좌표 $`(\theta,\phi)`$ 를 촉각 토큰의 하드웨어 무관 주소 체계 후보로 D11 논의에 연결할 것을 제안합니다. 다만 본 논문은 촉각을 다루지 않으므로 **논문의 주장이 아닌 파생 가설**로 표기해야 합니다.
- **P3 / D17 참고값 등록 제안** — 관절 그룹별 기준 자세 이탈 페널티(lateral $`-0.016`$ / encompassing $`-0.004`$)를 D17 보상 항 후보로, Table 6 PPO 설정을 Phase 1 초기값으로 기록할 것을 제안합니다. P3 핀 교체는 권하지 않습니다 — HORA·Beyond Binary·A-RMA·VE2VF 가 각각 다른 축을 맡고 있고, 본 논문은 그중 어느 축도 대체하지 않습니다.
- **`MASTER.md` §3.5 Phase 1 지표 확정 제안** — Phase 1 의 measurable falsifier 를 Success Rate + Average Consecutive Reorientations 2 지표(최대 10, 목표당 30 초, 1000 병렬 환경)로 명시할 것을 제안합니다. 현재 문구는 "measurable falsifier" 로만 되어 있어 지표가 특정되지 않았습니다.
- 그 외 신규 컨텍스트 변경 제안: 없음. `context/` 파일은 수정하지 않았습니다.

> 💡 base 매핑은 `/implement-design analysis/2607.03570/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
