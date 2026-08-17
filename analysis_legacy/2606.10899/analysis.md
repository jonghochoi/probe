# Paper Analysis — MV-Actor: Aligning Multi-View Semantics and Spatial Awareness for Bimanual Manipulation

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | MV-Actor: Aligning Multi-View Semantics and Spatial Awareness for Bimanual Manipulation |
| 저자 | Yinchen Tian, Huan Li, Muyao Peng, Xi Wang, Yan Wang, You Yang |
| 링크 | [arXiv:2606.10899](https://arxiv.org/abs/2606.10899) · [GitHub](https://github.com/TianYinchen56/MV-Actor) |
| 발행일 / 버전 | 2026-06-09 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-15 |
| 관련 Pillar | P2, P1, P0 |
| 태그 | vla-arch, sim2real |

---

## 🧭 한 줄 요약 (TL;DR)

MV-Actor 는 양팔(bimanual) 조작의 다중 카메라 관측을 "독립 인코딩 / 얕은 융합" 으로 다루던 기존 정책과 달리, **calibrated reprojection 으로 물리적으로 대응되는 영역끼리 의미(semantic) 증거를 공유**하고 **feed-forward 재구성 모델(Pi3X) 의 공간 토큰으로 신뢰할 수 있는 공간 인지를 주입**하며, 소비자급 depth 노이즈는 별도 **Guided Metric Depth Repair** 로 복원하는 통합 semantic-spatial 표현 프레임워크입니다. PerAct2 벤치마크에서 평균 성공률 87.8% 로 SOTA(3DFA 85.1%)를 넘고, 실로봇 ARK-Lift 에서도 RGB/RGB-D baseline 을 모두 능가합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 양팔 시스템은 손목·외부 카메라 등 다중 시점을 갖지만, 대부분의 정책이 각 카메라 스트림을 *별개의 시각 입력* 으로 처리해 시점 간 지각이 충분히 공유되지 않습니다. 다중 시점에서 일관되고 공간적으로 신뢰할 수 있는 통합 표현을 만드는 것이 목표입니다.
- **기존 접근의 한계** — 다중 시점 표현은 두 갈래입니다. (1) 각 시점을 독립 인코딩 후 정책 레벨에서 feature 를 융합 — 시점 간 대응(correspondence)을 고려하지 않음. (2) sensor depth 로 voxel/point cloud 같은 공유 3D 공간으로 lifting — 정렬은 명시적이지만 depth 센서 품질에 취약. 둘 다 "의미 공유" 와 "신뢰할 수 있는 공간 인지" 를 동시에 해결하지 못합니다.
- **본 논문의 가설** — 같은 물리적 영역에 대응되는 시점 간 feature 끼리 의미를 공유하고, feed-forward 재구성 모델이 RGB 만으로 산출하는 암묵적 기하 prior 로 공간 인지를 보강하면, 취약한 depth 정렬 없이도 더 강한 지각 기반을 만들 수 있다는 것입니다.
- **왜 지금 중요한가** — DUSt3R/Pi3 같은 feed-forward 재구성 모델이 다중 시점 RGB 만으로 dense pointmap·spatial token 을 산출할 수 있게 되었고, 소비자급 RGB-D 카메라(예: RealSense D405)는 반사·투명 표면에서 hole·noise 가 잦아 raw depth lifting 이 불안정하기 때문입니다.

---

## 🧩 핵심 기여

- **MV-Actor** — 다중 카메라 관측을 "같은 장면의 관련된 여러 시점" 으로 취급해, 의미 공유와 공간 인지를 통합한 양팔 조작 지각 프레임워크를 제안.
- **Multi-view Semantic Interaction** — calibrated reprojection 으로 물리적으로 대응되는 32×32 토큰 grid 영역 사이에서만 의미 증거를 전파(3D KNN 의 인접-그러나-다른-표면 오염 회피).
- **Semantic-Spatial Token Interaction** — Pi3X feed-forward 공간 토큰에 의미 토큰이 per-head sigmoid-gated attention 으로 attend 해 공간 인지를 주입.
- **Head-Aware Routing Gate** — position 헤드와 rotation 헤드가 semantic/spatial 잔차(residual)를 서로 다른 비율로 받도록 4개 sigmoid gate 로 적응적 라우팅(단순 합산의 간섭 회피).
- **Guided Metric Depth Repair** — raw sensor depth + RGB 텍스처 + Pi3X feed-forward depth prior 를 3-branch U-Net 으로 융합해 metric scale 을 유지한 채 hole·boundary 를 복원, 3D RoPE 의 metric anchor 신뢰도 확보.
- PerAct2 SOTA(87.8%) + 실로봇 ARK-Lift 에서 voxel/point-cloud/RGB-only baseline 대비 우위 실증.

---

## 🔑 기술 키워드

- **Bimanual manipulation** — 두 end-effector 의 협응·접촉 추론·시간적 정밀성을 요구하는 양팔 조작. 본 논문의 과제 도메인이자 다중 카메라 동기.
- **Multi-view perception** — 여러 카메라 시점에서 장면을 관측·통합하는 지각. 본 논문은 "시점 간 의미 공유 + 공간 인지" 로 이를 재정의.
- **Feed-forward reconstruction model** — 다중 시점 RGB 만으로 dense pointmap·spatial token 을 한 번의 순방향으로 산출하는 모델(DUSt3R, MoGe2, Pi3 계열). MV-Actor 의 공간 토큰 공급원.
- **Pi3X** — Pi3 계열 feed-forward 재구성 모델. 다중 시점 기하 구조를 인코딩한 공간 토큰과 depth prior 를 제공하는 frozen 모듈.
- **Reprojection-consistent correspondence** — 한 시점의 3D anchor 를 다른 시점 token grid 로 투영해, grid-plane 정렬 + depth 일관성을 모두 만족하는 토큰만 대응으로 인정하는 매칭. 의미 전파를 "같은 물리적 위치" 로 제한하는 핵심 장치.
- **Semantic token / Spatial token** — 전자는 frozen CLIP-FPN 의 32×32 의미 grid, 후자는 Pi3X 의 기하 grid. 두 토큰 흐름을 정렬·상호작용시키는 것이 방법의 골자.
- **Head-Aware Routing Gate** — position/rotation 헤드별로 semantic·spatial 잔차의 혼합 비율을 적응 결정하는 경량 gating. "헤드마다 선호하는 증거가 다르다" 는 관찰의 구현.
- **Guided Metric Depth Repair** — 소비자급 센서 depth 의 hole·noise 를 RGB + feed-forward depth prior 로 복원하는 3-branch U-Net. metric scale 보존이 목적.
- **Metric point cloud / 3D RoPE** — 복원된 depth 로 모든 시각 토큰에 robot-frame metric 좌표를 부여하고, 3D Rotary Position Encoding 으로 정책 backbone 에 공간 구조를 입력.
- **PerAct2** — voxel 기반 정책을 양팔로 확장한 다중 시점 양팔 조작 시뮬레이션 벤치마크. 본 논문의 주 평가 무대.

---

## 🔬 방법론

### 직관

MV-Actor 의 출발점은 "다중 카메라는 서로 다른 입력이 아니라 같은 장면의 여러 관측" 이라는 관점입니다. 한 시점에서 팔이나 다른 물체에 가려진 영역은 다른 시점에서 잘 보이므로, 같은 물리적 위치를 가리키는 토큰끼리 의미 증거를 교환하면 가림(occlusion) 에 강한 표현을 얻을 수 있습니다. 다만 이 교환을 "3D 공간에서 가까운 점끼리" 묶으면 인접하지만 물리적으로 다른 표면이 섞이므로, MV-Actor 는 **calibrated reprojection 으로 grid 정렬과 depth 일관성을 둘 다 만족하는 토큰만** 대응으로 인정합니다.

두 번째 축은 공간 인지입니다. 2D 의미 토큰만으로는 물체가 *무엇* 인지는 알아도 metric 3D 공간에서 *어디* 인지를 표현하기 어렵습니다. MV-Actor 는 raw RGB 만으로 기하를 추정하는 feed-forward 재구성 모델(Pi3X) 의 공간 토큰에 의미 토큰이 attend 하게 해, 취약한 센서 depth 에 의존하지 않고 공간 인지를 주입합니다.

세 번째로, 위치(position) 예측과 회전(rotation) 예측이 필요로 하는 증거가 다르다는 점을 인정합니다. 단순히 의미·공간 잔차를 합치면 간섭이 생기므로, **Head-Aware Routing Gate** 가 헤드별로 두 잔차의 혼합 비율을 적응적으로 정합니다.

마지막으로, 모든 토큰의 metric 좌표는 depth 에서 back-projection 되므로 depth 품질이 전체 파이프라인을 좌우합니다. 소비자급 센서의 hole·noise 를 RGB 경계 단서와 feed-forward depth prior 로 복원하는 **Guided Metric Depth Repair** 가 이 신뢰성을 확보합니다.

### 아키텍처

![Figure 2 — MV-Actor overview](https://arxiv.org/html/2606.10899/x2.png)

> "Figure 2: MV-Actor overview. Given multi-view RGB-D observations, MV-Actor first repairs degraded sensor depth by combining RGB texture and a Pi3X feed-forward depth prior, producing metric depth that can be back-projected into the robot frame. CLIP features provide semantic scene tokens, while Pi3X [44] provides feed-forward spatial tokens. Multi-view Semantic Interaction exchanges semantic evidence across physically corresponding regions, and Semantic-Spatial Token Interaction enables semantic tokens to acquire spatial awareness from the feed-forward spatial tokens. The Head-Aware Routing Gate forms enhanced scene tokens and routes them to position and rotation/gripper prediction streams before action decoding." (§3)
(한글 해설 — depth 복원 → metric back-projection → 의미/공간 토큰 구성 → 두 상호작용 → head-aware 라우팅 → action decoding 의 전체 파이프라인을 한 장에 담은 개요입니다.)

**입력/출력 (§3.1).** 시점 집합 $`\mathcal{V}=\{1,\dots,V\}`$ 에 대해 시각 $`t`$ 의 관측은

$$O_{t}=\left(\{I_{t}^{(v)},D_{t}^{(v)}\}_{v\in\mathcal{V}},\ell,q_{t}\right),$$

> "the policy receives multi-view RGB-D observations, a language instruction, and robot proprioception" (§3.1)
(한글 해설 — $`I_{t}^{(v)}`$ · $`D_{t}^{(v)}`$ 는 시점 $`v`$ 의 RGB·depth, $`\ell`$ 은 언어 지시, $`q_{t}`$ 는 proprioception 입니다.)

각 시점에서 frozen CLIP feature 가 $`32\times 32`$ 의미 토큰 grid 로 추출되고, 각 토큰은 robot frame 으로 back-projection 됩니다:

$$p_{i}^{(v)}=T_{\mathrm{base}\leftarrow\mathrm{cam}}^{(v)}\cdot D^{(v)}(u_{i})\cdot K^{(v)-1}\tilde{u}_{i},$$

> "where $`K^{(v)}`$ denotes camera intrinsics, $`T_{\mathrm{base}\leftarrow\mathrm{cam}}^{(v)}`$ is the camera-to-base extrinsic transform, and $`\tilde{u}_{i}`$ is the homogeneous pixel coordinate, forming a metric point cloud as the shared spatial carrier." (§3.1)
(한글 해설 — 의미 토큰이 metric point cloud 라는 공유 공간 carrier 에 anchor 되며, 이 좌표가 이후 모든 상호작용의 기준이 됩니다. 병렬로 Pi3X 가 공간 토큰을, frozen CLIP text encoder 가 언어 토큰을 제공합니다.)

정책은 action chunk $`A_{t}=\{a_{\tau}\}_{\tau=t}^{t+H-1}`$ 를 예측하며, 각 양팔 액션은

$$a_{\tau}=\left\{(p_{\tau}^{\mathrm{left}},r_{\tau}^{\mathrm{left}},g_{\tau}^{\mathrm{left}}),(p_{\tau}^{\mathrm{right}},r_{\tau}^{\mathrm{right}},g_{\tau}^{\mathrm{right}})\right\},$$

(한글 해설 — $`p`$ · $`r`$ · $`g`$ 는 각각 end-effector 위치·회전·그리퍼 상태입니다. 좌/우 두 팔에 대해 각각 산출됩니다.)

![Figure 3 — Multi-view and semantic-spatial token interaction](https://arxiv.org/html/2606.10899/x3.png)

> "Figure 3: Multi-view and semantic-spatial token interaction. MV-Actor builds semantic tokens from CLIP-FPN and spatial tokens from the Pi3X aggregator. The upper branch performs Multi-view Semantic Interaction: semantic queries retrieve key/value tokens from reprojection-consistent regions in other calibrated views. The lower branch performs Semantic-Spatial Token Interaction: semantic queries attend to Pi3X spatial tokens to inject spatial awareness. The two residuals are fused into the final scene tokens." (§3.2)
(한글 해설 — 상단 분기는 시점 간 의미 공유, 하단 분기는 의미↔공간 토큰 상호작용으로, 두 잔차가 최종 scene token 으로 융합됨을 보여줍니다.)

### Multi-view Semantic Interaction

가림으로 한 시점의 의미 토큰이 결정적 증거를 놓칠 수 있으므로, 다른 시점에서 reprojection 으로 증거를 탐색합니다. 시점 $`v`$ 의 3D anchor $`p_{i}^{(v)}`$ 를 대상 시점 $`u`$ 의 토큰 grid 로 투영합니다:

$$\hat{x}_{u}=R_{u}p_{i}^{(v)}+t_{u},\quad\hat{z}_{u}=[\hat{x}_{u}]_{z},\quad\hat{c}_{u}=\Pi\!\left(K_{u}^{\mathrm{grid}}\hat{x}_{u}\right),$$

> "where $`(R_{u},t_{u})`$ transforms robot-frame points into the camera frame of view $`u`$, $`K_{u}^{\mathrm{grid}}`$ is the camera intrinsic matrix scaled from image resolution to the $`32\times 32`$ token grid, $`\Pi([x,y,z]^{\top})=(x/z,y/z)`$ denotes perspective normalization, and $`\hat{z}_{u}`$ is the camera-frame depth." (§3.2)
(한글 해설 — anchor 를 대상 시점의 token grid 좌표 $`\hat{c}_{u}`$ 와 카메라-프레임 depth $`\hat{z}_{u}`$ 로 변환하는 단계입니다.)

$`\hat{c}_{u}`$ 주변 radius-1 local window 에서 후보 토큰을 찾되, grid-plane 정렬과 depth 일관성을 모두 만족해야 유효합니다:

$$\|\hat{c}_{u}-c_{j}^{(u)}\|_{2}\leq\epsilon_{\mathrm{reproj}},$$

$$|\hat{z}_{u}-z_{j}^{(u)}|\leq\epsilon_{\mathrm{depth}},$$

> "Eq. (5) enforces local grid alignment, while Eq. (6) rejects perspective-overlap artifacts where two different 3D surfaces project to a similar image location." (§3.2)
(한글 해설 — Eq.(5)는 grid 평면 정렬을, Eq.(6)은 서로 다른 3D 표면이 비슷한 화소로 투영되는 perspective-overlap 오류를 걸러냅니다. 두 오차의 합이 최소인 토큰만 대응 집합 $`\mathcal{C}_{i}^{(v)}`$ 에 남고, 어느 후보도 만족 못 하면 validity mask 로 그 시점을 attention 에서 제외합니다.)

유효 후보에 대해 masked local attention 잔차로 현재 토큰을 갱신합니다:

$$\alpha_{i,uj}=\mathrm{softmax}_{\mathcal{C}_{i}^{(v)}}\!\left(\frac{(W_{Q}s_{i}^{(v)})^{\top}W_{K}s_{j}^{(u)}}{\sqrt{d_{h}}}\right),$$

$$\Delta s_{i}^{\mathrm{sem}}=\lambda_{s}W_{O}\sum_{(u,j)\in\mathcal{C}_{i}^{(v)}}\alpha_{i,uj}W_{V}s_{j}^{(u)}.$$

> "The softmax is normalized only over valid candidates; a token with no valid match receives a zero residual. We apply this block twice with $`N_{h}=8`$ heads and $`\lambda_{s}=0.1`$." (§3.2)
(한글 해설 — softmax 가 유효 후보 위에서만 정규화되어, 대응이 없는 토큰은 잔차 0 을 받습니다. 이 블록을 head 8개·잔차 스케일 0.1 로 2회 적용합니다.)

### Semantic-Spatial Token Interaction

2D 의미 토큰이 3D 구조를 표현 못 하므로, 각 의미 토큰이 정렬된 feed-forward 공간 토큰에 attend 합니다. Pi3X 공간 토큰은 차원 $`d`$ 로 투영·layer-norm 후 nearest-neighbor 복사로 $`32\times 32`$ grid 에 맞춰 정렬됩니다($`\tilde{g}_{i}^{(v)}=\mathrm{Align}(\mathrm{LN}(W_{S}U^{(v)}),c_{i}^{(v)})`$). 각 의미 토큰은 per-head sigmoid-gated 잔차로 attend 합니다:

$$\beta_{i,h}^{(v)}=\sigma\!\left(\frac{(W_{Q,h}^{\mathrm{spa}}s_{i}^{(v)})^{\top}W_{K,h}^{\mathrm{spa}}\tilde{g}_{i}^{(v)}}{\sqrt{d_{h}}}\right),$$

$$\Delta s_{i}^{\mathrm{spa},(v)}=\lambda_{\mathrm{spa}}W_{O}^{\mathrm{spa}}\mathrm{Concat}_{h}\left(\beta_{i,h}^{(v)}W_{V,h}^{\mathrm{spa}}\tilde{g}_{i}^{(v)}\right),$$

> "where $`\beta_{i,h}^{(v)}`$ is a scalar gate for head $`h`$, broadcast over the head dimension, and $`\lambda_{\mathrm{spa}}=0.1`$." (§3.2)
(한글 해설 — softmax attention 이 아니라 head 별 scalar sigmoid gate $`\beta_{i,h}^{(v)}`$ 가 정렬된 공간 토큰을 얼마나 받을지 조절하는 형태입니다. 잔차 스케일은 0.1.)

두 분기는 공유 base scene token $`s=\{s_{i}\}`$ 위에서 병렬로 작동해 상보적 잔차 $`\Delta s^{\mathrm{sem}}`$ · $`\Delta s^{\mathrm{spa}}`$ 를 산출합니다.

> "Keeping these residuals separate is important because position and rotation heads may prefer different mixtures of semantic and spatial evidence." (§3.2)
(한글 해설 — 두 잔차를 분리해 두는 것이 다음 Head-Aware Routing Gate 의 전제입니다.)

### Head-Aware Routing Gate

base scene token $`s`$, 지시 토큰 $`e_{\ell}`$, proprioception $`q_{t}`$, 두 잔차로 context vector 를 만들고:

$$z_{\mathrm{route}}=\Big[\mathrm{Pool}(s),\mathrm{Pool}(e_{\ell}),\psi(q_{t}),\mathrm{Pool}(\Delta s^{\mathrm{sem}}),\mathrm{Pool}(\Delta s^{\mathrm{spa}})\Big],$$

2-layer MLP 가 4개 sigmoid gate 를 예측합니다:

$$\gamma=\sigma(\mathrm{MLP}_{\mathrm{route}}(z_{\mathrm{route}})),$$

$$s^{h}=s+\gamma_{\mathrm{sem}}^{h}\Delta s^{\mathrm{sem}}+\gamma_{\mathrm{spa}}^{h}\Delta s^{\mathrm{spa}},\quad h\in\{\mathrm{pos},\mathrm{rot}\}.$$

> "Here $`\gamma=(\gamma_{\mathrm{sem}}^{\mathrm{pos}},\gamma_{\mathrm{spa}}^{\mathrm{pos}},\gamma_{\mathrm{sem}}^{\mathrm{rot}},\gamma_{\mathrm{spa}}^{\mathrm{rot}})`$ are scalar gates broadcast over tokens and channels. The gripper head shares the rotation-routed representation." (§3.3)
(한글 해설 — position·rotation 헤드별로 의미/공간 잔차를 차등 혼합하는 4개 scalar gate 이며, gripper 헤드는 rotation 라우팅 표현을 공유합니다.)

### Guided Metric Depth Repair

policy backbone 의 3D RoPE 는 모든 시각 토큰에 metric 3D 좌표를 요구하며, 이는 복원된 depth 로 back-projection 됩니다:

$$\hat{p}_{i}^{(v)}=T_{\mathrm{base}\leftarrow\mathrm{cam}}^{(v)}d_{\mathrm{out}}^{(v)}(u_{i})K^{(v)-1}\tilde{u}_{i}.$$

repair 모듈은 세 입력을 융합합니다 — (i) metric scale 을 보존하는 raw sensor depth $`d_{\mathrm{noisy}}^{(v)}`$, (ii) 경계 단서를 주는 RGB $`I^{(v)}`$, (iii) hole 을 cross-view 일관 기하로 메우는 Pi3X feed-forward depth prior:

$$\left(P_{\pi^{3}}^{(v)},d_{\pi^{3}}^{(v)}\right)=\mathcal{G}_{\pi^{3}}\!\left(\{I^{(u)}\}_{u\in\mathcal{V}}\right)^{(v)}.$$

> "Since $`d_{\pi^{3}}^{(v)}`$ may exhibit scale drift, it serves as geometric guidance rather than the final output." (§3.4)
(한글 해설 — feed-forward depth 는 scale drift 가 있어 최종 출력이 아니라 기하 guidance 로만 쓰입니다.)

3-branch U-Net 의 scale $`l`$ 에서 각 분기가 한 입력을 인코딩하고 fusion block 이 병합합니다:

$$F_{l}=\Phi_{l}\!\left(E_{l}^{d}(d_{\mathrm{noisy}}^{(v)}),E_{l}^{I}(I^{(v)}),E_{l}^{\pi}(d_{\pi^{3}}^{(v)}),F_{l+1}\right),$$

decoder 는 음이 아닌 복원 depth 를 산출합니다:

$$d_{\mathrm{out}}^{(v)}=\max\!\left(0,H_{\mathrm{depth}}(F_{0})\right).$$

> "The resulting depth retains the sensor's metric scale, recovers missing geometry from the feed-forward depth prior, and preserves object boundaries via RGB guidance." (§3.4)
(한글 해설 — metric scale 유지 + hole 복원 + 경계 보존을 동시에 달성한 depth 가 Eq.(14)의 point cloud 구성에 쓰입니다. 이 repair 망은 PerAct2 sim 데이터로 사전학습 후 정책 joint training 중에는 frozen 입니다.)

### 학습 목표 / 손실

policy backbone 은 scene/instruction/proprioception/noisy action trajectory 로 조건화된 3D denoising 정책입니다. position·rotation 은 element-wise mean L1, gripper 는 BCE 로 감독됩니다:

$$\mathcal{L}_{\mathrm{pos}}=\mathrm{mean}\left|\hat{\epsilon}_{\mathrm{pos}}-\epsilon^{\star}_{\mathrm{pos}}\right|,$$

$$\mathcal{L}_{\mathrm{rot}}=\mathrm{mean}\left|\hat{\epsilon}_{\mathrm{rot}}-\epsilon^{\star}_{\mathrm{rot}}\right|,$$

$$\mathcal{L}_{\mathrm{grip}}=\mathrm{BCEWithLogits}\!\left(\hat{g},g^{\star}\right).$$

> "Here $`\epsilon`$ denotes the flow/denoising target rather than the action itself." (§3.5)
(한글 해설 — $`\epsilon`$ 은 액션 자체가 아니라 flow/denoising 타깃입니다. position 은 workspace-normalized 3D 좌표, rotation 은 quaternion → 연속 6D 표현, gripper 는 binary open/close 로 표현됩니다.)

전체 목표:

$$\mathcal{L}=\lambda_{\mathrm{pos}}\mathcal{L}_{\mathrm{pos}}+\lambda_{\mathrm{rot}}\mathcal{L}_{\mathrm{rot}}+\mathcal{L}_{\mathrm{grip}}.$$

> "We set the loss weights to $`\lambda_{\mathrm{pos}}=30`$ and $`\lambda_{\mathrm{rot}}=10`$." (§3.5)
(한글 해설 — position 손실에 30, rotation 손실에 10 의 가중을 두어 위치 정밀도를 강하게 우선합니다.)

### 학습 셋업

- **데이터/카메라** — PerAct2($`V=3`$ 시점: front, wrist_left, wrist_right), 입력 해상도 $`256\times 256`$ RGB/depth, history $`H_{\mathrm{obs}}=3`$, temporal subsampling 5 (Table 5).
- **인코더** — RGB: frozen CLIP RN50 + FPN(res3 readout) → 시점별 $`32\times 32`$ 의미 토큰; 공간: frozen Pi3X pointmap/decoder feature → 시점별 $`18\times 18`$, $`d_{\mathrm{spa}}=1024`$. token embed dim $`d=120`$. 시각·언어 토큰은 offline 사전추출(Table 5).
- **상호작용** — cross-view semantic: 2 cross-attn layer·head 8, reprojection 매칭 radius 1·max reproj error 1.5 grid cell·max depth error 0.05 m·잔차 스케일 0.1; semantic-spatial: pointwise readout·head 8·잔차 스케일 0.1.
- **action head** — flow model: rectified flow, 5 denoising step; shared decoder 4 self-attn layer; position/rotation 헤드 각 2 self-attn layer + MLP($`d\to d\to 3/6`$); gripper MLP($`d\to d\to 1`$).
- **최적화** — AdamW(betas (0.9,0.95), weight decay $`1\times 10^{-10}`$), main lr $`1\times 10^{-4}`$ ·backbone lr $`1\times 10^{-6}`$ constant, batch 256/val 64, ablation 200k·full 400k step, 8×A100 ~20h (Table 5).
- **depth repair 학습** — PerAct2 sim 기반 데이터, train:test=90:10, AdamW lr $`8\times 10^{-4}`$, weight decay $`1\times 10^{-4}`$, 100 epoch, batch 8, pixel-wise L1 + missing-pixel weight $`1+4m`$ (Table 6). 사전학습 후 joint training 동안 frozen.

---

## 📊 실험 설정과 결과

평가는 (1) PerAct2 시뮬레이션(online 성공률 + offline action 예측 지표), (2) 실로봇 ARK-Lift(staged score), (3) 두 ablation(상호작용 모듈 / depth guidance)으로 구성됩니다. baseline 결과는 3DFA 논문에서 인용했습니다.

**PerAct2 메인 비교 (Table 1).** 대표 task 발췌(전체 13 task 평균):

| Method | Category | Avg. | lift_ball | push_buttons | pick_plate | straighten_rope | handover |
|---|---|---|---|---|---|---|---|
| 3DFA [10] | RGB-D explicit 3D | 85.1 | 99.7 | 92.7 | 74.0 | 40.7 | 89.0 |
| ACT [49] | RGB-only | 5.9 | 36.0 | 4.0 | 0.0 | 16.0 | 0.0 |
| $`\pi_{0}`$-keypose [3] | RGB-only | 43.7 | 97.0 | 38.0 | 27.0 | 7.0 | 2.0 |
| **Ours** | **RGB-D repaired depth** | **87.8** | **100.0** | **93.0** | **64.0** | **55.0** | **92.0** |

> "MV-Actor achieves an average success rate of 87.8%, substantially outperforming the RGB-only baselines ACT and $`\pi_{0}`$-keypose and exceeding the strongest RGB-D method, 3DFA (85.1%)." (§4.1.2, Table 1)
(한글 해설 — RGB-only baseline 을 큰 격차로, 최강 RGB-D baseline 3DFA 를 2.7%p 앞섭니다.)

> "On tasks demanding high spatial precision, such as pick_plate (+19.3% over 3DFA) and straighten_rope (+14.3%), Semantic-Spatial Token Interaction injects geometric awareness from feed-forward reconstruction features into semantic tokens" (§4.1.2)
(한글 해설 — 공간 정밀도가 중요한 task 에서 semantic-spatial 상호작용의 기여가 두드러집니다. 단, Table 1 의 pick_plate 행은 Ours 64.0 vs 3DFA 74.0 으로 본문 +19.3% 서술과 수치가 어긋나, 본문이 다른 baseline 기준일 가능성이 있어 수치는 표 그대로 인용합니다.)

> "On long-horizon tasks such as sweep_dust, lift_tray, handover_easy, take_tray_out_of_oven, and pick_up_laptop, MV-Actor slightly underperforms 3DFA because extended manipulation introduces large viewpoint variation that reduces multi-view overlap and degrades feed-forward reconstruction quality, weakening both Multi-view Semantic Interaction and spatial awareness." (§4.1.2)
(한글 해설 — long-horizon task 에서 시점 변화가 커 다중 시점 overlap 이 줄고 feed-forward 재구성 품질이 떨어지면 두 상호작용이 약해진다는, 방법의 핵심 전제 의존성을 저자가 직접 밝힌 부분입니다.)

**실로봇 ARK-Lift (Table 2, 3 task · task 당 10 trial · staged score %).**

| Method | Avg. | Lift Plate | Block Handover | Stick Insertion |
|---|---|---|---|---|
| PerAct2 [13] (voxel) | 16.6 | 9.9 | 20.0 | 19.8 |
| 3DFA [10] (point-cloud) | 58.1 | 43.0 | 75.0 | 56.2 |
| $`\pi_{0}`$ [3] (RGB-only VLA) | 52.5 | 43.0 | 55.0 | 59.4 |
| **MV-Actor (Ours)** | **63.1** | **49.7** | **80.0** | **59.6** |

> "MV-Actor obtains the highest average staged score of 63.1%, improving over 3DFA, $`\pi_{0}`$, and PerAct2 by 5.0, 10.6, and 46.5 percentage points, respectively." (§4.2.2, Table 2)
(한글 해설 — 3개 실로봇 양팔 task 평균에서 모든 baseline 우위. 반사 금속판이 있는 Lift Plate 와 그리퍼 가림이 잦은 Block Handover 에서 depth repair·다중 시점 일관성의 이득이 특히 큽니다. Stick Insertion 은 horizon 이 길고 overlap 이 제한적이라 3DFA· $`\pi_{0}`$ 와 비슷합니다.)

**상호작용 모듈 ablation (Table 3, offline 지표, 200k step 발췌).** 각 행이 격리하는 것:

| Configuration | Multi-view | Sem-spa | Gate | pos_l2 ↓ | pos_acc@0.01 ↑ | rot_l1 ↓ | rot_acc ↑ | gripper ↑ |
|---|:--:|:--:|:--:|---|---|---|---|---|
| Baseline | ✗ | ✗ | ✗ | 0.012 | 81.0 | 0.046 | 70.2 | 98.3 |
| + Multi-view | ✓ | ✗ | ✗ | 0.012 | 74.1 | **0.045** | 69.9 | 98.2 |
| + Sem-spa | ✗ | ✓ | ✗ | 0.012 | 82.6 | 0.050 | 71.0 | 97.9 |
| + Both (no router) | ✓ | ✓ | ✗ | 0.013 | 79.3 | 0.046 | 70.8 | 98.2 |
| **MV-Actor (full)** | ✓ | ✓ | ✓ | **0.009** | **86.3** | **0.045** | 70.6 | 98.3 |

> "Multi-view Semantic Interaction mainly improves rotation prediction. At 100k and 200k steps, $`\mathrm{rot\_l1}`$ drops to 0.053 and 0.045, the best at each step." (§4.3.1, Table 3)
(한글 해설 — Multi-view Semantic Interaction 은 주로 회전 예측을 개선합니다.)

> "Semantic-Spatial Token Interaction mainly improves position prediction. $`\mathrm{pos\_acc@0.01}`$ rises from 35.8%, 60.6%, 81.0% (baseline) to 42.2%, 70.0%, 82.6% at the three checkpoints" (§4.3.1, Table 3)
(한글 해설 — Semantic-Spatial 상호작용은 주로 위치 예측을 개선합니다. 즉 두 상호작용이 서로 다른 헤드를 돕습니다.)

> "The "+ Both (no router)" setting directly merges the semantic and spatial residual streams, which causes interference; semantic and spatial residuals therefore need to be selectively routed according to the prediction head." (§4.3.1)
(한글 해설 — 라우터 없이 두 잔차를 합치면 간섭이 생겨 baseline 대비 pos_acc 가 오히려 하락(79.3)합니다. Head-Aware Routing Gate 가 들어가야 비로소 pos_acc 86.3·pos_l2 0.009 로 전 지표 최고에 도달해, 두 상호작용이 "합산이 아니라 라우팅" 으로 결합돼야 함을 보입니다.)

**Depth repair guidance ablation (Table 4, MAE ↓).**

| Setting | RGB | FFD | MAE (all) | MAE (miss.) | MAE (obs.) |
|---|:--:|:--:|---|---|---|
| Sensor only | ✗ | ✗ | 0.150 | 1.146 | 0.010 |
| + RGB | ✓ | ✗ | 0.014 | 0.049 | 0.009 |
| + Pi3X | ✗ | Pi3X | 0.030 | 0.160 | 0.012 |
| + Both (Pi3X) | ✓ | Pi3X | **0.012** | 0.045 | **0.008** |
| + MoGe2 | ✗ | MoGe2 | 0.012 | 0.037 | 0.009 |
| + Both (MoGe2) | ✓ | MoGe2 | 0.014 | **0.035** | 0.010 |

> "RGB+Pi3X achieves the lowest all and obs error, giving the best overall metric point cloud quality, while RGB+MoGe2 achieves the lowest miss error for large-hole recovery." (§4.3.2, Table 4)
(한글 해설 — RGB(경계 단서) + FFD(전역 기하 prior)의 joint guidance 가 single guidance 를 모두 능가하며, FFD 소스(Pi3X/MoGe2)를 바꿔도 성립해 repair 설계가 특정 feed-forward 모델에 종속되지 않음을 시사합니다.)

---

## ⚖️ 한계

- **다중 시점 overlap 의존성 (저자 명시)** — long-horizon task 에서 시점 변화가 커 overlap 이 줄면 Multi-view Semantic Interaction 의 대응 집합이 비고 feed-forward 재구성 품질도 떨어져, 정확히 그런 task 에서 3DFA 에 밀립니다. 방법의 두 핵심 축이 모두 "충분한 시점 중첩" 이라는 단일 가정에 묶여 있어, 시점이 급변하는 실사용에서 가장 약한 고리입니다.
- **calibration 정밀도 의존성** — reprojection 매칭(Eq.4–6)과 metric back-projection 이 카메라 intrinsic·extrinsic(hand-eye calibration)에 의존합니다. calibration 오차가 $`\epsilon_{\mathrm{reproj}}=1.5`$ grid cell· $`\epsilon_{\mathrm{depth}}=0.05`$ m 임계를 넘으면 대응이 잘못 맺히거나 비어, 의미 공유 자체가 무효화됩니다.
- **frozen depth-repair 의 도메인 갭** — repair 망이 PerAct2 sim 데이터로 사전학습 후 frozen 됩니다. 실로봇에서는 성립했으나, 학습 분포 밖 센서·재질(새 반사 표면, 다른 depth 센서)에서 복원 품질이 보장되지 않으며, frozen 이라 joint training 중 자가 보정이 불가능합니다.
- **action 표현의 모호성 (추론된 갭)** — 본문 Eq.(3)은 horizon $`H`$ 의 action chunk 를 정의하지만 Table 5 는 "Single-step keypose-only action prediction" 이라 적어, 실제 운용이 keypose 단발 예측인지 chunk 예측인지 불명확합니다. keypose 기반이면 dense continuous control 로의 전이가 추가 검증을 요합니다.
- **계산 비용 미정량화** — frozen 이지만 Pi3X feed-forward 재구성·3-branch U-Net depth repair·이중 cross-attention 상호작용이 추론 경로에 추가됩니다. 실시간성(RTX 4090 추론은 언급되나 지연·throughput 수치 없음)이 정량화되지 않아 고주파 제어 적합성을 판단하기 어렵습니다.

---

## ♻️ 재현성

- **코드** — 공식 GitHub 저장소 [TianYinchen56/MV-Actor](https://github.com/TianYinchen56/MV-Actor) 공개(논문 본문 명시). 공개 범위(학습 스크립트/체크포인트)는 본문에서 상세히 밝히지 않습니다.
- **데이터/벤치마크** — 시뮬레이션은 공개 PerAct2 양팔 벤치마크. 실로봇은 자체 ARK-Lift 플랫폼(3× Intel RealSense D405, hand-eye calibrated, RTX 4090 추론)으로 task 당 100 demo·10 test trial — 외부 재현 난이도 높음.
- **하드웨어/학습** — 8×A100 GPU 약 20h(full 400k step). 핵심 하이퍼파라미터(Table 5)·depth repair 학습 설정(Table 6)·random seed 42 까지 상세 기재되어 시뮬레이션 측 재현성은 비교적 양호합니다.
- **외부 의존** — frozen CLIP RN50, Pi3X(Pi3 계열) feed-forward 재구성 모델, MoGe2(ablation)에 의존하며, 이들 가중치 접근성이 재현의 전제입니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P2(Structured Multimodal Observation Fusion) — 주 pillar.** MV-Actor 는 P2 의 정체성 그 자체입니다.
  - **D8(multi-camera spatial-geometric grounding)** — flat per-camera concat 도, 취약한 3D-KNN lifting 도 아닌, calibrated reprojection-consistent correspondence 로 시점 간 의미를 공유하는 제3의 grounding 방식을 제시합니다. P2 D8 v1(geometry-grounded multi-view encoder → unified 3D-consistent embedding)의 구체적 변형으로, "cross-view registration 유지" 라는 D8 원칙과 정확히 합치합니다.
  - **D9(action/dynamics-aware vision encoder)** — feed-forward 재구성 모델(Pi3X)을 frozen 공간 인코더로 사용해 정책에 공간 인지를 주입합니다. P2 D9 의 "eVGGT 같은 geometry-distilled encoder 선호" 노선의 실증 사례입니다.
  - **D10(heterogeneous modality fusion beyond concat)** — 의미·공간 토큰을 cross-attention/sigmoid-gated 잔차로 융합하고 Head-Aware Routing Gate 로 헤드별 차등 라우팅하는 것은 "flat concat 초월" 의 한 형태입니다.
- **P1(Heterogeneous Body/Hand Action Expert) — 인접.** position·rotation·gripper 헤드가 서로 다른 증거 혼합을 받도록 한 Head-Aware Routing Gate 는, "헤드/expert 마다 입력 정보 구성을 달리한다" 는 P1 D4(Body↔Hand 정보 공유)·D6(coordination) 발상과 구조적으로 닮았습니다. 단, 본 논문의 분할은 anatomical Body/Hand 가 아니라 양팔(left/right) + 예측 헤드(pos/rot/grip)이므로 직접 이식 대상이 아니라 설계 참고입니다.
- **P0(VLA Datasets & Benchmarks) — 약한 접점.** PerAct2 를 주 평가 벤치마크로 사용(D26 benchmark scouting 범위)하나 새 데이터셋/벤치마크 기여는 없습니다.
- **Identity 긴장/지지** — Identity 의 "structured multimodal observation fusion — multi-camera spatial-geometric grounding" 축을 강하게 지지합니다. 다만 우리 정체성의 핵심인 per-finger proprio-tactile binding 은 다루지 않고(양팔 macro 조작), action backbone 도 π 계열 flow-matching VLA 가 아니라 3D denoising keypose 정책이라, 관측 융합 아이디어는 지지하되 decoder/backbone 노선과는 결이 다릅니다.
- **경쟁자 함의** — P2 §5 핀 논문 VGGT/eVGGT 가 "geometry-grounding 인코더 자체" 라면, MV-Actor 는 그 family(Pi3)를 *소비* 해 양팔 정책에 통합한 응용 사례로, 우리가 D8/D9 를 정책에 꽂을 때의 통합 패턴 레퍼런스가 됩니다.

---

## ✨ 핀 논문 대비 델타

- **vs VGGT (P2 핀, arXiv:2503.11651)** — VGGT 는 다중 시점에서 camera/point/depth/track 을 산출하는 geometry-grounding *인코더* 입니다. MV-Actor 는 같은 feed-forward 재구성 family(Pi3)를 frozen 공간-토큰 공급원으로 *사용* 하되, 그 위에 (a) calibrated reprojection 기반 *의미* 공유(VGGT 에 없는 semantic interaction 축)와 (b) 소비자급 depth 의 Guided Metric Depth Repair 를 더합니다. 즉 "geometry grounding 을 어떻게 정책에 통합하는가" 의 델타입니다.
- **vs eVGGT / Geometry-Aware Vision Encoder (P2 핀, arXiv:2509.15880)** — eVGGT 가 manipulation 용으로 distill 된 빠른 기하 인코더라면, MV-Actor 는 인코더 효율이 아니라 *시점 간 의미 정합 + 헤드별 라우팅* 이라는 정책-측 융합 메커니즘이 새롭습니다.
- **공통 신규성** — 두 핀 모두 "단일 인코더의 표현 품질" 에 초점인 반면, MV-Actor 는 의미 잔차와 공간 잔차를 *분리* 한 뒤 position/rotation 헤드별로 *적응적 혼합* 한다는 점(Head-Aware Routing Gate)이 핀 논문군에 없는 차별점입니다.

---

## ⚙️ 의사결정 함의

이 논문이 맞다면 우리 P2 관측 융합 설계에서 다음이 바뀝니다.

- **다중 시점 융합 기본형 (D8)** — flat concat / naive 3D-KNN 대신 *reprojection-consistent correspondence* 를 기본 후보로 둡니다. 구체 손잡이: `epsilon_reproj=1.5` (token-grid cell), `epsilon_depth=0.05` m, `residual_scale(lambda_s)=0.1`, semantic interaction block 2회·`num_heads=8`, 의미 token grid `32×32`.
- **공간 인코더 선택 (D9)** — frozen feed-forward 재구성 모델(Pi3/Pi3X 또는 MoGe2)을 공간-토큰 공급원으로 채택 가능. 단일 `FFD_source` config 키로 교체 가능하다는 점(Table 4 의 Pi3X↔MoGe2 호환)이 설계 유연성을 줍니다. spatial token grid `18×18`, `d_spa=1024`.
- **잔차 결합 방식 (D10)** — 의미·공간 잔차를 단순 합산하지 말고 *헤드별 sigmoid gate* 로 라우팅합니다. config: position/rotation 별 `gamma_sem`/`gamma_spa` 4-gate, router 2-layer MLP(SiLU), 출력 bias init 0·weight std `1e-3`.
- **depth 전처리 (preprocessing)** — 소비자급 depth 를 정책에 넣기 전 RGB + FFD prior 로 복원하는 별도 frozen 모듈을 둡니다. loss: pixel-wise L1 + missing-pixel weight `1+4m`.
- **메트릭/loss 가중** — keypose/denoising 정책을 쓸 경우 `lambda_pos=30`, `lambda_rot=10` 이 위치 정밀도를 우선하는 출발점.

모호하지 않은 단일 결정: **"우리 멀티뷰 인코더의 D8 v1 을 reprojection-consistent semantic sharing 으로 인스턴스화하고, 공간 prior 는 Pi3 계열 frozen feed-forward 재구성으로 공급한다"** 를 검토 대상에 올립니다.

---

## ⚠️ 먼저 검증할 실패 모드

가장 싼 sanity check 부터:

1. **시점 중첩(overlap) 측정** — 가장 싼 검사. 우리 hand-centric 셋업(egocentric + wrist 카메라, 손가락·물체에 의한 심한 가림)은 본 논문이 *직접 약점으로 밝힌* "낮은 multi-view overlap" 조건에 해당할 공산이 큽니다. 우리 카메라 배치에서 calibrated reprojection 으로 실제 대응 집합 $`\mathcal{C}_{i}^{(v)}`$ 가 비지 않는지부터 로그로 확인해야 합니다(빈 대응 비율이 높으면 의미 공유 이득이 사라짐).
2. **calibration 정밀도** — hand-eye calibration 오차가 `epsilon_reproj`(1.5 grid cell)·`epsilon_depth`(0.05 m) 임계 안에 드는지 확인. 우리 in-hand 셋업처럼 카메라가 손/팔에 장착돼 움직이면 extrinsic 이 동적으로 변해 정합이 깨질 수 있습니다.
3. **feed-forward 재구성 적용성** — Pi3X 같은 모델은 충분한 baseline 을 가진 다중 시점 RGB 를 가정합니다. 손가락이 시야를 가리고 시점 간 baseline 이 작은 in-hand reorientation 에서 재구성 품질이 나오는지 소규모 검증 필요.
4. **backbone 정합** — 본 논문은 3D denoising/rectified-flow keypose 정책이지 우리의 π0/π0.5 flow-matching VLA backbone 이 아닙니다. semantic-spatial 토큰 융합을 π 백본의 observation 경로에 꽂을 때, 토큰 수·attention 비용·VLM prior 보존(P4)과 충돌하지 않는지 확인.
5. **depth repair 도메인 갭** — sim 사전학습·frozen repair 망이 우리 하드웨어(RealSense 외 센서, 새 재질)에서 일반화하는지. frozen 이라 현장 보정이 안 되므로, 우리 데이터로 재학습이 필요한지 판단해야 합니다.
6. **dexterity 적합성** — 이 방법의 이득은 양팔 macro 조작의 metric 위치 정밀도에서 나옵니다. 접촉-풍부 손가락 제어(tactile 중심)에서는 depth/3D grounding 의 한계효용이 작을 수 있어, 우리 차별화 과제(in-hand reorientation, tool articulation)로의 전이 가치를 별도 검증해야 합니다.

---

## 💡 컨텍스트 제안

- **P2 Tracked Literature 후보** — MV-Actor 는 P2 §5 의 VGGT/eVGGT(geometry-grounding 인코더) 핀을 *대체* 하지 않되, "feed-forward 재구성 spatial token 을 양팔 정책에 통합 + cross-view semantic interaction" 의 구체 패턴을 보여주는 **D8/D9 통합 사례** 로 비-핀(Methodology base) 추가를 제안합니다(핀 cap 8 유지). reprojection-consistent semantic sharing 은 현재 핀들에 없는 메커니즘입니다.
- **카탈로그** — 새 데이터셋/벤치마크 기여가 없어 `datasets.md`/`benchmarks.md` 라우팅 대상은 아닙니다. 하나의 정책 아키텍처로서 `models.md` VLA 등재 여부는 사람 판단에 맡깁니다(현재 메타에 `카탈로그` 행 미기입).
- **Decision 이동 없음** — 기존 D8 v1/D9 v1 노선을 *지지* 하는 증거이므로 결정 변경 트리거는 아닙니다. context 파일은 수정하지 않았습니다.
