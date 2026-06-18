# Design — $`\mu_0`$: A Scalable 3D Interaction-Trace World Model

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | $`\mu_0`$: A Scalable 3D Interaction-Trace World Model |
| 링크 | [arXiv:2606.13769](https://arxiv.org/abs/2606.13769) |
| 분석 문서 | [`analysis/2606.13769/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-17 |

---

## 🧮 데이터 계약

시간 축은 의미 단위로 기록합니다 — `h`(history horizon), `H`(future horizon), `N`(query keypoint 수, 가변), `D`(B-spline 제어점 수), `T_action`(action chunk 길이).

**World model ($`\mu_{0}`$) 학습 단계**

- **입력 — RGB**: `I_rgb` shape `(B, 3, 512, 512)`, float, ImageNet/VLM 통계 정규화(ColorJitter s=0.3 증강).
- **입력 — Depth (선택)**: `I_dep` shape `(B, 3, 512, 512)`, metric depth 를 Turbo colormap 으로 RGB 렌더; meter 도메인에서 σ=0.01m Gaussian noise 후 colormap. 학습 시 확률 0.7 로 생략.
- **입력 — 언어**: `l` 토큰 시퀀스(event/merged task 캡션), VLM tokenizer.
- **입력 — Query keypoints**: `Q` shape `(B, N, ...)`, $`N \in [1, 256]`$ uniform 샘플; 각 query 는 현재 픽셀 위치 + 국소 DINO feature 로 토큰화.
- **입력 — Past trace history**: `H_hist` shape `(B, N, h, 3)`, `h=8`, reference 카메라 3D(anchor 차감: $`\mathbf{H} \leftarrow \mathbf{H} - \mathbf{c}`$). two-level dropout(전체 0.2 / keypoint별 0.3).
- **출력 — B-spline 제어점**: `P_hat` shape `(B, N, D, 3)`, `D=10`, anchor-relative·per-axis 95th-percentile scale $`\mathbf{s}_{\Delta}`$ 정규화, post-fit clip $`|\mathbf{P}| \leq 1.5`$.
- **출력 — Validity logits**: `(B, N, H)`, per-step trajectory 유효성(sigmoid).
- **디코딩 — 3D trace**: $`\hat{\mathbf{T}}^{1} = \mathbf{B}\hat{\mathbf{P}}`$ shape `(B, N, H, 3)`, reference 카메라 좌표 `(x,y,z)`(uv 는 [-1,1], z 는 metric meter).

**Action expert 단계 (downstream, embodiment별)**

- **입력 — Frozen trace feature**: `z_trace` = frozen $`\mu_{0}`$ 의 단일 partial-denoising step 중간 hidden state.
- **입력 — Gripper-camera 이미지**: DINOv2 인코딩.
- **입력 — Proprioception**: MLP 매핑.
- **입력 — 언어**: VLM tokenizer.
- **출력 — Action chunk**: `(B, T_action, action_dim)`, flow-matching 으로 생성된 연속 action(예: UR3 + 2-finger gripper).

---

## 🧰 모듈 인터페이스

```python
def trace_extract(video) -> list[tuple]:
    """uncurated 비디오 → {I_t, l_c, Q_t, T_ref^{t-h:t+H}} triplet.
       (1) DINOv2 entity 클러스터 keypoint 선택 + movement filter,
       (2) VGGT global-local 3D 재구성 + TAPIP3D progressive 추적,
       (3) Savitzky-Golay accel valley 로 event 분절 후 VLM 계층 캡셔닝."""

def mu0_predict(I_rgb, I_dep, l, Q, H_hist) -> (P_hat, validity):
    """query-conditioned 3D trace world model.
       SmolVLM2 prefix(frozen) + permutation-equivariant Trace Expert,
       conditional flow matching 으로 B-spline 제어점 P 예측."""

def trace_velocity(P_tau, tau, F_cond) -> v:
    """adaLN-Zero 로 flow-time τ 주입, control-point velocity (ε − P*) 예측."""

def action_expert(z_trace, gripper_img, proprio, l, a_noisy, tau) -> v_action:
    """frozen z_trace 를 gated cross-attention 으로 VLM feature 에 융합,
       π0.5 self-attn 구조로 연속 action chunk velocity 예측."""
```

- **`trace_extract`** — 데이터 엔진. 출력 triplet 이 `mu0_predict` 의 학습 supervision. 외부 의존: DINOv2, VGGT, TAPIP3D, VLM/LLM 캡셔너.
- **`mu0_predict`** — VLM(frozen) + Trace Expert(학습). 손실 $`\mathcal{L} = \mathcal{L}_{\text{flow}} + \lambda_{\text{done}}\mathcal{L}_{\text{done}} + \lambda_{\text{rig}}\mathcal{L}_{\text{rig}}`$. permutation-equivariant 이므로 query 순서 불변.
- **`trace_velocity`** — flow 네트워크 $`v_{\theta}`$. 4-step Euler 로 적분.
- **`action_expert`** — downstream 정책. frozen `mu0_predict` 위에서만 학습; gate `g` 0-init 으로 약-주입 시작. 손실 `L_action`(flow matching).

---

## ⛓️ 불변식·가정

- **(가정 1) Permutation equivariance** — query keypoint 집합 `Q` 의 임의 순열에 대해 예측 `P_hat` 이 동일하게 순열되어야 함(순서 의존 금지). 깨지면 trace world model 의 "exchangeable query" 전제가 무효.
- **(가정 2) Global-frame 3D 일관성** — 모든 chunk 의 trace 가 단일 global 좌표계(공유 `K_global`, sparse anchor SE(3) 정렬)에 놓여야 함. chunk 간 정렬 오차가 누적되면(독립·유계 가정 붕괴) z 축 metric 정합이 무너짐.
- **(가정 3) Anchor-relative target 분포** — 미래 target 은 current anchor 를 빼고 per-axis 95th-percentile $`\mathbf{s}_{\Delta}`$ 로 rescale 해 unit-Gaussian noise prior 와 분산이 정합되어야 함. 정규화가 어긋나면 flow matching 의 noise↔data 경로가 부정합.
- **(가정 4) Part-rigidity** — 같은 DINO 클러스터 keypoint 쌍의 control-point 거리는 시퀀스에 걸쳐 분산이 작아야 함(강체 part 가정). 비강체 객체에서는 약화되며 손실 가중으로만 soft 강제.
- **(가정 5) Trace = action proxy** — 의미적 상호작용 점들의 3D 궤적이 downstream action 생성에 충분한 motion 정보를 담는다는 가정. force/tactile/contact-mode 가 지배하는 task 에서는 깨질 수 있음(분석 ⚖️ 한계 참조).

---

## 📊 하이퍼파라미터·손실

- **World model 손실** (§B.3, Eq. 6–10), valid·present keypoint 한정:

$$\mathcal{L}=\mathcal{L}_{\text{flow}}+\lambda_{\text{done}}\mathcal{L}_{\text{done}}+\lambda_{\text{rig}}\mathcal{L}_{\text{rig}}$$

$$\mathcal{L}_{\text{flow}}=\mathbb{E}_{\tau,\mathbf{\epsilon}}\left[\left\|v_{\theta}(\mathbf{P}^{\tau},\tau,F_{\text{cond}})-(\mathbf{\epsilon}-\mathbf{P}^{\star})\right\|_{2}^{2}\right],\qquad \mathbf{P}^{\tau}=\tau\mathbf{\epsilon}+(1-\tau)\mathbf{P}^{\star}$$

$$\mathcal{L}_{\text{done}}=\frac{\sum_{t=1}^{H}\ell_{\text{BCE}}(\hat{d}_{n,t},y_{n,t})}{N},\qquad \mathcal{L}_{\text{rig}}=\mathbb{E}_{\tau,\mathbf{\epsilon}}\left[\frac{1}{|R|}\sum_{(n,n^{\prime})\in R}\mathrm{Var}_{d}\left(\left\|\hat{\mathbf{P}}_{n,d}-\hat{\mathbf{P}}_{n^{\prime},d}\right\|_{2}^{2}\right)\right]$$

- **Action 손실** (§B.4, Eq. 11–12):

$$\mathcal{L}_{\text{action}}=\mathbb{E}_{\tau,\mathbf{a},\mathbf{\epsilon}_{a}}\left\|v_{\phi}\!\left(\mathbf{a}^{\tau},\tau,\mathbf{z}_{\text{guided}},\mathbf{c}\right)-(\mathbf{a}-\mathbf{\epsilon}_{a})\right\|_{2}^{2},\qquad \mathbf{z}_{\text{guided}}=\mathbf{z}+\sigma(g)\cdot\mathrm{CA}\!\left(Q=\mathrm{LN}(\mathbf{z}),\;K=V=\tilde{\mathbf{h}}_{\text{trace}}\right)$$

| 이름 | 값 | 출처 |
|------|----|----|
| $`\lambda_{\text{done}}`$ | (원문에 가중 수치 미명시 — 항 존재) | §B.3, Eq. 10 |
| $`\lambda_{\text{rig}}`$ | (원문에 가중 수치 미명시 — ablation 으로 효과 검증) | §B.3, Eq. 9–10 |
| $`\lambda_{\text{bsp}}`$ | `0.2` | §B.2, Eq. 4 |
| $`\lambda_{z}`$ (movement filter depth weight) | `0.1` | §A.2 |
| $`\tau_{m}`$ (moving threshold) | `40` px | §A.2 |
| `h` (history horizon) | `8` | §B.2 |
| `H` (future horizon) | `32` | §B.2 |
| `D` (B-spline 제어점) | `10` (degree 3) | §B.2 |
| $`|\mathbf{P}^{\star}|`$ clip | $`\leq 1.5`$ | §B.2 |
| $`\mathbf{s}_{\Delta}`$ | per-axis 95th-percentile (corpus 1회 precompute) | §B.2, Eq. 3 |
| `L_vlm` (VLM truncate layer) | `20` | §B.1 |
| Trace Expert depth / width | `20` layer / `0.5×` VLM | §B.1 |
| cross-attn interleave | 매 2 layer | §B.1 |
| 이미지 해상도 | `512×512` | §B.1 |
| optimizer | AdamW, lr `1e-4`, wd `1e-10` | §B.1 |
| effective batch | `24` | §B.1 |
| `N` (keypoint/sample) | `[1, 256]` uniform | §B.1 |
| ColorJitter `s` / depth noise $`\sigma_{d}`$ | `0.3` / `0.01` m | §B.1 |
| history dropout (전체/개별) | `0.2` / `0.3` | §C.1 |
| depth dropout | `0.7` | §C.1 |
| inference solver | 4-step Euler ($`\tau\in[1,0]`$) | §B.3–B.4 |
| backbone / action expert arch | SmolVLM2-2.2B / π0.5 self-attn | §B.1, §B.4 |

---

## 🎯 평가 메트릭

- **지표** — moving-point 한정 `minADE` / `minFDE` / `minDTW`(+ appendix `minFD` Fréchet), top-1·top-5(S 샘플 중 최소). `(u,v,z)` 공간, uv∈[-1,1], z metric meter. · **임계값** — horizon $`T\in\{8,16,32\}`$ 별 비교(낮을수록 좋음) · **비교 baseline** — 2D: Track2Act, Hamster, Gemini/GPT(API); 3D: 3DFlowAction, Dream2Flow, TraceGen.
- **Downstream action** — 성공률(%). 시뮬: RoboCasa365 8 task(vs Diffusion Policy, π0, π0.5, TraceGen+AE). 실로봇: UR3 3 task, 각 20 rollout(vs VLM+AE, π0, π0.5, TraceGen).
- **효율** — single A6000 GPU 추론 latency(slot 당, $`\mu_{0}`$ 0.29s).

---

## ✨ 변경 의도 (intent)

기존 world model 은 픽셀(용량 낭비·geometry 손실) 또는 직접 action(embodiment 라벨 종속)을 예측합니다. $`\mu_{0}`$ 는 그 중간인 *의미적 상호작용 점들의 미래 3D trace* 를 예측해 compact·metric·embodiment-agnostic 한 motion interface 를 만듭니다. 선행 TraceGen 의 fixed-grid·episode-캡션·inference-depth 의존 3대 한계를, semantic keypoint 선택 + global-frame 3D 추적 + event-level 캡션 + depth-optional 로 교체하고, 미래 다중성을 평균내지 않도록 B-spline 제어점 위 conditional flow matching 에 validity·rigidity 구조 손실을 더합니다. 결정적 차별점은 **frozen·재사용성**: 한 번 학습한 trace world model 을 임의 embodiment 의 action expert 가 partial-denoising feature 로 plug-in 해, action-free 비디오 사전학습을 action-labeled VLA(π0/π0.5)에 필적하는 정책으로 전이합니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — backbone 이 SmolVLM2 prefix + flow-matching expert 라 `smolvla` family 와 가장 가깝고, downstream action expert 는 `pi05`(π0.5 self-attn 구조 채택)와 정합. Trace Expert·TraceExtract 데이터 엔진·B-spline target·gated cross-attention 융합은 vendor 에 없는 신규 모듈로 추가 구현 필요(매핑 시 `/implement-design` 가 frozen-prior + action-expert 두 단계로 분해할 것).

---

## 🚧 미해결 / 잠정

- $`\lambda_{\text{done}}`$ / $`\lambda_{\text{rig}}`$ 의 구체 수치가 본문에 명시되지 않음 — ablation 으로 효과만 검증(rigidity 제거 시 top5-DTW 소폭 악화).
- TraceExtract 사전학습 corpus 의 구체적 데이터셋 목록·규모가 추출 본문에 미명시(heterogeneous human/robot manipulation video, 선행 대비 약 8× 큐레이션이라고만 기술).
- VLM 캡셔너·text-only LLM 의 구체 모델명, per-chunk keypoint budget `N` 의 entity quota 배분 세부 규칙은 본문 산문 수준으로만 기술 — Layer 1 스펙으로 굳히기엔 일부 가정 필요.
- action chunk 길이 `T_action`·action_dim 은 embodiment(RoboCasa365 / UR3)별 task-specific(Table 4/5)로, 추출 범위 밖 — 매핑 시 target 인터페이스에서 확정.
