---
description: 논문 한 편을 분석 → foundry 매핑 → 정적 validation 의 반복 루프로 자동 수렴시켜 한글 분석 / Design / impl / validation 산출물 일체를 생성
argument-hint: <arXiv id | analysis/<id>/design.md> [--foundry <name>] [--max-rounds N]
---

- **실행** — `.claude/prompts/reproduction.md` 를 읽고 그대로 실행. 이 파일이 유일한 정보 원천 (로직 복제·변경 금지).
- **인자** — `$ARGUMENTS` = 재현 대상(arXiv id 또는 design path) + 옵션.
- **빈 인자 시** — arXiv id(또는 기존 `analysis/<id>/design.md` 경로)와 선택적 `--foundry <name>`(기본 `lerobot`) / `--max-rounds N`(기본 3)을 사용자에게 묻고 중단 (직접 선택 금지).
- **사전조건** — 입력이 design path 면 `analysis/<id>/analysis.md` 와 `analysis/<id>/design.md` 가 모두 존재해야 함. 없으면 중단하고 `/analyze-paper <id>` 부터 실행하도록 안내.
