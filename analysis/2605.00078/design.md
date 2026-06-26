# Design — Being-H0.7: A Latent World-Action Model from Egocentric Videos

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Being-H0.7: A Latent World-Action Model from Egocentric Videos |
| 링크 | [arXiv:2605.00078](https://arxiv.org/abs/2605.00078) |
| 분석 문서 | [`analysis/2605.00078/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-26 |

---

## 🧮 데이터 계약

- **입력 (컨텍스트)**
  - 언어 지시 $`x`$: 텍스트 토큰 시퀀스
  - 관찰 히스토리 $`o_{-H:0}`$: shape `(B, H, C, 224, 224)`, uint8, 정규화 후 `float32` (H=4, RGB)
  - 로봇 상태 $`s`$: shape `(B, D_state)`, `float32` (DoF에 따라 가변 — proprioception)
  - 잠재 쿼리 $`Q`$: shape `(B, K, d)`, `float32`, K=16, d=모델 은닉 차원 (학습 파라미터)
  - 노이즈 행동 $`a_t`$: shape `(B, T, D_action)`, `float32`, T=20

- **입력 (사후 분기 — 훈련 전용)**
  - 미래 관찰 $`\tilde{o}_{0:T}`$: shape `(B, T_future, C, 256, 256)`, uint8, 정규화 후 `float32` (RGB)
  - 미래 임베딩 $`z^{\mathrm{post}}`$: shape `(B, K, d)`, `float32` (Perceiver Resampler 출력)

- **출력**
  - 예측 속도장 $`v_\theta`$: shape `(B, T, D_action)`, `float32` (flow-matching 행동 헤드)
  - 추론 시: 사전 분기 속도장만 출력; ODE 적분으로 행동 청크 복원

- **정규화 가정**: 컨텍스트 이미지 `224×224`, 미래 프레임 `256×256` (원문 명시). 상태·행동 정규화 통계는 원문에 명시 없음 — 데이터셋 전체 평균/표준편차로 가정.

---

## 🧰 모듈 인터페이스

```python
class LatentWorldActionModel:
    """
    Being-H0.7: Latent World-Action Model.
    사전 분기(prior branch)와 사후 분기(posterior branch)를
    단일 MoT 시퀀스에 패킹하여 학습한다.
    추론 시에는 사전 분기만 실행.
    """
    def forward_train(
        self,
        context: dict,           # {instruction, obs_history, state}
        action_noisy: Tensor,    # (B, T, D_action) — 노이즈 행동 a_t
        future_obs: Tensor,      # (B, T_future, C, 256, 256) — 미래 관찰
        flow_time: Tensor,       # (B,) — t in [0,1]
    ) -> dict:
        """훈련: L_FM + L_align + L_reg 반환."""

    def forward_inference(
        self,
        context: dict,           # {instruction, obs_history, state}
    ) -> Tensor:
        """추론: 사전 분기만 실행. 행동 청크 반환 (B, T, D_action)."""
```

```python
class FutureEncoder:
    """
    동결된 ViT(V-JEPA2.1) + Perceiver Resampler.
    미래 관찰 시퀀스를 K개 임베딩으로 압축.
    """
    def encode(
        self,
        future_obs: Tensor,  # (B, T_future, C, H, W)
        K: int,              # 잠재 쿼리 수와 동일
        d: int,              # 은닉 차원
    ) -> Tensor:             # z_post: (B, K, d)
        ...
```

```python
def dual_branch_attention_mask(
    seq_len_context: int,
    seq_len_prior: int,      # K (잠재 쿼리)
    seq_len_posterior: int,  # K (미래 임베딩, = K)
    seq_len_action: int,     # T
) -> Tensor:
    """
    컨텍스트 토큰은 양쪽 분기에 보임.
    사전/사후 branch 전용 토큰은 서로 attend 불가.
    """
```

```python
def latent_alignment_loss(
    h_prior: list[Tensor],   # len=L, each (B, K, d)
    h_post: list[Tensor],    # len=L, each (B, K, d)
    L: int,                  # 정렬 레이어 수 (=9)
) -> Tensor:
    """L_align = (1/L) Σ_l (1/|h_l|) ||h_l^prior - h_l^post||_F^2"""
```

```python
def anti_collapse_regularization(
    h: Tensor,       # 잠재 은닉 상태 (B, K, d)
    tau: float,      # 노름 임계값
    n: int,          # 랜덤 투영 차원
    w_norm: float,   # = 1e-4
    w_rank: float,   # = 1e-4
) -> Tensor:
    """L_reg = w_norm * R_norm + w_rank * R_rank"""
```

---

## ⛓️ 불변식·가정

- **잠재 쿼리-미래 임베딩 구조 대응** — $`K`$ 와 $`d`$ 가 두 분기에서 동일해야 잠재 정렬 손실이 의미 있습니다.
- **동일 위치 ID** — 사전 분기 잠재 쿼리와 사후 분기 미래 임베딩 위치에 동일한 positional ID를 할당해야 레이어별 구조적 정렬이 보장됩니다.
- **공유 컨텍스트 불변** — 사전·사후 분기가 동일한 컨텍스트 토큰을 공유하며, 이 토큰에 가해지는 gradient는 두 분기 목표를 모두 반영합니다.
- **미래 프레임 인코더 동결** — V-JEPA2.1 미래 프레임 인코더는 학습 중 동결(컨텍스트 프레임 인코더는 학습 가능). 이 가정이 깨지면 사후 분기의 미래 임베딩이 불안정해집니다.
- **플로우 매칭 경계 조건** — $`t=0`$ 에서 $`a_t = \epsilon \sim \mathcal{N}(0,I)`$, $`t=1`$ 에서 $`a_t = a`$ (정답 행동). 이 선형 보간 가정이 성립해야 속도장 예측이 유효합니다.
- **정규화 목적의 분리** — $`\mathcal{R}_{\mathrm{norm}}`$ 은 크기 소실 방지, $`\mathcal{R}_{\mathrm{rank}}`$ 는 방향 붕괴 방지. 두 정규화자는 trivial solution(모든 잠재 쿼리가 동일한 zero 벡터로 수렴)을 제거합니다.

---

## 📊 하이퍼파라미터·손실

**손실 함수**

**플로우 매칭 (식 4)**

$$\mathcal{L}_{\mathrm{FM}}=\left\|v_{\theta}^{\mathrm{prior}}(a_{t},c,q)-u_{t}\right\|_{2}^{2}+\left\|v_{\theta}^{\mathrm{post}}(a_{t},c,z^{\mathrm{post}})-u_{t}\right\|_{2}^{2}$$

**잠재 정렬 (식 3)**

$$\mathcal{L}_{\mathrm{align}}=\frac{1}{L}\sum_{\ell=1}^{L}\frac{1}{|h_{\ell}|}\left\|h_{\ell}^{\mathrm{prior}}-h_{\ell}^{\mathrm{post}}\right\|_{F}^{2}$$

**최종 목표 (식 8)**

$$\mathcal{L}=\mathcal{L}_{\mathrm{FM}}+w_{\mathrm{align}}\mathcal{L}_{\mathrm{align}}+w_{\mathrm{norm}}\mathcal{R}_{\mathrm{norm}}+w_{\mathrm{rank}}\mathcal{R}_{\mathrm{rank}}$$

**하이퍼파라미터**

| 이름 | 값 | 출처 |
|------|----|----|
| $`K`$ (잠재 쿼리 수) | `16` | §4.1 |
| $`H`$ (관찰 호라이즌) | `4` | §4.1 |
| $`T`$ (행동 청크 길이) | `20` | §4.1 |
| $`L`$ (정렬 레이어 수) | `9` (마지막 9개) | §4.1 |
| $`w_{\mathrm{align}}`$ | `1e-3` | §4.1 |
| $`w_{\mathrm{norm}}`$ | `1e-4` | §4.1 |
| $`w_{\mathrm{rank}}`$ | `1e-4` | §4.1 |
| $`\tau`$ (노름 임계값) | (원문에 명시 없음 — 가정으로 메움) | §3.3 |
| $`n`$ (랜덤 투영 차원) | (원문에 명시 없음 — 가정으로 메움) | §3.3 |
| 컨텍스트 이미지 크기 | `224×224` | §4.1 |
| 미래 프레임 크기 | `256×256` | §4.1 |
| 글로벌 배치 크기 | $`\approx 128`$ 궤적 청크 | §4.1 |
| 다운스트림: $`\mathcal{L}_{\mathrm{reg}}`$ 적용 | 미적용 | §4.1 |
| 옵티마이저 상세 | (원문에 명시 없음 — 가정으로 메움) | — |

---

## 🎯 평가 메트릭

- **지표** — 태스크 성공률(%) · **비교 baseline** — Being-H0.5, π0.5, Fast-WAM
- **시뮬레이션 주요 지표**:
  - LIBERO: 4개 suite 평균 성공률(500 trials/suite)
  - RoboCasa-50: 24개 태스크 평균 성공률(50-shot, 50 trials/task, 비가시 씬)
  - GR1: 24개 태스크 평균 성공률(50 trials/task)
  - LIBERO-plus: zero-shot 및 fine-tuned 성공률
  - CALVIN: 5개 연속 명령 중 평균 완료 수(1000 시퀀스 기준)
  - RoboTwin 2.0: Easy/Hard 설정 성공률(100 rollouts/task)
- **실제 로봇 평가**: 과제당 20회 블라인드 평가, 5개 능력별 suite 평균 성공률
- **추론 비용**: ms/step (UAC 적용 기준, 3–4 ms/step 목표)

---

## ✨ 변경 의도

Being-H0.7은 기존 VLA(현재 관찰 → 행동 직접 매핑)와 픽셀 기반 세계-행동 모델(미래 프레임 생성 → 행동) 사이의 제3의 경로를 제안합니다. 핵심 변경은 두 가지입니다.

첫째, **잠재 추론 공간의 명시적 삽입** — 학습 가능한 잠재 쿼리를 인식과 행동 사이에 배치하여, Transformer 전파 과정에서 행동-지향 중간 표현이 점진적으로 형성됩니다. 이는 기존 VLA의 "관찰→행동 단축 매핑" 문제를 구조적으로 해결하면서도 추론 비용을 추가하지 않습니다.

둘째, **훈련 전용 사후 분기를 통한 미래-인식 학습** — 픽셀 생성 없이 미래 관찰 임베딩이 잠재 쿼리를 지도함으로써, 세계 모델의 예측적 이점을 VLA의 배포 효율성과 결합합니다. 이는 Fast-WAM(테스트 시 롤아웃 제거 + 비디오 생성 훈련 유지)과 달리 훈련 시에도 픽셀 생성 비용을 피합니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — Being-H0.5 기반 MoT 구조이며, lerobot의 현재 policy 계열(pi0, pi05, act 등)과 직접 대응이 어렵습니다. 가장 가까운 base는 `pi0` (flow-matching 행동 헤드, 멀티모달 컨텍스트)이나, MoT 구조 + 이중 분기 + 잠재 쿼리 삽입은 lerobot에 없는 구조이므로 상당한 커스텀 구현이 필요합니다.

---

## 🚧 미해결 / 잠정

- **노름 임계값 $`\tau`$** — 원문에 명시 없음. anti-collapse 정규화 효과에 중요하나 구체적 값을 알 수 없습니다.
- **랜덤 투영 차원 $`n`$** — 스펙트럼 다양성 계산에 사용되나 원문 미명시.
- **옵티마이저 및 학습률 스케줄** — 원문에 명시되지 않아 Being-H0.5 설정에서 이어받은 것으로 추정하나 확인 불가.
- **$`K`$ 민감도** — $`K=16`$ 에 대한 아블레이션 없음. 더 복잡한 손 조작(22 DoF)에 충분한지 불명확.
- **$`L=9`$ 정렬 레이어 선택 근거** — 마지막 9개 레이어를 선택한 설계 이유가 논문에 제시되지 않아 전이 시 재조정 필요 가능성.
- **미래 프레임 수 $`T_{\mathrm{future}}`$** — 행동 청크 길이 $`T=20`$ 과의 관계 미명시. 사후 분기가 참조하는 미래 프레임의 실제 수가 불명확.
- **다운스트림 사후학습 시 잠재 정렬 손실 가중치** — 파인튜닝 시 $`w_{\mathrm{align}}`$ 를 동일하게 유지하는지 또는 조정하는지 원문 미명시.
