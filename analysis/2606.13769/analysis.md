# Paper Analysis — $`\mu_0`$: A Scalable 3D Interaction-Trace World Model

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | $`\mu_0`$: A Scalable 3D Interaction-Trace World Model |
| 저자 | Seungjae Lee, Yoonkyo Jung, Jusuk Lee, Jonghun Shin, Amir Hossein Shahidzadeh, Yao-Chih Lee, H. Jin Kim, Jia-Bin Huang, Furong Huang (University of Maryland · Seoul National University) |
| 링크 | [arXiv:2606.13769](https://arxiv.org/abs/2606.13769) · [HuggingFace](https://hf.co/papers/2606.13769) · [Website](https://mu0-wm.github.io/) |
| 발행일 / 버전 | 2026-06-15 · v2 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-17 |
| 관련 Pillar | P5, P2, P0 |
| 태그 | flow-matching, egocentric-data, dataset |

---

## 🧭 한 줄 요약 (TL;DR)

픽셀도 액션 라벨도 아닌, 객체·도구·손·접촉부 같은 의미적 상호작용 키포인트의 **미래 3D 궤적(trace)** 을 예측하는 query-conditioned world model $`\mu_{0}`$ — action-free 비디오만으로 사전학습한 뒤 frozen 상태로 어떤 embodiment 의 action expert 와도 결합되어, action 라벨로 학습한 VLA(π0/π0.5)에 필적하는 정책 성능을 낸다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 로봇 학습은 "비디오는 풍부하지만 제어에 직접 쓸 수 있는 action-labeled 데이터는 희소·고비용·하드웨어 종속적"이라는 data paradox 에 묶여 있습니다. 임베디먼트에 독립적이면서 비디오로 스케일되는 supervision 표현이 필요합니다.
- **기존 접근의 한계** — Pixel-space video generation 은 스케일되지만 모델 용량을 dense appearance·배경 복원에 낭비하고 manipulation 에 필요한 metric geometry·contact·occlusion 을 놓칩니다. 반대로 직접 action 예측(VLA)은 embodiment-specific 라벨 희소성에 갇힙니다.
- **본 논문의 가설** — 그 중간 지대인 "의미적 상호작용 점들의 3D trace" 를 예측하면, *무엇이 움직여야 하는가* 를 로봇 종류와 무관하게 compact 하게 기술할 수 있고, 이 표현이 downstream 정책의 강력한 motion prior 가 됩니다.
- **기존 trace 기법의 3대 결함** — (1) tool tip·contact patch 같은 작지만 task-critical 영역을 under-sample, (2) local/2D 이미지 좌표에서 동작해 객체 운동과 카메라 운동을 혼동, (3) 긴 데모에 episode 단위 캡션을 붙여 event-level 의도를 잃음. 가장 가까운 선행 TraceGen 이 세 축 모두에서 제한적입니다.
- **왜 지금 중요한가** — VGGT·TAPIP3D·DINOv2 같은 perception 스택이 성숙해 uncurated 비디오에서 globally aligned 3D trace 를 자동 추출하는 데이터 엔진이 비로소 실현 가능해졌고, 이를 통해 trace 큐레이션을 선행 3D trace 데이터셋 대비 약 $`8\times`$ 로 스케일할 수 있게 되었습니다.

---

## 🧩 핵심 기여

- **TraceExtract** — uncurated 인간/로봇 manipulation 비디오를 *event-captioned 3D trace supervision* 으로 변환하는 스케일러블 데이터 엔진: (1) DINOv2 entity 클러스터 기반 semantic keypoint 선택, (2) globally aligned 3D lifting, (3) motion event 단위 hierarchical 언어 캡셔닝.
- **$`\mu_{0}`$** — VLM backbone + permutation-equivariant Trace Expert + B-spline trace target + semantic flow-matching 으로 이루어진 query-conditioned 3D trace-space world model.
- **Trace-conditioned action adaptation** — 사전학습된 $`\mu_{0}`$ 를 freeze 하고 그 trace-denoising feature 위에 action expert 만 학습 → action-free 비디오 사전학습이 실제 로봇 정책으로 전이됨을 입증.
- **결과** — 2D/3D trace forecasting 에서 trace 예측 모델과 tokenized-VLM 베이스라인을 모두 능가하고, 8개 RoboCasa365 시뮬 + 3개 실로봇 UR3 task 에서 action 라벨 사전학습 VLA(π0 의 120–130%, π0.5 의 70–115% 평균 성공률)에 필적/초과 — action supervision 을 사전학습에 전혀 쓰지 않고도.

---

## 🔑 기술 키워드

- **3D interaction trace** — dense pixel 대신 객체·도구·손·접촉부의 미래 3D 궤적만 예측하는 표현. "그림 전체를 그리지 말고 움직이는 점 몇 개의 경로만 그려라"에 해당하며 embodiment-agnostic 한 motion interface 가 됩니다.
- **World model** — action 이 물리적 변화를 어떻게 유발하는지를 모델링하는 예측기. 여기서는 raw-pixel 생성이 아니라 trace-space 의 forward 예측이 그 역할을 합니다.
- **TraceExtract** — uncurated 비디오 → {observation, trace, language} triplet 자동 추출 파이프라인. world model 의 supervision 공장.
- **Permutation-equivariant Trace Expert** — 임의 개수·임의 순서의 query 키포인트를 받아 순서에 무관하게 처리하는 모듈. "어떤 점을 어떤 순서로 묻든 같은 답"을 보장.
- **B-spline control points** — 미래 궤적을 dense waypoint 대신 소수의 cubic spline 제어점으로 표현. compact·smooth·denoising 용이.
- **Flow matching** — noise → 깨끗한 데이터로 가는 velocity field 를 학습하는 생성 기법. 여기서는 control point 위의 conditional flow.
- **adaLN-Zero** — flow-time 스텝을 각 레이어에 주입하는 zero-init 변조 모듈. 학습 시작 시 항등(identity)에서 출발해 안정적.
- **Semantic rigidity loss** — 같은 DINO 클러스터에 속한 키포인트들의 상대 거리를 시간에 따라 보존하라는 정규화. 합성 환경의 GT 마스크 없이 part-level 강체성을 부여.
- **Partial-denoising feature** — 전체 rollout 대신 flow 의 단일 부분-denoising 스텝에서 뽑은 중간 hidden state 를 motion descriptor 로 사용. 비용 절감 + task-relevant dynamics 보존.
- **Gated cross-attention** — frozen trace feature 를 VLM feature 에 주입하되 learnable scalar gate(0 init)로 약하게 시작해 유익할 때만 강해지도록 한 융합.

---

## 🔬 방법론

### 직관

$`\mu_{0}`$ 의 출발점은 "world model 이 *무엇을* 예측해야 하는가"라는 질문입니다. 픽셀을 통째로 예측하면 배경·질감 복원에 용량을 쓰느라 정작 manipulation 에 필요한 geometry·contact 를 놓치고, action 을 직접 예측하면 로봇별 라벨에 종속됩니다. 저자들은 그 중간, 즉 "작업과 무관하게 *무엇이 움직여야 하는가*"를 객체·도구·손·접촉부 위 소수 점들의 미래 3D 경로(trace)로 답합니다. 같은 컵 운동은 그리퍼든 다지 손이든 동일하게 가이드할 수 있으므로 trace 는 embodiment 에 독립적입니다.

이 표현이 실제로 작동하려면 세 조건이 필요합니다. (1) 점들이 task-relevant entity 위에 놓이도록 **의미적 선택**, (2) 카메라가 움직여도 점의 정체성이 유지되는 **일관된 3D 추적**, (3) 긴 데모가 아니라 reach·grasp·move·release 같은 국소 subgoal 단위로 묶이는 **event-level 언어**. TraceExtract 가 이 세 조건을 자동으로 충족시켜 비디오를 {관측, trace, 캡션} triplet 으로 바꾸는 데이터 엔진입니다.

$`\mu_{0}`$ 본체는 사전학습 VLM(SmolVLM2)을 의미·언어 prior 로 쓰고, 그 위에 motion 전용 stream 인 Trace Expert 를 붙입니다. 미래 궤적은 dense waypoint 대신 B-spline 제어점으로 압축해 부드럽고 denoising 하기 쉽게 만들고, 미래의 다중성(같은 지시에 여러 경로)을 평균내 뭉개지 않도록 deterministic 회귀 대신 flow matching 으로 생성합니다. 여기에 trajectory 가 언제 끝나는지(validity)와 같은 part 의 강체성(rigidity)을 보조 손실로 더합니다.

마지막으로, 사전학습이 끝난 $`\mu_{0}`$ 를 **frozen** 상태로 두고 그 trace-denoising feature 만 읽어 action 을 내는 action expert 를 target 로봇마다 따로 학습합니다. world model 은 한 번 학습해 여러 embodiment 에 재사용되고, action supervision 은 target 인터페이스로만 한정됩니다.

### 아키텍처

전체 파이프라인은 두 단계 — 데이터 엔진(TraceExtract)과 모델($`\mu_{0}`$ + action expert)입니다.

![Figure 1 — videos to reusable action priors](https://arxiv.org/html/2606.13769/x1.png)

> "Figure 1: From videos to reusable action priors. TraceExtract extracts event-captioned 3D interaction traces from heterogeneous videos by selecting entity-centric keypoints, lifting them into globally aligned 3D, and pairing motion events with language. This supervision pretrains $`\mu_{0}`$ as a world model that predicts compact future trajectories for interaction points, instead of dense pixels or robot-specific actions. Once pretrained, the frozen $`\mu_{0}`$ can be reused with any downstream action expert, which consumes trace features to produce executable robot action chunks." (§1)
> (한글 해설 — 비디오 → trace supervision → frozen world model → 임의 action expert 라는 논문의 전체 흐름을 한 장으로 보여 줍니다.)

**TraceExtract (§2)** — 세 단계로 분해됩니다.

![Figure 2 — TraceExtract overview](https://arxiv.org/html/2606.13769/x2.png)

> "Figure 2: Overview of TraceExtract. From an uncurated human or robot manipulation video, TraceExtract selects DINOv2 entity keypoints (Sec. 2.1), tracks and lifts them into globally aligned 3D traces with chunk-wise reconstruction (Sec. 2.2), and segments traces into motion-centric events for hierarchical VLM captioning (Sec. 2.3), producing event-captioned 3D trace supervision for $`\mu_{0}`$." (§2)
> (한글 해설 — keypoint 선택 → 3D 추적/lifting → motion event 캡셔닝의 3 stage 데이터 엔진 구조.)

1. **Semantic Keypoint Sampling (§2.1)** — fixed-grid(TraceGen)는 area-biased 해서 배경이 budget 을 잠식하고 작은 객체·contact patch 를 놓칩니다. 대신 DINOv2 patch feature 를 entity-level 로 클러스터링하고, entity 정체성을 클립 전체에 전파하며, entity 당 고정 keypoint quota 를 두고 high-visibility 프레임에서 spatially diverse 한 점을 farthest-point sampling 으로 고릅니다. movement filter 가 정적/배경 트랙을 표시해 zero-motion bias 를 막습니다.

> "A keypoint is marked moving when $`d_{i}`$ exceeds $`\tau_{m}=40`$ pixels." (§A.2)
> (한글 해설 — 키포인트의 trace diameter $`d_{i}`$ — 가시 프레임 집합 위 최대 쌍별 변위, depth 는 $`\lambda_{z}=0.1`$ 로 가중 — 가 40px 를 넘으면 "움직이는 점"으로 분류. 순간 속도가 아니라 최대 변위를 써서 tracker jitter 에 강건합니다.)

2. **3D Trace Construction (§2.2)** — egocentric 카메라 운동·객체 등장/퇴장·full-video 재구성의 메모리 한계를 global–local 재구성으로 해결합니다. sparse anchor 프레임으로 공통 global 좌표계를 세우고(VGGT 1회 global pass + 단일 공유 $`\mathbf{K}^{\text{global}}`$), dense local chunk 를 그 좌표계로 정렬합니다. chunk 별 SE(3) 정렬은

$$\mathbf{A}^{(c)}=\arg\min_{\mathbf{A}\in\mathrm{SE}(3)}\sum_{t\in\mathcal{S}\cap c}\big\|\mathbf{A}\,\mathbf{E}_{t}^{(c)}-\mathbf{E}_{t}^{\text{sparse}}\big\|^{2}$$

> "Because each chunk aligns directly to the same global anchors rather than to its predecessor, alignment errors are independent and bounded across chunks instead of compounding." (§A.3)
> (한글 해설 — 각 chunk 를 직전 chunk 가 아니라 동일 global anchor 에 직접 정렬하므로 오차가 누적되지 않고 chunk 간 독립·유계로 유지됩니다. 긴 horizon 비디오의 핵심 트릭.)

이후 track 을 per-chunk reference 카메라로 reproject 해 screen-aligned 3D trace $`\mathbf{T}_{\mathrm{ref},n}^{t:t+H}=[x_{n,i},y_{n,i},z_{n,i}]_{i=t}^{t+H}`$ 를 얻고(카메라 운동 제거 + 이미지 정렬 유지), arc-length reparameterization 으로 trace 속도를 정규화해 인간/로봇 데모의 duration 차이를 줄입니다. chunk 간 추적은 TAPIP3D 의 3D world 좌표를 직전 chunk 의 마지막 유효 world 위치를 다음 chunk 의 3D query 로 주어 progressive 하게 잇습니다.

3. **Event-Centric Captioning (§2.3)** — trace 가 캡셔닝 단위를 정의합니다. per-frame acceleration 을 Savitzky–Golay 로 smooth 한 $`\tilde{a}_{t}`$ 의 peak 를 action anchor 로 보고, 최저-가속 valley 에 chunk 경계를 둡니다.

$$b_{i}=\arg\min_{t\in[p_{i},p_{i+1}]}\tilde{a}_{t}$$

각 chunk 의 start/mid/end 프레임(선택적으로 motion mask·episode task 설명)으로 VLM 이 구조화된 캡션을 만들고, text-only LLM 이 sliding window 로 인접 캡션을 병합해 fine-grained event 캡션과 coarse task 요약을 동시에 산출합니다.

**Trace Supervision Interface (§2.4)** — 종합하면 각 비디오가 다음 튜플로 변환됩니다.

$$\mathcal{D}_{\mathrm{TE}}=\left\lbrace\left(I_{t},l_{c},\mathbf{Q}_{t},\mathbf{T}_{\mathrm{ref}}^{t-h:t+H}\right)\right\rbrace$$

여기서 $`I_{t}`$ 는 관측, $`l_{c}`$ 는 event/merged task 캡션, $`\mathbf{Q}_{t}=\{\mathbf{q}_{n}^{t}\}_{n=1}^{N}`$ 는 query keypoint 집합, $`\mathbf{T}_{\mathrm{ref}}^{t-h:t+H}`$ 는 reference 카메라의 과거·미래 3D trace 입니다. $`\mu_{0}`$ 는 이 튜플 위에서 예측 사상을 학습합니다.

$$\mu_{0}:\left(I_{t},l_{c},\mathbf{Q}_{t},\mathbf{T}_{\mathrm{ref}}^{t-h:t}\right)\mapsto\hat{\mathbf{T}}_{\mathrm{ref}}^{t:t+H}$$

**$`\mu_{0}`$ 본체 (§3)** — 세 결합 과제를 세 컴포넌트로 풉니다: (1) semantic–metric fusion, (2) query equivariance, (3) multi-modal dynamics.

![Figure 3 — μ_0 and action-expert interface](https://arxiv.org/html/2606.13769/x3.png)

> "Figure 3: Overview of $`\mu_{0}`$ and its action-expert interface. TraceExtract provides event-captioned 3D traces for semantic query keypoints. The VLM-conditioned trace context (Sec. 3.1) encodes RGB, language, and optional depth; spline query tokens (Sec. 3.2) represent each keypoint as an exchangeable B-spline query grounded by local DINO features; semantic flow matching (Sec. 3.3) denoises control points into smooth future 3D traces; and the action expert (Sec. 3.4) maps frozen trace features to executable robot actions." (§3)
> (한글 해설 — VLM backbone, spline query token, semantic flow matching, action expert 4 블록이 frozen prior → 정책으로 이어지는 구조.)

- **Multi-Modal Conditioning Backbone (§3.1)** — 사전학습 SmolVLM2-2.2B prefix 로 RGB+지시를 인코딩하고, VLM key-value cache 에 cross-attend 하되 별도 motion-specific stream 을 유지하는 Trace Expert 를 붙입니다. "VLM 이 보존하는 semantic memory" 와 "Trace Expert 가 학습하는 motion computation" 을 분리합니다. metric depth 는 VLM 입력 공간 밖이라 별도 trainable patch stem 으로 들어와 deeper SigLIP layer 를 RGB 와 공유 — pretrained RGB 통계를 깨지 않고 geometric cue 를 활용합니다.

> "This separates semantic memory, preserved by the VLM, from motion computation, learned by the trace expert." (§3.1)
> (한글 해설 — frozen VLM 은 의미·언어 prior 를 보존하고 새 motion 계산은 Trace Expert 가 전담하는 이원화가 설계 의도입니다.)

- **Permutation-Equivariant Trace Expert (§3.2)** — 각 keypoint 를 exchangeable query 로 취급, 모든 query 가 같은 처리 stack 을 공유해 keypoint 차원에 대한 permutation equivariance 를 보존합니다. 각 query 의 미래는 current 3D anchor 를 뺀 뒤 cubic B-spline 제어점으로 표현(compactness·smoothness·easier denoising). query token 은 (1) history/future segment embedding, (2) 현재 픽셀 위치의 Fourier embedding, (3) 국소 semantics 의 DINO feature 를 결합합니다.

- **Flow Matching with Semantic Structure (§3.3)** — deterministic 회귀는 여러 미래를 평균내 actionable 하지 않은 trace 를 내므로, control point 위 conditional flow 로 학습합니다. (1) VLM context, (2) per-query token, (3) adaLN-Zero 로 주입된 flow-time 변조 하에 noisy control point → clean control point velocity field 를 예측합니다. 두 구조적 항을 추가합니다 — validity prediction(occlusion/track loss 시 종료 시점)과 semantic rigidity(같은 DINO 클러스터 keypoint 의 국소 geometry 보존).

### 학습 목표 / 손실

flow path 는 표준 Gaussian noise $`\mathbf{\epsilon}\sim\mathcal{N}(\mathbf{0},\mathbf{I})`$ 와 virtual time $`\tau\in[0,1]`$ 의 linear path 입니다.

$$\mathbf{P}^{\tau}=\tau\mathbf{\epsilon}+(1-\tau)\mathbf{P}^{\star}$$

네트워크 $`v_{\theta}`$ 는 noise → clean data 로의 constant-in-time target velocity $`\mathbf{\epsilon}-\mathbf{P}^{\star}`$ 를 예측합니다. 주 손실은 control-point 공간의 masked MSE 입니다.

$$\mathcal{L}_{\text{flow}}=\mathbb{E}_{\tau,\mathbf{\epsilon}}\left[\left\|v_{\theta}(\mathbf{P}^{\tau},\tau,F_{\text{cond}})-(\mathbf{\epsilon}-\mathbf{P}^{\star})\right\|_{2}^{2}\right]$$

> "computed only over valid and present keypoints." (§B.3)
> (한글 해설 — 유효·존재하는 keypoint 위에서만 계산해 occlusion·track loss 가 gradient 를 오염시키지 않게 합니다.)

trace 절단(truncation)을 다루는 validity head 는 per-step validity logit 을 sigmoid cross-entropy 로 학습합니다.

$$\mathcal{L}_{\text{done}}=\frac{\sum_{t=1}^{H}\ell_{\text{BCE}}(\hat{d}_{n,t},y_{n,t})}{N}$$

여기서 $`\hat{d}_{n,t}`$ 는 keypoint $`n`$ 의 future step $`t`$ 예측 validity logit, $`y_{n,t}\in\{0,1\}`$ 는 GT validity. 추론 시 이 head 가 stop index 를 제공해 예측된 종료 이후의 trace 를 freeze 합니다.

rigidity 항은 in-flight 로 재구성한 clean control point $`\hat{\mathbf{P}}_{n}=\mathbf{P}_{n}^{\tau}-\tau v_{\theta}`$ 에 대해, 같은 part 클러스터 내 keypoint 쌍의 거리가 control-point 시퀀스에 걸쳐 불변하도록 강제합니다.

$$\mathcal{L}_{\text{rig}}=\mathbb{E}_{\tau,\mathbf{\epsilon}}\left[\frac{1}{|R|}\sum_{(n,n^{\prime})\in R}\mathrm{Var}_{d}\left(\left\|\hat{\mathbf{P}}_{n,d}-\hat{\mathbf{P}}_{n^{\prime},d}\right\|_{2}^{2}\right)\right]$$

> "Unlike prior work that relies on ground-truth object segmentation masks available only in synthetic environments, we use the DINO cluster identities produced by TraceExtract." (§B.3)
> (한글 해설 — 합성 환경에서만 가능한 GT segmentation 대신 TraceExtract 의 DINO 클러스터 정체성을 part label 로 써서 실세계 비디오에도 rigidity 정규화를 적용합니다.)

전체 목표는 가중합입니다.

$$\mathcal{L}=\mathcal{L}_{\text{flow}}+\lambda_{\text{done}}\mathcal{L}_{\text{done}}+\lambda_{\text{rig}}\mathcal{L}_{\text{rig}}$$

추론은 $`\tau\in[1,0]`$ 위 4-step Euler 적분 후 B-spline basis 로 절대 trace 를 디코딩합니다.

**B-spline target fitting** — 미래를 직접 회귀하지 않고 degree-3 B-spline 의 $`D{=}10`$ 제어점으로 re-parameterize 합니다. anchor-relative·per-axis rescaled future 는

$$\tilde{\mathbf{T}}^{1}_{n,k}=(\mathbf{T}^{1}_{n,k}-\mathbf{c}_{n})/\mathbf{s}_{\Delta}$$

이고($`\mathbf{s}_{\Delta}`$ 는 corpus 위 per-axis 95th-percentile scale), 제어점은 row-weighted ridge least squares 로 적합합니다.

$$\mathbf{P}^{\star}_{n}=\arg\min_{\mathbf{P}\in\mathbb{R}^{D\times 3}}\big\|\mathbf{M}_{n}\odot(\mathbf{B}\mathbf{P}-[\mathbf{0};\tilde{\mathbf{T}}^{1}_{n}])\big\|_{F}^{2}+\lambda_{\text{bsp}}^{2}\big\|\mathbf{\Gamma}\mathbf{P}\big\|_{F}^{2}$$

$`\mathbf{B}`$ 는 고정 cubic B-spline basis(anchor $`t{=}0`$ 에 pin), $`\mathbf{M}_{n}`$ 은 invalid future step 을 0 으로 만드는 row weight, $`\mathbf{\Gamma}`$ 는 인접 제어점의 1차 연산자, $`\lambda_{\text{bsp}}{=}0.2`$ 는 제어점 간격을 평활화하고, post-fit clip $`|\mathbf{P}^{\star}|\leq 1.5`$ 가 target box 를 제한합니다. rollout 은 단일 행렬곱 $`\hat{\mathbf{T}}^{1}=\mathbf{B}\hat{\mathbf{P}}`$ 로 디코딩합니다.

### 학습 셋업

- **Backbone** — SmolVLM2-2.2B prefix 를 첫 $`L_{\text{vlm}}{=}20`$ text-decoder layer 로 truncate. Trace Expert 도 20 layer, hidden width 는 VLM 의 $`0.5\times`$. SmolVLA 방식으로 2 layer 마다 VLM KV cache cross-attention 과 self-attention 을 interleave.
- **입력** — RGB $`I_{\text{rgb}}`$, 선택적 metric depth $`I_{\text{dep}}`$(Turbo colormap 후 별도 patch stem), 지시 $`l`$; 두 이미지 모달리티 모두 $`512\times 512`$ resize. RGB 는 ColorJitter $`s{=}0.3`$, depth 는 meter 도메인에서 $`\sigma_{d}{=}0.01`$ m Gaussian noise.
- **최적화** — AdamW, base lr $`10^{-4}`$, weight decay $`10^{-10}`$, effective batch size 24, sample 당 $`N`$ 은 $`[1,256]`$ 에서 uniform. VLM 및 RGB 용 SigLIP tower 는 frozen; action expert·trace projection·embedding table·depth-only stem·adaLN-Zero head 는 random init(adaLN-Zero 와 uv-MLP 출력 Linear 은 zero-init 으로 step-zero identity 시작).
- **Trace target** — history $`h{=}8`$, future horizon $`H{=}32`$, 제어점 $`D{=}10`$. keypoint 는 $`H`$ future step 중 최소 $`D`$ 개가 valid 일 때만 flow loss 에 참여.
- **Robustness 학습 전략 (§C.1)** — two-level history dropout(전체 동시 drop 확률 0.2, keypoint별 독립 drop 0.3), metric depth 는 확률 0.7 로 생략(static RGB fallback 유도). VLM backbone 은 generalist 표현 보존 위해 frozen.

**Trace-conditioned Action Expert (§3.4 / §B.4)** — frozen $`\mu_{0}`$(VLM backbone + Trace Expert) 위에 action expert 만 학습합니다. 정책은 full rollout 대신 단일 partial-denoising step 의 중간 hidden state $`\mathbf{z}_{\text{trace}}`$ 를 motion descriptor 로 읽습니다(pure-noise control point 에서 4-step Euler 의 1 step). 이를 gated cross-attention 으로 last-layer VLM feature 에 융합합니다.

$$\mathbf{z}_{\text{guided}}=\mathbf{z}+\sigma(g)\cdot\mathrm{CA}\!\left(Q=\mathrm{LN}(\mathbf{z}),\;K=V=\tilde{\mathbf{h}}_{\text{trace}}\right)$$

$`g`$ 는 head·위치 공유 learnable scalar gate 로 0 에서 시작($`\sigma(g)`$ 로 $`(0,1)`$ bound) — weak motion-injection 으로 출발해 유익할 때만 강해집니다. action expert 는 π0.5 의 self-attention 구조를 채택, gripper-camera(DINOv2)·proprioception(MLP)·언어를 추가 입력으로 받아 flow matching 으로 연속 action chunk 를 생성합니다.

$$\mathcal{L}_{\text{action}}=\mathbb{E}_{\tau,\mathbf{a},\mathbf{\epsilon}_{a}}\left\|v_{\phi}\!\left(\mathbf{a}^{\tau},\tau,\mathbf{z}_{\text{guided}},\mathbf{c}\right)-(\mathbf{a}-\mathbf{\epsilon}_{a})\right\|_{2}^{2}$$

---

## 📊 실험 설정과 결과

### Trace 예측 품질 (§4.1)

moving point 위에서만 ADE/FDE/DTW 를 측정(top-1·top-5, S 샘플 중 최소). 모든 baseline 은 동일 image+text 입력(‡ 는 depth 필요).

| Method | 분류 | top5-ADE (T=8/16/32) ↓ | top5-DTW (T=8/16/32) ↓ | Inf. Time ↓ |
|---|---|---|---|---|
| Gemini-3.1-pro | 2D | 0.161 / 0.232 / 0.253 | 0.152 / 0.208 / 0.224 | 78s † |
| GPT-5.5 | 2D | 0.178 / 0.249 / 0.272 | 0.173 / 0.238 / 0.259 | 38s † |
| Track2Act | 2D | 0.190 / 0.262 / 0.293 | 0.181 / 0.245 / 0.270 | 0.85s |
| Hamster | 2D | 0.178 / 0.239 / 0.256 | 0.170 / 0.220 / 0.233 | 14.4s |
| **$`\mu_{0}`$ (Ours)** | 2D | **0.124 / 0.188 / 0.227** | **0.114 / 0.171 / 0.211** | **0.29s** |
| 3DFlowAction | 3D | 0.531 / 0.605 / 0.630 | 0.529 / 0.600 / 0.623 | 3.38s |
| Dream2Flow ‡ | 3D | 0.201 / 0.286 / 0.336 | 0.198 / 0.281 / 0.329 | 106.8s |
| TraceGen ‡ | 3D | 0.208 / 0.276 / 0.325 | 0.204 / 0.262 / 0.299 | 1.20s |
| **$`\mu_{0}`$ (Ours)** | 3D | **0.132 / 0.199 / 0.239** | **0.127 / 0.187 / 0.223** | **0.29s** |

> "In 3D, $`\mu_{0}`$ obtains the best result on every reported ADE, FDE, and DTW metric across all horizons." (§4.1, Table 1)
> (한글 해설 — 3D 에서는 모든 horizon 의 ADE/FDE/DTW 를 전부 석권. 2D 에서도 Top-5 ADE/FDE/DTW 를 모두 최우수로 가져갑니다 — 즉 다중 샘플 중 goal-directed 미래의 정확도가 강함.)

> "its 0.29s prediction latency is 2.9$`\times`$ faster than the next-fastest reported 2D baseline (Track2Act, 0.85s)." (§4.1)
> (한글 해설 — 4-step flow + 단일 행렬곱 디코딩 덕에 0.29s 로 가장 빠릅니다. API-기반 VLM(38–78s)·확산 비디오(Dream2Flow 106.8s) 대비 수십~수백 배.)

### 시뮬 action 생성 — RoboCasa365 (§4.2)

8개 대표 task, 성공률(%). 모든 사전학습 방법은 action expert 만 fully finetune.

| Task | Diffusion Policy | $`\pi_{0}`$ | $`\pi_{0.5}`$ | TraceGen+AE | **Ours ($`\mu_{0}`$+AE)** |
|---|---|---|---|---|---|
| CloseFridge | 34 | 44 | 34 | 38 | **54** |
| OpenFridge | 28 | 12 | 26 | 36 | 18 |
| CoffeeServeMug | 28 | 34 | 48 | 42 | 36 |
| PickPlaceFridgeShelfToDrawer | 28 | 30 | 66 | 30 | 40 |
| TurnOnMicrowave | 0 | 2 | 12 | 0 | 4 |
| SlideToasterOvenRack | 48 | 46 | 76 | 28 | 56 |
| PickPlaceCounterToCabinet | 6 | 18 | 54 | 0 | 12 |
| TurnOnToasterOven | 10 | 16 | 20 | 10 | 22 |
| **평균 성공률 (%)** | 22.75 | 25.25 | **42** | 23 | 30.25 |

> "$`\mu_{0}`$ + action expert achieves a 30.25% average success rate, outperforming $`\pi_{0}`$ by 5.0 points, despite relying solely on video-only pretraining." (§4.2, Table 2)
> (한글 해설 — action 라벨 없이 video-only 로 π0 를 평균 5.0점 능가. 단 π0.5(42%)는 더 강하나, 이는 대규모 action-labeled 사전학습이라 data-matched 비교가 아님을 저자가 명시.)

> "Compared with the previous video-only trace baseline (TraceGen), $`\mu_{0}`$ improves average success by 7.25 points." (§4.2)
> (한글 해설 — 동일 video-only 조건의 TraceGen(23%) 대비 7.25점 향상 — 더 강한 3D trace 예측의 이득으로 해석.)

### 실로봇 — UR3 (§4.2)

UR3 + 2-finger gripper, 3 task(Pick into Sink, Pour Almonds, Unfold Towel; 데모 90/80/50, 각 20 rollout 평가).

> "$`\mu_{0}`$ + action expert achieves the highest average success rate of 91.7%, outperforming all baselines across the three real-world tasks on average." (§4.2)
> (한글 해설 — 실로봇 평균 91.7% 로 최고. VLM+action expert(trace expert 제거, 동일 구조) 대비 18.4%p, π0/π0.5 대비 각 20.0/11.7%p, TraceGen 대비 10.0%p 우위 — frozen trace feature 가 generic VLM 표현 이상의 motion guidance 를 준다는 증거.)

### Ablation (§E.1, Table 6) 과 Scaling (§E.2)

| 변형 | top5-DTW (T=8/16/32) ↓ | 무엇을 분리하나 |
|---|---|---|
| Full $`\mu_{0}`$ | 0.127 / 0.187 / 0.223 | (기준) |
| w/o B-spline (raw trace) | 0.156 / 0.222 / 0.258 | spline 파라미터화 제거 → 가장 큰 악화. compact·smooth target 의 기여가 최대. |
| w/o DINOv2 features | 0.139 / 0.193 / 0.230 | per-keypoint part semantics 제거 → 일관 악화. |
| w/o Rigidity Loss | 0.138 / 0.193 / 0.227 | intra-part 강체성 정규화 제거 → 소폭 악화. |
| w/ Depth & Trace history | 0.107 / 0.160 / 0.203 | 두 모달리티 모두 사용 시 최상 — depth·history 가 정보를 더함. |
| w/o Depth | 0.112 / 0.168 / 0.207 | depth 제거 영향(history 유지). |
| w/o Trace history | 0.126 / 0.183 / 0.224 | history 제거 영향(depth 유지). |
| w/o Depth & Trace history | 0.127 / 0.187 / 0.223 | static RGB 단독 — 그래도 baseline 들보다 우수. |

- **Model scaling (100% 데이터)** — 342M → 568M → 2.59B 로 갈수록 top5-DTW 가 0.143/0.205/0.240 → 0.136/0.191/0.227 → 0.127/0.187/0.223 로 단조 개선. 현 규모에서 여전히 capacity-limited.
- **Data scaling (2.59B)** — 5% → 100% 데이터로 0.134/0.200/0.235 → 0.127/0.187/0.223, 특히 long horizon 에서 이득이 일관적.
- **Action-head scaling (Table 8)** — 200M head: w/o Trace 10.675% → $`\mu_{0}`$+AE 25.625%; 400M head: 28.25% → 30.25%. action head 가 작을수록 trace feature 의 이득이 큼 — 제한된 정책 용량이 trace-space motion 구조의 도움을 가장 크게 받음.

---

## ⚖️ 한계

- **Perception 스택 오류 상속** — 저자 명시: semantic clustering·3D reconstruction·tracking·captioning 의 실패가 noisy supervision 으로 직결됩니다. world model 이 아무리 좋아도 TraceExtract 의 VGGT/TAPIP3D/DINOv2 가 틀린 곳에서는 잘못된 trace 를 학습하며, 이 오류는 라벨 노이즈로 silently 전파됩니다.
- **힘·촉각·접촉 모드 미모델링** — 저자 명시: trace 는 geometry·motion 은 잡지만 force·tactile feedback·contact mode 를 명시적으로 모델링하지 않습니다. fine manipulation(미끄러짐 억제, grasp 유지)처럼 접촉 동역학이 지배하는 영역에서는 "어디가 움직이는가"만으로 충분하지 않을 수 있습니다.
- **제한된 embodiment·task 범위** — 저자 명시: action expert 평가가 tabletop manipulation·제한된 embodiment(2-finger gripper)에 한정됩니다. mobile manipulator·dexterous hand·long-horizon 으로의 확장은 future work — 즉 다지 손에서의 검증이 전무합니다.
- **π0.5 미달(추론된 갭)** — 시뮬 평균에서 π0.5(42%)에 30.25% 로 뒤집니다. 저자는 "data-matched 가 아니다"라고 방어하지만, 이는 곧 *충분한 action-labeled 데이터가 있을 때는 직접 VLA 가 여전히 우월*함을 뜻합니다. trace prior 의 우위는 "데이터가 적을 때"에 국한될 수 있습니다(action-head scaling 결과가 이를 지지).
- **3D 라벨 품질의 metric 의존성(추론된 갭)** — globally aligned 3D 가 단일 $`\mathbf{K}^{\text{global}}`$ ·sparse anchor 정렬에 의존합니다. 객체가 빠르게 등장/퇴장하거나 텍스처가 빈약한 장면에서는 VGGT pose·TAPIP3D 추적이 흔들려 trace 의 metric 정합이 무너질 위험이 있고, 이는 z(depth) 축에서 가장 취약합니다.
- **Task 다양성 대비 평가 task 수(추론된 갭)** — 시뮬은 8 task, 실로봇은 3 task 로 표본이 작고 task 간 분산이 큽니다(예: TurnOnMicrowave 4%, OpenFridge 18%). 평균 우위가 task 조합에 민감할 수 있습니다.

---

## ♻️ 재현성

- **코드/데이터** — 공식 코드 공개 여부는 본문에서 확인되지 않습니다(Project page [mu0-wm.github.io](https://mu0-wm.github.io/), HF [papers/2606.13769](https://hf.co/papers/2606.13769) 존재). 라이선스 CC BY 4.0. TraceExtract 학습 corpus 의 구체적 데이터셋 구성은 추출된 본문에 명시되어 있지 않음(heterogeneous human/robot manipulation 비디오라고만 기술).
- **하드웨어/평가** — 추론 latency 는 single A6000 GPU 기준. 실로봇은 UR3 + 2-finger gripper, 3 task(데모 90/80/50, 각 20 rollout). 시뮬은 RoboCasa365 8 task.
- **하이퍼파라미터** — backbone(SmolVLM2-2.2B, 20 layer truncate), Trace Expert(20 layer, 0.5× width), AdamW lr 1e-4 / wd 1e-10, batch 24, N∈[1,256], h=8/H=32/D=10, λ_bsp=0.2, τ_m=40px, 4-step Euler 등 핵심 값이 Appendix B/C 에 명시되어 재현 가능 수준. RoboCasa365·실로봇 task-specific 하이퍼는 Table 4/5 에 정리(본문 표 수치 일부는 추출 범위 밖).

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P5(World Model) — 정면 핵심.** $`\mu_{0}`$ 는 P5 의 정의("action 이 물리 변화를 어떻게 유발하는지 예측하는 forward 모델")에 정확히 부합하며, 특히 **D30(prediction space)** 의 v1 선택인 *latent / 3D-flow 예측* 의 강력한 실증입니다 — raw-pixel 생성을 버리고 contact-relevant 한 3D trace 를 예측합니다. **D28(world-model role)** 측면에서는 "frozen 재사용 motion prior + future-prediction" 으로, P5 v1 의 "dynamics prior + future-prediction auxiliary" 와 결이 같되 *co-trained* 가 아니라 *완전 분리·frozen* 이라는 변종입니다.
- **D29(integration architecture)** — P5 v1 은 "shared backbone 위 auxiliary head" 를 기본, "decoupled two-stage(VLA-JEPA)" 를 변종으로 둡니다. $`\mu_{0}`$ 는 **frozen WM → 별도 action expert** 의 전형적 two-stage 로, VLA-JEPA 식 decoupled 경로의 또 다른 강한 사례입니다.
- **D31(action conditioning) — 긴장.** P5 v1 은 "action-conditioned(per-frame action) 예측" 을 채택하고 §4 anti-topic 에서 *action-free next-frame 예측* 을 배제합니다. 그런데 $`\mu_{0}`$ 는 **action-free 사전학습**입니다 — 단, "action-free video generation with no robot transfer" 라는 anti-topic 의 핵심 배제 사유(로봇 전이 부재)에는 해당하지 않습니다. trace 가 *명시적 action 대리(proxy)* 로 작동하고 downstream 로봇 전이를 입증하므로, anti-topic 의 정신은 벗어나지 않으나 D31 의 문자적 "action-conditioned" 와는 충돌합니다.
- **D32(egocentric hand-object) — 부분 지지.** TraceExtract 가 egocentric 인간 비디오를 다루고 손·접촉부를 trace 대상으로 삼아 hand-object 상호작용을 직접 겨냥합니다. 다만 평가는 tabletop gripper 로, dexterous hand 검증은 없습니다.
- **P2(Structured Multimodal Observation Fusion) — 강한 간접.** global–local VGGT 3D 재구성·단일 $`\mathbf{K}^{\text{global}}`$ 로 카메라 운동을 제거한 reference-frame 3D trace 는 **D8(multi-camera spatial-geometric grounding)** 의 정신(flat concat 대신 3D-consistent 표현)과, depth pathway·DINO part feature 는 **D9/D11(action-aware encoder·per-part token)** 과 맞닿습니다.
- **P0(VLA Datasets & Benchmarks) — 간접.** TraceExtract 는 본질적으로 **D24(priority data axis)** 의 egocentric 우선·데이터 엔진 사고와 정렬되며, "uncurated 비디오 → supervision triplet" 자동화는 P0 의 데이터 front-end 철학을 구현합니다.
- **Identity 지지/긴장** — Identity 의 "raw-pixel 위 latent/3D-flow 예측" 지향과 강하게 지지 관계. 다만 Identity 의 hand-centric **dexterity**(per-finger contact, System0 안정화) 관점에서 보면 $`\mu_{0}`$ 는 force/tactile/contact-mode 를 모델링하지 않아 "접촉 동역학" 핵심을 비워 둡니다 — world model 을 *손 위* 로 끌어오려면 이 갭을 메워야 합니다.
- **경쟁자 함의** — P5 §5 핀 중 VLA-JEPA(two-stage frozen prior)·DexWM(hand-object 3D keypoint)·TraceGen(직접 비교 대상, off-pin)과 동일 설계 공간에서 경쟁합니다.

---

## ✨ 핀 논문 대비 델타

- **vs. VLA-JEPA (P5 §5 핀, arXiv:2602.10098)** — 둘 다 "world model 을 frozen prior 로 두고 action head 만 학습하는 two-stage" 입니다. 차이는 **예측 공간**: VLA-JEPA 는 leakage-free *latent* state 예측인 반면 $`\mu_{0}`$ 는 *명시적 3D trace*(객체·손·접촉부의 metric 궤적). 명시 trace 는 해석 가능하고 part-rigidity·validity 같은 구조적 제약을 직접 걸 수 있는 대신, latent 보다 perception 스택 오류에 더 노출됩니다.
- **vs. DexWM (P5 §5 *Top* 핀, arXiv:2512.13644)** — DexWM 도 인간 비디오에서 hand-object world model 을 학습하지만 finger-keypoint·hand-consistency 예측으로 *손* 자체에 집중합니다. $`\mu_{0}`$ 는 손을 포함하되 객체·도구·접촉부까지 entity-agnostic 하게 다루고, *query-conditioned*(임의 keypoint 집합) + *permutation-equivariant* 라는 인터페이스 일반성과 cross-embodiment action 전이까지 확장한 점이 새롭습니다. 반대로 DexWM 의 per-finger·dexterous 초점은 $`\mu_{0}`$ 가 비워 둔 부분입니다.
- **vs. TraceGen (직접 선행, off-pin)** — $`\mu_{0}`$ 의 가장 직접적 델타. TraceGen 의 fixed-grid·episode-level 캡션·inference-time depth 의존 3대 한계를, (1) semantic keypoint 선택, (2) global-frame 3D 추적, (3) event-level 캡션, (4) depth-optional(0.7 dropout)로 정면 교체하고 trace 큐레이션을 약 $`8\times`$ 스케일. 2D/3D 모든 지표에서 TraceGen 을 능가.
- **vs. AHEAD·LOME·Being-H0.7 (P5 §5 핀)** — 이들은 latent 예측을 *VLA 와 co-train* 하는 경향(auxiliary head). $`\mu_{0}`$ 의 차별점은 *완전 frozen·재사용* — 한 번 학습한 world model 을 여러 embodiment 의 action expert 가 plug-in 하는 모듈성으로, "재사용성" 을 최전면에 둔 점입니다.

---

## ⚙️ 의사결정 함의

- **D30(prediction space)을 "3D trace" 로 구체화하는 후보.** 우리 v1 의 "latent / 3D-flow" 추상 선택을 *query-conditioned 3D interaction trace* 라는 구체 인스턴스로 내릴 수 있습니다. 구현 키: `trace_target = bspline(D=10, degree=3)`, `H=32`, `h=8`, 손실 `L = L_flow + λ_done·L_done + λ_rig·L_rig`(논문값 λ_bsp=0.2, 4-step Euler).
- **D29(integration)에서 frozen-prior + action expert 분리를 채택할 근거.** action expert 만 학습하면 backbone 재학습 없이 embodiment 전환 가능 — 우리의 Body/Hand expert(P1)를 trace prior 위에 얹는 구조와 자연스럽게 결합됩니다. 융합은 gate 0-init `z_guided = z + σ(g)·CA(...)` 의 약-주입 방식 채택을 권장(prior preservation 친화, P4 와 정합).
- **D31 재검토 트리거.** "action-conditioned" 를 엄격히 고수할지, $`\mu_{0}`$ 식 *action-free trace + 별도 action expert* 를 D31 의 허용 변종으로 받아들일지 결정해야 합니다. trace 가 action proxy 로 충분하다면 action 라벨 의존을 낮추는 P4 data-efficiency 목표와 합치됩니다.
- **데이터 엔진 도입 검토(P0).** TraceExtract 의 (DINOv2 entity 클러스터 → VGGT global-local 3D → TAPIP3D progressive 추적 → event 캡션) 파이프라인을 우리 in-house egocentric 수집(P0/P4)의 자동 라벨러로 채택할지 — 특히 단일 $`\mathbf{K}^{\text{global}}`$ + sparse-anchor SE(3) 정렬은 long-horizon ego 비디오에 직접 이식 가능한 레시피.
- **메트릭 채택.** trace 예측 품질을 moving-point 한정 top-5 ADE/FDE/DTW(+ Fréchet)로 측정하는 프로토콜을 world-model 평가 표준 후보로.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 체크) 우리 손-중심 task 에 trace 가 충분한가** — $`\mu_{0}`$ 는 force/tactile/contact-mode 를 모델링하지 않습니다. in-hand reorientation(Phase 1 cube rotation)처럼 접촉 동역학이 지배하는 task 에서 "객체 점들의 3D 궤적" 만으로 정책이 충분한지부터 적은 데모로 빠르게 확인 — 부족하면 trace 를 P3 System0(촉각 RL)과 합쳐야 합니다.
- **Perception 스택 전이성** — TraceExtract 는 VGGT·TAPIP3D·DINOv2 에 의존합니다. 우리 Sharpa/xhand 셋업의 다지 손·근접 시점·자기-가림(self-occlusion)이 심한 egocentric 영상에서 entity 클러스터링과 3D 추적이 무너지지 않는지 — 한 task 클립으로 trace 추출 품질을 육안 검수하는 것이 가장 싼 sanity check.
- **dexterous hand 의 keypoint under-sampling** — 손가락 끝·접촉 패치는 작아서 fixed budget $`N`$ 의 entity quota 가 finger tip 을 충분히 잡지 못할 수 있습니다. per-finger token(P2 D11) 수준의 attribution 이 보존되는지 확인 필요.
- **z(depth) 축 신뢰도** — metric depth 가 0.7 확률로 dropout 되도록 학습됐다는 것은 곧 depth 신호가 약하거나 noisy 함을 시사합니다. 우리 접촉-임계 task 에서 깊이 정확도가 grasp 성공을 좌우한다면, depth-optional 설계가 오히려 약점이 될 수 있어 depth 품질을 별도 검증.
- **데이터 매칭 시 우위 소멸** — action-head scaling 결과는 trace prior 의 이득이 *정책 용량/데이터가 작을 때* 가장 크다는 점을 보여 줍니다. 우리가 충분한 action-labeled 데모를 모을 수 있는 task 에서는 π0.5 식 직접 VLA 가 더 강할 수 있으므로, "trace prior 가 정말 이득인가" 를 data-matched ablation 으로 확인.
- **frozen WM 의 분포 이동** — $`\mu_{0}`$ 가 본 적 없는 객체·접촉·조명에서 trace 가 평균적 안전 궤적으로 수렴(mode collapse)하면 downstream action 도 보수화됩니다. OOD 객체 한두 개로 trace 다중성(top-5 diversity)이 유지되는지 점검.

---

## 💡 컨텍스트 제안

- **P5 §5 핀 교체 후보.** $`\mu_{0}`$ 는 D29(decoupled two-stage)·D30(3D-flow)·D32(egocentric hand-object)를 한 논문에서 실증하고 TraceGen 을 직접 대체합니다. P5 §5 가 8개 hard cap 임을 감안하면, 비교적 약한 핀(예: World Guidance) 대신 $`\mu_{0}`$ 를 *3D-trace world model* 대표로 승격하는 것을 제안합니다(최종 판단은 사람).
- **D31 문구 정련 제안.** 현재 D31 v1 의 "action-conditioned" 와 §4 anti-topic("action-free video generation") 사이에 $`\mu_{0}`$ 같은 *action-free trace 사전학습 + 로봇 전이 입증* 케이스가 회색지대로 남습니다. "action-free 라도 explicit motion(trace/flow) 예측 + downstream 로봇 전이가 있으면 허용" 식으로 D31/anti-topic 경계를 명문화할지 검토 제안.
- **P0 데이터 엔진 항목 신설 검토.** TraceExtract 를 in-house ego 수집의 자동 3D-trace 라벨러로 평가하는 항목을 P0(D24/D26 인접)에 둘지 — context 파일은 수정하지 않고 제안만 둡니다.
- **카탈로그.** $`\mu_{0}`$ 는 WAM(world-action model) 계열 카탈로그(`catalogs/models.md` 🌐 WAM) 등재 가치가 있으나 현재 WAM 하위에 적합한 `### ` 계보 subsection 이 없어(Donk 뿐) 라우팅 토큰은 보류합니다 — 사람이 WAM `### Standalone` 을 추가하면 등재 권장.

> 💡 base 매핑은 `/implement-design analysis/2606.13769/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
