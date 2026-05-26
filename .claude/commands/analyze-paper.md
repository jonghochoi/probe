---
description: arXiv id / URL 또는 PDF URL 한 편을 심층 분석해 한글 분석 문서(analysis/<id>/analysis.md) + Layer 1 Design 문서(analysis/<id>/design.md)를 생성
argument-hint: <arXiv id | arXiv url | pdf url>
---

`.claude/prompts/paper-analysis.md`를 읽고 그대로 실행하세요. 해당 파일이 이 커맨드의 유일한 정보 원천입니다 — 로직을 여기에 복제하거나 바꿔 쓰지 마세요.

분석할 논문: $ARGUMENTS

`$ARGUMENTS`가 비어 있으면 사용자에게 arXiv id / URL 또는 PDF URL을 물어보고 중단하세요 — 논문을 직접 선택하지 마세요.
