# Research Context — P<N>: <Pillar Name>

> **P<N> working context — Pillar <N> (<Pillar Name>).**
> Owns the P<N> Decision Log, Tracked Literature, Anti-topics, and Curated
> Lists. P<N> owns **D<a>–D<b>**; cross-cutting
> context (Identity, Pillars overview, Venue, Cross-pollination) lives in
> `context/MASTER.md`.
> **Agent usage**: *static* context. The retrieval agent reads (never writes)
> this file. Findings go to `scouting/P<N>/YYYY-MM-DD.md` (one per run).
> **Formatting & authoring rules**: `scouting/AUTHORING.md` (single source of
> truth — agent must read it before producing output).

---

## 1. Identity [STABLE] [AGENT-INPUT]

> <One paragraph: what question this pillar owns, why it exists, and the
> hand-centric bet that narrows its target. Written by the human owner.>

**Decomposition (P<N>-relevant)**
- *Antagonist*: <what looks adjacent but is explicitly NOT this pillar>
- *Protagonist (P<N> owns)*: <the positive scope, one dense line>
- *Coupling*: <which other pillars it shares a backbone / corpus / representation with>

> **Note**: P<N> owns the <half> half. <List the sibling pillars and their
> one-word scopes> are out of scope here — see `context/MASTER.md`.

---

## 2. Pillar P<N> — <Pillar Name> [STABLE structure, LIVING content] [AGENT-INPUT]

**Scope**: <the enumerable sub-axes this pillar tracks, **bold** on the axis names>.

**Identity tie**: <one line connecting the scope back to §1's bet>.

**Tracked items**: <axis 1> (D<a>), <axis 2> (D<a+1>), … — one per Decision.

**Anti-topics**: <one-line noise summary; the full filter is §4>.

**Literature anchor**: <the pinned papers by codename, one clause each>. See §5.

---

## 3. Decision Log — P<N> / <Pillar Name> (D<a>–D<b>) [LIVING] [AGENT-INPUT]

v1 choice per decision (first-attempt default; rationale and deferred candidates
held outside the context file). P<N> covers **D<a>–D<b>**; <list the other
pillars' ranges> are out of scope here — see `context/MASTER.md`.

#### [D<a>] <Decision title> (P<N>)
- **v1**: <the current first-attempt choice, **bold** on the chosen alternative;
  tracked/deferred alternatives named inline>
#### [D<a+1>] <Decision title> (P<N>)
- **v1**: …

---

## 4. P<N> Anti-topics (Noise Filter) [AGENT-INPUT]

Excluded from the digest unless an unusually strong tie to P<N> or a P<N> Decision (D<a>–D<b>):

- <exclusion 1>
- <exclusion 2>
- Survey / position papers (read manually, not via agent)

---

## 5. P<N> Tracked Literature [LIVING] [AGENT-INPUT]

> Hard cap 8 pinned. Rebalance quarterly; replace, don't append.
> **Format rule**: every entry carries `[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX)` (DOI/official URL if no preprint; `[no public link]` if neither). Never fabricate arXiv IDs. Canonical: `scouting/AUTHORING.md` §3.

### P<N> Pinned — <Pillar Name>
| Paper | arXiv | Year | Role |
|---|---|---|---|
| <codename> | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) | YYYY | *Top*: <why it anchors the pillar> (D<a>) |
| … | | | |

**Methodology base (non-pinned)**
| Paper | arXiv | Relevance |
|---|---|---|
| <codename> | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) | <one clause> (D<a>) |

---

## 6. P<N> Curated External Lists to Monitor [AGENT-INPUT]

> Human-curated GitHub lists, read in the scout's Curated-List Sweep. Topic
> whitelist only — this pillar's relevance score + §4 P<N> Anti-topics decide what
> survives. Recency narrowing (do NOT ingest the whole lists): keep only arXiv
> ids whose month-prefix `YYMM` is the current or previous month, then confirm
> the last-14-day window via `publicationDate`.

| List | raw README (HEAD = default branch) |
|---|---|
| <list name> | `https://raw.githubusercontent.com/<owner>/<repo>/HEAD/README.md` |

---

*P<N> working context. For the other pillars, their decision ranges, and the
cross-pillar anchor (Identity, Pillars overview, Venue, Cross-pollination),
consult `context/MASTER.md` and the other `context/P#.md`.*
