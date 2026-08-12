# Paper Analysis — CAAT: Contact-Aware Attention Scaling and Tactile Masking for Data-Efficient Contact-Rich Manipulation

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | CAAT: Contact-Aware Attention Scaling and Tactile Masking for Data-Efficient Contact-Rich Manipulation |
| 저자 | Jiaming Jiang, Yuzhe Huang, Hao Liang, Pei Lin, Shengcheng Luo, Fanrong Dong, Jiaping Wu, Chenxi Xiao, Wanlin Li, Ziyuan Jiao |
| 링크 | [arXiv:2608.01102](https://arxiv.org/abs/2608.01102) · [Website](https://mrjiangjm.github.io/caat/) |
| 발행일 / 버전 | 2026-08-02 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-08-12 |
| 관련 Pillar | P2, P1, P0 |
| 태그 | tactile, vla-arch |

<!-- 본문·그림은 https://arxiv.org/html/2608.01102 에서 전문 확보(HTTP 200).
     프로젝트 페이지 링크는 논문 초록·본문에 verbatim 으로 실린 URL 이지만,
     이 실행 환경의 네트워크 정책이 해당 호스트를 차단해 해상(resolve) 여부를
     직접 확인하지 못했습니다. 실패 기록 verbatim:
       curl -sSL -o /dev/null -w '%{http_code}\n' "https://mrjiangjm.github.io/caat/"
       curl: (56) CONNECT tunnel failed, response 403
     GitHub / HuggingFace 링크는 논문 어디에도 없으므로 기재하지 않습니다. -->

---

## 🧭 한 줄 요약 (TL;DR)

접촉(contact) 여부라는 이진 상태를 명시적 prior 로 삼아, Transformer 정책의 **어텐션 readout 단계**에서 시각·촉각 기여도를 고정 계수로 갈아 끼우고(Contact-Aware Attention Scaling), 동시에 비접촉 기준 프레임과 달라지지 않은 촉각 패치 토큰을 지워버리는(Dynamic Tactile Masking) 경량 플러그인 프레임워크입니다. 액션 디코더를 건드리지 않고 ACT / Diffusion Policy / π0 에 그대로 얹히며, 시뮬레이션에서 직접 concat 대비 +18.0%p, 실제 로봇 3개 백본 평균 60.0% 성공률로 최강 baseline 대비 +21.1%p 를 보고합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 접촉 집약적(contact-rich) 조작에서 시각과 촉각의 **모달리티 배분(modality allocation)** 을 언제·얼마나 할지 결정하는 문제입니다. 자유 공간 이동 구간에서는 시각이, 접촉 구간에서는 촉각이 정보량을 지배하는데 표준 정책은 이 구분을 갖고 있지 않습니다.
- **기존 접근의 한계 (concat)** — Transformer 정책의 관행은 촉각을 추가 토큰으로 만들어 시각·고유수용(proprioception) 토큰과 그냥 이어 붙이고 self-attention 이 알아서 융합을 배우게 두는 것입니다. 표현력은 높지만 "촉각이 언제 유의미한가"와 "어떻게 섞을 것인가"를 모두 시연에서 추론해야 합니다.
- **기존 접근의 한계 (gating)** — 학습 가능한 게이트·적응형 융합은 이 문제를 완화하지만, 그 게이트 자체를 동일한 시연에서 배워야 합니다. 접촉 사건이 궤적의 일부에 불과해 신호가 희소하므로 대규모 데이터를 요구하고 저데이터 구간에서는 오히려 성능을 떨어뜨립니다.
- **본 논문의 가설** — 접촉/비접촉 구분은 **비교적 쉽게 판별되는 상태**이므로, 모달리티 배분을 시연에서 배우는 대신 접촉 상태에 명시적으로 조건화하면 된다는 것입니다. 즉 학습해야 할 것을 prior 로 대체해 학습 부담 자체를 줄입니다.
- **왜 지금 중요한가** — 촉각 신호는 궤적 전체에서 희소하고, 실제 로봇 시연 수집 단가는 높습니다. 저데이터 구간에서 촉각을 살리는 구조적 유도 편향(inductive bias)이 없으면 촉각 센서를 달아도 성능이 오르지 않는다는 것이 이 논문의 출발점입니다.

---

## 🧩 핵심 기여

- **단계 의존적 촉각 희소성의 문제화** — 촉각 피드백이 궤적 내에서 특정 국면에만 몰려 있다는 성질을 접촉 집약적 조작 학습의 핵심 난점으로 지목하고, 접촉 인식형 비주오택타일(visuotactile) 융합의 필요성을 논거로 세웁니다.
- **Contact-Aware Attention Scaling (CAAS)** — 공동 self-attention 이후에 액션 쿼리가 모달리티별 토큰 부분집합에 **따로** cross-attention 하여 readout 을 만들고, 접촉 상태로 그 readout 들을 고정 계수로 가중합합니다.
- **Dynamic Tactile Masking (DTM)** — 현재 촉각 패치 토큰을 비접촉 기준 토큰과 코사인 유사도로 비교해, 변하지 않은 배경 토큰을 0 으로 눌러 접촉 유발 변형만 남깁니다.
- **플러그인 호환성 검증** — 액션 디코더를 수정하지 않고 ACT, Diffusion Policy (DP), π0 세 백본에 동일하게 적용해, 시뮬레이션(UniVTAC 5과제)과 실제 로봇(3과제)에서 일관된 향상을 보입니다.
- **동형(isomorphic) 촉각 UMI 장치** — 사람이 손으로 잡고 시연을 수집하는 2지 촉각 그리퍼를 직접 설계·제작하고, 배포 시 동일 하드웨어를 로봇에 장착해 시연-실행 간 embodiment 격차를 줄입니다.

---

## 🔑 기술 키워드

- **Contact-Aware Attention Scaling** — 접촉 인식 어텐션 스케일링. 액션 쿼리가 뽑아낸 모달리티별 요약본을 접촉 여부에 따라 볼륨 노브처럼 올리고 내리는 장치입니다.
- **Dynamic Tactile Masking** — 동적 촉각 마스킹. "누르기 전 사진"과 지금 사진을 겹쳐 놓고 달라진 자리만 남기는 스팟 더 디퍼런스에 해당합니다.
- **Modality-Specific Attention Readout** — 공동 self-attention 을 통과한 토큰을 원래 모달리티별로 되쪼갠 뒤, 액션 쿼리가 각 부분집합에만 따로 어텐션해 만든 모달리티별 요약 벡터.
- **Contact State Estimator** — 현재 촉각 이미지와 비접촉 기준 이미지의 차분을 입력받아 접촉 확률을 뱉는 경량 CNN–MLP 이진 분류기. 임계값 0.5 로 접촉 여부를 확정합니다.
- **Non-Contact Reference** — 에피소드 첫 타임스텝의 촉각 이미지. 마스킹과 접촉 판정 모두가 이 "아무것도 안 만진 상태" 기준선과의 차이로 정의됩니다.
- **ViT-VQGAN Tactile Encoder** — 여러 센서 종류의 촉각 이미지 수십만 장으로 사전학습한 ViT 인코더. 학습 후 동결되며 양자화기·디코더는 버리고 연속 공간 토큰만 씁니다.
- **Fixed Numerical Scaling** — 스케일 계수를 학습하지 않고 비접촉 `(0.7, 0.3)` · 접촉 `(0.3, 0.7)` 로 못 박은 변형. 본 논문에서 이진·학습형 변형을 모두 앞섭니다.
- **Visuo-Tactile UMI Gripper** — UMI 패러다임에서 착안한 수동 조작형 2지 촉각 그리퍼. 시연 수집기와 로봇 말단장치가 같은 형상이라 embodiment 격차가 줄어듭니다.
- **UniVTAC Benchmark** — 비주오택타일 조작의 데이터 생성·학습·벤치마킹 통합 시뮬레이션 플랫폼. 본 논문 시뮬레이션 평가 5과제의 출처입니다.

---

## 🔬 방법론

### 직관

CAAT 의 문제의식은 단순합니다. 로봇이 물체를 향해 다가가는 동안 촉각 센서에는 아무 일도 일어나지 않습니다. 손가락이 닿는 순간부터 비로소 촉각이 말을 하기 시작합니다. 그런데 표준 Transformer 정책은 이 사실을 모른 채, 궤적 전체에 걸쳐 촉각 토큰을 시각 토큰 옆에 나란히 놓고 "알아서 배우라"고 맡깁니다. 접촉 구간이 궤적의 일부에 불과하므로, 정책은 대부분의 학습 스텝에서 아무 정보도 없는 촉각 토큰을 보게 되고 정작 중요한 접촉 순간의 신호는 그 홍수에 묻힙니다.

학습형 게이트는 이 문제를 "모달리티 가중치를 배우자"로 바꿔 놓지만, 배울 재료가 되는 접촉 사건이 애초에 희소하다는 사실은 그대로입니다. 저자들의 관점 전환은 여기서 나옵니다 — 접촉 중인지 아닌지는 촉각 이미지가 기준 프레임 대비 얼마나 바뀌었는지만 봐도 꽤 쉽게 알 수 있는 상태입니다. 그렇다면 그것을 학습 대상으로 둘 이유가 없습니다. 접촉 여부를 별도의 가벼운 분류기로 뽑아 놓고, 그 값에 따라 시각과 촉각의 기여도를 **사람이 정한 숫자로** 갈아 끼우면 됩니다.

구체적으로는 두 개의 장치가 붙습니다. 첫째, 촉각 이미지 안에서도 정보가 있는 자리는 접촉으로 눌린 국소 영역뿐이므로, 에피소드 첫 프레임(아무것도 안 만진 상태)과 패치 단위로 비교해 안 변한 패치는 아예 0 으로 만들어 버립니다. 촉각 센서의 고정 무늬·조명 같은 배경을 정책이 학습으로 걸러낼 필요를 없애 주는 장치입니다. 둘째, 모든 토큰을 함께 self-attention 에 통과시킨 뒤 — 여기서 모달리티 간 상호작용은 그대로 학습됩니다 — 마지막 readout 단계에서만 시각/촉각/고유수용 요약본을 따로 뽑고, 접촉 전이면 시각에 0.7, 접촉 중이면 촉각에 0.7 을 주어 합칩니다.

중요한 설계 선택은 이 prior 를 **표현 학습이 아니라 읽어내기(readout) 지점에** 걸었다는 점입니다. 토큰을 미리 눌러 놓고 공동 어텐션에 넣으면 모달리티 간 상호작용 자체가 왜곡되지만, 공동 어텐션은 그대로 두고 최종 요약본만 가중하면 표현력은 유지한 채 배분 규칙만 주입됩니다. 그 결과 액션 디코더는 손댈 필요가 없고, ACT처럼 chunk 를 뱉는 정책이든 DP처럼 denoising 을 도는 정책이든 π0 같은 플로우 매칭 VLA 든 앞단만 갈아 끼우면 됩니다.

### 아키텍처

![Figure 1 — CAAT pipeline overview](https://arxiv.org/html/2608.01102/fig/pipeline.png)

> "Figure 1: Overview of CAAT. CAAT introduces contact-aware priors into Transformer-based visuo-tactile action prediction. Visual observations and robot states are encoded as modality-specific tokens, while tactile images are converted into patch tokens using a pretrained tactile encoder. CAAT first applies Dynamic Tactile Masking, which compares the current tactile tokens with a non-contact reference and suppresses unchanged background regions while retaining tokens that capture contact-induced deformations. The visual, masked tactile, and state tokens are then concatenated and processed by Transformer layers. For action decoding, CAAT computes modality-specific attention readouts and scales the visual and tactile contributions according to the estimated contact state: visual features are emphasized before contact, whereas tactile features are emphasized during contact. The resulting multimodal representation is passed to the action decoder to predict a sequence of future actions." (§3.1)
(한글 해설 — 촉각 인코딩 → DTM → 공동 Transformer → 모달리티별 readout → 접촉 조건부 스케일링 → 기존 액션 디코더로 이어지는 전체 경로가 한 장에 담겨 있으며, 디코더가 손대지 않은 회색 상자로 남아 있다는 점이 이 논문의 플러그인 주장을 시각화합니다.)

**문제 정식화.** 관측 이력에서 미래 액션 구간을 예측하는 표준 시퀀스 예측 문제로 둡니다. 시각 입력 $`I_{t-k:t}`$ , 촉각 입력 $`T_{t-k:t}`$ , 그리고 고유수용·과제 정보 같은 부가 조건 변수 $`\Upsilon`$ 이 들어가고 (식 1),

$$a_{t:t+H}=\pi_{\theta}\left(I_{t-k:t},T_{t-k:t},\Upsilon\right),$$

여기서 $`k`$ 는 관측 이력 길이, $`H`$ 는 액션 예측 지평(horizon)입니다. 이 정식화 자체는 새로울 것이 없고, CAAT 가 손대는 지점은 $`\pi_{\theta}`$ 내부의 융합 경로뿐입니다.

> "CAAT imposes this prior at the attention readout while preserving expressive cross-modal representation learning." (§1)
(한글 해설 — 이 한 문장이 설계 의도를 못 박습니다. prior 를 토큰 입력단이 아니라 readout 단에 거는 이유는, 공동 self-attention 이 학습하는 교차 모달 표현력을 훼손하지 않으면서 배분 규칙만 외부에서 주입하기 위함입니다. 뒤에 나오는 학습형 게이팅 baseline 과의 차이도 정확히 이 지점입니다.)

**촉각 토큰화.** 촉각 인코더 $`E_{\tau}`$ 가 촉각 이미지를 패치 토큰 열로 변환합니다 (식 2):

$$X_{t}^{\tau}=E_{\tau}(T_{t}),\quad X_{t}^{\tau}=[x_{t,1}^{\tau},\dots,x_{t,N}^{\tau}]\in\mathbb{R}^{N\times d},$$

$`N`$ 은 촉각 패치 수, $`d`$ 는 토큰 차원입니다. 구현상 $`E_{\tau}`$ 는 사전학습된 촉각 ViT 인코더입니다.

**Dynamic Tactile Masking (DTM).** 사전학습 인코더가 좋은 표현을 준다 해도, 촉각 이미지 전체를 그대로 인코딩하면 정적인 비접촉 배경이 함께 실려 옵니다. DTM 은 그 배경 패치를 죽입니다.

> "This operation injects a spatial prior: informative tactile evidence is concentrated in regions that change relative to the non-contact state, rather than being distributed across the entire tactile image." (§3.2)
(한글 해설 — 여기서 주입되는 것은 *공간* prior 입니다. 뒤의 CAAS 가 시간 축에서 "언제" 촉각을 볼지 정한다면, DTM 은 촉각 이미지 내부에서 "어디"를 볼지 정합니다. 두 장치의 역할 분담이 논문 후반 ablation 의 결론과 정확히 일치합니다.)

같은 인코더로 현재 관측과 기준 관측을 함께 인코딩한 뒤 (식 3),

$$X_{t}^{\tau}=E_{\tau}(T_{t}),\quad X_{0}^{\tau}=E_{\tau}(T_{0}).$$

패치별 코사인 유사도를 계산합니다 (식 4):

$$c_{t,n}=\frac{x_{t,n}^{\tau}\cdot x_{0,n}^{\tau}}{\|x_{t,n}^{\tau}\|\,\|x_{0,n}^{\tau}\|},\quad n=1,\dots,N.$$

이 유사도를 임계값 $`\rho`$ 로 이진 마스크로 바꿉니다 (식 5):

```math
M_{t,n}=\begin{cases}0,&c_{t,n}\geq\rho,\\
1,&c_{t,n}<\rho,\end{cases}
```

기준과 **닮은** 패치가 0 (억제), **달라진** 패치가 1 (보존)이라는 극성에 주의해야 합니다. 마스킹된 토큰은 곱셈으로 얻습니다 (식 6·7):

$$\tilde{x}_{t,n}^{\tau}=M_{t,n}x_{t,n}^{\tau}.$$

$$\tilde{X}_{t}^{\tau}=[\tilde{x}_{t,1}^{\tau},\dots,\tilde{x}_{t,N}^{\tau}],$$

즉 토큰을 시퀀스에서 **제거**하는 것이 아니라 영 벡터로 **치환**합니다. 토큰 개수와 위치는 그대로 유지되므로 백본의 시퀀스 길이 가정은 건드리지 않습니다.

**공동 self-attention 과 모달리티 재분할.** 시각 토큰 $`X_{t}^{v}`$ , 마스킹된 촉각 토큰 $`\tilde{X}_{t}^{\tau}`$ , 고유수용 토큰 $`X_{t}^{\Upsilon}`$ , 액션 토큰 $`{X}_{t}^{a}`$ 을 모두 이어 붙여 self-attention 에 통과시키고 (식 8), 결과를 원래 모달리티 경계대로 다시 쪼갭니다 (식 9):

$$X_{t}=[X_{t}^{v},\tilde{X}_{t}^{\tau},X_{t}^{\Upsilon},{X}_{t}^{a}],\quad H_{t}=\mathrm{SelfAttn}(X_{t}).$$

$$H_{t}=[H_{t}^{v},H_{t}^{\tau},H_{t}^{\Upsilon},H_{t}^{a}],$$

이 단계에서 교차 모달 상호작용은 아무 제약 없이 학습됩니다 — CAAT 의 prior 는 아직 개입하지 않습니다.

**모달리티별 readout.** 액션 쿼리 $`Q_{t}^{a}=H_{t}^{a}W_{Q}`$ 를 만들고, 각 모달리티 $`m\in\{v,\tau,\Upsilon\}`$ 의 토큰을 키·밸류로 투영한 뒤 (식 10), 모달리티마다 **따로** 어텐션을 계산합니다 (식 11·12):

$$K_{t}^{m}=H_{t}^{m}W_{K},\quad V_{t}^{m}=H_{t}^{m}W_{V}.$$

$$w_{t}^{m}=\mathrm{softmax}\left(\frac{Q_{t}^{a}(K_{t}^{m})^{\top}}{\sqrt{d_{h}}}\right),$$

$$r_{t}^{m}=w_{t}^{m}V_{t}^{m},\quad m\in\{v,\tau,\Upsilon\}.$$

softmax 를 모달리티별로 나누어 거는 것이 핵심입니다. 하나의 softmax 로 전 토큰을 정규화하면 시각 토큰 수가 촉각 토큰 수를 압도할 때 촉각 기여도가 구조적으로 눌리지만, 분리하면 각 모달리티 내부에서 정규화된 요약본이 나오고 그 뒤에 외부 계수로 상대 비중을 정할 수 있게 됩니다.

**접촉 조건부 스케일링.** 추정된 접촉 상태 $`z_{t}`$ ( $`z_{t}=0`$ 비접촉, $`z_{t}=1`$ 접촉)로 세 readout 을 가중합합니다 (식 13):

$$\hat{r}_{t}=\gamma_{v}(z_{t})r_{t}^{v}+\gamma_{\tau}(z_{t})r_{t}^{\tau}+r_{t}^{\Upsilon}.$$

고유수용 readout $`r_{t}^{\Upsilon}`$ 에는 계수가 붙지 않고 그대로 더해진다는 점에 유의해야 합니다 — 스케일링 대상은 시각·촉각 두 축뿐입니다.

> "The scaling factors $`\gamma(\cdot)`$ are user-specified functions that encode the desired phase-dependent modality preference." (§3.3)
(한글 해설 — 이 계수가 학습 파라미터가 아니라 **사용자 지정 함수**라는 선언이 논문의 성격을 규정합니다. 데이터에서 배우는 대신 사람이 아는 것을 그냥 적어 넣는 방식이고, 실험에서 이 선택이 학습형보다 나았다는 결과가 이어집니다.)

계수가 만족해야 할 유일한 조건은 단계별 선호의 방향성입니다 (식 14):

$$\gamma_{v}(0)>\gamma_{\tau}(0),\quad\gamma_{\tau}(1)>\gamma_{v}(1).$$

**접촉 상태 추정.** $`z_{t}`$ 는 별도 분류기가 만듭니다.

> "The contact phase is estimated by a lightweight CNN–MLP binary classifier operating on the difference between the current tactile observation and a non-contact reference observation." (§3.3)
(한글 해설 — 접촉 판정 역시 DTM 과 같은 "기준 대비 차분" 원리를 재사용합니다. 즉 이 프레임워크는 비접촉 기준 프레임 하나에 두 장치를 모두 걸고 있으며, 그 기준이 흔들리면 둘이 동시에 흔들린다는 구조적 결합이 여기서 생깁니다.)

차분 이미지 (식 15), 이진 교차 엔트로피 손실 (식 16), 임계값 판정 (식 17)은 다음과 같습니다:

$$D_{t}=\left|T_{t}-T_{\mathrm{ref}}\right|,$$

$$\mathcal{L}_{\mathrm{contact}}=-y_{t}\log p_{t}-(1-y_{t})\log(1-p_{t}).$$

$$z_{t}=\mathbb{I}\left(p_{t}>0.5\right).$$

여기서 $`T_{\mathrm{ref}}`$ 는 상호작용 시작 전에 기록되고, $`y_{t}\in\{0,1\}`$ 는 정답 접촉 레이블, $`p_{t}\in[0,1]`$ 는 예측 접촉 확률입니다. 학습·추론 모두 $`p_{t}>0.5`$ 를 접촉으로 봅니다.

**디코더 연결.** 스케일된 표현이 그대로 기존 정책의 액션 디코더로 들어갑니다 (식 18):

$$a_{t:t+H}=D_{\theta}(\hat{r}_{t}),$$

$`D_{\theta}`$ 는 선택한 Transformer 정책 백본의 액션 디코더입니다.

> "Moreover, CAAT is naturally modular and can be integrated into existing Transformer-based policies without modifying their action decoders." (§1)
(한글 해설 — 디코더 불변이라는 이 성질이 ACT·DP·π0 3종 백본 검증을 가능하게 한 실질적 근거이자, 동시에 실험에서 백본별 절대 성능 차이가 CAAT 의 효과와 분리되어 읽히게 하는 장치입니다.)

다만 논문 스스로 주입 경로가 백본마다 달라진다고 명시합니다 — "For clarity, we present CAAT using a generic token-based formulation. The exact representation and injection pathway of proprioceptive, latent, and action-conditioning features depend on the underlying policy architecture." (§3.3). 즉 위 수식은 일반형이고, π0 같은 플로우 매칭 VLA 에 정확히 어느 지점으로 꽂았는지는 본문에 구체적으로 서술되지 않습니다.

### 학습 목표 / 손실

CAAT 자체는 새로운 정책 손실을 도입하지 않습니다. 정책은 각 백본의 고유 학습 목표(ACT / DP / π0 의 native objective)를 그대로 쓰고, CAAT 가 추가하는 학습 신호는 접촉 분류기의 이진 교차 엔트로피 $`\mathcal{L}_{\mathrm{contact}}`$ (식 16) 하나뿐입니다. 게다가 실험 설정에서 이 분류기는 **동결(frozen)** 되어 사용되므로, 정책 학습 시점에는 사실상 손실 항이 추가되지 않습니다.

스케일 계수 $`\gamma`$ 는 세 가지 변형으로 비교됩니다 — 이진 스케일링 $`(0,1)`$ , 학습형 스케일링, 고정 수치 스케일링 $`(0.3,0.7)`$ . 학습형 변형만 파라미터를 가지며, 상태 의존 시각 계수를 시그모이드로 두고 (식 20·21·22):

$$\gamma_{v}^{\mathrm{L}}(z_{t})=\sigma\left(g_{z_{t}}\right),$$

$$\gamma_{\tau}^{\mathrm{L}}(z_{t})=1-\gamma_{v}^{\mathrm{L}}(z_{t}).$$

$$\hat{r}_{t}=\gamma_{v}^{\mathrm{L}}(z_{t})r_{t}^{v}+\left[1-\gamma_{v}^{\mathrm{L}}(z_{t})\right]r_{t}^{\tau}+r_{t}^{\Upsilon}.$$

$`g_{z_{t}}`$ 는 접촉 상태 $`z_{t}`$ 마다 하나씩 있는 학습 파라미터입니다. 즉 학습형 변형은 상태별로 계수 **두 개**만 배우는, 극도로 저차원인 학습입니다.

비교 대상인 학습형 게이팅 baseline 은 구조적으로 다른 자리에 붙습니다 (식 19):

$$\bar{X}_{t}^{v}=\alpha X_{t}^{v},\qquad\bar{X}_{t}^{\tau}=(1-\alpha)\widetilde{X}_{t}^{\tau},$$

$`\alpha=\sigma(a)`$ 이고 $`a`$ 는 제약 없는 학습 스칼라입니다.

> "The same learned coefficient is shared across all time steps and is not conditioned on the estimated contact state." (§C)
(한글 해설 — 이 문장이 baseline 의 성격을 규정합니다. 게이팅 baseline 은 시간 불변 스칼라 하나를 공동 self-attention **이전**에 토큰에 곱하는 반면, CAAT 는 접촉 상태 의존 계수를 self-attention **이후** readout 에 곱합니다. 논문이 주장하는 우위의 두 축 — 조건화 여부와 적용 위치 — 이 여기서 동시에 갈립니다.)

### 학습 셋업

**촉각 인코더.** $`256\times 256`$ 촉각 이미지를 받아 $`32\times 32`$ 공간 특징 격자, 즉 $`1{,}024`$ 개 토큰을 만들고, 정책 학습에 그만한 해상도가 필요 없으므로 $`2\times 2`$ 평균 풀링으로 $`16\times 16`$ , 최종 $`N=256`$ 토큰으로 줄입니다. 사전학습 코퍼스는 GelSight · DIGIT · 9DTact 등 공개 데이터셋에서 모은 수십만 장 규모이며, ViT-VQGAN 프레임워크로 재구성·지각·적대적 목적을 함께 써서 학습합니다.

> "After pretraining, the encoder is frozen and requires no task-specific adaptation." (§B)
(한글 해설 — 인코더 동결은 저데이터 주장과 직결됩니다. 과제별 촉각 표현을 다시 학습하지 않으므로 시연 예산이 정책 학습에만 쓰이지만, 반대로 코퍼스에 없던 센서 종류에 대해 표현이 얼마나 버티는지는 이 설정에서 검증되지 않습니다. 정책 학습·DTM 모두 양자화 이전의 연속 공간 토큰을 씁니다.)

**정책 백본.** ACT 는 인코더 4층 · 디코더 7층 · hidden 512 · 액션 chunk 50. DP 는 denoising 100 스텝 · 8층 denoising 망 · 예측 지평 10. π0 는 사전학습 체크포인트를 받아 CAAT 구성요소와 함께 fine-tune 합니다.

**최적화.** 전 모델 batch size 64, AdamW, 고정 학습률 $`1\times 10^{-5}`$ , weight decay $`1\times 10^{-4}`$ . π0 는 LoRA 로 NVIDIA A100 80GB 2장에서 global batch 64 로 fine-tune 하고, ACT 와 DP 는 각각 A100 80GB 1장에서 학습합니다.

**CAAT 하이퍼파라미터.** 비접촉 구간 $`(\gamma_{v},\gamma_{\tau})=(0.7,0.3)`$ , 접촉 구간 $`(\gamma_{v},\gamma_{\tau})=(0.3,0.7)`$ . 접촉 추정기는 동결된 CNN–MLP 이진 분류기이며 임계값 0.5. DTM 코사인 유사도 임계값 $`\rho=0.8`$ . 비접촉 기준 프레임은 각 에피소드의 첫 타임스텝 촉각 이미지입니다.

**데이터.** 실제 과제는 UMI 착안 수동 장치로 과제당 성공 시연 150개를 수집하고, 시뮬레이션은 UniVTAC 표준 데이터셋(역시 과제당 150개)을 씁니다. 모든 비교 방법에 DTM 을 동일하게 적용해 통제합니다.

![Figure 5 — tactile UMI gripper hardware](https://arxiv.org/html/2608.01102/fig/tactile_umi.png)

> "Figure 5: Hardware design of the tactile gripper. The dexterous two-finger tactile device is used for both human-operated demonstration collection and robot policy deployment. Each fingertip is equipped with a PPTac tactile sensor, and five Dynamixel motors control the opening/closing and lateral motion of the fingers. During data collection, a Vive Tracker mounted on the gripper records its pose and motion. During deployment, the tracker is removed, and the robot executes the policy based on the end-effector pose." (§A)
(한글 해설 — 시연 수집기와 로봇 말단장치가 같은 형상·같은 촉각 구성을 공유한다는 하드웨어 조건이, 이 논문의 실제 로봇 수치가 human-to-robot 전이 손실 없이 읽히는 전제입니다. Dynamixel XL330 5개로 개폐와 측방 운동을 제어합니다.)

**평가 프로토콜.** 시뮬레이션은 과제당 100개 랜덤 시드에 걸쳐 100 rollout 을 돌려 평균 성공률을 보고하고, 실제 로봇은 체크포인트당 과제별 20회를 물체 자세를 무작위화해 수행한 뒤 20회 평균을 보고합니다.

---

## 📊 실험 설정과 결과

평가는 두 축입니다 — UniVTAC 시뮬레이션 5과제(백본 고정, 융합 전략 비교)와 실제 로봇 3과제(백본 3종 × 융합 3종). 두 축 모두 과제당 시연 150개, 모든 방법에 DTM 적용이라는 통제 조건을 공유합니다.

### 시뮬레이션 — 융합 전략 비교 (UniVTAC, ACT 백본)

| Method | Lift Bottle | Pull Out Key | Lift Can | Put Bottle in Shelf | Insert Tube | Average |
|---|---|---|---|---|---|---|
| ACT+DTM | 20% | 70% | 59% | 14% | 95% | 51.6% |
| Gate ACT+DTM | 65% | 75% | 57% | 11% | 90% | 59.6% |
| Ours (Binary) | 56% | 46% | 50% | 16% | 91% | 51.8% |
| Ours (Learnable) | 56% | 42% | 51% | 10% | 94% | 50.6% |
| Ours (Numerical) | 71% | 80% | 63% | 38% | 96% | 69.6% |

> "CAAT with fixed numerical scaling achieves the best performance on all five tasks, attaining an average success rate of $`69.6\%`$." (§4.2, Table 1)
(한글 해설 — 5과제 전부에서 최고라는 진술이 중요합니다. 평균만 이긴 것이 아니라 과제별로도 지지 않았다는 뜻이라, 특정 과제에서의 큰 이득이 평균을 끌어올린 형태가 아닙니다.)

> "It outperforms the direct-concatenation baseline (ACT + DTM) and the learnable-gating baseline (Gated ACT + DTM) by $`18.0`$ and $`10.0`$ percentage points, respectively." (§4.2, Table 1)
(한글 해설 — 초록의 두 대표 수치가 여기서 나옵니다. 비교군 모두에 DTM 이 적용된 상태이므로 이 18.0%p 와 10.0%p 는 **어텐션 스케일링 단독의 몫**으로 읽어야 합니다.)

과제별로 뜯어보면 이득의 분포가 고르지 않습니다. ACT+DTM 대비 향상은 Lift Bottle 과 Put Bottle in Shelf 에서 각각 51%p 와 24%p 로 두드러지고, Gate ACT+DTM 대비 최대 이득은 Put Bottle in Shelf 의 27%p 입니다. 반대로 Insert Tube 는 모든 방법이 90% 이상이라 변별력이 없고(95 → 96), Lift Can 도 57–63% 구간에 몰려 있습니다. 즉 이 벤치마크에서 융합 전략이 실제로 갈리는 과제는 사실상 Lift Bottle · Pull Out Key · Put Bottle in Shelf 세 개입니다.

### 스케일링 함수 변형 비교

| 변형 | $`\gamma`$ 정의 | Sim. Average |
|---|---|---|
| Ours (Binary) | $`(0,1)`$ | 51.8% |
| Ours (Learnable) | 상태별 시그모이드 파라미터 $`g_{z_{t}}`$ | 50.6% |
| Ours (Numerical) | $`(0.3,0.7)`$ 고정 | 69.6% |

> "Fixed numerical scaling performs best, achieving an average success rate of $`69.6\%`$, whereas the binary and learnable variants achieve $`51.8\%`$ and $`50.6\%`$, respectively." (§4.2, Table 1)
(한글 해설 — 이 ablation 이 논문에서 가장 정보량이 큽니다. 이진 변형(51.8%)의 부진은 한쪽 모달리티를 0 으로 완전히 죽이면 손해라는 뜻이고, 학습형 변형(50.6%)의 부진은 계수 두 개조차 150개 시연에서 제대로 배우지 못한다는 뜻입니다. 두 실패가 함께 있어야 "부드러운 + 고정" 조합의 필요성이 성립합니다.)

> "This result suggests that fixed numerical scaling provides a balanced phase-dependent preference without completely suppressing either modality or requiring the weighting rule to be learned from limited demonstrations." (§4.2)
(한글 해설 — 저자의 해석도 같은 두 축입니다. 다만 학습형이 게이팅 baseline(59.6%)보다도 낮다는 점은 저자가 따로 논하지 않는데, 파라미터가 2개뿐인 학습형이 1개짜리 게이트보다 나쁘다는 결과는 데이터 희소성만으로는 설명이 덜 되고 최적화 이슈 가능성을 남깁니다.)

### 데이터 효율 (UniVTAC 5과제 평균, ACT 백본, 전 방법 DTM 적용)

| Method | 25 | 50 | 100 | 150 |
|---|---|---|---|---|
| ACT + DTM | 21.6 | 25.4 | 22.2 | 51.6 |
| Gated ACT + DTM | 15.4 | 30.0 | 27.8 | 59.6 |
| CAAT (Numerical) | 24.8 | 34.0 | 38.4 | 69.6 |

![Figure 3 — data efficiency on UniVTAC](https://arxiv.org/html/2608.01102/fig/data_eff2.png)

> "Figure 3: Data efficiency on the UniVTAC benchmark. The curves report the average success rate across five simulation tasks under different numbers of training demonstrations. All methods use ACT as the policy backbone and apply Dynamic Tactile Masking. CAAT uses the fixed numerical scaling strategy." (§4.2)
(한글 해설 — 논문 제목의 "data-efficient" 주장을 떠받치는 유일한 곡선이며, 세 방법 모두 DTM 을 켠 상태의 비교라는 통제 조건이 캡션에 명시되어 있습니다.)

> "Under the reduced-data settings of 25, 50, and 100 demonstrations, CAAT achieves $`24.8\%`$, $`34.0\%`$, and $`38.4\%`$, respectively, outperforming both baselines at every data scale." (§4.2)
(한글 해설 — 모든 예산에서 우위라는 서술은 표와 일치합니다. 다만 절대 간격은 25개에서 +3.2%p(24.8 vs 21.6)로 가장 작고 150개에서 +18.0%p 로 가장 큽니다. 즉 이 방법의 이득은 **가장 데이터가 적을 때 가장 크지 않습니다** — 저데이터 우위라기보다는 전 구간 우위에 가깝고, 극저데이터에서의 우위는 얇습니다.)

한 가지 더 짚을 점은 baseline 곡선의 비단조성입니다. ACT + DTM 은 50개(25.4)보다 100개(22.2)에서 낮고, Gated 역시 30.0 → 27.8 로 떨어집니다. 세 방법 모두 100 → 150 구간에서 20%p 이상 급등하는 점까지 겹쳐 보면, 이 구간의 학습이 성공/실패가 갈리는 임계 근처에 있고 실행 간 분산이 상당하다는 신호로 읽는 편이 안전합니다.

### 실제 로봇 (3과제 × 3백본, 과제당 20회 시행)

| Task | ACT / Concat | ACT / Gate | ACT / Ours | DP / Concat | DP / Gate | DP / Ours | π0 / Concat | π0 / Gate | π0 / Ours |
|---|---|---|---|---|---|---|---|---|---|
| Lift Bottle | 15% | 20% | 40% | 25% | 35% | 35% | 20% | 15% | 50% |
| Open Box | 10% | 10% | 50% | 20% | 25% | 60% | 25% | 35% | 60% |
| Powerbank Extraction | 50% | 60% | 75% | 65% | 65% | 80% | 65% | 85% | 90% |
| Average | 25.0% | 30.0% | 55.0% | 36.7% | 41.7% | 58.3% | 36.7% | 45.0% | 66.7% |

> "Compared with direct concatenation, CAAT increases the average success rate across tasks from $`25.0\%`$ to $`55.0\%`$ for ACT, from $`36.7\%`$ to $`58.3\%`$ for Diffusion Policy, and from $`36.7\%`$ to $`66.7\%`$ for $`\pi_{0}`$." (§4.3, Table 2)
(한글 해설 — 백본 3종 전부에서 concat 대비 20%p 이상 향상이라는 점이 플러그인 주장의 핵심 증거입니다. 절대 성능은 π0 가 가장 높아, 사전학습 VLA 위에서도 이득이 사라지지 않는다는 것이 함의 측면에서 가장 무거운 결과입니다.)

> "The improvements are particularly pronounced on Open Box, where CAAT achieves success rates of $`50\%`$ – $`60\%`$, compared with $`10\%`$ – $`35\%`$ for the baselines." (§4.3)
(한글 해설 — 이득이 몰린 곳은 Open Box 한 과제입니다. Lift Bottle 의 DP 열은 35% 대 35% 로 동률이고, Powerbank Extraction 의 π0 열은 85% → 90% 로 20회 시행 기준 1회 차이에 해당합니다. 백본별 평균의 상당 부분을 Open Box 가 끌어올린 구조입니다.)

### Ablation — Dynamic Tactile Masking

| Fusion Strategy | Masking | Sim. Avg. | Real Avg. |
|---|---|---|---|
| Direct Concat | ✗ | 38.8% | 21.7% |
| Direct Concat | ✓ | 51.6% | 32.8% |
| Learnable Gating | ✗ | 49.6% | 25.6% |
| Learnable Gating | ✓ | 59.6% | 38.9% |
| CAAT | ✗ | 48.1% | 43.3% |
| CAAT | ✓ | 69.6% | 60.0% |

> "For direct concatenation, masking increases the average success rate by $`12.8`$ and $`11.1`$ percentage points in simulation and the real world, respectively. Learnable gating exhibits similar gains of $`10.0`$ and $`13.3`$ percentage points." (§4.5, Table 3)
(한글 해설 — DTM 이 CAAT 전용 장치가 아니라 융합 전략과 무관하게 듣는 전처리라는 것이 이 두 줄의 요지입니다. 우리 관점에서는 이쪽이 더 실용적인 정보인데, 아키텍처 변경 없이 촉각 토큰 전처리만으로 10%p 안팎이 나온다는 뜻이기 때문입니다.)

> "The largest improvements are observed for CAAT, with gains of $`21.5`$ percentage points in simulation and $`16.7`$ percentage points in the real world." (§4.5, Table 3)
(한글 해설 — 두 구성요소가 단순 가산이 아니라 상승 작용한다는 근거입니다. 해석하자면 배경 토큰을 지워 놓아야 촉각 readout 이 실제로 접촉 정보를 담게 되고, 그래야 접촉 구간에 촉각 가중치를 올리는 것이 의미를 가집니다.)

행별로 더 읽어 보면, DTM 없는 CAAT(48.1%)는 시뮬레이션에서 학습형 게이팅(49.6%)보다도 낮습니다. 즉 시뮬레이션 한정으로는 **DTM 없이는 어텐션 스케일링이 게이팅을 이기지 못합니다**. 반면 실제 로봇에서는 DTM 없는 CAAT(43.3%)가 DTM 있는 게이팅(38.9%)보다 높아 순서가 뒤집힙니다. 실제 환경일수록 접촉 조건부 배분 자체의 값어치가 커진다는 저자 주장과 부합하는 유일한 직접 증거가 이 두 셀의 대비입니다.

어텐션 스케일링 자체의 ablation 에 대해서는 표가 따로 제시되지 않고, DTM 은 유지한 채 스케일링만 제거한 고정 융합 baseline 과의 비교로 서술만 됩니다 — "Removing attention scaling substantially degrades performance in both settings, with a more pronounced reduction in the real-world experiments." (§4.5). 표 3의 `Direct Concat ✓` 행(51.6% / 32.8%)이 그 baseline 에 해당하는 것으로 읽히지만, 전용 수치는 본문에 명시되지 않습니다.

> "Dynamic Tactile Masking determines where informative tactile changes occur, whereas Contact-Aware Attention Scaling determines when tactile information should receive greater emphasis." (§4.5)
(한글 해설 — 두 장치의 역할을 공간(어디)과 시간(언제)으로 분담시킨 요약이며, 이 프레임워크를 남의 스택으로 옮길 때 무엇을 먼저 가져갈지 판단하는 기준이 됩니다.)

### 정성 분석 — 어텐션 이동

![Figure 4 — attention heatmap visualization](https://arxiv.org/html/2608.01102/fig/heap_map.png)

> "Figure 4: Attention heatmap visualization. Panel (a) presents one representative real-world rollout, while panel (b) presents two representative simulated rollouts. Each rollout is arranged in two rows: the top row shows the raw observation frames, and the bottom row shows the corresponding attention heatmaps overlaid on the observations. The heatmaps visualize the modality-specific cross-attention weights after contact-aware attention scaling, with brighter regions indicating tokens with larger scaled attention contributions." (§4.4)
(한글 해설 — 접촉 전에는 시각 토큰에, 접촉 후에는 촉각 토큰에 어텐션이 몰린다는 의도된 동작을 육안으로 보여 주는 그림입니다. 다만 히트맵이 **스케일링을 적용한 뒤**의 가중치라는 캡션 문구가 중요한데, 스케일 계수를 사람이 접촉 상태에 따라 그렇게 넣어 두었으므로 이 이동 자체는 설계의 결과이지 독립적인 검증은 아닙니다.)

---

## ⚖️ 한계

- **접촉 상태가 전역 이진 스칼라입니다.** $`z_{t}\in\{0,1\}`$ 하나가 손 전체를 대표하므로, 손가락 A는 접촉 중이고 손가락 B는 자유 공간에 있는 상황을 표현할 수 없습니다. 2지 그리퍼의 핀치 파지에서는 두 손가락이 거의 동시에 닿으므로 이 근사가 잘 통하지만, 다지 손에서는 같은 시각에 접촉·비접촉이 공존하는 것이 정상 상태라 가정 자체가 깨집니다.
- **접촉 강도(intensity)가 버려집니다.** 계수는 접촉 여부만 보고 갈아 끼워지므로, 살짝 스친 접촉과 강하게 눌린 접촉이 동일한 $`\gamma_{\tau}=0.7`$ 을 받습니다. 슬립(slip) 직전처럼 힘의 *변화*가 결정적인 국면에서 이 이진화가 정보를 버리는 방향으로 작동할 여지가 있습니다.
- **모든 것이 비접촉 기준 프레임 하나에 걸려 있습니다.** DTM 의 $`T_{0}`$ 와 접촉 판정의 $`T_{\mathrm{ref}}`$ 가 모두 에피소드 첫 프레임입니다. 젤 히스테리시스, 센서 예열, 직전 에피소드의 잔류 변형, 혹은 애초에 접촉 상태로 시작하는 과제에서는 이 기준이 오염되고 그 순간 두 장치가 **동시에** 무너집니다. 기준 프레임 갱신 전략은 논의되지 않습니다.
- **계수·임계값에 대한 민감도 분석이 없습니다.** $`(0.7,0.3)`$ 과 $`\rho=0.8`$ 은 단일 설정으로만 보고되며, 이웃 값에서 성능이 어떻게 변하는지 알 수 없습니다. "사람이 정한 숫자가 학습보다 낫다"는 논지의 설득력은 그 숫자가 얼마나 넓은 구간에서 통하는지에 달려 있는데, 그 근거가 비어 있습니다.
- **학습형 변형의 부진이 충분히 해명되지 않습니다.** 상태별 파라미터 2개짜리 학습형(50.6%)이 파라미터 1개짜리 게이팅 baseline(59.6%)보다 낮습니다. 저자는 데이터 희소성으로 설명하지만, 표현력이 더 큰 모델이 특수 케이스로 포함하는 설정보다 나쁘다면 초기화·학습률·시그모이드 포화 같은 최적화 요인을 배제할 수 없습니다. 이 해명이 없으면 "prior 가 학습을 이긴다"는 주장의 일반화 범위가 불분명해집니다.
- **게이팅 baseline 이 약합니다.** 비교 대상 게이트는 전 시점 공유 스칼라 $`\alpha`$ 하나입니다. 토큰별·시점별 적응 가중, cross-attention 기반 융합 같은 현대적 적응 융합과는 비교되지 않았으므로, 10.0%p 격차는 "학습형 융합 일반"이 아니라 "가장 단순한 형태의 게이트"에 대한 우위로 좁혀 읽어야 합니다.
- **실제 로봇 표본이 얇습니다.** 과제당 20회 시행이면 성공률 50% 근처에서 표준오차가 약 11%p 이므로, 표 2의 5%p 안팎 차이(예: π0 Powerbank 85% 대 90%)는 사실상 구분되지 않습니다. 백본별 평균 향상 자체는 크지만, 셀 단위 비교를 근거로 삼기는 어렵습니다.
- **마스킹이 토큰을 제거하지 않고 0 으로 만듭니다.** 시퀀스 길이가 그대로라 계산량은 줄지 않고, 영 벡터 토큰도 위치 임베딩과 어텐션 슬롯을 계속 점유합니다. 토큰 드롭 방식과의 비교가 없어, 이득이 "배경 억제" 때문인지 "영 벡터라는 명시적 신호" 때문인지 분리되지 않습니다.
- **"negligible computational overhead" 주장에 수치가 없습니다.** 모달리티별 cross-attention 을 3회 계산하고 접촉 분류기를 매 스텝 돌리는데도 지연 시간·FLOPs·제어 주기 측정치가 제시되지 않습니다. 실시간 접촉 제어를 겨냥한 방법에서는 이 수치가 성공률만큼 중요합니다.
- **π0 주입 경로가 서술되지 않습니다.** 일반형 토큰 정식화만 제시하고 백본별 주입 경로는 아키텍처 의존이라고 명시했는데, 플로우 매칭 VLA 는 액션 전문가가 백본 KV 를 참조하는 구조라 "모달리티별 토큰 부분집합에 대한 액션 쿼리 readout"이 어디에 대응하는지가 자명하지 않습니다. 재현에 필요한 가장 중요한 정보가 빠져 있습니다.
- **접촉 레이블의 출처가 불명확합니다.** 분류기는 정답 레이블 $`y_{t}`$ 로 지도학습되지만, 실제 로봇 시연에서 이 레이블을 어떻게 얻는지는 `(원문 미명시)` 입니다. 시뮬레이션은 물리 엔진에서 얻을 수 있으나 실제 환경에서는 이 부분이 별도 파이프라인을 요구합니다.

---

## ♻️ 재현성

- **코드 / 가중치** — 논문 본문과 초록에는 프로젝트 페이지 URL 만 제시되고, 코드 저장소나 모델 가중치의 공개 여부는 `(원문 미명시)` 입니다. GitHub · HuggingFace 링크는 논문 어디에도 없습니다.
- **데이터** — 시뮬레이션은 공개 UniVTAC 표준 데이터셋(과제당 150개)을 그대로 사용하므로 재현 가능합니다. 실제 로봇 시연 150개 × 3과제는 자체 수집분이며 공개 여부가 명시되지 않았습니다.
- **하드웨어** — 2지 촉각 그리퍼는 자체 설계·제작입니다. 부품 수준 정보(Dynamixel XL330 5개, 핑거팁 PPTac 센서, Vive Tracker)는 공개되어 있으나, CAD·BOM 공개 여부는 명시되지 않았습니다. 촉각 센서가 PPTac 특정 하드웨어라 동일 재현에는 제작이 선행됩니다.
- **학습 환경** — A100 80GB 1–2장 규모로, 하이퍼파라미터(batch 64, AdamW, lr $`1\times 10^{-5}`$ , wd $`1\times 10^{-4}`$ , $`\rho=0.8`$ , $`\gamma`$ 값)가 부록에 모두 명시되어 재현 장벽은 낮은 편입니다.
- **촉각 인코더** — ViT-VQGAN 사전학습 절차와 코퍼스 구성(GelSight · DIGIT · 9DTact, 수십만 장)이 서술되어 있으나, 정확한 데이터셋 목록·분할·체크포인트 공개 여부는 명시되지 않아 이 부분이 재현의 실질적 병목입니다.
- **평가** — 시뮬레이션 100 시드 × 100 rollout, 실제 20회 시행이라는 프로토콜은 명시적입니다. 다만 학습 시드 반복 횟수와 분산은 보고되지 않습니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P2(구조적 멀티모달 관측 융합)** — 주 연결입니다. `D10`(heterogeneous modality fusion beyond concat) v1 의 "flat concat 대신 cross-attention / 비대칭 융합"과 정확히 같은 문제를 다루되, CAAT 는 **접촉 상태 조건부 readout 스케일링**이라는 새 축을 더합니다. `D11`(proprio-tactile-force token construction) v1 이 이미 명시한 contact-binary 보조 헤드가 여기서는 보조 손실에 그치지 않고 융합 가중치를 스위칭하는 **추론 시 신호**로 승격됩니다.
- **P2 `D8`/`D9` 는 건드리지 않습니다.** 다중 카메라 기하 grounding(`D8`)도, 행동/동역학 인식 시각 인코더(`D9`)도 이 논문의 관심사가 아닙니다. 시각 측은 백본 기본 인코더 그대로입니다.
- **P2 `D12`(topology-aware encoding + hand-level aggregation)** — 명시적 긴장 관계입니다. 우리는 손가락·손바닥 토큰의 위상 구조를 살리려 하는데, CAAT 는 접촉을 손 전체 스칼라 하나로 뭉갭니다. 2지 그리퍼에서는 문제가 없지만 22-DOF 손으로 올릴 때 그대로 쓸 수 없는 부분입니다.
- **P1(이종 Body/Hand 액션 전문가)** — 약한 연결입니다. 논문의 핵심 주장이 "액션 디코더를 **바꾸지 않는다**"이므로 `D1`–`D6` 에는 함의가 없습니다. `D7`(π backbone integration / partition) 에는 관련이 있는데, π0 위에 LoRA 로 CAAT 를 얹어 concat 대비 36.7% → 66.7% 를 얻은 것은 π 백본에 관측단 구조를 주입하는 한 가지 구체적 사례입니다.
- **P0(VLA 데이터셋·벤치마크)** — `D26`(benchmark / eval scouting scope) 연결. UniVTAC([arXiv:2602.10093](https://arxiv.org/abs/2602.10093))은 비주오택타일 조작 전용 시뮬레이션 벤치마크로, 접촉 집약적 평가 하네스를 찾는 `D26` 스코프에 정면으로 들어옵니다. `D25`(tactile / force / torque data scouting) 측면에서는 촉각 UMI 장치가 접촉 시연 수집 경로의 사례입니다.
- **P3(System0) 와는 무관합니다.** CAAT 는 전적으로 모방 학습(IL) 정책의 관측·readout 층이며 RL 요소가 없습니다. `D13`–`D18` 어디에도 함의를 주지 않습니다. 다만 접촉 상태 이진 판정기라는 부품은 `D14`(System1↔System0 binary `maintain_grasp` on/off) 의 게이팅 신호원으로 재활용 가능한 형태이긴 합니다 — 논문이 그 용도를 주장하지는 않습니다.
- **P4 함의는 제한적입니다.** π0 를 LoRA 로 fine-tune 했다는 사실은 `D19`(VLM lineage + adaptation range) v1 의 "(a) 전체 VLM 동결" 기본값과 **불일치**합니다. 논문이 사전학습 보존을 다루지 않으므로 `D20`(prior-preservation strategy) 에 대한 증거는 없고, 오히려 CAAT 도입이 동결 전제와 충돌할 수 있음을 시사합니다.
- **Identity 관계** — 지지와 긴장이 함께 있습니다. "flat concat 을 넘어 관측 자체를 구조적으로 끌어올린다"는 P2 정체성을 값싼 방식으로 실증한다는 점에서 지지이지만, 그 구조화가 **손가락별 접촉 귀속**이 아니라 **전역 단계 스위치**라는 점에서 우리 노선과는 다른 방향의 구조화입니다. 또한 P2 Anti-topic 의 "2-finger parallel-jaw grippers only" 조항에 걸리는 하드웨어이므로, 결과는 참고하되 핀 후보로는 보지 않는 것이 일관됩니다.
- **경쟁자 함의** — 저자진(Shengcheng Luo, Wanlin Li, Ziyuan Jiao, Chenxi Xiao)이 이미 분석한 RGB-S([arXiv:2606.08765](https://arxiv.org/abs/2606.08765))와 상당 부분 겹칩니다. 같은 그룹이 "촉각을 시각 공간에 명시 투영"(RGB-S)에 이어 "접촉 단계로 모달리티 배분을 명시 지정"(CAAT)을 내놓은 셈으로, **암시적 학습 대신 명시적 prior** 라는 일관된 노선을 빠르게 밀고 있습니다. 우리가 `D10`/`D11` 에서 같은 영역을 다루므로 추적 대상 그룹으로 볼 만합니다.

---

## ✨ 핀 논문 대비 델타

- **vs. ViTacFormer([arXiv:2506.15953](https://arxiv.org/abs/2506.15953), P2 핀)** — ViTacFormer 는 cross-attention 으로 시각-촉각 교차 모달 표현을 **학습**합니다. CAAT 는 그 학습을 그대로 두되(공동 self-attention 유지), 마지막 readout 에서 모달리티별로 softmax 를 분리하고 외부 계수로 가중합니다. 델타는 "융합 구조를 바꾼다"가 아니라 "융합 결과를 읽는 지점에 단계 prior 를 건다"입니다.
- **vs. ForceFlow([arXiv:2605.11048](https://arxiv.org/abs/2605.11048), P2 핀)** — ForceFlow 는 비대칭 융합과 V2F handover 로 이미 모달리티 전환 개념을 갖고 있습니다. CAAT 의 진짜 델타는 전환 개념 자체가 아니라 **전환 트리거를 학습이 아닌 동결된 이진 분류기로 외부화**한 점, 그리고 **고정 수치 계수가 학습형 계수를 69.6 대 50.6 으로 이겼다**는 음성 결과입니다. 후자는 우리가 `D10` 에 학습형 게이트를 하나 더 붙이려 할 때 반례로 쓸 수 있는 증거입니다.
- **vs. RGB-S([arXiv:2606.08765](https://arxiv.org/abs/2606.08765), 동일 그룹 인접 연구)** — RGB-S 는 촉각의 **공간적 위치**를 기하로 못 박고(어디를 만지는가), CAAT 는 촉각의 **시간적 유효 구간**을 접촉 상태로 못 박습니다(언제 만지는가). 두 축은 직교하며 원리적으로 결합 가능합니다. 우리 스택 관점에서 RGB-S 쪽이 per-finger 귀속과 더 잘 맞고, CAAT 쪽은 그 위에 얹는 시간 축 보완재로 읽는 것이 자연스럽습니다.
- **vs. DynaFLIP([arXiv:2605.30350](https://arxiv.org/abs/2605.30350)) · VGGT/eVGGT(`D8`/`D9` 핀)** — 접점이 없습니다. CAAT 의 시각 경로는 백본 기본 인코더 그대로이고 다중 뷰 기하도 다루지 않습니다. 이 핀들의 지위는 변하지 않습니다.
- **vs. Sparsh([arXiv:2410.24090](https://arxiv.org/abs/2410.24090), 비핀 촉각 파운데이션 모델)** — CAAT 의 ViT-VQGAN 촉각 인코더는 Sparsh 계열과 같은 발상(다중 센서 코퍼스 사전학습 + 동결)의 형제이며, 인코더 자체가 기여는 아닙니다. 델타는 그 동결 표현 **위에서** 코사인 유사도 마스킹을 돌린다는 사용법입니다.
- **vs. π0([arXiv:2410.24164](https://arxiv.org/abs/2410.24164), P1 핀)** — π0 를 백본으로 소비할 뿐 백본에 대한 기여는 없습니다. 다만 사전학습 VLA 위에서도 관측단 prior 의 이득이 남는다(36.7% → 66.7%)는 점은 P1 핀에 대한 유용한 부가 증거입니다.

---

## ⚙️ 의사결정 함의

이 논문이 옳다면 우리 파이프라인에서 바뀌는 것은 다음 네 가지입니다.

- **`D11` — 촉각 전처리에 변화 기반 마스킹 단계를 추가.** Deform Map 특징에 대해 에피소드 첫 프레임 기준 코사인 유사도 마스킹을 도입합니다. 신설 config: `obs.tactile.dtm.enabled: true`, `obs.tactile.dtm.rho: 0.8`, `obs.tactile.dtm.reference: episode_first_frame`, `obs.tactile.dtm.mode: zero_fill`. 근거는 이 장치가 융합 방식과 무관하게 시뮬레이션 +10.0–12.8%p · 실제 +11.1–13.3%p 를 준다는 표 3이며, 아키텍처 변경이 없어 **가장 먼저 시도할 항목**입니다.
- **`D11` — contact-binary 보조 헤드를 추론 시 신호로 승격.** 현재 v1 은 보조 손실용 경량 헤드로만 두고 있는데, 이를 손가락별 접촉 확률 $`p_{t}^{(i)}`$ 출력으로 바꾸고 임계값 0.5 로 이진화해 융합 가중에 넣습니다. 신설 config: `obs.tactile.contact_head.per_finger: true`, `obs.tactile.contact_head.threshold: 0.5`, `obs.tactile.contact_head.frozen_after_stage: 2`. 이 헤드는 정책과 함께 학습하지 않고 동결하는 것이 논문 설정과 일치합니다.
- **`D10` — 융합 출력에 단계 조건부 스케일링 항 추가.** cross-attention fuser 뒤, 액션 전문가 입력 직전에 모달리티별 readout 가중합을 삽입합니다. 신설 config: `fusion.contact_gamma.noncontact: [0.7, 0.3]`, `fusion.contact_gamma.contact: [0.3, 0.7]`, `fusion.gamma_learnable: false`, `fusion.proprio_unscaled: true` (고유수용 readout 은 계수 없이 가산 — 식 13 과 동일). 다지 손에서는 전역 스칼라 대신 손가락 토큰별 $`\gamma`$ 적용이 필요하므로 `fusion.gamma_scope: per_finger` 를 기본값으로 둡니다.
- **`D10` — 학습형 게이트 추가 계획의 우선순위 하향.** 고정 수치(69.6%) > 게이팅(59.6%) > 학습형 스케일링(50.6%) 순서는, 150개 시연 규모에서 모달리티 가중을 학습시키는 방향이 손해라는 증거입니다. 우리 배포 적응 예산(`D21` Stage 3, 분 단위 데이터)은 그보다도 작으므로, 가중 규칙은 **하드코딩 후 필요 시 완화**하는 순서로 갑니다.

**평가 측 변경.** 성공률 단일 지표로는 이 변경의 효과가 관측되지 않습니다. 접촉 구간과 비접촉 구간을 분리한 성공률/오차 지표를 평가 스윕에 추가하고(`eval.split_by_contact_phase: true`), 접촉 판정기 자체의 정확도(precision/recall)를 별도 지표로 기록합니다 — 스케일링이 잘못된 $`z_{t}`$ 위에서 돌면 이득이 손해로 뒤집히기 때문입니다.

**적용 순서.** DTM 등가물 → 접촉 헤드 승격 → 고정 $`\gamma`$ 스케일링. 앞 두 단계가 아키텍처 무변경이라 비용이 낮고, 표 3의 `CAAT ✗ masking` 행(시뮬 48.1%)이 마스킹 없는 스케일링 단독은 게이팅만도 못하다는 것을 보여 주므로 순서를 뒤집으면 안 됩니다.

---

## ⚠️ 먼저 검증할 실패 모드

싼 것부터 나열합니다. 앞의 세 항목은 정책 학습 없이 데이터만으로 판정 가능합니다.

1. **코사인 유사도 임계값이 우리 센서에서 분리되지 않을 위험 (가장 쌈).** CAAT 의 $`\rho=0.8`$ 은 GelSight · DIGIT · 9DTact 로 사전학습된 ViT-VQGAN 인코더의 특징 공간에서 정해진 값입니다. Sharpa Deform Map(약 320×240 · 30Hz)은 그 코퍼스에 없습니다. **검증**: 텔레옵 없이 손으로 5분 분량 Deform Map 을 기록하고, 명백한 비접촉 구간과 명백한 접촉 구간 각각에서 패치별 코사인 유사도 히스토그램을 그립니다. 두 분포가 0.8 근처에서 갈리지 않으면 임계값 재조정이 아니라 마스킹 기준 자체(픽셀 차분·힘 임계)를 바꿔야 한다는 신호입니다. 학습 코스트 0.
2. **전역 이진 접촉 상태가 다지 손에서 무의미해질 위험.** 같은 기록 데이터에서 손가락별 접촉 이진값을 라벨링해, "전 손가락 접촉"과 "일부 손가락만 접촉" 구간의 시간 비율을 셉니다. 후자가 지배적이면 전역 $`z_{t}`$ 는 대부분의 시간 동안 어느 손가락에도 맞지 않는 값이 되며, `fusion.gamma_scope: per_finger` 가 선택이 아니라 필수가 됩니다. 학습 코스트 0.
3. **인핸드 회전에서 시각 하향 가중이 해로울 위험.** CAAT 의 과제는 모두 파지 후 곧 끝나는 2지 핀치 계열(Lift Bottle · Open Box · Powerbank Extraction)이라 접촉 이후 시각 정보 가치가 실제로 떨어집니다. 우리 Phase 1 은 인핸드 큐브 회전으로, 접촉이 **거의 항상 켜져 있고** 물체 자세 추적을 위해 시각이 끝까지 필요합니다. 이 경우 접촉 중 $`\gamma_{v}=0.3`$ 은 순손실일 수 있고, 동시에 $`z_{t}`$ 가 상시 1 로 고정되어 CAAT 는 고정 재가중으로 퇴화합니다(표 3의 `CAAT ✗` 조건에 가까움). **검증**: 기존 시뮬레이션 회전 과제 하나에 $`\gamma`$ 스왑만 적용해 성공률을 비교합니다. 정책 1회 학습으로 판정됩니다.
4. **`D19` 동결 전제와의 충돌.** 논문의 π0 결과는 LoRA fine-tune 로 얻은 것입니다. 우리 v1 은 VLM 전체 동결 + 액션 전문가만 학습이며, 동결 상태에서 백본 내부 토큰을 모달리티별로 되쪼개 readout 을 만드는 개입이 가능한지는 별개 문제입니다. **검증**: openpi 그래프에서 액션 전문가가 참조하는 KV 텐서가 모달리티 경계로 분할 가능한지 코드 수준에서 확인합니다(학습 불필요). 분할이 불가능하면 CAAT 는 백본 밖 관측 융합기 단계에만 적용 가능하며, 그것이 논문 설정과 같은 것인지 재확인이 필요합니다.
5. **접촉 레이블 조달 비용.** 접촉 분류기는 지도 학습이 필요한데 실제 시연의 레이블 출처가 논문에 없습니다. 우리는 Isaac Lab 에서 정답 접촉을 뽑을 수 있으나 실기 데이터에는 없습니다. **검증**: 관절 토크(또는 모터 전류) 임계 + Deform Map 변화량의 조합으로 자동 라벨을 만들고, 사람이 눈으로 표시한 100프레임과 일치율을 잽니다. 일치율이 낮으면 분류기 학습 이전에 라벨링 파이프라인이 선행 과제가 됩니다.
6. **기준 프레임 오염.** 우리 과제는 파지 상태에서 시작하거나 에피소드 간 손가락이 재정렬되지 않을 수 있어, "첫 프레임 = 비접촉"이라는 가정이 깨질 수 있습니다. **검증**: 연속 20 에피소드의 첫 프레임끼리 코사인 유사도를 계산해 드리프트를 봅니다. 드리프트가 크면 기준 프레임을 에피소드별이 아니라 캘리브레이션 루틴(손 벌린 상태 강제)에서 취득하도록 프로토콜을 바꿔야 합니다.
7. **극저데이터 구간에서 이득이 얇아질 위험.** 표 4에서 25개 시연 시 CAAT 우위는 +3.2%p 에 불과합니다. 우리 배포 적응 목표는 분 단위 데이터로 그보다 작은 예산이므로, 이 prior 의 이득이 사전학습 단계(150개급)에서만 나타나고 배포 적응 단계에서는 사라질 수 있습니다. **검증**: 도입 시 사전학습 단계와 배포 적응 단계를 나누어 각각 ablation 합니다.
8. **토큰 수 규모 차이.** 논문은 센서당 $`N=256`$ 토큰을 씁니다. 우리 `D11` v1 은 손가락 10 + 손바닥 2 = 12개 토큰으로 훨씬 압축된 표현이라, 패치 단위 마스킹이라는 개념 자체가 그대로 옮겨지지 않습니다. **검증**: 마스킹을 토큰 단위가 아니라 fingertip CNN 입력단(Deform Map 픽셀 영역)에서 수행하는 변형이 등가인지 먼저 정하고 넘어갑니다.
9. **지연 시간.** 모달리티별 cross-attention 3회 + 접촉 분류기가 매 스텝 추가됩니다. 논문에 측정치가 없으므로 우리 제어 주기 예산 안에 들어가는지 직접 재야 합니다. **검증**: 더미 텐서로 forward 지연만 측정(정책 학습 불필요).

---

## 💡 컨텍스트 제안

사람이 판단할 항목만 적습니다. `context/` 파일은 수정하지 않았습니다.

- **P0 §5 — UniVTAC 을 벤치마크 추적 후보로 검토.** UniVTAC([arXiv:2602.10093](https://arxiv.org/abs/2602.10093))은 비주오택타일 조작의 데이터 생성·학습·벤치마킹 통합 시뮬 플랫폼으로, `D26`(dexterous + contact-rich 벤치마크 스코프)과 `D25`(촉각/힘 데이터 희소성)에 동시에 걸립니다. 현재 P0 핀 8개는 모두 채워져 있으므로 우선 비핀 methodology base 행 추가를 제안합니다. 단, 본 분석은 UniVTAC 원문을 읽지 않았고 CAAT 가 인용한 범위(5과제, 과제당 150 시연)만 확인했으므로, 핀 승격 판단 전 별도 검토가 필요합니다.
- **P2 `D10` — deferred 후보에 "접촉 단계 조건부 readout 스케일링" 추가.** 현 v1 은 cross-attention / 비대칭 융합 + modality dropout 입니다. 여기에 "접촉 상태로 모달리티 readout 을 고정 계수 가중"을 추적 대안으로 기록해 두기를 제안합니다. 근거 수치: 시뮬 +18.0%p(concat 대비) / +10.0%p(게이트 대비), 실제 백본 3종 평균 60.0%.
- **P2 `D10` — 학습형 가중에 대한 음성 증거 기록.** 고정 수치(69.6%)가 학습형(50.6%)을 이겼다는 결과는 `D10` 에 학습형 게이트를 추가하려는 방향의 반례입니다. Decision 자체를 바꾸자는 제안은 아니고, 저데이터 구간 판단 근거로 남겨 둘 값어치가 있습니다.
- **P2 `D11` — DTM 등가물을 스왑형 센서 헤드 규격에 반영 검토.** "비접촉 기준 대비 변화량 기반 억제"는 센서 종류와 무관한 전처리 원리이므로, `D11` 의 "swappable sensor head + common token format" 규격에 선택적 전처리 단계로 명시해 둘 수 있습니다.
- **핀 교체 제안 없음.** 2지 그리퍼 · 전역 이진 접촉 · per-finger 귀속 부재는 P2 핀 기준선(ViTacFormer / ForceFlow)에 미치지 못하고, P2 Anti-topic 의 2지 그리퍼 조항에도 부분적으로 걸립니다. 핀은 현행 유지를 권합니다.
- **추적 그룹 메모.** CAAT 와 RGB-S([arXiv:2606.08765](https://arxiv.org/abs/2606.08765))가 저자진을 공유하며 "암시적 학습 대신 명시적 prior" 노선을 연속으로 내고 있습니다. 개별 논문 핀보다 이 그룹의 후속 출력을 주시하는 편이 효율적일 수 있습니다.
