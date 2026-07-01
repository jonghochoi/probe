# Design — RoboTacDex: A Dexterous Visual-Tactile-Action Dataset for Humanoid Manipulation

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | RoboTacDex: A Dexterous Visual-Tactile-Action Dataset for Humanoid Manipulation |
| 링크 | [arXiv:2606.31836](https://arxiv.org/abs/2606.31836) |
| 분석 문서 | [`analysis/2606.31836/analysis.md`](./analysis.md) |
| 본문 확보 수준 | PDF 텍스트(PyMuPDF) |
| Design 적용 | 🚫 비대상 (dataset) |
| Design 생성일 | 2026-07-01 |

---

## 🚫 Design 비대상

본 논문은 foundry 로 포팅 가능한 새 model·architecture·학습목표·알고리즘을 제안하지 않는 **순수 데이터셋(dataset)** 논문이므로 Layer 1 Design 을 생성하지 않습니다. 핵심 산출물은 Unitree G1 + Brainco Revo2 촉각형 다지 손 기반의 멀티뷰·멀티모달 휴머노이드 조작 데이터셋(6k+ trajectory / 19 task / 23 skill / 22 object, RGB-D 4시점 + fingertip 촉각 + 언어 주석)과 이를 밀리초 급으로 정렬하는 하드웨어-소프트웨어 동기화 수집 시스템이며, 학습 손실·옵티마이저·텐서 학습 계약이 존재하지 않습니다. 논문이 평가에 사용한 ACT / Diffusion Policy / GROOT N1.5 세 정책은 데이터 품질 검증을 위한 *부수 베이스라인* 일 뿐 본 논문의 핵심 기여가 아니므로 매핑 대상에서 제외합니다(각 정책은 이미 별도 upstream 산출물). 따라서 이 논문의 가치는 `카탈로그` 라우팅(`dataset/robot/RoboTacDex` → `catalogs/datasets.md` 🤖 robot·촉각 축, P0 D25 대상)으로 전달되며, 촉각 modality 의 세밀도(RH20T wrist F/T 대비 fingertip normal/tangential + 근접)·멀티뷰 concat 무효 관측(P2)·System0 입력 후보(P3)·라이선스 미공개 유보(D27) 등 의사결정 함의는 분석 문서(`analysis.md`) 본문이 담습니다. `/implement-design` 호출 시 비대상 short-circuit 으로 `UNMAPPABLE.md` 가 산출됩니다.
