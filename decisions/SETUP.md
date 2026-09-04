# Stress-Test Setup Guide

Deploying the monthly stress-test routine — a cloud session that reads the
month just ended and commits one memo straight to `main`. It is the second
scheduled routine in this repo; the first is the per-pillar scouting run
(`scouting/SETUP.md`). The on-demand tracks (`/analyze`, `/compare`) need no
routine setup.

| | Monthly stress-test routine |
|---|---|
| **Where** | The **RemoteTrigger form** at [claude.ai/code/routines](https://claude.ai/code/routines) or the `/schedule` CLI, never a repo config file |
| **Durable asset** | The prompt `.claude/prompts/stress.txt`. **One** routine, pasted whole — the prompt carries no deployment token to substitute |
| **Retrieval** | None. The routine reads this repository and nothing else |
| **Output** | The prompt commits `decisions/YYYY-MM.md` + `decisions/MAP.md` and runs `git push origin HEAD:main`. No PR — commit history *is* the research log |

## 1. Prerequisites

| Item | Note |
|---|---|
| Claude Code Pro plan | Routines need cloud execution. One run a month is a rounding error against the scouting cadence |
| GitHub repo connected | The routine pushes to `main` in this repo |
| At least one OPEN decision | A memo covers exactly the OPEN set (`decisions/AUTHORING.md` §2). With none open there is nothing to stress-test — pause the routine rather than letting it write an empty file |

## 2. Environment

Routine → **Edit routine** → cloud icon → gear → **Update cloud environment**.
Changes apply to **new sessions only**.

- **Network allowlist — nothing to add.** The run makes no outbound call: its
  sources are `context/`, `scouting/`, `analysis/`, `comparison/` and
  `git log`, all local to the checkout. The default **Trusted** setting is
  enough, and a host list added here would only be misleading. A run that finds
  itself wanting `curl` is reading the wrong source.
- **Environment variables — none.** There is no API key to set and no
  `SEMANTIC_SCHOLAR_API_KEY` equivalent.

## 3. Routine

| Form field | Value |
|---|---|
| Name | `probe-monthly-stress` |
| Prompt (Instructions) | The full body of `.claude/prompts/stress.txt`, pasted as-is — no substitution. Model → **Sonnet** |
| Repositories | This repo |
| Environment | The default one from §2 |
| Trigger | Monthly, the **2nd at 06:00 KST** — `0 21 1 * *` in UTC |
| Connectors | None |
| Permissions | Must allow pushing to `main` — the default `claude/`-branch-only push is not sufficient |

- **Why the 2nd and not the 1st.** The window is the previous calendar month,
  and the scouting runs dated on the 1st land that morning. Starting on the 2nd
  means the month the memo reads is complete on disk when it starts reading.
- The form has no `context_files` field and needs none — the prompt names its
  own sources and resolves the window itself from `TZ=Asia/Seoul date`.
- Set the environment to **at most one active session**. The routine writes two
  files that every future run rewrites; concurrent runs race on both.

### 3-1. Re-paste after every prompt change

The form stores a **copy** of the prompt body, not a reference to the file. A
merged change to `.claude/prompts/stress.txt` reaches nothing until the routine
is edited and the body re-pasted. One routine, one paste — but the same rule as
the scouting fleet, and the same failure when it is skipped: the repo's contract
and the deployed contract drift apart with nothing on either side saying so.

## 4. First run

Use **Run now** on the routine detail page. A green status only means "exited
without an infra error" — open the transcript. Format belongs to the prompt's
SELF-CHECK and `linters/check-decisions-format.py`; what a first run checks is
that those fired and that the boundaries held:

- [ ] The transcript shows `linters/check-decisions-format.py` running on the
      memo and **exiting 0** before the commit. A run that skipped it, or
      committed while it still reported violations, is the failure to catch
      here — CI on `main` only reports after the fact.
- [ ] `decisions/MAP.md` was regenerated and staged in the **same commit** as
      the memo. `python3 decisions/build-map.py --check` on the pushed commit
      must exit 0.
- [ ] `git diff --stat` for the commit shows **no `context/` change** — the
      memo proposes, the human pastes.
- [ ] Every 판정 is one of the three states, and a verdict resting only on
      scouting lines carries `(근거: 리포트 인용만)`.
- [ ] The evidence links open at the quoted line. A link that lands on the file
      but not the claim is the failure the lint cannot see.

If anything fails, fix `.claude/prompts/stress.txt`, **re-paste the corrected
body into the routine** (§3-1) and re-run — do not leave automation on with a
bad prompt.
