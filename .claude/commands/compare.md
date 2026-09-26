---
description: 재작성본이 이미 있는 논문 2–3편을 한 질문 아래 놓고 갈리는 자리만 쓰는 비교문(comparison/<slug>.md)을 생성
argument-hint: <arXiv id> <arXiv id> [<arXiv id>] [--refresh]
---

- **실행** — `.claude/prompts/compare.txt` 를 읽고 그대로 실행 (로직 복제·변경 금지).
- **출력 형식** — 프롬프트가 아니라 `comparison/AUTHORING.md` 가 정본. 쓰기 전에 §1–§4 를 읽는다.
- **인자** — `$ARGUMENTS` = 비교할 arXiv id 2–3개 (`--refresh` 는 기존 비교문 덮어쓰기). 준 순서가 표의 열 순서이자 카드 순서다.
- **빈 인자 시** — 아직 비교문이 없는 조합을 최대 3개, 그들을 **가르는 질문**과 함께 제안하고 중단 (절차는 프롬프트). 고르는 것은 사용자 몫이다.
