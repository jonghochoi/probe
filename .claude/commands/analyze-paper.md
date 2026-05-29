---
description: arXiv id / URL 또는 PDF URL 한 편을 심층 분석해 한글 분석 문서(analysis/<id>/analysis.md) + Layer 1 Design 문서(analysis/<id>/design.md)를 생성
argument-hint: <arXiv id | arXiv url | pdf url> [fast|standard|strict]
---

`.claude/prompts/analysis.md`를 읽고 그대로 실행하세요. 해당 파일이 이 커맨드의 유일한 정보 원천입니다 — 로직을 여기에 복제하거나 바꿔 쓰지 마세요.

분석할 논문: $ARGUMENTS

`$ARGUMENTS`의 마지막 토큰이 `fast`/`standard`/`strict` 중 하나면 humanize 윤문 모드로 해석하고 나머지를 논문 식별자로 넘기세요. 모드 토큰이 없으면 기본값 standard 입니다. 파싱 규칙의 정본은 analysis.md(INPUT 섹션)이며 여기에 다시 쓰지 마세요.

`$ARGUMENTS`(모드 토큰 제외)가 비어 있으면 사용자에게 arXiv id / URL 또는 PDF URL을 물어보고 중단하세요 — 논문을 직접 선택하지 마세요.
