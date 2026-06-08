# Design — Multi-Resolution Tactile Imitation Learning for Contact-Rich Robotic Manipulation

> PROBE design 산출물 (Layer 1, vendor-agnostic). 단일 한글 문서이며,
> 영문 1차 파일은 없습니다. `/analyze-paper` 가 `analysis/<id>/analysis.md` 와
> 함께 자동 생성합니다 — 알고리즘 명세를 base 좌표계 없이 추출합니다.
> base 매핑은 `/implement-design` 단계에서 이루어집니다. 형식·이모지·용어 규칙은
> `docs/STYLE.md` §6 / §4 를 정확히 따릅니다. 재실행 시 이 파일을
> 덮어씁니다.

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Multi-Resolution Tactile Imitation Learning for Contact-Rich Robotic Manipulation |
| 링크 | [arXiv:2606.06281](https://arxiv.org/abs/2606.06281) |
| 분석 문서 | [`analysis/2606.06281/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-08 |

---

## 🧮 데이터 계약

시간 축은 의미 단위(`H`, `n_act`, `n_obs`)로 기록합니다. 배치 차원 `B`.

- **입력 (vision)** — `O_vision`: shape `(B, 2, 128, 128)`, RGB 2프레임 채널 스택, dtype float, 정규화 `[0, 1]`, 25 Hz 손목 카메라.
- **입력 (gelsight)** — `O_gelsight`: shape `(B, 2, 120, 160)`, dtype float, 정규화 `[0, 1]`, 25 Hz vision 기반 촉각.
- **입력 (evetac)** — `O_evetac`: shape `(B, 16, 120, 160)`, dtype float, 정규화 `[-1/2, 1/2]`(무이벤트 회색 프레임 → 0), 200 Hz 센서의 timestep 당 16 event 프레임 스택. co-training 시 배치 절반에만 존재, 배포 시 제거.
- **관측 윈도우** — `n_obs = 4`, 센서 프레임은 0.06 s 윈도우 균일 샘플링(15 Hz 제어).
- **조건 토큰 (encoder 출력)** — `C`: shape `(B, N_cond, D)`, `D = 256`. 토큰 수(`N_cond`/`Tok/obs`)는 센서 설정 의존 — V+G+E 644, V+G 452, V+E 452, V 260 (§A.2 Table 4).
- **출력 (action chunk)** — `A`: shape `(B, H, d_a)` = `(B, 16, 4)`, 로컬 프레임 delta `[Δx, Δy, Δz, Δψ]`, 정규화 minmax. 제어 루프는 처음 `n_act`(1–3) 스텝만 실행 후 재계획.
- **플로우 매칭 텐서** — 노이즈 `x_0 ~ N(0, I)` shape `(B, H, d_a)`, 종점 `x_1 = Ā`(정규화 action chunk), 시간 `t ∈ [0,1]`.

---

## 🧰 모듈 인터페이스

```python
def sensor_stem(obs, modality: str) -> Tensor:  # (B, C_in, Hs, Ws) -> (B, n_tok, D)
    """modality별 전용 CNN stem. vision/gelsight=4층 strided 2D conv,
    evetac=4층 3D conv(시간 커널 3-3-3-2, stride 2, 마지막 2x4x5 conv 로 시간 붕괴).
    vision -> 16x16 격자, gelsight/evetac -> 12x16 격자, 모두 D=256 토큰."""

def add_pos_modality_embedding(z, grid_idx, modality_id) -> Tensor:
    """z'_i = z_i + p_{g(i)} + e_{s(i)}. p=학습된 격자 위치 임베딩,
    e=학습된 modality 임베딩(vision/gelsight/evetac). 둘 다 정책과 공동 학습."""

def fusion_transformer(tokens) -> Tensor:  # (B, N_cond, D) -> (B, N_cond, D)
    """multi-head self-attention + MLP + pre-norm + residual.
    센서 간 full self/cross-attention 으로 조건 토큰 C 생성."""

def dit_velocity_head(x_t, t, C) -> Tensor:  # (B,H,d_a),(B,),(B,N_cond,D) -> (B,H,d_a)
    """L=10 DiT 블록. 각 슬롯 -> D 토큰 + chunk 위치 임베딩.
    블록당 (i) 액션 토큰 self-attn, (ii) C 로의 cross-attn(query=action,
    kv=C, 공유 D 라 중간 투영 없음), (iii) token-wise MLP, 모두 residual.
    AdaLN-Zero 로 t 조건화. 출력 = 예측 속도장 v_hat."""

def flow_matching_loss(v_hat, u_t, mask) -> Tensor:
    """masked MSE: mean over valid timesteps of ||v_hat - u_t||^2."""

def euler_sample(dit_head, C, K: int) -> Tensor:  # 추론
    """x_0 ~ N(0,I) 에서 시작, x_{t+Δt} = x_t + Δt·v_hat(x_t,t,C),
    Δt=1/K, t∈[0,1) 반복. K=10."""
```

- co-training 스케줄: 학습 루프가 배치별로 `use_evetac ~ Bernoulli(0.5)` 를 뽑아 절반은 evetac stem 포함, 절반은 미포함. 배포 시 evetac stem 완전 제거(co-trained V+G 정책).

---

## ⛓️ 불변식·가정

- (가정 1) — 모든 센서 토큰과 액션 토큰은 공유 임베딩 폭 `D = 256` 를 가진다. cross-attention 이 중간 투영 없이 동작하려면 query(action)/kv(condition) 차원이 동일해야 한다.
- (가정 2) — 정책은 로봇 상태(proprioception)·절대 위치를 입력받지 않는다. 따라서 출력은 반드시 로컬 프레임 상대 delta 여야 하며, 절대 위치 표현으로 바꾸면 가정이 깨진다.
- (가정 3) — 액션은 4-DoF `[Δx, Δy, Δz, Δψ]` 로 병진 + z축 yaw 만 제어하고 pitch·roll 은 reset 시 latch 한 값으로 고정한다.
- (가정 4) — 플로우 경로는 직선(straight-line): `x_t = t·x_1 + (1−t)·x_0`, 목표 속도 `u_t = dx_t/dt`(상수). 따라서 학습 노이즈 스케일 `σ = 0`.
- (가정 5) — co-training 의 유효성은 "Evetac 미포함 절반 배치가 모델로 하여금 누락 특징을 잠재 보상하도록 규제"한다는 데 의존한다. 즉 두 modality 분포가 표현 공간에서 정렬 가능해야 한다.
- (가정 6) — Evetac 정규화는 기본 회색 프레임(이벤트 없음)이 0 에 대응하도록 `[-1/2, 1/2]` 를 쓴다(다른 modality 의 `[0,1]` 와 비대칭).

---

## 📊 하이퍼파라미터·손실

- 손실 식 (masked MSE flow matching):

  $$\mathcal{L}_{\mathrm{FM}}=\big\|\hat{\mathbf{v}}_{\theta}(\mathbf{x}_{t},t,\mathbf{C})-\mathbf{u}_{t}\big\|^{2}, \quad \mathbf{x}_{t}=t\cdot\mathbf{x}_{1}+(1{-}t)\cdot\mathbf{x}_{0},\ \ \mathbf{u}_{t}=\mathrm{d}\mathbf{x}_{t}/\mathrm{d}t$$

- AdaLN-Zero 변조: $`\mathrm{AdaLN}(\mathbf{Y};\mathbf{\beta},\mathbf{\gamma})=\mathrm{LN}(\mathbf{Y})\odot(1+\mathbf{\gamma})+\mathbf{\beta}`$, 게이팅 잔차 $`\mathbf{Y}\leftarrow\mathbf{Y}+g\,f(\mathrm{AdaLN}(\mathbf{Y};\mathbf{\beta},\mathbf{\gamma}))`$.

  | 이름 | 값 | 출처 |
  |------|----|----|
  | `batch_size` | `64` | §A.4, Table 6 |
  | `H` (action horizon) | `16` | §A.4, Table 6 |
  | `n_act` (executed per replan) | `1–3` | §A.4, Table 6 |
  | `n_obs` (observation window) | `4` | §A.4, Table 6 |
  | `D` (embedding width) | `256` | §A.4, Table 6 |
  | `L` (DiT depth) | `10` | §A.4, Table 6 |
  | attention heads | `8` | §A.4, Table 6 |
  | MLP ratio | `4` | §A.4, Table 6 |
  | dropout | `0.0` | §A.4, Table 6 |
  | `d_t` (time embedding dim) | `128` | §A.4, Table 6 |
  | time embedding | sinusoidal | §A.4, Table 6 |
  | flow-matching noise `σ` | `0.0` | §A.4, Table 6 |
  | `K` (FM inference steps) | `10` | §A.4, Table 6 |
  | policy lr | `1e-4` | §A.4, Table 6 |
  | encoder lr | `1e-5` | §A.4, Table 6 |
  | weight decay | `1e-6` | §A.4, Table 6 |
  | Adam betas | `(0.95, 0.999)` | §A.4, Table 6 |
  | lr schedule | cosine | §A.4, Table 6 |
  | gradient clipping | `1.0` | §A.4, Table 6 |
  | action normalization | minmax | §A.4, Table 6 |
  | co-train batch ratio | `0.5` (Evetac 포함 절반) | §3.3 |
  | policy head params (공유) | `13,701,508` | §A.2 |

---

## 🎯 평가 메트릭

- **지표** — task success rate (%), 정책당 20회 시행 후 성공 비율 · **비교 baseline** — Sparsh-X(멀티모달 촉각 트랜스포머, attention-bottleneck 융합), ViT / ViT-CNN(vision-only).
- **핵심 임계값** — MiTaS V+G+E 평균 80% vs Sparsh-X V+G+E 54% vs ViT 31% / ViT-CNN 26% (5 과제 평균, §4.2 Table 1).
- **부가 지표** — co-training Δ(V+G 대비 성공률 증감, §4.2 Table 2), 추론 속도(ms / Hz, RTX 4080·10 적분 스텝, §A.2 Table 4), trainable params(perception / total).
- **과제** — Gear Assembly, Board Wiping, Lamp Installation, Key in Lock, Lightbulb Connection (5 contact-rich tasks).

---

## ✨ 변경 의도 (intent)

기존 촉각 조작 프레임워크는 대부분 단일 촉각 modality 에 의존합니다. 이 설계의 핵심은 **시간 해상도가 다른 두 이종 촉각 센서**(25 Hz frame 기반 GelSight + 200 Hz event 기반 Evetac)를 modality별 CNN stem 으로 토큰화하고, modality 임베딩으로 출처를 표시한 뒤 full self/cross-attention 트랜스포머로 융합하여 플로우 매칭 정책을 조건화하는 것입니다. attention-bottleneck 융합(Sparsh-X) 대비 full attention 융합이, 그리고 foundation 사전학습 대비 task end-to-end 학습이 접촉 집약적 과제에서 우위(80% vs 54%)를 보입니다. 두 번째 의도는 **비대칭 co-training** — 고주파 Evetac 을 학습 시에만 절반 배치에 주입해 표현을 규제하고 배포 시 제거함으로써, 추론 비용을 늘리지 않고 visual-tactile 정책을 강화하는 것입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — DiT + 플로우 매칭 액션 헤드·action chunking 은 `pi0` / `pi05` 의 flow-matching action expert family 와 가깝습니다. 다만 본 논문은 VLM backbone·언어 조건 없이 멀티 센서 인코더가 직접 조건 토큰을 만드는 구조라, `diffusion`(diffusion policy, 비전+상태 조건화) 계열의 인코더-조건화 패턴과도 절충될 수 있습니다. 핵심 신규 모듈(이종 촉각 CNN stem + modality 임베딩 + co-training 마스킹)은 어느 base 든 신규 입력 인코더로 추가해야 하며, 기존 정책 헤드(flow matching)는 재사용 가능성이 높습니다.

---

## 🚧 미해결 / 잠정

- masked MSE 의 마스크 `m_h`(에피소드 패딩 마스크, §A.4 Table 5 기호)가 구체적으로 어떤 timestep 을 무효화하는지 본문에 식 수준으로 명시되지 않아, "유효 timestep 평균 MSE"로 가정.
- co-training 의 `use_evetac` 추첨이 시퀀스 단위인지 배치 단위인지 — 본문은 "each training batch ... sampling half of the sequences with Evetac"(§3.3)이라 **시퀀스 단위 절반**으로 해석했으나, 구현 세부(샘플러 레벨)는 미명시.
- `N_cond`(조건 토큰 수)는 센서 설정별 Table 4 값으로 역산했을 뿐, vision 16x16=256 + gelsight 12x16=192 + evetac 12x16=192 의 합산 규칙이 본문 식으로 못박혀 있지는 않음(644 ≈ 256+192+192+추가 토큰 가능성).
- 정규화 통계(minmax action / `[0,1]` 이미지)의 산출 출처(데이터셋 전체 vs 에피소드별)가 본문에 없어 "데이터셋 전체 통계"로 가정.
- 코드/데이터셋 배포 경로가 본문 미명시 — 프로젝트 페이지(http://mitas-touch.github.io) 외 저장소 링크 없음.
