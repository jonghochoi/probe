---
description: 분석 완료된 논문(analysis/<id>/analysis.md)을 한 편당 GitHub Issue 하나로 논의 개설/갱신 — 동료 Q&A 용 (paper-qa 라벨, @claude 멘션으로 답변)
argument-hint: <arXiv id> [--dry-run] [--reopen]
---

- **실행** — `.claude/prompts/discussion.md` 를 읽고 그대로 실행. 이 파일이 유일한 정보 원천 (로직 복제·변경 금지).
- **인자** — `$ARGUMENTS` = 논의를 개설할 논문의 arXiv id. 선택 플래그 `--dry-run`(쓰기 없이 본문·경로만 출력), `--reopen`(닫힌 이슈를 다시 열어 갱신).
- **빈 인자 시** — arXiv id 를 사용자에게 묻고 중단 (직접 선택 금지).
- **사전조건** — `analysis/<id>/analysis.md` 가 존재해야 함. 없으면 중단하고 `/analyze-paper <id>` 를 먼저 실행하도록 안내.
