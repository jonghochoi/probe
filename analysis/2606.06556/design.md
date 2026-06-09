# Design — Robots Need More than VLA and World Models

> PROBE design 산출물 (Layer 1, vendor-agnostic). 단일 한글 문서이며,
> 영문 1차 파일은 없습니다. `/analyze-paper` 가 `analysis/<id>/analysis.md` 와
> 함께 자동 생성합니다 — 알고리즘 명세를 base 좌표계 없이 추출합니다.
> base 매핑은 `/implement-design` 단계에서 이루어집니다. 형식·이모지·용어 규칙은
> `docs/STYLE.md` §6 / §4 를 정확히 따릅니다. 재실행 시 이 파일을
> 덮어씁니다.

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Robots Need More than VLA and World Models |
| 링크 | [arXiv:2606.06556](https://arxiv.org/abs/2606.06556) |
| 분석 문서 | [`analysis/2606.06556/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-09 |

> **성격 주의** — 본 논문은 **position paper** 이며 구현 가능한 단일 알고리즘이 아니라 네 개의 *인터페이스(컴포넌트) 명세* 를 제시합니다. 학습 목표·손실·하이퍼파라미터·평가 임계값은 원문에 존재하지 않으므로 대부분 `(원문에 명시 없음 — 가정으로 메움)` 으로 남깁니다. 아래 형식화는 저자가 §3.1–§3.4 에서 추상 수준으로 못박은 입출력 계약만을 옮긴 것입니다. 이 Design 은 곧장 foundry 로 매핑되기 위한 것이 아니라, 네 인터페이스의 입출력 변수를 정리한 개념 스펙입니다.

---

## 🧮 데이터 계약

저자가 형식화한 변수 좌표계(§3.1–§3.4). 텐서 shape·dtype·정규화는 원문에 명시되지 않으므로 의미 단위로만 기록합니다.

- **입력 (raw episode)** — $`\mathbf{x}=\{(v_{i},\tau_{i}^{(v)}),(m_{j},\tau_{j}^{(m)}),(h_{k},\tau_{k}^{h}),(r_{l},\tau_{l}^{(r)}),\texttt{L}\}`$: 비동기 멀티모달 — 비디오 프레임 $`v`$, 모션캡처/wearable/body-pose $`m`$, 촉각/힘/접촉/hand-sensor $`h`$, raw 로봇 로그 $`r`$(선택), 언어 $`\texttt{L}`$. 각 스트림은 독립 타임스탬프($`\tau`$)를 가지며 샘플링 주파수가 다를 수 있음. 일반형 $`\mathbf{x}\in\mathcal{X}`$.
- **출력 (사건 단위 잠재 구조)** — $`\mathbf{z}_{\zeta}=[\mathbf{s}_{\zeta},\mathbf{c}_{\zeta},\phi_{\zeta},\mathbf{u}_{\zeta},\mathbf{r}_{\zeta}]`$: object-centric 물리 상태 $`\mathbf{s}`$, 접촉/상호작용 라벨 $`\mathbf{c}`$, 태스크 단계 $`\phi`$, 잠재 물리 액션(전이 코드) $`\mathbf{u}`$, task-conditioned 진척/보상 $`\mathbf{r}`$.
- **출력 (episode 수준)** — 목표 $`\mathbf{g}`$, 결과 라벨 $`\mathbf{y}`$(success / failure / partial / unsafe). 전체 숨은 설명 $`\mathbf{z}=[\mathbf{z}_{1:Z},\mathbf{g},\mathbf{y}]`$.
- **정렬 (alignment)** — $`\mathcal{A}:\{\tau_{i}^{(v)},\tau_{j}^{(m)},\tau_{k}^{(h)},\tau_{l}^{(r)}\}\rightarrow\{1,\dots,Z\}`$: 이질 스트림 타임스탬프를 잠재 사건 타임라인 $`\zeta\in\{1,\dots,Z\}`$ 로 사상. 연속시간/이산/event-based 모두 허용(원문 미명시).
- **embodiment 별 액션** — $`\mathbf{a}_{\zeta}^{(\text{embodied})}`$: 특정 robot body 의 실행 가능 액션/스킬(관절 명령·EE 변위·gripper 상태·velocity·skill primitive 중 무엇인지는 embodiment 의존, 원문 미명시).

---

## 🧰 모듈 인터페이스

저자가 §3.1–§3.4 에서 정의한 네 인터페이스의 호출 계약. 구현은 비어 있음(position paper).

```python
def physical_data_engine(x: Episode) -> tuple[LatentEvents, Alignment]:
    """q_θ(z, A | x): 비동기 멀티모달 episode → 정렬된 잠재 물리 사건 시퀀스.
    temporal alignment + event segmentation + object-state estimation +
    contact inference + phase recognition + latent-action discovery +
    reward grounding + outcome prediction 을 공동 추론 (§3.1)."""

def task_preserving_retarget(u, s, embodiment) -> EmbodiedAction:
    """f_ψ(u_ζ, s_ζ, embodiment): 잠재 물리 액션 + object-centric 상태 →
    실행 가능 로봇 액션. 목표 효과 보존 Δ_g(s, a_embodied) ≈ Δ_g(s, u) (§3.2)."""

def physics_grounded_world_model(s, action, g, embodiment=None) -> NextState:
    """p_ω(·| s_ζ, u_ζ or a_embodied, [embodiment], g): consequence prediction —
    다음 물리 상태 분포. 픽셀이 아니라 기하·접촉·힘·제약·물성 예측 (§3.3)."""

def task_conditioned_reward(s, g, phi) -> Reward:
    """r_η(s_ζ, g, φ_ζ): 상태·목표·태스크 단계 → 진척/성공/실패 해석.
    상태에 내재한 스칼라가 아니라 목표 하의 물리 진척 해석 (§3.4)."""
```

- **physical_data_engine ($`q_{\theta}`$)** — 단일 perception 모델이 아니라 8개 하위문제 공동 추론. 다른 세 모듈의 supervision 공급원.
- **task_preserving_retarget ($`f_{\psi}`$)** — data engine 의 $`\mathbf{u}_{\zeta},\mathbf{s}_{\zeta}`$ 를 입력받아 embodiment 별 액션 산출. world model 로 후보 액션 평가 가능.
- **physics_grounded_world_model ($`p_{\omega}`$)** — retargeting 후보 평가·계획·실패 설명·counterfactual 생성에 사용. autolabelled 접촉/상태 전이를 학습 supervision 으로 받음.
- **task_conditioned_reward ($`\mathbf{r}_{\eta}`$)** — deployment outcome 해석. 컴포넌트 수준 credit assignment(어느 모듈을 갱신할지 라우팅)의 근거.
- **closed-loop 계약** — deploy → observe → infer progress/success/failure($`\mathbf{r}_{\eta}`$) → explain → add grounded supervision to $`q_{\theta}`$ → update {policy, world model, retargeting, reward} → redeploy (§3.4).

---

## ⛓️ 불변식·가정

- **(가정 1)** — 효과 보존: retargeting 은 인간 관절 궤적이 아니라 목표 관련 물리 효과를 보존해야 함. $`\Delta_{\mathbf{g}}(\text{s}_{\zeta},\mathbf{a}_{\zeta}^{(\text{embodied})})\approx\Delta_{\mathbf{g}}(\mathbf{s}_{\zeta},\mathbf{u}_{\zeta})`$ (§3.2).
- **(가정 2)** — 보상의 목표 상대성: 동일 물리 상태도 목표 $`\mathbf{g}`$ 에 따라 success/failure/irrelevant 로 달라짐. 보상은 $`(\mathbf{s},\mathbf{g},\phi)`$ 의 함수여야 함(상태 단독 스칼라 아님) (§3.4).
- **(가정 3)** — world model 유용성 조건: 생성된 미래는 시각적 사실성이 아니라 성공/실패를 결정하는 물리 변수(접촉·힘·마찰·안정성·기하)를 보존할 때만 supervision 으로 유효 (§2.3 Takeaway, §3.3).
- **(가정 4)** — 잠재 액션 ≠ 로봇 명령: video 에서 학습된 $`\mathbf{u}`$/$`\mathbf{z}`$ 는 embodiment-conditioned decoder 를 통과하기 전까지는 전이 코드/물리변화 기술자일 뿐 (§2.2).
- **(가정 5)** — 라벨 결합성: task phase·contact·object state·action·reward 는 독립이 아니라 결합되어 있어, data engine 은 이들을 공동 표현으로 통합해야 함 (§3.1).

---

## 📊 하이퍼파라미터·손실

- 손실 식: `(원문에 명시 없음 — 가정으로 메움)`. 저자는 추론 모델 $`q_{\theta}`$ · $`f_{\psi}`$ · $`p_{\omega}`$ · $`\mathbf{r}_{\eta}`$ 의 *입출력 계약* 만 제시하며, 학습 목적함수·정규화·loss term 을 정의하지 않음(position paper).
- 하이퍼:

  | 이름 | 값 | 출처 |
  |------|----|----|
  | `Z` (잠재 사건 수) | `(원문에 명시 없음)` — episode 의존 | §3.1 |
  | 모달리티 수 | 5종 (video / motion / tactile-force / robot-log / language) | §3.1 |
  | retargeting 불변량 위계 | pose → contact → object-state → intent (4단계) | §3.2 |
  | 학습률 / 배치 / 스케줄 | `(원문에 명시 없음 — 학습 미수행)` | — |

---

## 🎯 평가 메트릭

저자는 정량 임계값·baseline 을 제시하지 않으며(§4), 대신 일반화 로봇을 위한 **평가 질문 셋**을 제안합니다. 이를 메트릭 후보로 옮깁니다.

- **지표** — 약한 경험 → 유용 supervision 변환 능력 · **임계값** — `(원문에 명시 없음)` · **비교 baseline** — `(원문에 명시 없음)`
- 평가 질문(§4, verbatim 의미 보존):
  - 인간 행동에서 접촉·물체 상태 변화·태스크 단계를 추론할 수 있는가?
  - 시연된 물리 효과를 pose 복사 없이 새 embodiment 로 retarget 할 수 있는가?
  - world model 이 plausible frame 이 아니라 성공/실패를 결정하는 consequence 를 예측하는가?
  - reward model 이 현재 목표 기준으로 progress / failure / recovery / success 를 구분하는가?
  - deployment 실패가 스택의 올바른 컴포넌트(policy / reward / world model / retargeting)를 갱신하는가?
- world model 평가 원칙(§3.3): "does the future look realistic?" 가 아니라 "does the prediction preserve the physical consequences that determine success or failure?" — 시각 사실성 대신 task-conditioned consequence 보존을 메트릭 축으로.

---

## ✨ 변경 의도 (intent)

prior art(robot-native VLA 스케일링, generic video world model)는 데이터가 이미 로봇 학습 좌표계로 grounding 된 *뒤* 학습을 시작합니다. 본 논문의 의도는 그 grounding 단계 자체를 일급 컴포넌트로 끌어올려, 입력 모집단을 "깨끗한 로봇 데모"에서 "세상의 거친 물리 경험 전부"로 넓히는 것입니다. 핵심 차별점은 ① 네 인터페이스($`q_{\theta}`$/$`f_{\psi}`$/$`p_{\omega}`$/$`\mathbf{r}_{\eta}`$)로 supervision 변환을 명세화하고, ② 이를 feed-forward 가 아니라 배포 결과가 환류되는 closed-loop 로 묶어, VLA 를 정책 인터페이스 레이어로 재배치한 점입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 없음. 본 논문은 position paper 로 구현 가능한 정책/모듈/손실을 제공하지 않으므로 `pi0`/`pi05`/`act`/`diffusion` 등 어느 base policy family 와도 직접 대응되지 않습니다. 굳이 인접성을 든다면 §2.1 에서 정책 인터페이스로 인용된 $`\pi_0`$(flow-matching action expert)가 lerobot 의 `pi0` 와 같은 계보이나, 이는 본 논문이 *재배치하려는 대상* 이지 *구현 대상* 이 아닙니다. `/implement-design` 은 `🚧 매핑 불가` 를 산출할 것으로 예상됩니다.

---

## 🚧 미해결 / 잠정

- **전 항목 구현 미명세** — 네 인터페이스의 학습 목적함수·아키텍처·정규화·하이퍼파라미터가 원문에 전혀 없음(position paper). 위 시그니처는 저자의 추상 입출력 계약을 옮긴 것이며, 구현 자유도가 거의 전부 미결.
- **텐서 계약 부재** — $`\mathbf{s},\mathbf{c},\phi,\mathbf{u},\mathbf{r}`$ 의 shape·dtype·정규화 미명시 → 의미 단위로만 기록.
- **$`\Delta_{\mathbf{g}}`$ metric 미정의** — 목표 관련 물리 효과 보존을 *무엇으로* 측정하는지 비어 있어, retargeting 손실/평가를 Layer 1 스펙으로 굳히지 못함.
- **alignment $`\mathcal{A}`$ 의 타임라인 형식 미결** — 연속/이산/event-based 중 무엇인지 원문이 열어둠.
- **컴포넌트 간 오차 전파 미분석** — closed-loop 에서 grounding 오차가 어떻게 누적·증폭되는지 명세 없음(analysis ⚖️ 참조).
