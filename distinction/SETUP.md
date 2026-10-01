# Distinction Routine Setup

Running `/distinguish` on the machine that holds the codebase — by hand first,
then on a schedule. The scouting routine runs in the cloud and pushes to
`main`; this one runs **locally** and pushes nothing, because what it reads
and writes must not be in a repository (`distinction/AUTHORING.md` §1).

| | Distinction routine |
|---|---|
| **Where** | A machine with the codebase on disk — a workstation or server that stays on, or a laptop with a scheduler that runs a missed job at the next wake |
| **Durable asset** | `.claude/prompts/distinguish.txt` in the checkout. The schedule runs `git pull` first, so a merged prompt change reaches the next run with nothing to re-paste |
| **Reads** | The checkout (`context/`, `analysis/` through `site/query.py`) and the private folder (§2) |
| **Writes** | The private folder only. No commit, no PR, no site |

## 1. Prerequisites

| Item | Note |
|---|---|
| Claude Code CLI on the machine, logged in | `claude --version` prints; `claude -p "say ok"` answers without a prompt |
| `python3` | `site/query.py` and the lint are standard library only |
| A checkout of this repository | Kept current by the schedule's `git pull`; `/distinguish` runs from its root |
| The codebase | On the same disk, at a path the private folder points at (§2-4) |

## 2. The private folder

One folder **outside the checkout** — `~/probe-private` in every example here
— named by the environment variable `PROBE_PRIVATE_DIR`. Outside, because a
folder inside the checkout is one `git add -A` away from the public remote
even when `.gitignore` lists it.

```
$PROBE_PRIVATE_DIR/
  BASKET.md        the basket                        human-written     §2-1
  METHOD.md        the method card                   human-written     §2-2
  CODEMAP.md       the code digest                   codemap.sh writes §2-3
  codemap.sh       the operator's digest script      human-written     §2-3
  code -> …        symlink to the codebase           or `code:` in METHOD.md §2-4
  ledger/          one <arxiv-id>.md per basket paper the routine writes
  matrix.md        claims × papers                   the routine writes
  runs/            one YYYY-MM-DD.md per run         the routine writes
```

The two human-written files start from `distinction/templates/BASKET.md` and
`distinction/templates/METHOD.md`. Both are read-only to the routine, as
`context/` is: a change it wants arrives under 제안 in the run's delta.

### 2-1. `BASKET.md`

One table, one paper per row.

| Column | Values |
|---|---|
| `arXiv` | the bare id, `YYMM.NNNNN`. The ledger is written only once `analysis/<id>.md` exists in the checkout — `/analyze` it first |
| `alias` | the rewrite's `alias:` where it has one, else a codename of your own |
| `role` | `baseline` it goes in the experiment table · `nearest` the closest prior work · `threat` it could take a claim · `donor` a mechanism to borrow |
| `claims` | the `C#` codes from `METHOD.md` §1 this paper bears on, comma-separated. Empty is allowed and is what the routine asks about first |
| `status` | `active` read every run · `parked` kept, not read · `graduated` carried into the paper, kept for the record |
| `note` | why it is here, one line |

At most 12 `active` rows (`distinction/AUTHORING.md` §5). The routine never
adds a row: a new paper it finds citing a basket paper is a candidate under
제안, and whether it enters is yours.

### 2-2. `METHOD.md`

The private counterpart of `context/MASTER.md`. The public thesis is there and
is pointed at from §0, not repeated. The spine, which the lint reads:

```
# METHOD — <working title>
code: <absolute path>                 optional; else the `code` symlink

## 0. 문제의식                        the half that cannot be public
## 1. 주장                            #### [C<n>] <title> + one bullet each
## 2. 방법                            architecture, recipe, data — with CODEMAP anchors
## 3. 측정                            benchmarks, metrics, current numbers
## 4. 알려진 약점                     where it can be refuted — the section the ledger's §4 argues with
## 5. 진행 중                         running ablations and what they should show
## 6. 외부 발화 금지                  literal strings no output may carry
```

A claim is one `####` heading and one bullet, like a Decision-Log entry
(`context/CLAUDE.md`): `#### [C1] <title>` then the claim, its 반증 조건 and
the `D#` it implements. Three to five claims is the working range — the
matrix has one row per claim, and more rows than the basket can fill leaves
cells empty, while fewer blurs the differences the ledger needs.

### 2-3. `CODEMAP.md` and `codemap.sh`

The routine reads the codebase through a digest, not whole: a repository does
not fit a context window, and the ledger's code anchors have to be lines that
exist. `codemap.sh` is yours — it lives in the private folder, is run by the
routine at the start of every run, and must write `CODEMAP.md` next to itself.
What it writes is the contract:

