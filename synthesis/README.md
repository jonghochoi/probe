# synthesis/

**월간 per-pillar 종합 브리프** — 이미 핀된 논문들 사이의 핵심 연결고리를
서사로 압축해, 사람이 P# 아키텍처를 머릿속에 들고 다닐 수 있게 하는 living
snapshot. (새 논문 탐색은 `scouting/`, 한 편 심층은 `analysis/`.)

| 파일 | 생성 주체 | 성격 |
|---|---|---|
| `P#_BRIEF.md` | `probe-p#-synthesis` Routine (월 1회) | `context/P#.md` §4(Decision Log) + §6(핀 논문)만 읽고 재생성 |

## 호출

- `probe-p#-synthesis` = [claude.ai/code/routines](https://claude.ai/code/routines) RemoteTrigger 루틴.
- 프롬프트 = `.claude/prompts/synthesis.md` 한 개 (pillar 4종 공유; 붙여넣기 전 `<PILLAR>` 토큰을 `P1`~`P4` 중 하나로 1회 치환).
- 입력 = `context/P#.md` §4 + §6 **만** — 외부 검색·MCP·`curl` 일절 없음 (인용 조작 원천 차단).
- 핀이 바뀌면 월간 실행을 기다리지 말고 루틴 상세의 **Run now** 로 즉시 재생성. 자세한 설정은 루트 `README.md` → Stage 3 Bonus.

## 절대 규칙

- `context/` 는 **절대 수정 금지** — 핀/Decision 변경 제안은 브리프의 💡 컨텍스트 제안 섹션에만.
- 한글 단일 문서 (영문 1차 파일 없음). 파일명에 날짜 토큰 없음.
- append 아니라 매번 **덮어쓰는** living snapshot.
- 형식·이모지·용어·링크는 `docs/STYLE.md`.
