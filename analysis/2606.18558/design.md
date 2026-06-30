# Design — MolmoMotion: Forecasting Point Trajectories in 3D with Language Instruction

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | MolmoMotion: Forecasting Point Trajectories in 3D with Language Instruction |
| 링크 | [arXiv:2606.18558](https://arxiv.org/abs/2606.18558) |
| 분석 문서 | [`analysis/2606.18558/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-30 |

---

## 🧮 데이터 계약

시간 축은 의미 단위로 기록합니다 — `H`(history length, ∈{1,3}), `T`(prediction horizon, 1단계 8 / 2단계 32), `N`(객체당 query point 수, 기본 8) `15 fps`.

- **입력 — RGB 이력** $`I_{t_s:t_0}`$: shape `(B, H, 3, 378, 378)`, SigLIP2 정규화. Molmo2 video preprocessor 가 image token 으로 인코딩.
- **입력 — 2D query points** `q`: shape `(B, N, 2)`, anchor 프레임 픽셀 좌표. anchor feature map $`F_{t_0}`$ 에서 bilinear sampling 해 point feature token `(B, N, d_lm)` 생성.
- **입력 — 초기 3D query 좌표** $`\mathbf{p}_{t_0}`$: shape `(B, N, 3)`, dtype float, **metric meter**, `t0` 카메라 프레임. AR 은 anchor-relative delta 를 mm 양자화 텍스트로, FM 은 연속값으로 인코딩.
- **입력 — 언어 명령** `a`: 가변 길이 text token.
- **출력 — 미래 3D 궤적**: anchor-relative delta $`\boldsymbol{\delta}`$, shape `(B, N, T, 3)`, metric meter. AR 변종은 시간순 직렬화 텍스트( $`y_{1:L}`$, mm 정수), FM 변종은 연속 `(N, T, 3)`.
- **정규화** — 모든 좌표를 첫 query point $`\mathbf{p}_{\mathrm{anc}} = \mathbf{p}_{t_0}^{1}`$ 기준 상대 $`\boldsymbol{\delta}_t^n = \mathbf{p}_t^n - \mathbf{p}_{\mathrm{anc}}`$. world frame 은 `t0` 카메라에 고정(미래 카메라 모션과 독립). AR 양자화: $`\mathrm{round}(1000\cdot\boldsymbol{\delta})`$ (mm bin). per-dataset 정규화 통계는 사용하지 않음(좌표가 이미 metric meter).

---

## 🧰 모듈 인터페이스

```python
def encode_inputs(images, text, q2d) -> Context:
    """RGB 이력·언어·2D query 점을 Molmo2 backbone 토큰열 C=[T_img, T_text, T_pt] 로 인코딩.
       T_pt[n] = bilinear_sample(F_{t0}, q2d[n])."""

def ar_decode(C, init_coords_text) -> str:
    """AR 변종: C + 직렬화된 초기 3D query 좌표 → 미래 궤적 문자열 y_{1:L} (next-token, greedy).
       정규식 파서가 (n, qx, qy, qz) mm 정수 quadruple 을 P_hat 으로 재조립."""

def fm_velocity(delta_tau, tau, init_delta, C) -> Tensor:  # (N, T, 3)
    """FM 변종 DiT trajectory expert (LM 층당 1 block, 총 36).
       block: self-attn over (N, H+T, 3) → cross-attn(keys/vals = 해당 LM 층 hidden).
       RoPE 를 point-index·frame-index 양축에 적용. tau 는 sinusoidal embedding 으로 주입."""

def fm_sample(C, init_delta, K=10) -> Tensor:  # (N, T, 3)
    """eps~N(0,I) 에서 K Euler step 으로 velocity field 적분(Δτ=0.1) → δ_1, p_anc 더해 복원."""
```

- **encode_inputs** — backbone(Molmo2-4B: SigLIP2 ViT + Qwen3-4B LM)으로 멀티모달 컨텍스트 생성. 두 디코더가 공유.
- **ar_decode** — Molmo2 LM head(미수정) + 추론 시 좌표 파서. 손실은 answer span 에만(다음 §).
- **fm_velocity / fm_sample** — DiT expert. 한 번의 velocity 평가가 캐시된 LM activation 재사용 → Euler step 1회 ≈ LM forward 1회.

---

## ⛓️ 불변식·가정

- **(가정 1)** Anchor-relative 파라미터화 — 모든 좌표는 `p_anc` 기준 상대값. 전역 위치 오프셋 제거가 핵심이며, 절대 좌표로 바꾸면 ADE/FDE 가 전 split 에서 약 50% 악화(설계의 최대 단일 기여).
- **(가정 2)** World frame 은 `t0` 카메라에 고정 → 예측이 미래 카메라 모션과 독립(view-stable).
- **(가정 3)** Metric scale — `1 unit = 1 m`. supervision 자체가 ViPE metric depth lift 에서 옴(추정치이므로 라벨 노이즈 존재).
- **(가정 4)** 가시성 — 시각 `t` 에 보이는 점만 출력/채점, 가려진 점은 imputation 하지 않음.
- **(가정 5)** AR answer span 길이 ∝ `N·T` 가 backbone context(Qwen3-4B 4096 token) 이내여야 함 → 기본 `N=8`, `T=32`. 초과 시 dense·long-horizon 불가.
- **(가정 6)** 객체 점들은 한 물리 entity 의 일부로 coherent 하게 움직인다(주석 필터/스무딩의 전제).

---

## 📊 하이퍼파라미터·손실

- **FM 손실** (식 4): 회귀 타깃 = clean − noise (직선 경로 속도), 미래 위치에만 마스킹.

$$\mathcal{L}_{\mathrm{FM}}=\mathbb{E}_{\tau,\,\epsilon}\!\left[\,\left\|v_{\phi}\!\left(\boldsymbol{\delta}_{\tau},\,\tau,\,\{\boldsymbol{\delta}_{t_{0}}^{n}\}_{n=1}^{N},\,\mathcal{C}\right)-\bigl(\boldsymbol{\delta}_{t_{0}+1:t_{0}+T}-\epsilon\bigr)\right\|_{2}^{2}\,\right]$$

- **AR 손실** — 표준 next-token cross-entropy, answer span 에만 계산(prompt 토큰 마스킹).
- **보간** (식 3): $`\boldsymbol{\delta}_\tau = (1-\tau)\cdot\epsilon + \tau\cdot\boldsymbol{\delta}_{t_0+1:t_0+T}`$, $`\tau\sim\mathcal{U}(0,1)`$.

  | 이름 | 값 | 출처 |
  |------|----|----|
  | optimizer | AdamW ( $`\beta_1=0.9`$, $`\beta_2=0.95`$, wd `0.1`) | §D.3 |
  | LR schedule | 1K step linear warmup → cosine to `0.1×` peak | §D.3 |
  | peak LR | `(원문 미명시)` | §D.3 |
  | grad clip | max-norm `1.0` | §D.3 |
  | precision | bf16 activation + fp32 master | §D.3 |
  | 분산 | FSDP2 full-shard, 16× H100, per-device batch `16`, global `256` | §D.3 |
  | dataset mixing | clip 수 square-root 가중 (6 소스) | §D.3 |
  | stage 1 | 40K step, `N=8`, `T=8`, `H=3`, 15 fps (예제당 64 타깃) | §4.1 |
  | stage 2 | 10K step, `T=32`, $`H\in\{1,3\}`$ 두 변종 | §4.1 |
  | FM 추론 | `K=10` Euler step, $`\Delta\tau=0.1`$ | §2.2, §D.4 |
  | AR 양자화 | $`\mathrm{round}(1000\cdot\boldsymbol{\delta})`$ (mm bin) | §2.2 |
  | DiT | 36 block (LM 층당 1), point·time 양축 RoPE | §D.1 |

---

## 🎯 평가 메트릭

- **지표** — `ADE↓` (전 가시 점·시각 평균 변위, m) · `FDE↓` (마지막 시각 변위, m) · `mean PWT↑` (임계 $`\delta\in\{0.01,0.02,0.05,0.10,0.20\}`$ m 내 비율 평균) · **임계값** — best-of-5 평가, `1 unit = 1 m` · **비교 baseline** — Static / Extrapolate / Wan2.2-5B / Cosmos-Predict / ObjectForesight / EgoScaler / Robot4DGen / Track2Act.
- 최고치: MolmoMotion-AR(`H=3`) HOT3D ADE `0.109` / FDE `0.217` / PWT `0.444`. 전이: MolmoSpaces 최종 성공률 56.0%→76.3%(backbone init 만 교체).

---

## ✨ 변경 의도 (intent)

객체 부착 3D world-frame point 를 **class-agnostic · view-stable · compact** 한 모션 예측 타깃으로 삼아, 픽셀 생성(비싸고 downstream 재추출)·parametric pose(카테고리 템플릿)·2D track(카메라 ego-motion 과 얽힘)의 한계를 동시에 피합니다. 좌표는 anchor-relative metric delta + 언어 goal 조건으로 표현하고, **상보적 두 디코더**(AR = 결정론·매끄러움, FM = 다봉 분포·고속)를 둡니다. 결정적 차별점은 이 모션 예측을 **사전학습 과제**로 두어 학습된 prior 를 **backbone 초기화만으로** 로봇 매니퓰레이션·영상 생성으로 전이한다는 점입니다 — 객체의 3D 운동이 embodiment 에 비교적 무관하다는 가정에 기댑니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — FM trajectory expert(VLM backbone + flow-matching 디코더, K Euler step)는 `pi0`/`pi05`/`smolvla` 의 flow-matching action expert family 와 구조적으로 가장 가깝습니다. 단 (1) backbone 이 Molmo2(Qwen3-4B+SigLIP2)로 PaliGemma 계열과 다르고, (2) 예측 타깃이 robot action 이 아니라 **3D point track** 이며, (3) AR 좌표-as-text 디코딩은 lerobot 에 직접 대응이 없습니다(가장 가까운 것은 `pi0_fast` 의 토큰화 action). 따라서 정책 foundry 로의 drop-in 이 아니라 **부분 매핑/`UNMAPPABLE` 가능성**이 큼 — `/implement-design` 가 판정.

---

## 🚧 미해결 / 잠정

- **peak LR 값** — `(원문에 명시 없음 — 가정으로 메움)`: warmup/cosine schedule 만 기술되고 peak 절대값 미기재.
- **DiT hidden width / coordinate MLP 차원** — `(원문에 명시 없음)`: "lightweight MLPs for coordinate encoding/decoding" 으로만 기술.
- **point-token 특수 토큰 포맷** — 프롬프트 예시(`<points anchor n ...>`, `<tracks coords=...>`)는 §D.2 에 부분 제공되나 전체 vocab/포맷은 코드 의존.
- **query point 샘플링** — K-means cluster center 로 `N` 점, 필터 후 median 88 점(범위 60–100) 중 학습은 `N=8` 사용. 8점 선택의 결정 규칙(어느 8개)은 본문에 명시적 알고리즘 없음.
