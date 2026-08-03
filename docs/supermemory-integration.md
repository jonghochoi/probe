# supermemory 통합 추천 — PROBE 지식을 연구 도출 에이전트의 검색 기층으로

이 문서는 "PROBE에 축적된 연구원의 직관·결정·문헌을 데이터베이스화해, 새 연구를
도출하는 에이전트가 빠르게 검색·회수하도록 하려면 [supermemory](https://supermemory.ai)가
어떤 도움을 줄 수 있는가"에 대한 **설계/추천 문서**다. 구현(수집 스크립트·에이전트
배선)은 포함하지 않으며, 의사결정을 위한 아키텍처·트레이드오프 정리가 목적이다.

설계 판단의 두 축 — 메타데이터 매핑(어떻게 PROBE 구조를 검색 필터로 옮기나)과
배포 방식(셀프호스팅 vs 호스티드) — 을 결론까지 끌고 간다.

## 1. 한 줄 답과 가치 명제

supermemory는 PROBE 마크다운 코퍼스 **위에 얹는 시맨틱 retrieval 기층**이다. 단일
진실 원천(SSOT)은 여전히 git에 든 마크다운이고, supermemory는 언제든 재생성 가능한
*파생 인덱스*로만 둔다 — 권위를 갖지 않는다.

현재 PROBE 지식은 세 경로로만 접근된다 — `grep`, 직접 파일 읽기, 그리고 단 하나의
자동 인덱스(`scripts/refresh-analysis-index.py`가 만드는 `analysis/README.md`).
"에이전트가 새 연구를 도출"하려면 이걸로는 부족하다. 필요한 질의는 정확 문자열
매칭이 아니라 *의미*에 걸리기 때문이다.

supermemory가 에이전트에 주는 것 4가지:

1. **퍼지 개념 → 관련 결정·논문 회수** — hybrid 시맨틱 검색(`POST /v3/search`)이
   문서 청크와 추출된 memory를 한 번에 랭킹한다. "tactile feedback을 action expert에
   주입하는 선택지"처럼 키워드가 일치하지 않는 개념 질의가 걸린다.
2. **Decision Log / Tracked Literature의 atomic memory 회수** — 수집 시 결정·문헌이
   atomic fact로 추출돼, 풀텍스트가 아니라 *결정 단위*로 회수된다.
3. **Pillar 간 교차수분(cross-pollination)** — `containerTags`를 전체로 열어 P1 개념을
   던지면 P2·P3 hit가 표면화된다. `context/MASTER.md`의 Cross-pollination 항목을
   수작업이 아니라 검색으로 자동화한다.
4. **결정 로그의 잠재 모순·공백 표면화** — 결정 memory와 최근 scouting을 함께 회수해
   "v1 선택을 뒤집는 새 문헌"을 에이전트가 찾아내게 한다.

핵심: PROBE는 이미 고도로 구조화돼 있어(아래 §2) supermemory의 메타데이터 필터축에
**거의 그대로 매핑**된다. 색인 가능한 시맨틱 단위가 결정(42)·분석 논문(36)·scouting
리포트 단위로 풍부하고, pillar·decision·tag의 다축 메타데이터가
이미 load-bearing이다.

## 2. 메타데이터 매핑 — PROBE 구조에서 supermemory 필터축으로

PROBE의 구조화된 메타데이터를 supermemory의 `containerTag` / `metadata` / `customId`로
직결한다. 왼쪽은 모두 *이미 존재하는* PROBE 필드다.

| PROBE 구조 | supermemory 필드 | 비고 |
|---|---|---|
| `관련 Pillar`(primary = 첫 항목) | `containerTag` = primary P#; `containerTags` = 나열된 전체 + `metadata.pillars[]` | primary로 격리, 전체로 교차수분 |
| `D#` 결정 연계 | `metadata.decisions[]` (예: `["D1","D2"]`) | decision 축 필터 |
| `태그`(통제 어휘 12종) | `metadata.tags[]` | topic 축 필터 |
| arXiv id | `customId = arxiv:<id>` | 중복제거 + 갱신 추적 → 재수집 idempotent |
| `발행일` / `분석 생성일` | `metadata.published` / `metadata.analyzed` | numeric range 필터 |
| 문서 종류 | `metadata.doc_type` | `decision` / `lit` / `analysis` / `scouting` |

