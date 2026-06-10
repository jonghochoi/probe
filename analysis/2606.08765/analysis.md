# Paper Analysis — RGB-S: Image-Aligned Tactile Saliency for Robust Dexterous Manipulation

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | RGB-S: Image-Aligned Tactile Saliency for Robust Dexterous Manipulation |
| 저자 | Shengcheng Luo, Kefei Wu, Xiaoying Zhou, Wanlin Li, Ziyuan Jiao, Chenxi Xiao |
| 링크 | [arXiv:2606.08765](https://arxiv.org/abs/2606.08765) · [Website](https://touch-as-saliency.github.io) |
| 발행일 / 버전 | 2026-06-07 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-10 |
| 관련 Pillar | P2, P4 |
| 태그 | tactile, force, dexterity |

---

## 🧭 한 줄 요약 (TL;DR)

순방향 기구학(FK)과 카메라 캘리브레이션으로 촉각 센서 위치를 RGB 이미지 평면에 직접 투영해, 힘으로 변조한 Gaussian saliency map 을 만들고 이를 사전학습 시각 백본에 zero-init 채널로 주입하는 비주오택타일(visuotactile) 융합 프레임워크입니다. 촉각-시각 대응을 암시적으로 학습시키는 대신 기하 prior 로 명시적으로 박아 넣어, 시각 가림(occlusion) 상황에서 실제 로봇 조작 성공률을 최강 암시적 baseline 대비 26.7%p 끌어올립니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 희소(sparse)·이종(heterogeneous)·로봇 중심(robot-centric)의 촉각 신호를 조밀(dense)한 시각 표현과 어떻게 *공간적으로* 정합(align)시킬 것인가. 특히 시각이 가려지거나 신뢰할 수 없을 때 촉각이 핵심 단서가 되어야 합니다.
- **기존 접근의 한계** — 다수의 비주오택타일 정책은 촉각-시각 대응을 제한된 시연(demonstration)으로부터 *암시적으로* 학습시킵니다(latent concat / FiLM / cross-attention). 기하 prior 가 없어 데이터 비효율적이고, 가림 상황에서 일반화가 약합니다.
- **3D 명시 융합의 한계** — 촉각을 명시적으로 3D 점군(point-cloud) 공간으로 들어 올리는 접근은 공간 추론에는 좋지만 깊이(depth) 센싱 의존, 노이즈 민감성, 계산 부담이 크고, 처음부터 작은 3D 망을 학습시키느라 풍부한 2D 사전학습 백본을 활용하지 못합니다.
- **본 논문의 가설** — 흔히 구할 수 있는 시각 표현을 *앵커(anchor)* 로 삼아 희소 촉각 신호를 명시적으로 *grounding* 할 수 있다. 즉 촉각을 이미지의 native 2D 좌표계로 투영해버리면 별도의 이종 아키텍처 없이 시각-촉각 대응이 deterministic 하게 성립합니다.
- **왜 지금 중요한가** — 시각은 표준 포맷·대규모 사전학습 백본이 풍부하지만 촉각은 센서마다 신호 형식이 달라 표준 데이터셋·전이 가능한 사전학습 파이프라인이 없습니다. 이 *모달리티 비대칭*을 이미지 공간이라는 공통 표현으로 흡수하려는 시도입니다.

---

## 🧩 핵심 기여

- **이미지 평면 촉각 grounding** — FK + 카메라 캘리브레이션으로 희소 촉각 측정값을 2D 이미지 평면에 투영, 로봇 중심 접촉 신호를 명시적 시각 saliency 단서로 변환.
- **Zero-initialized conditioning 융합** — 사전학습된 표준 2D 시각 인코더(ResNet-18)의 첫 conv 를 3→4 채널로 확장하고 saliency 채널을 0 으로 초기화. 초기 시점에 원본 RGB 인코더와 *기능적으로 동일*하여 사전학습 표현을 보존하면서 촉각 공간 정보를 점진적으로 흡수.
- **정책 비종속(policy-agnostic) 검증** — BC-MLP / ACT / Diffusion Policy 세 가지 모방학습(IL) 백본 + 시뮬레이션 3 + 실제 3 = 총 6 개 다지 조작(dexterous manipulation) 과제에서, 정상·가림 조건 모두에 대해 대표적 융합 baseline 들과 비교.
- **가림 강건성(occlusion robustness)** — 실제 로봇 가림 조건에서 최강 암시적 비주오택타일 baseline 대비 성공률 26.7%p 향상, 렌더링/정합/융합 구조에 대한 ablation 과 효율 분석 포함.

---

## 🔑 기술 키워드

- **RGB-S (RGB-Saliency)** — RGB 3채널에 촉각 saliency 1채널을 덧붙인 4채널 관측. 카메라가 "어디를 만지고 있는지"를 그림 위에 직접 그려 넣은 셈입니다.
- **Force-Aware Kinematic Projection** — 손가락 센서의 3D 위치를 FK 로 구하고 카메라 행렬로 픽셀로 투영한 뒤, 힘 크기에 비례한 Gaussian 점을 찍어 saliency 를 만드는 deterministic 절차.
- **Zero-Initialized Conditioning** — 새로 추가한 입력 채널의 가중치를 0 에서 출발시켜, 학습 초기엔 사전학습 망의 출력을 한 글자도 바꾸지 않다가 fine-tuning 동안 서서히 신호를 반영하는 ControlNet 식 전략.
- **Force-Modulated Gaussian Saliency** — 각 접촉 위치에 힘 크기로 진폭을 조절한 Gaussian 커널을 얹어 만든 히트맵. 강하게 누를수록 그 지점이 더 밝게 표시됩니다.
- **Spatial Softmax** — 특징 맵을 $`K`$ 개 keypoint 의 기대 2D 위치로 압축하는 풀링. 활성값을 전부 flatten 하지 않고 "어디가 두드러지는가"의 좌표만 남깁니다.
- **Visuo-Tactile Fusion** — 비주오택타일(시각+촉각) 융합. 본 논문은 latent 융합이 아니라 입력 단계 이미지 공간 융합을 택합니다.
- **Implicit vs Explicit Spatial Grounding** — 대응을 데이터로 학습(암시적)할지, 기하 prior 로 못 박을지(명시적)의 대비. 본 논문은 명시적 쪽.
- **Occlusion Robustness** — 과제 관련 이미지 영역을 마스킹한 가림 조건에서의 성능 유지력. 본 논문 평가의 핵심 축.
- **FSR / Taxel Tactile Nodes** — 손에 분포한 FSR(force-sensitive resistor) 12개 + fingertip TwinTac taxel 32개 = 44개 이산 접촉 노드. 투영의 단위가 되는 점들입니다.

---

## 🔬 방법론

### 직관

RGB-S 의 출발점은 한 가지 비대칭에 대한 인식입니다. 시각 데이터는 표준 포맷과 대규모 사전학습 백본이 풍부한 반면, 촉각 신호는 센서마다 형식이 제각각이라 그런 자산이 없습니다. 그렇다면 촉각을 별도의 표현 공간에서 다루지 말고, *이미 잘 갖춰진 시각의 좌표계로 끌어들이자*는 발상입니다. 손가락 센서가 물리적으로 어디에 붙어 있는지는 로봇이 자기 자세(proprioception)로 정확히 알고 있고, 카메라가 캘리브레이션되어 있다면 그 3D 위치가 이미지의 어느 픽셀에 찍히는지도 계산만으로 알 수 있습니다. 즉 "어디를 만지고 있는가"는 학습할 필요 없이 *기하학적으로 이미 정해져 있습니다*.

그래서 RGB-S 는 각 접촉점을 이미지 평면에 투영하고, 누르는 힘의 세기에 비례한 밝기의 Gaussian 점을 그 자리에 찍습니다. 결과물은 RGB 이미지와 같은 해상도의 1채널 saliency map — "지금 손이 화면의 이 지점들을 이만큼의 힘으로 누르고 있다"를 그림으로 그린 것입니다. 이 map 을 RGB 옆에 4번째 채널로 붙여(RGB-S) 정책에 넣습니다. 이렇게 하면 촉각과 시각이 같은 2D 좌표계 안에서 자동으로 정합되므로, 정책이 "이 촉각 벡터가 화면의 어느 물체에 해당하는가"를 시연으로부터 힘들게 추론할 필요가 없어집니다.

마지막 난제는 "사전학습된 RGB 인코더에 4번째 채널을 어떻게 끼워 넣어도 기존 표현을 망가뜨리지 않을까"입니다. 답은 ControlNet 의 zero-init 전략입니다. 첫 conv 레이어를 3→4 채널로 늘리되 새 채널 가중치를 0 으로 시작합니다. 그러면 학습 시작 시점엔 saliency 가 출력에 아무 영향을 주지 못해 인코더는 원본 RGB 망과 정확히 같게 작동하고, fine-tuning 이 진행되며 그 가중치가 0 에서 자라나 촉각 정보를 점진적으로 반영합니다. 사전학습 prior 를 보존하면서 새 모달리티를 안전하게 주입하는 장치입니다.

![Figure 1 — RGB-S overview](https://arxiv.org/html/2606.08765/x1.png)

> "Figure 1: Overview of RGB-S. Classical tactile-vision fusion relies on implicit multimodal embeddings that often lose spatial correspondence under occlusion. Our RGB-S paradigm explicitly projects tactile contacts onto image-space saliency maps, producing a force-aware and spatially aligned representation for robust dexterous manipulation." (§1)
(한글 해설 — 암시적 latent 융합이 가림 상황에서 공간 대응을 잃는 문제를, 촉각을 이미지 공간 saliency 로 명시 투영해 해결한다는 패러다임 대비를 한 장으로 요약합니다.)

### 아키텍처

**문제 정식화(Problem Formulation).** 표준 비주오택타일 모방학습 패러다임을 따릅니다.

> "We follow the standard visuotactile imitation learning paradigm, in which a policy $`\pi_{\theta}(\mathbf{a}_{t}\mid\mathbf{o}_{t-k:t})`$ is learned from expert demonstrations $`\mathcal{D}=\{(\mathbf{o}_{t},\mathbf{a}_{t})\}_{t=1}^{N}`$." (§3.1)
(한글 해설 — 정책 $`\pi_{\theta}(\mathbf{a}_{t}\mid\mathbf{o}_{t-k:t})`$ 를 전문가 시연 $`\mathcal{D}=\{(\mathbf{o}_{t},\mathbf{a}_{t})\}_{t=1}^{N}`$ 로부터 IL 로 학습하는 통상적 셋업입니다.)

관측은 멀티모달 $`\mathbf{o}_{t}=\{\mathbf{I}_{t},\mathbf{s}_{t},\mathbf{f}_{t}\}`$ 로, RGB 이미지 $`\mathbf{I}_{t}\in\mathbb{R}^{H\times W\times 3}`$, proprioception $`\mathbf{s}_{t}`$, 저차원 촉각 측정값 $`\mathbf{f}_{t}`$ 로 구성됩니다. 핵심은 $`\mathbf{f}_{t}`$ 를 독립 벡터로 처리하지 않고 이미지 공간 saliency map $`\mathbf{S}_{t}\in\mathbb{R}^{H\times W\times 1}`$ 로 변환해 RGB 와 concat 하는 것입니다 (식 1):

$$\mathbf{X}_{t}=\mathrm{Concat}(\mathbf{I}_{t},\mathbf{S}_{t})\in\mathbb{R}^{H\times W\times 4}.$$

학습 목표는 증강된 관측을 입력으로 한 정책 $`\pi_{\theta}(\mathbf{a}_{t}\mid\mathbf{X}_{t-k:t},\mathbf{s}_{t-k:t})`$ 를 표준 시각 IL 손실로 학습하는 것입니다.

**Force-Aware Kinematic Projection (3단계).** 이산 촉각 측정값을 이미지 공간 saliency 로 매핑하는 deterministic 정합 과정입니다.

- **1단계 — FK 위치추정.** 촉각 reading $`\mathbf{f}_{t}=\{f_{i,t}\}_{i=1}^{M}`$ (각 $`f_{i,t}`$ 는 스칼라 힘 크기 또는 접촉 강도)에 대해, $`i`$-번째 센서 노드의 world frame 3D 위치를 FK 로 계산합니다 (식 2):

$$\mathbf{P}_{i,t}=\mathrm{FK}(\mathbf{s}_{t},\mathbf{L}_{i}),$$

여기서 $`\mathbf{L}_{i}`$ 는 부착된 kinematic link 에 대한 센서의 고정 local offset 입니다.

- **2단계 — 카메라 투영.** 카메라 view $`c`$ 의 외부 파라미터 $`\mathbf{R}^{c}\in\mathbb{R}^{3\times 3}`$, $`\mathbf{t}^{c}\in\mathbb{R}^{3}`$ 와 내부 행렬 $`\mathbf{K}^{c}\in\mathbb{R}^{3\times 3}`$ 로 픽셀 좌표 $`\mathbf{p}^{c}_{i,t}=[u^{c}_{i,t},v^{c}_{i,t}]^{\top}`$ 를 얻습니다 (식 3):

$$[u^{c}_{i,t},v^{c}_{i,t},1]^{\top}\sim\mathbf{K}^{c}\left(\mathbf{R}^{c}\mathbf{P}_{i,t}+\mathbf{t}^{c}\right).$$

이미지 경계를 벗어난 노드는 버리고, 유효 노드 집합을 $`\mathcal{V}^{c}_{t}`$ 로 둡니다.

- **3단계 — Force-modulated Gaussian rendering.** 희소한 투영점을 조밀 saliency map $`\mathbf{S}^{c}_{t}\in\mathbb{R}^{H\times W\times 1}`$ 로 렌더링합니다 (식 4):

$$\mathbf{S}^{c}_{t}(u,v)=\max_{i\in\mathcal{V}^{c}_{t}}\left[\tilde{f}_{i,t}\exp\left(-\frac{(u-u^{c}_{i,t})^{2}+(v-v^{c}_{i,t})^{2}}{2\sigma^{2}}\right)\right],$$

$`\sigma`$ 가 각 투영 접촉 반응의 공간 퍼짐을 조절합니다. 촉각값은 $`\tilde{f}_{i,t}=\tanh\left(\gamma f_{i,t}/F^{i}_{\mathrm{limit}}\right)`$ 로 정규화하며, $`F^{i}_{\mathrm{limit}}`$ 는 센서별 포화 한계, $`\gamma`$ 는 스케일 인자입니다. $`\max`$ 집계는 여러 투영 접촉이 겹칠 때 saliency 를 bounded 하게 유지하기 위함입니다.

**Lightweight Network Architecture.** 증강 관측 $`\mathbf{X}_{t}`$ 를 사전학습 시각 인코더에 주입합니다.

![Figure 2 — RGB-S architecture](https://arxiv.org/html/2606.08765/x2.png)

> "Figure 2: The RGB-S architecture. RGB-S extends a pretrained RGB visual encoder with a zero-initialized saliency channel, allowing projected tactile cues to be fused in the image domain while preserving the original visual representation at initialization." (§3.3)
(한글 해설 — 첫 conv 채널 확장 + zero-init 으로, 이미지 도메인 융합과 사전학습 표현 보존을 동시에 달성하는 구조를 보여줍니다.)

- **백본** — ResNet-18 trunk 를 시각 인코더로 사용. 첫 conv 레이어를 3→4 입력 채널로 확장하고 이후 레이어는 그대로 둡니다.
- **Zero-init.** ControlNet 의 zero-initialization 을 따라 첫 3채널은 사전학습 RGB 가중치로, 새 saliency 채널은 0 으로 초기화합니다 (식 5):

$$\mathbf{z}^{c}_{t}=\mathbf{W}_{\mathrm{rgb}}\ast\mathbf{I}^{c}_{t}+\mathbf{W}_{s}\ast\mathbf{S}^{c}_{t},\qquad\mathbf{W}_{s}=\mathbf{0}\ \text{at initialization},$$

$`\mathbf{W}_{\mathrm{rgb}}`$ 는 원본 ResNet-18 첫 레이어 RGB 가중치, $`\mathbf{W}_{s}`$ 는 촉각 saliency 채널 가중치, $`\ast`$ 는 convolution.

> "With this initialization, the RGB-S encoder is initially functionally equivalent to the original RGB encoder." (§3.3)
(한글 해설 — 학습 시작 시점엔 saliency 채널이 출력에 0 만큼 기여하므로 원본 RGB 인코더와 완전히 동일하게 동작하고, fine-tuning 동안 $`\mathbf{W}_{s}`$ 가 갱신되며 공간 정합된 촉각 정보를 흡수합니다 — 사전학습 prior 보존의 핵심 장치입니다.)

- **풀링 / 압축** — 수정된 첫 conv 이후 ResNet-18 trunk 는 원본과 동일하게 처리. 출력 특징 맵을 spatial softmax 로 압축해 $`K`$ 개 feature point 의 기대 2D 위치로 표현합니다. 구현에서 $`K=32`$, 카메라 view 당 64차원 시각 특징을 생성한 뒤 경량 linear projection + ReLU 를 적용.
- **글로벌 조건 구성** — 모든 카메라 view 의 RGB-S 특징을 나머지 관측 모달리티와 concat 해 관측 horizon $`T_{o}`$ 길이의 compact 조건 시퀀스 $`\mathbf{g}_{t-T_{o}+1:t}`$ 를 만들고, 이를 downstream 정책 학습의 global condition 으로 사용.

### 학습 목표 / 손실

손실은 채택한 downstream 정책 백본을 따릅니다(별도 RGB-S 전용 손실은 없음, §4.1·Appendix E):

- **BC-MLP** — 단일 step behavior cloning, MSE action regression loss.
- **ACT** — transformer encoder-decoder + conditional VAE 분기, L1 masked action reconstruction loss + KL regularization.
- **DP (Diffusion Policy)** — conditional 1D denoising U-Net, 100 DDPM denoising step. 배포 시 예측 chunk 의 앞 8 action 실행 후 재계획.

### 학습 셋업

- **시뮬레이션 촉각** — ETac 기반 tactile simulator. 손 표면 샘플점과 물체 mesh 의 signed distance 로 접촉을 계산, spring-damper + 마찰 모델로 힘 추정. 시뮬레이션은 force-dependent kernel width $`\sigma_{i}=\sigma_{\min}+\bar{f}_{i}(\sigma_{\max}-\sigma_{\min})`$ 사용 ($`\sigma_{\min}=4`$, $`\sigma_{\max}=12`$, $`\bar{f}_{i}`$ 는 정규화 힘 크기).
- **실제 하드웨어** — xArm6 + LEAP Hand (12 joint-mounted FSR + 4 fingertip TwinTac, taxel 32 + FSR 12 = 44 투영 노드). RealSense D435 2대(캘리브레이션). 외부 파라미터는 EasyHEC 로 캘리브레이션.
- **관측 / 액션** — proprioception $`s_{t}=[q^{\mathrm{arm}}_{t},q^{\mathrm{hand}}_{t}]\in\mathbb{R}^{22}`$ (arm 6 + hand 16). 촉각 $`\tau_{t}\in\mathbb{R}^{44}`$. 액션 $`a_{t}\in\mathbb{R}^{22}`$. 모든 RGB 는 center-crop 후 $`224\times 224`$ 로 resize. 20Hz.
- **하드웨어/구현** — NVIDIA A40 학습, RTX 4090 배포. 텔레오퍼레이션은 Meta Quest 3(손목 추적) + Manus Quantum Metaglove(손가락 모션) + ARCap 프레임워크. 모든 downstream 정책은 **LeRobot 기반** 구현(Appendix E).
- **하이퍼파라미터(Table 7 발췌)** — BC-MLP/ACT/DP 모두 batch 64, train 120K steps. DP: obs step 5 / pred horizon 24 / exec 16 / Adam / lr $`1\times10^{-4}`$ / weight decay $`1\times10^{-6}`$. ACT: lr $`1\times10^{-5}`$. DP U-Net 채널 $`[512,1024,2048]`$, kernel 5, group norm 8 groups, diffusion-step embedding 128차원.

---

## 📊 실험 설정과 결과

평가는 시뮬레이션 3 + 실제 3 = 6 과제, 정상(normal)·가림(occluded) 두 조건에서 진행됩니다. 정책은 정상 관측으로 수집한 시연으로 학습하고, 평가 시에만 과제 관련 영역에 사전 정의된 검은 마스크를 적용합니다(마스크 크기 과제 공통). 세 연구 질문(RQ1 정책 비종속 효과, RQ2 실제 전이, RQ3 설계 요소 영향)을 검증합니다.

**시뮬레이션 성공률(Table 1, 단위 %)** — 정책 백본별로 RGB-S 와 융합 baseline 들을 비교. 아래는 핵심 행 발췌(Avg. = Normal·Occlud. 평균):

| Policy | Fusion | P&P Avg. | Cube-Push Avg. | Rotate-Cross Avg. |
|---|---|---|---|---|
| BC-MLP | Vision-Only | 3.7 | 16.7 | 6.0 |
| BC-MLP | Cross-Attn | 5.8 | 33.4 | 12.0 |
| BC-MLP | Ours (RGB-S) | **12.4** | **35.0** | **32.0** |
| ACT | Vision-Only | 29.4 | 38.4 | 41.0 |
| ACT | CLiP | 28.5 | 54.2 | 54.0 |
| ACT | Ours (RGB-S) | **38.4** | **63.4** | **57.0** |
| DP | Vision-Only | 39.7 | 60.9 | 52.0 |
| DP | Cross-Attn | 38.4 | 59.2 | 61.0 |
| DP | Ours (RGB-S) | **59.1** | **68.3** | **69.0** |

DP + RGB-S 의 Pick-and-Place 세부값은 Normal 78.5 / Occluded 39.7 로, vision-only(71.9 / 7.4)·Concat(72.7 / 14.9)·Cross-Attn(42.1 / 34.7) 대비 특히 가림에서 큰 격차를 보입니다.

> "Overall, across tasks and policy architectures, RGB-S achieves the best or second-best performance in most settings." (§4.1, Table 1)
(한글 해설 — 단순히 촉각을 넣는다고 항상 좋아지지 않으며(Concat·FiLM·CLIP·Cross-Attn 은 어떤 설정에선 vision-only 보다도 떨어짐), RGB-S 만이 이미지 정합 saliency 덕분에 대부분 설정에서 최고/차상위를 유지한다는 것이 1번 관찰입니다.)

**실제 로봇(Table 2)** — DP 정책으로 3 과제, Normal/Occluded 각 20 trial:

| Method | Normal Avg.(%) | Occluded Avg.(%) |
|---|---|---|
| Vision-Only | 56.7 | 10.0 |
| Concat | 55.0 | 13.3 |
| Cross-Attn | 30.0 | 25.0 |
| Ours (RGB-S) | **66.7** | **51.7** |

> "Real-world experiments show that explicit RGB-S grounding in the image domain improves real-world occluded manipulation success rates by $`26.7`$ percentage points over the strongest implicit visuo-tactile baseline." (Abstract)
(한글 해설 — 가림 조건에서 RGB-S 51.7% 는 최강 암시적 baseline(Cross-Attn 25.0%) 대비 +26.7%p 입니다. 시뮬레이션 결과가 실제 로봇으로 전이됨을 입증합니다.)

**Ablation 1 — 렌더링 방식(Table 3, DP·Pick-and-Place)** — 어떤 형태로 촉각을 그려 넣을지 비교:

| Variant | Normal | Occluded | Average |
|---|---|---|---|
| Vision-only | 71.9 | 7.4 | 39.7 |
| RGB Overlay | 65.3 | 33.1 | 49.2 |
| Binary RGB-S | 65.3 | 27.3 | 46.3 |
| Ours (Force-aware RGB-S) | **78.5** | **39.7** | **59.1** |

각 행이 분리하는 것: **RGB Overlay** 는 RGB 위에 촉각을 직접 그려 3채널 유지(채널 추가 없음), **Binary RGB-S** 는 4번째 채널을 쓰되 힘 크기 없이 접촉 위치만 상수 강도로 인코딩. 정상 조건에선 차이가 작으나 가림에선 두 촉각 증강 변형 모두 vision-only 를 크게 능가하며, Binary 만으로도 "접촉 위치"가 강한 기하 prior 임을 보입니다. 그러나 force-aware 가 두 조건 모두 최고로, 연속 힘 크기가 binary 접촉을 넘는 상호작용 정보를 전달함을 시사합니다.

**Ablation 2 — 공간 정합 민감도(Table 4)** — saliency map 에 픽셀 shift $`(\Delta_{x},\Delta_{y})`$ 를 주입한 강건성. shift 는 $`S_{\Delta}(x,y)=S\big((x-\Delta_{x})\bmod W,\,(y-\Delta_{y})\bmod H\big)`$ 로 구성(RGB 는 그대로):

| Setting / Condition | 0 px | 25 px | 50 px | 100 px |
|---|---|---|---|---|
| Sim · Normal | 78.5 | 66.9 | 70.2 | 62.0 |
| Sim · Occ. | 39.7 | 32.2 | 24.0 | 9.9 |
| Real · Normal | 9/20 | 8/20 | 5/20 | 5/20 |
| Real · Occ. | 7/20 | 4/20 | 3/20 | 3/20 |

> "the overall success rate remains above $`30\%`$ when the offset is below 25 pixels, confirming that policy learning is generally robust to minor misalignment in tactile saliency." (§4.3, Table 4)
(한글 해설 — 정상 시각에선 심한 offset 에도 완만히 감소하나, 가림에선 offset 증가에 따라 더 크게 저하 — 즉 시각이 막혔을 때 정책이 saliency 의 *정확한 위치*에 더 의존함을 드러냅니다. 캘리브레이션 품질이 가림 상황 성능과 직결된다는 뜻입니다.)

**Ablation 3 — 융합 구조(Table 5, DP·Pick-and-Place)** — 언제 saliency 를 주입하는가:

| Architecture | Normal | Occ. |
|---|---|---|
| Late Fusion | 73.6 | 35.5 |
| Intermediate | 73.6 | 22.3 |
| Ours (Early) | **78.5** | **39.7** |

> "our early conditioning approach consistently achieves the highest success rates in both normal and occluded settings." (§4.3, Table 5)
(한글 해설 — Late(별도 인코더 후 pooling+concat)·Intermediate(중간 단계 element-wise addition) 대비, 첫 시각 레이어에서 촉각 saliency 를 주입하는 early conditioning 이 가장 좋습니다. 특히 Intermediate 는 가림에서 22.3 으로 급락 — 주입 위치가 성능을 좌우합니다.)

**효율(Table 6, ms/step)** — 3D 점군 baseline 과의 대비:

| Model | Denoising | Pre-denoising | Overall |
|---|---|---|---|
| Vision-Only | 64.26 | 10.10 | 74.36 |
| Point Cloud | 76.72 | 95.12 | 171.84 |
| Ours (RGB-S) | 64.24 | 21.06 | 85.30 |

> "RGB-S is much faster, with a preprocessing latency of $`21.06\pm 4.54`$ ms; saliency generation itself takes only $`6.14\pm 1.89`$ ms." (§B.2, Table 6)
(한글 해설 — 명시적 3D grounding(PointNet+depth)은 전처리 95.12ms 로 무겁지만, RGB-S 는 saliency 생성이 6.14ms 에 불과해 표준 2D diffusion 정책의 denoising 속도를 그대로 유지합니다. 명시 grounding 의 강건성을 3D 의 비용 없이 얻는다는 주장입니다.)

**가림 하 attention(Fig. 6)** — Grad-CAM 으로 정책의 특징 attention 을 시각화:

![Figure 6 — Grad-CAM under occlusion](https://arxiv.org/html/2606.08765/x6.png)

> "Figure 6: Grad-CAM result of tasks in simulation and real-world." (§B.3)
(한글 해설 — 가림 시 baseline 은 과제 관련 영역에서 attention 이 이탈하나, RGB-S 는 손 주변에 계속 집중 — 시각이 불확실할 때 투영 촉각 단서에 의존하도록 학습됨을 보입니다.)

---

## ⚖️ 한계

- **캘리브레이션·기구학 정확도 의존(저자 명시)** — RGB-S 는 기하 투영에 의존하므로 캘리브레이션 품질과 로봇 configuration 정확도에 성능이 묶입니다. 저자는 외부 셋업의 미보정 물리 drift, joint backlash, link 변형, 접촉 시 구조적 컴플라이언스가 모두 cross-modal 정합을 왜곡할 수 있다고 적습니다. Table 4 의 가림 하 offset 민감도가 이를 정량적으로 뒷받침합니다 — 정합이 깨지면 가림 상황의 이득이 가장 먼저 무너집니다.
- **깊이 모호성(depth ambiguity, §B.1)** — 단일 2D saliency 는 카메라 반대편 면의 접촉도 전경으로 투영되어, 접촉이 물체 앞면인지 뒷면인지, 어느 센서가 활성인지 구분하지 못합니다. 저자는 proprioception·다중 view·offset 강건성으로 완화된다고 주장하지만, 이는 본질적으로 *2D 투영이 3D 접촉 상태를 손실 압축*한다는 구조적 한계입니다.
- **per-finger 접촉 귀속(attribution) 소실(추론)** — 44개 노드를 단일 saliency 채널로 $`\max`$ 집계하면서 "어느 손가락이 무엇을 누르는가"의 개별 귀속이 사라집니다. 손가락별 접촉/slip 의 정밀 추론이 필요한 인핸드 조작에서는 이 압축이 정보 병목이 될 수 있습니다.
- **백본 일반성 미검증(추론)** — zero-init 트릭은 ResNet-18 의 첫 conv 레이어에서만 시연되었습니다. ViT 계열 patch-embed 나 더 큰 사전학습 백본에서도 동일하게 prior 를 보존하는지는 보이지 않았습니다 (저자는 "원리상 인코더 선택과 무관"하다고 주장만).
- **DP 편중 평가(추론)** — 실제 로봇 평가와 ablation 전부 Diffusion Policy 에 집중됩니다. ACT·BC-MLP 는 시뮬레이션에서만, 그것도 RGB-S 이득이 DP 만큼 일관되지 않습니다(예 ACT·Pick-and-Place Occluded 13.2 로 CLIP 19.0 보다 낮음). 정책 비종속 주장은 DP 에서 가장 강합니다.

---

## ♻️ 재현성

- **코드/데이터** — 프로젝트 페이지(touch-as-saliency.github.io)가 존재하나, 본문 메타에 별도 GitHub/데이터셋 공개 링크는 명시되지 않았습니다(코드 공개 여부 미확정). 구현은 LeRobot 기반(Appendix E)이라 재현 좌표가 비교적 명확합니다.
- **하드웨어** — xArm6 + LEAP Hand(공개 하드웨어), TwinTac fingertip + FSR, RealSense D435 ×2. 캘리브레이션 EasyHEC, 텔레오퍼레이션 ARCap + Meta Quest 3 + Manus Quantum Metaglove — 모두 외부 공개 도구라 셋업 재현 가능성이 높습니다.
- **시뮬레이션** — 촉각 시뮬레이터는 ETac 기반. 과제별 시연 수·프레임 수·초기화 범위가 Appendix A 에 상세 기재(예 Sim Pick-and-Place 53 demos / 20,212 frames).
- **학습 자원** — A40 학습 / RTX 4090 배포, 모든 정책 120K train steps, batch 64 (Table 7). 하이퍼파라미터가 표로 제공되어 재현 친화적입니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P2(structured multimodal observation fusion)** — 본 논문의 일차 정착지입니다. RGB-S 는 P2 가 추구하는 "관측 elevation" 의 한 구현으로, 세 D# 를 직접 건드립니다:
  - **D10(heterogeneous modality fusion beyond concat)** — flat concat 의 대안으로 *이미지 공간 정합*을 제시. 단 P2 의 D10 v1 은 cross-attention/asymmetric 융합이고, RGB-S 는 입력 채널 융합이라 *메커니즘이 다른 경쟁 가설*입니다.
  - **D11(proprio-tactile-force token construction)** — FK 로 촉각을 공간 grounding 한다는 점은 D11 의 "swappable sensor head + common token format" 철학과 정렬됩니다. 그러나 D11 v1 의 핵심인 *per-finger 토큰(10 finger + 2 palm)·접촉/slip aux head* 와 달리, RGB-S 는 모든 노드를 단일 saliency 채널로 집계해 손가락별 귀속을 보존하지 않습니다 — D11 비협상 조건 (2)(접촉 관련 특징 보존)과 *긴장* 관계입니다.
  - **D8(multi-camera spatial-geometric grounding)** — 본 논문은 명시적 3D 점군 grounding 의 *2D 이미지 평면 대안*입니다. D8 v1 의 3D-consistent 임베딩과 다른 노선이지만, "다중 view 로 단일 투영 모호성을 줄인다"(§B.1)는 멀티카메라 정합 논의를 공유합니다.
- **P4(VLM 사전학습 보존)** — zero-init conditioning 은 사전학습 시각 표현을 보존하며 새 모달리티를 주입하는 장치로, **D20(prior-preservation strategy)** 의 구체 사례입니다. D20 v1 은 action-side adapter + conservative SFT 인데, RGB-S 의 zero-init 채널은 *입력측 adapter* 로서 "초기 시점 prior 동일성 보장 → 점진 흡수" 라는 동일한 보존 원리를 다른 위치에서 실현합니다. 확장하면 **D19(adaptation range)** 의 freeze 대비 "최소 침습 채널 추가" 라는 중간 옵션을 제공합니다.
- **Identity 지지/긴장** — P2 Identity 의 "observation elevation — 공간 정보 유지·정합, 암시적 학습 거부" 를 강하게 *지지*합니다. 반면 "per-finger/palm 접촉 귀속 보존" 축에서는 단일 채널 집계라 *긴장*합니다.
- **경쟁자 함의** — P2 §5 핀 논문 **ViTacFormer**(cross-attention visuotactile, D10/D11)와 직접 경쟁 비교군이며, 본 논문은 명시 기하 prior 가 가림에서 cross-attention 을 능가함을 보입니다. 비핀 methodology base **DexViTac**(kinematic-grounded tactile encoding, D11/D12)와 *FK grounding* 발상을 공유하고, **SaTA**(FiLM spatial-tactile) 와 인접합니다.

---

## ✨ 핀 논문 대비 델타

- **vs ViTacFormer (P2 핀, [arXiv:2506.15953](https://arxiv.org/abs/2506.15953))** — ViTacFormer 는 cross-attention 으로 시각-촉각 대응을 *암시적으로* 학습합니다. RGB-S 의 진짜 새로움은 그 대응을 FK+캘리브레이션으로 *학습 없이 못 박는다*는 점, 그리고 별도 융합 모듈 대신 사전학습 인코더의 입력 채널 하나로 끝낸다는 경량성입니다. 본 논문 Table 1·2 에서 Cross-Attn baseline 을 가림 조건에서 일관되게 능가합니다.
- **vs FiLM/CLIP 계열 융합 (P2 methodology base FiLM [arXiv:1709.07871](https://arxiv.org/abs/1709.07871))** — FiLM 은 촉각으로 시각 특징을 변조(채널 단위 scale/bias)할 뿐 *공간 위치* 정보를 부여하지 않습니다. RGB-S 의 델타는 촉각에 명시적 픽셀 좌표를 주어 spatial+semantic 대응을 동시에 제공한다는 것입니다.
- **vs P4 핀 ConSFT ([arXiv:2605.08879](https://arxiv.org/abs/2605.08879))** — ConSFT 는 adaptation 단계의 conservative importance weighting 으로 forgetting 을 줄입니다. RGB-S 의 zero-init 은 *아키텍처 초기화*로 prior 동일성을 보장하는 직교(orthogonal) 보존 레버 — 손실 정규화가 아니라 초기 가중치 0 으로 같은 목표를 달성합니다.

---

## ⚙️ 의사결정 함의

- **입력측 prior-preservation 어댑터(D20) 후보 추가** — 우리 VLA 시각 백본(PaliGemma/SigLIP 계열, D19 freeze 기조)에 촉각 saliency 채널을 zero-init 으로 덧붙이는 옵션을 D20 보존 레버 목록에 올릴 수 있습니다. 구체 config: vision patch-embed/첫 conv 의 입력 채널을 +1 확장, 신규 채널 가중치 $`\mathbf{W}_{s}=\mathbf{0}`$ 초기화, 나머지는 freeze 유지. action-side adapter(현 D20 v1)와 병행 가능한 *입력측* 옵션입니다.
- **촉각 토큰 vs saliency map 의 분기점(D11)** — 우리 D11 v1 은 per-finger 토큰(10 finger + 2 palm) 경로입니다. RGB-S 는 동일한 FK grounding 을 쓰되 출력 형태가 *이미지 채널*이라 손가락 귀속을 버립니다. 의사결정: "공간 정합(RGB-S) vs 손가락 귀속(토큰)" 중 무엇이 인핸드 reorientation 에 더 중요한지 ablation 필요. 두 표현을 동시에 줄 수도 있음(saliency 채널 + 토큰 병행).
- **렌더링 하이퍼파라미터** — 채택 시 고정해야 할 값: Gaussian $`\sigma`$(sim 은 force-dependent $`\sigma_{\min}=4,\sigma_{\max}=12`$), 힘 정규화 $`\tilde{f}=\tanh(\gamma f/F_{\mathrm{limit}})`$ 의 $`\gamma`$ · $`F_{\mathrm{limit}}`$, 겹침 처리 $`\max`$ 집계, 주입 위치 = early(첫 레이어, Table 5 근거).
- **메트릭** — 정상 vs 가림 성공률 격차를 핵심 지표로 채택. 가림 강건성이 RGB-S 이득이 가장 두드러지는 축입니다.

---

## ⚠️ 먼저 검증할 실패 모드

가장 싼 sanity check 부터:

1. **센서 형식 불일치(가장 싼 확인)** — RGB-S 는 *이산 노드별 스칼라 힘*(FSR/taxel 44개)을 전제로 점을 찍습니다. 우리 Sharpa Hand 는 vision-based Deform Map(~320×240/fingertip)으로, 노드별 스칼라가 아니라 *조밀 변형장*입니다. 먼저 확인: Deform Map 에서 투영 가능한 "이산 접촉 노드 + 스칼라 힘" 을 어떻게 정의할 것인가? (변형장 평균? peak 위치?) 이 정의가 불가능하면 식 2–4 가 그대로 전이되지 않습니다.
2. **per-finger 귀속 손실의 비용** — 단일 saliency 로 $`\max`$ 집계 시 D11 의 접촉/slip aux head 가 노리는 손가락별 신호가 뭉개집니다. 싼 확인: in-hand cube rotation(Phase 1)에서 단일 saliency 채널만으로 손가락별 slip 을 정책이 구분하는지 — 구분 못 하면 System0(P3) 트리거 신호가 약화될 위험.
3. **ViT patch-embed zero-init 동작** — 우리 백본은 conv 기반 ResNet 이 아니라 ViT patch-embed 일 가능성이 큽니다. 싼 확인: patch-embed conv 에 채널 +1 zero-init 시 정말 초기 출력이 사전학습과 bit-identical 한가(positional embedding·LayerNorm 통계 영향 점검).
4. **인핸드 자기가림 깊이 모호성** — 본 논문 과제는 tabletop pick/push/drawer 로 카메라가 손-물체를 비교적 정면에서 봅니다. 우리 Phase 1 in-hand reorientation 은 손이 물체를 감싸 *자기가림*이 심하고 접촉이 물체를 둘러쌉니다 — §B.1 깊이 모호성이 우리 환경에서 훨씬 악화됩니다. 다중 view + proprioception 으로 충분히 완화되는지 검증 필요.
5. **flow-matching VLA 전이** — RGB-S 이득은 DP(diffusion)에서 가장 강합니다. 우리 capability source 는 π 플로우 매칭 액션 전문가입니다. saliency 채널이 flow-matching 헤드/π 백본에서도 동일한 가림 강건성을 주는지(DP·ACT·BC 만 검증됨) 확인 전까지 일반화 가정 금지.
6. **캘리브레이션 예산** — Table 4 는 25px offset 이내에서만 가림 이득이 유지됨을 보입니다. 우리 셋업에서 EasyHEC 수준의 외부 캘리브레이션 + Sharpa FK 정확도가 이 임계 안에 드는지, 접촉 중 link 변형까지 포함해 실측 필요.

---

## 💡 컨텍스트 제안

- **P2 §5 Tracked Literature 핀 후보** — RGB-S 는 D10/D11 의 강한 증거(가림 조건에서 cross-attention·FiLM·CLIP 을 일관되게 능가)이며, 기존 핀 ViTacFormer 의 직접 비교 상위 결과입니다. 핀 cap(8) 중 현재 5편이므로, RGB-S 를 **P2 핀에 추가**하거나(명시 기하 grounding 노선 대표) 최소한 methodology base 의 DexViTac 옆에 등재 제안. 인간 판단 필요.
- **P4 D20 cross-pillar 메모** — zero-init 입력 채널 conditioning 을 D20 prior-preservation 의 *입력측 어댑터* 사례로 P4 §5 methodology base 에 메모 추가 검토(현재 D20 은 action-side adapter + conservative SFT 중심). 직교 레버로 가치가 있습니다.
- **catalogs** — 데이터셋/벤치마크 신규 공개가 없으므로 `catalogs/` 등재 대상 아님(method-only).

> 💡 base 매핑은 `/implement-design analysis/2606.08765/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
