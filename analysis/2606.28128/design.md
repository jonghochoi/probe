# Design — PhysisForcing: Physics Reinforced World Simulator for Robotic Manipulation

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | PhysisForcing: Physics Reinforced World Simulator for Robotic Manipulation |
| 링크 | [arXiv:2606.28128](https://arxiv.org/abs/2606.28128) |
| 분석 문서 | [`analysis/2606.28128/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-07-01 |

---

## 🧮 데이터 계약

시간 축은 프레임 수 $`T`$ (Wan 계열 ≤81, Cosmos3-Nano ≤189), 공간은 $`H\times W`$ (Wan 480p / Cosmos 720p) 의 의미 단위로 기록합니다.

- **입력 (참조 영상)** — `video`: shape `(B, T, C, H, W)`, `float`, `[0,1]` 정규화(semantic teacher 입력은 `64×256×256` 리샘플 + ImageNet 정규화).
- **입력 (물리 타깃, 학습-only 보조 산출)**
  - `traj_gt`: 참조 궤적 $`\mathcal{P}_{\mathrm{gt}}=\{\mathbf{p}_{i,\mathrm{gt}}^{t}\}`$, shape `(B, N_track, T, 2)`, CoTracker3 offline (첫 프레임 `25×25`=625 query).
  - `depth0`: 첫 프레임 depth $`D_{0}`$, shape `(B, H, W)`, `[0,1]` 정규화, Depth-Anything-V2 ViT-L.
  - `M_phy`: 물리 마스크 $`\mathbf{M}^{\mathrm{phy}}\in\{0,1\}^{T\times H\times W}`$, shape `(B, T, H, W)`.
  - `F_u`: teacher 토큰 $`\mathbf{F}^{u}`$, shape `(B, 32, 16, 16, C_u)`, V-JEPA 2 ViT-L/16 (hidden `1024`, tubelet 2, patch 16), 동결.
- **중간 (DiT 특징)** — `H_l`: 단일 중간 블록 hidden feature $`\mathbf{H}^{l}`$ (Wan A14B 기준 block 20, width 5120). pixel 분기는 $`\phi`$ 로 정제 후 `(B, T, C, H, W)` reshape; semantic 분기는 $`\psi`$ + resize 로 `(B, 32, 16, 16, C)` 정렬.
- **출력** — 손실 스칼라 $`\mathcal{L}`$ (학습). 추론 출력은 백본 원형과 동일한 생성 영상 `(B, T, C, H, W)` — PhysisForcing 은 추론 그래프를 바꾸지 않음.

---

## 🧰 모듈 인터페이스

```python
def extract_physics_region(video, tracker, depth_model, eps) -> Mask:
    """참조 영상에서 밀집 궤적·전경 depth 가중으로 시공간 물리 마스크 M_phy 생성 (§3.1)."""

def pixel_trajectory_loss(H_l, phi, traj_gt, M_phy) -> Tensor:
    """DiT 중간 특징을 MLP phi 로 정제→query/key 유사도 기대값으로 점 궤적 예측,
       참조 궤적과 masked MSE (§3.2, Eq.8)."""

def semantic_relational_loss(H_l, psi, F_u, M_phy, K) -> Tensor:
    """DiT 특징을 MLP psi 로 teacher 공간에 사영→마스크 토큰 K개의 쌍별 코사인
       관계 행렬을 teacher 관계 행렬에 L1 정렬 (§3.3, Eq.12)."""

def total_objective(L_fm, L_pix, L_sem, lam_pix, lam_sem) -> Tensor:
    """L = L_FM + lam_pix*L_pix + lam_sem*L_sem (§3.4, Eq.13)."""
```

- **`extract_physics_region`** — 입력: 참조 영상 + 동결 tracker/depth. 출력: `M_phy`. 두 손실이 공유하는 마스크 산출. 학습 스텝마다 GT 클립에 on-the-fly 실행.
- **`pixel_trajectory_loss`** — 외부 호출: CoTracker3(참조 궤적). loss 반환. query = 첫 프레임 특징, key = 이후 프레임 특징.
- **`semantic_relational_loss`** — 외부 호출: 동결 V-JEPA 2. 절대 특징이 아니라 $`K\times K`$ 관계 행렬 비교(스케일 불변).
- **`total_objective`** — flow-matching 손실과 optimizer(AdamW) 사이에 가중합으로 결합. 세 보조 모델은 optimizer 그래프 밖(동결).

---

## ⛓️ 불변식·가정

- **(마스크 이진성)** — $`\mathbf{M}^{\mathrm{phy}}\in\{0,1\}^{T\times H\times W}`$ 이며 적응 임계값(궤적 점수 평균) 위 궤적만 1. 마스크가 전부 0/1 로 붕괴하면(전경 없음/전경 전면) 영역 집중의 이점이 사라짐.
- **(전경-깊이 단조성)** — 전경 가중 $`r_{i}=1/(D_{0}+\epsilon)`$ 는 가까운 표면일수록 크다는 가정. 상대 depth 가 반전/무의미하면(반사·투명) 마스크가 오선택.
- **(궤적 index 정합)** — 예측 궤적과 참조 궤적이 같은 query 점 index·프레임에서 대응. tracker 가시성(visibility) 손실 시 대응 붕괴.
- **(토큰 index 정합)** — DiT 특징을 teacher 토큰 격자(`32×16×16`)로 리샘플해 student/teacher 토큰이 index-정렬됨. resize/pad 로 시공간 layout 일치가 전제.
- **(관계 정렬의 스케일 불변)** — 코사인 관계 행렬을 맞추므로 두 표현 공간의 절대 스케일·기저 차이에 불변. 이 성질이 깨지면(정규화 누락) L1 정렬이 무의미.
- **(추론 불변)** — 보조 모델은 학습-only. 추론 그래프에 어떤 파라미터도 추가되지 않아야 함(추론 비용 0 보장).

---

## 📊 하이퍼파라미터·손실

- 전체 손실: $`\mathcal{L}=\mathcal{L}_{\mathrm{FM}}+\lambda_{\mathrm{pix}}\mathcal{L}^{\mathrm{phy}}_{\mathrm{pix}}+\lambda_{\mathrm{sem}}\mathcal{L}^{\mathrm{phy}}_{\mathrm{sem}}`$
  - pixel: $`\mathcal{L}^{\mathrm{phy}}_{\mathrm{pix}}=\frac{1}{|\mathbf{M}^{\mathrm{phy}}|}\left\|\mathbf{M}^{\mathrm{phy}}\odot(\mathcal{P}_{\mathrm{pred}}-\mathcal{P}_{\mathrm{gt}})\right\|_{2}^{2}`$
  - semantic: $`\mathcal{L}^{\mathrm{phy}}_{\mathrm{sem}}=\frac{1}{K^{2}}\sum_{i,j}\left|\hat{\mathbf{R}}(i,j)-\mathbf{R}(i,j)\right|`$

| 이름 | 값 | 출처 |
|------|----|----|
| `lambda_pix` | (원문에 명시 없음 — 가정으로 메움) | §3.4, Eq. 13 |
| `lambda_sem` | (원문에 명시 없음 — 가정으로 메움) | §3.4, Eq. 13 |
| `eps` ($`\epsilon`$) | (원문에 명시 없음 — 가정으로 메움) | §3.1, Eq. 2 |
| alignment 블록 index | 중간 블록 (Wan A14B 기준 block 20; Wan5B 스윕서 layer 15 최적 85.2) | §3.4, App. A, Table 6 |
| `K` (mask 토큰 상한) | ≤ 512 | App. A |
| teacher 토큰 격자 | `32×16×16` (tubelet 2, patch 16) | App. A |
| query 격자 | `25×25` (625점), CoTracker3 offline | App. A |
| optimizer / lr | AdamW / $`1\times10^{-5}`$ (Wan 계열) | §4.1 |
| steps / batch | 20K / global 128 (Wan 계열) | §4.1 |
| 입력 해상도·프레임 | Wan `640×480`·≤81 / Cosmos `720`p·≤189 | §4.1 |

---

## 🎯 평가 메트릭

- **지표** — R-Bench Avg. (task-oriented + embodiment-specific) · **임계값** — base 대비 향상(PF-Cosmos 63.8, +9.2%; PF-Wan 62.0, +22.3%) · **비교 baseline** — base / vanilla finetune / open-source·commercial·robotics-specific.
- **지표** — PAI-Bench-G · EZS-Bench(zero-shot OOD) overall average · **비교 baseline** — vanilla finetune, Abot-PhysWorld, commercial.
- **지표** — WorldArena action-planner 폐루프 성공률 · **임계값** — 16.0→24.0% · **비교 baseline** — WoW(20.5) 등 world-model planner.
- **지표** — Fast-WAM downstream 정책 성공률(RoboTwin 2.0, 200 rollouts/task) · **임계값** — avg 68.2→72.8% · **비교 baseline** — 무-PhysisForcing 백본.
- **Ablation** — 성분(pix/sem/both), 영역 집중(w/·w/o), alignment 층 index.

---

## ✨ 변경 의도 (intent)

prior art(기하 단서·preference 정렬)는 물리 감독을 단일 수준(국소 기하)에서, 혹은 전 프레임 균등하게, 혹은 사후(post-hoc)로 가합니다. PhysisForcing 은 (1) 물리 증거가 밀집한 **영역만 골라**(region-focused) (2) **픽셀 궤적 연속성**과 **의미 수준 관계 일관성**을 **동시에**(hierarchical) (3) **학습 중에 예방적으로** 규제한다는 점이 다릅니다. 특히 동결 video encoder(V-JEPA 2)의 토큰 관계 행렬을 관계 정렬 타깃으로 재활용해 전역 상호작용(gripper-물체 결합 등)을 좌표 손실 없이 유도하고, 모든 보조 모델을 추론에서 폐기해 비용 증가 없이 물리 정합을 얻습니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 본 논문은 **diffusion/flow-matching video DiT** 백본의 학습-시점 auxiliary loss 레시피라, lerobot 의 정책 family 중 flow-matching 계열(`pi0` / `pi05`)의 학습 루프에 auxiliary loss term 을 얹는 형태와 개념적으로 가장 가깝습니다. 다만 lerobot 은 로봇 **정책**(행동 예측) 중심이고 영상 **생성** world model(DiT + VAE + 영상 인코더 teacher)을 갖추지 않아, base 후보가 분명하지 않습니다 — `/implement-design` 이 UNMAPPABLE 로 판정할 가능성이 높습니다. 매핑 가능 부분은 "중간 특징에 masked auxiliary alignment loss 를 더하는 훅" 정도로 국한.

---

## 🚧 미해결 / 잠정

- 손실 가중 $`\lambda_{\mathrm{pix}}`$ · $`\lambda_{\mathrm{sem}}`$, 수치 안정 상수 $`\epsilon`$ 값이 본문 미명시 — sweep/가정 필요.
- MLP $`\phi`$(pixel 정제)· $`\psi`$(semantic 사영) 의 구체 구조(층 수·차원)가 본문 미명시.
- Cosmos3-Nano 의 alignment 대상 "mid-depth MoT block" 정확한 index 미명시(Wan A14B 는 block 20 명시).
- RoVid-X 필터링 임계값(motion-score·중복 제거·clip-text 정렬)·최종 500K 클립 목록 미공개.
- pixel 손실의 $`\mathcal{P}_{\mathrm{pred}}`$ 를 프레임별 특징 격자에서 좌표로 환산하는 구현 세부(좌표 스케일·정규화)가 식(5~8) 수준까지만 서술.
