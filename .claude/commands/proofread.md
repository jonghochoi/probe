---
description: 기존 재작성본(analysis/<arxiv-id>.md)을 원문과 공개 코드에 다시 대조해 /loop 로 최소 N회(기본 5) 교정
argument-hint: [<arXiv id | alias>] [--rounds N]
---

- **실행** — `loop` 스킬을 Skill 도구로 **간격 없이**(자율 페이스) 호출한다. 넘길 루프 프롬프트는 한 줄: `.claude/prompts/proofread.txt 를 읽고 analysis/<id>.md 에 교정 한 회차를 그대로 실행 (최소 <N>회)`. 회차 절차·렌즈·종료 조건은 프롬프트가 정본이다 (로직 복제·변경 금지).
- **출력 형식** — 고치는 문장마다 `analysis/AUTHORING.md` 가 정본.
- **인자** — `$ARGUMENTS` = 재작성본 하나(arXiv id 또는 alias — alias 는 `python3 site/query.py show <alias>` 로 id 를 얻는다), `--rounds N` 은 최소 회차(기본 5).
- **빈 인자 시** — 이 세션에서 쓰거나 고친 재작성본이 `analysis/` 에 정확히 하나면 그것, 아니면 어느 재작성본인지 묻고 중단 (직접 선택 금지).
