# Design — DexVerse: A Modular Benchmark for Multi-Task, Multi-Embodiment Dexterous Manipulation

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | DexVerse: A Modular Benchmark for Multi-Task, Multi-Embodiment Dexterous Manipulation |
| 링크 | [arXiv:2607.08751](https://arxiv.org/abs/2607.08751) |
| 분석 문서 | [`analysis/2607.08751/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 적용 | 🚫 비대상 (benchmark) |
| Design 생성일 | 2026-08-02 |

---

## 🚫 Design 비대상

본 논문은 foundry 로 포팅 가능한 새 model·architecture·학습목표·알고리즘을 제안하지 않는 **벤치마크(benchmark)** 논문이므로 Layer 1 Design 을 생성하지 않습니다. 산출물은 Isaac Lab manager-based 인터페이스 위에 config 로 조립된 100개 태스크 환경, 3개 arm × 6개 dexterous hand 임베디먼트 설정, 9개 관측 그룹과 7개 관측 프리셋, VR 텔레오퍼레이션 수집 파이프라인, action-state 포맷의 3,180개 데모 데이터셋이며, 학습 손실·옵티마이저·텐서 학습 계약이라는 형태의 정책 알고리즘이 존재하지 않습니다. 평가에 쓰인 Diffusion Policy · DP3 · OpenVLA · $`\pi_{0.5}`$ 는 모두 기존 공개 방법을 그대로 학습·측정한 부수 베이스라인이므로 본 논문의 핵심 기여가 아니며 매핑 대상에서 제외합니다(Appendix B 의 하이퍼파라미터는 벤치마크 재현 설정이지 신규 제안이 아닙니다). 따라서 이 논문의 가치는 분석 문서(`analysis.md`) 본문 — 특히 §🔬 방법론의 관측 그룹·성공 술어 사양, §📊 실험 설정과 결과의 정밀 접촉 전면 붕괴 수치, §⚙️ 의사결정 함의의 `contact` 그룹 ablation 및 falsifier 후보 태스크 — 로 전달됩니다. `/implement-design` 호출 시 비대상 short-circuit 으로 `UNMAPPABLE.md` 가 산출됩니다.
