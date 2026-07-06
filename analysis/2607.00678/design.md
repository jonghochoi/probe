# Design — ABot-M0.5: Unified Mobility-and-Manipulation World Action Model

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | ABot-M0.5: Unified Mobility-and-Manipulation World Action Model |
| 링크 | [arXiv:2607.00678](https://arxiv.org/abs/2607.00678) |
| 분석 문서 | [`analysis/2607.00678/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-07-06 |

---

## 🧮 데이터 계약

시간 축은 chunk 의미 단위(`H` = chunk 당 control step 수, `T_ctx` = AR history chunk 수)로 기록합니다.

- **입력 (관측)** — multi-view 이미지 `` $`o_t=\{I_t^{(i)}\}_{i=1}^{N_c}`$ ``: shape `(B, T_ctx, N_c, 3, Himg, Wimg)`, float. 3D VAE 로 압축된 비디오 latent `z`: shape `(B, T_ctx, C_z, h, w)`. 카메라는 **fixed semantic slot**(third-person 2 + wrist 2, `N_c=4` canonical) 로 배치, 결측 view 는 all-zero latent + attention 마스킹.
- **입력 (언어)** — instruction `l`: UMT5 text encoder → 조건 feature `(B, L_text, D)`.
- **입력 (latent action, 학습 라벨)** — `` $`M=\{m_t^{view}\}\in\mathbb{R}^{H\times N_c\times d_m}`$ ``: frozen `E_m(I_t, I_{t+1})` 로 offline 추출, dtype float. `d_m` = latent action 차원 (원문에 수치 명시 없음 — 가정으로 메움).
- **출력 (executable action)** — `a_t = [a_t^move, a_t^manip]`: shape `(B, H, D_move + D_manip)`, float, subspace 별 채널 분리. `D_move`(base 이동)·`D_manip`(arm 조작) 차원은 embodiment 별 (원문에 수치 명시 없음).
- **중간 출력** — 미래 비디오 latent `` $`z_{t+1}`$ `` 과 latent action `` $`m_t`$ `` 는 cascade 내부 예측물이자 다음 단계 조건. inference 시 `` $`\hat{z}_{t+1},\hat{m}_t`$ `` 로 자기 생성.
- **정규화** — action 정규화 통계(mean/std) 출처는 원문에 명시 없음 — 가정으로 메움(데이터셋 전체 통계로 가정).

---

## 🧰 모듈 인터페이스

```python
def latent_action_encoder(I_t, I_tp1) -> m_t:
    """frozen E_m: 연속 프레임 쌍 → frame-level latent action (R^{d_m}). 학습 안 함."""

def world_model_step(z_hist, m_hist, a_hist, l, tau, eps) -> v_z:
    """CFM velocity field for future video latent z_{t+1}. 조건: 역사 상태만(미래 미포함)."""

def latent_action_step(z_leq_tp1, m_hist, a_hist, l, tau, eps) -> v_m:
    """CFM velocity field for latent action m_t. 조건: 예측된 z_{t+1} 포함."""

def action_expert_move(a_move_tau, a_manip_tau, z_leq_tp1, m_leq_t, a_hist, l, tau) -> v_move:
    """mobility sub-tower: 전용 FFN·head. 입력에 상대 branch(a_manip_tau) 포함(cross-subspace)."""

def action_expert_manip(a_manip_tau, a_move_tau, z_leq_tp1, m_leq_t, a_hist, l, tau) -> v_manip:
    """manipulation sub-tower: 전용 FFN·head. 입력에 상대 branch(a_move_tau) 포함."""

def d_mot_forward(X_z, X_m, X_a, causal_mask) -> (h_z, h_m, h_a):
    """dual-level MoT: shared joint self-attention(비대칭 마스크) + modality/subspace-별 FFN·head."""

def dream_forward(batch) -> loss:
    """two-phase: Phase A(self-dream ẑ,m̂ 병렬·few-step) → Phase B(action을 dreamed 조건에 학습)."""
```

- **`latent_action_encoder`** — frozen, gradient 없음. ALAM 사전학습 산출물(decoder·VQ 폐기 후 인코더만).
- **`world_model_step`** — 조건에 **미래 절대 금지**( `` $`z_{<t+1}, m_{<t}, a_{<t}, l`$ `` ), 비대칭 마스크의 상단.
- **`latent_action_step` / `action_expert_*`** — 점진적으로 receptive field 확장(cascade 순서 = inference AR 순서).
- **structured attention** — variable-length FlashAttention 으로 dense 하위 문제화(FlexAttention 대비 ~5× forward-backward).

---

## ⛓️ 불변식·가정

- **(가정 1) cascade 인과 순서 = inference AR 순서.** 학습 시 조건화 정보 흐름이 `` $`z_{t+1}\rightarrow m_t\rightarrow a_t`$ `` 순서를 정확히 mirror 해야 함. 비디오 토큰은 latent action 토큰을 attend 하지 못하고(미래 motion 미지), action 토큰은 latent action 을 attend. 이 비대칭이 깨지면 train-test 조건 정렬이 무효.
- **(가정 2) latent action 은 시각 상태 변화에만 의존.** `` $`m_t = E_m(I_t, I_{t+1})`$ `` 이 embodiment 에 무관한 motion 을 담아, 유사 물리 상호작용이 latent space 근방에 매핑됨(cross-embodiment transfer 전제). ALAM 의 additive(`` $`\mathcal{L}_{\mathrm{add}}`$ ``)·reversal(`` $`\mathcal{L}_{\mathrm{rev}}`$ ``) 대수 일관성이 이 구조를 강제.
- **(가정 3) closed-loop 에서 최근 chunk 만 dream.** 과거 chunk 는 배포 시 실제 GT 관측으로 계속 grounding 되므로, Phase A 는 sequential rollout 없이 **가장 최근 미래 chunk 만** 병렬 생성하면 됨. 이 가정이 깨지면(open-loop 다중 chunk rollout) two-phase 효율 논거 붕괴.
- **(가정 4) 두 action subspace 는 공유 denoising timestep `` $`\tau`$ `` 을 사용.** 별도 noise schedule 없이 병렬 joint denoising 과 정렬 — 이 공유가 깨지면 inference 병렬 denoising 과 불일치.
- **(가정 5) conditioning dropout = 0.** cascade inference 에서 denoised 상류 조건이 항상 존재하므로 `p_drop=0` 이 train-test 정렬 최적(0.2 는 성능 저하).

---

## 📊 하이퍼파라미터·손실

- **비디오 CFM (Eq 5):** `` $`\mathcal{L}_{\mathrm{z}}=\mathbb{E}\big[\|v_\theta^z(z_{t+1}^\tau; z_{<t+1},m_{<t},a_{<t},\tau,l)-(z_{t+1}-\epsilon)\|_2^2\big]`$ ``, `` $`z_{t+1}^\tau=\tau z_{t+1}+(1-\tau)\epsilon`$ ``
- **latent action CFM (Eq 9):** `` $`\mathcal{L}_{\mathrm{m}}=\mathbb{E}\big[\|v_\theta(m_t^\tau; z_{\leq t+1},m_{<t},a_{<t},\tau,l)-(m_t-\epsilon)\|_2^2\big]`$ ``
- **action CFM subspace (Eq 11/12/13):** `` $`\mathcal{L}_{\mathrm{a}}=\lambda_{\mathrm{move}}\mathcal{L}_{\mathrm{a}}^{\mathrm{move}}+\lambda_{\mathrm{manip}}\mathcal{L}_{\mathrm{a}}^{\mathrm{manip}}`$ `` (각 branch 는 상대 branch 의 noisy action 을 입력으로 받음)
- **SFT1 총손실 (Eq 23):** `` $`\mathcal{L}_{\mathrm{SFT1}}=\lambda_z\mathcal{L}_{\mathrm{z}}+\lambda_m\mathcal{L}_{\mathrm{m}}+\lambda_a\mathcal{L}_{\mathrm{a}}`$ `` (조건 = GT 미래)
- **SFT2 Dream Forcing (Eq 27/28):** `` $`\mathcal{L}_{\mathrm{SFT2}}=\lambda_z\mathcal{L}_{\mathrm{z}}+\lambda_m\mathcal{L}_{\mathrm{m}}+\lambda_a(\lambda_a^{\mathrm{move}}\tilde{\mathcal{L}}_{\mathrm{a}}^{\mathrm{move}}+\lambda_a^{\mathrm{manip}}\tilde{\mathcal{L}}_{\mathrm{a}}^{\mathrm{manip}})`$ `` (조건 = self-dreamed `` $`\hat{z},\hat{m}`$ ``)
- **LAM 사전학습 (Eq 19):** `` $`\mathcal{L}_{\mathrm{LAM}}=\lambda_{\mathrm{vq}}\mathcal{L}_{\mathrm{vq}}+\lambda_{\mathrm{rec}}\mathcal{L}_{\mathrm{rec}}+\lambda_{\mathrm{perc}}\mathcal{L}_{\mathrm{perc}}+\lambda_{\mathrm{add}}\mathcal{L}_{\mathrm{add}}+\lambda_{\mathrm{rev}}\mathcal{L}_{\mathrm{rev}}`$ ``
- **offset augmentation (Eq 29):** `` $`s\in\{0,1,\dots,H-1\}`$ `` → 유효 latent 분할 수 `H` 배

| 이름 | 값 | 출처 |
|------|----|----|
| `backbone` | Wan2.2 5B (video diffusion) | §3.1, §4.2 |
| `text_encoder` | UMT5 | §3.1 |
| `latent_encoder` | 3D VAE | §3.1 |
| `E_m` | frozen ALAM encoder | §3.2, §4.3 |
| `p_drop` (latent action) | `0` (최적; 0.2 저하) | §5.4, Table 7 |
| `denoise_timestep` | move·manip 공유 | §3.3 |
| `attn_kernel` | var-len FlashAttention (~5× vs FlexAttention) | §4.5 |
| `warm_start_steps` | 50k (SFT1), +5k (SFT2 DF) | §5.4, Table 8 |
| `` $`\lambda_z, \lambda_m, \lambda_a, \lambda_{\mathrm{move}}, \lambda_{\mathrm{manip}}, \lambda_{\mathrm{vq}}, \lambda_{\mathrm{rec}}, \lambda_{\mathrm{perc}}, \lambda_{\mathrm{add}}, \lambda_{\mathrm{rev}}`$ `` | (원문 미명시) | §3–4 |
| `H`, `d_m`, `C_z`, `N_c`, few-step 수 | (원문 미명시; `N_c=4` canonical slot) | §3–4 |
| optimizer / lr / batch / GPU | (원문 미명시) | — |

---

## 🎯 평가 메트릭

- **지표** — task success rate (주). RoboCasa365 는 atomic-seen / composite-seen / composite-unseen 범주별 분해. 실물은 success rate + process score.
- **임계값 / 비교** — RoboCasa365 pretraining avg 40.4%(직전 SOTA Qwen-RobotManip 35.9%); Target 100% avg 54.2%(Lingbot-VA 45.1%); RoboTwin 2.0 avg 94.10; LIBERO avg 99.4; LIBERO-Plus total 83.4(WAM 내 SOTA).
- **비교 baseline** — VLA: $`\pi_0`$, $`\pi_{0.5}`$, GR00T-N1.5/1.6, Qwen-RobotManip. WAM: Fast-WAM, Lingbot-VA, GigaWorld-Policy, ImageWAM, Cosmos-Policy, Motus.
- **ablation 지표** — latent action strategy(Table 7), MoT 설계(0.48 vs 0.34), Dream Forcing(+3.01%p @동일 예산), pretraining(격차 31.2%p @Target 10%).

---

## ✨ 변경 의도 (intent)

기존 WAM 은 "무엇을 예측하고(prediction space) 어떻게 조건화하느냐"에 집중했습니다. ABot-M0.5 의 차별점은 **세 축의 정렬을 동시에** 도입한 것입니다: (1) 비디오 latent 과 action 사이에 frame-level latent action 이라는 중간 bridging space 를 끼워 granularity 간극을 메우고(temporal alignment), (2) action space 내부까지 base 이동/arm 조작 subspace 로 분리하되 attention 만 공유해 gradient 간섭을 줄이며(action-space alignment), (3) 학습 조건의 *출처* 자체를 GT 미래가 아닌 모델 self-dreamed 미래로 바꿔 배포 조건과 일치시킵니다(train-test alignment, Dream Forcing). 특히 (3)은 대부분의 선행 WAM(teacher/diffusion forcing)이 남긴 exposure bias 를 조건의 출처 수준에서 제거한다는 점에서 새롭습니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 순수 flow-matching action head(`pi0` / `pi05` family)와 CFM 손실은 근접하나, ABot-M0.5 의 핵심(Wan2.2 5B 생성형 world model backbone + 3-stream cascade + Dream Forcing two-phase forward)은 lerobot 의 어느 baseline policy 에도 대응물이 없습니다. action-decoupled MoT 의 "shared attention + per-subspace FFN·head" 부분은 `pi0`-family 의 action expert 를 base 로 부분 매핑 가능성이 있으나, world-model cascade 전체는 신규 모듈이라 대체로 `UNMAPPABLE` 에 가깝습니다 — 실제 판정은 `/implement-design` 이 수행.

---

## 🚧 미해결 / 잠정

- 손실 가중치 `` $`\lambda_*`$ `` 일체, `` $`d_m`$ ``·`` $`H`$ ``·few-step denoising step 수, optimizer/lr/batch/GPU 등 핵심 하이퍼가 원문 미명시 — 가정으로 비워둠.
- action 정규화 통계 출처가 본문에 없어 "데이터셋 전체 평균/표준편차" 로 가정.
- `+Condensed Memory`(최고 수치 46.6%를 만든 memory 확장)는 future work 로 미공개 — Design 대상에서 제외.
- `E_m` 의 ALAM 세부(구조·차원·사전학습 데이터)는 외부 프레임워크에 의존, 본 논문 단독 스펙 불충분.
- inference 시 few-step denoising 스케줄·Phase A 병렬 생성의 정확한 step 구성 미명시.
