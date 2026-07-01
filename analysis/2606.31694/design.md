# Design — RCT: A Robot-Collected Touch–Vision–Language Dataset for Tactile Generalization

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | RCT: A Robot-Collected Touch–Vision–Language Dataset for Tactile Generalization |
| 링크 | [arXiv:2606.31694](https://arxiv.org/abs/2606.31694) |
| 분석 문서 | [`analysis/2606.31694/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 적용 | 🚫 비대상 (dataset) |
| Design 생성일 | 2026-07-01 |

---

## 🚫 Design 비대상

본 논문은 foundry 로 포팅 가능한 새 model·architecture·학습목표·알고리즘을 제안하지 않는 **로봇 수집 touch–vision–language 데이터셋 + held-out 평가 프로토콜(dataset)** 논문이므로 Layer 1 Design 을 생성하지 않습니다. 주 산출물은 (1) contact sequence 단위로 보존된 RCT 데이터셋(`122` 재료·`7` 카테고리·`29,279` 프레임·3× DIGIT·per-frame force·재료 단위 vision/language 주석)과 (2) 재료·카테고리·센서·접촉 위치·시퀀스 다섯 축의 held-out 평가 프로토콜, 그리고 그것으로 폭로한 frame-random split 의 누출(contact-sequence overlap `−17.7 pp` + 재료 overlap `−42.0 pp`, TVL/HCT 공개 split 의 raw-pixel NN `98.3%` 복원) 진단 결론입니다 — `/implement-design` 으로 lerobot 정책 family 에 이식할 새 학습 손실·옵티마이저·텐서 학습 계약이 존재하지 않습니다. 학습에 쓰인 tactile–vision–language InfoNCE alignment 은 저자가 명시적으로 "We use this recipe unchanged and focus on evaluation" 라고 밝힌 TVL 레시피의 *무변경 차용*이므로 새 기여가 아니라 실험 수단이며 매핑 대상에서 제외합니다. 부수적으로 제안된 `uniform5` 프레임 샘플링 처방과 material-level multi-positive 채점 기준도 독립된 알고리즘 기여가 아니라 데이터셋 사용·평가 방식의 권고라 Layer 1 스펙으로 굳히지 않습니다. 따라서 이 논문의 가치는 분석 문서(`analysis.md`) 본문 — 특히 §📊 실험 설정과 결과(누출 계단·감사 수치), §⚙️ 의사결정 함의(contact-sequence 단위 split 강제·near-duplicate 누출 게이트·uniform5 sampler·held-out-sensor 의무화), §⚠️ 먼저 검증할 실패 모드 — 로 전달됩니다. `/implement-design` 호출 시 비대상 short-circuit 으로 `UNMAPPABLE.md` 가 산출됩니다.
