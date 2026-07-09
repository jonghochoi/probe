# Design — RynnWorld-4D: 4D Embodied World Models for Robotic Manipulation

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | RynnWorld-4D: 4D Embodied World Models for Robotic Manipulation |
| 링크 | [arXiv:2607.06559](https://arxiv.org/abs/2607.06559) |
| 분석 문서 | [`analysis/2607.06559/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-07-09 |

---

## 🧮 데이터 계약

**세계 모델 (RynnWorld-4D)**

- **입력(조건)** — 초기 RGB-D 관찰 1장 + 언어 지시. RGB 프레임은 center-crop `480×640`, $`[-1,1]`$ 정규화. 각 모달 첫 프레임은 clean 조건화 잠재(실제 RGB / 실제 depth / zero-flow).
- **입력(잠재)** — 모달 $`m\in\{\text{rgb,depth,flow}\}`$ 별 $`\mathbf{z}_{t}^{m}`$: shape `(B, T, C, H, W)`, flow-matching timestep $`t\in[0,1]`$. 픽셀 `81×480×640` → causal VAE `4×` 시간 압축 → `T=21` latent frame ($`T_{\text{latent}}=(T_{\text{pixel}}-1)/4+1`$).
- **출력** — 세 모달 미래 시퀀스(RGB 비디오 / depth 맵 / optical flow), 프레임 `[1:]` 만 감독. depth 는 `[0.0, 5.0]` m clip 후 $`I=\lfloor d/d_{\max}\times 255\rfloor`$ 8-bit 양자화; flow 는 $`[\Delta u, \Delta v]`$.

**정책 (RynnWorld-4D-Policy)**

- **입력** — 현재 RGB 관찰 1장 (`480×640`, $`[-1,1]`$) + 언어 embedding $`l_{\text{emb}}`$ + proprioception $`p_{0}`$. 동결 세계 모델에서 뽑은 4D 특징 $`F_{p}`$: shape `(B, T, 3C, H, W)` (RGB/depth/flow 분기 은닉 concat, 각 3072-dim).
- **출력** — 행동 청크: 길이 `K=10`, 각 행동 `54-dim` (양손 dexterous; TIANJI M6 7-DOF 팔 + WUJI HAND 20-DOF 좌표계). 정규화 통계 출처는 원문 미명시.

---

## 🧰 모듈 인터페이스

```python
def rynnworld4d(rgb_d_init, text, z_t, t) -> dict[str, Tensor]:
    """tri-branch 확산 세계 모델: 초기 RGB-D + 언어 조건으로
       RGB/depth/flow 미래 시퀀스의 flow-matching 속도장을 예측."""

def joint_cross_modal_attention(z_l, layer_idx) -> dict[str, Tensor]:
    """3 layer 마다(0,3,...,27; 총 10개) 삽입. per-modality LayerNorm+모달임베딩,
       shared K/V(12d^2), frame-wise mask + 3D RoPE, zero-init OutProj + tanh(g) 게이트."""

def unproject_scene_flow(depth_t, depth_t1, flow, K) -> Tensor:
    """depth→3D 점(Eq.1) + optical flow 대응(Eq.2)으로 metric 3D scene flow
       f_3D = P_{t+1} − P_t 유도. ‖∇D‖>τ edge 마스킹."""

def extract_4d_features(rynnworld4d_frozen, rgb, text, t=500, block=15) -> Tensor:
    """동결 세계 모델의 단일 순전파(N=1)에서 block 15 은닉 상태를
       3 분기 concat → F_p (3×3072-dim). 반복 denoising 없음."""

def flow_former(F_p, learnable_Q) -> Tensor:
    """프레임별 spatial cross-attn → temporal self-attn → FFN 으로
       4D 특징을 고정 크기 토큰 Q'' 로 압축(Eq.8)."""

def action_head(Q_pp, l_emb, p_0, a_t, t) -> Tensor:
    """flow-matching 정책 속도장 v_φ. 추론 시 N=4-step Euler ODE →
       K=10 행동 청크."""
```

- **세계 모델 ↔ 정책** — 세계 모델은 학습·배포 내내 **동결**. 정책은 Flow Former + action head 만 학습. 세계 모델 특징 추출과 행동 생성은 loss 를 공유하지 않음(decoupled 2단계).
- **손실 관계** — 세계 모델·정책 모두 동일 flow-matching 목표(velocity 회귀). optimizer: AdamW(세계 모델 $`\beta=(0.9,0.95)`$, 정책 $`\beta=(0.9,0.9)`$).

---

## ⛓️ 불변식·가정

- **(공유 노이즈)** — 세 모달이 **동일한** Gaussian 샘플 $`\epsilon^{\text{rgb}}=\epsilon^{\text{depth}}=\epsilon^{\text{flow}}`$ 를 공유해야 denoising 궤적이 시간 정렬되고 cross-modal 일관성이 성립. 모달별 독립 노이즈면 물리적 정합성이 깨짐.
- **(프레임-국소 cross-attention)** — JA 의 cross-modal 어텐션은 **같은 시간 프레임** 토큰으로 제한(frame-wise mask). 프레임 간 누설 시 3D scene flow 대응 가정이 무너짐.
- **(기하 정렬)** — 3D RoPE 로 모달 간 동일 $`(u,v)`$ 좌표 특징이 정렬되어야 함. 제거 시 global semantic averaging 으로 퇴화($`\delta_{1}`$ 0.610→0.450).
- **(모달별 용량)** — RGB 텍스처 / depth 다양체 / motion field 의 잠재 공간은 이질적이므로 per-modality FFN 필수. shared FFN 은 catastrophic interference.
- **(RGB anchor)** — RGB 분기는 dropout 하지 않음(appearance anchor). depth/flow 만 branch dropout 대상.
- **(scene flow 물리성)** — depth·flow pseudo-label 이 metric 으로 정확해야 $`\mathbf{f}_{3D}`$ 가 실제 3D 운동에 대응. 단안 depth 오차가 back-projection 으로 전파되는 것이 상한.
- **(예측 결정성 — 잠정)** — 세계 모델이 행동-무조건이므로 "언어+RGB-D 가 미래를 충분히 결정한다"를 암묵 가정. 다중-모드 과제에서 깨질 수 있음(원문에서 명시적으로 다루지 않음).

---

## 📊 하이퍼파라미터·손실

- 세계 모델 손실 (Eq. 7), 경로 $`\mathbf{z}_{t}^{m}=(1-t)\mathbf{z}_{0}^{m}+t\,\epsilon^{m}`$:

$$\mathcal{L}_{\text{total}}=\sum_{m\in\mathcal{M}}\lambda_{m}\,\mathbb{E}\!\left[\bigl\|\mathbf{v}_{\theta}^{m}(\mathbf{z}_{t}^{m},t,\mathbf{c})_{[1:]}-(\epsilon^{m}-\mathbf{z}_{0}^{m})_{[1:]}\bigr\|_{2}^{2}\right]$$

- JA 출력 (Eq. 6): $`\hat{\mathbf{z}}_{l}^{m}=\mathbf{z}_{l}^{m}+\tanh(g_{l}^{m})\cdot\mathrm{OutProj}_{l}^{m}(\mathbf{A}_{l}^{m})`$, $`g_{l}^{m}`$ init `1`, OutProj zero-init.
- 정책 손실: flow-matching(Eq. 7 형식, 속도장 $`v_{\phi}`$ 가 행동 $`\mathbf{a}`$ 에 작동, $`\mathbf{Q}^{\prime\prime}\cdot l_{\text{emb}}\cdot p_{0}`$ 조건).

| 이름 | 값 | 출처 |
|------|----|----|
| `backbone` | Wan-2.2-TI2V-5B (30-layer DiT, $`d=3072`$, FFN `14336`) | §4.1.1 |
| `JA modules` | 10개 (layers 0,3,6,…,27) | §3.3 |
| $`\lambda_{\text{rgb}}`$, $`\lambda_{\text{depth}}`$ | `1`, `1` | §3.3, Eq. 7 |
| $`\lambda_{\text{flow}}`$ | `0.5` (Stage 1) → `1.0` (Stage 2,3) | §3.3, Table 2 |
| $`p_{\text{drop}}`$ (branch dropout) | `0.2` (Stage 2), `0.1` (Stage 3) | Table 2 |
| LR | `2e-5` / `5e-5` / `1e-5` (Stage 1/2/3) | Table 2 |
| warm-up steps | `500` / `200` / `500` | Table 2 |
| optimizer (WM) | AdamW $`\beta=(0.9,0.95)`$, wd `1e-4`, EMA `0.9999` | §4.1.1 |
| 해상도 / 프레임 | `81×480×640` → `T=21` latent | §4.1.1 |
| 정책 특징 추출 | diffusion `t=500`, block `15`, 3×`3072`-dim concat | §4.1.2 |
| 정책 행동 | chunk `K=10`, `54-dim`, ODE `N=4` step Euler | §3.4, §4.1.2 |
| 정책 optimizer | AdamW `1e-4`, $`\beta=(0.9,0.9)`$, wd `0.05`, 100 epoch, bs 1/GPU | §4.1.2 |
| 정책 LR schedule | 2% warmup / 8% hold / 90% cosine→`1e-6×peak` | §4.1.2 |
| 제어 주파수 | planning $`\approx 0.9`$ Hz, effective $`\approx 9`$ Hz (chunk 50Hz cached) | §3.5 |

---

## 🎯 평가 메트릭

- **세계 모델** — 시각(IQ/MS/SC/Subj., PSNR/SSIM/LPIPS) · 기하(AbsRel↓, $`\delta_{1}`$↑) · 운동(AEPE↓). held-out 50 비디오(RoboMIND/RDT-1B/Galaxea).
  - **임계값(달성)** — $`\delta_{1}=0.610`$(4DNeX 0.327·TesserAct 0.279 대비), AbsRel `0.310`, AEPE `0.170`, SSIM `0.754`, PSNR `17.85`, LPIPS `0.269`.
- **정책** — Success Rate(%), 120초 내 완료, 35회 연속 시행. 6 과제(Dual Picking / Block Pushing / Hand-over / Bimanual Lifting / Lid Placement / Bowl Stacking).
  - **비교 baseline** — DP(Diffusion Policy), $`\pi_{0}`$, $`\pi_{0.5}`$. 임계값(대표): Lid Placement 65.71%(DP+8.57%p), Hand-over 28.57%($`\pi_{0.5}`$ 0.00% 대비).

---

## ✨ 변경 의도 (intent)

기존 2D 미래-예측 정책(SuSIE/UniPi)은 픽셀 공간에서만 작동하며 매 스텝 denoising 을 요구해 기하 정확도·반응성에서 한계가 있고, 명시적 3D/4D 세계 모델은 다중 뷰·장면 특화·비확장성 문제를 가집니다. RynnWorld-4D 는 RGB 에 depth·optical flow 를 **한 확산 루프에서 동기 생성**하는 RGB-DF 표현으로 두 축을 잇습니다 — 2D 정렬 포맷을 유지해 대규모 비디오 확산 prior 를 상속하면서도, depth+flow 를 back-projection 해 명시적 metric 3D scene flow 를 얻어 로봇 행동 공간에 가까운 표현을 만듭니다. 나아가 세계 모델을 **동결한 예측적 4D 비전 인코더**로 재활용하고 내부 잠재를 단일 순전파로 소비함으로써, 반복 denoising 병목 없이 고주파 폐루프 제어를 실현합니다. TesserAct(RGB-D-Normal, 정적 기하)와의 차별점은 광학 흐름을 통한 **명시적 동적 단서**이며, 행동-조건 세계 모델(LOME/DexWM)과의 차별점은 **행동-무조건 예측 + 역동역학** 경로입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 정책 헤드(RynnWorld-4D-Policy)는 flow-matching action head + proprioception 조건 + action chunking 구조이므로 `pi0` / `pi05` family 와 가장 가까움. 다만 핵심 신규성인 tri-branch 확산 세계 모델(Wan-2.2 기반)과 "동결 WM 잠재 추출" 경로는 lerobot 의 기존 policy 계열에 직접 대응하는 base 가 없어, 세계 모델 부분은 별도 encoder 모듈로 이식해야 할 가능성이 큼(`/implement-design` 가 매핑 가능성 판정).

---

## 🚧 미해결 / 잠정

- 행동 정규화 통계(`54-dim` action)의 출처가 본문에 없어 "데이터셋 전체 평균/표준편차" 로 가정 필요.
- 세계 모델 학습 GPU 수·총 스텝 수 미명시(Table 2 는 grad accumulation 2-4 × $`N_{\text{GPU}}`$ 만 제시).
- Rynn4DDataset 1.0 의 배포 형태(pseudo-label 포함 여부)와 라이선스가 본문상 불명확.
- 정책이 세계 모델 특징을 뽑는 `t=500`, `block 15` 선택의 민감도(왜 이 값인지)는 ablation 부재.
- 세계 모델이 행동-무조건이라 "예측 미래 ↔ 의도 행동" 정렬을 무엇이 보장하는지 Layer 1 수준에서 미확정(역동역학 헤드가 암묵 학습).
