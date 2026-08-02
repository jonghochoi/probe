# Paper Analysis — Action with Visual Primitives

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | AVP: Action with Visual Primitives |
| 저자 | Weilong Guo, Yuchen Wang, Renping Zhou, Yunfeng Zhang, Rui Fang, Yuyang Pang, Wenda Xu, Gao Huang |
| 링크 | [arXiv:2605.22183](https://arxiv.org/abs/2605.22183) · [Website](https://kingdroper.github.io/AVP) |
| 발행일 / 버전 | 2026-05-21 · v3 (2026-06-13 최종 개정) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-08-02 |
| 관련 Pillar | P1, P4, P2 |
| 태그 | vla-arch, flow-matching |

<!-- 원문 제목의 H1/메타에는 콜론 코드네임이 없으나(제목이 "Action with Visual
     Primitives"), 저자가 초록·서론·기여 목록에서 "AVP (Action with Visual
     Primitives)" 로 약어를 명시적으로 정의하며 확장 initials(A-V-P)가 약어를
     그대로 철자하므로 alias = AVP (analysis.txt GIT 규칙 2번 경로). -->

---

## 🧭 한 줄 요약 (TL;DR)

VLM 과 액션 전문가(action expert) 사이의 암묵적 인터페이스를 **공간적으로 접지된(spatially grounded) "시각 프리미티브(visual primitive)" 토큰**이라는 명시적 통신 채널로 대체하여, VLM 은 "무엇을·어디서" 를 시각 공간에 표시하고 액션 전문가는 "어떻게 실행" 에만 집중하도록 책임을 분리한 end-to-end VLA 아키텍처입니다. 시각 프리미티브의 지도(supervision)는 외부 검출기 없이 **엔드이펙터 기구학(end-effector kinematics)** 에서 자동 유도되며, 실로봇 pick-and-place 에서 π0.5 대비 성공률을 크게 끌어올렸다고 주장합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 현행 VLA 는 언어 명령과 시각 관측을 단일 forward pass 로 액션에 매핑하여, 명령 이해·공간적 장면 이해·모터 제어를 하나의 학습 목표 안에 뒤섞습니다. 이 때문에 액션 전문가는 사전학습된 VLM 이 이미 갖춘 인지·지각 능력을 암묵적으로 재학습해야 합니다.
- **기존 접근의 한계** — 명시적 중간 표현을 도입하는 세 갈래 모두 결함이 있습니다. (i) π0.5 류 **계획 중심(planning-centric)** 은 서브태스크를 언어로 쪼개지만 인터페이스가 순수 언어라 미세한 공간 구분(밀집·유사 객체)을 전달하기 어렵습니다. (ii) π0.7·world-action 모델은 서브골 이미지/미래 프레임을 주지만, 조밀한 픽셀 예측은 "무엇이 정말 중요한지" 를 액션 전문가가 다시 발견해야 합니다. (iii) Point-VLA·VP-VLA·TraceVLA 류 **비주얼 프롬프트** 는 외부 모델에 의존해 다단계 파이프라인이 되어 지연·오류 전파를 유발합니다.
- **본 논문의 가설** — VLM 과 액션 전문가는 하나처럼 동작하되 학습 책임이 명확히 나뉘어야 하며, 그 경계는 **시각 프리미티브**(점·박스 등 시각 공간에 접지된 토큰)라는 명시적 매체로 통신하는 것이 가장 낫다는 가설입니다.
- **왜 지금 중요한가** — VLA 가 VLM 의 대규모 사전학습 공간 추론 능력을 아직 충분히 활용하지 못하는 상황에서, 외부 모듈 없이 그 능력을 정책 내부로 end-to-end 내재화하는 인터페이스 설계는 데이터 효율·일반화의 직접적 레버입니다.

---

## 🧩 핵심 기여

- VLM 과 액션 전문가의 **책임 분담을 재검토**하고, VLM 내부에서 생성되는 공간 접지 토큰 = 시각 프리미티브를, 현행 VLA 의 암묵적·비구조적 경계를 대체하는 **명시적 통신 매체**로 제안합니다.
- 이 아이디어를 end-to-end 로 구현한 **AVP** 아키텍처를 제시합니다: VLM 이 다음 단계 타깃을 추론하고 시각 프리미티브 토큰을 방출하여 **플로우 매칭(flow matching) 액션 전문가**를 조건화하며, 지도는 엔드이펙터 기구학에서 유도됩니다.
- **행동 중심 시각 프리미티브 지도(Action-Centric Visual-Primitive Supervision)** 파이프라인 — 그리퍼 상태 전이로 키프레임을 잡고, 3D EE 위치를 이미지 평면에 투영해 2D 공간 앵커로 이산화 — 를 통해 수작업 주석·외부 프롬프트 생성기 없이 지도 신호를 자동 구성합니다.
- 실로봇 pick-and-place(중국 장기·도미노·일반 물체) 실험에서 π0.5 대비 큰 성공률 향상과 공간-조합 일반화·객체 수준 전이 이득을 보고합니다.

---

## 🔑 기술 키워드

- **Visual Primitive** — 점·박스·마스크처럼 이미지 위에 그릴 수 있는 최소 공간 표식. 본 논문에서는 VLM 이 내부적으로 방출하여 액션 전문가에 "여기를 조작하라" 고 지시하는 명시적 통신 토큰의 역할을 합니다.
- **Action Expert** — VLM 뒤에 붙어 실제 로봇 액션을 생성하는 모듈. 본 논문은 여기서 공간 추론 부담을 떼어 내 "실행" 에만 집중시키는 것이 핵심입니다.
- **Flow Matching** — 노이즈에서 목표 분포로의 연속 변환을 학습하는 생성 기법. π0/π0.5 계열 액션 전문가의 표준 헤드로, AVP 액션 전문가도 이를 사용합니다.
- **Cascaded Visual Prompting** — 외부 지각 모듈이 먼저 프롬프트를 뽑고 그 위에 액션 정책을 얹는 2단계 파이프라인. AVP 가 지연·오류 전파를 이유로 극복하려는 대상입니다.
- **End-Effector Kinematics** — 로봇 팔 말단(그리퍼)의 3D 자세를 순방향 기구학으로 얻는 것. AVP 지도 라벨을 외부 주석 없이 자동 생성하는 근원입니다.
- **Perspective Projection** — 3D 점을 카메라 내부행렬 $`K`$ 와 외부변환 $`T_{R}^{C}`$ 로 2D 이미지 좌표에 사영하는 표준 투영. EE 위치를 시각 프리미티브 라벨로 바꾸는 기하 연산입니다.
- **Next-Stage Target** — VLM 이 현재 서브태스크를 파싱해 예측하는 "다음 단계에서 조작할 대상/위치". 시각 프리미티브가 표상하는 대상입니다.
- **Spatial-Compositional Generalization** — 학습 시 본 적 없는 공간 전이(예: 경유점 없는 직접 이동)를, 학습된 하위 동작을 재조합해 수행하는 능력. AVP 의 대표 일반화 주장입니다.
- **Autoregressive Decoder** — VLM 컨텍스트 토큰에서 이산화된 시각 프리미티브를 순차 예측하는 디코더($`D_{\psi}`$). 언어 공간의 예측을 시각 공간으로 옮기는 다리입니다.
- **Memory-Augmented Primitive** — 직전 서브태스크의 시각 프리미티브를 구별되는 형태로 이미지에 남겨 단계 간 공간 맥락을 잇는 변형. 최고 성능을 낸 ablation 설정입니다.

---

## 🔬 방법론

### 직관

AVP 의 출발점은 하나의 질문입니다 — VLM 과 액션 전문가 사이에 "무엇을·어디서 할지" 라는 판단을 어떤 형태로 흘려보낼 것인가? 기존 VLA 는 이 판단을 VLM 의 원시(raw) 특징 벡터에 암묵적으로 담아 액션 전문가에 넘깁니다. 그러면 액션 전문가는 매번 "이 특징 안 어디에 조작할 대상이 있는가" 를 스스로 다시 풀어야 하고, 결국 VLM 이 이미 아는 지각·공간 능력을 재학습하게 됩니다. 데이터가 많이 들고 장면이 조금만 바뀌어도 일반화가 무너지는 이유입니다.

AVP 의 해법은 이 경계를 **눈에 보이는 표식**으로 바꾸는 것입니다. VLM 이 "다음엔 여기를 조작하라" 를 이미지 위의 점·박스 같은 시각 프리미티브로 명시하면, 액션 전문가는 더 이상 대상을 찾을 필요 없이 표시된 곳으로 어떻게 움직일지에만 집중합니다. 언어 서브태스크(π0.5)처럼 추상적이지도, 미래 프레임(π0.7)처럼 조밀하지도 않은 — 딱 필요한 공간 정보만 담은 희소한 채널입니다.

문제는 이 시각 프리미티브의 정답 라벨을 어떻게 확보하느냐입니다. 외부 검출기·SAM·범용 VLM 으로 표식을 그리면 다시 다단계 파이프라인의 지연·오류로 돌아갑니다. AVP 는 이를 **로봇 자신의 기구학**으로 해결합니다 — 그리퍼가 열리고 닫히는 순간(파지·해제)이 곧 상호작용이 일어나는 곳이므로, 그 키프레임에서 EE 의 3D 위치를 카메라로 투영하면 "조작이 실제로 일어난 지점" 이 공짜로 라벨이 됩니다. 사람이 주석을 달 필요도, 외부 모델을 부를 필요도 없습니다.

전체는 세 부품 — 사전학습 VLM, 시각 프리미티브 디코더, 플로우 매칭 액션 전문가 — 을 하나의 end-to-end 모델로 묶고, 액션 손실과 프리미티브 예측 손실을 함께 최소화하도록 학습합니다. 추론 시에는 원시 관측·언어·로봇 상태만 있으면 되고, 시각 프리미티브는 내부에서 생성됩니다.

### 아키텍처

먼저 비교 기준이 되는 두 정식화를 짚습니다. 전형적 VLA 는 관측 $`o_{t}`$ · 언어 $`l`$ · proprioception $`s_{t}`$ 에서 액션 지평(horizon) $`h`$ 를 직접 매핑합니다.

> "Typical Vision-Language-Action (VLA) models characterize robotic manipulation as a direct mapping $`a_{t:t+h}=\pi_{\theta}(o_{t},l,s_{t})`$ to predict an action horizon $`h`$ ..." (§3.1)
(이 직접 매핑은 고수준 이해와 저수준 실행 사이에 오직 암묵적 인터페이스만 두기 때문에, 정책이 의미 이해와 액션 생성을 하나의 목표로 동시에 습득해야 한다는 점이 데이터 효율과 일반화를 떨어뜨린다는 것이 저자의 진단입니다.)

캐스케이드 비주얼 프롬프팅은 지각 모듈 $`\mathcal{M}_{per}`$ 이 프롬프트 $`v_{t}`$ 를 먼저 뽑아 관측에 합성한 뒤 하류 정책 $`\pi_{act}`$ 를 구동합니다 (식 1):

$$v_{t}=\mathcal{M}_{per}(o_{t},l),\quad\text{and}\quad a_{t:t+h}=\pi_{act}(\mathcal{F}(o_{t},v_{t}),l,s_{t}),$$

여기서 $`\mathcal{F}(\cdot)`$ 는 픽셀 오버레이/렌더링 같은 시각 합성 연산자입니다. 이 방식은 공간 위치 추정 부담은 덜지만, 비-end-to-end 구조라 추론 지연과 단계 간 오류 전파를 남깁니다.

AVP 는 이 인터페이스를 **단일 end-to-end 모델 내부로 내재화**합니다. 세 부품으로 구성됩니다.

- **VLM** — 명령 $`l`$ 과 관측 $`o_{t}`$ 에서 멀티모달 컨텍스트 토큰을 생성.
- **시각 프리미티브 디코더 $`D_{\psi}`$** — 그 컨텍스트에서 다음 단계 실행용 이산화 시각 프리미티브를 자기회귀적으로 예측 (식 2):

$$p_{t}=D_{\psi}(\mathrm{VLM}(o_{t},l)).$$

예측된 프리미티브 $`p_{t}`$ 는 다음 단계 서브태스크와 그 공간 타깃을 함께 인코딩하며, 이후 액션 예측의 명시적 조건이 됩니다.

- **투영 + 융합** — 프리미티브를 시각 토큰 공간으로 투영해 (식 3) 시각 프리미티브 토큰 $`z_{t}^{vp}`$ 를 얻고, 이를 원래 멀티모달 토큰과 융합해 증강 표현 $`z_{t}^{aug}`$ 를 만듭니다.

$$z_{t}^{vp}=\mathrm{Proj}(p_{t},o_{t}),$$

- **액션 전문가 $`\pi_{\theta}`$** — 증강 표현과 로봇 상태에서 액션 지평을 생성 (식 4):

$$a_{t:t+h}=\pi_{\theta}(z_{t}^{aug},s_{t}).$$

> "Through this design, the visual primitive acts as an explicit communication channel between the VLM and the action expert: the VLM predicts the task-relevant target in the visual space, while the action expert focuses on motion execution." (§3.2)
(설계의 핵심 문장입니다 — 시각 프리미티브가 "무엇을·어디서"(VLM)와 "어떻게"(액션 전문가)를 물리적으로 분리하는 채널이라는 것. 이 분리 덕에 액션 전문가는 대상 위치를 재학습하지 않고 실행 가능한 모션 패턴 학습에만 자원을 쓸 수 있습니다.)

아래는 프레임워크 개요도입니다.

![Figure 3 — AVP 프레임워크 개요](https://arxiv.org/html/2605.22183/figs/AVPv02.png)

> "Figure 3: Overview of the AVP framework. AVP uses visual primitives as an explicit interface between the VLM and the action expert. Given the instruction and multi-view observations, the model predicts the next-stage target and its associated visual primitive, which guides subsequent action generation." (§3.2)
(이 그림은 VLM → 시각 프리미티브 디코더 → 투영/융합 → 액션 전문가로 이어지는 조건화 흐름, 즉 §3.2 의 "명시적 통신 채널" 주장을 시각화합니다.)

시각 프리미티브 자체의 형태 다양성(점·박스·마스크 등)은 아래 그림이 예시합니다.

![Figure 1 — 시각 프리미티브 인터페이스 개관](https://arxiv.org/html/2605.22183/x1.png)

> "Figure 1: We present AVP, an end-to-end Vision-Language-Action architecture with a visual-primitive interface. The VLM infers the next-stage target and emits spatially grounded visual-primitive tokens, which condition a action expert to execute real-world robot manipulation tasks. Visual-primitive supervision is derived directly from end-effector kinematics, avoiding manual spatial annotation or external visual prompt generators." (§1)
(전체 파이프라인과 "지도가 EE 기구학에서 나온다" 는 차별점을 한 장에 요약한 티저 그림입니다.)

### 학습 목표 / 손실

시각 프리미티브 디코더는 합동 프리미티브 예측 손실로 지도됩니다 (식 5):

$$\mathcal{L}_{vp}=\mathcal{L}_{CE}\big(p_{t},y_{t}^{vp}\big),$$

여기서 $`y_{t}^{vp}`$ 는 엔드이펙터 기구학에서 유도한 정답 시각 프리미티브입니다. 액션 전문가는 표준 액션 예측 목표 $`\mathcal{L}_{act}`$ 로 학습되며, 전체 목표는 다음과 같습니다.

> "The action expert is trained with the standard action prediction objective $`\mathcal{L}_{act}`$ , and the overall training objective is $`\mathcal{L}=\mathcal{L}_{act}+\lambda\mathcal{L}_{vp}`$ , where $`\lambda`$ balances action learning and primitive supervision." (§3.2)
(액션 학습과 프리미티브 지도를 가중치 $`\lambda`$ 로 저울질하는 단일 합산 손실입니다. $`\mathcal{L}_{act}`$ 의 구체 형태(플로우 매칭 손실)는 π0.5 프레임워크를 그대로 따르며 본문에 별도 수식은 없습니다.)

**행동 중심 시각 프리미티브 지도 (Appendix B).** 라벨 $`y_{t}^{vp}`$ 는 세 단계로 구성됩니다.

- **키네마틱 키프레임 추출** — 그리퍼 상태 신호 $`g_{t}`$ (제어 명령과 실측 개구량의 불일치 등)의 급변으로 상호작용 키프레임을 잡습니다 (식 6):

$$T_{\mathrm{key}}=\{\,t\in[1,T]\mid|\Delta g_{t}|>\delta\,\},$$

$`\delta`$ 는 유의미한 그리퍼 상태 전이 검출 임계값이며, 키프레임은 파지 개시·해제 같은 물리적으로 의미 있는 이벤트에 해당합니다.

- **공간 자세 추정** — 각 키프레임 $`t\in T_{\mathrm{key}}`$ 에서 로봇 proprioception 으로부터 3D EE 위치를 얻습니다 (식 7):

$$P_{t}=[X_{t},Y_{t},Z_{t}]^{T}\in\mathbb{R}^{3}$$

- **프리미티브 투영** — 3D 점을 이미지 평면의 2D 앵커 $`m_{t}=(u_{t},v_{t})`$ 로 사영합니다. 내부행렬 $`K\in\mathbb{R}^{3\times 3}`$, 로봇 베이스→카메라 외부변환 $`T_{R}^{C}\in SE(3)`$ 에 대해 표준 투시 투영 (식 8):

```math
z_{c}\begin{bmatrix}u_{t}\\ v_{t}\\ 1\end{bmatrix}=KT_{R}^{C}\begin{bmatrix}P_{t}\\ 1\end{bmatrix},
```

$`z_{c}`$ 는 카메라 좌표계의 깊이 스케일 인자입니다. 투영된 $`(u_{t},v_{t})`$ 를 유한 공간 격자로 이산화해 디코더의 지도 타깃으로 삼습니다.

> "Primitive supervision is derived directly from end-effector kinematics, eliminating the need for manual spatial annotation or external visual prompt generators." (§3.3)
(이 파이프라인의 가치 제안 — 시각적으로 유사한 객체·가림·혼잡 장면에서 외부 지각 모델의 의미적 모호성을 피하고, 표준 실로봇 시연 이상의 주석 비용을 거의 들이지 않는다는 점입니다.)

### 학습 셋업

- **베이스라인/백본** — π0.5 프레임워크 위에 AVP 를 구축하고 π0.5 를 비교 기준으로 삼습니다.
- **로봇 임베디먼트** — AgileX Piper 탁상 플랫폼, 6-DoF 병렬 그리퍼 팔 2대로 구성된 dual-arm 시스템, 통합 14차원 액션 공간. 양팔 베이스 간격 54.4 cm. 각 팔 손목에 RealSense D435i, 상단에 Hikvision 카메라(작업대 기준 높이 66.5 cm). 전 카메라 동기 RGB `640×480` `30 fps`.
- **데이터** — 실세계 전문가 시연: 중국 장기 11.2 시간, 도미노 1.7 시간, 일반 물체 1.7 시간.
- **최적화** — AVP·π0.5 모두 배치 크기 64. 장기 정책 40k step, 도미노·일반 물체 정책 각 10k step.
- **2단계 학습 스케줄** — AVP 는 동일 총 step 내에서 (1) 시각 프리미티브 디코더를 프리미티브 지도로 먼저 최적화한 뒤 (2) 전체 모델을 합동 학습합니다. 장기 본실험 기준 `10k primitive + 30k joint`, 도미노/일반물체/ablation 은 `2.5k primitive + 7.5k joint`, 공간-조합 일반화는 총 50k(`12.5k primitive + 37.5k joint`) (Table 8).
- **추론 하드웨어** — 단일 NVIDIA RTX 3090 GPU 에서 실로봇 추론·지연 측정.

---

## 📊 실험 설정과 결과

세 실로봇 태스크(중국 장기·도미노·일반 물체 pick-and-place)에서 통일된 프로토콜로 평가합니다. 지표는 Instruction Following(올바른 매니퓰레이터 선택), Pick Success, Place Success, 평균, 지연(Latency). 도미노는 Instruction Following 대신 Orientation Success 를 씁니다.

**Experiment I — 중국 장기 조작 (Table 1, 72개 non-capture 이동).**

| Method | Instr. | Pick | Place | Avg. | Latency |
|---|---|---|---|---|---|
| π0 | 62.50 | 45.83 | 25.00 | 44.44 | 0.16 s |
| π0.5 | 75.00 | 63.89 | 20.83 | 53.24 | 0.16 s |
| Point-VLA | 65.28 | 47.22 | 31.94 | 48.15 | 37.32 s |
| DM0 | 73.61 | 40.28 | 22.22 | 45.37 | 0.52 s |
| LDA | 93.06 | 34.72 | 19.44 | 49.07 | 0.28 s |
| AVP | 98.61 | 90.28 | 81.94 | 90.28 | 0.27 s |

> "As shown in Table 1, AVP attains a 90.28% average success rate on the 72-instruction benchmark, an absolute gain of +37.04% over the strongest end-to-end baseline $`\pi_{0.5}`$ , with the largest improvement on placement (+61.11%)." (§4.2, Table 1)
(가장 극적인 결과입니다. 특히 π0.5 의 placement 가 20.83% 에 그친 반면 AVP 는 81.94% — 시각 프리미티브가 "대상 위치 찾기 + 액션 생성" 의 동시 학습 부담을 덜어 낸다는 주장의 핵심 증거입니다.)

> "In contrast, AVP runs at 0.27 s per step—over two orders of magnitude faster—while delivering the highest accuracy across all metrics." (§4.2, Table 1)
(캐스케이드 비주얼 프롬프트 베이스라인 Point-VLA(Kimi)는 48.15% 에 그치면서 step 당 37.32 s 로 실사용 불가 수준의 지연을 보이는데, AVP 는 내부화 덕에 이를 0.27 s 로 회피합니다. world-model 계열 DM0·LDA 는 π0 수준에 머물러, 픽셀 수준 미래 예측이 조밀한 공간 추론에 제한적 도움만 준다는 관찰로 이어집니다.)

**Experiment II — 도미노 배치 (Table 2, 48개 명령).** 성공 기준: 최종 위치 오차가 도미노 두께 1개 이내이고 목표 방향과의 각도 편차가 `10°` 미만.

| Method | Pick | Place | Orien. | Avg. |
|---|---|---|---|---|
| π0.5 | 87.50 | 64.58 | 93.75 | 81.94 |
| AVP | 100.00 | 64.58 | 100.00 | 88.19 |
| Imp. | +12.50 | 0.00 | +6.25 | +6.25 |

> "the proposed method improves both pick and orientation success rates over the $`\pi_{0.5}`$ baseline while maintaining comparable placement accuracy." (§4.2, Table 2)
(Place 는 동률(64.58%)이라 이득이 pick·orientation 에 집중됩니다. 저자는 π0.5 가 반복 파지·파지 실패를 자주 보인 반면 AVP 는 더 안정적 실행을 달성했다고 해설합니다.)

**Experiment III — 일반 물체 pick-and-place (Table 3).**

| Method | Instr. | Pick | Place | Avg. |
|---|---|---|---|---|
| π0.5 | 100.00 | 71.79 | 23.08 | 64.96 |
| AVP | 100.00 | 90.24 | 68.29 | 86.18 |
| Imp. | 0.00 | +18.45 | +45.21 | +21.22 |

> "AVP substantially improves both grasping and placement success rates over the $`\pi_{0.5}`$ baseline while maintaining perfect correct-manipulator accuracy." (§4.2, Table 3)
(여기서도 placement 이득(+45.21%p)이 가장 큽니다 — 세 태스크 공통으로 "어디에 놓을지" 의 공간 접지가 시각 프리미티브의 최대 수혜 지점임을 시사합니다.)

**일반화·Ablation (§4.3, 모두 중국 장기에서).**

*공간-조합 일반화 (Table 4a, 50개 unseen direct 명령).* 학습은 경유점을 거치는 Indirect($`A\rightarrow C\rightarrow B`$)만, 평가는 직접 전이($`A\rightarrow B`$)로.

| Method | Instr. | Pick | Place | Avg. |
|---|---|---|---|---|
| π0.5 | 58.00 | 4.00 | 0.00 | 20.67 |
| AVP | 100.00 | 90.00 | 60.00 | 83.33 |
| Imp. | +42.00 | +86.00 | +60.00 | +62.66 |

> "the $`\pi_{0.5}`$ baseline exhibits poor execution accuracy, often resulting in arm selection confusion or drifted trajectories that trigger early resets. In contrast, AVP achieves strong spatial-compositional generalization ..." (§4.3, Table 4(a))
(경유점이 사라진 unseen 직접 전이에서 π0.5 의 Place 가 0.00% 로 붕괴하는 반면 AVP 는 60% 를 유지 — 시각 프리미티브가 "어디서 실행할지" 를 명시하여 학습된 모션의 재사용을 가능하게 한다는 가장 강한 일반화 증거입니다.)

*교차 도메인 일반화 (Table 4b, 8개 unseen 물체, 배경 2종 × 실행 2종, 성공 개수/8).*

| Background | Task | π0.5 | AVP |
|---|---|---|---|
| Chessboard | Direct | 0/8 | 8/8 |
| Chessboard | Indirect | 7/8 | 8/8 |
| White cloth | Direct | 0/8 | 7/8 |
| White cloth | Indirect | 0/8 | 8/8 |

> "the $`\pi_{0.5}`$ baseline degrades substantially under distribution shifts, particularly in the 'Direct' setting." (§4.3, Table 4(b))
(장기 데이터만으로 학습한 정책의 zero-shot 물체 전이입니다. π0.5 는 Chessboard+Indirect(7/8)에서만 버티고 나머지에서 0/8 로 무너지는데, 저자는 이를 단순 명령-궤적 암기의 흔적으로 봅니다. AVP 는 4개 조건 모두 7~8/8.)

*시각 프리미티브 ablation (Table 5, 프롬프트 설계별).*

| Prompt | Instr. | Pick | Place | Avg. |
|---|---|---|---|---|
| None | 100 | 70 | 64 | 78 |
| Box | 100 | 82 | 68 | 83 |
| Box + Mask | 100 | 86 | 70 | 85 |
| Box + Mask + Mem. | 100 | 94 | 78 | 91 |

각 행이 고립하는 것 — None: 프리미티브 없는 원시 baseline(78). Box: 박스 공간 강조 추가(+5). Box+Mask: 배경 마스킹으로 무관 시각 맥락 억제(+2 추가). Box+Mask+Mem.: 직전 단계 프리미티브를 이미지에 남겨 단계 간 공간 맥락 제공 → 최고(91). 시각 프리미티브가 단계 간 공간 맥락을 자연스럽게 실을 수 있음을 시사합니다.

*추가 ablation (Appendix A.3, 25,282.7 s 데이터·10k step·50 명령).* 프리미티브 유형 — Raw(Pick 70/Place 64) < Box(82/68) ≈ Box-mask(86/70), **Point(86/74)** 가 강함(Table 6). 마스크 불투명도 — $`\alpha=0`$(82/68) → $`\alpha=0.7`$(86/70) → $`\alpha=0.9`$(86/74), 주로 placement 에 영향(Table 7).

> "our method improves the overall manipulation success rate by 37.04% over the $`\pi_{0.5}`$ baseline." (§1)
(주의 — 초록·서론은 "37.04% overall" 을 말하지만 이는 중국 장기 단일 태스크의 평균 이득(90.28−53.24)입니다. 결론(§5)은 "an overall success-rate gain of 27.61%" 로 다른 수치를 제시하며, 본문에 두 수치의 산출식이 명시되지 않아 내부 불일치로 남습니다 — ⚖️ 한계 참조.)

---

## ⚖️ 한계

- **순차 2단계 추론 지연 (저자 명시)** — 프리미티브 예측 후 액션 생성이라는 순차 구조가 single-pass 정책 대비 런타임 지연을 더합니다. AVP 의 0.27 s 는 캐스케이드(37.32 s)보다는 압도적으로 빠르지만 π0.5(0.16 s)보다는 느립니다. 메커니즘상 디코더의 자기회귀 예측이 임계 경로에 들어가므로, 프리미티브 길이가 길어질수록 지연이 누적됩니다.
- **하드-아이 캘리브레이션 의존 (저자 명시)** — 지도 파이프라인이 정밀한 $`K`$ · $`T_{R}^{C}`$ 에 의존해 카메라 외부변수 드리프트·물리적 교란에 민감합니다. 라벨 자체가 투영(식 8)으로 만들어지므로 캘리브레이션 오차는 학습 신호를 직접 오염시킵니다 — 이는 "외부 주석 불필요" 라는 장점의 이면입니다.
- **보고 수치의 내부 불일치 (추론된 갭)** — 초록·서론의 "37.04% overall" 과 결론의 "27.61% overall" 이 충돌하며 둘 다 산출식이 없습니다. 37.04 는 장기 태스크 평균 이득에 정확히 일치하나 27.61 의 근거는 불명확합니다. 헤드라인 지표의 정의가 흔들린다는 점은 재현·비교 시 주의가 필요합니다.
- **태스크 범위가 병렬 그리퍼 pick-and-place 에 국한 (추론된 갭)** — 세 태스크 모두 14차원 dual-arm 병렬 그리퍼이며 조작은 본질적으로 "집어서 특정 지점에 놓기" 입니다. 시각 프리미티브가 표상하는 "다음 단계 타깃" 은 이미지 평면의 2D 앵커(점/박스)로 충분한 태스크군입니다. 접촉 구성 자체가 목표가 되는 과제(도구 조작·인핸드 재배향)로의 확장 여부는 검증되지 않았습니다.
- **VLM 공간 접지 능력에 대한 상한 의존 (추론된 갭)** — "복잡 공간 추론을 VLM 으로 offload" 한다는 설계는 VLM 이 실제로 그 공간 접지를 방출할 수 있을 때만 성립합니다. 프리미티브 라벨이 이산 격자로 quantize 되므로 격자 해상도가 미세 조작 정밀도의 상한을 정하는데, 격자 크기·해상도가 본문에 명시되지 않았습니다.
- **world-model 계열 비교의 공정성 (추론된 갭)** — DM0·LDA 가 "수렴까지 50k step" 을 요한다고만 밝히고(Table 8) π0.5 는 40k 로 고정되어, "동일 조건" 비교가 step 수 측면에서 완전히 대칭은 아닙니다. 저자도 이를 명시하나 결과 해석에는 여전히 변수로 남습니다.

---

## ♻️ 재현성

- **코드/모델** — 프로젝트 페이지(<https://kingdroper.github.io/AVP>)만 제공되며, arXiv HTML·프로젝트 페이지 어디에도 공개 코드 저장소·가중치 링크가 확인되지 않습니다 (본 분석 시점).
- **데이터** — 실세계 전문가 시연(장기 11.2h·도미노 1.7h·일반물체 1.7h)은 자체 수집이며 공개 여부 미명시.
- **하드웨어** — AgileX Piper dual-arm(6-DoF×2, 병렬 그리퍼, 14-dim), RealSense D435i 손목 카메라 + Hikvision 상단 카메라(`640×480`,`30 fps`), 추론 RTX 3090 — 상용 부품이라 재현 문턱은 상대적으로 낮으나 정밀 캘리브레이션이 관건.
- **방법 재현성** — 손실·2단계 스케줄·기구학 지도 파이프라인은 수식·절차 수준으로 상세하나, $`\lambda`$ 값, 이산화 격자 해상도, 그리퍼 임계값 $`\delta`$, 프리미티브 디코더 세부 구조는 미명시라 정확 재현에는 가정이 필요합니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P1**(Heterogeneous Body/Hand Action Expert) — AVP 의 중심 질문은 "VLM 과 액션 전문가 사이 책임을 어떻게 분할하는가" 로, P1 의 아키텍처 코어와 직결됩니다. `D6`(coordination direction & flow — 본 stack v1 은 body→hand 계층 흐름)에 대한 강한 유비 증거입니다: AVP 는 VLM→액션 전문가의 **계층적 흐름**을 언어가 아닌 시각 프리미티브로 흘려보내 조합 일반화를 크게 개선합니다. 또한 `D7`(π backbone integration/partition — v1 은 π0 액션 전문가 슬라이스 + 양측 FT)의 직접 사례로, π0.5 백본을 슬라이스하고 그 위에 디코더+액션 전문가를 얹습니다. 조건화 지점은 `D4`(Body↔Hand information sharing — v1 은 FiLM 단일 지점)의 대안 채널(토큰 융합 $`z_{t}^{aug}`$)로 읽힙니다.
- **P4**(Pretraining for Data-Efficient Adaptation) — 논문의 최상위 동기("액션 전문가가 VLM 이 이미 가진 지각 능력을 재학습해야 해 데이터 효율·일반화가 나빠진다")는 `D20`(prior-preservation strategy — v1 은 action-side adapter + conservative SFT, 백본 보존)과 정확히 같은 문제의식입니다. 시각 프리미티브는 VLM 사전학습 능력을 정책이 소비하도록 강제하는 인터페이스로, 데이터 효율 이득을 명시적으로 주장합니다. `D23`(action representation × pretraining — v1 은 연속 flow-matching head)과도 일치(플로우 매칭 액션 전문가). π0.5 위 구축이므로 `D19`(lineage = PaliGemma × π mix, freeze 우선) 계열.
- **P2**(Structured Multimodal Observation Fusion) — 시각 프리미티브 토큰은 관측을 공간적으로 접지된 명시적 중간 표현으로 "격상" 시켜 멀티모달 토큰과 융합($`z_{t}^{aug}`$)합니다. `D8`(multi-camera spatial-geometric grounding)의 정신(공간 정보 보존·등록)과 `D10`(fusion beyond concat — cross-attention/비평면 융합)에 맞닿으나, AVP 의 접지는 VGGT식 다시점 3D 기하가 아니라 EE 투영 앵커라는 점에서 결이 다릅니다.
- **Identity 긴장/지지** — PROBE Identity 는 "dexterity 를 VLA-level 에서 직접 tackle" 을 주장합니다. AVP 는 **VLA-level 인터페이스 설계**라는 점에서 Identity 를 지지하나, dexterous **hand** 가 아닌 병렬 그리퍼 pick-and-place 라 손 수준 접촉 정교화(차별화 주장)와는 층위가 다릅니다 — 보완적 증거이지 경쟁 주장이 아닙니다.
- **경쟁자 함의** — P1/P4 의 핀 π0.5 를 직접 baseline 으로 삼아 넘어선 2026 아키텍처로, 핀 논문 대비 인터페이스 축의 신규 경쟁 포인트를 만듭니다.

---

## ✨ 핀 논문 대비 델타

- **π0.5 대비** (P1 §5 methodology base · P4 §5 pinned) — π0.5 는 명령을 **언어 서브태스크**로 분해하는 planning-centric 인터페이스입니다. AVP 는 그 인터페이스를 **시각 프리미티브**(공간 접지 토큰)로 교체하여, 언어가 전달하기 어려운 미세 공간 구분(밀집·유사 객체)을 직접 표시합니다. 진정한 신규성은 "고수준↔저수준 경계의 매체를 언어→시각으로 바꾼 것" 과, 그 시각 라벨을 **외부 모델 없이 EE 기구학에서 자동 생성**하는 지도 파이프라인입니다.
- **π0 대비** (P1 §5 pinned) — π0 는 직접 매핑($`a=\pi_\theta(o,l,s)`$)에 가깝습니다. AVP 는 명시적 시각 인터페이스를 삽입해 액션 전문가의 공간 추론 부담을 제거합니다.
- **캐스케이드 비주얼 프롬프트(Point-VLA 등) 대비** — 이들은 외부 지각 모델로 프롬프트를 뽑는 2단계라 지연·오류 전파가 있습니다. AVP 는 이를 단일 end-to-end 모델 내부로 내재화하여 두 자릿수 배 빠른 추론을 달성합니다(0.27 s vs 37.32 s).
- **π0.7·world-action 모델 대비** — 이들은 서브골 이미지/미래 프레임(조밀 픽셀)을 줍니다. AVP 는 "무엇이 중요한지" 를 이미 골라 놓은 **희소** 공간 프리미티브를 주어, 액션 전문가가 관련 대상을 재발견할 필요를 없앤다고 주장합니다.

---

## ⚙️ 의사결정 함의

- **인터페이스 채널 추가 후보** — 우리 stack 의 VLM↔Body/Hand 전문가 경계(`D4`/`D6`/`D7`)에 raw VLM 특징 외에 **명시적 시각-프리미티브 조건 토큰**을 더하는 설계가 후보로 올라옵니다. 특히 Body 전문가(macro 접근·배치)의 "어디에" 신호로 EE-투영 앵커가 적합할 수 있습니다.
- **새 손실항 + 하이퍼파라미터** — 액션 손실에 `L_vp = L_CE(p_t, y_t^vp)` 크로스엔트로피 보조항을 붙이고 가중치 $`\lambda`$ 를 도입. 값은 원문 미명시 → 우리 쪽에서 스윕 필요.
- **2단계 학습 스케줄** — "프리미티브 디코더 먼저, 이후 합동" 스케줄(예: 25%:75% step 비율)을 채택 후보로. 우리 conservative SFT(`D20`/`D21` Stage 3)와 순서 상호작용 검토.
- **저비용 공간 보조 지도** — 그리퍼 상태 전이($`|\Delta g_t|>\delta`$) 기반 키프레임 → 3D EE → 이미지 투영 → 격자 이산화 파이프라인은 수작업 주석 0 으로 공간 접지 보조 신호를 만듭니다. 우리 실로봇 시연 로그(proprioception + 캘리브레이션)만 있으면 재사용 가능한 메트릭/loss term 후보입니다.
- **평가 지표 채택** — placement 성공률과 **공간-조합 일반화**(unseen direct 전이) 를 별도 지표로 분리 측정하면, 인터페이스 개선의 효과를 pick 과 분리해 관찰할 수 있습니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 확인) 2D 앵커가 손 수준 의도를 담을 수 있는가** — AVP 의 프리미티브는 EE 의 이미지 평면 단일 점/박스입니다. 우리의 차별화 대상인 인핸드 재배향·도구 조작에서 "다음 단계 타깃" 은 단일 공간 위치가 아니라 **접촉 구성**(다지 접촉점·파지 자세)입니다. 먼저 종이 위 사고실험/소규모 라벨로 "우리 대표 태스크에서 2D EE 앵커가 태스크를 유일하게 규정하는가" 를 확인해야 합니다. 규정하지 못하면 인터페이스가 손가락 수준 의도를 못 전달합니다.
- **그리퍼 키프레임 정의의 붕괴** — 키프레임 추출이 이진에 가까운 그리퍼 개구량 급변($`\Delta g_t`$)에 의존합니다. 22-DOF Sharpa/xhand 같은 다지 손은 단일 "개구량" 이 없어 $`T_{\mathrm{key}}`$ 정의가 애매해집니다. 우리 손 데이터에서 어떤 신호가 "상호작용 키프레임" 대용이 될지 미리 정해야 합니다.
- **캘리브레이션 민감도 × 손목 카메라** — 라벨이 투영(식 8)으로 생성되므로 $`T_{R}^{C}`$ 드리프트가 학습 신호를 직접 오염시킵니다. 우리는 손목 이동 카메라 + 다시점 구성이라 외부변수 변동이 AVP 원 셋업보다 큽니다. 캘리브레이션 오차 대 프리미티브 라벨 오차의 민감도 곡선을 먼저 재야 합니다.
- **2단계 지연 vs System0 요구** — 순차 프리미티브→액션 지연은 우리 P3 System0 의 서브-정책-루프 반응 속도 요구와 상충할 수 있습니다. 접촉 유지 임계 구간에서 프리미티브 디코딩 지연이 허용 한계를 넘는지 확인 필요.
- **VLM lineage 의존** — offload 는 VLM 이 공간 접지를 실제로 방출할 때만 유효합니다. 우리 v1 lineage(PaliGemma×π mix, 백본 freeze)가 AVP 가 가정한 공간 추론 수준을 갖는지, freeze 상태에서 프리미티브 디코더만으로 접지가 학습되는지 소규모 검증이 선행되어야 합니다.
- **placement 편중 이득의 전이성** — 이득 대부분이 "어디에 놓을지" 의 평면 배치에서 나옵니다. 접촉이 지배하는 우리 dexterous 과제에서는 성공을 가르는 병목이 placement 정확도가 아닐 수 있어, 이득의 크기가 그대로 옮겨오지 않을 위험이 있습니다.

---

## 💡 컨텍스트 제안

- **P1 §5 methodology base 추가 후보** — AVP(arXiv:2605.22183)를 "VLM↔action-expert 인터페이스/조합 일반화" 증거로 P1 methodology base(non-pinned)에 추가 제안. `D6`(coordination direction & flow)에 대해 "언어가 아닌 **시각** 계층 인터페이스가 조합 일반화를 개선한다" 는 새 축의 증거로 태깅.
- **P4 방향 메모** — "액션 전문가가 VLM 지각 능력을 재학습하지 않도록 인터페이스를 명시화" 는 `D20`(prior-preservation) 을 백본 freeze/adapter 뿐 아니라 **인터페이스 표현 설계**로도 볼 수 있음을 시사. 핀 교체까지는 아니고 D20 논의에 각주로 반영 제안.
- **경쟁자 트래킹** — π0.5 를 직접 baseline 으로 넘어선 2026 아키텍처이므로, P1/P4 의 π0.5 핀 옆에 "인터페이스 축 경쟁자" 로 기록 권장.
- 그 외 Decision 이동/deferred trigger 변경 제안: 없음. (context/ 파일은 수정하지 않았습니다.)

---

> 💡 base 매핑은 `/implement-design analysis/2605.22183/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
