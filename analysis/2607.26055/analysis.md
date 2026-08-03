# Paper Analysis — πR²: Reactive Real-time Flow Policies

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | πR²: Reactive Real-time Flow Policies |
| 저자 | Sungjae Park, Shubham Tulsiani (Carnegie Mellon University) |
| 링크 | [arXiv:2607.26055](https://arxiv.org/abs/2607.26055) |
| 발행일 / 버전 | 2026-07-28 · v1 |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-08-02 |
| 관련 Pillar | P1, P3, P2, P4 |
| 태그 | vla-arch, flow-matching, force |

arXiv 원문 제목은 LaTeX 표기(`\pi\mathbf{R}^2`)를 포함하므로, 위 표에는 색인이 읽는 평문 형태로 적었습니다. 본문 전반에서는 $`\pi\mathbf{R}^{2}`$ 표기를 씁니다.

본문에 프로젝트 페이지 `https://pi-r2-flow.github.io/` 가 명시되어 있으나, 현재 환경의 네트워크 정책이 해당 호스트로의 연결을 차단해(`curl: (56) CONNECT tunnel failed, response 403`) 해석 여부를 확인하지 못했으므로 `링크` 행에서 제외했습니다. 코드 저장소는 본문 어디에도 제시되지 않았습니다 (♻️ 재현성 참조).

---

## 🧭 한 줄 요약 (TL;DR)

$`\pi\mathbf{R}^{2}`$ 는 action chunking 플로우 정책의 조건화를 **매 tick 갱신되는 fast 채널(proprioception)** 과 **비동기 갱신되는 slow 채널(vision-language 특징)** 로 쪼개고, 여기에 in-flight 액션을 inpaint 조건으로 물리는 **지연 적응형 계단 노이즈 스케줄**을 얹어 호출당 1 NFE 로 액션을 방출합니다. 그 결과 GR00T-N1.7 을 그대로 쓰면서도 폐루프 replanning 이 약 $`4\times`$ 빨라지고(A5000 기준 25 Hz), 시뮬레이션 최대 23 %p · 실환경 최대 30 %p 의 성공률 향상을 보고합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — 대형 백본 위에 올린 action-chunking 플로우 정책은 예측한 chunk 를 open-loop 로 실행하기 때문에, 실행 중 들어오는 감각 입력에 반응하지 못합니다. 반응성(reactivity)을 되찾으려면 replanning 주기를 줄여야 하는데, perception-to-action 경로 자체가 너무 느려 그것이 불가능합니다.
- **기존 접근의 한계** — RTC / Train-Time RTC 계열은 chunk 경계의 불연속만 해결하며, 매 호출마다 무거운 semantic 백본을 통째로 한 번 더 통과시켜야 한다는 지연의 근원은 건드리지 않습니다. Streaming Diffusion Policy 계열은 diffusion forcing 으로 점진 방출을 하지만 소형 visuomotor 정책을 동기 실행하는 전제에 묶여 있습니다.
- **본 논문의 가설** — 모든 입력 모달리티가 같은 주기로 갱신될 필요는 없다는 것입니다. proprioception 은 이미지·언어보다 몇 자릿수 싸게 취득·처리되고, 동적 과제에서 국소 반응 보정에 필요한 정보를 충분히 담고 있으므로, vision-language 는 낡아도 되고 proprioception 만 매 tick 신선하면 폐루프 제어가 성립한다는 주장입니다.
- **왜 지금 중요한가** — GR00T-N1.7 급 VLA 의 호출당 지연은 A6000 기준 약 140 ms (50 Hz 제어 기준 약 7 tick)이며, 이 상태로는 접촉이 발생한 뒤 반응하기까지 chunk 하나가 끝나야 합니다. 비파지·접촉 집약적 조작을 VLA 로 가져가려면 이 지연 구조 자체를 재설계해야 합니다.
- **설계 제약** — 해법은 기존 아키텍처에 최소 변경으로 얹혀야 하고(사전학습 백본 무변경), 사전학습된 정책으로부터 fine-tuning 만으로 획득 가능해야 하며, 하드웨어마다 다른 실측 지연에 **하나의 학습된 모델**이 적응해야 한다는 것이 저자들의 실무 기준입니다.

---

## 🧩 핵심 기여

- **Proprioception-Reactive Diffusion Forcing** — DiT 액션 헤드의 조건화를 slow 채널(VLM·이미지/텍스트 인코더 특징)과 fast 채널(proprioception)로 분리하고, slow 채널을 백그라운드 스레드에서 비동기 갱신해 액션 헤드가 백본 크기와 무관하게 호출당 1 NFE 로 동작하게 만듭니다.
- **학습 시점 slow-채널 지연 주입 + 지연 임베딩** — 학습 중 $`d_{\mathrm{vis}}\sim\mathrm{Uniform}\{0,\dots,d_{\mathrm{vis}}^{\max}\}`$ 로 이미지를 과거 프레임으로 대체하고, 정수 지연값을 룩업 테이블 임베딩으로 DiT 에 주입해 배포 시 실측 지연을 같은 경로로 흘립니다.
- **지연 적응형 계단(staircase) 노이즈 스케줄** — chunk 를 세 구역(clamp 된 clean front $`[0,d)`$ / 선형 ramp 인 interior $`[d,H-d)`$ / 순수 노이즈 tail $`[H-d,H)`$)으로 나눈 per-position 스케줄을 제안하고, 학습 시 $`d`$ 를 무작위화해 하나의 모델이 가변 지연에 적응하게 합니다.
- **호출당 1 NFE 방출 사이클** — 한 번의 Euler substep 이 스케줄을 $`d`$ 슬롯만큼 오른쪽으로 밀어 $`d`$ 개의 clean 액션을 방출하고, 버퍼가 $`d`$ 만큼 슬라이드하며 뒤에 노이즈 슬롯을 붙여 스케줄이 정확히 재생산되도록 설계했습니다.
- **최소 아키텍처 변경** — DiT 의 공유 AdaLN 변조를 chunk 위치별 $`(\gamma_{p},\beta_{p})`$ 쌍으로 바꾸는 한 줄 수준 변경만으로 기존 플로우 액션 헤드에 이식되며, 사전학습 파라미터에서 초기화되므로 GR00T-N1.7 fine-tuning 으로 획득됩니다.
- **실기 검증** — xArm6 + XHand 실환경 4개 접촉 집약 과제에서 최강 baseline(Train-Time RTC) 대비 모든 지표를 앞서며, 반응성이 결정적인 과제에서 약 20–30 %p 절대 향상을 보고합니다.

---

## 🔑 기술 키워드

- **Diffusion Forcing** — chunk 의 각 위치에 서로 다른 노이즈 레벨을 독립적으로 부여하는 확산/플로우 일반화. 한 장의 사진 전체를 동시에 현상하는 대신, 앞쪽 필름부터 순서대로 현상해 두는 것과 같아 앞쪽 액션을 먼저 확정할 수 있습니다.
- **Fast/Slow Channel Split** — 조건화 입력을 매 제어 tick 갱신되는 fast 채널(proprioception)과 비동기 갱신되는 slow 채널(vision-language)로 나누는 본 논문의 핵심 구조. 눈은 가끔 깜빡여도 손끝 감각은 끊기지 않는 상태에 대응합니다.
- **Latency-Adaptive Flow Schedule** — 실측 추론 지연 $`d`$ 를 파라미터로 받는 per-position 노이즈 스케줄. 하나의 학습된 모델이 GPU·네트워크가 달라져도 그때그때 측정된 지연에 맞춰 스케줄을 재구성합니다.
- **Staircase Schedule** — clean front · 선형 ramp interior · 순수 노이즈 tail 의 3구역 스케줄 $`\boldsymbol{\tau}^{\star,d}`$. 계단을 한 칸 오르면 맨 앞 $`d`$ 칸이 완성되어 떨어져 나가는 구조입니다.
- **Inpaint Conditioning** — 추론 중 이미 실행 중인 in-flight 액션을 노이즈 없는 값으로 고정해 새 chunk 를 그 뒤에 이어 붙이도록 유도하는 조건화. 이미지 인페인팅의 액션 시퀀스판입니다.
- **Per-Position AdaLN** — DiT 블록을 노이즈 레벨로 변조하는 AdaLN 을 chunk 위치마다 별도의 $`(\gamma_{p},\beta_{p})`$ 로 분리한 변경. 위치마다 노이즈 레벨이 다른 diffusion forcing 을 기존 헤드에 얹기 위한 최소 개조입니다.
- **Delay Embedding** — 정수 지연값 $`d_{\mathrm{vis}}`$ 를 인덱스로 하는 학습된 룩업 테이블. slow 특징이 "얼마나 오래된 것인지"를 모델에 알려주는 나이표에 해당하며, zero-init 이라 학습 전에는 무지연 변형과 정확히 같습니다.
- **NFE (Number of Function Evaluations)** — 한 번의 정책 호출에서 수행하는 네트워크 순전파 횟수. 표준 플로우가 호출당 4–16 회를 쓰는 반면 본 논문은 1 회로 고정합니다.
- **Execution Horizon (h)** — 예측된 chunk 중 실제로 실행하는 액션 개수. 크면 open-loop 구간이 길어져 반응성이 떨어지고, 작으면 replanning 부하가 커지는 전형적 트레이드오프의 축입니다.

---

## 🔬 방법론

### 직관

문제의 뿌리는 "예측 한 번의 비용"과 "반응 주기"가 한 덩어리로 묶여 있다는 데 있습니다. 지금의 VLA 는 한 번 호출될 때마다 커다란 vision-language 백본을 통과시키고, 그 위에서 플로우 매칭 denoising 을 여러 번 돌린 뒤, 그렇게 얻은 액션 뭉치를 눈 감고 실행합니다. 실행하는 동안 손끝에 무엇이 닿아도 정책은 그것을 모릅니다. 반응성을 되찾는 유일한 방법은 더 자주 다시 예측하는 것인데, 예측이 비싸니 자주 할 수 없다는 순환에 갇힙니다.

본 논문은 이 덩어리를 두 방향에서 풉니다. 첫째, 모든 입력이 같은 속도로 갱신될 필요가 없다는 점을 이용합니다. 관절 각도·토크·지문 힘 같은 고유수용 신호는 읽어 오는 데도, 작은 MLP 로 처리하는 데도 거의 비용이 들지 않는 반면, 이미지 한 장을 VLM 에 통과시키는 일은 수십 ms 가 듭니다. 그리고 조작이라는 과제 자체가 이 비대칭과 잘 맞습니다 — 시각과 언어는 "어디로 갈지"라는 큰 그림을 주고, 손끝 감각은 "지금 얼마나 세게 쥘지"라는 미세 조정을 담당합니다. 그래서 시각 특징은 백그라운드 스레드에서 느긋하게 갱신해 캐시에 두고, 액션 헤드는 매 tick 신선한 고유수용 신호와 조금 낡은 시각 캐시를 함께 보며 돌아갑니다.

둘째, denoising 자체를 시간에 걸쳐 나눠 갚습니다. 표준 플로우는 chunk 의 모든 위치를 같은 노이즈 레벨에서 출발시켜 한 호출 안에 전부 깨끗하게 만들지만, diffusion forcing 을 쓰면 위치마다 다른 노이즈 레벨을 줄 수 있습니다. 그러면 chunk 의 앞쪽은 이미 거의 완성된 상태로 대기시켜 둘 수 있고, 호출 한 번에 substep 한 번만 돌려도 맨 앞의 몇 개는 완성되어 로봇으로 떨어져 나갑니다. 뒤쪽 위치들은 다음 호출들에서 계속 다듬어지되, 그때마다 더 신선한 관측을 보게 됩니다. 결과적으로 "예측 한 번의 비용"은 1 NFE 로 고정되고, 반응 주기는 제어 tick 에 붙습니다.

여기서 현실이 하나 끼어듭니다. 계산이 0 초에 끝나지는 않으므로, 새 chunk 가 도착할 때쯤이면 로봇은 이미 몇 개의 액션을 실행하고 있습니다. 본 논문은 그 in-flight 액션들을 chunk 맨 앞에 노이즈 없이 못 박아 두고(inpaint 조건), 그 뒤로 선형 ramp, 맨 뒤에 순수 노이즈를 붙인 계단 모양 스케줄을 씁니다. 지연이 $`d`$ tick 이면 앞 $`d`$ 칸이 못 박히고 호출 한 번에 $`d`$ 칸이 방출되어 스케줄이 자기 자신을 정확히 재생산합니다. 학습 때 $`d`$ 를 무작위로 뽑아 두었기 때문에, 배포 GPU 가 바뀌어 지연이 달라져도 같은 가중치가 그대로 적응합니다.

### 아키텍처

![Figure 1 — πR² 개요: fast/slow 채널 분리 + 3구역 적응 스케줄](https://arxiv.org/html/2607.26055/fig/concept_v5.png)

> "Figure 1: Overview of  $`\pi\mathbf{R}^{2}`$ . Top. While standard diffusion/flow matching relies on stale observations to predict actions via iterative denoising,  $`\pi\mathbf{R}^{2}`$  disentangles the observation into a fast channel (proprioception) and a slow channel (image encoding, VLM embedding, etc.), and uses up-to-date observations for each denoising step. Bottom. To incorporate latency and smooth execution, we adopt an adaptive noise schedule, where the action chunk is divided into three regions: clean actions to be taken during inference, actions with increasing noise level following Diffusion Forcing [9], and pure noise with the same length as clean actions. Compared to Train-Time RTC, this enables faster inference and smoother actions." (§1)
(위쪽 절반이 조건화 분리, 아래쪽 절반이 계단 스케줄 — 논문의 두 기여가 서로 직교한다는 주장을 한 장으로 보여 줍니다.)

출발점은 표준 VLA 의 관측 분해입니다. 관측 $`\mathbf{o}_{t}=(\mathbf{s}_{t},\mathbf{I}_{t},\mathbf{T}_{t})`$ 는 proprioception, 이미지, 언어로 이루어지고, 이미지·언어는 대형 백본을 통과해 language-aligned 특징이 되며 proprioception 은 작은 MLP 로 state embedding 이 됩니다. DiT 액션 헤드는 이 둘을 이어붙인 표현에 조건화되어 chunk 위에서 $`K`$ 회 denoising 을 돕니다. 문제는 두 경로의 비용이 전혀 대칭이 아니라는 점입니다.

> "On RTX A6000 with GR00T-N1.7, image preprocessing + VLM ( $`\sim 60`$  ms) plus DiT denoising ( $`K{=}4`$ steps, $`\sim 80`$  ms) sum to $`\sim 140`$  ms per call – $`\sim 7`$ control ticks at $`50`$  Hz." (§3.2)
(이 한 문장이 논문 전체 설계의 근거입니다. 백본과 denoising 이 각각 절반씩 지연을 만들고 있으므로, 둘 중 하나만 줄여서는 반응 주기가 제어 tick 근처로 내려오지 않습니다.)

이에 따라 조건화를 두 채널로 나눕니다.

- **slow 채널** — VLM 과 이미지/텍스트 인코더가 만드는 vision-language 특징. 백그라운드 `VLM_Worker` 스레드가 이미지를 계속 읽어 순전파를 돌리고, 완료될 때마다 캐시를 원자적으로 갱신합니다. 액션 헤드가 보는 slow 특징은 $`d_{\mathrm{vlm}}`$ tick 만큼 낡아 있습니다.
- **fast 채널** — proprioception. 매 제어 tick 로봇 센서에서 새로 읽어 공유 상태로 발행되며, 액션 헤드 호출마다 최신값이 스냅샷됩니다.

> "Per-call cost of the action head is therefore one NFE only, independent of backbone size." (§3.2)
(백본 크기가 커져도 액션 루프의 주기는 변하지 않는다는 뜻으로, "큰 백본을 유지하면서 실시간"이라는 논문의 제목을 성립시키는 지점입니다.)

낡음을 그냥 감내하는 대신 학습 시점에 명시적으로 주입합니다. slow 채널을 $`d_{\mathrm{vlm}}\sim\mathrm{Uniform}\{0,\dots,d_{\mathrm{vlm}}^{\max}\}`$ 만큼 지연시키고, 그 정수 지연을 인덱스로 하는 학습된 임베딩을 slow 표현에 더해 배포 시 실측 지연도 같은 임베딩을 거치게 합니다. 실환경 구현에서는 $`(d_{\mathrm{vis}}^{\max}{+}1)`$ 항목짜리 룩업 테이블 $`e(d_{\mathrm{vis}})`$ 가 DiT 의 액션 토큰 특징에 더해지며(chunk $`H`$ 위치에 broadcast), 룩업 테이블은 zero-init 이라 학습 전 체크포인트가 무지연 변형을 정확히 재현합니다.

아키텍처 개조는 의도적으로 최소화되어 있습니다.

> "The procedure above plugs into any DiT-style flow matching action with a one-line architectural change: the AdaLN conditioning (which modulates each DiT block by the noise level $`\tau`$ ) becomes per-position, with one $`(\gamma_{p},\beta_{p})`$ pair per chunk position rather than one shared across positions." (§3.3)
(attention·MLP·백본·채널 경로는 그대로 두고 변조 헤드만 위치별로 분리한다는 것이며, 이 때문에 사전학습 VLA 를 백본에 손대지 않고 fine-tuning 할 수 있습니다. 시뮬레이션의 Conditional U-Net 1D 헤드에서는 같은 변경이 공유 FiLM projection → 위치별 FiLM 으로 나타납니다.)

### 학습 목표 / 손실

기반은 action chunking 을 얹은 표준 플로우 매칭입니다. 속도장 $`v_{\theta}(\mathbf{x}_{t},t)`$ 가 노이즈 $`p_{0}=\mathcal{N}(\mathbf{0},\mathbf{I})`$ 에서 데이터 $`p_{1}=p_{\mathrm{data}}`$ 로 가는 수송을 학습하며, 보간 경로는 $`\mathbf{x}_{t}=(1{-}t)\,\boldsymbol{\epsilon}+t\,\mathbf{x}_{1}`$, 목표는 조건부 속도 $`u_{t}(\mathbf{x}_{t}\mid\mathbf{x}_{1})=\mathbf{x}_{1}-\boldsymbol{\epsilon}`$ 입니다 (식 1):

$$\mathcal{L}_{\mathrm{FM}}=\mathbb{E}_{t,\mathbf{x}_{1},\boldsymbol{\epsilon}}\!\left[\|v_{\theta}(\mathbf{x}_{t},t)-(\mathbf{x}_{1}-\boldsymbol{\epsilon})\|^{2}\right].$$

> "Crucially, all $`H`$ positions share a single noise level $`t`$ and the chunk is committed open-loop: the $`h`$ executed actions never account for new observations during their execution window, limiting the reactivity that manipulation tasks demand." (§3.1.1)
(모든 위치가 노이즈 레벨을 공유한다는 이 제약이 open-loop 커밋의 구조적 원인이라는 진단이며, 이후의 모든 변경이 바로 이 공유를 깨는 작업입니다.)

diffusion forcing 은 위치 $`p\in\{0,\dots,H{-}1\}`$ 마다 독립적인 노이즈 레벨 $`\tau_{p}\in[0,1]`$ 을 부여해 이 공유를 해제합니다 (식 2):

$$\mathbf{x}_{\tau,p}=(1{-}\tau_{p})\,\boldsymbol{\epsilon}_{p}+\tau_{p}\,\mathbf{a}_{p},$$

모델은 $`v_{\theta}(\mathbf{x}_{\tau},\boldsymbol{\tau},\mathbf{o})`$ 로 위치별 속도를 예측합니다. 여기까지는 선행 연구(Streaming Diffusion)와 공유하는 토대이며, 본 논문의 기여는 이 위에 얹는 **스케줄의 형태**입니다.

> "A naive linearly increasing noise schedule, as in standard streaming diffusion [14], does not address this regime: it implicitly assumes $`d=0`$ (instantaneous inference, no in-flight actions), so when applied at $`d>0`$ the returning chunk can jump at the chunk boundary [6, 29]." (§3.3)
(선형 ramp 만으로는 안 되는 이유가 명확합니다 — 지연이 0 이 아니면 새 chunk 가 이미 실행 중인 액션과 이어지지 않아 경계에서 튑니다.)

목표 지연 $`d`$ 에 대해 3구역 계단 $`\boldsymbol{\tau}^{\star,d}\in[0,1]^{H}`$ 를 다음과 같이 정의합니다 (식 3):

```math
\tau^{\star,d}_{p}=\begin{cases}1&0\leq p<d\\[2.0pt]
1-\dfrac{p-d}{H-2d}&d\leq p<H-d\\[6.0pt]
0&H-d\leq p\leq H-1\end{cases}
```

interior 의 기울기는 $`s=1/(H{-}2d)`$ 이며, 각 구역의 역할은 서로 다릅니다.

- **front $`[0,d)`$** — 실행 중인 in-flight 액션. clean 으로 clamp 되어 inpaint 조건 역할만 합니다.
- **interior $`[d,H-d)`$** — clean 에서 noise 로 가는 선형 ramp. 호출 한 번의 substep 으로 앞부분이 완성되도록 하는 구간입니다.
- **tail $`[H-d,H)`$** — 매 사이클 뒤에 새로 붙는 $`d`$ 개의 순수 노이즈 슬롯.

> "This staircase can be viewed as a diffusion-forcing generalization of training-time RTC [7]: both clamp a clean front of $`d`$ in-flight actions for inpaint conditioning, but RTC applies a single shared noise level over the remaining $`H-d`$ positions, whereas the staircase replaces it with a ramped interior plus a pure-noise tail to enable single-step emission under diffusion forcing." (§3.3)
(Train-Time RTC 와의 관계를 논문 스스로 못 박는 문장입니다. front clamp 는 동일하고, 차이는 나머지 $`H-d`$ 를 공유 레벨로 둘 것인가 ramp + tail 로 구조화할 것인가이며, 후자여야만 1 NFE 방출이 가능합니다.)

학습 절차는 배치마다 $`d\sim\mathrm{Uniform}\{1,\dots,d_{\mathrm{max}}\}`$ 를 뽑아 $`\boldsymbol{\tau}^{\star,d}`$ 를 만들고, front $`d`$ 슬롯을 ground-truth 액션으로 채운 뒤 마스크 $`m_{p}=\mathbf{1}[p\geq d]`$ 로 손실에서 제외합니다(추론 시 inpaint 조건화를 그대로 흉내). interior 와 tail 은 계단 레벨로 노이즈를 입혀 위치별 MSE 에 기여합니다. 여기에 두 가지 정규화 장치가 붙습니다.

- **대칭 jitter** — $`\tau_{p}\leftarrow\mathrm{clip}(\tau^{\star,d}_{p}+\delta_{p},0,1)`$, $`\delta_{p}\sim\mathrm{Uniform}[-j,j]`$. 호출별 $`d`$ 변동에서 생기는 중심 계단으로부터의 작은 이탈을 흡수합니다.
- **표준 플로우 warm-up 분기** — 확률 $`p=0.2`$ 로 계단 대신 전 위치 공유 $`\tau\sim\mathrm{Uniform}[0,1]`$ · 마스크 없음의 표준 스케줄로 학습해, 같은 네트워크가 에피소드 시작 시 순수 노이즈에서 chunk 전체를 denoise 할 수 있게 합니다.

최종 손실은 위치별 마스킹 MSE 입니다 (Alg. 1, line 19):

$$\mathcal{L}\leftarrow\sum_{p=0}^{H-1}m_{p}\,\|\hat{\mathbf{v}}_{p}-(\mathbf{a}_{p}-\boldsymbol{\epsilon}_{p})\|^{2}$$

### 추론 사이클

에피소드 시작에서는 표준 플로우 추론으로 $`H`$ 위치를 모두 denoise 해 버퍼를 warm-start 하고, 초기 실측 $`d`$ 에 맞춰 $`\boldsymbol{\tau}^{\star,d}`$ 로 재노이즈합니다. 이후 매 호출은 위치별 전진량 $`\Delta\tau_{p}`$ 를 갖는 Euler substep 한 번입니다 (식 4):

$$\mathbf{x}_{p}\;\leftarrow\;\mathbf{x}_{p}+\Delta\tau_{p}\cdot v_{\theta}(\mathbf{x},\boldsymbol{\tau},\mathbf{o})_{p},\qquad\tau_{p}\;\leftarrow\;\tau_{p}+\Delta\tau_{p},$$

> "with region-dependent per-position advances $`\Delta\tau_{p}`$ chosen so the schedule shifts right by $`d`$ slots: positions $`[d,2d)`$ reach $`\tau{=}1`$ and are emitted, and the rest of the buffer rotates forward (Fig. 2b)." (§3.3)
(스케줄이 정확히 $`d`$ 칸 밀리도록 전진량을 잡았기 때문에, 방출과 슬라이드를 거친 뒤의 버퍼가 다시 $`\boldsymbol{\tau}^{\star,d}`$ 와 같아집니다. $`d`$ 가 유지되는 한 스케줄이 자기 자신을 정확히 재생산하고, $`d`$ 가 바뀌면 몇 호출에 걸쳐 새 $`\boldsymbol{\tau}^{\star,d}`$ 로 끌려갑니다.)

배포 루프(Alg. 2)는 세 개의 실행 흐름으로 구성됩니다. 메인 루프는 제어 tick(25 Hz)마다 신선한 proprioception 을 읽어 공유 상태에 발행하고 버퍼의 다음 액션을 로봇에 보냅니다. `Action_Worker` 는 fast 관측 스냅샷과 캐시된 slow 특징을 받아 $`d_{\mathrm{vis}}\leftarrow\mathrm{round}\big((t_{\mathrm{state}}-t_{\mathrm{image}})/T_{\mathrm{ctrl}}\big)`$ 로 캐시 나이를 계산하고, $`d\leftarrow\max\big(1,\ \mathrm{round}(\mathrm{mean}(Q)/T_{\mathrm{ctrl}})\big)`$ 로 최근 호출 지연의 롤링 평균에서 $`d`$ 를 자동 유도한 뒤 1 NFE 를 돌립니다. `VLM_Worker` 는 이미지·언어를 계속 읽어 캐시를 원자적으로 갱신합니다. 즉 $`d`$ 는 하이퍼파라미터가 아니라 **런타임 측정값**입니다.

### 학습 셋업

**시뮬레이션.** MuJoCo Playground 의 Leap Cube Reorientation(16-DoF Leap Hand)을 쓰되 제어율을 20 Hz → 50 Hz 로 올리고 목표 분포를 blue-side-up 4개 yaw 포즈 $`\{0,{\pi/2},\pi,{3\pi/2}\}`$ 로 제한했습니다. 성공은 600 스텝 내 0.2 rad 이내 도달이며 100 에피소드로 평가합니다. 데이터는 서로 다른 시드의 PPO 전문가 4개가 각 50개, 총 200 궤적을 50 Hz 로 생성했고, 시뮬레이터가 관절각 $`[-0.05,0.05]`$ rad · 큐브 위치 $`[-0.02,0.02]`$ m · 쿼터니언 scale 0.1 가우시안 노이즈를 주입한 상태로 기록됩니다. 관측은 proprioception 32-dim(노이즈 관절각 16 + 관절별 추종 오차 16)과 vision-derived 큐브 포즈 9-dim(palm-to-cube 위치 오차 3 + 월드 프레임 절대 자세 6)이며, 이 9-dim 부분집합이 §3.2 의 slow 채널 역할을 대신합니다. 액션은 50 Hz 의 16-dim 상대 관절 명령으로 $`\mathbf{a}_{t}\in[-1,1]^{16}`$ 에 0.5 를 곱해 현재 모터 타깃에 더합니다. 헤드는 모든 변형이 공유하는 Conditional U-Net 1D ($`H{=}16`$, $`n_{\mathrm{obs}}{=}2`$)이며 FiLM 변조를 위치별로 분리한 것만 다릅니다. $`d_{\mathrm{max}}{=}5`$, warm-up 확률 0.2, AdamW($`\beta{=}[0.95,0.999]`$), peak LR $`1{\times}10^{-4}`$, cosine · 500-step warm-up, weight decay $`1{\times}10^{-6}`$, grad-norm clip 1.0, 배치 256, A5000 1장, 800 epoch 입니다.

주의할 점은 시뮬레이션에서는 지연 임베딩이 쓰이지 않는다는 것입니다.

> "In this setting we find that neither delayed-visual-state sampling at training nor the learned delay embedding is necessary: the env already injects sensor noise on this subset at every step, so the policy is already tolerant to perturbed slow inputs out of the box." (§A.1)
(즉 학습된 지연 임베딩 메커니즘은 실환경 실험에서만 실제로 학습·검증되며, 시뮬레이션 수치는 계단 스케줄과 채널 분리의 효과만을 보여 줍니다.)

**실환경.** 6-DoF xArm6 + 손목의 12-DoF XHand, 오버헤드 `640×480` RGB 카메라 1대 구성입니다. GR00T-N1.7 을 fine-tune 하되 Qwen-VL 백본과 Eagle-2 비전 인코더는 동결하고 액션 헤드(state/action projector, position embedding, DiT)만 학습하며, 아키텍처 변경은 DiT 의 공유 AdaLN → 위치별 $`(\gamma_{p},\beta_{p})`$ 하나뿐입니다. 위치별 파라미터는 사전학습된 공유 쌍에서 초기화되어 position-uniform 스케줄에서 출발합니다. proprioception 은 45-dim(xArm6 관절각 6 + XHand 관절각 12 + 관절별 토크 12 + 지문 힘 15 = 5개 센서 지문 × 3축)이고, 액션은 25 Hz 의 $`H{=}50`$ 절대 관절 위치 타깃(2 s 분량)으로 매 tick 하나씩 각 드라이버에 전송됩니다. 학습은 $`8\times`$ A5000/A6000, fused AdamW, peak LR $`1{\times}10^{-4}`$, cosine · 5 % warm-up, weight decay $`1{\times}10^{-5}`$, grad clip 1.0, 배치 512, bf16 + tf32 이며 과제별 40,000 / 28,000 / 49,000 / 4,550 스텝(≈ 200/100/100/100 epoch)입니다. 배포는 baseline 이 A5000 1장, $`\pi\mathbf{R}^{2}`$ 가 2장(slow VLM 과 fast DiT 가 연산·메모리 대역을 공유하지 않도록)입니다.

---

## 📊 실험 설정과 결과

### 시뮬레이션 — 실행 지평 $`h`$ 스윕 (지연 0)

첫 연구는 추론 지연 $`d=0`$ 을 가정해 두 가지를 분리합니다: (i) 과제 성능과 실행 지평 $`h`$ 의 트레이드오프, (ii) 호출당 1 NFE 로 분할 상환한 denoising 이 $`h{=}1`$ 표준 플로우의 반응성을 따라잡는지. 표준 플로우는 평가 시 chunk 전체를 16 스텝으로 denoise 하고 $`h\in\{1,2,4,8\}`$ 를 스윕하며, $`\pi\mathbf{R}^{2}`$ 는 호출당 액션 1개를 1 NFE 로 방출합니다.

> "Intuitively, the performance of standard flow degrades as $`h`$ grows, confirming the $`h`$ tradeoff for reactive tasks. Meanwhile,  $`\pi\mathbf{R}^{2}`$ matches the flow configuration of standard flow $`h\in\{1,2\}`$ ." (§4.1.1)
(핵심은 "따라잡는다"이지 "이긴다"가 아닙니다. 지연이 없는 이상적 조건에서 $`\pi\mathbf{R}^{2}`$ 의 가치는 성능 향상이 아니라 **같은 성능을 1/16 의 호출당 비용으로** 낸다는 데 있습니다.)

### 시뮬레이션 — VLA 급 지연 하 배포 연구

현실적 지연을 넣기 위해 GR00T-N1.7 의 계산 비용(§3.2)을 단위화합니다. 단위 지연 $`d_{0}`$ 를 $`K=4`$ denoising 비용으로 정의하면 vision/text 처리는 $`\approx 0.75\,d_{0}`$, 1 NFE 는 $`d_{0}/4`$ 가 됩니다. 그 결과 방법별 유효 호출 지연은 아래와 같이 갈립니다.

| 방법 | 유효 호출 지연 | $`d_{0}\in\{1,2,3\}`$ 에서의 실효 proprio 지연 $`d`$ | 성공률 ($`d_{0}=1,2,3`$) |
|---|---|---|---|
| naive-async | $`1.75\,d_{0}`$ | 2 / 4 / 6 | 0.33 · 0.29 · 0.22 |
| train-time RTC | $`1.75\,d_{0}`$ | 2 / 4 / 6 | 0.36 · 0.32 · 0.19 |
| $`\pi\mathbf{R}^{2}`$ w/o async | $`1.0\,d_{0}`$ | 1 / 2 / 3 | (본문 수치 미제시) |
| $`\pi\mathbf{R}^{2}`$ w/ async | $`0.25\,d_{0}`$ | 1 / 1 / 1 | 0.43 · 0.42 · 0.45 |

모든 방법에서 실행 지평은 $`h=d`$ 로 맞추었고, async 변형에는 물체 포즈를 $`d_{vis}\in\{1,2,3\}`$ 만큼 추가 지연시켰습니다.

> "$`\pi\mathbf{R}^{2}`$ w/ async wins at every $`d_{0}`$ ( $`0.43`$ , $`0.42`$ , $`0.45`$ ), beating naive-async ( $`0.33`$ , $`0.29`$ , $`0.22`$ ) and Train-time RTC ( $`0.36`$ , $`0.32`$ , $`0.19`$ ) with margins that widen as delay grows." (§4.1.2)
(초록의 "최대 23 %" 는 $`d_{0}=3`$ 에서 0.45 대 0.22 의 차이입니다. 주목할 점은 $`\pi\mathbf{R}^{2}`$ 만 지연이 커져도 성능이 거의 평평하다는 것 — baseline 은 $`d`$ 가 2→6 으로 늘어나며 무너지는데, async 변형은 proprio 지연이 항상 1 에 고정되고 시각 지연만 증가하기 때문입니다.)

![Figure 3a — 실행 지평 h 스윕](https://arxiv.org/html/2607.26055/fig/sim_A.png)

![Figure 3b — 단위 지연별 성공률](https://arxiv.org/html/2607.26055/fig/sim_B_bar.png)

> "Figure 3: Simulation results. Left. Without any inference delay, executing a smaller number of actions within the chunk benefits the performance for a flow matching policy.  $`\pi\mathbf{R}^{2}`$  also achieves the same performance via replanning every timestep, while the only last denoising step is conditioned on up-to-date state. Right. When there is an inference delay for each component,  $`\pi\mathbf{R}^{2}`$  reduces the effective delay $`d`$ by reducing the number of denoising steps and asynchronously processing the visual features. For each datapoint, $`d`$ indicates the effective delay of proprioception, while $`d_{v}`$ is visual delay. We train 3 policies with different seeds for each method and report the mean and std of the success rate." (§4.1)
(왼쪽이 $`h`$ 트레이드오프, 오른쪽이 지연 하 배포 비교이며, 3 시드 평균과 표준편차로 보고됩니다.)

**ablation 해석.** 이 표에서 분리되는 것은 세 가지입니다. (1) naive-async → train-time RTC 는 *chunk 경계 연속성*만 추가한 것이며, $`d_{0}=1,2`$ 에서는 소폭 이득(0.33→0.36, 0.29→0.32)이지만 $`d_{0}=3`$ 에서는 오히려 역전됩니다(0.22→0.19). 즉 inpaint 조건화만으로는 큰 지연을 못 버팁니다. (2) $`\pi\mathbf{R}^{2}`$ w/o async 는 *계단 스케줄만*의 효과로 유효 지연을 $`1.75d_{0}`$ → $`1.0d_{0}`$ 로 줄이지만, 본문은 이 행의 성공률 수치를 제시하지 않아 두 기여의 정량 분해가 불완전합니다. (3) async 채널 분리가 붙어야 비로소 지연이 $`0.25d_{0}`$ 로 떨어지고 성능이 지연에 대해 평평해집니다.

### 실환경 — xArm6 + XHand, GR00T-N1.7 fine-tune

4개 접촉 집약 과제입니다. **Don't Spill**(공을 그릇에 넣고 그릇을 도마 위로, 흘리지 않고), **Tidy Up Book**(책 더미에서 한 권을 빼 바구니에), **Insert Box**(상자를 벽에 밀어 세운 뒤 책들 사이에 삽입), **Catch Book**(공에 맞아 떨어지는 책을 손바닥 안에서 잡기). 데모는 각각 200 / 300 / 300 / 100개이며, 셀당 $`N{=}20`$ 시행 · 30초 제한이고 Prog 는 하위 목표 달성 비율입니다(하위 목표 수 4 / 2 / 4 / 1).

> "Table 1: Real World Results. (xArm6 + XHand, fine-tuned GR00T N1.7). $`d`$ is the measured wall-clock inference delay in $`25`$ -Hz control ticks ( $`1`$ tick $`\approx 40`$  ms), which is the same as execution horizon $`h`$ for all methods other than synchronous inference." (§4.2, Table 1)
(지연이 곧 실행 지평이라는 점이 중요합니다 — 지연이 큰 방법은 자동으로 open-loop 구간도 길어져 두 손실이 겹칩니다.)

| Setting | Don't Spill SR | Prog | Tidy up Book SR | Prog | Insert Box SR | Prog | Catch Book SR |
|---|---|---|---|---|---|---|---|
| Flow, Synchronous ( $`h=10`$ ) | 4/20 | 16/80 | 4/20 | 9/40 | 11/20 | 56/80 | 4/20 |
| Flow, Naive Async, dense, TE [39] | 7/20 | 30/80 | 7/20 | 15/40 | 12/20 | 61/80 | 2/20 |
| Flow, Train-Time RTC [7] | 9/20 | 45/80 | 8/20 | 18/40 | 10/20 | 53/80 | 5/20 |
| $`\pi\mathbf{R}^{2}`$ | 10/20 | 55/80 | 12/20 | 24/40 | 16/20 | 68/80 | 11/20 |

> "$`\pi\mathbf{R}^{2}`$ with asynchronous vision–language inference operates near the per-control-tick limit ( $`d{=}1`$ at $`25`$  Hz, with occasional increases to $`d{=}2`$ under network delays), whereas all flow-based baselines incur the full GR00T pipeline latency of $`d\in{4,5}`$ ." (§4.2)
(측정된 지연 격차가 4–5배이며, 이것이 아래 성능 격차의 직접 원인이라는 것이 논문의 인과 주장입니다.)

> "Train-Time RTC [7] is the strongest baseline; however, $`\pi\mathbf{R}^{2}`$ outperforms it across all metrics, with the largest gains on reactivity-critical tasks such as Tidy Up Book, Insert Box, and Catch Book, achieving approximately $`20\sim 30`$ % absolute improvement." (§4.2)
(초록의 "실환경 최대 30 %" 는 Catch Book 의 11/20 대 5/20, 즉 55 % 대 25 % 입니다.)

**과제별 읽기.** Don't Spill 에서는 SR 격차가 10/20 대 9/20 으로 사실상 동률이지만 Prog 는 55/80 대 45/80 으로 벌어집니다 — 성공/실패 이분법보다 하위 목표 진행에서 차이가 먼저 드러나는 구조입니다. Insert Box 는 baseline 순위가 뒤집히는 유일한 과제로, Train-Time RTC(10/20)가 naive async(12/20)와 synchronous(11/20)보다도 낮습니다. 논문은 그 메커니즘을 명시합니다 — 이미 생성된 in-flight 액션이 정책을 최근 동작의 연장 쪽으로 편향시켜 실패 복구를 방해한다는 것입니다. 즉 inpaint 조건화는 매끄러움을 사는 대가로 **반응 전환의 관성**을 지불합니다. Catch Book 은 naive async 가 2/20 으로 synchronous(4/20)보다도 낮은데, 시간적 앙상블이 급격한 반응을 평균으로 뭉개기 때문으로 읽힙니다.

### 반응성 분석 — 힘 변조

![Figure 5 — 지문 힘 대 방출 액션 (Tidy Up Book)](https://arxiv.org/html/2607.26055/fig/proprio_book.png)

> "Figure 5: $`\pi\mathbf{R}^{2}`$ reacts to proprioception, while baselines run a stale plan (Tidy Up Book). Fingertip force (solid, left axis) and the emitted action (dashed, right axis) over time, for $`\pi\mathbf{R}^{2}`$ and Train-Time RTC; numbered markers link plot times to the overhead frames above. $`\pi\mathbf{R}^{2}`$ grips just enough ( $`\sim`$ 50 N), while RTC reacts late and over-grips to $`\sim`$ 120 N, dropping the book." (§4.2)
(성공률이라는 집계 지표 뒤에 있는 물리적 메커니즘을 한 장으로 보여 주는 그림입니다.)

> "Because $`\pi\mathbf{R}^{2}`$ refreshes proprioception at every denoising step, it modulates its grip from live force feedback and stops near $`\sim`$ 50 N, gripping just enough to reorient the book. Train-Time RTC instead commits to a stale plan and reacts late, so it keeps pushing down after contact, and its middle-finger force overshoots to $`\sim`$ 120 N, crushing the book." (§4.2)
(50 N 대 120 N 이라는 2배 이상의 접촉력 오버슈트 차이가 성공률 격차의 실제 정체이며, 이는 우리 스택에서도 촉각/힘 채널로 직접 계측 가능한 종류의 수치입니다.)

부록 A.4 는 같은 패턴이 나머지 과제에서도 유지된다고 보고합니다 — Catch Book 에서는 RTC 가 늦게 반응해 책이 미끄러지고, Insert Box 에서는 RTC 의 검지 힘이 분포 밖으로 오버슈트하며, Don't Spill 에서는 RTC 의 엄지가 공에 닿지도 않은 채(엄지 힘 $`\approx 0`$) 동작을 계속합니다.

### 하이퍼파라미터 대조 (Tab. 2 / Tab. 5)

| 항목 | 시뮬 $`\pi\mathbf{R}^{2}`$ | 시뮬 baseline 편차 | 실환경 $`\pi\mathbf{R}^{2}`$ | 실환경 baseline 편차 |
|---|---|---|---|---|
| Chunk length $`H`$ | 16 | — | 50 | — |
| Observation history $`n_{\mathrm{obs}}`$ | 2 | — | 1 | — |
| Control rate | 50 Hz | — | 25 Hz | — |
| Train-time $`d_{\mathrm{max}}`$ | 5 | 10 (Train-time RTC); n/a (Flow) | 5 | 10 (Train-time RTC); n/a (Flow) |
| Train-time $`d_{\mathrm{vis}}^{\max}`$ | n/a (§A.1) | n/a | 5 | n/a |
| Delay-embedding lookup | n/a (§A.1) | n/a | 6 entries → DiT hidden dim | n/a |
| Standard-flow warm-up prob. $`\alpha`$ | 0.2 | n/a | 0.2 | 0 (Flow, Train-time RTC) |
| Inference budget / NFE per call | 1 | 15 (Train-time RTC, Flow) | 1 (one sub-chunk) | 4 (Flow, Train-time RTC; full chunk) |

시뮬레이션 baseline 은 $`\pi\mathbf{R}^{2}`$ 와 배치별 지연 샘플링 프로토콜을 공유하되(지수 감쇠 분포 $`p(d{=}k)\propto e^{-\alpha_{d}k}`$, $`\alpha_{d}{=}1`$), Flow 는 지연 샘플링·front clamp 없이 전 chunk 공유 $`\tau`$ 를 쓰고, Train-time RTC 는 같은 지연 샘플링에 뒤쪽 $`H{-}d`$ 위치를 공유 노이즈 레벨로 처리하며 $`d_{\max}=10`$ 을 씁니다.

---

## ⚖️ 한계

- **모델 외부 지연은 다루지 않음 (저자 명시)** — 추론 서버와 로봇 클라이언트 사이의 통신 지연은 범위 밖이라고 선언합니다. 그런데 본 논문의 스케줄은 실측 $`d`$ 를 롤링 평균으로 유도하므로, 네트워크 지터가 큰 배포에서는 $`d`$ 추정 자체가 흔들리고 버퍼가 계속 새 $`\boldsymbol{\tau}^{\star,d}`$ 로 끌려다니게 됩니다. 실환경 본문도 "네트워크 지연 하에서 간헐적으로 $`d{=}2`$ 로 증가"한다고 적고 있어, 이 취약점은 이미 관측 범위 안에 있습니다.
- **base 아키텍처를 그대로 둠 (저자 명시)** — proprioception 을 더 강조하는 설계(전용 어텐션 헤드 등)는 향후 과제로 남겼습니다. 이는 곧 "fast 채널이 정말 fine motor 를 이끄는가"가 아키텍처적으로 보장되지 않고 데이터에 맡겨져 있다는 뜻이며, 45-dim proprio 벡터가 DiT 조건화에서 수백 개의 시각 토큰에 묻힐 위험이 구조적으로 남습니다.
- **배포 계산 예산의 비대칭** — baseline 은 A5000 1장, $`\pi\mathbf{R}^{2}`$ 는 2장을 씁니다. 저자들은 한 GPU 공유가 DiT 지연을 측정 가능하게 부풀려 $`d`$ 측정을 오염시킨다는 이유를 밝히지만, 결과적으로 Table 1 의 격차는 "알고리즘 + 추가 GPU 1장"의 합입니다. GPU 1장 제약 하에서 얼마가 남는지는 미측정입니다.
- **두 기여의 정량 분해가 실환경에 없음** — 시뮬레이션에는 `w/o async` 행이 설계되어 있지만 본문에 성공률이 없고, 실환경 Table 1 에는 그 행 자체가 없습니다. 따라서 "계단 스케줄"과 "비동기 채널 분리" 중 실기 성능의 몇 %p 가 어느 쪽인지 논문 안에서는 확정할 수 없습니다.
- **지연 임베딩이 검증되는 실험이 사실상 하나** — §A.1 이 시뮬레이션에서는 지연 임베딩도 지연 샘플링도 불필요했다고 명시하므로, 이 메커니즘은 실환경 4개 과제에서만 학습됩니다. 그런데 실환경에는 지연 임베딩 유무 ablation 이 없어, 임베딩이 실제로 기여했는지 아니면 zero-init 상태 근처에 머물렀는지 구분되지 않습니다.
- **시각 낡음의 학습 범위가 좁음** — $`d_{\mathrm{vis}}^{\max}{=}5`$ tick(25 Hz 기준 200 ms)까지만 학습합니다. 조명 변화나 사람 개입처럼 200 ms 를 넘는 시각 변화가 실제로 중요한 상황에서 정책이 어떻게 행동하는지는 학습 분포 밖입니다. "vision 은 coarse guidance 만 준다"는 전제 자체가 시각 변화가 느린 과제에서만 성립할 수 있습니다.
- **baseline 설정의 교란 요인** — Train-Time RTC 는 $`d_{\max}=10`$ · NFE 4(실환경) / 15(시뮬)로, $`\pi\mathbf{R}^{2}`$ 의 $`d_{\max}=5`$ · NFE 1 과 다릅니다. 저자들은 RTC 의 실효 지연이 더 크기 때문이라 정당화하지만, 노이즈 스케줄과 계산 예산이 동시에 달라진 비교임은 사실입니다.
- **통계적 검정력** — 실환경은 셀당 20 시행 단일 fine-tune 이고 시드 분산이 없습니다. Don't Spill 의 10/20 대 9/20 은 잡음 범위이며, 결론을 지탱하는 것은 Catch Book(11/20 대 5/20)과 Insert Box(16/20 대 10/20) 같은 큰 격차입니다. 시뮬레이션은 3 시드 평균/표준편차를 보고해 상대적으로 견고합니다.
- **"최강 baseline"이 과제마다 다름** — Insert Box 에서는 Train-Time RTC 가 세 baseline 중 최하위이고 Catch Book 에서는 naive async 가 synchronous 보다도 낮습니다. 즉 baseline 순위가 안정적이지 않아, 단일 "최강 baseline 대비 +30 %" 표현은 과제 선택에 민감합니다.
- **힘 변조는 창발이지 설계가 아님** — 지문 힘 15-dim 이 45-dim proprio 벡터에 flat 하게 concat 될 뿐, 접촉 의미를 손가락 단위로 귀속시키는 구조는 없습니다. 50 N vs 120 N 의 인상적 결과는 "빠른 갱신"만으로 얻어진 것이며, 촉각 표현 설계로 얼마나 더 밀 수 있는지는 열려 있습니다.

---

## ♻️ 재현성

- **코드** — 본문 어디에도 코드 저장소 링크가 없습니다. 프로젝트 페이지 `https://pi-r2-flow.github.io/` 만 §초록에 제시되며, 현재 환경의 네트워크 정책이 해당 호스트를 차단해(`curl: (56) CONNECT tunnel failed, response 403`) 코드 공개 여부를 확인하지 못했습니다.
- **의사코드** — §A.3 이 학습 스텝(Alg. 1)과 배포 추론 루프(Alg. 2)를 라인 단위 의사코드로 제공합니다. 계단 구성, 마스킹, jitter, warm-up 분기, 롤링 윈도 $`d`$ 유도, VLM/Action 워커 분리까지 모두 명시되어 있어 코드 없이도 재구현 경로가 상당히 명확합니다.
- **하이퍼파라미터** — Tab. 2(시뮬)와 Tab. 5(실환경)가 옵티마이저·LR·스케줄·배치·정밀도·예산과 baseline 편차를 함께 제시합니다. jitter 폭 $`j`$ 의 구체적 값만 본문·표 어디에도 없습니다.
- **데이터** — 시뮬레이션 데이터는 MuJoCo Playground Leap Cube Reorientation 환경을 개조해(제어율 20→50 Hz, 목표 4 yaw 제한) PPO 전문가 4개로 생성하므로 원칙적으로 재생성 가능합니다. 실환경 데모(200/300/300/100개)는 공개 언급이 없습니다.
- **하드웨어** — 학습 $`8\times`$ A5000/A6000(24/48 GB), 배포 A5000 1장(baseline) / 2장($`\pi\mathbf{R}^{2}`$). 실기는 xArm6 + XHand + 오버헤드 RGB 1대로 비교적 접근 가능한 구성이며, 드라이버 설정(§Tab. 3: xArm6 `mode=1` streaming servo / `set_servo_angle_j`, XHand RS485 position mode, per-joint PID $`k_{p}{=}100,\ k_{i}{=}0,\ k_{d}{=}0`$, 토크 한계 300)과 과제별 언어 프롬프트(§Tab. 4)까지 공개되어 있습니다.
- **베이스 모델** — GR00T-N1.7 (NVIDIA) 로부터 fine-tune 하며 백본·비전 인코더는 동결이라, 공개 체크포인트가 있으면 액션 헤드만 재학습하면 됩니다.

---

## 🎯 관련 Pillar / Decision (P# / D#)

- **P1(Heterogeneous Body/Hand Action Expert) — 주 pillar.** 본 논문은 action-expert 의 **조건화 주기 설계**를 정면으로 다룹니다.
  - `D5`(input-modality + control-rate separation) — v1 은 `(ii) modality-separated + (α) shared rate` 입니다. 본 논문은 modality-separated 를 지지하는 동시에 `(α) shared rate` 를 정면으로 반박합니다: proprioception 은 매 tick, vision-language 는 비동기라는 **rate-separated** 조건화가 VLA 규모에서 구현 가능하고 20–30 %p 가치가 있음을 보였습니다. 우리 Decision Log 에서 이 논문이 가장 강하게 건드리는 지점입니다.
  - `D4`(Body↔Hand information sharing) — v1 은 `a_b → (γ,β)` FiLM 단일 지점 변조입니다. 본 논문의 per-position AdaLN/FiLM 은 같은 변조 계층을 **chunk 위치 축**으로 확장한 것이라, 우리 hand head 의 FiLM 이 body intent 와 노이즈 레벨 두 소스를 동시에 받아야 하는 설계 문제를 새로 만듭니다.
  - `D7`(π backbone integration / partition) — v1 은 `π0 action expert 를 slice 하고 양쪽 FT` 입니다. 본 논문은 백본 동결 + 액션 헤드만 학습이라는 더 보수적인 분할로 같은 효과를 얻었고, 아키텍처 변경을 AdaLN 한 줄로 제한했습니다. 우리 slice-후-FT 계획에 "변경 최소화" 참조점이 됩니다.
  - `D1`(split form) / `D6`(coordination direction & flow) — 직접 건드리지 않습니다. 본 논문은 단일 액션 헤드를 전제하며 Body/Hand 분할 자체는 논외입니다.
- **P3(Hand-level System0 Module, RL-scoped) — Identity 긴장.** `D13`(System0 role & operating regime)의 전제는 "System1 이 접촉 유지에 필요한 반응 속도를 못 낸다"입니다. 본 논문은 System1 급 VLA 정책 자체를 25 Hz 폐루프 힘 반응까지 끌어올렸고, Figure 5 의 50 N vs 120 N 은 정확히 System0 이 담당하려던 "과도한 힘 억제"입니다. System0 의 존재 이유가 사라지는 것은 아니지만 — 슬립 억제는 여전히 25 Hz 아래 시간 척도의 문제입니다 — **System0 의 정당화가 "System1 이 느리다"에서 "슬립은 25 Hz 로도 늦다"로 이동해야 합니다**. `D14`(System1↔System0 interface)의 binary gating 도, System1 이 이미 매 tick 힘을 보고 있다면 게이팅 신호의 정보량을 재검토할 여지가 생깁니다.
- **P2(Structured Multimodal Observation Fusion) — 지지와 반증 동시.** `D10`(heterogeneous modality fusion beyond concat)의 "비대칭 융합" 방향과 본 논문의 fast/slow 분리는 같은 정신이되 축이 다릅니다 — 우리는 *구조* 축(cross-attention/AdaLN), 논문은 *갱신 주기* 축입니다. 두 축은 직교하며 결합 가능합니다. 반대로 `D11`(proprio-tactile-force token construction)에는 반증 사례입니다: 논문은 관절 토크 12 + 지문 힘 15 를 45-dim 벡터에 flat 하게 concat 하고도 힘 변조를 얻었으므로, "per-finger 토큰화가 접촉 성능의 필요조건"이라는 우리 가정에 대한 저비용 대조군이 생깁니다.
- **P4(Pretraining for Data-Efficient Adaptation) — 지지.** `D19`(VLM backbone lineage & adaptation range)의 v1 `(a) full VLM freeze + action experts only` 를 그대로 실행한 사례입니다(Qwen-VL 백본 · Eagle-2 인코더 동결, 액션 헤드만 학습). `D23`(action representation × pretraining/preservation)의 `(iii) 연속 flow-matching head` 도 유지됩니다 — 본 논문의 변경은 헤드의 *표현*이 아니라 *노이즈 스케줄*이므로 D23 v1 은 그대로 살아 있습니다. `D20`(prior-preservation strategy) 은 백본 미접촉이라 별도 개입 없이 충족됩니다.
- **P0 / P5** — 직접 연결 없음. 새 데이터셋·벤치마크 기여가 없고(P0), 세계 모델도 다루지 않습니다(P5). 다만 §3 서두에서 "flow matching 액션 헤드 + 무거운 사전학습 백본" 구조면 world-action model 에도 동일하게 적용된다고 주장하므로, P5 의 auxiliary-head 통합안이 실현될 때 지연 구조를 재검토할 근거는 됩니다.
- **경쟁자 함의** — P1 §5 의 핀 논문 중 π0 는 본 논문이 개조 대상으로 삼는 계열 그 자체이고, Dexora / DexGrasp-VLA 는 액션 공간·분할 축이라 지연 축과 직교합니다. 본 논문의 등장으로 "반응성"은 더 이상 아키텍처 분할과 별개의 부차 지표가 아니라, action-expert 설계에서 함께 최적화되어야 할 1급 축이 됩니다.

---

## ✨ 핀 논문 대비 델타

- **vs π0 ([arXiv:2410.24164](https://arxiv.org/abs/2410.24164), P1 핀 · 백본)** — π0 의 flow-matching action expert 는 모든 chunk 위치가 노이즈 레벨을 공유하고 chunk 를 open-loop 로 커밋합니다. 본 논문은 그 헤드를 유지한 채 공유 노이즈 레벨만 위치별로 풀어, 백본을 건드리지 않고 반응 주기를 제어 tick 으로 내립니다. π0 계열에 대한 개조 비용이 AdaLN 한 줄이라는 점이 델타의 핵심입니다.
- **vs Train-Time RTC ([arXiv:2512.05964](https://arxiv.org/abs/2512.05964), 본 저장소 기분석 · 미핀)** — 논문 스스로 자신을 "training-time RTC 의 diffusion-forcing 일반화"로 규정합니다. 공통점은 in-flight $`d`$ 개를 clean 으로 clamp 하는 inpaint 조건화이고, 차이는 나머지 $`H-d`$ 를 RTC 가 단일 공유 노이즈 레벨로 두는 반면 본 논문은 ramp interior + 노이즈 tail 로 구조화해 **1 NFE 방출**을 가능하게 한다는 점입니다. 더 큰 델타는 RTC 가 손대지 않은 축 — RTC 는 여전히 호출마다 백본 전체를 통과시키므로, 비동기 slow 채널은 RTC 계열에 없던 새로운 기여입니다.
- **vs RTC ([arXiv:2506.07339](https://arxiv.org/abs/2506.07339), 본 저장소 기분석 · 미핀)** — 추론 시점 pseudoinverse guidance 를 학습 시점 조건화로 옮긴 것이 Train-Time RTC 였다면, 본 논문은 거기서 한 걸음 더 나아가 **denoising 예산 자체를 호출들에 걸쳐 분할 상환**합니다. 지연을 "견디는" 문제에서 "구조적으로 없애는" 문제로 프레임이 바뀝니다.
- **vs Dexora ([arXiv:2605.18722](https://arxiv.org/abs/2605.18722)) / DexGrasp-VLA ([arXiv:2511.00139](https://arxiv.org/abs/2511.00139), P1 핀)** — 두 핀 논문은 액션 공간과 해부학적 분할을 다루며 지연·반응성 축은 다루지 않습니다. 본 논문은 그 분할 논의와 완전히 직교하는 축을 추가하므로 대체가 아니라 결합 대상입니다.
- **vs ForceFlow ([arXiv:2605.11048](https://arxiv.org/abs/2605.11048)) / ViTacFormer ([arXiv:2506.15953](https://arxiv.org/abs/2506.15953), P2 핀)** — 두 논문은 힘·촉각을 *구조적으로* 융합하지만 모든 모달리티가 동기 갱신되는 것을 전제합니다. 본 논문은 구조를 단순화(flat concat)하는 대신 *갱신 주기*를 비대칭화해 접촉 반응을 얻었습니다. "구조 대 주기" 중 접촉 성능에 무엇이 더 기여하는지는 아직 어느 논문도 분리 측정하지 않았습니다.
- **vs GR00T N1 ([arXiv:2503.14734](https://arxiv.org/abs/2503.14734), P4 핀)** — GR00T 는 본 논문의 base 모델(N1.7)이며 dual-system 명명에도 불구하고 액션 헤드는 동기 실행입니다. 본 논문은 GR00T 의 "vision-language 모듈 → flow-matching 액션 헤드" 구조를 유지한 채 두 모듈의 **시간축을 분리**했습니다.

---

## ⚙️ 의사결정 함의

이 논문이 맞다면 우리 파이프라인에서 구체적으로 다음이 바뀝니다.

- **관측 딕셔너리를 `obs_fast` / `obs_slow` 로 이분** — `D5` 의 `(α) shared rate` 를 폐기하고, proprioception(관절각 · 관절 속도 · 관절 토크 · 지문 힘/촉각 요약)은 제어 tick 마다, VLM/비전 인코더 특징은 백그라운드 워커가 갱신하는 캐시로 분리합니다. 새 config 키: `obs_slow_async: true`, `d_vis_max: 5`, `delay_embed_table: (d_vis_max+1) × d_hidden` (zero-init).
- **액션 헤드의 노이즈 조건화를 위치별로 분리** — π0 액션 expert 의 AdaLN(또는 우리 hand head 의 FiLM)을 `{(gamma_p, beta_p)}_{p=0..H-1}` 로 확장하고, 사전학습된 공유 쌍에서 초기화합니다. 파라미터 수는 $`H`$ 배가 되지만 변조 헤드에 한정되므로 미미합니다. `D4` 와의 충돌 해결이 필수 설계 항목입니다 — body intent $`a_b`$ 로부터의 FiLM 과 노이즈 레벨 $`\tau_p`$ 로부터의 AdaLN 이 같은 블록에 두 변조를 걸어야 하므로, 합성 순서(가산 vs 직렬)를 명시적으로 정해야 합니다.
- **학습 루프에 계단 스케줄 분기 추가** — 배치마다 `d ~ Uniform{1..d_max}` (`d_max: 5`), $`\boldsymbol{\tau}^{\star,d}`$ 구성, front-$`d`$ 를 ground truth 로 채우고 `loss_mask = (p >= d)`, jitter `tau_jitter: j` 적용. 확률 `standard_flow_prob: 0.2` 로 표준 플로우 분기(공유 $`\tau`$, 마스크 없음)를 섞어 warm-start 능력을 유지합니다. 우리 손실 항 이름으로는 기존 flow-matching MSE 에 위치별 마스크가 곱해지는 형태입니다.
- **추론 예산을 `num_denoise_steps: 4` → `nfe_per_call: 1` 로 변경** — 대신 매 호출 Euler substep 의 위치별 전진량 $`\Delta\tau_{p}`$ 를 실측 $`d`$ 로부터 계산하고, $`d`$ 는 하이퍼파라미터가 아니라 최근 $`W{=}20`$ 회 호출 지연의 롤링 평균에서 유도합니다(`d_estimation: rolling_mean`, `d_window: 20`).
- **평가 메트릭에 지연·힘 축을 1급으로 추가** — 성공률만으로는 이 논문의 차이가 안 보입니다. 로깅에 (1) 호출당 실측 지연 $`d`$ (제어 tick 단위), (2) 실효 replanning 주파수 (Hz), (3) 접촉 이벤트 후 **지문 힘 피크값**(논문 기준 50 N vs 120 N 급 차이), (4) 하위 목표 진행률(Prog) — 성공/실패보다 먼저 갈리는 지표 — 를 넣습니다.
- **`D19` 는 유지, `D7` 은 재검토** — 백본 동결(D19 v1 (a))은 그대로 유효하고 오히려 강화됩니다. 반면 `D7` 의 "π0 action expert slice + 양쪽 FT" 는, 본 논문이 액션 헤드만 학습해 동일 효과를 냈다는 점에서 "양쪽 FT" 의 필요성을 먼저 반증해 볼 대상이 됩니다.
- **`D26`(benchmark/eval scouting scope, P0) 확장** — 우리 벤치마크 범위에 **반응성 스트레스 과제**(낙하 물체 포착, 접촉 후 힘 조절)를 추가합니다. 현재 in-hand rotation / articulated-tool 중심 평가 세트로는 이 논문이 만든 차이가 측정되지 않습니다.

---

## ⚠️ 먼저 검증할 실패 모드

가장 싼 확인부터 나열합니다.

1. **우리 촉각은 "fast" 가 아닐 수 있습니다 (가장 싼 체크, 학습 불필요).** 논문의 fast 채널 전제는 "proprioception 은 이미지보다 몇 자릿수 싸다"입니다. 그런데 우리 Sharpa Hand 의 Deform Map 은 지문당 약 `320×240` 이미지 @30 Hz 이므로, 처리에 CNN 인코더가 필요합니다. **먼저 할 일은 Deform Map CNN 순전파 1회의 벽시계 지연을 재는 것**입니다 — 이것이 DiT 1 NFE 보다 크면 촉각은 fast 채널이 아니라 slow 채널에 속하게 되고, 논문 구조를 그대로 옮길 수 없습니다. 학습 없이 벤치마크 한 줄로 판정됩니다.
2. **30 Hz 촉각이 반응 주기의 상한이 됩니다.** 논문 실기는 25 Hz 제어에 매 tick 신선한 proprioception 을 전제합니다. Deform Map 이 30 Hz 라면 촉각 기반 반응의 실효 상한이 33 ms 로 고정되어, 제어율을 50 Hz 로 올려도 촉각 채널만 낡습니다. 즉 우리 스택에서는 fast 채널 내부에서 또 한 번 rate 가 갈립니다 — 관절각/토크(고속)와 촉각 이미지(30 Hz). 두 단계 slow 채널이 필요한지 먼저 정해야 합니다.
3. **`D11` per-finger 토큰과 1 NFE 비용의 충돌.** 논문의 "호출당 1 NFE" 는 fast 채널이 작은 MLP 하나로 끝난다는 전제에서 나옵니다. 우리 D11 은 10 finger + 2 palm 토큰 + topology-aware 인코딩(D12)을 요구하므로 fast 경로의 토큰 수와 어텐션 비용이 늘어납니다. **비용 검증**: 우리 토큰 구성으로 액션 헤드 1 NFE 를 측정해 40 ms tick 안에 들어오는지 확인합니다. 안 들어오면 D11 을 fast/slow 로 다시 쪼개야 합니다(예: 접촉 이진 플래그만 fast, 촉각 임베딩은 slow).
4. **계단 스케줄의 존재 조건 $`H > 2d`$.** interior 기울기 $`s=1/(H{-}2d)`$ 가 정의되려면 $`H>2d`$ 여야 합니다. 논문 실기는 $`H{=}50`$, $`d{\approx}1\!\sim\!2`$ 라 여유가 크지만, 우리 모델이 더 무겁거나 원격 추론이면 $`d`$ 가 커집니다. Sharpa 22-DOF + arm 조합에서 예상 $`d`$ 를 먼저 추정하고 $`H`$ 하한을 정해야 합니다. 이는 논문에 명시된 실패 조건이 아니라 식에서 직접 따라오는 제약이므로, 우리 쪽에서 명시적으로 가드해야 합니다.
5. **Body/Hand 분할과 단일 $`d`$ 가정의 충돌.** 본 논문은 액션 헤드가 하나이고 지연도 하나($`d`$)라고 가정합니다. 우리 `D1` v1 은 shared trunk + split body/hand heads 이고 `D5` v1 은 shared rate 이므로 현재는 단일 $`d`$ 가 성립하지만, rate 분리를 도입하는 순간 Body 와 Hand 가 서로 다른 실효 지연을 갖게 될 수 있습니다. 그러면 계단 스케줄이 헤드마다 따로 필요합니다. **먼저 결정할 것**: rate 분리를 조건화(관측) 축에만 둘 것인가, 출력(액션 방출) 축까지 갈 것인가. 전자면 단일 $`d`$ 로 충분합니다.
6. **액션 공간이 inpaint 조건화에 적합한가.** 논문 실기는 절대 관절 위치 타깃(보간 가능)을, 시뮬은 상대 관절 명령을 씁니다. 우리 `D2` v1 은 both-wrist / tool-flange **포즈**(SE(3))입니다. in-flight 액션을 clean 으로 clamp 하고 그 뒤를 이어 붙이는 방식은 액션이 chunk 경계에서 매끄럽게 보간된다는 암묵 가정에 기대는데, 회전 표현에서는 이 가정이 표현 선택(quaternion / 6D / axis-angle)에 따라 깨질 수 있습니다. 저비용 sanity check: 우리 데모 데이터에서 인접 timestep 포즈 차분의 분포를 뽑아 계단 ramp 구간 폭 대비 불연속 크기를 확인합니다.
7. **지연 임베딩이 조용히 no-op 이 될 위험.** 룩업 테이블이 zero-init 이므로, 학습 중 $`d_{\mathrm{vis}}`$ 분포가 좁거나 slow 채널이 어차피 성능에 덜 기여하면 임베딩이 0 근처에 머물러도 손실이 줄어듭니다. 논문에도 이 ablation 이 없습니다. 우리 재현에서는 학습 후 임베딩 노름을 항목별로 찍어 실제로 분화했는지 확인하는 진단을 넣어야 합니다.
8. **2 GPU 배포 전제.** 논문은 slow VLM 과 fast DiT 를 별도 GPU 에 올려야 $`d`$ 측정이 오염되지 않는다고 명시합니다. 우리 실기 예산이 단일 GPU 라면 두 워커가 대역폭을 다투어 논문 수치가 재현되지 않습니다. 이식 전에 배포 GPU 수를 확정하고, 단일 GPU 라면 slow 채널 갱신 주기를 얼마까지 늘려야 fast 루프가 tick 을 지키는지 먼저 측정해야 합니다.
9. **System0(P3) 과의 역할 중복 판정.** System1 이 25 Hz 로 힘에 반응하면 System0 의 정당화 근거가 좁아집니다. 판정 실험은 비쌉니다 — 대신 먼저 값싸게 물어야 할 것은 **"우리 과제에서 슬립 이벤트의 시간 척도가 40 ms 보다 짧은가"** 입니다. 기존 텔레옵 데모의 지문 힘 로그에서 슬립 발생 구간의 힘 변화 rise time 을 측정하면 답이 나오고, 이것이 System0 존치 여부의 1차 근거가 됩니다.
10. **시뮬 검증 경로의 근접성 — 오히려 기회.** 논문의 시뮬 과제(Leap Cube Reorientation, 16-DoF, 50 Hz, MuJoCo Playground)는 우리 Phase 1 검증 과제(in-hand cube rotation)와 사실상 같은 문제입니다. 다만 우리 시뮬 스택은 Isaac Lab(PhysX)이라 접촉 모델이 다릅니다. 가장 싼 재현 경로는 우리 Isaac Lab in-hand rotation 환경에서 **계단 스케줄만** (비동기 채널 없이) 얹어 $`h`$ 스윕을 재현하는 것이며, 여기서 논문의 "1 NFE 로 $`h{=}1`$ 성능 매칭" 이 재현되지 않으면 이후 실기 이식은 중단해야 합니다.

---

## 💡 컨텍스트 제안

- **`D5`(P1) 를 `OPEN` 으로 승격 제안** — 현재 v1 은 `(ii) modality-separated + (α) shared rate` 입니다. 본 논문은 VLA 규모에서 rate 분리가 구현 가능하고 20–30 %p 가치가 있음을 보인 첫 직접 증거이므로, `(α) shared rate` 를 확정 선택지로 두기 어렵습니다. `#### [D5] Input-modality + control-rate separation (P1) — **OPEN**` 으로 바꾸고 bullet 을 `(working, not settled)` 로 표시하는 것을 제안드립니다. 결정 자체를 v2 로 넘기는 것은 위 ⚠️ 1–3 번 측정 이후가 적절합니다.
- **P1 §5 Tracked Literature 에 지연/반응성 계열 추가 제안** — 현재 P1 핀 4편(π0 · Dexora · LaMP · DexGrasp-VLA)에는 지연 축 논문이 없습니다. 본 논문($`\pi\mathbf{R}^{2}`$, [arXiv:2607.26055](https://arxiv.org/abs/2607.26055))을 D5 앵커로 핀하거나, 최소한 **Methodology base (non-pinned)** 에 본 논문 + Train-Time RTC([arXiv:2512.05964](https://arxiv.org/abs/2512.05964)) + RTC([arXiv:2506.07339](https://arxiv.org/abs/2506.07339)) 3편을 "지연 하 chunk 실행" 계보로 묶어 추가하는 것을 제안드립니다. 뒤 두 편은 이미 본 저장소에 분석 문서가 있으나 어느 pillar 에도 핀되어 있지 않습니다.
- **`D13`(P3) 서술의 정당화 근거 이동 제안** — System0 의 존재 이유를 "System1 이 느리다"에서 "슬립 억제는 System1 의 제어 tick 으로도 늦다"로 좁히는 방향의 문구 조정을 제안드립니다. 결정 자체(v1 선택지)는 바꾸지 않되, 근거가 이 논문으로 반박되는 부분을 남겨두면 이후 스카우팅이 잘못된 축으로 논문을 모읍니다.
- **`D26`(P0) 범위에 반응성 스트레스 평가 추가 제안** — 벤치마크 스카우팅 범위에 낙하 물체 포착 · 접촉 후 힘 조절 같은 동적 반응 과제를 명시적으로 넣는 것을 제안드립니다. 현재 in-hand rotation / articulated-tool 중심 범위로는 본 논문류의 기여가 우리 평가에 잡히지 않습니다.
- **`D11`(P2) 에 대조군 기록 제안** — "per-finger 토큰화 없이 flat concat + 고빈도 갱신만으로 힘 변조를 얻은 사례"로 본 논문을 D11 의 반증 후보 참조로 기록해 두시길 제안드립니다. Decision 을 바꾸자는 것이 아니라, D11 의 비용을 정당화할 때 비교되어야 할 baseline 이 생겼다는 뜻입니다.
