# Audit Report — <one-line English-friendly title> on `<foundry>`

> PROBE audit 모드 산출물. 한글 단일 문서이며, sibling Design + 한
> foundry 의 impl 가이드/패치를 원천 분석 문서 (`analysis/<id>.md`) 와
> foundry 코드에 대조한 정적 검증 결과입니다. 코드는 실행하지
> 않습니다 (`git apply --check` 만 허용). 형식·이모지·용어 규칙은
> `docs/STYLE.md` §7 / §4 를 정확히 따릅니다. 재실행 시 이
> 파일을 덮어씁니다.

---

## 📄 검증 메타

| 항목 | 내용 |
|------|------|
| 상위 Design | [`../<id>_design.md`](../<id>_design.md) |
| Originating analysis | [`../<id>.md`](../<id>.md) |
| Foundry | `lerobot` (또는 다른 등록된 foundry 이름) |
| 구현 가이드 | [`../<id>_impl/<foundry>/impl.md`](../<id>_impl/<foundry>/impl.md) · [`../<id>_impl/<foundry>/impl.patch`](../<id>_impl/<foundry>/impl.patch) |
| 검증 생성일 | YYYY-MM-DD (`TZ=Asia/Seoul`) |
| 📚 문헌 대조 | `pass` / `fail` / `partial` |
| 🔍 패치 정합성 | `pass` / `fail` |
| 🧪 시그니처·하이퍼파라미터 | `pass` / `fail` / `partial` |
| 🧬 실행 검증 | `pass` / `fail` / `skipped` |
| ⚖️ 종합 판정 | 한 줄 요약 (분석 트랙은 상태 없음) |
| 🔎 §🚧 분류 | `vendor-resolved` N / `paper-extractable` N / `paper-silent-defaultable` N / `paper-silent-experimental` N / `out-of-base-scope` N (다음 액션 트리거) |

---

## 📚 문헌 대조

<!-- originating analysis/<id>.md 와 Design 이 명시한 추가 인용에 대해
     일치 / 충돌 / 확장 / 무관 중 어느 관계인지 한 줄씩 판정합니다.
     일치·충돌 의 경우 analysis 문서에서 직접 인용 (verbatim) 한 줄을
     반드시 함께 적습니다. -->

| 분석 | 관계 | 인용 / 사유 |
|------|------|-------------|
| [`../<id>.md`](../<id>.md) | 일치 / 충돌 / 확장 / 무관 | <verbatim 인용 또는 갭 설명> |
| … | | |

판정: `pass` / `fail` / `partial`

<!-- 적어도 하나의 일치/확장 → pass. 충돌 한 줄이라도 있으면 fail.
     무관만 있으면 partial. -->

---

## 🔍 패치 정합성

<!-- `git apply --check` 결과를 verbatim 으로 기록합니다. -->

```text
$ cd /home/user/probe && git apply --check analysis/<id>_impl/<foundry>/impl.patch
<stdout/stderr verbatim, 빈 출력이면 그 사실을 적습니다>
```

판정: `pass` (zero exit) / `fail — <stderr 첫 줄 verbatim>`

---

## 🧪 시그니처·하이퍼파라미터 일치

<!-- 패치가 손대는 foundry 파일들의 함수/클래스 시그니처와, Design /
     impl.md 에서 인용된 모든 verbatim 토큰(`ε = 0.1`,
     `chunk_size = 50` 등)이 패치 본문과 일치하는지 점검합니다. 코드
     실행 없이 정적 비교만 합니다. -->

| 항목 | 출처 | 패치 본문 | 일치 |
|------|------|-----------|------|
| 함수 시그니처 `forward(...)` | `vendor/lerobot/policies/<base>/modeling_<base>.py:LNN` | `patch hunk @<line>` | ✅ / ❌ / ⚠️ |
| 상수 `<name> = <value>` | `<id>_design.md §📊` verbatim | `patch hunk @<line>` | ✅ / ❌ / ⚠️ |
| import 경로 `<module>` | `impl.md §🪛` | `patch hunk @<line>` | ✅ / ❌ / ⚠️ |
| … | | | |

