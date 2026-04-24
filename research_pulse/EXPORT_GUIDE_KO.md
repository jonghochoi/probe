# Pulse Export Guide (Slack & Telegram)

> **Scope:** 주 1회, 수동 기반 export 를 `research_pulse/inbox/` 로 떨어뜨리는 플로우.
> **Non-scope:** live 봇 연동, 실시간 mirroring, workspace 전체 mirror.
> PoC 기간 동안에는 *의도적으로* 수동을 유지한다 — 자동화 부담보다 human review step 의 안전망이 더 중요하다.

---

## 0. 먼저 결정할 것 3가지

| 질문 | 권장 기본값 |
|---|---|
| 어떤 채널을 대상으로? | **연구 전용 채널 1개만.** 잡담/공지 섞인 채널은 noise 가 너무 크다. |
| 어느 범위로 자를까? | **최근 7일.** ISO 주 기준 월~일 또는 수~화 중 팀 리듬에 맞는 쪽. |
| 어떤 포맷으로 받을까? | **JSON 우선, HTML 차선, plain text 최후.** JSON 이면 타임스탬프·speaker 가 구조화되어 있어 digest confidence 가 올라간다. |

위 3개가 확정되면 아래 export 절차 중 본인 환경에 맞는 하나를 고르면 된다.

---

## 1. 공통 주의사항

**Privacy first.**
- Raw transcript 는 `research_pulse/inbox/` 에만 둔다. 이 경로는 `.gitignore` 로 제외되어 있다.
- 절대 `research_pulse/YYYY-WXX.md` (hint 파일) 에 transcript 전문을 붙이지 않는다. Digest 프롬프트가 이미 quote 5개 이하·200자 이하로 제한한다.
- 외부에 민감한 내용(급여·인사·벤더 협상 등)이 섞인 주가 있다면 해당 주는 건너뛰거나, export 직후 수동 redact 후 digest 한다.

**파일명 규칙** (`research_pulse/inbox/_README.md` 와 동일):

```
YYYY-WXX_<source>.<ext>
```

예: `2026-W17_slack-dexterous.json`, `2026-W17_telegram-research.html`

**익명화가 필요하면** digest 프롬프트에 "speaker 이름을 A/B/C 로 익명화" 를 한 줄 추가하면 된다. 기본 digest 프롬프트는 이름을 보존한다.

---

## 2. Slack export

Slack 은 권한 상황에 따라 세 가지 경로가 있다. **상황에 맞는 하나만** 선택하면 된다.

### 2-A. Workspace Admin export (가장 깔끔, admin 권한 필요)

팀에서 Workspace Owner 혹은 Admin 이 지정되어 있고, 그 권한을 쓸 수 있는 경우.

1. Slack 웹 → `Settings & administration` → `Workspace settings` → `Import/Export Data` → `Export` 탭.
2. Date range 를 직전 주로 좁힌다 (Public channel 만 포함되므로, 연구 채널이 Public 이어야 한다).
3. Export 요청 → 완료되면 메일로 zip 링크가 온다.
4. zip 을 풀면 `<channel-name>/YYYY-MM-DD.json` 형태. 해당 주 JSON 을 합쳐서
   `research_pulse/inbox/2026-WXX_slack-<channel>.json` 으로 복사.

**한계**
- Private channel / DM 은 Plus 이상 요금제 + 추가 Workspace Discovery 권한이 있어야 포함된다.
- 채널이 Private 이면 2-B 또는 2-C 로.

### 2-B. slackdump (권장 — admin 없이 본인이 속한 채널만)

본인이 채널 멤버라면 admin 권한 없이 export 할 수 있다. 오픈소스 CLI:
<https://github.com/rusq/slackdump>.

**설치 & 인증 요약**
1. `go install github.com/rusq/slackdump/v3/cmd/slackdump@latest` (또는 릴리즈 바이너리 다운로드).
2. Slack 을 로그인된 브라우저에서 `xoxc-` 토큰과 `xoxd-` 쿠키를 추출한다 (slackdump README 의 `Authentication` 섹션 절차를 따른다 — 주기적으로 포맷이 바뀌므로 upstream 문서가 단일 출처).
3. 한 번 인증하면 환경변수/파일로 재사용 가능.

**주간 덤프 명령 (예시)**

