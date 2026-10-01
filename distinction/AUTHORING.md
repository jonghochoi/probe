# Distinction authoring

The format contract for the distinction track — the documents `/distinguish`
writes into the private folder: one ledger per basket paper, the claims ×
papers matrix, and one delta per run. Every one of them holds the method
beside the papers, which is why none of them is in this repository.

`.claude/prompts/distinguish.txt` defers to this file for what the documents
must look like, and owns the procedure — what is read, how the delta is found,
how the evidence is confirmed. `distinction/SETUP.md` owns the private folder
itself: where it lives, what the human writes into it, how the machine runs
the routine. Edit this file first, then the prompt, then the lint.

## 1. The one rule

**Nothing this track writes reaches the repository.**

The other tracks publish: a rewrite, a comparison and a talk are pages on the
reading site, and a scouting report is a commit on `main`. A ledger cannot be
either. Its every row sets a basket paper's mechanism next to this method's —
a config key, a stated weakness, a number from a run that has not been
published — and the repository is public. So the track has no output folder
here, no site section, no CI gate and no commit step. The private folder
(`distinction/SETUP.md` §2) is where it reads and the only place it writes.

| Consequence | Where it is written down |
|---|---|
| The prompt has no GIT section; `git add`, `commit` and `push` are forbidden verbs in it | `.claude/prompts/distinguish.txt` |
| The lint runs over the private folder, as the routine's own gate, never in CI | §8 |
| The private folder lives outside the checkout, so no `git add -A` can reach it | `distinction/SETUP.md` §2 |
| Examples in this file, the prompt and the templates use placeholder ids, claims and keys — never a real one | this file |
| A ledger never names what `METHOD.md` §6 lists | §7 |

The other rule the track inherits: **only a paper with a rewrite in
`analysis/` gets a ledger.** The ledger reads the paper through
`site/query.py`, and a paper the corpus has not rewritten has no sections to
read, no act 4 to argue with and no `related` rows. A basket row without a
rewrite is reported in the delta (§3-3) as the next action and left unwritten.

## 2. What the routine reads and writes

Reads, all under `$PROBE_PRIVATE_DIR` and all human-owned:

| File | Role | Schema |
|---|---|---|
| `BASKET.md` | The basket — which papers, in which role, against which claims | `distinction/SETUP.md` §2-1 |
| `METHOD.md` | The method card — the private half of the thesis, the claims `C#`, the recipe, the measurements, the weaknesses, the strings that must not leave | `distinction/SETUP.md` §2-2 |
| `CODEMAP.md` | The code digest the operator's script regenerates at the start of a run — every entry anchored `path:line` or `cfg:key` | `distinction/SETUP.md` §2-3 |
| `code` | The codebase, opened only to `grep` for an anchor the digest lacks | `distinction/SETUP.md` §2-4 |

From the checkout it reads what every other track reads: `context/MASTER.md`,
the pillar files the basket touches, and the corpus through `site/query.py`.

Writes, all under `$PROBE_PRIVATE_DIR`:

| File | One per | Overwritten |
|---|---|---|
| `ledger/<arxiv-id>.md` | basket paper | yes — the ledger is the current position, never a history |
| `matrix.md` | folder | yes |
| `runs/YYYY-MM-DD.md` | run | no — one file per run date, and the previous run's is what the next run diffs against |

## 3. The documents

