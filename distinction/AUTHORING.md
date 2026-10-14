# Distinction authoring

The format contract for the distinction track — the documents `/distinguish`
writes into the private folder: one ledger per basket paper, the claims ×
papers matrix, one delta per run, and on demand a dissection of one paper
against one code scope. Every one of them holds the method or its code
beside the papers, which is why none of them is in this repository.

`.claude/prompts/distinguish.txt` defers to this file for what the documents
must look like, and owns the procedure — what is read, how the delta is found,
how the evidence is confirmed. `distinction/SETUP.md` owns the private folder
itself: where it lives, what the human writes into it, how the machine runs
the routine. Edit this file first, then the prompt, then the lint.

## 1. The one rule

**Nothing this track writes reaches the repository.**

Every row of a ledger sets a basket paper's mechanism next to this method's —
a config key, a stated weakness, an unpublished number — and the repository is
public. So the track has no output folder here, no site section, no CI gate
and no commit step; the private folder (`distinction/SETUP.md` §2), outside
the checkout, is where it reads and the only place it writes. Examples in this
file, the prompt and the templates use placeholder ids, claims and keys —
never a real one.

The other rule the track inherits: **only a paper with a rewrite in
`analysis/` gets a ledger** or a dissection — both read it through
`site/query.py`. A basket row without one is a next action in the delta
(§3-3), not a ledger.

## 2. What the routine reads and writes

Reads the human-owned `BASKET.md`, `METHOD.md`, `CODEMAP.md` and `code` under
`$PROBE_PRIVATE_DIR` (schemas: `distinction/SETUP.md` §2), and from the
checkout `context/MASTER.md`, the pillar files the basket touches, and the
corpus through `site/query.py`.

Writes, all under `$PROBE_PRIVATE_DIR`:

| File | One per | Overwritten |
|---|---|---|
| `ledger/<arxiv-id>.md` | basket paper | yes — the ledger is the current position, never a history |
| `matrix.md` | folder | yes |
| `runs/YYYY-MM-DD.md` | run | no — one file per run date, and the previous run's is what the next run diffs against |
| `dissect/<arxiv-id>--<scope>.md` | `--dissect` run | yes — the latest reading of that paper against that scope |
| `.scratch/` | run | yes — drafts for the verify agents and helper files; read by nothing after the run, and the only place a working file may go |

## 3. The documents

All four are Korean, in the register `scouting/AUTHORING.md` §4 fixes (§6
below). Section headers are fixed strings: the lint matches them verbatim.

### 3-1. The ledger — `ledger/<arxiv-id>.md`

`comparison/` holds papers against papers. The ledger holds **this method
against one paper**, and every section is one question asked in that order.

```
# <alias> — <한 문장: 이 논문 앞에서 내 방법은 무엇인가>
Role: baseline · Claims: C1, C3 · Rewrite: analysis/XXXX.XXXXX.md · Method: 0000000 · Run: YYYY-MM-DD

## 1 공통
## 2 차이
## 3 그들의 빈자리
## 4 내 방법이 메우는가
## 5 그들을 개선할 아이디어
## 6 위협
## 7 최저가 반증 실험
```

The H1 is the position in one sentence — what this method is *when this paper
is in the room*, not what either does. The metadata line holds exactly five
fields: the row's `role` and `claims` as `BASKET.md` has them, the rewrite
read, the first seven hex digits of the SHA-256 of `METHOD.md` as it was when
the ledger was written, and the run date. `Method:` is what lets the next run
see that the method moved under this ledger.

| Section | Holds | Each bullet carries (§4) |
|---|---|---|
| `1 공통` | The problem setting, the mechanism, the evaluation the two share | a paper anchor and a method anchor (`C#` or `METHOD §n`) |
| `2 차이` | Axis by axis: their choice, this method's choice | a paper anchor and a code anchor (`path:line`, `cfg:key`) or `METHOD §n` |
| `3 그들의 빈자리` | What the paper does not reach, **from its own ablation, failure case or stated limit** — never inferred from silence | a paper anchor, act 4 where it exists, and a quote anchor |
| `4 내 방법이 메우는가` | For each gap in §3: `메운다`, `부분` or `못 메운다`, then why, against `METHOD.md` §4 | the verdict first, then a `METHOD §n` anchor |
| `5 그들을 개선할 아이디어` | At most two `###` ideas, strongest first, in the §3-4 shape | the five labels |
| `6 위협` | The condition under which this paper takes a claim: which `C#`, on what number, in which setting — a condition on that claim's own axis, not a question the paper raises against it | a paper anchor and a quote anchor; a number confirmed in the original (§4) |
| `7 최저가 반증 실험` | The cheapest run on this codebase that would show the position wrong | at least one `cfg:key` anchor — the keys to change and the values |

