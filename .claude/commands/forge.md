---
description: distill → foundry → temper 루프를 한 번 순회 — 입력 위치에 따라 시작 단계가 결정되며, 단계 실패 시 즉시 중단
argument-hint: <arXiv id | arXiv url | pdf url | analysis/<id>.md | analysis/<id>_design.md> [--foundry <name>]
---

Read `.claude/prompts/forge.md` and execute it exactly as written.
That file is the single source of truth for this command — do not
duplicate or paraphrase its logic here.

The starting point and optional foundry flag are: $ARGUMENTS

If `$ARGUMENTS` is empty, ask the user for one of:

  - an arXiv id / URL / PDF URL          (start from `/distill`)
  - `analysis/<id>.md`                    (re-run `/distill` to refresh Design, then proceed)
  - `analysis/<id>_design.md`             (start from `/foundry`)

and optional `--foundry <name>` (기본 `lerobot`), and stop — do not
pick one yourself.
