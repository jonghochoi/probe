---
description: 재작성본 한 편을 NotebookLM 으로 슬라이드·인포그래픽·오디오·마인드맵으로 각색하고, 그린 쪽을 원문에 대조해 점검 노트를 붙여 레포 밖 폴더(<id>--<alias>/)에 남긴다 (레포 쓰기·커밋 없음)
argument-hint: <arXiv id | alias> [slide-deck,infographic,audio,mind-map]
---

- **실행** — `.claude/prompts/adapt.txt` 를 읽고 그대로 실행 (로직 복제·변경 금지).
- **출력 형식** — 프롬프트가 아니라 `adaptation/AUTHORING.md` 가 정본. 쓰기 전에 끝까지 읽는다.
- **어디서** — 브라우저로 NotebookLM 에 로그인한 **로컬 머신**에서만. `PROBE_ADAPT_DIR` 이 레포 밖 폴더를 가리켜야 하고, 없거나 로그인이 안 됐으면 첫 단계에서 멈춘다. 준비는 `adaptation/SETUP.md`.
- **인자** — `$ARGUMENTS` = 논문 하나(arXiv id 또는 alias)와, 쉼표로 이은 종류(`slide-deck`·`infographic`·`audio`·`mind-map`). 종류가 없으면 `slide-deck`.
- **보내는 것** — 재작성본, arXiv 원문, lint 를 통과한 `brief.md` 만. 비공개 폴더(`PROBE_PRIVATE_DIR`)는 읽지도 올리지도 않는다.
- **쓰는 곳** — `$PROBE_ADAPT_DIR/<id>--<alias>/` 만. 이 레포에는 파일도 커밋도 남기지 않는다.
- **빈 인자 시** — 어느 논문인지 묻고 중단 (직접 선택 금지).
