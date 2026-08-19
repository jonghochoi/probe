-- The reading site's semantic index, as one InsForge migration.
--
-- Every row is a chunk `build-site.py --index` produced: a section of a rewrite,
-- a term panel, a figure caption, or the paper as a whole. The table is derived,
-- never authored — dropping it and re-running the indexer rebuilds it exactly.
--
-- Nothing outside `probe_search` may read it. Every page it indexes is public
-- already, but a table a browser can `select *` from is a corpus a scraper takes
-- in one request, and the rewrites are the work this repo exists to produce.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS probe_chunks (
  uid           TEXT PRIMARY KEY,        -- <arxiv id>:<n>
  kind          TEXT NOT NULL,           -- paper | section | term | figure
  paper_id      TEXT NOT NULL,
  title         TEXT NOT NULL,
  context       TEXT NOT NULL DEFAULT '',
  path          TEXT NOT NULL,           -- p/<id>/ — the page the hit lands on
  anchor        TEXT NOT NULL DEFAULT '',
  pillars       TEXT[] NOT NULL DEFAULT '{}',
  tags          TEXT[] NOT NULL DEFAULT '{}',
  chunk_date    DATE,
  body          TEXT NOT NULL,
  content_hash  TEXT NOT NULL,           -- what decides a re-embed
  embedding     VECTOR(1536) NOT NULL,
  -- The keyword arm. `simple` rather than a language config on purpose: the
  -- corpus is Korean prose carrying English identifiers, and no stemmer covers
  -- both. What this arm is for is the exact token an embedding smears —
  -- `2607.26055`, `AdaLN`, `GR00T`, `25 Hz` — and `simple` keeps those whole.
  body_tsv      TSVECTOR GENERATED ALWAYS AS
                  (to_tsvector('simple', title || ' ' || body)) STORED,
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_probe_chunks_embedding
  ON probe_chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_probe_chunks_tsv
  ON probe_chunks USING gin (body_tsv);
CREATE INDEX IF NOT EXISTS idx_probe_chunks_paper ON probe_chunks (paper_id);

ALTER TABLE probe_chunks ENABLE ROW LEVEL SECURITY;   -- no policy: no direct reads

-- One normalised query → one answer. A reading site's queries repeat heavily
-- (the same paper, the same term, the same week), and a hit here costs no
-- embedding call and no model call at all.
CREATE TABLE IF NOT EXISTS probe_query_cache (
  q_norm      TEXT PRIMARY KEY,
  result      JSONB NOT NULL,
  hits        INT NOT NULL DEFAULT 1,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
ALTER TABLE probe_query_cache ENABLE ROW LEVEL SECURITY;

-- ── Search ──────────────────────────────────────────────────────────────────
-- Two arms, fused by Reciprocal Rank Fusion. RRF is used rather than a weighted
-- sum of scores because the two arms are not on one scale: cosine distance and
-- `ts_rank_cd` cannot be added without inventing a conversion, while their
-- ranks can. A chunk both arms like therefore beats one that either arm loves,
-- which is the behaviour the corpus needs — the embedding finds "느려터진 정책"
-- and the keyword arm is what stops `2607.26055` from ranking by vibe.
--
-- SECURITY DEFINER is what makes an anonymous call safe: the caller reaches the
-- table through this function's projection and nothing else.
CREATE OR REPLACE FUNCTION probe_search(
  query_embedding VECTOR(1536),
  query_text      TEXT    DEFAULT '',
  match_count     INT     DEFAULT 12,
  want_pillars    TEXT[]  DEFAULT '{}'
)
RETURNS TABLE (
  uid TEXT, kind TEXT, paper_id TEXT, title TEXT, context TEXT,
  path TEXT, anchor TEXT, pillars TEXT[], chunk_date DATE, body TEXT,
  similarity FLOAT, score FLOAT
)
LANGUAGE sql STABLE SECURITY DEFINER
SET search_path = public
AS $$
  WITH pool AS (
    SELECT * FROM probe_chunks c
    WHERE cardinality(want_pillars) = 0 OR c.pillars && want_pillars
  ),
  -- The candidate depth each arm contributes. Wider than `match_count` on
  -- purpose: fusion can only reorder what it was given, so an arm that stops
  -- at the answer count can never rescue what the other arm ranked poorly.
  semantic AS (
    SELECT uid, ROW_NUMBER() OVER (ORDER BY embedding <=> query_embedding) AS rank,
           1 - (embedding <=> query_embedding) AS sim
    FROM pool ORDER BY embedding <=> query_embedding LIMIT 60
  ),
  keyword AS (
    SELECT p.uid, ROW_NUMBER() OVER (ORDER BY ts_rank_cd(p.body_tsv, q) DESC) AS rank
    FROM pool p, websearch_to_tsquery('simple', query_text) q
    WHERE query_text <> '' AND p.body_tsv @@ q
    ORDER BY ts_rank_cd(p.body_tsv, q) DESC LIMIT 60
  ),
  fused AS (
    SELECT COALESCE(s.uid, k.uid) AS uid,
           COALESCE(s.sim, 0) AS sim,
           COALESCE(1.0 / (60 + s.rank), 0) + COALESCE(1.0 / (60 + k.rank), 0) AS score
    FROM semantic s FULL OUTER JOIN keyword k ON s.uid = k.uid
  )
  SELECT c.uid, c.kind, c.paper_id, c.title, c.context, c.path,
         c.anchor, c.pillars, c.chunk_date, c.body, f.sim, f.score
  FROM fused f JOIN probe_chunks c ON c.uid = f.uid
  ORDER BY f.score DESC, f.sim DESC
  LIMIT match_count;
$$;

REVOKE ALL ON FUNCTION probe_search FROM PUBLIC;
GRANT EXECUTE ON FUNCTION probe_search TO anon, authenticated;
