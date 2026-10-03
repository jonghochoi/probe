---
description: 지정한 필라들을 한 회차로 스카우팅해 필라별 리포트(scouting/P#/<날짜>.md)와 회차 파일(scouting/runs/<날짜>.md)을 커밋 하나로 남긴다
argument-hint: [필라 번호 … 예: 0 1 2 3 4]
---

- **실행** — `.claude/prompts/scouting.txt` 를 읽고 PART I(마스터)로 그대로 실행 (로직 복제·변경 금지).
- **출력 형식** — 프롬프트가 아니라 `scouting/AUTHORING.md` 가 정본. 쓰기 전에 끝까지 읽는다.
- **인자** — `$ARGUMENTS` = 이번 회차에 돌릴 필라 번호 (`0 1 2 3 4`, `1 3`, `P1 P3`).
- **빈 인자 시** — `context/P#.md` 가 있는 모든 필라를 돌린다.
