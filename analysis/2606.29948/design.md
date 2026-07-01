# Design — Heterogeneous Tactile Transformer

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Heterogeneous Tactile Transformer |
| 링크 | [arXiv:2606.29948](https://arxiv.org/abs/2606.29948) |
| 분석 문서 | [`analysis/2606.29948/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-07-01 |

---

## 🧮 데이터 계약

시간 축은 고정 접촉 윈도우 `` $`\tau=0.2\,\text{s}`$ `` 단위(의미 단위)로 기록합니다. `B` = paired sample batch, `N_i` = 센서 `i` 의 토큰 수.

- **입력 — optical 센서** (GelSight, 9DTact): 프레임 `(B, 3, 224, 224)` (time tubelet 2, tubelet 크기 2), **비접촉 기준 프레임 차감(background subtraction)** 후 ViT 식 비중첩 공간 패치 → tubelet 당 `196` 토큰, `float32`.
- **입력 — array/taxel 센서** (Xela, TAC-02): 고주파 다차원 시계열 `(B, T_frames, C_taxel)` (T_frames = 20 또는 40), 비접촉 기준 차감 후 길이 `4` 비중첩 시간 패치 → Xela `5` 토큰 / TAC-02 `10` 토큰, `float32`.
- **입력 — pairing**: 각 학습 인스턴스는 마주보게 장착된 두 센서의 **동기화 paired stream** (Pair A: Xela↔9DTact, Pair B: TAC-02↔GS Mini). 순서쌍 `` $`(i,j)\in\mathcal{S}`$ ``.
- **출력 (사전학습 산출)** — 재사용 백본: 센서 인코더 `E_i` + 공유 trunk `T`. downstream 은 `z^i = T(E_i(x^i))` 임베딩 `(B, N_i, D)`, `D=192` 를 소비. (decoder `D_i`, predictor `P_ij` 는 사전학습 후 폐기.)
- **정규화** — MAE 타깃은 패치 단위 zero-mean·unit-variance(`norm(·)`). 입력은 센서별 비접촉 기준 프레임 차감.

---

## 🧰 모듈 인터페이스

```python
def encoder_i(x_i_visible) -> tokens:      # E_i: 센서별, ViT(optical)/self-attn transformer(taxel)
    """센서 i 의 가시 토큰을 D=192 임베딩으로 인코딩 (depth: optical 3 / taxel 2)."""

def shared_trunk(tokens) -> z:             # T: 전 센서 공유, depth 9, no CLS, 입력 시퀀스 보존
    """센서별 토큰 임베딩을 공유 latent 공간에서 처리."""

def decoder_i(z) -> x_hat_i_masked:        # D_i: 센서별, depth 3(optical), masked reconstruction 전용
    """공유 latent 로부터 센서 i 의 가려진 토큰을 복원 (MAE loss)."""

def predictor_ij(z_i, z_j_visible) -> z_j_masked_hat:  # P_ij: cross-attention, depth 3, learnable mask token
    """source 임베딩 + 가시 target 임베딩 → 가려진 target 임베딩 예측 (alignment loss)."""
```

- **`E_i`** — 입력: 센서별 가시 토큰 `x^i_v`; 출력: 임베딩; 갱신원: **오직 `L_MAE`** (alignment gradient 는 인코더 출력에서 차단).
- **`T`** — 입력: 임베딩 토큰; 출력: `z`; 갱신원: `L_MAE` + `L_Align`.
- **`D_i`** — 입력: `T(E_i(x^i_v))`; 출력: 복원된 `x^i_m`; 사전학습 후 폐기.
- **`P_ij`** — 입력: `z^i`(full source) + `z^j_v`(visible target); 출력: `z^j_m` 예측; 타깃에 stop-gradient; 갱신원: `L_Align`(trunk 와 함께).

---

## ⛓️ 불변식·가정

- (가정 1) **Paired 동시성** — 순서쌍 `` $`(i,j)`$ `` 은 동일 접촉 이벤트를 같은 `` $`\tau=0.2\,\text{s}`$ `` 윈도우에서 동시에 측정한다(마주보기 장착 UMI 수집). 이 시간·접촉 동기화가 깨지면 cross-modal alignment 의 회귀 타깃이 무의미해진다.
- (가정 2) **표현 붕괴 방지** — alignment 회귀 타깃 `z^j_m` 에 stop-gradient 를 걸어야 두 표현이 서로를 향해 붕괴하지 않는다(`sg[·]` 필수).
- (가정 3) **특징 보존 분리** — 인코더 출력에서 alignment gradient 를 차단해, 인코더는 `L_MAE` 로만 갱신된다. 이를 어기면 정렬이 센서별 특징을 훼손한다(특히 정보량 적은 array 센서가 optical 로 드리프트).
- (가정 4) **공통 차원** — 전 센서 임베딩이 동일 `D=192` 로 사영되어 공유 trunk 가 이종 토큰을 한 시퀀스로 처리할 수 있다.
- (가정 5) **배경 차감 안정성** — 각 센서의 비접촉 기준 프레임이 안정적으로 존재해, 입력이 접촉 유발 변화만 담는다.

---

## 📊 하이퍼파라미터·손실

- 손실 식 (verbatim — 원문 §4.2 식 (1)–(3)):

$$\mathcal{L}_{\text{MAE}}=\mathbb{E}_{i\sim\mathcal{I}}\left[\left\|\mathcal{D}_{i}\bigl(\mathcal{T}(\mathcal{E}_{i}(\mathbf{x}^{i}_{v}))\bigr)-\mathrm{norm}(\mathbf{x}^{i}_{m})\right\|_{2}^{2}\right]$$

$$\mathcal{L}_{\text{Align}}=\mathbb{E}_{(i,j)\sim\mathcal{S}}\bigl\|\mathcal{P}_{ij}(\mathbf{z}^{i},\mathbf{z}^{j}_{v})-\mathrm{sg}[\mathbf{z}^{j}_{m}]\bigr\|_{2}^{2}$$

$$\mathcal{L}_{\text{HTT}}=\mathcal{L}_{\text{MAE}}+\alpha_{t}\cdot\mathcal{L}_{\text{Align}}$$
- 하이퍼:
  | 이름 | 값 | 출처 |
  |------|----|----|
  | `embed_dim D` | `192` | §A.1 |
  | `num_heads` | `3` | §A.1 |
  | `encoder depth` | optical `3` / taxel `2` | §A.1 |
  | `trunk depth` | `9` | §A.1 |
  | `decoder depth` | `3` (optical) | §A.1 |
  | `predictor depth` | `3` | §A.1 |
  | `` $`\tau`$ `` (접촉 윈도우) | `0.2 s` | §4.1 |
  | `MAE mask ratio` | optical `0.75` / taxel `0.60` | §A.1 |
  | `align target mask ratio` | optical `0.90` / taxel `0.80` | §A.1 |
  | `` $`\alpha_{\max}`$ `` | `0.1` | §4.2, §A.1 |
  | `` $`\alpha`$ `` warmup | 첫 `20,000` step 0→선형증가, 이후 `0.1` 고정 | §A.1 |
  | optimizer | AdamW | §A.1 |
  | `lr` | `3e-4` (warmup `3e-6`→`3e-4`, 2,000 step, cosine decay→`3e-6`) | §A.1 |
  | `batch_size` | `256` paired samples/step | §A.1 |
  | `grad_clip` | `1.0` | §A.1 |
  | total steps | `50,000` | §A.1 |
  | patch: optical | `224×224×3`, tubelet 2×크기 2, `196` tok/tubelet | §A.1 |
  | patch: taxel | 시간패치 길이 `4` → Xela `5` / TAC-02 `10` tok | §A.1 |

---

## 🎯 평가 메트릭

- **지표** — object classification `20`-class top-1 accuracy(%) · **비교 baseline** — Scratch / T3 / SITR / MAE(ours).
- **지표** — force estimation 3D force MAE(N, ↓, per-axis shear/normal + overall) · **비교 baseline** — 동일.
- **지표** — slip detection **macro-F1**(%, ↑, 3-class static/incipient/gross; 데이터 heavy imbalance 85.2% slide 이므로 accuracy 아닌 macro-F1) · **비교 baseline** — 동일.
- **지표(조작)** — task success rate. 실제(toy screw / grasp tofu, Sharpa hand, camera-free) 및 시뮬(ManiFeel Peg Insertion / Bulb Installation, 3 seeds × 50 rollouts) · **비교 baseline** — qpos / wrench / HTT(실제), tacRGB / T3 / SITR / HTT(RGB) / HTT(FF)(시뮬).
- **핵심 판정** — MAE(ours) vs HTT(ours) 델타로 cross-modal alignment 순효과 격리; 새 센서(Sharpa) zero-shot 로 백본 재사용성 측정.

---

## ✨ 변경 의도 (intent)

기존 촉각 표현학습(T3, SITR, AnyTouch 등)은 optical 계열 한 곳에 갇혀, array-based force 신호를 삼키지 못하고 force/slip 전이에서 무너집니다. HTT 의 변경 의도는 **이종 센서를 하나의 백본으로 통합**하는 것 — 센서별 인코더로 각 계열의 raw 구조·강점을 보존하되, 공유 trunk 와 **paired-data cross-modal alignment** 로 표현 공간을 하나로 정렬합니다. 표준 MAE 대비 추가된 것은 (1) 마주보기 paired 센서 간 양방향 cross-modal prediction 손실, (2) stop-gradient + 인코더 gradient 차단 + phased `` $`\alpha`$ `` 스케줄이라는 붕괴·특징훼손 방지 3종 안전장치입니다. 결과적으로 optical 은 array 의 force cue 로, array 는 optical 의 공간 cue 로 상호 보강되며(단, 정보량 비대칭으로 array 는 이득이 작거나 음수), 사전학습에서 못 본 센서로도 인코더를 재사용하는 sensor-agnostic 접촉 백본이 됩니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — HTT 는 정책이 아니라 **관측 인코더(촉각 백본) 사전학습** 이라, 어떤 policy family 의 decoder 와도 직결되지 않습니다. 가장 가까운 접점은 policy 의 **observation/입력 인코더 앞단**에 tactile branch 로 삽입하는 것 — `act` 나 `pi0` 계열의 관측 처리부에 sensor-specific encoder + shared trunk 를 얹고, 사전학습은 별도 self-supervised 루프(MAE + alignment)로 수행 후 인코더+trunk 만 policy 에 이식. 표준 policy 학습 루프에는 loss 항이 다르므로 `/implement-design` 에서 `UNMAPPABLE` 판정 가능성 있음(사전학습 스크립트가 vendor 에 없을 경우).

---

## 🚧 미해결 / 잠정

- **입력 텐서 정확 shape** — taxel 센서의 채널 수 `C_taxel`(Xela/TAC-02 감지소자 수) 원문 본문에 수치 미명시(토큰 수 5/10 만 제시) — Appendix D/A.1 의 프레임 수(20/40)와 시간패치 길이(4)에서 역산은 되나 채널 축은 가정으로 메움.
- **cross-modal predictor 방향성 구현** — "bidirectional / all ordered pairs `S`" 라 명시되나, 각 step 에서 어느 순서쌍을 몇 개 샘플하는지(전수 vs 샘플링) 원문에 명시 없음 — 가정으로 메움.
- **TacFF 인코더 확장 절차** — ManiFeel TacFF 는 "pretrained shared chunk 를 백본으로 새 인코더·디코더 초기화 후 MAE 학습" 이라 명시되나 학습 step/lr 등 세부는 원문 미명시.
- **downstream finetune 프로토콜** — 각 task 에서 인코더+trunk 를 task head/policy 와 jointly finetune 한다고만 명시(§5.1); task별 head 구조·finetune lr 은 Appendix B 로 미루어져 Layer 1 스펙엔 미고정.
