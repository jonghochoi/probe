# 🛸 Probe

> Automated research scouting for dexterous manipulation —
> citation-graph expansion, author watch, and arXiv triage
> distilled into weekly Scouting Reports, monthly synthesis
> briefs, and on-demand deep-dives with reproduction patches.

---

## 🧭 Why this exists

로보틱스 연구자의 하루는 이미 빡빡하다.
모델을 학습시키고, 하드웨어를 디버깅하고, 결과를 분석하다 보면
**arXiv는 자연스럽게 뒤로 밀린다.**

문제는 arXiv `cs.RO` + `cs.LG`에 매일 50 ~ 100편이 새로 올라온다는 것이다.
그 중 *Hand-centric dexterous manipulation + Sim2Real*에 실제로 연관된 논문은
**주당 3 ~ 5편에 불과하다.**

비율은 3 ~ 5%다.

직접 필터링하면 주당 몇 시간을 쓴다. 그냥 포기하면 중요한 논문을 놓친다.
놓친 논문 때문에 이미 누군가 풀어놓은 문제를 다시 푸는 건
연구자 입장에서 가장 비싼 실수 중 하나다.

**Probe는 그 3 ~ 5%를 대신 찾아온다 — 그리고 다운로드 폴더에서 죽게 두지 않는다.**
"이 논문이 흥미롭다"가 아니라
**"이 논문이 맞다면 지금 내 학습·평가 파이프라인에서 무엇을 바꿔야 하는가"** 를 묻고,
요약이 아니라 **세 갈래로 의사결정 재료**를 만든다 — outward (찾기), inward (압축), focused (재현):

- **주간 Scouting Report** (outward) — 월·목, pillar 별 3 ~ 5편. 점수화된 후보 + 너의 open question 에 묶인 decision implication.
- **월간 Synthesis Brief** (inward) — pillar 별 핀된 문헌(§6 8편)이 시간이 지나면 머릿속에서 흐려지는 걸 막는다. 짧고 정직한 산문 압축.
- **온디맨드 Analysis + Foundry + Verify** (focused) — `/analyze-paper` 가 한 편을 한국어 deep-dive + Layer 1 Design (vendor-agnostic) 으로 읽고, `/foundry` 가 그 Design 을 target foundry (기본 `lerobot`) 좌표계로 매핑한 unified diff 패치를 떠먹여 주며, `/verify` 가 Design + 패치 + 분석 문서를 정적 대조해 검증 보고서를 만든다.

---

## 🧭 파이프라인

PROBE 는 **하나의 정적 컨텍스트를 공유하는 세 갈래의 산출물**입니다 — outward (`scouting/`), inward (`synthesis/`), focused (`analysis/`). 각 갈래는 서로 다른 질문에 답하고, 서로 다른 주기로 돌고, 자기 폴더에 씁니다. 셋이 합쳐져 연구 로그를 정직하게 유지합니다. 네 번째 트랙 **`pulse/`** (PoC) 는 채팅→스카우트 *입력 보조* 레이어로, 사람이 읽는 산출물이 아닙니다 — 다이어그램 직후 사이드바에서 설명합니다.

> **Pillars**: P1 Heterogeneous Body/Hand Action Expert · P2 Structured Input-Modality Binding · P3 Hand-level System0 · P4 VLM Pretraining Preservation · P5 Task Definition & Falsifiable Evaluation — 정본 정의는 [`context/MASTER.md`](../context/MASTER.md) §5.
>
> **Full doc vs. per-pillar extract**: `context/MASTER.md` 는 다섯 pillar 전체(Decision Log 포함)의 단일 진실원입니다. `context/P{1..4}.md` 각 파일은 그 중 한 pillar 를 §1–§9 동일 골격으로 좁혀낸 history-free 추출본이며, 클라우드 scouting/synthesis 루틴은 **추출본 하나만** 읽어 컨텍스트를 가볍고 pillar-focused 하게 유지합니다. 풀 문서를 편집하고 추출본을 재생성하세요 — 역방향 금지.

