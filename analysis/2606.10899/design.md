# Design — MV-Actor: Aligning Multi-View Semantics and Spatial Awareness for Bimanual Manipulation

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | MV-Actor: Aligning Multi-View Semantics and Spatial Awareness for Bimanual Manipulation |
| 링크 | [arXiv:2606.10899](https://arxiv.org/abs/2606.10899) |
| 분석 문서 | [`analysis/2606.10899/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-15 |

---

## 🧮 데이터 계약

MV-Actor 는 다중 시점 RGB-D 관측을 metric point-cloud 공유 공간에 anchor 한 의미/공간 토큰으로 변환해 양팔 액션을 산출하는 지각-정책 프레임워크입니다. 시간 축은 history `H_obs` / action horizon `H` 의 의미 단위로 기록합니다.

- **입력 (관측)** — $`O_t = (\{I_t^{(v)}, D_t^{(v)}\}_{v\in\mathcal{V}}, \ell, q_t)`$. RGB `I^v`: shape `(B, V, 3, 256, 256)`; depth `D^v`: `(B, V, 1, 256, 256)`; 언어 $`\ell`$: frozen CLIP text 토큰; proprioception `q_t`: bimanual 이력 dim 48. `V=3` (front, wrist_left, wrist_right), `H_obs=3`.
- **의미 토큰** — frozen CLIP RN50+FPN(res3) → 시점별 `32×32` grid, embed dim `d=120`. shape `(B, V, 32×32, d)`.
- **공간 토큰** — frozen Pi3X pointmap/decoder feature → 시점별 `18×18`, `d_spa=1024`; `W_S` 로 `d` 투영·LN·nearest-neighbor 로 `32×32` grid 정렬 후 사용.
- **metric anchor** — 복원 depth `d_out` 로 각 토큰을 robot frame 으로 back-projection: $`\hat{p}_i^{(v)} = T_{\mathrm{base}\leftarrow\mathrm{cam}}^{(v)} d_{\mathrm{out}}^{(v)}(u_i) K^{(v)-1} \tilde{u}_i`$ (Eq.14). 3D RoPE 입력.
- **출력 (액션)** — $`a_\tau = \{(p,r,g)_{\mathrm{left}}, (p,r,g)_{\mathrm{right}}\}`$ (Eq.3). position `p`: workspace-normalized 3D; rotation `r`: quaternion `(x,y,z,w)` → 연속 6D; gripper `g`: binary. denoising/flow 타깃 $`\epsilon`$ 으로 감독.
- **정규화** — position 은 workspace-normalized 좌표(통계 출처 원문 미명시). depth repair 입력의 정규화 규약은 원문 미명시.

---

## 🧰 모듈 인터페이스

```python
def repair_metric_depth(d_noisy: Tensor, rgb: Tensor, d_ffd: Tensor) -> Tensor:
    """3-branch U-Net: raw sensor depth + RGB + Pi3X feed-forward depth prior 융합.
       d_out = max(0, H_depth(F_0)). metric scale 보존·hole 복원·경계 보존.
       PerAct2 sim 사전학습 후 joint training 중 frozen."""

def multiview_semantic_interaction(s: Tensor, anchors: Tensor,
                                   extrinsics, intrinsics_grid,
                                   eps_reproj: float, eps_depth: float) -> Tensor:
    """각 의미 토큰 anchor 를 타 시점 32x32 grid 로 reprojection(Eq.4),
       grid 정렬(Eq.5)+depth 일관(Eq.6) 둘 다 만족하는 후보 중 최소 오차 토큰을
       대응집합 C 로. masked local attention 잔차 Δs^sem 반환(Eq.7-8).
       block 2회, heads=8, residual scale lambda_s=0.1."""

def semantic_spatial_interaction(s: Tensor, spatial_tokens: Tensor) -> Tensor:
    """정렬된 Pi3X 공간 토큰 g~ 에 의미 토큰이 per-head sigmoid-gated attend.
       beta = sigmoid(qk/sqrt(d_h)) (Eq.9); Δs^spa = lambda_spa·W_O·Concat_h(beta·W_V g~)
       (Eq.10). residual scale lambda_spa=0.1."""

def head_aware_routing_gate(s, e_l, q_t, ds_sem, ds_spa) -> dict[str, Tensor]:
    """context z_route=[Pool(s),Pool(e_l),psi(q_t),Pool(ds_sem),Pool(ds_spa)] (Eq.11),
       2-layer MLP → 4 sigmoid gate gamma (Eq.12);
       s^h = s + gamma_sem^h·ds_sem + gamma_spa^h·ds_spa, h∈{pos,rot} (Eq.13).
       gripper 헤드는 rot 라우팅 표현 공유. 반환 {pos: s^pos, rot: s^rot}."""

def action_decoder(scene_pos, scene_rot, e_l, q_t, noisy_action) -> tuple:
    """3D denoising backbone(rectified flow, 5 step). shared self-attn decoder →
       position/rotation/gripper 헤드. ε(flow 타깃) 예측."""
```

- **repair_metric_depth** — 정책과 분리된 frozen 전처리. 출력 depth 가 모든 back-projection(Eq.14)의 입력.
- **multiview_semantic_interaction / semantic_spatial_interaction** — 공유 base token `s` 위에서 *병렬* 작동, 상보 잔차 $`\Delta s^{\mathrm{sem}}`$ / $`\Delta s^{\mathrm{spa}}`$ 산출. 서로 직접 호출하지 않음.
- **head_aware_routing_gate** — 두 잔차를 헤드별로 차등 혼합. 단순 합산 금지(간섭 유발).
- **action_decoder** — `L_pos`(mean L1)·`L_rot`(mean L1)·`L_grip`(BCE) loss 와 결합.

---

## ⛓️ 불변식·가정

- (가정 1) — **calibrated extrinsics/intrinsics 정확성.** reprojection 매칭(Eq.4–6)과 metric back-projection(Eq.2,14)이 카메라 intrinsic $`K^{(v)}`$ · extrinsic $`T_{\mathrm{base}\leftarrow\mathrm{cam}}^{(v)}`$ 의 정확도에 의존. calibration 오차가 `eps_reproj`(1.5 grid cell)·`eps_depth`(0.05 m) 임계를 넘으면 대응이 잘못 맺히거나 비어 알고리즘 무효.
- (가정 2) — **충분한 multi-view overlap.** 의미 공유는 시점 간 물리적으로 대응되는 영역이 존재해야 성립. overlap 이 낮으면 대응집합 `C_i^(v)` 가 비어 잔차 0(저자가 long-horizon task 약점으로 명시).
- (가정 3) — **depth 일관성으로 perspective-overlap 분리 가능.** Eq.(6)이 "다른 3D 표면이 비슷한 화소로 투영" 되는 경우를 depth 차로 걸러낼 수 있다는 가정. 표면 간 depth 차가 `eps_depth` 보다 작으면 분리 실패.
- (가정 4) — **feed-forward depth 는 scale drift 가 있으나 기하 guidance 로 유효.** $`d_{\pi^3}`$ 를 최종 출력이 아닌 guidance 로만 사용(원문 §3.4).
- (가정 5) — **헤드별 증거 선호가 다름.** position 헤드는 spatial 잔차를, rotation 헤드는 semantic 잔차를 더 선호한다는 ablation 관찰(Table 3)이 Head-Aware Routing Gate 의 전제.
- (가정 6) — **frozen 인코더 prior 유효성.** CLIP(의미)·Pi3X(공간)가 frozen 이므로, 이들 사전학습 표현이 대상 도메인에 전이된다는 가정.

---

## 📊 하이퍼파라미터·손실

- 토큰 back-projection: $`p_i^{(v)} = T_{\mathrm{base}\leftarrow\mathrm{cam}}^{(v)} D^{(v)}(u_i) K^{(v)-1} \tilde{u}_i`$ (Eq.2)
- reprojection: $`\hat{c}_u = \Pi(K_u^{\mathrm{grid}} (R_u p_i^{(v)} + t_u))`$, $`\hat{z}_u = [R_u p_i^{(v)}+t_u]_z`$ (Eq.4)
- 후보 유효성: $`\|\hat{c}_u - c_j^{(u)}\|_2 \le \epsilon_{\mathrm{reproj}}`$ (Eq.5), $`|\hat{z}_u - z_j^{(u)}| \le \epsilon_{\mathrm{depth}}`$ (Eq.6)
- 의미 잔차: $`\Delta s_i^{\mathrm{sem}} = \lambda_s W_O \sum \alpha_{i,uj} W_V s_j^{(u)}`$ (Eq.7-8)
- 공간 잔차: $`\Delta s_i^{\mathrm{spa}} = \lambda_{\mathrm{spa}} W_O^{\mathrm{spa}} \mathrm{Concat}_h(\beta_{i,h} W_{V,h} \tilde{g}_i^{(v)})`$ (Eq.9-10)
- 라우팅: $`s^h = s + \gamma_{\mathrm{sem}}^h \Delta s^{\mathrm{sem}} + \gamma_{\mathrm{spa}}^h \Delta s^{\mathrm{spa}}`$, $`h\in\{\mathrm{pos},\mathrm{rot}\}`$ (Eq.13)
- depth repair: $`d_{\mathrm{out}}^{(v)} = \max(0, H_{\mathrm{depth}}(F_0))`$ (Eq.17), loss = pixel-wise L1 + missing weight $`1+4m`$
- 액션 손실: $`\mathcal{L} = \lambda_{\mathrm{pos}}\mathcal{L}_{\mathrm{pos}} + \lambda_{\mathrm{rot}}\mathcal{L}_{\mathrm{rot}} + \mathcal{L}_{\mathrm{grip}}`$ (Eq.21), `L_pos`/`L_rot`=mean L1, `L_grip`=BCEWithLogits

| 이름 | 값 | 출처 |
|------|----|----|
| `V` (시점 수) | `3` (front, wrist_left, wrist_right) | Table 5 |
| 입력 해상도 | `256×256` | Table 5 |
| `H_obs` (history) | `3` | Table 5 |
| token embed dim `d` | `120` | Table 5 |
| 의미 token grid | `32×32` (CLIP RN50+FPN res3, frozen) | Table 5 |
| 공간 token grid / `d_spa` | `18×18` / `1024` (Pi3X, frozen) | Table 5 |
| `eps_reproj` | `1.5` grid cell | Table 5 |
| `eps_depth` | `0.05` m | Table 5 |
| `lambda_s` (의미 잔차 스케일) | `0.1`, block 2회, heads `8` | §3.2, Table 5 |
| `lambda_spa` (공간 잔차 스케일) | `0.1`, heads `8` | §3.2, Table 5 |
| router MLP | $`(5d+6)\to d\to 4`$, SiLU, bias init 0·weight std `1e-3` | Table 5 |
| flow model | rectified flow, `5` denoising step | Table 5 |
| rotation 표현 | quaternion `(x,y,z,w)` → 연속 6D | §3.5, Table 5 |
| `lambda_pos` / `lambda_rot` | `30` / `10` | §3.5 |
| optimizer | AdamW, betas `(0.9,0.95)`, wd `1e-10` | Table 5 |
| learning rate | main `1e-4`, backbone `1e-6`, constant | Table 5 |
| batch / val batch | `256` / `64` | Table 5 |
| max step | `200k`(ablation) / `400k`(full) | Table 5 |
| 하드웨어/시간 | 8×A100, ~20h(full) | Table 5 |
| depth repair: U-Net | 3-branch, 5 scale, base width 24 (24,48,48,96,96) | Table 6 |
| depth repair: optimizer/lr/epoch/batch | AdamW / `8e-4` / `100` / `8`, wd `1e-4`, seed 42 | Table 6 |

---

## 🎯 평가 메트릭

- **online 지표** — task 성공률(%) · **임계값** — 절대 임계 없음, baseline 대비 비교 · **비교 baseline** — 3DFA(point-cloud), PerAct2(voxel), `pi0`/`pi0-keypose`(RGB-only VLA), ACT, RVT-LF, PerAct-LF, DP3, KStarDiffuser, PPI, AnyBimanual
- **offline action 지표 (ablation)** — `pos_l2`↓, `pos_acc@0.01`↑(%), `rot_l1`↓, `rot_acc`↑(%), `gripper`↑(%); 50k/100k/200k step 별 보고
- **depth repair 지표** — pixel-wise MAE↓ over 3 regions: `all`(전체) / `miss`(block-missing mask 내부) / `obs`(mask 외 유효 화소)
- **핵심 수치** — PerAct2 평균 87.8%(vs 3DFA 85.1%); 실로봇 ARK-Lift 평균 staged score 63.1%(vs 3DFA 58.1·pi0 52.5·PerAct2 16.6); full 모델 ablation 에서 pos_acc@0.01 86.3·pos_l2 0.009(200k, 전 지표 최고); depth repair RGB+Pi3X MAE(all) 0.012
- **실로봇 채점** — staged score: 2-stage task 각 0.50, 3-stage task 누적 milestone 0.33/0.66/1.00; task 당 100 demo·10 test trial

---

## ✨ 변경 의도 (intent)

기존 다중 시점 정책은 각 시점을 독립 인코딩 후 정책 레벨에서 융합하거나(시점 간 대응 무시), sensor depth 로 voxel/point-cloud 공유 공간에 lifting(취약한 depth 의존)합니다. MV-Actor 는 세 가지를 바꿉니다. (1) **calibrated reprojection-consistent correspondence** — 3D-KNN 의 "가깝지만 다른 표면" 오염 대신, grid 정렬 + depth 일관성을 모두 만족하는 토큰끼리만 의미를 공유. (2) **feed-forward 재구성(Pi3X) 공간 토큰** — 취약한 센서 depth 대신 RGB-only 재구성 prior 로 공간 인지를 주입(D9 의 geometry-aware encoder 노선). (3) **Head-Aware Routing Gate** — 의미·공간 잔차를 합산하지 않고 position/rotation 헤드별 sigmoid gate 로 적응 혼합해 잔차 간 간섭을 제거. 추가로 **Guided Metric Depth Repair** 가 소비자급 depth 의 hole·noise 를 RGB+FFD prior 로 복원해 metric anchor(3D RoPE) 신뢰도를 확보합니다. 결과적으로 "다중 시점 = 같은 장면의 관련 관측" 이라는 관점을, 의미 공유 + 신뢰할 수 있는 공간 인지의 통합 표현으로 구현합니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — MV-Actor 는 π 계열 flow-matching VLA 가 아니라 *3D denoising/rectified-flow keypose 정책* 이고, frozen CLIP/Pi3X 인코더 + 다중 시점 기하 융합이 핵심이라 `pi0`/`pi05`/`smolvla` family 와 직접 정합하지 않습니다. action head 가 rectified flow 라는 점만 `pi0`/`pi05` 계열과 닮았습니다. lerobot 에 동급의 다중 시점 geometry-grounding 정책 base 가 없으면 `/implement-design` 가 `🚧 매핑 불가` 를 낼 가능성이 높습니다. 부분 매핑 후보: 관측 인코더(의미/공간 토큰 + 두 상호작용)는 backbone-agnostic 모듈이라, 임의 multi-view 정책의 observation 경로에 끼우는 형태로만 이식 가능.

---

## 🚧 미해결 / 잠정

- **action 표현 모호성** — Eq.(3)은 horizon `H` 의 action chunk $`A_t = \{a_\tau\}_{\tau=t}^{t+H-1}`$ 를 정의하나 Table 5 는 "Single-step keypose-only action prediction" 이라 명시 — 실제 운용이 keypose 단발인지 chunk 예측인지 본문이 상충. `H` 값·subsampling(=5) 과의 관계가 Layer 1 으로 굳지 않음.
- **denoising/flow 정식화 미상세** — 3D denoising backbone 의 noise schedule, $`\epsilon`$ 타깃의 정확한 정의(rectified flow velocity vs noise), 추론 시 5-step 적분 절차가 본문에 상세하지 않음.
- **정규화 통계 출처** — position 의 workspace-normalization 통계 및 depth repair 입력 정규화 규약이 원문에 명시 없음 — `(원문에 명시 없음 — 가정으로 메움)`.
- **fusion block $`\Phi_l`$ 내부 구조** — depth repair 의 multi-scale fusion(1×1 reduction + 병렬 3×3/5×5/dilation-2 depthwise)은 Table 6 에 있으나, 세 분기 feature 병합의 정확한 연산(concat/add/attention)이 불명확.
- **`Align`·`Pool`·`psi` 구체형** — nearest-neighbor 정렬, mean pooling 은 명시되나 proprio 투영 `psi`(48→d) 외 세부 구현은 일부 추정.
- **부분 매핑 경계** — 관측 인코더만 떼어 다른 backbone 에 이식할 때, base scene token `s` 의 출처(어떤 정책의 visual token 을 `s` 로 볼지)가 foundry 의존이라 Layer 1 에서 고정 불가.
