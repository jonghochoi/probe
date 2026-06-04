# Design — Dexterity-BEV: Aligning 3D World and Actions for Generalizable Robot Policies Learning

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
| 원문 제목 (영문) | Dexterity-BEV: Aligning 3D World and Actions for Generalizable Robot Policies Learning |
| 링크 | [arXiv:2606.02274](https://arxiv.org/abs/2606.02274) |
| 분석 문서 | [`analysis/2606.02274/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-06-04 |

---

## 🧮 데이터 계약

시간 축은 step $`t`$ 와 action chunk 길이 $`M`$ 으로 표기. 카메라 수 $`N`$.

- **입력 (관측)** — `state` $`\mathcal{X}_{t}=\{\{(\mathbf{O}_{t,i},\mathbf{K}_{i},\mathbf{T}_{t,i})\}_{i=1}^{N},\mathcal{L},\mathbf{s}_{t}\}`$
- **입력 (RGB)** — `image` $`\mathbf{I}_{t,i}`$: shape `(B, N, 3, H, W)`, float, VLM 전처리 정규화
- **입력 (depth, 선택)** — `depth` $`\mathbf{D}_{t,i}`$: shape `(B, N, H, W)`, float(미터), 없으면 vertex spectrum 으로 대체
- **입력 (intrinsic)** — `K` $`\mathbf{K}_{i}\in\mathbb{R}^{3\times 3}`$: shape `(B, N, 3, 3)`, OpenCV 표준
- **입력 (extrinsic)** — `T` $`\mathbf{T}_{t,i}\in SE(3)`$: shape `(B, N, 4, 4)`, 카메라→공유 프레임 변환
- **입력 (proprioception)** — `s` $`\mathbf{s}_{t}`$: 공유 BEV 프레임의 $`SE(3)`$ 포즈로 표현
- **입력 (language)** — `instruction` $`\mathcal{L}`$: 토큰 시퀀스
- **유도 입력 (3D)** — aligned vertex map $`\mathbf{P_{aligned\_i}}`$: shape `(B, N, 3, H, W)`, RGB 와 픽셀 정렬; depth 부재 시 vertex spectrum 격자 $`\mathcal{G}_{u,v}\in\mathbb{R}^{M\times 3}`$
- **유도 입력 (BEV)** — 합성 BEV 이미지 + 대응 vertex map: 전 카메라 컬러 포인트클라우드의 top-down 정사영
- **출력 (액션)** — `action` $`\{\mathbf{A}_{t+m}\}_{m=1}^{M}`$: 공유 BEV 프레임의 절대 $`SE(3)`$ 포즈 chunk, flow-matching 으로 생성
  - 정규화: 액션·proprioception 모두 공유 프레임 $`\mathbf{T}_{align\_t}`$ 기준 (원문에 명시적 mean/std 통계는 없음 — `(원문에 명시 없음 — 가정으로 메움)`)

---

## 🧰 모듈 인터페이스

```python
def back_project(K_i, D_ti, uv) -> P_camera_i:
    """픽셀 (u,v) 를 intrinsic·depth 로 camera-frame 3D 정점으로 역투영 (식 2)."""

def align_vertex_map(P_camera_i, T_align_t, T_ti) -> P_aligned_i:
    """camera-frame vertex map 을 공유 정렬 프레임으로 변환 (식 4). RGB 와 픽셀 정렬 유지."""

def vertex_spectrum(uv, K_i, T_ti, d_min, d_max, M) -> G:
    """depth 부재 RGB 뷰용: LID 깊이 가설 샘플링 (식 5) → volumetric 좌표 격자."""

def build_bev(point_clouds, T_align_t) -> (bev_image, bev_vertex_map):
    """전 카메라 컬러 포인트클라우드를 top-down 정사영해 BEV 이미지 + vertex map 합성."""

def vlm_backbone(images, bev_features, vertex_maps, spectrum, instruction) -> c_t:
    """멀티뷰 토큰·BEV 특징·3D 표현·언어를 융합해 contextual embedding c_t 생성."""

def flow_matching_expert(c_t, sigma, a_sigma) -> v_theta:
    """c_t 조건부 벡터장 회귀 (식 1); 추론 시 ODE solver 로 SE(3) 액션 chunk 샘플링."""
```

- `back_project` / `align_vertex_map` — 입력: intrinsic·extrinsic·depth, 출력: 공유 프레임 vertex map. 학습 파라미터 없음(기하 변환).
- `vertex_spectrum` — depth 없는 뷰에서 `align_vertex_map` 대체; 경량 인코더가 2D positional embedding 으로 변환해 RGB 특징에 element-wise 가산.
- `build_bev` — extrinsic 기반 기하 융합(학습 없는 정사영); D12 의 cross-attention fuser 와 대비되는 경로.
- `flow_matching_expert` — `L_FM`(식 1)로 학습; π0 계열 action expert 와 동일 계약.

---

## ⛓️ 불변식·가정

- (가정 1) 픽셀 정렬 — aligned vertex map 은 RGB 이미지와 픽셀 단위로 정렬되어야 한다. 정렬이 깨지면 3D 특징과 2D 특징의 element-wise 결합이 무의미해진다.
- (가정 2) 공유 프레임 일관성 — 모든 카메라 vertex map·proprioception·액션이 동일 $`\mathbf{T}_{align\_t}`$ 로 표현된다. 한 모달리티라도 다른 프레임에 있으면 입출력 정렬 이득이 소멸.
- (가정 3) 캘리브레이션 정확성 — intrinsic $`\mathbf{K}_{i}`$ 와 extrinsic $`\mathbf{T}_{t,i}`$ 가 정확해야 역투영·변환이 물리적으로 유효. 캘리브레이션 오차는 vertex map 정렬을 직접 오염.
- (가정 4) Quasi-static 작업 — 시간 정렬(EE 속도 정규화)은 작업이 quasi-static 이어서 속도를 바꿔도 작업이 성립한다는 가정에 의존. 동적 작업(예: 던지기)에는 불성립.
- (가정 5) 시점 불변성 — BEV 정사영 결과는 카메라 포즈가 크게 달라도 객체가 거의 같은 픽셀 위치에 오도록 충분히 불변해야 한다(§3.3 주장).

---

## 📊 하이퍼파라미터·손실

- 손실 식 (Flow Matching, 식 1):

$$\mathcal{L}_{FM}=\mathbb{E}_{\sigma\sim\mathcal{U}[0,1],\mathbf{a}_{1}\sim p_{data},\mathbf{a}_{0}\sim p_{0}}\left[\|\mathbf{v}_{\theta}(\sigma\mathbf{a}_{1}+(1-\sigma)\mathbf{a}_{0},\sigma,\mathbf{c}_{t})-(\mathbf{a}_{1}-\mathbf{a}_{0})\|^{2}\right]$$

- 역투영 (식 2): $`\mathbf{P}_{camera\_i}(u,v)=\mathbf{K}_{i}^{-1}[u,v,1]^{T}\mathbf{D}_{t,i}(u,v)`$
- 정렬 변환 (식 4): $`\mathbf{F_{3d\_i}}=\mathsf{Enc}_{3d}(\mathbf{T}_{align\_t}^{-1}\mathbf{T_{t,i}}\mathbf{P}_{camera\_i})`$
- LID 깊이 이산화 (식 5): $`d_{j}=d_{min}+(d_{max}-d_{min})\cdot\frac{j(j+1)}{M(M+1)}`$

- 하이퍼:
  | 이름 | 값 | 출처 |
  |------|----|----|
  | `N` (카메라 수) | 셋업 의존 (원문 미명시 수치) | §3.1 |
  | `M` (action chunk 길이) | (원문 미명시) | §3.1 |
  | `M` (vertex spectrum 깊이 가설 수) | (원문 미명시) | §3.3, Eq. (5) |
  | `[d_min, d_max]` | 작동 깊이 범위 (수치 미명시) | §3.3, Eq. (5) |
  | optimizer / LR / batch / steps | (원문 미명시 — Appendix/코드) | §4 |

---

## 🎯 평가 메트릭

- **지표** — task 성공률(success rate, %) · **임계값** — baseline($`\pi_{0}`$, X-VLA) 및 2D ablation 대비 우위 · **비교 baseline** — $`\pi_{0}`$, X-VLA, 2D ablation
- **일반화 (핵심)** — Modified LIBERO 의 카메라 포즈 + 로봇/씬 base 포즈 강섭동 하 성공률 유지. baseline·2D ablation 은 $`<10`$%, Dex-BEV 는 평균 89.9% (§4.1, Table 2)
- **Cross-embodiment** — 단일 체크포인트로 LIBERO(7-DoF franka) + RoboTwin-2.0(12-DoF agile-x) 동시 평가 (§4.1, Table 1)
- **실로봇** — 5개 long-horizon 양팔 작업, 작업당 30회 시도 평균 성공률 (§4.2, Table 3)
- **학습 동역학** — 학습 loss 곡선으로 2D baseline 의 포즈 변동 흡수 실패 비교 (Fig. 4)

---

## ✨ 변경 의도 (intent)

prior art 대비 차별점은 **개별 기법이 아니라 입출력 3D 정렬을 하나로 묶어낸 결합**이다. 순수 3D 입력(point cloud/voxel)은 2D VLM 의 웹스케일 일반화를 버리므로, 대신 픽셀 정렬을 유지한 vertex map/spectrum 으로 2D VLM 위에 3D 를 얹으면서, 기존 VLA 가 방치하던 출력 공간을 proprioception·액션까지 모두 공유 BEV 프레임의 $`SE(3)`$ 포즈로 표현해 임베디먼트·카메라·데이터셋 간 "불필요한" 액션 분포 변동을 제거한다. 멀티카메라 융합도 학습된 attention 이 아니라 extrinsic 기반 기하 정사영(BEV)으로 처리해, 시점 불변 입력을 학습 부담 없이 확보한다. 여기에 이질 데이터셋을 공간(TCP·extrinsic 통일)·시간(EE 속도 정규화)으로 정렬하는 파이프라인을 더한 것이 핵심 변경 의도다.

---

## 🔌 Foundry 힌트 (선택)

- **`lerobot`** — 후보 base: action expert 가 flow-matching 이므로 `pi0` / `pi05` family 와 가장 가깝다. 단 본 논문의 신규성은 action head 가 아니라 **백본 앞단의 3D 입력 표현 + 입출력 공유 BEV 좌표 정렬 + 데이터 정합 전처리**에 있다. 그러므로 `pi0` 입력 파이프라인(이미지·state 전처리, normalization)과 데이터셋 transform 계층에 vertex map/BEV/extrinsic 처리를 추가하는 매핑이 유력하다. 액션 정규화도 공유 프레임 절대 $`SE(3)`$ 기준으로 바꾸는 변경이 수반.

---

## 🚧 미해결 / 잠정

- 액션·proprioception 의 정규화 통계 출처가 본문에 없어 "공유 프레임 절대 $`SE(3)`$ 표현"까지만 확정, mean/std 산출 방식은 가정으로 비움.
- `N`(카메라 수), action chunk 길이 `M`, vertex spectrum 의 `M`·`[d_min, d_max]` 등 구체 수치가 본문에 미명시 — Appendix/공개 코드 의존.
- 옵티마이저·학습률·배치·스텝·하드웨어 규모 등 학습 셋업 수치가 본문에 없음.
- $`\mathsf{Enc}_{3d}`$ 및 vertex spectrum "경량 인코더"의 구체 아키텍처(레이어·채널)가 본문에 미명시.
- 시간 정렬(EE 속도 정규화)의 상세 절차가 Appendix 로 미뤄져 Layer 1 스펙으로 확정 불가.
- 공개 저장소 URL 이 추출본에서 `this https URL` 플레이스홀더로만 노출 — 실제 코드 주소 미확인.
