# Design — Let Robots Feel Your Touch: Visuo-Tactile Cortical Alignment for Embodied Mirror Resonance

> PROBE design 산출물 (Layer 1, vendor-agnostic). 단일 한글 문서이며
> 영문 1차 파일은 없습니다. `/analyze-paper` 가 `analysis/<id>/analysis.md` 와
> 함께 자동 생성합니다 — 알고리즘 명세를 base 좌표계 없이 추출합니다.
> base 매핑은 `/implement-design` 단계에서 수행합니다. 형식·이모지·용어 규칙은
> `docs/STYLE.md` §6 / §4 를 정확히 따릅니다. 재실행 시 이 파일을
> 덮어씁니다.

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Let Robots Feel Your Touch: Visuo-Tactile Cortical Alignment for Embodied Mirror Resonance |
| 링크 | [arXiv:2605.14571](https://arxiv.org/abs/2605.14571) |
| 분석 문서 | [`analysis/2605.14571/analysis.md`](./analysis.md) |
| 본문 확보 수준 | PDF 텍스트(PyMuPDF) |
| Design 생성일 | 2026-06-02 |

<!-- 주의: 손실 수식이 담긴 Methods 절이 PDF 추출본에 누락되어, 수식 형태가
     필요한 항목은 "(원문 Methods 미확보 — 본 추출에 미포함)" 으로 정직하게
     비웁니다. 본문이 prose 로 명시한 구조까지만 Layer 1 스펙으로 굳힙니다. -->

---

## 🧮 데이터 계약

<!-- 시간 축은 절대 좌표가 아닌 의미 단위로 기록. -->

- **입력 (시각)** — RGB 영상열: shape `(B, K, 3, H, W)`, `K = 5` 연속 프레임(`§2.3` Fig.3b 근거). dtype float, 정규화 통계는 (원문에 명시 없음 — 가정으로 메움).
- **입력 (촉각, 학습 시에만)** — 접촉 신호를 점군으로 정식화: 개념적 shape `(B, N_taxel, C)`, `N_taxel = 1,140` (11개 센서 세그먼트), 채널 = 3축 힘 + taxel 3D 좌표(somatotopic 조건). 추론 시에는 사용하지 않음(시각 prior 만).
- **출력 (taxel 힘)** — 각 taxel 의 3D 힘 벡터: shape `(B, N_taxel, 3)`, `N_taxel = 1,140`, 1 mm 공간 해상도. 현재 시점(current time step) 예측.
- **출력 (센서 접촉 상태)** — 11개 센서의 이진 접촉 상태: shape `(B, 11)`, {접촉/비접촉}. taxel 예측을 공간적으로 변조하는 데 사용.
- **조건 (somatotopic map)** — taxel 의 3D 좌표가 인코딩·디코딩을 조건화. shape `(N_taxel, 3)`, 손 형태 고정 상수.

---

## 🧰 모듈 인터페이스

<!-- 함수/클래스 시그니처 수준의 경계. base 좌표(file:line) 없음. -->

```python
def visual_encoder(frames) -> z_v:
    """연속 RGB 프레임열 (B,K,3,H,W) → 시각 잠재 z_v. 경량 백본(ResNet 계열)."""

def tactile_encoder(contact_points, taxel_xyz) -> z_t:
    """접촉 점군 + taxel 3D 좌표 → 촉각 잠재 z_t. 경량 백본(PointNet 계열).
       학습 시에만 호출(디코더 posterior 조건화·anchor 용)."""

def parietal_project(z) -> z_latent:
    """시각/촉각 스트림을 두정엽 유사 통합 잠재 공간으로 투영(공유)."""

def shared_decoder(z_latent, taxel_xyz) -> (force_pred, contact_state):
    """통합 잠재 + somatotopic 좌표 → (1,140×3 힘 예측, 11 센서 접촉 상태).
       추론 시 입력은 시각 prior 분포에서만 옴."""

def mtnet_loss(force_pred, contact_state, targets, z_v, z_t, z_t_ema) -> dict:
    """11항 복합 손실: 재구성 5 + 정렬 6.
       반환 dict = {recon(W-MSE, W-MAE, ...×4), bce_contact,
                    kl_intra_v, kl_intra_t, kl_cross_prior, kl_cross_post,
                    infonce_force_aware, relational_distance}."""
```

AMTNet (교차도메인 확장):

```python
def human_visual_encoder(human_frames) -> z_v_human:
    """사람 손 전용 시각 인코더. AMTNet 에서 새로 학습되는 유일한 인코더."""

def gating_network(frames) -> alpha:
    """입력 도메인 판별 게이트 α ∈ [0,1] (α→1 사람, α→0 로봇).
       사람/로봇 시각 경로 중 하나로 라우팅."""

def amtnet_forward(frames):
    """gating 으로 도메인 선택 → (human|robot) visual encoder →
       동결된 MTNet 코어(parietal_project + shared_decoder) → 촉각 예측.
       MTNet 의 visual/tactile encoder + decoder 는 frozen."""
```

- 외부 호출 계약 — `mtnet_loss` 의 `z_t_ema` 는 촉각 posterior 의 *안정화 이동평균* 추정치(교차모달 KL anchor). AMTNet 학습은 `human_visual_encoder` + `gating_network` 파라미터만 옵티마이저에 등록(나머지 freeze).

---

## ⛓️ 불변식·가정

<!-- 깨지면 알고리즘이 무효가 되는 수학적/통계적 성질. base 무관. -->

- (가정 1) — 물리적으로 유사한 접촉 사건은 시각 잠재 공간에서도 가까워야 한다 — 시각·촉각의 *쌍거리 행렬*이 배치 단위로 일치해야 하며(relational alignment), 이 정렬이 깨지면 교차모달 매핑이 평균 응답으로 붕괴한다.
- (가정 2) — 비가중 재구성 손실은 0/평균 응답으로 수렴한다. 접촉이 공간·시간 모두 *희소*하기(대다수 taxel·시점이 비접촉) 때문이다. 그래서 접촉 영역 가중(W-MSE/W-MAE) 과 정렬 제약 없이는 유효 신호를 학습하지 못한다.
- (가정 3) — 추론 시에는 촉각 없이 시각 prior 만으로 디코딩하므로, 시각 prior 분포가 촉각 posterior(의 이동평균)에 anchor 될 만큼 정보를 담아야 한다. 학습 시 두 분포의 KL 정렬이 추론 품질의 상한을 결정한다.
- (가정 4, AMTNet) — 사람 시각 표현을 *이미 촉각과 정렬된* 로봇 시각 매니폴드에 임베딩하면, 사람 촉각 정답 없이도 동결 디코더가 로봇 촉각 예측을 사람 손에 전이한다(시각 공간 정렬 ⇒ 간접 촉각 정렬).
- (가정 5) — taxel 3D 좌표 조건화가 잠재 표현을 손 형태에 접지한다. somatotopic 좌표가 없으면 1,140 출력의 공간 구조가 무너진다.

---

## 📊 하이퍼파라미터·손실

<!-- 식과 값. 본문에 없는 값은 정직하게 비움. -->

- 손실 식 (구조만; 수식 형태 미확보):
  `L = Σ_{i=1..5} L_recon^i + Σ_{j=1..6} L_align^j`
  - 재구성 5항: taxel 수준 4항(W-MSE, W-MAE = 접촉 영역 가중 MSE/MAE 포함) + 센서 수준 접촉 상태 BCE 1항.
  - 정렬 6항: 모달 내부 prior-posterior KL 2항 + 교차모달 KL 2항(시각 prior·posterior ↔ 촉각 posterior 이동평균 anchor) + force-aware InfoNCE 대조 1항 + relational(쌍거리 행렬) 1항.
  - (정확한 항별 수식 — 원문 Methods 미확보 — 본 추출에 미포함.)

- 하이퍼:
  | 이름 | 값 | 출처 |
  |------|----|----|
  | `K` (입력 프레임 수) | `5` | §2.3 (Fig.3b "K = 5 consecutive visual frames") |
  | `N_taxel` | `1,140` | §2.1 |
  | 센서 수 | `11` | §2.1 |
  | 공간 해상도 | `1 mm` | §2.1 |
  | 손실 항 수 | `11` (재구성 5 + 정렬 6) | §2.2 |
  | 반사 임계 힘 | `0.2 N` | §2.6 |
  | 반사 reset 시간 | `0.5 s` (무입력 시) | Fig.6 캡션 |
  | 데모 영상 프레임율 | `30 Hz` | §2.6 |
  | 각 정렬 손실 가중치 | (원문 Methods 미확보) | — |
  | 옵티마이저 / LR / 에폭 | (원문 Methods 미확보) | — |
  | KL 이동평균 계수 | (원문 Methods 미확보) | — |

---

## 🎯 평가 메트릭

<!-- 채점 방식. 가능한 한 verbatim. -->

- **지표 (5종, 희소·국소 접촉용)**
  - `NRMSE` (Normalized Root Mean Square Error) — ↓ 낮을수록 좋음 · 힘 크기 오차.
  - `S-SimCos` / `S-CosSim` (Spatial Cosine Similarity) — ↑ · 접촉 영역 내 공간 힘 분포 일치.
  - `S-CCC` (Smooth Concordance Correlation Coefficient) — ↑ · 연속 상호작용 중 힘 변화의 시간적 일관성.
  - `T-IoU` (Temporal Intersection over Union) — ↑ · 임계 접촉맵의 시공간 중첩(접촉 시점).
  - `W-F1` (Windowed F1) — ↑ · 시간 윈도 내 접촉 사건 검출 정확도.
- **비교 baseline** — Unaligned MTNet(재구성 5항만, 정렬 제약 제거), 및 정렬 계열별 leave-one-out(w/o distribution / representational / rational alignment). 5회 평균 ± SD.
- **임계값/대표 결과 (Table S1, Aligned MTNet)** — `T-IoU = 0.8814`, `W-F1 = 0.7920`, `S-CosSim = 0.6097`, `S-CCC = 0.9664`, `NRMSE = 0.0102`. distribution alignment 제거 시 T-IoU 0.0404 로 붕괴(가장 load-bearing).
- **매니폴드 진단 메트릭** — silhouette coefficient, CKA(Centered Kernel Alignment). 전체 MTNet CKA ≈ 0.74(미학습·미정렬 대비 +0.22·+0.55). AMTNet 도메인 간 CKA 0.07 → 0.93, 게이팅 바타차리야 거리 0 → 7.6.

---

## ✨ 변경 의도 (intent)

기존 시각→촉각 예측(VAE/MAE 계열)은 재구성 손실 최소화에만 의존해 직접 매핑이 어려운 교차모달 회귀를 그대로 떠안습니다. 이 알고리즘은 다릅니다. *피질 정렬 원리*를 확률(KL)·특징(InfoNCE)·기하(relational) 세 수준의 제약으로 번역해, 시각 매니폴드를 촉각 매니폴드와 호환되는 기하로 재편합니다. 차별점은 세 가지입니다. 먼저 융합이 아니라 분리된 표현 공간 사이의 정렬을 노립니다. 그 정렬은 CKA·silhouette 로 정량 검증합니다. 마지막으로 동결-코어 + 게이팅을 써서 사람 손에 *촉각 정답 없이* 교차도메인 전이합니다. 이로써 촉각은 수동적 사후 피드백이 아니라 시각과 미리 정렬된 표현으로 올라섭니다.

---

## 🔌 Foundry 힌트 (선택)

<!-- 후보 수준 1–2줄. 실제 매핑은 /implement-design. -->

- **`lerobot`** — 직접적 family 대응이 약함. 본 알고리즘은 VLA 액션 정책(`pi0`/`smolvla`/`act`/`diffusion`)이 아니라 *시각→촉각 예측을 위한 별도 인코더-디코더 + 다중 정렬 손실*이라, lerobot 의 policy family 어디에도 1:1 매핑되지 않습니다. 굳이 고르면 인코더-디코더 + CVAE 구조라는 점에서 `diffusion`/생성 계열의 표현 학습 모듈과 거리가 가깝지만 핵심 자산은 *정렬 손실 묶음*이며 이는 policy 본체보다 보조 손실/표현 학습 컴포넌트로 이식하는 편이 자연스럽습니다. 매핑 불가 가능성 높음 — `/implement-design` 가 판정.

---

## 🚧 미해결 / 잠정

<!-- 정직하게. 없음이면 "없음". -->

- **손실 수식 전부** — 11개 손실 항의 정확한 수식·정규화·가중치는 원문 Methods 절이 본 PDF 추출에 누락돼 미확보. 본문 prose 가 명시한 *구조*(재구성 5 + 정렬 6, 각 정렬의 수준)까지만 굳혔습니다.
- **학습 셋업** — 옵티마이저, 학습률, 에폭, 배치 크기, 하드웨어(GPU), KL 이동평균 계수, InfoNCE 온도 등 모두 미확보(가정 메움 금지 — 비워 둠).
- **정규화 통계** — RGB·힘 입력의 정규화 평균/표준편차 출처가 본문에 없어 "데이터셋 전체 통계"로 가정.
- **점군 정식화 세부** — 촉각을 point cloud 로 formulate 한다고만 명시. 점 수·좌표계·채널 구성의 정확한 정의는 미확보.
- **게이팅 네트워크 구조** — α 산출 네트워크의 아키텍처·학습 손실 형태 미확보(분포 분리 결과만 보고됨).
