# 로보틱스 PEFT 랜드마크 — 조사 + 평가

> 자매 문서 `vlm-prior-preservation.md` 가 P4 의 *보존 전략* 을 다룬다면, 이
> 문서는 한 발 더 넓게 **로보틱스 분야에 PEFT(parameter-efficient
> fine-tuning)를 적용한 랜드마크** 를 모아 *분석(deep-dive) 우선순위* 를
> 매깁니다.
> 한 줄 프레임: 로보틱스가 *task별 from-scratch 학습* → *대규모
> cross-embodiment VLA 사전학습 후 적응* 으로 옮겨가며 **적응 단계 비용이 새
> 병목** 이 됐고, PEFT 가 그 병목을 겨눕니다.
> 평가의 주 축은 4축 합계가 아니라 **분석 권고** 컬럼입니다. arXiv ID 는 모두
> resolve 검증을 마쳤습니다(§8).

---

## 1. 범위와 평가 축

### 1-1. 무엇을 "로보틱스 PEFT 랜드마크" 로 보는가

PEFT 는 큰 사전학습 모델의 가중치 대부분을 동결하고 *작은 추가 파라미터*
(LoRA·adapter·prefix 등)만 학습하는 적응 기법군입니다. 이 문서는 그중에서도
**로봇 정책 학습(VLA·모방 학습·RL)에 PEFT 를 적용했거나**, 그 적용의 *토대·
한계* 를 규정하는 방법론·분석 논문을 랜드마크로 모읍니다. `context/P4.md` 의
스코프(VLM freeze + LoRA/Adapter)보다 넓지만, 평가 시 P4 결정(D19 FT 범위 /
D20 보존 / D21 staged recipe)과의 접점을 항상 함께 기재합니다.

`vlm-prior-preservation.md` 의 forgetting 분류와의 매핑:
- **갈래 A 격리** (freeze + action-side adapter) — VLA-Adapter·TAIL adapter 갈래.
- **갈래 B① 부분공간 PEFT** (LoRA/DoRA/AdaLoRA) — 본 문서 클러스터 2 의 정본군.

### 1-2. 평가 축 (rubric)

각 후보를 4축(0–3)으로 보되, 최종 산출은 이를 P4 관련성과 합쳐 도출한 **분석
권고** 입니다.

- **Relevance** — P4 결정(D19~D23) 또는 로보틱스 적응 병목과의 직결도.
- **Novelty** — 핀/기수록 대비 델타.
- **Reproducibility** — 코드·가중치·하드웨어 공개 수준.
- **Sim2Real** — 실제 로봇 검증 유무.

**분석 권고** 4단계: `강력` (deep-dive 미존재 + 결정 직결 + 랜드마크) ·
`권고` · `중간` · `낮음` (방법론 일반론/신규성 낮음). 이미 deep-dive 가 있거나
P4 리포트에 다룬 항목은 상태 컬럼에 명시합니다.

### 1-3. 세 클러스터

1. **로보틱스/VLA 에 PEFT 적용** — 실제 로봇 정책에 LoRA/adapter 를 붙인 사례.
2. **기초 PEFT 방법론** — LoRA 계열의 정본(로봇 비특화, 도구의 출처).
3. **LoRA 효용·한계 분석** — "LoRA 가 full-FT 를 언제 따라잡고 언제 망가지나".

---

## 2. 랜드마크 스캔 표

> 상태 약어 — `P4핀`: `context/P4.md` 핀 또는 2026-05-28 P4 스카우트 리포트
> 기수록 · `NEW`: 본 조사로 추가 · `분석없음`: `analysis/<id>/` deep-dive 부재.
> 분석 권고 컬럼이 본 표의 핵심 산출입니다.

