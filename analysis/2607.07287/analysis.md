# Paper Analysis — TouchWorld: A Predictive and Reactive Tactile Foundation Model for Dexterous Manipulation

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | TouchWorld: A Predictive and Reactive Tactile Foundation Model for Dexterous Manipulation |
| 저자 | Jianyi Zhou, Feiyang Hong, Yunhao Li, Yicheng Zhao, Yongjue Cen, Zirui Liu, Jiakang Huang, Zirui Chen, Ruiyang Zhang, Weizhuo Zhu, Xuhua Song, Shuo Yang |
| 링크 | [arXiv:2607.07287](https://arxiv.org/abs/2607.07287) · [Website](https://phanes-lab.github.io/TouchWorld-website/) |
| 발행일 / 버전 | 2026-07-08 (v1) · v2 (2026-07-09 개정) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-07-13 |
| 관련 Pillar | P5, P3, P2, P4, P0 |
| 태그 | tactile, dexterity, vla-arch |

---

## 🧭 한 줄 요약 (TL;DR)

접촉이 풍부한 dexterous manipulation 을 **다중 시간척도 계층 정책**으로 분해해, 촉각을 두 방향으로 씁니다 — 느린 상위 계층의 **Tactile World Model** 이 미래 visual-tactile 서브골을 *예측*하고, 로봇 제어 루프 안의 **Tactile-Conditioned Refinement Policy(TRT)** 가 고주파 촉각 피드백으로 nominal 액션을 *반응적*으로 잔차 보정합니다. 6개 실로봇 태스크에서 clean 65.0%, 사람 교란 하 53.7% 성공률로 최강 baseline 을 각각 15.7·18.5%p 앞섭니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 일상 환경의 dexterous manipulation 은 접촉이 어떻게 전개될지 *예측*하면서 slip·정렬 오차·불안정 파지·힘 불일치로 생기는 국소 오류를 빠르게 *반응 보정*해야 합니다. 두 요구가 서로 다른 시간척도에서 동시에 필요합니다.
- **기존 접근의 한계** — 대부분의 VLA 정책은 촉각을 monolithic action model 안의 저주파 관측 스트림으로 취급해, 느린 의미 추론·액션 생성·빠른 접촉 피드백을 하나의 루프·같은 모델 용량에 억지로 합칩니다. 그 결과 태스크를 이해하고 그럴듯한 모션을 내면서도 slip 회복·힘 조절·정밀 삽입에서 실패합니다.
- **본 논문의 가설** — 의미 계획 / 촉각 world-model 예측 / visuo-tactile 액션 생성 / 촉각 조건 피드백 보정을 **명시적으로 분리**하면, VLA 의 의미 일반화를 보존하면서 접촉이 풍부한 태스크의 강건성을 높일 수 있습니다.
- **왜 지금 중요한가** — vision·language 는 semantic·geometric 안내는 주지만 파지 안정성·slip·접촉력·삽입 진행 같은 *숨은 접촉 상태*를 신뢰성 있게 드러내지 못합니다. 촉각만이 이 물리 단서를 노출하므로, 촉각을 예측·반응 양쪽에 배치하는 구조가 병목의 핵심입니다.

---

## 🧩 핵심 기여

- **예측·반응 이중 역할의 촉각 계층 정책** — 촉각을 (a) 미래 접촉 인지 서브골 예측을 위한 *예측 신호* 와 (b) 고주파 잔차 보정을 위한 *빠른 피드백 신호* 로 동시에 쓰는 첫 predictive-and-reactive tactile foundation model 을 제안합니다.
- **다중 시간척도 계층 아키텍처** — 느린 High-Level Planning Layer(Subtask Planner + Tactile World Model) + 중간 속도 visuo-tactile goal-conditioned 액션 청크 생성 + 고주파 촉각 잔차 refinement(TRT) 를 결합하고, end-to-end 역전파 없이 4단계로 분리 학습합니다.
- **6-태스크 실로봇 벤치마크** — clean / human-perturbation 두 설정을 갖춘 6개 태스크(Water Flower, Tabletop Clearing, Cup Insertion, Power Plug Insertion, Pot Wiping, Tissue Pulling)를 구축하고, TouchWorld 가 각각 65.0% / 53.7% 로 최강 baseline 을 15.7·18.5%p 앞섬을 보입니다.
- **이미지형 촉각 인터페이스 + 인간→로봇 촉각 사전학습** — nominal VLA 브랜치에서 촉각을 통일된 이미지로 렌더링해 image-language 사전학습과 호환시키고, Tactile World Model 을 EgoTouch 인간 상호작용 영상으로 사전학습한 뒤 로봇 데이터로 미세조정합니다.

---

## 🔑 기술 키워드

- **Tactile World Model** — 현재 관측·서브태스크를 조건으로 이 서브태스크가 도달할 미래 visual-tactile 접촉 결과(서브골)를 예측하는 상위 예측 모듈. "손이 이 동작을 마치면 접촉이 어떤 모양이어야 하는가"를 미리 그려 주는 참조 이미지 생성기.
- **Predictive-and-Reactive** — 촉각을 미래를 내다보는 예측 경로와 국소 오차를 즉시 고치는 반응 경로 양쪽에 배치하는 설계 철학. 예측은 목표를 세우고 반응은 그 목표에서 벗어남을 메웁니다.
- **Tactile Residual Transformer (TRT)** — nominal 액션 청크에 촉각·proprio 히스토리 기반 잔차를 더해 국소 접촉 오류를 온라인 보정하는 경량 Transformer. VLA 를 얼린 채 그 출력 주변만 미세하게 밀고 당기는 반응층.
- **Multi-timescale hierarchy** — 느린 의미 추론 · 중간 액션-청크 생성 · 빠른 접촉 보정을 서로 다른 갱신 주기에 배치하는 계층. 하나의 루프에 강제로 합치지 않아 각 계층이 자기 속도로 동작.
- **Image-form tactile representation** — raw 촉각 읽기를 이미지로 렌더/정규화해 VLA 백본이 시각 관측과 같은 표현형으로 촉각을 받게 하는 방식. 촉각 전용 인코더 없이 image-language 사전학습을 재사용.
- **Subtask Planner (memory-augmented)** — 태스크 지시·현재 관측·최근 상태 메모리로부터 실행 가능한 서브태스크를 느린 속도로 갱신하는 VLM 계획기. 저수준 명령이 아니라 "다음 의미 단계"를 내보내는 semantic 인터페이스.
- **Goal-conditioned flow-matching policy** — 서브태스크·예측 서브골·시각·촉각·proprio 를 조건으로 flow matching 으로 nominal 액션 청크를 생성하는 diffusion Transformer 정책.
- **Residual action subspace** — 잔차 보정을 wrist pose 블록 + 선택된 손가락 관절 등 접촉 민감 차원(58-dim)에만 적용하고 나머지는 nominal 출력을 그대로 두는 마스킹된 부분공간.

---

## 🔬 방법론

### 직관

TouchWorld 의 출발점은 "접촉이 풍부한 조작은 본질적으로 서로 다른 속도의 세 문제가 겹쳐 있다"는 관찰입니다. 물 주기·플러그 삽입 같은 일상 기술은 (i) 지금 어느 단계인지를 판단하는 느린 의미 추론, (ii) 그 단계를 진전시키는 중간 속도의 액션 청크 생성, (iii) 접촉이 어긋나는 순간 즉시 손끝을 미는 빠른 반응, 이 세 가지를 동시에 요구합니다. 기존 VLA 는 촉각을 그저 또 하나의 입력 토큰으로 붙여 세 문제를 한 모델·한 루프에 밀어 넣기 때문에, 태스크를 이해하고도 slip·삽입 정렬에서 무너집니다.

TouchWorld 는 이 세 속도를 아예 분리된 모듈에 배분합니다. 위에는 느리게 도는 High-Level Planning Layer 가 있어, VLM 기반 Subtask Planner 가 "지금 할 서브태스크"를 정하고, Tactile World Model 이 "그 서브태스크가 끝났을 때 접촉이 어떤 모양이어야 하는가"를 미래 visual-tactile 이미지로 그려 냅니다. 이 예측 서브골이 예측 경로의 핵심으로, 정책에 "도달해야 할 접촉 목표"를 미리 쥐어 줍니다.

가운데에는 중간 속도로 도는 visuo-tactile goal-conditioned 정책이 있어, 서브태스크·예측 서브골·시각·촉각·proprio 를 조건으로 flow matching 으로 nominal 액션 청크를 냅니다. 여기서 촉각은 이미지로 렌더되어 시각과 같은 형태로 들어가므로, VLM 의 image-language 사전학습을 그대로 재사용할 수 있고 촉각 전용 인코더를 백본에 심을 필요가 없습니다.

맨 아래에는 로봇 제어 루프 안에서 가장 빠르게 도는 TRT(Tactile Residual Transformer)가 있어, 최근 촉각·proprio 히스토리로 nominal 액션에 *잔차* 를 더합니다. nominal 정책이 의미·기하 진행을 책임지는 동안 TRT 는 slip·충격·삽입 정렬 오차 같은 국소 접촉 오류만 국소적으로 메웁니다. 예측(미래 목표)과 반응(현재 오차)을 이렇게 나눠 두는 것이 이 논문의 골격입니다.

### 아키텍처

![Figure 1 — TouchWorld 개념 개요](https://arxiv.org/html/2607.07287/x1.png)

> "Figure 1: Conceptual overview of TouchWorld. The High-Level Planning Layer contains a Subtask Planner that produces executable subtasks and a Tactile World Model that predicts visual-tactile subgoals. A visuo-tactile goal-conditioned policy generates nominal action chunks, and a tactile-conditioned refinement policy refines the final action online using high-frequency tactile feedback." (§1)
> (예측 경로(상위 계획 계층)와 반응 경로(refinement)가 nominal 정책을 사이에 두고 촉각을 양방향으로 쓰는 전체 구도를 시각화합니다.)

전체 파이프라인은 입력 — 태스크 지시 `` $`\ell`$ ``, 다중 뷰 이미지 `` $`\mathcal{I}_{t}`$ ``, proprio 상태 `` $`\mathbf{s}_{t}`$ ``, 촉각 관측 `` $`\mathcal{X}_{t}`$ ``, 상위 메모리 `` $`m_{t}`$ `` — 을 받아 실행 액션 `` $`\mathbf{a}_{t}`$ `` 를 냅니다. 상위 계획 계층이 서브태스크와 서브골을 만들고, 두 액션 정책이 이를 소비합니다.

> "Given a task instruction $`\ell`$, current multi-view images $`\mathcal{I}_{t}`$, proprioceptive state $`\mathbf{s}_{t}`$, tactile observations $`\mathcal{X}_{t}`$, and high-level memory $`m_{t}`$, TouchWorld predicts the executed action $`\mathbf{a}_{t}`$ through the High-Level Planning Layer and two action policies." (§2)
> (한 스텝의 입출력 계약을 못박습니다 — 네 모듈은 이 공통 관측 위에서 각자 자기 시간척도로 동작합니다.)

네 모듈의 함수적 정의는 다음과 같습니다.

$$\ell_{t}^{\mathrm{sub}}=\pi_{\mathrm{subtask}}(\ell,\mathcal{I}_{t},m_{t}),$$

$$g_{t}=\pi_{\mathrm{world}}(\ell,\ell_{t}^{\mathrm{sub}},\mathcal{I}_{t},\mathcal{X}_{t}),$$

$$\left(\hat{\mathbf{A}}_{t:t+H-1},\mathbf{c}_{t}\right)=\pi_{\mathrm{goal}}(\ell,\ell_{t}^{\mathrm{sub}},g_{t},\mathcal{I}_{t},\mathbf{s}_{t},\mathcal{X}_{t}),$$

$$\tilde{\mathbf{A}}_{\tau:\tau+W-1}=\pi_{\mathrm{tactile}}(\hat{\mathbf{A}}_{\tau:\tau+W-1},\mathbf{s}_{\tau-k:\tau},\mathcal{X}_{\tau-k:\tau},\mathbf{c}_{t}),$$

여기서 `` $`\pi_{\mathrm{subtask}}`$ `` · `` $`\pi_{\mathrm{world}}`$ `` · `` $`\pi_{\mathrm{goal}}`$ `` · `` $`\pi_{\mathrm{tactile}}`$ `` 는 각각 Subtask Planner · Tactile World Model · Visuo-Tactile Goal-Conditioned Policy · Tactile-Conditioned Refinement Policy 입니다. `` $`\ell_{t}^{\mathrm{sub}}`$ `` 는 시각 `` $`t`$ `` 의 실행 서브태스크, `` $`g_{t}`$ `` 는 그 서브태스크의 예측 visual-tactile 서브골, `` $`\hat{\mathbf{A}}_{t:t+H-1}`$ `` 는 horizon `` $`H`$ `` 의 nominal 액션 청크, `` $`\mathbf{c}_{t}`$ `` 는 컨텍스트 토큰입니다. refinement 스텝 `` $`\tau`$ `` 에서는 길이 `` $`W`$ `` 의 sliding lookahead 창과 길이 `` $`k`$ `` 의 촉각·proprio 히스토리를 씁니다.

![Figure 2 — TouchWorld 아키텍처](https://arxiv.org/html/2607.07287/x2.png)

> "Figure 2: TouchWorld architecture. The High-Level Planning Layer runs at a slow semantic rate and contains the Subtask Planner, which produces executable subtasks, and the Tactile World Model, which predicts visual-tactile subgoals. The Visuo-Tactile Goal-Conditioned Policy generates nominal action chunks at an intermediate rate, and the Tactile-Conditioned Refinement Policy refines execution inside the high-frequency robot control loop using tactile and proprioceptive feedback." (§2)
> (세 시간척도가 물리적으로 다른 모듈·다른 갱신 주기에 배치됨을 보여 줍니다 — 계층 분리가 이 논문의 아키텍처 골격입니다.)

**① Subtask Planner.** 태스크 지시·현재 시각 관측·상위 메모리 `` $`m_{t}`$ `` 를 받아 저수준 명령 대신 느린 속도로 semantic phase 를 갱신하고 실행 서브태스크를 냅니다. 구조화된 출력은

$$o_{t}^{\mathrm{sub}}=\{\ell,\ell_{t}^{\mathrm{sub}},r_{t}\},$$

로, `` $`r_{t}`$ `` 는 선택적 자유형 추론입니다. 원 지시와 실행 서브태스크만 하위 VLA 정책에 노출되고 자유형 추론은 액션 인터페이스 밖에 둡니다. 메모리 `` $`m_{t}`$ `` 는 이전 서브태스크·예측 서브골·실행 상태를 담아, 매 갱신에 현재 관측만 쓰면서도 태스크 진행을 추론하게 합니다.

**② Tactile World Model.** 현재 관측·상위 상태를 조건으로 현재 서브태스크의 기대 접촉 결과를 기술하는 미래 visual-tactile 서브골을 예측합니다. 결정적으로, 이 예측은 상시 재생성되지 않습니다.

> "These predictions are updated only when the Subtask Planner detects a new subtask or a meaningful task-state change, so stable task phases reuse the previous tactile subgoal instead of repeatedly regenerating future predictions." (§2.1)
> (안정 국면에서는 이전 서브골을 재사용해 무거운 world model 호출을 아껴, 예측을 이벤트 구동으로 만듭니다.)

**③ Visuo-Tactile Goal-Conditioned Policy.** tactile diffusion Transformer 정책으로, 촉각을 통일 이미지로 변환해 vision-language 브랜치가 시각과 함께 처리하게 하고, diffusion Transformer action expert 가 flow matching 으로 액션을 생성합니다. 프롬프트는 원 지시와 현재 서브태스크를 문자열 결합합니다.

$$\ell_{\mathrm{policy}}=\texttt{Task: }\ell\oplus\texttt{ Current subtask: }\ell_{t}^{\mathrm{sub}}.$$

이미지형 촉각 인터페이스의 설계 의도는 다음에 못박혀 있습니다.

> "This design keeps the nominal action policy compatible with image-language pretraining and avoids introducing modality-specific tactile encoders into the VLA branch." (§2.2)
> (촉각을 시각과 같은 표현형으로 넣어 VLM 사전학습을 재사용하고, 백본에 촉각 전용 인코더를 심는 부담을 피합니다.)

**④ Tactile-Conditioned Refinement Policy (TRT).** nominal 청크를 국소 보정된 창으로 바꾸는 반응층으로, goal-conditioned 정책보다 빠른 피드백 속도로 돌아 다음 nominal 청크를 기다리지 않고 접촉 변화를 반영합니다. TRT 는 nominal VLA 와 달리 고주파 촉각 히스토리를 직접 처리하고, 촉각 신호 유형별 경량 인코더를 씁니다 — 이미지형 촉각 맵은 촉각 이미지로, matrix 촉각 읽기는 convolution 으로, 저차원 촉각 상태는 Fourier feature + MLP 로 인코딩한 뒤 residual Transformer 로 융합합니다.

### 학습 목표 / 손실

refinement 스텝 `` $`\tau`$ `` 에서 TRT `` $`f_{\phi}`$ `` 는 잔차 창을 예측하고 nominal lookahead 에 더합니다.

$$\Delta\mathbf{A}_{\tau:\tau+W-1}=f_{\phi}(\hat{\mathbf{A}}_{\tau:\tau+W-1},\mathbf{s}_{\tau-k:\tau},\mathcal{X}_{\tau-k:\tau},\mathbf{c}_{t}),$$

$$\tilde{\mathbf{A}}_{\tau:\tau+W-1}=\hat{\mathbf{A}}_{\tau:\tau+W-1}+\Delta\mathbf{A}_{\tau:\tau+W-1}.$$

학습 타깃 잔차는 시연된 고주파 액션 창과 nominal VLA lookahead 창의 차이이고, 피드백-보정 손실은 그 잔차에 대한 `` $`\ell_2`$ `` 회귀입니다.

$$\mathcal{L}_{\mathrm{fb}}=\left\|f_{\phi}(\hat{\mathbf{A}}_{\tau:\tau+W-1},\mathbf{s}_{\tau-k:\tau},\mathcal{X}_{\tau-k:\tau},\mathbf{c}_{t})-(\mathbf{A}^{*}_{\tau:\tau+W-1}-\hat{\mathbf{A}}_{\tau:\tau+W-1})\right\|_{2}^{2}.$$

`` $`\mathbf{A}^{*}_{\tau:\tau+W-1}`$ `` 는 시연된 고주파 액션 창입니다. 핵심은 이 손실이 *접촉 민감 잔차 부분공간에만* 적용된다는 점입니다.

> "The loss is applied in the tactile-sensitive residual action subspace, while action dimensions outside this subspace follow the nominal VLA output." (§3.4)
> (반응층이 손댈 수 있는 축을 접촉 관련 차원으로 제한해, nominal 정책의 의미·기하 책임을 침범하지 않게 못박습니다.)

nominal 정책 자체는 flow matching 으로 학습됩니다 — 학습 시 데이터 액션과 Gaussian noise 의 보간에서 노이즈 액션을 뽑고, 추론 시 Gaussian noise 에서 시작해 예측 velocity field 를 적분해 nominal 시퀀스를 냅니다. 잔차 학습 단계에서는 학습된 nominal VLA 를 붙여 **얼린 채** 두고, residual actor 와 촉각 피드백 인코더만 최적화합니다.

### 학습 셋업

전체를 end-to-end 로 역전파하지 않고, 각 모듈을 자기 시간척도에 맞는 감독 신호로 먼저 학습한 뒤 마지막에 nominal VLA 와 반응층을 결합하는 **4단계 recipe** 입니다.

- **Stage 1 — Subtask Planner.** `Qwen3-VL-4B-Instruct` 를 주석된 teleoperation trace 로 LoRA SFT. 각 예제는 전역 지시·현재 카메라 관측·최근 planner 상태 메모리·실행 서브태스크 라벨로 구성되고, 데이터셋은 **128,866 records**. LoRA rank 16 · alpha 32 · dropout 0.05 · lr `` $`10^{-4}`$ `` · cosine decay(warmup 0.1) · bfloat16 · 20 epochs. stale/반복 히스토리에 강건하도록 teacher label·희귀 phase oversample·noisy-memory 변형을 포함.
- **Stage 2 — Tactile World Model.** `Wan2.2-TI2V-5B` 에서 미세조정. 먼저 대규모 **EgoTouch** 인간 상호작용 영상(동기화된 egocentric·wrist 영상, bimanual hand pose, dense bilateral palm pressure)으로 사전학습해 일반 visual-to-tactile dynamics prior 를 학습한 뒤, **10시간 로봇 시연(30 FPS ≈ 108만 프레임)** 으로 미세조정. 로봇 샘플은 `` $`384\times 224`$ `` 해상도 17-frame visual-tactile 타깃. LoRA(DiT attention·FFN, target `` $`\{q,k,v,o,\mathrm{ffn}.0,\mathrm{ffn}.2\}`$ ``) rank 64 · lr `` $`10^{-4}`$ `` · 50 epochs.
- **Stage 3 — Visuo-Tactile Goal-Conditioned Policy.** standalone nominal 정책으로 imitation + flow matching 학습. 예측 서브골이 있으면 추가 goal context 로, 없으면 현재 관측·서브태스크만으로 학습·평가. Wuji 플랫폼에서 **120-dim 액션(2×48-dim arm-hand + 9-dim head + 15 reserved), 32-step horizon**. 30,000 step · global batch 32 · bfloat16 · AdamW · grad clip 1.0 · cosine(warmup 1,000, peak lr `` $`2.5\times 10^{-5}`$ ``, final `` $`2.5\times 10^{-6}`$ ``).
- **Stage 4 — Integrated VLA-Refinement.** 학습된 nominal VLA(얼림)에 TRT 를 붙여 masked MSE 로 잔차 학습. TRT: `` $`d_{\mathrm{model}}=512`$ `` · 8 layers · 8 heads · `` $`W`$ ``-step residual query · residual reg `` $`10^{-4}`$ ``. 잔차는 **58-dim 접촉 민감 부분공간(두 wrist pose 블록 + 선택 손가락 관절)** 에만, 나머지는 nominal 유지. AdamW lr `` $`10^{-4}`$ `` · weight decay `` $`10^{-4}`$ ``.

배포 스케줄: nominal `` $`H=32`$ ``, TRT 는 `` $`W=16`$ `` lookahead · stride `` $`C=4`$ ``(offset `` $`\{0,4,8,12\}`$ ``)로 첫 `` $`C`$ `` 개 보정 액션을 커밋 후 잔차 재예측. 예컨대 nominal `` $`[0,15]`$ `` 에 조건화해 `` $`[0,3]`$ `` 커밋, 이어 `` $`[4,19]`$ `` 조건화해 `` $`[4,7]`$ `` 커밋. Subtask Planner/World Model 이 없으면 원 지시로 fallback 하고 예측-goal 조건화를 끄되, visuo-tactile 정책과 refinement 는 계속 실행 가능.

---

## 📊 실험 설정과 결과

**셋업.** teleoperation 은 Meta Quest 헤드셋 + Touch Plus 컨트롤러 + Wuji Glove, 로봇은 Wuji dexterous hand + JQ-Industries 촉각 글러브를 단 휴머노이드. 6개 태스크 각각 **200 teleoperated 학습 궤적 + 100 실로봇 평가 rollout**, clean / human-perturbation(목표 변위·불안정 접촉·파지 간섭) 두 설정. Baseline 은 Pi-0.5(VLA), FTP-1(이전 monolithic 촉각 정책), GR00T N1.7(generalist).

### 주 결과 (Table 1)

| Method | Water Flower | Tabletop Clearing | Cup Insertion | Power Plug Insertion | Pot Wiping | Tissue Pulling | Avg. |
|---|---|---|---|---|---|---|---|
| **Clean** | | | | | | | |
| Pi-0.5 | 52 | 66 | 36 | 12 | 39 | 39 | 40.7 |
| FTP-1 | 56 | 60 | 48 | 32 | 57 | 43 | 49.3 |
| GR00T N1.7 | 50 | 58 | 33 | 18 | 36 | 41 | 39.3 |
| **TouchWorld** | **72** | **76** | **66** | **45** | **70** | **61** | **65.0** |
| **Human Perturbation** | | | | | | | |
| Pi-0.5 | 34 | 44 | 24 | 6 | 28 | 30 | 27.7 |
| FTP-1 | 39 | 42 | 34 | 20 | 42 | 34 | 35.2 |
| GR00T N1.7 | 32 | 36 | 21 | 9 | 26 | 32 | 26.0 |
| **TouchWorld** | **60** | **62** | **52** | **35** | **57** | **56** | **53.7** |

> "In the clean setting, TouchWorld reaches 65.0% average success, improving over the strongest baseline by 15.7 percentage points. Under human perturbations, TouchWorld reaches 53.7% average success, improving over the strongest baseline by 18.5 percentage points." (§4.3, Table 1)
> (clean 최강 baseline 은 FTP-1(49.3), 교란 하도 FTP-1(35.2) — 즉 델타는 두 설정 모두 이전 촉각 정책 FTP-1 대비 값입니다.)

> "The gains are especially clear on power plug insertion, pot wiping, and tissue pulling, where tactile prediction and fast local correction are most important." (§4.3)
> (Power Plug Insertion 은 clean 에서 FTP-1 32→45, 교란 20→35 로 가장 큰 절대 이득 — 정밀 삽입이 예측+반응 촉각의 수혜가 가장 큰 태스크임을 시사합니다.)

주목할 점은 교란 하 성능 저하 폭입니다. TouchWorld 는 65.0→53.7(−11.3%p)로, Pi-0.5(40.7→27.7, −13.0%p)·GR00T(39.3→26.0, −13.3%p)보다 저하가 완만해, 반응 경로가 교란 강건성에 기여함을 정성적으로 보여 줍니다.

### Ablation (Figure 5)

![Figure 5 — Stacked ablation](https://arxiv.org/html/2607.07287/figures/ablation_results_stacked.png)

> "Removing tactile input causes the largest degradation, confirming that contact observations are essential for this benchmark. Removing the Tactile-Conditioned Refinement Policy particularly hurts the human perturbation setting, where the system must correct local execution errors online. Removing the Subtask Planner mainly reduces long-horizon consistency, while removing the Tactile World Model weakens contact-aware goal conditioning." (§4.4)
> (제거 실험은 각 컴포넌트가 겨냥한 실패 모드를 분리합니다 — 촉각 입력=전반 붕괴, refinement=교란 강건성, Subtask Planner=장기 일관성, World Model=접촉 인지 goal 조건화. 다만 수치가 아닌 stacked bar 로만 제시되어 컴포넌트별 %p 이득은 verbatim 인용 불가.)

- **Tactile input 제거** — 가장 큰 저하. 이 벤치마크가 근본적으로 접촉 의존적임을 확인(nominal 정책 성능이 촉각 없이는 무너짐).
- **Refinement(TRT) 제거** — 특히 교란 설정을 해침. 반응층이 온라인 국소 오차 보정 담당임을 분리 확인.
- **Subtask Planner 제거** — 장기 일관성 감소(원 프롬프트만으로 조건화 시 phase drift).
- **Tactile World Model 제거** — 접촉 인지 goal 조건화 약화(현재 관측·서브태스크만으로 조건화).

### Tactile World Model 예측 정확도 (Table 2)

| Method | Temporal Contact Acc. | Contact IoU | Volumetric IoU |
|---|---|---|---|
| Current tactile copy (persistence) | 70.4 | 31.8 | 24.6 |
| Nearest-neighbor subgoal | 77.5 | 39.2 | 31.0 |
| **Tactile World Model** | **86.3** | **52.7** | **43.8** |

> "Table 2 shows that the Tactile World Model predicts substantially more accurate contact timing and terminal tactile geometry than simple persistence or retrieval baselines." (§4.5, Table 2)
> (held-out 궤적에서 17-frame goal clip 을 생성해 실제 미래 구간과 정렬 — persistence(현 촉각 복사)·nearest-neighbor(라벨 retrieval) 대비 Contact IoU 를 21~13%p 앞서, 학습된 예측이 검색·복사보다 접촉 기하를 잘 잡음을 보입니다. 임계값 `` $`\tau`$ `` 로 pressure map 을 이진화 후 IoU 측정.)

### Subtask Planner 분석 (Table 3)

| Planner | Subtask Acc. | Execution Success | Transition F1 |
|---|---|---|---|
| Zero-shot Qwen3-VL-4B | 43 | 34 | 62 |
| Zero-shot Qwen3-VL-32B | 69 | 54 | 71 |
| SFT Qwen3-VL-4B w/o Memory | 73 | 60 | 76 |
| **Memory-Augmented SFT Qwen3-VL-4B (Ours)** | **88** | **65** | **82** |

> "The memory-augmented 4B Subtask Planner outperforms the zero-shot 32B planner, suggesting that task-phase supervision and execution history are more important than model scale alone for this interface." (§4.6, Table 3)
> (SFT 4B(w/o memory) 이 이미 zero-shot 32B 를 앞서고, 메모리 추가가 특히 Transition F1(76→82)·Subtask Acc(73→88)을 끌어올려 — phase 전이 일관성에는 스케일보다 실행 히스토리가 결정적임을 시사합니다.)

---

## ⚖️ 한계

- **단기 예측 지평의 world model** — 저자 명시: Tactile World Model 은 짧은 지평 visual-tactile 서브골만 예측합니다. 물체 이동·손 가림·사람 교란이 다수의 그럴듯한 미래를 만들면 장기 예측이 곤란해집니다. 예측 경로의 가치가 "다음 접촉 상태"에 국한되므로, 진정한 장기 계획은 여전히 Subtask Planner 의 semantic 분해에 의존합니다 — world model 이 실질적으로 *접촉 결과 예측기* 이지 dynamics planner 는 아닙니다.
- **6개 태스크의 좁은 커버리지** — 저자 명시: 계획·삽입·wiping·연성물 처리를 다루지만 가정 조작·변형체 상호작용의 다양성을 소진하지 못합니다. 태스크당 200 시연·100 rollout 은 통계적으로는 견고하나 태스크 다양성 축이 좁아, 절대 성공률(clean 65%)이 여전히 배포 가능 수준과는 거리가 있습니다.
- **센싱 레이아웃 고착** — 저자 명시: nominal 브랜치의 이미지형 촉각 + refinement 의 고주파 히스토리는 특정 로봇 플랫폼 배치에 묶여, 다른 촉각 센서·손 형태로의 전이는 calibration·normalization·소량 적응 데이터를 요구합니다. 모듈러하다고 주장하나 센서 교체 비용이 0 이 아닙니다.
- **고정 스케줄 하이퍼파라미터** — 저자 명시: 상위 갱신율·world model refresh 규칙·nominal chunk 길이·residual commit 간격을 고정 프로파일로 씁니다. 접촉 dynamics 가 급변할 때 적응형 스케줄이 없으면 반응 지연·과다 계산 트레이드오프가 고정됩니다.
- **추론 없는 정성적 지원 (추론된 갭)** — end-to-end 학습을 피하고 4단계 분리 학습을 택했기에, 컴포넌트 간 오차 누적(예: World Model 서브골이 부정확할 때 nominal 정책이 그 오차를 어떻게 흡수/증폭하는가)을 정량화하지 않았습니다. Table 2 의 예측 정확도(Contact IoU 52.7%)는 절대치로는 낮은 편이라, 부정확한 서브골이 하위 정책을 오도할 위험이 있으나 그 민감도 분석이 없습니다.
- **58-dim 잔차 부분공간의 수작업 지정 (추론된 갭)** — 접촉 민감 축(wrist pose + 선택 손가락 관절)을 사람이 지정합니다. 이 부분공간 선택이 태스크·손 형태별로 달라질 수 있고, 잘못 고르면 반응 경로가 정작 필요한 축을 못 건드립니다. 자동화·학습된 마스크 부재.

---

## ♻️ 재현성

- **코드/가중치** — 논문 본문·메타에 GitHub 코드 공개 표기 없음. 프로젝트 페이지([phanes-lab.github.io/TouchWorld-website](https://phanes-lab.github.io/TouchWorld-website/))만 제시되어, 정성 데모·설명 중심으로 추정. 코드·체크포인트 미공개로 간주(확인 불가).
- **데이터** — 로봇 데이터는 Wuji 플랫폼 자체 teleoperation(태스크당 200 궤적, 10시간·≈108만 프레임)으로 비공개. 사전학습에 쓴 **EgoTouch** 는 외부 인용 데이터([34])로, 이 부분은 잠재적 재사용 가능.
- **하드웨어** — Wuji dexterous hand + JQ-Industries 촉각 글러브 + Meta Quest teleoperation 스택. 특정 상용 하드웨어 의존으로 정확 재현에는 동일 플랫폼 필요.
- **베이스 모델** — Subtask Planner=`Qwen3-VL-4B-Instruct`(공개), Tactile World Model=`Wan2.2-TI2V-5B`(공개). 하이퍼파라미터(LoRA rank/lr/epoch, 액션 차원, 스케줄)는 §8 Implementation Details 에 상세 기재되어 아키텍처 재현성은 비교적 높음.

---

## 🎯 관련 Pillar / Decision (P# / D#)

TouchWorld 는 우리 스택의 여러 pillar 를 동시에 건드리는, 특히 P5·P3 에 밀도 높은 참조입니다.

- **P5(action-conditioned world model)** — Tactile World Model 이 D28(world-model role: 예측 auxiliary)·D29(integration architecture)·D30(prediction space)·D31(action conditioning)·D32(egocentric hand-object WM) 전반의 대안 데이터 포인트입니다. 우리 D29 v1 은 *공유 VLA 백본의 auxiliary head*(Being-H0.7 style) 를 택했는데, TouchWorld 는 정반대로 **별도 대형 비디오 모델(Wan2.2-TI2V-5B)** 을 world model 로 분리 배치합니다. 우리 D30 v1 은 *latent/3D-flow* 예측을 택했으나 TouchWorld 는 **raw visual-tactile 이미지/비디오 grid** 를 예측합니다(우리가 비용상 deferred 로 둔 raw-pixel 경로). D31 의 action-conditioned 라기보다 **subtask/goal-conditioned** 예측이라는 점도 차이입니다. D32 의 *egocentric 인간 영상 기반 hand-object WM* 는 EgoTouch 사전학습이 강하게 지지합니다.
- **P3(System0 저수준 반응 안정화)** — TRT 는 우리 System0 의 **비-RL 지도학습 대안** 입니다. D15(input modality: 촉각+proprio, **vision excluded**) 와 정확히 일치하고, D13(post-contact 국소 보정) 역할도 부합합니다. 다만 D14 v1 의 *binary maintain_grasp on/off gating(bypass-when-off)* 와 달리 TRT 는 **상시 동작하는 잔차층** 이고, D16 v1 의 *직접 finger joint command* 와 달리 **잔차(residual)** 출력입니다. RL 없이 imitation residual 로 반응 안정화를 얻는다는 점이 D17(System0 RL policy spec) 에 대한 도전적 반례입니다.
- **P2(구조화 다중모달 관측 융합)** — 이미지형 촉각 표현은 우리 D11 v1(**per-finger proprio-tactile 토큰 10 finger + 2 palm, topology-aware**)·D12·D10(cross-attention 비-concat 융합)와 **정면으로 대립** 합니다. TouchWorld 는 촉각을 이미지로 flatten 해 VLM 사전학습 재사용을 얻는 대신 per-finger 접촉 귀속을 포기합니다 — 우리 identity 가 명시적으로 지양하는 flat-concat 계열에 가깝습니다.
- **P4(데이터 효율 적응 사전학습)** — Stage 1~4 분리 학습 recipe 는 D21(staged pretraining + adaptation) 의 실증이고, EgoTouch(인간 ego 영상)→로봇 미세조정은 D22(egocentric-centric corpus, **OPEN**) 를 지지하는 데이터 포인트입니다.
- **P0(VLA 데이터/벤치마크)** — EgoTouch 는 D25(tactile/force/torque 데이터 스카우팅) 의 직접 후보 corpus(동기화 ego·wrist 영상, bimanual pose, dense palm pressure)입니다.

**Identity 긴장/지지** — 우리 identity 는 "correction/residual-on-frozen-VLA 는 VLA ceiling 을 못 넘는다"고 봅니다. TouchWorld 의 TRT 는 정확히 *frozen VLA 위의 residual 모듈* 이라 우리 Antagonist A 의 실증 사례입니다. 그러나 촉각 world model(예측 경로)은 residual 이 아닌 VLA-level 예측 강화라, 논문 전체는 "residual 만"이 아니라 "예측+반응"이라는 점에서 우리와 부분 일치합니다.

---

## ✨ 핀 논문 대비 델타

- **P5 vs. DexWM / Being-H0.7 / VLA-JEPA(핀)** — 핀들은 latent 또는 3D-flow 예측·auxiliary head 통합을 지향합니다. TouchWorld 의 새로움은 world model 을 **촉각 서브골 생성기** 로 좁히고, latent 가 아닌 **visual-tactile 이미지** 를 예측해 downstream 정책의 goal context 로 직접 소비시킨다는 점입니다. 즉 "world model = 접촉 예측 참조 이미지" 라는 실용적 축소로, 우리 D30 latent 결정에 대한 raw-pixel 반례입니다.
- **P3 vs. DexSynRefine(residual RL + RMA, 핀)** — DexSynRefine 은 residual **RL** + RMA contact adaptation 을 씁니다. TouchWorld 의 TRT 는 동일한 residual 발상을 **RL 없이 지도 imitation** 으로 얻고, teacher-student 대신 시연 고주파 액션과 nominal 의 차분을 직접 회귀합니다. reward engineering 을 아예 없앤 반응층이라는 점이 델타입니다.
- **P3/P5 vs. T-Rex([17], 관련 연구로 인용)** — T-Rex 는 고주파 촉각을 reactive control 에 쓰는 tactile-reactive dexterous manipulation 입니다. TouchWorld 는 그 reactive 경로에 **예측 경로(world model)** 를 얹어, 반응만이 아니라 "예측된 접촉 목표 → 반응 보정" 의 이중 구조로 확장합니다.

---

## ⚙️ 의사결정 함의

이 논문이 맞다면 우리 파이프라인에서 검토·조정할 구체 지점:

- **D29/D30 — world model 통합·예측 공간 재검토** — TouchWorld 의 성공은 "world model 을 백본 auxiliary head 가 아니라 *별도 예측 모델* 로 두고, latent 가 아니라 관측 공간(촉각 이미지)에서 예측해도 성능이 난다"는 증거입니다. 우리 D29(auxiliary head)·D30(latent) 결정에 대한 대안 arm 으로, `prediction_space ∈ {latent, raw_visual_tactile}` 와 `wm_integration ∈ {aux_head, separate_model}` 를 명시적 ablation 변수로 승격할 근거가 생깁니다. 단 world model 을 이벤트 구동(서브태스크 변경 시에만 refresh)으로 호출하는 스케줄링 트릭은 별도 모델 채택 시 계산 비용을 실용화하는 핵심 레버입니다.
- **D17/D16 — System0 를 RL 이 아닌 residual imitation 으로도 시도** — TRT 는 우리 System0 목표(post-contact 국소 안정화)를 reward engineering 없이 `L_fb` 같은 masked MSE 잔차 회귀로 달성합니다. System0 의 첫 baseline 으로 **imitation residual 층(58-dim 접촉 부분공간, frozen nominal 위)** 을 두고, RL System0 를 그 위 상한으로 비교하는 2-arm 설계가 가능합니다. 구체 config: `residual_subspace_dims`(wrist pose + 선택 손가락), `residual_reg=1e-4`, `commit_interval C=4`, `lookahead W=16`.
- **D14 — 상시 잔차 vs. binary gating 비교** — 우리 D14 v1 은 bypass-when-off binary gating 입니다. TouchWorld 는 상시 잔차로도 교란 강건성을 얻으므로, `system0_activation ∈ {always_on_residual, binary_gated}` 를 Phase 1 cube 회전에서 직접 대조할 falsifier 후보입니다.
- **D22 — EgoTouch 를 촉각 사전학습 corpus 후보로 등록** — Tactile World Model 이 EgoTouch 사전학습 없이는 접촉 prior 를 못 얻었을 가능성이 높으므로, 우리 egocentric-centric corpus 결정(D22 OPEN)에 tactile 축 corpus 로 EgoTouch 를 P0 스카우팅 큐에 올립니다.
- **주의 — P2 이미지형 촉각은 채택 아닌 대조군으로** — image-form tactile 은 우리 D11 per-finger 토큰 결정과 대립하므로, 성능이 좋더라도 우리 identity(접촉 의미의 per-finger 귀속 보존)를 포기하는 대가를 명시적으로 측정한 뒤에만 고려합니다.

---

## ⚠️ 먼저 검증할 실패 모드

우리 스택(Sharpa/xhand + π0/π0.5 백본 + Isaac System0)으로의 전이가 깨질 이유를, 싼 점검부터:

1. **(가장 싼) 액션 차원·부분공간 정의 불일치** — TouchWorld 는 Wuji 120-dim(2×48 arm-hand + 9 head + 15 reserved) 위에서 58-dim 잔차를 정의합니다. 우리 Sharpa(22-DOF, wrist DOF 없음)는 arm-hand 분할·wrist pose 블록 정의가 달라, 잔차 부분공간을 그대로 옮기면 무의미합니다. 첫 점검: 우리 액션 스펙에서 "접촉 민감 축"을 손으로 지정 가능한지, wrist DOF 부재가 wrist-pose 잔차 전제를 깨는지 확인.
2. **촉각 센서 표현형 불일치** — nominal 브랜치는 촉각을 *이미지* 로 렌더합니다. Sharpa Deform Map(~320×224 vision-based)은 이미지화가 자연스럽지만, xhand·in-house 손의 matrix/저차원 촉각은 TRT 의 modality-specific 인코더(conv / Fourier+MLP)를 재설계해야 합니다. 점검: 우리 센서 출력이 image-form 으로 손실 없이 렌더되는지.
3. **EgoTouch 사전학습 부재 시 world model 붕괴** — Tactile World Model 의 접촉 prior 는 EgoTouch(인간 dense palm pressure) 사전학습에서 옵니다. 우리 촉각 레이아웃(fingertip Deform Map)은 EgoTouch palm pressure 와 layout 이 달라, 논문의 "image-form shared interface" 로 bridge 되는지 불확실. 점검: EgoTouch pressure map 과 우리 fingertip 촉각을 같은 visual-tactile grid 로 변환했을 때 domain gap 크기.
4. **별도 5B world model 의 실시간성** — Wan2.2-TI2V-5B 를 서브태스크 변경 시에만 호출해 비용을 숨기지만, 우리 System0 목표는 sub-policy-loop 반응 속도입니다. world model 이 예측 경로(느림)에 있으므로 System0(빠름)와 시간척도가 다르나, 우리 하드웨어에서 5B 모델 refresh 지연이 서브태스크 전이 순간 제어를 얼마나 지연시키는지 측정 필요.
5. **분리 학습의 오차 누적** — 4단계 분리 학습은 World Model 서브골 부정확(Contact IoU 52.7%)이 nominal 정책으로 전파될 때 완충이 없습니다. 우리 태스크(in-hand 회전)는 접촉 예측 오차에 더 민감할 수 있어, 서브골 없이(current-obs-only)와의 성능차를 먼저 재 우리 태스크에서 예측 경로가 순이득인지 확인.
6. **residual-on-frozen-VLA 의 우리 identity 상한** — 우리 identity 는 frozen VLA 위 residual 의 성능 상한을 경계합니다. TRT 가 교란 강건성을 주더라도 nominal VLA 분포 밖 손 동작은 못 만드므로, dexterous 회전·도구 조작 같은 우리 flagship 태스크에서 residual 층이 정작 필요한 큰 접촉 재파지를 못 낼 위험. 점검: 잔차 크기 분포가 nominal std 대비 얼마나 큰지(작으면 국소 보정만, 크면 분포 이탈).

---

## 💡 컨텍스트 제안

- **P0 §5 / D25** — **EgoTouch**(동기화 egocentric·wrist 영상 + bimanual hand pose + dense bilateral palm pressure, 인용 [34])를 tactile/force 데이터 스카우팅 후보로 Tracked Literature 에 추가 검토 제안. 인간 촉각 사전학습→로봇 미세조정 recipe 의 실증 corpus.
- **P5 §5** — **TouchWorld** 를 "관측 공간(촉각 이미지) 예측 · 별도 대형 비디오 world model · subtask-conditioned" 축의 대조 데이터 포인트로 Tracked Literature 에 추가 검토 제안(우리 D29 auxiliary-head / D30 latent 결정의 반례 arm).
- **P3 §5** — **TouchWorld(TRT)** 를 "RL 없는 residual imitation 반응층" 사례로, DexSynRefine(residual RL) 대비 비교군으로 추가 검토 제안.
- 위는 사람 검토용 제안이며 `context/` 파일은 수정하지 않았습니다.

---

> 💡 base 매핑은 `/implement-design analysis/2607.07287/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
