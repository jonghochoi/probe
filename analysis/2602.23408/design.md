# Design — Demystifying Action Space Design for Robotic Manipulation Policies

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Demystifying Action Space Design for Robotic Manipulation Policies |
| 링크 | [arXiv:2602.23408](https://arxiv.org/abs/2602.23408) |
| 분석 문서 | [`analysis/2602.23408/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-11 |

<!-- 본 논문은 새 모델이 아니라 action-space "설계 축" 을 분리하는 study 입니다.
     따라서 Layer 1 Design 은 단일 알고리즘이 아니라, 임의의 chunked policy 위에
     끼우는 action-space 디코딩/사상 모듈(temporal decode + spatial map)의 계약으로
     정리합니다. 본문 미명시 항목은 "(원문에 명시 없음 — 가정으로 메움)" 으로 둡니다. -->

---

## 🧮 데이터 계약

시간 축은 절대 좌표가 아닌 의미 단위(`chunk_len` $`c`$, horizon $`k`$)로 기록합니다.

- **입력(정책 latent)** — `Z`: shape `(B, c, d_a)`, float32. 정책 backbone 이 내는 chunk latent 시퀀스($`c`$=chunk length, $`d_a`$=action 표현 차원). normalization = 데이터셋 action 통계로 표준화(원문 Table 2 는 학습 하이퍼만 명시, action 정규화 통계 출처는 미명시 — 가정으로 메움).
- **입력(reference 상태)** — `s_ref`: shape `(B, d_a)`, float32. delta 디코딩 기준 상태(chunk-wise=chunk 시작 시 로봇 상태). absolute 모드에서는 미사용.
- **입력(현재 joint)** — `q_t`: shape `(B, d_q)`, float32. task-space 모드의 IK 입력($`d_q`$=joint 차원). joint-space 모드에서는 미사용.
- **중간(디코딩 action)** — `A_tilde`: shape `(B, c, d_a)`, float32. temporal decode 결과(실행 표현 좌표, 아직 joint 미투영).
- **출력(joint command)** — `U`: shape `(B, k, d_q)`, float32. 실행할 joint command 시퀀스($`k\le c`$ = 배포 execution horizon). position-based low-level controller 가 인터페이스.
- **모드 플래그** — `temporal` = `absolute` 또는 `delta`; `delta_frame` = `chunk_wise` 또는 `step_wise`; `spatial` = `joint` 또는 `task`.

---

## 🧰 모듈 인터페이스

```python
def temporal_decode(Z, s_ref, temporal, delta_frame) -> A_tilde:
    """latent chunk Z 를 실행 action 시퀀스로 디코딩.
       absolute: a = Z (s_ref 무시)
       delta+chunk_wise: a_{t+k} = s_ref + Z[:,k]
       delta+step_wise:  a_{t+k} = s_ref + sum_{j<=k} Z[:,j]  (누적합)"""

def spatial_map(A_tilde, q_t, spatial, ik_solver) -> U:
    """실행 action 을 joint command 로 투영.
       joint: U = A_tilde (항등)
       task:  U = Phi_IK(A_tilde, q_t)  (현재 joint 의존 IK)"""

def decode_action_space(Z, s_ref, q_t, cfg, ik_solver) -> U:
    """temporal_decode -> spatial_map 2단계 합성. cfg 는
       (temporal, delta_frame, spatial, exec_horizon k) 를 보유."""
```

- `temporal_decode` — 손실/옵티마이저와 무관한 순수 디코딩. step_wise 만 chunk 내 누적(하삼각 연산자 `L_k`)이고 나머지는 element-wise.
- `spatial_map` — `ik_solver`(외부 IK, task 모드 전용)에만 의존. joint 모드는 호출 없음.
- 학습 손실은 표현 좌표(`A_tilde`/`Z`) 기준 — Regression(L2) 또는 Flow matching(velocity field) 으로 backbone 이 `Z` 를 생성. 디코딩/사상은 손실 바깥(배포 경로).

---

## ⛓️ 불변식·가정

- **(가정 1) 노이즈 전파 bound** — 예측 노이즈 $`\|\boldsymbol{\epsilon}\|_2\le\delta`$ 에 대해 chunk-wise delta·absolute 는 $`\|\mathbf{e}_a\|_2\le\delta`$ ($`\mathcal{O}(1)`$, $`\mathbf{M}=\mathbf{I}_k`$), step-wise delta 는 $`\|\mathbf{e}_a\|_2\le\frac{2k+1}{\pi}\delta`$ ($`\mathcal{O}(k)`$, $`\mathbf{M}=\mathbf{L}_k`$). 깨지면 horizon 확장 시 drift.
- **(가정 2) reference 정적성** — chunk-wise delta 의 $`\mathbf{s}^{\mathrm{ref}}_t`$ 는 chunk 구간 내 고정. 실행 중 reference 가 표류하면 $`\mathcal{O}(1)`$ bound 가 약화.
- **(가정 3) 운동학적 등가** — joint space 와 task space 는 FK/IK 로 등가지만, $`\Phi_{\mathrm{IK}}`$ 의 Jacobian $`\mathbf{J}^\dagger(\mathbf{q}_t)`$ 가 well-conditioned 일 때만 task-space 가 수치 안정. singularity 근방에서 깨짐.
- **(가정 4) horizon-abstraction 결합** — delta 는 짧은 $`k`$, absolute 는 긴 $`k`$ 에서 최적. open-loop 예측이라 $`k`$ 증가 시 변위 분산↑(variance growth) + $`I(\mathbf{a}^*_{t+k};\mathbf{o}_t)`$↓(information decay)로 조건부 엔트로피 증가.
- **(가정 5) 시간·공간 곱결합** — 전체 사상 $`\mathcal{T}_{\mathrm{total}}\approx(\mathbf{I}_k\otimes\mathbf{S}_t)\mathbf{M}_{\mathrm{time}}`$ — 안정성은 공간 Jacobian $`\mathbf{S}_t`$ 과 시간 연산자 $`\mathbf{M}_{\mathrm{time}}`$ 의 spectral 성질에 곱으로 좌우.

---

## 📊 하이퍼파라미터·손실

- 손실 식 (Regression): $`\mathcal{L}_{\mathrm{R}}=\mathbb{E}_{(\mathbf{o},\mathbf{a})\sim\mathcal{D}}[|\pi_{\theta}(\mathbf{o})-\mathbf{a}|^{2}]`$
- 손실 식 (Flow matching): $`\mathcal{L}_{\text{F}}=\mathbb{E}_{\tau\sim\mathcal{U}(0,1),(o,a)\sim\mathcal{D}}[\|v_{\theta}(a^{\tau},o,t)-(a-\epsilon)\|^{2}]`$, with $`\mathbf{x}_{\tau}=(1-\tau)\boldsymbol{\epsilon}+\tau\mathbf{a}`$
- 안정성 관계식: $`\|\mathbf{M}_{\mathrm{step}}\|_2=\sigma_{\max}(\mathbf{L}_k)\approx\frac{2k+1}{\pi}`$

| 이름 | 값 | 출처 |
|------|----|----|
| `optimizer` | `AdamW` | §D, Table 2 |
| `batch_size` | `512` | §D, Table 2 |
| `learning_rate` | `1e-4` | §D, Table 2 |
| `lr_scheduler` | `CosineAnnealingLR` | §D, Table 2 |
| `weight_decay` | `0.01` | §D, Table 2 |
| `betas` | `(0.9, 0.95)` | §D, Table 2 |
| `precision` | `float32` | §D, Table 2 |
| `image_size` | `224x224` | §D, Table 2 |
| `image_aug` | `ColorJitter(0.2,0.2,0.2,0)` | §D, Table 2 |
| `train_horizon k` | `60` (2s @30Hz) | §4.1.2 |
| `exec_horizon (delta)` | `30` | §4.2 |
| `exec_horizon (absolute)` | `60` | §4.2 |
| `train_epochs` | `600` (RQ2) / 600·900·1200 (RQ3) | §4.2, §4.3.1 |
| `demos/task` | `250` (real) / `50` (sim) / 100·250·500 (scaling) | §4.2, §4.3.1 |
| `pi0 transfer` | LoRA, 30k step, batch 32 | §E.3 |

---

## 🎯 평가 메트릭

- **지표** — `progress score`(real-world) / `success rate`(simulation) · **측정** — trial 3회 × rollout 10회 평균, $`6\times6`$ grid 표준화 초기화 · **비교 baseline** — 2×2 action space(EE/Joint × abs/delta) 교차 + ACT(Regression)/DP(Flow matching) 두 패러다임.
- **핵심 비교 임계** — chunk-wise delta vs step-wise delta 평균 격차 ≳ 10%p(§4.1.1); Overall Avg 최고 = Joint-delta(DP) 88.0±2.3(§4.2, Table 1).

---

## ✨ 변경 의도 (intent)

기존 정책 연구가 action 표현을 코드베이스 legacy 로 *물려받던* 관행을, temporal(absolute/delta·chunk_wise/step_wise·horizon $`k`$) × spatial(joint/task) 두 직교 축의 **통제된 설계 변수** 로 끌어올립니다. baseline 대비 새로움은 알고리즘이 아니라 (1) chunk-wise delta 의 노이즈 $`\mathcal{O}(1)`$ bound 라는 *이론적 분리*, (2) horizon-abstraction *결합* 의 실증, (3) "joint=단일 임베디먼트 안정성 / task=cross-embodiment 일반화" 라는 *조건부 우월성* 의 대규모 검증에 있습니다. 즉 같은 backbone·손실이라도 이 디코딩/사상 계약을 어떻게 설정하느냐로 15%p 급 성능차가 난다는 것이 핵심 주장입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — backbone 자체보다 **action 디코딩/사상 + 정규화 경로** 에 매핑됩니다. chunk-wise vs step-wise delta·joint vs EE 좌표·exec horizon 은 `act`/`diffusion`/`pi0` family 공통의 action chunking·normalization·delta-timestep 처리 지점에 해당하므로, 특정 policy family 보다 **공통 action processing/transform 계층** 후보. 손실(MSE↔`act`, flow matching↔`pi0`/`diffusion`)은 family 별로 갈림.

---

## 🚧 미해결 / 잠정

- action 정규화 통계의 출처가 본문에 명시되지 않아 "데이터셋 전체 action 평균/표준편차" 로 가정.
- chunk-wise delta 의 reference 상태 $`\mathbf{s}^{\mathrm{ref}}_t`$ 가 "chunk 시작 시 로봇 상태" 임은 명시되나, 그 상태가 measured proprio 인지 예측 상태인지의 세부는 본문에 불명확 — measured 로 가정.
- task-space 의 $`\Phi_{\mathrm{IK}}`$ 구체 solver(해석적 vs differential IK)는 일반 형식만 제시, 구현 detail 미명시.
- hybrid/adaptive action space(phase 별 표현 전환)는 §B 에서 future work 로만 언급 — Layer 1 스펙으로 굳히지 않음.
