# Paper Analysis — Dexora: Open-source VLA for High-DoF Bimanual Dexterity

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Dexora: Open-source VLA for High-DoF Bimanual Dexterity |
| 저자 | Zongzheng Zhang, Jingrui Pang (공동 1저자), Zhuo Yang, Kun Li, Minwen Liao, Saining Zhang, Guoxuan Chi, Jinbang Guo, Huan-ang Gao, Modi Shi, Dongyun Ge, Yao Mu, Jiayuan Gu, Rui Chen, Hao Dong, Huazhe Xu, Li Yi, Yixin Zhu, Hang Zhao, Pengwei Wang, Shanghang Zhang, Guocai Yao, Jianyu Chen, Hongyang Li, Hao Zhao (교신) — Tsinghua University / BAAI / HKU / SJTU / ShanghaiTech / Peking University |
| 링크 | [arXiv:2605.18722](https://arxiv.org/abs/2605.18722) · [GitHub](https://github.com/ZZongzheng0918/Dexora) · [HuggingFace](https://huggingface.co/datasets/Dexora/Dexora_Real-World_Dataset) |
| 발행일 / 버전 | 2026-05-18 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-05-29 |
| 관련 Pillar | P1, P2, P3 |
| 태그 | vla-arch, dexterity |

---

## 🧭 한 줄 요약 (TL;DR)

양팔·양손 36-DoF 다지(dexterous) 조작을 한 모델로 다루는 최초의 오픈소스 VLA로,
하이브리드 텔레오퍼레이션(팔=외골격, 손가락=Apple Vision Pro)으로 대규모 시뮬레이션
+ 실세계 데이터를 수집하고 노이즈 섞인 시연을 데이터 품질 판별기(discriminator)
가 클립 단위로 가중하는 디퓨전-트랜스포머 정책으로 학습시켜 기존 VLA 대비 다지
조작 성공률을 끌어올립니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 기존 VLA는 양팔 저-DoF 그리퍼이거나 단팔 다지 손이거나
  둘 중 하나에 묶여 있어 양팔 협응과 고차원 손가락 정밀도를 동시에 요구하는
  작업(피스톤 삽입, 병 따기, 빽빽한 책장에서 책 꺼내기)을 다루지 못합니다.
- **기존 접근의 한계** — 저차원 그리퍼 제어는 단순한 방법으로도 되지만 고차원
  다지 손 제어는 종단간(end-to-end) VLA 학습의 이득이 큽니다. 양팔·양손을 함께
  다루는 오픈소스 스택 자체도 부재했습니다.
- **본 논문의 가설** — 풍부한 고-DoF 행동 공간에서 학습한 정책은 저-DoF 임베디먼트를
  부분공간으로 포함하므로, "고차원에서 학습 → 저차원으로 사영"이 그 역(저→고 리프팅)
  보다 잘 정의된(well-posed) 경로라는 가설입니다.
- **데이터 품질 문제** — 텔레오퍼레이션 시연은 조작자 숙련도·센싱 노이즈·가림·지연
  때문에 품질 편차가 크고 무제한으로 학습하면 정책 학습이 오히려 저하됩니다.
- **왜 지금 중요한가** — VLA가 임베디드 AI의 중심 방향이 된 시점에, 다지 양팔이라는
  최고 난도 사분면을 커버하면서 하위 임베디먼트로 내려갈 수 있는 "보편 컨트롤러"의
  실현 가능성을 데이터·레시피·오픈소스로 함께 제시합니다.

---

## 🧩 핵심 기여

- 양팔·양손·고-DoF(36-DoF) 다지 조작을 네이티브로 겨냥한 최초의 오픈소스 VLA
  시스템 Dexora 를 제시합니다.
- 거시 팔 운동(외골격 백팩)과 미세 손가락 운동(Apple Vision Pro 마커리스 추적)을
  분리(decouple)하는 하이브리드 텔레오퍼레이션 파이프라인으로, 실물 로봇과
  동일한 MuJoCo 디지털 트윈을 함께 구동합니다.
- 임베디먼트 정합(embodiment-matched) 대규모 코퍼스 — 시뮬레이션 10만 궤적
  (6.5M 프레임)과 실세계 1만 에피소드(2.92M 프레임) — 를 구축합니다.
- 노이즈 시연 완화를 위한 데이터 품질 인지 학습 레시피: 오프라인 판별기가
  클립 단위 가중치를 산출해 디퓨전-트랜스포머 정책 학습에서 저품질 시연을
  하향 가중합니다.
- 다지 평균 성공률 66.7%(GR00T N1 51.7% 대비) 등 기본·다지 벤치마크에서 경쟁
  VLA 베이스라인을 능가하고 OOD·크로스 임베디먼트 일반화를 입증합니다.

---

## 🔑 기술 키워드

- **VLA (Vision-Language-Action)** — 시각·언어 입력을 받아 로봇 행동을 출력하는 정책.
  본 논문에서는 디퓨전-트랜스포머가 그 본체입니다.
- **High-DoF bimanual dexterity** — 양팔(各 6-DoF) + 양손(各 12-DoF) = 36-DoF 행동
  공간. 본 논문의 차별점이 되는 임베디먼트 규모입니다.
- **Hybrid teleoperation** — 정밀한 팔 관절각은 외골격으로, 편리한 손가락 추적은
  Vision Pro로 얻는 "역할 분담형" 원격 조작. 데이터 수집 확장성의 핵심입니다.
- **Digital twin (MuJoCo)** — 실물과 동일 기구학을 갖는 시뮬레이션 쌍둥이. 동일
  텔레오퍼레이션 드라이버로 실/시뮬을 오가며 데이터를 모읍니다.
- **DexMimicGen** — 소수 시드 시연을 초기 상태 랜덤화 + 리타게팅으로 증식해 작업당
  대량 궤적을 합성하는 데이터 엔진. 시뮬 코퍼스 생성에 사용됩니다.
- **Data-quality-aware training** — 시연 품질을 점수화해 손실에 가중을 거는 학습.
  텔레오퍼레이션 노이즈를 다루는 본 논문의 레시피 이름입니다.
- **Discriminator (PU learning)** — 고품질 양성 집합과 미분류 풀(Positive–Unlabeled)
  로 학습해 클립의 품질 점수 $`d(C_{k})\in(0,1]`$ 를 내는 판별기.
- **log-π proxy** — 사전학습된 디퓨전 정책이 해당 클립을 얼마나 잘 설명하는지를
  디노이징 잔차 에너지로 근사한 "정책 적합성" 대리 지표.
- **DWBC (Discriminator-Weighted Behavior Cloning)** — 판별기 점수를 행동 복제
  손실 가중치로 변환하는 기법. 가중치 매핑을 이 방식에서 차용합니다.
- **Cross-embodiment generalization** — 36-DoF로 학습한 정책을 단팔 그리퍼·양팔
  그리퍼·단팔 저-DoF 손 등 다른 로봇으로 전이하는 능력.

---

## 🔬 방법론

### 직관

핵심 직관은 두 갈래입니다. 고-DoF 다지 데이터는 종단간 VLA로 학습할 때
이득이 가장 크고, 양팔·양손을 함께 다루려면 그에 맞는 임베디먼트 정합 데이터가
필수입니다. 다른 한 축은 데이터 품질입니다. 텔레오퍼레이션 데이터는 본질적으로
노이즈가 섞여 있어 모두 동등하게 학습하면 정책이 저하되므로 품질을 명시적으로
가중해야 한다는 점입니다.

> "While low-dimensional gripper control can often be handled with simpler methods, high-dimensional dexterous hand control benefits greatly from full end-to-end VLA learning." (§Abstract)
(고차원 다지 손 제어일수록 종단간 VLA 학습의 이득이 크다는, 본 논문이 고-DoF를
정조준하는 근거 문장입니다.)

> "Training on such heterogeneous data without constraints often degrades policy learning." (§III-C)
(이질적 품질의 데이터를 제약 없이 학습하면 정책이 오히려 나빠진다 — 품질 인지
레시피의 출발점입니다.)

### 아키텍처

입력/출력과 모듈 구성을 정리하면 이렇습니다.

- **하드웨어/임베디먼트** — 6-DoF AIRBOT 팔 2대 + 12관절 완전 구동 XHAND 손 2개
  (엄지·검지는 측면 외전/내전 추가 지원), 총 36-DoF. 4개 RGB 뷰 + 36-DoF 관절 상태를
  20Hz로 로깅합니다.
- **텔레오퍼레이션** — 팔: 외골격 백팩이 어깨-팔꿈치-손목 각도를 로봇 관절 공간으로
  직접 매핑(IK 지터·특이점 회피). 손가락: Vision Pro의 마커리스 3D 손 골격을 짧은
  캘리브레이션으로 XHAND에 리타게팅(관절 한계·안전 제약 적용).
- **정책 본체(Diffusion Transformer)** — 디코더 전용 트랜스포머를 디퓨전 모델로
  사용합니다. 현재 관절각 상태 $`s_{t}`$ 와 노이즈 행동 $`\widetilde{\mathbf{a}}_{t:t+L-1}`$
  을 잠재 공간으로 투영하고 디퓨전 타임스텝 $`t`$ 와 결합해 토큰을 구성합니다.

> "We employ a decoder-only Transformer as the diffusion model for the policy." (§III-C)
(VLM 백본을 액션 토큰 예측에 쓰지 않고 디코더 전용 트랜스포머가 디퓨전 정책의
본체라는 설계 선언입니다.)

> "Natural language and multi-view image inputs are encoded into conditional tokens via the T5 and SigLip encoders, respectively, and alternately injected into the transformer blocks." (§III-C)
(언어는 T5, 다중 뷰 이미지는 SigLip 인코더로 조건 토큰화해 트랜스포머 블록에
교대 주입합니다 — 사전학습 VLM 백본 보존형 구조가 아니라 인코더-조건형
디퓨전 정책입니다.)

정책의 조건부 생성은 다음과 같이 표기됩니다.

$$\pi_{\theta}(s_{t},\ \mathbf{o}_{t},\ \ell)=\widehat{\mathbf{a}}_{t:t+L-1}.$$

여기서 $`\mathbf{o}_{t}`$ 는 다중 뷰 RGB 관측, $`\ell`$ 은 언어 지시,
$`\widehat{\mathbf{a}}_{t:t+L-1}`$ 은 길이 $`L`$ 의 예측 행동 청크입니다. 학습 시
샘플링은 표준 DDPM, 행동 생성 가속에는 DPMSolver++ 를 씁니다.

![Figure 5 — Dexora framework](https://arxiv.org/html/2605.18722/x5.png)

> "Figure 5: Dexora framework. (a) Data filtering: From the real-world dataset we pre-screen demonstrations by kinematic smoothness (low acceleration and jerk), then replay them for post-validation and keep the clips that complete the task without collisions, forming a high-quality subset. (b) Discriminator training: With the pretrained diffusion–transformer policy frozen, we compute a log-π proxy for each clip and train a discriminator that, conditioned on observations and language, outputs a quality score $`d(C_{t})\in(0,1]`$ . (c) Data-quality-aware post-training: During post-training, the score $`d(C_{t})`$ is converted to weights $`w_{i}`$ and used in the diffusion loss $`\mathcal{L}_{\pi}`$ . At inference time, only the policy is used." (§III-C)
(프레임워크 전경 — (a) 운동학적 평활도 사전선별 + 리플레이 후검증으로 고품질
부분집합 구성, (b) 정책을 동결한 채 판별기 학습, (c) 점수를 가중치로 변환해 디퓨전
손실에 반영. 추론 시에는 정책만 사용한다는 핵심 파이프라인을 시각화합니다.)

### 학습 목표 / 손실

**1) 데이터 품질 기준 (에피소드 단위).** 에피소드 $`\tau=\{s_{t}\}_{t=1}^{T}`$ 에서
$`s_{t}\in\mathbb{R}^{D}`$ 는 자기수용(proprioceptive) 상태 벡터이며 $`D=36`$ 입니다.
차원별 min–max 정규화 후 중심 유한차분으로 속도·가속도·저크를 계산합니다.

$$v_{t}=\frac{s_{t+1}-s_{t-1}}{2\Delta t},\quad a_{t}=\frac{v_{t+1}-v_{t-1}}{2\Delta t},\quad j_{t}=\frac{a_{t+1}-a_{t-1}}{2\Delta t},\quad$$

에피소드 가속도·저크는 시간·차원에 걸친 RMS로 정의합니다.

$$A_{\text{ep}}(\tau)=\sqrt{\frac{1}{(T-6)D}\sum_{t=4}^{T-3}\sum_{k=1}^{D}a_{t,k}^{2}},$$

$$J_{\text{ep}}(\tau)=\sqrt{\frac{1}{(T-6)D}\sum_{t=4}^{T-3}\sum_{k=1}^{D}j_{t,k}^{2}}.$$

> "We rank episodes by $`A_{\text{ep}}`$ and by $`J_{\text{ep}}`$ separately, keep the lowest $`20\%`$ in each list, and take their intersection" (§III-C)
(가속도·저크 각각 하위 20%의 교집합을 취해 약 18% 에피소드를 1차 통과시키고
그중 충돌 없는 리플레이 성공만 양성으로 지정해 약 15%의 고품질 시연
$`\mathcal{S}_{\text{high}}`$ 를 얻습니다. 청크가 아니라 에피소드 단위로 채점하는
이유는, 정지 구간이 가속도·저크가 낮아도 무의미할 수 있기 때문입니다.)

**2) log-π 대리 지표.** 각 에피소드에서 $`K`$ 개 서브클립을 균일 샘플링하고
사전학습 디퓨전 정책 $`\pi_{\theta}`$ 의 음의 디노이징 잔차 에너지로
$`\log\pi`$ 를 근사합니다.