```bash
# 채널 ID 는 Slack UI 에서 채널명 우클릭 → "Copy link" → 끝의 C... 문자열
CHANNEL_ID=C0XXXXXXXX
WEEK=2026-W17
FROM=2026-04-20   # 월
TO=2026-04-27     # 다음 주 월 (배타적)

slackdump export \
  -o "research_pulse/inbox/${WEEK}_slack-dexterous" \
  -time-from "${FROM}T00:00:00" \
  -time-to   "${TO}T00:00:00" \
  "${CHANNEL_ID}"
```

결과는 디렉토리 형태로 나오는데, digest 프롬프트는 단일 파일을 기대하므로 다음 중 하나로 정리:

```bash
# 옵션 1: 디렉토리를 zip 으로 묶기
cd research_pulse/inbox && zip -r "${WEEK}_slack-dexterous.zip" "${WEEK}_slack-dexterous"/ && rm -rf "${WEEK}_slack-dexterous"

# 옵션 2: 메시지 JSON 만 하나로 concat
jq -s '[.[] | .messages[]?]' research_pulse/inbox/${WEEK}_slack-dexterous/*.json \
  > research_pulse/inbox/${WEEK}_slack-dexterous.json && rm -rf research_pulse/inbox/${WEEK}_slack-dexterous
```

두 옵션 모두 digest 가 읽을 수 있다. JSON concat 쪽이 digest confidence 가 살짝 더 높다.

### 2-C. 수동 copy-paste (급할 때만)

채널에서 한 주 분량 메시지를 스크롤해 선택 → 복사 → 텍스트 파일로 저장.

```
research_pulse/inbox/2026-W17_slack-dexterous.txt
```

한계가 크다:
- 타임스탬프가 hover 에만 있어서 복사 시 유실된다 → digest confidence 가 `low` 로 캡.
- Thread reply 가 선형화되지 않는다 → "누가 누구에게 답했는지" 문맥 손실.

**이 경로는 1회성 긴급용으로만** 쓰고, 2주 PoC 동안 2-B 로 옮겨가는 것을 권장.

---

## 3. Telegram export

Telegram 은 Desktop 앱 native export 가 가장 깔끔하다. 자동화가 필요한 경우에만 Telethon 을 덧댄다.

### 3-A. Telegram Desktop native export (권장)

1. Telegram Desktop 설치 (모바일 앱에는 export 기능이 없다).
2. 대상 채팅 (그룹 혹은 1:1) 진입 → 우상단 `⋮` → `Export chat history`.
3. 옵션:
   - Format: **JSON** 선택 (HTML 은 human-readable 용; digest 에는 JSON 이 낫다).
   - Date range: 직전 주로 한정.
   - Media: 전부 체크 해제 (digest 에는 텍스트만 필요; 용량·privacy 측면에서도 유리).
4. Export 완료 후 기본 저장 위치는 `~/Downloads/Telegram Desktop/ChatExport_YYYY-MM-DD/`. 그 안의 `result.json` 을 찾아서:

```bash
mv ~/Downloads/Telegram\ Desktop/ChatExport_2026-04-24/result.json \
   research_pulse/inbox/2026-W17_telegram-research.json
```

**주의**
- Telegram 은 same-account 에서 24시간 내 재-export 에 제한이 걸리는 경우가 있다. 주 1회 페이스면 문제 없다.
- End-to-end 암호화된 Secret Chat 은 export 에 포함되지 않는다 (이건 Telegram 설계상 의도된 것).

### 3-B. Telethon 스크립트 (선택, 자동화 원할 때)

MTProto 기반으로 그룹/채널 메시지를 프로그램적으로 가져온다. 팀이 1명이라도 Desktop export 로 충분하면 이 경로는 스킵해도 된다.

**최소 스크립트 예시** (파일: `scripts/pulse_telegram_export.py` — 저장 위치는 자유)

```python
import os, json
from datetime import datetime, timedelta, timezone
from telethon.sync import TelegramClient

API_ID   = int(os.environ["TG_API_ID"])      # my.telegram.org 에서 발급
API_HASH = os.environ["TG_API_HASH"]
CHAT     = os.environ["TG_CHAT"]              # @groupname 또는 수치 ID
WEEK_TAG = os.environ.get("WEEK_TAG", "2026-W17")

end   = datetime.now(timezone.utc)
start = end - timedelta(days=7)

out = []
with TelegramClient("pulse_session", API_ID, API_HASH) as client:
    for msg in client.iter_messages(CHAT, offset_date=end, reverse=False):
        if msg.date < start:
            break
        if not msg.message:
            continue
        out.append({
            "date": msg.date.isoformat(),
            "from": getattr(msg.sender, "username", None) or str(msg.sender_id),
            "text": msg.message,
            "reply_to": msg.reply_to_msg_id,
        })

path = f"research_pulse/inbox/{WEEK_TAG}_telegram-research.json"
with open(path, "w") as f:
    json.dump(list(reversed(out)), f, ensure_ascii=False, indent=2)
print(f"wrote {len(out)} messages to {path}")
```

