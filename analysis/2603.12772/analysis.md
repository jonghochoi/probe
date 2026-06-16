# Paper Analysis — PVI: Plug-in Visual Injection for Vision-Language-Action Models

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | PVI: Plug-in Visual Injection for Vision-Language-Action Models |
| 저자 | Zezhou Zhang, Songxin Zhang, Xiao Xiong, Junjie Zhang, Zejian Xie, Jingyi Xi, Zunyao Mao, Zan Mao, Zhixin Mai, Zhuoyang Song, Jiaxing Zhang (Lionrock AI Lab, China Merchants Group) |
| 링크 | [arXiv:2603.12772](https://arxiv.org/abs/2603.12772) |
| 발행일 / 버전 | 2026-03-13 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-16 |
| 관련 Pillar | P2, P4, P5 |
| 태그 | vla-arch, peft, flow-matching |

---

## 🧭 한 줄 요약 (TL;DR)

PVI 는 사전학습된 VLA 의 flow-matching action expert(DiT)를 **얼리고**, 그 옆에 **zero-init 잔차 경로**로 보조 시각 표현(특히 V-JEPA2 의 시간적 비디오 특징)을 layer 마다 주입하는 encoder-agnostic plug-in 모듈입니다. 단일-stage fine-tuning 만으로 GR00T N1.5 baseline 대비 RoboTwin 2.0 양손 조작에서 평균 성공률을 +24pp(단일-task) 끌어올리고, **시간적 특징(V-JEPA2) > 정적 특징(DINOv2)** 임을 통제 실험으로 보입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — VLM + flow-matching action expert 형태의 VLA 에서, VLM 임베딩 `z_vl` 이 action expert 에 도달하는 유일한 시각 채널인데, 이 임베딩이 세밀한 기하 단서와 시간 정보를 잃어버려 정밀 양손 조작의 병목이 됩니다.
- **기존 접근의 한계** — 보조 시각 특징을 주입하는 선행 연구는 (a) 정적 공간 표현에만 집중하거나, (b) 시간 입력을 수용하려고 백본/인터페이스를 대대적으로 개조해야 하여, 시간 정보가 과소 탐구된 채 남아 있습니다.
- **본 논문의 가설** — frozen action expert 에 보조 시각 표현을 **behavior-preserving(zero-init)** 잔차로 주입하면, 사전학습 지식을 망치지 않고 단일-stage fine-tuning 만으로 일관된 이득을 얻을 수 있으며, 그중 **시간적(비디오) 특징이 정적 특징보다 더 중요**하다.
- **왜 지금 중요한가** — VLM + flow-matching expert 조합이 언어-조건 조작의 강력한 패러다임으로 자리잡은 지금, 백본을 재학습하지 않고 표현을 보강하는 **가볍고 plug-and-play 한** 방법은 실용적 레버가 됩니다.

---

## 🧩 핵심 기여

- **PVI 모듈** — 사전학습 action expert 에 붙는 경량 plug-in: frozen 보조 encoder → zero-init projection → action expert 의 **trainable copy branch** → zero-init 잔차로 main DiT 의 매 layer 에 주입. 백본 수정·재사전학습 불필요.
- **Encoder-agnostic 인터페이스** — 보조 encoder `E` 에 어떤 제약도 두지 않아, 시간적(V-JEPA2)·정적(DINOv2) 표현을 동일 경로로 갈아끼우는 **통제 비교**가 가능합니다.
- **주입 메커니즘 비교 연구** — Concat / ControlNet-style / ReferenceNet-style / ControlVLA-style 4개 대안 대비 PVI 의 dual-conditioning + layer-wise zero-init 잔차가 동일 데이터·예산에서 가장 큰 이득을 줌을 실증.
- **표현 차원의 발견** — 시간적 비디오 특징(V-JEPA2)이 강한 정적 이미지 특징(DINOv2)을 능가하며, 다단계·상태추적·협응 task 에서 격차가 가장 큼을 보임.
- **실로봇 검증** — Airbot 양팔 플랫폼에서 8단계 long-horizon 양손 천(deformable) 접기를 단일 PVI 정책으로 closed-loop 수행.

---

## 🔑 기술 키워드

- **Plug-in Visual Injection (PVI)** — frozen 정책 옆에 붙여 보조 시각 정보를 "끼워넣는" 콘센트 같은 모듈. 본 논문의 핵심 기여 그 자체.
- **Flow-matching action expert** — 가우시안 노이즈에서 목표 행동 궤적으로의 속도장(velocity field)을 학습하는 DiT 기반 연속 행동 생성기. PVI 가 주입 대상으로 삼는 base.
- **Auxiliary visual feature injection** — VLM 경로가 흘려버린 시각 정보를 action 네트워크에 직접 보태는 일반 전략. PVI 의 상위 범주.
- **V-JEPA2** — 비디오 클립에서 모션·상태 변화를 담는 시간적(temporal) 자기지도 표현. PVI 의 최선 보조 encoder.
- **DINOv2** — 단일 이미지의 경계·깊이·세밀 공간 구조를 담는 강한 정적(static) 표현. 시간 vs 정적 통제 비교의 대조군.
- **Zero-initialized residual injection** — 주입 layer 를 0 으로 초기화해 학습 시작 시점에 원본 정책과 **기능적으로 동일**하게 만드는, ControlNet 계열의 behavior-preserving 기법.
- **Copy branch (trainable DiT copy)** — main DiT 의 가중치를 복제해 보조 특징을 처리하도록 특화한 병렬 가지. 사전학습된 feature-processing prior 를 그대로 물려받음.
- **Dual conditioning** — main DiT 는 `z_vl`(VLM), copy branch 는 `z̃_aux`(보조 특징)로 조건화하는 이중 조건화 구조.
- **GR00T N1.5** — 실험의 base VLA(cross-attention 조건화 DiT action expert). PVI 가 붙는 사전학습 정책.
- **RoboTwin 2.0** — 다양한 조작 primitive 를 다루는 양손 조작 시뮬레이터. 정량 평가 환경.

---

## 🔬 방법론

### 직관

PVI 의 출발점은 "VLM 임베딩이 action expert 로 가는 유일한 시각 통로인데, 그 통로가 좁다"는 진단입니다. VLM 은 의미 추상화(언어 정렬, 장면 이해)에 최적화돼 있어 모서리·접촉면·국소 깊이 같은 기하 단서와 모션·상태전이 같은 시간 단서를 압축해 버립니다. 그러면 정밀 양손 조작에 필요한 정보가 action expert 에 닿기 전에 사라집니다.

해결책은 단순합니다. VLM 을 고치지 말고, **보조 시각 표현을 action expert 에 곧장 꽂아 넣자**는 것입니다. 다만 사전학습된 expert 의 행동을 망치지 않으려면 주입을 조심스럽게 해야 합니다. PVI 는 두 가지 장치로 이를 달성합니다. 첫째, main DiT 의 가중치를 그대로 복제한 **copy branch** 를 만들어 보조 특징을 처리시킵니다(처음부터 강한 feature-처리 prior 보유). 둘째, copy branch 가 main 으로 보내는 신호를 **0 으로 초기화된 잔차**로 더해, 학습 시작 시점에는 원본 정책과 완전히 동일하게 동작하게 합니다. 학습이 진행되며 주입 layer 가 비-0 매핑을 배워 보조 정보를 점진적으로 통합합니다.

이 설계 덕분에 백본 수정도, 재사전학습도, 다단계 학습도 필요 없습니다. frozen VLM·frozen main DiT·frozen 보조 encoder 위에서, 새로 들어온 projection·copy branch·injection layer 만 표준 flow-matching 손실로 학습합니다(보조 supervision 없음). 그리고 보조 encoder 가 무엇이든(`E` 에 제약 없음) 같은 경로로 갈아끼울 수 있어, "어떤 표현을 주입해야 하는가"를 통제 비교할 수 있게 됩니다.

### 아키텍처

![Figure 1 — PVI 개요](https://arxiv.org/html/2603.12772/x1.png)

> "Figure 1: Overview of Plug-in Visual Injection (PVI). Typical VLAs condition the VLM on static images with language, providing limited temporal context; moreover, the VLM's output representations may under-emphasize fine-grained geometric cues. PVI bypasses this bottleneck by injecting auxiliary visual representations directly into the frozen action expert via a trainable plug-in, with no backbone modification and no re-pretraining required." (§1)
(이 그림은 "VLM 경로의 시간/기하 병목" 이라는 문제 진단과, "frozen expert 에 직접 주입" 이라는 해법을 한 장으로 요약합니다.)

대상 base 는 두 부분으로 구성된 전형적 VLA 입니다 — 의미 grounding 을 맡는 VLM 백본과 연속 행동 생성을 맡는 DiT action expert.

> "Given a language instruction $`l`$ and multi-view image observations $`\{I_{v}\}_{v=1}^{V}`$, the VLM jointly encodes them into a sequence of embeddings" (§3.1)
(언어 지시 $`l`$ 과 다시점 이미지 관측을 VLM 이 함께 인코딩해 임베딩 시퀀스를 만듭니다.)

$$\mathbf{z}_{\mathrm{vl}}\in\mathbb{R}^{S\times D}$$

여기서 $`S`$ 는 시퀀스 길이, $`D`$ 는 임베딩 차원입니다. 핵심 진단은 이 `z_vl` 이 action expert 로 가는 **유일한** 시각 채널이라는 점입니다.

PVI 는 3개 구성요소로 이뤄집니다.

![Figure 2 — 아키텍처 개요](https://arxiv.org/html/2603.12772/x2.png)

> "Figure 2: Architecture overview. The frozen main DiT blocks receive semantic embeddings from a frozen VLM. A trainable DiT copy (PVI) conditions on auxiliary visual features and injects them into the main stream via zero-initialized linear projections to produce continuous actions." (§3.2)
(frozen main DiT 는 frozen VLM 의 의미 임베딩을, trainable copy(PVI)는 보조 시각 특징을 받아 zero-init 선형 projection 으로 main 흐름에 주입합니다.)

**(1) Encoder-agnostic 보조 특징 추출.** frozen encoder `E` 가 원시 관측에서 고정 차원 특징 시퀀스 $`\mathbf{z}_{\mathrm{aux}}\in\mathbb{R}^{L\times d_{E}}`$ 를 뽑고($`L`$ = 보조 시퀀스 길이, $`d_{E}`$ = encoder 특징 차원), trainable 선형 projection 이 이를 DiT 임베딩 공간으로 보냅니다.

> "We initialize $`\mathbf{W}_{\mathrm{proj}}`$ to zero so that the copy branch receives a zero conditioning signal at the start of training." (§3.3)
(projection 을 0 으로 초기화해, 학습 초기 copy branch 가 0 조건 신호를 받도록 합니다 — behavior-preserving 의 첫 장치.)

$$\tilde{\mathbf{z}}_{\mathrm{aux}}=\mathbf{z}_{\mathrm{aux}}\mathbf{W}_{\mathrm{proj}}\in\mathbb{R}^{L\times D}$$

본 논문은 두 보완적 표현 범주에 집중합니다 — **시간적 동적 표현**(비디오 클립에서, 모션 궤적·상태 진화를 인코딩해 정적 VLM 임베딩의 시간 결핍을 보완)과 **공간적 기하 표현**(이미지 관측에서, 경계·깊이·세밀 구조를 인코딩해 의미 압축으로 잃은 기하 정보를 보완).

**(2) Dual conditioning + layer-wise 주입.** copy branch 는 main DiT 의 아키텍처·조건화 메커니즘(cross-attention / AdaLN / 조건부 concat 등)을 **그대로** 유지하되, 조건 입력 `z_vl` 을 `z̃_aux` 로 치환합니다.

> "For example, GR00T N1.5 uses cross-attention layers conditioned on $`\mathbf{z}_{\mathrm{vl}}`$ alongside self-attention. In the PVI copy branch, the same cross-attention structure is retained, but its key/value inputs are replaced by $`\tilde{\mathbf{z}}_{\mathrm{aux}}`$." (§3.4)
(GR00T N1.5 의 cross-attention 구조를 copy branch 가 동일하게 쓰되, key/value 만 보조 특징으로 바꿉니다 — 다른 조건화 방식에도 같은 원리 적용.)

**(3) Zero-init 최소 개입 학습.** VLM·main DiT 를 얼리고 새 파라미터만 학습해, 초기 동작을 원본 VLA 와 동일하게 둔 뒤 보조 정보를 점진 통합합니다.

### 학습 목표 / 손실

base 의 flow-matching 정의를 그대로 따릅니다. 목표 행동 시퀀스 $`\mathbf{a}=(\mathbf{a}_{1},\ldots,\mathbf{a}_{H})`$(horizon $`H`$)와 노이즈 $`\boldsymbol{\epsilon}\sim\mathcal{N}(\mathbf{0},\mathbf{I})`$ 에 대해, flow time $`t\in[0,1]`$ 에서 보간 궤적은

$$\mathbf{a}_{t}=(1-t)\boldsymbol{\epsilon}+t\mathbf{a}$$

DiT 는 `z_vl` 조건 하에 속도장을 예측하고 표준 flow-matching 손실로 학습됩니다.

$$\mathcal{L}=\mathbb{E}_{t,\boldsymbol{\epsilon}}\Big[\big\|\hat{v}_{\theta}(\mathbf{a}_{t},t,\mathbf{z}_{\mathrm{vl}})-(\mathbf{a}-\boldsymbol{\epsilon})\big\|_{2}^{2}\Big]$$

추론 시 순수 노이즈에서 $`K`$-step Euler 적분으로 속도장을 통합해 행동을 생성합니다. **PVI 는 이 손실을 변경하지 않으며 보조 supervision 도 추가하지 않습니다** — 새 파라미터 전부가 오직 행동 예측 목표로만 학습됩니다.

**Layer-wise 잔차 주입.** main DiT 의 $`i`$-번째 블록을 $`f_{i}^{\mathrm{main}}`$, copy branch 의 대응 블록을 $`f_{i}^{\mathrm{copy}}`$ 라 하면, copy branch 는

$$\mathbf{h}_{i}^{\mathrm{copy}}=f_{i}^{\mathrm{copy}}\!\left(\mathbf{h}_{i-1}^{\mathrm{copy}},\tilde{\mathbf{z}}_{\mathrm{aux}}\right),\quad i=1,\ldots,N$$

으로 전진하고, main DiT 는 병렬로 전진하되 매 layer 에서 copy branch 의 제어 신호를 받습니다.

$$\mathbf{h}_{i}^{\mathrm{main}}=f_{i}^{\mathrm{main}}\!\left(\mathbf{h}_{i-1}^{\mathrm{main}},\mathbf{z}_{\mathrm{vl}}\right)+\mathbf{Z}_{i}\!\left(\mathbf{h}_{i}^{\mathrm{copy}}\right),\quad i=1,\ldots,N$$

> "where $`\mathbf{Z}_{i}`$ is a zero-initialized linear injection layer. This design allows auxiliary visual information to influence action generation at every layer of the DiT while preserving the pretrained main pathway." (§3.4)
($`\mathbf{Z}_{i}`$ 가 zero-init 선형 주입 layer 이며, 매 layer 에서 보조 정보가 행동 생성에 개입하되 사전학습 main 경로는 보존됩니다. 초기 상태 proprio+노이즈 행동 토큰 $`\mathbf{h}_{0}`$ 은 main 과 copy 양쪽의 공통 입력입니다.)

### 학습 셋업

> "The copy branch is initialized by copying the pretrained weights of the main DiT, providing a strong feature-processing prior from the start of training." (§3.5)
(copy branch 를 main DiT 의 사전학습 가중치로 초기화해 처음부터 강한 feature-처리 prior 를 줍니다.)

학습 대상 파라미터는 (i) projection $`\mathbf{W}_{\mathrm{proj}}`$, (ii) copy-branch 블록 $`\{f_{i}^{\mathrm{copy}}\}_{i=1}^{N}`$, (iii) injection layer $`\{\mathbf{Z}_{i}\}_{i=1}^{N}`$, (iv) embodiment-specific state/action encoder·decoder 입니다. VLM 백본·main DiT·보조 encoder `E` 는 모두 frozen. `W_proj` 와 `Z_i` 는 0 초기화로 초기 시점 원본 VLA 와의 **기능적 동일성**을 보장합니다.

평가 환경은 RoboTwin 2.0(양손 조작 시뮬레이터)이며, base 는 GR00T N1.5, 보조 encoder 기본값은 4 fps 로 샘플한 **8 frame V-JEPA2**. task 당 **50 demonstration** 으로 독립 fine-tune, **100 rollout**(무작위 초기조건)로 성공률 측정.

---

## 📊 실험 설정과 결과

### 주입 전략 비교 (단일-task, 20개 task, Table 1)

![Figure 3 — 주입 전략 비교](https://arxiv.org/html/2603.12772/x3.png)

> "Figure 3: Overview of PVI and four candidate strategies for injecting auxiliary visual features into the DiT action expert. We compare PVI (ours), which injects V-JEPA2 features via a trainable copy branch with zero-initialized injection layers, against input-level fusion (Concat), attention-level dual injection (ControlVLA-style), and parallel-branch designs with feature concatenation or residual addition (ReferenceNet- and ControlNet-style)." (§4.1)
(보조 encoder(V-JEPA2)와 학습 예산을 고정하고 "주입 방식"만 바꿔 메커니즘 효과를 격리합니다.)

| 방법 | 평균 성공률(%) | Δ vs Base(pp) |
|---|---|---|
| GR00T N1.5 (base) | 35.70 | – |
| **Ours (PVI)** | **59.70** | **+24.00** |
| Concat | 43.60 | +7.90 |
| ControlNet-style | 34.35 | −1.35 |
| ControlVLA-style | 37.00 | +1.30 |
| ReferenceNet-style | 37.40 | +1.70 |

> "The fine-tuned GR00T N1.5 baseline achieves 35.7% average success, while GR00T N1.5 + PVI reaches 59.7% (+24.0 pp). Concat provides a moderate improvement (43.6%), whereas the ControlVLA-, ControlNet-, and ReferenceNet-style variants remain close to the baseline (34.4–37.4%)." (§4.1, Table 1)
(동일 데이터·예산에서 PVI 만 큰 이득을 줍니다 — 주입 메커니즘 자체가 성패를 가른다는 핵심 증거.)

per-task 로 보면 baseline 성공률이 낮은 task 에서 이득이 특히 큽니다: beat_block_hammer 39→84, click_alarmclock 48→87, move_playingcard_away 23→84, scan_object 4→42, click_bell 46→91. 반면 ControlNet-style 은 평균이 base 보다 낮아(−1.35pp), zero-init 잔차라는 형태만으로는 부족하고 **copy branch 의 dual-conditioning(보조 특징을 조건으로 한 별도 가지)** 이 핵심임을 시사합니다.

### Encoder-agnostic 표현 비교 (10개 task, Fig 4)

| 보조 encoder | 평균 성공률(%) | Δ vs Base(pp) | 상대 향상 |
|---|---|---|---|
| Baseline (GR00T N1.5) | 39.8 | – | – |
| PVI @ DINOv2 (정적) | 56.8 | +17.0 | +42.7% |
| PVI @ V-JEPA2 (시간) | **69.4** | **+29.6** | **+74.4%** |
| PVI @ V-JEPA2 + DINOv2 | 68.9 | +29.1 | +73.1% |

> "Temporal features provide the largest improvement: GR00T+PVI@V-JEPA2 reaches 69.4% (+29.6 pp, +74.4% relative). Combining both encoders achieves 68.9% (+29.1 pp, +73.1% relative), on par with V-JEPA2 alone, suggesting that static appearance features provide little additional signal beyond what temporal features already capture." (§4.2)
(시간적 특징이 정적보다 크게 앞서고, 둘을 합쳐도 V-JEPA2 단독과 동급 — 정적 외관 정보는 시간 특징이 이미 포착한 것 이상을 거의 주지 못함.)

### 시간 컨텍스트·안정화 ablation (10개 task, Table 2)

| Variant | Frames@4fps | 평균(%) |
|---|---|---|
| Baseline (fine-tuned GR00T N1.5) | – | 39.8 |
| PVI@V-JEPA2 | 2 | 71.6 |
| PVI@V-JEPA2 | 4 | 71.8 |
| PVI@V-JEPA2 | 8 (main 설정) | 69.4 |
| PVI@V-JEPA2 | 16 | 66.6 |
| PVI@V-JEPA2 + DINOv2 | 16 | 68.9 |
| PVI@V-JEPA2 (no zero-init) | 8 | 71.8 |
| PVI@V-JEPA2 (freeze projector) | 8 | 55.3 |

- **시간 컨텍스트 길이** — 2–4 frame 이 최적(71.6–71.8%), 8→16 frame 은 수확 체감(69.4→66.6%). main 실험의 기본 8-frame 은 최적이 아니므로(격차 2.4pp) **§4.1/§4.2 의 보고 이득은 보수적**이라는 점을 저자가 명시합니다.
- **projector freeze** — 보조-to-DiT projection 을 얼리면 55.3% 로 크게 하락. 보조 encoder 가 frozen 이어도 **action expert 임베딩 공간으로의 정렬을 학습하는 것이 중요**.
- **zero-init 제거** — 최종 성공률은 71.8% 로 동등하거나 약간 높음. 그럼에도 저자는 behavior-preserving 초기화·보수적 점진 통합을 위해 main 실험에서 zero-init 을 유지(성능보다 안정성 명분).

### Multi-task 확장성 (4.4) · 실로봇 (4.5)

> "On the 20-task mixture, PVI increases average success from 61.15% to 69.15% (+8.00 pp). On the more challenging 50-task mixture, PVI yields a consistent gain from 61.32% to 63.56% (+2.24 pp), winning on the majority of individual tasks." (§4.4)
(단일 정책이 여러 skill 을 공유하는 multi-task 에서도 이득이 유지되나, task 수가 늘수록 평균 이득은 +8.00→+2.24pp 로 축소됩니다.)

실로봇은 Airbot 양팔 플랫폼에서 long-horizon 양손 천 접기 — 8개 순차 subtask(소매 집기, 형상 조정, 대칭 접기, edge-to-edge 반접기, tension 제어 sliding, 비대칭 anchoring, 최종 접기, lift-and-stack)를 **단일 PVI 정책**이 task-specific engineering·수동 reset 없이 closed-loop 수행. 정성적 실용성 검증.

---

## ⚖️ 한계

- **저자 명시: 8-frame 기본값이 비최적** — main 실험이 2–4 frame 최적(71.8%) 대신 8 frame(69.4%)을 써 보고 이득이 보수적. 뒤집어 보면 **하이퍼파라미터(temporal context) 민감도**가 있어, 새 task·embodiment 마다 frame 수를 다시 튜닝해야 할 수 있습니다.
- **저자 명시: zero-init 의 성능 이득 부재** — no zero-init(71.8%)이 zero-init(69.4%)보다 오히려 높습니다. zero-init 은 성능이 아니라 "안정적 초기화" 라는 정성 명분으로만 정당화되며, 핵심 셀링포인트(behavior preservation)가 정량 우위로 뒷받침되지 않는 것은 약점입니다.
- **추론 비용** — copy branch 가 main DiT 의 **전체 복제본**이라 action expert 파라미터·연산이 사실상 2배. 게다가 보조 encoder(V-JEPA2)의 비디오 forward 가 매 step 추가됩니다. "lightweight" 는 학습 측(백본 frozen) 표현이며, 추론 측 부담은 본문(부록 cost-stats)에서 텍스트로 확보되지 않았습니다.
- **multi-task 이득의 축소** — 50-task 에서 +2.24pp 로 줄어, 공유 정책 regime·task 다양성이 커질수록 보조 주입의 한계 효용이 떨어짐을 시사. 일반화 폭이 넓어질수록 이득이 희석되는 메커니즘은 미해명.
- **실로봇 검증의 정성성** — 단일 task(천 접기), baseline 과의 정량 비교·반복 통계 없는 데모. 일반화 주장의 근거로는 약합니다.
- **인용 인덱스 손상** — 본문이 `[ref14]`, `[ref23]` 식 미해소 참조로 렌더되어, ControlVLA·기하 grounding 선행 연구의 정확한 출처 대조가 제한됩니다(HTML 추출 한계).

---

## ♻️ 재현성

- **코드/모델** — v1 본문·초록에 공개 저장소(GitHub/HF)·프로젝트 페이지 링크가 **확인되지 않습니다**(LaTeXML feedback 링크만 존재). 라이선스 CC BY 4.0(논문).
- **데이터/환경** — 시뮬레이션은 공개 RoboTwin 2.0(양손 시뮬레이터), base 는 공개 계열 GR00T N1.5, 보조 encoder 는 공개 V-JEPA2·DINOv2. task 당 50 demo / 100 rollout 프로토콜은 명시.
- **하드웨어** — 실로봇은 Airbot 양팔 플랫폼. 학습 하드웨어·step 수·optimizer 등 세부는 부록(0.A.2 Training Setup / 0.A.3 Cost-Related Statistics)에 있으나 HTML 본문 텍스트로는 확보되지 않았습니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P2(structured multimodal observation fusion) — 일차 연관.** PVI 는 정확히 P2 의 thesis("VLM 경로가 흘려버린 시각 정보를 action 측에서 보강")를 구현합니다. 특히 D9(action/dynamics-aware vision encoder)와 정면으로 맞닿습니다 — 시간/동적 표현(V-JEPA2)이 정적 encoder(DINOv2)를 능가한다는 통제 결과는, "generic 정적 stem 보다 dynamics-aware encoder 를 선호" 하라는 D9 의 명제에 강한 외부 증거입니다. D10(fusion beyond concat)에도 직접 기여 — Concat baseline(+7.90)을 dual-conditioning copy-branch 주입(+24.00)이 크게 앞서, "flat-concat 초월" 의 정량 근거를 제공합니다.
- **P4(pretraining for data-efficient adaptation) — 이차 연관.** PVI 의 frozen-backbone + zero-init 잔차는 D19(adaptation range = freeze/PEFT)와 D20(prior-preservation strategy)의 구체적 인스턴스입니다. 다만 P4 Identity 는 "preservation 은 headline 이 아닌 하위 레버" 라고 못박으므로, PVI 는 P4 의 **부수 레버**를 정교화하는 사례이지 P4 의 핵심(lineage × corpus × recipe)을 건드리지는 않습니다.
- **P5(world model) — 보조 연관.** V-JEPA2 는 P5 §5 에 pin 된 JEPA 계열 latent-prediction 표현입니다. PVI 는 V-JEPA2 를 **frozen feature extractor** 로만 쓰므로 D29(integration architecture)·D31(action conditioning) 의 "co-trained dynamics prior" 와는 다르지만, "시간적/JEPA 표현이 조작에 유효" 라는 P5 의 베팅을 측면 지지합니다.
- **Identity 긴장 (중요).** PVI 는 "**frozen VLA 위에 잔차 모듈을 볼트로 붙인다**" 는 구조로, MASTER Identity 의 *Antagonist A*(VLA-output correction/residual module — distribution-bounded, 모션 패턴 바뀔 때마다 재학습)와 형태가 겹칩니다. 단, PVI 는 출력단 post-hoc 보정이 아니라 **매 layer 내부에 주입**하므로 P1 anti-topic 의 가장 나쁜 형태(출력 분포에 갇힌 보정)는 아닙니다 — 그래도 "action expert 를 얼리고 옆가지로 능력을 더한다" 는 점에서 우리의 "dexterity 는 VLA-level 에서 직접 tackle" 논제와는 방향이 다릅니다. 경쟁자라기보다 **대조 설계**로 읽는 것이 맞습니다.

---

## ✨ 핀 논문 대비 델타

- **vs DynaFLIP (P2 D9 핀, action/dynamics-aware encoder).** DynaFLIP 은 dynamics-aware **encoder 자체**를 제안하는 반면, PVI 는 encoder 를 고정한 채 **그 표현을 frozen action expert 에 주입하는 경로**(copy branch + zero-init 잔차)를 제안합니다. 둘은 보완적 — PVI 의 encoder-agnostic 슬롯에 DynaFLIP 을 꽂아볼 수 있습니다. PVI 의 진짜 새로움은 "어떤 encoder 인가" 가 아니라 "어떻게 주입하는가" 입니다.
- **vs ControlVLA (논문 내 baseline).** ControlVLA 는 attention 단에서 object-centric 특징을 dual cross-attention 으로 주입합니다. PVI 는 같은 zero-init 정신을 쓰되 **블록 전체를 복제한 copy branch + layer-wise 잔차** 로 일반화하고, 본 실험에서 ControlVLA-style(+1.30) 대비 압도적 우위(+24.00)를 보입니다.
- **vs ConSFT (P4 D20 핀, conservative adaptation).** ConSFT 가 손실/정규화로 prior 를 보존한다면, PVI 는 **아키텍처적(zero-init 잔차)** 으로 보존합니다. 다만 PVI 의 ablation 은 zero-init 의 성능 이점이 없음을 보여, "preservation = 정량 이득" 이라는 가정에는 오히려 신중함을 더합니다.

---

## ⚙️ 의사결정 함의

- **P2/D9 — 보조 encoder 는 dynamics-aware(temporal) 를 기본으로.** PVI 의 통제 결과(V-JEPA2 69.4% > DINOv2 56.8%, 결합해도 동급)는 우리 observation 스택에서 **정적 기하 encoder 단독보다 시간적 비디오 encoder 를 우선** 채택할 근거입니다. config 상으로는 보조 표현 슬롯의 기본값을 `aux_encoder = v-jepa2`, `n_frames ∈ {2,4}` (최적 구간), `fps = 4` 로 두는 결정.
- **주입 메커니즘 키 = dual-conditioning copy branch.** 만약 우리가 frozen 표현을 action expert 에 보탤 일이 생기면, 단순 `concat` 토큰 추가(+7.90)나 단일 zero-init 잔차(ControlNet-style, −1.35)가 아니라 **보조 특징을 조건으로 한 별도 copy branch + layer-wise zero-init 잔차** 가 정답에 가깝다는 강한 신호.
- **prior-preservation 은 안정성 명분으로만.** zero-init vs no-zero-init 동률(69.4 vs 71.8)은, 우리가 D20 에서 zero-init 류 보존을 채택할 때 **"성능을 위해서"가 아니라 "초기 behavior 동일성·학습 안정성"** 이라는 목적을 분명히 해야 함을 시사. 성능이 목표면 보존 제약을 풀어보는 ablation 을 항상 함께.
- **반례로서의 가치(P1).** PVI 는 "frozen expert + 옆가지" 설계의 상한 사례입니다. 우리 Body/Hand split 논제를 검증할 때 **"왜 우리는 action expert 를 얼리지 않고 직접 설계하는가"** 의 대조군 baseline 으로 PVI-style 주입을 세울 수 있습니다.

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 확인) 추론 2배 비용이 우리 제어율 예산에 맞는가.** copy branch 가 DiT 전체 복제 + 매 step V-JEPA2 비디오 forward 라, System1 루프율(특히 Hand expert 의 고빈도 제어)에서 latency 가 초과할 수 있습니다. 먼저 forward 시간만 프로파일해 보고 판단.
- **base 의존성 — cross-attention 조건화 가정.** PVI 는 main DiT 의 조건화 메커니즘을 copy branch 가 "그대로 복제" 한다고 가정합니다. 우리 π0/π0.5 계열(AdaLN/conditional-concat 등)에서 copy-branch 치환이 GR00T 의 cross-attention 만큼 깔끔히 떨어질지 미지수 — 1개 task 에서 copy-branch 가 실제로 학습되는지(injection layer norm 이 0 에서 벗어나는지) 먼저 확인.
- **temporal encoder ↔ 양손/손가락 정밀도 mismatch.** V-JEPA2 의 이득은 RoboTwin 양손 task(다단계 협응)에서 큽니다. 우리의 **per-finger 접촉·tactile** 정밀도 문제는 비디오 모션 표현이 아니라 촉각/force 표현이 필요할 수 있어, "시간 표현 주입" 의 이득이 dexterous hand 영역으로 전이될지 불확실 — in-hand reorientation 류 task 에서 별도 검증.
- **multi-task 희석.** 50-task 에서 +2.24pp 로 축소된 패턴이, 우리의 generalist(다양한 functional grasping) 목표에서 이득을 잠식할 위험. task 수를 늘린 mixture 에서 이득 곡선이 평탄해지는지 미리 측정.
- **prior-preservation 무효 가능성.** zero-init 이 성능 이득이 없다는 ablation 은, 우리가 이를 forgetting 방지용으로 차용할 때 **실제로 VLM/π prior 의 일반화가 보존되는지**(보존 metric 부재)를 별도로 측정해야 함을 경고. 성공률만으로는 preservation 을 입증하지 못합니다.

---

## 💡 컨텍스트 제안

- **P2 §5 트래킹 후보** — PVI 를 D9/D10 의 "주입 경로(injection mechanism)" 측면 증거로 off-pin 트래킹 제안. 단, PVI 자체는 encoder 가 아니라 **주입 방식** 기여이므로, DynaFLIP(encoder) 핀과는 다른 축(주입)으로 기록하는 것이 정확합니다.
- **P4 D20 노트** — "zero-init/behavior-preserving 잔차" 가 성능이 아닌 안정성 명분이라는 PVI ablation 을, prior-preservation 채택 시 "보존 metric 을 반드시 함께 측정" 하라는 caveat 의 근거로 기록 제안.
- 핀 교체 제안 없음(P2 의 핵심 핀은 encoder 계열이 유지).

> 💡 base 매핑은 `/implement-design analysis/2603.12772/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
