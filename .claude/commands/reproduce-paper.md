---
description: 논문 한 편을 분석 → foundry 매핑 → 정적 audit 의 반복 루프로 자동 수렴시켜 한글 분석 / Design / impl / audit 산출물 일체를 생성
argument-hint: <arXiv id | analysis/<id>_design.md> [--foundry <name>] [--max-rounds N]
---

Read `.claude/prompts/paper-reproduction.md` and execute it exactly as
written. That file is the single source of truth for this command —
do not duplicate or paraphrase its logic here.

The reproduction target (arXiv id 또는 design path) 와 옵션들은: $ARGUMENTS

If `$ARGUMENTS` is empty, ask the user for an arXiv id (또는 기존
`analysis/<id>_design.md` 경로) 와 optional `--foundry <name>` (기본
`lerobot`) / `--max-rounds N` (기본 3) 을 묻고 stop — do not pick a
target yourself.

Precondition: 입력이 design path 인 경우 `analysis/<id>.md` 와
`analysis/<id>_design.md` 가 모두 존재해야 합니다. 부재 시 stop 하고
`/analyze-paper <id>` 부터 돌리도록 안내하세요.
