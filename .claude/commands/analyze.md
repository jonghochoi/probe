---
description: 논문 한 편의 arXiv 원문을 읽어 사이트에 발행되는 한글 재작성본(analysis/<arxiv-id>.md)을 생성
argument-hint: <arXiv id> [--refresh]
---

- **실행** — `.claude/prompts/analyze.txt` 를 읽고 그대로 실행 (로직 복제·변경 금지).
- **출력 형식** — 프롬프트가 아니라 `analysis/AUTHORING.md` 가 정본. 쓰기 전에 §1–§5 를 읽는다.
- **인자** — `$ARGUMENTS` = 재작성할 논문의 arXiv id (`--refresh` 는 기존 재작성본 덮어쓰기).
- **빈 인자 시** — arXiv id 를 사용자에게 묻고 중단 (직접 선택 금지).
