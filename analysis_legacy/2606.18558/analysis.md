# Paper Analysis — MolmoMotion: Forecasting Point Trajectories in 3D with Language Instruction

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | MolmoMotion: Forecasting Point Trajectories in 3D with Language Instruction |
| 저자 | Jianing Zhang, Chenhao Zheng, Yajun Yang, Max Argus, Rustin Soraki, Winson Han, Taira Anderson, Chun-Liang Li, Shuo Liu, Jiafei Duan, Zhongzheng Ren, Jieyu Zhang, Ranjay Krishna |
| 링크 | [arXiv:2606.18558](https://arxiv.org/abs/2606.18558) · [GitHub](https://github.com/allenai/molmo-motion) |
| 발행일 / 버전 | 2026-06-17 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-30 |
| 관련 Pillar | P5, P0, P4 |
| 태그 | egocentric-data, flow-matching, dataset |

---

## 🧭 한 줄 요약 (TL;DR)

MolmoMotion 은 짧은 RGB 관측 이력 · 객체 위의 3D query point · 행동을 묘사한 언어 명령을 입력받아, 각 점의 **미래 3D 궤적을 metric world frame 에서 예측**하는 goal-conditioned 모션 예측 모델입니다. 1.16M 개 인터넷 영상에서 자동 주석한 대규모 코퍼스(MolmoMotion-1M)와 벤치마크(PointMotionBench)로 학습·평가하며, 이렇게 학습된 **3D 모션 prior 가 backbone 초기화만으로 로봇 매니퓰레이션의 샘플 효율·일반화를 끌어올린다**는 것을 보입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 일반 목적 모션 예측(motion forecasting)의 **표현(representation)** 선택. 에이전트가 행동을 계획하고 물리 상호작용을 추론하려면 "객체가 앞으로 어떻게 움직일지"를 예측해야 하는데, 그 예측 타깃을 무엇으로 둘지가 핵심입니다.
- **기존 접근의 한계** — 픽셀(영상 생성)은 풍부하지만 비싸고 downstream 에서 직접 쓰기 어렵고, parametric 3D pose 는 사람/손/강체 등 **카테고리 템플릿에 묶이며**, 2D point track 은 카테고리 무관이지만 **객체 운동과 카메라 ego-motion 이 얽혀** 도메인 전이가 어렵습니다.
- **본 논문의 가설** — **world coordinate 의 객체 부착(object-attached) 3D 점**이 class-agnostic · view-stable · compact 하면서 downstream 에 바로 쓸 수 있는 범용 모션 표현이라는 것. 언어 명령은 가능한 미래들 사이의 모호성을 줄이는 조건으로 작동합니다.
- **왜 지금 중요한가** — 3D point tracking(AllTracker, ViPE 등)의 발전으로 평범한 RGB 영상에서 metric 3D track 을 자동 추출하는 것이 가능해졌고, 이를 인터넷-스케일로 적용하면 3D 모션 supervision 데이터의 병목을 풀 수 있습니다.

---

## 🧩 핵심 기여

- **Task 정식화** — goal-conditioned 3D point motion forecasting: 시각 이력 + 객체 위 3D query points + 언어 목표 → 각 점의 미래 3D 궤적(world frame) 예측을 형식화.
- **MolmoMotion-1M 데이터셋** — 1.16M 개 비제약(unconstrained) 영상에서 자동 주석한 **action-described · object-grounded 3D point trajectory** 코퍼스. 가장 큰 규모라고 주장.
- **PointMotionBench 벤치마크** — 111개 객체 카테고리 · 61개 모션 타입을 아우르는 human-verified 3D 모션 예측 벤치마크(742 clip; ground-truth 3D capture + 사람 검증 track).
- **MolmoMotion 모델** — Molmo2 VLM backbone 위에 **autoregressive 좌표 예측(AR)** 과 **flow-matching 궤적 생성(FM)** 두 변종을 제안. PointMotionBench 에서 기존 모션 예측 baseline 을 큰 차이로 상회.
- **Downstream 전이 검증** — 학습된 3D 모션 prior 가 (1) 로봇 매니퓰레이션(MolmoSpaces pick-and-place, DROID)의 학습 효율·일반화 개선, (2) 영상 생성의 모션 가이드로 전이됨을 입증.

---

## 🔑 기술 키워드

- **Goal-conditioned 3D point motion forecasting** — "객체 위 점들이 앞으로 어디로 갈지"를 언어 목표에 맞춰 metric 3D 로 예측하는 과제. 본 논문의 정식화 대상.
- **Object-attached 3D points (world frame)** — 객체 표면에 붙은 소수의 점을 world 좌표로 추적하는 표현. 카테고리 템플릿 없이 강체·관절체·변형체 모션을 동시에 기술.
- **Anchor-relative coordinates** — 모든 좌표를 첫 query point $`\mathbf{p}_{\mathrm{anc}}`$ 기준 상대 델타 $`\boldsymbol{\delta}_{t}^{n}`$ 로 표현. 전역 위치 오프셋을 제거해 학습을 쉽게 만드는 좌표계(ablation 최대 기여 요인).
- **Autoregressive coordinate decoding** — 좌표를 millimeter 로 양자화한 **텍스트 토큰**으로 직렬화해 next-token 으로 생성. 이전 좌표에 조건화되어 시간적으로 매끄러운 rollout 유도.
- **Flow-matching trajectory generation** — 가우시안 노이즈에서 clean 궤적으로의 속도장(velocity field)을 학습하는 연속 좌표 생성. 미래 불확실성(다봉 분포)을 포착하고 추론이 빠름.
- **Molmo2 backbone** — SigLIP2 ViT + Qwen3-4B LM 기반 VLM. 강한 객체 grounding 능력을 입력 인코딩에 활용.
- **DiT trajectory expert** — FM 변종의 디코더. LM 층마다 하나씩 36개 블록, 각 블록이 trajectory 토큰에 self-attention + LM hidden 에 cross-attention.
- **2D query-point feature token** — anchor 프레임 feature map 에서 query 위치를 bilinear sampling 한 점-토큰. 객체 위 작은 점의 시각 단서를 LM 에 주입.
- **MolmoMotion-1M annotation pipeline** — grounding(MolmoPoint+SAM3) → 2D track(AllTracker) → metric 3D lifting(ViPE) → 필터/스무딩 → 모션 구간 clipping 의 5단계 자동 주석.
- **PWT (Percentage Within Threshold)** — 예측 점이 GT 의 임계 반경 안에 든 비율의 평균. ADE/FDE 와 함께 쓰는 3D 모션 정확도 지표.

---

## 🔬 방법론

### 직관

MolmoMotion 의 출발점은 "모션 예측 모델이 무엇을 출력해야 가장 쓸모 있는가"라는 표현(representation) 질문입니다. 영상 픽셀을 통째로 생성하면 그럴듯하지만 비싸고, downstream 에서 다시 추출해야 합니다. 객체 pose 를 예측하면 강체·손처럼 템플릿이 있는 카테고리에만 묶입니다. 2D point track 은 카테고리에 무관하지만, 이미지 평면 좌표라서 객체가 실제로 움직인 것인지 카메라가 움직인 것인지 구분이 안 됩니다. 저자들은 **객체 표면에 붙은 소수의 점을 world 좌표 3D 로 추적**하면 이 세 문제를 동시에 피한다고 봅니다 — 점은 어떤 객체에도 붙일 수 있어 class-agnostic 하고, 공유 world frame 을 쓰므로 카메라가 바뀌어도 같은 운동이 같게 표현되며(view-stable), 객체 위 점에만 집중하므로 compact 합니다.

핵심 task 는 이렇습니다. 기준 시각 $`t_{0}`$ 에 객체 위 몇 개의 점이 주어지고, 짧은 RGB 이력과 "서랍을 연다" 같은 언어 목표가 주어지면, 모델은 그 점들이 앞으로 어디로 갈지 3D 궤적을 예측합니다. 언어가 중요한 이유는, 같은 장면에서도 "들어올린다"와 "민다"는 전혀 다른 미래를 만들기 때문입니다 — 명령이 가능한 미래의 검색 공간을 좁혀줍니다.

모델은 같은 입력 인코딩(RGB + 텍스트 + 2D 점 특징)을 공유하되, 미래 궤적을 내는 방식이 다른 **두 변종**을 둡니다. AR 변종은 좌표를 텍스트로 한 토큰씩 생성해 매끄럽고 결정론적인 예측에 강하고, FM 변종은 노이즈에서 궤적 분포를 한 번에 생성해 불확실성 포착과 빠른 추론에 강합니다. 마지막으로 저자들은 이 모션 예측을 **사전학습 과제**로 보고, 거기서 얻은 표현을 로봇 매니퓰레이션과 영상 생성으로 옮길 수 있음을 보입니다 — 객체의 3D 운동은 사람 손이든 로봇 그리퍼든 비슷하므로, 인터넷 사람 영상에서 배운 prior 가 로봇으로 자연스럽게 전이된다는 논리입니다.

![Figure 1 — Overview](https://arxiv.org/html/2606.18558/x12.png)

> "Overview. We introduce the task of goal-conditioned 3D point motion prediction. Given initial 3D query points on an object, history RGB observations, and a language description of the future action, our model predicts the future 3D positions of all queried points in a metric world coordinate frame. We show that pretraining this motion prediction task produces a transferable motion representation for downstream applications, including robotics planning and video generation." (§1)
> (한글 해설 — task 정의와 "모션 예측을 사전학습으로 보면 전이 가능한 표현이 나온다"는 논문 전체 주장을 한 장으로 압축한 그림입니다.)

### 아키텍처

입력은 세 가지로 인코딩됩니다. 기준 시각 $`t_{0}`$ 에 객체 위 $`N`$ 개의 2D query point $`\{\mathbf{q}_{t_{0}}^{n}\in\mathbb{R}^{2}\}_{n=1}^{N}`$ 와 그에 대응하는 초기 3D 위치 $`\{\mathbf{p}_{t_{0}}^{n}\in\mathbb{R}^{3}\}_{n=1}^{N}`$ (depth + intrinsics 로 lift), 짧은 RGB 이력 $`I_{t_{s}:t_{0}}`$, 언어 명령 $`a`$ 가 주어지고, 목표는 horizon $`T`$ 동안의 미래 3D 위치 $`\{\{\hat{\mathbf{p}}_{t}^{n}\in\mathbb{R}^{3}\}_{t=t_{0}+1}^{t_{0}+T}\}_{n=1}^{N}`$ 입니다.

> "We therefore use Molmo2 [17] as the vision-language backbone for input processing, leveraging its strong object-grounding capability." (§2.2)
> (한글 해설 — 언어로 객체를 지시받아 모션을 예측하려면 먼저 그 객체를 화면에서 잡아야 하므로, grounding 이 강한 Molmo2 를 backbone 으로 택했습니다.)

Molmo2 vision encoder 가 RGB 이력에서 image token $`\mathcal{T}_{\mathrm{img}}`$ 를, 명령 $`a`$ 가 text token $`\mathcal{T}_{\mathrm{text}}`$ 를 만듭니다. query point 조건화는 anchor 프레임 feature map $`F_{t_{0}}`$ 를 각 $`\mathbf{q}_{t_{0}}^{n}`$ 위치에서 bilinear sampling 해 point feature $`\mathbf{e}_{\mathrm{pt}}^{n}`$ 를 얻고, 이를 image·text 토큰과 이어붙여 $`\mathcal{C}=[\mathcal{T}_{\mathrm{img}},\mathcal{T}_{\mathrm{text}},\mathcal{T}_{\mathrm{pt}}]`$ 로 LM 에 넣습니다. 두 변종은 이 $`\mathcal{C}`$ 를 공유하고 **초기 3D 좌표의 인코딩 방식과 미래 궤적의 디코딩 방식만 다릅니다**.

> "We implement two classes of trajectory predictors: one with an autoregressive objective and the other with a flow-matching objective." (§2.2)
> (한글 해설 — 두 목적이 상보적 모델링 편향을 갖기 때문입니다: AR 은 직전 예측에 조건화되어 매끄러운 시간 진화를, FM 은 미래 분포를 모델링해 불확실성을 잘 다룹니다.)

구현 세부(부록 D.1)는 다음과 같습니다. backbone 은 `Molmo2-4B-Pretrain` 으로, vision encoder 는 `378×378` 입력 · 14-pixel patch 의 SigLIP2 ViT 로 프레임당 `27×27` grid 의 1152-D 토큰을 만들고, connector 가 `3×3` pooling 후 LM hidden `2560` 으로 투영합니다. LM 은 `Qwen3-4B` 이며 backbone 전체를 end-to-end 학습합니다. FM 변종의 디코더는 **LM 층마다 하나씩 36개 블록**의 DiT trajectory expert 로, 각 블록은 shape `(N, H+T, 3)` 의 trajectory 텐서에 self-attention 을 건 뒤 해당 LM 층 hidden 을 key/value 로 하는 cross-attention 을 적용하고, **point-index 축과 frame-index 축 양쪽에 RoPE** 를 걸어 "같은 점의 다른 시각"과 "다른 점의 같은 시각"을 구분합니다.

![Figure 2 — MolmoMotion architecture](https://arxiv.org/html/2606.18558/x13.png)

> "MolmoMotion architecture. The shared input to Molmo2 [17] backbone consists of image tokens of RGB observations, text tokens of action description, and 2D query point feature tokens sampled from Molmo2 vision encoder. The autoregressive variant encodes the initial 3D query coordinates and decodes future trajectories as quantized coordinate text, while the flow-matching variant represents them directly in continuous 3D coordinate space." (§2.2)
> (한글 해설 — 공유 입력 인코딩과 두 디코더 분기를 한눈에 보여주는 그림. AR 은 좌표를 양자화 텍스트로, FM 은 연속 3D 공간으로 다룹니다.)

### 학습 목표 / 손실

두 변종 모두 좌표를 첫 query point 기준 **anchor-relative 델타**로 표현합니다. $`\mathbf{p}_{\mathrm{anc}}=\mathbf{p}_{t_{0}}^{1}`$ 라 두면

$$\boldsymbol{\delta}_{t}^{n}=\mathbf{p}_{t}^{n}-\mathbf{p}_{\mathrm{anc}}$$

이고, 모든 좌표는 meter 단위 metric scale 입니다.

> "For both prediction variants, we represent 3D coordinates relative to the first query point at $`t_{0}`$." (§2.2)
> (한글 해설 — 전역 위치 오프셋을 빼고 상대 운동만 남기는 좌표계로, 뒤의 ablation 에서 이 선택이 정확도의 가장 큰 단일 기여 요인으로 나타납니다.)

**AR 목적.** anchor-relative 좌표를 millimeter bin 으로 이산화하고

$$\bar{\boldsymbol{\delta}}_{t}^{n}=\mathrm{round}\!\left(1000\,\boldsymbol{\delta}_{t}^{n}\right)$$

시간순 point-coordinate tuple 로 직렬화합니다. 입력 프롬프트는 시각-언어 조건 $`\mathcal{C}`$ + 직렬화된 초기 query 좌표를 담고, 출력은 미래 궤적 문자열 $`y_{1:L}`$ 을 시간순으로 생성합니다. 표준 next-token 목적으로 학습하며, 손실은 **answer span 에만** 걸고 prompt(이미지·텍스트·점특징·이력좌표)는 마스킹합니다. 추론 시 좌표 문자열을 greedy 로 디코딩하고 파서가 $`\hat{\mathbf{P}}_{t_{0}+1:t_{0}+T}`$ 로 재조립합니다. 시각 $`t`$ 에 보이는 점만 출력하고 가려진 점은 imputation 하지 않습니다.

**FM 목적.** FM 변종은 미래 anchor-relative 궤적 텐서 $`\boldsymbol{\delta}_{t_{0}+1:t_{0}+T}\in\mathbb{R}^{N\times T\times 3}`$ 를 연속 좌표로 예측합니다. 학습 시 flow timestep $`\tau\sim\mathcal{U}(0,1)`$ 와 가우시안 노이즈 $`\epsilon`$ 를 뽑아 보간한 궤적(식 3)을 만듭니다.

$$\boldsymbol{\delta}_{\tau}=(1-\tau)\,\epsilon+\tau\,\boldsymbol{\delta}_{t_{0}+1:t_{0}+T}$$

$`\tau=0`$ 에서 순수 노이즈, $`\tau=1`$ 에서 clean 궤적으로 직선 이동합니다. 디코더 $`v_{\phi}`$ 는 그 직선 경로의 속도(= clean − noise)를 회귀하도록 표준 flow-matching MSE(식 4)로 학습됩니다.

$$\mathcal{L}_{\mathrm{FM}}=\mathbb{E}_{\tau,\,\epsilon}\!\left[\,\left\|v_{\phi}\!\left(\boldsymbol{\delta}_{\tau},\,\tau,\,\{\boldsymbol{\delta}_{t_{0}}^{n}\}_{n=1}^{N},\,\mathcal{C}\right)-\bigl(\boldsymbol{\delta}_{t_{0}+1:t_{0}+T}-\epsilon\bigr)\right\|_{2}^{2}\,\right]$$

> "The decoder is trained with the standard flow-matching objective [46]." (§2.2)
> (한글 해설 — 손실은 미래 위치에만 마스킹해 걸고, clean history 부분은 supervision 없이 둡니다. 회귀 타깃 $`\boldsymbol{\delta}_{t_{0}+1:t_{0}+T}-\epsilon`$ 는 식 3 직선 경로를 따라가는 일정 속도입니다.)

추론은 $`\epsilon\sim\mathcal{N}(0,I)`$ 에서 시작해 $`K=10`$ Euler step 으로 $`\tau`$ 를 0→1 까지 $`\Delta\tau=0.1`$ 씩 적분합니다(식 5).

$$\boldsymbol{\delta}_{\tau+\Delta\tau}=\boldsymbol{\delta}_{\tau}+\Delta\tau\cdot v_{\phi}\!\left(\boldsymbol{\delta}_{\tau},\,\tau,\,\{\boldsymbol{\delta}_{t_{0}}^{n}\}_{n=1}^{N},\,\mathcal{C}\right)$$

최종 $`\boldsymbol{\delta}_{1}`$ 에 anchor 위치 $`\mathbf{p}_{\mathrm{anc}}`$ 를 더해 world frame 미래 위치를 복원합니다. DiT 블록 수가 LM 층 수와 같고 한 번의 $`v_{\phi}`$ 평가가 캐시된 LM activation 을 재사용하므로, Euler step 하나는 대략 LM forward 한 번의 비용입니다.

### 학습 셋업

> "MolmoMotion uses the pretrained 4B Molmo2 [17] as its VLM backbone." (§4.1)
> (한글 해설 — 사전학습 VLM 을 그대로 초기화로 쓰고, backbone 전체를 모션 과제로 미세조정합니다.)

학습은 2단계입니다. **1단계**: 각 clip 에서 시작 시각 $`t_{0}`$ 를 랜덤 샘플, 한 객체에서 $`N=8`$ query point 를 뽑아 `15 fps` 로 $`T=8`$ 미래 시각(예제당 64개 3D 타깃)을 예측, history $`H=3`$, 40K step. **2단계**: 10K step 동안 horizon 을 $`T=32`$ 로 늘리고 $`H=3`$ 과 $`H=1`$ 두 변종을 학습해 짧은 이력과 단일 프레임 설정을 모두 지원. 옵티마이저는 Molmo2 SFT 기본값의 AdamW($`\beta_{1}=0.9`$, $`\beta_{2}=0.95`$, weight decay `0.1`), LR 은 첫 1K step linear warmup 후 peak 의 `0.1×` 로 cosine decay, grad clip max-norm `1.0`, bf16 activation + fp32 master, **16× H100 에 FSDP2 full-shard, per-device batch 16, global batch 256**. 6개 MolmoMotion-1M 소스는 clip 수의 square-root 가중으로 혼합합니다.

### 데이터 주석 파이프라인 (MolmoMotion-1M)

action description 이 있는 공개 영상(EgoDex, HD-EPIC, Xperience-10M, YT-VIS, Stereo4D 등)에서 5단계로 object-grounded 3D track 을 추출합니다(Fig. 3).

![Figure 3 — Data annotation pipeline](https://arxiv.org/html/2606.18558/x14.png)

> "Overview of data annotation pipeline. Given a video of an action event and its description, we first ground the moving object and sample query points on it. We then track dense 2D points on the object, lift these tracks into a shared metric 3D frame, and use object-level spatial and temporal consistency priors to filter unreliable trajectories. Finally, we clip the video around intervals where the grounded object undergoes meaningful motion." (§3.1)
> (한글 해설 — grounding → 2D tracking → 3D lifting → 필터 → clipping 의 흐름. 자동 파이프라인이 인터넷 영상을 3D 모션 supervision 으로 바꾸는 핵심 엔진입니다.)

1. **Semantic grounding** — LLM 으로 명령에서 객체 구를 추출, `MolmoPoint` 로 2D 점 지목 후 `SAM3` 로 마스크 $`M_{t_{0}}`$, K-means cluster center 로 $`N`$ query 점 샘플. (SAM3 직접 prompting 대신 MolmoPoint 를 먼저 쓰는 이유는 "테이블 위 물건" 같은 모호한 구에 더 강건하기 때문.)
2. **2D tracking + metric 3D lifting** — `AllTracker` 로 2D track + visibility, `ViPE` 로 per-frame metric depth · 카메라 geometry 추정 후 back-projection 으로 first-frame 카메라 기준 world frame 의 metric 3D track 생성. (end-to-end 3D tracker(SpatialTrackerV2)보다 정확하다고 경험적으로 보고.)
3. **필터·스무딩** — MAD 기반 outlier 제거 + Stereo4D 스무딩으로 depth jitter 제거(객체 점들이 한 물체의 일부로 coherent 하게 움직인다는 prior).
4. **Video clipping** — per-frame 모션 점수 $`s_{t}=\mathrm{median}_{n}\left\|\mathbf{p}_{t}^{n}-\mathbf{p}_{t-1}^{n}\right\|_{2}`$ 를 임계화해 유의미한 운동 구간만 남김(정적 영상 자동 제거).

결과 코퍼스는 약 1M clip, 736개 고유 action verb · 5,692개 고유 객체, median clip 길이 0.8–1.1 s(조작) / 1.7 s(Stereo4D), median per-clip 3D 변위 7–9 cm(조작) / 51 cm(Stereo4D), clip 당 median 88 query point(범위 60–100) 입니다.

---

## 📊 실험 설정과 결과

평가 지표는 모두 3D world space 에서 계산됩니다. ADE 는 모든 가시 query 점·예측 시각의 평균 변위 오차, FDE 는 마지막 시각의 변위 오차, PWT 는 임계 반경 안에 든 점 비율의 평균입니다.

$$\mathrm{ADE}=\frac{1}{|\mathcal{S}|}\sum_{(t,n)\,\in\,\mathcal{S}}\|\hat{p}(t,n)-q(t,n)\|_{2}$$

> "$`\mathrm{PWT}`$ is the average fraction of predicted points within $`\{0.01,0.02,0.05,0.10,0.20\}`$ meters of the ground truth." (§4.1)
> (한글 해설 — 1 unit = 1 m. ADE/FDE 는 낮을수록, PWT 는 높을수록 좋음. 각 샘플 best-of-5 평가.)

### 3D point motion forecasting (PointMotionBench, Table 1)

| Model (frames) | HOT3D ADE↓ | HOT3D PWT↑ | WorldTrack ADE↓ | WorldTrack PWT↑ | DAVIS ADE↓ | DAVIS PWT↑ |
|---|---|---|---|---|---|---|
| Static (1) | 0.180 | 0.293 | 0.167 | 0.390 | 2.281 | 0.085 |
| Extrapolate (3) | 0.159 | 0.351 | 0.184 | 0.436 | 2.683 | 0.104 |
| Wan2.2-5B (1) | 0.200 | 0.253 | 0.852 | 0.090 | 3.074 | 0.051 |
| Cosmos Predict (5) | 0.225 | 0.199 | 0.831 | 0.072 | 4.191 | 0.033 |
| ObjectForesight (3) | 0.129 | 0.353 | – | – | – | – |
| Track2Act (1) | 0.294 | 0.202 | 1.230 | 0.053 | 4.853 | 0.018 |
| **MolmoMotion-FM (3)** | 0.135 | 0.382 | 0.158 | 0.438 | 1.480 | 0.130 |
| **MolmoMotion-AR (1)** | 0.157 | 0.303 | 0.148 | 0.424 | 1.146 | **0.199** |
| **MolmoMotion-AR (3)** | **0.109** | **0.444** | **0.143** | **0.445** | 1.227 | 0.153 |

> "MolmoMotion outperforms prior methods by a large margin in almost all subsets of PointMotionBench, with the autoregressive variant achieving the strongest overall performance." (§4.1)
> (한글 해설 — AR(H=3) 이 HOT3D ADE 0.109 로 최고. ObjectForesight/EgoScaler 는 object mesh 가 필요해 HOT3D subset 에서만 평가됨.)

읽어둘 포인트 두 가지: (1) AR 이 결정론적 지표(ADE/FDE/PWT)에서 FM 을 앞서는데, 직전 좌표에 조건화되어 시간적으로 매끄러운 예측을 내기 때문입니다. (2) **단순 non-parametric baseline(Static/Extrapolate)이 학습된 픽셀-공간 영상 예측(Wan2.2, Cosmos)보다 오히려 강한** 경우가 많습니다 — 시각적으로 그럴듯한 RGB 미래가 정확한 metric point 운동을 복원하지는 못한다는 신호입니다.

### 모델 ablation (AR, H=3 기준; Table 6)

| 변종 | HOT3D ADE↓ | WorldTrack ADE↓ | DAVIS ADE↓ |
|---|---|---|---|
| MolmoMotion-AR (reference) | 0.109 | 0.143 | 1.227 |
| − 2D point feature | 0.118 | 0.155 | 1.310 |
| Absolute coords (no delta) | 0.165 | 0.220 | 1.940 |
| − language instruction | 0.158 | 0.215 | 1.890 |
| N=16 query points | 0.106 | 0.140 | 1.198 |

각 행이 분리하는 것: **anchor-relative 제거(절대 좌표)** 가 ADE/FDE 전 split 에서 약 50% 악화로 가장 큰 단일 기여 — 좌표 파라미터화가 가장 중요한 설계임을 뜻합니다. **언어 제거**도 비슷한 폭으로 악화하며, 특히 단일 anchor 프레임에서 의도 추론이 어려운 DAVIS 에서 타격이 큽니다 — 언어가 객체 disambiguation 을 넘어 **방향 prior** 를 제공함을 보입니다. **2D 점 특징**은 5–8%(ADE/FDE)의 작지만 일관된 이득(작은 객체가 많은 DAVIS 에서 최대). **N=16** 은 2–3% 개선에 그치는데, 8점이 K-means 로 이미 표면을 조밀히 덮고, 무엇보다 $`N=16`$, $`T=32`$ 의 AR answer span 이 Qwen3-4B 의 4096-token context 를 초과하기 때문에 기본값을 $`N=8`$ 로 둡니다.

### 추론 비용 (Table 7) · 로봇 전이 · 영상 생성

추론 비용은 A100 한 장, $`(N{=}8, T{=}32)`$, $`H{=}3`$ 기준 AR 148.4 s/clip vs FM($`K{=}10`$) 1.1 s/clip 입니다.

> "Flow-matching is roughly $`\mathbf{150\times}`$ faster than autoregressive decoding at $`T{=}32`$, at the modest accuracy cost in Tab. 1." (§E, Table 7)
> (한글 해설 — AR 비용은 $`N{\cdot}T`$ 에 선형으로 늘지만 FM 은 고정 K step 이라 $`T`$ 에 무관. closed-loop 제어·영상 가이드·대규모 평가처럼 속도가 중요한 영역은 FM 이 적합.)

로봇 전이(MolmoSpaces Franka pick-and-place)는 동일한 MolmoBot flow-matching action head · 20K 에피소드에서 backbone 초기화만 Molmo2 vs MolmoMotion-AR 로 바꿔 비교합니다.

> "success reaches 51% at 10K steps vs. 19% for Molmo2, and final average success increases from 56.0% to 76.3%." (§4.2)
> (한글 해설 — MolmoMotion 초기화가 학습 효율(10K step 51% vs 19%)과 최종 성공률(76.3% vs 56.0%)을 모두 끌어올리고, unseen-object/scene split 에서 낙폭이 작아 일반화 이득을 시사. DROID 미세조정에서도 더 낮은 L2 에서 시작해 더 빨리 수렴.)

영상 생성(Table 2)에서는 MolmoMotion 의 예측 track 으로 `DaS`(CogVideoX-5B 기반 3D-track-conditioned I2V)를 가이드하면, 5개 VBench 모션 지표 중 4개에서 약 2.8배 큰 `Wan2.2-I2V-A14B` 를 앞서고 base CogVideoX-5B 는 전 지표에서 상회합니다(Tem-Con 0.968 / Subj-Cons 0.950 / M-Smooth 0.990 / Dyn-Deg 0.876 / Bg-Cons 0.948).

---

## ⚖️ 한계

- **희소한 8점 — 기하·변형 표현 부족(저자 명시)** — 2단계 학습이 Molmo2 context 한계로 객체당 8 query point 만 쓰므로, 객체 geometry 를 조밀히 표현하지 못하고 fine-grained 구조·복잡한 변형 모션 이해가 제한됩니다. 조밀 track 을 얻으려면 여러 forward pass 가 필요합니다. 메커니즘적으로 이는 AR answer span 이 $`N{\cdot}T`$ 에 선형이라 4096-token 창에 갇히는 데서 옵니다 — tokenization 개선이나 context 확장이 없으면 dense·long-horizon 은 풀리지 않습니다.
- **Downstream 검증의 폭 부족(저자 명시)** — closed-loop 실제 로봇 실험이 없어, 모션 사전학습의 효과가 sim(MolmoSpaces) pick-and-place 와 DROID **오프라인 trajectory L2** 로만 입증됩니다. 정책의 실제 폐루프 성능으로 곧장 이어진다는 보장은 아직 없습니다.
- **자동 3D 주석의 노이즈 상한** — supervision 자체가 monocular depth(ViPE) + 2D track(AllTracker) 추정에서 lift 되므로, GT 가 추정치입니다. MAD 필터·스무딩으로 완화하지만 metric scale·depth 오차가 라벨에 스며들 수 있고, 이는 모델 상한을 데이터 파이프라인 품질에 묶습니다.
- **객체-중심 표현의 사각지대** — 점이 **조작 대상 객체 위**에만 붙어, 손/그리퍼 자체의 모션이나 손가락-수준 접촉은 표현 대상이 아닙니다. 도구 조작·변형체처럼 객체 운동만으로 의도를 다 담지 못하는 경우, 표현이 구조적으로 정보를 놓칩니다.
- **결정론 지표가 FM 의 강점을 가린다** — best-of-5 ADE/FDE/PWT 는 단일 mode 의 정확도를 재므로, 다봉 미래를 모델링하는 FM 의 이점이 수치로 잘 드러나지 않습니다. 불확실성이 중요한 설정에서의 우위는 본 평가에서 측정되지 않습니다.

---

## ♻️ 재현성

- **코드/모델** — `https://github.com/allenai/molmo-motion` 공개(메타). 모델·데이터(MolmoMotion-1M, PointMotionBench)를 함께 릴리스한다고 명시하며, Apache License 2.0 하에 공개(Xperience 데이터 사용 허가 명기).
- **하드웨어/레시피** — 학습 16× H100(FSDP2), global batch 256, 40K+10K step, AdamW 하이퍼 전부 명시. FM 추론 K=10 Euler. 로봇 전이(부록 F)·영상 생성(부록 G) 설정도 상세.
- **데이터 출처** — EgoDex / HD-EPIC / Xperience-10M / YT-VIS / Stereo4D 등 공개 코퍼스 + 자동 파이프라인. PointMotionBench 는 HOT3D / WorldTrack / DAVIS 재활용 + 사람 검증. 일부 소스(HD-EPIC, Xperience)는 외부 라이선스·접근 제약이 있어 완전 재현엔 원천 데이터 확보가 필요.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P5(World Model) — 주(primary).** MolmoMotion 은 사실상 **언어-목표 조건의 3D-flow forward 예측 모델**이며, 그 표현이 로봇 매니퓰레이션으로 전이됨을 보입니다. 이는 P5 의 핵심 베팅 — **action/goal-conditioned · egocentric · 3D-flow(픽셀 아닌 contact-relevant) 예측을 dynamics prior 로** — 와 정면으로 맞물립니다. 특히 D30(prediction space)의 v1 = "latent / 3D-flow" 선택에 대한 직접 증거(3D-flow 가 픽셀 대비 우월)이고, D31(action conditioning)에는 **per-frame action 이 아니라 언어 goal 조건**이라는 변형으로 닿습니다. D28(world-model role)에는 "co-trained auxiliary head" 대신 **사전학습→backbone 초기화 전이**라는 더 가벼운 통합 경로를 제시합니다(D29 대안).
- **P0(VLA Datasets & Benchmarks) — 부.** MolmoMotion-1M(1.16M 영상, egocentric 조작 비중 큼)과 PointMotionBench 는 D24(egocentric 우선 데이터 축)·D26(benchmark 스코우팅)에 바로 들어오는 신규 데이터/벤치 후보이며, Apache-2.0 라이선스로 D27(usability bar)을 통과합니다.
- **P4(Pretraining for Data-Efficient Adaptation) — 부.** "모션 예측을 사전학습 과제로 두면 적은 robot 데이터로 빠르게 적응한다"는 결과는 D22(pretraining data composition — egocentric vs mixed)와 D19(backbone lineage)의 data-efficiency 논거에 증거를 더합니다.
- **Identity 긴장/지지** — 지지: "인터넷 사람 영상의 모션 prior → 로봇 전이"는 egocentric-centric pretraining(P4 D22)·data-efficient adaptation 테제를 강화. 긴장: 본 repo 의 차별화 주장은 **hand-level 접촉**인데 MolmoMotion 은 **객체-중심**이라 손가락·접촉 정보가 표현 밖입니다.
- **경쟁자 함의** — Allen AI(Molmo/MolmoBot 계열)의 모션-사전학습 라인. P5 Tracked Literature 의 World Guidance(WAM)·AHEAD 와 같은 "모션 prior → 행동" 계열에 직접 경쟁/보완.

---

## ✨ 핀 논문 대비 델타

- **vs DexWM([arXiv:2512.13644], P5 *Top* 핀)** — DexWM 은 사람 영상에서 **손-객체 상호작용 WM**(finger-keypoint + hand-consistency 예측)을 학습합니다. MolmoMotion 의 진짜 새로움은 (1) 예측 타깃이 손 keypoint 가 아니라 **객체 부착 · class-agnostic · world-frame metric 3D point**, (2) **1.16M 영상 인터넷 스케일** + **언어 goal 조건**, (3) WM 특징 distillation 이 아니라 **backbone 초기화만으로** 로봇 전이를 입증한다는 점입니다.
- **vs AHEAD([arXiv:2606.02486])·VLA-JEPA([arXiv:2602.10098])** — 둘은 **latent** 예측을 dynamics prior 로 씁니다. MolmoMotion 은 latent 가 아니라 **명시적·해석 가능한 3D 궤적**을 예측하고 그 궤적 자체를 영상 생성 control signal 로도 직접 소비합니다(downstream 가용성↑).
- **vs World Guidance([arXiv:2602.22010])·LaST-HD([arXiv:2606.23685])** — 사람-조작 영상에서 모션 prior 를 길어 행동으로 잇는 같은 정신이지만, World Guidance/LaST-HD 가 condition-space/latent 정렬을 쓰는 데 비해 MolmoMotion 의 prior 는 **구체적 3D track predictor + 대규모 공개 데이터/벤치마크**라는 점이 다릅니다.

---

## ⚙️ 의사결정 함의

- **D30(prediction space) — 3D-flow 채택에 대한 정량 증거.** ablation 이 "absolute → anchor-relative delta ≈ 50% 개선", "language 조건 ≈ 50% 개선"을 보입니다. 우리가 3D-flow WM aux head 를 둔다면, 예측 타깃을 **anchor-relative metric delta + language/goal 조건**으로 파라미터화하라는 구체 설정이 나옵니다. config 키: 좌표 origin = first-query anchor, 단위 = meter, AR 경로 시 mm 양자화(`round(1000·δ)`).
- **D28/D29(role·integration) — 통합 경로 선택지 추가.** "co-trained auxiliary head"(현재 v1) 외에 **motion-pretrain → action-finetune(backbone init 전이)**라는 더 싼 경로가 실증됩니다. 적용 시 config: action 학습 전 backbone 을 모션-예측 checkpoint 로 초기화하고 동일 flow-matching action head 를 얹음(MolmoBot recipe: cross-attn 36 block, action dim 8, horizon 16, 10 Euler step).
- **D31(action conditioning) — 주의.** MolmoMotion 은 **per-frame action 이 아니라 언어 goal** 조건입니다. 우리 v1 의 per-frame action-conditioned 선택을 유지하려면, 이 논문은 "goal 조건만으로도 강한 prior 가 학습된다"는 보완 증거로 읽되 그대로 차용하지 않는 게 맞습니다.
- **D23(action representation) — FM head 설계 재확인.** DiT trajectory expert(LM 층당 1 block, point·time 양축 RoPE, K=10 Euler)는 우리의 continuous flow-matching head(D23 v1)와 정합. metric: ADE/FDE(m), mean PWT(δ∈{0.01,0.02,0.05,0.10,0.20} m) 를 모션-prior 품질 게이트로 도입 가능.
- **P0 카탈로그 액션** — MolmoMotion-1M 을 `catalogs/datasets.md`(👤 ego 중심)에, PointMotionBench 를 `catalogs/benchmarks.md`(✋/🧪)에 후보 등재 검토.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 체크) 객체-중심 ≠ 손-중심.** 릴리스된 MolmoMotion-1M 주석이 **손/손가락 점을 포함하는가**? 파이프라인은 "조작 대상 객체"를 grounding 하므로 손 keypoint 는 타깃이 아닙니다. 우리 thesis(per-finger 접촉)에는 표현이 구조적으로 비어 있어, 그대로는 P1/P2/P3 의 손-수준 신호를 못 줍니다.
- **Backbone lineage 불일치.** init 전이 이득은 `Molmo2-4B`(Qwen3-4B + SigLIP2)에서 측정됐습니다. 우리 D19 v1 은 PaliGemma×π(openpi) lineage 이므로, **π backbone 으로 모션-사전학습 checkpoint 의 이득이 전이되는지**는 별도 검증 필요(같은 lineage 가 아니면 효과 비보장).
- **3D supervision 정밀도.** ViPE monocular depth 기반 metric track 은 mm 급 정밀도를 보장하지 못합니다. 접촉/in-hand 처럼 mm 오차가 치명적인 regime 에서는 라벨 노이즈가 곧장 한계가 됩니다 — 우리 데이터(촉각·접촉)로 옮길 때 첫 검증 대상.
- **Sim·post-grasp 편향.** 로봇 전이가 MolmoSpaces **sim** 의 pick-and-place **post-grasp** 구간에 한정됩니다. contact-rich·dexterous·closed-loop 실로봇으로의 일반화는 미검증 — 우리 phase 1(in-hand rotation) 같은 과제로 직접 옮기기 전 폐루프 실험이 선행돼야 합니다.
- **Context-length 천장.** AR 변종은 $`N{\cdot}T`$ 선형이라 dense·long-horizon 이 4096-token 창에 막힙니다. 손-수준 dense 점을 long horizon 으로 쓰려면 tokenization/context 확장이 전제 — 채택 전 비용 추정 필요(FM 변종은 이 천장에서 자유로우나 결정론 정확도는 다소 낮음).

---

## 💡 컨텍스트 제안

- **P5** — MolmoMotion 을 P5 methodology-base(또는 핀 후보)로 추적 검토 권장: "world-frame 3D-flow 모션 prior + transfer-by-init" 라는 D28/D30 증거. 다만 **객체-중심**이라 D32(hand-object egocentric 우선)의 down-weight 대상에 가까우므로, 핀(8개 cap)보다는 methodology-base 등재가 적절할 수 있음(World Guidance/AHEAD 옆).
- **P0** — MolmoMotion-1M(👤 ego 중심, Apache-2.0) + PointMotionBench(111 cat / 61 motion, human-verified)를 `catalogs/datasets.md` / `catalogs/benchmarks.md` 후보로 제안. 단 hand-tracking·tactile 축은 아니므로 "객체 3D 모션" 라벨로 분류.
- **P4** — "모션 예측 = 사전학습 과제" 라인을 D22(data composition) 증거 풀에 추가 검토. 단, context/ 파일은 수정하지 않으며 위는 제안일 뿐입니다.
