# Design — DexJoCo: A Benchmark and Toolkit for Task-Oriented Dexterous Manipulation on MuJoCo

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | DexJoCo: A Benchmark and Toolkit for Task-Oriented Dexterous Manipulation on MuJoCo |
| 링크 | [arXiv:2605.16257](https://arxiv.org/abs/2605.16257) |
| 분석 문서 | [`analysis/2605.16257/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 적용 | 🚫 비대상 (benchmark) |
| Design 생성일 | 2026-06-25 |

---

## 🚫 Design 비대상

본 논문은 foundry 로 포팅 가능한 새 model·architecture·학습목표·알고리즘을 제안하지 않는 **벤치마크 + 데이터 수집 toolkit + 데이터셋** 논문이므로 Layer 1 Design 을 생성하지 않습니다. 핵심 산출물은 (1) MuJoCo 위에 구조화된 성공 조건으로 정의된 11개 task-oriented dexterous 태스크(tool-use·bimanual·long-horizon·reasoning), (2) Rokoko glove + HTC Vive tracker 기반 약 \$2,300 저비용 teleoperation 시스템과 GeoRT retargeting(자체 기여가 아닌 외부 모듈 채택), (3) 1.1K human demonstration 궤적과 LeRobot/DP Zarr 포맷 변환 인터페이스이며, 학습 손실·옵티마이저·텐서 학습 계약이 존재하지 않습니다(`/implement-design` 으로 이식할 정책 알고리즘 없음). 평가 대상이 된 ACT·Diffusion Policy·π0.5·GR00T N1.5 는 모두 기존 baseline 으로, 본 논문이 새로 제안한 모델이 아니라 매핑 대상에서 제외합니다. 따라서 이 논문의 가치는 `카탈로그` 라우팅(`benchmark/dexterous/DexJoCo` → `catalogs/benchmarks.md` ✋ Dexterous)으로 전달되며, 손 차별성 측정 축·실패 모드·prior-preservation 외부 증거(partial pretrain-AH > full reinit)·언어 일반화 검증 메트릭 등 의사결정 함의는 분석 문서(`analysis.md`) 본문이 담습니다. `/implement-design` 호출 시 비대상 short-circuit 으로 `UNMAPPABLE.md` 가 산출됩니다.
