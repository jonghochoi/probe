---
description: Design + foundry patch 를 문헌 / vendor 코드 정합성으로 정적 검증해 보고서를 생성
argument-hint: <design-path> [--foundry <name>]
---

`.claude/prompts/audit.md`를 읽고 그대로 실행하세요. 해당 파일이 이 커맨드의 유일한 정보 원천입니다 — 로직을 여기에 복제하거나 바꿔 쓰지 마세요.

Design 경로와 선택적 foundry 플래그: $ARGUMENTS

`$ARGUMENTS`가 비어 있으면 사용자에게 Design 경로(`analysis/<id>_design.md`)와 선택적 `--foundry <name>`(기본 `lerobot`)을 물어보고 중단하세요 — 직접 선택하지 마세요.

사전 조건: Design 문서, 원본 분석 문서(`analysis/<id>.md`), 그리고 매칭되는 foundry impl(`analysis/<id>_impl/<foundry>/impl.md` + `impl.patch`)이 모두 존재해야 합니다. 하나라도 없으면 중단하고 이전 단계(`/analyze-paper` 또는 `/foundry`)를 먼저 완료하도록 안내하세요.
