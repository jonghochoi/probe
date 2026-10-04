# Scouting Report Authoring Guide
> **Scope:** every `scouting/P#/YYYY-MM-DD.md` — the dated reports the
> scheduled routine writes — the run file `scouting/runs/YYYY-MM-DD.md` beside
> them (§8), and the skeletons in `scouting/templates/`.
> This document is the single source of truth for that format.
> `.claude/prompts/scout.txt` owns the *procedure* (retrieval, evidence,
> commit) and defers to this file for the output contract, the rubric
> included. Change a rule here first, then the prompt.

---

## 1. Output File Convention

One run covers the pillars it was asked for and writes **one Korean file per
pillar**, `scouting/P#/YYYY-MM-DD.md` — the pillar and the run date — plus one
run file for the run as a whole (§8). The run lands as one commit. There is
no English twin: titles, arXiv links and `P#/D#` tags stay verbatim (§4-1),
which is what de-duplication across reports keys on.

The reading site publishes the reports by date: every pillar's report of one
run date on one page, one row per arXiv id (`site/builder/scouting.py`). A
paper several pillars surfaced is one row with each pillar's rank and reading
side by side, and the run file's synthesis heads the page. The page orders
the rows by score and prints none of them (§5-3).

---

## 2. Emoji System and Section Headers

Every `##` header opens with one emoji from §2-1; §2-3 holds the rules.

### 2-1. Scouting report `##` sections

The table fixes the emoji, the exact Korean header text and the canonical
**section order** (top to bottom): papers and scores up top, the run-over-run
synthesis last.

| Emoji | `##` header (verbatim) | Holds | Rules |
|-------|------------------------|-------|-------|
| 🔑 | `## 🔑 참조 약어 풀이` | Reference Legend — the `P#` / `D#` codes this report cites | §3-1 |
| 🥇 🥈 🥉 | `## 🥇 논문 N` | The top three surfaced papers, one medal each and each medal at most once. The medal is the paper's rank (§5-3) and the header carries nothing after `논문 N` | §3, §5-1, §5-3 |
| 🌱 | `## 🌱 논문 N — 인접 분야 픽` | The cross-pollination pick — an adjacent-field paper, scored on the same rubric and carrying the same label | §5 |
| 📋 | `## 📋 기준 통과 · 추가 후보` | Every further surfaced paper, ranked below 🥉 — one table row each | §5-1 |
| 🔍 | `## 🔍 근접 후보` | Near-Miss Candidates — this run's papers one gate axis short | §5-5 |
| 🔄 | `## 🔄 직전 리포트 대비 종합` | Run-over-Run Synthesis — this run against the recent reports | §7-1 |

The run file has two `##` sections of its own, `## 🧭 회차 종합` and
`## 📐 논문 판정`, in that order (§8); the rules below bind them too.

### 2-2. Subsection (`###`) headers

Every paper section (🥇 🥈 🥉 🌱) carries the same four subsections, read as one
story — tie → what the paper is → what it means for us → what to check:

| `###` header (verbatim) | Holds |
|-------------------------|-------|
| `### (a) 관련 Pillar / Decision` | The badge line only (§3-1) |
| `### (b) 논문 요지` | The paper brief — a headline and the six labelled fields below |
| `### (c) 시사점` | What it could mean for us, in plain terms (`공개 기준점 확보`, `도입 비용 낮음`) |
| `### (d) 먼저 확인할 점` | The paper's own limits and the cheapest transfer caveat |

**(b) and (c) open on a headline.** Their first bullet is the whole point in
one line — about 40 characters and never more than 50 — and the bullets
after it carry the detail. The site prints the two headlines where a reader
scans: (b)'s on the paper's closed row, (c)'s as the pillar's line under
`연구 축별로 왜`, each cut to two lines and opening to the rest. A headline
that needs a clause for its evidence moves the evidence to the next bullet.

#### The paper brief

A reader deciding whether to open a paper asks the same questions of every
one: what problem, what was wrong with what came before, how this paper
answers, what sets it apart, what it showed, and why it matters. (b) answers
them in that order, one labelled field each, so the answers sit in the same
place in every paper and the site can lay them out as one card:

| Label (verbatim) | Answers | Where the paper says it |
|------------------|---------|-------------------------|
| `**문제**` | The problem the authors set out to solve, and why it is a problem | The introduction's opening paragraphs |
| `**기존 한계**` | Which existing approaches the authors argue against, and what each gets wrong or leaves out | "However, …", "existing methods …", the related-work paragraph of the introduction |
| `**핵심 방법**` | How the paper answers — its components and how they connect, not the name alone | "We propose …", the method overview |
| `**차별점**` | The design choice that separates it from the closest prior approach, and why that choice matters | "Unlike …", "rather than …", "without …" |
| `**핵심 기여**` | Every contribution the paper lists — each result with its numbers and setting, each released artifact | The introduction's contribution list, the abstract's results |
| `**가치**` | What the field gains if the claims hold — the paper's worth, read from the paper alone | The introduction's closing paragraph, the conclusion |

