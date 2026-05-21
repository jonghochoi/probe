---
description: Design + foundry patch 를 문헌 / vendor 코드 정합성으로 정적 검증해 보고서를 생성하고, 가설 트랙에서는 모든 foundry 통과 시 manifest 상태를 validated 로 격상
argument-hint: <design-path> [--foundry <name>]
---

Read `.claude/prompts/verify.md` and execute it exactly as written.
That file is the single source of truth for this command — do not
duplicate or paraphrase its logic here.

The Design path and optional foundry flag are: $ARGUMENTS

If `$ARGUMENTS` is empty, ask the user for a Design path
(`analysis/<id>_design.md` 또는 `experiments/H###-*/D###.md`) and
optional `--foundry <name>` (기본 `lerobot`) and stop — do not pick
one yourself.

Precondition: the Design document, the originating source
(`analysis/<id>.md` 또는 `H###.md`), and the matching foundry impl
(`<impl-root>/<foundry>/impl.md` + `impl.patch`) must all exist. If
any is missing, stop and instruct the user to complete the prior step
(`/analyze-paper`, `/hypothesize`, or `/foundry`) first.