> "Given a pretrained diffusion-transformer policy $`\pi_{\theta}`$ , we define a surrogate for $`\log\pi(\mathbf{a}_{t:t+L-1}\mid\ell,\mathbf{o}_{t})`$ via the negative denoising residual energy:" (§III-C)
(정책이 해당 청크를 얼마나 잘 설명하는지를 잔차 에너지로 측정합니다 — 클수록
설명력이 좋다는 뜻입니다.)

$$E_{t}=\frac{1}{|\mathcal{S}|\,L}\sum_{s\in\mathcal{S}}\sum_{\tau=t}^{t+L-1}\left\|\varepsilon_{\theta}\!\left(\mathbf{o}_{\tau},\,\ell,\,\mathbf{a}_{\tau:\tau+L-1},\,s_{\tau}\right)-\varepsilon\right\|_{2}^{2},$$

$$\widehat{\log\pi}_{t}=-\,\mathrm{zscore}\!\left(E_{t}\right)=-\frac{E_{t}-\text{Mean}(E)}{\sqrt{\text{Var}(E)+\varepsilon}},$$

여기서 $`\mathcal{S}`$ 는 소수의 디퓨전 스텝 집합입니다. 클립 토큰
$`\xi_{t}=\big(s_{t},\ \mathbf{o}_{t},\ \ell,\ \mathbf{a}_{t:t+L-1},\ \widehat{\log\pi}_{t}\big)`$
을 얕은 트랜스포머 스택 → 전역 평균 → MLP+sigmoid 헤드에 통과시켜 클립 점수
$`d(C_{k})\in(0,1]`$ 를 출력합니다.