| # | 논문 | arXiv | 클러스터 | PEFT 기법 | 로보틱스 적용 | P4 접점 | 상태 | 분석 권고 |
|---|---|---|---|---|---|---|---|---|
| 1 | TAIL | [arXiv:2310.05905](https://arxiv.org/abs/2310.05905) | 1 | adapter·LoRA·prefix 비교 | 모방 학습(continual IL) | D19(d)·D21 | NEW·분석없음 | 권고 |
| 2 | VLA-Adapter | [arXiv:2509.09372](https://arxiv.org/abs/2509.09372) | 1 | Bridge Attention adapter | VLA(LIBERO·CALVIN) | D20·D19b | P4핀·분석없음 | 강력 |
| 3 | VLM2VLA | [arXiv:2509.22195](https://arxiv.org/abs/2509.22195) | 1 | LoRA-only + NL action | VLA(BridgeData V2) | D19(d)·D20·D23(ii) | P4핀·분석없음 | 권고 |
| 4 | OpenVLA | [arXiv:2406.09246](https://arxiv.org/abs/2406.09246) | 1 | LoRA fine-tuning | VLA(OXE) | D19(d) | P4핀·분석없음 | 중간 |
| 5 | OpenVLA-OFT | [arXiv:2502.19645](https://arxiv.org/abs/2502.19645) | 1 | FT 레시피(병렬 디코딩·chunk) | VLA(LIBERO·ALOHA) | D23·D19 | NEW·분석없음 | 중간 |
| 6 | Natural Continual Learners w/ RL | [arXiv:2603.11653](https://arxiv.org/abs/2603.11653) | 1 | sequential LoRA | VLA continual RL | D20·D21 | NEW·분석없음 | 권고 |
| 7 | Accessible Physical AI (LoRA VLA) | [arXiv:2512.11921](https://arxiv.org/abs/2512.11921) | 1 | LoRA + quantization | VLA(SO101) | D19(d) | NEW·분석없음 | 낮음 |
| 8 | LoRA | [arXiv:2106.09685](https://arxiv.org/abs/2106.09685) | 2 | 저차원 부분공간 | (로봇 비특화) | D19(d) 토대 | P4핀·분석없음 | 낮음 |
| 9 | QLoRA | [arXiv:2305.14314](https://arxiv.org/abs/2305.14314) | 2 | 4-bit 양자화 + LoRA | (로봇 비특화) | D19(d) 배포 | NEW·분석없음 | 낮음 |
| 10 | DoRA | [arXiv:2402.09353](https://arxiv.org/abs/2402.09353) | 2 | weight-decomposed LoRA | (로봇 비특화) | D19(d) rank 대안 | P4핀·분석없음 | 낮음 |
| 11 | AdaLoRA | [arXiv:2303.10512](https://arxiv.org/abs/2303.10512) | 2 | 적응적 rank 배분 | (로봇 비특화) | D19(d)·트렌드① | NEW·분석없음 | 중간 |
| 12 | Houlsby Adapter | [arXiv:1902.00751](https://arxiv.org/abs/1902.00751) | 2 | bottleneck adapter | (NLP) | D20 토대 | P4핀·분석없음 | 낮음 |
| 13 | VL-Adapter | [arXiv:2112.06825](https://arxiv.org/abs/2112.06825) | 2 | V&L adapter | (멀티모달) | D20 멀티모달 가교 | NEW·분석없음 | 낮음 |
| 14 | LoRA vs Full FT: Illusion of Equivalence | [arXiv:2410.21228](https://arxiv.org/abs/2410.21228) | 3 | LoRA 해석 분석 | (분석) | D19(d) 근거 | NEW·분석없음 | 중간 |
| 15 | LoRA Learns Less and Forgets Less | [arXiv:2405.09673](https://arxiv.org/abs/2405.09673) | 3 | LoRA vs FT 실증 | (분석) | D19(d)·D20 직결 | NEW·분석없음 | 권고 |

---

## 3. 클러스터 1 — 로보틱스/VLA 에 PEFT 적용

### TAIL — Task-specific Adapters for Imitation Learning ([arXiv:2310.05905](https://arxiv.org/abs/2310.05905))

대형 사전학습 모델을 제한된 데이터·연산으로 새 조작 태스크에 적응시키기 위해
**adapter·prefix(P-Tuning)·LoRA 를 한 틀에서 비교** 한 모방 학습 연구입니다.
세 PEFT 기법을 continual IL 맥락에서 나란히 놓고 forgetting 과 plasticity 를
함께 측정한 점이 로보틱스-PEFT 비교의 정본 격입니다.
- **P4 접점**: D19(d) LoRA/adapter 이동 시 *어느 PEFT 를 고를지* 의 직접
  비교 근거. D21 Stage 3(LoRA·adapter 제한적 FT)의 설계 레퍼런스.
- **분석 사유 (권고)**: 로보틱스에서 PEFT 기법 *간* 비교를 정면으로 다룬 드문
  랜드마크인데 deep-dive 가 없습니다. D21 Stage 3 기법 선택을 근거화합니다.

### VLA-Adapter ([arXiv:2509.09372](https://arxiv.org/abs/2509.09372))

Prismatic-VLM + Qwen2.5-0.5B 의 초소형 백본에 Bridge Attention 어댑터만 붙여
대규모 VLM·사전학습 의존도를 낮추고, 소비자급 GPU 에서 빠른 추론과 경쟁력 있는
성능을 보고합니다(갈래 A④).
- **P4 접점**: D20 action-side adapter 의 대표. "백본 규모를 키워도 이득이
  제한적" 이라는 보고는 D19b lineage 규모 우선론의 반례.
- **분석 사유 (강력)**: 2026-05-28 P4 리포트에서도 분석 강력 권고로 꼽힌 반례
  트랙. 본 문서에서도 동일 평가를 유지하며 cross-link 합니다.

### VLM2VLA — Actions as Language ([arXiv:2509.22195](https://arxiv.org/abs/2509.22195))

저수준 행동을 자연어로 정합해 사전학습 분포와의 불일치를 데이터 레벨에서 먼저
없앤 뒤(갈래 D), **LoRA 만으로** VLA 를 학습해 catastrophic forgetting 을
회피합니다. <cite>이 catastrophic forgetting 은 VLM 의 인터넷 규모 사전학습
corpus 와 로보틱스 fine-tuning 데이터 사이의 분포 불일치 때문이다.</cite>
(VLM2VLA, arXiv:2509.22195)
- **P4 접점**: D19(d) LoRA-only + D23(ii) NL-action 경로의 유일한 레퍼런스.
- **분석 사유 (권고)**: D19/D23 가 PEFT·NL-action 으로 이동할 때의 정본.

### OpenVLA ([arXiv:2406.09246](https://arxiv.org/abs/2406.09246))

오픈소스 7B VLA 로, full fine-tuning 과 함께 **LoRA fine-tuning 레시피** 를
제공해 사실상 로보틱스 LoRA 적응의 de-facto 기준선이 됐습니다(PriorVLA 의 base).
- **P4 접점**: D19(d) LoRA-FT 의 표준 레퍼런스. 단 사전학습 자체는 full-FT 라
  freeze-사전학습 초점은 약함.
- **분석 사유 (중간)**: LoRA-FT 레시피 참조 가치는 높으나 보존-사전학습 초점은
  간접적.

### OpenVLA-OFT — Optimizing Speed and Success ([arXiv:2502.19645](https://arxiv.org/abs/2502.19645))

OpenVLA 의 적응 레시피를 최적화한 후속으로, **병렬 디코딩 · action chunking ·
연속 행동 표현 · L1 회귀 목표** 가 적응 효율·성공률을 끌어올린다고 보고합니다.
순수 PEFT 라기보다 *적응 레시피* 이지만, vision encoder/디코딩 설계가 적응
비용에 미치는 영향(트렌드 ②)을 가늠하는 데 유용합니다.
- **P4 접점**: D23 action 표현·디코딩 설계, D19 동결 범위 trade-off.
- **분석 사유 (중간)**: PEFT 자체보다 적응 레시피 보조 자료.

### Natural Continual Learners with RL ([arXiv:2603.11653](https://arxiv.org/abs/2603.11653))

**sequential fine-tuning + LoRA** 가 VLA 의 continual RL 에서 강력하다고
보고하며, catastrophic forgetting 에 대한 통념(순차 학습=망각)에 도전합니다.
on-policy RL · stability-plasticity trade-off 를 다룹니다.
- **P4 접점**: D20 보존(망각) · D21 staged recipe 의 RL 확장. forgetting 직결.
- **분석 사유 (권고)**: "LoRA 가 RL 적응에서 오히려 덜 잊는다" 는 P4 D20 의
  핵심 가설과 맞닿은 최신 실증. deep-dive 가치 높음.

### Accessible Physical AI — LoRA-Based VLA ([arXiv:2512.11921](https://arxiv.org/abs/2512.11921))

LoRA fine-tuning 과 양자화를 결합해 소비자급 하드웨어(SO101 암)에서 VLA 를
배포하는 실용 연구입니다.
- **P4 접점**: D19(d) PEFT 의 *배포 경제성* 측면.
- **분석 사유 (낮음)**: 실용·재현 가치는 있으나 방법론적 신규성은 제한적.

---

## 4. 클러스터 2 — 기초 PEFT 방법론 (anchor)

> 로봇 비특화이지만 D19(d)/갈래 B① 에서 쓰는 도구의 출처입니다. 대부분 일반론
> 이라 단독 deep-dive 한계효용은 낮고, *기법 선택의 근거* 로 인용합니다.

- **LoRA** ([arXiv:2106.09685](https://arxiv.org/abs/2106.09685)) — $`W = W_0 + BA`$
  ($`r \ll \min(d,k)`$). 갱신을 저차원 부분공간에 가두는 정본. **(낮음)**
- **QLoRA** ([arXiv:2305.14314](https://arxiv.org/abs/2305.14314)) — 4-bit
  양자화 백본 + LoRA 로 큰 모델을 단일 GPU 에서 적응. 배포 경제성 축의 근거.
  **(낮음~중간)**
- **DoRA** ([arXiv:2402.09353](https://arxiv.org/abs/2402.09353)) — 가중치를
  magnitude·direction 으로 분해해 LoRA 의 full-FT 격차를 줄임. rank 대안. **(낮음~중간)**
- **AdaLoRA** ([arXiv:2303.10512](https://arxiv.org/abs/2303.10512)) — 중요도에
  따라 **rank 예산을 적응적으로 배분**. 트렌드 ①(task별 적응적 rank)의 정본.
  **(중간)**
- **Houlsby Adapter** ([arXiv:1902.00751](https://arxiv.org/abs/1902.00751)) —
  transformer 에 bottleneck adapter 를 삽입하는 원조 PEFT. 갈래 B① 출처. **(낮음)**
- **VL-Adapter** ([arXiv:2112.06825](https://arxiv.org/abs/2112.06825)) —
  vision-and-language 태스크에 adapter 를 적용해 full-FT 대비 소수 파라미터로
  경쟁력 달성. VLM→VLA 어댑터 설계의 멀티모달 가교. **(낮음~중간)**

---

## 5. 클러스터 3 — LoRA 효용·한계 분석

> "어디에 LoRA 를 붙였나" 를 넘어 **"LoRA 가 full-FT 를 언제 따라잡고 언제
> 망가지나"** 를 규정하는 분석군. D19(d) 이동의 *의사결정 근거* 가 됩니다.

- **LoRA vs Full Fine-tuning: An Illusion of Equivalence**
  ([arXiv:2410.21228](https://arxiv.org/abs/2410.21228)) — 같은 성능을 내도
  LoRA 와 full-FT 의 해(solution)는 다르며, LoRA 가 사전학습 스펙트럼에 없던
  새 특이방향("intruder dimensions")을 들여온다고 분석합니다. 이 구조적 차이가
  타깃 밖 일반화·보존과 연관된다는 점에서 D19(d) 이동의 *주의 신호* 입니다.
  **(중간)**
- **LoRA Learns Less and Forgets Less**
  ([arXiv:2405.09673](https://arxiv.org/abs/2405.09673)) — LoRA 는 타깃에서
  full-FT 보다 *덜 배우지만*(learns less) base 능력을 *덜 잊는다*(forgets less)
  — 즉 정규화처럼 작동. 이는 P4 D20(보존) 가설과 정면으로 맞닿아, "freeze 대신
  LoRA 로 열어도 망각이 제한적일 수 있다" 는 D19(d) 검토의 핵심 실증입니다.
  **(권고)**

### 실무 참조 (web — 논문 아님)

> 아래 두 자료는 사용자 제공 실무/교육 자료입니다. 자동 fetch 가 HTTP 403 으로
> 막혀 *원문 수치는 인용하지 않으며*, 일반 논지만 기재합니다(정직성 원칙).

- Thinking Machines — *LoRA Without Regret*
  ([web](https://thinkingmachines.ai/blog/lora/)) — LoRA 가 full-FT 를 따라잡는
  *조건*(적용 레이어 범위·충분한 rank·학습률 조정)을 실무 관점에서 정리한
  글로 알려져 있습니다. 정확한 권고 수치는 원문 직접 확인 필요(❓).
- apxml — *Comparing PEFT vs Full Fine-Tuning*
  ([web](https://apxml.com/courses/introduction-to-llm-fine-tuning/chapter-4-parameter-efficient-fine-tuning-peft/comparing-peft-full-fine-tuning))
  — PEFT vs full-FT 의 메모리·연산·성능·망각 trade-off 교육 자료.

---

## 6. 적응 단계 분화 트렌드

단순 LoRA 를 넘어 적응 단계가 세 갈래로 분화 중입니다(사용자 제공 프레임).
각 갈래를 후보·P4 결정에 매핑합니다.

- **① task별 적응적 rank 배분** — 고정 rank 대신 중요도/태스크별로 rank 예산을
  배분. 정본 AdaLoRA([arXiv:2303.10512](https://arxiv.org/abs/2303.10512)).
  P4 접점: D21 Stage 3 의 `lora.rank` 를 "작은 값부터" 스윕하는 대신 적응적
  배분으로 대체할 수 있는지 — 단 measurement-first(자매 문서 §6.2) 원칙 유지.
- **② vision encoder 동결-vs-해제 trade-off** — 백본 중 *어디까지* 여는지를
  체계 분석하는 방향. 갈래 A(격리) 와 직결되며, OpenVLA-OFT 의 디코딩/표현
  설계와 LoRA-vs-FullFT 분석(클러스터 3)이 근거. P4 접점: D19(a→c→d) 의 단계적
  개방 곡선 = 자매 문서의 Stage 2→3→4 forgetting 측정.
- **③ 다른 action space 를 위한 커스텀 action head + PEFT** — 기존 행동 공간과
  다른 로봇용으로 action head 를 새로 두고 PEFT 와 결합. TAIL · VLA-Adapter ·
  VLM2VLA 가 사례. P4 접점: D4/D7 split-head 가 곧 action-side adapter 라는
  P4 의 핵심 구조와 같은 평면.

---

## 7. 분석(deep-dive) 우선순위 권고

`/analyze-paper` 신규 실행 권고를 우선순위대로 정리합니다. P4 리포트
(2026-05-28)는 π0 · VLA-Adapter · VLM2VLA 를 이미 강력/권고로 꼽았으므로,
**여기서는 P4 리포트에 없던 NEW 랜드마크** 를 앞세웁니다.

1. **TAIL** ([arXiv:2310.05905](https://arxiv.org/abs/2310.05905)) — 로보틱스
   PEFT 기법 비교의 정본. D21 Stage 3 기법 선택 근거.
2. **LoRA Learns Less and Forgets Less**
   ([arXiv:2405.09673](https://arxiv.org/abs/2405.09673)) — "LoRA 가 덜 잊는다"
   는 D20 보존 가설의 직접 실증.
3. **Natural Continual Learners with RL**
   ([arXiv:2603.11653](https://arxiv.org/abs/2603.11653)) — continual RL +
   LoRA, forgetting 통념에 도전한 최신작.

그다음 P4 리포트와 공유하는 강력/권고 항목(VLA-Adapter · VLM2VLA · π0)은 P4
스카우트 리포트의 💡 컨텍스트 제안과 cross-link 합니다(중복 실행 방지).

---

## 8. 출처·검증

### 8-1. arXiv ID 검증 (15편 전수)

전부 arXiv abstract 페이지 title 대조 + HuggingFace `paper_search` 로 확인,
모두 resolve 됨. 🟢 verified: arXiv ID·제목. 🟡 partial: 본문 주장은 abstract/
요약 수준에서 인용(전문 미독). 후속 deep-dive 시 전문 대조 권장.

| 항목 | 검증 |
|---|---|
| arXiv ID·제목 (15편) | 🟢 verified |
| 논문 핵심 주장 | 🟡 partial (요약 기반, 전문 미독) |
| web 3종 (Thinking Machines·apxml·DigitalOcean) | 🔴 unverified (자동 fetch 403; `web` 참조로만) |

### 8-2. web 참조 목록

- [web](https://thinkingmachines.ai/blog/lora/) — Thinking Machines, *LoRA Without Regret*
- [web](https://apxml.com/courses/introduction-to-llm-fine-tuning/chapter-4-parameter-efficient-fine-tuning-peft/comparing-peft-full-fine-tuning) — apxml, PEFT vs Full FT
- [web](https://www.digitalocean.com/community/tutorials/vision-language-action-finetuning-robotics) — DigitalOcean, VLA finetuning for robotics

### 8-3. 자매 문서 cross-link

- `vlm-prior-preservation.md` — P4 forgetting × carve-out 분류, 경로 개입
  A~D, staged recipe, forward KL 측정. 본 문서의 갈래 A/B① 매핑 출처.
- `../../scouting/P4/2026-05-28.md` — P4 freeze+PEFT 랜드마크 스카우트
  리포트(π0·VLA-Adapter·VLM2VLA deep-dive 권고).
