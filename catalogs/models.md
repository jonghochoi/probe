# catalogs/models.md

Hand-curated VLM/VLA lineage catalog — the P4 D19 deliverable
(`context/P4.md` §3/§5: "lineage candidates in `catalogs/models.md`").
Human-owned: the scouting/analysis routine *proposes* rows; a human lands
them here. Kept outside the `context/P4.md` §5 pin cap.

A **lineage** = `(initial weights) × (further-pretrain corpus)`, not the
bare model name (P4 D19). Record both halves for every candidate so
lineage comparisons stay apples-to-apples.

## Lineage candidates

| Model / lineage | arXiv / link | Year | VLM init | Further-pretrain corpus | Open weights | Role |
|---|---|---|---|---|---|---|
| π0 (openpi) | [arXiv:2410.24164](https://arxiv.org/abs/2410.24164) | 2024 | PaliGemma-2B | OXE + π in-house mix | ✅ openpi | v1 lineage choice (D19/D21) |
| Xiaomi-Robotics-0 | [arXiv:2602.12684](https://arxiv.org/abs/2602.12684) | 2026 | Qwen3-VL-4B-Instruct | ~200M robot traj timesteps (DROID + MolmoAct + in-house) + 80M+ VL | ✅ | open-weight lineage candidate (D19) |
| Qwen-VLA | — (tracked, release pending verification) | — | Qwen-VL family | TBD | TBD | open-weight candidate named in P4 D19; fill from release |

## Candidate inbox

Rows proposed by scouting reports but not yet vetted by the human curator.

| Model / lineage | arXiv / link | VLM init | Proposed by | Why |
|---|---|---|---|---|
| — | — | — | — | — |