- **Fixed labels, fixed order.** Each field is one top-level bullet,
  `- **문제** — …`, after the headline and in the table's order. No label is
  added, dropped, renamed or repeated.
- **Depth, not a cap.** A field opens with its answer in one line, and nested
  `-` sub-bullets carry what the paper gives to back it — the prior
  approaches by name and what each misses, the method's components, every
  listed contribution with its numbers. A field is as long as the paper's
  answer; there is no length limit. A field that would read the same for
  any paper in its area is not an answer.
- **Read from the introduction.** The abstract compresses the paper to a few
  sentences and drops most of what these fields need; the introduction is
  where the authors state the problem, name the work they argue against and
  list their contributions. The brief argues from the introduction, the
  abstract and the comment field (`.claude/prompts/scout.txt` says how the
  introduction is fetched). A paper with no HTML edition is briefed from its
  abstract alone, and (d) says so first: `HTML 원문 없음 — 요지는 초록 기준`.
- **The authors' claims, as theirs.** A field reports what the paper claims
  and shows. A number carries its setting — simulation or hardware, the
  benchmark, the baseline it beats — and a comparison the paper does not make
  is not drawn. Compression that changes a claim's scope is a wrong brief,
  however short.
- **From the paper, not from us.** What the paper means for a pillar is (c);
  `가치` states what the paper is worth to its field, never to a `P#` or
  `D#`.
- **An absent answer is said, not invented.** When the paper names no prior
  approach, `기존 한계` and `차별점` read `원문에 대비 대상 언급 없음` — never a
  gap the authors did not claim.

```markdown
### (b) 논문 요지

- 몸통·루트·손 주석을 한 액션 공간으로 묶은 사전학습
- **문제** — 휴머노이드 전신 이동 조작 정책을 학습할 전신 모션 데이터 부족
- **기존 한계** — 기존 로봇 사전학습 데이터의 전신 모션 커버리지 부족
  - 로봇 궤적만으로는 인간 모션의 다양성을 담지 못함
- **핵심 방법** — 몸통·루트·손가락 주석을 하나의 공유 물리 액션 공간으로 통합해 생성형 비디오 사전학습에 액션 지도로 편입
  - 1단계 — 부분 주석 비디오·모션 1,880.2시간으로 비디오와 액션을 함께 학습
  - 2단계 — PICO 미드트레이닝과 순기구학 보조 지도로 로봇 과제에 적응
- **차별점** — 부분 주석 데이터를 버리지 않고 한 액션 공간에서 함께 학습
- **핵심 기여** — 이종 주석을 함께 쓰는 전신 사전학습 레시피와 데이터셋
  - WB-Datasets — 리타깃팅한 에고센트릭 인간 시연과 로봇 궤적을 함께 묶은 코퍼스
  - 시뮬레이션 HumanoidArena 81.9%, 실물 5개 과제 평균 성공률 84.0%
  - 과제 정합형 미드트레이닝이 실물 시연 필요량을 줄인다는 ablation
- **가치** — 주석이 불완전한 인간 데이터를 전신 사전학습 자원으로 쓰는 경로 제시
```

### 2-3. Rules

- One emoji per `##` header, at the start, after `## ` and a space.
- No emoji on `#`, on `###` or deeper, on table headers, in table cells, in
  code blocks, or in body text.
- Do not use an emoji not listed in §2-1.
- Emojis are not translated — use the symbols exactly as listed.

#### Incorrect example
```markdown
## 논문 1 🥇                             ← emoji at end, wrong
### 🎯 (a) 관련 Pillar / Decision         ← emoji on H3, wrong (## only)
The policy achieved ✨ great results.     ← emoji in body text, wrong
```

---

## 3. Link Format Rule

Every paper entry must include a direct link. Precedence:

1. arXiv preprint → `[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX)`
2. DOI / proceedings → `[DOI](https://doi.org/...)`
3. Neither available → `[no public link]`

Links must appear:
- In the paper header (immediately below the bold title)
- In the further-surfaced (📋) and Near-Miss Candidates (🔍) tables (`Link` column)

Do not fabricate arXiv IDs. Verify that the URL resolves before including it.

### 3-1. Reference Legend & cross-reference links

The report opens with a **Reference Legend** — a one-line glossary of the
`P#` / `D#` codes, so a reader who does not have the codes memorized can
decode the report without opening `context/P#.md`.

**Scope.** Only `P#` (Pillar) and `D#` (Decision) codes.
**Only codes actually cited in this report.** Never list a code the body
does not use; never list competitor codenames, Identity, or the falsifier.

**Placement.** A single `## 🔑 참조 약어 풀이` section, immediately after the
top metadata block and before the first paper section — the report goes
metadata → legend, with no boilerplate intro between them.

