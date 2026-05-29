---
name: humanize-korean
version: "2.0.0"
description: AI(ChatGPT·Claude·Gemini 등)가 쓴 한글 텍스트를 "사람이 쓴 글처럼" 윤문해주는 오케스트레이터 스킬. 번역투·영어 인용 과다·기계적 병렬·관용구·피동태 남용·접속사 남발·리듬 균일성·이모지/불릿 과다 등 10대 카테고리 40+ AI 티 패턴을 탐지·분류해 내용은 한 글자도 건드리지 않고 문체·리듬·표현만 자연스러운 한국어로 재작성한다. 트리거 — "AI 티 없애줘", "AI 같은 글 자연스럽게", "GPT/ChatGPT 문체", "AI 번역투 고쳐", "사람이 쓴 것처럼 윤문", "AI 윤문", "ChatGPT 티 제거", "한글 AI 탐지·윤문", "AI 글 사람처럼", "번역투 제거", "영어 인용 많은 글 윤문", "AI 글 티 안 나게", "휴머나이저", "humanize Korean", "AI detector bypass 한글". 후속 작업 — "특정 카테고리만 다시", "윤문 강도 조정", "장르 바꿔서", "이 문단만", "2차 윤문" 도 모두 이 스킬. 단순 맞춤법·오탈자 교정은 직접 처리, 번역은 번역 스킬, 내용 추가·삭제를 동반한 재작성은 별도 집필 스킬. PROBE 호출 시 file_path prefix 로 mode (fast/standard/strict) 가 자동 결정되며 호출자가 `options.mode` 로 override 가능.
---

# Humanize Korean — AI 한글 티 제거 오케스트레이터 (v2.0)

> **PROBE 이식판 안내** — 본 스킬은 `epoko77-ai/im-not-ai` v1.5 에서 PROBE 로 이식 후 v2.0 에서 3-tier 모드 (`fast` / `standard` / `strict`) 로 분기된다. file_path prefix 에 따라 자동 선택되며 (`scouting/` → fast, `synthesis/` → standard, `analysis/` → standard), 호출자가 `options.mode` 로 override 가능 (strict 는 자동 기본값이 아니라 명시 지정으로만 진입). `docs/STYLE.md` §4-5 invariants 는 어느 모드에서나 동등하게 강제된다 — 이 단일 출처를 어떤 tier 도 우회하지 않는다. monolith fast-path 는 어느 모드에서도 사용하지 않는다. 입력은 항상 파일 경로이며 출력은 in-place 갱신.

## 의존 sub-agent (반드시 함께 존재해야 함)

본 스킬은 자기완결적이지 **않다** — Phase A/B/C 가 호출하는 4 개 sub-agent
정의가 `.claude/agents/` 에 함께 있어야 동작한다. 스킬 폴더만 다른 레포로
복사하면 깨지므로, 이식 시 아래 4 개 파일도 같은 리비전으로 함께 옮긴다.

| Phase | 호출되는 sub-agent | 모드 가용성 | 정의 파일 |
|---|---|---|---|
| A   | `ai-tell-detector`         | fast / standard / strict | `.claude/agents/ai-tell-detector.md` |
| B   | `korean-style-rewriter`    | fast / standard / strict | `.claude/agents/korean-style-rewriter.md` |
| C-1 | `content-fidelity-auditor` | standard / strict (fast 모드는 인라인 invariant 검사로 대체) | `.claude/agents/content-fidelity-auditor.md` |
| C-2 | `naturalness-reviewer`     | standard (final 1회) / strict (매 round) | `.claude/agents/naturalness-reviewer.md` |

추가로 본 스킬 폴더 안의 두 reference 문서(`references/ai-tell-taxonomy.md`,
`references/rewriting-playbook.md`)는 위 sub-agent 들이 진단·윤문 근거로
직접 읽으므로 함께 유지해야 한다. 3-tier 파이프라인의 검증 절차·STYLE
invariants 정본은 본 SKILL.md (Phase 0/A/B/C/D/E) 와 `docs/STYLE.md` §4-5
두 군데이며, sub-agent 의 system prompt 는 이 두 문서를 반복 재기술하지
않는다.