```
   ┌───────────────────────────────────────────────────────────────────┐
   │ context/  (static · human-owned · read-only every run)            │
   │                                                                   │
   │ MASTER.md   · Identity / Pillars (P1–P5) / Decision Log (D1–D26)  │
   │             · Tracked Literature (5 × 8) / Researchers /          │
   │               Competitor Monitoring / Anti-topics                 │
   │ P{1..4}.md  · per-pillar history-free extracts (§1–§9 skeleton)   │
   └─────────────────────────────────┬─────────────────────────────────┘
                                     │ read-only (every run)
                                     ▼
   ┌───────────────────────────────────────────────────────────────────┐
   │                             P R O B E                             │
   └───────────┬─────────────────────┬──────────────────────┬──────────┘
               │                     │                      │
               ▼                     ▼                      ▼
   ┌─────────────────────┐ ┌────────────────────┐ ┌────────────────────┐
   │   OUTWARD           │ │   INWARD           │ │   FOCUSED          │
   │   Weekly Scouting   │ │   Monthly Synth.   │ │   On-demand Anal.  │
   │                     │ │                    │ │                    │
   │   Mon/Thu · per P#  │ │   monthly · per P# │ │   /analyze-paper   │
   │                     │ │                    │ │                    │
   │ · Author Watch      │ │ · compress the     │ │ · one paper —      │
   │ · Citation-Graph    │ │   pinned set       │ │   full-text first  │
   │ · Keyword Sweep     │ │ · connect dots:    │ │ · neutral summary  │
   │ · Competitor watch  │ │   D# ↔ §6 pins     │ │   + decision-      │
   │                     │ │                    │ │   grade implic.    │
   │ in: P#.md +         │ │ in: P#.md §4 + §6  │ │ in: MASTER.md      │
   │     last ~2 wk      │ │     (D# + pins)    │ │     + paper body   │
   │                     │ │                    │ │                    │
   │ curl: arXiv + S2    │ │ no retrieval —     │ │ curl: arxiv/html   │
   │                     │ │ static compress    │ │ → ar5iv → abstract │
   └──────────┬──────────┘ └─────────┬──────────┘ └─────────┬──────────┘
              │ writes new           │ overwrites           │ overwrites
              ▼                      ▼                      ▼
   ┌─────────────────────┐ ┌────────────────────┐ ┌────────────────────┐
   │ scouting/           │ │ synthesis/         │ │ analysis/          │
   │ YYYY-MM-DD-P#.md    │ │ P{1..4}_BRIEF.md   │ │ <arxiv-id>.md      │
   │                     │ │                    │ │                    │
   │ 3–5 papers, scored, │ │ living per-pillar  │ │ single Korean      │
   │ decision-grade KO   │ │ narrative brief    │ │ deep-dive doc      │
   └──────────┬──────────┘ └─────────┬──────────┘ └─────────┬──────────┘
              │                      │                      │
              └──────────────────────┼──────────────────────┘
                                     │ informs
                                     ▼
                    ┌─────────────────────────────────┐
                    │             Human               │
                    │                                 │
                    │  · Read, judge, discard         │
                    │  · Update context (monthly)     │
                    │  · Log feedback   (monthly)     │
                    └─────────────────────────────────┘
```

### 사이드바: pulse — 채팅→스카우트 입력 보조 (PoC)

`pulse/` 는 위 OUTWARD 컬럼의 사이드카이지 4번째 peer 가 아닙니다. 팀 채팅 export 를 짧은 pillar별 힌트 파일로 증류해, 다음 `scouting/` 실행의 retrieval-weight nudge 로만 작동합니다. 정적 `context/` 가 충돌 시 항상 승리하며, pulse 는 어떤 `context/` 파일도 수정하지 않습니다.

```
   pulse/inbox/      ──►  .claude/prompts/      ──►  pulse/YYYY-MM-DD-P#.md
   (채팅 export,          pulse-digest.md            (pillar별 힌트,
    gitignored)           (수동, ~주 1회)             실행당 최대 4개 파일)
                                                              │
                                                              ▼
                                                    scouting/ retrieval
                                                    (nudge 전용)
```

상태: Tier A PoC — 수동, 자동화 없음, 2주 trial. 스키마는 [`pulse/README.md`](../pulse/README.md), 채팅 export 운영 가이드는 [`pulse/EXPORT_GUIDE_KO.md`](../pulse/EXPORT_GUIDE_KO.md) 참조.

### 사이드바: foundry + verify — 분석 후속 구현·검증 (on-demand)