판정: `pass` / `fail` / `partial`

<!-- 모든 행 ✅ → pass. 런타임 오류를 유발할 시그니처 ❌ 한 줄이라도
     있으면 fail. 인용은 되었으나 패치에 없는 상수 ⚠️ 가 있으면
     partial. -->

---

## 📐 식·표 일치

<!-- Design 또는 cited analysis/<id>.md 가 언급한 모든 수식 (`Eq. (4)`)
     · 표 (`Table 3`) 가 패치에 구현되어 있는지, 또는 impl.md §🚧
     미해결 로 명시적으로 유보되어 있는지 점검합니다. 둘 다 아닌
     silent-skip 은 partial 입니다. -->

| 참조 | 출처 | 패치 hunk / 🚧 항목 | 상태 |
|------|------|---------------------|------|
| `Eq. (4)` | `analysis/<id>.md §🔬` | `impl.patch @<line>` / `impl.md §🚧 #N` | 구현 / 유보 / silent-skip |
| `Table 3` | `<id>_design.md §📊` | `…` | 구현 / 유보 / silent-skip |
| … | | | |

<!-- silent-skip 항목은 §🧪 시그니처·하이퍼파라미터 판정에 partial 로
     반영됩니다. -->

---

## 🧬 실행 검증

<!-- 설치된 foundry 위에서 patch 를 적용하고 impl 의 sibling smoke
     test 를 실제로 실행한 결과입니다. 정적 체크(🔍/🧪/📐)가 "diff 가
     맞다"를 보이는 데 비해, 본 체크는 "코드가 실제로 import·인스턴스화
     ·계산된다"를 보입니다. 런타임을 만들 수 없으면(offline/install 실패)
     또는 sibling test 가 없으면 `skipped` — 정적 verdict 는 그대로
     유효합니다. 실제 학습/추론은 절대 돌리지 않습니다 (CPU·weight-free
     smoke test 만). -->

```text
$ py=$(bash scripts/ensure-foundry-runtime.sh <foundry>)
$ git -C .foundry-runtime/<foundry>/src apply -p3 --directory=src/lerobot <impl.patch>
$ "$py" -m pytest <sibling test> -q
<pytest 요약 줄 verbatim — 예: "6 passed in 2.96s">
```

판정: `pass` (전부 green) / `fail` (apply 또는 테스트 실패 — 실패
assertion verbatim) / `skipped` (테스트 부재 또는 런타임 미가용 — 사유)

<!-- fail 은 실제 결함입니다 — patch 가 코드로 성립하지 않음. 실패
     assertion 한 줄을 반드시 인용. skipped 는 정합성 fail 이 아니며
     `/reproduce-paper` 수렴 판정에서 pass 와 동일 취급. -->

---

## ⚖️ 종합 판정

- 📚 문헌 대조: `pass` / `fail` / `partial`
- 🔍 패치 정합성: `pass` / `fail`
- 🧪 시그니처·하이퍼파라미터: `pass` / `fail` / `partial`
- 🧬 실행 검증: `pass` / `fail` / `skipped`

→ <한 줄 요약: "이 foundry 의 구현은 Design 과 정합하며 실행 검증을
   통과합니다" / "이 foundry 의 구현은 정합하지 않습니다 — <사유>" /
   "이 foundry 의 구현은 부분적으로 정합합니다 — <partial 항목>">

---

## 🔎 §🚧 분류

