# Scouting Routine Setup

Deploying the scheduled scouting routine — a cloud session that commits its
own reports straight to `main`. The on-demand commands need none of this and
runs from any Claude Code session.

| | Scheduled scouting routine |
|---|---|
| **Where** | The **RemoteTrigger form** at [claude.ai/code/routines](https://claude.ai/code/routines) or the `/schedule` CLI, never a repo config file |
| **Durable asset** | The prompt `.claude/prompts/scouting.txt` in the checkout. One routine covers every pillar, given as its argument |
| **Retrieval** | `curl` to arXiv and Semantic Scholar, never MCP — a cloud session cannot reach a local MCP server |
| **Output** | One commit per run — every pillar's report and the run file — pushed with `git push origin HEAD:main`. No PR: commit history *is* the research log. The push redeploys the reading site with the run's page |

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

One routine runs every pillar. Its prompt is one line that points at the
files in the checkout, so a merged change to the prompt or the contract
reaches the next run with nothing re-pasted.

| Form field | Value |
|---|---|
| Name | `probe-scout` |
| Prompt (Instructions) | `Read .claude/prompts/scouting.txt and run PART I with pillars: 0 1 2 3 4` — the pillar numbers are the one argument. Model → **Sonnet** |
| Repositories | This repo |
| Environment | The one from §2 |
| Trigger | A recurring cadence of your choosing (the form takes local time → UTC, min interval 1 h) |
| Connectors | None — retrieval is `curl`, not a connector |
| Permissions | Must allow pushing to `main` — the default `claude/`-branch-only push is not sufficient |

- The session is the master: it dispatches one pillar agent per pillar in
  parallel, one paper judge, then the pillar agents again to write, and
  commits once (`.claude/prompts/scouting.txt`). A run therefore lasts about
  as long as its slowest pillar plus the judge, not five pillars end to end.
- Set the environment to **at most one active session** — two runs of one
  date would write the same files. The prompt keeps a `git pull --rebase`
  retry as a backstop.
- Fewer pillars is a different argument, not a different routine:
  `… with pillars: 1 3` runs P1 and P3, and the run file lists only those.
- `/scout 0 1 2 3 4` (`.claude/commands/scout.md`) runs the same thing from an
  interactive session.
- The pillar agents never read `context/MASTER.md`, so its Venue Priority and
  Cross-pollination Budget are inlined in the prompt's shared section. Keep
  them in sync with `context/MASTER.md` §5–§6.

## 4. First run

Use **Run now** on the routine detail page. A green status only means "exited
without an infra error" — open the transcript. Report format and evidence
rules belong to the prompt's SELF-CHECK (step 8) and
`linters/check-scouting-format.py`. What a first run checks is that those
gates fired, and that the environment is sound:

- [ ] The transcript shows `linters/check-scouting-format.py` running on the
      run file and every report and exiting 0 (PART I step 7). A run that skipped it, or
      committed while it still reported violations, is the failure to catch
      here — CI on `main` only reports after the fact.
- [ ] The `Papers scanned:` header discloses **no** `curl` 403 / network-block
      error. One there means the Custom allowlist is missing.
- [ ] The Anti-topics filter fired — 🔄 reports a filter count. A run that
      dropped nothing is suspicious.
- [ ] Implications are concrete — (c) names a specific cost, number or
      transfer caveat in plain terms, and a 🔄 Decision-Log bullet names the
      decision and the paper that moved it, not "tune DR wider".

If anything fails, fix `.claude/prompts/scouting.txt` (or `context/P1.md`),
merge it and re-run — do not
leave automation on with a bad prompt.
