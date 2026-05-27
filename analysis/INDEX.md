# analysis/ Index

`scripts/refresh-analysis-index.py` 가 자동 관리하는 deep-dive
인덱스입니다 — `/analyze-paper`, `/foundry`, `/audit` 가 자기
산출물을 커밋할 때 같이 갱신합니다. 마커 사이는 매 호출마다 멱등
재생성되므로 손으로 편집하지 마십시오. `lerobot` 컬럼은
`<id>/impl/lerobot/impl.md` 존재 시 ✅, `UNMAPPABLE.md` 존재 시
🚧 UNMAPPABLE, 둘 다 없을 때 —. `🧬` 컬럼은 `lerobot` audit 메타
헤더의 🧬 실행 검증 verdict (`pass`/`fail`/`skipped`, audit
없거나 구버전이면 —) 입니다. `🔎 vr/pe/sd/se/ob` 컬럼은
`lerobot` audit 의 §🔎 §🚧 분류 마커에서 vendor-resolved /
paper-extractable / paper-silent-defaultable /
paper-silent-experimental / out-of-base-scope 행 수를 읽어 옵니다
(audit 없으면 —). `ob` 는 논문·Design 모두 완전 명세하지만
선택된 foundry base 좌표계 밖이라 본 매핑에서 제외된 모듈 수입니다.
규칙은 `docs/STYLE.md` §5-7 에 정리돼 있습니다.

폴더 구조·생성 커맨드·라이프사이클은 [`README.md`](README.md) 를
보세요.

<!-- ANALYSIS_INDEX:START -->

| # | Analysis | arXiv | Title | Refreshed | lerobot | 🧬 | 🔎 vr/pe/sd/se/ob |
|---|---|---|---|---|---|---|---|
| 1 | [`2605.24934/analysis.md`](2605.24934/analysis.md) | [`2605.24934`](https://arxiv.org/abs/2605.24934) | HumanEgo: Zero-Shot Robot Learning from Minutes of Human Egocentric Videos | 2026-05-27 | — | — | — |
| 2 | [`2605.22082/analysis.md`](2605.22082/analysis.md) | [`2605.22082`](https://arxiv.org/abs/2605.22082) | CoRMA: Contrastive RMA for Contact-Rich Meta-Adaptation | 2026-05-26 | — | — | — |
| 3 | [`2605.19282/analysis.md`](2605.19282/analysis.md) | [`2605.19282`](https://arxiv.org/abs/2605.19282) | Rethinking Muon Beyond Pretraining: Spectral Failures and High-Pass Remedies for VLA and RLVR | 2026-05-26 | — | — | — |
| 4 | [`2605.15735/analysis.md`](2605.15735/analysis.md) | [`2605.15735`](https://arxiv.org/abs/2605.15735) | UAM: A Dual-Stream Perspective on Forgetting in VLA Training | 2026-05-26 | — | — | — |
| 5 | [`2605.13403/analysis.md`](2605.13403/analysis.md) | [`2605.13403`](https://arxiv.org/abs/2605.13403) | RotVLA: Rotational Latent Action for Vision-Language-Action Model | 2026-05-26 | — | — | — |
| 6 | [`2605.11048/analysis.md`](2605.11048/analysis.md) | [`2605.11048`](https://arxiv.org/abs/2605.11048) | ForceFlow: Learning to Feel and Act via Contact-Driven Flow Matching | 2026-05-26 | — | — | — |
| 7 | [`2605.08879/analysis.md`](2605.08879/analysis.md) | [`2605.08879`](https://arxiv.org/abs/2605.08879) | Preserving Foundational Capabilities in Flow-Matching VLAs through Conservative SFT | 2026-05-26 | — | — | — |
| 8 | [`2605.07308/analysis.md`](2605.07308/analysis.md) | [`2605.07308`](https://arxiv.org/abs/2605.07308) | AT-VLA: Adaptive Tactile Injection for Enhanced Feedback Reaction in Vision-Language-Action Models | 2026-05-26 | — | — | — |
| 9 | [`2604.23272/analysis.md`](2604.23272/analysis.md) | [`2604.23272`](https://arxiv.org/abs/2604.23272) | Modular Sensory Stream for Integrating Physical Feedback in Vision-Language-Action Models | 2026-05-26 | — | — | — |
| 10 | [`2511.00139/analysis.md`](2511.00139/analysis.md) | [`2511.00139`](https://arxiv.org/abs/2511.00139) | End-to-End Dexterous Arm-Hand VLA Policies via Shared Autonomy: VR Teleoperation Augmented by Autonomous Hand VLA Policy for Efficient Data Collection | 2026-05-21 | ✅ | pass | 0/0/0/0/4 |

<!-- ANALYSIS_INDEX:END -->
