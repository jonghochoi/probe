# Design — A Frame is Worth One Token: Efficient Generative World Modeling with Delta Tokens

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | A Frame is Worth One Token: Efficient Generative World Modeling with Delta Tokens |
| 링크 | [arXiv:2604.04913](https://arxiv.org/abs/2604.04913) |
| 분석 문서 | [`analysis/2604.04913/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-15 |

---

## 🧮 데이터 계약

VFM($`\phi`$, DINOv3 ViT-B, patch $`16\times16`$, frozen)이 모든 입력 프레임을 patch 토큰 grid 로 임베딩한 뒤, 이후 모듈은 픽셀이 아닌 *특징공간*에서만 동작합니다.

- **입력 (프레임)** — `video`: shape `(B, T, 3, H', W')`, float, VFM 전처리 정규화. 학습은 square crop(scale 0.6–1.0, aspect 3:4–4:3), 메인 $`H'{=}W'{=}512`$ / ablation 256.
- **VFM 특징** — $`x = \phi(v)`$ : shape `(B, T, H, W, D)`, $`D`$ = ViT-B 임베딩 차원, $`H{=}W{=}H'/16`$. frozen, grad 없음.
- **delta token** — `z`: shape `(B, T, D)` — 프레임당 **단일** 연속 벡터. 시퀀스 앞에 black frame 을 prepend 해 $`z_1`$ 이 첫 실프레임의 절대 특징을 담음.
- **타임스탬프** — $`T_{1:t} = (\tau_1,\dots,\tau_t)`$ : 각 프레임의 실제 timestamp(초). temporal offset $`\Delta\tau \sim \mathcal{U}[1/25, 1/3]`$ 초.
- **노이즈 쿼리** — `q^k`: shape `(B, K, D)`(공간위치 전체에 공유), $`q^k \sim \mathcal{N}(0, 0.02^2 I)`$.
- **출력 (predictor)** — $`\hat{z}_{t+1}`$ : shape `(B, K, D)` — K 개 후보 delta token. 디코딩시 $`\hat{x}_{t+1} = h(x_t, \hat{z}_{t+1})`$ : shape `(B, H, W, D)`.
- **시간 축** — 절대 frame index 가 아니라 `context_len = t` 와 `n_query = K`, `seq_len = 8`(학습) 같은 의미 단위로 기록. rollout 은 예측 delta 를 context 에 append 하는 autoregressive 단계 수(`rollout_steps`, 평가 mid = 3).

---

## 🧰 모듈 인터페이스

```python
def delta_tokenizer_encode(x_prev, x_curr, z_init) -> z:
    """이전·현재 프레임 VFM 특징(x_prev, x_curr ∈ R^{H×W×D})과 learnable
    embedding z_init 을 받아 단일 delta token z ∈ R^D 를 반환. per-frame
    embedding 으로 prev/curr 구분, self-attention ViT-B."""

def delta_tokenizer_decode(x_prev, z) -> x_hat:
    """이전 프레임 특징 x_prev 와 delta token z 로부터 현재 프레임 특징
    x_hat ∈ R^{H×W×D} 복원. H×W zero-init patch 토큰을 query 로 사용,
    self-attention ViT-B, 마지막 LayerNorm 생략(초기 near-identity)."""

def predictor(q_k, Z_1t, T_1t, tau_next) -> z_next:
    """K 개 노이즈 쿼리 q_k 가 과거 delta token 시퀀스 Z_1t 에
    cross/self-attention 하여 다음 delta token ẑ_{t+1} (K 후보) 예측.
    표준 causal mask + 1D RoPE(헤드당 앞 60차원 회전, 뒤 4 비회전)."""

def bom_loss(z_gt_next, z_cand) -> scalar:
    """K 후보 중 GT delta token 에 smooth L1(β=0.1)이 최소인 k* 만 골라
    그 항만 역전파. 후보 선택 pass 는 detach(파라미터 grad 없음),
    best 후보만 grad 와 함께 재실행."""
```

- **DeltaTok(encode/decode)** — world model 학습 *이전*에 MSE 로 별도 학습 후 **frozen**. predictor 와 loss/optimizer 를 공유하지 않음.
- **predictor** — 유일한 학습 대상(+ 별도 학습된 frozen DeltaTok). 입력=delta token 시퀀스+타임스탬프+노이즈 쿼리, 출력=다음 delta token K 후보. BoM 손실과 직접 연결.
- **task head(eval 전용)** — frozen VFM 특징 위에 학습된 linear seg/depth head. 예측 미래 특징(`x̂`)에 적용해 채점에만 사용, 학습 그래프와 분리.

---

## ⛓️ 불변식·가정

- **(가정 1) 연속 프레임 차분의 저차원성** — $`x_t`$ 는 $`x_{t-1}`$ 과 *구조적·저차원적*으로만 다르므로, 그 차이가 단일 $`D`$-차원 토큰에 (재구성 MSE 가 허용하는 수준으로) 들어간다. 이 전제가 깨지면(큰 모션/장면 전환·고주파 국소 변화 과다) 단일 delta token 가정 자체가 무효.
- **(가정 2) frame rate 가 변화량을 조절** — 추론 frame rate(=$`\Delta\tau`$ 표본 범위)가 토큰 하나가 담는 변화량을 결정한다. 거의 정적이면 이전 프레임 대부분 유지, 큰 전환이면 절대 압축에 근접.
- **(가정 3) black-frame 절대 기준** — 시퀀스 첫 delta token $`z_1`$ 은 black 이전-프레임 덕에 첫 실프레임의 *절대* 특징을 인코딩한다. 이 prepend 가 없으면 상대 표현의 기준점이 사라짐.
- **(가정 4) BoM best-supervision 의 다양성 유도** — 서로 다른 노이즈 쿼리가 서로 다른 미래로 사상되며, GT 에 가장 가까운 하나만 지도해도 mode collapse 하지 않는다(단, 분포 보정 보장은 없음 — §⚖️ 한계).
- **(가정 5) VFM frozen** — VFM 은 학습 내내 고정. delta·predictor 는 이 고정 특징공간의 시간 구조에 의존한다.

---

## 📊 하이퍼파라미터·손실

- **토크나이저 손실** — $`L_{\mathrm{tok}} = \| x_t - \hat{x}_t \|^2`$ (MSE, §3.3 Eq. 7).
- **world model 손실** — best-of-many: $`k^\star = \arg\min_k \sum_{h,w} \ell(x_{t+1,h,w}, \hat{x}^k_{t+1,h,w})`$ , $`L_{\text{BoM}} = \sum_{h,w} \ell(x_{t+1}, \hat{x}^{k^\star}_{t+1})`$ (§3.2 Eq. 4). DeltaWorld 에서는 $`\ell`$ 이 *delta token 공간*에서 계산(디코딩 불요).
- **delta 토큰화** — $`z_t = g(x_{t-1}, x_t, z_{\mathrm{init}})`$ (§3.4 Eq. 8), 복원 $`\hat{x}_t = h(x_{t-1}, z_t)`$ (§3.4 Eq. 9).
- **predictor** — $`\hat{z}_{t+1} = f(q^k, Z_{1:t}, T_{1:t}, \tau_{t+1})`$ (§3.4 Eq. 10).

| 이름 | 값 | 출처 |
|------|----|----|
| `loss ℓ` | smooth L1, $`\beta=0.1`$ | §A Predictor training |
| `bom_K` (train) | 256 (메인, $`512^2`$) / 16 (ablation, $`256^2`$) | §4.1 |
| 노이즈 쿼리 분포 | $`\mathcal{N}(0, 0.02^2 I)`$ | §A DeltaWorld predictor |
| `n_eval_samples` | 20 (best & mean) | §4.3 |
| predictor optim | AdamW, lr $`10^{-4}`$, warmup 5K→constant, wd $`4\times10^{-1}`$, no grad clip | §A Predictor training |
| predictor iters | 300K (메인) / 100K (ablation) + 5K fine-tune @ $`10\times`$ lower lr | §A |
| tokenizer optim | AdamW, lr $`10^{-3}`$, warmup 5K→constant, wd $`10^{-4}`$, grad-norm clip $`10^{-2}`$ | §A Tokenizer training |
| tokenizer iters | 50K (해상도별) | §A |
| batch / seq_len | 1,024 / 8 frames | §4.1, §A |
| $`\Delta\tau`$ | $`\mathcal{U}[1/25, 1/3]`$ s | §4.1, §A |
| backbone | DINOv3 ViT-B(patch 16); tokenizer·predictor 도 ViT-B | §4.1, §A |
| RoPE (predictor) | 1D, 헤드당 앞 60차원 회전, 뒤 4 비회전; 표준 causal mask | §A DeltaWorld predictor |
| 초기화 | linear/embed truncated normal $`\sigma{=}0.02`$, bias 0, Layer Scale $`10^{-5}`$, decoder 최종 LN 생략 | §A DeltaTok tokenizer |

---

## 🎯 평가 메트릭

- **지표** — dense forecasting: segmentation `mIoU ↑`(VSPW 124-class / Cityscapes 19-class), depth `RMSE ↓`(KITTI, Garg region). horizon: short ~0.2s(직접 예측) / mid ~0.6s(3-step autoregressive rollout).
- **표본 집계** — `best`(20 표본 중 GT 특징에 last-step feature loss 최소) + `mean`(20 특징 평균 후 head 1회 적용). 둘 다 강해야 유효(노이즈성 다양성 배제).
- **효율** — `GFLOPs`(DeepSpeed FLOPs Profiler, square 입력 doubled), 학습 `Time` / `Mem`(step 0 대비 상대).
- **비교 baseline** — Copy last(하한) · DINO-world†(결정론, 재구현) · Cosmos-4B/12B(대형 pixel 생성형) · Present(상한). 핵심 주장: best 가 모든 메트릭에서 Cosmos 능가, mean 은 결정론 baseline 수준 회복, FLOPs $`\sim2{,}000\times`$ ·params $`35\times`$ 절감.

---

## ✨ 변경 의도 (intent)

기존 생성형 world model 의 세 비효율 — (i) 픽셀 충실도 표현공간, (ii) 미래당 다중 forward pass, (iii) 시공간 중복 — 을 각각 (i) frozen VFM 특징공간, (ii) Best-of-Many 단일-패스 다중가설, (iii) 프레임당 단일 *delta* 토큰으로 동시에 제거합니다. 핵심 신규성은 결정론적 feature-space world model(DINO-world)을 *값싸게 생성형으로* 바꾸되, 예측 표적을 절대 특징맵이 아니라 **연속 프레임 차분**으로 두어 "변화 없음=이전 프레임 유지"라는 free prior 와 $`1{,}024\times`$ 토큰 절감을 함께 얻는 점입니다. diffusion 류의 반복 denoising 없이 단일 패스로 다양한 미래를 생성하는 것이 baseline 대비 결정적 차이입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 정책 family 와 직접 대응이 약함. DeltaWorld 는 action policy 가 아니라 *standalone feature-space world model* 이라, lerobot 의 `pi0`/`act`/`diffusion` policy backbone 보다는 `vla_jepa`(JEPA latent-prediction world model 계열)의 future-prediction/latent 예측 경로와 개념적으로 가장 가깝습니다. delta-token 토크나이저 + BoM 손실은 기존 policy 의 보조(auxiliary) 예측 헤드/loss 로 얹는 형태가 후보이며, 완전한 매핑 가능성은 `/implement-design` 가 판정.

---

## 🚧 미해결 / 잠정

- **action 조건 부재** — 원문은 action-free. 노이즈 쿼리의 "암묵적 action conditioning" 은 저자의 미검증 가설일 뿐이라, action-conditioned 변형의 인터페이스는 (원문에 명시 없음 — 가정으로 메움).
- **분포 보정** — BoM 은 표본 미래의 확률 보정을 보장하지 않음(원문 명시 한계). eval-in-imagination 용 캘리브레이션 메트릭은 원문 미정의.
- **DeltaTok 세부 차원** — $`D`$(DINOv3 ViT-B 임베딩 차원), 인코더/디코더 layer 수 등 일부 구조 상수는 "ViT-B 구성"으로만 기술되어 정확한 hidden/head 수는 (원문에 명시 없음 — ViT-B 표준값 가정).
- **GitHub 정확 URL** — 코드/가중치는 `deltatok.github.io` 공개 명시이나 레포 경로는 본문 미표기.
