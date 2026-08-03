# Paper Analysis — CoorDex: Coordinating Body and Hand Priors for Continuous Dexterous Humanoid Loco-Manipulation

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | CoorDex: Coordinating Body and Hand Priors for Continuous Dexterous Humanoid Loco-Manipulation |
| 저자 | Sikai Li, Shuning Li, Zhenyu Wei, Yunchao Yao, Chenran Li, Mingyu Ding |
| 링크 | [arXiv:2606.23680](https://arxiv.org/abs/2606.23680) · [Website](https://skevinci.github.io/coordex/) |
| 발행일 / 버전 | 2026-06-22 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-23 |
| 관련 Pillar | P1, P3 |
| 태그 | dexterity, force |

---

## 🧭 한 줄 요약 (TL;DR)

고차원 휴머노이드 전신 제어와 다지 손 제어를, 각각 동결된 잠재 모션 prior 위에서의 **잔차(residual) 제어**로 치환하고 — 공유 coordination trunk + 분리된 body/hand 잔차 head 로 둘을 조정하는 **coordinated latent residual policy** — 멈추지 않고 걷는 중에 20-DoF 다지 손으로 잡고·옮기고·문을 여는 연속 loco-manipulation 을 학습 가능하게 만든 파이프라인입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 휴머노이드 loco-manipulation 은 보통 "걷다가 멈춰서 조작하고 다시 걷는" stop-and-go 로 단순화되고, end effector 도 open-close grasp primitive 수준의 저(低)-DoF 에 머무릅니다. 걷는 도중 고-DoF 다지 손으로 접촉 집약적 조작을 수행하는 *on-the-move dexterous loco-manipulation* 은 거의 다뤄지지 않았습니다.
- **기존 접근의 한계** — 손 중심 방법들은 grasp 합성·hand-object 표현·교차 임베디먼트 전이에 강하지만, 손목(wrist)/팔 궤적이 텔레오퍼레이션·플래닝·고정 베이스·정지 전신 컨트롤러로 *외부에서 주어진다*고 가정합니다. 걷는 휴머노이드에서는 손목 자세가 발 타이밍·루트 모션·몸통 자세·전신 reaching 에서 *창발(emerge)* 하므로 이 가정이 깨집니다.
- **본 논문의 가설** — 손목 배치(body-side)와 손가락 조정(hand-side)을 **분리**해 각각 body prior 와 wrist-stabilized hand prior 로 모델링하고, 잔차 정책으로 둘을 *조정*하면 고차원 탐색 문제가 학습 가능해진다는 가설입니다.
- **왜 지금 중요한가** — 고-DoF 다지 손을 단 손에서 전 관절을 직접 RL 로 탐색하면 locomotion 과 손 제어가 동시에 결합된 고차원 exploration 폭발이 발생합니다. 구조화된 잠재 행동공간(prior)으로 탐색 차원을 낮추는 것이 이 결합을 풀 수 있는지가 핵심 질문입니다.

---

## 🧩 핵심 기여

- **완결형 학습 파이프라인** — Isaac Lab 에서 시뮬레이션 전신·손 시연 수집 → 모션 트래킹 정책 → prior 증류(distillation) → downstream 잔차 RL 까지 이어지는 고-DoF 다지 휴머노이드 loco-manipulation 전체 파이프라인을 제시합니다.
- **비대칭 body-hand prior 합성** — 손목 배치는 task-aligned **body prior** 의 전신 모션에서 창발시키고, 재사용 가능한 손가락 스킬은 **wrist-stabilized hand prior** 가 담당하는 비대칭 분해를 제안합니다.
- **Coordinated latent residual policy** — 동결된 두 prior 를 공유 task context 와 body·hand 잔차 head 로 적응시키는 조정 정책으로, 전신 모션의 자연스러움과 손가락 접촉 신뢰성을 동시에 보존합니다.
- **Ablation 으로 입증한 구조 필요성** — walk-grasp-carry 과제에서 joint-space PPO, hand joint-space 제어, monolithic latent 예측이 동일 보상 예산에서 *모두 실패*(success 0)함을 보여, 잠재-prior 인터페이스와 구조화된 body-hand 조정이 둘 다 필수임을 입증합니다.

---

## 🔑 기술 키워드

- **Coordinated latent residual policy** — 동결된 두 모션 prior 위에서 공유 coordination trunk + 분리된 body/hand head 로 잠재 잔차를 예측하는 본 논문의 핵심 정책 구조 — "기본 동작은 prior 가 깔아주고, 정책은 그 위에 교정값만 얹는다"는 발상.
- **Motion prior** — 전 관절을 직접 제어하는 대신, 자연스러운 모션이 압축된 저차원 잠재 행동공간 — RL 탐색을 그 잠재 공간 안으로 가두어 차원을 낮추는 장치.
- **Privileged motion tracking teacher** — 특권(privileged) 상태를 보며 참조 모션을 추종하도록 학습된 교사 정책 — 이후 proprioception 만 보는 학생 prior 로 증류됩니다.
- **Proprioception-conditioned prior** — 배포 가능한 고유감각(proprioception) 슬라이스만으로 잠재 평균을 내놓는 prior 네트워크 — 특권 정보 없이도 prior 가 기본 잠재 명령을 제공.
- **Variational bottleneck (VAE distillation)** — 인코더·prior·디코더로 구성된 변분 병목으로 교사를 잠재 스킬 공간에 증류 (PULSE 계열) — KL 항이 인코더와 prior 분포를 정렬.
- **Wrist-stabilized hand prior** — 학습 중 참조 손목 자세·속도를 시뮬레이션에 직접 써넣어 손목을 운동학적으로 고정하고, 손 prior 가 *손가락 관절만* 제어하도록 한 설계 — 잠재 용량을 6D 손목 모션에 낭비하지 않게 함.
- **Residual reinforcement learning** — prior 가 주는 기본 잠재 명령 위에 정책이 잔차 $`\Delta\mathbf{z}`$ 만 더하는 RL — 동결 prior 의 분포 주변에서만 탐색이 일어남.
- **NoDemoRSI** — 외부 시연 없이, 정책 스스로 도달한 상태를 스냅샷 버퍼에 모아 일부 에피소드를 후반 단계에서 reset 시키는 demonstration-free reference state initialization — 장기 과제의 희소 탐색 병목 완화.
- **Loco-manipulation** — 보행(locomotion)과 조작(manipulation)을 시간상 분리하지 않고 동시에 수행하는 문제 설정 — 본 논문은 걷는 중 grasp/운반이 일어나는 *non-stop* 버전을 다룸.
- **Coordination trunk / residual heads** — 모든 task 상태를 함께 보는 공유 trunk 와, body·hand 적응을 각자 별도 출력 경로로 내보내는 두 head — monolithic 단일 head 와의 대비점.

---

## 🔬 방법론

### 직관

CoorDex 의 출발점은 "걷는 휴머노이드에서 손목을 어디에 둘지(body-side)와 손가락을 어떻게 움직일지(hand-side)는 성격이 전혀 다른 문제"라는 관찰입니다. 손목 자세는 발 디딤·몸통·루트 모션의 결과로 *창발*하는, 본질적으로 전신 모션 문제입니다. 반면 손가락 조정은 접촉이 일어나는 좁은 영역에서의 정밀 제어 문제입니다. 만약 하나의 손 prior 가 6D 손목 모션까지 설명하려 들면, 그 잠재 용량 대부분을 손목 배치에 써버려 정작 손가락 조정에 쓸 표현력이 남지 않습니다.

그래서 CoorDex 는 두 개의 분리된 모션 prior 를 만듭니다. **body prior** 는 보행·reaching·손목 배치를 담당하고, **hand prior** 는 손목이 운동학적으로 고정된 환경에서 *손가락 관절만* 추종하도록 학습됩니다. 두 prior 모두 특권 교사를 먼저 학습한 뒤, 배포 가능한 고유감각만 보는 학생 prior+디코더로 증류합니다(PULSE 식 변분 병목). 증류가 끝나면 prior 와 디코더를 **동결**하고, 그 잠재 공간을 downstream RL 의 *행동공간*으로 씁니다.

downstream 에서는 정책이 관절 목표를 직접 내지 않고, 두 prior 가 주는 잠재 평균 위에 **잔차** $`\Delta\mathbf{z}`$ 만 예측합니다. 이때 단순히 잔차를 두 덩어리로 쪼개는 게 아니라, 모든 task 상태를 함께 보는 **공유 coordination trunk** 로 body-hand 결합을 먼저 포착한 뒤, **분리된 body head 와 hand head** 가 각각 잔차를 내놓습니다. 공유 trunk 는 두 서브시스템이 같은 task phase·접촉 상태를 공유하게 하고, 분리된 head 는 전신 적응과 손가락 적응이 하나의 출력 경로로 뭉개지지 않게 합니다. 이 구조 덕분에 탐색은 저차원 잠재 공간에서 일어나면서도 보행과 grasp 의 제어 권한은 분리된 채로 유지됩니다.

> "It builds separate body and hand priors and trains a downstream residual RL policy to coordinate them." (§3)
(이 한 문장이 파이프라인 전체를 요약합니다 — prior 구성과 잔차 RL 조정의 2단 구조가 본 논문의 골격입니다.)

![Figure 2 — CoorDex overview / pipeline](https://arxiv.org/html/2606.23680/x1.png)

> "Figure 2: Overview of CoorDex. Body and hand reference motions are tracked by privileged teachers and distilled into separate proprioception-conditioned latent priors. During downstream RL, a coordinated residual policy uses task context and prior means to predict body and hand latent residuals. The frozen decoders map the corrected latents to joint-position targets for loco-manipulation." (§3)
(교사 트래킹 → prior 증류 → 동결 prior 위 잔차 정책 → 동결 디코더의 관절 목표 출력이라는 좌→우 데이터 흐름을 시각화합니다.)

### 아키텍처

전체는 **(1) prior 구성**과 **(2) coordinated latent residual policy** 두 단계로 나뉩니다. 서브시스템을 $`x\in\{b,h\}`$ (body/hand)로 표기합니다.

**Prior 구성 (§3.1).**

- **시연 수집** — Isaac Lab 의 시뮬레이션 텔레오퍼레이션 파이프라인으로 참조 모션을 모읍니다. 하반신 보행은 AGILE 기반 컨트롤러가, 오른 손목·손 모션은 Apple Vision Pro(CloudXR XR 인터페이스)로 운영자가 제공합니다. 추적된 손목 자세는 Pink IK solver 의 end-effector 목표가 되고, 손 모션은 optimization 기반 dex-retargeting 으로 대상 다지 손에 retarget 됩니다.
- **Body prior** — 일반 전신 모션 트래킹 교사 $`\pi_{T}^{b}`$ (BeyondMimic 계열)를 먼저 학습합니다. 교사는 body proprioception $`\mathbf{s}^{b,p}_{t}`$ 와 참조 목표 $`\mathbf{s}^{b,g}_{t}`$ 를 받아 body 관절 목표 $`\mathbf{a}^{b,T}_{t}`$ 를 냅니다. 다지 손이 장착된 휴머노이드 모델 위에서 참조 모션을 전처리해 downstream 의 형상·기구학 구조와 일치시킵니다.
- **Hand prior** — floating-hand 환경에서 특권 손 트래킹 교사 $`\pi_{T}^{h}`$ (ManipTrans 식 retarget 된 hand-object 모션)를 학습합니다. 핵심은 **wrist-stabilized 설계**입니다.

> "During hand-prior training, the reference wrist pose and velocity are written directly into simulation, so the teacher and the learned prior control only finger motion." (§3.1)
(참조 손목을 시뮬레이션에 직접 써넣어 손목을 운동학적으로 고정 → 교사·prior 는 손가락 관절만 제어. 손목 자유도를 떼어내야 손 잠재 공간이 손가락 조정에 집중할 수 있습니다.)

> "This wrist-stabilized design keeps the hand latent space from spending most of its capacity on 6D wrist motion, and makes the learned latent command directly useful for finger coordination." (§3.1)
(왜 중요한가 — 동일 잠재 차원이라도 손목 6D 를 빼면 손가락 조정에 쓸 표현력이 그만큼 늘어납니다. body prior 가 손목을 결정하는 downstream 인터페이스와도 자연스럽게 맞물립니다.)

**Coordinated latent residual policy (§3.2).** 각 제어 스텝에서 동결 prior 가 proprioception 으로부터 잠재 평균을 냅니다 (식 2):

$$\boldsymbol{\mu}^{b,p}_{t}=\mathrm{Mean}\left[\mathcal{R}_{b}\left(\mathbf{z}^{b}_{t}\mid\mathbf{s}^{b,p}_{t}\right)\right],\qquad\boldsymbol{\mu}^{h,p}_{t}=\mathrm{Mean}\left[\mathcal{R}_{h}\left(\mathbf{z}^{h}_{t}\mid\mathbf{s}^{h,p}_{t}\right)\right].$$

정책은 관절 목표가 아니라 두 잠재 공간의 잔차를 예측합니다 (식 3):

$$\Delta\mathbf{z}_{t}=\left[\Delta\mathbf{z}^{b}_{t},\Delta\mathbf{z}^{h}_{t}\right],\qquad\Delta\mathbf{z}^{b}_{t}\in\mathbb{R}^{d_{b}},\quad\Delta\mathbf{z}^{h}_{t}\in\mathbb{R}^{d_{h}}.$$

> "The actor predicts residuals in the two latent spaces rather than joint-space targets" (§3.2)
(행동공간 자체를 prior 의 잠재 공간으로 옮긴 것이 차원 축소의 핵심 — 정책은 "기본값 대비 얼마나 어긋날지"만 학습합니다.)

먼저 공유 coordination 표현 $`\mathbf{c}_{t}`$ 로 body-hand 결합을 포착하고, 그 다음 body head $`f_{b}`$ · hand head $`f_{h}`$ 가 잔차를 냅니다 (식 4):

```math
\begin{gathered}\mathbf{c}_{t}=f_{\mathrm{coord}}\left(\mathbf{s}^{b,p}_{t},\mathbf{s}^{h,p}_{t},\mathbf{s}^{\mathrm{task}}_{t},\mathbf{s}^{\mathrm{hand\text{-}object}}_{t},\boldsymbol{\mu}^{b,p}_{t},\boldsymbol{\mu}^{h,p}_{t},\Delta\mathbf{z}_{t-1}\right),\\[3.0pt]
\Delta\mathbf{z}^{b}_{t}=\tanh\left(f_{b}(\mathbf{c}_{t},\mathbf{s}^{b,p}_{t},\boldsymbol{\mu}^{b,p}_{t})\right),\quad\Delta\mathbf{z}^{h}_{t}=\tanh\left(f_{h}(\mathbf{c}_{t},\mathbf{s}^{h,p}_{t},\boldsymbol{\mu}^{h,p}_{t},\mathbf{s}^{\mathrm{hand\text{-}object}}_{t})\right).\end{gathered}
```

여기서 $`\mathbf{s}^{\mathrm{task}}_{t}`$ 는 물체 자세·목표·projected gravity·접촉 특징 등 task 상태를, $`\mathbf{s}^{\mathrm{hand\text{-}object}}_{t}`$ 는 손 좌표계의 물체 자세·fingertip-object 접촉 특징을 담습니다. 보정된 잠재 명령은 (식 5):

$$\tilde{\mathbf{z}}^{b}_{t}=\boldsymbol{\mu}^{b,p}_{t}+\Delta\mathbf{z}^{b}_{t},\qquad\tilde{\mathbf{z}}^{h}_{t}=\boldsymbol{\mu}^{h,p}_{t}+\Delta\mathbf{z}^{h}_{t}.$$

최종 관절 목표는 동결 디코더가 냅니다 (식 6):

$$\mathbf{a}^{b}_{t}=D_{b}\left(\mathbf{s}^{b,p}_{t},\tilde{\mathbf{z}}^{b}_{t}\right),\qquad\mathbf{a}^{h}_{t}=D_{h}\left(\mathbf{s}^{h,p}_{t},\tilde{\mathbf{z}}^{h}_{t}\right).$$

body 디코더는 전 휴머노이드 body 관절 목표를, hand 디코더는 선택된 다지 손의 active 손가락 관절 목표를 냅니다. 두 출력은 해당 관절 슬롯에 삽입되어 저수준 PD 컨트롤러로 실행됩니다.

> "This design couples the two subsystems through shared task state without collapsing them into a single monolithic action head." (§3.2)
(공유 trunk 로 결합은 유지하되 monolithic 단일 head 로 합치지 않는 것 — 이것이 §4.4 ablation 에서 monolithic 대비 우위의 근거가 됩니다.)

### 학습 목표 / 손실

**증류 손실 (§3.1, 식 1).** 각 서브시스템 $`x\in\{b,h\}`$ 의 학생은 인코더 $`\mathcal{E}_{x}`$, proprioceptive prior $`\mathcal{R}_{x}`$, 디코더 $`D_{x}`$ 로 구성되며, 손실은 교사-행동 재구성 + 인코더 평균의 시간적 평활 + 인코더·prior 간 KL 정규화의 합입니다:

$$\mathcal{L}^{x}_{\mathrm{distill}}=\mathcal{L}^{x}_{\mathrm{action}}+\alpha_{x}\mathcal{L}^{x}_{\mathrm{regu}}+\beta_{x}\mathcal{L}^{x}_{\mathrm{KL}}.$$

**구체 형태 (§A.3).** 학생의 세 학습 네트워크는 인코더 $`q_{\phi}(z_{t}\mid s^{\mathrm{full}}_{t})`$, prior $`p_{\psi}(z_{t}\mid s^{\mathrm{prop}}_{t})`$, 디코더 $`D_{\theta}(s^{\mathrm{prop}}_{t},z_{t})`$ 이고, 학습 시 $`z_{t}`$ 는 reparameterization trick 으로 인코더에서 샘플링됩니다. 추론·downstream RL 시 기본 잠재는 prior 평균입니다. 전체 증류 손실은:

$$\mathcal{L}=\lambda_{a}\|\hat{a}_{t}-a^{T}_{t}\|_{2}^{2}+\lambda_{s}\|\mu^{q}_{t}-\mu^{q}_{t-1}\|_{2}^{2}+\lambda_{\mathrm{KL}}D_{\mathrm{KL}}\left(q_{\phi}(z_{t}\mid s^{\mathrm{full}}_{t})\,\|\,p_{\psi}(z_{t}\mid s^{\mathrm{prop}}_{t})\right)$$

> "The decoder learns the teacher's motor actions. The prior makes the latent usable from proprioception alone. And the temporal regularizer keeps nearby states from mapping to discontinuous latent codes." (§A.3)
(세 항의 역할 분담 — 재구성은 디코더가 교사 행동을 배우게, KL 은 prior 가 proprioception 만으로 쓸 수 있게, 평활 항은 인접 상태가 불연속 잠재로 매핑되지 않게 합니다. PULSE 의 동기를 그대로 따릅니다.)

**downstream 보상.** WalkGrab·OpenFridge 는 단일 stage 보상으로, phase 구조는 보상 항 내부의 predicate gating 으로 유도됩니다 — grasp predicate $`\mathbb{1}[\text{grasped}]`$ 가 approach 항을 끄고 manipulation 항을 켜며, contact predicate 가 문 열기/들어올리기 보상을 게이팅합니다. 보상은 locomotion·balance, palm-object reaching·alignment, fingertip contact·sustained contact, 완료(lift/carry/door-angle), 그리고 잠재 잔차·디코딩 행동 변화·관절 속도에 대한 정규화의 가중합입니다. 장기 과제 WalkPickTurn 은 stage 가중 보상 + NoDemoRSI 를 씁니다.

### 학습 셋업

- **플랫폼·하드웨어** — Isaac Lab, 29-DoF Unitree G1 + 20-DoF 5지 WUJI 손. body 관절 29 개만 actuate(학습 효율). 제어 60 Hz, physics step $`1/240`$ s, decimation 4.
- **행동 차원 (Table 1)** — body DoF 29 / 잠재 16, WUJI 손 DoF 20 / 잠재 12 → downstream 잔차 행동 28-dim (16 body + 12 hand).
- **Prior 입력** — body prior 는 5-프레임 suffix $`5\times[\omega_{\mathrm{base}}(3),q(29),\dot{q}(29),a_{t-1}(29)]=450`$ 차원, hand prior 는 $`[v_{\mathrm{wrist}}(3),\omega_{\mathrm{wrist}}(3),q_{\mathrm{rel}}(20),\dot{q}_{\mathrm{rel}}(20),a_{t-1}(20)]=66`$ 차원.
- **증류 옵티마이저** — body LR $`2\times10^{-4}`$, hand LR $`5\times10^{-4}`$, action 계수 1.0, smoothness 0.005, KL 계수 anneal(body $`10^{-3}\to10^{-4}`$ @15k–20k, hand $`10^{-2}\to10^{-3}`$ @15k–25k). 인코더·디코더·prior MLP $`[512,256,128]`$. 최대 30000 iter, grad accum 16, grad clip 1.0.
- **downstream PPO (Table 9)** — 4096 env, rollout 24 step, batch 98304, minibatch 4, epoch 5, $`\gamma=0.99`$, $`\lambda=0.95`$, clip 0.2, entropy 0.005, value 계수 1.0, adaptive LR $`1\times10^{-3}`$(KL target 0.01), max grad norm 1.0. actor/critic $`[1024,512,256]`$ ELU, coord trunk $`[512,256]`$, body/hand head $`[256,128]`$, 잔차 scale 1.0, init action noise $`\sigma=0.22`$.
- **downstream 합성 (§A.4)** — 동결 prior·디코더·observation normalizer 만 로드. 디코딩된 hand 목표에 EMA(계수 0.4) 적용 후 Isaac Lab joint position action term 으로 전송.

---

## 📊 실험 설정과 결과

평가는 별도 명시 없으면 10,000 병렬 환경에서 모은 50,000 에피소드 기준이며(Isaac Lab), success·fall·drop·과제별 진행 지표를 보고합니다. 세 가지 질문을 검증합니다 — **Q1** 통합 body–hand 잠재 잔차 인터페이스가 다양한 스킬을 지원하는가, **Q2** 잠재 행동이 joint-space 직접 제어보다 탐색에 유리한가, **Q3** coordinated 잔차 예측이 monolithic 대비 우월한가.

**과제별 성능 (Table 2 — Q1).**

| Task | Success | Fall | Drop | 과제별 지표 |
|------|---------|------|------|-------------|
| WalkGrab | 0.55 | 0.00 | 0.40 | 속도 프로파일 (Fig. 4) |
| OpenFridge | 0.66 | 0.00 | – | 문 각도 57.76 / $`60^{\circ}`$ |
| WalkPickTurn | 0.89 | 0.01 | 0.10 | 최소 heading 오차 9.98° |

> "Table 2 shows that the same CoorDex interface can be instantiated across all three tasks, answering Q1." (§4.2, Table 2)
(동일 인터페이스가 세 과제 모두에 인스턴스화됨 → Q1 긍정. WalkGrab 이 가장 어려운 이유는 grasp 이 연속 전신 모션 중에 일어나야 하기 때문이고, OpenFridge 는 조작 중 감속·재배치를 허용합니다.)

**행동공간 변형 (Table 3 — Q2).** 동일 환경·동일 task 보상·동일 PPO 예산에서 비교합니다. Reach=palm 이 임계 거리 진입, Grasp=병이 임계 이상 들림, Stop=병 근처에서 속도 임계 이하로 감속, Fall=낙상 종료 비율.

| Method | Success | Reach | Grasp | Stop | Fall |
|--------|---------|-------|-------|------|------|
| All Joint Space | 0 | 1.00 | 0.00 | 0.86 | 0.04 |
| Body Prior + Hand Joint Space | 0 | 0.96 | 0.01 | 0.90 | 0.04 |
| CoorDex | 0.55 | 1.00 | 0.55 | 0.00 | 0.00 |

> "This behavior shows that the body prior alone is not enough for non-stop dexterous loco-manipulation. The hand prior is also needed to make finger coordination learnable under residual RL." (§4.3, Table 3)
(두 실패 변형의 진단 — All Joint Space 는 전신을 비자연스럽게 비틀며 grasp 자체를 못 하고, Body Prior + Hand Joint Space 는 손목은 갖다 대지만(Reach 0.96) 손가락 조정을 joint space 에서 직접 못 배워 결국 *멈춰서*(Stop 0.90) 정지 grasp 으로 풀려 합니다. CoorDex 만 Stop 0.00 으로 비정지 grasp 을 달성.)

**Coordinated vs Monolithic (Table 4 — Q3).** 동일 동결 prior·동일 잠재 차원·동일 환경/보상, *정책 구조만* 다릅니다. action rate = 연속 제어 스텝 간 디코딩된 body 관절 목표의 평균 변화량(낮을수록 부드러움).

| Method | Success | Action rate | Fall |
|--------|---------|-------------|------|
| Monolithic Latent Residual | 0.00 | 0.40 | 0.02 |
| CoorDex | 0.55 | 0.22 | 0.00 |

> "CoorDex performs better because the shared trunk lets the policy reason about the same task state, while the separate heads keep body adaptation and finger adaptation from being forced through a single output pathway." (§4.4, Table 4)
(두 prior 가 모두 있어도 actor 구조가 중요함 — monolithic 은 방향은 따라가나 body 모션이 더 떨리고(action rate 0.40 vs 0.22) success 0 입니다. 분리 head 가 전신·손가락 적응을 단일 경로로 강제하지 않는 것이 결정적.)

![Figure 1 — 세 과제 (walk-grasp-carry, fridge, walk-pick-turn)](https://arxiv.org/html/2606.23680/figures/CoDex_teaser_v1.png)

> "Figure 1: Dexterous loco-manipulation on the move. CoorDex enables a humanoid equipped with high-DoF dexterous hands to perform continuous loco-manipulation tasks that require simultaneous coordination between locomotion and dexterous hand control, such as walk-grasp-carry, fridge opening while stepping back, and walk-pick-turn." (§1)
(보행과 손 제어의 동시 조정이 필요한 세 연속 과제를 시각화 — 멈춤 없이 잡고·운반하고·문 열고·들고 도는 동작.)

![Figure 3 — WalkGrab 정성 비교](https://arxiv.org/html/2606.23680/x2.png)

> "Figure 3: Qualitative comparison on WalkGrab. Each column shows sequential key frames from one rollout of the corresponding method. All Joint Space produces unstable whole-body motion. Body Prior + Hand Joint Space reaches the bottle but fails to learn a reliable grasp. Monolithic Latent Residual reaches the interaction region but produces less natural body motion and fails to complete the task. CoorDex completes the full sequence of approach, grasp, lift, and carry." (§4.3)
(세 실패 변형과 CoorDex 의 롤아웃 키프레임 비교 — Table 3·4 의 수치적 실패가 어떤 거동으로 나타나는지 보여줍니다.)

![Figure 4 — WalkGrab non-stop 속도 프로파일](https://arxiv.org/html/2606.23680/figures/velocity_vs_rel_x.png)

> "Figure 4: Non-stop locomotion on WalkGrab." (§4.2)
(상대 전진 위치 $`d_{t}`$ 별 body-frame 전진 속도. CoorDex 는 병 근처에서 약간 감속하나 $`d_{t}=0`$ 부근에서도 약 $`0.25\,\mathrm{m/s}`$ 의 전진 속도를 유지 → 멈춰서 잡는 것이 아님을 입증.)

**NoDemoRSI 보조 효과.** WalkPickTurn(success 0.89)은 3-stage(approach & hand-prep / grasp & lift / turn)로 분해되고, 비초기 stage 마다 capacity 512 의 ring buffer 가 정책이 도달한 상태 스냅샷을 저장합니다. 난이도×가용성 비례 적응 sampling, 단계별 progressive unlock(직전 stage success $`>0.70`$ + 최소 128 스냅샷), 전 단계 success $`0.80`$ 도달 시 stage-0 85% consolidation 모드로 외부 시연 없이 curriculum 을 형성합니다.

---

## ⚖️ 한계

- **RL-as-core 의존 + 보상 엔지니어링 부담** — 능력의 원천이 과제별로 정교하게 손-튜닝된 다항 보상(WalkGrab 만 20+ 항, OpenFridge·WalkPickTurn 별도 표)입니다. 새 과제마다 predicate gating·가중치·임계값을 다시 설계해야 하므로, 잠재-prior 인터페이스가 탐색을 쉽게 해줘도 *과제 일반화*는 보상 설계 노동에 묶여 있습니다.
- **Privileged 관측 — 지각 부재** — 현재 정책은 물체 자세·접촉 신호 등 특권 상태를 그대로 관측하며(저자 명시), 지각이나 visual sim2real 을 다루지 않습니다. 실제 로봇에서 물체 6D 자세를 동일 정확도로 추정할 수 있어야 성능이 유지되는데, 그 추정 오차의 영향은 평가되지 않았습니다.
- **정량 결과는 시뮬레이션 전용** — 모든 success 수치는 Isaac Lab 시뮬레이션 값이고, 실제 로봇 결과(Fig. 5–7)는 기록된 관절 궤적을 G1+Dex3-1 에 *kinematic replay* 한 정성 시각화일 뿐 closed-loop 검증이 아닙니다. 게다가 시뮬레이션은 G1+WUJI, 하드웨어는 G1+Dex3-1 로 손이 달라 직접 비교가 아닙니다.
- **WalkGrab drop 0.40 — 신뢰성 여백** — 가장 깨끗한 통제 과제에서도 success 0.55, drop 0.40 으로, 일단 잡아도 운반 중 40%가 떨어집니다. sustained-grasp/forward-progress 보상에도 불구하고 잠재 잔차의 접촉 유지 한계를 시사합니다.
- **잔차의 표현력 상한** — 행동공간이 동결 prior 의 잠재로 제한되므로, 정책이 도달할 수 있는 거동은 본질적으로 prior 디코더가 span 하는 manifold + tanh 로 bound 된 잔차 근방에 갇힙니다. prior 가 포착하지 못한 접촉 형상은 잔차만으로 복원이 어렵습니다(저자 미논의 추론 갭).
- **장기 과제의 task-specific 탐색 보조** — WalkPickTurn 은 NoDemoRSI 라는 별도 curriculum 없이는 초기 상태에서의 순수 보상 최적화가 불안정하다고 저자가 명시합니다. 즉 정책 구조만으로 장기 결합이 풀리지 않고, 외부(자기-생성) reset 분포에 의존합니다.

---

## ♻️ 재현성

- **코드** — 본문·메타에서 공개 코드 저장소(GitHub) 링크는 확인되지 않습니다. 자료는 프로젝트 페이지([Website](https://skevinci.github.io/coordex/))뿐입니다.
- **데이터** — 시연은 Isaac Lab 시뮬레이션 텔레오퍼레이션(AGILE 보행 + Apple Vision Pro/CloudXR + Pink IK + dex-retargeting)으로 *생성*되며 별도 공개 데이터셋이 아닙니다. 손 모션은 ManipTrans 식 주석 + SMPL-X/MANO 키포인트를 사용합니다.
- **하드웨어** — 시뮬레이션 Unitree G1(29-DoF) + WUJI 손(20-DoF); 실제 replay 는 G1 + Dex3-1 손. 둘 다 상용 플랫폼이나 WUJI 손 가용성은 별도 확인 필요.
- **구현 디테일** — 부록 A/B 에 prior·증류·보상·하이퍼파라미터·NoDemoRSI 설정이 표 단위로 상세히 제공되어, 코드 없이도 상당 부분 재현 명세가 갖춰져 있습니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P1**(이종 Body/Hand 액션 전문가) — 본 논문의 핵심 구조 `coordinated latent residual policy`(공유 trunk + 분리 body/hand head)는 우리 [D1](split form)의 v1 선택인 **(iii) hybrid — 공유 trunk + 분리 body/hand head 와 정확히 같은 형태**입니다. body=손목 배치(우리 [D2](Body output space): wrist/flange pose), hand=손가락 관절(우리 [D3](Hand output space): finger joint command) 분리, body→hand 흐름(우리 [D6](coordination direction & flow): body→hand hierarchical)도 일치합니다. 다만 본 논문은 IL flow-matching VLA 가 아니라 *RL+모션 prior* 위에서 이 구조를 구현한 증거입니다.
- **P3**(Hand-level System0 RL 안정화) — 동결 prior 위 잔차 PPO, contact/grasp 보상 항(fingertip contact `>1N`, grasp force clip), Isaac Lab GPU-병렬은 우리 [D17](System0 RL policy spec)의 셋업과 결이 같습니다. 특히 wrist-stabilized hand prior + 손가락 잔차는 "손가락 접촉 신뢰성 향상"이라는 System0 의 문제의식과 직접 겹칩니다.
- **Identity 긴장** — 본 논문은 *full task* 능력의 원천을 RL 로 삼습니다(Antagonist B: RL-as-core). 우리 Identity 는 일반화 dexterity 를 RL 로 풀지 않고 RL 을 System0 접촉 안정화로만 한정합니다. 또 "동결 모듈 위 잔차" 구조는 Antagonist A(correction/residual on frozen module)의 분포-bound 한계와 같은 형태의 긴장을 내포합니다 — 단, 여기서 동결 모듈은 VLA 가 아니라 모션 prior 라는 점이 다릅니다.
- **경쟁자 함의** — 휴머노이드 전신 loco-manipulation 은 P3 Anti-topic("Mobile manipulation / whole-body humanoid")에 해당해 *body/locomotion 절반*은 우리 범위 밖입니다. 가치는 **hand prior 절반**(wrist-stabilized 손가락 prior + 잔차 접촉 학습)에 집중됩니다.

---

## ✨ 핀 논문 대비 델타

- **vs Shared-Autonomy Arm-Hand VLA (DexGrasp-VLA, P1 핀)** — 둘 다 해부학적 body/arm ↔ hand 분리를 취하지만, DexGrasp-VLA 는 (VR-teleop 매크로 팔 + 자율 손 VLA)의 IL 구도인 반면 CoorDex 는 두 *동결 모션 prior* 의 RL 잔차 합성이라 학습 패러다임이 다릅니다. CoorDex 는 손목이 전신에서 *창발*하는 보행 설정을 추가로 다룹니다.
- **vs LaMP (P1 핀)** — LaMP 의 dual-expert gated cross-attention 과 CoorDex 의 공유 trunk + 분리 head 는 같은 [D1] hybrid 군이나, CoorDex 의 결합은 attention 게이팅이 아니라 *task 상태를 함께 보는 trunk → 분리 head*의 잔차 구조라는 점이 새롭고, monolithic 대비 우위를 ablation 으로 직접 보입니다.
- **vs DexSynRefine (P3 비핀 base)** — 둘 다 "residual RL + 동결 prior" 계열이지만, DexSynRefine 의 잔차는 RMA-style 접촉 적응을 joint/contact 수준에서 더하는 반면, CoorDex 는 잔차를 *증류된 잠재 모션 prior 의 latent 공간*에서 더합니다 — 탐색 차원 축소가 prior 의 표현력에 묶이는 형태가 진정 새로운 부분.

---

## ⚙️ 의사결정 함의

- **[D1] hybrid 분리의 외부 증거 확보** — 우리 v1 선택(공유 trunk + 분리 head)이 IL 이 아닌 RL+prior 도메인에서도 monolithic 대비 success 0→0.55, action rate 0.40→0.22 로 우월함을 보인 직접 비교를 인용 자산으로 확보합니다. body/hand head 분리의 "단일 출력 경로 회피" 논거(§4.4)를 우리 D1 rationale 에 보강.
- **[D4](Body↔Hand information sharing) 설계 옵션 추가** — CoorDex 의 결합은 우리 v1 FiLM(단일 지점 $`\gamma,\beta`$)과 달리 *공유 trunk 가 두 head 입력을 함께 생성*하는 방식입니다. "FiLM 단일 지점" vs "공유 trunk 양방 주입"을 D4 비교군으로 명시할 수 있습니다(config: hand head 입력에 task-coupled `coordination feature` 연결 여부).
- **[D17] System0 보상 항 참조** — fingertip contact predicate(`mean_i 1[||F_i||>1N]`), grasp force `clip(Σ||F||,0,2)`, sustained-grasp 카운터 같은 구체 항을 System0 reward-term 후보(AnyRotate 구조 보강)로 차용 가능. 단 우리 System0 은 vision-excluded·tactile 중심이므로 물체-자세 의존 항은 제외.
- **검증 대상 메트릭** — "non-stop" 판정을 위한 *상대 위치 binned 속도 프로파일*(Fig. 4)은 우리 grasp 데모에서 "정지 grasp 으로 회피했는가"를 측정하는 진단 지표로 채택 가치가 있습니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 체크) 도메인 자체가 우리 스택과 다름** — CoorDex 는 보행 휴머노이드(G1 + WUJI)이고 우리는 고정 베이스 팔 + Sharpa/xhand 입니다. body prior·locomotion 보상·NoDemoRSI 의 stage 분해 전부 보행 의존이라 *그대로 전이 불가*. 먼저 "hand prior + 잔차 접촉 학습"만 떼어 우리 손에 적용 가능한지부터 판별해야 합니다(나머지는 P3 Anti-topic).
- **잠재-prior manifold 가 우리 접촉 형상을 span 하는가** — 손 prior 는 ManipTrans/MANO 인간 손 모션에서 증류됩니다. 우리 타깃 과제(in-hand cube rotation, tool articulation)의 접촉 형상이 그 prior manifold 밖이면 tanh-bound 잔차로 복원 불가. 싼 체크: 타깃 데모 손 궤적을 prior 디코더로 재구성해 reconstruction error 를 먼저 측정.
- **Privileged 물체 자세 의존** — 모든 task 보상이 물체 6D 자세·접촉 predicate 를 특권으로 받습니다. 우리 System0 은 vision-excluded(tactile + joint state)라 물체-자세 기반 항을 쓸 수 없으므로, 동일 보상 구조를 그대로 옮기면 관측 불일치로 무효. 어떤 항이 tactile-only 로 재정의 가능한지 선별 필요.
- **RL 능력원천의 일반화 비용** — 본 논문이 보인 success 는 과제별 보상 손-튜닝의 산물입니다. 우리 Identity 는 일반화 dexterity 를 reward-engineerable 하지 않다고 보므로, 이 파이프라인을 *capability source*로 채택하면 Identity 와 충돌. System0 범위(slip/grasp 유지) 안에서만 차용해야 합니다.
- **EMA·tanh 등 안정화 트릭의 sim-bound 가능성** — hand 목표 EMA(0.4), action-rate 페널티, init noise $`\sigma=0.22`$ 등은 Isaac Lab PhysX 접촉 위에서 튜닝된 값입니다. 실제 접촉(점탄성 변형)으로의 sim2real 격차에서 이 값들이 유지될지 미검증 — 우리 System0 sim2real(친·동 마찰 분리 등) 셋업과 충돌 여부 확인 필요.

---

## 💡 컨텍스트 제안

- **P1 §5 base 후보 추가 고려** — CoorDex 를 [D1]/[D4] 의 "RL+모션 prior 도메인에서의 hybrid 분리" 비핀 methodology base 로 등재할지 검토(현 핀 4편은 모두 IL/VLA 계열이라, RL 측 대조군이 없음). 핀 교체가 아니라 base 행 추가 제안.
- **P3 §5 잔차 RL 대조군** — DexSynRefine 옆에 "latent-prior residual RL" 대비 항목으로 메모할 가치. 단 휴머노이드 전신 의존성 때문에 핀 승격은 비권장.
- 그 외 Decision/deferred trigger 이동 제안 없음.
