# site/search/

Semantic search for the reading site — the index, the endpoint, and what has to
be true for both to be safe.

The site's own filter (`builder/assets/filter.js`) matches strings, and strings
are the wrong tool for the question a reader actually arrives with: *"정책이
느려터진 거 해결한 논문"* shares no substring with anything in the corpus. This
folder answers that question instead, from a vector index of the rewrites, and
hands back a list of passages to open.

**It is an enhancement, never a dependency.** A build given no endpoint emits no
search script, makes no request, and behaves exactly as it does today. A build
given one still ships the lexical filter underneath, and the remote block
removes itself on any failure — offline, `file://`, a 502, an answer slower than
2.5 s.

## What is indexed

`analysis/<id>.md`, and nothing else — the same corpus the site publishes. A
chunk is one section, one term panel, one figure caption, or the paper as a
whole. Sections rather than documents, because a rewrite is 60 KB and "the paper
is somewhere in here" is the answer the reader already had.

A rewrite yields about 43 chunks, so the index tracks the corpus closely:

| Corpus | Chunks | Full re-index |
|---|---|---|
| 3 rewrites | ~130 | ~12 K tokens |
| 90 rewrites | ~3,900 | ~360 K tokens, cents |

A normal run embeds only what changed, so the second column is the cost of
rebuilding from nothing rather than the cost of a merge.

## Layout

| Path | Role |
|---|---|
| `chunks.py` | Cuts the rewrites into chunks. Pure — no network, no key. Anchors come from the same `DocRenderer` the page is built with, so a hit deep-links into markup that exists |
| `schema.sql` | The InsForge migration: `probe_chunks` (pgvector HNSW + a `simple` tsvector), `probe_query_cache`, and `probe_search` — a `SECURITY DEFINER` function fusing the two arms with Reciprocal Rank Fusion |
| `indexer.py` | Embeds and uploads. Stdlib only. Re-runs cost one embedding per changed chunk, because every chunk carries a `content_hash` |
| `function/search.ts` | The endpoint: read the query into search terms, embed, call `probe_search`, return the list. The model writes terms and nothing else — it does not summarise and does not rank |

## Running it

Chunking is offline and needs no project:

```bash
python3 site/build-site.py --index .search/index.jsonl
python3 site/search/indexer.py .search/index.jsonl --dry-run
```

Uploading needs one:

```bash
export INSFORGE_URL=https://<project>.insforge.app
export INSFORGE_API_KEY=<project api key>
python3 site/search/indexer.py .search/index.jsonl
```

Building the site against a deployed endpoint:

```bash
python3 site/build-site.py --search-api https://<project>.functions.insforge.app/search --serve
```

## Deploying

1. **Migrate** — run `schema.sql` against the project (dashboard SQL editor, or
   `POST /api/database/advance/rawsql/unrestricted`).
2. **Deploy the function** as `search`, with `OPENROUTER_API_KEY`,
   `INSFORGE_BASE_URL` and `ANON_KEY` in its environment, plus
   `PROBE_REWRITE_MODEL` if the query-reading step below is wanted. The
   OpenRouter key is the one InsForge provisions — the repo stores no provider
   credential.
3. **Index** — the two commands above, once by hand.
4. **Wire CI** — `deploy-site.yml` already carries the step. Add the repository
   secrets `INSFORGE_URL` and `INSFORGE_API_KEY`, and the repository *variable*
   `PROBE_SEARCH_API`. Until all three exist the step skips and the build emits
   no endpoint, which is the current state.

`--dry-run` prints the token estimate before anyone runs a full re-index in CI,
which is the number that matters as the corpus grows toward the legacy backlog.

## What keeps this safe

- **The table has no read policy.** `probe_search` is `SECURITY DEFINER`, so the
  endpoint can be asked questions and cannot be asked for the corpus. Every page
  it indexes is public already, but a table a browser can `select *` from is a
  corpus a scraper takes in one request.
- **The endpoint is public on purpose.** A key shipped inside a static site is
  not a secret, so the design does not pretend to have one. The ceiling is the
  query cache, a length cap, a per-isolate rate limit, and the project's own
  gateway quota — in that order of effectiveness.
- **No model writes prose.** M1 returns passages, ranked. A wrong list costs a
  reader one click; a wrong sentence costs the corpus its credibility.

## Reading the query

A reader types `플로우매칭`; the body says `flow matching`. The two share no
character, so no normalisation reaches across, and the embedding of a
transliteration lands nowhere near the term it transliterates. Naming the
standard term is what a small model is genuinely good at, so one runs in front
of the embedding and returns search terms — never an answer, never SQL.

```
"지연을 줄이는 정책"
   → terms   ["inference latency", "action chunking", "지연"]
   → embed   the query and the terms as one string, averaged into one vector
   → keyword "지연을 줄이는 정책 or inference latency or action chunking or 지연"
```

The two arms take the expansion differently on purpose. `websearch_to_tsquery`
ANDs the words inside a group, so appending terms there would demand every one
of them and return nothing; joining with its `or` keeps the reader's own words
AND'd among themselves and each expansion as an alternative.

The terms come back to the page and print above the results as `읽은 뜻`. A
search that silently rewrites itself cannot be trusted, and a reader who sees
what it understood can tell a good answer from a misread one.

Set `PROBE_REWRITE_MODEL` in the function's environment to an OpenRouter model
id to turn the step on — a small fast one, since it runs in front of every
uncached query and its budget is what the embedding and the search leave of the
page's 2.5 s. Unset, the step is skipped and the endpoint behaves exactly as it
does without it. So does any failure: a timeout, a non-200, or JSON the model
fenced or wrapped in a sentence all fall back to the raw query. Expansion
improves a search and is never what makes one possible.

A model reads reader-supplied text here, so what it can do with it is worth
stating: its output is used as strings to search with, capped at eight terms of
40 characters, stripped of quotes, and passed to a parameterised RPC. The worst
a crafted query buys is its own bad results.
