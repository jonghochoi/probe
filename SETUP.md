# Agent Setup Guide

How to run the scouting routine on a schedule — in the cloud, committing its
own reports directly to `main`. On-demand `/analyze` needs none of this; it
runs from any Claude Code session.

> **Run manually for 1–2 weeks first.** Paste `context/MASTER.md` and the
> `.claude/prompts/scouting.txt` template (one global find/replace of
> `<PILLAR>` → `P0`…`P5`) into a Claude conversation and iterate until the
> report quality is where you want it. Bad prompt + automation = garbage on a
> timer.

## What changes versus a manual run

| | Manual | Routine |
|---|---|---|
| Execution | your laptop | cloud, on a schedule |
| Retrieval | built-in web search | `curl` to arXiv + Semantic Scholar REST — **no MCP** (cloud sessions cannot reach a local MCP server) |
| Output | copy by hand | the prompt commits the report and runs `git push origin HEAD:main` — no PR; commit history *is* the research log |

The durable asset is the prompt (`.claude/prompts/scouting.txt`, shared by
P0–P5), not a config file. There is no `.claude/routines/*.yaml` and no
`claude routine register` — scheduling is created in the **RemoteTrigger form**
at [claude.ai/code/routines](https://claude.ai/code/routines) (or the
`/schedule` CLI). Register **one routine per pillar**; this guide uses P1 as
the worked example.

## Prerequisites

| Item | Note |
|---|---|
| Claude Code Pro plan | Routines need cloud execution; the daily cap covers the scouting cadence |
| GitHub repo connected | The routine pushes to `main` in this repo |
| Network policy = Custom | The default **Trusted** policy blocks arXiv and S2 — see below |
| `SEMANTIC_SCHOLAR_API_KEY` | Optional, and currently **prefer keyless** — see below |

## Step 1 — Environment: network allowlist

A cloud environment defaults to **Trusted**, which allows only package
registries and GitHub; everything else gets `HTTP 403` with
`x-deny-reason: host_not_allowed`. Fix it environment-side:
routine → **Edit routine** → cloud icon → gear → **Update cloud environment** →
**Network access → Custom**, then list one host per line:

```
export.arxiv.org
arxiv.org
api.semanticscholar.org
```

Keep **"Also include default list of common package managers"** checked —
unchecking it breaks GitHub/registry access. Policy changes apply to **new
sessions only**; the next scheduled run picks them up.

**`SEMANTIC_SCHOLAR_API_KEY`** goes in the same dialog under **Environment
variables**, `.env` format, no quotes. S2 does not issue keys to free-domain
emails, and an unapproved key makes the API return 403 *while keyless works*.
Unless you hold a valid approved key, **run keyless** — the prompt omits the
header when the variable is empty, sleeps ~3 s between calls, and backs off on
HTTP 429. There is no secret store; environment variables are visible to anyone
who can edit the environment.

> **Two different 403s.** `x-deny-reason: host_not_allowed` → network layer,
> fix with the allowlist above. S2 403 *only when the key header is sent* →
> API auth, fix by dropping the key.

Verify from a fresh session (both should print `200`):

```bash
curl -sS -o /dev/null -w "%{http_code}\n" \
  "https://api.semanticscholar.org/graph/v1/author/search?query=Kevin+Black&fields=name"
curl -sS -o /dev/null -w "%{http_code}\n" \
  "http://export.arxiv.org/api/query?search_query=cat:cs.RO&max_results=1"
```

## Step 2 — Create the RemoteTrigger routine

| Form field | Value |
|---|---|
| Name | `probe-weekly-scout` |
| Prompt (Instructions) | The full body of `.claude/prompts/scouting.txt` with every `<PILLAR>` replaced by `P1`. Model → **Sonnet** |
| Repositories | This repo |
| Environment | The Step 1 environment |
| Trigger | A recurring cadence of your choosing (the form takes local time → UTC; min interval 1 h) |
| Connectors | None — retrieval is `curl`, not a connector |
| Permissions | Must allow pushing to `main`; the default `claude/`-branch-only push is not sufficient |

Also set the environment to allow **at most one active session**, so concurrent
runs do not race on the shared branch (the prompt keeps a
`git pull --rebase origin main` retry as an in-prompt backstop).

The prompt is self-contained: it names its own context files (`context/P1.md`,
the last 2 weeks of `scouting/`), the `curl` procedure, the output rules and the
guards. The form has no `context_files` field — the agent clones the repo and
reads what the prompt names. It is **pillar-scoped**: it reads the `context/P#.md`
skeleton §1–§6 only, never the full doc, which is why the P#-scoped prompt drops
the monthly Cross-pollination rule (its source is `context/MASTER.md` §7).

## Step 3 — First run & verification

There is no `--dry-run`; use **Run now** on the routine detail page. A green
run status only means "exited without an infra error" — open the transcript and
check the output with the same rigor as a manual run:

- Follows `scouting/templates/report.md` + `scouting/AUTHORING.md`.
- One Korean report landed at `scouting/P#/YYYY-MM-DD.md` (no language-suffixed
  twin — see CLAUDE.md "Document language convention").
- Every paper link resolves (no fabricated arXiv IDs).
- The `Papers scanned:` header discloses **no** `curl` 403 / network-block
  errors — if it does, the Custom allowlist is missing.
- Decision implications are concrete (a specific config key / hyperparameter /
  metric, not "tune DR wider").
- The Anti-topics filter actually fired (an empty "did not pass filter" section
  is suspicious).

If it is unsatisfactory, fix `.claude/prompts/scouting.txt` (or `context/P1.md`)
and re-run — do not leave automation on with a bad prompt.
