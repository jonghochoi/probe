# Design — CoorDex: Coordinating Body and Hand Priors for Continuous Dexterous Humanoid Loco-Manipulation

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | CoorDex: Coordinating Body and Hand Priors for Continuous Dexterous Humanoid Loco-Manipulation |
| 링크 | [arXiv:2606.23680](https://arxiv.org/abs/2606.23680) |
| 분석 문서 | [`analysis/2606.23680/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-23 |

---

## 🧮 데이터 계약

시간 축은 제어 스텝 단위(60 Hz). 차원은 G1(29 body DoF) + WUJI 손(20 finger DoF) 인스턴스 기준이며, body latent `d_b=16` / hand latent `d_h=12`.

- **입력 (body prior)** — `s_b_prop`: shape `(B, 450)`, float. 5-프레임 suffix $`5\times[\omega_{\mathrm{base}}(3), q(29), \dot{q}(29), a_{t-1}(29)]`$, empirical observation normalization 적용.
- **입력 (hand prior)** — `s_h_prop`: shape `(B, 66)`, float. $`[v_{\mathrm{wrist}}(3), \omega_{\mathrm{wrist}}(3), q_{\mathrm{rel}}(20), \dot{q}_{\mathrm{rel}}(20), a_{t-1}(20)]`$ (wrist 좌표계, default 대비 상대 관절 상태).
- **입력 (task / coordination)** — `s_task` (물체 자세·목표·projected gravity·접촉 특징), `s_hand_object` (손 좌표계 물체 자세 + fingertip-object 접촉). 물체 자세는 3-D 위치 + 회전행렬 첫 두 열(6-D) = 9-D. downstream 관측 총합: WalkGrab `618` / OpenFridge `629` / WalkPickTurn `620`.
- **출력 (정책)** — $`\Delta\mathbf{z}`$ : shape `(B, 28)` = $`[\Delta\mathbf{z}_b(16), \Delta\mathbf{z}_h(12)]`$ , float, 각 성분 `tanh` 로 `[-1,1]` bound.
- **출력 (디코더 → 액션)** — `a_b`: `(B, 29)` body 관절 위치 목표, `a_h`: `(B, 20)` finger 관절 위치 목표. hand 목표는 joint-action scale/offset 변환 후 EMA(계수 `0.4`) 적용. 결합 후 PD 컨트롤러로 실행.
- **정규화 가정** — prior 입력은 empirical normalizer(동결 시 함께 로드); 관절 상태는 default joint state 대비 상대값. (원문에 명시 없음 — 절대 단위 통계의 구체 수치는 가정으로 메움.)

---

## 🧰 모듈 인터페이스

```python
def body_prior_mean(s_b_prop) -> mu_b:
    """동결 body prior R_b 의 평균. (B,450) -> (B,16). 기본 잠재 명령."""

def hand_prior_mean(s_h_prop) -> mu_h:
    """동결 wrist-stabilized hand prior R_h 의 평균. (B,66) -> (B,12)."""

def coordination_trunk(s_b_prop, s_h_prop, s_task, s_hand_object,
                       mu_b, mu_h, dz_prev) -> c:
    """공유 trunk f_coord: body-hand 결합을 포착한 task-level coordination feature."""

def body_head(c, s_b_prop, mu_b) -> dz_b:      # tanh, (B,16)
    """stepping/torso/reach/wrist 배치 잔차."""

def hand_head(c, s_h_prop, mu_h, s_hand_object) -> dz_h:   # tanh, (B,12)
    """finger preshape/closure/contact 잔차."""

def body_decoder(s_b_prop, mu_b + dz_b) -> a_b:   # 동결, (B,29)
    """보정 잠재 -> body 관절 위치 목표."""

def hand_decoder(s_h_prop, mu_h + dz_h) -> a_h:   # 동결, (B,20)
    """보정 잠재 -> active finger 관절 위치 목표."""

def distill_step(teacher_action, s_full, s_prop) -> loss:
    """teacher 행동 재구성 + 인코더 평균 시간평활 + 인코더|prior KL."""
```

- **호출 계약** — downstream RL(PPO)은 `coordination_trunk`·`body_head`·`hand_head`·critic 만 학습; `body_prior_mean`·`hand_prior_mean`·`body_decoder`·`hand_decoder` 는 **동결**(no-grad). `distill_step` 은 prior 구성 단계 전용으로 downstream 과 분리.
- **데이터 흐름** — `mu = prior_mean(s_prop)` → `c = trunk(...)` → `dz = tanh(head(c, ...))` → 보정 잠재 $`\tilde{\mathbf{z}} = \boldsymbol{\mu} + \Delta\mathbf{z}`$ 를 디코더에 투입해 `a = decoder(s_prop, z_tilde)`. body→hand 계층 흐름은 공유 `c` 를 통한 간접 결합.

---

## ⛓️ 불변식·가정

- (가정 1) 동결 prior 평균이 기본 명령 — $`\Delta\mathbf{z}=0`$ 이면 디코더는 prior 모션을 재생; 정책은 그 근방의 교정만 학습.
- (가정 2) 잔차는 성분별 `tanh` bound ( $`|\Delta\mathbf{z}_i| \le 1`$ ) — 도달 가능 거동은 prior 디코더가 span 하는 manifold + bounded 잔차 근방에 국한.
- (가정 3) wrist-stabilized 분리 — hand prior 학습 시 참조 손목 자세·속도를 시뮬레이션에 직접 기록하므로 hand 잠재는 *손가락 모션만* 설명. downstream 에서 손목은 body 잠재가 결정.
- (가정 4) prior/디코더 동결 불변 — downstream gradient 가 prior·디코더로 흐르지 않아야 잠재 행동공간의 의미가 보존(분포 drift 방지).
- (가정 5) 증류 잠재의 시간적 연속성 — 인접 valid 샘플 간 인코더 평균 차분이 작다(평활 항). 깨지면 잠재 명령이 불연속이 되어 잔차 정책 학습이 불안정.
- (가정 6) body/hand 행동공간은 같은 제어율(60 Hz)로 동기 실행되며 각자의 관절 슬롯에 비충돌 삽입.

---

## 📊 하이퍼파라미터·손실

- **증류 손실 (식 1 / §A.3)**:

$$\mathcal{L}=\lambda_{a}\|\hat{a}_{t}-a^{T}_{t}\|_{2}^{2}+\lambda_{s}\|\mu^{q}_{t}-\mu^{q}_{t-1}\|_{2}^{2}+\lambda_{\mathrm{KL}}D_{\mathrm{KL}}\left(q_{\phi}(z_{t}\mid s^{\mathrm{full}}_{t})\,\|\,p_{\psi}(z_{t}\mid s^{\mathrm{prop}}_{t})\right)$$

- **잠재 합성 (식 5–6)**: $`\tilde{\mathbf{z}} = \boldsymbol{\mu} + \Delta\mathbf{z}`$ , $`\mathbf{a} = D(\mathbf{s}^{\mathrm{prop}}, \tilde{\mathbf{z}})`$ .

| 이름 | 값 | 출처 |
|------|----|----|
| body latent dim `d_b` | `16` | §4.1 Table 1 |
| hand latent dim `d_h` | `12` | §4.1 Table 1 |
| 잔차 행동 차원 | `28` (16+12) | §A.4, Table 10 |
| 증류 action 계수 $`\lambda_a`$ | `1.0` (body·hand) | §A.3 |
| 증류 smoothness 계수 $`\lambda_s`$ | `0.005` | §A.3 |
| 증류 KL anneal (body) | $`10^{-3} \to 10^{-4}`$ @15k–20k | §A.3 |
| 증류 KL anneal (hand) | $`10^{-2} \to 10^{-3}`$ @15k–25k | §A.3 |
| 증류 LR (body / hand) | `2e-4 / 5e-4` | §A.3 |
| 증류 MLP hidden | `[512,256,128]` | §A.3 |
| 증류 최대 iter / grad accum / clip | `30000 / 16 / 1.0` | §A.3 |
| PPO env / rollout / batch | `4096 / 24 / 98304` | §B.3 Table 9 |
| PPO minibatch / epoch | `4 / 5` | §B.3 Table 9 |
| PPO $`\gamma`$ / $`\lambda_{\mathrm{GAE}}`$ / clip | `0.99 / 0.95 / 0.2` | §B.3 Table 9 |
| PPO entropy / value 계수 | `0.005 / 1.0` | §B.3 Table 9 |
| PPO LR (adaptive, KL target) | `1e-3` (KL `0.01`) | §B.3 Table 9 |
| PPO max grad norm | `1.0` | §B.3 Table 9 |
| actor/critic hidden | `[1024,512,256]`, ELU | §B.3 Table 9 |
| coord trunk hidden | `[512,256]` | §B.3 Table 9 |
| body/hand head hidden | `[256,128]` | §B.3 Table 9 |
| 잔차 scale | `1.0` | §B.3 Table 9 |
| init action noise $`\sigma`$ | `0.22` | §B.3 Table 10 |
| hand 목표 EMA 계수 | `0.4` | §A.4 |
| 제어율 / decimation | `60 Hz` / `4` (physics `1/240` s) | §A.1, §B |

- 보상은 과제별 다항 가중합(§B.2 Table 6–8): predicate-gated approach↔manipulation 전환, fingertip contact $`\mathrm{mean}_i\,\mathbb{1}[\|F_i\|>1\mathrm{N}]`$ , grasp force $`\mathrm{clip}(\Sigma\|F\|,0,2)`$ , sustained-grasp 카운터, locomotion/posture/termination 정규화. WalkPickTurn 은 stage 가중 $`r_t = \sum_i w_i\cdot\mathbb{1}[s_t=i]\cdot r^{(i)}_t`$ .

---

## 🎯 평가 메트릭

- **지표** — `success` (과제별 완료 조건 + 균형 유지) · **임계값** — WalkGrab: 루트 전진 `>2.0 m` + 병 lift `>0.02 m` + grasp; OpenFridge: 문 각도 $`\geq 60^{\circ}`$ + held-open $`\geq 30`$ step(각도 $`\geq 35^{\circ}`$ & ≥1 fingertip contact `>1N`); WalkPickTurn: grasp(fingertip-cube `<0.08 m` + contact) + lift `>0.10 m` + heading 오차 `<0.4 rad` 로 180° 회전.
- **보조 지표** — `fall` · `drop` · action rate(연속 스텝 body 관절 목표 변화량) · door angle · heading error · non-stop 진단(상대 위치 binned forward velocity).
- **비교 baseline** — `All Joint Space` (prior 제거, joint 직접) · `Body Prior + Hand Joint Space` (hand 만 joint) · `Monolithic Latent Residual` (단일 MLP 로 concat 잔차). 동일 환경·보상·PPO 예산에서 task-level 지표로 비교(보상 raw return 비교 불가).

---

## ✨ 변경 의도 (intent)

전 관절 직접 RL(고차원 결합 탐색 폭발) 대신, body·hand 를 각각 증류된 *동결 잠재 모션 prior* 로 치환해 탐색을 저차원 잠재 공간으로 가둡니다. 핵심 차별점은 두 가지입니다 — (1) **비대칭 분해**: 손목 배치는 전신 body prior 에서 창발시키고 손가락 조정은 wrist-stabilized hand prior 가 전담해, 손 잠재 용량이 6D 손목에 낭비되지 않게 함. (2) **coordinated 잔차 구조**: 잔차를 하나의 MLP 로 합쳐 내지(monolithic) 않고, 모든 task 상태를 함께 보는 공유 coordination trunk → 분리된 body/hand head 로 내보내, 전신 적응과 손가락 적응이 단일 출력 경로로 뭉개지지 않게 함. ablation 은 두 요소(잠재-prior 인터페이스 + 분리 head)가 *둘 다* 있어야 비정지 다지 loco-manipulation 이 학습됨을 보입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 깨끗한 base 후보 **없음**. lerobot 은 IL policy 라이브러리(`pi0`/`pi05`/`pi0_fast`/`smolvla`/`act`/`diffusion`/`vla_jepa` + `rtc`)로 PPO/Isaac Lab RL env·모션 prior 추상이 없고, CoorDex 는 RL 잔차 + 동결 VAE 모션 prior + 휴머노이드 loco-manipulation 구조라 정책 family 가 맞지 않습니다. 이식 가능한 *부분 조각*은 (a) 인코더–prior–디코더 VAE 증류 모듈(범용 MLP)과 (b) "동결 잠재 위 잔차 head + 공유 trunk/분리 head" 의 액션-헤드 구조 정도이며, 둘 다 lerobot 액션 디코더에 직접 대응하는 좌표가 없어 `/implement-design` 가 `UNMAPPABLE` 판정할 가능성이 높습니다.

---

## 🚧 미해결 / 잠정

- 인코더 $`q_\phi`$ 의 전체 관측 `s_full` 의 정확한 구성(특권 항 포함 범위)이 본문에 부분만 명시 — 디테일은 (원문에 명시 없음 — 가정으로 메움).
- prior 입력의 절대 정규화 통계(평균/표준편차 출처)는 본문 미명시 — "empirical observation normalization" 만 기록됨.
- `f_coord` 출력 `c_t` 의 차원은 본문 미명시(coord trunk hidden `[512,256]` 만 제공).
- 보상 항 일부(예: WalkPickTurn fingertip contact "contact ratio + count bonus")는 정성 서술로만 주어져 정확한 식이 잠정.