A section with nothing to say holds the single bullet `- 없음`. That is a
finding, and it is honest; a bullet padded to avoid it is not.

### 3-2. The matrix — `matrix.md`

```
# 주장 × 바구니
Method: 0000000 · Run: YYYY-MM-DD

| | <alias> (XXXX.XXXXX) | <alias> (XXXX.XXXXX) |
|---|---|---|
| C1 | 위협 — <한 줄> ([장부](ledger/XXXX.XXXXX.md)) | 무관 |
| C2 | 지지 — <한 줄> | 반박 — <한 줄> |
```

Rows are every `C#` in `METHOD.md` §1, columns are every `active` basket paper
that has a rewrite, in `BASKET.md` order, each head carrying the alias and the
id. A cell opens with one of four verdicts — `지지` the paper's evidence
supports the claim, `무관` it does not bear on it, `위협` it could take the
claim under a condition the ledger names, `반박` it already has — and may
carry one line and a link to the ledger section behind it. The matrix is the
related-work table and the experiment table in draft, and a cell transition
(`지지` to `위협`) is what the delta reports.

### 3-3. The delta — `runs/YYYY-MM-DD.md`

```
# YYYY-MM-DD 차별화 델타

## 1 코퍼스 변화
## 2 바구니 변화
## 3 방법론 변화
## 4 매트릭스 전이
## 5 새 아이디어
## 6 제안
## 7 다음 행동
## 8 감사

```probe-state
{"run": "YYYY-MM-DD", "corpus_head": "<git sha>", "method": "0000000",
 "codemap": "0000000", "basket": "0000000",
 "related": {"XXXX.XXXXX": ["XXXX.XXXXX", "XXXX.XXXXX"]},
 "verified": {"XXXX.XXXXX": "YYYY-MM-DD"}}
```
```

Only what changed since the previous run, section by section:

| Section | Holds |
|---|---|
| `1 코퍼스 변화` | Rewrites, comparisons and scouting reports landed since `corpus_head`, **only those `related` to a basket paper**, with the relation kind (`neighbour`, `cites`, `compared_with`, …) |
| `2 바구니 변화` | Rows added, removed or re-roled; rows with no rewrite yet; rows `graduated` |
| `3 방법론 변화` | If `method` or `codemap` moved: which `METHOD.md` sections changed and which ledgers were rewritten because of it; a `METHOD.md` untouched for eight weeks or more earns one line here |
| `4 매트릭스 전이` | Cells whose verdict changed, old to new, with the ledger section behind each |
| `5 새 아이디어` | At most three `###` ideas across the whole run, in the §3-4 shape — the strongest of what the rewritten ledgers' §5 hold, not a copy of all of them |
| `6 제안` | What the human should change in `BASKET.md` or `METHOD.md`: a basket candidate found citing a basket paper, a claim with no basket column, a row with empty `claims`, a `parked` row that bears on a claim new since the previous run |
| `7 다음 행동` | `/analyze <id>` for a row without a rewrite, `/compare <id> <id>` where two basket papers need their divergence laid out first, one ablation to run |
| `8 감사` | One bullet per ledger the audit re-read (prompt step 7), naming its id: what it corrected — a quote, a moved code line, a verdict — or `고칠 것 없음`. Only a run that audits has this section: a delta run or `--audit`, not a single-paper or `--all` run |

The `probe-state` block closes the file and is the track's memory — the
checkout's `HEAD`, the three input hashes, the `related` ids per basket
paper, and `verified`, the date each ledger was last rewritten or audited —
so the next run diffs instead of re-reading everything, and audits the
ledgers read longest ago.

