---
description: 입력(P# 또는 analysis/<id>)에서 falsifiable 가설을 도출해 experiments/H###-<slug>/ 에 단일 한글 문서 + manifest 를 생성
argument-hint: <P# | analysis-slug> [slug]
---

Read `.claude/prompts/hypothesize.md` and execute it exactly as
written. That file is the single source of truth for this command —
do not duplicate or paraphrase its logic here.

The hypothesis seed is: $ARGUMENTS

If `$ARGUMENTS` is empty, ask the user for `P1`/`P2`/`P3`/`P4` or an
existing `analysis/<id>` slug and stop — do not pick a seed yourself.
