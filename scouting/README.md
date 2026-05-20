# scouting/

월간 종합(`synthesis/`) · 온디맨드 심층분석(`analysis/`)과 함께 PROBE
산출물의 한 축인 **주간 스카우팅 리포트** 경로입니다.

이미 핀된 논문을 재진술하거나 한 편을 깊게 파는 곳이 아니라, **새 논문을
바깥에서 찾아오는** 곳입니다. 매주 월·목 2회, pillar별로 실행되어 그 주의
arXiv·Citation Graph·Author Watch를 훑고 의사결정 등급 후보만 추립니다.

| 파일 | 생성 주체 | 성격 |
|---|---|---|
| `YYYY-MM-DD-P#.md` | `probe-weekly-scout` Routine (주 2회, 월·목) | `context/P#.md` + 해당 pillar 최근 ~2주 리포트만 읽고 그 실행분 1개 생성 |
| `_TEMPLATE.md` | 사람 소유 | 리포트 폼(에이전트는 이 골격을 채움) |

- 파일명: 실행일 + pillar = `scouting/YYYY-MM-DD-P#.md`(예:
  `scouting/2026-05-19-P1.md`). 이 verbatim 토큰으로 중복 제거·재조회.
- 다른 PROBE 산출물과 마찬가지로 **한글 단일** 문서입니다.
- append 가 아니라 실행마다 **새 파일 1개**입니다(덮어쓰지 않음).
- 입력은 `context/P#.md`(pillar 추출본)와 같은 pillar의 최근 ~2주
  리포트뿐 — 컨텍스트를 가볍게 유지합니다. `context/` 는 **절대 수정하지
  않습니다**. 핀/Decision 변경 제안은 리포트의 💡 컨텍스트 제안 섹션에만
  적습니다.
- 옵션 입력: `pulse/*-P#.md`(같은 pillar 의 최신 1개) — PoC 단계의
  채팅 힌트로, retrieval-weight nudge 로만 작용합니다. 정적 `context/`
  가 충돌 시 항상 승리합니다. 없으면 무시.
- 폼은 `scouting/_TEMPLATE.md`, 형식·이모지·용어·링크 규칙은
  `docs/STYLE_GUIDE.md` 를 정확히 따릅니다.
- `probe-weekly-scout` 는 [claude.ai/code/routines](https://claude.ai/code/routines)
  의 RemoteTrigger 루틴입니다(프롬프트: `.claude/prompts/scouting-P#.md`,
  pillar별 1개). 검색은 MCP 가 아니라 `curl` REST(arXiv + Semantic
  Scholar)입니다. 자세한 설정은 루트 `README.md` → Stage 3 참조.
