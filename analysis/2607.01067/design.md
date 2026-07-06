# Design — Human-Centric Transferable Tactile Pre-Training for Dexterous Robotic Manipulation

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Human-Centric Transferable Tactile Pre-Training for Dexterous Robotic Manipulation |
| 링크 | [arXiv:2607.01067](https://arxiv.org/abs/2607.01067) |
| 분석 문서 | [`analysis/2607.01067/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-07-06 |

---

## 🧮 데이터 계약

시간 축은 의미 단위로 기록합니다: `K` = 예측 horizon(action chunk 길이), `L` = tactile history 길이, `d` = tactile history stride, `V` = 카메라 뷰 수. 통일 공간 차원은 상수: $`D_{\mathrm{act}}=200`$ (통일 action 공간, 슬롯 조직), $`D_{\mathrm{tac}}=351`$ (통일 tactile 공간, 손 하나당 MANO 표면 taxel).

- **입력 — language `l`**: 토큰 시퀀스 (base VLM 토크나이저 그대로).
- **입력 — RGB `I_t`**: `(B, V, H_I, W_I, 3)`, 사전학습 `448×448` / 사후학습 `224×224`, downsample ratio 0.5 (원문 Table 9). 정규화 통계는 (원문에 명시 없음 — 가정으로 메움: base VLM 전처리 그대로).
- **입력 — proprio `s_t`**: `(B, 200)`, float — 통일 action 공간과 동일 슬롯 레이아웃(EEF pose 0–17, 그리퍼 18–19, 다지 손 20–43, 팔 관절 50–69, 모바일 베이스 70–75, MANO $`\beta`$ / $`\theta`$ 90–199; 미사용 슬롯은 padding·마스킹).
- **입력 — tactile history `O_hist`**: `(B, L, 351)`, float — $`\mathcal{O}^{\mathrm{hist}}_{t}=[o_{t-d(L-1)},\ldots,o_{t-d},o_{t}]`$ (식 1). `L`/`d` = 4/8(사전), 2/1(시뮬 사후), 4/4(실로봇 사후). 각 embodiment 의 tactile 을 MANO 표면 351-taxel 로 투영한 값. tactile 이 없는 환경은 proxy $`o_{t}^{\mathrm{proxy}}=\mathrm{padding}(s_{t}-a_{t-1})`$ 로 치환 (351 과 200 의 차이는 zero-padding).
- **출력 — action chunk `A_t`**: `(B, K, 200)`, float — $`A_{t}=[a_{t},\ldots,a_{t+K-1}]`$ (식 2). `K` = 32(사전) / 8(시뮬) / 24(실로봇).
- **출력 — future tactile `O_t^+`**: `(B, K, 351)`, float — $`O_{t}^{+}=[o_{t},\ldots,o_{t+K-1}]`$ (식 2). action 과 동일 horizon.
- **학습 내부 — flow 보간점**: 모달리티 $`m\in\{\mathrm{act},\mathrm{tac}\}`$ 별 $`x_{\tau^{m}}^{m}=(1-\tau^{m})x_{0}^{m}+\tau^{m}x_{1}^{m}`$, $`x_{0}^{m}\sim\mathcal{N}(\mathbf{0},\mathbf{I})`$, $`\tau^{m}\in[0,1]`$ (식 4). shape 는 대응 출력과 동일.
- **학습 내부 — 컨텍스트** $`H_{t,\tau}`$ : VLM hidden 공간으로 투영된 suffix 토큰 feature(proprio state + tactile 관측 + noisy action + noisy tactile 예측 토큰). hidden 차원은 (원문에 명시 없음 — 가정으로 메움: base VLM hidden dim).

정규화·스케일링: action/tactile 값의 정규화 통계 출처는 (원문에 명시 없음 — 가정으로 메움: 데이터셋 통계 기반 표준화). 손실 계산 시 padding 되었거나 사용 불가한 차원은 마스킹(§4.3 "after masking padded or unavailable dimensions").

---

## 🧰 모듈 인터페이스

```python
def project_to_unified_tactile(raw_tactile, embodiment_spec) -> Tensor:  # (B, 351)
    """embodiment 별 tactile(피에조 저항 / visuo-tactile / 3D tactile / MANO
       per-vertex pseudo-contact)을 MANO 표면 351-taxel 공간으로 투영.
       사전학습(사람 손)과 사후학습(로봇 손)의 형태학적 일관성을 보존하는
       유일한 진입점 — UniTacHand UV 매핑(891-D → validation mask → 351-D)."""

def understanding_expert(l, I_t, s_t, O_hist,
                         x_tau_act, x_tau_tac, tau) -> Tensor:  # H_{t,tau}
    """멀티모달 이해 expert (InternVL-3.5 초기화, BeingH-0.5 계승).
       query [S_Q] = 이미지·언어·proprio·tactile 관측 토큰,
       answer [S_A] = (noisy) action·tactile 예측 토큰의 VQA 식 시퀀스를
       인코딩해 flow-time 의존 컨텍스트 H_{t,tau} 를 산출."""

def mpg(H_t_tau, Z_nf_act, Z_nf_tac) -> Tensor:  # H_tilde_{t,tau}
    """Tactile-Action Manifold-Preserving Gating (식 11–15).
       1) noise-free anchor: Z_bar = MeanPool(Z_nf_*) (식 12)
       2) 공유 정규화 공간 투영: LN(E_obs(H)), LN(E_act(Z_bar_act)),
          LN(E_tac(Z_bar_tac)) (식 13)
       3) SWD: D_act, D_tac = (1/M) Σ_i ||sort(θ_iᵀĤ) − sort(θ_iᵀẐ)||² (식 14)
       4) g = exp(−D/τ_g), D = (D_act + D_tac)/2 (식 15)
       5) H̃ = H + λ[W_MPG(stopgrad(g) ⊙ E_obs(H)) + b_MPG] (식 11)"""

def action_expert(x_tau_act, tau, H_tilde) -> Tensor:   # (B, K, 200) 속도
    """flow matching 속도 예측 v_θ^act (식 6/9)."""

def tactile_expert(x_tau_tac, tau, H_tilde) -> Tensor:  # (B, K, 351) 속도
    """flow matching 속도 예측 v_θ^tac (식 6/9) — 미래 tactile 예측으로
       접촉 동역학을 명시적으로 모델링하는 본 논문의 신설 expert."""

def flow_matching_loss(v_pred, x0, x1, valid_mask) -> Tensor:  # scalar
    """L_m = E[||v_θ − (x1 − x0)||²] (식 7), 무효 차원 마스킹 후.
       총손실 L = λ_act·L_act + λ_tac·L_tac (식 8)."""
```

- 호출 흐름: `project_to_unified_tactile` → `understanding_expert` → `mpg` → (`action_expert`, `tactile_expert`) 병렬 → `flow_matching_loss` 합산. 추론 시 Euler 적분 $`x_{\tau+\Delta\tau}^{m}=x_{\tau}^{m}+\Delta\tau\cdot v_{\theta}^{m}`$ (식 10)으로 action chunk·미래 tactile 을 동시 생성.
- 사전학습(인간 H-Tac)과 사후학습(로봇)은 **동일한 모듈·동일한 공간 계약**을 사용 — 단계 간 코드 경로 분기가 없어야 하는 것이 이 시스템의 설계 원칙.

---

## ⛓️ 불변식·가정

- (가정 1) **공간 불변성** — $`D_{\mathrm{act}}=200`$, $`D_{\mathrm{tac}}=351`$ 이 사전·사후학습 전 구간에서 동일. 이 계약이 깨지면(단계별 차원 변경) human→robot prior 보존이라는 알고리즘의 존립 근거가 무효.
- (가정 2) **tactile 투영 가능성** — 어떤 embodiment 의 tactile 신호든 MANO 표면 351-taxel 로 의미를 보존하며 투영 가능하다(형태학적 대응 존재). 투영이 신호 의미를 파괴하는 센서(예: 고해상 이미지형 tactile 의 국소 텍스처)는 이 가정의 경계 사례.
- (가정 3) **선형 flow 경로** — 보간은 $`x_{\tau}=(1-\tau)x_{0}+\tau x_{1}`$, target 속도는 상수 $`u=x_{1}-x_{0}`$ (조건부 선형 flow matching). 소스 분포는 표준 정규.
- (가정 4) **게이트 범위·단조성** — $`g=\exp(-D/\tau_{g})\in(0,1]`$ 이고 $`D`$ 에 단조 감소. $`g`$ 에는 stopgrad — 게이트 경로로 gradient 가 흐르면 anchor 정렬이 자기참조적으로 붕괴.
- (가정 5) **마스킹 완전성** — 손실은 padding/사용 불가 차원을 마스킹한 뒤 계산. 미사용 action 슬롯(embodiment 별 상이)과 tactile proxy 의 zero-padding 구간이 gradient 에 기여하면 통일 공간이 노이즈 학습으로 오염.
- (가정 6) **tactile history 의 정보 보존** — stride $`d`$ 를 둔 history $`(L,d)`$ 가 "계산 부담 축소 vs 지배적 tactile 정보 보존" 을 조율한다는 가정 — 접촉 이벤트의 시간 스케일이 $`d`$ 프레임 간격보다 길어야 유효.
- (가정 7) **proxy 의 무해성** — tactile 이 없는 환경에서 $`o^{\mathrm{proxy}}=\mathrm{padding}(s_{t}-a_{t-1})`$ 치환이 이중 목적함수 구조를 보존하며 성능을 해치지 않는다(LIBERO 98.1 로 실증 — 단 이득의 증거는 아님).

---

## 📊 하이퍼파라미터·손실

**손실 (식 7–8):**

$$\mathcal{L}_{m}=\mathbb{E}_{x_{0}^{m},\tau^{m}}\left[\left\|\left(v_{\theta}^{m}(x_{\tau^{m}}^{m},\tau^{m},H_{t,\tau^{m}})-(x_{1}^{m}-x_{0}^{m})\right)\right\|_{2}^{2}\right],\qquad m\in\{\mathrm{act},\mathrm{tac}\},$$

$$\mathcal{L}=\lambda_{\mathrm{act}}\mathcal{L}_{\mathrm{act}}+\lambda_{\mathrm{tac}}\mathcal{L}_{\mathrm{tac}}.$$

**하이퍼파라미터 (원문 Table 9):**

| 이름 | 값 (Pre / Post-sim / Post-real) | 출처 |
|------|----|----|
| `learning_rate` | `1e-4` / `1e-4` / `1e-4` | §7, Table 9 |
| `weight_decay` | `1e-5` / `1e-5` / `1e-5` | §7, Table 9 |
| `warmup_ratio` | `0.05` / `0.05` / `0.05` | §7, Table 9 |
| $`\lambda_{\mathrm{act}}`$ (action loss weight) | `1.0` (전 단계) | §7, Table 9 |
| $`\lambda_{\mathrm{tac}}`$ (tactile loss weight) | `1.0` (전 단계) | §7, Table 9 |
| `max_num_tokens` | `8192` (전 단계) | §7, Table 9 |
| `expected_num_tokens` | `7680` (전 단계) | §7, Table 9 |
| `equivalent_batch_size` | `128` (전 단계) | §7, Table 9 |
| `image_size` | `448×448` / `224×224` / `224×224` | §7, Table 9 |
| `downsample_ratio` | `0.5` (전 단계) | §7, Table 9 |
| `action_chunk_size` (`K`) | `32` / `8` / `24` | §7, Table 9 |
| `tactile_history_size` (`L`) | `4` / `2` / `4` | §7, Table 9 |
| `tactile_history_stride` (`d`) | `8` / `1` / `4` | §7, Table 9 |
| $`D_{\mathrm{act}}`$ | `200` | §4.2 |
| $`D_{\mathrm{tac}}`$ | `351` (손 하나당) | §4.2 |
| $`\tau_{g}`$ (게이트 온도) | (원문 미명시) | §4.4, Eq. (15) |
| `M` (SWD 투영 수) | (원문 미명시) | §4.4, Eq. (14) |
| $`\lambda`$ (MPG 잔차 가중) | (원문 미명시) | §4.4, Eq. (11) |
| optimizer 종류 | (원문 미명시) | — |
| 사전학습 총 스텝 | (원문 미명시 — ablation 은 150k 스텝 기준) | §5.4 |

---

## 🎯 평가 메트릭

- **사전학습 검증 (motion 예측)** — 지표: `MPJPE`, `PA-MPJPE`, `MPJAE`, `PA-MPJAE` (낮을수록 좋음) · 비교 baseline: TTP w/o MPG / w/o tac-pred 변형 · 목표선: MPJPE `23.5711` (full model, 150k 스텝).
- **시뮬 벤치마크** — 지표: 성공률(%) · LIBERO(task 당 50 에피소드) / LIBERO-plus(zero-shot, 카테고리당 70 trial) / RoboCasa(24 task ×50 trial) · 비교 baseline: BeingH-0.5, $`\pi_{0.5}`$, $`\pi_{0}`$ 등 · 목표선: LIBERO Avg `98.1`, LIBERO-plus Avg `75.7`, RoboCasa Avg `55.1`.
- **실로봇** — 지표: Peeling = 벗긴 껍질 평균 길이(cm), PaperFolding = 접힌 길이 비율(%), 나머지 = 성공률(%) · ID 10 trial + OOD 5 trial · 비교 baseline: $`\pi_{0.5}`$ (+tactile 변형), BeingH-0.5, TTP w/o pre-train · 목표선(카테고리 평균 진행률): Fine-grained `96.7%`, Contact-rich & Fragile `79.2%`, Vision Defect `37.8%`.

---

## ✨ 변경 의도 (intent)

기존 tactile×VLA 연구(VTLA 계열)는 tactile 을 post-training 단계에서만 주입해, 사전학습이 만들어 둔 표현과 tactile 사이의 정렬을 소량의 로봇 데이터가 떠안았습니다. 본 설계의 의도는 그 정렬을 **사전학습 단계로 앞당기는 것**입니다: (i) 인간 egocentric 시연에 tactile·action 을 정렬한 대규모 corpus(H-Tac)로 VLA 를 사전학습해 tactile-grounded prior 를 확보하고, (ii) 통일 action 공간(200-D)·통일 tactile 공간(MANO 표면 351-taxel)을 사전·사후학습에서 동일하게 유지해 human→robot 전이 시 그 prior 가 깨지지 않게 하며, (iii) action expert 와 대칭인 tactile expert 가 미래 tactile 을 flow matching 으로 예측하게 해 접촉 동역학을 명시적 학습 신호로 만들고, (iv) action·tactile 이중 anchor 의 SWD 게이트(MPG)로 분포 이동 시 컨텍스트 보정을 자동 감쇠시킵니다. prior art 대비 핵심 차별은 "tactile 융합 구조의 정교화" 가 아니라 "tactile 이 든 사전학습 자체" — 구조는 단순한 token-append 로 두고 규모와 공간 일관성으로 승부하는 설계입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 후보 base: `pi05` / `pi0` family 가 가장 가깝습니다(VLM backbone + flow matching action expert, 후자는 본 설계의 action expert 와 동형). tactile expert 는 action expert 와 같은 flow matching head 의 두 번째 인스턴스(출력 차원 351×K)로 증설하는 그림. 단 (i) tactile 관측 모달리티(351-D history)와 (ii) 200-D 통일 action 공간은 lerobot 표준 LeRobotDataset 스키마에 없어 processor·feature 정의 확장이 필요하고, (iii) understanding expert 의 InternVL-3.5 lineage 는 lerobot 의 PaliGemma 계열과 달라 checkpoint 이식은 불가 — 레시피(이중 flow 목적 + tactile proxy) 수준의 매핑이 현실적입니다.

---

## 🚧 미해결 / 잠정

- MPG 세부 미명시 — 게이트 온도 $`\tau_{g}`$, SWD 투영 수 `M`, 잔차 가중 $`\lambda`$ 의 값이 본문·부록 어디에도 없음. $`\mathcal{E}_{\mathrm{obs}}/\mathcal{E}_{\mathrm{act}}/\mathcal{E}_{\mathrm{tac}}`$ 인코더의 구조(MLP 여부·차원)도 미명시.
- tactile 관측 토큰의 임베딩 방식 미명시 — 351-D 벡터 ×L 프레임이 몇 개의 토큰으로, 어떤 인코더를 거쳐 시퀀스에 들어가는지 본문에 없음 (BeingH-0.5 관례를 따르는 것으로 추정되나 가정임).
- 양손 태스크의 tactile 차원 처리 미명시 — $`D_{\mathrm{tac}}=351`$ 은 "손 하나당" 인데 bimanual 태스크(VaseWiping bimanual, PaperFolding)에서 2×351 인지 단일 351 인지 본문이 특정하지 않음.
- optimizer 종류·본 학습 총 스텝·GPU 하드웨어 미명시 (ablation 만 150k 스텝 명시).
- action/tactile 값의 정규화 통계(평균/표준편차의 산출 범위) 미명시 — 데이터셋 전체 통계로 가정.
- understanding expert 크기(InternVL-3.5 의 파라미터 규모 변형) 미명시 — BeingH-0.5 구성을 따르는 것으로 가정.
- 추론 시 Euler 적분 스텝 수 미명시.
