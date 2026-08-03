# Hypotheses — <스코프 한 줄: P# 또는 D#-range + 지배 테마>

> PROBE hypothesize 모드 산출물 (`/hypothesize`). 누적 `analysis/` DB 를
> 한 pillar/decision 범위로 가로질러 읽어, Decision Log 에 앵커된
> 순위화·반증가능한 가설을 합성한 읽기 전용 문서입니다. 실험은 실행하지
> 않습니다 — 모든 가설은 `inferred`/`unverified` 로 출하되고, 경험적
> 검증 (Rung 3) 은 사람의 몫입니다. 형식·이모지·용어 규칙은
> `docs/style.md` §6 / §4 를 정확히 따릅니다. 재실행 시 이 파일을
> 덮어씁니다. 출처 회계는 sibling `hypotheses.provenance.md` 참조.

---

## 🧭 범위 / 요약

<!-- 스코프 (P#/D#-range + 추론된 스코프면 그 사실과 drop 한 runner-up),
     코퍼스 크기 (읽은 analysis 편수), 헤드라인 텐션 2–3 줄. --seed 런이면
     seed 요지 한 줄 포함. -->

- 스코프: <P# / D#-range> (<positional / seed 로부터 추론 — 근거 한 줄>)
- 코퍼스: <N>편 (`hypotheses.provenance.md` §📚)
- 헤드라인: <2–3 줄>

---

## 🔀 합의·불일치 매트릭스

<!-- Stage 2. 스코프 내 각 D# 에 대해, 각 논문의 ⚙️ 의사결정 함의가 그
     결정을 어느 방향으로 미는지 + 확신도 (강/중/약 — ♻️ 재현성과 방법론
     에서 도출, vibes 금지). 한 행 = (D#, 분석) 쌍. -->

| D# | 분석 | Push 방향 | 확신도 | 근거 한 줄 |
|----|------|-----------|--------|------------|
| D# | [`<id>`](../../analysis/<id>/analysis.md) | <v1 유지 / v2=<대안> 로 이동> | 강 / 중 / 약 | <⚙️ 인용 요지> |
| … | | | | |

---

## ⚡ 텐션

<!-- 네 클래스 각각 bullet + 출처 id. 해당 클래스가 비어 있으면 "없음" 명시
     (honest emptiness). -->

**모순 (contradiction)** — 두 분석이 한 D# 를 서로 다른 `v` 로 미는 경우

- <한 줄> (`<id>` vs `<id>`)

**반복 실패 모드** — 같은 ⚠️ 가 ≥2 편에서 재발

- <한 줄> (`<id>`, `<id>`)

**미시도 조합 (untried)** — 분석된 어떤 논문도 함께 시험하지 않은 결정-대안 쌍

- <한 줄>

**증거 공백 (evidence gap)** — 함의가 0–1 편에만 기대는 D#

- <한 줄> (`<id>` 단독)

---

## 💡 가설

<!-- 순위순. 가설마다 Stage-3 필수 필드 전부 — 하나라도 없으면 drop 이
     원칙 (예외: user-seeded). 라벨은 verbatim: `inferred`, `unverified`,
     `user-seeded`, `exploratory · ungrounded`. -->

### H1 — <한 줄 반증가능 주장 (틀릴 수 있는 예측형)>

- 앵커: D# (+ D#)
- 근거 (≥2): [`<id>`](../../analysis/<id>/analysis.md) — <한 줄>; [`<id>`](../../analysis/<id>/analysis.md) — <한 줄>
- 예측 효과: <메트릭/설정/손실항 이름 + 방향/크기>
- 측정 프로토콜: Rung <0–3> (<`implementable` / `proxy-consistent` / `indicative` / `empirically-verified` 목표 라벨>) — <pass/fail 이 뜻하는 바 한 줄>
- 상태: `inferred` · `unverified`

### H2 — …

---

## 🏆 순위

<!-- Stage 4. 축별 bullet (별도 표 없음), 0–3 점. top-K 순서 = §💡 순서.
     user-seeded 가설은 순위와 무관하게 §💡 에 항상 표시. -->

**H1 — <합계>점**

- 증거 강도: <0–3> — <한 줄>
- 결정 레버리지: <0–3> — <한 줄>
- 검증 가능성: <0–3> — <한 줄>
- 비용 역수: <0–3> — <한 줄>

**H2 — …**

---

## 🚧 제안 (Decision Log)

<!-- 사람이 context/P#.md 에 반영할지 판단할 제안. 이 커맨드는 절대
     context/ 를 편집하지 않습니다. 제안 없음이면 "없음" 명시. -->

- D#: <현 v1> → <제안 v2 + 근거 가설 (H#)>
- (신규 결정 제안이 있으면) D-신규: <제안 내용 + 근거>
