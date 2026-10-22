---
description: 코퍼스에서 논문·주제와 연관된 재작성본을 찾고, 어느 한 편도 하지 않은 조합을 근거와 반증 실험까지 붙이고, 별도 에이전트가 원문으로 감사한 뒤 채팅과 답할 수 있는 비공개 페이지로 제안(레포 쓰기·커밋 없음)
argument-hint: [<arXiv id | alias | 주제>]
---

- **실행** — `.claude/prompts/ideate.txt` 를 읽고 그대로 실행 (로직 복제·변경 금지).
- **도구** — 모든 조회는 `python3 site/query.py` 로 한다. 설치 없이 표준 라이브러리만으로 돌고, 사이트의 `corpus.json` 과 같은 레코드를 읽는다. 본문 전체 대신 `section` 으로 필요한 절만 꺼낸다.
- **인자** — `$ARGUMENTS` = 논문 하나(arXiv id 또는 alias), 자유 주제, 또는 빈 값. 빈 값이면 `pairs --by contrast` 로 아직 누구도 엮지 않은 조합에서 출발한다.
- **출력** — 채팅에 한글로. 아이디어의 모양과 인용 형식은 프롬프트의 5단계가, 원문 감사는 6–7단계가, 페이지는 8단계와 `.claude/prompts/ideate-page.html` 이 정본이다.
- **쓰지 않는다** — 레포에는 파일도 커밋도 없다. 페이지는 레포 밖에서 `.claude/vendor/html-plan/pack.mjs` 로 묶어 비공개로 띄운다. 비교문이 필요한 쌍은 `/compare` 로 넘기고 멈춘다.
- **답변** — 페이지에서 붙여넣은 답변은 사람의 선택이자 데이터다. 프롬프트의 "WHEN THE PAGE'S RESPONSE COMES BACK" 절을 따라 처리한다.
