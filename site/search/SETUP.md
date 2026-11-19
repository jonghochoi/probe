# Search Function Setup

Redeploying the search endpoint after a merge. `function/search.ts` runs on
InsForge, outside this repo's deploy: a push to `main` rebuilds the site and
refreshes the index, but the function is uploaded by hand. The first-time
deploy and what each file does are in this folder's `README.md`.

| | Search function |
|---|---|
| **Where** | The InsForge dashboard of the project the site's `PROBE_SEARCH_API` points at |
| **Durable asset** | `site/search/function/search.ts` on `main` — the dashboard holds a copy, never the source |
| **CI does** | Parses the file on a PR (`check-search-function.yml`), re-embeds the changed chunks on a push to `main` (`deploy-site.yml`, step `Refresh the search index`) |
| **You do** | Upload the file, empty the query cache, verify — §4 to §6 |

## 1. When to redeploy

After every merge that changes `site/search/function/search.ts`. The one that
matters most is `PILLARS`, which changes whenever a pillar is added, renamed
or renumbered (`context/CLAUDE.md`, "When adding a new pillar").

Until the upload, the live function serves the version it last accepted, and
nothing on the page says so:

- **Pillar guesses go wrong.** With `PROBE_REWRITE_MODEL` set, a small model
  reads each query and may name the pillar it asks about from the `PILLARS`
  glosses; an inferred pillar narrows the search (`search.ts`,
  `want = … expansion.pillars`). The index already carries the new ids, so a
  guess made from the old glosses filters to the wrong axis. Unset, there is
  no guess and nothing narrows.
- **A pillar missing from the live `PILLARS` is dropped as a filter.** A
  reader who picks it gets a search narrowed only by the model's guess, or
  not at all.
- **Wrong answers outlive the upload.** `probe_query_cache` is emptied only
  by a write to `probe_chunks` (the trigger in `schema.sql`), and uploading
  the function writes nothing there — hence §5.

## 2. What you need

| Item | Where to find it |
|---|---|
| A login to the InsForge dashboard | The account that owns the project |
| `INSFORGE_URL` | The dashboard — the project's base URL, `https://<project>.insforge.app`. Only for §6's full check |
| `INSFORGE_API_KEY` | The dashboard — the project API key. GitHub stores it as a secret but never shows it again. Only for §6's full check |
| `PROBE_SEARCH_API` | GitHub → the repo's **Settings** → **Secrets and variables** → **Actions** → **Variables** tab. Only for §6's full check |

## 3. Order

1. **Merge** the change to `main`.
2. **Wait for the deploy.** Open the repo's **Actions** tab, the `Deploy site`
   run for the merge commit, and wait for a green check. Its step
   `Refresh the search index` is the one that matters: it rewrites every
   chunk whose paper changed and, by writing, empties the cache once.
3. **Upload** the function — §4.
4. **Empty the cache** — §5.
5. **Verify** — §6.

Step 3 may run before step 2 finishes: the index refresh empties the cache
anyway. Step 4 comes after both, because only then is no stale answer left
to be cached.

## 4. Upload the function

1. On GitHub, open `site/search/function/search.ts` on `main`, then **Raw**
   (or the copy-raw-file icon beside it). Copy the whole file — about 300
   lines; a partial paste is the usual failure.
2. In the InsForge dashboard, open the project, then its functions, then the
   one named `search`.
3. **Back up** the code it holds now — paste it into a scratch file. It is the
   rollback in §7.
4. Replace the whole code field with the copied file and save or deploy it.
   The dashboard runs a validator; a parse error is refused here, not on the
   page.

Keep two things as they are:

- **The name `search`.** `PROBE_SEARCH_API` and every built page call the
  function by that name.
- **The function's environment** — `OPENROUTER_API_KEY`,
  `INSFORGE_BASE_URL`, `ANON_KEY` and `PROBE_REWRITE_MODEL`. A redeploy
  changes code only. While the environment is on screen, note whether
  `PROBE_REWRITE_MODEL` is set: unset, §1's first failure could not have
  happened.

## 5. Empty the query cache

Open the dashboard's SQL editor and run:

```sql
DELETE FROM probe_query_cache;
```

The cache is derived — each row is an answer the function can compute again —
so emptying it loses nothing but one embedding on the next uncached query.
The index lives in `probe_chunks` and is not touched. §6's full check empties
the cache as one of its checks, so running it makes this step unnecessary.

## 6. Verify

**Quick check, in the browser.** Open the reading site, press ⌘K (Ctrl+K),
switch to the **의미** tab and ask a question about one pillar's subject — a
benchmark question for the datasets-and-benchmarks pillar, say. The hits
should carry that pillar. A hit's chips print only its first two pillars
(`FILED_PILLARS` in `site/builder/corpus.py`) while the filter reads every
pillar its rewrite declares, so a hit without the chip can still belong to it:
the rewrite's `pillars:` front matter settles it.

**Full check, in a terminal**, from a checkout of `main`:

```bash
export INSFORGE_URL=https://<project>.insforge.app
export INSFORGE_API_KEY=<project api key>
export PROBE_SEARCH_API=<the repository variable's value>
```

```bash
python3 site/build-site.py --index .search/index.jsonl
```

```bash
python3 site/search/verify.py .search/index.jsonl
```

Seven checks in dependency order; the script's docstring lists them. All seven
passing ends the redeploy.

## 7. Roll back

Paste the §4 backup into the `search` function, deploy it, and empty the
cache again (§5). The site keeps working throughout: on any endpoint failure
the palette falls back to its 글자 tab.
