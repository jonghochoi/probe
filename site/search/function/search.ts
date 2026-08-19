/* The reading site's search endpoint — one InsForge edge function.
 *
 * POST { q, pillars?, limit? } → { hits: [...], expanded, cached, tookMs }
 *
 * It reads the query, embeds it, calls `probe_search` (schema.sql) and returns
 * what came back. It does not summarise, rank with a model, or answer in prose:
 * a wrong list costs a reader one click, and a wrong sentence costs the corpus
 * its credibility. The list is the whole contract.
 *
 * "Reads" is the one place a model writes anything, and it writes search terms.
 * A reader types `플로우매칭` while the body says `flow matching`; the two share
 * no character, so no normalisation reaches across and the embedding of a
 * transliteration lands nowhere near the term it transliterates. Naming the
 * standard term is what a model is genuinely good at, and the output is used
 * only as strings to search with — never as an answer, never as SQL.
 *
 * Public and unauthenticated, because the pages it searches are public and a
 * key shipped inside a static site is not a secret. What keeps that safe is
 * the shape of the surface: `probe_search` is SECURITY DEFINER over a table
 * with no read policy, so this endpoint can be asked questions and cannot be
 * asked for the corpus.
 */

const MODEL = Deno.env.get("PROBE_EMBED_MODEL") ?? "openai/text-embedding-3-small";
const DIMS = 1536;
const Q_MAX = 200;          // a query, not a document — the embedding is per call
const LIMIT_MAX = 24;

/* The query-expansion model, as an OpenRouter id. No default: unset, the step
 * is skipped and the endpoint behaves exactly as it does without it. Pick a
 * small fast one — this runs in front of every uncached query and its budget is
 * the slice of `TIMEOUT` in `semantic.js` that the embedding and the search do
 * not need. */
const REWRITE_MODEL = Deno.env.get("PROBE_REWRITE_MODEL") ?? "";
const REWRITE_MS = 1_200;
const TERMS_MAX = 8;
const TERM_LEN = 40;

const EXPAND_PROMPT = `You turn a reader's question about robot-manipulation
research papers into search terms. The corpus is Korean prose that keeps
technical terms in English.

Return JSON only: {"terms": string[], "pillars": string[]}

terms — up to ${TERMS_MAX} short search terms, most important first:
  · if the query is a Korean transliteration or translation of a standard
    English term, give that English term ("플로우매칭" → "flow matching")
  · if the query is colloquial, name what it is about in both languages
    ("느려터진 정책" → "inference latency", "지연", "action chunking")
  · keep any exact token the reader typed — an arXiv id, a number with a unit,
    a model name — unchanged
  · no explanations, no sentences, no duplicates of the query itself
pillars — any of P0..P5 the query clearly asks for, else []:
  P0 datasets and benchmarks · P1 body/hand action experts · P2 multimodal
  observation fusion · P3 hand-level low-level control · P4 pretraining and
  data-efficient adaptation · P5 world models`;

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

/* Per-isolate, so it bounds one warm instance rather than the endpoint. It is
 * the cheap half of the ceiling: the query cache below is what actually keeps a
 * repeated question free, and the project's own gateway quota is the hard stop. */
const RATE = { windowMs: 60_000, max: 30 };
let windowStart = 0;
let inWindow = 0;

function overRate(now: number): boolean {
  if (now - windowStart > RATE.windowMs) {
    windowStart = now;
    inWindow = 0;
  }
  return ++inWindow > RATE.max;
}

/* The cache key. Case, spacing and trailing punctuation are not the question —
 * "액션 청킹?" and "액션청킹" deserve one embedding between them. */
function normalise(q: string): string {
  return q.toLowerCase().normalize("NFC").replace(/\s+/g, " ").trim()
    .replace(/[?!.,·]+$/, "");
}

/* What the two arms are given.
 *
 * The embedding arm reads one string, so the expansions are appended to the
 * query and averaged into one vector with it. The keyword arm is `websearch_to_
 * tsquery`, which ANDs the words inside one group — appending expansions there
 * would demand every one of them and return nothing, so they are joined with
 * its `or`, leaving the reader's own words AND'd among themselves. Quotes are
 * dropped because a half-open phrase changes what the rest of the query means.
 */