| Section of `CODEMAP.md` | Holds | Every entry carries |
|---|---|---|
| `## Modules` | the module tree, one line per file with its one-line purpose | `path` |
| `## Config` | every config key with its default and the file that defines it | `cfg:<key>` and `path:line` |
| `## Entry points` | the classes and functions a ledger would name — signature and docstring first line | `path:line` |
| `## Results` | the current numbers, from the experiment logs, as a table | the run or log the row comes from |

A digest that lists a key without its file gives the ledger nothing to cite
(`distinction/AUTHORING.md` §4). With no `codemap.sh` the routine reads the
`CODEMAP.md` it finds and notes its age in the delta; with no `CODEMAP.md`
either, it stops.

### 2-4. `code`

Either a symlink `code` in the private folder pointing at the codebase, or a
line `code: <absolute path>` under the H1 of `METHOD.md`. The routine opens it
only to `grep` for an anchor the digest lacks, never to read a directory.

### 2-5. `PROBE_PRIVATE_DIR`

Exported by the schedule's wrapper script (§4), or by hand before a session.
The prompt's first step stops when it is unset or names no `BASKET.md`, so the
routine cannot run in a cloud session by mistake.

## 3. By hand

From the checkout root, in a Claude Code session on the machine:

```bash
export PROBE_PRIVATE_DIR="$HOME/probe-private"
claude --add-dir "$PROBE_PRIVATE_DIR"
# then, in the session:
/distinguish            # delta mode
/distinguish <alias>    # one ledger
/distinguish --all      # every active row
```

`--add-dir` is what lets the session write outside the checkout. The first
run is `--all`, with two or three active rows and the `METHOD.md` sections 1
and 4 written with care: those two sections are what the ledger argues with,
and the first ledgers are what the rules in `distinction/AUTHORING.md` are
tightened against.

## 4. The schedule

A wrapper script the scheduler calls — `$PROBE_PRIVATE_DIR/run-distinguish.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
export PROBE_PRIVATE_DIR="$HOME/probe-private"
cd "$HOME/src/probe"
git pull --ff-only origin main
claude -p "/distinguish" \
  --add-dir "$PROBE_PRIVATE_DIR" \
  --allowedTools "Read,Write,Edit,Glob,Grep,Bash(python3 *),Bash(git log *),Bash(git rev-parse *),Bash(grep *),Bash(sha256sum *),Bash(sh *),Bash(cd *)" \
  >> "$PROBE_PRIVATE_DIR/runs/distinguish.log" 2>&1
```

`-p` runs one turn without a terminal, so every tool it needs is granted up
front; the list above is what the procedure uses and nothing it must not (no
`git add`, `commit` or `push`). Check the flag names against `claude --help`
on the machine before the first scheduled run.

Weekly, with a missed run made up at the next wake:

| Scheduler | Entry |
|---|---|
| **launchd** (macOS) | A `LaunchAgents` plist with `StartCalendarInterval` (`Weekday`, `Hour`, `Minute`) and `ProgramArguments` naming the script. A job whose time passed while the machine slept runs when it wakes |
| **systemd timer** (Linux) | `OnCalendar=weekly` with `Persistent=true`, so a timer missed while off fires at the next boot |
| **cron** (Linux) | `0 7 * * 1 $HOME/probe-private/run-distinguish.sh`. cron does not make up a missed run — on a machine that is not always on, use the timer or `anacron` |

One run at a time: the delta reads the previous run's state block, and two
runs reading the same block write two deltas against one baseline.

## 5. First run

Run `/distinguish --all` by hand (§3) before the schedule, then check:

- [ ] The session stopped at step 0 when `PROBE_PRIVATE_DIR` was unset, and
      ran when it was set — the guard works.
- [ ] `codemap.sh` ran and `CODEMAP.md` carries `path:line` and `cfg:` anchors
      in every section (§2-3). A digest without them gives the ledger nothing
      to cite.
- [ ] `python3 linters/check-distinction-format.py` exits 0 over the folder,
      and the transcript shows it ran before anything was saved.
- [ ] Every ledger §2 row names an axis on which the two really chose
      differently, and every §3 row came from the paper's own ablation or
      stated limit — the two things the lint cannot see
      (`distinction/AUTHORING.md` §8).
- [ ] `runs/<date>.md` ends in a `probe-state` block, and a second `/distinguish`
      run straight after writes a no-change delta and rewrites no ledger.
- [ ] `git status` in the checkout is clean. Nothing the run wrote is there.

If a check fails, fix `.claude/prompts/distinguish.txt`, `distinction/AUTHORING.md`
or the private files, re-run by hand, and only then let the schedule run.
