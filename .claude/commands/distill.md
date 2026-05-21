---
description: arXiv id / URL 또는 PDF URL 한 편에서 정수를 증류해 한글 분석 문서(analysis/<id>.md) + Layer 1 Design 문서(analysis/<id>_design.md)를 생성 — forge 루프의 1단계
argument-hint: <arXiv id | arXiv url | pdf url>
---

Read `.claude/prompts/distill.md` and execute it exactly as written.
That file is the single source of truth for this command — do not
duplicate or paraphrase its logic here.

The paper to distill is: $ARGUMENTS

If `$ARGUMENTS` is empty, ask the user for an arXiv id / URL or a PDF
URL and stop — do not pick a paper yourself.
