# 🛰️ Stage 3 — Claude Code Routines로 완전 자동화 (한글 가이드)

> **대상:** Stage 1·2를 거쳐 프롬프트 품질이 검증된 상태에서 PROBE를
> 클라우드 스케줄·도구 장착·PR 자동 커밋으로 전환하려는 운영자.
> **요약본:** `README.md` §Agent Setup Guide. 이 문서는 그보다 깊게 —
> 각 단계의 *이유*, 검증법, 함정, 운영 루프까지 — 다룹니다.

---

## 🧭 이 단계가 필요한 이유

PROBE 도입은 3단계로 진화합니다.

```
Stage 1 (Week 1–2)  수동       Claude.ai에 컨텍스트 붙여넣고 프롬프트 반복 튜닝
Stage 2 (Week 3–4)  반자동     Claude Desktop Scheduled Tasks (노트북이 깨어 있어야 함)
Stage 3 (Week 5+)   완전 자동  Claude Code Routines (클라우드, PR 자동 커밋)
```

**단계를 건너뛰지 않습니다.** Stage 3는 새로운 프롬프트를 만드는 단계가
아니라, Stage 1에서 *살아남은* 프롬프트를 그대로 배포하는 단계입니다.
나쁜 프롬프트를 자동화하면 매주 정해진 시각에 쓰레기 로그가 생성될 뿐입니다.
Stage 1·2에서 두 번 이상 "실제로 읽을 만한" 리포트가 나왔을 때만 진입합니다.

Stage 3에서 달라지는 것은 **세 가지**뿐입니다.

- **실행 위치**: 노트북 → 클라우드 (월·목 09:00, 노트북이 꺼져 있어도 실행)
- **검색 방식**: Claude 내장 웹 검색 → 명시적 MCP 도구 호출 (arXiv /
  Semantic Scholar) — 인용 정확도와 재현성이 올라갑니다
- **출력 방식**: 수동 복사 → GitHub PR 자동 커밋 (커밋 이력 = 리서치 로그)

---

## 📦 사전 준비물

| 항목 | 설명 |
|---|---|
| Claude Code Pro 플랜 | Routines는 클라우드 실행이 필요합니다. Pro 한도 5회/일, 주 2회 실행이면 충분히 여유 있습니다 |
| GitHub 레포 연결 | 이 레포가 Claude Code에 연결되어 있어야 PR 출력이 동작합니다 |
| MCP 서버 2종 | 아래 Step 1에서 설치 |

설치할 MCP 서버:

