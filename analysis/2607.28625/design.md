# Design — ACE-Data-0: Human-Centric Ambient Capture as Embodied Data Engine

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | ACE-Data-0: Human-Centric Ambient Capture as Embodied Data Engine |
| 링크 | [arXiv:2607.28625](https://arxiv.org/abs/2607.28625) |
| 분석 문서 | [`analysis/2607.28625/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 생성일 | 2026-08-02 |
| Design 적용 | 🚫 비대상 (dataset) |

---

## 🚫 Design 비대상

본 논문은 foundry 로 포팅 가능한 Layer 1 알고리즘 기여가 없는 **데이터셋 + 벤치마크(dataset)** 논문이므로 Design 을 생성하지 않습니다. 핵심 deliverable 은 (1) 실제 가정을 동기화 녹화 스튜디오로 바꾸는 캡처 엔진 ACE(table-scale·room-scale 2구성)와 (2) 그로부터 수집한 150시간·17M 프레임·75,000 에피소드의 장기 가정 HOI 데이터셋 ACE-Data-0, 그리고 (3) signals→components→interactions 3단계 계층 벤치마크입니다 — 새로운 model/architecture/학습목표/알고리즘이 아닙니다. ACE 의 기술적 정수(광학 시계 동기화, 마커-브리지·hand-eye 캘리브레이션, 측정 기반 어노테이션 파이프라인)는 데이터 취득·정합 절차이지 학습 정책이 아니며, 벤치마크에 등장하는 30여 방법(PressureVision·TouchAnything·SMPLest-X·WiLoR·HaMeR 등)은 모두 *기존 공개 체크포인트로 평가된 부수 baseline* 일 뿐 본 논문이 제안·세부화한 것이 아닙니다. 따라서 🧮 데이터 계약 … 🚧 미해결 7개 섹션을 채울 재현 가능한 Layer 1 스펙이 존재하지 않습니다. 이 논문의 가치는 foundry 매핑이 아니라 분석 문서의 의사결정 함의 — P0 D24(priority data axis, egocentric 우선)·D25(tactile/force data 의 first-class gap)·D26(benchmark scouting scope)의 근거, 그리고 P2(multimodal fusion)·P4(pretraining corpus)·P5(world model)로의 데이터 소스 함의 — 로 전달됩니다. vision→tactile 예측·SMPL-X/MANO 변환·2DGS 물체 재구성 같은 *부수 기법*은 본 논문이 새로 제안한 것이 아니라 기존 도구/baseline 이므로 매핑 대상에서 제외합니다.
