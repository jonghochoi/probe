---
description: arXiv id / URL 또는 PDF URL 한 편을 심층 분석해 한글 분석 문서(analysis/<id>/analysis.md) + Layer 1 Design 문서(analysis/<id>/design.md)를 생성
argument-hint: <arXiv id | arXiv url | pdf url> [--deep]
---

- **실행** — `.claude/prompts/analysis.md` 를 읽고 그대로 실행. 이 파일이 유일한 정보 원천 (로직 복제·변경 금지).
- **인자** — `$ARGUMENTS` = 분석할 논문.
- **`--deep`** — 세밀 분석 모드. 기본 `analysis.md`/`design.md` 는 그대로 두고 `analysis.deep.md`/`design.deep.md` 를 별도로 생성해 두 상세도를 병존·비교 (상세 동작은 `analysis.md` 프롬프트 참조).
- **빈 인자 시** — arXiv id / URL 또는 PDF URL 을 사용자에게 묻고 중단 (직접 선택 금지).