**3) 판별기 학습 (Positive–Unlabeled).** 양성은 $`\mathcal{S}_{\mathrm{high}}`$
(약 15%), 미분류 풀은 $`\mathcal{U}=\mathcal{D}_{\mathrm{real}}\setminus\mathcal{S}_{\mathrm{high}}`$
입니다.

> "We optimize a positive–unlabeled objective:" (§III-D)
(고품질 집합은 양성 BCE로, 나머지는 음성처럼 다루는 PU 목적함수입니다.)

$$\mathcal{L}_{D}=\eta\,\underbrace{\mathbb{E}_{\tau\in\mathcal{S}_{\mathrm{high}}}\!\big[-\log d(\tau)\big]}_{\text{positive BCE}\;\to\;1}\;+\;\underbrace{\mathbb{E}_{\tau\in\mathcal{U}}\!\big[-\log(1-d(\tau))\big]}_{\text{unlabeled as negative}\;\to\;0},$$

$`\eta=0.5`$ 이며 안정성을 위해 점수를 $`d\in[0.1,0.9]`$ 로 클립합니다.

> "Following the DWBC mapping from [30], we convert calibrated scores to weights $`w_{i}`$ ." (§III-D)
(보정된 점수를 DWBC 방식으로 클립 가중치 $`w_{i}`$ 로 변환합니다.)

