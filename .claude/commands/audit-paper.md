---
description: 논문이 주장한 method/defaults/metric 이 논문 자체 공식 repo 와 일치하는지 검사해 한글 재현 게이트 보고서(analysis/<id>/audit.md)를 생성 — /reproduce-paper 투자 전 게이트
argument-hint: <arXiv id | arXiv url | pdf url> [--repo <url>]
---

- **실행** — `.claude/prompts/audit.txt` 를 읽고 그대로 실행. 이 파일이 유일한 정보 원천 (로직 복제·변경 금지).
- **인자** — `$ARGUMENTS` = 감사할 논문 + 선택적 `--repo <url>`.
- **빈 인자 시** — arXiv id / URL 또는 PDF URL 을 사용자에게 묻고 중단 (직접 선택 금지).
- **구분** — `/validate-impl`(PROBE Design+patch ↔ foundry)과 다름. 이건 *논문 주장 ↔ 논문 자체 공식 코드*를 본다.
- **정직성** — 공식 코드를 못 찾거나 가져올 수 없으면 `🚫 audit 불가`로 보고. 가짜 pass 금지.
