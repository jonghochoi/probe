# Paper Analysis — LAMP: Latent Motion Prior-Guided Real-World Learning for Dexterous Hand Manipulation

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | LAMP: Latent Motion Prior-Guided Real-World Learning for Dexterous Hand Manipulation |
| 저자 | Xinye Yang, Zhiyuan Ma, Hongze Yu, Yuanpei Chen, Yaodong Yang, Xiaojie Chai, Xinlei Chen, Chao Yu (Fudan University · Tsinghua University · Peking University · PsiBot · Zhongguancun Academy) |
| 링크 | [arXiv:2607.06323](https://arxiv.org/abs/2607.06323) · [GitHub](https://github.com/dex-lamp/LAMP) · [Website](https://dex-lamp.github.io/) |
| 발행일 / 버전 | 2026-07-07 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-07-10 |
| 관련 Pillar | P1, P3 |
| 태그 | dexterity, vla-arch |

<!-- GitHub / Website URL 은 논문 본문 첫 페이지의 "Project Page" / "Code"
     링크에서 verbatim 추출 (fabrication 아님). 다만 이 실행 환경의 네트워크
     정책이 두 호스트로의 직접 접근을 차단해 (curl -L https://dex-lamp.github.io/
     → CONNECT tunnel failed, response 403; https://github.com/dex-lamp/LAMP →
     HTTP 403 via proxy) 실제 resolve 여부는 미확인입니다. -->

---

## 🧭 한 줄 요약 (TL;DR)

고차원 손 액션을 히스토리 조건부 2-D 연속 잠재 인터페이스(LMPM)로 감싸고, 모방 학습(IL)은 잠재 오프셋을, 실환경 잔차 강화학습(RL)은 잠재 잔차를 **같은 좌표계**에서 예측하게 하면 탐사가 시연된 접촉-일관 손 모션 근방의 국소 보정으로 제한되어, 4개 실로봇 다지 조작 과제에서 IL 평균 56.25% 를 온라인 RL 후 98.75% 까지 끌어올릴 수 있다는 주장입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 실환경 다지 손(dexterous hand) 학습의 취약성입니다. 고차원 hand action 은 모방 오차를 증폭시키고, RL 탐사는 접촉을 깨는 동작을 유발해 물리 하드웨어에서 위험하고 샘플 비효율적입니다.
- **기존 접근의 한계 (IL)** — end-to-end behavior cloning 은 대안적 복구 행동을 모델링하지 않아, 고-DoF 공간의 작은 실행 오차가 빠르게 누적되어 손이 out-of-distribution 구성으로 표류합니다.
- **기존 접근의 한계 (RL)** — raw hand-action 공간의 무제약 확률적 탐사는 물체를 기울이거나 떨어뜨리는 비가역 전이를 일으키고, 실물 손은 에피소드 중 복구가 사실상 불가능해 성공 궤적이 극도로 희소해집니다.
- **기존 압축 표현의 한계** — PCA 선형 부분공간은 굽은 hand-motion manifold 를 따라가지 못하고, VQ 계열 이산 코드북은 코드 전환 시 급격한 손 명령 점프를 만들어 접촉 집약적(contact-rich) 국면에서 접촉을 깹니다.
- **본 논문의 가설** — 연속적이고(decodable) 디코딩 가능하며 히스토리에 조건화된 잠재 hand-action 공간을 지도학습 정책과 온라인 잔차 탐사가 공유하면, 탐사가 시연된 접촉-일관 모션 근방의 국소 보정이 되어 실환경 학습이 안정화됩니다.
- **왜 지금 중요한가** — 유아의 "structured motor babbling"(신경근 prior 에 유도된 탐사) 관찰이 시사하듯 무구조 탐사가 아니라 prior-유도 탐사가 필요하며, RLPD·시각 보상 분류기 등 실환경 RL 인프라가 성숙한 지금 병목은 action-space 설계로 이동했습니다.

---

## 🧩 핵심 기여

- **LMPM (latent motion prior module)** — 최근 손 명령 히스토리를 압축 잠재 prior 로 인코딩하고 연속 잠재 명령을 실행 가능한 고차원 손 목표로 디코딩하는, 히스토리 조건부 연속 모션 prior 를 오프라인 궤적에서 학습합니다.
- **LAMP 3-stage 실환경 학습 프레임워크** — Stage 1 LMPM 사전학습 → Stage 2 native 팔 명령 + 잠재 손 오프셋을 예측하는 시각운동 BC → Stage 3 동일 잠재 공간에서의 잔차 RL, 로 IL 과 residual RL 을 하나의 디코딩 가능한 인터페이스로 통합합니다.
- **실로봇 4과제 검증** — Raw / PCA / VQ-VAE(DQ-RISE) 인터페이스와 동일 파이프라인 비교에서 최고 성능: IL 평균 56.25% → 온라인 RL 후 98.75% (3개 과제 100%, 나머지 1개 95%).
- **Action-interface 진단 지표** — off-manifold 탐사 비율( $`\Delta\mathrm{NN}/\mathrm{Disp}`$ )과 2차 차분 jitter 지표로 "왜 연속·히스토리 조건부 인터페이스가 RL 에 유리한가"를 정량 분석합니다.

---

## 🔑 기술 키워드

- **LMPM (Latent Motion Prior Module)** — 최근 손 명령 히스토리를 2-D Gaussian prior 로 인코딩하고 잠재 벡터를 6-D 손 목표로 복원하는 VAE 형 모듈 — 손 동작의 "관절 언어"를 압축 좌표계로 번역해 주는 통역기에 해당합니다.
- **Latent action space** — 잠재 공간(latent space) 위에 정의된 행동 공간 — 정책이 관절을 직접 지정하는 대신 압축 좌표를 조작하고, 디코더가 이를 실행 가능한 관절 목표로 되돌립니다.
- **History-conditioned prior** — 최근 K=8 스텝 손 명령이 결정하는 국소 prior 중심 $`\mu_t`$ — 현재 모션 국면(phase)에서 "나올 법한 다음 손 동작"의 기본값을 정책에 공급합니다.
- **Residual RL** — 동결된 BC 정책 출력 위에 작은 보정만 학습하는 강화학습 (RL) — 기존 실력 위에 첨삭만 하는 과외에 비유할 수 있습니다.
- **RLPD** — 시연 버퍼와 온라인 버퍼를 반반 섞어 배치를 구성하는 SAC 계열 off-policy 실환경 RL 레시피입니다.
- **Behavior cloning** — 모방 학습 (IL)의 지도학습 형태 — 시연된 행동을 회귀로 복제합니다.
- **VQ-VAE (DQ-RISE)** — 이산 코드북으로 hand action 을 표현하는 비교군 — 코드 전환 시 손 명령 점프가 생겨 접촉이 깨질 수 있음이 본 논문의 반례 축입니다.
- **Off-manifold ratio** — 동일 변위 예산의 탐사 스텝 중 시연 manifold 를 벗어나는 비율 $`\Delta\mathrm{NN}/\mathrm{Disp}`$ — 낮을수록 접촉-보존 탐사입니다.
- **Hand synergy** — 인간의 다관절 손 자세가 소수의 주성분으로 설명된다는 고전 관찰 — 손 액션 압축이 정당한 이유를 제공하는 생물학적 근거입니다.

---

## 🔬 방법론

### 직관

다지 손 학습이 어려운 근본 원인은 손가락 관절이 많다는 사실 그 자체입니다. 관절이 많을수록 모방 학습의 회귀 목표가 커져 작은 예측 오차가 누적되고, RL 탐사 노이즈는 각 관절에 독립적으로 실려 애써 만든 접촉을 순식간에 깨뜨립니다. LAMP 의 출발점은 시연 데이터가 이미 손 동작의 "좁은 길"(저차원 manifold)을 보여주고 있다는 관찰입니다. 그렇다면 그 길 위의 좌표계를 먼저 배우고, 이후의 모든 학습 — 모방이든 RL 이든 — 을 그 좌표계 안에서만 수행하자는 것입니다.

프레임워크는 세 단계입니다. 먼저 시연의 손 명령 시퀀스만으로 인코더-디코더 쌍(LMPM)을 학습합니다. 인코더는 최근 8스텝 손 명령을 보고 "지금 이 국면에서 나올 법한 다음 손 동작"의 분포(prior)를 출력하고, 디코더는 잠재 좌표를 실행 가능한 손 목표로 복원합니다. 다음으로 시각운동 정책을 학습하되, 팔 명령은 원 좌표 그대로, 손은 prior 중심에서의 작은 오프셋만 예측하게 합니다. 마지막으로 실환경 RL 이 같은 잠재 좌표에 잔차를 더합니다. 그 결과 탐사는 "각 손가락을 제멋대로 흔드는" 것이 아니라 "시연된 손 모양 근방을 미세 조정"하는 형태가 됩니다.

핵심 비대칭은 팔을 잠재화하지 않는다는 점입니다. 팔은 접근 방향·물체 위치·배치 기하 같은 과제 수준의 변화를 표현해야 하므로 native 좌표를 유지하고, 압축이 이득이 되는 것은 시연 manifold 가 좁은 손 쪽뿐이라는 설계 판단입니다. 보상은 사람이 설계한 reward 항이 아니라 과제별 시각 성공 분류기의 sparse 신호만 사용해, 보상 엔지니어링을 성공 상태 라벨링으로 대체합니다.

### 아키텍처

> "This motivates a continuous, decodable, history-conditioned latent action space shared by supervised policy learning and online residual exploration." (§1)

(설계 의도를 한 문장으로 못 박는 앵커입니다 — 인터페이스가 갖춰야 할 세 성질: 연속성(잔차 갱신의 국소 부드러움), 디코딩 가능성(실행 가능한 손 목표로의 복원), 히스토리 조건화(접촉-일관 모션 근방 유지)를 지도학습과 온라인 탐사가 **공유**해야 한다는 것이 LAMP 의 전부입니다.)

![Figure 2 — LAMP 3-stage 파이프라인 개요](https://arxiv.org/html/2607.06323/x2.png)

> "Figure 2: Overview of LAMP. The framework first learns LMPM from demonstrated hand motion and then uses the frozen prior interface in both behavior cloning and real-world residual RL." (§3)

(한글 해설 — 시연 손 모션으로 LMPM 을 먼저 학습하고, 동결된 prior 인터페이스를 BC 와 실환경 잔차 RL 이 공유하는 3단계 구조를 시각화합니다.)

- **LMPM 인코더 $`E_{\phi}`$** — 8스텝 hand-target 히스토리(스텝당 6-D)를 받아 2-D Gaussian prior 의 $`(\mu_{t},\sigma_{t})`$ 를 출력합니다. hidden width 256 의 MLP 입니다.
- **LMPM 디코더 $`D_{\theta}`$** — 2-D 잠재 벡터를 다음 6-D 절대 hand target 으로 복원합니다. Stage 1 이후 인코더와 함께 동결됩니다.
- **BC 정책 $`\pi_{\psi}^{\mathrm{BC}}`$** — 뷰별 frozen ImageNet-pretrained ResNet-18 로 front/wrist RGB 를 인코딩하고, 12-D robot state·hand-history 특징과 concat 하여 `CoreActionHead` MLP(hidden `[512, 512, 256]`)로 6-D 팔 명령 + 2-D 잠재 오프셋을 예측합니다.
- **잔차 actor $`\pi_{\eta}`$ / critic $`Q_{\omega}`$** — `[256, 256]` MLP(tanh 활성화 + layer normalization), actor 는 tanh-squashed Gaussian 으로 8-D 잔차(팔 6 + 잠재 2)를 출력합니다. critic 은 실행된 12-D 환경 action 위에서 학습됩니다(ensemble 2).
- **시각 보상 분류기** — 뷰별 frozen SERL ResNet-10 + spatial learned embeddings(8 blocks, 256-D bottleneck) → 단일 성공 logit. proprioception 은 쓰지 않습니다.

### 학습 목표 / 손실

**Stage 1 — LMPM 사전학습.** 시연 궤적의 손 모션 성분만으로 학습합니다. $`h_{t+1}`$ 을 다음 제어 스텝의 목표 손 명령이라 할 때, 최근 hand-target 히스토리는 식 (1)로 정의됩니다:

$$H_{t}=(h_{t-K+1},\ldots,h_{t})$$

인코더는 $`H_{t}`$ 를 국소 잠재 prior 로, 디코더는 잠재 벡터를 실행 가능한 손 목표로 매핑합니다 (식 2):

$$q_{\phi}(z_{t}|H_{t})=\mathcal{N}\!\left(\mu_{\phi}(H_{t}),\mathrm{diag}(\sigma_{\phi}^{2}(H_{t}))\right),\qquad\hat{h}_{t+1}=D_{\theta}(z_{t}),\quad z_{t}\sim q_{\phi}(\cdot|H_{t})$$

학습 목표는 재구성 + KL 정규화 병목입니다 (식 3):

$$\mathcal{L}_{\mathrm{prior}}=\mathbb{E}_{(H_{t},h_{t+1})}\!\left[\|D_{\theta}(z_{t})-h_{t+1}\|_{2}^{2}+\beta D_{\mathrm{KL}}\!\left(q_{\phi}(z_{t}|H_{t})\,\|\,\mathcal{N}(0,I)\right)\right]$$

> "The reconstruction term preserves executability in the original hand-command space, while the KL term encourages a compact and smooth latent coordinate system." (§3.1)

(두 항의 역할 분담이 명확합니다 — 재구성 항이 없으면 잠재 명령이 실행 불가능한 손 목표로 디코딩되고, KL 항이 없으면 잠재 좌표계가 매끄럽지 않아 잔차 탐사의 국소성이 무너집니다.)

> "Two histories can share the same latent coordinates yet decode around different hand-motion phases through different encoder statistics." (§3.1)

(히스토리 조건화의 요점입니다 — 같은 잠재 좌표라도 인코더 통계( $`\mu_{t},\sigma_{t}`$ )가 다르면 다른 모션 국면 주변으로 디코딩됩니다. 즉 잠재 공간은 "전역 손 모양 사전"이 아니라 "현재 국면 기준의 상대 좌표계"로 동작합니다.)

**Stage 2 — 잠재 공간 모방 학습.** 시연 $`\mathcal{D}_{\mathrm{demo}}=\{(o_{t},a_{t}^{\mathrm{arm}},h_{t+1},H_{t})\}`$ 에서 초기 시각운동 정책을 학습합니다. 관측 $`o_{t}`$ 는 RGB 이미지와 팔 proprioceptive 상태 $`x_{t}^{\mathrm{arm}}`$ 을 담고, 손 모션은 동결된 prior 가 쓰는 히스토리 $`H_{t}`$ 로 별도 유입됩니다. 실행 action 은 식 (4)입니다:

$$a_{t}=(a_{t}^{\mathrm{arm}},a_{t}^{\mathrm{hand}}),\qquad a_{t}^{\mathrm{hand}}=h_{t+1}$$

$`h_{t+1}`$ 을 직접 회귀하는 대신, 동결 인코더가 $`(\mu_{t},\sigma_{t})=E_{\phi}(H_{t})`$ 를 계산하고 정책은 관측과 prior 통계를 받아 팔 명령과 잠재 오프셋을 예측합니다 (식 5):

$$(\hat{a}_{t}^{\mathrm{arm}},\Delta\hat{z}_{t})=\pi_{\psi}^{\mathrm{BC}}(o_{t},\mu_{t},\sigma_{t}),\qquad\hat{h}_{t+1}=D_{\theta}(\mu_{t}+\Delta\hat{z}_{t})$$

지도 목표는 시연된 팔 명령과 디코딩된 손 목표를 일치시키고 오프셋 크기를 억제합니다 (식 6):

$$\mathcal{L}_{\mathrm{BC}}=\|\hat{a}_{t}^{\mathrm{arm}}-a_{t}^{\mathrm{arm}}\|_{2}^{2}+\lambda_{h}\|\hat{h}_{t+1}-h_{t+1}\|_{2}^{2}+\lambda_{z}\|\Delta\hat{z}_{t}\|_{2}^{2}$$

> "The latent offset lets the policy adapt the hand-motion prior to the current visual observation while keeping decoded commands on the learned hand-motion interface." (§3.2)

(prior 중심 $`\mu_{t}`$ 는 "히스토리만 보고 예측한 다음 손 동작"이고, 시각 정보가 필요한 부분 — 물체가 어디 있고 어떤 국면인지 — 만 오프셋 $`\Delta\hat{z}_{t}`$ 로 보정합니다. 정책의 회귀 부담이 6-D 관절 목표에서 2-D 보정량으로 줄어드는 것이 IL 이득의 원천입니다.)

> "The arm head remains in the native arm coordinate because the arm must express task-level variation such as approach direction, object pose, and placement geometry." (§3.2)

(팔을 잠재화하지 않는 이유입니다 — 팔의 변화는 과제 수준(물체 위치·접근 방향)이라 시연 manifold 로 압축하면 오히려 표현력이 부족해집니다. 압축은 손에만 이득이라는 비대칭 설계 판단입니다.)

**Stage 3 — 잠재 공간 잔차 RL.** BC 정책을 동결하고, 잔차 actor 가 $`s_{t}=(o_{t},H_{t})`$ 를 관측해 raw 손 관절 공간이 아닌 $`\mathcal{A}_{\mathrm{arm}}\times\mathcal{Z}`$ 에서 잔차 $`u_{t}=(\rho_{t}^{\mathrm{arm}},\rho_{t}^{z})`$ 를 출력합니다. 상호작용 시 (식 7, 8):

$$(a_{t,\mathrm{bc}}^{\mathrm{arm}},\Delta z_{t,\mathrm{bc}})=\pi_{\psi}^{\mathrm{BC}}(o_{t},\mu_{t},\sigma_{t}),\quad z_{t,\mathrm{bc}}=\mu_{t}+\Delta z_{t,\mathrm{bc}},\quad u_{t}\sim\pi_{\eta}(\cdot|s_{t})$$

$$\tilde{a}_{t}=\left(a_{t,\mathrm{bc}}^{\mathrm{arm}}+s_{\mathrm{arm}}\rho_{t}^{\mathrm{arm}},\,D_{\theta}(z_{t,\mathrm{bc}}+s_{z}\rho_{t}^{z})\right)$$

> "Applying the hand residual in $`\mathcal{Z}`$ expresses exploration as local corrections to a history-conditioned hand command rather than independent perturbations of every finger joint." (§3.3)

(잔차 RL 을 잠재 공간에서 수행하는 이유의 앵커입니다 — 동일한 탐사 노이즈라도 raw 공간에서는 손가락별 독립 섭동이지만, $`\mathcal{Z}`$ 에서는 디코더를 통과하며 "시연된 손 모양의 이웃"으로 구부러집니다.)

새 전이는 온라인 버퍼 $`\mathcal{D}_{\mathrm{online}}`$ 에 쌓여 시연 데이터와 혼합되고, RLPD 방식의 SAC 손실로 잔차 actor/critic 을 갱신합니다 (식 9, 10; 배치 $`\mathcal{B}\subset\mathcal{D}_{\mathrm{demo}}\cup\mathcal{D}_{\mathrm{online}}`$ ):

$$\mathcal{L}_{Q}=\mathbb{E}_{\mathcal{B}}\!\left[(Q_{\omega}(s_{t},u_{t})-y_{t})^{2}\right],\quad y_{t}=r_{t}+\gamma\,\mathbb{E}_{u^{\prime}\sim\pi_{\eta}}\!\left[\bar{Q}(s_{t+1},u^{\prime})-\alpha\log\pi_{\eta}(u^{\prime}|s_{t+1})\right]$$

$$\mathcal{L}_{\pi}=\mathbb{E}_{s_{t}\sim\mathcal{B},\,u_{t}\sim\pi_{\eta}}\!\left[\alpha\log\pi_{\eta}(u_{t}|s_{t})-Q_{\omega}(s_{t},u_{t})\right]$$

**시각 보상 분류기 (sparse reward).** 과제별 이진 분류기를 학습해 온라인 보상과 평가 성공 라벨을 모두 생성합니다. $`p_{\mathrm{cls}}(o)=\sigma(f_{\mathrm{cls}}(o))`$ 에 대해 (식 C.1):

$$\mathcal{L}_{\mathrm{cls}}=-\mathbb{E}_{(o,y)}\left[y\log p_{\mathrm{cls}}(o)+(1-y)\log(1-p_{\mathrm{cls}}(o))\right]$$

온라인 상호작용 중 보상은 임계값 0.90 의 지시 함수입니다 (식 C.2):

$$r_{t}=\mathbb{1}\left[p_{\mathrm{cls}}(o_{t+1})>0.90\right]$$

$`r_{t}=1`$ 이면 에피소드를 종료하고 성공 플래그를 세웁니다. 양성 라벨은 수집 중 조작자가 성공 상태를 마킹하고, 같은 세션의 마킹되지 않은 방문 상태가 음성 예시가 됩니다.

### 학습 셋업

- **하드웨어 / 텔레오퍼레이션** — Franka Research 3 팔 + Ruiyan 다지 손(6-DoF) + front-view RealSense D435 + wrist-mounted RealSense D405. 시연은 human-in-the-loop 텔레옵으로 수집합니다: Synglove 가 손가락 모션을, SpaceMouse 가 TCP 병진·회전을 명령합니다. 시연은 hand 명령을 절대 목표로 저장하고, 실행 시 환경 래퍼가 디코딩된 절대 목표를 하드웨어의 저수준 delta 로 변환합니다.
- **관측 / 액션** — 매 제어 스텝에 front/wrist RGB + 12-D robot state + 최근 8개 hand target. 로봇 action 은 6-D 팔 명령 ⊕ 6-D Ruiyan 손 명령 = 12-D. BC 는 one-step 목표 예측(현재 관측 → 다음 12-D action)이며, 궤적 시작부의 누락 히스토리는 첫 기록 target 으로 padding 합니다.
- **데이터** — 과제별 소규모 시연: Grasp & Place 50개, Open Drawer 20개, Pull Tissue 20개, Assemble Box 30개. 9:1 분할로 LMPM/BC 학습과 검증에 사용하며 모든 인터페이스 변형이 같은 분할을 공유합니다.
- **LMPM 사전학습 (Table B.1)** — MLP encoder/decoder width 256, $`d_{z}=2`$ , AdamW, batch 256, LR $`2\times 10^{-3}`$ , 20k steps, warmup(LR 500 / KL 2000 steps), KL 가중치 $`10^{-3}`$ , hand-history 노이즈 std 0.01, gradient clip 1.0.
- **BC (Table B.1)** — 뷰별 frozen ResNet-18, head `[512, 512, 256]`, AdamW, batch 128, LR $`5\times 10^{-4}`$ , 20k steps, arm-state·hand-history 노이즈 std 0.10, gradient clip 1.0.
- **잔차 RLPD (Table B.2)** — actor/critic `[256, 256]` (tanh, layer norm), critic ensemble 2, discount 0.97, batch 256 = 온라인 128 + 시연 128, critic-to-actor ratio 2(critic-only 1회 + critic·actor·temperature 1회), replay 200k, 온라인 100 전이 후 학습 시작, network publish 간격 50 learner steps, 초기 temperature $`10^{-2}`$ . 과제별 온라인 예산: Grasp & Place 20k / Open Drawer 30k / Pull Tissue 40k / Assemble Box 25k steps.
- **보상 분류기 (Table C.1)** — 뷰별 frozen SERL ResNet-10, spatial learned embeddings(8 blocks, 256-D), head Dense 256 + dropout 0.1 + layer norm + ReLU + Dense 1, batch 256(양성 128 + 음성 128), Adam LR $`10^{-4}`$ , 250 epochs, 배포 규칙 $`p_{\mathrm{cls}}(o)>0.90`$ .

---

## 📊 실험 설정과 결과

> "Our setup uses a Franka Research 3 arm with a Ruiyan dexterous hand and two RGB cameras: a front-view RealSense D435 and a wrist-mounted RealSense D405." (§4.1)

(실험 플랫폼입니다. 온라인 RL 과 평가 시 TCP 시작 pose 를 명목 pose 주변에서 랜덤화해 공간 일반화를 시험합니다. 4개 과제는 모두 지속적 손-물체 접촉을 요구합니다 — Grasp & Place(좁고 높은 상자에 병을 세워 배치), Open Drawer(작은 서랍 손잡이 파지), Pull Tissue(형상이 변하는 유연체), Assemble Box(초기 접촉 오차가 실패로 이어지는 장기 삽입).)

동일 파이프라인에서 hand-action 인터페이스만 바꿔 4가지를 비교합니다 (Appendix B.4):

| Interface | Policy hand output | 6-D hand target 변환 |
|---|---|---|
| Raw | 6-D hand target | identity |
| PCA | 2-D PCA coordinate | 시연 hand target 에 적합한 inverse PCA transform |
| VQ-VAE (DQ-RISE) | 16-way residual-VQ code | two residual quantizers with four codes each |
| LAMP (Ours) | 2-D latent offset $`\Delta z_{t}`$ | frozen LMPM decoder $`D_{\theta}(\mu_{t}+\Delta z_{t})`$ |

![Figure 4 — 4개 실환경 과제 평가(성공/실패 유형 분해)](https://arxiv.org/html/2607.06323/x4.png)

> "Figure 4: Real-world evaluation on four dexterous tasks. Each bar reports success counts and failures categorized as arm-action error, dexterous-hand error, or stalled execution." (§4.2)

(한글 해설 — 인터페이스별 성공 수와 실패 원인(팔 오류 / 손 오류 / 정지)을 분해해, LAMP 의 이득이 어느 실패 유형을 줄여서 오는지 보여줍니다.)

**IL 성능 (§4.2.1).** Raw 는 고차원 회귀 목표 탓에 손이 눈에 띄게 떨리며 접촉 형성·유지에 실패합니다. PCA 는 2차원 선형 압축만으로 4개 과제 전부에서 Raw 를 크게 앞서 "압축 표현 자체가 다지 정책 학습을 쉽게 만든다"는 것을 보여줍니다. VQ-VAE 는 근접 action 사이를 빈번히 전환하며 jitter 가 생겨 강체 파지에서 물체가 미끄러질 수 있습니다.

> "The remaining gap from PCA to LAMP suggests that compression alone is not sufficient: PCA provides fixed linear hand coordinates, whereas the pretrained history-conditioned encoder in LMPM predicts a latent prior center from recent hand motion, making hand-action continuity directly available to the visuomotor policy." (§4.2.1)

(압축(차원 축소)과 LMPM 의 차이를 분리하는 핵심 문장입니다 — PCA 도 2-D 지만 좌표가 고정 선형인 반면, LMPM 은 최근 모션이 정하는 국소 prior 중심을 제공해 "손 동작의 연속성"이 정책 입력으로 직접 들어옵니다.)

**RL 성능 (§4.2.2).**

> "Real-world residual RL is most sample-efficient when exploration remains local to the imitation policy: residuals must improve the behavior without repeatedly breaking contact, so the replay buffer can keep receiving successful or near-successful rollouts." (§4.2.2)

(실환경 RL 의 성립 조건을 요약합니다 — 탐사가 접촉을 반복적으로 깨면 성공 궤적이 replay buffer 에 들어오지 못해 sparse reward 학습이 무너집니다.)

> "By contrast, LAMP uses a continuous decoder and a history-conditioned prior to organize demonstrated hand motions into a better-conditioned latent space, giving residual RL a smoother, more contact-preserving neighborhood for reward-guided refinement." (§4.2.2)

(Raw 는 낮은 IL 초기 성공률에서 출발해 수렴이 어렵고, PCA 는 고정 선형 사영이라 잔차가 여전히 접촉을 깨는 손 모션으로 디코딩되며, VQ-VAE 는 RL 로 개선되지만 코드북 전환의 gesture 점프가 최종 성공률을 제한합니다. LAMP 는 연속 디코더 + 히스토리 조건부 prior 로 잔차 RL 에 "접촉-보존 이웃"을 제공한다는 주장입니다.)

> "Starting from small task-specific demonstration sets, LAMP achieves a 56.25% average IL success rate and raises it to 98.75% after online RL, reaching 100% final success on three tasks and 95% on the remaining task." (§Abstract)

(헤드라인 수치입니다 — 과제당 20–50개 시연에서 출발해 온라인 RL 이 평균 +42.5%p 를 더합니다.)

**Ablation (§4.3, Table 1).** 20 에피소드 평가 기준 과제별 IL / RL 성공률:

| Variant | Grasp & Place (IL / RL) | Open Drawer (IL / RL) | Pull Tissue (IL / RL) | Assemble Box (IL / RL) |
|---|---|---|---|---|
| Full LMPM | 75% / 100% | 50% / 100% | 45% / 95% | 55% / 100% |
| w/o low-dimensional bottleneck | 40% / 35% | 65% / 85% | 15% / 80% | 5% / 20% |
| w/o history-conditioned encoder | 70% / 95% | 35% / 90% | 40% / 60% | 15% / 50% |
| Raw BC (no LMPM) | 0% / 15% | 20% / 0% | 0% / 0% | 0% / 0% |

> "Expanding the latent dimension usually lowers final performance, suggesting that a larger hand space still burdens arm-hand coordination and online exploration." (§4.3)

(각 ablation 이 분리하는 것 — **w/o bottleneck** 은 2-D 병목을 제거한 변형으로, IL·RL 모두 크게 하락합니다(특히 Assemble Box 5%/20%). 압축이 손가락만이 아니라 팔-손 협응 전체의 학습 문제를 줄인다는 신호입니다. **w/o history encoder** 는 국소 prior 중심 없이 잠재 점을 직접 예측하는 변형으로, IL 초기화가 약해지지만 잔차가 여전히 디코더를 거쳐 manifold 에 묶이므로 raw 보다는 안정적입니다 — 짧은 과제(Grasp & Place, Open Drawer)에서는 RL 이 회복하지만 긴 과제(Pull Tissue 60%, Assemble Box 50%)에서는 격차가 남습니다. **Raw BC** 는 전 과제에서 사실상 학습에 실패합니다.)

> "The low-dimensional bottleneck helps arm-hand coordination rather than only improving the fingers in isolation." (§E)

(Appendix E.2 의 실패 유형 분해가 뒷받침합니다 — bottleneck 제거 시 RL 후에도 팔-action 실패가 다수 남는 반면(Pull Tissue·Assemble Box 에서 가장 뚜렷), full LMPM 은 4개 과제 통틀어 팔 실패가 1건입니다. 정책이 팔·손을 결합 예측하므로 손 표현이 커지면 팔 분기의 학습 문제까지 어려워진다는 해석입니다.)

**잠재 action-flow 시각화 (§4.4).**

![Figure 6 — 3단계 잠재 action 흐름 시각화](https://arxiv.org/html/2607.06323/x6.png)

> "Figure 6: Latent action-flow visualization for the four tasks. Gray trajectories show the LMPM encoder output, teal trajectories show the latent action after adding the IL-predicted latent offset, and red dashed trajectories show the final latent action after applying the RL latent residual. Hand icons show decoded hand gestures at representative latent locations, and markers with the same color indicate the same sampled timestep." (§4.4)

(한글 해설 — prior 가 실행 가능 manifold 를 유지하고, IL 오프셋이 시각 기반 주 변위를 공급하며, RL 잔차는 같은 좌표계에서 국소 조정만 더한다는 3단 분업을 실측 rollout 로 보여줍니다. IL 격차가 큰 과제(Grasp & Place, Pull Tissue)에서는 잔차가 action 을 인접 성공 영역으로 이동시키고, IL 이 이미 근접한 과제(Open Drawer, Assemble Box)에서는 잔차가 작게 유지됩니다.)

**Off-manifold 탐사 분석 (Appendix A).**

> "The ratio $`\Delta\mathrm{NN}/\mathrm{Disp}`$ measures the fraction of the step that points away from the data-supported motion manifold." (§A)

(디코딩된 hand-action 변위 예산 $`\mathrm{Disp}`$ 를 맞춘 상태에서 시연 hand action 까지의 최근접 이웃 거리 증가량 $`\Delta\mathrm{NN}`$ 을 재는 정규화 지표로, 탐사 스텝의 크기와 방향을 분리합니다. 0 근처면 시연 모션을 따라 움직이고 1 근처면 거의 전부 manifold 밖입니다.)

![Figure A.1 — 동일 변위 예산에서의 off-manifold 탐사 비율](https://arxiv.org/html/2607.06323/x7.png)

> "Figure A.1: Fraction of exploration that leaves the manifold at a matched displacement budget ( $`\mathrm{Disp}=0.2`$ ). Bars show $`\Delta\mathrm{NN}/\mathrm{Disp}`$ ; $`1.0`$ (dashed) is fully off-manifold. LAMP keeps the smallest off-manifold fraction on most tasks. VQ-VAE is omitted here because its discrete action space cannot realise a controllable displacement budget; its behaviour is shown in the off-manifold panel instead." (§A)

(한글 해설 — Raw 는 일관되게 manifold 에서 멀고, PCA 는 고정 선형 좌표가 굽은 hand-motion 구조를 못 따라가 상당히 off-manifold 로 남으며, LAMP 가 대부분 과제에서 최저 비율을 유지한다는 §4.2.2 주장의 정량 근거입니다.)

**Action 부드러움 분석 (Appendix F).** 2차 차분 hand-target 변동으로 고주파 jitter 를 의도적 손 개폐와 분리해 측정합니다 (식 F.1):

$$J=\frac{1}{T-2}\sum_{t=1}^{T-2}\|a_{t+2}^{\mathrm{hand}}-2a_{t+1}^{\mathrm{hand}}+a_{t}^{\mathrm{hand}}\|_{2}$$

Raw·VQ-VAE 정책은 고-jitter 구간이 빈번한 반면 LAMP 는 대부분의 rollout 을 저-jitter 범위로 유지합니다(과제별 Raw-IL 점수로 정규화한 집계 기준).

---

## ⚖️ 한계

- **(저자 명시) 과제 특화 prior** — LMPM 이 과제별 오프라인 손 모션 데이터로 학습되어, 새 과제 배치마다 적합한 손 모션 궤적 수집과 prior 재학습이 필요합니다. 잠재 인터페이스가 과제의 접촉 패턴에 잘 맞는 것과 재사용성이 없는 것은 동전의 양면이라, "범용 인터페이스"가 아니라 "과제별 압축기"에 가깝습니다.
  > "This makes the latent interface well matched to each task’s contact patterns, but deploying LAMP to a new task still requires suitable hand-motion trajectories and prior pretraining." (§5)
- **(저자 명시) 6-DoF 손 · 2-D 잠재의 검증 범위** — 검증이 저-DoF 손과 극단적 압축(6→2)에 한정됩니다. 저자는 15-DoF Cyberglove 연구에서 첫 4개 주성분이 자세 변동의 95% 이상을 설명한다는 문헌을 들어 고-DoF 확장 가능성을 시사하지만, 이는 미검증 외삽입니다.
  > "We validate the latent-prior idea on a 6-DoF hand and map the raw hand space to a 2-D latent space." (§5)
- **(추론) BC 백본의 단순성** — 시각 정책이 frozen ResNet-18 + MLP 의 one-step 회귀입니다. diffusion policy·ACT 등 강한 IL 아키텍처(다봉 분포·action chunking 처리)와의 비교가 없어, "잠재 인터페이스의 이득"이 강한 IL 백본에서도 유지되는지 알 수 없습니다. Raw 의 0% IL 붕괴 폭은 약한 백본에서 과장되었을 수 있습니다.
- **(추론) VQ-VAE 비교의 이식 공정성** — DQ-RISE 의 원 시스템(3D 인코더 + diffusion 기반 arm-hand 결합 예측)이 아니라 그 이산 hand-action 인터페이스만 자기 파이프라인에 이식해 비교합니다. 이산 표현 자체의 한계와 이식 손실이 분리되지 않습니다.
- **(추론) 평가 규모와 통계** — 과제당 20 에피소드, 단일 로봇·단일 랩, 분산/신뢰구간 미보고입니다. 95–100% 급 수치의 차이는 1–2 에피소드 차이에 해당합니다.
- **(추론) 동결 디코더의 표현력 상한** — 잔차가 디코더를 통과하므로 도달 가능한 손 모션이 시연 manifold 근방으로 제한됩니다. 이것이 탐사 안전성의 원천이지만, 동시에 시연에 없는 새로운 접촉 패턴(복구 동작 포함)은 원리적으로 표현 불가능하다는 상한이기도 합니다.

---

## ♻️ 재현성

- **코드** — 본문 첫 페이지에 Project Page(`https://dex-lamp.github.io/`)와 Code(`https://github.com/dex-lamp/LAMP`) 링크가 명기되어 있습니다(이 환경의 네트워크 정책으로 실제 접근은 미확인 — 📄 메타 주석 참조).
- **데이터** — 과제별 시연(20–50개)과 분류기 데이터는 자체 수집이며 공개 여부는 본문에 명시가 없습니다.
- **하드웨어** — Franka Research 3 + Ruiyan 6-DoF hand + RealSense D435/D405 + Synglove·SpaceMouse 텔레옵 리그가 필요해, 실행 재현의 진입 장벽은 실로봇 셋업 전체입니다. 알고리즘 자체(LMPM VAE + MLP BC + RLPD)는 하이퍼파라미터가 Appendix B–C 에 상세히 표로 공개되어 사양 재현성은 높은 편입니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P1(이질적 Body/Hand 액션 전문가) — 주 pillar.** 본 논문은 P1 의 scouting lens 가 명시한 "action-space 아키텍처 비교군"의 정중앙에 있습니다.
  - **D1(split form)** — 팔은 native 좌표, 손만 잠재 인터페이스라는 LAMP 의 비대칭 설계는 "팔과 손을 하나의 동질 action 공간으로 취급하면 안 된다"는 D1 의 해부학적 이질성 주장에 실환경 증거를 더합니다(§3.2 arm-head 인용). 다만 LAMP 의 분리는 표현 수준(좌표계)이지 decoder 모듈 수준이 아닙니다.
  - **D3(Hand output space)** — v1 은 finger joint command 입니다. LAMP 는 "히스토리 조건부 연속 잠재 + 동결 디코더"가 joint command 직접 예측(Raw)을 IL·RL 양쪽에서 크게 앞선다는 비교군 증거입니다(Table 1 Raw BC 0–20% vs Full 45–75% IL). D3 v1 을 당장 뒤집을 증거는 아니지만(6-DoF 손, MLP 백본 한정) D3 의 대안 후보로 추적 가치가 있습니다.
- **P3(Hand-level System0 모듈) — 부 pillar.** LAMP 의 잔차 RL 은 System0 처럼 접촉-보존을 위한 저수준 보정 레이어로 읽히지만, 스코프가 다릅니다 — LAMP 는 시각 포함 full-task 잔차 RL(P3 의 anti-topic 경계)이고, System0 은 vision-excluded 접촉 안정화 서브루프입니다.
  - **D16(System0 output form)** — v1 은 직접 finger joint command 입니다. LAMP 의 "잠재 잔차 + 동결 디코더" 출력 형태는 D16 의 구조적 대안 증거입니다: 같은 크기의 보정 노이즈가 manifold 를 따라 구부러져 접촉을 덜 깹니다( $`\Delta\mathrm{NN}/\mathrm{Disp}`$ 최저, Appendix A).
  - **D17(System0 RL policy spec)** — v1 은 Isaac Lab GPU-병렬 PPO + hand-crafted 접촉 보상입니다. LAMP 는 대척점의 레시피(실환경 RLPD/SAC + 학습된 sparse 시각 보상, 과제당 20k–40k 스텝)로, System0 을 실환경에서 미세조정해야 할 때의 참조 사양입니다.
- **Identity 긴장/지지 — 양면.** LAMP 는 frozen BC 위 residual 모듈이라는 점에서 Identity 의 Antagonist A(correction/residual-on-frozen-VLA) 패턴 그 자체입니다. 단일 과제 내에서는 residual RL 이 성공률을 56.25%→98.75% 로 올려 "residual 은 base 를 넘지 못한다"는 명제의 반례처럼 보이지만, 도달 모션이 동결 디코더의 시연 manifold 로 제한되고(⚖️ 마지막 항목) 새 과제마다 prior·시연·분류기를 전부 다시 만들어야 한다는 저자 명시 한계는 "residual 계열은 base 의 분포에 묶이고 일반화가 없다"는 Identity 의 핵심 주장과 정합합니다. 또한 RL 을 사전학습된 정책 위 후단 미세조정으로만 쓰는 구도는 Antagonist B 에 대한 Identity 의 진단(π RLT 식 deploy-ready fine-tuning)과 일치합니다.
- **닿지 않는 pillar** — P2(관측은 flat ResNet-18 concat — P2 의 anti-topic 예시에 해당), P0(데이터셋 공개 기여 없음), P4(VLM/사전학습 lineage 없음), P5(world model 없음)는 본 논문이 건드리지 않습니다. P4 의 D23(action representation × pretraining) 과는 "연속 액션 표현이 이산 대비 RL-refinability 에 유리하다"는 간접 증거 수준에서만 닿습니다.

---

## ✨ 핀 논문 대비 델타

- **vs DQ-RISE ([arXiv:2509.17450](https://arxiv.org/abs/2509.17450), P1 methodology base — 본 repo 심층분석 [analysis/2509.17450](../2509.17450/analysis.md) 보유)** — 직접 head-to-head 입니다. DQ-RISE 는 hand state 를 residual VQ 이산 코드로 양자화해 IL(diffusion)에 최적화했고, LAMP 는 같은 문제에서 "온라인 잔차 RL 까지 지원하려면 연속·히스토리 조건부여야 한다"고 주장하며 자기 실험에서 DQ-RISE 인터페이스를 IL·RL 모두에서 앞섭니다(단 이식 공정성 한계 — ⚖️ 참조). 진정 새로운 것: **이산 vs 연속 잠재의 분기점을 'RL-refinability'로 옮긴 것**과 off-manifold 비율이라는 진단 지표입니다.
- **vs Dexora ([arXiv:2605.18722](https://arxiv.org/abs/2605.18722), P1 핀)** — Dexora 는 고-DoF 양팔 VLA 의 Body/Hand action-space 레퍼런스입니다. LAMP 는 VLA 가 아니고(언어·멀티태스크 없음) 과제당 수십 개 시연의 단일 과제 세팅이지만, "손 출력 공간을 어떻게 파라미터화할 것인가"라는 Dexora 가 비워둔 축에 실환경 RL 근거를 공급합니다.
- **vs DexSynRefine ([arXiv:2605.05925](https://arxiv.org/abs/2605.05925), P3 methodology base)** — 같은 residual-RL 계열이지만 DexSynRefine 의 잔차는 raw 관절 공간 + RMA 식 접촉 적응이고, LAMP 의 잔차는 학습된 잠재 공간에서 정의됩니다. 잔차의 "좌표계" 자체를 학습 대상으로 만든 것이 델타입니다.
- **vs VE2VF ([arXiv:2605.29564](https://arxiv.org/abs/2605.29564), P3 핀)** — 둘 다 실환경 RL 이지만 VE2VF 는 관측 축(vision-enabled→vision-free 증류)을, LAMP 는 액션 축(action-space 설계)을 공략합니다. 상호 보완적이며 System0 설계 시 양쪽을 조합할 여지가 있습니다.
- **이름 충돌 주의** — P1 핀 목록의 **LaMP ([arXiv:2603.25399](https://arxiv.org/abs/2603.25399), dual-expert gated cross-attention)** 와 본 논문 **LAMP (2607.06323)** 는 전혀 다른 논문입니다. 표기(대문자 vs 혼합)만으로 구분되므로 인용 시 arXiv id 병기가 안전합니다.

---

## ⚙️ 의사결정 함의

- **D3 실험 축 추가** — Hand expert 출력 파라미터화 비교(joint command vs latent)에 "LMPM 식 동결 디코더 + 잠재 오프셋" 변형을 추가할 가치가 있습니다. 구체 설정: hand head 출력 차원을 관절 수(22) 대신 `d_z` 로, LMPM 하이퍼는 본 논문 값( `K=8` , `beta_kl=1e-3` , encoder/decoder MLP width 256)을 출발점으로. 단 우리 손(22-DOF)에서는 `d_z=2` 가 아니라 시연 PCA 설명분산으로 `d_z` 를 먼저 정해야 합니다(⚠️ 1번).
- **D16 대안 등록** — System0 출력 형태에 "잠재 잔차 + 동결 디코더" 옵션을 deferred 후보로. 판단 기준은 본 논문의 지표를 그대로 차용할 수 있습니다: 동일 변위 예산에서의 $`\Delta\mathrm{NN}/\mathrm{Disp}`$ 와 2차 차분 jitter $`J`$ (식 F.1) — 이 두 지표는 우리 평가 하네스에 저비용으로 추가 가능한 액션-품질 메트릭입니다.
- **D17 실환경 참조 사양** — System0 를 실환경에서 후단 미세조정해야 하는 시점이 오면, 본 논문의 RLPD 세트(discount 0.97, batch 256 = 온라인 128 + 시연 128, critic-to-actor ratio 2, 초기 temperature $`10^{-2}`$ , 과제당 20k–40k 스텝)가 검증된 출발 값입니다.
- **바뀌지 않는 것** — 본 논문은 VLA·사전학습·멀티태스크 일반화에 대한 증거가 아니므로, D19–D23(P4 사전학습 축)과 P1 의 π backbone 통합(D7) 결정에는 영향이 없습니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **1. DoF 격차 (가장 싼 체크)** — 6-DoF Ruiyan → 2-D 압축이 성립했다고 22-DOF Sharpa 손에서도 저차원 잠재가 성립한다는 보장이 없습니다. **sanity check**: 보유 텔레옵 시연의 hand joint 궤적에 PCA 를 돌려 95% 설명분산에 필요한 주성분 수를 확인 — 수 시간짜리 오프라인 분석으로, 4–8 이 나오면 전이 가능성이 있고 12+ 가 나오면 "압축 자체"의 전제가 흔들립니다.
- **2. 과제 특화 prior 의 재사용성** — LMPM 은 과제당 20–50개 시연으로 과제별 학습됩니다. 멀티태스크 스택에서는 과제 수만큼 prior 가 필요해질 수 있습니다. **check**: 두 과제 시연을 합쳐 단일 LMPM 을 학습하고 과제별 재구성 오차가 과제 전용 대비 얼마나 열화되는지 비교(시뮬 데이터로 가능).
- **3. 동결 디코더의 OOD 상한** — 시연에 없는 물체·grasp 에서 필요한 손 모양이 manifold 밖이면 정책이 원리적으로 도달 불가합니다. **check**: 학습 물체와 형상이 다른 held-out 물체에서 IL 성공률 붕괴 폭 측정 — 붕괴가 크면 이 인터페이스는 우리 Phase 3(cross-object 일반화)와 충돌합니다.
- **4. Chunked flow-matching 과의 결합 비자명성** — LAMP 의 BC 는 one-step MLP 회귀지만 우리 스택은 π0 식 chunk 단위 플로우 매칭입니다. 잠재 오프셋을 chunk 의 각 스텝마다 줄지, chunk 당 하나 줄지, 히스토리 조건화가 chunk 경계에서 어떻게 갱신되는지가 미정의입니다. **check**: 설계 스파이크로 인터페이스 초안을 그려 보고 모순(디코더 호출 빈도 vs 제어 주기)이 없는지 확인.
- **5. 보상 분류기 운영 비용과 오탐** — 과제별 분류기 학습 + 0.90 임계값의 false positive 는 RL 을 가짜 성공에 수렴시킵니다. 물리 리셋(물체 재배치)도 사람 노동입니다. **check**: 분류기 held-out 정밀도를 먼저 측정하고, 오탐률이 낮아도 에피소드 종료 규칙(식 C.2)과 결합했을 때의 보상 해킹 여지를 소규모 온라인 파일럿으로 확인.
- **6. 평가 통계의 얕음** — 과제당 20 에피소드·단일 랩 수치이므로 95% vs 100% 급 비교는 노이즈 범위일 수 있습니다. 재현 시 시드·에피소드 수를 늘려 신뢰구간을 직접 확보해야 합니다.

---

## 💡 컨텍스트 제안

- **P1 §5 methodology base 추가 후보** — LAMP ([arXiv:2607.06323](https://arxiv.org/abs/2607.06323)): D3 비교군(히스토리 조건부 연속 잠재 hand 인터페이스) + D1 비대칭(팔 native·손 잠재) 실환경 증거. 핀 교체까지는 불요 — 6-DoF 손·단일 과제 세팅이라 증거 등급이 비교군 수준입니다.
- **P3 D16 deferred 후보 노트** — "잠재 잔차 + 동결 디코더" 출력 형태와 판정 지표( $`\Delta\mathrm{NN}/\mathrm{Disp}`$ , jitter $`J`$ )를 D16 의 deferred 대안으로 기록해 두시길 제안합니다.
- **P1 §5 DQ-RISE arXiv id 정정 필요** — 현재 P1.md 는 DQ-RISE 를 [arXiv:2605.03363](https://arxiv.org/abs/2605.03363) 으로 기재하고 있으나, 확인 결과 2605.03363 은 다른 논문("Learning Reactive Dexterous Grasping via Hierarchical Task-Space RL Planning and Joint-Space QP Control")입니다. DQ-RISE("Learning Dexterous Manipulation with Quantized Hand State")의 실제 id 는 [arXiv:2509.17450](https://arxiv.org/abs/2509.17450) 이며 본 repo 의 기존 심층분석 폴더와도 일치합니다. 사람 확인 후 정정을 제안합니다.
- **이름 충돌 표기** — P1 핀 LaMP(2603.25399)와 본 LAMP(2607.06323)의 혼동 방지를 위해, 향후 문서에서 두 논문 모두 arXiv id 병기를 권장합니다.

---

> 💡 base 매핑은 `/implement-design analysis/2607.06323/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