**4) 품질 인지 후학습.** 시뮬에서 사전학습한 $`\pi_{\theta}`$ 를 실세계 데이터로
후학습할 때, 사전 계산된 가중치로 디퓨전 손실에 가중을 겁니다.

$$\mathcal{L}_{\pi}=\sum_{i=1}^{L}w_{i}\;\big\|\varepsilon_{\theta}(\cdot)-\varepsilon\big\|_{2}^{2},$$

짧은 가중치 warm-up 을 적용합니다.

### 학습 셋업

- **데이터(시뮬)** — MuJoCo에서 Qwen2.5-VL로 Objaverse 객체를 마이닝·물리 파라미터
  자동 부여, 200개 작업 × DexMimicGen 증식으로 작업당 500궤적 = 약 6.5M 프레임,
  361시간. 장면 배치·성공 기준은 Qwen이 자동 생성합니다.
- **데이터(실세계)** — 동일 임베디먼트에서 200개 작업 × 작업당 50시연 = 1만
  에피소드. 본문(§III-B) 표기로는 40.5시간, 2.92M 프레임이며 LIBERO-2.1 표준으로
  변환·공개합니다. (주의: 초록은 "2.92M frames", 서론(§I)은 "177.5 hours, 3.2M frames"
  로 적어 시간·프레임 수치가 본문과 불일치합니다 — 원문에 그대로 상충하므로 보정 없이
  병기합니다.)