위 FOCUSED 컬럼의 후속 트랙입니다. `/analyze-paper` 가 "왜 / 무엇을"이라면, `/foundry` 가 "어디를 / 어떻게"를 채우고 `/verify` 가 "정합한가"를 따집니다. 두 층 모델로 분리되어 있습니다 — Layer 1 Design (vendor-agnostic) 은 `/analyze-paper` 가 분석 문서와 함께 산출하며, Layer 2 매핑은 `/foundry analysis/<id>_design.md [--foundry <name>]` 가 target foundry (기본 `lerobot`) 좌표계로 옮겨 `analysis/<id>_impl/<foundry>/impl.md` + `impl.patch` 를 산출합니다. baseline 은 foundry 의 byte-stable 스냅샷 (lerobot 의 경우 `vendor/lerobot/`) 에 보관되며, 패치는 그 스냅샷에 `git apply --check` 로 검증됩니다. Design 이 foundry 좌표계로 매핑되지 않으면 `UNMAPPABLE.md` 와 분석 문서 말미의 `> 🚧 매핑 불가 (<foundry>) — …` 한 줄만 남깁니다 — Design 자체는 항상 산출됩니다. `/verify analysis/<id>_design.md [--foundry <name>]` 는 Design + 패치 + 분석 문서를 4 단계 정적 체크 (📚 문헌 · 🔍 패치 · 🧪 시그니처 · 📐 식·표) 로 대조해 `analysis/<id>_verify/<foundry>.md` 를 산출합니다. 분석 트랙은 manifest 라이프사이클이 없으므로 보고서 자체가 산출물입니다. 자세한 형식은 [`docs/STYLE_GUIDE.md`](STYLE_GUIDE.md) §6 / §7, foundry 스냅샷 갱신 절차는 [`vendor/lerobot/README.md`](../vendor/lerobot/README.md) 참조.

### 핵심 원칙: 정적 vs 동적 분리

`context/` (정적)와 산출물 트랙들(동적) 사이의 분리는 단 하나의 이유로 존재합니다 — 에이전트 컨텍스트를 가볍게 유지하기 위해서입니다.

- **정적** (`context/`) — 월 단위로 한 번 정도 바뀝니다. 에이전트는 *읽기만* 하고, 절대 쓰지 않습니다.
- **동적** — 에이전트가 씁니다. `scouting/` 는 append-only 입니다 (실행마다 pillar별 새 dated 파일 1개; 다음 실행은 해당 pillar 의 직전 ~2주분만 읽습니다). `synthesis/` 와 `analysis/` 는 매 실행마다 덮어쓰는 living snapshot 입니다 — 이력 없음, 필요 시 재생성. `pulse/` (PoC 사이드카) 는 scouting 의 파일명 컨벤션을 따르되, 힌트 파일이 사람이 아닌 다음 `scouting/` 실행으로 흘러갑니다.

모든 것을 한 파일에 쌓으면 몇 주 안에 context 가 부풀어 에이전트가 이미 다뤘던 논문을 재추천하거나 핀된 literature 가 망각됩니다.

---

## 🗂️ 파일 구조

