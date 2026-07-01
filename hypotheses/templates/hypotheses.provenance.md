# Hypotheses Provenance — <스코프 한 줄 (sibling hypotheses.md 와 동일)>

> sibling `hypotheses.md` 의 출처 회계 사이드카. 어떤 분석을 읽었고, 어떤
> 텐션이 어떤 가설로 이어졌으며, 각 가설의 검증 상태가 무엇인지 —
> 독자가 DB 증거와 추론 사이의 점프를 감사(audit)할 수 있게 합니다.
> 형식 규칙은 `docs/style.md` §7 / §4. 재실행 시 덮어씁니다.

---

## 📚 코퍼스

<!-- 읽은 모든 analysis/<id>/ + 각각의 primary D# tie. 인덱스가 가리켰지만
     읽지 못한 id 는 여기가 아니라 §🕳️ 에 기록. -->

| 분석 | Primary D# tie | 읽은 섹션 |
|------|----------------|-----------|
| [`<id>`](../../analysis/<id>/analysis.md) | D# | 🎯 / ⚙️ / ⚠️ / ✨ (+♻️, design.md) |
| … | | |

---

## 🧶 텐션 → 가설 계보

<!-- Stage-2 텐션이 Stage-3 가설로 이어진 경로. user-seeded 가설은 lineage
     를 `user-seeded` 로 명시 — DB 증거가 어디서 끝나고 사용자 추측이
     어디서 시작하는지 보이게. -->

| 가설 | Lineage | 원 텐션 (§⚡) | 근거 id |
|------|---------|---------------|---------|
| H1 | mined / user-seeded | <모순/반복 실패/미시도/증거 공백 — 한 줄> | `<id>`, `<id>` |
| … | | | |

---

## 🏷️ 검증 상태

<!-- 가설별 상태 + 프로토콜이 겨냥한 rung. 모든 가설은 inferred 로 태어나
     측정 전까지 unverified — Rung 0–1 pass 는 "참" 이 아닙니다. -->

| 가설 | 상태 | 목표 Rung | 비고 |
|------|------|-----------|------|
| H1 | `inferred` · `unverified` | <0–3> | <exploratory · ungrounded 면 명시> |
| … | | | |

---

## 🕳️ 범위 공백

<!-- 근거 없는 결정 (grounding 0 편인 in-scope D#), 인덱스가 가리켰으나
     디스크에 없던 id, --seed 를 ground 하지 못한 사유 등. 없으면 "없음". -->

- <한 줄>
