---
description: 논문 한 편을 분석 → foundry 매핑 → 정적 audit 의 반복 루프로 자동 수렴시켜 한글 분석 / Design / impl / audit 산출물 일체를 생성
argument-hint: <arXiv id | analysis/<id>/design.md> [--foundry <name>] [--max-rounds N]
---

`.claude/prompts/paper-reproduction.md`를 읽고 그대로 실행하세요. 해당 파일이 이 커맨드의 유일한 정보 원천입니다 — 로직을 여기에 복제하거나 바꿔 쓰지 마세요.

재현 대상(arXiv id 또는 design path)과 옵션들: $ARGUMENTS

`$ARGUMENTS`가 비어 있으면 arXiv id(또는 기존 `analysis/<id>/design.md` 경로)와 선택적 `--foundry <name>`(기본 `lerobot`) / `--max-rounds N`(기본 3)을 사용자에게 물어보고 중단하세요 — 직접 대상을 선택하지 마세요.

사전 조건: 입력이 design path인 경우 `analysis/<id>/analysis.md`와 `analysis/<id>/design.md`가 모두 존재해야 합니다. 없으면 중단하고 `/analyze-paper <id>`부터 실행하도록 안내하세요.
