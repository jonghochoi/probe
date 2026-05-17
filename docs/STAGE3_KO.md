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
- **검색 방식**: Claude 내장 웹 검색 → `curl`로 공개 REST API 직접 호출
  (arXiv API / Semantic Scholar Graph API) — 인용 정확도·재현성 향상
- **출력 방식**: 수동 복사 → GitHub PR 자동 커밋 (커밋 이력 = 리서치 로그)

---

## 📦 사전 준비물

| 항목 | 설명 |
|---|---|
| Claude Code Pro 플랜 | Routines는 클라우드 실행이 필요합니다. Pro 한도 5회/일, 주 2회 실행이면 충분히 여유 있습니다 |
| GitHub 레포 연결 | 이 레포가 Claude Code에 연결되어 있어야 PR 출력이 동작합니다 |
| 아웃바운드 네트워크 | Routine 환경 정책이 `export.arxiv.org` / `api.semanticscholar.org` 호출을 허용해야 함 (Step 1 참고) |
| Semantic Scholar API 키 | 선택·권장. 클라우드 환경의 환경변수로 설정 (시크릿 저장소 없음) |

사용하는 공개 API (별도 설치 불필요, Routine이 `curl`로 호출):

- arXiv API — `http://export.arxiv.org/api/query` (키 불필요)
- Semantic Scholar Graph API — `https://api.semanticscholar.org/graph/v1`
  (citation/reference graph, author search; 키 선택)

이 레포가 제공하는 핵심 자산은 **프롬프트**입니다 (루틴은 yaml이 아니라
RemoteTrigger 폼으로 등록 — Step 2 참고):

```
.claude/
└── prompts/
    ├── scouting.md     # weekly 스카우팅 루틴의 프롬프트 본문 (Step 2·3)
    └── synthesis.md    # 월간 P1 Synthesis Brief 루틴의 프롬프트 본문 (보너스)
```

따라서 새로 작성할 필요는 없고, **프롬프트를 이해·검증한 뒤 RemoteTrigger
폼에 붙여넣어 등록**하면 됩니다.

---

## 🔌 Step 1 — Retrieval 경로: curl REST (MCP 아님)

> **핵심:** Stage 3 Routine은 Anthropic 클라우드에서 독립 실행됩니다.
> **로컬 머신의 MCP 서버(arxiv/semantic-scholar)에는 도달할 수 없습니다.**
> 그래서 weekly scouting은 MCP가 아니라 **`curl`로 공개 REST API를
> 직접 호출**합니다. MCP와 데이터 출처가 동일(arXiv·Semantic Scholar
> 같은 API)하므로 스카우트 품질은 그대로이고, 달라지는 건 배관뿐입니다.

별도 설치가 필요 없습니다. Routine은 `Bash` 도구로 두 공개 API를
호출합니다:

- arXiv: `http://export.arxiv.org/api/query` (Atom XML, 키 불필요)
- Semantic Scholar Graph: `https://api.semanticscholar.org/graph/v1`
  (JSON, 키 선택)