All three are Korean, in the register `scouting/AUTHORING.md` §4 fixes (§6
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
| `3 그들의 빈자리` | What the paper does not reach, **from its own ablation, failure case or stated limit** — never inferred from silence | a paper anchor, act 4 where it exists |
| `4 내 방법이 메우는가` | For each gap in §3: `메운다`, `부분` or `못 메운다`, then why, against `METHOD.md` §4 | the verdict first, then a `METHOD §n` anchor |
| `5 그들을 개선할 아이디어` | At most two `###` ideas, strongest first, in the shape `/ideate` fixes (§3-4) | the five labels |
| `6 위협` | The condition under which this paper takes a claim: which `C#`, on what number, in which setting | a paper anchor; a number confirmed in the original (§4) |
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

```probe-state
{"run": "YYYY-MM-DD", "corpus_head": "<git sha>", "method": "0000000",
 "codemap": "0000000", "basket": "0000000",
 "related": {"XXXX.XXXXX": ["XXXX.XXXXX", "XXXX.XXXXX"]}}
```
```

Only what changed since the previous run, section by section:

| Section | Holds |
|---|---|
| `1 코퍼스 변화` | Rewrites, comparisons and scouting reports landed since `corpus_head`, **only those `related` to a basket paper**, with the relation kind (`neighbour`, `cites`, `compared_with`, …) |
| `2 바구니 변화` | Rows added, removed or re-roled; rows with no rewrite yet; rows `graduated` |
| `3 방법론 변화` | If `method` or `codemap` moved: which `METHOD.md` sections changed and which ledgers were rewritten because of it; a `METHOD.md` untouched for eight weeks or more earns one line here |
| `4 매트릭스 전이` | Cells whose verdict changed, old to new, with the ledger section behind each |
| `5 새 아이디어` | At most three `###` ideas across the whole run, in the `/ideate` shape (§3-4) — the strongest of what the rewritten ledgers' §5 hold, not a copy of all of them |
| `6 제안` | What the human should change in `BASKET.md` or `METHOD.md`: a basket candidate found citing a basket paper, a claim with no basket column, a row with empty `claims` |
| `7 다음 행동` | `/analyze <id>` for a row without a rewrite, `/compare <id> <id>` where two basket papers need their divergence laid out first, one ablation to run |

The `probe-state` block closes the file and is what the next run reads first:
the checkout's `HEAD` when this run read it, the three input hashes, and the
`related` ids per basket paper as `site/query.py related` returned them. It is
the memory of the track, and it is why a run does not re-read everything.

**The no-change run.** When `corpus_head`, the three hashes and every
`related` list are unchanged, the run writes this file with `- 없음` under
sections 1 to 6, the standing next actions under 7, and the state block. It
rewrites no ledger and leaves the matrix alone. A run that finds nothing and
says so is the track working.

### 3-4. The shape of an idea

A `###` under a ledger's §5 or a delta's §5 is one idea in the five labels
`.claude/prompts/ideate.txt` fixes, each on its own line, bold, in this order:

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

## 4. Anchors

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

Which sections need which is §3-1's table. Two further rules:

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

## 5. Caps

| What | Cap | Why |
|---|---|---|
| `active` basket rows | 12 | past that a run re-reads everything and the delta becomes a reprint |
| Ideas per ledger (§3-1 `5`) | 2 | the ledger is a position, not a brainstorm |
| Ideas per delta (§3-3 `5`) | 3 | `/ideate`'s own ceiling, for the same reason |
| Ledger prose | 7,000 characters outside fences | the comparison ceiling; a ledger past it has started explaining the paper, which its rewrite already does |

## 6. Korean authoring

The register is `scouting/AUTHORING.md` §4 and binds here as written: what
stays verbatim (§4-1 — paper titles, arXiv ids, `C#`, `D#`, config keys,
every anchor), the glossary (§4-2), headers as fixed strings (§4-3), 개조식 /
명사형 종결 (§4-4), and the three render traps — a raw `~` striking out a line
(§4-6), a bare URL swallowing the particle after it (§4-7), a `**` closing
between a paren and a particle (§4-8). The ledger is read on a screen like a
scouting report and fails in the same places.

## 7. What never leaves

`METHOD.md` §6 is a list of literal strings — a codename, a number, a dataset,
a collaborator — that must not appear in any output yet. The lint searches
every ledger, the matrix and every run for each of them and fails on a hit,
and the routine does not save an output the lint fails. The strings are the
human's to list; the track's job is to never be the place one leaks from. A
ledger that needs to say the thing says it by its `C#` or its `METHOD §n`
anchor instead, which is what the anchors are also for.

## 8. Enforcement

`linters/check-distinction-format.py` reads the private folder (`PROBE_PRIVATE_DIR`,
or a path argument) and checks what a document can get wrong while reading
perfectly. It is the routine's own gate — step 6 of the procedure — and it
is run by hand after editing a document. It is in no workflow, because what it
checks is in no checkout.

| Rule | Check |
|---|---|
| §1 | every `ledger/<id>.md` names a `BASKET.md` row and `analysis/<id>.md` exists |
| §3-1 | the H1, the five-field metadata line, the seven headers verbatim and in order, no other `##` |
| §3-1, §4 | per section, every bullet carries the anchors its row of the table requires, or is `- 없음`; a §4 bullet opens with a verdict; §7 holds a `cfg:` anchor |
| §3-2 | the matrix's rows are `METHOD.md`'s claims and its columns the active rewritten basket, each cell opening with a verdict |
| §3-3 | the delta's H1 date is the file's, the seven headers, at most three `###` under `5`, a closing `probe-state` block that parses and carries every key |
| §3-4 | every `###` idea carries the five labels in order; a `D#` it names exists in a pillar's Decision Log |
| §5 | active rows, ideas per ledger and per delta, ledger prose length |
| §7 | no `METHOD.md` §6 string in any output |
| inputs | `BASKET.md` rows parse — id, role and status from their sets, no duplicate id; `METHOD.md` carries its spine and one bullet per `#### [C#]` |

```bash
python3 linters/check-distinction-format.py            # $PROBE_PRIVATE_DIR
python3 linters/check-distinction-format.py ~/probe-private
```

What the lint cannot see is whether a difference is a difference — whether §2
names an axis on which the two really chose differently, or restates a paper's
abstract against a config key — and whether §3 came from the paper's own
ablation rather than from what it did not mention. Read every ledger the run
rewrote once more with only those two questions.
