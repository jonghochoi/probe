---
description: arXiv id / URL 또는 PDF URL 한 편을 심층 분석해 한글 분석 문서(analysis/<id>/analysis.md) + Layer 1 Design 문서(analysis/<id>/design.md)를 생성
argument-hint: <arXiv id | arXiv url | pdf url> [fast|standard|strict]
---

- **실행** — `.claude/prompts/analysis.md` 를 읽고 그대로 실행. 이 파일이 유일한 정보 원천 (로직 복제·변경 금지).
- **인자** — `$ARGUMENTS` = 분석할 논문.
- **모드 토큰** — 마지막 토큰이 `fast`/`standard`/`strict` 면 humanize 윤문 모드, 나머지를 논문 식별자로 전달. 없으면 기본 `standard`. 파싱 정본은 analysis.md(INPUT 섹션) — 여기 재기술 금지.
- **빈 인자 시** — arXiv id / URL 또는 PDF URL 을 사용자에게 묻고 중단 (직접 선택 금지).
