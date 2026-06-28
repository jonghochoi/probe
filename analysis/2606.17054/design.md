# Design — Human Universal Grasping

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Human Universal Grasping |
| 링크 | [arXiv:2606.17054](https://arxiv.org/abs/2606.17054) |
| 분석 문서 | [`analysis/2606.17054/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-28 |

---

## 🧮 데이터 계약

시간 축이 없는 **단일-스텝 그래스프 생성** 모델입니다 (action chunk·시계열 없음). 좌표계는 모두 카메라 프레임(OpenCV 컨벤션).

- **입력 — RGB 이미지**: shape `(B, 3, 224, 224)`, float, DINOv2 정규화(ImageNet mean/std 가정 — 원문 명시 없음). grayscale 학습 엔트리는 3채널 복제로 동일 인코더 사용.
- **입력 — 깊이맵**: shape `(B, 1, 224, 224)`, 메트릭 깊이(m). 카메라 intrinsics `K`(`(B, 3, 3)`)로 back-project 해 포인트클라우드 생성.
- **입력 — query 클릭**: 2D 픽셀 $`(u,v)`$ → 깊이값·`K` 로 lift 한 3D query point `p_q`: shape `(B, 3)`, 메트릭(m).
- **입력 — 포인트클라우드(파생)**: `p_q` 중심 `0.3 m` 반지름 ball crop 후 `N_p = 4096` 점 샘플링: shape `(B, 4096, 3)`, 메트릭 XYZ.
- **출력 — 그래스프 상태** `x`: shape `(B, 99)`, 정규화 공간에서 생성 후 de-normalize.
  - `t` (손목 translation): `(B, 3)`, 메트릭 카메라 프레임.
  - `R_6d` (손목 글로벌 회전): `(B, 6)`, zhou2019continuity 연속 6D 표현.
  - $`\mathbf{\theta}_{\text{6d}}`$ (15 MANO 손가락 관절): `(B, 15, 6)` = `(B, 90)`, 6D 회전.
- **고정 상수** — MANO 형태 $`\mathbf{\beta} \in \mathbb{R}^{10}`$ 은 단일 캐노니컬 값으로 고정(학습·예측 대상 아님). 1M-HUGs·HUG-Bench 의 모든 그래스프를 이 형태로 재계산.

---

## 🧰 모듈 인터페이스

```python
def rgb_encoder(rgb):  # (B,3,224,224) -> (B, N=256, D_dino)
    """frozen DINOv2-Base ViT + register tokens; N=256 패치 토큰."""

def pc_encoder(pc_crop):  # (B,4096,3) -> tokens (B,N=256,D_pc), centroids (B,N=256,3)
    """trainable PointNeXt U-Net; per-region 토큰 + 메트릭 XYZ 중심점."""

def fuse_point_painting(dino_tokens, pc_tokens, centroids, K, p_q):
    # -> scene tokens s: (B, N=256, D_f=1024)
    """centroid 를 K 로 RGB 투영 → DINOv2 특징 bilinear 샘플 → PC 토큰과 concat →
       2-layer MLP(D_f=1024). p_q·centroids 는 공유 random Fourier γ(·) 인코딩.
       융합 토큰이 query 토큰 q=MLP(γ(p_q)) 에 cross-attend, 4-layer pre-norm
       transformer 로 refine."""

def flow_transformer(x_t, t, s):  # -> velocity v: (B, 99)
    """x_t 를 (trans 3 / wrist 6 / finger 90) 세 토큰(D_m=512)으로 분리,
       scene 토큰 s 에 cross-attend, timestep t 를 AdaLN-Zero 로 주입하는
       L=6 DiT 블록, 3개 linear head 로 (3,6,90) 디코딩."""

def sample_grasp(rgb, depth, K, uv, n_steps=50):  # -> x: (B,99)
    """정규화 공간에서 50-step Euler ODE 적분 후 de-normalize."""

def retarget(mano_grasp, robot_hand):  # -> robot joint targets
    """MANO 그래스프를 로봇 손 관절로 사상. 손별 학습 없음(예: AnyTeleop / WUJI
       retargeting). fingertip 정렬용 단일 고정 offset(로봇 손 프레임)."""
```

- **인코더 분리** — RGB 인코더는 frozen, PC 인코더·fusion·flow transformer 만 학습.
- **intrinsics `K`** — 학습 파라미터가 아니라 back-project/project 연산으로만 진입(서로 다른 스테레오 카메라 전이의 근거).
- **손실과의 관계** — `flow_transformer` 의 velocity 출력은 속도 MSE 와, clean state 추정 후 MANO FK 를 통과시킨 3D 랜드마크 L1 보조 손실에 동시에 묶임(아래 📊).

---

## ⛓️ 불변식·가정

- **(가정 1) 캐노니컬 형태 정규화** — MANO $`\mathbf{\beta}`$ 가 단일 고정값이어야 같은 $`\mathbf{\theta}`$ 가 수집자·임베디먼트 무관하게 같은 그래스프를 의미. 학습/평가 데이터 전체가 동일 $`\mathbf{\beta}`$ 로 재계산되어야 라벨 일관성이 성립.
- **(가정 2) 메트릭 깊이 가용성** — 입력 깊이가 메트릭이어야 `0.3 m` crop·3D query lift·point painting 투영이 물리적으로 유효. 깊이가 비메트릭/부정확하면 모델은 RGB-only 수준으로 저하.
- **(가정 3) query point 가 객체 위에 있음** — `p_q` 가 타깃 객체 표면의 점이어야 crop 이 타깃을 덮음. 클릭이 빗나가면 잘못된 객체로 crop.
- **(가정 4) 우손·정적 단일 그래스프** — 모델은 오른손·단발 정적 자세만 표현(왼손/양손/시계열 접촉 제어는 표현 공간 밖).
- **(가정 5) 회전 표현 연속성** — 손목·손가락 회전을 6D 연속 표현으로 두어야 학습이 회전 불연속을 겪지 않음. quaternion/Euler 직접 회귀는 이 불변식을 깸.

---

## 📊 하이퍼파라미터·손실

전체 손실(식 1) — 속도 MSE + clean-state MANO 3D 랜드마크 L1:

$$\mathcal{L}=\lambda_{\text{v}}\,\mathcal{L}_{\text{v}}+\lambda_{3\text{D}}\,(1-t)\,\mathcal{L}_{3\text{D}}$$

clean state 추정: $`\hat{\mathbf{x}}_{0}=\mathbf{x}_{t}-t\,f_{\phi}(\mathbf{x}_{t},t,\mathbf{s})`$ 를 MANO 에 통과시켜 카메라 프레임 3D 손 랜드마크를 L1 으로 지도. $`(1-t)`$ 가중은 near-clean 스텝에 기하 손실 집중.

| 이름 | 값 | 출처 |
|------|----|----|
| $`\lambda_{\text{v}}`$ (속도 MSE 가중) | `1` | §4.2, Eq. (1) |
| $`\lambda_{3\text{D}}`$ (3D 랜드마크 L1 가중) | `20` | §4.2, Eq. (1) |
| 패치 토큰 수 `N` | `256` | §4.1 |
| PC 샘플 점 수 `N_p` | `4096` | §4.1 |
| PC crop 반지름 | `0.3 m` | §4.1 |
| 융합 토큰 차원 `D_f` | `1024` | §4.1 |
| 플로우 토큰 차원 `D_m` | `512` | §4.1 |
| DiT 블록 수 `L` | `6` | §4.1 |
| fusion transformer 깊이 | `4` (pre-norm) | §4.1 |
| 그래스프 상태 차원 | `99` (= 3+6+90) | §4.1 |
| 옵티마이저 / lr | AdamW / `1e-4` | §4.2 |
| batch size | `128` (GPU 당 `64`, 2×RTX 5090 DDP) | §4.2 |
| 학습 스텝 / warmup | `100K` / `5K` linear | §4.2 |
| 추론 적분 | `50`-step Euler ODE | §4.2 |
| EMA 시작 | step `50K` | §4.2 |
| 학습 timestep 샘플 | $`t \sim \mathrm{U}[0,1]`$ | §4.2 |

보조 — `aria2mano` MANO 피팅 손실(데이터 라벨 생성): $`\mathcal{L}=\mathcal{L}_{\text{lm}}+\mathcal{L}_{\text{anat}}`$, fingertip 랜드마크 가중 $`w_i=5`$ (기타 `1`), $`\lambda_{\text{mse}}=2{\times}10^{4}`$, L-BFGS, 평균 fingertip 오차 < 2 mm.

---

## 🎯 평가 메트릭

- **지표** — `SR` (success rate, %) · **임계값** — lift 후 객체가 표면에서 떨어져 있으면 성공 · **비교 baseline** — Dex1B(43.7%), CAP(32.7%), Human grasp oracle(94.0% test).
- **지표** — `FC error` (fingertip contact error, mm) · **정의** — 엄지와 가장 가까운 지지 손가락의 객체 표면까지 signed distance 평균 (식 2; smaller better) · **임계값** — full HUG test 14.6 mm vs oracle 7.4 mm.

$$\mathrm{FC}=\tfrac{1}{2}\!\left(\,|d_{\text{thumb}}|+\min_{f\in\mathcal{F}}\,|d_{f}|\,\right)$$

- **프로토콜** — 객체당 10 그래스프, val 60 / test 30 객체. best-val-SR 체크포인트를 test 에 객체별 튜닝 없이 배포. 시뮬레이션은 MuJoCo(position-actuated MANO 손, open-loop pre-grasp→grasp→lift, lift 0.5 m). 실세계는 retarget 후 동일 open-loop.

---

## ✨ 변경 의도 (intent)

기존 다지 그래스핑이 시뮬레이션 합성(force-closure / RL, sim-to-real 갭 + 손별 재학습)이나 텔레오퍼레이션(타깃 임베디먼트 한정·수집 부담)에 의존하던 것과 달리, HUG 는 **순수 in-the-wild 인간 그래스프 분포**를 단일-스텝 플로우 매칭으로 모델링하고 예측 MANO 그래스프를 손별 학습 없이 retarget 해 zero-shot 다중 임베디먼트 배포를 달성합니다. 핵심 차별 메커니즘은 (1) 완전 객체 PC 가 아닌 **단일-시점 카메라 프레임 RGB-D + query-centric crop**(실배포 일반화), (2) **point painting** 으로 깊이의 기하와 RGB 의 의미를 결합, (3) clean-state 를 MANO FK 로 통과시킨 **3D 랜드마크 보조 손실**(fingertip 정확도의 결정적 레버), (4) **intrinsics 를 학습 파라미터에서 배제**해 카메라 간 전이를 확보한 점입니다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 직접 대응 family 없음. HUG 는 시계열 action chunk 를 내는 VLA 정책이 아니라 **단일-스텝 그래스프 생성기**라, `act`/`diffusion`/`pi0` 류의 sequential policy 와 입출력 계약이 다릅니다. 가장 가까운 재사용 지점은 `diffusion`/`pi0` 의 **플로우/디퓨전 생성 헤드 + DiT 블록(AdaLN-Zero)** 정도이며, RGB-PC point-painting 인코더·PointNeXt·MANO FK 보조 손실은 lerobot 에 대응 모듈이 없어 신규 구현이 필요할 가능성이 높습니다. `/implement-design` 가 실제 매핑 가부(혹은 `🚧 매핑 불가`)를 판정.

---

## 🚧 미해결 / 잠정

- **정규화 통계 출처** — 그래스프 상태(99-dim)의 그룹별 정규화 mean/std 출처가 본문에 명시되지 않음 — "1M-HUGs 전체 통계" 로 가정.
- **RGB 정규화** — DINOv2 입력 전처리(ImageNet mean/std)는 표준 관행으로 가정(원문 미명시).
- **MANO MJCF / 시뮬 손 사양** — position-actuated MANO 손의 정확한 actuator gain·force-close 파라미터는 Appendix(LABEL 참조)로 빠져 본 분석 본문에서 미확보.
- **retarget 세부** — Ability=AnyTeleop, WUJI=WUJI retargeting 사용 및 고정 offset(Ability `[0.020, 0, 0.025] m` + `y`축 `10°`, pre-grasp wrist offset WUJI `[-0.05,0,-0.02] m` / Ability `[-0.04,0,-0.01] m`)까지는 명시되나, 일반 로봇 손으로의 retarget 절차 일반화는 손별 도구 의존.
- **다후보 선택 미적용** — 생성 모델임에도 trial 당 1 그래스프만 실행 — 다후보 생성 후 스코어링 선택은 미구현(저자도 향후 확장으로 언급).