첫 실행 시 전화번호 인증이 필요하다. 세션 파일 (`pulse_session.session`) 이 로컬에 생기는데, **절대 repo 에 commit 하지 말 것** (이미 `.gitignore` 에 `.session` 패턴 추가를 고려).

---

## 4. Digest 호출

Export 가 `research_pulse/inbox/` 에 올라왔다면, 다음 단계는 digest:

```
Claude (Desktop / CLI / claude.ai) 세션에서:

1. 이 repo 를 attach.
2. .claude/prompts/pulse-digest.md 를 프롬프트로 주고, inbox 파일명을 명시:
   "Digest research_pulse/inbox/2026-W17_slack-dexterous.json into
    research_pulse/2026-W17.md following _TEMPLATE.md."
3. 산출된 research_pulse/2026-W17.md 를 60초 human review.
4. commit.
```

Claude Code CLI 라면 한 줄로:

```bash
claude "Run .claude/prompts/pulse-digest.md on research_pulse/inbox/2026-W17_slack-dexterous.json"
```

---

## 5. (선택) 로컬 주 1회 스케줄링

**PoC 기간에는 권장하지 않는다** — 사람이 매주 한 번 손으로 도는 것이 피드백 루프상 더 낫다. 2주 PoC 가 성공한 이후에만 적용.

### macOS / Linux cron 예시 (Slack, slackdump 기반)

```cron
# 매주 월요일 09:10 KST, 직전 주 export
10 9 * * 1  cd ~/probe && ./scripts/pulse_slack_weekly.sh
```

`scripts/pulse_slack_weekly.sh` 내용은 §2-B 의 명령을 래핑하면 된다. Digest 는 여전히 수동으로 — 자동 digest 는 human review step 을 무력화시키므로 **적어도 PoC 이후 1개월** 은 수동 유지.

---

## 6. 트러블슈팅

| 증상 | 원인 | 대응 |
|---|---|---|
| digest 결과 Confidence 가 항상 `low` | 타임스탬프/speaker 이름이 export 에 빠짐 | 2-C 대신 2-B 로 옮기거나, Telegram 의 경우 HTML 이 아닌 JSON 을 쓴다 |
| hint 의 *Converging on* 이 비어있음 | 정상. 그 주 팀이 발산 단계였던 것 | 그대로 두고, bias 는 *Exploring / confused about* 기반으로 약하게 작동 |
| hint 가 매 주 같은 signal 반복 | digest 프롬프트가 직전 주 hint 를 안 읽고 있음 | `research_pulse/*.md` glob 이 제대로 resolving 되는지 확인. `_TEMPLATE.md` / `*_EXAMPLE.md` / `_README.md` 는 제외해야 한다 |
| slackdump 토큰 만료 | Slack 이 주기적으로 session 갱신 요구 | upstream README 의 Authentication 절 재확인. PoC 기간 주 1회 페이스면 수작업 재인증이 덜 고통스럽다 |
| inbox 파일이 git 에 잡힘 | `.gitignore` 규칙 누락 | `git check-ignore -v research_pulse/inbox/<file>` 로 확인. `research_pulse/inbox/*` 와 `!research_pulse/inbox/_README.md` 두 줄이 있어야 한다 |
| digest 가 transcript 원문을 hint 에 붙임 | 프롬프트 안전장치 무시됨 | `.claude/prompts/pulse-digest.md` §6 (Privacy) 을 다시 프롬프트에 주입. 반복되면 해당 모델 세션을 버리고 새로 시작 |

---

## 7. 체크리스트 (주 1회)

- [ ] 대상 채널 확정
- [ ] 직전 주 범위로 export (§2 또는 §3)
- [ ] `research_pulse/inbox/YYYY-WXX_<source>.<ext>` 명명 규칙 준수
- [ ] `git status` 로 inbox 파일이 tracked 에 안 잡히는지 확인
- [ ] digest 실행 → `research_pulse/YYYY-WXX.md` 생성
- [ ] 60초 human review (Converging 섹션만이라도 눈으로)
- [ ] commit (hint 파일만; inbox 는 자동 제외)
- [ ] 주간 scout 돌릴 때 `_README.md` 의 PULSE HINT 블록 prompt 확장 확인
