# Design — Robots Need More than VLA and World Models

---

## 📄 Design 메타

| 항목 | 내용 |
|------|------|
| 원문 제목 (영문) | Robots Need More than VLA and World Models |
| 링크 | [arXiv:2606.06556](https://arxiv.org/abs/2606.06556) |
| 분석 문서 | [`analysis/2606.06556/analysis.md`](./analysis.md) |
| 본문 확보 수준 | 전문(arXiv HTML) |
| Design 적용 | 🚫 비대상 (survey) |
| Design 생성일 | 2026-06-09 |

---

## 🚫 Design 비대상

본 논문은 구현 가능한 단일 알고리즘이 아니라 네 개의 *인터페이스(컴포넌트) 명세* 를 추상 수준에서 제시하는 **position / survey paper** 이므로 Layer 1 Design 을 생성하지 않습니다. 학습 목표·손실·하이퍼파라미터·평가 임계값이 원문에 존재하지 않으며(저자는 $`q_{\theta}`$ · $`f_{\psi}`$ · $`p_{\omega}`$ · $`\mathbf{r}_{\eta}`$ 의 입출력 계약만 형식화), `/implement-design` 으로 이식할 재현 가능한 method 가 없습니다. 따라서 네 인터페이스(physical data engine · task-preserving retargeting · physics-grounded world model · self-improving deployment loop)와 그 closed-loop 주장, 평가 질문 셋 등 본 논문의 가치는 분석 문서(`analysis.md`) 본문이 담습니다(카탈로그 등재 대상 아님). `/implement-design` 호출 시 비대상 short-circuit 으로 `UNMAPPABLE.md` 가 산출됩니다.
