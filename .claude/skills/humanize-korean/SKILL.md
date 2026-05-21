---
name: humanize-korean
version: "1.5.0"
description: AI(ChatGPT·Claude·Gemini 등)가 쓴 한글 텍스트를 "사람이 쓴 글처럼" 윤문해주는 오케스트레이터 스킬. 번역투·영어 인용 과다·기계적 병렬·관용구·피동태 남용·접속사 남발·리듬 균일성·이모지/불릿 과다 등 10대 카테고리 40+ AI 티 패턴을 탐지·분류해 내용은 한 글자도 건드리지 않고 문체·리듬·표현만 자연스러운 한국어로 재작성한다. 트리거 — "AI 티 없애줘", "AI 같은 글 자연스럽게", "GPT/ChatGPT 문체", "AI 번역투 고쳐", "사람이 쓴 것처럼 윤문", "AI 윤문", "ChatGPT 티 제거", "한글 AI 탐지·윤문", "AI 글 사람처럼", "번역투 제거", "영어 인용 많은 글 윤문", "AI 글 티 안 나게", "휴머나이저", "humanize Korean", "AI detector bypass 한글". 후속 작업 — "특정 카테고리만 다시", "윤문 강도 조정", "장르 바꿔서", "이 문단만", "2차 윤문" 도 모두 이 스킬. 단순 맞춤법·오탈자 교정은 직접 처리, 번역은 번역 스킬, 내용 추가·삭제를 동반한 재작성은 별도 집필 스킬.
---

# Humanize Korean — AI 한글 티 제거 오케스트레이터 (v1.5)

> **PROBE 이식판 안내** — 본 스킬은 `epoko77-ai/im-not-ai` v1.5 에서 PROBE 로 이식됐다. PROBE 운용에서는 항상 **strict 모드 4 인 파이프라인(`ai-tell-detector` → `korean-style-rewriter` → [`content-fidelity-auditor` ∥ `naturalness-reviewer`])** 만 사용한다. monolith fast-path 는 PROBE 산출물(decision-grade 한글 문서)의 의미 보존 요건과 맞지 않아 비활성. 입력은 항상 파일 경로(`scouting/*.md`, `synthesis/*.md`, `analysis/*.md`)이며 출력은 in-place 갱신. `docs/STYLE.md` §4-5 가 본 스킬의 PROBE 측 invariants(롤백 트리거) 단일 출처이다.

## Phase 0: 컨텍스트 확인

작업 시작 시 한 줄을 출력한다.

```
humanize-korean (PROBE strict) / target: {file_path}
```

## Phase A: 탐지

`ai-tell-detector` 호출.

입력:
- `input_text`: 대상 파일의 전체 내용
- `genre_hint`: PROBE 컨텍스트에서는 `리포트` 고정 (scouting / synthesis / analysis 모두 리포트형)
- `options.min_severity`: `S2` (기본)
- `options.include_document_level`: `true`

출력: detector 의 `02_detection.json` 스키마 그대로 — `findings[]` + `meta`.

## Phase B: 윤문

`korean-style-rewriter` 호출.

입력:
- 원문 파일 경로
- Phase A 의 detection JSON
- `options.preserve_formatting`: `true` (PROBE 산출물의 헤딩·이모지·테이블 구조는 STYLE 가 강제하므로 유지)

출력: in-place 후보 rewrite + `03_rewrite_diff.json` (메모리 상)

## Phase C: 병렬 검증 (Fidelity + Naturalness)

`content-fidelity-auditor` 와 `naturalness-reviewer` 를 **병렬로** 호출한다. 두 검증층은 직교한다 — 전자는 "의미가 보존됐는가" 만, 후자는 "AI 티가 사라졌는가 + 과윤문되지 않았는가" 만 본다. PROBE 가 두 축을 모두 채택하는 이유는 rewriter 의 self-judgment(보류·적용 결정) 가 독립적으로 검증되어야 보수성·과적극 양쪽 편향을 모두 잡을 수 있기 때문이다.

### C-1. content-fidelity-auditor

입력:
- 원문 (Phase B 직전 상태)
- 후보 rewrite (Phase B 결과)
- diff JSON

출력: `04_fidelity_audit.json` — `audit_verdict` ∈ {`full_pass`, `conditional_pass`, `fail`}, `flagged_edits[]`

### C-2. naturalness-reviewer

입력:
- 원문
- 후보 rewrite
- Phase A 의 detection JSON (잔존 탐지 비교용)

출력: `05_naturalness_review.json` —
- `residual_findings[]`: S1/S2 패턴이 rewrite 후에도 남아 있는 항목
- `over_polish_findings[]`: 부자연스러운 문학체·어색한 리듬·억지 윤문 의심 구간
- `verdict` ∈ {`accept`, `accept_with_note`, `rewrite_round_2`, `rollback_and_rewrite`}

### PROBE 측 STYLE invariant 검사

`content-fidelity-auditor` 의 13항 체크리스트에 더해, PROBE 에서는 다음을 fidelity fail 로 동일 취급한다 (`docs/STYLE.md` §4-5 단일 출처):

- 원문 영어 논문 제목 변형
- 코드/설정명 (예: `env_cfg.py`, `ObservationManager`) 변형
- 수식·숫자 (예: `ε = 0.1`, `±2σ`) 변형
- `P#` / `D#` / `CP#` 태그 변형
- `<a id="ref-…">` 앵커 또는 `[CODE](#ref-CODE)` 링크 변형
- arXiv / DOI 링크 변형
- 이모지 종류·위치·"헤더당 1개" 규칙 위반
- `docs/STYLE.md` §4-2 용어집 외 임의 동의어로 기술 용어 치환
- 합니다/됩니다 정중체 이탈

