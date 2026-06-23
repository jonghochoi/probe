# Design — Tactile Genesis: Exploring Tactile Sensors at Scale for Learning Dexterous Tasks

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Tactile Genesis: Exploring Tactile Sensors at Scale for Learning Dexterous Tasks |
| 링크 | [arXiv:2606.22332](https://arxiv.org/abs/2606.22332) |
| 분석 문서 | [`analysis/2606.22332/analysis.md`](./analysis.md) |
| 본문 확보 수준 | PDF 텍스트(pypdf) |
| Design 적용 | 🚫 비대상 (benchmark) |
| Design 생성일 | 2026-06-23 |

---

## 🚫 Design 비대상

본 논문은 foundry 로 포팅 가능한 새 model·architecture·학습목표·알고리즘을 제안하지 않는 **GPU 병렬 촉각 센서 시뮬레이션 플랫폼(simulator)** 논문이므로 Layer 1 Design 을 생성하지 않습니다. 주 산출물은 Genesis World 에 통합된 촉각 센서 시뮬레이터(binary contact·depth·per-taxel force/torque·elastomer marker displacement·proximity·temperature·contact audio 를 공통 인터페이스로 노출, 설정형 배치/해상도/노이즈 모델)와 그 위에서 수행한 촉각 표현 통제 ablation 의 결론입니다 — `/implement-design` 으로 lerobot 정책 family 에 이식할 학습 손실·옵티마이저·텐서 학습 계약이 존재하지 않습니다. 본 논문에 등장하는 teacher-student(PPO 교사 + DAgger 학생 + RND + 보조 디코더) 학습 레시피는 새 기여가 아니라 표준 실험 수단(privileged→tactile 증류)이라 매핑 대상에서 제외합니다. 따라서 이 논문의 가치는 `카탈로그` 라우팅(`benchmark/sim/TactileGenesis` → `catalogs/benchmarks.md` 🎮 Simulator)과, 촉각 입력 선택(per-taxel force/torque)·배치(whole-hand)·System0 sim2real 함의를 담은 분석 문서(`analysis.md`) 본문으로 전달됩니다. `/implement-design` 호출 시 비대상 short-circuit 으로 `UNMAPPABLE.md` 가 산출됩니다.
