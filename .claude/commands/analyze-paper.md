---
description: arXiv id / URL 또는 PDF URL 한 편을 심층 분석해 한글 분석 문서(analysis/<id>.md) + Layer 1 Design 문서(analysis/<id>_design.md)를 생성
argument-hint: <arXiv id | arXiv url | pdf url>
---

Read `.claude/prompts/paper-analysis.md` and execute it exactly as
written. That file is the single source of truth for this command —
do not duplicate or paraphrase its logic here.

The paper to analyze is: $ARGUMENTS

If `$ARGUMENTS` is empty, ask the user for an arXiv id / URL or a PDF
URL and stop — do not pick a paper yourself.
