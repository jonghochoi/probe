---
description: Layer 1 Design 을 target foundry (기본 vendor/lerobot) 좌표계로 매핑해 한글 구현 가이드(impl.md) + unified diff(impl.patch)를 생성
argument-hint: <design-path> [--foundry <name>] [--feedback <verify-path>]
---

`.claude/prompts/foundry.md`를 읽고 그대로 실행하세요. 해당 파일이 이 커맨드의 유일한 정보 원천입니다 — 로직을 여기에 복제하거나 바꿔 쓰지 마세요.

Design 경로와 선택적 foundry 플래그: $ARGUMENTS

`$ARGUMENTS`가 비어 있으면 사용자에게 Design 경로(`analysis/<id>/design.md`)와 선택적 `--foundry <name>`(기본 `lerobot`)을 물어보고 중단하세요 — 직접 선택하지 마세요.

사전 조건: Design 문서가 이미 존재해야 합니다. 없으면 중단하고 `/analyze-paper <id>`를 먼저 실행하도록 안내하세요.
