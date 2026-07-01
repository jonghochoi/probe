# Design — HRDexDB: A Paired Human-Robot Dataset for Cross-Embodiment Dexterous Grasping

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | HRDexDB: A Paired Human-Robot Dataset for Cross-Embodiment Dexterous Grasping |
| 링크 | [arXiv:2604.14944](https://arxiv.org/abs/2604.14944) |
| 분석 문서 | [`analysis/2604.14944/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 적용 | 🚫 비대상 (dataset) |
| Design 생성일 | 2026-07-01 |

---

## 🚫 Design 비대상

본 논문의 핵심 기여는 foundry 로 포팅 가능한 새 model/architecture/학습목표/알고리즘이 아니라 **paired cross-embodiment dexterous grasping 데이터셋(HRDexDB)과 그 캡처·복원 시스템, 그리고 4종 벤치마크**이므로 Layer 1 Design 을 생성하지 않습니다. 데이터셋 자체는 학습 목표·손실·하이퍼파라미터·정책 구조를 정의하지 않으며(멀티카메라 캡처 리그 · 2단계 텔레오퍼레이션 취득 프로토콜 · MANO/FoundationPose 기반 복원 파이프라인은 데이터 생성 절차이지 이식 대상 정책이 아님), `/implement-design` 으로 옮길 재현 가능한 method 가 없습니다. 논문이 함께 제시하는 부수 baseline(human-to-robot contact map transfer, latent-space grasp retrieval)은 데이터셋의 유용성을 보이기 위한 **incidental baseline** 이며 핵심 기여가 아니므로 매핑 대상에서 제외합니다. 따라서 본 논문의 가치(5 임바디먼트 · 100 objects · 23뷰 · markerless 3D hand · object 6D · robot tactile 의 paired 데이터, cross-embodiment 전이·perception 벤치마크, `catalogs/datasets.md`·`catalogs/benchmarks.md` 라우팅과 P0 D24–D27 함의)는 분석 문서(`analysis.md`) 본문이 담습니다. `/implement-design` 호출 시 비대상 short-circuit 으로 `UNMAPPABLE.md` 가 산출됩니다.