**The no-change run.** When `corpus_head`, the three hashes and every
`related` list are unchanged, the run writes this file with `- 없음` under
sections 1 to 6, the standing next actions under 7, the audit under 8, and
the state block. It rewrites no ledger, but the audit still corrects the ones
it re-reads: nothing changing in the repository says nothing about whether
what a ledger already states is true. A run that finds nothing and says so
is the track working.

### 3-4. The shape of an idea

A `###` under a ledger's §5, a delta's §5 or a dissection's §8 is one idea in five labels, each
on its own line, bold, in this order. They follow `/ideate`'s idea shape with
one difference: a ledger is a position against the Decision Log, so where
`/ideate` asks what an idea opens, a ledger names the `D#` it moves.

```
### <아이디어 한 줄>
- **조합** — <alias> 의 <mechanism> + 내 <mechanism> (`path:line`)
- **왜 어느 쪽도 혼자 못 하나** — <their gap, `alias §4 Term`>; <mine, `METHOD §4`>
- **움직이는 결정** — D<id>, <which way>
- **가장 싼 반증 실험** — <setup>, `cfg:key` = <value>
- **이미 있는 것** — <the comparison or rewrite that comes closest>
```

The method is the permanent third party here: an idea that does not take
something from `METHOD.md` or `CODEMAP.md` is an `/ideate` answer and belongs
in that chat, not in a ledger.

### 3-5. The dissection — `dissect/<arxiv-id>--<scope>.md`

The ledger is a position, kept short so the scheduled run can re-read it.
The dissection is the long reading a human asks for when one paper matters:
that paper's rewrite against one **code scope** — a bare name
(`[a-z0-9_]+`) that the operator's `codemap.sh` resolves to a part of the
codebase (`distinction/SETUP.md` §2-3) — and the rewrite itself checked
against the original first, because every later section stands on what the
paper actually says. The paper needs a rewrite; it need not be in the
basket. Nothing else in the folder reads a dissection: no ledger, matrix or
delta changes because one was written.

```
# <alias> × <scope> — <한 문장: 둘이 같은 문제를 어떻게 다르게 풀었나>
Paper: XXXX.XXXXX · Scope: <scope> · Rewrite: analysis/XXXX.XXXXX.md · Code: 0000000 · Method: 0000000 · Run: YYYY-MM-DD

## 1 재작성본 정오표
## 2 동기
## 3 공통
## 4 구성요소 대조
## 5 실험 설정
## 6 결과 대조
## 7 빈자리와 메움
## 8 빌려 올 것
## 9 반증 실험
```

The metadata line holds exactly six fields: the paper id, the scope, the
rewrite read, the codebase's short commit hash as the scope's digest prints
it, the first seven hex digits of the SHA-256 of `METHOD.md`, and the run
date. The file name carries the same id and scope.

| Section | Holds | Each bullet carries (§4) |
|---|---|---|
| `1 재작성본 정오표` | One line `점검 N · 맞음 n · 틀림 n · 과장 n · 원문 없음 n`, then one bullet per statement the errata pass graded other than `맞음`, and one per `맞음` statement a later section rests on | a verdict first — `맞음`, `틀림` the original says otherwise, `과장` it says less, `원문 없음` it does not say it — then a paper anchor; every verdict but `원문 없음` also a quote anchor |
| `2 동기` | The problem each side set out to solve, and why then — theirs in their words, this scope's from `METHOD.md` §0 or as a reading | a quote anchor for theirs |
| `3 공통` | The setting, the mechanism, the evaluation the two share | a paper anchor and a code, config or `METHOD §n` anchor |
| `4 구성요소 대조` | One `###` per pipeline stage — input, anchor, read-out, injection, loss, inference, training recipe — each bullet their choice against this scope's | a paper anchor and a code or config anchor |
| `5 실험 설정` | One table, `\| 축 \| <alias> \| <scope> \|`: benchmark, embodiment, data scale, metric, baselines, compute | each row's scope cell a code, config or `METHOD §n` anchor, or `없음` |
| `6 결과 대조` | Their numbers, confirmed in the original, beside the scope's from the digest's Results or `METHOD.md` §3, and what keeps a pair from being comparable | a quote anchor or `원문 미확인` |
| `7 빈자리와 메움` | Each gap the paper states itself — ablation, failure case, stated limit — and whether this scope reaches it | a verdict first — `메운다`, `부분` or `못 메운다` — then a quote anchor |
| `8 빌려 올 것` | At most three `###` ideas, strongest first, in the §3-4 shape | the five labels |
| `9 반증 실험` | The runs on this scope that would show a §3 – §7 reading wrong | at least one `cfg:` anchor — the keys and the values |

