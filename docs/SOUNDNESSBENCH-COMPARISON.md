# SoundnessBench → probe 구조 비교와 기능 이식

이 문서는 신규 벤치마크 [`SoundnessBench`](https://github.com/jonghochoi/soundnessbench)를
분석하고, probe와 구조적으로 비교한 뒤, probe로 이식한 기능과 그 근거를
한곳에 정리한 기록입니다. 구현은 두 단계로 나뉘며 본 문서는 그 "왜"를 담습니다.

## 1. SoundnessBench이란

ML 연구 제안(가설 + 실험 설계)의 **건전성(soundness/rigor)**을 LLM이 사전에
판단할 수 있는지 측정하는 벤치마크입니다. ICLR 제출물에서 재구성한 1,099개
제안에 리뷰어 soundness 하위 점수로 만든 `low`/`high` 라벨을 붙였습니다.

핵심 발견은 **optimism bias**입니다. 중립 프롬프트하에서 프런티어 LLM은
방법론적으로 부실한 제안을 반복적으로 "건전하다(high)"고 과대평가합니다.
이를 잡기 위해 두 가지 장치를 제공합니다.

- **aggressive 프롬프트** — "명백한 근거가 없으면 기본값 low" 정책으로
  과대평가를 상쇄.
- **정량 측정** — 정답 라벨 대비 accuracy와 Cohen's κ(우연 보정 일치도).

## 2. SoundnessBench 워크플로

순수 LLM-as-a-judge 파이프라인입니다(딥러닝 프레임워크 없음).

1. 데이터 다운로드 — `data/soundnessbench.jsonl`(1,099 쌍).
2. 프로바이더 설정 — `config/eval/eval.yaml`(OpenAI/Anthropic/Gemini/Vertex/vLLM).
3. 평가 실행 — `scripts/run_evaluation.py`가 JSONL 로드 → 논문 단위 stratified
   split → 프롬프트(neutral 또는 aggressive)로 채점 → JSON 파싱(`rigor_bucket`,
   `confidence`, `justification`).
4. 메트릭 — `accuracy` + `cohen_kappa`(`rigorbench/evaluation/metrics.py`).
5. 산출 — 모델·모드별 결과 JSON, 동시성·스냅샷 저장, seed 고정 재현성.

## 3. probe와의 구조적 차이

| 축 | SoundnessBench | probe |
|---|---|---|
| 본질 | 측정 도구(benchmark) | 생산 도구(agentic scout) |
| 형태 | Python 패키지(`rigorbench/`), API 호출 | 마크다운 프롬프트 + Claude 에이전트 |
| 정답 | 1,099 라벨 gold set | 없음 |
| 판정자 | LLM-as-judge(다중 프로바이더) | Claude 에이전트, 품질 미측정 |
| 측정 | accuracy + Cohen's κ | 없음 |
| 편향 인식 | optimism bias 상쇄(aggressive) | 없음(중립 채점) |
| 채점 차원 | rigor 1축(low/high) + confidence | 4축 0–3, soundness 축 부재 |

핵심 관찰: probe의 `Reproducibility` 축은 "코드/데이터 공개 여부"일 뿐,
**"주장이 실험으로 방법론적으로 뒷받침되는가(soundness)"**와는 다릅니다.
probe의 스카우트·분석은 매주 논문을 채점하고 config 변경을 권고하므로 그
자체가 LLM 건전성 판정기인데, (1) 중립 프롬프트로 채점하고 (2) 자기 판정이
맞는지 측정할 수단이 없습니다. 즉 probe는 SoundnessBench가 측정한 바로 그
optimism bias에 구조적으로 노출돼 있어, 부실한 논문을 ★★★로 추천하고 잘못된
파이프라인 변경을 권고할 위험이 있습니다.

## 4. 이식한 기능 (Phase 1) — 회의적 soundness 게이트

SoundnessBench의 aggressive 정책을 probe의 마크다운-프롬프트 구조에 이식했습니다
(새 코드 없음).

- `.claude/prompts/scouting.md` — 5번째 채점 축 `Soundness`(0–3) 추가.
  내부 타당성(통제·baseline·ablation·metric 타당성·주장-증거 일치)을 보며,
  "명백한 근거 없으면 낮게"라는 aggressive 기본값을 적용. `(c) 의사결정 함의`는
  Soundness ≥ 2일 때만 실행 가능한 변경을 발행하도록 게이트.
- `.claude/prompts/analysis.md` + `analysis/_TEMPLATE.md` — Part (A) 끝에
  `🩺 건전성 판정` 섹션 추가(`rigor_bucket` low|high 기본값 low + `confidence`
  1–5 + step-by-step 근거). 이 판정이 `⚙️ 의사결정 함의`를 게이트.
- `scouting/_TEMPLATE.md` — 점수 요약 표에 `Soundness` 열 추가(Total /12 → /15).
- `docs/STYLE.md` — §5-2에 `🩺` 등록, v1.19 changelog.

효과: 부실한 논문이 ★ 티어로 승격되거나 잘못된 config 변경으로 이어지는 것을
차단합니다.

## 5. 이식한 기능 (Phase 2) — 캘리브레이션 하니스 `eval/`

probe의 최대 공백(판정 품질 측정 불가)을 메웁니다. probe의 soundness 프롬프트를
**프로그램적으로** gold set에 돌려 accuracy + Cohen's κ를 측정하고, 중립 vs
회의적 프롬프트를 A/B 비교해 optimism bias 감소를 수치화합니다. `rigorbench`의
`metrics`·`client`·`run`을 출처 명시하에 적응 이식했습니다.

- `eval/judge/` — `buckets`(라벨 정규화), `metrics`(accuracy + Cohen's κ +
  신규 `optimism_metrics`의 false-high rate), `client`(다중 프로바이더 +
  offline `RandomBaseline`), `prompts`, `run`(채점 루프 + `compare_prompts` A/B).
- `eval/prompts/soundness_{neutral,skeptical}.md` — A/B 대상 프롬프트.
- `eval/data/gold.jsonl` — 소규모 robotics gold set(12 시드).
- `scripts/run-soundness-eval.py` — CLI 엔트리.

핵심 메트릭 `false_high_rate`는 gold가 `low`인 항목 중 `high`로 예측한 비율 —
optimism bias의 직접 지표이며, 회의적 프롬프트가 이를 낮추는지로 Phase 1 게이트의
효용을 검증합니다.

부트스트랩: robotics gold set을 대규모로 만들기 전, `--gold`를 형제 repo의
`SoundnessBench/data/soundnessbench.jsonl`(1,099 라벨)로 가리켜 즉시 캘리브레이션할
수 있습니다.

자세한 사용법은 `eval/README.md`를 참고하십시오.

## 6. 한 줄 요약

Phase 1은 *나쁜 추천을 막고*, Phase 2는 *추천이 얼마나 맞는지 측정*합니다.
둘을 합치면 probe는 "논문을 더 많이 찾는 도구"에서 "추천을 신뢰할 수 있는
도구"로 이동합니다.
