---
description: 재작성본이 이미 있는 논문 한 편을 발표 자료(presentation/<arxiv-id>.md)로 다시 짜고, 슬라이드마다 발표 에세이를 붙인다
argument-hint: <arXiv id> [--refresh]
---

- **실행** — `.claude/prompts/present.txt` 를 읽고 그대로 실행 (로직 복제·변경 금지).
- **출력 형식** — 프롬프트가 아니라 `presentation/AUTHORING.md` 가 정본. 쓰기 전에 §1–§7 을 읽는다.
- **인자** — `$ARGUMENTS` = 논문 arXiv id 하나 (`--refresh` 는 기존 발표 자료 덮어쓰기).
- **빈 인자 시** — 발표 자료가 없는 재작성본 중 발표로 값을 할 만한 것을 최대 3개, 각각 **그 발표가 남길 한 문장**과 함께 제안하고 중단. 고르는 것은 사용자 몫이다.