- **모델 규모** — 정책: 28층, hidden 1024, 16 heads. 판별기: 12층, hidden 512,
  8 heads, 30M 파라미터.
- **최적화** — 정책 사전학습 100K 스텝, 판별기 10K 스텝. 8× NVIDIA A100, 총 배치
  64, AdamW.
- **베이스라인 학습** — 각 작업당 100시연으로 50K 스텝 학습/파인튜닝, 4× NVIDIA L20
  + LoRA, 추론은 단일 RTX 4090. 행동 청크 길이 $`L=32`$, 작업당 20 롤아웃 평가.

---

## 📊 실험 설정과 결과

베이스라인은 Diffusion Policy(DP), $`\pi_{0}`$ (플로우 매칭 액션 생성기 VLA),
GR00T N1(VLM+DiT 휴머노이드 VLA)입니다. DP는 36-D 벡터를 직접 회귀합니다.
$`\pi_{0}`$ 등은 2층 MLP 프로젝터(L/R 팔, L/R 손 물리 그룹별 분해)로 native 출력을
36-D 관절 명령으로 확장 매핑합니다.

**기본 작업 (Table I, 성공률 % / 20 trials)**

| Method | Pick&Place 평균대 | Assemble/Disassemble | Articulated | Avg. |
|---|---|---|---|---|
| DP | — | — | — | 34.2 |
| $`\pi_{0}`$ | — | — | — | 50.4 |
| GR00T N1 | — | — | — | 82.1 |
| **Dexora** | — | — | — | **89.6** |

> "Dexora attains the highest overall success, reaching $`\geq\!90\%`$ on 7/12 tasks and consistently leading the bimanual tasks." (§IV-B, Table I)
(12개 중 7개 작업에서 90% 이상, 양손 작업에서 일관된 선두. $`\pi_{0}`$ 는 그리퍼
중심 행동 공간을 고-DoF 손으로 매핑할 때 가장 크게 저하되어 임베디먼트 정합
데이터 없는 저→고 DoF 매핑이 ill-posed 임을 확인합니다.)

**다지 조작 작업 (Table II, 성공률 %)**

| Method | Use pen | Fetch book | Cut leek | Place plates | Rough dough | Twist cap | (평균) |
|---|---|---|---|---|---|---|---|
| DP | 5 | 10 | 10 | 0 | 15 | 0 | 6.7 |
| $`\pi_{0}`$ | 20 | 45 | 60 | 20 | 15 | 0 | 26.7 |
| GR00T N1 | 45 | 60 | 85 | 60 | 60 | 0 | 51.7 |
| **Dexora** | **65** | **80** | 80 | **70** | **80** | **25** | **66.7** |

> "Dexora gains the best average performance ( $`66.7\%`$ vs. $`51.7\%`$ for GR00T N1, $`26.7\%`$ for $`\pi_{0}`$ , and $`6.7\%`$ for DP)." (§IV-B, Table II)
(Dexora의 12-DoF 손 + 양팔 코퍼스가 인핸드·양팔 협응을 가능케 합니다. GR00T N1은
가장 강한 베이스라인이나 6-DoF 손이라 Use pen에 약하고 Twist cap에는 실패합니다.)

> "We find that cap twisting exhibits the lowest success rate. ... In our current setup, the absence of tactile feedback and relatively low-friction rigid fingertip pads leads to slip." (§IV-B)
(가장 접촉 집약적인 cap twisting이 25%로 최저 — 촉각 피드백 부재 + 저마찰 강체
지문 패드 때문에 미끄러짐이 발생합니다. 스케일만으로 접촉 정밀도 꼬리가 풀리지
않는다는 직접 증거입니다.)

**일반화.** OOD는 "Pick apple to the plate" 작업을 6조건(미지 배경/조명/객체,
가림, 혼잡, 높이 변화)에서 평가해 모든 변형에서 높은 성능을 유지합니다(Fig. 8).
크로스 임베디먼트는 EC-1(단팔 그리퍼 Franka Panda), EC-2(양팔 그리퍼 Cobot Magic
ALOHA), EC-3(Unitree G1 7-DoF 팔 + Inspire Hand 6-DoF)로 전이합니다.

