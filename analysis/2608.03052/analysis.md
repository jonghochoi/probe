# Paper Analysis — How Should Vision-Language-Action Models Use Proprioceptive State?

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | How Should Vision-Language-Action Models Use Proprioceptive State? |
| 저자 | Yiren Zhao, Ziyang Chen, Ziyang Rao, Pengteng Li, He Zhang, Weiyu Guo, Yandong Guo, Rushi Dai |
| 링크 | [arXiv:2608.03052](https://arxiv.org/abs/2608.03052) |
| 발행일 / 버전 | 2026-08-04 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-08-12 |
| 관련 Pillar | P2, P1, P4, P0 |
| 태그 | vla-arch, flow-matching |

<!-- 본문 확보 이력 (verbatim):
       1. curl --fail -sS "http://export.arxiv.org/api/query?id_list=2608.03052"  → exit 0 이나 응답 0 byte
       1b. curl --fail -sS "https://export.arxiv.org/api/query?id_list=2608.03052" → HTTP 200 (메타/초록 확보)
       2. curl --fail -sS "https://arxiv.org/html/2608.03052"                     → HTTP 200 (281,780 byte, 본문 + 부록 A/B/C 전문)
     전문(arXiv HTML) 확보이므로 (B) 섹션에 (본문 미확보) 마커를 붙이지 않습니다.
     코드/프로젝트 페이지 URL 은 본문·초록 어디에도 없어 링크 행은 arXiv 만 둡니다. -->

---

## 🧭 한 줄 요약 (TL;DR)

VLA 가 관습적으로 아무 데나 꽂아 넣던 proprioceptive state 를, 백본·데이터·액션 표현·평가 프로토콜을 전부 고정한 채 **표현(이산 vs 연속) × 시간 깊이(K=1–96) × 주입 위치(VLM 측 vs 액션 측)** 세 축으로 분해해 통제 비교한 연구입니다. 결론은 단일 최적 인터페이스가 없다는 것과, **현재 프레임 1장은 VLM 쪽에, 짧은 상태 히스토리는 액션 전문가 쪽에 넣으라**는 시간 예산 의존적 라우팅 규칙입니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 최근 VLA 는 거의 전부 로봇 proprioceptive state 를 입력으로 받지만, 그 배선 방식이 서로 호환되지 않습니다(텍스트 프롬프트 직렬화 / VLM prefix 투영 / 액션 전문가 직결). 무엇이 왜 나은지에 대한 통제된 근거가 없습니다.
- **기존 접근의 한계** — 각 설계가 서로 다른 시스템 안에 실려 나오기 때문에, 보고된 수치가 state 인터페이스 효과와 백본·사전학습·데이터·평가 프로토콜 효과에 뒤엉켜 있습니다. 같은 state 신호를 인터페이스·히스토리 깊이·주입 경로를 가로질러 옮겨 본 선행 연구가 없습니다.
- **왜 유독 state 만 미검증인가** — 시각과 언어는 VLM 안에서 대규모로 사전학습되어 있지만 proprioception 은 그런 사전학습이 없습니다. 그래서 VLA 입력 중 가장 덜 검토된 축으로 남았습니다.
- **본 논문의 가설** — state 설계는 "쓴다/안 쓴다"의 이분법이 아니라 표현·시간 깊이·주입 위치의 3축 설계 공간이며, 다른 모든 것을 고정하면 각 축의 효과를 성공률 차이로 귀속시킬 수 있다는 것입니다.
- **왜 지금 중요한가** — state 를 둘러싼 근거가 양방향으로 끌립니다. 정렬 감독·크로스 임보디먼트 정규화·장기 과제 메모리로 쓰자는 흐름과, 순진하게 융합된 state 가 시각을 압도해 실패를 못 보게 만든다는 경고가 동시에 나오고 있습니다.

> "At the same time, several studies warn in the opposite direction: naively fused state can dominate vision, letting a policy “complete” a task from its internal progress while ignoring visual failure (Li et al. 2026b), can suppress visual learning around motion-phase transitions (Lu et al. 2026), and can serve as an action-correlation shortcut in behavioral cloning (De Haan et al. 2019; Wen et al. 2020)." (§3.2)
(state 를 잘못 쓰면 정책이 시각 대신 자기 진행 상황만 보고 "다 했다"고 선언하거나, 행동과 상관된 지름길을 학습합니다. 즉 state 는 공짜 입력이 아니라 부작용을 가진 조건화이며, 이 논문이 이득과 손해가 어디서 갈리는지를 통제 실험으로 확정하려는 이유입니다.)

---

## 🧩 핵심 기여

- **3축 통제 실험 프레임워크** — $`\pi_{0.5}`$ 를 고정 테스트베드로 삼아 백본·학습 데이터·액션 표현·평가 프로토콜을 모두 고정하고, state 의 표현 / 히스토리 길이 $`K`$ / 주입 위치만 변인으로 남긴 비교 스캐폴드를 구축했습니다.
- **5개 대표 인터페이스의 동일 조건 구현** — 선행 연구에서 추출한 discrete state prompt(sp), VLM prefix(vp), action prefix(ap), state expert(se), feature modulation(fm) 을 하나의 코드베이스에서 구현해 비교했습니다.
- **계층적 평가 프로토콜** — RoboCasa365 위에서 45개 atomic 태스크를 제어 의미론 기준으로 사전 분할한 3개 패밀리(A 재배치 / B 관절 물체 / C 정밀 조작) + 20개 composite 태스크로 구성했습니다. 사후 성능 기준 분할이 아니라는 점이 핵심입니다.
- **RQ1 — 태스크 무관 최적 인터페이스는 없다** — 매크로 평균으로는 다섯 인터페이스 모두 no-state 를 상회하지만, 패밀리 수준에서 순위가 뒤집힙니다.
- **RQ2 — 히스토리의 유효 구간은 유계다** — 짧은 히스토리는 돕고 긴 원시 히스토리는 해칩니다. 슬롯 수를 맞춘 repeat-current 대조군으로, 이득이 조건화 용량이 아니라 진짜 시간 변이에서 온다는 것을 분리했습니다.
- **RQ3 — 주입 위치는 시간 예산에 따라 뒤바뀐다** — $`K{=}1`$ 이면 VLM 측, $`K{=}8`$ 이면 액션 측이 최적이라는 교차(crossover)를 두 state 표현·두 태스크 스위트에서 재현하고, 고정 체크포인트 프로브로 데이터 흐름 해석을 붙였습니다.

---

## 🔑 기술 키워드

- **Proprioceptive state** — 로봇 자신의 운동학적 형상(관절각, 엔드이펙터 자세, 그리퍼 개도). 출력 액션과 **같은 연속 물리 공간**에 사는 유일한 정책 입력이라는 점이 시각·언어와 결정적으로 다릅니다.
- **State interface** — 같은 state 신호를 모델 어디에, 어떤 형태로 꽂을지의 배선 설계. 이 논문의 주된 변인이며 sp / vp / ap / se / fm 다섯 가지로 대표화됩니다.
- **Action Prefix** — (ap) 연속 state 토큰을 노이즈 액션 토큰 앞의 causal action suffix 에 놓아, 액션 전문가의 속도장 예측에 매 디노이징 스텝마다 직접 참여시키는 경로. state→action 최단 경로입니다.
- **VLM Prefix** — (vp) 이미지·언어 토큰 뒤 양방향 VLM prefix 에 state 토큰을 삽입해, 먼저 멀티모달 문맥 모델링에 참여시키고 그 문맥을 통해 간접적으로 액션에 영향을 주는 경로.
- **Slot-matched control** — 8프레임 히스토리 대신 **현재 프레임을 8번 복제**해 넣는 대조군. 토큰 수·인터페이스·초기 노이즈를 모두 동일하게 유지하므로, 성능 차이를 "슬롯이 늘어서"가 아니라 "시간 변이가 있어서"로 귀속시키는 장치입니다.
- **State Prompt** — (sp) 현재 state 각 차원을 256 bin 으로 양자화해 기존 토크나이저로 직렬화, 약 66개 프롬프트 토큰으로 언어와 같은 임베딩 공간에 넣는 방식. 학습 파라미터가 0개인 대신 연산이 가장 비쌉니다.
- **State Expert** — (se) VLM 과 액션 전문가 옆에 state 전용 트랜스포머 스택을 두어, 자체 시퀀스 모델링 경로를 갖게 하는 최대 용량 설계.
- **Feature Modulation** — (fm) state 를 시퀀스 토큰이 아니라 별도 조건화 메모리로 두고, 액션 전문가의 **매 레이어**가 cross-attention 으로 읽어 per-feature scale $`\gamma`$ 와 shift $`\beta`$ 를 예측해 액션 특징을 변조하는 FiLM 계열 방식.
- **State history depth** — 조건화에 쓰는 최근 state 프레임 수 $`K`$ . 이 논문은 1에서 96까지 스윕해 $`K{=}8`$ 을 실용적 동작점으로 제시합니다.
- **Paired task-bootstrap interval** — 정렬된 태스크를 재표집해 두 고정 체크포인트 간 차이의 95% 구간을 얻는 절차. 최적화 분산이 아니라 평가·태스크 표집 불확실성을 재는 지표라는 점을 저자들이 명시합니다.

---

## 🔬 방법론

### 직관

이 논문은 새 모델을 제안하지 않습니다. 대신 "로봇이 자기 팔이 지금 어디 있는지를 아는 정보를, 신경망 어느 지점에 꽂아야 하는가"라는, 지금까지 각 팀이 관행적으로 결정해 온 배선 문제를 실험으로 확정하려 합니다. 이 질문이 실험적으로 의미를 가지려면 다른 모든 것이 고정되어야 하므로, 저자들은 백본 $`\pi_{0.5}`$ , 학습 데이터, 액션 표현, 평가 시드 스케줄까지 전부 묶어 두고 state 배선만 바꿉니다.

배선 후보는 크게 두 갈래입니다. 하나는 state 를 **VLM 쪽**에 넣어 이미지·언어와 함께 멀티모달 문맥을 만드는 방식이고, 다른 하나는 **액션 전문가 쪽**에 넣어 액션 생성 계산에 직접 참여시키는 방식입니다. 전자는 "장면을 해석할 때 내 몸 상태도 같이 고려하라"에 가깝고, 후자는 "지금 낼 명령을 만들 때 내 몸 상태를 직접 참조하라"에 가깝습니다. 다섯 인터페이스는 이 두 갈래를 표현 형식(이산 텍스트 토큰 vs 연속 임베딩)과 용량(전용 트랜스포머를 붙일 것인가, 변조 계층으로 쓸 것인가)으로 세분한 것입니다.

세 번째 축은 시간입니다. 대부분의 VLA 는 현재 프레임 1장만 씁니다. 저자들은 최근 $`K`$ 프레임을 넣어 보되, 히스토리를 늘리면 조건화 슬롯 수도 함께 늘어난다는 교란을 피하기 위해 **현재 프레임을 같은 개수만큼 복제한 대조군**을 항상 짝지어 학습·평가합니다. 이 장치가 없으면 "히스토리가 좋다"는 결론이 사실은 "토큰이 많으면 좋다"일 수 있습니다.

마지막으로, 각 인터페이스는 파라미터 수와 연산량이 서로 다릅니다. 저자들은 이를 숨기지 않고, 다섯 인터페이스 비교가 "추상적 주입 지점"이 아니라 **용량과 계산 경로까지 포함한 완결된 시스템**의 비교임을 명시한 뒤, 한계 연산량을 해석적으로 계산해 부록에 붙였습니다.

### 문제 설정

의사결정 시점 $`t`$ 에서 정책은 시각 관찰 $`o_{t}\in\mathcal{O}`$ , 언어 지시 $`\ell\in\mathcal{L}`$ , 그리고 최근 $`K`$ 스텝의 순서 있는 state 윈도우를 받습니다 (식 1):

$$S_{t}^{(K)}=\left(s_{t-K+1},\ldots,s_{t}\right),\qquad s_{t}\in\mathbb{R}^{d_{s}},$$

이 조건 아래 정책 $`\pi_{\theta}`$ 는 길이 $`H`$ 의 연속 액션 청크를 생성합니다 (식 2):

$$\hat{\mathbf{a}}_{t:t+H-1}=\pi_{\theta}\!\left(o_{t},\ell,S_{t}^{(K)}\right)\in\mathbb{R}^{H\times d_{a}},$$

여기서 $`K{=}1`$ 은 현재 스텝만 쓴다는 뜻입니다. 중요한 것은 예측 대상 자체는 인터페이스 간에 동일하다는 점입니다 — 다섯 설계는 오직 $`S_{t}^{(K)}`$ 를 **어떻게 표현하고 어디에 주입하는가**에서만 갈립니다.

> "All five interfaces share the same action-generation objective, data pipeline, and training recipe; they differ only in how the same state window is represented and where it enters the policy—the VLM prefix, the action prefix, a dedicated state stream, or feature modulation." (§4.1)
(통제 실험의 핵심 계약입니다. 손실 함수와 데이터 파이프라인이 같으므로 성공률 차이는 배선에 귀속됩니다. 다만 저자들도 인정하듯 파라미터 수와 계산 경로는 같지 않으므로, 비교 대상은 "주입 지점"이 아니라 "완결된 state 조건화 시스템"입니다.)

### 아키텍처

![Figure 1 — state design space and evaluation suite](https://arxiv.org/html/2608.03052/vla-architecture-figure_v2.png)

> "Figure 1: Overview of the state design space and evaluation suite. (1) State representation: robot state is represented either as a discrete current-state prompt or as continuous temporal tokens. (2) Shared VLA scaffold: multi-view observations and the task instruction enter the vision–language backbone, whose context conditions the action expert. (3) State interfaces: we compare a discrete state prompt, a continuous VLM prefix, a dedicated state expert, an action prefix, and feature modulation. The systems are evaluated on rearrangement (A), articulation (B), precision knob/switch control (C), and multi-stage composite tasks." (§1)
(공유 스캐폴드는 하나이고 그림의 (3) 블록만 갈아 끼운다는 이 논문의 실험 설계 전체가 한 장에 담겨 있습니다. 오른쪽 A/B/C + composite 구획은 결과 해석의 단위이기도 합니다.)

**state 표현 (§4.2).** 원시 state 프레임의 구성부터 짚어야 결과 해석이 흔들리지 않습니다.

> "Each raw state frame $`s_{q}\in\mathbb{R}^{16}`$ contains the end-effector position and quaternion in the base frame, the mobile-base position and quaternion in the world frame, and two gripper joint positions." (§4.2)
(16차원 = EEF 위치 3 + 쿼터니언 4 + 모바일 베이스 위치 3 + 쿼터니언 4 + 그리퍼 관절 2. 즉 여기서 말하는 state 에는 **월드 프레임 베이스 자세**가 섞여 있습니다.)

> "We keep the shorthand “proprioceptive state” below, but the base pose also carries world-frame localization, so its effect cannot be read as purely internal motor feedback." (§4.2)
(저자들이 스스로 단 경고입니다. 이 논문의 "state 가 도움이 된다"는 결과 중 일부는 순수한 자기수용 감각이 아니라 전역 위치 정보의 효과일 수 있으며, 고정 베이스 스택으로 옮길 때 그대로 재현되지 않을 수 있습니다.)

discrete state prompt 를 제외한 모든 연속 인터페이스는 수치 내용·시간 순서·히스토리 길이가 동일한 state 시퀀스를 받고, 각 프레임은 독립적으로 2층 투영기를 통과해 하나의 연속 state 토큰이 됩니다 (식 3):

$$h_{i}=\phi_{2}\!\left(\mathrm{Swish}\!\left(\phi_{1}(s_{i})\right)\right),$$

여기서 $`\phi_{1}`$ 은 프레임워크의 고정 32차원으로 zero-pad 된 state 입력을 폭 $`d`$ 로 끌어올리고, $`\phi_{2}`$ 는 그 폭을 유지합니다. $`d{=}2048`$ 은 VLM prefix 용, $`d{=}1024`$ 는 action prefix · state expert · feature modulation 용으로 각 호스트 모듈의 은닉 폭에 맞춘 값입니다. 프레임별 투영기를 공유하므로 히스토리 깊이가 달라져도 인코딩 과정은 일관되지만, 이것이 인터페이스 간 파라미터·연산 총량을 같게 만들지는 **않습니다**.

**다섯 인터페이스 (§4.3).** 각 경로가 무엇을 사는지가 다릅니다.

- **State Prompt (sp)** — 현재 state 각 차원을 256 bin 으로 양자화해 기존 토크나이저로 직렬화, 약 66개 프롬프트 토큰을 언어 지시와 함께 VLM 입력에 넣습니다.

  > "Because the bins map onto the pretrained vocabulary, this route adds no trainable parameters and is the only interface whose state tokens pass through the same embedding space as language; by construction it supports only the current frame." (§4.3)
  (학습 파라미터 0개라는 점에서 가장 "공짜"처럼 보이지만, 66개 시맨틱 토큰이 VLM 전체를 통과하므로 연산은 가장 비쌉니다. 그리고 구조상 히스토리를 못 씁니다 — 이 제약이 뒤의 시간 축 실험에서 sp 를 단일 프레임 전용으로 남겨 둡니다.)

- **VLM Prefix (vp)** — 프레임별 state 토큰( $`d{=}2048`$ )을 이미지·언어 토큰 뒤 양방향 VLM prefix 에 삽입합니다. state 가 먼저 멀티모달 문맥 모델링에 참여하고(모든 이미지·언어 토큰이 state 를 attend 할 수 있음), 그 다음 조건화 prefix 를 통해 **간접적으로** 액션 생성에 영향을 줍니다.
- **Action Prefix (ap)** — state 토큰( $`d{=}1024`$ )을 causal action suffix 의 노이즈 액션 토큰 앞에 배치합니다.

  > "State tokens ( $`d{=}1024`$ ) are placed in the causal action suffix, ahead of the noisy action tokens, so that they participate directly in the action expert’s velocity-field prediction at every denoising step without first being compressed into the VLM representation. This is the most direct route from state to action." (§4.3)
  (VLM 표상으로 압축되는 단계를 건너뛴다는 것이 요점입니다. 대신 매 디노이징 스텝마다 state 토큰 처리가 반복되므로, 학습은 싸고 추론은 상대적으로 비싼 비용 구조를 갖습니다.)

- **State Expert (se)** — VLM 과 액션 전문가 옆에 state 전용 처리 스트림을 두고, 생성 중 액션 모듈과 정보를 주고받습니다. state 를 VLM 으로 압축하지도, 액션 suffix 에 접어 넣지도 않고 자체 트랜스포머 스택으로 처리하는 최대 용량 설계입니다.
- **Feature Modulation (fm)** — state 를 일반 시퀀스 토큰이 아니라 별도 조건화 메모리로 유지하고, 액션 전문가의 각 레이어가 cross-attention 으로 읽어 per-feature scale 과 shift 를 예측해 액션 특징을 지속적으로 변조합니다 (식 4):

$$\mathrm{Mod}(z;S)=\left(1+\gamma(z,S)\right)\odot z+\beta(z,S).$$

> "Each layer of the action expert reads it through cross-attention and predicts a per-feature scale $`\gamma`$ and shift $`\beta`$ that continually modulate the action features:" (§4.3)
(형태는 정확히 FiLM 입니다. 다만 조건화 지점이 단일 지점이 아니라 액션 전문가의 **모든 레이어**이고, $`\gamma,\beta`$ 를 상수 임베딩이 아닌 cross-attention 출력에서 뽑는다는 점이 고전 FiLM 과의 차이입니다.)

용량은 결코 동등하지 않습니다.

> "Under single-frame conditioning, sp, vp, ap, se, and fm add 0, 4.26M, 1.08M, 199.30M, and 123.84M trainable parameters, respectively." (§4.3)
(se 와 fm 은 위상과 용량을 함께 바꾸므로 순수 배선 비교가 아닙니다. 저자들도 이를 근거로 다섯 비교를 "완결된 시스템" 비교로 규정하고, 경로만 다른 최근접 쌍은 vp 대 ap 라고 못 박습니다 — 뒤의 RQ3 라우팅 규칙이 이 쌍 위에서 읽혀야 하는 이유입니다.)

### 학습 목표 / 손실

액션 생성 목적함수는 인터페이스 간 동일하며, 시연 궤적 데이터셋 $`\mathcal{D}=\{(o_{t}^{(i)},\ell^{(i)},S_{t}^{(i,K)},\mathbf{a}_{t:t+H-1}^{(i)})\}`$ 위에서 예측 액션 청크를 전문가 액션 시퀀스에 맞추는 $`\mathcal{L}_{\mathrm{act}}`$ 를 씁니다. 기반 정책은 $`\pi_{0.5}`$ — VLM + flow-matching 액션 전문가 — 이며, 이 논문은 손실을 새로 설계하지 않습니다. 즉 **손실은 통제 변수이고 배선만 실험 변수**입니다.

프로브 분석용으로 도입된 보조 정의가 둘 있습니다. 액션 플로우 프로브는 오일러 스텝 $`t`$ 에서 state 조건화 보정 $`c_{t}`$ 와 state-off 로부터 전문가 액션까지의 잔차 $`r_{t}`$ 를 다음과 같이 두고 (식 5):

$$c_{t}=\hat{a}^{\mathrm{true}}_{t}-\hat{a}^{\mathrm{off}}_{t},\qquad r_{t}=a^{\star}-\hat{a}^{\mathrm{off}}_{t},$$

보정 방향 $`\cos(c_{t},r_{t})`$ 와 정규화 크기 $`\|c_{t}\|_{2}/\|r_{t}\|_{2}`$ 를 보고합니다. 사례 연구의 시간 민감도는 고정 체크포인트 안에서 순서 있는 8프레임 히스토리를 현재 프레임 8복제로 바꾼 뒤의 액션 거리로 잽니다 (식 6):

$$D_{q}=\left\|\hat{\mathbf{a}}^{\,\mathrm{true}}_{q}-\hat{\mathbf{a}}^{\,\mathrm{repeat}}_{q}\right\|_{2}$$

두 정의 모두 "state 가 정말 액션 생성에 도달하는가"를 성공률 밖에서 확인하기 위한 계측이며, 학습 신호가 아닙니다.

### 학습 셋업

- **기반 정책** — $`\pi_{0.5}`$ (VLM + flow-matching 액션 전문가). 모든 모델이 **동일한 사전학습 체크포인트에서 출발**해 해당 태스크 데이터로 **full fine-tuning** 됩니다.
- **관찰** — 좌측 외부 카메라, 우측 외부 카메라, 손목 카메라의 3개 뷰. 모든 방법이 동일한 시각 입력·언어 지시·액션 공간·평가 프로그램을 씁니다.
- **통제** — 데이터 파이프라인, 액션 표현, 학습률 스케줄, 학습 예산을 인터페이스 간 일치시킵니다. 학습·평가 전 난수 시드를 고정하고 같은 시드 스케줄을 재사용해 장면 초기화·객체 인스턴스·배치를 통제합니다. 슬롯 정합 시간 비교는 이미지·언어·state 슬롯 수·전문가 액션·초기 플로우 노이즈까지 고정합니다.

> "All models are initialized from the same pretrained $`\pi_{0.5}`$ checkpoint and fully fine-tuned on the corresponding task data under a shared optimization recipe, keeping the data pipeline, action representation, learning-rate schedule, and training budget matched across interfaces; se and fm train with a slightly lower nominal sample exposure due to hardware allocation, so we do not use them for capacity-matched claims." (§5.1)
(정직한 자기 제한입니다. se 와 fm 은 학습 노출량이 살짝 적으므로 용량 정합 주장에 쓰지 않겠다고 선언합니다. 뒤집으면, 이 논문에서 se/fm 의 성능은 하한으로 읽어야 하고 최종 라우팅 규칙은 vp/ap 쌍 위에서만 강하게 성립합니다.)

- **연산 회계 (§C.1)** — 해석적 비용 모델은 평가 스캐폴드를 따라 $`L=18`$ 트랜스포머 레이어, 각 256 토큰의 이미지 스트림 3개, 지시 토큰 16개, 액션 토큰 $`A=50`$ 을 가정합니다. state 추가 전 조건화 prefix 활성 토큰 수는 (식 7):

$$P=3\times 256+16=784$$

VLM 폭은 $`d_{v}=2048`$ (FFN 16384), 액션 전문가 폭은 $`d_{a}=1024`$ (FFN 4096), 그룹 어텐션 내부 폭 $`H=8\times 256=2048`$ , 추론은 $`N=10`$ 오일러 스텝입니다. 토큰 1개 추가의 한계 순전파 비용은 (식 8), 공유 2층 state 투영기 비용은 (식 9)로 둡니다:

$$F_{\mathrm{tok}}(d,m)=2L\!\left[d(H+2\!\times\!256+H)+3dm\right],$$

$$F_{\mathrm{enc}}(d,K)=2K(32d+d^{2})$$

주입 경로에 따른 어텐션 확장은 갈라집니다 — VLM prefix 에 $`K`$ 개 양방향 state 토큰을 넣으면 (식 10), 같은 토큰을 causal action suffix 에 넣으면 (식 11), 이미 prefix 에 캐시된 state 토큰은 매 오일러 스텝마다 suffix→prefix 어텐션 비용을 추가로 냅니다 (식 12):

$$\Delta F_{\mathrm{VP,attn}}=4HL\left(2PK+K^{2}+AK\right).$$

$$\Delta F_{\mathrm{AP,attn}}=4HL\left(PK+\frac{K(K+1)}{2}+AK\right).$$

$$\Delta F_{\mathrm{cache}}=4HLAK.$$

학습 비용은 트랜스포머 블록이 역전파 중 재계산된다는 점을 반영해 순전파의 4배로 근사합니다 (식 13):

$$\Delta F_{\mathrm{train}}\simeq 4\,\Delta F_{\mathrm{forward}},$$

이 회계가 말해 주는 비대칭이 결정적입니다. VLM prefix 는 state 토큰이 거대한 prefix( $`P=784`$ )에 참여하므로 **학습 비용**이 빠르게 커지고, action prefix 는 state 토큰 처리가 10회 디노이징 스텝 전체에서 반복되므로 **추론 비용**이 커집니다. 즉 보편적으로 싼 경로는 없고, 경로마다 소비하는 자원의 종류가 다릅니다.

---

## 📊 실험 설정과 결과

**평가 설계.** RoboCasa365 위에서 두 층으로 평가합니다. atomic 은 단일 단계 제어를 재며, RoboCasa365 의 atomic 태스크를 지배적 조작 의미론 기준으로 **사전 분할**해 A(재배치·pick-and-place, 엔드이펙터/모바일 베이스의 대범위 위치 결정), B(관절 물체 상호작용, 지속 접촉과 운동 위상 모델링), C(노브·스위치·가전 제어, 좁은 작업공간의 국소 정밀도) 세 패밀리로 나눕니다. composite 은 `lifelong_learning_phase2` 설정으로 20개 태스크 타입 각각이 한 에피소드 안에 2–3개 atomic 하위 목표를 사슬로 엮습니다.

> "Each family contains 15 representative tasks (45 in total) and trains a separate category expert, so cross-family results reflect interface behavior under different control demands rather than one unified multi-task policy." (§5.1)
(패밀리별 전문가를 따로 학습한다는 점이 중요합니다. 패밀리 간 순위 역전이 "하나의 멀티태스크 정책이 어떤 태스크를 희생했다"가 아니라 "제어 요구가 다르면 최적 배선이 다르다"로 읽히는 근거가 여기서 나옵니다.)

atomic 은 태스크당 50회, composite 은 25회 폐루프 롤아웃이며 동일 시드 스케줄을 씁니다. 주 지표는 폐루프 성공률(SR)이고, Phase 2 는 에피소드 내 모든 하위 목표를 완수해야 성공으로 칩니다.

### RQ1 — 현재 프레임 1장은 도움이 되는가

Table 1 (45 atomic 태스크, SR %; 괄호는 no-state 대비 증감, † 는 0을 배제하는 paired task-bootstrap 95% 구간):

| Task | NS (No state) | SP1 (State Prompt) | VP1 (VLM Prefix) | AP1 (Action Prefix) | SE1 (State Expert) | FM1 (Feature Mod.) |
|---|---|---|---|---|---|---|
| Atomic A | 61.7 | 68.7 (↑7.0) | 63.2 (↑1.5) | 61.7 (±0.0) | 61.6 (↓0.1) | 64.3 (↑2.6) |
| Atomic B | 62.7 | 64.3 (↑1.6) | 68.8 (↑6.1) | 65.9 (↑3.2) | 68.5 (↑5.8) | 68.2 (↑5.5) |
| Atomic C | 39.5 | 40.3 (↑0.8) | 38.3 (↓1.2) | 39.6 (↑0.1) | 42.8 (↑3.3) | 40.3 (↑0.8) |
| Atomic macro | 54.6 | 57.7 (↑3.1)† | 56.8 (↑2.1) | 55.7 (↑1.1) | 57.6 (↑3.0) | 57.6 (↑2.9) |

> "Table 1 shows that on the 45 atomic tasks the no-state model reaches a macro success rate of 54.6%, and the point estimates of all five state interfaces exceed this baseline, with gains ranging from $`+1.1`$ (ap) to $`+3.1`$ points (sp)." (§5.2, Table 1)
(다섯 인터페이스 전부 baseline 을 넘지만, 구간이 0을 배제하는 것은 sp 하나뿐입니다. 나머지는 "일관된 양의 경향"이지 개별적으로 입증된 효과가 아니라고 저자들이 스스로 강도를 낮춥니다.)

패밀리별 판독 — 각 행이 무엇을 분리하는가:

- **Atomic A (재배치)** — sp 가 68.7% (↑7.0) 로 압도하고 연속 인터페이스는 ↓0.1 에서 ↑2.6 에 머뭅니다. 대범위 위치 결정 태스크이므로, 이산화된 절대 좌표(베이스·EEF 자세 포함)가 언어 임베딩 공간에서 직접 읽히는 것이 유리하다는 해석이 자연스럽습니다.
- **Atomic B (관절 물체)** — 순서가 뒤집혀 vp 가 68.8% (↑6.1) 로 선두, se(↑5.8)·fm(↑5.5) 이 뒤따르고 sp 는 ↑1.6 으로 중위권으로 떨어집니다. 지속 접촉과 운동 위상 모델링에는 state 가 시각 문맥과 함께 해석되는 편이 낫다는 신호입니다.
- **Atomic C (노브·스위치)** — 가장 어렵고(no-state 39.5%) 가장 까다롭습니다. se 가 42.8% (↑3.3) 로 선두이고, **vp 는 유일하게 baseline 아래(↓1.2)** 로 떨어집니다. 좁은 작업공간의 국소 정밀도 태스크에서는 VLM 경유 압축이 오히려 손해라는 뜻입니다.

> "Each interface thus has a family where it shines and a family where it adds little or even hurts—a pattern consistent with the three families imposing different control demands, and one that a single benchmark-wide average would completely hide." (§5.2)
(이 논문에서 실무적으로 가장 값비싼 문장입니다. 벤치마크 전체 평균 하나로 인터페이스를 고르면, 실제로는 태스크 패밀리마다 다른 답을 하나의 숫자가 덮어 버립니다.)

**연산 비용 (Figure 2, §C).** 성능만 보면 안 되는 이유가 여기서 드러납니다.

> "sp serializes the state into roughly 66 discrete prompt tokens, adding about 1114 training GFLOPs per sample and 282 GFLOPs per ten-step policy call—the most expensive design by two orders of magnitude on the training side." (§5.2)
(sp 는 학습 파라미터가 0개인데도 학습 연산이 두 자릿수 배 비쌉니다. "파라미터 추가 없음"과 "연산 추가 없음"이 전혀 다른 개념이라는 점을 이 사례가 못 박습니다.)

| 인터페이스 | 추가 학습 파라미터 | 한계 학습 GFLOPs / sample | 한계 추론 GFLOPs / policy call (10-step) |
|---|---|---|---|
| sp (State Prompt) | 0 | 약 1114 | 282 |
| vp (VLM Prefix) | 4.26M | 16.9 | 4.3 |
| ap (Action Prefix) | 1.08M | 3.5 | 7.6 |
| se (State Expert) | 199.30M | 2.6 | 0.7 |
| fm (Feature Modulation) | 123.84M | 45.4 | 114 |

se 와 fm 은 매크로 점추정(57.6%)에서 sp(57.7%)와 사실상 같은 자리에 있으면서 한계 연산은 극히 일부만 씁니다. 히스토리 길이에 따라 state 인터페이스 비용이 함께 커져야 하는 상황이라면 이 트레이드오프가 결정적입니다.

### RQ2 — 히스토리는 얼마나 필요한가

> "Figure 3 shows a clear non-monotonic trend: short histories improve performance over the corresponding single-frame models, whereas deeper uncompressed histories provide no additional benefit and eventually degrade control." (§5.2)
(1–96 프레임 스윕의 결론이 "많을수록 좋다"가 아니라 유계 구간이라는 것입니다. 패밀리 A·B 는 문맥 증가에 비교적 관대하지만 **패밀리 C 는 긴 히스토리에서 뚜렷이 무너집니다** — 정밀한 state-to-action 정렬이 필요한 태스크일수록 중복·낡은 state 가 간섭한다는 해석입니다.)

저자들은 $`K{=}8`$ 을 이후 실험의 기본 시간 조건화 레시피로 채택하되, 이는 보편 최적이 아니라 경험적 동작점이라고 명시합니다. 핵심 주장은 "8이 최적"이 아니라 "짧은 히스토리가 긴 원시 시퀀스보다 일관되게 신뢰할 만하다"입니다.

Table 2 (composite 20개 태스크, SR %):

| Interface / control | $`K{=}1`$ | $`K{=}8`$ | $`\Delta`$ SR |
|---|---|---|---|
| **EEF-pose state (default)** | | | |
| AP | 28.2 | 39.0 | +10.8 |
| VP | 34.4 | 33.8 | −0.6 |
| SE | 25.8 | 28.0 | +2.2 |
| FM | 27.8 | 32.2 | +4.4 |
| **Joint-angle state (same protocol)** | | | |
| AP | 31.4 | 36.2 | +4.8 |
| VP | 33.6 | 35.8 | +2.2 |
| **Slot-matched control (EEF-pose state)** | | | |
| AP: current-only → genuine history | 30.8 | 39.0 | +8.2 |

세 블록이 각각 분리하는 것:

- **1블록(EEF-pose)** — 히스토리 확장의 이득이 **액션 측에 몰립니다**. ap 는 +10.8 인 반면 vp 는 −0.6 으로 오히려 미세하게 하락합니다. 같은 시간 정보인데 넣는 위치가 부호를 바꿉니다.
- **2블록(joint-angle)** — 같은 프로토콜에서 state 좌표계만 관절각으로 바꿔도 방향이 재현됩니다(ap +4.8, vp +2.2). 다만 격차는 크게 줄어, $`K{=}8`$ 에서 ap 36.2% 대 vp 35.8% 로 사실상 붙습니다.
- **3블록(슬롯 정합 대조)** — 가장 중요한 행입니다. 8개 ap 슬롯에 현재 state 를 복제해 넣은 30.8% 대 순서 있는 8프레임의 39.0%, 차이 +8.2. 토큰 수가 아니라 시간 변이가 이득의 원천임을 분리합니다.

> "The repeated-state control falls substantially short of the genuinely ordered history, and the paired task-bootstrap confidence interval excludes zero (Appendix B)." (§5.2)
(이 논문에서 sp 매크로 이득과 함께 구간이 0을 배제하는 두 결과 중 하나입니다. 히스토리 이득이 "조건화 용량이 늘어서"라는 대안 설명을 실험적으로 배제합니다.)

### RQ3 — state 는 어디로 들어가야 하는가

$`K{=}1`$ 에서는 VLM 측이 우세합니다. composite 에서 vp1 34.4% 대 ap1 28.2% (EEF-pose), 33.6% 대 31.4% (관절각)이며 다른 항목들은 no-state 28.4% 근처에 머뭅니다. atomic 에서는 단일 프레임 선두들이 0.1점 이내로 몰려 있어 선호가 결정되지 않습니다 — VLM 측 우위는 다단계 제어에서 단일 관찰이 시각-언어 표상을 문맥화해 줄 때 비로소 드러납니다.

> "The $`K{=}1\!\rightarrow\!8`$ gains are largest when the sequence directly conditions the action head: $`+10.8`$ points with the EEF-pose state, $`+4.8`$ with joint angles, and $`+3.9`$ on the atomic suite, whereas the same history in the VLM prefix yields only $`-0.6`$ , $`+2.2`$ , and $`+0.6`$ ." (§5.2)
(세 스위트 모두에서 같은 방향입니다. 그리고 반전의 폭이 극적입니다 — ap 는 단일 프레임에서 가장 약하거나 약한 축에 속했는데, 8프레임에서는 atomic 59.6% / composite 39.0% 로 모든 패널의 최고 진입점이 됩니다.)

> "Together with the slot-matched control in RQ2, the two findings compose into a simple design rule for our setting: inject single-frame state into the VLM, but route multi-frame state history to the action head." (§5.2)
(논문의 결론 규칙입니다. 다만 "for our setting" 이라는 한정이 문장 안에 명시되어 있습니다.)

프로브(§A)가 이 교차에 데이터 흐름 해석을 붙입니다.

> "Across the final six VLM layers, the 45-task mean language-to-image attention redistribution is 17.3% for vp1 and 22.0% for vp8; the corresponding image-token relative $`\ell_{2}`$ changes are 19.6% and 26.2%." (§A.2)
(VLM 측 state 는 액션 생성 **이전에** 멀티모달 문맥을 실제로 바꿉니다. 반대로 ap8 을 끄면 이 prefix 양들이 변하지 않는데, ap 의 state 토큰은 prefix 가 형성된 **뒤에** 들어오기 때문입니다. 두 경로가 서로 다른 계산 지점에서 작동한다는 물리적 근거입니다.)

![Figure 6 — state-conditioned correction over the flow trajectory](https://arxiv.org/html/2608.03052/flow_correction_dynamics_interfaces.png)

> "Figure 6: State-conditioned correction over the ten-step flow trajectory.
The top row reports alignment between the true-minus-off correction and the
state-off-to-expert residual. The bottom row reports correction magnitude
normalized by that residual. Columns compare action-side continuous state,
VLM-side continuous state, and discrete prompt state. Curves average 45
tasks; bands are task-bootstrap 95% intervals." (§A)
(성공률 밖에서 "state 가 정말 액션에 도달하는가"를 재는 계측입니다. 보정이 전문가 잔차와 같은 방향을 향할수록, 그리고 그 크기가 클수록 state 가 실질적으로 액션을 고치고 있다는 뜻입니다.)

> "With one continuous state frame, the final alignment is 0.245 for vp1 and 0.079 for ap1; normalized magnitudes are 0.297 and 0.174." (§A.3)
(단일 프레임에서는 ap 의 보정이 방향·크기 모두 vp 의 절반 이하입니다. ap1 이 왜 단일 프레임에서 가장 약한지가 성공률이 아니라 생성 내부 계측으로 설명됩니다.)

ap1→ap8 로 옮기면 최종 정렬이 0.079 → 0.270, 정규화 크기가 0.174 → 0.382 로 오릅니다. 45개 태스크 짝 비교에서 8-빼기-1 증가분은 정렬 $`+0.191`$ , 크기 $`+0.208`$ 이며 task-bootstrap 95% 구간은 각각 $`[+0.143,+0.239]`$ 와 $`[+0.171,+0.244]`$ 로 0을 배제합니다.

![Figure 7 — representative action-conditioned spatial attention](https://arxiv.org/html/2608.03052/representative_action_attention.png)

> "Figure 7: Representative action-conditioned spatial attention.
Matched true-state and state-off passes show how a one-frame VLM prefix and
one- and eight-frame action prefixes redistribute action-conditioned visual
attention. The visualization is descriptive: it reveals where state changes
the spatial readout, while the flow probe in Figure 6
measures how that change reaches action generation." (§A.4)
(단일 프레임 action prefix 는 공간 판독을 거의 바꾸지 못하는 반면, 순서 있는 짧은 히스토리는 VLM prefix 를 다시 쓰지 않고도 하류 반응을 키웁니다. 저자들이 "descriptive" 라고 명시했으므로 인과 근거가 아니라 예시로 읽어야 합니다.)

**사례 연구 (§B, PrepareToast).** 두 물건을 놓고 캐비닛을 다시 닫는 태스크에서, 50개 짝지은 에피소드 시드로 ap1 과 ap8 을 비교합니다. 초기 배치 단계는 비슷합니다 — S1/S2 도달률이 ap1 90%/64%, ap8 96%/68%. 분리는 그 이후에 시작됩니다.

> "ap1 reaches the cabinet-reclosed milestone S3 in 30% of episodes, whereas ap8 reaches it in 56%." (§B.2)
(같은 +26점 차이가 S4 와 최종 성공까지 이어지고, 짝 에피소드 부트스트랩 구간은 $`[+10,+42]`$ 점입니다. S2 도달 조건부로 보면 S3 완수율이 46.9% → 82.4% 로 오릅니다. 히스토리의 이득이 태스크 전체에 고르게 퍼진 것이 아니라 **하위 목표 전환 지점에 국소화**되어 있다는 뜻입니다.)

> "The mean true-history versus repeat-current action distance is 0.198 within a stage, 0.361 before a boundary, 1.033 at a boundary, and 0.748 afterward. Boundary sensitivity is therefore 5.2 times the within-stage value." (§B.3)
(고정 체크포인트 안에서 히스토리만 복제본으로 바꿨을 때 액션이 가장 크게 흔들리는 곳이 바로 진행 경계입니다. 학습된 정책이 시간 순서를 실제로 "읽고" 있으며, 그 읽기가 단계 전환 판단에 집중된다는 서술적 증거입니다.)

---

## ⚖️ 한계

- **실기 검증 부재 (저자 명시)** — 전 실험이 RoboCasa365 시뮬레이션입니다. state 의 유용성은 센서 노이즈·지연·캘리브레이션 오차에 특히 민감한 입력인데, 시뮬레이터의 state 는 이 모두가 없는 완벽한 신호입니다. 시뮬에서 "짧은 히스토리가 돕는다"는 결론이 실기에서 "노이즈 8프레임이 노이즈 1프레임보다 낫다"로 그대로 옮겨진다는 보장은 없습니다.
- **state 가 순수 자기수용 감각이 아님 (저자 명시)** — 16차원 state 의 절반 가까이가 모바일 베이스의 월드 프레임 위치·자세입니다. 저자들이 "purely internal motor feedback 으로 읽을 수 없다"고 경고했듯, 특히 대범위 위치 결정 태스크인 패밀리 A 에서 sp 가 ↑7.0 을 낸 것은 자기수용 감각이 아니라 **전역 위치 정보의 이산 좌표 판독** 효과일 가능성이 있습니다. 고정 베이스 플랫폼에서는 이 성분이 통째로 사라집니다.
- **운동학 state 만 다룸 (저자 명시)** — force·tactile 등 접촉 모달리티가 빠져 있습니다. 이 논문의 시간 상수(8프레임)와 라우팅 규칙이 접촉 신호에도 성립하는지는 미검증이며, 접촉은 운동학보다 대역폭이 훨씬 높아 같은 프레임 수가 전혀 다른 시간 길이를 의미합니다.
- **단일 시드 점추정 (저자 명시)** — 대부분의 비교가 단일 학습 시드입니다. 구간이 0을 배제하는 것은 sp 매크로 이득과 슬롯 정합 대조 두 개뿐이고, 인터페이스×깊이 스윕은 탐색적이며 다중 비교 보정이 없습니다. 라우팅 규칙은 "방향성 패턴"이지 통계적 순위가 아니라고 저자들이 스스로 규정합니다.
- **용량이 통제되지 않음** — se(199.30M)와 fm(123.84M)은 위상과 용량을 함께 바꿉니다. 게다가 하드웨어 배분 탓에 학습 노출량까지 약간 적습니다. 따라서 "se 가 패밀리 C 에서 최고"라는 결과가 배선 덕인지 용량 덕인지 분리되지 않습니다. 순수 경로 비교로 성립하는 쌍은 vp 대 ap 하나뿐이며, 이 쌍조차 투영 폭(2048 vs 1024)이 다릅니다.
- **관절각 표현에서 교차가 흐려짐** — $`K{=}8`$ 에서 ap 36.2% 대 vp 35.8% 는 짝 부트스트랩 잡음대 안입니다. 즉 라우팅 규칙의 강도가 state 좌표계에 의존하며, EEF-pose 에서 관측된 +10.8 이라는 큰 격차가 좌표계를 바꾸면 +0.4 로 줄어듭니다. 규칙의 방향은 재현되지만 크기는 재현되지 않습니다.
- **긴 히스토리가 해로운 메커니즘이 미규명** — 저자들은 "중복·낡은 state 정보가 간섭한다"고 해석하지만, 이것이 causal confusion / copycat 문제(자기 최근 궤적을 복사)인지, 단순한 시퀀스 길이 문제인지, 아니면 패밀리 C 의 좁은 작업공간 특유의 문제인지는 분리되지 않았습니다. 관련 연구에서 copycat 위험을 스스로 인용하면서도 그 진단을 실험으로 수행하지는 않았습니다.
- **원시(uncompressed) 히스토리만 검증** — 순환 모듈·메모리 토큰·압축 잠재 등 대안이 관련 연구로 언급되지만 비교군에 없습니다. "긴 히스토리는 해롭다"는 결론은 정확히는 "긴 **원시** 히스토리는 해롭다"이며, 압축된 장기 문맥이 여전히 유효할 여지가 남습니다.
- **패밀리 분할의 일반성** — A/B/C 는 RoboCasa365 주방 도메인의 제어 의미론 분할입니다. 사전 분할이라는 점에서 방법론적으로 건전하지만, 이 세 축이 조작 태스크 공간을 대표한다는 근거는 제시되지 않습니다.

---

## ♻️ 재현성

- **코드 / 모델** — 본문·초록·부록 어디에도 코드 저장소나 프로젝트 페이지 URL 이 없습니다 `(원문 미명시)`. 라이선스는 arXiv 영구 비독점 라이선스입니다.
- **기반 자산** — 기반 정책 $`\pi_{0.5}`$ ([arXiv:2504.16054](https://arxiv.org/abs/2504.16054))와 벤치마크 RoboCasa365 ([arXiv:2603.04356](https://arxiv.org/abs/2603.04356))는 모두 외부 공개 자산이므로, 스캐폴드 자체는 원리적으로 재구성 가능합니다.
- **프로토콜 재현성** — 이 논문의 실질적 기여물은 프로토콜입니다. 45개 atomic(패밀리당 15, 태스크당 50 롤아웃) + 20개 composite(태스크당 25 롤아웃), 고정 시드 스케줄, 슬롯 정합 repeat-current 대조군, 짝 태스크 부트스트랩 구간 — 이 절차는 코드 없이도 명세만으로 이식 가능하며 저자들도 "directly reusable" 이라고 밝힙니다.
- **하드웨어** — 학습 하드웨어 사양은 명시되지 않았습니다 `(원문 미명시)`. 다만 se·fm 의 학습 노출량 차이가 "hardware allocation" 때문이라고만 언급됩니다. 연산 비용 수치는 측정 wall-clock 이 아니라 하드웨어 독립적 해석 추정치입니다.
- **실기 검증** — 없음(저자 명시 한계).

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P2(구조적 멀티모달 관찰 융합) — 주 연결.** proprioception 이라는 비시각 모달리티를 VLA 에 어떻게 결합할지가 이 논문의 전부이므로 P2 의 정중앙입니다.
  - **D10(concat 을 넘어선 이종 모달리티 융합)** — 우리 v1 은 cross-attention / 비대칭 융합(ForceFlow 계열 modal masking·AdaLN)입니다. 이 논문의 fm 이 정확히 그 계열(레이어별 cross-attention → $`\gamma,\beta`$ )이고, ap 는 그보다 단순한 prefix 결합입니다. 결과는 우리 v1 을 **부분적으로만** 지지합니다 — fm 은 매크로 57.6% 로 상위권이지만 단독 최고는 아니며, 파라미터 123.84M·추론 114 GFLOPs 라는 값을 치릅니다. 반면 ap 는 1.08M·3.5 GFLOPs 로 $`K{=}8`$ 최고 성능을 냅니다.
  - **D11(proprio-tactile-force 토큰 구성)** — 우리 v1 은 손가락별 proprio-tactile 결합(양손 10 finger + 2 palm 토큰)입니다. 이 논문은 **프레임당 1토큰** 입도이며, 손가락별 분해는 다루지 않습니다. 다만 시간 축 결론( $`K{=}8`$ 유효, 그 이상 해로움)과 토큰 수 회계(식 10–12)는 우리 토큰 구성에 직접 곱해집니다 — 12토큰 × 8프레임 = 96 토큰이라는 비용이 여기서 계산됩니다.
- **P1(이종 Body/Hand 액션 전문가) — 강한 연결.**
  - **D5(입력 모달리티 + 제어율 분리)** — 우리 v1 은 (ii) 모달리티 분리 + (α) 공유 제어율입니다. 이 논문은 모달리티 분리의 **주입 위치** 축에 처음으로 통제된 근거를 제공하지만, D5 가 아직 다루지 않는 축인 **시간 깊이**를 새로 열어젖힙니다.
  - **D7(π 백본 통합 / 분할)** — 우리 v1 은 (i) π0 액션 전문가 슬라이스 + 양측 FT 입니다. 이 논문의 vp 대 ap 대립이 곧 "state 를 백본 쪽에 둘 것인가 액션 전문가 쪽에 둘 것인가"라는 분할 경계 문제이며, $`\pi_{0.5}`$ 위에서 직접 측정된 유일한 근거입니다.
  - **D4(Body↔Hand 정보 공유)** — 우리 v1 은 $`a_b`$ → $`(\gamma,\beta)`$ FiLM 으로 hand head 입력을 **단일 지점** 변조하는 것입니다. 이 논문의 fm 은 동일 메커니즘을 액션 전문가 **전 레이어**에 적용한 사례로, FiLM 계열 변조가 π 계열 flow-matching 액션 전문가 안에서 작동한다는 첫 통제 근거이자, 그 비용(123.84M 파라미터, 추론 114 GFLOPs)의 첫 견적입니다. 다만 조건 신호가 body 액션이 아니라 state 라는 점에서 유추이지 동일 실험은 아닙니다.
- **P4(사전학습 기반 데이터 효율 적응) — 간접 연결이자 긴장.**
  - **D19(VLM lineage 및 적응 범위)** — 우리 v1 은 (a) **VLM 전체 동결 + 액션 전문가만 학습**입니다. 이 논문은 모든 모델을 $`\pi_{0.5}`$ 체크포인트에서 **full fine-tuning** 했습니다. vp 경로의 이득은 VLM 이 state 토큰에 맞춰 갱신될 수 있다는 전제 위에 서 있으므로, 동결 백본 하에서는 vp 수치가 그대로 재현되지 않을 가능성이 큽니다.
  - **D23(액션 표현 × 사전학습/보존)** — 우리 v1 은 (iii) 연속 flow-matching 헤드입니다. 이 논문의 전 실험이 flow-matching 액션 전문가 위에서 수행되었으므로 셋업이 일치하며, 특히 식 (12)의 "매 오일러 스텝마다 반복되는 비용"은 우리 추론 예산에 그대로 적용됩니다.
- **P0(VLA 데이터셋 & 벤치마크) — 도구 연결. D26(벤치마크/eval 스카우팅 범위)** — RoboCasa365 기반 계층 프로토콜(사전 분할 패밀리 + composite + 슬롯 정합 대조군)은 우리 eval 하니스 설계에 직접 이식 가능한 절차입니다.
- **P3(Hand-level System0) / P5(World Model) — 연결 없음.** state 가 순수 운동학이고 tactile·force 가 배제되어 있어 D15(System0 입력 모달리티)를 움직일 근거가 없습니다. 예측 모델도 등장하지 않아 D28–D32 와 무관합니다. 연결을 만들지 않고 그대로 둡니다.
- **Identity 긴장/지지** — Identity 의 "flat-concat 을 넘어선 구조적 관찰 결합" 주장을 **부분적으로 지지**합니다. 배선이 성능을 유의하게 바꾼다는 것은 관찰 결합이 설계 변수라는 우리 전제와 일치합니다. 동시에 **긴장**도 있습니다 — 이 논문에서 최고 성능을 낸 배선은 정교한 구조적 융합(fm/se)이 아니라 가장 단순한 액션 측 prefix(ap)였고, 구조적 융합 쪽은 큰 용량을 쓰고도 동급에 머물렀습니다. 다만 이 논문의 state 는 손가락별 접촉 의미론이 없는 16차원 운동학 벡터이므로, 구조화할 것이 애초에 적었다는 반론이 성립합니다.
- **경쟁자 함의** — P1 §5 의 Demystifying Action Space Design ([arXiv:2602.23408](https://arxiv.org/abs/2602.23408))이 **액션** 공간 축에서 한 일을 이 논문이 **관찰(state)** 축에서 수행한 대칭 연구입니다. 두 편을 나란히 두면 "π 계열 위에서 입출력 배선을 통제 실험으로 확정한다"는 연구 형식 자체가 하나의 경쟁 흐름으로 굳어지고 있음을 보여 줍니다.

---

## ✨ 핀 논문 대비 델타

- **vs ForceFlow (P2 핀, [arXiv:2605.11048](https://arxiv.org/abs/2605.11048))** — ForceFlow 는 비대칭 멀티모달 융합 아키텍처 **하나**를 제안하고 자기 시스템 안에서 검증합니다. 이 논문은 아키텍처를 제안하지 않는 대신, 같은 신호를 다섯 배선에 걸쳐 옮기며 **배선 간 비교 가능성** 자체를 만들어 냅니다. 특히 "태스크 무관 최적 배선은 없다"는 음의 결과는 단일 아키텍처 논문이 구조적으로 낼 수 없는 종류의 결과입니다.
- **vs ViTacFormer (P2 핀, [arXiv:2506.15953](https://arxiv.org/abs/2506.15953))** — ViTacFormer 는 cross-attention 시각-촉각 융합의 유효성을 보입니다. 이 논문의 fm 이 같은 cross-attention 조건화 계열이면서, 그것을 prefix 결합·전용 전문가·텍스트 직렬화와 **동일 조건에서 나란히** 놓고 비용까지 함께 보고한다는 점이 새롭습니다. 융합 방식 선택을 성능 단독이 아니라 성능/파라미터/FLOPs 삼중 축으로 판단할 근거가 처음 생깁니다.
- **vs π0.5 (P4 핀, [arXiv:2504.16054](https://arxiv.org/abs/2504.16054))** — π0.5 는 state 를 텍스트 토큰으로 직렬화합니다(= 이 논문의 sp). 이 논문은 π0.5 자신의 그 선택을 자기 백본 위에서 감사한 셈이며, 결과는 절반의 지지입니다 — sp 는 매크로에서 유일하게 구간이 0을 배제하는 이득을 냈지만 학습 연산이 두 자릿수 배 비싸고, 히스토리를 구조상 못 쓰며, 패밀리 B·C 에서는 중위권으로 내려앉습니다.
- **vs Demystifying Action Space Design (P1 방법론 base, [arXiv:2602.23408](https://arxiv.org/abs/2602.23408))** — 통제 실험이라는 형식은 같지만 축이 반대편(출력 vs 입력)입니다. 새로운 것은 **시간 깊이와 주입 위치의 상호작용**이라는 2차 효과를 잡아냈다는 점입니다 — 단일 축 스윕만 했다면 $`K{=}1`$ 최적과 $`K{=}8`$ 최적이 서로 다른 경로라는 사실을 놓쳤을 것입니다.
- **vs FiLM (P1/P2 방법론 base, [arXiv:1709.07871](https://arxiv.org/abs/1709.07871))** — FiLM 은 조건화 계층 원형입니다. 이 논문은 그 원형을 flow-matching 액션 전문가의 전 레이어에 적용했을 때의 실측 성능과 비용을 처음으로 제공하며, "FiLM 은 싸다"는 통념과 달리 cross-attention 으로 $`\gamma,\beta`$ 를 생성하는 구현에서는 123.84M 파라미터·추론 114 GFLOPs 가 든다는 점을 드러냅니다.

---

## ⚙️ 의사결정 함의

이 논문이 옳다면 우리 파이프라인에서 바뀌는 것:

- **`state_history_len K` 를 1에서 8로 올리고, 그 히스토리를 액션 전문가 쪽으로 라우팅합니다.** 현재 D5/D11 은 시간 깊이를 명시하지 않아 사실상 $`K{=}1`$ 관행을 따릅니다. 변경 후 기본값은 "현재 프레임은 VLM prefix, $`K{=}8`$ 히스토리는 액션 전문가 prefix"의 **이중 경로**이며, 이는 단일 경로 결정보다 config 키가 하나 늘어난다는 뜻입니다 — `state.vlm_prefix.enabled = true (K=1)` 과 `state.action_prefix.history_len = 8` 을 분리해 둡니다.
- **D4 FiLM 의 조건화 지점 수를 재검토합니다.** v1 은 hand head 입력 단일 지점 변조인데, 이 논문의 fm 은 전 레이어 변조로도 ap 단순 prefix 를 넘지 못했습니다. 우선순위를 뒤집어, FiLM 지점 확장보다 **hand 토큰의 액션 전문가 prefix 결합**을 먼저 측정하는 것이 비용 대비 정보량이 큽니다.
- **eval 하니스에 `repeat_current` 대조군을 필수 ablation 으로 넣습니다.** 손가락별 tactile 히스토리를 넣고 성능이 오르면, 그것이 시간 정보 때문인지 토큰이 늘어서인지 반드시 분리해야 합니다. 구현은 히스토리 버퍼를 현재 프레임 복제로 채우는 플래그 하나이며, 이 논문 기준 +8.2점이라는 큰 격차를 만들어 낸 저비용 장치입니다.
- **평가 지표를 매크로 단일값에서 패밀리별 분해로 바꿉니다.** 우리 phasing 기준으로 in-hand 재배향(Phase 1)과 도구 조작(Phase 2)은 이 논문의 패밀리 C(좁은 작업공간·국소 정밀)에 대응하고, 접근·운반은 패밀리 A 에 대응합니다. **패밀리 C 가 긴 히스토리에서 가장 크게 무너진 패밀리**라는 사실이 우리 주력 태스크에 직접 걸리므로, 매크로 평균 하나로 배선을 고르면 우리가 가장 신경 쓰는 구간에서 잘못된 선택을 하게 됩니다.
- **추론 예산 재계산이 필요합니다.** 액션 측 state 토큰은 $`N=10`$ 디노이징 스텝마다 반복 처리됩니다(식 12). 우리 D11 토큰 구성(양손 12토큰) × $`K{=}8`$ = 96 state 토큰을 액션 prefix 에 얹으면, 이 논문의 단일 토큰 기준 ap 추론 증분 7.6 GFLOPs 와는 전혀 다른 규모가 됩니다. 히스토리 도입 전에 **토큰 압축(손 단위 집계 후 히스토리, 또는 히스토리 다운샘플링)** 을 함께 설계해야 합니다.
- **D19 동결 전제 하에서 vp 경로를 재측정합니다.** 우리 v1 은 VLM 전체 동결입니다. 이 논문의 vp 이득은 full FT 전제에서 나온 값이므로, 동결 하에서는 VLM 측 주입의 가치가 떨어지고 라우팅 규칙이 "모든 state 를 액션 측으로"로 단순화될 가능성이 있습니다. 이는 오히려 우리 스택에 유리한 방향이며, 검증되면 config 가 이중 경로에서 단일 경로로 되돌아갑니다.

---

## ⚠️ 먼저 검증할 실패 모드

가장 싼 확인부터:

1. **state 차원이 32차원 zero-pad 한도를 넘는지 (탁상 계산, 수 분).** 이 논문의 state 는 16차원이고 프레임워크 고정 폭 32로 zero-pad 됩니다. 우리 22-DOF Sharpa Hand + 6–7 DOF 팔이면 관절 위치만으로도 이미 28–29차원이고, 여기에 속도·토크·촉각 특징이 붙으면 32를 훌쩍 넘습니다. openpi 계열 스캐폴드의 state 슬롯 폭이 하드코딩되어 있는지 먼저 확인해야 합니다 — 넘으면 투영기 설계부터 달라지고, 이 논문의 "프레임당 1토큰" 회계가 그대로 적용되지 않습니다.
2. **베이스 자세 성분을 뺀 재해석 (문헌 재독, 수십 분).** 16차원 중 7차원이 모바일 베이스의 월드 프레임 위치·자세입니다. 우리 스택은 고정 베이스이므로 이 성분이 없습니다. 패밀리 A 에서 sp 가 낸 ↑7.0 이 전역 위치 판독 효과라면, 고정 베이스에서는 sp 의 우위가 사라지고 매크로에서 유일하게 구간이 0을 배제했던 근거도 함께 약해집니다. 논문 안에서 이 성분을 분리한 ablation 은 없으므로, 우리 쪽 첫 실험에서 직접 분리해야 합니다.
3. **동결 백본에서 vp 재현 (기존 파이프라인 1회 학습).** D19 v1 동결 하에서 vp 를 학습해, full FT 전제에서만 성립하는 이득인지 확인합니다. 재현되지 않으면 이중 경로 config 자체가 불필요해지므로 설계가 단순해집니다 — 실패해도 이득인 실험입니다.
4. **접촉 모달리티의 시간 상수 확인 (시뮬 로그 분석).** $`K{=}8`$ 은 운동학 state 기준 경험값입니다. 슬립 발생은 수 ms 규모라 정책 루프 30Hz 기준 8프레임(약 0.27초)은 이미 사후 관측일 수 있습니다. tactile 히스토리에는 별도의 $`K`$ 스윕이 필요하며, 운동학 $`K`$ 와 촉각 $`K`$ 를 같은 값으로 묶는 config 는 처음부터 만들지 않는 편이 낫습니다.
5. **패밀리 C 열화가 우리 주력 태스크에 걸리는지 (소규모 스윕).** 긴 히스토리가 가장 크게 해친 패밀리가 좁은 작업공간·국소 정밀 태스크입니다. in-hand 재배향은 정확히 그 성격이므로, 우리 스택에서는 히스토리가 **음의 효과**를 낼 가능성이 논문 평균보다 높습니다. Phase 1 데모에서 $`K \in \{1, 4, 8\}`$ 만 좁게 스윕해 부호부터 확인합니다.
6. **copycat / causal confusion 진단 (평가 프로토콜 추가).** 히스토리를 켠 정책이 시각 실패를 무시하고 자기 궤적을 복사하는지, 시각 입력을 교란한 롤아웃(카메라 가림·객체 위치 이동)에서 성공률이 비정상적으로 유지되는지로 확인합니다. 이 논문은 이 진단을 수행하지 않았고, 관련 연구에서 위험만 인용했습니다.
7. **시뮬 완벽 state 대 실기 노이즈 state (실기 전환 시).** 시뮬 state 에는 인코더 노이즈·지연·캘리브레이션 드리프트가 없습니다. 8프레임 히스토리는 노이즈를 8배로 들여오는 구조이기도 하므로, 실기에서는 필터링·다운샘플링 없이 원시 히스토리를 넣는 선택이 시뮬 결과와 정반대로 작동할 수 있습니다.
8. **손가락별 토큰 × 히스토리의 학습 안정성 (본격 학습 전 소규모).** 이 논문의 프레임당 1토큰과 달리 우리는 프레임당 12토큰입니다. 96개 state 토큰이 액션 suffix 를 지배해 시각 조건화를 밀어낼 위험(§3.2 의 "state dominates vision" 경고)이 프레임당 1토큰 설정보다 12배 큽니다. 모달리티 드롭아웃(D10 v1 에 이미 포함)을 히스토리 도입과 **동시에** 켜는 것이 안전합니다.

---

## 💡 컨텍스트 제안

- **P2 §5 방법론 base 추가 제안** — 이 논문을 `context/P2.md` §5 "Methodology base (non-pinned)" 에 추가. 역할 문구 예: "state 인터페이스 통제 비교(5 인터페이스 × K=1–96 × 주입 경로); D10/D11 배선·시간 깊이 근거". 핀 슬롯(현재 5/8)을 쓸 만큼 우리 촉각 축과 직접 겹치지는 않으므로 non-pinned 가 적절합니다.
- **D5 에 시간 깊이 축 추가 제안** — 현재 D5 는 "입력 모달리티 분리 + 제어율 분리" 두 축만 다룹니다. **proprio/tactile 히스토리 깊이 $`K`$** 를 세 번째 tracked 변수로 추가하고, v1 기본값을 $`K{=}1`$ (현행 암묵값)로 명시한 뒤 위 실패 모드 5의 스윕 결과를 트리거로 두는 것을 제안합니다.
- **D11 에 토큰 수 × 히스토리 비용 각주 제안** — 손가락별 12토큰 구성에 히스토리를 곱하면 액션 prefix 토큰이 96개가 되고, 이는 디노이징 스텝마다 반복 처리됩니다. D11 v1 의 "swappable sensor head + common token format" 옆에 **히스토리 도입 시 토큰 집계/다운샘플링이 선결**이라는 조건을 붙이는 것을 제안합니다.
- **D4 우선순위 조정 검토 제안** — FiLM 단일 지점 v1 을 바꾸자는 제안은 아닙니다. 다만 "FiLM 지점 확장(다층화)"이 deferred 후보로 잡혀 있다면, 이 논문의 fm 결과(전 레이어 변조가 단순 prefix 결합을 넘지 못함 + 123.84M 파라미터)를 근거로 그 후보의 우선순위를 낮추는 것을 검토할 만합니다.
- **P0 D26 벤치마크 트래킹 제안** — RoboCasa365 ([arXiv:2603.04356](https://arxiv.org/abs/2603.04356))를 `context/P0.md` 의 sim 벤치마크 트래킹 목록에 추가. 우리가 필요로 하는 접촉 집약적 다지 조작 평가는 없지만, **사전 분할 태스크 패밀리 + composite 계층 + 슬롯 정합 대조군**이라는 프로토콜 형식 자체가 D26 의 "eval 하니스" 범위에 정확히 들어맞습니다.