**Format.** One compact table, the pillar row first and the decision rows in
order of first appearance in the body — a `D#` id is opaque and carries no
sort order. One row per distinct cited code. Each code renders as a **shields.io
badge**, color-coded by category:

| Category | Color | Source |
|----------|-------|--------|
| `P0` | `f5d5d5` (pale red) | pillar palette — this table is the palette's source of truth |
| `P1` | `f5e9d5` (pale orange) | pillar palette |
| `P2` | `e2f5d5` (pale green) | pillar palette |
| `P3` | `d5def5` (pale blue) | pillar palette |
| `P4` | `e0d5f5` (pale purple) | pillar palette |
| every `D#` | `d97706` (amber) | single shared decision color |

Badge URL: `https://img.shields.io/badge/<CODE>-<hex>.svg` (label-only, no
message).

```markdown
## 🔑 참조 약어 풀이

| Code | Meaning |
|------|---------|
| <a id="ref-P2"></a>![P2](https://img.shields.io/badge/P2-e2f5d5.svg) | Structured Multimodal Observation Fusion (pillar) |
| <a id="ref-D9ZP"></a>![D9ZP](https://img.shields.io/badge/D9ZP-d97706.svg) | Body↔Hand information sharing — FiLM, cross-attn/hidden-state deferred |
```

If the body cites no such code (rare), omit the section entirely.

**Meaning** — derived from `context/P#.md`, never invented; **English only**,
commas not `;`, ≤ ~12 words:

| Code | Source in `context/P#.md` | Meaning string |
|------|-----------------------------------|----------------|
| `P#` | the pillar file's H1, `P# — <name>` | `<name>` + `(pillar)` |
| `D#` | the Decision Log's `#### [D#] <title>` + its current default | `<title>` — concise gloss |

**Anchors.** Each legend row carries `<a id="ref-<CODE>"></a>` before its
badge, `<CODE>` verbatim (`P1`, `D9ZP`); the legend badge itself is not a link.

**In-body links — first occurrence per `##` section.** The first occurrence of
each code in a `##` section is a linked badge
`[![D9ZP](https://img.shields.io/badge/D9ZP-d97706.svg)](#ref-D9ZP)`; later
ones in that section stay plain. Codes in table cells and code blocks are not
linked.

**The (a) line is badges only** — `[![P2](…)](#ref-P2) / [![D3AG](…)](#ref-D3AG)
[![D8EJ](…)](#ref-D8EJ)`: the pillar badge, ` / `, then the decision badges
separated by single spaces, never followed by a Korean gloss.

**Paper sections stay paper-focused.** (a) holds no body bullets. In (b)–(d)
no `D#` codes, `deferred` or config-key / `*.yaml` names — a reader follows the
paper without asking "what is D3AG?". A decision a run moves is a 🔄 bullet
(§7-1).

---

## 4. Korean Authoring Principles

### 4-1. What to write in Korean vs. keep verbatim

| Category | Treatment |
|----------|-----------|
| Body prose | Korean **개조식** (명사형 종결) — register governed by §4-4 |
| Paper titles | Keep original English title; add Korean description if helpful |
| Technical terms | First occurrence: Korean term + English in parentheses. Subsequent: Korean only |
| Config / code names | Keep verbatim (`env_cfg.py`, `ObservationManager`, etc.) |
| Formulas / numbers | Keep verbatim (`ε = 0.1`, `±2σ`, `< 15%`, etc.) |
| P#, D# tags | Keep verbatim (`P2`, `D3AG`, etc.). |
| Reference Legend | Meaning column in **English** (mirrors the English code definitions — no Korean); codes + `<a id="ref-…">` anchors verbatim |
| Anchor / intra-doc links | Keep `id=` and `[…](#ref-…)` verbatim — links resolve within the file |
| arXiv links | Keep verbatim |
| Section headers | Verbatim from §2-1 and §2-2 (§4-3) |

### 4-2. Technical term glossary (standard translations)

