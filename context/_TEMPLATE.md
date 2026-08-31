# P<N> — <Pillar Name>

> **Owns**: the P<N> Decision Log, Anti-topics and Tracked
> Literature.
> **Does not own**: the thesis, the pillar overview, hardware, venue and
> cross-pollination — those are `context/MASTER.md`. A fact in both files is
> one of them going stale.
> **Agent usage**: *static* context, read-only. A scouting run reads this file
> alone and writes `scouting/P<N>/YYYY-MM-DD.md`; `/analyze` and `/compare`
> read it beside `context/MASTER.md`.
> **Output format**: owned by the track — `scouting/AUTHORING.md`,
> `analysis/AUTHORING.md`, `comparison/AUTHORING.md`. Never restated here.

---

## 1. Scope [STABLE structure, LIVING content] [AGENT-INPUT]

**Owns**: <the enumerable sub-axes this pillar tracks, **bold** on the axis
names. One dense paragraph — what a paper must be about to land here.>

**Thesis tie**: <one line back to the `context/MASTER.md` §1 claim — the
sentence that makes a paper P<N>-relevant rather than merely adjacent.>

**Tracked items**: <axis 1> (D<id>), <axis 2> (D<id>), … — one per Decision.

**Scouting lens**: <how wide recall runs around the north star — the comparison
group that gets surfaced and scored rather than rejected.>

**Anti-topics** (noise filter — excluded unless an unusually strong tie to
P<N> or a P<N> Decision):

- <exclusion 1>
- <exclusion 2>
- Survey / position papers (read manually, not via agent)

---

## 2. Decision Log — P<N> [LIVING] [AGENT-INPUT]

One `####` heading and one bullet per decision — the current choice, **bold**
on the chosen alternative, tracked and deferred alternatives named inline. Rationale lives outside this file. Entry format and
the `D#` allocation across pillars: `context/CLAUDE.md`.

#### [D<id>] <Decision title> (P<N>)
- <the current choice>
#### [D<id>] <Decision title> (P<N>)
- …

---

## 3. Tracked Literature [LIVING] [AGENT-INPUT]

Two tiers, and the split is the point: a paper this repo has already read has a
rewrite in `analysis/` that carries its link, its numbers and its verdict, so
the row here is a pointer. Only a paper with no rewrite yet needs its
bibliography carried in the context file.

### 3-1. Corpus — rewritten in `analysis/`

The anchors this pillar argues from. One line each, and nothing the rewrite
already says.

| Alias | Rewrite | Anchors |
|---|---|---|
| <alias> | `analysis/<arxiv-id>.md` | <the one thing this pillar takes from it> (D<id>) |

### 3-2. External pins — no rewrite yet

> Hard cap 6. Rebalance quarterly; replace, don't append. A pin is a
> **reference the decisions cite**, not a reading queue — it stays a pin for as
> long as it anchors its decision. A pin that earns a rewrite moves to 3-1 and
> frees its slot.
> **Format rule**: every entry carries
> `[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX)` (DOI/official URL if no
> preprint; `[no public link]` if neither). Never fabricate arXiv IDs.
> Canonical: `scouting/AUTHORING.md` §3.

| Paper | arXiv | Year | Role |
|---|---|---|---|
| <codename> | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) | YYYY | <why it anchors the pillar> (D<id>) |
