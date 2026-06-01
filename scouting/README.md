# scouting/

**주간 스카우팅 리포트** — 매주 월·목, pillar별로 새 논문을 바깥에서 찾아
의사결정 등급 후보만 추리는 산출물 경로. (핀 논문 재진술은 `synthesis/`,
한 편 심층은 `analysis/`.)

| 파일 | 생성 주체 | 성격 |
|---|---|---|
| `P#/YYYY-MM-DD.md` | `probe-weekly-scout` Routine (주 2회) | `context/P#.md` + 같은 `P#/` 폴더의 최근 ~2주 리포트만 읽고 실행분 1개 생성 |
| `templates/report.md` | 사람 소유 | 리포트 폼 (에이전트가 채움) |

필라별 폴더 (`P1/`~`P4/`)로 분리 — 한 실행은 한 pillar 만 처리.

## 호출

- `probe-weekly-scout` = [claude.ai/code/routines](https://claude.ai/code/routines) RemoteTrigger 루틴.
- 프롬프트 = `.claude/prompts/scouting.md` 한 개 (pillar 4종 공유; 붙여넣기 전 `<PILLAR>` 토큰을 `P1`~`P4` 중 하나로 1회 치환).
- 입력 = `context/P#.md` + 같은 pillar 최근 ~2주 리포트. 검색은 `curl` REST (arXiv + Semantic Scholar), MCP 아님.
- 자세한 설정은 루트 `README.md` → Stage 3.

## 절대 규칙

- `context/` 는 **절대 수정 금지** — 핀/Decision 변경 제안은 리포트의 💡 컨텍스트 제안 섹션에만.
- 한글 단일 문서 (영문 1차 파일 없음). 경로 verbatim `scouting/P#/YYYY-MM-DD.md` 로 중복 제거·재조회.
- append 아니라 실행마다 **새 파일 1개** — 덮어쓰지 않음.
- 형식·이모지·용어·링크는 `docs/STYLE.md`, 폼은 `templates/report.md`.