> "projecting a 36-D joint action down to simpler robots is dimension reduction, not synthesis—far easier than “lifting” a gripper policy to dexterous hands." (§IV-C)
(36-D 행동을 단순 로봇으로 내리는 것은 차원 축소이지 합성이 아니므로, 그 역보다
잘 정의된 문제라는 본 논문의 핵심 가설을 실험으로 뒷받침합니다. 미사용 차원은
패딩, 부재 카메라는 마스킹으로 적응합니다.)

**어블레이션 1 — 데이터 구성(Fig. 10).** Sim Only → Sim+50% Real → Sim+All Real로
갈수록 성공률이 상승하며 다지 작업은 0→35→65, 10→60→85 로 개선됩니다.

![Figure 10 — Effect of training data composition](https://arxiv.org/html/2605.18722/x10.png)

> "Figure 10: Effect of training data composition. Success rate for four tasks under three training regimes: Sim Only, Sim + 50% Real, Sim + All Real." (§IV-D)
(시뮬은 기본 능력 부트스트랩에 효과적이나 실세계 데이터가 다지 능력 발현의
핵심 요인임을 보입니다.)

**어블레이션 2 — 판별기(Table III, S.R. % / Acc.↓ / Jerk↓, 20 episodes)**

| Method | Corn→plate S.R. | Acc.↓ | Jerk↓ | Lift basket S.R. | Acc.↓ | Jerk↓ |
|---|---|---|---|---|---|---|
| w/o discriminator | 85 | 0.034 | 0.043 | 55 | 0.041 | 0.052 |
| **w/ discriminator** | **95** | **0.020** | **0.032** | **80** | **0.023** | **0.036** |

> "the discriminator improves success rate and reduces acceleration and jerk at inference." (§IV-D, Table III)
(판별기가 성공률을 올리는 동시에 추론 시 가속도·저크를 줄여 더 매끄러운 동작을
유도합니다 — 혼합 품질 데이터에서 고품질 구간을 강조해 학습하는 효과입니다.)

---

## ⚖️ 한계

- **촉각 부재** — 가장 접촉 집약적인 cap twisting이 25%로 최저. 저자 스스로 촉각
  피드백 부재 + 저마찰 강체 지문 패드를 미끄러짐 원인으로 지목합니다(§IV-B).
- **데이터 수치 불일치** — 실세계 데이터 시간·프레임 수가 초록(2.92M)·서론(177.5h,
  3.2M)·본문(40.5h, 2.92M) 간에 상충합니다. 재현 시 정확한 규모를 코드/데이터
  배포본으로 확인해야 합니다.
- **장기 추론 부재** — 저자가 향후 과제로 명시: 메모리·하위목표 분해·언어 유도
  도구 사용을 결합하는 계층적 VLA 계획이 아직 없습니다(§V).
- **아키텍처상 손/팔 분리 부재** — 36-DoF를 단일 디코더 전용 디퓨전 트랜스포머로
  통째로 회귀합니다. 팔·손을 별도 모듈로 분리하거나 손가락별 구조적 입력을
  결합하는 장치는 없습니다. 성능은 데이터 스케일 + 품질 가중에서 옵니다(본 분석의 관찰).
- **베이스라인 핸디캡 가능성** — $`\pi_{0}`$ 등은 MLP 프로젝터로 그리퍼→고-DoF
  매핑을 강제당해 불리할 수 있어 비교의 공정성은 매핑 방식에 의존합니다.

---

## ♻️ 재현성

- **공개 범위** — 데모·데이터·코드·모델 공개 표명. 프로젝트 페이지
  `https://dexoravla.github.io`. 실세계 데이터는 LIBERO-2.1 표준으로 변환·오픈
  소스(§III-B).
- **하드웨어** — AIRBOT 팔 ×2 + XHAND 손 ×2(각 12관절), 외골격 백팩, Apple Vision
  Pro, 4× RGB @20Hz. MuJoCo 디지털 트윈.
- **학습 자원** — 8× A100(사전학습/판별기), 베이스라인 파인튜닝 4× L20 + LoRA,
  추론 단일 RTX 4090. 정책 28층/1024/16heads, 판별기 30M.
- **미상 항목** — 정확한 실세계 데이터 규모(상기 불일치), DWBC 점수→가중 매핑의
  구체 함수형, warm-up 스케줄 길이는 본문에 수치로 명시되지 않습니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P1 (Heterogeneous Body/Hand Action Expert)** — 강한 **긴장(tension)** 관계.
  Dexora는 36-DoF를 단일 디코더 전용 디퓨전 트랜스포머로 통째 회귀하는 monolithic
  decoder(Identity의 Antagonist C)이며 해부학적 Body/Hand 분리가 없습니다(D1).
  그럼에도 다지 66.7%를 달성한다는 점은 "분리 없이도 스케일+품질로 다지가 된다"는
  반례 후보입니다. 단, 가장 접촉 집약적인 Twist cap은 25%에 그쳐, 접촉 정밀도
  꼬리는 미해결로 남습니다. 텔레오퍼레이션 단계에서 팔(외골격)과 손가락(Vision
  Pro)을 분리한 점은 데이터 수집 계층의 해부학적 분리로, DexGrasp-VLA
  (arXiv:2511.00139)의 분리 철학과 닿지만 디코더 분리는 아닙니다.
- **P2 (Structured Input-Modality Binding)** — **지지(support, 간접)**. Dexora는
  비전+자기수용만 쓰고 촉각이 없으며 손가락별 구조적 결합도 없습니다(D8/D11
  반대편). 바로 그 때문에 Twist cap이 미끄러져 실패합니다 — PROBE의 촉각 결합 명제를
  음(-)의 증거로 지지합니다.
- **P3 (Hand-level System0 Module)** — **지지**. Dexora는 RL/저수준 안정화가 전혀
  없고 cap breakaway torque 하의 슬립이 미해결입니다(§IV-B). 이는 System0가
  겨냥하는 접촉 유지 문제(D13–D17)의 실제 실패 사례로, "VLA-only로 접촉 꼬리가
  풀리지 않는다"는 System0 필요성 주장을 뒷받침합니다(§10.1 Genesis AI 워치
  트리거 맥락).
