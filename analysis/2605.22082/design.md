# Design — CoRMA: Contrastive RMA for Contact-Rich Meta-Adaptation

> PROBE design 산출물 (Layer 1, vendor-agnostic). 단일 한글 문서이며,
> 영문 1차 파일은 없습니다. `/analyze-paper` 가 `analysis/<id>/analysis.md` 와
> 함께 자동 생성하며, 알고리즘 명세를 base 좌표계 없이 추출합니다.
> base 매핑은 `/foundry` 단계에서 진행합니다. 형식·이모지·용어 규칙은
> `docs/STYLE.md` §6 / §4 를 정확히 따릅니다. 재실행 시 이 파일을
> 덮어씁니다.

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | CoRMA: Contrastive RMA for Contact-Rich Meta-Adaptation |
| 링크 | [arXiv:2605.22082](https://arxiv.org/abs/2605.22082) |
| 분석 문서 | [`analysis/2605.22082/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-05-26 |

---

## 🧮 데이터 계약

CoRMA 의 학습·배포 단계별 텐서 계약입니다. 시간 축은 `H` (history length, 원문에서 구체 값 미명시) 와 step `t` 로 표기합니다.

- **입력 (Stage 1 교사)** — `o_t`: deployable observation. shape `(B, D_obs)`, dtype `float32`, normalization 원문 미명시. 구성: proprioception + 6-axis force/torque + force-threshold flag + previous action. 교사 학습 시에만 `z_t` (Privileged $`Z`$) 가 concat 되어 `(B, D_obs + 6)`.
- **입력 (Stage 2 adapter)** — `(o_{t-H+1:t}, a_{t-H+1:t})`: 시계열 history window. shape `(B, H, D_obs)` 와 `(B, H, D_act)`, dtype `float32`. history 길이 `H` 와 sampling 전략 (전체 trajectory 에서 windowed sampling) 만 명시되고 구체 값은 (원문에 명시 없음 — 가정으로 메움).
- **입력 (Stage 3 배포)** — deploy 시 `o_t` 만 사용, oracle `z_t` 는 제거. adapter 가 history 로부터 `\hat{z}_t` 추론.
- **출력 (privileged Z)** — `z_t`: shape `(B, 6)`, dtype `float32`. 차원 정의: `[onset, lateral, guided, dir_x, dir_y, jam]`. 시뮬레이터 contact·force 동역학에서 계산. 정규화 가정 (원문에 명시 없음 — 가정으로 메움).
- **출력 (adapter)** — `\hat{z}_t`: shape `(B, 6)`, dtype `float32`. policy 가 받는 conditioning. `u_t`: shape `(B, D_u)` (`D_u` 원문 미명시), contrastive head 의 표현 벡터, policy 에 미전달.
- **출력 (policy action)** — `a_t`: shape `(B, D_act)`. FORGE 원본 6-DoF Franka task-space action 인터페이스를 따르며 Marvin 7-DoF 으로 옮길 때 robot-specific 제어 인터페이스만 교체. 구체 차원은 (원문에 명시 없음 — 가정으로 메움).
- **부가 라벨** — `c_t`: 4-class force-regime label `{free, first_contact, guided_slide, jam}`. dtype `int32` 또는 one-hot. deployable force evidence 에서 산출, contrastive positive/negative 짝짓기 전용.

---

## 🧰 모듈 인터페이스

```python
def privileged_teacher_policy(o_t, z_t) -> a_t:
    """Stage 1 교사 정책 — observation + 6D Privileged Z conditioning."""

def deployment_policy(o_t, z_hat_t) -> a_t:
    """Stage 3 배포 정책 — adapter 가 추론한 z_hat_t 를 oracle 자리에 주입."""

def corma_adapter(o_hist, a_hist) -> (z_hat_t, u_t):
    """deployable history → (semantic context z_hat_t, contrastive embedding u_t).

    구현체:
      h_t = causal_transformer(o_hist, a_hist, readout_token)
      z_hat_t = semantic_head(h_t)   # 6D regression
      u_t     = contrastive_head(h_t) # InfoNCE embedding
    """

def semantic_regression_loss(z_hat_t, z_t) -> scalar:
    """L2 회귀 손실."""

def force_regime_infonce_loss(u_t, u_pos, u_neg_set, tau) -> scalar:
    """force-regime 라벨 기반 InfoNCE. cosine similarity, temperature tau."""

def stage2_loss(z_hat_t, z_t, u_t, u_pos, u_neg_set, tau, lambda_nce) -> scalar:
    """L_adapter = L_sem + lambda_nce * L_nce."""
```

- 교사 / 배포 policy 는 동일 구조이며 conditioning 차원 (`z_t` vs `\hat{z}_t`) 만 다릅니다. RL-Games PPO 인터페이스를 따릅니다.
- adapter 의 readout token 은 learned 이고, causal Transformer 인코더의 마지막 토큰 표현 `h_t` 가 두 head 의 분기점입니다.
- 두 head 는 독립 MLP 로 가정합니다 (원문 도식만 제공, 정확한 layer 구성은 명시 없음).
- contrastive 짝짓기는 task identity 를 무시하고 label 만 씁니다. negative set $`\mathcal{N}_t`$ 의 sampling 전략 (in-batch vs queue) 은 (원문에 명시 없음 — 가정으로 메움).

---

## ⛓️ 불변식·가정

- (가정 1) 관련 assembly 과제 (PegInsert, GearMesh, NutThread) 는 *공유 가능한 semantic contact structure* 를 띤다. 6D Privileged $`Z`$ 가 task 간 적응 인터페이스로 충분하다는 핵심 가설.
- (가정 2) deployable force / proprio / action history 만으로 `z_t` 의 의미 단위 정보를 추론할 수 있다. 다시 말해 force evidence 가 contact regime 의 충분 통계 역할을 한다는 뜻인 셈이다.
- (가정 3) force-regime 4-라벨 (`free / first_contact / guided_slide / jam`) 은 정확한 물리 상태 추정이 아니라 *coarse* contrastive 짝짓기 규칙. label noise 가 있어도 InfoNCE 의 representation 구조화 효과는 살아남는다는 가정.
- (가정 4) Stage 3 에서 policy 의 동작 분포는 oracle `z_t` 와 adapter 예측 `\hat{z}_t` 가 충분히 가까울 때 보존된다. 다시 말해 adapter regression error 가 policy 성능 저하 임계 밑이라는 암묵 가정이며, fine-tuning 단계가 이 mismatch 를 흡수한다.
- (가정 5) adapter 는 frozen 으로 두고, policy 만 Stage 3 에서 fine-tune 하거나 평가할 수 있다. adapter 의 frozen 시점 이후 분포 시프트는 따로 다루지 않는다.
- (가정 6) contrastive 항은 *약한 regularizer* 로 작용해야 한다. $`\lambda_{\mathrm{nce}}`$ 가 커지면 semantic regression 정확도가 하락하기 때문 (Appendix C ablation 증거).

---

## 📊 하이퍼파라미터·손실

- 손실 식:

  $$\mathcal{L}_{\mathrm{adapter}}=\mathcal{L}_{\mathrm{sem}}+\lambda_{\mathrm{nce}}\mathcal{L}_{\mathrm{nce}}$$

  $$\mathcal{L}_{\mathrm{sem}}=\|\hat{z}_{t}-z_{t}\|_{2}^{2}$$

  $$\mathcal{L}_{\mathrm{nce}}=-\log\frac{\exp(\mathrm{sim}(u_{t},u^{+})/\tau)}{\exp(\mathrm{sim}(u_{t},u^{+})/\tau)+\sum_{u^{-}\in\mathcal{N}_{t}}\exp(\mathrm{sim}(u_{t},u^{-})/\tau)}$$

- 하이퍼:
  | 이름 | 값 | 출처 |
  |------|----|----|
  | `lambda_nce` (best) | `0.01` | Appendix C, Table 4 (row D2) |
  | `lambda_nce` (Stage 2 main) | `0.01–0.1` 권장 범위 | §3.3 + Table 4 D2/D7/D8 |
  | `tau` (InfoNCE temperature, best) | (원문 미명시, default 추정) | §3.3, Table 4 B1/B2 (0.05, 0.5 비교) |
  | adapter `d_model` | `256` | Table 4 C2 (Large Transformer) |
  | adapter `n_layers` | `4` | Table 4 C2 |
  | dropout | `0` (best); `0.1` 비교 row 존재 | Table 4 C3, D9 |
  | history length `H` | (원문에 명시 없음 — 가정으로 메움) | — |
  | semantic head 차원 | (원문에 명시 없음 — 가정으로 메움) | — |
  | contrastive head 차원 `D_u` | (원문에 명시 없음 — 가정으로 메움) | — |
  | RL algorithm | PPO (RL-Games) | §3.2, §4.2 |
  | simulator | Isaac Lab + Isaac Sim 5.0 | §4.1 |
  | 실로봇 perturbation | target-position noise ≈ 3 mm | §4.1 |
  | sim 평가 episode 수 | 80 | §4.2 |
  | force regime 클래스 수 | 4 (`free / first_contact / guided_slide / jam`) | §3.3 |
  | privileged Z 차원 | 6 (`onset / lateral / guided / dir_x / dir_y / jam`) | §3.1 |

---

## 🎯 평가 메트릭

- **지표** — `simulation success rate` · **임계값** — 비교 baseline 대비 absolute % difference · **비교 baseline** — FORGE (privileged Z 미사용, adapter 미사용, 동일 task family).
- **지표** — `real success rate` (verified) · **임계값** — `insertion_verified` 신호의 run_id 별 max · **비교 baseline** — FORGE 실로봇.
- **지표** — `sim-to-real gap` (real − sim, 단위: percentage point) · **임계값** — 작을수록 좋음 · **비교 baseline** — FORGE gap.
- **지표** — Wilson 95% CI 적용 verified success · **임계값** — CoRMA / FORGE CI 가 분리되는지로 finite-sample 안전성 판단 · **비교 baseline** — 동일 task / 동일 verification rule.
- **지표** — Stage 2 adapter validation: mean `R²` / Pearson / cosine similarity / MSE · **임계값** — Table 2 의 RMA-Conv (0.43 R²) → CoRMA (0.88 R²) 격차 · **비교 baseline** — RMA-Conv, RMA-Transformer (MSE-only).
- **지표** — adapter 임베딩 분리도 (PCA 시각화) · **임계값** — qualitative, force regime 별 cluster 분리 · **비교 baseline** — `\hat{z}_t` vs `u_t` 양 공간 비교 (Appendix E).
- **지표** — predicted `\hat{z}_t` vs oracle `z_t` 산점도 (diagonal 집중도) · **임계값** — qualitative · **비교 baseline** — Appendix E.2.

---

## ✨ 변경 의도 (intent)

CoRMA 의 핵심 변경은 RMA 의 *target latent 의 의미화* 입니다. 기존 RMA / 변형들이 raw simulator extrinsic vector 를 privileged target 으로 쓰는 데 반해, CoRMA 는 contact-rich assembly 에서 task 간 *공유 가능한* 6D semantic contact context 를 정의하고 이를 회귀합니다. 여기에 (1) adapter 인코더를 Conv1D 에서 causal Transformer 로 교체해 sparse temporal force evidence 의 long-horizon 통합을 강화하고, (2) force-regime InfoNCE 를 약한 regularizer 로 얹어 같은 contact 의미를 띤 history 를 자동으로 묶도록 합니다. RMA 의 non-cheating deployment 원칙과 sim2real 골격 자체는 그대로 유지되고, 덕분에 sim 성능보다 *real* 성능이 더 잘 유지되는 trade 가 보고됩니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 후보 base: lerobot 의 6 정책군 (`pi0` / `pi05` / `pi0_fast` / `smolvla` / `act` / `diffusion`) 중 어디에도 1:1 매핑되지 않습니다. CoRMA 는 (a) PPO + Isaac Lab + RL-Games 기반 RL 학습 파이프라인, (b) FORGE 환경, (c) custom transformer adapter 의 세 축이 모두 lerobot 의 IL 중심 policy family 와 분리됩니다. lerobot 의 `rtc` 또는 processor / transforms 레이어에 *외부* adapter conditioning 을 주입하는 형태라면 부분 매핑은 시도해 볼 만하지만 full mapping 은 unlikely 합니다. `/foundry` 단계에서 `🚧 매핑 불가` 가 합당한 출력일 수 있습니다.

---

## 🚧 미해결 / 잠정

- history 길이 `H`, batch size, optimizer / learning rate, training step 수 같은 학습 셋업 하이퍼는 (원문에 명시 없음 — 가정으로 메움).
- causal Transformer 의 attention head 수, FFN 차원, positional encoding 형식은 본문·부록 모두 명시되지 않음.
- semantic / contrastive head 의 정확한 layer 구성 (MLP 깊이·폭) 미명시.
- InfoNCE negative 샘플링이 in-batch 인지 memory queue 인지 명시되지 않음.
- 6D Privileged $`Z`$ 각 차원의 수치 계산식 (시뮬레이터 contact·force dynamics 에서 어떻게 점수화하는지) 은 본문 수준에서 정의만 제시, 정확한 수식 미명시.
- force regime 라벨 결정 규칙 (threshold, sliding window 기준 등) 은 Appendix D 의 정성 기술 외 구체 알고리즘 미공개.
- 실로봇 평가의 verification 규칙 (`insertion_verified`) 의 측정 방식은 deployment-side 규칙으로 언급되나 구체 정의는 본문 범위 밖.
- Marvin 7-DoF arm 의 action space 차원과 TRAC-IK 호출 인터페이스의 구체 spec 은 본문에서 다루지 않음.
- Real2Sim calibration 은 일부러 보류했고, future work 으로 명시되어 있습니다.
- 코드·체크포인트 공개 여부는 본문에 명시되지 않음.
