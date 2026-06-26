# Design — One Hand to Rule Them All: Canonical Representations for Unified Dexterous Manipulation

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | One Hand to Rule Them All: Canonical Representations for Unified Dexterous Manipulation |
| 링크 | [arXiv:2602.16712](https://arxiv.org/abs/2602.16712) |
| 분석 문서 | [`analysis/2602.16712/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-26 |

이 Design 은 본 논문의 포팅 가능한 Layer 1 알고리즘 — **canonical morphology 표현(VAE latent) + 그 latent 를 조건으로 받는 cross-embodiment grasp 생성 정책(2-stage diffusion + MLP)** — 을 vendor-agnostic 명세로 정리합니다. canonical URDF parsing/generation 은 데이터 전처리 tooling 으로, 알고리즘이 아니라 데이터 계약의 일부로 다룹니다.

---

## 🧮 데이터 계약

- **입력 (손 형태)** — canonical 파라미터 벡터 `q_hand`: 기본 82-D (확장 173-D). 구성 = 연속 기하/frame 파라미터(`q_cont`) + 조인트 축 6-way one-hot(`q_axis`, 22 joint) + 조인트 활성 이진 지표(`q_joint`, 22-D). dtype float32. 연속부는 물리 타당 범위 정규화 가정.
- **입력 (물체)** — object point cloud `P_obj`: shape `(B, N, 3)`, D(R,O) point 인코더로 feature 추출.
- **입력 (grasp 조건)** — wrist rotation `R`: shape `(B, 3, 3)` 또는 등가 회전 표현(원문 표기 미상세), object frame 기준.
- **VAE latent** — `z_hand`: shape `(B, 16)`, float32. grasp 정책에는 **frozen** 으로 주입.
- **출력 (grasp)** — wrist translation $`\hat{T}`$: shape `(B, 3)` (diffusion 샘플); 조인트 구성 $`\hat{\theta}`$: shape `(B, 22)` (canonical action space, 비활성 joint dummy 포함).
- **시간 축** — grasp 생성은 단일 static pose 예측(time-step 없음). diffusion 의 step 축은 `T_diffusion=1000` (학습), 추론 `T_ddim=10`.

---

## 🧰 모듈 인터페이스

```python
def morphology_vae_encode(q_hand) -> z_hand:
    """canonical 파라미터 벡터 → 16-D 형태 latent (mean; 추론 시 frozen)."""

def morphology_vae_decode(z_hand) -> q_hand_hat:
    """16-D latent → canonical 파라미터 복원 (multi-head: continuous/axis/joint)."""

def grasp_feature(P_obj, z_hand) -> f_g:
    """object point feature + frozen VAE 손 latent 결합 → grasp 조건 feature."""

def wrist_translation_diffusion(f_g, R, t) -> T_hat:
    """f_g 와 명시적 wrist rotation R 을 조건으로 wrist translation 분포 샘플 (DDIM)."""

def joint_regressor(T, R, f_g) -> theta_hat:
    """샘플된 wrist pose (T,R) + f_g → 조인트 구성 (결정적 MLP)."""
```

- **morphology_vae_*** — 인코더 MLP hidden `[512,256,128]` + BatchNorm + ReLU, 디코더 대칭; 출력 3-head(continuous / categorical-axis / sigmoid-joint).
- **grasp_feature** — VAE latent 는 frozen(gradient 차단). object 인코더는 D(R,O) 외부 의존.
- **wrist_translation_diffusion** — MLP diffusion, hidden `[512,256]`, step embedding 64, "sample" prediction. `R` 분리 주입으로 orientation↔translation decouple.
- **joint_regressor** — 경량 MLP, 결정적 매핑.

---

## ⛓️ 불변식·가정

- (가정 1) — 모든 손은 최대 5-finger·22-DoF canonical 골격의 부분집합이며, 비활성 조인트는 dummy 변수로 22-D action 벡터에 항상 존재(indexing·부호 규약 고정).
- (가정 2) — 좌표 규약 불변: palm 법선 $`+x`$, (오른손) 엄지 $`+y`$, 비엄지 손가락 $`+z`$; 국소 축 abduction-adduction $`x`$ / flexion-extension $`y`$ / axial rotation $`z`$.
- (가정 3) — 기본 표현 가정: 모든 손가락 동일 capsule 직경, 비엄지 손가락 동일 link 길이·palm $`yz`$-평면 배치, 엄지 joint1/joint2 외 모든 축 고정. (위배 손은 173-D 확장 필요.)
- (가정 4) — VAE latent 는 grasp 정책 학습 중 frozen; morphology conditioning 은 오직 이 16-D latent 를 통해 전달.
- (가정 5) — canonical ↔ 원본 조인트 양방향 매핑이 동역학·기능 속성을 보존(action mapping 충실도 — Allegro axial-rotation 등 일부 손에서 위배되어 성능 손실).

---

## 📊 하이퍼파라미터·손실

- **Grasp 손실 (Eq. 1)**: $`\mathcal{L}=\text{SmoothL1}(\hat{T},T)+\text{SmoothL1}(\hat{\theta},\theta)`$
- **VAE 손실 (Eq. 2–3)**: $`\mathcal{L}=\mathcal{L}_{\text{cont}}+\mathcal{L}_{\text{axis}}+\mathcal{L}_{\text{joint}}+\beta\,\mathcal{L}_{\text{KL}}`$, where $`\mathcal{L}_{\text{cont}}=\|\hat{q}_{\text{cont}}-q_{\text{cont}}\|_{2}^{2}`$, $`\mathcal{L}_{\text{axis}}=\text{CrossEntropy}`$, $`\mathcal{L}_{\text{joint}}=\text{BCE}(\sigma(\cdot))`$
- **In-hand RL 보상 (Eq. 4, 선택 적용분)**: $`r_{\text{base}}=s_{\text{rot}}r_{\text{rot}}-s_{\text{v}}\,p_{\text{v}}-s_{\text{pose}}\,p_{\text{pose}}-s_{\tau}\,p_{\tau}-s_{\text{work}}\,p_{\text{work}}`$

| 이름 | 값 | 출처 |
|------|----|----|
| `latent_dim` | `16` | §IV-A |
| `vae_hidden` | `[512,256,128]` | §Appendix -C2 |
| $`\beta`$ (KL weight) | `0.01` | §Appendix -C3, Eq. (3) |
| VAE `lr` / $`(\beta_1,\beta_2)`$ / `wd` | `1e-4` / `(0.95,0.999)` / `1e-6` | §Appendix -C3 |
| VAE 학습 샘플 | `65,536` | §IV-A |
| diffusion timestep / 추론 | `1000` / `10-step DDIM` | §Appendix -E1, §V-C |
| diffusion `lr` (cosine) | `1e-3` → `1e-7` | §Appendix -E1 |
| diffusion hidden / step-emb | `[512,256]` / `64` | §Appendix -E1 |
| grasp 학습 데이터 | `24,764` (3-hand) / `69,917` (LEAP zero-shot) | §V-C, §V-D |
| PPO $`\gamma`$/$`\lambda`$/clip/lr | `0.99`/`0.95`/`0.2`/`5e-3` | §Appendix -D2, Table XII |
| 보상 scale `s_*` | `(원문에 명시 없음 — 가정으로 메움)` | §Appendix -D2 |

---

## 🎯 평가 메트릭

- **지표** — grasp success rate(%) · **임계값** — Isaac Gym 에서 6 직교 방향 외력 1초씩 인가 후 물체 변위 `< 2 cm` (force-closure 기준) · **비교 baseline** — D(R,O) Grasp, GenDexGrasp, DFC; Unified vs Specific.
- **부가 지표 (in-hand)** — Steps-to-Fall ↑, Cumulative Rotation(z축 라디안) ↑.
- **일반화 지표** — zero-shot success rate(미관측 LEAP 변형); 잘못된 hand condition 절제(조건 민감도).

---

## ✨ 변경 의도 (intent)

기존 cross-embodiment 방법(interaction field, contact pattern, PCA synergy)은 grasp synthesis 에 머무르거나(D(R,O)), 인간형 운동학을 가정하거나(DexUMI), 구조적으로 유사한 손에만 적용(particle dynamics)됩니다. 본 논문은 손의 형태·운동학을 **단일 파라미터 공간 + 통일 22-DoF action space** 로 표준화하고, 그 형태를 frozen VAE latent 조건으로 정책에 주입함으로써, 같은 정책이 학습 때 보지 못한 손에도 zero-shot 으로 일반화하도록 만든 점이 차별점입니다. 정책 아키텍처 자체는 의도적으로 단순(2-stage diffusion+MLP)하게 두어, 성능 향상이 표현/action space 의 표준화에서 온다는 것을 분리·입증합니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 직접 대응 family 는 없음. grasp 생성기의 diffusion 부분은 `diffusion` policy 의 noise-prediction/스케줄러 유틸과 가장 가까우나, 본 논문은 sequential action chunk 가 아니라 static grasp pose 예측이라 정합이 부분적. morphology-conditioning(frozen latent 를 feature 로 concat)은 어느 policy 든 조건 입력 경로에 얹을 수 있는 일반 패턴.

---

## 🚧 미해결 / 잠정

- 보상 scale 항 $`s_{\text{rot}}`$/$`s_{\text{v}}`$/$`s_{\text{pose}}`$/$`s_{\tau}`$/$`s_{\text{work}}`$ 및 $`\omega_{\text{min}}`$/$`\omega_{\text{max}}`$/$`z_{\text{threshold}}`$ 구체값이 본문에 없어 in-hand RL 재현 시 재튜닝 필요.
- wrist rotation `R` 의 정확한 표현(행렬 / 6D / quaternion)이 본문에 명시되지 않아 `(3,3)` 으로 가정.
- grasp 정책의 batch size·총 학습 step·하드웨어가 본문에 명시되지 않음.
- `q_cont` 의 정규화 통계 출처(샘플링 범위는 명시되나 정책 입력 정규화는 미상)는 "샘플링 범위 기준 min-max" 로 가정.