- **P4 (VLM Pretraining Preservation)** — **약한 접점**. Dexora는 사전학습 VLM
  백본을 보존·동결하는 구조가 아니라 T5/SigLip 인코더-조건형 디퓨전 정책으로,
  D19/D23(플로우 매칭 vs 디퓨전)와 직접 대비됩니다. VLM 사전학습 보존 분석은
  하지 않습니다.
- **P5 (Task Definition & Falsifiable Evaluation)** — **방법론 참고**. 4-기여
  어블레이션은 아니지만(데이터 구성·판별기 어블레이션) OOD 6조건·크로스
  임베디먼트 프로토콜·평활도 지표(Acc/Jerk)는 D26 평가 메트릭과 직접 비교 가능.
  특히 PROBE의 D26 contact-precision 지표(slip count, pose stability)와 Dexora의
  Acc/Jerk가 호환 축입니다.
- **§10 경쟁자 함의** — Dexora는 VLA-only 강성능 사례(§10.1)에 해당하나, 가장
  접촉 집약적 작업에서 슬립으로 실패하므로 System0 필요성 주장에 정면 반례가 되지는
  않습니다. XHAND(12-DoF)는 Sharpa/xhand 계열(§4.1) 하드웨어 지형과도 인접합니다.

---

## ✨ 핀 논문 대비 델타

- **vs Shared-Autonomy Arm-Hand VLA / DexGrasp-VLA (arXiv:2511.00139, P1 핀)** —
  둘 다 팔/손을 분리하지만 층위가 다릅니다. DexGrasp-VLA는 디코더 층(Arm-Hand
  Feature Enhancement) + 자율 손 VLA로 분리하고 단손입니다. Dexora는 텔레오퍼레이션
  수집 층에서만 분리(외골격 팔 + Vision Pro 손가락)하고 디코더는 monolithic이며
  양팔·양손 36-DoF로 규모가 큽니다.
- **vs GR00T N1 (arXiv:2503.14734, P4 핀)** — 여기서는 베이스라인. Dexora가 다지
  66.7% vs 51.7%로 앞섭니다. 차이의 핵심은 손 DoF(12 vs 6)와 양팔 코퍼스로,
  아키텍처 혁신보다 임베디먼트·데이터 규모 효과입니다.
- **vs $`\pi_{0}`$ (arXiv:2410.24164, P1/P4 핀)** — $`\pi_{0}`$ 는 플로우 매칭
  액션 전문가 구조이나 그리퍼→고-DoF 매핑에서 26.7%로 크게 저하. Dexora는 디퓨전
  (DDPM) 본체 + 임베디먼트 정합 데이터로 이를 회피합니다.
- **진정으로 새로운 점** — 데이터 품질 판별기(PU 학습 + log-π 디노이징 잔차
  에너지 대리 + DWBC 가중 디퓨전 손실, 식 (4)–(8))는 어떤 핀 논문에도 없는 신규
  레시피입니다. 텔레오퍼레이션 노이즈를 손실 가중으로 다루는 구체적 메커니즘이
  핵심 델타입니다.

---

## ⚙️ 의사결정 함의

