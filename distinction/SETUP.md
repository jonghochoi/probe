# Distinction Routine Setup

Running `/distinguish` on the machine that holds the codebase — by hand first,
then on a schedule. The scouting routine runs in the cloud and pushes to
`main`; this one runs **locally** and pushes nothing, because what it reads
and writes must not be in a repository (`distinction/AUTHORING.md` §1).

| | Distinction routine |
|---|---|
| **Where** | A Linux machine with the codebase on disk — a workstation or server that stays on, or one that is not, with a timer that runs a missed job at the next boot |
| **Durable asset** | `.claude/prompts/distinguish.txt` and `distinction/run-distinguish.sh` in the checkout. The schedule runs `git pull` first, so a merged change to either reaches the next run with nothing to re-paste |
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
  MY-METHOD.md     the method card                   human-written     §2-2
  CODEMAP.md       the code digest                   codemap.sh writes §2-3
  codemap.sh       the operator's digest script      human-written     §2-3
  code -> …        symlink to the codebase           or `code:` in MY-METHOD.md §2-4
  versus/          <arxiv-id>.md and .html per paper the routine writes
  scoreboard.md    claims × papers                   the routine writes
  reports/         YYYY-MM-DD.md and .html per run   the routine writes
  deepdive/        <arxiv-id>--<scope>.md and .html  `--deepdive` writes
  .scratch/        the run's working files           the routine writes
```

The two human-written files start from `distinction/templates/BASKET.md` and
`distinction/templates/MY-METHOD.md`. Both are read-only to the routine, as
`context/` is: a change it wants arrives under 제안 in the run's report.

### 2-1. `BASKET.md`

One table, one paper per row.

| Column | Values |
|---|---|
| `arXiv` | the bare id, `YYMM.NNNNN`. The versus note is written only once `analysis/<id>.md` exists in the checkout — `/analyze` it first |
| `alias` | the rewrite's `alias:` where it has one, else a codename of your own |
| `role` | `baseline` it goes in the experiment table · `nearest` the closest prior work · `threat` it could take a claim · `donor` a mechanism to borrow |
| `claims` | the `C#` codes from `MY-METHOD.md` §1 this paper bears on, comma-separated. Empty is allowed and is what the routine asks about first |
| `status` | `active` read every run · `parked` kept, not read · `graduated` carried into the paper, kept for the record |
| `note` | why it is here, one line |

At most 12 `active` rows (`distinction/AUTHORING.md` §5). The routine never
adds a row: a new paper it finds citing a basket paper is a candidate under
제안, and whether it enters is yours.

### 2-2. `MY-METHOD.md`

The private counterpart of `context/MASTER.md`. The public thesis is there and
is pointed at from §0, not repeated. The spine, which the lint reads:

```
# METHOD — <working title>
name: <short name>                    what every output calls this method
code: <absolute path>                 optional; else the `code` symlink

## 0. 문제의식                        the half that cannot be public
## 1. 주장                            #### [C<n>] <title> + one bullet each
## 2. 방법                            architecture, recipe, data — with CODEMAP anchors
## 3. 측정                            benchmarks, metrics, current numbers
## 4. 알려진 약점                     where it can be refuted — the section the versus note's §4 argues with
## 5. 진행 중                         running ablations and what they should show
## 6. 외부 발화 금지                  literal strings no output may carry
```

A claim is one `####` heading and one bullet, like a Decision-Log entry
(`context/CLAUDE.md`): `#### [C1] <title>` then the claim, its 반증 조건 and
the `D#` it implements. Three to five claims is the working range — the
scoreboard has one row per claim, and more rows than the basket can fill leaves
cells empty, while fewer blurs the differences the versus note needs.

### 2-3. `CODEMAP.md` and `codemap.sh`

The routine reads the codebase through a digest, not whole: a repository does
not fit a context window, and the versus note's code anchors have to be lines that
exist. `codemap.sh` is yours — it lives in the private folder, is run by the
routine at the start of every run, and must write `CODEMAP.md` next to itself.
What it writes is the contract:

| Section of `CODEMAP.md` | Holds | Every entry carries |
|---|---|---|
| `## Modules` | the module tree, one line per file with its one-line purpose | `path` |
| `## Config` | every config key with its default and the file that defines it | `cfg:<key>` and `path:line` |
| `## Entry points` | the classes and functions a versus note would name — signature and docstring first line | `path:line` |
| `## Results` | the current numbers, from the experiment logs, as a table | the run or log the row comes from |

Run with no arguments, `codemap.sh` digests the code `MY-METHOD.md` describes
into `CODEMAP.md`. `--deepdive` also calls it as `codemap.sh <scope> <out>`:
`<scope>` is a bare name (`[a-z0-9_]+`) the script maps to a part of the
codebase — which part is the script's alone, and no file in the checkout
names it — and `<out>` is where the digest of that part goes, in the same
four sections. A scope the script does not know exits non-zero and writes
nothing, which stops the run.

A digest that lists a key without its file gives the versus note nothing to cite
(`distinction/AUTHORING.md` §4). With no `codemap.sh` the routine reads the
`CODEMAP.md` it finds and notes its age in the report; with no `CODEMAP.md`
either, it stops.

### 2-4. `code`

Either a symlink `code` in the private folder pointing at the codebase, or a
line `code: <absolute path>` under the H1 of `MY-METHOD.md`. The routine opens it
only to `grep` for an anchor the digest lacks, never to read a directory.