| English | Korean |
|---------|--------|
| Sim-to-Real (Sim2Real) | Sim2Real (시뮬레이션-실환경 이전) |
| Domain Randomization (DR) | 도메인 랜덤화 (DR) |
| Reinforcement Learning (RL) | 강화학습 (RL) |
| Imitation Learning (IL) | 모방 학습 (IL) |
| Privileged teacher / student | 특권 교사 / 학생 |
| Contact-rich | 접촉 집약적 |
| In-hand manipulation | 인핸드 조작 |
| Dexterous manipulation | 다지 조작 / 손재주 조작 |
| Forward kinematics (FK) | 순방향 기구학 (FK) |
| Compliance controller | 컴플라이언스 컨트롤러 |
| Tactile sensing | 촉각 감지 |
| Visuotactile | 비주오택타일 |
| Deform Map | Deform Map (변형 맵) |
| Latent space | 잠재 공간 |
| Mixture of Experts (MoE) | 전문가 혼합 (MoE) |
| Skill basis | 스킬 기저 |
| Sticky routing | 스티키 라우팅 |
| Cross-pollination | 크로스폴리네이션 |
| Pinned paper | 핀 논문 |
| Anti-topic | Anti-topic (배제 주제) |
| Real-robot evidence | 실제 로봇 검증 |
| Failure mode | 실패 모드 |
| Decision implication | 의사결정 함의 |
| Citation-graph expansion | Citation-Graph 확장 |
| Keyword Sweep | Keyword Sweep (키워드 스윕) |
| System0 / System1 | System0 / System1 (저수준 안정화 / 고수준 정책 계층) |
| Structured input-modality binding | 구조적 입력-모달리티 결합 |
| VLM pretraining preservation | VLM 사전학습 보존 |
| Action expert | 액션 전문가 |
| Flow matching | 플로우 매칭 |

### 4-3. Section headers are fixed strings

Every `##` and `###` header is copied verbatim from §2-1 and §2-2. It is not
translated back to English, reworded, or extended — no `(월 1회)` on 🌱, no
paper name in a `###`. The English names the tables give are for this guide's
prose only.

### 4-4. Register — 개조식 (outline form, 명사형 종결)

The report is **개조식**: a scanned decision document, terse outline bullets,
not 합니다/됩니다 paragraphs.

- **명사형 종결.** End body items on a noun or nominalized form
  (`~함 / ~음 / ~필요 / 명사`), not a full polite sentence. `D3AG 인코더 학습
  기준 데이터` / `검증 필요` — not `…데이터입니다` / `…검증해야 합니다`.
- **Labelled bullets.** Each item is a bold label + a terse phrase
  (`- **판단 근거** — …`); nest sub-bullets for hierarchy. A section is a
  short bullet list, not one or more paragraphs.
- **One claim per bullet.** No `— …하기 위해` trailing-purpose tails; no
  hedging padding (`~할 수 있을 것으로 보입니다`). Speculation stays speculative
  in nominal form (`저하 우려` / `불필요 가능`), assertions stay assertive
  (단정↔추측 preserved).
