# Paper Analysis — Finetuning Vision-Language-Action Models Requires Fewer Layers Than You Think

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Finetuning Vision-Language-Action Models Requires Fewer Layers Than You Think |
| 저자 | Gia-Binh Nguyen, Trong-Bao Ho, Thien-Loc Ha, Khoa Vo, Philip Lund Møller, Quang T. Nguyen, Long Dinh, Tuan Dam, Vu Duong, Tung M. Luu, Trung Le, Tran Nguyen Le, Minh Vu, An Thai Le, Ngan Le, Daniel Sonntag, James Zou, Jan Peters, Duy M. H. Nguyen†, Ngo Anh Vien† (†Project Leads) |
| 링크 | [arXiv:2606.20246](https://arxiv.org/abs/2606.20246) · [Website](https://clpvla.github.io/) |
| 발행일 / 버전 | 2026-06-18 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-22 |
| 관련 Pillar | P4, P1 |
| 태그 | vla-arch, peft, flow-matching |

---

## 🧭 한 줄 요약 (TL;DR)

현대 continuous-control VLA (π0, GR00T-N1.5, SmolVLA) 는 깊이 방향으로 심한 표현 중복(representational redundancy)을 가지므로, **CKA(Centered Kernel Alignment) 한 번의 forward pass** 만으로 중복 layer 를 식별해 fine-tuning **전에** 정적으로 제거(최대 깊이 50%)할 수 있으며, 그 결과 학습 시간 40–50% · 추론 30% 단축에 더해 저데이터 영역에서는 오히려 성능이 향상된다(implicit regularizer) — 즉 SOTA VLA 는 통념보다 훨씬 적은 layer 로 충분하다는 주장.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 수십억 파라미터의 현대 VLA 는 downstream fine-tuning 과 실시간 추론 모두에서 막대한 연산·메모리 비용을 강제한다. "fine-tuning 이전에 redundant layer 를 제거해도 정책 성능을 잃지 않을 수 있는가?" 가 핵심 질문이다.
- **기존 접근의 한계** — (i) training-free token pruning / caching (VLA-Cache, EfficientVLA, SpecPrune-VLA) 는 **추론만** 가속하고 비싼 downstream fine-tuning 단계는 그대로 둔다. (ii) training-adaptive 방식 (DeeR-VLA, MoLe-VLA) 은 routing 모듈·early-exit head·distillation 을 추가해 핵심 구조를 바꾸고 학습 알고리즘과 마찰을 일으킨다.
- **본 논문의 가설** — modern VLA backbone 의 연속 transformer block 들은 고도로 상관된(중복) token 표현을 만들며, 이 high-similarity 구간의 layer 는 downstream 성능 저하 없이 제거 가능하다.
- **왜 지금 중요한가** — 평가 범위가 구식 autoregressive baseline(OpenVLA)에 치우쳐 있고 real-world 검증이 1–2개 단순 과제에 그쳤던 반면, 본 논문은 flow-matching 기반 SOTA 연속제어 모델을 표적해 3개 시뮬레이션 벤치마크 + 10개 실세계 과제 + 4개 임베디먼트로 광범위 검증한다.

---

## 🧩 핵심 기여

- **CLP (CKA-guided Layer Pruning)** — 단일 forward pass + CKA 로 표현 중복 transformer block 을 식별하고 fine-tuning **전에** 영구 제거하는 calibration 기반·training-free 압축 프레임워크. 보조 routing/early-exit/distillation 모듈이 전혀 없다.
- **SOTA 연속제어 foundation 의 저비용 적응** — π0, GR00T-N1.5 같은 모델을 깊이를 크게 줄인 채 fine-tune 해도 메모리·학습·추론 비용을 동시에 낮추면서 성능을 유지/초과함을 입증.
- **다임베디먼트 광범위 검증** — 3개 시뮬 벤치마크(LIBERO, RoboCasa, SimplerEnv) + 10개 실세계 과제 + 4개 로봇 임베디먼트(UR10, UR5, single-arm/bimanual ALOHA). 비침습적 깊이 축소가 platform-agnostic 하게 견고함을 보임.
- **압축의 정규화 효과** — 저데이터 영역에서 redundant layer 제거가 implicit regularizer 로 작동: LIBERO 10% 데이터에서 77.7% → 84.6%, 100-시연 실세계 과제에서 15–20% 향상.

---

## 🔑 기술 키워드

- **VLA (Vision-Language-Action) model** — 시각·언어 관측을 받아 로봇 action chunk 를 내놓는 멀티모달 정책. 본 논문의 압축 대상.
- **CKA (Centered Kernel Alignment)** — 두 layer 의 hidden 표현이 얼마나 닮았는지를 직교변환·등방 스케일에 불변하게 재는 [0,1] 유사도 점수. 어느 layer 가 "거의 일 안 하는지"를 판별하는 진단 도구.
- **Representational redundancy / plateau** — 연속 layer 들이 표현을 거의 바꾸지 않고 고만고만하게 통과시키는 깊이 구간. 압축 후보 zone.
- **Structured (layer) pruning** — 개별 가중치가 아니라 transformer block 전체를 통째로 떼어내고 앞뒤 block 을 재연결하는 압축. 정적이라 런타임 오버헤드가 없다.
- **Flow Matching** — Gaussian noise 를 target action 으로 선형 보간 경로를 따라 옮기는 velocity field 를 학습하는 연속 action 생성 목표. π0/GR00T/SmolVLA 의 action head 가 쓴다.
- **Calibration set** — pruning 판단용 CKA 를 계산하기 위해 학습 episode 에서 뽑은 소량 표본. 단 한 번 forward 만 흘린다.
- **Twin layers** — CKA 가 거의 1에 가까운, 사실상 같은 일을 하는 인접 layer 쌍. CLP 가 묶어서 한쪽만 남긴다.
- **Manifold restoration** — pruning 직후 좁아진 latent 공간이 fine-tuning 으로 원본과 닮은 표현 다양체로 복원되는 현상. 성능 회복의 기하학적 설명.
- **Training-free vs training-adaptive** — 추론만 가속(전자) / routing·early-exit 를 학습으로 추가(후자)하는 두 기존 가속 계열. CLP 는 둘 다 아닌 "정적 사전 압축".

---

## 🔬 방법론

### 직관 (Intuition)

CLP 의 출발점은 "깊은 VLA 안에서 정보가 layer 를 지날 때 실제로 얼마나 바뀌는가?"라는 진단 질문입니다. 저자들은 π0·GR00T-N1.5 의 hidden state 궤적을 CKA 로 추적했더니, 표현이 깊이에 따라 점진적·균일하게 변하는 게 아니라 **넓고 연속적인 정체 구간(plateau)** 을 이룬다는 것을 발견합니다. 즉 큰 특징 변환은 몇 개의 특정 transition 에만 몰려 있고, 나머지 인접 layer 들은 거의 같은 표현을 반복 통과시킬 뿐입니다.

여기서 자연스러운 가설이 나옵니다 — 이 high-similarity 구간의 layer 들은 떼어내도 정책 성능이 거의 안 떨어질 것이다. CLP 는 이를 곧이곧대로 실행합니다. calibration 표본으로 forward 를 한 번 흘려 인접 layer 간 CKA 점수를 재고, 임계값 τ 이상으로 묶이는 연속 block 을 찾은 뒤, 각 block 에서 **첫 layer(입력 표현을 세우는 anchor)만 남기고** 나머지를 가장 중복된 순서로 제거합니다.

핵심은 이 제거가 fine-tuning **이전**에, 학습 없이, 추가 모듈 없이 일어난다는 점입니다. 모든 block 이 같은 hidden 차원을 공유하므로 layer 를 빼면 앞뒤를 그냥 이어 붙이면 되고, 그 뒤 native 학습 목표(flow matching)로 그대로 fine-tune 합니다. 그래서 token pruning(추론만 빠름)이나 dynamic routing(모듈 추가)과 달리 학습·추론·메모리를 한꺼번에 줄이는 정적으로 더 작은 모델이 나옵니다.

마지막 직관은 "왜 성능이 안 깎이고 오히려 오르나?"입니다. PCA 로 보면 pruning 직후 latent 공간은 좁게 수축하지만, fine-tuning 동안 남은 layer 들이 경로를 재조직해 원본과 닮은 표현 다양체를 복원(manifold restoration)합니다. 저데이터에서는 줄어든 용량이 task-specific noise 과적합을 억제하는 implicit regularizer 로 작동해 오히려 이득을 줍니다.

### 아키텍처

![Figure 1 — CLP 파이프라인 개요](https://arxiv.org/html/2606.20246/images/CLS_Pruning_v2.png)

> "Figure 1: Overview of the proposed CLP framework. CLP prunes representationally redundant transformer layers via CKA, reducing network depth by up to 66% and training/inference cost by up to 50%. Fine-tuning restores the latent geometry of the compressed model, enabling competitive performance across three simulation benchmarks, 10 real-world tasks, and four robotic embodiments." (§3)
(한글 해설 — 좌측의 CKA 기반 layer 선택 → 정적 제거 → fine-tuning 으로 latent geometry 복원이라는 3단계 파이프라인 전체를 한 장으로 시각화합니다.)

대상 VLA 는 공통적으로 **decoupled** 구조입니다 — 환경 맥락을 추출하는 VLM backbone + 그 위에 flow/diffusion 기반 action-generation head.

> "State-of-the-art continuous-control foundations (e.g., $`\pi_{0}`$ [3], GR00T [2], SmolVLA [29]) generally share a decoupled architecture: a Vision-Language Model (VLM) backbone that extracts environmental context, followed by a flow- or diffusion-based action-generation head." (§3)
(한글 해설 — CLP 가 backbone 과 action head 양쪽 모두를 동일 원리로 prune 할 수 있는 이유가 이 공통 구조에 있습니다.)

**VLM backbone** 은 $`N_{v}`$ 개 transformer layer 의 스택입니다. $`H^{\text{vlm}}_{\ell}`$ 은 $`\ell`$ 번째 VLM layer 출력 hidden token, $`F^{\text{vlm}}_{\ell}`$ 은 해당 block, 입력은 언어·영상을 임베드한 $`H^{\text{vlm}}_{0}`$, 최종 맥락 표현은 $`Z=H^{\text{vlm}}_{N_{v}}`$ 입니다.

$$H^{\text{vlm}}_{0}=\mathrm{Embed}\left(\mathbf{x}^{\text{lang}},\mathbf{x}^{\text{img}}\right),\quad H^{\text{vlm}}_{\ell}=F^{\text{vlm}}_{\ell}\left(H^{\text{vlm}}_{\ell-1}\right)\quad\forall\ell\in\{1,\ldots,N_{v}\}.$$

**Action-generation head** 는 flow matching 으로, Gaussian noise $`\epsilon\sim\mathcal{N}(\mathbf{0},\mathbf{I})`$ 를 선형 보간 경로 $`\mathbf{a}_{t}=(1-t)\epsilon+t\mathbf{a}`$ 를 따라 target action $`\mathbf{a}`$ 로 옮기는 velocity field 를 파라미터화합니다. $`H^{\text{act}}_{m}`$ 은 $`m`$ 번째 action layer 의 hidden, $`F^{\text{act}}_{m}`$ 은 $`N_{a}`$ 개 layer 중 해당 block 입니다.

$$H^{\text{act}}_{0}=\mathrm{Embed}_{\text{act}}\left(\mathbf{a}_{t},t\right),\quad H^{\text{act}}_{m}=F^{\text{act}}_{m}\left(H^{\text{act}}_{m-1};\,\Phi_{m}(Z)\right)\quad\forall m\in\{1,\ldots,N_{a}\}.$$

여기서 $`\Phi_{m}(Z)`$ 는 VLM 맥락 $`Z`$ 에서 유도해 $`m`$ 번째 action layer 에 주입하는 cross-conditioning 신호(decoder cross-attention 또는 token prefixing)입니다. baseline 마다 $`\Phi_{m}`$ 전략은 다르지만, VLM·action 모듈을 모두 deep transformer block 으로 보는 이 공통 정식화 덕에 두 모듈의 중간 hidden state 가 layer 단위 유사도 분석에 구조적으로 호환됩니다.

### 학습 목표 / 손실

velocity field 예측 $`\hat{\mathbf{u}}_{t}=f_{\text{act}}(Z,\mathbf{a}_{t},t)=H^{\text{act}}_{N_{a}}`$ 는 Flow Matching 목표로 최적화됩니다. **CLP 는 이 native 목표를 바꾸지 않고** 그대로 둔 채 깊이만 줄입니다(추가 loss·distillation 없음).

$$\mathcal{L}_{\text{FM}}=\mathbb{E}_{t,\mathbf{a},\epsilon}\left[\left\|f_{\text{act}}\left(Z,\mathbf{a}_{t},t\right)-\left(\mathbf{a}-\epsilon\right)\right\|_{2}^{2}\right].$$

**CKA 정의.** hidden state $`H_{i},H_{j}\in\mathbb{R}^{n\times d}`$ 의 Gram 행렬 $`K=HH^{\top}`$ 정렬을 centered HSIC 으로 잰 뒤, centered linear kernel 에서는 Frobenius norm 비로 환원됩니다.

$$\mathrm{CKA}(H_{i},H_{j})=\frac{\mathrm{HSIC}(K_{i},K_{j})}{\sqrt{\mathrm{HSIC}(K_{i},K_{i})\cdot\mathrm{HSIC}(K_{j},K_{j})}}=\frac{\left|H_{j}^{\top}H_{i}\right|_{F}^{2}}{\left|H_{i}^{\top}H_{i}\right|_{F}\cdot\left|H_{j}^{\top}H_{j}\right|_{F}}.$$

> "The score bounded within $`[0,1]`$ indicates representational similarity as it approaches $`1`$. In our framework, a high CKA score between adjacent VLA layers signals minimal feature transformation, rendering those blocks prime candidates for structured pruning." (§3)
(한글 해설 — CKA 가 1에 가까우면 그 layer 는 표현을 거의 바꾸지 않으므로 제거 1순위 후보가 된다는 것이 CLP 의 판정 규칙입니다.)

### 학습 셋업 (CKA-Guided Pruning 절차)

![Figure 2 — π0·GR00T-N1.5 의 CKA 유사도 프로파일](https://arxiv.org/html/2606.20246/x1.png)

> "Figure 2: CKA similarity profiles across $`\pi_{0}`$ and GR00T-N1.5 sub-modules. The heatmaps illustrate pairwise representation alignment among transformer layers inside the VLM backbones, action heads, and DiT blocks. The extensive, contiguous plateaus of high similarity (dark red) across both model families signify minimal representational changes between successive layers, pinpointing candidate zones for structured pruning." (§4)
(한글 해설 — 두 모델 모두 큰 연속 dark-red 블록(high similarity plateau)이 존재한다는 것이 "deep VLA 에 구조적 중복이 만연하다"는 핵심 관찰의 시각적 증거입니다.)

prunable 모듈 $`\mathcal{M}`$ (VLM backbone 또는 action head)에 대해 layer 인덱스 $`\mathcal{I}_{\mathcal{M}}=\{1,\ldots,L_{\mathcal{M}}\}`$, pruning 예산 $`k_{\mathcal{M}}`$ 가 주어지면, 제거 집합 $`\mathcal{R}_{\mathcal{M}}`$ 을 골라 압축 정책 $`\pi_{\theta}^{\mathrm{pruned}}=\mathrm{RemoveLayers}(\pi_{\theta},\mathcal{R}_{\mathcal{M}})`$ 을 만듭니다.

> "Because all transformer blocks within $`\mathcal{M}`$ share identical hidden dimensions, layer removal simply reconnects the remaining predecessor and successor blocks. This design enables direct fine-tuning under the native training objective without requiring auxiliary routing parameters, distillation losses, or architectural modifications." (§4)
(한글 해설 — 같은 hidden 차원 덕에 layer 제거가 단순 재연결로 끝나고, 그래서 추가 파라미터·손실 없이 곧장 fine-tune 할 수 있다는 점이 CLP 의 "구조적 청결함"의 근거입니다.)

**(1) CKA 계산.** calibration set $`\mathcal{D}_{\mathrm{cal}}`$ 로 forward 를 흘려 layer activation $`\bar{H}^{\mathcal{M}}_{\ell}`$ 를 모으고 인접 layer 간 순차 중복도를 잰다.

$$s^{\mathcal{M}}_{\ell}=\mathrm{CKA}\left(\bar{H}^{\mathcal{M}}_{\ell-1},\bar{H}^{\mathcal{M}}_{\ell}\right),\quad\ell=2,\ldots,L_{\mathcal{M}}.$$

**(2) 블록 군집화.** 국소 표본 노이즈로 인한 고립 layer 제거를 막기 위해, $`s^{\mathcal{M}}_{\ell}\geq\tau`$ 인 연속 layer 를 contiguous block $`\mathcal{B}_{\mathcal{M}}=\{B_{1},\ldots,B_{Q}\}`$ 로 묶는다. 각 block $`B`$ 에서 첫 layer $`r(B)`$ 를 functional anchor 로 남기고 나머지를 후보 풀로 모은다.

$$\mathcal{P}_{\mathcal{M}}=\bigcup_{B\in\mathcal{B}_{\mathcal{M}}}\left(B\setminus\{r(B)\}\right).$$

**(3) TopK 제거.** $`|\mathcal{P}_{\mathcal{M}}|\geq k_{\mathcal{M}}`$ 가 되도록 τ 를 보정한 뒤, 후보 풀에서 가장 중복된 $`k_{\mathcal{M}}`$ 개를 제거 집합으로 확정한다.

$$\mathcal{R}_{\mathcal{M}}=\mathrm{TopK}_{\ell\in\mathcal{P}_{\mathcal{M}}}\left(s^{\mathcal{M}}_{\ell},k_{\mathcal{M}}\right).$$

이 절차(Algorithm 1)는 각 prunable 모듈에 독립적으로 적용되며, downstream 적응 이전에 깊이를 영구 truncate 하는 완전 정적 과정입니다 — 런타임 연산 오버헤드를 더하지 않습니다.

**실제 pruning 구성 (Table 5).** 모델별로 어느 모듈에서 몇 개 layer 를 떼었는지:

| 모델 | 모듈 | 원본 layer 수 | 제거 layer 수 | 제거 인덱스 |
|------|------|----|----|----|
| π0 | VLM and Action expert | 18 | 12 | 1, 2, 4, 6, 8, 9 |
| GR00T-N1.5 | VLM | 12 | 5 | 3, 4, 5, 6, 7, 8, 9 |
| GR00T-N1.5 | VL-self-attention | 4 | 3 | 2 |
| GR00T-N1.5 | DiT Action head | 16 | 8 | 1, 2, 4, 5, 6, 7, 10, 11 |
| SmolVLA | VLM and Action expert | 16 | 10 | 1, 2, 5, 6, 14, 15 |

> "For each identified block $`K`$, we retained only the first layer-hypothesizing that the initial layer is critical for processing and establishing the block's input representations - and pruned all subsequent layers within that same block." (§A.1)
(한글 해설 — block 내 첫 layer 보존 원칙(anchor)의 가설적 근거이며, Table 5 의 "제거 인덱스"가 그 원칙의 실제 산출물입니다.)

LIBERO 실험은 π0/GR00T-N1.5/SmolVLA 를 10% subset 으로 100k step·global batch 64 fine-tune, 과제당 50 episode·execution length 10 으로 평가했습니다.

---

## 📊 실험 설정과 결과

검증축은 4개 연구질문 — RQ1(압축 trade-off), RQ2(latent 거동·ablation), RQ3(SOTA 비교), RQ4(실세계 배치).

**효율 (Table 1, RTX 4070, LIBERO, 60000 step).**

| 모델 | 지표 | Base | CLP | 감소 |
|------|------|------|-----|------|
| π0 | Model Size | 3.5B | 2.7B | ↓22.9% |
| π0 | Trainable Params | 3.1B | 2.3B | ↓25.8% |
| π0 | Training Time (h) | 15.5 | 11.2 | ↓27.8% |
| π0 | GFLOPs | 3073 | 2196.5 | ↓28.5% |
| π0 | Inference (ms) | 211 | 152 | ↓27.9% |
| GR00T-N1.5 | Model Size | 2.7B | 2B | ↓25.9% |
| GR00T-N1.5 | Trainable Params | 1.07B | 0.75B | ↓30.1% |
| GR00T-N1.5 | Training Time (h) | 10.7 | 7.4 | ↓30.8% |
| GR00T-N1.5 | GFLOPs | 1010 | 512.4 | ↓49.3% |
| GR00T-N1.5 | Inference (ms) | 121 | 85 | ↓29.8% |
| SmolVLA | Model Size | 450M | 354M | ↓21.3% |
| SmolVLA | Trainable Params | 100M | 63M | ↓37% |
| SmolVLA | Training Time (h) | 24.75 | 8.83 | ↓64.3% |
| SmolVLA | GFLOPs | 598.4 | 536.1 | ↓10.41% |
| SmolVLA | Inference (ms) | 201 | 137 | ↓31.84% |

> "It can be seen that CLP demonstrates generalizability across structurally diverse VLA backbones, uniformly compressing total (i) model size by 21.3%–25.9% and (ii) cutting trainable parameters by 25.8%–37.0% from sub-billion to multi-billion scales as well as (iii) saving GFLOPs up to 50% while preserving equivalent success rate (Table 2)." (§5, Table 1)
(한글 해설 — sub-billion(SmolVLA)부터 multi-billion(π0)까지 backbone 규모와 무관하게 압축률이 균일하게 유지된다는 일반성 주장입니다.)

**RQ1 — 압축 trade-off.** Figure 3(a,b) 에서 π0(LIBERO)·GR00T-N1.5(RoboCasa)는 50% pruning ratio 까지 성능이 평탄합니다.

> "This capability allows us to cut total FLOPs by $`\times 1.39`$ and $`\times 1.42`$ with $`\pi_{0}`$ and GR00T-N1.5, respectively, with negligible loss in policy success rate." (§5)
(한글 해설 — 절반 깊이 제거가 성공률 손실 거의 없이 FLOPs 를 1.39–1.42× 줄인다는, 핵심 가설의 직접 검증입니다.)

![Figure 3 — 벤치마크·실세계 전반의 CLP 평가 분석](https://arxiv.org/html/2606.20246/x2.png)

> "Figure 3: Analysis of CLP evaluation across benchmarks and real-world tasks. (a) Success rate of $`\pi_{0}`$ on LIBERO with different layer pruning ratio; (b) Success rate of GR00T N1.5 on RoboCasa across pruning ratios; (c) Comparison with dynamic layer skipping method (MoLe-VLA [40]) vs ours; (d) Comparison of different pruning strategies on GR00T N1.5 across LIBERO benchmark; (e) Training time and success rate on real-world manipulation tasks; (f) PCA visualization of hidden states (state/future tokens and action tokens) for the Base model, CKA-guided pruned model with different pruning strategies." (§5)
(한글 해설 — pruning ratio 곡선(a,b), MoLe-VLA 대비(c), selection 전략 ablation(d), 실세계 학습시간(e), latent PCA(f)를 한 장에 모은 종합 분석 그림입니다.)

**RQ2 — selection 전략 ablation.** CKA 를 MSE / Cosine / random / keep-first 와 비교(Figure 3-d)했을 때 CKA 가 가장 안정적으로 unpruned baseline 에 근접합니다.

> "As shown in Figure 3-d, CKA consistently delivers the most stable performance across all benchmarks, closely matching the unpruned baseline while maintaining the highest average success rate. In contrast, localized similarity metrics and heuristic baselines can produce more unstable degradation, particularly on long-horizon and spatial tasks." (§5)
(한글 해설 — 국소 유사도(MSE/Cosine)·휴리스틱(random/keep-first)은 long-horizon·spatial 과제에서 불안정하게 무너지는 반면, CKA 만이 global topology 를 보존해 적응을 돕는다는 ablation 의 핵심 읽기입니다. — CKA 가 "유일하게 최적"이라는 RQ2 질문에 대한 답.)

**RQ3 — LIBERO training-free 비교 (Table 2).**

| Method | Spatial | Object | Goal | Long | Avg. SR (%) | Speedup |
|--------|---------|--------|------|------|-------------|---------|
| OpenVLA-OFT [14] | 97.6 | 96.5 | 97.9 | 94.5 | 96.6 | 1.00× |
| FastV [4] | 94.6 | 95.8 | 94.0 | 88.8 | 93.3 | 1.44× |
| DivPrune [1] | 92.4 | 91.2 | 89.0 | 84.8 | 89.4 | 1.46× |
| EfficientVLA [37] | 96.5 | 91.1 | 96.0 | 72.1 | 88.9 | 1.52× |
| ADP [27] | 97.6 | 98.4 | 97.4 | 84.2 | 94.4 | 1.35× |
| π0 | 94.6 | 98.2 | 95.4 | 90.0 | 94.6 | 1.00× |
| π0-SpecPrune-VLA [34] | 96.6 | 98.0 | 95.2 | 84.2 | 93.5 | 1.31× |
| **π0-CLP (Ours)** | 95.0 | 99.2 | 95.0 | 86.4 | 93.9 | 1.39× |
| GR00T-N1.5 | 90.8 | 98.4 | 95.4 | 91.0 | 93.9 | 1.00× |
| **GR00T-N1.5-CLP (Ours)** | 89.4 | 98.8 | 95.8 | 88.6 | 93.0 | 1.42× |
| SmolVLA | 71.8 | 92.2 | 87.4 | 57.2 | 77.15 | 1.00× |
| **SmolVLA-CLP (Ours)** | 75.6 | 93.0 | 81.6 | 56.2 | 76.75 | 1.47× |

> "On LIBERO (Table 2), CLP consistently achieves a superior efficiency–performance trade-off, delivering 1.39–1.47$`\times`$ speedups while maintaining near-baseline success rates across three modern VLA backbones." (§5, Table 2)
(한글 해설 — 세 backbone 모두에서 baseline 대비 평균 성공률 손실은 ≲1%p 수준이면서 1.39–1.47× 가속을 얻는다는 것이 RQ3 의 정량 결론입니다. 단, token-pruning baseline 과 달리 CLP 는 추론뿐 아니라 학습 비용까지 줄인다는 점을 강조.)

**저데이터·few-shot 우위.** LIBERO 10% 데이터에서 MoLe-VLA 와 비교(Figure 3-c):

> "Despite its simplicity, CLP achieves an 84.6% average success rate, surpassing both the full $`\pi_{0}`$ baseline (77.7%) and $`\pi_{0}`$-MoLe (79.7%), while reducing training time by 1.38$`\times`$." (§5)
(한글 해설 — 추가 학습 모듈을 붙이는 MoLe-VLA(79.7%)보다도 단순 정적 압축 CLP(84.6%)가 더 높다는, 정규화 효과의 직접 증거입니다.)

세부적으로 Table 6(LIBERO 10%): π0 77.7 / π0-MoLe 79.7 / **π0-CLP 84.6**, 학습시간 15.5 → 11.2h. Table 9(RoboCasa 30 demos avg): π0 base 15.6 / MoLe 17.6 / **CLP 18.0**, 학습시간 17.5 → 13.5h.

**SimplerEnv (Table 3, GR00T-N1.5, WidowX).** 학습시간 22.9 → 15.7h, Avg 16.57 → 20(절대 수치, 본문은 "16.6% → 20.0%"로 보고).

> "Finally, on (iii) SimplerEnv with GR00TN1.5 (Tab. 3), CLP improves the average success rate from 16.6% to 20.0% while shortening training time from 22.9 to 15.7 hours." (§5, Table 3)
(한글 해설 — 압축이 성능 유지가 아니라 향상으로 이어지는 또 다른 저데이터 사례입니다.)

**RQ4 — 실세계 (Table 4, GR00T-N1.5, 성공률 %).** 10개 과제 평균 73.5 → **75.9**, 학습은 최대 1.94× 가속.

| 과제 | GR00T-N1.5 | GR00T-N1.5-CLP |
|------|----|----|
| Groceries→Basket (UR10) | 90 | 89 |
| Open Kettle (UR10) | 100 | 95 |
| Close Kettle (UR10) | 100 | 100 |
| Serve Napkin (UR5) | 45 | 65 |
| Screwdriver→Basket (UR5) | 15 | 30 |
| Banana→Pot (ALOHA single) | 65 | 75 |
| Cube→Drawer (ALOHA single) | 75 | 60 |
| Block Stacking (ALOHA single) | 80 | 75 |
| Fold Shorts (ALOHA bimanual) | 90 | 95 |
| Fly Towel (ALOHA bimanual) | 75 | 70 |
| **Avg.** | **73.5** | **75.9** |

> "Despite reducing model depth, CLP maintains or improves overall task performance (Tab. 4), increasing the average success rate from 73.5% to 75.9% on GR00TN1.5 while outperforming the full model on several challenging tasks, including napkin serving (+20%), screwdriver placement (+15%), banana-to-pot transfer (+10%), and bimanual cloth folding (+5%)." (§5, Table 4)
(한글 해설 — 깊이를 줄였음에도 어려운 과제(napkin/screwdriver 등 저시연 100-demo 과제)에서 오히려 full model 을 능가하며, 일부 과제(Cube→Drawer, Block Stacking)는 소폭 하락해 trade-off 가 과제별로 갈림을 보여줍니다.)

> "We hypothesize that these gains arise from an implicit regularization effect: removing redundant layers reduces model capacity and discourages overfitting to task-specific noise." (§5)
(한글 해설 — 저데이터 향상의 메커니즘 가설로 implicit regularization 을 명시합니다 — 본 논문 결론의 핵심 주장.)

---

## ⚖️ 한계

- **(저자 명시) 전역 pruning 기준이 modality 별 token 동역학을 반영 못함** — CLP 는 action / state token 의 표현이 서로 다르다는 분석 결과에도 불구하고 단일 전역 기준으로 layer 를 제거한다. manipulation 에서 contact-rich action token 이 더 민감하다면, modality-agnostic 제거가 특정 과제에서 손실을 키울 수 있다(Table 4 의 Cube→Drawer 75→60 같은 하락이 그 징후로 읽힘).
- **(저자 명시) post-pretraining fine-tuning 단계에만 적용** — pretraining 단계 적용은 미탐구 open direction 으로 남겼다. 즉 "처음부터 얕게 pretrain" 가 가능한지는 검증되지 않았고, 어디까지나 기존 깊은 backbone 의 사후 압축이다.
- **(추론) τ·k 보정의 비용·민감도 불투명** — 본문은 "$`|\mathcal{P}_{\mathcal{M}}|\geq k_{\mathcal{M}}`$ 가 되도록 τ 를 보정"한다고만 하고 τ 의 구체 값·탐색 절차·민감도를 제시하지 않는다. Table 5 의 제거 인덱스가 사실상 hand-tuned 결과로 보이며, 새 backbone·과제에서 이 보정이 얼마나 자동화되는지가 재현의 관건이다.
- **(추론) "training-free" 의 범위 한정** — CLP 자체(layer 선택)는 training-free 지만, 압축 후 **반드시 downstream fine-tuning 으로 manifold 를 복원**해야 성능이 회복된다. 즉 "추가 학습 없이 바로 쓰는" 압축이 아니라 "더 싼 fine-tuning 을 가능케 하는 사전 압축"이며, fine-tuning 없는 zero-shot 압축 성능은 보고되지 않았다(PCA 상 pruning 직후 latent 공간 수축).
- **(추론) calibration set 분포 의존성 미검증** — CKA 는 calibration 표본에서 계산되는데, 표본이 deploy 분포와 다르면 redundant 판정이 틀릴 수 있다. calibration 크기·구성에 대한 ablation 이 본문에 없다.

---

## ♻️ 재현성

- **코드** — 본문/메타에 공개 GitHub 링크는 확인되지 않음. Project page `https://clpvla.github.io/` 만 명시(코드 공개 여부 불명).
- **데이터** — 모두 공개 자산 기반: 시뮬은 LIBERO / RoboCasa / SimplerEnv(Bridge), 실세계는 자체 수집 10개 과제(100–2800 시연, Table 7 에 episode·embodiment·view 수 상세). 자체 수집 실세계 데이터 공개 여부는 불명.
- **하드웨어** — 학습은 GR00T-N1.5/CLP 를 단일 NVIDIA H100(batch 32)에서, π0(RoboCasa)는 4×H100(batch 48). 추론 벤치는 RTX 4070. 실세계 임베디먼트는 UR10e / UR5 / single·bimanual ALOHA.
- **설정 명시도** — Algorithm 1 + Table 5(모델별 제거 layer 인덱스) + Table 7/8(과제별 시연·step·시간)으로 비교적 상세. 다만 τ 값과 calibration set 구성은 미명시.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P4(Pretraining for Data-Efficient Adaptation) — 주 연결.** CLP 는 D19(VLM backbone lineage & post-pretraining adaptation range)의 **adaptation range** 축에 직접 닿는다. 현재 v1 은 "VLM 전면 freeze + action expert 만 학습"인데, CLP 는 그 직교 축으로 "**backbone 과 action expert 양쪽의 깊이를 사전 정적 truncate**"를 제안한다 — freeze 가 *어느* layer 를 학습하느냐의 문제라면, CLP 는 *몇 개* layer 를 아예 들고 가느냐의 문제다. 또 D20(prior-preservation strategy)과 긴장/지지를 동시에 갖는다: layer 를 떼면 pretrained prior 의 일부를 영구 폐기하지만, 저데이터에서 implicit regularizer 로 작동해 ConSFT 류 conservative 적응과 같은 "과적합 억제" 목적을 다른 경로로 달성한다.
- **P1(Heterogeneous Body/Hand Action Expert) — 부 연결.** CLP 는 action head/expert 도 prune 대상으로 삼는다(π0 의 "VLM and Action expert" 통합 제거, GR00T 의 "DiT Action head" 8개 제거). 이는 D7(π backbone 통합/분할: v1 = π0 action expert slice + 양쪽 FT)의 전제 — action expert 깊이 — 가 사실 과잉일 수 있음을 시사한다. 우리의 shared trunk + split body/hand head(D1) 설계에서 trunk·head 깊이를 CKA 로 사전 진단하는 도구로 직접 재사용 가능하다.
- **Identity 지지/긴장.** Identity 의 "(4) data-efficient adaptation through the VLM pretraining recipe" 를 **지지**한다 — 저데이터 적응 효율을 pretraining 보존이 아닌 깊이 압축으로 얻는 보완 레버를 준다. 동시에 "pretrained prior 보존" 강조와는 **긴장**: CLP 는 prior 의 일부를 의도적으로 버린다.
- **경쟁자 함의.** P4 §5 Tracked Literature 의 ConSFT(D20/D21 Stage 3 conservative adaptation)와 같은 문제(저데이터 과적합/forgetting)를 정반대 수단(용량 축소 vs 보수적 weighting)으로 공략한다 — 직접 비교군. MoLe-VLA(P1 §5 off-pin)를 본 논문이 baseline 으로 직접 이기는 점도 주목.

---

## ✨ 핀 논문 대비 델타

- **vs ConSFT (P4 §5 핀, [arXiv:2605.08879]).** ConSFT 는 backbone 깊이를 유지한 채 importance-weighted conservative SFT 로 forgetting 을 ~20%p 줄인다(prior 보존형). CLP 는 정반대로 **깊이 자체를 줄여** 용량을 낮추고, 그 용량 감소가 저데이터 정규화로 작동해 forgetting 이 아니라 *과적합* 을 직접 공략한다 — "보존"이 아니라 "절제". 두 기법은 직교적이라 결합(압축된 backbone + conservative SFT) 가능성이 새 변수다.
- **vs π0 / GR00T N1 (P4 §5 핀, lineage anchor).** 핀 논문들이 "더 깊고 큰 backbone = 더 강함"을 전제로 lineage 를 정의했다면, CLP 는 그 lineage 의 30–50% layer 가 functionally redundant 임을 CKA 로 정량 입증한다 — lineage 선택(D19)의 "깊이" 차원을 처음으로 ablate 가능한 hyperparameter 로 만든다.
- **새로움의 핵심** — 기존 VLA 효율화(token pruning=추론만, dynamic routing=모듈 추가)와 달리, **fine-tuning 이전 단일 forward 정적 layer 제거**로 학습·추론·메모리를 동시에 줄이면서 보조 모듈이 0개라는 점. CKA 를 VLA depth-redundancy 진단에 적용한 것도 본 도메인에서 신규.

---

## ⚙️ 의사결정 함의

- **D19 adaptation-range 후보 추가** — 우리 v1 "VLM 전면 freeze + action expert 학습" 위에, fine-tuning **전** 단계로 `cka_layer_prune` 를 끼워 넣는 옵션을 검토한다. 구체 config: `prune.metric=cka`, `prune.tau=<보정값>`, `prune.budget_k` (모듈별), `prune.target_modules=[vlm_backbone, action_expert]`, `prune.keep_block_anchor=true`(block 첫 layer 보존). calibration 은 deploy episode 소량 1-pass.
- **저데이터 deploy 의 기본 레버** — 우리의 phase 1(in-hand cube, 소량 시연) 같은 데이터 희소 영역에서 CLP 를 **regularizer 로** 1순위 시도. 측정 지표: 동일 시연 수에서 success rate Δ, 그리고 학습 wall-clock(목표 ≥1.38× 단축).
- **P1 action expert 깊이 sizing** — Body/Hand split head(D1 hybrid) 설계 시 head 깊이를 임의 고정하지 말고, baseline π0 action expert 의 CKA 프로파일을 먼저 떠서(Table 5 의 GR00T DiT head 8/16 제거 선례) 초기 깊이 예산을 데이터로 정한다.
- **메트릭 추가** — adaptation 실험에 `cka_consecutive[ℓ]` 프로파일과 pruning ratio vs success-rate 곡선(Figure 3-a/b 형식)을 표준 진단으로 편입. PCA 기반 manifold-restoration(pruning 직후 vs FT 후) 시각화도 회복 여부 점검용으로.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 sanity check) CKA 프로파일이 dexterous/tactile 입력에서도 plateau 를 보이는가** — 논문의 redundancy 는 π0·GR00T 의 vision-language-dominant 입력에서 관찰됐다. 우리의 per-finger proprio-tactile(P2 D11) token 이 추가되면 layer 별 표현 변화가 더 활발해 plateau 가 사라질 수 있다. 자체 calibration 데이터로 CKA heatmap 한 장만 떠 보면 즉시 판별된다.
- **modality-agnostic 제거의 contact 손상** — 저자 스스로 action/state token 동역학 차이를 한계로 들었다. contact-rich in-hand 과제는 action token 표현 변화가 클 수 있어, 전역 CKA TopK 가 정작 중요한 contact 처리 layer 를 plateau 로 오인해 제거할 위험. Table 4 의 Cube→Drawer(75→60) 하락이 그 전조. → action head 는 pruning 예산을 보수적으로(또는 modality-aware 로) 두고 검증.
- **저시연 정규화 이득의 임베디먼트 의존성** — 본 논문 실세계 이득은 GR00T-N1.5·ALOHA/UR 계열에서 나왔다. 우리 Sharpa Hand(22-DOF, tactile) 처럼 action 차원이 크고 contact-민감한 임베디먼트에서 "용량 축소 = 정규화" 가 성립하는지는 미보장. cube-rotation 소량 시연으로 pruned vs full 의 success Δ 를 먼저 잰다.
- **fine-tuning 없는 즉시 사용 불가** — CLP 는 pruning 직후 latent 가 수축하므로 반드시 재적응이 필요하다. "minutes of deploy data" 를 노리는 우리 Genesis-style 목표에서, 재적응에 드는 추가 데이터/step 이 압축 이득을 상쇄하지 않는지(net 효율)를 학습 시간·시연 수 양축으로 확인.
- **τ 보정의 자동화 실패** — 새 backbone(π0.5 / 우리 split-head 변형)에서 Table 5 처럼 깔끔한 block 경계가 안 나오면 τ·k 가 hand-tuning 으로 흐른다. 재현 1단계로 우리 backbone 의 CKA 분포가 명확한 bimodal(plateau vs transition)인지부터 확인.

---

## 💡 컨텍스트 제안

- **P4 §5 Tracked Literature 후보(핀 아님, methodology base 행)** — 본 논문을 D19(adaptation range)·D20(prior-preservation 대안: 보존이 아닌 절제) 비교축으로 "methodology base (non-pinned)" 표에 추가 검토 제안. ConSFT(보존형)와 직교쌍을 이루어 D20 의 설계 공간을 넓힌다. (핀 8개 cap 은 유지 — 핀 교체까지는 불요.)
- **D19 deferred candidate 명시** — "post-pretraining adaptation range" 의 deferred 후보에 `pre-finetuning structural layer pruning (CKA-guided)` 을 한 줄 추가 제안. 현재 freeze/PEFT/full 축과 직교하는 "깊이" 축.
- 그 외 Decision 이동/핀 교체 트리거는 현 시점 근거 부족 — **보류**. (context/ 파일은 수정하지 않음.)

> 💡 base 매핑은 `/implement-design analysis/2606.20246/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
