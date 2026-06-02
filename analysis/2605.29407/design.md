# Design — Phase-Conditioned Imitation Learning with Autonomous Failure Recovery for Robust Deformable Object Manipulation

> PROBE design 산출물 (Layer 1, vendor-agnostic). 단일 한글 문서이며,
> 영문 1차 파일은 없습니다. `/analyze-paper` 가 `analysis/<id>/analysis.md` 와
> 함께 자동 생성합니다 — 알고리즘 명세를 base 좌표계 없이 추출합니다.
> base 매핑은 `/implement-design` 단계에서 수행합니다. 형식·이모지·용어 규칙은
> `docs/STYLE.md` §6 / §4 를 정확히 따릅니다. 재실행 시 이 파일을
> 덮어씁니다.

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Phase-Conditioned Imitation Learning with Autonomous Failure Recovery for Robust Deformable Object Manipulation |
| 링크 | [arXiv:2605.29407](https://arxiv.org/abs/2605.29407) |
| 분석 문서 | [`analysis/2605.29407/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-02 |

---

## 🧮 데이터 계약

입력은 ACT 정책과 phase 예측기가 대부분 공유합니다(예측기는 동결 백본 재사용). 시간 축은 행동 청크 단위($`N_{h}`$ = 50)를 한 단위로 삼습니다.

- **입력 — 이미지** — 4-view RGB, 각 640×480, 공유 ResNet-18 → 특징 맵 평탄화 `(B, 4·H'·W', d_model)`, 2D 사인 위치 임베딩 가산. `d_model = 512`.
- **입력 — 자세(pose)** — 양팔 EE 자세 `(B, 20)`, dtype float32, 6D 회전 표현 사용. 선형 투영 → `(B, d_model)`.
- **입력 — wrench(힘/토크)** — `(B, 12)`(양팔)을 같은 방식으로 투영해 `(B, d_model)` 로 맞춥니다. 정규화 통계 (원문에 명시 없음 — 가정으로 메움).
- **입력 — phase 라벨** — 정수 phase id(걸기 0–4, 벗기 5–7, 복구 8–10). 정책에서는 학습된 임베딩 → FiLM 조건. 예측기에서는 출력(softmax 분포).
- **입력 — Task ID** — phase 예측기 전용, 임베딩으로 탐색 공간 제약(시각이 닮은 phase 구분용).
- **출력 — 정책 행동** — $`a_{t}=[a_{t,L}^{\top},a_{t,R}^{\top}]^{\top}\in\mathbb{R}^{20}`$, 길이 `N_h=50` 청크. 각 팔 = 위치 $`\mathbb{R}^{3}`$ + 6D 방향 $`\mathbb{R}^{6}`$ + 그리퍼 $`\mathbb{R}^{1}`$.
- **출력 — phase 예측기** — phase 로짓 → softmax 분포(클래스 수 = 전체 phase 수). 1초 저역통과 필터로 평활화.
- **출력 — 컨트롤러** — 15 Hz 목표 자세를 고주파 컴플라이언스 명령으로 변환(임피던스 + 중력 보상, position/velocity 인터페이스 산업용 로봇 대상).

---

## 🧰 모듈 인터페이스

base 좌표(file:line)는 여기 들어오지 않습니다. 호출 계약만 기록합니다.

```python
def phase_conditioned_act_encoder(images, pose, wrench, phase_id) -> Tensor:
    """4-view RGB+pose+wrench+phase 임베딩을 토큰화해 FiLM 변조 트랜스포머
    인코더로 통과. phase 는 모든 인코더 층의 LayerNorm·MLP 출력에 FiLM affine
    변조(γ,β)로 주입(토큰 주입 아님). 반환: 인코더 메모리."""

def film_layer(h, gamma, beta) -> Tensor:
    """채널별 affine 변조 gamma ⊙ h + beta. (gamma,beta) 는 phase 임베딩에서
    층별로 생성. 인코더에만 적용, 디코더는 phase-agnostic 유지."""

def act_decoder(encoder_memory, z, queries) -> Tensor:
    """표준 ACT 디코더. 고정 위치 쿼리가 cross-attention 으로 인코더 메모리
    참조. z 는 CVAE 스타일 변수(추론 시 prior 평균). 반환: 행동 청크 (B,N_h,20)."""

def cvae_style_encoder(action_seq) -> z:
    """학습 시 정답 행동 시퀀스 → 잠재 분포. 추론 시 미사용(prior 평균 대체)."""

def multimodal_phase_predictor(images, pose, wrench, task_id) -> phase_logits:
    """정책의 동결 이미지 백본·자세/wrench 투영층 공유. 카메라별 GAP →
    1×d_model, 자세·wrench 투영, Task ID 임베딩 → 1×7d_model concat →
    MLP → phase 로짓 → softmax. 시각이 놓치는 접촉 실패를 힘으로 감지."""

def hybrid_impedance_controller(x_pred, x_obs, gripper_state, alpha, beta) -> cmd:
    """x_pred 보간 궤적(x_intp)과 증분 명령(Δx=x_pred-x_obs → x_inc)을
    α,β 로 혼합(Inc-IC). β 는 gripper_state 로 힘지향/순수임피던스 전환.
    임피던스+중력보상으로 실행."""

def closed_loop_step(obs) -> action:
    """예측기가 phase 추정 → 정책 조건화 → 컨트롤러 실행. 실패 감지 시 복구
    phase 출력으로 정책 재유도. phase 전환마다 temporal ensembler 리셋."""
```

---

## ⛓️ 불변식·가정

- (가정 1) — state aliasing 은 지각 수준에서 발생하는 것으로 본다. 따라서 phase 조건은 행동 생성(디코더) 이전, 특징 추출(인코더) 단계에서 작용해야 한다(인코더 변조의 근거).
- (가정 2) — 단일 phase 토큰은 1200+ 시각 토큰의 self-attention 속에 희석된다. 곱셈적(multiplicative) FiLM 변조로 모든 중간 표현을 직접 건드려야 영향력이 유지된다.
- (가정 3) — 디코더를 phase 무관(phase-agnostic)하게 두면 접근·삽입·후퇴 같은 저수준 동역학이 단계·작업 간 공유되어 데이터 효율이 오른다.
- (가정 4) — 접촉 실패(스내깅/재밍)는 시각상 성공과 구별되지 않더라도 힘 영역에서 스파이크/지속 비정상력으로 뚜렷한 시그니처를 남기는 것으로 관찰된다.
- (가정 5) — 그리퍼 닫힘 = 물체 접촉 상태로 간주 가능하며, 이를 컴플라이언스 모드 전환의 신호로 쓸 수 있다.
- (가정 6) — 추론 시 CVAE 스타일 변수 $`z`$ 를 prior 평균으로 고정하면 결정론적 디코딩이 된다.

---

## 📊 하이퍼파라미터·손실

- 손실: 표준 ACT 학습(행동 재구성 + CVAE KL 정규화). phase 예측기는 phase 분류(softmax cross-entropy). 복구 시연은 DAgger 로 정책 데이터에 통합. 구체 손실 가중치 (원문에 명시 없음 — 가정으로 메움).
- 하이퍼:

  | 이름 | 값 | 출처 |
  |------|----|----|
  | `N_h` (chunk size) | `50` | §4.B |
  | `d_model` | `512` | §4.B |
  | encoder layers | `4` | §4.B |
  | decoder layers | `2` | §4.B |
  | epochs | `60` | §4.B |
  | batch size | `8` (4 GPU) | §4.B |
  | learning rate | `1e-5` (고정) | §4.B |
  | RGB 해상도 | `640×480` | §4.B |
  | 정책 추론 주파수 | `15 Hz` | §3.C / §4.B |
  | 데이터 기록 주파수 | `30 Hz` | §4.B |
  | phase 평활화 필터 | `1초 low-pass` | §3.B |
  | 정상 시연 | 작업당 `100` 에피소드 | §4.B |
  | 복구 시연 | Phase 8/9/10 각 `30` 에피소드 | §4.B |
  | 컨트롤러 혼합 파라미터 | $`\alpha`$, $`\beta`$ (값 미명시) | §3.C |

---

## 🎯 평가 메트릭

- **지표 — Final Success Rate** · **임계값** — 걸기 56% → 87%, 벗기 88% → 92% · **비교 baseline** — 개루프(복구 없음) vs 폐루프.
- **지표 — Detection Rate / Recovery Success** · 걸기 40/44(90.91%) / 31/40(78.9%), 벗기 8/12(66.67%) / 4/8(50%) (Table I, N=100).
- **지표 — 실행 단계 robustness ablation** · Nominal / Misalignment(3–5cm) / Snagging 조건별 성공률 · baseline = ACT(A) / ACT-R(B) / ACT-MR(C) / Phase Tok(D) / Phase FiLM(E). 핵심 대비: D(60/0/20%) vs E(90/80/100%) (Table II).
- **지표 — 특징 분리도** · t-SNE 로 phase 별 임베딩 군집 분리(정량 임계값 없음, 정성). 복구 phase(8,9)가 정상 phase 와 분리된 타이트 군집인지 (§4.D.3).

---

## ✨ 변경 의도 (intent)

선행 연구(ACT·Diffusion Policy, 토큰 수준 조건화, SCIL 의 단계별 독립 정책)와 비교하면, 핵심 차이는 phase 를 **희석 불가능한 곱셈적 조건**으로 ACT 인코더 매 층에 주입하여 단일 통합 정책이 단계별 행동을 내면서도 공통 동역학까지 함께 학습시킨다는 데 있습니다. 여기에 시각만으로는 보이지 않는 접촉 실패를 힘 피드백으로 잡는 멀티모달 phase 예측기를 결합해 감지·복구·정상 복귀 전 과정을 닫힌 루프로 자동화했고, 그 결과 실행 단계(execution-time) 강건성을 확보합니다. 일반화 강건성이 아니라 실행 강건성으로 의도적으로 좁힌 적용 범위입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 베이스 정책 `act` family 와 구조적으로 가장 근접합니다(ACT 인코더-디코더 + CVAE + action chunking 구조를 그대로 계승하기 때문입니다). 핵심 변경은 세 가지입니다. 먼저 인코더 층에 FiLM 변조를 삽입하고(phase 임베딩 → 층별 γ,β), 멀티모달 phase 예측기를 추가하며, 마지막으로 폐루프 추론 루프(phase 추정 → 조건화 → temporal ensembler 리셋)를 둡니다. 임피던스 컨트롤러·햅틱 원격조작은 하드웨어 실행 계층이므로 정책 코드 매핑 대상에서 제외합니다.

---

## 🚧 미해결 / 잠정

- FiLM 의 정확한 적용 위치(LayerNorm 출력 + MLP 출력)는 본문이 서술하나, $`(\gamma,\beta)`$ 생성 네트워크의 구체 구조(층별 독립 MLP인지 공유인지)는 (원문에 명시 없음 — 가정으로 메움).
- 컨트롤러 혼합 파라미터 $`\alpha`$, $`\beta`$ 의 수치와 force-oriented 모드의 구체 임피던스 게인은 (원문에 명시 없음 — 가정으로 메움).
- pose/wrench 정규화 통계의 출처는 (원문에 명시 없음 — "데이터셋 전체 평균/표준편차"로 가정).
- 손실 항 가중치(ACT 재구성 vs KL, phase 분류 손실 비중)는 (원문에 명시 없음 — 가정으로 메움).
- phase 예측기의 static-scene 추가 샘플 규모/구성은 본문이 "추가 수집"이라고만 언급하고 수치는 (원문에 명시 없음).
