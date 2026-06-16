# Design — T-Rex: Tactile-Reactive Dexterous Manipulation

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | T-Rex: Tactile-Reactive Dexterous Manipulation |
| 링크 | [arXiv:2606.17055](https://arxiv.org/abs/2606.17055) |
| 분석 문서 | [`analysis/2606.17055/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-16 |

---

## 🧮 데이터 계약

시간 축은 의미 단위(`chunk_size`, `T_action`, force window)로 기록합니다. shape 의 `Nf` = 손당 fingertip 수(원문: 손당 5, 양손 10), `B` = 배치.

- **입력** — RGB `o_t`: `(B, V, 3, 360, 640)`, float, V=3(head + 2 wrist), ImageNet-류 정규화 가정 (원문에 정규화 통계 명시 없음 — 가정으로 메움)
- **입력** — language `ℓ`: 토큰 시퀀스, max sequence length 2048
- **입력** — tactile force history $`\mathbf{f}_{t-15:t}`$ : `(B, Nf, 16, 6)`, float (per-finger 6축 wrench, 16프레임 윈도)
- **입력** — current force `f_t`: `(B, Nf, 6)`, float (순간 contact 보존용 직접 projection)
- **입력** — deformation map `d_t`: `(B, Nf, 1, H, W)`, float, 단일채널 변위장 (원문에 H×W 명시 없음 — 가정으로 메움)
- **입력** — proprioception: 양손 `2×7` 팔 joint(pos/vel) + `2×22` hand joint 상태, `SE(3)` wrist pose (mid-training 데이터 스키마 기준)
- **출력** — action chunk $`\mathbf{A}_{t:t+16}`$ : `(B, 16, 62)`, float. action dim 62, chunk 16. 의미: 팔은 relative end-effector delta, 손가락은 absolute joint (62차원 내부 분해는 원문 미명시 — 가정으로 메움)
- **중간 산출** — tactile token $`\mathbf{z}^{\tau}_t`$ : $`[\mathrm{Emb}_{\mathrm{vq}}(E_f(\mathbf{f}_{t-15:t}));\,\mathrm{Proj}_f(\mathbf{f}_t);\,\mathrm{Proj}_d(E_d(\mathbf{d}_t))]`$ (Eq.2), 손가락당 1 VQ 토큰 + force proj + deform feature 의 concat

---

## 🧰 모듈 인터페이스

base 좌표(file:line)는 들어오지 않습니다 — 호출 계약만 기록합니다.

```python
def action_expert(x_tau, tau, c_vl) -> Tensor:        # f^act_θ, low-rate slow stream
    """멀티모달 문맥 c_vl 조건으로 τ∈[τ_split,1] 구간 velocity field 회귀. chunk당 1회."""

def tactile_expert(x, tau, c_tac, kv_split) -> Tensor: # f^tac_θ, high-rate fast stream
    """촉각 토큰 c_tac + 캐시 KV_{τ_split} 조건으로 τ∈[0,τ_split] 구간 velocity field 회귀.
       raw vision 미참조. chunk 내 offset {0,4,8,12}에서 재호출."""

def latent_expert(o_t, ℓ) -> (latent_ctx, future_pred):
    """시각·언어 관찰 → 미래 visual representation 예측(보조 목표) + KV^lat 문맥."""

def vq_force_encoder(f_window) -> token:               # E_f + Emb_vq
    """per-finger 6D force 16프레임 → 1D temporal conv(2 strided) → mean-pool(256d)
       → codebook(K=64) 최근접 양자화. finger-shared conv + finger-identity embed."""

def deform_encoder(d_t) -> feature:                    # E_d (frozen)
    """단일채널 deform map → ResNet-18 앞 3 stage → 3×3 conv(128ch) → flatten·linear.
       self-supervised conv-AE 사전학습 후 frozen."""

def cascaded_denoise_infer(c_vl, c_tac_stream) -> A:    # Algorithm 1
    """slow stream: x_1=ε에서 K_slow=6 step → x̂_{τ_split}, KV_{τ_split} 캐시(no_grad).
       fast stream: offset δ마다 KV clone + x̂에서 K_fast=4 step → 실행 action chunk.
       execution lock 으로 두 stream 직렬화(thread-safe)."""
```

- **action_expert** — 전체 $`\tau\in(0,1]`$ 에서 학습되어 단독 동작 생성 역량 유지(사전학습 일관성). conditioning: `c_vl`(head/wrist 카메라 + 언어 + future-pred 토큰)만.
- **tactile_expert** — 경량(FFN intermediate 1536, 0.62B). conditioning: `c_tac` + $`\mathrm{KV}_{\tau_{\mathrm{split}}}`$ 만, raw vision 미참조.
- **VQ/Deform 인코더** — 출력은 $`\mathbf{z}^{\tau}_t`$ 로 concat 되어 tactile_expert 입력 토큰 구성. deform 인코더는 frozen 이라 policy trainable 파라미터 미증가.

---

## ⛓️ 불변식·가정

- **(가정 1) 공유 속도 target** — 두 expert 는 동일한 $`v^{\star}=\boldsymbol{\epsilon}-\mathbf{A}^{\mathrm{demo}}`$ (Eq.3)를 **disjoint 한 $`\tau`$ 부분구간**에서 회귀한다. 이 공유가 깨지면 두 expert 출력이 한 denoising 궤적으로 매끄럽게 이어지지 않는다.
- **(가정 2) 고정 split** — $`\tau_{\mathrm{split}}`$ 는 학습·추론에서 고정 상수(=0.4). slow 구간 $`[\tau_{\mathrm{split}},1]`$ , fast 구간 $`[0,\tau_{\mathrm{split}}]`$ 의 경계가 두 expert 의 역할 분할을 정의한다.
- **(가정 3) detached slow-stream KV** — tactile_expert 에 전달되는 $`\mathrm{KV}_{\tau_{\mathrm{split}}}`$ 는 stop-gradient(`torch.no_grad`) pass 에서 추출된다. gradient 가 fast→slow 로 흐르면 amortization 가정과 역할 분리가 무너진다.
- **(가정 4) tactile expert 의 vision 비참조** — fast tick 은 비전 타워를 재실행하지 않고 캐시 + 촉각만 쓴다. 이 불변식이 고주파 연산 절감(amortization)의 근거다.
- **(가정 5) staleness 분포 일치** — 학습 delay augmentation $`\delta\sim\mathrm{Uniform}\{0,4,8,12\}`$ 가 배포 시 fast-tick offset 분포와 strictly 일치해야 한다. 어긋나면 frozen 시각 캐시-실시간 촉각 정합이 깨진다.
- **(가정 6) force 분포 정합** — VQ-VAE codebook 은 학습 시 본 force 분포에 묶이므로, 입력 force 의 스케일·센서 특성이 학습 분포와 일치해야 토큰이 의미를 유지한다(drift-robust 의 전제).

---

## 📊 하이퍼파라미터·손실

- 손실(Eq.7): $`\mathcal{L}=\mathcal{L}_{\mathrm{act}}+\lambda_{\mathrm{tac}}\mathcal{L}_{\mathrm{tac}}+\lambda_{\mathrm{future}}\mathcal{L}_{\mathrm{future}}`$
  - $`\mathcal{L}_{\mathrm{act}}=\lVert f_{\theta}^{\mathrm{act}}(\mathbf{x}_{\tau_{\mathrm{act}}},\tau_{\mathrm{act}};\mathbf{c}^{\mathrm{vl}})-v^{\star}\rVert^{2}`$ (Eq.6/8)
  - $`\mathcal{L}_{\mathrm{tac}}=\lVert f_{\theta}^{\mathrm{tac}}(\mathbf{x}_{\tau_{\mathrm{tac}}},\tau_{\mathrm{tac}};\mathbf{c}^{\mathrm{tac}},\mathrm{KV}_{\tau_{\mathrm{split}}})-v^{\star}\rVert^{2}`$ (Eq.6/9)
  - $`\mathcal{L}_{\mathrm{future}}`$ = 미래 visual representation 예측 손실 (latent expert; 구체 형태 원문 미명시 — 가정으로 메움)
  - VQ-VAE 보조: magnitude-weighted MSE(고접촉 프레임 가중) + codebook(EMA, dead-code reseed)

| 이름 | 값 | 출처 |
|------|----|----|
| $`\tau_{\mathrm{split}}`$ | `0.4` | §4.2 |
| `N` (total Euler steps) | `10` | §4.2 |
| `K_slow` | `6` | §4.2, Eq.(4) |
| `K_fast` | `4` | §4.2, Eq.(5) |
| `T_a` (action chunk) | `16` | §4.2, Table 4 |
| fast offsets $`\delta`$ | `{0,4,8,12}` | §4.2, App. B |
| $`\lambda_{\mathrm{tac}}`$ | `1.0` | §4.2, Eq.(7) |
| $`\lambda_{\mathrm{future}}`$ | `0.5` | §4.2, Eq.(7) |
| action expert $`\tau`$ 샘플 | $`\mathrm{Beta}(1.5,1.0)`$ on $`(0,1]`$ | §4.2 |
| tactile expert $`\tau`$ 샘플 | $`\tau_{\mathrm{split}}\cdot\tilde{\tau}`$ , $`\tilde{\tau}\sim\mathrm{Beta}(1.5,1.0)`$ | §4.2 |
| force window `T` | `16` frames | App. C |
| force dim | `6` (per finger) | App. C |
| VQ codebook size `K` | `64` | App. C |
| VQ embedding dim | `256` | App. C |
| deform encoder | ResNet-18 앞 3 stage → 128ch, frozen | App. C |
| action dim | `62` | Table 4 |
| inference steps (act / tac) | `6` / `4` | Table 4 |
| backbone (latent/action) | `Qwen3VL-2B` (1.41B each) | Table 4 |
| tactile expert | `0.62B`, FFN intermediate `1536` | Table 4 |
| optimizer | `AdamW`, peak LR `1e-4`, cosine(min-LR), wd `0`, grad clip `1.0` | Table 4 |
| 학습 자원 | `24× H100`, ZeRO-1, per-device batch `16`, bf16 | Table 4 |

---

## 🎯 평가 메트릭

- **지표** — task success rate (%), 멀티스테이지 태스크는 progress-based rubric 으로 partial completion 반영 · **측정** — task당 16 rollout(물체 위치·회전 무작위), trial 평균 후 task 평균 · **비교 baseline** — ViTacFormer, RDP, Tactile-VLA, EgoScale, π0.5, π0.5+tactile
- **임계값/기준** — full model 12-task 평균 65% (최강 baseline EgoScale 35% 대비 +30%p); ablation 은 6-task 평균(w/o Tactile −23%, w/o Async −5% 등)
- **데이터 효율** — post-training 데모 10→200 곡선, mid-training 유무 비교(Fig.5)

---

## ✨ 변경 의도 (intent)

T-Rex 의 핵심은 **denoising 시간축 분할로 control-rate separation 을 구현** 한 점입니다. 기존 dual-system 은 빠른 motor 와 인지 reasoning 을 완전히 분리해 두 모델을 따로 두고, variable-rate diffusion policy 는 parallel-gripper 의 task-specific imitation 에 갇혀 있었습니다. T-Rex 는 하나의 flow-matching 궤적을 $`\tau_{\mathrm{split}}`$ 에서 잘라 무거운 action expert 가 상단(거친 계획)을, 경량 tactile expert 가 하단(미세 마무리)을 이어받게 함으로써, 단일 통합 foundation model 안에서 저주파 visuomotor 계획과 고주파 촉각 반응을 공존시킵니다. action expert 를 전체 $`(0,1]`$ 에서 학습해 **기존 VLA 단독 역량을 비파괴적으로 보존** 하면서 촉각 반응을 더한 것이 prior art 대비 결정적 차이이며, per-finger VQ-VAE 시간 토큰화 + frozen deform 인코더는 drift-robust·파라미터 효율적인 촉각 표현을 공급합니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 후보 base: `pi0` / `pi05` (flow-matching action expert 골격이 가장 근접 — Eq.1 conditional flow matching, Beta τ 샘플, action chunk denoising 구조 공유). T-Rex 의 cascaded denoising 은 단일 flow-matching expert 를 두 구간( $`K_{\mathrm{slow}}`$ / $`K_{\mathrm{fast}}`$ )으로 자르고 두 번째 구간을 별도 경량 expert + 촉각 토큰으로 conditioning 하는 변형으로 매핑 가능. MoT/expert 분할 측면은 `smolvla` family 와도 비교 대상. 단, backbone(Qwen3VL vs PaliGemma)·촉각 modality·VQ-VAE 토큰화는 lerobot 에 없어 신규 모듈로 추가해야 함.

---

## 🚧 미해결 / 잠정

- action dim **62** 의 팔/손 차원 분해(양손 EE delta + 손가락 joint)가 본문에 명시되지 않아 매핑 시 가정 필요.
- `L_future`(latent expert 미래 visual representation 예측)의 정확한 손실 형태·예측 공간(latent vs feature)이 본문에 구체화되지 않음 — 가정으로 메움.
- deformation map 해상도(H×W)와 RGB 정규화 통계가 본문 미명시.
- VQ-VAE 의 temporal conv 채널/커널, strided block 세부 stride, finger-identity embedding 차원이 부분만 공개(256d / K=64 / T=16 외).
- 코드 저장소 URL 미공개(프로젝트 페이지만) — 데이터 로더·전처리 스크립트는 데이터셋과 함께 공개 예정으로만 명시.
