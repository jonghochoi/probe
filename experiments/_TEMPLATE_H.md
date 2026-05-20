# Hypothesis — <one-line English-friendly title>

> PROBE hypothesize 모드 산출물. 단일 한글 문서이며, 영문 1차 파일은
> 없습니다. 형식·이모지·용어 규칙은 `docs/STYLE_GUIDE.md` §7 / §4 를
> 정확히 따릅니다. 작성 후 본문은 불변(베이스 매칭 실패 시 추가되는
> 한 줄 🚧 블록쿼트만 예외). 같은 주제를 다시 다루려면 새 H 번호로
> 시작합니다. `manifest.yaml` 이 sibling 파일로 함께 존재합니다.

---

## 📄 가설 메타

| 항목 | 내용 |
|------|------|
| ID | `H###` |
| Pillar | `P#` |
| 슬러그 | `<kebab-case>` |
| 시드 | Pillar `P#` / `analysis/<id>.md` |
| 관련 Decision | `D#`, `D#` |
| 관련 분석 | [`analysis/<id>.md`](../../analysis/<id>.md) (없으면 "없음") |
| 후보 베이스 | `pi0` / `pi05` / `pi0_fast` / `smolvla` / `act` / `diffusion` / `null` |
| 생성일 | YYYY-MM-DD (`TZ=Asia/Seoul`) |
| 상태 | `draft` (`manifest.yaml` 가 단일 진실) |

<!-- 시드가 Pillar 인 경우 "관련 분석" 은 보통 "없음" 입니다. 시드가
     analysis 인 경우 해당 슬러그가 반드시 들어갑니다. 후보 베이스가
     `null` 이면 `/implement-hypothesis` 가 거절할 수 있습니다. -->

---

## 🧭 한 줄 요약 (TL;DR)

<!-- 1–2문장. 이 가설이 무엇을 주장하는지. 향후 사람도 에이전트도 이
     줄만 보고 가설을 변별할 수 있어야 합니다. -->

---

## ❓ 출발 갭

<!-- 왜 이 가설을 굳이 꺼냈는가. 시드 (Pillar `context/P#.md` 또는
     `analysis/<id>.md`) 에서 어떤 미해결 항목/충돌/지연된 Decision 을
     읽고 이 가설을 도출했는지 verbatim 인용 + 1–2문단 설명. -->

---

## 🧩 가설 진술

<!-- 가설의 본문. "X 를 하면 Y 가 일어난다" 형태로, X 와 Y 모두 가능한
     한 구체적으로. 모호하면 §🔬 falsifiable test 가 무너집니다. -->

---

## 🔬 Falsifiable Test 설계

<!-- 1–3개의 측정 가능한 체크. 각 체크는 (지표 · 임계값 · 비교 baseline)
     세 요소를 모두 갖춥니다. "성능이 좋아진다" 는 체크가 아닙니다 —
     명확한 숫자/조건이 들어가야 합니다. -->

1. **지표** — `<metric name>` · **임계값** — `<verbatim number/comparison>` · **비교 baseline** — `<vendor policy or pinned paper>`
2. <!-- 두 번째 체크. 없으면 줄 자체를 지웁니다. -->
3. <!-- 세 번째 체크. 없으면 줄 자체를 지웁니다. -->

---

## 🎯 관련 Pillar / Decision (P# / D#)

<!-- `context/MASTER.md` 기준. 어떤 P1–P5 / D1–D26 / CP1–CP5 를 건드리는지,
     supports / conflicts / extends / refines 중 어느 관계인지. 적어도
     하나의 관계가 필요합니다(없으면 가설이 너무 막연합니다). -->

- `D#` — supports / conflicts / extends / refines: <한 줄 요약>
- `D#` — supports / conflicts / extends / refines: <한 줄 요약>

---

## ✨ 핀 논문 대비 델타

<!-- `context/MASTER.md` §8 Tracked Literature 의 어떤 핀 논문 대비
     이 가설이 무엇을 다르게 주장하는가(핀 논문 이름 명시). 핀 논문이
     침묵하는 영역이라면 "핀 논문 미커버 영역 — 신규 주장" 으로 명시. -->

---

## ⚠️ 먼저 검증할 실패 모드

<!-- 이 가설이 우리 스택에서 무너질 가장 싼 이유. 학습 비용을 들이기
     전에 즉시 확인할 수 있는 sanity check 가 있다면 그 절차를 기록합니다. -->

---

## 💡 컨텍스트 제안

<!-- 가설이 채택되면 `context/MASTER.md` 의 어떤 Decision/핀이 흔들릴
     가능성이 있는지. 사람에게 제안만 — `context/MASTER.md` 는 절대
     수정하지 않습니다. 없으면 "없음". -->
