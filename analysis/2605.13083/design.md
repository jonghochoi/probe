# Design — TouchAnything: A Dataset and Framework for Bimanual Tactile Estimation from Egocentric Video

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | TouchAnything: A Dataset and Framework for Bimanual Tactile Estimation from Egocentric Video |
| 링크 | [arXiv:2605.13083](https://arxiv.org/abs/2605.13083) |
| 분석 문서 | [`analysis/2605.13083/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 적용 | 🚫 비대상 (dataset) |
| Design 생성일 | 2026-06-10 |

---

## 🚫 Design 비대상

본 논문의 핵심 기여는 대규모 멀티뷰 egocentric 촉각 데이터셋 **EgoTouch**(208 tasks / 1,891 episodes / ~2.1M frames)와 그 평가 프로토콜이므로, foundry 정책으로 포팅할 새 method 를 제안하는 **dataset** 논문으로 분류해 Layer 1 Design 을 생성하지 않습니다. 함께 제시된 TouchAnything 은 데이터셋의 가치를 입증하는 vision-to-touch **회귀(perception) 베이스라인**으로, action policy(`pi0`/`act`/`diffusion` 등)와 목적·출력(액션 chunk 가 아닌 $`21\times21`$ 압력맵)이 달라 매핑 대상에서 제외합니다. 따라서 이 논문의 가치는 `카탈로그` 라우팅(`dataset/human/EgoTouch` → `catalogs/datasets.md` 👤 Human Video)으로 전달되며, 데이터셋 facts·임바디먼트·라이선스 등 세부는 분석 문서(`analysis.md`) 본문이 담습니다. `/implement-design` 호출 시 비대상 short-circuit 으로 `UNMAPPABLE.md` 가 산출됩니다.
