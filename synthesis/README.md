# synthesis/

주간 스카우팅(`scouting/`) · 온디맨드 심층분석(`analysis/`)과 **분리된**
산출물 경로입니다. 새 논문을 찾는 곳도, 한 편을 깊게 파는 곳도 아닙니다.
이미 핀된 논문들 사이의 **핵심 연결고리를 서사로 압축**해 사람이 P#
아키텍처를 머릿속에 계속 들고 다닐 수 있게 하는 곳입니다.

| 파일 | 생성 주체 | 성격 |
|---|---|---|
| `P1_BRIEF.md` | `probe-p1-synthesis` Routine (월 1회) | `context/P1.md` §4(D1–D7) + §6(핀 논문)만 읽고 재생성 |
| `P2_BRIEF.md` | `probe-p2-synthesis` Routine (월 1회) | `context/P2.md` §4(D8–D12) + §6 |
| `P3_BRIEF.md` | `probe-p3-synthesis` Routine (월 1회) | `context/P3.md` §4(D13–D18) + §6 |
| `P4_BRIEF.md` | `probe-p4-synthesis` Routine (월 1회) | `context/P4.md` §4(D19–D23) + §6 |

## 호출

`probe-p#-synthesis` 는 [claude.ai/code/routines](https://claude.ai/code/routines)
의 RemoteTrigger 루틴입니다 (프롬프트: `.claude/prompts/synthesis-P#.md`,
pillar별 1개). 한 실행은 한 pillar 만 처리하며 결과는 `P#_BRIEF.md`
하나를 갈아끼웁니다. §6 핀이 바뀌면 월간 실행을 기다리지 말고 루틴 상세
페이지의 **Run now** 로 즉시 재생성합니다. 자세한 설정은 루트
`README.md` → Stage 3 Bonus 참조.

## 다른 산출물·컨텍스트와의 관계

- 입력: `context/P#.md` §4(Decision Log) + §6(핀 논문) — 그 외에 외부
  검색·MCP·`curl` 호출이 일절 없어 인용 조작 위험이 원천적으로
  차단됩니다.
- 다른 PROBE 산출물과의 분리: 새 논문 탐색은 `scouting/`, 한 편 심층은
  `analysis/`, 핀 묶음의 서사 압축만 `synthesis/`. `scouting/` 리포트
  · `analysis/` 산출물의 직접 참조는 하지 않습니다 (서사 압축의 입력은
  핀된 `context/` 만).
- 출력 흐름: 같은 `P#_BRIEF.md` 가 살아 있는 single source 가 되어
  사람이 P# 아키텍처를 빠르게 다시 잡을 때 읽는 한 페이지 역할을
  합니다.

## 절대 규칙

- `context/` 는 **절대 수정하지 않습니다**. 핀/Decision 변경 제안은
  브리프의 💡 컨텍스트 제안 섹션에만 적습니다.
- 한글 단일 문서 (영문 1차 파일 없음). 파일명에 날짜 토큰 없음 — 풀이
  바뀌면 같은 파일을 갈아끼웁니다.
- append 가 아니라 매번 **덮어쓰는** living snapshot.
- 형식·이모지·용어·링크 규칙은 `docs/STYLE.md` 를 정확히
  따릅니다.