## Phase 0: 컨텍스트 확인 및 모드 결정

```
mode := options.mode ?? (
    file_path startswith "scouting/"  → "fast"
    file_path startswith "synthesis/" → "standard"
    file_path startswith "analysis/"  → "standard"
    else                              → "standard"
)
# 우선순위: options.mode > prefix > default
# 세 tier (fast/standard/strict) 모두 어느 경로에서나 options.mode 로
# 명시 지정 가능. strict 는 명시 지정으로만 진입한다 (자동 기본값 아님).
```

작업 시작 시 한 줄을 출력한다.

```
humanize-korean (PROBE {mode}) / target: {file_path}
```

## Phase A: 탐지

`ai-tell-detector` 호출. 모드별로 Task 도구의 `model` 파라미터를 지정한다. agent frontmatter 의 `model: opus` 는 default 로 남겨두고 (수동 호출·upstream 호환), 오케스트레이터가 호출 시점에만 override.

| 모드 | model 파라미터 |
|---|---|
| fast | `haiku-4-5` |
| standard | `sonnet-4-6` |
| strict | `opus` (default, 명시 생략 가능) |

입력:
- `input_text`: 대상 파일의 전체 내용
- `genre_hint`: PROBE 컨텍스트에서는 `리포트` 고정 (scouting / synthesis / analysis 모두 리포트형)
- `options.min_severity`: `S2` (기본)
- `options.include_document_level`: `true`

출력: detector 의 `02_detection.json` 스키마 그대로 — `findings[]` + `meta`.

## Phase B: 윤문

`korean-style-rewriter` 호출. 모드별로 model 지정.

| 모드 | model | 추가 시그널 |
|---|---|---|
| fast | `sonnet-4-6` | `--conservative` 기본 (Sonnet 의 윤문 자유도를 사전 제한) |
| standard | `opus` | — |
| strict | `opus` | — |

입력:
- 원문 파일 경로
- Phase A 의 detection JSON
- `options.preserve_formatting`: `true` (PROBE 산출물의 헤딩·이모지·테이블 구조는 STYLE 가 강제하므로 유지)

출력: in-place 후보 rewrite + `03_rewrite_diff.json` (메모리 상). `edits[]` 각 항목의 `before` span 은 Phase C 의 `target_spans` 입력으로 재사용된다.

## Phase C: 검증 (모드별 분기)

### fast 모드 — 인라인 STYLE invariant 검사만

별도 agent 호출 없음. 오케스트레이터가 원문과 rewrite 본문 양쪽에서 invariant token 을 추출해 **set-difference 가 비어 있는지** 확인한다. (`docs/STYLE.md` §4-5 의 9개 invariant 가 SSOT.)

추출·비교 대상 (각 패턴마다 `set(original) \ set(rewrite)` 이 비어 있어야 통과):

- **영어 논문 제목**: 원문의 `> "..."` 인용 블록 또는 §4-1 형식의 영문 제목 토큰
- **코드/설정명**: 인라인 코드 토큰 — `` `[A-Za-z_][A-Za-z0-9_./-]*` `` (예: `env_cfg.py`, `ObservationManager`)
- **수식·숫자**: `ε = 0.1`, `±2σ`, `< 15%`, `2.0×10^-4` 등 수식·수치 토큰
- **`P#` / `D#` / `CP#` 태그**: 정규식 `\b(P\d|D\d|CP\d+)\b` 매치 토큰
- **앵커**: `<a\s+id="ref-[^"]+">…</a>` 전체 형태 보존
- **인트라 링크**: `\[[^\]]+\]\(#ref-[^)]+\)` 형태 보존
- **arXiv / DOI 링크**: `https?://(arxiv\.org|doi\.org)/\S+` 형태 보존
- **이모지 헤더 규칙**: 원문 각 헤더에 등장한 emoji 의 종류·위치·"헤더당 1개" 가 동일
- **정중체 종결**: 원문이 합니다/됩니다 정중체였다면 rewrite 의 모든 문장 말미도 동일 register

