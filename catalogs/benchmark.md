![Updated](https://img.shields.io/badge/updated-2026--06--09-blue.svg)

## 🧪 Eval harness

| # | Benchmark | Links | Source | Details | Type | License | Use |
|---|---|---|---|---|---|---|---|
| 1 | **vla-eval** | [![arXiv](https://img.shields.io/badge/arXiv-2603.13966-b31b1b.svg)](https://arxiv.org/abs/2603.13966) | • Allen AI unified VLA evaluation harness | • Standardized cross-model evaluation protocol (same-condition comparison across models) | harness | Apache-2.0 | Common yardstick for methodology comparison |
| 2 | **RoboArena** | [![arXiv](https://img.shields.io/badge/arXiv-2506.18123-b31b1b.svg)](https://arxiv.org/abs/2506.18123) | • Distributed real-robot evaluation network | • Double-blind pairwise comparison<br>• Generalist-policy evaluation on the DROID platform | real-robot | MIT | In-the-wild generalization eval (D26 real axis) |

## 🎮 Simulator / sim benchmark

| # | Benchmark | Links | Source | Details | Type | License | Use |
|---|---|---|---|---|---|---|---|
| 1 | **ManiSkill 3** | [![arXiv](https://img.shields.io/badge/arXiv-2410.00425-b31b1b.svg)](https://arxiv.org/abs/2410.00425) [![Website](https://img.shields.io/badge/Website-Link-blue)](https://maniskill.readthedocs.io/) | • SAPIEN GPU simulation<br>• High-throughput | • 12 domains<br>• 30K+ FPS<br>• Allegro 16-DOF / ShadowHand 24-DOF (some dexterous) | sim | CC-BY-4.0 | Also cross-listed in `dataset.md` as a data source (dual role) |
| 2 | **RoboTwin 2.0** | [![arXiv](https://img.shields.io/badge/arXiv-2506.18088-b31b1b.svg)](https://arxiv.org/abs/2506.18088) | • Bimanual sim data generator + benchmark | • Strong domain randomization<br>• Expert-data synthesis<br>• Sim-to-real transfer | sim | MIT | Bimanual policy robustness eval |
| 3 | **LIBERO** | [![arXiv](https://img.shields.io/badge/arXiv-2306.03310-b31b1b.svg)](https://arxiv.org/abs/2306.03310) | • Lifelong manipulation benchmark | • Spatial / Object / Goal / Long (4 suites)<br>• LIBERO-90/100 (130 tasks total) | sim | MIT (code) / CC-BY-4.0 (data) | De facto standard for VLA eval (many LIBERO-Plus/X derivatives) |
| 4 | **SimplerEnv (SIMPLER)** | [![arXiv](https://img.shields.io/badge/arXiv-2405.05941-b31b1b.svg)](https://arxiv.org/abs/2405.05941) | • Sim eval reproducing real-robot setups | • Reproduces Google RT / BridgeData WidowX setups<br>• Validates sim-real correlation | sim | MIT | Sim-real correlation eval without real robots |

## ✋ Dexterous / contact-rich eval

| # | Benchmark | Links | Source | Details | Type | License | Use |
|---|---|---|---|---|---|---|---|
| 1 | **CATFA** | [![arXiv](https://img.shields.io/badge/arXiv-2509.23075-b31b1b.svg)](https://arxiv.org/abs/2509.23075) | • Tool-articulation / in-hand precision-manipulation eval set | • 5-tool precedent<br>• Tool grasping + finger manipulation eval | dexterous | ❓ no public license | Phase-2 identity-demo eval criterion (MASTER §3.5) |
