# analysis/

주간 스카우팅(`scouting/`)·월간 종합(`synthesis/`)과 **분리된** 산출물
경로. 사람이 고른 **특정 논문 한 편**(보통 `context/MASTER.md` §8 Tracked
Literature)을 깊게 읽어 한글 심층 분석 + vendor-agnostic Layer 1 Design +
foundry 매핑 구현·검증을 남긴다.

논문마다 `<arxiv-id>/` 폴더 하나:

| 파일 | 생성 주체 | 성격 |
|---|---|---|
| `<id>/analysis.md` | `/analyze-paper` | 논문 한 편의 전문 우선 한글 심층 분석 |
| `<id>/design.md` | `/analyze-paper` | 위 분석에서 추출한 **Layer 1 Design** (vendor-agnostic) |
| `<id>/impl/<foundry>/impl.{md,patch}` | `/implement-design` | Design 을 한 foundry 좌표계로 매핑한 구현 가이드 + unified diff |
| `<id>/impl/<foundry>/test_*.py` | `/implement-design` | subclass-seam smoke test (`/validate-impl §🧬` 가 실행) |
| `<id>/impl/<foundry>/UNMAPPABLE.md` | `/implement-design` | 매핑 불가 시 한 줄 사유만 (impl 대신) |
| `<id>/validation/<foundry>.md` | `/validate-impl` | impl 을 Design+분석+foundry 코드와 대조한 검증 보고서 |
| `<id>/validation/<foundry>.round_<N>.md` | `/reproduce-paper` | 수렴 루프 라운드별 validation 사본 (N 은 0-indexed) |

- 전체 deep-dive 목록 = [`INDEX.md`](INDEX.md) — 머지 후 `main` 에서 `scripts/refresh-analysis-index.py` 가 자동 갱신 (PR 에서 직접 스테이지 안 함). 컬럼 규약 `docs/STYLE.md` §5-7, 정책 `CLAUDE.md` "Automatically-maintained indexes".
- cross-paper lineage 카탈로그(vlm / vla / dataset)와 pillar 방법론 문서는 별도 폴더 `catalogs/` — 사용법은 [`catalogs/README.md`](catalogs/README.md).

## 호출

네 슬래시 커맨드 모두 정식 로직은 `.claude/prompts/<name>.md` 에 있고, 커맨드
파일은 얇은 래퍼다.

- `/analyze-paper <arXiv id | url | pdf url>` → `analysis.md` + `design.md`. 본문은 `curl` 전문 우선 확보, 실패 시 ar5iv → 초록 단계 폴백하고 확보 수준을 헤더에 명시.
- `/implement-design analysis/<id>/design.md [--foundry <name>]` → `impl.md` + `impl.patch` (기본 `lerobot`). 매핑 불가 시 `UNMAPPABLE.md` 만.
- `/validate-impl analysis/<id>/design.md [--foundry <name>]` → `validation/<foundry>.md`. 정적 4-체크(📚/🔍/🧪/📐) + §🧬 실행 검증.
- `/reproduce-paper <arXiv id | design path> [--foundry <name>] [--max-rounds N]` — 위 셋을 위임 호출해 validation verdict 가 안정화되거나 라운드 상한까지 자동 수렴시키는 오케스트레이터 (기본 `--max-rounds 3`). 수렴 매트릭스·종료 사유의 정본은 `.claude/prompts/reproduction.md`.

- 호출 경로 — 로컬 인터랙티브(`claude` 세션에서 슬래시 입력) / 로컬 원샷(`claude -p "/analyze-paper 2410.07864"`) / 웹(claude.ai/code) 세 가지. 모두 셸 CLI 가 아니라 Claude Code 슬래시 커맨드.
- 다중 foundry — `<id>/impl/<foundry>/` 서브폴더로 수용. 같은 Design 을 `--foundry <name>` 만 바꿔 재사용 (Design 은 한 번 만들면 여러 foundry 공용).

## 절대 규칙

- `context/MASTER.md` 도 `vendor/lerobot/` 도 **절대 수정 금지**. 핀/Decision 제안은 분석 문서의 💡 컨텍스트 제안 섹션에만, vendor 갱신은 `vendor/lerobot/README.md` 절차로만.
- 한글 단일 문서 (영문 1차 파일 없음). 재실행 시 append 아니라 **덮어쓰는** 재생성.
- 입력은 사람이 슬래시 커맨드로 명시적으로 넘긴 논문 — `scouting/` → `analysis/` 자동 연결은 없음.
- 문서 구조: 분석 `docs/STYLE.md` §5 + `analysis/templates/analysis.md`, Design §6 + `analysis/templates/design.md`, 구현 §6 + `analysis/templates/impl.md`, 검증 §6-5 + `analysis/templates/validation.md`.
