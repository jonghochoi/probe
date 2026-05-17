# synthesis/

주간 스카우팅(`research_log/`)과 **분리된** 산출물 경로입니다.

새 논문을 찾는 곳이 아니라, 이미 핀된 논문들 사이의 **핵심 연결고리를
서사로 압축**해 사람이 머릿속에 계속 들고 다닐 수 있게 하는 곳입니다.

| 파일 | 생성 주체 | 성격 |
|---|---|---|
| `P1_BRIEF.md` | `probe-p1-synthesis` Routine (월 1회) | `research_context_P1.md` §4(D1–D9) + §6(핀 논문)만 읽고 재생성하는 living snapshot. append가 아니라 매번 덮어씀 |

`probe-p1-synthesis` 는 [claude.ai/code/routines](https://claude.ai/code/routines)
의 RemoteTrigger 루틴입니다(프롬프트: `.claude/prompts/synthesis.md`).
풀(§6 핀 논문)이 바뀌면 다음 월간 실행을 기다리지 말고 루틴 상세
페이지의 **Run now** 로 즉시 재생성해 직관을 리프레시합니다. 외부
검색·MCP·curl 호출 없음 — 오직 정적 파일의 압축이라 인용 조작
위험이 없습니다.
