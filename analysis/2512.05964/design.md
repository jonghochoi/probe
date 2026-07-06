# Design — Training-Time Action Conditioning for Efficient Real-Time Chunking

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Training-Time Action Conditioning for Efficient Real-Time Chunking |
| 링크 | [arXiv:2512.05964](https://arxiv.org/abs/2512.05964) |
| 분석 문서 | [`analysis/2512.05964/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-07-06 |

---

## 🧮 데이터 계약

- **입력 — observation**: `observation` — base 정책이 쓰는 관측 그대로 (이미지/proprio/언어 등 모달리티 구성은 원문에 명시 없음 — base 정책 계약을 따름). 본 방법은 관측 인코딩을 변경하지 않습니다.
- **입력 — action chunk (학습)**: `action_chunk` shape `(B, H, D_action)`, float. ground-truth 액션. 정규화는 base 정책 규약을 따름 (원문에 명시 없음 — 가정으로 메움).
- **입력 — delay (학습)**: `delay` shape `(B,)`, int, 분포에서 샘플 (실환경 예: `Unif[0, max_delay)`). `prefix_mask = arange(H) < delay`.
- **입력 — per-token flow matching timestep**: `time` shape `(B, H)`, float ∈ [0, 1]. prefix 위치는 1.0 고정, postfix 위치는 공유 스칼라 $`\tau \sim \mathrm{Unif}[0,1]`$.
- **입력 — action prefix (추론)**: `action_prefix` shape `(B, H, D_action)` 로 패딩하되 앞 `delay` 개만 유효 (이전 chunk 에서 겹치는 커밋 액션).
- **출력**: action chunk `(B, H, D_action)` — 앞 `delay` 개는 prefix 를 그대로 통과, 나머지 postfix 가 생성 결과. 유효 출력은 postfix $`\mathbf{A}_{t+d:H}`$.
- **시간 축 제약**: prefix 유효 조건 $`d \leq H - s`$ (`H` = prediction horizon, `s` = execution horizon).

---

## 🧰 모듈 인터페이스

```python
def compute_loss(rng, model, observation, action_chunk, max_delay) -> loss:
    """delay 를 배치별 샘플링, prefix 에 time=1.0·ground-truth 주입, postfix-only masked flow matching 손실을 반환"""

def sample_actions(rng, model, observation, action_prefix, delay, num_steps) -> action_chunk:
    """매 Euler 적분 스텝에서 prefix 위치를 action_prefix 로 덮어쓰고 time=1.0 을 부여, guidance 없이 postfix 를 생성"""

def model(observation, x_t, time) -> v_t:
    """velocity 네트워크 v_θ. time 이 스칼라가 아닌 per-token (B, H) 인 것이 유일한 시그니처 변화"""
```

- `compute_loss` — 역할: 학습 목표. 외부 계약: 표준 flow matching 학습 루프의 손실 함수 자리에 그대로 치환. optimizer·스케줄 변경 없음.
- `sample_actions` — 역할: 추론. 외부 계약: 추론 시점 RTC 의 액션 생성 컴포넌트와 동일한 인터페이스 (입력 (prefix, `delay`) → 출력 postfix) — 비동기 실행 런타임(chunk 스케줄링·큐)은 손대지 않음.
- `model` — 역할: DiT 계열 action expert. adaLN-zero 의 scale/shift/gate 를 토큰별로 달리 적용하도록 확장 (학습 파라미터 수 불변).

---

## ⛓️ 불변식·가정

- (가정 1) — flow matching 보간 규약에서 $`\tau=1`$ 이 깨끗한 데이터에 대응한다 ( $`\mathbf{A}_{t}^{\tau}=\tau\mathbf{A}_{t}+(1-\tau)\boldsymbol{\epsilon}`$ ). prefix 에 time=1.0 을 주는 트릭은 이 규약에 의존하며, 반대 규약( $`\tau=0`$ =데이터)의 base 에서는 time=0.0 으로 뒤집어야 한다.
- (가정 2) — 커밋된 prefix 액션은 로봇이 그대로 실행한다 (prefix = 실행 이력의 ground truth). prefix 가 실행 중 변형(안전 필터, 클리핑)되면 조건화 분포가 어긋난다.
- (가정 3) — 학습 시 시뮬레이션한 delay 분포가 배치 시 실제 지연 분포를 커버한다. 분포 밖 지연에서의 동작은 보장되지 않는다.
- (가정 4) — prefix 유효 조건 $`d \leq H - s`$ 가 런타임에서 항상 성립한다.
- (가정 5) — 학습 데이터의 chunk 내부가 시간적으로 일관된 단일 궤적이다 (prefix 와 postfix 를 같은 ground-truth chunk 에서 잘라 조건부 분포 $`p(\mathbf{A}_{t+d:H}|\mathbf{o}_{t},\mathbf{A}_{t:t+d})`$ 를 정의하므로).
- (가정 6) — per-token timestep 패턴만으로 모델이 지연 크기를 식별할 수 있다 (별도 delay 임베딩 없음).

---

## 📊 하이퍼파라미터·손실

**손실 식** — 표준 conditional flow matching 손실에 postfix 마스킹을 적용:

$$\mathcal{L}(\theta)=\mathbb{E}\;||\mathbf{v}_{\theta}(\mathbf{A}_{t}^{\tau},\mathbf{o}_{t},\tau)-(\boldsymbol{\epsilon}-\mathbf{A}_{t})||^{2}$$

(식 (2) 원문 표기. 단, Algorithm 1 코드의 타깃은 `(action_chunk - noise)` 로 부호가 반대이며 코드 쪽이 적분 규약과 정합적 — §🚧 참조.) postfix 마스킹은 Algorithm 1 그대로:

```python
loss = jnp.sum(loss * postfix_mask) / (jnp.sum(postfix_mask) + 1e-8)
```

| 이름 | 값 | 출처 |
|------|----|----|
| `H` (prediction horizon, sim) | `8` | §V-A |
| 정책 아키텍처 (sim) | 4-layer MLP-Mixer | §V-A |
| 학습량 (sim) | 32 epoch (학습 시점 RTC: 24 epoch 재개 + 8 epoch prefix 조건화) | §V-A |
| delay 분포 (sim) | `{0,1,2,3,4}`, 지수 감쇠 가중 | §V-A |
| base 모델 (real) | π0.6 | §V-B |
| fine-tune (real) | 8,000 gradient steps · batch 512 | §V-B |
| delay 분포 (real) | `Unif[0, 10]` (50 Hz 에서 최대 200 ms) | §V-B |
| denoising steps (추론) | `5` | §V-B |
| `H` (real) | (원문 미명시) | — |
| optimizer / lr / 스케줄 | (원문 미명시) | — |
| prefix 의 flow timestep | `1.0` 고정 | §IV, Algorithm 1 |

---

## 🎯 평가 메트릭

- **지표(sim)** — binary solve rate (Kinetix) · **셋업** — 지연 0–4 스윕, 고정 실행 지평 $`s=\max(d,1)`$, 데이터 포인트당 2048 rollout, 95% Wilson score interval · **비교 baseline** — naive synchronous, naive asynchronous, inference-time RTC
- **지표(real)** — task success rate (68% Wilson) + task duration ( $`\pm 1`$ SEM) · **태스크** — box building, espresso making · **비교 baseline** — synchronous inference, inference-time RTC
- **효율 지표** — end-to-end inference latency: 108 ms (training-time, $`d\approx 5`$ ) vs 135 ms (inference-time, $`d\approx 7`$ ), 원격 H100, 5 denoising steps
- **통과 기준** — 명시적 임계값 없음: 추론 시점 RTC 와 성능·속도 동률 + 오버헤드 제거가 성공 조건 (원문 주장 구조)

---

## ✨ 변경 의도 (intent)

추론 시점 RTC(pseudoinverse guidance 인페인팅)는 denoising 매 스텝 vector-Jacobian product(backprop)를 요구해 실시간 실행 장치가 스스로 지연을 늘리는 모순이 있었고, prefix 가 길어질수록 Jacobian 선형화에 의존하는 인페인팅이 일관된 postfix 생성에 실패하기 쉬웠습니다. 본 Design 은 같은 조건부 생성 문제 $`p(\mathbf{A}_{t+d:H}|\mathbf{o}_{t},\mathbf{A}_{t:t+d})`$ 를 학습 목표로 옮겨, (1) per-token flow matching timestep, (2) prefix = ground truth + time 1.0, (3) postfix-only 손실이라는 세 가지 최소 변경만으로 조건화를 가중치에 학습시킵니다. 결과적으로 추론은 순수 forward 적분이 되어 오버헤드가 0 이고, 고지연 구간( $`d\geq 2`$ )에서 인페인팅보다 강건하며, 아키텍처·런타임·인터페이스가 보존되는 drop-in 대체가 됩니다. 대가는 soft masking 유연성 상실과 delay 분포라는 새 하이퍼파라미터입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 후보 base: `pi05` / `pi0` (flow-matching action expert — adaLN/timestep 조건화 구조가 본 Design 의 per-token 확장 지점). 참고로 `policies/rtc` 에 추론 시점 RTC 인프라(RTCProcessor, ActionQueue 등)가 이미 있어, 본 Design 은 그 인터페이스를 유지한 채 학습 루프(손실)와 샘플러 쪽 변경으로 매핑될 가능성이 높습니다.

---

## 🚧 미해결 / 잠정

- **식 (2) vs Algorithm 1 부호 불일치** — 원문 식 (2)의 회귀 타깃은 $`(\boldsymbol{\epsilon}-\mathbf{A}_{t})`$, Algorithm 1 코드는 `(action_chunk - noise)` ( $`=\mathbf{A}_{t}-\boldsymbol{\epsilon}`$ ). 보간 규약( $`\tau=1`$ =데이터)과 샘플러의 `+dt*v` 적분 기준으로는 코드 부호가 정합적. 본 Design 은 양쪽을 그대로 기록하며 판정하지 않음 — 구현 시 Algorithm 1 기준 검증 필요.
- **실환경 `H` 미명시** — π0.6 의 prediction horizon 과 execution horizon 값이 본문에 없음 (원문에 명시 없음 — 가정으로 메움: base 모델 기본값 유지).
- **optimizer / learning rate / 스케줄 미명시** — sim·real 모두 명시 없음. base 정책의 기존 학습 설정 유지로 가정.
- **delay 분포 선택 지침 부재** — "expected inference latency 에 기반해 신중히 선택"이라는 원칙 외에 일반 규칙 없음. sim 은 지수 감쇠, real 은 균등 — 두 선택의 기준이 서로 다르고 근거는 경험적.
- **관측 인코딩·정규화** — 본 방법은 액션 경로만 변경하므로 원문이 관측 계약을 정의하지 않음. base 정책 계약 준수로 가정.
- **prefix 길이 0 처리** — `delay=0` 이면 prefix 없음(무조건부 생성과 동일)이 코드상 자연스럽게 성립하나, 학습 분포에 0 을 포함해야 동기/저지연 fallback 이 보장된다는 점은 잠정 해석.
