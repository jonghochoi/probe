---
description: Layer 1 Design 을 target foundry (기본 vendor/lerobot) 좌표계로 매핑해 한글 구현 가이드(impl.md) + unified diff(impl.patch)를 생성
argument-hint: <design-path> [--foundry <name>] [--feedback <verify-path>]
---

- **실행** — `.claude/prompts/implementation.txt` 를 읽고 그대로 실행. 이 파일이 유일한 정보 원천 (로직 복제·변경 금지).
- **인자** — `$ARGUMENTS` = Design 경로 + 선택적 `--foundry <name>`(기본 `lerobot`).
- **빈 인자 시** — Design 경로(`analysis/<id>/design.md`)와 선택적 `--foundry` 를 사용자에게 묻고 중단 (직접 선택 금지).
- **사전조건** — Design 문서가 이미 존재해야 함. 없으면 중단하고 `/analyze-paper <id>` 를 먼저 실행하도록 안내.
