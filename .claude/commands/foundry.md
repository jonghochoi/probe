---
description: Layer 1 Design 을 target foundry (기본 vendor/lerobot) 좌표계로 매핑해 한글 구현 가이드(impl.md) + unified diff(impl.patch)를 생성
argument-hint: <design-path> [--foundry <name>]
---

Read `.claude/prompts/foundry.md` and execute it exactly as written.
That file is the single source of truth for this command — do not
duplicate or paraphrase its logic here.

The Design path and optional foundry flag are: $ARGUMENTS

If `$ARGUMENTS` is empty, ask the user for a Design path
(`analysis/<id>_design.md`) and optional `--foundry <name>` (기본
`lerobot`) and stop — do not pick one yourself.

Precondition: the Design document must already exist. If it does not,
stop and instruct the user to run `/distill <id>` first.
