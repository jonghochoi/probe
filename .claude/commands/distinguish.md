---
description: 바구니의 관심 논문들을 비공개 방법론·코드베이스와 맞대어 로컬에만 차별화 장부(ledger/<id>.md)·매트릭스·델타를 쓴다 (레포 커밋 없음)
argument-hint: [<arXiv id | alias> | --all]
---

- **실행** — `.claude/prompts/distinguish.txt` 를 읽고 그대로 실행 (로직 복제·변경 금지).
- **출력 형식** — 프롬프트가 아니라 `distinction/AUTHORING.md` 가 정본. 쓰기 전에 §1–§8 을 읽는다.
- **어디서** — 코드베이스가 있는 **로컬 머신**에서만. `PROBE_PRIVATE_DIR` 이 비공개 폴더(`BASKET.md`·`METHOD.md`·`code`)를 가리켜야 하고, 없으면 첫 단계에서 멈춘다. 폴더 준비는 `distinction/SETUP.md`.
- **인자** — `$ARGUMENTS` = 비어 있으면 **델타 모드**(지난 런 이후 바뀐 것에 걸린 논문만 다시 쓴다), 논문 하나(arXiv id 또는 alias)면 그 장부만, `--all` 이면 바구니 전부를 다시 쓴다.
- **쓰는 곳** — `$PROBE_PRIVATE_DIR` 아래 `ledger/`·`matrix.md`·`runs/` 만. 이 레포에는 파일도 커밋도 남기지 않는다.
