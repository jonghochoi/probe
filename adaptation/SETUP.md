# Adaptation Setup

Running `/adapt` — NotebookLM draws a slide deck, an infographic, an audio
overview or a mind map from one rewrite, and the routine checks every drawn
page against the original (`adaptation/AUTHORING.md`). It runs by hand, on
a machine with a browser, because NotebookLM is reached through a signed-in
Google session and meters its generation.

| | Adaptation routine |
|---|---|
| **Where** | Your own machine — the Google session lives in its browser profile |
| **Reads** | The checkout: `analysis/<id>.md` through `site/query.py`, `context/MASTER.md` and the Decision Log |
| **Sends** | The rewrite, the arXiv original's URL and `brief.md` — to NotebookLM, nothing else |
| **Writes** | The folder `PROBE_ADAPT_DIR` names. No commit, no PR, no site |

## 1. Prerequisites

| Item | Note |
|---|---|
| A dedicated Google account | The CLI drives NotebookLM through its web session, and `language set` is account-wide. Keep it apart from the account your mail and Drive live on; a free account is enough |
| `notebooklm-py` | `uv tool install "notebooklm-py[browser]"` (or `pipx install`). An unofficial client of undocumented Google endpoints: it can break without notice, and its terms are Google's |
| Login | `notebooklm login` opens a browser once; `notebooklm auth check --test` exits 0 when the session is good. The session lasts a few weeks — run `login` again when the routine stops at step 1. Never the `--master-token` login: it is a full-account credential |
| Output language | `notebooklm language set ko`, once. The routine never changes it |
| Flags | The procedure's commands follow `notebooklm-py`'s CLI reference. Before the first kit, run `notebooklm generate --help` and `notebooklm download --help` and check that `--prompt-file`, `-n` and `--wait` are there |
| Quota | Generation is rate-limited per account. `notebooklm usage` shows the window; a run that hits it stops and says which kind failed |

## 2. The folder

One folder **outside the checkout** — `~/probe-adapt` in every example here —
named by `PROBE_ADAPT_DIR`. Its layout is `adaptation/AUTHORING.md` §2. The
CLI keeps its own session and settings under your home directory, apart from
it. Each run makes a fresh notebook in the account, named
`PROBE <id> <alias> <date>`; the check note records its id, and deleting old
notebooks is yours.

When the folder is a git repository of its own, its `.gitignore` lists
`.scratch/` and the drawn files (`*/*.pdf`, `*.pptx`, `*.png`, `*.mp3`,
`*.json`), which are large and drawn again on demand.

## 3. By hand

From the checkout root:

```bash
export PROBE_ADAPT_DIR="$HOME/probe-adapt"
claude --add-dir "$PROBE_ADAPT_DIR"
# then, in the session:
/adapt <alias>                       # a slide deck
/adapt <alias> slide-deck,audio      # the kinds named
```

`--add-dir` is what lets the session write outside the checkout. Set
`PROBE_PRIVATE_DIR` too when you run `/distinguish` on the same machine: the
lint then also checks every brief for the `MY-METHOD.md` §6 strings before
it is sent.

## 4. First kit

Check the first kit by hand:

- [ ] The session stopped at step 1 when `notebooklm auth check --test`
      failed, and ran once you logged in.
- [ ] `<id>--<alias>/check.md` lists exactly two sources under `1 소스`, and
      `python3 linters/check-adaptation-format.py` exits 0.
- [ ] Every slide `3 대조` grades other than `맞음` is one you agree is wrong,
      and every one still wrong is under `4 남은 오류`.
- [ ] The deck is Korean, follows the rewrite's acts, and states no number
      the 요약 tab does not carry.
- [ ] `git status` in the checkout is clean.

If a check fails, fix `.claude/prompts/adapt.txt` or
`adaptation/AUTHORING.md`, and run again.

Share a kit the way you would share your own notes on a paper — it is drawn
from someone else's work — and never through `notebooklm share`.
