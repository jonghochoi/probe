---
description: arXiv id / URL 또는 PDF URL 한 편을 심층 분석해 한글 분석 문서(analysis/<id>/analysis.md) + Layer 1 Design 문서(analysis/<id>/design.md)를 생성
argument-hint: <arXiv id | arXiv url | pdf url>
---

- **실행** — `.claude/prompts/analysis.txt` 를 읽고 그대로 실행. 이 파일이 유일한 정보 원천 (로직 복제·변경 금지).
- **인자** — `$ARGUMENTS` = 분석할 논문.
- **빈 인자 시** — arXiv id / URL 또는 PDF URL 을 사용자에게 묻고 중단 (직접 선택 금지).
