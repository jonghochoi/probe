# Paper Analysis — vla-eval: A Unified Evaluation Harness for Vision-Language-Action Models

---

## 📄 논문 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | vla-eval: A Unified Evaluation Harness for Vision-Language-Action Models |
| 저자 | Suhwan Choi¹, Yunsung Lee¹, Yubeen Park¹, Chris Dongjoo Kim², Ranjay Krishna², Dieter Fox², Youngjae Yu³ (소속 위첨자 1/2/3 — arXiv HTML 본문에서 기관명은 별도 추출되지 않음. 공개 코드/리더보드 호스트는 `allenai`) |
| 링크 | [arXiv:2603.13966](https://arxiv.org/abs/2603.13966) · [GitHub](https://github.com/allenai/vla-evaluation-harness) · [Website](https://allenai.github.io/vla-evaluation-harness/leaderboard/) |
| 발행일 / 버전 | 2026-03-14 제출 · 2026-04-17 개정 (v2) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| 분석 생성일 | 2026-06-04 |
| 관련 Pillar | P1 |
| 태그 | sim2real, dataset |
| 카탈로그 | benchmark/harness/vla-eval |

<!-- 본문은 arXiv HTML(전문)로 확보. 모든 수치는 본문/표에서 받은 그대로 인용. -->

---

## 🧭 한 줄 요약 (TL;DR)

VLA 모델 평가에서 벤치마크마다 반복되는 의존성·전처리·프로토콜 통합 비용을 없애는 오픈소스 평가 하니스로, 모델 추론과 벤치마크 실행을 WebSocket+msgpack 프로토콜과 Docker 격리로 분리해 통합 비용을 `O(N×M)`에서 `O(N+M)`로 떨어뜨립니다. 14개 시뮬레이션 벤치마크·6개 모델을 지원하고 에피소드 샤딩 병렬화로 최대 47배 wall-clock 가속을 달성합니다. 단일 미문서화 파라미터 하나가 성공률을 최대 55pp까지 흔든다는 재현 함정도 문서화합니다.

---

## ❓ 문제 정의 / 동기

- **풀고자 하는 문제** — VLA 모델은 점점 더 여러 시뮬레이션 벤치마크에서 평가되지만 벤치마크 하나를 평가 파이프라인에 추가할 때마다 상충하는 의존성 해소, 불완전하게 명세된 평가 프로토콜 맞추기, 문서화되지 않은 전처리의 역공학이 모두 필요합니다.
- **기존 접근의 한계** — 이 비용은 선형으로 누적됩니다. `M`개 벤치마크 × `N`개 모델 평가는 통합 작업을 `O(N×M)`번 반복하게 만들어, 소규모 팀에게 포괄적 다중 벤치마크 평가를 사실상 불가능하게 합니다.
- **숨은 함정** — 시드·에피소드 수·전처리가 논문에서 누락되는 일이 잦고 문서화되지 않은 파라미터 하나가 성공률을 최대 55pp까지 뒤바꿀 수 있습니다. 올바른 통합은 환경 셋업뿐 아니라 레퍼런스 구현과의 고통스러운 대조를 요구합니다.
- **본 논문의 가설** — 언어모델용 `lm-evaluation-harness`처럼 모델 추론과 벤치마크 실행을 분리하면, 모델은 한 번, 벤치마크는 한 번만 통합해도 전체 교차평가 행렬이 자동으로 작동해 통합 비용이 `O(N+M)`로 떨어진다.
- **왜 지금 중요한가** — 전체 리더보드 분석 결과 모델의 81%가 단일 벤치마크에서만 평가되고 3개 이상에서 평가된 모델은 6%에 그쳐, 교차 벤치마크 비교 자체가 희소합니다. 일반 능력 평가를 위해 통합 프레임워크가 필요한 상태입니다.

---

## 🧩 핵심 기여

- **통합 평가 하니스** — Docker 기반 격리 + WebSocket+msgpack 프로토콜로 14개 벤치마크와 6개 모델 서버를 지원하는 오픈소스 평가 프레임워크.
- **재현 검증 + 함정 문서화** — 6개 VLA 코드베이스 × 3개 벤치마크에서 published score를 재현하고 단일 미문서화 파라미터가 성공률을 최대 55pp 흔드는 함정들을 명시적으로 기록.
- **모델 비종속 병렬 평가 방법론** — 에피소드 샤딩 + 배치 추론으로 최대 47배 가속. 병목이 모델 추론이 아니라 환경 step rate라는 점을 demand/supply 분석으로 규명.
- **VLA 리더보드** — 정규 프로토콜 정의(canonical protocol definitions)와 함께 17개 벤치마크에 걸친 657개 published result를 집계.

---

## 🔑 기술 키워드

- **Evaluation harness** — 모델과 벤치마크를 각각 한 번만 끼워 맞추면 전체 조합 평가가 돌아가게 하는 "어댑터 허브". 언어모델의 `lm-evaluation-harness`를 VLA로 옮긴 발상.
- **WebSocket+msgpack protocol** — 모델 서버와 벤치마크 컨테이너 사이를 잇는 통신 규약. observation을 보내고 action을 받는 메시지를 바이너리 직렬화(msgpack)로 주고받아 추론과 실행을 물리적으로 분리.
- **Docker-based isolation** — 벤치마크마다 충돌하는 파이썬 런타임·시뮬레이터를 각자의 컨테이너에 가둬 한 머신에서 공존시키는 격리 방식.
- **predict() interface** — 모델 통합의 단일 접점. 모델 측은 `predict(obs, ctx)` 한 메서드(보통 약 50줄)만 구현하면 되고 action chunking·배치 추론은 베이스 클래스가 처리.
- **Four-method benchmark interface** — 벤치마크 통합의 단일 접점. `reset`·`step`·`make_obs`·`get_step_result` 네 메서드만 구현하면 됨.
- **Episode sharding** — 동일 벤치마크를 여러 Docker 컨테이너로 쪼개 에피소드를 분산 실행하는 환경 병렬화. 단일 환경 인스턴스가 시뮬레이션 병목인 문제를 해소.
- **Demand/supply methodology** — 환경 처리량 $`\lambda(K)`$(샤드 수 함수)와 모델 처리량 $`\mu(B)`$(배치 크기 함수)를 측정해 둘이 맞물리는 운영점을 잡는 병렬도 튜닝 방법.
- **Canonical protocol definition** — 같은 벤치마크라도 논문마다 다른 task 부분집합·메트릭·split을 비교 가능하도록 통일한 기준 프로토콜 정의.
- **pp (percentage point)** — 성공률 차이를 절대값으로 표현하는 단위. 97.8%→42%는 "55pp" 하락.

---

## 🔬 방법론

### 직관

핵심 통찰: 평가 비용 폭발의 원인은 "모델 × 벤치마크" 곱셈 구조다. 모델 `N`개를 벤치마크 `M`개에서 돌리려면 각 조합마다 의존성·전처리·프로토콜을 맞춰야 하므로 `O(N×M)`의 통합 부담이 생깁니다. 언어모델 진영의 `lm-evaluation-harness`가 보여준 해법은 모델 추론과 벤치마크 실행의 디커플링입니다. 둘 사이에 표준 통신 계약을 두면 모델은 한 번(추론 서버), 벤치마크는 한 번(컨테이너)만 끼워 맞추면 되고 교차평가 행렬은 자동으로 채워집니다.

> "Models integrate once, benchmarks integrate once, and the full $`N\times M`$ cross-evaluation matrix works automatically, reducing integration effort from $`O(N\times M)`$ to $`O(N+M)`$." (§I)
> (한글 해설 — 디커플링이 만들어내는 비용 구조 변화를 한 문장에 못 박은 설계 의도입니다. 곱셈을 덧셈으로 바꾸는 것이 프레임워크의 존재 이유입니다.)

두 번째 통찰: 병렬화의 진짜 병목은 모델 추론이 아니라 환경 시뮬레이션이다. 모델 추론은 배치로 쉽게 확장되지만 기존 벤치마크는 단일 환경 인스턴스로 돌기 때문에 시뮬레이션이 지배적 병목이 됩니다. 가속은 환경 병렬화가 결정하며 어떤 모델에도 동일하게 전이됩니다.

### 아키텍처

전체 구조는 WebSocket + msgpack 바이너리 직렬화를 쓰는 client-server 구조이며 모델 추론을 벤치마크 실행에서 분리합니다.

- **메시지 규약** — 각 메시지는 타입(`observation`, `action`, `episode_start/end`), 벤치마크별 payload, 시퀀스 번호, 타임스탬프를 담습니다.
- **모델 서버** — `PredictModelServer`를 상속하며 블로킹 `predict(obs, ctx)` 메서드(보통 약 50줄), 자동 action chunking, `max_batch_size`를 통한 선택적 배치 추론을 제공합니다. OpenVLA 통합 전체가 Listing 1 한 장(약 30줄)으로 표현됩니다.
- **의존성 격리** — 각 모델 서버는 PEP 723 inline 메타데이터로 의존성을 선언하고 `vla-eval serve`가 `uv run`으로 실행해 격리 환경을 자동 생성합니다. 충돌하는 의존성(예: CogACT의 `transformers==4.40.1` vs. X-VLA의 `transformers>=4.44`)이 간섭 없이 공존합니다.
- **벤치마크** — 통합자는 핀 고정된 의존성을 가진 전용 Docker 이미지 안에서 네 메서드(`reset`, `step`, `make_obs`, `get_step_result`)를 구현합니다.
- **선언적 config** — 벤치마크 + 모델 서버 두 개의 YAML config가 각 평가를 구동합니다. 모든 Docker 이미지는 버전 태그와 함께 `ghcr.io`에 게시되고 필요한 에셋(scene 파일, 텍스처, robot description)을 번들로 묶어, 평가 전체가 `vla-eval serve`와 `vla-eval run` 두 명령으로 끝납니다. 모든 실행은 하니스 버전·벤치마크 구성·에피소드별 메트릭을 기록한 구조화 JSON 결과 파일을 산출해 정확한 재현을 가능케 합니다.

지원 범위는 14개 벤치마크(action space 6D~14D, Docker 이미지 4.7~35.6GB)와 6개 모델 서버(CogACT, OpenVLA, OpenVLA-OFT, $`\pi_{0}`$ / $`\pi_{0}`$-FAST, GR00T N1, X-VLA)입니다.

### 학습 목표 / 손실

해당 없음 — 본 논문은 학습 알고리즘이 아니라 평가 인프라 논문입니다. 손실 함수·학습 목표가 존재하지 않으며 대신 병렬도 운영점을 정하는 demand/supply 모델이 핵심 수식 역할을 합니다.

병렬화는 두 축으로 나뉩니다. 환경 병렬성은 $`K`$ 개 Docker 컨테이너에 걸친 에피소드 샤딩, 추론 병렬성은 배치 forward pass입니다. 환경 처리량 $`\lambda(K)`$(샤드 수 함수)와 모델 처리량 $`\mu(B)`$(배치 크기 함수)를 측정하고 운영점은 환경 수요가 모델 공급 천장 아래에 놓이도록 잡습니다.

> "Episode sharding closes this gap (Fig. 1): the model supply ceiling exceeds environment demand at all shard counts, so the speedup is determined by environment parallelism and transfers to any model." (§II-C)
> (한글 해설 — 모델 공급 천장이 모든 샤드 수에서 환경 수요를 초과하므로 가속이 환경 병렬화에만 좌우되고, 따라서 어떤 모델에도 그대로 전이된다는 모델 비종속성의 근거입니다.)

![Figure 1 — demand/supply 처리량 곡선](https://arxiv.org/html/2603.13966/x1.png)

> "Figure 1: Demand/supply throughput for LIBERO + CogACT [14] on H100. Dashed lines show supply ceilings $`\mu(B)`$ at each batch size. The operating point $`K^{*}\!=\!50`$ uses 78% of the supply capacity at $`B\!=\!16`$, leaving headroom to absorb burst arrivals and prevent queue buildup; beyond $`K\!=\!80`$, environment overhead causes throughput to drop." (§II-C)
> (한글 해설 — 운영점 $`K^{*}=50`$ 이 $`B=16`$ 공급 용량의 78%만 쓰며 버스트 흡수 여유를 남긴다는, 병렬도 튜닝의 핵심 그림입니다. $`K=80`$ 을 넘으면 환경 오버헤드로 처리량이 오히려 떨어집니다.)

### 학습 셋업

학습이 없으므로 실행 셋업(벤치마크 호스트와 분리된 H100 모델 서버)만 기재합니다. LIBERO + CogACT-7B 측정 조건은 §📊에 정리합니다. 리더보드 큐레이션 단계는 AI 에이전트(Claude Code with Opus 4.6)가 MCP 도구(arXiv, Semantic Scholar, PDF reader)로 1,704편을 검토해 정규 프로토콜에 맞춰 결과를 추출·정규화하고 이후 사람 운영자가 모든 엔트리를 검토해 이상치와 모호 사례를 해소하는 방식입니다.

---

## 📊 실험 설정과 결과

검증은 학습이 아니라 재현 충실도와 병렬화 가속, 두 갈래로 나뉩니다.

**재현 행렬** — 6개 published VLA 코드베이스(OpenVLA, $`\pi_{0.5}`$, OpenVLA-OFT, GR00T N1.6, DB-CogACT, X-VLA)를 3개 벤치마크에서 고정 시드와 `ghcr.io`의 버전 고정 Docker 이미지로 평가했습니다. 평가 단위는 LIBERO 4 suites × 10 tasks × 50 episodes(총 2,000), CALVIN ABC→D 1,000 chained sequences, SimplerEnv 4 WidowX tasks × 24 episodes입니다.

| Codebase | LIBERO (%) | CALVIN (len) | SimplerEnv (%) |
|---|---|---|---|
| OpenVLA | 76.2 (−0.3) | — | — |
| $`\pi_{0.5}`$ | 97.7 (+0.8) | — | — |
| OpenVLA-OFT | 96.7 (−0.4) | — | — |
| GR00T N1.6 | 94.9 (−2.1) † | — | 59.7 (−8.0) ‡ |
| DB-CogACT | 94.7 (−0.2) | 4.02 (−0.04) | 63.5 (−6.0) |
| X-VLA | 97.4 (−0.7) | 4.30 (−0.13) | 94.8 (−1.0) |

(— = 공개 checkpoint 없음. † community checkpoint. ‡ Google Robot visual matching, 나머지는 WidowX. 괄호 안은 reported 대비 Δ.)

> "Published scores largely reproduce across six codebases and three benchmarks, validating the framework's fidelity to reference implementations." (§III-A)
> (한글 해설 — 대부분의 Δ가 1pp 안팎으로, 하니스가 레퍼런스 구현에 충실함을 보였습니다. GR00T·CogACT의 SimplerEnv 6~8pp 갭은 잔존 미해결 항목입니다.)

**재현 함정** — 단일 미문서화 설정이 치명적 점수 변화를 일으킵니다.

> "Using the wrong proprioceptive state source in X-VLA [23] on LIBERO drops success rate from 97.8% to 42%, a 55 percentage point (pp) swing from one parameter." (§III-B)
> (한글 해설 — proprioceptive state의 출처 하나만 잘못 잡아도 성공률이 55pp 무너집니다. 평가 재현성의 취약함을 보여주는 대표 사례입니다.)

| 함정 | 모델 | 영향 |
|---|---|---|
| 잘못된 proprioceptive state source | X-VLA | LIBERO 97.8% → 42% (−55pp) |
| absolute vs. delta action mode 혼동 | (7D 공통) | position 누적으로 robot 발산 → 0% |
| quaternion antipodal normalization 불일치 | OpenVLA-OFT | LIBERO-Goal 97%→83%, LIBERO-Long 95%→56% |
| 미문서화 center crop (scale=0.9) 누락 | OpenVLA | 약 3pp 손실 |
| end-effector pose proprio 입력 부재 | GR00T | SimplerEnv 30–55% → 0% |

> "OpenVLA-OFT [12] uses a quaternion-to-axis-angle conversion without antipodal normalization (angle $`\in[0,2\pi]`$, matching robosuite convention), while our initial implementation flipped $`w<0`$ quaternions (angle $`\in[0,\pi]`$); this single mismatch dropped LIBERO-Goal from 97% to 83% and LIBERO-Long from 95% to 56%." (§III-B)
> (한글 해설 — quaternion → axis-angle 변환에서 antipodal normalization 유무 하나로 LIBERO-Long이 95%→56%로 무너집니다. action representation의 미세 규약이 결과를 지배함을 보여줍니다.)

**병렬화 가속** — LIBERO + CogACT-7B(H100 모델 서버, 분리된 벤치마크 호스트) 측정입니다.

> "Combined, 2,000 episodes complete in $`{\sim}`$18 minutes versus $`{\sim}`$14 hours sequentially, a 47$`\times`$ wall-clock speedup." (§II-C)
> (한글 해설 — 환경 샤딩 $`K`$:1→50으로 $`\lambda`$ 11.2→364.6 obs/s(32.6배), 배치 $`B`$:1→16으로 $`\mu`$ 165.2→468.2 obs/s(2.8배). 결합 시 14시간 → 18분, 47배.)

| 벤치마크 | 단위 | 샤드 / 배치 | 시간 | 가속 |
|---|---|---|---|---|
| LIBERO | 2,000 episodes | 50 shards / B=16 | 약 18분 (vs ~14시간) | 47× |
| CALVIN | 1,000 sequences | 16 shards | 약 33분 | 16× |
| SimplerEnv | 288 episodes (3 seeds) | 16 shards | 약 8.5분 | 12× |

![Figure 2 — sequential vs. batch parallel wall-clock](https://arxiv.org/html/2603.13966/x2.png)

> "Figure 2: Wall-clock evaluation time: sequential vs. batch parallel. LIBERO: 2,000 episodes, 50 shards, $`B\!=\!16`$. CALVIN: 1,000 sequences, 16 shards. SimplerEnv: 288 episodes (3 seeds), 16 shards." (§II-C)
> (한글 해설 — 세 벤치마크 모두 순차 대비 두 자릿수 배 가속을 보이며, 병목이 환경 step rate라는 본문 주장을 시각화합니다.)

**리더보드 / 교차 벤치마크** — 17개 벤치마크·509+ 구성에 걸친 657개 result를, 추적 벤치마크 중 하나 이상을 인용한 1,704편에서 집계했습니다.

> "81% of the 509+ models are evaluated on only one benchmark; only 3 (0.6%) on 5 or more." (§IV-B, Figure 4)
> (한글 해설 — 모델의 81%가 단일 벤치마크에서만, 3개 이상에서 평가된 모델은 6%뿐이라, 교차 비교가 구조적으로 드물다는 사실이 수치로 드러납니다.)

---

## ⚖️ 한계

- **감사 범위 협소** — 저자가 명시한 한계로, 검증은 6개 코드베이스 × 3개 시뮬레이션 벤치마크에 그치며 추가 벤치마크와 real-robot transfer는 향후 과제입니다.
- **리더보드 미검증** — 리더보드 결과는 published 논문에서 추출한 것이며 독립적으로 재실행·검증되지 않았습니다.
- **메트릭 단일성** — 지원 메트릭이 task success rate에 한정됩니다. subtask progress, task efficiency, safety 같은 더 미세한 차원은 아직 지원하지 않습니다.
- **(명백한 갭) sim-only** — 14개 벤치마크가 모두 시뮬레이션입니다. 실로봇 접촉·dexterity 평가나 contact-precision 지표는 프레임워크 범위 밖이며 우리 식별성(P5)이 요구하는 평가 축과 직접 겹치지 않습니다.
- **(명백한 갭) checkpoint 의존** — 대부분 VLA가 벤치마크별 fine-tuning을 요구해, 공개 checkpoint가 있는 곳에서만 평가가 가능합니다(재현 행렬의 `—` 셀들).

---

## ♻️ 재현성

- **코드 / 프레임워크** — 오픈소스로 공개: `https://github.com/allenai/vla-evaluation-harness`. Docker 이미지는 버전 태그와 함께 `ghcr.io`에 게시, 에셋 번들 포함.
- **평가 config / 재현 결과** — evaluation config와 모든 reproduction 결과가 공개. 모든 실행이 하니스 버전·벤치마크 구성·에피소드별 메트릭을 담은 구조화 JSON을 남겨 단일 config 파일에서 정확 재현 가능.
- **리더보드** — `https://allenai.github.io/vla-evaluation-harness/leaderboard` 공개.
- **하드웨어** — 가속 측정은 H100 모델 서버 + 분리된 벤치마크 호스트. 실로봇 하드웨어는 사용하지 않음(전부 시뮬레이션).

---

## 🎯 관련 Pillar / Decision (P# / D#)

본 논문은 **P5(Task Definition & Falsifiable Evaluation)**에 가장 먼저 닿습니다.

- **D26(평가 프로토콜)** — 연결이 가장 직접적입니다. D26 v1은 "AutoEval-style automation(arXiv:2503.24278)으로 sim ablation 자동화 + Grouped Blind Ensemble"을 명시하는데 vla-eval은 정확히 그 sim-ablation 자동화 인프라의 한 후보입니다. 단일 config에서 재현 가능한 구조화 JSON 산출, 정규 프로토콜 정의, ghcr.io 버전 고정 이미지는 우리의 sim ablation 30 trials/condition(D24)을 재현 가능하게 운영하는 도구로 곧장 들어맞습니다.
- **D25(4-기여 ablation & falsifier)** — 부분 지지이자 경고. vla-eval은 ablation 조건을 자동으로 돌리는 인프라지만 지원 메트릭이 **task success rate 단일**입니다. 우리의 falsifier는 slip count·pose stability 같은 **contact-precision 메트릭**과 coordination corr($`a_b`$,$`a_h`$)을 요구하므로, vla-eval를 그대로 쓰면 falsifier 메트릭을 측정할 수 없습니다.
- **D24(데모 task & phasing)** — 우리 in-hand rotation/tool-articulation 데모는 vla-eval가 지원하는 14개 벤치마크 어디에도 없습니다(전부 일반 manipulation). four-method 벤치마크 인터페이스로 우리 sim 환경을 *통합자*로서 끼워 넣는 식의 활용만 가능합니다.

**P1(D2/D5)로의 부차적 연결** — §III-B 재현 함정에서 우리 아키텍처 결정의 직접 증거를 확인할 수 있습니다. "absolute vs. delta action mode 혼동 → 0%"와 "잘못된 proprioceptive state source → −55pp"는 D2(Body output space — Cartesian flange pose, absolute vs. delta)와 D5/D15(proprio 채널·출처)의 명세가 결과를 지배한다는 점을 외부에서 확인해주는 강력한 증거입니다. 이 P1 연결을 메타 행에 기록합니다.

**Identity 긴장** — 우리 식별성의 평가 축은 *실로봇 + contact-precision + 4-기여 isolation*입니다. vla-eval은 *sim-only + success-rate-only*라, 도구로는 유용하나 우리 falsifier 철학을 대체하지 못합니다(지지보다 보완 관계).

**§10 경쟁자 함의** — 직접 경쟁자는 없습니다. 저자에 Dieter Fox(NVIDIA/UW)·Ranjay Krishna(UW/AI2)가 포함되어 §9.1 P5 watch 대상과 겹칩니다. (흥미로운 메타 관찰: 리더보드 큐레이션을 Claude Code Opus 4.6로 수행 — PROBE 자신의 파이프라인과 같은 도구 계열.)

---

## ✨ 핀 논문 대비 델타

- **AutoEval([arXiv:2503.24278], P5 핀)** 대비 — AutoEval은 평가 *자동화*(스코어링 자동화) 자체에 초점을 둡니다. vla-eval의 진정한 새로움은 **모델×벤치마크 통합 비용을 `O(N×M)`→`O(N+M)`로 떨어뜨리는 디커플링 아키텍처**와, 단일 미문서화 파라미터가 55pp를 흔든다는 **재현 함정의 체계적 카탈로그화**입니다. AutoEval이 "자동 채점"이라면 vla-eval은 "교차평가 행렬의 인프라화 + 재현성 감사"입니다.
- **NVIDIA Robot Policy Evaluation([arXiv:2508.11117], P5 핀)** 대비 — 후자는 sim2real 벤치마킹과 Isaac 스택에 묶입니다. vla-eval은 **시뮬레이터-비종속**(SAPIEN·PyBullet·robosuite 등 14개를 Docker로 동등 격리)이고 모델-비종속 가속(47×)을 제공한다는 점이 다릅니다.
- **RoboEval([arXiv:2507.00435], P5 핀)** 대비 — RoboEval은 behavioral 메트릭(D25 falsifier 후보)을 제공합니다. vla-eval은 정반대로 메트릭을 success-rate로 좁히는 대신 **벤치마크 커버리지·재현성·throughput**을 첫째 시민으로 둡니다. 둘은 상보적입니다(메트릭 깊이 vs. 통합 폭).
- **요약 델타** — "평가 메트릭을 풍부하게"가 아니라 "평가 실행 자체를 싸고 재현 가능하게" 만든 인프라 논문. 핀들과 경쟁이 아니라 직교합니다.

---

## ⚙️ 의사결정 함의

- **D26 도구 후보 추가** — sim ablation(D24의 30 trials/condition) 운영 도구로 vla-eval의 **four-method 벤치마크 인터페이스**(`reset`/`step`/`make_obs`/`get_step_result`)에 우리 in-hand rotation sim 환경을 *통합자*로 끼워 넣는 경로를 검토. 산출물의 **구조화 JSON(하니스 버전 + per-episode 메트릭)** 포맷을 우리 ablation 로그 스키마의 레퍼런스로 채택하면 재현성이 곧장 올라갑니다.
- **action-space config 명세 강제** — 재현 함정이 가리키는 구체적 config 키: `action_mode`(absolute vs. delta)와 proprioceptive `state_source`를 **명시적·버전 고정** 항목으로 우리 학습/평가 config에 못 박는 것이 1순위입니다(둘 다 7D로 데이터만으로는 구분 불가 → 0% 또는 −55pp 위험). D2(Cartesian flange pose) 채택 시 absolute/delta 규약을 config에 못 박는 것이 1순위.
- **quaternion 규약 고정** — OpenVLA-OFT 사례(antipodal normalization 유무로 95%→56%)를 따라, 우리 Body 출력의 rotation 표현(quaternion → axis-angle)에서 `angle ∈ [0,2π]` vs `[0,π]` 규약을 robosuite/시뮬레이터 컨벤션에 맞춰 단일 고정.
- **평가 병렬도 운영점** — GPU 예산이 잡히면(§13.B compute 항목) demand/supply 방법론($`\lambda(K)`$ vs $`\mu(B)`$)으로 우리 ablation 평가의 샤드 수 $`K`$ 를 튜닝. CogACT 사례의 $`K^{*}=50`$(공급 78%)이 출발 휴리스틱.
- **단 메트릭 갭은 자력 보완** — vla-eval은 success-rate만 주므로, slip count·pose stability·coordination corr는 우리가 벤치마크 측 `get_step_result`에서 직접 산출해야 합니다(프레임워크가 대신 주지 않음).

---

## ⚠️ 먼저 검증할 실패 모드

- **(가장 싼 체크) 우리 데모가 지원 벤치마크에 없음** — 14개 벤치마크 어디에도 in-hand cube rotation·tool articulation이 없습니다. vla-eval를 "기성 벤치마크 러너"로 기대하면 즉시 어긋납니다. 5분 체크: 지원 벤치마크 목록(LIBERO/CALVIN/SimplerEnv/RoboTwin 등)에 우리 task family가 있는지 확인 → 없음 확정 → "통합자로서만 활용" 전제로 재설계.
- **메트릭 미스매치** — success-rate-only라 우리 falsifier(contact-precision)를 그대로 못 잽니다. four-method 인터페이스가 임의 per-step 메트릭(slip/pose) 산출을 허용하는지 코드로 확인 전에는 D26 도구 채택을 확정하지 말 것.
- **Isaac Lab/Sim 호환성** — 우리 System0 학습 스택은 Isaac Sim + Isaac Lab(§4.2)입니다. vla-eval의 Docker 격리·시뮬레이터 셋이 Isaac 계열을 1급으로 다루는지 불명(본문 벤치마크는 robosuite/SAPIEN/PyBullet 계열). Isaac 환경을 컨테이너에 넣는 통합 비용이 우리 쪽 부담.
- **sim-only + checkpoint 의존** — 실로봇 평가(우리 식별성의 핵심)는 프레임워크 범위 밖. fine-tuned checkpoint가 있어야 평가 가능하므로, ablation 중간 체크포인트를 매번 통합하는 운영 부담이 잠재.

---

## 💡 컨텍스트 제안

- **P5 핀 후보** — vla-eval를 §8.5 P5 Tracked Literature의 **AutoEval 보완 핀** 또는 D26 도구 레퍼런스로 추가 검토 제안(현 핀 8개 한도 내 교체 여부는 사람 판단). 역할: "sim ablation 통합·재현·throughput 인프라 (success-rate-only)". 단, contact-precision 메트릭 부재로 falsifier 도구로는 부분적임을 명시.
- **D26 노트 보강 제안** — D26 v1의 "AutoEval-style automation" 옆에 "vla-eval(four-method 통합 + 구조화 JSON 재현 로그) = sim ablation 실행 인프라 후보" 한 줄 추가 검토.
- **§13.B 연결** — vla-eval 가속 방법론은 §13.B "compute budget" 미해결 항목의 평가-측 비용 추정에 직접 입력(예: $`K^{*}`$ ·배치로 ablation wall-clock 산정).
- context/MASTER.md 는 수정하지 않았습니다 — 위는 모두 제안입니다.

> 💡 base 매핑은 `/implement-design analysis/2603.13966/design.md [--foundry <name>]` 로 생성하실 수 있습니다. 기본 foundry 는 `lerobot` 입니다.
