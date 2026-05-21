---
description: Design + foundry 패치를 문헌·vendor 코드 정합성으로 단련해 한글 temper 보고서를 생성 — forge 루프의 3단계
argument-hint: <design-path> [--foundry <name>]
---

Read `.claude/prompts/temper.md` and execute it exactly as written.
That file is the single source of truth for this command — do not
duplicate or paraphrase its logic here.

The Design path and optional foundry flag are: $ARGUMENTS

If `$ARGUMENTS` is empty, ask the user for a Design path
(`analysis/<id>_design.md`) and optional `--foundry <name>` (기본
`lerobot`) and stop — do not pick one yourself.

Precondition: the Design document, the originating analysis
(`analysis/<id>.md`), and the matching foundry impl
(`analysis/<id>_impl/<foundry>/impl.md` + `impl.patch`) must all
exist. If any is missing, stop and instruct the user to complete the
prior step (`/distill` or `/foundry`) first.
