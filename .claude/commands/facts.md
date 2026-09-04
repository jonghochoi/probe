---
description: 이미 있는 재작성본(analysis/<arxiv-id>.md)에 arXiv 원문에서 읽은 사실 카드(probe-facts) 한 블록만 채워 넣는다
argument-hint: <arXiv id>
---

- **실행** — `.claude/prompts/facts.txt` 를 읽고 그대로 실행 (로직 복제·변경 금지).
- **출력 형식** — 프롬프트가 아니라 `analysis/AUTHORING.md` R16(§2-14) 이 정본. 쓰기 전에 읽는다.
- **인자** — `$ARGUMENTS` = 사실 카드를 채울 논문의 arXiv id 한 개.
- **빈 인자 시** — arXiv id 를 사용자에게 묻고 중단 (직접 선택 금지). 아직 카드가 없는 재작성본 목록은 프롬프트의 첫 단계가 출력한다.
- **`analysis/<id>.md` 가 없으면 중단** — `/analyze <id>` 로 재작성본을 먼저 쓰라고 안내. 이 명령은 이미 있는 파일의 한 부분만 채운다.
- **출처는 arXiv 원문 하나** — 재작성본의 문장에서 값을 옮기지 않는다. 판(版)은 front matter 의 `arxiv_html:` 이 기록한 그것.
- **파일에서 바뀌는 줄은 그 블록뿐** — `git diff` 에 추가된 hunk 하나. 본문·요약·front matter 는 건드리지 않는다.
