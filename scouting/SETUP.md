# Agent Setup Guide

Deploying the scheduled scouting routine — a cloud session that commits its
own reports straight to `main`. On-demand `/analyze` needs none of this and
runs from any Claude Code session.

| | Scheduled scouting routine |
|---|---|
| **Where** | The **RemoteTrigger form** at [claude.ai/code/routines](https://claude.ai/code/routines) or the `/schedule` CLI, never a repo config file |
| **Durable asset** | The shared prompt `.claude/prompts/scouting.txt`. Register one routine per pillar (P0–P4) — P1 is the worked example below |
| **Retrieval** | `curl` to arXiv and Semantic Scholar, never MCP — a cloud session cannot reach a local MCP server |
| **Output** | The prompt commits and runs `git push origin HEAD:main`. No PR — commit history *is* the research log |

## 1. Prerequisites

| Item | Note |
|---|---|
| Claude Code Pro plan | Routines need cloud execution. The daily cap covers the scouting cadence |
| GitHub repo connected | The routine pushes to `main` in this repo |

## 2. Environment

Both settings live in one dialog: routine → **Edit routine** → cloud icon →
gear → **Update cloud environment**. Changes apply to **new sessions only** —
the next scheduled run picks them up.

### 2-1. Network allowlist

**Trusted** allows only package registries and GitHub. Everything else gets
`HTTP 403` with `x-deny-reason: host_not_allowed`. Set **Network access →
Custom** and list one host per line:

```
export.arxiv.org
arxiv.org
api.semanticscholar.org
```

Keep **"Also include default list of common package managers"** checked —
unchecking it breaks GitHub/registry access.

### 2-2. `SEMANTIC_SCHOLAR_API_KEY`

Same dialog, under **Environment variables**, `.env` format, no quotes.

- **Prefer keyless.** S2 does not issue keys to free-domain emails, and an
  unapproved key makes the API return 403 *while keyless works*. With the
  variable empty the prompt omits the header, sleeps ~3 s between calls and
  backs off on HTTP 429.
- There is no secret store — environment variables are readable by anyone who
  can edit the environment.

> **Two different 403s.** `x-deny-reason: host_not_allowed` → network layer,
> fix with the allowlist in §2-1. S2 403 *only when the key header is sent* →
> API auth, fix by dropping the key.

### 2-3. Verify

From a fresh session, both must print `200`:

```bash
curl -sS -o /dev/null -w "%{http_code}\n" \
  "https://api.semanticscholar.org/graph/v1/author/search?query=Kevin+Black&fields=name"
curl -sS -o /dev/null -w "%{http_code}\n" \
  "http://export.arxiv.org/api/query?search_query=cat:cs.RO&max_results=1"
```

## 3. Routine

| Form field | Value |
|---|---|
| Name | `probe-weekly-scout` |
| Prompt (Instructions) | The full body of `.claude/prompts/scouting.txt`, every `<PILLAR>` replaced by `P1`. Model → **Sonnet** |
| Repositories | This repo |
| Environment | The one from §2 |
| Trigger | A recurring cadence of your choosing (the form takes local time → UTC, min interval 1 h) |
| Connectors | None — retrieval is `curl`, not a connector |
| Permissions | Must allow pushing to `main` — the default `claude/`-branch-only push is not sufficient |

- Set the environment to **at most one active session** — concurrent runs race
  on the shared branch. The prompt keeps a `git pull --rebase` retry as a
  backstop.
- The form has no `context_files` field and needs none — the prompt names its
  own inputs (`context/P1.md` §1–§5, the last 2 weeks of `scouting/`), the
  `curl` procedure, the scoring contract and the guards.
- A pillar-scoped run never reads `context/MASTER.md`, so the two tables it
  would need from there — Venue Priority and the monthly Cross-pollination
  Budget — are inlined in the prompt's SCORING section. Keep them in sync with
  `context/MASTER.md` §6–§7 when either moves.

### 3-1. Re-paste after every prompt change

The form stores a **copy** of the prompt body, not a reference to the file. A
merged change to `.claude/prompts/scouting.txt` reaches nothing until every
routine is edited and the body re-pasted, `<PILLAR>` substitution redone.

- Six pillars means six routines to update, every time.
- Re-paste all six in one pass. A half-updated fleet has pillars scoring on
  different contracts — exactly the drift the scoring contract
  (`scouting/AUTHORING.md` §5) exists to prevent.
- After the last one, **Run now** on a single pillar and walk §4 before
  letting the cadence resume.

## 4. First run

Use **Run now** on the routine detail page. A green status only means "exited
without an infra error" — open the transcript. Report format and evidence
rules belong to the prompt's SELF-CHECK (step 8) and
`linters/check-scouting-format.py`. What a first run checks is that those
gates fired, and that the environment is sound:

- [ ] The transcript shows `linters/check-scouting-format.py` running on the
      report and exiting 0 (PROCEDURE step 7). A run that skipped it, or
      committed while it still reported violations, is the failure to catch
      here — CI on `main` only reports after the fact.
- [ ] The `Papers scanned:` header discloses **no** `curl` 403 / network-block
      error. One there means the Custom allowlist is missing.
- [ ] The Anti-topics filter fired. An empty "did not pass filter" section is
      suspicious.
- [ ] Decision implications are concrete — a specific config key,
      hyperparameter or metric, not "tune DR wider".

If anything fails, fix `.claude/prompts/scouting.txt` (or `context/P1.md`),
**re-paste the corrected body into every routine** (§3-1) and re-run — do not
leave automation on with a bad prompt.