검사 결과:
- 모두 통과 → `inline_invariant_pass` → 즉시 in-place 기록 후 종료.
- 어느 항목이라도 fail → `inline_invariant_fail` → 해당 edit 만 롤백 (원문 span 으로 복원), 나머지는 유지. 재호출 없음 (fast 모드 loop 한도 1).

> 주의: 이 정규식 셋은 `docs/STYLE.md` §4-5 의 invariant 목록을 ground 한 결과물이다. STYLE.md 가 변경되면 본 셋도 같은 PR 에서 동시 업데이트해 drift 를 방지한다.

### standard 모드 — `content-fidelity-auditor` (필수) + `naturalness-reviewer` (final 1회만)

C-1 (fidelity-auditor) 만 main loop 에서 호출. naturalness-reviewer 는 loop 가 fidelity full_pass 로 종료한 직후 final round 1회만 호출해 과윤문 시그널을 마지막으로 점검한다.

### strict 모드 — `content-fidelity-auditor` ∥ `naturalness-reviewer` (병렬, 매 round)

기존 4-agent 동작 그대로. 두 검증층은 직교한다 — 전자는 "의미가 보존됐는가" 만, 후자는 "AI 티가 사라졌는가 + 과윤문되지 않았는가" 만 본다.

### C-1. content-fidelity-auditor (standard / strict 공통)

입력:
- 원문 (Phase B 직전 상태)
- 후보 rewrite (Phase B 결과)
- diff JSON

출력: `04_fidelity_audit.json` — `audit_verdict` ∈ {`full_pass`, `conditional_pass`, `fail`}, `flagged_edits[]`

### C-2. naturalness-reviewer (standard final / strict 매 round)

입력:
- 원문
- 후보 rewrite
- Phase A 의 detection JSON (잔존 탐지 비교용)
- **`target_spans`**: rewriter 의 `03_rewrite_diff.json:edits[]` 의 `before` span 목록 + `context_radius: 200` — diff 영역 ± 200자만 재스캔하라는 지시. 전체 문서 재스캔 대비 입력 텍스트가 1/3~1/5 로 감소.

출력: `05_naturalness_review.json` —
- `residual_findings[]`: S1/S2 패턴이 rewrite 후에도 남아 있는 항목 (target_spans 범위 내)
- `over_polish_findings[]`: 부자연스러운 문학체·어색한 리듬·억지 윤문 의심 구간
- `verdict` ∈ {`accept`, `accept_with_note`, `rewrite_round_2`, `rollback_and_rewrite`}
- `meta.scan_scope`: `"diff_only"` (standard / strict 공통 기본값)

### PROBE 측 STYLE invariant 검사 (standard / strict)

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

위 항목이 단 하나라도 변형되면 standard·strict 에서는 `audit_verdict = fail`, fast 에서는 `inline_invariant_fail` 처리.

## Phase D: 종합 판정 매트릭스 (모드별 차등)

| 모드 | Loop 한도 | 매트릭스 |
|---|---|---|
| fast | 1 | invariant_pass → 승인. invariant_fail → 해당 edit 만 롤백 후 승인. 재호출 없음. |
| standard | 2 | 아래 매트릭스 (단 naturalness 는 loop 종료 직전 final round 1회만 평가) |
| strict | 3 | 아래 매트릭스 (현행 — naturalness 매 round 평가) |

standard / strict 판정 매트릭스 (현행 v1.5 그대로 유지):