A statement §1 grades `틀림` or `원문 없음` is never written as the paper's
in §2 – §9; where a later section needs it, it is the rewrite's reading and
says so. `C#` and `METHOD §n` anchors are allowed throughout and required
nowhere: they bind only when the scope is the code `METHOD.md` describes.
A section with nothing to say holds `- 없음`, as in the ledger.


**A bullet without its anchors is not written.** The anchors are what make a
row a lookup the reader can run rather than a claim the reader must trust, and
they are the one check the lint can make that the facts were looked at.

| Anchor | Grammar | Resolves through |
|---|---|---|
| paper | `` `<alias or id> §<act> <Term>` `` — one English term from that H3's `\| Term · Term` tail | `python3 site/query.py section <alias> --match "<Term>"` returns that H3 |
| claim | `` `C<n>` `` | `METHOD.md` §1 has `#### [C<n>]` |
| method | `` `METHOD §<n>` `` | that section of `METHOD.md` |
| code | `` `<path>:<line>` `` | a line of the codebase, as `CODEMAP.md` lists it |
| config | `` `cfg:<key>` `` | a key `CODEMAP.md` lists under its config section |
| quote | `원문 §<section> "<verbatim English>"` — at least a clause, copied byte for byte; a table row is quoted whole under `§TABLE-<n>` | `cd site && python3 -m builder.arxiv <id> --grep "<a phrase of it>"` prints it under that section, a table row under `Table TABLE <n>:` |

Which sections need which is §3-1's table. Four further rules:

- **A number is confirmed in the original before a ledger states it.** The
  rewrites are a map, not the source of fact (`.claude/prompts/ideate.txt`,
  step 4): `cd site && python3 -m builder.arxiv <id> --grep "<pattern>"`
  prints the lines of the original that carry it, with their section. A §6
  threat rests on a number, so a §6 bullet without that check is written as
  the rewrite's number and says so.
- **A code anchor comes from `CODEMAP.md` or from a `grep` that found it.**
  Never from memory of what the code probably does — the digest is regenerated
  at the start of every run (`distinction/SETUP.md` §2-3) so that the anchors
  a ledger carries are the code as it is.
- **What the authors did, found or meant is quoted, not paraphrased.** A
  sentence that states why the paper chose something, what it was for, or
  what it does not handle carries a quote anchor. When the original says
  nothing on the point, the sentence is either cut or written as this
  method's reading (`…로 읽힘`) — and a reading never carries a §6 threat or a
  matrix verdict other than `무관`. When the original cannot be fetched (a
  withdrawn paper), `원문 미확인` stands where the quote would, and the same
  limit applies.
- **The rewrite is a map, its commentary is not the paper.** A rewrite marks
  its own inferences (`원문이 따로 논하지 않지만`, `…로 보입니다`). A ledger
  that lifts one states it as the rewrite's reading, never as the paper's.

### 4-1. Evidence grades

Every paper-side statement in a ledger has one of three grades, and the grade
decides where it may stand. The verify pass (prompt step 6, or D4 for a
dissection) assigns them.

| Grade | Means | May carry |
|---|---|---|
| `원문` | the original says it — a quote anchor or a confirmed number proves it | anything: §1–§3, a §6 threat, any matrix verdict |
| `재작성본` | the rewrite says it, the original does not | §1 and §2 context, written as the rewrite's reading |
| `추론` | the ledger's own inference from either | §2 and §5 only, written as a reading |

## 5. Caps

