# Design — Real-Time Execution of Action Chunking Flow Policies

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Real-Time Execution of Action Chunking Flow Policies |
| 링크 | [arXiv:2506.07339](https://arxiv.org/abs/2506.07339) |
| 분석 문서 | [`analysis/2506.07339/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-07-06 |

---

## 🧮 데이터 계약

RTC 는 inference-time 알고리즘이므로 학습 데이터 계약이 없고, 아래는 실행 시점의 텐서 계약입니다. 시간 축은 의미 단위(`H` = prediction horizon, `s` = execution horizon, `d` = inference delay)로 기록합니다.

- **입력** — 이전 action chunk 잔여부 `A_prev`: shape `(H - s, M)` 를 길이 `H` 로 right-pad → `(H, M)` (`M` = 액션 차원), dtype 은 정책과 동일(실기 bfloat16), 정규화는 base 정책의 액션 정규화 공간 그대로 (원문에 별도 정규화 명시 없음)
- **입력** — 관측 `o`: base 정책이 요구하는 그대로 (이미지·proprio·언어 — RTC 는 관측 인코딩에 관여하지 않음)
- **입력** — 지연 추정 `d`: 정수 (과거 지연 버퍼 `Q` 의 최댓값, 보수적 예측), 제약 $`d\leq H-s`$
- **입력** — soft mask `W`: shape `(H,)` 실수 가중치 (식 5; freeze 구간 1, 중간 지수 감쇠, 신규 구간 0). guidance 계산 시 `(H·M,)` 벡터로 브로드캐스트 취급 (원문 표기 남용 명시)
- **입력** — 초기 노이즈 `A^0`: shape `(H, M)`, $`\mathcal{N}(\mathbf{0},\mathbf{I})`$ 샘플
- **출력** — 새 action chunk `A^1`: shape `(H, M)`, base 정책의 액션 공간·정규화와 동일

---

## 🧰 모듈 인터페이스

```python
def get_action(o_next) -> action:
    """컨트롤러가 매 Δt 마다 호출. 공유 상태(뮤텍스 보호)에서 현재 chunk 의
    다음 액션 1개를 반환하고, 최신 관측을 기록하며 t 를 1 증가."""

def inference_loop() -> None:
    """백그라운드 스레드. t >= s_min 이 되면 실행된 s = t 개를 잘라낸 A_prev,
    최신 관측 o, 지연 추정 d = max(Q) 로 guided_inference 를 호출.
    완료 즉시 A_cur 를 교체하고 t -= s, 관측된 지연 t 를 Q 에 push."""

def guided_inference(pi, o, A_prev, d, s) -> A_new:
    """식 5로 W 계산, A_prev 를 H 로 right-pad, A^0 ~ N(0, I) 초기화 후
    n 스텝 동안: 식 3의 denoising 함수 f 를 정의하고, 가중 오차
    e = (A_prev - f(A^tau))^T diag(W) 의 vector-Jacobian product 를
    역모드 자동미분으로 계산, min(beta, (1-tau)/(tau*r_tau^2)) 로 clip 된
    guidance 를 더해 식 1로 적분. A^1 반환."""

def soft_mask(H, s, d) -> W:
    """식 5: W_i = 1 (i < d) / c_i*(e^{c_i}-1)/(e-1) (d <= i < H-s) / 0 (i >= H-s),
    c_i = (H-s-i)/(H-s-d+1)."""
```

- `guided_inference` 는 base 정책의 속도장 $`\mathbf{v}_{\pi}`$ 를 블랙박스 호출하되, 역모드 자동미분이 가능해야 합니다 (denoising 스텝당 backward 1회).
- loss/optimizer 와의 계약 없음 — 학습 무관, 순수 실행층.
- 스레드 계약: `get_action` 과 `inference_loop` 는 뮤텍스 $`\mathcal{M}`$ + 조건변수 $`\mathcal{C}`$ 로 동기화되고, 추론 본체(`guided_inference`)는 뮤텍스를 풀고 실행합니다.

---

## ⛓️ 불변식·가정

- (가정 1) — **실시간 제약**: $`d\leq s\leq H-d`$ . 위반 시(지연이 chunk 의 절반 초과) 액션 고갈이 발생하며 알고리즘이 성립하지 않습니다.
- (가정 2) — **보수적 지연 예측**: freeze 길이는 실제 지연 이상이어야 합니다 (`d = max(Q)` 가 실측 지연을 커버). 과소 예측 시 freeze 밖 액션이 이미 소비되어 불연속이 재발합니다.
- (가정 3) — **base 정책은 반복 denoising 계열**: flow matching (또는 inference-time 에 flow 로 변환 가능한 diffusion). autoregressive/VQ 계열에는 적용 불가.
- (가정 4) — **속도장의 미분 가능성**: $`\mathbf{v}_{\pi}`$ 에 대해 vector-Jacobian product 계산이 가능해야 합니다.
- (가정 5) — **guidance 유한성**: $`\tau=0`$ 에서 식 2의 계수가 무한대이므로 $`\beta`$ clip 이 필수 (특히 $`n`$ 이 작을 때 발산 방지).
- (가정 6) — **관측-액션 동기화**: 환경/저수준 컨트롤러가 $`\mathbf{a}_{t-1}`$ 소비와 동시에 $`\mathbf{o}_{t}`$ 를 제공한다고 가정 (sub-timestep 지연은 다루지 않음, 원문 각주 1).
- (가정 7) — **이전 chunk 의 유효성**: 이전 chunk 의 잔여 계획이 조건으로 쓸 만큼 유효하다는 가정. 급격한 전략 전환이 필요한 순간에는 이 가정이 연속성-교정속도 트레이드오프로 나타납니다.

---

## 📊 하이퍼파라미터·손실

- 손실 식: 없음 (inference-time 알고리즘, 학습 없음). guidance 항이 유일한 "목적" 성분:

$$\mathbf{v}_{\Pi\text{GDM}}(\mathbf{A}^{\tau}_{t},\mathbf{o}_{t},\tau)=\mathbf{v}(\mathbf{A}^{\tau}_{t},\mathbf{o}_{t},\tau)+\min\left(\beta,\frac{1-\tau}{\tau\cdot r^{2}_{\tau}}\right)\left(\mathbf{Y}-\widehat{\mathbf{A}^{1}_{t}}\right)^{\top}\mathrm{diag}(\mathbf{W})\;\frac{\partial\widehat{\mathbf{A}^{1}_{t}}}{\partial\mathbf{A}^{\tau}_{t}}$$

- 하이퍼:

  | 이름 | 값 | 출처 |
  |------|----|----|
  | `n` (denoising steps) | 5 (시뮬·실기 동일) | §A.5, Table 4 |
  | `H` (prediction horizon) | 8 (시뮬) / 50 (실기) | §A.5, Table 4 |
  | `s_min` (min execution horizon) | 25 (실기; 시뮬은 d 고정이라 불사용) | §A.5, Table 4 |
  | `beta` (guidance weight clipping) | 5 | §A.2, §A.5, Table 4 |
  | `b` (delay buffer size) | 10 (실기) | §A.5, Table 4 |
  | 실행 horizon 규칙 | `s = max(d, s_min)` | §3.3 |
  | mask 감쇠 스케줄 | 지수 감쇠 (식 5; 선형이 근소 차 2위) | §3.2, §A.4 |

---

## 🎯 평가 메트릭

- **지표** — 시뮬: binary solve rate (2048 rollouts/point, 95% Wilson score interval) · **임계값** — 없음(상대 비교) · **비교 baseline** — naive async, BID (`N=32`, `K=3`), TE, hard masking(자체 ablation)
- **지표** — 실기: 에피소드당 정수 progress score(과제별 substep) 와 average throughput = 완료 비율 / 에피소드 시간 ( $`\pm 1`$ SEM) · **비교 baseline** — synchronous ( $`s=25`$ ), TE sparse, TE dense
- **지표** — OOD/평활성 프록시: 최대 가속도(액션의 2차 이산 차분) (§A.2, Figure 7)
- **지연 조건** — 시뮬 $`d\in\{0,...,4\}`$ ; 실기 기본 $`d\approx 6`$ + 주입 +100ms ( $`d\approx 11`$ ) / +200ms ( $`d\approx 16`$ )

---

## ✨ 변경 의도 (intent)

기존 chunked 실행(동기 정지·naive 전환·TE 평균화·BID rejection sampling) 대비, RTC 는 **비동기 chunk 전환을 학습 없는 인페인팅 문제로 환원**합니다. 델타는 세 가지입니다: (1) ΠGDM 계열 guidance 인페인팅을 실시간 제어에 최초 적용, (2) 제어 특유의 저스텝 denoising 에서 필수인 guidance weight clipping $`\beta`$ 추가, (3) freeze 구간 밖 겹침 전체에 지수 감쇠 가중치를 주는 soft masking 으로 cross-chunk 연속성 강화. 결과적으로 base 정책·학습 레시피를 전혀 바꾸지 않고, 추론 지연에 대한 강건성(+200ms 무저하)과 chunk 경계 연속성을 동시에 얻습니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — foundry 에 이미 `policies/rtc` 모듈(RTC 구현)이 존재하므로 1차 후보는 해당 모듈과의 정합 확인·보강입니다. base 정책 family 로는 flow matching 계열인 `pi0` / `pi05` / `smolvla` 가 직접 대상이고, `diffusion` 은 inference-time flow 변환을 전제로 한 2차 후보입니다 (`pi0_fast` 류 autoregressive 계열은 비대상).

---

## 🚧 미해결 / 잠정

- **식 5 중간 구간 계수의 표기** — v2 HTML 원문은 중간 case 를 $`c_{i}\frac{e^{c_{i}}-1}{e-1}`$ 로 표기합니다 ( $`c_i`$ 가 분수 앞에 곱해진 형태). 이 형태면 $`i=d`$ 에서 가중치가 1 이 아니라 1 미만에서 시작합니다. 지수 감쇠의 의도( $`c_i`$: 1→0 에 따라 가중치 1→0)와는 $`\frac{e^{c_{i}}-1}{e-1}`$ 단독 형태가 더 자연스러워 보이나, 원문 표기를 그대로 기록하고 구현 시 공개 코드와 대조할 것을 권합니다 (fabrication 방지 차원에서 본 Design 은 원문 수식을 유지).
- **`W` 의 차원 브로드캐스트** — 원문은 `W` 를 `HM` 차원 벡터로 "표기 남용" 처리한다고만 밝히고, timestep 가중치를 액션 차원으로 어떻게 확장하는지(균일 복제로 추정)는 명시하지 않습니다 — 균일 복제로 가정.
- **diffusion→flow 변환 경로** — diffusion 정책 적용 시의 변환([48, 18] 인용)은 참조만 있고 절차가 본문에 없습니다.
- **시뮬 전용 세부 하이퍼** — "Additional hyperparameters for the simulated experiments can be found in the code" (§A.5) — 본문 미기재분은 공개 코드 참조 필요.
- **`s_min` 선택 규칙** — 실기 25 ( $`=H/2`$ ) 외에 일반 선택 기준은 원문에 명시 없음.