<!-- impl.md `§🚧 미해결 / 잠정` 의 각 행을 다음 4 bucket 중 정확히
     하나로 분류합니다. 분류 근거는 한 줄 — vendor `file:line` 인용
     또는 본문 `§X.Y` 인용으로 ground. 본 절은 §🧪 / §📐 verdict 와
     독립이며 verdict 를 바꾸지 않습니다. `/reproduce-paper` 의
     §B 매트릭스가 이 표를 single source of truth 로 읽어 다음 액션
     (foundry feedback / paper-analysis focus / honest defer) 을 결정
     합니다. 매 라운드 zero-state 로 새로 분류합니다 (직전 라운드의
     분류를 inherit 하지 않음 — honesty 누적 오염 차단).

     Bucket 정의:
     - `vendor-resolved` — foundry 코드의 기존 상수/기본값이 동치
       답을 강제. 다음 라운드 foundry feedback 이 vendor 값을 lift
       하고 impl.md §🚧 → §🧪 로 이동.
     - `paper-extractable §X.Y` — 본문 §X.Y 에 정보가 있으나 Design
       이 sketch 만 했음. 다음 라운드는 outer step
       (`/analyze-paper --focus "§X.Y,..."`) 로 Design 갱신.
     - `paper-silent-defaultable` — 본문 침묵, 합리적 default 가
       존재. foundry feedback 이 default 값을 patch 에 도입하면서
       `# NOTE: paper §X 본문 침묵, default <v> 채택 — 근거: ...`
       1-line 주석 의무.
     - `paper-silent-experimental` — 본문 침묵 + 실험 결정 필요.
       honest defer (§🚧 잔존).
     - `out-of-base-scope` — 논문·Design 모두 완전 명세하지만,
       `/foundry` §A 가 선택한 단일 base 의 좌표계가 그 모듈/정책을
       포함하지 않음 (예: π_hand 촉각 인코더·LSTM 정책을 π_uni→pi0
       매핑에서 제외). 이 bucket 을 쓰려면 impl.md §🧱 의 cover/exclude
       scope 선언을 cite 해야 하며, 선언이 없으면 사용 금지. §🚧
       numbered bucket 이 아니라 §🪛 신규-미구현으로 기록하고, reproduce
       루프는 outer/inner 어느 것도 트리거하지 않는 honest defer 로
       취급. paper-extractable 보다 우선 — base 밖 모듈은 Design 을 더
       파도 이 base 에 구현되지 않으므로 outer step 이 무의미.
-->

| §🚧 # | 항목 한 줄 | bucket | 근거 / 다음 액션 |
|-------|------------|--------|-------------------|
| 1 | <impl.md §🚧 #1 한 줄 요약> | `vendor-resolved` / `paper-extractable §X.Y` / `paper-silent-defaultable` / `paper-silent-experimental` | <vendor file:line 또는 본문 §X.Y 인용 한 줄> |
| 2 | … | | |

<!-- ANALYSIS_BUCKETS:START -->
- vendor-resolved: <#N,#M 또는 비어 있으면 비워둠>
- paper-extractable: <#N,#M>
- paper-silent-defaultable: <#N>
- paper-silent-experimental: <#N>
- out-of-base-scope: <#N,#M 또는 비어 있으면 비워둠>
- focus-hint: <§3.2.1,§3.2.2 또는 비어 있으면 비워둠>
<!-- ANALYSIS_BUCKETS:END -->

<!-- 머신 파싱 토큰. `/reproduce-paper` 와
     `scripts/refresh-analysis-index.py` 가 이 영역만 읽습니다.
     hand-edit 금지 — audit prompt 가 매 라운드 zero-state 로 재생성
     합니다. focus-hint 는 paper-extractable bucket 의 §X.Y 토큰을
     쉼표로 join 한 정렬된 set. § 기호 (U+00A7) 는 본문 인용 verbatim
     규약 (`docs/STYLE.md` §4-1) 과 통일합니다. -->

---

## 🚧 미해결 / 잠정

<!-- 정적 검증으로 결론 낼 수 없어 사람의 후속 판단이 필요한 항목.
     코드 실행이 필요한 체크 (학습/평가), Design 본문이 너무 모호해
     식·표 매핑이 안 되는 항목 등. 없음이면 "없음" 으로 명시. -->

- (예) Design 의 §🔬 ② 체크는 실제 학습 결과 비교가 필요해 정적 검증으로 결론 불가
