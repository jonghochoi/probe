# 🛸 Probe

> Automated research scouting for dexterous manipulation RL —
> citation-graph expansion, author watch, and arXiv triage
> distilled into weekly decision-grade Scouting Reports.

---

## 🧭 Why this exists

로보틱스 연구자의 하루는 이미 빡빡하다.
Isaac Lab 실험을 돌리고, 하드웨어를 디버깅하고, 결과를 분석하다 보면
**arXiv는 자연스럽게 뒤로 밀린다.**

문제는 arXiv `cs.RO` + `cs.LG`에 매일 50 ~ 100편이 새로 올라온다는 것이다.
그 중 *Hand-centric dexterous manipulation + Sim2Real*에 실제로 연관된 논문은
**주당 3 ~ 5편에 불과하다.**

비율은 3 ~ 5%다.

직접 필터링하면 주당 몇 시간을 쓴다. 그냥 포기하면 중요한 논문을 놓친다.
놓친 논문 때문에 이미 누군가 풀어놓은 문제를 다시 푸는 건
연구자 입장에서 가장 비싼 실수 중 하나다.

**Probe는 그 3 ~ 5%를 대신 찾아온다.**
그리고 "이 논문이 흥미롭다"가 아니라
**"이 논문이 맞다면 지금 Isaac Lab 파이프라인에서 무엇을 바꿔야 하는가"** 를 묻는다.
요약이 아니라 의사결정 재료를 만드는 것이 Probe의 역할이다.

---

## ⚙️ 파이프라인

```
                  ┌──────────────────────────────┐
                  │     research_context.md      │  ← 정적. 사람이 관리.
                  │  • Active Questions (Q1–Q5)  │
                  │  • Hypotheses (H1–H5)        │
                  │  • Pinned Literature (≤8)    │
                  │  • Researchers to Follow     │
                  │  • Anti-topics               │
                  └──────────────┬───────────────┘
                                 │ reads (every run)
                                 ▼
                  ┌──────────────────────────────┐
                  │         P R O B E            │
                  │       (Claude Agent)         │
                  │                              │
                  │  1. Author Watch             │  ← 가장 효율적
                  │  2. Citation-graph Expansion │  ← 의미 기반 탐색
                  │  3. Keyword Sweep            │  ← 보조 (노이즈 多)
                  │                              │
                  │  Score each candidate:       │
                  │  · Q#/H# relevance           │
                  │  · Novelty vs. pinned        │
                  │  · Reproducibility           │
                  │  · Sim2Real evidence         │
                  └──────────────┬───────────────┘
                                 │ writes
                                 ▼
                  ┌──────────────────────────────┐
                  │  research_log/YYYY-W##.md    │  ← Scouting Report
                  │                              │
                  │  Top 3–5 papers only         │
                  │  • Connects to: Q# / H#      │
                  │  • What's genuinely new      │
                  │  • Decision implication      │  ← 핵심
                  │  • Failure mode to probe     │  ← 핵심
                  └──────────────┬───────────────┘
                                 │ informs
                                 ▼
                  ┌──────────────────────────────┐
                  │           Human              │
                  │                              │
                  │  · Read, judge, discard      │
                  │  · Update context.md (월 1회) │
                  │  · Record feedback (월 1회)   │
                  └──────────────────────────────┘
```

---

## 🧑‍🔬 인간이 집중해야 할 것

Probe는 탐사선이다. 전투는 하지 않는다.
인간의 판단이 개입해야 하는 지점은 명확하다:

| 역할 | 구체적 행동 |
|---|---|
| **방향 설정** | Active Questions의 우선순위 결정 (Q1이 정말 가장 중요한가?) |
| **가설 정제** | 에이전트가 찾아온 논문이 H# 중 하나를 흔들면, 가설을 수정 또는 강화 |
| **평가 프로토콜** | Sim2real gap을 측정할 객관적 기준을 정의 (없으면 어떤 리포트도 의미 없음) |
| **맥락 갱신** | 월 1회 `research_context.md` 업데이트 — 실험 결과, 방향 전환, 새 가설 반영 |
| **피드백 루프** | Scouting Report를 실제로 읽고, 실험 설계에 반영된 것을 기록 |

> "에이전트가 잘 작동하고 있는가"는 에이전트 스스로 판단할 수 없다.
> Section 9 (Feedback Loop)를 매월 채우는 것이 유일한 측정 수단이다.

---

## 🤖 에이전트가 집중하는 것

인간이 하기엔 반복적이고, 실수가 잦고, 시간이 아까운 것들:

| 태스크 | 방법 |
|---|---|
| **Author watch** | Pinned 연구자의 최근 14일 arXiv 제출 감시 |
| **Citation-graph expansion** | Pinned literature를 인용한 신규 논문 탐색 (키워드 없이 의미 기반) |
| **Keyword sweep** | cs.RO + cs.LG 검색, Anti-topics 필터 적용 |
| **Scoring** | Q#/H# 연관성, 재현 가능성, Sim2Real 증거 점수화 |
| **Anti-topic filtering** | 모바일 매니퓰레이션·로코모션·parallel gripper 등 자동 제거 |
| **Cross-pollination** | 월 1회 인접 분야(접촉 최적화, 촉각 신경과학 등)에서 강제 1편 픽업 |
| **Self-check** | 지난 2주 로그와 중복 여부, Anti-topics 필터 적용 횟수 자체 검증 |

