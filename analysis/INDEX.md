# analysis/ Index

`scripts/refresh-analysis-index.py` 가 자동 관리하는 deep-dive
인덱스입니다 — `/analyze-paper`, `/implement`, `/validate` 가 자기
산출물을 커밋할 때 같이 갱신합니다. 마커 사이는 매 호출마다 멱등
재생성되므로 손으로 편집하지 마십시오. `lerobot` 컬럼은
`<id>/impl/lerobot/impl.md` 존재 시 ✅, `UNMAPPABLE.md` 존재 시
🚧 UNMAPPABLE, 둘 다 없을 때 —. `🧬` 컬럼은 `lerobot` validation 메타
헤더의 🧬 실행 검증 verdict (`pass`/`fail`/`skipped`, validation
없거나 구버전이면 —) 입니다. `🔎 vr/pe/sd/se/ob` 컬럼은
`lerobot` validation 의 §🔎 §🚧 분류 마커에서 vendor-resolved /
paper-extractable / paper-silent-defaultable /
paper-silent-experimental / out-of-base-scope 행 수를 읽어 옵니다
(validation 없으면 —). `ob` 는 논문·Design 모두 완전 명세하지만
선택된 foundry base 좌표계 밖이라 본 매핑에서 제외된 모듈 수입니다.
규칙은 `docs/STYLE.md` §5-7 에 정리돼 있습니다.

폴더 구조·생성 커맨드·라이프사이클은 [`README.md`](README.md) 를
보세요.

<!-- ANALYSIS_INDEX:START -->

| # | Analysis | arXiv | Title | Refreshed | lerobot | 🧬 | 🔎 vr/pe/sd/se/ob |
|---|---|---|---|---|---|---|---|
| 1 | [`2605.30280/analysis.md`](2605.30280/analysis.md) | [`2605.30280`](https://arxiv.org/abs/2605.30280) | Qwen-VLA: Unifying Vision-Language-Action Modeling across Tasks, Environments, and Robot Embodiments | 2026-05-29 | — | — | — |
| 2 | [`2605.28812/analysis.md`](2605.28812/analysis.md) | [`2605.28812`](https://arxiv.org/abs/2605.28812) | Beyond Binary: Sim-to-Real Dexterous Manipulation with Physics-Grounded Contact Representation | 2026-05-29 | — | — | — |
| 3 | [`2603.11653/analysis.md`](2603.11653/analysis.md) | [`2603.11653`](https://arxiv.org/abs/2603.11653) | Simple Recipe Works: Vision-Language-Action Models are Natural Continual Learners with Reinforcement Learning | 2026-05-28 | — | — | — |
| 4 | [`2509.22195/analysis.md`](2509.22195/analysis.md) | [`2509.22195`](https://arxiv.org/abs/2509.22195) | Actions as Language: Fine-Tuning VLMs into VLAs Without Catastrophic Forgetting | 2026-05-28 | — | — | — |
| 5 | [`2509.09372/analysis.md`](2509.09372/analysis.md) | [`2509.09372`](https://arxiv.org/abs/2509.09372) | VLA-Adapter: An Effective Paradigm for Tiny-Scale Vision-Language-Action Model | 2026-05-28 | — | — | — |
| 6 | [`2405.09673/analysis.md`](2405.09673/analysis.md) | [`2405.09673`](https://arxiv.org/abs/2405.09673) | LoRA Learns Less and Forgets Less | 2026-05-28 | — | — | — |
| 7 | [`2310.05905/analysis.md`](2310.05905/analysis.md) | [`2310.05905`](https://arxiv.org/abs/2310.05905) | TAIL: Task-specific Adapters for Imitation Learning with Large Pretrained Models | 2026-05-28 | — | — | — |
| 8 | [`2605.24934/analysis.md`](2605.24934/analysis.md) | [`2605.24934`](https://arxiv.org/abs/2605.24934) | HumanEgo: Zero-Shot Robot Learning from Minutes of Human Egocentric Videos | 2026-05-27 | — | — | — |
| 9 | [`2605.00078/analysis.md`](2605.00078/analysis.md) | [`2605.00078`](https://arxiv.org/abs/2605.00078) | Being-H0.7: A Latent World-Action Model from Egocentric Videos | 2026-05-27 | — | — | — |
| 10 | [`2601.12993/analysis.md`](2601.12993/analysis.md) | [`2601.12993`](https://arxiv.org/abs/2601.12993) | Being-H0.5: Scaling Human-Centric Robot Learning for Cross-Embodiment Generalization | 2026-05-27 | — | — | — |
| 11 | [`2605.22082/analysis.md`](2605.22082/analysis.md) | [`2605.22082`](https://arxiv.org/abs/2605.22082) | CoRMA: Contrastive RMA for Contact-Rich Meta-Adaptation | 2026-05-26 | — | — | — |
| 12 | [`2605.19282/analysis.md`](2605.19282/analysis.md) | [`2605.19282`](https://arxiv.org/abs/2605.19282) | Rethinking Muon Beyond Pretraining: Spectral Failures and High-Pass Remedies for VLA and RLVR | 2026-05-26 | — | — | — |
| 13 | [`2605.15735/analysis.md`](2605.15735/analysis.md) | [`2605.15735`](https://arxiv.org/abs/2605.15735) | UAM: A Dual-Stream Perspective on Forgetting in VLA Training | 2026-05-26 | — | — | — |
| 14 | [`2605.13403/analysis.md`](2605.13403/analysis.md) | [`2605.13403`](https://arxiv.org/abs/2605.13403) | RotVLA: Rotational Latent Action for Vision-Language-Action Model | 2026-05-26 | — | — | — |
| 15 | [`2605.11048/analysis.md`](2605.11048/analysis.md) | [`2605.11048`](https://arxiv.org/abs/2605.11048) | ForceFlow: Learning to Feel and Act via Contact-Driven Flow Matching | 2026-05-26 | — | — | — |
| 16 | [`2605.08879/analysis.md`](2605.08879/analysis.md) | [`2605.08879`](https://arxiv.org/abs/2605.08879) | Preserving Foundational Capabilities in Flow-Matching VLAs through Conservative SFT | 2026-05-26 | — | — | — |
| 17 | [`2605.07308/analysis.md`](2605.07308/analysis.md) | [`2605.07308`](https://arxiv.org/abs/2605.07308) | AT-VLA: Adaptive Tactile Injection for Enhanced Feedback Reaction in Vision-Language-Action Models | 2026-05-26 | — | — | — |
| 18 | [`2604.23272/analysis.md`](2604.23272/analysis.md) | [`2604.23272`](https://arxiv.org/abs/2604.23272) | Modular Sensory Stream for Integrating Physical Feedback in Vision-Language-Action Models | 2026-05-26 | — | — | — |
| 19 | [`2511.00139/analysis.md`](2511.00139/analysis.md) | [`2511.00139`](https://arxiv.org/abs/2511.00139) | End-to-End Dexterous Arm-Hand VLA Policies via Shared Autonomy: VR Teleoperation Augmented by Autonomous Hand VLA Policy for Efficient Data Collection | 2026-05-21 | ✅ | pass | 0/0/0/0/4 |

<!-- ANALYSIS_INDEX:END -->
