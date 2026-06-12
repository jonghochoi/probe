# Design — vla-eval: A Unified Evaluation Harness for Vision-Language-Action Models

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | vla-eval: A Unified Evaluation Harness for Vision-Language-Action Models |
| 링크 | [arXiv:2603.13966](https://arxiv.org/abs/2603.13966) |
| 분석 문서 | [`analysis/2603.13966/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 적용 | 🚫 비대상 (benchmark) |
| Design 생성일 | 2026-06-04 |

---

## 🚫 Design 비대상

본 논문은 foundry 로 포팅 가능한 새 model·architecture·학습목표·알고리즘을 제안하지 않는 **평가 하니스(benchmark/eval-harness)** 논문이므로 Layer 1 Design 을 생성하지 않습니다. 산출물은 WebSocket+msgpack 통신 프로토콜과 Docker 격리, 에피소드 샤딩 병렬화로 이뤄진 평가 인프라이며, 학습 손실·옵티마이저·텐서 학습 계약이 존재하지 않습니다(`/implement-design` 으로 이식할 정책 알고리즘 없음 — 활용 방향은 오히려 역방향으로, `lerobot` 정책을 vla-eval 모델 서버로 노출하는 어댑터). 따라서 이 논문의 가치는 `카탈로그` 라우팅(`benchmark/harness/vla-eval` → `catalogs/benchmarks.md` 🧪 Eval Harness)으로 전달되며, 평가 함정·재현 디테일·리더보드 등 의사결정 함의는 분석 문서(`analysis.md`) 본문이 담습니다. `/implement-design` 호출 시 비대상 short-circuit 으로 `UNMAPPABLE.md` 가 산출됩니다.
