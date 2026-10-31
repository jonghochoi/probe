---
description: 바구니의 관심 논문들을 비공개 방법론·코드베이스와 맞대어 로컬에만 맞대기(versus/<id>--<alias>.md)·점수판(scoreboard.md)·회차 보고(reports/)를, 요청하면 논문 한 편과 코드 범위 하나를 깊게 맞댄 정밀 대조(deepdive/)를, 또는 재작성본 한 편으로 NotebookLM 이 그린 슬라이드·인포그래픽·오디오·마인드맵을 원문에 대조한 노트북 키트(notebook/)를 쓴다 (레포 커밋 없음)
argument-hint: [<arXiv id | alias> | --all | --audit | --deepdive <arXiv id | alias> <scope> | --notebook <arXiv id | alias> [<kinds>]]
---

- **실행** — `.claude/prompts/distinguish.txt` 를 읽고 그대로 실행 (로직 복제·변경 금지).
- **출력 형식** — 프롬프트가 아니라 `distinction/AUTHORING.md` 가 정본. 쓰기 전에 끝까지 읽는다.
- **어디서** — 코드베이스가 있는 **로컬 머신**에서만. `PROBE_PRIVATE_DIR` 이 비공개 폴더(`BASKET.md`·`MY-METHOD.md`·`code`)를 가리켜야 하고, 없으면 첫 단계에서 멈춘다. 폴더 준비는 `distinction/SETUP.md`.
- **인자** — `$ARGUMENTS` = 비어 있으면 **델타 모드**(지난 런 이후 바뀐 것에 걸린 논문만 다시 쓴다), 논문 하나(arXiv id 또는 alias)면 그 맞대기만, `--all` 이면 바구니 전부를 다시 쓴다. `--deepdive <논문> <범위>` 면 재작성본을 원문과 먼저 대조한 뒤 그 논문을 코드 범위 하나(`codemap.sh` 가 해석하는 이름)와 맞댄 정밀 대조 한 편만 쓴다 — 바구니에 없는 논문도 되고, 맞대기·점수판·회차 보고는 건드리지 않는다. `--notebook <논문> [<종류>]` 면 재작성본과 arXiv 원문만 NotebookLM 에 올려 종류(`slide-deck`·`infographic`·`audio`·`mind-map`, 쉼표로, 기본 `slide-deck`)를 그리고, 그린 쪽을 원문에 대조해 점검 노트를 남긴다 — 비공개 폴더의 다른 파일은 읽지도 올리지도 않는다. 맞대기·회차 보고·정밀 대조마다 옆에 읽기용 HTML 보기(`.html`)를 그린다.
- **쓰는 곳** — `$PROBE_PRIVATE_DIR` 아래 `versus/`·`scoreboard.md`·`reports/`·`deepdive/`·`notebook/` 만. 이 레포에는 파일도 커밋도 남기지 않는다.