| fidelity | naturalness | 종합 | 후속 |
|---|---|---|---|
| `full_pass` | `accept` | **최종 승인** | 후보 rewrite 를 in-place 기록. 종료. |
| `full_pass` | `accept_with_note` | **승인 + 메모** | in-place 기록. 호출자 보고에 naturalness 메모 첨부. |
| `full_pass` | `rewrite_round_2` | **2 차 윤문** | rewriter 에 잔존 finding 만 다시 줘 Phase B 재호출. |
| `full_pass` | `rollback_and_rewrite` | **롤백 후 재윤문** | 과윤문 구간만 원문으로 되돌린 부분 rewrite 로 Phase B 재호출. |
| `conditional_pass` | * | **롤백된 edit 만 재시도** | fidelity 가 지정한 `rollback_required` edit 만 빼고 Phase B 재호출. |
| `fail` | * | **전면 재작업** | 후보 rewrite 폐기 후 Phase B 전면 재호출. |

2 차·3 차 윤문 진입 시 `03_rewrite_v2.md`·`v3.md` 로 버전 분리. **각 모드 loop 한도 초과 후 미해결이면 `hold_and_report`** — 대상 파일은 원문 그대로 유지하고 호출자에게 미해결 finding 목록을 첨부해 사람 개입을 요청.

### 변경률 가드 (모드별)

| 모드 | 재호출 임계 | 즉시 전면 롤백 임계 |
|---|---|---|
| fast | > 25% → 임계 초과분 (over-edit) 만 부분 롤백. 재호출 없음. | > 40% → 즉시 전면 롤백 + `over_polish_warning` 보고 |
| standard | > 30% (현행) → rewriter `--conservative` 시그널로 1 회 재호출 | > 50% (현행) → 즉시 전면 롤백 + `over_polish_warning` |
| strict | > 30% (현행) → rewriter `--conservative` 시그널로 1 회 재호출 | > 50% (현행) → 즉시 전면 롤백 + `over_polish_warning` |

재호출 후에도 임계를 초과하면 초과분만 롤백.

## Phase E: 호출자 보고

호출자에게 다음 한 줄을 반환:

```
humanize-korean: {accept|partial|fail|hold} — mode {fast|standard|strict} / change_rate X% / findings_resolved N/M / fidelity {full_pass|conditional_pass|fail|skipped} / naturalness {accept|accept_with_note|rewrite_round_2|rollback_and_rewrite|skipped} / est_tokens ~{K}k (input={chars}c × loads={n})
```

- `est_tokens` (회귀 감시용 추정치, 별도 측정 agent 없음):
  - 공식: `(input_chars + ref_chars_loaded × loads) × agents_invoked / 4`
  - 4 자/토큰 환산. fast 모드 ref ≈ 11KB (rewriter playbook 만), standard/strict 모드 ref ≈ 71KB (detector taxonomy + rewriter playbook).
  - `loads`: 루프 회수.
  - 정확도 ±30% 가정. 진짜 측정값이 필요할 때만 `options.measure: true` 로 각 agent 의 `usage` 블록 수집 (영구 활성화 안 함).
- `fidelity` / `naturalness` 가 모드 정의상 호출되지 않았으면 `skipped` 로 표기.
- 모드 override 관련 특이사항이 있으면 (잘못된 `options.mode` 값 무시 등) 첫 줄 다음에 `mode_override_warning: {reason}` 한 줄 추가.

`fail` 또는 `hold` 인 경우 사유 (어떤 invariant 가 깨졌는지, 어떤 finding 이 잔존했는지, 어떤 구간이 과윤문 의심인지) 1~2 문장 첨부.

## 옵션

- `장르: 리포트` (PROBE 고정, 변경 금지)
- `강도: 보수|기본` (기본값 보수 — PROBE 산출물은 의미 보존 우선)
- `최소심각도: S2` (기본, S1 으로 올리면 더 적게 고침)
- `mode: fast|standard|strict` (지정 시 자동 결정 override. 세 tier 모두 어느 경로에서나 명시 지정 가능.)
- `measure: true|false` (기본 false. true 시 각 agent 의 `usage` 블록을 수집해 Phase E 에 exact token 보고 첨부.)

## 데이터 흐름 요약

