# supermemory PoC 런북 (cut 1 — analysis 색인 + 한글 회수 측정)

이 문서는 `docs/supermemory-integration.md`(설계/추천)의 첫 구현 조각을 **실제로
돌리는 절차서**다. cut 1 범위는 `analysis/<id>/analysis.md`(논문당 1 doc)만 —
supermemory 내장 로컬 임베딩의 **한글 회수 품질**(설계문서 §6 1순위 리스크)을 값싸게
먼저 측정하는 게 목적이다.

구성 산출물(전부 Python stdlib, 무의존):

| 파일 | 역할 |
|---|---|
| `scripts/probe_corpus.py` | 공유 파서 — `논문 메타` 파싱(인덱스 스크립트와 동일 소스) + supermemory-doc 빌더 + 임베딩 노이즈 스트립 |
| `scripts/supermemory_ingest.py` | 추출 CLI + 얇은 urllib 클라이언트 — `--dry-run`(JSON) 또는 `POST /v3/documents` |
| `scripts/supermemory_eval.py` | 한글 개념 질의 → `/v3/search` → hit-rank / hit@k / MRR |

## 1. 이 저장소(샌드박스)에서 검증 가능한 것

원격 샌드박스는 `api.supermemory.ai` 가 차단돼 있고 로컬 서버도 없어, **오프라인
dry-run 까지만** 검증한다. 이게 이 환경이 증명할 수 있는 전부다.

```
# 전체 코퍼스를 supermemory 문서로 빌드해 JSON 으로 확인
python3 scripts/supermemory_ingest.py --dry-run --out /tmp/docs.json

# 한 편만
python3 scripts/supermemory_ingest.py --dry-run --id 2606.12105
```

확인 포인트 — 각 doc 의 `customId = arxiv:<id>`, `containerTag`(primary Pillar) /
`containerTags`(전체), `metadata`(doc_type·pillars·tags·published·analyzed·
keywords), 그리고 본문에서 shields.io 배지와 KaTeX 수식 delimiter 가 제거되고 내부
식별자(`X-VLA_{AFM}` 등)는 보존됐는지.

## 2. 사용자 환경 라이브 실행

라이브 ingest/search 는 supermemory 서버가 필요하므로 **본인 환경**에서 돌린다.

### 2.1 서버 기동

```
npx supermemory local            # localhost:6767, 첫 부팅이 sm_... 키를 출력
```

- **임베딩 = 내장 로컬 고정.** 벡터는 기계에서 계산되고 외부로 나가지 않는다.
  WASM/CPU 기반이라 **GPU 불필요**. 임베딩 제공자를 바꾸는 경로는 없다
  (`SUPERMEMORY_LOCAL_EMBEDDING_*` 는 성능 노브일 뿐).
- **필수 키 = 생성 LLM 1개** — summaries / contextual chunking / memory extraction
  용. GPU 없는 환경에서는 `ANTHROPIC_API_KEY`(또는 `OPENAI_API_KEY` /
  `GEMINI_API_KEY` / `GROQ_API_KEY`) 하나를 넣는 게 현실적이다. 첫 부팅 마법사가
  대화식으로 받거나 환경변수로 준다. (완전 비유출을 원하면 로컬 CPU Ollama 로 생성
  LLM 을 돌릴 수 있으나 느리다.)
- cut 1 이 색인하는 analysis.md 는 **공개 논문 요약**이라, 생성 LLM 으로 호스티드
  키를 써도 유출 민감도가 낮다. 민감한 Decision Log 는 cut 2 이므로 그때 재검토.

### 2.2 색인 + 측정

```
# 첫 부팅이 출력한 키를 넣어 색인 (idempotent — customId upsert)
python3 scripts/supermemory_ingest.py --api-key sm_xxx

# 한글 회수 품질 측정
python3 scripts/supermemory_eval.py --api-key sm_xxx --top-k 10
```

`SUPERMEMORY_API_KEY` 환경변수로 키를 주면 `--api-key` 를 생략할 수 있다. 다른
서버 주소면 `--base-url` 로 바꾼다(호스티드 이전 시 여기만 교체).

## 3. §6 리스크 #1 게이트 — go/no-go

`supermemory_eval.py` 가 뱉는 `hit@1 / hit@3 / hit@5 / MRR` 을 읽고 판단한다.

- **회수 양호** → cut 2(Decision Log·Tracked Literature) 및 나머지 소스로 확장.
- **회수 부실** → 우리가 조정할 수 있는 변수는 **노이즈 스트립 강도**(`probe_corpus.strip_noise`)
  뿐이다. 임베딩 모델은 내장 로컬로 고정이라 교체가 불가하므로, 그래도 부족하면
  escalation 은 **호스티드 티어(전용 임베딩 모델, 설계문서 §5.2) 이전**이다 —
  `--base-url`/키 교체 수준의 마이그레이션.

측정은 서버가 필요하니 본인 환경에서만 나온다(샌드박스에서는 연결 실패가 정상).

## 4. 불변식 (반드시 유지)

- **SSOT 는 git + 마크다운.** supermemory 인덱스는 재생성 가능한 파생 캐시일 뿐
  권위가 아니다. 소스가 바뀌면 재수집하고, `customId`(`arxiv:<id>`)가 갱신을
  idempotent 하게 만든다.
- **`context/` 는 human read-only.** cut 1 은 `analysis/` 만 읽는다. 어떤 경로도
  `context/` 를 읽거나 되쓰지 않는다(cut 2 에서 결정로그를 읽더라도 읽기 전용).
- **임베딩 노이즈 제거.** Math/KaTeX·shields.io 배지는 수집 전 스트립한다
  (`docs/style.md` §5-6 규칙 참조).
