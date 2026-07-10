# Design — RynnWorld-Teleop: An Action-Conditioned World Model for Digital Teleoperation

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | RynnWorld-Teleop: An Action-Conditioned World Model for Digital Teleoperation |
| 링크 | [arXiv:2607.06558](https://arxiv.org/abs/2607.06558) |
| 분석 문서 | [`analysis/2607.06558/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-07-10 |

---

## 🧮 데이터 계약

- **입력 — reference 이미지** `I_ref`: RGB 단일 프레임, 평가 해상도 `480×832`, 사전학습 3D VAE 인코더 $`\mathcal{E}`$ 로 latent `z_ref` 화. dtype/정규화 (원문에 명시 없음 — 가정으로 메움)
- **입력 — 액션 (손 포즈)**: 21-관절 손 포즈 시퀀스 $`\mathcal{P}=\{p_{1},\dots,p_{T}\}`$ → depth-aware 스켈레톤 렌더링(관절·본의 색/지름을 카메라-공간 깊이로 변조)으로 RGB 비디오화, 16 FPS, chunk 길이 `T = 81` 프레임(VITRA 사전학습 구간만 25) → 동일 VAE 인코더로 제어 latent $`c\in\mathbb{R}^{C\times T\times H\times W}`$ (타깃 video latent 와 공간·시간 정렬)
- **입력 — 노이즈 latent** $`z_{t}\in\mathbb{R}^{C\times T\times H\times W}`$ : flow-matching 경로 $`z_{t}=(1-t)z_{0}+t\epsilon`$ 상의 점, $`t\in[0,1]`$
- **출력 — 속도장** $`v_{\Theta}(z_{t},t,z_{ref},c)`$ : `z_t` 와 동일 shape. ODE 적분(증류 student 는 4-step) 후 VAE 디코딩으로 비디오 $`V=\{v_{1},\dots,v_{T}\}`$ 복원
- **사이드채널 — 로봇 액션 라벨** $`a_{t}\in\mathbb{R}^{54}`$ : 양팔 7-DoF + 양손 20-DoF 절대 관절 위치의 연결 벡터. 모델 입출력이 아니라 데이터 엔진 출력 궤적의 동기화 라벨(포즈 스트림에서 DLS IK 로 retarget, 프레임 1:1 정렬)
- **정규화 — 제어 latent 분포 정렬**: $`\widetilde{c}=\frac{c-\mu_{c}}{\sigma_{c}}\cdot\sigma_{z}+\mu_{z}`$ — 두 신호의 running $`(\mu,\sigma)`$ 추정으로 patch 화 이전에 video latent 분포로 정렬

---

## 🧰 모듈 인터페이스

```python
def render_depth_aware_skeleton(hand_poses, camera_intrinsics, camera_pose,
                                T, H, W) -> SkeletonVideo:
    """21-관절 손 포즈를 깊이-변조 색/지름의 2D 스켈레톤 RGB 비디오로 렌더링"""

def encode_control(skeleton_video, vae_encoder) -> ControlLatent:
    """스켈레톤 비디오를 사전학습 VAE 로 제어 latent c (C,T,H,W) 로 인코딩"""

def align_and_fuse(z_t, c, stats, alpha) -> Tokens:
    """c 를 running (mu, sigma) 로 video latent 분포에 정렬 후,
    zero-init 제어 PatchEmbed 분기 출력을 alpha 게이트로 additive 융합 (식 3)"""

def denoise_velocity(z_t, t, z_ref, c) -> Velocity:
    """DiT denoiser — CFM 속도장 예측 (teacher: bidirectional attention)"""

def causal_student_step(frame_action, kv_cache, sink_token) -> Frame:
    """causal temporal mask + 고정 KV cache + I_ref sink 토큰으로
    프레임 단위 자기회귀 스트리밍 생성 (4-step 샘플링)"""

def retarget_dls_ik(tracker_poses, scale_s, shoulder_prior_w) -> RobotAction54:
    """Vive 트래커 6-DoF 포즈 → 좌표 변환 체인(식 5) → 감쇠 최소제곱 IK(식 6–7)
    + null-space 어깨 prior(식 8) → 54-차원 절대 관절 액션"""

def generate_chunked(demo_frames, pose_stream, world_model,
                     chunk_len=81) -> Trajectory:
    """chunk 단위 생성 + chunk 경계마다 실측 egocentric 프레임으로 I_ref 재앵커,
    (합성 비디오, 동기화 액션) 궤적 반환"""
```

- 학습 시 `denoise_velocity` 는 $`\mathcal{L}_{\text{CFM}}`$ 로 최적화되고, 증류 시 causal student 는 (1) causal flow-matching warm-up ( $`\mathcal{L}_{\text{MSE}}`$ ), (2) DMD(critic + frozen teacher score 지도, chunk 간 KV cache 를 통한 gradient 역전파) 순으로 최적화됩니다.
- `align_and_fuse` 의 제어 분기는 zero-init, 게이트 $`\alpha`$ 는 0.1 로 초기화 — 학습 시작 시점의 출력이 사전학습 모델과 일치하도록 하는 호출 계약입니다.

---

## ⛓️ 불변식·가정

- (정렬 불변식) — patch 화 직전의 $`\widetilde{c}`$ 는 video latent 와 동일한 1·2차 모멘트를 갖습니다. 이것이 깨지면 additive 조건이 사전학습 스트림을 교란합니다 (concat ablation 의 FVD 585→1191 악화가 그 증거)
- (prior-보존 불변식) — 제어 분기 zero-init + 소값 게이트로 인해 학습 스텝 0 에서 모델 출력은 사전학습 base 모델과 동일합니다
- (표현 통일 가정) — human 사전학습·robot 적응·추론의 모든 데이터는 동일한 (2D Skeleton, RGB) 계약으로 변환됩니다. 스켈레톤 렌더러(색/지름의 깊이 변조 규칙)가 stage 간에 달라지면 이전이 무효화됩니다
- (인과성 불변식) — student 의 시점 $`t`$ attention 은 $`\{1,\dots,t\}`$ + persistent sink 토큰( `I_ref` 임베딩)으로 제한됩니다. teacher 는 bidirectional
- (동기화 불변식) — 액션 $`a_{1:T}`$ 와 생성 프레임 $`v_{1:T}`$ 는 동일 포즈 스트림에서 유도되어 프레임 1:1 정렬을 유지합니다 (IL 소비 가능성의 근거)
- (재앵커 가정) — 장호라이즌 생성은 81-프레임 chunk 경계마다 실측 프레임으로 재접지된다는 조건 하에서만 물리 일관성이 주장됩니다. 완전-합성 다중 chunk 롤아웃의 드리프트 내성은 가정 밖입니다
- (액션 충실 가정) — 생성 비디오가 조건 스켈레톤을 프레임 단위로 추종합니다 (action-grounded 요건). 추종이 깨지면 (관측, 액션) 쌍의 라벨 정합성이 무효화됩니다

---

## 📊 하이퍼파라미터·손실

**손실 식** (모두 원문 표기):

$$\mathcal{L}_{\text{CFM}}=\mathbb{E}_{t,z_{0},\epsilon}\left[\left\|v_{\Theta}(z_{t},t,z_{ref},c)-(\epsilon-z_{0})\right\|_{2}^{2}\right]$$

$$\mathcal{L}_{\text{MSE}}=\mathbb{E}_{t,\boldsymbol{\epsilon}}\left[\left\|\mathbf{v}_{\theta}(\mathbf{x}_{t},t)-(\boldsymbol{\epsilon}-\mathbf{x}_{0})\right\|^{2}\right]$$

DMD 단계는 별도 식 없이 "learned critic + frozen teacher 의 score-based gradient guidance" 로 기술됩니다 (원문 식 미제시).

| 이름 | 값 | 출처 |
|------|----|----|
| base 모델 | `Wan2.2-TI2V-5B` | §5.1 |
| TI2V warm-up steps / lr | 2,000 / $`2\times 10^{-5}`$ | §5.1 |
| 학습 GPU | NVIDIA H100 × 64 | §5.1 |
| LoRA rank | 64 | §5.1 |
| Stage 1 lr (LoRA·SFT 공통) | $`2\times 10^{-5}`$ | §5.1 |
| Stage 2 lr (LoRA·SFT 공통) | $`1\times 10^{-5}`$ | §5.1 |
| SFT EMA decay / warmup | $`0.999`$ / 200 steps | §5.1 |
| causal warm-up lr | $`1\times 10^{-5}`$ | §5.1 |
| DMD generator / critic lr | $`2\times 10^{-6}`$ / $`5\times 10^{-7}`$ | §5.1 |
| 게이트 $`\alpha`$ 초기값 | 0.1 | §3.3, 식 (3) |
| student 샘플링 스텝 | 4 | §3.5, §5.2 |
| chunk 길이 / 조건 FPS | 81 프레임 / 16 FPS | §3.4, §4.1 |
| 생성 해상도 / 처리량 | `480×832` / 40.0 fps (H100 1장) | §5.2 |
| retarget 병진 배율 $`s`$ | 1.5 (예시값) | §8, 식 (5) |
| IK 감쇠 $`\lambda`$ | $`\lambda=\lambda_{\min}+\frac{0.01}{1+\sigma_{\max}}`$ ( $`\lambda_{\min}`$ 값 원문 미명시) | §8, 식 (7) |
| null-space 어깨 가중치 $`w`$ | 0.5 | §8, 식 (8) |
| Stage 1 데이터 | VITRA 30.7M 프레임(1.23M slice) + EgoDex 74.0M 프레임(0.91M slice) | §3.4, Table 1 |
| Stage 2 데이터 | 실로봇 1,800 에피소드 (0.43M 프레임, 5.3K slice) | §3.4, Table 1–2 |

---

## 🎯 평가 메트릭

- **지표 (생성 품질)** — `PSNR` ↑ · `SSIM` ↑ · `LPIPS` ↓ · `FVD` ↓ (표준 I3D 백본, 81-프레임 롤아웃) · `FPS` (H100 1장) — EgoDex-Test(공식 테스트셋 81-프레임 × 50 시퀀스) / Robotic-Test(학습 미사용 20 시퀀스, 4개 과제) · **비교 baseline** — CogVideoX-1.5-I2V-5B, Wan-2.1/2.2 I2V·TI2V 계열(+vanilla SFT), InterDyn, CosHand, Mask2IV
- **지표 (정책)** — `Success Rate` (%) · **채점** — 과제당 35회 연속 실측 시행, 120초 내 목표 상태 도달 시 성공, 초기 물체 6-DoF 포즈 랜덤화 · **비교 baseline** — DP / $`\pi_{0}`$ / $`\pi_{0.5}`$ 를 `300 Real` vs `300 Real + 300 생성` vs `0 Real + 300 생성` 데이터 소스로 대조
- **참조 수치 (재현 목표선)** — LoRA: PSNR 26.08 / FVD 585, SFT: PSNR 26.78 / FVD 550, Causal: PSNR 22.25 / FVD 1226 / 40.0 FPS (EgoDex-Test); 분포 정합 보조 지표로 실측 1,000 vs 생성 1,000 프레임의 I3D 특징 t-SNE 겹침

---

## ✨ 변경 의도 (intent)

기존 human-to-robot 비디오 변환(passive·observation-only)과 human-centric action-conditioned world model 의 두 갈래가 각각 "액션 없음"과 "embodiment 갭"에 막혀 있던 지점에서, 본 설계는 (1) 조건 표현을 depth-aware 2D 스켈레톤으로 통일해 사람/로봇 도메인을 같은 계약에 올리고, (2) 분포-정렬 zero-init additive 주입으로 사전학습 비디오 prior 를 보존한 채 액션 조건화를 추가하며, (3) causal warm-up → DMD 의 순차 증류로 bidirectional teacher 를 40+ FPS 스트리밍 student 로 압축합니다. 그 결과 조작자가 루프 안에 머무는 robot-centric·action-grounded·real-time world model 이 되고, retargeting·chunked re-anchoring 시스템 레이어와 결합해 IL 이 그대로 소비하는 (RGB 관측, 54-DoF 액션) 궤적의 데이터 엔진으로 기능하는 것이 prior art 대비 핵심 차별입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 정책 base 로 직접 매핑할 video-diffusion world model family 는 없습니다 (`pi0`/`pi05`/`act`/`diffusion`/`vla_jepa` 모두 정책·표현 학습 계열). 현실적 접점은 데이터-엔진 경로 — 생성된 (비디오, 54-DoF 액션) 궤적을 LeRobotDataset 포맷으로 적재해 기존 정책 학습에 공급하는 오프라인 증강 파이프라인 — 이며, 모델 자체의 매핑은 `/implement-design` 에서 `매핑 불가` 판정 가능성이 높습니다.

---

## 🚧 미해결 / 잠정

- depth-aware 렌더링의 구체 스펙(깊이→색 매핑 함수, 지름 스케일 함수, 색 팔레트) 원문 미명시 — 재현 시 공개 코드 확인 필요
- running $`(\mu,\sigma)`$ 추정 절차(모멘텀 계수, 갱신 주기, 학습/추론 시 동결 여부) 원문 미명시
- DMD critic 의 구조·학습 세부와 teacher 의 샘플링 스텝 수 원문 미명시
- KV cache 크기·sliding window 길이(§5.2 에 "sliding-window KV cache" 언급만) 원문 미명시
- 3D VAE 의 압축률과 latent `C/T/H/W` 구체 수치 원문 미명시
- Table 3 정책 학습용 생성 데이터가 teacher / causal student 어느 쪽 산출물인지 원문 미명시
- Stage 2 자체 수집 1,800 에피소드의 공개 여부 원문 미명시
- $`\lambda_{\min}`$ (IK 감쇠 하한) 값 원문 미명시