### 2-5. `PROBE_PRIVATE_DIR`

Set by the scheduler entry (§4), or exported by hand before a session.
The prompt's first step stops when it is unset or names no `BASKET.md`, so the
routine cannot run in a cloud session by mistake.

## 3. By hand

From the checkout root, in a Claude Code session on the machine:

```bash
export PROBE_PRIVATE_DIR="$HOME/probe-private"
claude --add-dir "$PROBE_PRIVATE_DIR"
# then, in the session:
/distinguish            # delta mode
/distinguish <alias>    # one versus note
/distinguish --all      # every active row
/distinguish --deepdive <alias> <scope>   # one paper against one code scope
```

Each versus note, report and deep dive has a page drawn from its Markdown
(`distinction/AUTHORING.md` §3-6). After editing one by hand, draw them
again:

```bash
python3 distinction/render-distinction.py          # every page in $PROBE_PRIVATE_DIR
```

`--add-dir` is what lets the session write outside the checkout. The first
run is `--all`, with two or three active rows and the `MY-METHOD.md` sections 1
and 4 written with care: those two sections are what the versus note argues with,
and the first versus notes are what the rules in `distinction/AUTHORING.md` are
tightened against.

## 4. The schedule

The scheduler calls `distinction/run-distinguish.sh` in the checkout. The
script finds the checkout from its own path, appends everything it prints to
`$PROBE_PRIVATE_DIR/reports/distinguish.log`, stops unless the checkout is on
`main`, pulls, and runs `/distinguish` in delta mode with `claude -p` — which also
audits half the active versus notes (prompt step 7).

`-p` runs one turn with no one to approve a tool, so the script grants every
tool the procedure uses up front and nothing it must not — no `git add`,
`commit` or `push`. `Agent` is the verify pass (prompt step 6); without it the
run stops before saving. A headless run also refuses any command that expands
a shell variable, which is why the prompt reads the folder once with
`printenv` and writes its path out in every command after. The tool list
lives in the script alone, so a change to it reaches the schedule through the
pull, like a prompt change. Check the flag names against `claude --help` on
the machine before the first scheduled run.

The scheduler entry is the machine-specific half — it names the checkout,
sets `PROBE_PRIVATE_DIR`, and puts `claude` on `PATH`, which a scheduled job
does not inherit from the login shell. Twice a week, Tuesday and Thursday at
noon — the cadence the audit is sized to, so every versus note is re-read within
the week (`distinction/AUTHORING.md` §5) — with a missed run made up at the
next boot:

| Scheduler | Entry |
|---|---|
| **systemd timer** (Linux) | A user service and timer, below. `Persistent=true` fires a timer missed while off at the next boot |
| **cron** (Linux) | `0 12 * * 2,4 PROBE_PRIVATE_DIR=$HOME/probe-private PATH=$HOME/.local/bin:/usr/bin:/bin <checkout>/distinction/run-distinguish.sh`. cron does not make up a missed run — on a machine that is not always on, use the timer or `anacron` |

The systemd pair, in `~/.config/systemd/user/`:

```ini
# distinguish.service
[Service]
Type=oneshot
Environment=PROBE_PRIVATE_DIR=%h/probe-private
Environment=PATH=%h/.local/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=<checkout>/distinction/run-distinguish.sh

# distinguish.timer
[Timer]
OnCalendar=Tue,Thu *-*-* 12:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

`systemctl --user enable --now distinguish.timer` starts it, and
`systemctl --user start distinguish.service` runs it once now. A user timer
runs only while the user is logged in unless `loginctl enable-linger` is on.
The log is the place to read a run that no one watched. When the private
folder is a git repository of its own — the way to keep its history — its
`.gitignore` lists the log, `.scratch/`, `CODEMAP.md` (regenerated each run)
and `code`.

One run at a time: the report reads the previous run's state block, and two
runs reading the same block write two reports against one baseline.

## 5. First run

Run `/distinguish --all` by hand (§3) before the schedule, then check:

- [ ] The session stopped at step 0 when `PROBE_PRIVATE_DIR` was unset, and
      ran when it was set — the guard works.
- [ ] `codemap.sh` ran and `CODEMAP.md` carries `path:line` and `cfg:` anchors
      in every section (§2-3). A digest without them gives the versus note nothing
      to cite.
- [ ] `python3 linters/check-distinction-format.py` exits 0 over the folder,
      and the transcript shows it ran before anything was saved.
- [ ] The transcript shows one verify agent per versus note (prompt step 6), and
      its rows were applied — no §3 gap or §6 threat stands on a 재작성본 or
      추론 grade (`distinction/AUTHORING.md` §4-1).
- [ ] Every versus note §2 row names an axis on which the two really chose
      differently, and every §3 row came from the paper's own ablation or
      stated limit — the two things the lint cannot see
      (`distinction/AUTHORING.md` §8).
- [ ] `reports/<date>.md` ends in a `probe-state` block, and a second `/distinguish`
      run on a later day writes a no-change report, rewrites no versus note, and
      lists the versus notes it audited under `8 감사` with their dates in
      `verified`.
- [ ] `git status` in the checkout is clean. Nothing the run wrote is there.

If a check fails, fix `.claude/prompts/distinguish.txt`, `distinction/AUTHORING.md`
or the private files, re-run by hand, and only then let the schedule run.
