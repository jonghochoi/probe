---
description: 해결된 논문 Q&A 이슈 스레드를 큐레이션해 analysis/<id>/qa.md 로 레포에 보존 (수동 트리거 — 자동 발화 없음)
argument-hint: <arXiv id> [--force]
---

- **실행** — `.claude/prompts/qa-sync.md` 를 읽고 그대로 실행. 이 파일이 유일한 정보 원천 (로직 복제·변경 금지).
- **인자** — `$ARGUMENTS` = 동기화할 논문의 arXiv id. 선택 플래그 `--force`(닫히지 않은/미해결 스레드도 강제 동기화).
- **빈 인자 시** — arXiv id 를 사용자에게 묻고 중단 (직접 선택 금지).
- **사전조건** — `analysis/<id>/analysis.md` 와 `probe-paper-qa:<id>` 마커를 가진 이슈가 존재해야 함. 없으면 중단하고 `/discuss-analysis <id>` 안내.
