# Probe 펄스 힌트 — 2026-04-24 · Pillar P1 [EXAMPLE, not real data]

**Digest date:** 2026-04-24
**Pillar:** P1 — Dexterous Manipulation
**Source:** `pulse/inbox/2026-W17_slack-dexterous.json` (illustrative)
**Window:** 2026-04-17 → 2026-04-23
**Messages processed:** 142 (3 distinct speakers)
**Confidence:** medium

> 이번 주 팀은 single-skill 데모를 **in-hand rotation 한정**으로 좁히는 데
> 수렴했고, RMA extrinsics 가 friction 과 mass 를 정말로 분리해서 잡고
> 있는지를 계속 의심했다. bottle-cap opening 은 이번 분기 명시적으로
> 폐기했다. 다음 P1 스카우트는 RMA-ablation, friction identification 쪽으로
> bias 하고 bottle-cap 은 downweight 한다.

---

## 🎯 Focus Signals

### ✨ Converging on
- 이번 분기 single-skill 데모는 **in-hand rotation 만** — bottle-cap opening 은 보류 (3 speakers, 3일 이상 반박 없음).
- 가까운 실험은 RMA extrinsics probing — probing-classifier 셋업이 구체화 중 (2 speakers 합의).

### 🌀 Exploring / confused about
- 현재 extrinsics 에서 `friction` 과 `mass` 가 실제로 *분리* 되는지, 아니면 단일 "inertia-ish" 축으로 collapse 하는지. 미해결.
- DR 을 좁히는 것이 먼저인지 system-ID 가 먼저인지 — 두 speaker 가 양쪽을 주장.

### 🚫 Explicitly discarded
- Q2 2026 데모 task 로서의 bottle-cap opening.
- Rotation task 에 DrEureka 식 automatic reward synthesis (한 명이 실험, 다른 사람들이 hand-crafted 보다 못하다고 동의).

---

## ⚙️ Scouting Bias (다음 실행 1회 한정)

- **Boost authors:** Haozhi Qi, Ashish Kumar, Yichao Liang (RMA 계보 + extrinsics probing).
- **Boost keywords:** `RMA extrinsics probing`, `friction identification`, `mutual information extrinsics`, `in-hand rotation ablation`.
- **Downweight topics:** bottle-cap opening, DrEureka / automatic reward synthesis (hand-crafted 직접 비교 ablation 이 아닌 한).
- **Retrieval mode bias:** citation-graph (HORA, RMA2 주변 확장).

---

## 💡 Context Links

- **Touches Q#:** Q2 (single-skill mastery — 범위 축소), Q3 (RMA quantification — active probing).
- **Pressures H#:** H2 (supports — hand-crafted > auto reward 합의), H3 (challenges — subspace separability 의문).
- **Pinned literature referenced:** HORA, RMA2.
- **New names surfaced (not yet pinned):** "AnyRotate ablation" 논문 (2회 언급, arXiv ID 미상 — 스카우트 검증 필요).

---

## 🗂️ Provenance

- `[2026-04-18 14:22] A`: "let's just kill bottle-cap for this quarter. we keep cycling on it and it's not moving."
- `[2026-04-19 10:05] B`: "the probing classifier on mass vs friction should tell us whether the extrinsics are actually disentangled — I bet they aren't."
- `[2026-04-20 17:41] C`: "ran DrEureka on rotation. hand-crafted still wins by 8pp. not worth another week."
- `[2026-04-22 09:30] A`: "do we narrow DR first, then system-ID? or the other way? I keep flipping on this."

---

## ⚠️ Low-confidence flags

- 🌀 *Exploring / confused about* #2 (DR vs. system-ID 순서) 는 speaker A 가 입장을 뒤집고 있음 — bias 가 아니라 미해결로 취급.
- "AnyRotate ablation" 은 링크 없이 언급됨; 스카우트는 retrieval anchor 로 쓰기 전에 검증해야 함.