```
대상 파일 (in-place 대상)
    ↓ [Phase 0: mode 결정 (options > prefix > default)]
    ↓ [Phase A: ai-tell-detector (mode-aware model)]
detection JSON
    ↓ [Phase B: korean-style-rewriter (mode-aware model)]
후보 rewrite + diff JSON
    ↓ [Phase C: 모드별 검증]
    ├ fast:     인라인 STYLE invariant 정규식 검사 (no agent)
    ├ standard: content-fidelity-auditor (필수) + naturalness-reviewer (final 1회, diff_only)
    └ strict:   content-fidelity-auditor ∥ naturalness-reviewer (병렬, 매 round, diff_only)
    ↓ [Phase D: 모드별 매트릭스 + loop 한도 (1/2/3)]
    ├ 승인        → in-place 기록
    ├ 재윤문      → Phase B 재호출 (모드 한도 내)
    └ fail / hold → 전면 롤백 + 보고
    ↓ [Phase E: 보고 한 줄 (mode, change_rate, findings, est_tokens)]
```

## 에이전트 호출 규칙

**모델 (Task 도구 `model` 파라미터 override):**

| agent | fast | standard | strict |
|---|---|---|---|
| `ai-tell-detector` | `haiku-4-5` | `sonnet-4-6` | `opus` (default) |
| `korean-style-rewriter` | `sonnet-4-6` | `opus` | `opus` (default) |
| `content-fidelity-auditor` | — (호출 안 함) | `opus` | `opus` (default) |
| `naturalness-reviewer` | — (호출 안 함) | `opus` (final 1회) | `opus` (default) |

agent frontmatter 의 `model: opus` 는 변경하지 않는다 — default 로 남겨두면 strict 모드와 수동 호출이 영향을 안 받고, fast/standard 모드에서만 호출 시점 override 로 다운그레이드한다.

**에이전트 정의 위치:** `<cwd>/.claude/agents/` (프로젝트 로컬).

필요 에이전트 4 종 (PROBE 이식판):
- `ai-tell-detector`
- `korean-style-rewriter`
- `content-fidelity-auditor` (standard·strict 만)
- `naturalness-reviewer` (standard final·strict 만)

strict 모드의 Phase C 의 fidelity-auditor 와 naturalness-reviewer 는 **반드시 병렬**로 호출한다 (단일 메시지에서 두 Agent 도구 호출). standard 모드는 main loop 에서 fidelity 만 호출하고, naturalness 는 loop 종료 직전 1회만 sequential 호출. fast 모드는 둘 다 호출하지 않고 인라인 invariant 검사로 대체한다.

## 주의 사항

- **의미 불변이 최상위 불문율.** fidelity 결과가 fail 이면 (또는 fast 모드의 인라인 invariant 가 fail 이면) 무조건 롤백 — naturalness 가 accept 여도 fidelity / invariant 가 거부권을 갖는다.
- **과윤문도 실패다.** naturalness 가 `rollback_and_rewrite` 이면 fidelity 가 full_pass 여도 해당 구간은 원문으로 되돌린다.
- **수치·고유명사·직접 인용·코드명·태그·앵커·링크는 탐지/윤문 대상 아님.** Do-NOT list 엄수.
- **장르 이탈 금지.** PROBE 산출물은 리포트 장르로 고정.
- **register 보존.** 합니다/됩니다 정중체 입력 → 동일 정중체 출력.
- **자동 로드 금지.** 다른 파일을 자동 파싱해 옵션을 추론하지 않는다.
- **STYLE.md §4-5 가 SSOT.** 본 스킬의 invariant 정규식 셋은 STYLE.md §4-5 의 invariant 목록을 ground 한 결과물 — STYLE.md 변경 시 본 스킬도 동시 변경해야 drift 방지.

## 참고 자료

- 분류 체계: [`references/ai-tell-taxonomy.md`](references/ai-tell-taxonomy.md) — 10 대분류 × 40+ 패턴 전수 (detector 가 로드)
- 윤문 처방: [`references/rewriting-playbook.md`](references/rewriting-playbook.md) — 카테고리별 치환 레시피 (rewriter 가 로드)
- PROBE invariants SSOT: `docs/STYLE.md` §4-5