export function searchText(q: string, terms: string[]): { embed: string; keyword: string } {
  const clean = terms
    .map((t) => String(t ?? "").replace(/["']/g, " ").trim().slice(0, TERM_LEN))
    .filter((t) => t && t.toLowerCase() !== q.toLowerCase())
    .slice(0, TERMS_MAX);
  return {
    embed: clean.length ? `${q}\n${clean.join(", ")}` : q,
    keyword: clean.length ? [q, ...clean].join(" or ") : q,
  };
}

export function parseExpansion(raw: string): { terms: string[]; pillars: string[] } {
  // Models fence JSON as often as not, and one stray fence should cost the
  // query its expansion rather than its answer.
  const body = raw.replace(/^[\s\S]*?\{/, "{").replace(/\}[^}]*$/, "}");
  try {
    const got = JSON.parse(body);
    return {
      terms: Array.isArray(got.terms) ? got.terms.map(String) : [],
      pillars: (Array.isArray(got.pillars) ? got.pillars.map(String) : [])
        .filter((p: string) => /^P[0-5]$/.test(p)),
    };
  } catch {
    return { terms: [], pillars: [] };
  }
}

async function expand(q: string): Promise<{ terms: string[]; pillars: string[] }> {
  if (!REWRITE_MODEL) return { terms: [], pillars: [] };
  const ctl = new AbortController();
  const bail = setTimeout(() => ctl.abort(), REWRITE_MS);
  try {
    const res = await fetch("https://openrouter.ai/api/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${Deno.env.get("OPENROUTER_API_KEY")}`,
        "Content-Type": "application/json",
      },
      signal: ctl.signal,
      body: JSON.stringify({
        model: REWRITE_MODEL,
        temperature: 0,
        max_tokens: 200,
        response_format: { type: "json_object" },
        messages: [
          { role: "system", content: EXPAND_PROMPT },
          { role: "user", content: q },
        ],
      }),
    });
    if (!res.ok) return { terms: [], pillars: [] };
    const got = await res.json();
    return parseExpansion(got.choices?.[0]?.message?.content ?? "");
  } catch {
    // Slow, down, or malformed — the raw query is still a query. Expansion
    // improves a search and is never what makes one possible.
    return { terms: [], pillars: [] };
  } finally {
    clearTimeout(bail);
  }
}

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...CORS, "Content-Type": "application/json" },
  });
}

export default async function (req: Request): Promise<Response> {
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });
  if (req.method !== "POST") return json({ error: "POST only" }, 405);

  const started = Date.now();
  if (overRate(started)) return json({ error: "rate limited" }, 429);

  let payload: Record<string, unknown>;
  try {
    payload = await req.json();
  } catch {
    return json({ error: "body must be JSON" }, 400);
  }

  const q = String(payload.q ?? "").slice(0, Q_MAX).trim();
  if (!q) return json({ error: "q is required" }, 400);

  const limit = Math.min(Number(payload.limit) || 12, LIMIT_MAX);
  const pillars = Array.isArray(payload.pillars)
    ? (payload.pillars as string[]).filter((p) => /^P[0-5]$/.test(p))
    : [];

  const { createClient } = await import("npm:@insforge/sdk");
  const db = createClient({
    baseUrl: Deno.env.get("INSFORGE_BASE_URL"),
    anonKey: Deno.env.get("ANON_KEY"),
  }).database;

  // Only the plain question is cached. A query narrowed by pillar is a
  // different answer to the same words, and caching it under the words would
  // hand the next reader someone else's filter.
  const plain = pillars.length === 0;
  const key = `${normalise(q)}|${limit}`;
  if (plain) {
    const { data } = await db.from("probe_query_cache").select("result").eq("q_norm", key).limit(1);
    if (data?.[0]?.result) {
      return json({ ...data[0].result, cached: true, tookMs: Date.now() - started });
    }
  }

  const expansion = await expand(q);
  const text = searchText(q, expansion.terms);
  // A pillar the reader picked is a filter they set; one the model inferred is
  // a guess, and a guess may narrow a search only when nothing else does.
  const want = pillars.length ? pillars : expansion.pillars;

  const res = await fetch("https://openrouter.ai/api/v1/embeddings", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${Deno.env.get("OPENROUTER_API_KEY")}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ model: MODEL, input: text.embed, dimensions: DIMS }),
  });
  if (!res.ok) {
    // The site falls back to its own lexical filter on any non-200, so saying
    // so plainly is more useful than dressing the failure up as an empty result.
    return json({ error: "embedding unavailable" }, 502);
  }
  const embedding = (await res.json()).data[0].embedding;

  const { data, error } = await db.rpc("probe_search", {
    query_embedding: embedding,
    query_text: text.keyword,
    match_count: limit,
    want_pillars: want,
  });
  if (error) return json({ error: "search unavailable" }, 502);

  const hits = (data ?? []).map((r: Record<string, unknown>) => ({
    uid: r.uid, kind: r.kind, paperId: r.paper_id,
    title: r.title, context: r.context, path: r.path, anchor: r.anchor,
    pillars: r.pillars, date: r.chunk_date,
    // Enough to recognise the passage, not enough to replace opening it.
    snippet: String(r.body ?? "").slice(0, 240),
    similarity: r.similarity, score: r.score,
  }));

  // `expanded` goes back so the page can print what the query was read as. A
  // reader who sees "느려터진 → inference latency" can tell a good answer from a
  // misread one, and a search that silently rewrites itself cannot be trusted.
  const result = { q, hits, expanded: expansion.terms, pillars: want };
  if (plain) {
    await db.from("probe_query_cache").insert({ q_norm: key, result });
  }
  return json({ ...result, cached: false, tookMs: Date.now() - started });
}
