# pulse/

주간 스카우팅(`scouting/`) · 월간 종합(`synthesis/`) · 온디맨드 심층분석
(`analysis/`)과 **분리된** 산출물 경로입니다.

새 논문을 찾거나 핀 논문을 재진술하거나 한 편을 깊게 파는 곳이 아니라,
팀 채팅에서 발생한 **동적 신호를 짧은 힌트 파일로 증류**해 다음 pillar별
스카우팅의 retrieval-weight nudge 로만 작동시키는 곳입니다. 산출물이 아니라
입력 보조이며, `context/` 와 충돌 시 정적 컨텍스트가 항상 승리합니다.

> **Status:** proof-of-concept (Tier A only). 2주 PoC. 자동화 미연동.

| 파일 | 생성 주체 | 성격 |
|---|---|---|
| `YYYY-MM-DD-P#.md` | `.claude/prompts/pulse-digest.md` (수동 1회/주) | `context/P#.md` + `pulse/inbox/<주간 export>` 만 읽고 pillar별 1개, 한 실행에서 최대 4개 |
| `_TEMPLATE.md` | 사람 소유 | 힌트 폼(에이전트는 이 골격을 채움) |
| `_EXAMPLE.md` | 사람 소유 | 품질 기준 예시 (P1 illustrative) |
| `EXPORT_GUIDE_KO.md` | 사람 소유 | Slack · Telegram 채팅 export 운영 가이드 |
| `inbox/` | 사람 입력 | 원시 채팅 export 투입처. `inbox/README.md` 외 전부 gitignored |

- 파일명: 실행일 + pillar = `pulse/YYYY-MM-DD-P#.md`(예:
  `pulse/2026-05-19-P1.md`). 스카우트는 `pulse/*-P#.md` 의 가장 최근
  파일만 읽습니다.
- 다른 PROBE 산출물과 마찬가지로 **한글 단일** 문서입니다.
- append 가 아니라 실행마다 **pillar별 새 파일**입니다. 신호 없는 pillar
  는 파일 생략 가능(덮어쓰지 않음).
- 입력은 `pulse/inbox/<주간 export>` 와 `context/P{1..4}.md` 뿐 —
  `context/` 는 **절대 수정하지 않습니다**. 수렴이 보이면 힌트의
  💡 *Context Links* 섹션에만 기록하고, 다음 스카우트가 💡 컨텍스트 제안
  에서 사람에게 올립니다.
- 폼은 `pulse/_TEMPLATE.md`, 형식·이모지·용어는 `docs/STYLE_GUIDE.md` 의
  분류를 따릅니다. 디지스트 절차는 `.claude/prompts/pulse-digest.md` 가
  단일 출처입니다.
- 채팅 export 운영 가이드(트러블슈팅·체크리스트 포함)는
  [`EXPORT_GUIDE_KO.md`](EXPORT_GUIDE_KO.md).