위 항목이 단 하나라도 변형되면 `audit_verdict = fail` 처리.

## Phase D: 종합 판정 매트릭스

두 검증층의 출력을 AND 결합해 분기한다. 최대 3 회까지만 윤문 루프를 돌고, 그래도 미해결이면 사람 개입.

| fidelity | naturalness | 종합 | 후속 |
|---|---|---|---|
| `full_pass` | `accept` | **최종 승인** | 후보 rewrite 를 in-place 기록. 종료. |
| `full_pass` | `accept_with_note` | **승인 + 메모** | in-place 기록. 호출자 보고에 naturalness 메모 첨부. |
| `full_pass` | `rewrite_round_2` | **2 차 윤문** | rewriter 에 잔존 finding 만 다시 줘 Phase B 재호출. |
| `full_pass` | `rollback_and_rewrite` | **롤백 후 재윤문** | 과윤문 구간만 원문으로 되돌린 부분 rewrite 로 Phase B 재호출. |
| `conditional_pass` | * | **롤백된 edit 만 재시도** | fidelity 가 지정한 `rollback_required` edit 만 빼고 Phase B 재호출. |
| `fail` | * | **전면 재작업** | 후보 rewrite 폐기 후 Phase B 전면 재호출. |

2 차·3 차 윤문 진입 시 `03_rewrite_v2.md`·`v3.md` 로 버전 분리. **최대 3 회 후 미해결이면 `hold_and_report`** — 대상 파일은 원문 그대로 유지하고 호출자에게 미해결 finding 목록을 첨부해 사람 개입을 요청.

### 변경률 가드 (필수)

- 변경률 > 30% → rewriter 를 `--conservative` 시그널로 자동 1 회 재호출. 재호출 후에도 > 30% 이면 30% 초과분만 롤백.
- 변경률 > 50% → 즉시 전면 롤백 + `over_polish_warning` 보고.

## Phase E: 호출자 보고

호출자에게 다음 한 줄을 반환:

```
humanize-korean: {accept|partial|fail|hold} — change_rate X% / findings_resolved N/M / fidelity {full_pass|conditional_pass|fail} / naturalness {accept|accept_with_note|rewrite_round_2|rollback_and_rewrite}
```

`fail` 또는 `hold` 인 경우 사유 (어떤 invariant 가 깨졌는지, 어떤 finding 이 잔존했는지, 어떤 구간이 과윤문 의심인지) 1~2 문장 첨부.

## 옵션

- `장르: 리포트` (PROBE 고정, 변경 금지)
- `강도: 보수|기본` (기본값 보수 — PROBE 산출물은 의미 보존 우선)
- `최소심각도: S2` (기본, S1 으로 올리면 더 적게 고침)

## 데이터 흐름 요약

```
대상 파일 (in-place 대상)
    ↓ [ai-tell-detector]
detection JSON
    ↓ [korean-style-rewriter]
후보 rewrite + diff JSON
    ↓ [Phase C 병렬 검증]
    ├→ [content-fidelity-auditor + STYLE §4-5 invariants] → fidelity verdict
    └→ [naturalness-reviewer]                                    → naturalness verdict
    ↓ [Phase D 종합 매트릭스]
    ├ 최종 승인 / 승인+메모 → in-place 기록
    ├ 2 차·3 차 윤문        → Phase B 재호출 (최대 3 회)
    └ fail / hold           → 전면 롤백 + 보고
```

## 에이전트 호출 규칙

**모델:** 모두 `model: opus`.

**에이전트 정의 위치:** `<cwd>/.claude/agents/` (프로젝트 로컬).

필요 에이전트 4 종 (PROBE 이식판):
- `ai-tell-detector`
- `korean-style-rewriter`
- `content-fidelity-auditor`
- `naturalness-reviewer`

Phase C 의 fidelity-auditor 와 naturalness-reviewer 는 **반드시 병렬**로 호출한다 (단일 메시지에서 두 Agent 도구 호출). 결과를 모두 받은 뒤 Phase D 의 매트릭스로 분기.

## 주의 사항

- **의미 불변이 최상위 불문율.** Phase C 의 fidelity 결과가 fail 이면 무조건 롤백 — naturalness 가 accept 여도 fidelity 가 거부권을 갖는다.
- **과윤문도 실패다.** naturalness 가 `rollback_and_rewrite` 이면 fidelity 가 full_pass 여도 해당 구간은 원문으로 되돌린다.
- **수치·고유명사·직접 인용·코드명·태그·앵커·링크는 탐지/윤문 대상 아님.** Do-NOT list 엄수.
- **장르 이탈 금지.** PROBE 산출물은 리포트 장르로 고정.
- **register 보존.** 합니다/됩니다 정중체 입력 → 동일 정중체 출력.
- **자동 로드 금지.** 다른 파일을 자동 파싱해 옵션을 추론하지 않는다.

## 참고 자료

- 분류 체계: [`references/ai-tell-taxonomy.md`](references/ai-tell-taxonomy.md) — 10 대분류 × 40+ 패턴 전수
- 윤문 처방: [`references/rewriting-playbook.md`](references/rewriting-playbook.md) — 카테고리별 치환 레시피
- PROBE invariants 단일 출처: `docs/STYLE.md` §4-5
