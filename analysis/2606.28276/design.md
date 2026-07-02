# Design — SimFoundry: Modular and Automated Scene Generation for Policy Learning and Evaluation

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | SimFoundry: Modular and Automated Scene Generation for Policy Learning and Evaluation |
| 링크 | [arXiv:2606.28276](https://arxiv.org/abs/2606.28276) |
| 분석 문서 | [`analysis/2606.28276/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-07-02 |
| Design 적용 | 🚫 비대상 (tooling) |

---

## 🚫 Design 비대상

본 논문은 foundry 로 포팅 가능한 새 model·architecture·학습목표·알고리즘을 제안하지 않는 **non-policy tooling** 논문이므로 Layer 1 Design 을 생성하지 않습니다. 핵심 기여는 외부 foundation model 슬롯( $`V_{*}`$ — DepthAnything3, SAM3, Gemini-Pro-3, Hunyuan2.1, FoundationPose 등)을 조합한 real-to-sim 장면 생성 파이프라인과 object / scene / task cousins 증강, 그리고 Pearson·MMRV 기반 real-to-sim 평가 프로토콜이라는 시뮬레이션 인프라이며, 자체 학습 손실·옵티마이저·텐서 학습 계약이 존재하지 않습니다. 실험에 등장하는 정책들(π0 / π0.5 finetune, from-scratch 플로우 매칭)은 모두 기존 방법의 표준 적용으로, 데이터·평가 인프라의 효과를 보이기 위한 부수 베이스라인이라 매핑 대상에서 제외합니다 (`/implement-design` 으로 이식할 정책 알고리즘 없음 — 활용 방향은 오히려 평가 쪽으로, 트윈 장면에서의 체크포인트 사전 순위화·서브태스크 평가 프로토콜의 도입). 따라서 이 논문의 가치 — 상관 수치 기준선, cousins ablation, 평가 프로토콜, 파이프라인 구성 요소 목록 — 는 분석 문서(`analysis.md`)의 §📊 실험 설정과 결과 / §⚙️ 의사결정 함의 / §⚠️ 먼저 검증할 실패 모드가 담습니다. `/implement-design` 호출 시 비대상 short-circuit 으로 `UNMAPPABLE.md` 가 산출됩니다.