```
probe/
│
├── CLAUDE.md                       # 기여 규칙 — commit & 문서 스타일
├── README.md                       # ← 대문
├── brand.py                        # ASCII 아트, sigil, 컬러 상수
│
├── context/                        # 정적 입력 — 사람이 관리
│   ├── MASTER.md                   #   단일 진실원 (P1–P5):
│   │                               #   Identity, Pillars, Decision Log,
│   │                               #   Tracked Literature,
│   │                               #   Competitor / Researchers / Anti-topics
│   └── P{1..4}.md                  #   pillar별 history-free 추출본 —
│                                   #   §1–§9 동일 골격; 파이프라인은
│                                   #   추출본 하나만 읽음
│
├── .claude/
│   ├── prompts/                    # 외부화된 에이전트 프롬프트
│   │   ├── scouting-P{1..4}.md     #   주간 스카우트 (pillar별 1개)
│   │   ├── synthesis-P{1..4}.md    #   월간 synthesis brief
│   │   ├── paper-analysis.md       #   온디맨드 단일 논문 심층분석
│   │   │                           #     + Layer 1 Design (vendor-agnostic)
│   │   ├── hypothesize.md          #   가설 + Layer 1 Design
│   │   ├── foundry.md              #   Design → foundry 별 구현 패치
│   │   ├── verify.md               #   Design + 패치 정적 검증
│   │   └── pulse-digest.md         #   채팅 → pillar별 힌트 (PoC)
│   └── commands/                   # 슬래시 커맨드 (온디맨드)
│       ├── analyze-paper.md        #   /analyze-paper <id|url|pdf>
│       ├── hypothesize.md          #   /hypothesize <P# | analysis-slug>
│       ├── foundry.md              #   /foundry <design-path> [--foundry <n>]
│       └── verify.md               #   /verify <design-path> [--foundry <n>]
│
├── scouting/                       # 동적 산출 — 주간 (월·목)
│   ├── README.md                   #   파이프라인 요약
│   ├── _TEMPLATE.md                #   Scouting Report 양식
│   └── YYYY-MM-DD-P#.md            #   한글 리포트 — 실행·pillar별 1개
│
├── pulse/                          # 채팅→스카우트 입력 보조 (PoC 사이드카)
│   ├── README.md                   #   목적 + Tier A 상태
│   ├── _TEMPLATE.md                #   힌트 스키마 (pillar별)
│   ├── _EXAMPLE.md                 #   참조 예시
│   ├── EXPORT_GUIDE_KO.md          #   Slack / Telegram export 운영 가이드
│   ├── inbox/                      #   원시 채팅 export (README 외 gitignored)
│   │   └── README.md
│   └── YYYY-MM-DD-P#.md            #   pillar별 힌트 — 수동 ~주 1회
│
├── synthesis/                      # 월간 종합 산출
│   ├── README.md                   #   파이프라인 요약
│   └── P{1..4}_BRIEF.md            #   pillar별 living narrative (재생성)
│
├── analysis/                       # 단일 논문 심층 (온디맨드)
│   ├── README.md                   #   목적 + 파일명 컨벤션
│   ├── _TEMPLATE.md                #   한글 deep-dive 양식
│   ├── _TEMPLATE_DESIGN.md         #   한글 Layer 1 Design 양식
│   ├── _TEMPLATE_IMPL.md           #   한글 foundry-impl 가이드 양식
│   ├── <arxiv-id>.md               #   단일 한글 분석 (재생성)
│   ├── <arxiv-id>_design.md        #   Layer 1 Design (vendor-agnostic)
│   ├── <arxiv-id>_impl/<foundry>/  #   foundry별 서브폴더
│   │   ├── impl.md                 #     foundry-specific 구현 가이드
│   │   └── impl.patch              #     foundry baseline 대비 unified diff
│   └── <arxiv-id>_verify/<foundry>.md  #   정적 검증 보고서
│
├── experiments/                    # 팀 내부 가설 사이클 (온디맨드)
│   ├── README.md                   #   목적 + 파일명/상태 전이
│   ├── _TEMPLATE_H.md              #   한글 가설 양식
│   ├── _TEMPLATE_D.md              #   한글 Layer 1 Design 양식
│   ├── _TEMPLATE_I.md              #   한글 foundry-impl 가이드 양식
│   ├── _TEMPLATE_V.md              #   한글 검증 보고서 양식
│   └── H###-<slug>/                #   가설 1개당 폴더 1개
│       ├── H###.md                 #     가설 (작성 후 불변)
│       ├── D###.md                 #     Layer 1 Design (불변)
│       ├── I###/<foundry>/         #     foundry별 서브폴더
│       │   ├── impl.md, impl.patch #       impl 가이드 + diff (재생성)
│       ├── V###/<foundry>.md       #     검증 보고서 (재생성)
│       └── manifest.yaml           #     foundry-keyed impl/validation
│
├── vendor/                         # 읽기 전용 외부 코드
│   └── lerobot/                    #   pinned lerobot 스냅샷 —
│                                   #   6개 baseline policy + configs,
│                                   #   v0 foundry (foundry=lerobot 의
│                                   #   impl.patch 적용 대상)
│
└── docs/
    ├── INTRO_KO.md                 # 한글 온보딩 + 운영 매뉴얼
    ├── STYLE_GUIDE.md              # 산출물 포맷 규칙 (이모지, 링크,
    │                               #   한글 작성) — 리포트 SSOT
    └── LOGO.png                    # 프로젝트 로고
```

---

## 🧑‍🔬 인간이 집중해야 할 것