- **No semicolon chains in body.** A `;` joining two or three clauses reads as
  an unstructured run-on. When a bullet carries multiple clauses, use a comma,
  or — if they are genuinely parallel items — split into nested sub-bullets
  (e.g. the 🔄 Decision-Log signal becomes one sub-bullet per D#).
- **Where it applies.** All body content — paper (a)–(d) and 🔄 synthesis. Exempt: table cells (a `;` may separate
  distinct entries there) and verbatim English citation blockquotes.

Two surface conventions (markdown, not register):

- Use bold (`**text**`) for the bullet label and for emphasis — and never
  close it between a paren and a particle (§4-8).
- Code blocks and inline code (`` `text` ``) are kept verbatim.

**Meaning is never altered for style.** Restructuring prose into 개조식, a
table or bullets (§4-5) must not add, drop, or reorder any fact, number, date,
quotation, citation polarity, causal direction, or `P#`/`D#` / arXiv / formula
token.

### 4-5. Scannability — repetitive structure goes in a table

§4-4 governs the register inside a bullet; this rule governs the layout above
it.

- **Repetitive records become a table, never a run-on sentence.** Wherever
  the report enumerates the same shape N times — near-miss paper → what
  would lift it (🔍), or any researcher/paper roster — render it as a table (or a clean
  bullet list), not a comma/`·`/`—`-chained paragraph. Target: one
  eye-saccade per record. (Markdown needs a blank line both before and after
  a table, including when a `-` bullet follows.)
- **Lists inside a table cell — use `<br>` + `•`, never `*`/`-`.** A GFM
  table cell cannot hold a real list (`<ul>`) or a literal newline — a
  newline ends the row, and a leading `*`/`-` renders as text, not a bullet.
  To stack several items in one cell, join them with `<br>` and a literal
  bullet glyph: `• a<br>• b<br>• c`.
- **Conclusion before enumeration.** When a long list resolves to one
  verdict ("10편 전원 재등장·제외"), state the verdict first, then the list —
  the reader must not parse every item to reach the point.
- **Machine identifiers stay out of prose.** Semantic Scholar author ids,
  and any arXiv id already carried by an adjacent `Link` column or table
  cell, do not belong inline in Korean sentences. Put them in a dedicated
  cell; never repeat an id a sibling cell already shows (e.g. the 🔍
  `Paper` column drops the id its `Link` column already carries).
- **No enumeration markers in body.** 개조식 uses bullets (§4-4); do not fall
  back to `①②` / `1. 2.` / `첫째·둘째` running inside a sentence.

### 4-6. No raw `~` in prose — it is a strikethrough delimiter on GitHub

GitHub's strikethrough accepts a **single** tilde, so two raw `~` in one
inline context — a paragraph, a list item, a table cell, a blockquote line —
silently strike out everything between them on github.com, where these reports
are read. A lone `~` renders, but becomes the bug the moment a second lands.

**Write ranges and approximations like this instead:**

| Intent | Write | Not |
|---|---|---|
| Numeric / date range | `4.7–35.6GB`, `2026-06-01–06-19`, `1–4편` (en dash `–`, U+2013) | `4.7~35.6GB` |
| Approximation | `약 300M`, `약 2×`, `약 110K frame` | `~300M` |
| Paper notation `\sim` | `` $`\sim 50`$ `` (inline math) | `~50` |
| Open-ended range | `2026-05-11–`, or spell it (`2026-05-11 이후`) | `2026-05-11~` |

**A raw `~` is still correct** inside a code span or fence, inside `$$…$$` or a
` ```math ` fence (LaTeX's non-breaking space), in an HTML comment, and in a
deliberate `~~strikethrough~~`. An English verbatim blockquote is byte-locked
(§4-1) and never edited — keep the Korean line beside it tilde-free.

### 4-7. No bare URL in Korean prose — the following particle joins the href

GitHub autolinks a bare `https://…` and reads trailing Hangul as part of the
URL, so a particle written straight after it joins the href and the link 404s.
**In Korean prose a URL is always an explicit `[텍스트](…)` link:**

| | Write | Not |
|---|---|---|
| URL with a following particle | `[프로젝트 페이지](https://example.org/x/) 하나뿐이며` | `프로젝트 페이지(https://example.org/x/)만` |
| URL as the sentence subject | `[공식 저장소](https://example.org/r)에서 받습니다` | `https://example.org/r 에서 받습니다` |

A bare URL is still correct inside a code span or fence, an HTML comment, or
an English verbatim blockquote.

### 4-8. Never close `**` between a closing paren and a particle

A `**` between punctuation and a letter cannot close an emphasis run, so a
parenthetical gloss followed by a particle publishes both markers as
asterisks — and the sentence still reads, which is why it survives review:

| Write | Not |
|---|---|
| `**느린 채널**(비전·언어)과 **빠른 채널**(고유수용감각)로` | `**느린 채널(비전·언어)과 빠른 채널(고유수용감각)**로` |
| `**계단 스케줄**로` (letter before the marker — closes fine) | — |

**The character before a closing `**` is never punctuation** when a letter
follows. Bold the phrase, not the phrase plus its parenthesis. No build step
catches it on this track.

---

## 5. Scoring Contract

The rubric is **five fixed dimensions, 0–3 each, total /15**. A report never
adds, drops, or renames one, and always shows all five for every paper it
scores. This section owns the dimensions, who scores each, the gate and the
rank order; the prompt owns how the evidence is fetched.

| Dimension | Code | What it scores | Scored by |
|---|---|---|---|
| Relevance | `R` | Which `P#` / `D#` the paper touches, and how directly | the pillar |
| Novelty | `N` | Genuinely new, or a delta over this pillar's tracked work | the pillar |
| Methodology | `M` | Experimental rigor (§5-2) | the run, once per paper |
| Real-robot evidence | `Real` | How much of the result stands on real hardware (§5-2) | the run, once per paper |
| Reproducibility | `Repro` | Whether the artifact is obtainable (§5-2) | the run, once per paper |

Relevance and Novelty are read against one pillar's Scope and Tracked
Literature, so a paper two pillars surface may score differently in each.
Methodology, Real and Reproducibility describe **the paper**, so they are
judged once per run for every candidate any pillar keeps, and every report of
that run prints the same three (§5-4).

### 5-1. The gate is Relevance, Novelty and Methodology

A paper is surfaced as a `## 🥇 / 🥈 / 🥉 / 🌱` section when **Relevance, Novelty
and Methodology are each ≥ 2**. Real and Reproducibility are scored, shown and
counted in the total that ranks (§5-3), but they are **not** part of the gate.

Both measure where a result stands rather than whether it is worth reading. A
fresh preprint rarely has a public repository on the day it posts, and a paper
can be sound, new and on-topic with every result in simulation — or with no
simulation at all, entirely on hardware. A gate term for either measures the
kind of paper, not its quality.

**The gate binds in both directions.** A candidate whose three gate dimensions
are each ≥ 2 is surfaced — never parked in 🔍 or dropped over a closed
repository or a simulation-only result. Those cost the paper points in the
total and show in its code label (§5-3); they never remove it.

**The gate decides whether a paper surfaces; its rank decides the shape.**
The top three by rank (§5-3) take the full `## 🥇 / 🥈 / 🥉` sections, one
medal each. Every further paper that clears the gate is still surfaced — as one
row of `## 📋 기준 통과 · 추가 후보`, in rank order — so a strong week stays a
report a reader can scan rather than a stack of full sections. The 🌱 pick
keeps its own section (§5) and is not one of the three. A 🌱 proposal that
does not clear the gate is not printed — no 🌱 section and no 🔍 row — and
the pillar's budget for the slot stays open.

```markdown
| Paper | Link | R·N·M·Real | Repro | 합계 | 코드 | 한 줄 근거 |
|---|---|---|---|---|---|---|
| LIRA | [arXiv:2608.07596](https://arxiv.org/abs/2608.07596) | 3·2·2·2 | 1 | 10/15 | 코드 공개 예정 | <한 줄> |
```

Omit 📋 when three or fewer papers clear the gate. The metadata field
`**Papers surfaced (게이트 통과):**` (§6) counts the paper sections and the
📋 rows together. When fewer than 3 papers clear the gate, say so and do not
pad.

A paper section carries its scores on **the score line**, the paragraph right
under its header line — the total, the five dimensions and the Reproducibility
evidence (§5-2), in this form and no other:

```markdown
**점수 13/15** · R3 · N3 · M3 · Real3 · Repro1 — arXiv comment "Project Page: https://wb-wam.github.io"
```

The five sum to the total. A 📋 row carries the same scores in its own cells;
a paper the report did not surface carries none. Why a dimension scored what it
did is what (b)–(d) and the run file (§8) already say, so no section restates
it per dimension.

### 5-2. The paper's three are scored from quoted evidence

Methodology, Real and Reproducibility are scored from **strings the retrieval
pass actually received** — the arXiv `<arxiv:comment>` field and the abstract
body, both in the response the run already makes. Each level below names what
the text must say; a score the text does not support is not given, and an
absent signal is stated as absent. `초록상 미확인` / `확인 필요` is not an
outcome — the run has already read the text.

**Methodology** — what the experiments compare against and isolate.

| Score | Condition |
|---|---|
| 3 | 2, and repeated seeds / variance, or a stated limit or failure mode |
| 2 | Two or more baselines, and an ablation of the paper's own component |
| 1 | One baseline or fewer, or no ablation |
| 0 | Demonstrations only — no comparison |

**Real** — how much of the result stands on real hardware. A paper with no
simulation at all is scored on its hardware results like any other; nothing
here asks for a transfer from simulation.

| Score | Condition |
|---|---|
| 3 | Quantitative real-robot results on several tasks or platforms, or a measured sim-to-real or human-to-robot transfer |
| 2 | Quantitative real-robot results (success rate, trials) on at least one task |
| 1 | Real-robot demonstrations without numbers — videos, a qualitative case |
| 0 | No real-robot result — simulation, video or human data only |

For a dataset or benchmark paper, Real scores the real-robot data or
evaluation the release itself carries.

**Reproducibility** — whether the artifact is obtainable.

| Score | Condition |
|---|---|
| 3 | Repository URL present **and** data / checkpoints **and** hardware or config detail |
| 2 | A code repository URL is stated (`github.com/…`, `Code: …`) |
| 1 | Project page only, or a promise (`code will be released`, `release soon`, `upon acceptance`) |
| 0 | No repository, page, or release statement anywhere in the abstract or the comment field |

**Evaluation on a public benchmark is not reproducibility evidence** — LIBERO,
CALVIN, SIMPLER, DexYCB say the paper is comparable, not that the artifact is
obtainable. A Repro ≥ 2 whose evidence says `코드 공개 미확인` contradicts
itself.

The score line **quotes the Reproducibility evidence** after the `—`; the run
file quotes all three (§8):

```markdown
… · Repro2 — arXiv comment "Code: https://github.com/LeapWM/leapbot-wa"
… · Repro1 — arXiv comment "Code and model checkpoints will be released upon acceptance"
… · Repro0 — 초록·arXiv comment 모두 코드·프로젝트 페이지 신호 없음
```

The quote names its source, `arXiv comment "…"` or `초록 "…"`. A
Reproducibility kept from an earlier report (§5-4) reads
`<pillar> <date> 판정 유지` in its place (`… · Repro1 — P1 2026-10-01 판정 유지`).

### 5-3. The Reproducibility label and the rank order

Every paper header line and every 📋 `코드` cell carries the label its
Reproducibility score implies, as plain text (emoji stay on `##` headers — §2):

| Score | Label |
|---|---|
| 2–3 | `코드 공개` |
| 1 | `코드 공개 예정` |
| 0 | `코드 미공개` |

The site prints no score. Beside the code label it prints what the paper's
Real score says, in words — the one part of the rubric a reader decides by:

| Real | Site label |
|---|---|
| 3 | `실물 정량, 다수 과제` |
| 2 | `실물 정량 결과` |
| 1 | `실물 시연만` |
| 0 | `실물 결과 없음` |

The label is the report's only priority marker — a header carries no stars or
other grade. Rank by Relevance, then by the /15 total, then by venue tier —
this order assigns the medals and orders the 📋 rows (§5-1). Real and
Reproducibility count toward the total, so between two equally relevant papers
the one with more on hardware and an artifact to run ranks first.
Venue tier comes from the Venue Priority table `context/MASTER.md` §5 owns (the prompt
carries a copy), read from the arXiv comment field and recorded on the paper header line. Venue
breaks ties only; it never gates and never overrides the rubric.

### 5-4. One paper, one judgement of what does not depend on the pillar

The same paper reaches several pillars' reports — that is what a single
release looks like from five axes — and a reader comparing them must not find
two answers about the paper itself.

- One run scores Methodology, Real and Reproducibility **once per paper**,
  across every pillar it runs, and records them with their evidence in the
  run file (§8). Every report of the run prints those three.
- A paper already scored in a report dated within the ~8-week
  de-duplication window, before this run's date, **keeps** that report's
  three — the most recent date, and on one date the lowest pillar number. A
  score line and a 📋 row carry all three; a 🔍 row carries Methodology and
  Real, which it keeps while Reproducibility is scored afresh. No other
  line is a source.

### 5-5. Near-miss candidates

`## 🔍 근접 후보` holds this run's candidates that are **exactly one gate axis
short** — one of Relevance, Novelty and Methodology scores 1 and the
other two are ≥ 2. Two or more axes short is dropped and appears in the report only
as part of the filter count in 🔄 (§7-1); zero axes short is a surfaced paper
(§5-1), never a 🔍 row.

The table is this run's alone. A row is not carried into the next report and
is not re-checked there; like every id a report names, the paper is then held
out of later runs by the routine's de-duplication window. `재검토 조건` names,
for the reader, what would lift the short axis.

One table, no per-paper `###` subsections. The `코드` cell is the §5-3 label
of the run's Reproducibility score for the paper:

```markdown
| Paper | Link | R·N·M·Real | 코드 | 재검토 조건 |
|---|---|---|---|---|
| LIRA | [arXiv:2608.07596](https://arxiv.org/abs/2608.07596) | 2·2·1·3 | 코드 공개 예정 | 베이스라인 비교가 추가되면 Methodology 충족 |
```

Omit the section when it has no rows.

---

## 6. Report Metadata Block

The block between the H1 and the first `---` is exactly two lines:

```markdown
# Probe 스카우트 리포트 — YYYY-MM-DD · Pillar P#

**Papers scanned:** <one-line summary, ≤ 400 characters>
**Papers surfaced (게이트 통과):** <integer>
```

- **No `Run date:` or `Agent version:` line** — the H1 carries the date, the
  commit the provenance.
- **`Papers surfaced` is a bare integer** equal to the `## 🥇 / 🥈 / 🥉 / 🌱`
  sections plus the `## 📋` rows (§5-1); why it is low belongs in 🔄.
- **`Papers scanned` is ≤ 400 characters** and the report's only provenance:
  the passes run, an order-of-magnitude count per pass, and any call still
  failing at the end, verbatim as `… 최종 실패`. No per-query breakdown, no
  funnel arithmetic (`661건 → 507편 → …`), no retry narration — a retry that
  succeeded is a non-event.

```markdown
**Papers scanned:** citation-graph 8핀 280편 + keyword sweep 110편(14일 44편)
— keyword sweep 1개 쿼리 HTTP 429 최종 실패
```

---

## 7. Section Discipline

§4-4 governs the register inside a bullet and §4-5 the layout above it. This
section governs what each `##` section is allowed to repeat.

### 7-1. Run-over-Run Synthesis — 3–5 bullets

`## 🔄 직전 리포트 대비 종합` covers, one bullet each and only when the run has
something to say: papers already covered (verdict first), contradictions with
recent findings, Decision-Log triggers, filter health as a count,
already-analyzed dedup count.

- **A Decision-Log trigger names the decision and the paper that moved it**
  (`[![D5DQ](https://img.shields.io/badge/D5DQ-d97706.svg)](#ref-D5DQ) —
  Rho(2609.38164) 15회 교정 적응이 서브루프 없는 대안 제시`). It is
  a signal for the reader, not an edit proposal — `context/` is the human's
  record, and the report names no pin, rule or wording to change there.
- **Filter health is the only trace of a dropped candidate.** A count and a
  reason (`5편 제외 — WAM 아키텍처 4편, Methodology 미달 1편`), never a
  per-paper list and never the pipeline arithmetic from `Papers scanned` (§6).
- **A "not applicable" item is omitted, not narrated.** `월간 트렌드: 첫 리포트
  아님 — 생략` and `재등장 여부 — 해당 없음(N/A)` are lines that exist only to
  report their own emptiness. Drop the bullet.

### 7-2. Paper names must be unambiguous across reports

Codenames collide — two unrelated papers both self-titling `Faster-WAM` is an
ordinary occurrence in this corpus, and the reports read side by side across
pillars. A bare alias is only safe where a `Link` column resolves it in the
same row.

- **The alias** is the paper's own codename — the part of its title before
  the colon — or else the title's first words, up to about 30 characters.
  Plain text: no `$…$` math, and a Δ is written as the character.
- In **prose** (🔄), an alias carries its id on first use in the
  section: `Faster-WAM(2608.04404)`.
- In the 📋 and 🔍 tables the `Paper` column stays alias-only — the `Link`
  column is the disambiguator (§4-5).
- One table row is **one paper**. A cell like `Faster-WAM 외 2편 (ω-0, WAM-Diff2)`
  against a single link hides two papers behind a third one's id; give each its
  own row.

---

## 8. The Run File

One run of the routine covers the pillars it was asked for and writes, beside
their reports, **one run file**: `scouting/runs/YYYY-MM-DD.md`. It is the
record of the run as a whole — which pillars it covered, the one judgement of
each paper's own scores (§5-4), and what the pillars found together. The site
prints its synthesis at the top of the date's page (§1).

```markdown
# Probe 스카우트 회차 — YYYY-MM-DD

**Pillars:** P0 P1 P2 P3 P4
**Failed:** P2 — arXiv API HTTP 503 최종 실패

---

## 🧭 회차 종합

- <3–5 bullets>

---

## 📐 논문 판정

| Paper | Link | M | Real | Repro | 근거 |
|---|---|---|---|---|---|
| WB-WAM | [arXiv:2609.34199](https://arxiv.org/abs/2609.34199) | 3 | 3 | 1 | M: "outperforms … and ablates …" · Real: "84.0% on five real-world tasks" · Repro: "Project Page: https://wb-wam.github.io" |
```

- **`Pillars:`** lists the pillars the run was asked for, in order. Each has
  a report of the same date unless `**Failed:**` names it, with the error
  that stopped it verbatim. With nothing failed the `Failed:` line is absent.
- **`## 🧭 회차 종합`** is 3–5 bullets about the run across pillars and
  nothing a pillar's own 🔄 already says: the papers several pillars surfaced
  and why each wanted them, a decision two pillars' findings bear on together,
  a pillar that came back thin. 개조식, §4-4.
- **`## 📐 논문 판정`** has one row for every paper any report of the run
  surfaces or lists in 🔍, with the three scores every report prints for it.
  `Paper` is the paper's alias (§7-2) — the name every report of the run
  uses for it, and the one the site prints on the paper's row.
  `근거` quotes the text each score stands on, `M:`, `Real:` and `Repro:` in
  that order; a score kept from an earlier report (§5-4) reads
  `<pillar> <date> 판정 유지` instead.

---

## 9. Enforcement

A run goes straight to `main` with no PR, so the routine runs
`linters/check-scouting-format.py` on every file it wrote before committing
(`.claude/prompts/scout.txt`) and CI re-runs it on every push to `main` as
the backstop. The lint binds reports dated on or after its
`_CONTRACT_EFFECTIVE`; the gate arithmetic binds from `_GATE_EFFECTIVE`, the
medal, 📋 and retry rules from `_SHAPE_EFFECTIVE`, and the §2-1 section set,
the bare medal header, the score line, the three-axis gate and the run file
from `_SECTIONS_EFFECTIVE`. A report dated earlier is the record of a run
under the contract of its day and is read, never rewritten, in that form.

| Rule | Checked by |
|---|---|
| H1 form and its date against the filename; the two-line metadata block, the 400-character cap, no retry narration without `최종 실패`, `Papers surfaced` a bare integer equal to the paper sections plus the 📋 rows (§6) | lint |
| Every `##` opens with a §2-1 emoji, sections in §2-1 order, each medal at most once, 📋 only under all three medals, no emoji on `###`, nothing after `논문 N` on a paper header, the (b) and (c) headlines within 50 characters, the six (b) labels each once and in order (§2, §5-1, §5-3) | lint |
| A score line on every paper section, its five scores summing to its total and to each 📋 row's 합계; each surfaced paper and 📋 row clears the gate; each 🔍 row exactly one gate axis short; no Reproducibility ≥ 2 that pleads an unconfirmed signal; a code label on every paper header, agreeing with its Reproducibility score (§5) | lint |
| The run file's form; a report for every pillar it lists and not `Failed:`; a 📐 row for every paper a report of the run scores, and Methodology, Real and Reproducibility in every report equal to that row; a 📐 row equal to an earlier report's three when one scored the paper in the window (§5-4, §8) | lint |
| One paper per 🔍 / 📋 row (§7-2) | lint |
| Links resolve and no id is fabricated (§3); the legend lists exactly the cited codes, with badges and anchors (§3-1); the header strings (§4-3); the 개조식 register (§4-4); the render traps (§4-6 – §4-8); the three paper scores standing on the evidence quoted for them (§5-2); 🔄 and 🧭 discipline (§7-1, §8) | the routine's SELF-CHECK and the reader — nothing parses them |
