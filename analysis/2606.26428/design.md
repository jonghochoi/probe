# Design — Play2Perfect: What Matters in Dexterous Play Pretraining for Precise Assembly?

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Play2Perfect: What Matters in Dexterous Play Pretraining for Precise Assembly? |
| 링크 | [arXiv:2606.26428](https://arxiv.org/abs/2606.26428) |
| 분석 문서 | [`analysis/2606.26428/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-07-01 |

---

## 🧮 데이터 계약

시연·데이터셋이 아니라 *goal-conditioned RL 환경*이 데이터 원천입니다. 계약은 (a) play 사전학습 환경의 관측/행동, (b) 조립 미세조정 환경의 관측/행동으로 나뉘며 관측·행동 규격은 동일합니다.

- **입력 — proprioception**: `(B, D_proprio)` float. 29개 관절 위치·속도 + 직전 관절 위치 타깃 + palm pose + palm-상대 5개 fingertip 위치 (§3.1, §Appendix D).
- **입력 — object pose (current/goal)**: 각 포즈를 4개 keypoint 로 표현. observation 은 물체 orientation + palm-상대 현재 keypoint + 현재→목표 keypoint 변위 + 3개 물체 dimension. keypoint 는 물체 primary 성분 dims 로 정의 (§Appendix D).
- **입력 — object geometry $`\mathbf{\phi}`$**: 3D bounding-box dimensions `(B, 3)` float (§3.1).
- **관측 총차원** — `140` (proprio + current/goal pose + geometry descriptor) (§Appendix D).
- **입력 — privileged (critic 전용, 학습 시)**: noise-free·undelayed 관측 + palm·object velocity + reward 신호 + stateful 진행 특징(도달한 최소 goal 거리, lifted flag). actor 에는 미제공 (§Appendix C).
- **출력 — action**: `(B, 29)` 관절 위치 명령 = 7-DoF 팔(delta 관절 위치 타깃) + 22-DoF 손(absolute 관절 위치 타깃). 관절 한계로 클리핑 후 EMA($`\alpha=0.1`$) 평활 (§Appendix D).
- **CAD 계약 (조립)**: 조립 task = $`K`$ 강체 부품 $`\mathcal{A}=\{p^{i}\}_{i=1}^{K}`$ + 각 부품의 최종 조립 포즈. 부품-고정구 쌍마다 CAD 가 상대 변환 $`\mathbf{T}^{f}_{p}`$ 를 명시. contact-critical hole/삽입 부위는 SDF(res 256), 나머지는 convex decomposition (§3.2, §Appendix F).
- **정규화 가정** — 보상 keypoint 거리 계산 시 물체별 고정 dims $`\mathbf{s}^{\mathrm{rew}}=[0.14,0.03,0.03]`$ m 사용(병진·회전 트레이드오프 일정). observation keypoint 는 실제 물체 dims 사용 (§Appendix D). action/obs 통계 정규화 방식은 *(원문에 명시 없음 — 가정으로 메움)*.

---

## 🧰 모듈 인터페이스

```python
def keypoint_pose(pose_R: Tensor, pose_t: Tensor, dims: Tensor) -> Tensor:
    """물체 로컬 4-keypoint(Eq.1)를 월드 프레임으로 변환(Eq.2). o_i = R_o k_i + t_o"""

def keypoint_distance(o: Tensor, g: Tensor) -> Tensor:
    """현재/목표 포즈 keypoint 최대 유클리드 거리(Eq.3). 병진+회전 오차를 한 스칼라로 통합"""

def play_reward(state, obs, goal, grasped: bool) -> Tensor:
    """play 보상 r = r_smooth + r_grasp + I[grasped]·r_goal (Eq.4–9).
       approach→lift→6D goal progress + sparse success bonus."""

def sample_procedural_object(rng) -> ObjectSpec:
    """cuboid/capsule primitive 2개 결합. primary 길이·단면 [5,30]cm,
       secondary 길이 [1,15]cm·단면 [0.5,12]cm, 밀도 primary [300,600]/
       secondary [300,2000] kg/m^3 무작위화(§Appendix D)."""

def sample_play_goal_sequence(rng, workspace_bounds) -> list[SE3]:
    """첫 goal 은 workspace 넓게, 이후 goal 은 직전 대비 병진 ≤0.1m·회전 ≤90°.
       online random(기본) 또는 fixed bank(10/100) (§3.1, §Appendix D)."""

def assembly_by_disassembly(cad: CADAssembly) -> list[AssemblyStep]:
    """완성 조립에서 부품 순차 제거→역순으로 조립 순서.
       각 스텝: 최종 포즈 + 소수 중간 접촉 목표(pre-insert / 90° screw offset)."""

def assembly_goal(fixture_pose_t: SE3, T_f_p: SE3) -> SE3:
    """g_M = f_t · T^f_p (Eq.10). 무작위 고정구 배치에 불변인 월드 goal."""

def assembly_reward(obs, goal_m, goal_M, palm, obj) -> Tensor:
    """미세조정 보상 r = r_smooth + r_goal (Eq.11–14).
       dense shaping 전부 제거, sparse success + retraction bonus 만."""

def sapg_update(rollouts, actor_lstm_mlp, critic_mlp) -> None:
    """Split and Aggregate Policy Gradients(PPO population 변종).
       사전학습·미세조정 동일 알고리즘·하이퍼파라미터."""

def deploy_step(proprio, cad_meshes) -> Tensor:
    """배포: FoundationPose 로 현재 부품·고정구 6D 포즈 추적(30Hz),
       정책 60Hz closed-loop, goal 시퀀스 도달 시 advance. 스크립트 컨트롤러 없음."""
```

- **keypoint_pose / keypoint_distance** ↔ keypoint 포즈 표현 (§Appendix D, Eq. 1–3)
- **play_reward** ↔ play 보상 (§3.1, §Appendix D, Eq. 4–9)
- **sample_procedural_object / sample_play_goal_sequence** ↔ object/trajectory diversity (§3.1, §Appendix D)
- **assembly_by_disassembly / assembly_goal / assembly_reward** ↔ CAD 조립 환경·sparse 보상 (§3.2, §Appendix F, Eq. 10–14)
- **sapg_update** ↔ SAPG + asymmetric actor-critic (§3.3, §Appendix C)
- **deploy_step** ↔ FoundationPose sim2real 파이프라인 (§3.3, §Appendix G)

---

## ⛓️ 불변식·가정

- **(가정 1)** — 조립 task 의 성공은 "최종 부품 포즈 도달"이라는 sparse 조건으로 *정의 가능*하다. goal 을 이렇게 못 박을 수 없는 task 에는 이 프레임워크가 성립하지 않는다.
- **(가정 2)** — play 로 학습한 grasp·in-hand 재배향·정밀 포즈 도달 prior 가 조립의 dense shaping(approach/grasp/lift/정렬)을 *대체*한다. 미세조정 보상에는 이 항들이 전혀 없으므로, prior 가 부실하면 sparse 보상만으로는 학습 불가.
- **(가정 3)** — keypoint 최대 거리(Eq. 3)가 병진·회전 오차를 하나로 통합하는 유효 대리 지표다. 고정 $`\mathbf{s}^{\mathrm{rew}}`$ 가 물체 간 병진/회전 트레이드오프를 일정하게 유지한다.
- **(가정 4)** — actor 가 배포-가용 관측만으로도 미관측 물체 속성(질량·CoM·관성)을 LSTM 이력으로 추론할 수 있다. privileged 정보는 critic 에만 주어 배포 시 관측 격차가 없다.
- **(가정 5)** — 정밀 play 목표(허용오차 $`\epsilon=1`$ cm) + 6D(병진+회전) objective 가 tight-clearance 조립에 맞는 prior 를 유도한다. 느슨한 허용오차(≥10 cm)나 translation-only 는 전이 실패.
- **(가정 6)** — DR(pose noise·latency·외력·기하 scale) 로 학습한 정책이, 배포 시 CAD 포즈추적(FoundationPose) 의 오차 분포를 충분히 커버한다. occlusion·빠른 운동에서 추적 실패는 이 가정의 파괴점.
- **(가정 7)** — 시뮬레이터의 contact-critical SDF(res 256) 접촉 기하가 실세계 clearance(0.5 mm 급)·접촉 동역학을 충분히 근사한다.
- **(가정 8)** — primitive(cuboid/capsule) 물체·자유 공간 조작으로 학습한 prior 가 CAD 정의 임의 부품 형상으로 전이된다. object diversity 의 diminishing returns(100≈1000) 가 이 상한이 낮음을 시사.

---

## 📊 하이퍼파라미터·손실

### 손실 / 보상 식

play 보상 (§Eq. 4):

$$r=r_{\mathrm{smooth}}+r_{\mathrm{grasp}}+\mathbb{I}_{\mathrm{grasped}}r_{\mathrm{goal}}.$$

smoothness (§Eq. 5):

$$r_{\mathrm{smooth}}=-\lambda_{\mathrm{arm}}\left\|\dot{\mathbf{q}}^{\mathrm{arm}}\right\|_{1}-\lambda_{\mathrm{hand}}\left\|\dot{\mathbf{q}}^{\mathrm{hand}}\right\|_{1}.$$

grasp (§Eq. 6–8):

$$r_{\mathrm{grasp}}=r_{\mathrm{approach}}+(1-\mathbb{I}_{\mathrm{grasped}})r_{\mathrm{lift}},$$

$$r_{\mathrm{approach}}=\lambda_{\mathrm{approach}}\max\!\left(\bar{d}^{*}_{\mathrm{ft}}-\bar{d}_{\mathrm{ft}},0\right),$$

$$r_{\mathrm{lift}}=\lambda_{\mathrm{lift}}\max(z-z_{\mathrm{init}},0)+B_{\mathrm{lifted}}\mathbb{I}[z\geq z_{\mathrm{lifted}}],$$

play goal (§Eq. 9):

$$r_{\mathrm{goal}}=\lambda_{\mathrm{goal}}\max\!\left(d^{*}-d(o_{t},g_{t}),0\right)+B_{\mathrm{succ}}\mathbb{I}[d(o_{t},g_{t})<\epsilon],$$

조립 미세조정 보상 (§Eq. 11–14):

$$r_{t}=r_{\mathrm{smooth}}+r_{\mathrm{goal}}.$$

$$r_{\mathrm{goal}}=B_{\mathrm{succ}}\mathbb{I}\!\left[d(o_{t},g_{m})<\epsilon\right]+r_{\mathrm{retract}},$$

$$r_{\mathrm{retract}}=B_{\mathrm{retract}}\mathbb{I}\!\left[d(o_{t},g_{M})<\epsilon\;\land\;\left\|\mathbf{p}^{\mathrm{palm}}_{t}-\mathbf{p}^{\mathrm{obj}}_{t}\right\|_{2}>0.2~\mathrm{m}\right].$$

keypoint 포즈 거리 (§Eq. 1–3):

$$d(o,g)=\max_{i}\left\|\mathbf{o}_{i}-\mathbf{g}_{i}\right\|_{2},\qquad \mathbf{o}_{i}=R_{o}\mathbf{k}_{i}+\mathbf{t}_{o}.$$

조립 goal (§Eq. 10): $`g_{M}=f_{t}T^{f}_{p}`$.

### 하이퍼파라미터

| 이름 | 값 | 출처 |
|------|----|----|
| RL 알고리즘 | SAPG (PPO population 변종) | §3.3, §Appendix C |
| Actor network | `LSTM[1024] + MLP[1024,1024,512,512]` | §Appendix C, Table 2 |
| Critic network | `MLP[1024,1024,512,512]` (asymmetric, privileged) | §Appendix C, Table 2 |
| Learning rate | `1e-4` | Table 2 |
| Minibatch size | `98,304` | Table 2 |
| SAPG block size | `4,096` | Table 2 |
| Entropy bonus scale | `0.002` | Table 2 |
| Discount $`\gamma`$ | `0.99` | Table 2 |
| GAE $`\lambda`$ | `0.95` | Table 2 |
| PPO clip range | `0.1` | Table 2 |
| $`\lambda_{\mathrm{arm}}`$ | `0.03` | §Appendix D |
| $`\lambda_{\mathrm{hand}}`$ | `0.003` | §Appendix D |
| $`\lambda_{\mathrm{approach}}`$ | `50` | §Appendix D |
| $`\lambda_{\mathrm{lift}}`$ | `20` | §Appendix D |
| $`\lambda_{\mathrm{goal}}`$ | `200` | §Appendix D |
| $`B_{\mathrm{lifted}}`$ | `300` | §Appendix D |
| $`B_{\mathrm{succ}}`$ | `1000` | §Appendix D, F |
| $`B_{\mathrm{retract}}`$ | `1000` | §Appendix F |
| goal 허용오차 $`\epsilon`$ | `1 cm` (기본; ablation 5·10 cm) | §3.1, §4.2 |
| reward keypoint dims $`\mathbf{s}^{\mathrm{rew}}`$ | `[0.14, 0.03, 0.03] m` | §Appendix D |
| grasp lift 임계 | `10 cm` (I_grasped=1) | §Appendix D |
| action EMA $`\alpha`$ | `0.1` | §Appendix D |
| 물체 수 (object diversity) | `1000` (기본; ablation 10/100) | §4.2 |
| 관측 차원 | `140` | §Appendix D |
| 행동 차원 | `29` (7 arm delta + 22 hand absolute) | §Appendix D |
| 물리 / 정책 rate | `120 Hz / 60 Hz` | §Appendix B |
| play 병렬 환경 / 학습기간 | `24,576 env / 7일` | §Appendix B |
| finetune 병렬 환경 / 학습기간 | `12,228 env / 1일` | §Appendix B |
| GPU | 단일 NVIDIA RTX A6000 | §Appendix B |
| SDF 해상도 (contact-critical) | `256` | §Appendix F |
| DR (play) | pose noise 1cm/5°, obs delay 0–10, act delay 0–3, joint-vel σ=0.1, dim scale 90–110%, table ±1cm, force 20N, torque 2Nm | Table 3 |
| DR (finetune 추가) | goal noise 2mm/1°, fixture yaw ±10° | Table 4 |
| 배포 포즈추적 | FoundationPose, 30 Hz | §3.3, §Appendix G |
| 에피소드 길이 (play) | ≤ 600 control step (10 s) | §Appendix D |
| goal 전이 (play) | 병진 ≤0.1 m, 회전 ≤90° | §Appendix D |

---

## 🎯 평가 메트릭

- **지표** — Success Rate (%) · **임계값** — 부품이 최종 goal 포즈에 허용오차 $`\epsilon=1`$ cm 내 도달 · **비교 baseline** — Scratch (sparse reward), Scratch (dense reward, grasp/lift/10-waypoint shaping), Play-only(동결 prior).
- **지표** — Completion Time (s) · **임계값** — approach·grasp·transport·최종 contact-rich 상호작용 포함 전체 시간, 성공 시행 mean±std.
- **효율 지표** — 동일 성공률 도달 wall-clock RL 시간 · **결과** — Fixtured 삽입에서 dense scratch 100 h+ vs Play2Perfect 4 h → **33×** (§4.1).
- **강건성 지표** — 외력 perturbation 하 success rate · **결과** — dense scratch 10 N 에서 ~20 %→큰 외력 0 %; Play2Perfect 최대 외력에도 >75 % (§4.1).
- **정밀도 sweep** — clearance 별 success (sim) · **결과** — Play2Perfect 4 mm 95 % / 1 mm 92 % / 0.2 mm 80 %; Play-only 40 mm 75 %→4 mm ~0 % (§4.3).
- **실세계 (Table 1)** — Tight-Insertion 10/2/0.5 mm = 10·9·6 /10; Assemble-Beam Step1·2 = 8·7 /10; Screw-Leg insert·screw = 7·5 /10.
- **평가 규모** — sim 500 rollout(무작위 부품·고정구 포즈), real 10 rollout(고정 고정구, 무작위 부품 초기 포즈) (§4).

---

## ✨ 변경 의도 (intent)

핵심 변경 의도는 "정밀 조립을 직접 RL 로 풀지 말고, 먼저 노는 법을 배워 그 prior 를 완성하라"입니다. prior art 는 sparse·contact-rich 조립을 (a) 전용 고정구·툴로 문제를 단순화하거나 (b) dense·task-specific 보상 shaping·스크립트 다단계 컨트롤러로 풀어, 조립마다 하드웨어/보상 엔지니어링을 요구했습니다. Play2Perfect 는 세 결정으로 이를 뒤집습니다. (1) 시연 없이 절차적 물체·무작위 6D 목표로 task-agnostic play prior 를 RL 학습 — 데이터 수집을 시뮬레이션 절차 생성으로 대체. (2) 조립 미세조정 보상에서 approach·grasp·lift·정렬 등 *모든 dense shaping 을 제거*하고 sparse success + retraction 만 남겨, 그 행동들을 오직 play prior 에서 상속·특화. (3) 무엇이 좋은 play 인가를 체계적으로 절제해 "손가락 6D in-hand 정밀 제어(1 cm 허용오차, online 무작위 궤적)"가 전이의 핵심임을 규명. 그 결과 dense 보상 scratch 대비 33× 효율, tactile 없이 CAD 포즈추적만으로 0.5 mm clearance zero-shot sim2real 을 달성합니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — `vendor/lerobot` 는 imitation-learning 정책(π0/π0.5/act/diffusion/smolvla) 계열이라 *직접 대응 base 가 없습니다*. 본 논문은 RL(SAPG) + Isaac Sim 병렬 환경 + goal-conditioned reward 로, lerobot 의 어떤 policy family 와도 학습 패러다임이 다릅니다. lerobot 재사용 가능 부분은 배포 측 데이터/포즈 인터페이스 정도이며, play/finetune 환경·SAPG·보상·DR 은 전부 *신규 RL 스택(Isaac Lab 계열)* 이 필요합니다. 실제 매핑 가능 여부와 `🚧 매핑 불가` 판정은 `/implement-design` 단계에 위임합니다.

---

## 🚧 미해결 / 잠정

- **observation/action 통계 정규화** — 관측·행동의 정규화(스케일링) 방식이 본문에 명시되지 않아 *(원문에 명시 없음 — 가정으로 메움)*. 보상 keypoint 의 고정 dims 만 명시됨.
- **`D_proprio` 정확 차원** — proprio 구성요소(29 관절 위치·속도, 직전 타깃, palm pose, 5 fingertip)는 나열되나 palm pose 표현(quat vs 6D)·정확 합산 차원은 미명시. 총 관측 140-dim 만 확정.
- **screw goal 간격 / pre-insert 오프셋** — 나사조임은 90° 회전 offset goal, 삽입은 pre-insert 정렬 포즈로 명시되나, pre-insert 의 정확한 거리·중간 goal 개수 $`M`$ 는 task 별로 미공개.
- **SAPG 세부 (population 크기·aggregation)** — SAPG block size 4,096 만 표에 있고, population 수·split/aggregate 세부는 원 논문(선행연구)에 위임되어 본문 미상술.
- **Scratch dense 의 10-waypoint shaping** — dense baseline 이 초기→고정구 10 waypoint tracking + grasp/lift shaping 을 받는다고만 명시, waypoint 생성 규칙·가중치는 미공개.
- **에피소드 종료 조건 (finetune)** — play 종료 조건(낙하·1.5 m 이탈·100 N·최대 성공)은 명시되나 finetune 환경의 종료 조건은 별도 상술 없음.
- **코드 공개 여부** — 프로젝트 페이지 URL 만 있고 소스·모델·config 공개 범위는 미확인.
