# Design — Beyond Binary: Sim-to-Real Dexterous Manipulation with Physics-Grounded Contact Representation

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
| 원문 제목 (영문) | Beyond Binary: Sim-to-Real Dexterous Manipulation with Physics-Grounded Contact Representation |
| 링크 | [arXiv:2605.28812](https://arxiv.org/abs/2605.28812) |
| 분석 문서 | [`analysis/2605.28812/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-05-29 |

---

## 🧮 데이터 계약

CoP 표현 추출(센서 매핑)과 정책 학습(RL)의 두 계약으로 나뉩니다.

- **입력 (raw taxel forces)** — $`\{{}^{\mathcal{T}_{i}}f_{i}\}_{i=1\dots N}`$: shape `(N, 3)`, dtype float32, taxel 국소 프레임 표현. 손끝별 어레이당 $`N`$ 개 taxel(값은 센서 스펙 의존, 원문 미명시).
- **입력 보조 (센서 기하)** — taxel 원점 $`{}^{\mathcal{S}}p_{i}`$ shape `(N, 3)` (스펙에서 획득), taxel 회전 $`R_{i}\in\mathbb{SO}(3)`$ shape `(N, 3, 3)` (캘리브레이션으로 학습).
- **중간 출력 (CoP 표현)** — 접촉력 벡터 $`f_{\rm{cop}}\in\mathbb{R}^{3}`$ + 접촉 위치 $`p_{\rm{cop}}\in\mathbb{R}^{3}`$. 실사용에서는 **법선 성분만** 사용(전단 제외) → 정책 입력으로는 손끝당 정렬된 힘·위치.
- **정책 관측 (actor)** — 현재 관절각 $`q_{t}\in\mathbb{R}^{16}`$ + 이전 행동 $`a_{t-1}\in\mathbb{R}^{16}`$ + flatten 된 접촉 표현(고차 텐서는 단일 벡터로 평탄화 후 concat). 시각 제외.
- **정책 관측 (critic)** — actor 관측 + 특권 물체 상태(과제별, 아래 표). 학습에만 사용.
- **출력 (action)** — $`a\in\mathbb{R}^{16}`$: 16-DOF 목표 관절 위치 증분. $`[-1,1]^{16}`$ 클립 후 action scale(0.03 삽입 / 0.05 균형) 적용, EMA $`\alpha=0.5`$ 평활화, 이전 명령 목표에 가산해 PD 제어로 추종.

| critic 특권 관측 (Peg-in-Hole) | 양 | critic 특권 관측 (Ball Balancing) | 양 |
|---|---|---|---|
| peg position | $`p_{\rm{peg}}\in\mathbb{R}^{3}`$ | plate position | $`p_{\rm{plate}}\in\mathbb{R}^{3}`$ |
| peg rotation | $`R_{\rm{peg}}\in\mathbb{R}^{4}`$ | plate rotation | $`R_{\rm{plate}}\in\mathbb{R}^{4}`$ |
| goal vector | $`r_{\rm{goal}}=p_{\rm{goal}}-p_{\rm{peg}}`$ | plate lin./ang. velocity | $`v_{\rm{plate}},\omega_{\rm{plate}}\in\mathbb{R}^{3}`$ |
| goal reached | $`\mathbb{1}(\|r_{\rm{goal}}\|\leq\epsilon)`$ | ball position / velocity | $`p_{\rm{ball}},v_{\rm{ball}}\in\mathbb{R}^{3}`$ |
| | | goal distance | $`d_{\rm{goal}}=p_{\rm{ball}}-p_{\rm{plate}}`$ |

---

## 🧰 모듈 인터페이스

```python
def forward_mapping(f_cop, p_cop, taxel_pos, taxel_normals, sigma) -> taxel_forces:
    """CoP (힘 벡터 + 접촉점) → taxel 별 유효 힘 {f_i}. M_i = w_i(b_i n_cop^T + P_shear)."""

def solve_cop_force(taxel_forces, M) -> f_cop:
    """관측 taxel 힘에서 미지 f_cop 를 정규화 최소제곱 닫힌 해로 복원.
       f_cop = (A^T A + λ^2 I)^{-1} A^T b."""

def estimate_cop_position(taxel_forces, taxel_pos, eps) -> p_cop:
    """active 집합 {i: ||f_i|| > eps} 의 힘 가중 평균으로 접촉 위치 추정."""

def calibrate_taxel_orientation(taxel_forces, joint_torques, joint_angles) -> R:
    """미분 가능 동역학으로 taxel 회전 학습. R = SVD^+(P);
       loss = MSE(τ̂, τ), τ̂ = -J_cop^T f_cop. ground-truth 힘 불필요."""
```

- **forward_mapping** / **solve_cop_force** — 같은 미분 가능 모델의 양방향 평가. 시뮬레이션 CoP ↔ 하드웨어 taxel 상호 변환. 외부 호출 계약: 정책 관측 파이프라인이 매 스텝 `solve_cop_force` + `estimate_cop_position` 으로 관측 벡터를 구성.
- **calibrate_taxel_orientation** — 학습 1회(센서 기하당), task-specific 실세계 정책 학습 불필요. gradient 는 taxel→CoP→FK→토크 경로를 따라 회전 파라미터 $`\hat{P}`$ 로 역전파.
- **정책 (actor/critic)** — 동일 recurrent 구조 공유. 비대칭 PPO; actor 는 전이 가능한 관측만, critic 은 특권 관측 추가.

---

## ⛓️ 불변식·가정

- (가정 1) 정적 평형에서 외력과 관절 토크는 $`\tau\approx-J^{\top}f`$ 를 만족하며 중력 보상항 $`g(q)`$ 은 무시 가능하다고 가정합니다.
- (가정 2) 접촉력은 부드러운 실리콘 층을 통해 퍼집니다. 접촉점으로부터 거리에 따라 Gaussian 으로 감쇠합니다(단순 합산/평균은 합력·위치를 편향시킴).
- (가정 3) 각 taxel 은 한 프레임 축이 표면에 직교하도록 배열되어 inward unit surface normal $`\hat{n}_{i}`$ 을 손쉽게 얻습니다.
- (가정 4) 시뮬레이터 전단 추정이 불안정하므로 CoP 는 **법선 성분만** 사용합니다 — 전단 정보를 희생해 Sim2Real 정렬성을 확보하는 의도적 trade-off.
- (가정 5) taxel 원점 $`p_{i}`$ 은 스펙에서 알려진 값이고 미지수는 회전 $`R_{i}`$ 뿐입니다.
- (가정 6) 시뮬레이터가 물체 간 3D 접촉력 벡터 + 접촉 위치를 제공하므로(예: IsaacSim, MuJoCo) 학습된 인코더 없이 시뮬레이션-하드웨어 표현을 정렬할 수 있습니다.

---

## 📊 하이퍼파라미터·손실

- **Forward 매핑**: $`f_{i}=M_{i}f_{\rm{cop}}`$, $`M_{i}=w_{i}(\hat{b}_{i}\hat{n}_{\rm{cop}}^{\top}+P_{\text{shear}})`$, $`P_{\text{shear}}=I_{3}-\hat{n}_{\rm{cop}}\hat{n}_{\rm{cop}}^{\top}`$, Gaussian 가중치 $`w_{i}=\exp(-\|p_{i}-p_{\rm{cop}}\|^{2}/2\sigma^{2})`$.
- **Inverse 해**: $`f_{\rm{cop}}=(A^{\top}A+\lambda^{2}I)^{-1}A^{\top}b`$.
- **회전 파라미터화**: $`R=\text{SVD}^{+}(P)=U\text{diag}(1,1,\det(UV^{\top}))V^{\top}`$.
- **캘리브레이션 손실**: $`\text{MSE}(\hat{\tau},\tau)`$, $`\hat{\tau}=-{}^{\mathcal{B}}\hat{J}_{\mathrm{cop}}^{\top}{}^{\mathcal{B}}\hat{f}_{\mathrm{cop}}`$.

| 이름 | 값 | 출처 |
|------|----|----|
| `learning rate` (적응형 시작) | `5.0e-4` | §E.5 |
| `target KL` | `0.016` | §E.5 |
| `discount γ` | `0.99` | §E.5 |
| `GAE λ` | `0.95` | §E.5 |
| `clip range` | `0.2` | §E.5 |
| `entropy coef` | `0.005` | §E.5 |
| `steps/env` | `64` (삽입) / `16` (균형) | §E.5 |
| `epochs / minibatches` | `5` / `4` | §E.5 |
| `action scale` | `0.03` (삽입) / `0.05` (균형) | §E.2 |
| `action EMA α` | `0.5` | §E.2 |
| `PD gains (P, D)` | `(3.0, 0.1)` 삽입 / `(6.0, 0.15)` 균형 | §E.2 |
| `seeds` | `5` | §E.5 |
| 응력 spread `σ` | (원문 미명시) | §3.2 |
| 정규화 `λ` | (원문 미명시) | §3.2 |
| active 임계 `ε` | (원문 미명시) | §3.2 |

주요 보상 항(§E.3, Table 5) — 삽입: goal distance $`\exp(-0.5(d_{\rm{goal}}/0.015))`$ (w 1.0), goal reached $`\mathbb{1}(\|r_{\rm{goal}}\|\leq\epsilon)`$ (w 400.0), good contact $`\sum_{i}\mathbb{1}(\|f_{i}\|\geq 1.0)`$ (w 0.25), rotation·DOF deviation penalty (각 w 1.0). 균형: goal distance (w 1.0), plate contact (w 0.2), ball fallen $`\mathbb{1}(p_{\rm{ball,z}}\leq 0.2)`$ (w 200.0), action diff penalty (w 1.0) 등.

도메인 랜덤화(§E.4) — 마찰 정적/동적 분리, 물체·plate 질량, 초기 pose, PD 게인 ×U(0.8,1.2)/×U(0.7,1.3), 관절 관측 노이즈 +U(-0.1,0.1) rad, 힘 벡터 노이즈(확률 0.2·회전 +U(-0.1,0.1)·크기 ×U(0.9,1.1)), 접촉 위치 노이즈, 관절 관측 지연 0.05s, 접촉 관측 지연 [0.05,0.1]s.

---

## 🎯 평가 메트릭

- **지표** — peg-in-hole: 성공률(sr) + 완료시간(time, s) · **비교 baseline** — base/bin/mag/vec/pos/taxel/human · **임계값** — `cop` overall sr 0.78 (최고 로봇 정책).
- **지표** — ball balancing: time-to-fall(TTF, s) · **비교 baseline** — 동일 · **임계값** — `cop` overall 4.60s.
- **강건성** — OOD 초기화 성공률 유지, raw taxel 40% 마스킹 성공률.
- **표현 분석** — 잠재 linear probing RMSE / $`r^{2}`$ (공 위치·속도), 질량별 PCA 군집 Silhouette Coefficient.

---

## ✨ 변경 의도 (intent)

기존 Sim2Real 촉각 처리는 두 극단입니다 — binary 처럼 거칠게 단순화(전이 OK, 정보 손실)하거나, raw taxel + 학습된 인코더 + 교사-학생 distillation(정보 OK, 센서 특화·정렬 난이도). CoP 는 접촉을 "3D 힘 벡터 + 3D 접촉 위치"라는 시뮬레이터가 본래 제공하는 물리량으로 환원합니다. 그래서 학습된 인코더도 distillation 도 없이 시뮬레이션-하드웨어를 정렬하고 zero-shot 전이합니다. 표현에서 학습되는 것은 taxel 회전 캘리브레이션뿐입니다. 그조차 ground-truth 힘 없이 정적 평형 토크 정합으로 얻습니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 명확한 정책 family base 없음. 본 산출물의 핵심은 IL 정책(`act` / `diffusion` / `pi0` 계열)이 아니라 **관측 전처리 모듈**(raw taxel → CoP 힘·위치)과 RL 학습 레시피(비대칭 PPO + DR)입니다. lerobot 좌표계로는 정책 base 보다 `transforms/` / `processor` 의 관측 변환 단계에 가깝습니다. PPO·IsaacLab RL 루프 자체는 lerobot 의 IL baseline 범위 밖입니다. 매핑 적합성은 `/implement-design` 가 최종 판정합니다.

---

## 🚧 미해결 / 잠정

- 응력 분포 모델의 spread $`\sigma`$, 정규화 $`\lambda`$, active 임계 $`\epsilon`$ 의 구체 수치가 확보 본문에 없습니다 — (원문에 명시 없음 — 가정으로 메움) 필요.
- taxel 수 $`N`$ 과 어레이 격자 형상은 알 수 없습니다(XELA uSkin 스펙 의존).
- 학습 환경 수(병렬 env count)와 총 학습 step / 반복 수가 본문에 명시되지 않습니다.
- 코드·데이터·가중치 공개 여부 및 라이선스가 확보 본문에서 확인되지 않습니다(project site / supplementary video 만 언급).
- CoP 의 "법선 성분만" 사용은 시뮬레이터 전단 불안정에서 비롯된 구현 제약입니다. 전단을 살린 일반 버전은 본문 범위 밖입니다.