| What | Cap | Why |
|---|---|---|
| `active` basket rows | 12 | past that a run re-reads everything and the delta becomes a reprint |
| Ideas per ledger (§3-1 `5`) | 2 | the ledger is a position, not a brainstorm |
| Ideas per delta (§3-3 `5`) | 3 | `/ideate`'s own ceiling, for the same reason |
| Ledger prose | 7,000 characters outside fences | the comparison ceiling; a ledger past it has started explaining the paper, which its rewrite already does |
| Ideas per dissection (§3-5 `8`) | 3 | `/ideate`'s ceiling |
| Dissection prose | 20,000 characters outside fences | room for every stage and the errata, short of retelling the paper |
| Ledgers audited per delta run | half the active ones, rounded up | at the two scheduled runs a week (`distinction/SETUP.md` §4) every ledger is re-read within the week, and no run carries the whole basket |

## 6. Korean authoring

`scouting/AUTHORING.md` §4 binds here as written — what stays verbatim (every
anchor, `C#`, `D#`, id and config key included), the glossary, fixed headers,
개조식, and the three render traps (§4-6 – §4-8).

## 7. What never leaves

`METHOD.md` §6 lists literal strings — a codename, a number, a dataset, a
collaborator — that no output may carry yet. The lint fails on any of them in
a ledger, the matrix, a run or a dissection, and the routine does not save an output the
lint fails. A ledger that needs to say the thing says it by its `C#` or
`METHOD §n` anchor.

## 8. Enforcement

`linters/check-distinction-format.py` reads the private folder (`PROBE_PRIVATE_DIR`,
or a path argument) and checks what a document can get wrong while reading
perfectly. It is the routine's own gate — step 8 of the procedure — and it
is run by hand after editing a document. It is in no workflow, because what it
checks is in no checkout.

| Rule | Check |
|---|---|
| §1 | every `ledger/<id>.md` names a `BASKET.md` row and `analysis/<id>.md` exists |
| §3-1 | the H1, the five-field metadata line, the seven headers verbatim and in order, no other `##` |
| §3-1, §4 | per section, every bullet carries the anchors its row of the table requires, or is `- 없음` — a §3 and a §6 bullet carry a quote anchor or `원문 미확인`; a §4 bullet opens with a verdict; §7 holds a `cfg:` anchor |
| §3-2 | the matrix's rows are `METHOD.md`'s claims and its columns the active rewritten basket, each cell opening with a verdict |
| §3-3 | the delta's H1 date is the file's, the seven headers and an optional `8 감사` whose every bullet names a ledger id, at most three `###` under `5`, a closing `probe-state` block that parses and carries every key, its `verified` (when present) mapping ids to dates |
| §3-4 | every `###` idea carries the five labels in order; a `D#` it names exists in a pillar's Decision Log |
| §3-5 | the dissection's file name and six-field metadata line agree, `analysis/<id>.md` exists, the nine headers verbatim and in order; §1 opens with its count line and every bullet with a verdict, a paper anchor and — but for `원문 없음` — a quote anchor; §3 and §4 bullets carry their anchors; §5 holds a table whose scope cells carry an anchor or `없음`; §6 bullets a quote anchor; §7 bullets a verdict and a quote anchor; §9 a `cfg:` anchor |
| §5 | active rows, ideas per ledger, per delta and per dissection, ledger and dissection prose length |
| §7 | no `METHOD.md` §6 string in any output |
| inputs | `BASKET.md` rows parse — id, role and status from their sets, no duplicate id; `METHOD.md` carries its spine and one bullet per `#### [C#]` |

```bash
python3 linters/check-distinction-format.py            # $PROBE_PRIVATE_DIR
python3 linters/check-distinction-format.py ~/probe-private
```

What the lint cannot see is whether a difference is a difference — whether §2
names an axis on which the two really chose differently, or restates a paper's
abstract against a config key — whether §3 came from the paper's own
ablation rather than from what it did not mention, and whether a quote says
what the bullet claims it says. Those are the verify pass's (prompt step 6):
a separate agent that never saw the ledger being written reads it against the
original and grades every paper-side statement (§4-1). The writer reads its
own work with the reasons it wrote it; the verifier reads only the page. The
audit (prompt step 7) sends a ledger nothing changed under back to a fresh
verifier and re-resolves its code and method anchors, so a miss or a moved
line does not stand for longer than a week. A dissection gets readers of
its own (prompt D2 and D4): the errata pass reads the rewrite against the
original before anything is written on it, and a code reader opens every
`path:line` and `cfg:` anchor and checks it says what the bullet uses it
for.