이 매핑으로 에이전트는 "P1 ∩ D4 ∩ tag=tactile ∩ 2025년 이후" 같은 다축 질의를
시맨틱 검색 위에서 던질 수 있다 — pillar(아키텍처 축) × decision(전술 축) ×
tag(주제 축)의 최소 3개 독립 필터축.

**핵심 재사용 (새로 짜지 말 것).** `scripts/refresh-analysis-index.py`가 이미
`논문 메타` 테이블의 load-bearing 행(`관련 Pillar` → `PILLAR_ROW`, `링크`, `태그`,
`분석 생성일`)을 정규식으로 파싱한다. 수집기의
메타데이터 추출 로직은 이 파서를 **재사용하거나 그대로 본떠야** 한다 — 같은 행
스펙을 두 곳에서 다르게 해석하면 인덱스와 supermemory가 어긋난다. 행 스펙의 SSOT는
`docs/style.md` §5-6이다.

## 3. 소스별 수집 매핑 (개념 설계)

각 PROBE 산출물을 어떤 단위로 쪼개 어떤 메타데이터를 달아 수집할지. 코드가 아니라
*무엇을 document로 보느냐*의 설계다.

- **`context/P{0..5}.md` §3 Decision Log** → **결정당 1 document**
  (`customId = decision:P1:D1`), `containerTag = P1`, `metadata.doc_type = decision`.
  `entityContext`로 "이 결정의 선택지 코드와 근거를 추출하라"를 지시한다.
  *최고가치 — 연구원의 직관이 가장 농축된 곳.* (`context/`는 human read-only이므로
  수집은 **읽기만**, 어떤 경우에도 역기록 금지.)
- **`context/P{0..5}.md` §5 Tracked Literature** → 행당 1 doc,
  `customId = arxiv:<id>`, `metadata`에 role·year. 결정과 문헌을 같은
  `containerTag` 안에 두어 "이 결정을 떠받치는 논문" 회수가 한 질의에 걸린다.
- **`analysis/<id>/analysis.md`** → 논문당 1 doc, `customId = arxiv:<id>`,
  `논문 메타` 전체를 metadata로. **본문이 한글**이므로 임베딩 모델의 한국어 처리력이
  회수 품질을 좌우한다(→ §5·§6의 1순위 리스크).
- **`scouting/P#/YYYY-MM-DD.md`** → 리포트당 1 doc, `containerTag = P#`,
  `metadata.date`. 주간 스냅샷이라 "최근 N주 동향" 시간축 질의의 소스가 된다.

수집 전 정제: Math/KaTeX 수식과 shields.io 배지 마크업은 임베딩에 노이즈이므로
청크 전 스트립을 권장한다(아래 §6).

## 4. "연구 도출 에이전트" 워크플로 (개념)

supermemory는 retrieval 기층일 뿐이고, 도출 로직은 그 위에 올리는 별도 루프다(미래의
slash-command로 구현 가능). 기존 PROBE 파이프라인(scouting → analysis)을
대체하지 않고 *그 산출물을 재료로* 쓴다.

1. **시드** — 개념/공백을 받아 전 P# hybrid `search`로 관련 결정·논문 회수.
2. **교차수분** — P1 개념을 `containerTags = [전체]`로 던져 P2·P3 hit 표면화 →
   pillar 경계를 넘는 연결 후보(=`MASTER.md` Cross-pollination의 자동화).
3. **모순/공백 탐지** — `metadata.doc_type = decision` memory + 최근 scouting을 함께
   회수해, v1 선택을 약화시키는 신규 문헌이 있는지 모델에 판단시킨다.
4. **근거화** — 제안 아이디어를 Tracked Literature·analysis로 뒷받침/반증.
5. **출력** — scouting-style 신규 제안. 사람이 검토 후 `context/P#.md`에 반영.

## 5. 배포 방식 — 셀프호스팅 vs 호스티드 (실제 사례 대비)

supermemory는 두 형태로 운영된다. 각각을 PROBE의 구체 시나리오로 대비한다.

### 5.1 셀프호스팅 — `npx supermemory local`

`npx supermemory local`이 `localhost:6767`에 단일 바이너리 서버를 띄운다. API 키
불필요, 데이터는 로컬 디스크(`./.supermemory/`)에만 머문다.

