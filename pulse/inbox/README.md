# inbox/

원시 채팅 export 를 여기에 떨어뜨리세요. 이 README 를 제외한 모든 파일은
**gitignored** 입니다 — 팀 채팅은 private 으로 간주합니다.

## 파일명 규칙

```
YYYY-WXX_<source>.<ext>
```

예:
- `2026-W17_slack-dexterous.txt`
- `2026-W17_telegram-research.json`
- `2026-W17_slack-dexterous.zip` (multi-channel export 압축)

## 지원 포맷

`.claude/prompts/pulse-digest.md` 는 speaker 와 timestamp 를 기대하지만 특정
포맷을 가정하지 않습니다. 다음 모두 동작합니다:

- Slack channel export (txt 또는 JSON)
- Telegram chat export (HTML 또는 JSON)
- Plain markdown / text (한 줄 하나의 메시지)
- speaker 가 보이는 채팅 복사-붙여넣기

timestamp 나 speaker 가 빠지면 디지스트 confidence 는 `low` 로 cap 됩니다.
이는 정상 동작입니다 — 메타데이터를 지어내지 않습니다.

## Do not

- 트랜스크립트를 repo 에 commit (gitignore 가 처리; override 금지).
- 디지스트 후 트랜스크립트를 `inbox/` 밖으로 이동. 커밋 산출물은
  `pulse/YYYY-MM-DD-P#.md` 만이고, 원시 소스는 여기에 남아 리뷰 후 로컬에서
  삭제 가능합니다.
- 한 파일에 1주 이상의 window 를 붙이기 — 1파일 = 1주가 디지스트의 window
  추론을 안정적으로 유지합니다.
