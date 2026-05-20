---
description: H### 의 가설·구현·패치를 문헌과 vendor 코드 정합성으로 검증해 V###.md 를 생성하고 통과 시 manifest 상태를 validated 로 격상
argument-hint: <H###>
---

Read `.claude/prompts/validate-hypothesis.md` and execute it exactly as
written. That file is the single source of truth for this command —
do not duplicate or paraphrase its logic here.

The hypothesis id is: $ARGUMENTS

If `$ARGUMENTS` is empty, ask the user for a hypothesis id (e.g. `H001`)
and stop — do not pick one yourself.

Precondition: `experiments/H###-*/{H###.md, I###.md, I###.patch,
manifest.yaml}` must all exist. If any is missing, stop and instruct
the user to complete the prior step (`/hypothesize` or
`/implement-hypothesis`) first.
