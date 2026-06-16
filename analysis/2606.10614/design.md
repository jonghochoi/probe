# Design — Dexterous Point Policy: Learning Point-based Dexterous Hand Policies from Human Demonstrations

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Dexterous Point Policy: Learning Point-based Dexterous Hand Policies from Human Demonstrations |
| 링크 | [arXiv:2606.10614](https://arxiv.org/abs/2606.10614) |
| 분석 문서 | [`analysis/2606.10614/analysis.md`](./analysis.md) |
| 본문 확보 수준 | PDF 텍스트(PyMuPDF) |
| Design 생성일 | 2026-06-16 |

---

## 🧮 데이터 계약

시간 축은 의미 단위(`H` = action horizon, `K` = 6 keypoints)로 기록합니다. 좌표는 world frame 3D(배포 시 정적 카메라라 camera frame = world frame).

- **입력 — 언어 지시** — `L`: 자연어 1개 → Sentence Transformer(Sentence-BERT) 인코딩 → shape `(B, d_model)` 단일 토큰.
- **입력 — 객체 점** — task-relevant 객체당 (semantic 토큰, geometry 토큰) 2개. semantic = 객체명 텍스트 인코딩 `(B, d_model)`; geometry = mask 당 128점 3D → PointNet → `(B, d_model)`. 객체 최대 `N_obj = 4`(총 8 토큰), 빈 slot 은 zero embedding. 점 좌표 dtype `float32`, world 좌표(depth lift + extrinsics).
- **입력 — 손 키포인트** — `H_t`: 6 키포인트(wrist, thumb, index, middle, ring, pinky 고정 순서) × 3D → 18-dim concat → hand projector $`\phi_{hand}`$ → `(B, d_model)`. fine-tuning 시 contact projector 출력과 합산해 단일 contact-aware hand token.
- **입력 — contact 주석(fine-tuning only)** — `c_t`: shape `(B, 5)`, binary `{0,1}`, index `[thumb, index, middle, ring, pinky]`. 2-layer MLP $`\phi_{contact}`$ (마지막 linear zero-init) → `(B, d_model)`, 손 임베딩에 가산.
- **입력 — 카메라 extrinsics** — 1 토큰 추가(배포 시 identity).
- **출력 — 손 궤적** — $`\hat{H}_{t+h}`$: shape `(B, H, 6, 3)`, `float32`, world 좌표. action head $`\psi_{act}`$, autoregressive(step `h` 예측을 `h+1` 입력으로 되먹임).
- **출력 — contact 확률(fine-tuning only)** — $`\hat{p}_{t+h}`$: shape `(B, H, 5)`, `[0,1]`(logit→sigmoid). contact head $`\psi_{ct}`$, backbone 에서 gradient detach.

정규화: 본문에 명시적 통계 출처 없음 — `(원문에 명시 없음 — 가정으로 메움)`. fine-tuning IK supervision 은 6개 로봇 키포인트에만 손실 적용, 객체 점 토큰은 무지도.

---

## 🧰 모듈 인터페이스

```python
def extract_points(image, lang, depth, intrinsics, extrinsics) -> tuple:
    """초기 frame + 지시문 → (object_points[N_obj,128,3], hand_points[6,3]).
       VLM 객체식별 → SAM3 segmentation+memory 추적 → mask당 128점 → depth 3D lift."""

def policy_forward(lang_tok, obj_tokens, hand_tok, extr_tok, horizon_H) -> tuple:
    """tokenized 관찰 → autoregressive 로 (Ĥ[H,6,3], p̂[H,5]) 예측.
       teacher forcing(train) / 자기예측 되먹임(infer)."""

def hand_projector(hand_18d) -> token: ...        # ϕ_hand: 18 → d_model
def contact_projector(c_5d) -> token: ...         # ϕ_contact: 5 → d_model, 마지막 linear zero-init
def action_head(hidden) -> kp_6x3: ...            # ψ_act
def contact_head(hidden) -> logits_5: ...         # ψ_ct, backbone gradient stop

def deploy_step(Ĥ, p̂, robot_urdf, joint_state) -> joint_targets:
    """예측 6점 → damped-LS position-only IK(wrist+5 fingertip site 추종) → 관절 목표.
       p̂ → sigmoid → threshold → per-finger grip bit → closing offset smooth ramp-in(힘 주입).
       20 Hz 실행."""
```

- `policy_forward` 는 backbone(autoregressive transformer, GPT-style)을 공유하고 두 head 를 병렬 호출. $`\psi_{ct}`$ 의 gradient 는 backbone 과 $`\phi_{contact}`$ 로 전파되지 않음($`\mathcal{L}_{ct}`$ 는 $`\psi_{ct}`$ 만 갱신).
- $`\phi_{contact}`$ 는 $`\mathcal{L}_{act}`$ 가 공유 hand token 을 거쳐 backward 될 때만 학습.

---

## ⛓️ 불변식·가정

- **(가정 1) keypoint 공유성** — 사람 손과 로봇 end-effector 가 동일한 6-키포인트(wrist + 5 fingertip) 추상화로 기술되어, 사람 데이터로 예측된 궤적이 retargeting 없이 로봇 목표로 직접 해석 가능해야 함. 이 정렬이 깨지면 알고리즘의 zero-robot-data 전제가 무효.
- **(가정 2) keypoint 정지 ⇒ 점 정보 한계** — 접촉 성립 후 손·객체 키포인트는 멈추므로 point-only 관찰은 light touch 와 firm grasp 를 구분 못 함. 따라서 force 는 별도 contact 채널로만 표현 가능(설계 동기이자 한계).
- **(가정 3) contact 의 저차원성** — 접촉은 fingertip-object 근접도에서 추론 가능한 저차원 신호라, 사전학습에 contact 가 없어도 소량 fine-tuning 으로 학습됨.
- **(가정 4) IK 도달성** — 예측 6점이 로봇 URDF 의 wrist+fingertip site 로 damped-LS IK 해를 가져야 함. 기구학적 비실현 궤적은 IK residual 로 누수.
- **(가정 5) zero-init 보존** — $`\phi_{contact}`$ 마지막 linear 의 zero-init 으로 fine-tuning 시작 시 사전학습 hand token 이 정확히 복원(prior 비교란).

---

## 📊 하이퍼파라미터·손실

**손실 — 사전학습(식 1)**, $`K=6`$, $`H=16`$:

$$\mathcal{L}_{act} = \frac{1}{B H K} \sum_{b=1}^{B} \sum_{h=1}^{H} \sum_{k=1}^{K} \ell_1\!\left(\hat{H}^{(b)}_{t+h,k} - H^{(b)}_{t+h,k}\right)$$

**손실 — fine-tuning(식 2)**, $`\lambda=1`$, $`w_+`$ = positive-class weight:

$$\mathcal{L}_{ft} = \mathcal{L}_{act} + \lambda \mathcal{L}_{ct}, \quad \mathcal{L}_{ct} = \mathrm{BCE}_{w+}(\hat{p}, c)$$

| 이름 | 값 | 출처 |
|------|----|----|
| `optimizer` | AdamW | §A |
| `lr` | `1e-4` | §A |
| `weight_decay` | `1e-4` | §A |
| `global_batch (pretrain)` | `256` | §A |
| `pretrain_steps` | `100k` | §A |
| `precision` | bf16(fwd/loss) + fp32(opt step) | §A |
| `grad_clip` | $`\|g\| \le 1`$ | §A |
| `warmup` | LinearLR, start_factor `1e-2`, 1k step | §A |
| `chunk Q` / horizon `H` | `16` / `16` | §A, §3.3 |
| `K` keypoints | `6` | §3.3, Eq.(1) |
| $`\lambda`$ (contact) | `1` | §3.3, Eq.(2) |
| `finetune_steps` | `400k` | §A |
| `batch (P&P / Tool)` | `128` / `64` | §A |
| `contact_head_detach` | True | §3.3, §A |
| `N_obj` cap / tokens | `4` / `8` | §3.3 |
| `points per mask` | `128` | §3.2 |
| `control rate` | `20 Hz` | §3.4 |
| `IK` | position-only damped least-squares | §3.4 |
| pretrain compute | 1× A100(80GB), ~36 GPU-h | §A |
| finetune compute | ~4 h / task (A100) | §A |

외부 모델: Qwen3.5-VL-8B-Instruct(객체식별), SAM3(segmentation), Depth-Anything-3(사전학습 depth) / ZED stereo(fine-tune·배포), HaWoR→scale-consistent(손 추적), Sentence-BERT(텍스트), PointNet(점). 정규화 통계 출처 `(원문 미명시)`.

---

## 🎯 평가 메트릭

- **지표** — single-attempt success rate(%) · **임계값** — human evaluator 의 태스크별 성공 기준(예: P&P = 객체가 컨테이너 안에 정지; 1~3분 timeout) · **비교 baseline** — Point Policy(6-키포인트화), VITRA(joint-space VLA, IK supervision).
- 프로토콜: 태스크당 24 trial(P&P 는 4 위치 × 6, 총 120). 일반화: multi-object / novel-object 동일 24 trial.
- 주요 수치(본문): DPP avg 75.0%(8 task), P&P 81.7%, multi-object 80.0%, novel 76.7%. ablation w/o AR 37.5%, w/o Pretrain 67.5%(vs full 81.7%).
- (부록 G, 분리) sim residual RL: base 52.2% → 74.7%(anchor-balanced, 4 seed).

---

## ✨ 변경 의도 (intent)

선행 Point Policy/Point Bridge 는 관찰·행동을 모두 키포인트로 두되 **두 손가락 gripper** 에 한정되어, 사용자가 gripper 흉내 자세를 취한 특수 사람 영상에만 학습이 묶이고 인터넷 규모 일반 영상을 못 썼습니다. 본 설계의 변경 의도는 세 가지입니다. (i) gripper-centric 표현을 **wrist + 5 fingertip 6-키포인트 다지 손 추상화**로 일반화해 일반 사람 영상을 사전학습 재료로 끌어옴. (ii) point-only 가 구조적으로 표현 못 하는 **force 모달리티**를, 손끝 binary contact 를 손 token 에 융합(zero-init)하고 별도 head 로 공동 예측(backbone gradient detach)하는 **비교란·경량 주입**으로 복원. (iii) 비인과 병렬 디코딩 대신 **autoregressive rollout** 으로 chunk 를 생성해 다지 손 협응의 시간적 일관성을 확보. 결과적으로 로봇 teleoperation·co-training·fine-tuning 을 어느 단계에도 쓰지 않고 사람 영상만으로 다지 정책을 학습합니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 정확한 base 가 없는 **신규 아키텍처**(keypoint 관찰·행동 + autoregressive transformer + contact head)라 기존 family 와 1:1 대응이 어렵습니다. 굳이 고르면 시퀀스 토큰화·transformer 백본이라는 점에서 `pi0`/`pi0_fast`(autoregressive/transformer 계열)에 구조적으로 가깝고, action chunk 회귀라는 점에서 `act` 의 chunking 학습 루프를 부분 참조 가능. 단 입력이 이미지가 아니라 **PointNet 점 토큰 + 키포인트**이고 출력이 flow-matching 이 아닌 직접 회귀라, observation/action 파이프라인은 대부분 신규 구현이 필요. `/implement-design` 가 실제 매핑 가능 여부를 판정.

---

## 🚧 미해결 / 잠정

- **정규화 통계 출처** — 키포인트·점 좌표의 정규화 가정이 본문에 없어 `(원문 미명시)`. residual RL(부록 G)은 action scaler `g` 를 successful offline rollout 에서 1회 fit 한다고만 명시.
- **VITRA arXiv id** — baseline·사전학습 corpus 인 VITRA(ref [25])의 정확한 arXiv id 가 본문에서 식별되지 않음(ICRA 2026 표기). 인용 시 확인 필요.
- **backbone 규모** — autoregressive transformer 의 정확한 layer/width/parameter 수, `d_model`, attention mask 세부가 본문(PDF)에 명시되지 않음.
- **IK 세부** — damped least-squares 의 damping 계수, site 정의, 수렴 기준 미명시.
- **contact threshold·ramp** — sigmoid threshold 값과 closing offset ramp 속도/크기 미명시.
- **scale-consistent HaWoR** — shape 평균 $`\bar\beta`$ 산출(HaMeR) 외 학습 세부는 부록 F 수준에서만 기술.
- **부록 G residual RL** 은 메인 파이프라인과 분리된 sim-only 보조 실험 — Layer 1 핵심 알고리즘에는 포함하지 않음(Table 5–7 하이퍼는 분석 문서 참조).