Probe는 탐사선이다. 전투는 하지 않는다.
인간의 판단이 개입해야 하는 지점은 명확하다:

| 역할 | 구체적 행동 |
|---|---|
| **방향 설정** | Identity 명제 점검 + Pillar 우선순위 결정 (최우선 Pillar 가 여전히 맞는가?) |
| **Decision 정제** | 에이전트가 찾아온 논문이 어떤 Decision 의 default 를 흔들거나 deferred 트리거를 점등시키면, 해당 Decision 을 Decision Log 에서 업데이트 |
| **평가 프로토콜** | 현재 Decision Log 가 정의한 falsifier 임계값·메트릭을 유지·강화 — 없으면 어떤 리포트도 의미 없음 |
| **맥락 갱신** | Revisit Checkpoint 도래 시 `context/MASTER.md` 업데이트 — 실험 결과, deferred 트리거, 새 evidence 반영 |
| **피드백 루프** | Scouting Report 를 실제로 읽고, 실험 설계에 반영된 것을 기록 |

> "에이전트가 잘 작동하고 있는가"는 에이전트 스스로 판단할 수 없다.
> `context/MASTER.md` 의 Feedback Loop 섹션을 매월 채우는 것이 유일한 측정 수단이다.

---

## 🤖 에이전트가 집중하는 것

인간이 하기엔 반복적이고, 실수가 잦고, 시간이 아까운 것들:

| 태스크 | 방법 |
|---|---|
| **Author watch** | Researchers 리스트의 최근 arXiv 제출 감시 |
| **Citation-graph expansion** | Tracked Literature anchor 들을 인용한 신규 논문 탐색 (키워드 없이 의미 기반) |
| **Keyword sweep** | cs.RO + cs.LG 검색, Anti-topics 필터 적용 |
| **Competitor monitoring** | Competitor watch list 의 신규 릴리스 점검 |
| **Scoring** | Pillar / Decision 연관성, Identity 정합/긴장, 재현 가능성, Sim2Real 증거 점수화 |
| **Anti-topic filtering** | Anti-topics 리스트가 배제하는 항목 자동 제거 |
| **Cross-pollination** | Cross-pollination 로테이션에서 주기적으로 강제 1편 픽업 |
| **Self-check** | 직전 2주 로그와 중복 여부, Anti-topics 필터 적용 횟수 자체 검증 |

에이전트가 **절대 하지 않는 것**: `context/MASTER.md` 수정.
Scouting Report 말미에 *수정 제안*만 하고, 실제 반영은 사람이 결정한다.

---

## 🛠️ 운영 노하우

### 자동화 전에 수동 실행부터

자동화 → 나쁜 프롬프트 → 매주 쓰레기 로그 자동 생성.
**반드시 수동 실행 1 ~ 2주로 프롬프트를 검증한 뒤** Routine에 등록한다.

수동 실행: 새 Claude 대화 → `context/MASTER.md` 업로드 → 에이전트 프롬프트 실행 → 결과 검토 → 프롬프트 수정 반복.

### 초반에 반드시 나타나는 문제 3가지

| 증상 | 원인 | 처방 |
|---|---|---|
| 추천 논문이 Anti-topic에 가까움 | Anti-topics 목록이 느슨함 | 더 공격적으로 구체화 |
| Decision implication이 generic ("DR range를 넓혀야 함") | 프롬프트가 약함 | "구체적 config 키 / 하이퍼파라미터 / 메트릭을 지목하라" 강화 |
| 같은 논문이 매주 재추천됨 | 이전 로그를 읽지 않음 | 직전 2주 로그를 read-only로 첨부하는 프로세스 추가 |

### Probe가 잘 작동하고 있다는 신호

- 매주 3~5편 중 최소 1편이 현재 실험 설계에 구체적인 변화를 유발한다
- Anti-topics 필터가 매주 10편 이상 걸러내고 있다 (그게 정상 비율)
- 에이전트가 "이번 주 score ≥3 논문 없음"이라고 솔직하게 보고한다 (패딩 없이)

### Echo chamber 방지

Citation-graph만 쓰면 본인 관심사 주변에서만 맴돈다.
`context/MASTER.md` 의 Cross-pollination 로테이션 섹션이 이를 막는다.
월 1회 인접 분야(접촉 최적화, FEM 시뮬레이션, 촉각 신경과학 등)에서
강제로 1편을 픽업하는 것이 의외로 가장 가치 있는 발견의 소스가 된다.

