# scouting/

월간 종합(`synthesis/`) · 온디맨드 심층분석(`analysis/`)과 함께 PROBE
산출물의 한 축인 **주간 스카우팅 리포트** 경로입니다. 이미 핀된 논문을
재진술하거나 한 편을 깊게 파는 곳이 아니라, **새 논문을 바깥에서 찾아오는**
곳이며, 매주 월·목 2회, pillar별로 실행되어 그 주의 arXiv·Citation Graph·
Author Watch를 훑고 의사결정 등급 후보만 추립니다.

| 파일 | 생성 주체 | 성격 |
|---|---|---|
| `YYYY-MM-DD-P#.md` | `probe-weekly-scout` Routine (주 2회, 월·목) | `context/P#.md` + 해당 pillar 최근 ~2주 리포트만 읽고 그 실행분 1개 생성 |
| `_TEMPLATE.md` | 사람 소유 | 리포트 폼(에이전트는 이 골격을 채움) |

## 호출

`probe-weekly-scout` 는 [claude.ai/code/routines](https://claude.ai/code/routines)
의 RemoteTrigger 루틴입니다. 프롬프트는 `.claude/prompts/scouting-P#.md`
(pillar별 1개), 검색은 MCP 가 아니라 `curl` REST (arXiv + Semantic Scholar)
입니다. 한 실행은 한 pillar 만 처리하며 결과 파일은 `YYYY-MM-DD-P#.md`
하나입니다. 자세한 설정은 루트 `README.md` → Stage 3 참조.

## 다른 산출물·컨텍스트와의 관계

- 입력: `context/P#.md` (pillar 추출본) + 같은 pillar 의 최근 ~2주 `scouting/`
  리포트.
- 출력 흐름: 리포트는 그 자체로 결정 기록입니다. 핀/Decision 변경
  제안은 리포트의 💡 컨텍스트 제안 섹션에 남기고, 다음 `synthesis/`
  월간 실행이 핀 변경을 반영합니다.

## 절대 규칙

- `context/` 는 **절대 수정하지 않습니다**. 핀/Decision 변경 제안은
  리포트의 💡 컨텍스트 제안 섹션에만 적습니다.
- 한글 단일 문서 (영문 1차 파일 없음). 파일명 verbatim 토큰
  `YYYY-MM-DD-P#.md` 로 중복 제거·재조회.
- append 가 아니라 실행마다 **새 파일 1개** — 덮어쓰지 않습니다.
- 형식·이모지·용어·링크 규칙은 `docs/STYLE.md` 를 정확히
  따릅니다. 폼은 `scouting/_TEMPLATE.md`.
