# Design — FM-VLA: Force-based Memory for Vision-Language-Action Models in Contact-Rich Manipulation

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | FM-VLA: Force-based Memory for Vision-Language-Action Models in Contact-Rich Manipulation |
| 링크 | [arXiv:2607.18231](https://arxiv.org/abs/2607.18231) |
| 분석 문서 | [`analysis/2607.18231/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-08-02 |

---

## 🧮 데이터 계약

**Stage 1 — Force-VAE (wrench 시계열 재구성)**

- **입력** — wrench 이력 $`F=[f_{1},\ldots,f_{T}]`$: shape `(B, T, d_f)`, `d_f = 6` (3축 힘 + 3축 토크), float. 단일 손목(오른손목) 스트림. 원 센서 `100 Hz` → `30 Hz` 다운샘플.
- **정규화** — 시점별 **quantile 정규화**, 통계는 과제별이 아니라 **데이터셋 전체** 기준. Stage 2 와 동일한 `q_01 / q_99` 스킴.
- **전처리 1 (평활)** — 인과적 1차 EMA: $`\tilde{f}_{\tau}=\alpha f_{\tau}+(1-\alpha)\tilde{f}_{\tau-1}`$, $`\alpha=0.3`$. onset·peak 보존이 목적이므로 비인과 필터로 대체 불가.
- **전처리 2 (증강)** — 학습 시에만 이력 앞에 랜덤 길이 가우시안 노이즈 prefix($`\sigma=0.05`$, quantile 정규화 후 기준; 길이 `~U(0, 1000)` 프레임 ≈ 10 s). 추론 시 비활성.
- **마스크** — 패딩 프레임 표시 $`m_{\tau}\in\{0,1\}`$: shape `(B, T)`. 재구성 손실은 유효 프레임에서만 계산.
- **잠재** — $`Z\in\mathbb{R}^{K\times d_{z}}`$: shape `(B, K, d_z)`, `K = 8`, `d_z = 96`. posterior 파라미터는 $`(\mu_{k},\log\sigma_{k}^{2})`$.
- **출력(재구성)** — $`\hat{F}\in\mathbb{R}^{T\times d_{f}}`$: shape `(B, T, 6)`.

**Stage 2 — VLA 정책 (메모리 조건부 플로우 매칭)**

- **입력(관찰)** — RGB 3-뷰(머리 + 좌/우 손목) + 언어 지시 + 현재 proprioceptive state. 뷰별 이미지 dropout `p = 0.4` (학습 시, 독립 적용).
- **입력(장기 힘 메모리)** — 동결 인코더의 **사후분포 평균만** $`\mu_{f}\in\mathbb{R}^{K\times d_{z}}`$ → zero-init 선형 사영 → $`Z_{f}\in\mathbb{R}^{K\times d_{h}}`$: shape `(B, 8, d_h)`. reparameterization 노이즈 미사용.
- **입력(단기 상태 메모리)** — 관절 상태 윈도우 $`S_{t}\in\mathbb{R}^{W\times d_{s}}`$: shape `(B, 10, d_s)`, stride `3` 서브샘플, offsets $`\{-27,-24,-21,\ldots,-3,0\}`$ (30 Hz 기준 ≈ 0.9 s). $`d_{s}`$ 는 embodiment 의존 — 7-DoF 양팔 + 1-D 그리퍼 2개면 `d_s = 16`. flatten 후 zero-init 선형 사영 → 단일 토큰 $`z_{s}\in\mathbb{R}^{d_{h}}`$.
- **액션 전문가 시퀀스** — noisy-action 토큰 `30` 개 → force memory 토큰 `8` 개 → state 토큰 `1` 개 순서로 concat (식 3). 메모리 토큰은 **반드시 noisy-action 토큰 뒤**.
- **출력** — 액션 청크: horizon `H = 30`, action dim `32`, delta action 타깃. 평가 시 flow-matching `10` step.
- **정규화(액션)** — quantile $`q_{01}/q_{99}`$ 스킴을 모든 baseline 과 공유.

---

## 🧰 모듈 인터페이스

```python
def preprocess_wrench(raw_100hz, alpha=0.3, train=True) -> Tensor:
    """100Hz→30Hz 다운샘플 + 전역 quantile 정규화 + 인과적 1차 EMA;
       train 이면 랜덤 길이 저진폭 가우시안 prefix 를 pre-pad (추론 시 off)."""

def force_vae_encode(F, mask) -> tuple[Tensor, Tensor]:
    """Perceiver-IO 인코더: 입력 MLP + Fourier PE → wrench 토큰,
       cross-attn(→K latent query) + latent self-attn 스택,
       per-latent 선형 헤드 → (mu, logvar), 각 (B, K, d_z)."""

def force_vae_decode(z, T) -> Tensor:
    """시점별 Fourier-encoded query 가 latent 에 cross-attn → (B, T, 6) 복원."""

def vae_loss(F, F_hat, mask, mu, logvar, beta, free_bits) -> Tensor:
    """마스크 재구성 MSE + 차원별 free-bits KL (식 4)."""

def project_force_memory(mu_f) -> Tensor:
    """동결 인코더의 사후 평균 (B, K, d_z) → zero-init 선형 → (B, K, d_h).
       학습 대상은 이 사영 레이어(W_f)뿐, 인코더는 eval 모드 동결."""

def project_state_window(S_t) -> Tensor:
    """(B, W, d_s) flatten → zero-init 선형 → 단일 토큰 (B, 1, d_h).
       사전학습 없이 정책과 end-to-end 학습."""

def build_action_expert_suffix(noisy_actions, Z_f, z_s) -> Tensor:
    """[noisy actions ‖ Z_f ‖ z_s] 순서로 concat (식 3).
       post-position 이 계약 — 앞에 삽입하면 RoPE 위치 보존이 깨짐."""

def flow_matching_loss(v_theta, a_0, eps, k, c_t, Z_f, z_s) -> Tensor:
    """rectified-flow: a_k = (1-k)a_0 + k·eps, 타깃 속도 (eps - a_0) (식 5).
       base 손실 형태 불변 — 조건 인자에 Z_f, z_s 만 추가."""
```

- **Stage 1 ↔ Stage 2 경계** — Stage 1 은 정책과 gradient 를 공유하지 않습니다. Stage 2 진입 시 인코더는 `eval()` + `requires_grad=False` 이며, 사후분포 평균만 forward 에 쓰입니다(샘플링 없음). 이 단절이 방법의 정체성이므로 end-to-end 로 합치면 다른 알고리즘이 됩니다.
- **Stage 2 학습 대상** — VLM 인코더, 플로우 매칭 액션 전문가, $`\mathrm{Proj}_{\psi}`$(단기 상태), $`W_{f}`$(wrench 잠재 사영). 힘 인코더만 제외.
- **손실 관계** — 새 보조 손실 없음. 액션 손실 하나만 존재하며 메모리 경로는 조건으로만 관여합니다.

---

## ⛓️ 불변식·가정

- **(접촉 관측 가능성)** — 과제 관련 상태 변화가 **wrench 시계열에 식별 가능한 파형으로 남는다**는 것이 전체 전제입니다. 접촉이 없거나 힘 흔적이 남지 않는 비-Markovian 과제에서는 이 방법이 원리적으로 무효입니다.
- **(길이 비누설)** — 이력 길이가 에피소드 진행도를 누설하면 모델이 신호 내용 대신 길이를 세는 지름길을 학습합니다. 랜덤 노이즈 pre-padding 이 이 불변식을 강제하는 유일한 장치이며, 제거 시 "메모리 학습" 결과가 길이 세기의 착시가 됩니다.
- **(onset 보존)** — 접촉 카운팅은 파형의 개시점·피크에 의존하므로 평활 강도 $`\alpha`$ 는 노이즈 제거와 onset 보존의 균형점이어야 합니다. 과도한 저역통과는 정보 파괴와 동치입니다.
- **(토큰 예산 ≤ base 사전학습 관측치)** — 액션 전문가가 사전학습 중 본 최대 토큰 수를 넘기면 분포 이동으로 행동 생성이 무너집니다. 원문 base 기준 최대 50 토큰이며, 32 force token 이 이를 초과해 성능이 퇴행했습니다. 따라서 $`K`$ 는 용량이 아니라 **제약**이 결정합니다.
- **(RoPE 위치 보존)** — noisy-action 토큰이 base 사전학습 당시와 동일한 RoPE 위치를 유지해야 합니다. 메모리 토큰의 post-position 배치가 이를 보장합니다.
- **(장기·단기 상보성)** — 장기 힘 메모리 단독 조건화는 접촉 전 공간 인식 부재로 반복 동작을 유발하며, 원문 실험에서 memoryless base 보다도 낮은 성공률을 냈습니다. 단기 proprioception 윈도우 병용은 선택이 아니라 **안정성 조건**입니다.
- **(posterior 비붕괴)** — 접촉 사건은 희소하므로 KL 항이 잠재를 사전분포로 눌러버릴 위험이 큽니다. 차원별 free-bits 하한이 이를 막는 필수 항입니다.
- **(전역 정규화 통계)** — quantile 정규화 통계가 **데이터셋 전체** 기준이어야 인코더의 task-agnostic 성격이 유지됩니다. 과제별 통계로 바꾸면 잠재 공간이 과제 정보를 우회 획득합니다.
- **(단일 스트림 대표성 — 잠정)** — 양팔 로봇임에도 오른손목 wrench 하나가 전체 접촉 사건을 대표한다고 가정합니다. 원문이 이 가정을 명시적으로 검증하지 않았습니다.

---

## 📊 하이퍼파라미터·손실

**Stage 1 손실 (식 4)** — 마스크 재구성 + 차원별 free-bits KL:

$$\mathcal{L}_{\text{VAE}}=\frac{1}{\sum_{\tau}m_{\tau}\cdot d_{f}}\sum_{\tau=1}^{T}m_{\tau}\|f_{\tau}-\hat{f}_{\tau}\|^{2}\;+\;\beta\cdot\frac{1}{Kd_{z}}\sum_{k,j}\max\!\big(D_{\text{KL}}^{(k,j)},\lambda\big)$$

**Stage 1 reparameterization (식 2)**:

$$(\mu_{k},\log\sigma_{k}^{2})=\text{Head}_{\text{VAE}}\big(\text{Enc}_{\phi}(F)_{k}\big),\quad z_{k}=\mu_{k}+\sigma_{k}\odot\epsilon_{k},\;\;\epsilon_{k}\sim\mathcal{N}(0,I)$$

**Stage 2 손실 (식 5)** — 조건만 확장된 rectified-flow 회귀 ($`a_{k}=(1-k)\,a_{0}+k\,\epsilon`$):

$$\mathcal{L}=\mathbb{E}_{a_{0},\,\epsilon,\,k}\left[\big\|v_{\theta}(a_{k},k,c_{t},Z_{f},z_{s})-(\epsilon-a_{0})\big\|^{2}\right]$$

**메모리 결합 (식 1)**:

$$h_{t}\;=\;\big[\,\underbrace{\mathrm{Enc}_{\phi}\!\big(\{f_{\tau}\}_{\tau=1}^{t}\big)}_{\text{wrench history }Z_{f}\in\mathbb{R}^{K\times d_{h}}}\;\;\|\;\;\underbrace{\mathrm{Proj}_{\psi}\!\big(\{s_{\tau}\}_{\tau=t-W+1}^{t}\big)}_{\text{state history window}z_{s}\in\mathbb{R}^{d_{h}}}\,\big]$$

| 이름 | 값 | 출처 |
|------|----|----|
| `d_f` (wrench 차원) | `6` | §3.1 |
| `K` (latent / force memory 토큰 수) | `8` | §3.2.2, Table 3, Table 4 |
| `d_z` (per-latent dim) | `96` | §E.1, Table 3 |
| hidden / latent width | `384 / 384` | Table 3 |
| encoder / decoder cross-attn depth | `2 / 2` | Table 3 |
| processor self-attn layers | `10` | Table 3 |
| encoder cross-attn heads / head-dim | `1` head, `64` | §E.1 |
| latent self-attn heads / head-dim | `8` heads, `32` | §E.1 |
| decoder cross-attn heads | `8` | §E.1 |
| Fourier PE | `32` bands, $`f_{\max}=1500`$ | §E.1, Table 3 |
| input dropout / attention dropout | `0.2` / `0.1` | Table 3 |
| EMA smoothing $`\alpha`$ | `0.3` | §E.1, Table 3 |
| noise pre-pad $`\sigma`$ / max len | `0.05` / `1000` 프레임 (≈10 s) | §E.1, Table 3 |
| KL weight $`\beta`$ | `1e-3` | Table 3 |
| free-bits $`\lambda`$ (per dim) | `0.5` nats | Table 3 |
| Stage 1 optimizer | AdamW $`(0.9,0.95)`$, grad-clip `1.0` | Table 3 |
| Stage 1 peak LR / warm-up / total | `3e-4` / `1000` / `100000` steps | Table 3 |
| Stage 1 batch / precision | `64×8 = 512` / bf16 | Table 3 |
| Stage 1 샘플링 | inverse-frequency task sampling | §3.3, §E.2 |
| base model | $`\pi_{0.5}`$ (OpenPI 공개 체크포인트 + Zhiyuan Challenge 추가 사전학습) | Table 4, §C |
| action chunk horizon `H` / action dim | `30` / `32` | Table 4 |
| flow-matching steps (eval) | `10` | Table 4 |
| state-window taps / length | `10` (stride `3`) / `0.9 s` | Table 4, §E.1 |
| image dropout (per view) | `p = 0.4` | Table 4 |
| norm. scheme | quantile $`q_{01}/q_{99}`$ | Table 4 |
| Stage 2 optimizer / peak LR | AdamW / `5e-5` (decay phase 없음) | Table 4, §D |
| Stage 2 warm-up / total / batch | `1000` / `50000` steps / global `32` | Table 4 |
| Stage 2 precision / hardware | bf16 / 8×A100 (40 GB) | Table 4 |
| 사영 초기화 | $`W_{f}`$ · $`\mathrm{Proj}_{\psi}`$ 모두 zero-init | §3.2.3, §E.3 |

---

## 🎯 평가 메트릭

- **지표** — Success Rate (%), 과제당 `18` 시행. 성공 판정은 과제 완수 **및** 안정 종료(그리퍼 개방 + 약 3초 무동작)를 모두 요구합니다.
- **과제별 성공 기준** — Task 1(Cups): 각 컵 1회 이하 들기 + 블록이 왼손에 잡힘 + 마지막 든 컵 복귀. Task 2(Buttons): 정확히 $`N`$ 회 **가청 click** 후 그리퍼 개방(과소·과다 모두 실패). Task 3(Wipe): 좌 rim→우 rim 접촉 유지 왕복 $`N`$ 회 후 그리퍼 개방(부분 왕복 불인정). $`N\in\{1,2,3\}`$ 각 6 시행.
- **비교 baseline** — $`\pi_{0.5}`$ (memoryless) · TA-VLA (단기 wrench 윈도우 + 미래 힘 예측 헤드) · $`\pi`$-MEM (MEM 의 시각 메모리 재구현).
- **달성 임계값** — 평균 `83.3%` (Cups `100.0` / Buttons `72.2` / Wipe `77.8`). baseline: $`\pi_{0.5}`$ `27.8`, TA-VLA `22.2`, $`\pi`$-MEM `53.7`.
- **ablation 임계값** — Force-only `25.9`, State-only `40.7`, GRU 인코더 `33.3`, Q-Former 인코더 `57.4`. 토큰 수 $`\{4,8,16,32\}`$ 중 `8` 이 정점(Wipe 기준).
- **효율 지표** — 추론 지연(ms, RTX 4090): base `60.7 ± 0.3`, FM-VLA `64.0 ± 0.4` (`+3.3`), $`\pi`$-MEM `99.8 ± 0.4` (`+39.1`, `K=5`) / `190.0 ± 1.0` (`+129.3`, `K=16`). **base 대비 지연 증가가 상수에 가깝다**는 것이 이 방법의 부수 계약입니다.
- **공정 비교 조건** — 모든 baseline 이 동일 데이터·동일 정규화 통계·동일 LR 스케줄·동일 batch·동일 이미지 dropout 으로 후학습되어야 합니다.

---

## ✨ 변경 의도 (intent)

기존 메모리 VLA(MemoryVLA, MEM)는 메모리를 시각·언어 토큰으로 구성하므로, 접촉은 발생했으나 화면에 변화가 남지 않는 사건(미세 이동 버튼 누름 등)을 원리적으로 관측하지 못하고, 과거 프레임 저장·어텐션 비용이 프레임 수에 비례해 커집니다. 반대로 힘을 쓰는 VLA(ForceVLA, TA-VLA)는 현재 행동과 동시간대의 **짧은 wrench 윈도우**만 조건으로 삼아, 접촉 성립 여부나 힘 크기는 알지만 에피소드 누적 이력(몇 번 눌렀는가)은 남기지 못합니다. FM-VLA 는 두 결핍이 만나는 지점을 겨냥해, proprioceptive–wrench 스트림을 **순간 조건이 아니라 장기 메모리**로 다룹니다. 핵심 장치는 두 가지입니다. 첫째, 힘 표현 학습을 정책 학습에서 분리해 시계열 **재구성** 목표로 먼저 사전학습합니다 — 복원을 강제하면 라벨 없이도 힘 크기·개시 시점·접촉 횟수 같은 거시 구조가 소수 토큰에 담기며, 이는 정책 손실만 받는 from-scratch 압축기(Q-Former)가 순간 피크에 과적합하는 문제를 우회합니다. 둘째, 결과 토큰을 액션 전문가 suffix 의 noisy-action 토큰 **뒤**에만 붙여 base 정책의 RoPE 위치와 손실식을 건드리지 않습니다. 그 결과 새 보조 손실 없이, 6차원 시계열 한 번 인코딩이라는 상수 비용(+3.3 ms)만으로 시각 메모리 대비 성공률을 크게 앞섭니다. 여기에 힘 단독 조건화가 접촉 전 반복 행동을 유발한다는 관찰에서 단기 관절 상태 윈도우 1토큰을 병용해, "장기 = 무슨 일이 있었나 / 단기 = 지금 어디로 가고 있나" 로 시간 스케일별 역할을 분담시킵니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — base 가 $`\pi_{0.5}`$ 이므로 `pi05` 가 1순위 후보이며, 플로우 매칭 액션 전문가 구조를 공유하는 `pi0` / `pi0_fast` / `smolvla` 도 차선입니다. 이식 대상은 (i) 액션 전문가 suffix 에 조건 토큰을 append 하는 경로, (ii) zero-init 사영 2개, (iii) 별도 모듈로 추가되는 Perceiver-IO Force-VAE 와 그 사전학습 스크립트입니다. 다만 **wrench 를 관찰로 싣는 데이터 경로**(LeRobotDataset 에 6축 F/T 시계열 + 에피소드 전체 이력 접근)가 표준 포맷에 없을 가능성이 크고, 이력이 프레임 단위가 아니라 **에피소드 시작부터의 가변 길이 시퀀스**라 기존 delta-timestamps 방식의 관찰 슬라이싱과 맞지 않습니다 — 실제 매핑 가능 여부는 `/implement-design` 가 판정합니다.

---

## 🚧 미해결 / 잠정

- 액션 전문가 hidden width $`d_{h}`$ 의 구체 값이 원문에 없습니다(§E.1 은 "$`\pi_{0.5}`$ base 의 액션 전문가 hidden width" 라고만 기술) — base 체크포인트에서 읽어야 합니다.
- Figure 2 캡션은 잠재 사영을 "MLP" 로, §3.2.3·§E.1 은 zero-init **선형** 레이어로 기술해 표기가 어긋납니다. 본문 쪽(선형)을 계약으로 채택하고 그림은 개념 도식으로 간주했습니다.
- 노이즈 pre-padding 길이의 정확한 분포가 "uniformly sampled up to 10 s" / "sampled uniformly with maximum length 1000 frames" 로만 기술되어, 하한이 `0` 인지 여부는 `(원문에 명시 없음 — 가정으로 메움)` 입니다(하한 0 으로 가정).
- 학습 시 wrench 이력의 배치 처리 방식(최대 길이 truncation 여부, 패딩 정렬 방향)이 명시되지 않았습니다. 마스크 $`m_{\tau}`$ 의 존재만 확인됩니다.
- 추론 시 이력이 에피소드 진행에 따라 계속 길어지는데, 인코더 재계산 주기(매 제어 스텝인지 캐싱하는지)가 명시되지 않았습니다. `+3.3 ms` 라는 상수 오버헤드는 매 스텝 재인코딩을 시사하나 본문 확언은 없습니다.
- State-only ablation 이 "동일 Perceiver-IO 를 장기 상태 이력으로 100,000 steps 학습" 이라고만 기술되어, 이때 $`d_{s}`$ 입력 차원과 정규화 스킴이 힘 쪽과 동일한지 `(원문에 명시 없음 — 가정으로 메움)` 입니다.
- 양팔 중 왼손목 wrench 를 쓰지 않는 이유(센서 부재인지 설계 선택인지)가 기술되지 않았습니다.
- 액션 정규화 통계의 산출 범위(과제별 vs 전역)는 "same normalized statistics" 로 baseline 간 동일함만 확인되고 산출 방식은 `(원문에 명시 없음 — 가정으로 메움)` 입니다.
