---
description: 기존 experiments/H###-*/H###.md 를 입력으로 vendor/lerobot baseline 대비 한글 구현 가이드(I###.md) + unified diff(I###.patch)를 생성
argument-hint: <H###>
---

Read `.claude/prompts/implement-hypothesis.md` and execute it exactly as
written. That file is the single source of truth for this command —
do not duplicate or paraphrase its logic here.

The hypothesis id is: $ARGUMENTS

If `$ARGUMENTS` is empty, ask the user for a hypothesis id (e.g. `H001`)
and stop — do not pick one yourself.

Precondition: `experiments/H###-*/H###.md` and its `manifest.yaml` must
already exist. If they do not, stop and instruct the user to run
`/hypothesize` first.
