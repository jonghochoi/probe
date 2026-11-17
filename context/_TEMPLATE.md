# P<N> — <Pillar Name>

> **Owns** the P<N> Open Questions, Anti-topics and Tracked
> Literature. The thesis, the pillar overview, venue and
> cross-pollination are `context/MASTER.md`'s — a fact in both files is one of
> them going stale.
> **Static context, read-only.** A scouting run reads this file, and of
> `context/MASTER.md` §5 and §6 alone, and writes
> `scouting/P<N>/YYYY-MM-DD.md`; the on-demand commands (`/analyze`,
> `/compare`, `/ideate`, `/distinguish`, `/adapt`) read it beside
> `context/MASTER.md`. Output format is the track's own contract
> (`scouting/AUTHORING.md`, `analysis/AUTHORING.md`,
> `comparison/AUTHORING.md`), never restated here.

---

## 1. Scope [STABLE structure, LIVING content] [AGENT-INPUT]

**Owns**: <the questions this pillar asks, **bold** on the axis names. One
dense paragraph — what a paper must be about to land here, stated as what is
asked, not as an answer.>

**Thesis tie** — why this axis is asked: <what is open on this axis, in a
line or two back to `context/MASTER.md` §1 — the sentence that makes a paper
P<N>-relevant rather than merely adjacent. A tension the questions keep open,
never a bet on how it resolves.>

**Questions**: <short form> (D<id>), <short form> (D<id>), … — one per question.

**Premises** — <the setting the questions are asked in, stated as fact; leave
this paragraph out when the pillar has none>.

**Scouting lens** — three tiers, and a paper is placed on this ladder before
it is scored:

1. **<the north star>** — <what a paper must show to rank first>.
2. **<the evidence pool>** — <what transfers to this pillar's questions>.
3. **<the outermost ring>** — <what is still surfaced, often as the
   comparison group>.

Recall runs wide across all three; the ranking anchor stays tier 1.

**Anti-topics** (noise filter — excluded unless an unusually strong tie to
P<N> or a P<N> question):

- <exclusion 1>
- <exclusion 2>
- Survey / position papers (read manually, not via agent)

---

## 2. Open Questions — P<N> [LIVING] [AGENT-INPUT]

The questions this pillar keeps open. Each names what it turns on and the
threads the corpus has followed so far; none is waiting to be closed, and a
thread is added when a paper opens one.

#### [D<id>] <the question, in Korean> (P<N>)
- <what the question turns on>. Threads: <thread>; <thread>; ….
#### [D<id>] <the question, in Korean> (P<N>)
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
> **reference the questions cite**, not a reading queue — it stays a pin for as
> long as it anchors its question. A pin that earns a rewrite moves to 3-1 and
> frees its slot.
> **Format rule**: every entry carries
> `[arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX)` (DOI/official URL if no
> preprint; `[no public link]` if neither). Never fabricate arXiv IDs.
> Canonical: `scouting/AUTHORING.md` §3.

| Paper | arXiv | Year | Role |
|---|---|---|---|
| <codename> | [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) | YYYY | **tier <n>** — <what it is and what it anchors> (D<id>) |
