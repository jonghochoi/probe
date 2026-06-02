# `catalogs/` — 카탈로그 + pillar 방법론

per-paper deep-dive (`analysis/<arxiv-id>/`) 와 별도로 두는 cross-paper 자료. 각 파일이 담는 내용 요약:

| 파일 | 내용 |
|---|---|
| [`models.md`](models.md) | VLA 와 open-weight VLM 후보의 평면 큐레이션 (이름 + 논문 제목 + arXiv + GitHub/HF 배지) |
| [`dataset.md`](dataset.md) | VLA further-pretrain 데이터셋 큐레이션 — 유형별 3 섹션 (🤖 Robot action / 👤 Human video / 🔀 Mixed). entry 당 facts 한 줄 + 적층 VLA 한 줄 |
| [`vlm-prior-preservation.md`](vlm-prior-preservation.md) | P4 사전학습 보존 방법론 — forgetting × carve-out 직교 평면, θ_VLM 경로 개입 A~D, staged training recipe, forward KL 측정 프로토콜 |
| [`peft-robotics.md`](peft-robotics.md) | 로보틱스 PEFT 랜드마크 조사 + 평가 — VLA/IL/RL 에 LoRA·adapter 적용 사례 + 기초 PEFT 방법론 + LoRA 효용·한계 분석, deep-dive 우선순위 권고 |
| [`peft-genesis-strategy.md`](peft-genesis-strategy.md) | 프로젝트 전략 노트 — 단기 PEFT 실험 + 장기 Genesis식 full-stack |
| `assets/` | `vlm-prior-preservation.md` 가 인용하는 SVG 다이어그램 |
