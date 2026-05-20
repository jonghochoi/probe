# synthesis/

주간 스카우팅(`scouting/`) · 온디맨드 심층분석(`analysis/`)과 **분리된**
산출물 경로입니다.

새 논문을 찾는 곳도, 한 편을 깊게 파는 곳도 아닙니다. 이미 핀된
논문들 사이의 **핵심 연결고리를 서사로 압축**해 사람이 P# 아키텍처를
머릿속에 계속 들고 다닐 수 있게 하는 곳입니다.

| 파일 | 생성 주체 | 성격 |
|---|---|---|
| `P1_BRIEF.md` | `probe-p1-synthesis` Routine (월 1회) | `context/P1.md` §4(D1–D7) + §6(핀 논문)만 읽고 재생성 |
| `P2_BRIEF.md` | `probe-p2-synthesis` Routine (월 1회) | `context/P2.md` §4(D8–D12) + §6 |
| `P3_BRIEF.md` | `probe-p3-synthesis` Routine (월 1회) | `context/P3.md` §4(D13–D18) + §6 |
| `P4_BRIEF.md` | `probe-p4-synthesis` Routine (월 1회) | `context/P4.md` §4(D19–D23) + §6 |

- 파일명: pillar 단위 = `synthesis/P#_BRIEF.md`(예: `synthesis/P1_BRIEF.md`).
  날짜 토큰 없음 — 풀이 바뀌면 같은 파일을 갈아끼웁니다.
- 다른 PROBE 산출물과 마찬가지로 **한글 단일** 문서입니다.
- append 가 아니라 매번 **덮어쓰는** living snapshot 입니다(루틴 최초
  실행 시 파일이 생성됩니다).
- 입력은 `context/P#.md` §4(Decision Log) + §6(핀 논문)뿐 — 외부
  검색·MCP·`curl` 호출이 없어 인용 조작 위험이 없습니다. `context/` 는
  **절대 수정하지 않습니다**. 핀/Decision 변경 제안은 브리프의 💡
  컨텍스트 제안 섹션에만 적습니다.
- 형식·이모지·용어·링크 규칙은 `docs/STYLE_GUIDE.md` 를 정확히
  따릅니다.
- `probe-p#-synthesis` 는 [claude.ai/code/routines](https://claude.ai/code/routines)
  의 RemoteTrigger 루틴입니다(프롬프트: `.claude/prompts/synthesis-P#.md`,
  pillar별 1개). §6 핀이 바뀌면 월간 실행을 기다리지 말고 루틴 상세
  페이지의 **Run now** 로 즉시 재생성합니다. 자세한 설정은 루트
  `README.md` → Stage 3 Bonus 참조.
