---
description: Design + foundry patch 를 문헌 / vendor 코드 정합성으로 정적 검증해 보고서를 생성
argument-hint: <design-path> [--foundry <name>]
---

- **실행** — `.claude/prompts/validation.txt` 를 읽고 그대로 실행. 이 파일이 유일한 정보 원천 (로직 복제·변경 금지).
- **인자** — `$ARGUMENTS` = Design 경로 + 선택적 `--foundry <name>`(기본 `lerobot`).
- **빈 인자 시** — Design 경로(`analysis/<id>/design.md`)와 선택적 `--foundry` 를 사용자에게 묻고 중단 (직접 선택 금지).
- **사전조건** — `analysis/<id>/design.md`, `analysis/<id>/analysis.md`, 매칭 foundry impl(`impl/<foundry>/impl.md` + `impl.patch`)이 모두 존재해야 함. 하나라도 없으면 중단하고 이전 단계(`/analyze-paper` 또는 `/implement-design`)를 먼저 완료하도록 안내.
