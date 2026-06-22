# Design — HumanScale: Egocentric Human Video Can Outperform Real-Robot Data for Embodied Pretraining

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | HumanScale: Egocentric Human Video Can Outperform Real-Robot Data for Embodied Pretraining |
| 링크 | [arXiv:2606.20521](https://arxiv.org/abs/2606.20521) |
| 분석 문서 | [`analysis/2606.20521/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(PDF 텍스트, PyMuPDF 추출) |
| Design 생성일 | 2026-06-22 |
| Design 적용 | 🚫 비대상 (survey) |

---

## 🚫 Design 비대상

본 논문은 foundry 로 포팅 가능한 Layer 1 알고리즘 기여가 없는 **통제 비교 study(survey)** 논문이므로 Design 을 생성하지 않습니다. 핵심 deliverable 은 “동일 post-training·평가를 고정한 matched-scale 조건에서 egocentric 인간 영상 사전학습이 teleoperation 로봇 데이터 사전학습을 능가한다(특히 OOD)”는 *실증 결과와 scaling 곡선*이지, 새로운 model/architecture/학습목표/알고리즘이 아닙니다. 실험 vehicle 인 autoregressive World-Action Model(Mixture-of-Transformers, video expert=Wan 2.2 초기화)은 LingBot-VA 계열에서 *빌려온* 고정 백본일 뿐 본 논문이 제안·세부화한 것이 아니며(손실식·하이퍼파라미터·MoT 구성 모두 본문 미명시), 사전학습 corpus 역시 별도 논문 HumanNet([arXiv:2605.06747](https://arxiv.org/abs/2605.06747))에서 큐레이션한 부분집합이라 본 논문 고유의 데이터셋 기여도 아닙니다. 따라서 🧮 데이터 계약 … 🚧 미해결 7개 섹션을 채울 재현 가능한 Layer 1 스펙이 존재하지 않습니다. 이 논문의 가치는 카탈로그 라우팅(해당 없음 — model/dataset/benchmark 어느 카탈로그에도 등재 대상이 아닌 study)이 아니라 분석 문서의 의사결정 함의(P4 D22 egocentric-vs-mixed OPEN ablation·P0 D24 priority data axis 의 통제 증거)로 전달됩니다. pseudo-action(hand-pose retargeting)·video-prediction 사전학습 신호 같은 *부수 기법*은 본 논문이 새로 제안한 것이 아니라 vehicle 의 기존 구성요소이므로 매핑 대상에서 제외합니다.