---

## 🔁 실행 유지 방법

### 3단계 점진적 전환

```
Week 1–2:  수동 실행     새 대화 → context.md 업로드 → 프롬프트 실행
Week 3–4:  반자동화      Claude Desktop Scheduled Tasks (데스크톱 앱 오픈 시)
Week 5+:   완전 자동화   Claude Code Routines (클라우드, 노트북 꺼도 실행)
```

### Claude Code Routines 설정 (Week 5+)

루틴은 `.claude/routines/*.yaml` 로 자동 등록되지 **않습니다.** 실제
스케줄링은 [claude.ai/code/routines](https://claude.ai/code/routines)
의 **RemoteTrigger 폼**(또는 CLI `/schedule`)으로 만듭니다 — 폼에
`.claude/prompts/scouting-P#.md` 전문을 붙여넣고, 레포·스케줄(월·목
09:00)·환경을 지정합니다. 클라우드 루틴은 로컬 MCP 서버에 도달할 수
없으므로 검색은 **MCP가 아니라 `curl`로 공개 REST API**(arXiv
`export.arxiv.org` + Semantic Scholar Graph)를 직접 호출합니다. 환경의
**Network access = Custom** 으로 두 도메인을 허용해야 하며,
`SEMANTIC_SCHOLAR_API_KEY` 는 환경변수(선택)입니다. 단계별 절차·검증·
트러블슈팅은 `README.md` §Agent Setup Guide → Stage 3 를 따릅니다.

> Pro 플랜: 일일 한도가 주 2회 실행을 충분히 커버합니다.

### 지속 가능성의 핵심: 월간 리뷰

자동화됐다고 방치하면 에이전트가 잘 작동하는지 알 수 없다.
`context/MASTER.md` 의 Feedback Loop 섹션을 월 1회 직접 채운다.

| 채울 것 | 질문 |
|---|---|
| Papers surfaced | 이번 달 Probe가 올린 총 논문 수 |
| Actually read | 실제로 정독한 것 |
| Influenced a decision | 실험 설계나 Decision Log 수정에 반영된 것 |

이 세 숫자의 **비율**이 Probe의 실효성 지표다.
3개월마다 "내 Identity 명제 또는 어느 Pillar에 대한 생각이 실제로 바뀌었는가?"를 자문한다.
바뀌지 않았다면 retrieval 파이프라인을 재점검한다.
추가로 매 Checkpoint마다 Competitor 동향과 Decision Log 의 deferred 트리거를 함께 점검한다.

---

## 🧱 에이전트 스택

| 컴포넌트 | 기술 |
|---|---|
| **에이전트 엔진** | Claude (Sonnet 4.6 / Opus 4.7) via Claude Code Routines |
| **스케줄러** | Claude Code Routines — cloud-managed cron, GitHub webhook 지원 |
| **논문 검색** | arXiv REST API (`export.arxiv.org/api/query`, Atom XML) — `curl` 직접 호출 |
| **인용 추적** | Semantic Scholar Graph API (`api.semanticscholar.org/graph/v1`, JSON `jq`) — 키 선택 |
| **출력 저장** | `main` 직접 push (PR 없음) — 변경 이력 = 리서치 로그 |
| **컨텍스트 관리** | `context/MASTER.md` (정적, 사람 관리) + `scouting/` (동적, 에이전트 생성) |

---

## 🔗 관련 프로젝트

| 프로젝트 | 역할 |
|---|---|
| **[nexus](https://github.com/jonghochoi/nexus)** | Centralized RL experiment log management — TensorBoard + MLflow dual logging |
| **[observer](https://github.com/jonghochoi/observer)** | Automated evaluation pipeline — multi-view recording, failure mode classification, checkpoint ranking |
| **probe** | Research scouting — 위 두 프로젝트가 "무엇을 실험할지"를 결정하기 전의 upstream |

> `probe` → `nexus` → `observer` 는 하나의 연구 루프다.
> Probe가 발굴한 아이디어가 Nexus에서 실험되고, Observer로 평가된다.

---

<div align="center">

*"It doesn't read papers for you.*
*It scouts which papers change your mind."*

</div>
