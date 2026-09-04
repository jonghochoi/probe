# Decision stress-test authoring

The format contract for `decisions/YYYY-MM.md` — the monthly memo that puts
every OPEN decision back in front of the month's evidence and says whether it
still stands. One file is one month.

`.claude/prompts/stress.txt` owns the *procedure* — which month, where the
evidence comes from, how to verify, how to commit — and defers to this file for
the output contract. Change a rule here first, then the prompt.

The memo is an in-repo document. `site/build-site.py` publishes `analysis/` and
`comparison/` and nothing else, so a memo carries no front matter and no site
conventions; it is read on GitHub, next to the files it links into.

## 1. File convention

| File | Language | Purpose |
|---|---|---|
| `decisions/YYYY-MM.md` | Korean | The stress-test memo. `YYYY-MM` is the calendar month the memo *covers*, never the day it was written — a run on the 2nd of October writes `2026-09.md` |
| `decisions/MAP.md` | mixed | Generated index of where each live decision is cited (§6) |

One run produces exactly one memo. A month with nothing in it still gets its
file: a month where no verdict moved is a finding about the decisions, and a
missing file cannot be told apart from a run that never happened.

The prose is Korean and **개조식** — labelled bullets, 명사형 종결 — the
register `scouting/AUTHORING.md` §4-4 fixes, for the same reason: the memo is
scanned by a reader hunting the verdict, not read end to end. Two things stay
verbatim in whatever language they already are: the Decision-Log bullet quoted
under 현재 결정, and the bullet inside the 제안 문안 fence (§4). Both are text
the human pastes or compares character by character.

## 2. Memo spine

```markdown
# 결정 스트레스 테스트 — YYYY-MM

**Window:** YYYY-MM-DD → YYYY-MM-DD · **Reports read:** n · **Rewrites landed:** n · **Open decisions:** n

## D<id> — <title> (P<m>)

### 현재 결정

> <the Decision-Log bullet, verbatim>

### 무엇이 뒤집는가

- **<label>** — <the falsifier, in the bullet's own terms>

### 이달의 증거

| 방향 | 출처 | 요지 |
|---|---|---|
| 지지 | [<한 줄 이름>](../scouting/P1/2026-09-03.md?plain=1#L40) | <한 줄> |

**판정:** <state> — <한 줄>

### 제안 문안

<the ```markdown fence — §4>
```

- **The H1 month is the filename month.** The two carry the same value twice;
  the H1 is the one a reader sees.
- **The metadata line is one line and holds four fields.** `Window` is the
  calendar month's first and last day. `Reports read` counts the
  `scouting/P#/YYYY-MM-*.md` files inside the window, `Rewrites landed` the
  `analysis/` and `comparison/` files committed inside it, `Open decisions` the
  number of `##` sections below — the field is a count, and its arithmetic
  belongs in nothing but itself.
- **One `##` per OPEN decision, in pillar order, and exactly the current OPEN
  set.** An entry is OPEN when its Decision-Log title ends in ` — **OPEN**`.
  The header repeats the log's own title and pillar verbatim, minus that
  suffix — the suffix is why the section exists, not part of the title.
- **A memo naming a settled decision, or missing an open one, is off-contract**
  and the lint refuses it. The reason is the reader: a decision the memo skips
  is indistinguishable, on the page, from a decision the month left untouched,
  and those are opposite findings. The set is read back off `context/P*.md`
  every run, so a decision the human settled mid-month drops out by itself.
- **Four `###` under each `##`, in this order**, and nothing else at that
  level:

| Subsection | What goes in it |
|---|---|
| `현재 결정` | The log bullet, **quoted verbatim** in a `>` block. The memo argues against the text as it stands; a paraphrase is where a verdict starts drifting from the decision it claims to test |
| `무엇이 뒤집는가` | The falsifier, derived from the bullet's **own wording** — the measurement or result the bullet itself says would settle it. A criterion invented this month tests the memo's opinion, not the decision |
| `이달의 증거` | The evidence table, then the 판정 line (§3) |
| `제안 문안` | The proposed replacement bullet (§4) |

- **The evidence table is `| 방향 | 출처 | 요지 |`.** `방향` is one of `지지` /
  `반박` / `무관`. `출처` is a **relative link to the exact line** —
  `?plain=1` opens GitHub's source view and `#L<n>` lands on it:
  `../scouting/P1/2026-09-03.md?plain=1#L40`,
  `../analysis/2608.25798.md?plain=1#L728`,
  `../comparison/fast-loop-without-vision.md?plain=1#L133`. A row without a
  line anchor is an assertion; the anchor is what makes it evidence.
