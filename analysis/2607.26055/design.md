# Design — πR²: Reactive Real-time Flow Policies

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | πR²: Reactive Real-time Flow Policies |
| 링크 | [arXiv:2607.26055](https://arxiv.org/abs/2607.26055) |
| 분석 문서 | [`analysis/2607.26055/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-08-02 |

---

## 🧮 데이터 계약

시간 축은 chunk 위치 $`p\in\{0,\dots,H-1\}`$ 로만 표기하며, 절대 timestep 은 쓰지 않습니다.

**입력 — 관측 (두 채널로 분리)**

- **fast 채널 (`obs_fast`)** — proprioception. shape `(B, n_obs, D_proprio)`, float32. 제어 tick 마다 새로 읽어 액션 헤드 호출 시 최신값을 스냅샷. 실환경 인스턴스는 `D_proprio = 45` (arm 관절각 6 + hand 관절각 12 + 관절별 토크 12 + 지문 3축 힘 15), `n_obs = 1`. 시뮬 인스턴스는 `D_proprio = 32` (노이즈 관절각 16 + 관절별 추종 오차 16), `n_obs = 2`. 정규화 통계 출처는 `(원문에 명시 없음 — 가정으로 메움)` — 데이터셋 전체 평균/표준편차로 가정.
- **slow 채널 (`obs_slow`)** — vision-language 특징. shape `(B, N_slow_tokens, D_hidden)`, 백본 출력 dtype(실환경 bf16). **비동기 캐시**이며 액션 헤드가 보는 값은 $`d_{\mathrm{vis}}`$ tick 만큼 낡음. 실환경 원본은 단일 오버헤드 `640×480` RGB → 비전 인코더 → vision token + 과제 언어 프롬프트. 시뮬 인스턴스에는 실제 이미지가 없고 상태 벡터의 `9`-dim 부분집합(palm-to-object 위치 오차 3 + 물체 절대 자세 6)이 slow 채널 역할을 대신.
- **slow 채널 나이 (`d_vis`)** — 정수 스칼라 `(B,)`, 범위 `{0, …, d_vis_max}`. 학습 시 균등 샘플, 배포 시 $`d_{\mathrm{vis}}=\mathrm{round}((t_{\mathrm{state}}-t_{\mathrm{image}})/T_{\mathrm{ctrl}})`$ 로 실측.

**입력 — 노이즈 상태**

- **버퍼 (`x_tau`)** — shape `(B, H, D_action)`, float32. 위치별 노이즈 레벨이 서로 다름.
- **노이즈 레벨 (`tau`)** — shape `(B, H)`, float32, 각 원소 $`\tau_{p}\in[0,1]`$. $`\tau_{p}=1`$ 이 clean, $`\tau_{p}=0`$ 이 순수 노이즈.
- **호출 지연 (`d`)** — 정수 스칼라, 범위 `[1, d_max]`. 하이퍼파라미터가 아니라 **런타임 측정값**(학습 시에는 샘플값).

**출력**

- **속도장 (`v_hat`)** — shape `(B, H, D_action)`, float32. 위치별 플로우 속도.
- **방출 액션** — 호출당 `d` 개, shape `(B, d, D_action)`. 실환경 인스턴스는 절대 관절 위치 타깃 (`D_action = 18` = arm 6 + hand 12), `H = 50` @ 25 Hz (2 s). 시뮬 인스턴스는 상대 관절 명령 (`D_action = 16`, $`\mathbf{a}\in[-1,1]^{16}`$ 에 `0.5` 를 곱해 현재 모터 타깃에 가산), `H = 16` @ 50 Hz.
- **손실 마스크 (`m`)** — shape `(B, H)`, `{0,1}`, $`m_{p}=\mathbf{1}[p\geq d]`$.

---

## 🧰 모듈 인터페이스

```python
def build_staircase(d: int, H: int) -> Tensor:
    """3구역 계단 스케줄 tau*^{,d} in [0,1]^H 를 구성.
       front [0,d)=1 (clean clamp), interior [d,H-d)=선형 ramp,
       tail [H-d,H)=0. 사전조건: H > 2d."""

def apply_jitter(tau_star: Tensor, j: float) -> Tensor:
    """대칭 jitter tau_p <- clip(tau*_p + delta_p, 0, 1),
       delta_p ~ Uniform[-j, j]. 호출별 d 변동 흡수용."""

def training_step(a_chunk, obs_fast, obs_slow_history, d_max, d_vis_max,
                  j, alpha) -> Tensor:
    """확률 alpha 로 표준 플로우 분기(공유 tau, 마스크 없음),
       나머지는 계단 분기(d 샘플 → 계단 → front-d 를 GT 로 채움 →
       마스크). slow 채널은 d_vis 만큼 지연시키고 e(d_vis) 를 더함.
       반환: 위치별 마스킹 MSE 스칼라."""

def velocity_field(x_tau, tau, obs_fast, obs_slow, delay_embed) -> Tensor:
    """v_theta: 위치별 노이즈 레벨 tau 를 per-position 변조로 받는
       플로우 액션 헤드. 반환 shape (B, H, D_action)."""

def per_position_modulation(tau: Tensor) -> tuple[Tensor, Tensor]:
    """공유 AdaLN/FiLM 변조를 chunk 위치별 (gamma_p, beta_p) 로 분리.
       사전학습 공유 쌍에서 초기화(position-uniform 출발)."""

def delay_embedding(d_vis: int) -> Tensor:
    """(d_vis_max+1)-entry 룩업 테이블 → 헤드 hidden dim.
       zero-init (미학습 체크포인트 == 무지연 변형)."""

def euler_step(x_tau, tau, d, obs_fast, obs_slow, delay_embed) -> tuple:
    """위치별 전진량 delta_tau_p 로 1 NFE Euler substep.
       스케줄이 정확히 d 슬롯 오른쪽으로 이동 →
       위치 [d,2d) 가 tau=1 도달 후 방출. 반환: (새 버퍼, 새 tau, 방출 액션)."""

def slide_buffer(x_tau, tau, d) -> tuple[Tensor, Tensor]:
    """버퍼를 d 만큼 슬라이드하고 뒤에 d 개의 순수 노이즈 슬롯
       (tau=0) 을 append. 결과가 다시 tau*^{,d} 와 일치."""

def warm_start(obs_fast, obs_slow, H, d0) -> tuple[Tensor, Tensor]:
    """에피소드 시작: 표준 플로우 추론으로 H 위치 전체 denoise 후
       초기 추정 d0 의 tau*^{,d0} 로 재노이즈."""

def estimate_delay(query_times: deque, T_ctrl: float) -> int:
    """d <- max(1, round(mean(Q)/T_ctrl)). 최근 W 회 호출 벽시계
       지연의 롤링 평균에서 유도."""
```

**모듈 간 계약**

- `velocity_field` 는 유일한 학습 대상 경로이며, slow 백본은 **동결**(사전학습 가중치 무변경)이라 gradient 가 흐르지 않습니다. 학습되는 것은 액션 헤드(state/action projector, position embedding, DiT/U-Net 본체), per-position 변조 파라미터, 지연 임베딩 테이블입니다.
- `per_position_modulation` 은 기존 헤드에 대한 **유일한 아키텍처 변경**입니다. attention · MLP · 백본 · 채널 경로는 불변이므로, 사전학습된 플로우 정책에서 fine-tuning 으로 획득 가능해야 합니다.
- 배포 시 세 실행 흐름이 병렬입니다: 메인 제어 루프(tick 마다 fast 관측 발행 + 버퍼의 다음 액션 송신), `Action_Worker`(연속 1 NFE 질의), `VLM_Worker`(slow 캐시 원자적 갱신). 새 chunk 가 도착하면 인덱스를 $`i \leftarrow d`$ 로 되돌려 in-flight front 를 건너뜁니다.
- 옵티마이저와의 관계: 손실은 표준 플로우 매칭 MSE 에 위치별 마스크가 곱해진 형태 하나뿐이며, 보조 손실·정규화 항은 없습니다.

---

## ⛓️ 불변식·가정

- **(계단 존재 조건)** — $`H > 2d`$ 여야 interior 기울기 $`s=1/(H-2d)`$ 가 정의됩니다. $`d`$ 는 배포 시 측정값이므로, 지연이 커지면 이 조건이 런타임에 깨질 수 있습니다.
- **(스케줄 자기 재생산)** — 위치별 전진량 $`\Delta\tau_{p}`$ 는 "1 substep 후 스케줄이 정확히 $`d`$ 슬롯 오른쪽으로 이동"하도록 잡혀야 합니다. 그래야 방출 + 슬라이드 후의 버퍼가 다시 $`\boldsymbol{\tau}^{\star,d}`$ 와 일치합니다. $`d`$ 가 호출 간 변하면 몇 호출에 걸쳐 새 $`\boldsymbol{\tau}^{\star,d}`$ 로 수렴합니다.
- **(모달리티 비용 비대칭)** — proprioception 처리 비용이 vision-language 처리 비용보다 몇 자릿수 작아야 fast/slow 분리가 이득입니다. 이 비대칭이 없으면(예: fast 채널에 무거운 인코더가 들어가면) 호출당 1 NFE 전제가 무너집니다.
- **(정보 분업)** — vision·language 는 coarse 공간/과제 유도를, 신선한 proprioception 은 fine motor 보정을 담당한다는 분업이 성립해야 slow 채널의 낡음을 감내할 수 있습니다. 시각이 빠르게 변하는 과제에서는 깨집니다.
- **(제한된 slow 낡음)** — slow 채널 나이 $`d_{\mathrm{vis}}`$ 는 학습 범위 $`\{0,\dots,d_{\mathrm{vis}}^{\max}\}`$ 안에 있어야 합니다. 범위 밖은 학습 분포 밖입니다.
- **(액션 경계 연속성)** — in-flight front 를 clean 으로 clamp 하고 그 뒤를 이어 붙이는 방식은, 액션 표현이 chunk 경계에서 매끄럽게 이어진다는 가정에 의존합니다. 위치/관절각처럼 보간 가능한 표현을 전제합니다.
- **(단일 지연)** — 전 액션 차원이 하나의 $`d`$ 를 공유합니다. 출력 축을 나눠 서로 다른 실효 지연을 갖는 헤드가 둘 이상이면 스케줄도 헤드마다 필요합니다.
- **(warm-up 분기 필요)** — 에피소드 시작 시 순수 노이즈에서 chunk 전체를 denoise 하려면, 같은 네트워크가 표준(공유 $`\tau`$) 스케줄도 처리할 수 있어야 합니다. 이것이 확률 $`\alpha`$ 의 표준-플로우 분기가 존재하는 이유입니다.
- **(변조 초기화)** — per-position 파라미터가 사전학습된 공유 쌍에서 초기화되어야 position-uniform 스케줄에서 출발해 점진적으로 특화됩니다. 무작위 초기화는 사전학습 정책의 동작을 파괴합니다.
- **(지연 임베딩 zero-init)** — 룩업 테이블이 zero-init 이어야 미학습 체크포인트가 무지연 변형을 **정확히** 재현합니다.

---

## 📊 하이퍼파라미터·손실

**플로우 매칭 기본 손실 (식 1)**

$$\mathcal{L}_{\mathrm{FM}}=\mathbb{E}_{t,\mathbf{x}_{1},\boldsymbol{\epsilon}}\!\left[\|v_{\theta}(\mathbf{x}_{t},t)-(\mathbf{x}_{1}-\boldsymbol{\epsilon})\|^{2}\right].$$

**Diffusion forcing 위치별 보간 (식 2)**

$$\mathbf{x}_{\tau,p}=(1{-}\tau_{p})\,\boldsymbol{\epsilon}_{p}+\tau_{p}\,\mathbf{a}_{p},$$

**3구역 계단 스케줄 (식 3)** — interior 기울기 $`s=1/(H{-}2d)`$

```math
\tau^{\star,d}_{p}=\begin{cases}1&0\leq p<d\\[2.0pt]
1-\dfrac{p-d}{H-2d}&d\leq p<H-d\\[6.0pt]
0&H-d\leq p\leq H-1\end{cases}
```

**추론 Euler 갱신 (식 4)**

$$\mathbf{x}_{p}\;\leftarrow\;\mathbf{x}_{p}+\Delta\tau_{p}\cdot v_{\theta}(\mathbf{x},\boldsymbol{\tau},\mathbf{o})_{p},\qquad\tau_{p}\;\leftarrow\;\tau_{p}+\Delta\tau_{p},$$

**학습 손실 (Alg. 1, line 19)** — 위치별 마스킹 MSE, 보조 항 없음

$$\mathcal{L}\leftarrow\sum_{p=0}^{H-1}m_{p}\,\|\hat{\mathbf{v}}_{p}-(\mathbf{a}_{p}-\boldsymbol{\epsilon}_{p})\|^{2}$$

**jitter** — $`\tau_{p}\leftarrow\mathrm{clip}(\tau^{\star,d}_{p}+\delta_{p},0,1)`$, $`\delta_{p}\sim\mathrm{Uniform}[-j,j]`$

| 이름 | 값 | 출처 |
|------|----|----|
| `d_max` (train-time) | `5` | §3.3, Tab. 2, Tab. 5 |
| `d_vis_max` (train-time slow 지연) | `5` (25 Hz 기준 `200 ms`) | §A.2, Tab. 5 |
| `alpha` (표준-플로우 warm-up 확률) | `0.2` | §3.3, Tab. 2, Tab. 5 |
| `j` (jitter 폭) | `(원문 미명시)` | §3.3 |
| `nfe_per_call` | `1` | §3.3, Tab. 2, Tab. 5 |
| `delay_embed_table` | `(d_vis_max + 1) = 6` entries → 헤드 hidden dim, zero-init | §A.2, Tab. 5 |
| `d_window` (롤링 지연 윈도) | `W = 20` (본문 표기 "e.g.") | Alg. 2 |
| `H` (chunk length) | `50` (실환경 @ 25 Hz) / `16` (시뮬 @ 50 Hz) | Tab. 5 / Tab. 2 |
| `n_obs` (관측 history) | `1` (실환경) / `2` (시뮬) | Tab. 5 / Tab. 2 |
| optimizer | fused AdamW (실환경) / AdamW $`\beta{=}[0.95,0.999]`$ (시뮬) | Tab. 5 / Tab. 2 |
| peak LR | `1e-4` (양쪽 동일) | Tab. 5, Tab. 2 |
| LR schedule | cosine, `5%` warm-up (실환경) / cosine, `500`-step warm-up (시뮬) | Tab. 5 / Tab. 2 |
| weight decay | `1e-5` (실환경) / `1e-6` (시뮬) | Tab. 5 / Tab. 2 |
| grad-norm clip | `1.0` | Tab. 5, Tab. 2 |
| batch size | `512` (실환경) / `256` global (시뮬) | Tab. 5 / Tab. 2 |
| precision | bf16 + tf32 (실환경) | Tab. 5 |
| 학습 예산 | `100` epoch (3개 과제) / `200` epoch (1개 과제); 시뮬 `800` epoch | Tab. 5 / Tab. 2 |
| baseline 편차 (참고) | Train-time RTC: `d_max=10`, `alpha=0`, NFE `4`(실)/`15`(시뮬) | Tab. 5, Tab. 2 |
| 배치별 $`d`$ 분포 (시뮬 baseline 공유 프로토콜) | $`p(d{=}k)\propto e^{-\alpha_{d}k}`$, $`\alpha_{d}{=}1`$, $`d\in\{0,\dots,d_{\max}\}`$ | §A.1 |

`d_max` 와 `d_vis_max` 는 서로 다른 지연을 가리킵니다 — 전자는 액션 예측 루프의 호출당 지연, 후자는 vision-language 캐시의 나이입니다. 이 둘을 분리한 것이 본 논문이 Train-Time RTC 대비 더 작은 `d_max` 를 쓸 수 있는 이유입니다.

---

## 🎯 평가 메트릭

- **지표 — 성공률 (SR)** · **임계값** — 실환경은 30초 제한 내 과제 전체 완수, 셀당 `N=20` 시행 · 무작위 초기 물체 배치. 시뮬은 600 스텝 내 목표 자세 `0.2 rad` 이내 도달, 100 에피소드 평균. · **비교 baseline** — Flow Synchronous($`h=10`$) · Flow Naive Async(dense + temporal ensembling) · Flow Train-Time RTC.
- **지표 — 진행 점수 (Prog)** · **임계값** — 과제를 하위 목표로 분해한 뒤 시행당 달성 비율(하위 목표 수 `4 / 2 / 4 / 1`). 성공/실패 이분법보다 먼저 차이가 드러나므로 SR 과 함께 보고해야 합니다.
- **지표 — 실측 호출 지연 $`d`$** · **임계값** — 제어 tick 단위(25 Hz 기준 1 tick $`\approx 40`$ ms). 보고값: $`\pi\mathbf{R}^{2}`$ 는 $`d{=}1`$ (네트워크 지연 시 간헐적 $`d{=}2`$), baseline 은 $`d \in \{4,5\}`$. 이 지표가 성능 격차의 인과 축이므로 성공률과 반드시 함께 기록합니다.
- **지표 — 지문 접촉력 피크** · **임계값** — 보고값 $`\pi\mathbf{R}^{2}`$ 약 `50 N` vs Train-Time RTC 약 `120 N` (Tidy Up Book 중지). 반응성이 실제로 힘 변조로 이어졌는지 확인하는 메커니즘 지표.
- **지표 — 지연 하 성공률 곡선** · **임계값** — 단위 지연 $`d_{0}\in\{1,2,3\}`$ 스윕에서 보고값 `0.43 / 0.42 / 0.45`, 비교군 naive-async `0.33 / 0.29 / 0.22`, train-time RTC `0.36 / 0.32 / 0.19`. **판정 기준은 절대값이 아니라 기울기** — $`d_{0}`$ 증가에 대해 성능이 평평해야 채널 분리가 실제로 작동한 것입니다.
- **지표 — 실행 지평 $`h`$ 스윕** · **임계값** — 지연 0 조건에서 표준 플로우 $`h\in\{1,2,4,8\}`$ 대비, 1 NFE 방출이 $`h\in\{1,2\}`$ 성능과 동등해야 합니다(우월이 아니라 동등이 목표).

---

## ✨ 변경 의도 (intent)

기존 action-chunking 플로우 정책은 "예측 한 번의 비용"과 "반응 주기"를 하나로 묶어 놓았습니다 — 대형 백본 순전파 1회 + denoising $`K`$ 회가 끝나야 다음 액션이 나오므로, 반응 주기는 백본 크기에 비례해 늘어납니다. RTC 계열은 이 구조를 그대로 둔 채 chunk 경계의 불연속만 inpaint 조건화로 봉합했고, streaming diffusion 계열은 diffusion forcing 으로 점진 방출을 했지만 지연 0(즉시 추론)을 암묵 전제해 in-flight 액션을 다루지 못했습니다.

본 Design 은 두 축을 동시에 끊습니다. 첫째, 조건화를 **갱신 주기**로 비대칭 분할합니다 — 시각·언어 특징은 비동기 백그라운드 갱신 캐시로 내리고 그 나이를 학습된 임베딩으로 명시화하는 대신, proprioception 은 매 tick 신선하게 유지합니다. 그 결과 액션 헤드의 호출당 비용이 백본 크기와 분리됩니다. 둘째, denoising 예산을 **호출들에 걸쳐 분할 상환**합니다 — 위치별 노이즈 레벨을 clean front / ramp interior / noise tail 의 계단으로 배치해, 호출당 1 NFE 만으로 앞쪽 $`d`$ 개가 완성되어 방출되고 스케줄이 자기 자신을 재생산하게 만듭니다.

Train-Time RTC 와의 차이는 정확히 계단의 interior 에 있습니다: 양쪽 모두 in-flight $`d`$ 개를 clean 으로 clamp 하지만, RTC 는 나머지 $`H-d`$ 위치에 단일 공유 노이즈 레벨을 두는 반면 이 Design 은 ramp + tail 로 구조화해 single-step 방출을 가능하게 합니다. 그리고 RTC 가 손대지 않은 축 — 매 호출 백본 재통과 — 이 비동기 slow 채널로 제거됩니다. 학습 시 $`d`$ 와 $`d_{\mathrm{vis}}`$ 를 각각 무작위화했으므로, 하나의 가중치가 GPU·네트워크가 바뀌어 달라진 실측 지연에 재학습 없이 적응합니다. 아키텍처 변경을 공유 변조 → 위치별 변조 하나로 제한한 것은 사전학습 정책을 fine-tuning 만으로 승격시키기 위한 설계 제약입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 핵심 대상은 flow-matching 액션 헤드를 가진 `pi0` / `pi05` family 이며, 위치별 노이즈 조건화 변경이 들어갈 자리는 액션 expert 의 시간 조건화(AdaLN/시간 임베딩) 경로입니다. `rtc` 모듈이 in-flight 액션 prefix 조건화라는 인접 개념을 이미 담고 있으므로, 계단 스케줄은 그 위의 일반화로 얹히거나 별도 스케줄러 모듈로 들어갈 후보가 있습니다. 반면 **비동기 slow 채널**은 정책 코드가 아니라 배포 런타임(워커 스레드 + 캐시 + 롤링 지연 측정)의 문제라 대응 base 가 분명하지 않으므로, 이 절반은 매핑 불가 판정이 날 가능성이 있습니다(`/implement-design` 가 판정). 시뮬 인스턴스의 Conditional U-Net 1D + 위치별 FiLM 변형은 `diffusion` family 쪽에 더 가깝습니다.

---

## 🚧 미해결 / 잠정

- **jitter 폭 $`j`$ 의 값이 원문 어디에도 없습니다** — §3.3 과 Alg. 1 이 기호로만 도입하고 Tab. 2 / Tab. 5 에도 행이 없습니다. Layer 2 에서 값을 가정해야 합니다.
- **위치별 전진량 $`\Delta\tau_{p}`$ 의 닫힌 식이 없습니다** — "스케줄이 $`d`$ 슬롯 오른쪽으로 이동하도록 선택"이라는 조건만 서술되고 구역별 구체식은 제시되지 않습니다. 계단 형상과 $`d`$ 로부터 유도 가능하지만, 구현 시 재유도가 필요합니다.
- **$`d`$ 가 호출 간 변할 때의 전이 규칙이 정성적입니다** — "몇 호출에 걸쳐 새 $`\boldsymbol{\tau}^{\star,d}`$ 로 끌려간다"고만 적혀 있고, 끌어당김의 구체적 보간 규칙은 명시되지 않았습니다.
- **정규화 통계 출처 미명시** — proprioception / 액션 정규화의 통계 산출 범위가 본문에 없어 "데이터셋 전체 평균/표준편차" 로 가정했습니다.
- **지연 임베딩의 주입 지점이 두 서술 사이에서 다릅니다** — §3.2 는 "학습된 임베딩을 slow 표현에 더한다", §A.2 는 "DiT 가 $`e(d_{\mathrm{vis}})`$ 를 액션 토큰 특징에 $`H`$ 위치 broadcast 로 더한다" 로 적혀 있습니다. Alg. 1 line 17 은 "append to slow representation" 입니다. 실제 구현 지점을 하나로 굳히지 못했습니다.
- **시뮬 인스턴스에는 지연 임베딩·지연 샘플링이 없습니다** — §A.1 이 불필요했다고 명시하므로, 이 메커니즘의 Layer 1 스펙은 실환경 서술에만 근거합니다.
- **`d_max` 와 실행 지평의 관계** — 실험에서는 $`h=d`$ 로 맞추었으나, 이것이 알고리즘의 요구인지 실험 통제인지 본문이 구분하지 않습니다. 잠정적으로 실험 통제로 해석했습니다.
- **두 기여의 정량 분해 부재** — 계단 스케줄 단독(`w/o async`) 성능이 본문 수치로 제시되지 않아, Layer 1 에서 두 모듈의 상대 기여를 스펙에 반영하지 못했습니다.