- **D21(staged training recipe) 보강 후보** — Stage 2 후학습에서 시연 품질
  가중치 $`w_{i}`$ 를 손실에 거는 옵션. 구체 config: 에피소드 단위 Acc/Jerk 하위
  20% 교집합 사전선별 → 리플레이 성공 양성($`\mathcal{S}_{\text{high}}`$ ≈15%) →
  PU 판별기($`\eta=0.5`$, 점수 클립 $`d\in[0.1,0.9]`$) → DWBC 가중. PROBE의 손실은
  플로우 매칭이므로 식 (4)의 디노이징 잔차 에너지를 플로우 매칭 속도장 잔차로
  치환하는 적응이 선행되어야 합니다.
- **D26(평가 프로토콜) 직접 차용** — contact-precision 지표에 Dexora의 정규화
  관절 가속도/저크(Acc↓, Jerk↓)를 추가하면, slip count·pose stability와 별도로
  동작 평활도를 수치화합니다(falsifier 보조 지표).
- **D24(첫 데모) 검증 가능 신호** — Twist cap 25% 실패는 인핸드 회전/도구 조작에서
  촉각·System0 없는 VLA의 한계 상한을 보여주는 외부 기준점입니다. PROBE의 phase 1/2
  목표치 설정 시 "촉각/System0 없이 도달 가능한 상한"의 외부 앵커로 사용 가능합니다.
- **D2(Body output space) 간접 지지** — "고→저 DoF 사영이 잘 정의됨"은 고-DoF
  학습 후 단순 임베디먼트로 내리는 전략을 지지하지만 PROBE의 flange-pose 결정과는
  관절 공간 패딩 방식이라 직접 일치하지는 않습니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **monolithic 반례의 적용 범위** — Dexora 66.7%는 평균치이며 가장 접촉 집약적
  Twist cap은 25%입니다. *가장 싼 sanity check*: PROBE 벤치마크가 정말 접촉 정밀도를
  요구하는 작업(인핸드 회전)인지 먼저 확인 — Dexora의 고득점 작업이 PROBE의
  분리/촉각 명제를 시험하는 작업과 겹치지 않으면 반례로서의 위협은 약합니다.
- **판별기 레시피의 손실 호환성** — 식 (4)의 log-π 대리는 DDPM 디노이징 잔차
  $`\|\varepsilon_{\theta}-\varepsilon\|^{2}`$ 기반입니다. PROBE는 플로우 매칭이므로
  그대로 옮길 수 없습니다. *가장 싼 check*: 소규모 홀드아웃에서 플로우 매칭 속도장
  잔차로 z-score 품질 점수가 고/저품질 시연을 분리하는지 먼저 확인.
- **VLM 백본 부재의 일반화** — Dexora는 사전학습 VLM 없이도 OOD에 강합니다. 이는
  P4(VLM 보존이 일반화의 근원)와 충돌하는 신호일 수 있습니다. *가장 싼 check*:
  Dexora OOD 6조건이 시각 일반화를 진짜로 강하게 요구하는지(미지 객체·혼잡 난이도)
  를 정성 확인 — 약한 OOD면 P4 명제와의 충돌은 과대평가입니다.
- **데이터 규모 불확실성** — 실세계 시간·프레임 수치가 본문 내에서 상충하므로,
  "스케일 효과" 결론을 PROBE 의사결정에 반영하기 전 배포 데이터로 실제 규모를
  확인해야 합니다.

---

## 💡 컨텍스트 제안

- **핀 후보(P5 또는 §10.1)** — Dexora를 "VLA-only 강성능 + 데이터 품질 인지 레시피"
  사례로 추적 대상에 올리는 것을 제안합니다. ① §10.1 Genesis AI 워치 트리거 맥락의
  실제 사례(VLA-only가 접촉 꼬리에서 실패하는 증거)로서, ② D21 학습 레시피에
  품질 가중 옵션을 추가하는 방법론 근거로서 가치가 있습니다. 단 P1/P4 핀 캡(각 8개)이
  차 있으므로 교체 대상 검토 필요 — 분리/촉각/System0 핵심 명제를 직접 다루지는
  않으므로 핀보다 §10 경쟁자/방법론 참조가 더 적합할 수 있습니다.
- **방법론 레퍼런스 후보** — 데이터 품질 판별기(PU + log-π 대리 + DWBC 가중)는
  `catalogs/` 의 학습 레시피 방법론 문서로 분리 정리할 가치가 있습니다
  (D21 보강 근거).
- context/MASTER.md 는 수정하지 않았습니다 — 위는 사람 판단을 위한 제안일 뿐입니다.
