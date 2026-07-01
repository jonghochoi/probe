# catalogs/datasets.md

Hand-curated VLA dataset catalog — the P0 curation deliverable
(`context/P0.md` §1/§2: "Curation lands in `catalogs/datasets.md`").
Human-owned: the scouting/analysis routine *proposes* rows in its reports;
a human lands them here. Kept outside the `context/P0.md` §5 pin cap, so
this file is the full corpus while §5 holds only the anchors.

Axis legend (per `context/P0.md` §5): 🤖 robot action · 👤 human egocentric ·
🔀 mixed human→robot retarget. Tactile/force/torque coverage is a column,
not an axis — it cuts across all three (P0 D25). License bar per P0 D27:
prefer permissive (Apache-2.0 / CC-BY / MIT); gated corpora tracked but
flagged ⚠️; NC-only flagged for downstream-use risk.

## Datasets

| Dataset | arXiv / link | Year | Axis | Scale | Embodiment / DOF | Tactile · F/T | License | Lineage / notes |
|---|---|---|---|---|---|---|---|---|
| EgoDex (Apple) | [arXiv:2505.11709](https://arxiv.org/abs/2505.11709) | 2025 | 👤 ego | 829 h | human hands, 3D hand/finger tracking (Vision Pro) | — | check release terms | flagship for the in-house ego plan (D24) |
| Ego-Exo4D (Meta) | [arXiv:2311.18259](https://arxiv.org/abs/2311.18259) | 2023 | 👤 ego | 1,286 h | human, paired ego + multi-exo | — | gated ⚠️ (Ego4D terms) | multi-cam grounding (D24; P2 link) |
| UniHand-2.0 (BeingBeyond) | [arXiv:2601.12993](https://arxiv.org/abs/2601.12993) | 2026 | 🔀 mixed | ~35k h | 30 embodiments, human→multi-hand retarget | — | TBD | mixed-corpus reference (D24); Being-H0.5 pretraining corpus |
| AgiBot World | [arXiv:2503.06669](https://arxiv.org/abs/2503.06669) | 2025 | 🤖 robot | 1M+ traj | bimanual humanoid w/ dexterous hands | — | CC-BY-NC-SA ⚠️ NC | large robot-action anchor (D24) |
| DROID | [arXiv:2403.12945](https://arxiv.org/abs/2403.12945) | 2024 | 🤖 robot | 76k traj | Franka, in-the-wild | — | CC-BY | lineage core — DROID-pretrained VLAs (D24) |
| RH20T | [arXiv:2307.00595](https://arxiv.org/abs/2307.00595) | 2023 | 🤖 robot | 110k+ seq | single-arm, multi-skill | ✅ 6-axis wrist F/T + audio | CC-BY-NC ⚠️ NC | the rare tactile/torque corpus (D25) |

## Candidate inbox

Rows proposed by scouting reports but not yet vetted by the human curator.
Move a row up once modality/scale/license are verified against the release.

| Dataset | arXiv / link | Axis | Proposed by | Why |
|---|---|---|---|---|
| — | — | — | — | — |
