# site/search/

Semantic search for the reading site — the index, the endpoint, and what has to
be true for both to be safe.

The site's own filter (`builder/assets/filter.js`) matches strings, and strings
are the wrong tool for the question a reader actually arrives with: *"정책이
느려터진 거 해결한 논문"* shares no substring with anything in the corpus. This
folder answers that question instead, from a vector index of the rewrites, and
hands back a list of passages to open.

The two are named on the page for what they match: **의미** is this folder, and
**글자** is the filter — which compares substrings rather than words, so
`액션청` finds `액션청킹` and a name promising word boundaries would be a name
that lies.

**It is an enhancement, never a dependency.** A build given no endpoint emits no
search script, makes no request, and behaves exactly like a build without search. A build
given one still ships the lexical filter underneath, and the remote block
removes itself on any failure — offline, `file://`, a 502, an answer slower than
5 s.

## When it asks

The lexical filter narrows the list on every keystroke; this costs a round
trip, a model call and an embedding, so it asks only when the reader submits —
`Enter` or the 검색 button, which ships only with an endpoint — and a `#q=`
link asks on arrival. An answer splits the result area into `의미 검색` and
`글자 검색` tabs, landing on 의미. The page-side behaviour is
`builder/assets/semantic.js`, whose comments carry the reasons.

## What is indexed

`analysis/<id>.md`, and nothing else — the same corpus the site publishes. A
chunk is one section, one term panel, one figure caption, the 요약 surface, or
the paper as a whole. Sections rather than documents, because a rewrite is
60 KB and "the paper is somewhere in here" is the answer the reader already had.

Both surfaces, and a section carries the panels it holds. A term and a figure
are chunks of their own — a term is the 한/영 bridge a reader searches by name,
a caption is a different sentence about a different thing — and every other
panel stays inside the section it argues for, contributing the keys that carry
prose. What a panel keeps out is addressing and machinery: `tex` and `sym` are
LaTeX, `url` and `link` are targets, `tone` drives layout. A quiz gives up its
`why` alone, since its options are written to include wrong statements and a
result must not hand one back as the corpus speaking.

A rewrite yields about 44 chunks and about 22 K tokens to embed. The corpus
only grows, so the rate is what this states rather than a count of it — for
the figures as they stand, `build-site.py --index` reports chunks and
`indexer.py --dry-run` reports tokens:

| Corpus | Chunks | Full re-index |
|---|---|---|
| 50 rewrites | ~2,200 | ~1.1 M tokens · ~2¢ |
| 100 rewrites | ~4,400 | ~2.3 M tokens · ~5¢ |
| 200 rewrites | ~8,800 | ~4.5 M tokens · ~9¢ |

A normal run embeds only what changed, so the last column is the cost of
rebuilding from nothing rather than the cost of a merge.

## Layout

| Path | Role |
|---|---|
| `chunks.py` | Cuts the rewrites into chunks. Pure — no network, no key. Anchors come from the same `DocRenderer` the page is built with, so a hit deep-links into markup that exists |
| `schema.sql` | The InsForge migration: `probe_chunks` (pgvector HNSW + a `simple` tsvector), `probe_query_cache`, and the three `SECURITY DEFINER` functions that are the only way in — `probe_search`, fusing the two arms with Reciprocal Rank Fusion, and `probe_cache_get` / `probe_cache_put`. A statement trigger on `probe_chunks` empties the cache, so an answer never outlives the index it was computed from |
| `indexer.py` | Embeds and uploads. Stdlib only. Re-runs cost one embedding per changed chunk, because every chunk carries a `content_hash` |
| `function/search.ts` | The endpoint: read the query into search terms, embed, call `probe_search`, return the list. The model writes terms and nothing else — it does not summarise and does not rank |
| `verify.py` | Asks a connected project the seven questions nothing else can answer, in dependency order. Stdlib only, run by hand |

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
   OpenRouter key is the one InsForge provisions.
3. **Index** — the two commands above, once by hand.
4. **Wire CI** — `deploy-site.yml` already carries the step. Add the repository
   secrets `INSFORGE_URL` and `INSFORGE_API_KEY`, and the repository *variable*
   `PROBE_SEARCH_API`. `OPENROUTER_API_KEY` is an optional secret — unset, the
   indexer fetches the key from InsForge (`indexer.py`). Without them the step skips and the build emits no
   endpoint; with them, every push to `main` embeds only the chunks that
   changed and the build's `llms.txt` lists the endpoint for agents.
5. **Verify** — `python3 site/search/verify.py .search/index.jsonl`, with
   `INSFORGE_URL`, `INSFORGE_API_KEY` and `PROBE_SEARCH_API` set. Seven checks,
   each assuming the one before it: the migration answers, the table holds this
   build's chunks at their current versions, a Korean question comes back a list
   inside the 5 s the page waits, the same question twice is cached, a write
   to the index clears that cache, `플로우매칭` is read as `flow matching`, and
   the anon key reads neither table directly. Four of them fail invisibly —
   the fallback above is what a reader sees either way — so the page cannot
   tell you which. Not in CI: a gate needing a key and egress fails for reasons
   its pull request did not cause, and in the deploy job it would make
   publishing the site depend on a service the site does not need.

`--dry-run` prints the token estimate before anyone runs a full re-index in CI,
which is the number that matters as the corpus grows.

## What keeps this safe

- **Neither table has a policy.** Both are reached through `SECURITY DEFINER`
  functions, so the endpoint can be asked questions and cannot be asked for the
  corpus. Every page it indexes is public already, but a table a browser can
  `select *` from is a corpus a scraper takes in one request — and the endpoint
  carries the anon key a browser has, so what the key can reach directly is
  what a reader can reach directly. The cache is closed for the second half of
  that: a cache a browser can write is a cache that can be made to answer.
- **The endpoint is public on purpose.** A key shipped inside a static site is
  not a secret, so the design does not pretend to have one. The ceiling is the
  query cache, a length cap, a per-isolate rate limit, and the project's own
  gateway quota — in that order of effectiveness.
- **No model writes prose.** The endpoint returns passages, ranked. A wrong list costs a
  reader one click; a wrong sentence costs the corpus its credibility.

## Reading the query

A reader types `플로우매칭`; the body says `flow matching`. The two share no
character, so a small model runs in front of the embedding and returns search
terms — never an answer, never SQL. The terms are embedded with the query and
OR'd into the keyword arm, and print above the results as `읽은 뜻` so a reader
can see what the search understood.

Set `PROBE_REWRITE_MODEL` in the function's environment to an OpenRouter model
id to turn the step on — a small fast one, since it runs in front of every
uncached query. Unset, or on any failure, the raw query is searched as is. The
limits that keep reader-supplied text harmless (eight terms of 40 characters,
quotes stripped, a parameterised RPC) are in `function/search.ts`.