- [`blazickjp/arxiv-mcp-server`](https://github.com/blazickjp/arxiv-mcp-server)
  — arXiv 검색, topic-watch, citation graph
- [`zongmin-yu/semantic-scholar-fastmcp`](https://github.com/zongmin-yu/semantic-scholar-fastmcp)
  — citation / reference graph, author search

이 레포에는 Stage 3 인프라가 이미 준비되어 있습니다:

```
.claude/
├── routines/
│   └── probe-weekly.yaml      # Routine 정의 (Step 2)
└── prompts/
    └── scouting.md            # 외부화된 에이전트 프롬프트 (Step 3)
```

따라서 직접 만들 필요는 없고, **내용을 이해하고 검증한 뒤 등록**하면 됩니다.

---

## 🔌 Step 1 — MCP 서버 설치

`~/.claude/mcp.json` (전역) 또는 프로젝트 루트 `.mcp.json` (레포 한정)에
다음을 추가합니다.

```json
{
  "mcpServers": {
    "arxiv": {
      "command": "uvx",
      "args": ["arxiv-mcp-server"]
    },
    "semantic-scholar": {
      "command": "uvx",
      "args": ["semantic-scholar-fastmcp"],
      "env": { "SEMANTIC_SCHOLAR_API_KEY": "<optional-but-recommended>" }
    }
  }
}
```

- 서버 이름 `arxiv` / `semantic-scholar` 는 `probe-weekly.yaml` 의
  `mcp_servers` 항목 및 `scouting.md` 의 도구 호출 이름과 **정확히 일치**해야
  합니다. 임의로 바꾸지 마십시오.
- `SEMANTIC_SCHOLAR_API_KEY` 는 선택이지만 **권장**합니다. 키가 없으면
  citation-graph 확장 단계에서 rate limit에 자주 걸려 리포트가 부분적으로만
  채워집니다. Author Watch·Citation-Graph가 PROBE의 가장 효율적인 검색
  경로이므로, 이 단계가 막히면 신호 품질이 크게 떨어집니다.

검증 — 등록 전에 로컬에서 먼저 확인합니다.

```bash
claude mcp list
# arxiv ✓  semantic-scholar ✓  가 보여야 합니다
```

두 서버가 ✓ 로 뜨지 않으면 다음 단계로 넘어가지 마십시오. Routine은
이 두 서버에 전적으로 의존합니다.

---

## ⚙️ Step 2 — Routine 정의 (`.claude/routines/probe-weekly.yaml`)

파일 내용:

```yaml
name: probe-weekly-scout
description: Weekly arXiv scouting for hand-centric dexterous manipulation.

trigger:
  cron: "0 9 * * 1,4"          # 월/목 09:00
  timezone: Asia/Seoul

model: claude-sonnet-4-6

mcp_servers:
  - arxiv
  - semantic-scholar

context_files:
  - research_context_P1.md      # P1 전용 스코프 (이 브랜치)
  - research_log/_TEMPLATE.md
  - research_log/*.md           # 직전 2주 분량을 에이전트가 자동 절삭

prompt_file: .claude/prompts/scouting.md

output:
  mode: github_pr
  branch: probe/weekly-YYYY-W##
  path:   research_log/YYYY-W##.md
  title:  "chore(probe): scouting report YYYY-W##"
```

필드 해설:

- **`trigger.cron: "0 9 * * 1,4"`** — `분 시 일 월 요일` 순서.
  `1,4` 는 월요일·목요일을 의미하므로 주 2회, 09:00에 실행됩니다.
- **`timezone: Asia/Seoul`** — cron이 KST 기준으로 해석됩니다. 이게 없으면
  UTC로 동작해 한국 시간 18:00에 실행되니 반드시 지정합니다.
- **`model: claude-sonnet-4-6`** — 주간 스카우팅의 기본 모델. 더 깊은 분석이
  필요하면 Opus로 올릴 수 있으나, 주 2회 정기 실행에는 Sonnet이 비용·품질
  균형이 좋습니다.
- **`context_files`** — 에이전트가 read-only로 읽는 정적 컨텍스트.
  이 브랜치는 **P1 전용 스코프**로 동작하므로 전체 `research_context.md`가
  아니라 P1만 좁힌 추출본 **`research_context_P1.md`** 를 읽습니다. 이 파일은
  섹션 번호가 전체 문서와 다릅니다(Pillar P1=§2, Decision D1–D9=§4,
  Anti-topics=§5, Tracked Literature=§6, Researchers=§7, Competitor=§8;
  Cross-pollination·Feedback Loop 섹션은 없음). `research_log/*.md` glob은
  전체를 다 읽지 않고 **직전 2주만 자동 절삭**해 중복 추천 방지에만
  사용합니다. 이 glob이 비어 있으면 같은 논문이 매주 재추천되므로
  (트러블슈팅 참고) 경로가 실제로 매칭되는지 확인하십시오.
- **`prompt_file`** — Step 3의 외부화된 프롬프트.
- **`output.mode: github_pr`** — 실행 결과를 `probe/weekly-YYYY-W##`
  브랜치에 커밋하고 PR을 엽니다. PR 설명이 그 주의 변경 로그가 됩니다.

---

## 📝 Step 3 — 프롬프트 외부화 (`.claude/prompts/scouting.md`)

이 파일은 Stage 1의 Scouting Prompt를 그대로 옮기되, **검색 지시문만** 내장
웹 검색에서 명시적 MCP 도구 호출로 교체한 버전입니다.

| 검색 단계 | Stage 1·2 | Stage 3 (MCP 도구) |
|---|---|---|
| Author Watch | 내장 웹 검색 | `semantic-scholar.get_author_papers` |
| Citation-Graph 확장 | 내장 웹 검색 | `semantic-scholar.get_paper_citations` |
| Keyword Sweep / topic-watch | 내장 웹 검색 | `arxiv.search_papers` |
| Competitor Monitoring | 내장 웹 검색 | `arxiv.search_papers` + `semantic-scholar.get_author_papers` |

바뀌지 **않는** 것 (Stage 1에서 검증된 그대로 유지):

- 0–3 점수 체계 (Relevance / Novelty / Reproducibility / Sim2Real)
- 모든 차원 ≥ 2 인 논문만 상위 3–5편으로 노출, 부족하면 솔직히 보고(패딩 금지)
- 직전 2주 로그와 중복 추천 금지
- 영문 `YYYY-WXX.md` + 한글 `YYYY-WXX-KO.md` **2파일** 산출
- 이모지·링크·한글 번역 규칙은 `docs/STYLE_GUIDE.md` §2–§4 참조
- **`research_context_P1.md` 수정 절대 금지** — 변경 제안은 💡 Context
  Suggestions 에만 작성

> P1 전용 스코프에서는 월 1회 Cross-pollination 강제 1편 규칙이
> 빠집니다. 해당 규칙의 근거 섹션(전체 `research_context.md` §12
> Cross-pollination Budget)이 P1 추출본에 존재하지 않기 때문입니다.

핵심 가드 — 인용 조작 방지:

> MCP 도구 호출이 실패하면 조용히 건너뛰지 말 것. 에러 원문을 📋 Scout
> Methodology 에 그대로 기록하고, 성공한 소스만으로 진행한다. arXiv ID를
> 절대 지어내지 않는다.

이 가드가 없으면 도구 실패 시 에이전트가 그럴듯한 가짜 인용을 채워 넣을 수
있고, 그게 가장 비싼 실패입니다.

---

## 🚀 Step 4 — 등록과 드라이런

```bash
claude routine register .claude/routines/probe-weekly.yaml
claude routine run probe-weekly-scout --dry-run
```

`--dry-run` 은 스케줄을 기다리지 않고 즉시 1회 실행하되 PR을 만들지 않고
출력을 보여줍니다. 이 출력을 **Stage 1 리포트를 검수하던 그 엄격함으로**
점검합니다.

점검 체크리스트:

- `research_log/_TEMPLATE.md` 의 구조를 정확히 따르는가 (이 브랜치의
  `research_log/` 에는 템플릿만 남아 있으므로, 구조·품질 기준은 템플릿과
  `docs/STYLE_GUIDE.md` 를 직접 대조)
- 영문/한글 2파일이 모두 생성되었는가
- 모든 논문 링크가 실제로 열리는가 (지어낸 arXiv ID 없음)
- "의사결정 함의"가 구체적인가 — Isaac Lab config 키·하이퍼파라미터·메트릭을
  지목하는가, 아니면 "DR 범위를 넓혀라" 수준의 generic인가
- Anti-topics 필터가 실제로 동작했는가 (필터 통과 실패 후보가 비어 있으면 의심)

드라이런이 만족스러우면 끝입니다. Routine이 월·목 자동 실행되며 매번 PR을
올립니다. 만족스럽지 않으면 **자동화하지 말고** `scouting.md` 또는
`research_context_P1.md` 를 손본 뒤 드라이런을 반복합니다.

---

## 🔁 Step 5 — 월간 휴먼 리뷰

자동화는 결승선이 아닙니다. 에이전트가 잘 작동하는지는 에이전트 스스로
판단할 수 없습니다. 월 1회 Feedback Loop에 세 숫자를 직접 채웁니다.
P1 추출본에는 Feedback Loop 섹션이 없으므로, 이 휴먼 리뷰는 멀티필러
원본인 전체 `research_context.md` Section 13 에 기록합니다(에이전트는
P1 추출본만 읽지만, 사람의 피드백 기록은 원본에서 관리).

| 채울 것 | 질문 |
|---|---|
| Papers surfaced | 이번 달 PROBE가 올린 총 논문 수 |
| Actually read | 그중 실제로 정독한 수 |
| Influenced a decision | 그중 실험 설계나 Decision Log를 바꾼 수 |

이 세 숫자의 **비율**이 PROBE의 진짜 KPI입니다. 비율이 0으로 수렴하면
모델이 아니라 **프롬프트가 드리프트**한 것입니다 — `scouting.md` 와
`research_context_P1.md` 의 Anti-topics(§5)·Pillar P1(§2)을 재점검합니다.

---

## 🧵 보너스 — P1 Synthesis Brief (풀 연결고리 서사)

주간 스카우팅이 *바깥*에서 새 논문을 찾아온다면, 이 산출물은 *안*을
봅니다. 이미 핀된 논문들이 결국 무슨 이야기를 하고 있는지 — 각 Decision을
무엇이 떠받치고 무엇이 흔드는지 — 를 산문 서사로 압축해, 사람이 P1
아키텍처를 머릿속에 계속 들고 다닐 수 있게 합니다.

스카우팅 Routine과 **완전히 분리**된 두 번째 Routine으로 굴립니다.

| 항목 | 값 |
|---|---|
| Routine | `.claude/routines/probe-synthesis.yaml` (`probe-p1-synthesis`) |
| 프롬프트 | `.claude/prompts/synthesis.md` |
| 트리거 | 월 1회 (`0 9 1 * *`, Asia/Seoul) |
| 입력 | `research_context_P1.md` §4(D1–D9) + §6(핀 논문)만 |
| 출력 | `synthesis/P1_BRIEF.md` (Korean, 매번 덮어쓰는 living snapshot) |
| 검색 | **없음** — MCP·웹 호출 없이 정적 파일 압축만 (인용 조작 위험 0) |

구성:

- **Decision별 서사** — D1~D9 각각 2~3문장. (1) v1 선택을 떠받치는 §6 핀
  논문(이름 + Role 컬럼의 D# 태그), (2) 이를 흔들거나 긴장 관계에 있는
  논문/deferred 트리거. 떠받치는 핀 논문이 없으면 솔직히 그렇게 적습니다
  (지어내지 않음).
- **`## 지금 머릿속에 들고 있어야 할 것`** — D1~D9를 관통하는 줄기, 가장
  날카로운 미해결 긴장, "새 논문 한 편이 그림을 바꾸려면 무엇을 보여야
  하는가". 고정 줄 수 없음 — load-bearing한 만큼만, 패딩 금지.

핀 논문(§6)이 바뀌면 다음 월간 실행을 기다리지 말고 즉시 재생성합니다:

```bash
claude routine register .claude/routines/probe-synthesis.yaml
claude routine run probe-p1-synthesis --dry-run
```

> 길어지면 죽는 문서입니다. 가치는 *간결함과 솔직함*에 전적으로 달려
> 있으므로, 드라이런 검수 시 "모든 핀 논문을 다 언급하려 들지 않는가",
> "Decision당 2~3문장을 넘기지 않는가"를 가장 먼저 봅니다.

> 산출물 언어는 한글 단일 파일입니다. 이건 에이전트가 retrieval에 쓰는
> 문서가 아니라 사람이 다시 읽는 직관 도구라, 영문/한글 2파일 규칙
> (`docs/STYLE_GUIDE.md` §1, `research_log/` 한정)을 적용하지 않습니다.

---

## 🧰 트러블슈팅

| 증상 | 추정 원인 | 처방 |
|---|---|---|
| 추천 논문이 Anti-topics 목록에 가까움 | Anti-topics가 너무 모호함 | `research_context_P1.md` §5(P1 Anti-topics)를 구체적 배제 규칙으로 재작성 (예: "주 태스크가 locomotion인 논문 전부 제외") |
| "의사결정 함의"가 generic ("DR을 넓혀라") | 프롬프트가 구체성을 강제하지 않음 | `scouting.md` 에 "정확한 Isaac Lab config 키와 범위를 지목하라" 추가 |
| 같은 논문이 2주 연속 추천됨 | 직전 2주 컨텍스트를 건너뜀 | `context_files` 의 `research_log/*.md` glob이 실제로 매칭·비어있지 않은지 확인 |
| 에이전트가 `research_context_P1.md` 를 무단 수정 | 프롬프트 가드 누락 | `scouting.md` 에 "어떤 경우에도 research_context_P1.md를 수정하지 말 것" 재삽입 (현재 포함돼 있음 — 제거 금지) |
| Routine은 돌았는데 PR이 비어 있음 | MCP 도구 실패가 조용히 삼켜짐 | routine 실행 로그 확인. `scouting.md` 의 "도구 실패 시 에러 원문 기록" 가드가 살아 있는지 확인 |
| `claude mcp list` 에 서버가 안 보임 | mcp.json 경로/이름 오류 | Step 1 JSON의 서버 이름이 yaml `mcp_servers` 와 일치하는지 대조 |

---

## 🧱 운영 원칙 요약

- **자동화는 결승선이 아니다.** 월간 Feedback Loop를 채우지 않으면 PROBE가
  잘 도는지 알 방법이 없습니다.
- **정적/동적 분리를 유지한다.** `research_context_P1.md`(사람 관리)와
  `research_log/`(에이전트 생성)를 절대 섞지 않습니다. 섞으면 6주 안에
  컨텍스트가 부풀어 재추천·망각이 발생합니다.
- **이 브랜치는 P1 전용 스코프.** 에이전트는 `research_context_P1.md` 만
  읽습니다. 전체 `research_context.md`(P1–P5)는 멀티필러 원본으로 별도
  유지되며, P2–P5 콘텐츠는 거기에만 존재합니다.
- **Tracked literature는 추가만 하지 말고 교체 기준으로 관리.**
- **Scouting Report는 직전 2주 로그만 읽는다.** 그 이전은 컨텍스트에서 제외.
- **단계를 건너뛰지 않는다.** Stage 1에서 검증된 프롬프트만 Stage 3로.

---

## 🔗 관련 문서

| 문서 | 역할 |
|---|---|
| `README.md` §Agent Setup Guide | Stage 1→3 전체 요약 |
| `docs/INTRO_KO.md` | 한글 온보딩 (왜 존재하는가 / 파이프라인) |
| `docs/STYLE_GUIDE.md` | 출력 포맷·이모지·한글 번역 규칙 (에이전트 필독) |
| `research_context_P1.md` | **이 브랜치가 읽는** P1 전용 정적 컨텍스트 |
| `research_context.md` | 멀티필러 원본 (P1–P5, Feedback Loop §13) |
| `research_log/_TEMPLATE.md` | 매주 채우는 리포트 양식 |
| `synthesis/P1_BRIEF.md` | 월 1회 재생성되는 P1 연결고리 서사 (사람이 다시 읽는 직관 도구) |