- **`무관` rows earn their place.** A row naming what the month actually
  brought and stating that it does not bear on this decision is the difference
  between "nothing was found" and "nobody looked" — and it is the only way the
  next month can tell which of the two happened.
- **No line opens `#### [D`.** That is the Decision Log's own entry form and
  three parsers in this repo match on it (`context/CLAUDE.md`).

## 3. The verdict line

One per decision, closing `### 이달의 증거`:

```markdown
**판정:** <흔들림 없음 | 재검토 권고 | 뒤집을 증거 도착> — <한 줄>
```

Three states, no fourth, and no hedged fifth spelled differently. They mean:

| State | When |
|---|---|
| `흔들림 없음` | Nothing this month reached the falsifier |
| `재검토 권고` | Evidence pushes on the bullet without settling it — the human should re-read the decision |
| `뒤집을 증거 도착` | The falsifier named under 무엇이 뒤집는가 was met |

**The falsifiability rule.** When no `출처` in that decision's evidence table
links into `analysis/` or `comparison/`, the verdict line ends with the literal
token `(근거: 리포트 인용만)`. The token is **forbidden** when such a link
exists.

A scouting line is a sweep's one-line note about a paper nobody read in full. A
verdict resting on nothing else is a summary of summaries, and it reads exactly
like a verdict resting on a full reading. The contract does not forbid it — a
month whose only signal came from the sweeps is an honest month — it forbids
not saying so. The token is what says so, in five words a reader can grep.

## 4. 제안 문안

The replacement bullet the human would paste into `context/P#.md`, inside a
fenced ` ```markdown ` block:

````markdown
```markdown
- **Working, not settled**: <the bullet as it would read after this month>
```
````

- **Never a `#### [D` heading.** Inside the fence it is a bullet and nothing
  parses it; as a heading it is a second definition of a decision that already
  has one (§2).
- **Never applied.** `context/` is human-owned and read-only to every agent
  track (`context/CLAUDE.md`); the memo proposes and the human pastes it or
  does not. A run that edits a pillar file has broken the boundary the whole
  pipeline rests on.
- **A `흔들림 없음` decision still carries one** — the current bullet, held, and
  one clause on what the month did to it. "Keep" is a proposal, and writing it
  out is what makes the following month's diff readable.

## 5. Enforcement

`linters/check-decisions-format.py` gates the mechanical half. Run it on the
memo before committing — the routine pushes straight to `main`, so this is the
gate that runs in time to matter, and CI is the backstop:

```bash
python3 linters/check-decisions-format.py decisions/YYYY-MM.md
python3 decisions/build-map.py --check
python3 linters/check-decision-refs.py
```

| Rule | Section |
|---|---|
| H1 month agrees with the filename | §2 |
| The metadata line and its four fields, `Open decisions` agreeing with the section count | §2 |
| The `##` set equals the OPEN set in `context/P*.md`, each header repeating the log's title and pillar | §2 |
| The four `###` present, in order, and no fifth | §2 |
| One 판정 line per decision, one of the three states, closing 이달의 증거 | §3 |
| The `(근거: 리포트 인용만)` token present exactly when the evidence table links into no rewrite or comparison | §3 |
| Every relative link resolves once `?plain=1#L…` is stripped | §2 |
| No line opens `#### [D` | §2, §4 |
| Every `D#` cited exists in the Decision Log | `linters/check-decision-refs.py` |
| `MAP.md` matches the corpus | `decisions/build-map.py --check` |

**The contract-effective gate.** `_CONTRACT_EFFECTIVE` in the linter is the day
this contract takes effect; a memo is bound when the month it covers is the last
complete month before that day or later — the first month the track can produce.
A memo backfilled for an earlier month is skipped rather than rewritten.

What the lint cannot see, and review has to: whether the falsifier is the one
the bullet actually implies, whether a `지지` row supports the decision or only
mentions it, and whether the 요지 column says what the linked line says.

## 6. `MAP.md`

`decisions/MAP.md` is generated by `decisions/build-map.py` and committed. It
indexes every live decision to the `analysis/` and `comparison/` sections that
cite it, at the line, so a run can open a decision's history instead of grepping
the corpus for it.

- **Never hand-edited.** Every run regenerates it and the next write overwrites
  an edit.
- **Regenerated and staged in the same commit as the memo**, so the index and
  the month that read it land together.
- **`--check` diffs the committed file against a fresh build** and fails when
  they differ; CI runs it on `decisions/**`.
