# pulse/

주간 스카우팅(`scouting/`) · 월간 종합(`synthesis/`) · 온디맨드 심층분석
(`analysis/`)과 **분리된** 산출물 경로 — 정확히는 산출물이 아니라
**입력 보조** 입니다. 팀 채팅에서 발생한 동적 신호를 짧은 힌트 파일로
증류해 다음 pillar별 스카우팅의 retrieval-weight nudge 로만 작동시키는
곳이며, `context/` 와 충돌 시 정적 컨텍스트가 항상 승리합니다.
**Tier A PoC** — 수동 1회/주, 자동화 미연동, 2주 trial 단계입니다.

| 파일 | 생성 주체 | 성격 |
|---|---|---|
| `YYYY-MM-DD-P#.md` | `.claude/prompts/pulse-digest.md` (수동 1회/주) | `context/P#.md` + `pulse/inbox/<주간 export>` 만 읽고 pillar별 1개, 한 실행에서 최대 4개 |
| `_TEMPLATE.md` | 사람 소유 | 힌트 폼(에이전트는 이 골격을 채움) |
| `_EXAMPLE.md` | 사람 소유 | 품질 기준 예시 (P1 illustrative) |
| `EXPORT_GUIDE.md` | 사람 소유 | Slack · Telegram 채팅 export 운영 가이드 |
| `inbox/` | 사람 입력 | 원시 채팅 export 투입처. `inbox/README.md` 외 전부 gitignored |

## 호출

수동 1회/주, 자동화 routine 없음. 사람이 `pulse/inbox/` 에 주간 채팅
export 를 떨군 뒤 Claude Code 세션에서 `.claude/prompts/pulse-digest.md`
의 절차를 한 번 실행합니다. 한 실행은 pillar별로 0~4 개 파일을
산출합니다 — 신호 없는 pillar 는 파일 생략입니다. 채팅 export 의 운영
가이드 (트러블슈팅·체크리스트 포함) 는
[`EXPORT_GUIDE.md`](EXPORT_GUIDE.md) 에 단일 출처로 모여
있습니다.

## 다른 산출물·컨텍스트와의 관계

- 입력: `pulse/inbox/<주간 export>` (사람이 떨군 원시 채팅) +
  `context/P{1..4}.md` (pillar 추출본).
- 출력 흐름: `pulse/YYYY-MM-DD-P#.md` 는 다음 `scouting/` 실행의
  **옵셔널 입력**입니다. 스카우트는 `pulse/*-P#.md` 의 가장 최근
  1 개만 읽고, 정적 `context/` 가 충돌 시 항상 승리하며, 파일이 없으면
  무시합니다.
- 다른 산출물과의 분리: 새 논문 탐색은 `scouting/`, 핀 묶음 서사는
  `synthesis/`, 한 편 심층은 `analysis/`. `pulse/` 는 어느 산출물도
  생산하지 않고, **scouting 의 retrieval bias** 로만 기능합니다.

## 절대 규칙

- `context/` 는 **절대 수정하지 않습니다**. 수렴이 보이면 힌트의
  💡 *Context Links* 섹션에만 기록하고, 다음 스카우트가 💡 컨텍스트 제안
  으로 사람에게 올립니다.
- 정적 `context/` 가 충돌 시 항상 승리한다는 규칙은 깨지지 않습니다 —
  pulse 는 nudge 이지 truth 가 아닙니다.
- 한글 단일 문서. 파일명 verbatim 토큰 `YYYY-MM-DD-P#.md` 로 중복
  제거·재조회.
- append 가 아니라 실행마다 **pillar별 새 파일**. 신호 없는 pillar 는
  파일 생략 가능 (덮어쓰지 않음).
- 폼은 `pulse/_TEMPLATE.md`, 디지스트 절차는
  `.claude/prompts/pulse-digest.md` 가 단일 출처입니다. 형식·이모지·
  용어는 `docs/STYLE_GUIDE.md` 의 분류를 따릅니다.
