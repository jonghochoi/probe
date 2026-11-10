# Adaptation authoring

The format contract for what `/adapt` writes: one kit per paper — a slide
deck, an infographic, an audio overview or a mind map that NotebookLM draws
from one rewrite, with the brief that was sent and a check note that grades
every drawn page against the original. `.claude/prompts/adapt.txt` owns the
procedure and defers to this file for what the kit must look like;
`adaptation/SETUP.md` owns the account, the CLI and the folder. Edit this
file first, then the prompt, then the lint.

## 1. The two rules

**Only public material goes to NotebookLM.** The sources are the rewrite
`analysis/<id>.md` and the arXiv original at the version the rewrite read
(its `arxiv_html:` or `arxiv_src:`), and the instructions sent are `brief.md`, written from
the rewrite and `context/` alone. Nothing of the operator's private folder
(`distinction/SETUP.md` §2) is read, uploaded or quoted into a brief, and a
kit says nothing about the operator's own method.

**Nothing this track writes reaches the repository.** A kit is generated
from someone else's paper and is checked only as far as its check note says,
so it is not published: it lives in the folder `PROBE_ADAPT_DIR` names,
outside the checkout, and the track has no site section and no commit step.
Only a paper with a rewrite in `analysis/` gets a kit.

## 2. The folder

```
$PROBE_ADAPT_DIR/
  <arxiv-id>--<alias>/   one kit per paper — overwritten by the next run on it
    brief.md             the instructions sent, one `##` per kind    written first, linted before it is sent
    check.md             the check note                              written last
    slides.pdf           `slide-deck`, and slides.pptx beside it
    infographic.png      `infographic`
    audio.mp3            `audio`
    mindmap.json         `mind-map`
  .scratch/              the run's working files; read by nothing after the run
```

Only the kinds the run asked for are present. `<alias>` is the rewrite's
`alias:` with every run of whitespace turned into `-`, or the id when the
rewrite has none — the rule `distinction/AUTHORING.md` §2 fixes for its
files.

## 3. The documents

Both are Korean, in the register `scouting/AUTHORING.md` §4 fixes. Section
headers are fixed strings: the lint matches them verbatim.

### 3-1. The brief — `brief.md`

```
# <alias> 각색 지시문
Paper: XXXX.XXXXX · Rewrite: analysis/XXXX.XXXXX.md · Run: YYYY-MM-DD

## slide-deck
<NotebookLM 에 보내는 지시 — 한국어>
## audio
<…>
```

Each `##` is a kind exactly as the NotebookLM CLI names it — `slide-deck`,
`infographic`, `audio`, `mind-map` — and its body is the text sent as that
kind's prompt, verbatim. The body:

- asks for Korean and names the reader — the researcher `context/MASTER.md`
  §1 describes;
- follows the rewrite's thesis and its four acts, in order;
- gives the numbers the rewrite's 요약 cards carry, with their units, and
  asks that no other number be stated;
- leaves the pictures to NotebookLM — its own illustrations, scenes and
  metaphors carry the deck, and nothing points at the original's figure
  numbers, because a reader who needs the original's figures reads the
  original — but asks that a drawn mechanism follow the paper's own steps
  and arrows, and that no shape's size, length or position stand for a
  quantity — a bubble, a bar, an axis — so the numbers stand as text;
- asks that each claim keep the original's strength: its hedges stay ("개선
  여지", not "취약"), and no word of degree ("급락", "수직 하락") is added;
- closes on the paper's own stated limits and the `D#` its act 4 argues
  with, each `D#` beside the paper's fact that bears on it and no reading
  of ours added to it.

It carries no anchor of the private side — no `C#`, `METHOD §n`, `cfg:` or
`path:line` — because it is the one text that leaves the machine.

### 3-2. The check note — `check.md`

```
# <alias> 각색 점검 — <한 문장: 이 키트를 보여 주기 전에 알아야 할 것>
Paper: XXXX.XXXXX · Rewrite: analysis/XXXX.XXXXX.md · Notebook: <NotebookLM notebook id> · Run: YYYY-MM-DD

## 1 소스
## 2 생성물
## 3 대조
## 4 남은 오류
```

| Section | Holds | Each bullet carries |
|---|---|---|
| `1 소스` | Every source the notebook holds, one bullet each | exactly `` `analysis/<id>.md` `` or the arXiv URL of the read version — nothing else may stand here |
| `2 생성물` | One bullet per kind made | the kind in backticks, its file names, then `점검함` or `미점검` — audio is always `미점검`, because no reader here hears it |
| `3 대조` | One line `점검 N · 맞음 n · 틀림 n · 과장 n · 원문 없음 n`, then one bullet per statement graded other than `맞음` | a verdict first, the place — `slide-deck p.<n>`, `infographic` or `mind-map` — and, but for `원문 없음`, a quote anchor (§4) |
| `4 남은 오류` | Each §3 statement still standing after the revision pass, so a reader knows which slide not to show | the place, and what the original says instead |

A statement is anything a drawn page asserts about the paper: a number, a
method or model name, a mechanism step, a causal claim, a stated limit, and
the values and arrows of a drawn chart or diagram. The grades:

| Grade | Means |
|---|---|
| `맞음` | the original says it |
| `틀림` | the original says otherwise |
| `과장` | the original says less — a narrower setting, a hedge dropped, an average presented as a minimum |
| `원문 없음` | the original does not say it |

`4 남은 오류` holds `- 없음` when the revision pass left nothing standing —
the only state in which the kit is ready to show as it is.

## 4. Anchors

A quote anchor is `원문 §<section> "<verbatim English>"` — at least a clause,
copied byte for byte, a table row quoted whole under `§TABLE-<n>` — and
resolves through `cd site && python3 -m builder.arxiv <id> --grep "<a phrase
of it>"`, as `distinction/AUTHORING.md` §4 defines it.

## 5. Caps

| What | Cap | Why |
|---|---|---|
| Brief per kind | 2,000 characters | NotebookLM follows a short instruction; a longer one restates the rewrite it already holds as a source |
| Revision passes on the slides | 1 | what one pass does not fix is the operator's to judge, under `4 남은 오류` |

## 6. Enforcement

`linters/check-adaptation-format.py` reads the folder (`PROBE_ADAPT_DIR`, or
a path argument). It is the routine's own gate — the prompt runs it before a
brief is sent and before the check note is final — and it is in no workflow,
because what it checks is in no checkout.

| Rule | Check |
|---|---|
| §2 | the kit's folder name and both files' metadata agree, `analysis/<id>.md` exists; a folder holding a drawn file has a `check.md` |
| §3-1 | the brief holds only kind headers, each once and not empty; no `C#`, `METHOD §n`, `cfg:` or `path:line` anchor; and, when `PROBE_PRIVATE_DIR` is set, no `MY-METHOD.md` §6 string |
| §3-2 | the four headers verbatim and in order; every §1 bullet the rewrite or an arXiv URL of that id; every §2 bullet a kind and `점검함` or `미점검`, audio `미점검`, its files present; §3 its count line and every bullet a verdict, a place and — but for `원문 없음` — a quote anchor; every §4 bullet a place |
| §5 | brief length per kind |

```bash
python3 linters/check-adaptation-format.py            # $PROBE_ADAPT_DIR
python3 linters/check-adaptation-format.py ~/probe-adapt
```

What the lint cannot see is whether a grade is right. That is the check
pass's: an agent that did not write the brief reads every drawn page against
the original, and its rows are the check note's §3.
