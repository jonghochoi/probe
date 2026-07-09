# Design — RoboDojo: A Unified Sim-and-Real Benchmark for Comprehensive Evaluation of Generalist Robot Manipulation Policies

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | RoboDojo: A Unified Sim-and-Real Benchmark for Comprehensive Evaluation of Generalist Robot Manipulation Policies |
| 링크 | [arXiv:2607.04434](https://arxiv.org/abs/2607.04434) |
| 분석 문서 | [`analysis/2607.04434/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 적용 | 🚫 비대상 (benchmark) |
| Design 생성일 | 2026-07-09 |

---

## 🚫 Design 비대상

본 논문은 foundry 로 포팅 가능한 새 model·architecture·학습목표·알고리즘을 제안하지 않는 **평가 벤치마크(benchmark)** 논문이므로 Layer 1 Design 을 생성하지 않습니다. 실제 산출물은 (1) 5개 능력 차원 42개 시뮬 task + 3 embodiment 18개 실세계 task, (2) Isaac Sim/Isaac Lab 기반 heterogeneous 병렬 시뮬레이션 플랫폼, (3) 표준화 물리 rig 원격 클라우드 평가 시스템(RoboDojo-RealEval), (4) 30개 이질적 정책을 공용 표준으로 감싸는 통합 인프라(XPolicyLab), (5) hidden-layout anti-gaming 리더보드로 이뤄진 **평가 인프라·데이터셋**이며, 학습 손실·옵티마이저·텐서 학습 계약이 존재하지 않습니다(`/implement-design` 으로 이식할 정책 알고리즘 없음 — 활용 방향은 오히려 역방향으로, `lerobot` 정책을 XPolicyLab 인터페이스에 통합해 RoboDojo 에서 평가하는 어댑터입니다). XPolicyLab 이 통합하는 30개 정책(π0.5·X-VLA·GR00T-N1.7·SmolVLA 등)은 벤치마크의 *평가 대상 baseline* 일 뿐 본 논문의 핵심 기여가 아니므로 매핑 대상에서 제외합니다. 따라서 이 논문의 가치는 분석 문서(`analysis.md`) 본문 — 능력별 실패 모드 진단, sim–real 순위 불일치, heterogeneous 병렬화 효율, 평가 지표·anti-gaming 방법론, 그리고 P0(D26/D27)·P3·P5 의사결정 함의 — 로 전달됩니다. `/implement-design` 호출 시 비대상 short-circuit 으로 `UNMAPPABLE.md` 가 산출됩니다.