**전제 — 아웃바운드 네트워크 정책 (진짜 리스크):**
Default 환경의 **Trusted** 네트워크는 패키지 레지스트리·GitHub만
허용하고, 그 외 도메인은 `403 host_not_allowed` 로 막힙니다. 따라서
환경 설정에서 **Network access = Custom** 으로 바꾸고 **Allowed
domains** 에 `export.arxiv.org` 와 `api.semanticscholar.org` 를
추가해야 curl이 동작합니다("Also include default list…" 체크 유지).
설정 위치는 아래 절차 참조. (문서:
https://code.claude.com/docs/en/routines#environments-and-network-access)

**`SEMANTIC_SCHOLAR_API_KEY` — 권장, 환경변수로 (시크릿 문법 없음):**
없어도 API는 동작하지만 rate limit이 낮아 Citation-Graph 확장이
부분적으로만 채워집니다. **Routine에는 전용 시크릿 저장소가 없고**,
클라우드 **환경(environment)의 환경변수**를 그대로 상속합니다. 따라서
`${{ secrets.… }}` 같은 표기는 존재하지 않으며, yaml에 키를 적지도
않습니다. 설정 절차 (키 입력과 도메인 허용이 같은 다이얼로그):

1. [claude.ai/code/routines](https://claude.ai/code/routines) → routine → 연필(**Edit routine**)
2. Instructions 박스 아래 **클라우드 아이콘**(환경 이름) 클릭
3. 환경에 마우스 올려 나오는 **설정(톱니) 아이콘** → **Update cloud environment**
4. **Environment variables** 에 `.env` 형식 한 줄 (따옴표 금지):
   `SEMANTIC_SCHOLAR_API_KEY=받아둔_키`
5. 같은 다이얼로그 **Network access → Custom**, **Allowed domains** 에
   `export.arxiv.org` / `api.semanticscholar.org` 추가
6. **Save changes** → 다음 run부터 적용. curl에서는 `$SEMANTIC_SCHOLAR_API_KEY` 로 참조됨

> 주의: 전용 시크릿 저장소가 아직 없어 환경변수는 그 환경을 편집할 수
> 있는 사람에게 보입니다. 개인용 키 수준이면 무방하나 가시성 인지 필요.
> 키 발급은 Semantic Scholar API 페이지의 "Request an API Key" 폼.

<details>
<summary>참고 — 로컬 대화형(Stage 1·2) 테스트용 MCP 설정 (선택)</summary>

클라우드 Routine에는 불필요하지만, 로컬 Claude Code 세션에서 대화형
으로 프롬프트를 다듬을 때는 MCP가 편합니다. 검증된 설정:

```json
{
  "mcpServers": {
    "arxiv": {
      "command": "uvx",
      "args": ["arxiv-mcp-server@latest", "--storage-path", "/절대경로/probe/.arxiv-storage"]
    },
    "semantic-scholar": {
      "command": "uvx",
      "args": ["semantic-scholar-fastmcp"],
      "env": {
        "SEMANTIC_SCHOLAR_API_KEY": "<optional>",
        "SEMANTIC_SCHOLAR_ENABLE_HTTP_BRIDGE": "0"
      }
    }
  }
}
```

- **arxiv**: `@latest` + `--storage-path`(절대경로, 미리 `mkdir -p`)
  필수. 구버전 캐시는 서버 엔트리포인트가 없고 `arxiv-search` CLI만
  있어 `-32000`으로 죽습니다.
- **semantic-scholar**: `SEMANTIC_SCHOLAR_ENABLE_HTTP_BRIDGE=0` 권장
  (불필요한 `:8000` HTTP 브리지 포트 충돌로 간헐 실패 방지).
- 콜드스타트가 기본 핸드셰이크 제한을 넘으므로 타임아웃을 넉넉히:
  `MCP_TIMEOUT=60000 MCP_TOOL_TIMEOUT=60000 claude` → `/mcp` 확인.
  간헐 실패 시 `pkill -f semantic-scholar-fastmcp` 후 재시도.

</details>

---

## ⚙️ Step 2 — RemoteTrigger 폼 명세 (실행 메커니즘)

> **중요:** Claude Code에는 `.claude/routines/*.yaml` 을 읽어 루틴을
> 자동 등록/실행하는 기능이 **없습니다.** 실제 스케줄링은
> [claude.ai/code/routines](https://claude.ai/code/routines) 의
> **RemoteTrigger** 폼(또는 CLI `/schedule`)으로 만듭니다. 이 레포가
> 제공하는 핵심 자산은 yaml이 아니라 **프롬프트(`scouting.md`)와 P1
> 스코프 로직**입니다. 아래 표는 그 폼에 넣을 값의 명세입니다.

| 폼 항목 | 넣을 값 |
|---|---|
| Name | `probe-weekly-scout` |
| Prompt (Instructions) | `.claude/prompts/scouting.md` 전문을 그대로 붙여넣기. 모델은 폼의 모델 선택기에서 **Sonnet** |
| Repositories | 이 레포. 산출물은 `claude/`-prefixed 브랜치로 푸시되고 PR로 검토 |
| Environment | Step 1의 환경: `SEMANTIC_SCHOLAR_API_KEY` 환경변수 + Network access **Custom** (`export.arxiv.org`, `api.semanticscholar.org` 허용) |
| Trigger (Schedule) | 주 2회(월·목) 09:00. 폼은 로컬 시각 입력→UTC 자동 변환. 최소 간격 1시간. 정밀 cron이 필요하면 생성 후 CLI `/schedule update` 로 `0 9 * * 1,4` 지정 |
| Connectors | 불필요 — 모두 제거 (retrieval은 curl, MCP 커넥터 안 씀) |
| Permissions | 기본값(`claude/` 브랜치 푸시)로 충분. PR 출력이므로 unrestricted 푸시 불필요 |

해설:

- **프롬프트가 루틴의 본문입니다.** `scouting.md` 안에 컨텍스트
  파일 경로(`research_context_P1.md`, `research_log/` 직전 2주),
  curl 절차, 산출물 규칙, 가드가 모두 자기완결적으로 들어 있어야
  합니다. 폼에는 별도 `context_files` 필드가 없으므로, 에이전트가
  레포를 클론한 뒤 프롬프트 지시에 따라 파일을 읽습니다.
- **P1 전용 스코프** — 프롬프트가 전체 `research_context.md` 가
  아니라 P1 추출본 `research_context_P1.md` 를 읽도록 지시합니다. 이
  파일은 섹션 번호가 다릅니다(Pillar P1=§2, Decision D1–D9=§4,
  Anti-topics=§5, Tracked Literature=§6, Researchers=§7,
  Competitor=§8; Cross-pollination·Feedback Loop 섹션 없음).
- **출력** — 별도 출력 모드 설정이 없습니다. 에이전트가 변경을
  `claude/`-prefixed 브랜치에 커밋하고, 그 run 세션에서 PR을
  만듭니다. 프롬프트가 산출 경로(`research_log/YYYY-W##.md` +
  `-KO.md`)를 지정합니다.
- **참고** — 로컬 머신 cron이 필요하면 RemoteTrigger 대신
  `CronCreate`(로컬 cron job) 경로도 있으나, 노트북이 꺼져도 도는
  것이 Stage 3의 목적이므로 RemoteTrigger를 권장합니다.

---

## 📝 Step 3 — 프롬프트 외부화 (`.claude/prompts/scouting.md`)

이 파일은 Stage 1의 Scouting Prompt를 그대로 옮기되, **검색 지시문만** 내장
웹 검색에서 **명시적 `curl` REST 호출**로 교체한 버전입니다 (클라우드
Routine은 로컬 MCP에 도달 불가하므로).

| 검색 단계 | Stage 1·2 | Stage 3 (curl REST) |
|---|---|---|
| Author Watch | 내장 웹 검색 | S2 `/author/search` → `/author/{id}/papers` |
| Citation-Graph 확장 | 내장 웹 검색 | S2 `/paper/arXiv:XXXX.XXXXX/citations` |
| Keyword Sweep / topic-watch | 내장 웹 검색 | arXiv `export.arxiv.org/api/query` |
| Competitor Monitoring | 내장 웹 검색 | arXiv query + S2 author lookup |

> S2 = Semantic Scholar Graph API. JSON은 `jq` 로 파싱, arXiv는 Atom
> XML로 직접 파싱. rate limit 대비 호출 간 ~3초 sleep, 429/5xx는
> 백오프 재시도. 실패 시 명령·HTTP 상태를 📋 Scout Methodology 에
> **원문 그대로** 기록(인용 조작 금지).

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

> curl 호출이 실패하면(비정상 종료·HTTP 에러·재시도 후에도 빈 응답)
> 조용히 건너뛰거나 결과를 지어내지 말 것. 실행한 명령과 에러/HTTP
> 상태를 📋 Scout Methodology 에 원문 그대로 기록하고, 성공한 소스만으로
> 진행한다. arXiv ID는 받은 응답에 있는 것만 사용한다.

이 가드가 없으면 도구 실패 시 에이전트가 그럴듯한 가짜 인용을 채워 넣을 수
있고, 그게 가장 비싼 실패입니다.

---

## 🚀 Step 4 — RemoteTrigger 생성과 첫 실행 검증

1. [claude.ai/code/routines](https://claude.ai/code/routines) →
   **New routine**
2. **Name / Prompt**: 이름 `probe-weekly-scout`, Instructions에
   `.claude/prompts/scouting.md` 전문 붙여넣기, 모델 **Sonnet**
3. **Repositories**: 이 레포 선택 (기본 `claude/` 브랜치 푸시 권한)
4. **Environment**: Step 1에서 만든 환경 선택 — `SEMANTIC_SCHOLAR_API_KEY`
   환경변수 + Network access **Custom** (두 API 도메인 허용) 확인
5. **Connectors**: 전부 제거 (curl만 사용)
6. **Trigger**: Schedule → 월·목 09:00 (정밀 cron은 생성 후 CLI
   `/schedule update` 로 `0 9 * * 1,4`)
7. **Create** → 루틴 상세 페이지에서 **Run now** 로 즉시 1회 실행

`--dry-run` 같은 별도 모드는 없습니다. **Run now** 가 검증 수단입니다 —
새 세션이 열리고 실제로 1회 실행되며, 그 세션에서 산출물·PR을 직접
확인합니다. (run 목록의 green 상태는 "인프라 에러 없이 종료"일 뿐
프롬프트 성공을 뜻하지 않으니, **반드시 세션 트랜스크립트를 열어**
실제 결과를 검수합니다. 차단된 네트워크 요청·실패는 거기에 드러납니다.)

첫 Run now 출력을 **Stage 1 리포트를 검수하던 그 엄격함으로** 점검:

- `research_log/_TEMPLATE.md` 구조를 정확히 따르는가 (이 브랜치의
  `research_log/` 에는 템플릿만 남아 있으므로 템플릿 + `docs/STYLE_GUIDE.md`
  를 직접 대조)
- 영문/한글 2파일이 모두 생성되었는가
- 모든 논문 링크가 실제로 열리는가 (지어낸 arXiv ID 없음)
- 📋 Scout Methodology 에 curl 403/네트워크 차단 에러가 없는가
  (있으면 환경 Custom 도메인 허용 누락)
- "의사결정 함의"가 구체적인가 (Isaac Lab config 키·메트릭 지목 vs generic)
- Anti-topics 필터가 실제로 동작했는가 (필터 통과 실패 후보가 비면 의심)

만족스러우면 끝 — 스케줄대로 월·목 자동 실행되며 매번 PR을 올립니다.
만족스럽지 않으면 **자동화 켜둔 채 방치하지 말고** `scouting.md` (또는
`research_context_P1.md`)를 손본 뒤 다시 Run now 로 반복합니다.

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

스카우팅과 **완전히 분리**된 두 번째 RemoteTrigger 루틴으로 굴립니다
(별도 New routine, 폼 명세는 아래).

| 폼 항목 | 값 |
|---|---|
| Name | `probe-p1-synthesis` |
| Prompt | `.claude/prompts/synthesis.md` 전문 붙여넣기, 모델 Sonnet |
| Repositories | 이 레포 |
| Environment | 기본 환경으로 충분 (검색 없음 → 커스텀 도메인 불필요) |
| Trigger | Schedule, 월 1회 (정밀 cron은 CLI `/schedule update` 로 `0 9 1 * *`) |
| Connectors | 전부 제거 |
| 입력 | `research_context_P1.md` §4(D1–D9) + §6(핀 논문)만 |
| 출력 | `synthesis/P1_BRIEF.md` (Korean, 매번 덮어쓰는 living snapshot) |
| 검색 | **없음** — MCP·웹·curl 없이 정적 파일 압축만 (인용 조작 위험 0) |

구성:

- **Decision별 서사** — D1~D9 각각 2~3문장. (1) v1 선택을 떠받치는 §6 핀
  논문(이름 + Role 컬럼의 D# 태그), (2) 이를 흔들거나 긴장 관계에 있는
  논문/deferred 트리거. 떠받치는 핀 논문이 없으면 솔직히 그렇게 적습니다
  (지어내지 않음).
- **`## 지금 머릿속에 들고 있어야 할 것`** — D1~D9를 관통하는 줄기, 가장
  날카로운 미해결 긴장, "새 논문 한 편이 그림을 바꾸려면 무엇을 보여야
  하는가". 고정 줄 수 없음 — load-bearing한 만큼만, 패딩 금지.

핀 논문(§6)이 바뀌면 다음 월간 실행을 기다리지 말고 루틴 상세 페이지의
**Run now** 로 즉시 재생성합니다.

> 길어지면 죽는 문서입니다. 가치는 *간결함과 솔직함*에 전적으로 달려
> 있으므로, Run now 검수 시 "모든 핀 논문을 다 언급하려 들지 않는가",
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
| 같은 논문이 2주 연속 추천됨 | 직전 2주 로그를 안 읽음 | `scouting.md` 의 "직전 2주 `research_log/*.md` read-only 참조" 지시가 살아 있는지, 레포에 해당 로그가 실제로 있는지 확인 |
| `claude routine register` / yaml 파일이 안 먹힘 | `.claude/routines/*.yaml` 은 실행 메커니즘이 아님 | RemoteTrigger 폼([claude.ai/code/routines](https://claude.ai/code/routines))으로 등록 — Step 2·4 |
| 에이전트가 `research_context_P1.md` 를 무단 수정 | 프롬프트 가드 누락 | `scouting.md` 에 "어떤 경우에도 research_context_P1.md를 수정하지 말 것" 재삽입 (현재 포함돼 있음 — 제거 금지) |
| Routine은 돌았는데 PR이 비어 있음 / 모든 curl 실패 | 아웃바운드 네트워크 정책이 API 도메인 차단 | 환경 네트워크 정책에서 `export.arxiv.org` / `api.semanticscholar.org` 허용 확인. 📋 Scout Methodology 의 에러 원문 확인 |
| Citation-Graph가 부분적으로만 채워짐 / HTTP 429 빈발 | Semantic Scholar API 키 없음 → rate limit | 환경 환경변수에 `SEMANTIC_SCHOLAR_API_KEY=<key>` 추가(시크릿 문법 없음). 프롬프트의 호출 간 sleep·백오프 유지 확인 |
| `scouting.md` 가 MCP 도구를 호출하려 함 | 구버전 프롬프트(MCP 잔재) | `scouting.md` RETRIEVAL 섹션이 curl REST 기반인지 확인 (MCP 서버는 클라우드에서 도달 불가) |
| (로컬 대화형) MCP `✘ failed` `-32000` / 간헐 실패 | Step 1 접힌 섹션 참고 — 구버전 캐시 또는 `:8000` 브리지 충돌 | 클라우드 Routine과 무관. 로컬 테스트 시에만 해당 — Step 1 `<details>` 의 검증된 설정 적용 |

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
