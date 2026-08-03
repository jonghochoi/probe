# Paper Analysis — Play2Perfect: What Matters in Dexterous Play Pretraining for Precise Assembly?

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Play2Perfect: What Matters in Dexterous Play Pretraining for Precise Assembly? |
| 저자 | Tyler Ga Wei Lum, Kushal Kedia, C. Karen Liu, Jeannette Bohg (Stanford University · Cornell University) |
| 링크 | [arXiv:2606.26428](https://arxiv.org/abs/2606.26428) · [Website](https://play2perfect.github.io) |
| 발행일 / 버전 | 2026-06-24 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-07-01 |
| 관련 Pillar | P3, P4, P0, P1 |
| 태그 | dexterity, sim2real |

---

## 🧭 한 줄 요약 (TL;DR)

정밀 조립(precise assembly)이라는 sparse-reward·contact-rich 문제를 곧바로 RL 로 풀지 않고, "먼저 노는 법을 배운다(learn to play)" — 절차적으로 생성한 다양한 물체를 무작위 6D 목표 포즈로 조작하는 task-agnostic play 정책을 RL 로 사전학습한 뒤, CAD 로부터 유도한 sparse 보상으로 조립에 미세조정하는 2단계 프레임워크입니다. play prior 덕분에 dense·multi-stage 보상을 받은 scratch RL 대비 33× 샘플 효율을 얻고, 0.5 mm clearance 삽입에서 60 %, 장기·다부품 조립·나사조임에서 50 % 이상의 zero-shot sim-to-real 성공률을 달성합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 다지 손(multi-fingered hand)으로 정밀 조립(삽입·나사조임)을 원격조종(teleoperation) 없이 학습하는 것입니다. 조립은 최종 부품 포즈로만 정의되는 sparse-reward 문제라 무작위 정책에서 시작하면 보상을 받기 전에 grasp·in-hand 재정렬·정렬·삽입을 스스로 발견해야 합니다.
- **기존 접근의 한계** — 지금까지의 진전은 문제에 구조를 덧대어 이뤄졌습니다. 전용 그리퍼·툴 부착물·환경 고정구(fixture)로 grasp/삽입을 단순화하거나, dense 보상 shaping·스크립트 다단계 컨트롤러에 의존합니다. 모두 조립마다 하드웨어/환경/보상 엔지니어링이 필요하고, 병렬-죠 그리퍼 의존은 손의 속도·민첩성을 포기합니다.
- **본 논문의 가설** — 어려운 정밀 조립을 완성하기 전에 로봇은 먼저 *자유 공간에서 물체를 가지고 노는* 쉬운 문제를 배워야 하며, play 사전학습이 재사용 가능한 조작 prior(grasp, in-hand 재정렬, 포즈 도달)를 심는다는 것입니다. 핵심 takeaway 는 "play 는 고정 grasp 로의 팔 이동이 아니라 *손가락을 써 in-hand manipulation 을 강제할 때* 가장 잘 전이된다"입니다.
- **왜 지금 중요한가** — 이 논문은 22-DoF Sharpa 다지 손 + 7-DoF KUKA iiwa 14 팔이라는, PROBE 의 근시일 하드웨어와 *정확히 같은 손*으로 sim-to-real dexterous contact-rich RL 을 실증합니다. RL 을 어디에·어떻게 쓸지는 우리 Identity 의 핵심 논쟁점이며, 본 논문은 "RL 을 capability source 로 쓴" 강력한 반례이자 sim2real 레시피의 참조점입니다.

---

## 🧩 핵심 기여

- **Play2Perfect 프레임워크** — 일반 물체·목표에서 task-agnostic play prior 를 RL 로 학습한 뒤, 새 CAD-정의 조립 task 로 그 prior 를 sparse-reward RL 로 "완성(perfect)"하는 2단계 파이프라인. 원격조종·시연 없이 동작합니다.
- **play 사전학습 설계 인자의 체계적 연구** — 조립으로 전이되는 play 의 네 가지 설계 선택(object diversity, training objective, trajectory diversity, goal precision)을 하나씩 절제(ablation)하여, 무엇이 downstream contact-rich 조립에 유효한지 규명합니다.
- **33× 샘플 효율** — Fixtured 삽입에서 dense·multi-stage 보상의 scratch 는 near-perfect 까지 100 시간 이상 걸리는 데 비해, Play2Perfect 는 같은 성공률을 4 시간에 도달합니다.
- **6D in-hand 제어가 전이의 핵심** — Translation-only play 는 grasp·lift 만 배워 조립에 실패하고, rotation-only 는 잘 전이되나 full 6D 보다 느립니다. 정밀 목표(1 cm)와 online 무작위 궤적이 tight-clearance 조립에 가장 잘 맞는 prior 를 만듭니다.
- **zero-shot sim-to-real** — FoundationPose 기반 CAD 포즈 추적만으로, 0.5 mm clearance 삽입 60 %, 다부품 beam 조립·나사조임 50 % 이상을 실세계에서 미세조정 없이 달성합니다.

---

## 🔑 기술 키워드

- **Play pretraining** — 특정 task 없이 다양한 물체를 무작위 목표 포즈로 조작하며 재사용 가능한 조작 prior 를 얻는 사전학습. 사람 아이가 조립 전에 블록을 이리저리 만지며 손 감각을 기르는 것에 대응합니다.
- **Precise / contact-rich assembly** — 부품을 tight-clearance 로 삽입·나사조임하는, 접촉이 지배하는 정밀 조작. 본 논문의 downstream target.
- **Sparse reward** — 최종 조립 포즈에 도달했을 때만 보상이 주어지는 설정. 무작위 정책에서 탐색이 사실상 불가능한 근본 난점.
- **Goal-conditioned RL** — 현재/목표 물체 포즈를 입력으로 받아 목표 도달을 학습하는 강화학습. play 를 목표 포즈 시퀀스 도달 문제로 정식화합니다.
- **In-hand reorientation** — 물체를 손 안에서 손가락으로 재배향하는 능력. 고정 grasp 로 팔만 움직이는 것과 대비되는, 전이의 핵심 skill.
- **6D pose reaching** — 병진(translation)과 회전(rotation)을 모두 포함하는 6자유도 목표 포즈 도달. play objective 의 기본형.
- **Assembly-by-disassembly** — 완성된 CAD 조립에서 부품을 순차적으로 제거해 얻은 분해 순서를 뒤집어 조립 순서·중간 목표를 자동 생성하는 기법.
- **SAPG (Split and Aggregate Policy Gradients)** — 대규모 병렬 환경에서 탐색을 개선하는 PPO 의 population-based 변종. 본 논문의 유일한 RL 알고리즘.
- **Sim-to-real transfer** — 시뮬레이션에서 학습한 정책을 실로봇에 무손실로 옮기는 것. domain randomization + CAD 포즈 추적으로 zero-shot 실현.
- **FoundationPose** — CAD 메시로 물체 6D 포즈를 실시간 추적하는 범용 포즈 추정기. 배포 시 현재 부품·고정구 포즈 관측을 제공.
- **Keypoint-based pose distance** — 물체 로컬 프레임의 4개 keypoint 를 월드 좌표로 변환해 최대 유클리드 거리로 병진·회전 오차를 하나의 스칼라로 통합하는 거리 지표.
- **Domain randomization (DR)** — action latency, 관측 지연·노이즈, 물체 기하·질량, 외력을 무작위화해 sim2real 격차를 메우는 학습 기법.

---

## 🔬 방법론

### 직관

핵심 착상은 한 문장입니다: 어려운 문제(정밀 조립)를 직접 RL 로 풀려 하면 sparse reward 때문에 아무 보상도 받지 못한 채 무한 탐색에 빠지므로, 그 전에 *쉽고 보상이 풍부한 놀이*를 먼저 배워 손 쓰는 법을 익히자는 것입니다. 놀이는 절차적으로 만든 온갖 물체를 집어 들고 손 안에서 이리저리 무작위 목표 포즈로 돌려놓는 것이며, 이 과정에서 grasp·in-hand 재배향·정밀 포즈 도달이라는 재사용 가능한 손 기술이 정책에 심깁니다.

그다음 조립은 이 일반 prior 를 특정 task 에 "완성"하는 단계입니다. 조립 환경은 CAD 설계에서 자동으로 만들고, 보상은 오직 최종(및 소수의 중간 접촉) 목표 포즈 도달로만 정의되는 sparse 신호입니다. play 로 이미 물체를 안정적으로 쥐고 돌릴 줄 알기 때문에, 미세조정은 마지막 contact-rich·고정밀 상호작용에만 탐색을 집중하면 되고, 그래서 학습이 극적으로 빨라집니다.

논문 전체를 관통하는 발견은 "무엇이 좋은 놀이인가"입니다. 물체를 그냥 집어 옮기는 놀이(translation-only)로는 부족하고, *손가락으로 물체 자세를 정밀하게(6D, 1 cm 허용오차) 제어*하도록 강제해야 조립으로 전이됩니다. 즉 놀이의 가치는 "물건을 옮기는 법"이 아니라 "손가락으로 물체를 6D 로 정밀 제어하는 법"에 있습니다.

![Figure 2 — play 사전학습에서 무엇이 중요한가](https://arxiv.org/html/2606.26428/x2.png)

> "Figure 2: What matters in dexterous play pretraining? We study the key factors that shape the learned manipulation prior. Our design emphasizes in-hand manipulation with fingers across diverse objects and trajectories, with 6D pose-reaching objectives and precise goal tolerances." (§2)
(한글 해설 — 놀이 prior 를 결정짓는 네 축(물체 다양성 · 궤적 다양성 · 6D 포즈 도달 목표 · 정밀 허용오차)을 한 장에 요약한 그림으로, 본 논문의 ablation 이 각각을 어떻게 검증하는지 예고합니다.)

### 아키텍처

**정책 정식화.** play 는 goal-conditioned RL 로 정식화되고, 하나의 정책이 팔과 손을 함께 제어합니다.

> "Concretely, we formulate play as a goal-conditioned RL problem and train a policy $`\pi_{\theta}(\mathbf{s}_{t},\mathbf{o}_{t},\mathbf{g}_{t},\mathbf{\phi})`$, where $`\mathbf{s}_{t}`$ denotes robot proprioception, $`\mathbf{o}_{t},\mathbf{g}_{t}\in SE(3)`$ are the current and target object poses, and $`\mathbf{\phi}`$ encodes object geometry through its 3D bounding-box dimensions. A single policy controls both the arm and hand attached to it." (§3.1)
(한글 해설 — 입력은 로봇 proprioception, 현재·목표 물체 포즈(SE(3)), 3D bounding-box 로 인코딩한 물체 기하이며, *팔과 손을 하나의 정책*이 동시에 제어한다는 점이 P1 관점에서 중요한 설계 선택입니다.)

- **관측 (140-dim)** — robot proprioception(29개 관절 위치·속도, 직전 관절 위치 타깃, palm pose, palm 기준 5개 fingertip 위치) + 현재/목표 물체 포즈(primary 성분 dims 로 정의한 4 keypoint 의 palm-상대 표현 + 목표까지의 keypoint 변위) + 3개 물체 dimension. 상대 keypoint 표현으로 절대 workspace 좌표 의존을 줄이고 물체 기하를 조건화합니다.
- **행동 (29-dim)** — 7-DoF 팔 + 22-DoF 손의 관절 위치 명령. 팔은 delta 관절 위치 타깃, 손은 absolute 관절 위치 타깃으로 표현하며, 관절 한계로 클리핑 후 계수 $`\alpha=0.1`$ 의 EMA 로 평활합니다.
- **네트워크 (asymmetric actor–critic)** — actor 는 상호작용 이력을 통합하고 미관측 물체 속성을 추론하기 위해 LSTM 을 쓰고 그 뒤 MLP 가 팔·손 행동을 냅니다. critic 은 학습 시에만 noise-free·undelayed 관측, palm·물체 속도, 보상 신호, "지금까지 도달한 최소 목표 거리·lift 여부" 같은 stateful 진행 특징을 추가로 받습니다(privileged information).

  - actor: `LSTM[1024] + MLP[1024, 1024, 512, 512]`
  - critic: `MLP[1024, 1024, 512, 512]`

**조립 환경의 자동 구성.** 조립 task 는 $`K`$ 개 강체 부품과 최종 조립 포즈를 담은 CAD 설계로 정의되고, assembly-by-disassembly 로 조립 순서를 만듭니다.

![Figure 3 — Assembly-by-Disassembly](https://arxiv.org/html/2606.26428/x3.png)

> "Figure 3: Assembly-by-Disassembly. Given a completed CAD assembly, we generate assembly steps by sequentially removing parts and reversing the disassembly sequence. Each step defines a sparse goal sequence: the final assembled pose and intermediate contact goals, e.g., pre-insert pose." (§3.1)
(한글 해설 — 완성 조립에서 부품을 하나씩 빼 얻은 분해 순서를 뒤집어 조립 순서를 얻고, 각 스텝이 "최종 조립 포즈 + pre-insert 같은 소수 중간 접촉 목표"의 sparse 목표 시퀀스가 되는 자동화 절차입니다.)

각 스텝은 이미 조립된 부품들이 이루는 고정구 $`f^{i}`$ 에 부품 $`p^{i}`$ 를 삽입하는 문제이며, 부품·고정구 포즈를 테이블 위에서 무작위화해 RL 환경으로 인스턴스화합니다. 접촉이 중요한 hole·삽입 부위만 해상도 256 의 signed distance field(SDF) 로, 나머지는 convex decomposition 으로 표현하는 hybrid 충돌 기하로 effective clearance 왜곡을 피합니다.

### 학습 목표 / 손실

**키포인트 기반 포즈 표현.** 각 6D 포즈를 물체 로컬 프레임의 4개 keypoint 로 나타냅니다. dims $`\mathbf{s}=[s_{x},s_{y},s_{z}]`$ 에 대해 (Eq. 1):

```math
\mathcal{K}(\mathbf{s})=\left\{\begin{bmatrix}s_{x}/2\\ s_{y}/2\\ s_{z}/2\end{bmatrix},\begin{bmatrix}s_{x}/2\\ -s_{y}/2\\ -s_{z}/2\end{bmatrix},\begin{bmatrix}-s_{x}/2\\ s_{y}/2\\ -s_{z}/2\end{bmatrix},\begin{bmatrix}-s_{x}/2\\ -s_{y}/2\\ s_{z}/2\end{bmatrix}\right\}.
```

포즈 $`o=(R_{o},\mathbf{t}_{o})`$ 에서 각 keypoint 를 월드로 변환하고(Eq. 2), 현재·목표 포즈 거리를 keypoint 최대 거리로 정의합니다(Eq. 3):

$$\mathbf{o}_{i}=R_{o}\mathbf{k}_{i}+\mathbf{t}_{o}.$$

$$d(o,g)=\max_{i}\left\|\mathbf{o}_{i}-\mathbf{g}_{i}\right\|_{2}.$$

> "This provides a single metric that jointly captures translation and rotation error." (§Appendix D)
(한글 해설 — 병진·회전 오차를 한 스칼라로 통합하는 것이 keypoint 거리의 핵심 의도입니다. 보상 계산 시에는 물체마다 병진·회전 트레이드오프를 일정하게 유지하려고 고정 dims $`\mathbf{s}^{\mathrm{rew}}=[0.14,0.03,0.03]`$ m 를 씁니다.)

**Play 보상.** 전체 보상은 smoothness · grasp · goal 세 항으로 구성됩니다(Eq. 4):

$$r=r_{\mathrm{smooth}}+r_{\mathrm{grasp}}+\mathbb{I}_{\mathrm{grasped}}r_{\mathrm{goal}}.$$

smoothness 는 팔·손 관절 속도 패널티(Eq. 5), grasp 는 fingertip 접근 후 lift 유도(Eq. 6–8):

$$r_{\mathrm{smooth}}=-\lambda_{\mathrm{arm}}\left\|\dot{\mathbf{q}}^{\mathrm{arm}}\right\|_{1}-\lambda_{\mathrm{hand}}\left\|\dot{\mathbf{q}}^{\mathrm{hand}}\right\|_{1}.$$

$$r_{\mathrm{grasp}}=r_{\mathrm{approach}}+(1-\mathbb{I}_{\mathrm{grasped}})r_{\mathrm{lift}},$$

$$r_{\mathrm{approach}}=\lambda_{\mathrm{approach}}\max\!\left(\bar{d}^{*}_{\mathrm{ft}}-\bar{d}_{\mathrm{ft}},0\right),$$

$$r_{\mathrm{lift}}=\lambda_{\mathrm{lift}}\max(z-z_{\mathrm{init}},0)+B_{\mathrm{lifted}}\mathbb{I}[z\geq z_{\mathrm{lifted}}],$$

여기서 $`\bar{d}_{\mathrm{ft}}`$ 는 평균 fingertip-물체 거리, $`\bar{d}^{*}_{\mathrm{ft}}`$ 는 에피소드 내 최소 거리이며, 물체를 10 cm 들어올리면 $`\mathbb{I}_{\mathrm{grasped}}=1`$ 이 됩니다. grasp 이후 6D 목표 진행 보상(Eq. 9):

$$r_{\mathrm{goal}}=\lambda_{\mathrm{goal}}\max\!\left(d^{*}-d(o_{t},g_{t}),0\right)+B_{\mathrm{succ}}\mathbb{I}[d(o_{t},g_{t})<\epsilon],$$

$`d^{*}`$ 는 현재 목표가 샘플된 이후 최소 목표 거리입니다. 허용오차 $`\epsilon=1`$ cm 안에 들면 sparse success bonus 를 주고 새 목표를 샘플합니다. 계수는 $`\lambda_{\mathrm{arm}}=0.03`$, $`\lambda_{\mathrm{hand}}=0.003`$, $`\lambda_{\mathrm{approach}}=50`$, $`\lambda_{\mathrm{lift}}=20`$, $`\lambda_{\mathrm{goal}}=200`$, $`B_{\mathrm{lifted}}=300`$, $`B_{\mathrm{succ}}=1000`$ 입니다.

> "Across these studies, we find a consistent takeaway: play pretraining transfers best when it forces the robot to learn in-hand manipulation using its fingers rather than movement with a fixed grasp." (§1)
(한글 해설 — dense progress 항 $`r_{\mathrm{goal}}`$ 의 $`d^{*}`$ 최소거리 shaping 과 1 cm 허용오차가 결합해, 팔로 대충 옮기는 shortcut 대신 손가락 in-hand 정밀 제어를 강제하는 것이 설계 의도입니다.)

**조립 미세조정 보상.** 미세조정에서는 grasp·lift·dense 포즈 진행 보상을 *모두 제거*하고 smoothness + sparse 목표 보상만 남깁니다(Eq. 11–13):

$$r_{t}=r_{\mathrm{smooth}}+r_{\mathrm{goal}}.$$

$$r_{\mathrm{goal}}=B_{\mathrm{succ}}\mathbb{I}\!\left[d(o_{t},g_{m})<\epsilon\right]+r_{\mathrm{retract}},$$

CAD 유도 최종 목표는 고정구 포즈 $`f_{t}`$ 와 CAD 변환 $`T^{f}_{p}`$ 로부터 $`g_{M}=f_{t}T^{f}_{p}`$ (Eq. 10) 로 계산되어 무작위 고정구 배치에 불변입니다. 최종 목표에는 조립 후 손을 떼도록 retraction bonus 를 추가합니다(Eq. 14):

$$r_{\mathrm{retract}}=B_{\mathrm{retract}}\mathbb{I}\!\left[d(o_{t},g_{M})<\epsilon\;\land\;\left\|\mathbf{p}^{\mathrm{palm}}_{t}-\mathbf{p}^{\mathrm{obj}}_{t}\right\|_{2}>0.2~\mathrm{m}\right].$$

> "There are no explicit rewards for approaching, grasping, lifting, alignment, contact, or reducing pose error. These behaviors must instead be retained from the pretrained play policy and adapted through sparse-reward finetuning." (§Appendix F)
(한글 해설 — 미세조정 보상이 극도로 sparse 하다는 점이 이 논문의 핵심 주장입니다. approach·grasp·정렬 등 모든 dense shaping 을 제거했으므로, 그 행동들은 오직 play prior 에서 보존되어야만 하며 이것이 33× 효율의 원천입니다. $`B_{\mathrm{succ}}=B_{\mathrm{retract}}=1000`$.)

### 학습 셋업

- **RL 알고리즘** — SAPG(Split and Aggregate Policy Gradients), PPO 의 population-based 변종. 선행연구가 dexterous play 에서 SAPG 가 PPO 를 능가함을 보고했다고 명시합니다. 사전학습·미세조정 모두 *동일한* 알고리즘·하이퍼파라미터를 씁니다.

> "We train both play pretraining and assembly finetuning policies with Split and Aggregate Policy Gradients (SAPG), which prior work found to outperform PPO for dexterous play." (§3.3)
(한글 해설 — 대규모 병렬 환경 탐색 개선이 SAPG 채택 이유이며, 우리 D17 v1 이 PPO 를 기본으로 둔 것과 대비되는 선택입니다.)

- **SAPG 하이퍼파라미터** — learning rate `1e-4`, minibatch `98,304`, SAPG block size `4,096`, entropy bonus `0.002`, discount $`\gamma=0.99`$, GAE $`\lambda=0.95`$, PPO clip `0.1`.
- **시뮬레이터·자원** — Isaac Sim, 단일 NVIDIA RTX A6000. 물리 120 Hz, 정책 60 Hz. play 사전학습은 24,576 병렬 환경으로 7일, 각 조립 미세조정은 12,228 병렬 환경으로 1일(접촉 시뮬레이션의 GPU 메모리 부담으로 환경 수를 줄임).
- **절차적 물체** — 각 물체는 cuboid/capsule primitive 2개를 강체 결합. primary 성분 길이·단면 `[5,30]` cm, secondary 길이 `[1,15]` cm·단면 `[0.5,12]` cm, 밀도 primary `[300,600]`·secondary `[300,2000]` kg/m³ 로 기하·질량·CoM·관성을 폭넓게 무작위화.
- **에피소드·목표 샘플링** — 첫 목표는 workspace 안(`x∈[-0.35,0.35]`, `y∈[-0.1,0.2]`, `z∈[0.15,0.52]` m)에서 넓게, 이후 목표는 직전 목표 기준 병진 최대 0.1 m·회전 최대 90° 로 샘플해 반복적 in-hand 재배향을 유도. 에피소드 최대 600 control step(10 s), 물체 낙하·손이 물체에서 1.5 m 이탈·테이블 접촉력 100 N 초과·최대 성공 수 도달 시 조기 종료.
- **Domain randomization** — 현재/목표 포즈 노이즈(병진 1 cm, 회전 5°), object-pose delay 0–10 step, action·proprio delay 0–3 step, 관절속도 노이즈 σ=0.1 rad/s, 물체 dim scale 90–110 %, 테이블 높이 ±1 cm, 외력 20.0 N·외토크 2.0 N·m. 미세조정은 여기에 goal-pose 노이즈(병진 2 mm, 회전 1°), fixture yaw `[-10°,10°]` 를 추가.
- **Sim-to-real** — 배포 시 조립 CAD 메시로 FoundationPose 가 현재 부품·고정구 포즈를 6D 추적. 정책은 60 Hz closed-loop, 포즈 추적은 30 Hz. 스크립트 삽입·나사·복구 컨트롤러 없이 local search·corrective motion·regrasp·in-hand spinning 을 모두 학습된 정책이 생성합니다.

---

## 📊 실험 설정과 결과

**Task 설계.** 로봇은 22-DoF Sharpa 다지 손 + 7-DoF KUKA iiwa 14. 세 task: (1) Tight-Insertion(T자 peg 삽입, clearance 감소), (2) Assemble-Beam(Fabrica 기반 다부품 beam), (3) Screw-Leg(FurnitureBench 기반 다리 나사조임). Fabrica·FurnitureBench 부품은 병렬-죠용으로 작아 3× 스케일로 3D 프린트. 지표는 Success Rate(허용오차 $`\epsilon=1`$ cm)와 Completion Time. sim 500 rollout, 실세계 10 rollout.

### 실험 1 — dense 보상이 play 필요성을 대체하는가 (§4.1)

![Figure 4 — play 사전학습이 효율적 downstream 조립을 가능케 함](https://arxiv.org/html/2606.26428/assets/experiments/2a.png)

> "Figure 4: Dexterous Play Pretraining Enables Efficient Downstream Assembly Learning. Across four contact-rich assembly tasks, Play2Perfect rapidly learns successful policies from the shared dexterous prior, reaching high success within 2-5 hours. In contrast, training from scratch fails to make progress with either sparse task rewards or hand-engineered dense rewards." (§4)
(한글 해설 — 네 조립 task 에서 Play2Perfect 는 2–5 시간에 높은 성공률에 도달하나, sparse·dense 어느 보상의 scratch 도 진전을 못 냄을 보이는 학습곡선입니다.)

> "However, Scratch (dense reward) requires over 100 hours to reach near-perfect success, while Play2Perfect reaches the same success rate in only 4 hours, yielding a 33 $`\times`$ speed-up." (§4.1)
(한글 해설 — 단순화된 Tight-Insertion (Fixtured) 에서만 scratch 가 학습 가능해지는데, dense 보상 scratch 는 100 시간 이상, Play2Perfect 는 4 시간으로 33× 가속입니다.)

| 셋업 | 결과 |
|---|---|
| Play2Perfect (4 main tasks) | 2–5 시간 내 높은 성공률 |
| Scratch (sparse reward) | 24 시간 후에도 성공 rollout 0 |
| Scratch (dense reward) | 24 시간 후에도 성공 rollout 0 (main tasks) |
| Scratch (dense), Tight-Insertion (Fixtured) | near-perfect 까지 100 시간+ |
| Play2Perfect, Tight-Insertion (Fixtured) | 동일 성공률 4 시간 → 33× |

**강건성.** dense scratch 는 학습에 성공해도 엄지로 peg 를 *balance* 하는 brittle 전략을 씁니다.

![Figure 5 — play 사전학습이 강건한 조립 전략을 유도](https://arxiv.org/html/2606.26428/x4.png)

> "Under external force perturbations, its success rate drops to $`\sim`$ 20% with a 10N perturbation and eventually to 0% under larger perturbations. In contrast, Play2Perfect maintains over 75% success even under the largest perturbations, indicating that play pretraining induces a more robust manipulation strategy." (§4.1)
(한글 해설 — dense scratch 는 10 N 외력에 ~20 %, 더 큰 외력에 0 % 로 붕괴하는 반면 Play2Perfect 는 최대 외력에도 75 % 이상 유지 — play prior 가 안정적 grasp·복구 전략을 심는다는 증거입니다.)

### 실험 2 — play 설계 인자 절제 (§4.2)

![Figure 6 — downstream 조립 미세조정에 무엇이 중요한가](https://arxiv.org/html/2606.26428/x5.png)

> "Figure 6: What Matters in Pretraining for Downstream Assembly Finetuning? We vary key play pretraining choices and evaluate downstream RL finetuning success averaged across four assembly tasks and three seeds. Pretraining transfers best when it encourages in-hand manipulation via 6D in-hand object control across diverse objects and trajectories with precise goal tolerances." (§4)
(한글 해설 — 네 조립 task × 3 seed 평균으로 네 설계 인자를 절제한 결과를 요약한 그림으로, 각 인자가 downstream 미세조정 속도·성능에 미치는 영향을 보입니다.)

| 인자 | 변형 (기본 = Play2Perfect) | 발견 |
|---|---|---|
| Object Diversity | 10 / 100 / **1000** objects | 다양성↑ 전이↑, 단 diminishing returns — 100·1000 유사. 적당히 다양한 집합이면 충분 |
| Training Objective | **6D full** / Translation-only / Rotation-only | orientation 제어가 결정적. Translation-only 는 grasp·lift 만 배워 실패, Rotation-only 는 잘 전이되나 6D 보다 약간 느림 |
| Trajectory Diversity | **online random** / fixed 10 / fixed 100 | fixed 10·100 유사, online random 이 가장 빠름 — 목표 전이 커버리지가 조립 미세조정과 더 잘 맞음 |
| Goal Precision | **1 cm** / 5 cm / 10 cm | 정밀 목표가 중요. 10 cm 는 전이 실패, 5 cm 는 학습하나 느림 — 정밀 play 가 tight-clearance 에 맞는 prior 유도 |

> "Translation-only pretraining learns grasping and lifting, but does not learn object orientation control, and therefore fails to provide the in-hand reorientation prior needed for assembly." (§4.2)
(한글 해설 — 네 인자 중 training objective(특히 회전 제어)가 가장 크게 작동함을 못 박는 문장으로, "놀이는 옮기기가 아니라 손가락 6D 제어여야 한다"는 논문의 중심 takeaway 를 정량화합니다.)

### 실험 3 — 미세조정이 정밀 조립에 필요한가 (§4.3)

![Figure 7 — 미세조정이 tight insertion 을 가능케 함](https://arxiv.org/html/2606.26428/assets/experiments/1.png)

> "In contrast, Play2Perfect maintains high success as precision increases, achieving 95% at 4 mm, 92% at 1 mm, and 80% at 0.2 mm, which is tighter than the training distribution." (§4.3)
(한글 해설 — play-only(미세조정 없는 동결 prior)는 loosest 만 풀고 4 mm 에서 거의 0 % 인 반면, 미세조정한 Play2Perfect 는 학습 분포보다 tight 한 0.2 mm 에서도 80 % — prior 는 grasp·재배향을 주지만 정밀 접촉은 미세조정이 필요함을 보입니다.)

| Clearance | Play-only (sim) | Play2Perfect (sim) | Play-only (real) | Play2Perfect (real) |
|---|---|---|---|---|
| 40 mm | 75 % | (높음) | — | — |
| 10 mm | — | — | 60 % | 100 % |
| 4 mm | ~0 % | 95 % | — | — |
| 2 mm | — | — | 20 % | 90 % |
| 1 mm | — | 92 % | — | — |
| 0.5 mm | — | — | 0 % (실패) | 60 % |
| 0.2 mm | — | 80 % | — | — |

> "Qualitatively, Play-only tends to move directly toward the goal pose and treats contact as a disturbance. In contrast, Play2Perfect learns to search locally near the hole, make corrective motions under contact, and commit to insertion once the part is aligned." (§4.3)
(한글 해설 — 미세조정이 심는 것은 "접촉을 방해로 보고 직진"에서 "구멍 근처 local search → 접촉 하 corrective motion → 정렬 후 삽입 commit"으로의 질적 전환입니다.)

### 실험 4 — 실세계 전이 (Table 1, §4.4)

> "Table 1: Real-World Assembly Results. Play2Perfect transfers zero-shot to real-world insertion, multi-part assembly, and screwing tasks. Completion times are mean $`\pm`$ std over successful trials and measure the full task duration, including grasping, transport, and final contact-rich assembly." (§4.4, Table 1)
(한글 해설 — FoundationPose 추적만으로 실세계 미세조정 없이 세 task 모두 전이됨을 보이는 주력 표입니다. 완료 시간은 성공 시행의 mean±std.)

| | Tight-Insertion 10mm | 2mm | 0.5mm | Assemble-Beam Step 1 | Step 2 | Screw-Leg Insert | Screw |
|---|---|---|---|---|---|---|---|
| Success Rate | 10/10 | 9/10 | 6/10 | 8/10 | 7/10 | 7/10 | 5/10 |
| Completion Time | 6.8±1.5 s | 9.4±1.9 s | 11.1±5.1 s | 6.9±1.9 s | 6.4±2.5 s | 15.6±2.9 s | — |

> "On Screw-Leg, Play2Perfect achieves 7/10 success on insertion and 5/10 on full screwing, with successful trials taking $`15.6\pm 2.9`$ s including both phases." (§4.4)
(한글 해설 — clearance 가 tight 해질수록 local search 로 완료 시간이 늘고(6.8→11.1 s), 나사조임은 삽입 7/10 → full screw 5/10 로 접촉 단계에서 실패가 집중됩니다. 대부분 실패는 occlusion 에 의한 perception 저하와 contact-dynamics sim2real 불일치에서 발생.)

**Appendix ablation.** per-task ablation(Fig. 8)도 평균 곡선과 일관: 다양성↑ 안정성·최종 성능↑, translation-only 는 전 task 부진, 정밀 목표가 필수. "효과적 play 는 물체를 집어 옮기는 것이 아니라 contact-rich 조립으로 특화 가능한 정밀 손가락 6D 물체 제어를 배우는 것"이라는 중심 결론을 강화합니다.

---

## ⚖️ 한계

- **외부 지정 의존 (저자 명시)** — 시스템은 완전 자율 조립 파이프라인이 아니라 short-horizon 조립 skill 을 배웁니다. task sequencing, active-part 선택, goal pose 가 외부에서 주어지고, 정책은 task/benchmark family 별로 미세조정됩니다. 즉 "무엇을·어떤 순서로 조립할지"는 사람이 넣어야 하므로, 실제 조립 자동화로 가려면 sequencing·scene memory·recovery·multi-task 미세조정이 별도로 필요합니다.
- **포즈 추정 의존 (저자 명시)** — 실세계 배포가 FoundationPose 의 물체 포즈 추정에 전적으로 의존합니다. occlusion·빠른 운동에서 추정이 실패하며, 실패의 상당수가 여기서 발생합니다. 손가락이 물체를 가리는 in-hand manipulation 특성상 occlusion 은 구조적 취약점이며, tactile/force 관측이 없다는 점과 맞물립니다.
- **주변 기하 미관측 (저자 명시)** — 정책은 goal pose 외에 고정구·주변 geometry 를 직접 관측하지 않습니다. 새 고정구 형상·장애물이 있으면 학습된 local search 가 무력화될 수 있어, visual/tactile 관측 추가가 필요하다고 저자도 인정합니다.
- **task-agnostic 를 표방하나 primitive 물체·자유 공간에 국한** — play 물체가 cuboid/capsule primitive 뿐이고 조작이 자유 공간 포즈 도달입니다. 절제 결과가 "1000 objects 나 100 objects 나 비슷"이라는 것은 오히려 downstream 조립이 요구하는 다양성 상한이 낮음을 시사하며, 더 복잡한 concave/articulated 물체나 양손 조작으로의 확장은 검증되지 않았습니다.
- **하드웨어·시뮬레이터 종속** — 22-DoF Sharpa + KUKA iiwa 조합, Isaac Sim SDF hybrid 접촉, 물체당 7일(play)/1일(finetune) A6000 학습이라는 자원 규모는 재현·이식 비용이 큽니다. 특히 접촉 정밀 SDF(res 256)와 DR 값들은 이 특정 시뮬레이터·손에 튜닝된 것이라 다른 손·시뮬레이터로의 이식성은 미지수입니다.
- **RL-as-core 의 일반화 경계** — 조립은 "최종 부품 포즈"라는 명확한 goal 로 sparse reward 를 *정의할 수 있는* task 라서 이 접근이 성립합니다. goal 을 그렇게 못 박기 어려운 일반 dexterous task(도구 사용, 자유형 조작)로 같은 recipe 가 확장될지는 본 논문 범위 밖입니다.

---

## ♻️ 재현성

- **코드/웹사이트** — 프로젝트 페이지 `play2perfect.github.io` 가 arXiv 메타에 명시됩니다(본 분석 환경의 프록시 제약으로 직접 열람은 못 했으나 논문이 제시한 URL). 소스코드·모델 공개 여부는 페이지 확인 필요.
- **알고리즘** — SAPG(선행연구), FoundationPose(외부), Fabrica·FurnitureBench(벤치마크 출처)를 재사용. 핵심 보상·keypoint 정식화·DR 표(Table 2–4)·아키텍처(Table 2)가 Appendix 에 수치까지 명시되어 재구현 가능성이 높습니다.
- **하드웨어** — 22-DoF Sharpa 다지 손 + 7-DoF KUKA iiwa 14. Fabrica beam·FurnitureBench leg 를 3× 스케일 3D 프린트. Sharpa 팀의 기술 지원을 acknowledgements 에 명시.
- **자원** — 단일 RTX A6000, 물리 120 Hz/정책 60 Hz, play 24,576 env × 7일, finetune 12,228 env × 1일.
- **데이터** — 시연·수집 데이터 불필요(절차적 물체 + CAD). 이 점이 재현·확장 관점의 큰 장점입니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P3(Hand-level System0 RL 안정화 모듈) — 방법론적 최근접이자 최대 긴장** — 본 논문은 dexterous contact-rich 조작을 *RL 을 capability source 로* 풀며, 이는 우리 Identity 의 Antagonist B("RL-as-core for generalized dexterity") 와 P3 의 "System0-scoped 만 RL" 원칙에 정면으로 긴장합니다. 다만 조립이 *sparse-but-definable* goal task 라는 점에서, "reward-engineerable 한 좁은 문제에만 RL"이라는 우리 논리와 완전히 배치되지는 않습니다. D17(System0 RL policy spec) 은 v1 이 PPO·Isaac Lab·contact-aware reward 인데, 본 논문의 SAPG·keypoint sparse reward·retraction bonus 는 D17 의 알고리즘·보상 구조 비교군입니다. D18(System0 sim2real) 의 DR·teacher-student 라인과 달리 본 논문은 *asymmetric actor-critic(privileged critic) + CAD 포즈추적*으로 sim2real 을 해결 — D18 의 대안 레시피입니다.
- **P4(데이터 효율 적응을 위한 사전학습)** — "play 사전학습 → 조립 미세조정 → 33× 효율"은 P4 의 중심 명제(사전학습이 data-efficient adaptation 의 upstream 레버)를 *RL 판*으로 그대로 재현합니다. VLM 이 아니라 RL prior 라는 점만 다릅니다. D19(VLM lineage·적응 범위), D21(단계별 사전학습·적응 레시피) 의 "무엇을 사전학습에 담아야 downstream 이 싸지는가" 질문에 "정밀 6D in-hand 제어를 담아라"는 구체적 답을 줍니다.
- **P0(VLA 데이터셋·벤치마크)** — 사전학습 데이터를 시연이 아닌 *절차적 생성 + CAD*로 만든 사례로, D24(우선 데이터 축, egocentric-video 중심)와는 축이 다르지만 "contact-rich 데이터 부족을 sim RL 로 우회"하는 대안 데이터 소스입니다.
- **P1(이종 Body/Hand 액션 전문가)** — *하나의 정책이 팔+손을 동시 제어*(monolithic)하는 구성으로, 우리 D1(split form) v1(공유 trunk + Body/Hand split head)의 비교군입니다. 팔은 delta·손은 absolute 관절 명령이라는 표현 분리는 D5(입력 모달리티·제어율 분리) 의 관점에서 흥미로운 데이터 포인트입니다.
- **Identity 긴장/지지** — 손가락 in-hand 정밀 제어를 최우선 skill 로 못 박는다는 점은 우리 "hand-level contact 차별화" 주장을 *지지*합니다. 그러나 RL 을 전 정책의 학습 신호로 삼고 VLA·구조적 관측 융합·tactile 을 전혀 쓰지 않는다는 점은 우리 아키텍처 노선과 *상반*됩니다.
- **경쟁자 함의** — Tracked Literature(P3 §5)의 HORA·AnyRotate 계열(in-hand rotation RL)과 같은 sim2real dexterous RL 진영의 최신 강자로, 특히 *동일 Sharpa 하드웨어* 실증이라 우리 System0 sim2real 계획의 직접 참조점입니다.

---

## ✨ 핀 논문 대비 델타

- **vs HORA (P3 핀, [arXiv:2210.04887])** — HORA 는 in-hand rotation 을 RMA + privileged→tactile distillation 으로 푸는 *단일 skill* sim2real 입니다. Play2Perfect 는 (a) task-agnostic *다물체 6D play* 를 prior 로 두고 (b) *새 조립 task 로 미세조정*하는 2단계이며 (c) tactile 없이 CAD 포즈추적으로 sim2real 합니다. HORA 의 "privileged critic → 배포 관측" 축은 본 논문의 asymmetric actor-critic 과 유사하나, 본 논문은 distillation 대신 관측 자체를 배포-가용 집합으로 제한합니다.
- **vs AnyRotate (P3 방법론 base, [arXiv:2405.07391])** — AnyRotate 의 기여가 contact-aware *reward-term 구조*라면, 본 논문의 조립 보상은 정반대로 *거의 모든 dense 항을 제거한 sparse + retraction* 입니다. dense shaping 을 prior 로 대체한다는 것이 본 논문 델타의 핵심입니다.
- **vs Being-H0.5 / π0.5 (P4 핀)** — P4 핀들은 *VLM lineage × 대규모 human/robot corpus* 로 data-efficient adaptation 을 얻습니다. Play2Perfect 는 시연·human video·VLM 없이 *sim RL play* 만으로 같은 "사전학습→싼 적응" 효과(33×)를 냅니다. 즉 P4 의 "사전학습이 레버"라는 명제를 *비-VLM·비-시연* 경로로 입증하는 상보적 증거입니다.
- **vs VE2VF (P3 핀, [arXiv:2605.29564])** — VE2VF 가 vision-enabled→vision-free distillation 으로 System0-유사 배포 정책을 얻는다면, 본 논문은 애초에 배포 관측(proprio + CAD 포즈)만으로 학습해 distillation 단계를 생략합니다. 둘 다 "배포-가용 관측으로 수렴"을 지향하나 경로가 다릅니다.

---

## ⚙️ 의사결정 함의

- **D18 (System0 sim2real)** — 본 논문의 DR 표(Table 3–4)는 우리 System0 DR 설계의 직접 참조값입니다. 구체적으로 `dr.pose_noise_trans=1cm`, `dr.pose_noise_rot=5°`, `dr.action_delay=[0,3] steps`, `dr.obs_delay=[0,10] steps`, `dr.ext_force=20N`, `dr.ext_torque=2Nm` 를 우리 Sharpa Isaac Lab 셋업의 초기값 후보로 채택 검토. 미세조정 단계의 `dr.goal_noise_trans=2mm / goal_noise_rot=1° / fixture_yaw=±10°` 도 contact 단계 특화 DR 예시로 기록.
- **D17 (System0 RL policy spec)** — v1 의 PPO 대신 *SAPG* 를 대규모 병렬(Isaac Lab 8k–16k env) 탐색 개선용 후보로 추가 검토. 보상 구조 인자: `reward.keypoint_dims=[0.14,0.03,0.03]`(병진·회전 트레이드오프 고정), `reward.success_bonus=1000`, `reward.progress_shaping="min_distance"` (best-so-far shaping). 아키텍처: *asymmetric actor-critic* 에서 `critic.privileged_obs = {velocity, reward, min_goal_dist, lifted_flag}` 를 우리 System0 critic 에 추가하는 것을 검토.
- **관측 설계 (D15/D16 접점)** — actor 가 배포-가용 관측만 받고 privileged 정보는 critic 전용이라는 패턴은, 우리 System0 의 "vision 제외 + tactile·proprio" 관측 설계와 정합적입니다. `actor.obs = proprio + relative_keypoints`, `critic.obs += privileged` 라는 두 관측 집합 분리를 config 로 명시.
- **행동 표현 (P1 D3/D5)** — 팔 delta·손 absolute 관절 명령 + EMA(`action.ema_alpha=0.1`) 평활은 우리 Body/Hand 출력 표현 분리 실험에 넣을 수 있는 구체 옵션입니다.
- **사전학습 objective (P4 D21)** — "downstream 이 요구하는 정밀 skill 을 사전학습 objective 로 직접 강제하라"는 교훈은, 우리 사전학습 corpus/objective 설계에 *in-hand 6D 정밀 제어 비중*을 명시적으로 늘리는 curriculum 인자(`pretrain.objective="6D_pose_reaching"`, `pretrain.goal_tolerance=1cm`)로 반영 가능.

---

## ⚠️ 먼저 검증할 실패 모드

- **tactile 부재가 우리 Sharpa 셋업에서 치명적인가 (가장 싼 확인)** — 본 논문은 *tactile/force 없이* CAD 포즈추적만으로 성공했습니다. 하지만 우리 Sharpa 는 fingertip Deform Map 을 핵심 자산으로 봅니다. 가장 싼 sanity check: 본 논문 스타일의 keypoint sparse-reward play 를 우리 Sharpa Isaac Lab 에 그대로 붙여 *tactile 없이* in-hand cube rotation 을 학습시켜 보고, tactile 추가 시 성공률·slip count 델타를 30 trial 로 측정. tactile 이득이 작으면 우리 System0 의 tactile 중심 가정을 재검토해야 합니다.
- **FoundationPose 급 포즈추적이 우리 손가락 occlusion 에서 버티는가** — 본 논문 실패의 상당수가 occlusion 발 perception 저하입니다. 22-DoF 손으로 물체를 감싸면 occlusion 이 더 심할 수 있어, 우리 카메라 배치에서 FoundationPose 추적 dropout rate 를 먼저 측정(오프라인, 로봇 없이 rollout 영상만으로)하는 것이 저비용 게이트입니다.
- **SAPG·7일 사전학습 규모의 이식성** — play 사전학습이 물체당 7일(24,576 env, A6000)입니다. 우리 자원·시뮬레이터(Isaac Lab)로 이 규모가 재현 가능한지, SAPG 구현이 우리 스택에 있는지부터 확인. 없으면 PPO 로 대체 시 33× 주장이 유지되는지가 첫 반증 대상입니다.
- **sparse-reward 미세조정이 goal 정의 불가 task 로 확장 안 됨** — 이 recipe 는 "최종 부품 포즈"로 goal 을 못 박을 수 있어 성립합니다. 우리 flagship 인 도구 조작(tagging machine·trigger tool)은 goal 을 그렇게 정의하기 어렵습니다. 도입 전, 우리 target task 중 *sparse goal 로 표현 가능한 부분집합*(예: 삽입성 하위 task)을 먼저 식별해 적용 범위를 좁혀야 합니다.
- **SDF hybrid 접촉 튜닝 의존** — 접촉 정밀 성공이 res-256 SDF + 정밀 DR 튜닝에 기대고 있습니다. 우리 시뮬레이터·물체에서 같은 접촉 충실도를 못 내면 sim2real 이 무너집니다. 우리 Isaac Sim 접촉 파라미터로 0.5 mm clearance peg 삽입 물리를 먼저 시뮬레이션-단독 재현하는 것이 선결 확인입니다.

---

## 💡 컨텍스트 제안

- **P3 §5 Tracked Literature 후보** — 본 논문은 *동일 Sharpa 하드웨어*로 dexterous contact-rich sim2real RL 을 실증한 최신 CoRL/RSS-급 후보이며, HORA·VE2VF 와 함께 System0 sim2real·정책 spec(D17/D18)의 참조 pin 후보로 검토할 만합니다. 특히 "asymmetric privileged critic + 배포-가용 actor 관측"과 "sparse-reward + prior" 조합은 현재 pin 라인에 없는 각도입니다. (제안만 — `context/` 파일은 수정하지 않습니다.)
- **P4 관점 메모** — "사전학습이 레버"라는 명제의 *비-VLM 반례*로, P4 의 논증(사전학습 composition 이 적응 효율을 좌우)을 강화하는 cross-modal 증거로 인용 가치가 있습니다. Cross-pollination(MASTER §7) Month B(VLA/self-improving) 또는 별도 RL-pretraining 각주로 남길 후보.
- **Decision 이동 트리거 없음** — 본 논문이 우리 v1 결정을 뒤집을 근거는 아직 아닙니다. RL-as-core 는 여전히 우리 Identity 의 Antagonist 이며, 본 논문은 "goal 정의 가능한 sparse task 에 한정된 성공"이라 우리 System0-scoped 원칙을 오히려 뒷받침합니다.

---
