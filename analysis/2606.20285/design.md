# Design — Co-VLA: Coordination-Aware Structured Action Modeling for Dual-Arm Vision–Language–Action Systems

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Co-VLA: Coordination-Aware Structured Action Modeling for Dual-Arm Vision–Language–Action Systems |
| 링크 | [arXiv:2606.20285](https://arxiv.org/abs/2606.20285) |
| 분석 문서 | [`analysis/2606.20285/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-22 |

---

## 🧮 데이터 계약

- **입력** — `hidden_state`: $`h_t\in\mathbb{R}^{H}`$, shape `(B, T_action, H)`, VLA transformer hidden representation (정규화는 backbone 내부, 본 모듈은 raw hidden 가정).
- **입력(보조손실용)** — `expert_velocity`: $`u_{t,L},u_{t,R}\in\mathbb{R}^{7}`$, dataset joint-velocity 타깃 ($`\mathcal{L}_{\text{shared}}`$ 의 $`\bar{u}_t`$ 계산용).
- **출력(SAE)** — `action`: $`a_t=[a_{t,L},a_{t,R}]\in\mathbb{R}^{14}`$, shape `(B, T_action, 14)`, 양팔 joint velocity. 내부적으로 shared/residual 4-tuple $`\{a^s_{t,L},a^s_{t,R},a^r_{t,L},a^r_{t,R}\}`$ (각 $`\mathbb{R}^7`$) 도 노출 (LAC 입력).
- **출력(LAC)** — `refined_action`: $`\tilde{q}_t\in\mathbb{R}^{14}`$, shape `(B, H, 14)`, 배포 시 저역통과 정제된 joint command.
- **latent 차원** — shared/residual latent $`z\in\mathbb{R}^{L}`$ (L 은 원문 미명시 — `(원문에 명시 없음 — 가정으로 메움)`, hidden 대비 작은 bottleneck 가정).

---

## 🧰 모듈 인터페이스

```python
def structured_action_expert(h_t):  # SAE
    """단일 hidden state → shared/residual latent → 가법 합성 joint command.
    반환: action[14], 그리고 LAC 용 (a_s_L, a_s_R, a_r_L, a_r_R) 각 [7]."""
    z_s, z_L, z_R = g_s(h_t), g_L(h_t), g_R(h_t)      # 세 latent 디코더
    a_s_L, a_s_R = phi_s_L(z_s), phi_s_R(z_s)          # shared → 좌/우 별도 head
    a_r_L, a_r_R = phi_r_L(z_L), phi_r_R(z_R)          # residual → 좌/우 별도 head
    return (a_s_L + a_r_L, a_s_R + a_r_R), (a_s_L, a_s_R, a_r_L, a_r_R)

def coordination_aux_loss(a_s, a_r, u, regime):
    """regime ∈ {sparse, shared, sync} 에 따라 보조손실 하나 선택."""

def latent_aware_controller(q_chunk, latents):  # LAC, 학습 없음 (배포 시)
    """energy/opposition 으로 adaptive stiffness → 1차 low-pass 정제."""
```

- **SAE** — 역할: monolithic projector 교체. 입력 $`h_t`$, 출력 양팔 action + latent 4-tuple. backbone 동결 가능(Phase 1).
- **coordination_aux_loss** — $`\mathcal{L}_{\text{action}}`$ 에 가중 $`\lambda`$ 로 더해짐. regime 은 task-level 사전지식으로 *수동* 선택(약점).
- **LAC** — 추가 학습 모듈 없음, 정책 미수정. SAE 의 latent 분해만 읽어 stiffness $`\alpha_t`$ 변조 후 joint command 정제. standard joint-command 파이프라인 호환, force/impedance 불요.

---

## ⛓️ 불변식·가정

- (가정 1) 최종 명령은 shared + residual 의 **가법** 합성 $`a_{t,\cdot}=a^s_{t,\cdot}+a^r_{t,\cdot}`$ — 두 성분이 같은 joint-velocity 공간에서 합산 가능해야 함(단위·스케일 동일).
- (가정 2) shared latent 은 양팔 *공통* 의도를 인코딩 — $`\mathcal{L}_{\text{shared}}`$ 가 의미를 가지려면 좌·우 출력이 평균속도 $`\bar{u}_t`$ 를 공유할 수 있는 대칭/공통-운반 구조여야 함.
- (가정 3) residual energy 는 대부분 스텝에서 shared 대비 작음($`\rho_t`$ 작음) — LAC 의 macro-dominant 판정과 micro-adjustment 보호 논리의 전제.
- (가정 4) 의미 있는 협응 = 좌·우 residual 의 *반대 방향성*($`\omega_t`$ 큼); 무질서한 residual = 노이즈 — opposition 휴리스틱의 핵심 가정.
- (가정 5) 보조손실 regime 이 task 당 하나로 라벨링 가능(near-symmetric / asymmetric / temporal 중 지배적 1종).

---

## 📊 하이퍼파라미터·손실

- 손실 식:
  - $`\mathcal{L}=\mathcal{L}_{\text{action}}+\lambda\,\mathcal{L}_{\text{aux}}`$
  - $`\mathcal{L}_{\text{sparse}}=\mathbb{E}_t[\|a^r_{t,L}\|_1+\|a^r_{t,R}\|_1]`$
  - $`\mathcal{L}_{\text{shared}}=\mathbb{E}_t[\|a^s_{t,L}-\bar{u}_t\|_2^2+\|a^s_{t,R}-\bar{u}_t\|_2^2]`$, $`\bar{u}_t=\tfrac12(u_{t,L}+u_{t,R})`$
  - $`\mathcal{L}_{\text{sync}}=1-\mathbb{E}_t[\tilde{m}_{t,L}\tilde{m}_{t,R}]`$, $`m_{t,\cdot}=\|\Delta a_{t,\cdot}\|_2`$
- LAC: $`\rho_t=E^r_t/(E^s_t+\varepsilon)`$, $`\omega_t=-\cos(a^r_{t,L},a^r_{t,R})`$, $`\alpha_t=(1-\beta)\alpha_{t-1}+\beta\hat{\alpha}_t`$, $`\tilde{q}_t=(1-\alpha_t)\tilde{q}_{t-1}+\alpha_t q_t`$

  | 이름 | 값 | 출처 |
  |------|----|----|
  | `lambda` ($`\lambda`$) | `0.001` | §III-A, Eq. (4) |
  | Phase1 steps / LR | `1000` / `5e-5` (backbone freeze) | §IV-A |
  | Phase2 steps / LR | `30000` / `2.5e-5`→`2.5e-6` decay (full unfreeze) | §IV-A |
  | batch / 분산 | `32` / 4-GPU FSDP | §IV-A |
  | `alpha_base` | `0.4` | §IV-C |
  | `delta_macro` / `delta_prec` / `delta_noise` | `0.4` / `0.3` / `0.1` | §IV-C |
  | `tau_rho` / `tau_omega` | `0.01` / `0.3` | §IV-C |
  | `beta` | `0.2` | §IV-C |
  | `[alpha_min, alpha_max]` | `[0.05, 0.95]` | §IV-C |
  | latent 차원 `L` | `(원문 미명시)` | — |

---

## 🎯 평가 메트릭

- **지표** — task success rate(%) · **임계값** — baseline 초과(higher better) · **비교 baseline** — π₀, π₀.₅ (sim); π₀, Co-VLA(noLAC), EMA filter (실세계/ablation).
- **보조 지표** — 완료시간(s, lower better; Table III), 시연 생성시간(s; Table II), latent–behavior 상관($`E^s_t`$–$`\mathrm{Sync}_t`$ 양상관 / $`E^r_t`$ 음상관; Fig. 5), trajectory 가속 peak·cross-rollout variance(Fig. 6).
- **평가 프로토콜** — sim 100 rollout(Easy/Hard, scene randomization 증가), 실세계 30 rollout(ID/OOD).

---

## ✨ 변경 의도 (intent)

기존 VLA 는 양팔 14-DoF 를 단일 벡터로 직접 회귀해 "task-level 협응 의도"와 "팔별 실행 보정"을 한데 뭉칩니다. Co-VLA 는 monolithic projector 를 *shared latent(공통 협응) + 좌·우 residual latent(보정)* 의 가법 분해로 교체해 협응을 **action 위의 구조**로 명시화하고, regime 별 보조손실로 그 분해가 의미를 갖도록 형태를 잡습니다. 핵심 차별점은 (1) gating/cross-attention(LaMP) 대신 *가법 합성 + 손실 기반 의미 형성*, (2) anatomical split(DexGrasp-VLA) 과 직교하는 *shared coordination 축*의 추가, (3) 학습 없이 배포 시 latent 의 energy·opposition 만으로 stiffness 를 변조하는 LAC — EMA 의 균일 평활이 지우는 precision-critical residual 을 선택적으로 보존하는 deployment-side 기여입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 후보 base: `pi0` / `pi05`. SAE 는 π₀ flow-matching action expert 의 최종 projector 를 shared/residual 병렬 디코더로 교체하는 형태라 `pi0` family 의 action head 가 직접적 매핑 지점. LAC 는 정책 외부의 배포-시 후처리라 inference/control wrapper 로 분리 매핑 가능.

---

## 🚧 미해결 / 잠정

- shared/residual latent 차원 `L`, 각 latent 디코더·projection head($`g_s,g_L,g_R,\phi`$)의 구체 구조(MLP 깊이·activation)는 원문 미명시 — 구현 시 가정 필요.
- $`\mathcal{L}_{\text{shared}}`$ 의 타깃 평균속도 $`\bar{u}_t`$ 가 dataset GT velocity 인지 예측값인지 본문 표기상 GT($`u_{t,\cdot}`$)로 해석했으나 확정 어려움.
- 보조손실 regime 의 *자동* 라우팅은 미구현(future work); 본 Design 은 수동 regime 라벨 가정.
- $`\mathcal{L}_{\text{action}}`$ 의 구체 형태(flow-matching loss 가정)는 backbone 의존 — 본문 명시 없음.
- LAC 파라미터는 실세계 task 간 공유값으로 고정; 다른 embodiment 로의 이식 시 재튜닝 필요(원문 미평가).