> **실제 사례.** PROBE의 P1–P5 Decision Log는 *발표 전* 아키텍처 선택(어떤 split
> form을 쓰는지, body↔hand 정보 공유를 FiLM으로 하는지)이다. 이걸 연구원 노트북이나
> 샌드박스 컨테이너에서 색인하면 한 비트도 외부로 나가지 않는다. 임베딩은 로컬
> Ollama 모델이나 본인이 관리하는 OpenAI/Anthropic 키로 돌린다. 커넥터와 호스티드
> MCP는 없으므로, 로컬 API(`/v3/documents`·`/v3/search`)를 slash-command에 직접
> 배선한다 — SDK는 `baseURL`만 `http://localhost:6767`로 바꾸면 된다.

- **적합** — 발표 전 경쟁 연구 + 한글 콘텐츠 + 단일 연구원 소유 컨텍스트
  (= PROBE의 현재 상태 그대로).
- **한계** — 외부 커넥터 없음, 호스티드 MCP 없음, 임베딩 품질이 *직접 고른 모델*에
  좌우됨(특히 한글).

### 5.2 호스티드 — `api.supermemory.ai`

`sm_*` API 키로 `api.supermemory.ai`에 붙는다. 전용 long-horizon 임베딩 모델,
커넥터(Google Drive·Notion·GitHub 등), 호스티드 MCP 서버를 포함한다.

> **실제 사례.** PROBE가 팀 공유 KB로 자란 경우. 전용 임베딩이 고밀도 한글 Decision
> Log의 회수율을 끌어올린다. 호스티드 MCP(`mcp.supermemory.ai`)가 제로 인프라로
> Claude에 `recall`·`memory` 툴을 즉시 탑재한다. 커넥터로 외부 awesome-list GitHub
> 저장소를 자동 수집할 수도 있다. 대가는 — 데이터가 SaaS로
> 전송된다.

- **적합** — 다수 연구원 공유 + 최고 회수율 요구 + 결정이 SaaS 반입을 막을 만큼
  비밀은 아닐 때.
- **한계** — 데이터 외부 전송, API 키·비용.

### 5.3 대비표와 추천

| 기준 | 셀프호스팅 | 호스티드 |
|---|---|---|
| 프라이버시 | 데이터 로컬 고정 | SaaS로 전송 |
| 한글 회수율 | 선택한 로컬 모델에 의존 | 전용 모델로 일반적으로 우위 |
| 인프라 | 단일 바이너리, 본인 관리 | 제로 인프라 |
| 커넥터 | 없음 | 있음(Drive·Notion·GitHub …) |
| MCP | 직접 배선 | 호스티드 MCP 즉시 |
| 비용 | 무료(+ 본인 모델 비용) | API 키·사용량 과금 |

**추천 — 셀프호스팅으로 PoC를 시작한다.** PROBE는 발표 전 경쟁 연구이고 한글이며
단일 연구원이 소유한 컨텍스트라, 프라이버시·통제 우선순위가 명확하다. 먼저 로컬에서
한글 회수 품질을 검증(아래 §6)하고, 팀이 커지거나 로컬 임베딩의 한글 회수율이
부족하다고 판명되면 그때 호스티드로 이전한다 — SDK `baseURL` 교체만으로 마이그레이션
경로가 열려 있어 초기 선택의 매몰비용이 낮다.

## 6. 주의·경계 (Caveats)

- **한글 임베딩 품질 검증이 1순위 리스크.** PROBE 본문은 한글이라 로컬 임베딩 모델이
  약하면 회수가 무너진다. PoC 첫 단계에서 대표 `analysis/<id>/analysis.md` 몇 편으로
  retrieval 정확도를 *반드시* 측정한 뒤 본격 색인을 결정한다.
- **SSOT는 마크다운 + git.** supermemory는 파생/재생성 가능한 인덱스이지 권위가
  아니다. 소스 변경 시 재수집하며, `customId`(arXiv id·`decision:P#:D#`)가 갱신을
  idempotent하게 만든다.
- **`context/`는 human read-only.** 수집은 `context/P{0..5}.md`를 읽기만 하고 절대
  되쓰지 않는다 — PROBE의 핵심 불변식이다.
- **임베딩 노이즈 제거.** Math/KaTeX 수식과 shields.io 배지 마크업은 의미가 없으니
  수집 전 스트립을 권장한다(`docs/style.md` §5-5의 수식 규칙 참조).

## 다음 단계 (참고)

이 문서는 설계/추천까지다. 진행을 결정하면 다음이 후속 작업 — (1) `refresh-analysis-index.py`
파서를 재사용한 수집기, (2) 한글 회수 품질 PoC 측정, (3) 도출 에이전트 slash-command.
이 문서는 그 작업들의 설계 기준점으로 둔다.