에이전트가 **절대 하지 않는 것**: `research_context.md` 수정.
Scouting Report 말미에 *수정 제안*만 하고, 실제 반영은 사람이 결정한다.

---

## 🗂️ 파일 구조

```
probe/
├── README.md
├── research_context.md        # 정적 컨텍스트. 사람이 관리.
└── research_log/
    ├── _TEMPLATE.md           # 에이전트가 매주 복사해서 채우는 양식
    ├── YYYY-W##.md            # 실제 Scouting Reports (에이전트 생성)
    └── 2026-W16_EXAMPLE.md    # 출력 품질 기준 예시 (실운영 전 삭제)
```

### 핵심 원칙: 정적 vs 동적 분리

`research_context.md`와 `research_log/`를 **절대 섞지 않는다.**
모든 것을 한 파일에 쌓으면 6주 안에 context가 부풀어
에이전트가 이미 다뤘던 논문을 재추천하거나 오래된 pinned literature를 망각한다.

- **Pinned literature: 최대 8편.** 추가만 하지 말고, 교체 기준으로 관리.
- **Active Questions: 5개 고정.** 늘리면 scoring이 희석된다.
- **Scouting Report: 직전 2주 로그만 읽는다.** 그 이전은 에이전트 context에서 제외.

---

## 🛠️ 운영 노하우

### 자동화 전에 수동 실행부터

자동화 → 나쁜 프롬프트 → 매주 쓰레기 로그 자동 생성.
**반드시 수동 실행 1 ~ 2주로 프롬프트를 검증한 뒤** Routine에 등록한다.

수동 실행: 새 Claude 대화 → `research_context.md` 업로드 → 에이전트 프롬프트 실행 → 결과 검토 → 프롬프트 수정 반복.

### 초반에 반드시 나타나는 문제 3가지

| 증상 | 원인 | 처방 |
|---|---|---|
| 추천 논문이 Anti-topic에 가까움 | Anti-topics 목록이 느슨함 | 더 공격적으로 구체화 |
| Decision implication이 generic ("DR range를 넓혀야 함") | 프롬프트가 약함 | "구체적 Isaac Lab config 변경을 지목하라" 강화 |
| 같은 논문이 매주 재추천됨 | 이전 로그를 읽지 않음 | 직전 2주 로그를 read-only로 첨부하는 프로세스 추가 |

### Probe가 잘 작동하고 있다는 신호

- 매주 3~5편 중 최소 1편이 현재 실험 설계에 구체적인 변화를 유발한다
- Anti-topics 필터가 매주 10편 이상 걸러내고 있다 (그게 정상 비율)
- 에이전트가 "이번 주 score ≥3 논문 없음"이라고 솔직하게 보고한다 (패딩 없이)

### Echo chamber 방지

Citation-graph만 쓰면 본인 관심사 주변에서만 맴돈다.
`research_context.md` Section 8의 Cross-pollination 로테이션이 이를 막는다.
월 1회 인접 분야(접촉 최적화, FEM 시뮬레이션, 촉각 신경과학 등)에서
강제로 1편을 픽업하는 것이 의외로 가장 가치 있는 발견의 소스가 된다.

---

## 🔁 실행 유지 방법

### 3단계 점진적 전환

```
Week 1–2:  수동 실행     새 대화 → context.md 업로드 → 프롬프트 실행
Week 3–4:  반자동화      Claude Cowork Scheduled Task (데스크톱 앱 오픈 시)
Week 5+:   완전 자동화   Claude Code Routines (클라우드, 노트북 꺼도 실행)
```

### Claude Code Routines 설정 (Week 5+)

```yaml
name: probe-weekly-scout
trigger:
  cron: "0 9 * * 1,4"          # 월/목 오전 9시 (주 2회)
  timezone: Asia/Seoul
mcp_servers:
  - arxiv-mcp-server
  - semantic-scholar-fastmcp
output:
  - path: research_log/YYYY-W##.md
    via: github-pr             # git log = research history
```

> Pro 플랜: 5회/일 한도. 주 2회 실행이면 충분히 여유 있음.

### 지속 가능성의 핵심: 월간 리뷰

자동화됐다고 방치하면 에이전트가 잘 작동하는지 알 수 없다.
`research_context.md` Section 9 (Feedback Loop)를 월 1회 직접 채운다.

| 채울 것 | 질문 |
|---|---|
| Papers surfaced | 이번 달 Probe가 올린 총 논문 수 |
| Actually read | 실제로 정독한 것 |
| Influenced a decision | 실험 설계나 가설 수정에 반영된 것 |

이 세 숫자의 **비율**이 Probe의 실효성 지표다.
3개월마다 "내 Q1–Q5에 대한 생각이 실제로 바뀌었는가?"를 자문한다.
바뀌지 않았다면 retrieval 파이프라인을 재점검한다.

---

## 🧱 에이전트 스택

| 컴포넌트 | 기술 |
|---|---|
| **에이전트 엔진** | Claude (Sonnet) via Claude Code Routines |
| **스케줄러** | Claude Code Routines — cloud-managed cron, GitHub webhook 지원 |
| **논문 검색** | `blazickjp/arxiv-mcp-server` — arXiv search + topic-watch + citation-graph |
| **인용 추적** | `zongmin-yu/semantic-scholar-fastmcp` — citation/reference graph, author search |
| **출력 저장** | GitHub PR (자동) — 변경 이력 = 리서치 로그 |
| **컨텍스트 관리** | `research_context.md` (정적, 사람 관리) + `research_log/` (동적, 에이전트 생성) |

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
