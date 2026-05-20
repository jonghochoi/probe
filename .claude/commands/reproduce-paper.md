---
description: 기존 analysis/<id>.md 를 입력으로 받아 vendor/lerobot baseline 대비 한글 구현 가이드(analysis/<id>_impl.md) + unified diff 패치(analysis/<id>_impl.patch)를 생성
argument-hint: <arXiv id | arXiv url | analysis slug>
---

Read `.claude/prompts/paper-reproduction.md` and execute it exactly as
written. That file is the single source of truth for this command —
do not duplicate or paraphrase its logic here.

The paper to reproduce is: $ARGUMENTS

If `$ARGUMENTS` is empty, ask the user for an arXiv id / URL or the slug
of an existing analysis and stop — do not pick a paper yourself.

Precondition: `analysis/<id>.md` must already exist. If it does not,
stop and instruct the user to run `/analyze-paper <id>` first.
