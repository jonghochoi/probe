# Paper Analysis — Let Robots Feel Your Touch: Visuo-Tactile Cortical Alignment for Embodied Mirror Resonance

> PROBE analysis 모드 산출물. 단일 한글 문서이며, 영문 1차 파일은
> 없습니다. 형식·이모지·용어 규칙은 `docs/STYLE.md` §5 / §4 를
> 정확히 따릅니다. 재실행 시 이 파일을 덮어씁니다.

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Let Robots Feel Your Touch: Visuo-Tactile Cortical Alignment for Embodied Mirror Resonance |
| 저자 | Tianfang Zhu, Ning An, Rui Wang, Jiasi Gao, Qingming Luo, Anan Li, Guyue Zhou (Tsinghua AIR · Hainan University · Beihang · HUST) |
| 링크 | [arXiv:2605.14571](https://arxiv.org/abs/2605.14571) |
| 발행일 / 버전 | 2026-05-14 · v1 (cs.RO) |
| 본문 확보 수준 | PDF 텍스트(PyMuPDF) |
| 분석 생성일 | 2026-06-02 |

<!-- 확보 경위(정직 기록):
     - `curl https://arxiv.org/html/2605.14571` → HTTP 404 (LaTeX-source HTML 미생성).
     - `curl https://ar5iv.labs.arxiv.org/html/2605.14571` → HTTP 403,
       `https://ar5iv.org/html/2605.14571` → HTTP 403.
     - `command -v pdftotext` → 없음. 대신 PyMuPDF(`fitz`)로
       `https://arxiv.org/pdf/2605.14571` (HTTP 200, 21쪽) 텍스트 추출.
     - 본문(서론·Results·Discussion) + 참고문헌 + 부록 그림 캡션 + Table S1 은 확보.
       단, "Methods" 절(손실 수식 정의)은 이 PDF 21쪽에 포함되지 않았고
       본문이 "Details are provided in Methods" / "See Sec. ?? for details"
       (깨진 상호참조)로 가리키므로, 손실 항의 수식 형태는 미확보입니다.
       아래 🔬 방법론은 본문이 prose 로 서술한 범위까지만 기록하며 수식은
       날조하지 않습니다.
     - PDF-only 확보이므로 STYLE §5-6 규칙에 따라 figure hotlink 은 생략합니다. -->

---

## 🧭 한 줄 요약 (TL;DR)

거울 촉각(mirror touch)의 신경 원리 — 시각·체성감각 피질의 구조적 정렬 — 을 계산 가능한 다중 제약으로 옮겨, RGB 영상만으로 로봇 손 위 1,140개 taxel 의 촉각 신호를 예측하고(MTNet), 그 예측을 관찰된 *사람* 손의 접촉에까지 전이(AMTNet)하는 뇌 영감(brain-inspired) 프레임워크입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 로봇이 접촉이 일어나기 *전에* 시각 관찰만으로 촉각 결과를 예측(anticipatory touch)하고, 타인이 만져지는 장면을 보고 자기 손에 대응 촉각을 떠올리는 "거울 촉각"을 구현할 수 있는가.
- **기존 접근의 한계** — 지배적 패러다임은 촉각을 *수동 피드백*으로만 취급합니다. 촉각 신호는 물리 접촉이 실제로 일어날 때만 얻어지므로 시간 지연이 생기고, 인간이 관찰만으로 수행하는 선제적 촉각 추론이 불가능합니다. VAE·MAE 기반 시각→촉각 예측 연구들도 재구성 손실 최소화에 의존해 뇌가 보이는 구조적 정렬 없이 어려운 교차모달 매핑을 떠안습니다.
- **본 논문의 가설** — 시각·체성감각 피질 간 "강하게 제약된 매핑(structured computational principle)"을 명시적 다중 제약으로 계산화하면, 흩어진 시각 표현을 촉각 매니폴드와 호환되는 기하로 재구성해 교차모달 매핑의 난이도를 낮출 수 있다.
- **왜 지금 중요한가** — 다지 손(anthropomorphic hand)용 고밀도 촉각 센싱이 성숙하면서, 촉각을 사후 피드백이 아니라 시각과 *정렬된* 표현으로 다루는 설계가 인간-로봇 상호작용(공감적 반응)과 신경 기반 체화 지능을 설명할 유력한 길로 자리잡았습니다.

---

## 🧩 핵심 기여

- **거울 촉각의 계산화** — 피질 정렬 원리를 의미(semantic)·분포(distributional)·기하(geometric) 세 수준의 다중 제약으로 번역한 듀얼 스트림 아키텍처 **MTNet** 을 제안합니다.
- **고밀도 시각→촉각 예측** — RGB 영상열만으로 로봇 손 위 1,140개 독립 taxel(11개 핑거 세그먼트, 1 mm 해상도)의 3축 힘 벡터를 예측하며, 기존 vision-based / 희소 촉각 접근보다 큰 교차모달 간극을 다룹니다.
- **매니폴드 재구성 분석** — 정렬 제약이 무질서한 시각 표현을 촉각 매니폴드와 일관된 구조로 재편함을 t-SNE·silhouette·CKA 로 정량 입증하고, 제약 제거 시 성능이 급락함을 보입니다.
- **교차도메인 전이 (AMTNet)** — MTNet 코어를 동결한 채 사람 손 전용 시각 인코더 + 게이팅 네트워크만 학습해, 사람 촉각 정답 없이 관찰된 사람 손 접촉으로부터 로봇 촉각을 예측합니다.
- **물리 로봇 거울 촉각 시연** — 예측된 힘이 0.2 N 임계를 넘으면 해당 손가락이 flick 반사를 내도록 해, 물리적으로 닿지 않은 로봇 손이 관찰된 사람 접촉에 반사적으로 반응함을 보입니다.

---

## 🔑 기술 키워드

- **Mirror touch** — 타인이 만져지는 것을 *보기만 해도* 관찰자 몸에 대응 촉감이 떠오르는 현상. 본 논문이 로봇에 이식하려는 신경·인지 목표 자체입니다.
- **Cortical alignment** — 시각 피질과 체성감각 피질의 표현이 구조적으로 대응(상위 시야 ↔ 높은 신체 부위)된다는 신경 원리. MTNet 이 거는 제약의 설계 근거가 됩니다.
- **Taxel** — 촉각 센서 표면의 단위 측정점(tactile element). 이 손은 11개 센서에 걸쳐 1,140개 taxel 로 3축 힘을 1 mm 해상도로 잰다는 점이 핵심 난이도입니다.
- **CVAE (Conditional Variational Autoencoder)** — 조건부 잠재변수 생성 모델. MTNet 이 잠재 공간을 확률 수준에서 정규화하고 KL 항을 거는 골격입니다.
- **InfoNCE contrastive alignment** — 유사한 물리 접촉의 표현은 당기고 상이한 사건은 미는 대조 학습. 여기서는 "force-aware" 변형으로 시각·촉각 표현을 특징 수준에서 정렬합니다.
- **Relational (geometric) alignment** — 배치 내 표본 간 쌍거리 행렬(pairwise distance matrix)을 시각·촉각 사이에서 일치시키는 제약. 매니폴드의 *기하*를 맞춥니다.
- **CKA (Centered Kernel Alignment)** — 두 표현 집합의 유사도를 재는 지표. 시각 매니폴드가 촉각 매니폴드에 얼마나 정렬됐는지의 정량 척도로 쓰입니다.
- **Somatotopic conditioning** — taxel 의 3D 좌표로 인코딩·디코딩을 조건화해 "인공 체성감각 지도"를 부여하는 설계. 잠재 표현을 손 형태(morphology)에 접지합니다.
- **Cross-domain transfer (AMTNet)** — 동결된 로봇용 코어 위에 사람 도메인 시각 공간을 정렬해, 촉각 정답 없는 사람 손으로 예측을 옮기는 전략.

---

## 🔬 방법론

> 주의 — 본 PDF 추출본에는 손실 항의 수식 정의가 담긴 "Methods" 절이 포함되지 않았습니다(본문이 "Details are provided in Methods" / "See Sec. ?? for details" 로만 가리킴). 아래는 본문이 산문으로 명시한 범위까지의 기록이며, 수식은 추정·날조하지 않습니다.

### 직관

뇌의 "감각 분리 후 통합" 구조를 모사해, 시각·촉각을 별도 표현 공간에 두되 둘 사이를 강한 다중 제약으로 정렬한다는 것이 핵심 직관입니다.

> "Following the brain's sensory segregation and integration, MTNet models visual and tactile modalities in separate representational spaces, with their structured alignment enforced through six constraints, including distributional alignment, semantic correspondence, and sample-wise distance consistency." (§1)
> (한글 해설 — 시각·촉각을 분리된 표현 공간에 두고, 분포 정렬·의미 대응·표본 간 거리 일관성을 포함한 6개 제약으로 구조적 정렬을 강제한다는 설계 의도를 한 문장에 못 박습니다. 단순 재구성이 아니라 "정렬"이 메커니즘의 주어임을 선언합니다.)

설계가 모델 용량이 아니라 *구조적 귀납 편향*에서 나오도록, 인코더는 일부러 경량 백본을 씁니다.

> "Notably, both encoders employ lightweight backbones (e.g., ResNet and PointNet) to ensure that MTNet's efficacy is driven by its architectural inductive biases rather than massive model capacity." (§2.2)
> (한글 해설 — ResNet·PointNet 급 경량 인코더로 성능 향상이 거대 용량이 아닌 아키텍처적 편향에서 비롯됨을 보이려는 의도입니다.)

### 아키텍처

- **입력 / 출력** — 시각 경로는 연속 이미지 프레임(K=5)을 받아 ResNet 계열로 특징을 뽑고, 촉각 경로는 접촉 신호를 *점군(point cloud)* 으로 정식화해 PointNet 계열로 처리합니다. 모델은 연속 프레임으로부터 현재 시점 각 taxel 의 3D 힘 벡터를 예측합니다.

> "By contrast, our hand contains 1,140 discrete mechanoreceptor-like taxels across 11 finger segments. The model is therefore required to predict, from consecutive image frames, the three-dimensional (3D) force vector for each taxel at the current time step." (§2.1)
> (한글 해설 — 출력 차원이 1,140 taxel × 3축 힘이라는 점이 시각(밀집)–촉각(희소) 간 큰 모달리티 간극의 원천임을 규정합니다.)

- **공유 잠재 공간 + 공유 디코더** — 두 스트림은 두정엽(parietal) 유사 영역으로 투영돼 통합 잠재 공간을 거친 뒤, 공유 디코더로 원래 촉각 도메인에 되돌려 매핑됩니다. 인코딩·생성 디코딩은 taxel 의 3D 좌표로 조건화돼 인공 체성감각 지도를 부여합니다.
- **추론 시 비대칭** — 학습 시에는 짝지어진 촉각 특징이 디코더의 사후분포(posterior)를 조건화하지만, 추론 시에는 시각 prior 분포만으로 촉각을 예측합니다(촉각 센서 없이 시각만 사용).

### 학습 목표 / 손실

복합 목적함수는 **11개 손실 항**으로 구성되며, **5개 재구성 항 + 6개 교차모달 정렬 제약**으로 나뉩니다.

> "MTNet is trained with a composite objective consisting of 11 carefully designed loss terms, including five reconstruction terms and six cross-modal alignment constraints." (§2.2)
> (한글 해설 — 손실 설계가 이 논문의 본체입니다. 재구성만으로는 부족하고, 정렬 제약이 핵심 혁신임을 명시합니다.)

- **재구성 5항** — taxel 수준 4항(접촉 영역 가중 MSE·MAE = W-MSE / W-MAE 포함) + 센서 수준 접촉 상태 이진 분류 1항(BCE). 활성 영역에 더 큰 가중치를 부여하는 contact-aware 메커니즘으로, 항상 비접촉인 배경이 아니라 실제 접촉 사건을 우선 최적화합니다.
- **확률 수준 정렬 — KL 4항** —

> "At the probabilistic level (Fig. 2f), MTNet adopts a Conditional Variational Autoencoder (CVAE) [35] formulation and regularizes the latent space with four complementary Kullback-Leibler (KL) divergence terms, including both intra-modal prior-posterior regularization and cross-modal KL losses that anchor the visual prior and posterior to a stabilized moving-average estimate of the tactile posterior." (§2.2)
> (한글 해설 — CVAE 골격에서 모달 내부 prior-posterior 정규화 2항 + 시각 prior·posterior 를 촉각 posterior 의 *이동평균* 추정치에 고정하는 교차모달 KL 2항으로 합 4항입니다. 이동평균 고정이 학습 안정화 장치입니다.)

- **특징 수준 정렬 — force-aware contrastive 1항** —

> "At the feature level (Fig. 2g), a force-aware contrastive objective aligns cross-modal representations by explicitly pulling representations of similar physical interactions together while pushing disparate events apart." (§2.2)
> (한글 해설 — InfoNCE 류 대조 손실로, 물리적으로 유사한 접촉의 시각·촉각 표현을 끌어당겨 의미 수준에서 정렬합니다.)

- **기하 수준 정렬 — relational 1항** —

> "At the geometric level (Fig. 2h), a relational constraint aligns batch-wise geometry by penalizing discrepancies between the pairwise distance matrices of visual and tactile samples, encouraging physically similar touch events to occupy similar positions in the visual latent space." (§2.2)
> (한글 해설 — 배치 내 쌍거리 행렬을 두 모달 사이에서 일치시켜, 시각 잠재 공간의 *기하*가 촉각 구조를 닮도록 강제합니다.)

(KL 4 + contrastive 1 + relational 1 = 정렬 제약 6항. Table S1 은 이 6항을 분포(distribution)·표현(representational)·관계(rational) 3개 계열로 묶어 ablation 합니다.)

### 학습 셋업

- **MTNet 데이터** — 전용 로봇 시각-촉각 데이터셋(VTDataset): 500개 상호작용 에피소드, 26,788개 시각-촉각 짝 프레임.

> "we construct a dedicated robotic visual-tactile dataset (VTDataset) comprising 500 interactive episodes, yielding 26,788 paired visual and tactile frames" (§2.3)
> (한글 해설 — 학습·평가에 쓰인 데이터 규모를 명시합니다.)

- **AMTNet 학습 (교차도메인)** — 사전학습 MTNet 의 시각·촉각 인코더와 디코더를 *동결*하고, 사람 전용 시각 인코더 + 게이팅 네트워크만 학습합니다.

> "During training, the visual encoder, tactile encoder, and decoder inherited from MTNet are frozen to preserve the established alignment between the robotic visual and tactile spaces and avoid catastrophic forgetting." (§2.5)
> (한글 해설 — 동결로 로봇 시각-촉각 정렬을 보존하고 catastrophic forgetting 을 피한다는 전이 전략의 핵심입니다. 사람 도메인은 촉각 정답이 없어 직접 회귀 학습이 불가능하므로, 시각 공간 정렬을 통한 간접 전이를 택합니다.)

- **사람-로봇 짝 데이터** — VTDataset 의 로봇 RGB 를 참조해 손 자세·상호작용을 재현한 사람 손 이미지 100개 시퀀스, 5,499개 프레임 짝.
- **옵티마이저·스케줄·하드웨어** — (원문 Methods 미확보 — 본 추출에 미포함.)

---

## 📊 실험 설정과 결과

평가 지표는 희소·국소 접촉에 맞춘 5종입니다: NRMSE(↓, 힘 크기 오차), S-SimCos / S-CosSim(↑, 공간 분포 일치), S-CCC(↑, 시간적 힘 변화 일관성), T-IoU(↑, 접촉 시점 검출), W-F1(↑, 윈도 단위 접촉 사건 검출).

**Table S1 — 정렬 제약 ablation (5회 평균 ± SD):**

| Model variant | NRMSE (↓) | S-CosSim (↑) | T-IoU (↑) | W-F1 (↑) | S-CCC (↑) |
|---|---|---|---|---|---|
| Unaligned MTNet | 0.0576 ± 0.0023 | 0.1682 ± 0.0059 | 0.0090 ± 0.0067 | 0.0816 ± 0.0003 | 0.1397 ± 0.0001 |
| MTNet w/o distribution alignment | 0.0640 ± <0.0001 | 0.2217 ± 0.0020 | 0.0404 ± 0.0006 | 0.0818 ± <0.0001 | 0.1397 ± <0.0001 |
| MTNet w/o representational alignment | 0.0101 ± <0.0001 | 0.5921 ± 0.0010 | 0.8669 ± 0.0007 | 0.7364 ± 0.0021 | 0.9524 ± 0.0009 |
| MTNet w/o rational alignment | 0.0098 ± <0.0001 | 0.6078 ± 0.0015 | 0.8710 ± 0.0005 | 0.7573 ± 0.0017 | 0.9553 ± 0.0004 |
| Aligned MTNet | 0.0102 ± <0.0001 | 0.6097 ± 0.0010 | 0.8814 ± 0.0005 | 0.7920 ± 0.0019 | 0.9664 ± 0.0007 |

> "the full MTNet consistently outperforms the unconstrained baseline across all metrics." (§2.3)
> (한글 해설 — 정렬 제약 전체를 뺀 Unaligned 대비 Aligned 가 모든 지표에서 우세합니다. 특히 T-IoU 0.0090 → 0.8814, S-CosSim 0.1682 → 0.6097 처럼 접촉 시점·공간 분포 지표의 격차가 큽니다. distribution alignment 를 빼면 오히려 거의 붕괴(T-IoU 0.0404)하는 반면, representational·rational 을 하나씩 빼는 것은 영향이 작아, 분포(KL) 정렬이 가장 load-bearing 함을 시사합니다.)

**매니폴드 분석.** 학습되지 않은 망에서 시각 매니폴드의 silhouette 점수는 촉각보다 약 0.31 낮고, 재구성 손실만으로 학습하면 그 격차가 약 0.66 으로 *더 벌어집니다*. 전체 MTNet 만이 이 붕괴를 극복합니다.

> "It achieves the highest Centered Kernel Alignment (CKA) score of about 0.74, outperforming the untrained and unaligned baselines by 0.22 and 0.55, respectively." (§2.4)
> (한글 해설 — 시각 매니폴드가 촉각 매니폴드에 정렬된 정도(CKA)가 0.74 로, 미학습·미정렬 baseline 을 각각 0.22·0.55 앞섭니다. 재구성만으로는 평균 응답으로 수렴해 사건 구별력이 사라지지만(손실은 정상적으로 감소하므로 최적화 붕괴는 아님), 정렬 제약이 잠재 표현을 접촉 관련 구조에 고정함을 보입니다.)

**교차도메인 전이 (AMTNet).** 게이팅 출력 $`\alpha`$ 분포가 학습 후 두 도메인 양 끝으로 갈라지고, 사람·로봇 시각 표현은 하나의 공유 매니폴드로 모입니다.

> "with the bhattacharyya distance (Db) [37] increasing from 0 to 7.6" (§2.5)
> (한글 해설 — 사람/로봇 입력을 가르는 게이팅 출력의 바타차리야 거리 $`D_b`$ 가 0 → 7.6 으로 늘어, 두 도메인을 깔끔히 식별함을 뜻합니다.)

> "with the CKA similarity between the two feature domains increasing from 0.07 to 0.93" (§2.5)
> (한글 해설 — 사람·로봇 시각 특징 도메인 간 CKA 가 0.07 → 0.93 으로, 초기엔 분리됐던 두 표현이 학습 후 공유 잠재 매니폴드로 수렴함을 보입니다.)

**물리 로봇 거울 촉각.** 임계 힘 기반 반사로 시각 관찰만으로 반응을 유발합니다.

> "we conduct a real-robot experiment in which the system was programmed to generate a physical response whenever the maximum contact force on any robotic finger exceeded a preset threshold of 0.2 N." (§2.6)
> (한글 해설 — 손가락 최대 힘이 0.2 N 을 넘으면 flick 반사를 내도록 한 setup 으로, 사람 손을 카메라 아래에서 만지면(로봇은 비접촉) AMTNet 이 30 Hz 영상에서 촉각을 예측해 대응 손가락의 반사를 촉발합니다. 예측 촉각 궤적이 프레임 차분 모션 곡선과 시간적으로 일치합니다.)

---

## ⚖️ 한계

> 아래 세 항목은 논문 저자가 직접 명시한 한계이고, "(분석자 관찰)" 표시가 붙은 항목만 본 분석에서 덧댄 것입니다.

- **단안 RGB 의 가림(occlusion) 한계** — 접촉은 본질적으로 가림을 유발해, taxel 수준의 미세한 3D 힘 값은 단안 RGB 만으로 완전 복원되지 않습니다. 거친 접촉 위치·힘 크기에는 신뢰할 만하지만 정밀 값은 어렵습니다.
- **교차도메인 전이의 짝 데이터 의존** — AMTNet 은 사람-로봇 손 이미지 짝의 품질에 의존하며, 접촉 자세·운동 속도가 도메인 간 크게 다르면 강건성이 떨어집니다. 소량의 사람 촉각 정답을 앵커로 넣으면 성능을 더 끌어올릴 수 있습니다.
- **행동 표현의 단순성** — 시연된 운동 반응은 의도적으로 단순한 임계 기반 flick 하나에 그쳐, 거울 촉각 경험을 더 풍부한 운동·인지 반응으로 잇지는 못했습니다.
- **(분석자 관찰) 수식·재현 세부 미확보** — 본 추출본에서 손실 수식·옵티마이저·학습 스케줄이 담긴 Methods 가 누락돼, 11개 손실의 정확한 형태·가중치는 본문만으로 검증 불가합니다. 또한 깨진 상호참조("See Sec. ??")가 남아 있습니다.
- **(분석자 관찰) 센서 특수성** — 전자기(electromagnetic) 3축 taxel 손이라는 특정 하드웨어에 강하게 묶여, 다른 촉각 모달리티(vision-based 등)로의 일반화는 미검증입니다.

---

## ♻️ 재현성

- **코드** — 공개. `https://github.com/fun0515/Mirror-Touch-Net` (논문 Abstract·서론 명시).
- **데이터** — VTDataset(500 에피소드·26,788 짝 프레임)과 사람-로봇 Hand 데이터셋(100 시퀀스·5,499 짝)을 자체 구축했다고 기술하나, 공개 여부·라이선스는 본 추출본에 명시 없음.
- **하드웨어** — 4지 다지 손 + 11개 전자기 촉각 센서(1,140 taxel, 1 mm 해상도, 3축 힘), 단안 RGB 카메라(Fig. S1). 상세 BOM·구동기 사양은 미확보.
- **학습 세부** — 옵티마이저·LR·에폭·하드웨어(GPU)·시드 등은 Methods 누락으로 미확보. 5회 평균±SD 보고는 확인.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P2 (구조적 입력-모달리티 결합) — 주 접점.** 본 논문은 시각·촉각 표현을 *flat-concat 이 아니라* 다중 제약으로 정렬한다는 점에서 P2 의 "구조적 결합" 정체성에 정확히 들어맞습니다. 특히 **D11(비주오택타일/proprio-tactile 인코더 후보)** 의 deferred 항목인 *latent tactile prediction* 및 *force-prediction aux* 와 같은 문제 계열입니다.
- **P2 / D10 (hand-level aggregation), D12 (multi-camera pre-fusion)** — "시각·촉각 잠재를 정렬하는" 메커니즘(InfoNCE·rational alignment)은 우리 손-수준 집계·다중 카메라 융합 인코더에 *결합 정렬 손실*을 더하는 후보 설계가 됩니다.
- **크로스폴리네이션 Month D (촉각 센싱 in 신경과학)** — §12 의 Month D("tactile sensing in prosthetics / neuroscience") 회전 주제에 정확히 부합하는 뇌 영감 촉각 논문입니다. 본 논문은 P# 핵심 결정의 *변경* 트리거라기보다 이 크로스폴리네이션 슬롯의 강력한 후보입니다.
- **Identity 긴장/지지** — 우리 Identity 는 촉각을 *1급 구조적 입력*으로 끌어올립니다(P2 "observation elevation"). 본 논문은 촉각을 *시각에서 예측*하는, 추론 시 촉각-부재 전제를 깔아 정반대 방향(센서 없는 손)으로 보일 수 있습니다. 그러나 "촉각을 수동 사후 피드백으로 보지 말고 선제(anticipatory)·정렬된 표현으로 다루자"는 *주장*은 우리 "관찰 격상" 철학과 방향을 같이합니다. 긴장과 지지가 공존하는 셈입니다.
- **무관한 결정 (명시)** — P1(Body/Hand 분리), P3(System0 RL), P4(VLM 사전학습 보존), P5(평가/falsifier)와는 직접 연결이 없습니다. RL·VLA 백본·액션 디코더를 다루지 않으므로 해당 Decision(D1–D7, D13–D26)을 건드리지 않습니다.
- **§10 경쟁자 함의** — 직접적 경쟁자/형제 아키텍처는 아닙니다. Sharpa(우리 하드웨어 후보)는 vision-based Deform Map 인 반면 본 논문은 전자기 taxel 이라 하드웨어 계열도 다릅니다.

---

## ✨ 핀 논문 대비 델타

- **vs. Touch Dreaming ([arXiv:2604.13015](https://arxiv.org/abs/2604.13015), P2/D11 핀 — latent tactile prediction aux)** — Touch Dreaming 이 "잠재 촉각 예측"을 보조 과제로 두는 것과 같은 시각→촉각 예측 계열이되, 본 논문은 (1) 예측을 *명시적 다중 제약 정렬*(분포 KL + InfoNCE + 기하 거리)로 환원하고, (2) t-SNE/CKA/silhouette 로 매니폴드 정렬을 정량 입증하며, (3) **동결 코어 + 게이팅으로 사람 손까지 교차도메인 전이**하는 점이 새롭습니다. 즉 "예측 보조 손실"을 넘어 "왜 정렬이 매핑을 쉽게 하는가"를 매니폴드 기하로 설명합니다.
- **vs. AdapTac ([arXiv:2505.13982](https://arxiv.org/abs/2505.13982), P2/D11 핀 — future-force aux)** — 두 논문은 촉각/힘 예측이라는 목표를 공유하지만, AdapTac 이 미래-힘 예측을 aux 로 두고 촉각 입력 위 force-guided attention 인 데 반해 본 논문은 *촉각 입력 없이 시각만으로* 1,140 taxel 힘을 예측하고, 핵심을 attention 이 아니라 *교차모달 표현 정렬*에 둡니다.
- **vs. ViTacFormer ([arXiv:2506.15953](https://arxiv.org/abs/2506.15953), P2 핀 — cross-attention 비주오택타일)** — ViTacFormer 가 cross-attention 으로 두 모달을 *융합*한다면, 본 논문은 두 모달을 *분리 표현 공간에 두고 정렬 손실로 기하를 맞춥니다*. 융합 vs 정렬이라는 설계 축의 대비가 델타입니다.

---

## ⚙️ 의사결정 함의

- **D11 (visuotactile/proprio-tactile 인코더) — 정렬 보조 손실 후보 추가.** 우리 인코더 학습에 *교차모달 정렬 손실*(시각 prior ↔ 촉각 posterior KL, force-aware InfoNCE, 쌍거리 행렬 일치)을 보조 항으로 거는 설계를 후보로 등재합니다. 구체적으로는 D11 의 "latent tactile prediction (Touch Dreaming) → trigger: inference-time tactile dropout robustness" 트리거가 켜질 때, AMTNet 식 **동결-코어 + 정렬-인코더** 레시피가 *촉각 센서 dropout 시 시각으로 보강*하는 구현 레시피가 됩니다.
- **구체 config 후보** — 인코더 학습 손실에 `align_kl_weight`(시각↔촉각 KL), `align_infonce_weight`(force-aware 대조), `align_relational_weight`(쌍거리 행렬) 3개 가중치 항을 노출하고, Table S1 의 시사(분포 정렬이 가장 load-bearing)에 따라 KL 항을 우선 켭니다.
- **메트릭 후보** — 우리 P2 인코더가 시각·촉각을 *정렬*했는지 진단할 척도로 **CKA(시각 잠재 ↔ 촉각 잠재)** 와 silhouette 점수의 도입을 권장합니다(현재 D26 메트릭에는 없음). 이는 "structured binding 이 실제로 모달리티를 정렬했는가"의 정량 falsifier 후보입니다.
- **주의 — 전제 차이.** 우리 스택은 Sharpa Deform Map 으로 *추론 시에도 촉각을 가짐*. 따라서 본 논문의 "시각→촉각 예측"을 그대로 채택할 이유는 약하고, 가치는 "두 모달을 *정렬*하는 손실/메트릭"에 있습니다(예측이 아니라 정렬의 전이).

---

## ⚠️ 먼저 검증할 실패 모드

- **가장 싼 sanity check** — *두 모달이 모두 train·test 에서 존재할 때*도 정렬 손실이 이득을 주는가. 본 논문의 큰 이득은 *추론 시 촉각 부재*라는 어려운 설정에서 왔습니다. 촉각이 항상 있는 우리 셋업에서는, 작은 ablation(정렬 손실 on/off, 우리 데이터 일부)으로 접촉-정밀 지표(slip count·pose stability) 개선이 유의한지부터 따져 봐야 합니다.
- **센서 모달리티 불일치** — 본 논문은 전자기 3축 taxel(희소·1,140점). 우리는 vision-based Deform Map(이미지형, ~320×240). "희소 taxel ↔ 밀집 영상" 정렬 손실 설계가 "이미지형 촉각 ↔ 영상" 에 그대로 옮겨질지는 아직 불확실합니다. 토큰화 단계(D8 per-finger token)와 호환되는 거리 척도부터 점검해야 합니다.
- **분포 정렬의 취약성** — Table S1 에서 distribution alignment 제거 시 거의 붕괴(T-IoU 0.0404)했습니다. KL 항은 강력하지만 이동평균 추정·하이퍼파라미터에 민감할 수 있습니다. 우리 데이터 규모(VTDataset 26k 짝 대비)에서 안정적으로 수렴하는지를 먼저 확인해야 합니다.
- **교차도메인 짝 데이터 비용** — AMTNet 의 사람-로봇 전이는 *수동으로 자세를 맞춘* 짝 데이터에 의존합니다. 우리가 동등한 짝 데이터를 만들 비용이 크고, 자세·속도 차에 약하다는 저자 한계가 그대로 전이됩니다.

---

## 💡 컨텍스트 제안

- **크로스폴리네이션 후보로 기록** — §12 Month D("tactile sensing in prosthetics / neuroscience") 회전 주제의 강한 후보입니다. 핀 교체까지는 불필요하나, 다음 P2 분기 rebalance 시 D11 deferred(latent tactile prediction) 논의에 Touch Dreaming 과 *나란히* 참조할 만합니다.
- **D11 메모 후보(사람 판단 필요)** — D11 의 deferred 항목에 "교차모달 *정렬* 손실(KL/InfoNCE/relational) 기반 비주오택타일 인코더"를 Touch Dreaming(예측) 과 구분되는 별도 후보로 부기하는 안을 제안합니다. 단, 이는 제안일 뿐이며 `context/MASTER.md` 는 수정하지 않았습니다.
- **그 외** — Tracked Literature 핀 8개 한도(P2) 변경, Decision/deferred 트리거 이동 제안 없음.

> 💡 base 매핑은 `/implement-design analysis/2605.14571/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
